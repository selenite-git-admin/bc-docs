---
id: errata
title: "Errata"
status: drafting
authority: authoritative
---

# Errata

## Purpose

The Errata Ledger is the single place where governed contradictions and version-gap exceptions live. An erratum records a case in which the platform's implementation diverges from a source of authority (typically Foundation) and names the ADR or chapter that temporarily governs the divergence until a target resolution is reached.

No chapter and no ADR may introduce a silent override of Foundation. Where an override is warranted, it is recorded as an erratum here. The Errata Ledger is the only admissible form of "X takes precedence over Y until Z" within v3.

## Entry schema

Each erratum is a separate file named `FND-ERR-xxx.md` with the following frontmatter:

```yaml
---
id: FND-ERR-xxx
title: <one-line title>
status: open | adopted | rejected | deferred | closed
authority: authoritative
affected: <Foundation §, chapter, or source of authority that is contradicted>
temporary_governance: <ADR or artifact that governs during the gap>
target_resolution: <Foundation v2 section | ADR supersession | chapter rewrite | etc.>
opened: <YYYY-MM-DD>
---
```

Body sections:

1. **Contradiction summary** — what the source says vs what the platform does
2. **Implementation behavior** — how the platform actually behaves
3. **Temporary governance** — which artifact governs until resolved
4. **Resolution state** — current status and expected path to closure
5. **References** — ADRs, chapters, Foundation sections, other errata

## Status lifecycle

- `open` — contradiction identified, temporary governance named, resolution not yet applied
- `adopted` — the platform's behavior is the correct behavior; Foundation will be updated to match in a future version
- `rejected` — the platform's behavior is incorrect; implementation is changing to match Foundation
- `deferred` — contradiction acknowledged, resolution postponed to a named future milestone
- `closed` — resolution applied, source of authority updated, erratum retained as historical record

## Current entries

| ID | Title | Status | Affected | Governance |
|---|---|---|---|---|
| FND-ERR-001 | Observation Contract outside six-family Foundation list | adopted | Foundation §2.2 (contract families) | DEC-0e3c64, DEC-136a23, DEC-1edaaa |
| FND-ERR-002 | Reader Observation Schema dual-layer | adopted | Foundation §3.3 (admission contracts) | DEC-136a23 |
| FND-ERR-003 | Metric cardinality N:1 (MC to CC) | adopted | Foundation §6 (metric evaluation) | DEC-29c324 |
| FND-ERR-004 | Source-to-Canonical cardinality N:1 | adopted | Foundation §4.3 (canonical evaluation inputs) | DEC-97bb94 |
| FND-ERR-005 | Object count — 4 progression + 2 proof, not 7 or 8 | adopted | Foundation §2.2 (object types) | Chapters 2, 3 |
| FND-ERR-006 | Evaluation boundary count: four, not five | adopted | Foundation §2.3 and evaluation-boundaries.md | Chapters 2, 3, 5 |
| MCF-ERR-001 | First-real-M12 authorization DBCP: verdict-to-intake-status mapping is incorrect | adopted | metric-context-framework-m12-first-real-run-authorization-dbcp.md §4 / §8 / §10 | M12 authoring panel DBCP, M12.5 materialization DBCP, bc-core metric-authoring-panel.service.ts + metric-authoring-materialization.service.ts |

## Governance of the ledger itself

Entries may be added only via a session that opens a DevHub change record. Entries may not be deleted; a closed erratum is retained as a historical record. Status changes are recorded in the erratum's frontmatter and noted in the session that applied the change.

## References

- Chapter 6 — The Authority Model (defines how the Errata Ledger fits into the authority ladder)
- Appendix F — ADR Registry (every erratum names a governing ADR)
- Foundation `system/foundation/patent/foundation-gaps.md` (v2 source for initial entries)
