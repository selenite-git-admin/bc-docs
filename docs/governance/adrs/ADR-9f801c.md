---
uid: DEC-9f801c
title: "Connector tenant usage: read-only visibility in platform admin"
description: "Platform admin sees which tenants use each connector as read-only. No tenant mutation from platform side."
status: implemented
subdomain: connectors
focus: tenant-connector-visibility
date: 2026-03-14
project: bc-core
domain: connectors
refs:
  - type: decision
    label: "D062"
authority: authoritative
migrated_from: legacy v2 archive
---


# Connector tenant usage: read-only visibility in platform admin

## Context

Platform team needs to know which tenants use which connectors before deprecating or retiring them. Without visibility, lifecycle transitions are blind.

## Decision

ConnectorDetailPage shows a read-only "Tenant Usage" section: connection count per tenant, connection health, last check time. Platform team gets operational visibility without mutation of tenant-scoped connection config (per D062).

New API endpoint: `GET /connectors/:connectorId/usage` returns `{ totalConnections, byTenant: [{ tenantId, tenantName, connectionCount, healthySummary }] }`.

Platform controls: ability to change connector status to `deprecated`/`retired` which blocks new tenant connections.

## Options Considered

N/A

## Consequences

N/A
