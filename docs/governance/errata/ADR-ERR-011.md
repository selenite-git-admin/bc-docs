---
id: ADR-ERR-011
title: "DEC-3926bf Amendment 2's residual-as-of-P derivation is at PE-MC (M13), not the canonical layer (C); C carries the dated application schedule"
status: open
authority: authoritative
affected: DEC-3926bf (D664) — Amendment 2 ("Option B derivation shape") clause "DERIVE (C/CC): residual-as-of-P = gross − Σ(applied ≤ P) at the canonical", and its Foundation-gate "Repair A+B+C"
resolution: correction recorded here; Amendment 2's gross→residual meaning-change and Option B decision stand unchanged; the residual-as-of-P derivation LAYER is PE-MC (M13), not the canonical (C) — C carries only the P-independent dated application schedule; the evaluator capability is declared in DEC-c741a3 (D665)
opened: 2026-10-14
---

# ADR-ERR-011 — DEC-3926bf Amendment 2: residual-as-of-P is derived at PE-MC (M13), not the canonical (C)

## Contradiction summary

DEC-3926bf Amendment 2 adopted the gross→residual meaning-change for the aging/overdue family (Option B) and stated its derivation shape as: "ADMIT (A/OC) the dated application events; **DERIVE (C/CC): residual-as-of-P = gross − Σ(applied ≤ P) at the canonical**", with a Foundation gate of "Repair A+B+C". That names the **canonical layer (C)** as where residual-as-of-P is derived.

residual-as-of-P = f(P) is **P-dependent** (it varies with the evaluation period P). The canonical object (CO) is built **once per admission, P-independently** — so a quantity that varies with P cannot be a single canonical value. The "DERIVE at C" layer statement is therefore wrong: the derivation cannot live at the canonical layer.

## Implementation behaviour

Grounded at the served build (freeze-v `04cc7f97`), independently by Platform and the Chief:

- `buildCoPayload` builds the CO once per admission, with no evaluation period — the CO is P-independent.
- `evaluateGovernedMetric` (`governed-metric-runtime.ts:398`) threads `asOf` (P) **only** into `selectByGate` (selection). `buildSectionA` (L312/L415) and `FormulaExecutionEngine.execute` take **no** `asOf` — the aggregation phase is P-blind.
- So the canonical/aggregation layers provably cannot compute `Σ(applied WHERE application_date ≤ P)`. P-dependent aggregation must live at the metric evaluator (PE-MC / M13), where P is bound.

## Resolution

Amendment 2's **decision stands unchanged**: the aging/overdue family ages the residual/outstanding balance (gross+binary was a meaning-defect), gross − Σ(applied ≤ P) is the semantic, and `ar_balance` retires to the outstanding control balance. This entry corrects only **where** the P-dependent part is realized:

1. **residual-as-of-P and the binary open/settled (residual > 0) are computed at PE-MC (M13)**, not the canonical layer — Repair **D** (evaluation implementation). The evaluator capability this requires is declared in **DEC-c741a3 (D665)** (the PE-MC as-of conditional aggregate: a P-aware signed sum over a sub-grain dated schedule, rolled to the metric grain). "Repair A+B+C" in Amendment 2 is corrected to **A + B + D** (A admits the schedule, B declares the meaning, D computes the P-dependent aggregate).
2. **The canonical layer (C) carries only the P-INDEPENDENT dated application schedule** (per-event applied amount + application date, at event grain) — no as-of aggregation.
3. **`clearing_date` is dropped.** R1 found no Wave-1 invoice-grain metric consumes a settlement-date **value** (open/settled-at-P = residual > 0 at PE-MC covers the binary), so the canonical group-max-date extension Amendment 1/D1 contemplated for clearing_date is not built. clearing_date is not a canonical field; the open/settled predicate is the residual sign at PE-MC.
4. **Realized `outstanding_amount` vocabulary** (which Amendment 2 referenced as the to-be-authored `amount_residual`): the governed characteristic `outstanding amount` `b3661d56` (frozen, cert `6e17814a`), bound as AR concept `9e5423e0` (Customer Invoice `e3963e45`) and AP concept `1a45f9e4` (Supplier Invoice `4471cb17`), representation amount/decimal. This is the P-dependent residual the DEC-c741a3 capability computes from the dated schedule.
   - **Transparency note (immutable-freeze hygiene):** the frozen characteristic definition is a fuller prose version than the terse paraphrase quoted in the finality grant (bc-exchange #256); it was independently confirmed semantically identical and more complete, and the grant named the registry object by id (`b3661d56`), so the operator's finality affirmation bound to the registry object whose bytes are faithful. No semantic drift.

This changes no decision: the P-dependent/as-of part is evaluation (DEC-c48b0f), which belongs at the evaluator; Amendment 2's meaning and Option B are intact.

## Resolution state

The layer correction stands as recorded. Full realization rides **DEC-c741a3 (D665)** (the PE-MC as-of aggregate capability) being accepted and built (red-first + Codex engine-lane + a Chief-gated serve-move), then the terminal demo-tenant fixture re-provision (Amendment 1) admitting the clean event-grain schedule. Open until DEC-c741a3 lands and the capability is built. Recorded by the Architect, SES-b9b0ef, 2026-10-14.
