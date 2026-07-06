---
title: "D408 DBCP-1q-B verification plan"
date: 2026-05-16
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
dbcp_design: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md
predecessor: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-16-d408-dbcp-1q-a-verification-plan.md
session: SES-8714df
type: verification-plan
status: proposed
---

# D408 DBCP-1q-B verification plan

**This is the verification plan only. It does not authorise execution. DBCP-1q-B may only run after DBCP-1q-A has been applied and verified in the same environment.**

## 0. Authority and artifacts under test

- **ADR:** [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md) — DEC-1ce490 / D408 (decided).
- **DBCP design:** [2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md](2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md).
- **DBCP-1q-A verification plan (predecessor):** [2026-05-16-d408-dbcp-1q-a-verification-plan.md](2026-05-16-d408-dbcp-1q-a-verification-plan.md).
- **DBCP-1q-B precondition SQL:** `bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-b-bf-catalog-demotions.sql` (no DDL; PL/pgSQL preconditions only).
- **DBCP-1q-B reverse SQL:** `bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-b-bf-catalog-demotions.revert.sql` (documentation only; no destructive reverse SQL).
- **Demotion script:** `bc-core/scripts/d408-demote-bf-catalog-state-1q-b.mjs` (dry-run default; apply requires `--apply` AND `D408_APPLY=1`).
- **Fresh audit JSONL:** `bc-core/scripts/audit-output/d408-bf-admission-audit-calibrated-2026-05-16T08-32-46-736Z.per-bf.jsonl` (re-run after the importer fallback fix landed at `bc-core@186979d`; G1 patterns extended with `from_oagis_template` + `synthetic_oagis_on_template`).

## 1. Pre-flight (read-only)

### 1.1 D408 invariant

```sql
SELECT COUNT(*) FROM contract.certification_record
 WHERE action_code = 'remediate_bf_semantics';
-- Expected: 1392
```

### 1.2 1q-A baseline (must match exactly)

```sql
SELECT
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='admit_bf_catalog')              AS admit_total,
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='mark_bf_correction_required')   AS mark_total,
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='demote_bf_catalog')             AS demote_total,
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='candidate_import')             AS candidate_count,
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='certified_catalog')            AS certified_count,
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='correction_required')          AS correction_count,
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='demoted_catalog')              AS demoted_count;
```

Expected baseline (post-1q-A, pre-1q-B):

| Column | Value |
|---|---:|
| `admit_total` | 1,651 |
| `mark_total` | 30 |
| `demote_total` | **0** |
| `candidate_count` | 5,381 |
| `certified_count` | 1,651 |
| `correction_count` | 30 |
| `demoted_count` | **0** |

If any value differs, **halt and investigate**.

### 1.3 Re-run calibrated audit

```sh
node bc-core/scripts/audit-bf-admission-d408-calibrated.mjs
```

The audit is read-only and produces a new dated artifact under `bc-core/scripts/audit-output/`. Confirm the cohort sizes in the new artifact's `demotion_sizing` block match the 2026-05-16T08:32 audit (within ±5 rows):

| Bucket | Expected |
|---|---:|
| `t1_only_intersect_g1_fail_and_g5_structural` (P3) | 259 |
| `broken_fallback_no_anchor` (raw P4) | 370 |
| `broken_fallback_definitions_total` | 682 |
| `broken_fallback_with_cc_mapping` | 4 |

If the demotion sizing has shifted materially (e.g. counts differ by > ±5), **halt and investigate** before proceeding — likely cause is unrelated DB churn or an audit-rule version bump that must land in its own DBCP first.

### 1.4 Dry-run demotion plan

```sh
node bc-core/scripts/d408-demote-bf-catalog-state-1q-b.mjs
```

Expected stats (from 2026-05-16T08:35 dry-run):

| Cohort | Expected count |
|---|---:|
| Total BFs in audit | 7,062 |
| P3 (demoted_catalog, T1_only ∩ G1 fail ∩ G5 structural ∩ no_anchor) | **259** |
| P4 (demoted_catalog, banned-template ∩ no_anchor, excluding P3 overlap) | **115** |
| SKIP (out of 1q-B scope) | 6,688 |
| **Rows to touch in 1q-B** | **374** |

The deduplicated total (374) is materially less than the user's pre-design upper bound of "≤629" because P3 and P4 overlap by ~255 rows (T1_only banned-template rows with structural-only evidence). This is expected.

The dry-run also exercises the **baseline guard** (assertSchemaAndBaseline) and will refuse to proceed if:
- Any of the 11 1q-A columns is missing on `contract.business_field`.
- Baseline counts do not match the expected post-1q-A state.

If the dry-run reports a guard failure, **halt and investigate**.

## 2. Precondition SQL (no DDL)

Operator runs:

```sh
psql "$DATABASE_URL" -f bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-b-bf-catalog-demotions.sql
```

This file contains a `DO $$ … $$` block that re-checks:
- Schema columns present (catalog_state_code, archived_at).
- `certification_record.action_code` CHECK includes `demote_bf_catalog`.
- D408 invariant `remediate_bf_semantics=1392`.
- 1q-A baselines `admit_bf_catalog=1651` and `mark_bf_correction_required=30`.

On success, the file emits a `RAISE NOTICE` and commits. No row changes. If any assertion fails, the transaction aborts with an explicit `EXCEPTION` message naming the failed condition.

## 3. Apply (data only, after preconditions pass)

```sh
D408_APPLY=1 node bc-core/scripts/d408-demote-bf-catalog-state-1q-b.mjs --apply
```

Either guard alone leaves the script in dry-run. The script logs its mode in the first 6 lines of output.

### 3.1 Mid-apply progress

The script writes progress every 100 rows. Expected sequence:

```
Mode: APPLY (both --apply flag and D408_APPLY=1 present). DB WRITES WILL OCCUR.
[baseline] {"rbs_total":1392,"admit_total":1651,...}
…plan stats…
── APPLY mode — writing to database ──
Applied: 100/374
Applied: 200/374
Applied: 300/374
Apply complete: 374 rows demoted; 0 skipped (not candidate_import); 0 skipped (prior demote ledger exists).
```

Skip counts > 0 on a first-time apply are a warning sign — investigate.

### 3.2 Post-apply state

```sql
SELECT catalog_state_code, COUNT(*)
  FROM contract.business_field
 GROUP BY catalog_state_code
 ORDER BY catalog_state_code;
```

Expected:

| `catalog_state_code` | Count |
|---|---:|
| `candidate_import` | **5,007** (= 5,381 − 374) |
| `certified_catalog` | 1,651 |
| `correction_required` | 30 |
| `demoted_catalog` | **374** |
| `recertify_pending` | 0 |
| **Total** | **7,062** |

```sql
SELECT action_code, COUNT(*)
  FROM contract.certification_record
 WHERE primitive_type='business_field'
 GROUP BY action_code
 ORDER BY action_code;
```

Expected (delta from 1q-A baseline):

| `action_code` | Count |
|---|---:|
| `admit_bf_catalog` | 1,651 (unchanged) |
| `mark_bf_correction_required` | 30 (unchanged) |
| `demote_bf_catalog` | **374** (this DBCP) |
| `remediate_bf_semantics` | 1,392 (invariant) |
| Other historical action codes | (unchanged) |

```sql
-- Every demoted BF carries archived_at NOT NULL + certification_record_id NOT NULL
SELECT COUNT(*) FROM contract.business_field
 WHERE catalog_state_code='demoted_catalog'
   AND (archived_at IS NULL OR certification_record_id IS NULL);
-- Expected: 0
```

```sql
-- Every demoted BF has a paired demote_bf_catalog ledger row with the audit_run_uid
SELECT COUNT(*) FROM contract.certification_record
 WHERE primitive_type='business_field'
   AND action_code='demote_bf_catalog'
   AND gate_results_json->>'audit_run_uid' = 'audit-2026-05-16T08-32-46-736Z';
-- Expected: 374
```

```sql
-- Reason-code distribution among demoted rows
SELECT catalog_state_reason_code, COUNT(*)
  FROM contract.business_field
 WHERE catalog_state_code='demoted_catalog'
 GROUP BY catalog_state_reason_code
 ORDER BY COUNT(*) DESC;
```

Expected reason codes (from cohort logic):
- `broken_fallback_definition` — the bulk of the 374 (P3 rows that failed G1 via banned_template + all P4 rows).
- `definition_too_short` — the small subset of P3 rows that failed G1 via `definition_too_short` rather than `banned_template`.

### 3.3 Out-of-bounds (no spillover)

```sql
-- These counts MUST equal §1.2 baselines (no change)
SELECT 'business_field' AS tbl, COUNT(*) FROM contract.business_field
UNION ALL SELECT 'canonical_field',       COUNT(*) FROM contract.canonical_field
UNION ALL SELECT 'metric_contract',       COUNT(*) FROM contract.metric_contract
UNION ALL SELECT 'cc_field_mapping',      COUNT(*) FROM contract.cc_field_mapping
UNION ALL SELECT 'business_object_field', COUNT(*) FROM contract.business_object_field
UNION ALL SELECT 'business_field_alias',  COUNT(*) FROM contract.business_field_alias;
```

All counts unchanged. `certification_record` increased by exactly 374 (delta = new demote rows).

### 3.4 Tenant scope

**No tenant DB is touched.** Confirm `DATABASE_URL` points to the platform DB (`bc_platform_dev` on dev, staging/prod platform equivalents). The script reads only `DATABASE_URL` — it has no awareness of `TENANT_DATABASE_URL`.

## 4. Spot checks

### 4.1 Sample P3 row

```sql
SELECT b.name, b.catalog_state_code, b.catalog_state_reason_code,
       LEFT(b.catalog_state_reason_text, 100) AS reason_snippet,
       b.archived_at IS NOT NULL AS archived,
       cr.action_code, cr.gate_results_json->>'cohort' AS cohort
  FROM contract.business_field b
  JOIN contract.certification_record cr ON cr.certification_record_id = b.certification_record_id
 WHERE b.catalog_state_code = 'demoted_catalog'
   AND cr.gate_results_json->>'cohort' = 'P3'
 LIMIT 5;
-- Expected: 5 rows, all with archived=true, action_code='demote_bf_catalog', cohort='P3'.
```

### 4.2 Sample P4 row

```sql
SELECT b.name, b.catalog_state_code, b.catalog_state_reason_code,
       LEFT(b.catalog_state_reason_text, 100) AS reason_snippet,
       b.tier_estimate_if_any  -- pseudo; actual tier in gate_results_json
  FROM contract.business_field b
  JOIN contract.certification_record cr ON cr.certification_record_id = b.certification_record_id
 WHERE b.catalog_state_code = 'demoted_catalog'
   AND cr.gate_results_json->>'cohort' = 'P4'
 LIMIT 5;
-- Expected: 5 rows. P4 cohort is dominated by T0_only rows (no BO membership at all).
```

### 4.3 Confirm a known-good T4 BF was NOT touched

```sql
SELECT name, catalog_state_code, catalog_state_reason_code
  FROM contract.business_field
 WHERE name = 'actual_ledger_amount';
-- Expected: certified_catalog / legacy_hard_pass_grandfathered (untouched by 1q-B).
```

### 4.4 Confirm a known-good P0 BF (1q-A correction cohort) was NOT touched

```sql
SELECT name, catalog_state_code, catalog_state_reason_code
  FROM contract.business_field
 WHERE name = 'credit_type_code';
-- Expected: correction_required / broken_fallback_definition (untouched by 1q-B).
```

## 5. Rollback posture

Per ADR §6 / DBCP §8: **forward-only correction preferred; no destructive reverse SQL.** If 1q-B is applied in error, the operator does NOT delete certification_record rows or `UPDATE catalog_state_code` directly. Instead:

1. Identify the demote ledger rows by `gate_results_json->>'audit_run_uid' = 'audit-2026-05-16T08-32-46-736Z'`.
2. Author a paired re-admit script (or use the bc-admin review queue once GS-5 lands) that:
   - Inserts a `certification_record` row with `action_code='admit_bf_catalog'` or `'recertify_bf_catalog'`.
   - Updates `catalog_state_code` back to the prior value (typically `candidate_import`).
   - Clears `archived_at`.
3. The audit trail preserves both demotion and re-admit; demotion is **reversible by ledger action**, not by `DELETE` or `UPDATE` without a paired ledger row.

The `.revert.sql` for this DBCP is documentation-only and intentionally has no destructive SQL.

## 6. Promotion sequence

| Env | Step |
|---|---|
| dev | §1 pre-flight → §2 precondition SQL → §3 apply → §3.2–3.4 post checks → §4 spot checks. |
| | **Operator sign-off recorded in DevHub checkpoint on SES-8714df** before promoting to staging. |
| staging | §1 pre-flight → §2 → §3 → §3.2–3.4 → §4. **Sign-off recorded.** |
| prod | §1 pre-flight → §2 → §3 → §3.2–3.4 → §4. **Sign-off recorded.** |

After prod sign-off: file follow-on service-guard slices GS-1 through GS-5 (separate decisions); close TSK-9515d5 Phase 3 with references to DEC-1ce490, DBCP-1q-A (commit `513404d`), DBCP-1q-B (commit TBD), and the importer fallback fix (`186979d`).

## 7. Out of scope (explicit)

- No schema changes (DDL already shipped in 1q-A).
- No service-code change in this DBCP. Service-guard slices GS-1 through GS-5 follow separately.
- No bc-admin UI change.
- No tenant DB touched.
- No P0/P1/P2 row changed (those landed in 1q-A; this DBCP touches only `candidate_import` rows).
- No `correction_required` row changed.
- No `certified_catalog` row changed.
- No registered-abbreviation registry (separate ADR).
- No G3 LLM / G4 embedding (separate ADRs).
- No remediation endpoint call.
- No metric promotion. No metric_contract change.

## 8. References

- ADR: [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md)
- DBCP design: [2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md](2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md)
- DBCP-1q-A verification plan: [2026-05-16-d408-dbcp-1q-a-verification-plan.md](2026-05-16-d408-dbcp-1q-a-verification-plan.md)
- Fresh audit artifact: `bc-core/scripts/audit-output/d408-bf-admission-audit-calibrated-2026-05-16T08-32-46-736Z.{md,json,per-bf.jsonl}`
- 1q-A forward SQL: `bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-a-bf-catalog-admission-state.sql`
- 1q-B precondition SQL: `bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-b-bf-catalog-demotions.sql`
- Importer fallback fix: `bc-core@186979d`
- D162 (database rules): `bc-docs-v3/docs/adrs/ADR-1918d0.md`
