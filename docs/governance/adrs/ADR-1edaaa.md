---
uid: DEC-1edaaa
title: "One Observation Contract Per System Per Reader + Source Entity Provenance on Field Map"
description: "One flavor = one system (not one table). observation_field_map carries source_entity column to track which table owns each field."
status: implemented
subdomain: contract-chain
focus: one-OC-per-system-source-entity
date: 2026-03-24
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# One Observation Contract Per System Per Reader + Source Entity Provenance on Field Map

## Context

One flavor per table leaks source implementation details to the Reader level. The Reader is business-object-centric — it doesn't care that SAP stores AR data in BSID+BKPF. Same field name across tables in the same system means the same thing (no conflict). The source_entity column captures which table is authoritative (original vs copy/reference).

## Design

One flavor = one system (not one table). One observation contract = complete business-need field mapping for that system. Multiple source entities are extraction config detail inside the flavor.

The observation_field_map now carries `source_entity` — the authoritative source entity for each field. This captures system knowledge: which table OWNS the field vs which tables COPY it.

Example: SAP AR Invoice Reader, SAP flavor:
```
BUKRS → company_code    | source_entity: BKPF (original — header owns company code)
BELNR → document_number | source_entity: BKPF (original)
DMBTR → amount_local    | source_entity: BSEG (original — line items own amounts)
HKONT → gl_account      | source_entity: BSEG (original)
```

No PK change, no junction table, no conflicts. Flat field map with source_entity annotation.

## DB Change

```sql
ALTER TABLE contract.observation_field_map ADD COLUMN source_entity text;
```

## Impact

- Flavor extraction config: array of source entities (JSON shape, no DDL)
- Lineage: provenance of each SO field traceable to exact source entity
- AI mapper: can suggest source_entity based on key/FK analysis from source catalog

## Consequences

N/A
