---
id: security-operations
order: 32
title: "Security Operations"
status: drafting
authority: authoritative
depends_on: [the-authority-model, infrastructure, deployment-topology, backend-services, tenancy-and-binding]
governing_sources:
  - Data Model and Schema
  - The Authority Model
  - Infrastructure
  - Deployment Topology
governing_adrs:
  - DEC-1918d0 (Deployment and database architecture; two-database split)
  - DEC-771baf (Tenant database topology; tenant ownership boundary)
  - DEC-490520 (PII classification at source field level)
  - DEC-69f09e (ISO 11179 naming standard)
  - DEC-441665 (CodeArtifact supply-chain mitigation)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Security Operations

## Scope

This chapter records the operational view of platform security: the JWT authentication boundary at the request edge, the per-tenant scope discipline that prevents cross-tenant data exposure, the secrets surface (Cognito credentials, AWS service-account keys, CodeArtifact tokens, Bedrock access), the supply-chain governance via the AWS CodeArtifact npm mirror, the PII classification trail at the Source Field layer (DEC-490520), the pre-commit hook surface that bc-qa installs across repositories, and the security-operations gaps the platform records explicitly. It records the boundary between Security Operations and the deploy-time provisioning of those security primitives (Infrastructure, Deployment Topology). It records the as-built drift between the procedure and the platform's current security posture.

This chapter does not redefine the AuthN substrate (Cognito; Infrastructure governs the deployment), the tenant ownership boundary (Tenancy and Binding), the audit substrate that records security events (Audit and Activity Logging in Implementation), or the formal compliance control map (Compliance section, queued).

**Governing source.** outline.md §4.7; The Authority Model.

## What the Procedure Produces

A security-operations cycle produces:

| Artifact | Persistent store | Created by |
|---|---|---|
| Cognito user creation, role assignment, session record | AWS Cognito user pool `cognito-pool-platform-dev-aps1` | `auth.service.ts` admin-provisioned paths |
| JWT access and ID tokens (15-minute validity) | Cognito issuer | `cognito-jwt.strategy.ts` validates incoming tokens against the JWKS URL |
| Refreshed CodeArtifact npm token (twelve-hour TTL) | AWS CodeArtifact under the `barecount` domain | `aws codeartifact login` operator action |
| PII classification per source field | `source.source_field.pii_classification` | The PII classification step at field admission per DEC-490520 |
| Pre-commit hook artifacts | Per-repository `.git/hooks/pre-commit` from `bc-qa/hooks/install-hooks.sh` | Engineer onboarding |

The procedure produces no infrastructure-as-code mutations. The deploy-time provisioning of the user pool itself is owned by the `cd-deploy.yml` GitHub Actions file against AuthStack (Deployment Topology); this chapter records what runs against the provisioned substrate operationally.

**Governing source.** Infrastructure; Deployment Topology.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| AuthStack deployed in the target AWS account | The Cognito user pool is the request-boundary substrate; without the pool, no JWT validation is possible |
| Platform AWS profile configured locally | Per CLAUDE.md, every AWS CLI operation runs against the named platform profile (account identifier, region code, and profile name are deploy coordinates owned by Infrastructure); the default profile points at a different account |
| CodeArtifact domain `barecount` and repository `npm-mirror` provisioned | All `npm install` routes through CodeArtifact per DEC-441665; absence breaks dependency installation |
| bc-qa cloned alongside bc-core | The pre-commit hook installer at `bc-qa/hooks/install-hooks.sh` runs against each repository the engineer wants gated |

A precondition that fails is not bypassed.

**Governing source.** Infrastructure; CLAUDE.md.

## Authentication Boundary: Cognito JWT

The request-boundary discipline is JWT validation against the Cognito issuer. bc-core's `CognitoJwtStrategy` at `src/auth/strategies/cognito-jwt.strategy.ts` is the validator; the issuer URL and JWKS URL are read from the SSM parameters `bc/dev/auth/cognito-issuer-url` and `bc/dev/auth/cognito-user-pool-id` that AuthStack publishes at deploy time.

Token shape:

| Property | Value |
|---|---|
| Access and ID token validity | AuthStack-configured short-lived window |
| Refresh token lifetime | AuthStack-configured refresh window |
| Issuer URL | `https://cognito-idp.ap-south-1.amazonaws.com/{userPoolId}` |
| JWKS URL | `https://cognito-idp.ap-south-1.amazonaws.com/{userPoolId}/.well-known/jwks.json` |
| Multi-tenant claims | `custom:tenant_id`, `custom:roles`, `custom:display_name` |

The JWT guard, role guard, and scope guard at `bc-core/src/auth/guards/` are the request gate per route. A request without a valid token is rejected at the JWT guard before any controller code runs. A request with a valid token but insufficient role or scope is rejected at the role or scope guard.

**Per-tenant route scope is enforced, but tenant-selector matching is not.** The JWT carries `custom:tenant_id`, and `CognitoJwtStrategy` copies it into `AuthUser`. Current `ScopeGuard` enforces platform-versus-tenant route scope only; it does not compare the token tenant to `x-tenant-id` or subdomain. That comparison is recorded as drift, not as an active guard guarantee.

**Governing source.** `bc-core/src/auth/strategies/cognito-jwt.strategy.ts`; `bc-core/src/auth/guards/`; Infrastructure.

## Secrets Surface

The platform's secrets surface lives at four substrates. Each is governed by a different operational discipline.

| Substrate | What it holds | How it is provisioned | Rotation |
|---|---|---|---|
| AWS Secrets Manager (queued) | The dormant Aurora PostgreSQL secret rotation in `PlatformInfraStack` configures 30-day rotation; the rotation surface is in code but not deployed | CDK `aurora-postgres.ts` construct | Every 30 days when the stack is deployed |
| AWS SSM Parameter Store | Cognito user pool ID, client ID, issuer URL | AuthStack at deploy time | Manual; SSM parameters are immutable per stack version |
| Tenant `runtime.connection` rows | Per-tenant credentials for source systems (BYO-DB connection strings, source system API keys) | Authored at Tenant Onboarding Step 6; stored encrypted at rest | Manual rotation via re-authoring the Connection record |
| CodeArtifact npm token | Twelve-hour scoped token for `npm install` | `aws codeartifact login --tool npm --domain barecount --repository npm-mirror --region ap-south-1` | Manual; expires every twelve hours |

The CodeArtifact rotation is the most frequent operational task an engineer performs. CLAUDE.md records the renewal command; absence of a renewed token surfaces as HTTP 401 or 403 on `npm install`.

The Bedrock access key is NOT a separate secret. bc-ai's `boto3.Session(profile_name='barecount', region_name='ap-south-1').client('bedrock-runtime')` uses the local AWS profile credentials; the per-engineer credential is the boundary.

**Governing source.** `platform-infra-stack/cdk/lib/constructs/aurora-postgres.ts`; `bc-ai/app/clients/bedrock.py`; CLAUDE.md.

## Supply-Chain Governance: AWS CodeArtifact

Every npm install in the five npm-consuming repositories (barecount-devhub, bc-core, bc-portal, bc-admin, bc-qa) routes through AWS CodeArtifact's `npm-mirror` repository per `DEC-441665`. The mirror delegates to `npm-public`, which delegates to npmjs.org. A package not yet seen by the platform is fetched on first install and cached for subsequent installs. bc-ai (Python) and bc-docs (markdown) do not consume the npm registry.

| Property | Value |
|---|---|
| Domain | `barecount` |
| Repository | `npm-mirror` |
| Repository chain | `npm-mirror` receives packages from the external npm store |
| Token TTL | Twelve hours |
| Auth path | `aws codeartifact login --tool npm --domain barecount --repository npm-mirror --region ap-south-1` |
| Project enforcement | Each project's committed `.npmrc` configures the registry URL to the CodeArtifact endpoint; CI honors the same `.npmrc` |

Per CLAUDE.md, `.npmrc` files are committed to Git; engineers do not remove or bypass them. Setting `registry=https://registry.npmjs.org` in any project is forbidden because it bypasses the supply-chain mirror. The discipline applies in CI through the same committed `.npmrc`.

The discipline is the platform's ISO 27001 A.14.2.1 control surface (per CLAUDE.md). A package that the platform does not depend on is not in CodeArtifact's cache; the next `npm install` of a malicious or compromised package would surface as a CodeArtifact pull from npmjs.org with a deterministic provenance trail.

**Governing source.** CLAUDE.md (NPM Registry section); per-project `.npmrc` files.

## PII Classification at Source Field Layer

DEC-490520 establishes PII classification at the source field level. Each row in `source.source_field` carries a `pii_classification` value (`none`, `personal`, `sensitive`, `confidential`); the value is set at field admission via the AI PII classifier path.

The operational consequence: every Source Object the Reader produces, every Canonical Object the canonical evaluator produces, and every Metric Snapshot the metric engine produces inherits the PII classification of its source fields through the chain. The classification is not duplicated at each layer; the chain reads it from `source.source_field` at the layer that needs it.

The classification surface admits the four values listed in the readiness baseline; later nullification of PII fields per the platform's Privacy and the Immutable Fact policy (queued in Compliance) is the policy that consumes the classification at request time.

**Governing source.** DEC-490520; `bc-core/src/database/schema/source/source-field.ts`.

## bc-qa Pre-Commit Hooks

The pre-commit gate at `bc-qa/hooks/pre-commit` runs against any repository that has installed it via `bash bc-qa/hooks/install-hooks.sh <repo-path>`. The hook enforces:

| Check | Form |
|---|---|
| `eval()` is forbidden | Block per the universal coding rule (CLAUDE.md) |
| `@ts-ignore` discouraged | Use `@ts-expect-error` with justification comment |
| `console.log/info/debug/trace` not in `src/` | Only `console.warn()` and `console.error()` admissible |
| ESLint clean | Per `@barecount/eslint-config` from CodeArtifact |
| Python `ruff` clean for bc-ai | Per `pyproject.toml` `[tool.ruff]` rules |

The hook is a safety net, not the only enforcement. The post-hoc audit at `bc-qa/audits/audit-repo.sh <repo-path>` runs the full check set against any repository on demand, and the `devhub_qa_audit` MCP tool triggers audits from Claude sessions.

**Governing source.** `bc-qa/hooks/pre-commit`; `bc-qa/hooks/install-hooks.sh`; CLAUDE.md (Coding Standards section).

## Audit Substrate

Security-relevant events emit through the audit substrate that the Audit and Activity Logging chapter (Implementation) governs. The relevant emission points:

| Event | Emission |
|---|---|
| Cognito JWT validation failure | bc-core logs the rejection at the JWT guard; no separate Cognito-side audit trail is consumed in the readiness baseline |
| Tenant scope mismatch | bc-core logs the rejection at the role or scope guard; the event is recorded in the request log, not in a separate security log |
| `@PlatformOnly()` route accessed by tenant token | Same as the tenant scope mismatch path |
| AI act evidence and budget rows | Evidence rows record completed maker-checker-gate acts; `budget_log` records Bedrock and direct-Anthropic cost; Gemini budget capture remains a gap |
| Document access through the bc-admin reader | `DocsController.audit()` writes JSONL for successful controller responses; lookup misses and rate-limit denials are warning logs in the readiness baseline |

The `bc-core/src/audit/audit.service.ts` scaffold is wired into `DocsController` as a proof-of-concept caller; broader rollout to every authenticated mutation is queued in the Audit and Activity Logging chapter's drift inventory. The DocsController-side write is conditional: `DocsController.audit()` writes JSONL after successful response handling and delegates to `AuditService.append(...)` fire-and-forget for the durable row in `operations.audit_log`; lookup misses and rate-limit denials surface as warning logs in the readiness baseline rather than as audit rows.

AWS CloudTrail is not consumed in the readiness baseline. The Cognito user pool emits CloudTrail events for admin operations; the platform does not aggregate those events into a security-operations dashboard. The gap is recorded in the Audit and Activity Logging chapter.

**Governing source.** Audit and Activity Logging; `bc-core/src/audit/audit.service.ts`; `bc-core/src/docs/docs.controller.ts`.

## Failure Modes

| Cause | System response |
|---|---|
| JWT signature invalid | bc-core's JWT guard rejects with HTTP 401 before controller code runs |
| Token expired (past access-token validity) | Same as invalid signature; client renews via the refresh token (the term `refresh token` is the OAuth and OIDC protocol identifier and is admissible as protocol vocabulary) |
| `custom:tenant_id` claim absent on a tenant-scoped route | Tenant scope guard rejects with HTTP 403; logged but no separate audit row in the readiness baseline |
| CodeArtifact token expired | `npm install` fails with HTTP 401 or 403; engineer re-runs `aws codeartifact login` |
| AWS profile drifts from `barecount` | bc-ai's Bedrock client connects to the wrong account; queries fail at IAM authorization; the failure is loud, not silent |
| Pre-commit hook missing on the engineer's clone | The hook is opt-in; an engineer who has not run `install-hooks.sh` skips local enforcement; the post-hoc `bc-qa` audit and CI ESLint gate (where wired) catch the same violations later |
| PII field misclassified at admission | The wrong `pii_classification` propagates through the chain; correction requires re-running the PII classification step and updating `source.source_field`; later COs and Metric Snapshots inherit the correction at next evaluation |

**Governing source.** `bc-core/src/auth/`; `bc-qa/`; `bc-ai/`.

## Drift Inventory

| Drift item | Form |
|---|---|
| AWS CloudTrail not consumed | Cognito admin operations emit CloudTrail events; the platform does not aggregate them; security-operations dashboard for admin actions is queued |
| MFA optional in dev | The deployed Cognito user pool has MFA optional in dev and required in prod (per `cognito-user-pool.ts`); the gap is intentional during platform development but recorded |
| Tenant secret rotation is manual | Tenant `runtime.connection` rows hold per-tenant credentials; rotation is operator-initiated re-authoring; no automated rotation surface in the readiness baseline |
| Pre-commit hook is opt-in | Engineers who have not installed the hook skip local enforcement; post-hoc audit and CI gates catch the same issues later but the latency is days, not seconds |
| ESLint and TypeScript strict gates partially wired | CLAUDE.md records per-repo severity (block in bc-core and bc-admin; warn in bc-portal; skip in bc-ai and devhub); CI enforcement matches the severity but per-repo `.github/workflows/` test workflows are absent in the readiness baseline |
| No formal Security Operations dashboard | No single pane of glass for JWT rejections, scope mismatches, CodeArtifact pulls, PII classification volume, or Cognito admin actions; each emission point is its own surface |
| Bedrock per-tenant usage not recorded | bc-ai writes one evidence row per invocation but the per-tenant aggregation is not surfaced in the readiness baseline; per-tenant AI cost attribution is queued in AI Usage Visibility (drafted) |

**Governing source.** Audit and Activity Logging; `bc-ai/`; `bc-core/`.

| JWT tenant selector match not enforced | `ScopeGuard` enforces platform-versus-tenant route scope only; it does not compare `custom:tenant_id` to `x-tenant-id` or subdomain. | High |

## Boundary with Other Operations Chapters

| Chapter | Relationship |
|---|---|
| Tenant Lifecycle and Subscription | Owns the tenant-side subscription state and entitlement; this chapter consumes the tenant identity at the JWT scope discipline |
| Deployment Topology | Owns the deploy-time provisioning of the Cognito user pool and SSM parameters; this chapter consumes them operationally |
| Upgrade and Migration | Owns the procedures that touch the Cognito user pool's structure or the secrets substrate during a platform upgrade |
| Observability and Telemetry | Owns the log-and-metric surfaces that aggregate security events; this chapter records the emission points |
| Performance and Scale | Independent at the security layer |
| Incident and Change Management | Owns the change-record substrate that records security-relevant changes (Cognito user pool changes, secret rotations, CodeArtifact policy changes) |
| Support and Escalation | Owns the customer-side response surface for security incidents (queued) |

**Governing source.** The owning Operations chapters; outline.md §4.7.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-1918d0 | Establishes the two-database split that defines the tenant scope discipline this chapter records |
| DEC-771baf | Establishes the tenant ownership boundary that the tenant scope guard enforces |
| DEC-490520 | Establishes PII classification at the source field level; this chapter records the operational consequence of the classification trail |
| DEC-69f09e | Establishes ISO 11179 naming; the security substrate honors the naming convention (`pii_classification`, `tenant_id`, `cognito_user_pool_id`, etc.) |

The CodeArtifact supply-chain mitigation referenced in CLAUDE.md and Infrastructure (DEC-441665) is recorded in this chapter's "Supply-Chain Governance" section by name; this chapter cites Infrastructure for the deploy-time provisioning of the CodeArtifact substrate.

**Governing source.** Decisions: ADR Registry.

| DEC-441665 | Keeps authority behavior routed through the authority model; Security Operations records enforcement boundaries and drift rather than redefining authority semantics. |

## References

- The Authority Model
- Infrastructure
- Deployment Topology
- Backend Services
- Tenancy and Binding
- Tenant Lifecycle and Subscription
- Audit and Activity Logging
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-490520: PII classification at source field level
- DEC-69f09e: ISO 11179 naming standard
- `bc-core/src/auth/strategies/cognito-jwt.strategy.ts`
- `bc-core/src/auth/guards/`
- `bc-core/src/database/schema/source/source-field.ts`
- `bc-qa/hooks/pre-commit`
- `platform-infra-stack/cdk/lib/constructs/cognito-user-pool.ts`
- CLAUDE.md (NPM Registry, AWS Profile, Coding Standards sections)
- outline.md §4.7: Operations






