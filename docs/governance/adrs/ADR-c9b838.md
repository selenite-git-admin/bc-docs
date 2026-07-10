---
uid: DEC-c9b838
title: "From-seed-only authoring + reservoir status ledger as progress SSOT for MCF enrichment"
description: "Formalizes two Phase 0 practices as standing MCF governance: seed-only authoring + reservoir ledger as progress SSOT"
status: decided
date: 2026-07-07T04:12:27.238Z
project: bc-core
domain: metrics
subdomain: mcf/governance
focus: authoring-discipline
---

# From-seed-only authoring + reservoir status ledger as progress SSOT for MCF enrichment

## Context

Both practices are already enforced in code and proven across 85 active metrics. Formalization prevents future sessions from bypassing the reservoir (ad-hoc creation) or using non-authoritative progress signals (session notes, memory files). The red-team audit (PLN-457cd0 v2) and grounded audit (SES-464df9, v3) both relied on the reservoir ledger as ground truth — it must be the declared SSOT.

## Context

The MCF enrichment program (PLN-457cd0) manages 12,507 candidate metrics. Two practices emerged organically during Phase 0 and Wave 0-2 and need formalization as standing governance:

1. **From-seed-only authoring:** Every metric authored through the MCF panel MUST originate from a seed_metric record in `mcf.seed_metric`. No ad-hoc metric creation outside the reservoir. This ensures the reservoir is the single progress tracker and prevents shadow metrics that bypass triage, dedup, and classification.

2. **Reservoir status ledger as progress SSOT:** The `mcf.seed_metric.status_code` field (candidate/superseded/published/deferred/queued/in_review) is the authoritative progress signal. Burn-down queries (`SELECT status_code, count(*) FROM mcf.seed_metric GROUP BY 1`) are the canonical KPI, not session notes or memory files. Wave 0 shipped the ledger (PR #413). The onboarding orchestration schema (DEC-f90ba3) extends this with per-step pipeline state but does not replace the ledger as authority.

## Decision

### D1: From-seed-only authoring
Every MCF panel run (M12) MUST reference a `seed_metric_id`. The intake controller validates this — panel admission without a seed back-pointer is rejected. Operator-direct intake (`POST /api/mcf/intake`) also requires `seed_metric_id`. This is already enforced in the intake controller; this ADR formalizes it as standing policy.

### D2: Reservoir status ledger
`mcf.seed_metric.status_code` transitions are the progress SSOT:
- `candidate` → `queued` (triage pass)
- `queued` → `in_review` (intake created)
- `in_review` → `published` (MCV activated)
- `candidate`/`queued` → `superseded` (semantic dup detected)
- `candidate`/`queued` → `deferred` (blocked, not rejected)
Never `rejected` for a dup — always `superseded` or `deferred`.

### D3: Duplicate disposition vocabulary
Pre-panel dedup gate uses `superseded` for confirmed dups (intent matches an active MC) and `deferred` for uncertain cases. Never `rejected` — a dup against one source family may be valid for another.

### D4: Re-verification mandate
Counts and gates must be re-verified against the live DB before every wave (PLN-457cd0 §1 standing rule). Memory-sourced claims are systematically stale.
