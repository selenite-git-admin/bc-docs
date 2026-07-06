---
uid: DEC-69a24a
title: "Foundation Boundary Precision — tighten conceptual model to match implementation reality"
description: "Clarify that boundaries are logical state transitions (not physical ops), batch writes are valid, and typed payload tables are allowed."
status: proposed
subdomain: foundational-architecture
focus: evidence-scope-batch-validity
date: 2026-03-25
project: platform
domain: database
refs:
  - type: decision
    label: "D210"
  - type: decision
    label: "D211"
  - type: decision
    label: "D212"
authority: evolving
migrated_from: legacy v2 archive
---


# Foundation Boundary Precision — tighten conceptual model to match implementation reality

## Context

The foundation was written as a conceptual visualization, not a literal implementation spec. D210-D212 review exposed three areas where boundary definitions are imprecise or contradict each other. Tightening the foundation to distinguish logical state transitions from physical operations prevents future architectural decisions from being blocked by conceptual model ambiguity.

## Problem

The foundation specification was written as a conceptual/visualization model describing how the system thinks about data progression. Several boundary definitions are imprecise or internally contradictory when read as implementation constraints. This creates confusion when reviewing architectural decisions (D210, D211, D212) against the foundation.

### Contradictions found during D210-D212 review

**1. Evidence Object scope vs. current implementation**

Foundation says:
- "An Evidence Object is created only in reference to an existing Canonical Object, Metric Snapshot, or Intervention."
- "An Evidence Object must not reference any Source Object, Observed Record, Admitted Record, or Evaluation."

Current implementation creates evidence with `subjectRef: source_object:{id}` and `boundary: observation`. This directly violates the foundation spec. Either the foundation is wrong (evidence should be allowed at all boundaries) or the implementation is wrong (shouldn't create evidence at observation).

D212 resolves this by eliminating the separate evidence table entirely, but the foundation text still needs updating.

**2. Object creation at Observation Boundary**

Foundation Observation Boundary spec says:
- "An Observed Record may be created at this boundary. No other system object may be created here."

Foundation Source Object spec says:
- "A Source Object is created at the observation boundary from exactly one Observed Record."

These contradict — the boundary says "no other objects" but the Source Object spec says SOs are created there. The state progression (Observed → Sourced) suggests these may be sub-steps within the observation boundary, but the boundary spec doesn't describe this.

**3. "Object created at boundary" — logical vs. physical**

The foundation uses "created at" ambiguously. Does it mean:
- The object's logical state transition happens at this boundary? (conceptual)
- The INSERT statement runs at this boundary? (physical)
- The object is semantically scoped to this boundary's concern? (domain)

This matters for D211 (batch writes) — if "created at" means physical INSERT, then batching changes the semantics. If it means logical state transition, batching is just an optimization.

## Decision

**Update the foundation specification to clarify three things:**

### 1. Boundary = logical state transition, not physical operation

A boundary describes WHEN an object transitions between states. It does not prescribe HOW the physical write occurs. Batch INSERTs, typed payload tables, and write optimizations are implementation choices that preserve the logical model.

### 2. Evidence/lineage is a structural property, not a separate object requirement

The traceability guarantee (any object can be traced back to its source through an unbroken chain) is satisfied by structural FK relationships between boundary objects. The foundation should describe the PROPERTY (unbroken traceability) rather than prescribing the MECHANISM (separate evidence objects).

Update the evidence spec to say: "Every boundary object carries a reference to its predecessor object and the contract version that governed its creation. These structural references form an unbroken lineage chain. The system may provide a unified traversal interface over these references."

### 3. Observation boundary produces OR + SO as an atomic unit

Clarify that the observation boundary admits data from external sources and produces an Observed Record (what was seen) and a Source Object (what was admitted under contract) as a single atomic operation. The OR → SO progression is internal to the boundary, not a separate boundary crossing.


## Options Considered

N/A

## Scope

This is a documentation/governance task. It does not change the system's behavior — it brings the conceptual model into alignment with implementation decisions D210, D211, D212 so future sessions don't have to re-derive the same conclusions.

## Patent Alignment

The patent describes Evidence Objects as a plane. The foundation update preserves the plane's PURPOSE (traceability, immutability, deterministic replay) while allowing the implementation to deliver these properties structurally rather than through a separate object type. The patent's inventive claims are about the traceability properties, not the storage mechanism.

## Consequences

N/A
