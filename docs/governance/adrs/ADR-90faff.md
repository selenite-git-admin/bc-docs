---
uid: DEC-90faff
title: "Canonical-Driven Reader Creation Flow — Top-Down Assembly of the BareCount Machine"
description: "Readers are assembled top-down starting from canonical objects, not bottom-up from sources. CO drives what gets read."
status: implemented
subdomain: reader-architecture
focus: top-down-assembly
date: 2026-03-24
project: bc-core
domain: database
refs:
  - type: decision
    label: "D069"
authority: authoritative
migrated_from: legacy v2 archive
---


# Canonical-Driven Reader Creation Flow — Top-Down Assembly of the BareCount Machine

## Context

Foundation spec (LOCKED) is explicit:
1. Source Contract = "expected schema of projected fields, NOT full source table schema" (contract.md line 28)
2. Observation Schema = Reader's declaration of what to observe and what to produce (D069)
3. "Readers selectively observe — field projection IS the Reader's business awareness" (UinBAT Reader §3)
4. "Multiple Admitted Records may be evaluated together when the business object spans multiple source structures" (canonical-object.md line 14)
5. Reader identity is "business-object-centric, not source-system-centric" (UinBAT Operational §2)

The canonical-driven flow is the only design consistent with ALL of these constraints simultaneously.

## The Problem

Current implementation creates Source Contracts as full table dumps (all fields from the source object). This violates the Foundation spec which states:

> "Source Contract — declares the expected schema of the **projected fields** that the Reader will observe from this source entity, **not the full source table schema**."

The 28,918 contracts seeded in the last session (14,459 source + 14,459 admission) are architecturally incorrect — they contain all fields instead of business-scoped projections.

## The Design: Canonical-Driven (Top-Down) Assembly

Reader creation is driven by **what business meaning the platform needs** (Canonical Object), not by what the source system has. The flow works backwards from meaning to data.

### The 8-Step Flow

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Select Business Object (WHAT we want to know)      │
│  ─────────────────────────────────────────────────────────── │
│  User picks a Business Object from the Business Catalog      │
│  e.g., "GL Journal Entry" (18 business fields)               │
│  This defines the canonical target — the meaning endpoint.   │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Ensure Canonical Contract                           │
│  ─────────────────────────────────────────────────────────── │
│  Canonical contract declares the universal CO form.          │
│  References BO via object_id FK.                             │
│  Adds: business_key_fields, semantic_rules.                  │
│  Source-agnostic — same for all tenants (Pattern C).         │
│  If exists → reuse. If not → create (auto-populate from BO).│
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Select Source (WHERE to get the data)               │
│  ─────────────────────────────────────────────────────────── │
│  User drills into Source Catalog:                            │
│  Provider → System → Version → Module → Source Object        │
│  e.g., SAP → S/4HANA → S4H2023 → FI → BKPF                │
│  Source Object has N fields (e.g., BKPF has 86 fields).     │
│  We need only a SUBSET — the business-relevant projection.   │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: AI-Assisted Field Mapping (THE MAGIC)               │
│  ─────────────────────────────────────────────────────────── │
│  Given:                                                      │
│    Target = BO fields (company_code, document_number, etc.)  │
│    Source = Source Object fields (BUKRS, BELNR, GJAHR, etc.) │
│  AI suggests: BUKRS → company_code, BELNR → document_number │
│                                                              │
│  This produces the OBSERVATION SCHEMA:                       │
│    projected_fields: [BUKRS, BELNR, GJAHR, BUDAT, ...]     │
│    standard_fields:  [company_code, doc_number, fy, ...]    │
│    field_map: { BUKRS: company_code, BELNR: doc_number }    │
│                                                              │
│  User reviews, adjusts, confirms.                            │
│  NOT all 86 source fields — only the ~12 that map to BO.    │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Create Source Contract (Business-Scoped Projection) │
│  ─────────────────────────────────────────────────────────── │
│  Source Contract = expected schema of the PROJECTED fields.   │
│  Contains only the ~12 fields from the Observation Schema,   │
│  NOT all 86 fields from BKPF.                               │
│  Declares: field names, types, drift baseline.               │
│  Binds to: source_version_id, source_object_id.             │
│  Scope: per source entity per Reader flavor (D069).          │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: Create Observation Contract (Admission Rules)       │
│  ─────────────────────────────────────────────────────────── │
│  Observation contract carries the field map:                 │
│    source_field_name → business_field_id                     │
│  Plus admission rules:                                       │
│    required fields, type constraints, identity semantics.    │
│  Links to source_contract_id.                                │
│  This is the Reader-scoped admission gate.                   │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: Create Reader + Flavor                              │
│  ─────────────────────────────────────────────────────────── │
│  Reader named after BO: gl_journal_reader (not sap_reader).  │
│  Flavor for this source: sap_s4_bkpf                        │
│  Flavor carries:                                             │
│    - observation_contract_id (from Step 6)                   │
│    - source_version_id (from Step 3)                         │
│    - connector_id (from connector catalog)                   │
│    - Observation Schema in config_json                       │
│    - Extraction config (sourceEntity, keyFields, batchSize)  │
│  Reader Binding: reader → source_contract + entity.          │
│  Schedule, retry, backfill on the Reader level.              │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 8: Create Canonical Mapping (Tenant Wiring)            │
│  ─────────────────────────────────────────────────────────── │
│  Canonical Mapping = how THIS tenant's source data resolves  │
│  to the universal CO form.                                   │
│  Binds: canonical_contract → observation_contract(s)         │
│  Pattern A: platform master is template, tenant instantiates.│
│  Multiple observation contracts can feed one canonical       │
│  contract (multi-source CO).                                 │
│  The mapping_json declares the resolution rules.             │
└─────────────────────────────────────────────────────────────┘
```

### Why Canonical-Driven (Not Source-Driven)

**Source-driven (wrong):** Start from source table → create contract with all fields → hope someone maps them to business meaning later. Produces: full table dumps, no business purpose, 28,918 contracts with no value.

**Canonical-driven (correct):** Start from business meaning → identify which source fields serve that meaning → create contracts for only those fields. Produces: focused projections, clear business purpose, every field has a reason to exist.

The Foundation spec is explicit: *"the Reader selectively observes — field projection IS the Reader's business awareness"* (D069). The Reader knows what to look for because the canonical target tells it what matters.

### Multi-Source Canonical Objects

A single Business Object (e.g., GL Journal Entry) may need data from multiple source objects:
- SAP: BKPF (header) + BSEG (line items)
- Oracle: GL_JE_HEADERS + GL_JE_LINES

Each source object gets its own Source Contract + Observation Contract. The Canonical Mapping declares how multiple observation contracts feed into one canonical evaluation. The Foundation spec explicitly supports this: *"Multiple Admitted Records may be evaluated together when the business object spans multiple source structures."*

### AI Field Mapping Service

The AI mapping in Step 4 is the differentiator. Given:
- Business field: `company_code` (type: string, role: identifier, standard: ISO 11179)
- Source fields: `BUKRS` (varchar, SAP company code), `COMP_CODE` (varchar), `ORG_CODE` (varchar)

The AI considers: field name similarity, data type compatibility, semantic role, source system domain knowledge (SAP field dictionary), and prior successful mappings. It suggests confidence-scored matches that the user reviews.

### Observation Schema Placement

The Observation Schema (D069) lives in TWO places:
1. **Reader Flavor config_json** — the runtime artifact. The executor reads this to know what to project and how to name it.
2. **Source Contract contract_json** — the declaration artifact. Declares the expected schema of projected fields for drift detection and governance.

These must be consistent. The creation flow generates both from the same field mapping.

### Existing Contracts: Rework Strategy

The 28,918 existing contracts (full table dumps) need rework:
1. Do NOT delete — they represent real source catalog structure
2. Reclassify: these are "source catalog reference" contracts, not business-scoped projections
3. When a Reader is created through the canonical-driven flow, a NEW source contract is created with the correct business-scoped projection
4. The old contracts remain as reference data showing the full source schema

## Contract Chain Summary

```
Canonical Contract (universal CO form, source-agnostic)
  ← Canonical Mapping (tenant-specific wiring)
    ← Observation Contract (field map + admission rules)
      ← Source Contract (projected field schema)
        ← Source Object in Source Catalog (full reference)
          ← Reader Flavor (runtime extraction)
            ← Reader (domain-specific observer)
```

Direction: Canonical DRIVES everything backwards. You don't start a Reader until you know what canonical meaning you're after.

## Consequences

N/A
