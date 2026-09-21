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

See decision text below.

## Context

Track S ("Structure") of Platform Readiness & Legibility (DEC-33d436/D606) was spun off 2026-09-21 as its own program and, on a grounded read-only study (SES-2b96b2, measured against bc-core origin/main 53bb1115, bc-docs origin/main be4f6ce, and live bc_platform_dev), reframed from "code movement" to **structural integrity across four planes** — decisions (ADRs) ↔ docs (bc-docs) ↔ code (bc-core) ↔ DB (bc_platform_dev). The parent program's stall analysis is load-bearing: code structure was ~9% of stalls, docs≠code and wrong-plane ~24% each. The study found the substrate **mostly coherent**, with a real long tail: dead-mount 410 residue, doctrine that lives only in CLAUDE.md without an ADR, numeric doc staleness, and two genuine coherence gaps — retired canonical_mapping backing two live routes (L5), and runtime.admission_run hard-deleted on reader removal in tension with Invariant III (RT). SSOT: docs/implementation/structural-integrity-program.md.

## Decision

1. **Framework.** Structural Integrity is an umbrella program on the locked platform lane/function spine (S1–S5, L1–L10, RT/EV/TS/A1, DEC-a67bae/D590), expressed as a **lane × plane matrix** — plane a code structure, b decision/doc hygiene, c decision↔code↔DB coherence, d SSOT/authority. This mirrors the Platform-Readiness and Tenant-Readiness frameworks for cross-program legibility.

2. **Method (the coherence engine).** Each gap is adjudicated: (i) pin the load-bearing assertion; (ii) name the expected code/DB surface; (iii) read substrate read-only; (iv) verdict + plane — coherent / design-gap (declaration wrong or missing) / execution-gap (code violates a correct declaration). Step (iv) is the DEC-c48b0f/D541 intake. Reads never trigger evaluation; no substrate hand-edits to "fix" a number.

3. **Work product — design-cum-implementation packages.** No refactor in isolation. The pre-code work product is a set of packages each carrying macro (connection map: what it touches, depends on, couples to) and micro (target state, file-level steps, D541 verdict, acceptance evidence) vision, plus a plain-English note. The package is the review unit; **Codex approves each package before any code**; the PR implements an approved package.

4. **Ownership — reference, not absorb.** The program owns only the unowned drift + the cross-plane map + the reusable method. D608 (legacy metric corpus, TSK-d21b97), Platform DB Foundation (schema/tenant, TSK-cc348a), the ADR-hygiene punch-list (DEC-623f8f/D370), the design/execution coupling anchor (TSK-b5ab8a), and the platform/tenant boundary drift (DEC-96cc78/D612) remain their owners.

5. **Sequencing.** Foundation + coherence first (SI-RT-1 through the Foundation gate; SI-L5-1); then doctrine + leverage (SI-B-1 promote doctrine to ADRs; SI-B-3 self-closing hygiene check); then quick wins + residue (SI-D-1 doc numbers; SI-A-1 dead-mount removal); hand-offs throughout; the five physical code moves last (SI-A-2…6), BoundaryModule last.

6. **Discipline.** Safe window re-confirmed with active peers (foremost Tenant Readiness / TSK-d73f01) immediately before every code move, not once; worktree off origin/main, parent==tip verified at commit; D541 intake per unit; auditor gate via this program's own Codex exchange family; DBCP-with-explicit-consent if any schema is touched.

7. **Bounded — not a standing audit.** The program produces the map, the method, and a finite backlog; hands each item to its owner; does the small unowned ones; and closes when the backlog is drained. The recurring check moves into the plane-b hygiene tooling (SI-B-3), not a perpetual program.

This ADR re-decides no prior decision; it locks how the Structural Integrity program executes. Its D-code names the program's Codex exchange family.
