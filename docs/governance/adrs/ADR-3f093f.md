---
uid: DEC-3f093f
title: "MCF Canonicality and Legacy Runtime Boundary"
description: "MCF Canonicality and Legacy Runtime Boundary"
status: decided
date: 2026-06-02T06:01:19.466Z
project: bc-docs
domain: mcf
subdomain: legacy-bridge
focus: governance
---

# MCF Canonicality and Legacy Runtime Boundary

> **Amended by DEC-61f7c8 / D428 (decided 2026-06-07).** The metric-contract **store mechanism** in this ADR (Decisions 1–5: `mcf.*` canonical + no legacy writes + future `mcf → NEW shadow` projection) is amended to the **"clean single published metric-contract store"**: `contract.metric_contract*` = the single clean published runtime store (MCF materializes into it after clean-slate adoption); raw Postgres `mcf.seed_metric` operational reservoir (Mongo/export = preserved upstream seed archive); panel = the enrichment mechanism; legacy archived/exported then wiped under a governed DBCP. **D426's anti-contamination goal and its runtime-boundary + three-store findings remain in force.** See `docs/adrs/ADR-61f7c8.md` + `docs/implementation/mcf-d426-amendment-draft-2026-06-07.md`.

## Context

End-to-end M12 (AI authoring panel) + M12.5 (materialization) succeeded for `average_revenue_per_invoice` on intake `6fa62a0b-5004-4a68-94b4-0761b5b0c271`, producing the first clean MCF substrate row: metric_contract_uid `49cdde1a-8bb3-41ad-9f67-9bb05d9f18a0`, metric_contract_version_uid `8c088f55-5cd2-41f0-a1e6-501dce0fe104`, with `governance_state_code='draft'` per HA-6 (MCV stops at draft). Verifier verdict pass. Intake transitioned `pending → consumed_by_panel`. Lifecycle proof supported by three merged PRs in bc-core: #204 (Checker turn budget 8→12 via per-role `turnBudgetFor`), #205 (L-V1g pre-TX-A `temporal_gate_params_json` kernel precheck + preflight parity), and #206 (Maker prompt teaches per-shape temporal_gate_params_json grammar from M7/M8 §9.3).

This proof establishes MCF as a working authoring pipeline. It does NOT establish that legacy runtime can be replaced.

## Decision

1. **MCF is canonical for newly authored metric contracts.** `mcf.metric_contract*` (mcf.metric_contract, mcf.metric_contract_version, mcf.certification_record, mcf.metric_self_verification_fixture, mcf.metric_self_verification_result, mcf.metric_publication_eligibility_result) is the authored truth for any metric admitted through the MCF M11 → M12 → M12.5 pipeline.
2. **Legacy stores remain operational and runtime surfaces until proven replaceable.** `metric.metric_definition`, `contract.metric_contract`, and their dependent runtime graph (`metric.metric_binding`, `metric.metric_knowledge`, `metric.metric_formula`, `metric.metric_formula_variable`, `metric.metric_formula_verification`, `metric.readiness_ledger`, `metric.metric_contract_version_activation_log`, `metric.mls_trigger_binding`, `metric.metric_enrichment_job`, `metric.metric_discipline`, `contract.metric_contract_version`, `contract.metric_contract_approval`, `contract.chain_status`, `contract.mc_integrity_state`, `contract.chain_trace`, `contract.contract_lineage`, `tenant.contract_binding`, `tenant.tenant_binding`) continue to serve UI catalog reads, evaluator wiring, chain integrity, readiness state, tenant runtime, and append-only audit history.
3. **MCF does not directly write into legacy runtime tables.** HA-1 (no legacy `metric.*` writes from M12.5 materialization) extends to M13 (PE-MC evaluator writes only to `mcf.metric_publication_eligibility_result`) and M14 (publication updates only `mcf.metric_contract_version.governance_state_code` + inserts one `mcf.certification_record`). The legacy graph is not a write target for any MCF M-series service.
4. **No truncation, cleanup, or replacement of legacy stores before a proven projection strategy.** Any cutover that mutates `metric.metric_definition`, `contract.metric_contract`, or their dependents requires a separately authorized ADR with an explicit projection function, default/null/lossy field policy, append-only-log preservation policy, runtime smoke-test plan, and rollback plan.
5. **No compatibility projection before M14 active-state proof.** Until at least one metric reaches `governance_state_code='active'` on `mcf.metric_contract_version` through a successful M13 PE-MC pass + M14 publication, there is no MCF-active row to project from. Any projection design before that point is theoretical.

## Why M12/M12.5 success does NOT mean legacy runtime can be replaced yet

Three independent constraints, each of which would block replacement:

**(a) M13/M14 are not yet open.** HA-6 holds the new MCV at `draft`. No MCF metric is currently active. Without an `active` state on at least one MCF metric, the projection has nothing to project from, and the consumer query pattern documented in `mcf-legacy-bridge.md` (MCF-first, legacy fallback) cannot return a row from the MCF side. The lifecycle proof completes M11→M12.5; M13 and M14 remain CLOSED until separately gated.

**(b) Schema asymmetry is substantial.** `metric.metric_definition` carries 37 columns; `mcf.metric_contract` carries 17. Approximately 22 of 37 legacy columns have no native MCF equivalent — `discipline_code` (NOT NULL), `composition_code` (NOT NULL), `direction_code` (NOT NULL), `maturity_code` (NOT NULL), `type_code`, `purpose_code`, `shape_code`, `temporality_code`, `precision_code`, `impact_code`, `temporality_kind`, `verification_result_code`, `verification_evidence_id`, `industry_category_code`, `needs_revalidation` (NOT NULL), `readiness_min_snapshots`, `readiness_max_freshness_days`, `shape_params_json`, `metric_seq` (NOT NULL), and tag/locking fields. Projecting from MCF would set roughly 59% of legacy fields to defaults, nulls, or denormalized intake-provenance reads. The projected row is structurally complete (satisfies NOT NULL constraints) but semantically thinner than the legacy row it would replace.

**(c) Coverage gap.** As of this ADR, `mcf.metric_contract` holds 1 active row (the draft `49cdde1a-…`) and 2 archived audit specimens. `contract.metric_contract` holds 780 active rows. `metric.metric_definition` holds 1241 rows. Even with M13/M14 open, populating 780–1241 metrics through the AI panel + materialization pipeline is a multi-quarter sustained-budget exercise (≈125s per success + non-trivial failure rate). A cutover before MCF coverage approaches legacy would create a regression event in the running platform.

## Three-store reality

The platform carries three metric-shaped surfaces, with overlap but no identity:

| Surface | Row count | Role | Authority |
|---|---:|---|---|
| `metric.metric_definition` | 1241 | Pre-MCF seed catalog — enriched flat metric library with knowledge (1:1), formula, discipline, readiness policy | Legacy candidate reservoir + UI registration/seed-promote |
| `contract.metric_contract` | 780 (all `archived_at IS NULL`; FK to `metric_definition_id` NOT NULL) | Pre-MCF authored contracts — the existing UI catalog canonical | Legacy authored contract; UI catalog/domain/readiness reads |
| `mcf.metric_contract*` | 3 (1 draft + 2 archived audit specimens) | Canonical going forward per ADR-c3e57f / D422 | MCF authored truth for new metrics |

461 metric_definition rows (1241 − 780) have no `contract.metric_contract` row — an existing dual-state inconsistency that predates MCF and is independent of this boundary.

The current bc-admin UI reads `contract.metric_contract` for operational catalog pages (`/catalog/metrics/:function`, `:function/:subfunction`, readiness drill, KpiSpec). It reads `metric.metric_definition` for registration/seed-promote, definition detail, and landscape stats. It does NOT read `mcf.metric_contract*` today; `McfReadService` does not expose a materialized-metric-contract listing endpoint at all (only intake, panel run, transcripts, PE-MC status, and materialization preflight).

## Runtime / chain-integrity blast radius

A single working legacy metric touches approximately 15 tables across 3 schemas (`metric.*`, `contract.*`, `tenant.*`), including append-only audit logs (`metric.metric_contract_version_activation_log` at 1656 rows; `contract.contract_lineage`). Of the ~20 tables in the legacy graph, ~12 are NOT safely rebuildable from MCF — they carry data MCF does not model (operator-curated knowledge, append-only history, legacy classification taxonomy, evaluator/tenant binding state). Any cutover mode that truncates or replaces contents must explicitly except the append-only logs and either preserve, port, or document the loss of the un-modeled fields.

Tenant runtime (`tenant.contract_binding`, `tenant.tenant_binding`) and evaluator wiring (`metric.metric_binding`) hold per-tenant activation state keyed on legacy IDs. Replacing legacy contents with MCF projections requires re-keying or breaking FKs across these tables — a runtime continuity risk that cannot be discharged with a read-side projection alone.

## M14 activation means MCF-internal active

Per `mcf-legacy-bridge.md` and M13 DBCP §0bis: M14 publishes by flipping `mcf.metric_contract_version.governance_state_code` from `approved` to `active`, plus inserting one `mcf.certification_record` row (`action_code='metric_transition'`, `to_state_code='active'`). M14 does NOT create a new "published_metric" table, does NOT write to `metric.metric_definition`, and does NOT write to `contract.metric_contract`. Consumer visibility of an M14-active metric to the bc-admin UI or to tenant runtime is NOT established by M14 alone — it requires either (1) `McfReadService` to expose a list/detail endpoint over active MCs and the UI to consume it, or (2) a projection layer to translate MCF-active rows into legacy shape, or (3) a hybrid. None of these exist today.

Until one of those visibility bridges is built and proven, M14 activation is a state change on the MCF substrate only. It does not imply product / runtime visibility.

## Shadow projection pilot — explicit future work only

When M14 has shipped and at least one MCF metric has reached `governance_state_code='active'`, the smallest safe next step is a single-metric shadow projection pilot, scoped as follows: a deterministic, idempotent projection function `projectMcToLegacy(mcUid) → {metric_definition_row, contract_metric_contract_row}` writes into NEW shadow tables or materialized views (NOT into the live legacy tables); the projection is compared structurally against any matching legacy row; the legacy UI is smoke-tested against the shadow in an isolated environment; the projection's field-mapping table explicitly records every default, null, and lossy mapping. The pilot does not mutate legacy data and does not flip authority. It is gated on a separate ADR.

This boundary ADR does not authorize the pilot. It authorizes only the constraint that the pilot is the next move when the prerequisites land.

## `metric.metric_knowledge` preservation — explicit open question

`metric.metric_knowledge` holds 1241 1:1 enrichment rows: `definition_summary`, `definition_context`, `formula_explanation`, `threshold_source`, `threshold_notes`, `stakeholders` (jsonb), `drivers` (jsonb), `related_metrics` (jsonb), `search_tags` (text array). This is operator-curated knowledge that MCF substrate does not currently model. Any future cutover or projection strategy must address knowledge preservation explicitly: either (a) MCF substrate is extended to carry knowledge metadata (substrate grammar change — Foundation Gate B; requires its own ADR), or (b) `metric.metric_knowledge` is EXCEPTED from any cutover and remains the authoritative source for knowledge regardless of which contract surface (legacy or MCF) is canonical for the metric itself, or (c) an explicit ADR accepts the loss of curated knowledge in MCF-authored metrics. This boundary ADR does not pick among (a)/(b)/(c) — it records that the question is open and must be resolved before any cutover proceeds.

## Non-goals (scope guard)

- No code change is authorized by this ADR.
- No schema change is authorized by this ADR.
- No M13 PE-MC evaluator invocation is authorized by this ADR.
- No M14 publication invocation is authorized by this ADR.
- No write or mutation of any legacy table (`metric.*`, `contract.*`, `tenant.*`) is authorized by this ADR.
- No truncation, replacement, blue-green, or shadow-population of legacy stores is authorized by this ADR.
- No new compatibility projection layer is authorized by this ADR.
- No commitment is made on the MCF-side read-API design (list/detail over `mcf.metric_contract*`) or on the UI migration path. Those are separate decisions to be filed when their inputs are ready.

## Consequences

This ADR locks the platform into the documented `mcf-legacy-bridge.md` dual-authority pattern (MCF-first read, legacy fallback) and forbids the alternative ("clean out legacy and repopulate from MCF") until the three blockers above are addressed. Until those blockers are addressed:
- M13/M14 may be invoked when separately authorized; they will produce MCF-internal state changes only.
- New MCF authoring continues through M11→M12.5; new MCs accumulate as `draft`.
- Legacy authoring paths (`POST /metric-catalog/definitions`, `POST /api/mcf/intakes/from-metric-definition` for path-2 intakes) continue to function.
- bc-admin UI continues to read legacy surfaces. No new UI work depends on MCF-active rows existing.

A future ADR (gated on M14 active-state proof + a knowledge-preservation decision) will design the shadow projection pilot and the visibility bridge. This ADR is the precondition record for that future work, not the design.

## Authority

- Substrate: bc-core `mcf.*` schema (validated this session; live row counts cited above)
- Documented architecture: bc-docs-v3 `docs/operating-model/mcf-legacy-bridge.md`, `docs/implementation/metric-context-framework-m13-pe-mc-evaluator-dbcp.md`, `docs/implementation/metric-context-framework-m14-m12-governance-dbcp.md`, `docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md`, ADR-c3e57f (D422)
- Lifecycle proof: change record `CHG-3e19c5` (session record on `SES-9ad704`, report side) records the M12 + M12.5 success for `49cdde1a-…` with full substrate UIDs and verification invariants.
- bc-core main at adoption: commit `efdc072`
