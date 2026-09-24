---
uid: DEC-80eade
title: "Legacy metric corpus retirement — single MCF corpus, bc-core re-points, W5 drops"
description: "Legacy metric corpus retirement — single MCF corpus, bc-core re-points, W5 drops"
status: implemented
date: 2026-09-19T12:19:30.584Z
project: bc-core
domain: metrics
subdomain: metrics/legacy-retirement
focus: lifecycle
---

# Legacy metric corpus retirement — single MCF corpus, bc-core re-points, W5 drops

## Context

Grounded study 2026-09-19 (docs/design/metric-world-grounded-study-2026-09-19.md) reconciled four lenses: decision trail (primary intent), live DB counts, code consumers, and DevHub task registry. Intent trail shows legacy formally superseded (authoring 410 D481/DEC-7bdd03; activation 410 D547/DEC-d9fa49; materialization paused DEC-7b15c7; runtime reads mcf.* directly DEC-483f1e; MCF-native projection DEC-b049f6; chain_status dropped DEC-9c0da7). Row-count alone was shown unreliable (metric_definition is 0 in dev only due to the greenfield wipe TSK-20f5e1, but 2271 in golden and KEEP). Anchor reconciliation: DEC-468d01 governs src/registry file cleanup, NOT the binding re-point; the re-point had no DEC of record until this one.

## Decision

The platform keeps ONE metric corpus — MCF (mcf.*). The legacy metric world is retired on an abandon-don't-translate basis (legacy is 0-row in golden AND dev; no legacy->MCF backfill; name-bridging ~4/70 rejected). Scope: (1) DROP target = contract.metric_contract, contract.metric_contract_version, contract.metric_contract_approval, contract.chain_trace; (2) the metric.* legacy AUTHORING tables (metric_binding, metric_formula/_variable/_verification, metric_knowledge, mc_dependency, metric_enrichment_job, lifecycle_event_log, metric_contract_version_activation_log) are retired with their code — function is preserved by MCF successors (metric_binding->mcf.metric_variable_binding; metric_knowledge->mcf.metric_knowledge_profile; mc_dependency->mcf.mcv_closure_dependency; formula->mcv formula_ast_canonical_json + metric_self_verification_result/_fixture + formula_explanation_binding; activation_log->mcf.certification_record; enrichment_job/lifecycle_event_log concept-superseded by panel authoring + governance-state/cert); (3) metric.metric_definition is KEPT (separate populated registry, 2271 rows in golden, 30+ consumers, still extended by ADRs); (4) MCF adjacent machinery, the MLS system, readiness_ledger, metric_discipline, and non-metric contract families are KEPT. Ownership is split: bc-core owns the re-pointing engineering (task of record TSK-d21b97 '5 repoint jobs off contract.metric_contract/metric.* onto MCF'; the chain-status/display re-point ①/⑤/④ is the sibling thread TSK-296271, merged); DB-Foundation Wave W5 owns ONLY the final DROP TABLE (custody DEC-591eb7), gated behind the re-point via the drop-readiness checklist. ARPI (D429 Step-5) MCF->legacy writer is abandoned per DEC-483f1e. Execution is phase-gated (Phase 0 read-only binding-id-space audit -> schema approval -> devhub-writer lockstep -> per-phase auditor review) and operator-run; no live drop is Claude-run.
