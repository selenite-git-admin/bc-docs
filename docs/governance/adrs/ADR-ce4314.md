---
uid: DEC-ce4314
title: "Onboarding Runway Lanes — source-classified workstreams for onboarding a source system (BCF/MCF vocabulary)"
description: "Ten source-classified onboarding-runway lanes (corrected BCF/MCF vocabulary) + a thread-anchoring model, so onboarding work has a durable, discoverable, extendable home."
status: decided
date: 2026-08-21T13:20:23.207Z
project: platform
domain: sources
subdomain: onboarding/runway-lanes
focus: governance
---

# Onboarding Runway Lanes — source-classified workstreams for onboarding a source system (BCF/MCF vocabulary)

## Context

Loose, memory-stitched scoping repeatedly caused large time loss and drift across the tenant/execution boundary (e.g. applying a tenant substrate + seeding while the actual anchor was source-side runway authoring). A grounded, source-classified lane structure with an explicit anchoring model and a demand-pull operating rule gives every ongoing thread a durable home and lets future sessions find, latch onto, understand, and extend the onboarding runway from a citable authority instead of reconstructing it from memory. The vocabulary was re-grounded (BF/BO/CF retired -> BCF/MCF) and verified against the substrate because the onboarding docs are stale on this point.

## Decision

Organize onboarding a source system (first: Odoo) as TEN classified LANES — each an onboarding artifact family, tagged source-dependent (SD) or source-agnostic (SA), in build order — plus an anchoring model that maps ongoing work threads onto lanes. This is an ORGANIZING decision; it does NOT redefine the artifact families (authority: bc-docs onboarding-overview.md) or the vocabulary (authority: DEC-02f5a9, DEC-65dc86, DEC-5a9dee, business-concept-registry.md).

LOCKED LANES (build order):
L1 Source Catalog authoring (Source Registration; system->tables->fields) — SD
L2 SC + AC authoring (source structure + admission on source fields) — SD
L3 BCF Enrichment (the vocabulary registry: Entity x Characteristic x Business-Concept) — SA
L4 BCF<->Source-Catalog Map = OC authoring (bind source field -> BCF Business Concept) — SD
L5 CC authoring (select BCF concepts, grain = Entity, CO shape) — SD
L6 MCF Metric Contract authoring (bind formula variables -> BCF concepts by id; grain = Entity) — SA
L7 Reader creation (UniBAT runtime executing the OC against the source) — SD
L8 Metric Registration / Directory (seed -> directory member -> realized MCF authority) — SA
L9 MC Chain Integrity (end-to-end chain checks) — SA
L10 Tenant Onboarding (one tenant onto the operational chain) — tenant-scope

CLASSIFICATION RULE: source-dependent if the artifact is specific to the source system (catalog, SC/AC, OC map, CC, Reader); source-agnostic if universal (BCF vocabulary, MCF metrics, directory, chain integrity).

VOCABULARY (VERIFIED 2026-08-21 against substrate + primary ADRs): Business Field / Business Object / Canonical Field are RETIRED and physically dropped (D417 quarantine -> D418 retirement; platform-DB tables business_field / business_object / canonical_field / cc_field_mapping all ABSENT — substrate-confirmed). CF collapsed into one Business Concept (DEC-02f5a9 s2: 'Business Field and Canonical Field collapse into one Business Concept'); the BF->Canonical-Mapping->CF identity hop is eliminated. The single vocabulary is BCF: a Business Concept = Entity x Characteristic x representation-term (kind value|reference; identity_role identity_bearing|descriptive; reference_role/target_entity for references), identity = (entity, characteristic). Computed meaning is MCF (mcf.metric_contract, 432), binding to BCF concepts by id with grain = an Entity; the legacy contract.metric_contract is superseded/0. Active contract families: Source -> Admission -> Observation -> Canonical -> MCF Metric -> Intervention. Family taxonomy (DEC-5a9dee): MCF, BCF, Metric Directory are the authority-creating families. NOTE: bc-docs onboarding + operating-model chapters still teach BF/BO/CF (stale doc-debt, TSK-f13259); ground vocabulary on BCF/MCF, not those chapters.

VOCABULARY FLOW: Source -> SC/AC (source fields) -> OC binds source field -> BCF concept -> CC selects BCF concepts (grain = Entity) -> MCF MC binds variables -> Metric Snapshot.

ANCHORING MODEL (ongoing threads -> lanes; point-in-time snapshot barecount-devhub@b4c93d5 artifacts/thread-inventory/):
- The onboarding runway = L1-L7 (catalog -> reader). The metric side = L6/L8/L9.
- NOT lanes (they are what lanes depend on / run on): the source DATA (SDG/demo-world realism) is upstream of L1; the runtime EXECUTION engines (Reader/Runner/Evaluators) run the lanes' artifacts; numeric-representation config and documentation are cross-cutting.
- Thread map: A(SDG data)=source upstream; B(cert/directory)=L6/L8/L9; C(front door)=L4/L5/L7+connection; D(A0-D574 legal-entity)=L5 canonical-resolution feature; E(runtime ecosystem)=L7+runtime engines; F(D575)=L10/tenant infra; G(E6-B PR#704)=L6/runtime metric-eval; H(D508 join)=L5; I(numeric flip)=runtime config; J(v3 book)/K(TSK-f13259 vocab cleanup)=docs.

OPERATING RULE (prevents the drift this decision was created to stop): work is DEMAND-PULLED — a metric (L8/L6) pulls the exact chains (L4/L5) that pull the concepts (L3); the source data + runtime engines gate compute. Never author a lane artifact without a metric pulling it; never cross the tenant boundary except at L10 or the gated compute step.

HOW TO EXTEND: a new source system re-runs the source-dependent lanes (L1/L2/L4/L5/L7) against its catalog while reusing the source-agnostic lanes (L3/L6/L8/L9). A new metric family adds L6 authoring pulling new L3 concepts + L4/L5 chains as needed.
