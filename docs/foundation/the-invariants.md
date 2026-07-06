---
id: the-invariants
order: 3
title: "The Invariants"
status: drafting
authority: authoritative
depends_on: [the-problem]
governing_sources:
  - Foundation §9.2 (global execution invariants)
  - Foundation §2 (object ordering)
  - Foundation §4 (canonical evaluation)
  - Foundation §5 (governed state and version coexistence)
  - Foundation §6 (metric evaluation)
  - Foundation §8 (evidence and lineage)
governing_adrs:
  - DEC-97bb94 (N:1 Source Object to Canonical Object cardinality)
  - DEC-c4c742 (defines the governed selection artifact reserved under Invariant IV)
errata_referenced:
  - FND-ERR-004
v2_sources:
  - system/foundation/principles/execution-model.md §9
word_target: 3500
---

# The Invariants

## Scope

This chapter defines the six invariants that govern the execution model. The Problem described three failure classes and the constraints applied in response. This chapter formalizes those constraints as invariants and adds the conditions required for deterministic evaluation, referential stability, and preserved proof. It does not define each object type or each evaluation boundary exhaustively. Those definitions are provided in The Object Model through The Evaluation Boundaries.

## Role of invariants

An invariant is an operational rule encoded in the execution model. The model does not authorize behavior that violates an invariant. An implementation that permits such behavior is incorrect under the model.

Contracts are the governed mechanism through which these invariants are applied. The invariants do not replace contract governance and they are not a seventh contract family. They define the conditions that every contract-governed evaluation must satisfy.

The six invariants described below are the minimal set. Removing any one removes one or more platform guarantees defined in Foundation.

## Invariant summary

| Invariant | Operational rule | Primary failure prevented |
|---|---|---|
| Invariant I. Meaning is evaluated once | Business meaning is produced once per Canonical Object version at the canonical evaluation boundary. | Meaning drift |
| Invariant II. Object ordering is fixed | Authoritative objects are produced in a non-skippable sequence. | Order violation and hidden derivation |
| Invariant III. All state is immutable | Produced authoritative objects are never altered in place. | Historical rewrite |
| Invariant IV. All references are explicit | References identify object type, identity, and version. | Implicit reference |
| Invariant V. Evaluation is non-replayable | A boundary evaluation produces one object version per act. Re-evaluation yields a new version. | Replay-based audit |
| Invariant VI. Evidence is emitted, not inferred | Evidence and Lineage are emitted with the evaluation and preserved in the authoritative evidence chain. | Reconstruction of proof |

## Invariant I. Meaning is evaluated once

**Statement.** Business meaning is produced exactly once per Canonical Object version, at the canonical evaluation boundary, by applying a Canonical Contract to one or more Source Objects.

**Behavior.** Canonical evaluation reads Source Objects, applies the contract, resolves semantic state, and emits a Canonical Object together with its Evidence and Lineage. The evaluation is non-replayable (Invariant V) and the produced Canonical Object is immutable (Invariant III). No other operation produces, modifies, or reinterprets meaning. Reads, queries, and consumer access do not trigger evaluation.

**Consequence.** A Canonical Object version always expresses what it meant when produced. Changes in contract definition, participant consumption patterns, or platform version do not alter its meaning. Disputes about meaning are resolved by reading preserved state, not by reconstructing prior interpretation.

Cardinality. N Source Objects may feed one Canonical Object evaluation (FND-ERR-004, DEC-97bb94). Foundation's earlier linear framing is superseded by the N:1 pattern recorded in the Errata Ledger.

**Disallowed behaviors.**
- A consumer component produces meaning by querying raw Source Objects and inferring canonical values.
- A surface layer aliases a Canonical Object version to a different meaning based on presentation context.
- An operator re-evaluates a prior Canonical Object version under a newer contract and assigns the new meaning to the old version.
- A service emits a Canonical Object outside the canonical evaluation boundary.

**Governing source.** Foundation. Cardinality governed by DEC-97bb94 and FND-ERR-004.

## Invariant II. Object ordering is fixed

**Statement.** The platform produces four authoritative object types in a single non-skippable sequence: Source Object, Canonical Object, Metric Snapshot, and Action Object. Evidence Objects and Lineage Objects are emitted orthogonally at each evaluation boundary. They are not part of the authoritative object sequence.

**Behavior.** Each object type derives from objects of the preceding type in the sequence. A Canonical Object derives from one or more Source Objects. A Metric Snapshot derives from one or more Canonical Object versions. An Action Object derives from one or more Metric Snapshots. No object exists without its ordered predecessors, and no object derives from a successor.

**Consequence.** The ancestry of any authoritative object is deterministic and traceable. A Metric Snapshot can be resolved to the Canonical Object versions it evaluates. An Action Object can be resolved to the Metric Snapshots it references. Auditability and accountability depend on this ancestry remaining unbroken.

**Disallowed behaviors.**
- A reader emits a Canonical Object directly from external observation, bypassing the Source Object layer.
- A metric service admits a raw Source Object value into a Metric Snapshot, skipping canonical evaluation.
- An action binds to a Canonical Object version directly, bypassing the Metric Snapshot.
- A Canonical Object references a Metric Snapshot produced after it.
- A later-level object rewrites an earlier-level object in place.

**Governing source.** Foundation.

## Invariant III. All state is immutable

**Statement.** Once produced, an authoritative object is never altered. Corrections, adjustments, and reinterpretations are expressed only as new object versions. All versions coexist.

**Behavior.** An attempt to modify an existing Source Object, Canonical Object, Metric Snapshot, or Action Object is rejected. Producing a corrected value is permitted, but it yields a new version with a distinct identity and preserved provenance. The prior version remains addressable.

**Consequence.** Historical state is preserved indefinitely. Any reference to a past version resolves to the value the object had at production time. Disputes about past state are settled by reading preserved state, not by recomputation.

Version coexistence is a first-class property (Foundation). No version is considered overwritten, invalidated, or erased within the execution model. Supersession is a governance act described in The Authority Model. It changes future use. It does not modify the retired version or remove its history.

**Disallowed behaviors.**
- A service updates a Canonical Object in place to correct an admission-time error.
- A correction path overwrites an earlier Metric Snapshot.
- A silent deprecation marks a prior version as invalid and hides it from consumers.
- A consolidation collapses multiple versions into a single stored value.

**Governing source.** Foundation and §5.4.

## Invariant IV. All references are explicit

**Statement.** Every reference to an authoritative object identifies its type, its identity, and its version. Implicit references are forbidden.

**Behavior.** A participant reading an authoritative object names it precisely. A reference such as Canonical Object type X, identity Y, version Z is resolvable deterministically. A reference that does not identify version is rejected.

**Consequence.** A reference is deterministic. The referenced object is uniquely identified and cannot change meaning based on when or how the reference is resolved. Referential stability is preserved across contract evolution, platform upgrades, and access methods.

Reference handling is constrained as follows.

| Reference mode | Status | Behavior |
|---|---|---|
| Fixed binding | Permitted | The reference names a specific version. Resolution is deterministic and repeatable. |
| Governed selection artifact | Defined — see The Governed Selection | A governed selection is a declared, versioned rule that resolves, from the immutable object set, the object versions a reference names, recording the resolved set in Lineage. The artifact itself is versioned and the resolved set is recorded in Lineage. Defined in The Governed Selection (DEC-c4c742); resolving a single reference to a single version is the degenerate set-of-one case. |

**Disallowed behaviors.**
- Head-version semantics that resolve to whichever version is selected at read time.
- Time-based inference that resolves a version without a declared, governed rule.
- Query-driven selection that is not represented by a governed artifact.
- Alias-only reference that names the object identity without naming a version.

**Governing source.** Foundation and §5.5.

## Invariant V. Evaluation is non-replayable

**Statement.** Each evaluation boundary evaluates exactly once per object version it produces. Re-evaluation of the same inputs does not yield the same object version. It yields a new version.

**Behavior.** Each call to an evaluation boundary, admission, canonical, metric, or action, produces exactly one object version, emits its Evidence and Lineage, and closes. Subsequent evaluations against the same inputs are permitted, but they are distinct acts. They produce distinct object versions with their own Evidence and Lineage.

**Consequence.** Historical outcomes cannot be reconstructed by rerunning the platform. They can only be read from preserved state. Audit is a read operation. Audit is not a rerun operation.

**Corollary on reproducibility.** Reproducibility in BareCount means that a reader can observe what occurred at a prior evaluation by reading preserved objects and their evidence. It does not mean that the platform can be rerun to obtain identical state.

**Disallowed behaviors.**
- Re-evaluating a prior Canonical Object version under the same contract to produce an identical Canonical Object.
- Re-running a Metric Contract against a prior Canonical Object version to produce an identical Metric Snapshot.
- Replaying an Action Object outcome resolution to reassert the same outcome.
- Reconstructing historical state for audit by running evaluations against preserved copies of inputs.
- Treating a backfill of prior periods as equivalent to the original evaluation act.

**Governing source.** Foundation, §6.5, and §10.4.

## Invariant VI. Evidence is emitted, not inferred

**Statement.** At every evaluation boundary, the platform emits Evidence Objects and Lineage Objects that record what occurred, what was referenced, and under what conditions. These artifacts are immutable and append-only. They are never reconstructed, regenerated, or inferred from other state.

**Behavior.** Evidence and Lineage are emitted synchronously with the evaluation that produces the authoritative object. Evidence records the evaluation type, inputs, outputs, evaluation context, and outcome. Lineage records the direct reference relationships between objects. Both are preserved in the authoritative evidence chain and may be surfaced through different stores or retention tiers. Retention governs observability. It does not redefine truth.

**Consequence.** If no Evidence or Lineage artifact exists in the authoritative evidence chain for an evaluation, the platform treats that evaluation as not having occurred. Audit relies on preserved Evidence and Lineage. It does not infer missing proof from logs, surrounding state, or replayed computations.

Evidence does not influence meaning. Lineage does not compute dependency graphs. Both are descriptive records of what the platform did, not operational inputs to what the platform is doing.

**Disallowed behaviors.**
- Reconstructing lineage from application logs.
- Inferring evaluation context post hoc from surrounding state.
- Regenerating missing Evidence by replaying the evaluation that originally produced the authoritative object.
- Treating an absent Evidence record on the authoritative chain as a probably-successful evaluation.
- Allowing a consumer component to synthesize its own Lineage entries.

**Governing source.** Foundation.

## Interdependence

The six invariants are interdependent. Each prevents a distinct failure class. Removing any one reintroduces the class it addresses.

| Invariant removed | Effect |
|---|---|
| Invariant I | Meaning can be produced outside the canonical boundary. |
| Invariant II | Later components can bypass or invert the object sequence. |
| Invariant III | Historical state can be rewritten. |
| Invariant IV | Consumers can bind to unstable or inferred references. |
| Invariant V | Historical outcomes can be reconstructed by replay. |
| Invariant VI | Audit falls back to inferred proof rather than preserved proof. |

Each invariant also enables a distinct audit capability.

| Invariant | Audit capability enabled |
|---|---|
| Invariant I | Meaning audit |
| Invariant II | Ancestry audit |
| Invariant III | Preservation audit |
| Invariant IV | Reference audit |
| Invariant V | Non-replay audit |
| Invariant VI | Boundary audit |

the Operations chapters map these capabilities to external control frameworks.

## Testing a proposed behavior

Any proposed behavior is tested against the six invariants by applying the following checks.

| Check | Required condition | Failure condition |
|---|---|---|
| Meaning | Business meaning is produced only at the canonical evaluation boundary by applying a Canonical Contract. | The behavior produces, modifies, or reinterprets business meaning outside the canonical evaluation boundary. |
| Ordering | An authoritative object derives only from objects of the preceding type in the sequence. | The behavior skips a level, back-references a later level, or produces an authoritative object out of sequence. |
| Immutability | Corrections are expressed only as new object versions. | The behavior modifies an existing authoritative object in place. |
| Reference | Every reference identifies object type, identity, and version explicitly. | The behavior resolves an authoritative object through an implicit, inferred, or alias-only reference. |
| Replay | Re-evaluation, if permitted, produces a new version with its own Evidence and Lineage. | The behavior re-executes a prior evaluation to recreate an identical historical outcome. |
| Evidence | Evidence and Lineage are emitted synchronously with the evaluation and preserved on the authoritative evidence chain. | The behavior synthesizes Evidence after the fact, omits it from the authoritative chain, or infers proof from surrounding state. |

A behavior that passes all six checks is consistent with the execution model. A behavior that fails any one is incorrect under the execution model regardless of intent or utility.

## Chapter boundaries

This chapter states the invariants and their consequences. It does not define the objects (The Object Model), the contract grammar (The Contract Grammar), or the evaluation boundaries (The Evaluation Boundaries) in full. Where the invariants reference those artifacts, the treatment here is minimal and points to the chapter that defines them.

Parts II through V describe how runtime components, services, operational procedures, and compliance artifacts satisfy these six invariants. A component that cannot demonstrate satisfaction is either incorrect under the execution model or has not yet been fully described.

## References

- Foundation: Global Execution Invariants (primary source)
- Foundation: Object ordering (Invariant II)
- Foundation: Canonical evaluation (Invariant I)
- Foundation: Governed state, version coexistence, and referential stability (Invariants III and IV)
- Foundation: Metric evaluation discipline (Invariant V)
- Foundation: Evidence and Lineage emission (Invariant VI)
- Foundation: Platform guarantees that emerge from the invariants
- FND-ERR-004: N:1 Source Object to Canonical Object cardinality (Errata)
- DEC-97bb94: N:1 canonical evaluation (Decisions, upon migration)
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- Evidence and Lineage: Evidence and Lineage
