---
uid: DEC-0f3e57
title: "MCF Secondary Metrics — metric-over-metric-snapshot DAG (Component D)"
description: "Implement MCF secondary metrics (a Metric Contract that reads upstream Metric Snapshots, forming an acyclic DAG) to unblock ratio-of-metric classes (DSO, turnover, CEI, overdue%, collection-efficiency)"
status: decided
date: 2026-06-30T01:43:00.850Z
project: bc-core
domain: metrics
subdomain: contracts/metric
focus: grammar-and-runtime
---

# MCF Secondary Metrics — metric-over-metric-snapshot DAG (Component D)

## Context

CB-007 (~10 cross-temporal: DSO/turnover/CEI/collection-period) and CB-011 (~12 incl. overdue%/collection-efficiency) are blocked not on substrate but on a metric-engine capability MCF never built. The Foundation already DEFINES this capability — The Object Model §Metric Snapshot states a snapshot is 'secondary when its Lineage references at least one other Metric Snapshot… Secondary snapshots form a directed acyclic graph of metric dependencies', and The Governed Selection cites DEC-483f1e (The General Metric Runtime) as the generalized authority. So this implements the Foundation rather than extending it. It is the highest-leverage, most Foundation-explicit, lowest-coupling component (no reference/cross-entity dependency) of the TSK-c7523f scope, and it reuses metrics that already exist live (AR Balance a11a88f4, Overdue Invoice Amount 72ddde1a, Gross Invoiced Amount cdd2a474) — DSO/overdue% are governed divisions of existing snapshots.

DECIDED (operator-locked 2026-06-30). Scoping authority: docs/implementation/metric-context-framework-reference-dimension-cross-entity-scope-2026-06-30.md §6 Component D. The authoring-substrate is specified by the locked DBCP `docs/implementation/metric-context-framework-secondary-metric-dag-substrate-dbcp-2026-06-30.md` (open decisions a–d resolved there; execution gated separately under the Database Change Protocol). This ADR is the foundational decision for a NEW MCF gate beyond build-plan M0–M20 (the build plan's computed dimensions are temporal-only; no secondary-metric gate exists).

## Decision

MCF implements **secondary metrics**: a Metric Contract whose evaluation reads one or more upstream **Metric Snapshots** (optionally alongside Canonical Objects) and computes a value, producing a **secondary Metric Snapshot**. The dependency graph across metrics is a **directed acyclic graph** (DAG). No new authoritative object type is introduced — the output is an ordinary Metric Snapshot whose Lineage references other snapshots (The Object Model §Metric Snapshot).

## Foundation grounding (this implements, does not extend)

- **The Object Model §Metric Snapshot — "Primary and secondary snapshots":** "A Metric Snapshot is secondary when its Lineage references at least one other Metric Snapshot in addition to Canonical Objects. Secondary snapshots form a directed acyclic graph of metric dependencies. The graph is descriptive only. Traversal reads preserved Lineage; it does not trigger recomputation." Disallowed: "A secondary Metric Snapshot is produced without Lineage to the other snapshots it references."
- **Invariant II (object ordering fixed):** a secondary metric derives only from objects of preceding type — Metric Snapshots — never from raw Source Objects, never by skipping. The DAG flows snapshot→snapshot, acyclic by definition.
- **Invariant IV + The Governed Selection (DEC-c4c742):** which snapshot of each upstream metric a secondary evaluation reads is resolved by a declared, versioned governed-selection predicate over the upstream snapshots' stamped fields and the evaluation parameter P — never "latest", never read-time. "a metric evaluation is one path: a governed selection, then an aggregation over the resolved set" — for a secondary metric the candidate set is the upstream snapshot set.
- **Invariant VI (evidence emitted):** the secondary snapshot emits Lineage to exactly the upstream snapshot versions it selected, synchronously.
- **General Metric Runtime — DEC-483f1e** is the cited generalized authority; this ADR is its secondary-metric instantiation.

## Grammar / substrate / evaluator shape (proposed)

1. **Input binding.** A new variable-binding role kind on `mcf.metric_variable_binding` — `role_kind_code='metric_input'` — binds a formula variable to an **upstream Metric Contract** (by metric_contract identity), not a Business Concept. (Today only `role_kind='input'`→BC exists.) The binding carries the upstream metric identity + the per-input snapshot-selection rule (below).
2. **Snapshot selection rule (per input).** Each metric_input declares, as a governed selection, which upstream snapshot the evaluation at period P reads — e.g. `as_of_period_end` (for a balance/state input like AR Balance) or `period_matched` (for a flow input like Gross Invoiced Amount). This is the temporal-alignment declaration that makes DSO well-formed (a point-in-time balance ÷ a period flow). The rule is versioned; the resolved snapshot version is recorded in Lineage.
3. **Formula AST.** Reuses the existing AST (divide/multiply/minus/sum/case — proven live SES-469bf4). `variable_ref` to a `metric_input` resolves to the selected upstream snapshot's value. No new node types required for the first cut (ratio/arithmetic over inputs).
4. **Acyclicity + identity.** The metric identity tuple extends to include the ordered set of upstream metric refs + their selection rules; authoring rejects a binding that would create a cycle in the metric-dependency graph.
5. **Lineage.** On evaluation the secondary snapshot's Lineage records each selected upstream snapshot version (Invariant VI; Object Model disallowed-behavior).
6. **Gates.** PE-MC extends with: upstream metrics are active; each metric_input's selection rule is valid for the upstream's temporal-gate shape; the DAG is acyclic. The M10 verifier handles secondary metrics by treating upstream snapshot values as fixture inputs (Section A supplies the input snapshot values; the verifier computes the formula) — no new verifier class beyond input-value substitution.

## Scope boundaries (first cut)

IN: arithmetic/ratio over N upstream Metric Snapshots with a declared per-input snapshot-selection rule; secondary-over-secondary allowed (acyclic). DEFERRED: window/rolling composition across multiple periods beyond the single per-input selection rule; cross-entity inputs (that is Component C, a separate ADR); auto-derivation of the selection rule (operator/authoring declares it explicitly).

## What it unblocks

CB-007: days_sales_outstanding (AR Balance as_of period-end ÷ Gross Invoiced Amount period × days), accounts_receivable_turnover, collection_effectiveness_index, average_collection_period. CB-011: overdue_ar / past_due_balance_percentage (Overdue Invoice Amount ÷ AR Balance), collection_efficiency. The component primary metrics already exist live; the secondary metric governs the combination. ~12 metrics.

## Why first (vs the customer-axis chain)

No reference/cross-entity dependency (those need the unbuilt reference→CO stamping path — scope §11). Most Foundation-explicit (defined verbatim in the Object Model). Highest leverage. Reuses live primaries. Smallest new grammar surface (one binding role-kind + a selection rule; reuses the AST + verifier).

## Open operator decisions

(a) Snapshot-selection-rule vocabulary (the closed enum of per-input temporal-alignment rules) — must align with the existing temporal-gate shapes. (b) Whether the secondary metric's own temporal gate is `period_aggregate` always, or inherits/derives from inputs. (c) Substrate: extend `mcf.metric_variable_binding` with a nullable upstream-metric FK + selection-rule columns vs a dedicated `mcf.metric_secondary_input` table — a gate-specific DBCP. (d) PE-MC numbering for the new acyclicity + alignment checks.
