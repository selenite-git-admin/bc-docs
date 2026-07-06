---
id: development-overview
order: 37.9
title: "Development: Overview"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-problem, the-solution, the-invariants, the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, the-dual-layer-interaction-model, operating-model-overview, implementation-overview, ai-overview]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Authority Model
  - Operating Model: Overview
  - Implementation: Overview
  - AI: Overview
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus a home; Development section shape)
  - DEC-376587 (Section renames; Development as the section name for engineering practice and tooling)
  - DEC-a4e550 (ADR-First Decision Workflow; the Decision and Change Procedure chapter consumes it)
  - DEC-633b2a (D-code monotonic allocator; the Decision and Change Procedure chapter records it)
  - DEC-623f8f (ADR Hygiene Policy; the Decision and Change Procedure chapter records the eight rules)
  - DEC-ebf0b4 (Session Discipline and Data Integrity Rules; threads through DevHub, Decision and Change Procedure, and Developer Experience)
  - DEC-804874 (L-Node Verification with Semantic Family Classification; the DevHub session-close gate)
  - DEC-ee6018 (bc-qa standalone repo; the Quality Assurance chapter records it)
  - DEC-3395bc (bc-docs-v3 SSOT cutover; the Documentation System chapter records it)
  - DEC-b97390 (bc-admin embedded reader; the Documentation System chapter records it)
  - DEC-890417 (pm2 service supervisor; superseded; the Build and Release chapter records the as-built model)
  - DEC-1918d0 (Two-database split; the Build and Release chapter records the canonical DDL location)
  - DEC-e50b83 (Port reservation; the Build and Release and Developer Experience chapters record the discipline)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Development: Overview

## Scope

This chapter is the section opener for Development. It states what Development is and what role it plays in the documentation, maps the six chapters that follow this overview into reading groups, gives a recommended reading sequence by audience, declares the boundaries between Development and the other sections of the documentation, names the cross-cutting concerns that thread the section's chapters, and records the constraints under which Development chapters are written.

This chapter does not redefine any Development claim. DevHub, Decision and Change Procedure, Build and Release, Quality Assurance, Documentation System, and Developer Experience each govern their own claims. This overview locates them; it does not restate them with authority. Where this overview names a section-wide property, the governing source is the outline that records Development's structure or the chapter that owns the property.

This chapter exists so that a reader who opens Development cold can locate any specific chapter without having read the others, and so that a reader who has finished Development can hold the six chapters that follow as one coherent set rather than as six independent files.

**Governing source.** outline.md §4.5.

## What Development Means

Development is the descriptive authority for the engineering practice that maintains and evolves the platform. Where Foundation defines the architectural rules, Operating Model defines the contract-execution runtime, Implementation describes the built artifact, AI describes the AI surface, Onboarding describes the governed sequences that build the platform up, Operations describes how the platform runs day-to-day, and Compliance reports against the platform's preserved state, Development describes how the platform is built and changed.

| Property | Operational form |
|---|---|
| Engineering-facing | Development chapters describe the substrate the engineering team consumes: registries, decision tooling, build commands, QA gates, documentation tooling, agent harness. The audience is the engineer or the agent, not the runtime user |
| As-built and gaps | Per pattern 81, every Development chapter that surveys an engineering substrate maintains a drift inventory recording gaps between intended discipline and current state. Development does not present an aspirational engineering posture as if it were the as-built |
| Foundation-and-Authority-Model bound | Every Development chapter consumes Foundation and the Authority Model as locked authority. A Development claim that contradicts a Foundation invariant or an Authority-Model rule is incorrect against the platform's architecture, regardless of what the engineering practice happens to do |
| Section-internal sequencing | Development chapters depend on each other (the change procedure reads DevHub; the build chapter reads the QA tooling; the documentation chapter reads the SSOT; the developer experience chapter consumes all of them). The dependency direction is recorded in each chapter's prerequisites; this overview does not re-record it |
| Outside the runtime artifact | Development is not the runtime. Development describes the practice that produces the runtime. The runtime artifacts are owned by Implementation and Operating Model |

The as-built discipline is the section's defining trait. A reader who finds an aspirational claim in a Development chapter (a CI workflow, a release manifest, a coordinated reconciliation procedure) should treat it as a recorded gap if the chapter's drift inventory catches it, or as an undocumented gap to surface for the next cold-read. Development records the engineering practice represented by the readiness baseline.

**Governing source.** outline.md §4.5; The Authority Model.

## The Six Chapters That Follow

Development has seven chapters: this overview plus the six chapters that follow. The grouping below is for navigation; section order is fixed by the outline and by chapter dependencies.

| Group | Chapters | What the group covers |
|---|---|---|
| Engineering-coordination substrate | DevHub | Navigation entry for the DevHub MCP server and SQLite registry, the session and task lifecycle, the change-record and decision tables, the activity log, the L-node semantic gate at session close |
| Governance procedure | Decision and Change Procedure | Navigation entry for the ADR-first procedure, the canonical UID and D-code allocator, the ADR hygiene rules, the change-record plan-and-report pair, the D268 session-discipline rules |
| Build cycle | Build and Release | Navigation entry for the CodeArtifact registry routing, the per-repo dev commands, the build outputs, the docker compose substrate, the canonical DDL location, the seed scripts, the as-built CI gap |
| Quality enforcement | Quality Assurance | Navigation entry for the bc-qa repository, the audit harness, the gate-config severity matrix, the eslint-config package, the pre-commit hook, the QA NC register |
| Documentation tooling | Documentation System | Navigation entry for the bc-docs-v3 SSOT, the bc-admin embedded reader, the bc-core JWT-served document endpoints, the sync-docs manifest builder, the data-dictionary generator, the DevHub document scanner |
| Developer-machine substrate | Developer Experience | Navigation entry for the per-repo CLAUDE.md instruction surface, the SOP catalog, the .claude harness, the worktree harness, the verification surface, the port reservation discipline, the AWS profile discipline, the database change protocol |

The six groups cover the six chapters that follow without overlap. A chapter that does not fit a group is a chapter that does not belong in Development.

**Governing source.** outline.md §4.5.

## Reading Sequence

The six chapters can be read in outline order, but the section also supports audience-specific reading paths. The order below is intentional: each later chapter assumes the prior chapters' substrates where they share a common engineering concern.

| Reader intent | Recommended sequence | Why |
|---|---|---|
| Architectural orientation | DevHub; Decision and Change Procedure; Documentation System; the rest as needed | The architectural reader builds the engineering mental model from the registry substrate outward to the governance procedure and the documentation surface |
| Engineering | Developer Experience; Build and Release; Quality Assurance; the rest as needed | Engineering reads the developer-machine substrate first, then the build cycle, then the quality enforcement before tackling registry and governance detail |
| Operations or SRE | Decision and Change Procedure; DevHub; Build and Release; Quality Assurance; the rest as needed | Operations reads the change-record substrate first (to understand the discipline that produces the artifacts they operate against), then the registry that holds the records, then the build and quality cycle |
| Audit and compliance | Decision and Change Procedure; Quality Assurance; DevHub; Documentation System; the rest as needed | Audit reads the change-record discipline, the QA enforcement, the registry substrate, and the documentation tooling as the four primary control surfaces |
| New hire | Developer Experience; DevHub; Decision and Change Procedure; Documentation System; the rest as needed | A new hire reads the developer-machine setup first, then the engineering-coordination registry, then the governance procedure, then the documentation surface |

The reading sequences do not reorder the chapters in the section. They guide a reader who needs to extract a coherent subset for a specific purpose.

**Governing source.** outline.md §4.5.

## Boundaries with Other Sections

Development describes the engineering practice. The boundaries with other sections are explicit and one-way: Foundation, Operating Model, and Implementation bind Development; AI provides the AI surfaces Development governs; Onboarding consumes Development discipline; Operations consumes Development tooling; Compliance reports against the change-record and QA records that Development produces.

| Section | Boundary role | What crosses the boundary |
|---|---|---|
| Foundation | Binds Development as locked authority | Development chapters cite Invariants, the Authority Model, the Object Model as already-defined authority. Development describes how the platform is built; it does not redefine Foundation |
| Operating Model | Binds Development as locked authority | Development chapters cite the contract-execution runtime as the artifact the engineering practice produces and protects; the runtime semantics are owned by Operating Model |
| Implementation | Binds Development as locked authority | Development chapters cite Backend Services (DevHub, bc-core, bc-pg-mcp), Internal Modules, Auxiliary Services, Infrastructure, Data Model and Schema, API Surface as the artifacts the engineering practice produces |
| AI | Adjacent | AI chapters describe the AI participation in the platform; Development governs the AI engineering practice through the same change-record substrate; AI Trust and Verification consumes the QA gate substrate that Development records |
| Onboarding | Consumes Development discipline | Onboarding chapters cite the SOPs (Developer Experience), the change-record substrate (Decision and Change Procedure), and the documentation surface (Documentation System) as governance substrates |
| Operations | Consumes Development tooling | Operations chapters cite DevHub (the substrate Incident and Change Management uses), the change-record discipline (Decision and Change Procedure as the procedure Operations honors), the build cycle (the artifacts Operations deploys); Operations is not authored in Development |
| Compliance | Consumes Development records | Compliance chapters cite the change records as audit evidence, the QA NC register as preventive control evidence, and the ADR registry as decision authority; Compliance reports conformance against Development records, not against the Development discipline itself |

**Governing source.** outline.md §4.5; The Authority Model.

## Cross-Cutting Concerns

Several concerns thread the six Development chapters. The matrix below routes the reader to the chapter that owns each concern; per pattern 87, the matrix locates the concern and does not restate the behavior.

| Concern | Owning chapter | Adjacent chapters that thread it |
|---|---|---|
| Engineering session lifecycle | Decision and Change Procedure (the protocol authority) | DevHub (the registry substrate); Developer Experience (the agent-side discipline) |
| Activity log emission | Audit and Activity Logging in Implementation (the substrate authority) | DevHub (the per-domain event-type enumeration); Decision and Change Procedure (the change-record events) |
| AWS profile and CodeArtifact authentication | Infrastructure in Implementation (the deploy coordinate authority) | Build and Release (the renewal procedure); Developer Experience (the discipline) |
| Reserved port assignment | Infrastructure in Implementation (the deploy coordinate authority) | Build and Release (the per-repo dev commands that bind to reserved ports); Developer Experience (the launch.json that names the entries) |
| Bidirectional frontmatter discipline | Documentation System (the discipline) | Decision and Change Procedure (the ADR frontmatter shape); every chapter applies the discipline at draft time |
| Pre-commit and audit-harness rule set | Quality Assurance (the rule authority) | Build and Release (the package install through CodeArtifact); Developer Experience (the install-hooks invocation) |
| Database change governance | DevHub (the change-record substrate); Decision and Change Procedure (the protocol) | Build and Release (the canonical DDL location); Developer Experience (the database change protocol) |
| L-node semantic gate at session close | DevHub (the gate implementation); Decision and Change Procedure (the override discipline) | Operating Model: Chain Completeness and Verdict (the SSOT substrate the gate consumes) |
| ADR-first decision recording | Decision and Change Procedure (the procedure) | Documentation System (the file shape and the v3 layout); DevHub (the registry surface) |

The matrix is navigation. Following the cell to the owning chapter produces the chapter's substantive treatment; following the cell to an adjacent chapter produces the partial treatment that chapter carries.

**Governing source.** outline.md §4.5; per-chapter Boundaries with Other Chapters tables.

## Constraints

| Constraint | Form |
|---|---|
| Single SSOT for documentation | bc-docs-v3 per `DEC-3395bc`; legacy v2 archive is read-only archive |
| ADR-first | Every architectural decision lands as an ADR file before code changes per `DEC-a4e550` |
| Single QA authority | bc-qa per `DEC-ee6018`; no platform repo defines its own rule set |
| Single MCP harness | `barecount-devhub/.claude/settings.json` is the master MCP registration |
| Per-repo independence | Each service starts in its own repo; no platform-wide supervisor (pm2 superseded per `DEC-890417`) |
| Reserved ports | Every service binds to its reserved port per `DEC-e50b83`; the deploy-coordinate detail is owned by Infrastructure |
| Database changes are user-approved | The override of every permission mode |
| Voice discipline | Every chapter passes the AWS rewrite checklist's pre-commit grep before commit |
| Section-internal dependency direction | Decision and Change Procedure reads DevHub; Build and Release reads Quality Assurance; Documentation System reads Decision and Change Procedure; Developer Experience consumes all five |

**Governing source.** outline.md §2; outline.md §4.5; the constraints table on each chapter.

## Governing Decisions

The Development section rests on the ADRs below. Each row carries the bounded scope language per pattern 87.

| ADR | Title | Scope of governance over Development |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus a home | Governs documentation structure: Development is the fifth top-level section; this overview's chapter map and section composition derive from the spine |
| DEC-376587 | Section renames | Governs documentation structure: the section name "Development" replaces an earlier label; chapter slugs and section folder names follow |
| DEC-a4e550 | ADR-First Decision Workflow | Governs the Decision and Change Procedure chapter; the ADR file is SSOT and DevHub holds metadata |
| DEC-633b2a | D-code monotonic allocator | Governs the Decision and Change Procedure chapter; UID canonical, D-code nickname |
| DEC-623f8f | ADR Hygiene Policy | Governs the Decision and Change Procedure chapter; eight rules for the ADR lifecycle |
| DEC-ebf0b4 | Session Discipline and Data Integrity Rules | Governs the Decision and Change Procedure chapter and threads through DevHub and Developer Experience |
| DEC-804874 | L-Node Verification with Semantic Family Classification | Governs the DevHub session-close gate and the Decision and Change Procedure override discipline |
| DEC-ee6018 | bc-qa standalone repo | Governs the Quality Assurance chapter; bc-qa is the platform's QA authority |
| DEC-3395bc | bc-docs-v3 SSOT cutover | Governs the Documentation System chapter; bc-docs-v3 is the documentation source of truth |
| DEC-b97390 | bc-admin embedded reader | Governs the Documentation System chapter; the bc-admin reader is canonical |
| DEC-890417 | pm2 service supervisor (superseded) | Governs the Build and Release chapter; the as-built model starts each service independently |
| DEC-1918d0 | Two-database split | Governs the Build and Release chapter (canonical DDL location); threads through Developer Experience (database change protocol) |
| DEC-e50b83 | Port reservation | Governs the Build and Release and Developer Experience chapters; the deploy-coordinate detail is owned by Infrastructure |

This overview routes governance to the owning chapter. The bounded scope language above prevents this overview from claiming authority over the platform behavior the ADRs govern; the chapter that owns the topic carries the substantive treatment.

**Governing source.** outline.md §4.5; per-chapter `governing_adrs` frontmatter.

## References

- Foundation (the locked architectural authority)
- The Authority Model
- Operating Model: Overview
- Implementation: Overview
- AI: Overview
- DevHub
- Decision and Change Procedure
- Build and Release
- Quality Assurance
- Documentation System
- Developer Experience
- DEC-c06f41 (Spine expansion to eight sections plus a home)
- DEC-376587 (Section renames)
- DEC-a4e550 (ADR-First Decision Workflow)
- DEC-633b2a (D-code monotonic allocator)
- DEC-623f8f (ADR Hygiene Policy)
- DEC-ebf0b4 (Session Discipline and Data Integrity Rules)
- DEC-804874 (L-Node Verification with Semantic Family Classification)
- DEC-ee6018 (bc-qa standalone repo)
- DEC-3395bc (bc-docs-v3 SSOT cutover)
- DEC-b97390 (bc-admin embedded reader)
- DEC-890417 (pm2 service supervisor; superseded)
- DEC-1918d0 (Two-database split)
- DEC-e50b83 (Port reservation)
- bc-docs-v3 outline.md (section structure)
- bc-docs-v3 HANDOFF.md (current drafting state)
