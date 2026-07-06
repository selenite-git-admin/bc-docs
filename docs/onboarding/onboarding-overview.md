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
  - DEC-c06f41 (Spine expansion to eight sections plus home; Onboarding section shape)
  - DEC-1918d0 (Two-database split; Onboarding writes platform-scope artifacts the tenant later consumes)
  - DEC-771baf (Tenant database topology; Onboarding's tenant scope produces tenant-scope substrate)
  - DEC-d72560 (Canonical Field as third contract primitive; Onboarding keeps BF and CF vocabulary lanes separate)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Onboarding: Overview

## Scope

This chapter is the section opener for Onboarding. It states what Onboarding is and what role it plays in the documentation, maps the fifteen chapters that follow this overview into reading groups, gives a recommended reading sequence by audience, declares the boundaries between Onboarding and the other sections of the documentation, and records the as-built discipline under which Onboarding chapters are written.

This chapter does not redefine any Onboarding claim. Source Registration, Seed Catalog Management, Metric Seed Catalog Management, Business Field and Business Object Onboarding, Canonical Field Seeding, Source and Admission Contract Creation, Observation Contract Creation, Canonical Contract Creation, Metric Contract Creation, Reader Creation, Metric Registration, MC Chain Integrity, Data Seeding and Build Order, Multi-Standard Onboarding, and Tenant Onboarding each govern their own claims. This overview locates them; it does not restate them with authority. Where this overview names a section-wide property, the governing source is the outline that records Onboarding's structure or the chapter that owns the property.

This chapter exists so that a reader who opens Onboarding cold can locate any specific chapter without having read the others, and so that a reader who has finished Onboarding can hold the fifteen chapters that follow as one coherent set rather than as fifteen independent files.

**Governing source.** outline.md §4.6.

## What Onboarding Means

Onboarding is the descriptive authority for the platform's governed sequences. Where Foundation defines the architectural rules and Operating Model defines the contract-execution runtime, Onboarding describes the procedures that build the platform's contract chain up from source structure to metric snapshot, register the standards-sourced vocabulary that the chain consumes, and bring tenants onto the platform so their data is observed through the chain.

| Property | Operational form |
|---|---|
| Procedural | Onboarding chapters describe the governed sequences the platform admits. Each chapter is a procedure, not a runtime act. The runtime acts are owned by Operating Model; the procedures that produce the artifacts the runtime consumes are owned here. |
| Per-artifact and end-to-end | Most Onboarding chapters govern the creation of one artifact (Source Registration produces catalog rows; Metric Contract Creation produces an MC). Two chapters govern end-to-end sequencing across multiple artifacts (Data Seeding and Build Order; Tenant Onboarding). The two scopes coexist; the per-artifact chapters are the building blocks the end-to-end chapters sequence. |
| Standards-anchored where possible | The vocabulary chapters (Business Field and Business Object Onboarding, Multi-Standard Onboarding) source from authoritative published standards (OAGIS, ISO 20022, XBRL, IFRS, UN/CEFACT) before falling back to BareCount Standard. Standards-anchored vocabulary inherits the standard's authority; BareCount Standard vocabulary earns its authority through additional gates. |
| Gate-enforced | Every Onboarding chapter is gated. The gates are AI verification (Source Registration, Metric Registration), structural completeness (contract creation chapters), bidirectional alignment (CF Seeding, MC Chain Integrity), and one-then-many discipline (Data Seeding and Build Order, Tenant Onboarding). The gates are not optional; bypassing a gate produces an artifact the chapter does not admit. |
| Foundation-and-Operating-Model-bound | Every Onboarding chapter consumes Foundation and Operating Model as locked authority. An Onboarding claim that contradicts a Foundation invariant or an Operating Model rule is incorrect against the platform's architecture, regardless of what the procedure happens to do. |
| Section-internal sequencing | Many Onboarding chapters depend on prior Onboarding chapters: contract creation depends on vocabulary; tenant onboarding depends on operational chains; chain integrity depends on existing MCs. The dependency direction is recorded in each chapter's prerequisites; this overview does not re-record it. |

The procedural-and-gated discipline is the section's defining trait. A reader who finds a procedure that bypasses a gate should treat the bypass as drift, not as the chapter's authority. The chapter's authority is the gated procedure; the bypass is recorded as drift if it exists.

**Governing source.** outline.md §4.6; The Authority Model.

## The Fifteen Chapters That Follow

Onboarding has sixteen chapters: this overview plus the fifteen chapters that follow. The grouping below is for navigation; section order is fixed by the outline and by chapter dependencies.

| Group | Chapters | What the group covers |
|---|---|---|
| Catalog substrate | Source Registration; Seed Catalog Management; Metric Seed Catalog Management | Navigation entry for the chapters that admit source structure (catalog rows) and curated reference data (seed catalogs for source tables and metrics). The catalog substrate is the input every later chapter consumes. |
| Vocabulary | Business Field and Business Object Onboarding; Canonical Field Seeding; Multi-Standard Onboarding | Navigation entry for the chapters that produce the platform's two-vocabulary substrate (BFs and BOs in source vocabulary; CFs in metric vocabulary) and the multi-standard generalization that admits ISO 20022, XBRL, IFRS, UN/CEFACT, and BareCount Standard sources. |
| Contract families | Source and Admission Contract Creation; Observation Contract Creation; Canonical Contract Creation; Metric Contract Creation | Navigation entry for the chapters that author the four chain-contract families. SC and AC declare source structure and admission rules; OC binds source fields to BFs; CC translates BFs to CFs and declares CO shape; MC binds CFs into formulas and produces Metric Snapshots. |
| Runtime infrastructure | Reader Creation | Navigation entry for the chapter that creates the Reader, the platform's UniBAT runtime substrate that executes the OC. |
| Metric registration and integrity | Metric Registration; MC Chain Integrity | Navigation entry for the chapter that admits metrics from the seed catalog into the platform metric catalog and the chapter that walks existing MCs through end-to-end integrity checks. |
| End-to-end orchestration | Data Seeding and Build Order; Tenant Onboarding | Navigation entry for the two chapters that sequence multiple per-artifact chapters. Data Seeding and Build Order is the platform-side build sequence (the chain). Tenant Onboarding is the customer-side sequence (one tenant onto the operational chain). |

The six groups cover the fifteen chapters that follow without overlap. A chapter that does not fit a group is a chapter that does not belong in Onboarding.

**Governing source.** outline.md §4.6.

## Reading Sequence

The fifteen chapters can be read in outline order, but the section also supports audience-specific reading paths. The order below is intentional: each later chapter assumes the prior chapters' procedures where they share a common artifact.

| Reader intent | Recommended sequence | Why |
|---|---|---|
| Architectural orientation | Source Registration; Business Field and Business Object Onboarding; Canonical Field Seeding; Source and Admission Contract Creation; Observation Contract Creation; Canonical Contract Creation; Metric Contract Creation; the rest as needed | The architectural reader builds the platform's contract chain mental model from catalog up; Reader Creation, Metric Registration, MC Chain Integrity, Data Seeding and Build Order, Multi-Standard Onboarding, Tenant Onboarding are each navigable as topics arise |
| Engineering | Source Registration; Seed Catalog Management; Reader Creation; Source and Admission Contract Creation; Observation Contract Creation; the rest as needed | Engineering reads the substrate-and-runtime first (catalog, seed, Reader), then the contracts that wire to the runtime; CC and MC chapters follow when engineering touches the metric layer |
| Operations | Tenant Onboarding; Data Seeding and Build Order; MC Chain Integrity; Reader Creation; the rest as needed | Operations reads the customer-facing procedures first (Tenant Onboarding), then the platform-side build sequence (Data Seeding), then the integrity walks; per-artifact chapters follow as remediation depths require |
| Audit and compliance | Source Registration; Metric Registration; Source and Admission Contract Creation; MC Chain Integrity; Tenant Onboarding; the rest as needed | Audit reads the gates first (Source Registration's AI verification; Metric Registration's four registration gates; SC and AC structural completeness; MC Chain Integrity's twelve problem classes; Tenant Onboarding's Subscription artifact authoring), then per-artifact chapters as control-mapping depth requires |
| Frontend | Source Registration; Reader Creation; Tenant Onboarding; the rest as needed | Frontend reads the chapters whose surfaces the bc-admin UI exposes (Source Catalog browsers; Reader configuration; tenant onboarding wizards); other chapters follow as the UI surfaces grow |

The reading sequences do not reorder the chapters in the section. They guide a reader who needs to extract a coherent subset for a specific purpose.

**Governing source.** outline.md §4.6.

## Boundaries with Other Sections

Onboarding describes governed procedures. The boundaries with other sections are explicit and one-way: Foundation, Operating Model, and Implementation bind Onboarding; AI provides the gate envelope Onboarding chapters consume; Operations and Compliance consume Onboarding's outputs.

| Section | Boundary role | What crosses the boundary |
|---|---|---|
| Foundation | Binds Onboarding as locked authority | Onboarding chapters cite Invariants, the Object Model, the Contract Grammar, the Evaluation Boundaries, the Authority Model as already-defined authority. Onboarding produces artifacts that the runtime acts (Operating Model) consume; it does not redefine Foundation. |
| Operating Model | Binds Onboarding as locked authority | Onboarding chapters cite Sources and the Catalog (the catalog Source Registration writes), Admission and Observation (the runtime acts the OC governs), Canonical Evaluation (the runtime act the CC governs), Metric Evaluation (the runtime act the MC governs), Tenancy and Binding (the tenant scope Tenant Onboarding produces). Onboarding is the procedural authority; Operating Model is the runtime authority |
| Implementation | Binds Onboarding as locked authority | Onboarding chapters cite the API surface (the endpoints procedures call), Data Model and Schema (the persistent stores procedures write to), Audit and Activity Logging (the change records procedures produce). Onboarding does not redefine Implementation |
| AI | Provides the gate envelope Onboarding consumes | Source Registration cites AI Gates and AI Trust and Verification for the maker-checker-gate envelope at AI verification; Metric Registration cites the same; Business Field and Business Object Onboarding cites it for certification dedup, BO approval, PII classification; MC Chain Integrity cites it for the CF-to-BF semantic review |
| Development | Adjacent | Development governs DevHub, decision and change procedure, build and release; Onboarding consumes DevHub for session management and change records but does not redefine the Development discipline |
| Operations | Consumes Onboarding | Operations chapters (Tenant Lifecycle and Subscription, Operations: Overview when drafted, Security Operations, Upgrade and Migration) consume the artifacts Onboarding produces. Tenant Lifecycle and Subscription is the artifact authority for the Subscription record Tenant Onboarding produces; this chapter's Tenant Onboarding cites the artifact authority |
| Compliance | Consumes Onboarding | Compliance chapters cite the Onboarding gates as the platform's preventive controls (Source Registration AI verification, Metric Registration four gates, BF and BO certification gates, MC validation gates) and the change records the procedures produce. Compliance reports conformance against Onboarding; it does not produce Onboarding authority |

The dependency direction is one-way. An Onboarding chapter that depends on a later section for its own correctness is a boundary violation. A later section that redefines an Onboarding procedure instead of consuming it is also a boundary violation.

**Governing source.** outline.md §4.6; The Authority Model; Operating Model: Overview; Implementation: Overview; AI: Overview.

## Cross-Cutting Concerns

Several concerns thread through multiple Onboarding chapters. The cross-cutting nature is intentional; the concerns are stated in each chapter where they apply rather than centralized in one chapter that the others would then need to consult separately.

| Concern | Chapters that thread it | How it is preserved |
|---|---|---|
| AI verification gate | Source Registration; Seed Catalog Management; Metric Seed Catalog Management; Business Field and Business Object Onboarding; Multi-Standard Onboarding; Metric Registration; MC Chain Integrity | Follow AI Gates and AI Trust and Verification first; each chapter records its own verdict-routing rule and the gate's specific question set |
| Two-vocabulary discipline | Canonical Field Seeding; Observation Contract Creation; Canonical Contract Creation; Metric Contract Creation; MC Chain Integrity | Follow The Contract Grammar and DEC-d72560 first; the BF-vocabulary side and the CF-vocabulary side stay separate, with the CC as translator |
| One-then-many (D268) | Business Field and Business Object Onboarding; Source and Admission Contract Creation; Observation Contract Creation; Canonical Contract Creation; Metric Contract Creation; Data Seeding and Build Order; MC Chain Integrity; Tenant Onboarding | Follow the ADR for D268 (session discipline); each chapter records its own one-then-many enforcement (the first item of a bulk batch passes the full gate; if it fails, the entire batch is rejected) |
| Standards-sourced auto-certification | Business Field and Business Object Onboarding; Multi-Standard Onboarding | Follow Business Field and Business Object Onboarding for the OAGIS-specific case; Multi-Standard Onboarding generalizes to other standards with the same auto-certification rule plus the additional tier-3 gates for BareCount Standard |
| Demand-pull discipline | Canonical Field Seeding; MC Chain Integrity | Follow Canonical Field Seeding for the rule (every CF is traceable to a metric formula variable or a grain reference; no speculative CFs); MC Chain Integrity reinforces it (the diagnostic catches dead field references and missing BF source) |
| Two-database split (platform-tenant) | Tenant Onboarding; (every Onboarding chapter that produces platform-scope artifacts a tenant later consumes) | Follow DEC-1918d0 and DEC-771baf; platform-scope artifacts (catalog rows, BFs, BOs, contracts, Readers, metric definitions) live in the platform database; tenant-scope substrate (tenant Connections, runtime rows in tenant DB, Subscription records, Cognito users with `custom:tenant_id`) is governed by Tenant Onboarding |
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
| Forbidden-vocabulary scrub | The forbidden roots (the ETL-style framing tokens listed in `outline.md` §2) are not used in body prose. Replacements (observe, admit, evaluate, resolve, preserve, record, reference, bind, finalize, surface) are used instead |
| AI verification cannot be silently bypassed | Where a chapter declares an AI gate (Source Registration, Metric Registration, BF and BO certification, MC Chain Integrity), absence of the AI surface defers the procedure with explicit drift recording, never silent admission |
| Direct DB writes are forbidden | Catalog mutations, contract mutations, and metric mutations route through the API surface only. Direct SQL writes against the platform database bypass the audit substrate; the chapter does not admit such writes as governed activity |
| Voice and vocabulary discipline | No em dashes; no chapter numbers; section-mark byte integrity; the eighty-eight voice patterns in `aws-rewrite-checklist.md` apply to every chapter |

A chapter that violates any of these constraints is incorrect against the section's discipline.

**Governing source.** The Authority Model; outline.md §4.6; `scripts/reference/aws-rewrite-checklist.md`.

## Governing Decisions

| Decision | Scope in this overview | Boundary |
|---|---|---|
| DEC-c06f41 | Establishes the eight-section spine plus home and the Onboarding section shape that includes this overview and the fifteen following chapters | Governs documentation structure only; child chapters own their procedural claims |
| DEC-1918d0 | Supplies the two-database split as a cross-cutting concern readers will see across most Onboarding chapters (platform-scope artifacts vs tenant-scope substrate) | This overview routes the concern; child chapters own the database-write behavior |
| DEC-771baf | Supplies tenant database topology that Tenant Onboarding produces and other Onboarding chapters defer to | This overview routes the concern; Tenant Onboarding records the as-built tenant behavior |

**Governing source.** Decisions: ADR Registry; outline.md §4.6.

## References

- Source Registration
- Seed Catalog Management
- Metric Seed Catalog Management
- Business Field and Business Object Onboarding
- Canonical Field Seeding
- Source and Admission Contract Creation
- Observation Contract Creation
- Canonical Contract Creation
- Metric Contract Creation
- Reader Creation
- Metric Registration
- MC Chain Integrity
- Data Seeding and Build Order
- Multi-Standard Onboarding
- Tenant Onboarding
- Foundation: Overview
- Operating Model: Overview
- Implementation: Overview
- AI: Overview
- The Authority Model
- The Contract Grammar
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- outline.md §4.6: Onboarding


