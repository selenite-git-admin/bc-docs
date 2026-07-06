---
id: developer-experience
order: 43
title: "Developer Experience"
status: drafting
authority: authoritative
depends_on: [the-authority-model, devhub, decision-and-change-procedure, build-and-release, quality-assurance, documentation-system]
governing_sources:
  - The Authority Model
  - DevHub
  - Decision and Change Procedure
  - Build and Release
  - Quality Assurance
  - Documentation System
governing_adrs:
  - DEC-e50b83 (Port reservation; per-service reserved port ranges; the table is reproduced in CLAUDE.md and the deploy-coordinate detail is owned by Infrastructure)
  - DEC-1918d0 (Two-database split; the canonical DDL and the database change protocol)
  - DEC-3395bc (bc-docs-v3 SSOT cutover; the agent reads bc-docs-v3, not legacy v2 archive)
  - DEC-ebf0b4 (Session Discipline and Data Integrity Rules; the ten rules govern engineering session behavior)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Developer Experience

## Scope

This chapter records the developer-experience substrate as the platform's engineering team consumes it: the per-repo CLAUDE.md files that govern Claude Code agent behavior, the SOP catalog under legacy v2 archive that records recurring procedures, the .claude harness directory in barecount-devhub that holds launch configurations and worktree directories, the MCP server registration in `.claude/settings.json`, the worktree harness that lets multiple sessions run concurrently, the port reservation discipline that governs which service binds where, the verification tool surface that the agent uses to render and read the running platform, the AWS profile discipline, the database change protocol, and the session protocol that every Claude session honors.

This chapter does not redefine the DevHub MCP tool surface (DevHub), the change-record substrate (Decision and Change Procedure), the build commands (Build and Release), the QA tooling (Quality Assurance), or the documentation surface (Documentation System).

This chapter does not name specific port numbers, AWS account identifiers, AWS profile names, or AWS region codes. Those deploy coordinates are owned by Infrastructure and Operations: Deployment Topology per pattern 85.

**Governing source.** outline.md §4.5; The Authority Model.

## CLAUDE.md as the Per-Repo Agent Instruction Surface

Every platform repo that the Claude Code agent operates against carries a `CLAUDE.md` file at the repo root. The file records repo-specific instructions: the platform-wide rules that always apply (session protocol, change-record discipline, voice discipline), the repo-specific commands and conventions, and the repo-specific gotchas the agent must observe.

| Repo | CLAUDE.md role |
|---|---|
| `barecount-devhub` | The master harness; records the platform-wide session protocol, the SOP compliance discipline, the dev-service management model, the port reservation table, the AWS profile discipline, the database change protocol, the QA coding standards, and the don't-list |
| `bc-core` | NestJS-specific instructions: docker compose for postgres and redis; canonical DDL location; Drizzle and migration paths; tenancy header conventions; testing harness commands |
| `bc-admin` | React and Vite specifics: dev server command; sync-docs procedure for the embedded reader; tenant-platform scope rules; component conventions |
| `bc-portal` | Customer-frontend specifics |
| `bc-ai` | Python uvicorn specifics; the Python rule set (ruff, mypy strict) |
| `bc-qa` | QA tooling specifics; the audit-runner invocation; the gate-config layout |

The barecount-devhub CLAUDE.md is the master harness because every Claude session opens against barecount-devhub first (per the session protocol). The per-repo CLAUDE.md files inherit the master rules and add repo-specific surface.

The CLAUDE.md files are committed; the agent reads them at session start and treats them as instructions. A drift between CLAUDE.md and the actual repo state is a discipline violation: the file is the agent's instruction surface, and an instruction that does not match reality misleads the agent.

**Governing source.** Per-repo `CLAUDE.md` (barecount-devhub master, bc-core, bc-admin, bc-portal, bc-ai, bc-qa).

## The SOP Catalog

The Standard Operating Procedures live under `legacy-v2/docs/sops/` (twenty SOP files in the v2 archive). Each SOP records a recurring procedure: source registration, seed catalog management, metric registration, contract creation, data seeding, demo execution, and similar.

| Core SOP | Scope |
|---|---|
| `source-registration-sop.md` | Register a system, add tables, add fields (manual-and-AI plus programmatic paths) |
| `seed-catalog-sop.md` | Add or enrich systems in the MongoDB seed catalog (programmatic only) |
| `metric-seed-catalog-sop.md` | Add or enrich metrics in the MongoDB seed catalog (programmatic only) |
| `metric-registration-sop.md` | Register metrics from seed to platform with AI gates (manual-and-AI plus programmatic) |
| `data-seeding-sop.md` | Contract chain build order |

Per CLAUDE.md, every Claude session that performs a recurring procedure first checks whether an SOP exists, then follows it step by step. SOP deviation is recorded explicitly (which step was skipped, why, what was done instead) via `devhub_session_checkpoint`. SOPs that are missing are flagged via `devhub_task_add` with tag `sop-gap`.

The SOPs have not yet been migrated from legacy v2 archive to bc-docs-v3. Per Documentation System the migration is queued; until then the v2 archive is the canonical SOP surface and the agent reads against the v2 path.

**Governing source.** CLAUDE.md (SOP Compliance section); `legacy-v2/docs/sops/`.

## The .claude Harness Directory

The Claude Code harness state for the barecount-devhub repo lives under `.claude/`. The directory holds the configuration that lets multiple Claude sessions coexist, the MCP server registrations, and the per-session worktree directories.

| Path | Form |
|---|---|
| `.claude/settings.json` | The shared settings, including MCP server registration |
| `.claude/settings.local.json` | The local-only settings (not committed) |
| `.claude/launch.json` | Per-service launch configurations; the worktree harness reads this for service start commands |
| `.claude/api-reference.md` | The DevHub API reference, read on demand |
| `.claude/tool-guide.md` | Per-tool guidance for the agent (Bash on Windows discipline, etc.) |
| `.claude/worktrees/` | Per-session worktree directories, each named after a session-specific identifier |
| `.claude/plans/` | Plan documents the agent has staged for review |

A worktree is a git worktree that a Claude session can attach to so that multiple sessions can edit the same repository concurrently without trampling each other. The worktree harness creates a worktree per session, names it with a session identifier, and removes it when the session closes.

**Governing source.** `barecount-devhub/.claude/`; CLAUDE.md (Verification, Don't sections).

## MCP Server Registration

Two MCP servers are registered in `barecount-devhub/.claude/settings.json` for Claude session consumption.

| Server | Purpose | Form |
|---|---|---|
| `bc-postgres` | Read-only PostgreSQL access for the agent (`pg_query`, `pg_count`, `pg_describe_table`, `pg_list_tables`, `pg_list_indexes`, `pg_list_schemas`, `pg_server_info`) | A node-spawned stdio server at `C:/MyProjects/bc-pg-mcp/dist/index.js`; the database URL, schema set, row cap, and output format are configured through environment variables |
| `devhub` | The DevHub MCP server | A node-spawned stdio server that proxies to the DevHub HTTP API at the reserved DevHub port |

The MCP servers are spawned by the Claude Code harness as stdio children. Per pattern 71: the agent observes the MCP servers' behavior, not just their names. The `bc-postgres` row cap and the schema allowlist are configurable knobs whose precise enforcement scope is documented in Backend Services: the `PGMCP_SCHEMAS` allowlist applies to schema-aware tools and configured introspection surfaces (it is NOT a parser for arbitrary SQL in `pg_query`), and the `PGMCP_MAX_ROWS` cap appends a `LIMIT` clause only when the client query has none (it does NOT override an explicit `LIMIT` already in the SQL). The substantive read-only guarantees come from the three composed layers in `pg_query` itself — the runtime-side SQL guard, parameterized execution, and PostgreSQL's `default_transaction_read_only=on` connection setting — as detailed in the bc-pg-mcp Behavior section of Backend Services. The DevHub MCP transport is the engineering-coordination registry surface.

The MCP server registration is per-repo; only barecount-devhub's `.claude/settings.json` records the platform-wide servers. Other repos may carry their own `.claude/settings.json` with repo-specific MCP entries; the platform discipline is to keep platform MCP servers in the master harness and avoid per-repo divergence.

**Governing source.** `barecount-devhub/.claude/settings.json`; `bc-pg-mcp/`; DevHub.

## The Worktree Harness

A Claude session can spawn a git worktree to operate against an isolated copy of the repository. The worktree harness registers the worktree under `.claude/worktrees/`, names it with a session-specific identifier (a memorable string and a hex tail), and provides launch configurations through `.claude/launch.json`.

| Launch entry | Purpose |
|---|---|
| `devhub` | DevHub server with Node `--watch` for HMR |
| `bc-core` | bc-core NestJS server |
| `bc-portal` | bc-portal Vite dev server |
| `bc-admin` | bc-admin Vite dev server |
| `intra-site` | An internal site dev server |
| `bc-core-dashboard` | The bc-core operational dashboard surface |

Each launch entry names the working directory, the start command, and the reserved port that Infrastructure assigns. Reserved ports are owned by Infrastructure per `DEC-e50b83`; the launch.json simply names the entry the harness invokes.

When the session closes, the worktree is either removed (if no changes) or preserved for review (if changes are staged). The harness handles cleanup automatically; the operator does not run worktree commands directly.

**Governing source.** `barecount-devhub/.claude/launch.json`; DEC-e50b83 (Port reservation; deploy-coordinate detail in Infrastructure).

## Verification Surface

The agent verifies UI and runtime changes by attaching to the running services. The verification surface is the platform's "see what the running code does" capability.

| Tool family | Form |
|---|---|
| Preview tools | The harness exposes `preview_*` tools (`preview_start`, `preview_eval`, `preview_snapshot`, `preview_click`, `preview_screenshot`, `preview_console_logs`, `preview_logs`, `preview_network`, `preview_resize`) that attach to a running service via the launch.json entry |
| Playwright (native) | Available with the `--browser msedge` flag; Chrome conflicts with the user's active session |
| Direct API call | `node -e "fetch(...)"` for backend-only checks; `npx vitest run` for unit tests |
| Browser snapshot | The agent prefers structural snapshot over screenshot; screenshots are reserved for visual proof |

Per pattern 88: the verification surface is a set of tools, not a universal "always preview" rule. The agent picks the right tool for the change: preview tools for UI changes, direct API calls for backend-only changes, unit tests for type-and-shape changes.

A drift item exists in CLAUDE.md regarding preview tools: the master harness CLAUDE.md text states "Do NOT use `preview_*` tools" while the auto-memory note records that the preview tools were validated post-pm2-removal and are usable. The text is stale; the auto-memory is current. The agent reads the auto-memory as the operative guidance and surfaces the contradiction so that the next CLAUDE.md amendment lands. This drift is recorded in the inventory below.

**Governing source.** CLAUDE.md (Verification section); auto-memory operational checklist.

## Port Reservation Discipline

Per `DEC-e50b83`, every BareCount local-development service binds to a reserved port. The discipline prevents two services from contending for the same port and gives the agent a deterministic place to look for each service.

The port reservation table is reproduced in `barecount-devhub/CLAUDE.md` for agent reference; the canonical table lives in `DEC-e50b83`. Specific port numbers, the per-service binding, and the per-environment variation are deploy coordinates owned by Infrastructure per pattern 85; this chapter records the discipline (every service has a reserved port; the table is the source of truth) and routes the figures to the owning chapters.

**Governing source.** DEC-e50b83 (Port reservation); Infrastructure.

## AWS Profile Discipline

Every BareCount service that consumes AWS APIs uses a single named profile. The profile name, the AWS account identifier, and the region are deploy coordinates owned by Infrastructure per pattern 85; this chapter records the discipline.

| Aspect | Form |
|---|---|
| Single profile | One named profile is the only authorized AWS profile for BareCount development; the agent does not consume the default profile |
| `bc-core` `.env` | Carries the profile name as an environment variable that bc-core reads at startup |
| CLI invocation | The operator sets `AWS_PROFILE=...` before running `aws codeartifact login`, `aws s3 ls`, or any other AWS CLI call |
| Drift consequence | Using the default profile points at the wrong account; the agent surfaces the misconfiguration immediately and refuses the operation |

The profile is the platform's account isolation. Per CLAUDE.md, the discipline is mandatory; the agent does not bypass it.

**Governing source.** CLAUDE.md (AWS section); Infrastructure (deploy coordinates).

## Database Change Protocol

Per CLAUDE.md (Database Change Protocol section), no database change runs without explicit user approval. The protocol overrides every permission mode the harness can be in; even in `Bypass permissions` mode the agent does not execute a database change without approval.

| Step | Form |
|---|---|
| 1 | Present the change to the user with: target table, what changes, why |
| 2 | Wait for explicit approval (the user types "yes", "go", or equivalent) |
| 3 | Only then execute |

The protocol applies to: adding, removing, or renaming tables or columns; changing column types, constraints, defaults, or indexes; adding or modifying Drizzle schema definitions; creating or modifying migration files; changing seed data structure (not content); modifying the canonical DDL files under `bc-core/docker/redesign/`.

Per `DEC-1918d0`, the canonical DDL is the source of authority for the schema; the Drizzle schemas track the canonical DDL; the migrations directory contains evolution files that fold back into the canonical DDL on the queued schedule.

**Governing source.** CLAUDE.md (Database Change Protocol section); DEC-1918d0.

## Session Protocol Adherence

Every Claude session honors the six-step session protocol per CLAUDE.md (Session Protocol section). The protocol is recorded in detail by Decision and Change Procedure; this chapter records the developer-experience surface.

| Step | Tool |
|---|---|
| Boot | `devhub_session_boot` |
| Research | `devhub_decision_list`, `devhub_task_list`, `devhub_plan_read`, `devhub_session_get_context` |
| Open | `devhub_session_open` |
| Plan | `devhub_session_save_plan` (mandatory before any work) |
| Work | `devhub_session_checkpoint` at every governed mutation; `devhub_task_add` and `devhub_task_update` for task tracking |
| Close | `devhub_session_close` with the D268 self-audit; the L-node semantic gate may block close if a regression is detected |

Per `DEC-ebf0b4`, the ten session-discipline rules govern session behavior. The four rules with the strongest developer-experience surface: rule four (one-then-many; prove on a single instance before scaling), rule six (checkpoint after every governed mutation), rule seven (self-audit at session close), rule ten (if a shortcut tempts, stop and flag it).

**Governing source.** CLAUDE.md (Session Protocol section); DEC-ebf0b4; Decision and Change Procedure.

## The Cold-Read and Founder-Review Cycle

The agent drafts; the founder cold-reads. The cold-read produces `_opt2.md` files alongside the canonical chapter; the agent diff-validates the `_opt2.md` against the canonical, debates substantive contradictions before promoting, and lands the cold-read corrections plus carry-along fixes in a follow-up commit.

| Channel | Form |
|---|---|
| `_opt2.md` channel | Founder writes the cold-read corrections in a parallel file with the same name plus an `_opt2.md` suffix; the agent promotes after diff-validate-then-debate |
| Bullet-form channel | Founder lists corrections in conversation; the agent applies the corrections in place |

The cold-read is the gate that flips a chapter from `drafting` to `reviewing`; locking requires founder approval. The pattern is established and is recorded in the AWS rewrite checklist under multiple patterns (the most relevant: pattern 87 for section-overview locating discipline, pattern 88 for universal-claim per-instance enumeration).

**Governing source.** bc-docs-v3 `HANDOFF.md` (drafting workflow section); aws-rewrite-checklist.md.

## Constraints

| Constraint | Form |
|---|---|
| Single agent instruction surface per repo | One CLAUDE.md per repo; platform-wide rules in barecount-devhub's master, repo-specific in each repo's |
| One MCP harness | `barecount-devhub/.claude/settings.json` is the master MCP registration |
| Worktree per session | Each Claude session attaches to its own worktree; concurrency is preserved through worktree isolation |
| Port reservation mandatory | Every service binds to its reserved port per `DEC-e50b83`; the deploy-coordinate detail is owned by Infrastructure |
| AWS profile discipline | A single named profile; the default profile is rejected |
| Database changes are user-approved | The override of every permission mode |
| Session protocol mandatory | Every session boots, researches, opens, plans, works, and closes through the DevHub MCP tools |
| ADR-first | Every architectural decision lands as an ADR file before code changes |
| One-then-many | Discipline rule four; bulk operations are forbidden until a single-instance proof exists |

**Governing source.** CLAUDE.md (Don't section, Session Protocol section, Database Change Protocol section, AWS section); DEC-e50b83.

## Failure Modes

| Failure | Behavior |
|---|---|
| Agent reads stale CLAUDE.md instruction | The agent surfaces the contradiction (real vs CLAUDE.md) and asks the operator before proceeding; the CLAUDE.md amendment lands as a follow-up |
| Worktree is not cleaned up after session close | The harness has a stale-worktree sweep at the next session boot; the operator can also remove the worktree directory by hand |
| Two sessions allocate the same worktree name | The harness names worktrees with a session-specific suffix to prevent collision |
| MCP server fails to start | The agent surfaces the failure; the operator restarts the server and reruns the failing tool |
| Database change attempted without user approval | The agent halts and asks for approval; the discipline override prevents the change |
| AWS CLI invocation runs against the default profile | bc-core fails to authenticate against the platform AWS account; the agent re-runs with the named profile |
| Session close is blocked by the L-node gate | Operator inspects the regression via `devhub_l_node_verify`; either fixes or supplies an `l_node_override` rationale |
| Founder cold-read produces an `_opt2.md` that contradicts the canonical | The agent diff-validates against the actual code; substantive disagreements are surfaced as debate items before promotion |

**Governing source.** CLAUDE.md (Recovery Protocol section); DevHub; Decision and Change Procedure.

## Drift Inventory

| Drift item | Status |
|---|---|
| CLAUDE.md `preview_*` instruction is stale | Recorded; auto-memory operational checklist supersedes; CLAUDE.md amendment is queued |
| SOPs have not been migrated from legacy v2 archive to bc-docs-v3 | Recorded; queued per Documentation System |
| `bc-core-dashboard` and `bc-core` launch.json entries are stubs | Recorded; pending full pm2 removal completion |
| Per-repo CLAUDE.md files have not been audited for consistency with the master harness | Recorded; periodic audit is queued |
| Worktree cleanup on abrupt session termination relies on the next session's sweep | Recorded; the harness cleanup is best-effort |
| Auto-memory file lives outside the committed repo (in the operator's user profile) | Recorded; the auto-memory is local to the developer machine and does not propagate across operators |

**Governing source.** CLAUDE.md (Verification section); bc-docs-v3 `HANDOFF.md` (drift inventory section).

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| DevHub | The MCP tool surface and the registry tables | The agent's consumption of the MCP tools |
| Decision and Change Procedure | The session protocol details, the change-record substrate, the D268 discipline rules | The developer-experience surface that follows the protocol |
| Build and Release | The per-repo dev commands and the CodeArtifact registry | The launch.json entries that invoke the per-repo dev commands |
| Quality Assurance | The pre-commit hook, the audit harness, the eslint-config | The developer-machine pre-commit installation procedure |
| Documentation System | bc-docs-v3 SSOT, the bc-admin reader, the sync-docs script | The agent reading documentation as part of session research |
| Infrastructure | Reserved port assignments; AWS account, region, profile, IAM | The discipline of consuming reserved ports and named profiles without naming the values |

**Governing source.** outline.md §4.5; The Authority Model.

## References

- The Authority Model
- DevHub
- Decision and Change Procedure
- Build and Release
- Quality Assurance
- Documentation System
- Infrastructure
- DEC-e50b83 (Port reservation)
- DEC-1918d0 (Two-database split; Database Change Protocol authority)
- DEC-3395bc (bc-docs-v3 SSOT cutover)
- DEC-ebf0b4 (Session Discipline and Data Integrity Rules)
- CLAUDE.md (Session Protocol section, Don't section, AWS section, Database Change Protocol section, Verification section)
- bc-docs-v3 `HANDOFF.md` (current drafting state, drafting workflow)
