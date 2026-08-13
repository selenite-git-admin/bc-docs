---
id: demo-estate-module-coverage
title: "Demo-Estate Module Coverage — Odoo apps/modules exercised, mapped to metric functions"
status: approved
authority: derived
depends_on: [demo-estate-simulator-requirements, demo-estate-metric-coverage]
governing_sources:
  - DEC-8b17b1 (D561 demo-estates doctrine)
  - D566 (bc-demo v2 simulator-as-product)
  - "operator direction 2026-08-13: re-scope for maximum coverage"
---

> **Promoted to SSOT 2026-08-13** (was `artifacts/odoo-pilot/COVERAGE-MEMO-profile1.md`, REVIEW INPUT). The matrix below reflects the Odoo **pilot** world (bc-sdg, 64-month), which runs CRM pipeline, work-centres/WIP, and quality-scrap. **bc-demo v2.1's current state is thinner** (16 of 78 apps installed; CRM + Quality installed-but-empty; workorders were dropped during a margin fix and must be restored). The `demo-estate-max-coverage-rescope.md` plan lists the delta bc-demo v2.1 must close to match this. Odoo Enterprise app count for reference: **78 apps** available; **16 installed** on the estate (177 of 1,466 modules).

# Coverage memo — Odoo module × metric-function map (demo-estate)

Date: 2026-08-08 · TSK-509c97 · Status: **REVIEW INPUT** — measured now, mid-build; items
marked ⏳ re-verify at gate-green. Companion documents: `SOFT-TARGET-METRICS-pilot.md`
(metric scope + end-game rings), `bc-docs/docs/reference/mfg-in-world-known-limitations.md`
(accepted divergences), the D554 manifest split (`bc-sdg pilots/profiles/mfg-in/manifest/`,
EQUIVALENCE_GREEN).

## 1. Module coverage matrix (measured from `ir_module_module`, 177 installed)

| module surface | state | pilot verdict |
|---|---|---|
| account + accountant + reports | installed, **exercised 64 months** | covered |
| sale_management | installed, exercised (SO→deliver→invoice→collect) | covered |
| purchase | installed, exercised (PO→receive→bill→pay, imports) | covered |
| stock + stock_account | installed, exercised (perpetual AVCO, W14 company fields) | covered |
| mrp + mrp_workorder + mrp_account | installed, exercised (MOs, work orders, absorption, WIP) | covered |
| crm | installed, exercised (pipeline, stages, lost reasons, campaigns) | covered |
| **hr + hr_payroll + hr_holidays** | **installed (l10n dependency), UNUSED — no employees** | **substrate ready for MASTER.5; data-only unit** |
| quality + quality_control | installed, **inert by design** (0 quality points) | thin metrics source from scrap documents, labelled honestly |
| maintenance, project, hr_expense, helpdesk, repair, plm, POS, website | **not installed** | out of profile-1 by decision; profile-2+ candidates per industry |

## 2. l10n_in family study (operator point 3 — measured, 9 installed / 9 relevant uninstalled)

**Installed:** `l10n_in`, `_asset`, `_hr_holidays`, `_hr_payroll`, `_hr_payroll_account`,
`_purchase_stock`, `_sale`, `_sale_stock`, `_stock` — the accounting + operational layer.

**Uninstalled, and what each means:**

| module | function | proposed disposition |
|---|---|---|
| l10n_in_edi | e-invoice (IRN) submission | **Limitation candidate L-007**: the world POSTS GST-correct invoices but does not simulate statutory e-invoice filing — filing is an exchange with government infrastructure, not bookkeeping |
| l10n_in_edi_gstr, l10n_in_reports, l10n_in_reports_gstr_pos | GSTR return preparation/filing | same family — L-007; GSTR data *content* is derivable from posted documents if a demo ever needs it |
| l10n_in_ewaybill (+_irn, +_stock) | e-waybill for goods movement | same family — L-007; movement documents exist, waybill filing does not |
| l10n_in_pos (+_urban_piper) | point-of-sale | out of industry — B2B manufacturer |

**Assessment:** the installed set is the correct *bookkeeping* superset; every uninstalled
member is a *statutory-filing or channel* surface. Recommend one limitations entry (L-007,
"statutory filings not simulated — documents carry filing-ready data") rather than installs.
⏳ Operator confirms at review.

## 3. Profile naming (operator point 5)

Everything named `mfg-in` is **profile-1 of the mfg-in family**. Proposal: directory stays
`profiles/mfg-in/` (it is the identity); the D554 `parent.json` gains
`profile_generation: 1`; profile-2 (any industry) gets its own directory + its own runbook
cloned from this one at the post-cycle structural revision — runbooks are per-world-build by
design. No renames of exchanged artifacts (durable-naming rule).

## 4. Session-history sweep — discussed-but-not-yet-implemented register (operator point 8)

Everything below is TRACKED; nothing is silently open. ⏳ = decision or verification at review.

| item | state |
|---|---|
| MASTER.5 (employees/departments/payslips) | ⏳ decision via soft-target proposal (recommend GO; module substrate measured ready) |
| D556 close acts 2–9 (migrate from forward_build) + set-off already live | queued post-cycle (TSK-bcc138) |
| Close-content list: prepaid amortization, doubtful-debt provision, overhead apportionment depth, unrealised FX (L-003) | ⏳ operator ranks at review |
| CLOSING.3 deferred tax | parked (L-005) |
| SETUP.5 subscription activation | deferred, operator's moment; not a build gate |
| Runbook relocation to bc-sdg | parked post-cycle (TSK-de7e6c) |
| Jurisdiction facts out of driver literals | parked, forcing function = profile-2 (TSK-c24cb1) |
| Runbook prose queue (§0 test-not-milestone, §8 review inputs, §10 closure fields) | queued, next byte-touching revision |
| Seed-corpus noise audit | planned post-cycle (TSK-70dd05) |
| GST set-off statutory ordering simplification | accepted L-001 |
| Statutory parameters: 19 of 46 unverified (demo grade) | ⏳ standing runbook note — operator accepts or upgrades |
| Work-order productivity timestamps = now() (cosmetic; valuation unaffected) | limitations candidate at review |
| Execution deviations D-r42-1/2 (PILOT_HOST; §7/§8 bindings) | queued for post-cycle structural revision |

## 5. Gate-green verification checklist (runs before the review, evidence attached to it)

- [ ] WB.6 battery `BATTERY_ALL_GREEN` + `CLOSE_GATE_GREEN` (close-completeness, first populated-world run)
- [ ] Bank statement HEADERS ≈ 64 months × 3 companies (not just lines)
- [ ] Picking counts by type (deliveries / receipts) per company
- [ ] GST set-off entries present monthly (`CLS-*-GSTSETOFF-*`) and ITC balance behaviour sane
- [ ] Loan accounts: opening + monthly EMI postings share ONE account per kind (W15 claim)
- [ ] Soft-target spot-check: one metric per thin slate computable from world data by hand
