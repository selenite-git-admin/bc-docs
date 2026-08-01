# Errata 03 — repo relocation (bc-pilot → bc-sdg/pilots)

**To:** Codex (auditor). **Date:** 2026-07-31.
**Applies to:** the review package accepted 2026-07-31, which cited the world engine as
**`bc-pilot @9f1cc8c`** (doc B).

## Change (address only — content unchanged)

The standalone **`bc-pilot`** repo has been **retired** and its content **folded into
`bc-sdg/pilots/`** (same day, one day after creation). New location:

- **`bc-sdg/pilots/ @8849c2e`** (github: `selenite-git-admin/bc-sdg`, private) —
  `pilots/profiles/mfg-in/` + `pilots/systems/odoo/`. Files moved as git **renames**
  (history preserved); the fail-closed doctrine correction that was `bc-pilot @9f1cc8c` is
  carried in. The `bc-pilot` GitHub repo is deleted.

**Nothing Codex inspected changed** — same profiles × systems structure, same engine, same
gate scripts, same profile artifacts. Only the repository address moved. Re-verify at
`bc-sdg/pilots/ @8849c2e` if desired.

## Why (so the reasoning is on record)

The separate `bc-pilot` repo bought **none** of the benefits that justify a repo boundary —
no independent deploy (dev tooling run on EC2), zero dependencies, same owner — while adding
the cross-repo coordination cost we had already learned hurts (cf. `bc-ai`, split then
reverted into bc-core). Principle adopted: *name the specific repo-benefit you're buying, or
use a directory.*

**The one boundary that IS kept** is the meaningful one: `bc-sdg` (the synthetic-source lab —
both `src/simulators/` shapes and `pilots/` real-vendor worlds) stays separate from
**`bc-core`** (the platform). Data-fabrication tooling must never live in the production
evaluation engine — the platform's trust model ("source is authoritative; SDG is not the
source") depends on that separation. The reader that consumes these worlds remains in bc-core.

## Impact on the disposition
**None to the findings or gates (G1/G2/G3).** All references to `bc-pilot` in the design
docs now read `bc-sdg/pilots/`; the pinned review artifacts (immutable) retain the
`bc-pilot @9f1cc8c` reference with this relocation note attached.
