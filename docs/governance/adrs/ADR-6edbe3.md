---
uid: DEC-6edbe3
title: "D409 catalog factory — four-stage division of labor (Rules shortlist → AI panel → Endpoint gates → Operator approval)"
description: "D409 admission must traverse four mandatory stages — rules shortlist, AI panel semantic review, endpoint gate validation, operator approval — none of which alone is sufficient for catalog admission."
status: decided
date: 2026-05-17T15:45:09.578Z
project: bc-core
domain: contracts
subdomain: contracts/business-field
focus: governance
---

# D409 catalog factory — four-stage division of labor (Rules shortlist → AI panel → Endpoint gates → Operator approval)

## Context

Rules-only admission is shape-blind: SES-9c1824 / SES-84335a showed the scan classifier marked 133 of 250 rows ADMIT_READY_CANDIDATE on structural shape, but DB re-validation of the top 25 found ALL of them in (status_code='certified', catalog_state_code='candidate_import', standard_ref=NULL, semantic_family=NULL) — a state combination the live admission gate rejects on the first precondition. The rule-based classifier could not see this because it never asked the semantic questions (is this BF name semantically aligned with its definition, is the source citation relevant or just adjacent, is this a duplicate of an existing certified BF, does the CF perspective match the BF perspective, should this be generic or subtype-specific, does the object_class make sense, is this a business concept or imported noise). LLM-only admission is the symmetric error: it would skip the deterministic guardrails (gate compatibility matrices, no-write enforcement, invariant drift detection). The endpoint gates remain the only authoritative semantic-vocabulary contract; the operator remains the only authoritative writer of consequence.

## Decision

D409 catalog admission proceeds through four mandatory stages, in order. Skipping any stage is not D409 admission.

STAGE 1 — RULES SHORTLIST (deterministic, read-only).
Filter obvious garbage. Detect missing required fields. Check type/family/unit compatibility. Find duplicates by normalized name. Verify gates' pre-conditions. Stop on invariant drift. Output: a candidate cohort with a structural-precheck classification. Lane name MUST carry a _CANDIDATE suffix (e.g. ADMIT_READY_CANDIDATE) to signal structural-only judgment. Rules are the guardrails, not the judge.

STAGE 2 — AI PANEL (Maker / Checker / Moderator).
Three independent agents review each shortlisted row.
- Maker / Explorer: argues for admission, cites evidence from row definition, alias, source.
- Checker / Skeptic: tries to reject — fallback definition, wrong BO scope, generic property, duplicate BF, weak source, name/object_class mismatch.
- Moderator: consolidates and emits one verdict per row: APPROVE_FOR_DRY_RUN, NEEDS_EVIDENCE, REJECT_BAD_MODEL, DUPLICATE_OR_MERGE, HOLD.
Only APPROVE_FOR_DRY_RUN rows proceed to stage 3.

Provider diversity is a panel goal but not a requirement of this decision. Until the bc-ai bf_admission_review endpoint ships (extending TSK-8c3e7c), the panel may be implemented as three isolated Claude Agent processes in the harness. That implementation MUST be labeled Claude-only multi-agent — provider diversity must not be claimed. Provider-diverse Gemini/OpenAI/Claude panel is the target end-state and is filed as the bc-ai follow-up.

STAGE 3 — ENDPOINT GATES (live validation).
POST /api/business-fields/:id/admit-from-candidate-import runs the deterministic G1-G8 + state-precondition + type-pair + CC-conflict gates. Stage 2 verdicts do not bypass any gate. A row that stage 2 approves but the endpoint rejects is not admitted.

STAGE 4 — OPERATOR APPROVAL (human writer).
Every apply requires explicit operator sign-off after seeing stage 2 + stage 3 dry-run output. Batches cap at 25. Halt-on-first-failure. No autonomous apply, regardless of upstream confidence.

NEGATIVE RULES.
- No rules-only catalog admission.
- No LLM-only catalog admission.
- Endpoint gates remain mandatory.
- Operator approval remains mandatory for apply.
- Rules and AI both produce read-only artifacts; only the endpoint and the operator write.
