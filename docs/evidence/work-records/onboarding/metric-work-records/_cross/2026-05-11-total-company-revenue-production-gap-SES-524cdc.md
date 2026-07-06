---
uid: MWR-tcr-524cdc
title: total_company_revenue production-gap diagnosis (Apex)
description: Read-only Foundation-gated diagnosis of the 4 Apex MCs broken on `total_company_revenue`. Establishes that the gap is a platform-wide canonical_mapping + funnel-padding cluster, not a tenant-data issue or a one-line D330-R5 repair. Recommends defer; revisit with reporting-CC cluster build.
status: decision-pending
date: 2026-05-11
project: bc-core
domain: metric-platform
subdomain: production-expansion
focus: metric-readiness
tenant: apex
session_uid: SES-524cdc
related_adrs: [DEC-a4e550, DEC-bebaec, DEC-ebf0b4]
related_mwrs:
  - 2026-05-11-total-revenue-production-gap-SES-1c080e.md
  - 2026-05-11-operating-cash-flow-production-gap-SES-524cdc.md
---

# total_company_revenue — production-gap diagnosis (Apex)

## Why this arc

`total_company_revenue` was flagged in the apex formula-token audit as the next quick producing-count candidate after the operating_cash_flow defer: 4 broken MCs, all `null_in_tenant`. The hypothesis was that this could mirror the total_revenue Slice 1 pattern — a single `cc_field_mapping` pointing at a wrong-target BF on an otherwise-built CC, repairable in-place via D330-R5 for a quick +N producing uplift.

This MWR records the read-only registry diagnosis. **No writes were made.** A repair was NOT executed; the arc is recommended for defer for the reasons below.

## Baseline (read-only)

- **Apex readiness dial** (D394, 2026-05-11T12:57Z):
  - bound: 160
  - producing: 46
  - wouldProduceIfBound: 0
- **Catalog dial:** 376 MCs, 185 chainComplete, 360 formulaSupported, 175 ready.
- **Formula-token audit (apex):** 376 MCs | clean=38 | broken=338. Reason breakdown: 396 null_in_tenant / 134 type_mismatch / 2 no_mapping.
- **`total_company_revenue` rank:** position 10 in top-broken-CFs, null_tnt=4 / type_mm=0.

## MCs in scope (4)

| MC | Versions active | Variable role | Co-binding | Co-binding CF |
|----|-----------------|---------------|------------|---------------|
| `mc__recurring_revenue_pct` | 1.0.0, 1.1.0 | primary | `cc__actual_ledger` | `total_recurring_revenue` |
| `mc__revenue_concentration` | 1.0.0, 1.1.0 | primary | `cc__actual_ledger` | `revenue_from_top_customers` |
| `mc__revenue_per_employee` | 1.0.0 | primary | `cc__gaap_cash_flow` | `average_number_of_employees` |
| `mc__tax_department_cost_as_of_revenue` | 1.0.0, 1.1.0 | primary | `cc__actual_ledger` | `total_tax_function_cost` |

All four bind `cc__invoice_hdr` for `total_company_revenue` AND a co-binding for the other formula token.

## Registry diagnosis

### CF wiring (Location B/C — done)

`total_company_revenue` is wired:

- `canonical_field`: `field_name=total_company_revenue`, `function_code=finance`, `subfunction_code=accounts_payable` (← misclassified; semantic is revenue), `role=input`, `status_code=draft`.
- `cc_field_mapping`: one row only.
  - `cc__invoice_hdr` (finance / accounts_payable)
  - `business_field = invoice_hdr_total_amount`
  - `resolution_rule_code = sum`
  - `filter_json = NULL`, `compute_json = NULL`

### Source projection (Location C — gap)

The active `canonical_mapping_version` for `sap_ecc_ehp8-cc_invoice_hdr-mapping` (v1.2.0, active) lists 20 `field_resolutions` and 35 `unmapped_fields`. **`invoice_hdr_total_amount` is in the `unmapped_fields` array** — it is a known BF for `cc__invoice_hdr` but the source mapping does NOT project a `source_field_ref` to it. The `sap_s4hana_cloud-cc_invoice_hdr-mapping` (v1.0.0) has the same shape (invoice_hdr_total_amount unmapped; invoice_hdr_extended_amount mapped).

Consequence: every Apex (and every other sap_ecc_ehp8 / sap_s4hana_cloud) row projected through `cc__invoice_hdr` has `invoice_hdr_total_amount = NULL`. SUM over NULL yields NULL — Apex observes 4 null `total_company_revenue` formula tokens, which the audit classifies as `null_in_tenant`. The label is misleading: the root is a **platform-side unmapped BF**, not a tenant-data sparsity issue.

### Comparison: total_revenue (Slice 1, repaired)

`total_revenue` maps to the SAME `cc__invoice_hdr` CC, but via a different BF: `invoice_hdr_extended_amount` (sum). That BF IS in `field_resolutions` (source_field_ref = `invoice_hdr_extended_amount`). That is why total_revenue Slice 1 succeeded with a D330-R5 in-place mapping repair: the target BF was actually projected by the source mapping.

The naive D330-R5 candidate for total_company_revenue would be: swap `invoice_hdr_total_amount` → `invoice_hdr_extended_amount` on this `cc_field_mapping`. **This would violate Foundation Invariant #1 (Meaning once)**: `total_revenue` and `total_company_revenue` would both compute `SUM(invoice_hdr_extended_amount)` over the same projected rows, producing identical values from two CF names. That is funnel padding, not a semantic repair.

### Co-binding CFs (also broken)

The three GL-side co-bindings on `cc__actual_ledger` are themselves a funnel-padding cluster:

| CF | BF | Aggregation | filter_json |
|----|----|-------------|-------------|
| `total_recurring_revenue` | `actual_ledger_amount` | sum | NULL |
| `revenue_from_top_customers` | `actual_ledger_amount` | sum | NULL |
| `total_tax_function_cost` | `actual_ledger_amount` | sum | NULL |

All three SUM the same unfiltered `actual_ledger_amount` BF — three distinct "meanings" that would produce identical values (or NULL — the active `sap_ecc_ehp8-cc_actual_ledger-mapping` v1.2.0 does not include any of the three CF names; `actual_ledger_amount` would project, but the three CFs are semantically undifferentiated GL-amount sums without filter/compute predicates). Even if `total_company_revenue` were realized, three of the four MCs would still emit semantically meaningless values until the GL-side CFs receive proper chart-of-accounts filter_json.

The fourth (`mc__revenue_per_employee`) co-binds `cc__gaap_cash_flow`, which has **zero canonical_mapping rows** — the same unbuilt reporting CC blocked by the operating_cash_flow arc defer.

## Foundation Gate

Repair-location classification per the playbook:

- **Location A (source / SDG):** Possibly — if SAP VBRK actually carries a "total amount" field distinct from `NETWR`, the right fix may be to add a source-side projection for `invoice_hdr_total_amount`. Not verified in this read-only pass.
- **Location B (contract definition):** Yes — `total_company_revenue` is mis-categorized (subfunction=accounts_payable) and has no `compute_json`/`filter_json` to differentiate it from `total_revenue`. Semantic specification work is required.
- **Location C (canonical_mapping projection):** Yes — `invoice_hdr_total_amount` is in `unmapped_fields` for both source-system mappings; no source_field_ref exists.
- **Location D (engine):** No — engine handles SUM correctly; NULL handling is intentional.
- **Location E/F (storage / read model):** No — runtime correctly emits NULL when the projected BF is NULL.

**Design-From-Tenant-Data Guardrail:** The gap is platform-wide. `invoice_hdr_total_amount` is unmapped at the source-mapping level for every tenant on `sap_ecc_ehp8` and `sap_s4hana_cloud`, not just Apex. Any repair must be designed from the canonical contract semantics + source schema, NOT from "Apex shows NULL therefore patch the mapping." The Slice 1 total_revenue D330-R5 path is NOT applicable here without violating the Meaning-once invariant.

## Impact lens (read-only)

- **Apex MCs affected:** 4 (3 of them also blocked on undifferentiated GL co-bindings; 1 also blocked on unbuilt `cc__gaap_cash_flow`).
- **Producing uplift IF total_company_revenue alone were realized:** 0 — every MC has at least one other broken token.
- **Cross-tenant blast radius of any source-side mapping change:** every tenant bound to `sap_ecc_ehp8-cc_invoice_hdr-mapping` or `sap_s4hana_cloud-cc_invoice_hdr-mapping` (CCv1.1.0 / 1.2.0). Adding `invoice_hdr_total_amount` as a `field_resolution` is a CC-mapping bump (new mapping_version), requiring source-field discovery, change record, and re-emission.
- **Demo bearing:** none of these 4 MCs surfaces on the Apex CFO Pack demo tiles (verified against Section 13 of the demo-readiness triage). No demo-cycle win from repair.

## Recommendation — defer

This arc is **not** a quick producing-count candidate. Two paths exist; neither is a one-shot repair:

1. **Path 1 — proper semantic repair (defer).** Author a successor mapping version that adds `invoice_hdr_total_amount` to `field_resolutions` for both sap_ecc_ehp8 and sap_s4hana_cloud, AFTER confirming the SAP source field exists and differs semantically from `invoice_hdr_extended_amount`. Add `compute_json`/`filter_json` to the GL-side CFs (`total_recurring_revenue`, `revenue_from_top_customers`, `total_tax_function_cost`) so they are not undifferentiated SUM aliases. Build `cc__gaap_cash_flow` (blocked on the operating_cash_flow defer). **Estimated scope:** CC-mapping bump × 2 source systems + 3 CF compute_json edits + 1 reporting-CC build. Not a demo-cycle repair.

2. **Path 2 — naive D330-R5 alias-swap (rejected).** Swap `invoice_hdr_total_amount` → `invoice_hdr_extended_amount` on the `total_company_revenue` cc_field_mapping. Rejected on Foundation Invariant #1 grounds (Meaning once): would make total_company_revenue and total_revenue semantically identical, which is funnel padding.

3. **Path 3 — defer (recommended).** Record the diagnosis. Revisit when:
   - The reporting-CC cluster build is scheduled (this rolls up under the operating_cash_flow defer, which already noted the cluster-level scope).
   - The GL-side CFs receive proper compute/filter specs (Location B semantic work, not Apex-specific).
   - SAP source schema for invoice header "total amount" vs "extended amount" is verified.

### Decision (operator)

_Pending operator review._

## Hard constraints honored

- Read-only registry queries (canonical_field, cc_field_mapping, canonical_contract, canonical_mapping, canonical_mapping_version, metric_binding, business_field, formula-token audit, readiness dial).
- No writes to mapping, contract, schema, code, SDG, or runtime.
- No reader execution, no metric evaluation, no DB writes.
- No commits made; this MWR is uncommitted pending review.

## Followups (proposed, not filed)

- **Funnel-padding sweep** on `cc__actual_ledger` and `cc__invoice_hdr`: list every `cc_field_mapping` where multiple CFs map to the same BF with the same aggregation and NULL filter_json — these are platform-wide "meaning once" violations. Filed as a sweep task only if operator confirms.
- **CF subfunction reclassification:** `total_company_revenue` is tagged `accounts_payable`; should be `revenue_accounting` or `general_finance`. Cosmetic in isolation but a symptom of broader CF-catalog drift.
- **Top-broken-CF triage cadence:** the audit's top broken CFs (operating_cash_flow, total_payments_count, total_invoice_line_items_count, total_invoices_processed_count, total_journal_entry_line_items, total_debt) collectively account for ~40 broken token instances. Each warrants a similar read-only pass before any repair-or-defer decision; the pattern recurring across these is unmapped/funnel-padded canonical fields on otherwise-built CCs, not tenant-data sparsity.
