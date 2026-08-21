---
uid: DEC-9e68e0
title: "Period close is an idempotent act on (company, period), not a step inside the backfill driver"
description: "Extract the nine month-close acts out of forward_build into a standalone idempotent close keyed on (company, period), so the close survives the world cutoff and covers transactions the backfill driver did not create."
status: proposed
date: 2026-08-07T15:58:33.199Z
project: bc-synth
domain: sources
subdomain: odoo-pilot/world-build
focus: lifecycle
---

# Period close is an idempotent act on (company, period), not a step inside the backfill driver

## Context

MEASURED on 2026-08-07 against forward_build.py's month loop, not assumed. The close is better populated than expected — nine acts: statutory remittance (GST 20th, PF 15th, wages 5th), payroll accrual, term-loan service, cash-credit interest, cash-credit revolve against closing working capital, accrual reversals, suspense clearing, FY-end, depreciation and income tax. The defect is not a missing process; it is WHERE the processes live.

All nine exist only inside forward_build.py::month(). The close is coupled to the backfill driver rather than to the period, which fails in two directions.

Forward: after the world cutoff nothing runs them. A demo-day delta yields documents with no depreciation, no tax provision, no accrual reversal and no interest accrual — precisely the hole W0 closed for the historical build, reopening at the live edge. It fails silently because the DOCUMENTS are all present; only the close is missing, and no gate looks for a close.

Sideways: any transaction created outside forward_build — a human working in Odoo on demo day, a manual correction, a hand-made invoice — is uncovered by construction. Every existing gate measures the world as a whole (totals, ties, coverage families), so none can see that one period received transactions and no close.

This is the same class as the three WB.3b halts and the world-shape defects: a property that was true because one particular driver happened to make it true, never asserted anywhere, and therefore silently false the moment anything else touched the world. The remedy that has worked repeatedly in this programme is to name the property and assert it, not to add another step to the driver that happens to satisfy it.

Doing this BEFORE the pilot_ent rebuild is deliberate. The rebuild replays the full 2021-04 to cutoff history; if the close is extracted first, the rebuilt world is the first one whose per-period completeness is an asserted property rather than an accident of which driver ran.

## Decision

The period close becomes a first-class act with the signature close(company, period), implemented in month_close.py, idempotent by construction — it guards on whether that period's close entries already exist for that company and is safe to invoke repeatedly.

Three callers use the SAME act: (a) forward_build.py, which stops owning the close and instead invokes it at the end of each month it builds; (b) a post-cutoff trigger, fired when a delta generation cycle adds transactions to periods beyond the world cutoff; (c) an operator-run repair, for a period found incomplete.

A new per-period completeness gate asserts the property no current gate expresses: every (company, period) carrying transactions carries a corresponding close. This is a structural assertion in the family of verify/world_shape.py — it names the property rather than a proxy for it, and it must be injection-proven able to report red before its green is quoted.

Whether the post-cutoff trigger is a scheduler or an event on the delta cycle is deliberately NOT decided here. Once the close is an idempotent act keyed on (company, period), that choice is a deployment concern and can change without touching the close.

Scope note: this ADR decides the SHAPE of the close, not its CONTENTS. The measured-absent items (prepaid amortization, unrealized FX revaluation, overhead apportionment to WIP, bank reconciliation moving into the monthly rhythm) and the unverified GST ITC set-off are each a separate realism decision, to be taken against the operator realism review. Extracting the act first is what makes adding any of them a single-site change rather than an edit to the backfill driver.
