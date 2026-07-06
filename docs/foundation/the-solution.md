---
id: the-solution
order: 2
title: "The Solution"
status: drafting
authority: authoritative
depends_on: [the-problem]
governing_sources:
  - Patent Abstract
  - Patent §1 Technical Field and System Overview
  - Patent §2 Problem Statement and Limitations of Existing Systems
  - Foundation (scope and non-negotiability)
governing_adrs:
  - DEC-97bb94 (N:1 Source Object to Canonical Object cardinality)
errata_referenced:
  - FND-ERR-004
v2_sources:
  - system/foundation/patent/sections/intro.md
  - system/foundation/patent/sections/section-01.md
  - system/foundation/patent/sections/section-02.md
word_target: 1800
---

# The Solution

## Scope

This chapter names the platform's response to the three failure classes identified in The Problem and describes the structural moves that prevent each class. It introduces the architectural posture before the formal definitions land. It does not enumerate the invariants, the object model, the contract grammar, the evaluation boundaries, or the authority ladder in full. Those definitions are provided in The Invariants through The Authority Model. The reader leaves with a sentence-level account of how meaning is fixed, how proof is preserved, and how reference is bound, together with a roadmap to the Foundation chapters that formalize each move.

## Summary

The platform applies one structural response to each failure class. Each response is realized at a single boundary in the execution model, governed by an authoritative artifact, and bound to the same act that produces authoritative state.

| Failure class | Response | Operational effect | Where formalized |
|---|---|---|---|
| Meaning drift after observation | Business meaning is produced once, at the canonical evaluation boundary, by applying a Canonical Contract to one or more Source Objects. | Consumers read preserved semantic state. No component reinterprets meaning at read time. | The Invariants; The Object Model; The Evaluation Boundaries |
| Reconstruction-based audit | Evidence and Lineage are emitted at the same evaluation act that produces authoritative state, and are preserved indefinitely. | Audit reads preserved proof. The platform does not assemble historical answers from logs and replays. | The Invariants; The Evaluation Boundaries |
| Implicit reference | Every reference identifies object type, identity, and version. Resolutions such as head-version-at-read are not admitted. | Two consumers issuing nominally identical requests receive the same value. Decisions are traceable to specific historical state. | The Invariants; The Object Model |

The three responses are interdependent. Each prevents one failure class. None is sufficient on its own.

## Meaning is produced at one boundary

The platform admits external state through the admission boundary, which produces Source Objects. Source Objects carry observed values. They do not carry business meaning. Business meaning is produced by canonical evaluation: a separate, governed act that reads one or more Source Objects, applies a Canonical Contract, and emits a Canonical Object together with its proof.

Two properties of canonical evaluation address meaning drift directly.

The first is exclusivity. Business meaning is produced at the canonical evaluation boundary and at no other operation. Read access does not produce or modify meaning. Query operations do not produce or modify meaning. Surface and consumer components do not produce or modify meaning. A consumer that needs the meaning of an observed value reads the Canonical Object that already carries it.

The second is determinism. A Canonical Object version expresses what it meant when produced. Subsequent contract revisions do not alter prior versions. Subsequent consumption patterns do not alter prior versions. A request for a Canonical Object identified by version returns the value the platform produced at that version, with the meaning the contract assigned at that act.

These two properties together remove the conditions that produce meaning drift. Meaning has one author, expressed once, preserved as state. Disputes about meaning are resolved by reading preserved state, not by reconstructing prior interpretation.

The Invariants formalizes the singularity of canonical evaluation. The Object Model defines Source Objects, Canonical Objects, and the cardinality between them. The Evaluation Boundaries describes admission and canonical evaluation as separate non-skippable boundaries. The Contract Grammar defines the Canonical Contract and its supporting Canonical Mapping schema.

**Governing source.** Foundation. Cardinality governed by DEC-97bb94 and FND-ERR-004.

## Proof is emitted at the act that produces state

The platform emits Evidence and Lineage at every evaluation boundary as part of the act that produces an authoritative object. Evidence records per-record outcomes, including admitted, rejected, warned, and logged outcomes. Lineage records the references that bind the produced object to its predecessors. Both are immutable and append-only, preserved in a tenant-scoped evidence chain.

The synchronous emission of proof is the move that addresses reconstruction-based audit. Reconstruction is required when proof is missing. When proof is preserved at production time, audit reads the preserved record and does not need to replay the original act. Inputs may change. Logic may change. Configuration may change. The preserved Evidence and Lineage describe the act as it was performed; they do not depend on later state to be reread.

Two properties matter. The first is co-emission. Evidence and Lineage are not produced as a separate operation at a later time. They are produced at the same act, by the same boundary, governed by the same contract version. A boundary act that does not emit its proof is not authorized. The second is immutability. Once emitted, an Evidence Object or Lineage Object is never altered. Corrections are recorded as new entries in the chain. The historical record is preserved indefinitely.

The Invariants formalizes proof emission as a condition every governed evaluation must satisfy. The Evaluation Boundaries describes the four boundaries at which proof is emitted. Evidence and Lineage in Operating Model describes the proof object types and the chain that preserves them.

**Governing source.** Foundation.

## Reference identifies a specific version

The platform admits no implicit reference. Every reference to an authoritative object identifies the object's type, its identity, and its version. A reference to "the customer balance" without a version is not admitted. A reference to "the most recent version" is not admitted. A reference to "current state" without an explicit version is not admitted.

Explicit reference is the move that addresses the failure class at its most subtle point. Two systems can preserve identical state and still produce divergent answers if their consumers resolve references at read time to whichever version each system treats as current. Stable historical answers require stable references.

Two properties extend this constraint to historical state. The first is immutability of authoritative objects. Once produced, an authoritative object is never altered in place. A correction is a new version with a distinct identity. The prior version remains addressable. The second is version coexistence. No version is considered overwritten, invalidated, or erased within the execution model. Supersession is a governance act. It changes which version subsequent acts use; it does not modify the retired version or remove it from the addressable history.

A reference, once written, resolves to the same value indefinitely. Decisions recorded against an explicit reference are traceable to the state on which they were made.

The Invariants formalizes immutability and explicit reference as conditions every governed evaluation must satisfy. The Object Model defines version identity and coexistence. The Authority Model describes supersession as a governance act and the Errata Ledger as the governed mechanism for recording adopted contradictions.

**Governing source.** Foundation.

## The integrated solution

BareCount evaluates business meaning once at the canonical evaluation boundary, emits Evidence and Lineage at the same act that produces authoritative state, and admits no reference that does not identify the version it touches. The remaining Foundation chapters formalize each move, define the artifacts and boundaries on which it depends, and describe the authority model that governs change.

**Governing source.** Foundation.

## Foundation roadmap

The remaining Foundation chapters formalize the responses described above. Each chapter is named below with the aspect of the solution it formalizes.

| Chapter | Aspect formalized |
|---|---|
| The Invariants | Six invariants encode the responses as conditions every governed evaluation must satisfy. The set is interdependent. |
| The Object Model | Four authoritative progression objects, two orthogonal proof objects, and the boundary sequence that orders their production. |
| The Contract Grammar | The governed grammar artifacts (contract families, supporting schema, primitives) that govern evaluation acts. |
| The Evaluation Boundaries | The four boundaries at which authoritative state is produced and the rule that read access never triggers evaluation. |
| The Authority Model | The three-rung authority ladder, the Errata Ledger mechanism, and the rule that no silent override is permitted. |

Each chapter assumes the responses described in this chapter and adds the operational definitions on which they depend.

## References

- Patent Abstract
- Patent §1: Technical Field and System Overview
- Patent §2: Problem Statement and Limitations of Existing Systems
- Foundation: Scope and Non-Negotiability
- The Problem: The Problem
- The Invariants: The Invariants
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- The Authority Model: The Authority Model
- Errata: Errata Ledger
