---
title: "D408 DBCP-1q-G verification plan — add admit_bf_from_correction_required action_code"
date: 2026-05-17
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
design: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-admit-from-correction-required-design-DEC-1ce490.md
plan: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md
sql_forward: bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-g-add-admit-from-correction-required-action.sql
sql_revert: bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-g-add-admit-from-correction-required-action.revert.sql
session: SES-c5af8c
task: TSK-eae922
precedent: DBCP-1q-D (additive CHECK enum expansion for catalog_state_reason_code)
type: verification-plan
status: proposed
---

# DBCP-1q-G verification plan — add `admit_bf_from_correction_required` action_code

Schema-only additive change. Adds a new value `admit_bf_from_correction_required` to the CHECK constraint on `contract.certification_record.action_code`. **No data rows are mutated. No business_field is touched. No ISO row is admitted. No service code is exercised.** The endpoint that will write rows with this action_code is implemented in a separate bc-core commit AFTER this DBCP applies (per design §9).

## 1. Scope (locked from the design)

- **In scope:** one `ALTER TABLE ... DROP CONSTRAINT ... ADD CONSTRAINT ...` pair against `contract.certification_record.action_code`, expanding the closed enum from 15 → 16 values.
- **Excluded:** any data rows, any other constraint, any other table, any tenant DB, any endpoint call, any service code.

The new endpoint design is `POST /api/business-fields/:id/admit-from-correction-required` (`bc-docs-v3@2c457a8`); this DBCP adds the ledger vocabulary the endpoint will need at insert time.

## 2. Pre-apply checks

### 2.1 DB baseline (must match exactly)

```sql
SELECT
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='remediate_bf_semantics') AS rbs,        -- 1396
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='admit_bf_catalog') AS admit,            -- 1651
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='mark_bf_correction_required') AS mark,   -- 30
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='demote_bf_catalog') AS demote,           -- 388
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='recertify_bf_catalog') AS recertify,     -- 4
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='candidate_import') AS cand,             -- 5007
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='certified_catalog') AS cert,            -- 1655
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='correction_required') AS corr,          -- 12
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='demoted_catalog') AS demoted,           -- 388
  (SELECT COUNT(*) FROM contract.business_field) AS bf_total,                                                     -- 7062
  (SELECT COUNT(*) FROM contract.canonical_field) AS cf_total,                                                    -- 3097
  (SELECT COUNT(*) FROM contract.metric_contract) AS mc_total,                                                    -- 780
  (SELECT COUNT(*) FROM contract.cc_field_mapping) AS cfm_total;                                                  -- 1603
```

### 2.2 Constraint presence

```sql
SELECT pg_get_constraintdef(oid)
  FROM pg_constraint
 WHERE conrelid='contract.certification_record'::regclass
   AND conname='certification_record_action_code_chk';
```

Expected: exactly one row whose `def` contains 15 string literals matching the prior enum (no `admit_bf_from_correction_required`). The forward SQL re-asserts this implicitly via the `v_have_chk` check.

### 2.3 Defence-in-depth — no row uses the new value yet

```sql
SELECT COUNT(*) FROM contract.certification_record
 WHERE action_code='admit_bf_from_correction_required';
```

Expected: **0**. The forward SQL re-asserts this and aborts with RAISE EXCEPTION if non-zero.

## 3. Apply runbook

| # | Step | Command | Expected outcome |
|---|---|---|---|
| 1 | Apply forward SQL | `docker exec -i bc-postgres-redesign psql -U barecount -d bc_platform_dev -v ON_ERROR_STOP=1 < bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-g-add-admit-from-correction-required-action.sql` | `BEGIN` → `NOTICE: DBCP-1q-G CHECK expanded: added admit_bf_from_correction_required.` → `NOTICE: DBCP-1q-G preconditions + ALTER + post-check OK.` → `DO` → `COMMIT`. On re-apply (idempotency): `NOTICE: DBCP-1q-G CHECK already extended: admit_bf_from_correction_required present. No-op.` |
| 2 | Verify CHECK now lists 16 values including the new one | `SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='contract.certification_record'::regclass AND conname='certification_record_action_code_chk';` | Output contains `admit_bf_from_correction_required` plus all 15 prior values. |
| 3 | Verify zero row mutation | run §2.1 baseline SQL again | identical to pre-apply (all 13 keys unchanged). |
| 4 | Verify no spurious row insert | `SELECT COUNT(*) FROM contract.certification_record WHERE action_code='admit_bf_from_correction_required';` | **0** (DBCP is schema-only). |

If any step diverges, **halt** and inspect.

## 4. Post-apply expected counts

| key | baseline | expected post-apply | Δ |
|---|---:|---:|---:|
| rbs | 1,396 | 1,396 | 0 |
| admit | 1,651 | 1,651 | 0 |
| mark | 30 | 30 | 0 |
| demote | 388 | 388 | 0 |
| recertify | 4 | 4 | 0 |
| cand | 5,007 | 5,007 | 0 |
| cert | 1,655 | 1,655 | 0 |
| corr | 12 | 12 | 0 |
| demoted | 388 | 388 | 0 |
| bf_total | 7,062 | 7,062 | 0 |
| canonical_field | 3,097 | 3,097 | 0 |
| metric_contract | 780 | 780 | 0 |
| cc_field_mapping | 1,603 | 1,603 | 0 |
| `admit_bf_from_correction_required` ledger rows | 0 | **0** (no row write by 1q-G) | 0 |
| Distinct `action_code` values now allowed by CHECK | 15 | **16** | +1 |

**This DBCP changes exactly one thing: the CHECK constraint definition. No data row is inserted, updated, or deleted. The ISO row is NOT admitted by this DBCP.**

## 5. Reverse posture

`20260517-d408-dbcp-1q-g-add-admit-from-correction-required-action.revert.sql` restores the prior 15-value CHECK by DROP+ADD. It **refuses** to run if any `contract.certification_record` row uses `admit_bf_from_correction_required`. If such rows exist, the operator must either:

- supersede each row via the standard certification chain (preferred), then re-attempt the revert; or
- hard-DELETE them (out of scope — requires a separate operator decision and is outside the polymorphic-ledger immutability norm).

The revert is idempotent: re-running after a successful revert is a no-op (detects the value already absent).

The forward CHECK expansion is **additive** and forward-only in normal operation. Reverting it is an explicit operator action; the design assumes the endpoint will be implemented and used after this DBCP lands, so reverts are reserved for emergencies (e.g. mis-named action_code, ADR amendment that renames the action).

## 6. Out-of-scope assertion

The following are **NOT** changed by 1q-G:

| primitive | check |
|---|---|
| `contract.business_field` | row count = 7,062 unchanged; no column mutation |
| `contract.certification_record` | row count unchanged; no INSERT/UPDATE/DELETE |
| `contract.canonical_field` | row count = 3,097 unchanged |
| `contract.metric_contract` | row count = 780 unchanged |
| `contract.cc_field_mapping` | row count = 1,603 unchanged |
| ISO row `iso20022_camt_xchg_rate` | state identical to pre-1q-G (still `status_code='draft'`, `catalog_state_code='correction_required'`) |
| 11 NEEDS_EVIDENCE definition rows | untouched |
| 4 A1 BFs + 10 retained A1 mappings | untouched |
| 14 demoted (DBCP-1q-D) rows | untouched |
| 5,007 `candidate_import` rows | untouched |
| Tenant DBs (`tbc_apex_dev`, `tbc_sandbox1_dev`) | not connected to |

## 7. Service implementation — separate next step

`1q-G is schema-only and does not admit the ISO row.` The new endpoint
`POST /api/business-fields/:id/admit-from-correction-required` is implemented in a **separate bc-core commit** that lands AFTER `1q-G` applies. Per design §9, the rollout sequence is:

1. (this DBCP) — apply `1q-G` to extend CHECK enum.
2. Service implementation — `AdmitFromCorrectionRequiredDto`, service method `admitFromCorrectionRequired`, repo method `admitBfFromCorrectionRequiredWithAuditTx`, controller `@Post(':fieldId/admit-from-correction-required')`. Also extend `CERTIFICATION_ACTION_CODES_SET` in `bc-core/src/registry/semantic-definitions/certification-record.ts`.
3. Unit tests covering the 6 refusal paths (404, 422 status-code, 422 catalog-state, 422 archived, 409 cc-conflict, 422 gate-fail) + 1 happy path (mocked at repo level).
4. ISO-row probe script.
5. APPLY ISO row.
6. Reconcile plan §11b sub-cohort A2 disposition.

`1q-G` is the foundation step for that sequence: until it applies, the service code cannot insert ledger rows with the new action_code (the CHECK would refuse).

## 8. Linkages

- Design: `bc-docs-v3@2c457a8` `2026-05-17-d408-admit-from-correction-required-design-DEC-1ce490.md`
- Plan: `bc-docs-v3/.../2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md` (§11b sub-cohort A2)
- Halted apply that exposed the gap: `bc-core@397d9b3`
- A2 evidence packet: `bc-core@cea5695`
- Precedent: DBCP-1q-D (additive CHECK enum expansion for `catalog_state_reason_code`)
- Active task: TSK-eae922
- Foundation invariants: `bc-docs-v3/docs/foundation/the-invariants.md` — `1q-G` is a schema-only additive change; respects Invariants I–VI by not changing meaning, ordering, or any stored data.
