---
id: ai-overview
order: 26.9
title: "AI: Overview"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-problem, the-solution, the-invariants, the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, the-dual-layer-interaction-model, operating-model-overview, implementation-overview]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Dual-Layer Interaction Model
  - The Authority Model
  - Operating Model: Overview
  - Implementation: Overview
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; the AI section exists as a first-class peer)
  - DEC-804874 (D366 L-node semantic gate at session close; the one hard close-blocker depending on AI verdicts)
  - DEC-ebf0b4 (D268 Session Discipline and Data Integrity; the auditor agent reports against this discipline)
errata_referenced: []
v2_sources: []
diagrams: []
---

# AI: Overview

## Scope

This chapter is the section opener for AI. It states what AI is and what role it plays in the documentation, maps the six chapters that follow this overview into reading groups, gives a recommended reading sequence by audience, declares the boundaries between AI and the other sections of the documentation, and records the section-wide constraints that every AI chapter inherits.

This chapter does not redefine any AI claim. AI Architecture, Bedrock and Inference Profiles, AI Agents, AI Gates, AI Trust and Verification, and AI Usage Visibility each govern their own claims. Per pattern 87, this overview locates the chapters and routes the reader; it does not restate child-chapter behavior. Where the overview names a section-wide property, the governing source is `outline.md` (for documentation structure), the relevant Foundation chapter (for binding architectural authority), or the chapter that owns the property.

This chapter exists so that a reader who opens the AI section cold can locate any specific chapter without having read the others, and so that a reader who has finished AI can hold the six chapters that follow as one coherent set rather than as six independent files.

**Governing source.** outline.md §4.4.

## What AI Means

AI is the descriptive authority for the platform's AI surface: the bc-ai service, the agents and gates the service hosts, the model substrate the agents consume, the trust posture the verdicts carry, and the visibility surface the platform exposes for the operators and tenants who consume the verdicts. Per the Dual-Layer Interaction Model, AI participation runs on the Conversation surface and not on the Trust surface; AI does not produce authoritative state, and AI verdicts that feed the Trust surface (the L-node semantic gate at session close per DEC-804874) are recorded inputs to gates rather than authoritative state themselves.

| Property | Operational form |
|---|---|
| Conversation-surface only | AI runs as a verification surface and as a recommendation surface; the platform's authoritative state (Source Objects, Canonical Objects, Metric Snapshots, Action Objects, Evidence, Lineage) is produced at the four governed boundary acts and is owned by Operating Model: Evidence and Lineage. AI does not write authoritative state |
| Cross-family discipline by design | Governed AI acts use the maker-checker-gate pattern. Registry grounding shows both cross-family and same-family pairings in the readiness baseline. AI Trust and Verification records the target discipline and the drift. |
| As-built and gaps | Per pattern 69, every AI chapter that surveys a substrate maintains a drift inventory; the AI substrate is at varying maturity (the maker-checker-gate triplets are wired, the housekeeping agents are wired, the auditor is wired and advisory, the tenant-facing visibility surface is largely absent) and the chapters record the variance honestly |
| Gate-recorded but not gate-blocking by default | Most AI verdicts are advisory; only the L-node semantic gate per DEC-804874 is a hard close-blocker. AI Gates records the gate consumption posture; AI Architecture records the broader substrate |
| Cost-bounded with provider gaps | Bedrock and direct Anthropic calls enforce the daily budget cap and write `budget_log`; Gemini calls log tokens only and do not write cost rows in the readiness baseline. Bedrock and Inference Profiles records the budget boundary and gap. |

The Conversation-surface commitment is the section's defining trait. A reader who finds an apparent contradiction between an AI verdict and the platform's authoritative state should treat the authoritative state as binding; the AI verdict is a verification or a recommendation, not the source of truth.

**Governing source.** outline.md §4.4; The Dual-Layer Interaction Model; The Authority Model.

## The Six Chapters That Follow

The AI section has seven chapters: this overview plus the six chapters that follow. The grouping below is for navigation; the owning chapter governs each cluster's substantive claims per pattern 87.

| Group | Chapters | Group role |
|---|---|---|
| Substrate | AI Architecture; Bedrock and Inference Profiles | Navigation entry for the AI service architecture and the model substrate. AI Architecture owns the patterns; Bedrock and Inference Profiles owns the model substrate |
| Inventory | AI Agents | Navigation entry for the agent inventory at the cluster level. AI Agents owns the per-agent role and entity scope |
| Consumption | AI Gates | Navigation entry for the verdict response shape and the consumption posture. AI Gates owns the gate's authority over runtime decisions |
| Trust | AI Trust and Verification | Navigation entry for the cross-family discipline and the implicit trust ladder. AI Trust and Verification owns the trust posture each verdict carries |
| Surface | AI Usage Visibility | Navigation entry for the tenant-facing transparency surface. AI Usage Visibility owns the surface's current absence and the queued hardening |

The five groups cover the six chapters that follow without overlap. A chapter that does not fit a group is a chapter that does not belong in AI.

**Governing source.** outline.md §4.4.

## Reading Sequence

The six chapters that follow are written so they can be read in outline order, but the section also supports audience-specific reading paths. The order below is intentional: each later chapter assumes the prior chapters' definitions where they share a common substrate.

| Reader intent | Recommended sequence | Why |
|---|---|---|
| Architectural orientation | AI Architecture, then the rest in outline order | AI Architecture is the section's binder; reading it first gives the patterns (maker-checker-gate, housekeeping, auditor) that the model substrate, the agent inventory, the gates, the trust ladder, and the visibility surface all reference |
| Engineering | AI Architecture; Bedrock and Inference Profiles; AI Agents; AI Gates; AI Trust and Verification; AI Usage Visibility | Engineering reads the patterns and the substrate first to know what the service does and how, then the agents to know what's wired, then the gates and the trust to know how the platform consumes the verdicts, then visibility to know what the user sees |
| Operations | AI Architecture; Bedrock and Inference Profiles; AI Agents; AI Gates | Operations reads the patterns, the substrate (including the budget controls), the agent inventory, and the gate consumption posture; the trust ladder and the visibility surface follow as relevant to operational concerns |
| Audit and compliance | AI Trust and Verification; AI Gates; AI Architecture; AI Agents; AI Usage Visibility; Bedrock and Inference Profiles | Audit reads the trust posture first (cross-family discipline, the trust ladder, the auditor's place on the ladder), then the gates that consume the verdicts, then the architecture and agents that produce them, then the visibility surface and the substrate as supporting context |
| Frontend | AI Usage Visibility; AI Architecture; AI Agents; AI Trust and Verification | Frontend reads the user-facing surface first to know what is exposed in the readiness baseline and what is queued, then the architecture and agents to understand the substrate behind the surface, then the trust posture to know what trust signal the surface should expose |

The reading sequences do not reorder the chapters in the section. They guide a reader who needs to extract a coherent subset for a specific purpose.

**Governing source.** outline.md §4.4.

## Boundaries with Other Sections

AI describes the platform's AI surface. The boundaries with the other sections are explicit: Foundation and Operating Model bind AI; Implementation, Development, Onboarding, Operations, and Compliance consume AI when they reference the AI surface.

| Section | Boundary role | What crosses the boundary |
|---|---|---|
| Foundation | Binds AI as locked authority | AI chapters cite the Dual-Layer Interaction Model, the Object Model, the Contract Grammar, the Authority Model, and the Invariants as already-defined authority. AI runs on the Conversation surface; AI does not redefine Foundation |
| Operating Model | Binds AI as locked authority | AI chapters cite the contract-execution runtime, Evidence and Lineage, Quality Gates and Chain Integrity, and Tenant Entitlement Enforcement as already-defined runtime authority. AI verdicts feed gates that are owned by Operating Model; AI does not redefine Operating Model |
| Implementation | Consumes AI when Implementation references the AI surface | The Implementation: Backend Services and Auxiliary Services chapters describe bc-ai's deployable shape; the Audit and Activity Logging chapter describes the auditor verdict's substrate; the Frontend Experience chapter describes the AI Assistant Drawer's shell; the Notifications and Webhooks chapter describes the queued notification surface that may surface AI events |
| Development | Consumes AI when Development references the AI surface | Development chapters cite the AI service for the test substrates that exercise it; the AI section does not own development tooling |
| Onboarding | Consumes AI when Onboarding references the AI surface | Onboarding sequences that invoke maker-checker-gate triplets (the cc-field-audit gate during contract creation, for example) cite the AI section for the verdict semantics; the AI section does not own onboarding sequences |
| Operations | Consumes AI when Operations references the AI surface | Operations chapters cite Bedrock and Inference Profiles for budget concerns, AI Architecture for service-level deployable shape, AI Trust and Verification for verification cadence concerns; the AI section does not own operational procedures |
| Compliance | Consumes AI when Compliance references the AI surface | Compliance chapters cite AI Trust and Verification for the cross-family discipline as a control, AI Usage Visibility for the per-tenant transparency surface, and Audit and Activity Logging for the auditor's verdict trail. Compliance reports conformance against AI; it does not produce AI authority |

The dependency direction is explicit. Foundation and Operating Model bind AI; the rest of the documentation consumes AI.

**Governing source.** outline.md §4.4; The Authority Model; Operating Model: Overview; Implementation: Overview.

## Cross-Cutting Concerns

Several concerns thread through multiple AI chapters. The cross-cutting nature is intentional; each concern is named where it is owned and the table routes the reader without restating the substantive claim.

| Concern | Chapters that thread it | How to follow it |
|---|---|---|
| Cross-family discipline | AI Architecture; AI Agents; AI Trust and Verification | Follow AI Trust and Verification for the discipline's rationale; AI Architecture and AI Agents for how it is realized in the readiness baseline |
| Budget and cost | Bedrock and Inference Profiles; AI Usage Visibility | Follow Bedrock and Inference Profiles for the daily budget cap and the per-call cost recording; AI Usage Visibility for the per-tenant aggregation gap |
| Verdict persistence | AI Architecture; AI Gates; AI Trust and Verification; Audit and Activity Logging (Implementation section) | Follow AI Architecture for the substrate inventory; AI Gates for the bc-core-side persistence; Audit and Activity Logging for the cross-service push to DevHub |
| Conversation-surface commitment | AI Trust and Verification; AI Architecture; The Dual-Layer Interaction Model (Foundation) | Follow Foundation for the commitment; AI Trust and Verification for the trust ladder that respects it |
| Provider routing | AI Architecture; Bedrock and Inference Profiles | Follow AI Architecture for the per-call provider branching; Bedrock and Inference Profiles for the model registry that drives it |
| Tenant-facing visibility | AI Usage Visibility; AI Trust and Verification; Frontend Experience (Implementation section) | Follow AI Usage Visibility for the surface's current absence; AI Trust and Verification for the trust posture that should be exposed; Frontend Experience for the broader frontend |

A chapter that introduces a new claim about any cross-cutting concern aligns with the threading discipline. A later section that consumes an AI chapter consumes the cross-cutting concern as the chapter states it.

**Governing source.** The owning AI chapters named in the table; The Authority Model; Foundation; Operating Model: Overview.

## Constraints

The constraints below apply to AI as a whole and are inherited by every chapter in the section.

| Constraint | Operational form |
|---|---|
| AI runs on the Conversation surface | Per the Dual-Layer Interaction Model, AI does not produce authoritative state. AI verdicts are recorded inputs to gates and to operator-and-tenant-facing surfaces; the platform's authoritative state is produced at the four governed boundary acts |
| Cross-family discipline by design | Governed AI acts use maker-checker-gate triplets. Cross-family maker/checker pairing is the target discipline; current registry coverage is partial and must be recorded as drift until runtime enforcement exists. Explicit carve-outs do not feed governed gates. |
| Drift inventory is mandatory | Per pattern 69, every AI chapter that surveys a substrate maintains a drift inventory that records gaps between design intent and current state explicitly |
| Substrate-canonicality scope matches drift inventory | Per pattern 81, when a chapter spans multiple substrates of varying maturity, the chapter's lead-paragraph scope statement matches the drift inventory |
| Behavior-search grounding for any cross-service claim | Per pattern 71, an AI chapter that asserts behavior across the bc-ai-to-bc-core or bc-ai-to-DevHub boundary verifies the claim against both ends of the API surface |
| Persistence-claim precision | Per pattern 86, when a chapter says an AI verdict creates a record, writes to a table, persists a value, or maintains a durable ledger, the chapter verifies the actual write path, the FK constraints, and the raise-vs-warn semantics |
| Bidirectional citation discipline | Per the chapter-Scope frontmatter discipline, every `DEC-xxxxxx` and `FND-ERR-xxx` cited in body appears in frontmatter `governing_adrs` or `errata_referenced`, and vice versa; the Governing Decisions table is bidirectionally complete with frontmatter and body citations per pattern 77 |
| Deploy-specific figures belong elsewhere | Per pattern 85, an AI chapter does not embed specific port numbers, AWS account identifiers, IAM role ARNs, region codes, profile names, or other deploy-time figures; those figures are owned by Infrastructure |
| Voice and vocabulary discipline | Forbidden vocabulary scrub per outline §2.6; no em dashes; no chapter numbers; section-mark byte integrity per pattern 84; the eighty-seven voice patterns in `aws-rewrite-checklist.md` apply to every chapter |
| Section-overview locates, does not restate | Per pattern 87, this overview's tables identify each chapter's group role and route the reader to the owning chapter; the overview does not restate child-chapter behavior |

A chapter that violates any of these constraints is incorrect against the section's discipline.

**Governing source.** The Authority Model; outline.md §4.4; `scripts/reference/aws-rewrite-checklist.md`.

## Governing Decisions

The table below records the ADRs that govern the section shape or the cross-cutting concerns named by this overview. The rows are bounded because this chapter locates the concerns; the substantive AI behavior remains in the owning chapters.

| Decision | Scope in this overview | Boundary |
|---|---|---|
| DEC-c06f41 | Establishes the eight-section spine plus home and the AI section that includes this overview and the six following chapters | Governs documentation structure only; child chapters own their AI claims |
| DEC-804874 | Supplies the L-node semantic gate at session close as the one hard close-blocker that depends on AI verdicts; AI Gates routes the consumption posture | This overview routes the concern; AI Gates and Audit and Activity Logging own the gate's authority |
| DEC-ebf0b4 | Supplies the session-discipline rules the auditor agent reviews against; AI Agents owns the auditor's role | This overview routes the concern; AI Agents and Audit and Activity Logging own the auditor's substrate |

**Governing source.** Decisions: ADR Registry; outline.md §4.4.

## References

- AI Architecture
- Bedrock and Inference Profiles
- AI Agents
- AI Gates
- AI Trust and Verification
- AI Usage Visibility
- Foundation: Overview
- The Dual-Layer Interaction Model
- Operating Model: Overview
- Implementation: Overview
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-804874: L-node semantic gate (D366)
- DEC-ebf0b4: Session Discipline and Data Integrity (D268)
- outline.md §4.4: AI
- Decisions: ADR Registry
