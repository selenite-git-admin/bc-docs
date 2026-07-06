---
id: performance-and-scale
order: 35
title: "Performance and Scale"
status: drafting
authority: authoritative
depends_on: [the-authority-model, metric-evaluation, infrastructure, data-model-and-schema, chain-completeness-and-verdict]
governing_sources:
  - The Authority Model
  - Metric Evaluation
  - Infrastructure
governing_adrs:
  - DEC-c0290f (Metric evaluation engine; grain-aware GROUP BY; schedule-driven orchestration)
  - DEC-bebaec (Chain Completeness SSOT)
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules)
  - DEC-771baf (Tenant database topology; one tenant database per tenant)
  - DEC-35b34b (Formula-driven aggregation)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Performance and Scale

## Scope

This chapter records the performance and scale posture of the platform in the readiness baseline: the metric engine's per-CC evaluation cost, the per-tenant database isolation model that makes per-tenant scaling independent, the chain status SSOT as the read substrate for L1-L7 coverage, the metric catalog cardinality surface, the AI provider rate limits that gate batch workloads, the per-runtime AI cost cap, and the queued surfaces that scale matters demand but the platform has not yet built (load testing, capacity planning, autoscaling). It records the boundary between Performance and Scale and the runtime authority chapters that own the actual performance contract (Metric Evaluation; Canonical Evaluation). It records the as-built drift between the procedure and the platform's readiness-baseline performance state.

This chapter does not redefine the metric engine (Metric Evaluation), the canonical evaluator (Canonical Evaluation), the database architecture (Infrastructure; Data Model and Schema), or the chain completeness model (Chain Completeness and Verdict).

The chapter records what is measurable in the readiness baseline and what is queued; it does not assert performance numbers without their measurement substrate.

**Governing source.** outline.md §4.7; Metric Evaluation.

## Measured Performance Surfaces In The Readiness Baseline

| Surface | What it measures | Read source |
|---|---|---|
| Metric engine per-CC evaluation | Latency of one CC evaluation across its bound COs | bc-core engine logs; one per scheduled run |
| Metric engine per-MC evaluation | Latency of one MC formula evaluation against its bound COs | bc-core engine logs |
| Chain status snapshot | The per-MC L1-L7 state at a point in time | `contract.chain_status` SSOT; reconciled at operator request via the chain-status reconcile endpoint |
| AI invocation latency | Per-call wall-clock from boto3 invoke to response | bc-ai evidence table |
| AI invocation cost | Per-call cost estimate from token counts and per-model pricing | bc-ai evidence table |
| HTTP request latency | Per-request handling time | bc-core stdout (no aggregation in the readiness baseline) |

The platform records per-call data on each surface. Aggregation across surfaces (a performance dashboard, a per-tenant performance report, a per-MC-family latency profile) is queued; the substrate exists, the aggregation does not.

**Governing source.** Metric Evaluation; AI Architecture.

## Cardinality Inventory

This chapter does not freeze live row counts. Current cardinality belongs in database inspection, monitoring output, and Data Dictionary generation, not chapter prose.

| Surface | Live read source | Operational reading |
| --- | --- | --- |
| Platform database | `pg_catalog`, `information_schema`, and generated Data Dictionary | Use live inspection for table and row counts. |
| Tenant databases | Tenant DDL plus live tenant database inspection | Treat schema shape as design, row counts as runtime telemetry. |
| AI telemetry | bc-ai SQLite `evidence` and `budget_log` | Evidence rows track completed AI acts; budget rows track supported provider costs. |
| Documentation telemetry | Docs JSONL and CloudWatch pickup when deployed | Treat as access telemetry for successful docs controller responses, with denial gaps recorded elsewhere. |
## Per-Tenant Isolation as the Scale Model

Per DEC-1918d0 and DEC-771baf, the platform enforces a one-tenant-database-per-tenant model. Each tenant's data lives in its own PostgreSQL database (`tbc_{slug}_{env}`); the platform database (`bc_platform_dev`) holds platform-side definitions and the tenant identity registry only.

The scale consequence is that per-tenant load scales independently. A tenant with high-volume metric evaluation does not contend with another tenant for the same connection pool, the same query planner cache, or the same `vacuum` cycle. Per-tenant database creation and removal is operator-initiated; per-tenant performance characteristics are tenant-specific.

The aggregate scale (many tenants under the platform umbrella) is bounded by:

| Bound | Form |
|---|---|
| PostgreSQL per-instance database count | Practical bound on a single Postgres instance; sharding across instances is queued |
| Per-tenant connection pool sizing | bc-core's connection pool sizes for tenant DBs; current local-dev posture does not stress this |
| Cross-tenant aggregation queries | The platform DB holds tenant identity but no cross-tenant data; cross-tenant aggregation requires application-side fan-out across per-tenant connections |
| Per-tenant AI cost attribution | bc-ai records per-call cost; per-tenant aggregation is queued |

**Governing source.** Infrastructure; DEC-1918d0; DEC-771baf.

## Metric Engine Performance Posture

DEC-c0290f establishes the metric evaluation engine. The engine is grain-aware (`GROUP BY` on grain keys at the database layer, not in application memory), schedule-driven (the cron in `temporal_gate.schedule` triggers evaluation), and formula-driven (formulas own aggregation per DEC-35b34b).

Engine performance characteristics:

| Property | Form |
|---|---|
| Per-CO grain GROUP BY | Done at the database layer; the engine builds the GROUP BY clause from the MC's grain declaration |
| Per-formula evaluation | One formula evaluation per grain group; `mathjs` parser interprets the formula expression |
| Schedule cadence | Per-MC `temporal_gate.schedule.cron`; ranges from realtime to monthly per the cron preset |
| Idempotency | Per-grain-group, per-period idempotent; re-evaluation produces the same Metric Snapshot row (or supersedes it on value change) |
| Verification path | The mc-verify.mjs script (per MC Chain Integrity) re-evaluates against demo-selenite and diffs old vs new snapshot values |

The chapter does not assert per-MC latency figures. Engine benchmark data lives in CLAUDE.md memory files (e.g., the `session_metric_engine_apr12.md` file records benchmark figures at one point in time); current per-MC latency is read from the bc-core engine logs and the bc-ai evidence table when AI is involved in the evaluation.

**Governing source.** Metric Evaluation; DEC-c0290f.

## Database Performance

The platform database carries the platform schema and table set recorded in Infrastructure and Data Model and Schema; the tenant database carries the tenant schema set plus dynamic `fact.*` tables created per activated contract by `SchemaProvisionerModule`. Index discipline per the D162 ten normalization rules:

| Rule | Form |
|---|---|
| Indexes follow query patterns | The index is added in the same migration as the list endpoint it supports |
| FK constraints mandatory | Every FK reference has an explicit constraint |
| Naming per ISO 11179 | Indexes named `idx_{table}_{cols}`; FKs `fk_{table}_{ref}` |
| Soft deletes via `archived_at` | NULL = active; set = archived |
| Temporal via `effective_from`/`effective_to` | NULL `effective_to` marks the active row |

The Data Model and Schema chapter (Implementation) records the precise index inventory; this chapter records the discipline.

The dynamic `fact.*` tables are per-contract; activation of a contract creates the table at runtime via `SchemaProvisionerModule`. The performance consequence is that the per-tenant `fact.*` cardinality grows with the tenant's contract activation; per-table query plans evolve as the tenant uses the platform.

**Governing source.** Data Model and Schema; DEC-1918d0.

## AI Provider Rate Limits and Cost Caps

bc-ai operates against three model families (Bedrock Anthropic, Bedrock Nova, Bedrock Gemini, plus direct Anthropic). Each surface has its own rate limit:

| Surface | Rate-limit model |
|---|---|
| Bedrock Anthropic | Per-region, per-account TPM (tokens per minute) and RPM (requests per minute); inference profiles route across regional capacity |
| Bedrock Nova | Same per-region per-account model |
| Bedrock Gemini | Same per-region per-account model |
| Direct Anthropic SDK | Per-API-key TPM and RPM |

bc-ai's budget control is a per-runtime daily USD cap (`BUDGET_DAILY_LIMIT=10.0`) plus an alert threshold (`BUDGET_ALERT_THRESHOLD=8.0`) per `bc-ai/config.py`. The cap is enforced at invocation time; an invocation that would exceed the cap is rejected and recorded.

The Metric Registration chapter records that the platform applies a concurrency cap on AI verification (rate-limit protection); the active cap is implementation configuration, not chapter prose.

**Governing source.** AI Architecture; Bedrock and Inference Profiles; AI Trust and Verification.

## Aspirational Surfaces

| Surface | Form |
|---|---|
| Load testing | No formal load-test suite; `bc-sdg` (synthetic data generator) seeds source data shape but is not a load harness |
| Capacity planning | No documented capacity model; per-tenant scale is observed, not forecast |
| Autoscaling | No autoscaling configuration; the deployed AuthStack carries a Cognito user pool whose scaling is provider-managed; the dormant `PlatformInfraStack` Lambda has no autoscaling beyond Lambda concurrency defaults |
| Per-tenant performance budget | No SLA per tenant; no per-tenant latency guardrail enforced at the runtime |
| Cross-instance sharding | The platform-DB plus per-tenant-DB model can move per-tenant DBs across PostgreSQL instances; the orchestration is not built |
| Read replica strategy | No read replicas defined; the dormant Aurora construct supports replicas in CDK but the stack is not deployed |
| Connection pool tuning | bc-core's connection pool defaults are NestJS plus drizzle defaults; per-tenant tuning is not surfaced |

**Governing source.** Infrastructure; Backend Services.

## Failure Modes

| Cause | System response |
|---|---|
| Metric engine evaluation exceeds the per-MC time budget | The engine logs the latency; no automatic kill or backoff; an operator reviewing engine logs notices and takes action |
| AI provider rate limit hit | bc-ai retries with exponential backoff per the SDK; if persistent, the invocation fails and is recorded in the evidence table |
| AI cost cap exceeded mid-day | The daily-cap check at invocation time rejects further calls; bc-ai surfaces an alert log line; operator action required to extend or wait for the next day |
| Per-tenant database connection pool exhausted | bc-core queues incoming requests at the connection pool; queue depth growth surfaces as latency at the request layer |
| Cross-tenant aggregation requested | Application-side fan-out across per-tenant connections; latency is the sum of per-tenant query times plus aggregation time |
| Postgres `vacuum` lag | Per-table bloat surfaces as query slowdown; `autovacuum` runs per Postgres defaults; manual `VACUUM ANALYZE` is operator-initiated |

**Governing source.** Metric Evaluation; AI Architecture.

## Drift Inventory

| Drift item | Form |
|---|---|
| No load testing | The platform has no load harness; performance characterization is observational |
| No capacity model | Per-tenant capacity is observed per-tenant; aggregate capacity model is not built |
| No per-tenant performance budget | The runtime does not enforce per-tenant latency or throughput; no SLA defined |
| Per-tenant AI cost attribution queued | bc-ai records supported provider cost in `budget_log`; per-tenant aggregation is queued in AI Usage Visibility's drift inventory |
| Index inventory discipline ad-hoc | Per the D162 rule, indexes follow query patterns; the platform has audit data showing the indexes-vs-queries alignment but the audit is not run on a cadence |
| Production hardware not specified | The dormant Aurora construct configures a dev-sized instance; prod sizing is not specified; capacity-to-tenant ratio is not modeled |
| Connection pool tuning not surfaced | Defaults across bc-core and bc-ai; per-tenant or per-environment tuning is not accessible to operators in the readiness baseline |
| AWS-side cost telemetry partial | bc-ai per-call cost is recorded; AWS-side per-service or per-tenant cost aggregation is not built |

**Governing source.** Audit and Activity Logging.

## Boundary with Other Operations Chapters

| Chapter | Relationship |
|---|---|
| Tenant Lifecycle and Subscription | Owns the per-tenant subscription tier that gates per-tenant scale assumptions |
| Deployment Topology | Owns the deploy-time hardware shape; this chapter consumes it for performance characterization |
| Security Operations | Independent at the performance layer |
| Upgrade and Migration | Owns the migration-impact assessment; this chapter consumes it for query-plan and index-impact analysis |
| Observability and Telemetry | Owns the substrate this chapter reads; the consolidated performance dashboard is queued |
| Incident and Change Management | Owns the change-record substrate; performance regressions are governed change events |
| Support and Escalation | Consumes the per-tenant performance signal to drive customer-side communication when wired |

**Governing source.** The owning Operations chapters; outline.md §4.7.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-c0290f | Establishes the metric evaluation engine; per-CC and per-MC performance characteristics derive from the engine's design |
| DEC-bebaec | Establishes the chain completeness SSOT; the per-MC L1-L7 read substrate is the operational scale measure |
| DEC-1918d0 | Establishes the deployment and database architecture; the index discipline and the per-tenant database isolation are the scale-relevant rules |
| DEC-771baf | Establishes one tenant database per tenant; the per-tenant scale model |

**Governing source.** Decisions: ADR Registry.

| DEC-35b34b | Keeps chain-status reads as an operational scale surface while this chapter avoids freezing live cardinality figures. |

## References

- The Authority Model
- Metric Evaluation
- Infrastructure
- Data Model and Schema
- Chain Completeness and Verdict
- Metric Catalog
- AI Architecture
- Bedrock and Inference Profiles
- AI Trust and Verification
- AI Usage Visibility
- Tenant Lifecycle and Subscription
- Deployment Topology
- Security Operations
- Upgrade and Migration
- Observability and Telemetry
- Incident and Change Management
- Support and Escalation
- DEC-c0290f: Metric evaluation engine
- DEC-bebaec: Chain Completeness SSOT
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- `bc-ai/config.py`
- CLAUDE.md (Chain Completeness SSOT section)
- outline.md §4.7: Operations




