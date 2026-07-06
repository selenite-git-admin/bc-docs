---
id: FND-ERR-003
title: "Metric cardinality is N:1 (Metric Contract to Canonical Contracts)"
status: adopted
authority: authoritative
affected: Foundation §6 (metric evaluation)
temporary_governance:
  - DEC-29c324
target_resolution: Foundation v2 metric-cardinality statement
opened: 2026-04-23
---

# FND-ERR-003 — Metric cardinality N:1 (MC to CC)

## Contradiction summary

Foundation §6 describes metric evaluation as producing one Metric Snapshot from exactly one Canonical Object. The cardinality implied is linear: 1 Canonical Contract → 1 Metric Contract → 1 Metric Snapshot. In the platform implementation, a single Metric Contract may reference multiple Canonical Contracts via `metric_binding` entries, producing one Metric Snapshot whose evaluation draws from N Canonical Object versions.

## Implementation behavior

- A Metric Contract declares one or more Canonical Contract bindings. Each binding names a role (primary, joined, reference) and the specific Canonical Contract it binds to.
- At the metric evaluation boundary, the platform resolves each binding to a specific Canonical Object version at the declared evaluation time, applies the Metric Contract's formula, and emits one Metric Snapshot.
- The Metric Snapshot carries references to all Canonical Object versions consumed, preserving full ancestry.

This cardinality is N:1 at the contract layer and N:1 at the evaluation layer. The Foundation's linear framing was a historical simplification that did not survive real-world metric design: most business metrics compose values from multiple canonical domains (for example, revenue from invoicing plus cost-of-goods from inventory).

## Temporary governance

**DEC-29c324** codifies the N:1 cardinality and defines the `metric_binding` shape, role semantics, and evaluation ordering.

## Resolution state

**Adopted.** The platform's cardinality is correct. Foundation v2 will state that a Metric Contract may reference N Canonical Contracts, and a Metric Snapshot may draw from N Canonical Object versions, each preserved in Lineage. This erratum closes when Foundation v2 publishes the revised cardinality statement.

## References

- DEC-29c324 — Metric N:1 cardinality
- Chapter 10 — Metric Runtime (describes `metric_binding`, role semantics, and evaluation order)
- Appendix A — metric-v1 contract schema body page
- Foundation §6 — affected section
