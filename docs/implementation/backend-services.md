---
id: backend-services
order: 17
title: "Backend Services"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, the-dual-layer-interaction-model, operating-model-overview, architecture]
governing_sources:
  - Foundation
  - The Object Model
  - The Contract Grammar
  - The Evaluation Boundaries
  - The Authority Model
  - The Dual-Layer Interaction Model
  - Operating Model
  - Architecture
governing_adrs:
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules)
  - DEC-771baf (Tenant database topology; platform-tenant one-way dependency)
  - DEC-e50b83 (Master port reservation)
  - DEC-9b23a7 (pm2 removed; independent service startup)
  - DEC-3395bc (v3 documentation structure; bc-core JWT-guarded /api/docs/*)
  - DEC-b97390 (bc-admin embedded documentation reader)
  - DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact)
  - DEC-a4e550 (ADR-first decision workflow; ADR files are the source of truth)
  - DEC-ebf0b4 (Session discipline and data integrity)
  - DEC-804874 (L-node semantic verification gate at session close)
  - DEC-324d9e (Subscription tiers and hosting variants)
  - DEC-c06f41 (Spine expansion to eight sections plus home)
errata_referenced: []
v2_sources:
  - legacy-v2/docs/architecture/index.md
  - legacy-v2/docs/decisions/ADR-1918d0.md
  - legacy-v2/docs/decisions/ADR-9b23a7.md
diagrams: []
---

# Backend Services

## Scope

This chapter describes the deployable backend services that compose the BareCount platform: bc-core (the single execution authority for the contract-execution spine), DevHub (the governance backbone for sessions, plans, decisions, and change records), and bc-pg-mcp (a read-only PostgreSQL surface for development tooling). For each service, the chapter records purpose, runtime, port, database access, authorization, dependencies, deployment shape, behavior, constraints, failure modes, and interactions with the other services.

This chapter sits between Architecture and the rest of Implementation. Architecture established the layers, surfaces, execution spine, contract chain, and repository composition that the platform realizes. Backend Services names the deployable backend artifacts that host that architecture and records what each one runs, on which port, against which database, under which authorization, and in dependency on which other services. The internal module catalog inside bc-core is owned by Internal Modules; the smaller deployables (bc-core-dashboard, bc-sdg, bc-website) are owned by Auxiliary Services; the AI runtime (bc-ai) is owned by AI Architecture in the AI section; the frontend services (bc-portal, bc-admin) are owned by Frontend Experience.

This chapter does not redefine Foundation invariants, the Object Model, the Contract Grammar, the Evaluation Boundaries, the Authority Model, or the Dual-Layer Interaction Model. It does not redefine the architectural commitments, layers, surfaces, execution spine, contract chain, two-database split, port reservation, or residency boundary recorded in Architecture. It does not enumerate AWS network, compute, secret, or storage detail (deferred to Infrastructure); database schemas (deferred to Data Model and Schema); endpoint catalogues (deferred to API Surface); the NestJS module catalog inside bc-core (deferred to Internal Modules); the per-service deployment topology in production (deferred to Infrastructure and to Deployment Topology in Operations); the development-tooling protocol that DevHub implements (deferred to Decision and Change Workflow in the Development section); the AI service runtime (deferred to AI Architecture in the AI section); or the synthetic-data and testing surfaces (deferred to Synthetic Data and Testing).

**Governing source.** Architecture; outline.md §4.3.

## Service Inventory

The platform composes from three deployable backend services. Each is independently startable, independently runnable, and owns a distinct architectural responsibility.

| Service | Runtime | Port | Primary database | Authorization boundary | Architectural role |
|---|---|---|---|---|---|
| bc-core | NestJS on Node.js | 3100 | Platform DB and Tenant DB (one connection per scope) | Cognito JWT with `custom:tenant_id` claim; `@PlatformOnly()` and `@TenantScoped()` route annotations | Single execution authority for the contract-execution spine; hosts the contract registry, the four boundary acts, and the documentation read-surface |
| DevHub | Node.js with Express | 4000 | Local SQLite via better-sqlite3 (`data/devhub.db`) | Local-trust development service; no remote authentication boundary | Governance backbone: sessions, plans, tasks, decisions, change records, activity log, MCP tool surface |
| bc-pg-mcp | Node.js with TypeScript | Standard input and output transport (no HTTP port) | Read-only connections to Platform DB and Tenant DB | Connection-string trust scoped to the local environment | Development tooling surface that exposes PostgreSQL state to MCP clients without authoring rights |

The three services do not depend on each other for runtime correctness. bc-core runs independently of DevHub (the platform executes contracts whether or not a developer has DevHub running). DevHub runs independently of bc-core (governance records persist whether or not the platform is up). bc-pg-mcp runs independently of both (it observes whatever a connection string can reach). Per DEC-9b23a7, no central supervisor coordinates the three; each starts in its own repository under its own watch.

**Governing source.** Architecture; DEC-e50b83; DEC-9b23a7.

## bc-core

### Purpose

bc-core is the single execution authority for the contract-execution spine. The four boundary acts (admission, canonical evaluation, metric evaluation, action evaluation) run only here. All `@PlatformOnly()` and `@TenantScoped()` API routes are served from this one runtime.

### At a glance

| Property | Value |
|---|---|
| Runtime | NestJS on Node.js 22+ (TypeScript) |
| Port | 3100 (configurable via `PORT` env var) |
| Platform DB | One Platform DB per environment (the dev environment uses the naming pattern `bc_platform_*`) |
| Tenant DB | One Tenant DB per tenant (the dev environment uses the naming pattern `tbc_{slug}_dev`) |
| Database driver | Drizzle ORM over the `postgres` library; one connection pool per scope |
| Authentication | Cognito JWT validated locally against the issuer's JWKS at every request boundary |
| Tenant scope | `custom:tenant_id` JWT claim binds tenant-scoped requests to one Tenant DB |
| Route annotations | `@PlatformOnly()` for control-plane routes; `@TenantScoped()` for execution-plane routes; both enforced by a global ScopeGuard |
| Cache | Redis (`REDIS_URL`, default `redis://localhost:6379`) |
| AI dependencies | bc-ai (`BC_AI_URL`, default `http://localhost:4300`) for orchestrated agent invocations; the Anthropic SDK is also called directly from bc-core for inline verification routines (catalog and Business Object verification) |
| Object storage | AWS S3 for evidence archival and the typed-fact / canonical / archive layer |
| Package registry | AWS CodeArtifact via `barecount/npm-mirror` (per `.npmrc`) |
| Source repository | `C:\MyProjects\bc-core` |

### Behavior

bc-core hosts both control-plane modules and execution-plane modules in one runtime. Control-plane modules serve the contract registry, the Source Catalog, master data, tenant identity records, Subscription records, governance state, and chain status. Execution-plane modules run the four boundary acts under bound contract versions, write the produced authoritative objects (Source Object, Canonical Object, Metric Snapshot, Action Object) to the addressed Tenant DB, and emit Evidence and Lineage at the same act that produces the object. The control-plane modules and execution-plane modules share the runtime; the database connections separate them: control-plane modules write the Platform DB, execution-plane modules write the addressed Tenant DB.

bc-core also serves the documentation read-surface introduced by DEC-3395bc. Three routes (`/api/docs/manifest`, `/api/docs/file/*splat`, `/api/docs/asset/*splat`) deliver manifest, markdown, and asset content to the bc-admin embedded reader. The routes are `@PlatformOnly()` JWT-guarded and rate-limited (60 requests per minute and 1000 per day per Cognito subject, enforced by an in-memory sliding-window interceptor). The source content lives in a gitignored `private-docs/` directory populated by `bc-admin/scripts/sync-docs.js`. The documentation surface is a delivery-plane concern colocated with the platform runtime so that authentication, rate limiting, and audit logging are shared with the rest of the platform's read paths.

bc-core depends on a small set of external systems by capability. PostgreSQL holds Platform DB and Tenant DB; the local development topology runs PostgreSQL on port 5434 via Docker compose. Redis on port 6379 holds short-lived runtime cache and rate-limit counters. AWS Cognito is the user-pool issuer; bc-core validates each request's JWT locally against the issuer's published JWKS rather than calling Cognito per request. The AI surface has two paths: bc-core invokes bc-ai over HTTP for orchestrated agent operations, and bc-core also calls the Anthropic SDK directly for inline verification routines such as catalog verification and Business Object verification. The model routing inside bc-ai (Bedrock inference profiles, model-family selection) is owned by the AI section. AWS S3 stores evidence archives and the canonical-archive layer that the Tenant DB references. The npm package registry is AWS CodeArtifact (`barecount/npm-mirror`) per DEC-441665; raw npmjs.org is not used for dependency installation.

### Constraints

- bc-core is the only runtime that runs the four boundary acts. The architecture admits no second execution authority for the spine. A second deployable that emitted Source Objects, Canonical Objects, Metric Snapshots, or Action Objects would split execution authority and is not permitted.
- bc-core writes to the Tenant DB through two governed categories only: the four boundary acts that produce authoritative runtime state, and tenant-scoped authoring acts that produce registration records (Connections, Contract Bindings, tenant-scoped extension content). Per DEC-1918d0 and DEC-771baf, no other write path to the Tenant DB exists.
- bc-core does not author tenant state outside governed acts. Discovery acts that read tenant data structure read tenant state without writing.
- bc-core's local port is 3100. Per DEC-e50b83, a service that changes its local port without a governed port-reservation update is incorrect against the architectural discipline.
- bc-core is started independently. Per DEC-9b23a7, no service supervisor coordinates bc-core with other services. The repository's `npm run start:dev` command starts the NestJS runtime under its own watch.

### Failure modes

| Cause | System response | Retriable | Recorded as |
|---|---|---|---|
| PostgreSQL connection failure on Platform DB | Control-plane requests reject with a connection error; execution-plane requests reject before they write any object; no partial state is emitted | Yes, after the connection recovers; no contract change required | Application logs; admission, canonical, metric, and action Run records record the failed invocation |
| PostgreSQL connection failure on a Tenant DB | Requests scoped to that tenant reject; requests scoped to other tenants are unaffected; no boundary act proceeds for the affected tenant | Yes, after the tenant connection recovers | Application logs; per-tenant Run records record the failed invocation |
| Redis unavailable | Routes that depend on cache fall back to direct database reads with degraded latency; no authoritative state is affected because cache holds no authoritative content | Yes, after Redis recovers | Application logs |
| Cognito JWT validation failure (expired token, invalid signature, missing `custom:tenant_id` for a tenant-scoped route) | Request rejects with `401 Unauthorized` or `403 Forbidden`; no authoritative state is read or written | Yes, after the client renews the token; not retriable for an invalid signature | Application logs; rate-limit accounting on `/api/docs/*` routes |
| AI surface unavailable (bc-ai unreachable, or the Anthropic SDK rejects) | AI-dependent acts do not proceed; contract execution does not depend on AI and continues for non-AI paths. The continuation semantics for AI gates are owned by AI Gates and Onboarding workflows | Yes, after the AI surface recovers | Application logs; per-act records in the AI gate's owning chapter |
| AWS S3 unavailable | Acts that archive to S3 do not complete the archive step; the boundary act records the partial completion and does not emit a successful archive. The authoritative object is not produced if archival is part of the boundary's contract | Yes, after S3 recovers | Application logs; boundary Run records |
| AWS CodeArtifact token expired | `npm install` and dependent build steps reject with HTTP 401 or 403; running runtimes are unaffected because installation is a build-time concern | Yes, after the package-registry session is renewed by the owning Build and Release procedure | Build logs |
| Platform DB schema drift between Drizzle definitions and the authoritative DDL | Strict-mode TypeScript builds reject; runtime startup rejects if a column the runtime depends on is missing | Yes, after the schema is reconciled (DDL is authoritative per Data Model and Schema) | Build logs; startup logs |

The architectural discipline is that bc-core does not silently degrade authoritative state production. A failure that prevents a boundary act produces no Source Object, Canonical Object, Metric Snapshot, or Action Object; no partial Evidence is written; the Run record records the failure. The next invocation re-attempts under the same bound contract version; per Invariant IV, supersession does not auto-advance the bound version.

### Interactions

bc-core is referenced by bc-portal and bc-admin (read and authoring routes through the JWT-guarded API), by bc-ai (called over HTTP from bc-core for orchestrated agent operations), by external integration paths that consume Action Objects, by bc-pg-mcp (which reads from the same PostgreSQL instances bc-core writes to, but through its own connection string), and by DevHub (which calls bc-core's L-node semantic audit endpoint at session-close time). bc-core does not depend on DevHub at runtime: governance records are authored by developer tooling, not by the runtime that produces tenant state. bc-core depends on the contracts published in the Platform DB; the authoring paths that produce those contracts are platform routes inside bc-core itself.

**Governing source.** Architecture; The Object Model; The Contract Grammar; The Evaluation Boundaries; DEC-1918d0; DEC-771baf; DEC-e50b83; DEC-9b23a7; DEC-3395bc; DEC-441665.

## DevHub

### Purpose

DevHub is the governance backbone for the platform's engineering practice. It records sessions (every coding interaction is opened against a DevHub session), plans (each session saves its intended work before editing), tasks (the unit of intended work), decisions (every architectural decision is recorded as an ADR), change records (each session's plan and report under ISO 27001 A.14.2.1), and activity log (the append-only event stream across the engineering practice). DevHub exposes its surface as MCP tools so that AI development assistants can author governance records as part of doing the engineering work.

### At a glance

| Property | Value |
|---|---|
| Runtime | Node.js with Express (JavaScript) |
| Port | 4000 (configurable via `PORT` env var) |
| Database | Local SQLite via better-sqlite3 in WAL mode with foreign keys enforced |
| Database file | `data/devhub.db` (one per developer instance) |
| View layer | EJS for the local web surface |
| MCP transport | A separate `src/mcp-server.js` runtime binds standard input and output and calls the Express HTTP API on `localhost:4000` for tool invocations |
| Authentication | No remote authentication boundary; the HTTP server has no auth middleware and is reachable only from the host the runtime binds on |
| Documentation index | Scans `bc-docs-v3/docs/` on boot and on demand; derives type, domain, and authority from filesystem path and frontmatter; default path overridable via `BC_DOCS_PATH` |
| Source repository | `C:\MyProjects\barecount-devhub` |

### Behavior

DevHub composes from two cooperating runtimes that share one HTTP API surface. The first is the Express HTTP server (started by `npm run dev` or `npm start` from `src/index.js`); it binds port 4000, serves the developer-facing EJS browser views, and exposes the JSON HTTP API. The second is the MCP server (started by `npm run mcp` from `src/mcp-server.js`); it binds standard input and output, registers the `devhub_*` tool surface, and translates tool invocations into HTTP calls against the Express API on `localhost:4000`. AI development assistants reach DevHub through the MCP server; human developers reach it through the browser views. The protocol semantics of individual tools are owned by Decision and Change Workflow in the Development section.

DevHub holds its data in better-sqlite3. Each developer instance has its own `data/devhub.db`. Governance records authored on one developer instance are not automatically visible on another; the durable record of platform decisions is the ADR file committed to the bc-docs-v3 repository (per DEC-a4e550). DevHub's better-sqlite3 store is the metadata index that points at those files and records the procedural state (sessions, change records, activity log) under which the files were produced.

DevHub indexes the documentation. On boot and on demand via `devhub_doc_scan`, it walks `bc-docs-v3/docs/` (the path is configurable through the `BC_DOCS_PATH` environment variable for legacy v2 scans), reads each file's frontmatter, and records the resulting metadata in its better-sqlite3 store under the `documents` table. The `devhub_doc_list` and `devhub_doc_get` tools serve the metadata; the file content is read directly from the source repository on each request.

DevHub depends on bc-core for the L-node verification check that runs during session close. The `devhub_session_close` path calls a bc-core audit endpoint using a configurable `BC_CORE_URL`; if the endpoint is unreachable, the gate fails open per DEC-804874 and records the condition. Backend Services records that dependency shape only. The close protocol, override semantics, follow-up task behavior, and self-audit payload are owned by Decision and Change Workflow in the Development section.

### Constraints

- DevHub is not in the path that produces authoritative tenant state. The execution spine in bc-core does not depend on DevHub; contracts execute whether or not DevHub is running.
- DevHub does not author platform state. The contracts that bc-core executes against, the Source Catalog entries, master data, and tenant identity records are all authored through bc-core's control-plane routes and stored in the Platform DB. DevHub authors governance records (sessions, plans, decisions, change records) and indexes documentation; it does not write to the Platform DB or any Tenant DB.
- DevHub may be deployed to a team-shared host for cross-developer visibility (a deployment script in `scripts/deploy.sh` targets a long-running host). Each developer instance, local or shared, holds its own better-sqlite3 store; the durable cross-instance authority for decisions is the ADR file in the bc-docs-v3 repository, not the better-sqlite3 row.
- DevHub's port is 4000. Per DEC-e50b83, the port is reserved and a change requires a governed port-reservation update.
- DevHub is started independently. Per DEC-9b23a7, no service supervisor manages it; the repository's `npm run dev` command starts the Express server under Node's `--watch`, and `npm run mcp` starts the MCP server separately.
- DevHub stores governance metadata; the durable authority is the ADR file. The decision row stored in better-sqlite3 carries the UID, title, status, description, file path, and domain; the decision content lives in the ADR file under `bc-docs-v3/docs/adrs/`. A reader who needs the decision's full context reads the ADR file, not the better-sqlite3 row.

### Failure modes

| Cause | System response | Retriable | Recorded as |
|---|---|---|---|
| better-sqlite3 file lock contention | Concurrent writes serialize behind the file lock; long-held locks reject further writes with a busy error | Yes, after the lock releases | Application logs |
| `data/devhub.db` corruption | DevHub fails to open the database on startup and exits; recovery requires restoring from a developer-side backup or seeding a fresh database with `npm run seed` | No automatic recovery; manual restore or reseed | Startup logs |
| MCP transport connection drop | The MCP client reconnects on the next tool invocation; in-flight tool calls fail and are reported to the calling session | Yes, on the next invocation | MCP client logs; activity log if the call reached the tool handler |
| `bc-docs-v3/docs/` path missing or unreadable | Documentation scan reports the failure; previously indexed entries remain in better-sqlite3 until the next successful scan | Yes, after the path is reachable | Scan log entry; activity log |
| L-node semantic verification gate fails open due to bc-core or Cognito unavailability | Per DEC-804874, the gate fails open: an infrastructure outage in bc-core's L-node verification endpoint does not block session close. The session closes; a follow-up task is not auto-spawned in that case because the verdict could not be computed | Yes, after bc-core recovers and the next session runs verification | Activity log; change record records the gate-failed-open state |

DevHub does not silently lose governance records. A failed `devhub_session_close` call leaves the session open; the next session's `devhub_session_boot` reports it as orphaned and the recovery protocol applies. A failed `devhub_change_record_save` rejects the call without partial persistence.

### Interactions

DevHub is invoked by AI development assistants (via the MCP server) and by developers (via the browser surface on port 4000). DevHub reads from `bc-docs-v3/docs/` as the documentation source; it writes ADR files to `bc-docs-v3/docs/adrs/` when `devhub_decision_record` is invoked, per DEC-3395bc. DevHub does not depend on bc-core at runtime, but its L-node semantic verification gate calls a bc-core endpoint when computing the session-close verdict; the gate fails open if that endpoint is unavailable. DevHub does not depend on bc-pg-mcp; it reads its own better-sqlite3 store and the documentation files directly.

**Governing source.** Architecture; DEC-a4e550; DEC-ebf0b4; DEC-804874; DEC-3395bc; DEC-e50b83; DEC-9b23a7.

## bc-pg-mcp

### Purpose

bc-pg-mcp is a read-only PostgreSQL MCP server that surfaces Platform DB and Tenant DB state to development tooling. It exists so that AI development assistants and developer scripts can query the live database without bypassing bc-core's authoring boundary, and without needing to instantiate a separate database client per session.

### At a glance

| Property | Value |
|---|---|
| Runtime | Node.js 18+ with TypeScript |
| Port | Standard input and output transport (no HTTP port) |
| Database access | One PostgreSQL connection per server instance, configured via `PGMCP_DATABASE_URL`; pool size capped at three connections |
| Authorization | Connection-string trust scoped to the host environment; no remote authentication boundary |
| Tool surface | Exactly seven tools: `pg_server_info`, `pg_list_schemas`, `pg_list_tables`, `pg_describe_table`, `pg_list_indexes`, `pg_query`, `pg_count` |
| Read-only enforcement | Three layers for arbitrary `pg_query` calls: a runtime-side SQL guard (statement validator), parameterized execution through the `postgres` library, and PostgreSQL `default_transaction_read_only=on` at connection level. Schema-aware introspection tools also apply the `PGMCP_SCHEMAS` schema allowlist. |
| Row cap | `PGMCP_MAX_ROWS` env var, hard range [1, 10000], default 1000 |
| Query timeout | `PGMCP_TIMEOUT_MS` env var |
| Write mode | Not part of BareCount-governed operation; the service contract is read-only |
| Source repository | `C:\MyProjects\bc-pg-mcp` |

### Behavior

bc-pg-mcp registers as an MCP server in the consumer's Claude Code settings. The barecount-devhub worktree registers it as `bc-postgres` with a connection string targeting Platform DB, a `PGMCP_SCHEMAS` allowlist of `contract,source,metric,platform,runtime,master`, a `PGMCP_MAX_ROWS` of 500, and `PGMCP_OUTPUT_FORMAT=tsv`. It exposes exactly seven tools that map to standard PostgreSQL introspection and query operations: `pg_server_info` returns server version and configured connection metadata; `pg_list_schemas` lists schemas filtered by the allowlist; `pg_list_tables` lists tables in a schema with row counts; `pg_describe_table` returns columns, types, constraints, and indexes for a table; `pg_list_indexes` returns index definitions for a table; `pg_query` executes a read-only-guarded SELECT, WITH, or EXPLAIN statement and returns rows; `pg_count` returns the row count for a table or for a counted query.

Read-only enforcement composes three layers for arbitrary `pg_query` calls. The first is the runtime-side SQL guard: it admits only statements starting with SELECT, WITH, or EXPLAIN; rejects statements containing semicolons (preventing multi-statement injection); rejects statements containing `--` or `/*`; and rejects DDL or DML keywords from a configured block-list after string literals are stripped. The second is parameterized execution through the `postgres` library. The third is PostgreSQL's `default_transaction_read_only=on` connection setting, which causes the database itself to reject any write statement that survives the first two layers. The `PGMCP_SCHEMAS` allowlist applies to schema-aware tools and configured introspection surfaces; it is not represented here as a parser for arbitrary SQL in `pg_query`. The result-row cap (`PGMCP_MAX_ROWS`) appends a `LIMIT` clause when the client query has none, preventing an unbounded query from exhausting the MCP transport buffer.

bc-pg-mcp's connection string is configured at registration time as an environment variable; it is not stored in any persistent index. The credential is part of the host environment that registered the MCP server.

### Constraints

- bc-pg-mcp is read-only in BareCount-governed operation. Any implementation switch that disables database read-only mode is outside the governed service contract and is not used for normal operation.
- bc-pg-mcp is a development-time tool. It is not part of the platform runtime; production tenant environments do not register it.
- bc-pg-mcp does not bypass bc-core's authoring boundary. A developer or AI assistant that needs to author state goes through bc-core's API routes; bc-pg-mcp provides observation, not authoring.
- bc-pg-mcp uses standard input and output transport. It does not bind to a TCP port and does not appear in the port reservation table.

### Failure modes

| Cause | System response | Retriable | Recorded as |
|---|---|---|---|
| `PGMCP_DATABASE_URL` invalid or PostgreSQL unreachable | Tool calls reject with a connection error; the MCP client receives the error and may retry | Yes, after the connection recovers or the configuration is corrected | MCP client logs |
| Query starts with a keyword outside SELECT, WITH, or EXPLAIN | The SQL guard rejects the statement before it reaches the database; the tool returns the guard error | Not applicable; the act is forbidden by the read-only commitment | Tool response payload |
| Query contains a semicolon, a `--` comment delimiter, or a block-listed keyword | The SQL guard rejects the statement before it reaches the database | Not applicable | Tool response payload |
| Write statement that survives the SQL guard reaches the database | PostgreSQL rejects the statement under `default_transaction_read_only=on`; the tool returns the database error | Not applicable | Tool response payload |
| Query targets a schema not in `PGMCP_SCHEMAS` through a schema-aware tool | The schema-aware tools (list, describe, count) return empty or rejected. Arbitrary `pg_query` SQL is guarded for read-only behavior but is not described here as schema-parsed by the allowlist. | Yes, after the allowlist is updated and the server restarted | Tool response payload |
| Query lacks an explicit limit and exceeds `PGMCP_MAX_ROWS` | The runtime appends a capped `LIMIT` clause when the query lacks one. Queries that include their own `LIMIT` are not documented here as rewritten down to the cap. | Yes, with a narrower query or a higher cap | Tool response payload |
| Query exceeds `PGMCP_TIMEOUT_MS` | PostgreSQL cancels the statement; the tool returns the timeout error | Yes, with a faster query or a higher timeout | Tool response payload |
| MCP transport disconnected | The runtime exits when standard input closes; the MCP client may relaunch the server | Yes, on relaunch | MCP client logs |

### Interactions

bc-pg-mcp is invoked by AI development assistants and by developer scripts via the MCP server interface. It reads from the same PostgreSQL instances that bc-core writes to, but through its own connection strings and its own read-only transaction discipline. bc-pg-mcp does not depend on bc-core at runtime: it speaks PostgreSQL directly. bc-pg-mcp does not depend on DevHub.

**Governing source.** Architecture; DEC-1918d0; DEC-e50b83; DEC-9b23a7.

## Cross-Service Topology

The three backend services compose at three points: a shared package registry, a shared port reservation, and a shared documentation source.

| Shared resource | What is shared | What is not shared |
|---|---|---|
| AWS CodeArtifact npm registry (`barecount/npm-mirror`) | All three services install npm packages through the same CodeArtifact mirror per DEC-441665. The registry is a supply-chain governance boundary, not a runtime dependency | Runtime database connections, runtime authentication boundaries, runtime caches |
| Port reservation table (DEC-e50b83) | The local-development port assignments are coordinated across all platform services so that a developer running multiple services has stable, predictable addresses for each | Production port placement is owned by Infrastructure |
| Documentation source (`bc-docs-v3/docs/`) | bc-core serves documentation to bc-admin from this source per DEC-3395bc. DevHub indexes the same source to populate its document registry. bc-pg-mcp does not consume documentation | Authoritative state, runtime caches, governance records |

The three services do not share a runtime database. bc-core uses PostgreSQL (Platform DB and Tenant DB). DevHub uses local better-sqlite3. bc-pg-mcp reads the PostgreSQL instances bc-core uses but through its own read-only connections, not through bc-core's connection pool.

The three services do not share an authentication boundary. bc-core enforces Cognito JWT at every request boundary. DevHub is local-trust on the developer's machine. bc-pg-mcp is connection-string trust scoped to the local environment. A request authenticated to bc-core does not carry authority on DevHub or bc-pg-mcp; a developer authenticated to DevHub or bc-pg-mcp does not carry authority on bc-core.

The three services do not share a supervisor. Per DEC-9b23a7, pm2 was removed because pm2 on Windows spawned a visible cmd.exe window for each supervised service, broke memory monitoring, and treated bc-core's MCP backbone as restartable alongside application services. Each service starts independently in its own repository under its own watch.

**Governing source.** Architecture; DEC-441665; DEC-e50b83; DEC-3395bc; DEC-9b23a7.

## Local Development Topology

The three services are designed to be started independently in the developer's local environment. The startup pattern is:

| Service | Working directory | Start command | Watch behavior |
|---|---|---|---|
| DevHub | `C:\MyProjects\barecount-devhub` | `npm run dev` | Node `--watch` restarts on source change |
| bc-core | `C:\MyProjects\bc-core` | `npm run start:dev` after `docker compose up -d` for PostgreSQL and Redis | NestJS with SWC restarts on source change |
| bc-pg-mcp | Registered in the consumer's Claude Code settings | Launched on demand by the MCP client | Restarted by the MCP client when it reconnects |

DevHub is started first and kept running for the entire engineering session. It is the MCP backbone; subsequent service starts assume it is up. bc-core is started when contract-execution work is in scope. bc-pg-mcp is launched by the MCP client when a developer invokes one of its tools; it does not need a long-running supervisor.

The local development topology depends on Docker compose for PostgreSQL on port 5434 and Redis on port 6379. Both are started from `C:\MyProjects\bc-core` via `docker compose up -d`. The compose configuration is owned by bc-core because bc-core is the only runtime that authors against PostgreSQL and Redis; DevHub holds its own SQLite store independently, and bc-pg-mcp connects to the same PostgreSQL instance read-only through its own connection string.

The CodeArtifact token has a finite TTL. When `npm install` rejects with HTTP 401 or 403, the package-registry session has usually expired. Renewal is a developer-side Build and Release procedure and does not affect running services.

**Governing source.** DEC-9b23a7; DEC-441665; DEC-e50b83; DEC-1918d0.

## Hosting and Deployment Shape

Backend Services records the deployment-shape invariants that every hosting variant must preserve. The variant inventory (Demo, Starter, Professional, Enterprise; AWS Shared, Separate, BYO-DB, BC-Agent) is owned by the chapter that authors the variants.

| Service | Deployment-shape invariant | Why |
|---|---|---|
| bc-core | Single execution authority for the spine. Every hosting variant runs bc-core such that it is the only runtime emitting Source Objects, Canonical Objects, Metric Snapshots, and Action Objects | Two execution authorities would split the spine and is not authorized by the architecture |
| bc-core | Cognito JWT validation at every request boundary, with `custom:tenant_id` binding tenant-scoped requests to one Tenant DB | The auth boundary is the request-time enforcement of the asymmetric ownership rule |
| bc-core | Platform DB and Tenant DB remain separate physical scopes; one Platform DB per environment, one Tenant DB per tenant | Two-database split per DEC-1918d0 and DEC-771baf is preserved across all hosting variants |
| bc-core | Evidence and Lineage are emitted at the same act that produces the corresponding authoritative object | Per The Evaluation Boundaries; the proof-emission rule is hosting-variant-independent |
| DevHub | Not in the tenant-data execution path. May be deployed to a team-shared host for cross-developer visibility; deployed instances do not author tenant state and remain outside the four boundary acts | Governance authoring is a development-time concern; durable cross-instance authority is the ADR file in the bc-docs-v3 repository, not the DevHub better-sqlite3 store |
| bc-pg-mcp | Not in the tenant-data execution path. Registered locally per consumer; production tenants do not register it as part of their runtime | Read-only observation is a development-time concern; production tenant runtimes do not include MCP tooling |

The hosting variant detail (which operator runs what, what the prerequisites are, what the lifecycle gates are, which tier maps to which variant, which commercial categorization applies) is owned by Tenant Lifecycle and Subscription in the Operations section. Backend Services records only the service-level invariants every variant must preserve.

Production deployment placement (which AWS account, which region, which network, which compute target, which ALB, which database service tier, which secret store path) is owned by Infrastructure in the Implementation section and by Deployment Topology in the Operations section. Backend Services records the service-level deployment shape, not the production placement.

**Governing source.** DEC-1918d0; DEC-771baf; DEC-324d9e; The Object Model; The Evaluation Boundaries.

## Governing Decisions

The decisions that govern the deployable backend services are listed below. Per-component ADRs that apply to one service's internals are listed in the chapter for that component.

| Decision | Title | Service-level impact |
|---|---|---|
| DEC-1918d0 | Deployment and database architecture; ten normalization rules | Two-database split; bc-core writes Platform DB and Tenant DB through separate connections under the asymmetric ownership rule |
| DEC-771baf | Tenant database topology; platform-tenant one-way dependency | bc-core writes tenant state only through governed runtime acts and governed tenant-scoped authoring acts; bc-pg-mcp observes tenant state read-only |
| DEC-e50b83 | Master port reservation | bc-core on 3100; DevHub on 4000; bc-pg-mcp on standard input and output (not in the port table) |
| DEC-9b23a7 | pm2 removed; independent service startup | Each service starts independently in its own repository; no central supervisor coordinates them |
| DEC-3395bc | v3 documentation structure; bc-core JWT-guarded `/api/docs/*` | bc-core hosts the documentation read-surface for the bc-admin embedded reader; DevHub indexes the same source for `devhub_doc_*` tools |
| DEC-b97390 | bc-admin embedded documentation reader | bc-core's `/api/docs/*` routes serve the canonical reader hosted in bc-admin |
| DEC-441665 | NPM supply chain mitigation via AWS CodeArtifact | All three services install npm packages through the `barecount/npm-mirror` CodeArtifact registry |
| DEC-a4e550 | ADR-first decision workflow; ADR files are the source of truth | DevHub stores decision metadata; the ADR file under `bc-docs-v3/docs/adrs/` is the durable authority |
| DEC-ebf0b4 | Session discipline and data integrity | DevHub participates in the session-discipline protocol; detailed gate semantics are owned by Decision and Change Workflow |
| DEC-804874 | L-node semantic verification gate at session close | DevHub depends on bc-core for the L-node verification check used during session close; detailed override semantics are owned by Decision and Change Workflow |
| DEC-c06f41 | Spine expansion to eight sections plus home | The Backend Services chapter exists in the reshaped Implementation section per DEC-c06f41 |

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
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-e50b83: Master port reservation
- DEC-9b23a7: pm2 removed; independent service startup
- DEC-3395bc: v3 documentation structure
- DEC-b97390: bc-admin embedded documentation reader
- DEC-441665: NPM supply chain mitigation via AWS CodeArtifact
- DEC-a4e550: ADR-first decision workflow
- DEC-ebf0b4: Session discipline and data integrity
- DEC-804874: L-node semantic verification gate
- DEC-c06f41: Spine expansion to eight sections plus home
- outline.md §4.3: Implementation
- Decisions: ADR Registry
