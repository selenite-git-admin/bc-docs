---
title: "D408 DBCP-1q-D verification plan — demote 14 no-CC type-incoherence rows"
date: 2026-05-17
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
plan: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md
sql_forward: bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-d-demote-no-cc-type-incoherence.sql
sql_revert: bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-d-demote-no-cc-type-incoherence.revert.sql
node_script: bc-core/scripts/d408-demote-correction-required-no-cc-1q-d.mjs
target_evidence: bc-core/scripts/audit-output/d408-1q-d-no-cc-type-incoherence-demotion-targets.json
session: SES-c5af8c
task: TSK-eae922
type: verification-plan
status: proposed
---

# DBCP-1q-D verification plan — demote 14 no-CC type-incoherence BFs

This DBCP carries out the **Path C** disposition of plan §11b sub-cohort **C1**: the 14 `correction_required` BFs with `catalog_state_reason_code='type_incoherence'`, zero `cc_field_mapping` references, and no SDA evidence are demoted via the existing `demote_bf_catalog` ledger action. No row in the asset_*_amount cohort, the iso row, or the 11 NEEDS_EVIDENCE definition cohort is touched.

## 1. Scope (locked from §11b)

- **In scope (14 rows):** commercial_invoice_line_×4, debit_transfer_×2, credit_transfer_×1, warranty_claim_×4, invoice_ledger_entry_hdr_×2, payment_status_payment_payment_status_amount.
- **Excluded by name:** `iso20022_camt_xchg_rate` (A2 hold), every `asset_*_amount` (A1 uplift path).
- **Excluded by predicate:** anything with `cc_field_mapping` count > 0, anything not in `correction_required`.
- **Untouched cohorts:** 11 NEEDS_EVIDENCE definition rows (§11a.2 track), all 5,007 `candidate_import`, all 1,651 `certified_catalog`, all 374 `demoted_catalog` already on disk.

The 14 targets are captured in `bc-core/scripts/audit-output/d408-1q-d-no-cc-type-incoherence-demotion-targets.json` (read-only snapshot, captured 2026-05-17).

## 2. Pre-apply checks

### 2.1 Filesystem

- `bc-core/scripts/audit-output/d408-1q-d-no-cc-type-incoherence-demotion-targets.json` exists and contains `"target_count": 14`, with every target row carrying `cc_count: 0` and a name not in `{iso20022_camt_xchg_rate}` and not matching `^asset_.+_amount$`.

### 2.2 DB baseline (must match exactly)

```sql
SELECT
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='remediate_bf_semantics') AS rbs,
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='admit_bf_catalog') AS admit,
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='mark_bf_correction_required') AS mark,
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='demote_bf_catalog') AS demote,
  (SELECT COUNT(*) FROM contract.certification_record WHERE action_code='recertify_bf_catalog') AS recertify,
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='candidate_import') AS cand,
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='certified_catalog') AS cert,
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='correction_required') AS corr,
  (SELECT COUNT(*) FROM contract.business_field WHERE catalog_state_code='demoted_catalog') AS demoted,
  (SELECT COUNT(*) FROM contract.business_field) AS bf_total;
```

Expected (baseline):

| key | expected |
|---|---:|
| rbs | 1,392 |
| admit | 1,651 |
| mark | 30 |
| demote | 374 |
| recertify | 0 |
| cand | 5,007 |
| cert | 1,651 |
| corr | 30 |
| demoted | 374 |
| bf_total | 7,062 |

### 2.3 Target enumeration cross-check (independent of evidence JSON)

```sql
SELECT COUNT(*) FROM contract.business_field bf
LEFT JOIN (SELECT business_field_id AS bf_id, COUNT(*) AS n
             FROM contract.cc_field_mapping GROUP BY business_field_id) c
  ON c.bf_id = bf.field_id
WHERE bf.catalog_state_code='correction_required'
  AND bf.catalog_state_reason_code='type_incoherence'
  AND COALESCE(c.n,0)=0
  AND bf.name <> 'iso20022_camt_xchg_rate'
  AND bf.name !~ '^asset_.+_amount$';
```

Expected: **14**.

If this SQL returns any other number, **halt**. Re-capture the target evidence JSON and resolve the divergence before proceeding.

## 3. Apply runbook

Strictly ordered. No step starts until the previous one closes clean.

| # | Step | Command | Expected outcome |
|---|---|---|---|
| 1 | Apply additive DDL + preconditions | `psql "$DATABASE_URL" -f bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-d-demote-no-cc-type-incoherence.sql` | `NOTICE: CHECK expanded: added type_incoherence_no_active_anchor.` (or `... No-op.` on re-apply). |
| 2 | Dry-run Node script | `node bc-core/scripts/d408-demote-correction-required-no-cc-1q-d.mjs` | "Dry-run summary: would demote 14 rows." No DB writes. |
| 3 | Apply via Node script | `D408_APPLY=1 node bc-core/scripts/d408-demote-correction-required-no-cc-1q-d.mjs --apply` | "Applied: 14. Skipped (not correction): 0. Skipped (already demoted): 0." |
| 4 | Post-apply baseline read | run the SQL from §2.2 | counts match the §4 post-apply table. |
| 5 | Spot check (§5) | run the SQL in §5 | every demoted row matches §5 expectations. |

If any step diverges from the expected outcome, **halt**. The Node script is idempotent; rerunning a partial apply is safe.

## 4. Post-apply expected counts

| key | baseline | expected post-apply | Δ |
|---|---:|---:|---:|
| rbs | 1,392 | 1,392 | 0 |
| admit | 1,651 | 1,651 | 0 |
| mark | 30 | 30 | 0 |
| demote | 374 | **388** | **+14** |
| recertify | 0 | 0 | 0 |
| cand | 5,007 | 5,007 | 0 |
| cert | 1,651 | 1,651 | 0 |
| corr | 30 | **16** | **−14** |
| demoted | 374 | **388** | **+14** |
| bf_total | 7,062 | 7,062 | 0 |
| canonical_field | 3,097 | 3,097 | 0 |
| metric_contract | 780 | 780 | 0 |
| tenant DB | n/a | untouched | — |

`recertify_bf_catalog` stays at 0 because the Path A uplifts have not been performed yet. `mark_bf_correction_required` stays at 30 because the original mark ledger rows are immutable (Invariant III).

## 5. Spot check (all 14 rows)

```sql
SELECT name,
       catalog_state_code,
       catalog_state_reason_code,
       (catalog_state_reason_text LIKE 'C1 (Path C, plan %11b)%') AS reason_text_ok,
       archived_at IS NOT NULL                AS archived_set,
       gate_signals_json ->> 'cohort'         AS cohort,
       gate_signals_json ->> 'dbcp'           AS dbcp,
       certification_record_id IS NOT NULL    AS cert_record_set
  FROM contract.business_field
 WHERE field_id IN (
   '019d704f-9214-70bd-9d99-1493a9b04e69','019d7042-c546-7a90-b99b-1bc8caf6bafa',
   '019d704f-2da9-77ec-9005-b27bbb9f5325','019d7042-8c40-7014-a627-e3a8ab9f811b',
   '019d7077-fb55-78e9-bad9-53adfd2520fe','019d707c-e2a9-7be0-9509-6813464bb297',
   '019d7081-b35f-7405-8347-812e3da7541f','019d708f-b72f-717f-822d-abe91f2ddf79',
   '019d708f-4822-70b2-8909-a8178d4c1bb2','019d70b2-3918-7a48-93ff-25dc6714ed5b',
   '019d701b-3503-77ee-8b73-17df528d86f0','019d702d-2952-7a21-b23d-53c24f2d7885',
   '019d701e-22f3-71bb-8521-f1eb444829db','019d701c-ea05-7e1b-9383-90206ee1a009'
 )
 ORDER BY name;
```

Expected for every row:
- `catalog_state_code = 'demoted_catalog'`
- `catalog_state_reason_code = 'type_incoherence_no_active_anchor'`
- `reason_text_ok = true`
- `archived_set = true`
- `cohort = 'C1'`
- `dbcp = '1q-D'`
- `cert_record_set = true`

Ledger spot check:

```sql
SELECT COUNT(*) FROM contract.certification_record
 WHERE primitive_type='business_field'
   AND action_code='demote_bf_catalog'
   AND (gate_results_json ->> 'cohort') = 'C1'
   AND (gate_results_json ->> 'dbcp')   = '1q-D';
```

Expected: **14**.

## 6. Out-of-scope assertion (must all return zero)

```sql
-- No asset_*_amount touched
SELECT COUNT(*) FROM contract.business_field
 WHERE name ~ '^asset_.+_amount$'
   AND catalog_reviewed_at >= '2026-05-17';
-- No iso row touched
SELECT COUNT(*) FROM contract.business_field
 WHERE name = 'iso20022_camt_xchg_rate'
   AND catalog_reviewed_at >= '2026-05-17';
-- No NEEDS_EVIDENCE definition row touched
SELECT COUNT(*) FROM contract.business_field
 WHERE catalog_state_reason_code IN ('definition_too_short','broken_fallback_definition')
   AND catalog_reviewed_at >= '2026-05-17';
-- No tenant DB touched (run against each tenant DB)
SELECT COUNT(*) FROM information_schema.tables WHERE table_name='business_field';
```

All four queries must return 0 (the last must return 0 because tenant DBs do not host `business_field` at all).

## 7. Rollback / re-admit posture

Per ADR §6 and the §11b discipline, demoted rows are restored via a **paired admit_bf_catalog / recertify_bf_catalog ledger action** — never by `DELETE`, never by `UPDATE catalog_state_code` without a paired ledger row. The reverse SQL file is documentation only; it contains the operator runbook for re-admission of an individual BF and the sketch for a bulk reverse Node script (not authored unless a real mistake is detected).

The CHECK enum addition (`type_incoherence_no_active_anchor`) is **forward-only** and is **not** dropped on reverse. Dropping the enum value would invalidate the demoted rows just written.

## 8. Linkages

- Plan §11b (locked): `bc-docs-v3@2d8a544` `../2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md`
- Active task: TSK-eae922 (D408 type corrections require SDA uplift before recertify)
- Pre-1q-D probes / halts:
  - Halted apply: `bc-core@8ff2a9f`
  - ISO single-row probe: `bc-core@a82a63b`
- Endpoints (unchanged this slice): `bc-core@9243984` (`correct-type`, `correct-definition`)
- Sibling DBCPs:
  - `1q-A` schema + backfill: `bc-core@513404d`
  - `1q-B` 374-row demotions: `bc-core@<1q-B commit>` (post-§11b path C precedent)
  - `1q-C` credit_type_code mapping removal: `bc-core@<1q-C commit>`
- Foundation invariants: `bc-docs-v3/docs/foundation/the-invariants.md` — this DBCP respects I (meaning evaluated once), II (object ordering), III (immutability — original mark ledger rows untouched), IV (explicit reference — paired ledger row per BF), V (non-replayable evaluation — fresh `catalog_review_run_uid`), VI (evidence emitted, not inferred — `gate_signals_json` snapshot per row).
