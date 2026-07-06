---
uid: DEC-36d78f
title: "Reader Observation Schema — selective observation with standard field naming"
description: "Observation schema is a first-class artifact on reader_flavor with observedFields, standardFields, and fieldMap"
status: implemented
subdomain: readers
focus: observation-schema
date: 2026-03-14
project: bc-admin
domain: database
refs:
  - type: decision
    label: "D055"
authority: authoritative
migrated_from: legacy v2 archive
---


# Reader Observation Schema — selective observation with standard field naming

## Context

## D069: Observation Schema & Contract Architecture (FINAL CLARIFICATION)

### Observation Schema
- **First-class artifact on the Reader Flavor** (not derived from contracts)
- Structure per Ref 091 §4.3: `{observedFields, standardFields, fieldMap}`
- `observedFields`: source field names as they appear in the source system
- `standardFields`: registered Standard Field names (validated against SF registry)
- `fieldMap`: source → standard field mapping
- Stored as `observation_schema` jsonb column on `reader_flavor` table

### Contract Architecture (post-D069)
- **Extraction Contract: RETIRED** — replaced by Observation Schema on Flavor
- **Contract types reduced from 7 to 6**: Source, Admission, Canonical Evaluation, Metric Evaluation, Action Evaluation, Observation (the schema itself)
- **Source chain**: Source → Admission → Canonical (no Extraction step)

### Contract Immutability Rule (USER DIRECTIVE)
- **Source Contract and Admission Contract are immutable** — they live with their parent source table/field
- They are **NOT versioned or created per Reader** — they describe the source schema/rules for fields at a source table
- They are **referenced in context of** the Observation Schema's field needs
- The Observation Schema declares WHICH fields the flavor observes; the contracts declare the RULES for those fields at the source

### Reader Detail Page (TSK-3304cd) Implications
- Show per-flavor: Observation Schema (field mapping table)
- Source Contract: referenced (not created per reader), shown in context of observed fields
- Admission Contract: referenced (not created per reader), shown in context of observed fields  
- SOs produced by this flavor
- Group with source entity/table

### Source Object Field Names
- SO fields use `standardFields` from Observation Schema as their field names
- Values preserved exactly as observed — no transformation
- Immutable after creation

**Supersedes:** D055 (output_fields removal from Extraction Contract)

## 1. Readers selectively observe

"Business-Aware" means the Reader knows WHAT to observe, not what it MEANS. The Reader declares which fields to extract per source entity via its Observation Schema. This is field projection, not transformation. Values are preserved exactly as the source gave them.

## 2. Reader Observation Schema — new first-class artifact

Per flavor, per source entity:
- **Projected fields**: which source fields to extract (source field names)
- **Output SO schema**: standard field names (source-agnostic)
- **Field map**: source name → standard name (e.g., BUKRS → company_code, BELNR → document_number)

The Observation Schema is the Reader's business awareness. It declares what to look at and how to name it consistently.

## 3. SO uses standard field names

The Reader always produces `company_code` regardless of whether it read SAP BUKRS, Oracle COMPANY_ID, or Tally CompanyCode. This makes Field Bindings (SO→CO) near-mechanical — same vocabulary, trivial mapping.

This is NOT transformation. The value of BUKRS is preserved exactly. Only the field name is standardized.

## 4. Extraction Contract retired

The Flavor already carries extraction config (connector, connection, sourceEntity, keyFields, sourceSpecific). A separate Extraction Contract is redundant. Extraction declaration merges into the Flavor + Observation Schema.

Contract types reduced from 7 to 6: Source, Admission, Canonical, Metric, Intervention, AI.

## 5. Source Contract scope narrowed

Source Contract declares the expected schema of the PROJECTED fields (what the Reader will observe from this source entity), not the full table schema. The full table/object schema lives in Source Catalog as reference data (Source Landscape).

## 6. Admission Contract unchanged in purpose

Admission Contract validates the projected fields as declared in the Source Contract. Its scope is the Reader's projection, not the full table. Admission still does acceptance only — no meaning resolution.

## 7. Foundation alignment

Foundation says "observe" and "preserve observed state." Selective observation is still observation. Preserved observed state with standard field names is still preserved observed state. No foundation principle, prohibition, or guarantee is violated. Correction is at Component Reference level (090, 091) and Contract Registry.

## Impact on existing artifacts

- Component Ref 090 (UinBAT Reader): Add selective observation, observation schema
- Component Ref 091 (Operational): Add observedFields to flavor shape, observation schema reference
- Contract Registry: Retire Extraction Contract type, narrow Source Contract description
- Foundation contract.md: Remove Extraction Contract from contract types list
- bc-core schema: Add observation_schema to reader_flavor table (future migration)
- bc-admin UI: Reader detail page to surface observation schema (future)

## Consequences

N/A
