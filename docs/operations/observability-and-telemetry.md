---
id: observability-and-telemetry
order: 34
title: "Observability and Telemetry"
status: drafting
authority: authoritative
depends_on: [the-authority-model, infrastructure, audit-and-activity-logging, backend-services]
governing_sources:
  - The Authority Model
  - Audit and Activity Logging
  - Infrastructure
governing_adrs:
  - DEC-1918d0 (Deployment and database architecture)
  - DEC-bebaec (Chain Completeness SSOT)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Observability and Telemetry

## Scope

This chapter records the operational view of platform observability and telemetry. It states the structured-logger discipline (no `console.log` in `src/`; only `console.warn` and `console.error` admissible), the health-endpoint surface (`/api/health`), the bc-core docs JSONL access log that CloudWatch reads at the log group, the bc-ai evidence table that records every AI invocation, the chain status SSOT as the operational read for chain completeness (DEC-bebaec), the metric snapshot table as the operational read for metric runtime, the access-log retention configured at the dormant `PlatformInfraStack` HTTP API construct (1-year retention as coded), and the gaps the chapter records honestly (no consolidated dashboard, no AWS CloudTrail consumption, no alerting wired in the readiness baseline). It records the boundary between Observability and Telemetry and the audit substrate that governs change records (Audit and Activity Logging in Implementation). It records the as-built drift between the procedure and the platform's readiness-baseline observability state.

This chapter does not redefine the audit substrate (Audit and Activity Logging), the metric evaluation runtime (Metric Evaluation; Metric Catalog), or the chain status SSOT (Chain Completeness and Verdict).

The chapter records what the platform observes in the readiness baseline, not what an aspirational SRE-grade observability surface would look like.

**Governing source.** outline.md §4.7; Audit and Activity Logging.

## What the Platform Emits

The platform's readiness-baseline emission surface is decentralized across four substrates.

| Emission | Surface | Persistence |
|---|---|---|
| HTTP request log | bc-core stdout via NestJS default logger | Container stdout; CloudWatch when bc-core deploys to AWS; readiness baseline uses local stdout only |
| Document access log | bc-core `DocsController.audit()` writes JSONL after successful docs controller handling | bc-core local file; CloudWatch picks up the JSONL at the log group when deployed; lookup misses and rate-limit denials are warning logs in the readiness baseline |
| AI invocation evidence | bc-ai writes one row per Bedrock or Anthropic-direct call to its `evidence` table | bc-ai PostgreSQL evidence table |
| DevHub session and activity log | DevHub MCP records every session, checkpoint, change record, plan, and decision | DevHub SQLite at `data/devhub.db` |

A consolidated observability pane is not part of the readiness baseline. Each emission surface is its own read; an operator answering "what happened in the last hour" reads each surface separately.

**Governing source.** Audit and Activity Logging.

## Structured Logger Discipline

Per CLAUDE.md (Coding Standards section), `console.log/info/debug/trace` are forbidden in `src/` directories. Only `console.warn()` and `console.error()` are admissible. Structured logging through a logger instance is the platform's preferred path.

The discipline is enforced by the `bc-qa` audit set (`audit-repo.sh <repo-path>`) and by the per-repo pre-commit hook (`bc-qa/hooks/pre-commit`). Scripts and seed files are exempt; structured logging in those is project judgment.

The structured logger is not a single library decision in the readiness baseline. Different services use different loggers (NestJS default in bc-core; Python `logging` in bc-ai; Node `console.error` plus the discipline above in DevHub). A unified logger choice across the platform is not a committed platform baseline; the discipline is the per-repo audit gate.

**Governing source.** CLAUDE.md (Coding Standards section); `bc-qa/audits/`.

## Health Endpoints

| Service | Path | Purpose |
|---|---|---|
| bc-core | `GET /api/health` | Returns 200 when the service is responsive; full controller live at `bc-core/src/health/health.controller.ts` |
| bc-ai | `GET /api/ai/health` | Returns 200 when the FastAPI app is responsive |
| Per-Connection health | `GET /api/connections/:connectionId/health` | Returns the operational status of a tenant's per-source-system Connection (live at `bc-core/src/registry/connection.controller.ts`) |

A health endpoint is a liveness probe. None of the three constitute a deep readiness check (database reachability, later service reachability, queue depth, etc.); deeper readiness is queued.

**Governing source.** `bc-core/src/health/health.controller.ts`; `bc-core/src/main.ts`; `bc-ai/main.py`.

## Document Access JSONL Trail

bc-core's `DocsController` emits JSONL after successful handling on the bc-admin reader's `/api/docs/*` endpoints. The line carries the Cognito subject identifier, the resource path, the timestamp, the bytes served, and the request identifier.

The intent is CloudWatch ingestion when bc-core deploys to AWS. The current local-only deployment writes to stdout. The CloudWatch log group at AuthStack is configured with 1-year retention (per Infrastructure); the dormant `HttpApi` construct in `PlatformInfraStack` configures the same retention for the HTTP API access log when that stack is deployed.

The JSONL trail is the platform's first operational telemetry surface. It is the proof-of-concept caller for `bc-core/src/audit/audit.service.ts`; broader rollout to every authenticated mutation is queued in the Audit and Activity Logging chapter's drift inventory.

**Governing source.** `bc-core/src/audit/audit.service.ts`; Audit and Activity Logging; Infrastructure.

## bc-ai Evidence Table

bc-ai records evidence rows for completed maker-checker-gate acts. The current SQLite schema carries flow id, entity, routing, maker/checker/gate outputs, combined confidence, prompt version, model ids, token counts, cost, and duration; it does not carry a hashed prompt value or provider response id.

The evidence table is the operational telemetry substrate for AI verdicts, while `budget_log` records Bedrock and direct-Anthropic provider cost. Gemini calls remain a cost-capture gap unless routed through the same budget logger.

**Governing source.** AI Evidence and Budgeting; `bc-ai/app/db/schema.sql`; `bc-ai/app/clients/bedrock.py`; `bc-ai/app/clients/anthropic_client.py`.
## Chain Status SSOT as Operational Read

DEC-bebaec establishes `contract.chain_status` as the SSOT for chain completeness. The operational consequence: an operator answering "is metric X computable end-to-end?" reads from the chain status SSOT, not from ad-hoc queries against the chain artifacts.

The MCP tool `devhub_chain_status` exposes the SSOT to Claude sessions; the bc-admin Metric Readiness page (per CLAUDE.md) is the operator-facing surface; the underlying API is `GET /registry/chain-status/summary` and `GET /registry/chain-status/funnel`.

The chain status SSOT is the platform's first observability surface that aggregates across the contract chain. It is not a general-purpose metrics dashboard; it is a chain-completeness query surface.

**Governing source.** DEC-bebaec; CLAUDE.md (Chain Completeness SSOT section); Chain Completeness and Verdict.

## Metric Snapshot Table

`metric.metric_snapshot` is the runtime emission of the metric engine. Each row carries the MC identifier, the grain values, the snapshot value, the band classification, the timestamp, and the per-CO evidence identifiers.

The metric snapshot table is the operational read for "what value does this metric expose for the selected read?". The bc-admin metric catalog UI reads against it. The chain status SSOT references it for the L8 chain-coverage check.

**Governing source.** Metric Evaluation; Metric Catalog.

## DevHub Activity Log

DevHub records every governed-platform-action through its MCP tools as a row in the SQLite `data/devhub.db`. The activity log includes session start, session close, plan save, checkpoint, change record (plan and report sides), task creation and completion, decision recording, screen update, document scan, and risk add.

The activity log is the platform's governed-action audit trail for the platform team. The MCP tool `devhub_activity_log` exposes the trail to Claude sessions; the DevHub web surface (port 4000) renders it for human review.

The activity log is project-scoped (one project, multiple sessions). A cross-project view aggregates across projects; the current local DevHub instance carries the activity for every project the engineer touches.

**Governing source.** Audit and Activity Logging; DevHub MCP tool surface.

## Aspirational Surfaces

Several observability surfaces are aspirational against the readiness baseline. The chapter records them honestly so the gap is visible.

| Surface | Form |
|---|---|
| Consolidated observability dashboard | No single pane of glass that aggregates HTTP requests, AI invocations, chain status, metric snapshots, DevHub activity, security events |
| Alerting | No PagerDuty or equivalent; no alarm definitions in `PlatformInfraStack`; the dormant Aurora construct configures CloudWatch alarms for backup and storage but the stack is not deployed |
| AWS CloudTrail consumption | Cognito admin operations and any future AWS-resource changes emit CloudTrail events; the platform does not aggregate them in the readiness baseline |
| Per-tenant observability | The chain status SSOT is platform-scoped; per-tenant chain status is queryable but not surfaced as a tenant-facing view |
| Distributed tracing | No OpenTelemetry, Jaeger, X-Ray, or equivalent; per-request trace correlation through the request-identifier header is the substitute |
| Synthetic monitoring | No external probe pings the deployed AuthStack or `/health` endpoints |
| Cost telemetry | bc-ai records cost per invocation; AWS-side cost telemetry per service or per tenant is not aggregated |

Each row in this table is a queued observability surface. The platform's readiness-baseline emission discipline is the substrate the queued surfaces will read from when wired.

**Governing source.** Audit and Activity Logging; Infrastructure.

## Failure Modes

| Cause | System response |
|---|---|
| `console.log` slipped past the pre-commit hook | The `bc-qa` audit catches it; CI gate fails for repos where ESLint blocks; the engineer rewrites |
| bc-core stdout overflows in local dev | Container restart; logs lost; structured logging at the queued unified-logger choice would solve this with rotation |
| bc-ai evidence write fails | bc-ai retries the write; if persistent failure, the AI invocation result returns to the caller but the audit trail is incomplete; recorded as a known integrity failure |
| Chain status SSOT stale | Per DEC-bebaec, the SSOT is event-driven plus periodically reconciled via the chain-status reconcile endpoint; staleness surfaces as outdated read; the reconciliation is operator-initiated in the readiness baseline |
| DevHub SQLite write contention | Multiple Claude sessions writing concurrently can serialize on SQLite; rare in single-engineer dev; not modeled as a multi-engineer production concern in the readiness baseline |
| CloudWatch ingestion fails (when deployed) | bc-core continues to emit; the JSONL trail accumulates locally; ingestion failure surfaces as missing log-group entries; recoverable on next ingestion attempt |

**Governing source.** Audit and Activity Logging; Infrastructure.

## Drift Inventory

| Drift item | Form |
|---|---|
| No unified logger choice | Per-service logger; per-service format; aggregation across services requires per-format parsing |
| No deep readiness probe | Health endpoints are liveness only; readiness (database reachable, later service reachable, queue depth) is queued |
| No alerting wired | No alarm definitions; no on-call routing; no incident escalation surface (Support and Escalation governs the customer-side response when wired) |
| No AWS CloudTrail consumption | Account-level CloudTrail emits events; platform does not aggregate them in the readiness baseline |
| Per-tenant observability not surfaced | The chain status SSOT is queryable per tenant by composing the SSOT read with tenant scope, but no tenant-facing dashboard exists |
| Distributed tracing absent | No correlation across service boundaries beyond the request-identifier header |
| Cost telemetry partial | bc-ai records per-invocation cost; AWS-side cost telemetry per service or per tenant aggregation is not built |
| Synthetic monitoring absent | No external probe; the platform learns about a downed service from the next request that fails |
| `tenant.tenant_migrations` audit table queued | Per-tenant migration application audit row is planned but not wired (recorded in Upgrade and Migration's drift inventory) |

**Governing source.** Audit and Activity Logging; Infrastructure.

## Boundary with Other Operations Chapters

| Chapter | Relationship |
|---|---|
| Tenant Lifecycle and Subscription | Owns the Subscription artifact; this chapter consumes the lifecycle state for per-tenant observability when wired |
| Deployment Topology | Owns the deploy-time provisioning of CloudWatch log groups and HTTP API access logs |
| Security Operations | Owns the security-relevant emission points; this chapter records the substrate they emit through |
| Upgrade and Migration | Owns the migration-event log; this chapter aggregates the migration events with other operational reads when the consolidated dashboard exists |
| Performance and Scale | Owns the performance-instrumentation that this chapter's substrate would aggregate |
| Incident and Change Management | Owns the change-record substrate; this chapter records the change events as part of the operational read surface |
| Support and Escalation | Consumes the observability surface to drive customer-side incident response |

**Governing source.** The owning Operations chapters; outline.md §4.7.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-1918d0 | Establishes the deployment and database architecture; the observability substrate runs against the database the architecture defines |
| DEC-bebaec | Establishes the chain completeness SSOT; this chapter records the SSOT as the operational read for chain status |

**Governing source.** Decisions: ADR Registry.

## References

- The Authority Model
- Audit and Activity Logging
- Infrastructure
- Backend Services
- Chain Completeness and Verdict
- Metric Evaluation
- Metric Catalog
- AI Trust and Verification
- AI Usage Visibility
- Tenant Lifecycle and Subscription
- Deployment Topology
- Security Operations
- Upgrade and Migration
- Performance and Scale
- Incident and Change Management
- Support and Escalation
- DEC-1918d0: Deployment and database architecture
- DEC-bebaec: Chain Completeness SSOT
- `bc-core/src/health/health.controller.ts`
- `bc-core/src/audit/audit.service.ts`
- `bc-core/src/registry/connection.controller.ts`
- CLAUDE.md (Coding Standards; Chain Completeness SSOT sections)
- outline.md §4.7: Operations




