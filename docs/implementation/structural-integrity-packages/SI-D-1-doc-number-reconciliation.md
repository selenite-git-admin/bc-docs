---
title: "SI-D-1 — Doc↔substrate number reconciliation"
status: draft-for-review
package: SI-D-1
program: Structural Integrity (DEC-027ef6/D619)
plane: d (SSOT / authority structure)
anchor_task: TSK-f38fb6
date: 2026-09-21
d541_intake: >
  Design act — the authority documents have drifted from substrate (stale inline counts) and one
  delegates to an absent doc. Fix the dangling authority pointer and refresh dated snapshots; do NOT
  rewrite the decided ADRs' decisions. Repair location F (docs) + D (authority pointer). No schema, no
  code, no DBCP. D162 touches a bc-docs ADR whose subject (schema evolution) is DB-Foundation-owned →
  coordinate, don't unilaterally re-decide.
---

# SI-D-1 — Doc↔substrate number reconciliation

> **Plain English.** A couple of docs quote numbers that drifted from the live database, and one
> decision points its "schema map" authority at a file that doesn't exist. This package fixes the
> **broken pointer** (to the doc that *does* hold the current inventory) and **refreshes the stale dated
> snapshots** — without rewriting any decided ADR. Documentation only — no schema, no code, no DBCP.

## 1. Grounded findings (verified @ bc-docs origin/main + live `bc_platform_dev`)

### D-1a — schema count + a dangling authority pointer (bc-docs)
- **`DEC-1918d0/D162`** states inline: *"82 tables across 12 schemas"* (line 54). Live `bc_platform_dev`
  (read-only, 2026-09-21): **20 application schemas** (`NOT LIKE 'pg_%'` and not public/information_schema),
  **258 application base tables** — so the inline figure is a **stale historical fact** (D162 dated
  2026-03-17).
- **D162 delegates the authoritative inventory** — its `references` frontmatter names
  `architecture/database/schema-map.md` ("Platform DB schema map"). **That file does not exist** in
  bc-docs or bc-core (verified `git ls-tree`). The delegation is **dangling**.
- **The current inventory that *does* exist** is **`docs/reference/data-dictionary/`** — 21 auto-generated
  per-schema files (CLAUDE.md names it the authoritative per-schema column inventory). Its **currency vs
  the live 20 platform schemas is to be confirmed with DB-Foundation** (it also carries tenant-side
  schemas; not asserted current here).

### D-1b — CLAUDE.md MCF snapshot (barecount-devhub repo)
- CLAUDE.md line 527: *"**Current state (2026-06-06):** … `mcf.metric_contract` = 5 (1 active = ARPI, 1
  approved, 2 draft, 1 review)…"*. Live `mcf.metric_contract` = **433**. The line is an explicitly **dated**
  snapshot (2026-06-06), now stale; the whole status breakdown — not just the count — is out of date.

## 2. D541 intake
**Design act (authority hygiene).** The fixes **do not re-decide** anything: D162's *decision* (the 11-rule
DB model + platform/tenant split) stands; only its **broken reference pointer** and **stale inline count
annotation** are addressed, and only in coordination with the schema owner. The CLAUDE.md line is a dated
project-memory snapshot to refresh. Repair location F (docs) + D (authority pointer). No schema/code/DBCP.

## 3. The design — per finding

- **D-1a (D162 / schema authority) — coordinate with DB-Foundation; do not rewrite the decision.**
  1. **Re-point the dangling reference**: D162's `references` entry `architecture/database/schema-map.md`
     → `reference/data-dictionary/` (the doc that actually holds the current inventory), **or** create
     `schema-map.md` if DB-Foundation wants that specific artifact. This is the real plane-d fix — a
     decision pointing at an absent authority.
  2. **Annotate the inline count** as a dated historical figure (2026-03-17) with a pointer to the live
     authority (data-dictionary), rather than editing "82/12" to "258/20" inside a decided ADR — the ADR
     *delegates* the live inventory, so the inline number is context, not the authority.
  3. **DB-Foundation owns schema evolution + the data-dictionary generation** (TSK-cc348a) → this item is a
     **coordinated hand-off**, not a unilateral edit; confirm the data-dictionary's currency there.

- **D-1b (CLAUDE.md MCF) — refresh the dated snapshot (barecount-devhub, this program's scope).**
  Re-ground the MCF state to a current-dated snapshot: `mcf.metric_contract = 433` with a fresh status
  breakdown (active/approved/draft/review counts, re-queried), and update the date; or, if a full
  re-ground is deferred, mark the line explicitly as a **stale 2026-06-06 snapshot** pointing to the live
  count. The count refresh is trivial; the status breakdown needs a small read-only re-query.

## 4. Connections
- **Docs/ADRs:** `DEC-1918d0/D162` (bc-docs, decided — reference + annotation only), `reference/data-dictionary/`,
  `CLAUDE.md` (barecount-devhub).
- **Owners:** DB-Foundation (TSK-cc348a) owns schema evolution + the data-dictionary → coordinate D-1a.
  D-1b is this program's (project-memory refresh).
- **Sibling packages:** none coupled. Independent.

## 5. Implementation sketch (after approval)
1. D-1a: raise the dangling-reference + currency question with DB-Foundation; on their steer, either
   repoint D162's reference to the data-dictionary (via errata/amendment, not a decision rewrite) or
   create the schema-map artifact; annotate the inline count as dated.
2. D-1b: read-only re-query the MCF status breakdown; update CLAUDE.md line 527 to a current-dated snapshot
   (barecount-devhub) — a small, separate change in that repo.

## 6. Boundary
Design only — no docs changed yet. For Codex review as `d619-004`. D-1a is a **DB-Foundation-coordinated**
hand-off (no unilateral edit to the decided D162 or its delegated authority); D-1b is a project-memory
refresh in barecount-devhub. No schema, code, or DBCP. Does not assert the data-dictionary is current (that
is confirmed with DB-Foundation).
