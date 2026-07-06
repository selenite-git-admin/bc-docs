---
id: apex-cfo-pack-demo-readiness-triage
order: 81
title: "Apex CFO Pack Demo-Readiness Triage"
status: draft
authority: reference
depends_on: [demo-operations, demo-plan-cfo-pack-storyboard, metric-readiness-toolkit]
governing_sources:
  - CFO Pack Demo Storyboard (locked)
  - Metric Workstream Playbook
  - DSO Metric Work Record (2026-05-11)
  - ADR-c012c0 (DEC-c012c0 / D400) — Metric Contract grammar v1.1
  - Readiness Toolkit (D394 / D397)
governing_adrs:
  - DEC-c012c0 (D400 — Metric Contract grammar v1.1)
  - DEC-1db1c7 (D401 — Open-item / as-of canonical semantics)
  - DEC-28b176 (D394 — Metric Readiness Model)
  - DEC-a8b33e (D397 — Metric Lifecycle Funnel)
  - DEC-bebaec (D305 — Chain Completeness SSOT)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Apex CFO Pack Demo-Readiness Triage

This is an **orientation triage**, not authority. It surveys the locked
storyboard against the platform's current state to surface honestly-demoable
tiles, reframable tiles, and tiles gated on Foundation-side work. The
storyboard's authority is unchanged; this document is a working note for
the demo-readiness conversation.

If this triage conflicts with the locked storyboard, the storyboard wins
and this document is corrected.

## Scope

The locked CFO Pack storyboard
([demo-plan-cfo-pack-storyboard.md](../operating-model/demo-plan-cfo-pack-storyboard.md))
defines:

- **36 hero KPIs** (25 Tier-A + 11 Tier-B) across 10 KPI groups.
- **40 Q&A scenarios** across 5 role lenses (Meera, Anil, Suresh, Pradeep, Rajesh) plus 3 treasury-angle add-ons (M9–M11).
- **8 coherence assertions** that must tie out for the "numbers settle" claim.
- **7 embedded story events** (MetroLink, Plating overrun, xPress same-party, after-hours JE, close-day-7, MSME exposure, Q3 results beat).

This triage classifies each of the above as **GREEN / AMBER / RED** and names the blocker for every RED.

## Triage axes

A line item is **GREEN** when all four are true:

1. **Tenant data exists** — bc-sdg has emitted, or a real-tenant binding holds, data in the shape the scenario needs.
2. **Metric authored and producing** — the relevant MC is at Stage 7 (Live) per the D397 ladder (or, for non-metric scenarios, the relevant reader/connector emits the signal).
3. **Semantic honesty holds** — what the scenario *claims* matches what the metric/reader *honestly computes*. No DSO-shaped overclaiming.
4. **UI surface exists** — the bc-portal Beyond canvas, LHS tile, drag-and-narrate, or Trust Chain drill renders the scenario.

**AMBER** = a rename or reframe converts the scenario to GREEN without touching code/contracts. (Example: relabel "DSO" tile as "Collection Pressure.")

**RED** = at least one of the four conditions fails and a non-trivial Foundation-side gate must land first.

## Platform state snapshot (read 2026-05-11 via Readiness Toolkit)

| Dial | Value | Notes |
|---|---|---|
| Catalog `totalMcs` (Stage 3 Active) | 376 | |
| Catalog `chainComplete` | 176 | 46.8% of active |
| Catalog `formulaSupported` | 360 | 95.7% — formula-shape mostly clean |
| Catalog `ready` (Stage 4 Platform Ready) | **163** | 43.4% of active |
| Chain status (SSOT, all MCs) | 539 total / 228 complete / 311 partial | Per `contract.chain_status` |
| **`apex` tenant dial** (canonical slug) | **bound 148 / producing 31 / wouldProduceIfBound 0** | Apex demo substrate is alive and producing. |
| `apex-motors` route response | **500** | Alias / readiness-surface mismatch, NOT tenant absence. See correction note. |
| `apex` formula-token audit | 376 MCs / **27 clean** / 349 broken (415 null_in_tenant, 134 type_mismatch, 2 no_mapping) | Most authoring is intact; null_in_tenant dominates → SDG-emission gap is the leading repair class. |
| `apex` readiness ledger | 79 metric_snapshot rows (546 records) / 2 reader_run (76) / 4 resolution (149); latest 2026-05-10 23:48 UTC | Substrate has live runs, recent activity. |
| `mc__days_sales_outstanding` | versions 1.0.0 / 1.1.0 / 1.2.0 all `governance_state_code = active` on `accounts_receivable` subfunction; audit_status_code = `warn` | DSO v1.2.0 exists and is live; the "warn" audit state is consistent with the semantic envelope captured in the DSO MWR. |
| `sandbox1` tenant dial | bound 20 / producing 13 | Separate pilot; not the Apex demo substrate. |

### Correction — Apex tenant identity

A prior version of this triage stated *"No Apex tenant exists — `apex-motors` returns 500"*. **That finding was wrong.** The canonical Apex tenant slug is **`apex`** (tenant DB `tbc_apex_dev`); prior sessions proved invoice + AR + DSO chains under that slug. The 500 on `apex-motors` is an alias / readiness-surface mismatch — `apex-motors` is the storyboard's display name (and possibly the bc-sdg profile name), not the platform tenant slug. The platform readiness API does not register that alias.

**Headline finding (corrected):** Apex demo substrate is alive (148 bound, 31 producing, 79 recent metric snapshots, DSO live). The storyboard is **not** uniformly RED because of tenant absence. The real blocker mix is a combination of: SDG emission-shape gaps (null_in_tenant — 415 broken tokens, the largest reason class), authoring-shape gaps (type_mismatch — 134), demo-safe labeling work (DSO → Collection Pressure and similar reframes), metric semantic gaps where ADR-c012c0's successor work is required (DSO/DPO/DIO realistic / CCC tie-out), UI/read-model gaps (Trust Chain, role-based LHS panels, drag-and-narrate), and a small but operationally-relevant tenant alias / readiness endpoint mismatch (the `apex-motors` 500). The reclassification flows through Sections 1–7 below.

## Section 1 — Hero KPI tiles (Tier-A, 25 items)

Reclassified after Apex-substrate verification. **B1 is no longer "tenant not provisioned"**; it now means **"`apex` tenant exists, but the specific MC is not yet producing for it — null_in_tenant or unmapped binding on the relevant CF"**. See §6 for the corrected blocker taxonomy.

| Group | KPI | Class | Demo-safe label / reframe | Blocker if AMBER/RED |
|---|---|---|---|---|
| Revenue & Profitability | Total Revenue | RED | — | B1a — `total_revenue` is the **top broken CF for apex (19 MCs null_in_tenant)**; reader/CC mapping or SDG emission gap. Quickest win class. |
| Revenue & Profitability | Revenue Growth Rate | RED | — | B1a (depends on total_revenue) + B4 (likely needs trailing-window grammar v1.1 once it ships) |
| Revenue & Profitability | Gross Profit Margin | RED | — | B1a + B4 |
| Revenue & Profitability | Variance to Budget/Forecast | RED | — | B1a + B7 — needs budget/forecast feed (no budget reader today) |
| Revenue & Profitability | Operating Profit Margin | RED | — | B1a + B4 |
| Liquidity & Working Capital | Current Ratio | RED | — | B1a + B4; balance-sheet snapshot semantics required (asset/liability open-position families) |
| Liquidity & Working Capital | Quick Ratio | RED | — | B1a + B4 |
| Liquidity & Working Capital | DSO | **AMBER → demo-safe** | Tile renamed **"Collection Pressure"** / sub-label **"Receivables Coverage (period view)"**. v1.2.0 active and producing under `apex` (audit `warn`); semantics honest only as a same-period coverage indicator. | B2 — realistic-DSO gated on successor open-item/as-of ADR + DSO v2.0.0. DSO MWR Demo Positioning applies. |
| Liquidity & Working Capital | DPO | RED | — | B2-mirror — same balance-side honesty gap on the AP side; needs successor open-item ADR + DPO v2 |
| Liquidity & Working Capital | Cash Conversion Cycle (CCC) | **RED — defer** | Drop CCC tile + identity claim from this demo cycle | B2 + B2-mirror + DIO equivalent; CCC tie-out depends on DSO v2 + DPO v2 + DIO v2 with consistent open-item semantics |
| AR Performance | Total Outstanding AR | **AMBER (likely producing)** | Show as "Total Receivables (period close)" — verify whether the existing producing MC is honest as a closing-balance read. | B5 — verify which AR balance MC under `accounts_receivable` is currently producing for `apex` (3 of 22 subfunction MCs are clean per audit); decide rename + position. |
| AR Performance | Overdue Receivables % | **AMBER → AMBER-with-SDG** | Honest iff SDG (or actual CC) carries open-AR snapshot with `aging_bucket`. `accounts_receivable` subfunction has 3 clean MCs; verify whether one is an overdue % already. | B1a / B1b — confirm presence of aging signal; bind if MC exists but unbound; author if not. |
| AR Performance | AR Aging Analysis (incl. weighted-average) | **AMBER → AMBER-with-SDG** | Same as above. Critical for M3 reframe — see §4. | B1a / B1b — verify aging signal in `apex` CC layer; the audit's `null_in_tenant` count for AR fields will indicate. |
| AR Performance | Top 10 Overdue Customers | AMBER → AMBER-with-SDG | Customer-grouped open AR. | B1a / B1b — verify customer-segment attribute in `apex` substrate |
| AP Performance | Total Outstanding AP | AMBER → AMBER-with-SDG | Mirror of Total Outstanding AR. AP subfunction has 2 clean MCs of 76 — most accounts_payable work is broken. | B1a — `accounts_payable` subfunction has dominant null_in_tenant; AP reader/CC emission gap |
| AP Performance | AP Aging Analysis | RED → AMBER-with-SDG | Mirror of AR Aging | B1a |
| AP Performance | Early Payment Discounts Captured | RED | — | B1a + B4 |
| AP Performance | MSME Compliance % | RED | — | B1a + B4 + B7; India-specific. SDG must emit MSME-tagged vendor records and 45-day aging signal. |
| Cost Accounting | Cost of Goods Sold | RED | — | B1a + B4 |
| Cost Accounting | Variance from Standard Cost | RED | — | B1a + B4; also requires standard-cost reference data |
| Cost Accounting | Cost Center Efficiency | RED | — | B1a + B4 |
| Anomaly & Alerts | Same Party AR/AP | RED | — | B6 — anomaly-detection MC family and its evidence-shape grammar not in current scope |
| Anomaly & Alerts | After-Hours Transactions | RED | — | B6 + B7 — posting-time-of-day signal needed in canonical layer; reader-side enrichment |
| Anomaly & Alerts | Duplicate Vendor Payments | RED | — | B6 |
| Finance Ops Readiness | Group Consolidation Days | RED | — | B1a + B4 |
| Finance Ops Readiness | Reconciliation Status | RED | — | B1a + B4 |
| Finance Ops Readiness | JE Backlog | RED | — | B1a + B4 + B7 (JE-workflow signal upstream) |

**Tier-A subtotals (corrected):** 1 AMBER demo-safe today (DSO → Collection Pressure with semantic guardrails). **6 AMBER conditional on Apex AR/AP emission-shape verification** (Total Outstanding AR, Overdue %, AR Aging, Top 10 Overdue, Total Outstanding AP, AP Aging) — these may already be producing for `apex` and need a verification + rename pass, not net-new SDG profile work. **18 RED** — mostly B1a (`null_in_tenant`) plus B2/B4/B6/B7 layered dependencies.

## Section 2 — Tier-B background tiles (11 items)

Tier-B classification is unchanged in pattern: most items are **RED** because the relevant MCs are either not authored or have null_in_tenant on Apex. None of them are *demo-safe today*; several become AMBER once the upstream CF audit is repaired (B1a → bind) or the relevant MC is authored (B4). Two specific items keep their structural blockers:

- **Outside Working Hours Transactions** — anomaly-detection family (B6) plus posting-time-of-day signal (B7).
- **Forecast vs Actual variance metrics** — require a budget/forecast reader (B7) not currently in scope.

## Section 3 — Q&A scenarios (40 + 3 treasury = 43)

Classified by primary blocker. Detail tables follow for each role.

### Meera (Group CFO) — 11 scenarios (M1–M11)

| # | Mode | Topic | Class | Notes |
|---|---|---|---|---|
| M1 | T | "Attention this week" — 3-item Rooth answer | RED | Multi-source synthesis (AR + cost variance + anomaly); requires all three streams live |
| M2 | T | Quarterly guidance tracking | RED | Needs forecast feed + group consolidation |
| M3 | **D** | **Drag DSO tile, narrate 47/38** | **RED — reframe required** | See §4 for the full M3 reframe |
| M4 | T | Close pending | RED | Needs consolidation + reconciliation + JE-backlog signals |
| M5 | T | GST input credit reconciliation | RED | India-specific; no GST reader |
| M6 | D | Drag Anomaly badge | RED | Anomaly metric family not authored |
| M7 | T | Audit-committee readiness | RED | Composite narrative; depends on M1–M6 |
| M8 | T | "Anything I should know" — MSME flag | RED | MSME compliance signal not authored |
| M9 | D | Drag Working Capital tile | RED | Working-capital snapshot + drivers |
| M10 | T | FX exposure | RED | FX reader + hedge book; not in scope |
| M11 | T | NBFC capital adequacy | RED | NBFC-specific signals; out of current chain |

**Meera subtotal:** 0 GREEN, 0 AMBER, 11 RED.

### Anil (Head of Receivables) — 8 scenarios (A1–A8)

| # | Mode | Topic | Class | Notes |
|---|---|---|---|---|
| A1 | T | "Who's overdue today" — top 5 | RED → AMBER-with-SDG | Honest iff SDG emits an open-AR-with-aging snapshot |
| A2 | D | Drag Top 10 Overdue | RED → AMBER-with-SDG | Same as A1 |
| A3 | H | MetroLink customer + "what's the latest" | RED | Requires per-customer historical + dispute-cycle signals; SDG must emit dispute events; UI requires customer drill |
| A4 | T | Largest collection due this week | RED → AMBER-with-SDG | Needs payment-due-date signal in the open-AR snapshot |
| A5 | T | Dealer credit holds | RED | Credit-hold flag is not a current canonical concept; new reader/CC scope |
| A6 | T | Collected this month vs target | RED | Needs collection-target reference data + payments stream |
| A7 | T | Disputes nearing 90 days | RED | Dispute lifecycle reader/CC not in current scope |
| A8 | T | Fleet vs dealer aging | RED → AMBER-with-SDG | If SDG emits the customer-segment attribute alongside open AR, aging WA per segment is honest. |

**Anil subtotal:** 0 GREEN, 0 AMBER unconditionally; **5 RED → AMBER conditional on bc-sdg Apex emission shape**, **3 unconditionally RED** (A3, A5, A6, A7 require canonical/reader scope beyond AR snapshots).

### Suresh (Head of Vendor Management) — 8 scenarios (S1–S8)

| # | Mode | Topic | Class | Notes |
|---|---|---|---|---|
| S1 | T | Due to vendors this week | RED → AMBER-with-SDG | Honest iff SDG emits AP-with-due-date snapshot |
| S2 | T | MSME 45-day approaching | RED | MSME flag + 45-day rule = India-specific business rule; needs reader + MC |
| S3 | D | Drag xPress vendor tile | RED | Cross-BU same-party flag = anomaly metric (B6) |
| S4 | T | Early-pay discounts missed | RED | Discount-terms reader not present |
| S5 | T | GST input credit | RED | GST reader not present |
| S6 | T | Vendor disputes | RED | Dispute lifecycle CC not present |
| S7 | T | TDS reconciliation | RED | TDS reader not present |
| S8 | T | Rentals/utilities/insurance | RED | Lease/utility reader not present |

**Suresh subtotal:** 0 GREEN, 0 AMBER unconditionally; **1 RED → AMBER conditional on SDG (S1)**, **7 unconditionally RED**.

### Pradeep (Head of Internal Audit) — 8 scenarios (P1–P8)

All eight scenarios depend on **B6 (anomaly-detection metric family)**, **B7 (posting-time-of-day enrichment in reader/CC)**, and **B5 (Trust Chain UI with source-ID drill for P6)**. None of these are in scope of the current grammar or canonical-contract families. **0 GREEN, 0 AMBER, 8 RED.**

### Rajesh (Plant CFO 1100) — 8 scenarios (R1–R8)

All eight depend on **plant + cost-center canonical contracts**, **standard-cost reference data**, **production-efficiency reader (MES or equivalent)**, and **3-way-match signal**. These are plausible canonical extensions but none are in current scope. **0 GREEN, 0 AMBER, 8 RED.**

### Scenario summary

| Role | GREEN | AMBER (rename only) | AMBER (conditional on Phase 1 SDG emission shape) | RED unconditionally |
|---|---|---|---|---|
| Meera (11) | 0 | 0 | 0 | 11 |
| Anil (8) | 0 | 0 | 5 | 3 |
| Suresh (8) | 0 | 0 | 1 | 7 |
| Pradeep (8) | 0 | 0 | 0 | 8 |
| Rajesh (8) | 0 | 0 | 0 | 8 |
| **Total (43)** | **0** | **0** | **6** | **37** |

## Section 4 — DSO / M3 deep dive

Aligned with the uncommitted **Demo Positioning** subsection in the DSO MWR.

### What the storyboard claims for M3

> *"DSO is 47 days, up from 38 in Q2. State transport corporations + corporate fleets drive 71% of the increase: MetroLink ₹15 Cr (8 weeks), HighMile Logistics ₹4 Cr (5 weeks), CityRide Mobility ₹3 Cr (4 weeks). Dealer DSO stable at 22 days."*

### Why M3 cannot be delivered as written

1. **"DSO is 47 days" is not honestly computable from v1.2.0.** Same-period-AR / same-period-credit-sales × 30 is structurally capped at 30–38 days. Even with Apex tenant data, the metric ceiling forbids the number.
2. **"Up from 38 in Q2" implies period-over-period DSO trend interpretation.** v1.2.0 deltas reflect within-period AR/sales-ratio drift, not the collection-cycle change the term implies. Forbidden claim per the MWR.
3. **"Dealer DSO 22 days" implies per-segment DSO computation.** v1.2.0 does not segment by customer type; no segment-aware variable selector exists in grammar v1.0 or v1.1.
4. **"State transport corporations + corporate fleets drive 71% of the increase" is causal attribution** — needs per-segment trend decomposition. Out of scope for any current metric.

### Can AR Aging Weighted Average honestly support "47 up from 38"?

**Status reclassified: verification-pending, not unconditionally blocked.** The Apex substrate is alive (3 of 22 `accounts_receivable` subfunction MCs are audit-clean for `apex`; 79 metric_snapshot rows for `apex` since 2026-05-09). The honest answer depends on:

- Whether one of the producing AR MCs already carries an aging signal that the storyboard's M3 narrative can ride on (rename + position task, not new SDG profile work).
- If not, whether the existing `apex` invoice + AR reader chain already emits aging-bucket information at the CC layer, in which case an MC authoring pass closes the gap.
- Only if both checks come up empty does the gap reduce to a bc-sdg emission-shape question — author or extend an open-AR snapshot emission with aging metadata.

**Verification action (read-only, before commit):** inspect `accounts_receivable` subfunction's 3 clean MCs and the broken-CF list under `apex` to determine which case applies. Tools: `devhub_formula_token_audit` (already run for this triage), bc-admin Tenant Metrics drill, or `pg_query` against the `apex` CC fact tables once that schema is in the allowlist.

**Phase-1 SDG emission contract recommendation (still applies if verification reveals a gap):** open-AR snapshot + posting-date metadata + customer-segment tag — normal ERP-export shape, within bc-sdg scope. Unblocks AR Aging WA, Top-10 Overdue, Overdue %, and segment-aware aging — without touching DSO grammar.

### M3 narratives, ranked by honesty

| Option | Demo-safe? | Notes |
|---|---|---|
| (a) "DSO is 47 days, up from 38 in Q2" with DSO tile renamed Collection Pressure | **No** — the tile-and-narration mismatch is obvious to a CFO | Reject |
| (b) Drag **AR Aging Weighted Average** tile, narrate "*Receivables aging weighted average is 47 days, up from 38 in Q2. Fleet customers drive the increase.*" | **Yes — if Phase 1 SDG emits open-AR-with-aging** | **Recommended.** Same operational signal (collection-cycle drift). No mention of DSO. Customer-segment attribution is honest if SDG emits the segment tag. |
| (c) Drag the renamed **Collection Pressure** tile, narrate "*Collection pressure has tightened this quarter — fleet customers are driving the receivables stretch. Anil has the customer-by-customer escalation queue.*" | Yes (defensive fallback) | Loses the "47/38" anchor number but keeps the M3 drag-first moment |
| (d) Skip M3 entirely | Yes (most defensive) | Loses a centerpiece moment; not recommended |

**Primary recommendation:** option (b), conditional on bc-sdg Apex AR-emission shape including open-AR snapshot + aging metadata + customer segment.
**Fallback:** option (c), unconditional on SDG shape.

### CCC

CCC = DSO + DIO − DPO. With DSO RED (semantic gap), DPO RED (mirror gap), and DIO not even discussed in current scope, the CCC tile and the §9 coherence assertion *"CCC visible on tile = DSO + DIO − DPO"* cannot tie out. **Drop CCC from this demo cycle.** Re-introduce after the successor open-item ADR lands and DSO v2 / DPO v2 / DIO v2 are authored with consistent semantics.

## Section 5 — Coherence assertions (storyboard §9, 8 items)

| # | Assertion | Class | Notes |
|---|---|---|---|
| 1 | MetroLink overdue ₹15 Cr = sum of unpaid AR open items at demo date | RED → AMBER-with-SDG | Honest if bc-sdg Apex emits open-AR snapshot with customer grouping |
| 2 | CCC visible on tile = DSO + DIO − DPO | **RED — defer this demo cycle** | Drop CCC tile; see §4 |
| 3 | xPress same-party net ₹1.6 Cr = vendor − NBFC loan | RED | Anomaly + cross-BU computation; B6 |
| 4 | Plant 1100 Plating variance ₹14 Cr reflected in Plant 1100 COGS | RED | Cost-center + COGS metric authoring |
| 5 | Q3 revenue group = sum of BU1..BU5 FX-translated | RED → AMBER-with-SDG | Honest if SDG emits BU-level postings with company-code + currency tags and an FX-rate reference |
| 6 | MSME exposure ₹40 Cr = sum of unpaid invoices to MSME vendors aged 35–44 days | RED | MSME flag + aging on AP side |
| 7 | Period GLT0 at group = sum of detail postings (BSEG) | RED → AMBER-with-SDG | Honest if SDG emits both header and line-level postings reconciled |
| 8 | Forecast accuracy 95.8% = computed from actual vs forecast | RED | Forecast feed not present |

**Coherence summary:** **0 GREEN, 0 AMBER (rename only), 3 RED → AMBER-with-SDG, 5 RED unconditionally** (1 explicitly deferred — CCC).

## Section 6 — Blocker taxonomy (corrected)

The original taxonomy collapsed "Apex tenant does not exist" into a single B1. The corrected taxonomy splits the dominant blocker class — `null_in_tenant` — into upstream-emission vs binding-state subclasses, and adds the alias-mismatch operational blocker that prompted this correction.

| Code | Blocker | Items affected | Owner / next step |
|---|---|---|---|
| **B0** | Tenant-alias / readiness-route mismatch (`apex-motors` returns 500; canonical slug is `apex`) | Operational: anyone who tries to drive the demo via the storyboard's display name. The error masks substrate readiness. | bc-core: decide whether to register `apex-motors` as an alias or document `apex` as the canonical slug. Quick operational fix. |
| **B1a** | `null_in_tenant` on a specific CF for `apex` — upstream source-data emission gap (CC mapping points at a BF whose column is all-null in Apex's CC fact table) | 415 broken tokens (dominant reason class). Top: `total_revenue` (19 MCs), `operating_cash_flow` (11), `total_payments_count` (7). | Per-CF reader/CC audit; either repoint mapping to a populated BF or extend the reader/SDG emission to populate the BF. |
| **B1b** | Tenant binding missing for an MC that IS audit-clean on `apex` | `wouldProduceIfBound = 0` today (no audit-clean unbound MCs), but as `null_in_tenant` is repaired CF-by-CF, MCs flip to audit-clean and need binding via `devhub_tenant_bind_metrics`. | Curated bind under D268 DB Change Protocol. |
| **B2** | Realistic balance-side metrics (DSO numerator + mirrors); CCC tie-out | DSO honestly-as-DSO; DPO; AR Aging *if forced through append-only CC*; CCC | Successor open-item / as-of ADR (named in ADR-c012c0); pick one of the three candidate mechanisms. |
| **B3** | Grammar v1.1 engine implementation | Phase-1 flow-only pilot metric (not in storyboard); future trailing-window metrics | Stage 2 of ADR-c012c0 (separate operator approval); DSO v2 still gated on B2. |
| **B4** | Metric Contract authoring gap (MC not yet authored, or authored at wrong grain/formula) | type_mismatch class (134) + missing MCs across cost-accounting, finance-ops-readiness, MSME, fx/treasury | Per-MC authoring per playbook §3 Metric Work Sequence. |
| **B5** | bc-portal UI — Beyond canvas + role-based LHS panels + drag-narrate + Trust Chain drill | Every drag-first scenario (M3, M6, M9, A2, A3, S3, P1, P6, R2) | bc-portal three-surface split (DEC-6cdceb / D361) + Trust Chain implementation. |
| **B6** | Anomaly-detection metric family (same-party, after-hours, duplicates) | All P series + M6 + Anomaly & Alerts tile group | New metric/evaluator family; distinct from balance-vs-flow conversation. |
| **B7** | Reader/connector gaps for non-finance signals or non-emitted finance signals | India-specific (GST, TDS, MSME 45-day rule); production-efficiency; 3-way match; FX/treasury; budget/forecast feed | Source registration + AC/OC/CC authoring per onboarding chain. |
| **B8** | Automated coherence test suite | Locked storyboard decision #5; all 8 coherence assertions | Test-harness scope; design unscoped today. |

**Distribution shift after correction:** the `null_in_tenant` cleanup queue (B1a) replaces the catch-all "tenant not provisioned." That queue is per-CF and per-tenant; the top three CFs (`total_revenue`, `operating_cash_flow`, `total_payments_count`) collectively account for 37 of the 415 broken tokens and are concrete, addressable units of work — not a Phase-1-blocking unknown.

## Section 7 — Summary counts (corrected)

### Tiles (Tier-A + Tier-B, 36 total)

| Class | Count | Notes |
|---|---|---|
| GREEN (demo-safe as-is) | 0 | |
| AMBER (rename + position fix only — demo-safe today) | **1** | DSO → "Collection Pressure" with semantic guardrails (DSO MWR Demo Positioning) |
| AMBER pending verification (likely producing under `apex`; needs check + rename + position decision) | **6** | Total Outstanding AR / Overdue % / AR Aging / Top 10 Overdue / Total Outstanding AP / AP Aging |
| RED (B1a — `null_in_tenant` cleanup queue; per-CF action units) | **~10** | Revenue & Profitability set; CoGS / Variance / Cost Center; Finance Ops Readiness; MSME |
| RED (B2 — semantic gap, gated on successor open-item ADR) | **3** | DPO honestly-as-DPO; CCC; balance-sheet ratios (Current, Quick) where they need open-item resolution |
| RED (B6 — anomaly metric family) | **3** | Same Party AR/AP, After-Hours, Duplicate Payments |
| RED (B7 — reader/connector gap) | **rest of Tier-B** | Budget/forecast variance, FX, NBFC ratios, etc. |

### Scenarios (43 total)

| Class | Count |
|---|---|
| GREEN | 0 |
| AMBER (rename only — demo-safe today) | 0 |
| AMBER pending verification of `apex` substrate (likely demo-able after rename) | **6** (A1, A2, A4, A8, S1, plus M3-option-b conditional) |
| RED (mix of B1a / B4 / B5 / B6 / B7) | **37** |

### Coherence assertions (8 total)

| Class | Count |
|---|---|
| GREEN | 0 |
| AMBER pending verification (likely demo-able after `apex` substrate check) | 3 |
| RED (B2 / B4 / B7) | 5 (1 explicitly deferred — CCC) |

**Net effect of the correction:** the "AMBER pending verification" class replaces the prior "RED → AMBER-with-SDG" class for items that were classified RED *only because the triage assumed no Apex tenant*. The number of items that may already be demo-ready under the correct slug is non-zero; this triage does not enumerate them past the §1 table because verification is the next-action work, not part of this docs slice.

## Section 8 — Top three demo-readiness actions (corrected)

1. **Verify the existing `apex` substrate's AR/AP producing-MC set, then rename + position the demo-safe tiles.** With 148 MCs bound and 31 producing for `apex`, the AR/AP balance-side tiles may already have honest data — they just need the demo-safe rename pass (DSO → Collection Pressure; AR balance MCs → "Total Receivables (period close)"; AR aging MC → drag-first M3 if substrate supports), an alignment audit against the DSO MWR Demo Positioning rules, and a verification that no rendered claim crosses into forbidden semantics. This is doc + UI label work, not net-new substrate work, and converts ~7 tiles from AMBER-pending-verification to AMBER-demo-safe in one pass.

2. **Run the `null_in_tenant` cleanup queue against `apex` — top 5 CFs first.** `total_revenue` (19 MCs broken), `operating_cash_flow` (11), `total_payments_count` (7), `total_invoice_line_items_count` (6), `total_invoices_processed_count` (5) collectively touch 48 broken tokens. Each is a per-CF audit: confirm the BF the CC maps to, confirm whether the column is null because the reader doesn't emit it or because the SDG profile doesn't generate it, then either repoint the mapping (Layer C) or fix the upstream emitter (Layer A). After each CF lands, re-run `devhub_formula_token_audit` and `devhub_tenant_bind_metrics` (dry-run first) for the freshly-clean MCs. Highest-leverage Tier-A unblocks: Total Revenue, Revenue Growth Rate, Gross Profit Margin, Operating Profit Margin, all of which gate Meera's M2/M9 narratives.

3. **Storyboard amendment proposal — narrower than the prior version.** The storyboard's two structurally-undemonstrable claims remain: DSO-as-DSO and CCC tie-out. Both are gated on the successor open-item/as-of ADR. Propose:
   - Replace the DSO Tier-A entry with "Collection Pressure (period view)."
   - Defer CCC and §9 coherence assertion #2 to a successor demo cycle (already documented in DSO MWR follow-ups).
   - Replace M3 narration with the AR Aging Weighted Average variant (option b in §4) **after** action 1's verification confirms substrate.
   - Note that all other "RED" tiles are tractable per-CF cleanup work, not architectural changes. The storyboard does not need to be rewritten — just amended on the DSO/CCC items and updated as the cleanup queue lands.

## Section 9 — Non-decisions

This triage does **not**:

- Recommend modifying the locked storyboard. The storyboard owner is the only party who can sign off on amendments.
- Author or commit any metric, contract, schema, or SDG change.
- Specify the successor open-item/as-of ADR's three candidate mechanisms (named in ADR-c012c0 §Successor; the choice is a separate Foundation Gate).
- Propose UI changes to bc-portal or bc-admin.
- Run any metric evaluation, recompute any chain, or write to any tenant table.

## Section 10 — Evidence

| Source | Used for |
|---|---|
| `demo-plan-cfo-pack-storyboard.md` (locked) | Tile and scenario inventory |
| `metric-workstream.md` | Foundation Gate framing |
| MWR `days-sales-outstanding/2026-05-11-grammar-design-SES-b7db1a.md` | DSO honest-computation envelope + Demo Positioning subsection |
| `ADR-c012c0.md` (DEC-c012c0 / D400, proposed) | Phase-1 grammar scope + successor ADR pointer |
| `metric-readiness-toolkit.md` | Dial semantics; 7-stage ladder |
| `devhub_readiness_dial` (read 2026-05-11 02:50 + 03:36 UTC) | Catalog: 163 ready of 376 active. **`apex` bound 148 / producing 31 / wouldProduceIfBound 0.** `apex-motors` returned 500 (alias/route mismatch, NOT tenant absence). `sandbox1` bound 20 / producing 13 (separate pilot). |
| `devhub_formula_token_audit` (apex, 2026-05-11 03:36 UTC) | 376 MCs / 27 clean / 349 broken. 415 null_in_tenant, 134 type_mismatch, 2 no_mapping. Top broken CFs: `total_revenue` (19), `operating_cash_flow` (11), `total_payments_count` (7). |
| `devhub_chain_status` (read 2026-05-11) | Chain SSOT: 228 complete / 311 partial of 539 |
| `metric.readiness_ledger` (`apex`, read 2026-05-11) | 79 metric_snapshot rows / 546 records; 2 reader_run / 76 records; 4 resolution / 149 records. Latest 2026-05-10 23:48 UTC. Live substrate. |
| `contract.metric_contract` + `contract.metric_contract_version` (read 2026-05-11) | `mc__days_sales_outstanding` versions 1.0.0 / 1.1.0 / 1.2.0 all `active`, subfunction `accounts_receivable`, audit_status_code `warn`. DSO MC is real, producing, and consistent with the DSO MWR's semantic envelope. |

## Section 11 — Follow-ups

- **Tenant-alias decision (B0).** Owner: bc-core / platform. Decide whether to register `apex-motors` as a readiness-route alias for `apex`, or to document `apex` as the only canonical slug and update demo-script wording. Either is fine; ambiguity is not.
- **Per-CF `null_in_tenant` cleanup queue (B1a).** Owner: platform / SDG workstream. Top-5 CF batch: `total_revenue`, `operating_cash_flow`, `total_payments_count`, `total_invoice_line_items_count`, `total_invoices_processed_count`. Each is a Layer A vs Layer C audit + repair.
- **AR/AP producing-MC verification + rename pass (Section 8 action 1).** Owner: demo workstream + DSO MWR Demo Positioning author. Establish which AR balance / aging MCs are currently producing for `apex`, decide the demo-safe label set, align with the DSO MWR.
- **Storyboard amendment proposal (narrower than original).** Owner: storyboard owner. Surface this triage's §8 action 3.
- **Successor open-item/as-of ADR scoping.** Already named in ADR-c012c0 and DSO MWR follow-ups. No new action from this triage.
- **Coherence test suite design.** Storyboard decision #5 names it; design work scope is unscoped today.
- **Anomaly metric family scoping (B6).** Required for the entire Pradeep role lens + Meera M6.

## Section 12 — Correction history

- **2026-05-11 (this revision).** Replaced the false finding *"No Apex tenant exists — `apex-motors` returns 500"* with accurate wording. The canonical Apex tenant slug is `apex`; the 500 was an alias/route mismatch. Substrate verified live via readiness dial (148 bound / 31 producing), formula-token audit (27 clean / 349 broken with `null_in_tenant` dominating), readiness ledger (79 recent metric snapshots, latest 2026-05-10 23:48 UTC), and DSO MC inspection (v1.0/v1.1/v1.2 all active, subfunction `accounts_receivable`). Tile and scenario counts in §7 reclassified accordingly: 6 tiles moved from "RED → AMBER-with-SDG" to "AMBER pending verification" of the existing substrate; the B1 catch-all blocker split into B0 (alias mismatch), B1a (per-CF `null_in_tenant` cleanup), and B1b (binding-state cleanup as MCs flip to clean). DSO MWR Demo Positioning wording is unchanged — the substantive demo-positioning advice (Collection Pressure label, AR-Aging-WA-led M3, CCC deferred) is independent of the tenant-existence correction.

## Section 13 — Refresh after total_revenue arc + DSO Phase-2 ADR (2026-05-11 PM)

After the original triage landed (commit `9317e17`), two events changed the state:

- **total_revenue arc completed** (Slices 1 → 1h, commits `fded8d9` → `d94e936`): apex producing count moved from 31 → **46** (+15 cumulative); 7 stale `total_revenue` MCs realized via the H3 grain-alignment repair; the D337 dispatcher auto-fanout produced ~8 additional MCs.
- **DSO Phase-2 ADR promoted** (commit `276ff15`): DEC-1db1c7 / D401 — *Open-item / as-of canonical semantics — temporal projection for balance metrics*. ADOPTED Mechanism A (separate open-item CC family). **Implementation gated on bc-core code work** (DEC-c012c0 Stage 2 engine paths + DEC-1db1c7's Slice 1 CC authoring) — see commit `8f28074` for the gate-failure record.

**Demo-cycle scope (per current operator instruction):** realistic DSO and CCC are **excluded from this demo cycle**. Focus is on increasing producing count via per-CF cleanup arcs (total_revenue pattern), and demo-safe tile labeling for tiles that won't realize this cycle.

### Refreshed platform state (read 2026-05-11T11:59 UTC)

| Dial | Value | Delta from §Platform-state |
|---|---|---|
| Catalog `ready` (Stage 4) | 175 | +12 |
| Apex `bound` | 160 | +12 |
| **Apex `producing` (Stage 7)** | **46** | **+15** |
| Apex audit-clean | 38 | +11 |
| Apex `wouldProduceIfBound` | 0 | 0 |
| `apex-motors` alias | still 500 (alias-route mismatch; not tenant absence) | unchanged |

### Tiles that have realized via the total_revenue arc (RED → producing)

Cross-referencing the 85 distinct MCs with apex metric_snapshot ledger entries against the Tier-A + Tier-B tile list:

| Storyboard tile | Producing MC(s) | Notes |
|---|---|---|
| Revenue & Profitability → **Total Revenue** | mc__total_revenue | producing (general_finance) — directly addressable as primary tile |
| Revenue & Profitability → **Gross Profit Margin** | mc__gross_profit_margin (cost_accounting) + mc__gross_margin (general_ledger) | sibling MCs both producing |
| AR Performance → **Total Outstanding AR** | mc__total_ar_balance | producing — can lead the AR tile set |
| AR Performance → AR Aging signal | mc__average_days_delinquent, mc__aged_dispute_count_30_plus_days, mc__doubtful_debt_provision | partial; **weighted-average AR aging** still pending a dedicated MC |
| AR Performance → Top 10 Overdue Customers | mc__intercompany_reconciliation_aging, mc__cost_per_collection_attempt, mc__ar_staff_productivity | indirect signal; customer-level drill TBD |
| Liquidity & Working Capital → DSO | mc__days_sales_outstanding v1.2.0 | producing as v1.2.0 only — **demo as "Collection Pressure"** per DSO MWR Demo Positioning |
| AP Performance → AP analytics | mc__blocked_invoices_value, mc__gr_ir_imbalance, mc__ap_negotiation_cost_savings, mc__ap_process_improvement_savings | partial — broader AP coverage still gated by `total_payments_count`, `total_invoice_line_items_count` |
| Treasury angle (M9/M10/M11) | mc__operating_cash_flow, mc__fx_exposure_by_currency, mc__fx_gain_loss_impact_on_p_l, mc__hedge_effectiveness, mc__liquidity_coverage_ratio, mc__total_treasury_costs | producing — Meera's treasury narrative is partially supported |
| Tax / compliance | mc__time_to_close_tax_provision, mc__tax_jurisdictions_managed, mc__unrecognized_tax_benefits_utb | producing |
| Capital structure | mc__equity_turnover_ratio, mc__capital_intensity_ratio, mc__capital_turnover_ratio, mc__capitalization_ratio, mc__debt_refinancing_rate, mc__fixed_to_variable_interest_rate_debt_ratio, mc__interest_rate_spread, mc__preferred_to_common_equity_ratio, mc__book_value_of_equity_per_share_bvps | producing — large block |
| Revenue analytics | mc__cost_of_revenue, mc__deferred_revenue, mc__deferred_revenue_balance, mc__recognized_revenue, mc__unbilled_revenue, mc__revenue_recognition_lag, mc__revenue_by_product_line, mc__revenue_by_channel, mc__revenue_by_region, mc__revenue_backlog, mc__mrr, mc__arpa, mc__return_on_revenue, mc__sg_a_to_revenue_ratio, mc__research_development_to_revenue_ratio, mc__shipping_cost_as_of_revenue, mc__cost_of_revenue_cogs_ratio | producing — extensive Tier-A + Tier-B coverage |
| Asset / inventory | mc__asset_utilization_ratio, mc__working_capital_turnover, mc__working_asset_turnover_ratio, mc__total_asset_turnover, mc__total_asset_turnover_ratio, mc__gross_margin_return_on_investment_gmroi, mc__net_asset_value_nav, mc__asset_management_training_investment, mc__asset_management_cost_benefit_ratio, mc__cost_avoidance_from_asset_management | producing |

**Storyboard implication:** the M1 ("attention this week"), M2 (quarterly guidance), M3 (with AR Aging WA fallback), M9–M11 (treasury / FX / NBFC), and most Anil + Suresh AR/AP scenarios are now substantially supported by producing MCs. The bottleneck for full Tier-A coverage has shifted from "structural readiness" to "specific per-CF cleanup arcs."

### Tiles that remain RED — demo-safe labeling required this cycle

These tiles cannot realize before the demo cycle and need explicit demo-safe disposition:

| Tile / Scenario | RED reason | Demo-safe disposition |
|---|---|---|
| DSO (Liquidity tile) | v1.2.0 is same-period coverage indicator; realistic DSO blocked on DEC-c012c0 Stage 2 + DEC-1db1c7 implementation | **Rename:** "Collection Pressure" (visible) / "Receivables Coverage (period view)" (sub-label). M3 drag-narrate via AR Aging Weighted Average instead. Per DSO MWR Demo Positioning. |
| CCC (Liquidity tile) | Requires DSO v2 + DPO v2 + DIO v2 with consistent open-item semantics | **Drop CCC tile from this demo cycle.** Re-enable post-Phase-2. Storyboard §9 coherence assertion #2 deferred. |
| Variance to Budget/Forecast | No budget/forecast reader (B7) | **Hide tile or relabel "Forecast Coverage TBD" with no number.** Don't promise the variance arithmetic. |
| MSME Compliance % | India-specific MSME flag + 45-day rule not modeled (B4 + B7) | **Drop from M8/S2 narration this cycle.** Optionally relabel "Vendor Aging Indicator" as a generic AP-aging signal. |
| Same Party AR/AP | Anomaly metric family not authored (B6) | **Drop M6/S3 same-party demo.** xPress Logistics narrative requires anomaly detection. |
| After-Hours Transactions | Posting-time-of-day signal not in CC layer (B6 + B7) | **Drop M6/P1/P2/P6 after-hours narration.** Pradeep's role's after-hours JE story cannot run honestly. |
| Duplicate Vendor Payments | Anomaly family (B6) | **Drop P5 duplicate-payment narration.** |
| Group Consolidation Days / Reconciliation Status / JE Backlog | Finance-Ops-Readiness signal not authored (B4) | **Drop M4 narration about close-day-7.** |
| Cost Center Efficiency / Variance from Standard Cost | Cost accounting MCs + standard-cost reference not in scope (B4 + B7) | **Drop R1/R2/R5/R6 plant CFO narration.** Rajesh's entire role lens is not demoable this cycle. |
| Production Efficiency / Scrap Rates / GRN-Invoice Match | Plant-side readers (B7) | **Drop R3/R4/R8 narration.** |

### Demo-flow recommendation (30-minute version, updated)

The 30-minute role tour from storyboard §10 is **partially supported**. Recommended cuts and substitutions:

| Act | Original role | Status now | Recommendation |
|---|---|---|---|
| Act I — Meera (Group CFO) | M1, M3, M7, M8 | M3 has fallback (AR Aging WA); M8 (MSME) drop or generic | Run M1, M3 (renamed tile), M7 (audit committee), skip M8 |
| Act II — Anil (Head of Receivables) | A2, A3, A4 | A2 (Top 10 Overdue) — partial; A3 (MetroLink narrative) requires customer-level drill; A4 (collections-due) — partial | Run A2 in renamed mode, defer A3, run A4 partial |
| Act III — Suresh (Vendor Mgmt) | S2 (MSME), S3 (xPress same-party) | Both drop in this cycle | **Skip Act III entirely** OR substitute generic AP-due narration via mc__blocked_invoices_value + mc__gr_ir_imbalance |
| Act IV — Pradeep (Internal Audit) | P1 (anomaly), P6 (after-hours JE audit trail) | Both drop | **Skip Act IV entirely** until anomaly metric family lands |
| Act V — Rajesh (Plant CFO) | R1, R2, R5 (Plating variance) | All drop (no cost-center / plant signal) | **Skip Act V entirely** |
| Act VI — Return to Meera | Defensible answer summary | Requires preceding acts | **Substitute with shorter close on Meera's tiles only.** |

The 30-minute demo collapses to roughly a **15-minute Meera + Anil flow** with renamed DSO tile. CCC and the Pradeep / Rajesh / Suresh acts defer to a post-Phase-2 / post-anomaly-family cycle. This is the honest demo-readiness picture this slice.

### High-leverage CF cleanup candidates (next Slice-1-style arcs — no DSO/CCC)

Per current audit, the top broken CFs that would unblock additional Tier-A producing MCs:

| CF | MCs broken | Likely root pattern | Slice-1-style approach |
|---|---|---|---|
| `operating_cash_flow` | 11 | Probably similar to `total_revenue` pre-repair: mapping repointing OR per-tenant data extension on cc__actual_ledger | (a) Audit `cc_field_mapping` for `operating_cash_flow`. (b) If wrong-BF-target, repair via D330-R5. (c) If sparse data, extend GL coverage already done in Slice 1g — re-check after. |
| `total_payments_count` | 7 | AP processing analytics; likely mapped to `cc__invoice_hdr` or `cc__payment_run` with sparse source coverage | Per-CF audit + targeted reader run for the AP source entity |
| `total_invoice_line_items_count` / `total_invoice_line_items` | 6 + 4 | Likely needs invoice-line CC authoring (Tier-A AP coverage) | Larger scope — author new CC for invoice line items (sibling to cc__invoice_hdr) |
| `total_journal_entry_line_items` | 5 | Already have cc__journal_entry_hdr from Slice 1g; line-item CC needed | New CC authoring |
| `total_debt` | 5 | Capital structure; likely needs liabilities CC or remapping to existing cc__actual_ledger | Audit cc_field_mapping for `total_debt` |
| `average_total_assets` | 4 | Asset turnover MCs; likely needs balance-sheet aggregation MC or remapping | Audit |
| `total_company_revenue` | 4 | Sibling CF to `total_revenue`; likely same Slice-1 pattern (mapping repair) | D330-R5 repair candidate |
| `total_current_liabilities` | 4 | Liquidity ratios; new mapping or new CC | Audit |
| `total_finance_function_it_costs` | 4 | Operational; likely cost-center sourced — needs cost-center reader | Out of scope; B7 |

**Highest immediate ROI:** `operating_cash_flow` (11 MCs) and `total_company_revenue` (4 MCs, likely a one-line D330-R5 mapping repair). Following the total_revenue Slice 1 pattern: registry audit → D330-R5 repair → L-node refresh → chain-status refresh → tenant-DB grain verification → optional reader extension → MC realization check.

### Updated counts summary

Re-applying the original §7 classification framework with current evidence:

**Tiles (Tier-A + Tier-B, 36 total):**

| Class | Count | Notes |
|---|---|---|
| GREEN (producing with sensible label today) | ~12 | Total Revenue, Gross Profit Margin (×2), Total AR Balance, Working Capital indicators, Treasury basics, Revenue analytics block — directly addressable in the demo |
| AMBER (rename + position, demo-safe) | 1 | DSO → Collection Pressure |
| AMBER (producing but needs labeling decision) | ~6 | Asset turnover, capital structure ratios, tax compliance, AP partial — present but not headline-grade for the storyboard's Tier-A |
| **RED — must drop from this demo cycle** | ~17 | CCC, MSME, Anomaly (×3), Finance Ops Readiness (×3), Plant CFO scenarios (×6), Variance to Budget/Forecast |

**Demo-flow scenarios (43 total):** roughly 12–15 are honestly runnable (Meera M1/M3-renamed/M7/M9–M11; Anil A2/A4 in renamed mode); the rest defer.

### Confirmation — no implementation occurred this slice

| Check | Result |
|---|---|
| Realistic DSO / CCC implementation | ✗ Excluded per scope |
| Bc-core code changes | ✗ None |
| Contract / mapping / schema / SDG | ✗ None |
| Reader execution | ✗ None |
| Metric evaluation | ✗ None |
| Cross-tenant impact | ✗ None (apex only, read-only) |
| Commits | ✗ Triage updates uncommitted pending operator review |

---

*This triage is uncommitted working memory for the demo-readiness conversation. Status remains `draft` until the storyboard owner has signed off on the §8 action 3 amendment scope; this document's role is then to be either decommissioned or superseded by the amended storyboard.*
