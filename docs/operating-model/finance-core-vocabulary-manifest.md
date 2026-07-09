---
id: finance-core-vocabulary-manifest
order: 10.86
title: "Finance-core BCF Vocabulary Manifest + Dedup (gap sizing)"
status: drafting
authority: draft-authoritative
depends_on: [business-vocabulary, metric-directory, gl-vocabulary-enrichment-design]
governing_sources:
  - Business Vocabulary (BCF — entity / characteristic / business_concept)
  - The Metric Directory (the value layer these gaps feed)
  - mcf.seed_metric (the demand corpus; 1287 finance seeds)
governing_adrs:
  - DEC-b5c7ff (D506 — Metric Directory)
errata_referenced: []
ratification: analysis pass 2026-07-08 (SES-61fedf); read-only; input to governed BCF authoring decisions
scope_locks: documentation-only; no substrate mutation; no panel run
related:
  - gl-vocabulary-enrichment-design.md
  - metric-directory.md
  - business-vocabulary.md
---

# Finance-core BCF Vocabulary Manifest + Dedup

## Why this exists

Before deciding *how* to fast-track finance-core metric authoring (batched recipe vs building a BCF authoring drive), we needed to know **how many genuine BCF vocabulary gaps finance-core actually has**. This is that count — enumerated from the seed demand, deduped against the existing registry, and adjudicated.

## Method

- **Dedup dictionary:** 172 active `concept_registry.characteristic` terms (the reusable value-properties already governed).
- **Demand corpus:** `mcf.seed_metric`, finance function = **1287 seeds / 23 subfunctions**. The metric directory carries no gap signal (all 111 members `planned`, 0 blockers), so demand came from the seed corpus.
- **Frontier scope:** the 7 untouched core-accounting subfunctions (AR/AP/credit/billing already have vocabulary and MCs): general_ledger (94), revenue_accounting (102), treasury (76), tax (64), fixed_assets (34), cost_accounting (29), cash_flow_management (26) = **425 seeds**.
- **Rubric (applied per subfunction):** noise-filter (drop mis-bucketed metrics) → compose-not-gap (drop ratios/compositions of existing vocab) → anti-duplicate (drop near-synonyms of existing terms — the M5 discipline) → cluster the remainder into the smallest set of vocabulary primitives.
- GL analyzed first-hand; the other six fanned out to per-subfunction agents, then **operator-adjudicated** (the raw agent output over-counted — see caveats).

## Headline findings

1. **The corpus is heavily mis-bucketed and ratio-heavy.** A large fraction of "finance" seeds are misfiled (audit-committee independence, ESG FTEs, EPS/ROE/EBITDA, even `gross_margin_per_hectare`) or are derived ratios that **compose from existing measures**. Effective vocabulary demand is far smaller than 1287.
2. **Vocabulary is a small shared set.** 94 GL seeds → ~2 genuine gaps. Hundreds of metrics reuse a few dozen primitives.
3. **The transactional accounting core is essentially covered.** GL journal-quality is already handled by the `entry method` + `line type` characteristics (authored 2026-07-08) + composition; AR/AP/billing vocab exists. GL adds **zero** new dimensions.
4. **The gaps are ENTITIES, not dimensions — and they cluster in the not-yet-modeled domains:** treasury (financial instruments), fixed assets (asset register), tax (tax types / returns), revenue-recognition (ASC 606), cost (cost centers). These need **new entities**, which are gated on **source availability** (does a tenant actually emit debt instruments, hedges, reconciliation logs, close-task data?), not merely on BCF authoring.

## The adjudicated gap register (~20 structural gaps)

### Track 1 — dimensions/statuses (preflight refined; NOT a clean batch of 7)

Preflight (entity-attachment + dedup) 2026-07-08 refined the "7 dimensions" — only 2 were cleanly authorable; the rest are gated on Track-2 entities, carry M5/compose risk, or intersect a deferred ADR.

| Gap | Kind | Attaches to | Canonical values | Status |
|---|---|---|---|---|
| revenue stream type | dimension | Contract (57bc032a) | recurring, one_time | ✅ **AUTHORED + ACTIVE** — char `825e9233`, concept `8654d362` (2026-07-08). Drives ARR/MRR share. |
| cost type | dimension | Journal Entry Line (07cef8c4) | direct, indirect | ✅ **AUTHORED + ACTIVE** — char `2f8c2acb`, concept `cf08abc6` (2026-07-08). Traceability axis only (the haiku-proposed `fixed/variable/overhead` conflated two axes — dropped; behavior is a separate dimension if needed). |
| cash flow category | dimension | GL Account (bab79e7e) | operating, investing, financing | ✅ **AUTHORED + ACTIVE** — char `24c4042e`, concept `49fc159f`. Reframed: the *metric* composes, but the *vocabulary* is a real per-account IAS-7 attribute, orthogonal to account class code. |
| revenue recognition status | dimension | Customer Invoice Line Item (734d2c51) | recognised, deferred | ✅ **AUTHORED + ACTIVE** — char `fbfa1300`, concept `43ad88f5`. Panel M5-**accepted** the ASC-606 distinction from `status` (contrast: it correctly rejected processing_quality). Reduced to the line-grain coherent subset; unbilled/accrued deferred to a Track-2 Performance Obligation grain. |
| tax type | dimension | (tax-bearing line) | income, vat, gst, withholding… | ⏸ **DEFERRED to DEC-9c430b/D503 + TSK-c9c192** — canonical tax-type classification is that ADR's scope; not front-run. |
| allocation base | dimension | Cost Center | labor_hours, machine_hours, units_produced, direct_cost, headcount, floor_area | ✅ **AUTHORED (2026-07-08)** — char `8322f6e6` on Cost Center (unblocked once Cost Center was built). |
| hedge status | dimension | Hedge Instrument* | hedged, unhedged, partially_hedged | ⏸ **GATED** — needs the Hedge Instrument entity (Track-2, doesn't exist) + `status` M5-risk. |

**Track-1 result: 4 authored (revenue stream type, cost type, cash flow category, revenue recognition status), 1 deferred to D503, 2 gated on Track-2 entities.** Combined with the earlier GL journal dimensions (entry method, line type), **6 finance dimensions are now active.** Lesson: even "dimensions on existing entities" require per-concept modeling judgment (attachment entity, value-set coherence, M5 dedup, compose-check) — Track 1 is not a blind batch, but the panel's M5 gate reliably distinguishes genuine value-properties (revenue recognition status: accepted) from convenience aggregations (processing_quality: rejected).

### Track 2 — entities (recheck 2026-07-08: dedup vs existing registry + source-availability signal)

The manifest's initial "12 entity gaps" over-counted — the analysis agents lacked the entity list. Rechecking against the 136 live entities + the SAP source catalog:

**A. Already covered by existing entities (NOT new entities — add characteristics if needed):**

| Proposed | Existing entity | Action |
|---|---|---|
| Bank Account | **Bank Account** (exists) | Add treasury characteristics if needed |
| Fixed Asset | **Asset** (exists) | ✅ **DONE (2026-07-08)** — added financial characteristics to the Asset entity: acquisition cost (`1c6fa423`), accumulated depreciation (`73dcca83`), useful life (`129057e2`), depreciation method (`4ee97683`). NBV composes (acquisition − accumulated dep). Source-grounded SAP FI-AA (ANLC/ANEP/AFAMA). |
| Capital Project | **Project** (exists) | Add capital/capitalization characteristic |
| Tax Audit | **Audit** (exists) | Add tax characteristics |
| Tax Dispute | **Legal Case** / **Settlement** (exist) | Add tax characteristics |

**B. Genuinely new entities (~6) + source signal:**

| New entity | Subfunction | Source-availability (SAP catalog signal) | Priority |
|---|---|---|---|
| **Cost Center** | cost | ✅ **Available** — `KOSTL` / `0COSTCENTER` / `ACC_ASS_COST_CENTER` catalogued | ✅ **BUILT + ACTIVE** (2026-07-08) — entity `0e1a0035` + `cost center code` (char `2a360a9c`) + reference Journal Entry Line→Cost Center (`51b2d6bd`, role `cost_center`). Unblocks the gated `allocation base` + `cost type` rollup. |
| GL Account Reconciliation | general_ledger | ~ partial — clearing docs (`AUGDT`/`AUGBL`) exist; true GL-account recon logs unconfirmed | Medium |
| Financial Close | general_ledger | Unconfirmed — needs a close-management system | Low (deferred) |
| Debt Instrument | treasury | Unconfirmed — needs treasury system data | Low (deferred) |
| Hedge / Derivative Instrument | treasury | Unconfirmed — needs treasury system data | Low (deferred) |
| Performance Obligation | revenue | Unconfirmed — needs rev-rec system (SAP RAR) | Low (deferred) |

**C. Borderline (probably not entities):**
- **Counterparty** — likely a reference *role* played by Legal Entity / Customer / Supplier, not a standalone entity.
- **Cash Flow Forecast** — an internal planning artifact, not a source-emitted entity; likely out of scope.

**Refined Track-2 result: ~6 genuinely new entities (down from 12), and only ~2 (Cost Center, Fixed-Asset financials) have confirmed source backing in the SAP catalog today.** The rest are genuinely deferred until a source emits their data — authoring them now would produce dead vocabulary. **Recommended first Track-2 target: Cost Center** (source-available, high value, unblocks the gated `allocation base`).

## What is NOT a gap (the reassurance)

- **Covered:** GL journal-quality (entry method + line type), all AR/AP/credit/billing vocab, most measures (gross/net/tax/payment amounts, dates, currencies, rates).
- **Compose:** all the derived ratios — EPS, EBITDA, ROE/ROCE/ROIC, margins, coverage ratios, CCC/DSO/DPO, variances. These are metric-layer formulas over existing vocabulary, not new vocabulary.
- **Noise:** mis-bucketed audit/ESG/exec metrics and industry-specific KPIs (telecom postpaid/prepaid, voice/data/SMS) that leaked into the finance scrape.

## Recommendation

**Do not build a BCF authoring drive.** ~20 genuine gaps does not justify the tooling, and ~12 of them are entities gated on source availability — which can't be batch-authored blindly (that's what would manufacture dead vocabulary). Instead:

- **Track 1 (now):** batch-author the ~7 dimension/status gaps via the proven 4-step recipe (`createCharacteristic → confirm → publish → createBusinessConcept`), with a preflight dedup query against the 172-term dictionary and read-the-review-reason retry discipline. One focused pass clears them.
- **Track 2 (gated):** for each entity gap, do the A-layer source-availability check first (does the pilot/tenant source emit it). Author only the source-backed ones; defer the rest until a source provides the data. This is a per-entity governed decision, not a throughput problem.

## Confidence + caveats

- The ~20 count is an **operator-adjudicated estimate, medium confidence.** The per-subfunction agent passes systematically **over-counted** (listed per-measure attributes separately, proposed dimensions belonging to already-authored subfunctions, and included industry noise); these were pruned/collapsed by hand. The **entity-vs-dimension split and the "gaps are bounded and source-gated" conclusion are robust**; exact primitive names/values are first-draft and get finalized at authoring time through the panel.
- Subfunctions not analyzed (fpa, financial_risk_management, internal_audit, financial_systems, iso_55001, capital_structure, investor_relations, payroll) are largely derived/analytical or non-core; expected to compose from existing vocab or belong to other functions. Revisit only if a specific metric demands it.

## Enrichment execution log — final state (2026-07-08)

The directory was enriched from this manifest. **Final: 198 Metric Directory members, all `bcf_ready`, across all 7 finance-frontier subfunctions** (general_ledger, revenue_accounting, fixed_assets, cost_accounting, tax, treasury, cash_flow_management) plus the pre-existing AR/AP/billing/credit families. Progression: initial enrichment 130 → +30 curated → 160; balance/current-ratio digs → 171; contract value + first-hand re-triage corrections → **198**. **Enrichment mode only — no metric contracts were authored** (declaring intended metrics, not evaluating them).

### Vocabulary authored / bound to enable members
- **Track-1 dimensions:** entry method, line type (GL journal); revenue stream type (Contract); cost type (JE Line); cash flow category (GL Account); revenue recognition status (Customer Invoice Line Item).
- **Cost Center entity** (`0e1a0035`) + `cost center code` + JE-Line→Cost-Center reference.
- **Fixed-asset financials** on the Asset entity: acquisition cost, accumulated depreciation, useful life, depreciation method; `allocation base` on Cost Center.

### Backlog digs (post-enrichment) — dedup-FIRST discipline
| Dig | Gap real? | Action | Result |
|---|---|---|---|
| GL/Bank balance measures | No — `closing`/`opening balance` chars existed | **bind** to GL Account + Bank Account | unlocked total assets/liabilities/equity, cash balance, net movement |
| current/non-current | No — `account type code` already carries `current asset`/`current liability` | **enrich-only** (no authoring) | unlocked working capital + current/quick/cash ratios |
| contract value | **Yes** | **author** (`c1c587e9`, finance-scoped) → bind to Contract | unlocked total/recurring/one-time contract value + ARR/MRR/ACV |
| tax type | **Yes** — routed through **DEC-9c430b/D503** T2 | **author** (`e74f808d`, output/input × regime component, source-agnostic) → bind to invoice lines | enables canonical tax-by-type slicing |

**Scorecard: 2 of 4 "gaps" needed no new authoring** — the vocabulary already existed and just needed binding/applying. Dedup-first is the operating lesson: the agent-reported `NEEDS_VOCAB` backlog is inflated; verify against live vocabulary before authoring.

### First-hand re-triage + correction (2026-07-08)
The initial enrichment leaned on fan-out agents for the candidate lists. A first-hand re-triage of all 7 subfunctions' seeds against the **actual** business concepts found the agent output was **both inflated and shallow** — it over-marked READY (e.g. treasury claimed ~33 READY; reality ~3) *and* missed feasible flagship metrics. Three concrete mistakes:
1. **cash_flow:** members `operating/investing/financing_gl_account_count` counted *accounts*; the flagship metric is the cash-flow **amount** per category. Added `operating/investing/financing_cash_flow` (the account-counts remain, pending archive).
2. **fixed_assets:** `depreciation_expense` is a period *flow*, but Asset carries *accumulated* depreciation (a stock) — not directly READY (NEEDS_VOCAB / derived-Δ).
3. **general_ledger:** reconciliation was over-classified AWAIT_ENTITY — `account_reconciliation_completion` needs only a **reconciliation-status dimension** on the existing GL Account (NEEDS_VOCAB), not a new entity.

**Corrected additive pass (+21 READY-missed members):** cash-flow amounts; GL `journal_entry_processing_cycle_time` / `gl_account_count` / `total_credit_amount` + 6 derived %s; revenue growth-rate / YoY / run-rate / avg-line-items-per-invoice; fixed-assets NBV-per-asset / PP&E-growth; treasury avg-daily-cash-balance / bank cash inflows-outflows.

**Operating lesson:** do NOT trust agent output for feasibility *or* completeness. First-hand triage against live BCs is the reliable method — agents both invent infeasible metrics and miss obvious ones. `cost` and `tax` were confirmed genuinely thin/entity-gated (agent was ~right there).

**Genuine NEEDS_VOCAB identified (not yet authored):** `reconciliation status` (GL Account), `line source method` (JE Line — M5-care vs entry method).

### Layer discipline (source-agnosticism)
The directory and metrics reference only **canonical** vocabulary (e.g. `tax type` values like `output_igst`) — never a source code. Mapping a source's raw codes onto canonical values (e.g. SAP `MWSKZ` → `tax type`) is a **reader/canonical (A/C), per-source-system** concern that belongs to tenant/source onboarding — **not** directory or metric work, and never a universal step. D503-T2 tracks that runtime mapping under TSK-c9c192.

### Remaining backlog (genuine)
- **D503 continuation** (TSK-c9c192): tax jurisdiction / taxable base / recoverable flag; the source-code→canonical-tax-type mapping at the reader/canonical layer (A/C, per source); richer tax metrics (T3); tax-point selector (T4).
- **AWAIT_ENTITY builds** — new entities, each **source-availability-gated** (A-layer check first): Financial Close, GL Account Reconciliation, Debt/Hedge Instrument, Performance Obligation, Capital Project, Tax Return, Cash Flow Forecast.

### Known bc-core defects surfaced during this arc (filed)
- **TSK-386325** — `v_member_realized` counted archived/abandoned MCs as realizations (coverage inflation). ✅ **FIXED** (bc-core `4c71eb4`, CI green): `mc.archived_at IS NULL` added to the derive-view join.
- **TSK-658566** — materialization emits malformed SQL when a fixture omits `section_c_resolver_config_json` (500 + orphan draft). Deferred (off-arch — metric-contract path).

## Track A — coverage addition via existing-entity characteristics (2026-07-09, SES-a366fb)

Operator directive: enrich the directory via **characteristics on entities that already exist** (Track A) + 6 clean new entities (Track B, later). Steer: **entry into dictionary is the target — not data production / metric contracts.** Source availability is a downstream/runtime concern, explicitly out of scope for the blueprint.

**Result: 198 → 244 members (+46), 25 → 30 families (+5). All `planned` (0 blocked — every referenced concept resolves).**

### Part 1 — existing-vocab entries (36 members, ZERO authoring)
First-hand census confirmed the dedup lesson again: **most Track-A characteristics already existed** — the win was entering members from **already-active but unused discriminators/measures**:
| Theme (family) | Discriminator/measure (pre-existing) | Members |
|---|---|---|
| general_ledger / journal_and_close_quality | Journal Entry `status` [draft/posted/reversed/cancelled] | posted/reversed/draft/cancelled counts + **journal_reversal_rate** + draft/cancelled % (7) |
| fixed_assets / **asset_lifecycle** (new) | Asset `status` [operational/in_maintenance/standby/decommissioned] | status counts + utilization/decommission/under-maintenance rates (7) |
| fixed_assets / asset_value_and_depreciation | Asset `depreciation method` [straight_line/…] | method counts + straight-line % (5) |
| revenue_accounting / **contract_lifecycle** (new) | Contract `status` [active/executed/renewed/terminated/expired] | lifecycle counts + renewal/termination/expiry rates (8) |
| accounts_payable / **ap_invoice_workflow** (new) | Supplier Invoice `status` [received/approved/posted/cancelled] | funnel counts + approval/cancellation rates (6) — intent-valid; realization runtime-gated (TSK-999084), a downstream concern |
| revenue_accounting / **order_fulfillment** (new) | CILI `delivered`/`ordered quantity` | total delivered/ordered qty + order fill rate (3) |

### Part 2 — 2 genuine new characteristics authored, then entered (10 members)
Authored via the **OPERATOR-DIRECT path (`POST /api/bcf/registry/characteristics/admission-recommendations` → confirm → publish → `/concepts/authoring-recommendations` → confirm) — NO LLM panel, zero-Anthropic (cost-lean compliant)**. Operator IS the maker; gated on written directive + named published-standard evidence + re-validation at confirm.
- **`reconciliation status`** (dimension, GL Account; concept `3489e93c`; values reconciled/in_progress/unreconciled/discrepancy; IAS/SOX-404 grounding) → new family general_ledger/**account_reconciliation**: reconciled/unreconciled/in-progress/discrepancy account counts + **account_reconciliation_completion_rate** + unreconciled/discrepancy rates (7).
- **`impairment amount`** (measure, Asset; concept `d58c5490`; IAS 36 grounding; distinct from accumulated depreciation + acquisition cost) → asset_value_and_depreciation: total impairment amount + impairment_rate + impairment_to_net_book_value (3).

### Recipe additions learned (operator-direct authoring)
1. **Two zero-LLM surfaces exist** — characteristic admission + business-concept authoring — the cost-lean way to admit vocabulary when the operator has authorized it and named evidence exists. Not a semantic bypass (confirm re-validates name-conflict, grammar floor, F4-v2 checklist).
2. **`dataType` differs by surface:** characteristic-admission `dataType` is surface-only (F3 ignores; enum text/currency-amount/…); **BC-authoring `dataType` is `BCF_DATA_TYPES` = string|integer|decimal|boolean|date|timestamp|json** (use `string` for a code dimension, `decimal` for a monetary measure).
3. **`registry-publications/confirm` requires `rationale` (≥40)** + `semanticFinalityAffirmed:true` for a characteristic.
4. Confirm pairings: characteristic → `{characteristic, registry_author_vocabulary}`; BC create → `{business_concept, registry_create}` (auto-activates, no separate publish).
5. Metric-directory API is snake_case + `{data}`-enveloped; BCF authoring API is camelCase.

### Deferred NEEDS_VOCAB backlog (Track A remainder — NOT authored; recorded for a later governed pass)
Each is a real gap but held for one of: M5 near-dup risk (needs panel review, never a blind operator-direct admission), murky grain, or lower value. Author only with dedup-first + read-the-review-reason discipline.
- **`line source method`** (JE Line) — M5-care vs `entry method`/`line type`.
- **`accrual flag`** (Journal Entry) — M5 risk vs `entry method`.
- **`maintenance cost`**, **`revaluation surplus`** (Asset measures) — genuine but murkier grain (maintenance is event-based; revaluation is IFRS-model-specific).
- **standard cost / actual-vs-standard variance** (cost accounting) — no clean source grain for *standard* cost (planning data); actual cost already covered via JE-Line cost-type amounts.
- **transfer-pricing classification**, **deferred tax**, **recoverable-tax flag / taxable base** — route through D503 (TSK-c9c192).
- **sales channel / region** (revenue) — likely reference-role/CRM context; revisit if a metric demands it.
- **contract expansion / churn markers** — needs customer-level tracking; revisit with revenue-retention work.

## Track B — 6 new entities → directory members (2026-07-09, SES-be98c9)

Operator directive: after Track A, create the 6 clean new entities and enrich each into the directory. Same steer — **entry into dictionary is the target; source availability is downstream/out of scope.**

**Result: 244 → 295 members (+51), 30 → 36 families (+6). All `planned` (0 blocked). 6 new BCF entities created + enriched.**

### Authoring pattern (per entity)
1. **Create entity via the BCF panel** (`POST /api/bcf/registry-authoring-runs` `operation:createEntity`). New-entity creation has **no operator-direct surface** — the panel is required (Opus maker, locked roster). But `createEntity` **auto-authors on a clean APPROVE** (`operator_confirm_required=false` for entities; the high-risk operator-confirm parking is characteristic-only) — one panel run, no confirm dead-end. All 6 returned `kind:authored`, `lifecycleState:active` first try (grounding = evidence-cited + non-colliding name).
2. **Author its measures/dimensions via the operator-direct zero-Anthropic path** (as Track A Part 2).
3. **Enter directory members** via the gated `/api/metric-directory` API.

### Entities + families
| Entity (id) | Subfn / theme (new family) | Chars authored (operator-direct) | Members |
|---|---|---|---|
| Debt Instrument `bc3829f5` | treasury / debt_and_leverage | principal amount, debt type | 11 (count/by-type + total principal + D/E, net-debt/EBITDA, DSCR, avg) |
| Financial Close `c262f1c3` | general_ledger / financial_close | close status, close type | 9 (by-cadence/status counts + cycle time, on-time/delayed rate) |
| GL Account Reconciliation `a811010b` | general_ledger / reconciliation_events | reconciliation outcome | 7 (outcome-mix counts + cycle time, adjustment/overdue rate) — the EVENT grain, distinct from Track-A reconciliation-status % on GL Account |
| Hedge Instrument `9e270a91` | treasury / hedging | notional amount, hedge type | 7 (by-type counts + total notional + effectiveness, avg notional) |
| Performance Obligation `fc7f48ab` | revenue_accounting / performance_obligations | allocated transaction price, obligation satisfaction status | 8 (satisfaction-mix counts + allocated price + satisfaction rate, backlog, unbilled) |
| Tax Return `0c2baf29` | tax / tax_filing_compliance | filing status, return type | 9 (by-status/regime counts + timeliness, compliance, rejection rate) |

### Notes
- **GL Account Reconciliation** dedup: kept distinct from Track A's `reconciliation status` (a current-state % on GL Account) — this is the per-record **event** grain (cycle time, outcome mix). Term uniqueness forced a distinct char name (`reconciliation outcome`).
- Cross-entity derived members (D/E, net-debt/EBITDA, DSCR, revenue backlog, unbilled revenue) are **intent-only** (name+class) under their theme — the directory blueprints the intended metric; its realization composes inputs at authoring time.
- All 6 entity families are directory intent — several members' realization is source-availability-gated downstream (out of scope for the blueprint per the operator steer).

**Track A + B combined: directory 198 → 295 members (+97), 25 → 36 families (+11), 8 new BCF entities/characteristics + 2 Track-A characteristics, all via governed services (panel for entities, operator-direct zero-Anthropic for vocabulary, gated API for members).**

## Track A NEEDS_VOCAB — panel-reviewed pass (2026-07-09, SES-c57954)

Ran the 4 finance-scoped deferred dup-risk candidates through the **BCF panel** (`createCharacteristic`) so the panel adjudicates M5 near-duplication — the arbiter these were held for. Read each `verdict_payload_json->>'review_reason'` (all parked `OPERATOR_REVIEW`, the panel's procedural default for new vocabulary; the *reason* is what discriminates). **Result: directory 295 → 301 members (+6).**

| Candidate | Panel `review_reason` (verbatim gist) | Disposition |
|---|---|---|
| **line source method** (JE Line) | **M5 synonym collision** with active `entry method` — "same value-property… line-grain framing does not create a distinct substrate property; header-to-line inheritance is a BC binding concern" | **RESPECTED — rejected.** Not authored. Insight: line-grain origination = *bind* `entry method` to JE Line, not a new characteristic. |
| **maintenance cost** (Asset) | Grain wrong — "asset-lifetime aggregation (derived), not a single-instance value-property; admissible base grain is per-maintenance-order cost"; evidence attests treatment not a carrier field | **RESPECTED — deferred.** Needs a Maintenance Order grain entity + named-system evidence. Validates the "murky grain" deferral. |
| **revaluation surplus** (Asset) | "Maker and Checker agree the meaning is sound and the term is not a synonym"; only fails the function_scoped **2-source evidence precondition** (SCOPE_PRECONDITION_FAILED) | **AUTHORED** via operator-direct with the required 2nd source (IAS 16 + FRS 102 §17 + SAP FI-AA revaluation reserve). Members: `total_revaluation_surplus`, `revaluation_surplus_to_carrying_value`. |
| **accrual indicator** (JE) | Semantic overlap flagged, but "**Operator must confirm whether this is a genuinely distinct value-property** (boolean accrual/deferral orthogonal to origination)" | **AUTHORED** via operator-direct — operator determination: accrual/deferral basis IS orthogonal to origination (a *manual* entry can be an accrual; an *automated* entry can be cash-basis). Members: accrual/deferral/cash-basis JE counts + `accrual_entry_percentage`. |

**Discipline note:** the two authored candidates were panel-*cleared* (sound + not-a-dup, or explicitly deferred-to-operator), not forced past a semantic objection. The one hard **M5 dup (line source method) was respected and rejected** — the panel doing its job. Both authored via operator-direct (zero-Anthropic) with `priorPanelRunUidReference` audit linkage to their panel runs.

**Still deferred (out of this pass, unchanged):** tax gaps → D503/TSK-c9c192; sales channel/region + contract expansion/churn → need customer-level reference context; standard-cost variance → no source grain; maintenance cost → needs a Maintenance Order entity.

**Track A (full) + B combined: directory 198 → 301 members (+103), 25 → 36 families (+11).**

## Genuinely-remaining — completed to logical end (2026-07-09, SES-7d7d6e)

Closed every remaining NEEDS_VOCAB item to a definitive end (authored, or scoped-out with a documented reason) so it is not revisited. First-hand assessment corrected several earlier assumptions (grains that were thought missing already exist). **Result: directory 301 → 318 members (+17), 36 → 39 families (+3).**

### AUTHORED (grain existed; operator-direct zero-Anthropic, or panel-approved)
| Item | Grain (existing entity) | Vocab authored | Members |
|---|---|---|---|
| **maintenance cost** | **Maintenance Order** (existed — no new entity) | maintenance cost (measure) — at the per-order atomic grain the panel demanded | fixed_assets/**asset_maintenance**: order count, total maintenance cost, cost-per-order, cost-to-book-value (4) |
| **standard cost** | **Product** (existed) | standard cost (measure) — ERP standard price IS source-observable, resolving the "no grain" deferral | cost_accounting/**product_costing**: total standard cost + standard-to-actual variance, variance %, purchase-price variance (4) |
| **contract expansion/retention** | Contract (no new vocab) | — (derived intent from contract value) | revenue_accounting/contract_lifecycle: net & gross revenue retention, expansion revenue, contract-value growth (4) |
| **tax recoverable indicator** | **Supplier Invoice Line** (existed) | tax recoverable indicator (dimension: recoverable/non_recoverable/partially_recoverable) — **BCF-panel-APPROVED** (`awaiting_operator_confirm`, run 8ef06cdc), completed | tax/**input_tax_recovery**: recoverable/non-recoverable line counts + amounts + recovery rate (5) |

### SCOPED-OUT — documented logical end (NOT authored)
| Item | Disposition |
|---|---|
| **region / geography** | **DEDUP — no new vocab.** Customer already carries `country code`, `territory code`, `industry code` (all active dimensions). Geographic/segment analysis is a high-cardinality *slicing dimension* over existing revenue members (via the CILI→Customer reference), not enumerable per-value directory members. Available now; nothing to author. |
| **sales channel** | **CRM-domain gap.** No channel concept on any onboarded source; addable only when a channel-carrying source is registered. Not a core finance-substrate gap. |
| **taxable base** | **RESPECTED panel park (probable synonym).** Panel (run d58a7814): probable M5 collision with active `line extension amount` — "both denote the amount a tax rate is applied to"; the distinct case (partial exemption / mixed rate → multiple taxable bases per commercial line) is plausible but unsubstantiated by generic evidence. Common case = `line extension amount` (use it). The genuinely-distinct case needs per-source tax-procedure record-structure evidence → **D503 T3**. |
| **deferred tax** | **→ D503 T3.** Needs a deferred-tax GL-account sub-classification (account-type value), not a new measure — a tax-accounting balance-classification concern in the D503 workstream. |
| **transfer-pricing classification** | **→ D503 T3.** Transfer-pricing *method* dimension (cost-plus / resale-minus / CUP / profit-split) on intercompany transactions — deeper tax modeling, D503. |
| **standard-cost deep variance decomposition** | Standard cost + basic variance (above) covers the intent. Full price/usage/mix decomposition needs production volume + consumption data (Production Run / material movements) — a future manufacturing-costing extension, not a finance-substrate vocab gap. |

**Discipline:** operator-direct only for clean non-dup measures; the two tax candidates went through the **panel** for M5 adjudication — `tax recoverable indicator` cleared (authored), `taxable base` flagged a probable synonym and was **respected (not authored)**. No park was forced.

**Finance directory frontier — final: 198 → 318 members (+120), 25 → 39 families (+14).** All remaining items are either authored or closed with a documented reason (region=dedup; channel=CRM; taxable base/deferred tax/TP=D503 T3; deep variance=manufacturing-costing). No open finance-vocabulary backlog remains.

## Domain-knowledge completeness pass — the reporting/derived layer the seeds missed (2026-07-09, SES-475b39)

Operator prompt: review families/members for KPIs that domain knowledge says exist but the (transaction-grain) seeds never surfaced. First-hand audit of all 318 members found the directory deep on transaction metrics but **missing the entire reporting/derived layer** a finance professional lives by. **Result: directory 318 → 361 members (+43), 39 → 47 families (+8).** All additions are DERIVED intent (name+class) — zero new vocab except the Budget entity/measures — grain = Legal Entity (entity-level reporting), Asset (CapEx), Supplier Invoice (AP discount), Budget (FP&A).

### AUTHORED — new reporting families (derived intent, no vocab)
| Family | Members (flagship KPIs that were entirely absent) |
|---|---|
| financial_reporting/**profitability** | COGS, gross profit, operating income (EBIT), EBITDA, net income + gross/operating/EBITDA/net margins (9) |
| financial_reporting/**returns_and_efficiency** | ROA, ROE, ROCE, ROIC, asset turnover (5) |
| financial_reporting/**solvency** | debt-to-assets, equity ratio, financial leverage, net debt, net-debt-to-equity (5) |
| cash_flow_management/**free_cash_flow** | free cash flow, FCF margin, operating-cash-flow ratio, cash-flow-to-debt, capex-to-OCF (5) |
| fixed_assets/**capital_investment** | CapEx, capex-to-revenue, capex-to-depreciation, fixed-asset turnover (4) |
| tax/**tax_rate_analysis** | effective tax rate, cash tax rate, book-tax difference (3) |
| treasury/**working_capital** | cash conversion cycle, days working capital (2) |
| accounts_payable/ap_payment_and_dpo (add) | early-payment discount capture rate, discount lost (2) |

### AUTHORED — FP&A layer (was entirely empty): Budget entity built (panel) + variance
`Budget` entity `63445ca2` (EPM planning grounding) + `budget amount` (measure) + `plan version` (dimension: budget/forecast/latest_estimate/actual), operator-direct → **fpa/budget_and_variance**: budget line count, total budgeted/forecast amount + budget variance, variance %, budget attainment rate, forecast accuracy, expense budget utilization (8).

### DOCUMENTED out-of-scope (needs data the finance transaction substrate doesn't carry)
- **Investor-market metrics** (EPS, P/E, market cap, book value per share) → need a market-data source (share price, shares outstanding). Dividend payout/retention are computable but low-priority; addable later.
- **Inventory metrics** (DIO, inventory turnover, days inventory) → need an Inventory entity/balance; cash-conversion-cycle is declared but its DIO term composes from inventory once onboarded.
- **Cost-of-capital** (WACC, cost of debt/equity) → need market rates.
- **Financial-risk models** (VaR, stress exposure) → need risk-model inputs beyond the ledger.

**Why this mattered (accuracy + coverage):** the seed catalog is transaction-grain, so the P&L subtotals, margins, return ratios, free cash flow, and effective tax rate — the metrics executives and investors actually watch — never appeared. These are not padding; they are the textbook core of financial analysis and were the single largest coverage gap. **Lesson: seed-driven enrichment must be paired with a domain-expert reporting-layer sweep — the most important metrics are often the derived ones no source row emits.**

**Finance directory — final after domain pass: 198 → 361 members (+163), 25 → 47 families (+22).**
