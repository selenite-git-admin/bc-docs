---
uid: DEC-b54a43
title: "Core chain consolidation: canonical context/onboarding/execution/store path, mark-don't-delete cleanup, core-then-tenant sequencing"
description: "Locks the canonical bc-core chain (context=BCF, onboarding=ContractService+MCF, execution=4 boundaries, store=mcf.*→materialize→contract.metric_contract), a mark-don't-delete cleanup policy for legacy authoring/wizards/mapping + readiness duplicates, a dev-phase data reset, and Phase-1(core+admin)→Phase-2(tenant) sequencing."
status: decided
date: 2026-06-09T15:55:29.723Z
project: bc-core
domain: contracts
subdomain: contracts/core-chain-consolidation
focus: architecture
---

# Core chain consolidation: canonical context/onboarding/execution/store path, mark-don't-delete cleanup, core-then-tenant sequencing

## Context

Months of MCF/BCF migration left the core chain with overlapping legacy + governed surfaces (4-5 metric stores, ~10 readiness surfaces, legacy authoring wizards/mapping, untrusted old tenant data). The re-entry index existing at all is the symptom. A small mis-targeted authoring act (wrong store/path) costs large rework loops. A bounded clarity pass — document the one canonical path per layer, cleanly mark the rest, reset only the data — defuses the rework time-bomb without the opposite trap of boil-the-ocean service deletion. Marking-not-deleting preserves working surfaces (and the only existing authoring UI) while the governed MCF UI is built; sequencing core+admin before tenant ensures the platform-authoring substrate is trustworthy before customer-facing work. Grounded by a 3-cluster read-only deep report (readiness/integrity, runtime/orchestrator, authoring/wizards/mapping) + Foundation (the four evaluation boundaries; three-level governance where tenant Contract Binding = tenant-scoped Z-field/custom extensions, not metric activation).

## Decision

Locks the target architecture for the bc-core "chain" (the four confused layers: context, onboarding, execution, store) after a 3-cluster read-only deep ground report, plus the cleanup policy and sequencing.

CANONICAL SURFACES (one per layer; KEEP):
- CONTEXT (vocabulary): BCF concept_registry (entity.property Business Concepts) + its existing authoring UI. Legacy BO/BF/CF physically removed (D417/D418).
- ONBOARDING (authoring): ContractService is the single authoring path for SC/AC/OC/CC (draft→review→approved→active), with D430/D431 concept-identity resolvers gating OC/CC activation against BCF concepts. MCF (intake→M12 panel→M13→M14) is the single Metric Contract authoring path; legacy MC authoring stays quarantined (D432).
- EXECUTION (runtime): the four evaluation boundaries (Admission→Canonical→Metric→Action) driven by OrchestratorService, with real production triggers (reader-driven auto-eval + readiness-ledger dispatch). The runtime evaluates contract.metric_contract.
- STORE: mcf.* is the SOLE metric authority; contract.metric_contract is a DERIVED runtime projection populated by the MCF→legacy materialization bridge (KEPT, per DEC-7ab22b/D429). Trust VERDICT = MCF M13/M14 evidence; lifecycle SSOT = MetricFunnelService (D397); chain-completeness verdict = ChainStatusService (D305, vestigial for metrics once all-MCF).

CLEANUP POLICY — MARK, DON'T DELETE: legacy/duplicate services + UI (the SC/AC/MC authoring wizards, the embedded mapping tools, canonical_mapping/cc_field_mapping, the POST /metric-definitions leak, deprecated IntegrityService, the readiness redundancies) are NOT deleted in this drive. They are cleanly MARKED legacy/WIP and FIXED later — including building a governed MCF authoring UI to parity with the existing BCF authoring UI. Hasty service deletion is the rework risk; documentation + clean marking is the clarity mechanism.

DATA RESET (DEV ONLY): Invariant III (immutability) governs PROD, not dev historical cleanup. Approved: reset old metric versions to clean 1.0.0, delete the legacy metric corpus + status-sprawl data (recomputable), and DROP the old/untrusted tenant DBs (apex, sandbox1) + provision a fresh pilot tenant. Old tenant data was produced from incorrect/ungoverned legacy semantics and is discarded, not migrated (a fresh tenant is the Invariant-III-correct way to handle untrusted history).

SEQUENCING: Phase 1 = make bc-core + bc-admin (the chain) clean, governed-with-UI, and documented (this ADR + the golden-path SSOT doc). Phase 2 (later) = the tenant side: bc-portal (customer UI) + Rooth (AI). No portal/Rooth work until Phase 1 is in place and documented.

ACCEPTANCE PROOF (Phase 1): one AR metric proven end-to-end on the clean path — BCF concepts → fresh OC/CC bound to BCF → MC authored via MCF → materialize → fresh tenant + tuned SDG → runtime → a Metric Snapshot whose readiness is its M13/M14 evidence.
