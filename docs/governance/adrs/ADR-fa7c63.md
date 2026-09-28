---
uid: DEC-fa7c63
title: "DSO family meaning: receivable balance from dated application events, net billing, calendar days (W9 U9.1)"
description: "Source-independent meaning for ar_balance, net billing and DSO on Kaveri: dated application events, net billing, days(W) from the governed calendar, LE/functional-currency/tax-inclusive basis, governed non-results."
status: proposed
governing_task: TSK-4cabcb
related_adrs: [DEC-952faa, DEC-f4b2b0, DEC-ada203, DEC-c48b0f]
date: 2026-09-28T04:15:12.616Z
project: bc-core
domain: metrics
subdomain: metrics/receivables
focus: semantics
---

# DSO family meaning: receivable balance from dated application events, net billing, calendar days (W9 U9.1)

## Context

Today's DSO family cannot be trusted: DSO f660fb7b uses a literal 90 over Kaveri's MONTHLY calendar (about 3x off) and was never audit-admitted; ar_balance 61a876e7 is the open-item face value (it ignores partial payments and credit notes); gross_invoiced leaves the credit-note basis undecided. The W9 read-only probe U9.0 (TSK-b57b0a, gen-852f3a, accepted 2026-09-28) established Kaveri's source facts: 2,699 posted invoices and 15 posted credit notes, no drafts or cancels; USD and INR documents, INR functional; amount_total_signed + on invoices and − on credit notes; 2,720 receivable reconciliations (2,717 full, 3 partial-only) whose counterparts are payments 2,634, exchange differences 74, credit-note applications 10 and misc/write-offs 2; credit notes not linked through reversed_entry_id. A trustworthy DSO therefore needs a source-independent meaning built on dated application events (Foundation location A/B; a design act, DEC-c48b0f). Alternatives rejected: open-item face value as numerator (cannot reconcile to the receivable control account); gross billing (basis mismatch); a literal day count (breaks on non-90-day periods); allocation through reversed_entry_id (unpopulated and source-specific). Plan: barecount-devhub#36 (accepted with boundary gen-793604-03), successor 1 §4 and successor 2 §5 acceptance criteria. Arc PLN-c96901, TSK-4cabcb.

## Decision

**D-1. Receivable document.** A receivable document d of legal entity E is a posted customer invoice or customer credit note of E. It carries a posting date pd(d) and a signed functional amount amt(d): in E's functional currency, tax-inclusive, invoice > 0 and credit note < 0. Draft and cancelled documents are not receivable documents. A reversal is its own receivable document with its own posting date.

**D-2. Application event.** An application event x is a dated settlement against a receivable document: a customer payment application, a credit-note application, a write-off or an exchange-difference adjustment. It carries applied(x, d), in E's functional currency and signed so that it reduces |amt(d)|, and an effective date ed(x). An event that settles two receivable documents against each other (an invoice and a credit note) is ONE event that reduces BOTH documents, each by its own applied amount. Write-offs and exchange differences enter only as application events, never also as receivable documents, so they are never counted twice.

**D-3. Outstanding and receivable balance (stock).** For a period-end instant T: out(d, T) = amt(d) − Σ { applied(x, d) : ed(x) ≤ T }, taken over the documents with pd(d) ≤ T; and ar_balance(E, T) = Σ_d out(d, T). Consequences: unapplied credit notes are negative open items; a partial payment reduces the balance from its own effective date; settlement after T does not reduce the balance at T. temporality_kind = stock_at_period_end (DEC-952faa).

**D-4. Open-item face value is a different metric.** The current ar_balance meaning (the gross of any not-yet-cleared invoice) is not the DSO numerator. If it is kept, it is kept under its own name and definition. It is not silently redefined; its successor is a governed MCV act (U9.5).

**D-5. Billing (flow), net basis.** billed(E, W) = Σ amt(d) over the receivable documents with pd(d) ∈ W. Net billing: credit notes posted in W reduce billing, so numerator and denominator share one basis. temporality_kind = flow_per_period.

**D-6. DSO.** dso(E, T, W) = ar_balance(E, T) / billed(E, W) × days(W). W is the window of N trailing fiscal periods ending with the period that contains T. days(W) is the count of calendar days in those periods, taken from E's governed fiscal calendar (D623) as resolved for the evaluation, and is never a literal. N is declared by the metric contract version. Recommended N = 3: it keeps the historical 90-day intent and damps monthly noise. N is left to the operator decision at acceptance.

**D-7. Basis and scope (both operands, enforced at evaluation).** Scope: one legal entity E. Currency: E's functional currency, aggregation_currency = local_currency (DEC-f4b2b0 D1); its prerequisite, an OC/CC projection of the functional amount (DEC-f4b2b0 D5), is delivered by the chain successors, not assumed. Tax: tax-inclusive in both operands. Period: T and W are resolved from the same calendar. A composite evaluation whose operands differ in E, currency basis, tax basis, calendar or T is refused, not computed (U9.3b, extending DEC-ada203's fail-closed rule).

**D-8. Non-results.** When billed(E, W) ≤ 0, DSO is a governed non-result with a recorded reason: never ∞, never 0, never omitted. When ar_balance(E, T) < 0 with positive billing, the negative DSO is reported as computed and flagged as a credit position, not clamped. Missing upstream snapshots defer, per DEC-ada203.

**D-9. Independent expected value (acceptance, U9.8).** For the same E and T, ar_balance must equal (a) the receivable-control balance computed independently from journal-entry lines on receivable accounts, and (b) the source's own aged-receivables total as of T. The acceptance corpus must include: a payment before and after the cutoff; a partial payment; a credit note applied after T; a balanced invoice/credit-note allocation reducing both documents; a write-off; a foreign-currency invoice with an exchange-difference event (counted once); a reversal; and a zero-billing window (non-result).

**D-10. Source realization (non-normative; each choice certified only through its own act).** For Odoo:
- documents: account.move with move_type ∈ {out_invoice, out_refund} and state = posted, amt(d) realized from amount_total_signed (U9.0 verified the signs);
- application events: account.partial.reconcile rows against the documents' receivable lines, with the amount in company currency and max_date as ed(x);
- exchange-difference and write-off entries realize application events only;
- credit-note allocation is realized through those reconciliation rows, never through reversed_entry_id, which is empty on Kaveri.
This is a second observation leg with its own entity. BCF has no application/allocation entity today, so a BCF concept act is expected (U9.4a).

## Consequences

- **Successor MCVs (U9.5):** `ar_balance` and `gross_invoiced` (or a renamed net-billing metric) and DSO get successors under this meaning; the historical versions stay as they are. The DSO successor is the first DSO version to go through audit admission.
- **Concepts and chain (U9.4a–e):** the Customer Invoice chain successor adds the posted-only filter and the functional signed amount; a new application-event leg is authored.
- **Gates (U9.3/U9.3b):** U9.3 takes "nullable means open" off the openness characteristic and moves to dated application events. U9.3b enforces D-7 and D-8.
- **Not in scope:** multi-entity consolidation, group currency, and aging buckets (a separate metric family).

## Alternatives considered

- **Keep the open-item face value as the numerator.** Rejected: it ignores partial payments and credit notes, and it cannot reconcile to the receivable control account.
- **Gross billing (credit notes excluded).** Rejected as the default: numerator and denominator would sit on different bases.
- **Literal day count (90).** Rejected: it breaks on any calendar whose period is not 90 days (Kaveri's is monthly).
- **Credit allocation through `reversed_entry_id`.** Rejected: it is unpopulated on Kaveri, and it is source-specific.
