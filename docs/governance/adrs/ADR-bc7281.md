---
uid: DEC-bc7281
title: "Connections reversed from tenant DB to platform runtime schema"
description: "Connection records moved from tenant databases to platform runtime schema. Platform owns connection lifecycle."
status: reversed
subdomain: tenant-topology
focus: schema
date: 2026-03-26
project: bc-infra
domain: database
refs:
  - type: decision
    label: "D163"
authority: authoritative
migrated_from: legacy v2 archive
---


# Connections reversed from tenant DB to platform runtime schema

## Context

1. Connectors are platform — connections are children, FK integrity requires same DB (D162 rule 3). 2. bc-admin needs cross-tenant visibility without fan-out queries. 3. Reader runtime needs connection without tenant context. 4. Follows established pattern: contracts are platform with tenant binding. 5. Connection is low-volume config, not high-volume execution data.

## Decision

Connections move back to platform DB `runtime` schema alongside connectors. D163 was overreaching — connections are infrastructure/configuration, not tenant execution data. Tenant ownership via `tenant_id` column on connection table. Same pattern as contracts (platform-level, tenant binds via contract_binding).

## Options Considered

N/A

## Consequences

N/A
