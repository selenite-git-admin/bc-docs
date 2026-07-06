---
uid: DEC-24b4ec
title: "Contract Registry — 7 Contract Types"
description: "Original 7 contract types including Extraction Contract. Superseded by D069 which retires Extraction, reducing to 6 families."
status: superseded
date: 2026-02-28
project: bc-core
domain: database
authority: retired
migrated_from: legacy v2 archive
---


# Contract Registry — 7 Contract Types

## Context

Superseded by D069 (DEC-36d78f). D018 declared 7 contract types including Extraction Contract. D069 retires Extraction Contract — extraction config is carried by Reader Flavor + Observation Schema. Contract types reduced from 7 to 6: Source, Admission, Canonical, Metric, Intervention, AI. The "extraction" category code in bc-core registry should be deprecated.

## Decision

All registry entries are Contracts (not "schemas"). Seven contract types:

1. extraction — Extraction Contract: what to extract from source systems
2. source — Source Contract: structure of observed data (SO)
3. admission — Admission Contract: admissibility rules at admission boundary
4. canonical — Canonical Contract: business meaning resolution (CO/DOMNS)
5. metric — Metric Contract: measure computation from canonical state
6. intervention — Intervention Contract: declared response to metric state
7. ai — AI Contract: feature/context definitions for AI

Dropped: gdp (old CXOFacts term, replaced by canonical), kpi (replaced by metric), extractor (replaced by extraction).

Common attributes (all types): name, display_name, category, kind, version, description, tags, owner, governance_state, data_classification, pii, sox_critical, compatibility_policy, tenant scope.

Per-version attributes: contract_json (the actual contract body, JSONB), success_score (REAL 0-1, cross-tenant), last_validated_at (TIMESTAMPTZ).

Bindings: connector_id FK on schema table. Cross-contract relationships via binding table with explicit relation types (extracts_from, observed_from, validates, maps_from, measures, references). Reader consumption via reader_binding table.

Relationships are peer bindings with explicit semantics, NOT parent-child hierarchy.

## Options Considered

N/A

## Consequences

N/A
