---
id: foundation-overview
order: 0.9
title: "Foundation: Overview"
status: drafting
authority: authoritative
depends_on: []
governing_sources: []
governing_adrs: []
errata_referenced: []
v2_sources: []
---

# Foundation: Overview

## Scope

This chapter is the section opener for Foundation. It states what Foundation is and what role it plays in the documentation, maps the eight chapters that follow this overview into reading groups, gives a recommended reading sequence for a cold reader, declares the boundaries between Foundation and the other five sections of the documentation, and records the locked-status discipline under which Foundation chapters are amended.

This chapter does not redefine any Foundation concept. The Problem, The Solution, The Invariants, The Object Model, The Contract Grammar, The Evaluation Boundaries, The Authority Model, and The Dual-Layer Interaction Model each govern their own claims. This overview locates them; it does not restate them with authority. Where this overview names a section-wide property, the governing source is the outline that records Foundation's structure or the chapter that owns the property.

This chapter exists so that a reader who opens Foundation cold can locate any specific chapter without having read the later chapters, and so that a reader who has finished Foundation can hold the eight chapters that follow as one coherent set rather than as eight independent files.

**Governing source.** outline.md §4.1.

## What Foundation Means

Foundation is the architectural authority for the platform. Every claim that any other section makes about platform behavior derives from a Foundation chapter, an Architecture Decision Record (ADR), or an Errata entry. Foundation does not derive its claims from any later section.

| Property | Operational form |
|---|---|
| Authoritative | The nine-chapter Foundation section defines the architectural rules that bind every later section. A claim that contradicts a Foundation chapter is incorrect against the platform's architecture, regardless of where in the documentation it appears. |
| Locked | Foundation chapters are not amended through ordinary authoring acts. Material changes to a Foundation chapter require an ADR or an Errata entry under the Authority Model's discipline. The lock prevents per-session reinterpretation of the platform's bedrock rules. |
| Section-independent | Foundation depends on no other section. Operating Model, Implementation, AI, Development, Onboarding, Operations, and Compliance all depend on Foundation; Foundation depends on none of them for its own correctness. |
| Source of constraint | Foundation's claims appear in later sections as constraints, not as descriptions. Operating Model obeys the Object Model; it does not redefine the Object Model. The same discipline applies to every later section. |

The lock-status discipline is the section's defining trait. A reader who finds an apparent inconsistency between a Foundation chapter and a later chapter should treat the Foundation chapter as authoritative until an ADR or Errata entry records a governed change to the Foundation reading.

**Governing source.** outline.md §4.1; The Authority Model.

## The Eight Chapters That Follow

Foundation has nine chapters: this overview plus the eight chapters that follow. The grouping below is for navigation; section order is fixed by the outline and by chapter dependencies.

| Group | Chapters | What the group covers |
|---|---|---|
| Origin | The Problem; The Solution | Why the platform exists. The three failure classes that conventional procedural controls cannot prevent, and the architectural constraints that BareCount introduces to prevent each class. |
| Hard Rules | The Invariants | Six invariants that define platform correctness. Each invariant prevents a distinct failure class; the set is interdependent. |
| Vocabulary | The Object Model; The Contract Grammar | The six authoritative object types (four progression objects and two proof objects), and the six contract families with their shared grammar (Source, Admission, Observation, Canonical, Metric, Intervention). |
| Acts | The Evaluation Boundaries | The four evaluation boundaries that produce authoritative state. Read access never triggers evaluation; authoritative state is produced only at the four governed acts. |
| Authority | The Authority Model | The three-level authority ladder (Foundation; ADRs and Errata; Descriptive layers) that governs all platform change. The model defines who may decide what and how decisions are recorded. |
| Interaction | The Dual-Layer Interaction Model | The two surfaces with two trust models. The Conversation surface (AI Panel) is advisory and ephemeral; the Trust surface (metrics, Canonical Objects, proof chain) is authoritative and immutable. The same contract applies to human and agent interaction. |

The six groups cover the eight chapters that follow without overlap. A chapter that does not fit a group is a chapter that does not belong in Foundation.

**Governing source.** outline.md §4.1.

## Reading Sequence

Foundation is written so the eight chapters that follow are read in outline order. The order is intentional: each later chapter assumes the prior chapters' definitions.

| Reader intent | Recommended sequence | Why |
|---|---|---|
| First-time architectural understanding | The eight chapters that follow, in outline order | The Problem motivates the solution; The Solution introduces the constraints that the Invariants define; the Invariants frame the Object Model and Contract Grammar; the Object Model and Contract Grammar are consumed by the Evaluation Boundaries; the Authority Model governs how everything in the prior chapters changes; the Dual-Layer Interaction Model defines who interacts with what the prior seven chapters established. |
| Audit and compliance | The Invariants; The Object Model; The Authority Model; The Evaluation Boundaries; The Dual-Layer Interaction Model | Audit reads the binding constraints (Invariants), the authoritative artifact set (Object Model), the change-governance rules (Authority Model), the act inventory (Evaluation Boundaries), and the interaction discipline first; the Problem and Solution chapters provide context but are not directly audit material. |
| Engineering reading | The Object Model; The Contract Grammar; The Evaluation Boundaries; The Invariants; The Authority Model; The Dual-Layer Interaction Model; The Problem; The Solution | Engineering reads the artifact and act definitions first to know what to build, then the invariants and authority model to know what constraints bind the build, then the interaction model to know who consumes what is built. The origin chapters are read last as motivation for the rules already absorbed. |

The reading sequences do not reorder the chapters in the section. They guide a reader who needs to extract a coherent subset for a specific purpose.

**Governing source.** outline.md §4.1.

## Boundaries with Other Sections

Foundation supplies the architectural authority that every other section consumes. The boundaries are inverted from later sections: Foundation does not depend on anything; everything depends on Foundation.

| Section | Boundary role | What crosses the boundary |
|---|---|---|
| Operating Model | Consumes Foundation as locked authority | Operating Model chapters cite Invariants, the Object Model, the Contract Grammar, the Evaluation Boundaries, the Authority Model, and the Dual-Layer Interaction Model as already-defined authority. Operating Model obeys Foundation; it does not redefine Foundation. |
| Implementation | Consumes Foundation as locked authority | Implementation chapters describe service placement, storage shape, APIs, user interfaces, and tooling for artifacts that Foundation defines. Implementation chapters do not redefine Foundation artifacts. |
| AI | Consumes Foundation as locked authority | AI services, agents, and gates participate in the platform under Foundation invariants and the Dual-Layer Interaction Model. AI Contract grammar (provisional family) is defined in The Contract Grammar; AI runtime behavior obeys Foundation. AI does not redefine Foundation. |
| Development | Consumes Foundation as locked authority | DevHub, decision and change workflow, build and release, and quality assurance operate as engineering process around Foundation-governed artifacts. Development does not redefine Foundation. |
| Onboarding | Consumes Foundation as locked authority | Onboarding workflows produce contracts whose grammar is defined by Foundation. Quality gate verdicts cite Foundation invariants. Onboarding acts do not redefine Foundation. |
| Operations | Consumes Foundation as locked authority | Operational governance records (subscription, security, lifecycle, observability) operate around Foundation-defined artifacts. Operations does not redefine Foundation. |
| Compliance | Consumes Foundation as locked authority | Compliance reads against Foundation's invariants and proof discipline. Compliance reports conformance; it does not produce Foundation authority. |

The dependency direction is uniform and one-way. A Foundation chapter that depends on a later section for its own correctness is a boundary violation. A later section that redefines a Foundation invariant instead of consuming it is also a boundary violation. The boundaries make these violations detectable through cross-section citation patterns.

**Governing source.** outline.md §4.1; The Authority Model.

## Cross-Cutting Concerns

Three concerns thread through multiple Foundation chapters. The cross-cutting nature is intentional; the concerns are stated in each chapter where they apply rather than centralized in one chapter that the others would then need to consult separately.

| Concern | Chapters that thread it | How it is preserved |
|---|---|---|
| The invariants | The Invariants names them; The Object Model, The Contract Grammar, The Evaluation Boundaries, and The Dual-Layer Interaction Model each apply specific invariants to their content | Each chapter that applies an invariant cites it by name. The Invariants chapter is the single definitional source. |
| Authoritative state | The Object Model defines the artifacts; The Evaluation Boundaries defines the acts that produce them; The Authority Model defines who may govern changes to the rules under which they are produced | Authoritative state is produced only at governed boundary acts and is governed by versioned contracts under the Authority Model's three-level ladder. |
| Trust and interaction | The Dual-Layer Interaction Model defines the trust contract; The Authority Model defines the change-governance rules that protect the Trust surface; The Object Model defines the immutable artifacts that the Trust surface preserves | The Trust surface is authoritative and immutable; the Conversation surface is advisory and ephemeral. The same contract binds human and agent interaction. |

A Foundation chapter that introduces a new claim about any of the three cross-cutting concerns must align with the threading discipline. A later section that consumes a Foundation chapter must consume the cross-cutting concern as the chapter states it.

**Governing source.** outline.md §4.1; The Invariants; The Object Model; The Evaluation Boundaries; The Authority Model.

## Constraints

The constraints below apply to Foundation as a whole and are inherited by every chapter in the section.

| Constraint | Operational form |
|---|---|
| Foundation is locked | Material changes to a Foundation chapter require an ADR or an Errata entry. The Authority Model governs the change discipline. |
| Foundation cites no later section | A Foundation chapter does not cite Operating Model, Implementation, AI, Development, Onboarding, Operations, or Compliance as governing source. Foundation may signpost later sections as targets where a topic is elaborated, but does not depend on them for its own correctness. |
| Foundation's claims are absolute within the platform | A claim that contradicts a Foundation chapter is incorrect against the platform's architecture. There is no per-tenant override of a Foundation invariant. There is no per-environment relaxation of a Foundation rule. |
| ADRs and Errata are the only paths for Foundation change | An ADR records a governed decision; an Errata entry records a governed contradiction or version-gap exception. Per-session reinterpretation of a Foundation chapter without an ADR or Errata entry is not admissible. |
| Foundation chapters interlock | The eight chapters that follow are not independent. A change to one Foundation chapter that touches another Foundation chapter's claim requires the second chapter's reading to be reconsidered in the same governance act. |

A Foundation chapter that violates any of these constraints is incorrect against the section's discipline.

**Governing source.** The Authority Model.

## References

- The Problem
- The Solution
- The Invariants
- The Object Model
- The Contract Grammar
- The Evaluation Boundaries
- The Authority Model
- The Dual-Layer Interaction Model
- outline.md §4.1: Foundation
- Decisions: ADR Registry
- Errata: FND-ERR Registry
