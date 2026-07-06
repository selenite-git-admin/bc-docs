---
title: "D408 DBCP-1q-A verification plan"
date: 2026-05-16
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
dbcp_design: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md
session: SES-8714df
type: verification-plan
status: proposed
---

# D408 DBCP-1q-A verification plan

**This is the verification plan only. It does not authorise SQL execution. Steps run in order in dev → staging → prod; each environment requires operator sign-off before promoting.**

## 0. Authority and artifacts under test

- **ADR:** [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md) — DEC-1ce490 / D408 (decided).
- **DBCP design:** [2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md](2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md).
- **Forward SQL:** `bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-a-bf-catalog-admission-state.sql`.
- **Reverse SQL:** `bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-a-bf-catalog-admission-state.revert.sql`.
- **Backfill script:** `bc-core/scripts/d408-backfill-bf-catalog-state-1q-a.mjs` (dry-run default; APPLY requires `--apply` AND `D408_APPLY=1`).
- **Audit artifact** (read by backfill): `bc-core/scripts/audit-output/d408-bf-admission-audit-calibrated-2026-05-16T04-50-46-684Z.per-bf.jsonl`.

## 1. Pre-flight (read-only; environment-agnostic)

Run **before** applying the forward SQL.

### 1.1 D408 invariant

```sql
SELECT COUNT(*) AS rbs_total
  FROM contract.certification_record
 WHERE action_code = 'remediate_bf_semantics';
-- Expected: 1392
```

### 1.2 Pre-DBCP row count snapshots (record baseline)

```sql
SELECT 'business_field' AS tbl, COUNT(*) FROM contract.business_field
UNION ALL SELECT 'cc_field_mapping',     COUNT(*) FROM contract.cc_field_mapping
UNION ALL SELECT 'business_object_field',COUNT(*) FROM contract.business_object_field
UNION ALL SELECT 'business_field_alias', COUNT(*) FROM contract.business_field_alias
UNION ALL SELECT 'canonical_field',      COUNT(*) FROM contract.canonical_field
UNION ALL SELECT 'metric_contract',      COUNT(*) FROM contract.metric_contract
UNION ALL SELECT 'certification_record', COUNT(*) FROM contract.certification_record;
```

Record these counts; §3.4 verifies most are unchanged after the full DBCP.

### 1.3 No prior 1q-A schema

```sql
SELECT column_name
  FROM information_schema.columns
 WHERE table_schema='contract' AND table_name='business_field'
   AND column_name IN ('catalog_state_code','gate_signals_json','archived_at');
-- Expected: 0 rows (DBCP-1q-A has not been applied yet)
```

### 1.4 Dry-run backfill plan stats

```sh
node bc-core/scripts/d408-backfill-bf-catalog-state-1q-a.mjs
```

Expected output (from 2026-05-16 audit):

| Cohort | Expected count |
|---|---:|
| Total BFs in audit | 7,062 |
| P0 (correction_required, broken-fallback ∩ CC) | **4** |
| P1 (correction_required, T4 hard-fail) | **11** |
| P2 (correction_required, G3 type-incoherence) | **15** |
| GRANDFATHER (certified_catalog, T3 \| T4 \| T1_req_or_bk hard-pass) | **1,651** |
| SKIP (out of 1q-A scope) | **5,381** |
| **Rows to touch in 1q-A** | **1,681** |

If any cohort differs by more than ±5, **halt and investigate**. Either the audit artifact has changed, or the classification logic has drifted.

## 2. Forward SQL apply (schema only)

Operator runs:

```sh
psql "$DATABASE_URL" -f bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-a-bf-catalog-admission-state.sql
```

### 2.1 Mid-flight checks (immediately after forward SQL)

```sql
-- New columns present (expect 13 rows)
SELECT column_name, data_type, is_nullable, column_default
  FROM information_schema.columns
 WHERE table_schema='contract' AND table_name='business_field'
   AND column_name IN (
     'catalog_state_code','catalog_state_reason_code','catalog_state_reason_text',
     'catalog_reviewed_at','catalog_review_run_uid',
     'gate_signals_json','gate_signals_at','gate_signals_row_hash',
     'admission_rule_version_at_certify','certification_record_id',
     'source_origin_code','source_origin_ref','archived_at'
   )
 ORDER BY column_name;
-- Expected: 13 rows; catalog_state_code default = 'candidate_import', NOT NULL; all others NULL/nullable.
```

```sql
-- CHECK constraints present (expect 2 rows on business_field)
SELECT conname, pg_get_constraintdef(oid)
  FROM pg_constraint
 WHERE conrelid='contract.business_field'::regclass
   AND conname IN (
     'business_field_catalog_state_code_chk',
     'business_field_catalog_state_reason_code_chk'
   );
-- Expected: 2 rows, definitions match SQL file.
```

```sql
-- FK present
SELECT conname, pg_get_constraintdef(oid)
  FROM pg_constraint
 WHERE conrelid='contract.business_field'::regclass
   AND conname = 'business_field_certification_record_id_fk';
-- Expected: 1 row, references contract.certification_record(certification_record_id).
```

```sql
-- Whitelist table + 3 seed rows
SELECT field_name, owner_email, char_length(rationale_text) AS rationale_len
  FROM contract.business_field_foundational_whitelist
 ORDER BY field_name;
-- Expected: 3 rows: country_code / currency_code / language_code, owner_email='anant@selenite.co', rationale_len >= 40.
```

```sql
-- certification_record CHECK widened to 15 values
SELECT pg_get_constraintdef(oid)
  FROM pg_constraint
 WHERE conrelid='contract.certification_record'::regclass
   AND conname='certification_record_action_code_chk';
-- Expected: definition includes all 15 codes: 10 pre-existing + admit_bf_catalog,
-- demote_bf_catalog, mark_bf_correction_required, recertify_bf_catalog, mark_recertify_pending.
```

```sql
-- All existing BF rows now carry catalog_state_code = 'candidate_import' (DEFAULT applied at ALTER)
SELECT catalog_state_code, COUNT(*)
  FROM contract.business_field
 GROUP BY catalog_state_code;
-- Expected: single row 'candidate_import' = 7062.
```

```sql
-- Invariant still holds
SELECT COUNT(*) FROM contract.certification_record
 WHERE action_code='remediate_bf_semantics';
-- Expected: 1392.
```

## 3. Backfill script apply (data only, after schema verified)

Operator runs (in apply mode, double-guarded):

```sh
D408_APPLY=1 node bc-core/scripts/d408-backfill-bf-catalog-state-1q-a.mjs --apply
```

Either guard alone leaves the script in dry-run; the script logs its mode in the first 6 lines of output.

### 3.1 Mid-apply (script reports progress every 100 rows)

Expected progress messages: `Applied: 100/1681`, `Applied: 200/1681`, …, `Applied: 1681 rows updated, 0 skipped (already non-default).` Final summary on success.

### 3.2 Post-backfill row counts by `catalog_state_code`

```sql
SELECT catalog_state_code, catalog_state_reason_code, COUNT(*)
  FROM contract.business_field
 GROUP BY catalog_state_code, catalog_state_reason_code
 ORDER BY catalog_state_code, catalog_state_reason_code;
```

Expected (sums of 1q-A backfill + remaining default rows):

| catalog_state_code | catalog_state_reason_code | Count |
|---|---|---:|
| `candidate_import` | `NULL` | **5,381** |
| `certified_catalog` | `legacy_hard_pass_grandfathered` | **1,651** |
| `correction_required` | `broken_fallback_definition` | **4** |
| `correction_required` | `definition_too_short` | (subset of P1 with G1 fail) |
| `correction_required` | `type_incoherence` | (subset of P1 with G3 fail + all P2) |
| **Sum of correction_required** | (any) | **30** |
| **Total** | – | **7,062** |

If totals don't sum to 7,062, halt.

### 3.3 Paired certification_record ledger rows

```sql
SELECT action_code, COUNT(*)
  FROM contract.certification_record
 WHERE primitive_type='business_field'
   AND created_at >= (now() - interval '1 day')  -- adjust window per actual apply time
 GROUP BY action_code
 ORDER BY action_code;
```

Expected:
- `admit_bf_catalog`: **1,651** (grandfather cohort)
- `mark_bf_correction_required`: **30** (P0 + P1 + P2)
- Total new ledger rows in window: **1,681**

```sql
-- Every touched BF has its certification_record_id populated
SELECT COUNT(*) FROM contract.business_field
 WHERE catalog_state_code IN ('certified_catalog','correction_required')
   AND certification_record_id IS NULL;
-- Expected: 0.
```

```sql
-- Every new ledger row carries gate_results_json with audit_run_uid
SELECT COUNT(*) FROM contract.certification_record
 WHERE primitive_type='business_field'
   AND action_code IN ('admit_bf_catalog','mark_bf_correction_required')
   AND gate_results_json->>'audit_run_uid' = 'audit-2026-05-16T04-50-46-684Z';
-- Expected: 1681.
```

### 3.4 Out-of-bounds (no spillover)

Compare with §1.2 pre-DBCP snapshots:

```sql
-- These counts MUST equal §1.2 baselines (no change)
SELECT COUNT(*) FROM contract.canonical_field;       -- unchanged
SELECT COUNT(*) FROM contract.metric_contract;       -- unchanged
SELECT COUNT(*) FROM contract.cc_field_mapping;      -- unchanged
SELECT COUNT(*) FROM contract.business_object_field; -- unchanged
SELECT COUNT(*) FROM contract.business_field_alias;  -- unchanged
SELECT COUNT(*) FROM contract.business_field;        -- unchanged at 7062

-- D408 invariant
SELECT COUNT(*) FROM contract.certification_record
 WHERE action_code='remediate_bf_semantics';         -- = 1392, unchanged
```

```sql
-- certification_record count CHANGED by exactly 1681
-- (§1.2 baseline + 1681 = post-backfill count)
SELECT COUNT(*) FROM contract.certification_record;
```

### 3.5 Tenant scope

**No tenant DB is touched by this DBCP.** Confirm by checking psql connection target is `bc_platform_dev` (or staging/prod platform equivalent), never a `tbc_*_dev` database. The backfill script reads `DATABASE_URL` only — it has no awareness of `TENANT_DATABASE_URL`.

```sh
# Operator visual check on the running command — script logs DATABASE_URL host:
node bc-core/scripts/d408-backfill-bf-catalog-state-1q-a.mjs 2>&1 | head -10
```

If `DATABASE_URL` points to a tenant DB by mistake, **halt immediately** before --apply.

## 4. Spot checks (sample inspection)

### 4.1 Sample P0 row

```sql
SELECT name, catalog_state_code, catalog_state_reason_code,
       LEFT(catalog_state_reason_text, 80) AS reason_snippet,
       gate_signals_json->>'audit_run_uid' AS audit_run,
       certification_record_id IS NOT NULL AS has_ledger
  FROM contract.business_field
 WHERE catalog_state_code='correction_required'
   AND catalog_state_reason_code='broken_fallback_definition'
 LIMIT 5;
-- Expected: 4 rows, all P0 cohort, all with paired ledger.
```

### 4.2 Sample grandfather row

```sql
SELECT name, catalog_state_code, catalog_state_reason_code, certification_record_id IS NOT NULL AS has_ledger
  FROM contract.business_field
 WHERE name = 'actual_ledger_amount';  -- T4 hard-pass with 319 cc_mappings
-- Expected: certified_catalog / legacy_hard_pass_grandfathered / has_ledger=true
```

### 4.3 Sample whitelist row

```sql
SELECT w.field_name, w.owner_email, b.catalog_state_code
  FROM contract.business_field_foundational_whitelist w
  LEFT JOIN contract.business_field b ON b.name = w.field_name
 WHERE w.field_name IN ('currency_code','language_code','country_code');
-- Expected: 3 rows. catalog_state_code may be 'certified_catalog' (if grandfathered via tier
-- in the backfill) or 'candidate_import' (if not yet touched — whitelist membership alone
-- does not auto-grandfather in 1q-A; that is handled in a later admission action).
```

## 5. Rollback path (if any check fails)

If a §2 mid-flight check or §3 post-backfill check fails irrecoverably, the operator may revert with:

```sh
# 1. Revert backfill data — DESTRUCTIVE (loses catalog_state_code values)
# Optional approach: write a one-off SQL to UPDATE catalog_state_code='candidate_import'
# and DELETE FROM certification_record WHERE primitive_type='business_field' AND created_at >= <apply window>.
# A reverse-data script is NOT provided in this DBCP because demotion is reversible by
# new ledger action per ADR §6 — preferred path is forward correction, not rollback.

# 2. Revert schema (after pre-checks in the .revert.sql header)
psql "$DATABASE_URL" -f bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-a-bf-catalog-admission-state.revert.sql
```

The reverse SQL has pre-check comments at its head; operator runs those queries first to confirm reverse is safe.

**Preferred response to a check failure is forward fix, not rollback.** Forward fix examples:
- Wrong reason_code on a specific cohort → small UPDATE with paired `mark_bf_correction_required` ledger row.
- Missed cohort → re-run backfill (idempotent — skips rows with non-default `catalog_state_code`).

## 6. Promotion sequence

| Env | Step |
|---|---|
| dev | §1 pre-flight → §2 forward SQL → §2.1 mid-flight checks → §3 backfill apply → §3.2–3.5 post checks. |
| | **Operator sign-off recorded in DevHub checkpoint on SES-8714df** before promoting to staging. |
| staging | §1 pre-flight → §2 forward SQL → §2.1 mid-flight checks → §3 backfill apply → §3.2–3.5 post checks. |
| | **Operator sign-off recorded** before promoting to prod. |
| prod | §1 pre-flight → §2 forward SQL → §2.1 mid-flight checks → §3 backfill apply → §3.2–3.5 post checks. |
| | **Operator sign-off recorded.** Then DBCP-1q-B (Tranche 2 demotions) becomes the next artifact to author. |

## 7. Out of scope (explicit)

- No service-code change (GS-1 through GS-5 are separate slices).
- No bc-admin UI change.
- No tenant DB touched.
- No `contract.canonical_field` change.
- No `contract.metric_contract` change.
- No P3 / P4 demotion in 1q-A (deferred to DBCP-1q-B).
- No registered-abbreviation registry (separate ADR).
- No G3 LLM / G4 embedding (separate ADRs).

### 7.1. Fallback-definition admissibility (added 2026-05-16, post-1q-A)

Per ADR §2.2 and DBCP §10.6: no fallback / synthetic / template definition may pass G1 for `certified_catalog`. The 1q-A backfill grandfathered 1,651 rows that passed the calibrated audit's G1 regex set, which catches the literal `"… from OAGIS undefined"` pattern and CCTS boilerplate but **does not yet catch the broader synthetic-template family** (e.g. `"<field> on <component> (OAGIS <noun>)"`). Consequence:

- The 1q-A `certified_catalog` cohort may contain rows whose definitions are synthetic templates under ADR §2.2's tighter rule.
- A future audit cycle with the extended G1 pattern set will surface those rows for `recertify_pending` → human review. 1q-A is not retroactively re-classified.
- DBCP-1q-B (Tranche 2 demotions) must run with the extended G1 set before authoring its row list, so demotion is not blind to the broader pattern.
- The OAGIS onboarding service path remains a live importer-compliance gap (ADR Open item §6); fix is a separate slice, not part of 1q-A or 1q-B.

## 8. References

- ADR: [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md)
- DBCP design: [2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md](2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md)
- Calibrated audit (md): `bc-core/scripts/audit-output/d408-bf-admission-audit-calibrated-2026-05-16T04-50-46-684Z.md`
- Calibrated audit (per-bf): `bc-core/scripts/audit-output/d408-bf-admission-audit-calibrated-2026-05-16T04-50-46-684Z.per-bf.jsonl`
- Sibling DBCP-1p pattern: `bc-core/docker/redesign/migrations/20260515-d407-dbcp-1p-certification-record-remediate-bf-semantics.sql`
- D162 (database rules): `bc-docs-v3/docs/adrs/ADR-1918d0.md`
- D268 (session discipline): `bc-docs-v3/docs/adrs/ADR-ebf0b4.md`
