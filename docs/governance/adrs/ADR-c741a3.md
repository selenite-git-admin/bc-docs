---
uid: DEC-c741a3
title: "PE-MC as-of conditional aggregate: the metric evaluator gains a P-aware signed sum over a sub-grain dated schedule"
description: "PE-MC as-of conditional aggregate: the metric evaluator gains a P-aware signed sum over a sub-grain dated schedule"
status: proposed
date: 2026-10-14T14:57:13.703Z
project: bc-core
domain: metrics
subdomain: metrics/pe-mc-evaluator
focus: runtime: as-of conditional-aggregate evaluator capability (M13)
---

# PE-MC as-of conditional aggregate: the metric evaluator gains a P-aware signed sum over a sub-grain dated schedule

## Context

residual-as-of-P = f(P) is P-dependent; the canonical object is built once per admission P-independently, so it cannot be a canonical value (canonical-resolver NO-GO, verified). The served evaluator threads asOf only into selectByGate (selection); buildSectionA + FormulaExecutionEngine.execute take no asOf, so the aggregation phase cannot sum a dated schedule WHERE date<=P (verified @freeze-v 04cc7f97: governed-metric-runtime.ts:398; buildSectionA L312/L415 — Chief + Platform independently grounded). P-dependent aggregation must live at the evaluator (D) where P is bound. Additive P-threading keeps the blast radius bounded (only the new kind consumes P; working P-blind nodes untouched — Inv-III-respecting). Foundation gate (DEC-79b62f): Repair D design act; (Q1) D because P lives only at the evaluator; (Q2) not upper — A/B/C are provably SPECIFIED (outstanding_amount authored+frozen+correct at B; the event-grain dated schedule is DESIGNED at A/C, its admission Amendment-2-sequenced future work — specification-complete, NOT yet a working input path), so D is NOT compensation for an underspecified upper layer; (Q3) not lower — reads/projections are P-blind and a read computing it is the forbidden reads-trigger-evaluation; (Q4) DESIGN act — the evaluator grammar has no as-of conditional-aggregate kind, so the declaration must be named/recorded, not just implemented. Extends the M13 PE-MC evaluator gate. Chief+Architect co-decision; build HELD pending this ADR's acceptance + red-first.

## Decision

Declare a new PE-MC/M13 metric-evaluator capability: an AS-OF CONDITIONAL AGGREGATE — a P-aware signed sum over a sub-grain dated event schedule, rolled to the metric grain. asOf (P) is threaded ADDITIVELY into the aggregation phase so ONLY this new aggregate kind binds P (existing P-blind nodes — positional window, time_anchor passthrough, static bucket/filter — stay unchanged); buildSectionA associates the sub-grain events (the invoice's dated application legs) into the metric-grain group; the aggregate computes per group Σ(signed value WHERE event_date <= P). This enables P-dependent quantities (residual-as-of-P = gross - Σ(signed applied <= P)) that the current two-phase evaluator (P-aware selection, P-blind aggregation) provably cannot express. It is an AGGREGATE kind, not a new gate (the as_of gate stays selection/open-at-P). The capability computes residual-as-of-P for the Option-B aging/overdue family; for those residual-bearing members the binary open/settled is residual>0. D1's NON-AGING binary-open as_of members are UNCHANGED (Option A, clearing_date as the as_of-gate closing_field, per DEC-3926bf D1) and are NOT addressed by this ADR — clearing_date is preserved; this ADR neither drops clearing_date nor retires D1 nor replaces those members' selection gate. Repair D (evaluation implementation); the canonical layer stays P-independent and carries only the dated schedule; NOT a canonical/ccv2 change. Build is red-first + Codex engine-lane (Lane: platform) + a gated serve-move; this ADR is the design-act declaration the build reviews against.

## Foundation Gate (DEC-79b62f)

Repair **D** (evaluation implementation). Design act (DEC-c48b0f): a missing DECLARATION — the evaluator grammar has no as-of conditional-aggregate kind — so it is named here, not merely implemented.
1. **Why D?** residual-as-of-P = f(P) is evaluation-time; the evaluation period P is bound only at the evaluator (the canonical object is built once per admission, P-independently — verified). The missing capability is the evaluator's.
2. **Why not an upper layer (A/B)?** A/B/C are provably SPECIFIED: the `outstanding amount` characteristic is authored, FROZEN and correct (B; cert 6e17814a); the event-grain dated application schedule is DESIGNED at A/C — its admission is Amendment-2-sequenced future work (specification-complete, NOT yet a working input path; this must not be read as evidence of an admitted path). No meaning or specification gap. So the D fix is NOT lower-layer compensation for an underspecified upper layer — this is the load-bearing gate answer.
3. **Why not a lower layer (E/F)?** No working lower implementation is bypassed; read models/projections are P-blind, and a read computing residual-as-of-P would be the forbidden reads-trigger-evaluation. P-dependent aggregation must live at D.
4. **Design or execution act (DEC-c48b0f)?** DESIGN — the declaration of a new evaluator aggregate kind. The per-run computation is execution, gated separately.

## Scope and shape

- **Kind:** an AGGREGATE kind, not a new gate. The `as_of` gate stays selection (open-at-P, returns refs); the new construct is the P-aware conditional aggregate.
- **(a) P-threading — additive:** `asOf` (P) is threaded into the aggregation phase (`FormulaExecutionEngine.execute` context / the new aggregate node) so ONLY the new kind binds P. Existing P-blind nodes (positional window, `time_anchor` passthrough, static bucket/filter) are unchanged; the numeric selectors (`strictNumericSelector`/A8) are untouched. Bounded blast radius; no P-everywhere rewrite.
- **(b) Event→metric grain association:** `buildSectionA` brings the metric grain's sub-grain events (the invoice's dated application legs — the schedule the canonical layer carries at event grain) into the grain group; the aggregate rolls the sub-grain schedule up to the metric grain: per group, Σ(signed value WHERE event_date ≤ P).
- **Scope — the residual-bearing aging/overdue family only:** delivers residual-as-of-P (Option-B aging/overdue) AND, for those members, the binary open/settled via residual > 0 (NOT free in the served build — it holds only once this capability exists). R1 found no metric surfaces the clearing_date VALUE, **but clearing_date IS consumed as the as_of-gate CLOSING_FIELD** (selection, open-at-P) by D1's non-aging binary-open members (Option A). So **D1 and its clearing_date are PRESERVED, unchanged, and out of scope here** — this ADR does not drop clearing_date, retire D1, or replace those members' selection gate. The clearing_date Option-A derivation (the P-independent full-settlement date; the numeric-only `latest_by` reduce) is a SEPARATE, re-opened design question — not resolved here, non-blocking on this residual/PE-MC path.
- **Layer:** PE-MC (M13), NOT canonical/ccv2. The canonical layer stays P-independent and carries only the dated schedule.

## Status

Proposed. Chief+Architect co-decision; Foundation gate passed (Repair D, design act). Extends the M13 PE-MC evaluator build-plan gate. The decided-status flip takes a recorded byte-bound operator desk grant (the DEC-3926bf #187/#188 pattern). The BUILD is HELD pending (1) this ADR accepted, (2) Platform's red-first spec (all branches) + Codex engine-lane (Lane: platform) review — which independently re-verifies the load-bearing P-threading premise, and (3) the Chief-gated serve-move.

## References

- **DEC-3926bf** (Kaveri Wave-1 invoice-chain unblock), Amendment 2 (gross→residual, Option B) declared residual-as-of-P; its "derive at the canonical (C)" layer statement is corrected by a separate forthcoming erratum (residual is evaluation-time, realized here at D). This ADR declares the evaluator capability Option B requires.
- Realized vocabulary: the `outstanding amount` characteristic `b3661d56` (frozen) + AR concept `9e5423e0` (Customer Invoice) + AP concept `1a45f9e4` (Supplier Invoice) — the P-dependent residual this evaluator capability computes from the dated schedule.
- **DEC-79b62f** (the Foundation gate), **DEC-c48b0f** (design vs execution act). M13 gate: `metric-context-framework-build-plan.md` (the PE-MC evaluator).
