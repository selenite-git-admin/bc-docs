---
uid: DEC-4a17e0
title: "Observation Contract field-level semantic identity (sibling to DEC-a6258b; old Business Field role)"
description: "Observation Contract field-map entries carry business_concept_id (semantic authority; business_field_code demoted to label) + a frozen semantic snapshot; an author-time O↔C consistency check requires a Canonical Contract field and its source Observation Contract field to share the same concept_id. Sibling to DEC-a6258b/D430 (not amending it). Grammar/check decision only — implementation deferred to a DBCP."
status: decided
date: 2026-06-07T16:30:16.505Z
project: bc-core
domain: contracts
subdomain: contracts/observation
focus: schema
---

# Observation Contract field-level semantic identity (sibling to DEC-a6258b; old Business Field role)

## Context

DEC-d72560 split field vocabulary into a source-side Business Field (Observation Contract) and a canonical-side Canonical Field (Canonical Contract), joined by the Canonical Mapping. DEC-02f5a9 collapsed both into one Business Concept and eliminated the Canonical Mapping, so each boundary must declare which concept its field carries, with runtime joining by identity equality. DEC-a6258b/D430 implemented the Canonical declaration; this ADR implements the Observation declaration — the old Business Field role. Proven gap (live bc_platform_dev, 2026-06-07): an OC field-map entry is {transform, source_field, source_table, business_field_code}, where business_field_code is a free string with zero concept reference across all 95 active OC versions; no code or table links it to concept_registry. Choosing business_concept_id (over the (entity_id, characteristic_id) pair or name strings) matches the key D430 and the Metric variable binding already use, making the cross-boundary join trivial and stable across supersession. The author-time O↔C consistency check is the decisive addition: it turns a canonical field's concept claim from asserted into provable-from-source, which is what makes the ARPI slice a genuine O→C→M proof rather than canonical-side-only.

## Decision

File a SIBLING ADR to DEC-a6258b/D430 (canonical-side) for the Observation-side of field semantic identity — the old Business Field role (DEC-d72560) after DEC-02f5a9 collapsed Business Field + Canonical Field into one Business Concept. This ADR does NOT amend or combine with DEC-a6258b. Scope = grammar + consistency-check decision only; no schema/code/DB change is authorized here; implementation is deferred to a later DBCP.

1. Observation Contract field-map entries carry business_concept_id (O-A1) — the concept anchor uuid, identity-equal to the Canonical Contract field (DEC-a6258b) and the Metric Contract variable binding, so the cross-boundary join is concept_id = concept_id.
2. business_field_code is kept only as a label / backward-compat display field if needed — NOT semantic authority. Identity is business_concept_id.
3. The entry stores business_concept_id PLUS a frozen semantic snapshot (representation_term / unit / data_type) for drift defense (O-E). The concept_id is identity; the snapshot is defense.
4. Author-time O↔C consistency check is REQUIRED (O-C1): if a Canonical Contract field is sourced from an Observation Contract field, their business_concept_id values MUST match — enforced at authoring in the canonical onboarding service (SERVICES-ONLY). This is what makes a canonical field's concept claim provable from source rather than merely asserted.
5. The binding lives in the OC field-map entry (O-B) — the Observation Contract declares it; symmetric with DEC-a6258b's B1.
6. Legacy/archived Observation Contracts are NOT migrated (O-D) — preserved immutable state; new OCs authored greenfield with identity. (95 free-string active versions remain; the 0-active-headers/95-active-versions parent/version desync is a separate governance follow-up.)
7. Implementation — the observation-v1 meta-schema change, the author-time O↔C check, and greenfield OC authoring — is DEFERRED to a later DBCP (O-F: sequenced after DEC-a6258b's CC change). No schema/code/DB change authorized here.
8. ARPI OC slice: NETWR → a42d3fc0 (amount), VBELN → 095afe86 (identifier), FKDAT → d05f24b3 (date) on the Customer Invoice OC (entity e3963e45) — the SAME three BCF concepts used by the DEC-a6258b CC slice. Paired with the CC slice, this is the first full O→C→M concept-identity proof for ARPI.

Consequences: completes the admission-side half of field semantic identity. With DEC-a6258b (canonical) and the already-correct Metric Contract binding, concept identity is shared across all three semantic boundaries (Observation ∧ Canonical ∧ Metric by concept_id) — full O→C→M. The old BF→CF Canonical Mapping stays eliminated (DEC-02f5a9); consistency is identity equality, checked at authoring (item 4), not a mapping. Foundation repair-location B (Observation contract semantics) + read-only governance at C (the O↔C check); Invariants I (meaning anchored at the admission boundary) and IV (explicit references — concept identity replaces the free string).

Grounding: docs/implementation/observation-field-semantic-identity-study-2026-06-07.md. Sequence: D429 Step 1 (immutability) applied; Step 2 canonical (DEC-a6258b/D430) decided; this Observation-side ADR decided (sibling); Steps 3 (guard legacy metric door), 4 (fix fail-open gates), 5 (resume materialization) follow. MCF materialization remains paused.
