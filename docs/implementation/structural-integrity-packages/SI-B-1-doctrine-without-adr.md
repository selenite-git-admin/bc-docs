---
title: "SI-B-1 — Doctrine-without-ADR (backfill the missing decision records)"
status: draft-for-review
package: SI-B-1
program: Structural Integrity (DEC-027ef6/D619)
plane: b (decision / doc hygiene)
anchor_task: TSK-f38fb6
date: 2026-09-21
d541_intake: >
  Design act — governance declarations exist as operational doctrine in CLAUDE.md but have no backing
  decision record (design-gap: the declaration is missing/misplaced, so write it). Repair location B
  (declaration) + F (docs/comments). No Foundation-boundary matter; no schema; no DBCP. The only code
  touch is comment text (citation fixes), which is a separate bc-core review with its own safe window.
---

# SI-B-1 — Doctrine-without-ADR

> **Plain English.** Several "X is retired/deprecated" rules live only in the project-memory file
> (CLAUDE.md), not in a decision record — including a **whole retired project** (`bc-core-dashboard`) with
> **no record at all**. This package writes the **missing ADRs** so the governance trail is complete, and
> fixes code comments that cite "CLAUDE.md" as their authority instead of the real ADR. Documentation +
> comment text only — **no behaviour change, no schema, no DBCP.**

## 1. Grounded inventory (verified firsthand @ bc-docs origin/main + bc-core `53bb1115…`)

| # | Doctrine-only assertion | Where it lives | ADR backing? (verified) |
|---|---|---|---|
| **B1-a** | **`bc-core-dashboard` project retired (2026-07-07)** | CLAUDE.md Project Repos table (archived to `_archived-repos/bc-core-dashboard-2026-07-07`) | **NONE.** `ADR-890417` (pm2) + `ADR-e50b83` (port table) name it as an *active* service *before* retirement; `ADR-2e801a`/`ADR-7e76b9` are **bc-portal v2-dashboard** retirements — unrelated. A whole project's shutdown has **zero governance trail.** |
| **B1-b** | **IntegrityService deprecation lifecycle** — "survives only for bc-admin panels + test-bench; R5 removal planned; do NOT extend; BF/CF tracing removed in PR #707" | CLAUDE.md "Chain Completeness" + `integrity.service.ts` comment ("DEPRECATED per CLAUDE.md") | **PARTIAL.** The gate-**off** is ADR'd (DEC-29b518/D429 + DEC-d9fa49/D547); the **lifecycle** clauses above are **not** in any ADR. |
| **B1-c** | **Auth-bypass ban (bc-core scope)** + the "~30% of session time" rationale | CLAUDE.md "Authentication" | **PARTIAL.** `DEC-04dade` is **bc-portal-scoped** (and itself the current of a superseded chain); no **bc-core-scoped** ADR; the rationale is un-ADR'd. |
| **B1-d** | **Citation-drift** — code comments citing "CLAUDE.md" as governing authority | ~8 bc-core `src/**/*.ts` files (e.g. `mls14-activation-gate.service.ts:19` cites CLAUDE.md for the display-only chain-status doctrine that **is** ADR-backed via `ADR-ea9bdc`/`1e55d3`/`a6cdae`; `integrity.service.ts` "DEPRECATED per CLAUDE.md") | the doctrine **is** ADR-backed; the **code comment points at the wrong authority** (project-memory, not the ADR). |

## 2. D541 intake

**Design act.** Each item is a *missing or misplaced declaration*, not a code defect: the governance is
real and in force, but its authoritative home (an ADR) is absent or the code cites the wrong home. The fix
is to **supply the declaration** (write the ADR) and **repoint the citation** (fix the comment). Repair
location **B** (declaration) + **F** (docs/comments). Not a Foundation-boundary matter; no schema; no DBCP.

## 3. The design — what each item needs

- **B1-a → backfill ADR (status `implemented`), records an already-effected retirement.** Content: the
  `bc-core-dashboard` project was retired 2026-07-07 and archived to `_archived-repos/…`; **the retirement
  rationale must be sourced** (its `ARCHIVED.md` or the operator) — this package does **not** invent it;
  supersession note to the `ADR-890417`/`ADR-e50b83` entries that still list it as active; frees port 4100
  (already noted in the port table). *Open input: the rationale.*
- **B1-b → backfill ADR (or amend DEC-29b518).** Records IntegrityService's interim-survival scope (the
  bc-admin metric-catalog panels `/registry/integrity/kpi/:id` + `/coverage`, test-bench), the **R5-removal
  commitment**, and the PR #707 BF/CF-tracing-removal fact. **Spawn a tracked `R5-removal` task** (the
  forward commitment currently has no owning record). Prefer an amendment to DEC-29b518 (keeps the lineage)
  over a fresh ADR — *design choice for Codex.*
- **B1-c → backfill a bc-core-scoped ADR (or promote DEC-04dade to platform-wide).** Records the auth-bypass
  prohibition for bc-core + the rationale. *Design choice: new bc-core ADR vs widening DEC-04dade's scope —
  for Codex.*
- **B1-d → comment fixes (bc-core, comment-only).** Repoint the ~8 "CLAUDE.md"-citing comments to the
  governing ADRs (mls14 → ADR-ea9bdc/1e55d3/a6cdae; integrity.service.ts → DEC-29b518 + the new B1-b ADR;
  etc.). **Comment text only** — no provider/route change, so `__architecture__` snapshots are untouched;
  still a **separate bc-core code review with its own fresh safe window** (§5.2 of the program SSOT).

## 4. Macro connection map

- **Docs:** CLAUDE.md (the doctrine's current home — after backfill, it **cites** the ADRs rather than
  being the authority); the ADR estate (3 new/amended records); README/index scans.
- **Code (comment-only):** ~8 bc-core `src/**/*.ts` files (B1-d).
- **Tasks:** a new `R5-removal` task (B1-b's forward commitment).
- **Governance:** DEC-623f8f/D370 (hygiene policy — SI-B-3 will add the "doctrine-without-ADR" detector so
  this class is caught automatically hereafter). No sibling-package coupling; independent of SI-A-1/SI-L5-1.

## 5. Implementation sketch (after Codex approval)

1. Source B1-a's retirement rationale (archive `ARCHIVED.md` / operator).
2. Write the 3 backfill ADRs via `devhub_decision_record` (B1-a `implemented`; B1-b amendment/new; B1-c
   bc-core-scoped), each with the standard supersession/citation frontmatter; flip the `ADR-890417`/`e50b83`
   entries' mention to "retired, see B1-a" where a supersession applies.
3. Spawn the `R5-removal` task (B1-b).
4. B1-d comment fixes as a **separate bc-core PR** (comment-only), its own review + safe-window.
5. Optionally trim CLAUDE.md's doctrine lines to *point at* the new ADRs (keeps memory legible, ADRs
   authoritative).

## 6. Acceptance

Each of B1-a/b/c has a backing ADR (with real content, not a stub); the `R5-removal` task exists; each of
the ~8 B1-d comments cites an ADR, not CLAUDE.md; a re-scan (SI-B-3, once built) reports this class covered.

## 7. Boundary

Design only — **no ADRs written, no comments changed yet.** This package proposes the backfill set for
**Codex review as `d619-002`**; the ADR-writing follows approval, and the B1-d comment fixes are a separate
bc-core code review with a fresh safe window. No schema, no DBCP, no Foundation-boundary matter. B1-a's
rationale is an **open input** to be sourced before its ADR is written.
