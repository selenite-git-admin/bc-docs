---
title: "SI-D-1 — Point docs at the source; never freeze a stat"
status: draft-for-review
package: SI-D-1
program: Structural Integrity (DEC-027ef6/D619)
plane: d (SSOT / authority structure)
anchor_task: TSK-f38fb6
date: 2026-09-21
d541_intake: >
  Design act embodying the doc-estate rule (below): a document never freezes a volatile statistic — it
  points to the live source, or carries an explicit "snapshot as of DATE — not authority" stamp. Applied
  to the schema authority (D-1a: the delegation must resolve to the live bc-db source, not an absent or
  stale derived copy — target chosen by bc-db/DB-Foundation, per DEC-4c1396/DEC-826390) and the MCF count
  (D-1b: point to the live source and mark June as history — do NOT swap in today's number, which is stale
  tomorrow). Do NOT rewrite decided ADRs. Repair location F (docs) + D (authority pointer). No schema,
  code, or DBCP.
---

# SI-D-1 — Point docs at the source; never freeze a stat

> **The standing rule this package sets and applies (operator-affirmed 2026-09-21):**
> **a document must never freeze a number that lives in the database.** It either *points to the live
> source*, or it is stamped *"snapshot as of DATE — not authority."* Chasing a frozen number to match the
> DB is a treadmill — it is stale again the next day; the fix is structural, not a value update.

> **Plain English — the two cases.** (1) The database-rules decision points its "schema map" at a file
> that doesn't exist; the fix is that the **schema owner re-targets it at the live/generated source** —
> not a stale copy — and this package flags it (it does not choose the target). (2) The instructions file
> **freezes a metric count from June**; the fix is to **point at the live source and mark June as
> history** — not to swap in today's 433, which is stale tomorrow. Documentation only — no schema, no
> code, no DBCP; no decided ADR rewritten.

## 1. Grounded findings (verified @ bc-docs origin/main + live `bc_platform_dev`, 2026-09-21)

### D-1a — a dangling schema-authority delegation (bc-docs)
- **`DEC-1918d0/D162`** states inline: *"82 tables across 12 schemas"* (line 54); live `bc_platform_dev` =
  **20 application schemas / 258 base tables** — the inline figure is a **stale historical fact** (D162
  dated 2026-03-17).
- **D162 delegates the authoritative inventory** to `architecture/database/schema-map.md`, which **does
  not exist** in bc-docs or bc-core (verified `git ls-tree`). The delegation is **dangling** — the real
  plane-d gap.
- **The `docs/reference/data-dictionary/` is NOT the fix target.** Its own README frontmatter declares
  `authority: source-derived`, `status: generated`, `generated_at: 2026-07-06`, from `bc-core` `44767f0`
  `/src/database/schema`. It has **20 schema pages + README** (not 21 per-schema files), **no `mcf` page**,
  and `contract.md` still references the retired `contract.metric_contract` — so it is a **derived
  reference with demonstrable stale/missing coverage**, not current authority.
- **The authority chain is settled elsewhere:** `DEC-4c1396` — bc-db is the **sole platform schema
  authoring/apply path**; live DB is current-state truth; `schema_migration_event` is applied-change
  evidence; Drizzle/derived docs are a **type surface / reference, not authority**. `DEC-826390` — the DB
  spine's home is **bc-db**. So the schema-map/inventory target is a **bc-db / DB-Foundation-owned**
  decision, not this program's to assign.

### D-1b — CLAUDE.md MCF snapshot (barecount-devhub repo)
- CLAUDE.md line 527 is an explicitly **dated 2026-06-06** paragraph: *"…18 `mcf.*` tables live;
  `mcf.metric_contract` = 5 (1 active = ARPI, 1 approved, 2 draft, 1 review); … Next governed gate: M14…"*.
- Live (read-only, 2026-09-21): `mcf.metric_contract` = **433 contract identities**;
  `mcf.metric_contract_version` = **433 versions**, of which **80 are `is_current`**. **`governance_state_code`
  is on the *version*, not the contract** (verified: absent on `metric_contract`, present on
  `metric_contract_version`) — so the old "1 active/1 approved/2 draft/1 review" was a **version-state**
  breakdown, and version-states **do not sum to the contract count**. The paragraph's *other* claims (18
  mcf tables, M2-M13 closeouts, "next gate M14") are unverified here and must not be silently redated.

## 2. D541 intake
**Design act (authority hygiene).** No decision is re-decided; the schema-map/inventory **target** is
bc-db/DB-Foundation's to choose (DEC-4c1396/DEC-826390). This program flags the dangling reference and
annotates stale figures. Repair location F + D. No schema/code/DBCP.

## 3. The design — per finding

- **D-1a — flag + coordinate; do not re-point to a derived reference.**
  1. **Flag the dangling `schema-map.md` delegation** in D162 to **DB-Foundation / bc-db** (the schema
     authority per DEC-4c1396/DEC-826390). The owner chooses the target — an **owner-reviewed
     schema-map/inventory documenting a pinned live/spine state**. The source-derived `data-dictionary`
     stays a **reference** unless regenerated **and validated** against the intended platform scope
     (it currently misses `mcf` and carries retired `contract.metric_contract`).
  2. **Annotate D162's inline count** as a dated historical figure (2026-03-17) pointing to the
     owner-chosen live authority — via **errata/amendment, not a decision rewrite**.
  3. This program does **not** unilaterally edit the decided D162 or assign its delegated authority; it
     records the gap and hands the target choice to the owner.

- **D-1b — point to source; do not freeze a new number.**
  Apply the standing rule: the MCF count must **not** be re-frozen (swapping "5" → "433" just re-starts the
  drift). Instead:
  1. **Mark the entire 2026-06-06 paragraph as a dated historical snapshot** — "as of 2026-06-06, not
     current authority" — preserving its other claims (18 tables, M2-M13, "next gate M14") as history, not
     silently redated.
  2. **Replace the frozen count with a pointer to the live source** — the metric directory / an on-demand
     read-only query is where the current MCF count actually lives; the instructions file points there
     rather than restating a number. If a figure is unavoidable inline, it carries an explicit
     *"snapshot as of DATE — not authority"* stamp with the exact query, never a bare current-sounding count.
  This is a barecount-devhub (project-memory) change. Verified population (for the pointer's context, not
  to be frozen): 433 identities (97 archived) / 433 versions / 80 `is_current`; `governance_state_code`
  lives on the *version*, so version-states do not sum to the contract count.

## 4. Connections
- **Docs/ADRs:** `DEC-1918d0/D162` (bc-docs, decided — errata/annotation only), `DEC-4c1396` + `DEC-826390`
  (schema authority = bc-db), `reference/data-dictionary/` (source-derived reference), `CLAUDE.md`
  (barecount-devhub).
- **Owners:** DB-Foundation / bc-db (TSK-cc348a) owns the schema-map/inventory target and the
  data-dictionary generation → **coordinate D-1a**. D-1b is this program's project-memory refresh.
- **Sibling packages:** none coupled.

## 5. Implementation sketch (after approval)
1. D-1a: raise the dangling delegation with DB-Foundation/bc-db; on their target decision, record the
   errata/annotation on D162 (owner-reviewed); do not repoint to the data-dictionary as authority.
2. D-1b: in CLAUDE.md (barecount-devhub), mark the June-06 paragraph as a dated historical snapshot and
   replace the frozen count with a pointer to the live source (metric directory / on-demand query) — not a
   re-frozen 433.

## 6. Boundary
Design accepted-with-boundary (d619-005, bc-docs PR #56). D-1b implemented (barecount-devhub PR #20); D-1a raised to the bc-db owner (`TSK-d3fbc0`). D-1a's authority target is **not chosen
here** (bc-db/DB-Foundation's, per DEC-4c1396/826390); the data-dictionary is **not** asserted as current
inventory (it is a source-derived reference with stale/missing coverage). D-1b keeps historical claims
intact. No schema, code, or DBCP. SI-L5-1 remains OPEN/Foundation-gated; RT withdrawn.
