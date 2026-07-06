---
id: the-evaluation-boundaries
order: 6
title: "The Evaluation Boundaries"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar]
governing_sources:
  - Foundation §2.3 (evaluation boundaries)
  - Foundation §§3-7 (per-boundary specifications)
  - Foundation §8 (evidence and lineage at boundaries)
governing_adrs:
  - DEC-97bb94 (N:1 Source Object to Canonical Object cardinality)
  - DEC-29c324 (N:1 Metric Contract to Canonical Contract cardinality)
  - DEC-02f5a9 (Business Concept Registry — supersedes the BF/BO/CF vocabulary model)
errata_referenced:
  - FND-ERR-003
  - FND-ERR-004
  - FND-ERR-006
v2_sources:
  - system/foundation/principles/evaluation-boundaries.md
  - system/foundation/principles/execution-model.md §§2-7
diagrams:
  - DG-evaluation-boundaries
---

# The Evaluation Boundaries

## Scope

This chapter defines the four evaluation boundaries at which the platform produces authoritative state. It names each boundary, its governing contract family, its inputs, its produced progression object, and the proof artifacts emitted alongside. It states the rules that apply uniformly at every boundary: once-only evaluation, synchronous proof emission, non-replayability, and the rule that read access does not trigger evaluation. Per-boundary runtime behavior, the Readers and services that perform evaluation, is described in Sources and the Catalog through Action Evaluation.

![The Four Evaluation Boundaries · Admission, Canonical, Metric, and Action. Each boundary applies one or more governed contracts to admitted inputs, emits one progression object class, and emits Evidence and Lineage at the same act.](/docs/assets/diagrams/DG-evaluation-boundaries.svg)

## Boundary inventory

The platform produces authoritative state at exactly four evaluation boundaries. Each boundary produces one class of progression object and emits Evidence and Lineage alongside. No other operation produces authoritative state.

| Boundary | Primary inputs | Progression output | Governed artifacts applied | Proof emitted |
|---|---|---|---|---|
| Admission | Observed external state | Source Object | Source Contract as structural reference; Admission Contract; Observation Contract | Evidence, Lineage |
| Canonical | One or more Source Objects | Canonical Object | Canonical Contract; Canonical Mapping (superseded — DEC-02f5a9; persists until cutover, see the Canonical evaluation boundary note) | Evidence, Lineage |
| Metric | One or more Canonical Object versions; any governed upstream Metric Snapshot references for secondary evaluation | Metric Snapshot | Metric Contract | Evidence, Lineage |
| Action | One or more Metric Snapshots | Action Object | Intervention Contract | Evidence, Lineage |

The boundary ordering is fixed by Invariant II (the Invariant II. Object ordering is fixed section of The Invariants). No boundary receives input from a later boundary, and no boundary produces output that skips a level.

The `FND-ERR-006` entry records a Foundation inconsistency on boundary count. Foundation `evaluation-boundaries.md` names five boundaries by treating observation preservation as a distinct boundary before admission. Foundation `execution-model.md` the Invariant I. Meaning is evaluated once section of The Invariants names four. This chapter holds the four-boundary reading. Observation of external state is the input to the admission boundary, not a separate authoritative-producing boundary.

## Boundary-independent rules

Six rules apply at every evaluation boundary. They are consequences of the invariants in The Invariants applied to boundary operation.

| Rule | Statement | Invariant source |
|---|---|---|
| Upstream-only input | A boundary act reads only declared upstream state and the governed artifacts permitted for that boundary. | Invariants II and IV |
| Boundary-specific output | A boundary act produces only its own progression object type. It does not emit a later-sequence progression object. | Invariant II |
| Once-only evaluation | A boundary act produces exactly one progression-object version. The same inputs evaluated at a later boundary act produce a new version, not the same version. | Invariant V |
| Synchronous proof emission | Evidence and Lineage are emitted in the same boundary act that produces the progression object. Proof is not written after the fact. | Invariant VI |
| Reads do not trigger evaluation | Reading a progression object, a Canonical Mapping, or a Contract does not cause a boundary act. Evaluation is explicitly invoked, not implicit in access. | Invariants I and V |
| Non-replayability | A boundary act is not re-executable. Rerunning with the same inputs produces a distinct new object version with its own proof, not a recreation of an earlier object. | Invariant V |

These rules are invariant-grade. A boundary implementation that relaxes any of them is incorrect under the execution model.

## Admission boundary

**Purpose.** The admission boundary admits observed external state into the platform as Source Objects. It applies structural validation and field selection before any authoritative Source Object is emitted.

**Contract governance.** Two contract families govern this boundary. The Admission Contract declares validation rules (required fields, nullability, identity semantics, temporal discipline, rejection versus warning policy). The Observation Contract declares field selection from the Source Contract structure to the business vocabulary preserved on the Source Object. Both contracts are resolved by reference; the boundary act does not author contracts.

**Inputs.** Observed external state from a named source system. The Source Contract referenced by the Admission Contract describes the structural shape the observation must satisfy.

**Outputs.** For each admitted observation, the boundary emits one Source Object together with its Evidence and Lineage. Rejected observations emit Evidence recording the rejection reason and do not emit Source Objects.

**Once-only guarantee.** Admitting the same observed state at two different admission acts produces two distinct Source Objects, each with its own observation timestamp and proof. The boundary does not coalesce repeated admissions.

**Disallowed behaviors.**
- External state is emitted as a Source Object outside the admission boundary.
- An Admission Contract validates state under a newer version after the original admission act.
- Rejected observations do not emit Evidence.
- A Source Object is produced without a referenced Admission Contract version and Observation Contract version.

**Governing source.** Foundation; the Admission Contract section of The Contract Grammar and the Observation Contract section of The Contract Grammar.

## Canonical evaluation boundary

**Purpose.** The canonical evaluation boundary produces business-meaningful Canonical Object versions from one or more Source Objects. It resolves semantic state.

**Contract governance.** The Canonical Contract governs the boundary. The Canonical Contract references a Business Object, declares the grain, declares the field selection and resolution rules across multiple Source Objects, declares the resolved output schema, and declares the temporal gate that controls evaluation timing. The Canonical Mapping governs the field-level binding from Business Fields on the Source side to Canonical Fields on the Canonical side.

> **DEC-02f5a9.** The Business Concept Registry supersedes the Business Object / Business Field / Canonical Field vocabulary model: the Canonical Contract references an Entity and binds Business Concepts directly, and the Canonical Mapping identity layer is eliminated. The four evaluation boundaries and their once-only semantics are unchanged. The text in this section applies until the greenfield cutover (DEC-02f5a9 §6).

**Inputs.** One or more Source Objects of the types the Canonical Contract references. A canonical evaluation act may read N Source Objects (FND-ERR-004, DEC-97bb94); the N:1 cardinality supersedes Foundation's earlier linear framing.

**Outputs.** One Canonical Object version per evaluation act, together with its Evidence and Lineage. The Canonical Object records the Canonical Contract version and Canonical Mapping version applied.

**Once-only guarantee.** A canonical evaluation act produces exactly one Canonical Object version. Subsequent evaluations of the same Source Objects under the same Canonical Contract produce new Canonical Object versions, not replacements of the prior version. Multiple Canonical Object versions coexist.

**Disallowed behaviors.**
- A Canonical Object is produced outside this boundary.
- A prior Canonical Object version is re-evaluated under a newer Canonical Contract version.
- A canonical evaluation act omits Lineage to its input Source Objects.
- A read of Source Objects triggers canonical evaluation.

**Governing source.** Foundation; the Canonical Contract section of The Contract Grammar and the Supporting schema: Canonical Mapping section of The Contract Grammar.

## Metric evaluation boundary

**Purpose.** The metric evaluation boundary produces a Metric Snapshot from one or more Canonical Object versions. It computes a numeric assertion over canonical state.

**Contract governance.** The Metric Contract governs the boundary. The Metric Contract declares the referenced Canonical Contracts (through `metric_binding`), the formula, the grain alignment with the referenced contracts, the temporal gate, the thresholds, and the unit semantics.

**Inputs.** One or more Canonical Object versions from the Canonical Contracts referenced by the Metric Contract. Where a governed secondary metric chain is declared, the boundary may also read one or more upstream Metric Snapshot versions explicitly referenced by that chain. A metric evaluation act may read N Canonical Object versions across N Canonical Contracts (FND-ERR-003, DEC-29c324).

**Outputs.** One Metric Snapshot per evaluation act, together with its Evidence and Lineage. The snapshot records the Metric Contract version, the specific Canonical Object versions referenced, and the resolved numeric value.

**Once-only guarantee.** A metric evaluation act produces exactly one Metric Snapshot. The same Canonical Object inputs evaluated at a later metric evaluation act produce a new Metric Snapshot, not the same snapshot. Secondary Metric Snapshots (those whose Lineage references other Metric Snapshots) are each a distinct evaluation act; traversal of the secondary chain reads preserved Lineage and does not trigger re-evaluation of any snapshot.

**Disallowed behaviors.**
- A Metric Snapshot value is produced by read-time query rather than boundary evaluation.
- A Metric Snapshot is rewritten to correct a value.
- A metric evaluation act references raw Source Objects.
- A metric evaluation act omits Lineage to its input Canonical Object versions.

**Governing source.** Foundation; the Metric Contract section of The Contract Grammar.

## Action evaluation boundary

**Purpose.** The action evaluation boundary produces an Action Object bound to one or more Metric Snapshots. It records declared intent, applies outcome resolution rules against the referenced snapshots, and resolves closure.

**Contract governance.** The Intervention Contract governs the boundary. The Intervention Contract declares activation mode, trigger conditions against one or more Metric Snapshots, assignee pool, closure window, and the evaluation model that resolves outcome against preserved snapshots.

**Inputs.** One or more Metric Snapshots that satisfy the trigger conditions of the Intervention Contract.

**Outputs.** One Action Object per action-creation act, together with its Evidence and Lineage. The Action Object records the Intervention Contract version, the specific Metric Snapshot versions referenced at creation time, and the declared intent. If the governing contract defines a later outcome-resolution act, that act emits additional Evidence and Lineage against the preserved Action Object and referenced Metric Snapshots.

**Once-only guarantee.** An action-creation act produces exactly one Action Object. The references to Metric Snapshots are fixed at creation time and are not rebound. Any governed outcome-resolution act compares preserved referenced snapshots under the governing Intervention Contract. It does not re-enter metric evaluation and it does not rebind the Action Object to newer snapshot state.

**Disallowed behaviors.**
- An Action Object is rebound to newer Metric Snapshots after creation.
- An outcome is reassigned by reading updated metric state.
- An operational workflow outside the platform modifies the Action Object.
- An Action Object permits open-ended non-closure with no terminal state declared.

**Governing source.** Foundation; the Intervention Contract section of The Contract Grammar.

## Proof emission at every boundary

Evidence and Lineage are emitted at every progression-producing boundary act. Their emission is part of the same act that produces the progression object. Proof emission is not a deferred or compensating operation.

Some governed acts emit proof without producing a new progression object. Rejected admissions emit Evidence for the failed admission act. A governed action outcome-resolution act may emit additional Evidence and Lineage against a preserved Action Object. These acts do not change the four-boundary inventory and they do not introduce new progression object types.

| Proof artifact | What it records | Emitted at |
|---|---|---|
| Evidence Object | Evaluation type, inputs, outputs, evaluation context, outcome, timestamp | Every progression-producing boundary act; rejected admissions; any governed action outcome-resolution act |
| Lineage Object | Direct reference relationships between the produced progression object and its input progression objects, and between the produced progression object and the contract versions applied | Every progression-producing boundary act; any additional governed act that establishes a new explicit reference relationship |

Retention of Evidence and Lineage is a policy concern governed at the storage layer. Retention does not change the execution-model status of a boundary act. If no Evidence exists on the authoritative evidence chain for a boundary act, the platform does not treat that boundary act as authoritatively proved for audit (Invariant VI).

The proof chain is described in full in Evidence and Lineage.

## Read access does not trigger evaluation

Evaluation is an explicit act performed at a named boundary with a governed contract. Reading a progression object, a Canonical Mapping, a Contract, or any other platform artifact does not cause a boundary act.

Four consequences follow.

| Operation | Triggers evaluation | Notes |
|---|---|---|
| A consumer reads a Canonical Object version | No | The Canonical Object is returned as preserved state. The canonical evaluation boundary is not re-entered. |
| A dashboard queries a Metric Snapshot | No | The snapshot is returned as preserved state. The metric evaluation boundary is not re-entered. |
| A surface layer computes a value from Canonical Objects | No (and the surface layer must not produce a Metric Snapshot) | Metric values are produced only at the metric evaluation boundary. Computation at the surface produces display values, not authoritative state. |
| An operational workflow executes against an Action Object | No | Workflow execution consumes the preserved Action Object. It does not create, rebind, or modify authoritative action state. |

A platform implementation that allows a read to trigger a boundary act is incorrect under the execution model. An implementation that allows a surface-layer computation to produce a Metric Snapshot or a Canonical Object is incorrect under Invariant II (object ordering) because the object bypasses its governing boundary.

## Chapter boundaries

This chapter has defined the four evaluation boundaries, the contract families that govern each, the rules that apply uniformly at every boundary, the proof emission rules, and the read-access rule. It has deferred:

- Runtime components that perform each evaluation (Sources and the Catalog through Action Evaluation).
- Evidence and Lineage service implementation (Evidence and Lineage).
- Chain completeness across all four boundaries (Chain Completeness and Verdict).
- Database-level storage and indexing of progression objects and proof artifacts (Data Model and Schema).

## References

- Foundation: Evaluation boundaries (authoritative count reconciled in §5.1)
- Foundation: Admission boundary specification
- Foundation: Canonical evaluation boundary specification
- Foundation: Metric evaluation boundary specification
- Foundation: Action evaluation boundary specification
- Foundation: Evidence and Lineage emission at boundaries
- DEC-97bb94: N:1 Source Object to Canonical Object (Decisions)
- DEC-29c324: N:1 Metric Contract to Canonical Contract (Decisions)
- DEC-02f5a9: Business Concept Registry — supersedes the BF/BO/CF vocabulary model (Decisions)
- FND-ERR-003: N:1 Metric cardinality (Errata)
- FND-ERR-004: N:1 Canonical cardinality (Errata)
- FND-ERR-006: Boundary count reconciliation, four not five (Errata)
- The Invariants: The Invariants (Invariants I, II, V, VI referenced here)
- The Object Model: The Object Model (describes the progression objects produced at each boundary)
- The Contract Grammar: The Contract Grammar (describes the contracts that govern each boundary)
- Admission and Observation: Admission and Observation
- Canonical Evaluation: Canonical Evaluation
- Metric Evaluation: Metric Runtime
- Action Evaluation: Intervention and Action
- Evidence and Lineage: Evidence and Lineage
- Chain Completeness and Verdict
- Contract Schemas reference
- Decisions: ADR Registry
- Errata: Errata Ledger
