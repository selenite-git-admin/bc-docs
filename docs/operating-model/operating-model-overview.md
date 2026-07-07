---
id: operating-model-overview
order: 7.9
title: "Operating Model: Overview"
status: drafting
authority: authoritative
depends_on: [the-problem, the-solution, the-invariants, the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, the-dual-layer-interaction-model]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Object Model
  - The Contract Grammar
  - The Evaluation Boundaries
  - The Authority Model
governing_adrs:
  - DEC-771baf (Tenant database architecture; platform-tenant one-way dependency)
  - DEC-ce6e2b (Section rename: The Runtime → The Operating Model)
  - DEC-9c58c6 (Article-drop refinement: section name canonical form is "Operating Model")
errata_referenced: []
v2_sources: []
---

# Operating Model: Overview

## Scope

This chapter is the section opener for Operating Model. It states what the section is and what it is not, names the architectural through-line that binds the chapters in the section, maps the eighteen chapters that follow into reading groups, gives a recommended reading sequence, and declares the boundaries between Operating Model and the other five sections of the documentation. It does not redefine any Operating Model chapter's governed behavior.

Operating Model chapters named here are mapped as section navigation and bounded role summaries. The overview may point to a later Operating Model chapter without depending on that later chapter for correctness; authority-bearing details remain governed by the chapter that owns them. Where this overview states a section-wide invariant, the governing source is Foundation, the current outline, a cited ADR, or an already-governing Foundation chapter.

This chapter exists so that a reader who opens Operating Model cold can locate any specific chapter without having read the prior chapters, and so that a reader who has finished Operating Model can hold the section's claims as one coherent set rather than eighteen independent files.

**Governing source.** Foundation; The Object Model; The Contract Grammar; The Evaluation Boundaries; The Authority Model; outline.md §4.2.

## What Operating Model Means

Operating Model in this documentation describes the contract-execution runtime: the set of acts, contracts, artifacts, and governance records through which the platform turns observed source state into authoritative metric values and recorded actions, governed by the contract chain and bounded by the invariants of Foundation. The label is the established architectural term for a layer that names a system's artifacts, composition rules, execution acts, proof emissions, and governance frame as one interdependent set. It captures both the static structure (catalog, vocabulary, contracts) and the dynamic behavior (the four boundary acts and proof emission) without privileging either.

Operating Model does not mean every runtime concern in the platform. Three categories of runtime concern are deferred to other sections:

| Concern category | Where it lives | Reason for the boundary |
|---|---|---|
| Commercial and tenant lifecycle | Operations | These concerns govern the tenant's relationship to the platform, not the contract-execution runtime. Where they touch contract execution at runtime, this section consumes declared state read-only at named entitlement surfaces without redefining the lifecycle acts. |
| Infrastructure and service runtime | Implementation; Operations | These concerns govern where and how the runtime executes, not what it does. The contract-execution runtime is service-runtime-agnostic at the architectural level. |
| Onboarding runtime | Onboarding | These concerns govern how the contracts that Operating Model executes against come to exist. Operating Model chapters may read onboarding verdicts and contract registry state; this section does not redefine onboarding acts. |

The boundary is operationally consequential. A reader who expects to find billing integration, deployment topology, or contract authoring procedures here will not find them. A reader who finds claims about entitlement consultation, lifecycle state reads, or quality gate verdict consumption here is reading a consumption boundary, not the artifact's home.

**Governing source.** Foundation; The Authority Model; outline.md §4.2; DEC-ce6e2b; DEC-9c58c6.

## The Architectural Through-Line

Six claims bind every chapter in this section.

| Claim | Where it is governed | Operational form in Operating Model |
|---|---|---|
| The contract chain is the spine of authoritative evaluation | Contract Chain Assembly | Source Contract, Admission Contract, Observation Contract, Canonical Contract, Metric Contract, and Intervention Contract pass values from observed source state to recorded action under explicit reference at every link. |
| Four boundary acts produce all authoritative state | The Evaluation Boundaries | Admission produces Source Objects; canonical evaluation produces Canonical Objects; metric evaluation produces Metric Snapshots; action evaluation produces Action Objects. No other act produces authoritative state. |
| Read access never triggers evaluation | The Evaluation Boundaries | A read of authoritative state returns the recorded value. It does not invoke admission, canonical evaluation, metric evaluation, or action evaluation. |
| Proof is emitted at the act, not deferred | The Object Model; Evidence and Lineage | Evidence and Lineage are produced by the same act that produces authoritative state. They are not synthesized later from logs or reconstructed from runtime telemetry. |
| Tenants own execution data; the platform owns contracts | Tenancy and Binding (DEC-771baf) | Source Objects, Canonical Objects, Metric Snapshots, Action Objects, Evidence, Lineage, Run records, Connections, and Bindings live in the tenant database. Contract registry records, the Source Catalog, and global chain status live in the platform database. The dependency direction is one-way: tenants depend on platform contracts, platform does not read tenant state to produce platform-level outputs. |
| Read-only validation is separate from authoritative state production | Chain Completeness and Verdict | The chain integrity check is a registry-side governance asset that records global chain readiness and tenant/source readiness. It does not produce, modify, or replace any authoritative state, and it does not run as part of the four boundary acts. |

The six claims interlock. A chapter that violates any of them is wrong against this section's architecture; a chapter that obeys all six can be located, audited, and extended within the section's discipline.

**Governing source.** Foundation; The Object Model; The Evaluation Boundaries; The Authority Model; DEC-771baf.

## Chapter Map

The eighteen chapters that follow this overview fall into ten groups by concern. The grouping is for reader navigation; chapter order in the section is fixed by the outline and by chapter dependencies, and is not the same as group order.

| Group | Chapters | What the group covers |
|---|---|---|
| Catalog and Vocabulary | Sources and the Catalog; Business Vocabulary | The platform's record of observable source structure across six hierarchy entities, and the platform's internal vocabulary of Business Fields, Business Objects, and Canonical Fields. |
| Chain Assembly and Authoring Gates | Contract Chain Assembly; Quality Gates and Chain Integrity | The six-link relay that turns a source-system field into a trusted metric value, and the quality gates that govern every authoring act on the chain. |
| The Reader Stack | Connectors and Readers | Connector, Reader, Reader Flavor, Reader Binding, and Connection. The UniBAT pattern: source-system-agnostic on input, business-aware on output. |
| The Four Boundary Acts | Admission and Observation; Canonical Evaluation; Metric Evaluation; Action Evaluation | The runtime acts at the four evaluation boundaries that produce authoritative state. Each act has its own Run record, its own contract family, and its own proof emission. |
| The Metric Catalog | Metric Catalog | The platform-scoped registry of metric definitions: classification, lifecycle, formula tests, registration gates, and tenant view. |
| Metric Management | Metric Management System; Metric Management System — Recovery Track | The Metric Management System (MMS) umbrella for the full lifecycle of a metric — creation, activation, runtime evaluation, recovery from stuck states, evolution (supersession / retirement), and catalog visibility — organised into four tracks (Creation, Recovery, Runtime, Evolution) above the Metric Contract Framework (MCF) grammar layer. The parent chapter (`metric-management-system.md`) carries the Creation Track flow, the gate inventory, the recovery-route enumeration, and the cross-track touchpoints for Runtime and Evolution. The Recovery Track child chapter (`metric-management-system-recovery-track.md`) carries the per-route operational policy for Stage 7's eight recovery routes (R1–R8), multi-route conflict discipline, catalog-visibility consequences, and the recommended route plans for recorded stuck Metric Contract Versions. Both chapters are operator-ratified draft-authoritative. Runtime Track and Evolution Track doctrines remain future artifacts and will land as peer chapters when drafted. |
| Proof | Evidence and Lineage | Two proof object types emitted at every proof-emitting act; immutable and append-only; tenant-scoped; the proof chain that preserves authoritative-act history for audit. |
| Tenant Scope | Tenancy and Binding; Tenant Extensions and Overrides; Tenant Entitlement Enforcement | Tenant ownership boundary, Contract Binding as bounded variation, per-family extension surfaces, and how contract-execution acts consult Subscription state. |
| Time | Fiscal Time and Temporal Gates | Fiscal period as a per-Canonical-Object attribute resolved at canonical evaluation; the calendar stack that holds the resolution rules; the boundary that separates fiscal time from observation time and from invocation time. |
| Readiness | Chain Completeness and Verdict | The locked definition of complete (L1-L7 + C1-C5 + E1-E2 for global chain status), tenant/source E3 readiness, the chain verdict set, and the persisted stores that preserve those readiness answers at their correct grains. |

The ten groups cover the section without overlap. A chapter that does not fit a group is a chapter that does not belong in this section.

**Governing source.** outline.md §4.2; Foundation.

## Reading Sequence

The section is written to be read in outline order. Two alternative sequences serve specific reader intents.

| Reader intent | Recommended sequence | Why |
|---|---|---|
| Architectural understanding | Operating Model outline order | Each chapter assumes the prior chapters' definitions. Linear reading produces the cleanest architectural picture. |
| Audit and compliance | Evidence and Lineage; Chain Completeness and Verdict; Tenancy and Binding; the four boundary acts (Admission and Observation, Canonical Evaluation, Metric Evaluation, Action Evaluation); Metric Management System (lifecycle states, cert grammar, supersession discipline) + Metric Management System — Recovery Track (recovery routing decisions, abandon / supersession audit trail); Tenant Entitlement Enforcement | Audit reads the proof chain, readiness records, and the tenant ownership boundary first; the boundary act details support that reading; the MMS parent adds lifecycle-state evidence (Stage 6 verdict ledger, Stage 8 cert ledger, Stage 10 supersession ledger) and the Recovery Track adds the recovery-routing-decision ledger that audit relies on for metric provenance and operator-decision history. |
| Engineering reading | Sources and the Catalog; Business Vocabulary; Connectors and Readers; Admission and Observation; Canonical Evaluation; Metric Evaluation; Metric Management System (Creation Track flow + cross-track touchpoints) + Metric Management System — Recovery Track (per-route operational policy); the rest in outline order | Engineering reads the catalog and the boundary acts that consume it first; MMS then names the operational flow the engineering work executes; the Recovery Track names the per-route operational policy for stuck-candidate handling; the chain-assembly and tenant-scope material anchors the engineering work in governance. |

The reading sequences do not reorder the chapters in the section. They guide a reader who needs to extract a coherent subset for a specific purpose.

**Governing source.** outline.md §4.2; Foundation.

## Boundaries with Other Sections

Operating Model depends on Foundation and supplies the contract-execution substrate that later sections host, author against, operate, or audit. The boundaries are explicit.

| Section | Boundary role | What crosses the boundary |
|---|---|---|
| Foundation | Governs Operating Model | Invariants, the Object Model, the Contract Grammar, the Evaluation Boundaries, the Authority Model, and the Dual-Layer Interaction Model are governed by Foundation chapters and consumed by Operating Model chapters as already-defined authority. |
| Implementation | Hosts and surfaces Operating Model | Implementation chapters describe service placement, storage shape, APIs, user interfaces, integration surfaces, and test surfaces for Operating Model artifacts. Operating Model chapters describe what the contract-execution runtime does. |
| AI | Participates in Operating Model under bounded surfaces | AI participates in Operating Model at three named places: AI gates inside Quality Gates and Chain Integrity, AI agents that may consult Operating Model state read-only, and the AI Contract grammar (provisional) defined in The Contract Grammar. AI is otherwise advisory under the Dual-Layer Interaction Model and does not author Operating Model authoritative state. |
| Development | Provides the engineering process around Operating Model | DevHub records authoring acts that produce Operating Model contract registry state. Decision and Change Workflow governs how Operating Model spec evolves through ADRs and Errata. Development does not redefine Operating Model behavior. |
| Onboarding | Produces contracts that Operating Model governs | Onboarding workflows produce contract registry state that Operating Model consumes. Quality-gate and chain-readiness chapters in Operating Model define the verdicts that onboarding workflows must satisfy without redefining the workflows themselves. |
| Operations | Operates tenant and service envelopes around Operating Model | Operational records can affect runtime preconditions at named read-only surfaces. Operating Model consumes such records where an Operating Model chapter declares the surface; it does not author tenant lifecycle, support, incident, or performance operations. The shared root in "Operating Model" and "Operations" is intentional: this section names the spec, that section names the activity. |
| Compliance | Reads Operating Model proof and boundaries | Compliance chapters read the Operating Model proof chain and tenant ownership boundary as evidence for conformance assertions. Compliance does not produce Operating Model authoritative state. |

The dependency directions are observable in cross-section citations. An Operating Model chapter that depends on a later section for its own correctness, or a later section that redefines an Operating Model invariant instead of consuming it, is a boundary violation.

**Governing source.** Foundation; The Authority Model; outline.md §4.2.

## Cross-Cutting Concerns

Four concerns thread through multiple chapters in Operating Model. The cross-cutting nature is intentional; the concerns are surfaced in each chapter where they apply rather than centralized in one chapter that the runtime acts would then need to consult separately.

| Concern | Chapters that thread it | How it is preserved across chapters |
|---|---|---|
| The contract chain | Contract Chain Assembly defines it; Admission and Observation, Canonical Evaluation, Metric Evaluation, and Action Evaluation execute it; Chain Completeness and Verdict validates it | Each runtime act describes its consumption of the chain in operational terms; the chain definition is not redefined per act. |
| Tenant scope | Tenancy and Binding establishes the ownership boundary; Tenant Extensions and Overrides defines per-family bounded variation; Tenant Entitlement Enforcement defines runtime consultation of Subscription state | Each chapter scopes its claims to platform side or tenant side consistent with DEC-771baf. The tenant database is the home of all tenant-scoped artifacts; the platform database is the home of all platform-scoped artifacts. |
| Proof | Evidence and Lineage defines it; every boundary act emits it | Per-record Evidence and per-object Lineage are emitted at the same act that produces authoritative state. The proof chain is append-only, immutable, and tenant-scoped. |
| Read-only validation | Chain Completeness and Verdict centralizes the read-only check | Global chain status is platform registry metadata; tenant/source readiness is tenant/source-scoped governance metadata. The boundary acts consume these records as preconditions where declared; they do not modify them. |

A chapter that introduces a new claim about any of the four cross-cutting concerns must align with the threading discipline established here.

**Governing source.** Foundation; DEC-771baf; The Object Model; The Evaluation Boundaries.

## Constraints

The constraints below apply to Operating Model as a whole and are inherited by every chapter in the section.

| Constraint | Operational form |
|---|---|
| Section is self-contained for the contract-execution runtime | Every claim a chapter in this section makes is grounded in Foundation, in another chapter in this section, or in a governed ADR or Errata entry. The section does not depend on chapters in Implementation, AI, Development, Onboarding, Operations, or Compliance for its own correctness. |
| Drafted authority only | Chapters cite drafted authorities. Forward references to queued chapters use bounded role language rather than chapter names per the authoring conventions for this documentation. |
| Tenant-scoped artifacts are tenant-scoped | Source Objects, Canonical Objects, Metric Snapshots, Action Objects, Evidence, Lineage, Run records, Connections, and Bindings live in the tenant database. Operating Model does not place tenant-scoped artifacts in the platform database, and the platform does not read tenant state to produce platform-level outputs. |
| Authoritative state is produced only at the four boundaries | No chapter introduces an act that produces a Source Object, Canonical Object, Metric Snapshot, or Action Object outside the four governed evaluation boundaries. |
| Read access is non-evaluating | No chapter introduces a read path that triggers admission, canonical evaluation, metric evaluation, or action evaluation as a side effect of the read. |
| Proof at the act | No chapter defers proof emission to a later act, a separate logging path, or a reconstruction step. Evidence and Lineage are emitted at the boundary act that produces authoritative state. |
| Read-only validation discipline | Chain integrity is a registry-side governance asset. No chapter elevates it to a runtime act or to a fifth evaluation boundary. |

A chapter that violates any of the seven constraints is incorrect against this section's architecture and is treated as such in cold-read review.

**Governing source.** Foundation; The Object Model; The Evaluation Boundaries; The Authority Model.

## Diagram Convention

Operating Model chapters may embed diagrams **inline** as Mermaid code blocks within the chapter body. The `diagrams:` frontmatter field lists the diagram IDs (e.g. `DG-mms-track-architecture`) regardless of whether the diagram is inline or rendered as a standalone asset file under `bc-docs/docs/assets/diagrams/`. Inline Mermaid is the accepted default for Operating Model chapters; standalone asset files are a future option if rendering, export, or cross-section reuse needs require it, and are not a precondition for chapter authoring.

A chapter that uses inline Mermaid registers each diagram with a `DG-{kebab-name}` identifier in the frontmatter `diagrams` array. The identifier is the stable handle other chapters or ADRs cite when referencing the diagram, even if its rendering form (inline vs. asset file) changes later. Migration to standalone assets, when undertaken, preserves the identifier — the asset file at `bc-docs/docs/assets/diagrams/{DG-id}.{ext}` becomes authoritative and the inline block is removed from the chapter body.

Operating Model chapters that carry diagrams in this snapshot:

- Metric Management System — `DG-mms-track-architecture` (§1A.6), `DG-mms-creation-track-state-machine` (§3.0); both inline Mermaid.
- Metric Management System — Recovery Track — `DG-mms-recovery-decision-flow` (§4.1), `DG-mms-recovery-completion-events` (§9.3); both inline Mermaid.

**Governing source.** Operator decision recorded as part of the Metric Management System chapter relocation pass; this convention is provisional and may be lifted into an ADR if the standalone-asset question is later opened.

## References

- Foundation: Scope and Non-Negotiability
- The Problem
- The Solution
- The Invariants
- The Object Model
- The Contract Grammar
- The Evaluation Boundaries
- The Authority Model
- The Dual-Layer Interaction Model
- outline.md §4.2: Operating Model
- Sources and the Catalog
- Business Vocabulary
- Contract Chain Assembly
- Quality Gates and Chain Integrity
- Connectors and Readers
- Admission and Observation
- Canonical Evaluation
- Metric Evaluation
- Metric Catalog
- Metric Management System
- Metric Management System — Recovery Track
- Action Evaluation
- Evidence and Lineage
- Tenancy and Binding
- Tenant Extensions and Overrides
- Tenant Entitlement Enforcement
- Fiscal Time and Temporal Gates
- Chain Completeness and Verdict
- DEC-771baf: Tenant database architecture and one-way dependency
- DEC-ce6e2b: Section rename rationale
- DEC-9c58c6: Article-drop refinement
- Decisions: ADR Registry
