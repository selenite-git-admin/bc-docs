---
uid: DEC-8d180b
title: "Three-Level Source Model — Source System / Connector Type / Connection"
description: "Source model split into 3 levels: Source System (physical), Connector Type (reusable integration pattern), Connection (live instance)."
status: implemented
subdomain: connectors
focus: 3-level-source-model
date: 2026-02-28
project: bc-infra
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Three-Level Source Model — Source System / Connector Type / Connection

## Context

D019 fully implemented with all 6 tiers materialized as catalog tables (not just tiers 1-3). Tiers 4-6 (Module, Object, Field) are structural facts about source systems — contracts reference them, they don't define them. This enables discovery, referential integrity, and reuse across contract types. Full API with CRUD for all 6 tiers, cursor-based pagination, seed data for SAP (S/4HANA FI: BKPF/BSEG, MM: EKKO) and ECB (exchange rates). schema.source_object_id FK binds contracts to source objects.

## Decision

Separate the current two-level model (connector → schema) into three levels:

1. **Source System** (master) — the physical external system (SAP S/4HANA Frankfurt, ECB SDMX Service, Oracle EBS Mumbai). Attributes: vendor, version, deployment type, owner, department, SLA, location, data domains.

2. **Connector Type** (catalog/template) — the reusable integration pattern (SAP OData Connector v2.1, SDMX REST Connector v1.0, Generic SFTP v1.0). Attributes: protocol, SDK version, supported auth methods, configuration schema.

3. **Connection** (bound instance) — ties a source system to a connector type with specific credentials and config. Attributes: endpoint, auth, rate limits, health status, schedule.

Relationships:
- source_system 1→N connection
- connector (type) 1→N connection
- connection 1→N schema (contracts bound via connection_id, NOT connector_id)
- UinBAT Reader flavor → uses a Connection

Key insight: A single source system (SAP) may require multiple connection methods (OData for real-time, RFC for batch, File for legacy). The current connector table conflates the type/template with the instance. Separating them allows proper health tracking per connection method and correct blast-radius analysis when a source system goes down.

Use case: ECB — Source System "ECB" + Connector Type "SDMX REST" + Connection "ECB-SDMX-Prod" → Reader exchange_rate_reader (ecb_sdmx flavor).

## Options Considered

N/A

## Consequences

N/A
