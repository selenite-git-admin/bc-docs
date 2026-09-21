---
uid: DEC-027ef6
title: "Structural Integrity program — execution, method & sequencing"
description: "The execution & sequencing ADR for the Structural Integrity program (Track S of Platform Readiness, anchor TSK-f38fb6). Locks the four-plane lane-anchored framework, the pin→verify→name coherence method, the design-cum-implementation package discipline (auditor-approved before code), the references-not-absorbs ownership rule, the safe-window peer discipline, and the sequencing. Re-decides no prior decision; locks HOW the program executes."
status: decided
date: 2026-09-21T08:59:34.620Z
project: platform
domain: platform
subdomain: structural-integrity
focus: governance
---

# Structural Integrity program — execution, method & sequencing

## Context

Track S ("Structure") of Platform Readiness & Legibility (DEC-33d436/D606) was spun off 2026-09-21 as its own program and, on a grounded read-only study (SES-2b96b2, measured against bc-core origin/main 53bb1115, bc-docs origin/main be4f6ce, and live bc_platform_dev), reframed from "code movement" to **structural integrity across four planes** — decisions (ADRs) ↔ docs (bc-docs) ↔ code (bc-core) ↔ DB (bc_platform_dev). The parent program's stall analysis is load-bearing: code structure was ~9% of stalls, docs≠code and wrong-plane ~24% each. The study found **no coherence gap where assessed**, but the sweep was breadth-first, not a per-cell audit (the SSOT §3 matrix marks most cells not-assessed). Two plane-c items first elevated as coherence gaps were re-examined on verification (Codex d619-001): the RT hard-delete path is **unreachable** (the service throws before the repository runs) and its intended design already exists (D564 governed expunge + soft `archiveReader`) — **withdrawn**; the L5 resolver routes' failure-mode claim was corrected to **fail-safe refusal**, but whether their empty-legacy dependency satisfies the advertised route contract is an **OPEN adjudication (SI-L5-1), Foundation-gated before any removal/repointing** — **not** closed. What remains is a **governance-trail + legibility long tail** plus that one open L5 contract question. SSOT: docs/implementation/structural-integrity-program.md.

## Decision

1. **Framework.** Structural Integrity is an umbrella program on the locked platform lane/function spine (S1–S5, L1–L10, RT/EV/TS/A1, DEC-a67bae/D590), expressed as a **lane × plane matrix** — plane a code structure, b decision/doc hygiene, c decision↔code↔DB coherence, d SSOT/authority. This mirrors the Platform-Readiness and Tenant-Readiness frameworks for cross-program legibility.

2. **Method (the coherence engine).** Each gap is adjudicated: (i) pin the load-bearing assertion; (ii) name the expected code/DB surface; (iii) read substrate read-only; (iv) verdict + plane — coherent / design-gap (declaration wrong or missing) / execution-gap (code violates a correct declaration). Step (iv) is the DEC-c48b0f/D541 intake. Reads never trigger evaluation; no substrate hand-edits to "fix" a number.

3. **Work product — design-cum-implementation packages.** No refactor in isolation. The pre-code work product is a set of packages each carrying macro (connection map: what it touches, depends on, couples to) and micro (target state, file-level steps, D541 verdict, acceptance evidence) vision, plus a plain-English note. The package is the review unit; **Codex approves each package before any code**; the PR implements an approved package.

4. **Ownership — reference, not absorb.** The program owns only the unowned drift + the cross-plane map + the reusable method. D608 (legacy metric corpus, TSK-d21b97), Platform DB Foundation (schema/tenant, TSK-cc348a), the ADR-hygiene punch-list (DEC-623f8f/D370), the design/execution coupling anchor (TSK-b5ab8a), and the platform/tenant boundary drift (DEC-96cc78/D612) remain their owners.

5. **Sequencing (post-review).** Real + cheap first — SI-B-1 (promote doctrine-without-ADR to ADRs) and SI-D-1 (fix stale doc numbers); then SI-B-3 (self-closing hygiene checks: decided-not-implemented + status-vs-body); then SI-A-1 (dead/unreachable residue removal — route-by-route, preserving the 410 contract or via an approved retirement amendment); hand-offs throughout; the five physical code moves last (SI-A-2…6), BoundaryModule last. **SI-RT-1 is withdrawn** (unreachable; design already exists). **SI-L5-1 stays OPEN** — the L5 route-contract adjudication, **not** folded into SI-A-1 as cosmetic; it is a coherence unit that **passes the Foundation gate before any removal/repointing**. The Foundation gate applies to it and to any future coherence unit.

6. **Discipline.** Safe window re-confirmed with active peers (foremost Tenant Readiness / TSK-d73f01) immediately before every code move, not once; worktree off origin/main, parent==tip verified at commit; D541 intake per unit; auditor gate via this program's own Codex exchange family; DBCP-with-explicit-consent if any schema is touched.

7. **Bounded — not a standing audit.** The program produces the map, the method, and a finite backlog; hands each item to its owner; does the small unowned ones; and closes when the backlog is drained. The recurring check moves into the plane-b hygiene tooling (SI-B-3), not a perpetual program.

This ADR re-decides no prior decision; it locks how the Structural Integrity program executes. Its D-code names the program's Codex exchange family.
