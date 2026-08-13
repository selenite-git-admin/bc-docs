---
id: demo-estate-max-coverage-rescope
title: "Demo-Estate Max-Coverage Re-scope — bc-demo v2.1 build reoriented to widest metric horizon"
status: approved
authority: derived
depends_on: [demo-estate-metric-coverage, demo-estate-module-coverage, demo-estate-simulator-requirements]
governing_sources:
  - D566 (bc-demo v2 simulator-as-product)
  - "operator direction 2026-08-13: yes, re-scope for max coverage and promote the docs"
---

# Demo-estate max-coverage re-scope (bc-demo v2.1)

## The reframe (operator, 2026-08-13)

**Data is NOT the demand of a metric — it is the other way round.** A rich module/data
surface lets us onboard the maximum metrics and gives the widest-horizon demo. The world's
job is to emit a realistic company's *full exhaust*; metric coverage then grows platform-side
against a world that never changes (the "end-game rings" in `demo-estate-metric-coverage.md`:
slate → data-latent (zero world-work) → world-latent (a named unit) → out-of-world).

**Consequence for the build:** never strip a module or data surface to satisfy an economic
gate. Gates *shape* the economics; they do not get to *narrow* what the world emits. If a gate
and a coverage surface conflict, fix the gate.

**Anchor numbers:** seed reservoir `mcf.seed_metric` ≈ 12,500 rows across ~21 functions /
~210 subfunctions (in master, expandable); finance directory ≈ 430 members over 13
subfunctions (curated from the ~1,250 finance pool). Finance is DEEP; adjacent functions are
THIN (one layer) but chosen so each also deepens finance realism.

## Current bc-demo v2.1 coverage vs the pilot target

The pilot world (bc-sdg) supports ~340/380 finance members and runs CRM + work-centres +
quality-scrap. bc-demo v2.1 is currently **thinner**, and a recent margin fix regressed it:

| surface | pilot | bc-demo v2.1 now | unlocks |
|---|---|---|---|
| GL / AR / AP / revenue / tax / treasury / cash / billing | full | **covered** | most of finance (≈340) |
| cost_accounting (work-centre absorption, WIP) | full | **REGRESSED — workorders dropped** | cost_accounting (10) + Mfg slate |
| perpetual AVCO valuation | full | covered (reval-leak fixed via jitter, but guard trips at realistic variance) | inventory / cost |
| CRM pipeline (leads, stages, lost reasons, campaigns) | exercised | **empty (installed, no data)** | Sales/CRM slate (corpus 554) |
| HR employees / departments / payslips | unused | **partial (employees only, JE payroll)** | HR slate (corpus 1,175) |
| Quality (scrap/rework documents) | thin | **empty** | Quality slate (corpus 86) |
| Supply-chain / inventory ops | full | covered (data-latent) | SC slate (corpus 1,099) — zero world-work |

## Build units to close the delta (each maps to a metric slate)

Sequenced so the blocker and the regression land first, then the horizon widens.

1. **U1 — AVCO-aware reval guard (blocker, doctrine-correct).** The flat ₹100k
   `reval_leak_guard` cannot accommodate legitimate perpetual-AVCO cost-averaging residual at
   realistic RM price variance (both-signs, oscillating; ±2% jitter still trips it at month 4
   per smoke v2rw4). Distinguish the *structural* leak class (S-49 one-directional double-debit)
   from the *measurement* residual: allow the reval to true GL→physical when the two independent
   Odoo inventory measures agree (`stock.quant.value` == Σ `stock.move.remaining_value`) and the
   drift oscillates; guard only the structural class (volume-relative + directional). Failure-inject
   an S-49-class leak to prove it still reds. **This lets RM price variance stay realistic** instead
   of forcing ±0% jitter — realism preserved, not stripped.

2. **U2 — Restore work-centres / workorders (undo the regression).** Re-enable costed
   workorders (the margin fix wrongly set `fg_minutes_per_unit=0`). Conversion cost stays on the
   COGS charge (already decoupled), so workorders exist purely for **cost_accounting** (work-centre
   absorption, WIP) and the **Manufacturing** slate (capacity-utilisation proxy, open-WO backlog).
   Duration model: the pilot ran realistic per-unit minutes and accepted multi-week batch durations;
   adopt the same, and if DQ-01 date-stamping conflicts with planned workorders, unplan-before-stamp
   or stamp only writable fields (do not drop the workorder).

3. **U3 — CRM pipeline lifecycle.** Leads → opportunities → stages → won → SO (with lost reasons
   and campaigns), so the CRM app carries data. Unlocks the **Sales/CRM slate**: pipeline
   conversion, win rate, average deal size / revenue per customer, campaign-attributed lead volume
   — plus the CRM corpus's data-latent ring.

4. **U4 — MASTER.5 (HR depth).** Departments + payslips + join/exit dates over the window (+ thin
   attendance, cheapest to cut). Employees already exist. Unlocks the **HR slate**: headcount by
   company/department, payroll cost per FTE, voluntary attrition, absence rate. Masters are addable
   to a built world without rebuild; historical payslips derive from the posted payroll GL bands.

5. **U5 — Quality-via-scrap.** Formalize QA-rejection + scrap-at-carrying-value documents (the
   quality *module* stays inert by design — 0 quality points). Unlocks the **Quality slate**: QA
   rejection rate, cost of poor quality.

6. **U6 — Supply-chain metrics (data-latent, zero world-work).** Inventory turns, days-of-inventory,
   shrinkage %, supplier concentration, OTIF proxy — already emitted; metric-side build only.

## Non-goals (unchanged from the coverage plan)

FP&A budget objects (operator call), IGST/inter-state, e-invoice/e-way-bill filing (limitation
L-007 — documents carry filing-ready data), and any out-of-industry app (Website, POS, eCommerce,
Events, Recruitment marketing, Field Service). Thin means thin; the rings say what comes later.

## Definition of done

bc-demo v2.1 full 41-month build (2023-04 → 2026-08) green, with: work-centres + WIP present,
CRM pipeline populated, HR masters + payslips present, quality-scrap documents present, finance
gates in band (gross margin ~35% via the conversion COGS charge), and the AVCO-aware reval guard
holding at realistic RM price variance. Then the finance directory (~430) and each adjacent slate
are hand-spot-checkable from world data, and the data-latent rings are open for platform-side
onboarding with zero further world-work.
