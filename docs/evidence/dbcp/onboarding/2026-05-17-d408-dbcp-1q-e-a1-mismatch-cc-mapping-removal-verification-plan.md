---
title: "D408 DBCP-1q-E verification plan — remove 45 A1 MISMATCH cc_field_mapping rows"
date: 2026-05-17
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
plan: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md
sql_forward: bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-e-remove-a1-mismatch-cc-mappings.sql
sql_revert: bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-e-remove-a1-mismatch-cc-mappings.revert.sql
node_script: bc-core/scripts/d408-remove-a1-mismatch-cc-mappings-1q-e.mjs
target_evidence: bc-core/scripts/audit-output/d408-1q-e-a1-mismatch-cc-mapping-targets.json
audit_packet: bc-core/scripts/audit-output/d408-a1-asset-cf-binding-audit-packet-2026-05-17.md
session: SES-c5af8c
task: TSK-eae922
precedent: DBCP-1q-C (credit_type_code mapping removal)
type: verification-plan
status: proposed
---

# DBCP-1q-E verification plan — remove 45 A1 MISMATCH cc_field_mapping rows

Removes the 45 `cc_field_mapping` rows on `cc__asset` that bind to the 4 corrected A1 `asset_*_amount` BFs and that the deterministic A1 audit classifier (bc-core@752d66b) flagged **MISMATCH** (unit-type contradiction or strong-mismatch name pattern). The 10 `cc_field_mapping` rows that the audit classified `FIT` / `REVIEW` / `INSUFFICIENT_CONTEXT` are explicitly excluded.

## 1. Scope (locked from the audit packet)

- **In scope (45 rows):**
  - `asset_net_book_value_amount`: 34
  - `asset_cost_amount`: 8
  - `asset_accumulated_depreciation_amount`: 3
  - `asset_salvage_value_amount`: 0 (no MISMATCH; row not in 1q-E)
- **Excluded by classifier verdict:** every `FIT` (8), `REVIEW` (1), `INSUFFICIENT_CONTEXT` (1) row — see audit packet §"FIT / REVIEW / INSUFFICIENT_CONTEXT" lists.
- **Excluded by topic:** ISO row (`iso20022_camt_xchg_rate`), 11 NEEDS_EVIDENCE definition rows, 14 demoted rows (DBCP-1q-D).

The 45 targets are captured in `bc-core/scripts/audit-output/d408-1q-e-a1-mismatch-cc-mapping-targets.json` (read-only snapshot, captured 2026-05-17). The full reverse data (mapping_id + FKs + resolution_rule_code + filter_json + compute_json + created_at) is preserved there and inlined verbatim into the reverse SQL.

## 2. Pre-apply checks

### 2.1 Filesystem

- `bc-core/scripts/audit-output/d408-1q-e-a1-mismatch-cc-mapping-targets.json` exists with `"target_count": 45`, `predicate.audit_packet_verdict='MISMATCH'`, and every target has `classifier_verdict='MISMATCH'` and `business_field_name ∈ {4 A1 BFs}`.

### 2.2 DB baseline (must match exactly)

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
  (SELECT COUNT(*) FROM contract.cc_field_mapping m
     JOIN contract.business_field bf ON bf.field_id=m.business_field_id
    WHERE bf.name IN ('asset_net_book_value_amount','asset_cost_amount',
                      'asset_accumulated_depreciation_amount','asset_salvage_value_amount')) AS a1_bindings;     -- 55
```

### 2.3 SQL target enumeration cross-check (independent of evidence JSON)

The forward SQL marker file re-derives a MISMATCH lower bound from CF.unit_type_code ∈ `{count, percentage, ratio, days, hours, minutes, seconds}` ∪ a hard-listed set of currency-unit-but-semantically-wrong CF names. Expected count: **45**. If this query returns any other number, **halt**; re-run `build-d408-a1-asset-cf-binding-audit-packet.mjs` and re-derive the target evidence JSON.

## 3. Apply runbook

Strictly ordered. No step starts until the previous one closes clean.

| # | Step | Command | Expected outcome |
|---|---|---|---|
| 1 | Apply forward SQL preconditions | `psql "$DATABASE_URL" -f bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-e-remove-a1-mismatch-cc-mappings.sql` | `NOTICE: DBCP-1q-E preconditions OK.` (or `RAISE EXCEPTION` if any baseline / target count diverged). |
| 2 | Dry-run Node script | `node bc-core/scripts/d408-remove-a1-mismatch-cc-mappings-1q-e.mjs` | "Dry-run plan: would DELETE 45 cc_field_mapping rows on cc__asset." No DB writes. |
| 3 | Apply via Node script | `D408_APPLY=1 node bc-core/scripts/d408-remove-a1-mismatch-cc-mappings-1q-e.mjs --apply` | "removed 45 rows" inside a single transaction with CTE-bounded pre/post checks. |
| 4 | Post-apply baseline read | run §2.2 SQL | counts match the §4 post-apply table. |
| 5 | Per-BF spot check | run §5 SQL | each BF's binding count drops by the expected per-BF delta. |

If any step diverges from the expected outcome, **halt**. The Node script's allow-list is naturally idempotent: re-running after a successful apply finds 0 matching rows and refuses with `live rows 0 != targets 45`.

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
| a1_bindings | 55 | **10** | **−45** |
| tenant DB | n/a | untouched | — |

The certification ledger is **not** advanced — `cc_field_mapping` is not a `primitive_type` recognised by `contract.certification_record` (see precedent in DBCP-1q-C). Governance evidence comes from the audit packet, the forward SQL preconditions, the target evidence JSON, and the apply script's audit JSONL.

## 5. Per-BF spot check (post-apply)

```sql
SELECT bf.name,
       COUNT(*)::int AS bindings
  FROM contract.cc_field_mapping m
  JOIN contract.business_field bf ON bf.field_id=m.business_field_id
 WHERE bf.name IN ('asset_net_book_value_amount','asset_cost_amount',
                   'asset_accumulated_depreciation_amount','asset_salvage_value_amount')
 GROUP BY bf.name
 ORDER BY bf.name;
```

Expected:

| BF | baseline | expected post | Δ |
|---|---:|---:|---:|
| `asset_accumulated_depreciation_amount` | 5 | 2 | −3 |
| `asset_cost_amount` | 10 | 2 | −8 |
| `asset_net_book_value_amount` | 39 | 5 | −34 |
| `asset_salvage_value_amount` | 1 | 1 | 0 |
| **total** | **55** | **10** | **−45** |

## 6. Exact list of 45 mappings (CF name per BF)

### 6.1 `asset_net_book_value_amount` — 34 removals

`accurate_asset_records_count`, `actual_value_generated_from_capex`, `amortization_expense`, `asset_appraised_value`, `change_in_value_of_hedge`, `desired_reserve_ratio`, `discount_rate`, `fair_market_value_of_assets`, `gross_value_of_disposed_assets`, `inventory_value`, `net_debt_balance`, `net_interest_expense_sensitivity_per_bp`, `number_of_accurate_asset_records`, `number_of_assets_in_register`, `number_of_fixed_assets`, `number_of_periods`, `present_value_fixed_leg`, `present_value_variable_leg`, `total_asset_data_records_reviewed`, `total_asset_records_audited`, `total_asset_replacement_value`, `total_capital_investment`, `total_estimated_asset_retirement_obligations`, `total_farm_asset_value`, `total_fixed_asset_records_audited`, `total_number_of_asset_activities`, `total_number_of_assets`, `total_number_of_disposed_assets`, `total_number_of_financial_asset_activities`, `total_physical_assets_identified`, `total_scheduled_operational_hours`, `total_value_of_fixed_assets_written_off`, `untaxed_transaction_value`, `value_generated_from_capex_projects`.

### 6.2 `asset_cost_amount` — 8 removals

`asset_carrying_amount`, `asset_recoverable_amount`, `cost_of_debt`, `cost_of_equity`, `expected_future_cost`, `revalued_amount`, `total_cost_treasury_operations_management`, `total_maintenance_cost`.

### 6.3 `asset_accumulated_depreciation_amount` — 3 removals

`annual_depreciation_expense`, `depreciation_expense`, `total_depreciation_expense_for_period`. _(P&L flow CFs flagged in Step B; need a separate `asset_depreciation_expense_amount` BF if re-binding is desired.)_

## 7. Out-of-scope assertions (FIT / REVIEW / INSUFFICIENT_CONTEXT rows excluded)

The following mappings are **NOT** removed by 1q-E. The Node script refuses to proceed if any of their `mapping_id`s appear in the target set (defence-in-depth from `loadPacketGuardSet()`).

| BF | excluded CF | classifier verdict |
|---|---|---|
| `asset_net_book_value_amount` | `book_value_of_assets` | FIT |
| `asset_net_book_value_amount` | `carrying_value_before_revaluation` | FIT |
| `asset_net_book_value_amount` | `total_book_value` | FIT |
| `asset_net_book_value_amount` | `asset_value` (or near term) | REVIEW |
| `asset_net_book_value_amount` | `total_asset_value` | INSUFFICIENT_CONTEXT (empty CF description) |
| `asset_cost_amount` | `asset_acquisition_cost` | FIT |
| `asset_cost_amount` | `initial_asset_cost` | FIT |
| `asset_accumulated_depreciation_amount` | `accumulated_depreciation` | FIT |
| `asset_accumulated_depreciation_amount` | `total_accumulated_depreciation` | FIT |
| `asset_salvage_value_amount` | `estimated_salvage_value_at_end_of_life` | FIT |

(Operators may revisit these later — REVIEW + INSUFFICIENT_CONTEXT especially — but the 1q-E DBCP does not touch them.)

## 8. Rollback / reverse posture

Reversal is **fully implemented** via `20260517-d408-dbcp-1q-e-remove-a1-mismatch-cc-mappings.revert.sql`. The reverse SQL:

- inlines all 45 rows verbatim (original `cc_field_mapping_id`, FKs, `resolution_rule_code`, `filter_json`/`compute_json` = NULL, original `created_at`);
- refuses to run if any of the 45 IDs already exist (no duplicate-key risk);
- post-checks that exactly 45 rows are reinserted before COMMIT.

Source of truth for the reinsert values: `bc-core/scripts/audit-output/d408-1q-e-a1-mismatch-cc-mapping-targets.json` (the same JSON the apply script uses for its allow-list). The reverse SQL was machine-generated from that JSON; the JSON should be preserved in git as long as 1q-E is potentially reversible.

A future ADR could extend the polymorphic ledger to cover `cc_field_mapping` mutations; until then, audit trail = audit packet + target JSON + apply script audit JSONL + this verification plan.

## 9. Hard boundaries observed by 1q-E

- Data-only. No DDL. No schema change. No CHECK enum change.
- No `business_field` mutation. No `canonical_field` mutation. No `certification_record` insert. No `metric_contract` / `metric_binding` change.
- No tenant DB connection.
- No endpoint invocation (`/correct-type`, `/correct-definition`, `/remediate-semantics` are not called).
- A1 D408 cohort: 4 asset rows remain `certified_catalog` with full `definition_standard='US_GAAP'` + `semantic_family='measure-currency'` + `unit_type_code='currency'` + cited `standard_ref`. The MISMATCH mappings are removed; the FIT mappings stay.

## 10. Linkages

- Audit packet: `bc-core@752d66b`
- Step C apply (uplift): `bc-core@1902d5d`
- Step D probe (1 row): `bc-core@c5cdb85`
- Step D remaining 3: `bc-core@b23122d`
- §11b sub-cohort A1 lock: `bc-docs-v3@2d8a544`
- Active task: TSK-eae922
- Precedent: DBCP-1q-C (`credit_type_code` mapping removal) — the only prior `cc_field_mapping` removal under D408; 1q-E follows the same shape but uses the SQL-marker + Node-apply split (like 1q-D) since the target set is operator-curated via the audit packet, not derivable from a static SQL predicate.
- Foundation invariants: `bc-docs-v3/docs/foundation/the-invariants.md` — 1q-E respects I (meaning evaluated once: the audit packet's classifier is the meaning), II (object ordering: BF→CF binding mutation only), III (immutability: certification_record rows for the 4 BFs unchanged), IV (explicit references: every removal cites a captured row in the target JSON), V (non-replayable: a fresh audit_run_uid would re-classify), VI (evidence emitted: the audit packet + target JSON + apply JSONL form the proof chain in lieu of a ledger row).
