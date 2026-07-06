---
uid: DEC-a6258b
title: "Canonical Contract field-level semantic identity (implements DEC-02f5a9 schema-key)"
description: "A Canonical Contract field carries one primary governed business_concept.concept_id + a frozen semantic snapshot; MC variables and CC fields resolve by shared concept_id. Grammar/resolver decision only — implementation deferred to a DBCP."
status: decided
date: 2026-06-07T15:14:31.442Z
project: bc-core
domain: contracts
subdomain: contracts/canonical
focus: schema
---

# Canonical Contract field-level semantic identity (implements DEC-02f5a9 schema-key)

## Context

DEC-02f5a9 (Business Concept Registry) already locks the direction — "Contracts reference Business Concepts by identity"; the Canonical Contract "binds Business Concepts directly" — and explicitly defers one item: "the schema-level key naming is settled at the greenfield cutover." Audit finding X2 confirmed the deferral is unimplemented: a Canonical Contract field today is name-only (field_selection is a string array), carrying no business-semantic identity. The proven gap (live bc_platform_dev, 2026-06-07): Metric Contract variable binding → BCF Business Concept ✅; Canonical Contract field → BCF Business Concept ❌ — and nothing joins a business_concept_id to a (canonical_contract, field). The Metric Contract knows what each variable means; the Canonical Contract records only column names; the link is absent. Anchoring meaning at the canonical boundary (Invariant I) via concept_id — the same key the Metric side already uses — closes the gap with the smallest, Foundation-correct change and makes the metric chain resolvable. concept_id is chosen over (entity_id, characteristic_id) because it is the single stable anchor a Metric Contract variable binding already references (trivial concept_id = concept_id match), and over name pairs because terms are reusable after supersession.

## Decision

Implement the deferred DEC-02f5a9 schema-key decision at the Canonical Contract field level. THIS ADR's scope is the grammar + resolver decision only — no schema/code/DB change is authorized here; implementation is deferred to a later DBCP.

1. Implements (does not supersede) the DEC-02f5a9 deferred decision: "the schema-level key naming is settled at the greenfield cutover."
2. A Canonical Contract field carries exactly ONE primary governed business_concept.concept_id (decision A1) — the concept-anchor uuid, the same key a Metric Contract variable binding already uses (mcf.metric_variable_binding.bound_business_concept_id).
3. The field stores the concept_id PLUS a frozen semantic snapshot (representation_term / unit / data_type) for drift defense (decision E2). concept_id is identity; the snapshot is defense, never identity.
4. The concept→field binding lives in the Canonical Contract field declaration (decision B1) — not in a side mapping table, not in the Metric Contract or MCF.
5. Runtime resolution matches a Metric Contract variable to a Canonical Contract field by shared business_concept.concept_id, deterministically under one active CC per grain entity with each concept appearing at most once (decision C1).
6. MCF authors/governs Metric Contracts; it does NOT invent or consume runtime mappings. The runtime engine performs the concept_id match. BCF defines meaning; the Metric Contract records variable→concept; the Canonical Contract records field→concept.
7. Archived legacy Canonical Contracts are NOT migrated (decision D1) — they are immutable preserved state; new CCs are authored greenfield with identity (0 active CCs exist today).
8. Observation-level concept binding (source field → business_concept) is DEFERRED (decision F1) — sequenced after this CC change, not folded into this ADR.
9. DDL, meta-schema (canonical-v1) changes, and the resolver implementation are DEFERRED to a later DBCP (Step 1's decide→DBCP→apply rhythm). No schema/code/DB change is authorized by this ADR.
10. ARPI proof slice: one greenfield Customer Invoice Canonical Contract (entity e3963e45) declaring the three ARPI concepts (numerator_source a42d3fc0, denominator_key 095afe86, temporal_anchor d05f24b3) + the resolver — before any generalization beyond one entity.

Consequences: closes Foundation gap X2 (Invariant I — canonical meaning anchored at the canonical boundary); makes MCF-authored Metric Contracts resolvable to runtime evaluation, unblocking the ARPI synthesis proof's UNRESOLVED@C bindings and thus D429 Step 5 (resume materialization) for ARPI; satisfies the cross-system portability test (a second source system onboards via its own OC→concept + CC→concept with no Metric Contract edit). Foundation repair-location B (contract semantics) + read-only C (resolver); no lower-layer compensation.

Grounding: docs/implementation/canonical-field-semantic-identity-study-2026-06-07.md. Sequence: D429 Step 1 (contract-version immutability) applied (CHG-7fb0db); this is Step 2 (decided); Steps 3 (guard legacy metric authoring door), 4 (fix fail-open activation gates), 5 (resume materialization) follow. MCF materialization remains paused.
