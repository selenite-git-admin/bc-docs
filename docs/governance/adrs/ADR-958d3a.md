---
uid: DEC-958d3a
title: "Platform-readiness engine-conformance is satisfied by compositional CI evidence; the single continuous end-to-end run is reclassified to tenant-readiness (governance is interlocked)"
description: "Platform-readiness engine-conformance is satisfied by compositional CI evidence; the single continuous end-to-end run is reclassified to tenant-readiness (governance is interlocked)"
status: decided
date: 2026-09-21T02:06:13.803Z
project: platform
domain: platform
subdomain: platform-readiness
focus: governance
---

# Platform-readiness engine-conformance is satisfied by compositional CI evidence; the single continuous end-to-end run is reclassified to tenant-readiness (governance is interlocked)

## Context

No rationale recorded.

## Decision

DECISION (operator ruling 2026-09-21, "B then A", SES-4ecd20). Amends the platform-readiness PROOF definition (DEC-33d436/D606 + SSOT bc-docs docs/implementation/platform-readiness-program.md §1).

CONTEXT / FINDING: This session drove toward the "proven-once-E2E" closing act (a single continuous fixture/real run: Source->Reader->SO->Canonical->CO->Metric Snapshot->Evidence). Grounded investigation established that a single continuous run is INSEPARABLE from the full governed onboarding stack, because governance is interlocked at the substrate level:
- Metric ACTIVATION is certification-gated in the DB: mcf.fn_mcv_state_transition_check forces draft->review->approved->audit_pending->active, each edge requiring real certification_record rows (metric_approve, audit_migrate, audit_admit) + an approval mcv_package_snapshot + metric_audit.fn_intrinsic_decision_ready. Hand-seeding or quick-fixing an active metric is impossible.
- Reaching an evaluable metric requires either full certification (the §11.A/C8 gate) or reusing an existing certified-active metric + repairing its downstream chain (CC re-pin), which goes through governed CC versioning -> activateVersion -> provisioning fanout -> owner-privileged worker for fact-table DDL (not in the served process). Either way = the full onboarding stack.
- Verified corpus state: no active metric is currently evaluable over real COs (operand-projection gaps e.g. cost_center_count binds temporal_anchor not projected by cc-gkbqb; OR superseded-OC pins e.g. cc-dh5d9 pins oc-vg0zn@1.1.0 while 1.2.0 active) — TSK-afd7ff. mcv_chain_status green does not imply evaluable (checks neither operand-projection nor OC-pin currency) — TSK-aaa6ae.

DECISION:
1. Platform-readiness ENGINE-CONFORMANCE is SATISFIED by COMPOSITIONAL evidence, not a single continuous run: every platform boundary is individually green + the couplings fail closed + the evaluation/evidence boundary is proven E2E. Authoritative evidence = bc-core CI on main (run 35552644122, headSha e72391fd, 2026-09-21): job e6b-db-integration=success (the 3 evaluation integration proofs metric-evaluation-proof/composite-metric-evaluation/governed-metric-persistence.adapter + the 3 execution-plane seam regression specs), quality-gate=success + static-analysis=success (T-track gates), vitest-shard 1/2/3=success. Seams merged PRs #726/#770(15cdbc37)/#769(eeb3d161)/#772(9fb10d98). Track T CLOSED 2026-08-25.
2. The single CONTINUOUS end-to-end run (the 4th "proven-once-E2E" criterion) is RECLASSIFIED to TENANT-READINESS milestone #1 (the Kaveri/lc5 onboarding); it requires the full interlocked governed onboarding stack. It is no longer the platform-readiness closing act.
3. Sequencing = B then A: close platform readiness on this compositional engine evidence + the in-gate residuals (L9 chain-audit door, S2 users door, ADR-hygiene), THEN perform the full Kaveri onboarding (tenant readiness) which produces the continuous real run naturally.

FOUNDATION GATE: design act (amends a ratified proof definition), not an execution net; repair location B (governance semantics of the readiness definition); no DBCP. FOLLOW-UPS: amend SSOT §1 + DEC-33d436 (bc-docs, via worktree — checkout is on a DB-Foundation branch); residuals gate the SSOT status:closed flip; the continuous real run rides tenant-readiness (TSK-d73f01). Anchor TSK-4b2404.
