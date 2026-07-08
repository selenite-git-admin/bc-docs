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
