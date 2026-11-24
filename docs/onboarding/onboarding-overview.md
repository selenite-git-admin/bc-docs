---
id: onboarding-overview
order: 49.9
title: "Onboarding: Overview"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-problem, the-solution, the-invariants, the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, the-dual-layer-interaction-model, operating-model-overview, implementation-overview, ai-overview]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Authority Model
  - The Contract Grammar
  - Operating Model: Overview
  - Implementation: Overview
  - AI: Overview
governing_adrs:
  - DEC-3395bc (bc-docs SSOT cutover: the documentation layout, chapter list, voice discipline and editorial gates)
  - DEC-c06f41 (Spine expansion to eight sections plus home; Onboarding section shape)
  - DEC-1918d0 (Two-database split; Onboarding writes platform-scope artifacts the tenant later consumes)
  - DEC-771baf (Tenant database topology; Onboarding's tenant scope produces tenant-scope substrate)
  - DEC-d72560 (Canonical Field as third contract primitive; Onboarding keeps BF and CF vocabulary lanes separate)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Onboarding: Overview

> **Bridging note.** Where this chapter refers to Business Field, Business Object, or Canonical Field, the semantic-identity role those primitives served is superseded by the **Business Concept Framework (BCF)** — the `concept_registry` schema (Entity / Characteristic / Business Concept), authored through governed ceremonies (AI panel + C5 operator-confirm + F3 write). The legacy `contract.business_field` / `contract.business_object` / canonical-field tables remain in use for OC/CC `field_selection` binding, so the mechanics described here stay valid for that purpose; for semantic identity — "what does this field mean?" — consult the BCF registry. Governing ADRs: DEC-02f5a9 (greenfield), DEC-61850f (adoption). See The Contract Grammar and The Object Model for the Registry model.

## Scope

This chapter is the section opener for Onboarding. It states what Onboarding is and what role it plays in the documentation, maps the nineteen chapters that follow this overview into reading groups, gives a recommended reading sequence by audience, declares the boundaries between Onboarding and the other sections of the documentation, and records the as-built discipline under which Onboarding chapters are written.

This chapter does not redefine any Onboarding claim. Source Registration, Seed Catalog Management, Canonical Field Seeding, Source and Admission Contract Creation, Observation Contract Creation, Canonical Contract Creation, Reader Creation, Multi-Standard Onboarding, Tenant Onboarding, Tenant Metric Binding and the eight metric onboarding chapters (Onboard one metric to the Metric Catalog, Onboard a business concept, Add a directory family and group, Add a directory member, Author and approve a metric contract, Link a directory member to its contract, Prove a metric version on the demo world, Certify and activate a metric version) each govern their own claims. The Metric Workstream Playbook is superseded by the metric onboarding chapters. Five earlier metric-side procedures (Metric Seed Catalog Management, Metric Contract Creation, Metric Registration, MC Chain Integrity, Data Seeding and Build Order) are archived in `docs/archive/onboarding/` and govern nothing. This overview locates them; it does not restate them with authority. Where this overview names a section-wide property, the governing source is the outline that records Onboarding's structure or the chapter that owns the property.

This chapter exists so that a reader who opens Onboarding cold can locate any specific chapter without having read the others, and so that a reader who has finished Onboarding can hold the nineteen chapters that follow as one coherent set rather than as nineteen independent files.

**Governing source.** DEC-3395bc.

## What Onboarding Means

Onboarding is the descriptive authority for the platform's governed sequences. Where Foundation defines the architectural rules and Operating Model defines the contract-execution runtime, Onboarding describes the procedures that build the platform's contract chain up from source structure to metric snapshot, register the standards-sourced vocabulary that the chain consumes, and bring tenants onto the platform so their data is observed through the chain.

| Property | Operational form |
|---|---|
| Procedural | Onboarding chapters describe the governed sequences the platform admits. Each chapter is a procedure, not a runtime act. The runtime acts are owned by Operating Model; the procedures that produce the artifacts the runtime consumes are owned here. |
| Per-artifact and end-to-end | Most Onboarding chapters govern the creation of one artifact (Source Registration produces catalog rows; Author and approve a metric contract produces an approved metric contract version). Two chapters govern end-to-end sequencing across multiple artifacts (Onboard one metric to the Metric Catalog; Tenant Onboarding). The two scopes coexist; the per-artifact chapters are the building blocks the end-to-end chapters sequence. |
| Standards-anchored where possible | The standards chapter (Multi-Standard Onboarding) sources from authoritative published standards (OAGIS, ISO 20022, XBRL, IFRS, UN/CEFACT) before falling back to BareCount Standard. Standards-anchored vocabulary inherits the standard's authority; BareCount Standard vocabulary earns its authority through additional gates. |
| Gate-enforced | Every Onboarding chapter is gated. The gates are AI verification and operator confirmation (Source Registration; Onboard a business concept, where a panel run and a confirm chain certify and write a concept), structural completeness (contract creation chapters; Author and approve a metric contract), bidirectional alignment (Canonical Field Seeding), proof against the demo world (Prove a metric version on the demo world), certification (Certify and activate a metric version), and one-then-many discipline (Tenant Onboarding). The gates are not optional; bypassing a gate produces an artifact the chapter does not admit. |
| Foundation-and-Operating-Model-bound | Every Onboarding chapter consumes Foundation and Operating Model as locked authority. An Onboarding claim that contradicts a Foundation invariant or an Operating Model rule is incorrect against the platform's architecture, regardless of what the procedure happens to do. |
| Section-internal sequencing | Many Onboarding chapters depend on prior Onboarding chapters: contract creation depends on vocabulary; tenant onboarding depends on operational chains; chain integrity depends on existing MCs. The dependency direction is recorded in each chapter's prerequisites; this overview does not re-record it. |

The procedural-and-gated discipline is the section's defining trait. A reader who finds a procedure that bypasses a gate should treat the bypass as drift, not as the chapter's authority. The chapter's authority is the gated procedure; the bypass is recorded as drift if it exists.

**Governing source.** DEC-3395bc; The Authority Model.

## The Chapters That Follow

Onboarding currently has **twenty** files in `docs/onboarding/`: this overview plus nineteen that follow, of which one (the Metric Workstream Playbook) is superseded and kept as a record. Five earlier metric-side procedures (Metric Seed Catalog Management, Metric Contract Creation, Metric Registration, MC Chain Integrity, Data Seeding and Build Order) are in `docs/archive/onboarding/` and are not routes to follow. The live metric procedure is the set of eight metric onboarding chapters below. The current cross-cutting index of platform workflows is the **[Platform-Side Workflow Catalog](../reference/platform-workflow-catalog.md)**. The grouping below is for navigation.

| Group | Chapters | What the group covers |
|---|---|---|
| Catalog substrate | Source Registration; Seed Catalog Management | Navigation entry for the chapters that admit source structure (catalog rows) and curated reference data (seed catalogs for source tables). The catalog substrate is the input every later chapter consumes. |
| Vocabulary | Canonical Field Seeding; Multi-Standard Onboarding | Navigation entry for the chapters that produce the canonical-field vocabulary (CFs in metric vocabulary) and the multi-standard generalization that admits ISO 20022, XBRL, IFRS, UN/CEFACT, and BareCount Standard sources. The identity of a business concept is authored in the metric onboarding group (Onboard a business concept). |
| Contract families | Source and Admission Contract Creation; Observation Contract Creation; Canonical Contract Creation | Navigation entry for the chapters that author the chain-contract families. SC and AC declare source structure and admission rules; OC binds source fields to certified Business Fields (`field_mappings`); CC selects Business Fields (`field_selection`), maps them to CFs and declares CO shape. The legacy BF tables stay in use for this binding; see the bridging note above. The metric contract is authored in the metric onboarding group (Author and approve a metric contract). |
| Runtime infrastructure | Reader Creation | Navigation entry for the chapter that creates the Reader, the platform's UniBAT runtime substrate that executes the OC. |
| Metric onboarding | Onboard one metric to the Metric Catalog; Business Field and Business Object Onboarding (file name kept; its title and body are now "Onboard a business concept"); Add a directory family and group; Add a directory member; Author and approve a metric contract; Link a directory member to its contract; Prove a metric version on the demo world; Certify and activate a metric version; Metric Workstream Playbook (superseded, a record only) | The walkthrough gives the order for one metric, from its seed to an active version; each task chapter does one step of that order in detail. These chapters replace the Metric Workstream Playbook, which stays as a superseded record. |
| Tenant | Tenant Onboarding; Tenant Metric Binding | Navigation entry for the customer-side sequence: one tenant onto the operational chain, and the binding of a metric to a tenant. |

The six groups cover the nineteen chapters that follow: eighteen live chapters and the superseded Metric Workstream Playbook, listed in the metric onboarding group as a record. A chapter that does not fit a group is a chapter that does not belong in Onboarding.

**Governing source.** DEC-3395bc.

## Reading Sequence

The chapters can be read in outline order, but the section also supports audience-specific reading paths. The order below is intentional: each later chapter assumes the prior chapters' procedures where they share a common artifact.

| Reader intent | Recommended sequence | Why |
|---|---|---|
| Architectural orientation | Source Registration; Onboard a business concept; Canonical Field Seeding; Source and Admission Contract Creation; Observation Contract Creation; Canonical Contract Creation; Onboard one metric to the Metric Catalog; the rest as needed | The architectural reader builds the platform's contract chain mental model from catalog up; Reader Creation, Multi-Standard Onboarding, Tenant Onboarding and the metric task chapters are each navigable as topics arise |
| Engineering | Source Registration; Seed Catalog Management; Reader Creation; Source and Admission Contract Creation; Observation Contract Creation; the rest as needed | Engineering reads the substrate-and-runtime first (catalog, seed, Reader), then the contracts that wire to the runtime; the canonical contract and the metric onboarding chapters follow when engineering touches the metric layer |
| Metric onboarding | Onboard one metric to the Metric Catalog; then the task chapter each of its steps names (Onboard a business concept; Add a directory family and group; Add a directory member; Author and approve a metric contract; Link a directory member to its contract; Prove a metric version on the demo world; Certify and activate a metric version) | The walkthrough gives the order and the decision points; each task chapter gives one task with its actor, grant, inputs, door, writes and failure modes |
| Operations | Tenant Onboarding; Tenant Metric Binding; Reader Creation; the rest as needed | Operations reads the customer-facing procedures first (Tenant Onboarding), then the tenant binding and the Reader; per-artifact chapters follow as remediation depths require |
| Audit and compliance | Source Registration; Source and Admission Contract Creation; Onboard a business concept; Certify and activate a metric version; Tenant Onboarding; the rest as needed | Audit reads the gates first (Source Registration's AI verification; the structural completeness of the SC and AC; the panel and confirm chain of a business concept; certification of a metric version; Tenant Onboarding's Subscription artifact authoring), then per-artifact chapters as control-mapping depth requires |
| Frontend | Source Registration; Reader Creation; Tenant Onboarding; the rest as needed | Frontend reads the chapters whose surfaces the bc-admin UI exposes (Source Catalog browsers; Reader configuration; tenant onboarding wizards); other chapters follow as the UI surfaces grow |

The reading sequences do not reorder the chapters in the section. They guide a reader who needs to extract a coherent subset for a specific purpose.

**Governing source.** DEC-3395bc.

## Boundaries with Other Sections

Onboarding describes governed procedures. The boundaries with other sections are explicit and one-way: Foundation, Operating Model, and Implementation bind Onboarding; AI provides the gate envelope Onboarding chapters consume; Operations and Compliance consume Onboarding's outputs.

| Section | Boundary role | What crosses the boundary |
|---|---|---|
| Foundation | Binds Onboarding as locked authority | Onboarding chapters cite Invariants, the Object Model, the Contract Grammar, the Evaluation Boundaries, the Authority Model as already-defined authority. Onboarding produces artifacts that the runtime acts (Operating Model) consume; it does not redefine Foundation. |
| Operating Model | Binds Onboarding as locked authority | Onboarding chapters cite Sources and the Catalog (the catalog Source Registration writes), Admission and Observation (the runtime acts the OC governs), Canonical Evaluation (the runtime act the CC governs), Metric Evaluation (the runtime act the MC governs), Tenancy and Binding (the tenant scope Tenant Onboarding produces). Onboarding is the procedural authority; Operating Model is the runtime authority |
| Implementation | Binds Onboarding as locked authority | Onboarding chapters cite the API surface (the endpoints procedures call), Data Model and Schema (the persistent stores procedures write to), Audit and Activity Logging (the change records procedures produce). Onboarding does not redefine Implementation |
| AI | Provides the gate envelope Onboarding consumes | Source Registration cites AI Gates and AI Trust and Verification for the maker-checker-gate envelope at AI verification; Onboard a business concept (file `business-field-and-business-object-onboarding.md`) cites it for the authoring panel, its verdicts and the operator-confirm chain that certifies and writes a concept |
| Development | Adjacent | Development governs DevHub, decision and change procedure, build and release; Onboarding consumes DevHub for session management and change records but does not redefine the Development discipline |
| Operations | Consumes Onboarding | Operations chapters (Tenant Lifecycle and Subscription, Operations: Overview when drafted, Security Operations, Upgrade and Migration) consume the artifacts Onboarding produces. Tenant Lifecycle and Subscription is the artifact authority for the Subscription record Tenant Onboarding produces; this chapter's Tenant Onboarding cites the artifact authority |
| Compliance | Consumes Onboarding | Compliance chapters cite the Onboarding gates as the platform's preventive controls (Source Registration AI verification, the business concept panel and operator-confirm chain, the metric approval and certification gates) and the change records the procedures produce. Compliance reports conformance against Onboarding; it does not produce Onboarding authority |

The dependency direction is one-way. An Onboarding chapter that depends on a later section for its own correctness is a boundary violation. A later section that redefines an Onboarding procedure instead of consuming it is also a boundary violation.

**Governing source.** DEC-3395bc; The Authority Model; Operating Model: Overview; Implementation: Overview; AI: Overview.

## Cross-Cutting Concerns

Several concerns thread through multiple Onboarding chapters. The cross-cutting nature is intentional; the concerns are stated in each chapter where they apply rather than centralized in one chapter that the others would then need to consult separately.

| Concern | Chapters that thread it | How it is preserved |
|---|---|---|
| AI verification gate | Source Registration; Seed Catalog Management; Onboard a business concept; Multi-Standard Onboarding; Author and approve a metric contract | Follow AI Gates and AI Trust and Verification first; each chapter records its own verdict-routing rule and the gate's specific question set |
| Two-vocabulary discipline | Canonical Field Seeding; Observation Contract Creation; Canonical Contract Creation; Author and approve a metric contract | Follow The Contract Grammar and DEC-d72560 first; the BF-vocabulary side and the CF-vocabulary side stay separate, with the CC as translator |
| One-then-many (D268) | Source and Admission Contract Creation; Observation Contract Creation; Canonical Contract Creation; Tenant Onboarding | Follow the ADR for D268 (session discipline); each chapter records its own one-then-many enforcement (the first item of a bulk batch passes the full gate; if it fails, the entire batch is rejected) |
| Standards-sourced auto-certification | Multi-Standard Onboarding | Follow Multi-Standard Onboarding for the tiered standards rule. Its tier-1 (OAGIS) rows still cite the earlier Business Field and Business Object Onboarding chapter, whose standards-derivation and auto-certification procedure is superseded (DEC-02f5a9, DEC-61850f) and is no longer in that file, which now holds the business concept procedure. Until Multi-Standard Onboarding is revised, read its tier-1 claims as drift, not as a route into the replacement chapter |
| Demand-pull discipline | Canonical Field Seeding | Follow Canonical Field Seeding for the rule (every CF is traceable to a metric formula variable or a grain reference; no speculative CFs) |
| Two-database split (platform-tenant) | Tenant Onboarding; (every Onboarding chapter that produces platform-scope artifacts a tenant later consumes) | Follow DEC-1918d0 and DEC-771baf; platform-scope artifacts (catalog rows, business concepts, contracts, Readers, metric definitions) live in the platform database; tenant-scope substrate (tenant Connections, runtime rows in tenant DB, Subscription records, Cognito users with `custom:tenant_id`) is governed by Tenant Onboarding |
| Foundation invariant respect | Every Onboarding chapter that touches a runtime act | Follow Foundation and Operating Model for the binding rules; each Onboarding chapter records any as-built drift in its own scope |

A chapter that introduces a new claim about any cross-cutting concern aligns with the threading discipline. A later section that consumes an Onboarding chapter consumes the cross-cutting concern as the chapter states it.

**Governing source.** The owning Onboarding chapters named in the table; The Authority Model; Foundation; Operating Model: Overview; AI: Overview; DEC-1918d0; DEC-771baf.

## Constraints

The constraints below apply to Onboarding as a whole and are inherited by every chapter in the section.

| Constraint | Operational form |
|---|---|
| Onboarding is procedural, not normative | Onboarding chapters describe what procedures the platform admits. The architectural rules are owned by Foundation; the runtime acts are owned by Operating Model. An Onboarding claim that redefines a runtime act is recorded as drift, never as redefinition of the act |
| Drift inventory is mandatory | Every Onboarding chapter that surveys a procedure maintains a drift inventory recording gaps between procedure intent and current state. The chapter does not present an aspirational procedure as if it were the as-built |
| Substrate-canonicality scope matches drift inventory | When a chapter spans procedures of varying maturity (canonical, functional, scaffolded, aspirational), the chapter's lead-paragraph scope statement matches the chapter's own drift inventory. A canonical claim that the chapter's own drift inventory immediately contradicts is internal incoherence |
| Behavior-search grounding for Foundation-invariant claims | An Onboarding chapter that asserts a Foundation invariant about runtime behavior verifies the claim against the code path the procedure produces. A name-based search alone is not sufficient grounding |
| Bidirectional citation discipline | Every `DEC-xxxxxx` and `FND-ERR-xxx` cited in body appears in frontmatter `governing_adrs` or `errata_referenced`, and vice versa. The Governing Decisions table is bidirectionally complete with frontmatter and body citations |
| Forbidden-vocabulary scrub | The forbidden roots (the ETL-style framing tokens listed in the Documentation System chapter) are not used in body prose. Replacements (observe, admit, evaluate, resolve, preserve, record, reference, bind, finalize, surface) are used instead |
| AI verification cannot be silently bypassed | Where a chapter declares an AI gate (Source Registration, Onboard a business concept, Author and approve a metric contract), absence of the AI surface defers the procedure with explicit drift recording, never silent admission |
| Direct DB writes are forbidden | Catalog mutations, contract mutations, and metric mutations route through the API surface only. Direct SQL writes against the platform database bypass the audit substrate; the chapter does not admit such writes as governed activity |
| Voice and vocabulary discipline | No em dashes; no chapter numbers; section-mark byte integrity; the eighty-eight voice patterns in `aws-rewrite-checklist.md` apply to every chapter |

A chapter that violates any of these constraints is incorrect against the section's discipline.

**Governing source.** The Authority Model; DEC-3395bc; `scripts/reference/aws-rewrite-checklist.md`.

## Governing Decisions

| Decision | Scope in this overview | Boundary |
|---|---|---|
| DEC-c06f41 | Establishes the eight-section spine plus home and the Onboarding section shape that includes this overview and the nineteen following chapters | Governs documentation structure only; child chapters own their procedural claims |
| DEC-1918d0 | Supplies the two-database split as a cross-cutting concern readers will see across most Onboarding chapters (platform-scope artifacts vs tenant-scope substrate) | This overview routes the concern; child chapters own the database-write behavior |
| DEC-771baf | Supplies tenant database topology that Tenant Onboarding produces and other Onboarding chapters defer to | This overview routes the concern; Tenant Onboarding records the as-built tenant behavior |

**Governing source.** Decisions: ADR Registry; DEC-3395bc.

## References

- Source Registration
- Seed Catalog Management
- Canonical Field Seeding
- Source and Admission Contract Creation
- Observation Contract Creation
- Canonical Contract Creation
- Reader Creation
- Multi-Standard Onboarding
- Tenant Onboarding
- Tenant Metric Binding
- Onboard one metric to the Metric Catalog
- Onboard a business concept
- Add a directory family and group
- Add a directory member
- Author and approve a metric contract
- Link a directory member to its contract
- Prove a metric version on the demo world
- Certify and activate a metric version
- Foundation: Overview
- Operating Model: Overview
- Implementation: Overview
- AI: Overview
- The Authority Model
- The Contract Grammar
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-3395bc: Onboarding


