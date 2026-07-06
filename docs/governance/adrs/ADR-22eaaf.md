---
uid: DEC-22eaaf
title: "bc-core serves both bc-admin and bc-portal frontends"
description: "Single NestJS backend (bc-core) serves both bc-admin (platform) and bc-portal (tenant). RBAC at API layer separates admin vs tenant operations."
status: implemented
subdomain: cross-frontend
focus: backend-sharing
date: 2026-02-23
project: bc-admin
domain: tenants
authority: authoritative
migrated_from: legacy v2 archive
---


# bc-core serves both bc-admin and bc-portal frontends

## Context

bc-admin already has 140+ route shells with mock data waiting for API integration. Single backend avoids duplicating business logic. RBAC at the API layer cleanly separates admin vs tenant operations. Shared types package ensures contract alignment across all three repos.

## Decision

bc-core is the single NestJS backend API serving both frontends. bc-admin (admin portal, 140+ routes, React 18 + Vite + ShadCN) handles platform administration (tenant mgmt, platform health, billing, runtime, asset mgmt). bc-portal (customer portal, React 18 + Vite) handles tenant-scoped operations (HR, payroll, attendance). Authorization via RBAC in bc-core determines endpoint access — super_admin/org_admin for admin features, hr_manager/hr_executive/employee for portal features. Both frontends share @barecount/types for type safety.

## Options Considered

N/A

## Consequences

N/A
