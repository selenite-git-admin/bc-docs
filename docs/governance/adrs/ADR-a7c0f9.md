---
uid: DEC-a7c0f9
title: "Canonical Resolution — Run-scoped, multi-SO, CO DAG support"
description: "Canonical resolution is run-scoped, supports multiple source objects per CO, and allows CO-to-CO DAG dependencies."
status: implemented
subdomain: contract-chain
focus: run-scoped-multi-so-co-dag
date: 2026-03-15
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Canonical Resolution — Run-scoped, multi-SO, CO DAG support

## Context

Run-scoped avoids mutable state at canonical boundary (tracking "waiting for more SOs" violates append-only model). CO DAG enables meaningful business objects (AR Position) as intermediate COs that simplify metric formulas and are independently auditable. The mapping binding schema already supports multi-source via source_dependencies, join_context, canonical_mapping — resolution service consumes this existing contract structure.

## Decision

1. Canonical resolution is RUN-SCOPED — triggered after admission completes for a run. The reader guarantees co-arrival of related entities (multi-table executor). No accumulation state, no cross-run joining. 2. Multi-SO resolution via mapping bindings — source_dependencies declare which admission contracts participate, join_context declares business key matching, canonical_mapping declares field-by-field resolution with source_ref provenance. 3. CO DAG supported — source_dependencies can reference canonical contracts (not just admission contracts). Primary COs resolved from SOs, secondary COs resolved from primary COs. Same engine, different input source. Role field distinguishes: primary, enrichment, lookup, settlement. 4. COs are immutable snapshots — each run produces fresh COs. No mutation, no back-reference. 5. Resolution input is abstract — ResolutionInput can be AR payload or CO payload, determined by source_dependency role and contract category.

## Options Considered

N/A

## Consequences

N/A
