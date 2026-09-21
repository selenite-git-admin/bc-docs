---
title: "Structural Integrity — Document Integrity Register"
status: living
program: Structural Integrity (DEC-027ef6/D619)
anchor_task: TSK-f38fb6
date: 2026-09-21
---

# Document Integrity Register

A **running byproduct log** of the Structural Integrity program: whenever a package inspects or updates a
document, one row is recorded here. It is *not* a driver of a separate sweep — it accumulates as SI does its
normal package work, and it later **seeds a dedicated documentation-refactoring program** rather than
starting that from a blank page. It doubles as the coverage tracker and the **dead-doc finder**.

## Standing rule (operator-affirmed 2026-09-21)

> **A document must never freeze a volatile statistic.** It points to the live source, or carries an
> explicit *"snapshot as of DATE — not authority"* stamp. Chasing a frozen number to match the database is
> a treadmill; the fix is structural (point to the source), not a value update.

## Category-appropriate integrity (the check depends on the doc's category)

"Does it point to source / match code" is **not** a uniform test — a foundational doc with no code is the
*source*, not a dead doc. Per category:

| Category | What "integrity" means | Dead-doc flag applies? |
|---|---|---|
| **foundational** (invariants, execution model) | it *is* the source; check internal consistency + that code conforms to it | never |
| **SOP** (procedures) | the procedure is current (live tools/steps/paths) | only if it targets something removed |
| **design** | implemented, or explicitly marked pending/superseded | if it designs something abandoned |
| **implementation** | matches code/DB; **stats → pointers**; drift is the main risk | if it documents code that's gone |
| **reference** (data-dictionary, catalogs) | generated / points-to-source; dated | if it describes a dropped surface |
| **governance-ADR** | status truthful; supersession flipped; citations verified | n/a (decisions persist) |
| **evidence / archive** | frozen history — legitimately skipped-archival | no — it's a record |

## Disposition legend
`created` · `updated` · `partial` (owner-gated / follow-up) · `inspected` (finding, no edit) ·
`skipped-archival` · `dead` (no relevance / no code found)

## Register

| Doc | Category | Package | Disposition | What / finding | Date |
|---|---|---|---|---|---|
| `governance/adrs/ADR-027ef6.md` (DEC-027ef6/D619) | governance-ADR | SI framework | created | program execution & sequencing ADR | 2026-09-21 |
| `implementation/structural-integrity-program.md` | implementation | SI framework | created | program SSOT (map/method/matrix) | 2026-09-21 |
| `governance/adrs/ADR-fbe2c2.md` (DEC-fbe2c2/D620) | governance-ADR | SI-B-1 | created | backfilled bc-core-dashboard retirement record (had none) | 2026-09-21 |
| `governance/adrs/ADR-ce3e7a.md` (DEC-ce3e7a/D621) | governance-ADR | SI-B-1 | created | backfilled bc-core no-auth-bypass record | 2026-09-21 |
| `governance/adrs/ADR-29b518.md` | governance-ADR | SI-B-1 | updated | IntegrityService lifecycle follow-up (Amendment 1) | 2026-09-21 |
| `governance/adrs/ADR-1918d0.md` (DEC-1918d0/D162) | governance-ADR | SI-D-1 | partial (owner-gated) | delegates schema inventory to `architecture/database/schema-map.md` which is **absent** (2 surfaces: refs L16 + body L90); inline "82 tables/12 schemas" is a frozen/stale count (live 20/258). **Hand-off raised 2026-09-21 → bc-db `TSK-d3fbc0`**: owner chooses the live/spine-derived target (per DEC-4c1396/826390/489492); SI drafts the D162 errata (both surfaces + dated inline count) on the owner's decision. | 2026-09-21 |
| `CLAUDE.md` (barecount-devhub) | reference / operational-memory | SI-D-1 | updated (merged) | June-06 snapshot had **frozen** `mcf.metric_contract = 5`. **Fixed** — barecount-devhub PR #20 (merge `9f029697`): June paragraph marked dated-historical + count now **points to the live source** (`mcf.metric_contract` / `mcf.metric_contract_version` in `bc_platform_dev`), not a re-frozen number. Applied on current origin/main via a clean worktree (local `.git` had been damaged + repaired first). | 2026-09-21 |
| `reference/data-dictionary/README.md` + `contract.md` | reference (source-derived) | SI-D-1 | inspected (finding) | **source-derived** (generated 2026-07-06 @ bc-core `44767f0`), stale: no `mcf` page, still lists retired `contract.metric_contract` → **not** current authority; a regenerated/validated view is bc-db's to own. | 2026-09-21 |

## Parked — seeds for a future documentation-refactoring program
Recorded here so they are not lost; **out of scope now** (avoid doing too many things):

- **Path-portability (cloud-move readiness).** Docs, ADRs, and code comments carry **local Windows absolute
  paths** (`C:\MyProjects\...`) — e.g. `ADR-fbe2c2` references `C:\MyProjects\_archived-repos\...`. These
  break on a cloud move or a non-Windows clone. Needs a **decided convention** (repo-relative +
  a `<repo-root>` logical marker + a "local-dev" tag for genuinely-local instructions), then a sweep.
- **Frontmatter / references / links consistency** across the ~1,180-doc estate — a bounded, register-driven
  pass under that future program.
