---
uid: DEC-acce2b
title: "CC-v2 canonical resolution engine — runtime SO→CO for field_selection contracts (replaces canonical_mapping resolver)"
description: "Build a CC-v2-native canonical resolver: OC-v2 source_references + CC field_selection/derivations → join fact.so_* → stamp fiscal_period → write fact.co_*. The legacy canonical_mapping resolver cannot serve CC-v2 (mechanism superseded + empty)."
status: implemented
date: 2026-07-02T05:43:51.783Z
project: bc-core
domain: contracts
subdomain: contracts/canonical
focus: runtime
---

# CC-v2 canonical resolution engine — runtime SO→CO for field_selection contracts (replaces canonical_mapping resolver)

## Context

fact.so_* persistence is proven on pilot1 and the reverse-walk (DEC-4aa2fd) now binds + provisions fact.co_ tables, but they stay empty because no runtime reads the CC-v2/OC-v2 declarations to produce Canonical Objects — the sole CO writer is gated on the superseded, now-empty canonical_mapping. This is the single blocker between admitted typed facts and every downstream metric snapshot for the entire CC-v2 population. Locking the resolver design against the live declaration surfaces (OC-v2 source_references + CC field_selection/derivations, with the shared deriveCcGrainEntityId identity) before building prevents re-deriving canonical meaning ad-hoc per metric and keeps the SO→CO boundary as the one place canonical meaning is produced (Invariant I).

## Context (live-verified 2026-07-02, tbc_pilot1_dev + bc_platform_dev)

Runtime canonical resolution (Source Object → Canonical Object) is not wired for the CC-v2 contract architecture. Concretely:

- **`contract.canonical_mapping` is empty system-wide (0 rows).** The mechanism is superseded (DEC-02f5a9); canonical field-resolution now lives in the Canonical Contract body (`field_selection` + `derivations`) per D439/D461/D462, and source declaration lives in the OC-v2 body `source_references`.
- **The only code that writes `fact.co_*` is `CanonicalResolutionService.resolveRun`/`resolveGroup`, and it is `canonical_mapping`-gated** (`MappingBindingRepository.findBindingById` → `normalizeMappingBody`). With zero mapping rows it can resolve no contract. Its input model (`source_dependencies`, `join_context`, `canonical_mapping[]`) is the superseded shape.
- **arpi_slice is pure CC-v2:** its sources are declared by OC-v2 `source_references` (e.g. `oc__customer_invoice_arpi_slice_type_sd_s_map` v3 → `source_table=TYPE_SD_S_MAP` with `sc_version_id`/`ac_version_id` + `role`/`cardinality`), and its canonical fields by the CC body `field_selection` (business_concept_id → canonical_field) + `derivations` (e.g. `due_date`, `clearance_time`).
- The D429 Step-5 `McfArpiMaterializationWriterService` is NOT a resolver — it synthesizes a legacy `contract.metric_contract` from an MCF metric and explicitly never writes fact/progression projections.

Net: `fact.so_*` is populated (pilot1: bsad 1716 / kurgv 200 / type_sd_s_map 2052), and `fact.co_customer_invoice_arpi_slice_v8_0_0` now exists (0 rows) — but nothing can populate it. This is the genuine runtime-readiness boundary (contract-gate-eligible ≠ runtime-ready) for every CC-v2 metric, AR Balance being the first case.

## Decision (proposed — design lock; implementation to follow on approval)

Build a **CC-v2-native canonical resolution engine** that reads the live CC-v2/OC-v2 declarations (never `canonical_mapping`) and produces Canonical Objects:

1. **Source discovery from OC-v2.** For the target CC, gather every active OC-v2 whose `field_mappings` feed the CC's `field_selection` concepts; read their `source_references` (`source_table`, `sc_version_id`, `ac_version_id`, `role`, `cardinality`) to identify the `fact.so_*` tables and their join roles (header/line/lookup) and join keys.
2. **Join over typed facts.** Join the identified `fact.so_*` rows by the declared keys (multi-source, e.g. BSAD ⋈ TYPE_SD_S_MAP), honoring cardinality, into one row per grain instance. No envelope/JSONB hop — read the typed fact store (post-M2.5).
3. **Project + derive canonical fields.** Map source fields → canonical fields via the OC field_mappings (business_concept_id) intersected with the CC `field_selection`; compute the CC body `derivations` (D461/D462) — the same derivation set the C1/C2 chain gates and PE-MC-13 read (one derivation, no fork).
4. **Stamp fiscal grain.** Stamp `fiscal_period`/`fiscal_year`/`period_number` via `FiscalCalendarService` from the CC's `posting_date_field` (D363–D365), exactly as the legacy path did (`enrichFiscalPeriod`).
5. **Emit CO + evidence.** Write `fact.co_{cc}_v{ver}` (typed) + `progression.canonical_evaluation` + evidence + lineage, reusing the existing `EvaluationRepository.createCanonicalObject` writer and the identity rule `canonical_object_id == canonical_evaluation_id == evaluation_id` (so `FactReaderService`/`CoCandidateReader` and the governed metric engine resolve the same UUID). Idempotent (skip grain instances already resolved).
6. **Grain-CC identity is the shared derivation.** The CC a resolution run targets is picked by `deriveCcGrainEntityId` (same rule as `CoCandidateReader.pickGrainCc` and the reverse-walk DEC-4aa2fd) — never `canonical_mapping`.

Trigger surfaces (later increment): reader-runtime post-admission (replacing the `autoResolveForOc` call), and a platform-scoped on-demand endpoint for backfill (mirrors `onboard-metric`). SELECT-then-evaluate; reads never trigger evaluation elsewhere.

## Repair-location & Foundation

- **Location D (evaluation boundary implementation)** — the Canonical Evaluation runtime for CC-v2. NOT B (the CC-v2/OC-v2 grammar is sound and already declares everything needed), NOT C (bindings/field_selection exist), NOT A (sources emit correctly; fact.so_ is populated). Building CO production at its own boundary is the opposite of lower-layer compensation.
- **Invariant I (meaning evaluated once):** canonical meaning is produced exactly at the canonical evaluation boundary — this ADR builds that boundary for CC-v2 rather than faking COs downstream.
- **Invariant II (ordering fixed):** SO → CO strictly; CO carries its admitted-record lineage.
- **Invariant IV (references explicit):** the resolver traverses only explicit declarations (OC-v2 `source_references` sc/ac refs, CC `field_selection` business_concept_ids, `derivations` input concept ids).
- **Invariant VI (evidence emitted):** CO acceptance/rejection emits evidence + progression rows; never inferred.

## Relationship to the legacy resolver

The `canonical_mapping`-based `CanonicalResolutionService` is retained only for any legacy contracts that still carry mapping rows (currently none). For CC-v2 it is not used. This ADR provides the runtime replacement that DEC-02f5a9 (which superseded `canonical_mapping` as a declaration surface) implied but did not build. Interim `canonical_mapping`-bridge authoring for arpi_slice is explicitly rejected as reintroducing a superseded mechanism (tech debt).
