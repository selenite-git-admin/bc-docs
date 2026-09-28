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

Today's DSO family cannot be trusted: DSO f660fb7b uses a literal 90 over Kaveri's MONTHLY calendar (about 3x off) and was never audit-admitted; ar_balance 61a876e7 is the open-item face value (it ignores partial payments and credit notes); gross_invoiced leaves the credit-note basis undecided. The W9 read-only probe U9.0 (TSK-b57b0a, gen-852f3a, accepted 2026-09-28) established Kaveri's source facts: 2,699 posted invoices and 15 posted credit notes, no drafts or cancels; USD and INR documents, INR functional; amount_total_signed + on invoices and − on credit notes; 2,720 receivable reconciliations (2,717 full, 3 partial-only) whose counterparts are payments 2,634, exchange differences 74, credit-note applications 10 and misc/write-offs 2; credit notes not linked through reversed_entry_id. A trustworthy DSO therefore needs a source-independent meaning over the whole receivable-control population, with dated application events for per-item open amounts (Foundation location A/B; a design act, DEC-c48b0f). Alternatives rejected: open-item face value as numerator (cannot reconcile to the receivable control account); gross billing (basis mismatch); a literal day count (breaks on non-90-day periods); allocation through reversed_entry_id (unpopulated and source-specific). Plan: barecount-devhub#36 (accepted with boundary gen-793604-03), successor 1 §4 and successor 2 §5 acceptance criteria. Arc PLN-c96901, TSK-4cabcb.

## Decision

**D-1. Receivable item (the whole receivable-control population).** A receivable item i of legal entity E is one posted line on E's customer receivable-control accounts (trade receivables). It carries a posting date pd(i) and a signed functional amount amt(i) in E's functional currency, tax-inclusive where the line carries tax, debit > 0 and credit < 0. Every posted line on those accounts is an item, and every item has exactly one category:
- **document**: the receivable line of a posted customer invoice (> 0) or customer credit note (< 0);
- **unapplied cash**: the receivable line of a customer payment or an on-account credit;
- **adjustment**: a receivable line of an exchange-difference entry, a write-off or any other journal entry posted to the receivable-control accounts.
Draft and cancelled entries post no lines and are not items. A reversal is its own item with its own posting date. The category is source-independent; D-10 says how Odoo realizes it. Nothing posted to the receivable-control accounts falls outside the population, so no residual bridge is needed (see D-9).

**D-2. Application event.** An application event x is a dated allocation between receivable items: a payment applied to an invoice, a credit note applied to an invoice, or an exchange-difference or write-off line allocated against the item it adjusts. It has one stable identity, an effective date ed(x), and exactly one signed leg applied(x, i) per item it touches, in E's functional currency. The legs of one event sum to zero: an allocation moves an open amount between items and never creates or destroys receivable balance. Exchange differences and write-offs are counted once, as the adjustment items they post (D-1). Their allocations are zero-sum legs, never a second amount.

**D-3. Outstanding and receivable balance (stock).** For a period-end instant T:
- out(i, T) = amt(i) − Σ { applied(x, i) : ed(x) ≤ T }, for the items with pd(i) ≤ T;
- ar_balance(E, T) = Σ_i out(i, T).
Because each event's legs sum to zero, ar_balance(E, T) = Σ { amt(i) : pd(i) ≤ T }: the receivable-control balance at T. Allocation timing moves open amounts between items, not the total. Consequences: an unapplied payment or on-account credit reduces the balance from its own posting date, even if it is applied after T; an unapplied credit note is a negative open item; write-offs and exchange differences change the balance once, at their posting date. temporality_kind = stock_at_period_end (DEC-952faa). The per-item open amounts out(i, T) are the basis for aging and open-item metrics; the DSO numerator needs only their total.

**D-4. Open-item face value is a different metric.** The current ar_balance meaning (the gross of any not-yet-cleared invoice) is not the DSO numerator. If it is kept, it is kept under its own name and definition. It is not silently redefined; its successor is a governed MCV act (U9.5).

**D-5. Billing (flow), net basis.** billed(E, W) = Σ amt(i) over the **document** items with pd(i) ∈ W. Net billing: credit notes posted in W reduce billing, so numerator and denominator share one basis. Unapplied cash and adjustment items are not billing. temporality_kind = flow_per_period.

**D-6. DSO.** dso(E, T, W) = ar_balance(E, T) / billed(E, W) × days(W). W is the window of N trailing fiscal periods ending with the period that contains T. days(W) is the count of calendar days in those periods, taken from E's governed fiscal calendar (D623) as resolved for the evaluation, respecting D623's half-open period boundaries (each day counted once), and is never a literal. N is declared by the metric contract version. Recommended N = 3: it keeps the historical 90-day intent and damps monthly noise. N is left to the operator decision at acceptance.

**D-7. Basis and scope (both operands, enforced at evaluation).** Scope: one legal entity E. Currency: E's functional currency, aggregation_currency = local_currency (DEC-f4b2b0 D1); its prerequisite, an OC/CC projection of the functional amount (DEC-f4b2b0 D5), is delivered by the chain successors, not assumed. Tax: tax-inclusive in both operands. Period: T and W are resolved from the same calendar. A composite evaluation whose operands differ in E, currency basis, tax basis, calendar or T is refused, not computed (U9.3b, extending DEC-ada203's fail-closed rule).

**D-8. Non-results.** When billed(E, W) ≤ 0, DSO is a governed non-result with a recorded reason: never ∞, never 0, never omitted. When ar_balance(E, T) < 0 with positive billing, the negative DSO is reported as computed and flagged as a credit position, not clamped. Missing upstream snapshots defer, per DEC-ada203.

**D-9. Independent expected value (acceptance, U9.8).** For the same E and T:
- (a) ar_balance(E, T) must equal the receivable-control balance computed independently, as the sum of journal-entry lines on E's receivable-control accounts with posting date ≤ T (a different path from the item and event realization);
- (b) Σ_i out(i, T) must equal the source's own aged-receivables total as of T, over the same population (all receivable-control lines, including unapplied cash and adjustments) and the same as-of rule.
Both equalities hold by construction when D-1's population is complete, so any difference is a realization defect: an unclassified or missed line. It is reported as a refusal, never bridged.
- (c) **Per-item assertion.** Because zero-sum legs keep the total right even with inverted signs, (a) and (b) alone cannot catch a sign error. Acceptance therefore also asserts both affected items' open amounts, before and after the cutoff, for a partial payment, a credit-note allocation, and an FX / write-off allocation, together with the unchanged control total. The acceptance corpus must include:
- a payment posted before T and applied after T;
- an unapplied payment and an on-account credit;
- a non-document receivable journal entry;
- a partial payment;
- a credit note applied after T;
- a balanced invoice/credit-note allocation reducing both items;
- a write-off, and a foreign-currency invoice with an exchange-difference entry, each changing the balance exactly once;
- a reversal;
- a zero-billing window (non-result).

**D-10. Source realization (non-normative; each choice certified only through its own act).** For Odoo:
- items: posted account.move.line rows of company E on accounts with account_type = asset_receivable, amt(i) = balance (company currency). Category: document when the move is out_invoice / out_refund; unapplied cash when the line comes from a customer payment (or an on-account entry); adjustment when the move is in the exchange-difference journal, a write-off, or any other entry;
- documents for billing: account.move with move_type ∈ {out_invoice, out_refund} and state = posted. The company-currency signed total amount_total_signed agrees in sign with the document's receivable line (U9.0 verified the signs); billing uses the document's receivable-line amount, so billing and balance share one realization;
- application events: account.partial.reconcile rows between receivable lines. Each row is one event with two legs under D-3's subtraction convention: the debit receivable line gets applied = +amount and the credit receivable line gets applied = −amount (company currency), so a +100 invoice and a −20 payment reconciled for 20 have open amounts +80 and 0; max_date as ed(x);
- exchange-difference and write-off entries realize adjustment items (their receivable lines), counted once; their reconciliations are zero-sum legs;
- credit-note allocation is realized through those reconciliation rows, never through reversed_entry_id, which is empty on Kaveri.
This is a second observation leg with its own entity. BCF has no application/allocation entity today, so a BCF concept act is expected (U9.4a).

## Consequences

- **Successor MCVs (U9.5):** `ar_balance` and `gross_invoiced` (or a renamed net-billing metric) and DSO get successors under this meaning; the historical versions stay as they are. The DSO successor is the first DSO version to go through audit admission.
- **Concepts and chain (U9.4a–e):** the receivable population is the receivable-control *lines* (D-1), not only customer-invoice headers. The chain successors therefore observe (i) the receivable lines of every posted entry on E's receivable-control accounts, with category and functional amount, and (ii) the allocation events (D-2). The Customer Invoice chain successor still supplies the document header facts for billing. BCF concepts for the receivable item and the allocation event are expected (U9.4a).
- **Population completeness is proven, not assumed.** U9.0 counted reconciliations on customer-document lines only; it did not enumerate unapplied cash, on-account credits or non-document receivable entries. D-9 (a) proves completeness at each acceptance cutoff. A read-only probe of the unmatched receivable-control lines may run earlier under the operator's standing read-only grant.
- **Gates (U9.3/U9.3b):** U9.3 takes "nullable means open" off the openness characteristic and moves to dated application events. U9.3b enforces D-7 and D-8.
- **Not in scope:** multi-entity consolidation, group currency, and aging buckets (a separate metric family).

## Alternatives considered

- **Keep the open-item face value as the numerator.** Rejected: it ignores partial payments and credit notes, and it cannot reconcile to the receivable control account.
- **Gross billing (credit notes excluded).** Rejected as the default: numerator and denominator would sit on different bases.
- **Literal day count (90).** Rejected: it breaks on any calendar whose period is not 90 days (Kaveri's is monthly).
- **Credit allocation through `reversed_entry_id`.** Rejected: it is unpopulated on Kaveri, and it is source-specific.
- **A document-scoped balance (invoices and credit notes only) with a residual bridge to the control account.** Rejected for the DSO numerator: unapplied cash and on-account credits are part of what a customer owes net, and a bridge whose zero condition must be proven at every cutoff adds a second reconciliation for no gain. A document-scoped open-invoice amount remains available as its own metric from out(i, T) over document items (D-4).
