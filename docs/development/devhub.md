---
id: devhub
order: 38
title: "DevHub"
status: drafting
authority: authoritative
depends_on: [the-authority-model, audit-and-activity-logging, incident-and-change-management]
governing_sources:
  - The Authority Model
  - Audit and Activity Logging
  - Incident and Change Management
governing_adrs:
  - DEC-a4e550 (ADR-First Decision Workflow; ADR file is SSOT, DevHub is metadata registry)
  - DEC-633b2a (D-code monotonic allocator; concurrent-session safety; UID canonical, D-code nickname)
  - DEC-623f8f (ADR Hygiene Policy; supersession pair rule, stuck-proposed audit, eight rules)
  - DEC-ebf0b4 (Session Discipline and Data Integrity Rules; D268 self-audit at session close)
  - DEC-804874 (L-Node Verification with Semantic Family Classification; session-close gate per D366)
  - DEC-3395bc (bc-docs-v3 SSOT cutover; ADR files written into bc-docs-v3 by devhub_decision_record)
errata_referenced: []
v2_sources: []
diagrams: []
---

# DevHub

## Scope

This chapter records DevHub as the platform's engineering-coordination substrate. It states the deployable shape of DevHub (a Node and Express HTTP server backed by a SQLite database, paired with a stdio MCP server that exposes DevHub operations to a Claude Code agent), the DevHub registry surface (sessions, tasks, plans, decisions, change records, document index, screen registry, API registry, MCP tool registry, risk register, QA non-conformity records, L-node verdicts), the DevHub MCP tool families that Claude sessions consume, the DevHub activity log as the cross-domain trail, and the boundaries between DevHub-owned state and the artifact-owning chapters that consume it.

This chapter does not redefine the decision and change procedure (Decision and Change Procedure), the audit and change-record substrate (Audit and Activity Logging), or the QA tool surface (Quality Assurance). Those chapters consume DevHub and own their own claims.

**Governing source.** outline.md §4.5; Audit and Activity Logging.

## What DevHub Is

DevHub is a single Node service plus a single SQLite database plus a stdio MCP server. The combination is the platform's coordination registry for engineering work: the substrate where sessions are opened and closed, where tasks are recorded and tracked, where decisions are recorded as ADR registry rows that point at ADR files in bc-docs-v3, where change records pair plan with report per session, and where cross-domain registries (documents, screens, API endpoints, MCP tools, risks, QA non-conformities, L-node verdicts) hold metadata that other surfaces scan into.

| Property | Form |
|---|---|
| Deployable shape | One Node service on a reserved port; one SQLite database file in `data/devhub.db`; one stdio MCP server spawned by the Claude Code agent. Reserved-port detail is owned by Infrastructure |
| Storage substrate | better-sqlite3, WAL journal mode, FK constraints enabled (`src/db.js`) |
| Registry tables | The DevHub schema declares thirty-six tables covering session, task, plan, decision, change-record, document, screen, screen-children, API, MCP-tool, risk, QA-audit-run, QA-NC, ADR-orphan-triage, ADR-audit-snapshot, `process_audit`, plan-approval, plan-version, plan-reference, audit-finding, parking-item, todo, server, and project domains |
| MCP server | `src/mcp-server.js` registers sixty `devhub_*` tools across eighteen domains; the server speaks stdio to the Claude Code harness |
| Activity log | Every governed action writes a row in `activity` with `session_id`, `project_id`, `activity_type`, and `message_text`; reads do not log |

DevHub is deliberately a coordination registry, not a runtime. It does not run contract evaluation, does not write tenant-database authoritative state, does not host tenant-facing surfaces. It records what engineering intends, what engineering did, and what governance bodies authored, and it surfaces that record back to the Claude session at session boot.

**Governing source.** `barecount-devhub/src/db.js` (table declarations); `barecount-devhub/src/mcp-server.js` (tool registration); CLAUDE.md (Stack section).

## The MCP Tool Surface

The DevHub MCP server exposes sixty tools to a Claude Code session. The tool families are a stable surface; tool counts inside a family change as registries evolve.

| Family | Count | Representative tools |
|---|---|---|
| Session | 6 | `devhub_session_boot`, `devhub_session_open`, `devhub_session_save_plan`, `devhub_session_checkpoint`, `devhub_session_close`, `devhub_session_get_context` |
| Task | 5 | `devhub_task_add`, `devhub_task_batch`, `devhub_task_list`, `devhub_task_update`, `devhub_task_quick_complete` |
| Decision | 3 | `devhub_decision_record`, `devhub_decision_list`, `devhub_decision_update` |
| Plan | 5 | `devhub_plan_read`, `devhub_plan_save`, `devhub_plan_update`, `devhub_plan_submit_for_review`, `devhub_plan_approve` |
| Change record | 2 | `devhub_change_record_save`, `devhub_change_record_list` |
| Document | 6 | `devhub_doc_scan`, `devhub_doc_list`, `devhub_doc_get`, `devhub_doc_update`, `devhub_doc_link_ref`, `devhub_doc_validate` |
| Screen | 5 | `devhub_screen_list`, `devhub_screen_get`, `devhub_screen_update`, `devhub_screen_stats`, `devhub_screen_children_list` |
| API | 3 | `devhub_api_list`, `devhub_api_blast`, `devhub_api_scan` |
| MCP tool | 3 | `devhub_mcp_list`, `devhub_mcp_get`, `devhub_mcp_scan` |
| Risk | 3 | `devhub_risk_add`, `devhub_risk_list`, `devhub_risk_update` |
| QA NC | 5 | `devhub_qa_audit`, `devhub_qa_nc_list`, `devhub_qa_nc_raise`, `devhub_qa_nc_update`, `devhub_qa_nc_stats` |
| L-node | 3 | `devhub_l_node_verify`, `devhub_l_node_audit`, `devhub_l_node_refresh` |
| Chain status | 1 | `devhub_chain_status` |
| Audit harness | 3 | `devhub_process_audit_run`, `devhub_process_audit_get`, `devhub_process_audit_list` |
| ADR orphan triage | 2 | `devhub_adr_orphan_triage_list`, `devhub_adr_orphan_triage_save` |
| ADR audit | 2 | `devhub_adr_audit_history`, `devhub_adr_audit_save` |
| Activity log | 1 | `devhub_activity_log` |
| Auth | 1 | `devhub_get_cognito_token` |
| Project | 1 | `devhub_project_list` |

A session that needs to coordinate engineering work consumes the MCP family that owns the artifact. The chapter that owns the artifact (Decision and Change Procedure for decisions and change records; Documentation System for the document registry; Quality Assurance for the QA NC register; Audit and Activity Logging for the activity log; Operating Model for chain-status reads) names the runtime act; this chapter names the deployable surface.

**Governing source.** `barecount-devhub/src/mcp-server.js`.

## The Session Substrate

Sessions are the unit of governed engineering work. Each session opens against a project, carries a plan, records checkpoints, and closes with a summary plus a self-audit. The `sessions` table records the row; the `session_checkpoints` table records the per-session progress entries; the `change_records` table records the paired plan-and-report side per session UID; the `activity` table records the lifecycle events.

| Lifecycle act | Tool | Write path |
|---|---|---|
| Open | `devhub_session_open` | Inserts a row into `sessions` with `uid` (`SES-xxxxxx`), `project_id` (FK to `projects.id`), `branch_name`, `actor_name`, and `started_ts`; logs `session_start` |
| Plan | `devhub_session_save_plan` | Updates `sessions.plan_text`; auto-writes the plan side of `change_records` for the session UID; logs `session_plan` |
| Checkpoint | `devhub_session_checkpoint` | Inserts a row into `session_checkpoints` with `session_id` FK, auto-numbered `checkpoint_number`, `checkpoint_status`, `summary_text`, `remaining_text`; logs `session_checkpoint` |
| Close | `devhub_session_close` | Updates `sessions.ended_ts`, `summary_text`, `state_at_end_text`, `next_steps_text`; computes a discipline report; runs the L-node semantic gate; if accepted, logs `session_end` |

The plan side is mandatory before any work begins. CLAUDE.md (Session Protocol step 4) states this explicitly: a session that starts coding without a saved plan has no crash-recovery substrate and no plan-side change record.

The session UID is the linkage that joins the `activity` rows, the `session_checkpoints` rows, the `change_records` row, and the close summary. An auditor reconstructs a session by querying each table with `ref_uid = SES-xxxxxx` or `session_id = N`.

**Governing source.** `barecount-devhub/src/routes/projects.js` (session lifecycle endpoints); CLAUDE.md (Session Protocol section); Audit and Activity Logging.

## The L-Node Semantic Gate at Session Close

Session close runs a gate before accepting the close summary. The gate reads the chain-status SSOT for the session window and detects regression in the `overall_verdict`: a transition from `complete` or `partial` to `broken` or `unlinked` during the session.

| Outcome | Behavior |
|---|---|
| No regression | Close proceeds; `sessions.ended_ts` is set and the close summary is recorded |
| Regression detected, no override supplied | Close is blocked; the MCP tool returns an error naming the regressed contracts |
| Regression detected, override supplied | `self_audit_json.l_node_override` carries a rationale of at least forty characters; close proceeds; a followup task tagged `l-node-regression` is auto-spawned with the regression list and break reasons; the override rationale is preserved in the change record |
| Gate errors (chain-status endpoint unreachable, Cognito outage, audit endpoint outage) | Gate fails open; close proceeds with a non-blocking warning so that infrastructure outages do not block governed close |

Per `DEC-804874`: legitimate override cases are emergency fix, known-broken tenant, or migration in progress. The override surface is a discipline gate, not an authorization escape hatch; CLAUDE.md ("Don't" section) names casual override as a violation of session discipline.

The L-node verdicts themselves are persisted in the bc-core `contract.l_node_semantic_verdict` table and read through the `devhub_l_node_verify`, `devhub_l_node_audit`, and `devhub_l_node_refresh` MCP tools, which proxy to the bc-core registry endpoint. DevHub does not author L-node verdicts; it consumes them at session close as a governance gate.

**Governing source.** `barecount-devhub/src/mcp-server.js` (session close gate at the close-handling block); DEC-804874 (the L-Node Verification ADR titled "L-Node Verification with Semantic Family Classification").

## The D-Code Allocator

Decision UIDs (`DEC-xxxxxx`) and decision codes (`Dxxx`) are two parallel identifiers per `DEC-633b2a`. The UID is canonical and structurally unique. The D-code is a monotonic nickname allocated by an atomic transaction in DevHub.

| Identifier | Form | Allocation | Use |
|---|---|---|---|
| UID | `DEC-xxxxxx` (six hex chars from `crypto.randomBytes(3)`) | Per row, generated at insert time | Canonical reference in code, ADR filename, registry primary key |
| D-code | `D{nnn}` (monotonic decimal) | Atomic transaction against the `decision_code_counter` singleton row, serialized so concurrent sessions cannot collide | Human-readable nickname in conversation and in v2 SOP shorthand |

The allocator is `src/lib/decision-code-reconcile.js`. Concurrent decision-record calls are serialized at the SQLite transaction layer; two parallel calls cannot allocate the same `Dxxx` value. The historical registry contains twenty-four duplicate D-codes from before the allocator existed; per `DEC-623f8f` rule 5, those duplicates are not renumbered, the canonical UID is used as the load-bearing identifier in published content, and the D-code remains as a nickname.

**Governing source.** `barecount-devhub/src/lib/decision-code-reconcile.js`; DEC-633b2a (the D-code vs DEC-UID ADR); DEC-623f8f (the ADR Hygiene Policy).

## The Document, Screen, API, and MCP-Tool Registries

DevHub holds derived registries scanned from external repositories. Each scanner walks a target repo, extracts metadata, and writes rows into the corresponding table. Scanners run on demand, not on session boot.

| Registry | Scanner tool | Source | Written rows |
|---|---|---|---|
| Document | `devhub_doc_scan` | `bc-docs-v3` walked by frontmatter (env override `BC_DOCS_PATH`) | `documents` rows with `id`, `type`, `domain`, `authority`, `status`, `governing_adrs` derived from path and frontmatter |
| Screen | `devhub_screen_stats` (and adjacent tools) | bc-portal and bc-admin source for screen metadata | `screen_registry`, `screen_children`, `screen_api_map`, `screen_data_needs`, `screen_dependencies`, `screen_tests` |
| API | `devhub_api_scan` | bc-core, bc-admin, bc-portal, bc-ai source for endpoint declarations | `api_registry`, `api_consumer`, `api_cross_cutting` |
| MCP tool | `devhub_mcp_scan` | DevHub itself plus other MCP server source | `mcp_tool_registry` |

Per pattern 81: the registries are derived. They are an index for navigation, not the authority for the artifacts they index. Authority is the file (the chapter under `bc-docs-v3/docs/`, the route handler under `bc-core/src/`, the screen component under `bc-admin/src/`, the MCP tool registration under `barecount-devhub/src/mcp-server.js`). When a registry row contradicts the file, the file wins and the registry is rescanned.

**Governing source.** `barecount-devhub/src/lib/doc-scanner.js`, `barecount-devhub/src/lib/api-scanner.js`, `barecount-devhub/src/lib/mcp-tool-scanner.js`; CLAUDE.md (Documentation section, MCP Server section).

## Activity Log Coverage

The `activity` table records every governed write across DevHub. Reads are not recorded. The `activity_type` column carries a small enumeration of event names; each governed write writes one row.

| Domain | Event types recorded | What is not recorded |
|---|---|---|
| Session lifecycle | `session_start`, `session_plan`, `session_checkpoint`, `session_end` | Read calls (`devhub_session_boot`, `devhub_session_get_context`) |
| Task | `task_created`, `task_updated`, `task_completed` | List calls (`devhub_task_list`) |
| Decision | `decision` | List calls (`devhub_decision_list`); ADR file write outside DevHub (direct file edit not routed through `devhub_decision_record` is not logged in DevHub) |
| Change record | `change_record_plan_json`, `change_record_report_json` | List calls (`devhub_change_record_list`) |
| Project | `project_created` | None other |
| Scanners | `api_scanned`, `mcp_scanned`, `doc_scanned`, `screen_scanned` | The scanner read paths themselves; file-system traversal events |

Per pattern 79: audit-emission scope names the code paths that emit and the ones that do not. The DevHub activity log is not a per-MCP-tool-invocation log; it is a governed-write log. The Claude harness layer (the MCP transport) does not write to `activity`; only the route handler that performs the write does. Tool-invocation logging is owned by the harness, not by DevHub.

**Governing source.** `barecount-devhub/src/routes/projects.js` (activity log writes); Audit and Activity Logging.

## Constraints

| Constraint | Form |
|---|---|
| Local-only deployable | DevHub runs on the developer machine. There is no hosted DevHub. The SQLite file is the single store; no replication, no multi-writer coordination |
| Single SQLite writer | better-sqlite3 with WAL journal mode handles concurrent reads but serializes writes; concurrent decision recording is serialized at the transaction layer |
| Foreign-key enforcement | The schema declares seven explicit FK constraints at the SQLite layer (`session_checkpoints.session_id`, `decisions.project_id`, `change_records.project_id`, `plan_versions.plan_id`, `plan_references.plan_id`, `plan_approvals.plan_id`, plus one `sessions.project_id`); other cross-table linkages are by UID convention without explicit FK enforcement |
| MCP server is stdio | The MCP server is spawned by the Claude Code harness as a stdio child; there is no network MCP transport |
| Read does not log | Read calls do not write to `activity`; the trail is governed-writes only |
| ADR file write is non-fatal | If the decision-record handler cannot write the ADR file (filesystem permission, target directory missing), the registry row is still created and the failure is logged; the file is reconciled by the next `devhub_doc_scan` |
| pm2 removed | Per CLAUDE.md the pm2 service supervisor is removed; DevHub starts as a long-running `npm run dev` in its own repo with Node `--watch` for HMR |

**Governing source.** `barecount-devhub/src/db.js` (FK declarations and journal mode); `barecount-devhub/src/mcp-server.js` (stdio transport); CLAUDE.md (Dev Service Management section).

## Failure Modes

| Failure | What happens |
|---|---|
| SQLite database file missing or corrupt | DevHub server fails to start; the operator restores from a backup or runs `npm run seed` to rebuild a clean schema with seed data |
| Concurrent decision-record calls allocate the same D-code | Cannot occur: `decision_code_counter` is updated under `db.transaction()` and rows are serialized |
| ADR file write fails while registry row succeeds | Registry row is created; file is missing; next `devhub_doc_scan` flags the registry row as having no corresponding file; operator reruns `devhub_decision_record` patch path or writes the file by hand and rescans |
| Session close blocked by L-node regression | Operator inspects regression via `devhub_l_node_verify`; either fixes the regression and reruns close, or supplies a forty-plus-character `l_node_override` rationale per CLAUDE.md ("Don't" section); blocked-close state is recoverable |
| L-node gate cannot reach bc-core | Gate fails open with a warning; close proceeds; the regression detection runs again on the next session boot |
| Activity log write fails | The governed write itself succeeds; the missing `activity` row is a trail gap that surfaces in `devhub_session_get_context` review at the next session boot |
| MCP server crash mid-session | Claude harness reports the MCP error; the operator restarts DevHub; in-flight write transactions either committed or rolled back per SQLite atomicity; the session itself remains open until `devhub_session_close` is called |

**Governing source.** `barecount-devhub/src/db.js`; `barecount-devhub/src/mcp-server.js`; CLAUDE.md (Recovery Protocol section).

## Drift Inventory

These are the gaps between the substrate as documented and the substrate as implemented. Each is a real concern that the operator should know about.

| Drift item | Status |
|---|---|
| Twenty-four historical D-code duplicates | Recorded; not retroactively renumbered per `DEC-623f8f` rule 5 |
| Activity log records governed writes only; tool-invocation log is owned by the harness, not DevHub | Recorded; tool-invocation logging is a future concern owned by the harness layer |
| Read calls do not log | Recorded; per pattern 79 the chapter does not overstate audit coverage |
| Auto-scanners run on demand only, not on session boot | Recorded; the boot output's "AUTO-SCAN" section is informational, not a re-scan |
| No explicit FK between `change_records.ref_uid` and `sessions.uid` or `tasks.uid` | Soft-link by UID convention; orphaned change records can occur and are surfaced by `devhub_change_record_list` review |
| `change_records.report_json` upsert is not transaction-wrapped | Independent statements; partial-write windows exist on abrupt termination mid-call; operator reruns the close to resolve |
| Twelve-hour token TTL on the AWS profile that some MCP tools consume | Recorded; the token-renewal procedure is owned by Build and Release |
| L-node gate fail-open on bc-core or audit-endpoint outages | Recorded; infrastructure outages do not block close per `DEC-804874` |

**Governing source.** `barecount-devhub/src/db.js`; CLAUDE.md (Don't section, Recovery Protocol section).

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| Decision and Change Procedure | The ADR-first procedure (D221), the eight ADR hygiene rules (D370), the supersession-pair discipline, the change-record plan-and-report pair semantics | The DevHub registry tables and tools that the procedure writes through |
| Audit and Activity Logging | The DevHub activity log as the cross-domain governance trail; the JSONL docs trail; the bc-core operational logging | The activity-log write semantics and the per-domain event-type enumeration as DevHub-side facts |
| Quality Assurance | The bc-qa repository, the audit script, the gate-config, the eslint-config package, the pre-commit hooks | The DevHub QA NC tables and `devhub_qa_audit` MCP tool that auto-raises NCs from audit findings |
| Documentation System | bc-docs-v3 as the documentation SSOT; the bc-admin reader; bc-core JWT-served document endpoints | The DevHub document registry as a derived index; `devhub_decision_record` writing into `bc-docs-v3/docs/adrs/` |
| Operating Model: Chain Completeness and Verdict | The chain-status SSOT and the L-node semantic verdict table in bc-core | The DevHub `devhub_chain_status` and L-node MCP tools that proxy to bc-core; the session-close gate that reads them |
| Backend Services | bc-core, DevHub, bc-pg-mcp as deployable services | DevHub specifically as the engineering-coordination service |

**Governing source.** outline.md §4.5; The Authority Model.

## References

- The Authority Model
- Audit and Activity Logging
- Incident and Change Management
- Operating Model: Chain Completeness and Verdict
- Backend Services
- DEC-a4e550 (ADR-First Decision Workflow)
- DEC-633b2a (D-code monotonic allocator)
- DEC-623f8f (ADR Hygiene Policy)
- DEC-ebf0b4 (Session Discipline and Data Integrity Rules)
- DEC-804874 (L-Node Verification with Semantic Family Classification)
- DEC-3395bc (bc-docs-v3 SSOT cutover)
- CLAUDE.md (Session Protocol section, Dev Service Management section, Don't section)
