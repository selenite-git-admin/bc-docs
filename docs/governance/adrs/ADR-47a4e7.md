---
uid: DEC-47a4e7
title: "C5 operator-driven transition expansion (operatorAdvance)"
description: "Add FrameworkApprovalService.operatorAdvance for operator-authority BF/BO governance_state transitions; prerequisite for supersede-active."
status: decided
date: 2026-05-20T04:00:39.217Z
project: bc-core
domain: contracts
subdomain: framework-approval
focus: lifecycle
---

# C5 operator-driven transition expansion (operatorAdvance)

## Context

C5's decide() authorizes only draft→review and is panel-evidence-driven; supersede-active needs review→approved and approved→active. Per Foundation Invariant III and N8, the activation that completes a supersession is an operator act with no panel evidence — AI cannot activate over an active predecessor. Widening decide() for the AI-panel path is blocked on the unbuilt bc-ai Context Publication Panel. A sibling operator-authority method unblocks supersede-active with zero bc-ai dependency and matches the Requirements' explicit two-path model (AI proposes/prepares/approves under Framework Approval; operator overrides as exception).

# C5 Operator-Driven Transition Expansion — operatorAdvance

## Authority / requirements basis
DEC-149ab2 (D411); BCF Requirements Ch.5 "Division of labor" + Ch.7 "Bounded-write discipline"; Foundation Invariant III (active artifacts immutable; supersession is the only change mechanism); N3 (operator override must never be disabled); N8/N23 (AI cannot mutate or activate active artifacts). Build-plan §3 C7.

## Substrate inventory (verified against bc_platform_dev)
- FrameworkApprovalService.decide() runs 7 bounded-write checks; THREE things hard-lock it to draft→review: Check 1 (literal from/to equality), V1_PANEL_STAGE='authoring' (Check 3a + pause stage), V1_ACTION_CODE='submit_for_review'.
- decide() is panel-evidence-driven (Checks 3/3a/3b/4 require a panel_output_record). It never reads the BF/BO member row.
- GovernanceStateRepository.advanceBusinessField/ObjectGovernanceState are the sole-writer-fenced governance_state helpers (bcf-c5-governance-state-sole-writer.spec.ts grep).
- governance_state CHECK already permits all five values (draft/review/approved/active/superseded) — no enum DDL needed.
- C6 transitionKey already maps draft_to_review / review_to_approved / approved_to_active; the A9 operator_confirm_rule.transition enum already carries all four — C6 is transition-ready.
- The bc-ai Context Publication Panel (stage_code='publication') emit path does NOT exist; B-runtime emits only authoring-stage records today.

## Accepted decision
1. Add a sibling method FrameworkApprovalService.operatorAdvance(...) for operator-authority governance_state transitions. decide() is left unchanged as the AI-panel-only path.
2. operatorAdvance supports BF/BO transitions draft→review, review→approved, approved→active. The predecessor transition active→superseded is NEVER a standalone request — it occurs only as the paired flip during a successor's approved→active activation.
3. The operator-driven path skips pause (Check 5) and operator-confirm (Check 6): operator override is always available (N3; "operator may execute transitions manually at any time"), and operator-confirm exists to make AI pause for the operator — moot when the operator is the actor. operatorAdvance also skips the panel-evidence checks (3/3a/3b/4) — operator acts carry no panel run.
4. operatorAdvance is NOT gated by policy eligible_operations_json — that field gates AI execution; gating operator authority would violate N3. No policy seed change is required.
5. operatorAdvance keeps a scope/primitive guard (BF/BO only) and a transition-set guard, and ADDS a guard that the member's current governance_state equals the proposed fromState — C5 may read BF/BO member rows to validate current governance_state and supersedes_id.
6. Add one new certification_record action_code: operator_advance_state. from_state_code/to_state_code carry the precise transition; a single code cleanly distinguishes operator-driven advancement from AI submit_for_review in the ledger. Each operatorAdvance transition writes one operator-authored "legacy-shape" cert row (7 NF1 fields NULL, override_* triple NULL, certifier_sub = operator, operator rationale in gate_results_json).
7. Successor activation runs in one db.transaction: load successor row + assert governance_state='approved'; advance successor approved→active; advance predecessor active→superseded guarded WHERE governance_state='active'; write the successor activation cert row; write the supersede cert row. If the predecessor is no longer active, the transaction is ABORTED and rolled back.
8. Scope is BF/BO (bf_bo) only. CF and mapping are deferred, consistent with C5 v1.

## Rejected alternatives
- Widen decide() itself for review→approved / approved→active: blocked on the unbuilt bc-ai Context Publication Panel; conflates the AI-consensus path with operator authority. The AI-panel wider-transition path remains a separate future effort once the Publication Panel ships.
- Gate operatorAdvance by eligible_operations_json or by pause: violates N3 (operator override must never be disabled/suppressed).
- Per-transition action_codes (approve, activate): two enum values where one (operator_advance_state) plus the from/to columns suffice.

## DDL / DBCP implications
- One additive DBCP: add operator_advance_state to certification_record_action_code_chk (paired revert; no column; no data migration) — same pattern as the C7 edit_non_active migration.
- supersede action_code and supersedes_primitive_id already exist — no DDL for the predecessor-flip half.
- No governance_state enum change. No eligible_operations_json seed change.

## Implementation sequence
1. DBCP: operator_advance_state action_code (apply to bc_platform_dev, verify).
2. operatorAdvance method on FrameworkApprovalService + transition-set guard + member-row read.
3. Successor-activation transaction (approved→active + paired predecessor active→superseded).
4. Per-scope operator endpoints land with the supersede-active slice (ADR 2).

## Test obligations
- Transition-set guard: draft→review / review→approved / approved→active accepted; others rejected.
- Current-state guard: member governance_state must equal proposed fromState.
- Operator path skips pause + operator-confirm (assert checkPause / operatorConfirmPort not consulted).
- Cert row shape: operator_advance_state, legacy-shape NF1 NULL, rationale in gate_results_json.
- Successor activation: predecessor flips active→superseded atomically; both cert rows written.
- Predecessor no longer active → whole transaction aborts, no partial write.
- supersedes_id IS NULL successor activation → no predecessor flip.
- bcf-c5-governance-state-sole-writer grep still green (no advance-helper import outside framework-approval/).

## Dependency
This ADR is a prerequisite for ADR 2 (BF/BO versioning model for supersede-active). ADR 2's approved→active + predecessor-flip behavior IS operatorAdvance. The two ADRs are filed as a pair; this one is implemented first.
