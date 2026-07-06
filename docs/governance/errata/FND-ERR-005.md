---
id: FND-ERR-005
title: "Object count: 4 progression plus 2 proof, not 7 or 8"
status: adopted
authority: authoritative
affected: Foundation §2.2 (object taxonomy)
temporary_governance:
  - Chapter 2 (The Invariants)
  - Chapter 3 (The Object Model)
target_resolution: Foundation v2 object taxonomy
opened: 2026-04-23
---

# FND-ERR-005 — Object count: four progression objects plus two proof objects

## Contradiction summary

Foundation §2.2 describes the platform's object taxonomy in terms that admit at least three distinct readings:

1. A **7-object progression** framing, inherited from an earlier conflation of objects and operations (Source State → UinBAT Reader → SO → Canonical Evaluation → CO → Metric Snapshot → Action Object). This mixes objects with the processes that produce them.
2. An **8-object framing** that includes Metric Contract and Evaluation Object as first-class platform objects alongside SO, CO, Metric Snapshot, AO, EV, LO.
3. A **6-object framing** that names all authoritative objects (SO, CO, Metric Snapshot, AO, EV, LO) without distinguishing their relationship to the progression.

These readings are not equivalent and have led to drift in documentation and in conversation. The drift is concrete: some internal references say "7-object progression" while describing 4 types, some say "6 objects" while grouping evidence and lineage with the progression.

## Implementation behavior

The platform defines:

- **Four authoritative object types in a fixed, non-skippable boundary sequence:** Source Object → Canonical Object → Metric Snapshot → Action Object.
- **Two orthogonal proof objects** emitted at each evaluation boundary: Evidence Object and Lineage Object.

Contracts (Source, Admission, Observation, Canonical, Metric, Intervention) are grammar, not objects. They govern the production of objects but are not themselves in the progression. "Metric Contract" is an artifact of the contract grammar (Chapter 4); it is not a seventh authoritative object.

"Evaluation Object" mentioned in Foundation §2.2 appears to refer either to (a) the Metric Snapshot produced at the metric evaluation boundary, or (b) the evaluation act itself, which is a boundary operation, not an object. Neither reading adds a new authoritative object type to the platform.

## Temporary governance

**Chapter 2 (The Invariants)** and **Chapter 3 (The Object Model)** of v3 are the authoritative source for the object taxonomy. Both chapters state: four progression objects plus two orthogonal proof objects. The six-object total is correct; the 4+2 decomposition is the correct reading.

## Resolution state

**Adopted.** The 4+2 taxonomy is the correct reading. Foundation v2 will be revised to state the taxonomy explicitly in these terms and to remove the ambiguous 7-object and 8-object framings. This erratum closes when Foundation v2 publishes the revised object taxonomy.

## References

- Chapter 2 — The Invariants (Invariant II: object ordering is fixed)
- Chapter 3 — The Object Model (full object taxonomy)
- Chapter 4 — The Contract Grammar (contracts are grammar, not objects)
- Foundation §2.2 — affected section
- Patent §1.3 (describes the progression and implies the 4+2 model)
