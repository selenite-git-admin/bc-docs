---
uid: DEC-b228ec
title: "Two independent trees: Source Catalog and Integration — contracts reference provider"
description: "Source Catalog (provider>system>module>object) and Integration (connector>reader) are separate trees. Contracts bridge them."
status: implemented
subdomain: connectors
focus: catalog-integration-trees
date: 2026-03-01
project: bc-core
domain: database
refs:
  - type: decision
    label: "D018"
  - type: decision
    label: "D019"
authority: authoritative
migrated_from: legacy v2 archive
---


# Two independent trees: Source Catalog and Integration — contracts reference provider

## Context

Discovered during bc-admin Contract Registry work that the Source filter was using connectors (technical pipes) instead of source catalog providers (authoritative source of truth). Documentation, database schema, and UI were at three different stages with conflicting relationships. This decision aligns all three by establishing two clean, independent trees with a single binding point (connector → source system) and clear contract ownership (contract → provider).

## Decision

Two independent domain trees exist:

**Tree 1 — Source Catalog** (what exists, 6-tier):
Provider → System → Version → Module → Object → Field

This hierarchy is the authoritative catalog of where data comes from. Already implemented in `registry.source_provider`, `registry.source_system`, `registry.source_version`, `registry.source_module`, `registry.source_object`, `registry.source_field`.

**Tree 2 — Integration** (how we connect):
Connector → Connection → Reader

This hierarchy is the technical plumbing for data admission. Connector is the reusable pattern (e.g., "SDMX REST Connector"). Connection is a configured instance with credentials. Reader is the UinBAT executor that uses a connection.

**Binding point between trees:**
Connector references a Source System (tier 2 of Source Catalog). Example: "SDMX REST Connector" targets "ECB SDMX API" (a source system under provider "European Central Bank"). FK: `connector.source_system_id → source_system.system_id`.

**Contract ownership:**
Contracts reference Source Provider (tier 1 of Source Catalog), NOT connector or connection. A contract says "this is the admission rule for ECB exchange rates" — it belongs to the source (ECB), not to the pipe (SDMX REST connector). FK: `schema.provider_id → source_provider.provider_id`. The existing `schema.connector_id` FK is removed.

**Impact analysis:**
"Source goes down — what's affected?" is answered by: Provider → which systems → which connectors reference those systems → which connections/readers use those connectors. No connector FK needed on contracts for this.

**Supersedes:**
- D018 (DEC-24b4ec) §11.3: `connector_id` FK on schema table → replaced by `provider_id`
- D019 (DEC-8d180b): "connection 1→N schema" → contracts reference provider, not connection

## Options Considered

N/A

## Consequences

N/A
