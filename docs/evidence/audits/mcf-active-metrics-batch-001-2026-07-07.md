---
title: MCF Active Metrics Audit - Batch 001
doc_type: evidence
domain: metrics
authority: audit-record
status: current
created: 2026-07-07
source_repo: C:\MyProjects\barecount-devhub
source_database: bc_platform_dev
source_schema: mcf
---

# MCF Active Metrics Audit - Batch 001

Date: 2026-07-07  
Mode: read-only audit  
Database: `bc_platform_dev`  
Schema: `mcf.*`

## Audit Parameters

- Source of truth: `mcf.metric_contract` joined to `mcf.metric_contract_version`.
- Active set: `metric_contract_version.governance_state_code = 'active'` and `metric_contract.archived_at IS NULL`.
- Batch selection: five most recently created active MCVs, ordered by `mcv.created_at DESC, mc.mc_name`.
- Scope: contract identity, formula shape, temporal gate, variable bindings, filter clauses, activation certification, PE-MC rows, self-verification, chain-status presence, seed-ledger linkage.
- Non-scope: runtime tenant snapshots and governed metric evaluation values.

## Corpus Snapshot

- `mcf.metric_contract_version`: 114 total versions, 108 active versions.
- `mcf.certification_record`: 122 `metric_create` draft records, 114 `metric_transition` active records.
- `mcf.mcv_chain_status`: 54 green and 28 amber rows in the table, but none for this batch.

## Batch Inventory

| Metric | MC UID | MCV UID | Function | Subfunction | Grain entity | Created UTC |
|---|---|---|---|---|---|---|
| `disputed_exposure_rate` | `edfbe0c7-29bd-442e-8340-1e851a589552` | `1c201242-b36e-4f8c-a7e3-0e796019509c` | finance | accounts_receivable | `e3963e45-ad13-4f6c-a1c3-fa56d8fd6446` | 2026-07-07 11:40:38 |
| `partially_paid_exposure_rate` | `d9443b69-d49c-467e-bb52-75464fb919fe` | `cdc056a3-ea73-4c32-af71-09d402530c8c` | finance | accounts_receivable | `e3963e45-ad13-4f6c-a1c3-fa56d8fd6446` | 2026-07-07 11:40:27 |
| `payables_settlement_rate` | `36f0d411-8732-41ba-89c2-8577f0d4887d` | `3ff390d2-aba5-4116-b611-73d9bc760a54` | finance | accounts_payable | `4471cb17-df9c-4e36-8d53-01a391c162ce` | 2026-07-07 11:40:03 |
| `discount_rate_on_sales` | `b150591d-0552-43c0-8973-ba5bc83b15bf` | `fed1dea5-23f9-4710-a31d-0ad35f2bc631` | finance | accounts_receivable | `e3963e45-ad13-4f6c-a1c3-fa56d8fd6446` | 2026-07-07 11:32:57 |
| `payables_discount_rate` | `c07654fe-65ff-477e-b48b-412a66c5e098` | `e3e63b13-c311-41be-9b3a-556f144dc9c1` | finance | accounts_payable | `4471cb17-df9c-4e36-8d53-01a391c162ce` | 2026-07-07 11:32:50 |

## Shape Summary

All five metrics are secondary percentage metrics:

- Formula pattern: `multiply(divide(numerator_metric_input, denominator_metric_input), 100)`.
- Temporal gate: `period_aggregate` with `{"period_type":"fiscal_period"}`.
- Variable bindings: exactly two `metric_input` bindings per metric.
- Snapshot selection: all upstream inputs use `period_matched`.
- Filter clauses: zero for all five metrics.
- Computed dimensions: not inspected in this batch because these metrics are simple secondary ratios with no filter clauses and no group-by evidence in the sampled contract shape.

## Upstream Inputs

| Metric | Numerator upstream | Denominator upstream | Upstream status |
|---|---|---|---|
| `discount_rate_on_sales` | `invoice_discount_amount` | `gross_invoiced_amount` | both active |
| `disputed_exposure_rate` | `disputed_invoice_amount` | `gross_invoiced_amount` | both active |
| `partially_paid_exposure_rate` | `partially_paid_invoice_amount` | `gross_invoiced_amount` | both active |
| `payables_discount_rate` | `payables_invoice_discount_amount` | `gross_payables_invoiced_amount` | both active |
| `payables_settlement_rate` | `paid_supplier_invoice_amount` | `gross_payables_invoiced_amount` | both active |

## Gate Evidence

- Panel verdict: all five have `APPROVE_FOR_DRAFT` in `metric_authoring_panel_run.consensus_payload_json`.
- Activation certification: all five have `metric_transition` certification records from `approved` to `active`.
- Self-verification: all five have one fixture and one result; all result verdicts are `pass`; no stale fixtures were observed.
- PE-MC: all five have 32 PE rows covering 16 distinct checks. Thirty rows are `PASS`; two rows are `PE-MC-8 = OPERATOR_REVIEW` for each metric. This matches the known deferred temporal-anchor review behavior, but the duplicate PE rows should be understood before treating row count as a unique-check count.
- Chain status: no `mcf.mcv_chain_status` rows were present for these five MCVs at audit time.
- Seed ledger: no `mcf.seed_metric` rows linked through `last_metric_contract_uid` or `last_metric_contract_version_uid` for these five MCVs.

## Findings

### Medium - Chain status missing for newest active metrics

The five sampled active MCVs have no rows in `mcf.mcv_chain_status`, even though the chain-status table contains 82 rows overall. These metrics are active and self-verified, but downstream chain readers that rely on `mcv_chain_status` will not see a green or amber verdict for them until the chain-status refresh runs.

### Medium - Seed-ledger back-pointers missing

No sampled metric is linked from `mcf.seed_metric.last_metric_contract_uid` or `last_metric_contract_version_uid`. If the onboarding queue or enrichment consumer expects seed-ledger provenance, these five active metrics are not consumable through that path yet.

### Low - PE-MC rows are duplicated per check

Each metric has 32 PE rows for 16 distinct PE-MC checks. The duplicate row pattern did not create contradictory verdicts, but consumers should aggregate by distinct `pe_check_code` and latest/effective certification evidence rather than raw row count.

### Info - Metric contract shapes look internally coherent

The sampled contracts are consistent with secondary ratio doctrine: both inputs are active upstream metrics, snapshot selection is `period_matched`, no source literals or filter clauses were found, formula shape is ratio times 100, and self-verification passed without stale fixtures.

## Follow-Up Queries

1. Refresh or inspect `mcf.mcv_chain_status` for the five MCVs above.
2. Backfill or reconcile `mcf.seed_metric` pointers if seed-ledger provenance is expected for active MCF metrics.
3. Confirm whether duplicate PE-MC rows are expected from re-evaluation before activation, or whether the effective row should be selected by certification/evaluated timestamp.
4. In the next batch, include runtime snapshot availability once contract-activation audit is complete.
