---
uid: DEC-61f7c8
title: "MCF Clean Single Published Metric-Contract Store (amends D426)"
description: "Amends D426: contract.metric_contract* = single clean published runtime metric-contract store; MCF authors, panel enriches, raw Postgres seed reservoir; legacy archived then wiped under DBCP."
status: decided
date: 2026-06-07T05:25:11.857Z
project: bc-core
domain: contracts
subdomain: metric-store
focus: store-architecture
---

# MCF Clean Single Published Metric-Contract Store (amends D426)

## Context

The 2026-06-07 panel-side enrichment experiment validated that the MCF panel self-enriches from thin seeds (E2; panel_run b85186ef + 088e22f9), so the raw seed catalog can be the candidate reservoir and no batch pre-enrichment pipeline is needed. A single clean published store (contract.metric_contract*) is a more maintainable anti-contamination mechanism than D426's separation+shadow approach: it reuses the tested runtime engine unchanged and avoids a permanent projection bridge that future engineers must mentally simulate. Postgres is chosen as the operational reservoir for single-datastore maintainability (no Mongo runtime dependency in the authoring path); Mongo/export is retained as the preserved upstream seed archive.

## Decision

Amends DEC-3f093f / D426 (MCF Canonicality & Legacy Runtime Boundary) on the metric-contract STORE mechanism, preserving D426's anti-contamination goal and its runtime-boundary + three-store findings.

TARGET ARCHITECTURE (the decision; not conditional):
1. MCF = governed authoring framework (intake -> M12 panel -> PE-MC eligibility -> certification -> lifecycle).
2. Candidate reservoir = raw Postgres mcf.seed_metric, refreshed from Mongo bc_seed.seed_metrics (12,501) via a governed import; Mongo/export = preserved upstream seed archive; runtime/MCF reads Postgres.
3. Panel = the enrichment mechanism (validated 2026-06-07: self-enriches from thin seeds via BCF tool calls; no batch pre-enrichment pipeline; metric_knowledge not required as a candidate source).
4. contract.metric_contract* = the single clean published runtime metric-contract store after clean-slate adoption; published MCs materialize here; the existing runtime engine consumes it unchanged.
5. Legacy metric/contract data archived/exported, then wiped under a governed DBCP (golden snapshot + rollback).
6. metric_knowledge preserved as historical reference/evidence (expensive AI-enriched work), NOT future authority; archived/exported before wipe.
7. Runtime engine UNCHANGED (reads contract.metric_contract_version.contract_json -> progression.metric_evaluation -> typed fact.*).
8. D400 (grammar v1.1), D401 (open-item canonical), D427 (references) remain SEPARATE gates, not resolved here.
9. GUARDRAIL: no MCF materialization into contract.* and no legacy wipe until this amendment AND its implementing DBCP(s) are approved.

RELATIONSHIP TO D426: D426 chose 'mcf.* canonical + no legacy writes + future mcf->shadow'. This amends those store-mechanism decisions to 'contract.metric_contract* = single clean published store; MCF materializes into it; legacy archived+wiped'. D426's runtime-boundary and three-store-reality findings remain in force; the affected D426 store decisions should be annotated to point here (follow-up). Not a wholesale supersession.

SUPPORTING ARTIFACTS (bc-docs-v3/docs/implementation/): mcf-d426-amendment-draft-2026-06-07.md (full amendment text), mcf-seed-reservoir-postgres-design-2026-06-07.md (reservoir design check), mcf-enrichment-experiment-2026-06-07.md (E2 validation).

Wording discipline: "clean single published metric store", never "reuse legacy".
