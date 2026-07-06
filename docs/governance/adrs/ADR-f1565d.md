---
uid: DEC-f1565d
title: "Multi-Table Executor — Backward-Compatible Interface Extension"
description: "Extend ReaderExecutor.execute() with optional sourceEntities[] for multi-table readers (e.g. SAP BKPF+BSEG). Each table fetched independently, no cross-table joins."
status: implemented
subdomain: readers
focus: executor-interface
date: 2026-03-15
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Multi-Table Executor — Backward-Compatible Interface Extension

## Context

1. Foundation spec: Reader observes without transforming. Each table row = one SO. Cross-table joins happen at Canonical Evaluation. 2. Backward compatible: existing single-table executors unchanged. 3. FRED executor already demonstrates multi-series-in-one-executor pattern. 4. Minimal interface change — no new base class or separate MultiTableReaderExecutor type. 5. SAP FI reader needs BKPF+BSEG in same execution cycle to maintain temporal consistency (same date filter, same run).

## Decision

Extend ReaderExecutor.execute() params with optional `sourceEntities: string[]` alongside existing `sourceEntity`. Single-table executors ignore it. Multi-table executors (SAP BKPF+BSEG) loop over entities, fetching each independently and returning combined observations. Each observation retains its own sourceEntity — the reader does NOT join/transform across tables. Cross-table correlation happens at the Canonical Evaluation boundary. ReaderRuntimeService resolves ALL active bindings for a reader (not just one) and passes the entity list. One admission run per execution cycle regardless of entity count.

## Options Considered

N/A

## Consequences

N/A
