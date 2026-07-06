---
uid: DEC-20eefe
title: "Evidence as Structural Lineage — per-run summaries in RDS, detailed archive on S3"
description: "Per-run evidence summaries in RDS (not per-row). Detailed archive on S3 WORM. Eliminates 5x write amplification while preserving audit safety."
status: decided
subdomain: evidence-architecture
focus: per-run-summaries-s3-detail
date: 2026-03-25
project: platform
domain: database
refs:
  - type: decision
    label: "D210"
  - type: decision
    label: "D213"
authority: evolving
migrated_from: legacy v2 archive
---


# Evidence as Structural Lineage — per-run summaries in RDS, detailed archive on S3

## Context

Per-row evidence is 5x write amplification with zero information gain — every field duplicates what's on the business object. But dropping evidence entirely removes defense in depth. Per-run evidence summaries (1 row per run, not per record) plus S3 archive (detailed WORM backup) provides the same audit safety at 1/10000th the RDS write cost. Redundancy preserved where it matters (S3 WORM), eliminated where it's waste (per-row RDS duplication).

## Problem

Creating evidence_object rows at every boundary for every row produces 5x write amplification. Every field in the evidence object already exists on the business object it references. But dropping evidence entirely removes defense in depth — redundancy in the audit trail is not waste in an ISO 27001 system.

### The math (unchanged)

One row through the full chain = 5 evidence rows. 10K journal entries = 50K evidence objects. 20 entities × 10K/month = 1M evidence objects/month. Before you've done anything useful, evidence is the largest table in RDS.

### Every field is already on the business object (unchanged)

```
evidence.object_ref       = canonical_object.canonical_object_id (PK)
evidence.predecessor_ref  = canonical_object.source_object_id (FK)
evidence.contract_ref     = canonical_object.contract_id (FK)
evidence.outcome_code     = canonical_object.evaluation_outcome
evidence.timestamp        = canonical_object.created_at
```

## Decision

**Three-layer evidence architecture:**

### 1. FK chain = primary lineage (structural, zero cost)

The FK relationships between boundary objects ARE the instance-level lineage. A SQL view provides uniform traversal:

```sql
CREATE VIEW lineage_chain AS
SELECT observed_record_id AS from_id, 'observed_record' AS from_type,
       source_object_id AS to_id, 'source_object' AS to_type,
       contract_id, evaluation_outcome, created_at
FROM source_object
UNION ALL
SELECT source_object_id, 'source_object',
       canonical_object_id, 'canonical_object',
       contract_id, evaluation_outcome, created_at
FROM canonical_object
UNION ALL
-- ... metric, action
```

### 2. Per-run evidence summaries (RDS — lightweight audit)

One evidence row per run per boundary. Not per record.

```
evidence_id:    UUID
run_id:         UUID (FK to run record)
boundary_code:  'observation'
contract_id:    UUID
record_count:   10000
outcome_summary: { admitted: 9950, rejected: 50 }
archive_key:    's3://barecount-data/.../run_id.jsonl.gz'
created_at:     timestamp
```

10K records → 1 evidence row (not 10K). Contains: what contract, how many records, what outcomes, where's the archive.

### 3. S3 archive = detailed evidence (WORM safety net)

The per-run S3 archive file (from D210) doubles as the detailed evidence. Each JSONL line includes the raw payload + the envelope metadata. If you ever need per-row evidence detail, it's in the archive.

```
s3://barecount-data/{tenant}/archive/{boundary}/{entity}/{run_id}.jsonl.gz
```

### Comparison

| Approach | RDS writes per 10K records | RDS storage | Safety |
|----------|---------------------------|-------------|--------|
| Current (per-row evidence) | 50,000 evidence rows | Largest table | High (redundant) |
| D212 v1 (drop evidence) | 0 evidence rows | Zero | Low (FK only) |
| **D212 v2 (per-run + S3)** | **1 evidence summary** | **Minimal** | **High (run summary + S3 archive)** |

### What this replaces

- **Stop:** per-row evidence_object INSERT at every boundary
- **Start:** per-run evidence summary INSERT (1 row per run per boundary)
- **Keep:** lineage_chain view over FK chain for traversal queries
- **Keep:** S3 archive as detailed evidence store (shared with D210)


## Options Considered

N/A

## Patent Review — COMPLIANT

Patent claims "persistent Evidence Objects" and "instance-level lineage." Delivered by:
- Instance-level: FK chain (structural, per record)
- Persistent evidence: per-run summary in RDS + detailed archive on S3 (WORM)
- Transitive traversal: lineage_chain view
- Patent Section 13 "WORM object store": S3 Object Lock ✅

## Foundation Review

Foundation says evidence references COs/MSs/Interventions. Per-run evidence summary references the run (which produced COs/MSs), not individual SOs/ORs. This is more compliant than the current per-row evidence at observation boundary.

D213 will tighten the foundation text to match this model.

## Consequences

N/A
