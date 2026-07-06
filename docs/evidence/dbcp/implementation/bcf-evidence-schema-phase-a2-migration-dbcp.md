---
uid: bcf-evidence-schema-phase-a2-migration-dbcp
title: BCF Evidence Schema — Phase A2 Migration DBCP (3,568 authority-bearing BCF rows; contract.* → bcf.*; insert-copy; smoke debt excluded)
description: Phase A2 design DBCP for migrating authority-bearing BCF evidence rows from generic `contract.*` evidence tables into the new `bcf.*` substrate created by Phase A1 (applied at bc-core `2026-05-29T02-11-41-745Z`, verdict APPLY PASS). Exact migration scope is 3,568 rows = 19 authority `contract.panel_output_record` + 0 authority `contract.authoring_panel_rejection_log` + 19 authority `contract.calibration_event` + 3,530 authority (non-synthetic) `contract.certification_record`. The 11 smoke rows (5 panel + 1 rejection_log + 4 calibration + 1 synthetic cert) are explicitly excluded and are retired by bc-core PR #133 cleanup apply at its own separately-authorized gate which must execute BEFORE Phase A2 apply (parent boundary DBCP §13 step 8). Migration is **insert-copy only** — original `contract.*` rows remain in place (Phase A4 owns the freeze/retire of the source tables; Phase A3 owns the writer/reader cutover that makes the duplication unobservable). **NOT EXECUTED.** This DBCP does NOT apply DML, does NOT migrate rows, does NOT delete `contract.*` rows, does NOT touch `mcf.*` / `metric.*` / `concept_registry.*` / tenant DBs, does NOT execute PR #133 apply, does NOT run rollback, does NOT invoke M11/M12/M12.5/M13. M14 remains CLOSED. PR #133 apply gate remains PAUSED per parent D9 — this DBCP's apply gate is a SEPARATE follow-up after PR #133 apply executes. Operator stance ADR DEC-7f9597 / D423 honoured throughout — substrate truth is inviolate; smoke retirement precedes authority migration; the additive HR1 substrate CHECKs on `bcf.panel_output_record` and `bcf.certification_record` will reject any synthetic-provider row that survived PR #133 apply.
status: draft
date: 2026-05-29
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-evidence-schema-phase-a2-row-migration
supersedes:
superseded_by:
---

# BCF Evidence Schema — Phase A2 Migration DBCP

## 1. Scope

### 1.1 Question this DBCP answers

> Under the operator-authorized Option A path with Phase A1 applied (bcf.* substrate present and empty at bc-core `2026-05-29T02-11-41-745Z`), what is the exact migration design — row classification, dependency order, idempotency model, dry-run plan, apply plan, rollback plan — for moving the 3,568 authority-bearing BCF rows from `contract.*` into `bcf.*` while explicitly excluding the 11 smoke rows that PR #133 cleanup apply retires at its own separately-authorized gate?

### 1.2 In scope

- Authority/smoke row classification with byte-pinned UIDs (5 + 1 + 4 + 1 = 11 smoke; 19 + 0 + 19 + 3,530 = 3,568 authority)
- Insert-copy migration strategy from `contract.*` → `bcf.*`
- Per-table dependency / order model: `bcf.panel_output_record` first (root), then leaves
- HR1 substrate guard interaction: the 2 new no-synthetic CHECKs on `bcf.panel_output_record` + `bcf.certification_record` will reject synthetic-provider rows. PR #133 apply must retire those before A2.
- Idempotency model decision (ON CONFLICT DO NOTHING vs strict-empty enforcement) with explicit operator decision
- Pre-A3 rollback design (delete A2-inserted rows from `bcf.*` leaves-first; do NOT drop schema)
- Relationship to PR #133 apply (must precede A2 apply)
- Relationship to A3/A4/A5
- Risks (R1..R12)
- Operator decisions D1..D12
- Authorization to author 3 bc-core scripts in a follow-up PR: dry-run, apply, rollback

### 1.3 Explicit non-scope

- ❌ **No DML apply.** This DBCP authorizes the *authoring of scripts*; their apply gate is a separately operator-authorized follow-up.
- ❌ **No DDL.** Phase A1 ships the substrate; A2 only INSERTs into already-existing `bcf.*` tables.
- ❌ **No `contract.*` row deletion.** A2 is insert-copy; the source tables remain populated (Phase A4 owns freeze/retire).
- ❌ **No writer/reader flip.** Phase A3 owns this. BCF authoring writers continue to INSERT into `contract.*` during A2; readers continue to SELECT from `contract.*`.
- ❌ **No `mcf.*` FK retarget.** Phase A5 owns the 5 mcf→contract FK redirects.
- ❌ **No `mcf.*` / `metric.*` / `concept_registry.*` touch.** A2 only writes to `bcf.*` and only reads from `contract.*`.
- ❌ **No tenant `tbc_{slug}_dev` DB connection.** Substrate-enforced via env-var separation.
- ❌ **No PR #133 apply or restore execution.** PR #133 cleanup is the *prerequisite* gate but is operator-authorized separately.
- ❌ **No bc-core source edit outside the 3 follow-up scripts.** No service code, no Drizzle schema flip.
- ❌ **No M11 / M12 / M12.5 / M13 invocation.** M14 remains CLOSED.
- ❌ **No `framework_policy` placement.** Parent D7 deferred.
- ❌ **No re-litigation of Option A target.** `bcf.*` is the locked target; `concept_registry.*` is BCR vocabulary and remains untouched (assertion stays from Phase A1 apply DBCP §6).

## 2. Authority

| Artifact | Location | Authority for |
|---|---|---|
| Boundary DBCP (Option A) | `docs/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` @ bc-docs-v3 main `6f8cc15` | Option A target; 5-phase ladder; §13 step 8 PR-#133-apply-before-A2 sequencing |
| D1-D11 decision record | `docs/implementation/bcf-mcf-evidence-boundary-operator-decisions-d1-d11.md` @ bc-docs-v3 main `70beeb7` | D2=A; D4=Phase A1+A2 design authorization; D9=PAUSE PR #133 apply until A1+A2 designs accepted |
| Phase A1 substrate-design DBCP | `docs/implementation/bcf-evidence-schema-phase-a1-dbcp.md` @ bc-docs-v3 main `70beeb7` | `bcf.*` column / CHECK / index / FK shape; HR1 substrate enforcement design |
| Phase A1 apply DBCP | `docs/implementation/bcf-evidence-schema-phase-a1-apply-dbcp.md` @ bc-docs-v3 main `cdc6efa` | Apply-gate pattern (env-gate + sha256 + single-tx + post-apply assertions + pre-A2-only rollback) — mirrored in A2 design below |
| PR #134 (Phase A1 scripts) | bc-core main `61f2e02` | The dry-run / apply / rollback scripts whose pattern A2 mirrors |
| PR #135 (Phase A1 apply evidence) | bc-core main `09035b8` | Confirms Phase A1 apply succeeded with verdict APPLY PASS; `bcf.*` substrate live and empty |
| Smoke cleanup DBCP | `docs/implementation/bcf-authoring-test-row-cleanup-dbcp.md` @ bc-docs-v3 main `0f42662` | 11-row smoke debt identification + the byte-pinned UIDs reproduced in §3 below |
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) @ bc-docs-v3 main `cdc6efa` | No substrate shortcuts; PR #133 apply must precede A2 (no gate cascades); substrate-bound HR1 inviolate |
| Hard rules HR1..HR5 | parent DBCP §5 | Substrate constraints enforced by A2 design |
| Live DB shape (this DBCP §3) | `bc-postgres` MCP `allow_write=false` probes against `bc_platform_dev` @ 2026-05-29 post-PR-#135-merge | Authority/smoke counts; pinned UIDs |

## 3. Current state (read-only baseline; live-verified)

All numbers verified via `bc-postgres` MCP with `allow_write=false`.

### 3.1 Substrate state

| Surface | Today | A2 apply changes? |
|---|---|---|
| `bcf` schema | present (Phase A1 applied) | NO — schema unchanged |
| `bcf.panel_output_record` rows | **0** | YES → INSERT 19 authority rows |
| `bcf.authoring_panel_rejection_log` rows | **0** | NO authority rows; INSERT 0 |
| `bcf.calibration_event` rows | **0** | YES → INSERT 19 authority rows |
| `bcf.certification_record` rows | **0** | YES → INSERT 3,530 authority rows |
| `contract.panel_output_record` rows | **24** (19 authority + 5 smoke) | NO — A2 is insert-copy; source unchanged |
| `contract.authoring_panel_rejection_log` rows | **1** (1 smoke; 0 authority) | NO |
| `contract.calibration_event` rows | **23** (19 authority + 4 smoke) | NO |
| `contract.certification_record` rows | **3,531** (3,530 authority + 1 synthetic-smoke) | NO |
| `mcf.*` 17 tables, 0 rows total | 0 | NO (Phase A5 owns mcf substrate change) |
| `concept_registry.*` 11 tables, 68 rows total | 68 | NO (BCR vocabulary; out of scope) |
| Tenant `tbc_{slug}_dev` DBs | not connected to | NO (D11 out of scope) |
| 9 inbound FKs on `contract.panel_output_record.panel_run_uid` | intact | NO (A5 retargets the 5 mcf ones) |

### 3.2 Authority / smoke classification (live-verified)

Source row counts split by smoke-UID predicate:

| Table | Authority | Smoke | Total | Smoke UID predicate |
|---|---|---|---|---|
| `contract.panel_output_record` | **19** | 5 | 24 | `panel_run_uid IN (5 UIDs in §3.3)` |
| `contract.authoring_panel_rejection_log` | **0** | 1 | 1 | `rejection_log_id = '0cc5ad4b-a727-4238-b07c-3b33e3e513e6'` |
| `contract.calibration_event` | **19** | 4 | 23 | `panel_run_uid IN (5 UIDs in §3.3; one panel has no calibration row)` |
| `contract.certification_record` | **3,530** | 1 | 3,531 | `certification_record_id = '21023aa1-ddf0-4f42-9100-7242bcf5bf6f'` |
| **TOTAL** | **3,568** | **11** | **3,579** | — |

`bcf.authoring_panel_rejection_log` will remain empty after A2 because the only `contract.authoring_panel_rejection_log` row is smoke. The migration explicitly skips this table at the apply layer (no INSERT statement emitted) and the post-apply assertion permits `bcf.authoring_panel_rejection_log` row count = 0.

### 3.3 Pinned smoke UIDs (live-verified at 2026-05-29 baseline)

**5 smoke `contract.panel_output_record` UIDs:**

| `panel_run_uid` | `prompt_version` | `policy_version` | `verdict_code` | `created_at` |
|---|---|---|---|---|
| `c05258de-8a62-456e-89fd-220a16684268` | `smoke-test-v0` | `smoke-test/pr10` | `APPROVE_FOR_DRAFT` | 2026-05-20T12:03:25Z |
| `54890bec-28cb-4d55-8aeb-fb3f81e0b359` | `v1.0` | `context-smoke/2026-05-20` | `FAIL_QA_GATE` | 2026-05-20T13:15:17Z |
| `c6d85db6-c466-4993-8fdf-959ae33ffbe2` | `bcf-live-smoke/2026-05-20` | `v1` | `APPROVE_FOR_DRAFT` | 2026-05-20T15:13:33Z |
| `c20f4d65-2021-451f-aebb-10cc8ca1249c` | `bcf-live-smoke/2026-05-20` | `v1` | `REJECT` | 2026-05-20T15:13:33Z |
| `6aaad537-eab9-4bca-a6cc-4acff74211ff` | `v1.0` | `bcf-roster-smoke/2026-05-20` | `FAIL_QA_GATE` | 2026-05-20T15:54:33Z |

**1 smoke `contract.authoring_panel_rejection_log` UID:**

- `rejection_log_id = '0cc5ad4b-a727-4238-b07c-3b33e3e513e6'`

**4 smoke `contract.calibration_event` UIDs (one per smoke panel except `c05258de` which has no calibration row):**

| `calibration_event_uid` | linked `panel_run_uid` |
|---|---|
| `8a51c710-11eb-4ab8-9d6b-88955ee2553c` | `54890bec-28cb-4d55-8aeb-fb3f81e0b359` |
| `7d1a2c25-e5eb-4e4b-8032-918dccb0c7b4` | `c6d85db6-c466-4993-8fdf-959ae33ffbe2` |
| `9d20f4ce-ade6-4489-94b9-f5423a9e364c` | `c20f4d65-2021-451f-aebb-10cc8ca1249c` |
| `4db0d205-5cd1-4cc5-8fbd-9be15a61f165` | `6aaad537-eab9-4bca-a6cc-4acff74211ff` |

**1 smoke `contract.certification_record` UID (synthetic-provider):**

- `certification_record_id = '21023aa1-ddf0-4f42-9100-7242bcf5bf6f'`

These 11 UIDs match the bytes pinned in the smoke cleanup DBCP (`bcf-authoring-test-row-cleanup-dbcp.md` @ `0f42662`) and PR #133's dry-run precondition.jsonl. PR #133 apply retires these 11 rows from `contract.*`; A2 must run after that retirement (post-retirement, source counts become 19 / 0 / 19 / 3,530 and the smoke-UID predicates return empty sets — A2's selector then simply copies "everything remaining in `contract.*`" into `bcf.*`).

## 4. Migration scope (precise)

### 4.1 What moves

3,568 authority-bearing BCF evidence rows = 19 panel + 0 rejection_log + 19 calibration + 3,530 cert.

### 4.2 What does NOT move

- The 11 smoke rows (5 + 1 + 4 + 1). Retired by PR #133 apply BEFORE A2.
- Any `concept_registry.*` row (BCR vocabulary; out of scope).
- Any `contract.framework_policy` row (parent D7 deferred to separate placement gate).
- Any `mcf.*` row (none exist; all 17 tables empty).
- Any `metric.*` row (legacy; out of scope per parent D11).
- Any `contract.*` chain-infrastructure row (`source_contract`, `admission_contract`, `canonical_*`, `observation_*`, `chain_status`, etc.) — different concern from authoring boundary.

### 4.3 Why insert-copy (not move-and-delete)

- **HR1 substrate enforcement requires PR #133 first.** The 2 new no-synthetic CHECKs on `bcf.panel_output_record` + `bcf.certification_record` will reject the 1 synthetic-provider cert and any synthetic-provider panel row. PR #133 apply retires that smoke before A2 runs.
- **Phase A3 owns the writer/reader cutover.** Until A3, `contract.*` writers continue to INSERT into `contract.*` and readers continue to SELECT from `contract.*`. Removing `contract.*` rows before A3 would break those paths.
- **Phase A4 owns `contract.*` freeze/retire.** A2 must NOT pre-empt A4. The source tables stay populated and the migration leaves them readable for the duration of A2→A3→A4.
- **Audit safety.** Original `contract.*` rows remain available for audit comparison against `bcf.*` rows until A4 commits to the destructive step.

## 5. Hard rules (restated)

- **HR1** — No synthetic / mock / replay / canned data written to persistent substrate. The 2 substrate CHECKs added in Phase A1 reject synthetic-provider rows on INSERT. **A2 apply will fail if PR #133 apply has not run** because the synthetic-smoke cert (uid `21023aa1`) will be rejected by `bcf_certification_record_no_synthetic_provider_chk`.
- **HR2** — MCF evidence belongs in `mcf.*`. A2 does not touch MCF.
- **HR3** — Future MCF metric authority events MUST NOT write to generic `contract.*` authoring tables. A2 does not change MCF behaviour; Phase A5 will retarget the M12 writer.
- **HR4** — Tenant result DBs are separate and out of scope. A2 only touches platform DB `bc_platform_dev`.
- **HR5** — Mocks only inside unit tests or SAVEPOINT-rolled-back integration tests. Production scripts contain no mocks.

## 6. Dependency / order model

### 6.1 INSERT order (roots first, leaves second)

Inside the A2 apply transaction:

| Step | Operation | Source predicate | Target | Expected row count |
|---|---|---|---|---|
| 1 | `INSERT INTO bcf.panel_output_record SELECT * FROM contract.panel_output_record WHERE panel_run_uid NOT IN (5 smoke UIDs)` | authority panels | `bcf.panel_output_record` | 19 |
| 2 | `INSERT INTO bcf.calibration_event SELECT * FROM contract.calibration_event WHERE panel_run_uid NOT IN (5 smoke UIDs)` | authority calibrations | `bcf.calibration_event` | 19 |
| 3 | `INSERT INTO bcf.certification_record SELECT * FROM contract.certification_record WHERE certification_record_id <> '21023aa1-…'` | authority certs | `bcf.certification_record` | 3,530 |
| 4 | (no-op for `bcf.authoring_panel_rejection_log`; no authority rows) | — | `bcf.authoring_panel_rejection_log` | 0 |

Step 1 must complete before steps 2 and 3 because the intra-`bcf.*` FKs `fk_bcf_calibration_event__panel_run` and `fk_bcf_certification_record__panel_run` reference `bcf.panel_output_record(panel_run_uid)`.

### 6.2 Why this order is FK-safe

- `bcf.panel_output_record` has no inbound FKs from other `bcf.*` tables at insert time except those declared from the leaves (calibration_event, certification_record). Inserting it first satisfies the leaves' FK references.
- The leaves' `panel_run_uid` values must already exist in `bcf.panel_output_record`. By inserting roots first, this is guaranteed.
- `bcf.authoring_panel_rejection_log` is also a leaf but has 0 authority rows to insert; no FK reference is exercised.

### 6.3 Single-transaction discipline

All 3 INSERT statements run inside one `BEGIN; ... COMMIT;` block. A failure mid-transaction triggers automatic ROLLBACK and `bcf.*` returns to empty. No partial state persists.

### 6.4 Value preservation

Each INSERT uses `SELECT *` (or an explicit column list in the same order) — all original `uuid` PKs, `timestamptz` columns, `jsonb` payloads, and other values are preserved byte-for-byte. The migrated row has the same `panel_run_uid` / `rejection_log_id` / `calibration_event_uid` / `certification_record_id` as its `contract.*` source. The same `created_at`, `model_identity_json`, `agent_outputs_json`, `gate_results_json`, etc. carry over unchanged.

## 7. Migration strategy

### 7.1 Insert-copy (not move-and-delete)

See §4.3. The `contract.*` source tables remain populated. A4 owns the freeze/retire step that eventually makes the source unreadable. Between A2 and A4, the same authority-bearing rows exist in BOTH `contract.*` AND `bcf.*`. Phase A3 flips writers/readers so the duplication becomes operationally invisible: writers stop appending to `contract.*` (new rows go to `bcf.*`) and readers stop reading from `contract.*` (queries hit `bcf.*`).

### 7.2 Idempotency model — operator decision D3

Two viable patterns; operator chooses one:

**Option A (RECOMMENDED) — Strict empty target enforcement.** Pre-apply guard: `SELECT count(*) FROM bcf.<each>` must equal 0 across all 4 tables. If any row exists, abort before any INSERT. Apply succeeds → tables transition from 0 to {19, 0, 19, 3530}. Re-running the apply (after a successful first run) is impossible — the strict-empty guard refuses. To re-run, operator must first run rollback (which restores empty `bcf.*` per §9).

- **Pro:** matches Phase A1's design pattern (strict-empty guard before DDL apply). Operator stance DEC-7f9597 §"Do NOT reduce: operator authorization for mutating gates" — a re-run is a new mutation that requires its own explicit authorization (via rollback + re-apply chain).
- **Con:** if the apply fails after partial INSERT but before transaction abort (e.g. coordinator crash), the script's pre-apply guard becomes incorrect for a subsequent re-run. Mitigation: the single-transaction wrapper makes partial commits impossible. A failure inside the transaction rolls back to empty automatically.

**Option B — `ON CONFLICT DO NOTHING` (rejected as default).** Each INSERT uses `ON CONFLICT (<pk>) DO NOTHING`. Re-running the apply against a partially-populated `bcf.*` would be a no-op for rows already present; new rows would be inserted.

- **Pro:** survives partial-apply scenarios without requiring rollback.
- **Con:** masks an unexpected state. If the operator runs A2 twice by accident (or A2 runs after a partial A3 cutover that already populated `bcf.*` via the new writers), `ON CONFLICT` silently accepts the second invocation. Operator stance §"Do NOT reduce" rejects this kind of silent re-mutation: every mutating event must be an explicit operator instruction at its own gate.

**Recommendation:** Option A (strict-empty enforcement). The single-transaction wrapper makes partial commits impossible, so the partial-apply risk Option B addresses is structurally absent. Option A keeps the substrate-bound discipline that the operator stance ADR makes inviolate.

### 7.3 No DELETE in A2

A2 never deletes from `contract.*` or from `bcf.*`. The script contains no `DELETE` statements. (Phase A4 owns the eventual `contract.*` freeze/retire; the Phase A1 rollback script owns the empty-only `DROP SCHEMA bcf CASCADE` if A2 is rolled back pre-A3.)

## 8. Relationship to existing `contract.*`

During A2 and through to Phase A3 cutover:

- BCF authoring writers continue to INSERT into `contract.panel_output_record` and friends. A2 does NOT redirect any writer.
- The 9-FK closure on `contract.panel_output_record.panel_run_uid` is intact (4 contract + 5 mcf).
- The 3 framework_policy rows in `contract.framework_policy` continue to serve both BCF and MCF runtime policy probes (parent D7 deferred).
- BCF readers continue to SELECT from `contract.*` until Phase A3 cutover.
- Once A2 ships, the same authority-bearing rows exist in BOTH `contract.*` AND `bcf.*`. The duplication is operationally tolerated until A3 cutover.

## 9. Pre-A3 rollback plan

### 9.1 Validity window — PRE-A3 ONLY

A2 rollback is safe **iff** Phase A3 has not yet flipped writers/readers. Once A3 ships and the BCF authoring code starts INSERTing new rows into `bcf.*`, deleting those rows would lose authority-bearing evidence that has no `contract.*` counterpart.

### 9.2 Pre-rollback guards

The A2 rollback script asserts BEFORE any DELETE:

1. Env var `BCCORE_BCF_PHASE_A2_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_<apply-timestamp>` present (matching the pattern from Phase A1).
2. Phase A3 has NOT shipped (operator-attestation; or a substrate marker — see §11 D10).
3. `bcf.*` row counts match the post-A2 baseline (19 / 0 / 19 / 3,530). If counts diverge (e.g. additional rows present, indicating A3 has shipped or external writes occurred), abort.
4. `contract.*` row counts match the post-PR-#133-apply baseline (19 / 0 / 19 / 3,530 in `contract.*` + 0 smoke). The rollback assumes the `contract.*` authority rows are intact and re-becomes the BCF source of truth on rollback.

### 9.3 Rollback DML (leaves-first DELETE order)

```
BEGIN;
  DELETE FROM bcf.calibration_event;                  -- 19 rows
  DELETE FROM bcf.certification_record;               -- 3,530 rows
  DELETE FROM bcf.authoring_panel_rejection_log;      -- 0 rows
  DELETE FROM bcf.panel_output_record;                -- 19 rows (root last)
COMMIT;
```

Leaves-first order is the inverse of the apply INSERT order — required because the 3 intra-`bcf.*` FKs are `ON DELETE RESTRICT`. Deleting `bcf.panel_output_record` rows while leaves still reference them would violate the FKs.

### 9.4 Post-rollback assertions

1. `bcf.*` all 4 tables back to 0 rows.
2. `contract.*` row counts unchanged (post-PR-#133-apply state: 19 / 0 / 19 / 3,530; **NOT** 24/1/23/3,531 — that's the pre-PR-#133-apply state).
3. `mcf.*` row counts unchanged (0 across 17).
4. `concept_registry.*` row counts unchanged (68 across 11).
5. 9 inbound FKs on `contract.panel_output_record.panel_run_uid` intact.
6. `bcf` schema still present (this is a row rollback, NOT a schema rollback). The Phase A1 rollback script (which executes `DROP SCHEMA bcf CASCADE`) is a SEPARATE operation; A2 rollback is row-only and leaves the schema in place.

### 9.5 No source restore needed

Because A2 is insert-copy and the source `contract.*` rows are never deleted during A2, no restore of `contract.*` is required on A2 rollback. The original 19+0+19+3,530 authority rows remain in `contract.*` continuously from PR #133 apply through A2 apply through A2 rollback.

### 9.6 Post-A3 rollback (explicit non-scope)

Once Phase A3 ships and BCF authoring writes new rows directly to `bcf.*`, the A2-rollback approach (delete all from `bcf.*` leaves-first) would destroy those new authority rows. **A3 must include its own rollback plan** that distinguishes A2-migrated rows from post-A3 newly-written rows. That rollback path is NOT covered here.

## 10. Relationship to PR #133

PR #133 (`bcf-authoring-test-row-cleanup-pr1-dry-run`, merged at bc-core main `204c1cf` as inventory tooling per parent D8) carries:

- `scripts/bcf-authoring-test-row-cleanup-dry-run.mjs` (read-only; dry-run already passed)
- `scripts/bcf-authoring-test-row-cleanup-apply.mjs` (env-gated; **NOT YET EXECUTED** per parent D9)
- `scripts/bcf-authoring-test-row-cleanup-restore.mjs` (env-gated; companion restore)
- 3 dry-run artifacts at `2026-05-28T15-10-48-199Z`

The PR #133 apply gate retires the 11 smoke rows from `contract.*`. Sequence per parent §13:

| Step | Gate | Trigger |
|---|---|---|
| 5 | Phase A1 design DBCP merged | parent D2=A + D4 |
| 6 | Phase A1 apply gate executed | bc-core PR #134 + operator instruction |
| 7 | Phase A1 closeout (PR #135 evidence merged) | operator authorization of merge |
| **8** | **Phase A2 DBCP merged** | **this DBCP** |
| **9** | **PR #133 apply gate executed** | **must precede A2 apply per parent §13 step 8** |
| 10 | Phase A2 apply gate executed | follow-up bc-core PR + operator instruction |
| 11 | Phase A2 closeout | operator authorization |

**A2 apply MUST fail if PR #133 apply has not run.** The mechanism: A2 dry-run's pre-apply probe #5 (no-synthetic source) returns non-zero counts (today: 2 panel + 1 cert with `provider IN ('synthetic','replay','mock','canned')`), so the dry-run reports those counts as BLOCKING. Even if the operator overrode the dry-run, the A2 apply script's pre-apply probe re-validates the same predicate; if non-zero, the substrate CHECKs on `bcf.*` reject the synthetic-cert INSERT and the entire transaction rolls back.

## 11. Relationship to Phase A3 / A4 / A5

| Phase | Owns | Effect on A2 design |
|---|---|---|
| A3 | BCF writer/reader cutover | A2 explicitly does NOT flip writers; A3 does. Until A3, `contract.*` writers stay live. After A3, `bcf.*` writers replace them; `contract.*` evidence tables become read-only by convention until A4. |
| A4 | `contract.*` evidence freeze (trigger + grant) or DROP | A2 explicitly does NOT freeze or drop the source. A4 makes the operational decision (freeze vs drop) once A3 cutover has soaked. |
| A5 | `mcf.*` FK reconsideration + M12 writer flip | Out of A2 scope. A2 does NOT touch the 5 `mcf.* → contract.panel_output_record` FKs. A5 creates `mcf.metric_authoring_panel_output_record` and redirects those FKs to intra-mcf. |

## 12. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Apply runs before PR #133 apply; the synthetic-cert INSERT trips the `bcf_certification_record_no_synthetic_provider_chk` CHECK and rolls back the whole transaction | LOW (script structure prevents) | HIGH (one full re-run cycle wasted) | Pre-apply probe verifies smoke is retired BEFORE first INSERT. Single-transaction wrapper means a CHECK failure costs only one connection round-trip, not partial state |
| R2 | Duplicate rows inserted by re-running the apply script | LOW | HIGH | Operator decision D3 = Option A (strict-empty guard). Pre-apply assertion: all 4 `bcf.*` at 0 rows. Re-run requires explicit rollback first |
| R3 | Partial copy (some rows inserted, others not) | LOW | HIGH | Single-transaction wrapper. Any error mid-tx triggers auto-rollback. Post-apply assertions check per-table row counts |
| R4 | Synthetic-provider row leakage (a `contract.*` row carrying `provider IN ('synthetic','replay','mock','canned')` reaches `bcf.*`) | LOW | CRITICAL | Substrate-bound HR1 CHECKs reject the INSERT before the row commits. Pre-apply probe re-validates source counts. PR #133 apply must retire the 1 known violation BEFORE A2 |
| R5 | Source `contract.*` changes between dry-run and apply (e.g. a new authoring event lands in `contract.panel_output_record` after dry-run but before apply) | MEDIUM | MEDIUM | Dry-run computes a row-snapshot hash; apply re-validates. If counts drift, apply aborts. Note: this is a behavioural quirk during A2 — Phase A3 cutover eliminates the drift window by stopping `contract.*` writes |
| R6 | Readers accidentally read from both `contract.*` and `bcf.*` after A2 ships (before A3 cutover) and double-count | MEDIUM | MEDIUM | A2 ships duplication intentionally. BCF reader code is NOT modified by A2 — reads continue to hit `contract.*` only until Phase A3. New code paths that touch `bcf.*` directly during A2→A3 window MUST filter to avoid double-counting; review at every PR that touches BCF read paths until A3 ships |
| R7 | PR #133 apply leaves a smoke row behind (e.g. due to operator override or partial failure) and A2 apply silently migrates it | VERY LOW | HIGH | Substrate-bound HR1 CHECKs reject synthetic rows. Smoke rows that are NOT synthetic-provider would still trip the dry-run's no-synthetic probe (informational at A1; **binding at A2**) — A2 dry-run reports any non-zero count as BLOCKING |
| R8 | The 0-row `bcf.authoring_panel_rejection_log` post-A2 state is mistakenly read as "A2 apply failed" by a future maintainer | LOW | LOW | This DBCP §3.2 documents that 0 authority rejection log rows exist; post-A2 assertion permits 0. Comment on the table updated in Phase A1 design notes this is A2-pending; we keep the same comment after A2 |
| R9 | Apply script env-gate format diverges from the established `BCCORE_BCF_PHASE_A1_APPLY_CONFIRM=I_HAVE_REVIEWED_DRY_RUN_<ts>` pattern | LOW | LOW | A2 uses the same pattern: `BCCORE_BCF_PHASE_A2_APPLY_CONFIRM=I_HAVE_REVIEWED_DRY_RUN_<ts>`. Operator decision D5 confirms |
| R10 | A2 apply runs in a session where TENANT_DATABASE_URL is set | LOW | HIGH | Substrate-enforced via env-var separation (`DATABASE_URL` vs `TENANT_DATABASE_URL`); script guards mirror Phase A1's pattern |
| R11 | `concept_registry.*` accidentally touched by the apply script | VERY LOW | HIGH | The apply script's DML list contains zero `concept_registry` references; post-apply assertion checks `concept_registry.*` unchanged (11 tables / 68 rows) |
| R12 | Rollback run after A3 cutover destroys post-A3 authority rows | LOW | CRITICAL | Pre-rollback guard #2 (Phase A3 not shipped) + guard #3 (row counts match post-A2 baseline). If A3 has shipped, counts will diverge → rollback refuses |

## 13. Operator decisions (D1..D12)

| # | Decision | Default proposal | Operator must confirm |
|---|---|---|---|
| **D1** | Accept Phase A2 migration scope: 3,568 authority-bearing rows; insert-copy from `contract.*` to `bcf.*`; no source DELETE; no writer/reader flip; no MCF FK retarget; no `concept_registry.*` touch; no tenant DB touch | ACCEPT | Y / N |
| **D2** | Authorize authoring 3 bc-core scripts in a follow-up bc-core PR: `bcf-evidence-schema-phase-a2-dry-run.mjs`, `bcf-evidence-schema-phase-a2-apply.mjs`, `bcf-evidence-schema-phase-a2-rollback.mjs` | ACCEPT | Y / N |
| **D3** | Idempotency model: Option A (strict-empty target enforcement) vs Option B (ON CONFLICT DO NOTHING) — see §7.2 | **A** (RECOMMENDED) | A / B |
| **D4** | Confirm no source `contract.*` row deletion during A2 (insert-copy only; Phase A4 owns the eventual freeze/retire) | ACCEPT | Y / N |
| **D5** | Confirm A2 apply env-gate format: `BCCORE_BCF_PHASE_A2_APPLY_CONFIRM=I_HAVE_REVIEWED_DRY_RUN_<dry-run-timestamp>` (mirroring Phase A1's pattern) | ACCEPT | Y / N |
| **D6** | Confirm PR #133 apply MUST execute BEFORE Phase A2 apply (parent D9 + parent §13 step 8 ordering) | ACCEPT | Y / N |
| **D7** | A2 dry-run probe #5 (no-synthetic source) is **BINDING at A2** (was informational at A1). Counts must equal 0 across BOTH `contract.panel_output_record` and `contract.certification_record` before A2 apply. If non-zero, dry-run BLOCKS | ACCEPT | Y / N |
| **D8** | Confirm A2 rollback validity is PRE-A3 ONLY. Post-A3 rollback requires a separate Phase A3 restore plan (NOT covered here) | ACCEPT | Y / N |
| **D9** | Confirm tenant `tbc_{slug}_dev` databases remain OUT OF SCOPE (substrate-enforced via `DATABASE_URL` vs `TENANT_DATABASE_URL`; script guards mirror Phase A1) | OUT OF SCOPE | Y / N |
| **D10** | Pre-rollback "A3 not shipped" check mechanism: (a) operator attestation in env var, OR (b) substrate marker table (e.g. `bcf.phase_marker` with `phase_code='a3-shipped'`), OR (c) row-count divergence detection only (rely on §9.2 guard #3) | RECOMMEND (c) row-count divergence only; substrate marker introduces new substrate complexity for one bit; operator attestation is unverifiable | A / B / C |
| **D11** | Confirm legacy `metric.*` (16,820 rows + 2 AR pilot KPIs) and `concept_registry.*` (BCR vocabulary; 11 tables / 68 rows) remain OUT OF SCOPE | OUT OF SCOPE | Y / N |
| **D12** | Confirm M11 / M12 / M12.5 / M13 not invoked; M14 stays CLOSED | OUT OF SCOPE | Y / N |

## 14. Test / evidence plan

### 14.1 Dry-run probes (read-only; `allow_write=false`)

A2 dry-run mirrors Phase A1 dry-run's pattern. Probe list (codes 3..N):

1. (code 3) `bcf` schema present (Phase A1 invariant; count = 1).
2. (code 4) 4 `bcf.*` tables all at **0 rows** (strict-empty target; D3=A).
3. (code 5) Source `contract.*` shape parity vs Phase A1 design §4 (column / CHECK / index count match).
4. (code 6) Source `contract.*` row counts post-PR-#133-apply baseline: panel=19, rejection_log=0, calibration=19, cert=3,530.
   - **Note:** PR #133 apply MUST have run by this point. If smoke rows still present (count != 19 / 0 / 19 / 3,530), probe FAILS with verdict "PR #133 apply not yet executed".
5. (code 7) **BINDING:** no-synthetic source probe — `COUNT(*)` for `provider IN ('synthetic','replay','mock','canned')` across `contract.panel_output_record` AND `contract.certification_record` must equal 0 / 0.
6. (code 8) `mcf.*` 17 tables at 0 rows.
7. (code 9) `concept_registry.*` 11 tables, 68 rows.
8. (code 10) `idx_mcf_mc_mc_name_active` + `idx_mcf_mper_mcv_check_eval_pkg` present.
9. (code 11) 9 inbound FKs on `contract.panel_output_record.panel_run_uid` intact.
10. (code 12) Synthesize planned INSERT statements deterministically; compute `sha256(planned_dml_text)`; pin in evidence.

### 14.2 Apply assertions (post-apply; codes 200..N)

1. (code 200) `bcf.panel_output_record` row count = 19.
2. (code 201) `bcf.authoring_panel_rejection_log` row count = 0.
3. (code 202) `bcf.calibration_event` row count = 19.
4. (code 203) `bcf.certification_record` row count = 3,530.
5. (code 204) **Total `bcf.*` row count = 3,568.**
6. (code 205) Per-row byte-equivalence (a sample check; pick 3 representative rows and assert column-by-column equality with their `contract.*` source).
7. (code 206) FK validity: every `bcf.calibration_event.panel_run_uid` and `bcf.certification_record.panel_run_uid` references an existing `bcf.panel_output_record.panel_run_uid` (FK already enforces; assertion is post-apply verification).
8. (code 207) No-synthetic substrate guard not triggered (no rejected rows; the CHECK didn't fire because PR #133 had already retired the 1 known violation).
9. (code 208) `contract.*` row counts unchanged from pre-A2 baseline (insert-copy; source preserved): panel=19, rejection_log=0, calibration=19, cert=3,530 (post-PR-#133-apply state).
10. (code 209) `mcf.*` 17 tables still 0 rows.
11. (code 210) `concept_registry.*` 11 tables, 68 rows unchanged.
12. (code 211) 9 inbound FKs on `contract.panel_output_record.panel_run_uid` intact.
13. (code 212) Standing mcf indexes (`idx_mcf_mc_mc_name_active` + `idx_mcf_mper_mcv_check_eval_pkg`) present.
14. (code 213) Cross-schema FK guard: 0 FKs from `bcf.*` to anything other than `bcf.*` (intra-bcf only).

### 14.3 Rollback assertions

Per §9.4 — 6 post-rollback assertions covering empty `bcf.*` + unchanged `contract.*` + unchanged `mcf.*`/`concept_registry.*` + FKs intact + `bcf` schema still present.

### 14.4 No mocks in production paths

Production scripts contain no mocks. Integration tests use SAVEPOINT-rolled-back per HR5.

## 15. Evidence artifact naming convention

Per Phase A1 + PR #133 pattern, evidence lands under `bc-core/scripts/audit-output/`:

```
bcf-evidence-schema-phase-a2-{dry-run|apply|rollback}-<ISO-timestamp>.{
  precondition.jsonl,
  summary.md,
  planned-dml.sha256.txt,        -- (dry-run only) sha256 of planned INSERT text
  evidence.jsonl                 -- (apply / rollback) post-stage assertions
}
```

ISO timestamp format: `YYYY-MM-DDTHH-MM-SS-mmmZ` (filesystem-safe, mirrors PR #133's pattern).

## 16. Explicit non-scope statement (repeated)

This DBCP is **NOT** the Phase A2 apply execution. It authorizes the *authoring of scripts* that will, at their own separately-authorized gate, execute the apply.

This DBCP does **NOT** authorize PR #133 apply execution. PR #133 apply is a SEPARATE operator instruction at its own gate; it is the prerequisite to A2 apply per parent §13 step 8.

This DBCP is **NOT** Phase A3 / A4 / A5.

This DBCP does **NOT** authorize any source `contract.*` row deletion. A2 is insert-copy only.

This DBCP does **NOT** authorize any bc-core source edit outside the 3 follow-up scripts.

This DBCP does **NOT** touch tenant DBs.

This DBCP does **NOT** alter `mcf.*`, `metric.*`, `concept_registry.*`, `contract.framework_policy`, or any `contract.*` chain table.

This DBCP does **NOT** open M14.

## 17. Discipline assertions (this DBCP-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — DBCP file lands only in bc-docs-v3 |
| No DDL applied | ✓ |
| No DML applied | ✓ |
| No M11 / M12 / M12.5 / M13 / M14 invocation | ✓ |
| `bc-postgres` MCP `allow_write=false` throughout (column / row-count / smoke-UID confirmation probes only) | ✓ |
| No `mcf.*` touched | ✓ |
| No `metric.*` touched | ✓ |
| No `contract.*` row mutation | ✓ |
| No `concept_registry.*` touched | ✓ |
| No tenant `tbc_{slug}_dev` DB connection opened | ✓ |
| PR #133 not modified | ✓ |
| PR #133 apply NOT run (still PAUSED per parent D9) | ✓ |
| No-synthetic hard rule respected (this DBCP designs the binding A2 enforcement; does not write to substrate) | ✓ |
| Operator stance ADR DEC-7f9597 / D423 honoured (no substrate shortcut; strict-empty discipline; PR #133 apply must precede A2; pre-A3-only rollback) | ✓ |

## 18. Sequencing

Under the merged Option A path, this DBCP slots in at step 8 of the ladder pinned in the boundary DBCP §13:

1. ~~Boundary DBCP merged~~ — bc-docs-v3 main `6f8cc15`.
2. ~~Operator authorization D1..D11~~ — recorded at bc-docs-v3 main `70beeb7`.
3. ~~Phase A1 substrate-design DBCP merged~~ — `70beeb7`.
4. ~~Phase A1 apply DBCP merged~~ — bc-docs-v3 main `cdc6efa`.
5. ~~Phase A1 scripts merged (PR #134)~~ — bc-core main `61f2e02`.
6. ~~Phase A1 dry-run executed~~ — sha256 `b31dcb26…` pinned at `2026-05-29T02-00-51-885Z`.
7. ~~Phase A1 apply executed~~ — APPLY PASS at `2026-05-29T02-11-41-745Z`; PR #135 evidence merged at bc-core main `09035b8`.
8. **This DBCP (Phase A2 migration design)** → operator reviews §13 D1..D12.
9. **Operator authorization of D1..D12** in writing.
10. **bc-core PR — Phase A2 dry-run / apply / rollback scripts** — authored separately; opens with 3 scripts + tests; merged after independent review.
11. **PR #133 apply gate executed** — retires 11 smoke rows from `contract.*` (parent §13 step 9; MUST precede step 12).
12. **PR #133 closeout doc** — `bcf-authoring-test-row-cleanup-closeout.md` on bc-docs-v3.
13. **Phase A2 dry-run execution** — operator-authorized; produces evidence artifacts; sha256 pinned.
14. **Phase A2 apply gate execution** — operator-authorized with `BCCORE_BCF_PHASE_A2_APPLY_CONFIRM=I_HAVE_REVIEWED_DRY_RUN_<ts>`; single-transaction; 14 post-apply assertions; closeout doc.
15. **Phase A3 DBCP + apply** — BCF writer/reader cutover.
16. **Phase A4 DBCP + apply** — freeze or retire `contract.*` evidence tables.
17. **Phase A5 DBCP + apply** — `mcf.metric_authoring_panel_output_record` creation; 5 mcf→contract FKs redirected to mcf→mcf; M12 writer flipped.
18. **M12 first real panel run DBCP** — separately authored.
19. **M12 first real panel run** — operator-authorized.
20. **M12.5 first materialization** — operator-authorized.
21. **M13 first evaluation** — operator-authorized.
22. **M14 opening** — after M13 first evaluation closes.

This DBCP authorizes step 10. Steps 11..14 each require their own operator instruction at their respective gates.

---

**End of DBCP. NOT EXECUTED. Operator authorization on §13 D1..D12 required before the bc-core script-authoring PR opens.**
