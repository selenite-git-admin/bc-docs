---
id: architecture
order: 16
title: "Architecture"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-invariants, the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, the-dual-layer-interaction-model, operating-model-overview]
governing_sources:
  - Foundation
  - The Invariants
  - The Object Model
  - The Contract Grammar
  - The Evaluation Boundaries
  - The Authority Model
  - The Dual-Layer Interaction Model
  - Operating Model
governing_adrs:
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules)
  - DEC-771baf (Tenant database topology; platform-tenant one-way dependency)
  - DEC-e50b83 (Master port reservation)
  - DEC-9b23a7 (pm2 removed; independent service startup)
  - DEC-3395bc (v3 documentation structure; bc-core JWT-guarded /api/docs/*)
  - DEC-b97390 (bc-admin embedded documentation reader)
  - DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact)
  - DEC-324d9e (Subscription tiers and hosting variants)
  - DEC-c06f41 (Spine expansion to eight sections plus home)
errata_referenced: []
v2_sources:
  - legacy-v2/docs/architecture/index.md
  - legacy-platform-docs/docs/about-platform/architecture/principles.md
  - legacy-platform-docs/docs/about-platform/architecture/taxonomy.md
diagrams:
  - DG-architecture-conceptual
  - DG-architecture-layers
  - DG-architecture-two-db
  - DG-architecture-composition
---

# Architecture

## Scope

This chapter describes the architectural shape of the BareCount platform: the commitments the architecture rests on, the layers and surfaces that compose it, the execution spine that produces authoritative state, the contract chain that governs that production, the repository composition that realizes it, the port reservation that stabilizes local service identity, the end-to-end path from source state to delivered output, the cross-cutting concerns that thread through every layer, the residency boundary that hosting variants must preserve, the RACI of who does what, the evolution that brought the architecture to its current shape, and the decisions that govern it.

This chapter is the architectural view. It does not redefine Foundation invariants, the Object Model, the Contract Grammar, the Evaluation Boundaries, the Authority Model, or the Dual-Layer Interaction Model. It does not redefine Operating Model contract execution. It does not enumerate per-service detail (deferred to Backend Services, Internal Modules, Auxiliary Services), AI service depth (deferred to AI Architecture), AWS network and compute and secret detail (deferred to Infrastructure), database schemas (deferred to Data Model and Schema), endpoint catalogues (deferred to API Surface), frontend specifics (deferred to Frontend Experience), build configuration (deferred to Build and Release), code quality discipline (deferred to Quality Assurance), or developer tooling setup (deferred to Developer Experience).

The chapter sits between Foundation and the rest of Implementation. Foundation tells the reader what BareCount is. The Operating Model tells the reader how it works at runtime. Architecture tells the reader how the platform is shaped: the commitments, the layers, the spine, the chain, the composition.

Four diagrams accompany the chapter prose: a conceptual view of sources, the four-boundary spine, and delivery; a layers-and-surfaces map; a two-database topology with one-directional authority; and a repository composition. Each is a navigation aid for the prose, not the spec.

![Architecture: Conceptual View](/docs/assets/diagrams/DG-architecture-conceptual.svg)

**Governing source.** Foundation; outline.md §4.3.

## Architectural Commitments

Six commitments are the architectural posture of the platform. Each is a Foundation invariant or a Foundation-derived principle. The architecture realizes them; it does not relitigate them.

| Commitment | What it means in architectural terms | Foundation source |
|---|---|---|
| Determinism | Same inputs plus same contracts produce the same authoritative outputs. The architecture admits no environment-specific behavior, no hidden randomness, no machine-local defaults that change results. | The Invariants (derived from Invariants I and V together) |
| Contracts over convenience | Every state-producing act traverses a versioned contract. The architecture admits no shortcut path that bypasses contract governance, no ad-hoc table join that produces metric-shaped output without a Metric Contract, no privileged write that produces a Source Object outside admission. | The Invariants (Invariant I); The Contract Grammar |
| Immutability and append-only progression | Authoritative state is never updated in place. Corrections are new versions, recorded as new objects with explicit references to the prior versions. The architecture admits no schema for retraction, no UPDATE on Source Objects or Canonical Objects or Metric Snapshots or Action Objects, no compensating write that mutates a prior boundary's emission. | The Invariants (Invariant III); The Object Model |
| Feed-forward only | State traverses the four boundaries in a fixed order (admission, canonical evaluation, metric evaluation, action evaluation). No boundary reads from a later boundary. No boundary mutates a prior boundary's emission. The architecture admits no back-reference path. | The Invariants (Invariant II); The Object Model; The Evaluation Boundaries |
| Evidence emitted, not reconstructed | Proof of an evaluation exists only because it was recorded at the boundary that produced authoritative state. The architecture admits no log-replay path, no "we can rebuild evidence from operational telemetry" claim, no inference of Evidence or Lineage from anything other than the act that produced them. | The Invariants (Invariant VI); The Object Model |
| The platform does not decide | The platform evaluates, measures, records, and surfaces. It does not autonomously modify policy, escalate without governed authoring, or replace human decision authority. The architecture admits AI as advisory under the Conversation surface; AI may read the Trust surface but never writes it. | The Dual-Layer Interaction Model |

The six commitments interlock. An architectural change that violates one usually violates several. A proposed architectural change that appears to honor all six but does so by relaxing the meaning of any of them is incorrect against the platform's architectural posture.

**Governing source.** The Invariants; The Object Model; The Contract Grammar; The Evaluation Boundaries; The Dual-Layer Interaction Model.

## Layers and Surfaces

![Architecture: Layers and Surfaces](/docs/assets/diagrams/DG-architecture-layers.svg)

The architecture is organized as a small set of layers and surfaces. Naming them is the architecture's first task, because every later concern (auth, lineage, observability, residency) is defined by where it sits in this map.

### Two interaction surfaces

| Surface | Authority | What lives here | Read and write rules |
|---|---|---|---|
| Trust surface | Authoritative, immutable | Source Objects, Canonical Objects, Metric Snapshots, Action Objects, Evidence, Lineage, governed grammar artifacts (contracts, primitives, mappings), governance records (decisions, change records, activity log) | Writes only through governed evaluation acts and governed authoring acts. Reads do not produce or modify state. |
| Conversation surface | Advisory, ephemeral | AI Panel content, conversational suggestions, agent outputs that have not been promoted to governed state | May read the Trust surface freely. May not write the Trust surface. Promotion to authoritative state requires a governed authoring act. |

The asymmetry between the two surfaces is a Foundation claim and a load-bearing architectural commitment. Cross-Cutting Concerns later in this chapter shows how each cross-cutting concern is defined differently for each surface.

### Three planes within the Trust surface

Within the Trust surface, three planes separate concerns by responsibility.

| Plane | What it owns | Stored in | Service that hosts |
|---|---|---|---|
| Control plane | Contract authoring and registry; Source Catalog; master data; tenant identity records; Subscription records; governance state; chain status; AI Contract grammar | Platform DB | bc-core (control-plane modules) plus DevHub for governance protocol |
| Execution plane | The four boundary acts (admission, canonical evaluation, metric evaluation, action evaluation); Source Objects, Canonical Objects, Metric Snapshots, Action Objects; Evidence and Lineage; Run records (admission, canonical, metric, action) | Tenant DB | bc-core (boundary modules) |
| Delivery plane | Tenant-facing UI surfaces; platform-facing UI surfaces; read APIs for analytics integration; read-only AI visibility surfaces | Read-only views over Platform DB and Tenant DB; later in the spine than execution | bc-portal, bc-admin, bc-core delivery routes, and bc-ai visibility routes |

The control plane authors and governs. The execution plane runs the boundaries and produces authoritative state. The delivery plane surfaces results. External write-back and AI-triggered authoring are adjacent integration paths that consume delivered state; they are not delivery-plane writes and require their own governed act before any authoritative state changes. None of the three planes consumes a later plane: control plane state is the input to execution; execution state is the input to delivery; delivery does not author or execute.

### Two ownership boundaries

The architecture rests on a strict ownership boundary between platform and tenant.

| Side | What is owned | Where it is stored | Who writes |
|---|---|---|---|
| Platform side | All contract definitions, Source Catalog entries, master data, governance records, chain status, Subscription records, tenant identity records | Platform DB (`bc_platform_dev`) | Platform-side governance acts; bc-core control-plane modules |
| Tenant side | All execution data: Source Objects, Canonical Objects, Metric Snapshots, Action Objects, Evidence, Lineage, Run records, Connections, Contract Bindings, tenant-scoped extension content | Tenant DB (`tbc_{slug}_dev`, one per tenant) | bc-core execution-plane modules acting through governed tenant-scoped runtime acts under the bound contract version |

The boundary is one-directional for authority. The platform does not author tenant state outside governed runtime acts. The tenant does not author platform contracts. Discovery acts that observe a tenant's data structure are platform acts that read tenant state read-only without writing to it. This is the asymmetric ownership rule recorded in DEC-1918d0 and DEC-771baf.

**Governing source.** The Dual-Layer Interaction Model; The Object Model; The Contract Grammar; DEC-1918d0; DEC-771baf.

## The Execution Spine

The architecture's central commitment is that authoritative state is produced only at four governed evaluation boundaries. The spine is the same for every tenant, every source system, every metric, every action.

| Boundary | Reads | Applies | Produces | Emits proof |
|---|---|---|---|---|
| Admission | Observed source state from the connected source system | Source Contract; Admission Contract; Observation Contract; Reader Flavor | Source Object | Per-record Evidence; per-Source-Object Lineage |
| Canonical evaluation | Source Objects (one or more per Canonical Object per the canonical multi-source rule) | Canonical Contract; Canonical Mapping | Canonical Object | Per-record Evidence; per-Canonical-Object Lineage |
| Metric evaluation | Canonical Objects (and, for secondary metrics, prior Metric Snapshots) | Metric Contract | Metric Snapshot | Per-record Evidence; per-Metric-Snapshot Lineage |
| Action evaluation | Metric Snapshots | Intervention Contract | Action Object | Per-record Evidence; per-Action-Object Lineage |

Every boundary reads only the prior boundary's authoritative output (or, at admission, observed source state). Every boundary applies a versioned contract to that input. Every boundary emits Evidence and Lineage at the same act that produces the authoritative object. No boundary modifies a prior boundary's emission. No boundary acts as a side effect of a read.

The spine is the same architectural commitment regardless of how many services compose the platform, how many tenants share a deployment, or what hosting variant a tenant chose. Operating Model defines the runtime semantics of each boundary in detail. Architecture defines that the spine exists, that it is the only producer of authoritative state, and that it is governed by the contract chain.

**Governing source.** The Object Model; The Evaluation Boundaries; Operating Model.

## The Contract Chain

The contract chain is the architectural backbone. Every state-producing act in the spine is governed by a versioned contract drawn from the chain.

| Family | Role | Authoritative source |
|---|---|---|
| Source Contract | Declares the structural shape of one source table or API endpoint | The Contract Grammar |
| Admission Contract | Declares validation rules, data-quality rules, and the admission verdict for observed records | The Contract Grammar |
| Observation Contract | Declares which source fields are observed at admission and how they map to Business Fields | The Contract Grammar |
| Canonical Contract | Declares the Canonical Object shape, grain, resolution semantics, temporal gate, and Canonical Field bindings | The Contract Grammar |
| Canonical Mapping (supporting schema) | Binds Business Fields to Canonical Fields for one Canonical Contract version | The Contract Grammar |
| Metric Contract | Declares the metric formula, Canonical Field bindings, grain, classification, and thresholds | The Contract Grammar |
| Intervention Contract | Declares the intervention conditions, target value, evaluation cadence, and outcome semantics | The Contract Grammar |
| AI Contract (provisional) | Declares an AI participation surface; not in the execution spine at this writing | The Contract Grammar |

The chain composes from Source Contract through to Intervention Contract: a metric instance traces back through one Metric Contract, one Canonical Contract (with its Canonical Mapping), one Observation Contract, one Source and Admission Contract pair, to the source table the contracts describe. An action instance adds an Intervention Contract over the Metric Snapshot. The chain is the only path from observed source state to authoritative metric or action output. The Contract Grammar defines the family-level rules; Operating Model defines how each contract is applied at runtime; Onboarding workflows define how each contract is authored.

Three governed primitives (Business Object, Business Field, and Canonical Field) provide the vocabulary that contracts reference. Observation Contract maps source fields to Business Fields; Canonical Mapping binds Business Fields to Canonical Fields for one Canonical Contract version; Metric Contract binds the metric formula to Canonical Fields. The primitives are not contract families and do not appear in the chain table above; their full definitions are in The Contract Grammar.

**Governing source.** The Contract Grammar; Operating Model.

## System Composition

The platform composes from a small set of repositories and two database scopes.

![Architecture: Repository Composition](/docs/assets/diagrams/DG-architecture-composition.svg)

### Repository map

| Repository | Role |
|---|---|
| bc-core | Hosts the contract registry and the four boundary acts. Single execution authority for the spine. NestJS monorepo. |
| bc-ai | Hosts the AI runtime and AI agents. Python and FastAPI. Detailed in AI Architecture. |
| bc-portal | Tenant-facing browser shell. Vite and React. |
| bc-admin | Platform-facing browser shell. Vite and React. Hosts the canonical embedded documentation reader (per DEC-b97390). |
| DevHub | Hosts the governance backbone: sessions, plans, tasks, decisions, change records, activity log. MCP-server interface. Independent of bc-core. |
| bc-pg-mcp | Hosts a PostgreSQL MCP server that surfaces platform and tenant database state to development tooling. Read-only at the architectural level. |
| bc-core-dashboard | Hosts the operations dashboard for platform monitoring. Auxiliary to bc-core. |
| bc-sdg | Synthetic data generator and per-system-type simulators. Auxiliary; not in production execution path. |
| bc-website | Marketing site. Static. Not in the platform execution surface. |

bc-core is the single execution authority for the spine. The architecture admits no tenant-side execution: the four boundary acts run only in bc-core. The `@PlatformOnly()` annotation on platform-only routes and the `@TenantScoped()` annotation on tenant-scoped routes are routing mechanisms inside bc-core, not separate runtimes.

### Two-database architecture

![Architecture: Two-Database Topology](/docs/assets/diagrams/DG-architecture-two-db.svg)

| Property | Platform DB | Tenant DB |
|---|---|---|
| Identifier | `bc_platform_dev` (one per environment) | `tbc_{slug}_dev` (one per tenant) |
| Owner | Platform | Tenant-scoped (writes only through governed tenant-scoped acts) |
| Stores | Contract registry across the seven active families plus AI provisional; Source Catalog hierarchy; master data; tenant identity records; Subscription records; governance state; chain status | Boundary envelopes; typed payload tables per activated contract; Evidence and Lineage; Run records; Connections; Contract Bindings; tenant-scoped extension content |
| Schema inventory | Governed by Data Model and Schema | Governed by Data Model and Schema |

Writes to the tenant database fall into two governed categories. The first is the four boundary acts, which produce authoritative runtime state (Source Object, Canonical Object, Metric Snapshot, Action Object) and emit Evidence and Lineage. The second is governed tenant-scoped authoring acts, which produce registration and binding records (Connections, Contract Bindings, tenant-scoped extension content). Discovery acts read tenant state read-only without writing. The tenant database receives no other writes; both governed categories run only inside bc-core acting under a bound contract version.

### Single execution runtime

bc-core is one runtime that hosts both `@PlatformOnly()` routes (control plane) and `@TenantScoped()` routes (execution plane). The architecture supports a future split into a separate platform service and a separate tenant-side execution service, but the split is deferred. The split-readiness commitment is: `registry/` and `boundary/` modules do not import each other; shared types live in a shared package; contract reads are cached such that a future network hop between services would not change correctness. When and if the split happens, it is a deployment refactor, not an architectural change to the spine.

**Governing source.** DEC-1918d0; DEC-771baf; DEC-9b23a7; The Contract Grammar.

## Port Reservation

Architecture records local service identity through fixed port reservations. Port numbers are not the deployment topology; they are the stable local addresses used by developers, documentation, and cross-repository tooling.

| Range | Purpose | Service | Port |
|---|---|---|---|
| 3000 to 3099 | Frontends | bc-portal (tenant-facing) | 3000 |
| 3000 to 3099 | Frontends | bc-admin (platform-facing) | 3010 |
| 3100 to 3199 | APIs | bc-core | 3100 |
| 4000 to 4099 | Development tools | DevHub | 4000 |
| 4100 to 4199 | Operations tooling | bc-core-dashboard | 4100 |
| 4300 to 4399 | AI services | bc-ai | 4300 |
| 5432 to 5499 | Databases | PostgreSQL local development topology | 5435 |
| 6379 | Cache | Redis | 6379 |

A service that changes its local port without a governed port-reservation update is incorrect against the architectural discipline. Production endpoint placement is owned by Infrastructure and deployment configuration; Architecture preserves service identity, not production socket layout.

**Governing source.** DEC-e50b83.

## End-to-End Path

A single source-to-action path traverses the architecture in a fixed sequence.

| Step | Surface | Owner | What happens |
|---|---|---|---|
| Source registration | Control plane | Platform | Source system, version, module, table, and field entries are added to the Source Catalog. |
| Contract authoring | Control plane | Platform | Source, Admission, Observation, Canonical, Metric, and Intervention Contracts are authored against the Source Catalog and the Business Object vocabulary. |
| Tenant binding | Control plane | Platform | A tenant's Subscription, Connections, and Contract Bindings are recorded; the bound contract version becomes the version that subsequent runtime acts will use for that tenant. |
| Connection registration | Control plane | Tenant (under the bound contract version) | A Connection is recorded for the tenant with credentials and a Reader Flavor compatible with the bound Reader. |
| Admission | Execution plane | bc-core | The Reader observes source state under the Observation Contract, the Admission Contract validates, the Source Object is emitted into the tenant database, and Evidence and Lineage are recorded. |
| Canonical evaluation | Execution plane | bc-core | Source Objects are read, the Canonical Contract resolves business meaning through the Canonical Mapping, the Canonical Object is emitted, and Evidence and Lineage are recorded. |
| Metric evaluation | Execution plane | bc-core | Canonical Objects (and prior Metric Snapshots for secondary metrics) are read, the Metric Contract evaluates the formula, the Metric Snapshot is emitted, and Evidence and Lineage are recorded. |
| Action evaluation | Execution plane | bc-core | Metric Snapshots are read, the Intervention Contract evaluates the intervention condition, the Action Object is emitted with set-once terminal-state attributes, and Evidence and Lineage are recorded. |
| Surfacing | Delivery plane | bc-portal, bc-admin | Authoritative state is queried read-only and rendered for tenant users and platform operators. |
| AI visibility | Delivery plane | bc-ai | AI agents read the Trust surface and surface advisory output on the Conversation surface. Any authoring triggered from that output leaves the delivery plane and enters a governed authoring act. |
| Action write-back request | Adjacent integration path | External | Action Objects with terminal state may be consumed by external integration paths. The write-back path is not a delivery-plane mutation and must be governed by the integration surface that owns the external act. |

The control-plane steps in this path create governed platform records. The execution-plane steps produce authoritative runtime objects and emit Evidence and Lineage. Delivery-plane steps consume authoritative state read-only. Adjacent integration paths consume delivered state and require their own governed act before any external system is changed.

**Governing source.** Operating Model; The Object Model; The Evaluation Boundaries.

## Cross-Cutting Concerns

A small set of concerns thread through every layer and surface. The architecture defines where each concern is owned and how it is enforced.

| Concern | Control plane | Execution plane | Delivery plane |
|---|---|---|---|
| Identity and access control | Cognito user pool; platform-admin scope; ADR access for governance authoring | Cognito JWT validated at every backend service boundary; `custom:tenant_id` claim binds tenant-scoped requests to one tenant database | Platform routes guarded by `@PlatformOnly()`; tenant routes guarded by `@TenantScoped()` and the same JWT validation |
| Secrets and credentials | AWS Secrets Manager; ADR-recorded secret policies | Per-tenant Connection credentials retrieved at admission time only | Browser session tokens for read-only surfacing; API tokens for tenant-scoped read paths |
| Telemetry | Governance latency, ADR throughput, change record completeness | Boundary execution latency, per-Run success rate, Evidence emission rate, chain readiness drift | Frontend latency, read-API throughput, AI visibility surface latency |
| Lineage | Contract version graph; supersession chains | Per-Source-Object, per-Canonical-Object, per-Metric-Snapshot, per-Action-Object Lineage emission at the boundary act | Lineage browser surfaces in bc-admin; tenant-facing lineage views in bc-portal |
| Quality gates | Authoring gates with red, amber, and green verdicts; AI gate participation | Chain integrity checks read-only; activation gates that block bound-contract activation if chain is incomplete | None; delivery surfaces consume only authoritative state |
| Alerts | Governance breaches, ADR conflicts, supersession-pair gaps | Boundary failures, chain readiness regressions, semantic verdict drops | Read-API failure rates, AI visibility surface error rates |
| Cost and quota | Subscription tiers per DEC-324d9e; tier-permitted ranges for envelope dimensions | Per-tenant rate limits, concurrent admission caps, evaluation rate limits | Read-API rate limits per tenant; UI rate limits per user |
| Backup, continuity, disaster recovery | Platform DB backup; ADR archive immutability | Tenant DB backup per RPO and RTO declared by hosting variant | Frontend asset CDN cache; read-cache invalidation policy |
| Compliance and evidence | ADR audit trail; change records under ISO 27001 A.14.2.1 | Evidence and Lineage proof chain as compliance evidence; tenant ownership boundary as data residency evidence | Compliance dashboard; tenant-facing evidence views |

The cross-cutting concerns matrix is the architecture's check on whether a concern has a defined home for the three Trust-surface planes. A concern that does not appear in the matrix is either out of architectural scope (in which case it should be added or moved to a chapter that owns it) or under-defined (in which case it should be raised against the relevant chapter).

Adjacent integration paths (AI-triggered authoring, action write-back to source systems) are not Delivery-plane writes and do not appear in the Delivery column. Their cross-cutting concerns belong to the integration surface that initiates the act: secrets governance for the external endpoint travels with the integration surface; telemetry for the external act is owned by the consuming chapter; the act's compliance and audit trail merge into the governed authoring act it triggers and the receiving system's audit surface. Architecture records that adjacent paths exist; the chapters that own each path govern its concerns.

**Governing source.** The Authority Model; DEC-1918d0; DEC-771baf; DEC-3395bc.

## Residency Boundary

Architecture records the residency boundary that every hosting variant must preserve. It does not define subscription tiers, operator responsibilities, network placement, tenant provisioning prerequisites, or lifecycle gates.

| Boundary | Architectural rule |
|---|---|
| Execution spine | The four boundary acts produce the same authoritative state regardless of where bc-core runs. |
| Database split | Platform definitions and tenant data remain separate physical scopes. A hosting variant may move where a scope lives; it may not collapse the two scopes into one authority domain. |
| Auth boundary | Cognito/JWT tenant scope remains the request boundary unless a later governed security architecture records an equivalent boundary. |
| Proof emission | Evidence and Lineage are emitted at the same proof-emitting acts regardless of hosting variant. |
| Contract reference | Runtime acts use explicit bound contract versions regardless of hosting variant. |

Subscription tier categorization, hosting-variant commercial rules, tenant lifecycle state, onboarding prerequisites, and operations-side provisioning are governed outside Architecture. Architecture records only that those later decisions do not relax the execution spine, two-database split, auth boundary, proof-emission rule, or explicit-reference discipline.

**Governing source.** DEC-324d9e; DEC-1918d0; The Object Model; The Evaluation Boundaries.

## RACI

The architecture assigns responsibilities at the surface level. The table below records who is accountable, responsible, consulted, or informed for the major architectural acts.

| Act | Platform team | Tenant operator | bc-admin | bc-portal |
|---|---|---|---|---|
| Author Source Catalog entries | A, R | I | (governs) | I |
| Author contracts (Source, Admission, Observation, Canonical, Metric, Intervention) | A, R | I (consulted on tenant requirements) | (governs) | I |
| Approve contract publication | A, R | I | (governs) | I |
| Configure tenant Connection | I (provisions credentials path) | A, R (within bound contract) | I | (configures) |
| Configure Goals (intervention parameters) | I | A, R | I | (configures) |
| Run boundary acts (admission, canonical, metric, action) | A, R (single execution authority in bc-core) | I (consumes results) | (monitors) | I |
| Emit Evidence and Lineage | A, R (automatic at the boundary act) | I | (browses) | (browses) |
| Decide on actions | I (the platform does not decide) | A, R (acts on platform-evaluated outputs) | I | (consumes) |
| Author ADRs and change records | A, R | I (consulted on tenant-impacting changes) | (browses) | I |
| Operate hosting infrastructure | A, R for platform-managed infrastructure boundaries | A, R for tenant-managed infrastructure portions when a hosting variant assigns them | I | I |

A is Accountable; R is Responsible; C is Consulted; I is Informed. The architecture's central RACI claim is "the platform does not decide": the platform evaluates and surfaces; the tenant operator decides and acts.

**Governing source.** The Authority Model; The Dual-Layer Interaction Model; DEC-324d9e.

## Evolution Context

The architecture reached its current shape through three documented eras. Earlier eras are preserved as historical record, not as architectural authority.

| Era | Architectural shape | Vocabulary | Status |
|---|---|---|---|
| Platform-Documentation v1 | Layered medallion architecture (Bronze, Silver, Gold, Golden Data Points, KPI); Control Plane, Data Plane, Data Action Layer; ETL-shaped extraction and transformation prose | Vocabulary the v3 register forbids: pipeline, ingestion, transformation, extract | Superseded |
| bc-docs v2 | Five-stream model (Foundation, Platform, Tenant, Common, AI); per-family contract tables; multi-schema DDL; four evaluation boundaries; v3 vocabulary introduced | Mixed: some legacy compounds (workflow, pipeline) remained; four-boundary vocabulary canonical | Superseded |
| bc-docs v3 (current) | Eight-section structure (Foundation, Operating Model, Implementation, AI, Development, Onboarding, Operations, Compliance) plus Platform Overview at home; same four boundaries; section overviews; explicit hosting-variant model | v3 vocabulary throughout; forbidden tokens lint-enforced | Current |

Key architectural transitions across the eras:

| What changed | From (legacy) | To (current) | Governing record |
|---|---|---|---|
| Object progression vocabulary | Bronze, Silver, Gold, GDP, KPI | Source Object, Canonical Object, Metric Snapshot, Action Object | Foundation (locked) |
| Production model | Pipeline-shaped extraction and transformation | Contract-governed boundary acts | The Contract Grammar; The Evaluation Boundaries |
| Database topology | Single database with mixed registry and boundary schemas | Two databases: platform definitions and tenant data, with a one-way ownership boundary | DEC-1918d0; DEC-771baf |
| Contract grammar | Single registry table for all contract types | Per-family contract tables plus Canonical Mapping plus AI Contract provisional | The Contract Grammar |
| Service supervision | pm2 ecosystem orchestration | Independent service startup; each service owns its own watch | DEC-9b23a7 |
| Documentation structure | Five-stream model | Eight-section spine plus Platform Overview at home | DEC-c06f41 |

The transitions are recorded as historical context. The current architecture is what governs.

**Governing source.** Foundation; The Contract Grammar; The Evaluation Boundaries.

## Governing Decisions

The decisions that govern the architecture are listed below. The list is the architectural-level subset; per-component ADRs are listed in the chapter for that component.

| Decision | Title | Architectural impact |
|---|---|---|
| DEC-1918d0 | Deployment and database architecture; ten normalization rules | Two-database split; ten DB rules; staging topology |
| DEC-771baf | Tenant database topology; platform-tenant one-way dependency | Asymmetric ownership; tenant DB schemas; platform never reads tenant DB to author platform state |
| DEC-e50b83 | Master port reservation | Stable local service identity and cross-repository tooling addresses |
| DEC-9b23a7 | pm2 removed; independent service startup | Each service starts independently; no central orchestrator |
| DEC-3395bc | v3 documentation structure; bc-core JWT-guarded `/api/docs/*` | Documentation served under JWT; bc-admin embedded reader is canonical |
| DEC-b97390 | bc-admin embedded documentation reader | Documentation reader is part of the platform delivery plane |
| DEC-441665 | NPM supply chain mitigation via AWS CodeArtifact | All package installs route through CodeArtifact; supply-chain governance |
| DEC-324d9e | Subscription tiers and hosting variants | Hosting variants exist and do not relax Architecture's residency boundary |
| DEC-c06f41 | Spine expansion to eight sections plus home | Architectural-documentation shape; Implementation reshape |

**Governing source.** The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Invariants
- The Object Model
- The Contract Grammar
- The Evaluation Boundaries
- The Authority Model
- The Dual-Layer Interaction Model
- Operating Model: Overview
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-e50b83: Master port reservation
- DEC-9b23a7: pm2 removed; independent service startup
- DEC-3395bc: v3 documentation structure
- DEC-b97390: bc-admin embedded documentation reader
- DEC-441665: NPM supply chain mitigation via AWS CodeArtifact
- DEC-324d9e: Subscription tiers and hosting variants
- DEC-c06f41: Spine expansion to eight sections plus home
- outline.md §4.3: Implementation
- Decisions: ADR Registry
