---
title: "D408 DBCP-1q-C verification plan — credit_type_code mapping removal"
date: 2026-05-17
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
plan: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md
session: SES-c5af8c
type: verification-plan
status: proposed
---

# D408 DBCP-1q-C verification plan

**This is the verification plan only. It does not authorise SQL execution.** DBCP-1q-C may only run after operator sign-off on this plan.

## 0. Authority and artifacts under test

- **ADR:** [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md) — DEC-1ce490 / D408 (decided).
- **Correction plan:** [2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md](../../work-records/onboarding/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md). Disposition locked at §11a.1.
- **Forward SQL:** `bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-c-remove-credit-type-code-cc-mappings.sql`.
- **Reverse SQL:** `bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-c-remove-credit-type-code-cc-mappings.revert.sql`.
- **Pre-state JSON extract:** `bc-core/scripts/audit-output/d408-1q-c-credit-type-code-target-mappings.json`.

## 1. Pre-flight (read-only)

### 1.1 D408 invariants

```sql
SELECT
  (SELECT COUNT(*)::int FROM contract.certification_record WHERE action_code='remediate_bf_semantics') AS rbs,
  (SELECT COUNT(*)::int FROM contract.certification_record WHERE action_code='admit_bf_catalog') AS admit,
  (SELECT COUNT(*)::int FROM contract.certification_record WHERE action_code='mark_bf_correction_required') AS mark,
  (SELECT COUNT(*)::int FROM contract.certification_record WHERE action_code='demote_bf_catalog') AS demote;
-- Expected: 1392 / 1651 / 30 / 374
```

### 1.2 Target predicate returns exactly 11 rows

```sql
SELECT
  cfm.cc_field_mapping_id, cc.canonical_contract_name AS cc_name,
  cf.field_name AS cf_name, cf.data_type AS cf_data_type,
  bf.name AS bf_name, bf.data_type AS bf_data_type,
  cfm.resolution_rule_code AS rule_code
FROM contract.cc_field_mapping cfm
JOIN contract.canonical_contract cc ON cc.canonical_contract_id = cfm.canonical_contract_id
JOIN contract.canonical_field    cf ON cf.canonical_field_id    = cfm.canonical_field_id
JOIN contract.business_field     bf ON bf.field_id              = cfm.business_field_id
WHERE bf.name = 'credit_type_code'
  AND cc.canonical_contract_name = 'cc__credit'
  AND cfm.resolution_rule_code = 'assert_equal'
  AND cf.data_type IN ('number','date')
ORDER BY cf.field_name;
-- Expected: 11 rows. cf_name values must match the operator-approved whitelist:
--   automated_credit_decisions_count, available_credit_lines,
--   credit_application_submission_date, credit_approval_completion_date,
--   customer_credit_risk_rating, drawn_credit_facility_amount,
--   revolving_credit_drawn, revolving_credit_limit,
--   total_credit_decisions_count, total_credit_deployed,
--   total_credit_facility_limit
-- bf_data_type must be 'code' for every row.
```

If the query returns a row count ≠ 11 or any cf_name not in the whitelist, **halt and investigate**. The forward SQL's PL/pgSQL pre-check will refuse with `RAISE EXCEPTION` in this case; this manual query confirms the same predicate before invoking psql.

### 1.3 Baseline row counts (capture for §3 comparison)

```sql
SELECT 'cc_field_mapping' AS tbl, COUNT(*) FROM contract.cc_field_mapping
UNION ALL SELECT 'canonical_field',  COUNT(*) FROM contract.canonical_field
UNION ALL SELECT 'metric_contract',  COUNT(*) FROM contract.metric_contract
UNION ALL SELECT 'metric_binding',   COUNT(*) FROM metric.metric_binding
UNION ALL SELECT 'business_field',   COUNT(*) FROM contract.business_field
UNION ALL SELECT 'certification_record', COUNT(*) FROM contract.certification_record;
```

Record these counts; §3 compares.

### 1.4 cc__credit metric bindings (informational; not changed by this DBCP)

```sql
SELECT mb.metric_contract_id, mc.metric_contract_name
  FROM metric.metric_binding mb
  JOIN contract.metric_contract mc ON mc.metric_contract_id = mb.metric_contract_id
 WHERE mb.canonical_contract_id = '019d762a-1998-738d-9b42-f14e1e6ed892';
-- Expected ~6 rows. These bindings remain after this DBCP but will produce
-- incoherent evaluations for the 11 orphaned CFs until the orphan-CF triage
-- task lands. This is the accepted blast radius per plan §11a.1.
```

## 2. Apply

Operator runs:

```sh
docker exec -i bc-postgres-redesign psql -U barecount -d bc_platform_dev \
  < bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-c-remove-credit-type-code-cc-mappings.sql
```

Expected output sequence:

```
BEGIN
NOTICE:  DBCP-1q-C pre-check OK: exactly 11 target rows match the whitelisted predicate.
SELECT 1            (or similar, from the CTE pre-check temp table)
DELETE 11
NOTICE:  DBCP-1q-C post-check OK: zero target rows remain.
COMMIT
```

If the output shows `DELETE` with anything other than `11`, the COMMIT will still proceed but the post-check `DO $$` block raises an exception, rolling back the transaction (per PostgreSQL transaction-on-exception semantics). Operator must investigate before retrying.

## 3. Post-apply verification (read-only)

### 3.1 D408 invariants unchanged

```sql
SELECT
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='remediate_bf_semantics') AS rbs,
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='admit_bf_catalog') AS admit,
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='mark_bf_correction_required') AS mark,
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='demote_bf_catalog') AS demote;
-- Expected (unchanged from §1.1): 1392 / 1651 / 30 / 374
```

### 3.2 Target predicate returns zero rows

```sql
SELECT COUNT(*) FROM contract.cc_field_mapping cfm
  JOIN contract.canonical_contract cc ON cc.canonical_contract_id = cfm.canonical_contract_id
  JOIN contract.canonical_field    cf ON cf.canonical_field_id    = cfm.canonical_field_id
  JOIN contract.business_field     bf ON bf.field_id              = cfm.business_field_id
 WHERE bf.name = 'credit_type_code'
   AND cc.canonical_contract_name = 'cc__credit'
   AND cfm.resolution_rule_code = 'assert_equal'
   AND cf.data_type IN ('number','date');
-- Expected: 0
```

### 3.3 cc_field_mapping count decreased by exactly 11

```sql
SELECT COUNT(*) FROM contract.cc_field_mapping;
-- Expected: (§1.3 baseline) - 11
```

### 3.4 Other tables unchanged

```sql
SELECT 'canonical_field' AS tbl, COUNT(*) FROM contract.canonical_field
UNION ALL SELECT 'metric_contract',      COUNT(*) FROM contract.metric_contract
UNION ALL SELECT 'metric_binding',       COUNT(*) FROM metric.metric_binding
UNION ALL SELECT 'business_field',       COUNT(*) FROM contract.business_field
UNION ALL SELECT 'certification_record', COUNT(*) FROM contract.certification_record;
-- Each must equal the §1.3 baseline exactly.
```

### 3.5 credit_type_code BF row unchanged

```sql
SELECT field_id, name, status_code, catalog_state_code, catalog_state_reason_code
  FROM contract.business_field
 WHERE name = 'credit_type_code';
-- Expected: catalog_state_code='correction_required'; catalog_state_reason_code='broken_fallback_definition'.
-- The BF row itself is NOT touched by this DBCP — its definition stays broken;
-- the correct-definition endpoint (separate slice) will fix it later.
```

### 3.6 The 11 canonical_field rows still exist

```sql
SELECT canonical_field_id, field_name, data_type
  FROM contract.canonical_field
 WHERE canonical_field_id IN (
   '881c329d-e3e7-406d-a70f-1443d59413b4', '015f1306-86f0-430a-883a-49adfaeee6c5',
   'fb538f29-162f-4267-a8b2-849e183af735', '85b073d9-f8a7-4efa-ae15-87a834f255ec',
   '489651c6-fd42-434d-8f18-966491fd1d0a', '9ecdd811-8ed6-4a3b-9e1f-137184e18ae6',
   'c6c03063-1537-42dd-933c-cea1e0b74f40', 'bd18ab56-8ac7-4650-821b-722da738b77f',
   '7c1469fe-cf2e-4f0f-bc44-072402762c2e', '38e2f1f6-938f-4db2-9e1f-cdb4ade8caeb',
   'e350d327-9dc0-4a6d-a69c-7203841dabd1'
 )
 ORDER BY field_name;
-- Expected: 11 rows. The CFs are intact; they just have no BF binding now.
-- (No cc_field_mapping row references them on cc__credit anymore.)
```

### 3.7 Tenant scope

**No tenant DB touched.** Confirm `DATABASE_URL` points to the platform DB (`bc_platform_dev` on dev; staging/prod platform equivalents).

## 4. Known blast radius

- **~66 MC references degrade.** Each of the 11 removed mappings was supporting metric evaluations against `cc__credit`. With 6 metric bindings per CF, ~66 distinct (MC × CF) pairs lose their BF backing.
- **No data loss.** Removed rows are reversible from the JSON extract via the .revert.sql file; no row content destroyed beyond the 11 mapping records themselves.
- **Orphan CFs.** The 11 CFs still exist as rows in `canonical_field`. They are now un-bound to any BF on `cc__credit`. The orphan-CF triage task (per plan §11a.1) is required to either re-bind them to a proper BF, convert them to compute mappings, or leave them un-bound until a suitable BF is admitted.
- **Operator accepted this window.** Per plan §11a.1: the alternative of leaving structurally-broken `code = number/date` assert_equal mappings in place is strictly worse than the degradation window.

## 5. Rollback

If DBCP-1q-C was applied in error, run the reverse SQL:

```sh
docker exec -i bc-postgres-redesign psql -U barecount -d bc_platform_dev \
  < bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-c-remove-credit-type-code-cc-mappings.revert.sql
```

Reverse SQL:
- Refuses if any of the 11 `cc_field_mapping_id` values already exist.
- Refuses if `credit_type_code` BF, `cc__credit` CC, or any of the 11 CFs is missing.
- Re-inserts the 11 rows with their **original** primary keys, FKs, rule_code, and `created_at` timestamps (sourced from the JSON extract).
- Post-check: 11 mappings binding `credit_type_code` exist after the run.

**Reverse reintroduces the semantic problem.** Run only if the operator decides DBCP-1q-C was authored against the wrong cohort or applied in error. The right correction path is **forward**: orphan-CF triage + `credit_type_code` definition correction.

## 6. Sign-off sequence (dev-only deployment)

1. Operator runs §1 read-only checks on dev. Confirms counts.
2. Operator runs §2 apply on dev.
3. Operator runs §3 post-apply checks on dev.
4. **Sign-off recorded** in DevHub checkpoint on SES-c5af8c (or successor session) with:
   - count of `cc_field_mapping` before / after.
   - confirmation that the 11 target rows are gone.
   - confirmation that D408 invariants are unchanged.

This deployment has no staging or prod environments; dev is production.

## 7. Out of scope

- No BF row update (`credit_type_code` itself stays `correction_required`).
- No CF row mutation.
- No metric_contract / metric_binding mutation.
- No tenant DB.
- No new endpoint authoring.
- No certification_record ledger row insert (mapping changes are not in the polymorphic ledger's primitive_type enum; see SQL file header).
- No orphan-CF re-binding (separate triage task).
- No `credit_type_code` definition fix (deferred to `correct-definition` endpoint slice).

## 8. References

- ADR: [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md)
- Correction plan: [2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md](../../work-records/onboarding/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md) §11a.1
- D408 data closeout: [2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md](../../closeouts/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md)
- D408 service-guard closeout: [2026-05-16-d408-service-guard-closeout-DEC-1ce490.md](../../closeouts/onboarding/2026-05-16-d408-service-guard-closeout-DEC-1ce490.md)
- Sibling DBCP-1q-A: `bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-a-bf-catalog-admission-state.sql`
- Sibling DBCP-1q-B: `bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-b-bf-catalog-demotions.sql`
- D162 (database rules): `bc-docs-v3/docs/adrs/ADR-1918d0.md`
