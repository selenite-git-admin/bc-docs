---
uid: DEC-41e4bc
title: "Session protocol for controllers: roster, responsibility map, work binding, review ledger, close gates, daily seal"
description: "The controller fleet's rules move from memory and instructions into DevHub gates and detectors, built in phases 0–4."
status: decided
date: 2026-09-30T08:04:02.240Z
project: barecount-devhub
domain: devhub
subdomain: devhub/session-protocol
focus: governance
---

# Session protocol for controllers: roster, responsibility map, work binding, review ledger, close gates, daily seal

## Context

The operator's concern (2026-09-30): about a dozen controllers and their workers depend on memory and instructions, so a forgotten review, handoff or thread becomes a timebomb that no later controller has the context to catch. Verified at barecount-devhub cfe3a60a:
- session open records only project and branch (src/routes/projects.js:154-166);
- close has one gate, chain status, only in the MCP layer (src/mcp-server.js:379,464), while PATCH closes with no gate (src/routes/projects.js:184-230);
- review state exists only for plans (src/db.js:326-330);
- tasks and plans have no owner (src/db.js:75-87,138-145);
- no Claude Code hooks exist;
- DevHub runs node --watch with no liveness probe and no launchd supervision.

Principles: guard the class; detect, don't trust self-report; visible overrides; one source of truth; agents lift and controllers verify.

**Review:** Codex, gen-8ce4fa, three rounds.
- Round 1: changes required (self-reported inventory; unproven reviews).
- Round 2: changes required (identity; memory in phase 4; unverified passing).
- Round 3 (operator grant cc4978fb): memory and unverified resolved; review identity for ordinary documents left to the operator, who chose option C.

**Operator grants:**
- 2026-09-30T07-52-42-774Z-8c4753bf (decisions), text SHA-256 8c4753bf7f21d49a8ec204fbe53e6037de477ea764f09da661da19633f3e5cf4;
- 2026-09-30T07-53-08-183Z-cc4978fb (third round), text SHA-256 cc4978fb522d4421288606be17ae877dd99fed10e65f838338624a03cedbe373;
- 2026-09-30T08-03-18-236Z-64db9578 (option C), text SHA-256 64db9578b8942495af24d0e8050647a53646c4affbad1319dbcd1d522f76a03a.

**Named residuals:** same-user processes outside Claude can write memory (detected after the fact and forced to attribution); an attested-only acceptance is unproven for up to about one working day, and labelled so.

## Decision

BareCount work runs as a fleet of controller sessions with short-lived workers. Its rules are enforced by DevHub, not by memory or instructions. The authoritative design is barecount-devhub PR 148, artifacts/controllers/DESIGN-session-protocol-controllers-2026-09-30.md at head 70f5cf35.

1. **Roster.** Twelve controllers as DevHub data: Chief, Architect, Platform, Metrics & Onboarding, DB, DevHub, UI, Infra & CI, Audit, Docs, Demo, Compliance & Quality.
2. **Responsibility map.** Each area has an owner, reviewers by output kind, and an escalation path, with a lookup tool and a boot display. Escalation runs worker → its controller → the area's owner → Chief → operator (authority only). An unmapped area goes to the Chief.
3. **Sessions.** Every session declares a role (controller or worker); a worker names its controller. Every session is bound to one task before it changes anything; undefined work opens a self-opened task owned by its controller. Worker results land as handoffs in the controller's inbox.
4. **Ownership.** Every task and plan has an owning controller: the column is staged nullable, then backfilled in a reviewed batch, then enforced. History (terminal tasks, plans, sessions, ADRs) is backfilled with an owner_basis_code, so inferred ownership is never shown as fact. Transfers go directly between controllers with accept or decline; the Chief takes them after 24 hours.
5. **Operator entry points.** The operator talks to the Chief and the controllers, never to workers. Operator directions are recorded in DevHub; grants stay on the desk.
6. **Review ledger.** Every durable output is a deliverable, with an immutable required-reviewer snapshot and verdicts bound to its content SHA-256. What a session changed comes from an independent inventory: Session: trailers on commits, git log --all plus reflogs, and a memory-write log with snapshots; the report must reconcile with it. Codex and operator verdicts are derived by DevHub from committed replies and exact-template grants, never written by sessions. Controller verdicts are labelled attested. Governing kinds (adr, design, skill_text, sop) need an authenticated verdict (Codex or operator). Attested-only acceptances of other kinds are sealed daily by one operator grant (option C).
7. **Close** is one server-side route. Async gathering runs outside any transaction; then one short synchronous better-sqlite3 transaction re-checks and writes. It gates on the report, deliverables, open gen- threads, controller self-audit, worker handoff and chain status. `unverified` never passes. The PATCH close path is removed.
8. **Hooks.** User-level Claude Code hooks: layer 1 blocks a first prompt outside barecount-devhub; layer 2 (phase 4) is the work gate. A narrow memory-write hook ships in phase 2.
9. **Availability (phase 0).** No --watch; a liveness restart; launchd for process-compose; an outage watchdog with a Slack alert after 2 minutes and a stop flag after 10 minutes; incidents reconciled after recovery.
10. **Daily rhythm.** The Chief runs a start-of-day and a wind-down with the operator. Slack #chief-daily is one-way, and the operator answers in the Claude app.

**Phases:** 0 availability; 1 roster, map, roles, ownership, binding, transfers; 2 ledger, inventory, close, memory hook; 3 briefs and full sweep; 4 work gate. Each phase needs the operator's separate database approval.
