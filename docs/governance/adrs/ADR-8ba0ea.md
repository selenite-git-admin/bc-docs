---
uid: DEC-8ba0ea
title: "Onboarding lifecycle-state SSOT = bc-core; DevHub onboarding is a thin planning view (D501-sibling; amends D494)"
description: "Onboarding lifecycle-state SSOT = bc-core; DevHub onboarding is a thin planning view (D501-sibling; amends D494)"
status: decided
date: 2026-07-08T03:18:53.416Z
project: bc-core
domain: metrics
subdomain: mcf-onboarding/state-ssot
focus: architecture-boundary
---

# Onboarding lifecycle-state SSOT = bc-core; DevHub onboarding is a thin planning view (D501-sibling; amends D494)

## Context

No rationale recorded.

## Decision

CONTEXT (verified live, SES-fe423b map). DevHub's onboarding_candidate store (devhub.db, D494/DEC-f90ba3; its own comment: 'DevHub = orchestration state; bc-core = governed truth') has drifted into independently OWNING metric-onboarding lifecycle state — the same class of boundary violation D501 corrected for the preflight/generator/drive. Findings:
- onboarding_candidate.pipeline_state (a 16-state devhub-defined enum) parallels bc-core mcf.seed_metric.status_code (candidate→queued→in_review→authored→published + terminals). It is advanced ENTIRELY by the DevHub metric_workflow (onboarding-sync.js STEP_TO_STATE; substrate UIDs regex-scraped from the workflow's free-text evidence), and is NEVER reconciled against the bc-core substrate. Result: 3 disagreeing sources of onboarding truth — bc-core substrate (~111 active MCVs), bc-core seed_metric.status_code (~19, reconcile lagging), devhub pipeline_state (85 activated).
- bc-core ALREADY has the authoritative derive: SeedMetricLedgerService.reconcile() forward-derives status_code from committed substrate (in_review←panel_run, authored←metric_create cert, published←active MCV), idempotent + self-backfilling, with per-event primitives. This is the SSOT the devhub store duplicates.
- DevHub-UNIQUE (no bc-core home): family_code, wave_code, class_code, priority_code, the blocker registry (onboarding_blocker), envelope_path, and cost/telemetry (panel_cost_usd, panel_duration_sec, attempt_count). bc-core seed_metric has only function_code/subfunction_code — no family/wave/class/priority/wave-planning concept anywhere. These are genuine program-planning taxonomy.

FOUNDATION / D501 BOUNDARY. The metric-onboarding LIFECYCLE STATE (what stage each metric is at) is DOMAIN state — it belongs to bc-core, the domain owner, and must derive from the substrate (single source, no drift). The PROGRAM-PLANNING taxonomy (how we sequence the enrichment: family/wave/priority/blockers/cost) is dev/ops COORDINATION — legitimately DevHub's, and has no bc-core home. This is exactly the D501 split applied to onboarding.

DECISION.

T1 — SSOT = bc-core. bc-core mcf.seed_metric.status_code (substrate-derived via SeedMetricLedgerService.reconcile) is the single authority for onboarding lifecycle state. DevHub does NOT independently track or advance lifecycle state.

T2 — DevHub onboarding views DERIVE state from bc-core. The read tools/boot banner (devhub_onboarding_queue, devhub_onboarding_stats, session_boot MCF ONBOARDING line) resolve lifecycle state by joining the devhub planning overlay to bc-core status_code (by seed_metric_id), not from the local pipeline_state. Retire the pipeline_state write paths — onboarding-sync.js auto-advance + devhub_onboarding_advance's state mutation + the block→state write — so DevHub no longer authors lifecycle state. (devhub_onboarding_block keeps writing the BLOCKER, which is planning; it stops writing pipeline_state.)

T3 — DevHub KEEPS the planning overlay. family_code, wave_code, class_code, priority_code, the blocker registry, cost/telemetry, and envelope_path stay in DevHub, keyed to seed_metric_id — genuine dev/ops coordination with no bc-core home. The import + family/wave-assign scripts stay (they seed the planning overlay); import maps bc-core status→display but does not own it.

T4 — Reconcile the drift. Run SeedMetricLedgerService.reconcile() so seed_metric.status_code matches the substrate (fixes 85 vs 19 vs 111), then the DevHub view reflects truth. This is the fast first step and is the prerequisite for trustworthy coverage numbers (e.g. the finance GL/treasury/etc. done-vs-open split).

T5 — AMENDS D494/DEC-f90ba3. D494 introduced onboarding_candidate as 'orchestration state'; that orchestration state is now DERIVED from bc-core truth, not independently advanced. The finer transient workflow steps (preflight_pass/panel_submitted/…) belong to the DevHub metric_workflow (WFL) record if wanted, not to onboarding_candidate's persistent state.

CONFORMANCE. Single-source lifecycle state (derived from the immutable substrate) — no drift, auditable (bc-core Invariant discipline). No independent domain-state write in the dev/ops hub (D501 boundary). Planning overlay is additive coordination, join-keyed, never a truth source for state.

WHAT THIS DOES NOT SOLVE. Near-real-time state (reconcile cadence: nightly + per-event primitives already exist; wiring them is impl). A bc-core home for family/wave IF the taxonomy is ever deemed domain (currently kept devhub-side). The metric_workflow (D492 Layer-2) thinning itself (tracked under D501).

MIGRATION PHASES. A (this ADR): decision. B: run reconcile → status_code authoritative + backfilled (fast). C: repoint devhub queue/stats/boot to derive state from bc-core status_code; retire onboarding-sync auto-advance + pipeline_state writes; keep the planning overlay. RELATIONSHIP: D501-sibling (same boundary); amends D494.
