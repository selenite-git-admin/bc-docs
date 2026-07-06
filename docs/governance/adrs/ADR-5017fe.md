---
uid: DEC-5017fe
title: "Standard Field Registry — ISO 11179 MDR for observation vocabulary"
description: "Platform-level metadata registry governing every standard field name used in Reader Observation Schemas and Source Object emission, aligned with ISO 11179/8000/CEFACT/XBRL"
status: superseded
superseded_by: DEC-a17d0f
subdomain: naming-standards
focus: standard-field-registry-mdr
date: 2026-03-14
project: bc-core
domain: readers
refs:
  - type: decision
    uid: DEC-69f09e
    label: "D148: ISO 11179 Technical Naming Standard"
  - type: decision
    uid: DEC-36d78f
    label: "D138: Reader Observation Schema"
  - type: decision
    uid: DEC-ddbce8
    label: "D135: Unified Business Domain Taxonomy"
  - type: document
    path: "component-references/source-catalog.md"
    label: "Source Catalog component reference"
authority: authoritative
migrated_from: legacy v2 archive
---

# Standard Field Registry — ISO 11179 MDR

## Context

Readers observe source data and emit Source Objects. Without a governed vocabulary, each reader team would invent field names independently — one reader emits `company_code`, another `comp_code`, another `BUKRS`. This makes SO→CO field binding (the next evaluation step) a manual, error-prone mapping exercise.

The Standard Field Registry ensures every observation uses the same vocabulary. If SAP BUKRS and Oracle COMPANY_ID both mean "company code," both readers emit `company_code` — the registered standard name.

## Decision

BareCount introduces a **Standard Field Registry** — a platform-level metadata registry governing the vocabulary of observation.

### Standards Alignment

- **ISO/IEC 11179** (Parts 1, 3, 5) — Metadata Registries. Naming convention, registry metamodel.
- **ISO 8000** (Parts 100, 110) — Data Quality. Field names as characteristics.
- **UN/CEFACT CCTS** — Core Components Technical Specification.
- **XBRL Taxonomy model** — Domain validation, tenant extension model.

### Registry Structure (per field)

- **name**: `snake_case` standard name (e.g., `company_code`, `document_number`)
- **definition**: human-readable semantic definition
- **domain**: business domain (finance, sales, operations, etc.)
- **object_class / property / representation_term**: ISO 11179-5 grammar
- **data_type**: string, number, date, boolean
- **status**: draft → registered → deprecated → retired
- **source_aliases**: known source representations (SAP: BUKRS, Oracle: COMP_CODE, Tally: company_id)

### Two-Tier Model (D054 alignment)

- **Platform fields**: ~50 per domain, ISO 11179 governed, owned by platform
- **Tenant extension fields**: prefixed `z_`, tenant-scoped, XBRL extension model

### Invariants

1. No Observation Schema may reference an unregistered standard field name
2. Standard field names are immutable once registered (can be deprecated, never renamed)
3. Platform fields are universal — same name, same meaning across all tenants
4. Source aliases are informational — aid authoring, don't govern extraction

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **ISO 11179 standard field registry (chosen)** | Governed vocabulary, near-mechanical SO→CO binding, audit guarantee | Requires upfront registry population |
| Source-native field names | Zero mapping effort | Every SO→CO binding is a custom mapping |
| Auto-generated canonical names | Low effort | No semantic meaning, unreadable |

## Consequences

1. **SO field names ARE standard field names** — `company_code` regardless of source
2. **SO→CO binding becomes near-mechanical** — same vocabulary on both sides
3. **Differentiator**: BareCount governs the vocabulary of observation — every field registered, every observation traceable to a registered semantic element
4. **The Standard Field is the single identity anchor** across the entire observation chain
