---
id: infosec-and-access-control
order: 45
title: "InfoSec and Access Control"
status: drafting
authority: authoritative
depends_on: [the-authority-model, the-dual-layer-interaction-model, tenancy-and-binding, backend-services, audit-and-activity-logging, security-operations]
governing_sources:
  - The Authority Model
  - The Dual-Layer Interaction Model
  - Tenancy and Binding
  - Backend Services
  - Audit and Activity Logging
  - Security Operations
governing_adrs:
  - DEC-1918d0 (Two-database split; platform DB plus per-tenant DB; access-control isolation at the database layer)
  - DEC-771baf (Tenant database topology; one database per tenant; one-way dependency platform reads contracts only, tenant owns its data)
  - DEC-3395bc (bc-docs SSOT cutover; the docs anti-scraping mechanism with JWT-guarded endpoints, rate limiting, audit log)
  - DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact; mitigates RSK-cb8929)
  - DEC-ee6018 (bc-qa standalone repo; the preventive control surface)
errata_referenced: []
v2_sources: []
diagrams: []
---

# InfoSec and Access Control

## Scope

This chapter records the platform's information-security posture and the access-control surfaces that bind it. It states the Cognito JWT authentication boundary at bc-core, the ScopeGuard that classifies every authenticated request as platform-scope or tenant-scope, the `@PlatformOnly()` and tenant-scoped decorators that gate per-route access, the TenantMiddleware that resolves tenant identity from header or subdomain, the two-database split as the access-isolation substrate, the docs anti-scraping mechanism that protects the documentation surface, the AWS CodeArtifact npm registry as the supply-chain control mitigating `RSK-cb8929`, the bc-qa pre-commit hook as the developer-machine preventive boundary, and the AWS profile discipline that prevents cross-account leakage.

This chapter does not redefine the runtime tenant scope (Tenancy and Binding), the audit substrate that records access (Audit and Activity Logging), the operational secrets management (Security Operations), or the bc-qa rule set itself (Quality Assurance).

**Governing source.** outline.md §4.8; The Authority Model.

## Cognito JWT Authentication Boundary

bc-core authenticates every API request through an AWS Cognito-issued JWT. The strategy at `bc-core/src/auth/strategies/cognito-jwt.strategy.ts` validates the token via the Cognito JWKS endpoint using RS256 signatures.

| Validated claim | Form |
|---|---|
| `iss` (issuer) | Must match the configured Cognito issuer URL |
| `aud` (audience) | Must match either the platform-scope client ID or the tenant-scope client ID |
| `token_use` | Typed as `id` or `access`; the strategy handles both |
| `exp` | Token expiry; expired tokens are rejected |
| `custom:tenant_id` | Cognito custom attribute used for tenant identity resolution |
| `custom:roles` | Cognito custom attribute used for role-based decisions |

A failed authentication returns HTTP 401 with an RFC 7807 `application/problem+json` body. The `ProblemDetailFilter` at `bc-core/src/common/filters/problem-detail.filter.ts` standardizes the response; the failure is recorded in the audit substrate.

The `JwtAuthGuard` is registered globally as `APP_GUARD`; every route inherits the authentication requirement unless explicitly opted out.

**Governing source.** `bc-core/src/auth/strategies/cognito-jwt.strategy.ts`; The Dual-Layer Interaction Model.

## Scope Resolution and the Platform-vs-Tenant Boundary

After authentication, every request is classified as platform-scope or tenant-scope. The classification is enforced by `ScopeGuard` at `bc-core/src/auth/guards/scope.guard.ts`, which is registered globally as `APP_GUARD` after the authentication guard.

| Decorator | Effect |
|---|---|
| `@PlatformOnly()` | Marks a controller or route as platform-scope only; tenant-scope users cannot reach it; bc-admin operator endpoints carry this marker |
| `@TenantScoped()` | Marks a route as tenant-scope only; the request must carry tenant identity |
| (no marker) | Inherits the controller-level marker if any; routes are explicit by default |

`ScopeGuard` reads the `REQUIRED_SCOPE_KEY` metadata set by the decorator and compares it against the request's resolved scope (set by the JWT strategy at validate-time). The `super_admin` role bypasses scope checks per the role definition; this is the only scope override.

A scope mismatch returns HTTP 403 with the message naming the required scope and the request's actual scope.

**Governing source.** `bc-core/src/auth/guards/scope.guard.ts`; `bc-core/src/common/decorators/scope.decorator.ts`.

## Tenant Identity Resolution

For tenant-scope routes, the `TenantMiddleware` at `bc-core/src/tenancy/tenant.middleware.ts` resolves tenant identity before the request reaches the controller. The resolution order is:

| Source | Form |
|---|---|
| `x-tenant-id` header | Explicit identity supplied by the caller |
| Subdomain extraction | The host's leftmost subdomain (e.g., `selenite.barecount.com` resolves to slug `selenite`) |
| Failure | `BadRequestException` with the message "Tenant identification required" |

The resolved tenant context is stored in CLS (continuation-local storage) for the duration of the request. Platform-scope routes carry `cls.set('scope', 'platform')` and skip tenant resolution entirely.

The `TenantConnectionService` consumes the resolved slug and produces a connection to the tenant database `tbc_{slug}_dev`; platform-scope routes use the platform connection to `bc_platform_dev`. The two-database split per `DEC-1918d0` and the per-tenant topology per `DEC-771baf` are the access-isolation substrate that underpins this resolution.

**Governing source.** `bc-core/src/tenancy/tenant.middleware.ts`; `bc-core/src/database/tenant-connection.service.ts`; DEC-1918d0; DEC-771baf.

## Two-Database Split as Access Isolation

Per `DEC-1918d0`, the platform's data is split into two database tiers. Per `DEC-771baf`, the tenant tier carries one database per tenant.

| Tier | Database | Schemas | Access path |
|---|---|---|---|
| Platform | `bc_platform_dev` | Eleven schemas covering registry, contract, source, runtime, master, metric, operations, tenant, infrastructure, pricing, support | Platform-scope routes only; never reached from tenant-scope routes |
| Tenant | `tbc_{slug}_dev` (one per tenant) | Seven schemas during the D369 M4.4 transition: envelope (deprecated, dropped at M4.4 cleanup), progression (D369 metadata-only events; replaces envelope), fact, evidence, admin, organization, tenant_dim | Tenant-scope routes after `ScopeGuard` plus `TenantMiddleware` resolve the slug |

The connection isolation is structural: the platform connection cannot read tenant data because the connection string points at a different database; the tenant connection cannot read platform-scope tables because the search path scopes the resolution to the tenant schemas. A misrouted query returns "relation does not exist" rather than leaking data across the boundary.

The one-way dependency rule per `DEC-771baf` constrains the direction of authority: platform services read contracts (the platform-side authority) and pass governed contract bindings to tenant services; tenant services own their tenant data and never read platform-scope rows directly. The dependency direction is the access-control discipline.

**Governing source.** DEC-1918d0; DEC-771baf; `bc-core/src/database/tenant-connection.service.ts`.

## Docs Anti-Scraping Mechanism

Per `DEC-3395bc`, the bc-core documentation endpoints carry an anti-scraping discipline. The mechanism is layered.

| Layer | Form |
|---|---|
| JWT guard | All `/api/docs/*` endpoints carry `@PlatformOnly()`; only platform-scope authenticated callers reach them |
| Rate limit | `DocsRateLimiterInterceptor` at `bc-core/src/docs/docs-rate-limiter.interceptor.ts` enforces per-Cognito-subject limits: sixty requests per minute, one thousand per day; in-memory sliding-window counter |
| Audit log | `DocsController.audit()` writes a JSONL line per docs response; the AuditService caller wires the structured detail row through `auditService.append()` |
| Watermark | An invisible per-request marker is woven into the Markdown response so that scraped content is traceable to the requesting subject |
| Cache header | `Cache-Control: private, max-age=0, no-store` so that cached copies do not leak across users |

A rate-limit rejection returns HTTP 429 with a `retryAfter` field. The rejection logs a warning via the rate limiter; the durable audit row covers the successful-access path. The drift between successful-access audit emission and rate-limit-rejection logging is recorded below.

**Governing source.** DEC-3395bc; `bc-core/src/docs/docs.controller.ts`; `bc-core/src/docs/docs-rate-limiter.interceptor.ts`.

## CodeArtifact Supply-Chain Control

Per `DEC-441665`, every npm install in every BareCount repository routes through AWS CodeArtifact. The mirror caches every package the platform has ever installed; npmjs.org sits behind the mirror but is not consulted directly.

| Aspect | Form |
|---|---|
| Domain | `barecount` (CodeArtifact domain identifier owned by Infrastructure) |
| Repository | `npm-mirror` plus a delegate chain to `npm-public` then npmjs.org |
| `.npmrc` distribution | Five repos carry committed `.npmrc` (barecount-devhub, bc-core, bc-portal, bc-admin, bc-qa); two repos do not consume npm (bc-ai is Python, bc-docs is markdown-only) |
| Token TTL | Twelve hours; renewal via `npm run codeartifact:refresh` per Build and Release |
| Mitigated risk | `RSK-cb8929`: npm registry outage, package yanking incidents, dependency compromise events |

The control is structural: the `.npmrc` files are committed; an install that bypasses CodeArtifact requires an explicit override that the platform's CLAUDE.md "Don't" section names as a discipline violation. The mirror cache survives npmjs.org outages.

**Governing source.** DEC-441665; CLAUDE.md (NPM Registry section); Build and Release.

## Pre-Commit Hook as the Developer-Machine Preventive Boundary

The bc-qa pre-commit hook at `bc-qa/hooks/pre-commit` runs at developer commit time. It blocks the introduction of dynamic code execution, suppression of type-check errors, and dynamic Python execution.

| Check | Block or warn |
|---|---|
| `eval()` or `new Function()` introduced | Block |
| Python `eval()` or `exec()` introduced | Block |
| `@ts-ignore` introduced | Block; `@ts-expect-error` with justification is the substitute |
| ESLint errors on staged files | Block |
| `console.log` introduced in `src/` | Warn |

The hook is installed via `bash bc-qa/hooks/install-hooks.sh <repo-path>` per Developer Experience. It is the developer-machine boundary; the bc-qa audit harness is the on-demand boundary that catches drift in the repository state. Quality Assurance records the rule set; this chapter records the access-control role of the hook as a preventive control.

**Governing source.** `bc-qa/hooks/pre-commit`; Quality Assurance.

## AWS Profile Discipline

Every BareCount service that consumes AWS APIs runs under a single named AWS profile. The profile name, the AWS account identifier, and the region are deploy coordinates owned by Infrastructure per pattern 85; this chapter records the discipline.

| Aspect | Form |
|---|---|
| Single named profile | One profile is the only authorized identity; the default profile is rejected because it points at the wrong account |
| `bc-core` startup | Reads the profile name from `.env`; refuses to start if the profile cannot be resolved |
| CLI invocation | The operator sets the profile environment variable before running any AWS CLI command |
| Drift consequence | Using the default profile produces credential errors that surface immediately; the discipline is mandatory |

**Governing source.** CLAUDE.md (AWS section); Infrastructure.

## Constraints

| Constraint | Form |
|---|---|
| Authentication is global | Every API request reaches the JWT guard; opting out requires an explicit decorator and is rare |
| Scope resolution is global | Every authenticated request is classified as platform or tenant scope; no in-between |
| Tenant identity is required for tenant-scope | The middleware rejects tenant-scope requests without an `x-tenant-id` header or a recognized subdomain |
| Two-database split is structural | Cross-tier access is prevented by connection isolation, not by application-level checks |
| One-way dependency | Platform reads contracts; tenant owns tenant data; the dependency direction does not reverse |
| CodeArtifact is mandatory | Every npm install routes through the mirror; bypassing the mirror is a discipline violation |
| Pre-commit hook is the developer-machine boundary | The hook blocks the highest-risk introductions; the audit harness catches the rest |
| AWS profile is mandatory | The default profile is rejected; the named profile is the only authorized identity |

**Governing source.** DEC-1918d0; DEC-771baf; DEC-3395bc; DEC-441665; CLAUDE.md.

## Failure Modes

| Failure | Behavior |
|---|---|
| JWT signature invalid | HTTP 401; `ProblemDetailFilter` returns the standardized error response; AuditService records the failure |
| JWT expired | HTTP 401; the client renews the token via Cognito and retries |
| `@PlatformOnly()` route reached by tenant-scope user | HTTP 403; the `ScopeGuard` returns the message naming the required scope |
| `@TenantScoped()` route reached without tenant identity | HTTP 400; `TenantMiddleware` returns "Tenant identification required" |
| Cross-tier query attempt | The connection-tier mismatch returns "relation does not exist"; the request fails at the database layer rather than leaking data |
| Docs endpoint reached without JWT | HTTP 401; the rate limiter records nothing (the request never reaches the limiter) |
| Docs rate-limit exceeded | HTTP 429 with `retryAfter`; the rate limiter logs a warning; the durable audit row is not written for the rejected request |
| CodeArtifact token expired | `npm install` returns HTTP 401 or 403; the operator runs `npm run codeartifact:refresh` |
| AWS profile resolution fails at startup | bc-core refuses to start; the operator confirms the profile name and reruns |
| Pre-commit hook blocks a commit | Staged files remain in place; the developer fixes the violation and recommits |

**Governing source.** `bc-core/src/auth/strategies/cognito-jwt.strategy.ts`; `bc-core/src/auth/guards/scope.guard.ts`; `bc-core/src/tenancy/tenant.middleware.ts`; DEC-441665.

## Drift Inventory

| Drift item | Status |
|---|---|
| `RSK-cb8929` is referenced in `DEC-441665` and in committed `.npmrc` files but is not present as a row in the DevHub `risks` table | Recorded; risk is documented but not registered; reconciliation queued (see Risk and Vendor Management) |
| Rate-limit rejections log a warning but do not write a durable audit row | Recorded; rejection visibility is via the rate-limit warning log only; durable rate-limit-event audit is queued |
| DevHub MCP server runs on the local trusted-host port without authentication | Recorded; DevHub is a developer-machine substrate; the trust boundary is the local network; remote deployment is outside the readiness baseline |
| `.env.example` does not export the AWS profile name | Recorded; the profile is set per CLAUDE.md instruction at session start; an explicit `.env.example` entry is queued |
| Docs Markdown watermark mechanism is named in `DEC-3395bc` but per-line wiring is in the docs service module | Recorded per Documentation System; not re-stated here |
| Cross-tier prevention is by connection isolation rather than by application-level scope check on every query | Recorded; the structural prevention is the load-bearing control; an additional defense-in-depth scope check at query time is queued |

**Governing source.** `bc-qa/.npmrc`; `bc-core/.env.example`; Documentation System.

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| The Authority Model | The platform's authority semantics (who may write what) | The runtime mechanism that binds authority to the access-control boundary |
| Tenancy and Binding | The tenant-scope semantics and the binding mechanism | The runtime resolution that the access-control mechanism executes |
| Backend Services | The deployable boundary of bc-core, DevHub, bc-pg-mcp | The auth boundary as a feature of bc-core specifically |
| Audit and Activity Logging | The audit substrate and the JSONL trail | The audit emission on access events |
| Security Operations | The operational secrets, key rotation, JIT access | The runtime gate; the operational discipline is owned by Operations |
| Quality Assurance | The bc-qa rule set and the audit harness | The pre-commit hook as the developer-machine preventive boundary |
| Risk and Vendor Management | The risk register and the vendor inventory | The CodeArtifact supply-chain mitigation as a recorded risk treatment |
| ISO 27001 Conformance | The conformance posture | The InfoSec controls as the technical control surface that conformance reports against |
| SOC 2 Conformance | The Trust Services Criteria mapping | The CC6 logical-access surface specifically |

**Governing source.** outline.md §4.8; The Authority Model.

## References

- The Authority Model
- The Dual-Layer Interaction Model
- Tenancy and Binding
- Backend Services
- Audit and Activity Logging
- Security Operations
- Quality Assurance
- Risk and Vendor Management
- ISO 27001 Conformance
- SOC 2 Conformance
- DEC-1918d0 (Two-database split)
- DEC-771baf (Tenant database topology)
- DEC-3395bc (bc-docs SSOT cutover and anti-scraping mechanism)
- DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact)
- DEC-ee6018 (bc-qa standalone repo)
- CLAUDE.md (AWS section, NPM Registry section, Don't section)
