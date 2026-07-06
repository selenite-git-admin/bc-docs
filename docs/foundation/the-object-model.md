---
id: the-object-model
order: 4
title: "The Object Model"
status: drafting
authority: authoritative
depends_on: [the-invariants]
governing_sources:
  - Foundation §2 (object ordering)
  - Foundation §4 (canonical evaluation)
  - Foundation §8 (evidence and lineage)
  - Patent §1.3 (contract-governed execution)
governing_adrs:
  - DEC-0e3c64 (Observation Contract)
  - DEC-136a23 (Reader Observation Schema)
  - DEC-97bb94 (N:1 Source Object to Canonical Object cardinality)
  - DEC-02f5a9 (Business Concept Registry — supersedes the BF/BO/CF vocabulary model)
errata_referenced:
  - FND-ERR-003
  - FND-ERR-004
  - FND-ERR-005
v2_sources:
  - system/foundation/principles/data-object-model.md
  - system/foundation/principles/execution-model.md §2
diagrams:
  - DG-object-model
word_target: 4000
---

# The Object Model

## Scope

This chapter defines the authoritative object types produced by the platform and the sequence in which they are produced. It distinguishes four progression objects (Source Object, Canonical Object, Metric Snapshot, and Action Object) from two orthogonal proof objects (Evidence Object and Lineage Object). It describes the role, identity, cardinality, lifecycle, and consumption discipline of each object type. It does not define contract grammar (The Contract Grammar), evaluation boundary semantics (The Evaluation Boundaries), governance and supersession policy (The Authority Model), or runtime component implementations (Sources and the Catalog through Chain Completeness and Verdict).

![Object Model · four progression objects (SO, CO, Metric Snapshot, AO) and two proof objects (Evidence, Lineage), with governing contracts and store locations per object.](/docs/assets/diagrams/DG-object-model.svg)

## Object inventory

The platform produces six authoritative object types. Four form a non-skippable progression. Two preserve proof records at every evaluation boundary.

| Object | Role | Produced by boundary | Cardinality relative to predecessor |
|---|---|---|---|
| Source Object (SO) | Preserved observation of external state | Admission | N per admitted observation batch |
| Canonical Object (CO) | Business-meaningful state derived from one or more SOs | Canonical | N:1 (N SOs feed one CO version) |
| Metric Snapshot | Numeric assertion over one or more CO versions | Metric | N:1 (N CO versions feed one snapshot) |
| Action Object (AO) | Declared intent bound to one or more Metric Snapshots | Action | N:1 (N snapshots feed one AO) |
| Evidence Object (EV) | Record of what occurred at an evaluation boundary | Any boundary | One or more per boundary act |
| Lineage Object (LO) | Record of reference relationships established at an evaluation boundary | Any boundary | One or more per boundary act |

Progression objects carry semantic state and control outputs. Proof objects carry boundary occurrence and direct references. The object model separates these responsibilities.

| Audit objective | Object class read | Result |
|---|---|---|
| Determine what state was recorded | Progression objects | The reader resolves preserved semantic state and its ordered predecessors. |
| Determine what boundary act occurred | Evidence Objects | The reader resolves boundary type, context, outcome, and timestamp. |
| Determine what the boundary act referenced | Lineage Objects | The reader resolves direct references between produced and consumed objects. |

Invariant II (the Invariant II. Object ordering is fixed section of The Invariants) governs progression order. Invariant VI (the Invariant VI. Evidence is emitted, not inferred section of The Invariants) governs proof emission. Invariant III (the Invariant III. All state is immutable section of The Invariants) applies to all six object types; all six are immutable once produced.

## Authoritative progression objects

### Source Object

**Statement.** A Source Object is an immutable record of external state from a named source system at a specific point in time. Source Objects are the only authoritative objects that directly reference external systems.

**Behavior.** The admission boundary applies governed admission and observation definitions to external state and emits one Source Object per admitted observation. The Source Object preserves the observed payload as received, captures source-specific structure, and records the observation context required for later interpretation. Consumer components may read Source Objects as inputs to canonical evaluation. They do not modify them.

**Identity.** Each Source Object is identified by source system identifier, source object type, source business keys, and observation timestamp. Identity is preserved permanently.

**Cardinality.** An admission boundary act admits one batch of external state and emits one Source Object per admitted observation in the batch. Rejected observations emit Evidence but do not emit Source Objects.

**Lifecycle.** Source Objects are append-only. They are never updated, merged, reinterpreted, or reclassified. A correction in the source system is admitted as a new observation with a later timestamp. The earlier observation remains in preserved state unchanged.

**Provenance metadata.** Each Source Object records the metadata required to locate and interpret its observation. This includes source system identifier, source table or API, extraction method (batch, event, or polled snapshot), extraction timestamp, source entity scope, and the boundary context recorded at admission. Provenance is stored with the object and does not rely on external logs for preservation.

**Disallowed behaviors.**
- A component admits external state outside the admission boundary.
- A service updates a Source Object in place to reflect a change in the source system.
- A consumer infers canonical meaning from a Source Object without canonical evaluation.
- An admission act omits Evidence emission for a rejected observation.
- A Source Object is produced without recording its observation timestamp.

**Governing source.** Foundation (semantic admission); Foundation (admission inputs to canonical evaluation); DEC-0e3c64 and DEC-136a23 for Observation Contract and Reader Observation Schema.

### Canonical Object

**Statement.** A Canonical Object represents business-meaningful state derived from one or more Source Objects by applying a Canonical Contract at the canonical evaluation boundary. Canonical Objects are the authoritative objects that carry business meaning.

**Behavior.** Canonical evaluation reads Source Objects, applies the Canonical Contract (The Contract Grammar), resolves semantic state, and emits a Canonical Object together with its Evidence and Lineage. The evaluation is non-replayable (Invariant V) and the Canonical Object is immutable (Invariant III). Reads, queries, and consumer access do not trigger evaluation. Contract changes do not alter prior Canonical Object versions.

**Identity.** Each Canonical Object is identified by canonical object type, business identity keys, contract version, and evaluation timestamp. Identity is deterministic from the recorded inputs and the governed contract version.

**Cardinality.** One Canonical Object version is produced per canonical evaluation act. A single evaluation act may read N Source Objects of the same or different types. This N:1 cardinality (FND-ERR-004, DEC-97bb94) supersedes Foundation's earlier linear framing. Multiple Canonical Object versions coexist across time; no version invalidates another.

**Lifecycle.** Canonical Objects are append-only and version-coexistent. Corrections are expressed as new versions with distinct identity and preserved provenance. Supersession is a governance act (The Authority Model) that changes future use. It does not modify or remove the superseded version.

**Field mapping.** Each Canonical Contract declares a field mapping from Source Object payloads to canonical Business Concepts. Under DEC-02f5a9 (Business Concept Registry) the Canonical Mapping *identity* layer is eliminated: the Canonical Contract binds Business Concepts directly. Until the greenfield cutover (DEC-02f5a9 §6), Canonical Mapping persists physically and each Canonical Object version records the Canonical Mapping version applied; mapping changes produce new Canonical Object versions going forward and do not alter prior versions.

**Disallowed behaviors.**
- A service emits a Canonical Object outside the canonical evaluation boundary.
- A consumer fabricates a Canonical Object from raw Source Object payloads by inference.
- An operator re-evaluates a prior Canonical Object version under a newer contract and assigns the new meaning to the old version.
- A component modifies a Canonical Object to correct an admission-time error in its inputs.
- A Canonical Object is produced without recording the contract versions that produced its fields.

**Governing source.** Foundation (canonical evaluation); FND-ERR-004 and DEC-97bb94 for N:1 cardinality.

### Metric Snapshot

**Statement.** A Metric Snapshot represents a numeric assertion over one or more Canonical Object versions, produced by applying a Metric Contract at the metric evaluation boundary.

**Behavior.** Metric evaluation references one or more Canonical Object versions, applies the Metric Contract (Metric Evaluation), computes the numeric value, and emits a Metric Snapshot together with its Evidence and Lineage. The snapshot captures the resolved value, the referenced Canonical Object versions, the contract version, and the evaluation context. Dashboards, queries, and consumer reads do not trigger metric evaluation.

**Identity.** Each Metric Snapshot is identified by metric identity, contract version, referenced Canonical Object versions, and evaluation timestamp.

**Cardinality.** One snapshot is produced per evaluation act. A single evaluation may reference N Canonical Object versions across one or more canonical contracts. This N:1 cardinality (FND-ERR-003) supersedes Foundation's earlier linear framing, which implied one Metric Snapshot per one Canonical Object.

**Lifecycle.** Metric Snapshots are append-only. They are never rewritten, recomputed in place, or replaced. A later evaluation over the same period, the same referenced objects, or preserved historical inputs is permitted only as a distinct metric evaluation act. That act produces a new Metric Snapshot version with its own Evidence and Lineage. It does not recreate or replace the earlier snapshot.

**Primary and secondary snapshots.** A Metric Snapshot is primary when its Lineage references only Canonical Objects. A Metric Snapshot is secondary when its Lineage references at least one other Metric Snapshot in addition to Canonical Objects. Secondary snapshots form a directed acyclic graph of metric dependencies. The graph is descriptive only. Traversal reads preserved Lineage; it does not trigger recomputation of any snapshot in the chain.

**Disallowed behaviors.**
- A consumer reconstructs a Metric Snapshot value by querying Canonical Objects directly.
- A service rewrites a Metric Snapshot to correct a value.
- A component references a Metric Snapshot without naming its version.
- A metric evaluation act omits Lineage to its input Canonical Object versions.
- A secondary Metric Snapshot is produced without Lineage to the other snapshots it references.

**Governing source.** Foundation (metric evaluation); FND-ERR-003 for N:1 Metric Contract to Canonical Contract cardinality.

### Action Object

**Statement.** An Action Object represents a declared intent bound at creation time to one or more Metric Snapshots. It records what was decided, on what basis, and with what outcome.

**Behavior.** Action evaluation references one or more Metric Snapshots, applies an Intervention Contract (Action Evaluation), records the declared intent, resolves outcome conditions, and emits an Action Object together with its Evidence and Lineage. Outcome resolution compares declared conditions against preserved snapshots. It does not re-evaluate metric logic or reference newer state.

**Identity.** Each Action Object is identified by action definition identity, contract version, referenced Metric Snapshot versions, baseline binding timestamp, and outcome resolution timestamp.

**Cardinality.** One Action Object is produced per action evaluation act. The action references N Metric Snapshots at creation time. These references are immutable for the life of the Action Object.

**Lifecycle.** Action Objects progress to a terminal state. The platform prohibits open-ended, indefinitely pending, or retroactively closed actions. If closure conditions are not met by the declared threshold, the Action Object records non-closure explicitly.

**Disallowed behaviors.**
- A service rebinds an Action Object to newer Metric Snapshots after creation.
- An outcome is reassigned by reading updated metric state.
- An operational workflow outside the platform modifies or replaces an Action Object.
- An Action Object is closed by collapsing it into a later Action Object.

**Governing source.** Foundation (action binding and outcome resolution).

## Orthogonal proof objects

Evidence Objects and Lineage Objects are emitted at every evaluation boundary. They are authoritative proof objects, not progression objects. They do not carry business meaning and they do not participate in progression ordering. Their absence does not change the semantic value already recorded in progression objects, but it removes authoritative proof of the boundary act. Under Invariant VI, an evaluation without preserved Evidence and Lineage on the authoritative evidence chain is not treated as an authoritatively proved boundary act for audit.

### Evidence Object

**Statement.** An Evidence Object records that an evaluation or binding occurred, what was referenced, under what conditions, and with what outcome. Evidence is emitted synchronously with the evaluation that produces the authoritative object.

**Behavior.** At every evaluation boundary the platform emits at least one Evidence Object. The record captures evaluation type, inputs, outputs, evaluation context, outcome, and timestamp. Evidence is immutable and append-only. Evidence describes the boundary act. It does not influence later evaluation.

**Emission boundaries.** Evidence is emitted at Source Object admission, including rejected admissions, Canonical Object evaluation, Metric Snapshot materialization, Action Object creation, and Action outcome resolution. Evidence is not emitted during read access, query execution, visualization, or consumer consumption.

**Consequence.** If no Evidence Object exists on the authoritative evidence chain for a boundary act, the platform does not treat that boundary act as authoritatively proved. Audit does not reconstruct missing Evidence from logs, surrounding state, or replayed operations.

**Disallowed behaviors.**
- A consumer component synthesizes an Evidence Object post hoc from application logs.
- A service modifies an Evidence Object to correct a recorded context.
- An evaluation boundary act omits Evidence because the produced authoritative object is considered trivial.
- A retention policy removes Evidence from the authoritative evidence chain while continuing to represent the boundary act as authoritatively auditable.

**Governing source.** Foundation and §8.4.

### Lineage Object

**Statement.** A Lineage Object records an explicit reference relationship between authoritative objects. It identifies what referenced what, and when.

**Behavior.** Lineage is emitted at every evaluation or binding act. It records the direct relationships between produced and referenced objects: Canonical Objects evaluated from Source Objects, Metric Snapshots evaluated from Canonical Object versions, Action Objects bound to Metric Snapshots, and cross-references between Evidence and the objects it documents. Lineage is immutable and append-only.

**Scope.** Lineage records direct relationships only. It does not compute transitive dependency graphs. The platform does not traverse Lineage to infer causality or trigger further evaluation.

**Consequence.** Lineage enables ancestry audit (the Interdependence section of The Invariants). A reader traces any authoritative object to its direct inputs by reading preserved Lineage. Deeper traversal is constructed from direct edges; the platform does not infer missing links.

**Disallowed behaviors.**
- A consumer synthesizes Lineage entries to represent references inferred from context.
- A service rebuilds Lineage from application logs after a gap.
- Lineage is modified to reflect a correction in the referenced object.
- Lineage emission is deferred past the boundary act that produced the referenced object.

**Governing source.** Foundation and §8.6.

### The proof chain

Evidence and Lineage together form the proof chain for each authoritative object.

| Proof requirement | Object used | Result |
|---|---|---|
| Demonstrate that a boundary act occurred | Evidence Object | Boundary type, context, outcome, and timestamp are preserved. |
| Demonstrate what the boundary act referenced | Lineage Object | Direct references between produced and consumed objects are preserved. |
| Demonstrate both occurrence and ancestry | Evidence Object and Lineage Object | The boundary act is auditable without replay, recomputation, or inference. |

The proof chain is preserved on the authoritative evidence chain, a storage concept defined in Evidence and Lineage. Audit reads the preserved proof chain. Audit does not replay the evaluation, re-evaluate inputs, or infer missing steps. Invariant VI therefore constrains audit to preserved proof rather than reconstruction.

## Contracts are grammar, not objects

Foundation includes terms that require clarification because they can be misread as adding object types beyond the authoritative set defined in this chapter. The `FND-ERR-005` entry records the clarification.

Under the canonical reading:

- Contracts are grammar, not objects. A Canonical Contract, Metric Contract, or Intervention Contract is a versioned, governed definition of how a boundary evaluation is performed. It is defined, versioned, and referenced, but it is not one of the six authoritative object types. Contracts are defined in The Contract Grammar.
- An "Evaluation Object" mentioned in Foundation resolves either to the authoritative object produced at the boundary, a Canonical Object, Metric Snapshot, or Action Object, or to the evaluation act itself, which is a boundary operation rather than an object. Neither reading adds a distinct authoritative object type.

The following table distinguishes authoritative objects from adjacent constructs that appear in diagrams, grammar definitions, or prior Foundation drafts.

| Construct | Category | Counted as authoritative object |
|---|---|---|
| Source Object | Authoritative object (progression) | Yes |
| Canonical Object | Authoritative object (progression) | Yes |
| Metric Snapshot | Authoritative object (progression) | Yes |
| Action Object | Authoritative object (progression) | Yes |
| Evidence Object | Authoritative object (proof) | Yes |
| Lineage Object | Authoritative object (proof) | Yes |
| Source Contract, Admission Contract, Observation Contract, Canonical Contract, Metric Contract, Intervention Contract | Grammar | No |
| Canonical Mapping | Supporting grammar schema (superseded — DEC-02f5a9) | No |
| Business Concept Registry — Entity, Property, Business Concept (supersedes Business Object / Business Field / Canonical Field — DEC-02f5a9) | Grammar vocabulary | No |
| Contract Binding (tenant-scoped) | Grammar instance | No |
| Evaluation act | Boundary operation | No |
| Activity Log entry | Operational record | No |

The authoritative object count is therefore six: four progression objects and two orthogonal proof objects. Contracts, evaluation acts, contract bindings, and similar grammar and execution constructs are referenced throughout the documentation but are not counted as authoritative objects for the purposes of Invariants II, III, IV, V, and VI.

## Object-boundary mapping

Each progression object is produced at exactly one evaluation boundary. Evidence and Lineage are emitted at every boundary.

| Boundary | Progression object produced | Proof objects emitted |
|---|---|---|
| Admission | Source Object | Evidence, Lineage |
| Canonical | Canonical Object | Evidence, Lineage |
| Metric | Metric Snapshot | Evidence, Lineage |
| Action | Action Object | Evidence, Lineage |

The Evaluation Boundaries defines each boundary in full, including its contract governance, inputs, outputs, and the invariants it preserves.

## Consumption discipline

Consumer components, including surface layers, operational tooling, reporting, and external integrations, interact with the object model under the following discipline.

| Consumer action | Permitted on | Not permitted on |
|---|---|---|
| Read | All six object types | No restriction beyond access scope |
| Reference (by type, identity, version) | All six object types | Any reference that omits the version or resolves implicitly |
| Display | Progression objects as their recorded values; proof objects as preserved evidence records | Displaying a "current" value without naming the version |
| Export | Progression objects; proof objects, subject to retention policy and access scope | Exporting a derived value as if it were an authoritative object |
| Trigger evaluation | Not applicable; reads do not trigger evaluation | Any read path that causes a new authoritative object to be produced |

Consumer actions are descriptive and read-only with respect to authoritative state. A consumer component that needs to produce a new Canonical Object, Metric Snapshot, or Action Object does so through the governed boundary for that object type, not through a consumption surface.

## Chapter boundaries

This chapter has defined the six authoritative object types, their cardinality, their lifecycle, the proof chain that accompanies them, and the consumption discipline applied to them. It has deferred:

- Contract grammar and the 12-artifact taxonomy (The Contract Grammar).
- Evaluation boundary semantics and the once-only guarantee at each boundary (The Evaluation Boundaries).
- The authority model and how objects relate to the governance ladder (The Authority Model).
- Runtime component descriptions for Readers, Canonical evaluators, Metric evaluators, and Action processors (Sources and the Catalog through Action Evaluation).
- Evidence and Lineage service implementation (Evidence and Lineage).

## References

- Foundation: Object ordering and types
- Foundation: Semantic admission and Source Object emission
- Foundation: Canonical evaluation and Canonical Object production
- Foundation: Metric evaluation and Metric Snapshot production
- Foundation: Action binding and Action Object production
- Foundation: Evidence and Lineage emission
- Patent §1.3: Contract-governed execution
- FND-ERR-003: N:1 Metric Snapshot cardinality clarification (Errata)
- FND-ERR-004: N:1 Source Object to Canonical Object cardinality (Errata)
- FND-ERR-005: Object count clarification (Errata)
- DEC-0e3c64: Observation Contract (Decisions, upon migration)
- DEC-136a23: Reader Observation Schema (Decisions, upon migration)
- DEC-97bb94: N:1 canonical evaluation (Decisions, upon migration)
- DEC-02f5a9: Business Concept Registry — supersedes the BF/BO/CF vocabulary model (Decisions)
- The Invariants: The Invariants
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- Action Evaluation: Intervention and Action
- Evidence and Lineage: Evidence and Lineage
