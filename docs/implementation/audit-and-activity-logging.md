---
id: audit-and-activity-logging
order: 25
title: "Audit and Activity Logging"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-authority-model, operating-model-overview, evidence-and-lineage, architecture, backend-services, internal-modules, infrastructure, api-surface, notifications-and-webhooks]
governing_sources:
  - Foundation
  - The Authority Model
  - Operating Model
  - Evidence and Lineage
  - Architecture
  - Backend Services
  - Internal Modules
  - Infrastructure
  - API Surface
  - Notifications and Webhooks
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; this chapter exists in the reshaped Implementation section)
  - DEC-3395bc (v3 documentation structure; bc-core JWT-guarded /api/docs/* and the structured access log)
  - DEC-ebf0b4 (D268 Session Discipline and Data Integrity; ten rules including Rule 7 self-audit at session close)
  - DEC-804874 (D366 L-node semantic gate; session close consults verdict and persists override rationale)
  - DEC-ee6018 (bc-qa standalone repo; QA audit emissions land in DevHub)
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules including FK and soft-delete shape)
  - DEC-771baf (Tenant database topology; platform-tenant one-way dependency; per-tenant audit tables live tenant-side)
  - DEC-623f8f (D370 ADR Hygiene Policy; commit message convention names governing decision via D-codes and `closes:` tokens)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Audit and Activity Logging

## Scope

This chapter records the platform's operational audit and activity logging surface in its as-built state at the time of writing: the durable record of who did what when across DevHub, bc-core, bc-ai, and bc-qa, plus the external substrates the platform borrows (git, CloudWatch) and the surfaces it does not yet consume (Cognito audit trail, AWS CloudTrail, external observability). The chapter records reality and the gaps; it describes the two stable substrates (DevHub and bc-ai), the slim bc-core surface, and the absent integration surfaces explicitly per pattern 69.

This chapter sits between Notifications and Webhooks and Synthetic Data and Testing. Notifications and Webhooks records how selected facts surface to humans or external systems; this chapter records the durable preservation of those facts as governance state. The relation between this chapter and Evidence and Lineage in Operating Model is the central scoping line: Evidence and Lineage owns the runtime proof chain bound to the four governed boundary acts (Source Object admission, Canonical Object evaluation, Metric Snapshot evaluation, Action Object evaluation); Audit and Activity Logging owns the operational governance trail (who opened a session, who saved a plan, who pushed a commit, which gate verdict landed, which override rationale was supplied, which non-conformance was raised, which housekeeping run found which staleness). Same platform, two distinct authorities, two distinct consumers: auditors and operators read the operational trail; runtime decisions and external attestations read the proof chain.

This chapter does not redefine Foundation invariants, the Authority Model, or the Architecture chapter's commitments. It does not enumerate the runtime proof emission acts (deferred to Evidence and Lineage; the four boundary acts in Operating Model own the proof commitment), the per-event audit retention policy (deferred to Operations: Security Operations when drafted), the per-control SOC 2 or ISO 27001 conformance mapping (deferred to Compliance: ISO 27001 Conformance and Compliance: SOC 2 Conformance when drafted), the AI gate verdict authoring contract (deferred to AI Gates when drafted), the surfacing of audit events to humans through notification channels (deferred to Notifications and Webhooks), the per-table column inventory of every audit-bearing table (deferred to the Data Dictionary reference, which generates from live PostgreSQL state), or the gate-by-gate definition of what each governed gate evaluates (deferred to Quality Gates and Chain Integrity).

**Governing source.** Architecture; Backend Services; Internal Modules; outline.md §4.3.

## The Two Logging Surfaces

The platform maintains two distinct logging substrates with non-overlapping authority.

| Surface | Owner | Consumer | What it records | Lock |
|---|---|---|---|---|
| Runtime proof chain | Operating Model: Evidence and Lineage | Runtime decisions; external auditor attestation | The boundary-act emissions producing authoritative runtime objects (SO, CO, MS, AO) plus their Evidence and Lineage rows | Locked by the four boundary acts and the contract grammar |
| Operational governance trail | This chapter | Operators, governance reviewers, internal audit | Sessions, plans, change records, gate overrides, code-quality audits, decision-state snapshots, AI auditor verdicts, housekeeping run results, NC register entries | Discipline-level (D268, D366) plus ISO 27001 framing |

The chapter that follows describes the second surface. The first surface is named here only to fix the boundary; its mechanics are owned by Evidence and Lineage.

A row written to either surface does not duplicate to the other. The runtime proof chain proves that a Metric Snapshot was emitted under a bound Metric Contract version against a Canonical Object whose Evidence is preserved. The operational governance trail proves that a session was opened to draft the contract that the runtime then bound, that the gate that admitted the contract recorded its verdict, that the change record paired the plan with the report at session close, and that the self-audit was honest. The two surfaces are complementary. A platform with only the proof chain has no governance trail; a platform with only the governance trail has no runtime proof.

**Governing source.** Evidence and Lineage; The Authority Model.

## DevHub: The Operational Governance Substrate

DevHub is the platform's primary operational governance substrate. It runs as a standalone Node.js plus better-sqlite3 plus EJS service per Backend Services and persists DevHub-governed events to a single SQLite database at `data/devhub.db`. The substrate is canonical for sessions, plans, change records, DevHub audit families, and lifecycle transitions that DevHub owns; it is not the substrate for bc-ai-local gate evidence, pre-commit failures, or git history.

The substrate has five clusters of audit-bearing tables. Each cluster is named by its authoritative role.

| Cluster | Tables | Authoritative role |
|---|---|---|
| Event stream | `activity` | Append-only event log of every governance event, written by the routes that perform the governed act |
| Change records | `change_records` | ISO 27001 plan-and-report pair per session or task, written at work start (plan side) and at work close (report side) |
| Audit families | `process_audit`, `process_audit_finding`, `qa_audit_runs`, `qa_nc_records`, `adr_audit_snapshot`, `adr_orphan_triage` | Structured audit verdicts per audit type with explicit finding rows |
| Session trail | `sessions`, `session_checkpoints` | Per-session lifecycle plus crash-recovery checkpoints; D366 L-node gate is consulted at close; D268 self-audit is persisted via change_records |
| Lifecycle implicit | `tasks`, `decisions`, `risks`, `plans` | Current-state lifecycle records with `created_ts`, `updated_ts`, `actor_name`; implicit history via timestamps; no fine-grained per-transition log |

Each cluster has writers (the API routes and MCP tools that append rows), readers (the API endpoints, MCP tools, and the EJS UI that surface the rows), and retention behavior (no retention policy is active across the clusters; rows accumulate indefinitely). The cluster table above is the chapter's authoritative summary; the per-table column shape is the Data Dictionary reference's responsibility and is not enumerated here per pattern 74.

**Governing source.** Backend Services; `barecount-devhub/src/db.js`.

### Event Stream

The `activity` table is the platform's append-only event log. Every governance event the platform performs writes a row through one of two writer paths: the explicit `POST /api/activity` endpoint that any caller may use, or a `logActivity()` helper invoked from the route handlers that perform a governed act (session open, session plan, session checkpoint, session close, change record save, QA audit run, QA non-conformance state change). The vocabulary of `activity_type` values is informal and free-form; observed values include `session_start`, `session_plan`, `session_checkpoint`, `session_end`, `change_record_plan_json`, `change_record_report_json`, `qa_audit`, `qa_nc_raised`, `qa_nc_resolved`, `qa_nc_waived`, `qa_nc_accepted`, `qa_nc_updated`, and `task_created`. The MCP tool `devhub_activity_log` is the read-only surface; no UI consumer exists at the time of writing.

Retention is unbounded. No prune or archive code exists; every row written to `activity` since DevHub's first session in February 2026 is still present. The chapter records this as a drift item; the eventual policy is owned by Operations.

**Governing source.** `barecount-devhub/src/routes/activity.js`; `barecount-devhub/src/routes/projects.js`; `barecount-devhub/src/routes/qa.js`; `barecount-devhub/src/mcp-server.js`.

### Change Records (ISO 27001 Plan-and-Report Pair)

The `change_records` table is the platform's ISO 27001 change management substrate. Every session and every implementation task carries a single change record keyed by the session UID or task UID; the record holds two JSON columns:

| Column | Filled when | What it carries |
|---|---|---|
| `plan_json` | Work starts: session plan saved or task transitions to `wip` | Objective, approach, files affected, risks, rollback strategy |
| `report_json` | Work closes: session closed or task completed | Summary text, files actually changed, commit hashes, verification description, decisions made, risks identified, follow-up tasks, incidents, rollback path; plus `discipline_audit` carrying the D268 self-audit if supplied |

The plan side is auto-wired. `devhub_session_save_plan` calls the change-record write path internally; the founder does not invoke `devhub_change_record_save` separately. The report side is invoked at close: the founder fills the report or `devhub_session_close` writes a minimal report when the founder supplies `self_audit_json` (the audit lands at `report_json.discipline_audit`).

The pair maps to ISO 27001 controls A.12 (Operations Security; planned activity) and A.14 (System Acquisition, Development, and Maintenance; monitoring and review). The pairing is explicit in code comments at `barecount-devhub/src/db.js` and in the MCP tool description for `devhub_change_record_save`. No formal ISO control mapping document exists at the time of writing; the framing is operational, not certification-grade.

The plan-side write is governance-mandatory per CLAUDE.md session protocol step 4 ("This step is mandatory. Do not start coding until the plan is saved to DevHub"). The report-side write is mandatory per CLAUDE.md step 6. The founder may extend the report through follow-up `devhub_change_record_save` calls between plan and report.

**Governing source.** `barecount-devhub/src/routes/change-records.js`; `barecount-devhub/src/db.js`; CLAUDE.md.

### Audit Families

DevHub stores structured verdicts for three distinct audit types. Each type has its own table for verdicts and (for the structured types) a finding-row table.

| Audit type | Verdict table | Finding table | Source of verdicts | Reader |
|---|---|---|---|---|
| Session governance audit | `process_audit` | `process_audit_finding` | bc-ai Gemini-based session governance auditor; POST `/api/process-audits` from `bc-ai/app/auditor/reporter.py` | `devhub_process_audit_list`, `devhub_process_audit_get` |
| QA audit (code quality) | `qa_audit_runs` | `qa_nc_records` (auto-created from findings) | bc-qa shell-based audit runner; MCP tool `devhub_qa_audit` invokes `audit-repo.sh` and parses ESLint + custom-check output | `GET /api/qa/audits/:uid/report`, MCP read tools |
| ADR audit | `adr_audit_snapshot` | `adr_orphan_triage` (per-decision triage decisions) | External `legacy-v2/scripts/adr-audit.js` runner (local CLI or GitHub Actions cron) pushing via MCP `devhub_adr_audit_save` | `devhub_adr_audit_history`, `devhub_adr_orphan_triage_list` |

The session governance audit is advisory at the time of writing. A `fail` verdict from bc-ai's auditor records into `process_audit` but does not block session close; only the D366 L-node gate is the hard close-blocker. The QA audit is also advisory; non-conformances are auto-created with `nc_status: 'open'` and follow a triage workflow (open then investigating then resolved or waived or accepted) but the audit run itself does not block any platform operation. The ADR audit is purely diagnostic; it produces a snapshot per run with denormalized counts (`decided_count`, `implemented_count`, `superseded_count`, `proposed_count`, `supersession_issues`, `stuck_proposed`, `dcode_duplicates`) and a full payload, plus the orphan triage table for decisions that do not resolve cleanly under the D370 ADR Hygiene Policy.

**Governing source.** `barecount-devhub/src/routes/process-audits.js`; `barecount-devhub/src/routes/qa.js`; `barecount-devhub/src/routes/adr.js`; `legacy-v2/scripts/adr-audit.js`.

### Session Trail

The `sessions` table holds the per-session lifecycle record: started timestamp, ended timestamp, branch, plan text, summary at end, state at end, next steps, actor name. The `session_checkpoints` table holds the crash-recovery substrate: per-session sequenced checkpoints with summary text and remaining text and one of three checkpoint statuses (`in-progress`, `blocked`, `pivoted`). Checkpoints are auto-numbered per session; the writer is the MCP tool `devhub_session_checkpoint`.

Two governance gates land in the session trail.

The D268 self-audit (Rule 7) is persisted at session close when supplied. The persistence path is not a column on `sessions`; it is a key on `change_records.report_json` named `discipline_audit`. `devhub_session_close` accepts an optional `self_audit_json` argument and routes it through `devhub_change_record_save` with `report_json.discipline_audit` set only when the caller supplies the audit. The tool description explicitly states "omission is treated as honest absence, not a fake clean report"; absence is therefore represented by the missing key rather than by a fabricated clean report.

The D366 L-node semantic gate is enforced at session close. `devhub_session_close` consults `contract.l_node_semantic_verdict` rows on bc-core's platform database whose `computedAt` falls within the session's window; if any verdict reached `red` during the session, close is blocked unless `self_audit_json.l_node_override` is supplied with a rationale of at least 40 characters. On override, a follow-up task tagged `l-node-regression` is auto-spawned with the merit-class list and the break reasons; the override rationale itself is recorded in the change record. The gate fails open when bc-core, Cognito, or the audit endpoint is unreachable, so infrastructure outage does not block session close.

**Governing source.** `barecount-devhub/src/mcp-server.js`; `barecount-devhub/src/routes/projects.js`; ADR DEC-ebf0b4 (D268); ADR DEC-804874 (D366).

### Lifecycle With Implicit Audit

Tasks, decisions, risks, and plans carry their current state plus `created_ts` and `updated_ts` timestamps. State transitions (a task moving `parked` then `planned` then `wip` then `completed`; a decision moving `proposed` then `decided` then `implemented`; a risk moving `identified` then `assessed` then `mitigated` or `accepted`) update `updated_ts` and the relevant status column in place. There is no per-transition history table; a caller cannot reconstruct the timeline of a task's priority changes or a decision's status path from DevHub alone.

The implicit-audit shape is recorded as a drift item. The discipline reasoning (every transition timestamped via `updated_ts` plus actor recorded via `actor_name` plus session linkage via `plan_uid` or `session_id` backlinks) provides enough operational forensic detail for most cases; a platform-wide audit obligation that requires per-transition reconstruction would need a dedicated event log per table.

**Governing source.** `barecount-devhub/src/db.js`.

## bc-core: Operational Audit Logging

bc-core's operational audit surface is slim relative to DevHub's. The chapter records the as-built state honestly: schema is in place; one structured-output surface is wired (the docs access log per DEC-3395bc); the general mutation audit service exists as code but has no callers; the authentication trail relies entirely on Cognito's external substrate.

### Request Correlation

`RequestIdMiddleware` accepts an inbound `x-request-id` header or generates a UUID per request, stores it in continuation-local storage, and echoes it on the response header. The middleware runs globally and gives every audit-bearing log line and every persisted audit row a stable correlation token. Request correlation is the substrate that any future operational audit emission must carry.

**Governing source.** `bc-core/src/common/middleware/request-id.middleware.ts`.

### Structured Documentation Access Log

Docs access auditing is **conditional**, not universal: only successful manifest/file/asset lookups create `docs.access` rows (or `docs.access` JSONL stdout lines). Pre-handler failures (path-not-found, asset-not-found, manifest-not-found) and rate-limit 429 rejections emit warning logs and do **not** produce `docs.access` rows. This narrowing is canonical in Security Operations and is reflected in the chapter's Drift Inventory below.

The bc-admin embedded reader fetches manifest, markdown, and assets from bc-core's JWT-guarded `/api/docs/manifest`, `/api/docs/file/*splat`, and `/api/docs/asset/*splat` endpoints per DEC-3395bc. Successful controller responses emit a structured JSON log line through `DocsController.audit()` to the NestJS logger, which writes to stdout for CloudWatch pickup. The log line carries `type: 'docs.access'`, the first eight characters of the Cognito subject, the email address, the access type (`manifest`, `file`, or `asset`), the request path, the response status, the response byte count, the user agent, the IP address, and the ISO timestamp. A second governance mechanism (markdown watermarking) appends a per-request markdown comment to successful file responses naming the email and timestamp and the session subject prefix.

The access log is dual-written in the v4 baseline: the structured JSON line goes to stdout for CloudWatch pickup (the original mechanism), and a fire-and-forget audit row lands in `operations.audit_log` per the general mutation audit section below (wired in bc-core commit `1570555`). The DocsController source comment about a future `platform.docs_access_log` schema is superseded by the general `operations.audit_log` re-use; the row carries `action_code` in `{docs.manifest, docs.file, docs.asset}` plus the same field set as the JSONL line. Per DEC-3395bc the per-subject rate limits are enforced by `DocsRateLimiterInterceptor`; rate-limit rejections are emitted as warning logs, not as `docs.access` JSON lines and not as audit rows. Non-200 access logging is therefore a current-state gap on both surfaces.

**Governing source.** `bc-core/src/docs/docs.controller.ts`; `bc-core/src/docs/docs.service.ts`; DEC-3395bc.

### General Mutation Audit (One Caller)

bc-core declares an `AuditService` at `src/audit/audit.service.ts` and exports it through a `@Global()` `AuditModule`. The service exposes an `append()` method that writes to `operations.audit_log` with a request-id correlation, an action code, an entity type and identifier, a tenant identifier, an actor identifier, and a JSON detail blob. The schema column shape is in place: the platform-side `operations.audit_log` and `operations.activity_log` tables and the tenant-side `admin.activity_log` table all carry the right columns and indexes.

The service has one caller at the time of writing: `DocsController.audit()` (per the structured documentation access log section above). Every successful docs access writes a row to `operations.audit_log` with `action_code` in `{docs.manifest, docs.file, docs.asset}` alongside the structured-stdout JSONL line. The wiring is fire-and-forget with a warning-log fallback so that audit-write failures do not block or fail the docs response.

No other controller, repository, interceptor, or service in bc-core invokes `auditService.append()`. The general-mutation-audit pattern (a global interceptor that runs after every authenticated mutation) is plausible but no decision authorizes that shape; the broader rollout is queued for a future ADR. `admin.activity_log` on the tenant side has no caller and remains empty at runtime.

**Governing source.** `bc-core/src/audit/audit.service.ts`; `bc-core/src/audit/audit.module.ts`; `bc-core/docker/redesign/02-platform-tables/07-operations.sql`; `bc-core/docker/redesign/03-tenant-db.sql`.

### Authentication Trail

bc-core does not maintain its own login or logout audit trail. The `JwtAuthGuard` validates Cognito-issued tokens against the JWKS URL provisioned by AuthStack and stores no row on validation. The `ScopeGuard` and `RolesGuard` enforce per-route scope and role and store no row on enforcement. The `AuthController` exposes only `GET /api/auth/me`; there is no login route, no logout route, and no token-renewal route on bc-core. Cognito itself owns the IdP-side audit trail (sign-in events, password resets, admin actions) and stores them in the AWS account; the platform does not consume Cognito's audit trail surface (no calls to `cognito-idp:AdminListUsers`, no calls to CloudTrail's `LookupEvents`).

The tenant-side `admin.users.last_login_at` column exists in the tenant database schema but is never updated by any code path. A future hook that updates it on a successful authenticated request is plausible; the current state is that the column is dead schema.

**Governing source.** `bc-core/src/auth/auth.service.ts`; `bc-core/src/auth/guards/jwt-auth.guard.ts`; `bc-core/src/auth/guards/scope.guard.ts`; `bc-core/docker/redesign/03-tenant-db.sql`.

### Boot, Shutdown, Error

The bc-core bootstrap path logs application start to the NestJS logger, registers `process.on('unhandledRejection')` and `process.on('uncaughtException')` handlers that log the error and exit with status 1, and enables NestJS shutdown hooks. The startup logger writes the resolved port, the resolved environment, and the API and health and Swagger URLs. No persistent audit row is written for application start, application stop, module initialization, or unhandled error. The boot-shutdown trail is stdout only; CloudWatch retention is the only preservation surface.

**Governing source.** `bc-core/src/main.ts`.

## bc-ai: Housekeeping and Verification Audit

bc-ai is a Python plus FastAPI plus uvicorn service. It carries two distinct audit surfaces: a housekeeping run record (durable in bc-ai's local SQLite plus pushed to DevHub via REST) and a maker-checker-gate verdict trail (durable in bc-ai's local SQLite, not pushed to DevHub). The session governance auditor described in the previous DevHub section is bc-ai's third surface, the only one that posts directly to DevHub's audit family substrate.

### Housekeeping Run Record

bc-ai runs eight housekeeping agents (DocStaleness, SessionHygiene, TaskTriage, NcAging, RegistryRefresh, RiskReview, QaPatrol, MkDocsMaintainer). Each agent produces a `HousekeepingReport` with findings and actions; the report is written to bc-ai's local SQLite under `housekeeping_run` (run metadata) and `housekeeping_finding` (per-finding rows) by `app/housekeeping/persistence.py:save_report()`. The SQLite store is the durable record; the DevHub push is REST-mediated through `app/housekeeping/client.py` and lands in DevHub through the standard project, session, task, and document endpoints. The QA housekeeping action posts to singular `/api/qa/audit`, while DevHub exposes `/api/qa/audits` for recording and `/api/qa/audits/run` for triggering; the mismatch is recorded as drift.

The housekeeping scheduler in `app/housekeeping/scheduler.py` is disabled at the time of writing. Per a code note dated to D269, scheduling has migrated to Claude Code scheduled tasks; the scheduler module remains in the repository but does not run in the active deployment. The housekeeping agents continue to be invokable on demand through bc-ai's MCP surface.

**Governing source.** `bc-ai/app/housekeeping/persistence.py`; `bc-ai/app/housekeeping/client.py`; `bc-ai/app/housekeeping/__init__.py`; `bc-ai/app/db/schema.sql`.

### Maker-Checker-Gate Verdict Trail

bc-ai runs twelve maker-checker-gate triplets (`bf-dedup`, `bf-pii-classify`, `bo-suggest`, `bo-dedup`, `field-map`, `metric-trace`, `eval-advise`, `cc-field-audit`, `chain-audit`, `table-verify`, `source-verify`, `metric-verify`). Each triplet produces a maker output, a checker output, and a gate verdict; the trio is persisted to bc-ai's local SQLite `evidence` table per `app/db/schema.sql`. The evidence table records `maker_output`, `checker_output`, `gate_output`, `combined_confidence`, and routing in `{green, amber, red}`.

The verdict trail is bc-ai-local. It is not pushed to DevHub. Callers that consume bc-ai through the MCP surface receive the verdict inline in the response; the durable record lives in bc-ai's SQLite store. A future expansion that posts gate verdicts to DevHub is plausible (it would land in `process_audit_finding` or in a dedicated AI gate verdict table) but no decision authorizes it. The chapter records this as a drift item.

**Governing source.** `bc-ai/app/db/schema.sql`; `bc-ai/app/agents/`.

## bc-qa: Code-Quality Audit Emissions

bc-qa is a standalone repository per DEC-ee6018. It runs shell-based audits against any of the platform repositories and emits findings to two stores: a local non-conformance register (`audits/nc-register.json`) and the DevHub QA audit substrate (`qa_audit_runs` and `qa_nc_records`).

The audit driver is `audits/audit-repo.sh`, which invokes a set of check scripts under `audits/checks/check-*.sh`. The gate configuration at `gates/gate-config.json` declares per-check severity (block, warn, skip) and per-repo overrides per the bc-qa severity matrix. The driver writes audit output to console and optionally to a timestamped report file under `audits/reports/`. The DevHub integration runs through the MCP tool `devhub_qa_audit` in `barecount-devhub/src/mcp-server.js`, which invokes the shell script, parses the result, and posts to `POST /api/qa/audits` to create the audit run row plus the auto-created NC rows.

The non-conformance register at `audits/nc-register.json` is a single JSON file at the repository root maintained by `audits/nc-manage.sh`. Each NC carries `nc_id`, `raised_at`, `repo`, `check`, `severity`, `finding`, `file`, `line`, `status` in `{open, investigating, resolved, accepted, waived}`, `resolved_at`, `resolution_type` in `{fixed, waived, false-positive, deferred}`, `waiver_reason`, `session_ref`, and `commit_ref`. The register is the human-facing surface; the DevHub `qa_nc_records` table is the platform-wide aggregated surface. The two are not bidirectionally synchronized at the time of writing; the chapter records this as a drift item.

**Governing source.** `bc-qa/audits/audit-repo.sh`; `bc-qa/audits/nc-register.json`; `bc-qa/audits/nc-manage.sh`; `bc-qa/gates/gate-config.json`; DEC-ee6018.

## Pre-Commit Hooks and Git as Audit Substrate

Pre-commit hooks installed by `bc-qa/hooks/install-hooks.sh` run code-quality checks against the files in the git index (ESLint for TypeScript, ruff for Python, plus `@ts-ignore` and `eval()` and `console.log` rejections per the QA shift-left rules in CLAUDE.md). The hooks are pure validators. A failed check blocks the commit by exiting non-zero and prints the violation to console; a passing check exits zero silently. No durable audit record is emitted for either a pass or a fail. A reviewer cannot ask DevHub "which pre-commit checks ran on which commit" because the data does not exist; the only audit substrate for pre-commit hook activity is the absence or presence of a successful commit.

Git itself is the platform's immutable audit substrate for code change. The platform's commit message convention names the governing decision (D-codes such as D366 or D268, plus `closes: DEC-xxxxxx` tokens per the D370 ADR Hygiene Policy) and the implementing session as part of the commit message. Commit hashes are passed by the founder or by Claude Code into bc-ai's session-audit payload (`AuditPayload.commits`) so that the session governance auditor can correlate a session's claimed work with the actual git diff. Git is therefore an audit substrate the platform borrows by reference; it is not an audit substrate the platform consumes programmatically. No code in bc-core, bc-ai, bc-qa, or DevHub parses `git log` automatically. A future automation that walks the commit graph to verify ADR-`closes` tokens is plausible (the D370 hygiene policy anticipates a post-merge hook); no implementation exists at the time of writing.

**Governing source.** `bc-qa/hooks/install-hooks.sh`; `bc-core/.git/hooks/pre-commit`; `bc-ai/app/auditor/models.py`; ADR DEC-623f8f (D370 ADR Hygiene Policy).

## External Surfaces Not Yet Consumed

Three external audit surfaces exist around the platform and are not consumed by any platform code at the time of writing.

| Surface | What it offers | Why it is named here |
|---|---|---|
| Cognito audit trail | IdP-side log of sign-in events, password resets, MFA challenges, admin actions | The platform's authentication boundary lives in Cognito per Infrastructure; consuming this trail would close the bc-core authentication audit gap recorded above |
| AWS CloudTrail | Account-wide log of every AWS API call: CDK deploys, IAM role assumptions, S3 reads and writes, Bedrock model invocations | The platform runs in AWS with CloudTrail available at the account boundary; consuming this trail would surface infrastructure-side audit alongside the application-side trail |
| External observability (Sentry, Datadog, OpenTelemetry, Honeycomb) | Distributed tracing, error aggregation, performance metrics with retention and search | No `package.json` dependency or `pyproject.toml` dependency on any of these names exists at the time of writing; the platform's runtime telemetry is stdout plus CloudWatch only |

These three are named explicitly so that a reviewer or auditor reading this chapter does not read the surfaces it does describe and assume they are exhaustive. The platform does not consume external audit trails; the operational and runtime audit substrates the chapter records are the entire surface.

**Governing source.** Architecture; Infrastructure.

## ISO 27001 Framing

The change record plan-and-report pair in DevHub is the platform's primary ISO 27001 alignment surface. The pairing follows the discipline of A.12 (Operations Security) and A.14 (System Acquisition, Development, and Maintenance): planned activity is recorded before work begins, outcomes and reviews are recorded after work completes, and the pair is keyed by the work item identifier (session UID or task UID) so that the trail is reconstructible. Code comments at `barecount-devhub/src/db.js` and the MCP tool description for `devhub_change_record_save` explicitly reference ISO 27001 change management as the governing framing.

Two further audit families align with ISO controls without naming them explicitly. The QA audit family (`qa_audit_runs` plus `qa_nc_records`) is the platform's secure development life-cycle audit trail (A.14.2.1 Secure development policy plus A.14.2.5 Secure system engineering principles); its non-conformance triage workflow is the secure-coding-practice corrective action substrate. The session governance audit family (`process_audit` plus `process_audit_finding`) is the platform's session governance audit trail; bc-ai's Gemini-based auditor reviews session conduct against the SOPs CLAUDE.md declares.

The platform does not at the time of writing carry a formal ISO 27001 control mapping document. Each of the audit families is operational governance, and the framing is informal. The full conformance map is owned by Compliance: ISO 27001 Conformance when drafted; this chapter records the substrate surfaces that the conformance chapter will reference.

**Governing source.** `barecount-devhub/src/db.js`; `barecount-devhub/src/mcp-server.js`; CLAUDE.md.

## Failure Modes

| Cause | System response |
|---|---|
| DevHub unreachable mid-session | Session protocol step 4 cannot complete; the founder cannot save a plan; CLAUDE.md prescribes pausing work until DevHub is reachable. There is no offline buffer; a plan that is not saved to DevHub is not saved at all |
| `change_records` write fails on session close | `devhub_session_close` records the close in `sessions` but the report-side change record is missing; the next session's `devhub_session_boot` shows the session as closed but a reviewer reading the change record stream sees a plan without a paired report |
| D366 L-node gate computes red mid-session | Session close is blocked unless a 40-character override rationale is supplied; on override, a `l-node-regression` follow-up task is auto-spawned and the rationale is persisted to the change record |
| bc-core, Cognito, or audit endpoint unreachable when D366 gate runs | Gate fails open; close proceeds; the absence of verdict data does not block close (infrastructure failure does not become a governance failure) |
| Pre-commit hook check fails | Commit exits non-zero; no commit lands; no audit row is written; the only substrate for the failed attempt is the developer's terminal |
| bc-qa audit runner fails mid-run | Audit row is written with `verdict: 'non-compliant'` and the failed-check rows are auto-NC'd; the audit run row is the durable record of the failure |
| bc-ai session governance auditor returns `fail` verdict | Verdict is recorded in `process_audit` but session close is not blocked; the auditor is advisory at the time of writing |
| `operations.audit_log` write would fail (hypothetical) | The general mutation audit has zero callers at the time of writing; the failure mode is therefore unreachable. A future implementation that wires the audit hook must record this failure mode at that time |
| Docs access log emission fails (CloudWatch unavailable) | The structured JSON line is lost; no buffer; no retry; the access fact is not preserved |
| Session checkpoint write fails | `devhub_session_checkpoint` returns the error; the founder may retry; if retry is not possible, the recovery substrate for the in-flight session is degraded but the session itself is not invalidated |
| Activity event stream fills disk | Unbounded retention is the documented gap; eventual remediation owned by Operations |

**Governing source.** `barecount-devhub/src/`; `bc-core/src/`; CLAUDE.md.

## Drift Inventory

Per pattern 69, gaps between the design intent recorded above and the current state are surfaced explicitly.

| Gap | Severity | Detail |
|---|---|---|
| `activity` table has unbounded retention | Open | No prune or archive code exists; rows accumulate indefinitely. Eventual policy owned by Operations |
| `qa_audit_runs` and `qa_nc_records` have unbounded retention | Open | Same shape as `activity`; no archive policy at the time of writing |
| Session checkpoints have unbounded retention | Low | Per-session detail accumulates; not strictly a problem but eventual archive policy is owned by Operations |
| `tasks`, `decisions`, `risks` carry no per-transition history | Open | Implicit audit only via `updated_ts`; reconstruction of state-change timelines requires external git or session-context evidence; a per-table event log table is the eventual fix |
| bc-core `AuditService` has one caller (`DocsController`) | Low | Closed-narrowly in bc-core commit `1570555`: every successful docs access writes a row to `operations.audit_log` alongside the structured-stdout JSONL line. The broader pattern (global mutation interceptor across every authenticated POST/PATCH/PUT/DELETE) remains queued for a future ADR; other controllers and repositories still do not invoke `auditService.append()`. `admin.activity_log` is empty at runtime (no tenant-scoped caller yet) |
| bc-core `admin.users.last_login_at` is never updated | Low | Schema column exists; no code path writes it |
| Docs access log was stdout only | Closed | Closed in bc-core commit `1570555`: the access log is dual-written (structured-stdout JSONL line plus fire-and-forget row in `operations.audit_log` with `action_code` in `{docs.manifest, docs.file, docs.asset}`). The previously-anticipated `platform.docs_access_log` table is not needed; `operations.audit_log` carries the rows |
| Docs access log does not cover non-200 controller misses or rate-limit rejections as `docs.access` | Open | `DocsController.audit()` runs after successful controller handling; `DocsRateLimiterInterceptor` emits warning logs for 429s before the controller path |
| Pre-commit hooks emit no durable audit | Open | Failed checks block the commit but the failure is not preserved; no DevHub row, no audit log line |
| Cognito audit trail is not consumed | Open | The platform has no integration with Cognito's IdP-side audit; sign-in events and admin actions are not visible in any platform substrate |
| AWS CloudTrail is not consumed | Open | Infrastructure-side audit (CDK deploys, IAM assumptions, Bedrock invocations) is account-default in CloudTrail but not consumed by the platform |
| External observability is absent | Open | No Sentry, Datadog, OpenTelemetry, or Honeycomb dependency; runtime telemetry is stdout plus CloudWatch only |
| bc-ai maker-checker-gate verdict trail is not pushed to DevHub | Low | Twelve triplet types record verdicts in bc-ai SQLite only; the platform-wide audit substrate (process_audit_finding or a dedicated table) does not see them |
| bc-ai housekeeping QA push endpoint mismatch | Closed | Fixed in bc-ai commit `8ff8e44`: client URL aligned to `/api/qa/audits/run`, payload key aligned to `repo_slug` (matching DevHub's `runAuditRequest` zod schema), and response-key handling in `_format_audit_result` aligned to DevHub's response shape (`passed`/`warned`/`failed`/`nc_count`). Per pattern 82 (cross-service push verifies both ends of the API surface) |
| bc-qa NC register and DevHub `qa_nc_records` are not bidirectionally synchronized | Low | The local `nc-register.json` and the DevHub table can drift; a session that resolves an NC in one substrate is not reflected in the other automatically |
| Session governance audit verdict is advisory | Open | A `fail` verdict from bc-ai's session auditor records but does not block session close; only the D366 L-node gate is the hard close-blocker. The platform records the verdict and continues |
| Git log is not parsed automatically | Low | Commits are passed by the caller into the auditor payload; an automated walk that verifies `closes: DEC-xxxxxx` tokens against decision state is plausible but not implemented |
| ISO 27001 control mapping is informal | Open | Code comments and the MCP tool description name ISO 27001 change management; no formal control-by-control conformance map exists at the time of writing. Owned by Compliance: ISO 27001 Conformance when drafted |

**Governing source.** Architecture; Backend Services; Internal Modules; Infrastructure.

## Boundaries with Adjacent Chapters

Several adjacent chapters have surfaces that resemble audit and activity logging but are not part of this chapter's scope.

| Adjacent surface | Where it lives | Why it is not this chapter |
|---|---|---|
| Evidence and Lineage | Operating Model | Owns the runtime proof chain at the four governed boundary acts: Source Object, Canonical Object, Metric Snapshot, Action Object plus their Evidence and Lineage rows. This chapter records the operational governance trail that runs alongside but does not duplicate the runtime proof |
| Notifications and Webhooks | Implementation section | Records how selected facts are surfaced to humans or external systems. The fact's preservation is this chapter's responsibility; the surfacing is the notification chapter's responsibility |
| Quality Gates and Chain Integrity | Operating Model | Owns the gate definitions and verdict semantics. This chapter records that gate verdicts land in `process_audit_finding` and `qa_nc_records` and that the D366 L-node gate consults `contract.l_node_semantic_verdict` at session close, but the gate's authority over runtime decisions is owned by Quality Gates |
| AI Gates, AI Trust and Verification | AI section, queued | Owns the AI gate authoring contract and the maker-checker-gate triplet semantics. This chapter records that the verdict trail lands in bc-ai SQLite and (for session governance audits) in DevHub's `process_audit` table; the trust model is owned by the AI section |
| ISO 27001 Conformance, SOC 2 Conformance | Compliance section, queued | Owns the per-control mapping that demonstrates the platform's audit substrates satisfy specific certification requirements. This chapter records the substrate surfaces; the conformance chapters consume them |
| Security Operations | Operations section, queued | Owns the retention policy, the access-control review schedule, the credential rotation procedure, the audit-log review cadence. This chapter records the substrates; the operational policy on top of them is owned by Security Operations |
| Observability and Telemetry | Operations section, queued | Owns the runtime metrics surface (logs at stdout, CloudWatch pickup, future tracing). This chapter records governance audit substrates; the runtime telemetry is owned by Observability and Telemetry |

**Governing source.** Operating Model; Notifications and Webhooks; outline.md §4.

## Governing Decisions

| Decision | Title | Audit and activity logging impact |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus home | The Audit and Activity Logging chapter exists as a first-class platform-feature chapter in the reshaped Implementation section per DEC-c06f41, distinct from generic service or runtime treatment |
| DEC-3395bc | v3 documentation structure; bc-core JWT-guarded /api/docs/* and the structured access log | The docs access log is the wired structured-output audit surface in bc-core's v4 baseline; the controller emits one JSON line per request to stdout for CloudWatch pickup; rate limit and watermarking are paired governance mechanisms |
| DEC-ebf0b4 | D268 Session Discipline and Data Integrity (ten rules) | Rule 7 mandates a self-audit at every session close; the audit is persisted to `change_records.report_json.discipline_audit`. Honest absence is recorded as such, not as a clean report |
| DEC-804874 | D366 L-node semantic gate at session close | Session close consults `contract.l_node_semantic_verdict` rows on bc-core; on a red verdict, close is blocked unless an override rationale of at least 40 characters is supplied; on override, a `l-node-regression` follow-up task is auto-spawned and the rationale is persisted to the change record. The gate fails open on infrastructure outage |
| DEC-ee6018 | bc-qa standalone repo | Code-quality audit emissions land in DevHub's `qa_audit_runs` and `qa_nc_records` through the MCP tool `devhub_qa_audit`; the local `nc-register.json` substrate parallels the DevHub table |
| DEC-1918d0 | Deployment and database architecture; ten normalization rules | Governs the schema shape of every audit-bearing table; the ten rules apply to `operations.audit_log`, `admin.activity_log`, `change_records`, and the others |
| DEC-771baf | Tenant database topology; platform-tenant one-way dependency | Governs the placement of audit rows: tenant-scoped audit rows live in tenant database `admin.activity_log`; platform-scoped audit rows live in platform database `operations.audit_log`; cross-write asymmetry holds |
| DEC-623f8f | D370 ADR Hygiene Policy | Governs the commit-message convention that names the governing decision via D-codes and `closes: DEC-xxxxxx` tokens; this is the substrate the chapter records git as audit-by-reference against. The post-merge automation that consumes the tokens is anticipated by the policy but not implemented at the time of writing |

**Governing source.** The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Authority Model
- Operating Model: Overview
- Evidence and Lineage
- Architecture
- Backend Services
- Internal Modules
- Infrastructure
- API Surface
- Notifications and Webhooks
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-3395bc: v3 documentation structure; bc-core JWT-guarded /api/docs/*
- DEC-ebf0b4: Session Discipline and Data Integrity (D268)
- DEC-804874: L-node semantic gate (D366)
- DEC-ee6018: bc-qa standalone repo
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-623f8f: ADR Hygiene Policy (D370)
- outline.md §4.3: Implementation
- Decisions: ADR Registry
