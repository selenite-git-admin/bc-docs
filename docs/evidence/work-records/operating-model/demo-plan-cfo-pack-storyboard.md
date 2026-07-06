---
id: demo-plan-cfo-pack-storyboard
order: 31
title: "CFO Pack Demo Storyboard"
status: locked
authority: authoritative
depends_on: [demo-plan-cfo-pack, tenancy-and-binding, metric-catalog, metric-evaluation]
governing_sources:
  - BareCount Context (philosophical foundation, December 2025)
  - BareCount Concept v2 (one-line positioning, January 2026)
  - DataJetty Platform pitch deck (CFO Pack KPI scaffold)
  - bc-portal Beyond UX v1 spec
governing_adrs:
  - DEC-28b176 (D394 — Metric Readiness Model)
  - DEC-6cdceb (D361 — bc-portal three-surface split)
  - DEC-2cf250 (D362 — BareCount visual language)
errata_referenced: []
v2_sources: []
diagrams: []
---

# CFO Pack Demo Storyboard

This is the contract for everything downstream of Phase 0 in the [CFO Pack Demo Plan](demo-plan-cfo-pack.md). It locks the narrative, the hero KPIs, the per-role Rooth dialogue, and the synthetic-business shape. Phase 1 (bc-sdg coherent ledger) cannot begin until the storyboard is signed off.

## 1. Philosophical north star

From the BareCount Context document:

> *"BareCount did not emerge from a gap in tooling. It emerged from a gap in truth."*
> *"What is true, and who gets to decide?"*
> *"Most data products optimize for possibility. BareCount optimizes for finality."*
> *"You can start with the facts, that's it."* (Concept v2)

The demo is not a feature tour. The demo demonstrates the moment a Group CFO realises **she no longer has to negotiate truth before a board meeting, an analyst call, or an audit committee review**. That moment is the entire pitch.

Three corollaries that constrain the storyboard:

| Corollary | Implication |
|---|---|
| **Numbers must settle.** | Coherence assertions (revenue − COGS = gross profit; group consolidation = sum of business-unit postings; DSO + DIO − DPO = CCC) are identity-level requirements. A demo number that doesn't tie out kills the pitch. |
| **Authority shift is the through-line.** | Traditional dashboard demo: CFO scrolls, says "interesting." BareCount demo: CFO asks a normally-contestable question, Rooth answers with named entities + amounts + provenance, CFO can answer the board / auditor / analyst without saying *"let me come back to you."* |
| **Source primacy is visible.** | Every Rooth answer ends with a click into the Trust Chain. Real source IDs, real timestamps, real run IDs. No abstract certifications. The provenance is the trust. |

### A property the demo claims, not a limitation it tolerates

The demo proves the platform works **on synthetic data without ever reading a real client's data** — because the platform's value is intrinsic to the rules, not dependent on the dataset, and the architecture enforces this. Per DEC-771baf and DEC-1918d0, platform and tenant connections are structurally isolated; a misrouted query returns *"relation does not exist"* rather than leaking data. The team building the demo cannot pull a real client's data into it, by design — full rationale in the demo plan's [Permanent demo invariant](demo-plan-cfo-pack.md#permanent-demo-invariant--client-data-access-is-denied-by-design) section.

This is a positioning advantage with risk-averse Indian large-cap CFOs. *"We can't use your data"* (system property) is a stronger claim than *"we won't"* (contractual). It also means the demo is permanent — even after BareCount has paying clients, this same SDG-backed Apex tenant remains the marketing surface. Live client data is never used for marketing. Names and numbers in the storyboard are templates the bc-sdg patterns instantiate quarterly so the demo never feels frozen.

## 2. The 60-second pitch (as the Group CFO experiences it)

A working Group CFO of a listed Indian auto OEM. ₹40,000+ Cr group revenue. Five business units. 24 months post-S/4HANA-implementation. Quarterly analyst calls in two weeks. Board audit committee in three. She has a daily morning brief to the MD/CEO that her team prepares overnight.

She opens BareCount for the first time. Beyond canvas. Finance card expanded by default. She types: *"What needs my attention this week?"*

Rooth answers in three sentences: a state transport corporation (₹15 Cr overdue 8 weeks), a Plant 1100 Plating cost-center variance (₹14 Cr unfavourable), and a related-party flag (xPress Logistics is both a vendor and an NBFC borrower — net group exposure ₹1.6 Cr in her favour, but disclosable). Below the answer, four metric tiles update: DSO, AR Aging, Cost Variance, Same-Party Anomaly. Each has a small *"click for chain"* link.

She clicks the cost variance. The Trust Chain opens. She sees: source SAP table COEP, run ID `019d8...`, the canonical contract that produced the number, the formula that aggregated it, the production run that drove the variance.

She closes the laptop. Her team's morning-brief preparation is now a 3-minute review, not a 50-minute reconstruction. That's the pitch.

## 3. Demo persona — Apex Motors Limited (Group CFO)

> Listed Indian auto OEM. Promoter-influenced board. Big 4 statutory auditor. Multiple business units. Mid-tier in the Indian auto-OEM landscape (smaller than Tata Motors, larger than Force Motors).

| Field | Value |
|---|---|
| Company | **Apex Motors Limited** (listed on BSE/NSE) |
| Industry | Auto OEM — passenger vehicles + commercial vehicles + vehicle finance NBFC |
| Revenue | ₹42,000 Cr (~$5B) FY25; growing ~12% YoY (scale comparable to Bajaj Auto's group revenue) |
| Ownership | Promoter family ~25%; FII ~22%; DII ~28%; retail + others ~25% |
| Geography | India HQ (Pune); exports to ASEAN, Africa, LatAm; one global subsidiary in Indonesia |
| Plants | 4 plants — Pune Passenger (1100), Pune Commercial (2100), Chennai Assembly (3100), Aurangabad CV (4100) |
| Business units | Passenger Vehicles (BU1) / Commercial Vehicles (BU2) / International (BU3) / Apex Financial Services NBFC (BU4) / Aftermarket Parts & Service (BU5) |
| Customers | ~9,500 dealers nationwide + corporate fleets + state transport corps + government tenders + exports distributors |
| Vendors | ~3,200 (Tier-1 + Tier-2 + raw material + services); ~1,400 are MSME-registered |
| ERP | SAP S/4HANA, ~24 months live; 84 SAP company codes (most are operational subsidiaries) |
| Statutory auditor | Big 4 firm (anonymised in the demo) |
| Finance team | ~180 people across Group + plant CFOs + AR/AP/GL/Tax/Treasury/Internal Audit/IR |
| Posture | Group CFO has daily morning brief to MD/CEO. Quarterly analyst calls. Audit Committee meets monthly during quarter-end window. |

**Story posture:** the Group CFO is two weeks from quarterly results and three weeks from audit committee. Working capital is under pressure as production ramps for festive season. Two business unit consolidations are running close to deadline. One related-party flag has surfaced that Internal Audit is reviewing.

## 4. The five users (logged-in personas)

First names only. Functional roles via Cognito profile claim. All on `@apex.in`.

| Login | Role | Owns these story events |
|---|---|---|
| meera@apex.in | **Group CFO** | Master narrative; daily morning brief; quarterly results posture; Audit Committee preparation |
| anil@apex.in | **Head of Receivables** | MetroLink State Transport (state transport corp) ₹15 Cr arrears; dealer credit-hold list; fleet customer escalations |
| suresh@apex.in | **Head of Vendor Management** | MSME 45-day rule exposure; xPress Logistics related-party; Tier-1 vendor disputes |
| pradeep@apex.in | **Head of Internal Audit** | After-hours JE on revenue account; same-party anomaly flag; control-violation queue; statutory auditor interface |
| rajesh@apex.in | **Plant CFO, Pune Passenger Plant 1100** | Plating cost-center 1100-PLT variance ₹14 Cr; production efficiency; plant-level close |

**Same data, five lenses.** Beyond's LHS panel, Rooth's narration, and the metric tiles all adapt to the logged-in user's functional role. The platform knows who you are; what you should see; what concerns matter to your work. Coherence holds across roles — the same business event is reflected consistently from each viewpoint.

## 5. The narrative arc (embedded story events)

Single quarter (Q3 FY26, July-September), one set of synthetic events that connect across multiple metrics so coherence is visible.

| # | Event | When | Surfaces in (multiple roles) |
|---|---|---|---|
| 1 | **MetroLink State Transport Ltd** (state transport, large CV fleet customer) misses two payment cycles | Aug-Sep | DSO ↑ (Meera), AR Aging shift to 60-90 (Anil), Top 10 Overdue (Anil), Dispute Cycle Time (Anil) |
| 2 | **Plant 1100 Plating cost-center 1100-PLT** overruns standard cost by 18% (₹14 Cr) | Aug | Variance from Standard Cost (Rajesh, Meera), Cost Center Efficiency (Rajesh), Group Margin Compression (Meera) |
| 3 | **xPress Logistics Pvt Ltd same-party flag** — vendor balance ₹3.1 Cr we owe + AFS NBFC has lent them ₹4.7 Cr (net ₹1.6 Cr in our favour, but related-party disclosable) | Q3 | Anomaly: Same Party AR/AP (Pradeep), AP balance (Suresh), NBFC exposure (Meera) |
| 4 | **One after-hours JE** (₹2.4 Cr) posted to revenue account 470000 in BU1 by user U7341 on Sep 14, 23:47 IST | Sep | Anomaly: After-hours posting (Pradeep), ERP Practices flag (Pradeep) |
| 5 | **Group consolidation runs Day 7** (target Day 5) due to BU3 (International) intercompany clearing delay ₹89 Cr | Sep close | Finance Ops Readiness: Month-End Closing Time (Meera), Reconciliation Status (Meera, Pradeep) |
| 6 | **MSME 45-day rule exposure**: 47 MSME vendors approaching the 45-day threshold; ₹40 Cr exposure if not paid in time; 2 already breached | Sep | MSME Compliance % (Suresh, Meera), Working Capital posture (Meera) |
| 7 | **Q3 results +4.2% vs analyst consensus** (revenue ₹10,840 Cr actual vs ₹10,400 Cr consensus); margin compression of 250 bps from Plating event | Sep close | Variance to Forecast (Meera), Investor Relations posture (Meera) |

Connections: MetroLink (event 1) and the Plating overrun (event 2) together explain the working-capital + margin story. xPress Logistics (event 3) and the after-hours JE (event 4) together feed the audit committee narrative. The MSME exposure (event 6) and BU3 intercompany delay (event 5) shape the close posture. The Q3 results (event 7) is the public-facing crystallisation.

## 6. Hero KPIs (proposed)

> 36 hero KPIs across the deck's 10 groups, weighted toward "questions a Group CFO / Head / Plant CFO / Internal Auditor would normally trigger ambiguity around." Tier-A must produce coherently; Tier-B fills the canvas.

### Tier-A (must produce, drives Rooth answers)

| Group | KPIs | Story role |
|---|---|---|
| Revenue & Profitability | Total Revenue, Revenue Growth Rate, Gross Profit Margin, Variance to Budget/Forecast, Operating Profit Margin | Anchor the analyst-call posture |
| Liquidity & Working Capital | Current Ratio, Quick Ratio, DSO, DPO, Cash Conversion Cycle | CCC tie-out is the coherence proof |
| AR Performance | Total Outstanding AR, Overdue Receivables %, AR Aging Analysis, Top 10 Overdue Customers | MetroLink event lives here |
| AP Performance | Total Outstanding AP, AP Aging Analysis, Early Payment Discounts Captured, **MSME Compliance % (India-specific)** | MSME 45-day rule event |
| Cost Accounting | Cost of Goods Sold, Variance from Standard Cost, Cost Center Efficiency | Plating overrun event |
| Anomaly & Alerts | Same Party AR/AP, After-Hours Transactions, Duplicate Vendor Payments | Three of the embedded events surface here |
| Finance Ops Readiness | Group Consolidation Days, Reconciliation Status, JE Backlog | Close-day-7 event |

**Subtotal: 25 KPIs.** All must produce coherently across the five roles' views.

### Tier-B (background metrics, populate the canvas)

| Group | KPIs |
|---|---|
| Revenue & Profitability | Net Profit Margin, EBITDA Margin, Average Selling Price, Revenue per Product Line |
| Budgeting & Forecast Accuracy | Forecast vs Actual Revenue Variance, Forecast vs Actual Expense Variance, Budget Utilization % |
| Tax, Compliance & Risk | GST Input Credit Reconciliation %, Regulatory Filing Timeliness, TDS Reconciliation Status |
| ERP Practices & Control | Custom Z-Program Usage, Outside Working Hours Transactions, Manual JE Volume |
| Cost Accounting | Overhead Cost Ratio |

**Subtotal: 11 KPIs.** Numbers must be plausible and tie out at the group level.

### Tier-C (deferred — won't be in the demo)

The remaining ~10 KPIs from the deck's 46-item set. Defer to post-demo.

## 7. Per-role Q&A library

Each role's Beyond canvas shows their own LHS metric set, with Rooth tuned to their vocabulary and concerns. Mode codes: **T** = type-first, **D** = drag-first (Rooth proactively narrates the focused metric), **H** = hybrid (drag + follow-up question).

### 7.1 Meera (Group CFO) — 8 scenarios

| # | Mode | Trigger | Rooth response |
|---|---|---|---|
| M1 | T | *"What needs my attention this week?"* | "Three items. MetroLink State Transport (₹15 Cr / 8 weeks overdue) — Anil escalating. Plant 1100 Plating cost-center variance ₹14 Cr — Rajesh investigating. xPress Logistics same-party flag (₹1.6 Cr net) — Pradeep reviewing for the audit committee." |
| M2 | T | *"How are we tracking against quarterly guidance?"* | "Revenue ₹10,840 Cr Q3 actual vs ₹10,400 Cr consensus — beat by 4.2%. Operating margin compressed 250 bps, primarily the Plating event. EBITDA margin 13.8% vs 16.3% Q2." |
| M3 | **D** | *Drag DSO tile* | "DSO is 47 days, up from 38 in Q2. State transport corporations + corporate fleets drive 71% of the increase: MetroLink ₹15 Cr (8 weeks), HighMile Logistics ₹4 Cr (5 weeks), CityRide Mobility ₹3 Cr (4 weeks). Dealer DSO stable at 22 days." |
| M4 | T | *"What's pending in the close?"* | "Group consolidation runs Day 7 — target was Day 5. BU3 (International) intercompany clearing ₹89 Cr open with Indonesia subsidiary. All other reconciliations clear. JE backlog: 4 items, all routine." |
| M5 | T | *"GST input credit reconciliation — any issues?"* | "Three plant-vendor reconciliations open: Plant 1100 ₹2.3 Cr, Plant 2100 ₹1.1 Cr, Plant 4100 ₹0.4 Cr. Aggregate ₹3.8 Cr held — within tolerance. No vendor invoices held beyond 30 days." |
| M6 | **D** | *Drag the Anomaly badge* | "Three flags. xPress Logistics: same-party AR + AP, net ₹1.6 Cr in our favour — disclosable as related-party. After-hours JE on revenue 470000 by U7341 on Sep 14 — Pradeep reviewing. No duplicate vendor payments." |
| M7 | T | *"Are we ready for the audit committee next week?"* | "Three items to brief: MetroLink arrears (collections position), Plating variance (cost-control posture), xPress same-party flag (related-party disclosure). All three have provenance ready. Statutory audit interactions: clean as of yesterday." |
| M8 | T | *"Anything I should know that I haven't asked?"* | "MSME 45-day rule. 47 vendors approaching threshold; ₹40 Cr exposure if not paid in time. Two have already breached. Suresh has the run schedule but you may want to flag at MD's morning brief — penalty exposure is material." |

**Treasury angle (light — folded into Meera's flow, no separate role):** the Group CFO's strategic-financial concerns at OEM scale aren't a separate persona. They're three additional questions she asks Rooth as part of her own view.

| # | Mode | Trigger | Rooth response |
|---|---|---|---|
| M9 | **D** | *Drag the Working Capital tile* | "Working capital ₹3,420 Cr, up 6.4% from Q2. Drivers: AR creep (₹190 Cr from MetroLink + 3 fleet customers), MSME payment compression (₹40 Cr exposure), BU3 intercompany ₹89 Cr held. NBFC arm portfolio (AFS): ₹4,200 Cr, 8% of group capital employed." |
| M10 | T | *"FX exposure on exports?"* | "BU3 (International) export book ₹140 Cr equivalent. Hedged: 73% via forwards covering Q4-Q1. Unhedged: ₹38 Cr — within group hedging policy threshold. Mark-to-market on hedges: ₹2.1 Cr unrealised gain at quarter-end. No outliers." |
| M11 | T | *"NBFC capital adequacy?"* | "AFS NBFC: CAR 18.4% (RBI minimum 15%, group target 17%). Tier-1 capital ₹680 Cr. AUM ₹4,200 Cr. NPA: 1.8% (within sector benchmark). RBI quarterly return filed Sep 22 — clean. No supervisory observations open." |

### 7.2 Anil (Head of Receivables) — 8 scenarios

| # | Mode | Trigger | Rooth response |
|---|---|---|---|
| A1 | T | *"Who's overdue today?"* | "84 customers past due > 30 days. Top 5: MetroLink State Transport ₹15 Cr (8 wk), HighMile Logistics ₹4 Cr (5 wk), WestBay Auto Sales (dealer chain) ₹3.2 Cr (4 wk), CityRide Mobility ₹3 Cr (4 wk), FleetMax Logistics ₹2.8 Cr (3 wk). Aggregate top-10: ₹38 Cr." |
| A2 | **D** | *Drag the Top 10 Overdue tile* | "Concentration at the top: MetroLink State Transport ₹15 Cr is 39% of the total overdue amount. They've been on a 25-day average payment cycle for 4 quarters; this is the longest stretch yet. Three open disputes — last contacted by your team Sep 28 — meeting noted no resolution." |
| A3 | **H** | *Drag MetroLink customer tile, type "what's the latest?"* | "Last contact: Sep 28, your team to their Finance Controller. Outcome: they cited budget release delay from state government. Three open disputes from last quarter unresolved (₹1.8 Cr aggregate). Their last 4 quarter average dispute cycle: 31 days. This batch: 76 days. 95th percentile vs their own history." |
| A4 | T | *"Largest collection due this week?"* | "₹62 Cr expected this week. Top 3: MetroLink ₹15 Cr (overdue, follow-up scheduled), GreenLine Transit ₹8 Cr (on schedule), AutoStar Distributors ₹6 Cr (export, on schedule). 39 dealer collections aggregating ₹22 Cr." |
| A5 | T | *"Which dealers are on credit hold?"* | "12 dealers on hold. Reasons: 6 for cheque dishonour (last 90 days), 4 for >60-day overdues, 2 for dispute escalations. Aggregate held order value: ₹4.2 Cr. Three are eligible for review based on recent payment behaviour." |
| A6 | T | *"What's collected this month vs target?"* | "Target ₹520 Cr; actual to-date ₹380 Cr (73%). Trailing 3 days: ₹47 Cr. Pacing slightly behind — running about ₹15 Cr short of pro-rata. Primary gap: MetroLink + HighMile combined ₹19 Cr expected this month, neither received." |
| A7 | T | *"Any disputes nearing 90 days?"* | "Four. MetroLink State Transport (₹1.8 Cr aggregate, 76 days), CityRide Mobility (₹0.9 Cr, 71 days), AutoStar Distributors (₹0.4 Cr, 68 days), one dealer (₹0.2 Cr, 65 days). All eligible for escalation under your 90-day policy." |
| A8 | T | *"Fleet receivables vs dealer receivables?"* | "Total AR ₹1,840 Cr. Fleet (state transport + corporate fleet + cab aggregators): ₹620 Cr (34%), aging 47-day weighted average. Dealers: ₹1,090 Cr (59%), aging 22-day weighted average. Exports: ₹130 Cr (7%), aging 41-day weighted average. Fleet is the entire DSO drift." |

### 7.3 Suresh (Head of Vendor Management) — 8 scenarios

| # | Mode | Trigger | Rooth response |
|---|---|---|---|
| S1 | T | *"What's due to vendors this week?"* | "₹312 Cr scheduled. Top 5: BrakeWorks India ₹42 Cr (Tier-1, on contract), GearLine Components ₹38 Cr (Tier-1), MetalEdge Steel ₹29 Cr (raw material), PlateTech Surface Finishing ₹14 Cr (Plant 1100 service), ColorPro Coatings ₹11 Cr. 312 MSME invoices aggregating ₹89 Cr." |
| S2 | T | *"MSME vendors approaching 45 days?"* | "47 vendors in the 35-44 day window. ₹40 Cr aggregate exposure. 2 already breached: CastEdge Foundry (47 days, ₹0.8 Cr) and PrecisionMachining Co (46 days, ₹0.5 Cr) — penalty interest accruing. Need payment run by Friday to clear the 45-day list." |
| S3 | **D** | *Drag xPress Logistics vendor tile* | "Vendor balance ₹3.1 Cr we owe (45 days outstanding). Related-party flag: xPress also has a fleet finance loan from Apex Financial Services NBFC, ₹4.7 Cr outstanding. Net cross-BU exposure ₹1.6 Cr in Apex's favour. Last 4 quarters: vendor relationship clean, finance relationship current. Pradeep is reviewing for related-party disclosure." |
| S4 | T | *"Are we missing early-pay discounts?"* | "Eight vendors offer 2/10 net 30 terms; we're capturing 5 of 8 this month. Three missed: WireWorks Industries (₹0.4 Cr discount foregone), CableTech Co (₹0.2 Cr), ToolWorks (₹0.1 Cr). Aggregate ₹0.7 Cr opportunity. Cash position supports capture; payment-run scheduling is the gap." |
| S5 | T | *"GST input credit — any vendor invoices held up?"* | "Three plant-level reconciliations open. Plant 1100: 12 invoices ₹2.3 Cr (PlateTech billing dispute). Plant 2100: 7 invoices ₹1.1 Cr (vendor GSTIN mismatch on 2 lines). Plant 4100: 4 invoices ₹0.4 Cr (date format issue from MSME vendor). All within statutory window." |
| S6 | T | *"Vendor disputes this month?"* | "Six open. Three are amount disputes (PlateTech ₹0.6 Cr, BrakeWorks ₹0.4 Cr, MetalEdge ₹0.2 Cr). Two are quality holds (CastEdge — rejected casting batch). One is a delivery shortfall (PrecisionMachining). Average resolution cycle: 12 days; current oldest 28 days." |
| S7 | T | *"TDS reconciliation status?"* | "Q3 TDS deductions ₹14.2 Cr. Filed on Oct 7 (within deadline). 26AS reconciliation: 99.4% match; 0.6% (₹0.09 Cr) under review with two vendors. No statutory exposure." |
| S8 | T | *"Are we current on rentals and utilities?"* | "Rentals ₹4.1 Cr/month — paid through October. Utilities ₹6.2 Cr/month — paid through September; October billing under 3-way match (3 plants). Insurance premium ₹2.4 Cr due Nov 15 — scheduled. No arrears." |

### 7.4 Pradeep (Head of Internal Audit) — 8 scenarios

| # | Mode | Trigger | Rooth response |
|---|---|---|---|
| P1 | **D** | *Drag the Anomaly badge* | "Three items this period. (1) After-hours posting on revenue 470000 by U7341 on Sep 14 at 23:47 — ₹2.4 Cr — outside operating hours window. (2) xPress Logistics flagged same-party AR + AP — net ₹1.6 Cr cross-BU exposure, related-party disclosure scope. (3) No duplicate vendor payments." |
| P2 | T | *"After-hours postings this period?"* | "27 entries outside 09:00-21:00 IST. Most are routine reversals or correction entries posted by IT-supported overnight batches (U7102, U7245). One outlier: U7341 on Sep 14 at 23:47 IST, manual entry, posted to revenue account 470000, ₹2.4 Cr. Single largest after-hours entry in the quarter." |
| P3 | T | *"Manual JEs above threshold?"* | "12 manual JEs above ₹1 Cr this quarter. 8 routine (provision adjustments, rate corrections). 4 require review: the U7341 entry ($2.4 Cr revenue), one Q3 close adjustment from BU3 (₹1.8 Cr intercompany), two prior-period adjustments from BU2 (₹1.4 Cr aggregate). Audit log preserved for all." |
| P4 | T | *"Same-party transactions flagged?"* | "Two patterns this quarter. xPress Logistics: vendor (₹3.1 Cr we owe) + AFS NBFC borrower (₹4.7 Cr they owe) = net ₹1.6 Cr in our favour, related-party disclosure scope. PartHub Trading: dealer customer (₹0.9 Cr they owe) + vendor (₹0.4 Cr we owe) = net ₹0.5 Cr. Both within group standards but both disclosable." |
| P5 | T | *"Any duplicate vendor payments?"* | "None this quarter. Last instance was Q1 (₹0.3 Cr to PaintCraft, refunded within 11 days). Duplicate-payment control hit-rate: 100% caught on the run cycle for 6 quarters." |
| P6 | **H** | *Drag the after-hours JE entry, type "show me the audit trail"* | "JE 4500001234, posted Sep 14 23:47 IST by U7341. Document type SA, ₹2.4 Cr Dr Account 410001 Cr Account 470000. Reference text: 'Q3 revenue accrual — Aurangabad CV'. Approver: U7102 (auto-approved per workflow rule WF-CV-002). Source SAP: BKPF/BSEG, ledger 0L. No subsequent reversal. Linked CO: 019d8...". |
| P7 | T | *"User access exceptions?"* | "Six users with access to both vendor master and payment posting (SoD violation per group policy). Mitigation: dual-control on payment runs above ₹5 L. No actual SoD breaches in posted documents this quarter." |
| P8 | T | *"Cycle of last 5 manual reversal entries?"* | "(Lists each: original posting → reversal → reason → approver → time-to-reverse). Pattern: 4 of 5 are correction entries within same business day, average reversal lag 4 hours. One outlier: 11-day reversal lag on a CV intercompany — flagged for finance team training." |

### 7.5 Rajesh (Plant CFO, Plant 1100 Pune Passenger) — 8 scenarios

| # | Mode | Trigger | Rooth response |
|---|---|---|---|
| R1 | T | *"Cost-center 1100-PLT status?"* | "Plating cost center, August + September period. Standard cost ₹78 Cr; actual ₹92 Cr; variance ₹14 Cr unfavourable (18%). Primary driver: chemical bath batch failure mid-August requiring 9 days of rework + redo at premium pricing. Secondary: utility consumption +12% (electricity tariff revision). Recovery plan: bath replacement schedule revised, utility hedging in review." |
| R2 | **D** | *Drag the Standard Cost Variance tile* | "Plant 1100 aggregate variance ₹17 Cr unfavourable (10% of standard). Cost-center 1100-PLT (Plating) drives 82% of the unfavorable variance. Other 6 cost centers: 5 within ±3% of standard, 1 (1100-PNT Paint Shop) +6% on consumption variance only. Plating is the entire story." |
| R3 | T | *"Production efficiency this month?"* | "12,840 units passenger vehicles produced in September vs 13,200 plan (-2.7%). Line 1 (Sedan) 98% efficiency. Line 2 (SUV) 91% (Plating bottleneck). Line 3 (Compact) 102%. Plating-driven downtime: 14 hours aggregate across 9 days." |
| R4 | T | *"Scrap rates by line?"* | "Line 1: 1.4% (target 2.0%). Line 2: 3.1% (target 2.0%, +1.1 pts — Plating-related rework). Line 3: 1.6% (target 2.0%). Aggregate plant: 2.0% — at target despite Line 2 elevation." |
| R5 | T | *"Where am I overrunning standard?"* | "1100-PLT (Plating) ₹14 Cr. 1100-PNT (Paint Shop) ₹0.4 Cr (consumption only — within tolerance). All other cost centers within ±3% of standard. The actionable item is Plating." |
| R6 | T | *"Material consumption vs standard?"* | "Steel: 102% of standard (+₹0.8 Cr). Plating chemicals: 134% (+₹6.2 Cr — bath failure period). Paint: 103% (+₹0.4 Cr). Other materials: within tolerance. Plating chemicals alone account for 44% of the cost variance." |
| R7 | T | *"Any plant-specific anomalies?"* | "One. 9-day continuous Plating downtime in mid-August is the longest stretch in 6 quarters; previous worst was 3 days. Outlier from process-stability standpoint. Bath-replacement schedule under revision with maintenance team." |
| R8 | T | *"GRN-to-Invoice reconciliation?"* | "Plant 1100 3-way match status: 96.4% auto-cleared (target 95%). 3.6% under exception review — 11 invoices, ₹2.7 Cr aggregate. Most are PO-quantity vs receipt mismatches under ₹10 L. PlateTech Surface Finishing dispute is the largest single hold (₹0.6 Cr)." |

### 7.6 Mode + category mix across the library

40 scenarios total. **Mix:** 9 drag-first, 28 type-first, 3 hybrid. **Category mix:** trust (P1, P4, P6, M6, M8), decision-readiness (M2, M4, M7, A4, A6, S1, S2, R1, R5), causal-explanation (M3, A2, A8, R2, R6), operational-status (most of A, S, R), audit-control (P series).

The Authority shift only lands when all five role lenses demonstrate it. The 30-min demo flow tours through 3-4 scenarios per role.

## 8. Synthetic business shape (bc-sdg target)

The bc-sdg coherent ledger generates this shape.

| Dimension | Value |
|---|---|
| Industry | Auto OEM (passenger + commercial vehicles + NBFC + parts) |
| Group structure | 5 business units; 84 SAP company codes total; demo focuses on the 5 BU primaries |
| Company codes (demo-focal) | Apex Motors PV (1100 Pune), Apex Motors CV (2100 Pune), Apex International (3000 Indonesia subsidiary), Apex Financial Services (4000 NBFC), Apex Aftermarket (5000 Mumbai) |
| Customers | ~9,500 dealers + corporate fleets + state transport corps + government tenders + exports distributors |
| Vendors | ~3,200 (Tier-1, Tier-2, raw material, services); ~1,400 MSME-registered |
| Products / SKUs | ~600 (vehicle variants + spare parts + sub-assemblies) |
| Cost centers (Plant 1100) | ~40 (production + admin + sales + service); 1100-PLT Plating is the focal center |
| Periods | 24 months ending Q3 FY26 |
| Open AR items at story start | ~28,000 |
| Open AP items at story start | ~9,500 |
| Inventory turns/year | ~14 |
| Embedded story events | The 7 in section 5 |

## 9. Coherence assertions (must tie out)

| Assertion | Why it matters |
|---|---|
| MetroLink overdue ₹15 Cr = sum of their unpaid AR open items at demo date (across BUs) | If AR Aging tile and Top 10 Overdue tile disagree on MetroLink, the demo dies |
| CCC visible on tile = DSO + DIO − DPO | Arithmetic shown on screen must compute correctly |
| xPress same-party net ₹1.6 Cr = (vendor balance ₹3.1 Cr − NBFC loan balance ₹4.7 Cr) sign-flipped to favour | Anomaly must be reproducible by inspection across two BUs |
| Plant 1100 Plating variance ₹14 Cr reflected in Plant 1100 COGS roll-up exactly | Margin compression of 250 bps must compute from this delta |
| Q3 revenue ₹10,840 Cr (group) = sum of BU1 + BU2 + BU3 + BU4 + BU5 in their reporting currency, FX-translated | Group consolidation must equal sum of legal entities |
| MSME exposure ₹40 Cr = sum of unpaid invoices to MSME-flagged vendors aged 35-44 days | India-specific compliance — auditor will ask |
| Period total (GLT0) at group level = sum of detail postings (BSEG) across all BU company codes | Foundation invariant |
| Forecast accuracy 95.8% = (1 − ABS(actual ₹10,840 − forecast ₹10,400) / forecast ₹10,400) × 100 | Public-disclosure number — must match analyst-call narrative |

## 10. Demo flow at three lengths

### 5-minute version (elevator)

Login as **Meera (Group CFO)**. Beyond canvas. Finance card expanded.

1. M1: *"What needs my attention this week?"* → 3-item answer
2. M3: drag DSO tile → Rooth narrates with named entities (MetroLink, HighMile, CityRide)
3. Click DSO → Trust Chain → real source IDs visible
4. Close.

### 10-minute version (executive briefing)

Login as **Meera**. Same as 5-min, plus:

5. M2: *"How are we tracking against quarterly guidance?"* → +4.2% beat with margin compression context
6. M7: *"Are we ready for the audit committee next week?"* → 3-item brief
7. M8: *"Anything I should know that I haven't asked?"* → MSME exposure surfaces

### 30-minute version (working session — full role tour)

**Act I (~6 min): Meera's view.** M1, M3, M7, M8. Rooth surfaces three items; Meera realises she has questions for AR (Anil) and Internal Audit (Pradeep).

**Act II (~5 min): Switch to Anil's view.** A2 (drag Top 10), A3 (drag MetroLink + ask for latest), A4 (this week's collections). The same DSO Meera saw at group level is now decomposed into the customer-by-customer escalation queue.

**Act III (~5 min): Switch to Suresh's view.** S2 (MSME 45-day), S3 (drag xPress vendor — same data Meera saw flagged, but Suresh sees it from the vendor-management lens). Demonstrates that the same xPress entity is one truth, two viewpoints.

**Act IV (~5 min): Switch to Pradeep's view.** P1 (drag Anomaly), P6 (drag the U7341 after-hours JE → audit trail). Demonstrates the auditor's lens — same anomaly Meera saw is now Pradeep's review queue with full provenance.

**Act V (~5 min): Switch to Rajesh's view — and close the loop.** R1 (1100-PLT status), R2 (drag Cost Variance tile), R5 (where overrunning). Rajesh confirms: Plating is the entire margin compression story; recovery plan in place (bath replacement schedule revised, utility hedging in review).

**Act VI (~4 min): Return to Meera's view — the defensible answer.** Meera now has what she needs for the analyst call: *"Q3 margin compression of 250 bps is contained to a single cost-center event at Plant 1100; recovery is in train."* That is a sentence she can say on the call without saying *"let me come back to you."* The pitch lands not on a multi-tile coherence stunt but on the working-CFO outcome — **a defensible answer in 30 minutes, not 50.***

## 11. Final locks

All decisions locked. The storyboard is the contract for Phase 1.

| # | Decision | Locked |
|---|---|---|
| 1 | Demo scope | **T1 only** — Apex Motors finance-deep. SFDC sales bridge (T2) deferred to a future phase. |
| 2 | Default demo length | **30-min canonical role tour.** The 5-min and 10-min flows are cuts of the 30-min, not separately produced demos. |
| 3 | Statutory auditor | **Anonymous "Big 4 firm"** in the storyboard and demo. No fictional name. |
| 4 | Promoter family | **Implicit** — "promoter-influenced board" framing only. No named promoter chairman. |
| 5 | Coherence test suite | **Automated.** Every Phase 1 bc-sdg run and every Phase 2 catalog change re-evaluates the 8 coherence assertions in section 9. Failure of any assertion fails the run loudly. The *"data settles"* claim cannot erode silently. |

The storyboard is locked. Phase 1 (bc-sdg coherent ledger) starts with explicit emission targets — every named entity, every embedded event, every coherence assertion must be reproducible by bc-sdg.

## Cross-references

- Demo Plan: [CFO Pack Demo Plan](demo-plan-cfo-pack.md)
- ADR: [DEC-28b176 (D394) — Metric Readiness Model](../../../governance/adrs/ADR-28b176.md)
- Toolkit: [Metric Readiness Toolkit](../../../development/metric-readiness-toolkit.md)
- Source: BareCount Context (`OneDrive/BareCount/Documentation/Strategy/BareCount Context.docx`)
- Source: BareCount Concept v2 (`OneDrive/BareCount/Conceptual Presentation/Presentation v2/BareCount Concept v2.pptm`)
- Source: DataJetty Platform deck (`OneDrive/BareCount/Business Presentations/DataJetty Platform.pptx`)
