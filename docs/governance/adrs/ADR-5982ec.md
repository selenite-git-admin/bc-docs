---
uid: DEC-5982ec
title: "The point_in_time family reshape: re-declare each member's true temporal meaning (shape and definition), grouped by target shape; the as_of/flow targets are gated on the per-input period predicate"
description: "The point_in_time family reshape: re-declare each member's true temporal meaning (shape and definition), grouped by target shape; the as_of/flow targets are gated on the per-input period predicate"
status: proposed
date: 2026-10-07T02:58:35.170Z
project: bc-core
domain: metrics
subdomain: contracts/metric-shape-semantics
focus: point_in_time family reshape: per-member disposition by target shape, name↔definition fidelity, the TSK-36440f gate, active exposure
---

# The point_in_time family reshape: re-declare each member's true temporal meaning (shape and definition), grouped by target shape; the as_of/flow targets are gated on the per-input period predicate

**Status:** proposed. Successor to DEC-d0b66a (decided), which it applies — it does **not** supersede it. Author: Architect SES-b9b0ef. Grounded at bc-core / bc-docs `origin/main` and the live `bc_platform_dev` MCF substrate, 2026-10-07. The operator decides this ADR; it authorizes no write or evaluation act.

## Context

DEC-d0b66a decided, for the `point_in_time` shape, that it resolves to **identity** (no gate-level date basis and no runtime period/snapshot selection), that its directory generator **over-claims** an as-of runtime semantic the evaluator does not implement, that its members are therefore **not auto-clean**, and (Decision 5/6) that giving a member "the state at a reporting point" is a **re-shape** to `as_of`/`cumulative_to_date` and is **its own design act**. DEC-d0b66a settled the shape's semantics on a single-member finding. This ADR carries that decision across the **whole `point_in_time` family** as the design act Decision 6 anticipated.

**The substrate population (live `bc_platform_dev`, 2026-10-07).** `mcf.metric_contract` holds **49** non-archived `point_in_time` contracts. These are **27 distinct base concepts** plus **22 `__tacorr_*` duplicate variants** (the C-FX-8 row-stamping temporal-anchor correction from `metric-directory.service.ts:289-302`; one companion for each stock and each flow — the 5 counts carry none). The 27 base concepts are **6 stocks + 5 counts + 16 flows**. (Two further members Metric triaged alongside this family — `write_off_amount`, `customer_invoice_line_item_count` — carry the `none` shape, and `total_cash_balance` is already `as_of`; they are related defects dispositioned below, but they are not `point_in_time`.)

**The defect is a meaning-fidelity defect (Invariant I — meaning is evaluated once, and must be evaluated as what it means).** The 16 flows are **named** as flows but **defined** as as-of stock snapshots. Verbatim from the current substrate:

- `operating_revenue_amount` (a P&L flow): *"As-of (point-in-time) snapshot balance (sum) of the GL Account grain filtered to … 'operating_revenue' …, point_in_time as-of balance date (a stored balance/stock read as-of the reporting date …)".*
- `financing_asset_movement` (a cash-flow movement): *"As-of (point-in-time) snapshot balance (sum) … as-of balance date (a stored balance/stock read as-of …)".*
- `change_in_current_assets` (a period delta): *"As-of (point-in-time) snapshot balance (sum) …".*

A flow's meaning is a quantity **accrued over a period**; defining it as a stock **read at one date** declares a different meaning than the one the member names and the one a reader expects. Reshaping only the gate shape and leaving the definition wording in place would leave Invariant I violated at the declaration.

**The same concepts, done right — the reference pattern.** The `cumulative_to_date` family on the **journal-entry-line grain** (11 contracts, all active) expresses the balance-sheet and earnings concepts **correctly**: e.g. `current_asset_balance`, `total_asset_balance`, `current_liability_balance`, `recorded_equity_balance`, `non_current_liability_balance`, `earnings_to_date`, `receivable_control_balance` = *"the sum of amount_input, the posted amount of each journal-entry line …, over [period to date]"* — a real period-end row selection, not an identity read. This is the pattern the reshape targets, and it is **load-bearing for the stocks**: the 6 `point_in_time` GL-Account-grain stocks are wrong-shaped duplicates of concepts the JEL `cumulative_to_date` family already states correctly (see Decision 2, stocks).

**Active exposure (corrected to substrate).** Of the 27 concepts, **6 are producing today**: the 5 counts (`gl_account_count`, `financing_/investing_/operating_gl_account_count`, `cost_center_count`) and `current_liabilities` (via its active `__tacorr` variant) each have an active current version. Their grains' canonical contracts are active, so the evaluator runs them now — a **date-less current snapshot presented as an as-of value** (worse than non-producing: it looks authoritative). The remaining 21 concepts have **no current version** (in-flight / `audit_pending`); they are **latent** exposures that become live on activation.

**Why an ADR, not a directory-clean or an evaluator patch.** The declared meaning is wrong at the contract layer. Correcting the directory classification (read model, F) or adding an evaluator selection (D) without first re-declaring the member's true shape and definition would be lower-layer compensation for an upper-layer declaration gap — forbidden by DEC-c48b0f and the Invariants. The faithful repair is a declaration act at **repair location B** (contract semantics).

## Decision

1. **The reshape target is the member's economic meaning, not its current (wrong) shape.** Each member is re-declared to the shape that evaluates its true meaning once, correctly (Invariant I). The current `point_in_time` shape is retained for a member only where identity selection already equals its intended value (a current-state read whose grain yields a single-reporting-date candidate set) — per DEC-d0b66a Decision 5.

2. **Per-member disposition, grouped by target shape.** Metric's per-member triage (first-hand, MSG-e6764c) is the authority for each member's target; this ADR records the target-shape doctrine and the groupings.

   - **Stocks (6) → `as_of`.** `current_assets`, `current_liabilities`, `total_assets`, `total_equity`, `total_liabilities` (GL Account grain); `total_standard_cost` (Product grain). A balance-sheet stock is the value **at** a reporting date; its faithful shape is `as_of` (real max-anchor-≤-P row selection) — **gated** on the per-input period predicate (Decision 4). **Sub-decision (duplicate vs distinct grain):** each of these GL-Account-grain stocks has an already-correct counterpart in the `cumulative_to_date` JEL family (e.g. `current_assets` ↔ `current_asset_balance`). Where the two express the **same** economic concept, the faithful repair is **supersession by the existing JEL member** (abandon the duplicate; soft-archive the parent, never mutate the version — Invariant III), not a parallel `as_of` reshape. Where a distinct stored-balance grain read is genuinely intended, the `as_of` reshape applies. **Metric confirms, per stock, duplicate-vs-distinct-grain before the stock reshape executes.**
   - **Counts (5) → `as_of` count.** `gl_account_count`, `financing_/investing_/operating_gl_account_count` (GL Account grain); `cost_center_count` (Cost Center grain). A count of a grain's members **as of** a reporting date is a stock-like as-of read (row-count basis, not COUNT_DISTINCT), not an identity re-count across every reporting date in the candidate set — **gated** on the per-input period predicate (Decision 4). These 5 are **actively producing today** (Context, active exposure).
   - **Flows (16) → `period_aggregate` or `cumulative_to_date` (never `as_of`).** The 8 P&L amounts (`operating_revenue_amount`, `cost_of_sales_amount`, `operating_expense_amount`, `other_expense_amount`, `other_income_amount`, `interest_expense_amount`, `tax_expense_amount`, `depreciation_amortization_amount`); the 2 period deltas (`change_in_current_assets`, `change_in_current_liabilities`); the 6 cash-flow movements (`financing_/investing_` × `asset_/equity_/liability_movement`). The **per-member choice between period (`period_aggregate`) and year-to-date (`cumulative_to_date`) is Metric's call**, by the member's intended meaning. Two notes: (a) the 2 `change_in_*` deltas are **differences of two balances** (end(P) − start(P)), not a single-sign period sum — their declaration must express the difference, not a `period_aggregate` of raw amounts; (b) all 16 still require the period basis to select the period (Decision 4).
   - **Related `none`-shape defects (2) → `period_aggregate`.** `write_off_amount` (Customer Invoice grain); `customer_invoice_line_item_count` (Customer Invoice Line Item grain). Not `point_in_time`, but the same meaning-fidelity class: a shapeless flow must be declared `period_aggregate` with a period basis.
   - **Questionable (1): `total_cash_balance`** (already `as_of`, with a NULL closing field). Either declare its closing basis (the as-of closing field) or record, with rationale, that none is needed; do not leave the field silently null.
   - **`__tacorr` variants.** The disposition attaches to the **concept**: a base member and its `__tacorr_*` companion are reshaped together (where `current_liabilities` carries its meaning on the active `__tacorr` variant, that variant is the one reshaped).

3. **Name↔definition fidelity is corrected in the same act.** For every flow (and the `none`-shape defects), the **definition wording is re-authored** to its true flow/cumulative meaning in the same reshape; the as-of-snapshot phrasing is removed. Correcting the shape while leaving the definition describing an as-of stock read would record a new version whose declared meaning still contradicts its shape (Invariant I). Shape and definition are re-declared as one design act per member.

4. **Gate: the `as_of`, count-`as_of`, and all flow reshapes are sequenced AFTER the per-input period predicate (TSK-36440f, "ADR #2").** Without real reporting-date / period selection, `as_of` is as degenerate as `point_in_time` (identity), and a flow cannot select its period. No reshape yields a correct value before that selection mechanism exists. This ADR **declares** the targets and **defers** execution to after TSK-36440f lands (and the standing write-lane halt lifts). It builds nothing and asserts no closed gap (consistent with DEC-d0b66a Decision 7).

5. **Active exposure is recorded, not latent.** The 6 producing members (5 counts + `current_liabilities` via `__tacorr`) emit a date-less current snapshot presented as an as-of value **today**. This is recorded as an **active meaning-fidelity exposure** (risk RSK-2ff5b1 / the DEC-d0b66a wrong-data risk). Until the reshape executes, they remain exposed; the ADR does not by itself remediate them. The other 21 concepts are latent (no current version) and become exposures on activation.

6. **Foundation.** Repair **location B** (contract semantics — the declared temporal meaning). This is a **design act** (a wrong/missing declaration of true meaning), not a detector: per DEC-c48b0f item 5, an execution-plane detector is a net, not a fix, so correcting the gate's refusal would not repair the declaration. No lower-layer compensation: the directory must not clean these members on "`point_in_time` = identity," and the evaluator selection (TSK-36440f) is a necessary separate act, not a substitute for the declaration. Invariant III holds throughout: reshape mints new versions / supersedes; it never mutates an existing version row, and abandonment soft-archives the parent.

## References

- Governing: **DEC-d0b66a** (decided — `point_in_time` resolves to identity; generator over-claims; members not auto-clean; reshape is its own design act).
- Generator layer: **DEC-5842d4** (implemented — Metric Directory Knowledge & Governance Layer), whose `buildGateArtifacts` generator (`metric-directory.service.ts:289-305`) asserts the as-of runtime semantic the evaluator does not deliver.
- Foundation: `foundation/the-invariants.md` Invariant I (meaning is evaluated once), Invariant III (immutability); **DEC-c48b0f** (certification is a lifecycle act; no lower-layer compensation; a detector is a net, not a fix).
- Gate: **TSK-36440f** ("ADR #2" — the per-input period predicate for `point_in_time`; planned/next). Risk: **RSK-2ff5b1** (the `point_in_time` runtime wrong-data risk).
- Reference pattern: the `cumulative_to_date` journal-entry-line family (`current_asset_balance`, `total_asset_balance`, `current_liability_balance`, `recorded_equity_balance`, `non_current_liability_balance`, `earnings_to_date`, `receivable_control_balance`, …) — the same concepts expressed correctly.
- Substrate grounding: `bc_platform_dev` `mcf.metric_contract` / `mcf.metric_contract_version`, read 2026-10-07 (49 `point_in_time` contracts = 27 base + 22 `__tacorr`; 6 active current versions; flow definitions quoted verbatim).
- Per-member split source: Metric MSG-e6764c; ruling returned to Metric MSG-746607.
