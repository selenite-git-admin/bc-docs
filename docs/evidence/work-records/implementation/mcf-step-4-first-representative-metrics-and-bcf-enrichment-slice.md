---
uid: mcf-step-4-first-representative-metrics-and-bcf-enrichment-slice
title: MCF Step 4 — First Representative Metrics + BCF Enrichment Slice
description: Step 4 of the MCF arc. Selects 10 representative candidate-intent metrics from the bc_seed.seed_metrics high-confidence + apqc pool and derives the minimal BCF enrichment slice (entities, business concepts, characteristics) required to author them later under MCF. Candidate-intent only — no co_bindings, no BF/BO/CF/CM fragments, no legacy SQL MC migration. Selection is a proposal scoped to ~3 Entity families + ~10-12 BCs + at most 1 new characteristic, well within BCF v1 packet sufficiency envelope (per BCF enrichment preflight, commit 3495739). No code changes. No DDL apply. No MCF M3.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: enrichment-slice
---

# MCF Step 4 — First Representative Metrics + BCF Enrichment Slice

## 1. Scope and grounding

### 1.1 Purpose

Step 4 of the MCF arc. The arc to date:

| Step | Artifact | Commit |
|---|---|---|
| 1 | MCF inventory | `d9b10d2` |
| 2 | MCF gap survey | `0ba202b` |
| 2-addendum | Reservoir + authority classification | `0e3644b` |
| 3 | MCF build plan (21 gates M0-M20) | `40a9adc` |
| M0 | Pre-M1 decision packet + correction | `5cd72c6` + `6ce9451` |
| BCF/MCF alignment note | Panel-workbench reconciliation | `da8d9b7` |
| M1 | Foundational MCF ADR (DEC-c3e57f / D422) | `155ed4f` |
| M2 preflight + DBCP design | Identity substrate design | `1987306` + `a4b25a5` + `dda900e` |
| M2 doc alignment | Schema-name fix | `27dcc80` |
| M2 execution | bc-core PR #101 merged | bc-core `92a9056` (DDL not applied) |
| BCF enrichment preflight | v1 packet sufficient verdict | `3495739` |

This Step 4 deliverable:

1. **Selects 10 representative candidate-intent metrics** from the operator-decided starting pool (high-confidence + apqc seed_metrics, ~397 rows per addendum §3.5).
2. **Derives the minimal BCF enrichment slice** the 10 metrics will need before they can be authored under MCF.
3. **Confirms BCF v1 packet sufficiency** for the derived slice against the preflight's enumerated trigger conditions.
4. **Stops at the slice proposal.** Step 4 does **not** implement BCF enrichment, does **not** open MCF M3, does **not** apply MCF M2 DDL.

### 1.2 What this is not

- **Not an MCF authoring act.** The 10 selected candidates are candidate-intent only. Authoring authority is created at the MCF Metric Authoring Panel + operator confirm + deterministic verifier path (DEC-c3e57f Decision 3); inclusion in this Step 4 doc creates no MCF metric contract.
- **Not a BCF authoring act.** The derived BCF slice is a proposal for the BCF panel + operator to author against business reality. Per DEC-c3e57f Decision 10 guardrail #2, BCF enrichment is operator + BCF-panel decided, not seed-wording driven; the BCs and characteristics named here are intent labels, not authored definitions.
- **Not a build plan.** Sequencing (which entities first, which BCs next, etc.) is in build plan §6 + BCF preflight §6.7; this doc inventories the slice content.
- **Not an MCF M3 / M2 DDL trigger.** Both gates stay closed per operator instruction.
- **Not authority over legacy SQL MC rows.** The legacy `contract.metric_contract` corpus (778/780 archived; 2 non-archived 2026-05-14 drafts) is historical-only per DEC-c3e57f Decision 2. Nothing in §4 below is sourced from those rows.

### 1.3 Inputs read

| Class | Source | Role |
|---|---|---|
| Build plan §7 selection criteria | `metric-context-framework-build-plan.md` (`40a9adc`) §7.1, §7.2 | The 10 metric classes + per-class formula pattern |
| Reservoir classification | `metric-context-framework-candidate-reservoir-and-authority-classification.md` (`0e3644b`) §3.5 | Starting pool: 397 high-confidence + apqc seed_metrics |
| MCF foundational ADR | `ADR-c3e57f.md` Decision 3 + 5 + 6 + 8 + 10 | Candidate-vs-authority discipline; BCF as sole semantic-binding authority |
| BCF enrichment preflight | `bcf-enrichment-preflight-for-mcf-seed-cases.md` (`3495739`) §4 + §5 + §6 | v1 packet sufficiency verdict; trigger conditions; recommended slice scope |
| BCF F4-S1 v1 characteristic seed list | `business-concept-registry-f4-s1-characteristic-seed-list.md` (`accepted` 2026-05-21) | The 24 approved characteristics seeded into BCF substrate |
| BCF B10a-S4 UI readiness checklist | `business-concept-registry-b10a-s4-ui-readiness-checklist.md` line 31 | Confirmed-active baseline: Entity `Sales Order Line` + BC `Unit Price` |
| BCF B10-publication-lifecycle-design | `business-concept-registry-b10-publication-lifecycle-design.md` line 84 | Confirms a `draft` characteristic is invisible to binding; activation is operator-gated |
| Live Mongo `bc_seed.seed_metrics` | direct read 2026-05-26 (script `bc-seed/tmp/mcf-step4-seed-pool.mjs`, read-only) | Candidate-intent pool sampling |
| Live SQL `metric.metric_definition` | `pg-postgres` MCP read 2026-05-26 | Finance candidate-intent distribution |

### 1.4 Discipline assertions (per operator brief verification)

| Assertion | Status |
|---|---|
| All selected metrics are candidate-intent only | ✓ — none binds a substrate row; none creates an MCF MC. |
| No `co_bindings` / BF / BO / CF / CM fragments used as authority | ✓ — Mongo project-only excluded `co_bindings`, `related_metrics`, `search_tags`. |
| No legacy SQL MC row migrated or treated as authoritative | ✓ — `contract.metric_contract*` not consulted; selection pool is the post-D418 candidate reservoir only. |
| BCF enrichment slice ≤ v1 packet capacity | ✓ — derived slice: 1 new Entity + ~11 new BCs + at most 1 new Characteristic across 3 Entity families. Each authoring is one panel run. See §8. |

---

## 2. Selection method

### 2.1 Method

1. **Read** build plan §7.1 (the 10 representative metric *classes* the slice must exercise) and §7.2 (selection criteria).
2. **Sample** the high-confidence + apqc pool (Mongo `bc_seed.seed_metrics`) across the function buckets relevant to each class. Pool size: 397 docs (confirmed live 2026-05-26).
3. **Filter** in a per-class targeted scan (`ar_collections_candidates`, `sales_candidates`, `ops_cycle_lead_candidates`, `period_anchored_candidates`) to surface concrete candidate-intent names + reference formulas.
4. **Map** each class to one concrete candidate-intent metric whose intent fits the class pattern, prefering metrics whose BCs map to already-active or F4-S1-seeded characteristics where possible (reduces enrichment scope).
5. **Reserve** two slots (metric 9, metric 10) for deliberate-failure constructions per build plan §7.1 (one MLS-14 semantic-collapse, one PE-MC-10 stale-fixture).
6. **Constrain** to ≤3 Entity families for the slice (per BCF preflight §6.3 recommended starting set), reusing Customer Invoice across multiple AR/billing metrics rather than spawning a new Entity per metric.

### 2.2 Selection guardrails (per DEC-c3e57f Decision 10 + addendum §5)

| # | Guardrail | How honored here |
|---|---|---|
| 1 | No candidate reservoir creates authority by inclusion | This doc explicitly proposes; final MCF MC authoring is panel + operator-confirm + verifier later. |
| 2 | BCF enrichment scope is operator + BCF-panel decided, not seed-wording driven | The seed metric `display_name` and `description` text is intent reference only; BCF concepts are named per the F4-S1 24-characteristic vocabulary + at most 1 new characteristic. |
| 3 | Panel rejection of legacy-only grounding is mandatory; `co_bindings` stripped at ingest | This doc does not read `co_bindings` at all. |
| 4 | Duplicate-intent detection at draft → review (PE-MC-9) | Step 4 selection avoids duplicate-intent within the 10 — checked manually below; PE-MC-9 will re-check at MCF authoring. |
| 5 | Source-system assumptions must be explicit before draft | Each per-metric row in §4 notes the source-system shape it assumes (e.g. "ledger-recording date"); MCF panel may route to operator-confirm. |
| 6 | Reservoir provenance recorded | Each selected metric in §4 cites its seed `metric_name` + sources tag; MCF panel will record these on `mcf.metric_authoring_panel_run`. |
| 7 | No SQL MC corpus migration; ever | No legacy MC rows referenced in §4. |

### 2.3 What this method does not do

- It does not enumerate live BCF concept density (the `concept_registry` schema is not in this Claude session's bc-postgres allowlist — same constraint as the gap survey Q4 / addendum §8.4).
- It does not author the BCF slice or the MCF MCs.
- It does not propose the per-MC AST nodes in detail — only the formula *shape* and which BCs the variables bind to.
- It does not select the 11th-Nth seed candidates (the 397-pool remainder stays available for Step 5 / later operator selection).

---

## 3. Candidate reservoir evidence

### 3.1 Pool size

Per Mongo read 2026-05-26:

| Filter | Count |
|---|---:|
| `confidence='high'` AND `apqc` in sources | **397** |
| `confidence='high'` AND `cfo-pack` in sources | 397 |
| `confidence='high'` total | 397 |

**Implication:** the high-confidence subset is fully and simultaneously apqc + cfo-pack sourced — there is no apqc-only or cfo-pack-only high-confidence row. The full 397-row pool is therefore PE-MC-1-eligible on (b) bc-seed catalog lineage AND (c) operator-curated bounded-domain provenance (per addendum §3.4); internet-only seeds (8,860 rows) are excluded from this Step 4 selection scope.

### 3.2 Distribution across function / subfunction buckets (top 25 of 397)

| function | subfunction | n |
|---|---|---:|
| operations | (null) | 21 |
| finance | general_ledger | 16 |
| finance | fpa | 16 |
| rnd_engineering | (null) | 15 |
| **finance** | **accounts_receivable** | **14** |
| finance | (null) | 13 |
| customer_experience | service_quality | 13 |
| finance | accounts_payable | 12 |
| supply_chain | procurement | 12 |
| sales | pipeline | 11 |
| marketing | campaigns | 11 |
| operations | process_efficiency | 10 |
| manufacturing | production | 10 |
| sales | sales_operations | 10 |
| quality | inspection | 10 |
| marketing | lead_generation | 9 |
| asset_management | (null) | 9 |
| product_portfolio | (null) | 8 |
| finance | treasury | 8 |
| executive | (null) | 8 |
| supply_chain | logistics | 7 |
| human_resources | performance | 7 |
| customer_experience | retention | 7 |
| governance | compliance | 7 |
| sales | bookings | 7 |

**Implication:** AR is the most populated business-meaningful bucket within finance for the natural pool (14 high-confidence + apqc rows). AR-class metrics naturally map to ratio + delta + count + windowed shapes against billing / collection / aging semantics — covering the bulk of the 10 representative classes in one entity family. This argues for **Customer Invoice as the second BCF entity** after Sales Order Line.

### 3.3 SQL candidate-intent cross-reference

`metric.metric_definition` candidate-intent (live 2026-05-26 from earlier gap survey + this scan):

| function | subfunction | n |
|---|---|---:|
| finance | general_finance | 203 |
| finance | accounts_payable | 111 |
| finance | general_ledger | 98 |
| finance | revenue_accounting | 97 |
| finance | fpa | 96 |
| finance | treasury | 75 |
| **finance** | **accounts_receivable** | **72** |
| finance | financial_risk_management | 64 |
| finance | tax | 59 |
| finance | financial_systems | 50 |
| finance | internal_audit | 44 |
| finance | iso_55001 | 33 |
| finance | credit_and_collections | 33 |

The SQL carve-out is finance-heavy and AR-rich (72 + 33 credit/collections = 105 finance-AR-area rows). Cross-reservoir alignment confirms the choice of AR as the operationally densest area for the first slice.

### 3.4 Sample evidence — AR/collections candidates from the 397-pool

Per Mongo read 2026-05-26 (15-row sample of `confidence='high'` AND `apqc` in sources AND AR-class match):

| metric_name | function/subfunction | reference_formula |
|---|---|---|
| `overdue_ar` | finance / accounts_receivable | `Overdue AR / Total AR * 100` |
| `unbilled_revenue` | finance / accounts_receivable | `Recognized Revenue - Billed Revenue` |
| `bad_debt_provision` | finance / accounts_receivable | `Bad Debt Provision / Total AR * 100` |
| `billing_to_cash_cycle_time` | finance / accounts_receivable | `AVG(cash_receipt_date - invoice_date)` |
| `average_days_to_collect` | finance / accounts_receivable | `AVG(clearing_date - due_date)` |
| `dispute_rate` | finance / accounts_receivable | `Disputed Invoices / Total Invoices * 100` |
| `disputes_older_than_30_days` | finance / accounts_receivable | `COUNT(disputes WHERE age > 30)` |
| `top_10_customer_ar_concentration` | finance / accounts_receivable | `Top10 AR / Total AR * 100` |
| `ar_with_missing_proof_of_delivery` | finance / accounts_receivable | `No-PoD Items / Total Open Items * 100` |
| `promise_to_pay_reliability` | finance / accounts_receivable | `Kept Promises / Total Promises * 100` |
| `invoice_adjustment_ratio` | finance / accounts_receivable | `Adjusted Invoices / Total Invoices * 100` |
| `reversal_credit_note_ratio` | finance / accounts_receivable | `Credit Notes / Gross Sales * 100` |
| `ar_without_recent_follow_up` | finance / accounts_receivable | `No Follow-Up > 14d / Total Overdue * 100` |
| `bookings_growth_rate` | sales / bookings | `(Bookings(current) - Bookings(prior)) / Bookings(prior) * 100` |
| `revenue_growth_rate` | finance / revenue_accounting | `(Current Period Revenue - Previous Period Revenue) / Previous Period Revenue` |

These candidate-intent shapes map cleanly to build plan §7.1 classes 1-7. The MLS-14 specimen (class 9) and stale-fixture failure (class 10) are deliberately constructed from class-2 (`overdue_ar`) and one of the AR-balance shapes; no separate seed row is needed.

---

## 4. The selected 10 metrics

Selection is operator-revisable. The selection authority remains operator + MCF panel + verifier at MCF MC authoring time.

Notation: `Cn` = constant; `In` = input variable; `O1` = output. Variable role per MCF requirements §6 / §7.2.

### Metric 1 — Simple aggregation (build plan §7.1 class 1)

| Attribute | Value |
|---|---|
| **Seed source** | `bad_debt_provision` denominator + `top_10_customer_ar_concentration` denominator (shared intent: "Total AR") |
| **Reservoir** | `bc_seed.seed_metrics` (high-confidence; apqc + cfo-pack) |
| **Metric intent** | Total open receivables at observation time |
| **Formula shape** | `O1 = SUM(I1)` |
| **Variable bindings (intent)** | `I1` ← Customer Invoice · outstanding amount |
| **Grain entity** | Customer Invoice |
| **Temporal gate shape** | point_in_time / as_of (observation timestamp) |
| **Direction** | n/a (raw value, not bounded by direction) |
| **Failure expected** | No — happy-path metric |

### Metric 2 — Ratio (build plan §7.1 class 2)

| Attribute | Value |
|---|---|
| **Seed source** | `overdue_ar` (`Overdue AR / Total AR * 100`) |
| **Reservoir** | `bc_seed.seed_metrics` (high-confidence; apqc + cfo-pack) |
| **Metric intent** | Percentage of receivables past due date |
| **Formula shape** | `O1 = (I1 / I2) * C1` |
| **Variable bindings (intent)** | `I1` ← SUM(Customer Invoice · outstanding amount) WHERE due_date < observation_date; `I2` ← SUM(Customer Invoice · outstanding amount); `C1` ← 100 |
| **Grain entity** | Customer Invoice (rolled up) |
| **Temporal gate shape** | as_of |
| **Direction** | lower-is-better |
| **Failure expected** | No — happy-path metric (and the parent for metric 10's stale-fixture variant) |

### Metric 3 — Difference / delta (build plan §7.1 class 3)

| Attribute | Value |
|---|---|
| **Seed source** | `unbilled_revenue` (`Recognized Revenue - Billed Revenue`) |
| **Reservoir** | `bc_seed.seed_metrics` (high-confidence; apqc + cfo-pack) |
| **Metric intent** | Revenue recognized but not yet invoiced |
| **Formula shape** | `O1 = I1 - I2` |
| **Variable bindings (intent)** | `I1` ← SUM(recognized revenue amount per period); `I2` ← SUM(billed revenue amount per period) |
| **Grain entity** | Customer Invoice (with recognition-period reference) |
| **Temporal gate shape** | period_aggregate |
| **Direction** | lower-is-better |
| **Failure expected** | No |
| **Note** | I1 and I2 bind to distinct BCs whose substrate signatures must differ — MLS-14 will refuse if they collapse (positive guard against the MT-04971-class trap). |

### Metric 4 — Passthrough / count (build plan §7.1 class 4)

| Attribute | Value |
|---|---|
| **Seed source** | `disputes_older_than_30_days` (`COUNT(disputes WHERE age > 30)`) |
| **Reservoir** | `bc_seed.seed_metrics` (high-confidence; apqc + cfo-pack) |
| **Metric intent** | Count of invoices in dispute status older than 30 days |
| **Formula shape** | `O1 = I1` (where I1 is a COUNT aggregate) |
| **Variable bindings (intent)** | `I1` ← COUNT(Customer Invoice · invoice id) WHERE status = 'in_dispute' AND (observation_date - status_change_date) > 30 |
| **Grain entity** | Customer Invoice |
| **Temporal gate shape** | as_of |
| **Direction** | lower-is-better |
| **Failure expected** | No |

### Metric 5 — Windowed (build plan §7.1 class 5)

| Attribute | Value |
|---|---|
| **Seed source** | `average_days_to_collect` (`AVG(clearing_date - due_date)`) — windowed to trailing 30 days |
| **Reservoir** | `bc_seed.seed_metrics` (high-confidence; apqc + cfo-pack) |
| **Metric intent** | Average days late collected (trailing 30-day window of payments) |
| **Formula shape** | `O1 = AVG(window(I1 - I2, '30d', payment posting date))` |
| **Variable bindings (intent)** | `I1` ← Customer Invoice · payment posting date; `I2` ← Customer Invoice · due date |
| **Grain entity** | Customer Invoice (windowed over recent payments) |
| **Temporal gate shape** | trailing_window (window = 30 days, anchor = I1) |
| **Direction** | lower-is-better |
| **Failure expected** | No |
| **AST node exercised** | `window` |

### Metric 6 — Fiscal-period computed-dimension (build plan §7.1 class 6)

| Attribute | Value |
|---|---|
| **Seed source** | `revenue_growth_rate` denominator + `recognized_revenue` intent (period-aggregated revenue) |
| **Reservoir** | `bc_seed.seed_metrics` (high-confidence; apqc + cfo-pack) |
| **Metric intent** | Recognized revenue per fiscal period |
| **Formula shape** | `O1 = SUM(I1) GROUP BY fiscal_period` |
| **Variable bindings (intent)** | `I1` ← Customer Invoice · invoice amount; computed-dimension `fiscal_period` resolved via D365 `posting_date_field` + tenant FiscalCalendarService from Customer Invoice · posting date |
| **Grain entity** | Customer Invoice (rolled to fiscal_period) |
| **Temporal gate shape** | period_aggregate (per fiscal_period) |
| **Direction** | higher-is-better |
| **Failure expected** | No — happy-path metric, but **defers** if D365 `posting_date_field` is not landed (per DEC-c3e57f Decision 9 + build plan §5.3) |
| **AST node exercised** | `time_anchor_resolution` |

### Metric 7 — Bucket-assign (build plan §7.1 class 7)

| Attribute | Value |
|---|---|
| **Seed source** | AR aging bucket discipline — multi-bucket extension of `disputes_older_than_30_days` (intent: invoices by aging band) |
| **Reservoir** | derived from `bc_seed.seed_metrics` AR-class shapes; intent is industry-standard DSO aging-bucket |
| **Metric intent** | Outstanding AR by aging bucket (0-30 / 30-60 / 60-90 / 90+ days past due) |
| **Formula shape** | `O1 = bucket_assign(I1, buckets=[0,30,60,90,∞])` followed by `SUM(I2) GROUP BY bucket` |
| **Variable bindings (intent)** | `I1` ← (observation_date - Customer Invoice · due date) in days; `I2` ← Customer Invoice · outstanding amount |
| **Grain entity** | Customer Invoice (rolled to aging bucket) |
| **Temporal gate shape** | as_of |
| **Direction** | n/a (per-bucket value) |
| **Failure expected** | No |
| **AST node exercised** | `bucket_assign` |

### Metric 8 — Positive cross-coherence (build plan §7.1 class 8)

| Attribute | Value |
|---|---|
| **Seed source** | `discount_rate_applied` (`AVG(discount_pct WHERE period = current)`) — recast at line grain |
| **Reservoir** | `bc_seed.seed_metrics` (high-confidence; apqc + cfo-pack) |
| **Metric intent** | Discount-to-line-amount ratio at Sales Order Line grain |
| **Formula shape** | `O1 = I1 / I2` |
| **Variable bindings (intent)** | `I1` ← Sales Order Line · discount; `I2` ← Sales Order Line · unit price × Sales Order Line · ordered quantity (line amount, derived) |
| **Grain entity** | Sales Order Line (already active in BCF Registry) |
| **Temporal gate shape** | point_in_time (per line) |
| **Direction** | lower-is-better |
| **Failure expected** | No — happy-path metric exercising same-entity bindings (positive grain-alignment check) |
| **Cross-coherence property** | I1 and I2 bind to distinct BCs on the **same** Entity (Sales Order Line). MLS-14 substrate-identity check should pass (signatures differ); MCF §6.3 check 5 should pass (grain-alignment positive). |

### Metric 9 — Failure case (MLS-14 semantic-collapse) (build plan §7.1 class 9)

| Attribute | Value |
|---|---|
| **Seed source** | Deliberate construction — MT-04971 specimen class per CLAUDE.md feedback_metric_lifecycle_states |
| **Reservoir** | n/a — constructed; not from a seed row |
| **Metric intent** | Deliberately collapsed ratio: numerator and denominator bound to the same BC |
| **Formula shape** | `O1 = I1 / I2` with bindings deliberately set so `I1` and `I2` share substrate identity |
| **Variable bindings (intent)** | `I1` ← Customer Invoice · outstanding amount; `I2` ← Customer Invoice · outstanding amount (identical binding) |
| **Grain entity** | Customer Invoice |
| **Temporal gate shape** | as_of |
| **Direction** | n/a |
| **Failure expected** | **YES — MLS-14 must return red.** PE-MC-10 should also catch via verifier fixture diff (output = 1.0 regardless of fixture inputs). Both gates apply (DEC-c3e57f Decision 7, layered both-must-pass). |

### Metric 10 — Stale fixture failure case (build plan §7.1 class 10)

| Attribute | Value |
|---|---|
| **Seed source** | Construction over Metric 2 (`overdue_ar`) — mutate the AST after fixture passes |
| **Reservoir** | n/a — constructed on top of Metric 2 |
| **Metric intent** | Confirm PE-MC-10 refuses to pass when fixture's bound `package_signature_hash` no longer matches |
| **Formula shape** | Initially `O1 = (I1 / I2) * C1` (Metric 2 AST); then mutate (e.g. swap I1 numerator filter or change C1) to invalidate the fixture |
| **Variable bindings (intent)** | Identical to Metric 2 |
| **Grain entity** | Customer Invoice |
| **Temporal gate shape** | as_of |
| **Direction** | n/a |
| **Failure expected** | **YES — PE-MC-10 must refuse** the post-mutation MC because its fixture's `package_signature_hash` no longer matches the MC's current hash (MCF §12.7 stale-fixture rule). |

### 4.x Selection summary

| # | Class | Concrete intent | Grain entity | Failure expected | AST node added |
|---|---|---|---|---|---|
| 1 | Simple aggregation | Total open receivables | Customer Invoice | No | (basic) |
| 2 | Ratio | Overdue AR % | Customer Invoice | No | (basic) |
| 3 | Difference | Unbilled revenue | Customer Invoice | No | (basic) |
| 4 | Passthrough / count | Aged dispute count | Customer Invoice | No | (basic) |
| 5 | Windowed | Avg days late, 30d window | Customer Invoice | No | `window` |
| 6 | Fiscal-period | Recognized revenue per fiscal_period | Customer Invoice | No (defers if no D365) | `time_anchor_resolution` |
| 7 | Bucket-assign | AR aging buckets | Customer Invoice | No | `bucket_assign` |
| 8 | Cross-coherence | Discount-to-line-amount | Sales Order Line | No | (basic) |
| 9 | MLS-14 failure | Self-collapsed ratio | Customer Invoice | YES (MLS-14 red) | (basic) |
| 10 | Stale-fixture failure | Post-mutation Overdue AR % | Customer Invoice | YES (PE-MC-10 refuse) | (basic) |

**Entity coverage:** Customer Invoice (8 metrics) + Sales Order Line (1 metric) + Customer Invoice constructed-failure (1 metric). 2 Entity families. Per build plan §7.2 the slice needs ≥3 Entity families for cross-Entity binding reachability — **see §6.4** for the third Entity choice.

**AST-node coverage:** `variable_ref`, `literal`, `aggregate`, `arithmetic`, `window`, `time_anchor_resolution`, `bucket_assign` — 7 of the closed taxonomy node types exercised (per MCF requirements §7.2). `case` and a few others are not exercised in the first 10; they roll into later metric selections.

**Failure-case coverage:** 2 (Metrics 9 + 10) — meeting build plan §7.2's "at least 2 metrics deliberately built to fail" requirement.

---

## 5. Per-metric BCF enrichment needs

For each metric, the BCF concepts the metric's variable bindings, grain entity, time anchors, filter inputs, and computed-dimension sources will need. "Status" column uses:

- **A**: already active in BCF Registry (confirmed per B10a-S4 readiness checklist).
- **S**: seeded in BCF substrate as F4-S1 v1 characteristic (accepted 2026-05-21) — lifecycle activation per-row needs verification (`concept_registry` not in this Claude session's allowlist).
- **N**: new — must be authored via BCF panel (createEntity / createBusinessConcept / createCharacteristic) during Step 4 enrichment.

### Metric 1 — Total open receivables

| Need | Concept | Status |
|---|---|---|
| Grain entity | Customer Invoice | **N** (createEntity) |
| Variable I1 — value | BC: Customer Invoice · outstanding amount | **N** (createBusinessConcept; characteristic = `outstanding amount` **N** see §5.x) |
| Time anchor | BC: Customer Invoice · observation reference (operation-time) — handled at MCF runtime, no BCF asset needed | n/a |

### Metric 2 — Overdue AR %

| Need | Concept | Status |
|---|---|---|
| Grain entity | Customer Invoice | (from Metric 1) **N** |
| Variable I1 — value (overdue subset) | BC: Customer Invoice · outstanding amount | (from Metric 1) **N** |
| Variable I2 — value (total) | BC: Customer Invoice · outstanding amount | (from Metric 1) **N** — same BC, different filter |
| Filter — date | BC: Customer Invoice · due date (characteristic = `due date` **S**) | **N** (createBusinessConcept; characteristic seeded) |
| Constant | `C1` = 100 (literal; not a BCF asset) | n/a |

### Metric 3 — Unbilled revenue

| Need | Concept | Status |
|---|---|---|
| Grain entity | Customer Invoice | (from Metric 1) **N** |
| Variable I1 — value (recognized) | BC: Customer Invoice · recognized revenue amount | **N** (characteristic = `recognized amount` **N** OR a panel decision; see §5.x) |
| Variable I2 — value (billed) | BC: Customer Invoice · billed amount | **N** (characteristic = `billed amount` **N** OR a panel decision; see §5.x) |
| Period anchor (for "per period") | BC: Customer Invoice · posting date (characteristic = `posting date` **S**) | **N** (createBusinessConcept; characteristic seeded) |

### Metric 4 — Aged dispute count

| Need | Concept | Status |
|---|---|---|
| Grain entity | Customer Invoice | (from Metric 1) **N** |
| Count target — identifier | BC: Customer Invoice · invoice id (characteristic = `line number`? OR identifier-role BC) | **N** (createBusinessConcept; representation_term = identifier; characteristic possibly = a panel decision) |
| Filter — status | BC: Customer Invoice · status (characteristic = `status` **S**) | **N** (createBusinessConcept; characteristic seeded) |
| Filter — date | BC: Customer Invoice · status change date (characteristic = `effective date` **S** — repurposed) | **N** (createBusinessConcept; characteristic seeded) |

### Metric 5 — Avg days late, 30-day window

| Need | Concept | Status |
|---|---|---|
| Grain entity | Customer Invoice | (from Metric 1) **N** |
| Variable I1 — date | BC: Customer Invoice · payment posting date (characteristic = `posting date` **S** — same characteristic as Metric 3's posting date, different role) | (from Metric 3) **N** |
| Variable I2 — date | BC: Customer Invoice · due date (characteristic = `due date` **S**) | (from Metric 2) **N** |
| Window anchor | reuses I1 (payment posting date) | n/a |

### Metric 6 — Recognized revenue per fiscal_period

| Need | Concept | Status |
|---|---|---|
| Grain entity | Customer Invoice | (from Metric 1) **N** |
| Variable I1 — value | BC: Customer Invoice · invoice amount | **N** (characteristic = panel decision; possibly new `invoice amount` characteristic) |
| Computed-dimension source | BC: Customer Invoice · posting date (characteristic = `posting date` **S**) | (from Metric 3) **N** |
| D365 dependency | `contract.canonical_contract.posting_date_field` column populated for relevant CC | **NOT BCF**; runtime prerequisite — see DEC-c3e57f Decision 9 + build plan §5.3 |

### Metric 7 — AR aging buckets

| Need | Concept | Status |
|---|---|---|
| Grain entity | Customer Invoice | (from Metric 1) **N** |
| Bucket-input date | BC: Customer Invoice · due date | (from Metric 2) **N** |
| Bucket-aggregate value | BC: Customer Invoice · outstanding amount | (from Metric 1) **N** |
| Bucket boundaries | `[0, 30, 60, 90, ∞]` (literal, not BCF) | n/a |

### Metric 8 — Discount-to-line-amount

| Need | Concept | Status |
|---|---|---|
| Grain entity | Sales Order Line | **A** (already active per B10a-S4 checklist line 31) |
| Variable I1 — value (discount) | BC: Sales Order Line · discount (characteristic = `discount` **S**) | **N** (createBusinessConcept; entity active, characteristic seeded) |
| Variable I2-a — value (unit price) | BC: Sales Order Line · unit price | **A** (already active per B10a-S4 checklist line 31) |
| Variable I2-b — value (ordered quantity) | BC: Sales Order Line · ordered quantity (characteristic = `ordered quantity` **S**) | **N** (createBusinessConcept; entity active, characteristic seeded) |
| Derived I2 = I2-a × I2-b | computed at MCF AST; no BCF asset | n/a |

### Metric 9 — MLS-14 self-collapse failure

| Need | Concept | Status |
|---|---|---|
| Grain entity | Customer Invoice | (from Metric 1) **N** |
| Variable I1 + I2 | BC: Customer Invoice · outstanding amount (same binding twice — deliberate substrate-identity collapse) | (from Metric 1) **N** — no additional BCF asset |

### Metric 10 — Stale fixture failure

| Need | Concept | Status |
|---|---|---|
| Reuses all of Metric 2 | (no additional BCF asset) | n/a |

### 5.x BCF-panel-decided characteristic ambiguity (operator surface)

Three characteristics are intent-load-bearing for Metrics 1, 3, 6 but are not in the F4-S1 24-approved list:

| Intent characteristic | F4-S1 status | Most relevant panel route |
|---|---|---|
| `outstanding amount` | DEFERRED at 2026-05-21 content-review lock as "aggregate / net position, not v1 raw characteristic; sits at metric / canonical layer; deferred to … carefully framed concept authored after Registry is live" (F4-S1 §6 decision 1) | F4-v2 `createCharacteristic` — high-risk; Vocabulary Admission Checklist routes to operator-confirm. The "carefully framed" wording from F4-S1 §6 is now load-bearing — operator + BCF panel decide whether to author this now, or to reframe Metric 1's variable bindings to compose from rawer characteristics (e.g. invoice amount minus payments received). |
| `recognized amount` / `billed amount` | NOT in F4-S1 list; not deferred (not previously considered) | F4-v2 `createCharacteristic` — likely `industry_specific` (finance) classification; routes to operator-confirm. Alternative: panel may reframe as a panel-judged composite of existing characteristics. |
| `invoice amount` | NOT in F4-S1 list (OAGIS has component `Invoice` but the field is composed, not atomic) | F4-v2 `createCharacteristic` — panel may decide this is a composite (unit price × ordered quantity summed over lines) rather than a primitive characteristic. |

**This ambiguity is the load-bearing operator decision Step 4 enrichment surfaces.** It is not blocking for Step 4 *planning*; it is blocking for Step 4 *execution* on Metrics 1, 3, 6 specifically. Metrics 2, 4, 5, 7, 8, 9, 10 are not affected (their BCs map to F4-S1-seeded characteristics).

**Operator decision (deferred to Step 4 enrichment session, not this preflight):**

- Option (a): Author `outstanding amount` and the two revenue-amount characteristics under F4-v2 operator-confirm path. The F4-S1 §6 deferral implicitly anticipated this.
- Option (b): Reframe the affected metrics to compose from rawer characteristics (e.g. `invoice amount = SUM(unit price × ordered quantity)` over Sales Order Line; `outstanding amount = invoice amount - sum of payments received`). This avoids new characteristic authoring at the cost of more complex MCF AST per metric.
- Option (c): Defer Metrics 1, 3, 6 to a Step-4-bis enrichment after the BCF panel reaches consensus on the characteristics question; ship Step 4 with Metrics 2, 4, 5, 7, 8, 9, 10 (7 of 10).

This decision is taken at Step 4 enrichment session opening, not here.

---

## 6. Consolidated BCF enrichment slice

### 6.1 Entities to author

| # | Entity name | Status | Required by metrics |
|---|---|---|---|
| 1 | Sales Order Line | **A** (active in Registry) | 8 |
| 2 | Customer Invoice | **N** (createEntity) | 1, 2, 3, 4, 5, 6, 7, 9, 10 |
| 3 | (third Entity — see §6.4) | **N** | — for ≥3 Entity coverage criterion |

### 6.2 Characteristics to author (new beyond F4-S1)

| # | Characteristic name | Why needed | Authoring path |
|---|---|---|---|
| 1 | `outstanding amount` (or alternative per §5.x option (b)) | Metric 1 + 2 + 7 value | F4-v2 — high-risk; operator-confirm required (revisit F4-S1 §6 decision 1) |
| 2 (conditional) | `recognized amount` | Metric 3 numerator | F4-v2 (defer if §5.x option (b) or (c) chosen) |
| 3 (conditional) | `billed amount` | Metric 3 denominator | F4-v2 (defer if §5.x option (b) or (c) chosen) |
| 4 (conditional) | `invoice amount` | Metric 6 value | F4-v2 (defer if §5.x option (b) or (c) chosen) |

**Minimum new characteristics:** 1 (`outstanding amount`, if option (a) chosen and Metrics 3 + 6 reframed per option (b)).
**Maximum new characteristics:** 4 (if option (a) chosen for all three intent characteristics).

### 6.3 Business concepts to author

Customer Invoice (8 BCs):

| # | BC name | Characteristic | Rep term | Role | Required by metrics |
|---|---|---|---|---|---|
| 1 | Customer Invoice · outstanding amount | `outstanding amount` (N) | amount | value | 1, 2, 7, 9 |
| 2 | Customer Invoice · due date | `due date` (S) | date | value | 2, 5, 7 |
| 3 | Customer Invoice · posting date | `posting date` (S) | date | value | 3, 5, 6 |
| 4 | Customer Invoice · status | `status` (S) | code | value | 4 |
| 5 | Customer Invoice · status change date / effective date | `effective date` (S) | date | value | 4 |
| 6 | Customer Invoice · invoice id | (panel decision; identifier-role) | identifier | identifier | 4 |
| 7 (conditional) | Customer Invoice · invoice amount | `invoice amount` (N) | amount | value | 6 — defers if §5.x option (b)/(c) chosen |
| 8 (conditional) | Customer Invoice · recognized revenue amount | `recognized amount` (N) | amount | value | 3 — defers if §5.x option (b)/(c) chosen |
| 9 (conditional) | Customer Invoice · billed amount | `billed amount` (N) | amount | value | 3 — defers if §5.x option (b)/(c) chosen |

Sales Order Line (3 BCs beyond existing `Unit Price`):

| # | BC name | Characteristic | Rep term | Role | Required by metrics |
|---|---|---|---|---|---|
| 10 | Sales Order Line · discount | `discount` (S) | amount | value | 8 |
| 11 | Sales Order Line · ordered quantity | `ordered quantity` (S) | quantity | value | 8 |
| 12 (negative test) | (intentionally-unreachable BC on a 3rd entity; see §6.4) | — | — | — | none — exists to confirm grain-reachability check refuses |

Plus the 1 already-active BC: `Sales Order Line · Unit Price` (A).

**BC count summary:**
- Minimum new BCs (Metrics 2 + 4 + 5 + 7 + 8 + 9 + 10 only; §5.x option (c)): 9 new BCs.
- Maximum new BCs (all 10 metrics, all conditional BCs authored; §5.x option (a)): 12 new BCs.
- Plus 1 already-active (Sales Order Line · Unit Price) and 1 negative-test BC.

**Aggregate slice size:** 9-12 BCs + 1-4 new Characteristics + 2 new Entities. Well below the BCF preflight's ~30-BC envelope.

### 6.4 Third Entity — negative-test placement

Per build plan §7.2 selection criteria (≥3 Entity families for cross-Entity reachability test) and per BCF preflight §6.5 (one negative-test case: a BC deliberately placed on an Entity unreachable from a representative metric's grain).

**Recommendation:** the third Entity is **the negative-test Entity itself**, not an additional happy-path Entity. Concretely, author a third Entity (e.g. "Employee" or "Vendor" — operator chooses) and author one BC on it (e.g. `Employee · employee id`) that is NOT reachable from Sales Order Line or Customer Invoice grains. This BC participates in no positive Metric 1-10; its purpose is to confirm that MCF Gate M11 / M12 + PE-MC-2 grain-coherence check refuses an attempted binding from a Customer-Invoice-grained metric.

This keeps the slice tight (3 Entity families: Sales Order Line + Customer Invoice + one negative-test Entity) while satisfying both criteria.

### 6.5 Representation-term coverage check (per BCF preflight §6.2)

| Rep term class | BC count in slice | Need ≥1? |
|---|---:|---|
| amount (currency) | 4 (outstanding amount, invoice amount, recognized amount, billed amount, discount, unit price) | ✓ |
| count | 1 (via aggregate; Metric 4 is COUNT, no separate count-BC needed) | ✓ |
| duration | 0 directly; Metric 5 derives `payment_posting_date - due_date` from two date-BCs | ⚠ acceptable — duration computed at MCF, no duration-typed BC in v1 slice |
| date | 4 (due date, posting date, effective date, status change date) | ✓ |
| identifier | 1 (invoice id) | ✓ |
| quantity | 1 (ordered quantity) | ✓ |

All representation-term classes required by the 10 metrics are covered. `duration`-typed BC is not in v1 slice because Metric 5 derives duration arithmetically from two date-BCs; if MCF Gate M7 v1 AST taxonomy requires a duration-typed BC for the `window` node, the panel may surface this as a slice gap (low-risk; one additional BC).

---

## 7. Existing BCF registry coverage vs gaps

### 7.1 Confirmed-active baseline (per shipped BCF docs)

| Asset | Status | Evidence |
|---|---|---|
| Entity: Sales Order Line | active | `business-concept-registry-b10a-s4-ui-readiness-checklist.md` line 31 |
| BusinessConcept: Sales Order Line · Unit Price | active | `business-concept-registry-b10a-s4-ui-readiness-checklist.md` line 31 |
| 15 representation terms (F2-seeded; FK-enforced) | seeded + active | `business-concept-registry-f4-s1-characteristic-seed-list.md` §4 representation-term-overlap check |
| 24 F4-S1 v1 characteristics (accepted 2026-05-21) | seeded; per-row lifecycle state needs live verification | `business-concept-registry-f4-s1-characteristic-seed-list.md` §3 |

### 7.2 Per-asset slice coverage assessment

| Slice asset | Coverage status |
|---|---|
| Entity: Sales Order Line | **covered** (active) |
| Entity: Customer Invoice | **gap** — must author via createEntity |
| Entity: third (negative-test) | **gap** — must author via createEntity |
| BC: Sales Order Line · Unit Price | **covered** (active) |
| BCs on Customer Invoice (6-9 BCs) | **gap** — must author via createBusinessConcept |
| BCs on Sales Order Line (discount, ordered quantity, negative-test BC) | **gap** — must author via createBusinessConcept |
| Characteristic: `due date` | **seeded (F4-S1)** — lifecycle activation verification needed before binding |
| Characteristic: `posting date` | **seeded (F4-S1)** — lifecycle activation verification needed before binding |
| Characteristic: `effective date` | **seeded (F4-S1)** — lifecycle activation verification needed before binding |
| Characteristic: `status` | **seeded (F4-S1)** — lifecycle activation verification needed before binding |
| Characteristic: `discount` | **seeded (F4-S1)** — lifecycle activation verification needed before binding |
| Characteristic: `ordered quantity` | **seeded (F4-S1)** — lifecycle activation verification needed before binding |
| Characteristic: `unit price` | **seeded (F4-S1)** — lifecycle activation verification needed before binding |
| Characteristic: `outstanding amount` | **gap** — F4-S1 §6 explicitly deferred; F4-v2 path required (operator-confirm) |
| Characteristics: `recognized amount` / `billed amount` / `invoice amount` | **gap** (conditional on §5.x decision) — F4-v2 path |

### 7.3 Lifecycle-state verification dependency

The F4-S1 24 characteristics were `accepted` 2026-05-21 in the seed-content artifact. Per `business-concept-registry-b10-publication-lifecycle-design.md` line 84, a `draft` characteristic is invisible to BCF binding (the `lead time` example) — activation is an operator-gated B10 step.

**Step 4 enrichment opens with a verification act**: confirm via live `concept_registry.characteristic` read (after authorizing the schema on bc-postgres allowlist per BCF preflight §7.1 / gap survey §2.5.4) which of the 24 F4-S1 characteristics are in `active` state today. The seven characteristics named in §7.2 above must be active before the Customer Invoice BCs that depend on them can be authored.

If any of the seven is still `draft`, that B10 activation is a Step 4 prerequisite act (operator-confirm-required per the B10 design).

### 7.4 What this enumeration does NOT do

- Does not enumerate live `concept_registry.entity` / `business_concept` / `characteristic` counts beyond what shipped BCF docs cite. The `concept_registry` schema remains outside this Claude session's bc-postgres allowlist (same constraint as gap survey Q4).
- Does not author or activate anything.
- Does not propose `lead time` activation (that characteristic is not in the 24 F4-S1 list and is not in the 10-metric slice).

---

## 8. BCF v1 packet sufficiency check against this slice

Per BCF enrichment preflight §4, the v1 bounded authoring-context packet is sufficient for the first-10-metric enrichment slice. Re-checked against this Step 4 slice:

### 8.1 Per-operation check

| Operation | Slice usage | v1 packet capacity per BCF preflight §3 | Sufficiency |
|---|---|---|---|
| `createEntity` | 2 new entities (Customer Invoice + negative-test third Entity) | Each createEntity packet carries candidate + `entityNameMatches` only; sufficient for fresh-name authoring | ✓ |
| `createBusinessConcept` | 9-12 new BCs across Customer Invoice + Sales Order Line + negative-test Entity | Each createBusinessConcept packet carries candidate + selected entity + existing-concepts-for-entity + entityPlacementCandidates + active-characteristics + representation-terms; sufficient for duplicate-detection within target entity and vocabulary validation | ✓ |
| `createCharacteristic` (F4-v2) | 1-4 new characteristics (`outstanding amount` definite; 3 conditional) | Each createCharacteristic packet carries candidate + active-characteristics + representation-terms; F4-v2 Vocabulary Admission Checklist routes to operator-confirm for non-`global` scopes; sufficient | ✓ |

### 8.2 Per-trigger check (against BCF preflight §5.1 hard triggers)

| Hard trigger | Slice exposure | Verdict |
|---|---|---|
| T-H1 (cross-entity disambiguation load-bearing) | Customer Invoice BCs are clearly per-entity (no plausible Sales Order Line placement for `outstanding amount`); Sales Order Line BCs are clearly per-line (no plausible Customer Invoice placement) | **NOT TRIGGERED** |
| T-H2 (source-reality grounding PE-MC-1-mandatory for the BC class) | Step 4 enrichment proceeds with operator-supplied candidate evidence per BC; no class-wide source-reality mandate proposed | **NOT TRIGGERED** |
| T-H3 (active characteristic vocabulary >50 × full-active-list wire bloat) | 24 + 4 = 28 characteristics worst-case after slice; well under threshold | **NOT TRIGGERED** |
| T-H4 (bc-ai acquires free-query tool to Registry) | No proposal to break L1 lock in this slice | **NOT TRIGGERED** |

### 8.3 Per-trigger check (against BCF preflight §5.2 soft triggers)

| Soft trigger | Slice exposure | Verdict |
|---|---|---|
| T-S1 (per-agent transcripts become audit requirement) | No such requirement raised in this slice | not triggered |
| T-S2 (workbench fingerprint regulatory/operational requirement) | Not surfaced | not triggered |
| T-S3 (packet as audit-review unit) | v1 input-hash discipline still sufficient | not triggered |
| T-S4 (MCF Gate M12 panel authored, BCF/MCF divergence inconvenient) | Step 4 is pre-M12; not yet relevant | not triggered |

### 8.4 Verdict

**BCF v1 bounded packet is sufficient for the Step 4 enrichment slice as enumerated in §6.** No B6-v2 workbench retrofit is required to open Step 4 enrichment.

---

## 9. Risks and stop conditions

### 9.1 Slice-internal risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-A | `outstanding amount` characteristic explicitly deferred per F4-S1 §6 (2026-05-21 decision); authoring now needs an explicit operator decision to reverse / refine the deferral rationale | High (load-bearing for Metrics 1, 2, 7, 9, 10) | §5.x options (a) / (b) / (c) — operator chooses at Step 4 enrichment session opening |
| R-B | F4-S1 24 characteristics' per-row lifecycle state may be `draft` rather than `active` (BC binding requires active) | Medium (blocks BC authoring on dependent characteristics) | First Step 4 enrichment act: bc-postgres allowlist expansion to include `concept_registry`; live verify; B10 activation as prerequisite if any of the 7 needed chars is draft |
| R-C | `invoice id` representation-term + characteristic choice is ambiguous (could be `identifier` rep-term with a panel-judged characteristic, or could be `line number` characteristic if document-position semantics applies) | Low (Metric 4 only) | Panel decision at createBusinessConcept time |
| R-D | Metric 6 (fiscal_period) depends on D365 `posting_date_field` landing on `contract.canonical_contract`; not currently present (gap survey Q-7) | Medium for Metric 6 only | Per DEC-c3e57f Decision 9 + build plan §5.3: M20 fiscal-period metric defers if D365 not landed; substitute another metric class (e.g. a second windowed or bucket-assign) |
| R-E | Negative-test Entity choice (§6.4) may inadvertently overlap with operationally-meaningful future Entity authoring; "Employee" or "Vendor" name collisions later | Low | Operator names the negative-test Entity with a deliberately-non-collisional name (e.g. `Test Negative Entity` with explicit definition stating its non-binding role); alternatively pick a non-business Entity name |
| R-F | `recognized amount` / `billed amount` / `invoice amount` may be deemed `industry_specific` rather than `global` by F4-v2 Vocabulary Admission Checklist, routing to operator-confirm and slowing Step 4 | Medium | Operator anticipates the routing; §5.x option (b) (compose from rawer characteristics) avoids if needed |

### 9.2 Hard triggers that would stop Step 4 enrichment mid-flight

Carried from BCF preflight §5.1; restated as Step-4-active stop conditions:

| # | Trigger | Step 4 stop action |
|---|---|---|
| T-H1 | Cross-entity disambiguation becomes load-bearing for a candidate | Stop enrichment; open B6-v2 retrofit before next concept |
| T-H2 | Source-reality grounding becomes PE-MC-1-mandatory for a class | Stop; open B6-v2 |
| T-H3 | Active characteristic vocabulary exceeds wire-size threshold | Stop; open B6-v2 |
| T-H4 | bc-ai acquires free-query Registry tool | Stop; open B6-v2 |

If any T-H trigger fires during Step 4 enrichment, **stop enrichment and open B6-v2 retrofit** before continuing. None is expected for this slice (per §8.2).

### 9.3 Step 4 enrichment ordering risks (sequence-dependent)

| # | Risk | Mitigation |
|---|---|---|
| O-1 | Customer Invoice Entity authored before required characteristics are active → BC authoring blocked at variable-binding time | Phase A (Entities) → Phase B (Characteristics, including activations) → Phase C (BCs), per BCF preflight §6.7 |
| O-2 | Negative-test Entity authored before happy-path enrichment lands → operator confusion about purpose | Author negative-test Entity last (after the 9-12 happy-path BCs are in place), with explicit definition noting its negative-test role |

### 9.4 What this preflight explicitly does NOT recommend

- Does **not** recommend opening MCF M3.
- Does **not** recommend applying MCF M2 DDL.
- Does **not** recommend opening B6-v2 retrofit (no hard trigger fires).
- Does **not** recommend skipping the Phase A → B → C order at Step 4 enrichment time.

---

## 10. Recommended next gate

### 10.1 Immediate next: Step 4 enrichment session (opener)

Step 4 enrichment session opens with **two acts before any panel run**:

1. **bc-postgres allowlist expansion** to include `concept_registry` schema. This is the BCF Registry read authorization called out in BCF preflight §7.1 / gap survey §2.5.4 / M0 §9 item 5. Until landed, Step 4 enrichment cannot verify per-row characteristic lifecycle state (R-B above).
2. **Operator decision on §5.x** (`outstanding amount` characteristic deferral revisit; options a / b / c). The decision shapes which BCs Step 4 authors and which (if any) characteristics need F4-v2 createCharacteristic runs.

Once both are landed, Step 4 enrichment proceeds per BCF preflight §6.7 phase order:

- Phase A: createEntity for Customer Invoice + negative-test Entity (2 panel runs).
- Phase B: F4-v2 createCharacteristic for `outstanding amount` (+ conditional 3 more depending on §5.x), plus B10 activation of any F4-S1 characteristic still in `draft` state (one B10 act per characteristic).
- Phase C: createBusinessConcept for 9-12 BCs (one panel run each).
- Phase D: acceptance check per BCF preflight §6.7 D criteria.

### 10.2 What follows Step 4

When Step 4 enrichment lands and the acceptance check passes:

- **MCF Gate M20 (first representative metric re-authoring program)** is the operational gate that authors the 10 MCs from §4 above under MCF. M20 depends on MCF Gates M2-M19 having shipped (per build plan §4). M20 cannot open until the full MCF substrate + services + console land.
- The MCF intermediate gates (M2-M19, except M15-M16-M20 which are BCF-density-dependent per gap survey §2.5) can proceed in parallel with Step 4 enrichment — as flagged in build plan §5.2 (Track 1 substrate + Track 2 services + Track 3 BCF enrichment converge at M17 + M18 + M20).

### 10.3 What stays closed after this Step 4 doc commits

- **MCF M3**: stays closed per operator instruction.
- **MCF M2 DDL apply**: stays closed per operator instruction; CLAUDE.md Database Change Protocol applies.
- **BCF B6-v2 retrofit**: stays closed; no hard trigger fired in this slice per §8.2.
- **Step 4 enrichment itself**: stays closed until operator authorizes a Step 4 enrichment session.

---

## Document verification

- **All 10 required sections present** (§1 Scope and grounding; §2 Selection method; §3 Candidate reservoir evidence; §4 The selected 10 metrics; §5 Per-metric BCF enrichment needs; §6 Consolidated BCF enrichment slice; §7 Existing BCF registry coverage vs gaps; §8 BCF v1 packet sufficiency check; §9 Risks and stop conditions; §10 Recommended next gate).
- **Discipline assertions (§1.4) all hold:** candidate-intent only; no `co_bindings` / BF / BO / CF / CM authority; no legacy SQL MC migration; slice ≤ BCF v1 packet capacity (per §8).
- **All 10 metrics traceable** to either a `bc_seed.seed_metrics` candidate row + provenance tag (Metrics 1-8) or to a deliberate-construction class per build plan §7.1 (Metrics 9, 10).
- **BCF slice scope documented**: 2 new Entities + 9-12 new BCs + 1-4 new Characteristics across 3 Entity families, well within BCF preflight ~30-BC envelope.
- **No code changes, no DDL, no DB writes.** All reads were read-only (Mongo `bc_seed.seed_metrics` + Postgres `metric.metric_definition` distribution).
- **Read-only script** (`bc-seed/tmp/mcf-step4-seed-pool.mjs`) is local-only, not authored into bc-seed proper; evidence for §3 lives in this doc.
- **No MCF M3 opened. No MCF M2 DDL applied. No B6-v2 retrofit opened. No BCF enrichment performed.**
