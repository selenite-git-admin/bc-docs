---
id: platform-overview
order: 0
title: "Platform Overview"
status: drafting
authority: authoritative
depends_on: []
governing_sources:
  - Foundation (the locked architectural authority)
  - The Authority Model
  - Operating Model: Overview
  - Implementation: Overview
  - AI: Overview
  - Development: Overview
  - Onboarding: Overview
  - Operations: Overview
  - Compliance: Overview
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus a home; the documentation's structural authority)
  - DEC-376587 (Section renames; the canonical section names)
  - DEC-9c58c6 (Operating Model section name; the no-article register that the home overview honors when naming the section)
  - DEC-3395bc (bc-docs-v3 SSOT cutover; the documentation home that the bc-admin reader fetches against)
  - DEC-b97390 (bc-admin embedded reader is canonical; the home of the reader sidebar)
  - DEC-a4e550 (ADR-First Decision Workflow; the registry the documentation's Decisions peer holds)
  - DEC-ebf0b4 (Session Discipline and Data Integrity Rules; the engineering-session discipline the documentation's drafting workflow honors)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Platform Overview

## Scope

This chapter is the home of the reader sidebar. It states what BareCount is, names the eight top-level sections of the documentation, gives recommended reading paths by audience, declares the documentation's frontmatter state machine, names the voice and citation discipline that every chapter honors, and locates the reference materials that sit as governance peers under `docs/`.

This chapter does not redefine any platform claim. The section openers (Foundation: Overview, Operating Model: Overview, Implementation: Overview, AI: Overview, Development: Overview, Onboarding: Overview, Operations: Overview, Compliance: Overview) each navigate within their section; this home Platform Overview navigates across sections. Where this chapter names a section-wide property, the governing source is the section opener that owns the property or the outline that records the documentation's structure.

This chapter exists so that a reader who opens the documentation cold can locate any section without prior context, and so that a reader who has finished one section can hold the eight sections as one coherent set rather than as eight independent surfaces.

**Governing source.** outline.md §1; outline.md §4.

## What BareCount Is

BareCount is an enterprise data observation platform. It admits external state through governed Admission and Observation contracts, evaluates business meaning through governed Canonical Mapping, computes metrics through governed Metric Contracts, and records every step as immutable authoritative state with paired Evidence and Lineage.

The platform's central architectural commitment is that authoritative state is produced only at four governed evaluation boundaries (admission, canonical evaluation, metric evaluation, action evaluation), that every produced object carries Evidence emitted at the same act, and that no version of an authoritative object is ever altered. Corrections produce new versions; the original remains addressable. The Foundation chapters define the invariants and the object model; the Operating Model chapters define the contract-execution runtime; the Implementation chapters describe the built artifact; the remaining sections describe the AI surface, the engineering practice, the governed building procedures, the operational discipline, and the conformance posture.

The platform is not a generic ETL tool. The vocabulary it admits in body prose excludes pipeline, ingest, transform, materialize, flow, stage, job, refresh, recompute, and process. The vocabulary it preserves is observe, admit, evaluate, resolve, preserve, record, reference, bind, finalize, surface. The platform's correctness is a structural property of the contract grammar, not an operational property of any particular run.

**Governing source.** Foundation; The Invariants; The Object Model; The Contract Grammar; The Evaluation Boundaries.

## The Documentation's Shape

The documentation is one home plus eight top-level sections. The home is this Platform Overview. The eight sections are listed below in the canonical reader-sidebar order.

| Section | Chapters | What the section provides |
|---|---|---|
| Foundation | 9 (8 substantive plus the section opener) | The locked architectural authority: the problem, the solution, the invariants, the object model, the contract grammar, the evaluation boundaries, the authority model, the dual-layer interaction model |
| Operating Model | 17 (16 substantive plus the section opener) | The contract-execution runtime: sources, business vocabulary, contract chain assembly, quality gates, connectors and readers, admission and observation, canonical evaluation, metric evaluation, metric catalog, action evaluation, evidence and lineage, tenancy and binding, tenant extensions, tenant entitlement enforcement, fiscal time, chain completeness |
| Implementation | 12 (11 substantive plus the section opener) | The built artifact: architecture, backend services, internal modules, auxiliary services, infrastructure, data model and schema, API surface, frontend experience, notifications and webhooks, audit and activity logging, synthetic data and testing |
| AI | 7 (6 substantive plus the section opener) | The AI surface: AI architecture, Bedrock and inference profiles, AI agents, AI gates, AI trust and verification, AI usage visibility |
| Development | 7 (6 substantive plus the section opener) | Engineering practice and tooling: DevHub, decision and change procedure, build and release, quality assurance, documentation system, developer experience |
| Onboarding | 16 (15 substantive plus the section opener) | The governed building procedures: source registration, seed catalog management, metric seed catalog management, business field and business object onboarding, canonical field seeding, source and admission contract creation, observation contract creation, canonical contract creation, metric contract creation, reader creation, metric registration, MC chain integrity, data seeding and build order, multi-standard onboarding, tenant onboarding |
| Operations | 9 (8 substantive plus the section opener) | Running the platform day-to-day: tenant lifecycle and subscription, deployment topology, security operations, upgrade and migration, observability and telemetry, performance and scale, incident and change management, support and escalation |
| Compliance | 6 (5 substantive plus the section opener) | The conformance posture: InfoSec and access control, ISO 27001 conformance, SOC 2 conformance, privacy and the immutable fact, risk and vendor management |

The total is 84 chapters: 1 home plus 83 across the eight sections per `DEC-c06f41`. Section order is the canonical sidebar order; chapter order within a section is fixed by the section opener and by the chapter's `order` frontmatter field.

**Governing source.** outline.md §4; DEC-c06f41.

## Reading Paths by Audience

The documentation supports the audiences named by outline §1. Each audience has a recommended reading path that produces a coherent subset for a specific purpose.

| Audience | Sequence | Outcome |
|---|---|---|
| Architect | Foundation; Operating Model; selective chapters in Implementation; reference Decisions and Data Dictionary as needed | A complete mental model of the execution invariants, authoritative objects, evaluation boundaries, contract taxonomy, and authority model; capacity to evaluate a proposed change against the invariants |
| Developer | Operating Model; Implementation; reference Data Dictionary, the Contract Schemas reference (when built), and the API Reference (when built) | Working knowledge of how each component is built, what it exposes, and what it depends on; capacity to implement or modify a component without violating the invariants |
| Operator | Operations; selective chapters in Onboarding; reference the SOP Index (when built) and Decisions | The deployment topology, the telemetry, the incident protocols, and the escalation paths; capacity to run the platform, diagnose failures, and coordinate response |
| Auditor | Compliance; reference Decisions and Errata; selective chapters in Operations and in Audit and Activity Logging | The control mapping, the evidence sources, and the governance discipline; capacity to complete an ISO 27001 or SOC 2 engagement using preserved state alone |
| New hire | Foundation cover-to-cover; then the audience-specific path that matches the role | The vocabulary, the invariants, and the platform's core claim; capacity to participate in design conversations without rebuilding context from scratch |
| Enterprise buyer | Foundation; Compliance; selective chapters in Operating Model | The platform's thesis, the governance posture, and the compliance story; capacity to evaluate BareCount against internal standards |

The reading paths do not reorder the sections. They guide a reader who needs to extract a coherent subset for a specific purpose. The reference materials are for lookup and derive from the chapters; no audience reads them front-to-back.

**Governing source.** outline.md §1; outline.md §5.

## The Frontmatter State Machine

Every chapter and every governance file under `docs/` carries two orthogonal frontmatter axes. The two axes are never collapsed.

| `authority` | Meaning |
|---|---|
| `authoritative` | When this chapter or governance file reaches `status: locked`, its statements bind. Drafts and reviews have no binding force yet |
| `reference` | Explanatory material. Never binding by itself. Points to an authoritative source |
| `evidentiary` | Patent text, audit reports, historical records. Referenced for proof, not for operational decisions |

| `status` | Meaning |
|---|---|
| `drafting` | Being written. No binding force regardless of authority |
| `reviewing` | Mechanical gates pass. Awaiting founder cold-read. No binding force yet |
| `locked` | All gates cleared, founder approved. Binding if authority is `authoritative` |
| `superseded` | Replaced by a newer version. Carries `superseded_by` |
| `retired` | Withdrawn without replacement. Documented in the Errata Ledger |

Binding force equals `authority == authoritative` and `status == locked`. Any other combination is non-binding. The chapter that a reader follows for a specific platform behavior is binding only when both conditions hold.

**Governing source.** outline.md §2.

## Voice and Citation Discipline

Every chapter is written in a single voice across all sections. The discipline below is the floor; the AWS rewrite checklist (`scripts/reference/aws-rewrite-checklist.md`) refines and extends it through earned voice patterns from founder cold-reads of specific chapters.

| Discipline | Form |
|---|---|
| Tone | Neutral and declarative; third person; no `you`, `we`, or `I`; no contractions; no rhetorical questions; no narrative origin stories |
| Em dashes | None in titles, headings, or body prose; commas, colons, periods, semicolons, or parentheses substitute |
| Forbidden vocabulary | The ten roots `pipeline`, `ingest`, `transform`, `materialize`, `flow`, `stage`, `job`, `refresh`, `recompute`, `process` are forbidden in body prose; the carve-out for `upstream` and `downstream` admits DAG-direction terms on declared chains; protocol-vocabulary identifiers (such as `codeartifact:refresh` or "OAuth refresh token") are admissible inside backticks or as standards-vocabulary protocol identifiers |
| Section pattern | Behavior sections carry Purpose, Scope, Behavior, Constraints, Failure modes, and Governing source; component sections add Interactions |
| Citation discipline | Every substantive section ends with a `Governing source.` footer naming the authoritative references; queued chapters are not cited as governing source; `outline.md` is cited only for documentation-structure claims, not for system-behavior claims |
| Bidirectional frontmatter | Every `DEC-xxxxxx` and `FND-ERR-xxx` cited in body appears in `governing_adrs` or `errata_referenced`; every frontmatter-listed reference appears in body |
| Numbering | None in chapter titles, headings, or cross-references; chapters are name-keyed; only frontmatter `order` provides sort stability |
| Diagram discipline | Source format is SVG; bidirectional declaration in frontmatter `diagrams` and body references; prose is the spec, the diagram is the navigation aid |

The discipline is enforced by a pre-commit grep, by the founder cold-read, and by the earned voice patterns the checklist records.

**Governing source.** outline.md §2; `scripts/reference/aws-rewrite-checklist.md`.

## Reference Materials

The reference materials sit as first-class top-level peers under `docs/`. Each holds derived or governance content; none is a chapter; no audience reads any of them front-to-back.

| Reference | Path | Status |
|---|---|---|
| Decisions | `docs/adrs/` | Authoritative; ADRs created and governed via DevHub MCP tools per `DEC-a4e550`; the ADR file is the source of truth |
| Errata | `docs/errata/` | Authoritative; governed contradictions to Foundation; entries tracked by the errata register |
| Data Dictionary | `docs/data-dictionary/` | Reference; auto-generated from live PostgreSQL state by `scripts/generate-data-dictionary.mjs` |
| Contract Schemas | `docs/schemas/` (queued) | Reference; per-contract-family JSON schemas plus body pages |
| API Reference | `docs/api/` (queued) | Reference; per-endpoint request and response shape; generated from the DevHub API scanner |
| Screen Registry | `docs/screen-registry/` (queued) | Reference; per-screen route, layout, child screens, API consumption, auth scope; generated from DevHub when both frontends stabilize |
| SOP Index | `docs/sops/` (queued) | Reference; per-SOP governing chapter, prerequisites, steps, post-verification; migration from legacy v2 archive queued |
| Glossary | `docs/glossary/` (queued) | Reference; every defined term with its first-use chapter |
| Diagram Index | `docs/diagrams-index/` (queued) | Reference; every diagram with its source chapter |

The chapter is the authority for the rationale and the design intent; the reference is the authority for the inventory. Chapters describe; references enumerate.

**Governing source.** outline.md §4.9.

## Repository and Reader

The documentation lives at the bc-docs-v3 repository per `DEC-3395bc`. The bc-admin embedded reader is the canonical reader per `DEC-b97390`. The reader fetches manifest, Markdown, and assets from bc-core's JWT-guarded `/api/docs/*` endpoints; the bc-admin sync-docs script bridges bc-docs-v3 to bc-core's `private-docs/` directory; the bc-core docs controller serves the content with rate limiting, audit logging, and the anti-scraping discipline. Documentation System (within Development) records the substrate; this overview locates it.

The legacy `legacy v2 archive` repository is read-only archive. New chapters land in v3; the v2 SOPs migration is queued.

**Governing source.** Documentation System; DEC-3395bc; DEC-b97390.

## Constraints

| Constraint | Form |
|---|---|
| Eight top-level sections plus one home | Per `DEC-c06f41`; replaces prior Part I-V framing; replaces prior six-section spine |
| No chapter numbering | Chapters are name-keyed; H1 has no `Chapter N` prefix; H2 has no `N.N`; cross-references use names |
| Single voice across all sections | Per outline §2; the AWS rewrite checklist is the refining authority |
| Bidirectional frontmatter | Every `DEC-xxxxxx` cited in body appears in `governing_adrs`; every frontmatter-listed reference appears in body |
| No deploy-specific figures in feature chapters | Port numbers, AWS account identifiers, region codes, profile names, IAM ARNs route to Infrastructure or Operations: Deployment Topology per pattern 85 |
| Section openers locate, do not restate | Per pattern 87; this home overview applies the same discipline at the documentation level |
| ADR file is canonical | DevHub holds metadata; the ADR file under `docs/adrs/` is the source of truth per `DEC-a4e550` |
| The platform's correctness is structural | The contract grammar is the platform's discipline; correctness emerges from the invariants, not from any particular run |

**Governing source.** outline.md §2; outline.md §4; DEC-c06f41; DEC-a4e550.

## Governing Decisions

The documentation rests on a small set of structural decisions. Each row carries the bounded scope language per pattern 87.

| ADR | Title | Scope of governance over the documentation |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus a home | Governs documentation structure: the eight sections plus this home is the canonical spine |
| DEC-376587 | Section renames | Governs documentation structure: the section names are the canonical labels |
| DEC-9c58c6 | Operating Model section name | Governs documentation structure: the no-article register for sections; section-internal mid-sentence usage admits the lowercase article |
| DEC-3395bc | bc-docs-v3 SSOT cutover | Governs the documentation's home repository, the v3 layout, and the bc-core docs endpoints |
| DEC-b97390 | bc-admin embedded reader | Governs the canonical reader; the bc-admin reader is the reference rendering |
| DEC-a4e550 | ADR-First Decision Workflow | Governs the Decisions peer; ADR file is SSOT, DevHub holds metadata |
| DEC-ebf0b4 | Session Discipline and Data Integrity Rules | Governs the engineering session discipline that drafts and revises the chapters |

This overview routes governance to the owning chapter or owning section. The bounded scope language above prevents this overview from claiming authority over the platform behavior the ADRs govern; the chapter that owns the topic carries the substantive treatment.

**Governing source.** outline.md §4; per-chapter `governing_adrs` frontmatter.

## References

- Foundation (the locked architectural authority)
- The Invariants
- The Object Model
- The Contract Grammar
- The Evaluation Boundaries
- The Authority Model
- The Dual-Layer Interaction Model
- Operating Model: Overview
- Implementation: Overview
- AI: Overview
- Development: Overview
- Onboarding: Overview
- Operations: Overview
- Compliance: Overview
- Documentation System
- DEC-c06f41 (Spine expansion to eight sections plus a home)
- DEC-376587 (Section renames)
- DEC-9c58c6 (Operating Model section name)
- DEC-3395bc (bc-docs-v3 SSOT cutover)
- DEC-b97390 (bc-admin embedded reader)
- DEC-a4e550 (ADR-First Decision Workflow)
- DEC-ebf0b4 (Session Discipline and Data Integrity Rules)
- bc-docs-v3 outline.md (the framework)
- bc-docs-v3 HANDOFF.md (the per-session entry point)
- `scripts/reference/aws-rewrite-checklist.md` (the eighty-eight earned voice patterns)
