---
uid: DEC-9e0cd0
title: "Contract-Typed Payload Tables — known schema gets real columns, not JSONB"
description: "Superseded approach where boundary payloads with known schemas got typed columns. Replaced by JSONB-first (D208)."
status: superseded
date: 2026-03-25
project: bc-core
domain: database
refs:
  - type: decision
    label: "D162"
authority: retired
migrated_from: legacy v2 archive
---


# Contract-Typed Payload Tables — known schema gets real columns, not JSONB

## Context

Superseded by DEC-42421d which adds the critical change: JSONB payload columns are DROPPED from envelope tables, not kept as "frozen audit artifacts." Keeping JSONB defeats the purpose of D210.

## Problem

The core tenant transactional data — SO, CO, MS, AO payloads — is stored as JSONB blobs. But the schema is known BEFORE write time: contracts define the exact fields, types, and structure before a single row is written. This means known-schema data is being stored in the wrong format, violating D162 Rule #1 ("No JSONB for queryable data").

Three compounding concerns:

### 1. Query
JSONB payloads are un-queryable for business use. `WHERE payload->>'amount' > 10000` can't use regular indexes. `GROUP BY payload->>'customer_id'` forces per-row extraction and casting. Cross-object JOINs on business fields (correlating CO vendor_id with another CO invoice_id) means joining on extracted JSONB fields — no FK enforcement, no planner stats.

### 2. Storage
JSONB repeats field names in every row. A canonical object with 30 fields repeats all 30 field name strings per row. At 1M rows/month per entity per tenant: ~50-100MB of pure key name repetition. No columnar compression. TOAST adds read amplification.

### 3. Workload
Envelope tables serve both runtime execution (write-optimized) and business reporting (read-optimized). Same table, conflicting access patterns. Analytical scans over JSONB require full detoast + extract + cast per row.

## Key Insight

**We know the schema exactly before the JSON is formed.** Contract activation defines fields and types. There is zero reason to serialize known-schema data into JSON.

## Decision

**Contract activation = DDL generation.** When a contract is activated for a tenant, generate a typed SQL table in the tenant schema.

Example: Canonical contract "Journal Entry" v1.0 activated for tenant t_demo with fields {posting_date:date, company_code:text, document_type:text, amount:numeric, currency_code:text}:

```sql
CREATE TABLE t_demo.co_journal_entry_v1 (
  canonical_object_id  uuid PRIMARY KEY
    REFERENCES t_demo.canonical_object(canonical_object_id),
  posting_date         date,
  company_code         text,
  document_type        text,
  amount               numeric,
  currency_code        text
);
```

Applies at every boundary:

| Boundary | Envelope table (unchanged) | Typed payload table (new) |
|----------|---------------------------|--------------------------|
| Observation | observed_record | or_{entity}_v{N} |
| Canonical | canonical_object | co_{contract}_v{N} |
| Metric | metric_snapshot | ms_{metric}_v{N} |

**What stays:** Envelope tables are the execution model backbone — immutable chain, contract binding, run tracking. JSONB payload column stays as frozen audit artifact.

**What's new:** Typed table holds the resolved fields with proper SQL types, proper indexes, proper planner stats.

**Runtime write:** envelope INSERT + typed table INSERT in same transaction.

**Business queries:** hit the typed table with full SQL — WHERE, ORDER BY, GROUP BY, JOIN.

**Contract version change → new table version.** co_journal_entry_v1 stays (immutable data), co_journal_entry_v2 is generated for the new version. This naturally implements the DOMNS versioning recommendation from the foundation-gaps analysis (version artifacts rather than mutate).


## Options Considered

N/A

## Patent Review — COMPLIANT

- Section 4 (Reader/Extraction): SO encapsulates "extracted values, extraction metadata, contract identifiers." Typed table = extracted values in columnar form. Envelope = metadata/contract binding. Same information, better storage. ✅
- Section 6 (Canonical/DOMNS): Immutable Attributes Block + Mutable Semantic Block separation is preserved. Envelope = execution backbone, typed table = resolved fields. Versioned table naming (v1, v2) implements the recommended DOMNS versioning model. ✅
- Section 10 (Evidence/Lineage): "Instance-level lineage, specific record to specific record." FK from typed table → envelope preserves per-instance traceability. ✅

## Foundation Review — COMPLIANT, strengthens DOMNS

- Facts Are Immutable: typed table rows are INSERT-only, same immutability as JSONB. ✅
- State Advances Forward Only: no change to state transitions. ✅
- No Recomputation: no change to finalization. ✅
- DOMNS gap resolution: foundation-gaps.md recommended "version canonical artifacts (produce CO-v2) rather than mutate." Versioned table naming (co_journal_entry_v1, co_journal_entry_v2) naturally implements this. New contract version = new table = new typed rows. Old version untouched. ✅

## Consequences

N/A
