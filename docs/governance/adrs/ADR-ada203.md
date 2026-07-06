---
uid: DEC-ada203
title: "Composite (metric-of-metrics) evaluation — resolve upstream snapshots + reuse the formula engine"
description: "Composite (metric-of-metrics) evaluation — resolve upstream snapshots + reuse the formula engine"
status: decided
date: 2026-07-02T11:18:03.337Z
project: bc-core
domain: metrics
subdomain: metrics/runtime
focus: runtime
---

# Composite (metric-of-metrics) evaluation — resolve upstream snapshots + reuse the formula engine

## Context

19 of pilot1's 51 active MCF metrics (days_sales_outstanding, collection_effectiveness_index/ratio, accounts_receivable_turnover, all AR concentration/composition/percentage metrics) are composites blocked ONLY because metric-variable-resolver rejected metric_input as 'ADR #3, not evaluable over Canonical Objects'. The blocker is not data and not the engine (FormulaExecutionEngine already evaluates the 5 arithmetic ops + variable_ref + literal); it is the missing resolve-upstream-snapshot step + routing. With the base metrics now producing governed snapshots on pilot1 (e.g. ar_balance 10,306,696.90, gross_invoiced_amount 19,019,959.32), the composites become computable — DSO = (ar_balance / gross_invoiced) x 90 = ~48.8 days. Reuses the atomic persistence act (DEC-5ea578) and the version-normalization + fact.ms_ self-provisioning already built. Foundation: composites read upstream snapshots (immutable, already-emitted evidence — Invariant VI); evaluation is emitted once per (composite, period) and non-replayable; no CO re-evaluation. Highest-leverage of the three runtime gaps (composite 19 vs filter 9 vs grouping 4) and unblocked now.

## Decision

Composite metrics — those whose variable bindings have role_kind_code='metric_input' (they reference upstream Metric Snapshots, not Canonical Object fields) — are evaluated by a dedicated composite path, NOT the CO-enumeration path: (1) resolve each metric_input variable to its referenced metric's snapshot value for (tenant, evaluation period) per snapshot_selection_rule_code — 'period_matched' = the upstream snapshot whose fiscal_period equals this period; 'as_of_period_end' = the upstream's latest accepted snapshot at/before the as-of point P — read from progression.metric_evaluation + fact.ms_<upstream>_v<ver>; (2) build a Section A of {variable_role_code → scalar value} and evaluate the composite's arithmetic formula AST (plus/minus/multiply/divide/mod + literal + variable_ref) via the EXISTING FormulaExecutionEngine (which already supports arithmetic); (3) persist via the EXISTING GovernedMetricPersistenceAdapter (atomic act: progression.metric_evaluation + fact.ms_ self-provisioned + run finalize). Guard (fail-closed, honest): if any upstream snapshot is missing for the period, DEFER (deferred_inputs_unavailable) rather than compute a partial value. New: CompositeMetricEvaluationService + orchestrator routing (a metric whose input bindings are all metric_input takes the composite path) + metric-variable-resolver RESOLVES metric_input (returns {upstreamMetricUid, snapshotSelectionRule}) instead of rejecting it. Evaluate in dependency order: base metrics first (over COs), then composites (over base snapshots); composites-of-composites resolve transitively. Reuses the engine + persistence; the only genuinely new code is the upstream-snapshot resolver + the routing.

