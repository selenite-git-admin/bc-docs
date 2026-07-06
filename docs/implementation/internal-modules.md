---
id: internal-modules
order: 18
title: "Internal Modules"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, the-dual-layer-interaction-model, operating-model-overview, architecture, backend-services]
governing_sources:
  - Foundation
  - The Object Model
  - The Contract Grammar
  - The Evaluation Boundaries
  - The Authority Model
  - The Dual-Layer Interaction Model
  - Operating Model
  - Architecture
  - Backend Services
governing_adrs:
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules)
  - DEC-771baf (Tenant database topology; platform-tenant one-way dependency)
  - DEC-c06f41 (Spine expansion to eight sections plus home)
  - DEC-bebaec (Chain completeness SSOT in contract.chain_status)
  - DEC-804874 (L-node semantic verification gate at session close)
  - DEC-3395bc (v3 documentation structure; bc-core JWT-guarded /api/docs/*)
errata_referenced: []
v2_sources:
  - legacy-v2/docs/architecture/index.md
diagrams: []
---

# Internal Modules

## Scope

This chapter describes the NestJS module catalog inside bc-core: the modules that compose the bc-core runtime, what each module groups, the controllers and services and repositories registered inside it, the test surface, and how modules cooperate at the request lifecycle. The chapter sits one level below Backend Services. Backend Services records the bc-core deployable boundary (port, database, authentication, dependencies); Internal Modules records the interior of that deployable.

This chapter does not redefine Foundation invariants, the Object Model, the Contract Grammar, the Evaluation Boundaries, the Authority Model, or the Dual-Layer Interaction Model. It does not redefine the four boundary semantics (admission, canonical evaluation, metric evaluation, action evaluation): the runtime acts that the boundary modules host are owned by Operating Model. It does not enumerate API endpoint shapes (deferred to API Surface), database table or column structure (deferred to Data Model and Schema), the Evidence and Lineage proof rules (deferred to Operating Model Evidence and Lineage), the chain readiness L1 to L7 verdict semantics (deferred to Operating Model Chain Completeness and Verdict), the operational audit log retention and query surface (deferred to Audit and Activity Logging), the privacy erasure protocol (deferred to Privacy and the Immutable Fact in Compliance), the contract-creation onboarding workflows that the onboarding controllers serve (deferred to the Onboarding section), the synthetic-data and pressure-test methodology (deferred to Synthetic Data and Testing), the L-node verification gate's session-close protocol (deferred to Decision and Change Workflow in the Development section), the bc-ai service depth (deferred to AI Architecture in the AI section), or the per-tenant view contracts (deferred to API Surface and Frontend Experience).

The chapter records modules by name, by source directory, and by the small set of facts that locate the module in the platform: the spec it implements (cross-referenced by chapter), the controllers and services and repositories it registers, the modules it imports, the providers it exports, and the test surface that exercises it.

**Governing source.** Architecture; Backend Services; outline.md §4.3.

## Module Catalog Overview

bc-core composes from one root module and twenty-seven feature and infrastructure modules. The root module imports the feature modules; each feature module is a self-contained NestJS unit with its own controllers, providers, and exports. The catalog is grouped into ten clusters by responsibility.

| Cluster | Modules |
|---|---|
| Auth and request lifecycle | AuthModule, TenancyModule |
| Global infrastructure | DatabaseModule, AuditModule, HealthModule |
| Contract registry | ContractModule, MetricModule, BusinessObjectModule, SourceCatalogModule, ConnectorModule, ReaderModule, PlatformModule |
| Evaluation boundary | BoundaryModule, EvidenceModule, ProgressionModule |
| Execution and reconciliation | ExecutionModule, SemanticModule, SchemaProvisionerModule |
| Tenant management and views | TenantManagementModule, TenantViewsModule |
| Privacy and erasure | NullificationModule |
| Catalog aggregation | BusinessCatalogModule, MetricCatalogModule |
| Documentation read-surface | DocsModule |
| Support and ops | SupportModule, FunctionAdminModule, TestBenchModule |

Every module sits under `src/` in the bc-core repository. Module files end in `*.module.ts` and follow NestJS conventions: an `@Module()`-decorated class declaring `imports`, `controllers`, `providers`, and `exports`. The root module is `src/app.module.ts`; it composes the feature modules, mounts the global ClsModule for request-scoped context, and registers global interceptors and filters.

Per-module enumeration of controllers, services, and repositories will live in a future Module Inventory reference, auto-generated from the bc-core source. This chapter records the design rationale for each module: why the module exists, what design choice it embodies, what cross-cutting concern it owns. The per-class inventory is not enumerated here; a reader who needs the exhaustive list reads the module's source file at the cited path.

**Governing source.** Architecture; Backend Services.

## Auth and Request Lifecycle

Two modules establish the per-request execution context that every other module reads from: AuthModule resolves the caller identity and scope; TenancyModule resolves the tenant identity and binds it to the request scope.

### AuthModule

AuthModule lives at `src/auth/auth.module.ts`. It hosts the Cognito JWT validation strategy (validates incoming JWTs against the Cognito issuer's published JWKS), the three global APP_GUARD providers (JwtAuthGuard, ScopeGuard, RolesGuard registered in that fixed order: JWT validation first, then scope enforcement, then role enforcement), and the `@PlatformOnly()` / `@TenantScoped()` route decorators that ScopeGuard consults. The CognitoJwtStrategy extracts the `custom:tenant_id` claim, the `custom:roles` claim, and a request-scope marker derived from the JWT audience (admin client identifier resolves to the platform scope; portal client identifier resolves to the tenant scope). ScopeGuard rejects a request whose JWT scope does not match the route's required scope.

**Governing source.** Architecture; Backend Services.

### TenancyModule

TenancyModule lives at `src/tenancy/tenancy.module.ts`. It hosts tenant identity lookup, per-tenant feature flag configuration, and the TenantMiddleware that runs on every request before the route handler.

TenantMiddleware extracts the tenant identity from the request's `x-tenant-id` header or, when the request arrives with a tenant-bound subdomain, from the subdomain. Routes prefixed with `/api/t/` are tenant-scoped and require the tenant identity; routes prefixed with `/api/` (without `/t/`) are platform-scoped and skip tenant resolution; declared public paths skip both. The middleware writes the resolved tenant context into the ClsService under the `tenant` key and the request scope under the `scope` key (`'tenant'` or `'platform'`). The ClsModule is mounted globally in `app.module.ts` so that any provider injected lower in the request can read the tenant context without explicit propagation.

The tenant identity that reaches request-scoped repositories comes from this middleware-resolved CLS value, not directly from the JWT `custom:tenant_id` claim. The JWT claim is the platform-side tenant identifier carried by the authenticated user; the request-scope tenant identifier is the operational tenant the request targets. In the readiness baseline, ScopeGuard enforces platform-vs-tenant route scope, while TenantMiddleware resolves the operational tenant from the request. A direct comparison between `custom:tenant_id` and the resolved tenant is a security-hardening gap, not a guarantee this module enforces.

**Governing source.** Architecture; Backend Services.

## Global Infrastructure

Three modules provide the shared runtime substrate that feature modules depend on. DatabaseModule and AuditModule are global provider modules; HealthModule is a normal module imported by AppModule for readiness and liveness probes.

### DatabaseModule

DatabaseModule lives at `src/database/database.module.ts` and is marked `@Global()`. It exposes the Platform DB connection pool and the per-tenant Tenant DB connection (request-scoped via CLS) through five injection tokens: `CONTROL_PLANE_DB` for Platform DB; `TENANT_DATA_DB` for the addressed Tenant DB; and three legacy aliases (`DRIZZLE`, `REGISTRY_DB`, `PLATFORM_DB`) that resolve to the same Platform DB pool for backward compatibility.

The tenant-DB connection pool is request-scoped: NestJS instantiates a fresh provider per request, the provider reads the tenant identifier from CLS, and the provider returns the Drizzle connection bound to that tenant's database. Repositories that inject `TENANT_DATA_DB` therefore see the addressed Tenant DB without any explicit tenant-passing, and a request that did not pass through TenantMiddleware (for example, a `@PlatformOnly()` route) cannot inject `TENANT_DATA_DB` because no tenant context exists in CLS.

Connection-pool sizing, pool keys, idle and connect timeouts, and connection-string env vars are configured in `database.config.ts`. Per DEC-1918d0, the architectural commitment is one Platform DB connection pool per runtime instance, one Tenant DB connection pool per tenant, and no shared privileged tenant connection that multiplexes tenant identities.

**Governing source.** Architecture; Backend Services; DEC-1918d0; DEC-771baf.

### AuditModule

AuditModule lives at `src/audit/audit.module.ts` and is marked `@Global()`. It hosts the append-only operational audit writer and a UID generation service. The audit log this module writes is operational audit, distinct from the Evidence and Lineage proof chain that the boundary acts emit. The retention policy, the query surface, and the schema of operational audit records are owned by Audit and Activity Logging.

**Governing source.** Architecture.

### HealthModule

HealthModule lives at `src/health/health.module.ts`. It serves the `/api/health` readiness and liveness endpoints. The probe surface is the only thing this module owns; deployment-side use of the probes is owned by Deployment Topology in the Operations section.

**Governing source.** Backend Services.

## Contract Registry Cluster

Seven modules compose the contract-registry surface inside bc-core. They host the platform-side authoring and lookup paths for contract families, the catalogues those contracts reference, and the chain-readiness state that connects them.

### ContractModule

ContractModule lives at `src/registry/contract.module.ts`. It is the platform-side contract registry: the CRUD surface for the seven contract families, the platform-side authoring validator, the formula audit and metric readiness derivations, and the host for ChainStatusService (the SSOT reader and re-evaluation API for `contract.chain_status` per DEC-bebaec). The chain-readiness verdict semantics, the L1 to L7 layer definitions, and the per-variable funnel are owned by Operating Model Chain Completeness and Verdict; ContractModule hosts the API.

**Governing source.** Architecture; DEC-bebaec.

### MetricModule

MetricModule lives at `src/registry/metric.module.ts` and imports ContractModule. It is the platform-authoring surface for Metric Contracts: metric definition, metric binding, metric reference KPIs (industry and enterprise), and the metric authoring wizard. The runtime application of Metric Contracts at metric evaluation is owned by Operating Model Metric Evaluation and runs in BoundaryModule.

**Governing source.** Architecture.

### BusinessObjectModule

BusinessObjectModule lives at `src/registry/business-object.module.ts` and imports ContractModule and SourceCatalogModule. It is the platform-authoring surface for the three governed primitives the contract grammar names (Business Object, Business Field, Canonical Field), plus the Mapping Binding surface, the Canonical Wizard, and two AI-driven verification surfaces (BoVerificationService and CatalogVerificationService) that call the Anthropic SDK directly. The semantics of the primitives are owned by The Contract Grammar.

**Governing source.** Architecture.

### SourceCatalogModule

SourceCatalogModule lives at `src/registry/source-catalog.module.ts`. It is the platform-authoring surface for the six-tier Source Catalog (provider, system, version, module, object, field), plus reference-data import surfaces (SAP, OAGIS, generic seed). The Source Catalog hierarchy is owned by Operating Model Sources and the Catalog.

**Governing source.** Architecture.

### ConnectorModule

ConnectorModule lives at `src/registry/connector.module.ts`. It hosts platform-authored Connector definitions (how a Reader Flavor speaks to a source-system class) and tenant-scoped Connection records (per-tenant credentials bound to a Connector). The credential resolver is in this module.

**Governing source.** Architecture.

### ReaderModule

ReaderModule lives at `src/registry/reader.module.ts` and imports EvidenceModule, ContractModule, ConnectorModule, and BusinessObjectModule. It is the platform-authoring and platform-stats surface for Readers and Reader Flavors, plus Tenant Binding records and aggregated boundary stats. The UniBAT Reader concept and Reader Flavor semantics are owned by Operating Model Connectors and Readers; the runtime execution of Readers runs in BoundaryModule.

**Governing source.** Architecture.

### PlatformModule

PlatformModule lives at `src/platform/platform.module.ts`. It hosts the platform-wide library registry (software bill of materials) and the master reference data (countries, currencies, functions, subfunctions, industries, statuses, system types). Each master has its own repository.

**Governing source.** Architecture.

## Evaluation Boundary Cluster

Three modules host the runtime production of authoritative state at the four governed evaluation boundaries.

### BoundaryModule

BoundaryModule lives at `src/boundary/boundary.module.ts` and is the largest module in the catalog. It hosts all four evaluation boundaries (admission, canonical evaluation, metric evaluation, action evaluation) in one NestJS module. The grouping is a code-organization choice; the four boundaries remain semantically distinct as defined by Operating Model The Evaluation Boundaries.

The module hosts three evaluation engines (CanonicalEvaluationEngine, MetricEvaluationEngine, ActionEvaluationEngine) that the corresponding boundary services delegate to for the deterministic per-record computation. There is no separate observation engine; the admission-boundary computation surface is the ObservationService directly.

The module also registers an executor catalogue: ExecutorRegistryService plus per-source-class executors for the Reader Flavors that admission can invoke. Executors register into ExecutorRegistryService at module-init time, indexed by the Reader Flavor's protocol class name and the legacy flavor name; new executors are added as new Reader Flavors land.

Per-record Evidence and per-object Lineage emission at every boundary act is delegated to EvidenceModule. The semantic rules of each boundary act are owned by the corresponding Operating Model chapter (Admission and Observation, Canonical Evaluation, Metric Evaluation, Action Evaluation).

**Governing source.** Architecture; The Evaluation Boundaries.

### EvidenceModule

EvidenceModule lives at `src/evidence/evidence.module.ts`. It hosts the append-only writer surface for Evidence and Lineage plus the read surfaces. Every boundary act in BoundaryModule calls the writer at the same act that produces the authoritative object. The Foundation proof rule requires authoritative state and proof to be emitted together; the current implementation logs Evidence or Lineage write failures in several boundary services instead of rolling back the authoritative write, so strict rollback enforcement is recorded as an implementation gap.

The proof rules (per-record Evidence, per-object Lineage, the granularity of each, the immutable append-only commitment) are owned by The Object Model and Operating Model Evidence and Lineage. EvidenceModule hosts the writer and the read surface; it does not redefine the rules.

**Governing source.** Architecture; The Object Model.

### ProgressionModule

ProgressionModule lives at `src/progression/progression.module.ts`. It hosts the D369 M4.2 progression-family repositories (one per boundary act) and the S3ArchiverService that writes raw payload archives to S3 alongside the typed-fact tables. The progression repositories dual-write alongside the boundary envelope repositories during the in-flight envelope-to-progression migration; M4.4 will drop the envelope path. Schema definitions for both layers are owned by Data Model and Schema.

**Governing source.** Architecture; The Object Model.

## Execution and Reconciliation Cluster

Three modules sit between the contract registry and the boundary execution. They host the platform-side onboarding controllers, the deterministic compatibility filter that drives onboarding, and the tenant-side schema reconciler.

### ExecutionModule

ExecutionModule lives at `src/registry/execution.module.ts` and imports the contract registry cluster modules plus SemanticModule. It hosts the platform-side onboarding controllers (one per contract family: Observation, Canonical, Metric, Canonical Mapping), the cross-contract relationship reads, grouped contract package operations, the L-node semantic verdict reader, and runtime execution coordination. The ContractController itself is registered here rather than in ContractModule due to a circular-dependency constraint with BusinessObjectService; the placement is a code-organization detail and does not affect the contract surface's external semantics.

The platform-side onboarding controllers expose the surfaces that the bc-admin onboarding UI and AI authoring agents call to create and govern contracts; the onboarding workflows themselves (the ordered sequence of steps, the AI gate participation, the verification checks) are owned by the chapters in the Onboarding section.

**Governing source.** Architecture.

### SemanticModule

SemanticModule lives at `src/registry/semantic/semantic.module.ts`. It hosts the deterministic compatibility filter introduced by DEC-804874, the HTTP client that calls bc-ai for orchestrated agent operations, and the L-node semantic verdict producer that DevHub's session-close gate consults. The module isolates the AI integration boundary so that other modules consume L-node verdicts and AI agent outputs through a single named surface.

**Governing source.** Architecture; DEC-804874.

### SchemaProvisionerModule

SchemaProvisionerModule lives at `src/schema-provisioner/schema-provisioner.module.ts`. It is the tenant-side reconciler that keeps each tenant's `fact.*` typed tables aligned with the bound Canonical Contract version. The module orchestrates connector onboarding, generates typed-fact table DDL from the bound contract, walks the contract chain to determine which tables a tenant needs, activates contract versions after gate verdicts pass, runs nightly drift reconciliation, and serves the typed-fact read and write paths. The schema rules and DDL conventions are owned by Data Model and Schema.

**Governing source.** Architecture; DEC-1918d0.

## Tenant Management and Views Cluster

### TenantManagementModule

TenantManagementModule lives at `src/tenant-management/tenant-management.module.ts`. It hosts tenant identity CRUD on the platform side. The active tenant-database provisioning path (creating separate `tbc_{slug}_dev` databases and applying `docker/redesign/03-tenant-db.sql`) lives in `src/registry/seed/seed-tenant-dbs.ts` rather than in this module; the tenant-DB DDL itself owns the per-tenant `users` and admin tables. A legacy `TenantProvisioningService` from the D084/D087 era remains in this module's source tree but is not the active provisioning path under D368. The Subscription record and the tenant lifecycle state machine are owned by Tenant Lifecycle and Subscription in the Operations section.

**Governing source.** Architecture.

### TenantViewsModule

TenantViewsModule lives at `src/tenant-views/tenant-views.module.ts` and imports ExecutionModule. It hosts read-only, tenant-filtered views under the `/api/t/` route prefix (every controller carries `@TenantScoped()`). The module is the consumption surface that bc-portal calls; the underlying authoring lives in the contract-registry cluster modules.

**Governing source.** Architecture.

## Privacy and Erasure

### NullificationModule

NullificationModule lives at `src/nullification/nullification.module.ts` and imports EvidenceModule. It is the implementation surface for privacy-erasure operations: the erasure coordinator and runner, the erasure-evidence emitter (so that erasure itself is recorded), the data-subject access request handler, the S3 write-once-read-many tombstone marker, and the retention-policy applicator.

The privacy-erasure protocol semantics, the legal basis for each erasure verdict, the relationship between the immutable Evidence chain and the sentinel-based nullification model, and the GDPR / DPDP / CCPA mapping are owned by Privacy and the Immutable Fact in the Compliance section.

**Governing source.** Architecture.

## Catalog Aggregation Cluster

### BusinessCatalogModule

BusinessCatalogModule lives at `src/registry/business-catalog.module.ts` and imports ContractModule and MetricModule. It is a read-only aggregator: it joins authoring data into a flat business-catalog read surface that bc-admin renders. It holds no authoritative state of its own.

**Governing source.** Architecture.

### MetricCatalogModule

MetricCatalogModule lives at `src/registry/metric-catalog.module.ts` and imports ContractModule and ExecutionModule. It is a read-only aggregator parallel in shape to BusinessCatalogModule, joining metric authoring with execution-state data into a single metric-catalog read surface.

**Governing source.** Architecture.

## Documentation Read-Surface

### DocsModule

DocsModule lives at `src/docs/docs.module.ts`. It hosts the three documentation routes (`/api/docs/manifest`, `/api/docs/file/*splat`, `/api/docs/asset/*splat`) under the `@PlatformOnly()` class decorator and the in-memory rate-limit interceptor recorded in Backend Services. Files are read from the `private-docs/` directory that the bc-admin sync script populates. The module is intentionally narrow.

**Governing source.** Backend Services; DEC-3395bc.

## Support and Ops Cluster

Three modules cover internal operations surfaces that the platform team uses but that are not part of the tenant-data execution path.

### SupportModule

SupportModule lives at `src/support/support.module.ts`. It hosts the internal support-ticket surface.

### FunctionAdminModule

FunctionAdminModule lives at `src/function-admin/function-admin.module.ts` and imports DatabaseModule and AuthModule. It hosts the function-admin governance surface.

### TestBenchModule

TestBenchModule lives at `src/test-bench/test-bench.module.ts` and imports BoundaryModule and ContractModule. It hosts end-to-end chain pressure-test infrastructure. The pressure-test methodology, the scenario library, and the qa-bench tenant convention are owned by Synthetic Data and Testing.

**Governing source.** Architecture.

## Cross-Module Patterns

A small set of patterns recur across the catalogue.

| Pattern | What it looks like | Where it is registered |
|---|---|---|
| Controller / service / repository triad | Most feature modules group a Controller (route handler), a Service (business logic), and a Repository (database access). The controller injects the service; the service injects the repository; the repository injects a database token | Every contract-registry, evaluation-boundary, and tenant-management module |
| Request-scoped tenant context | TenantMiddleware writes the tenant identifier into ClsService; TenantDataProvider reads it per request to resolve `TENANT_DATA_DB`; tenant-scoped repositories inject `TENANT_DATA_DB` and see the addressed Tenant DB without explicit tenant-passing | TenancyModule (writer); DatabaseModule (reader); every tenant-scoped repository (consumer) |
| Global guards in fixed order | JwtAuthGuard validates the token; ScopeGuard enforces `@PlatformOnly()` and `@TenantScoped()`; RolesGuard enforces role restrictions; the order is JWT first, then scope, then role, registered by AuthModule as APP_GUARD providers | AuthModule |
| Global response envelope and ETag | ResponseEnvelopeInterceptor wraps every successful response into a consistent envelope; EtagInterceptor stamps cacheable reads with an ETag header. ProblemDetailFilter formats errors as RFC 7807 Problem Detail responses | Registered as APP_INTERCEPTOR and APP_FILTER in AppModule |
| Module-init executor registration | BoundaryModule registers per-source-class executors into ExecutorRegistryService at `onModuleInit` time, indexed by the Reader Flavor's protocol class name and the legacy flavor name | BoundaryModule |
| Aggregation modules | Read-only modules (BusinessCatalogModule, MetricCatalogModule, TenantViewsModule) import authoring modules and expose composed read surfaces for UI consumers; they hold no authoritative state of their own | BusinessCatalogModule, MetricCatalogModule, TenantViewsModule |

The patterns are NestJS conventions plus three platform-specific patterns (request-scoped tenant context, global guard ordering, module-init executor registration).

**Governing source.** Architecture.

## Test Surface

Tests are colocated with the source files they exercise. Unit tests use the `*.spec.ts` convention next to the unit they test; selected integration tests as `*.integration.spec.ts` exercise repositories and services against a real Drizzle connection to a local Postgres test database; selected end-to-end tests under `test/` exercise the HTTP API. The test infrastructure (fixtures, seed loaders, the synthetic-data bench) and the per-chapter test methodology are owned by Synthetic Data and Testing.

The test surface inside Internal Modules is the location where each module's tests live (colocated with the source). The tests are run with `npm test` (`vitest run`), and the type and lint passes are run with `npm run typecheck` and `npm run lint`.

**Governing source.** `bc-core/package.json` (the `test`, `typecheck`, `lint` scripts).

## Module-Level Failure Modes

The failure modes Backend Services records for bc-core (database connection failure, JWT validation failure, AI surface unavailable, S3 unavailable, package registry token expired, schema drift) are deployable-boundary failures that surface as request errors regardless of which module handled the request. The module-level failure modes below are additional and module-specific.

| Cause | Module that owns the failure | System response |
|---|---|---|
| TenantMiddleware cannot resolve a tenant identifier on a `/api/t/` route | TenancyModule | The request rejects with a `400 Bad Request` Problem Detail before the route handler runs; no Tenant DB connection is attempted |
| ScopeGuard rejects a request whose JWT scope does not match the route's required scope | AuthModule | The request rejects with `403 Forbidden`; no controller method is invoked |
| RolesGuard rejects a request whose JWT roles do not include the required role | AuthModule | The request rejects with `403 Forbidden` |
| TenantDataProvider injected into a request that did not pass through TenantMiddleware | DatabaseModule | The request rejects with a provider-resolution error; this is a developer-time guarantee that `TENANT_DATA_DB` cannot leak across the platform-tenant boundary |
| ExecutorRegistryService cannot find a registered executor for the requested Reader Flavor | BoundaryModule | Admission rejects the runtime invocation with a registry-miss error; the Source Object is not produced; the Run record records the miss |
| EvidenceService or Lineage write fails after a boundary act produced an authoritative object | EvidenceModule | Current boundary services log the failure rather than consistently rolling back the authoritative write. This is an implementation gap against the proof-emitted-at-boundary commitment and remains visible until the boundary transaction path is tightened. |
| Onboarding controller in ExecutionModule receives an authoring request that violates a chain-readiness gate | ExecutionModule | The request rejects with a gate-failure Problem Detail naming the failed gate; the gate semantics themselves are owned by the chapter that defines the gate |
| ChainStatusService re-evaluation fails because `contract.chain_status` is unreadable | ContractModule | The re-evaluation call returns the prior persisted state with a stale-flag warning; the SSOT remains the persisted table per DEC-bebaec |
| NullificationExecutorService cannot complete an erasure because the receiving external system rejects the tombstone | NullificationModule | The erasure act records partial completion; the protocol response is owned by Privacy and the Immutable Fact |

Module-level failures all surface as Problem Detail responses through the global ProblemDetailFilter; they are recorded in the operational audit log through AuditService when AuditModule's interceptor is invoked on the failed request.

**Governing source.** Architecture.

## Governing Decisions

| Decision | Title | Module impact |
|---|---|---|
| DEC-1918d0 | Deployment and database architecture; ten normalization rules | Two-database split realized in DatabaseModule's two connection paths and in the asymmetric write rule the contract-registry and evaluation-boundary modules honor |
| DEC-771baf | Tenant database topology; platform-tenant one-way dependency | TenancyModule and DatabaseModule cooperate to keep the boundary one-directional: TenantMiddleware resolves the operational tenant identifier into CLS, DatabaseModule's TenantDataProvider consumes that identifier per request to select the addressed Tenant DB connection, and tenant-scoped repositories read and write through that connection. ScopeGuard enforces platform-vs-tenant route scope only |
| DEC-c06f41 | Spine expansion to eight sections plus home | The Internal Modules chapter exists in the reshaped Implementation section per DEC-c06f41 |
| DEC-bebaec | Chain completeness SSOT in `contract.chain_status` | ContractModule hosts ChainStatusService as the SSOT reader and refresher |
| DEC-804874 | L-node semantic verification gate at session close | SemanticModule hosts LNodeSemanticService that DevHub's session-close gate calls |
| DEC-3395bc | v3 documentation structure; bc-core JWT-guarded `/api/docs/*` | DocsModule hosts the documentation read-surface |

**Governing source.** The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model
- The Contract Grammar
- The Evaluation Boundaries
- The Authority Model
- The Dual-Layer Interaction Model
- Operating Model: Overview
- Architecture
- Backend Services
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-bebaec: Chain completeness SSOT
- DEC-804874: L-node semantic verification gate
- DEC-3395bc: v3 documentation structure
- outline.md §4.3: Implementation
- Decisions: ADR Registry
