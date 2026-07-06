---
uid: DEC-c318b2
title: "Tenant Database Segregation — separate DB per tenant"
description: "Each tenant gets its own PostgreSQL database. Platform DB retains only operational metadata; business data lives in tenant DB."
status: superseded
date: 2026-03-03
project: bc-core
domain: database
authority: retired
migrated_from: legacy v2 archive
---


# Tenant Database Segregation — separate DB per tenant

## Context

Superseded by D085 (DEC-d7c1dd) hybrid model: schema-per-tenant (standard), database-per-tenant (premium). D087 implemented schema-per-tenant.

## Decision

Each tenant gets its own PostgreSQL database provisioned at tenant creation time. Tenant DB holds all business data: boundary objects (SO, CO, metric snapshots, action objects, evaluations), evidence, and lineage. Platform DB retains only operational metadata: registry (readers, connectors, contracts, source catalog), admission run logs, health checks, tenant registry, audit log. The current boundary.* and evidence.* schemas move from the shared platform DB to per-tenant databases.

## Options Considered

N/A

## Consequences

N/A
