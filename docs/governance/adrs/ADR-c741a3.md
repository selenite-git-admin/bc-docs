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

residual-as-of-P = f(P) is P-dependent; the canonical object is built once per admission P-independently, so it cannot be a canonical value (canonical-resolver NO-GO, verified). The served evaluator threads asOf only into selectByGate (selection); buildSectionA + FormulaExecutionEngine.execute take no asOf, so the aggregation phase cannot sum a dated schedule WHERE date<=P (verified @freeze-v 04cc7f97: governed-metric-runtime.ts:398; buildSectionA L312/L415 — Chief + Platform independently grounded). P-dependent aggregation must live at the evaluator (D) where P is bound. Additive P-threading keeps the blast radius bounded (only the new kind consumes P; working P-blind nodes untouched — Inv-III-respecting). Foundation gate (DEC-79b62f): Repair D design act; (Q1) D because P lives only at the evaluator; (Q2) not upper — A/B/C are provably complete (outstanding_amount authored+frozen+correct at B; event-grain dated schedule admitted at C), so D is NOT compensation; (Q3) not lower — reads/projections are P-blind and a read computing it is the forbidden reads-trigger-evaluation; (Q4) DESIGN act — the evaluator grammar has no as-of conditional-aggregate kind, so the declaration must be named/recorded, not just implemented. Extends the M13 PE-MC evaluator gate. Chief+Architect co-decision; build HELD pending this ADR's acceptance + red-first.

## Decision

Declare a new PE-MC/M13 metric-evaluator capability: an AS-OF CONDITIONAL AGGREGATE — a P-aware signed sum over a sub-grain dated event schedule, rolled to the metric grain. asOf (P) is threaded ADDITIVELY into the aggregation phase so ONLY this new aggregate kind binds P (existing P-blind nodes — positional window, time_anchor passthrough, static bucket/filter — stay unchanged); buildSectionA associates the sub-grain events (the invoice's dated application legs) into the metric-grain group; the aggregate computes per group Σ(signed value WHERE event_date <= P). This enables P-dependent quantities (residual-as-of-P = gross - Σ(signed applied <= P)) that the current two-phase evaluator (P-aware selection, P-blind aggregation) provably cannot express. It is an AGGREGATE kind, not a new gate (the as_of gate stays selection/open-at-P). One capability serves BOTH Option-B residual aging AND the binary open/settled via residual>0 (no clearing_date value needed — R1: no consumer). Repair D (evaluation implementation); the canonical layer stays P-independent and carries only the dated schedule; NOT a canonical/ccv2 change. Build is red-first + Codex engine-lane (Lane: platform) + a gated serve-move; this ADR is the design-act declaration the build reviews against.
