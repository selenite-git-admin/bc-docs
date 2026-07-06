---
id: the-dual-layer-interaction-model
order: 8
title: "The Dual-Layer Interaction Model"
status: drafting
authority: authoritative
depends_on: [the-authority-model]
governing_sources:
  - Foundation (scope and non-negotiability)
governing_adrs: []
v2_sources: []
word_target: 2200
---

# The Dual-Layer Interaction Model

## Scope

This chapter defines the two interaction surfaces through which human and agent actors participate in the platform: the Conversation surface and the Trust surface. The Conversation surface, including the AI Panel, is advisory. The Trust surface is authoritative. The chapter defines the trust contract between them, the read and write asymmetry that governs their boundary, the governed paths through which advisory output can become a proposal, and the rule that the same contract applies to human and agent actors.

This chapter does not redefine the contract grammar, the evaluation boundaries, the authority ladder, or the runtime systems that implement either surface. Those definitions are provided by the preceding Foundation chapters and by Operating Model chapters that follow.

**Governing source.** Foundation; The Authority Model.

## Surface Summary

The platform exposes two interaction surfaces. They differ by trust model, persistence, and write authority.

| Surface | Purpose | Trust model | Persistence | Writes authorized |
|---|---|---|---|---|
| Conversation surface | Free-form interaction with the platform, including questions, summaries, drafts, and advisory output | Advisory. Output is not binding by itself. | Operational conversation history. Not authoritative state. | None to authoritative state |
| Trust surface | Authoritative platform state, including progression objects, proof objects, governed contracts, governed bindings, ADRs, and Errata Ledger entries | Authoritative. Preserved state is binding under the execution model. | Immutable and append-only where the object model requires it | Governed evaluation acts and governed authoring acts only |

The surfaces are interdependent but not equal. The Conversation surface can read from the Trust surface when the actor's authority permits it. The Trust surface does not read from the Conversation surface to produce authoritative state. A statement that is not preserved on the Trust surface is not authoritative.

**Governing source.** Foundation; The Invariants; The Object Model; The Authority Model.

## Conversation Surface

**Purpose.** The Conversation surface helps an actor inspect, understand, summarize, draft, or propose work against preserved platform state.

**Scope.** The surface can read Trust-surface state through authorized read paths. It can produce free-form advisory output, including summaries, draft contract text, draft ADR text, draft Errata Ledger text, metric explanations, and investigation notes. It does not produce or modify authoritative state.

**Behavior.** The Conversation surface reads preserved state through authority-controlled read paths. It synthesizes advisory output from preserved state, actor input, and any external knowledge available to its runtime components. It can record conversation history for operational continuity. It does not emit Source Objects, Canonical Objects, Metric Snapshots, Action Objects, Evidence Objects, Lineage Objects, governed contracts, governed bindings, ADRs, or Errata Ledger entries.

**Constraints.**

- Conversation history is not authoritative state.
- A statement made on the Conversation surface is not binding on the platform, a tenant, or an actor.
- A draft produced on the Conversation surface remains a proposal until a governed authoring path records and approves it.
- The Conversation surface does not emit Evidence or Lineage. Proof objects are emitted only by proof-emitting acts defined elsewhere in the execution model.

**Failure modes.**

- If the surface produces incorrect or unfounded output, authoritative state is unchanged. The conversation record can preserve the output as operational history, but the Trust surface remains the source for decisions and audit.
- If the surface contradicts preserved Trust-surface state, the preserved state stands. The platform does not update Trust-surface state to match the advisory assertion.
- If the surface is unavailable, Trust-surface state remains available through its own read paths. Authoritative evaluation and governed authoring do not depend on Conversation-surface availability.

**Interactions.** The Conversation surface reads from the Trust surface through authorized read paths. It can hand proposals to governed authoring, where they are treated as drafts. It does not write directly to the Trust surface.

**Governing source.** Foundation; The Authority Model; The Contract Grammar.

## Trust Surface

**Purpose.** The Trust surface provides the authoritative state that platform decisions, tenant decisions, and audit activity can rely on.

**Scope.** The Trust surface contains the authoritative objects defined in The Object Model: Source Objects, Canonical Objects, Metric Snapshots, Action Objects, Evidence Objects, and Lineage Objects. It also contains governed grammar artifacts defined in The Contract Grammar, governed bindings defined in Operating Model, and governance records defined in The Authority Model.

**Behavior.** The Trust surface admits writes only through governed evaluation acts and governed authoring acts. Each write is authorized by the relevant governed artifact, records explicit references, and emits or preserves proof where the execution model requires it. Read access does not produce or modify authoritative state.

**Constraints.**

- Authoritative objects are immutable once produced.
- Every reference to a Trust-surface object identifies object type, object identity, and version.
- Evidence and Lineage are emitted at the act that produces authoritative state.
- A statement that is not preserved on the Trust surface is not authoritative, regardless of the runtime component or actor that produced it.

**Failure modes.**

- If a governed evaluation act fails, the platform records the failure according to the relevant boundary rules. No successful authoritative object is emitted for the failed act.
- If a governed authoring act fails its quality gates, the Trust surface remains unchanged. The proposal remains non-authoritative until a later governed act approves it.
- If a read request resolves to no result for an explicit version, the platform does not silently substitute another version.

**Interactions.** The Trust surface is read by the Conversation surface, runtime evaluators, governed authoring paths, and audit readers according to the actor's authority. It receives writes from governed evaluation and governed authoring only.

**Governing source.** Foundation; The Invariants; The Object Model; The Evaluation Boundaries; The Authority Model.

## Trust Contract

The trust contract defines what each surface can do at the boundary between advisory interaction and authoritative state.

| Direction | Allowed | Forbidden |
|---|---|---|
| Conversation reads Trust | Authorized reads of authoritative objects, governed contracts, governed bindings, Evidence, Lineage, ADRs, and Errata Ledger entries | Reads that bypass authority controls |
| Trust reads Conversation | Nothing for authoritative production | Use of conversation output as an admissible source for an evaluation act |
| Conversation writes Trust | Nothing directly | Direct writes to Source Objects, Canonical Objects, Metric Snapshots, Action Objects, Evidence, Lineage, governed contracts, governed bindings, ADRs, or Errata Ledger entries |
| Trust writes Conversation | Operational display or response content derived from preserved state | Modification of conversation history by authoritative state as if conversation history were authoritative |

The asymmetry is deliberate. Read can cross from the Trust surface to the Conversation surface when authority permits. Write cannot cross directly from the Conversation surface to the Trust surface. Advisory output can become a proposal only when a governed authoring path records it, evaluates it, approves it, and preserves the resulting governed artifact.

**Failure modes.**

- If a runtime path treats Conversation-surface output as authoritative input, the implementation violates the trust contract. The act is not authorized by the execution model.
- If an actor attempts a direct write from the Conversation surface to authoritative state, the platform rejects the write or routes the content into a governed proposal path.
- If a read attempts to bypass authority controls, the platform rejects the read according to the applicable authorization rules.

**Governing source.** Foundation; The Authority Model.

## Human And Agent Symmetry

The trust contract applies to human and agent actors in the same way. Neither actor type receives a privileged path to authoritative state. A human actor and an agent actor read the Trust surface under the authority controls assigned to their authenticated identity. A human actor and an agent actor submit proposed governed artifacts through the same governed authoring path.

Capability differences are recorded but not privileged. An agent can draft a proposal faster than a human actor, but speed does not alter authority. A proposal becomes authoritative only when the governed path approves it and records the resulting artifact. The actor identity recorded on the authoring act preserves whether the actor was human or agentic; the authority rule remains the same.

**Failure modes.**

- If an agent receives a direct write path that a human actor would not receive under the same authority model, the implementation violates the trust contract.
- If an actor identity is not recorded on a governed authoring act, the act lacks the required provenance and is not ready to become authoritative.
- If a proposal bypasses the governed path because it was produced by an agent, the resulting artifact is not authoritative.

**Governing source.** Foundation; The Authority Model.

## AI Interaction With The Trust Surface

AI-assisted interaction is a specific case of the general trust contract. The AI Contract family is provisional in The Contract Grammar. Until governance activates that family, AI participation remains bounded by read access, advisory output, and governed proposals.

| Interaction | Allowed | Notes |
|---|---|---|
| Read | Yes | AI reads Trust-surface state through the same authority-controlled read paths available to the authenticated actor. |
| Advise | Yes | AI produces advisory output on the Conversation surface. The output is not authoritative. |
| Propose through governed authoring | Yes | AI can draft contract text, ADR text, Errata Ledger text, or other governed artifact text. The draft becomes authoritative only through the governed authoring path. |
| Write authoritative state directly | No | AI does not write authoritative objects, proof objects, governed contracts, governed bindings, ADRs, or Errata Ledger entries outside governed evaluation or governed authoring. |

The direct-write prohibition is the load-bearing rule. An implementation that authorizes AI to write authoritative state outside the governed authoring path violates the trust contract and the authority model. The provisional status of the AI Contract family does not create a hidden write path.

**Failure modes.**

- If AI output is stored only as conversation history, it remains advisory.
- If AI output is submitted as a governed proposal and fails the applicable gates, authoritative state remains unchanged.
- If AI output is written directly to authoritative state outside governed authoring or governed evaluation, the implementation is incorrect.

**Governing source.** Foundation; The Contract Grammar; The Authority Model.

## Transition To Operating Model

Operating Model chapters describe how the Foundation model operates at runtime. They assume the two-surface interaction model defined here: advisory interaction can read preserved state, and authoritative state changes only through governed evaluation or governed authoring.

**Governing source.** Foundation.

## References

- Foundation: Scope and Non-Negotiability
- The Problem: The Problem
- The Solution: The Solution
- The Invariants: The Invariants
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- The Authority Model: The Authority Model
