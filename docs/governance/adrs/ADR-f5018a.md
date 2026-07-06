---
uid: DEC-f5018a
title: "Canonical Contract Split — universal form vs tenant-scoped mapping binding"
description: "Split canonical contract into universal form (platform-scoped CO shape) and tenant-scoped mapping binding (source-specific field resolution). Corrects D026."
status: implemented
subdomain: contracts-architecture
focus: canonical-split
date: 2026-03-08
project: bc-core
domain: database
refs:
  - type: decision
    label: "D026"
  - type: decision
    label: "D048"
authority: authoritative
migrated_from: legacy v2 archive
---


# Canonical Contract Split — universal form vs tenant-scoped mapping binding

## Context

Foundation Data Object Model (Component Ref 100): COs are domain-scoped, do not reference raw source systems. Patent: canonical objects are universal business vocabulary. D026's bundled body violates this by embedding source_dependencies and canonical_mapping (source-specific) inside the canonical contract (should be universal). Scenario planning (SES-6bb15f) confirmed: different tenants need different mappings to the same CO form.

## Decision

Corrects D026 (DEC-efb5bf). The canonical contract body is split into two distinct artifacts:

**Canonical Contract (platform-scoped, universal):**
- evaluation_tier (1=primary from SOs, 2=derived from COs)
- resolved_schema (JSON Schema defining CO output shape)
- business_key_fields[] (composite business identity)
- semantic_rules[] (validation invariants)

This defines "what does this CO look like" — the same regardless of tenant or source system.

**Canonical Mapping Binding (tenant-scoped):**
- canonical_contract_ref (which canonical contract this maps to)
- tenant_id (which tenant)
- source_dependencies[] (which admission contracts feed this, with roles)
- join_context[] (cross-table join keys — same source system only, per D048)
- canonical_mapping[] (per-field: canonical_field, source_field, source_ref, transform, mapping_type, priority)
- version (evolvable)
- status (active/inactive)

This defines "how do we produce this CO from this tenant's source data."

**Evaluation engine change:** Resolves canonical contract for the CO form, then resolves the tenant's mapping binding for the wiring. Both required to produce a CO.

**Rationale:** COs are "domain-scoped, referentially stable" and "do not reference raw source systems" (Data Object Model §100). Bundling source_dependencies and canonical_mapping inside the canonical contract violates this — it embeds source references in what should be a universal business concept. The split preserves CO universality while allowing tenant-specific source wiring.

**Seed impact:** Canonical contracts become universal (no mapping in body). Demo mapping bindings created for demo-selenite tenant only.

## Options Considered

N/A

## Consequences

N/A
