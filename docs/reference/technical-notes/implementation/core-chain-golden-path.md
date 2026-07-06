---
title: Core Chain Golden Path — the canonical context → onboarding → execution → store path
description: The single positive "here is THE path" reference for the bc-core chain, per DEC-b54a43 (D437). Names the one canonical surface per layer (vocabulary, authoring, runtime, store, readiness verdict); the cleanly-marked legacy/WIP surfaces to fix later (mark-don't-delete); the dev-phase data reset keep/delete list; the Phase-1 (core+admin) → Phase-2 (tenant) sequencing; and the one-AR-metric acceptance proof. Authoritative orientation for the chain.
status: active
date: 2026-06-09
project: bc-core
domain: contracts
subdomain: core-chain-consolidation
focus: architecture
governs: DEC-b54a43 (D437)
change_record: (consolidation ADR)
---

# Core Chain Golden Path

> **What this is.** The ONE canonical path through the bc-core "chain" — *context → onboarding → execution → store* — and the disposition of everything else. Per **DEC-b54a43 / D437**. Where the MCF re-entry index says "don't get fooled by legacy," this says **"here is the one real path; everything else is cleanly marked legacy/WIP, NOT deleted."** Authoritative for the chain; grounded in a 3-cluster read-only deep report (readiness/integrity · runtime/orchestrator · authoring/wizards/mapping) + Foundation.

## 1. The canonical path (one surface per layer — KEEP)

| Layer | Canonical surface | Store / table | Service / entrypoint |
|---|---|---|---|
| **Context** (vocabulary) | BCF Business Concept Registry (`entity.property`) + its bc-admin authoring UI | `concept_registry.*` | `/api/bcf/*` |
| **Onboarding** (SC/AC/OC/CC) | `ContractService` (draft→review→approved→active); D430/D431 concept gates on OC/CC activation | `contract.{source,admission,observation,canonical}_contract(_version)` | `/api/contracts/*` + connector-onboarding |
| **Onboarding** (MC) | **MCF** (intake→M12 panel→M13→M14); legacy MC authoring quarantined (D432) | `mcf.*` | `/api/mcf/*` |
| **Materialize** (bridge) | MCF active MCV → `contract.metric_contract` (DERIVED projection) | `contract.metric_contract(_version)`, `metric_definition_id` NULL | McfArpiMaterializationWriterService |
| **Execution** (runtime) | 4 boundaries (Admission→Canonical→Metric→Action) via `OrchestratorService`; reads `contract.metric_contract` | tenant `fact.*` + `progression.*` + `evidence.*` | OrchestratorService · ReaderRuntime · ReadinessEvaluationDispatcher |
| **Store authority** | `mcf.*` = SOLE metric authority; `contract.metric_contract` = derived projection | `mcf.metric_contract(_version)` | — |
| **Trust verdict** | **MCF M13/M14 evidence** | `mcf.metric_publication_eligibility_result`, `mcf.certification_record` | McfReadinessBridgeService |
| **Lifecycle SSOT** | `MetricFunnelService` (D397; Seed→…→Live ladder) | projects the above | `/api/registry/metric-funnel/*` |

### End-to-end flow
```
BCF concepts → SC→AC→OC→CC (ContractService, bound to BCF) → MC (MCF: intake→M12→M13→M14)
   → materialize active MCV → contract.metric_contract (derived)
   → runtime 4 boundaries on the tenant's data (reader / orchestrator / dispatcher)
   → SO → CO → Metric Snapshot   (+ Evidence + Lineage in the tenant store)
   → trust verdict = the metric's M13/M14 evidence
```

## 2. Cleanly MARKED legacy/WIP — fix later, DO NOT delete or extend
Per DEC-b54a43, these are kept + marked, not deleted. Each has a fix-later task.

| Surface | Layer | Why legacy | Fix-later task |
|---|---|---|---|
| bc-admin SC/AC/MC create wizards (`CreateSourceContractPage`, `CreateAdmissionContractPage`, `CreateMetricWizardPage`) | onboarding UI | POST `/contracts` / `/metric-definitions` directly, bypassing the governed path | TSK-a6502d |
| `POST /metric-definitions` (legacy metric store write) | onboarding | competes with MCF | TSK-a6502d |
| **(GAP) governed MCF authoring UI — does not exist** (BCF has one, MCF doesn't) | onboarding UI | metric authoring is API-only today | **TSK-c6f0be (build it)** |
| `canonical_mapping` / `cc_field_mapping` tables, `MappingBindingService`, FieldResolution/MappingBindings pages | mapping | superseded by BCF concept binding (DEC-02f5a9, D430/D431); `cc_field_mapping` already dead | TSK-7a2699 |
| `IntegrityService` (still wired to the activation gate) + `computeTenantGates` redundancy + `l_node` gate | store/readiness | superseded by ChainStatusService (D305) + MetricFunnelService (D397) | TSK-a714a6 |

## 3. Data reset (DEV only) — keep / delete
Invariant III governs PROD, not dev historical cleanup. Golden snapshot first; specific approval before execution (TSK-20f5e1).

- **DELETE:** legacy `contract.metric_contract` corpus (778 archived + 732 active-on-archived versions); status-sprawl DATA (`chain_status`, `l_node_*`, `mc_integrity_state`, `chain_trace` — recomputable); old tenant DBs (`tbc_apex_dev`, `tbc_sandbox1_dev`).
- **RESET:** curated OC/CC/MC re-authored fresh at 1.0.0 via the governed path.
- **KEEP:** BCF `concept_registry`, `master.*` dimensions, the ~28k SC/AC catalog, MCF machinery, the runtime engine, and **all authoring services/UI (marked, not deleted)**.
- **PROVISION:** one fresh pilot tenant DB from canonical DDL.

## 4. Sequencing
- **Phase 1 — bc-core + bc-admin (the chain):** clean + governed-with-UI + documented. Includes the data reset, the MCF authoring UI, the marked-legacy fixes, and the AR-metric proof. **← we are here.**
- **Phase 2 — tenant (later):** bc-portal (customer UI) + Rooth (AI). Not started until Phase 1 is in place and documented.

## 5. Acceptance proof (Phase 1) — TSK-f77fd2
One AR metric, end-to-end on the clean path, producing a trustworthy tenant Metric Snapshot whose readiness is its M13/M14 evidence. Start with the simplest atomic AR metric (e.g. *Total Outstanding AR* off SAP `BSID` open items).

## 6. Open tasks
| Task | What | When |
|---|---|---|
| TSK-20f5e1 | Data reset DBCP (golden snapshot + keep/delete + fresh tenant) | Phase 1 · next |
| TSK-f77fd2 | One AR metric end-to-end proof | Phase 1 · next |
| TSK-c6f0be | Build governed MCF authoring UI (BCF parity) | Phase 1 · later |
| TSK-a6502d | Mark + later-fix legacy authoring wizards + `/metric-definitions` leak | later |
| TSK-a714a6 | Migrate activation gate off IntegrityService; retire integrity/readiness redundancies | later |
| TSK-7a2699 | Mark + later-retire legacy mapping surfaces | later |

## 7. References
- ADR: `docs/adrs/ADR-b54a43.md` (DEC-b54a43 / D437)
- Foundation: `the-evaluation-boundaries.md` (four boundaries) · `the-contract-grammar.md` (three-level governance; tenant Contract Binding = tenant-scoped Z-field/custom extensions, not metric activation)
- Lineage referenced (kept, not superseded): D305 chain-status · D397 funnel · D432 legacy-MC guard · DEC-02f5a9 BCF · DEC-7ab22b/D429 materialization · D430/D431 concept resolvers
- Orientation: `mcf-re-entry-index.md`
