---
id: contract-chain-assembly
order: 8.6
title: "Contract Chain Assembly"
status: drafting
authority: authoritative
depends_on: [the-contract-grammar, business-vocabulary, sources-and-the-catalog]
governing_sources:
  - Foundation (scope and non-negotiability)
governing_adrs:
  - DEC-0e3c64 (Observation Contract is canonical-chain mapping-binding)
  - DEC-97bb94 (N:1 SO to CO multi-source canonical evaluation)
  - DEC-29c324 (N:1 MC to CC metric contracts reference N canonical objects)
  - DEC-bebaec (D305 Chain Completeness SSOT)
  - DEC-762336 (Contract Chain Reconciliation)
  - DEC-d72560 (D301 Canonical Field as 3rd Contract Primitive)
  - DEC-490520 (PII classification at Source Field, propagated through chain)
errata_referenced:
  - FND-ERR-001
  - FND-ERR-003
  - FND-ERR-004
diagrams:
  - DG-binding-chain
v2_sources: []
word_target: 4000
---

# Contract Chain Assembly

## Scope

This chapter defines how the six active contract families compose into the governed chain that connects an observed Source Field to a trusted metric value and an associated action. It defines each link's assembly role, the value identifier each link passes forward, the cardinality rules for multi-source canonical evaluation and multi-canonical metric binding, and the assembly-level integrity rules that determine whether the chain is complete.

This chapter does not redefine the contract grammar or the runtime acts that apply each contract version. The Contract Grammar defines the families. Admission and Observation, Canonical Evaluation, Metric Evaluation, and Action Evaluation define runtime application. Later runtime material defines the detailed gate set and persisted readiness records; this chapter names only the assembly rules that those mechanisms validate.

**Governing source.** Foundation; The Contract Grammar; Business Vocabulary.

## Assembly Summary

The platform recognizes six active contract families in the contract chain. Each family carries one assembly decision and passes a declared identifier set to the next family.

![Binding Chain · field resolution path from a Source Table through the active contract families to a Metric Snapshot. The Observation Contract acts as a double bridge: it directs the Reader against the Source Contract and maps to Business Fields consumed by the Canonical Contract.](/docs/assets/diagrams/DG-binding-chain.svg)

| Position | Link | Input | Assembly decision | Output identifier | Consumed by |
|---|---|---|---|---|---|
| 1 | Source Contract | Source Catalog entries; Business Vocabulary | Declare observable Source Fields and select Business Fields | Business Field codes scoped to a Business Object | Admission Contract; Observation Contract |
| 2 | Admission Contract | Source Contract version | Declare structural and quality validation rules | Validation rules keyed to Business Field codes | Observation Contract; admission boundary |
| 3 | Observation Contract | Source Contract; Admission Contract; Business Object | Map Source Field paths to Business Field codes and direct the Reader | Field-mapping declaration for Source Object payload admission | Canonical Contract; admission boundary |
| 4 | Canonical Contract | Business Object code; Canonical Fields; Canonical Mapping | Declare Canonical Object shape and bind Business Fields to Canonical Fields | Canonical Field codes selected by `field_selection` | Metric Contract; canonical evaluation boundary |
| 5 | Metric Contract | One or more Canonical Contract versions; Canonical Field codes | Bind formula variables to Canonical Field codes and declare grain, temporal gate, and thresholds | Metric value with classification on the emitted Metric Snapshot | Intervention Contract; metric evaluation boundary |
| 6 | Intervention Contract | Metric Contract version | Declare action triggers and outcome resolution against Metric Snapshots | Action Object emission terms | Action evaluation boundary |

Each link is governed and versioned. Each link reads prior outputs by explicit reference. Composition is forward-only: a later link cannot supply input to an earlier link.

**Governing source.** The Contract Grammar; Business Vocabulary; The Object Model; The Evaluation Boundaries.

## Source Contract

**Purpose.** A Source Contract declares what the platform observes from a specific Source Table by selecting Business Fields and binding them to Source Catalog entries.

**Scope.** A Source Contract covers one Source Table within one Source Version. It selects Business Fields by code and records the Source Field path each selection observes. It does not define validation rules, canonical translation, metric formulas, or action triggers.

**Behavior.** A Source Contract version is registered with a contract code, a Source Table reference, selected Business Field codes, and Source Field paths. Later links read the Source Contract version by explicit reference.

**Constraints.**

- A Source Contract references one Source Table.
- Business Field selections must reference certified Business Fields whose Business Object scope matches the Source Contract's declared scope.
- A Source Contract does not declare validation thresholds or value translation.
- Source Field paths must resolve to Source Catalog entries.

**Failure modes.**

- If a Source Contract selects an uncertified Business Field, registration is rejected.
- If a Source Field path does not resolve to a Source Catalog entry, registration is rejected.
- If two Source Contract versions select the same Business Field on the same Source Table with conflicting Source Field paths, chain integrity rejects the conflicting registration.

**Interactions.** The Source Contract is consumed by the Admission Contract for validation-rule scope and by the Observation Contract for Source Field to Business Field mapping. It does not reach canonical evaluation directly; the Observation Contract carries the selected Business Field identifiers forward.

**Governing source.** The Contract Grammar; Business Vocabulary; Sources and the Catalog.

## Admission Contract

**Purpose.** An Admission Contract declares validation rules applied at the admission boundary to records observed under a Source Contract.

**Scope.** An Admission Contract covers structural and quality validation, including required Business Field presence, data type conformance, controlled-list membership, and per-record quality rules. It does not define source-to-business mapping or canonical translation.

**Behavior.** An Admission Contract version is registered with a contract code, the Source Contract version it scopes, and validation rules keyed to Business Field codes. The admission boundary applies the rules per record. Passing records can produce Source Objects with Evidence and Lineage. Rejected records produce Evidence according to admission rules.

**Constraints.**

- An Admission Contract references exactly one Source Contract version.
- Validation rules are keyed by Business Field code.
- A validation rule that references a Business Field code not selected by the Source Contract is rejected.
- An Admission Contract does not produce canonical state.

**Failure modes.**

- If a validation rule references a Business Field code not selected by the Source Contract version, registration is rejected.
- If a record fails a validation rule at admission, the boundary emits Evidence recording the rejection and does not produce a Source Object for that record.
- If the referenced Source Contract version is superseded before republishing, chain integrity routes the authoring act to the superseding version.

**Interactions.** The Admission Contract is consumed alongside the Observation Contract at the admission boundary. The Admission Contract validates. The Observation Contract maps. Both must reference the same Source Contract version.

**Governing source.** The Contract Grammar; Admission and Observation; The Evaluation Boundaries.

## Observation Contract

**Purpose.** An Observation Contract declares the Source Field path to Business Field code mapping that the Reader applies at admission, and identifies the Business Object scope that canonical evaluation later reads.

**Scope.** An Observation Contract covers the field-mapping declaration and the Business Object reference. It is admission-side in runtime execution and canonical-chain-bridging in assembly scope. This dual role is recorded by DEC-0e3c64 and FND-ERR-001.

**Behavior.** An Observation Contract version is registered with a contract code, Source Contract version, Admission Contract version, Business Object code, and field-mapping declaration. The admission boundary admits Source Objects whose payload is keyed by Business Field codes produced by the mapping.

**Constraints.**

- An Observation Contract references exactly one Source Contract version, one Admission Contract version, and one Business Object.
- The field-mapping declaration must cover every Business Field selected by the Source Contract that the Business Object marks as required for canonical evaluation.
- The Observation Contract does not define Business Field to Canonical Field translation.
- PII classification recorded on Source Fields propagates through the Observation Contract to the Source Object payload.

**Failure modes.**

- If a Business Field code in the mapping declaration is not certified or is not a member of the referenced Business Object, registration is rejected.
- If a required Business Field for canonical evaluation is missing from the mapping declaration, chain integrity marks the Observation Contract incomplete.
- If a Source Field path fails Source Catalog resolution at runtime, admission rejects the affected records and Evidence records the failure.

**Interactions.** The Observation Contract is consumed at the admission boundary alongside the Admission Contract. It supplies the Business Field identifiers that the Canonical Contract later reads through Canonical Mapping.

**Governing source.** The Contract Grammar; Admission and Observation; DEC-0e3c64; DEC-490520; FND-ERR-001.

## Canonical Contract

**Purpose.** A Canonical Contract declares the Canonical Object shape produced at the canonical evaluation boundary.

**Scope.** A Canonical Contract covers one Business Object's canonical representation. It selects Canonical Fields through `field_selection`, declares grain through Canonical Field roles, and references the Canonical Mapping version that translates Business Fields to Canonical Fields.

**Behavior.** A Canonical Contract version is registered with a contract code, Business Object code, selected Canonical Field codes, and Canonical Mapping reference. The canonical evaluation boundary reads one or more Source Objects, applies the pinned Canonical Mapping version, and emits a Canonical Object whose payload is keyed by Canonical Field codes.

**Constraints.**

- A Canonical Contract references one Business Object.
- The selected fields must be Canonical Fields, not Business Fields.
- The Canonical Mapping reference must cover every Canonical Field in `field_selection`.
- A Canonical Object can derive from N Source Objects under DEC-97bb94 and FND-ERR-004. A strict 1:1 source-to-canonical assertion is incorrect.

**Failure modes.**

- If `field_selection` includes an uncertified Canonical Field, registration is rejected.
- If Canonical Mapping does not cover a selected Canonical Field, publication is rejected.
- If runtime canonical evaluation cannot resolve a Canonical Field source binding, the boundary emits Evidence recording the failure and does not emit a Canonical Object for that failed act.

**Interactions.** The Canonical Contract is consumed at the canonical evaluation boundary. It carries Canonical Field identifiers that Metric Contracts bind formula variables to. The Canonical Mapping is independently versioned; the Canonical Contract pins one Canonical Mapping version.

**Governing source.** The Contract Grammar; Canonical Evaluation; DEC-97bb94; DEC-d72560; FND-ERR-004.

## Metric Contract

**Purpose.** A Metric Contract binds formula variables to Canonical Field codes from one or more Canonical Contracts and declares the metric evaluation rules that produce Metric Snapshots.

**Scope.** A Metric Contract covers one metric definition. It declares `metric_binding`, formula, grain, temporal gate, and classification thresholds.

**Behavior.** A Metric Contract version is registered with a contract code, metric definition reference, `metric_binding`, formula, grain, temporal gate, and threshold structure. The metric evaluation boundary applies the formula deterministically per grain row and emits a Metric Snapshot.

**Constraints.**

- A Metric Contract references one or more Canonical Contract versions.
- N Canonical Contract versions can feed one Metric Contract under DEC-29c324 and FND-ERR-003.
- Canonical Field codes in `metric_binding` must be certified and present in the selected `field_selection` of the referenced Canonical Contract versions.
- The grain must be consistently declared across every referenced Canonical Contract version.
- Shared-dimension Business Fields exempted under BO-scoped composition can align grains across Canonical Contracts. Non-shared dimensions cannot.

**Failure modes.**

- If `metric_binding` references a Canonical Field not present in the referenced Canonical Contract version, registration is rejected.
- If the grain Canonical Field is not present in every referenced Canonical Contract, publication is rejected.
- If the temporal gate's posting-date binding does not resolve to a Canonical Field role, metric evaluation emits Evidence and does not emit a Metric Snapshot for the affected period.

**Interactions.** The Metric Contract is consumed at the metric evaluation boundary. It produces Metric Snapshot values and classifications that Intervention Contracts read when declaring action triggers.

**Governing source.** The Contract Grammar; Metric Evaluation; DEC-29c324; FND-ERR-003.

## Intervention Contract

**Purpose.** An Intervention Contract declares action triggers and outcome-resolution rules applied at the action evaluation boundary against Metric Snapshots.

**Scope.** An Intervention Contract covers one intervention definition. It binds to Metric Contract versions, declares trigger conditions against emitted Metric Snapshot fields, and declares the outcome-resolution model that produces or resolves Action Objects.

**Behavior.** An Intervention Contract version is registered with a contract code, Metric Contract version references, trigger conditions, assignee pool, closure window, and outcome-resolution model. The action evaluation boundary applies the contract to Metric Snapshots and emits Action Objects through action-creation acts and outcome-resolution acts.

**Constraints.**

- An Intervention Contract references one or more Metric Contract versions.
- Trigger conditions reference fields produced by those Metric Contract versions.
- An Action Object outcome is set once against a specific Metric Snapshot version.
- The outcome-resolution model uses explicit Metric Snapshot versions. Resolutions such as `latest` or `current` are not admitted.

**Failure modes.**

- If a trigger condition references a Metric Snapshot field not produced by the bound Metric Contract version, registration is rejected.
- If outcome resolution references a Metric Snapshot version that does not exist, action evaluation records the failure and does not produce the outcome.
- If the assignee pool is empty at action-creation time, action evaluation records the failure and does not emit the Action Object.

**Interactions.** The Intervention Contract is consumed at the action evaluation boundary. It is the terminal contract-family artifact in the assembly chain.

**Governing source.** The Contract Grammar; Action Evaluation; The Evaluation Boundaries.

## Vocabulary Transition

The chain operates with two vocabularies. Source-side assembly uses Business Field codes. Canonical-side assembly uses Canonical Field codes. The transition happens at the Canonical Contract through Canonical Mapping.

| Chain position | Identifier carried forward |
|---|---|
| Source Contract output | Business Field codes scoped to a Business Object |
| Admission Contract output | Validation rules keyed by Business Field code |
| Observation Contract output | Mapping declaration that places Business Field codes on Source Object payload |
| Canonical Contract output | Canonical Field codes on Canonical Object payload |
| Metric Contract output | Metric value and classification on Metric Snapshot payload |
| Intervention Contract output | Action Object emission and outcome-resolution terms |

The Business Field to Canonical Field transition is the chain's vocabulary boundary. Canonical Mapping records the per-Business-Object translation. A Canonical Contract version pins a specific Canonical Mapping version, and canonical evaluation applies that mapping deterministically.

The two-vocabulary model has three assembly rules. Source Contract, Admission Contract, and Observation Contract reference Business Field codes. Metric Contract and Intervention Contract reference Canonical Field codes. Canonical Contract is the only active contract family that names both vocabularies.

**Governing source.** Business Vocabulary; The Contract Grammar; DEC-d72560.

## Chain Cardinality

The chain is not a strict one-to-one path from Source Field to Action Object. Two cardinality rules govern multi-input behavior.

| Rule | Statement | Authority |
|---|---|---|
| Multi-source canonical evaluation | A Canonical Object can derive from N Source Objects, where N is greater than or equal to 1. One canonical evaluation act can read multiple Source Objects from one or more Source Contracts. | DEC-97bb94; FND-ERR-004 |
| Multi-canonical metric binding | A Metric Snapshot can derive from N Canonical Objects across N Canonical Contracts, where N is greater than or equal to 1. One Metric Contract `metric_binding` can reference multiple Canonical Contract versions. | DEC-29c324; FND-ERR-003 |

Both rules supersede earlier linear framings recorded in Foundation. The Errata Ledger entries name the supersession explicitly.

**Constraints.**

- A Canonical Contract that asserts strict 1:1 source-to-canonical correspondence is incorrect.
- A Metric Contract that asserts strict 1:1 metric-to-canonical correspondence is incorrect.
- Multi-input cardinality does not relax once-per-act evaluation. A multi-input act reads N inputs; it does not authorize mutation of prior outputs.

**Failure modes.**

- If a Canonical Contract publication asserts strict 1:1 source-to-canonical cardinality, publication is rejected.
- If a Metric Contract `metric_binding` references multiple Canonical Contract versions whose grain Canonical Field is inconsistently declared, publication is rejected.

**Governing source.** The Object Model; The Evaluation Boundaries; DEC-97bb94; DEC-29c324; FND-ERR-003; FND-ERR-004.

## Chain Integrity

The chain is complete only when every link's outputs are reachable from the next link's inputs without unresolved references. The platform records chain status as the persisted source of truth for completeness. This section names the assembly-level rules that the chain-readiness mechanism evaluates.

| Rule | Statement |
|---|---|
| Forward composition | A later link's input set is a subset of prior links' output sets. No later link supplies input to an earlier link. |
| Versioned references | Every reference between links identifies a version. Resolution of `latest` or `current` is not admitted. |
| Vocabulary partition | Source Contract, Admission Contract, and Observation Contract reference Business Fields. Metric Contract and Intervention Contract reference Canonical Fields. Canonical Contract names both. |
| Cardinality conformance | Multi-source canonical evaluation and multi-canonical metric binding are admissible under FND-ERR-004 and FND-ERR-003. Strict 1:1 assertions are rejected. |
| Certification reachability | Every Business Field, Business Object, and Canonical Field referenced through the chain is certified. |
| Provenance preservation | PII classification declared at Source Field level propagates through the chain under DEC-490520. No link silently drops the classification. |

**Failure modes.**

- If a later link's input references an unresolved prior output, chain status records the chain as incomplete.
- If a versioned reference resolves to a superseded artifact during readiness evaluation, the authoring path identifies the superseding version before republication.
- If a referenced primitive is not certified, chain status records the chain as incomplete and identifies the missing certification.
- If PII classification is declared at the Source Field but missing from the Source Object payload at admission, registration or admission is rejected according to the failing act.

**Governing source.** DEC-bebaec; DEC-762336; DEC-490520; The Object Model; The Evaluation Boundaries.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- The Authority Model: The Authority Model
- Business Vocabulary: Business Vocabulary
- Sources and the Catalog: Sources and the Catalog
- Admission and Observation: Admission and Observation
- Canonical Evaluation: Canonical Evaluation
- Metric Evaluation: Metric Evaluation
- Action Evaluation: Action Evaluation
