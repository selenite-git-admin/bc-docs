---
id: FND-ERR-006
title: "Evaluation boundary count: four, not five"
status: adopted
authority: authoritative
affected: Foundation §2.3 and Foundation evaluation-boundaries.md
temporary_governance:
  - Chapter 2 (The Invariants)
  - Chapter 3 (The Object Model)
  - Chapter 5 (The Evaluation Boundaries)
target_resolution: Foundation v2 evaluation boundary count aligned to four
opened: 2026-04-24
---

# FND-ERR-006 — Evaluation boundary count: four, not five

## Contradiction summary

Foundation contains two readings of the evaluation-boundary count.

- Foundation `execution-model.md` §2.3 lists four evaluation boundaries: admission, canonical, metric, action.
- Foundation `evaluation-boundaries.md` describes five boundaries by naming an Observation Boundary (preservation of raw source state) as distinct from the Admission Boundary (validation).

Ch 2 (Invariant II object ordering), Ch 3 (four progression objects produced at four boundaries), and Ch 5 (four boundaries defined per this chapter) all commit to four boundaries.

## Implementation behavior

The platform treats observation of external state as the input to the admission boundary, not as a distinct authoritative-producing boundary. No "Observed Record" authoritative object exists. The first authoritative progression object emitted is the Source Object, and it is produced at the admission boundary.

The Reader that performs external observation is a runtime component that prepares inputs for the admission boundary. Its internal operation (connecting to the source, reading records, applying governed field selection via the Observation Contract) is not a distinct authoritative-producing boundary. The governed act that produces authoritative state is the admission boundary act, which emits the Source Object along with Evidence and Lineage.

## Temporary governance

Chapters 2, 3, and 5 of v3 are the authoritative source for the boundary count and taxonomy. All three chapters hold the four-boundary reading. Foundation `evaluation-boundaries.md` is superseded by the v3 chapters on this specific count.

## Resolution state

**Adopted.** The four-boundary reading is correct. Foundation v2 will be revised to state the boundary count explicitly as four and to remove the separate Observation Boundary entry. This erratum closes when Foundation v2 publishes the revised boundary list.

## References

- Chapter 2 §2.4 (Invariant II object ordering)
- Chapter 3 §3.1 (object inventory, four progression objects)
- Chapter 3 §3.5 (object-boundary mapping, four rows)
- Chapter 5 §5.1 (boundary inventory, four rows)
- Chapter 5 §5.3 through §5.6 (per-boundary sections)
- Foundation `execution-model.md` §2.3 (four-boundary list, correct)
- Foundation `evaluation-boundaries.md` (five-boundary list, superseded on this count)
