---
id: api-surface
order: 22
title: "API Surface"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-authority-model, the-dual-layer-interaction-model, operating-model-overview, architecture, backend-services, internal-modules, infrastructure, data-model-and-schema]
governing_sources:
  - Foundation
  - The Authority Model
  - The Dual-Layer Interaction Model
  - Operating Model
  - Architecture
  - Backend Services
  - Internal Modules
  - Infrastructure
  - Data Model and Schema
governing_adrs:
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules)
  - DEC-771baf (Tenant database topology; platform-tenant one-way dependency)
  - DEC-3395bc (v3 documentation structure; bc-core JWT-guarded /api/docs/*)
  - DEC-c06f41 (Spine expansion to eight sections plus home)
errata_referenced: []
v2_sources: []
diagrams: []
---

# API Surface

## Scope

This chapter records the design rationale for the BareCount API surface served by bc-core: the route shape and conventions, the authorization decorators and their global-guard enforcement, the response envelope and ETag interceptors, the Problem Detail error format per RFC 7807, request validation, pagination, rate limiting, the endpoint families at the Internal Modules cluster level, and the conventions that keep the controller surface coherent as bc-core evolves.

This chapter does not enumerate every endpoint. Per-endpoint detail (HTTP method, route, request and response shape, query parameters, response codes per route) belongs to the **API Reference** reference (`docs/api/`, queued; auto-generated from the DevHub API scanner per outline §4.9). When the API Reference lands, a reader who needs per-route detail consults it; this chapter records the conventions every endpoint follows.

This chapter sits between Data Model and Schema and Frontend Experience. Data Model and Schema records what is stored; this chapter records how the frontends and external consumers read and write that store; Frontend Experience records the UI that consumes the API. It does not redefine boundary semantics (deferred to Operating Model), the authorization invariants (deferred to The Authority Model), the per-module catalog (deferred to Internal Modules), the tenant lifecycle (deferred to Tenant Lifecycle and Subscription), or the operational SOPs that consume the API (deferred to Operations).

**Governing source.** Architecture; Internal Modules; outline.md §4.3.

## Route Shape

The API surface uses a single global prefix `/api`, set in `bc-core/src/main.ts`. Every controller's route string composes with this prefix. The chapter does not enumerate routes; the cluster groupings below name the controller families.

| Prefix | Purpose | Authorization |
|---|---|---|
| `/api/...` (no `t/` segment) | Platform-scope routes: contract authoring, registry reads, master data, governance, platform stats | `@PlatformOnly()` decorator on each controller; ScopeGuard enforces |
| `/api/t/...` | Tenant-scope routes: read-only and tenant-scoped authoring views (Connections, Tenant Bindings, tenant-filtered consumption) | `@TenantScoped()` decorator on each controller; ScopeGuard enforces platform-vs-tenant route scope. The addressed Tenant DB is resolved separately by TenantMiddleware from the `x-tenant-id` header or the request subdomain (see Authorization at the API Boundary) |
| `/api/health` | Readiness and liveness probes | `@Public()` decorator; no authentication required |
| `/api/docs` | Swagger UI for the API surface itself | Mounted in non-production environments only |
| `/api/docs/manifest`, `/api/docs/file/*splat`, `/api/docs/asset/*splat` | Documentation read-surface (DEC-3395bc) consumed by the bc-admin embedded reader | `@PlatformOnly()` plus the in-memory rate limiter |
| `/api/static/*` | Static assets such as logos | Public |

The `/api/docs` Swagger UI mount and the `/api/docs/manifest` documentation routes share a path prefix without conflict: Swagger mounts at the bare `/api/docs` path; the documentation routes mount at `/api/docs/{subpath}`. NestJS routes the two distinct paths to distinct handlers. Production runtimes do not host Swagger, so the only `/api/docs/*` routes there are the documentation read-surface.

**Governing source.** Architecture; Backend Services; DEC-3395bc.

## Controller and Verb Conventions

Every NestJS controller in bc-core uses the `@Controller(<route>)` decorator with an explicit route string. The conventions below describe the verb mix at the surface level.

| Convention | Realization |
|---|---|
| HTTP verbs | `@Get()` for reads, `@Post()` for create and list-with-body queries, `@Patch()` for partial updates, `@Delete()` for archival or removal. `@Put()` is used in one place; the platform's update convention is PATCH |
| URL design | Resource-noun routes (`/api/contracts`, `/api/t/admission-runs`); identifier in path (`/:id`); sub-resources nested under parent (`/api/contracts/:id/versions`); action verbs as POST sub-routes (`/:id/approve`, `/:id/publish`) when the action is not a pure CRUD operation |
| Async operations | Long-running operations return `202 Accepted` with an operation identifier; the consumer polls the operation by identifier. Synchronous CRUD returns `200`, `201`, or `204` |

**Governing source.** Architecture; Internal Modules.

## Authorization at the API Boundary

Authorization is enforced by three globally-registered guards, in fixed order, per Internal Modules AuthModule. The order is enforced because each guard's invariant depends on the prior:

| Order | Guard | What it enforces |
|---|---|---|
| 1 | `JwtAuthGuard` | The request carries a Cognito JWT validated locally against the issuer's published JWKS. Rejects unauthenticated requests with `401 Unauthorized` |
| 2 | `ScopeGuard` | The route's required scope (`@PlatformOnly()` or `@TenantScoped()`) matches the JWT scope (derived from the JWT audience: admin client identifier resolves to platform; portal client identifier resolves to tenant). Rejects scope mismatch with `403 Forbidden` |
| 3 | `RolesGuard` | The route's `@Roles(...)` requirement intersects with the user's `custom:roles` claim. Rejects role mismatch with `403 Forbidden` |

The `super_admin` role bypasses ScopeGuard (a privileged platform role used for cross-scope governance acts). Role enforcement is per-route via `@Roles(...)`.

The five route-decorator families are:

| Decorator | Effect |
|---|---|
| `@PlatformOnly()` | The route is platform-scope; `ScopeGuard` rejects requests whose JWT scope is not platform |
| `@TenantScoped()` | The route is tenant-scope; the request also requires the operational tenant resolved by TenantMiddleware (per Internal Modules TenancyModule) |
| `@AnyScope()` | The route accepts both platform and tenant scope; rare, used for cross-scope governance |
| `@Public()` | The route bypasses authentication; reserved for the health probe |
| `@Roles(...)` | The route additionally requires one of the named roles |

The `custom:tenant_id` JWT claim is the platform-side tenant identifier the user is bound to. The request-scope tenant identifier (the operational tenant the request targets) is resolved separately by `TenantMiddleware` from the `x-tenant-id` header or the request subdomain. ScopeGuard enforces platform-vs-tenant route scope only; a direct comparison of `custom:tenant_id` against the resolved request tenant is not enforced in the current implementation, which is recorded as a security-hardening gap in Internal Modules.

**Governing source.** Architecture; Internal Modules; The Authority Model.

## Response Envelope

`ResponseEnvelopeInterceptor` is registered globally and wraps every successful response into a consistent envelope:

```
{
  "data": <controller payload>,
  "meta": <optional metadata: pagination, etc.>,
  "timestamp": "<ISO-8601>"
}
```

The interceptor skips the wrap when the controller uses NestJS's `@Res()` raw response mode (which a small set of file-streaming and document-serving routes use). The envelope is the surface every consumer sees for ordinary JSON responses.

**Governing source.** Internal Modules; Architecture.

## ETag and Conditional Reads

`EtagInterceptor` is registered globally and applies to GET requests only. For each GET response the interceptor computes an MD5 hash of the JSON payload and emits an `ETag` response header. When the next request to the same route carries an `If-None-Match` header matching the prior ETag, the interceptor returns `304 Not Modified` with no body.

ETag is intentionally GET-only. POST, PATCH, DELETE, and PUT requests do not produce conditional read semantics; the interceptor passes them through unchanged.

**Governing source.** Internal Modules.

## Problem Detail per RFC 7807

`ProblemDetailFilter` is registered globally and catches every uncaught exception. It formats errors as `application/problem+json` per RFC 7807:

```
{
  "type":     "https://barecount.dev/problems/<slug>",
  "title":    "<human-readable summary>",
  "status":   <HTTP status code>,
  "detail":   "<optional detailed message>",
  "instance": "<request URL>",
  "errors":   [<class-validator error array, when applicable>]
}
```

The filter maps NestJS exceptions to status codes and Problem Detail types. The standard codes the platform emits:

| Status | Meaning |
|---|---|
| 400 | Bad request: malformed input the request schema rejects |
| 401 | Unauthenticated: JWT missing, invalid, or rejected |
| 403 | Forbidden: scope or role mismatch |
| 404 | Not found: resource does not exist |
| 409 | Conflict: optimistic-concurrency, duplicate key, or governance-state conflict |
| 422 | Unprocessable: input validates but is semantically rejected |
| 429 | Too many requests: rate limit exceeded |
| 500 | Internal error: uncaught exception |

The platform does not define custom `HttpException` subclasses; the standard NestJS exceptions (`NotFoundException`, `ConflictException`, `UnprocessableEntityException`, `BadRequestException`, `ForbiddenException`) carry domain-specific messages and produce the appropriate Problem Detail responses through the filter.

Validation errors raised by class-validator are surfaced as a Problem Detail with the per-field error array under the `errors` key. The status is `400 Bad Request` because the global ValidationPipe registration in `main.ts` does not set `errorHttpStatusCode: 422`; the `422` row in the table above applies only when a controller explicitly throws `UnprocessableEntityException` (typically for semantic-rejection cases that pass syntactic validation).

**Governing source.** Internal Modules; RFC 7807.

## Request Validation

A global `ValidationPipe` is registered in `main.ts` with the following configuration:

| Option | Value | Effect |
|---|---|---|
| `whitelist` | `true` | Strips properties not declared in the DTO class |
| `forbidNonWhitelisted` | `true` | Rejects requests carrying undeclared properties with `400 Bad Request` |
| `transform` | `true` | Auto-converts incoming JSON into typed DTO instances |
| `enableImplicitConversion` | `true` | Coerces query-string parameters and path params into the declared DTO types |

DTO classes use class-validator decorators (`@IsUUID()`, `@IsString()`, `@IsOptional()`, `@IsObject()`, `@IsEnum()`, and so on) as their constraint surface. The pipe runs before the controller method and produces typed instances; per-controller validation pipes are not used.

**Governing source.** Internal Modules.

## Pagination

The platform's primary pagination convention is **cursor-based**. Listing routes accept `?cursor=<base64>&limit=N` query parameters, where the cursor is an opaque base64-encoded position and the limit is bounded (default 50, minimum 1, maximum 2000). The response shape is:

```
{
  "items":   [<resource>...],
  "cursor":  "<next cursor>" | null,
  "hasMore": <boolean>,
  "count":   <optional total>
}
```

Cursor pagination is the default for all list endpoints. A small set of routes also expose **offset-based** pagination via `?page=N&pageSize=M` for cases where ordinal navigation matters (UI page-by-page browsing); the offset response shape is `{ items, total, page, pageSize, totalPages }`. Both shapes are returned through the response envelope (the pagination shape lives under `meta`).

The cursor encoding is opaque to the client; consumers do not parse or construct cursors. A consumer that requires a stable position across writes uses the cursor; a consumer that requires absolute page numbers uses the offset variant.

**Governing source.** Internal Modules.

## Rate Limiting

In the readiness baseline, rate limiting is applied to the documentation read-surface (`/api/docs/*` per DEC-3395bc). The `DocsRateLimiterInterceptor` enforces configured per-subject sliding-window request limits using in-memory counters. Exceeded limits produce `429 Too Many Requests` with a Problem Detail body.

`@nestjs/throttler` (the standard NestJS rate-limiter) is not wired up at the global level; per-route rate limiting beyond the documentation surface is a security-hardening gap. Closing the gap requires either a global `@nestjs/throttler` registration with per-route override decorators or a Redis-backed rate-limiter that supports multi-instance deployments. The readiness-baseline single-runtime topology per Infrastructure makes the in-memory limiter sufficient for the documentation surface.

**Governing source.** Backend Services; Internal Modules; DEC-3395bc.

## Endpoint Families

The endpoint surface organizes by Internal Modules cluster. Per pattern 74, this chapter records the families at the cluster level; per-route detail is the future API Reference's role.

| Cluster | Endpoint family | Authorization |
|---|---|---|
| Auth and request lifecycle | Authentication endpoints (token validation, user introspection); tenant feature flag reads | Mixed; some routes are `@Public()`, some require authentication |
| Contract registry | Contract CRUD across the seven families; chain-status reads and re-evaluation; metric readiness; formula audit; integrity reads; Business Object, Business Field, Canonical Field authoring; canonical mapping; Source Catalog tier reads; reader and connector reads; metric definition reads | `@PlatformOnly()` |
| Evaluation boundary | Boundary act invocation routes for admission, canonical evaluation, metric evaluation, action evaluation; per-record reads; per-object reads; per-run reads; orchestrator routes; reader execution | `@TenantScoped()` (the tenant-scoped reader and aggregator routes are in TenantViewsModule under `/api/t/`) |
| Execution and reconciliation | Onboarding endpoints for OC, CC, MC, CM authoring; package routes; L-node semantic verdict reads; schema-provisioner routes for connector onboarding and drift checks | `@PlatformOnly()` |
| Tenant management and views | Tenant identity CRUD (platform side); tenant-filtered consumption reads under `/api/t/` (TenantViewsModule controllers all carry `@TenantScoped()`) | Platform routes `@PlatformOnly()`; tenant-views routes `@TenantScoped()` |
| Privacy and erasure | DSAR, retention, nullification, PII registry routes | `@PlatformOnly()` |
| Catalog aggregation | Read-only business catalog and metric catalog aggregator routes for bc-admin | `@PlatformOnly()` |
| Documentation read-surface | Manifest, file, and asset routes consumed by the bc-admin embedded reader | `@PlatformOnly()` plus the docs rate limiter |
| Support and ops | Ticket routes; function admin governance routes; test bench routes | `@PlatformOnly()` |
| Health | `/api/health` readiness and liveness probes | `@Public()` |

The per-controller, per-route enumeration is not in the chapter. The future API Reference will list each route with HTTP method, full path, request and response shape, status codes, and example payloads.

**Governing source.** Internal Modules; Architecture.

## Documentation Surface and Swagger

The OpenAPI surface is wired through `@nestjs/swagger`. SwaggerModule mounts at `/api/docs` in non-production environments only. Authentication options documented in the Swagger setup include the bearer-token (Cognito JWT) and the `x-tenant-id` header used by tenant-scoped requests.

Swagger decorator coverage on controllers is high but not complete; a small set of controllers lack `@ApiTags` and `@ApiOperation` decorators. DTO classes carry `@ApiProperty` and `@ApiPropertyOptional` decorators for type and required-flag documentation. The auto-generated API Reference will consume the Swagger metadata; the gap (controllers without Swagger decorators) is the current limit on auto-generation completeness.

**Governing source.** Internal Modules.

## CORS

CORS is configured in `main.ts`. The allowed origins at the time of writing are `http://localhost:3000` (bc-portal dev server) and `http://localhost:3010` (bc-admin dev server), with `credentials: true` to permit cookies. Production CORS configuration is deployment-side and lives in Infrastructure.

**Governing source.** Backend Services.

## Failure Modes

| Cause | System response |
|---|---|
| Request lacks JWT or JWT validation fails | `JwtAuthGuard` rejects with `401 Unauthorized`; Problem Detail body |
| JWT scope does not match route's required scope | `ScopeGuard` rejects with `403 Forbidden`; Problem Detail body |
| User roles do not include the route's required role | `RolesGuard` rejects with `403 Forbidden`; Problem Detail body |
| Request body fails class-validator | `ValidationPipe` rejects with `400 Bad Request`; the Problem Detail `errors` array lists per-field violations. `422` is reserved for controller-thrown `UnprocessableEntityException` on semantic rejection |
| Request carries unknown properties | `ValidationPipe` rejects with `400 Bad Request` (`forbidNonWhitelisted`) |
| Resource does not exist | Controller throws `NotFoundException`; Problem Detail with `404` |
| Optimistic-concurrency or duplicate-key conflict | Controller throws `ConflictException`; Problem Detail with `409` |
| `/api/docs/*` rate limit exceeded | `DocsRateLimiterInterceptor` rejects with `429 Too Many Requests`; Problem Detail body |
| Uncaught server exception | `ProblemDetailFilter` catches; Problem Detail with `500 Internal Server Error`; the `detail` field carries a sanitized message |
| Tenant-scoped route reached without resolved tenant context | `TenantMiddleware` returns `400 Bad Request` before the controller handler executes |

**Governing source.** Internal Modules; Infrastructure.

## Drift Inventory

Per pattern 69, the gaps below are recorded explicitly rather than glossed.

| Gap | Severity | Detail |
|---|---|---|
| `@nestjs/throttler` not globally wired | Low | Rate limiting is applied only to `/api/docs/*` via the in-memory interceptor. Routes outside the documentation surface have no per-route rate limit. The single-runtime topology makes this acceptable for the current state; multi-instance deployment would require a Redis-backed limiter |
| Tenant-identifier divergence not enforced at the API boundary | Medium | `ScopeGuard` enforces platform-vs-tenant route scope only; it does not compare `custom:tenant_id` against the resolved request tenant. A user with one tenant in the JWT could in principle target another tenant via the `x-tenant-id` header. Closing the gap requires adding a header-vs-claim comparison in `ScopeGuard` or `TenantMiddleware`. Recorded in Internal Modules as well |
| Approximately 8 percent of controllers lack Swagger decorators | Low | The future API Reference auto-generation will not cover those controllers' routes until the decorators are added. The affected controllers are listed in the survey output that grounds this chapter; closing the gap is mechanical |
| Custom `HttpException` subclasses not used | Low | The platform uses standard NestJS exceptions with domain-specific messages. A typed-exception hierarchy could carry richer per-domain error metadata; not implemented |

**Governing source.** Internal Modules; Backend Services.

## Governing Decisions

| Decision | Title | API surface impact |
|---|---|---|
| DEC-1918d0 | Deployment and database architecture | The two-database split underlies the platform-vs-tenant route scope split and the `custom:tenant_id` claim's role |
| DEC-771baf | Tenant database topology; one-way dependency | The `/api/t/` route prefix and the `@TenantScoped()` decorator preserve the asymmetric ownership at the API boundary |
| DEC-3395bc | v3 documentation structure; bc-core JWT-guarded `/api/docs/*` | The documentation read-surface routes plus the in-memory rate limiter |
| DEC-c06f41 | Spine expansion to eight sections plus home | The API Surface chapter exists in the reshaped Implementation section per DEC-c06f41 |

**Governing source.** The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Authority Model
- The Dual-Layer Interaction Model
- Operating Model: Overview
- Architecture
- Backend Services
- Internal Modules
- Infrastructure
- Data Model and Schema
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-3395bc: v3 documentation structure
- DEC-c06f41: Spine expansion to eight sections plus home
- RFC 7807: Problem Details for HTTP APIs
- outline.md §4.3: Implementation
- Decisions: ADR Registry
