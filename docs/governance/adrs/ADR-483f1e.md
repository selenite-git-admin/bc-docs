---
uid: DEC-483f1e
title: "The General Metric Runtime — substrate-driven, shape-dispatched governed-selection → aggregation"
description: "Every metric = governed-selection(predicate per temporal_gate shape over stamped fields + P) → aggregation(formula AST) → Snapshot + resolved-set Lineage. Generalize the governed selection to all 7 shapes; read mcf.* directly; retire the ARPI synthesizer; promote the AST engine to runtime."
status: decided
date: 2026-06-29T11:27:57.531Z
project: bc-core
domain: metrics
subdomain: metric-runtime
focus: architecture
---

# The General Metric Runtime — substrate-driven, shape-dispatched governed-selection → aggregation

## Context

The metric-space study (SES-8f76ae, read-only) established: (1) the runtime is doubly behind — it uses the weaker LEGACY string engine while the general AST engine exists but is fenced into the M10 verifier, never touching live COs; temporal_gate_shape is NEVER read at runtime; selection is absent (the runtime aggregates a handed-in 500-cap id-list from the readiness dispatcher). (2) The unification holds — all 7 shapes reduce to select-COs-where-predicate(stamped fields, P); flow vs state differ only in the predicate. (3) An existing latent Foundation breach: applyLookbackWindow cuts on Date.now() (read-time/wall-clock selection — Inv IV). (4) The ARPI synthesizer is ARPI-shape-locked debt (parseArpiAst throws on any non-divide(sum,count_distinct) AST); generalizing it is a dead end; reading mcf.* directly retires it + the legacy envelope. (5) Foundation already generalizes the governed-selection artifact at the invariant level (Inv IV); only the chapter examples were state-scoped. Promoting the unified governed-selection→aggregation model FIXES two latent violations (the Date.now() cut; the un-recorded dispatcher selection) while turning the metric runtime from a one-shape (ARPI) proof into the general engine the platform's amortization thesis requires — a runtime entangled with one metric is a demo, not a platform. Operator-locked the platform-integrity verification boundary (stop at chain integrity; tenant snapshots deferred to the SDG phase) to keep metric onboarding from being clubbed with impulsive data tests.

## Decision

THE GENERAL METRIC RUNTIME — every metric evaluates as a GOVERNED SELECTION (a declared predicate over stamped Canonical Object fields + the reporting point P, per the temporal_gate shape) → an AGGREGATION (the formula AST) → a Metric Snapshot + the resolved-set Lineage. The governed selection (DEC-c4c742) is GENERALIZED from state-only to THE metric-selection primitive for ALL SEVEN temporal_gate shapes; flow and state differ only in the predicate (interval-membership on an event time vs openness relative to P). Confirmed by the metric-space study: all 7 shapes reduce to select-COs-where-predicate(stamped fields, P). Extends DEC-c4c742; subsumes the route-B as-of work (DEC-83fda0) as one shape; neither superseded.

DECISIONS:
1. Unified model (above).
2. Widen the Foundation scope of the-governed-selection chapter + DEC-c4c742 from {as_of, cumulative_to_date} to 'the temporal_gate shape'. No invariant changes — Invariant IV already frames the artifact generally ('resolves the object versions a reference names; single-version = the degenerate set-of-one case'); only the chapter's worked surface was state-scoped (editorial).
3. Substrate-driven runtime; RETIRE the ARPI synthesizer. The runtime reads mcf.* directly: grain_entity_id → enumerate COs (FactReaderService.listCanonicalObjects); temporal_gate_shape+params → the selection predicate; metric_filter_clause[] → refine; formula_ast_canonical_json + metric_variable_binding[] → aggregate. The ARPI-hardcoded mcf-contract-json-synthesizer + the legacy contract_json envelope retire for MCF metrics — generalizing the synthesizer is a dead end (the legacy string-formula grammar cannot express case/window/bucket/percentile/as_of).
4. Promote the general AST engine (FormulaExecutionEngine — today wired only to the M10 verifier, never touching live COs) to the RUNTIME aggregation, replacing the legacy string engine (MetricEvaluationEngine). A SEPARATE seam from selection; lands independently.
5. Dispatch seam at metric.service.ts evaluateMetricInner (~line 120, replacing applyLookbackWindow): selectByGate(candidates, shape, params, P) → shape→predicate→resolved set. ADDITIVE — period_aggregate routes to pass-through first so no live flow metric breaks.

CORRECTNESS SPINE (Foundation non-negotiables): (a) the recorded Lineage input set MUST be the predicate-RESOLVED set (post-selection), not the handed-in candidate list — today inputReferencesJson records the pre-selection 500-cap candidates (Inv IV/VI breach the moment a predicate runs); (b) KILL applyLookbackWindow's Date.now() wall-clock cutoff (a read-time selection Inv IV forbids — an EXISTING latent breach); (c) disambiguate selection-vs-grain for period_aggregate (period membership is a declared predicate, not an implicit GROUP BY side-effect — so the resolved set matches the aggregated set).

SECONDARY/DERIVED metrics (DSO etc.) = the same select→aggregate with the candidate POPULATION swapped from COs to upstream Metric Snapshots; a substrate extension (role_kind_code + the selection source). DEFERRED (DSO unauthored); the model accommodates it — not a fourth kind.

VERIFICATION BOUNDARY (operator-locked): verified AT THE PLATFORM LEVEL ONLY — unit tests of the per-shape predicates + dispatch + aggregation over controlled inputs, AND chain integrity (chain_status green). STOP AT CHAIN INTEGRITY. Tenant metric-snapshot validation is a SEPARATE, later, SDG-fine-tuned phase — no impulsive tenant data.

SEQUENCE: (1) this ADR + the chapter widening; (2) build the selection layer (selectByGate + per-shape predicates; reuse the proven resolveAsOf + listCanonicalObjects) honoring the correctness spine → verify by unit + chain integrity; (3) promote the AST engine to runtime + retire the synthesizer; (4) secondary metrics; (5) the metric library scales on one general runtime. Repair-location B (selection grammar per shape + scope widening) + D (dispatch + engine). No lower-layer compensation.

## Amendment — seam correction (SES-e736e5, 2026-06-29)

Grounding the live substrate during the build (read-only) corrected Decision 5's seam assumption:

- `contract.metric_contract_version` (the table `metric.service.evaluateMetric` reads) is **EMPTY** — 0 rows. All 10 live metrics are in `mcf.*` (`mcf.metric_contract` = 10), every one `temporal_gate_shape_code = 'period_aggregate'` (8 active, 2 review), pre-runtime-crossing. So the legacy `metric.service.evaluateMetricInner` path — and its `applyLookbackWindow` — see **no live metric**; Decision 5's seam targeted a dead path. `applyLookbackWindow` is left untouched (dead) until the legacy path is formally retired; it is NOT the wiring point for the general runtime.

- **Corrected seam.** The general runtime is a NEW `mcf.*`-direct module — `bc-core/src/boundary/governed-metric-runtime.ts` `evaluateGovernedMetric(spec, candidates, P)` — composing `gate-spec-from-substrate` (authored kernel → GateSpec) → `select-by-gate` (`selectByGate`, reusing `governed-selection`) → the **existing, unmodified** `FormulaExecutionEngine` over the resolved set, with grain-grouping (one result per fiscal period). The AST engine was only *usage*-fenced to the M10 verifier (not code-fenced), so Decision 4's "promotion" was pure composition — no engine change.

- **Correctness spine status.** (b) the `Date.now()` cut is removed *by construction* — the new path has no `applyLookbackWindow`; selection is P-relative (proven by a P-in-the-past unit test). (a) the resolved set is returned as `GateSelection` for the caller to record in Lineage. (c) `period_aggregate` selection is identity + an explicit grain-grouping pass (declared), not an implicit GROUP BY.

- **Built + proven + committed (platform level, no tenant data).** Selection layer + bridge + runtime core + grain-grouping — 47 unit tests; from constructed COs the path reproduces the real-DB `2800 / 1900` and per-period `Q1=300 / Q2=700`. Commits `f83ada4f`, `eba8a48a` (branch `feat/route-b-as-of-governed-selection`).

- **Deferred to the SDG phase (TSK-8570e8).** The live I/O wrapper — the spec loader (`mcf.*` → `GovernedMetricSpec`) requires a C-layer binding resolution (`metric_variable_binding.bound_business_concept_id` → canonical field → CO payload key via the CC), which needs the live COs + the canonical contract; plus CO enumeration (`listCanonicalObjects`) and Snapshot + Lineage persistence. These produce numbers only against tenant data, so they land in the deliberate SDG-fine-tuned phase, batched over ~25 AR metrics — not now.

Decisions 1-4, the correctness spine, and the verification boundary stand. Only Decision 5's seam *location* is corrected: `mcf.*`-direct via `governed-metric-runtime`, not `metric.service:120`.
