---
uid: DEC-6bc7ef
title: "Graph DB for lineage, bindings, and contract relationships"
description: "Evaluated Neptune/Neo4j for lineage and contract relationships. Decision to keep PostgreSQL with JSONB edges and join-based traversal."
status: implemented
subdomain: data-store-strategy
focus: lineage-storage-choice
date: 2026-03-02
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Graph DB for lineage, bindings, and contract relationships

## Context

DECIDED: Stay with PostgreSQL. BareCount's object chain is a strict linear progression (SO→CO→Metric→AO) with explicit, bounded lineage edges — not an arbitrary graph. Traversal depth is known (6-8 hops max), handled well by recursive CTEs. Adding a second DB technology increases operational burden without meaningful query benefit. Revisit only if emergent relationship patterns appear that PostgreSQL genuinely cannot serve.

## Decision

Should BareCount adopt a Graph DB (e.g., Neptune, Neo4j) for modeling contract lineage, bindings, domain taxonomy, and the SO→CO→Metric→AO chain? Currently these relationships are stored as JSONB arrays in PostgreSQL (lineage edges, bindings) and queried with joins.

## Options Considered

N/A

## Consequences

N/A
