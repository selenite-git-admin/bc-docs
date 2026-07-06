---
uid: DEC-a0e92e
title: "Contract Requirements Correction + Master Shape as Unified Artifact"
description: "Requirements corrections for all 6 families (SC one-per-table, CC all-fixed, OC binding-only tenant, MC execution fields, IC conditional triggers) + master JSON as unified validation+governance artifact"
status: implemented
subdomain: contract-spec
focus: requirements-reconciliation
date: 2026-04-02T04:01:31.639Z
project: bc-docs
domain: foundation
migrated_from: legacy v2 archive
---

# Contract Requirements Correction + Master Shape as Unified Artifact

## Context

The requirements document had drifted from decided architecture (D164/D232/D233) at critical points: SC scope, CC tenant model, OC governance. Implementation had also diverged (metric normalization across 8 tables instead of JSON-first). A single reconciliation pass — requirements first, then implementation — prevents compounding errors. The master JSON as unified artifact eliminates the duplication between JSON Schema validators and governance metadata.

## What Changed

### Requirements Corrections (contract-requirements-v1.md)

Six corrections validated against D164 (platform-only), D232 (JSON-first), D233 (three-level model):

1. **SC: One contract per source table** — not per source system version. Binding triplet: (source_system_version_id, module_code, table_code). Removed tables[] array. Admission outcomes moved to AC.
2. **AC: Inherits table scope from SC** — removed redundant table_code. Added admission_bands (moved from SC). Confirmed no maps_to on fields.
3. **OC: All body fields fixed** — tenant Z-field extensions and ignored_fields go in contract_binding (extensions_json / override_json), not on the OC body. Aligns with D233 "OC: Fixed only."
4. **CC: Platform-only and entirely fixed** — was wrongly described as tenant-scoped with overridable grain/field_selection. Per D164+D233, all CC keys are fixed. Added evaluation_tier (1/2). Renamed output_schema → resolved_schema.
5. **MC: Added 9 execution fields** — kpi_id, catalog_code, category, tier, pack_code, module_code, sql_logic, value_type, direction. Three formula representations (human + SQL + variables). Thresholds as array with ops and tenant_overridable flag. Removed CR-MC-006 (runtime behavior, not contract structure).
6. **IC: trigger_conditions conditional** — only present when activation_mode=auto. Existing intervention-v1.md spec describes wrong model (alerting vs governed template) — must be rewritten.

### Master Shape = Unified Artifact

The master JSON per family is a single artifact serving two roles:
- **JSON Schema** for structural validation (AJV validates contract_json bodies)
- **Governance annotations** via `x-governance` custom keywords (fixed/overridable/extensible per field)

This eliminates the need for a separate "meta-contract" concept. The master JSON IS the meta-schema with governance. Stored in `contract.contract_meta_schema`. Source of truth files in legacy v2 archive foundation.

### Reconciliation Principle

Each master JSON takes the best of three sources:
1. Requirements doc (corrected) — business intent, governance tags
2. Implementation (bc-core seed data, 46 CC + 54 MC) — proven runtime fields
3. Legacy specs (bc-docs v1, patent) — gap-filling

Where they conflict: D164/D232/D233 override all. Requirements win on structure. Implementation wins on proven field names/types. Legacy fills gaps.

### Lifecycle

- Master shapes are locked. Changes require ADR + governance review.
- New instances must use the latest active master version.
- Old instances are NOT retroactively changed — they record their meta_version.
- Each contract version stores which meta_version it was validated against.
- Backward-incompatible changes = new meta_version (v1 → v2).
