---
uid: DEC-fa7c63
title: "DSO family meaning: receivable balance from dated application events, net billing, calendar days (W9 U9.1)"
description: "Source-independent meaning for ar_balance, net billing and DSO on Kaveri: dated application events, net billing, days(W) from the governed calendar, LE/functional-currency/tax-inclusive basis, governed non-results."
status: decided
governing_task: TSK-4cabcb
related_adrs: [DEC-952faa, DEC-f4b2b0, DEC-ada203, DEC-c48b0f, DEC-83fda0, DEC-0f3e57, DEC-f44a71, DEC-6fd09d]
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

## Operator decision (2026-09-28)

- **Status:** decided.
- **N = 3 fiscal periods** (D-6): the DSO window is the three trailing fiscal periods ending with the period that contains T; days(W) is counted from the governed calendar.
- **Authority:** the operator's direct line to Codex on thread gen-8f1eb6 (2026-09-28): once bc-docs PR 83 lands, the ADR is accepted as decided with N = 3 fiscal periods. PR 83 landed as merge f7b23af9 (reviewed head 6b8a2da0).

## Consequences

- **Successor metrics (U9.5):** NEW line-grained MCs for the balance (D-1), billing (D-5) and DSO, not new versions of the invoice-grain `ar_balance` / `gross_invoiced_amount` / DSO (Amendment 1 (d), (e)); the invoice-grain family is retired through the governed MCF path once they are live (Amendment 1 (g)). The DSO successor is the first DSO version to go through audit admission.
- **Concepts and chain (U9.4a–e):** the receivable population is the receivable-control *lines* (D-1), not only customer-invoice headers. The chain successors therefore observe (i) the receivable lines of every posted entry on E's receivable-control accounts, with category and functional amount, and (ii) the allocation events (D-2). ~~The Customer Invoice chain successor still supplies the document header facts for billing.~~ Superseded by Amendment 1 (c): billing comes from the receivable-control lines by document category. BCF concepts for the receivable item and the allocation event are expected (U9.4a).
- **Population completeness is proven, not assumed.** U9.0 counted reconciliations on customer-document lines only; it did not enumerate unapplied cash, on-account credits or non-document receivable entries. D-9 (a) proves completeness at each acceptance cutoff. A read-only probe of the unmatched receivable-control lines may run earlier under the operator's standing read-only grant.
- **Gates (U9.3/U9.3b):** U9.3 takes "nullable means open" off the openness characteristic and moves to dated application events. U9.3b enforces D-7 and D-8.
- **Not in scope:** multi-entity consolidation, group currency, and aging buckets (a separate metric family).

## Amendment 1 (2026-09-28): lineage, grain, billing source, new MCs, naming, dependants, evidence and retirement

It records what the W9 design work (U9.3 to U9.4) did, so that nothing is re-derived without its prior decisions. It changes no D-rule; it corrects one Consequences sentence (c) and settles five points the ADR left implicit.

**(a) Prior decisions this ADR builds on (lineage).**
- **DEC-83fda0 "Route B" (implemented): the balance mechanism.** A balance is postings − clearings, netted as of P, with the `cumulative_to_date` gate (U9.3 made its predicate ordinal, bc-core#862). DSO = balance ÷ trailing billing × days.
  - D-1 and D-2 are the Odoo realization of that netting on the receivable-control LINES: debit legs are postings; credit legs (payments, credit notes, write-offs, FX) are clearings; zero-sum allocation legs.
  - This replaces Route B's separate posting/clearing canonical surfaces. They were drafted SAP-side as `cc__receivable_posting` / `cc__receivable_clearing`, have no Odoo realization and are not a live home for this population.
- **DEC-0f3e57 (secondary metrics) and DEC-ada203 (composites):** DSO stays a composite over upstream Metric Snapshots. The trailing window those ADRs deferred is now declared by DEC-6fd09d (a fiscal-period rolling window; `window_days` from the calendar).
- **DEC-f44a71 "route (a)":** a source-bounded DSO repair on Kaveri. This ADR, with W9, is that repair.
- **TSK-a2ab87 (the `days_ratio` derivation op, with a literal `scale`):** the source of the literal 90 (and the directory member's 365). It is superseded for DSO by D-6: days(W) is counted from the governed calendar, and no literal scale is used.
- **The reference map:** the lc5 metric-coverage study, bc-demo `sources/odoo19ee/demos/auto-components-in/design/metric-coverage/finance/days_sales_outstanding.md` (commit 37b0f73f).
  - Its numerator is exactly D-1's population: posted `account.move.line` on the `asset_receivable` accounts, dated on or before the reference date.
  - Its AR balances at 2024-03-31, 2025-03-31, 2025-09-30 and 2026-03-31, independently confirmed to the cent, are the **independent expected values** for D-9 (a). Any difference is explained before the rung is claimed.
  - The study's §2 finding (the realized DSO MC says 90 days and gross, while directory member MDM-d1510b says 365 days and net) is answered by this ADR: N = 3 fiscal periods, tax-inclusive billing net of credit notes (D-5, D-7). The directory member's `derivation_json` is reconciled to this in the U9.5 act.

**(b) Grain change: Customer Invoice → Journal Entry Line.**
- The historical DSO family (`days_sales_outstanding` f660fb7b, `ar_balance` 61a876e7, `gross_invoiced_amount` 8a38e79c) is grained on Customer Invoice (e3963e45). The successor family is grained on **Journal Entry Line** (07cef8c4).
- **Why:** D-1's population includes unapplied cash, on-account credits and adjustments. These are receivable-control lines that belong to no customer invoice, so no invoice-grain metric can hold them.
- Invoice-grain openness also needs a header clearing date, which Odoo does not have (U9.0).
- The line chain is the existing `oc-h827j` / `cc-x13pb`, extended to 1.1.0 (U9.4) on its existing reader `d24f928a`. That is a deliberate reuse from the 2026-08-16 Odoo re-base reconcile closure.

**(c) Billing comes from the lines; the Customer Invoice chain is NOT used for DSO.**
- The Consequences bullet saying "the Customer Invoice chain successor still supplies the document header facts for billing" is **superseded**.
- Billing (D-5) is the sum of the functional amount over the receivable-control lines, of E, in window W, whose document category is `customer_invoice` or `customer_credit_note`. It is carried on the same line chain (U9.4 adds the line's document category).
- It is tax-inclusive by construction, because the receivable leg carries the gross.
- The Customer Invoice chain (`oc-3kgrr` / `cc-das36`, bound on Kaveri as binding bc2cfdab, never observed) stays as it is. It is not an operand of DSO.

**(d) The line-grained metrics are NEW Metric Contracts.** The grain is fixed on an MC, so the successors of D-1, D-5 and D-6 are new MCs on the Journal Entry Line grain. They are not new versions of f660fb7b / 61a876e7 / 8a38e79c. The invoice-grain family is RETIRED when the new MCs are live (see (g), Retirement). The U9.5 bullet under Consequences reads accordingly.

**(e) Naming: no collision with `net_invoiced_amount`.**
- In D-5, "net billing" means net of credit notes. It does NOT mean net of tax.
- The existing `net_invoiced_amount` (0d61b620, audit_pending) is the pre-tax subtotal, a different meaning. So the new billing MC must not be called "net invoiced", nor anything that reads as untaxed.
- The working names, fixed at U9.5 authoring: `receivable_control_balance` (D-1) and `receivable_billed_amount` (D-5: tax-inclusive, net of credit notes, over the document categories). The DSO successor keeps the business name "days sales outstanding" and is linked to directory member MDM-d1510b.

**(f) Dependants.**
- `dso_to_credit_term_ratio` (11fb263d, active, Customer Invoice grain) reads the HISTORICAL DSO. It is not silently rebound. In U9.5 it is either re-authored over the new DSO (as a new MC or version, per its own grain rules) or withdrawn, in the same act that retires the old DSO ((g)). Until then it keeps reading the historical DSO, and it must not be presented as consistent with the new one.
- `total_outstanding_receivables` (13e8a077, audit_pending, Customer Invoice grain, open-item face value) is the rejected "open-item face value" alternative below, under another name. It is not an operand of DSO, and its disposition is recorded as a U9.5/coverage-arc task. No contract changes now.

**(g) Why the existing invoice-grain MCs are not reused: the evidence (operator ruling 2026-09-28, "journal lines + retire old").**
Foundation's default is to keep an MC and onboard a new source by binding (layer C). That default was checked against the existing family, and it fails on MEANING, not on source shape. The evidence below is read-only: a pinned SQL probe on v3_lc5, company 1, 2026-09-28 (`docs/evidence/closeouts/implementation/w9-dso-grain-feasibility-2026-09-28/`: the SQL, sha256 `355430d1…`, its runner and transcript, MANIFEST.sha256), compared with the lc5 coverage study's second-model-confirmed values.
- **`ar_balance` (61a876e7) as declared is semantically wrong for D-1 and D-7.**
  - It sums each open invoice's header gross amount in DOCUMENT currency, so Kaveri's USD invoices are added as INR numbers. It takes the face value of invoices not yet fully cleared, not their residual.
  - Its `as_of` gate reads the literal payload keys `document_date`/`clearing_date`, and Odoo has no header clearing date.
  - On Kaveri it gives 974.8M / 1,155.8M / 1,397.2M / 1,229.1M at 2024-03-31 / 2025-03-31 / 2025-09-30 / 2026-03-31. That is 17–24% below the confirmed receivable balances (1,173.9M / 1,354.8M / 1,646.0M / 1,406.3M).
- **`days_sales_outstanding` (f660fb7b)** multiplies by a literal 90, which D-6 rejects, and aggregates in document currency. **`gross_invoiced_amount` (8a38e79c)** sums unsigned document-currency totals over invoices and credit notes alike, the CB-013 mixing that D-5 forbids.
- **Even corrected at invoice grain, the balance cannot meet D-1.**
  - "Corrected" means company currency, with the residual at P from dated payment applications. It would also need a new clearing chain (`account.partial.reconcile` has a source contract but no OC/CC/reader) and a Customer Invoice chain successor.
  - It still misses the receivable-line balance by exactly the non-invoice receivable residual: 0.45M / 0.90M / 1.35M / 1.35M / 1.35M at the four dates and at 2026-08-31. Those are unapplied cash and misc entries on the control accounts (BNK1, EXCH, MISC), which belong to no invoice.
  - D-1 includes them, and the Alternatives below reject a document-scoped balance with a bridge.
- **The journal-line balance (D-1) reproduces all four confirmed values to the cent.**

**Retirement: two DSOs never coexist.** When the new line-grained MCs are live (U9.5), the invoice-grain family, `days_sales_outstanding` f660fb7b, `ar_balance` 61a876e7 and `gross_invoiced_amount` 8a38e79c, is withdrawn or superseded through the governed MCF lifecycle path (M15 supersession). It is executed in U9.5, not deferred. It is never done by hand, and never before its successors are live. `dso_to_credit_term_ratio` is re-authored on the new DSO, or withdrawn, in the same act; it is never silently rebound.

## Amendment 2 (2026-09-29): U9.5 retirement scope narrowed (operator ruling)

This amendment narrows **when** Amendment 1 (g)'s retirement happens. It changes no D-rule and no meaning.

- **Authority:** the operator's direct grant through bc-exchange:
  - grant_id `2026-09-29T01-54-40-015Z-20b8ff52`;
  - text_sha256 `20b8ff52522e0f11b5bb6800de1587af12d21121f3b9654183d15d230277d4eb`;
  - request `2026-09-29T01-54-11-394Z-20b8ff52`, TOTP-recorded 2026-09-29T01:54:40Z.
- **In U9.5 (TSK-16eb78):**
  - `days_sales_outstanding` f660fb7b is superseded (M15) by the new Journal Entry Line DSO, so two DSOs never coexist;
  - `dso_to_credit_term_ratio` 11fb263d is retired in the same act, never rebound. Its re-author is TSK-d9fdca.
- **Not in U9.5:**
  - `ar_balance` 61a876e7 and `gross_invoiced_amount` 8a38e79c are **superseded in meaning** by `receivable_control_balance` and `receivable_billed_amount`, but their MCVs are not retired in U9.5;
  - they move, with their dependent receivables metrics, to the first batch of the Kaveri full metric coverage arc (PLN-1a0ee1, TSK-af9630), where each is rebuilt on journal lines or retired;
  - until then they stay in their current lifecycle states, and must not be presented as consistent with the journal-line family.
  - **Why:** the live consumer trace (2026-09-29) found `ar_balance` bound as an operand by 12 metric versions, one of them active (`bad_debt_to_ar_ratio`). `gross_invoiced_amount` is bound by 10. Retiring them in U9.5 would make the active consumer a governed non-result and multiply the act.
- **`gross_invoiced_amount` 8a38e79c** is `audit_pending` and not current, so M15 cannot apply to it. Its disposition is record-only in TSK-af9630. The `retire-demoted-duplicate` path is not used, because it would assert a duplicate meaning that does not exist.
- **Amendment 1 (g)'s sentence** "the invoice-grain family ... is withdrawn or superseded ... executed in U9.5" reads, for `ar_balance` and `gross_invoiced_amount`, as "executed in the coverage arc (PLN-1a0ee1)".

## Amendment 3 (2026-09-29): the DSO successor's directory identity (U9.5)

This amendment replaces two sentences of Amendment 1 about directory member MDM-d1510b. It changes no D-rule and no meaning. It is required before the U9.5 live admission (Codex gen-658c4e-03).

**What Amendment 1 said, and why it cannot be done.** Amendment 1 (a) says MDM-d1510b's `derivation_json` "is reconciled to this in the U9.5 act". Amendment 1 (e) says the DSO successor "is linked to directory member MDM-d1510b". Neither is reachable through a governed surface:
- MDM-d1510b is a member of the Customer Invoice grain group `ar_collections_and_dso_derived`. Its identity is Customer Invoice grained, and a member's grain comes from its group.
- The directory HTTP surface cannot give an existing member a new-grain version. `POST /metric-directory/members/:uid/version` only authors a missing v1, and the member-versioning service is reachable only from the a2 backfill tool.
- The directory derivation vocabulary (ratio, percentage, subtract, add, passthrough) has no calendar-window ratio. A governed `derivation_json` patch therefore cannot express D-6 (TSK-540c6a item 7; gap G4).
- MDM-d1510b cannot be archived either. `PATCH members/:uid/archive` refuses a member that still carries its legacy `realized_metric_contract_uid` (the invoice-grain DSO `db373d5b`).

**Decision (umbrella ruling, 2026-09-29).**
- **New groups and members.** The journal-line family gets two new groups on the Journal Entry Line grain, both in the AR family `ar_collections_and_dso`:
  - `receivable_control_base`, holding the members `receivable_control_balance` (D-1) and `receivable_billed_amount` (D-5);
  - `receivable_control_derived`, holding the member `receivable_days_sales_outstanding`.
- **THE Days Sales Outstanding.** That new DSO member is the family's Days Sales Outstanding. Its versioned intent carries the D-6 definition, and it depends on the two base members. The DSO successor MC is keyed `receivable_days_sales_outstanding`, with display name "Days Sales Outstanding" (Codex gen-658c4e-01, Q-N2). The key `days_sales_outstanding` stays reserved by the superseded invoice-grain MC `db373d5b`, whose parent M15 does not archive.
- **MDM-d1510b.** It is superseded in meaning by the new DSO member and is not moved. Its `derivation_json` is not reconciled (gap G4). It is recorded in TSK-af9630 (PLN-1a0ee1) for retirement in coverage batch 1, together with its legacy pointer.
- **One operative DSO, a stop condition.** The directory must never present two operative DSO realizations. The U9.5 package proves exactly one operative DSO realization after the M15 supersession, and a second one at the live precheck is a stop.

Amendment 1's two sentences read accordingly: (a) "MDM-d1510b is superseded in meaning; its `derivation_json` is not reconciled (G4); see Amendment 3", and (e) "is realized on the new member `receivable_days_sales_outstanding`; see Amendment 3".

## Alternatives considered

- **Keep the open-item face value as the numerator.** Rejected: it ignores partial payments and credit notes, and it cannot reconcile to the receivable control account.
- **Gross billing (credit notes excluded).** Rejected as the default: numerator and denominator would sit on different bases.
- **Literal day count (90).** Rejected: it breaks on any calendar whose period is not 90 days (Kaveri's is monthly).
- **Credit allocation through `reversed_entry_id`.** Rejected: it is unpopulated on Kaveri, and it is source-specific.
- **A document-scoped balance (invoices and credit notes only) with a residual bridge to the control account.** Rejected for the DSO numerator: unapplied cash and on-account credits are part of what a customer owes net, and a bridge whose zero condition must be proven at every cutoff adds a second reconciliation for no gain. A document-scoped open-invoice amount remains available as its own metric from out(i, T) over document items (D-4).
