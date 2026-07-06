---
uid: DEC-efb5bf
title: "Canonical-v1 meta-schema body structure finalized"
description: "Meta-schema body: evaluation_tier, source_dependencies, join_context, canonical_mapping (per-field), business_key_fields, resolved_schema. Supports N SOs to 1 CO."
status: implemented
subdomain: canonical-meta-schema
focus: contract-body-shape-v1
date: 2026-03-01
project: bc-core
domain: database
refs:
  - type: decision
    label: "D024"
  - type: decision
    label: "D025"
  - type: decision
    label: "D023"
authority: authoritative
migrated_from: legacy v2 archive
---


# Canonical-v1 meta-schema body structure finalized

## Context

Evidence from bc-portal dummy data (AP Vendor Invoice: 17 fields from 4 sources; AP Aging: 100% derived CO→CO) and CXOFacts documentation (GDP GL Account: SKA1 + SKAT) confirmed the need for multi-source resolution, join context, field-level source attribution, and derived vs mapped distinction. The resolved_schema per contract allows each canonical entity to have its own unique output shape while the meta-schema validates the contract template structure uniformly.

## Decision

The canonical-v1 meta-schema body contains: evaluation_tier (1=primary from SOs, 2=derived from COs per D024), source_dependencies[] (references admission contracts for Tier 1 or canonical contracts for Tier 2, with role: primary/enrichment/lookup/settlement), join_context[] (cross-source join keys with left/right/join_keys/join_type), canonical_mapping[] (per-field with canonical_field, source_field, source_ref, transform, mapping_type: mapped|derived, priority), business_key_fields[], semantic_rules[] (typed validation rules), temporal_gate (shared $def per D025 — required for Tier 2, optional for Tier 1), resolved_schema (JSON Schema defining the CO output shape, specific to each canonical entity). This structure supports D023 (N SOs → 1 CO) and D024 (Tier 1/Tier 2 internal layering) while keeping the meta-schema as a template validator, not a data shape enforcer.

## Options Considered

N/A

## Consequences

N/A
