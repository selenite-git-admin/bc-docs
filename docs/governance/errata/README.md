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

Each erratum is a separate file named `<FAMILY>-ERR-xxx.md`, where the family says what kind of source is contradicted:

| Family | Contradicted source | Resolution fields |
|---|---|---|
| `FND-ERR` | A Foundation statement | `temporary_governance` (the ADR or artifact that governs during the gap) and `target_resolution` |
| `ADR-ERR` | A stated fact or clause inside a decided ADR, without rewriting the ADR | `resolution` (what is corrected and where) |
| `GOV-ERR` | An applied-instance clause of a governance ADR that the substrate proves invalid | `temporary_governance` and `target_resolution` |
| `MCF-ERR` | A metric-context-framework implementation document | `temporary_governance` and `target_resolution` |

Common frontmatter:

```yaml
---
id: <FAMILY>-ERR-xxx
title: <one-line title>
status: open | adopted | rejected | deferred | closed
authority: authoritative
affected: <the statement, chapter, clause or ADR that is contradicted>
opened: <YYYY-MM-DD>
---
```

plus the family's resolution fields above. Body sections:

1. **Contradiction summary** — what the source says vs what the platform does or what is true
2. **Implementation behavior** — how the platform actually behaves
3. **Temporary governance** or **Resolution** — which artifact governs until resolved, or what is corrected
4. **Resolution state** — current status and expected path to closure
5. **References** — ADRs, chapters, Foundation sections, other errata

## Status lifecycle

- `open` — contradiction identified, temporary governance named, resolution not yet applied
- `adopted` — the platform's behavior is the correct behavior; Foundation will be updated to match in a future version
- `rejected` — the platform's behavior is incorrect; implementation is changing to match Foundation
- `deferred` — contradiction acknowledged, resolution postponed to a named future milestone
- `closed` — resolution applied, source of authority updated, erratum retained as historical record

## Current entries

One row per file in this directory; the frontmatter of each file is the authority for its row.

| ID | Title | Status | Affected | Governance / resolution |
|---|---|---|---|---|
| ADR-ERR-001 | D559 reference coherence over-constrained: polymorphic references have no fixed target | adopted | DEC-3d4304 (D559) — reference-kind coherence rule (typing CHECK + source-v1 grammar mir... | bc-core PR #672 (merge 3bb21a41, 2026-08-10) — three-surface amendment |
| ADR-ERR-002 | D569 overstated the authorship evidence: one SAP source contract IS authored | adopted | DEC-ea9bdc (D569) — SAP catalog contamination declaration, Rationale §2 | correction recorded here; D569's decision stands, its evidence sentence is amended |
| ADR-ERR-003 | D569 names the wrong mechanism: the SAP tables cannot be retired under the D564 expunge path | adopted | DEC-ea9bdc (D569) — title, description, and every body sentence citing the D564 carve-out | correction recorded here; D569's declaration stands, its named mechanism is superseded by DEC-e1312a (D570) |
| ADR-ERR-004 | DEC-41e4bc roster: twelve controllers amended to thirteen (UI split into Customer Portal and Admin Portal; Metrics & Onboarding renamed Metric) | adopted | DEC-41e4bc (D637) — decision point 1, the roster | operator direction 2026-09-30, recorded in the design document (barecount-devhub PR 148, artifacts/controll... |
| ADR-ERR-005 | DEC-623f8f names an enforcer that does not exist and two automations that were never built | adopted | DEC-623f8f (D370) — rule 1 (the CI enforcer's name), rule 2 (stuck-proposed task spawne... | correction recorded here; the policy's eight rules stand; the live enforcer is scripts/docs-control/audit_a... |
| ADR-ERR-006 | DEC-a4e550 names a decision-file path that no longer exists | adopted | DEC-a4e550 (D221) — Decision, the sentence "All decisions are stored as markdown files... | correction recorded here; the decision stands; ADR files live at docs/governance/adrs/ADR-{uid}.md under th... |
| ADR-ERR-007 | DEC-38b354 housekeeping roster: three of the eight agents are retired (qa-patrol, mkdocs-maintainer, registry-refresh); task-triage folded, doc-staleness kept | adopted | DEC-38b354 — the "Agents migrated" list of eight | correction recorded here; the migration decision stands; roster of record is barecount-devhub src/lib/jobs.js (Chief ruling 2026-10-01, rationale TSK-52eec7) |
| FND-ERR-001 | Observation Contract outside six-family Foundation list | adopted | Foundation §2.2 (contract families) | DEC-0e3c64, DEC-136a23, DEC-1edaaa |
| FND-ERR-002 | Reader Observation Schema dual-layer | adopted | Foundation §3.3 (admission contracts) | DEC-136a23 |
| FND-ERR-003 | Metric cardinality is N:1 (Metric Contract to Canonical Contracts) | adopted | Foundation §6 (metric evaluation) | DEC-29c324 |
| FND-ERR-004 | Source-to-Canonical cardinality is N:1 | adopted | Foundation §4.3 (canonical evaluation inputs) | DEC-97bb94 |
| FND-ERR-005 | Object count: 4 progression plus 2 proof, not 7 or 8 | adopted | Foundation §2.2 (object taxonomy) | Chapter 2 (The Invariants), Chapter 3 (The Object Model) |
| FND-ERR-006 | Evaluation boundary count: four, not five | adopted | Foundation §2.3 and Foundation evaluation-boundaries.md | Chapter 2 (The Invariants), Chapter 3 (The Object Model), Chapter 5 (The Evaluation Boundaries) |
| FND-ERR-007 | Live authority-creating families outside the grammar taxonomy | adopted | The Contract Grammar §Artifact classification; The Authority Model §Foundation authorit... | DEC-c3e57f, DEC-c48b0f, DEC-02f5a9, DEC-149ab2, DEC-b5c7ff |
| FND-ERR-008 | Legacy five-state lifecycle stated linear/no-rollback; the implementing machine was looser | adopted | The Contract Grammar §Lifecycle and deprecation policy (legacy contract-family envelope) | DEC-5a9dee |
| GOV-ERR-001 | DEC-97445d applied-instance clause (b): cross-feed registration supersession is structurally invalid | adopted | docs/governance/adrs/ADR-97445d.md (bc-docs main `4c63d79`) — Decision, applied-instanc... | bc-core metric_audit.fn_feed_registration_guard (DB guard — code is SoT for chain semantics), artifacts/met... |
| GOV-ERR-002 | DEC-97445d applied-instance clause (c): re-signing canary B is structurally impossible; the EXACT_REPROOF canary moves to a fresh subject | adopted | docs/governance/adrs/ADR-97445d.md (bc-docs main `4c63d79`) — Decision, applied-instanc... | AuditHub schema (bc_audit_dev audit_execution) — code/DDL is SoT for run/packet identity, docs/MEMO-Claude-... |
| GOV-ERR-003 | DEC-b7d74b retirement scope is broader than the evidence supports: the request lane stays | adopted | docs/governance/adrs/ADR-b7d74b.md (bc-docs main `31907fc`) — Decision, "WHAT IS RETIRE... | bc-core metric_audit.request_publication / metric-audit-request feed (code + substrate are SoT for the requ... |
| MCF-ERR-001 | First-real-M12 authorization DBCP: verdict-to-intake-status mapping is incorrect | adopted | docs/implementation/metric-context-framework-m12-first-real-run-authorization-dbcp.md (... | docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md (M12 design-blueprint; Step 8 + ou... |

## Governance of the ledger itself

Entries may be added only via a session that opens a DevHub change record. Entries may not be deleted; a closed erratum is retained as a historical record. Status changes are recorded in the erratum's frontmatter and noted in the session that applied the change.

## References

- Chapter 6 — The Authority Model (defines how the Errata Ledger fits into the authority ladder)
- Appendix F — ADR Registry (every erratum names a governing ADR)
- Foundation `system/foundation/patent/foundation-gaps.md` (v2 source for initial entries)
