---
uid: DEC-d308de
title: "Re-scale Profile #1 (mfg-in) to a Tier-1 auto-component supplier at target-buyer scale, with an OEM-concentrated customer master"
description: "Profile #1 moves from a ~₹6 Cr SME job-shop to a ~₹3,000 Cr Tier-1 auto-component group; customer master becomes OEM-concentrated, which is both the realism fix and what keeps document volume tractable."
status: decided
date: 2026-08-04T07:25:13.591Z
project: bc-synth
domain: sources
subdomain: pilot-source/odoo-profile
focus: archetype-scale
---

# Re-scale Profile #1 (mfg-in) to a Tier-1 auto-component supplier at target-buyer scale, with an OEM-concentrated customer master

## Context

The platform's target buyer is a company that can afford SAP and a CRM suite — practically, ₹1,000 Cr+ turnover. Profile #1 was built at ~₹6 Cr per entity, roughly 500× too small: a world at that scale demonstrates the platform to nobody who could buy it. Bajaj Auto is a live demo prospect, which makes a *supplier to Bajaj* the natural archetype.

## Why an ADR rather than a calibration pass

This changes what the profile IS — customer shape, document volume, entity structure — not merely its parameters. Calibration was explicitly paused (SES-b5642e) pending this decision, because tuning toward a superseded target wastes the work. Per D221/D334 a change of this kind belongs in a recorded decision rather than drifting there through tuning.

## Evidence

**Primary sources, both audited filings, both accepted ONLY after arithmetic reconciliation** of income, expenses, PBT, PAT and balance sheet (a first extraction produced cost-of-materials EXCEEDING revenue — two-column PDF decoupling labels from figures — and was discarded rather than reasoned around):
- Sona BLW Precision Forgings ("Sona Comstar") FY2024-25 consolidated, auditor Walker Chandiok & Co LLP — revenue ₹3,546 Cr
- Sansera Engineering FY2024-25 consolidated — revenue ₹3,017 Cr
- Craftsman Automation, SECONDARY and indicative only — ₹5,690 Cr, net margin 3.5% FY25 / 7.6% FY24. The secondary source printed FY24 profit as "₹33733 Crores", a corrupted figure, which is precisely why primary filings are required.

Full citations and reconciliation proofs: `bc-sdg/pilots/profiles/mfg-in/research/SOURCES.md` and `FINDINGS.md`.

**Measured build cost** (phase instrumentation, 12-month build): document creation 78.7%, coverage journals 16.0%, manufacturing orders 5.1%, scrap 0.2%. This measurement is what made the document-volume question answerable rather than speculative — and it corrected an earlier assumption that manufacturing was the expensive part.

## Why OEM concentration is the pivot

Concentration is usually argued for on realism grounds alone. Here it also resolves the cost objection, because a Tier-1's OEM revenue arrives in few large scheduled invoices rather than many small ones. Modelling it therefore makes the world both more realistic AND cheaper to build — the rare case where the two pull the same way. The earlier 40–120h estimate treated the whole book as SME-sized invoices and was wrong by 4–10×.

Concentration is also, arguably, the single most important realism property for the intended demo: a supplier's books that a Bajaj audience would recognise must show a handful of dominant OEM accounts, long-term price agreements and scheduled deliveries — not 200 scattered customers ordering at random. No gate currently tests it.

## Alternatives considered

- **Keep the ₹6 Cr scale.** Rejected: no target buyer resembles it, and the loans, credit limits and audit fees already encoded in the profile describe a much larger company, so the world was internally inconsistent anyway.
- **Model one plant of a larger group.** Rejected as unnecessary once the arithmetic showed full-group volume is only ~3×. It remains the fallback if per-despatch invoicing is later required.
- **Shorten the window to 2–3 FY.** Rejected for now: five fiscal years is what makes trend and seasonality metrics meaningful. Available as a lever if build time becomes binding.
- **Inflate invoice values instead of counts.** Rejected outright — it would corrupt DSO, ageing buckets and invoice-size distribution, which are exactly the metrics a CFO reads. This is the plausible-but-not-real failure mode in its purest form.
- **Parallelise the build with threads.** Rejected: determinism ("same seed ⇒ same world") is load-bearing for registry reproducibility, catch-up runs and gate comparison. Batched multi-record creation achieves the speedup while preserving ordering.

## Consequences

**Requires:**
- `master_gen` customer generation rewritten for three segments with concentration; registry regenerates.
- Sales generation to respect segment cadence and price agreements rather than uniform random orders.
- BoM material-cost band moved from ~49% toward 42–45%.
- Expense, loan and credit-limit constants re-derived for ~₹3,000 Cr.
- A NEW GATE for customer concentration — the property is currently untested.
- Batched record creation to keep build time near ~6h.

**Accepts:**
- Build time roughly triples (~4h → ~11h naive) for the 5-FY window.
- Existing `ITEM-####` / `VEND-####` identities are preserved; `CUST-####` identities change shape, so any cross-system projection of the customer master is invalidated and must be regenerated.

**Provisional until further research lands:** RBI "Performance of the Private Corporate Business Sector" (ratios by industry AND size class — the instrument that prevents a ₹3,000 Cr supplier inheriting a ₹40,000 Cr company's ratios); ACMA FY24 industry aggregates; a PRIMARY commodity-grade comparable (Rico, Jamna, MM Forgings) to anchor the low-margin end, since Sona is a high-margin outlier; and published OEM customer-concentration data.

The calibration bands in this decision are therefore declared PROVISIONAL. They are evidence-backed but rest on two comparables, one of which is atypical.

## Decision

Profile #1 (`mfg-in`) is re-scaled from a ~₹6 Cr-per-entity SME job-shop to a **Tier-1 automotive-component group of ~₹3,000 Cr**, and its customer master becomes **OEM-concentrated**.

The profile CODE and archetype family are unchanged — it remains an Indian, B2B, discrete-manufacturing, Ind AS, multi-entity world. What changes is scale, customer shape and document mix. This is a new version of Profile #1, not Profile #2.

### 1. Target scale

| entity | revenue | note |
|---|---|---|
| Bharat Precision Industries | ~₹1,500 Cr | flagship; exports; imports |
| Shree Engineering Works | ~₹900 Cr | |
| Kirti Tooling | ~₹600 Cr | |
| **group** | **~₹3,000 Cr** | |

Chosen to sit inside the verified comparable band: Sansera ₹3,017 Cr, Sona Comstar ₹3,546 Cr, Craftsman ₹5,690 Cr (see Evidence). The 50/30/20 entity split is retained.

### 2. Customer master becomes OEM-concentrated

Replacing 200 undifferentiated customers ordering at random with three segments:

| segment | share of revenue | customers | invoicing cadence | avg invoice |
|---|---|---|---|---|
| **OEM** | 60% | ~8 | scheduled, weekly-consolidated | ~₹1.9 Cr |
| Tier-2 / industrial / export | 28% | ~50 | monthly | ~₹70 lakh |
| Aftermarket / spares / job work | 12% | ~150 | occasional | ~₹20 lakh |

OEM accounts carry long-term price agreements and scheduled deliveries rather than independent random orders.

### 3. Document volume — the corrected finding

**The OEM concentration in (2) is not only a realism fix; it is what makes (1) affordable.** These are the same change.

An earlier estimate in this workstream put a ₹1,000 Cr+ world at 500–1,600 invoices/month and a 40–120 hour build. **That estimate was wrong.** It assumed ₹5–50 lakh invoices across the whole book — the SME/aftermarket profile — whereas a concentrated Tier-1 invoices OEMs in large scheduled despatches. Re-derived per segment:

- ~1,980 invoices/year for the flagship ⇒ **~165/month, against ~52 today — 3.2×, not 30×**
- Build time **2.83×** overall (documents and manufacturing scale; coverage does not, being a fixed count of chart-of-accounts journals)
- A 5-FY build goes **4h → ~11.3h naive**, or **~6.3h** with batched record creation

**Sensitivity — OEM invoicing cadence is the swing factor and is itself a profile parameter:**

| cadence | invoices/month | docs | 5-FY build |
|---|---|---|---|
| fortnightly | 141 | 2.7× | ~9.8h |
| **weekly (adopted)** | **165** | **3.2×** | **~11.3h** |
| twice-weekly | 205 | 3.9× | ~13.9h |
| per-despatch daily | 292 | 5.6× | ~19.5h |

**Weekly-consolidated OEM invoicing is adopted** — realistic for the segment and the least costly realistic option. Per-despatch daily invoicing is also realistic but nearly doubles build cost for no metric-visible gain.

### 4. Calibration targets (PROVISIONAL)

From two arithmetic-reconciled primary filings. **Provisional pending the outstanding research in Consequences.**

| measure | evidence | provisional target |
|---|---|---|
| Cost of materials / revenue | 43.0% (Sona), 42.6% (Sansera) | **42–45%** — current BoM design targets ~49% and must come DOWN |
| Net margin | 3.5%–16.9% observed | band floor lowered to **~3%**, centred 7–8% (current 4–15% floor is too high) |
| Other income / total income | 0.7%, 3.8% | 12% ceiling **retained** — validated as defensible |
| Short-term borrowing ÷ working-capital gap | 29.2%, 104.6% | `FUNDED_SHARE = 0.60` **retained** — now evidence-backed |
| DSO | 55–73 days | adopt as a band |
| DIO (on material cost) | 84–142 days | adopt as a band |
| DPO (on material cost) | 78–103 days | adopt as a band |

### 5. What explicitly does NOT change

All structural work from the inventory/MRP increment is scale-independent and is retained unmodified: the chronological forward loop; perpetual AVCO valuation; anglo-saxon COGS; the BoM cost-design method; demand-driven purchasing; replenishment production; the cash-credit drawing-power model; every gate; and every defect fix. Only numeric calibration and the customer master are affected.

### 6. Bajaj Auto is the customer reference, not the archetype

Bajaj Auto (~₹40,000 Cr) is an OEM and a live demo prospect. The pilot world models **a Tier-1 supplier to such an OEM** — the books a supplier would recognise — not the OEM itself. A ₹40,000 Cr OEM's ratios must not be borrowed for a ₹3,000 Cr supplier.
