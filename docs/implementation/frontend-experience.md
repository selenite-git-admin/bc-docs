---
id: frontend-experience
order: 23
title: "Frontend Experience"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-dual-layer-interaction-model, the-authority-model, operating-model-overview, architecture, backend-services, internal-modules, infrastructure, api-surface]
governing_sources:
  - Foundation
  - The Dual-Layer Interaction Model
  - The Authority Model
  - Operating Model
  - Architecture
  - Backend Services
  - Internal Modules
  - Infrastructure
  - API Surface
governing_adrs:
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules)
  - DEC-771baf (Tenant database topology; platform-tenant one-way dependency)
  - DEC-f0e78e (Platform and tenant authority classes; x-tenant-id from a platform identity is rejected)
  - DEC-eea376 (Platform scope follows the user; admin-client tokens need the bc-platform Cognito group)
  - DEC-8dc51d (bc-portal tenant header derived from the JWT tenant claim)
  - DEC-f0c0f7 (No hardcoded enum arrays; consume master-data hooks)
  - DEC-e50b83 (Master port reservation)
  - DEC-b97390 (bc-admin embedded documentation reader)
  - DEC-3395bc (v3 documentation structure; bc-core JWT-guarded /api/docs/*)
  - DEC-ee6018 (bc-qa standalone repo; QA tooling enforces the no-hardcoded-enum-arrays rule)
  - DEC-c06f41 (Spine expansion to eight sections plus home)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Frontend Experience

## Scope

This chapter records the design rationale for the BareCount frontend experience: the two browser-shell frontends (bc-portal and bc-admin), the dual-layer interaction realized in the UI per The Dual-Layer Interaction Model, the runtime stack and design-system convention, the authentication sequence into Cognito, the master-data hook discipline, and the API client convention that consumes bc-core's response envelope and Problem Detail errors.

The chapter is deliberately a stub. Both frontends are in flux: bc-portal carries three incomplete UI iterations under active redesign; bc-admin is the more matured of the two but continues to evolve. Per pattern 69, this chapter records the in-flight state honestly rather than pretending a stable surface that does not yet exist.

Per-screen, per-component, per-route inventory is the role of the future **Screen Registry** reference, sourced from the DevHub screen-registry surface (`devhub_screen_*` MCP tools and the `screen_registry` table in DevHub's better-sqlite3 store). No generator for that reference exists. The registry is seeded by hand (DevHub `scripts/register-admin-screens.js` and `scripts/seed-screen-registry.js`); on 2026-09-30 it held 83 bc-admin screens and 0 bc-portal screens, and the DevHub tools only read or update rows. A generated reference, analogous to the Data Dictionary, remains intent. Until it exists, this chapter records the design intent; the inventory is queued.

This chapter sits between API Surface and Notifications and Webhooks. API Surface records the endpoints the frontends consume; this chapter records the design rationale of the consumers. It does not redefine boundary semantics (deferred to Operating Model), the dual-layer trust contract (deferred to The Dual-Layer Interaction Model), the per-endpoint shapes (deferred to API Surface), the embedded documentation reader's documentation discipline (deferred to Documentation System in the Development section), or the bc-portal subscription tier surface (deferred to Tenant Lifecycle and Subscription).

**Governing source.** Architecture; Backend Services; API Surface; outline.md §4.3.

## Two Frontends, Two Scopes

The platform serves browser experience through two frontends. The split realizes the dual-layer interaction model in the UI: bc-portal serves tenant-scope users (the customers whose tenant data the platform observes); bc-admin serves platform-scope users (the platform team that authors contracts and operates the platform).

| Frontend | Scope | Routes consumed | Authorization |
|---|---|---|---|
| bc-portal | Tenant scope | `/api/t/...` routes on bc-core | `@TenantScoped()` per API Surface; the JWT audience resolves to the tenant scope |
| bc-admin | Platform scope | `/api/...` routes on bc-core | `@PlatformOnly()` per API Surface; the admin-client token is platform scope only for a member of the platform Cognito group (DEC-eea376); ScopeGuard enforces |

Neither frontend is a privileged surface above the API. Both go through the same global guard chain in bc-core, registered in this order: JwtAuthGuard, ScopeGuard, TenantClaimGuard, RolesGuard (`src/auth/auth.module.ts`); both consume the same response envelope and Problem Detail formats; both share the same Cognito user pool with the audience claim distinguishing scope. The dual-layer trust contract per The Dual-Layer Interaction Model holds: each frontend can read and surface what its scope admits; neither can author beyond what its bound role permits at bc-core.

**Governing source.** Architecture; Backend Services; API Surface; The Dual-Layer Interaction Model.

## Runtime Stack

Both frontends share the same runtime stack. The chapter records the convention; specific dependency versions live in each frontend's `package.json` and drift faster than the chapter can be re-edited.

| Concern | Convention |
|---|---|
| Build and dev server | Vite |
| Framework | React |
| Language | TypeScript with strict mode |
| Server state | TanStack Query (React Query) |
| UI primitives | Radix UI primitives wrapped with Tailwind CSS via class-variance-authority (CVA). bc-admin packages this as the shadcn/ui convention; bc-portal carries an in-house variant of the same approach |
| Styling tokens | Tailwind CSS v4 with oklch color space; primary color `#7263FF` shared across both frontends |
| Form handling | react-hook-form |
| Routing | React Router (v6 family) |
| Auth client | `amazon-cognito-identity-js` (the standalone Cognito SDK; not AWS Amplify) |
| Icons | lucide-react |
| Toasts | sonner |

Vite dev-server ports follow the platform port reservation per DEC-e50b83: bc-portal on 3000; bc-admin on 3010.

**Governing source.** Backend Services; Infrastructure; DEC-e50b83.

## Authentication Sequence

Both frontends authenticate against the same Cognito user pool provisioned by the AuthStack per Infrastructure. The sequence is identical:

1. The user submits credentials at the login route.
2. `authenticateUser(email, password)` calls Cognito via the standalone SDK.
3. Cognito returns SUCCESS, MFA_REQUIRED, or NEW_PASSWORD_REQUIRED.
4. On SUCCESS, the Cognito SDK persists the ID token, the access token, and the renewal token to `localStorage` under SDK-managed keys.
5. The frontend hydrates the auth context from the persisted session on subsequent loads.
6. Every API call attaches the ID token as a `Bearer` token in the `Authorization` header.
7. On `401 Unauthorized`, the frontend redirects to the login route.
8. Logout clears the SDK-managed localStorage entries.

The token's app client and the user's group decide scope (bc-core `src/auth/strategies/cognito-jwt.strategy.ts:108-131`). A token from the bc-portal client is tenant scope. A token from the bc-admin client is platform scope only if the user belongs to the Cognito group named by `COGNITO_PLATFORM_GROUP` (bc-platform); otherwise bc-core answers `401` (DEC-eea376). ScopeGuard in bc-core then enforces route-level scope against that decision.

Multi-factor authentication is configured per Infrastructure (optional in dev, required in prod for AuthStack). MFA verification uses TOTP; it is a second step in the login sequence between SUCCESS and the authenticated landing page.

**Governing source.** Infrastructure; API Surface; Backend Services.

## API Client Convention

Both frontends call bc-core through a fetch-wrapping client that follows the same shape:

| Concern | Realization |
|---|---|
| URL base | `/api` (relative); the Vite dev server proxies `/api` to bc-core on port 3100 |
| Headers attached on every request | `Authorization: Bearer <ID token>`, `Content-Type: application/json`, and (for bc-portal tenant-scoped requests) `x-tenant-id: <tenant>` |
| Response envelope | The bc-admin client unwraps the bc-core envelope and returns the `data` value to the caller. Surfacing of `meta` (pagination) and `timestamp` to caller code is per-call where needed; the current bc-admin client does not propagate `meta` on every call. The bc-portal API client follows the same envelope shape per the established convention |
| Error handling | Non-2xx responses throw a typed `ApiError`. The current bc-admin `ApiError` carries `status`, the parsed response body, and a message string; structured Problem Detail field surfacing (`title`, `detail`, `errors[]` per RFC 7807) is per-call by reading the error body. `401 Unauthorized` is surfaced as a thrown `ApiError`; redirect to login is enforced at route-load time by `ProtectedRoute` consulting the Cognito session, not by an automatic redirect inside the fetch wrapper |
| Pagination | Cursor-based per API Surface; the client passes `cursor` and `limit` as query parameters and surfaces `hasMore` and the next cursor in the result |

The `x-tenant-id` header in bc-portal carries the operational tenant identifier. TenantMiddleware (Internal Modules, TenancyModule) reads the header to resolve the addressed Tenant DB before authentication runs. TenantClaimGuard then binds that resolution to the caller's identity: for a tenant route, the resolved tenant must equal the JWT `custom:tenant_id` claim, or the request is refused with 403 before any Tenant DB access. A `super_admin` may address another tenant, and each such access is logged (`src/auth/guards/tenant-claim.guard.ts`). The header selects the tenant; the claim authorizes it.

**Governing source.** API Surface; Internal Modules; Backend Services.

## Master-Data Hook Discipline

Per the platform's QA discipline (the no-hardcoded-enum-arrays rule audited post-hoc by `bc-qa` per DEC-ee6018), frontend code does not hardcode enum arrays for values that come from master tables in the platform. Instead, master values arrive through `useMaster*` hooks that fetch from the platform `master.*` tables via bc-core.

bc-admin implements this discipline in the readiness baseline: `useMasterIndustries`, `useMasterFunctions`, `useMasterSubfunctions`, `useMasterCurrencies`, `useMasterCountries`, `useMasterStatuses`, and others fetch from the masters API surface and cache results through TanStack Query with a configured stale window. Components that need an industry, function, or status pick consume the hook rather than embedding a literal list.

bc-portal is adopting the same discipline incrementally. The readiness baseline has `useMaster*` hooks queued for adoption; some legacy pages still carry hardcoded enum arrays from earlier iterations. This is a readiness-baseline limitation, not the design intent.

**Governing source.** API Surface; DEC-ee6018.

## Tenant Context in bc-portal

bc-portal is a single-tenant SPA per browser session. The operational tenant identifier is derived from the signed-in user's JWT `custom:tenant_id` claim (`getTenantSlugSync()`, per DEC-8dc51d) and attached to every API call as the `x-tenant-id` header (bc-portal `apps/web/src/api/client.ts`). The `VITE_TENANT_ID` env variable survives only as a deprecated fallback for mock mode and branded per-tenant deployments; its retirement is tracked as DevHub TSK-7fc51d. The frontend does not switch tenants mid-session; cross-tenant behavior is not in the bc-portal surface.

bc-admin is platform-scope and does not attach `x-tenant-id` on most requests. Pages that operate on per-tenant state (the tenants page, tenant detail, tenant binding views) pass the target tenant identifier as a query parameter or path parameter; ScopeGuard in bc-core admits the request because the platform-scope JWT carries the privilege.

**Governing source.** API Surface; Internal Modules.

## Calling Tenant Routes: What a Client Must Do

bc-core checks every `/api/t/` call in the order recorded in API Surface (Request Authorization Chain for Tenant Routes). For a frontend, that comes down to three requirements, each read from the code on `main`:

| Requirement | Why | Source |
|---|---|---|
| Sign in through the bc-portal app client and send the **ID token** as `Authorization: Bearer <token>` | bc-core accepts only ID tokens. A bc-portal client token is tenant scope; a bc-admin client token is platform scope and is refused on `@TenantScoped()` routes | bc-core `cognito-jwt.strategy.ts:104-131`, `scope.guard.ts:43-46` |
| Send `x-tenant-id: <slug>` equal to the token's `custom:tenant_id` | TenantMiddleware resolves the tenant from this header (or, without it, from the subdomain); TenantClaimGuard then refuses the call unless the slug equals the claim | bc-core `tenant.middleware.ts:73-90`, `tenant-claim.guard.ts:63-65` |
| Send a token whose user has a `custom:tenant_id` | A token with no tenant claim is refused on every tenant route, whatever header it sends | bc-core `tenant-claim.guard.ts:63` |

Which app client a frontend uses is deployment configuration: each frontend reads `VITE_COGNITO_CLIENT_ID` (bc-portal `apps/web/src/config/env.ts:25`, bc-admin `src/config/env.ts:19`), and bc-core knows the two clients as `COGNITO_CLIENT_ID` (portal) and `COGNITO_ADMIN_CLIENT_ID` (admin) (`cognito-jwt.strategy.ts:62-69`).

**bc-portal meets these by construction.** Its API client reads the tenant slug from the signed-in user's ID token (`getTenantSlugSync()`, bc-portal `apps/web/src/adapters/auth.adapter.ts:76-89`) and sends it as `x-tenant-id` (`apps/web/src/api/client.ts:46-49`), so header and claim match. A mismatch can arise only on the fallback path: when the token carries no tenant claim, the client falls back to `VITE_TENANT_ID` (`client.ts:46`), and bc-core refuses that call because the claim is absent.

**What a tenant user sees on a mismatch.** bc-core answers `403 Forbidden` with a Problem Detail body whose `detail` is "Tenant context does not match token tenant claim". The bc-portal client does not redirect on `403`; it throws an `ApiError` carrying the status and the parsed body (`client.ts:62-65`), and the calling page renders its own error state. Only a `401` sends the user to `/login` (`client.ts:57-60`). An unknown or inactive slug is refused earlier, by TenantMiddleware, with `404` and "Tenant not found or inactive: <slug>" (bc-core `tenant.service.ts:36-37`).

**bc-admin and tenant routes.** bc-admin does not send `x-tenant-id`, with one known exception: the Runtime console hooks in `src/api/runtime.ts`, which a shrink-only architecture test allowlists as debt (bc-admin `src/__architecture__/tenant-header-boundary.test.ts:8-26`, TSK-df381f). Those hooks call `t/runtime-console`, a `@TenantScoped()` controller (bc-core `src/boundary/runtime-console.controller.ts:31-32`). A platform-scope token is refused there by ScopeGuard with `403`, unless the user holds `super_admin`, which passes ScopeGuard and TenantClaimGuard for any tenant; TenantClaimGuard logs each such crossing (`tenant-claim.guard.ts:50-61`). For this reason an operator account holding `super_admin` cannot be used to see the refusals a tenant user would see.

**Governing source.** API Surface; DEC-eea376; DEC-8dc51d; DEC-f0e78e.

## bc-admin: Maturing Surface

bc-admin is the more matured of the two frontends. The route catalogue has stabilized into clusters that mirror the Internal Modules clusters: Sources (Source Catalog tiers and discovery), Registry (the seven contract families plus connectors and readers and packages), Catalog (business and metric catalogs), Business Chain (Business Field, Business Object, Canonical Field authoring), Operations (data readiness, runs, boundaries, health, integrity, activity, rejections, test bench), Governance (libraries, masters, nullification), Platform (tenants, tickets, infrastructure), and Docs (the embedded documentation reader per DEC-b97390 and DEC-3395bc).

The AppLayout shell composes a top navigation bar and a left sidebar with grouped navigation. An AI Assistant drawer is mounted globally and is available across the app. The embedded documentation reader is treated separately in the sidebar from chapter sections (per recent discipline that reference materials open as list views in the main pane rather than expand inline in the sidebar).

Per the stub-then-sync principle in this chapter, per-page detail and per-component conventions are not enumerated here. The future Screen Registry reference will surface them.

**Governing source.** Architecture; Backend Services; DEC-b97390; DEC-3395bc.

## bc-portal: Three Incomplete Iterations

bc-portal carries three incomplete UI iterations (still true on 2026-09-30; the choice of the canonical one is an open operator decision, prepared by the Customer Portal controller). Each iteration represents a different design exploration of the tenant-facing surface; none of the three is the canonical surface yet. The shared substrate across all three iterations is the runtime stack (Vite + React + TypeScript + TanStack Query + Cognito auth + the API client convention above) and the dual-layer interaction commitment (tenant scope, `/api/t/` consumption); the page-level surface differs.

This chapter does not describe the iterations individually. The full design treatment of bc-portal lands in a future revision of this chapter when one iteration is selected as canonical and the others are retired or merged. Until then, the dual-layer commitment plus the runtime stack plus the API client convention plus the auth sequence constitute everything the chapter can say honestly.

**Grounding.** The bc-portal claims in this chapter were re-checked against bc-portal `main` (b018178) on 2026-09-30: port 3000, the API client convention and the tenant header are confirmed; `useMaster*` adoption is partial (two hooks, `useMasterFunctions` and `useMasterSubfunctions` in `apps/web/src/api/masters.ts`, used only under `surfaces/dashboard/`).

**Governing source.** Architecture; The Dual-Layer Interaction Model.

## Embedded Documentation Reader (bc-admin)

The bc-admin browser shell hosts the platform's canonical documentation reader per DEC-b97390 (D372). The reader fetches manifest and content from bc-core's `/api/docs/*` routes per DEC-3395bc; the content originates in this `bc-docs` repository and is mirrored into bc-core's `private-docs/` directory by `bc-admin/scripts/sync-docs.js`.

The reader's readiness-baseline UI conventions distinguish chapter sections (expand-collapse navigation in the sidebar) from reference collections (single sidebar entry that opens a list view in the main pane with search and filters). Reference collections in the readiness baseline: Decisions, Errata, Data Dictionary; future reference collections (Contract Schemas, API Reference, SOP Index, Glossary, Diagram Index, Screen Registry) follow the same pattern.

Per pattern 67, the reader's protocol detail (manifest shape, frontmatter handling, the markdown renderer's behavior, the approval-bar and frontmatter-bar surfaces) is owned by the Documentation System chapter in the Development section. This chapter records that the reader exists and that it lives in bc-admin.

**Governing source.** Backend Services; DEC-b97390; DEC-3395bc.

## Failure Modes

| Cause | System response |
|---|---|
| `401 Unauthorized` on any API call | In bc-admin, the fetch wrapper throws an `ApiError`; the calling React Query hook surfaces it. There is no automatic redirect inside the bc-admin fetch wrapper (bc-portal's client does redirect to `/login` on `401`, bc-portal `apps/web/src/api/client.ts:57-60`). Redirect to the login route happens at route load when `ProtectedRoute` finds no active Cognito session; a 401 response mid-session that does not trigger a route change leaves the user with a thrown error in the calling component until the next route navigation re-checks the session |
| `403 Forbidden` (scope or role mismatch) | The error propagates to the calling component; the component renders a "not permitted" surface |
| `403 Forbidden` on a tenant route because `x-tenant-id` differs from the token's `custom:tenant_id` | bc-portal's client throws an `ApiError` with status `403` and the Problem Detail body (detail "Tenant context does not match token tenant claim"); no redirect. See Calling Tenant Routes |
| Network failure or timeout | The fetch wrapper rejects the promise; React Query's retry policy applies in the readiness baseline; the calling component renders an error state |
| Cognito session expired | The Cognito SDK auto-renews via the renewal token; if the renewal token has also expired, the next API call returns `401` and the redirect-to-login path runs |
| `/api` proxy not running (bc-core down in dev) | The fetch wrapper rejects with a connection error; the user sees an error state per page; the dev console shows the failed proxy attempt |

**Governing source.** API Surface; Backend Services.

## Drift Inventory

Per pattern 69, gaps between the design intent recorded above and the current state are surfaced explicitly.

| Gap | Severity | Detail |
|---|---|---|
| bc-portal carries three incomplete UI iterations | Open | None of the three is the canonical surface; this chapter cannot describe a stable bc-portal page catalogue until one iteration is selected |
| bc-portal `useMaster*` hook adoption is partial | Low | bc-admin enforces the master-data hook discipline; bc-portal has it queued. Some legacy pages still hardcode enum arrays |
| Screen Registry auto-generation is not yet built | Low | The DevHub screen registry has the data structure but is seeded by hand, bc-admin only (83 rows, 0 bc-portal on 2026-09-30); no generator analogous to `scripts/generate-data-dictionary.mjs` exists |
| The chapter is a stub | Open | A non-stub treatment requires the bc-portal canonical iteration to land and the Screen Registry to generate per-screen detail |
| Login redirect does not preserve the prior route | Low | A user who is mid-session and times out is bounced to login then back to the home page, not back to the page they were on. Implementation gap; no dedicated tracking yet |

**Governing source.** Architecture; API Surface.

## Governing Decisions

| Decision | Title | Frontend impact |
|---|---|---|
| DEC-1918d0 | Deployment and database architecture | The two-database split underlies the platform-vs-tenant scope split that the two frontends realize |
| DEC-771baf | Tenant database topology; platform-tenant one-way dependency | The asymmetric ownership rule shows up in the API client: bc-portal's `x-tenant-id` header reaches the addressed Tenant DB; bc-admin's platform-scope requests do not address a Tenant DB except through governed authoring acts |
| DEC-e50b83 | Master port reservation | bc-portal on 3000; bc-admin on 3010 |
| DEC-eea376 | Platform scope follows the user | bc-admin sign-in yields platform scope only for members of the platform Cognito group; others get `401` |
| DEC-b97390 | bc-admin embedded documentation reader | The reader is part of bc-admin's surface |
| DEC-3395bc | v3 documentation structure; bc-core JWT-guarded `/api/docs/*` | The reader fetches manifest and content from bc-core under the documented JWT-guarded routes |
| DEC-c06f41 | Spine expansion to eight sections plus home | The Frontend Experience chapter exists in the reshaped Implementation section per DEC-c06f41 |

**Governing source.** The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Dual-Layer Interaction Model
- The Authority Model
- Operating Model: Overview
- Architecture
- Backend Services
- Internal Modules
- Infrastructure
- API Surface
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-e50b83: Master port reservation
- DEC-eea376: Platform scope follows the user
- DEC-b97390: bc-admin embedded documentation reader
- DEC-3395bc: v3 documentation structure
- DEC-ee6018: bc-qa standalone repo
- DEC-c06f41: Spine expansion to eight sections plus home
- outline.md §4.3: Implementation
- Decisions: ADR Registry
