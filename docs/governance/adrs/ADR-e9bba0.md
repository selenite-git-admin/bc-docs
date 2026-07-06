---
uid: DEC-e9bba0
title: "Tenant infrastructure table — per-tenant deployment configuration on platform DB"
description: "Add tenant.tenant_infrastructure (1:1 with tenants) for deployment config: tier, DB host, schema, storage, compute, region, provisioned/approved by."
status: implemented
subdomain: tenant-deployment
focus: infrastructure-config
date: 2026-03-20
project: bc-infra
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Tenant infrastructure table — per-tenant deployment configuration on platform DB

## Context

Tenant infrastructure config belongs on platform, not tenant DB. Currently only DB schemas, but future deployment options (dedicated compute, dedicated storage, network isolation, custom domains, resource quotas) need proper columns per D089 Rule 1 (no JSONB for queryable data). provisioned_by_name + approved_by_name provide separation of duties (ISO 27001).

## Decision

Add `tenant.tenant_infrastructure` (1:1 with tenants via unique index on tenant_id). Columns: deployment_code (shared/dedicated_compute/dedicated_full), database_host, database_schema_name, storage_bucket_name, compute_pool_ref, network_ref, custom_domain, resource_quota_json (opaque JSONB), region_code, status_code (provisioning/active/decommissioning/decommissioned), provisioned_at/by_name, approved_at/by_name. Platform-owned — tenants don't see their own infra config.

## Options Considered

N/A

## Consequences

N/A
