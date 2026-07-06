---
uid: DEC-8c489b
title: "Evidence as Structural Lineage — FK chain IS the evidence, no separate evidence table"
description: "Eliminate separate evidence_object table. FK chain across boundaries IS the lineage. SQL view for uniform traversal. Superseded."
status: superseded
date: 2026-03-25
project: platform
domain: database
refs:
  - type: decision
    label: "D210"
  - type: decision
    label: "D213"
authority: retired
migrated_from: legacy v2 archive
---


# Evidence as Structural Lineage — FK chain IS the evidence, no separate evidence table

## Context

Superseded by DEC for D212 v2. v1 dropped evidence entirely. v2 keeps per-run evidence summaries in RDS (lightweight audit) + archives detailed evidence to S3. Defense in depth without 5x write amplification.

## Problem

The patent (Section 10) describes Evidence Objects at every boundary transition. The current implementation creates evidence_object rows at each boundary. But this produces massive write amplification with zero information gain.

### The math

One journal entry row flowing through the full chain:

| Boundary | Business object created | Evidence Object created |
|----------|----------------------|----------------------|
| Observation | observed_record | 1 |
| Admission | source_object | 1 |
| Canonical Evaluation | canonical_object | 1 |
| Metric Evaluation | metric_snapshot | 1 |
| Action Evaluation | action_object | 1 |

**5 evidence rows per 1 business row.**

- Reader extracts 10,000 journal entries → 50,000 evidence objects
- Tenant with 20 entities, 10K rows/month each → 1,000,000 evidence objects/month
- Before you've done anything useful, evidence is the largest table in the system

### What each evidence object contains

```
evidence_id:      UUID
object_ref:       "canonical_object:uuid-xxx"
predecessor_ref:  "source_object:uuid-yyy"
contract_ref:     "contract:uuid-zzz"
outcome_code:     "ADMITTED"
timestamp:        2026-03-25T...
```

Now look at the canonical_object row itself:

```
canonical_object_id:   uuid-xxx       ← same as evidence.object_ref
source_object_id:      uuid-yyy       ← same as evidence.predecessor_ref (FK)
contract_id:           uuid-zzz       ← same as evidence.contract_ref (FK)
evaluation_outcome:    "ADMITTED"      ← same as evidence.outcome_code
created_at:            2026-03-25     ← same as evidence.timestamp
```

**Every field in the evidence object already exists as a column on the business object itself.** The evidence table is a denormalized copy that adds zero information.

### What the patent claims evidence provides

**1. Transitive propagation (chain traversal)**
FK chain already does this: typed_row → CO → SO → OR. Standard SQL JOINs.

**2. Immutability**
The objects themselves are INSERT-only. Already immutable.

**3. Deterministic replay**
Contract version + immutable objects already enables this. contract_id on each object records which contract version produced it.

### What evidence actually is

A **uniform query interface**. Instead of knowing that canonical_object.source_object_id links back and source_object.observed_record_id links back, you get one table with from_ref → to_ref. That's a query convenience layer — not a data integrity mechanism.

**Is a query convenience layer worth 5x write amplification on every business transaction?** No.

## Decision

**Eliminate the separate evidence_object table. The FK chain IS the evidence. Provide a SQL view for uniform traversal.**

```sql
CREATE VIEW lineage_chain AS
-- Observation → Source
SELECT
  observed_record_id AS from_id,
  'observed_record' AS from_type,
  source_object_id AS to_id,
  'source_object' AS to_type,
  contract_id,
  evaluation_outcome AS outcome_code,
  created_at
FROM source_object

UNION ALL

-- Source → Canonical
SELECT
  source_object_id,
  'source_object',
  canonical_object_id,
  'canonical_object',
  contract_id,
  evaluation_outcome,
  created_at
FROM canonical_object

UNION ALL

-- Canonical → Metric
SELECT
  canonical_object_id,
  'canonical_object',
  metric_snapshot_id,
  'metric_snapshot',
  metric_contract_id,
  evaluation_outcome,
  created_at
FROM metric_snapshot

UNION ALL

-- Metric → Action
SELECT
  metric_snapshot_id,
  'metric_snapshot',
  action_object_id,
  'action_object',
  action_contract_id,
  evaluation_outcome,
  created_at
FROM action_object;
```

Same uniform traversal interface. Zero additional storage. Zero write amplification.

### Comparison

| Aspect | Separate evidence table | FK chain + view |
|--------|------------------------|-----------------|
| Write cost | 5x amplification | Zero overhead |
| Storage | Largest table in system | Zero |
| Information content | Duplicate of existing FKs | Already on objects |
| Query interface | Uniform table scan | Uniform view |
| Immutability | INSERT-only table | INSERT-only objects |
| Chain traversal | Single table | JOIN or view |
| Patent "persistent evidence" | Separate artifact | Structural — objects ARE persistent |

### What this means for D210

D210 (typed payload tables) + D212 (structural lineage) = full patent compliance without a separate evidence table. The evidence plane becomes a **logical construct** (the view) rather than a physical one (a table with 5x row count).


## Options Considered

N/A

## Patent Review — STRUCTURALLY EQUIVALENT

The patent claims "persistent Evidence Objects" with "instance-level lineage (specific record to specific record)." The business objects themselves are persistent and carry all evidence fields (predecessor ref via FK, contract ref via FK, outcome code, timestamp). The FK chain provides instance-level record-to-record traceability. The lineage_chain view materializes the uniform interface the patent describes.

The patent's inventive claim is the **traceability property** — that you can traverse from any action back to the raw source data through an unbroken chain. This property is preserved by the FK chain. The storage mechanism (separate table vs. structural FKs + view) is an implementation choice, not a patent claim.

## Foundation Review

The foundation spec says Evidence Objects reference only COs, MSs, and Interventions — not SOs or ORs. The current per-row evidence at observation boundary actually violates this. D212 resolves the violation by removing the separate evidence table entirely and letting structural FKs provide the lineage the foundation describes.

Note: the foundation was written as a conceptual/visualization model, not a literal implementation spec. D213 addresses tightening the foundation boundary definitions to match implementation reality.

## Consequences

N/A
