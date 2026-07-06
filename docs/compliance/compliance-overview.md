---
id: compliance-overview
order: 44.9
title: "Compliance: Overview"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-problem, the-solution, the-invariants, the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, the-dual-layer-interaction-model, operating-model-overview, implementation-overview, ai-overview, development-overview, onboarding-overview, operations-overview]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Authority Model
  - Operating Model: Overview
  - Implementation: Overview
  - Development: Overview
  - Operations: Overview
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus a home; Compliance section shape)
  - DEC-376587 (Section renames; Compliance as the section name for conformance and privacy posture)
  - DEC-ae331f (Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria; the section's load-bearing decision)
  - DEC-bd5492 (GDPR/DPDP/CCPA Nullification Object; the privacy mechanism the section records)
  - DEC-1918d0 (Two-database split; the access-isolation substrate the section reports against)
  - DEC-771baf (Tenant database topology; the tenant-isolation refinement)
  - DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact; the supplier-side preventive control)
  - DEC-ee6018 (bc-qa standalone repo; the preventive-control authority)
  - DEC-bebaec (Chain Completeness SSOT; the processing-integrity authority)
  - DEC-804874 (L-Node Verification with Semantic Family Classification; the session-close gate)
  - DEC-ebf0b4 (Session Discipline and Data Integrity Rules; the engineering session discipline that operates as the de facto information security policy)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Compliance: Overview

## Scope

This chapter is the section opener for Compliance. It states what Compliance is and what role it plays in the documentation, maps the five chapters that follow this overview into reading groups, gives a recommended reading sequence by audience, declares the boundaries between Compliance and the other sections of the documentation, names the cross-cutting concerns that thread the section's chapters, and records the constraints under which Compliance chapters are written.

This chapter does not redefine any Compliance claim. InfoSec and Access Control, ISO 27001 Conformance, SOC 2 Conformance, Privacy and the Immutable Fact, and Risk and Vendor Management each govern their own claims. This overview locates them; it does not restate them with authority. Where this overview names a section-wide property, the governing source is the outline that records Compliance's structure, the chapter that owns the property, or the load-bearing ADR that governs the conformance posture (`DEC-ae331f`).

This chapter exists so that a reader who opens Compliance cold can locate any specific chapter without having read the others, and so that a reader who has finished Compliance can hold the five chapters that follow as one coherent set rather than as five independent files.

**Governing source.** outline.md §4.8.

## What Compliance Means

Compliance is the descriptive authority for the platform's conformance and privacy posture. Where Foundation defines the architectural rules, Operating Model defines the contract-execution runtime, Implementation describes the built artifact, AI describes the AI surface, Development describes the engineering practice, Onboarding describes the governed sequences that build the platform up, and Operations describes how the platform runs in steady state, Compliance reports against the substrate the prior sections produce.

| Property | Operational form |
|---|---|
| Reporting, not authoring | Compliance chapters report what the platform's substrate provides; they do not author the substrate. The InfoSec controls are in InfoSec and Access Control's running surface; Compliance reads them as the technical-control evidence |
| As-built and gaps | Per pattern 81, every Compliance chapter that surveys a conformance posture maintains a drift inventory. Compliance does not present an aspirational attestation as if it were the as-built |
| Foundation-and-prior-sections-bound | Every Compliance chapter consumes Foundation and the prior sections as locked authority. A Compliance claim that contradicts a Foundation invariant or a runtime substrate is incorrect against the platform's architecture, regardless of what an external framework's checklist might suggest |
| Forward-looking on certification | Per `DEC-ae331f`, the platform's certification engagement is staged. Readiness baseline first; certification after pilot evidence. The chapters record substrate, not attestation |
| Three-of-five SOC 2 scope | Per `DEC-ae331f`, the SOC 2 Type I scope is reduced: Security, Confidentiality, Processing Integrity. Availability and Privacy are gated on maturity |
| Nullification as the privacy resolution | The platform resolves the Foundation immutability invariant against privacy erasure obligations through sentinel-based field overwrite per `DEC-bd5492`, preserving authoritative state and audit chain |

The honesty discipline is the section's defining trait. A reader who finds an aspirational claim in a Compliance chapter (an attested control, an audited statement, a guaranteed SLA) should treat it as a recorded gap if the chapter's drift inventory catches it, or as an undocumented gap to surface for the next cold-read. Compliance records what the readiness-baseline substrate provides.

**Governing source.** outline.md §4.8; DEC-ae331f.

## The Five Chapters That Follow

Compliance has six chapters: this overview plus the five chapters that follow. The grouping below is for navigation; section order is fixed by the outline and by chapter dependencies.

| Group | Chapters | What the group covers |
|---|---|---|
| Technical control surface | InfoSec and Access Control | Navigation entry for the JWT auth boundary, the scope guard, the platform-vs-tenant decorators, the docs anti-scraping mechanism, the supply-chain control as a technical surface |
| Risk and supplier substrate | Risk and Vendor Management | Navigation entry for the DevHub risk register, the eleven external vendor surfaces, the per-vendor failure mode, the recorded risk treatments |
| Framework conformance | ISO 27001 Conformance; SOC 2 Conformance | Navigation entry for the framework mappings: Annex A control families to substrate per ISO 27001:2022; Common Criteria, Confidentiality, and Processing Integrity mappings per SOC 2 Type I scope |
| Privacy substrate | Privacy and the Immutable Fact | Navigation entry for the sentinel-based nullification mechanism, the PII tier model, the per-jurisdiction deadline encoding, the evidence-extension pattern, the S3 WORM marker pattern |

The four groups cover the five chapters that follow without overlap. A chapter that does not fit a group is a chapter that does not belong in Compliance.

**Governing source.** outline.md §4.8.

## Reading Sequence

The five chapters can be read in outline order, but the section also supports audience-specific reading paths. The order below is intentional: each later chapter assumes the prior chapters' substrates where they share a common conformance concern.

| Reader intent | Recommended sequence | Why |
|---|---|---|
| Architectural orientation | InfoSec and Access Control; ISO 27001 Conformance; SOC 2 Conformance; the rest as needed | The architectural reader builds the conformance mental model from the technical-control surface outward to the framework mappings |
| External auditor (ISO 27001) | ISO 27001 Conformance; InfoSec and Access Control; Risk and Vendor Management; Privacy and the Immutable Fact | The auditor reads the framework mapping first, then the technical-control evidence, then the risk register, then the privacy mechanism |
| External auditor (SOC 2) | SOC 2 Conformance; InfoSec and Access Control; Risk and Vendor Management; Privacy and the Immutable Fact | Parallel to the ISO path with SOC 2 as the entry point |
| Privacy reviewer (DPO, GDPR controller) | Privacy and the Immutable Fact; InfoSec and Access Control; Risk and Vendor Management; ISO 27001 Conformance | The privacy reviewer reads the nullification mechanism and the access-control boundary first, then the risk register, then the framework mapping for A.8.10 |
| Procurement and risk officer | Risk and Vendor Management; InfoSec and Access Control; ISO 27001 Conformance; SOC 2 Conformance | Procurement reads the vendor inventory and the recorded risks first, then the technical-control surface, then the framework mappings |
| Engineering | InfoSec and Access Control; Privacy and the Immutable Fact; Risk and Vendor Management; the rest as needed | Engineering reads the technical control surface first, then the privacy mechanism's runtime substrate, then the risk register |

The reading sequences do not reorder the chapters in the section. They guide a reader who needs to extract a coherent subset for a specific purpose.

**Governing source.** outline.md §4.8.

## Boundaries with Other Sections

Compliance reports against the substrate. The boundaries with other sections are explicit and one-way: every prior section produces the substrate; Compliance reads it.

| Section | Boundary role | What crosses the boundary |
|---|---|---|
| Foundation | Binds Compliance as locked authority | Compliance chapters cite Invariants (especially Invariant III for Privacy and the Immutable Fact), the Object Model, the Authority Model as the architectural authority |
| Operating Model | Binds Compliance as locked authority | Compliance chapters cite the contract-execution runtime as the processing-integrity substrate; the Chain Completeness SSOT per `DEC-bebaec` is the SOC 2 PI authority |
| Implementation | Binds Compliance as locked authority | Compliance chapters cite Backend Services (the bc-core auth boundary), Data Model and Schema (the database substrate), Audit and Activity Logging (the audit trail) |
| AI | Adjacent | AI chapters describe AI participation; Compliance reports the AI's per-gate verdict trail and the AI provider risk surface |
| Development | Adjacent | Development chapters govern DevHub (the change-record substrate that Compliance cites as the ISO 27001 plan-and-report pair), Decision and Change Procedure (the engineering session discipline), Quality Assurance (the preventive-control surface) |
| Onboarding | Adjacent | Onboarding chapters govern the SOPs that Compliance reads as the operational-policy substrate |
| Operations | Adjacent | Operations chapters govern Incident and Change Management (the incident-response substrate), Observability and Telemetry (the monitoring surface), Performance and Scale (the per-tenant isolation), Tenant Lifecycle and Subscription (the offboarding-erasure trigger) |

Compliance is the consumer; the prior sections are the producers. Compliance does not author the substrate.

**Governing source.** outline.md §4.8; The Authority Model.

## Cross-Cutting Concerns

Several concerns thread the five Compliance chapters. The matrix below routes the reader to the chapter that owns each concern; per pattern 87, the matrix locates the concern and does not restate the behavior.

| Concern | Owning chapter | Adjacent chapters that thread it |
|---|---|---|
| Authentication boundary | InfoSec and Access Control (the JWT plus ScopeGuard surface) | ISO 27001 Conformance (A.8.2 Privileged access; A.8.3 Information access restriction); SOC 2 Conformance (CC6 Logical access) |
| Two-database isolation | InfoSec and Access Control (the structural isolation discipline) | ISO 27001 Conformance (A.8.3); SOC 2 Conformance (Confidentiality category) |
| Risk treatment | Risk and Vendor Management (the DevHub register) | ISO 27001 Conformance (the risk register as ISO 27001 mandatory substrate); SOC 2 Conformance (CC3 Risk Assessment) |
| Supply-chain control | Risk and Vendor Management (the CodeArtifact mitigation; `RSK-cb8929`) | InfoSec and Access Control (the technical surface); ISO 27001 Conformance (A.5.20 Supplier relationships) |
| Audit trail | Audit and Activity Logging in Implementation (the substrate authority) | ISO 27001 Conformance (A.8.15 Logging); SOC 2 Conformance (CC2 Communication; CC4 Monitoring) |
| Change-record plan-and-report pair | Decision and Change Procedure in Development (the procedure authority) | ISO 27001 Conformance (A.5.36 Compliance with policies); SOC 2 Conformance (CC8 Change management) |
| Internal-audit substrate | Quality Assurance in Development (the bc-qa harness); Decision and Change Procedure (the ADR audit script) | ISO 27001 Conformance (the internal-audit mapping); SOC 2 Conformance (CC4 Monitoring) |
| Privacy erasure mechanism | Privacy and the Immutable Fact (the nullification authority) | ISO 27001 Conformance (A.8.10 Information deletion); SOC 2 Conformance (Privacy criterion's deferred substrate) |
| Processing-integrity SSOT | Chain Completeness and Verdict in Operating Model (the substrate authority) | SOC 2 Conformance (Processing Integrity category) |
| Session-close gate | DevHub in Development (the gate implementation); Decision and Change Procedure (the override discipline) | SOC 2 Conformance (CC9 Risk mitigation) |
| Staged pursuit posture | `DEC-ae331f` (the load-bearing decision) | ISO 27001 Conformance (the readiness posture); SOC 2 Conformance (the Type I reduced-scope posture); Privacy and the Immutable Fact (the Privacy criterion's deferral) |

The matrix is navigation. Following the cell to the owning chapter produces the chapter's substantive treatment; following the cell to an adjacent chapter produces the partial treatment that chapter carries.

**Governing source.** outline.md §4.8; per-chapter Boundaries with Other Chapters tables.

## Constraints

| Constraint | Form |
|---|---|
| Honesty over aspiration | The chapters record substrate, not attestation; gaps are inventoried explicitly per pattern 81 |
| Staged pursuit per `DEC-ae331f` | ISO 27001 readiness baseline plus certification after pilot; SOC 2 Type I on Security plus Confidentiality plus Processing Integrity; Availability and Privacy gated on maturity |
| Nullification per `DEC-bd5492` | Privacy erasure operates through sentinel-based field overwrite; authoritative state is preserved; the audit chain is extended |
| Three of five Trust Services Criteria | The SOC 2 Type I scope is reduced; Availability and Privacy are forward-looking |
| Risk register is canonical | DevHub `risks` table; ADR cross-references point at the registry row |
| Reporting role | Compliance chapters report; they do not author the substrate |
| Voice discipline | Every chapter passes the AWS rewrite checklist's pre-commit grep before commit |
| ISO/IEC 27001:2022 standard choice | The four-theme Annex A revision; the 2013 revision's control numbers are accepted as historical references where they appear |

**Governing source.** outline.md §2; outline.md §4.8; DEC-ae331f.

## Governing Decisions

The Compliance section rests on the ADRs below. Each row carries the bounded scope language per pattern 87.

| ADR | Title | Scope of governance over Compliance |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus a home | Governs documentation structure: Compliance is the eighth top-level section; this overview's chapter map and section composition derive from the spine |
| DEC-376587 | Section renames | Governs documentation structure: the section name "Compliance" is the section's canonical label |
| DEC-ae331f | Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria | Governs the section's load-bearing posture: readiness baseline plus certification after pilot; reduced TSC scope; Availability and Privacy gated |
| DEC-bd5492 | GDPR/DPDP/CCPA Nullification Object | Governs the Privacy and the Immutable Fact chapter; sentinel-based privacy erasure |
| DEC-1918d0 | Two-database split | Governs the access-isolation substrate that InfoSec and Access Control records and that ISO 27001 and SOC 2 cite |
| DEC-771baf | Tenant database topology | Governs the tenant-isolation refinement |
| DEC-441665 | NPM supply chain mitigation via AWS CodeArtifact | Governs the supply-chain control that Risk and Vendor Management records |
| DEC-ee6018 | bc-qa standalone repo | Governs the preventive-control authority that ISO 27001 and SOC 2 cite |
| DEC-bebaec | Chain Completeness SSOT | Governs the processing-integrity authority that SOC 2 PI cites |
| DEC-804874 | L-Node Verification with Semantic Family Classification | Governs the session-close gate that SOC 2 CC9 cites |
| DEC-ebf0b4 | Session Discipline and Data Integrity Rules | Governs the engineering-session discipline that operates as the de facto information-security policy |

This overview routes governance to the owning chapter. The bounded scope language above prevents this overview from claiming authority over the platform behavior the ADRs govern; the chapter that owns the topic carries the substantive treatment.

**Governing source.** outline.md §4.8; per-chapter `governing_adrs` frontmatter.

## References

- Foundation (the locked architectural authority)
- The Authority Model
- The Object Model
- The Invariants
- Operating Model: Overview
- Implementation: Overview
- AI: Overview
- Development: Overview
- Onboarding: Overview
- Operations: Overview
- InfoSec and Access Control
- Risk and Vendor Management
- ISO 27001 Conformance
- SOC 2 Conformance
- Privacy and the Immutable Fact
- DEC-c06f41 (Spine expansion to eight sections plus a home)
- DEC-376587 (Section renames)
- DEC-ae331f (Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria)
- DEC-bd5492 (GDPR/DPDP/CCPA Nullification Object)
- DEC-1918d0 (Two-database split)
- DEC-771baf (Tenant database topology)
- DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact)
- DEC-ee6018 (bc-qa standalone repo)
- DEC-bebaec (Chain Completeness SSOT)
- DEC-804874 (L-Node Verification with Semantic Family Classification)
- DEC-ebf0b4 (Session Discipline and Data Integrity Rules)
- bc-docs-v3 outline.md (section structure)
- bc-docs-v3 HANDOFF.md (current drafting state)
