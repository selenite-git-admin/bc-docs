---
uid: DEC-97bb94
title: "Canonical Object resolves N Source Objects — multi-source canonical evaluation"
description: "A single Canonical Object can resolve from multiple Source Objects. Canonical evaluation is multi-source by design."
status: implemented
subdomain: canonical-evaluation
focus: multi-source-resolution
date: 2026-03-01
project: platform
domain: database
refs:
  - type: decision
    label: "D021"
  - type: decision
    label: "D023"
authority: authoritative
migrated_from: legacy v2 archive
---


# Canonical Object resolves N Source Objects — multi-source canonical evaluation

## Context

Real-world enterprise data always spans multiple tables. SAP AP invoices require BKPF (header) + BSEG (line items). GL accounts require SKA1 + SKAT. No single source table contains all fields needed for a canonical business entity. Readers must not cross their boundary (one reader, one source entity), so the join must happen at canonical evaluation. This was already modeled in the CXOFacts Golden Data Contracts (gdp_source_mapping with source_dataset + source_key_context) and confirmed by the bc-portal dummy data (AP_4101 Vendor Invoice mapping fields from BKPF, BSEG, and BARECOUNT-derived).

## Decision

A Canonical Object is resolved from one or more Source Objects originating from different source entities/readers. Canonical evaluation handles the join — readers never cross their boundary.

**Pattern:** N SOs → Canonical Evaluation → 1 CO

Each reader stays within its boundary (one reader, one source entity, one SO type). Canonical evaluation is where business meaning is resolved — it joins/merges across SOs by business key context (join keys).

**Canonical contract body must declare:**
1. `source_dependencies[]` — which source/admission contracts feed this canonical evaluation, with roles (primary, detail, reference)
2. `join_context` — the keys used to correlate records across source datasets (e.g., BUKRS + BELNR + GJAHR for SAP)
3. `canonical_mapping[]` — per-field mapping with source_dataset, source_field, transform, priority, and mapping_type (mapped | derived)
4. Derived fields — canonical fields computed by the platform (e.g., DUE_DATE from baseline_date + payment_terms), not passed through from any source

**Evidence from existing design:**
- AP Vendor Invoice CO maps from BKPF (header) + BSEG (line items) + platform-derived fields
- GL Account CO maps from SKA1 (account master) + SKAT (account texts)
- CXOFacts `gdp_source_mapping` table had: attribute_code, source_system, source_dataset, source_field, source_key_context (JSON), transform_expression, priority, is_primary
- CXOFacts dummy data confirms per-field source attribution with priority and mapping_status (Mapped | Derived)

**FOUNDATION-CONTRADICTION-003:** The execution model's linear `SO → Canonical Evaluation → CO` implies 1:1. In practice, canonical evaluation resolves N source objects from multiple source entities into one canonical business object. Foundation v2 must clarify this as N:1.

**Relationship to D021:** Same N:1 pattern, one layer down. D021 established Metric references N Canonical Objects. D023 establishes Canonical Object references N Source Objects. The feed-forward chain is: N SOs → 1 CO → N COs → 1 Metric Snapshot.

## Options Considered

N/A

## Consequences

N/A
