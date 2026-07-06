---
uid: bcf-authoring-test-row-cleanup-dbcp
title: BCF Authoring Test-Row Cleanup DBCP
description: Design-blueprint for the planning + execution gate that removes the BCF authoring smoke-test artifacts from `contract.panel_output_record` and the immediately downstream chain (1 `contract.authoring_panel_rejection_log` + 4 `contract.calibration_event` + 1 `contract.certification_record` rows) so the first real BCF→MCF evidence chain does not land beside ambiguous test data. **This DBCP is NOT MCF cleanup and NOT legacy `metric.*` retirement.** The `mcf.*` substrate stays untouched (already 0 rows; nothing to clean). The legacy `metric.*` schema (16,820 rows including 2 active AR pilot KPIs) is explicitly preserved. The active `contract.*` chain tables (~127,000 rows of source/admission/canonical/observation/chain_status/integrity/L-node-semantic-trace) are explicitly preserved. The only chain-table touch is the 1 BCF cert row + 4 calibration events that are 1:1 with the 5 smoke panel runs and would otherwise leave dangling RESTRICT FK references. The 19 `registry-authoring/v1.0` panel rows from real BCF `RegistryAuthoringOrchestrator` work (2026-05-22 → 2026-05-26) are explicitly preserved. **NOT YET EXECUTED.** This DBCP only specifies the predicates, dry-run SQL design, planned DELETE SQL design, snapshot/rollback plan, evidence artifact names, and the operator decision matrix. The execution gate ships separately after operator authorization of the decisions in §10.
status: draft
date: 2026-05-28
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-authoring-test-row-cleanup-dbcp
---

# BCF Authoring Test-Row Cleanup DBCP

## 1. Scope

### 1.1 What this DBCP cleans up

| Object | Predicate | Row count | Justification |
|---|---|---|---|
| `contract.panel_output_record` (smoke cohort A) | `policy_version = 'smoke-test/pr10'` | 1 | PR-10 smoke marker — not authority-bearing |
| `contract.panel_output_record` (smoke cohort B) | `policy_version = 'context-smoke/2026-05-20'` | 1 | Context smoke marker — not authority-bearing |
| `contract.panel_output_record` (smoke cohort C) | `prompt_version = 'bcf-live-smoke/2026-05-20'` | 2 | BCF live-smoke session of 2026-05-20 — 1 APPROVE_FOR_DRAFT + 1 REJECT (paired test) |
| `contract.panel_output_record` (smoke cohort D) | `policy_version = 'bcf-roster-smoke/2026-05-20'` | 1 | Roster smoke marker — not authority-bearing |
| `contract.authoring_panel_rejection_log` | `panel_run_uid = 'c20f4d65-2021-451f-aebb-10cc8ca1249c'` (cohort C REJECT) | 1 | Rejection log for smoke cohort C; references smoke panel via RESTRICT FK |
| `contract.calibration_event` | `panel_run_uid IN <5 smoke uids>` | 4 | Calibration event 1:1 with each smoke panel run (4 of 5 smoke runs produced one) |
| `contract.certification_record` | `panel_run_uid = 'c6d85db6-c466-4993-8fdf-959ae33ffbe2'` (cohort C APPROVE) | 1 | BCF business_field submit_for_review cert from smoke cohort C; `model_identity_json` self-identifies as `"provider":"synthetic"` |
| **TOTAL** | | **11 rows** | |

**Operator-stated scope was "5 rows" (4 panel + 1 rejection log).** The 4 calibration_event + 1 certification_record rows MUST also be addressed because all 9 inbound FK constraints on `contract.panel_output_record.panel_run_uid` are `delete_rule = RESTRICT` — deleting the panel rows without first deleting these chain dependencies will fail with FK violations. The 4 calibration + 1 cert rows are themselves smoke artifacts (verified via timestamps and `model_identity_json.provider = 'synthetic'`); they were not previously surfaced because the read-only inventory in the prior planning gate stopped at the panel and rejection-log layer.

### 1.2 What this DBCP explicitly does NOT touch

| Surface | Rows | Reason |
|---|---|---|
| All 17 `mcf.*` tables | 0 | Already empty; nothing to clean |
| `metric.metric_definition` (2 active AR pilot KPIs + 1239 inactive seed rows) | 1241 | Authority-bearing pilot KPIs (`ar_growth_rate`, `revenue_collection_rate`) feed chain_status / readiness_ledger / L-node traces |
| All other `metric.*` tables | 15,579 | Pilot infrastructure: MLS state/event, lifecycle event log, formula, formula variable, formula verification, binding, mc_dependency, enrichment job, readiness ledger, mls_trigger_binding, intentional_reuse_pattern, discipline |
| `contract.metric_contract` / `_version` / `_approval` | 1,802 | Legacy pre-MCF metric chain; separate schema from `mcf.metric_contract`; no shadow risk |
| `contract.panel_output_record` `registry-authoring/v1.0` cohort | **19** | Real BCF authoring outcomes from `RegistryAuthoringOrchestrator` (2026-05-22 → 2026-05-26); authority-bearing |
| `contract.certification_record` (real cert ledger) | 3,530 | Real BCF cert ledger (only 1 of 3,531 is the smoke cert in §1.1) |
| `contract.calibration_event` (real calibration ledger) | 19 | Real calibration events (only 4 of 23 are smoke-derived) |
| `contract.source_contract` / `_version` | 60,735 | SAP table catalog + admission contracts (active dev work, D408/D409) |
| `contract.admission_contract` / `_version` | 60,734 | BF admission audit (active dev work) |
| `contract.canonical_contract` / `_version` / `mapping` / `_version` | 257 | Canonical contract chain |
| `contract.observation_contract` / `_version` / `field_map` | 672 | Observation contracts + field maps |
| `contract.l_node_semantic_trace` / `_verdict` | 25,439 | D366 / DEC-804874 semantic ledger |
| `contract.chain_status` / `_trace` / `mc_integrity_state` | 1,608 | D305 SSOT + chain trace + integrity ledger |
| `contract.contract_release_note` | 733 | Release notes |
| `contract.framework_policy` | 3 | All authority-bearing (`bcf-bf-bo-scope1`, `mcf_v1`, `bcf-registry-scope1`) |
| BCF concept_registry (`entity`, `business_concept`, `characteristic`, `representation_term`, etc.) | All | NOT touched — the smoke `business_field` primitive_id `019e45f2-c97c-7274-a6e4-95b2e45f451c` (referenced by the cert) MAY live in `concept_registry.business_concept`; even so, the BF row is not in this cleanup scope (only the cert+panel chain) |
| Tenant result databases `tbc_{slug}_dev` (all tenants) | n/a | **Out of scope — separate DB cluster from `bc_platform_dev`. This cleanup operates exclusively against the platform DB. Per D162-D167, all tenant analytical substrate (snapshots, fact tables, evaluation results, MLS-15..MLS-25 tenant-side state) lives in `tbc_{slug}_dev` and is never touched by this DBCP.** |

**This is NOT MCF cleanup** (M13 closeout-readiness gate already locked `mcf.*` at 0 rows; M12.5 closeout-readiness gate already locked the BCF preserved counts at 24+1). **This is NOT legacy `metric.*` retirement** (deferred per M12 closeout §9 to M17 tenant-runtime migration alongside `POST /api/metric-catalog/definitions` deprecation handling).

## 2. Authority

- Predecessor: M13 closeout-readiness gate (`mcf-m13-implementation-closeout.md` + `mcf-m13-closeout-readiness-2026-05-28T14-01-39-509Z.summary.md`)
- Companion: M12.5 closeout-readiness gate (`mcf-m12-5-implementation-closeout.md`)
- Upstream operational gate: M12 first-real-panel-run DBCP (TO BE WRITTEN — blocker for first real BCF→MCF metric)
- Substrate FK chain: live verified via `bc-postgres` MCP at DBCP-write time (see §3)

## 3. Read-only inventory (live verified 2026-05-28T14:xxZ via `bc-postgres` MCP, `allow_write=false`)

### 3.1 Cleanup candidate identification

#### 3.1.1 `contract.panel_output_record` (5 rows)

| # | `panel_run_uid` | `prompt_version` | `policy_version` | `verdict_code` | `created_at` |
|---|---|---|---|---|---|
| 1 | `c05258de-8a62-456e-89fd-220a16684268` | `smoke-test-v0` | `smoke-test/pr10` | APPROVE_FOR_DRAFT | 2026-05-20T12:03:25Z |
| 2 | `54890bec-28cb-4d55-8aeb-fb3f81e0b359` | `v1.0` | `context-smoke/2026-05-20` | FAIL_QA_GATE | 2026-05-20T13:15:17Z |
| 3 | `c6d85db6-c466-4993-8fdf-959ae33ffbe2` | `bcf-live-smoke/2026-05-20` | `v1` | APPROVE_FOR_DRAFT | 2026-05-20T15:13:33Z |
| 4 | `c20f4d65-2021-451f-aebb-10cc8ca1249c` | `bcf-live-smoke/2026-05-20` | `v1` | REJECT | 2026-05-20T15:13:33Z |
| 5 | `6aaad537-eab9-4bca-a6cc-4acff74211ff` | `v1.0` | `bcf-roster-smoke/2026-05-20` | FAIL_QA_GATE | 2026-05-20T15:54:33Z |

#### 3.1.2 `contract.authoring_panel_rejection_log` (1 row)

| `rejection_log_id` | `scope_code` | `primitive_type` | `defect_code` | `panel_run_uid` (→ panel #4) | `decided_at` |
|---|---|---|---|---|---|
| `0cc5ad4b-a727-4238-b07c-3b33e3e513e6` | `bf_bo` | `business_field` | `DEF_PLACEHOLDER` | `c20f4d65-…` | 2026-05-20T15:14:32Z |

#### 3.1.3 `contract.calibration_event` (4 rows — downstream)

| `calibration_event_uid` | `panel_run_uid` | `ai_verdict_code` | `policy_version` | `created_at` |
|---|---|---|---|---|
| `4db0d205-…` | `6aaad537-…` (panel #5) | FAIL_QA_GATE | `bcf-roster-smoke/2026-05-20` | 2026-05-20T15:54:33Z |
| `7d1a2c25-…` | `c6d85db6-…` (panel #3) | APPROVE_FOR_DRAFT | `v1` | 2026-05-20T15:13:33Z |
| `8a51c710-…` | `54890bec-…` (panel #2) | FAIL_QA_GATE | `context-smoke/2026-05-20` | 2026-05-20T13:15:17Z |
| `9d20f4ce-…` | `c20f4d65-…` (panel #4) | REJECT | `v1` | 2026-05-20T15:13:33Z |

Note: panel #1 (`c05258de-…`) has NO calibration_event row — the PR-10 smoke harness did not write one. So only 4 of 5 smoke panels produced calibration rows.

#### 3.1.4 `contract.certification_record` (1 row — downstream)

| `certification_record_id` | `primitive_type` | `primitive_id` | `action_code` | `from→to` | `panel_run_uid` (→ panel #3) | `model_identity_json` marker |
|---|---|---|---|---|---|---|
| `21023aa1-ddf0-4f42-9100-7242bcf5bf6f` | `business_field` | `019e45f2-c97c-7274-a6e4-95b2e45f451c` | `submit_for_review` | `draft → review` | `c6d85db6-…` | `{"maker":{"provider":"synthetic","model_version":"smoke-v1"}, "checker":{"provider":"synthetic",…}, "moderator":{"provider":"synthetic",…}}` |

Confidence this row is a test artifact: **HIGH** — explicit `"provider":"synthetic"` markers on all three roles + paired with smoke panel cohort C + `sampling_status='sampled_for_calibration'`.

### 3.2 Preserved-scope verification

- `contract.panel_output_record` with `prompt_version = 'registry-authoring/v1.0' AND policy_version = 'v1'`: **19 rows preserved** ✓
- `mcf.*` row sum: **0** ✓
- `metric.*` row sum: **>16,000** ✓ (untouched)
- `contract.metric_contract`: **780** ✓ (untouched)
- `contract.metric_contract_version`: **1,022** ✓ (untouched)
- `contract.framework_policy` (`bcf-bf-bo-scope1`, `mcf_v1`, `bcf-registry-scope1`): all 3 preserved ✓

### 3.3 FK chain map

`contract.panel_output_record.panel_run_uid` is referenced by **9 RESTRICT FK constraints**:

| Constraint | Source table | `delete_rule` | Rows referencing the 5 smoke uids |
|---|---|---|---|
| `fk_authoring_panel_rejection_log__panel_run` | `contract.authoring_panel_rejection_log` | RESTRICT | **1** |
| `fk_calibration_event__panel_run` | `contract.calibration_event` | RESTRICT | **4** |
| `fk_certification_record__panel_run` | `contract.certification_record` | RESTRICT | **1** |
| `fk_intake_queue__panel_run` | `contract.intake_queue` | RESTRICT | 0 |
| `fk_mcf_cert_panel_run` | `mcf.certification_record` | RESTRICT | 0 (table = 0 rows) |
| `fk_mapr_panel_run` | `mcf.metric_authoring_panel_run` | RESTRICT | 0 (table = 0 rows) |
| `fk_mcr_panel_run` | `mcf.metric_contract_revision` | RESTRICT | 0 (table = 0 rows) |
| `fk_mper_panel_run` | `mcf.metric_publication_eligibility_result` | RESTRICT | 0 (table = 0 rows) |
| `fk_mcs_panel_run` | `mcf.metric_supersession` | RESTRICT | 0 (table = 0 rows) |

`contract.certification_record.certification_record_id` is referenced by **0 FK constraints** (verified via `information_schema` probe — no `*_cert_id` references found in any table for the smoke cert). No further cascade depth.

`contract.authoring_panel_rejection_log.rejection_log_id` is a leaf — never referenced.
`contract.calibration_event.calibration_event_uid` is a leaf — never referenced.

### 3.4 Hard-delete vs archive availability

| Table | `archived_at` | `deleted_at` | `tombstone_at` | `status_code` | Other lifecycle column |
|---|---|---|---|---|---|
| `contract.panel_output_record` | ❌ | ❌ | ❌ | ❌ | none — append-only |
| `contract.authoring_panel_rejection_log` | ❌ | ❌ | ❌ | ❌ | `override_state` (NOT NULL; used for override flow, not archive) |
| `contract.calibration_event` | ❌ | ❌ | ❌ | ❌ | none |
| `contract.certification_record` | `is_archived_after` (timestamp) | ❌ | ❌ | ❌ | append-only cert ledger; `is_archived_after` is the only lifecycle column |

**Hard DELETE is the only available cleanup mechanism for 3 of the 4 tables.** Soft-archive via `is_archived_after` is technically available for `contract.certification_record` but does not solve the FK problem (a non-null `is_archived_after` does not satisfy a RESTRICT FK).

## 4. Cleanup scope vs operator's stated 5-row scope

**Operator's prior scope:** 4 `panel_output_record` smoke rows + 1 `authoring_panel_rejection_log` row = 5 rows.

**Actual minimum scope:** 5 `panel_output_record` smoke rows (operator's count missed the 2nd `bcf-live-smoke` row) + 1 `authoring_panel_rejection_log` + 4 `calibration_event` + 1 `certification_record` = **11 rows**.

**Why the original 5-row count is unexecutable:**
- The original count missed the 2-row pairing of the `bcf-live-smoke` cohort (APPROVE_FOR_DRAFT + REJECT).
- The original count did not survey downstream FK dependencies. The 9 inbound `RESTRICT` FK constraints from `contract.*` and `mcf.*` mean any `DELETE FROM contract.panel_output_record WHERE …` that does not first DELETE the dependent rows will fail with FK violation.

The expansion from 5 → 11 rows is **not scope creep** — it is the minimum closure of the dependency graph for the 5 smoke panels to be deletable. The 5 added rows (1 rejection_log + 4 calibration_event + 1 certification_record) are themselves classifiable as test artifacts by stable predicates (model_identity_json `"provider":"synthetic"`, policy_version smoke markers, 1:1 panel_run_uid join).

## 5. Dry-run SQL design

The dry-run SQL is read-only: it SELECTs every row that the planned DELETE statements would touch and writes them to evidence artifacts (JSONL + summary.md). No rows mutated. The output JSONL captures the full row before any execution, providing the snapshot for §7 rollback.

```sql
-- ── 5.1 panel_output_record candidates ──
SELECT * FROM contract.panel_output_record
WHERE panel_run_uid IN (
  'c05258de-8a62-456e-89fd-220a16684268',
  '54890bec-28cb-4d55-8aeb-fb3f81e0b359',
  'c6d85db6-c466-4993-8fdf-959ae33ffbe2',
  'c20f4d65-2021-451f-aebb-10cc8ca1249c',
  '6aaad537-eab9-4bca-a6cc-4acff74211ff'
)
ORDER BY created_at ASC;

-- ── 5.2 authoring_panel_rejection_log candidates ──
SELECT * FROM contract.authoring_panel_rejection_log
WHERE panel_run_uid IN (<same 5 uids>);

-- ── 5.3 calibration_event candidates ──
SELECT * FROM contract.calibration_event
WHERE panel_run_uid IN (<same 5 uids>);

-- ── 5.4 certification_record candidates ──
SELECT * FROM contract.certification_record
WHERE panel_run_uid IN (<same 5 uids>);

-- ── 5.5 Preserve-scope assertions (must hold; if not, ABORT) ──
SELECT COUNT(*)::int = 19 AS preserved_registry_authoring_intact
FROM contract.panel_output_record
WHERE prompt_version = 'registry-authoring/v1.0' AND policy_version = 'v1';

SELECT SUM(n_live_tup)::int = 0 AS mcf_substrate_untouched
FROM pg_stat_user_tables WHERE schemaname='mcf';

SELECT COUNT(*)::int >= 1241 AS metric_definition_untouched
FROM metric.metric_definition;

SELECT COUNT(*)::int = 780 AS contract_metric_contract_untouched
FROM contract.metric_contract;

-- ── 5.6 FK-chain closure assertion ──
-- For every smoke panel_run_uid, every inbound FK row count = 0 EXCEPT
-- the 3 expected sources (authoring_panel_rejection_log + calibration_event
-- + certification_record). All 6 mcf.* sources should be 0.
SELECT 'authoring_panel_rejection_log' AS src, COUNT(*)::int AS rows
FROM contract.authoring_panel_rejection_log
WHERE panel_run_uid IN (<5 smoke uids>)
UNION ALL SELECT 'calibration_event', COUNT(*) FROM contract.calibration_event WHERE panel_run_uid IN (...)
UNION ALL SELECT 'certification_record (contract)', COUNT(*) FROM contract.certification_record WHERE panel_run_uid IN (...)
UNION ALL SELECT 'intake_queue', COUNT(*) FROM contract.intake_queue WHERE panel_run_uid IN (...)
UNION ALL SELECT 'mcf.certification_record', COUNT(*) FROM mcf.certification_record WHERE panel_run_uid IN (...)
UNION ALL SELECT 'mcf.metric_authoring_panel_run', COUNT(*) FROM mcf.metric_authoring_panel_run WHERE panel_run_uid IN (...)
UNION ALL SELECT 'mcf.metric_contract_revision', COUNT(*) FROM mcf.metric_contract_revision WHERE panel_run_uid IN (...)
UNION ALL SELECT 'mcf.metric_publication_eligibility_result', COUNT(*) FROM mcf.metric_publication_eligibility_result WHERE panel_run_uid IN (...)
UNION ALL SELECT 'mcf.metric_supersession', COUNT(*) FROM mcf.metric_supersession WHERE panel_run_uid IN (...);
-- Expected: 1 + 4 + 1 + 0 + 0 + 0 + 0 + 0 + 0 = 6 (no surprises)
```

The dry-run script `scripts/bcf-authoring-test-row-cleanup-dry-run.mjs` (TO BE AUTHORED in bc-core during execution gate) runs all of the above as read-only queries, writes a `.precondition.jsonl` (one row per pre-existing row) + `.summary.md`, and computes a sha256 over the planned DELETE SQL for the post-apply gate.

## 6. Planned DELETE SQL design

Executed inside a single transaction; deletion order respects all 9 RESTRICT FKs.

```sql
BEGIN;

-- ── Step 1: delete leaf dependencies first ──
-- 1.a calibration_event (4 rows; leaf — no inbound FKs)
DELETE FROM contract.calibration_event
WHERE panel_run_uid IN (<5 smoke uids>);
-- Expected delta: -4 rows

-- 1.b authoring_panel_rejection_log (1 row; leaf — no inbound FKs)
DELETE FROM contract.authoring_panel_rejection_log
WHERE panel_run_uid IN (<5 smoke uids>);
-- Expected delta: -1 row

-- 1.c certification_record (1 row; verified no inbound FKs reference it)
DELETE FROM contract.certification_record
WHERE panel_run_uid IN (<5 smoke uids>)
  AND model_identity_json->'maker'->>'provider' = 'synthetic';
-- Belt-and-braces: confine to provider=synthetic to refuse to delete any
-- non-synthetic cert row that may have been written against the same panel
-- uids by future error. Expected delta: -1 row.

-- ── Step 2: delete panel_output_record (now FK-clear) ──
DELETE FROM contract.panel_output_record
WHERE panel_run_uid IN (<5 smoke uids>);
-- Expected delta: -5 rows

-- ── Step 3: in-tx invariants (assert before COMMIT) ──
-- contract.panel_output_record = 19 (was 24 - 5)
-- contract.authoring_panel_rejection_log = 0 (was 1 - 1)
-- contract.calibration_event = 19 (was 23 - 4)
-- contract.certification_record = 3530 (was 3531 - 1)
-- All 17 mcf.* = 0 (unchanged)
-- metric.metric_definition >= 1241 (unchanged)
-- contract.metric_contract = 780 (unchanged)
-- 19 registry-authoring/v1.0 panel rows still present (unchanged)
-- All 3 framework_policy rows still present (unchanged)

COMMIT;
-- ON FAILURE OF ANY ASSERTION: ROLLBACK and surface in summary as APPLY_FAILED.
```

The apply script `scripts/bcf-authoring-test-row-cleanup-apply.mjs` (TO BE AUTHORED) wraps this in a transaction, captures per-statement row deltas, writes `.evidence.jsonl` (one record per deleted row, mirroring the dry-run precondition) + `.summary.md`, verifies the sha256 of the planned-SQL fingerprint matches dry-run, and runs the post-apply invariants. On any pre-condition mismatch (e.g., row counts drift between dry-run and apply), the script ROLLBACKs.

## 7. Snapshot / rollback plan

### 7.1 Snapshot

The dry-run `.precondition.jsonl` is the canonical snapshot. Every row in scope is captured at full fidelity (every column). The apply script also re-captures the same rows inside the transaction before deletion to detect drift.

### 7.2 Rollback

Two independent rollback paths:

#### 7.2.1 Same-session ROLLBACK
If the apply script detects any pre-condition mismatch inside the transaction, it ROLLBACKs. DB returns to pre-script state immediately.

#### 7.2.2 Post-apply restore from snapshot
A separate `scripts/bcf-authoring-test-row-cleanup-restore.mjs` (TO BE AUTHORED) reads the `.precondition.jsonl` from a prior dry-run + the `.evidence.jsonl` from a prior apply and re-INSERTs the 11 rows in reverse dependency order (panel_output_record → certification_record → authoring_panel_rejection_log → calibration_event). Uses `INSERT … ON CONFLICT (pk) DO NOTHING` idempotency.

Restoration is reversible because:
- All 11 rows have stable UUID primary keys captured in the snapshot
- No DDL is involved (pure DML)
- No downstream tables CASCADEd off the smoke cert/calibration/rejection_log (verified empty FK closure in §3.3)

### 7.3 What rollback CANNOT restore

- BCF-side timestamps will differ: `created_at` of restored rows will reflect the restore time, not the original 2026-05-20 time. Mitigation: include `OVERRIDING SYSTEM VALUE` if `created_at` is a generated default, or explicitly set `created_at` from the snapshot in the restore INSERT.
- Sequential ordering of cert IDs may shift if any other cert was written between cleanup and restore. Mitigation: pin all UUIDs in the restore INSERTs.

## 8. Evidence artifact names

Following the M-series convention:

| Phase | Filename | Location |
|---|---|---|
| Dry-run preconditions | `bcf-authoring-test-row-cleanup-dry-run-<ts>.precondition.jsonl` | `bc-core/scripts/audit-output/` |
| Dry-run summary | `bcf-authoring-test-row-cleanup-dry-run-<ts>.summary.md` | same |
| Dry-run planned-SQL fingerprint | `bcf-authoring-test-row-cleanup-dry-run-<ts>.planned-sql.sha256.txt` | same |
| Post-apply evidence (deleted-row snapshots) | `bcf-authoring-test-row-cleanup-post-apply-<ts>.evidence.jsonl` | same |
| Post-apply summary | `bcf-authoring-test-row-cleanup-post-apply-<ts>.summary.md` | same |
| Closeout doc | `bcf-authoring-test-row-cleanup-closeout.md` | `bc-docs-v3/docs/implementation/` |

`<ts>` = ISO 8601 with colons replaced by hyphens (e.g., `2026-05-28T14-01-39-509Z`).

## 9. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Operator's prior "5-row" scope mismatches actual 11-row minimum closure; misapproval if not reconciled in §10 D1 | HIGH (already a finding in this DBCP) | MEDIUM (DBCP could be approved against the wrong number) | Explicit §10 D1 acknowledgment required |
| R2 | New chain rows written between DBCP approval and execution that reference the smoke panel_run_uids (e.g., a future calibration loop appends to the smoke runs) | LOW (smoke runs are 2026-05-20; no new dev work on this date is active) | MEDIUM (DELETE would fail FK violation; rollback safe) | Apply script runs §5.6 FK-closure assertion at the top of the transaction; ROLLBACK on drift |
| R3 | `contract.certification_record` row (`21023aa1-…`) was misclassified as test (in reality references a real BCF business_field via primitive_id) | MEDIUM | MEDIUM (deleting could orphan an audit trail) | Triple-marker classification: `model_identity_json.maker.provider = 'synthetic'` + paired with smoke panel + `sampling_status='sampled_for_calibration'`. Operator confirms in §10 D2. Also: the BF row at `019e45f2-…` is NOT touched by this cleanup (only the cert) |
| R4 | The smoke `business_field` UUID `019e45f2-c97c-7274-a6e4-95b2e45f451c` referenced by the cert may also live in `concept_registry.business_concept` or `concept_registry.business_field_*`; deleting the cert without addressing the BF leaves a half-state | LOW | LOW | Out of scope for this DBCP. BCF concept_registry is not touched. The cert deletion does not require the BF row to also be deleted (no inbound FK); the BF row is independently authoritative. Confirm operator decides in §10 D3 |
| R5 | Future `RegistryAuthoringOrchestrator` runs may write to the same `policy_version='v1'` as the `bcf-live-smoke` cohort C rows; predicate `prompt_version='bcf-live-smoke/2026-05-20'` alone disambiguates, but cohort A uses `policy_version='smoke-test/pr10'` (panel #1 has no calibration_event so this is a quirk) | LOW | LOW | Predicates pin BOTH prompt_version AND policy_version. Specific panel_run_uid IN(…) form is even more conservative; recommend uid-based deletion in apply script |
| R6 | Apply script writes rows that are mishandled by an unmocked downstream BCF reader/audit tool that did not expect the deletions (e.g., chain_status materialized view miscount) | LOW | LOW | Smoke cohort is BCF-only and never bubbled into `contract.chain_status` (verified: 540 chain_status rows but none reference these 5 smoke panel_run_uids — the chain_status table is metric-side / MCF chain). Re-verify in apply pre-condition |
| R7 | The DBCP's "minimal" framing conflates with future M12 first-real BCF→MCF prerequisites; operator might assume this cleanup unblocks M12 first run | LOW | LOW | §1.2 + §11 make explicit: this is BCF authoring-table hygiene only. The M12 first-real-panel-run unblock is a separate gate covering **real vendor-API-backed panel execution and/or operator-authored payload** (per the no-synthetic hard rule — synthetic adapters, cached replay, canned transcripts, and mock panel outputs are disallowed for any persistent substrate write; mocks remain allowed only inside unit tests or SAVEPOINT-rolled-back integration tests) plus operator CLI authoring |

## 10. Operator decisions required before execution

| # | Decision | Default proposal | Operator must confirm |
|---|---|---|---|
| **D1** | Accept the **11-row scope** (5 + 1 + 4 + 1) as the minimum closure of the FK dependency graph | ACCEPT | Y / N |
| **D2** | Confirm the `certification_record` row (`21023aa1-…`) is treated as a smoke artifact based on `model_identity_json.maker.provider = 'synthetic'` + paired with smoke panel cohort C | ACCEPT | Y / N |
| **D3** | Leave the BCF `business_field` row (`019e45f2-…`, primitive referenced by the deleted cert) UNTOUCHED in `concept_registry` for separate review | ACCEPT | Y / N |
| **D4** | Use hard DELETE (no archive column available on 3 of 4 tables anyway). Reject the "soft tombstone" option | ACCEPT | Y / N |
| **D5** | Apply order = leaves first (calibration_event → authoring_panel_rejection_log → certification_record → panel_output_record), single transaction | ACCEPT | Y / N |
| **D6** | Evidence artifacts named per the M-series convention (§8); closeout doc lands in `bc-docs-v3/docs/implementation/bcf-authoring-test-row-cleanup-closeout.md` after apply | ACCEPT | Y / N |
| **D7** | This cleanup is treated as a **prerequisite** for the M12 first-real-panel-run gate, NOT for M13/M12.5 closeout (already locked) | ACCEPT | Y / N |
| **D8** | Schedule: dry-run + post-apply gate run on the same operator-authorized session; restore script kept on-hand but not pre-emptively run | ACCEPT | Y / N |
| **D9** | **Affirm the no-synthetic hard rule.** No synthetic / mock / replay / canned data may be written to any persistent substrate going forward. This cleanup retires existing smoke debt (the 1 synthetic `certification_record` + 4 smoke `calibration_event` + 1 smoke `authoring_panel_rejection_log` + 5 smoke `panel_output_record` rows) and is **NOT** a delete-and-reseed pattern. Any future row matching `model_identity_json.*.provider IN ('synthetic','replay','mock','canned')` (or equivalent markers) is automatically out-of-scope-for-persistence and must be rejected at the writer boundary, not retired after the fact. Mocks remain allowed only inside unit tests or SAVEPOINT-rolled-back integration tests. | ACCEPT | Y / N |

## 11. Explicit non-scope statement

This DBCP is **NOT MCF cleanup** — the `mcf.*` substrate is already at 0 rows across all 17 tables (verified at the M13 closeout-readiness gate); nothing to clean. This DBCP does NOT touch any `mcf.*` row.

This DBCP is **NOT legacy `metric.*` retirement** — the 16,820 rows in `metric.*` (including the 2 active AR pilot KPIs `ar_growth_rate` and `revenue_collection_rate` plus all MLS / lifecycle / formula / readiness ledger infrastructure) are explicitly preserved. Their eventual retirement belongs to a separate gate alongside M17 tenant-runtime migration per the M12 implementation closeout §9.

This DBCP is **NOT chain-table cleanup** — `contract.source_contract` / `admission_contract` / `canonical_contract` / `observation_contract` / `metric_contract` / `chain_status` / `chain_trace` / `mc_integrity_state` / `l_node_semantic_trace` / `l_node_semantic_verdict` / `framework_policy` are explicitly preserved. The 1 cert row + 4 calibration rows that ARE touched are 1:1 dependents of the 5 smoke panel runs and are themselves classifiable as test artifacts.

This DBCP is **NOT tenant-results cleanup or migration** — all tenant analytical substrate (per-tenant snapshots, fact tables, evaluation results, MLS-15..MLS-25 tenant-side state) lives in `tbc_{slug}_dev` databases per D162-D167 (separate DB cluster from `bc_platform_dev`). This cleanup operates exclusively against the platform DB. No tenant DB connection is opened by any of the scripts authored under the execution gate.

This DBCP **does NOT unblock the M12 first-real-panel-run** — that gate requires separately: (a) **real vendor-API-backed panel execution and/or operator-authored payload** (per the no-synthetic hard rule — synthetic adapters, cached replay, canned transcripts, and mock panel outputs are **disallowed** for any persistent substrate write; mocks remain allowed only inside unit tests or SAVEPOINT-rolled-back integration tests), (b) operator-authored metric request JSON, (c) M12 operator CLI authoring or NestJS DI registration, (d) optional M12 allowlist seed execution. None of those are addressed here.

## 12. Discipline assertions (this DBCP-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — DBCP file lands only in bc-docs-v3 |
| No DDL applied | ✓ |
| No DML applied | ✓ |
| No M11 / M12 / M12.5 / M13 invocation | ✓ |
| `bc-postgres` MCP `allow_write=false` throughout | ✓ |
| No `mcf.*` touched | ✓ |
| No `metric.*` touched | ✓ |
| No `contract.metric_contract` / chain tables touched | ✓ |
| M14 still CLOSED | ✓ |
| No bc-admin / tenant-runtime / controllers / DI modules touched | ✓ |
| Future scripts (`dry-run.mjs` / `apply.mjs` / `restore.mjs`) and any tests authored under the execution gate MUST use mocks only inside unit tests or SAVEPOINT-rolled-back integration tests; no persistent mock/synthetic/replay/canned data may be written by any of these scripts to `bc_platform_dev` or any tenant `tbc_{slug}_dev` | ✓ — locked by no-synthetic hard rule; execution-gate DBCP will re-affirm at script-authoring time |

## 13. Sequencing

1. **This DBCP merges** → operator reviews §10 D1..D8 in a follow-up gate.
2. **Operator authorizes the 8 decisions** (or amends them) in writing.
3. **Execution gate opens** — author the 3 scripts (`dry-run.mjs`, `apply.mjs`, `restore.mjs`) in bc-core; PR-1 (dry-run) + PR-2 (apply + closeout) as separate gates.
4. **Apply gate executes** under operator-authorized session with `bc-postgres` MCP temporarily flipped to `allow_write=true` for the apply script's window only.
5. **Closeout doc lands** documenting before/after row counts + evidence artifact references.
6. **M12 first-real-panel-run DBCP can then proceed** without ambiguous test rows in the BCF authoring substrate.

---

**End of DBCP. NOT YET EXECUTED. Operator authorization on §10 D1..D8 required before any script work begins.**
