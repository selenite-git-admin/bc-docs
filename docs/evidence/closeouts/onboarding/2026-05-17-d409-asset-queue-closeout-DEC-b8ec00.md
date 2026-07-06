---
title: "D409 cc__asset queue closeout — wrong-domain handoff"
date: 2026-05-17
authority: DEC-b8ec00 (D409 — BF-BO Catalog Expansion Factory)
adr: bc-docs-v3/docs/adrs/ADR-b8ec00.md
sop: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md
modeling_policy: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-credit-facility-modeling-policy.md
predecessor_pilot: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-pilot-1-cc-credit-closeout-DEC-b8ec00.md
parent_decision: DEC-1ce490 (D408)
sessions:
  - SES-a887b5 (Asset Batch 1 classify)
  - SES-9be130 (Asset Batch 1 apply)
  - SES-fdb476 (Mega Drive 1 source-family review)
  - SES-c8ad05 (Mega Drive 1 apply, US-GAAP subset)
  - SES-92747b (Asset Batch 3 sublane triage)
  - SES-829c1c (this closeout)
type: closeout
status: closed
hands_off_to: future domain queues (asset-operations / derivatives / debt / opex / treasury / intangible / inventory)
---

# D409 — cc__asset queue closeout

Closes the D409 cc__asset queue. **No further apply from this thread.** The 27 wrong-domain rows hand off to future domain-CC queues, not to a DEMOTE bin.

---

## 1. Executive summary

The cc__asset queue moved from polluted A1 mappings to a clean status in five sessions:

- **DBCP-1q-E** (D408 cleanup) removed 45 bad A1 mismatch `cc_field_mapping` rows; **10 mappings were intentionally retained** as FIT/REVIEW/INSUFFICIENT_CONTEXT.
- **D409 resolved 9 of the 45 orphan CFs** through governed paths: 1 rebind to an existing certified BF + 8 mappings to 5 newly admitted US-GAAP-backed BFs.
- **27 wrong-domain rows separated from cc__asset** — these are valid business concepts that belong in sibling domain CCs (derivatives, treasury, opex, intangible, inventory, asset-operations), not in cc__asset's PP&E balance-sheet scope.
- **2 IFRS-only rows parked** pending cc__asset standards-scope decision.
- **5 other rows parked** as NEEDS_SOURCE / LOW_VALUE / collateral-context.
- **No direct SQL shortcuts.** Every state change went through a governed endpoint or an explicitly approved DBCP. Every batch ran pre/post invariant checks.

---

## 2. Starting point

D408 closeout (DEC-1ce490, SES-c5af8c) left the asset queue in this state:

- 45 A1 `cc_field_mapping` rows on cc__asset bound to the 4 A1 `asset_*_amount` BFs with verdict=MISMATCH. **DBCP-1q-E removed all 45.**
- 10 A1 mappings classified as FIT/REVIEW/INSUFFICIENT_CONTEXT (other A1 BFs or other CC bindings). **Retained untouched.**
- The 45 orphan CFs became the input to the D409 asset queue.

### 2.1 Session trail

| # | Session | Output | Commit |
|---:|---|---|---|
| 1 | SES-a887b5 | Asset Batch 1 classification (45 rows → 6 lanes) | bc-core@4b8d0d3 |
| 2 | SES-9be130 | Asset Batch 1 apply (4 READY rows: 1 rebind + 3 depreciation flow → new BF) | bc-core@617dc45 |
| 3 | SES-fdb476 | Mega Drive 1 source-family review (12 NEEDS_SOURCE rows → 7 READY) | bc-core@4897257 |
| 4 | SES-c8ad05 | Mega Drive 1 apply (US-GAAP subset: 4 BFs + 5 mappings; IFRS excluded) | bc-core@9340bb5 |
| 5 | SES-92747b | Asset Batch 3 sublane triage (27 model-conflict rows → wrong-domain) | bc-core@fab51e3 |
| 6 | SES-829c1c | This closeout | bc-docs-v3 (this file) |

---

## 3. Resolved cc__asset mappings (9)

All inserted via `POST /api/onboarding/cc/:contractId/field-mappings` with `resolution_rule_code='sum'`. The two batches were verified end-to-end with per-mapping DB read-back.

### 3.1 Batch 1 apply (4 mappings, 1 new BF)

| CF | Target BF | filter_json |
|---|---|---|
| `asset_carrying_amount` | `asset_net_book_value_amount` (existing) | NULL |
| `annual_depreciation_expense` | `asset_depreciation_expense_amount` (new) | `{"period_basis":"annual"}` |
| `depreciation_expense` | `asset_depreciation_expense_amount` (new) | NULL |
| `total_depreciation_expense_for_period` | `asset_depreciation_expense_amount` (new) | `{"period_basis":"period_total"}` |

### 3.2 Mega Drive 1 apply (5 mappings, 4 new BFs)

| CF | Target BF | filter_json |
|---|---|---|
| `total_value_of_fixed_assets_written_off` | `asset_write_off_amount` (new) | NULL |
| `gross_value_of_disposed_assets` | `asset_disposition_gross_amount` (new) | NULL |
| `total_estimated_asset_retirement_obligations` | `asset_retirement_obligation_amount` (new) | `{"measurement_basis":"present_value"}` |
| `expected_future_cost` | `asset_retirement_obligation_amount` (new) | `{"measurement_basis":"undiscounted_future_cost"}` |
| `total_capital_investment` | `capital_expenditure_amount` (new) | `{"asset_category":"aggregate_fixed_intangible_r_and_d"}` |

---

## 4. New BFs admitted in the asset queue (5)

All admitted via the standing `POST /api/business-fields/:id/admit-from-candidate-import` endpoint with full SDA evidence and `action_code='admit_bf_from_candidate_import'`. All in `certified_catalog`, `definition_standard='US_GAAP'`, `semantic_family='measure-currency'`, `representation_term='Amount'`, `data_type='number'`, `unit_type_code='currency'`.

| BF | Standards anchor |
|---|---|
| `asset_depreciation_expense_amount` | `us-gaap:Depreciation` (ASC 360-10-35-4) |
| `asset_write_off_amount` | ASC 360-10-40 Derecognition |
| `asset_disposition_gross_amount` | ASC 360-10-40 Derecognition |
| `asset_retirement_obligation_amount` | `us-gaap:AssetRetirementObligation` (ASC 410-20) |
| `capital_expenditure_amount` | `us-gaap:PaymentsToAcquirePropertyPlantAndEquipment` (ASC 230) |

Per the D409 modeling policy v0.1 (generic-first), the ARO BF and the capex BF each carry a dimension filter at the `cc_field_mapping` level (`measurement_basis` and `asset_category` respectively) rather than spawning subtype-specific BFs.

---

## 5. Retained A1 mappings (10, untouched)

D408 DBCP-1q-E removed only the 45 MISMATCH rows. The 10 A1 mappings classified as FIT/REVIEW/INSUFFICIENT_CONTEXT were intentionally retained:

- **8 FIT** — strong-match cc_field_mapping rows where the (CC, CF, BF) binding was semantically correct.
- **1 REVIEW** — a row flagged as plausible-but-ambiguous; left pending operator judgement.
- **1 INSUFFICIENT_CONTEXT** — a row whose CF definition was too thin for the deterministic classifier to verdict; left pending operator-sourced clarification.

None of these were modified by the D409 asset queue. Future operator action may decide to revisit the REVIEW + INSUFFICIENT_CONTEXT rows when their semantic context is clearer.

---

## 6. Parked rows (34)

### 6.1 IFRS-only (2)

These rows proposed BFs whose standards-tier anchor is IFRS, not US-GAAP. Mega Drive 1 deliberately excluded them via a script-level `IFRS_FORBIDDEN_BFS` guard pending an operator decision on cc__asset's standards scope.

| CF | Proposed BF | IFRS anchor |
|---|---|---|
| `asset_recoverable_amount` | `asset_recoverable_amount` | IAS 36.18 (impairment recoverable amount) |
| `revalued_amount` | `asset_revalued_amount` | IAS 16.31 (revaluation model) |

**Action when cc__asset's standards scope is settled:** if IFRS is in scope, admit both via the standing factory chain; if US-GAAP-only, route to a sibling IFRS-scoped CC.

### 6.2 Various parked from Mega Drive 1 (5)

| CF | Lane | Reason |
|---|---|---|
| `asset_appraised_value` | PARKED_MODEL_CONFLICT | Definition reads "collateral securing the loan" — loan-underwriting context, not PP&E |
| `fair_market_value_of_assets` | PARKED_NEEDS_SOURCE | ASC 820 is a *measurement framework*, not a line-item anchor |
| `total_asset_replacement_value` | PARKED_NEEDS_SOURCE | Replacement cost is a separate valuation concept; no US-GAAP reporting element |
| `actual_value_generated_from_capex` | PARKED_LOW_VALUE_OR_NOISE | ROIC KPI; no standards anchor |
| `value_generated_from_capex_projects` | PARKED_LOW_VALUE_OR_NOISE | ROIC KPI; no standards anchor |

### 6.3 Wrong-domain (27, from Asset Batch 3)

See §7 for the full handoff.

---

## 7. Wrong-domain handoff

**These 27 rows are not garbage.** They are valid business concepts that landed in cc__asset because A1 was the polluted MISMATCH origin. They belong in sibling domain CCs that do not exist yet (or are out of D409's current scope). Demoting them as non-business would lose real catalog value.

Sublane → destination domain hint (from `bc-core/scripts/audit-output/d409-asset-model-conflict-sublane-packet-2026-05-17.md`):

### 7.1 Asset-operations / audit (14 rows) — `cc__asset_operations` or similar

Count-of-assets and operational-hour metrics. Valid as operations KPIs; out of scope for PP&E reporting balance-sheet.

- `accurate_asset_records_count`
- `number_of_accurate_asset_records`
- `number_of_assets_in_register`
- `number_of_fixed_assets`
- `number_of_periods`
- `total_asset_data_records_reviewed`
- `total_asset_records_audited`
- `total_fixed_asset_records_audited`
- `total_number_of_asset_activities`
- `total_number_of_assets`
- `total_number_of_disposed_assets`
- `total_number_of_financial_asset_activities`
- `total_physical_assets_identified`
- `total_scheduled_operational_hours`

### 7.2 Derivatives / hedge accounting (4 rows) — `cc__derivatives` (ASC 815)

Hedge fair-value, sensitivity, swap-leg present values. Valid derivatives concepts; ASC 815 territory.

- `change_in_value_of_hedge`
- `net_interest_expense_sensitivity_per_bp`
- `present_value_fixed_leg`
- `present_value_variable_leg`

### 7.3 Debt / capital structure (3 rows) — `cc__debt` or `cc__capital_structure`

Debt-side balances and cost-of-capital rates. Valid concepts; liability side of the balance sheet or weighted-average-cost-of-capital inputs.

- `net_debt_balance`
- `cost_of_debt`
- `cost_of_equity`

### 7.4 Operating expense (2 rows) — `cc__operating_expense` or `cc__opex`

Operating expenditure for asset maintenance and treasury operations. Income-statement opex, not asset balance.

- `total_maintenance_cost`
- `total_cost_treasury_operations_management`

### 7.5 Valuation inputs / treasury (2 rows) — `cc__valuation_inputs` or similar

Discount-rate and reserve-ratio inputs. Used in IFRS impairment and risk-management calculations; not asset balances.

- `discount_rate`
- `desired_reserve_ratio`

### 7.6 Intangible asset (1 row) — `cc__intangible_asset` (ASC 350)

Amortization is the intangible-asset analog of depreciation. Distinct from PP&E.

- `amortization_expense`

### 7.7 Inventory (1 row) — `cc__inventory` (ASC 330)

Inventory is a current asset; ASC 330 governs it. Distinct from fixed assets (ASC 360).

- `inventory_value`

---

## 8. Final counters (verified read-only at closeout, 2026-05-17)

| Counter | Value | Notes |
|---|---:|---|
| `bf_total` | 7069 | +5 from D408 closeout (asset queue admitted 5 BFs) |
| `cf_total` | 3097 | unchanged |
| `mc_total` | 780 | unchanged |
| `cc_field_mapping_total` | 1616 | +13 from D408 closeout (4 cc__credit Pilot 1 + 9 cc__asset; 1q-E removed 45 + 1q-C removed 11 = -56; D408 work +43 = net +13 vs the very original) |
| `certified_catalog` | 1662 | +7 from D408 closeout (2 cc__credit + 5 cc__asset) |
| `candidate_import` | 5007 | unchanged net (create-then-admit on each new BF) |
| `correction_required` | 12 | unchanged |
| `demoted_catalog` | 388 | unchanged — **no asset row was demoted in D409** |
| `admit_bf_from_candidate_import` | 7 | +7 from D408 closeout (2 cc__credit + 5 cc__asset) |
| `admit_bf_from_correction_required` | 0 | unchanged |
| `rbs` | 1396 | unchanged |
| `admit` | 1651 | unchanged |
| `mark` | 30 | unchanged |
| `demote` | 388 | unchanged |
| `recertify` | 4 | unchanged |

Two notable deltas across both D409 pilot CCs (cc__credit + cc__asset):

- **`admit_bf_from_candidate_import`: 0 → 7**: the entire usage of this new D409 action_code has been operator-driven and gated.
- **`cc_field_mapping_total`: +13 from D408 closeout**: 4 cc__credit + 9 cc__asset rebinds.

---

## 9. Lessons learned

1. **Batch mode works.** Asset Batch 1 (45-row classify), Mega Drive 1 (12-row review), Asset Batch 3 (27-row sublane triage) each closed in one session per phase. Per-row sub-packets are not necessary at this scale.

2. **Parked rows must not block ready rows.** The IFRS exclusion via script-level `IFRS_FORBIDDEN_BFS` guard let the US-GAAP subset apply without operator delay; the IFRS rows wait their turn without holding up the 5 ready BFs.

3. **Wrong-domain classification is a valid outcome.** A row landing as PARKED_WRONG_DOMAIN is not a failure or a demote — it is a finding that the row belongs elsewhere. Mixing these into a DEMOTE bin would erase real catalog value.

4. **Generic-first modeling worked.** Three of the five new BFs (`asset_depreciation_expense_amount`, `asset_retirement_obligation_amount`, `capital_expenditure_amount`) carry their specialisation as a `cc_field_mapping.filter_json` dimension rather than spawning subtype-specific BFs. This kept the catalog small and faithful to the XBRL design pattern.

5. **Source-family lanes are productive.** Splitting the 12-row Mega Drive 1 into three families (impairment / ARO / capex) made the standards anchors immediately visible (ASC 360, ASC 410, ASC 230). The lane structure scales to future drives.

6. **Do not use DEMOTE language for valid-but-out-of-scope CF concepts.** The 27 wrong-domain rows are explicitly handed off to future domain queues, not demoted. The factory contract preserves their potential value.

7. **The factory's halt-on-first-failure contract is the safety net.** Every batch (Batch 1 apply, Mega Drive 1 apply) caught real failure modes (uppercase `piiClassification`, response wrapping, IFRS leak) before any DB write. The discipline is operationally valuable, not ceremonial.

---

## 10. Next recommended D409 domain

Four candidate next moves:

- **A. Finish cc__credit residuals.** 6 NEEDS_EVIDENCE + 1 HOLD remaining on cc__credit. Operator-decision work; the factory machinery is in place to apply outcomes when decisions land.
- **B. Open the asset-operations / audit destination queue.** 14 wrong-domain rows from §7.1 land cleanly once `cc__asset_operations` (or equivalent) is authored. Largest single drop.
- **C. Open the intangible-asset queue.** 1 wrong-domain row (amortization_expense) + intangible-asset modeling work; opens a parallel domain to the asset queue and exercises the `intangible_asset_amortization_expense_amount` BF pattern that's already drafted in the Mega Drive 1 packet for Family A.
- **D. Open the derivatives / hedge-accounting queue.** 4 wrong-domain rows; ASC 815 territory; high-complexity but high-value.

**Recommendation: (C) Intangible-asset queue.** Reasoning:

- Smallest scope to test the next domain-CC pattern end-to-end (one new CC + one new BF generic + one rebind).
- The pattern is directly transferable to (B) and (D) afterwards.
- Exercises the case where amortization is the intangible-asset analog of depreciation — a clean parallel to cc__asset's work that closes a referenced thread from the Mega Drive 1 packet.
- (A) is operator-decision-paced; the factory waits.

Sequence after (C): (B) → (A) interleaved → (D) when the operator has bandwidth for derivatives complexity.

---

## 11. References

- [ADR-b8ec00](../../../governance/adrs/ADR-b8ec00.md) — DEC-b8ec00 (D409)
- [D409 SOP v0.1](../../work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md)
- [D409 modeling policy v0.1](../../work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-credit-facility-modeling-policy.md)
- [D409 admit-from-candidate-import design v0.1](../../work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-admit-from-candidate-import-design-DEC-b8ec00.md)
- [D409 Pilot 1 (cc__credit) closeout](2026-05-17-d409-pilot-1-cc-credit-closeout-DEC-b8ec00.md) — sibling closeout
- `Asset Batch 1 classification packet`
- `Mega Drive 1 source-family packet`
- `Mega Drive 1 apply artifacts`
- `Asset Batch 3 sublane triage packet`
- [D408 correction_required closeout](2026-05-17-d408-correction-cleanup-closeout-DEC-1ce490.md) — parent

### Changelog

| Version | Date | Note |
|---|---|---|
| 1.0 | 2026-05-17 | Initial closeout (SES-829c1c). cc__asset queue closed on the factory side; 9 mappings restored; 27 wrong-domain rows handed off without demote; 2 IFRS rows parked pending standards-scope decision. |
