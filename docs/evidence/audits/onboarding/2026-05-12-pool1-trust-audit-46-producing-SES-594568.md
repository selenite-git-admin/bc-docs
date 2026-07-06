---
metric: apex-pool1-trust-audit
metric_version: n/a
tenant: apex
source_system: n/a
work_type: read-only-diagnostic
session_uid: SES-594568
date: 2026-05-12
status: decision-pending
related_commits: []
related_tasks: []
related_adrs:
  - DEC-a17d0f
related_mwrs:
  - 2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md
  - 2026-05-12-semantic-definitions-authority-design-SES-a223ea.md
related_change_records:
  - CHG-28ab0c
repair_location: D
affected_boundary: metric_evaluation
foundation_gate: passed
---

# Pool 1 trust audit — 46 producing Apex MCs

> **Read-only diagnostic.** Audits the 46 currently-producing Apex MCs against the SDA Phase 0 projections + chain-detail traces. Establishes the **trust baseline** before any Lane B certification work proceeds. No writes proposed.

## 0. Stance

The Apex dial shows 46 producing MCs. Before declaring any of them "demo-ready", this MWR asks: **how many are actually trustworthy?** A producing MC is one that the engine returned a number for. A trustworthy MC is one whose number, by inspection of the chain, can be defended as the metric's stated meaning.

Trust verdict per MC is computed from observable evidence in `chain-detail` + the G10 meaning-once-candidates projection. **No source-data inspection** — that would require tenant-runtime reads which are out of scope.

## 1. Method — trust-verdict heuristic

For each producing MC, capture: formula text, formula audit status, audit findings, every input variable's CF, the cc_field_mapping target BF, source table, source field, and the CF's worst G10 collision-group size.

| Verdict | Heuristic |
|---|---|
| **HIGH** | audit `pass` + 0 findings + no fiscal-year source + no exchange-rate source + every input collision ≤ 1 |
| **MEDIUM** | audit `pass` + 0 critical findings + every input collision ≤ 5, but ≥ 2 |
| **LOW** | audit `warn` OR any input collision in [10, 50), no nonsense source |
| **UNTRUSTED** | any D335-R4 finding (formula vs mapping-rule mismatch) OR fiscal-year-as-source OR exchange-rate-as-source OR any input collision ≥ 50 |

This is a deliberately conservative heuristic. A MEDIUM or LOW verdict does not mean "wrong number" — it means the number cannot be defended *purely from the chain* without further per-cluster adjudication. UNTRUSTED means the chain itself contains a structural defect that makes the number unreliable regardless of source data.

## 2. Headline result

| Verdict | Count of 46 | Share |
|---|---|---|
| **HIGH** | **1** | 2% |
| **MEDIUM** | **0** | 0% |
| **LOW** | **3** | 7% |
| **UNTRUSTED** | **42** | 91% |

**The 46-MC producing dial reduces to 1 confidently-trustworthy MC + 3 plausible-with-adjudication MCs.** The remaining 42 produce values that the chain itself flags as semantically unreliable.

### Finding-code tally (across 17 of 46 MCs)

| Finding | Count |
|---|---|
| `D335_SUM_ON_LATEST` | 8 |
| `D335_SUM_ON_COUNT_WHERE_NOT_NULL` | 5 |
| `D335_SUM_ON_COUNT_DISTINCT` | 4 |

Total: 17 MCs (37%) carry an explicit formula-vs-mapping-rule mismatch. The engine returns a number, but the number's semantic is not what the formula text implies (e.g. `SUM()` wrapping a `latest`-rule mapping returns the latest value, not a sum).

### Source-field nonsense flags

| Flag | MCs |
|---|---|
| Fiscal-year (GJAHR / `*fiscal_year` BF) used as a measure | **14** |
| Exchange-rate (KURSF / `*exchange_rate` BF) used as a measure | 0 |
| `computed` source (engine-derived, not source-mapped) | 2 |

### Worst-input-collision histogram

| Worst input collision | MCs |
|---|---|
| 1 (unique signature) | 2 |
| 2 – 5 | 1 |
| 6 – 10 | 0 |
| 11 – 30 | 10 |
| 31 – 78 | 8 |
| **79 – 281** | **25** |

**More than half** of the producing surface (25/46) has at least one input that sits in the 281-collision group through `cc__actual_ledger.actual_ledger_amount sum`. The 14-MC fingerprint cluster in §3 is exactly this set.

## 3. Mapping-fingerprint clustering (the duplicate-numbers finding)

The 46 producing MCs share only **21 distinct mapping fingerprints**. The largest clusters:

### Cluster F1 — 14 MCs share the fingerprint `cc__actual_ledger.actual_ledger_amount/sum` (single input)

```
mc__gross_written_premium_gwp
mc__insurance_revenue_ifrs_17
mc__total_revenue
mc__unrecognized_tax_benefits_utb
mc__value_of_new_business_vnb
mc__asset_management_training_investment
mc__cost_avoidance_from_asset_management
mc__cost_of_revenue
mc__deferred_revenue
mc__deferred_revenue_balance
mc__recognized_revenue
mc__revenue_backlog
mc__revenue_by_channel
mc__revenue_by_region
```

**All 14 reduce to `SUM(actual_ledger_amount)` over the same source rows.** Each produces an identical number unless distinguished by a `filter_json` on the cc_field_mapping (none of which were observed in the trace data). Distinct business concepts on the same wire: revenue, premium written, IFRS-17 insurance revenue, unrecognized tax benefits, value of new business, training investment, cost avoidance, cost of revenue, deferred revenue, deferred revenue *balance*, recognized revenue, revenue backlog, revenue by channel, revenue by region — **14 names, presumably one number.**

This is the 281-CF Meaning-once collision (DEC-a17d0f §4 G10 Class-A) made concrete at the running-metric layer.

### Cluster F2 — 9 MCs share the fingerprint `cc__actual_ledger.actual_ledger_amount/sum + cc__invoice_hdr.invoice_hdr_extended_amount/sum`

```
mc__gross_profit_margin
mc__asset_utilization_ratio
mc__capital_intensity_ratio
mc__research_development_to_revenue_ratio
mc__sg_a_to_revenue_ratio
mc__shipping_cost_as_of_revenue
mc__cost_of_revenue_cogs_ratio
mc__gross_margin
mc__return_on_revenue
```

**All 9 reduce to a ratio of two summed source columns.** Distinct business ratios on identical fingerprint: gross profit margin, asset utilization, capital intensity, R&D to revenue, SG&A to revenue, shipping to revenue, COGS ratio, gross margin, return on revenue — **9 ratio metrics, presumably one ratio.**

### Cluster F3 — 4 AR MCs share `receivable_hdr_amount/count_where_not_null + receivable_hdr_fiscal_year/sum`

```
mc__dispute_resolution_time
mc__intercompany_reconciliation_aging
mc__invoice_delivery_time
mc__revenue_recognition_lag
```

The count_where_not_null on `receivable_hdr_amount` returns the count of AR rows with non-null amount; the `sum` on `receivable_hdr_fiscal_year` sums the fiscal-year codes. **Neither operation is semantically meaningful for "dispute resolution time" or "invoice delivery time" — these MCs produce numbers that are arithmetically defined but business-meaningless.** D335-R4 implicit.

### Cluster F4 — 2 MCs share `actual_ledger_fiscal_year/latest + invoice_hdr_extended_amount/sum`

```
mc__total_asset_turnover
mc__working_capital_turnover
```

Mapping `actual_ledger_fiscal_year` (GJAHR code) via `latest` rule and dividing by sum of NETWR. Returns a number; the number is a fiscal-year-code divided by an invoice-amount-sum. Not a turnover ratio.

### Unique-fingerprint MCs (17 of 46)

17 MCs each have their own distinct fingerprint. Some are HIGH/LOW verdicts (see §4); most are UNTRUSTED for the standard reasons (D335 / fiscal_year / large collision).

## 4. The trustworthy subset

### The 1 HIGH verdict

```
mc__average_days_delinquent (accounts_receivable, fact_rows=59)
  formula: O1 = SUM(I1) / SUM(I2)
  audit: pass, findings: []
  inputs:
    sum_of_days_past_due_for_overdue_invoices  <- compute__derived
    number_of_overdue_invoices                 <- compute__derived
```

**Important caveat:** this MC is HIGH per the heuristic because both inputs are `compute__derived` (engine-derived, not source-mapped) — they cannot collide on source signatures by construction. The trust verdict therefore rests on **the engine's derivation logic being correct**, which this audit did not validate. The MWR cannot certify the number as trustworthy without inspecting how `compute__derived` is implemented for these two CFs. **HIGH should be read as "no chain-level defect detected" — not "verified correct".**

### The 3 LOW verdicts

| MC | Formula | Worst input | Notes |
|---|---|---|---|
| `mc__blocked_invoices_value` (AP) | `O1 = SUM(I1)` | 30 (cc__invoice_hdr.invoice_hdr_extended_amount/sum) | Single-input sum of NETWR. Defensible if `sum_of_all_blocked_invoices_value` becomes the survivor of the 30-CF cluster. |
| `mc__ar_to_sales_ratio` (AR) | `O1 = SUM(I1) / SUM(I2)` | 49 (cc__receivable_hdr.receivable_hdr_amount/sum) | Inputs: `accounts_receivable_balance` (49-CF cluster) and `total_credit_sales` (30-CF cluster). Defensible if both CFs become their respective cluster survivors. |
| `mc__total_ar_balance` (AR) | `O1 = SUM(I1)` | 49 | Single-input sum of WRBTR via `open_item_amount`. Note: `open_item_amount` is **not** `accounts_receivable_balance` — there are two AR-amount CFs in the 49-cluster. If `accounts_receivable_balance` is chosen as the cluster survivor, this MC may need its variable re-bound. |

**All 3 LOW are AR/AP and have audit-pass, no findings, no fiscal-year source.** Their trustworthiness is contingent on Pool 3's per-cluster adjudication outcome — not on any further read-only inspection.

## 5. Implications for Lanes A / B / C

This audit changes the Lane B scope materially. Three explicit revisions:

### Revision R1 — the demo set is much smaller than 46

The original plan implicitly treated the 46 producing MCs as the demo trust-baseline. The audit shows that baseline is **1 + 3 contingent = 4 MCs**, not 46. Any demo narrative built on "46 metrics producing" is currently overselling.

**Implication for Lane B:** Pool 1 doesn't yield a ready demo set. The Lane B output is a much shorter list of *demo-eligible candidates* dependent on Pool 3 adjudication. The 4 demo-eligible MCs span 2 subfunctions (AR, AP) — narrow.

### Revision R2 — the 14 / 9 / 4 / 2 fingerprint clusters are the demo problem and the adjudication target

If the goal is "more trustworthy demo metrics", the highest-leverage move is **per-cluster adjudication of the F1 (14-MC) and F2 (9-MC) clusters**, not certification of individual primitives one-by-one. Adjudicating F1 cleanly could yield several distinguishable revenue/cost CFs each underpinning 1-3 MCs. Without adjudication, those 14 MCs remain UNTRUSTED no matter what else Lane B does.

This **confirms** the Lane B Pool 3 sequence (281-CF cluster first) but **strengthens its urgency**. It is not a structural improvement deferred to Phase 2 — it is **the primary path to a defensible demo today**.

### Revision R3 — `compute__derived` CFs are a separate category that the SDA does not currently govern

The 1 HIGH and the 2 `computedSrc` flagged MCs reach the engine via `compute__derived` source — meaning a derived-CF mechanism exists in the engine and is in active use. The SDA grammar today governs CF identity but not derivation logic. **The engine's derivation logic is unmanaged from the SDA's standpoint.** This is a fourth governance gap to add to Lane C's scope (alongside BF-CF compatibility, MC dedup, and cross-domain scope) — possibly as part of the C1 amendment, possibly as its own.

For Apex demo purposes, the 1 HIGH MC (`mc__average_days_delinquent`) should not be claimed as trustworthy without inspecting its derivation logic separately. **This is a TSK candidate (read-only):** trace `compute__derived` for `sum_of_days_past_due_for_overdue_invoices` and `number_of_overdue_invoices` and confirm the engine's logic matches the CF's stated meaning.

## 6. Confirmation of Pool 3 cluster sequence

The Pool 1 audit confirms the planned Pool 3 sequence — **the 281-CF cluster is correctly the first target.**

Refined per-cluster impact on Apex producing dial (estimated post-adjudication uplift):

| Cluster | Apex producing MCs in cluster | Post-adjudication trustworthy uplift |
|---|---|---|
| 281-CF `cc__actual_ledger.actual_ledger_amount/sum` | 14 (F1) + portions of 25 with 79-281 collision | Could turn 5-10 of the 14 into trustworthy MCs (those whose business semantic genuinely is "ledger amount summed", filtered appropriately) |
| 78-CF `cc__invoice_hdr.invoice_hdr_total_amount/sum` | 0 producing today | Affects non-stale candidates (Phase 0 walkthrough §A4); not Pool 1 surface |
| 49-CF `cc__receivable_hdr.receivable_hdr_amount/sum` | 3 (the LOW verdicts + others in F3) | Affects the 3 LOW + the F3 cluster (4 MCs) |
| 30-CF `cc__invoice_hdr.invoice_hdr_extended_amount/sum` | At least 1 of the LOW + portions of F2 | Affects F2 9-MC cluster |

**Sequence approved:** 281 → 49 → 78 → 30. The 49 moves up because three of the 4 demo-eligible MCs depend on it; the 78 and 30 follow.

## 7. Recommendations for next action

Confirmed and refined:

1. **Pool 3 cluster adjudication starts now**, in the order 281 → 49 → 78 → 30. Paper-only per-cluster MWRs; certification acts wait on Lane A's substrate.
2. **The HIGH MC's derivation logic** needs a separate read-only trace before being claimed as demo-ready. Small TSK candidate.
3. **A fourth governance scope gap** (engine `compute__derived` governance) should be added to Lane C, either as part of C1 or as its own small ADR.
4. **Demo narrative should be re-framed** from "46 producing" to "1 verified + 3 contingent-on-adjudication today; 5-10 expected post-Pool-3-cluster-adjudication".

## 8. Stop conditions encountered

| Stop condition | Triggered | Action |
|---|---|---|
| Producing-but-untrustworthy pattern at scale | 42 of 46 UNTRUSTED | Reported; no shortcut greenification proposed |
| Fingerprint collapse (14 MCs on one signature) | Cluster F1 = 14 producing MCs sharing one fingerprint | Reported; pointed at Pool 3 cluster adjudication, not at hand-curation |
| Engine derivation as an unmanaged surface | 2 `computedSrc` cases, 1 HIGH verdict resting on it | Reported as new governance scope-gap candidate |
| D335-R4 widespread | 17 MCs across 3 finding codes | Reported; flagged as Lane B adjudication input, not as standalone fix |
| Demo narrative gap | Producing≠trustworthy | Reported in §5 R1 |

## 9. Evidence

| Source | Used for | Computed |
|---|---|---|
| `GET /api/admin/tenant-metrics/snapshot?tenant=apex` (46 producing rows) | §1 MC selection | 2026-05-12 PM |
| `GET /api/registry/metric-readiness/chain-detail/:mcId` × 46 | §2 audit findings, §3 fingerprints, §4 inputs | 2026-05-12 PM |
| `GET /api/semantic-definitions/projections/meaning-once-candidates` | §3 collision membership for each CF | 2026-05-12 PM |

Raw audit output: `C:/tmp/apex-46-trust.json` (46 records, schema documented in §1).
