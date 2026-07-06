---
uid: bcf-evidence-schema-phase-a1-apply-dbcp
title: BCF Evidence Schema — Phase A1 Apply DBCP (`bcf.*` schema + 4 empty evidence tables; apply gate)
description: Operational apply DBCP for Phase A1 of the operator-authorized Option A path from `bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` (merged at bc-docs-v3 main `6f8cc15`) and the D1-D11 decision record + Phase A1 substrate-design DBCP (merged at bc-docs-v3 main `70beeb7`). Authorizes the next-step authoring of bc-core dry-run / apply / rollback scripts that will create the new `bcf` schema and 4 empty evidence tables (`bcf.panel_output_record`, `bcf.authoring_panel_rejection_log`, `bcf.calibration_event`, `bcf.certification_record`) with column/constraint/index/FK shapes byte-pinned to the Phase A1 design DBCP's §4. Target-schema review at the prior gate confirmed `bcf.*` (not `concept_registry.*`, which is BCR vocabulary, not BCF evidence). **NOT EXECUTED.** This DBCP does NOT apply DDL, does NOT migrate data, does NOT touch `mcf.*` FKs, does NOT touch `contract.*` rows, does NOT touch `concept_registry.*`, does NOT touch tenant `tbc_{slug}_dev` databases, does NOT execute PR #133 apply or restore, does NOT touch bc-core source outside the scripts that the operator authorizes next, and does NOT invoke M11/M12/M12.5/M13. M14 remains CLOSED. PR #133 apply gate remains PAUSED per parent D9 (Phase A1 + A2 designs both accepted prerequisite). The operator stance ADR DEC-7f9597 (D423, untracked locally until this PR commits it) is honoured throughout — substrate truth is inviolate; ceremony is reduced where coupled gates allow combining.
status: draft
date: 2026-05-29
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-evidence-schema-phase-a1-apply-gate
supersedes:
superseded_by:
---

# BCF Evidence Schema — Phase A1 Apply DBCP

## 1. Scope

### 1.1 Question this DBCP answers

> Under the operator-authorized Option A path with target schema confirmed as `bcf.*` (not `concept_registry.*`), what is the exact apply-gate procedure — dry-run probes, DDL synthesis, single-transaction apply wrapper, post-apply parity probes, rollback path, evidence artifacts — that the next-step bc-core scripts must implement to create the new `bcf.*` schema and its 4 empty evidence tables?

### 1.2 In scope

- The procedural gate that turns Phase A1 substrate-design (PR #12) into an executable bc-core apply.
- Authorization to author 3 bc-core scripts in a follow-up PR: dry-run, apply, rollback.
- DDL operation list pinned by reference to Phase A1 design DBCP §4 (column shapes, CHECK clauses, index definitions, FK clauses).
- 5-probe pre-apply gate (read-only, `allow_write=false`).
- Single-transaction apply wrapper with 13 post-apply assertions.
- `DROP SCHEMA bcf CASCADE` rollback path valid only before Phase A2 ships.
- Evidence artifact naming convention.
- Operator decisions D1..D11 narrower than the design DBCP's D1..D11.

### 1.3 Explicit non-scope

- ❌ **No DDL apply.** This DBCP authorizes the *authoring of scripts*; the scripts' apply gate is a separately authorized follow-up.
- ❌ **No DML.** No row migration in A1.
- ❌ **No data migration.** Phase A2 owns row migration.
- ❌ **No writer/reader flip.** Phase A3 owns the BCF authoring writer cutover.
- ❌ **No `mcf.*` FK retarget.** Phase A5 owns the 5 mcf→contract FK redirects.
- ❌ **No `contract.*` evidence table freeze / DROP.** Phase A4 owns that.
- ❌ **No `concept_registry.*` change.** BCR vocabulary stays in `concept_registry.*` per the target-schema review.
- ❌ **No tenant `tbc_{slug}_dev` DB connection.** Substrate-enforced via separate connections.
- ❌ **No PR #133 apply or restore execution.** PR #133 apply remains paused per parent D9.
- ❌ **No bc-core source edit outside the 3 follow-up scripts.** No service code, no Drizzle schema flip, no migration files in this gate.
- ❌ **No M11 / M12 / M12.5 / M13 invocation.** M14 remains CLOSED.
- ❌ **No `framework_policy` placement.** Parent D7 deferred.
- ❌ **No re-litigation of Option A target.** Target-schema review concluded KEEP `bcf.*`; the BCR/BCF category-distinction reasoning is recorded in §6 below.

## 2. Authority

| Artifact | Location | Authority for |
|---|---|---|
| Boundary DBCP (Option A chosen) | `docs/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` @ bc-docs-v3 main `6f8cc15` | Option A target architecture; 5-phase migration plan |
| D1-D11 decision record | `docs/implementation/bcf-mcf-evidence-boundary-operator-decisions-d1-d11.md` @ bc-docs-v3 main `70beeb7` | D2=A; D4=ACCEPT (Phase A1+A2 design); D6=ACCEPT (5-phase sequence); D9=PAUSE PR #133 apply |
| Phase A1 substrate-design DBCP | `docs/implementation/bcf-evidence-schema-phase-a1-dbcp.md` @ bc-docs-v3 main `70beeb7` | Column shapes, CHECK clauses, index definitions, FK clauses (byte-pinned in §4 of that doc) — referenced from this apply DBCP rather than duplicated |
| Operator stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) — untracked locally; included in this PR | Rulebook-first execution stance: no substrate shortcuts; reduce ceremony only where coupled gates allow combining |
| Target-schema review (this session, prior turn) | inline in conversation transcript | Confirms `bcf.*` is the target; `concept_registry.*` is BCR vocabulary and out of scope |
| Hard rules HR1..HR5 | parent DBCP §5 | Substrate constraints enforced by this apply gate |
| Predecessor cleanup DBCP | `docs/implementation/bcf-authoring-test-row-cleanup-dbcp.md` @ bc-docs-v3 main `0f42662` | The 11-row smoke debt that PR #133 will retire — sequenced AFTER A1 apply and BEFORE A2 migration per parent §13 step 8 |

## 3. Current state (read-only baseline)

Verified via `bc-postgres` MCP (`allow_write=false`) against `bc_platform_dev` post-PR-#11-merge, re-confirmed post-PR-#12-merge, re-confirmed post-PR-#133-merge:

| Surface | Today | Phase A1 apply changes? |
|---|---|---|
| `bcf` schema present? | **No** (information_schema.schemata count = 0) | YES — apply creates it |
| `bcf.*` tables | n/a (schema absent) | YES — apply creates 4 empty tables |
| `contract.panel_output_record` rows | 24 | NO — apply does not write |
| `contract.authoring_panel_rejection_log` rows | 1 | NO |
| `contract.calibration_event` rows | 23 | NO |
| `contract.certification_record` rows | 3,531 | NO |
| `contract.framework_policy` rows | 3 | NO (parent D7 deferred) |
| `mcf.*` 17 tables (all 0 rows) | 0 rows total | NO |
| `concept_registry.*` 11 tables, 68 rows total | 68 rows | NO (BCR vocabulary; out of scope) |
| `metric.*` legacy ~16,820 rows | preserved | NO (D11 out of scope) |
| Tenant `tbc_{slug}_dev` DBs | not connected to | NO (D10 out of scope) |
| 9 inbound FKs on `contract.panel_output_record.panel_run_uid` | intact (4 contract + 5 mcf) | NO — Phase A5 will retarget the 5 mcf ones |
| `idx_mcf_mc_mc_name_active` on `mcf.metric_contract` | present | NO |
| `idx_mcf_mper_mcv_check_eval_pkg` on `mcf.metric_publication_eligibility_result` | present | NO |
| `pgcrypto` extension | present (required for `gen_random_uuid()`) | NO — depended upon, not modified |
| 1 known synthetic-provider row on `contract.certification_record` (uid `21023aa1`) | present | NO — PR #133 apply retires it BEFORE Phase A2; this Phase A1 apply does not touch it |

## 4. Planned DDL (operation list; full text pinned by reference)

The Phase A1 design DBCP §4 already pins the byte-exact column shapes, CHECK clauses, index definitions, and FK clauses. This apply DBCP does NOT duplicate that pinned text; the dry-run script will synthesize the SQL deterministically from the design DBCP §4 and compute a sha256 fingerprint that pins the SQL byte-equivalent across dry-run, apply, and any future re-execution.

### 4.1 DDL operation list (single transaction)

The bc-core apply script will execute these operations in order, wrapped in one transaction:

| # | Operation | Source of byte-exact shape |
|---|---|---|
| 1 | `CREATE SCHEMA bcf` | §4.1 |
| 2 | `COMMENT ON SCHEMA bcf IS '...'` | §4.1 |
| 3 | `CREATE TABLE bcf.panel_output_record (...)` — 13 cols + PK | Phase A1 design §4.2 |
| 4 | `CREATE TABLE bcf.authoring_panel_rejection_log (...)` — 15 cols + PK + UNIQUE on panel_run_uid | Phase A1 design §4.3 |
| 5 | `CREATE TABLE bcf.calibration_event (...)` — 13 cols + PK + UNIQUE on panel_run_uid | Phase A1 design §4.4 |
| 6 | `CREATE TABLE bcf.certification_record (...)` — 27 cols + PK | Phase A1 design §4.5 |
| 7..32 | 26 mirrored CHECK constraints (5 on panel_output_record, 7 on authoring_panel_rejection_log, 4 on calibration_event, 10 on certification_record), constraint names `bcf_*_chk` with byte-equivalent clauses | Phase A1 design §4.2 / §4.3 / §4.4 / §4.5 CHECK tables |
| 33 | `bcf_panel_output_record_no_synthetic_provider_chk` — NEW HR1 substrate CHECK | Phase A1 design §4.2 row 6 + §7 |
| 34 | `bcf_certification_record_no_synthetic_provider_chk` — NEW HR1 substrate CHECK | Phase A1 design §4.5 row 11 + §7 |
| 35..50 | 16 non-PK indexes (PK indexes created implicitly by CREATE TABLE; total index count = 20 = 4 PKs + 16 explicit) | Phase A1 design §4.2 / §4.3 / §4.4 / §4.5 index tables |
| 51 | `ALTER TABLE bcf.authoring_panel_rejection_log ADD CONSTRAINT fk_bcf_authoring_panel_rejection_log__panel_run FOREIGN KEY (panel_run_uid) REFERENCES bcf.panel_output_record(panel_run_uid) ON DELETE RESTRICT` | Phase A1 design §6.1 |
| 52 | `ALTER TABLE bcf.calibration_event ADD CONSTRAINT fk_bcf_calibration_event__panel_run FOREIGN KEY (panel_run_uid) REFERENCES bcf.panel_output_record(panel_run_uid) ON DELETE RESTRICT` | Phase A1 design §6.1 |
| 53 | `ALTER TABLE bcf.certification_record ADD CONSTRAINT fk_bcf_certification_record__panel_run FOREIGN KEY (panel_run_uid) REFERENCES bcf.panel_output_record(panel_run_uid) ON DELETE RESTRICT` | Phase A1 design §6.1 |
| 54..57 | `COMMENT ON TABLE bcf.<each>` — 4 comments describing the A2-pending status | §4.1 |

Total: 1 schema + 1 schema-comment + 4 CREATE TABLE + 2 CONSTRAINT UNIQUE (already declared inside CREATE TABLE) + 28 CHECK constraints (26 mirrored + 2 new HR1) + 16 explicit indexes + 3 FK constraints + 4 table-comments = **58 DDL statements** in one transaction (the exact count may differ by ±2 depending on whether the script emits inline-vs-ALTER constraints; the sha256 fingerprint is the binding artifact, not the statement count).

### 4.2 No cross-schema FK introduced

The apply explicitly does NOT emit any FK from `bcf.*` to `contract.*`, `mcf.*`, `concept_registry.*`, or `metric.*`. The two clusters (BCF and the rest) operate independently from the moment `bcf.*` exists.

### 4.3 sha256 fingerprint binds design ↔ apply ↔ replay

The dry-run script synthesizes the DDL, computes `sha256(planned_ddl_text)`, and pins it. The apply script re-synthesizes the DDL, recomputes the sha256, and refuses to apply if it does not match the dry-run pin. This is the same pattern as PR #133's planned-delete.sha256.txt.

## 5. Hard rules (restated from boundary DBCP §5)

- **HR1** — No synthetic / mock / replay / canned data written to persistent substrate. Phase A1 substrate-enforces HR1 on the new `bcf.panel_output_record` and `bcf.certification_record` via the two additive `bcf_*_no_synthetic_provider_chk` CHECKs.
- **HR2** — MCF evidence belongs in `mcf.*`. Phase A1 does not change MCF substrate.
- **HR3** — Future MCF metric authority events must NOT write to generic `contract.*` authoring tables. Phase A1 does not change MCF behaviour; Phase A5 will retarget the M12 writer.
- **HR4** — Tenant result DBs are separate and out of scope. Phase A1 only touches platform DB `bc_platform_dev`.
- **HR5** — Mocks only inside unit tests or SAVEPOINT-rolled-back integration tests. Phase A1 apply integration tests must SAVEPOINT-rollback or run against a disposable test DB.

## 6. BCR vs BCF (preventing re-litigation of the target)

The prior target-schema review confirmed:

- **`concept_registry.*`** = **BCR** (Business Concept Registry) — vocabulary primitives (entity / business_concept / characteristic / representation_term + supersession graphs). 68 rows; ISO-11179-shaped. All 19 FKs intra-schema. **Out of scope** for Phase A1.
- **`bcf.*`** (this gate creates) = **BCF authoring evidence** — events that decide about BCR rows. Empty in A1; gets 3,568 authority-bearing rows in Phase A2.

The two are categorically distinct: BCR is the *subject* (vocabulary); BCF authoring evidence is the *predicate* (events that act on BCR rows). The 3,531 `contract.certification_record` rows are certifications **of** BCR primitives — they are not BCR primitives themselves.

This distinction is locked. Future gates should not re-litigate "should we fold evidence into `concept_registry.*`?" — the answer is documented as a category error.

## 7. Dry-run procedure

Authored as `bc-core/scripts/bcf-evidence-schema-phase-a1-dry-run.mjs` (follow-up PR per D2 below). Read-only, no DB writes.

### 7.1 Pre-apply probes (all must PASS before SQL is synthesized)

1. **Schema availability**: `SELECT count(*) FROM information_schema.schemata WHERE schema_name = 'bcf'` → expect **0**.
2. **Extension availability**: `SELECT count(*) FROM pg_extension WHERE extname = 'pgcrypto'` → expect **1**.
3. **Source `contract.*` shape parity vs Phase A1 design §4**: for each of the 4 source tables (`contract.panel_output_record`, `contract.authoring_panel_rejection_log`, `contract.calibration_event`, `contract.certification_record`), enumerate `information_schema.columns` and diff against the pinned shape in Phase A1 design §4.{2,3,4,5}. Any drift halts the gate (R10 mitigation).
4. **Source `contract.*` CHECK parity**: for each source table, enumerate `pg_get_constraintdef()` for all `contype='c'` constraints and diff against the pinned CHECK clauses in Phase A1 design §4. Any drift halts the gate.
5. **No-synthetic source probe** (per Phase A1 design §12.1 probe #3, post-NIT-patch):
   ```sql
   SELECT 'contract.panel_output_record' AS table_name, count(*) AS n
     FROM contract.panel_output_record
     WHERE (model_identity_json->'maker'->>'provider')
           IN ('synthetic','replay','mock','canned')
   UNION ALL
   SELECT 'contract.certification_record', count(*)
     FROM contract.certification_record
     WHERE (model_identity_json->'maker'->>'provider')
           IN ('synthetic','replay','mock','canned')
   ```
   This probe MAY return non-zero today (1 known smoke row in `contract.certification_record`). Phase A1 apply does NOT require this to be zero — Phase A2 does. The probe is informational here and pinned for Phase A2's pre-migration gate.

### 7.2 DDL synthesis + sha256

After all 5 probes PASS:

6. Synthesize the full DDL text (~58 statements) from Phase A1 design §4 + §6.1 + §4.1 (schema comment) + §4.{2,3,4,5} (table comments).
7. Compute `sha256(planned_ddl_text)`.
8. Emit dry-run evidence artifacts per §13 naming convention.

### 7.3 Tenant-DB connection guard

The dry-run script MUST NOT open a connection using `TENANT_DATABASE_URL`. Only `DATABASE_URL` (platform DB `bc_platform_dev`) is permissible. Substrate-enforced via env-var separation (HR4).

## 8. Apply procedure

Authored as `bc-core/scripts/bcf-evidence-schema-phase-a1-apply.mjs` (follow-up PR per D2). Env-gated. Single-transaction wrapper.

### 8.1 Apply gate guard

Env var required: `BCCORE_BCF_PHASE_A1_APPLY_CONFIRM=I_HAVE_REVIEWED_DRY_RUN_<dry-run-timestamp>` (operator copies the timestamp from the dry-run evidence file). Mismatch or absence → exit with no DB connection.

### 8.2 Re-synthesize + sha256 match

The apply script re-synthesizes the DDL (same algorithm as dry-run), recomputes sha256, and compares against the dry-run-pinned fingerprint. Mismatch → exit before any DB write. This is the binding link between dry-run and apply.

### 8.3 Single-transaction wrapper

```
BEGIN;
  -- 58 DDL statements per §4.1
COMMIT;
```

Any error inside the transaction triggers automatic ROLLBACK. No partial state persists.

### 8.4 Post-apply assertions (read-only, all must PASS for COMMIT to be reported as successful; failure triggers no-op)

The apply script executes the assertion suite AFTER COMMIT but BEFORE writing the success evidence artifact. If any assertion fails, the script emits a `failed.summary.md` with the failing assertion and the operator's next action is to consider rollback (§9):

1. `bcf` schema present: `SELECT count(*) FROM information_schema.schemata WHERE schema_name = 'bcf'` = **1**.
2. 4 `bcf.*` tables present and empty: `SELECT table_name, (xpath…)` count = **0** for all 4.
3. Column-shape parity diff between `bcf.*` and `contract.*` counterparts via `information_schema.columns`: column_name + data_type + is_nullable + column_default + ordinal_position match exactly (modulo schema prefix); for `contract.certification_record` ↔ `bcf.certification_record` the diff allows the missing `bcf_certification_record_no_synthetic_provider_chk` CHECK to be present on `bcf.*` only (additive HR1 enforcement).
4. CHECK parity diff via `pg_get_constraintdef()`: 26 mirrored CHECKs present on `bcf.*` with byte-equivalent clauses (modulo `bcf_` prefix); plus 2 additive HR1 CHECKs present.
5. Index parity diff via `pg_indexes`: 20 `bcf.*` indexes correspond 1:1 to 20 `contract.*` indexes by definition; partial-UNIQUE `uq_bcf_certification_record__registry_dedup` present with `governance_scope = 'registry'` predicate.
6. FK parity: 3 intra-`bcf.*` FKs present, each `ON DELETE RESTRICT`, each targeting `bcf.panel_output_record(panel_run_uid)`. **0** `bcf.* → contract.*` FKs. **0** `bcf.* → concept_registry.*` FKs. **0** `bcf.* → mcf.*` FKs.
7. `COMMENT ON SCHEMA bcf` present and non-empty.
8. `COMMENT ON TABLE bcf.<each>` present and non-empty for all 4 tables.
9. **No cross-schema FK drift**: 9 inbound FKs on `contract.panel_output_record.panel_run_uid` unchanged (4 from `contract.*` + 5 from `mcf.*`); no FK in `bcf.*`, `mcf.*`, `concept_registry.*`, or `contract.*` chain tables redirected.
10. **`contract.*` row counts unchanged**: panel_output_record = 24, authoring_panel_rejection_log = 1, calibration_event = 23, certification_record = 3531.
11. **`mcf.*` remains 0**: all 17 tables at 0 rows.
12. **`concept_registry.*` unchanged**: 11 tables, 68 rows total (no row change; no schema change).
13. **`pg_indexes` for `idx_mcf_mc_mc_name_active` and `idx_mcf_mper_mcv_check_eval_pkg`** present (standing post-PR-#11/#12/#133 invariants).

### 8.5 Tenant-DB connection guard

The apply script MUST NOT open a connection using `TENANT_DATABASE_URL`. Same enforcement as dry-run.

## 9. Rollback procedure

Authored as `bc-core/scripts/bcf-evidence-schema-phase-a1-rollback.mjs` (follow-up PR per D2). Env-gated.

### 9.1 Validity window — PRE-A2 ONLY

`DROP SCHEMA bcf CASCADE` is a safe rollback **iff** Phase A2 has not yet shipped (i.e. `bcf.*` tables are still empty). Once Phase A2 begins inserting authority-bearing rows, rollback requires a different procedure (a Phase A2 restore plan, authored as part of the Phase A2 design DBCP).

### 9.2 Pre-rollback guards

The rollback script asserts BEFORE issuing DROP:

1. Env var `BCCORE_BCF_PHASE_A1_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_<apply-timestamp>` present.
2. All 4 `bcf.*` tables exist and are at **0 rows**. Non-zero row count in any → exit without DROP and emit error.
3. No cross-schema FK targets `bcf.*` (parent DBCP and Phase A1 design forbid this; assert it).

### 9.3 Rollback DDL

```
BEGIN;
  DROP SCHEMA bcf CASCADE;
COMMIT;
```

Wrapped in a transaction so any error aborts cleanly.

### 9.4 Post-rollback assertions

1. `bcf` schema absent (information_schema.schemata count = 0).
2. `contract.*` row counts unchanged (24 / 1 / 23 / 3531).
3. `mcf.*` row counts unchanged (0 across all 17).
4. `concept_registry.*` row counts unchanged (68 across 11).
5. 9 inbound FKs on `contract.panel_output_record.panel_run_uid` intact.

### 9.5 Post-A2 rollback (explicit non-scope)

Once Phase A2 ships, `DROP SCHEMA bcf CASCADE` would destroy migrated authority-bearing BCF rows. Post-A2 rollback is therefore explicitly NOT covered by this Phase A1 rollback script. Phase A2 DBCP must include its own restore plan (the symmetric pattern of PR #133's restore script: pre-A2 snapshot + post-rollback restore).

## 10. Risk register (Phase A1 apply specific)

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Apply runs without dry-run (no sha256 pin) | LOW | MEDIUM | Apply script requires the env var to include the dry-run timestamp; sha256 re-computed and matched against the dry-run-pinned value before any DB write |
| R2 | Source `contract.*` shape drifted since Phase A1 design was authored | LOW | HIGH | Pre-apply probe §7.1 #3 + #4 re-validates; halts gate on any drift |
| R3 | `pgcrypto` extension removed | VERY LOW | HIGH | Pre-apply probe §7.1 #2 verifies; halts gate if absent |
| R4 | Mid-apply transaction fails | LOW | LOW | Single-transaction wrapper auto-rollbacks; no partial state |
| R5 | Post-apply assertion suite incomplete (operator declared success without all 13 assertions passing) | LOW | HIGH | Script enforces; failed.summary.md emitted; operator decision is to run rollback or fix forward |
| R6 | Operator runs rollback after Phase A2 ships and destroys migrated rows | LOW | CRITICAL | Pre-rollback assertion §9.2 #2 requires all 4 `bcf.*` tables at 0 rows; non-zero → exit. Phase A2 DBCP also documents this risk |
| R7 | Tenant DB connection opened accidentally | LOW | HIGH | Substrate-enforced via env-var separation (`DATABASE_URL` vs `TENANT_DATABASE_URL`); script guards in §7.3 + §8.5 |
| R8 | DDL byte-drift between design DBCP §4 and apply synthesis | LOW | HIGH | sha256 fingerprint binds; dry-run + apply must produce identical text |
| R9 | Future maintainer mistakes empty `bcf.*` for legacy dead schema and DROPs it before Phase A2 ships | LOW | MEDIUM | `COMMENT ON SCHEMA bcf` and `COMMENT ON TABLE bcf.<each>` document A2-pending status; cross-reference the parent DBCP path |
| R10 | New HR1 CHECK rejects legitimate post-PR-#133-apply rows when Phase A2 begins | LOW | HIGH | Pre-Phase-A2 probe (§7.1 #5; informational here, binding at A2) must return 0 across both source tables before A2 migration runs; PR #133 apply retires the 1 known violation |
| R11 | Cross-schema FK accidentally introduced (e.g. `bcf.certification_record.panel_run_uid → contract.panel_output_record`) by a copy-paste error in the apply script | LOW | HIGH | Post-apply assertion §8.4 #6 explicitly checks 0 cross-schema FKs from `bcf.*` |
| R12 | `concept_registry.*` accidentally touched during apply | VERY LOW | HIGH | Post-apply assertion §8.4 #12 checks `concept_registry.*` unchanged (11 tables, 68 rows). The apply script's DDL list contains no `concept_registry` references |
| R13 | Apply runs in a session where PR #133 apply has already run and the smoke debt has been retired but the migration boundary has been forgotten | LOW | LOW | Phase A1 apply is independent of PR #133 apply — A1 only creates the empty schema. Either PR #133 order is acceptable for A1 |

## 11. Operator decisions (D1..D11)

| # | Decision | Default proposal | Operator must confirm |
|---|---|---|---|
| **D1** | Accept Phase A1 apply-gate scope: dry-run + apply + rollback scripts only; no data migration; no cross-schema FK changes; no writer/reader flip; no `concept_registry.*` touch; no tenant DB touch; no PR #133 apply execution | ACCEPT | Y / N |
| **D2** | Authorize authoring 3 bc-core scripts in a follow-up bc-core PR: `bcf-evidence-schema-phase-a1-dry-run.mjs`, `bcf-evidence-schema-phase-a1-apply.mjs`, `bcf-evidence-schema-phase-a1-rollback.mjs` | ACCEPT | Y / N |
| **D3** | Confirm `bcf.*` remains the Phase A1 target; `concept_registry.*` is BCR vocabulary and explicitly out of scope (target-schema review concluded KEEP `bcf.*`) | ACCEPT | Y / N |
| **D4** | Confirm no DDL apply is authorized by this DBCP; apply happens only when the bc-core apply script is operator-authorized at its own gate (separate explicit instruction after the bc-core PR ships and dry-run passes) | ACCEPT | Y / N |
| **D5** | Confirm PR #133 apply gate remains PAUSED. PR #133 apply ordering vs Phase A1 apply: Phase A1 apply is **independent** of PR #133 (A1 creates empty `bcf.*`; doesn't touch the contract.* smoke rows). PR #133 apply still must precede Phase A2 migration per parent §13 step 8 | ACCEPT | Y / N |
| **D6** | Confirm tenant `tbc_{slug}_dev` databases are OUT OF SCOPE for this apply (substrate-enforced via `DATABASE_URL` vs `TENANT_DATABASE_URL`; script guards in §7.3 + §8.5) | ACCEPT | Y / N |
| **D7** | Confirm legacy `metric.*` (16,820 rows + 2 AR pilot KPIs) remains OUT OF SCOPE | ACCEPT | Y / N |
| **D8** | Confirm no-synthetic substrate enforcement in `bcf.*` via the 2 new HR1 CHECKs (Phase A1 design D5 = ACCEPT; this DBCP carries that forward as a substrate-bound assertion in §8.4 #4) | ACCEPT | Y / N |
| **D9** | Confirm rollback (`DROP SCHEMA bcf CASCADE`) is valid ONLY pre-A2 (assertion §9.2 #2). Post-A2 rollback requires a separate Phase A2 restore plan, not covered here | ACCEPT | Y / N |
| **D10** | Accept evidence artifact naming convention per §13: `bcf-evidence-schema-phase-a1-{dry-run\|apply\|rollback}-<ISO-timestamp>.{precondition.jsonl, summary.md, planned-ddl.sha256.txt, evidence.jsonl}` and per-script `audit-output/` subfolder | ACCEPT | Y / N |
| **D11** | Confirm the operator stance ADR DEC-7f9597 / D423 governs this gate (no substrate shortcuts; reduce ceremony only where coupled gates allow combining) and that this apply DBCP includes the uncommitted ADR file in the same PR as a clerical-batch commit | ACCEPT | Y / N |

## 12. Test / evidence plan

### 12.1 Dry-run script tests

- Unit test: shape parity probe correctly identifies a synthetic drifted column in a SAVEPOINT-rolled-back test fixture.
- Unit test: sha256 fingerprint is deterministic across runs given identical input.
- Integration test (SAVEPOINT-rolled-back per HR5): full dry-run against a disposable DB; assert all 5 §7.1 probes PASS and evidence artifacts emitted.

### 12.2 Apply script tests

- Unit test: env var validator rejects malformed `BCCORE_BCF_PHASE_A1_APPLY_CONFIRM` values.
- Unit test: sha256 mismatch with dry-run pin halts before DB connection.
- Integration test (SAVEPOINT-rolled-back per HR5): apply against disposable DB; assert all 13 §8.4 post-apply assertions PASS.

### 12.3 Rollback script tests

- Unit test: rollback aborts if `bcf.*` tables non-empty.
- Integration test (SAVEPOINT-rolled-back per HR5): apply then rollback against disposable DB; assert all 5 §9.4 post-rollback assertions PASS.

### 12.4 No mocks in production paths

All test mocks confined to unit tests or SAVEPOINT-rolled-back integration tests (HR5). Production scripts contain no mocks.

## 13. Evidence artifact naming convention

Per the M-series + PR #133 pattern, evidence lands under `bc-core/scripts/audit-output/` with this scheme:

```
bcf-evidence-schema-phase-a1-{dry-run|apply|rollback}-<ISO-timestamp>.{
  precondition.jsonl,   -- pre-stage probe results (one JSON per line)
  summary.md,           -- human-readable summary + verdict
  planned-ddl.sha256.txt, -- (dry-run only) sha256 fingerprint of synthesized DDL
  evidence.jsonl        -- post-stage probe results (one JSON per line)
}
```

ISO timestamp format: `YYYY-MM-DDTHH-MM-SS-mmmZ` (filesystem-safe, mirrors PR #133's `bcf-authoring-test-row-cleanup-dry-run-2026-05-28T15-10-48-199Z.*` naming).

Operator-readable verdict format in `summary.md`: matches the PR #133 dry-run summary structure for consistency (check-by-check PASS/FAIL/SKIP with row counts and rationale).

## 14. Explicit non-scope statement (repeated)

This DBCP is **NOT** the Phase A1 apply execution. It authorizes the *authoring of scripts* that will, at their own separately-authorized gate, execute the apply.

This DBCP is **NOT** Phase A2 / A3 / A4 / A5.

This DBCP is **NOT** the `concept_registry.*` consolidation gate. Target-schema review concluded that consolidation belongs to a future Phase A6+ gate.

This DBCP is **NOT** the policy/governance placement gate for `contract.framework_policy` (parent D7 deferred).

This DBCP does **NOT** authorize PR #133 apply or restore execution. Parent D9 keeps them paused.

This DBCP does **NOT** authorize any bc-core source edit outside the 3 follow-up scripts.

This DBCP does **NOT** touch tenant DBs.

This DBCP does **NOT** alter `mcf.*`, `metric.*`, `concept_registry.*`, `contract.framework_policy`, or any `contract.*` chain table.

This DBCP does **NOT** open M14.

## 15. Discipline assertions (this DBCP-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — DBCP file lands only in bc-docs-v3 (plus the previously-authored ADR-7f9597.md riding along) |
| No DDL applied | ✓ |
| No DML applied | ✓ |
| No M11 / M12 / M12.5 / M13 / M14 invocation | ✓ |
| `bc-postgres` MCP `allow_write=false` throughout (read-only baseline confirmation only) | ✓ |
| No `mcf.*` touched | ✓ |
| No `metric.*` touched | ✓ |
| No `contract.*` row mutation | ✓ |
| No `concept_registry.*` touched | ✓ |
| No tenant `tbc_{slug}_dev` DB connection opened | ✓ |
| PR #133 not modified | ✓ |
| No-synthetic hard rule respected | ✓ |
| Operator stance ADR DEC-7f9597 / D423 honoured (no substrate shortcut; ADR included in this PR as a clerical batch — no separate PR opened just for it) | ✓ |

## 16. Sequencing

Under the merged Option A path, this DBCP slots in at step 3 of the ladder pinned in Phase A1 design §16:

1. ~~Phase A1 design DBCP~~ — merged at `70beeb7`.
2. ~~Operator authorization of Phase A1 design D1..D11~~ — implicitly accepted by authorizing this apply DBCP.
3. **This DBCP (Phase A1 apply gate authorization)** → operator reviews §11 D1..D11.
4. Operator authorizes D1..D11.
5. **bc-core PR — Phase A1 dry-run / apply / rollback scripts** — authored separately; opens with the 3 scripts + tests; merged after independent review.
6. **Phase A1 dry-run execution** — operator-authorized; produces evidence artifacts; sha256 pinned.
7. **Phase A1 apply gate execution** — operator-authorized with `BCCORE_BCF_PHASE_A1_APPLY_CONFIRM=I_HAVE_REVIEWED_DRY_RUN_<ts>`; single-transaction; post-apply assertions; closeout doc.
8. **Phase A2 DBCP authored** — design for 3,568-row migration; explicitly excludes synthetic-smoke debt.
9. **PR #133 apply gate execution** — retires 11 smoke rows from `contract.*` before Phase A2 row migration (parent D9 sequencing).
10. **Phase A2 apply gate execution** — INSERT…SELECT into `bcf.*`; parity probes; closeout.
11. **Phase A3 DBCP + apply** — BCF writer/reader cutover.
12. **Phase A4 DBCP + apply** — freeze or retire `contract.*` evidence tables.
13. **Phase A5 DBCP + apply** — `mcf.metric_authoring_panel_output_record` creation; 5 mcf→contract FKs redirected to mcf→mcf; M12 writer flipped.
14. **M12 first real panel run DBCP** — separately authored.
15. **M12 first real panel run** — operator-authorized.
16. **M12.5 first materialization** — operator-authorized.
17. **M13 first evaluation** — operator-authorized.
18. **M14 opening** — after M13 first evaluation closes.

This DBCP authorizes step 5. Step 6 (dry-run execution) and step 7 (apply execution) each require their own operator instruction at their respective gates.

---

**End of DBCP. NOT EXECUTED. Operator authorization on §11 D1..D11 required before the bc-core script-authoring PR opens.**
