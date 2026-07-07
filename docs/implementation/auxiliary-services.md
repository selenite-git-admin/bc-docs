---
id: auxiliary-services
order: 19
title: "Auxiliary Services"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-object-model, the-authority-model, operating-model-overview, architecture, backend-services]
governing_sources:
  - Foundation
  - The Object Model
  - The Authority Model
  - Operating Model
  - Architecture
  - Backend Services
governing_adrs:
  - DEC-e50b83 (Master port reservation)
  - DEC-9b23a7 (pm2 removed; independent service startup)
  - DEC-c06f41 (Spine expansion to eight sections plus home)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Auxiliary Services

## Scope

This chapter records the smaller deployables that support BareCount development and platform observability without participating in the tenant-data execution path: bc-core-dashboard (an operational dashboard for bc-core), bc-sdg (the synthetic data generator with per-system-type simulators), and bc-website (the marketing site). Per outline §4.3 thesis, treatment is lighter than Backend Services: each service's section records purpose, runtime, port, role, deployment shape, and a short list of constraints and failure modes. The chapter does not enumerate per-page UI detail, per-simulator data shape, or per-route API surface.

This chapter sits adjacent to Backend Services. Backend Services records the deployable backend services that participate in the contract-execution spine (bc-core, DevHub, bc-pg-mcp). Auxiliary Services records deployables that are independent of the spine: none of them produces authoritative tenant state, none of them is on the request path that traverses the four boundary acts, and none of them holds tenant data.

This chapter does not redefine Foundation invariants, the Object Model, the Authority Model, or the Architecture chapter's commitments. It does not enumerate the synthetic-data methodology that bc-sdg supports (deferred to Synthetic Data and Testing), the bc-admin operational dashboards (deferred to Frontend Experience), the platform observability schema (deferred to Observability and Telemetry in the Operations section), or the marketing content of bc-website (out of platform scope).

**Governing source.** Architecture; Backend Services; outline.md §4.3.

## Service Inventory

The platform composes from three auxiliary deployables. Each is independently startable, has a narrow role, and is outside the tenant-data execution path.

| Service | Runtime | Default port | Role |
|---|---|---|---|
| bc-core-dashboard | Node.js with Express and EJS (JavaScript) | 4100 | Stateless operational dashboard, registry browser, and trusted-host API tester for bc-core |
| bc-sdg | TypeScript with Fastify and Drizzle | 4200 | Synthetic data generator with per-system-type simulators (SAP S/4HANA, SAP ECC, Salesforce, MES); serves generated data over OData |
| bc-website | Astro with React and Tailwind | 4200 (dev only) | Static marketing site; production build emits static files for CDN hosting |

Two of the three (bc-sdg, bc-website) bind to port 4200 in their default configurations. The collision is a development-time concern only when both run on the same host concurrently; production hosting of bc-website does not bind a runtime port. Port 4200 sits outside the DEC-e50b83 reservation table; the table reserves 3000 to 3099 (frontends), 3100 to 3199 (APIs), 4000 to 4099 (development tools), 4100 to 4199 (operations tooling), 4300 to 4399 (AI services), and database and cache ports. Auxiliary deployables on 4200 occupy unreserved space; a future port-reservation update either includes 4200 in a new range or moves the auxiliary services into reserved space.

**Governing source.** Architecture; Backend Services; DEC-e50b83.

## bc-core-dashboard

### Purpose

bc-core-dashboard is a stateless operational dashboard for bc-core. It renders platform health, the registry catalogue (connectors, connections, readers, schemas), the boundary statistics (admission runs, metric snapshots, action objects), and an interactive HTTP request tester that proxies requests to bc-core. The dashboard is intended as a developer and operator visibility surface, but the current API tester is a trusted-host-only proxy surface rather than a read-only guarantee.

### At a glance

| Property | Value |
|---|---|
| Runtime | Node.js with Express and EJS (JavaScript) |
| Port | 4100 (configurable via `PORT` env var) |
| Backend dependency | bc-core HTTP API (`BC_CORE_URL` env var; no other dependencies) |
| Authentication | None at the dashboard's own boundary; the dashboard is trusted-host-only in the current configuration |
| Persistence | None; the dashboard is stateless and proxies all data from bc-core on each request |
| Source repository | `C:\MyProjects\bc-core-dashboard` |

### Behavior

The dashboard fetches data from bc-core on each page load (no caching beyond per-request HTTP) and renders Express + EJS templates. The interactive API tester proxies arbitrary HTTP requests to bc-core, bounded by a configurable timeout. Because the proxy is not documented here as restricted to safe read methods, the dashboard cannot be treated as a read-only boundary. The dashboard is intentionally simple: no build step beyond `npm install`, no compiled output, no server-side state.

### Constraints

- bc-core-dashboard holds no local state and writes to no database directly. Any platform or tenant state change still occurs only if bc-core accepts the proxied request under its own route semantics.
- bc-core-dashboard has no authentication boundary in the current implementation. Public exposure of the dashboard would expose bc-core read paths and the API tester proxy to unauthenticated callers. The current operating model is local-developer use only; deploying the dashboard outside a trusted host requires a security-hardening pass (added authentication, API tester method restrictions, proxy removal, or a reverse-proxy auth layer) that is not part of the current dashboard.
- The dashboard's `BC_CORE_URL` default points at `http://localhost:3000` in `src/index.js`; the actual bc-core port per DEC-e50b83 is 3100. The default is incorrect against the port reservation and is set per-environment via the env var.

### Failure modes

| Cause | System response |
|---|---|
| bc-core unreachable | Dashboard renders with empty registry and empty stats; no error page is surfaced to the user; configured per-request timeouts prevent the dashboard from hanging |
| bc-core returns HTTP error | The dashboard surfaces the error in the API tester; the dashboard rendering paths render empty for failed reads |
| Public network exposure | Per the constraint above, exposes bc-core read paths and the unrestricted proxy to unauthenticated callers |

**Governing source.** Backend Services; Architecture.

## bc-sdg

> **Residual risk (audit GAP-011).** The `bc-sdg` repository was not readable in the platform code/docs gap audit. All claims in this section about bc-sdg's runtime, port, database, OData shape, simulator coverage, and CLI behavior rest on prior grounding, not on this-pass verification. Treat as unverified until a dedicated readable bc-sdg pass confirms the synthetic-data methodology and per-simulator interfaces. Source: `bc-docs/reports/platform-code-doc-gap-report.md` GAP-011.

### Purpose

bc-sdg is a synthetic data generator with per-system-type simulators. It generates and serves realistic master and transactional data across three SAP landscapes (S/4HANA Public Cloud via OData V4, S/4HANA On-Premise via OData V4, SAP ECC EHP8 via OData V2) plus optional Salesforce Sales Cloud and MES per-profile generators. bc-core's Reader Flavors connect to bc-sdg's OData endpoints to read source data during admission, the same way they would connect to a real source system.

### At a glance

| Property | Value |
|---|---|
| Runtime | TypeScript on Node.js 20+ with Fastify and Drizzle ORM |
| Port | 4200 (configurable) |
| Modes | Hybrid: an HTTP service (`sdg serve`) that exposes OData V4 and V2 endpoints; a CLI (`sdg`) for interactive generation, reset, and migration |
| Database | Its own PostgreSQL database `bc_sdg` (not Platform DB; not Tenant DB); generated data lives entirely inside bc-sdg's database |
| Generation library | `@faker-js/faker` for realistic synthetic values |
| Per-system simulators | S/4HANA Public Cloud, S/4HANA On-Premise, SAP ECC EHP8; optional Salesforce Sales Cloud and MES |
| Industry profiles | Six built-in (manufacturing, pharma, automotive parts, chemicals, FMCG, real estate); each declares company structure, transaction volumes, and optional cross-system integrations |
| Source repository | `C:\MyProjects\bc-sdg` |

### Behavior

bc-sdg's CLI generates data into its own PostgreSQL database via Drizzle batch inserts. Its HTTP server then serves the generated data through OData endpoints that mimic the corresponding source-system protocols (SAP OData V4 for S/4HANA, OData V2 for ECC). bc-core's Reader Flavors connect to those endpoints as if they were real source systems; admission then runs against synthetic data without modification to the platform's reader code.

bc-sdg writes only to its own database. It does not call bc-core's API, does not write to Platform DB or Tenant DB, and is not in the request path that produces authoritative tenant state. The synthetic-data methodology (which scenarios are generated, what coverage they aim for, how the bench's qa-tenant convention works) is owned by Synthetic Data and Testing.

### Constraints

- bc-sdg writes only to its own database (`bc_sdg`). It does not bypass bc-core's authoring boundary, because the data it produces is consumed by bc-core's Readers as ordinary source-system input, not injected into Platform DB or Tenant DB directly.
- bc-sdg is not part of the tenant-data execution path. Production tenant runtimes do not host bc-sdg; the generator is a development and testing surface.
- bc-sdg's port (4200) is outside the DEC-e50b83 reservation table; the port discipline is a development-time convention pending a port-reservation update.

### Failure modes

| Cause | System response |
|---|---|
| `bc_sdg` PostgreSQL unreachable | CLI generation rejects with a connection error; OData server rejects requests with a connection error; no synthetic data is produced or served |
| OData endpoint shape drifts from a target system's actual OData contract | Reader Flavors that depend on the drifted shape reject during admission; the failure surfaces as a Reader Flavor failure inside bc-core, not as a bc-sdg failure |
| Generation profile is incomplete or invalid | CLI rejects with a profile-validation error; no partial data is written |

**Governing source.** Architecture; Backend Services.

## bc-website

### Purpose

bc-website is the BareCount marketing website. It is a static site that presents the platform's positioning to visitors. It is not part of the platform execution surface, holds no tenant data, and depends on no backend.

### At a glance

| Property | Value |
|---|---|
| Runtime | Astro 5 with React and Tailwind; MDX support for content pages |
| Output | Static HTML and assets (`output: "static"` in `astro.config.mjs`); production is a directory of static files |
| Dev port | 4200 (configured in `.claude/launch.json`) |
| Production hosting | CDN or static-file hosting; specific target is configured outside the repository |
| Backend dependency | None |
| Source repository | `C:\MyProjects\bc-website` |

### Behavior

The site is an Astro project with React components and Tailwind styling. Pages are authored under `src/pages/` (landing page and design-system reference in the readiness baseline). The build emits static HTML and bundled assets into `dist/` for delivery from a CDN. Content updates are deploy-once-and-cache; there is no runtime authentication, no API surface, and no per-visitor server-side rendering.

### Constraints

- bc-website holds no tenant data. It does not authenticate users, does not call bc-core, and does not connect to any platform database.
- bc-website's dev port (4200) collides with bc-sdg's default. The collision matters only when both run concurrently on the same host; production deployment of bc-website does not bind a runtime port.

### Failure modes

| Cause | System response |
|---|---|
| Build fails | The previous static deployment continues to serve until a successful build is published |
| CDN misconfiguration | Visitors receive static-host errors; the platform runtime is unaffected |

**Governing source.** Architecture.

## Cross-Service Posture

The three auxiliary services share a common posture relative to the platform execution spine:

| Property | bc-core-dashboard | bc-sdg | bc-website |
|---|---|---|---|
| In tenant-data execution path | No | No | No |
| Holds tenant data | No | No (holds synthetic data only, in its own database) | No |
| Calls bc-core authoring routes | No intended authoring role; unrestricted API tester proxy is a trusted-host-only mutation risk | No (does not call bc-core at all) | No |
| Production deployment posture | Local-developer or trusted-host use; not in production tenant runtimes | Local-developer or test-bench host; not in production tenant runtimes | CDN-hosted static site; not on the platform execution surface |
| Port reserved per DEC-e50b83 | Yes (4100) | No (4200, unreserved) | No (4200 dev only, unreserved) |

None of the three has a dependency that the bc-core execution spine consumes at runtime. The execution spine continues to produce authoritative state regardless of whether any auxiliary service is up, deployed, or even built.

**Governing source.** Architecture; Backend Services; The Authority Model.

## Governing Decisions

| Decision | Title | Auxiliary-service impact |
|---|---|---|
| DEC-e50b83 | Master port reservation | bc-core-dashboard occupies a reserved port (4100); bc-sdg and bc-website use unreserved port 4200; a future reservation update either reserves 4200 or moves the services into reserved space |
| DEC-9b23a7 | pm2 removed; independent service startup | Each auxiliary service starts independently in its own repository under its own watch; no central supervisor coordinates them |
| DEC-c06f41 | Spine expansion to eight sections plus home | The Auxiliary Services chapter exists in the reshaped Implementation section per DEC-c06f41 |

**Governing source.** The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model
- The Authority Model
- Operating Model: Overview
- Architecture
- Backend Services
- DEC-e50b83: Master port reservation
- DEC-9b23a7: pm2 removed; independent service startup
- DEC-c06f41: Spine expansion to eight sections plus home
- outline.md §4.3: Implementation
- Decisions: ADR Registry
