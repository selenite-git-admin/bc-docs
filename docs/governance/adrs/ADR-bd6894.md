---
uid: DEC-bd6894
title: "Order of live changes on the platform: number-order migration applies, joint DDL + code windows, no code ahead of its DDL"
description: "Live platform migrations apply in number order (dispositions for skipped ones); coupled DDL and code go live in one window; no serve build contains code for unapplied DDL; such code merges only after its migration is live."
status: reversed
date: 2026-09-30T12:40:38.656Z
project: platform
domain: platform
subdomain: platform/live-operations
focus: live change order
---

# Order of live changes on the platform: number-order migration applies, joint DDL + code windows, no code ahead of its DDL

## Withdrawn (2026-11-16)

The operator withdrew this ADR on 2026-11-16 while it was still `proposed`. It was never decided and never in force. The status value `reversed` is used only because the ADR status vocabulary (`proposed`, `decided`, `implemented`, `superseded`, `reversed`) has no value for a withdrawal. The recorded desk grant is `2026-11-16T10-15-16-479Z-539245b2` (text SHA-256 `539245b2042a2cf28d65304fdc4d6ea75fe92e72c56480c9077c75d50f5cc555`).

What becomes of the four parts of the Decision below:

1. **Part 1 (number order): not a rule of the platform.** The ledger already departs from it, and no rule replaces it.
2. **Part 2 (one window).** It stands in section 5 of the Operations definition (`docs/development/platform-refactor-program/definition-operations.md`) only as far as its words go: a migration "is applied in the same window in which that code is served". The ADR’s further words (schema first, then the build; one grant naming both; both roll back on a failure) are not carried anywhere and end with this ADR.
3. **Part 3 (no served build carries code for schema that is not applied).** It stands as step 1 of a serve move in section 3 of the same definition: "The build needs no schema change that is not applied."
4. **Part 4 (code that needs a migration merges only after that migration is live): not carried.** Section 5 states a different rule, "A migration is merged only together with, or after, the engine code that needs it", and that is the rule that stands.

The original text below is unchanged and kept as history.

---

## Context

- **The runner has no ordering check.** DEC-4c1396 makes bc-db forward migrations the sole schema path, and the runner applies a named migration from a staged directory holding only that migration.
- **Out-of-order applies left holes on live.** The live ledger (read 2026-09-30):
  - 0000 adopted; 0004–0007, 0009–0019, 0021–0024, 0026 and 0027 applied;
  - 0020 and 0025 never merged;
  - 0001, 0002, 0003 and 0008 were never applied on live, while CI and clones have them.
- **Coupling.** The output-declaration migration (ADR DEC-b1e9eb) makes the database refuse new metric versions without a declaration, which only a bc-core build with the authoring slice writes. Separated, either half breaks new-metric authoring.
- **Near miss.** A serve build almost carried code for unapplied DDL (2026-09-30; devhub serve-move-9 evidence NO-UNAPPLIED-DDL-CHECK.md).
- **Why an ADR.** bc-docs docs/operations/serve-moves-and-live-windows.md (847d4467) cites these rules; this ADR makes them durable (Codex gen-fa967b-01 asked for this).
- **Authority.** Co-signed by the Platform Controller (SES-a76e1e) and the DB Controller (edits E1–E4, 2026-09-30). Task TSK-ff2a61.

## Decision

1. **Number order.** Live platform migrations apply in migration-number order. A migration is not applied while a lower-numbered migration on main is unapplied on live, unless that lower migration carries a recorded disposition.
   - **The "excepted" ledger kind** comes with bc-db 0031 (merged e47c1c8): 0001, 0002 and 0008 excepted, 0003 applied. An exception needs a review binding plus the operator's apply grant.
   - **Backfill:** a lower number may be applied below the live maximum only as a named backfill step in a DBCP under its grant.
   - **Renumbering:** a PR that would merge a number below the live maximum must renumber before merging.
   - **Enforcement:** until the runner's ordering gate (M3, TSK-723a3f) is built, the live window's pre-check enforces this rule.
2. **Joint windows.** When a migration and bc-core code depend on each other in either direction, they go live in ONE live window under ONE operator grant naming the migration bytes and the build commit. DDL first, then the build.
   - **On red, both roll back** while the migration's rollback is still permitted. Once a rollback is refused (e.g. after declarations or exceptions exist), recovery is a forward fix.
3. **No code ahead of its DDL.** No serve build may contain code that reads or writes database objects of a migration not yet applied on live. Every serve move pins its build commit and records a pre-check searching the build for the objects of every unapplied migration.
4. **Merge discipline.** Code needing an unapplied migration may be reviewed and marked ready, but merges to main only after that migration is live, or with a joint window's build.
