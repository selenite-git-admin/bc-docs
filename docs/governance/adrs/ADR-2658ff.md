---
uid: DEC-2658ff
title: "Contract-Typed Payload Tables — real columns in RDS, raw payloads archived to S3"
description: "Contract activation generates typed SQL tables in RDS for queryable data. Raw payloads archived to S3 per run. JSONB columns dropped from envelopes."
status: implemented
subdomain: payload-storage
focus: schema
date: 2026-03-25
project: bc-core
domain: database
authority: evolving
migrated_from: legacy v2 archive
---


# Contract-Typed Payload Tables — real columns in RDS, raw payloads archived to S3

## Context

Three-layer separation: RDS envelope (lean metadata), RDS typed table (queryable payload with real SQL types), S3 archive (schema-agnostic raw payload as WORM safety net). RDS stays lean and fast. S3 is 10x cheaper for the safety/audit/recovery role that JSONB was filling. Patent Section 13 explicitly recommends WORM object store — S3 Object Lock delivers this. DDL generator bugs are recoverable from S3 archive without re-reading source systems.

## Problem

Tenant transactional data (SO/CO/MS/AO payloads) stored as JSONB in RDS despite schema being known at contract activation time. Three concerns: un-queryable business data, storage bloat (field names repeated per row), conflicting read/write workload on same table. RDS storage at ~$0.115/GB/month makes JSONB bloat expensive.

## Key Insight

**We know the schema exactly before the JSON is formed.** Contracts define fields and types before data flows. Known-schema data in JSONB is the wrong format for the query path.

**But raw payloads are the safety net.** The DDL generator is new code — it will have bugs. The raw payload is a schema-agnostic point-in-time snapshot that doesn't depend on our type mapping being correct. We need to keep it, but not in RDS.

## Decision

**Contract activation = DDL generation for typed tables in RDS. Raw payloads archived to S3 per run. JSONB columns dropped from RDS envelope tables.**

### Typed tables (RDS — query path)

When a contract is activated for a tenant, generate a typed SQL table:

```sql
CREATE TABLE t_demo.or_bkpf_v1 (
  source_object_id  uuid PRIMARY KEY
    REFERENCES t_demo.source_object(source_object_id),
  posting_date      date,
  company_code      text,
  document_type     text,
  amount            numeric,
  currency_code     text
);
```

Table naming: `{boundary_prefix}_{entity_or_contract}_v{version}`
- Observation: `or_{entity}_v{N}`
- Canonical: `co_{contract}_v{N}`
- Metric: `ms_{metric}_v{N}`

### S3 archive (safety net / audit / recovery)

Per-run archive file containing all raw payloads:

```
s3://barecount-data/{tenant_id}/archive/{boundary}/{entity}/{run_id}.jsonl.gz
```

- One gzipped JSONL file per run per entity
- Write once, never update (WORM via S3 Object Lock)
- 10K journal entries ≈ 2MB compressed
- S3 Standard: ~$0.023/GB/month. S3 IA: ~$0.0125/GB/month. 10x cheaper than RDS.

### JSONB dropped from RDS

Envelope tables after D210:
- **Keep:** identity (PK), structural FKs (predecessor, contract, run), status/outcome, timestamps
- **Drop:** observed_payload_json, canonical_payload_json, metric_value_json, action_payload_json
- **Add:** archive_key on run record (not per row) — S3 path to the archive file

### Runtime write (per run)

1. Batch INSERT into envelope table (metadata only) — RDS
2. Batch INSERT into typed table (payload columns) — RDS
3. Single S3 PUT of gzipped JSONL (raw payloads) — S3
4. Record archive_key on run record — RDS

Steps 1-2 in same RDS transaction. Step 3 can be async (fire-and-forget with retry) or sync depending on durability requirements.

### Recovery path

If DDL generator had a bug (wrong type, missing field):
1. Read S3 archive for the affected run(s)
2. Fix the type mapping
3. Re-populate typed table from raw payloads
4. No re-reading from source system needed

### Contract versioning

New contract version → new table version. or_bkpf_v1 stays (immutable). or_bkpf_v2 generated. Old S3 archives stay — they reference v1 contract.

### Applies at every boundary

| Boundary | RDS Envelope (metadata) | RDS Typed Table (payload) | S3 Archive (safety net) |
|----------|------------------------|--------------------------|------------------------|
| Observation | observed_record | or_{entity}_v{N} | {run_id}.jsonl.gz |
| Canonical | canonical_object | co_{contract}_v{N} | {run_id}.jsonl.gz |
| Metric | metric_snapshot | ms_{metric}_v{N} | {run_id}.jsonl.gz |


## Options Considered

N/A

## Patent Review — COMPLIANT, strengthened

- Section 4/6: Typed tables = extracted/evaluated values. Envelope = metadata. Same information, optimal storage. ✅
- Section 10: Instance-level lineage via FK chain. ✅
- Section 13: Patent explicitly describes "Distributed object store with WORM for durability." S3 Object Lock = literal WORM. This is stronger than RDS JSONB ever was. ✅
- Section 14: "Storage/I/O Optimization via DOMNS" — separating metadata (envelope) from payload (typed table) from archive (S3) is exactly this. ✅

## Foundation Review — COMPLIANT

- Facts Are Immutable: typed rows INSERT-only, S3 archive WORM. ✅
- Evidence Is Recorded Not Reconstructed: raw payload preserved on S3 at observation time. ✅
- Strengthens DOMNS: versioned tables + immutable archive. ✅

## Consequences

N/A
