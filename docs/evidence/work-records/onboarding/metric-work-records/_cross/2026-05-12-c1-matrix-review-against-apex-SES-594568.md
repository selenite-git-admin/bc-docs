---
metric: c1-matrix-review-against-apex
metric_version: n/a
tenant: apex
source_system: n/a
work_type: matrix-validation
session_uid: SES-594568
date: 2026-05-12
status: decision-pending
related_commits: []
related_tasks: []
related_adrs:
  - DEC-a17d0f
  - DEC-804874
related_mwrs:
  - 2026-05-12-c1-bf-cf-compatibility-amendment-draft-SES-594568.md
  - 2026-05-12-pool1-trust-audit-46-producing-SES-594568.md
  - 2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md
  - 2026-05-12-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md
related_change_records:
  - CHG-28ab0c
repair_location: B
affected_boundary: contract_authoring
foundation_gate: passed
---

# C1 §4 matrix + DBCP-1a metadata — validation against Apex Pool 1 evidence

> **Read-only validation.** Tests the C1 amendment draft's §4 compatibility matrix and DBCP-1a's `compatible_data_types` / `compatible_unit_types` seed against every `(BF, CF, rule)` triple observed in Apex's 46 producing MCs + 114 non-stale candidates (160 MCs, 246 distinct variable inputs). No filing, no schema execution. Output: confirmed cells, contested cells, refinements needed before C1 is filed.

## 0. Method and caveats

### Method

For each input variable of every audited MC: infer `BF.semantic_family` from the BF name + source-field, infer `CF.semantic_family` from the CF name, look up the C1 §4 matrix for the `(BF.family, CF.family, rule)` triple, and record the verdict (`accept` / `review` / `reject` / `ambiguous`).

Heuristic source rules (script: `C:/tmp/matrix-review.js`):
- BF inference uses `BF.field_name` + `source_field` (e.g. `GJAHR` → `dim-fiscal-period`; `KURSF` → `measure-ratio`; `WRBTR/NETWR/HWBET/HWBAS/KANSW/WTG001` → `measure-currency`).
- CF inference uses CF name tokens (`*_amount/*_balance/*_revenue/...` → `measure-currency`; `*_count/number_of_*` → `measure-count`; etc.).

### Caveats (read before acting)

1. **`rule` is partially observed.** The chain-detail trace surfaces `l2BfName` but not the cc_field_mapping rule for every variable; the rule is only fully captured for CFs that appear in G10 collision-groups. **125 of 246 inputs (51%) carry `rule = (no-rule)` in this scan**, meaning the matrix could not apply rule-specific verdicts to them. This is a **data-availability gap**, not a matrix gap. The matrix's structural verdict (which family-pairs are admissible at all) still applies; the rule-specific refinement does not.
2. **CF inference is heuristic, not authoritative.** 62 of 246 inputs (25%) failed CF-family inference (e.g. `total_credit_sales`, `weighted_average_common_shares_outstanding`, `total_subscribers_or_users` — names that don't match the heuristic token set). Apparent matrix verdicts on these are **ambiguous, not authoritative**.
3. **One-shot validation, not iterative.** The heuristic was authored before this run; cases that surface here as ambiguous would be cleaner with an iterated heuristic, but iteration risks circularity. The honest count of confidently-validated cells is what matters.
4. **Producing-and-flagged hits exist.** Several rows show matrix verdict `accept` AND an audit `D335_SUM_ON_LATEST` finding. The matrix passes them because the BF-CF type-shape is compatible; the rule-vs-formula mismatch is a separate gate (engine audit D335-R4) that runs orthogonally. **G11 is correct to pass these.** D335 is the right tool for that mismatch.

### Numbers from the run

| Verdict | Triple-types | Input-hits |
|---|---|---|
| **accept** | 3 distinct triples | **47** inputs |
| **review** | 0 distinct triples | 0 inputs |
| **reject** | 17 distinct triples | **136** inputs |
| **ambiguous (inference failed)** | 12 distinct triples | 63 inputs |
| **Total** | 32 | 246 |

**Caveat on the 86-hit "measure-currency BF + measure-currency CF + (no-rule)" cell:** it is shown as `reject` because the matrix requires a rule. With rule data present, those 86 cells would resolve to either `accept` (sum/latest) or `review` (count_*). They are **data-availability rejects, not structural rejects**.

## 1. Confirmed ACCEPT cells (matrix passes, Apex evidence agrees)

| Triple | Hits | Representative Apex evidence | Notes |
|---|---|---|---|
| `measure-currency BF + measure-currency CF + sum` | **41** | `mc__blocked_invoices_value`: `sum_of_all_blocked_invoices_value <- invoice_hdr_extended_amount (NETWR) | sum`; `mc__ar_to_sales_ratio`: `accounts_receivable_balance <- receivable_hdr_amount (WRBTR) | sum` | The dominant legitimate pattern: currency summed to a currency. **Confirmed accept-cell.** |
| `measure-currency BF + measure-count CF + count_where_not_null` | **5** | `mc__dispute_resolution_time`: `number_of_disputes_resolved <- receivable_hdr_amount (WRBTR) | count_where_not_null` | Counting rows where amount is non-null. Matrix says any BF + count_* → measure-count is accept. **Structurally correct, but see §3 review concern.** |
| `measure-currency BF + measure-currency CF + latest` | 1 | `mc__spread_yield_on_advances_minus_cost_of_deposits`: `yield_on_advances <- actual_ledger_amount (WRBTR) | latest` | Single accept; carries a D335_SUM_ON_LATEST finding from the formula-vs-rule audit (G11 still passes; the rule-mismatch is a separate D335 concern). |

**Confirmed-accept totals: 47 input-hits across 3 cells.** No matrix cell that the heuristic identified as accept produced an unsupported-by-evidence outcome.

## 2. Confirmed REJECT cells (matrix rejects, Apex evidence agrees)

Operator §5 non-overridable classes (from C1 acceptance):
- (a) measure ↔ temporal / dimension
- (b) amount/currency ↔ fiscal-year / date / period
- (c) exchange-rate-as-cost (measure-ratio → measure-currency)
- (d) ratio / percent / score used as raw sum amount

### Class (a) + (b) — fiscal-year-as-monetary-measure (the dominant Apex failure)

| Triple | Hits | Representative Apex evidence |
|---|---|---|
| `dim-fiscal-period BF + measure-currency CF + (no-rule)` | **10** | `mc__roa_return_on_assets`: `average_total_assets <- actual_ledger_fiscal_year (GJAHR)`; `mc__capital_expenditure_growth_rate`: `prior_period_capital_expenditures <- actual_ledger_fiscal_year (GJAHR)`; `mc__gross_margin_return_on_investment_gmroi`: `average_inventory_investment <- journal_entry_hdr_fiscal_year (GJAHR)` |
| `dim-fiscal-period BF + measure-currency CF + latest` | 5 | `mc__ar_turnover`: `average_accounts_receivable <- actual_ledger_fiscal_year (GJAHR) | latest`; `mc__total_asset_turnover`: `average_total_assets <- actual_ledger_fiscal_year (GJAHR) | latest`; `mc__total_asset_turnover_ratio`: same |
| `dim-fiscal-period BF + measure-currency CF + count_distinct` | 2 | `mc__accounts_receivable_turnover_ratio`: `average_accounts_receivable_balance <- receivable_hdr_fiscal_year (GJAHR) | count_distinct`; `mc__average_payment_days_apd`: same |
| `dim-fiscal-period BF + measure-currency CF + sum` | 1 | `mc__intercompany_reconciliation_aging`: `total_days_unreconciled_intercompany_balances <- receivable_hdr_fiscal_year (GJAHR) | sum` |
| `dim-fiscal-period BF + duration CF + sum/latest` | 2 | `mc__aged_dispute_count_30_plus_days`: `total_disputes_over_30_days <- receivable_hdr_fiscal_year (GJAHR) | sum`; `mc__liquidity_coverage_ratio`: `net_cash_outflows_30_days <- ... | latest` |
| `dim-fiscal-period BF + measure-percent CF + latest` | 1 | `mc__doubtful_debt_provision`: `estimated_uncollectible_percentage <- receivable_hdr_fiscal_year (GJAHR) | latest` |

**Class (a)+(b) total: 21 inputs across 6 triple-types.** Matrix rejects all of them. Operator §5 names them as non-overridable. **Confirmed.**

### Class (c) — exchange-rate-as-monetary-amount

| Triple | Hits | Representative Apex evidence |
|---|---|---|
| `measure-ratio BF + measure-currency CF + (no-rule)` | **10** | `mc__maintenance_cost_pct_of_asset_value`: `total_asset_value <- journal_entry_hdr_exchange_rate (KURSF)`; `mc__total_revenue_per_active_customer`: `total_business_entity_revenue <- ... KURSF`; `mc__finance_function_it_costs_allocated_to_decision_support`: `total_finance_function_it_costs <- ... KURSF` |

**Class (c) total: 10 inputs.** Matrix rejects. Operator §5 names as non-overridable. **Confirmed.**

### Class (d) — code-as-amount and other structural mismatches

| Triple | Hits | Representative Apex evidence |
|---|---|---|
| `code BF + measure-currency CF + (no-rule)` | 2 | `mc__budget_execution_rate`: `approved_budget_amount <- budget_ledger_hdr_status_code (STATUS)`; `mc__budget_utilization_rate`: `allocated_budget_amount <- ... STATUS` |
| `date BF + measure-count CF + (no-rule)` | 2 | `mc__capital_projects_completed_on_time`: `number_of_projects_completed_on_time <- journal_entry_hdr_last_modification_date_time (AEDAT)`; `mc__task_completion_by_deadline`: similar |

**Class (d) total: 4 inputs across 2 triples.** Matrix rejects. **Confirmed.**

### Other reject-cell hits (not in operator's named classes — surfaced separately for visibility)

| Triple | Hits | Note |
|---|---|---|
| `measure-currency BF + measure-count CF + (no-rule)` | 7 | E.g. `mc__average_invoice_processing_time`: `number_of_invoices_processed <- receivable_hdr_amount (WRBTR)`. **Matrix reject (no-rule).** With rule data this becomes accept if rule=count_*; but currently no rule is set. **Data gap, not matrix issue.** |
| `date BF + date CF + (no-rule)` | 4 | E.g. `mc__producing_monthly_flash_reports_*`: `monthly_consolidated_financial_statements_completion_date <- journal_entry_hdr_reversal_date`. **Matrix accepts date→date+latest, but rule=(no-rule) here. Data gap, not matrix issue.** |
| `date BF + duration CF + (no-rule)` | 1 | `mc__average_invoice_processing_time`: `total_processing_time_for_invoices <- receivable_hdr_last_modification_date_time`. **This is the balance-flow grammar gap** — duration derived from a date column needs the engine's temporal-arc grammar (D210 family). Out of G11 scope. |
| `code BF + measure-score CF + (no-rule)` | 1 | `mc__high_risk_ar_exposure`: `customer_credit_risk_rating <- credit_type_code (CTLPC)`. **This is Apex Case C.** Matrix REJECTs at the score-vs-code level (matrix entry for measure-score allows `code` BF only at `latest` rule, marked `review`; with no-rule it falls through to reject). **The deeper code-vocabulary mismatch is the G11b sub-gate (deferred).** |
| `measure-currency BF + measure-ratio CF + (no-rule)` | 1 | `mc__gross_margin_return_on_investment_gmroi`: `gross_margin <- actual_ledger_amount`. Reject is correct — ratio CF from currency BF doesn't compose. |
| `measure-ratio BF + measure-ratio CF + (no-rule)` | 1 | `mc__gmroi_gross_margin_return_on_investment`: `gross_margin_dollars <- journal_entry_hdr_exchange_rate (KURSF)`. **CF inference put `gross_margin_dollars` in `measure-ratio` (because name contains "margin"); the CF's true family is `measure-currency` (dollars). Reject is right by either reading — currency CF from KURSF is wrong.** |

**Confirmed-reject totals: 136 input-hits across 17 cells.** 35 of those are operator-named hard-reject classes; the remaining 101 split between data-availability rejects (rule missing) and a few structurally correct rejects on cases the matrix already handles.

## 3. Review / ambiguous cells — operator decision needed

### Review cell A — count_* rule on any BF is currently ACCEPT for measure-count CF

| Triple | Hits | Concern |
|---|---|---|
| `measure-currency BF + measure-count CF + count_where_not_null` (matrix says ACCEPT) | 5 | E.g. `number_of_disputes_resolved <- receivable_hdr_amount`. The matrix passes because counting rows-where-amount-is-non-null is a structurally valid operation. **But:** "presence of a non-null amount" is not the same as "presence of a dispute resolution event". This is **funnel-padding at the rule layer**: the count is mechanically correct but semantically substitutes "rows in this table" for "dispute resolutions". |

**Proposed matrix refinement:** downgrade `(any-BF + count_* → measure-count)` from ACCEPT to **REVIEW** when the BF is `measure-currency` or `measure-ratio`. The argument: counting rows of a financial measure (`receivable_hdr_amount`) to mean "number of disputes" is suspicious — the row count of an AR-detail table is a proxy that may or may not correspond to the business event. ACCEPT for `(identifier, count_distinct)` (a true distinct count of identifiers) and `(code, count_distinct)` (counting categorical values) remains correct. ACCEPT for `(any, count_*)` is currently too permissive.

**Pre-filing change to C1 §4.2 — the `measure-count` row:**

```
Before:
  measure-count: (any BF.family, count_distinct/count_where_not_null) accept;
                 (measure-count, sum/latest) accept

After:
  measure-count: (identifier|code|name|text|measure-count, count_distinct/count_where_not_null) accept;
                 (measure-currency|measure-ratio|measure-percent|measure-score, count_distinct/count_where_not_null) review (overridable with rationale; counting a measure column's row-presence rarely matches the named CF concept);
                 (date|datetime|period|dim-*, count_distinct/count_where_not_null) review;
                 (measure-count, sum/latest) accept
```

This is a real-world tightening, traceable to Apex evidence.

### Review cell B — code-vocabulary deferred to G11b is correctly identified

The single `code BF + measure-score CF` hit (`customer_credit_risk_rating <- credit_type_code`) reaches REJECT in the current matrix (because the matrix's `measure-score` row treats `code` as `review` only at `latest` rule, which falls through to reject when no rule is observed). Operator-direction: **C1 should not pretend to solve this — G11b is deferred.** Confirmed; no matrix change needed.

### Review cell C — `dim-fiscal-period BF + measure-count CF + count_*` not yet observed in Apex but plausible

A pattern not directly observed but worth specifying: `count_distinct(fiscal_year)` to get "number of distinct fiscal years in window" is a legitimate measure-count operation. The matrix currently passes it via the `(any, count_distinct → measure-count)` rule. After the §3 review-cell-A tightening above, `(dim-*, count_*)` would move from ACCEPT to REVIEW. **Acceptable** — it stays admissible with rationale, and the rationale is straightforward to provide.

## 4. CF-inference gaps — heuristic should be improved before next pass

Names where the heuristic returned `ambiguous`:

- `total_credit_sales`, `net_credit_sales`, `total_credit_deployed`, `weighted_average_common_shares_outstanding`, `total_subscribers_or_users`, `total_segment_subscribers_or_users`, `total_orders_fulfilled` — **all should resolve to `measure-currency` (the first three) or `measure-count` (the rest)** but failed heuristic recognition. The token set missed `sales`, `shares_outstanding`, `subscribers`, `users`, `orders` as identity-bearing tokens.
- `days_to_consolidated_statements`, `measurement_period_in_years` — **should resolve to `duration` or `dim-fiscal-period`** but the heuristic missed.
- `gross_margin_dollars` was incorrectly resolved to `measure-ratio` (token "margin" matched) when it should be `measure-currency` (token "dollars" should override).

**Implication for C1 filing:** the heuristic gaps are not matrix-design problems — they are a separate **AI-advisory prompt-engineering task** for `POST /ai/api/semantic-definitions/semantic-family-suggest`. The matrix's correctness is unaffected; the gap is in the input layer that feeds family values into the matrix. The MWR notes this; it is not a blocker for C1.

## 5. DBCP-1a `compatible_data_types` / `compatible_unit_types` — issues found

The DBCP-1a draft seeds a compatibility matrix per `semantic_family` value. Cross-checking against Apex examples:

### Issue D1a-i — `measure-score` data_type=number only

DBCP-1a seeds `measure-score` with `compatible_data_types = {'number'}`. But Apex's `customer_credit_risk_rating` is a categorical score (HIGH / MEDIUM / LOW) — a **string-coded score**, not a numeric one.

**Two options:**
- (a) Broaden `measure-score` compatible_data_types to `{'number','string'}`.
- (b) Reclassify categorical scores as `code` family (not `measure-score`). Per the operator's discussion of Case C, treating credit_risk_rating as `code` may be more honest — it is a controlled vocabulary, not a numeric measure. Then `measure-score` keeps `{'number'}` for true numeric scores (e.g. NPS 0-10, credit score 300-850).

**Recommendation:** (b). Reclassify categorical risk ratings as `code` family with `code_vocabulary_code = 'credit_risk_rating'` (G11b future). Keep `measure-score` `{'number'}` for numeric scores. **Matrix unchanged; DBCP-1a unchanged; the semantic_family choice for Apex's risk-rating CF changes from `measure-score` to `code`.**

### Issue D1a-ii — `dim-fiscal-period` data_type=string only

DBCP-1a seeds `dim-fiscal-period` with `compatible_data_types = {'string'}`. But Apex's GJAHR is **numeric** (integer year, e.g. `2026`). The current Drizzle BF column data_type for fiscal-year BFs is likely `integer` or `text` depending on the source.

**Recommendation:** broaden `dim-fiscal-period` compatible_data_types to `{'string','number'}`. Same applies to `dim-calendar-date` (some sources store as YYYYMMDD integer; others as date) — broaden to `{'date','string','number'}`. Also `period` already has `{'string','number'}` in DBCP-1a — consistent.

### Issue D1a-iii — `measure-ratio` unit_type = ratio is over-restrictive

DBCP-1a seeds `measure-ratio` with `compatible_unit_types = {'ratio'}`. But Apex's KURSF (exchange rate) — which sits at semantic_family `measure-ratio` — is more accurately a **currency-conversion factor** with unit `factor` or `multiplier`, not `ratio` in the pure sense.

**Recommendation:** broaden `measure-ratio` compatible_unit_types to `{'ratio','factor','multiplier'}` or add a separate `measure-factor` family. **Defer this decision** — it's borderline scope creep on the 24-family closed enum from D366. For now, accept the lossy mapping: KURSF → semantic_family=`measure-ratio` with `unit_type_code = 'ratio'` as the best available fit. Revisit if the type-shape comparison surfaces real problems in Phase 1.

### Issue D1a-iv — `compute__derived` source has no semantic_family

Apex has 2 producing MCs whose inputs are `compute__derived` (engine-derived, not source-mapped). DBCP-1a's `master.semantic_family` seed has no family for "engine-derived" inputs — and shouldn't, because `compute__derived` is a *binding mechanism*, not a value semantic. The CF still has its own `semantic_family` (e.g. `measure-count` for `number_of_overdue_invoices`); the BF side is `compute__derived` with no semantic_family.

**Implication for G11:** when BF source is `compute__derived`, G11 evaluation should **skip** — the BF-CF compatibility check is N/A for engine-derived inputs. This is **a gap in the C1 draft** that needs to be named.

**Pre-filing change to C1:** add to §6.1 / §8 a clarifying note that G11 does not apply when BF source is `compute__derived`. Engine-derived inputs are governed by the engine's derivation logic, not G11. (See Lane B C-extension placeholder: governance of `compute__derived` is the fourth scope gap surfaced in Pool 1.)

## 6. Summary of changes needed before filing C1

| # | Change | Affects | Severity |
|---|---|---|---|
| **M1** | Tighten §4 `measure-count` row: `(measure-currency|measure-ratio|measure-percent|measure-score, count_*)` → REVIEW (not ACCEPT). Same for `(date|datetime|period|dim-*, count_*)` → REVIEW | C1 §4.2 matrix table | Medium |
| **M2** | Add clarifying paragraph: G11 does not apply when BF source is `compute__derived` (engine-derived inputs). Reference the deferred engine-derivation governance gap | C1 §6 / §8 | Low |
| **M3** | Re-classify categorical scores (HIGH/MEDIUM/LOW-style ratings) as `code` family, not `measure-score`. Update §1 Case C example accordingly: `customer_credit_risk_rating` is `code` (with `code_vocabulary_code='credit_risk_rating'` per G11b); the BF `credit_type_code` is `code` (with `code_vocabulary_code='credit_type'`). G11 still passes Case C at the family-pair level; G11b catches the code-vocabulary mismatch | C1 §1 Case C; §7 G11b discussion | Low |
| **M4** | Broaden DBCP-1a seed for `dim-fiscal-period` to `compatible_data_types = {'string','number'}` (GJAHR as integer is real-world common) | DBCP-1a seed | Low |
| **M5** | Broaden DBCP-1a seed for `dim-calendar-date` to `compatible_data_types = {'date','string','number'}` (YYYYMMDD-as-integer is real-world) | DBCP-1a seed | Low |
| **M6** | Note in DBCP-1a that `measure-ratio` unit_type=ratio is a best-fit for currency-conversion factors like KURSF; revisit if Phase 1 surfaces real conflicts | DBCP-1a notes | Low |

**Not changes — confirmations:**
- The operator's §5 non-overridable classes (a-d) are all confirmed by Apex evidence (35+ direct hits).
- The G11 gate sequence at cc_field_mapping authoring is correct.
- The G11b deferral is the right call — credit_type vs credit_risk_rating is not solvable at family level alone.
- The 24-value `master.semantic_family` enum from D366 is structurally sufficient for the observed Apex surface (no missing families).

## 7. Validation completeness

| Layer | Validated | Notes |
|---|---|---|
| §4 matrix structural correctness (which family-pairs the matrix accepts/rejects) | ✓ confirmed against 17 distinct reject-cells, 3 accept-cells | Strong evidence |
| §4 matrix rule-specific completeness | △ partial — 51% of inputs lack rule data in the chain-detail surface | Iterate after Phase 0 projection extension to surface cc_field_mapping rule per variable |
| §5 non-overridable classification (operator's hard-reject classes) | ✓ confirmed | All four classes (a-d) have ≥4 Apex hits each |
| §7 G11b deferral rationale | ✓ confirmed | The 1 code-BF + code-CF case (Apex Case C) is exactly the gap G11b would close |
| DBCP-1a seed `compatible_data_types` | △ 2 broadenings needed | M4 + M5 |
| DBCP-1a seed `compatible_unit_types` | △ 1 best-fit note | M6 |
| CF-inference heuristic | △ 25% gap; not a C1 blocker | AI-advisory prompt-engineering task |

## 8. Recommendation

**Apply M1–M6 to the C1 draft + DBCP-1a draft before filing.** None of the changes alters the fundamental amendment shape; all are tightening or clarification based on Apex evidence.

After M1–M6:
- C1 can be filed as an amendment to DEC-a17d0f via `devhub_decision_record` per the C1 draft §14.
- DBCP-1a's seed is ready to present for execution-approval (still draft, still no execution).

The §7 G11b sub-gate and the engine `compute__derived` governance gap should be tracked as **two named future amendment ADRs** (not filed in this wave; named in the C1 ADR body and in the Lane C backlog).

## 9. Evidence

| Source | Used for | Computed |
|---|---|---|
| `C:/tmp/apex-46-trust.json` (Pool 1 audit output) | 46 producing MCs with full chain-detail per variable | 2026-05-12 PM |
| `C:/tmp/apex-all-candidates.json` (Phase 0 walkthrough output) | 114 non-stale candidate MCs | 2026-05-12 PM |
| `GET /api/semantic-definitions/projections/meaning-once-candidates` | CF → collision-rule mapping (144 groups) | 2026-05-12 PM |
| Heuristic inference script | `C:/tmp/matrix-review.js` (no-write, no-network) | 2026-05-12 PM |
| Raw output | `C:/tmp/matrix-review-summary.json` (32 distinct triples, JSON shape) | 2026-05-12 PM |

## 10. Operator review checklist

- [ ] §1 confirmed-accept cells reviewed; 47 inputs across 3 cells
- [ ] §2 confirmed-reject cells reviewed; 35+ inputs across operator §5 (a-d) classes
- [ ] §3 M1 matrix refinement (count_* on measure-* BFs → REVIEW) approved
- [ ] §5 M2 clarification on `compute__derived` skip approved
- [ ] §5 M3 reclassification of categorical scores as `code` family approved
- [ ] §5 M4–M6 DBCP-1a seed broadenings reviewed
- [ ] Plan to file C1 as ADR amendment with M1–M3 applied: _yes / no_
- [ ] Plan to update DBCP-1a draft with M4–M6: _yes / no_
- [ ] G11b deferral confirmed as the next future amendment, not in this wave: _yes / no_
- [ ] `compute__derived` engine-derivation governance noted as a separate future amendment: _yes / no_
