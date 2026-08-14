---
id: demo-estate-metric-coverage
title: "Demo-Estate Metric Coverage — finance deep, adjacent worlds one layer thick (coverage → metrics)"
status: approved
authority: derived
depends_on: [demo-estate-simulator-requirements, demo-estate-module-coverage]
governing_sources:
  - DEC-8b17b1 (D561 demo-estates doctrine)
  - D566 (bc-demo v2 simulator-as-product)
  - "operator direction 2026-08-13: re-scope for maximum coverage; data is NOT the demand of a metric — rich module/data coverage onboards the maximum metrics and widens the demo horizon"
---

> **Promoted to SSOT 2026-08-13** (was `artifacts/odoo-pilot/SOFT-TARGET-METRICS-pilot.md`, PROPOSAL). This is the standing coverage plan for the **demo-estate program** — both the Odoo *pilot* (bc-sdg testbed) and **bc-demo v2.1** (the shipped demo estate, D566). The per-subfunction finance verdict below was measured against the pilot world; **bc-demo v2.1 must reach the same coverage**, and any build change that STRIPS a module/data surface to satisfy a gate is a regression against this plan (see `demo-estate-max-coverage-rescope.md`). Seed numbers refreshed since: metric directory has grown 380 → ~430 members.

# Demo-estate soft-target metric coverage — finance deep, adjacent worlds one layer thick

Date: 2026-08-08 · Status: **PROPOSAL for operator soft-agreement** (promotes to bc-docs on
agreement) · Sources, measured: `mcf.seed_metric` (12,507 rows; finance 1,287 with 1,210
candidate) and the metric directory (380 active members, all finance, 13 subfunctions,
realized=380 per `v_member_realized`).

## Doctrine (locked before any list)

This is a **soft agreement for program focus, never a demand gate**. Source-as-backbone
stands: readers stay function-scoped and source-agnostic; SC/AC/OC/CC chains are built from
what the source system emits, and world completeness flows from realism. The list below says
*what the pilot intends to demonstrate*, so that world-building, close content, and chain
work pull in one direction — the operator's framing: **the HR organization gives the books
meaning AND enables HR metrics to a stated depth; both directions, one investment.**

## 1. Finance — DEEP (the 380-member directory is the spine)

The directory is already the curated deep set. What the pilot adds is the world-support
verdict per subfunction, measured against what the mfg-in world actually produces:

| directory subfunction | members | world support today | gap / dependency |
|---|---|---|---|
| general_ledger | 78 | **Full** — 64-month GL, per-company charts, fiscal calendar | — |
| accounts_receivable | 59 | **Full** — invoices, collections, advances, late fees, bad debt | provision for doubtful debts absent (close-content list) |
| accounts_payable | 41 | **Full** — bills, payments, import charges, named vendors | vendor-payment TDS = L-006 (accepted) |
| revenue_accounting | 41 | **Full** — domestic + export, GST treatments, scrap/service income | unrealised FX = L-003 (accepted) |
| fixed_assets | 34 | **Strong** — opening register, monthly depreciation, capex | no asset revaluation/impairment (annual list) |
| financial_reporting | 28 | **Strong** — trial-balance-level; Schedule III is presentation-layer | — |
| treasury | 28 | **Strong** — term loans (non-current, W15), CC revolve, OD, bank recon | — |
| tax | 20 | **Full (rc3)** — GST set-off (D556 act 1), monthly income tax, **+ U6 statutory filing: e-invoice/IRN status, e-waybill records, monthly GSTR-1/3B filings (synthetic artifacts)** unlocking filing-timeliness / e-invoice-coverage / GSTR↔books-reconciliation compliance metrics | advance-tax phasing = L-004; ITC ordering = L-001; live IRP/GSTN submission not simulated (L-007, refined) |
| credit_and_collections | 13 | **Full** — terms, credit limits, ageing-capable data | — |
| cash_flow_management | 12 | **Full** — statement headers + lines, suspense cycle | — |
| fpa | 11 | **Partial** — actuals only; no budget objects in world | budgets = candidate close/master content, operator call |
| cost_accounting | 10 | **Strong** — perpetual AVCO, work-centre absorption, WIP (W14) | overhead apportionment beyond routing = close-content list |
| billing | 5 | **Full** | — |

**Soft target: ~340 of 380 members supportable at gate-green world state** (→ **high-370s with rc3's
U6 statutory-filing surface**, which sources the previously-out-of-scope tax/compliance filing
metrics); the small remainder sits behind named, already-tracked decisions (fpa budgets,
doubtful-debt provision, apportionment depth) — no silent gaps. Proven in v2rwrc3 (BUILDDONE GREEN,
2026-08-14): finance + adjacent slates all world-sourced, economics in-band (per-FY PAT 6.8/6.8/10.7%),
U6 filing at 100% e-invoice / e-waybill-per-qualifying / GSTR-per-company-month.

## 2. Adjacent worlds — THIN (one layer, seed-grounded, each names its prerequisite)

Selection rule: a thin metric earns its place only if (a) the world can source it from data
that *also* deepens finance realism, and (b) it is one layer — no sub-function drill-downs.

**How to read each header:** "corpus: N" is the size of the seed universe the slate was
selected FROM — it grounds the picks in the real corpus and claims nothing about support.
The support claim ("world sources it today" / "requires X") applies ONLY to the listed
slate; everything else in that corpus is a §3 non-target for profile-1.

### Human resources — slate of 4, selected from a corpus of 1,175 — **requires MASTER.5**
| metric (seed-grounded) | world prerequisite |
|---|---|
| Headcount (by company/department) | MASTER.5 employees |
| Payroll cost per FTE | MASTER.5 + existing payroll GL |
| Attrition rate (voluntary) | MASTER.5 with join/exit dates across the 64 months |
| Absence rate | MASTER.5 thin attendance (operator call — cheapest to cut) |
**This is the decision point**: MASTER.5 becomes a build unit iff this slate is in scope.
Employees are masters — addable to the built world without rebuild; historical payslips are
derivable from the already-posted payroll GL bands.

### Sales / CRM — slate of 4, selected from a corpus of 554 — **world sources it today**
| metric | world prerequisite |
|---|---|
| Pipeline conversion rate (stage-to-stage) | exists (crm_pipeline, stages, lost reasons) |
| Win rate | exists |
| Average deal size / revenue per customer | exists |
| Campaign-attributed lead volume | exists (campaigns) |

### Supply chain / inventory ops — slate of 5, selected from a corpus of 1,099 — **world sources it today**
| metric | world prerequisite |
|---|---|
| Inventory turns (by category) | exists (perpetual AVCO) |
| Days of inventory | exists |
| Annual shrinkage % of inventory value | exists (scrap at carrying value) |
| Active supplier count / vendor spend concentration | exists |
| On-time-in-full proxy (delivery vs SO date) | exists (pickings carry dates) |

### Manufacturing — slate of 4, selected from a corpus of 28 — **world sources it today**
| metric | world prerequisite |
|---|---|
| Production output (units, by plant) | exists (MOs) |
| Open work order backlog | exists |
| Capacity utilisation proxy (recorded WO hours vs available) | exists (workorder durations) |
| Scrap rate | exists (QA-rejection scrap) |

### Quality — slate of 2, selected from a corpus of 86 — **thin via scrap/rework documents**
| metric | world prerequisite |
|---|---|
| QA rejection rate | exists (qa_rejection scenario) |
| Cost of poor quality (scrap value) | exists |
Note: the quality *module* is inert by design (0 quality points) — these source from stock
documents, honestly labelled.

## 2b. The end game — latent coverage (operator direction, 2026-08-08)

The slates are the pilot's first bite, not the ceiling. Each corpus splits into four rings:

| ring | meaning | cost to unlock |
|---|---|---|
| **slate** | picked, supported, pilot-now (the 19 above) | in flight |
| **data-latent** | the world ALREADY emits the inputs; metric-side build (chains, MCs) unlocks them | **zero world-work** |
| **world-latent** | needs new masters/simulation first (HR → MASTER.5; anything needing reps, activities, machine states) | a named world unit each |
| **out-of-world** | corpus noise for this industry (SaaS metrics in the sales pool, hospital metrics in quality) | never |

**Direction:** the world's job is to emit a realistic company's full exhaust; coverage then
grows platform-side against a world that never changes. The mechanism already exists and has
run once — the finance directory IS this triage completed (1,287 seeds → 380 members with
realizability verdicts). The end game is the same directory treatment extended corpus by
corpus (sales 554, supply chain 1,099, HR 1,175, …), with the pilot world as the
realizability test bed. Ring sizes are NOT estimated here — sizing them is what the triage
does, and each wave is its own scoped unit after profile-1's cycle closes.

## 3. Explicit non-targets for profile-1's cycle (thin means thin — the rings above say what comes after)

Marketing beyond campaign counts; IT/executive/governance/risk seeds; project management;
multi-echelon supply chain; OEE (needs machine states the world does not simulate);
HR beyond the four metrics above. These are profile-2+ or platform-later territory.

## 4. Decisions this proposal puts to the operator (at or before realism review)

1. **MASTER.5 go/no-go** — the only thin slate needing new build work. Recommend GO
   (headcount/attrition are the operator's own example of books-with-meaning).
2. FP&A budgets in or out for profile-1 (out = my recommendation; revisit at profile-2).
3. Depth numbers: "~340 finance + ~20 thin" is the soft handshake — adjust counts, not
   the doctrine.
