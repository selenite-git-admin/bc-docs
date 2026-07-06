---
id: implementation-overview
order: 15.9
title: "Implementation: Overview"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-problem, the-solution, the-invariants, the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, the-dual-layer-interaction-model, operating-model-overview]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Authority Model
  - Operating Model: Overview
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; Implementation reshape into twelve chapters)
  - DEC-376587 (Section rename from "The Platform" to "Implementation")
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules; the two-database split as cross-cutting concern)
  - DEC-771baf (Tenant database topology; platform-tenant one-way dependency; cross-cutting concern)
  - DEC-e50b83 (Master port reservation; cross-cutting concern across the deployable substrate)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Implementation: Overview

## Scope

This chapter is the section opener for Implementation. It states what Implementation is and what role it plays in the documentation, maps the eleven chapters that follow this overview into reading groups, gives a recommended reading sequence by audience, declares the boundaries between Implementation and the other sections of the documentation, and records the as-built discipline under which Implementation chapters are written.

This chapter does not redefine any Implementation claim. Architecture, Backend Services, Internal Modules, Auxiliary Services, Infrastructure, Data Model and Schema, API Surface, Frontend Experience, Notifications and Webhooks, Audit and Activity Logging, and Synthetic Data and Testing each govern their own claims. This overview locates them; it does not restate them with authority. Where this overview names a section-wide property, the governing source is the outline that records Implementation's structure or the chapter that owns the property.

This chapter exists so that a reader who opens Implementation cold can locate any specific chapter without having read the others, and so that a reader who has finished Implementation can hold the eleven chapters that follow as one coherent set rather than as eleven independent files.

**Governing source.** outline.md §4.3.

## What Implementation Means

Implementation is the descriptive authority for the platform's built artifact. Where Foundation defines the architectural rules (locked, normative, section-independent) and Operating Model defines the contract-execution runtime (locked, normative, dependent on Foundation), Implementation describes how the platform realizes those rules and that runtime in code, services, infrastructure, databases, APIs, browser shells, and the cross-cutting platform features that lean on them.

| Property | Operational form |
|---|---|
| Descriptive | Implementation chapters describe what the platform actually is at the time of writing, not what the spec demands. The spec is owned by Foundation and Operating Model; Implementation reports the realization. |
| As-built and gaps | Per pattern 69, every Implementation chapter that surveys a substrate maintains a drift inventory that records gaps between design intent and current state explicitly. The chapter does not present an aspirational topology as if it were the as-built. |
| Maturity-graded | Per pattern 81, when a chapter spans multiple substrates of varying maturity (canonical, functional, scaffolded, aspirational), the chapter's lead-paragraph scope statement matches the chapter's own drift inventory. The chapter does not overstate the substrate's coverage. |
| Foundation-and-Operating-Model-bound | Every Implementation chapter consumes Foundation and Operating Model as locked authority. An Implementation claim that contradicts a Foundation invariant or an Operating Model rule is incorrect against the platform's architecture, regardless of what the code happens to do. Code that drifts from the spec is recorded as drift, not as redefinition. |
| Section-internal independence | Implementation chapters do not depend on AI, Development, Onboarding, Operations, or Compliance for their own correctness. Where an Implementation chapter touches a topic owned by a later section, the boundary is named explicitly and the topic is signposted to its owning section. |

The as-built and drift discipline is the section's defining trait. A reader who finds an apparent inconsistency between an Implementation chapter and the code in the relevant repository should treat the inconsistency as a signal that the chapter or the code has drifted; the resolution is either to update the chapter to reflect reality or to record the gap as drift, never to silently align the chapter with an aspirational reading.

**Governing source.** outline.md §4.3; The Authority Model.

## The Eleven Chapters That Follow

Implementation has twelve chapters: this overview plus the eleven chapters that follow. The grouping below is for navigation; section order is fixed by the outline and by chapter dependencies.

| Group | Chapters | What the group covers |
|---|---|---|
| Spine | Architecture | Navigation entry for the section's conceptual map, diagram set, layer model, two-database split, and service composition. The Architecture chapter owns the platform claims. |
| Deployable substrate | Backend Services; Internal Modules; Auxiliary Services; Infrastructure | Navigation entry for the service, module, auxiliary-deployable, and hosting chapters. Those chapters own the deployable-substrate claims and their drift inventories. |
| Contracts the substrate exposes | Data Model and Schema; API Surface | Navigation entry for the durable storage and HTTP-surface chapters. Data Model and Schema owns schema facts; API Surface owns route, guard, envelope, validation, pagination, and error-shape facts. |
| Consumers | Frontend Experience | Navigation entry for the browser-shell chapter. Frontend Experience owns the bc-admin and bc-portal maturity notes, implementation claims, and inherited-grounding caveats. |
| Platform-feature surfaces | Notifications and Webhooks; Audit and Activity Logging; Synthetic Data and Testing | Navigation entry for the cross-cutting feature chapters. Each chapter owns its as-built status, drift inventory, and boundary claims. |

The five groups cover the eleven chapters that follow without overlap. A chapter that does not fit a group is a chapter that does not belong in Implementation.

**Governing source.** outline.md §4.3.

## Reading Sequence

The eleven chapters that follow are written so they can be read in outline order, but the section also supports audience-specific reading paths. The order below is intentional: each later chapter assumes the prior chapters' definitions where they share a common substrate.

| Reader intent | Recommended sequence | Why |
|---|---|---|
| Architectural orientation | Architecture, then the rest in outline order | Architecture is the spine; reading it first gives the conceptual model that the deployable substrate, the contracts, the consumers, and the platform-feature chapters all reference. |
| Engineering | Architecture; Backend Services; Internal Modules; Data Model and Schema; API Surface; Infrastructure; the remaining chapters as needed | Engineering reads the spine and the deployable units first to know what runs where, then the schema and API surface to know what the runtime exposes, then infrastructure to know the runtime's hosting, then the platform-feature chapters as topics arise. |
| Operations | Architecture; Infrastructure; Backend Services; Auxiliary Services; Audit and Activity Logging; the remaining chapters as needed | Operations reads the spine and the hosting first, then the deployables that run there, then the operational audit substrate that records what happened. The platform-feature surfaces (Notifications, Synthetic Data) follow as relevant to the operational concern. |
| Audit and compliance | Architecture; Audit and Activity Logging; Data Model and Schema; API Surface; the remaining chapters as needed | Audit reads the topology, the operational governance trail, the schema (for evidence preservation), and the API surface (for the contract Audit and Activity Logging records). The other chapters provide context but the audit substrate is the authoritative trail. |
| Frontend | Frontend Experience; API Surface; Backend Services; Infrastructure (for the Cognito and port surfaces); the remaining chapters as needed | Frontend reads its own chapter first, then the API surface it consumes, then the backend services that host that surface, then the infrastructure that authenticates the user. |

The reading sequences do not reorder the chapters in the section. They guide a reader who needs to extract a coherent subset for a specific purpose.

**Governing source.** outline.md §4.3.

## Boundaries with Other Sections

Implementation describes the built artifact. The boundaries with the other sections are explicit and one-way: Foundation and Operating Model bind Implementation; AI, Development, Onboarding, Operations, and Compliance consume Implementation when they reference the realized platform.

| Section | Boundary role | What crosses the boundary |
|---|---|---|
| Foundation | Binds Implementation as locked authority | Implementation chapters cite Invariants, the Object Model, the Contract Grammar, the Evaluation Boundaries, the Authority Model, and the Dual-Layer Interaction Model as already-defined authority. Implementation realizes Foundation; it does not redefine Foundation. |
| Operating Model | Binds Implementation as locked authority | Implementation chapters cite the contract-execution runtime, Evidence and Lineage, Tenancy and Binding, the Quality Gates and Chain Integrity surface, and the rest of Operating Model as already-defined runtime authority. Implementation realizes Operating Model; it does not redefine Operating Model. |
| AI | Consumes Implementation when AI references the realized platform | AI chapters cite Backend Services and Auxiliary Services for bc-ai's deployable shape, Audit and Activity Logging for the AI auditor's verdict trail, and the API surface for AI gate authoring. AI's contract grammar (provisional family) is owned by Operating Model; AI's runtime semantics are owned by AI itself. Implementation describes the deployable substrate AI runs on; AI describes the AI surface specifically. |
| Development | Consumes Implementation when Development references the realized platform | Development chapters cite Backend Services for DevHub's deployable shape, the API surface for DevHub's MCP and HTTP endpoints, Audit and Activity Logging for the change-record substrate, and Infrastructure for the dev-environment substrate. Development describes the engineering practice and tooling around Implementation; it does not redefine Implementation. |
| Onboarding | Consumes Implementation when Onboarding references the realized platform | Onboarding chapters cite the API surface for the contract-creation endpoints, Data Model and Schema for the registry table shape, Audit and Activity Logging for the change-record discipline, and Synthetic Data and Testing for the bc-sdg integration that exercises new contracts. Onboarding describes governed sequences against Implementation; it does not redefine Implementation. |
| Operations | Consumes Implementation when Operations references the realized platform | Operations chapters cite Infrastructure for the hosting topology, Audit and Activity Logging for the operational governance trail, Backend Services for service-level deployables, and the platform-feature chapters for runtime concerns that operators interact with. Operations describes running the platform; it does not redefine Implementation. |
| Compliance | Consumes Implementation when Compliance references the realized platform | Compliance chapters cite Audit and Activity Logging for the ISO 27001 plan-and-report substrate, Data Model and Schema for evidence preservation, the API surface for authentication boundaries, and Infrastructure for the AWS account and region scope. Compliance reports conformance against Implementation; it does not produce Implementation authority. |

The dependency direction is one-way. An Implementation chapter that depends on a later section for its own correctness is a boundary violation. A later section that redefines an Implementation surface instead of consuming it is also a boundary violation.

**Governing source.** outline.md §4.3; The Authority Model; Operating Model: Overview.

## Cross-Cutting Concerns

Several concerns thread through multiple Implementation chapters. The cross-cutting nature is intentional; the concerns are stated in each chapter where they apply rather than centralized in one chapter that the others would then need to consult separately.

| Concern | Chapters that thread it | How it is preserved |
|---|---|---|
| The two-database split | Architecture; Backend Services; Infrastructure; Data Model and Schema; Audit and Activity Logging | Follow DEC-1918d0 and DEC-771baf first, then the owning chapters for the current realization and drift inventory. |
| Tenant scope | Architecture; Internal Modules; API Surface; Frontend Experience; Audit and Activity Logging; Synthetic Data and Testing | Follow DEC-771baf and the owning chapters for route scope, tenant context, browser headers, audit placement, and qa-bench discipline. |
| Audit substrate | Backend Services; Audit and Activity Logging; Development chapters covering decision-and-change governance (queued) | Follow Audit and Activity Logging for the as-built governance trail. Later Development chapters may consume the substrate but do not govern Implementation. |
| Port reservation | Architecture; Backend Services; Auxiliary Services; Infrastructure; Synthetic Data and Testing | Follow DEC-e50b83 and Infrastructure for the reservation. Feature chapters record bounded drift without embedding deploy coordinates in this overview. |
| ISO 27001 framing | Audit and Activity Logging; Backend Services; Compliance: ISO 27001 Conformance, queued | Follow Audit and Activity Logging for the Implementation framing. The formal control map is deferred to the Compliance section. |
| Foundation invariant respect | Every Implementation chapter that touches a runtime act | Follow Foundation and Operating Model for the binding rules; each Implementation chapter records any as-built drift in its own scope. |

A chapter that introduces a new claim about any cross-cutting concern aligns with the threading discipline. A later section that consumes an Implementation chapter consumes the cross-cutting concern as the chapter states it.

**Governing source.** The owning Implementation chapters named in the table; The Authority Model; Foundation; Operating Model: Overview; DEC-1918d0; DEC-771baf; DEC-e50b83.

## Constraints

The constraints below apply to Implementation as a whole and are inherited by every chapter in the section.

| Constraint | Operational form |
|---|---|
| Implementation is descriptive, not normative | Implementation chapters describe what the platform actually is. The spec is owned by Foundation and Operating Model. An Implementation claim that contradicts the spec is recorded as drift, never as redefinition of the spec. |
| Drift inventory is mandatory | Per pattern 69, every Implementation chapter that surveys a substrate maintains a drift inventory that records gaps between design intent and current state explicitly. The chapter does not present an aspirational topology as if it were the as-built. |
| Substrate-canonicality scope matches drift inventory | Per pattern 81, when a chapter spans multiple substrates of varying maturity (canonical, functional, scaffolded, aspirational), the chapter's lead-paragraph scope statement matches the chapter's own drift inventory. A canonical claim that the chapter's own subsequent sections immediately contradict is internal incoherence. |
| Behavior-search grounding for Foundation-invariant claims | Per pattern 71, an Implementation chapter that asserts a Foundation invariant about runtime behavior verifies the claim against the code path. A name-based search alone is not sufficient grounding. |
| Bidirectional citation discipline | Per the chapter-Scope frontmatter discipline, every `DEC-xxxxxx` and `FND-ERR-xxx` cited in body appears in frontmatter `governing_adrs` or `errata_referenced`, and vice versa. The Governing Decisions table is bidirectionally complete with frontmatter and body citations per pattern 77. |
| Adjacency in Scope implies dependency in frontmatter | Per pattern 78, when a chapter's Scope says "this chapter sits between X and Y" or names a prior chapter as a governing source, the prior chapter appears in `depends_on` and `governing_sources`. Per pattern 83 (the inverse), the frontmatter does not list governing sources that the body does not substantively cite. |
| Deploy-specific figures belong in Infrastructure or Operations | Per pattern 85, an Implementation chapter outside Infrastructure and Operations does not embed specific port numbers, AWS account identifiers, IAM role ARNs, region codes, profile names, or other deploy-time figures. Those figures are owned by Infrastructure (deployed-surface record) or Operations: Deployment Topology when drafted. |
| Persistence-claim precision | Per pattern 86, when a chapter says an endpoint creates a record, writes to a table, persists a value, or maintains a durable ledger, the chapter verifies the actual write path, the FK constraints, and the raise-vs-warn semantics. A persistence claim that the implementation does not honor creates a guarantee reviewers depend on falsely. |
| Voice and vocabulary discipline | Forbidden vocabulary scrub per outline §2.6; no em dashes; no chapter numbers; section-mark byte integrity per pattern 84; the eighty-six voice patterns in `aws-rewrite-checklist.md` apply to every chapter. |

A chapter that violates any of these constraints is incorrect against the section's discipline.

**Governing source.** The Authority Model; outline.md §4.3; `scripts/reference/aws-rewrite-checklist.md`.

## Governing Decisions

The table below records the ADRs that govern the section shape or the cross-cutting concerns named by this overview. The rows are bounded because this chapter locates the concerns; the substantive platform behavior remains in the owning chapters.

| Decision | Scope in this overview | Boundary |
|---|---|---|
| DEC-c06f41 | Establishes the eight-section spine plus home and the Implementation section shape that includes this overview and the eleven following chapters | Governs documentation structure only; child chapters own their platform claims |
| DEC-376587 | Renames the former Platform section to Implementation | Governs section naming only; does not change platform behavior |
| DEC-1918d0 | Supplies the two-database split as a cross-cutting concern readers will see across Architecture, Infrastructure, Data Model and Schema, and Audit and Activity Logging | This overview routes the concern; it does not restate database behavior as authority |
| DEC-771baf | Supplies tenant database topology and the platform-tenant dependency direction used by several Implementation chapters | This overview routes the concern; the owning chapters record the as-built tenant behavior and drift |
| DEC-e50b83 | Supplies the master port-reservation concern that Infrastructure and deployable-substrate chapters consume | This overview routes the concern without embedding deploy-specific figures |

**Governing source.** Decisions: ADR Registry; outline.md §4.3.

## References

- Architecture
- Backend Services
- Internal Modules
- Auxiliary Services
- Infrastructure
- Data Model and Schema
- API Surface
- Frontend Experience
- Notifications and Webhooks
- Audit and Activity Logging
- Synthetic Data and Testing
- Foundation: Overview
- Operating Model: Overview
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-376587: Section rename from "The Platform" to "Implementation"
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-e50b83: Master port reservation
- outline.md §4.3: Implementation
- Decisions: ADR Registry
