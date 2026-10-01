---
id: ADR-ERR-007
title: "DEC-38b354's housekeeping roster: three of the eight agents are retired"
status: adopted
authority: authoritative
affected: DEC-38b354 (Housekeeping Agents Migration) — the "Agents migrated" list of eight (registry-refresh, doc-staleness, session-hygiene, task-triage, nc-aging, risk-review, qa-patrol, mkdocs-maintainer)
resolution: correction recorded here; DEC-38b354's migration decision stands; three agents (qa-patrol, mkdocs-maintainer, registry-refresh) are retired from the roster, task-triage is folded into session-hygiene, and doc-staleness is kept as a light digest; the roster of record is barecount-devhub src/lib/jobs.js
opened: 2026-10-01
---

# ADR-ERR-007 — DEC-38b354's housekeeping roster: three of the eight agents are retired

## Contradiction summary

DEC-38b354 (Housekeeping Agents Migration, `implemented`, 2026-04-04) migrated eight housekeeping agents from the retired bc-ai scheduler to Claude Code scheduled tasks and lists them by name: registry-refresh, doc-staleness, session-hygiene, task-triage, nc-aging, risk-review, qa-patrol and mkdocs-maintainer. The operator, through the Chief (ruling 2026-10-01 17:17 IST; rationale in DevHub TSK-52eec7, from the Compliance and Quality assessment verified against the host and the substrate), decided that three of the eight no longer earn their keep and are retired, one is folded into another, and two are kept re-scoped. DEC-38b354's roster of eight is therefore no longer the current set.

## Implementation behavior

The current housekeeping roster, maintained in `barecount-devhub/src/lib/jobs.js` (DevHub maintains it; the Jobs screen reads it), is: session-hygiene (now also carrying the task-triage digest), nc-aging, risk-review, and doc-staleness (a light age and orphaned-citation digest routed to the Docs Controller, which the document scanner does not itself judge). The three retired agents are each superseded by a live mechanism:

- **qa-patrol** (the laptop-era cross-repository rule audit) is superseded by DEC-5b760c, which makes each repository's CI the only enforcement home, together with the bc-core `src/__architecture__` gates and the DevHub read-only Guards rule scan.
- **mkdocs-maintainer** has nothing to maintain: no `mkdocs.yml` exists in bc-docs, and the canonical reader is the bc-admin embedded reader served by bc-core at `/api/docs/*` (DEC-b97390).
- **registry-refresh** is superseded by `barecount-devhub/src/lib/codebase-fresh.js` and the DevHub scanners (code scan, document scanner, MCP tool scanner) that refresh on boot, on demand, and when a repository's main moves.

`task-triage` is not retired; its unowned-task, stale-work and priority-aging digest is folded into the session-hygiene scheduled task and lands in the Chief inbox.

## Resolution state

**Adopted as a correction; DEC-38b354 is not rewritten.** Its decision (housekeeping runs as Claude Code scheduled tasks, not the bc-ai scheduler) stands. The roster membership is governed by `src/lib/jobs.js` and this erratum, not by the ADR's original list. doc-staleness activates on the operator's Run-now of its scheduled task (TSK-2ef346).

## References

- DEC-38b354 — Housekeeping Agents Migration
- DEC-5b760c — per-repository CI is the enforcement home (supersedes qa-patrol)
- DEC-b97390 — the bc-admin embedded reader is canonical (supersedes mkdocs-maintainer)
- DevHub TSK-52eec7 — the Compliance and Quality assessment and the Chief ruling
- `barecount-devhub/src/lib/jobs.js` — the roster of record
