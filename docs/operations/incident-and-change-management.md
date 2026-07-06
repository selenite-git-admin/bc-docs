---
id: incident-and-change-management
order: 36
title: "Incident and Change Management"
status: drafting
authority: authoritative
depends_on: [the-authority-model, audit-and-activity-logging, observability-and-telemetry, deployment-topology, upgrade-and-migration]
governing_sources:
  - The Authority Model
  - Audit and Activity Logging
  - Observability and Telemetry
governing_adrs:
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules)
  - DEC-bebaec (Chain Completeness SSOT)
  - DEC-633b2a (D-code monotonic allocator; concurrent-session safety)
  - DEC-324d9e (Stripe billing integration; subscription and payment management from day 1)
  - DEC-ebf0b4 (Session Discipline and Data Integrity Rules; D268 self-audit at session close)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Incident and Change Management

## Scope

This chapter records the operational view of platform change governance and incident response. It states the DevHub change-record substrate (`devhub_change_record_save`) that pairs a plan with a report per session, the ISO 27001 plan-and-report discipline that every governed change honors, the session UID as the linkage between the change record and the audit substrate, the D268 self-audit discipline at session close, the L-node semantic verdict gate (the session-close gate that surfaces verifiable chain regression and may block close), the followup-task pattern that persists work across sessions, the manual incident triage path that the platform supports in the readiness baseline, and the queued surfaces (no PagerDuty, no formal incident severity model, no runbook library) that incident management at scale will demand. It records the boundary between Incident and Change Management and the audit substrate that holds the records (Audit and Activity Logging in Implementation). It records the as-built drift between the procedure and the platform's readiness-baseline incident-and-change posture.

This chapter does not redefine the audit substrate (Audit and Activity Logging), the chain completeness SSOT (Chain Completeness and Verdict), or the per-migration discipline (Upgrade and Migration).

**Governing source.** outline.md §4.7; Audit and Activity Logging.

## Change Records: The DevHub Substrate

Every governed platform change runs through DevHub's change-record surface. The pattern has two sides:

| Side | When | Form |
|---|---|---|
| Plan side | At session open or task transition to `wip` | `devhub_change_record_save` with `plan_json` (objective, approach, files_affected, risks, rollback) |
| Report side | At session close or task transition to `completed` | `devhub_change_record_save` with `report_json` (summary, files_changed, commits, verification, decisions_made, risks_identified, followup_tasks, incidents, rollback_path) |

The two sides share a `ref_uid` (the session UID `SES-xxxxxx` or task UID `TSK-xxxxxx`) and produce a single `CHG-xxxxxx` record. The record is the platform's ISO 27001 plan-and-report pair (per CLAUDE.md).

The `devhub_session_save_plan` MCP tool writes the plan-side automatically; the `devhub_session_close` MCP tool prompts for the report-side fields. A session that closes without a report-side change record is a discipline violation recorded by the next session's audit.

**Governing source.** CLAUDE.md (Session Protocol section); Audit and Activity Logging.

## Session UID as Linkage

DevHub sessions are the platform's unit of work. Each session carries a UID (`SES-xxxxxx`, six hex characters) that links to:

| Linked artifact | Form |
|---|---|
| The session row | `devhub_session_open` creates the row with project, branch, actor, started timestamp |
| The plan row | `devhub_session_save_plan` writes the plan markdown plus optional structured `plan_json` |
| Per-session checkpoints | `devhub_session_checkpoint` rows recording mid-session progress |
| The change record | `CHG-xxxxxx` paired with the `ref_uid: SES-xxxxxx` |
| Per-session activity log entries | One row per governed action (decision recording, task creation, document scan, etc.) |
| The session close summary | The `devhub_session_close` summary text plus the D268 self-audit |

The UID is the trail. An auditor reconstructing a session reads the activity log filtered by `SES-xxxxxx`, then reads the plan, the checkpoints, the change record, and the close summary.

**Governing source.** CLAUDE.md (Session Protocol section).

## D268 Self-Audit at Session Close

CLAUDE.md establishes D268 (Session Discipline) with ten rules. The discipline is enforced at session close via the `self_audit_json` parameter on `devhub_session_close`:

| Field | Form |
|---|---|
| `rules_relevant` | The D268 rules that applied this session |
| `rules_tested` | The rules where a shortcut tempted and was held; the session records the temptation |
| `near_misses` | Honest prose about close calls |
| `rules_obeyed` | True only if no rule was violated |

The self-audit *practice* is not optional — every session is expected to reflect on which D268 rules applied. The `self_audit_json` *parameter* on `devhub_session_close`, however, is optional in the MCP tool contract: per the tool schema, *"Optional — omit if you did not perform one. Do not fabricate a clean report."* The two statements are not in tension. The discipline violation is fabricating a clean report (e.g., asserting `rules_obeyed: true` against a session that violated a rule); honest absence — supplying no `self_audit_json`, or supplying one with empty `rules_relevant` and a rationale — is admitted as recorded honesty. The next session's audit reads either form as a discipline observation.

**Governing source.** CLAUDE.md (Session Discipline section); DEC-ebf0b4 (the D268 ADR titled "Session Discipline & Data Integrity Rules (NOT-TO-DO)").

## L-Node Semantic Verdict Gate

CLAUDE.md (Session Protocol step 6) records the L-Node semantic gate. The `devhub_session_close` tool runs a semantic-verdict check before accepting close:

> Per D366: If any `contract.l_node_semantic_verdict` row reached `red` during this session's window, close is **blocked** unless `self_audit_json.l_node_override` is supplied with at least 40 characters of rationale.

The gate is the platform's last-line check that a session did not regress the L-node semantic state. Legitimate override cases (recorded in CLAUDE.md): emergency fix; known-broken tenant (`demo-selenite`); migration in progress.

On override, a followup task tagged `l-node-regression` is auto-spawned; the override rationale is recorded in the change record. The gate fails-open on bc-core, Cognito, or audit-endpoint outages so that infrastructure issues do not block close.

The L-node semantic state is inspected via the `devhub_l_node_verify`, `devhub_l_node_audit`, and `devhub_l_node_refresh` MCP tools.

**Governing source.** CLAUDE.md (Session Protocol step 6); D366 (referenced in CLAUDE.md; `ADR-804874`, which documents the L-node verification with semantic-family classification).

## Followup-Task Pattern

When a session surfaces a real concern that cannot be addressed in the session itself, the platform admits the concern as a followup task via `devhub_task_add` with status `parked` or `planned`. The task row carries:

| Field | Form |
|---|---|
| Task UID | `TSK-xxxxxx` (six hex characters) |
| Project slug | The project the task belongs to |
| Status | `parked` (no schedule) or `planned` (next session candidate) |
| Tag | A free-form tag identifying the concern (e.g., `sop-gap`, `l-node-regression`, `chain-integrity`, `ddl-hygiene`) |
| Description | Prose explaining the concern and the suggested action |
| Optional `plan_uid` | Linkage to a parent plan if the followup belongs to one |

Followup tasks persist across sessions. The next session that opens against the same project sees the parked tasks at boot via `devhub_session_boot`. The discipline keeps real concerns from disappearing into session-end summaries.

**Governing source.** CLAUDE.md (Work Model section).

## Manual Incident Triage

The platform's incident triage in the readiness baseline is operator-judgment. There is no PagerDuty integration, no formal incident severity model, no on-call rotation, and no runbook library. An incident surfaces in one of three ways:

| Surface | Triage path |
|---|---|
| The chain status SSOT shows a regression | Operator reviews the SSOT (`devhub_chain_status` or the Metric Readiness UI); identifies the affected MC; routes to MC Chain Integrity diagnostic |
| A bc-ai evidence row records a high-cost or red-verdict invocation | Operator reviews the evidence; identifies the agent, the prompt, and the model; takes corrective action |
| A bc-core log line surfaces an unexpected error | Operator reads the local stdout (current local-dev posture) or the CloudWatch log group (queued for AWS deployment); identifies the request that failed |

Once triaged, the operator opens a session, runs the appropriate remediation (MC Chain Integrity walk, contract migration, schema repair, etc.), and the session's change record carries the incident-response trail.

**Governing source.** Audit and Activity Logging; Observability and Telemetry; MC Chain Integrity.

## D-Code Allocation Discipline

DEC-633b2a establishes the D-code monotonic allocator: when an ADR is recorded via `devhub_decision_record`, the allocator assigns the next D-number atomically so concurrent sessions cannot collide on the same nickname. Per CLAUDE.md, the actor never specifies `decision_code` when recording a decision; the allocator runs.

The historical record contains 24 known D-code duplicates (D210 four times, D232 four times, etc.) per CLAUDE.md. The duplicates predate the allocator. Per CLAUDE.md and per pattern (l) in the voice checklist, the canonical reference is the `DEC-xxxxxx` UID; the D-code is a human-readable nickname.

The change-management consequence: an ADR cited in a change record uses the `DEC-xxxxxx` UID, not the D-code. The D-code may appear in the change record's prose for human readability; the UID is the linkage.

**Governing source.** CLAUDE.md (D-code allocation section); DEC-633b2a.

## Aspirational Surfaces

| Surface | Form |
|---|---|
| Formal incident severity model | No SEV-1/2/3 model defined |
| On-call rotation | No on-call schedule; no PagerDuty or equivalent |
| Runbook library | No structured runbook set; per-incident actions are ad-hoc |
| Post-incident review | No formal post-incident review template; the change record's `incidents` field captures unexpected events but no separate retrospective surface |
| Status page | No public or tenant-facing status page; tenant-side incident communication is direct |
| Customer notification on incident | No automated tenant notification; Subscription notifications per DEC-324d9e (queued) would carry incident-class messages when wired |
| Change Advisory Board | No CAB; the platform's change discipline is the DevHub plan-and-report pair plus the founder approval gate per CLAUDE.md (no DB change without explicit approval) |

**Governing source.** Audit and Activity Logging; Tenant Lifecycle and Subscription.

## Failure Modes

| Cause | System response |
|---|---|
| Session close attempted without `self_audit_json` | The MCP tool admits the close with honest absence; the next session's audit reads the absence as a discipline observation |
| Session close attempted with fake clean self-audit | Discipline violation; the change-record substrate captures the close summary verbatim; later audit can compare with the session's actual activity log |
| L-node verdict regression during session | `devhub_session_close` blocks; operator either fixes the regression or supplies a 40+ character override rationale; followup task auto-spawns |
| L-node infrastructure outage | The semantic-gate fails-open; the close proceeds; the outage is recorded in the change record |
| Concurrent ADR recording | The D-code allocator atomically assigns the next D-number; no collision possible |
| Followup task forgotten across sessions | The next `devhub_session_boot` surfaces parked and planned tasks; the operator decides whether to action this session or push to a later session |
| Incident surfaces but no session opened to address it | The chain status SSOT shows the regression; the followup task pattern admits the concern; no automated incident-creation surface in the readiness baseline |

**Governing source.** CLAUDE.md (Session Protocol; D-code allocation; L-Node Semantic Gate sections).

## Drift Inventory

| Drift item | Form |
|---|---|
| No formal incident severity model | Operator judgment classifies incidents in the readiness baseline; SEV labels are informal |
| No on-call rotation | No PagerDuty or equivalent; no after-hours escalation surface |
| No runbook library | Per-incident actions are ad-hoc; the chain integrity SOP and clean-slate procedure are the closest formal procedures |
| Post-incident review absent | The change record's `incidents` field captures the event; no separate retrospective surface |
| Status page absent | No public or tenant-facing status page |
| Tenant notification on incident absent | No automated tenant alert path; tenant-side communication is direct |
| Auto-spawned followup tasks for regressions | The L-node override path auto-spawns; other regression-followup paths (chain status drop, MC count regression, AI evidence anomalies) do not auto-spawn in the readiness baseline |
| Cross-session incident continuity | The followup task pattern admits the concern; the chain status SSOT continues to show the regression; no separate incident-tracking surface aggregates the trail |

**Governing source.** Audit and Activity Logging; Observability and Telemetry.

## Boundary with Other Operations Chapters

| Chapter | Relationship |
|---|---|
| Tenant Lifecycle and Subscription | Owns the Subscription artifact; this chapter records lifecycle-state changes as governed change events |
| Deployment Topology | Owns the deploy-time change events (AuthStack updates, future PlatformInfraStack instantiation); this chapter records the change record for each |
| Security Operations | Owns the security-relevant change events; this chapter records them through the same change-record substrate |
| Upgrade and Migration | Owns the migration change events; this chapter records each migration as a governed change |
| Observability and Telemetry | Provides the substrate this chapter reads to detect incidents |
| Performance and Scale | Owns the performance regression detection; this chapter records the response |
| Support and Escalation | Owns the customer-side response; this chapter records the platform-side change |

**Governing source.** The owning Operations chapters; outline.md §4.7.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-1918d0 | Establishes the deployment and database architecture; the change-record substrate honors the two-database split (records live in DevHub, not in tenant DBs) |
| DEC-bebaec | Establishes the chain completeness SSOT; this chapter records SSOT regressions as the primary incident-detection surface |
| DEC-633b2a | Establishes the D-code monotonic allocator; the discipline applies when this chapter's change records cite new ADRs |

The L-node semantic verdict gate (D366; ADR-804874) and the D268 session-discipline rules (referenced in CLAUDE.md) govern the session-close gate this chapter records. The corresponding ADR files are present in `docs/adrs/`; the standalone ADR for D268 itself is referenced in CLAUDE.md without a directly verified ADR file in the chapter's review.

**Governing source.** Decisions: ADR Registry.

| DEC-324d9e | Establishes Stripe billing integration and subscription management from day 1; this chapter records that customer-facing notification surfaces tied to Subscription state remain queued, not active |
| DEC-ebf0b4 | Establishes the D268 Session Discipline and Data Integrity Rules; this chapter's session-protocol substrate (plan-and-report change record, self-audit at close, L-node override discipline, followup-task pattern) is the operational form of D268 |

## References

- The Authority Model
- Audit and Activity Logging
- Observability and Telemetry
- Deployment Topology
- Upgrade and Migration
- Tenant Lifecycle and Subscription
- Security Operations
- Performance and Scale
- Support and Escalation
- MC Chain Integrity
- Chain Completeness and Verdict
- DEC-1918d0: Deployment and database architecture
- DEC-bebaec: Chain Completeness SSOT
- DEC-633b2a: D-code monotonic allocator
- CLAUDE.md (Session Protocol; D-code allocation; L-Node Semantic Gate; Session Discipline sections)
- outline.md §4.7: Operations

