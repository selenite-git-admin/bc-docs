---
id: platform-refactor-program-functions-runtime
order: 45.3
title: "Function Dossiers: Runtime, Proof, Delivery and Support"
status: drafting
authority: reference
depends_on: [devhub, documentation-system, decision-and-change-procedure]
governing_sources:
  - Platform Readiness Program (the function list)
  - Vocabulary (the status words and the definition of done)
  - Documentation System
  - Decision and Change Procedure
governing_adrs:
  - DEC-3395bc (bc-docs is the single source of truth)
  - DEC-a67bae (the locked lane taxonomy; one owner per surface)
  - DEC-ce4314 (the ten onboarding lanes)
  - DEC-71c027 (Integrity Assurance as the platform thesis)
  - DEC-c220e4 (the interim rule on which metrics a tenant sees)
  - DEC-cf6d3b (the tenant activation model; tenant-to-package assignment)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Function Dossiers: Runtime, Proof, Delivery and Support

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md).

This annex holds the dossiers of eleven functions of the functional map: RT, Runtime; EV, Evidence and lineage; PV, Proof against the source; DL, Delivery to a tenant; TS, Tenant self-service; A1, Action and intervention; NT, Notifications and webhooks; PR, Privacy and retention; MD, Master data; AI, AI services; and SU, Support. Every dossier has the same eleven headings, in this order: "What it is", "How bc-docs defines it", "What it owns", "The acts it performs", "What it receives and what it hands on", "State today", "Known defects and risks", "Governing ADRs", "Chapters to fold in, rewrite or retire", "Open questions for the operator" and "What "locked" will mean here". Each repository was read on 2026-11-13 at the short sha given in the table below. Live data was read from the platform database with SELECT only; the queries are listed below and cited by letter. Tenant databases were not read, and no service was started, so nothing in this annex rests on a tenant's rows or on the running applications. A code or name such as "S4" or "L10" is a function of the main document's functional map; a ruling such as "T3" is recorded in the main document under "The rulings".

**Read on 2026-11-13, at origin/main only.**

| Repository | Short sha of origin/main |
|---|---|
| bc-core | ec72438b |
| bc-portal | 04930c8 |
| bc-admin | d37b241 |
| bc-db | c6de1c4 |
| bc-demo | 91e7e6bf |
| bc-docs | f4f5edd |
| barecount-devhub | 93cc1ea5 |

**Limits of this reading.**
- Tenant databases are not reachable through the read-only tool. Every statement about a tenant's `progression.*`, `fact.*`, `evidence.*` or `tenant_dim.*` rows rests on code or on a document, never on a count. Where that matters the dossier says so.
- Live data is the platform database `bc_platform_dev`, read with SELECT only.

**Queries run today.** Each is cited below by its letter, as "query QA (bc_platform_dev, 2026-11-13)".

| Id | SQL (one line) |
|---|---|
| QA | `select table_schema, count(*) from information_schema.tables where table_type='BASE TABLE' and table_schema not in ('pg_catalog','information_schema') group by 1` -> 22 schemas |
| QB | `select table_schema||'.'||table_name, (xpath('/row/c/text()', query_to_xml(format('select count(*) c from %I.%I', table_schema, table_name), false, true, '')))[1]::text::bigint from information_schema.tables where table_type='BASE TABLE' and table_schema in (<the schemas named>)` -> exact row count per table |
| QC | `select package_name, display_name, status_code, tier_order from pricing.package` |
| QD | `select slug, status_code, tenant_class_code from tenant.tenants` |
| QE | `select table_schema, table_name from information_schema.tables where table_name ~ 'subscription|entitlement|visibility|metric_release|portfolio'` -> no rows |
| QF | `select contract_family, is_active, count(*) from tenant.contract_binding group by 1,2` and `select (effective_to is null), count(*) from tenant.tenant_binding group by 1` |
| QG | `with last as (select distinct on (provisioning_command_id) provisioning_command_id, to_state from schema_provisioner.provisioning_command_transition order by provisioning_command_id, transitioned_at desc, attempt_seq desc) select tenant_key, contract_family_code, to_state, count(*) from schema_provisioner.provisioning_command left join last using (provisioning_command_id) group by 1,2,3` |
| QH | `select requested_by, count(*) from schema_provisioner.provisioning_command group by 1` |
| QI | `select governance_state_code, is_current, count(*) from mcf.metric_contract_version group by 1,2` |
| QJ | `select demo_world_version, metric_contract_version, comparison_outcome, created_at::date from demo.metric_proof_pin`; `select demo_world_version, period_label, independent_author, authored_at::date from demo.oracle_custody`; `select world_code, declared_at::date from demo.synthetic_world`; `select demo_world_version_code, demo_cc_version_code, live_cc_version_code, coverage_verdict_code, recorded_at::date from mcf.demoed_evidence_bridge` |
| QK | `select is_active, (archived_at is not null), (tenant_id is null), event_types from runtime.webhook_endpoint` |
| QL | `select category_code, source_code, status_code, count(*) from support.ticket group by 1,2,3`; `select min(created_at)::date, max(created_at)::date from support.ticket`; `select count(*) from support.ticket where tenant_id is not null` |
| QM | `select request_type, legal_basis_code, status_code, fields_scanned, fields_nullified, s3_objects_handled, submitted_at::date from operations.nullification_request` |
| QN | `select run_kind, status, count(*) from ai_telemetry.ai_run_ledger group by 1,2`; `select min(started_at)::date, max(started_at)::date, round(sum(actual_cost_usd)::numeric,2) from ai_telemetry.ai_run_ledger` |
| QO | `select count(*) from contract.intervention_contract`; `select count(*) from contract.intervention_contract_version` |
| QP | `select max(created_at)::date from bcf.panel_output_record`; `select max(created_at) from mcf.metric_authoring_panel_run`; `select max(created_at) from mcf.audit_contextual_panel_run` |
| QR | `select rolname from pg_roles where rolname ~ 'demo'` |
| QS | `select column_name from information_schema.columns where table_schema='pricing' and table_name='package' order by ordinal_position` |
| QT | `select database_scope, sensitivity_tier, count(*) from operations.pii_field_registry group by 1,2` |
| QU | `select to_jsonb(d)->>'fiscal_calendar_code' from master.dim_fiscal_calendar d` |

---

### RT, Runtime

**What it is.** Runtime is the set of acts that take one tenant's source data and turn it into governed values. In order, the acts are: observe the source, admit the observations as source objects, resolve canonical objects from them, evaluate metrics, and record a metric snapshot. A source object is one admitted observation; a canonical object is business meaning resolved from source objects; a metric snapshot is a metric's value for a period. Each act happens at one of four evaluation boundaries and only when it is explicitly invoked.

**How bc-docs defines it.**
- The function list: "**Runtime / metric-evaluation engine** | Execution plane — observe→admit→canonical→evaluate→snapshot→evidence" (`bc-docs:docs/implementation/platform-readiness-program.md:117 @ f4f5edd`).
- The boundaries: "The platform produces authoritative state at exactly four evaluation boundaries. Each boundary produces one class of progression object and emits Evidence and Lineage alongside. No other operation produces authoritative state." (`bc-docs:docs/foundation/the-evaluation-boundaries.md:37 @ f4f5edd`).
- The rule on reads: "Evaluation is an explicit act performed at a named boundary with a governed contract." (`bc-docs:docs/foundation/the-evaluation-boundaries.md:164 @ f4f5edd`).
- The records: vocabulary slice 2, sections S2.2 and S2.3 (`bc-docs:docs/reference/vocabulary.md:310-336 @ f4f5edd`).
- What starts an act is written in one chapter, `docs/operations/runtime-operations.md`, section "Trigger modes": "Every engine invocation carries exactly one declared trigger mode." It then separates target from as-built, for example "`event` | evaluation chained from an upstream act's completion event, version-pinned | **as-built: not an evaluation invoker**" (`bc-docs:docs/operations/runtime-operations.md:44,53 @ f4f5edd`).
- **Stale or silent.** The four boundary chapters (`admission-and-observation.md`, `canonical-evaluation.md`, `metric-evaluation.md`, `action-evaluation.md`) all carry `status: drafting`. `runtime-runbook.md` still names a tenant database `tbc_pilot1_dev` (`bc-docs:docs/operations/runtime-runbook.md:95,102 @ f4f5edd`); no tenant of that name exists (query QD). No chapter says who supplies the period for a metric evaluation, or what invokes canonical resolution after an admission.

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Module | `src/boundary` (admission, observation, canonical resolver, governed metric evaluation, campaigns, scheduler) | `bc-core:src/boundary/boundary.module.ts @ ec72438b` |
| Module | `src/progression` (progression repositories) | `bc-core:src/progression/progression.module.ts @ ec72438b` |
| Module | `src/boundary/reader-runtime` (reader execution, watermarks); shared with L7, to be split | `bc-core:src/boundary/reader-runtime/reader-runtime.service.ts @ ec72438b` |
| Route | `POST t/readers/:readerId/execute` | `bc-core:src/boundary/reader-runtime/reader-execution.controller.ts:32-37 @ ec72438b` |
| Route | `POST t/admission-runs/:runId/execute`, `/observe`, `/admit` | `bc-core:src/boundary/orchestrator.controller.ts:22-53 @ ec72438b` |
| Route | `POST t/observed-records`, `POST t/admitted-records`, `POST t/admission/validate` | `bc-core:src/boundary/observation.controller.ts:22-36 @ ec72438b`; `bc-core:src/boundary/admission.controller.ts:23-94 @ ec72438b` |
| Route | `POST t/ccv2-resolve` | `bc-core:src/boundary/ccv2-canonical-resolver.controller.ts:23-27 @ ec72438b` |
| Route | `POST t/metric-evaluation-governed` | `bc-core:src/boundary/metric-evaluation-orchestrator.controller.ts:34-38 @ ec72438b` |
| Route | `POST t/metric-evaluation-campaigns`, `GET :campaignId` | `bc-core:src/boundary/campaign-evaluation.controller.ts:63-93 @ ec72438b` |
| Route | `GET t/period-readiness`, `GET t/runtime-console/*` | `bc-core:src/boundary/period-readiness.controller.ts:45-51 @ ec72438b`; `bc-core:src/boundary/runtime-console.controller.ts:32-72 @ ec72438b` |
| Scheduled task | nightly cycle at 02:00 and weekly sweep, both off unless `BC_SCHEDULER_ENABLED=1` | `bc-core:src/boundary/runtime-scheduler.service.ts:58-91 @ ec72438b` |
| Tables (tenant database) | `progression.*`, `fact.so_*`, `fact.co_*`, `fact.ms_*` | defined in `bc-core:src/registry/seed/tenant-skeleton/0000_tenant_skeleton.sql @ ec72438b`; rows not reachable |
| Tables (platform) | `runtime.admission_run` (22 rows), `runtime.admission_run_context` (24), `execution.run_summary` (140), `execution.boundary_rollup` (170) | query QB |
| Screens | bc-admin `runtime/console`, `runtime/events` | `bc-admin:src/components/AppRouter.tsx:191-192 @ d37b241` |
| Documents | the five chapters named above, plus `the-runtime-ecosystem.md`, `the-governed-selection.md`, `fiscal-time-and-temporal-gates.md` (shared with MD) | listed under "Chapters to fold in, rewrite or retire" below |

`src/boundary` also holds proof-plane files (`demo-*`, `plane/`), the event outbox and the webhook controller. Those are shared with PV and NT, to be split.

**The acts it performs.**

| Act | Who | Trigger as built | Entry point | Reads and writes |
|---|---|---|---|---|
| Observe and admit | operator, tenant admin or the scheduler | manual call; or the nightly cycle for reader and flavor pairs named in `BC_SCHEDULE_ADMISSION_READERS` | `POST t/readers/:readerId/execute`; `runScheduledAdmissions` (`runtime-scheduler.service.ts:94-105`) | reads the source through a connection; writes `progression.admission*` and `fact.so_*` in the tenant database |
| Resolve canonical objects | a signed-in tenant-scoped user | manual call only | `POST t/ccv2-resolve` | reads the canonical contract version whose state is `active` (`bc-core:src/boundary/ccv2-canonical-resolver.service.ts:742-749 @ ec72438b`) and `fact.so_*`; writes `fact.co_*` and `progression.canonical_evaluation` |
| Evaluate one metric | a signed-in tenant-scoped user | manual call | `POST t/metric-evaluation-governed`; the caller supplies `asOfDate` and `legalEntityCode` (`metric-evaluation-orchestrator.controller.ts:21-30`) | reads the metric version with `is_current = TRUE AND governance_state_code = 'active'` (`bc-core:src/boundary/metric-spec-loader.ts:237 @ ec72438b`); writes the snapshot with its evidence |
| Evaluate a campaign (many metrics) | operator or platform admin; or the scheduler | manual; or nightly, with today's date as the period and one act per legal entity named in `BC_SCHEDULE_LEGAL_ENTITY` | `POST t/metric-evaluation-campaigns`; `runNightlyCampaign` (`runtime-scheduler.service.ts:107-139`) | scope `all` takes every version in state `active` (`bc-core:src/boundary/campaign-evaluation.service.ts:170 @ ec72438b`) |

bc-docs states the trigger modes (see above). It does not state who supplies the period, and it records that no event invokes canonical or metric evaluation.

**What it receives and what it hands on.**

| Hand-off | What passes | Defined in bc-docs | Built |
|---|---|---|---|
| In from L7, Readers and connections | the reader, flavor and connection for a source | yes (`connectors-and-readers.md`) | yes |
| In from L5 and L6 | the contract version to apply | Foundation forbids implicit references ("Implicit references are forbidden.", `bc-docs:docs/foundation/the-invariants.md:105 @ f4f5edd`); `tenancy-and-binding.md:114` says a tenant "operates against the adopted version" | code follows the globally `active` or current version; no file under `src/boundary` reads `tenant_binding` or `contract_binding` (command: `git grep -lE "tenant_binding|contract_binding|entitlement|subscription" origin/main -- src/boundary`, excluding specs and fixtures -> only `webhook-endpoint.controller.ts`) |
| In from DL, Delivery to a tenant | whether the metric is enabled for the tenant | vocabulary group 6 | only by the existence of the `fact.ms_*` table |
| Out to EV | evidence and lineage for each act | yes | yes for metric evaluation; partly for the others (see EV) |
| Out to NT | completion events | chapter says not built | built (`bc-core:src/boundary/runtime-event.service.ts:21-26 @ ec72438b`) |
| Out to TS | accepted snapshots | vocabulary section 6 | built (`t/beyond`) |
| Out to A1 | snapshots that would start an action | Foundation | not built |

**State today.**
- Works: the three engines are present and the legacy metric path was retired on 2026-09-29 (command: `git log -1 4ab0ea0b` -> "retire the legacy metric evaluation path and the action boundary (Unit R1)").
- Hard-coded: the scheduler serves one tenant and one default reader, taken from environment variables; the header comment still shows `BC_SCHEDULE_TENANT=pilot1` (`runtime-scheduler.service.ts:5-12`).
- Duplicated: four routes can start or feed an admission (`t/readers/.../execute`, `t/admission-runs/.../execute`, `t/observed-records`, `t/admitted-records`).
- Not built: evaluation chained from an event; a trigger-mode column on the run tables (`runtime-operations.md:44`).
- Live counts: 93 metric versions are current and `active` (query QI); 22 platform admission runs (query QB). Tenant snapshot counts could not be read.

**Known defects and risks.**
1. The canonical resolve route and the governed metric evaluation route carry `@TenantScoped()` and no `@Roles` (`ccv2-canonical-resolver.controller.ts:22-27`; `metric-evaluation-orchestrator.controller.ts:33-38`), and the roles guard allows a route with no roles (`bc-core:src/auth/guards/roles.guard.ts:24-27 @ ec72438b`). The resolver's header says "@PlatformOnly, platform_admin" (`ccv2-canonical-resolver.controller.ts:5`).
2. Version selection is global, against Invariant IV and against ruling T3 (citations in the hand-off table).
3. The nightly campaign passes today's date as both period start and period end (`runtime-scheduler.service.ts:125-131`).
4. The runbook's commands name a tenant that does not exist (citation above).

**Governing ADRs.**

| ADR | Summary | Status at origin/main |
|---|---|---|
| DEC-9c0da7 | Runtime doctrine: four engines, trigger modes, run lifecycle, campaigns | decided |
| DEC-01bd6b | Runtime orchestration on two axes; the target the scheduler does not yet meet | decided |
| DEC-acce2b | The canonical resolution engine | implemented |
| DEC-5ea578 | The governed metric evaluation act | implemented |
| DEC-ffbc24 | Legal entity is a runtime evaluation axis | decided |
| DEC-c4c742 | The governed selection | decided |
| DEC-3cc8a1 | Cited by `runtime-operations.md:38` as the "future authority" for the action engine | **reversed**; the citation conflicts with its status |

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/foundation/the-evaluation-boundaries.md` | keep nearly as is | firm on the four boundaries |
| `docs/operations/runtime-operations.md` | keep nearly as is | the only chapter that separates target from as-built triggers |
| `docs/operations/runtime-runbook.md` | rewrite | names a tenant that does not exist |
| `docs/operating-model/admission-and-observation.md`, `canonical-evaluation.md`, `metric-evaluation.md` | rewrite | drafting; silent on who starts the act and who supplies the period |
| `docs/operating-model/the-runtime-ecosystem.md` | keep nearly as is | short map-level chapter |

**Open questions for the operator.**
- Who supplies the period for a scheduled evaluation: the tenant's fiscal calendar, a tenant setting, or the operator?
- Is canonical resolution started by the completion of an admission, by a schedule, or only by command?
- Which roles may start canonical resolution and metric evaluation: platform operator only, or the tenant's admin as well?

**What "locked" will mean here.**
1. Each of the three acts has exactly one entry point, and a CI guard fails on a second.
2. Each act reads the contract version from the tenant's adoption record, as ruling T3 requires, and a test proves a tenant stays on its adopted version when a newer one is in force.
3. Every write route names the roles that may call it.
4. The scheduler reads its tenants, readers and periods from records, with no tenant name in an environment variable.
5. The chapter states what starts each act and who supplies the period, and the reference run gives the same numbers before and after.

---

### EV, Evidence and lineage

**What it is.** Evidence is the record that a boundary act happened, with its outcome. Lineage is the record of what that act referenced. Both are written by the act itself and are never rebuilt afterwards. Together they let an auditor confirm a value without running the act again.

**How bc-docs defines it.**
- Invariant VI: "At every evaluation boundary, the platform emits Evidence Objects and Lineage Objects that record what occurred, what was referenced, and under what conditions. These artifacts are immutable and append-only. They are never reconstructed, regenerated, or inferred from other state." (`bc-docs:docs/foundation/the-invariants.md:147 @ f4f5edd`).
- The object model: "Evidence is emitted synchronously with the evaluation that produces the authoritative object." (`bc-docs:docs/foundation/the-object-model.md:158 @ f4f5edd`).
- The governing chapter is `docs/operating-model/evidence-and-lineage.md`. It states two different durability rules: "**Metric evaluation is atomic** (DEC-48d222, D578)." and "**The other boundaries remain best-effort** per DEC-ebb3cd (D387) until their own governed units bring them to the atomic posture." (`bc-docs:docs/operating-model/evidence-and-lineage.md:37-38 @ f4f5edd`).
- **Contradiction inside bc-docs.** Foundation requires proof "in the same boundary act" (`the-evaluation-boundaries.md:59`), while the chapter accepts best-effort writes at admission and canonical evaluation. The vocabulary records the same gap as a defect: "Canonical evaluation writes no lineage object." (`bc-docs:docs/reference/vocabulary.md:366 @ f4f5edd`).
- The readiness list joins this function with chain integrity ("**Evidence, chain-integrity & audit**", `platform-readiness-program.md:118`), while the functional map gives chain integrity to L9, Chain integrity.

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Module | `src/evidence` (service, repository, archive, proof checks) | `bc-core:src/evidence/evidence.service.ts @ ec72438b` |
| Route | `t/evidence` (`POST`, `GET`, `GET verify`, `GET export`) | `bc-core:src/evidence/evidence.controller.ts:24-117 @ ec72438b` |
| Route | `t/evidence/records`, `t/lineage` (`POST`, `GET`, `GET trace/:objectId`) | `bc-core:src/evidence/evidence.controller.ts:128-213 @ ec72438b` |
| Service | S3 archive copy, off unless `BC_EVIDENCE_S3_BUCKET` is set | `bc-core:src/evidence/evidence-archive.service.ts:1-12 @ ec72438b` |
| Tables (tenant database) | `evidence.evidence_object`, `evidence.lineage_object` | named in `vocabulary.md:320-321`; rows not reachable |
| Tables (platform, demo plane) | `demo.evidence_object` (2,718 rows), `demo.lineage_object` (2,718); shared with PV, to be split | query QB |
| Module | `src/audit`, activity logging; shared with OP, to be split | `bc-core:src/audit/audit.service.ts @ ec72438b` |
| Documents | `evidence-and-lineage.md`; `audit-and-activity-logging.md` (shared with OP) | below |

**The acts it performs.** Evidence has no act of its own; it is written inside the acts of RT and PV.
- **Emit at admission.** `recordAdmissionAcceptance` is "Awaited but non-fatal — returns 'recorded' if both land, 'degraded' if either fails." (`bc-core:src/boundary/admission.service.ts:321-324 @ ec72438b`).
- **Emit at canonical resolution.** A canonical object realized through a legal-entity binding commits in one transaction; the others keep "the pre-existing best-effort path" (`bc-core:src/boundary/ccv2-canonical-resolver.service.ts:1978-1980 @ ec72438b`).
- **Emit at metric evaluation.** Atomic with the snapshot, by DEC-48d222 (chapter line 37).
- **Archive.** "Archive failures are logged and swallowed" (`evidence-archive.service.ts:10-12`).
- **Create by HTTP.** `POST t/evidence` and `POST t/lineage` accept a record from any tenant-scoped caller (`evidence.controller.ts:28-33,176`). bc-docs does not say who may call them or why they exist.

**What it receives and what it hands on.**

| Hand-off | Defined in bc-docs | Built |
|---|---|---|
| In from RT: one evidence and one lineage record per act | yes (Invariant VI) | atomic at the metric boundary; best-effort at admission and for canonical objects without a binding |
| Out to TS and the operator console: read, verify, export, trace | reads are named in the chapter | routes built; the portal calls neither (command: `git grep -nE "/t/(evidence|lineage)" origin/main -- apps/web/src`, excluding `_archived`, in bc-portal @ 04930c8 -> 0 matches) |
| Out to PV: the evidence identity a proof pin names | ADR DEC-025bfc only | built (`demo.metric_proof_pin.evidence_id`, query QJ columns) |
| Out to PR: evidence of a nullification act | `privacy-and-the-immutable-fact.md` | service present (`bc-core:src/nullification/nullification-evidence.service.ts @ ec72438b`) |

**State today.**
- Works: atomic proof at the metric boundary; hash-chained rows with a verify route.
- Not guaranteed: proof at admission and at canonical resolution for canonical objects without a binding.
- Open door: evidence can be created through an HTTP route, outside any boundary act.
- Live counts: on the demo plane, 2,718 evidence and 2,718 lineage rows (query QB). Tenant counts could not be read.

**Known defects and risks.**
1. Best-effort evidence at two boundaries contradicts Invariant VI (citations above).
2. `POST t/evidence` and `POST t/lineage` let a caller write proof records by hand; the object model lists "A consumer component synthesizes an Evidence Object post hoc" as disallowed (`the-object-model.md:167`).
3. The event outbox is "fail-open (an event failure never fails the engine act)" (`bc-core:src/boundary/runtime-event.service.ts:6-9 @ ec72438b`); that is acceptable for a notification and must not be read as evidence.
4. The archive copy is off by default; whether it is on for the served host was not checked.

**Governing ADRs.**

| ADR | Summary | Status |
|---|---|---|
| DEC-48d222 | Atomic proof for metric evaluation: no proof, no record | decided |
| DEC-ebb3cd | Best-effort evidence with a degraded marker | decided; **conflicts** with Invariant VI and is partly replaced by DEC-48d222 |
| DEC-dc5d52 | Platform-internal evidence is the sole intrinsic authority class | decided |
| DEC-793e13 | The external metric-audit exchange is retired | decided |

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/operating-model/evidence-and-lineage.md` | keep nearly as is | accurate on the two durability rules; update when the other boundaries become atomic |
| `docs/implementation/audit-and-activity-logging.md` | rewrite | activity logging belongs to OP; split from evidence |
| `docs/operations/evaluation-evidence-dbcp-application.md` | history | a record of one applied change |

**Open questions for the operator.**
- Are admission and canonical evidence brought to the atomic rule inside this program, or recorded as designed and not built?
- Are the HTTP create routes for evidence and lineage removed, or kept for a named caller?

**What "locked" will mean here.**
1. Every boundary act writes its evidence and lineage in the same transaction as its object, and a test fails when evidence is missing.
2. No route creates evidence or lineage outside a boundary act; a CI guard fails on a new one.
3. DEC-ebb3cd is marked superseded, or its remaining scope is stated in the chapter.
4. Canonical evaluation writes a lineage object, closing the vocabulary's defect 3.

---

### PV, Proof against the source

**What it is.** Proof against the source answers one question: does the value the platform produced agree with a value worked out independently from the same source data for the same period? Today this is done on the demo plane, a set of tables in the platform database (schema `demo`) that holds a frozen copy of demonstration data, an independently authored expected value (the oracle), and an immutable record of the comparison (the proof pin). An earlier tenant-side comparison tool also exists, outside main.

**How bc-docs defines it.**
- The requirement is condition 4 of "done": "That value **agrees with the expected value** worked out independently from the same source data for the same period, and the agreement is written down where it can be read again." (`bc-docs:docs/reference/vocabulary.md:241 @ f4f5edd`).
- The status word is "**validated against** *source*", and the vocabulary says of its record: "**No record yet.** It will be the append-only validation evidence record" (`bc-docs:docs/reference/vocabulary.md:128 @ f4f5edd`).
- **bc-docs has no chapter for this function.** The command `git grep -lE "demo plane|bc_demo_runtime|oracle_custody|Demoed|demoed" origin/main -- docs`, excluding ADRs, returns only `docs/governance/errata/ADR-ERR-013.md` and the errata index. The design lives in six ADRs: DEC-89db41, DEC-025bfc, DEC-b269fd, DEC-e8dd2d, DEC-3f6b1b and DEC-eb612b.
- **Contradiction.** The vocabulary reserves "validated" (the word "is additionally a Phase-C, tenant-zone word", `vocabulary.md:729`), while DEC-eb612b names a "VALIDATED claim level" for a metric version, and its records exist (query QJ).
- The functional list in the readiness chapter does not contain this function; the main document, under "The functional map", adds it.

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Schema | `demo` (36 tables) and `demo_staging` (15 tables) | query QA |
| Tables | `demo.synthetic_world` (2 rows), `demo.oracle_custody` (3), `demo.oracle_custody_ccy` (2), `demo.metric_proof_pin` (4), `demo.metric_proof_input` (2), `demo.ms_snapshot` (3), `demo.metric_evaluation` (4) | query QB |
| Tables | one canonical-object table per contract version: `demo.co_cc_das36_v3_0_0`, `v4_0_0`, `v5_0_0`, `v5_1_0`, `v5_2_0`, and `demo.co_cc_apl_v1_0_0` | query QB |
| Tables | `mcf.demoed_evidence_bridge` (2 rows), `mcf.demoed_bridge_coverage_element` (8), `mcf.demoed_bridge_residue_disposition` (2), `mcf.demoed_bridge_proof_attestation` (1) | query QB |
| Database roles | `bc_demo_runtime`, `bc_demo_loader`, `bc_demo_resolver`, `bc_demo_oracle_author`, `bc_demo_prover` | query QR |
| Migrations | bc-db `0047` to `0060`, `0064` to `0071` (demo plane, bridge, attestation) | command: `git ls-tree --name-only origin/main migrations/` in bc-db @ c6de1c4 |
| Version pins held in code | `PLANE_CC_VERSION_BINDINGS`; `PLANE_METRIC_VERSION_BINDINGS` | `bc-core:src/database/plane/plane-cc-version-binding.ts:26-35 @ ec72438b`; `bc-core:src/database/plane/plane-metric-version-binding.ts:52 @ ec72438b` |
| Commands | `demo-loader:admit`, `demo:e3-dry-eval`, `demo:commit`, `demo:oracle-author`, `demo:oracle-author-ccy` | `bc-core:package.json:21-25 @ ec72438b` |
| Commands with no npm script | `demo-resolve-cli`, `demoed-evidence-bridge-cli`, `demoed-bridge-attest-cli` | `bc-core:src/demo-resolve/demo-resolve-cli.ts @ ec72438b`; `bc-core:src/registry/mcf/demoed-bridge-attest-cli.ts @ ec72438b` |
| Routes | `POST mcf/metric-contract-versions/:mcvUid/demoed-bridge` (refuses), `POST .../residue-dispositions`, `GET .../demoed-claim` | `bc-core:src/registry/mcf/demoed-evidence-bridge.controller.ts:3-5,38-62 @ ec72438b` |
| Routes | `registry/mcf/audit-relations`, `POST t/metric-value-audit/run`; shared with L9, to be split | `bc-core:src/boundary/metric-value-audit.controller.ts:53-99 @ ec72438b` |
| Module | `src/test-bench` and schema `test_bench` (4 tables, all empty); shared with OP, to be split | query QB |
| Repository | bc-demo, the builder of the demonstration source data | `bc-demo:README.md:1-12 @ 91e7e6bf` |
| Tool outside main | the batch comparison tool of September | see "State today" |

`src/attestation` is not part of this function. It is a bounded reader of tenant databases for the operator console (`bc-core:src/attestation/attestation.service.ts:1-15 @ ec72438b`).

**The acts it performs.** Every act is a command run by a session under a recorded operator grant. None is started by an event or a schedule, and bc-docs gives no trigger for any of them.

| Act | Entry point | Reads and writes |
|---|---|---|
| Admit demonstration source rows | `npm run demo-loader:admit` | writes `demo.so_*` through `demo_staging` batches |
| Resolve canonical objects on the demo plane | `demo-resolve-cli`: "it runs the ONE canonical resolver (the same engine tenants use)" and commits through a database routine named for one contract version (`demo-resolve-cli.ts:4-6`) | writes `demo.co_*`, `demo.canonical_evaluation`, evidence and lineage |
| Author the oracle | `npm run demo:oracle-author`: "authors ONE immutable row per cell as the owns-nothing `bc_demo_oracle_author` login" (`bc-core:src/demo-oracle-author/demo-oracle-author-cli.ts:4-6 @ ec72438b`) | writes `demo.oracle_custody` |
| Emit the proof | `npm run demo:commit`: "emits ONE immutable proof act as the owns-nothing `bc_demo_prover` login" (`bc-core:src/boundary/demo-commit-cli.ts:4-5 @ ec72438b`) | writes `demo.metric_evaluation`, `demo.ms_snapshot`, `demo.metric_proof_pin` |
| Bridge the proof to a metric version | `demoed-evidence-bridge-cli`; the HTTP route refuses with `bridge_authoring_cli_only` (`demoed-evidence-bridge.controller.ts:53-56`) | writes `mcf.demoed_evidence_bridge` |
| Attest that the proof is still current | `demoed-bridge-attest-cli`: "appends ONE `current` or `not_current` attestation" (`demoed-bridge-attest-cli.ts:4-5`) | writes `mcf.demoed_bridge_proof_attestation` |
| Run declared cross-metric checks on a tenant | `POST t/metric-value-audit/run`, or the nightly cycle | reads accepted snapshots; writes verdict rows (`bc-core:src/boundary/metric-value-audit.service.ts:1-12 @ ec72438b`) |

**What it receives and what it hands on.**

| Hand-off | Defined in bc-docs | Built |
|---|---|---|
| In from L5 and L6: the contract versions a proof is pinned to | ADR DEC-3f6b1b only | built as a manifest in code, "APPEND-ONLY. Never edit an existing world's entry" (`plane-cc-version-binding.ts:25`) |
| In from RT: the engine's computed value | no chapter | built; the value reaches the proof through the commit command |
| In from bc-demo: the source data of a world | ADR DEC-ec1991 | built |
| Out to L6: a claim on the metric version (`demoed-claim`) | ADR DEC-eb612b and ADR-ERR-013 | built, read-only route |
| Out to DL: whether a metric offered to a tenant has been proven | vocabulary condition 4; no record named (reads 3 and 4 "need their records named exactly", `vocabulary.md:279`) | not built |
| Out to a tenant: agreement with that tenant's own source | vocabulary section 5 | not built |

**State today.**
- Works: two worlds are declared and four proof pins exist, all with outcome `match`, each at metric contract version `1.0.0` (query QJ). Two bridge rows exist, both with coverage verdict `partial` (query QJ).
- Hand-built per contract version: six canonical-object tables exist on the demo plane, one per contract version (query QB), and bc-db carries a separate migration per version, named for it (`0050_demo_co_v4_writepath`, `0053_demo_co_v5_writepath`, `0060_demo_rescur_co_v5_1_0`, `0069_demo_co_das36_v5_2_0_and_event_co`; the migration bodies were not opened). The tenant plane generates its tables from the contract.
- Hard-coded: the version pins and three metric contract identifiers are constants in code (`plane-metric-version-binding.ts:31-52`).
- Weak independence: the three custody rows name their author as "metric-controller (governed metric lane)" with independence tier `synthetic-fixture` (two rows) or `admitted-recompute` (one row) (query QJ). None is worked from the source system itself.
- Not on main: the comparison tool that read the source system directly. On barecount-devhub origin/main, `artifacts/coverage-arc/tool/` holds seven files and none performs a value check (command: `git ls-tree -r --name-only origin/main artifacts/coverage-arc`). The value-check files are listed only on branch `origin/claude/coverage-arc-groundwork-land` (not re-checked beyond the file listing; reported in artifacts/spine-review/REVIEW-4-planes-and-proof.md).
- Empty: `test_bench.*` (query QB).

**Known defects and risks.**
1. No bc-docs chapter defines the function; a session can learn it only from ADRs and code comments.
2. Code cites ADR DEC-1bb88e (`bc-core:src/boundary/demo-metric-contract-pin-reader.ts:22 @ ec72438b`); `docs/governance/adrs/ADR-1bb88e.md` does not exist at bc-docs origin/main.
3. The expected value is not worked from the source system, which condition 4 of "done" requires (ruling B5).
4. Each new canonical contract version needs a new migration, a new table and a new world label, each written by hand for that version (see "State today": six tables and four version-named migrations so far).
5. The word "validated" is used by DEC-eb612b for a claim the vocabulary says has no record.
6. Three of the acts have no npm script, so their invocation is known only from file headers.

**Governing ADRs.**

| ADR | Summary | Status |
|---|---|---|
| DEC-89db41 | The demo runtime plane inside the platform database | decided |
| DEC-b269fd | Adds the proof-writing login to DEC-89db41 | decided |
| DEC-025bfc | "Demoed" as a read-time projection over a preserved proof | decided |
| DEC-e8dd2d | Governed authoring of the oracle | decided |
| DEC-3f6b1b | A plane resolves its own canonical contract version | decided |
| DEC-eb612b | The bridge from a demo-plane proof to a metric version; amended by ADR-ERR-013 (adopted) | decided |
| DEC-346ae7 | Metric validation as a three-part claim | decided |
| DEC-1bb88e | Cited in code | **no file on main** |

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| (none exists) | rewrite | a new chapter, "Proving a metric against its source", is needed |
| `docs/implementation/synthetic-data-and-testing.md` | rewrite | drafting; predates the demo plane |
| `docs/operations/demo-operations.md` | rewrite | last changed 2026-08-19, before the demo plane existed |
| `docs/implementation/demo-estate-*.md` (five files) | history | records of the bc-demo build program |

**Open questions for the operator.**
- Ruling B4 (open): is proof done on the demo plane, on a platform-owned demonstration tenant using the normal route, or both?
- Ruling B5 (open): must the expected value be read from the source system, or is a re-sum of admitted rows accepted for a named tier?
- Which word names the result: "validated against (source)" as the vocabulary says, or "Demoed" as the ADRs say?
- Does a proof on demonstration data count toward "done" for a tenant, or must each tenant have its own?

**What "locked" will mean here.**
1. One chapter defines the proof, its record and its words, and the vocabulary names the record for condition 4 of "done".
2. A new contract version can be proven with no new migration and no hand-written table.
3. Version pins and worlds are records, not constants in code.
4. Each act has one command with status, check, do and verify, and a CI guard fails on a second entry point.
5. Every expected value states its independence tier, and the tier required for "done" is written in the chapter.
6. Every ADR the code cites has a file on main.

---

### DL, Delivery to a tenant

**What it is.** Delivery to a tenant is how a metric that the platform has certified reaches one tenant and is consumed there. The operator's ladder has five steps: the metric is available, the tenant is subscribed to it, it is enabled or disabled for that tenant, it is visible or hidden to the tenant's users, and it is reporting. This function also covers the package a tenant buys, the Subscription record that holds its entitlement, and how a new version of a contract reaches a tenant.

**How bc-docs defines it.**
- **The ladder** (`bc-docs:docs/reference/vocabulary.md:164-168 @ f4f5edd`), quoted from the "Plain meaning" and "True when" columns:
  - metric available: "In the platform's portfolio: any tenant could have it. It is the tenant-side word for a released metric".
  - subscribed: "The tenant's package includes the metric"; "**no record yet.** It will be the metric entitlement on the tenant's Subscription record, which is not built (ADR DEC-c220e4 sets the latest moment)."
  - enabled / disabled: "Whether the metric is **produced** for that tenant: its tables and contract bindings exist there, so it can be evaluated on the tenant's data"; "**Disabled: not built.**"
  - visible / hidden: "The tenant's admin chooses whether an enabled metric is shown to the tenant's users. It never stops production"; "**no record today, and no such choice exists today. This is new.**"
  - reporting: "The metric has at least one accepted value on the tenant's own data."
- **Section 5**, the six conditions of "done": "1. It is **certified** and **released**. 2. It is **enabled** for that tenant, by the governed onboarding act alone. 3. It is **reporting** for a stated period, by the governed evaluation act alone, with the proof that act writes. 4. That value **agrees with the expected value** worked out independently from the same source data for the same period, and the agreement is written down where it can be read again. 5. A tenant user **sees that value** in the portal, checked in the running application. 6. **No workaround was used at any step.**" (`vocabulary.md:238-243`, first sentence of each item).
- **ADR DEC-c220e4** (decided): "Every active tenant may see and evaluate every active platform metric, on its own data only." and "The metric entitlement record, with its check before metric evaluation and its check on the tenant's catalog view, must be live before either of these acts: (a) any tenant is activated for a party outside BareCount, on any source system; (b) a plan narrower than the whole catalog is sold." (`bc-docs:docs/governance/adrs/ADR-c220e4.md:45,49 @ f4f5edd`).
- **ADR DEC-cf6d3b** (decided): "A tenant is `active` **if and only if** Activation is complete, i.e. **(i)** a provisioned *and verified admin* exists for the tenant ... **and (ii)** the tenant references a **Subscription** record"; the interim subscription is "a **\"Pre Launch Exclusive\"** package denoting *all-metrics-allowed*" (`bc-docs:docs/governance/adrs/ADR-cf6d3b.md:73,67 @ f4f5edd`).
- **`docs/operations/tenant-lifecycle-and-subscription.md`** (drafting): "Subscription is a platform-scoped governance record." Metric entitlement is "The subset of platform-registered metrics the tenant may evaluate. Where a tenant has entitled a function or subfunction, metric entitlement may be expressed as full inclusion or as a named subset." (`:38,84 @ f4f5edd`).
- **`docs/operating-model/tenant-entitlement-enforcement.md`** (drafting): "Each active tenant identity references exactly one Subscription record at a time." Eight enforcement surfaces are listed, each "Not yet wired", and "The platform does not represent any of these surfaces as enforced." (`:35,126-135 @ f4f5edd`).
- **`docs/operating-model/tenancy-and-binding.md`** (drafting): "An adoption whose contract version is later superseded does not silently follow the supersession: the tenant operates against the adopted version until a new adoption is recorded." (`:114 @ f4f5edd`).
- **`docs/operating-model/source-change-classification.md`** (drafting): "Activation triggers `ContractActivationService` fanout (per DEC-95687d / D369): tenants bound to the prior version receive bindings to the new version; fact tables reconcile" and "major bumps are governance acts that surface for review; minor bumps cascade automatically." (`:119,110 @ f4f5edd`).
- **Contradictions.** (1) `tenancy-and-binding.md:114` says a tenant does not follow a new version; `source-change-classification.md:119` says it receives it. (2) The same chapter classes a changed resolution rule as minor: "Same shape, different values; CC consumers unaware" (`:85`). Ruling T3 treats any change that can affect a value as needing the tenant's acceptance. (3) The vocabulary says "A tenant's kind is not recorded, and no field is to be added for it." (`vocabulary.md:438`); the live table has `tenant.tenants.tenant_class_code` (query QD), added by `bc-db:migrations/0040_fixture_classification_and_datname_authority.sql:8-9 @ c6de1c4`. (4) The lifecycle chapter's drift inventory says of the onboarding record that "readable source did not show a durable onboarding-record table or service" (`tenant-lifecycle-and-subscription.md:229`); `tenant.onboarding_record` exists with 3 rows (query QB).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Module | `src/schema-provisioner` (metric onboarding, binding populator, provisioning commands, worker); shared with L10, to be split | `bc-core:src/schema-provisioner/metric-onboarding.service.ts @ ec72438b` |
| Route | `POST schema-provisioner/onboard-metric`, `POST schema-provisioner/onboard-connector` | `bc-core:src/schema-provisioner/connector-onboarding.controller.ts:40-61 @ ec72438b` |
| Route | `GET schema-provisioner/tenants/:tenantSlug/provisioning`; `POST .../commands/:id/reissue` | same file, lines 72-83 |
| Route | `packages` (create, list, patch, delete, provision preview); shared with S4, to be split | `bc-core:src/registry/execution/package.controller.ts:27-90 @ ec72438b` |
| Route | `registry/metric-usage` | `bc-core:src/registry/mcf/metric-usage.controller.ts:14 @ ec72438b` |
| Service | `ContractActivationService`, the fan-out of a newly active version to tenants | `bc-core:src/schema-provisioner/contract-activation.service.ts:1-21 @ ec72438b` |
| Command | `npm run provisioning:worker`, `npm run provisioning:sweep` | `bc-core:package.json:26,28 @ ec72438b` |
| Table | `pricing.package` (7 rows); shared with S4 | query QC |
| Tables | `tenant.contract_binding` (17), `tenant.tenant_binding` (28), `tenant.onboarding_record` (3) | query QB |
| Tables | `schema_provisioner.provisioning_command` (45), `provisioning_command_transition` (150) | query QB |
| Tables not built | Subscription, entitlement, release, visibility | query QE -> no rows |
| Screens | bc-admin `registry/packages`; `pricing/entitlements`, `pricing/usage`, `pricing/billing` are placeholders | `bc-admin:src/components/AppRouter.tsx:198-199,306-309 @ d37b241` |
| Screens | bc-portal `/workspace/subscription`, `/workspace/billing-payments` | `bc-portal:apps/web/src/components/AppRouter.tsx:153,155 @ 04930c8` |
| Documents | the six documents quoted above, plus `docs/onboarding/tenant-metric-binding.md` and `docs/operating-model/metric-catalog.md` | below |

**The acts it performs.**

| Act | Who | Trigger as built | Entry point | Reads and writes |
|---|---|---|---|---|
| Release a metric (make it available) | not built | none; "every certified metric is treated as released" (`vocabulary.md:129`) | none | none |
| Subscribe a tenant to a package | not built | none | none | none |
| Enable a metric for a tenant | a platform admin | a direct API call; no bc-admin caller was found (command: `git grep -n "onboard-metric" origin/main -- src` in bc-admin -> no match) | `POST schema-provisioner/onboard-metric` | walks back from the metric to its canonical and source contracts, writes bindings, and enqueues provisioning commands (`metric-onboarding.service.ts:78-124`); the worker then creates the tables |
| Disable a metric for a tenant | not built | none | none | none |
| Show or hide a metric | not built | none | none | none |
| Deliver a newly active contract version | the platform, automatically | activation of a canonical or metric contract version | `ContractActivationService` | "add the missing contract_binding, and ENQUEUE a governed provisioning command per tenant" (`contract-activation.service.ts:4-6`) |
| Maintain packages | operator or platform admin | manual | `packages` routes | `pricing.package` |

bc-docs does not say what triggers a subscription or a release, because neither act is designed to that level. For enablement, the vocabulary says the tenant's admin should start it and "That route is not built" (`vocabulary.md:166`).

**What it receives and what it hands on.**

| Hand-off | What passes | Defined in bc-docs | Built |
|---|---|---|---|
| In from L6: the offerable set | certified metric versions; later, released ones | vocabulary groups 4 and 6 | by default only: `active` and current (93 versions, query QI) |
| In from S4: the package and its metrics | the Subscription's catalog entitlement | lifecycle chapter | not built; `pricing.package` holds `reader_manifest_json` and no metric column (query QS) |
| In from S3: an active tenant with a Subscription | ADR DEC-cf6d3b | decided | not built: no Subscription table (query QE), and no row named "Pre Launch Exclusive" (query QC) |
| Out to L10: provisioning commands | `schema_provisioner.provisioning_command` | `tenant-metric-binding.md` | built |
| Out to RT: which metrics may be evaluated for the tenant, at which version | enforcement chapter; ruling T3 | "Not yet wired" | not built: evaluation reads no binding (see RT) |
| Out to TS: the tenant's list of metrics and their standing | vocabulary group 6 | defined | the list returns every current certified metric; `snapshotBacked` is the only standing shown (`bc-core:src/tenant-views/beyond-metrics.service.ts:75-79 @ ec72438b`) |

**State today.**
- Built: enablement. The current command state per tenant is: `kaveri` 17 metric commands provisioned and 1 pending; `kaveridemo` 1 provisioned; `kaveridemo2` 4 provisioned and 1 failed (query QG). Of 45 commands, 30 were requested by `metric-onboarding`, 13 by `activation` and 2 by `evaluation` (query QH).
- By default: available equals certified; subscribed equals every active tenant; visible equals everything.
- Not built: release, Subscription, entitlement checks, disable, visible or hidden.
- Mismatch: `pricing.package` has 7 rows, 5 of them `deprecated`, the other two named `custom` and `Free` (query QC). Its columns describe readers, protocols and source compatibility (query QS).
- Bindings: all 17 `tenant.contract_binding` rows are family `canonical` and active; there is no metric-family row (query QF). 27 of 28 source bindings are open (query QF).
- Tenants: `kaveri` is active with class `fixture`; `kaveridemo` and `kaveridemo2` are suspended with class `customer`; `probe_unit4` is archived (query QD).

**Known defects and risks.**
1. Nothing checks subscription, enablement or visibility before evaluation; ADR DEC-c220e4 records this as the rule in force.
2. A newly active version reaches every bound tenant automatically, with no acceptance, against ruling T3 (`contract-activation.service.ts:1-21`).
3. The writers do not enforce one active adoption per contract: "a tenant can currently hold more than one active adoption of a contract" (`tenancy-and-binding.md:104`).
4. Two tenants carry class `customer` while the vocabulary says no tenant kind is recorded; ruling T5 depends on that field.
5. Enablement has no screen and no command; it is a direct API call.
6. `McfBindingResolverService` has no caller (command: `git grep -l McfBindingResolverService origin/main -- src`, excluding specs -> only its own file).
7. The package table cannot express the decided model of ruling T1.

**Governing ADRs.**

| ADR | Summary | Status |
|---|---|---|
| DEC-c220e4 | Every active tenant gets every certified metric until the Subscription is built; the entitlement record must exist before an outside tenant | decided |
| DEC-cf6d3b | A tenant is active only with a verified admin and an assigned Subscription | decided; not built |
| DEC-4aa2fd | Metric entitlement as the one control surface | superseded by DEC-c220e4 |
| DEC-a1290e | The tenant metric list reads the metric contract store directly | decided |
| DEC-7df811 | Tenant onboarding state model; amended by DEC-cf6d3b | decided |
| DEC-f7d4fc | Source adoption in `tenant_binding`; other adoption and overrides in `contract_binding` | decided |
| DEC-95687d | Activation fan-out to tenants | implemented; **conflicts** with ruling T3 |
| DEC-324d9e | Four subscription tiers billed through Stripe | decided; not built |
| DEC-bebaec | Cited by `source-change-classification.md:120` for the 48-hour window | **superseded** |

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/reference/vocabulary.md` (groups 4 and 6, section 5) | keep nearly as is | the operator-approved definition |
| `docs/operations/tenant-lifecycle-and-subscription.md` | rewrite | sound target; its drift inventory is stale; must absorb DEC-cf6d3b and ruling T1 |
| `docs/operating-model/tenant-entitlement-enforcement.md` | keep nearly as is | honest about "Not yet wired" |
| `docs/operating-model/tenancy-and-binding.md` | rewrite | must state adoption under ruling T3 |
| `docs/operating-model/source-change-classification.md` | rewrite | minor and major rule replaced by ruling T3; cites a superseded ADR |
| `docs/onboarding/tenant-metric-binding.md` | rewrite | the procedure for enablement; last changed 2026-09-21 |
| `docs/operating-model/metric-catalog.md` | rewrite | last changed 2026-07-06, before DEC-c220e4 |

**Open questions for the operator.** Rulings T1 and T3 are decided and still leave these to settle; the first question is open ruling T6.
- T6: does a package name its metrics as a list, or by function and subfunction with full inclusion, as the lifecycle chapter allows?
- T1: is the built `pricing.package` table reshaped, or replaced by a new package record?
- T1: is "released" recorded per metric, as the vocabulary proposes, or implied by membership of any package?
- T1: when a metric sits in two packages and a tenant leaves one, does the metric stay enabled?
- T3: who classifies a change as value-affecting: the author, the certification panel, or a rule in the database?
- T3: what is the acceptance record, and which tenant role may accept?
- T3: what does a tenant see while it has not accepted, and is there a date after which the old version stops reporting?
- T3: metric contracts have one version each today (1 superseded version, query QI); does acceptance apply to a successor metric version in the same way as to a canonical version?
- T3: does the activation fan-out stop for value-affecting changes, or continue and wait at the tenant?
- Beyond T1 and T3: who enables a metric for a tenant, the platform operator or the tenant's admin (the vocabulary says the admin)?

**What "locked" will mean here.**
1. Each step of the ladder has one record and one read, and the vocabulary's "no record yet" notes are gone for the steps the thread needs.
2. One resolver answers "may this tenant run this metric, at which version", and evaluation and the tenant's list both call it.
3. A value-affecting version change does not reach a tenant without an acceptance record, proven by a test.
4. Enablement is one command with status, check, do and verify, and the direct route has no other caller.
5. A tenant holds at most one open adoption per contract, enforced by the database.
6. The six chapters above agree with each other and with rulings T1 to T3.

---

### TS, Tenant self-service

**What it is.** Tenant self-service is the customer portal, the application a tenant's own users sign in to. In it they see their metrics and values, declare their legal entities and fiscal calendars, and register connections to their source systems. The portal is the repository bc-portal; it reads and writes through tenant-scoped routes of bc-core.

**How bc-docs defines it.**
- The function list: "**Tenant self-service (bc-portal)** | The customer's face — finish onboarding, connect source, view metrics" (`bc-docs:docs/implementation/platform-readiness-program.md:119 @ f4f5edd`).
- The same row names ADR DEC-6cdceb as "current". At origin/main that ADR is `superseded`, `superseded_by: DEC-c562d5` (`bc-docs:docs/governance/adrs/ADR-6cdceb.md:5-6 @ f4f5edd`). The readiness row is stale.
- `docs/implementation/frontend-experience.md` says of itself: "The chapter is deliberately a stub. Both frontends are in flux: bc-portal carries three incomplete UI iterations under active redesign" (`:41 @ f4f5edd`).
- The vocabulary sets what a tenant may be shown: "a tenant-facing screen does not print \"subscribed\", \"visible\" or \"hidden\" against a metric" (`vocabulary.md:178`), and "Shown in the portal" "is not a status word. It is something a person checks in the running application" (`vocabulary.md:180`).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Repository | bc-portal, application `apps/web` | command: `git ls-tree --name-only origin/main` in bc-portal @ 04930c8 |
| Screens | sign-in pages; `/dashboard` and metric pages; `/workspace/*`; `/legal-entities/*`; `/support`, `/help`, `/alerts`, `/profile` | `bc-portal:apps/web/src/components/AppRouter.tsx:119-184 @ 04930c8` |
| Archived code | `apps/web/src/_archived` (171 files) | command: file count by directory at 04930c8 |
| Route | `t/beyond` (`metric-functions`, `metrics`, `metrics/:mcUid`, `metrics/:mcUid/snapshot`) | `bc-core:src/tenant-views/beyond-metrics.controller.ts:17-42 @ ec72438b` |
| Route | `t/discovery`, `t/mapping-bindings`, `t/admission-run-logs`, `t/contracts`, `t/readers-catalog`, `t/connectors-catalog`, `t/connections`, `t/tenant-bindings`, `t/metrics` | `bc-core:src/tenant-views/tenant-views.controller.ts:29-433 @ ec72438b` |
| Route | `t/context` | `bc-core:src/tenancy/tenant-context.controller.ts:16 @ ec72438b` |
| Route | `t/legal-entities`, `t/tax-registrations`; shared with MD, to be split | `bc-core:src/registry/legal-entity/legal-entity.controller.ts:34-65 @ ec72438b` |
| Documents | `frontend-experience.md`; ADR DEC-c562d5 | below |

**The acts it performs.**

| Act | Who | Entry point | Built |
|---|---|---|---|
| Sign in, with MFA and password reset | tenant user | `/login`, `/mfa-verification`, `/set-new-password` (`AppRouter.tsx:119-122`) | yes |
| View metrics and one metric's values | tenant user | `/dashboard`; `GET /api/t/beyond/metric-functions` and `/metrics` (`bc-portal:apps/web/src/api/beyond-metrics.ts:41-46 @ 04930c8`) | yes |
| Declare a legal entity and its fiscal calendar | tenant admin | `/legal-entities/declare`; `POST t/legal-entities` (`legal-entity.controller.ts:40,53`) | yes |
| Register and view connections | tenant admin | `/workspace/data/connections` (`AppRouter.tsx:156-157`) | yes |
| Enable or disable a metric; show or hide it | tenant admin, by the vocabulary | none | not built |
| Manage subscription and billing | tenant admin | `/workspace/subscription`, `/workspace/billing-payments` | pages exist; no Subscription record exists behind them (query QE) |
| Create an intervention | tenant user | `/dashboard/metrics/:metricId/interventions/new` | sample data only (see A1) |

All acts are started by a person. bc-docs names no other trigger.

**What it receives and what it hands on.**

| Hand-off | Defined in bc-docs | Built |
|---|---|---|
| In from RT: accepted snapshots per metric | vocabulary section 6 names `GET /api/t/beyond/metrics/<metric id>` | built |
| In from DL: the tenant's list and each metric's standing | vocabulary group 6 | every certified metric is listed; no standing other than `snapshotBacked` |
| In from S1: the signed-in user's tenant claim | ADR DEC-8dc51d, cited in `frontend-experience.md:23` | built |
| Out to L7: a connection to a source | `connectors-and-readers.md` | built |
| Out to MD: legal entities and fiscal calendars | ADR DEC-4aa1ff | built |
| Out to SU: a support ticket | no chapter | the page calls a platform-only route (see SU) |
| Out to DL: the admin's choice to enable or show a metric | vocabulary open point 10 | not built |

**State today.**
- Works: sign-in, the dashboard, the metric pages, legal entities, connections.
- Sample data: five files use the notice "Sample data: illustrative, not this tenant's figures", among them the two intervention pages, `DashboardMetricPage.tsx` and `MetricPlanTargetsPage.tsx` (command: `git grep -l SampleDataNotice origin/main -- apps/web/src`, excluding `_archived`).
- When a metric is not reporting, "the screen gives no reason" (`vocabulary.md:176`).
- The last commit on bc-portal origin/main is dated 2026-10-20 (command: `git log -1 --format=%cs origin/main`).
- Whether a tenant user sees a given value in the running portal was not checked today; no service was started.

**Known defects and risks.**
1. The readiness chapter names a superseded ADR as current for this function.
2. The governing chapter calls itself a stub.
3. `DashboardMetricPage.tsx` imports sample facts (`financeMetricFacts`) beside governed values (`bc-portal:apps/web/src/surfaces/dashboard/DashboardMetricPage.tsx:16-17 @ 04930c8`); a reader of the page must tell the two apart by the notice alone.
4. 171 archived files remain in the source tree.
5. The support page calls `/support/tickets`, a platform-only route (see SU).

**Governing ADRs.**

| ADR | Summary | Status |
|---|---|---|
| DEC-c562d5 | The canonical portal design: Dashboard and Workspace | decided |
| DEC-6cdceb | The earlier surface split | superseded by DEC-c562d5 |
| DEC-a1290e | The tenant metric read surface reads the metric contract store | decided |
| DEC-4aa1ff | Legal-entity declaration is a tenant-side act | decided |
| DEC-e82f0a | The portal's AI assistant drawer | implemented |

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/implementation/frontend-experience.md` | rewrite | a self-declared stub covering two applications |
| `docs/foundation/the-dual-layer-interaction-model.md` | keep nearly as is | Foundation; not opened in this task beyond the vocabulary's reference to it |
| `docs/implementation/platform-readiness-program.md` row TS | rewrite | names a superseded ADR |

**Open questions for the operator.**
- Which of the tenant admin's switches are in the program: enable, disable, show, hide, or none until delivery is built?
- What is a tenant told when a metric is not reporting: one sentence per reason, or nothing until a later slice?
- Are the sample-data pages removed until they are real, or kept with the notice?

**What "locked" will mean here.**
1. Every page shows either governed data or nothing; no page mixes sample facts with a tenant's values.
2. Every word on a metric's standing comes from the vocabulary and from a record.
3. The portal calls only tenant-scoped routes, checked by a test over its API clients.
4. The archived tree is deleted.
5. Condition 5 of "done" has a written check that a fresh session can repeat.

---

### A1, Action and intervention

**What it is.** An action object is a declared intent bound to one or more metric snapshots, with its outcome recorded. An intervention contract is the governed definition that says when an action is created and how its outcome is resolved. This is the fourth evaluation boundary and the last object in the fixed order. It is designed in Foundation and is not built.

**How bc-docs defines it.**
- "An Action Object represents a declared intent bound at creation time to one or more Metric Snapshots. It records what was decided, on what basis, and with what outcome." (`bc-docs:docs/foundation/the-object-model.md:134 @ f4f5edd`).
- "Action Objects progress to a terminal state. The platform prohibits open-ended, indefinitely pending, or retroactively closed actions." (`the-object-model.md:142`).
- The boundary: "The Intervention Contract declares activation mode, trigger conditions against one or more Metric Snapshots, assignee pool, closure window, and the evaluation model that resolves outcome against preserved snapshots." (`bc-docs:docs/foundation/the-evaluation-boundaries.md:131 @ f4f5edd`).
- The function list marks it "*(design pending)*" and "**no design yet**" (`platform-readiness-program.md:120`).
- The governing chapter, `docs/operating-model/action-evaluation.md`, carries the note "As-built: implementation absent (fail-closed)." (`:33 @ f4f5edd`). The same note names `ActionRepository.createActionObject`. No class of that name exists at bc-core origin/main (command: `git grep -n "class ActionRepository" origin/main -- src` -> no match), so the note is stale in its detail.
- The vocabulary: "**not built.** `progression.intervention_evaluation` exists with the values `triggered` and `not_triggered`, and holds no rows." (`vocabulary.md:319`).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Tables (platform) | `contract.intervention_contract`, `intervention_contract_version`, `intervention_contract_approval`; 0 contracts, 0 versions | query QO |
| Tables (tenant database) | `progression.intervention_evaluation`, `progression.intervention_run` | `bc-core:src/registry/seed/tenant-skeleton/0000_tenant_skeleton.sql:483,511 @ ec72438b` |
| Schema code | `src/database/schema/contract/intervention-contract.ts` | `bc-core @ ec72438b` |
| Repository | `InterventionEvaluationProgressionRepository` | `bc-core:src/progression/intervention-evaluation-progression.repository.ts:55 @ ec72438b` |
| Route | `GET actions/stats`, a placeholder that returns "Action stats require tenant scope" | `bc-core:src/registry/readers/reader.controller.ts:408 @ ec72438b` |
| Screens | bc-admin `registry/contracts/intervention`, `registry/contracts/action` | `bc-admin:src/components/AppRouter.tsx:174,180 @ d37b241` |
| Screens | bc-portal intervention create and detail pages, on sample data | `bc-portal:apps/web/src/components/AppRouter.tsx:133-134 @ 04930c8` |
| Documents | `action-evaluation.md` | below |

**The acts it performs.** None is built. The designed acts are action creation and outcome resolution (`action-evaluation.md:29`). The action boundary's code was removed on 2026-09-29 (command: `git log -1 4ab0ea0b` -> "retire the legacy metric evaluation path and the action boundary (Unit R1)"). bc-docs does not say what would trigger an action-creation act as built, because nothing is built.

**What it receives and what it hands on.**

| Hand-off | Defined in bc-docs | Built |
|---|---|---|
| In from RT: metric snapshots that meet a trigger condition | Foundation | no |
| In from the Authoring functions (L1 to L10): an intervention contract version | the contract grammar | tables only, no rows |
| Out to EV: evidence and lineage for creation and for outcome | Foundation | no |
| Out to NT and TS: an assigned action shown to a person | not defined | no |

**State today.**
- Not built: the evaluator, the object, its evidence.
- Present and empty: three platform tables (query QO).
- Shown as if real: the portal's intervention pages read a static file (`bc-portal:apps/web/src/surfaces/dashboard/dashboardIntervention.data.ts:1-12 @ 04930c8`) and carry the sample-data notice.

**Known defects and risks.**
1. The record that would hold an action carries `triggered` and `not_triggered`, which "do not express Foundation's lifecycle" (`vocabulary.md:367`).
2. `contract.intervention_contract_version` uses `status_code` with no rule on its values, unlike the other families (`vocabulary.md:369`).
3. `runtime-operations.md:38` names DEC-3cc8a1 as the future authority; that ADR is reversed.
4. The portal shows intervention pages for a capability that does not exist.
5. The chapter's as-built note names a class that is gone.

**Governing ADRs.**

| ADR | Summary | Status |
|---|---|---|
| DEC-615b87 | The intervention contract as the sixth contract family | implemented (tables only) |
| DEC-bae0ef | A single intervention with a numeric target | implemented (tables only) |
| DEC-3cc8a1 | AI counterparts at the intervention boundary | reversed |

No decided ADR designs the action evaluator.

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/operating-model/action-evaluation.md` | keep nearly as is | the Foundation contract; mark it "designed, not built" and correct the as-built note |

**Open questions for the operator.**
- Do the portal's intervention pages stay on sample data, or are they removed until the boundary is built?
- Are the empty intervention tables kept as the future home, or dropped until a design exists?

**What "locked" will mean here.**
1. The guide lists the function as designed, not built, with the Foundation text as its definition. The guide is the new bc-docs section `docs/guide/` that the main document describes under "bc-docs: read first, and kept true".
2. No screen presents an action as real.
3. No citation to the reversed ADR remains.
4. The empty tables and placeholder route are either named in the guide as reserved or removed.

---

### NT, Notifications and webhooks

**What it is.** Notifications and webhooks are how the platform tells someone outside an act that the act happened. A webhook is an HTTP call the platform makes to an address a recipient has registered. As built, the platform records a completion event for each runtime act, raises a support ticket from some events, and can deliver signed webhooks. It sends no email and shows no in-app notification.

**How bc-docs defines it.**
- The governing chapter is `docs/implementation/notifications-and-webhooks.md` (drafting). It says: "The platform does not send outbound notifications, expose inbound webhook receivers, or emit outbound webhooks to caller-configured URLs in the readiness baseline." (`:35 @ f4f5edd`) and "The surface is not stubbed-with-disabled-deliveries; it is structurally absent." (`:56`).
- **The chapter is wrong for webhooks.** A second chapter says the opposite: "`RuntimeEventService.emit` persists the event and drives only the boundary-ticket and webhook consumers" (`bc-docs:docs/operations/runtime-operations.md:53 @ f4f5edd`).
- The function is not in the readiness list; the main document, under "The functional map", adds it.

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Service | `RuntimeEventService`, the event outbox and its consumers | `bc-core:src/boundary/runtime-event.service.ts:1-10 @ ec72438b` |
| Route | `admin/webhook-endpoints` (`POST`, `GET`, `DELETE`), platform admin only | `bc-core:src/boundary/webhook-endpoint.controller.ts:50-75 @ ec72438b` |
| Route | `GET t/runtime-console/events`, `GET t/runtime-console/webhook-deliveries` | `bc-core:src/boundary/runtime-console.controller.ts:47,64 @ ec72438b` |
| Table (platform) | `runtime.webhook_endpoint` (3 rows) | query QB |
| Tables (tenant database) | `runtimeEvent`, `webhookDelivery` in the progression schema | `bc-core:src/boundary/runtime-event.service.ts:17 @ ec72438b`; rows not reachable |
| Tables (platform, unused) | `infrastructure.notification_log` (0 rows), `infrastructure.email_template` (0 rows) | query QB |
| Screens | bc-admin `runtime/events`; the webhook list read | `bc-admin:src/components/AppRouter.tsx:192 @ d37b241`; `bc-admin:src/api/runtime.ts:235-236 @ d37b241` |
| Screen | bc-portal `/alerts` | `bc-portal:apps/web/src/components/AppRouter.tsx:140 @ 04930c8` |
| Document | `notifications-and-webhooks.md` | below |

**The acts it performs.**

| Act | Who | Trigger as built | Entry point | Reads and writes |
|---|---|---|---|---|
| Record a completion event | the engine | the end of an admission run, a canonical resolution, a metric run, a campaign or a value audit | `runtimeEvents.emit` at `bc-core:src/boundary/reader-runtime/reader-runtime.service.ts:733`, `ccv2-canonical-resolver.service.ts:676`, `metric-evaluation-orchestrator.service.ts:160`, `campaign-evaluation.service.ts:120`, `metric-value-audit.service.ts:89` (all @ ec72438b) | writes the event row; runs the consumers |
| Raise a ticket from an event | the ticket consumer | an event that needs operator attention | `BoundaryTicketService` (`bc-core:src/boundary/boundary-ticket.service.ts:1-6 @ ec72438b`) | writes `support.ticket` (see SU) |
| Deliver a webhook | the webhook consumer | an event whose type an endpoint lists | inside `RuntimeEventService`; signed with HMAC; at most three attempts (`runtime-event.service.ts:12,35`) | reads `runtime.webhook_endpoint`; writes delivery rows |
| Register or archive an endpoint | platform admin | manual | `admin/webhook-endpoints` | `runtime.webhook_endpoint` |
| Send an email or in-app notice | not built | none | none | none |

bc-docs's notification chapter names no trigger, because it says nothing is built.

**What it receives and what it hands on.**

| Hand-off | Defined in bc-docs | Built |
|---|---|---|
| In from RT: completion events of five types | `runtime-operations.md:53` | yes (`runtime-event.service.ts:21-26`) |
| Out to SU: tickets | no chapter | yes |
| Out to a recipient's address: signed webhooks | the notification chapter says "no decision authorizes it" (`:100`) | yes |
| Out to a tenant: what changed (a new version, a metric not reporting) | ruling T3 needs it; no chapter | no |
| In from a billing provider: inbound webhooks | DEC-324d9e | no |

**State today.**
- Built: the outbox, the ticket consumer, webhook delivery.
- Unused today: all 3 endpoints are inactive and archived, and none is tied to a tenant (query QK).
- Not built: email, in-app notification, inbound receivers; `notification_log` and `email_template` are empty (query QB).
- Emission is "fail-open (an event failure never fails the engine act)" (`runtime-event.service.ts:6-7`).

**Known defects and risks.**
1. The governing chapter says the function is absent, so a session reading it will build a second one.
2. No ADR authorizes outbound webhooks; the chapter itself says so (`:100`).
3. Endpoints are registered by a platform admin only; a tenant cannot register its own.
4. Ruling T3 needs a way to tell a tenant about a pending version; nothing exists.
5. The value audit emits its result as event type `metric_run_completed` (`metric-value-audit.service.ts:89-90`), the same type a metric run uses.

**Governing ADRs.**

| ADR | Summary | Status |
|---|---|---|
| DEC-9c0da7 | Runtime doctrine; the event outbox is built under its sections 3 and 9 | decided |
| DEC-c06f41 | Created the chapter | decided |
| DEC-324d9e | Anticipates a billing webhook receiver | decided; not built |

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/implementation/notifications-and-webhooks.md` | rewrite | states that nothing is built; webhooks and the outbox are built |

**Open questions for the operator.**
- Are outbound webhooks an approved capability, to be recorded in an ADR, or removed?
- May a tenant register its own endpoint, or only the platform operator?
- Which channel tells a tenant about a pending value-affecting change: the portal only, or also email?

**What "locked" will mean here.**
1. The chapter matches the code, and an ADR authorizes each channel that exists.
2. Each event type has one meaning; the value audit has its own type.
3. Unused tables are either used or dropped.
4. The notice ruling T3 requires has a defined record and channel, or is listed as designed, not built.

---

### PR, Privacy and retention

**What it is.** Privacy and retention is how the platform meets a person's right to have personal data erased, and how it limits how long personal data is kept, on a platform whose records are immutable. The mechanism is nullification: a personal-data field is overwritten with a sentinel value while the row and its history remain. A data-subject request is a person's request to see or erase their data.

**How bc-docs defines it.**
- The governing chapter is `docs/compliance/privacy-and-the-immutable-fact.md` (drafting). Its scope: "This chapter records the platform's privacy posture and the resolution of the apparent tension between Foundation Invariant III (authoritative objects are immutable and append-only) and the right-to-be-forgotten obligations of GDPR, India's DPDP Act 2023, and California's CCPA." (`:29 @ f4f5edd`).
- The unit of erasure: "the field is the unit of erasure, not the row" (`:46`).
- Retention: "the engine evaluates active policies and creates nullification requests" (`:115`).
- A gap the chapter records itself: "The drift: the read-path filter is not yet wired; current readers see the original PII bytes from S3." (`:164`).
- Foundation says retention is "a policy concern governed at the storage layer" (`bc-docs:docs/foundation/the-evaluation-boundaries.md:158 @ f4f5edd`).
- The function is not in the readiness list; the main document, under "The functional map", adds it.

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Module | `src/nullification` (service, executor, evidence, S3, retention, data-subject response) | `bc-core:src/nullification/nullification.module.ts @ ec72438b` |
| Route | `nullification/requests` (create, list, get, approve, reject, execute, actions) | `bc-core:src/nullification/nullification.controller.ts:24-93 @ ec72438b` |
| Route | `nullification/requests/:id/dsar`, `nullification/dsar/:token` | `bc-core:src/nullification/dsar.controller.ts:19-54 @ ec72438b` |
| Route | `nullification/pii-registry` | `bc-core:src/nullification/pii-registry.controller.ts:23-63 @ ec72438b` |
| Route | `nullification/retention-policies`, `POST .../evaluate` | `bc-core:src/nullification/retention.controller.ts:18-61 @ ec72438b` |
| Tables | `operations.nullification_request` (1 row), `nullification_action` (0), `pii_field_registry` (24), `retention_policy` (0), `dsar_response` (0) | query QB |
| Screen | bc-admin `platform/nullification` | `bc-admin:src/components/AppRouter.tsx:303 @ d37b241`; `bc-admin:src/api/nullification.ts:92-211 @ d37b241` |
| Screens | bc-portal `/workspace/governance/policies-retention`, `/privacy-compliance` | `bc-portal:apps/web/src/components/AppRouter.tsx:164,167 @ 04930c8` |
| Seed | `src/nullification/seed/seed-pii-registry.ts` | `bc-core @ ec72438b` |
| Document | `privacy-and-the-immutable-fact.md` | below |

**The acts it performs.**

| Act | Who | Trigger as built | Entry point | Reads and writes |
|---|---|---|---|---|
| File a request | platform admin | manual | `POST nullification/requests` | `operations.nullification_request` |
| Approve or reject | platform admin | manual | `PATCH .../approve`, `.../reject` | the request row |
| Execute | platform admin | manual | `POST .../execute` | by the chapter's design, reads `pii_field_registry`, overwrites the listed fields and writes `nullification_action` (the executor's code was not opened) |
| Answer a data-subject request | platform admin | manual | `POST .../dsar` | `operations.dsar_response` |
| Evaluate retention policies | platform admin | manual only | `POST nullification/retention-policies/evaluate` | creates and auto-approves requests (`bc-core:src/nullification/retention.service.ts:1-8 @ ec72438b`) |

The retention service is "Designed to be invoked on a schedule" (`retention.service.ts:8`). No schedule invokes it: the only three scheduled tasks in bc-core are the nightly cycle, the weekly sweep and the provisioning-readiness check (command: `git grep -n "@Cron(" origin/main -- src`, excluding specs -> 3 matches, none in `src/nullification`). The chapter does not say what triggers retention evaluation.

**What it receives and what it hands on.**

| Hand-off | Defined in bc-docs | Built |
|---|---|---|
| In from a tenant: a person's request | the chapter names deadlines per regulation (`:71-83`) | no tenant route; every route is `@PlatformOnly()` (`nullification.controller.ts:24`) |
| In from S3, Tenant lifecycle and management: termination of a tenant, starting retention | stitch point 11 of the main document, under "The hand-offs between functions"; not in the chapter | no |
| Out to EV: evidence of the erasure | chapter | service present (`nullification-evidence.service.ts`) |
| Out to every reader of archived evidence: a filter that hides nullified fields | chapter line 164 | "not yet wired" |

**State today.**
- Built: the request lifecycle, the registry (24 fields: 14 with scope `platform`, 10 with scope `tenant`, query QT), the executor, the screen.
- Not exercised: the one request on record is an erasure with legal basis `gdpr_art17`, status `completed`, with 0 fields scanned, 0 fields nullified and 0 S3 objects handled, and there are no action rows (query QM; query QB).
- Not in use: no retention policy exists (query QB).
- Not built: a tenant-facing request route; scheduled retention; the archive read filter.

**Known defects and risks.**
1. The only completed erasure changed nothing, so the mechanism has no recorded real run.
2. Retention never runs unless an admin calls the route, and there is no policy to evaluate.
3. Archived copies still show original personal data to readers (chapter line 164).
4. The field registry is seeded by hand; a new table with personal data is covered only if someone adds a row.
5. The portal's retention and privacy pages exist without a tenant route behind them in bc-core.

**Governing ADRs.**

| ADR | Summary | Status |
|---|---|---|
| DEC-bd5492 | Nullification as privacy erasure on an immutable platform | decided |
| DEC-ae331f | ISO 27001 and SOC 2 pursued step by step on reduced criteria; the chapter cites it for deferring the privacy criterion | decided |
| DEC-771baf | Tenant database topology the executor traverses | implemented |

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/compliance/privacy-and-the-immutable-fact.md` | keep nearly as is | accurate on the mechanism; add the triggers and the as-built gaps |
| `docs/operating-model/tenancy-and-binding.md`, section "Proof Retention Policy" | rewrite | retention of proof must be joined to this function |

**Open questions for the operator.**
- Is retention evaluated on a schedule, or only by an operator act?
- May a tenant's admin file a data-subject request in the portal, or only the platform operator on the tenant's behalf?
- When a tenant is terminated, what is retained, for how long, and what is erased?

**What "locked" will mean here.**
1. One erasure has been run end to end on a test subject, with action rows and evidence, by the written procedure.
2. Every table that holds personal data is in the registry, checked by a CI guard over the schema.
3. The trigger for retention is stated and built, or the function is listed as designed, not built.
4. The archive read filter is built, or the chapter states the limit in plain words for a customer.

---

### MD, Master data

**What it is.** Master data is the reference data that other functions look up and do not author: countries, currencies, the calendar of dates, named fiscal calendars and their periods, business functions and subfunctions, industries, and the lists of allowed values for classifications. It also includes, per tenant, the legal entities a tenant declares and the fiscal calendar each one uses.

**How bc-docs defines it.**
- **bc-docs has no chapter for master data.** The readiness function list does not contain it; the main document, under "The functional map", adds it.
- The nearest governing chapter is `docs/operating-model/fiscal-time-and-temporal-gates.md` (drafting): "Fiscal period is a per-Canonical-Object attribute. The value of fiscal period for a Canonical Object is determined by the posting date carried on the Canonical Object's canonical payload, resolved against the tenant's fiscal calendar configuration for the relevant legal entity." (`:36 @ f4f5edd`). It names "the calendar stack" of four components governed by DEC-d7e7a0 (`:52`).
- The vocabulary defines the legal-entity binding: "Which legal entity a source's company code belongs to, for one tenant" (`vocabulary.md:552`).
- A generated reference exists, `docs/reference/data-dictionary/master.md`, "Generated from `bc-core/src/database/schema`", `generated_at: 2026-07-06`, `source_commit: 44767f0` (`:1-14 @ f4f5edd`). It is four months old.
- The frontend rule that screens read lists through master-data hooks is cited in `frontend-experience.md:39` ("the master-data hook discipline").

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Schema | `master` (32 tables) | query QA |
| Tables | `master.dim_date` (36,890 rows), `dim_fiscal_calendar` (3), `dim_fiscal_period` (110,670), `dim_country` (50), `dim_currency` (40) | query QB |
| Tables | `master.master_function` (20), `master_subfunction` (119), `master_status` (42), `master_industry` (21), and 20 further `master_*` lists | query QB |
| Table | `master.library` (75), a register of software libraries; shared with OP, to be split | query QB; `bc-core:src/platform/library.controller.ts:21-102 @ ec72438b` |
| Table | `master.semantic_family` (23); shared with L3, to be split | query QB |
| Route | `masters/*`, read only (industries, functions, currencies, countries, statuses, subfunctions) | `bc-core:src/platform/masters/masters.controller.ts:13-142 @ ec72438b` |
| Route | `t/legal-entities`, `t/legal-entities/:code/fiscal-calendars` | `bc-core:src/registry/legal-entity/legal-entity.controller.ts:34-65 @ ec72438b` |
| Route | `t/tax-registrations` | `bc-core:src/registry/tax-registration/tax-registration.controller.ts:35-67 @ ec72438b` |
| Route | `tenant-classification/gl-accounts`; shared with L5, to be split | `bc-core:src/registry/gl-classification/gl-classification-binding.controller.ts:33-85 @ ec72438b` |
| Service | `FiscalCalendarService` | `bc-core:src/registry/fiscal-calendar.service.ts:122 @ ec72438b` |
| Seeds | `src/platform/masters/seed/*` (countries, currencies, domains, statuses, subdomains) | command: `git ls-tree -r --name-only origin/main src/platform` @ ec72438b |
| Tables (tenant database) | legal entities and per-entity fiscal calendar (`tenant_dim.*`) | named in `vocabulary.md:552`; rows not reachable |
| Tables (demo plane) | `demo.dim_legal_entity` (3), `demo.fiscal_calendar_config` (3); shared with PV | query QB |
| Screens | bc-admin `platform/masters`; bc-portal `/workspace/fiscal-context`, `/legal-entities/*` | `bc-admin:src/components/AppRouter.tsx:302 @ d37b241`; `bc-portal:apps/web/src/components/AppRouter.tsx:148,172-176 @ 04930c8` |

**The acts it performs.**

| Act | Who | Trigger as built | Entry point | Reads and writes |
|---|---|---|---|---|
| Load or change platform master lists | a developer | a seed script, run by hand | the seed files; no npm script for them was found (command: `grep -nE '"(seed|masters)' package.json` at ec72438b -> `seed:registry` and an archived `seed:v2` only) | `master.*` |
| Read a master list | any platform-scoped caller | on demand | `GET masters/*` | `master.*` |
| Declare a legal entity | tenant admin, operator or platform admin | manual | `POST t/legal-entities` | tenant database |
| Assign a fiscal calendar to a legal entity | the same roles | manual | `POST t/legal-entities/:legalEntityCode/fiscal-calendars` | tenant database; reads `master.dim_fiscal_calendar` |
| Classify a tenant's ledger accounts | platform admin | manual | `POST tenant-classification/gl-accounts/seed-from-defaults`, `/overrides` | `tenant.gl_account_classification_binding` (0 rows, query QB) |

bc-docs does not say who may change a platform master list, or by which act. There is no governed write route for `master.*`.

**What it receives and what it hands on.**

| Hand-off | Defined in bc-docs | Built |
|---|---|---|
| Out to RT: the fiscal period of a canonical object, from posting date and the legal entity's calendar | `fiscal-time-and-temporal-gates.md:36-43` | yes (`FiscalCalendarService`) |
| Out to RT: the legal entities a scheduled evaluation covers | ADR DEC-ffbc24 | taken from an environment variable, not from the record (see RT) |
| Out to the Authoring functions (L1 to L10): functions, subfunctions and classification lists | no chapter | yes, by lookup |
| Out to S4 and DL: functions and subfunctions as a way to name a package's metrics | lifecycle chapter line 84 | no |
| In from TS: a tenant's declared legal entities | ADR DEC-4aa1ff | yes |

**State today.**
- Built: 32 tables with data; three named fiscal calendars (`IN-APR-MAR-MONTHLY`, `US-CAL-MONTHLY`, `UK-APR-MAR-QUARTERLY`, query QU).
- No governed write: platform lists change only through seed scripts.
- Mixed scope: the schema holds a software-library register and a vocabulary table beside true reference data.
- Not in use: account classification bindings (0 rows).
- Tenant-side counts (legal entities, calendars) could not be read.

**Known defects and risks.**
1. No chapter defines the function or names its owner.
2. The generated dictionary is dated 2026-07-06 and cannot be trusted as current.
3. A change to a master list has no act, no evidence and no review route other than a code change.
4. `master.master_status` (42 rows) sits beside the vocabulary page as a second list of status words; which one governs a screen is not stated.
5. The scheduler names legal entities in an environment variable, so the record a tenant declared is not what a scheduled evaluation follows.

**Governing ADRs.**

| ADR | Summary | Status |
|---|---|---|
| DEC-d7e7a0 | Platform date table, per-entity tenant fiscal calendar, and the fiscal calendar service | implemented |
| DEC-4aa1ff | A platform-minted legal-entity identity; declaration is a tenant-side act | decided |
| DEC-ea4523 | The fiscal resolver derives the period from posting date and the entity's calendar | decided |
| DEC-ffbc24 | Legal entity is a runtime evaluation axis | decided |

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/operating-model/fiscal-time-and-temporal-gates.md` | keep nearly as is | named sound by the chapters annex; last changed 2026-07-07, so check against DEC-4aa1ff |
| `docs/reference/data-dictionary/master.md` | rewrite | regenerate from the live database |
| (none exists) | rewrite | a short new chapter: what master data is, who changes it, by which act |

**Open questions for the operator.**
- Who may change a platform master list, and is that a governed act with a record or a reviewed code change?
- Does `master.master_status` remain, or does the vocabulary page become the only list of status words?
- Do the library register and the vocabulary table leave the `master` schema?

**What "locked" will mean here.**
1. One chapter lists every master table with its owner and the one act that changes it.
2. A fresh restore plus the written procedure reproduces every master list, checked by row counts.
3. The dictionary is generated in CI and fails when it is out of date.
4. No evaluation setting names a legal entity or calendar outside its record.

---

### AI, AI services

**What it is.** AI services are the AI panels the platform uses to draft and to judge governed content, the vendors those panels call, and the record of what each call cost. An AI panel is a fixed set of AI models, each in a named seat, that answers one question about one case. There are four panels. All run inside bc-core. bc-docs still describes a separate service, bc-ai, that was retired.

**How bc-docs defines it.**
- The vocabulary, slice 5: "An **AI panel** is a fixed set of AI models, each in a named seat, that answers one question about one case. The panels run inside bc-core (DEC-ffee4e). A panel advises or decides only as far as its governing decision says; the operator's acts and the gates stay in force." (`bc-docs:docs/reference/vocabulary.md:622 @ f4f5edd`). It names the four panels and their records (`:626-629`).
- The seven chapters under `docs/ai/` say otherwise: "bc-ai is the platform's single AI service. It is a Python service running FastAPI on uvicorn" (`bc-docs:docs/ai/ai-architecture.md:41 @ f4f5edd`). Counting the string `bc-ai` in each chapter at f4f5edd gives: ai-architecture 30, ai-gates 23, bedrock-and-inference-profiles 21, ai-agents 18, ai-usage-visibility 16, ai-trust-and-verification 5, ai-overview 3. None of the seven cites DEC-ffee4e (count 0 in each).
- The vocabulary records this as a defect: "`docs/ai/` pages carry `authority: authoritative` and describe bc-ai, which DEC-ffee4e retired." (`vocabulary.md:703`).
- The function is not in the readiness list; the main document, under "The functional map", adds it.

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Call path 1 | registry authoring panel: Anthropic, Bedrock and OpenAI clients | `bc-core:src/registry/bcf/panel/in-process/panel-vendor-clients.ts:104,130,192,233 @ ec72438b` |
| Call path 2 | metric authoring panel: Anthropic, OpenAI, Z.ai, DeepSeek and Bedrock endpoints | `bc-core:src/registry/mcf/panel-agents/panel-agent-factory.ts:65-76,209 @ ec72438b` |
| Call path 3 | certification panel: DeepSeek, Z.ai and Google endpoints | `bc-core:src/registry/mcf/audit-panel/audit-seat-factory.ts:129,137,311 @ ec72438b` |
| Call path 4 | ABC reasoning panel: its own model client for Anthropic, which wraps an SDK object passed to it | `bc-core:src/registry/abc/panel/anthropic-model-client.ts:2,191,326 @ ec72438b` |
| Model defaults in code | maker `claude-opus-4-7`, checker `gpt-5.4-mini-2026-03-17`, judge `deepseek-v4-pro` | `bc-core:src/registry/mcf/panel-agents/model-defaults.ts:67-74 @ ec72438b` |
| Route | `POST bcf/registry-authoring-runs`; panel run reads | `bc-core:src/registry/bcf/panel/registry-authoring-run.controller.ts:24 @ ec72438b` |
| Route | `mcf/panel-runs`, `mcf/audit-panel` | `bc-core:src/registry/mcf/mcf-panel-run.controller.ts:39 @ ec72438b`; `bc-core:src/registry/mcf/audit-panel/audit-panel-roster.controller.ts:26 @ ec72438b` |
| Route | `GET vendor-costs` | `bc-core:src/platform/vendor-costs/vendor-costs.controller.ts:32-37 @ ec72438b` |
| Route | `POST ai-telemetry/bcf-panel-run/from-summary` | `bc-core:src/registry/bcf/telemetry/bcf-telemetry.controller.ts:42-59 @ ec72438b` |
| Tables | `bcf.panel_output_record` (2,743 rows), `bcf.calibration_event` (2,129), `mcf.metric_authoring_panel_run` (553), `mcf.metric_authoring_panel_transcript` (1,659), `mcf.audit_contextual_panel_run` (81), `mcf.audit_panel_roster_registration` (1) | query QB |
| Tables | `ai_telemetry.ai_run_ledger` (142), `ai_telemetry.ai_call_ledger` (376) | query QB |
| Documents | `docs/ai/*` (seven chapters); vocabulary slice 5 | below |

The panels' verdicts and their governed writes belong to L3 and L6. This function owns the calling, the rosters and the cost. That line is shared with L3 and L6, to be split.

**The acts it performs.**

| Act | Who | Trigger as built | Entry point | Reads and writes |
|---|---|---|---|---|
| Run the registry authoring panel | operator | manual call | `POST bcf/registry-authoring-runs` | `bcf.panel_output_record` |
| Run the metric authoring panel | operator | manual call on an intake | `mcf/panel-runs` | `mcf.metric_authoring_panel_run` and transcripts |
| Run the certification panel | operator | a request for certification (`POST mcf/metric-contract-versions/:mcvUid/request-audit`, `bc-core:src/registry/mcf/mcf-request-audit.controller.ts:50-59 @ ec72438b`) | `POST mcf/metric-contract-versions/:mcvUid/certification-runs/:runUid/panel-decision` (`bc-core:src/registry/mcf/mcf-certification-panel-decision.controller.ts:37-41 @ ec72438b`) | `mcf.audit_contextual_panel_run`; `metric_audit.decision` |
| Register a certification roster | operator, with calibration evidence | manual | `mcf/audit-panel` | `mcf.audit_panel_roster_registration` |
| Reconcile vendor spend | platform user | on read; "Phase 1 is STATELESS — nothing is persisted" (`bc-core:src/platform/vendor-costs/vendor-costs.service.ts:1-9 @ ec72438b`) | `GET vendor-costs` | reads vendor billing APIs and `bcf.panel_output_record` |
| Record telemetry | operator | manual post of a run summary | `POST ai-telemetry/bcf-panel-run/from-summary` | `ai_telemetry.*` |

bc-docs does not say what triggers a panel run beyond the procedures of L3 and L6.

**What it receives and what it hands on.**

| Hand-off | Defined in bc-docs | Built |
|---|---|---|
| In from L3 and L6: a case to draft or judge | vocabulary S5.1 | yes |
| Out to L3 and L6: a panel verdict | vocabulary S5.2a | yes |
| In from OP: vendor keys from the secrets store | CLAUDE.md of barecount-devhub; no bc-docs chapter opened | yes, read from environment variables (`panel-vendor-clients.ts:130,233`) |
| Out to the operator: cost per run and per vendor | `ai-usage-visibility.md` describes bc-ai | partly: a stateless report and a ledger that stopped |

**State today.**
- Works: the panels run. The latest registry panel record is dated 2026-11-12, the latest metric authoring run 2026-11-04, and the latest certification run 2026-09-30 (query QP).
- Duplicated: four separate sets of vendor clients, one per panel.
- Hard-coded: the metric authoring panel's models are constants in code, overridable by environment variables (`model-defaults.ts:67-88`).
- Stopped: the telemetry ledger holds runs from 2026-06-17 to 2026-06-19 only, 142 runs with a recorded cost of 38.86 USD (query QN). Panel runs after that date are not in it.
- Stale documents: seven authoritative chapters describe a service that does not exist.

**Known defects and risks.**
1. "The documented roster is not the roster that runs." (`vocabulary.md:698`).
2. The registry panel's verdict field has no value rule and one result has two spellings (`vocabulary.md:696`).
3. "The ABC reasoning panel keeps no record of its runs." (`vocabulary.md:702`).
4. Cost is not recorded per run after June 2026, so spend can be reconciled only against vendor invoices.
5. A vendor change must be made in up to four places.
6. A Gemini API key is committed in an archived script (not re-checked for this dossier; recorded in the evidence annex, row 17a, and in the main document under "Items outside the program").

**Governing ADRs.**

| ADR | Summary | Status |
|---|---|---|
| DEC-ffee4e | Retire bc-ai; the registry panel runs inside bc-core | implemented |
| DEC-53629b | Replaces the registry panel's moderator model; amends DEC-ffee4e | decided |
| DEC-09f86b | The metric authoring panel's judge seat | implemented |
| DEC-e87701 | The metric panel's lower-cost roster with a direct DeepSeek judge | decided |
| DEC-d3b916 | Certification roster registrations are governed by DEC-c48b0f | decided |
| DEC-c48b0f | Certification is a second panel before activation | decided |
| DEC-cff0cf | The ABC orchestrator and its reasoning panel | decided |
| DEC-149ab2 | Framework approval; its title still says "Business Context Framework", a retired name | decided |

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/ai/ai-architecture.md`, `ai-agents.md`, `ai-gates.md`, `ai-usage-visibility.md`, `bedrock-and-inference-profiles.md` | history | describe the retired bc-ai service |
| `docs/ai/ai-overview.md`, `ai-trust-and-verification.md` | rewrite | few references to bc-ai; the trust posture may still hold |
| `docs/reference/vocabulary.md` slice 5 | keep nearly as is | the accurate definition of the panels |

**Open questions for the operator.**
- Is there one shared vendor client and one roster record for all panels, or does each panel keep its own?
- Is cost recorded per run in the ledger for every panel, or reconciled from vendor invoices only?
- Is the ABC reasoning panel kept, with a record of its runs, or retired?

**What "locked" will mean here.**
1. One chapter describes the panels as they run; the bc-ai chapters are marked as history.
2. One module calls vendors; a CI guard fails on a vendor address outside it.
3. Every roster is a record with the operator's sign-off, and the running models match it, checked at start-up.
4. Every panel run writes its cost to one ledger.
5. Verdict fields have value rules.

---

### SU, Support

**What it is.** Support is how a problem with the platform or with a tenant's data becomes a tracked ticket and is resolved. As built, the platform raises tickets automatically when a runtime act fails or a contract is violated, and platform operators work them in the operator console. There is no route for a tenant to open a ticket.

**How bc-docs defines it.**
- The governing chapter is `docs/operations/support-and-escalation.md` (drafting). It says: "A customer ticketing system (ServiceDesk, Zendesk, Intercom, Front, or equivalent) is not part of the readiness baseline. A customer concern arrives through the email inbox or through direct sales-led channels for Professional and Enterprise tiers." (`:57 @ f4f5edd`) and lists the email channel as having "no automated triage or ticketing surface in the readiness baseline" (`:54`).
- **The chapter is silent on what is built.** A search of the chapter for `support/tickets`, `support.ticket` or "ticket table" returns nothing (command: `git show origin/main:docs/operations/support-and-escalation.md | grep -iE "support/tickets|support\.ticket|ticket table"` -> no match).
- Its escalation path still lists `bc-ai` among the projects (`:68`).
- The function is not in the readiness list; the main document, under "The functional map", adds it.

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Module | `src/support` | `bc-core:src/support/support.service.ts @ ec72438b` |
| Route | `support/tickets` (`POST`, `GET`, `GET stats`, `GET :ticketId`, `PATCH :ticketId`, `POST :ticketId/comments`), platform only | `bc-core:src/support/support.controller.ts:20-84 @ ec72438b` |
| Service | `BoundaryTicketService`, automatic tickets; shared with NT, to be split | `bc-core:src/boundary/boundary-ticket.service.ts:1-18 @ ec72438b` |
| Tables | `support.ticket` (6,227 rows), `support.ticket_comment` (4) | query QB |
| Screens | bc-admin `platform/tickets`, `platform/tickets/:ticketId` | `bc-admin:src/components/AppRouter.tsx:297-298 @ d37b241` |
| Screens | bc-portal `/support`, `/help`, `/contact-admin` | `bc-portal:apps/web/src/components/AppRouter.tsx:123,139,141 @ 04930c8` |
| Document | `support-and-escalation.md` | below |

**The acts it performs.**

| Act | Who | Trigger as built | Entry point | Reads and writes |
|---|---|---|---|---|
| Raise a ticket automatically | the platform | a boundary failure: categories `admission_failure`, `connection_failure`, `contract_violation`, `drift_alert`, with "one open ticket per entity per category" (`boundary-ticket.service.ts:4-5,11`) | `BoundaryTicketService` | `support.ticket` |
| Open a ticket by hand | platform admin, operator or analyst | manual | `POST support/tickets` | `support.ticket` |
| Update, assign, resolve | the same roles | manual | `PATCH support/tickets/:ticketId` | `support.ticket` |
| Comment | the same roles | manual | `POST support/tickets/:ticketId/comments` | `support.ticket_comment` |
| Open a ticket as a tenant | not built | none | none | none |

bc-docs does not describe the automatic trigger at all.

**What it receives and what it hands on.**

| Hand-off | Defined in bc-docs | Built |
|---|---|---|
| In from RT and NT: failures that need attention | `runtime-operations.md`, section "Failure routing" (heading at `:85`) | yes |
| In from TS: a tenant's request for help | the chapter names email only | the portal page calls `GET /support/tickets?limit=100` (`bc-portal:apps/web/src/api/support.ts:52-53 @ 04930c8`), a route marked `@PlatformOnly()` (`support.controller.ts:20`) |
| Out to the operator: a queue to work | no chapter | yes (bc-admin) |
| Out to a tenant: status of its ticket | not defined | no |
| In from S4: the support terms of the tenant's tier | chapter, "Per-Tier Support Posture" (`:34`) | no Subscription exists (query QE) |

**State today.**
- Built: the ticket store, the automatic raising, the operator screens.
- Volume: 6,227 tickets created between 2026-03-23 and 2026-10-20; 6,224 carry a tenant; all have source `system`. By category and status: `contract_violation` 6,171 closed and 33 open; `connection_failure` 11 closed, 6 open, 1 in progress; `manual` 3 closed; `admission_failure` 1 closed; `drift_alert` 1 closed (query QL).
- Hardly worked by people: 4 comments on 6,227 tickets (query QB).
- Not built: a tenant route; tier-based terms.
- Whether the portal's support page is refused at run time was not tested; no service was started.

**Known defects and risks.**
1. The portal's support page depends on a platform-only route, so a tenant user's call is expected to be refused (not tested).
2. 39 tickets are open (33 + 6) and 1 is in progress (query QL); no ticket has been created since 2026-10-20.
3. Almost every ticket is an automatic contract violation, so the store is a failure log more than a support desk.
4. The chapter describes a support model by tier that has no record to stand on.
5. The chapter does not mention the built ticket system, so a session will not find it.

**Governing ADRs.**

| ADR | Summary | Status |
|---|---|---|
| DEC-324d9e | Four subscription tiers; the chapter derives support terms from them | decided; not built |
| DEC-1392ee | The demo tier | decided |
| DEC-9c0da7 | Runtime doctrine, including failure routing to tickets | decided |

No ADR governs the ticket store itself.

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/operations/support-and-escalation.md` | rewrite | describes email-only support; the ticket system is built and unmentioned |
| `docs/operations/incident-and-change-management.md` | rewrite | the boundary with support must be redrawn (not opened in this task; listed for its Define step) |

**Open questions for the operator.**
- Are automatic failure tickets support, or a runtime failure log that belongs to RT and the operator console?
- May a tenant open and follow a ticket in the portal, or does support stay with email?
- Who owns the open tickets today, and are they closed in bulk as part of the freeze?

**What "locked" will mean here.**
1. The chapter describes the ticket store, its automatic triggers and who works it.
2. The portal's support page either calls a tenant-scoped route or is removed.
3. Each automatic ticket category has an owner and a closing rule.
4. No ticket is open without an assignee, checked by a read in DevHub.
