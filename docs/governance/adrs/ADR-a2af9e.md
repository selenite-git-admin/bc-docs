---
uid: DEC-a2af9e
title: "Single Cognito User Pool with custom:tenant_id"
description: "One Cognito User Pool for all tenants. Tenant isolation via custom:tenant_id attribute, not separate pools."
status: implemented
subdomain: tenant-binding
focus: claims-design
date: 2026-02-26
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Single Cognito User Pool with custom:tenant_id

## Context

Simpler to manage than pool-per-tenant. Database schema-per-tenant already provides physical data isolation. Most enterprises want Bring Your Own IdP (federation), not isolated pools. Custom attribute tags user to tenant. Can add per-tenant IdPs to single pool. Pool-per-tenant only needed for government/defense compliance — rare in accounting sector.

## Decision

Single User Pool for all tenants. custom:tenant_id (immutable) maps users to tenants. Federation-ready for enterprise tenants (SAML/OIDC per tenant). Architecture supports migration to pool-per-tenant if specific compliance demands it — bc-core JWKS validation is issuer-configurable.

## Options Considered

N/A

## Consequences

N/A
