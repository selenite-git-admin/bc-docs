---
uid: DEC-d785d4
title: "Reader → Business Object FK — SO Shape Enforcement via BO Constraint"
description: "Add business_object_id FK to runtime.reader so all flavors are structurally constrained to produce the same SO shape defined by the BO's field composition."
status: implemented
subdomain: contract-chain
focus: so-shape-enforcement-bo-fk
date: 2026-03-24
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Reader → Business Object FK — SO Shape Enforcement via BO Constraint

## Context

UinBAT Reader spec line 130: "All flavors of the same Reader produce the same standardFields." Reader identity is business-object-centric (091 §2). Without a Reader→BO FK, the SO shape consistency is a semantic promise with no technical enforcement. Adding the FK makes it structurally impossible to violate.

## The Problem

All flavors of a Reader must produce the same SO shape (same standard fields). Currently nothing enforces this — each observation_contract independently maps to business_field_ids with no shared constraint.

## The Fix

Add `business_object_id` FK to `runtime.reader`. The Reader declares which BO it reads. Every observation_contract's field_map is validated against the BO's field composition.

```sql
ALTER TABLE runtime.reader
  ADD COLUMN business_object_id uuid REFERENCES contract.business_object(object_id);
CREATE INDEX idx_reader__business_object ON runtime.reader(business_object_id);
```

## Enforcement Rule

When creating/updating an observation_contract's field_map for a Reader:
1. Load the Reader's `business_object_id`
2. Load the BO's field composition (`business_object_field` junction)
3. Every `business_field_id` in `observation_field_map` MUST exist in the BO's composition
4. Reject the operation if any field_id is not in the BO

This guarantees: all flavors map to the same BO fields → all produce the same standard SO shape.

## Chain Update

```
Business Object (defines SO shape: 12 fields)
  ↑ business_object_id FK
Reader (ar_invoice_reader)
  ├── Flavor A (SAP) → Observation Contract A → field_map targets BO fields
  ├── Flavor B (Oracle) → Observation Contract B → field_map targets BO fields
  └── Flavor C (NetSuite) → Observation Contract C → field_map targets BO fields
```

## Consequences

N/A
