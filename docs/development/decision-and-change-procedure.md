---
id: decision-and-change-procedure
order: 39
title: "Decision and Change Procedure"
status: drafting
authority: authoritative
depends_on: [the-authority-model, devhub, audit-and-activity-logging, incident-and-change-management]
governing_sources:
  - The Authority Model
  - DevHub
  - Audit and Activity Logging
  - Incident and Change Management
governing_adrs:
  - DEC-a4e550 (ADR-First Decision Workflow; ADR file is SSOT, DevHub holds metadata only, devhub_decision_record auto-generates the ADR file)
  - DEC-633b2a (D-code monotonic allocator; UID canonical, D-code nickname; concurrent-session safety)
  - DEC-623f8f (ADR Hygiene Policy; eight rules for supersession pairs, stuck-proposed audit, implementation verification, monthly audit, D-code guidance, orphan tolerance, authoring gates, quarterly sweep)
  - DEC-ebf0b4 (Session Discipline and Data Integrity Rules; the ten D268 rules)
  - DEC-804874 (L-Node Verification with Semantic Family Classification; the session-close gate per D366)
  - DEC-3395bc (bc-docs-v3 SSOT cutover; the v3 layout under docs/; ADR files written into docs/adrs/)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Decision and Change Procedure

## Scope

This chapter records the procedure for recording architectural decisions and governing change in the BareCount platform. It states the ADR-first discipline (the ADR file in `bc-docs-v3/docs/adrs/` is the source of truth; DevHub holds metadata pointing at it), the canonical UID and the nickname D-code distinction (per `DEC-633b2a`), the eight ADR hygiene rules (per `DEC-623f8f`), the change-record plan-and-report pair that ISO 27001 conformance reads against, the session-discipline rules that govern engineering session behavior (per `DEC-ebf0b4` rules one through ten), and the L-node semantic gate that runs at session close (per `DEC-804874`).

This chapter does not redefine the DevHub registry tables (DevHub), the audit substrate that holds the records (Audit and Activity Logging), or the operational triage path for incidents (Incident and Change Management).

**Governing source.** outline.md §4.5; The Authority Model.

## Architectural Decisions Are ADR Files

The platform records every architectural decision as an ADR file under `bc-docs-v3/docs/adrs/`. Per `DEC-a4e550`, the ADR file is the source of truth; the DevHub `decisions` table row is metadata that points at the file.

| Property | Form |
|---|---|
| Filename | `ADR-{shortUid}.md` where `shortUid` is the six-hex tail of the canonical `DEC-xxxxxx` UID |
| Authority | The ADR file's frontmatter `authority` field; status transitions encode the lifecycle |
| Frontmatter | `uid`, `title`, `description`, `status`, `date`, `project`, `domain`, optional `subdomain`, optional `focus`, optional `supersedes`, optional `superseded_by` |
| Body | Free-form Markdown; conventional sections are Context, Decision, and Consequences |
| Canonical reference | Body prose and code cite `DEC-xxxxxx` (the canonical UID); D-code nicknames are not used as the load-bearing identifier in a published chapter |
| File write path | The `devhub_decision_record` MCP tool both inserts the registry row and writes the ADR file at the bc-docs-v3 path; the file write is non-fatal for the registry insert |

The ADR file is the authoritative record. DevHub's `decision_text` column is deprecated content from the pre-D221 era and is not consulted. To read a decision's full context, the reader opens the ADR file.

**Governing source.** DEC-a4e550 (ADR-First Decision Workflow); CLAUDE.md (Architecture Decision Records section).

## DEC-UIDs and D-Codes

Every ADR carries two parallel identifiers per `DEC-633b2a`: a canonical UID and a monotonic nickname.

| Identifier | Form | Generation | Use |
|---|---|---|---|
| UID | `DEC-xxxxxx` (six hex characters) | Per row, generated atomically by `generateUid('DEC')` | Canonical reference in code, ADR filename, registry primary key, frontmatter `uid` |
| D-code | `D{nnn}` (monotonic decimal) | Allocated atomically by the D-code allocator under `db.transaction()`; concurrent sessions cannot collide | Human-readable nickname in conversation and in v2 SOP shorthand |

The discipline for which identifier appears where:

| Surface | Identifier |
|---|---|
| ADR filename | UID (`ADR-xxxxxx.md`) |
| ADR frontmatter `uid` | UID |
| Code, configuration, schema comments, frontmatter `governing_adrs` | UID |
| Frontmatter `governing_adrs` parenthetical (optional) | UID with optional `(D{nnn} description)` for human readability |
| Body prose in chapters | UID only (no parenthetical D-code) |
| Conversation between operators and the founder | D-code nickname |
| v2 SOP shorthand citations | D-code nickname (records reference v2 era) |

The historical registry contains twenty-four D-code duplicates from before the allocator existed (D210 four times, D232 four times, and others). Per `DEC-623f8f` rule five, those duplicates are not retroactively renumbered; the canonical UID is the load-bearing identifier and the D-code remains a nickname with known historical collisions.

`devhub_decision_record` does not accept a caller-supplied `decision_code`; the allocator runs unconditionally so concurrent sessions cannot collide on the same nickname. A caller-supplied value is silently ignored and may be rejected in a future release.

**Governing source.** DEC-633b2a (D-code monotonic allocator); `barecount-devhub/src/lib/decision-code-reconcile.js`.

## The Eight ADR Hygiene Rules

`DEC-623f8f` records eight rules for ADR lifecycle. The four enforced at commit time are the load-bearing rules; the remaining four are background discipline.

| Rule | Form |
|---|---|
| Supersession pair | When a new ADR has `supersedes: DEC-xxx` in frontmatter, the target ADR's status flips to `superseded` in the same commit; `superseded_by: DEC-yyy` is added to the target. The audit script flags any unflipped pair as a `supersessionIssues` row |
| Stuck-proposed | An ADR in `proposed` status for more than thirty days auto-spawns a DevHub task tagged `adr-stuck-proposed`; informational, not merge-blocking |
| Implementation verification | Status transitions follow draft → proposed → decided → implemented; the `closes: DEC-xxxxxx` commit token signals implementation completion; a future post-merge hook will auto-flip the status |
| Monthly audit | `bc-docs-v3/scripts/adr-audit.js` runs monthly; output is compared to the prior month; regressions open a governance task |
| D-code guidance | UIDs are canonical; D-codes are nicknames. New content uses UIDs; D-codes remain readable in conversation |
| Orphan tolerance | Zero incoming references does not auto-mark stale; the orphan count is informational; no closure pressure |
| Authoring gates | Existing gates are kept; the supersession pair check is added as a new gate; if `supersedes:` is present in frontmatter, the target ADR must exist and the status flip must be staged in the same commit |
| Quarterly sweep | A quarterly review reruns the audit, reads the top twenty orphan ADRs, and reviews retired SOPs for ADR coverage |

The audit script is `bc-docs-v3/scripts/adr-audit.js`. It is a pure diagnostic; it writes nothing. The operator runs it ad hoc; the monthly cron is a future surface owned by Operations.

**Governing source.** DEC-623f8f (ADR Hygiene Policy); `bc-docs-v3/scripts/adr-audit.js`.

## ADR Authoring with Subdomain and Focus

Per `DEC-623f8f` rule five, new ADRs carry classification axes alongside the existing `domain` field. The `devhub_decision_record` MCP tool accepts `subdomain_text` and `focus_text` arguments.

| Axis | Examples | Form |
|---|---|---|
| Domain | `architecture`, `governance`, `metric-runtime`, `source-catalog` | The platform-level domain the decision lives in |
| Subdomain | `cognito-pool`, `metric-runtime`, `source-catalog` | A free-form refinement of domain; cluster-and-normalize after a corpus accumulates |
| Focus | `infrastructure`, `lifecycle`, `schema`, `governance`, `totp` | The aspect within the subdomain the decision addresses |

The axes are free-form strings at authoring time and converge to a normalized vocabulary as the registry accumulates. Existing ADRs are backfilled during deep-triage sweeps.

**Governing source.** DEC-623f8f (ADR Hygiene Policy, classification axis section); `barecount-devhub/src/routes/decisions.js`.

## The Change-Record Plan-and-Report Pair

Every governed change runs through a change-record pair that joins planning intent with execution outcome. The pair is the ISO 27001 conformance trail.

| Side | When written | Tool | Fields |
|---|---|---|---|
| Plan side | At session open or task transition to `wip` | `devhub_session_save_plan` (auto-writes the plan) or `devhub_change_record_save` with `plan_json` | `objective`, `approach`, `files_affected`, `risks`, `rollback` |
| Report side | At session close or task transition to `completed` | `devhub_session_close` (prompts for the report) or `devhub_change_record_save` with `report_json` | `summary`, `files_changed`, `commits`, `verification`, `decisions_made`, `risks_identified`, `followup_tasks`, `incidents`, `rollback_path` |

The two sides share a `ref_uid` (a session UID `SES-xxxxxx` or task UID `TSK-xxxxxx`) and produce a single `CHG-xxxxxx` row in the `change_records` table. The shared UID is the linkage; the plan and the report are two halves of the same record.

A session that closes without the report-side change record is a discipline violation. The next session's audit at `devhub_session_boot` surfaces the gap.

**Governing source.** DEC-ebf0b4 (Session Discipline rule seven, change record at session close); `barecount-devhub/src/routes/change-records.js`.

## D268 Session Discipline Rules

`DEC-ebf0b4` records ten rules that govern engineering session behavior. The rules are platform-binding; the discipline is enforced at session close via the `self_audit_json` parameter.

| Rule | Theme |
|---|---|
| 1 | No bulk contract chain generation; chain artifacts are produced through the governed authoring sequences |
| 2 | No cosmetic status changes; status transitions reflect verified state, not desired state |
| 3 | No metadata mutation without verified source; the source of truth governs the metadata |
| 4 | One-then-many; prove the procedure on a single instance before scaling to N |
| 5 | Plan granularity matches risk; plans for risky changes record per-step intent |
| 6 | Checkpoint after every governed mutation so that crash-recovery can resume from the last verified state |
| 7 | Self-audit at session close; the discipline is recorded in the change record, not just claimed |
| 8 | Independent verification; script output is not proof, the side-effect is |
| 9 | Script output is not verification; an inspector or a re-read of the persisted state is |
| 10 | If a shortcut tempts, stop and flag it; record the temptation rather than yielding |

The self-audit at session close carries four fields: `rules_relevant` (the rules that applied), `rules_tested` (the rules where a shortcut tempted and was held), `near_misses` (close calls), and `rules_obeyed` (true only if no rule was violated). Omission of `self_audit_json` is treated as honest absence; fabrication of a clean report is the discipline violation that surfaces in subsequent audits.

**Governing source.** DEC-ebf0b4 (Session Discipline and Data Integrity Rules); CLAUDE.md (Session Discipline section).

## The L-Node Semantic Gate

`DEC-804874` records the L-node semantic verdict mechanism. The gate runs at session close per CLAUDE.md (Session Protocol step six).

| Aspect | Form |
|---|---|
| Purpose | Detect regression in chain semantic state during a session window before accepting the close |
| Substrate | The bc-core `contract.l_node_semantic_verdict` table holds per-MC L1 through L8 verdicts plus an `overall_verdict` and a `computed_at` timestamp |
| Regression definition | An overall verdict transition from `complete` or `partial` to `broken` or `unlinked` during the session window (`computed_at > session.started_ts`) |
| Block behavior | If a regression is detected and no `self_audit_json.l_node_override` is supplied, close is blocked and the MCP tool returns an error naming the regressed MCs |
| Override behavior | An override of at least forty characters of rationale is required; on override, close proceeds, a followup task tagged `l-node-regression` is auto-spawned with the regression list and break reasons, and the rationale is preserved in the change record |
| Fail-open behavior | If the gate cannot reach bc-core, Cognito, or the audit endpoint, the gate fails open with a non-blocking warning so that infrastructure outages do not block governed close |

The legitimate override cases per CLAUDE.md are emergency fix, known-broken tenant (such as the `demo-selenite` tenant during its reset cycle), and migration in progress. Casual override is a discipline violation; the override rationale is preserved in the change record and visible to subsequent audits.

The gate consumes the L-node verdict; it does not author the verdict. The verdict is authored by the bc-core L-node re-evaluation path; the per-MC inspector is `devhub_l_node_verify`, the bulk audit is `devhub_l_node_audit`, and the per-MC re-evaluation trigger is `devhub_l_node_refresh`.

**Governing source.** DEC-804874 (L-Node Verification with Semantic Family Classification); CLAUDE.md (Session Protocol step six).

## Constraints

| Constraint | Form |
|---|---|
| ADR file is canonical | The DevHub `decisions.decision_text` column is deprecated; the ADR file under `bc-docs-v3/docs/adrs/` is the authority |
| UID canonical, D-code nickname | Body prose, code, schema comments cite the UID; D-codes appear in conversation and in optional frontmatter parentheticals only |
| Caller-supplied D-code rejected | `devhub_decision_record` ignores any caller-supplied `decision_code`; the allocator runs unconditionally |
| Supersession pair commit | A new ADR with `supersedes: DEC-xxx` and the target's status flip to `superseded` land in the same commit |
| Plan before work | The plan-side change record is mandatory before any session work begins |
| Report at close | The report-side change record is mandatory at session close |
| Self-audit at close | The D268 self-audit is recorded at session close; honest absence is acceptable; fabrication is the violation |
| L-node override is rationale-bearing | An override carries at least forty characters of rationale; the rationale is preserved |

**Governing source.** DEC-a4e550; DEC-633b2a; DEC-623f8f; DEC-ebf0b4; DEC-804874; CLAUDE.md.

## Failure Modes

| Failure | Behavior |
|---|---|
| ADR file write fails after registry row insert | Registry row is created; file is missing; next `devhub_doc_scan` flags the registry row as having no corresponding file; operator writes the file by hand or reruns `devhub_decision_record` |
| Concurrent decision-record calls allocate the same D-code | Cannot occur: the allocator runs under `db.transaction()` and serializes |
| Supersession-pair commit lands without target status flip | The audit script `adr-audit.js` flags the gap on the next run; operator amends the target ADR's frontmatter and recommits |
| ADR proposed for more than thirty days | The audit script auto-spawns a `adr-stuck-proposed` task; the operator either advances the ADR to decided or closes it as reversed or superseded |
| Session close blocked by L-node regression | Operator inspects the regression via `devhub_l_node_verify`; either fixes the regression and reruns close, or supplies an `l_node_override` rationale per CLAUDE.md |
| L-node gate cannot reach bc-core | Gate fails open with a warning; close proceeds; regression detection runs again on the next session boot |
| Session closes without `self_audit_json` | Honest absence is recorded; the absence is visible in subsequent audits |
| Session closes with fabricated clean self-audit | Fabrication is the violation; subsequent audits read the change record against the actual session activity log and surface the contradiction |
| Plan-side change record absent at session start | The next session's boot output flags the gap; the operator writes the plan-side change record retroactively or accepts the discipline violation in the audit trail |

**Governing source.** DEC-623f8f (audit script); DEC-804874 (L-node gate); DEC-ebf0b4 (session discipline).

## Drift Inventory

| Drift item | Status |
|---|---|
| Twenty-four historical D-code duplicates | Recorded; not retroactively renumbered per `DEC-623f8f` rule five |
| Implementation-verification commit token (`closes: DEC-xxxxxx`) lacks an auto-flip post-merge hook | Recorded; the historical backfill script `bc-docs-v3/scripts/adr-backfill-implemented.js` reads commit messages to propose flips; the post-merge hook is queued |
| Subdomain and focus axes are free-form | Recorded; cluster-and-normalize after a corpus accumulates |
| Existing ADRs are being backfilled with subdomain and focus | Recorded; the deep-triage sweep is a long-running governance task |
| `change_records.report_json` upsert is not transaction-wrapped | Independent statements; the operator reruns the close to resolve a partial-write window |
| `change_records.ref_uid` does not have an explicit FK to `sessions.uid` or `tasks.uid` | Soft-link by UID convention; orphans surface in `devhub_change_record_list` review |
| Monthly ADR audit cron is not yet wired | Recorded; the audit script runs ad hoc; the cron schedule is a future surface owned by Operations |

**Governing source.** DEC-623f8f; CLAUDE.md.

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| DevHub | The DevHub deployable shape and the registry tables, including the `decisions`, `change_records`, `decision_code_counter`, and activity tables | The procedure that runs through those tables |
| Audit and Activity Logging | The cross-domain DevHub activity log; the JSONL docs trail; the bc-core operational logging | The activity-type events emitted by decision recording, change-record writes, session lifecycle, L-node re-evaluation, and ADR audit save |
| Incident and Change Management | The operational view of change governance and incident response; the operator-facing triage path; the followup-task pattern | The procedural side of the change-record substrate that the operational view consumes |
| Operating Model: Chain Completeness and Verdict | The chain-status SSOT and the L-node semantic verdict definition | The session-close gate that consumes the verdict at the engineering boundary |
| Quality Assurance | The bc-qa repository and the audit harness | The QA NC records that link to commits and to session UIDs through the change-record trail |

**Governing source.** outline.md §4.5; The Authority Model.

## References

- The Authority Model
- DevHub
- Audit and Activity Logging
- Incident and Change Management
- Operating Model: Chain Completeness and Verdict
- Quality Assurance
- DEC-a4e550 (ADR-First Decision Workflow)
- DEC-633b2a (D-code monotonic allocator)
- DEC-623f8f (ADR Hygiene Policy)
- DEC-ebf0b4 (Session Discipline and Data Integrity Rules)
- DEC-804874 (L-Node Verification with Semantic Family Classification)
- DEC-3395bc (bc-docs-v3 SSOT cutover)
- CLAUDE.md (Session Protocol section, Architecture Decision Records section, Session Discipline section)
