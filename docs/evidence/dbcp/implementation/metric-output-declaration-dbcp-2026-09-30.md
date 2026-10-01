---
uid: metric-output-declaration-dbcp-2026-09-30
title: "DBCP — metric output declaration (bc-db migration 0032, renumbered from 0030; ADR DEC-b1e9eb)"
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

# DBCP — metric output declaration (bc-db migration 0032)

**Decision:** ADR DEC-b1e9eb (D636, proposed). The design was accepted with boundary by the auditor on gen-fe8f9d-03, after three rounds.

**Task:** TSK-af9706.
- **Author:** SES-a5e264 (ended).
- **Owner since 2026-09-30:** the DB Controller, for the migration PR, this DBCP and the re-review. The Metric Controller owns the declaration semantics and the bc-core slice (the Chief's routing).

**Renumbered 0030 → 0032** (the Chief Controller's ruling, 2026-09-30T16:00Z), so that the ledger-only bc-db 0031 (merged `e47c1c8`) is not held behind this migration's joint window.
- The live order is 0028 → 0029 → 0031 → 0032.
- The rename changes only the migration-number literals: the header, the RAISE texts, the rollback's ledger name and psql variables. The rollback is re-pinned to the new migration sha256.
- The body is otherwise byte-identical to `ec1aba34` (the gen-fe8f9d-05 fix).
- The number 0030 is recorded as a gap in bc-db `docs/migration-number-gaps.md`.

**Status: NOT APPLIED.** Applying is a separate act. It needs the operator's explicit DB yes, recorded as a bc-exchange grant.

**Where the migration lives:** bc-db `migrations/0032_mcf_metric_output_declaration.sql` (PR bc-db#98, head `b840b8e0`).
- It supersedes the first draft, bc-core#897, which was written in bc-core `docker/redesign`. That tree is frozen by ADR DEC-4c1396: bc-core CI `docker-redesign-freeze.spec.ts` failed the draft, run 36669976926.
- Platform schema changes are bc-db forward migrations.

## 1. What changes

**Files:**

| File | sha256 |
|---|---|
| migration `migrations/0032_mcf_metric_output_declaration.sql` | `16c8cde599671936088352b167957858e652c1b7816345bea58e6f4256279f4f` |
| rollback `rollback/0032_mcf_metric_output_declaration.rollback.sql` | `c582689a4b991eb8b5be875afe4a9b8f1e51de8a41edbc740fd6a93484327918` |

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
  - It also checks currency coherence **under a `FOR NO KEY UPDATE` lock on the parent row**: the same lock an UPDATE takes (added for Codex gen-fe8f9d-05).
  - A concurrent currency change on the same version therefore serializes with the insert. Either it waits, and then the update guard sees the declaration and refuses; or it commits first, and the insert sees it and refuses.
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
- **Apply 0032 only in the same deploy window that serves the bc-core build whose cert writer writes the declaration** (the authoring slice). Otherwise approval of every new metric stops.
- The umbrella's window plan puts this in the joint cutover window: 0032, plus the authoring slice, plus the DECLARED_DECIMAL evaluator, under one operator grant that pins the migration bytes and the build. It must be announced on gen-d2e52d.

## 4. Clone proof (2026-10-01T05:38Z, run 3: after the Repeatable Read fix, gen-fe8f9d-06; owner- and grant-faithful)

**What changed in run 3:** `mcf.fn_mod_mcv_update_guard` now refuses an `aggregation_currency_code` change unless `transaction_isolation` is `read committed` (bc-db `b840b8e0`). At READ COMMITTED its declaration read takes a fresh snapshot after the UPDATE waits on the declaration's `FOR NO KEY UPDATE` parent lock. At REPEATABLE READ or SERIALIZABLE the snapshot can predate a committed declaration (Codex's blocking residual). Race vectors R3 (REPEATABLE READ) and R4 (SERIALIZABLE) are added, with a second red check on the round-2 bytes `ec3946e1`. Run 2 (2026-09-30T12:45Z, dump `e2969fea…`) is superseded.

**The driver:** `metric-output-declaration/0032-clone-proof.zsh`, with its transcript `0032-clone-proof.txt`. Every evidence file is hashed in `metric-output-declaration/MANIFEST.sha256`.

**Source:**
- A fresh read-only `pg_dump -Fc` of live `bc_platform_dev` (dump sha256 `17579ba1c279b22f7f501e9345869707325674e6cfc1423e974d16ffd264780a`; live ledger 32 rows / max seq 35), plus `pg_dumpall --roles-only --no-role-passwords`.
- Restored **with owners and grants** into a throwaway container of the pinned engine, with **no published port**. The script refuses a clone that reports the live system identifier (7689410286420172840).
- The dump was restored into four databases:
  - `bc_platform_dev`: the proof;
  - `prev_bytes`: the previous, unfixed bytes `c7da1454…` (bc-db `46453b57`, then named 0030), for the race red check;
  - `rr_prev`: the round-2 bytes `ec3946e1…` (bc-db `99dfd55f`, the READ COMMITTED fix only), for the R3/R4 red check;
  - `rb_fresh`: the rollback test.
- 0 restore errors; 451 versions.
- **The container, the dump and the runner tree were removed after the proof.** Nothing ran against live.

**The window's true pre-state first, on all four databases, through the bc-db runner** (bc-db main `209ff624`):
- 0029;
- then the 0031 window: 0003, 0031, and `record-exception` for 0001, 0002 and 0008.

**Apply:**
- 0032 (sha256 `16c8cde5…`) was applied **through the bc-db runner**, from a staged directory holding only 0032: the same command as live.
- Its in-transaction verification passed: 1 policy row, 0 members, 0 declarations, 9 `trg_mod_*` triggers, ownership, the served login's exact grants, and SECURITY DEFINER.
- The runner recorded the ledger `applied` event. This replaces the earlier proofs' hand-recorded ledger call, so the transcript-clarity note from gen-fe8f9d-05 no longer arises.

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

**Two-session race vectors** (`0032-race.zsh`, `0032-race-transcript.txt`; Codex gen-fe8f9d-05 and -06). Four draft members, X, Y, Z and W, start at `not_applicable`. In R3 and R4 the updater T2 opens its transaction at the named isolation level and takes its snapshot (`SELECT 1`) while T1's declaration is still uncommitted.

| Case | What happens | Fixed bytes `16c8cde5` (0032) | Round-2 bytes `ec3946e1` (red check) | Previous bytes `c7da1454` (red check) |
|---|---|---|---|---|
| **R1, update first** (READ COMMITTED) | T2 sets X to `local_currency`, holds 4 s; T1 declares X `days` at +1 s | T1 waits, then is refused (incoherent). Final: no declaration / local_currency | the same, refused | T1 commits: **days / local_currency, incoherent** |
| **R2, declaration first** (READ COMMITTED) | T1 declares Y `days`, holds 4 s; T2 sets Y to `local_currency` at +1 s | T2 waits, then is refused (frozen). Final: days / not_applicable | the same, refused | T2 commits |
| **R3, declaration first, T2 at REPEATABLE READ** | as R2, on Z | T2 waits, then is **refused** ("may change only at READ COMMITTED, not repeatable read"). Final: days / not_applicable | T2 **commits**: **days / local_currency, incoherent** | T2 commits |
| **R4, declaration first, T2 at SERIALIZABLE** | as R2, on W | T2 waits, then is **refused** ("… not serializable"). Final: days / not_applicable | T2 **commits**: **days / local_currency, incoherent**. PostgreSQL's serializable checking did not catch it | T2 commits |
| **Incoherent pairs afterwards** | | **0** | **2** | **1** |

**Behaviour change, stated plainly:** any change of a version's `aggregation_currency_code` at REPEATABLE READ or SERIALIZABLE is now refused, declared or not. No bc-core `src` path changes the currency today (specs only); `mcf-cert-writer`'s REPEATABLE READ transactions are the audit and admission paths, which do not touch it.

**Rollback** (the real rollback file, `0032-rollback-transcript.txt`):
- **A:** on the proof clone, where declarations exist, it is refused: "output declarations exist (immutable evidence)".
- **B:** on a fresh restore (`rb_fresh`): apply through the runner, ledger `applied`, rollback OK, then **0** tables, triggers and functions remaining, and the ledger showing `rolled_back`. Re-applying through the runner works. Running the SQL directly a second time is refused at the absence precondition.
- **C:** without the ledger variables, it is refused.

## 5. Apply procedure (after the DB yes)

1. Confirm the window:
   - no live window open on gen-d2e52d;
   - the declaration-writer build is Codex-accepted and ready to serve in the same window;
   - read the grants-list for the DB yes grant and verify its bytes. It must pin the migration sha256 `16c8cde5…` and the build.
2. Apply `0032_mcf_metric_output_declaration` with the bc-db runner, on the bootstrap plane. The runner records the ledger event; keep the transcript.
3. Verify: 1 policy row, 0 members, 0 declarations, 9 `trg_mod_*` triggers, the served login's exact grants, and unchanged counts of existing versions.
4. Serve the declaration-writer build in the same window, and prove that one new version is created with its declaration under the served login.
5. **Rollback:** the rollback file, with the operator's authority, only while zero declarations exist. After that, stop writing declarations (governance). Never DROP populated immutable evidence.

## 6. Risk

**Low data risk, high operational risk if sequenced wrongly.**
- **Data:** the change is additive, with no rewrite, and existing behaviour is untouched for all 450 versions.
- **Operations:** the declaration requirement blocks approval of new versions until the writer serves (§3). Mitigation: a single coordinated window.
- **Privilege:** the served login gains only SELECT on the new tables and INSERT on the declaration; the guards run as `bc_schema_owner`.
