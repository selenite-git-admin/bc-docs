---
id: operations-overview
order: 29.9
title: "Operations: Overview"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-problem, the-solution, the-invariants, the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, the-dual-layer-interaction-model, operating-model-overview, implementation-overview, ai-overview, onboarding-overview]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Authority Model
  - Operating Model: Overview
  - Implementation: Overview
  - Onboarding: Overview
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; Operations section shape)
  - DEC-3b86ea (Section renames; Operations as the section name; clean slate migration moved into Upgrade and Migration)
  - DEC-1918d0 (Two-database split; Operations honors the platform plus tenant DB topology)
  - DEC-771baf (Tenant database topology; one tenant database per tenant)
  - DEC-324d9e (Stripe billing; four subscription tiers; four hosting variants)
  - DEC-bebaec (Chain Completeness SSOT)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Operations: Overview

## Scope

This chapter is the section opener for Operations. It states what Operations is and what role it plays in the documentation, maps the eight chapters that follow this overview into reading groups, gives a recommended reading sequence by audience, declares the boundaries between Operations and the other sections of the documentation, and records the as-built discipline under which Operations chapters are written.

This chapter does not redefine any Operations claim. Tenant Lifecycle and Subscription, Deployment Topology, Security Operations, Upgrade and Migration, Observability and Telemetry, Performance and Scale, Incident and Change Management, and Support and Escalation each govern their own claims. This overview locates them; it does not restate them with authority. Where this overview names a section-wide property, the governing source is the outline that records Operations' structure or the chapter that owns the property.

This chapter exists so that a reader who opens Operations cold can locate any specific chapter without having read the others, and so that a reader who has finished Operations can hold the eight chapters that follow as one coherent set rather than as eight independent files.

**Governing source.** outline.md §4.7.

## What Operations Means

Operations is the descriptive authority for running the platform day-to-day. Where Foundation defines the architectural rules, Operating Model defines the contract-execution runtime, Implementation describes the built artifact, AI describes the AI surface, Development describes the engineering practice, and Onboarding describes the governed sequences that build the platform up, Operations describes how the platform runs in steady state and how it recovers from change.

| Property | Operational form |
|---|---|
| Operational | Operations chapters describe the procedures the platform follows in steady-state operation. Each chapter is an operational discipline, not a runtime act and not an authoring procedure. The runtime acts are owned by Operating Model; the authoring procedures are owned by Onboarding |
| As-built and gaps | Per pattern 81, every Operations chapter that surveys an operational substrate maintains a drift inventory recording gaps between operational intent and current state. Operations does not present an aspirational SRE-grade posture as if it were the as-built |
| Tenant-and-platform scoped | Operations distinguishes platform-side operations (deployment, migration, observability infrastructure, change management) from tenant-side operations (Subscription lifecycle, tenant onboarding through Tenant Onboarding, customer-facing support); both lanes coexist in the section |
| Foundation-and-Operating-Model-bound | Every Operations chapter consumes Foundation and Operating Model as locked authority. An Operations claim that contradicts a Foundation invariant or an Operating Model rule is incorrect against the platform's architecture, regardless of what the operational practice happens to do |
| Section-internal sequencing | Operations chapters depend on each other (incidents read observability; observability reads the change-record substrate; performance reads metric evaluation; support reads the incident classification). The dependency direction is recorded in each chapter's prerequisites; this overview does not re-record it |

The as-built discipline is the section's defining trait. A reader who finds an aspirational claim in an Operations chapter (an SLA, an on-call rotation, a status page, a customer health score) should treat it as a recorded gap if the chapter's drift inventory catches it, or as an undocumented gap to surface for the next cold-read. Operations records what is true in the readiness baseline.

**Governing source.** outline.md §4.7; The Authority Model.

## The Eight Chapters That Follow

Operations has nine chapters: this overview plus the eight chapters that follow. The grouping below is for navigation; section order is fixed by the outline and by chapter dependencies.

| Group | Chapters | What the group covers |
|---|---|---|
| Tenant lifecycle | Tenant Lifecycle and Subscription | Navigation entry for the Subscription artifact, the tier model, the hosting variants, and the lifecycle state machine |
| Deployment substrate | Deployment Topology | Navigation entry for the deployment procedure, the AuthStack and dormant PlatformInfraStack, the local plus dev plus aspirational prod posture, and the per-hosting-variant realization status |
| Security and compliance posture | Security Operations | Navigation entry for the JWT authentication boundary, the secrets surface, the supply-chain governance via CodeArtifact, the PII classification trail, and the bc-qa pre-commit hook surface |
| Change management | Upgrade and Migration; Incident and Change Management | Navigation entry for the migration discipline (DDL, contract, chain rebuild, golden snapshot, clean-slate reset) and the change-record substrate (DevHub plan-and-report pair; D268 self-audit; L-node semantic gate) |
| Operational read substrate | Observability and Telemetry; Performance and Scale | Navigation entry for the emission surfaces (structured logs, health endpoints, document JSONL trail, AI evidence table, chain status SSOT, DevHub activity log) and the performance posture (per-tenant isolation, metric engine cost, AI rate limits) |
| Customer-facing operations | Support and Escalation | Navigation entry for the per-tier support posture, the platform-side escalation path, the incident-class scope for customer-facing events, and the customer communication cadence |

The six groups cover the eight chapters that follow without overlap. A chapter that does not fit a group is a chapter that does not belong in Operations.

**Governing source.** outline.md §4.7.

## Reading Sequence

The eight chapters can be read in outline order, but the section also supports audience-specific reading paths. The order below is intentional: each later chapter assumes the prior chapters' substrates where they share a common operational concern.

| Reader intent | Recommended sequence | Why |
|---|---|---|
| Architectural orientation | Tenant Lifecycle and Subscription; Deployment Topology; Upgrade and Migration; the rest as needed | The architectural reader builds the operational mental model from the tenant-side artifact (Subscription) outward to the deployment substrate and the migration discipline |
| Engineering | Deployment Topology; Upgrade and Migration; Security Operations; Observability and Telemetry; the rest as needed | Engineering reads the deploy substrate first, then the migration cycle that produces new schema, then the security operations against the deployed substrate, then the observability surfaces |
| Operations or SRE | Observability and Telemetry; Performance and Scale; Incident and Change Management; Deployment Topology; the rest as needed | Operations reads the read substrate first (to know what is observable), then the performance posture, then the incident-and-change governance, then the deploy topology that produces the substrate they observe |
| Audit and compliance | Security Operations; Incident and Change Management; Upgrade and Migration; Tenant Lifecycle and Subscription; the rest as needed | Audit reads the security posture, the change-record substrate, the migration discipline, and the tenant lifecycle as the four primary control surfaces |
| Customer-facing or sales engineering | Tenant Lifecycle and Subscription; Support and Escalation; Performance and Scale; the rest as needed | Customer-facing reads the tier and lifecycle model first, then the support posture per tier, then the performance posture that customers will ask about |

The reading sequences do not reorder the chapters in the section. They guide a reader who needs to extract a coherent subset for a specific purpose.

**Governing source.** outline.md §4.7.

## Boundaries with Other Sections

Operations describes running the platform. The boundaries with other sections are explicit and one-way: Foundation, Operating Model, and Implementation bind Operations; AI provides the AI-runtime surfaces Operations consumes; Development governs the engineering practice that produces the artifacts Operations runs against; Onboarding governs the governed sequences that produce the operational state; Compliance reports against the Operations substrate.

| Section | Boundary role | What crosses the boundary |
|---|---|---|
| Foundation | Binds Operations as locked authority | Operations chapters cite Invariants, the Object Model, the Authority Model as already-defined authority. Operations describes running the platform; it does not redefine Foundation |
| Operating Model | Binds Operations as locked authority | Operations chapters cite Sources and the Catalog (the catalog Source Registration produces and Operations operates against), Admission and Observation (the runtime acts), Metric Evaluation (the engine Performance and Scale measures), Tenancy and Binding (the tenant scope) as already-defined runtime authority |
| Implementation | Binds Operations as locked authority | Operations chapters cite Infrastructure (the deploy substrate), Backend Services (the deployable shape), Data Model and Schema (the database the migration discipline acts against), Audit and Activity Logging (the substrate Incident and Change Management consumes) |
| AI | Provides AI-runtime surfaces Operations consumes | Performance and Scale cites Bedrock and AI provider rate limits; Observability and Telemetry cites the AI evidence table; Security Operations cites the AI gate surfaces; Support and Escalation cites the AI verdict trail for customer-facing incident triage |
| Development | Adjacent | Development governs DevHub (the substrate Operations' Incident and Change Management uses), the decision and change procedure (the discipline Operations honors), build and release (the cycle that produces the deploy artifacts Operations deploys); Operations consumes the Development discipline without redefining it |
| Onboarding | Adjacent | Onboarding governs the governed sequences that produce the operational state Operations runs against; Tenant Onboarding produces the tenant-side substrate Tenant Lifecycle and Subscription manages; the per-artifact onboarding chapters produce the contract artifacts the chain runs against |
| Compliance | Consumes Operations | Compliance chapters cite the Operations gates as preventive controls and the change records as audit evidence; Compliance reports conformance against Operations; it does not produce Operations authority |

The dependency direction is one-way. An Operations chapter that depends on a later section for its own correctness is a boundary violation. A later section that redefines an Operations procedure instead of consuming it is also a boundary violation.

**Governing source.** outline.md §4.7; The Authority Model; Operating Model: Overview; Implementation: Overview; Onboarding: Overview.

## Cross-Cutting Concerns

Several concerns thread through multiple Operations chapters. The cross-cutting nature is intentional; the concerns are stated in each chapter where they apply rather than centralized in one chapter that the others would then need to consult separately.

| Concern | Chapters that thread it | How it is preserved |
|---|---|---|
| Two-database split (platform plus tenant) | Deployment Topology; Security Operations; Upgrade and Migration; Performance and Scale | Follow DEC-1918d0 and DEC-771baf first; each chapter records its own treatment (deploy-time DDL application, per-tenant scope discipline, per-tenant migration application, per-tenant performance isolation) |
| As-built honesty over aspirational posture | Every Operations chapter | Per pattern 81; each chapter records its drift inventory explicitly; aspirational surfaces are recorded as queued, not asserted as real |
| The four hosting variants | Tenant Lifecycle and Subscription (authority); Deployment Topology (realization status); Security Operations (per-variant credential surface) | The variant inventory authority is Tenant Lifecycle and Subscription; other Operations chapters consume it for their per-variant view |
| The DevHub change-record substrate | Incident and Change Management (authority); Upgrade and Migration; Deployment Topology; Security Operations | The change-record discipline is the same regardless of which Operations chapter triggers a change; the substrate is shared |
| The chain status SSOT | Observability and Telemetry; Performance and Scale; Incident and Change Management; Support and Escalation | Per DEC-bebaec; the SSOT is the operational read for chain completeness; Operations chapters that need a chain-state read use the SSOT, not ad-hoc queries |
| The tier model | Tenant Lifecycle and Subscription (authority); Support and Escalation (per-tier posture); Security Operations (per-tier credential discipline) | Per DEC-324d9e; the tier model carries different commercial and operational arrangements per tier |
| Per-tenant isolation | Deployment Topology; Security Operations; Performance and Scale; Upgrade and Migration | Per DEC-771baf; the per-tenant database is the platform's isolation boundary at the operational layer |

A chapter that introduces a new claim about any cross-cutting concern aligns with the threading discipline. A later section that consumes an Operations chapter consumes the cross-cutting concern as the chapter states it.

**Governing source.** The owning Operations chapters; The Authority Model; Foundation; Operating Model: Overview; Implementation: Overview; DEC-1918d0; DEC-771baf; DEC-bebaec; DEC-324d9e.

## Constraints

The constraints below apply to Operations as a whole and are inherited by every chapter in the section.

| Constraint | Operational form |
|---|---|
| Operations is descriptive, not normative | Operations chapters describe what the platform's operational practice actually is. The architectural rules are owned by Foundation; the runtime acts are owned by Operating Model. An Operations claim that redefines a runtime act is recorded as drift, never as redefinition of the act |
| Drift inventory is mandatory | Every Operations chapter that surveys an operational substrate maintains a drift inventory recording gaps between operational intent and current state. The chapter does not present an aspirational substrate as if it were the as-built |
| As-built discipline matches drift inventory | Per pattern 81, when a chapter spans operational practices of varying maturity (formalized, partial, aspirational), the chapter's lead-paragraph scope statement matches the chapter's own drift inventory. A claim that the chapter's own drift inventory immediately contradicts is internal incoherence |
| Behavior-search grounding for code-bearing claims | Per pattern 71, an Operations chapter that asserts an operational behavior verifies the claim against the code path or the configuration file that implements it. A name-based search alone is not sufficient grounding; the chapter cites the actual file path |
| Bidirectional citation discipline | Every `DEC-xxxxxx` and `FND-ERR-xxx` cited in body appears in frontmatter `governing_adrs` or `errata_referenced`, and vice versa. The Governing Decisions table is bidirectionally complete with frontmatter and body citations |
| Forbidden-vocabulary scrub | The forbidden roots (the ETL-style framing tokens listed in `outline.md` §2, plus the broader tightening that replaces preceding-layer and later-layer language with neutral adjacency wording in non-DAG contexts) are not used in body prose. Replacements (observe, admit, evaluate, resolve, preserve, record, reference, bind, finalize, surface) are used instead |
| Deploy-specific figures cited from Infrastructure | Per pattern 85; an Operations chapter that needs port numbers, account identifiers, IAM ARNs, region codes, or other deploy-time figures cites Infrastructure or Deployment Topology; the figures live in those chapters, not duplicated across Operations |
| Voice and vocabulary discipline | No em dashes; no chapter numbers; section-mark byte integrity; the live voice-pattern checklist in `aws-rewrite-checklist.md` applies to every chapter |

A chapter that violates any of these constraints is incorrect against the section's discipline.

**Governing source.** The Authority Model; outline.md §4.7; `scripts/reference/aws-rewrite-checklist.md`.

## Governing Decisions

| Decision | Scope in this overview | Boundary |
|---|---|---|
| DEC-c06f41 | Establishes the eight-section spine plus home and the Operations section shape that includes this overview and the eight following chapters | Governs documentation structure only; child chapters own their operational claims |
| DEC-3b86ea | Establishes the section rename to Operations and explicitly moves Clean Slate Migration into Upgrade and Migration in this section | Governs documentation scope only; child chapters own the procedural claims |
| DEC-1918d0 | Supplies the two-database split as a cross-cutting concern readers will see across most Operations chapters | This overview routes the concern; child chapters own the operational treatment |
| DEC-771baf | Supplies tenant database topology and the per-tenant isolation that the operational practices honor | This overview routes the concern; child chapters own the operational consequence |
| DEC-324d9e | Supplies the four subscription tiers and four hosting variants whose operational consequences this section's chapters carry | This overview routes the concern; Tenant Lifecycle and Subscription is the authoring authority |

**Governing source.** Decisions: ADR Registry; outline.md §4.7.

| DEC-bebaec | Keeps chain-status and test-bench reconciliation routed to owning chapters while this overview remains navigational. |

## References

- Tenant Lifecycle and Subscription
- Deployment Topology
- Security Operations
- Upgrade and Migration
- Observability and Telemetry
- Performance and Scale
- Incident and Change Management
- Support and Escalation
- Foundation: Overview
- Operating Model: Overview
- Implementation: Overview
- AI: Overview
- Onboarding: Overview
- The Authority Model
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-3b86ea: Section renames; Operations as the section name
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-324d9e: Stripe billing; four subscription tiers; four hosting variants
- outline.md §4.7: Operations




