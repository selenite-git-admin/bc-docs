---
uid: metric-output-declaration-dbcp-2026-09-30
title: "DBCP — metric output declaration (bc-db migration 0030; ADR DEC-b1e9eb)"
description: "Adds mcf.metric_output_declaration (1:1 with a post-cutover metric contract version: unit, decimals, rounding), its immutable cutover membership written at version creation, and SECURITY DEFINER guards that require a declaration before a new version freezes. Additive; no backfill; existing versions untouched. Clone-proved on an owner- and grant-faithful restore of a fresh read-only live dump, including served-login vectors. NOT APPLIED: needs the operator's explicit DB yes, applied together with the declaration writer."
status: proposed
date: 2026-09-30
project: bc-db
domain: metrics
subdomain: metric-contract
focus: output-declaration
supersedes:
superseded_by:
---

# DBCP — metric output declaration (bc-db migration 0030)

**Decision:** ADR DEC-b1e9eb (D636, proposed). The design was accepted with boundary by the auditor on gen-fe8f9d-03, after three rounds.

**Task:** TSK-af9706. **Author:** SES-a5e264.

**Status: NOT APPLIED.** Applying is a separate act. It needs the operator's explicit DB yes, recorded as a bc-exchange grant.

**Where the migration lives:** bc-db `migrations/0030_mcf_metric_output_declaration.sql` (PR bc-db#98).
- It supersedes the first draft, bc-core#897, which was written in bc-core `docker/redesign`. That tree is frozen by ADR DEC-4c1396: bc-core CI `docker-redesign-freeze.spec.ts` failed the draft, run 36669976926.
- Platform schema changes are bc-db forward migrations.

## 1. What changes

**Files:**

| File | sha256 |
|---|---|
| migration `migrations/0030_mcf_metric_output_declaration.sql` | `c7da14541197ad9b26de6b113ead95c4d0314a9201bcd405de00f9bc46b2e73f` |
| rollback `rollback/0030_mcf_metric_output_declaration.rollback.sql` | `a569409d4b735e08d832c16b4aa79d930bf921d01ddd3242188e461f81804c6f` |

The rollback is pinned to the migration bytes and bound to the ledger.

**Header:** `transactional: true`, `plane: bootstrap`. The migration adds triggers to the baseline-owned `mcf.metric_contract_version` and `mcf.mcv_package_snapshot`.

**New tables** (schema `mcf`, all owned by `bc_schema_owner`, `REVOKE ALL FROM PUBLIC`):

| Table | Columns | Rules |
|---|---|---|
| `metric_output_declaration_policy` | `policy_code` PK, `cutover_at`, `recorded_by_name` | One row, written by the migration. Immutable. An audit record only: no gate reads it. |
| `metric_output_declaration_required` | `metric_contract_version_uid` PK/FK, `recorded_at` | Cutover **membership**: one row per version created after the apply, written by `trg_mod_mcv_membership` (SECURITY DEFINER). Immutable. A direct INSERT is refused (`pg_trigger_depth() < 2`). |
| `metric_output_declaration` | `metric_contract_version_uid` PK/FK, `unit_type_code` FK → `master.master_unit_type`, `decimal_places_count` (0–6, NULL exactly when the unit is `currency`), `rounding_mode_code` (`half_up` default, or `half_even`), `declared_at`, `declared_by_name` | 1:1 with the version. Immutable. Indexed on `unit_type_code`. |

**New guard functions** (8, named `mcf.fn_mod_*`):
- The guards are `SECURITY DEFINER`, with `SET search_path TO pg_catalog`, owned by `bc_schema_owner`, and `EXECUTE` revoked from PUBLIC. This follows the 0029 / `fn_mc_grain_freeze_guard` pattern.
- The two raise-only helpers (`fn_mod_refuse_change`, `fn_mod_required_insert_guard`) are invoker functions.

**New triggers** (9, named `trg_mod_*`):
- **Immutability:** on the policy, membership and declaration tables.
- **Membership:** written at version INSERT.
- **Declaration insert guard:** a declaration needs membership and an unfrozen parent. "Frozen" uses the platform predicate: a frozen governance state, or `mcf.fn_mcv_has_approval_snapshot`.
- **Currency coherence:** a deferred constraint trigger. Unit `currency` needs a currency `aggregation_currency_code`; every other unit needs `not_applicable`.
- **Version update guard:** the parent's currency is frozen once a declaration exists, and a member version cannot enter a frozen state without its declaration.
- **Snapshot guard:** a member version gets no package snapshot without its declaration.

**Served login `bc_platform_runtime`:**
- It holds SELECT on the three tables and INSERT on the declaration only.
- It writes membership only through the SECURITY DEFINER trigger; it holds no INSERT on the membership table.
- It needs no EXECUTE on any new function.

**Rows at apply:** 1 policy row, 0 members and 0 declarations. The migration's verification blocks assert these counts, the 9 triggers, the ownership, the served login's exact grants, and that the six guard functions are SECURITY DEFINER.

## 2. What does not change

- **No existing column, grant or row changes.** Existing versions (450 in the clone) get no membership. They can never gain a declaration, and their evaluation and package identity are untouched. There is no backfill (Invariants III and V).
- **No existing digest changes.** The package `output_digest` starts covering the declaration only in the later package-format slice (v4), which must agree with the auditor validator.
- **There is no insert-as-frozen route.** New versions must start at `draft` (`mcf.fn_mcv_state_transition_check`, INSERT branch). review→approved requires an approval snapshot, which the snapshot guard covers.

## 3. Sequencing constraint (blocking)

From the apply on, **every new metric contract version is a member**, and needs its declaration before approval or a package snapshot.

- The only governed writer of new versions is bc-core `src/registry/mcf/mcf-cert-writer.service.ts`, whose `insertMcv` is reached through `createMetricDraft` / `createMetricDraftWithGrainPin`. It is the only non-test inserter; checked by grep of bc-core src.
- **Apply 0030 only in the same deploy window that serves the bc-core build whose cert writer writes the declaration** (the authoring slice). Otherwise approval of every new metric stops.
- The umbrella's window plan puts this in the joint cutover window: 0030, plus the authoring slice, plus the DECLARED_DECIMAL evaluator, under one operator grant that pins the migration bytes and the build. It must be announced on gen-d2e52d.

## 4. Clone proof (2026-09-30, owner- and grant-faithful)

**Source:**
- A fresh read-only `pg_dump -Fc` of live `bc_platform_dev`, taken 2026-09-30T05:54:05Z (cluster sysid 7689410286420172840; dump sha256 `21c03553…3831`).
- Restored **with owners and grants** into a throwaway `postgres:17.11-alpine` container (127.0.0.1:55975).
- The 15 roles were recreated with their live LOGIN / INHERIT attributes (`0030-clone-roles.sql`; passwords are clone-only).
- 0 restore errors; 450 versions; `mcf.metric_contract_version` owned by `bc_schema_owner`.
- **The container and the dump were deleted after the proof.** Nothing ran against live.

**Evidence files** (in `metric-output-declaration/`):

| File | sha256 |
|---|---|
| `0030-clone-source.txt` | `579d3adf2d8a0e4d3f28d8a3b5009178c4d10a09b837d9a0b8d5b64b3fa9770f` |
| `0030-clone-roles.sql` | `04d4c621e4ff058c41d3f07ca7cdcc20935e50798ea4bdf2e4ccacaa2562a4cd` |
| `0030-apply-transcript.txt` | `4b1135fcff1076c58ace9b557cb3aca271ec781cd27c68a84da225967b87f9c0` |
| `0030-vectors.sql` | `74805c76ddbb9ce5ebe101e87b5ef5b6358cabd4af867509f85f287ee52e3e8e` |
| `0030-vectors-transcript.txt` | `1d907803dd98aba63b220566448a7148b4fa85b8db271361db518e685028cf35` |
| `0030-rollback-transcript.txt` | `5fd705f222863b8fca6c2de56751a113062e052065345074638b6a8caf3661d8` |

**Apply:**
- 0030 was applied as one transaction by the bootstrap principal, and its verification blocks passed.
- The ledger `applied` event was recorded as the runner records it, through `infrastructure.fn_record_migration_event`, with sha256 `c7da1454…`. Git ref `clone-proof`, and a clone-only review disposition.
- The ledger state is `applied`.

**Vectors: all passed** (the transcript ends "ALL VECTORS PASSED: 3 declarations, 5 members").
- Where a pre-existing platform trigger would refuse first, an **isolated** variant disables that one trigger on the clone, to show the new gate itself refuses. Those triggers are `trg_mcf_mcv_state_transition`, `trg_mcv_package_snapshot_guard`, and for V10 `trg_mcv_grain_entity_version_guard`.

| # | Vector | Result |
|---|---|---|
| setup | 4 new versions | 4 membership rows written by the trigger; pre-cutover versions have none |
| 1 | `days` / 2 / `half_up` on a post-cutover draft with `not_applicable` | accepted |
| 2 | `currency` with places 2; `days` on a `local_currency` version | both refused |
| 3 | `days` with NULL places | refused |
| 4 | a declaration on a pre-cutover version | refused: predates the cutover |
| 5 | a declaration on a frozen, declared member | refused: frozen |
| 6 | an undeclared member entering `approved` | refused by the new gate (isolated), and by the platform state rules (realistic) |
| 7 | a package snapshot for an undeclared member | refused |
| 8 | changing the currency on a declared draft | refused |
| 9 | UPDATE or DELETE of a declaration and of the policy row | refused |
| 10 | a pre-cutover version entering `approved` (isolated) | accepted: the new gate does not apply |
| 11 | a member with `created_at` backdated to 2020: approval, and a snapshot | both refused (membership holds) |
| 12 | UPDATE or DELETE of a membership row; a direct INSERT for a pre-cutover version | refused |
| 13 | a pre-cutover version with `created_at` moved forward, then declared | refused (no membership) |

**Served login** (`SET ROLE bc_platform_runtime`, under its real grants):

| # | Vector | Result |
|---|---|---|
| L1 | the served login creates a version | its membership row is written by the SECURITY DEFINER trigger |
| L2 | the served login declares it | accepted |
| L3 | the served login UPDATEs a declaration | refused: permission denied |
| L4 | the served login INSERTs membership directly | refused: permission denied |
| L5 | the served login declares a pre-cutover version | refused |
| L6 | the served login changes the currency of its declared version | refused |
| L7 | the served login declares `currency` with places | refused |

**Rollback** (the real rollback file, `0030-rollback-transcript.txt`):
- **A:** on the proof clone, where declarations exist, it is refused: "output declarations exist (immutable evidence)".
- **B:** on a fresh restore: apply, ledger `applied`, rollback OK, then **0** objects remaining and the ledger showing `rolled_back`. Re-applying works. A double apply is refused at the absence precondition.
- **C:** without the ledger variables, it is refused.

## 5. Apply procedure (after the DB yes)

1. Confirm the window:
   - no live window open on gen-d2e52d;
   - the declaration-writer build is Codex-accepted and ready to serve in the same window;
   - read the grants-list for the DB yes grant and verify its bytes. It must pin the migration sha256 `c7da1454…` and the build.
2. Apply `0030_mcf_metric_output_declaration` with the bc-db runner, on the bootstrap plane. The runner records the ledger event; keep the transcript.
3. Verify: 1 policy row, 0 members, 0 declarations, 9 `trg_mod_*` triggers, the served login's exact grants, and unchanged counts of existing versions.
4. Serve the declaration-writer build in the same window, and prove that one new version is created with its declaration under the served login.
5. **Rollback:** the rollback file, with the operator's authority, only while zero declarations exist. After that, stop writing declarations (governance). Never DROP populated immutable evidence.

## 6. Risk

**Low data risk, high operational risk if sequenced wrongly.**
- **Data:** the change is additive, with no rewrite, and existing behaviour is untouched for all 450 versions.
- **Operations:** the declaration requirement blocks approval of new versions until the writer serves (§3). Mitigation: a single coordinated window.
- **Privilege:** the served login gains only SELECT on the new tables and INSERT on the declaration; the guards run as `bc_schema_owner`.
