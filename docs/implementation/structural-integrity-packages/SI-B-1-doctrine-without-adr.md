---
title: "SI-B-1 — Doctrine-without-ADR (backfill the missing decision records)"
status: draft-for-review
package: SI-B-1
program: Structural Integrity (DEC-027ef6/D619)
plane: b (decision / doc hygiene)
anchor_task: TSK-f38fb6
date: 2026-09-21
d541_intake: >
  Design act — where a governance rule genuinely lacks a decision record, supply it; where the record
  exists but a code comment cites the wrong authority, repoint the citation; where a CLAUDE.md reference
  is legitimately descriptive/process, keep it. Repair location B (declaration) + F (docs/comments). No
  Foundation-boundary matter; no schema; no DBCP. The comment fixes are a separate bc-core review with a
  fresh safe window.
---

# SI-B-1 — Doctrine-without-ADR

> **Plain English.** Some governance rules live only in the project-memory file (CLAUDE.md). This package
> **backfills the genuinely-missing decision records** and **repoints code comments that cite the wrong
> authority** — after verifying, per item, what really governs it. It does **not** treat every CLAUDE.md
> mention as a defect (many are legitimate descriptive/process references), and it does not invent
> rationale it cannot source. Documentation + comment text only — **no behaviour change, no schema, no DBCP.**

## 1. Grounded inventory (verified per item @ bc-docs origin/main + bc-core `53bb1115…`)

### B1-a — `bc-core-dashboard` project retirement
- CLAUDE.md records the **retirement, date (2026-07-07), and archive path**, but **not the rationale**.
  A scoped search of the pinned ADR corpus finds **no ADR for this retirement** — `ADR-890417`/`ADR-e50b83`
  name it as an *active* service pre-retirement; `ADR-2e801a`/`ADR-7e76b9` are **unrelated bc-portal
  v2-dashboard** retirements. (Honest bound: "no ADR found in the searched corpus" — **not** "zero
  governance trail," which overstates a scoped search.)
- **`ARCHIVED.md` is absent** at the archive path in this environment, so the rationale cannot be recovered
  there. It is an **explicit prerequisite input** (operator ratification if the original authority is
  unrecoverable), which this package does not invent.
- **`ADR-890417` is itself superseded by `DEC-9b23a7`** — follow the successor; any annotation is limited to
  the **dashboard mention**, not a wholesale supersession of the pm2/port policy.

### B1-b — IntegrityService deprecation lifecycle
- **Retention is already ADR-recorded** — correcting the earlier "only gate-off" claim: `DEC-29b518`
  Decision 4 retains IntegrityService **"ONLY for detail/read contexts, if still needed"**; `ADR-b54a43`
  places it under **mark-don't-delete**; `ADR-bebaec` (chain-completeness, now superseded by `DEC-b390ef`)
  records backward-compat retention; `DEC-d9fa49` retires the legacy metric-activation route.
- The **genuinely-missing delta** is narrow: the **"do-not-extend + R5-removal follow-up"** (CLAUDE.md
  states it; **removal is owned by the existing `TSK-3359d7`** — registry searched — but no *ADR* recorded
  the do-not-extend/lifecycle follow-up). → a **dated, narrowly-scoped amendment to `DEC-29b518`** that records
  *only* that follow-up, reconciling the lineage above and **not** rewriting old gate authority or
  presenting inherited retention as newly-discovered doctrine.

### B1-c — auth-bypass ban (bc-core scope)
- **`ADR-04dade` is superseded by `DEC-6cdceb`** (verified frontmatter) — correcting the earlier "current"
  claim; it is a bc-portal ADR, and the successor governs surface/route shape. So B1-c is **not** widening
  04dade. → a **new bc-core-scoped ADR** citing the portal auth-policy history (04dade→6cdceb) as
  **precedent** and CLAUDE.md as the current operational doctrine. The "~30% of session time" figure is an
  **attributed recollection**, not a verified metric. The ADR states the intended **authenticated-application
  boundary** and the **separately-reviewed legitimate test/public/service-auth cases** — it does **not**
  import frontend `VITE_BYPASS_AUTH`/`useAuth` semantics into the backend, and **no auth behaviour changes**
  in this package.

### B1-d — CLAUDE.md-citing comments: per-file citation map (verified)
A non-spec `src/**/*.ts` scan finds **6** (Codex's broader scan found **8**, incl. test-discipline + one
more in specs — the 2 extra are reconciled before the comment PR). They are **heterogeneous**, and most are
legitimate references, not defects:

| # | File:line | Asserted rule | Verified authority → intended edit |
|---|---|---|---|
| d1 | `mls/gate/mls14-activation-gate.service.ts:19` | chain-status is display-only, never a refusal authority | **authority UNRESOLVED** — candidates `DEC-b390ef` (chain-completeness successor) + the D481 MCF chain-status lineage; **`ADR-ea9bdc` is wrong** (SAP contamination). Verify the exact controlling clause, then repoint; if none governs the display-vs-gate distinction, **keep-as-context** + a tracked authority-TODO. |
| d2 | `platform/scan/scan-libraries.ts:21` | "matches CLAUDE.md project table" | **keep-as-context** — CLAUDE.md is the legitimate project-table source; not an authority defect. |
| d3 | `registry/integrity.service.ts:722` | "IntegrityService is DEPRECATED" | **fix** → cite `DEC-29b518` Decision 4 (+ the B1-b amendment), not CLAUDE.md. |
| d4 | `registry/mcf/billing-volume-retry-unlock/…:89` | "Foundation gate (CLAUDE.md §Foundation Invariant Check)" | **keep-as-context** for the session-gate *process*; may add a pointer to `foundation/the-invariants.md` for the invariants themselves. |
| d5 | `registry/mcf/package-signature.service.ts:602` | "per CLAUDE.md QA shift-left rule 9" | optional cite `DEC-ee6018` (Power-of-Ten) or **keep-as-context** — a coding-standard, low value. |
| d6 | `tenant-views/tenant-metric-catalog.service.ts:39` | "vocabulary mirrors the runtime-readiness gate" | **keep-as-context** — descriptive vocabulary reference. |

Net B1-d: **one real fix (d3)**, **one conditional on authority verification (d1)**, **four keep-as-context**,
plus **2 to reconcile** against Codex's count of 8. No "cite an ADR by count" instruction.

## 2. D541 intake
**Design act** — supply the missing declaration (B1-a rationale-gated; B1-b amendment; B1-c new ADR) and
repoint mis-cited comments (B1-d), or keep legitimate references. Repair location **B** + **F**. Not a
Foundation-boundary matter; no schema; no DBCP.

## 3. Ownership handoffs (reference-not-absorb)
- **B1-b owns** the IntegrityService lifecycle/authority record. **SI-A-1 owns** any *separately-approved*
  removal inventory + route/410 compatibility. A new R5-removal task is **tracking only, not permission to
  remove** retained consumers — and an existing removal task must be **searched for first** (its absence is
  unverified without DevHub).
- **B1-a** rationale → operator/archive. **B1-c** precedent → the 04dade→6cdceb portal lineage.

## 4. Implementation sketch (after Codex approval)
1. B1-a: source the rationale (operator ratification if archive unrecoverable); write an ADR recording the
   retirement (historical 2026-07-07 + new record date), following `DEC-9b23a7`; annotate only the dashboard
   mention.
2. B1-b: dated scoped amendment to `DEC-29b518` for the do-not-extend/R5-removal follow-up (after lineage
   reconciliation); search for an existing removal task before creating a tracking-only one.
3. B1-c: new bc-core-scoped auth ADR (precedent 04dade→6cdceb; ~30% as recollection; boundary + legitimate
   cases stated).
4. B1-d: comment fixes per the map (d3 fix; d1 after authority verification; keep-as-context the rest) as a
   **separate bc-core PR** with its own review + fresh safe window; reconcile the 2 extra vs Codex's count.

## 5. Acceptance
Each genuinely-missing record (B1-a/b/c) has a backing ADR with real, sourced content; B1-d's map is applied
exactly (fixes cite the verified ADR clause; keep-as-context items are left, annotated); the R5-removal
follow-up is owned; a re-scan (SI-B-3) reports the covered class.

## 6. Boundary
Design only — **no ADRs written, no comments changed.** For Codex review as `d619-002`. ADR-writing follows
approval; B1-d comment fixes are a separate bc-core review with a fresh safe window. B1-a's rationale is an
explicit unresolved input; d1's authority is an explicit unresolved input. No package acceptance implies
code, deployment, or a Foundation/DBCP waiver. SI-L5-1 remains OPEN (Foundation-gated); SI-RT-1 withdrawn.
