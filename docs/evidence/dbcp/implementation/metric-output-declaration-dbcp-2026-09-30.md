---
uid: metric-output-declaration-dbcp-2026-09-30
title: "DBCP — metric output declaration (migration 63; ADR DEC-b1e9eb)"
description: "Adds mcf.metric_output_declaration (1:1 with a post-cutover metric contract version: unit, decimals, rounding), its immutable cutover membership written at version creation, and the guards that require a declaration before a new version freezes. Additive; no backfill; existing versions untouched. Clone-proved (13 vectors plus rollback). NOT APPLIED: needs the operator's explicit DB yes, applied together with the declaration writer."
status: proposed
date: 2026-09-30
project: bc-core
domain: metrics
subdomain: metric-contract
focus: output-declaration
supersedes:
superseded_by:
---

# DBCP — metric output declaration (migration 63)

**Decision:** ADR DEC-b1e9eb (D636, proposed). The design was accepted with boundary by the auditor on gen-fe8f9d-03, after three rounds.

**Task:** TSK-af9706. **Author:** SES-a5e264.

**Status: NOT APPLIED.** Applying is a separate act. It needs the operator's explicit DB yes, recorded as a bc-exchange grant.

## 1. What changes

The migration is bc-core `docker/redesign/63-mcf-metric-output-declaration.sql` (sha256 `96c1df1c55277ffdcdc8255a58b80705211bbb6afce1c4c9153d3c812aeb9bef`). Its rollback is `63-mcf-metric-output-declaration-rollback.sql` (sha256 `a7118e509f5431e4bdcc678a52c16c29e7a0430e6a29f28bfd19c52b44e42feb`).

**New tables** (schema `mcf`):

| Table | Columns | Rules |
|---|---|---|
| `metric_output_declaration_policy` | `policy_code` PK, `cutover_at`, `recorded_by_name` | One row, written by the migration. Immutable. An audit record only: no gate reads it. |
| `metric_output_declaration_required` | `metric_contract_version_uid` PK/FK, `recorded_at` | Cutover **membership**: one row per version created after the apply, written by `trg_mod_mcv_membership`. Immutable. A direct INSERT is refused (`pg_trigger_depth() < 2`). |
| `metric_output_declaration` | `metric_contract_version_uid` PK/FK, `unit_type_code` FK → `master.master_unit_type`, `decimal_places_count` (0–6, NULL exactly when the unit is `currency`), `rounding_mode_code` (`half_up` default, or `half_even`), `declared_at`, `declared_by_name` | 1:1 with the version. Immutable. |

**New triggers** (9 in total, all named `trg_mod_*`):
- **Immutability:** on the policy, membership and declaration tables.
- **Membership:** writes the membership row at version INSERT.
- **Declaration insert guard:** a declaration needs membership and an unfrozen parent. "Frozen" uses the platform predicate: a frozen governance state, or `fn_mcv_has_approval_snapshot`.
- **Currency coherence:** a deferred constraint trigger. Unit `currency` needs a currency `aggregation_currency_code`; every other unit needs `not_applicable`.
- **Version update guard:** the parent's currency is frozen once a declaration exists, and a member version cannot enter a frozen state without its declaration.
- **Snapshot guard:** a member version gets no package snapshot without its declaration.

**Rules and size:**
- Naming follows ISO 11179.
- There is no JSONB, and each table has fewer than 20 columns.
- Every foreign key is declared. Indexes are the primary keys only: every lookup is by version uid.

**Rows at apply:** 1 policy row, 0 members and 0 declarations. The migration's own verification block asserts these counts and the 9 triggers.

## 2. What does not change

- **No existing table's columns or rows change.** Existing versions (450 in the clone of `bc_platform_dev`) get no membership. They can never gain a declaration, and their evaluation and package identity are untouched. There is no backfill (Invariants III and V).
- **No existing digest changes.** The package `output_digest` starts covering the declaration only in the later package-format slice (v4), which must agree with the auditor validator.

## 3. Sequencing constraint (blocking)

From the apply on, **every new metric contract version is a member**, and needs its declaration before approval or a package snapshot.

- The only governed writer of new versions is `src/registry/mcf/mcf-cert-writer.service.ts`. It is the only non-test file that inserts `mcf.metric_contract_version`; checked by grep of bc-core src.
- **Apply this DDL only in the same deploy window that serves the cert-writer change writing the declaration** (the authoring slice). Otherwise approval of every new metric stops.
- The umbrella coordinates that window with the live arcs (Kaveri coverage). It must be announced on gen-d2e52d.

## 4. Clone proof (2026-09-30)

**How the proof was run:**
- A throwaway `postgres:17-alpine` container, bound to 127.0.0.1 only.
- It was restored from a read-only `pg_dump -Fc` of `bc_platform_dev` (202 MB database, 450 versions), then removed after the run.
- Nothing ran against the live database.
- The migration applied cleanly, and its verification block passed.
- For vectors whose refusal a pre-existing platform trigger would raise first, the proof also runs an **isolated** variant, disabling that one trigger on the clone, to show the new gate itself refuses. Those triggers are `trg_mcf_mcv_state_transition`, `trg_mcv_package_snapshot_guard`, and for V10 `trg_mcv_grain_entity_version_guard`.

**Evidence files** (in this directory, `metric-output-declaration/`):

| File | sha256 |
|---|---|
| `m63-vectors.sql` | `448878ffa2fb3da2cf42cec79f0518d39612759d9a7c86a452c512f5107bdf95` |
| `m63-vectors-transcript.txt` | `55b4eb01c224917451aaecd76ad04e80f332b631f4f8b0ca09bc4919b724d722` |
| `m63-rollback-transcript.txt` | `0a618a77a19fdeaf6fa02e1210a87524a0a2a9de00ae90a2f924bdd836c04580` |

**Results** (every row passed; the transcript ends "ALL VECTORS PASSED: 2 declarations, 4 members"):

| # | Vector | Result |
|---|---|---|
| setup | 4 new versions | 4 membership rows written by the trigger; pre-cutover versions have none |
| 1 | `days` / 2 / `half_up` on a post-cutover draft with `not_applicable` (the DSO shape) | accepted |
| 2 | `currency` with places 2; `days` on a `local_currency` version | both refused: `chk_…places_by_unit`; incoherent currency |
| 3 | `days` with NULL places | refused |
| 4 | a declaration on a pre-cutover version | refused: predates the cutover |
| 5 | a declaration on a frozen, declared member | refused: frozen |
| 6 | an undeclared member entering `approved` | refused by the new gate (isolated), and by the platform state rules (realistic) |
| 7 | a package snapshot for an undeclared member | refused by the new gate (isolated) |
| 8 | changing the currency on a declared draft | refused: frozen by the declaration |
| 9 | UPDATE or DELETE of a declaration and of the policy row | refused |
| 10 | a pre-cutover version entering `approved` (isolated) | accepted: the new gate does not apply |
| 11 | a member with `created_at` backdated to 2020: approval, and a snapshot | both refused (membership holds) |
| 12 | UPDATE or DELETE of a membership row; a direct INSERT for a pre-cutover version | refused |
| 13 | a pre-cutover version with `created_at` moved forward, then declared | refused (no membership) |

**Rollback** (`m63-rollback-transcript.txt`):
- On the proof clone, where declarations exist, the rollback is refused: "output declarations exist (immutable) — roll back by governance, not DROP".
- On a fresh restore: apply, then rollback, leaves **0** `metric_output*` relations. Re-applying works. A second apply on top of an existing one is refused at the migration's absence precondition (fail-closed).

## 5. Apply procedure (after the DB yes)

1. Confirm the window:
   - no live window open on gen-d2e52d;
   - the declaration-writer build is ready to serve in the same window;
   - read the grants-list for the DB yes grant and verify its bytes.
2. Apply `63-mcf-metric-output-declaration.sql` with `psql -v ON_ERROR_STOP=1` to `bc_platform_dev`. Record the event in `infrastructure.schema_migration_event` and keep the transcript.
3. Verify: 1 policy row, 0 members, 0 declarations, 9 `trg_mod_*` triggers, and unchanged counts of existing versions.
4. Serve the declaration-writer build in the same window, and prove one new version is created with its declaration.
5. **Rollback:** the rollback file, only while zero declarations exist. After that, stop writing declarations (governance). Never DROP populated immutable evidence.

## 6. Risk

**Low data risk, high operational risk if sequenced wrongly.**
- **Data:** the change is additive, with no rewrite. Existing behaviour is untouched for all 450 versions.
- **Operations:** the declaration requirement blocks approval of new versions until the writer serves (§3). Mitigation: a single coordinated window.
