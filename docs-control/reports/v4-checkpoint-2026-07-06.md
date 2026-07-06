# v4 Checkpoint - 2026-07-06

This checkpoint records the isolated `bc-docs-v4` state after the first control-plane, coverage, navigation, source-reference, and mutable-claim cleanup pass.

## Safety Boundary

- `bc-docs-v3` remains untouched.
- Claude-facing v3 references are intentionally not cut over.
- Remaining `bc-docs-v3` references are deferred until active Claude sessions are stopped and the cutover is explicitly approved.
- Legacy repository deletion/rename work has not started.
- Named legacy documentation roots are already staged under `bc-docs-safe-delete`; inventory is report-only and physical deletion remains blocked on explicit approval.

## Gate Snapshot

| Gate | Status |
|---|---|
| Target documents registered | 977 |
| Audit errors/blockers | 0 |
| Broken-link findings | 0 |
| Generated references pending regeneration | 0 |
| Mutable-claim review lines | 0 |
| Latest target-audit run | 75 |
| bc-core coverage | 1107/1107 linked targets |
| Reader navigation | 210 visible, 760 hidden |

## Coverage Snapshot

| Target Type | Targets | With Links | Without Links |
|---|---:|---:|---:|
| config | 7 | 7 | 0 |
| controller | 105 | 105 | 0 |
| module | 59 | 59 | 0 |
| schema | 193 | 193 | 0 |
| script | 573 | 573 | 0 |
| service | 170 | 170 | 0 |

## Audit Snapshot

| Severity | Category | Findings |
|---|---|---:|
| warning | stale-doc-root-reference | 33 |
| info | stale-doc-root-reference | 228 |

## Remaining Queues

1. Defer v3 cutover references: 261 remaining legacy-root mentions are intentionally left until active Claude sessions are stopped and cutover is explicitly approved. The generated cutover-reference plan separates 33 warning/current-visible references from 228 informational provenance references.
2. Preserve generated references and bc-core coverage as `bc-core` evolves.
3. Keep source-system vendor facts out of static pages; tenant-specific limits, licensing, and verification terms belong in onboarding evidence.
4. Run the later external reference scan before physical deletion of `bc-docs-safe-delete` contents.
5. Use the external legacy-reference scan as the repoint input for other repos: 4,470 project-repo matches, including 1,222 code/config references, 2,157 served-doc-copy references, and 354 Claude handoff/memory references.
6. Build the later cutover report before any rename from `bc-docs-v4` to `bc-docs`.

## Reports

- `docs-control/reports/cleanup-queue.md`
- `docs-control/reports/bc-core-coverage.md`
- `docs-control/reports/navigation-report.md`
- `docs-control/reports/mutable-claim-review.md`
- `docs-control/reports/source-system-volatility-sanitization-report.md`
- `docs-control/reports/cutover-reference-plan.md`
- `docs-control/reports/legacy-documentation-retirement-inventory.md`
- `docs-control/reports/external-legacy-reference-scan.md`

## Worktree State

The v4 tree is still uncommitted and untracked as an isolated build product. This is intentional until the structure stabilizes and the user approves a repository checkpoint or commit.
