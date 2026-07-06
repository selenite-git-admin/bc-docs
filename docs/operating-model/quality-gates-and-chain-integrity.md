---
id: quality-gates-and-chain-integrity
order: 8.7
title: "Quality Gates and Chain Integrity"
status: drafting
authority: authoritative
depends_on: [the-contract-grammar, contract-chain-assembly, business-vocabulary]
governing_sources:
  - Foundation (scope and non-negotiability)
governing_adrs:
  - DEC-40b650 (AI-assisted verification hybrid gated model)
  - DEC-804874 (D366 L-node semantic verification cross-family)
  - DEC-b5631b (Field Data Type Quality Gate)
  - DEC-bebaec (D305 Chain Completeness SSOT)
  - DEC-490520 (PII classification propagation)
errata_referenced: []
v2_sources: []
word_target: 4000
---

# Quality Gates and Chain Integrity

## Scope

This chapter defines the gate set that every governed authoring act passes through and the chain integrity check that validates an assembled contract chain. It defines verdict semantics, track equivalence across Manual-with-AI and Programmatic authoring tracks, the four gate categories, the read-only chain integrity check, and the AI verification posture under the trust contract.

This chapter does not redefine assembly rules or runtime evaluation. Contract Chain Assembly defines the assembly rules that gates validate. The Authority Model defines the authority levels under which gate verdicts hold. The Dual-Layer Interaction Model defines the trust contract that governs AI-assisted verification. This chapter names the checks and their consequences; persisted readiness records are governed by the chain-completeness source of truth.

**Governing source.** Foundation; Contract Chain Assembly; The Authority Model; The Dual-Layer Interaction Model.

## Verdict Semantics

A gate emits one of three verdicts. The verdict carries a fixed consequence for the authoring act and for chain readiness.

| Verdict | Meaning | Consequence on authoring act | Consequence on chain readiness |
|---|---|---|---|
| Green | The gate conditions are satisfied without exception | The act proceeds; the artifact is admissible to certification | The artifact can contribute to chain completeness |
| Amber | The gate conditions are satisfied with declared exceptions or warnings | The act proceeds; the artifact is admissible to certification with a recorded exception | The chain remains assembleable; the exception is surfaced on readiness review |
| Red | The gate conditions are not satisfied | The act is rejected; the artifact is not admissible to certification | The chain is incomplete until a corrected submission clears the red verdict |

Verdicts are recorded against the artifact and the act, not against the actor. A gate that emits a red verdict for a Programmatic submission and an amber verdict for a Manual-with-AI submission of the same artifact is incorrect unless the artifact or evaluation conditions differ.

**Constraints.**

- Every gate emits exactly one verdict per artifact per evaluation.
- A gate does not silently downgrade a red verdict to amber.
- A corrected resubmission creates a new gate evaluation. The prior verdict remains in act history.
- An amber verdict carries a recorded exception that names the condition admitted and the authority that admitted it.

**Failure modes.**

- If a gate emits a verdict without recording its evaluation conditions, the verdict is not admissible to certification and the act is held until the conditions are recorded.
- If two evaluations of the same gate against the same artifact emit different verdicts without an intervening artifact change, the platform records verdict drift and routes the artifact to manual review.
- If an amber verdict has no recorded exception, certification is blocked.

**Governing source.** Foundation; The Authority Model.

## Track Equivalence

The platform recognizes two authoring tracks: Manual-with-AI and Programmatic. The two tracks must produce identical verdicts against the same artifact under the same gate conditions. A gate verdict depends on the artifact and the gate conditions, not on the track that submitted the artifact.

**Manual-with-AI track.** A human author drafts the artifact, AI verification produces advisory output, and the gates evaluate the artifact. AI advisory output participates as input to AI-Verification Gates only. It does not adjust verdicts emitted by Structural, Data-Quality, or Certification Gates.

**Programmatic track.** A bulk authoring act submits one or more artifacts produced by a script, generator, or migration. The same gate set evaluates each artifact under the same conditions. The Programmatic track is admissible only when gate conditions are recorded against each artifact with the same discipline as the Manual-with-AI track.

**Constraints.**

- Gate conditions are identical across the two tracks.
- A gate that admits Programmatic submissions under relaxed conditions is incorrect.
- The Programmatic track records the responsible human author identity on each authoring act.
- Both tracks use the same Errata Ledger path for adopted exceptions.

**Failure modes.**

- If a Programmatic submission emits amber when the Manual-with-AI track would emit red on the same artifact under the same conditions, the implementation has track drift and the artifact is re-evaluated.
- If a Programmatic submission omits responsible human author identity, the act is rejected before gate evaluation.
- If track-equivalent submissions produce different recorded exception sets, manual review reconciles the exceptions and records the agreed set.

**Governing source.** The Authority Model; The Dual-Layer Interaction Model.

## Per-Act Gate Matrix

The platform applies a gate set at each authoring act. The gate set varies by the act's subject. The table summarizes gates for the authoring acts described by Business Vocabulary and Contract Chain Assembly.

| Authoring act | Structural | Data-Quality | AI-Verification | Certification |
|---|---|---|---|---|
| Business Field registration | Yes | Yes, data type | Yes | Yes |
| Business Object registration | Yes | Yes, composition | Yes | Yes |
| Canonical Field registration | Yes | Yes, data type | Yes | Yes |
| Source Contract publication | Yes | Yes, path resolution | Optional | Through references |
| Admission Contract publication | Yes | Yes, rule keying | Optional | Through references |
| Observation Contract publication | Yes | Yes, mapping coverage | Yes, mapping advice | Through references |
| Canonical Contract publication | Yes | Yes, mapping coverage | Yes, mapping advice | Through references |
| Canonical Mapping publication | Yes | Yes, translation coverage | Yes, translation advice | Through references |
| Metric Contract publication | Yes | Yes, binding coverage | Yes, formula advice | Through references |
| Intervention Contract publication | Yes | Yes, trigger coverage | Optional | Through references |

`Through references` means that a contract-publication act inherits certification reachability from referenced primitives and prior contract versions. Certification is checked transitively, but the contract artifact does not certify the primitive again.

**Constraints.**

- A gate listed for an authoring act must run for that act.
- A required gate cannot be omitted because the artifact was submitted programmatically.
- Optional AI-Verification Gates become required only when the authoring policy for that artifact type declares them required.

**Failure modes.**

- If a required gate is absent from an act record, certification is blocked.
- If a gate runs at an act where no governing rule authorizes it, the result is recorded as non-authoritative and cannot block or admit certification.
- If a transitive certification reference cannot be resolved, publication is rejected.

**Governing source.** Contract Chain Assembly; Business Vocabulary; The Authority Model.

## Structural Gates

**Purpose.** Structural Gates verify that an artifact has required fields, well-formed values, and resolvable references.

**Scope.** Structural Gates cover frontmatter completeness, body element presence, reference resolution against governed primitives and prior contract versions, and grammar conformance against the artifact's contract-family schema. They do not evaluate declared-value quality, advisory AI findings, or certification status.

**Behavior.** A Structural Gate evaluates an artifact against the schema declared by its contract family or primitive type. The gate emits a verdict and records the conditions evaluated. Green requires required fields to be present and references to resolve. Amber requires every exception to be recorded under a governing authority. Red indicates at least one unresolved schema or reference condition.

**Constraints.**

- A Structural Gate evaluates one artifact at a time.
- Cross-artifact conditions belong to the chain integrity check.
- The schema referenced by the gate is the published schema for the artifact's contract family or primitive type.
- Custom schema variants are not admissible.

**Failure modes.**

- If an artifact omits a required field, the gate emits red.
- If a reference resolves to a superseded artifact, the gate emits red and identifies the superseding artifact.
- If a reference resolves to an unrecognized identifier, the gate emits red.
- If a controlled-list value falls outside the declared controlled list, the gate emits red.

**Interactions.** Structural Gates run first at every authoring act. A green or amber Structural verdict is a precondition for Data-Quality, AI-Verification, and Certification Gates.

**Governing source.** The Contract Grammar; Contract Chain Assembly; Business Vocabulary.

## Data-Quality Gates

**Purpose.** Data-Quality Gates verify that declared values conform to the quality rules attached to the artifact's contract family or primitive type.

**Scope.** Data-Quality Gates cover data-type conformance against governed primitives, controlled-list membership for controlled values, mapping coverage between source-side and target-side identifiers, and propagation rules for values declared at one chain position that must persist to a later position. They do not evaluate structural well-formedness or advisory AI findings.

**Behavior.** A Data-Quality Gate evaluates the artifact's declared values against registered rules. Business Field and Canonical Field gates enforce declared type rules under DEC-b5631b. Observation Contract gates verify required Business Field mapping coverage. Canonical Mapping gates verify Canonical Field translation coverage. Metric Contract gates verify formula-variable binding coverage. PII classification gates verify that PII declared at Source Field level under DEC-490520 reaches the Source Object payload through the Observation Contract.

**Constraints.**

- A Data-Quality Gate runs only after the corresponding Structural Gate emits green or amber.
- Data-quality rules are registered with the gate conditions.
- Ad hoc rules added at evaluation time are not admissible.
- Amber verdicts require recorded exceptions.

**Failure modes.**

- If a Business Field's declared data type conflicts with the registered data type rule, the gate emits red.
- If an Observation Contract omits a Business Field required by the referenced Business Object, the gate emits red.
- If a Metric Contract `metric_binding` references a Canonical Field not present in the referenced Canonical Contract version's `field_selection`, the gate emits red.
- If PII classification declared at Source Field level is missing from the Observation Contract mapping output, the gate emits red.

**Interactions.** Data-Quality Gates run after Structural Gates and before AI-Verification Gates. A green or amber Data-Quality verdict is a precondition for Certification Gates.

**Governing source.** DEC-b5631b; DEC-490520; Contract Chain Assembly; Business Vocabulary.

## AI-Verification Gates

**Purpose.** AI-Verification Gates produce advisory findings for semantic checks that benefit from AI-assisted review but remain governed by the trust contract.

**Scope.** AI-Verification Gates cover semantic-family classification of vocabulary primitives under DEC-804874, mapping suggestions against Business Object composition, formula review for Metric Contract drafts, name conformance against ISO 11179 conventions, and likely duplication during onboarding. They do not authorize direct writes to authoritative state and do not override Structural or Data-Quality verdicts.

**Behavior.** An AI-Verification Gate produces advisory output bound to the artifact under evaluation. The output enters the act record as advisory annotation with evidence and timestamp. AI-Verification Gates can emit their own gate verdict, but that verdict is advisory to the Certification Gate and does not override other gate categories. AI participation is read-and-advise only under The Dual-Layer Interaction Model.

**Constraints.**

- An AI-Verification Gate cannot override a Structural Gate verdict.
- An AI-Verification Gate cannot override a Data-Quality Gate verdict.
- AI advisory output must be recorded with evidence and timestamp.
- Cross-family verification under DEC-804874 runs when a vocabulary primitive must be classified across multiple authoritative standards.

**Failure modes.**

- If a required AI-Verification Gate is unavailable, the authoring act records the unavailability and pauses until the gate can evaluate the artifact.
- If AI advisory output lacks recorded evidence, the output is rejected and not added to the act record.
- If AI classification conflicts with a Data-Quality verdict, the conflict is recorded and resolved at the Certification Gate. AI does not silently override the prior verdict.

**Interactions.** AI-Verification Gates run after Data-Quality Gates and before Certification Gates. They participate in Manual-with-AI authoring under The Dual-Layer Interaction Model. Programmatic submissions record AI-Verification advisory output under the same rules when AI participates in the submission path.

**Governing source.** DEC-40b650; DEC-804874; The Dual-Layer Interaction Model; The Contract Grammar.

## Certification Gates

**Purpose.** Certification Gates record that an artifact has cleared the required prior gates and admit the artifact to its certified or published state.

**Scope.** Certification Gates cover certified-state transitions for vocabulary primitives and publication-state transitions for contract family versions and Canonical Mapping versions. They do not re-evaluate schema conformance, data-quality conformance, or advisory verification.

**Behavior.** A Certification Gate evaluates the artifact's recorded verdict history. The gate emits green only when every required prior gate has emitted green or amber with a recorded exception. A red prior verdict produces a red Certification verdict. The state transition is recorded with artifact identity, verdict, gate evidence, and actor identity.

**Constraints.**

- A Certification Gate cannot emit green if any required prior gate emitted red.
- A Certification Gate cannot emit green if a required prior gate is missing.
- The certified or published state transition is recorded only when Certification emits green or amber.
- A red Certification verdict leaves the artifact in its prior state.

**Failure modes.**

- If a Certification Gate evaluates an artifact with no recorded prior gate verdicts, it records the gap and emits red.
- If a Certification Gate emits green for an artifact that has a red prior verdict, chain integrity records the certification as inconsistent and routes the artifact to manual review.
- If the state-transition record lacks actor identity, certification is not effective.

**Interactions.** Certification Gates are the final gate in the per-act sequence. Their green or amber verdict makes a vocabulary primitive admissible to contract authoring. The chain integrity check reads certified-state status when it evaluates chain readiness.

**Governing source.** Business Vocabulary; The Authority Model; The Contract Grammar.

## Chain Integrity Check

The chain integrity check is a read-only evaluation of assembled contract-chain artifacts. It does not author state, modify artifacts, or adjust prior gate verdicts. The check produces a readiness result that names each rule evaluated, the artifacts that participated, and the verdict for the assembled chain.

The check evaluates the assembly-level rules named in Contract Chain Assembly.

| Rule | Read-only check |
|---|---|
| Forward composition | A later link's input set is a subset of prior links' output sets |
| Versioned references | Every reference between links resolves to an explicit version |
| Vocabulary partition | Source-side links reference Business Fields; canonical-side links reference Canonical Fields; the Canonical Contract names both |
| Cardinality conformance | Multi-source canonical evaluation and multi-canonical metric binding are admissible; strict 1:1 assertions are absent |
| Certification reachability | Every primitive referenced through the chain is certified |
| Provenance preservation | PII classification declared at Source Field level reaches the Source Object payload |

The check does not run the gates again. Gates evaluate each artifact at its authoring act. The chain integrity check evaluates assembled artifacts together. A red chain-integrity verdict does not invalidate prior artifact-level gate verdicts; it records that the assembly does not yet meet chain-completeness conditions.

**Constraints.**

- The chain integrity check is read-only.
- The check produces a readiness result; it does not write to a contract artifact, primitive registration, or certification record.
- The check uses chain status under DEC-bebaec as the source of truth for completeness.
- A red chain-integrity verdict identifies the failed rule and participating artifacts.

**Failure modes.**

- If the check encounters a missing artifact reference, it records the chain as incomplete and identifies the missing artifact.
- If the check disagrees with chain status under DEC-bebaec, the disagreement is recorded for the readiness path. The check itself does not write the persisted record.
- If assembled artifacts have inconsistent verdict histories, the check records the inconsistency and routes the chain to manual review.

**Governing source.** DEC-bebaec; Contract Chain Assembly; The Authority Model.

## AI Verification Posture

The AI verification posture under The Dual-Layer Interaction Model is read-and-advise only. AI-Verification Gates produce advisory output and participate as one input to Certification Gates. AI does not write authoritative state directly. The governed authoring path is the only path through which AI-drafted artifact text can become authoritative.

This posture has three consequences for gates.

**Gate independence.** AI-Verification verdicts are independent of Structural and Data-Quality verdicts. AI cannot relax a red Structural or Data-Quality verdict. AI cannot turn a green Structural or Data-Quality verdict into a contradictory blocker by itself.

**Escalation.** When AI-Verification output flags a likely issue that Structural and Data-Quality Gates did not catch, the artifact is routed to manual review. The reviewer's recorded verdict governs whether the artifact proceeds. Adopted exceptions use the Errata Ledger path.

**Auditability.** AI-Verification output is recorded with evidence on the act record. An auditor sees AI participation as a discrete advisory line, distinct from human authoring acts and gate verdicts. The advisory line is recorded for completeness; recording it does not make it authoritative.

**Failure modes.**

- If AI-Verification output is treated as authoritative input by a later gate, the implementation violates the trust contract.
- If an AI-Verification Gate runs without the governed authoring path available, the gate records the unavailability and the act pauses.
- If AI-drafted artifact text submits as Programmatic without responsible human author identity, track equivalence is violated and the act is rejected.

**Governing source.** The Dual-Layer Interaction Model; DEC-40b650; DEC-804874; The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- The Authority Model: The Authority Model
- The Dual-Layer Interaction Model: The Dual-Layer Interaction Model
- Business Vocabulary: Business Vocabulary
- Sources and the Catalog: Sources and the Catalog
- Contract Chain Assembly: Contract Chain Assembly
