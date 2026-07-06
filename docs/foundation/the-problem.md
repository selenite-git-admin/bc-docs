---
id: the-problem
order: 1
title: "The Problem"
status: drafting
authority: authoritative
depends_on: []
governing_sources:
  - Patent Abstract
  - Patent §1 Technical Field and System Overview
  - Patent §2 Problem Statement and Limitations of Existing Systems
  - Foundation (scope and non-negotiability)
v2_sources:
  - system/foundation/patent/sections/intro.md
  - system/foundation/patent/sections/section-01.md
  - system/foundation/patent/sections/section-02.md
word_target: 2400
---

# The Problem

## Scope

This chapter describes three failure classes observed in conventional enterprise data architectures: meaning drift after observation, reconstruction-based audit, and implicit reference. It then describes the limits of procedural controls and the execution-model constraints applied in response. Detailed treatment of runtime components, authoritative object types, and contract families is deferred to The Invariants through The Evaluation Boundaries and Operating Model chapters.

## Failure classes

Conventional enterprise data architectures exhibit three recurring failure classes. Each is architectural rather than operational. Each degrades reliability, traceability, or both.

| Failure class | Conventional behavior | Resulting risk | Execution-model constraint |
|---|---|---|---|
| Meaning drift after observation | Business meaning is assigned, reassigned, and reinterpreted at multiple points along an execution path. Different components apply different interpretations of the same observed value. | The same value carries different meanings across the architecture. Historical comparisons are unreliable. Disputes cannot be settled by reading preserved state. | Business meaning is evaluated once per Canonical Object version at the canonical evaluation boundary. No other operation produces or modifies meaning. |
| Reconstruction-based audit | Historical outputs are explained by replaying the original observation, re-running intermediate operations, and reconstructing the context in which a value was computed. | Inputs, logic, and configuration change over time. Reconstructed answers are approximations built from remaining fragments. Historical claims cannot be verified against preserved state. | Evidence and Lineage are emitted at every evaluation boundary, immutable and append-only. Audit reads preserved artifacts. The platform does not reconstruct proof. |
| Implicit reference | Consumers refer to data by identity alone, resolving the specific version at read time. Requests for head state resolve to whichever version is selected when the request is received. | The same reference returns different values at different times. Decisions cannot be traced to the specific state on which they were made. | Every reference identifies the object's type, identity, and version. Implicit resolutions such as "head version" are not admitted. |

The three failure classes can coexist in the same workflow, but they are not identical. Each has a distinct operational effect and a distinct corrective constraint.

## Meaning drift after observation

Meaning drift occurs when business meaning is not fixed at a declared evaluation point. A component that reads an accounts-receivable balance from a source system may compute it differently than a component that displays it in a report, which in turn may differ from a component that feeds it into a forecast. Each component can be internally consistent. The architecture as a whole is not.

The result is that the same observed value has no stable meaning across the system. A question about why two systems report different values for the same metric cannot be answered by inspection of preserved state. The answer depends on which component is asked, which code version is running, and which interpretation path is reconstructed for the inquiry.

This failure class is architectural because local correctness does not preserve cross-system meaning. The architecture preserves values, but it does not preserve the semantic act that assigned meaning to those values.

Patent §2.2.2 characterizes this condition as split-brain semantics: multiple tools applying different versions of the same definition without a single preserved semantic act.

## Reconstruction-based audit

Reconstruction-based audit occurs when historical outputs are explained by replay rather than by preserved state. When an auditor asks how a value was produced, the answer is assembled from logs, queries, replayed code paths, and reconstructed configuration.

This method is unstable for three reasons.

- Inputs change. Source systems edit, overwrite, and correct their own records.
- Logic changes. The code that produced the original value is not necessarily the code running at a later evaluation time.
- Context changes. Parameters, feature flags, schedules, and environmental settings are not preserved with the output unless the platform records them explicitly.

A reconstructed answer is therefore an approximation. It can describe a plausible path. It cannot prove the original act unless the original act was preserved at the time it occurred.

Patent §2.2.3 describes this condition as late-binding validation: error detection after costly operations have already executed, without preserved proof of the original act.

## Implicit reference

Implicit reference occurs when a consumer identifies an object but not the version of that object. A request for the customer list resolves to whichever head version the system selects at read time. A dashboard resolves a metric to the most recently computed instance. A report resolves a period total to whichever data is available when the report is generated.

This behavior makes the reference unstable. Two consumers making nominally identical requests can receive different values. The same consumer can make the same request twice and receive different values. The system holds no durable record of which specific version was consumed unless the reference itself is explicit.

A decision recorded against an implicit reference cannot be traced to a stable historical state. Accountability requires reference stability. Implicit reference does not provide it.

## Interaction between the failure classes

The three failure classes compound.

- Meaning drift makes reconstruction-based audit necessary because preserved semantic state is unavailable.
- Reconstruction-based audit makes implicit reference tolerable because historical state is already being reassembled from fragments.
- Implicit reference makes meaning drift harder to detect because different resolutions appear as ordinary variation rather than as violations of a stable fact.

Correcting one class in isolation does not correct the others. A platform can centralize definitions and still depend on replay for audit. A platform can preserve logs and still allow implicit reference. A platform can require explicit reference and still permit downstream reinterpretation.

## Why procedural controls are insufficient

Procedural controls address these failure classes by policy. Typical examples include centralized metric definitions, approved reference data, mandatory audit trails, and review gates. Each is useful. None is sufficient on its own.

Procedural controls fail in three predictable ways.

| Procedural limit | Description |
|---|---|
| Participant dependence | A policy is effective only if each component and operator knows it, understands it, and implements it correctly. |
| Drift from runtime | The policy recorded in governance documents and the behavior implemented in code are revised through different mechanisms and can diverge over time. |
| Delayed detection | Review identifies violations after outputs have already been produced and consumed. |

These failure modes are not caused by poor discipline alone. They follow from an architecture that embeds semantic interpretation in procedural code and treats evidence as a secondary artifact.

## Execution-model constraints

The execution model applies one constraint to each failure class. These constraints are formalized as invariants in The Invariants.

| Failure class | Constraint | Operational effect |
|---|---|---|
| Meaning drift after observation | Business meaning is produced once per Canonical Object version at the canonical evaluation boundary. | Downstream components read preserved semantic state rather than recomputing meaning. |
| Reconstruction-based audit | Evidence and Lineage are emitted synchronously with each evaluation boundary. | Audit reads preserved proof rather than replaying prior operations. |
| Implicit reference | Every reference identifies object type, identity, and version. | Consumers bind to stable historical state rather than to whichever version is selected at read time. |

The Invariants formalizes these constraints as invariants. Sources and the Catalog through Chain Completeness and Verdict describe the runtime components that satisfy them.

## Chapter boundaries

This chapter has described the problem space and the corresponding execution-model constraints. It has not defined the execution model, object sequence, contract grammar, or evaluation boundaries in full. The Invariants defines the six invariants that formalize these constraints. The Object Model through The Evaluation Boundaries define the object model, contract grammar, and evaluation boundaries on which the invariants depend.

## References

- Patent Abstract
- Patent §1: Technical Field and System Overview
- Patent §2: Problem Statement and Limitations of Existing Systems
- Foundation: Scope and Non-Negotiability
- The Invariants: The Invariants
- Evidence and Lineage: Evidence and Lineage
- Errata: Errata Ledger
