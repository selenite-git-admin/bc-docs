---
uid: mfg-in-world-known-limitations
title: mfg-in Pilot World — Known Limitations and Accepted Divergences
description: Divergences between the synthetic mfg-in pilot world (Odoo 19 Enterprise, three Indian manufacturing entities) and how a real Indian manufacturer's ERP would behave, accepted on purpose. Consulted when a metric computed against this world returns an unexpected number — the register says whether the metric is wrong or the world is. Accepted limitations (L-nnn) are kept strictly separate from open defects so the two are never confused.
status: active
date: 2026-08-07
project: bc-synth
domain: sources
subdomain: odoo-pilot/world-build
focus: realism
---

# mfg-in pilot world — known limitations and accepted divergences

**What this file is for.** BareCount computes metrics against this world. When a metric
returns a surprising number, this register is what tells you whether the **metric** is wrong
or the **world** is. Without it, every surprising number costs a fresh investigation from
scratch. It is what makes a synthetic world usable as a test fixture rather than only a demo.

**What belongs here.** A divergence between this world and how a real Indian manufacturer's
ERP would behave, that we have **accepted on purpose**. Each entry says what diverges, why it
was accepted, which metrics it could distort, and how to recognise its fingerprint.

**What does NOT belong here.** Defects. A defect gets fixed or becomes a task. An entry here
is a decision, not a bug someone forgot. If an entry starts feeling like an excuse, it is
probably a defect wearing the wrong hat.

Last updated: 2026-08-07 · World profile `mfg-in` · Odoo 19 Enterprise

---

## L-001 · GST set-off uses simplified ordering

**Diverges:** Real set-off follows CGST Act s.49/49A/49B — a prescribed sequence with
cross-utilisation restrictions. This world uses **like-against-like plus IGST spillover**:
IGST credit is consumed first and may spill to CGST then SGST; CGST and SGST otherwise offset
only their own kind.

**Why accepted (operator, 2026-08-07):** the full statutory sequence is a large build for a
demo, and the residual difference is small once IGST spillover is included. Pure
like-against-like was rejected *because* it would strand IGST credit — the entities are in
different states, so interstate purchase against intrastate sale is the normal pattern.

**Could distort:** net GST payable in edge months; the split between cash paid and credit
utilised. Aggregate GST cost over any quarter should be very close to correct.

**Fingerprint:** a month where credit utilisation looks implausibly clean, or a residual
credit balance that a real filing would have consumed.

---

## L-002 · Payroll is synthetic, not the HR module

**Diverges:** payroll posts as journal entries rather than through Odoo's payroll module.
`hr.contract` does not exist in Odoo 19 as the drivers once assumed. MASTER.5 remains `[SPEC]`.

**Why accepted:** the payroll *module* is not what BareCount reads; the resulting accounting
is. Building it would be a large detour for no metric gain.

**Could distort:** any metric sourced from payroll master data rather than the GL — headcount,
cost per employee, or attrition. Salary cost in the P&L is unaffected.

**Fingerprint:** payroll figures that tie in the GL but have no supporting employee records.

---

## L-003 · No unrealised FX revaluation

**Diverges:** Odoo books **realised** FX gain/loss automatically when a foreign-currency
receivable settles at a different rate. **Unrealised** FX on receivables still open at month
end requires a manual revaluation act, which this world does not run.

**Why accepted:** it is a month-end judgement act rather than a transaction, and its absence
is visible rather than misleading — there simply is no unrealised FX line.

**Could distort:** other income/expense by month; the carrying value of export receivables at
period end. Settled-transaction FX is correct.

**Fingerprint:** FX gain/loss appearing only in months where an export invoice was *paid*,
never in months where one merely stayed open.

---

## L-004 · Income tax is provided monthly, not as quarterly advance tax

**Diverges:** Indian companies pay advance tax on 15 June / September / December / March and
true up at year end. This world provides tax monthly.

**Why accepted:** the annual charge is right; only the phasing and the cash profile differ.

**Could distort:** monthly cash flow, tax expense phasing, and anything reading tax paid in a
specific month. Annual tax expense is unaffected.

**Fingerprint:** a smooth monthly tax outflow where a real company shows four lumps.

---

## L-005 · Deferred tax is not computed

**Diverges:** no deferred tax asset or liability is recognised. Tracked as CLOSING.3, parked.

**Why accepted:** deferred tax needs a book-vs-tax timing-difference model that no current
metric consumes.

**Could distort:** effective tax rate; net worth. Current tax is unaffected.

---

## L-006 · TDS is deducted on salaries but not on vendor payments

**Diverges:** salary TDS (s.192) IS deducted, via `statutory.py` against the profile's declared
workforce bands. TDS on vendor payments — s.194C contractors, s.194J professional fees,
s.194I rent — is not. The l10n_in chart carries the accounts (`TDS Deducted`,
`TDS (Withholding Control)`) but no driver uses them, so service vendors are paid gross.

**Why accepted:** TDS applies to *service* payments at 1–10%, not to goods.
For a manufacturer the affected slice is contractors, professional fees and rent — real, but a
modest share of total spend. Building it means a per-vendor-category withholding rule and a
separate remittance stream, which is a meaningful build for a small correction.

**Could distort:** cash paid to service vendors (overstated by the withheld amount); the TDS
remittance stream (understated); vendor payable ageing very slightly. Materials procurement,
COGS and inventory are unaffected — no TDS applies there.

**Fingerprint:** service vendor payments that exactly equal the invoice gross, with no
withholding line, and a TDS liability sourced only from payroll.

**Status:** **Accepted** — operator (anant) accepted this limitation on 2026-08-22 at the realism review (acceptance recorded in barecount-devhub session SES-e8ffeb plan/change record, and on bc-docs PR #8 as the re-review comment for review 5000717885). Deduct-at-source on service vendors is out of scope for the mfg-in world unless a metric demands it.

---

## Open, NOT accepted — these are defects being fixed, listed so they are not mistaken for limitations

| Ref | Defect | Status |
|---|---|---|
| TSK-98235d | GST input credit never set off — output paid gross in cash | Being fixed |
| TSK-bcc138 / D556 | Period close welded to the backfill driver; nothing runs it after cutoff | Being fixed |
| — | Overhead apportionment/absorption into WIP absent — breaks COGS, gross margin, inventory value | Ranked for operator review |
| — | Prepaid/deferred expense amortization absent | Ranked for operator review |
| — | Provision for doubtful debts absent | Ranked for operator review |
