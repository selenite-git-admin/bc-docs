---
uid: DEC-9361cd
title: "CC Field Mapping: 1-BF-to-Many-CFs + Filter + Canonical Uniqueness"
description: "CC Field Mapping: 1-BF-to-Many-CFs + Filter + Canonical Uniqueness"
status: implemented
date: 2026-04-10T05:46:17.921Z
project: platform
domain: contracts
migrated_from: legacy v2 archive
---

# CC Field Mapping: 1-BF-to-Many-CFs + Filter + Canonical Uniqueness

## Context

D301 introduced `cc_field_mapping` with `UNIQUE(canonical_contract_id, business_field_id)` — one BF maps to one CF per CC. During CC chain creation for AR metrics, this proved too restrictive: `receivable_hdr_amount` (one BF) needs to produce `accounts_receivable_balance`, `total_past_due_ar`, `open_item_count`, etc. — multiple CFs with different resolution rules and filter conditions.

## Decision

### 1. Drop UNIQUE on (canonical_contract_id, business_field_id)

One BF can map to many CFs within the same CC. Replace with regular index.

### 2. Keep UNIQUE on (canonical_contract_id, canonical_field_id)

One CF resolves from exactly ONE BF per CC. **Canonical Uniqueness Invariant** — no ambiguity in the reverse direction.

### 3. Add `filter_json` JSONB column

Enables conditional mappings (e.g., `sum WHERE due_date < today`). Evaluator applies filter before resolution rule.

### 4. Canonical Uniqueness Invariant (platform-wide)

- `canonical_field.field_name` is globally UNIQUE — one business concept, one CF name
- CFs are **standard-agnostic** — no source_standard tag on CFs
- Multiple BFs from different standards can map to the same CF through different CCs
- **Synonym check gate required** before CF creation

### 5. BF/BO Sourcing Hierarchy (3-tier)

| Tier | Source | Tag |
|------|--------|-----|
| 1 | OAGIS | `source_standard: 'oagis'` |
| 2 | Other international standards (ISO, GAAP, IFRS, XBRL) | `source_standard: 'gaap'` etc. |
| 3 | BC Standard (last resort, 5 quality gates) | `source_standard: 'bc_standard'` |

BFs/BOs from Tier 2/3 never pollute OAGIS-sourced BOs.

## Schema Changes

```sql
ALTER TABLE contract.cc_field_mapping
  DROP CONSTRAINT cc_field_mapping_canonical_contract_id_business_field_id_key;
CREATE INDEX idx_cc_field_mapping__cc_bf
  ON contract.cc_field_mapping(canonical_contract_id, business_field_id);
ALTER TABLE contract.cc_field_mapping ADD COLUMN filter_json jsonb;
```

## Consequences

- CC can express complex translations: one source field → multiple business concepts
- Canonical Evaluator must support per-mapping filters
- CF registry is the single canonical vocabulary — no fragmentation across standards
- Every metric variable → CF → BF chain is fully resolvable (no orphans)
