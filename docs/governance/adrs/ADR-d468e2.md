---
uid: DEC-d468e2
title: "Reference BCs deferred until Reference BC End-to-End DBCP"
description: "Defer all kind=reference BC authoring; SUBSTRATE_READY_BUT_MCF_UNSPECIFIED; gated on a single coupled BCF+MCF reference DBCP."
status: decided
date: 2026-06-06T07:48:14.625Z
project: bc-core
domain: metrics
subdomain: bcf-reference-concepts
focus: governance
---

# Reference BCs deferred until Reference BC End-to-End DBCP

## Context

No rationale recorded.

## Decision

Reference (kind=reference) business concepts are DEFERRED. No reference BC is authored until a single coupled DBCP — "BCF Reference Concepts + MCF Reference Binding Semantics" — exists and is decided.

STATUS CLASSIFICATION: SUBSTRATE_READY_BUT_MCF_UNSPECIFIED. The BCF substrate (concept_registry.business_concept kind / reference_role / target_entity_id columns; the kind/metadata-disjoint CHECK; the uq_business_concept_reference_identity partial-unique index; the recursive-CTE acyclic identity-DAG trigger) and the F3 SERVICE layer (RegistryAuthoringService.createBusinessConcept CreateReferenceConceptInput branch + assertReferenceConceptInvariants) can REPRESENT references. But (a) the B6 panel CANNOT author them — recommendation.validator.ts:88-90 hard-rejects kind!='value'; the run-DTO and RegistryCreateBusinessConceptCandidate carry no referenceRole/target_entity_id; and (b) MCF CANNOT consume them — metric_variable_binding.role_kind_code enum is ('input','output','constant') only; L-V1i at M12.5 and PE-MC-4 at M13 reject bindings whose representation_term_snapshot/data_type_snapshot are null (structurally true for every reference BC); PE-MC-2 does not traverse target_entity_id. The reference-property bind semantics (MCF Q23, requirements §19.8 — "does the MC operate on the reference target's entity, or on the reference itself as a join column?") are UNRESOLVED with no implementation DBCP.

POLICY (in force now):
1. No reference BC authoring in BCF enrichment waves.
2. No raw F3 / script reference writes.
3. No operator-direct reference workaround.
4. No B6 reference-authoring implementation until the decision note exists.
5. No MCF reference-binding code until Q23 is resolved.

NEXT REQUIRED ARTIFACT (gates ALL reference work): a single coupled DBCP/decision note titled "BCF Reference Concepts + MCF Reference Binding Semantics" that MUST decide:
(1) BCF meaning of kind=reference; (2) reference_role naming discipline; (3) identity_bearing vs descriptive usage; (4) the B6 authoring surface (Maker/Checker/Moderator reference templates + recommendation.validator extension + run-DTO referenceRole/targetEntityId/identityRole fields + context-builder reference grounding); (5) MCF role_kind_code / binding model (whether 'reference' is added as a role kind); (6) Q23 — target-entity-grain vs join-edge semantics; (7) PE-MC / M12.5 behavior for snapshot-less reference bindings (skip type/unit checks; perform target-entity grain reachability); (8) the first proof reference candidate (docs nominate CIA->Customer Invoice or Invoice Dispute->Customer Invoice); (9) explicit out-of-scope items.

INTERIM OPERATING POLICY: continue BCF value / entity / characteristic coverage waves only. Metrics that require a reference binding are tagged `reference_deferred` and parked — they do NOT block value-layer enrichment.</decision_text>
<parameter name="rationale_text">A read-only 5-area study (BCF substrate, BCF authoring path, MCF docs, MCF code, planning docs) found the substrate fully built but the governed authoring chain value-only and MCF consumption both unspecified (Q23 open, no DBCP) and unimplemented (no 'reference' role_kind; L-V1i/PE-MC-4 reject snapshot-less reference bindings; PE-MC-2 does not traverse target_entity_id). Authoring a reference BC now — only possible via raw F3 — would create an orphan no metric can consume, outside the governed chain, violating the "mint references on demand for a real consumer" discipline. BCF authoring and MCF consumption are coupled and must be decided together in one DBCP before any code or authoring. Aligns with the standing planning-doc rule "Do NOT introduce reference BCs without the Wave 3 architecture decision first."</rationale_text>
</invoke>

