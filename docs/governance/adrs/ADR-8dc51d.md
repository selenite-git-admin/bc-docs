---
uid: DEC-8dc51d
title: "bc-portal: resolve x-tenant-id from JWT claim at runtime, not from build-time env"
description: "bc-portal sends `x-tenant-id` to bc-core derived from the Cognito ID token's `custom:tenant_id` claim at request time. `VITE_TENANT_ID` becomes a deprecated fallback for mock/pre-auth paths and will be retired after a soak period."
status: decided
date: 2026-04-28T03:05:57.955Z
project: bc-portal
domain: auth
subdomain: tenancy
focus: runtime-claim-resolution
---

# bc-portal: resolve x-tenant-id from JWT claim at runtime, not from build-time env

## Context

The Cognito ID token's `custom:tenant_id` is the platform's authoritative tenant binding for a logged-in user (per the Tenant Onboarding SOP, Step 8, governed by DEC-771baf). bc-portal must derive its API tenant header from that same claim, not from a build-time Vite env (`VITE_TENANT_ID`). The env-based pattern is silently wrong for any deployment that serves more than one tenant from the same bundle — switching the logged-in user has no effect on the header, so cross-tenant testing produces 404s with no visible cause. Surfaced when a sandbox1 user landed on a demo-selenite-shaped 404 because the dev .env still said `demo-selenite`. The env pattern only makes sense for branded per-tenant deployments (one bundle per tenant); for multi-tenant or shared deployments it must read from the JWT.

# Tenant Identity from JWT Claim at Runtime (bc-portal)

## Decision

The `x-tenant-id` header bc-portal sends to bc-core is derived at request time from the Cognito ID token's `custom:tenant_id` claim, not from the Vite `VITE_TENANT_ID` build-time env.

### Implementation

Add `getTenantSlugSync()` to `bc-portal/apps/web/src/adapters/auth.adapter.ts` (mirrors the existing `getAuthTokenSync`). It scans Cognito's localStorage keys for the current ID token, decodes the JWT payload, and returns `custom:tenant_id` or null.

Update `bc-portal/apps/web/src/api/client.ts` so the request builder reads tenant via `getTenantSlugSync() ?? env.tenantId`. JWT wins; env stays as a fallback during the soak period.

### Why this isn't just a config fix

The pattern itself is the bug. With `VITE_TENANT_ID` as the source of truth:
- Switching the logged-in user has no effect on API calls.
- Different tenants need different bundles, contradicting the single-bundle multi-tenant deployment model that bc-core's tenant middleware (`/api/t/*` reads `x-tenant-id` per request) was built to support.
- Cross-tenant smoke testing in dev produces 404s with no visible diagnostic — surfaced today as `404 Tenant not found or inactive: demo-selenite` for a sandbox1 user.

### What this aligns with

- The Cognito user record carries `custom:tenant_id` as the canonical tenant binding (per the Tenant Onboarding SOP, governed by DEC-771baf and DEC-b97390).
- bc-core's `TenantMiddleware` already reads `x-tenant-id` per request, so the header is the right transport — only the source needed correcting.
- bc-admin already operates platform-scope (no `x-tenant-id` needed); this decision concerns bc-portal exclusively.

### Soak + retirement

`VITE_TENANT_ID` stays as fallback until two conditions hold:
- All bc-portal tenant-scoped routes are auth-gated (so a JWT is always present where the header matters).
- A short soak in dev confirms no path regresses to env-fallback.

After both, retire `VITE_TENANT_ID` entirely. Tracked as a follow-up DevHub task.

## Consequences

- Login-page → no JWT → no `x-tenant-id` header. bc-core's tenant middleware throws "Tenant identification required" if such a path hits a `/api/t/*` route. Login endpoints are public and auth-only paths are gated by `ProtectedRoute`, so this is a non-issue in practice.
- JWT-decoding failure → falls back to env. Same end-state as today on the failure path.
- One bundle now serves multiple tenants for real. Branded per-tenant builds remain possible by setting `VITE_TENANT_ID` and skipping the JWT path; the new behavior does not block that pattern.
- Switching tenants requires a re-login (new JWT). Acceptable; matches bc-admin and platform expectations.

## Implementation tracking

- Code: `bc-portal/apps/web/src/adapters/auth.adapter.ts` (`getTenantSlugSync` helper)
- Wiring: `bc-portal/apps/web/src/api/client.ts` (request header builder)
- Documentation: `bc-portal/apps/web/src/config/env.ts` (deprecation note for `VITE_TENANT_ID`)
- Follow-up: DevHub task to retire `VITE_TENANT_ID` after the soak period.
