---
uid: DEC-b049f6
title: "MCF-native readiness projection replaces the legacy metric funnel, dials, and Landscape source — F-021/F-023 disposition"
description: "One thin read-model projection over existing SSOTs (seed ledger, MCV governance states, certification records, mcv_chain_status overlay) replaces MetricFunnelService.getLadder() and every surface that made it canonical; legacy funnel/dial endpoints retire 410-Gone; residue shown as a mandatory labelled sub-line; nightly seed-ledger reconcile added. Supersedes DEC-a8b33e (D397), DEC-28b176, DEC-4ca5a5."
status: decided
date: 2026-08-03T00:31:26.816Z
project: bc-core
domain: metrics
subdomain: metric-lifecycle/readiness
focus: read-model
supersedes:
  - DEC-a8b33e
  - DEC-28b176
  - DEC-4ca5a5
---

# MCF-native readiness projection replaces the legacy metric funnel, dials, and Landscape source — F-021/F-023 disposition

## Context

The funnel preserved a vocabulary that no longer matches the substrate; a crash-only fix would satisfy availability while leaving the authority defect intact (Codex). A projection over SSOTs cannot drift the way the funnel did — every number is a GROUP BY, and substrate changes break it loudly at review time rather than silently at verdict time. Closing F-021 and F-023 together is the both-or-neither condition of the ratification.

## Decision

F-021/F-023 DISPOSITION (ratified fast-lane; design memo DESIGN-MEMO-dial-repair-F021-F023.md at devhub e86c3ef, sha256 fb3c9adc…; Codex disposition ACCEPTED WITH BOUNDARY for Option A, 2026-08-03).

1. THE PROJECTION. A new read-model service (McfReadinessProjectionService) computes the platform readiness view as GROUP BYs over existing SSOTs and NOTHING else: reservoir stages from `mcf.seed_metric.status_code`; authoring stages from `mcf.metric_contract_version.governance_state_code` (draft / review / approved / audit_pending-"awaiting certification" / active); the certified-active split from certification records — **"certified-active" = active MCV + live certification-era `audit_admit` cert; `metric_transition`-only historical actives are a SEPARATE, MANDATORY labelled sub-line** (Codex point 2: never silently merged) until their standing resolves (TSK-fa743d); a chain-health overlay from `mcf.mcv_chain_status` verdict counts — **display-only, never a hidden gate** (Codex boundary; DEC-1e55d3 two-surfaces rule). Tenant runtime-producing counts are NOT platform lifecycle authority and stay off this projection (DEC-57c6d9); they arrive later as a tenant/runtime overlay.

2. RETIREMENTS (the same defect surface travels together — Codex boundary). `MetricFunnelService.getLadder()` and its "sole owner of the ladder's truth" authority; the legacy funnel + readiness-dial endpoints (410 Gone, M17/D547 pattern — strictly better than today's crash); the `mls-14-predicate`; ALL direct `contract.chain_status` reads in the readiness family (incl. metric-readiness.service and the metric-catalog-reader joins), not just getLadder() callers; the tenant-metrics and mls-backfill dependencies on the ladder. bc-admin Landscape repoints to the projection in a follow-up PR (today it consumes a surface that throws; 410 is an improvement in the interim).

3. SUPERSESSIONS. This decision supersedes DEC-a8b33e (D397 canonical 7-stage ladder + single-service ownership), DEC-28b176 (three-dial readiness model), and DEC-4ca5a5 (Metric Landscape reading getLadder as truth) — all three flipped to superseded in the same bc-docs commit (D370 rule 1). Legacy MLS/funnel IMPLEMENTATION claims directly conflicting with the projection are marked historical where touched; the broad MLS ADR-family settlement is DEFERRED to Phase 3's authority ranking (Codex point 4).

4. SEED-LEDGER RECONCILE (Codex point 3). `SeedMetricLedgerService.reconcile()` (forward-only, already built) joins the nightly scheduler step alongside chain-status refresh — the stale `published=6` vs 85 actives was a governance-visible omission. Reconcile remains an explicit act; the scheduler invocation is its cadence, not a new authority.

5. WHAT THIS IS NOT. Not a new lifecycle authority (a projection may never verdict); not a Phase 2/3 expansion; no production data mutation; counts in the memo (271/85/55) are memo-provided pending implementation-review evidence (Codex evidence basis).

Build flow: this ADR → scoped bc-core branch/PR (Codex review) → operator merge → bc-admin follow-up PR → ledger E-9 closes F-021/F-023.
