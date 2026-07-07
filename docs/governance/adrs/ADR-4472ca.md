---
uid: DEC-4472ca
title: "Reader Batch Write Model — per-run operations, not per-row"
description: "Replace row-by-row writes with batch operations per run. One evidence record per run, not per row. Chunked at 5K per INSERT"
status: decided
subdomain: evidence-model
focus: batch-write-performance
date: 2026-03-24
project: platform
domain: database
refs:
  - type: decision
    label: "D210"
authority: evolving
migrated_from: legacy-v2-archive
---


# Reader Batch Write Model — per-run operations, not per-row

## Context

1. Current row-by-row model (6 ops × N rows) will not scale beyond demo workloads. Real SAP tenants produce millions of records per extraction.
2. Per-row evidence/lineage for bulk observations is pure overhead — the row's existence + run_id already provides complete traceability.
3. Reader/binding don't change mid-run — validating per-row is wasted work.
4. PostgreSQL multi-row INSERT is dramatically faster than N individual INSERTs (fewer round-trips, fewer WAL flushes, fewer index maintenance passes).

## Problem

ObservationService.recordObservation() writes ONE ROW AT A TIME with 6 DB round-trips per record:
1. Validate reader exists (query)
2. Resolve reader binding (query)
3. INSERT observed_record
4. INSERT source_object
5. INSERT evidence_object
6. INSERT lineage_object

Even recordObservationBatch() just loops the single-row method, capped at 100.

10K journal entries from SAP BKPF = 60,000 individual DB operations. This does not scale to production workloads (millions of records per extraction cycle).

## Decision

Replace row-by-row writes with batch operations scoped to a single run.

### 1. Reader validation + binding resolution: ONCE per run
The reader and binding don't change mid-run. Validate and resolve once at run start, reuse for all rows.

### 2. Envelope writes: multi-row INSERT
Single INSERT statement for all observed_records in a batch. Single INSERT for all source_objects. PostgreSQL handles multi-row VALUES natively.

### 3. Evidence + lineage: per-run granularity, not per-row
A run that observes 10K records produces 1 evidence record ("run R observed 10K records from BKPF via contract C v1") — not 10K identical evidence records. The observed_record → source_object 1:1 FK IS the per-row lineage. The run_id groups them. Per-row evidence that says "this row was observed" adds no information the row's existence doesn't already provide.

### 4. Chunked batches for very large extractions
For runs exceeding 10K rows, chunk at the batch level (e.g. 5K per INSERT), not at the row level. Each chunk is a single transaction.

### Result
10K journal entries: ~60,000 DB operations → ~3-4 batch INSERTs + 1 evidence record in 1 transaction.


## Options Considered

N/A

## Interaction with D210
If D210 (contract-typed payload tables) is adopted, the batch write includes one additional multi-row INSERT into the typed table. Typed columns make multi-row VALUES more efficient than JSONB serialization. The two decisions reinforce each other but are independently valuable.

## Consequences

N/A
