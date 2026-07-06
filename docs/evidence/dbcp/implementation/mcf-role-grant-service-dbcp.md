---
uid: mcf-role-grant-service-dbcp
title: MCF — Role-Grant Service DBCP (PR-G1 design lock; resolves PR-G2 precondition; "service-first" for Cognito custom:roles updates)
description: Governance DBCP authored after PR-E1 (bc-core readiness evidence pack ahead of PR-G2 first calibrated service-surface M12 run) surfaced a hard precondition gap — bc-core has no service/API for granting the `mcf_author` role introduced by PR-S1 / PR-C4. The auth pipeline (`CognitoJwtStrategy` + `RolesGuard` + `ScopeGuard`) is consume-only; it validates inbound Cognito JWTs but does NOT manage Cognito users. No `@aws-sdk/client-cognito-identity-provider` usage exists in bc-core. The only available paths to grant `mcf_author` today are AWS Cognito Console UI, `aws cognito-idp admin-update-user-attributes` (CLI), or `mcp__AWS_API_MCP_Server__call_aws` (MCP-mediated raw AWS) — all operational shortcuts that re-create the "cliff-crossing event has no BareCount-side service surface" anti-pattern that PR-C4 retired for M12 invocation. Locks the architectural decision to build a BareCount platform-admin endpoint `POST /api/admin/mcf/role-grants` (PR-G1) ahead of PR-G2, with `@PlatformOnly()` + a new `@RequireSuperAdmin()` decorator (no admin-bypass for this sensitive endpoint), a tight `mcf_author` + `mcf_publisher` role allowlist, preservation of non-MCF roles, mandatory immutable audit emission (operator id + target id + before/after roles + reason text ≥20 chars + source PR/DBCP reference + cognito request id), and explicit rejection of the AWS-CLI / Console / raw-MCP paths as HR1 deviations after PR-G1 merges. Names the bootstrap path for the first `super_admin` as a SEPARATE DBCP (not authorized here). Defers Cognito Groups → MCF role projection (the `mcf-auth.config.ts` from PR-S1 §4.3.2 TODO) as a separate follow-up. Updates the sequencing: PR-E1 → THIS → PR-G1 (bc-core implementation) → PR-G1.5 (operator-attested first invocation granting `mcf_author` to anant@selenite.co) → PR-G2 (first-real service-surface M12 authorization DBCP) → PR-E2 → PR-A0/PR-A1 (bc-admin UI). **NOT EXECUTED** — docs-only design lock. No bc-core code change, no AWS calls, no Cognito modification, no role grants, no M12 / M12.5 / M13 / M14 invocation, no provider calls, no substrate mutation, no tenant DB touch, no metric contract authored.
status: proposed
date: 2026-05-31
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-role-grant-service
supersedes:
superseded_by:
---

# MCF — Role-Grant Service DBCP (PR-G1 design lock)

> Subordinate to PR-S1 (`docs/implementation/metric-context-framework-service-ification-dbcp.md`, merged at bc-docs-v3 main `fa1b719`) and to PR-C4 (bc-core main `2a7a1e5` — MCF controllers + McfModule). Adds **PR-G1** (bc-core implementation), **PR-G1.5** (operator-attested first invocation), and updates the sequencing so PR-G2 cannot fire until `mcf_author` is granted through the new BareCount service.
>
> Does NOT supersede PR-S1, PR-C4, MCF-ERR-001, DEC-7f9597 / D423, or DEC-ebf0b4 / D268.

## 1. Scope

### 1.1 Question this DBCP answers

> PR-C4 introduced two new MCF roles (`mcf_author`, `mcf_publisher`) on `@Roles()` guards across the four `/api/mcf/*` controllers, but bc-core has no service or API to GRANT these roles to a Cognito user. PR-E1 readiness verification surfaced that the canonical operator user (`anant@selenite.co`) carries `custom:roles = ["platform_admin", "schema_author", "operator", "analyst"]` — no `mcf_author`, no `admin`/`super_admin` bypass. `POST /api/mcf/panel-runs` returns HTTP 403 today regardless of substrate readiness. The only paths to fix this are AWS Cognito Console UI, AWS CLI, or raw AWS MCP — all of which violate the service-first discipline PR-C4 established. **What is the BareCount service path to grant MCF roles, and how does it integrate with the PR-G2 service-surface-M12 sequence?**

### 1.2 In scope

- Current-truth statement at bc-core main `2a7a1e5` and bc-docs-v3 main `fa1b719`
- Locked decision to build `POST /api/admin/mcf/role-grants` in bc-core BEFORE PR-G2
- Endpoint contract (request, response, error envelope, security guards)
- Audit contract (immutable evidence emission shape, preservation semantics, idempotency)
- MCF role allowlist (`mcf_author`, `mcf_publisher`)
- Hard rules HR1–HR7
- PR-G1 implementation scope (what code work this authorizes)
- Test obligations (15 named cases — 13 original + 2 added by amendment v2 covering defense-in-depth x-tenant-id and empty-MCF-removal paths)
- Sequencing update (PR-E1 → THIS → PR-G1 → PR-G1.5 → PR-G2 → PR-E2 → PR-A0/PR-A1)
- Risk register R1–R10
- Open questions (7 named OPEN-Q items deferred to PR-G1 implementation DBCP)

### 1.3 Explicitly out of scope

- Any bc-core code change (this is docs-only)
- Any AWS Cognito attribute update or AWS call from this session
- Any role grant
- `mcf-auth.config.ts` Cognito Groups → MCF role projection (PR-S1 §4.3.2 TODO; deferred)
- bc-admin UI for role grants (separate)
- `mcf_reader` role (does not exist as a UserRole literal yet)
- Cross-tenant role grants
- Bulk role grants
- First-time `super_admin` bootstrap (named as SEPARATE DBCP requirement)
- Updates to PR-E1 evidence pack (separate close-out in bc-core SES-461793 after this PR merges)
- PR-G2 authorization DBCP authoring
- M12 / M12.5 / M13 / M14 invocation
- Substrate mutation; tenant DB touch

## 2. Current finding (current truth at this commit)

### 2.1 bc-core has no service for role grants

| Probe | Result |
|---|---|
| `grep "@aws-sdk/client-cognito"` in `bc-core/src/` | 0 matches |
| `find` for `user.controller.ts`, `identity.controller.ts`, `role-grant.controller.ts` | 0 matches |
| `CognitoJwtStrategy` (`src/auth/strategies/cognito-jwt.strategy.ts`) | Validates inbound ID tokens via JWKS; extracts `custom:roles` JSON array into `AuthUser.roles`. No write path. |
| `RolesGuard` (`src/auth/guards/roles.guard.ts`) | Reads `AuthUser.roles`; bypass on `super_admin` OR `admin`. No write path. |
| DevHub MCP | `devhub_get_cognito_token` (read) exists; no `set_role` / `update_user` write tool. |
| TSK-e5f943 (parked, open) | "Cognito user provisioning conflates platform-admin and tenant-member identities" — acknowledges this gap area. |

### 2.2 PR-G2 is hard-blocked

PR-C4 added the role literals at `bc-core/src/types/enums.ts:20-21`:
```ts
| 'mcf_author'      // POST /api/mcf/intakes, /reject, /panel-runs
| 'mcf_publisher'   // POST /api/mcf/materialize, /evaluate-pe-mc
```

Live JWT decoded from `devhub_get_cognito_token` for `anant@selenite.co`:
```
custom:roles = ["platform_admin", "schema_author", "operator", "analyst"]
aud           = "5sn94c6o5timitiujjalv3uv11" (bc-admin client → scope=platform ✓)
token_use     = "id"
```

`RolesGuard` bypass is exactly `super_admin` OR `admin` (`roles.guard.ts:35`). Neither present. `@Roles('mcf_author')` → HTTP 403 Forbidden. PR-G2 cannot fire.

### 2.3 Why operational shortcuts are rejected

| Path | Why rejected |
|---|---|
| AWS Cognito Console UI | Manual click-through; no BareCount-side audit; no operator-attestation contract; cannot be enforced repeatable across users |
| `aws cognito-idp admin-update-user-attributes` (CLI) | Script-path; same shape PR-C4 just retired for M12; re-creates the "cliff-crossing event has no service" anti-pattern |
| `mcp__AWS_API_MCP_Server__call_aws` (raw AWS via MCP) | MCP-mediated but proxies raw AWS; leaves the role-grant outside BareCount's audit trail; no allowlist enforcement; no DTO validation |

### 2.4 Why doing nothing is not viable

Without PR-G1, every future MCF user / rotation / off-boarding becomes an unwitnessed AWS Console action. Audit drift compounds. The fix is permanent infrastructure, not a one-time exception.

## 3. Locked decisions (D-1 through D-6)

### D-1: build a bc-core platform-admin endpoint for MCF role grants BEFORE PR-G2

- Endpoint: `POST /api/admin/mcf/role-grants`
- Wraps AWS Cognito `AdminUpdateUserAttributes` behind `@PlatformOnly()` + `@RequireSuperAdmin()` + immutable audit emission
- Returns 201 with `{grant_uid, target_user_uid, roles_before, roles_after, mcf_roles_added, mcf_roles_removed, granted_at, granted_by_email_snapshot}`

### D-2: endpoint operates on `custom:roles` attribute directly

Matches the current `CognitoJwtStrategy` shape. Cognito Groups → role projection (`mcf-auth.config.ts`) is **deferred** — not because Groups are wrong but because adding the projection layer simultaneously expands scope beyond what PR-G2 needs. PR-G1 stays narrow; Groups projection is a separate follow-up DBCP.

### D-3: allowed-role allowlist — `mcf_author` and `mcf_publisher`

Encoded both in the endpoint source AND in this DBCP. Any role outside the allowlist → HTTP 400 `role_not_in_allowlist`. `mcf_reader` is out (not yet a `UserRole` literal). Expanding the allowlist requires a new DBCP.

### D-4: preservation semantics — explicit desired-set with non-MCF passthrough

Endpoint accepts `desired_mcf_roles` (allowlist subset) and computes:

```
final_roles = (current_roles ∖ MCF_ALLOWLIST) ∪ (desired_mcf_roles ∩ MCF_ALLOWLIST)
```

Non-MCF entries in `custom:roles` are NEVER added, removed, or modified by this endpoint. MCF-allowlist entries are added/removed to match `desired_mcf_roles`.

### D-5: audit emission is mandatory and immutable

Every successful grant emits a single audit row before the 201 response. The row carries:

| Field | Type | Notes |
|---|---|---|
| `grant_uid` | UUID, PK | Generated server-side |
| `granted_at` | TIMESTAMPTZ NOT NULL | Server clock at insert |
| `granted_by_user_uid` | UUID | Invoker's Cognito sub |
| `granted_by_email_snapshot` | TEXT | Immutable copy at grant time |
| `target_user_uid` | UUID | Target Cognito sub |
| `target_email_snapshot` | TEXT | Immutable copy at grant time |
| `roles_before_json` | JSONB | Full `custom:roles` array as observed pre-grant |
| `roles_after_json` | JSONB | Full `custom:roles` array as observed post-grant (re-read) |
| `mcf_roles_added_json` | JSONB | Derived: MCF-allowlist subset added |
| `mcf_roles_removed_json` | JSONB | Derived: MCF-allowlist subset removed |
| `reason_text` | TEXT NOT NULL, ≥20 chars | Operator-supplied; analogous to RejectIntakeDto |
| `source_pr_or_dbcp_text` | TEXT NOT NULL, ≥10 chars | Cite the DBCP or PR that authorized this grant |
| `cognito_request_id` | TEXT | AWS RequestId from AdminUpdateUserAttributes response for CloudTrail cross-correlation |

The BareCount audit row is the canonical reasoning record. CloudTrail captures the AWS call independently for infrastructure forensics.

### D-6: bootstrap path is NAMED but NOT authorized here

If no `super_admin` exists in the Cognito user pool, no one can call this endpoint. The first-`super_admin` provisioning requires its own DBCP authored separately. That bootstrap DBCP names a one-time AWS Console or AWS CLI action with explicit operator attestation and a check-in commit to `bc-docs-v3/docs/operations/cognito-bootstrap-evidence.md` (or equivalent — name resolved at that DBCP's time). After bootstrap, ALL subsequent role grants flow through PR-G1's endpoint. **This DBCP does NOT authorize the bootstrap.**

## 4. Endpoint contract

### 4.1 Request

```http
POST /api/admin/mcf/role-grants HTTP/1.1
Host: <bc-core-host>:3100
Authorization: Bearer <Cognito ID token, bc-admin client, custom:roles must include super_admin>
Content-Type: application/json

{
  "target_user_uid": "8bdb9bd0-8827-4cc8-b640-2087658f1eb6",
  "desired_mcf_roles": ["mcf_author"],
  "reason_text": "PR-G2 prerequisite — grant mcf_author to operator anant@selenite.co per PR-G2 authorization DBCP.",
  "source_pr_or_dbcp_text": "PR-G2 (bc-docs-v3 main <merge-sha-when-PR-G2-DBCP-lands>)"
}
```

DTO field semantics:

| Field | Validation |
|---|---|
| `target_user_uid` | `@IsUUID()`; must exist in the configured Cognito user pool (verified by a pre-update `getUserAttributes` call); cross-pool / unknown → 404 |
| `desired_mcf_roles` | Non-null array of strings; every entry must be in the allowlist `{mcf_author, mcf_publisher}`; empty array allowed (removes all MCF roles) |
| `reason_text` | `@MinLength(20)`, `@MaxLength(4096)`; analogous to `RejectIntakeDto.reason_text` |
| `source_pr_or_dbcp_text` | `@MinLength(10)`, `@MaxLength(512)`; free text but must cite the authorizing DBCP/PR |

### 4.2 Response (HTTP 201)

```json
{
  "grant_uid": "<uuid>",
  "target_user_uid": "8bdb9bd0-8827-4cc8-b640-2087658f1eb6",
  "target_email_snapshot": "anant@selenite.co",
  "roles_before": ["platform_admin", "schema_author", "operator", "analyst"],
  "roles_after": ["platform_admin", "schema_author", "operator", "analyst", "mcf_author"],
  "mcf_roles_added": ["mcf_author"],
  "mcf_roles_removed": [],
  "granted_at": "<iso-timestamp>",
  "granted_by_email_snapshot": "<invoker-email>"
}
```

### 4.3 Error envelope

| Status | Code | When |
|---|---|---|
| 400 | `invalid_dto` | Missing field, malformed UUID, reason too short, source too short |
| 400 | `role_not_in_allowlist` | `desired_mcf_roles` contains a role outside `{mcf_author, mcf_publisher}` |
| 403 | `requires_super_admin_role` | Invoker lacks `super_admin` OR is in tenant scope |
| 404 | `target_user_not_found` | Cognito `UserNotFoundException` (pre-call lookup or AdminUpdate response) |
| 409 | `no_op_grant` | Current MCF-subset of `custom:roles` already equals `desired_mcf_roles`; no AWS call made; no audit row emitted; response body includes current `roles_after` for client diagnosis |
| 500 | (ProblemDetail) | Unmapped AWS error (`AccessDeniedException`, `ServiceFailureException`, `InternalErrorException`) |

### 4.4 Security guards

| Layer | Check |
|---|---|
| `@PlatformOnly()` (class-level) | Token scope must be `platform` (bc-admin client only); tenant-scope token → 403 |
| `@RequireSuperAdmin()` (method-level — NEW decorator) | Invoker MUST include `super_admin` in `AuthUser.roles`. Unlike `@Roles('super_admin')`, this decorator EXPLICITLY rejects the `admin` bypass that `RolesGuard` applies globally (`roles.guard.ts:35`). Rationale: this endpoint mutates platform identity; "admin" alone is too broad |
| Defense-in-depth | Endpoint code REJECTS requests where `x-tenant-id` header is present (returns 403 `tenant_context_forbidden`) — `@PlatformOnly()` should already catch this, but explicit check guards against guard-ordering bugs |
| DTO allowlist enforcement | Service layer rejects any `desired_mcf_roles` entry outside the allowlist BEFORE the AWS call |
| Secret/token hygiene | Controller, service, AWS-wrapper, and tests MUST NOT log `Authorization` header content, JWT raw value, `custom:roles` array contents at INFO/DEBUG, or AWS response bodies. Audit row IS the persistent record; logs stay structurally minimal |

The new `@RequireSuperAdmin()` decorator design (OPEN-Q-2) is resolved in PR-G1 implementation DBCP — choice between (a) decorator + RolesGuard inspection or (b) layered custom guard. Either works; pick the simpler one at implementation time.

## 5. Hard rules (HR1–HR7)

- **HR1 — service-first invocation:** after PR-G1 merges, ALL MCF role grants flow through `POST /api/admin/mcf/role-grants`. AWS Console / CLI / SDK direct usage for MCF role attribute changes is a deviation requiring its own DBCP. CloudTrail catches the out-of-band event for after-the-fact detection.
- **HR2 — thin controller (delegation pattern LOCKED regardless of OPEN-Q-2 outcome):** controller is a delegate to a `McfRoleGrantService`; AWS SDK lives in `CognitoAdminService`; tests mock at the service boundary, never call AWS. OPEN-Q-2 governs WHERE the auth check fires (decorator + RolesGuard extension vs layered custom guard); it does NOT relax the controller's delegation pattern — either OPEN-Q-2 outcome must preserve the controller-to-service split named in this rule.
- **HR3 — audit BEFORE response:** audit row INSERT must commit before the 201 response is sent. If audit INSERT fails after Cognito update succeeded, return 500. Operator's idempotent re-invocation (D-4 + 409 `no_op_grant`) cleanly recovers: the second call detects no diff and short-circuits without producing a duplicate audit row.
- **HR4 — no tenant context:** endpoint is `@PlatformOnly()`; explicit `x-tenant-id` header rejection as defense-in-depth.
- **HR5 — no role outside the allowlist:** roles outside `{mcf_author, mcf_publisher}` → 400 `role_not_in_allowlist`. Allowlist expansion requires a DBCP update.
- **HR6 — preserve unrelated roles:** non-MCF entries in `custom:roles` are NEVER touched. Per D-4 formula.
- **HR7 — never log secrets:** controller, service, AWS-wrapper, test fixtures, and observability hooks MUST NOT log Authorization, raw JWT, `custom:roles` contents, or Cognito response bodies. Test fixtures scrub the same.

## 6. PR-G1 implementation scope (next bc-core PR, NOT this session)

### 6.1 In scope

1. **`CognitoAdminService`** in `bc-core/src/auth/cognito-admin/` (or equivalent):
   - Wraps `@aws-sdk/client-cognito-identity-provider`
   - Methods: `getUserAttributes(targetUserUid): Promise<{ email: string; customRoles: string[] }>`, `updateCustomRoles(targetUserUid, newRoles): Promise<{ requestId: string }>` — `updateCustomRoles` MUST read `result.$metadata.requestId` from the AWS SDK response and surface it so `McfRoleGrantService` can populate the `cognito_request_id` audit field (D-5). If the method returns `void` the audit row cannot be completed; PR-G1 review must reject any signature that drops `requestId`.
   - Maps AWS exceptions → typed errors: `TargetUserNotFoundError`, `CognitoServiceFailureError`, `CognitoAccessDeniedError`
   - No logging of role contents at INFO/DEBUG
2. **`McfRoleGrantService`** in `bc-core/src/registry/mcf/` (or `bc-core/src/admin/mcf-role-grants/`):
   - Constructor: `CognitoAdminService`, `CONTROL_PLANE_DB`
   - Method `grantMcfRoles(input)`:
     1. Fetch current `custom:roles` via `CognitoAdminService.getUserAttributes`
     2. Compute diff (D-4 formula; preserves non-MCF roles)
     3. If diff is empty → throw `NoOpGrantError` (controller maps to 409)
     4. Call `CognitoAdminService.updateCustomRoles` with new full role array
     5. INSERT audit row (D-5 shape) per HR3
     6. Return GrantResult shape per §4.2
3. **`McfRoleGrantController`** at `bc-core/src/registry/mcf/` (or `bc-core/src/admin/`):
   - `@PlatformOnly()`, `@Controller('admin/mcf/role-grants')`
   - `POST /` with `@RequireSuperAdmin()`
   - Maps typed errors → HTTP envelope per §4.3
4. **`@RequireSuperAdmin()` decorator** + RolesGuard extension (OPEN-Q-2)
5. **Audit table** — placement decided in PR-G1 implementation DBCP (OPEN-Q-1: mcf.role_grant_audit vs platform-wide audit table)
6. **AppModule wiring** for the new module
7. **OpenAPI tags + DTO schemas**
8. **Tests** per §7
9. **IAM policy snippet** in PR-G1 implementation DBCP — bc-core's ECS/Lambda role must carry `cognito-idp:AdminUpdateUserAttributes` permission scoped to the configured user pool (R10 mitigation)

### 6.2 Out of scope for PR-G1

- Cognito Groups → role mapping (`mcf-auth.config.ts`) — separate follow-up
- bc-admin UI for role grants — separate
- `mcf_reader` role — UserRole type addition required first
- Cross-tenant role grants — would need a separate DBCP per PR-S1
- Bulk role grants — one target per call
- Removing the global admin-bypass from `RolesGuard` — scope-limited to this endpoint
- AWS SDK integration tests (localstack/sandboxed) — follow-up; not required for v1
- First-time `super_admin` bootstrap — separate DBCP

## 7. Test obligations

Required vitest cases (NO live AWS calls; `CognitoAdminService` mocked with `vi.fn()`):

1. **requires super_admin** — token with `[mcf_author]` → 403; token with `[admin]` → 403 (no admin bypass for this endpoint); token with `[super_admin]` → 201
2. **rejects tenant context** — token with `scope='tenant'` → 403 from `ScopeGuard`
3. **rejects unknown role** — `desired_mcf_roles: ['mcf_admin']` → 400 `role_not_in_allowlist`
4. **rejects malformed target_user_uid** — non-UUID → 400 `invalid_dto`
5. **rejects short reason_text** — under 20 chars → 400 `invalid_dto`
6. **rejects short source_pr_or_dbcp_text** — under 10 chars → 400 `invalid_dto`
7. **preserves unrelated roles** — current `[platform_admin, analyst]`; desired `[mcf_author]`; final `[platform_admin, analyst, mcf_author]`
8. **no-op grant** — current MCF subset already equals desired → 409 `no_op_grant`; `CognitoAdminService.updateCustomRoles` NOT called; audit row NOT emitted
9. **happy path 201** — current `[]`; desired `[mcf_author]`; `updateCustomRoles` called with `[mcf_author]`; audit row INSERTed; response matches §4.2
10. **AWS UserNotFoundException → 404** with `code: 'target_user_not_found'`
11. **AWS AccessDeniedException → 500** + ProblemDetail body
12. **audit-row failure → 500** — mock audit INSERT throws; endpoint returns 500 (Cognito update may have succeeded; operator re-invokes idempotently)
13. **secrets not logged** — assert via test spy that no `info`/`debug` log entry contains the Authorization header value, the JWT raw value, or any `custom:roles` array content
14. **rejects `x-tenant-id` header even with platform-scope super_admin token** — platform-scope `super_admin` token + `x-tenant-id: <any value>` header present → 403 `tenant_context_forbidden` (defense-in-depth per §4.4; guards against guard-ordering bugs even when `@PlatformOnly()` should catch this first; the explicit header check is the safety net)
15. **empty desired_mcf_roles removes all MCF roles** — current `custom:roles=[platform_admin, analyst, mcf_author]`; `desired_mcf_roles=[]`; expected `CognitoAdminService.updateCustomRoles` called with `[platform_admin, analyst]`; 201 returned with `mcf_roles_removed=[mcf_author]`, `mcf_roles_added=[]`; audit row INSERTed with `roles_after=[platform_admin, analyst]` (full MCF off-boarding path — D-4 formula with `desired_mcf_roles ∩ MCF_ALLOWLIST = ∅`)

### 7.1 Deferred to follow-up

- Integration test against localstack/sandboxed Cognito pool — out of PR-G1 v1

## 8. PR-G1.5 — operator-attested first invocation

After PR-G1 merges to bc-core main, the **first** invocation of `POST /api/admin/mcf/role-grants` is operator-driven and attested:

1. Operator authors a brief one-page evidence note at `bc-docs-v3/docs/operations/cognito-role-grants/pr-g1.5-evidence-<ISO-timestamp>.md` (canonical destination — ISO timestamp uses the `YYYY-MM-DDTHH-MM-SSZ` pattern matching the `scripts/audit-output/` convention in bc-core). The `cognito-role-grants/` directory is created at PR-G1.5 execution time if it does not yet exist. Declares:
   - The target user uid + email
   - The desired MCF roles
   - The reason text and source DBCP/PR reference
   - The expected response shape
2. Operator calls the endpoint with a `super_admin` token (curl, node-e, or Bruno — whatever the operator workflow uses)
3. Captures the response (201 body + audit `grant_uid`)
4. Re-fetches a fresh Cognito token via `devhub_get_cognito_token`
5. Decodes the new token and asserts `custom:roles` now includes `mcf_author`
6. Commits the evidence: captured response + new token's role list (token value REDACTED — only the role array)

PR-G1.5 is the formal close of the PR-G2 prerequisite "operator user carries `mcf_author`."

## 9. Sequencing update

```
PR-S1     bc-docs-v3 main fa1b719      MCF service-ification DBCP                 [MERGED]
PR-C4     bc-core    main 2a7a1e5      MCF as service (controllers + McfModule)   [MERGED]
PR-E1     bc-core    SES-461193        Readiness evidence pack (Gap #1 named)     [in-flight]
THIS      bc-docs-v3 SES-5fa003        PR-G1 design DBCP (THIS document)          [in-flight]
PR-G1     bc-core    NEXT              Implement MCF role-grant service
PR-G1.5   operator   AFTER PR-G1       First invocation; mcf_author grant attested
PR-G2     bc-docs-v3 AFTER PR-G1.5     First-real service-surface M12 authz DBCP
PR-E2     bc-core    AFTER PR-G2       Execute POST /api/mcf/panel-runs; evidence
PR-A0     bc-admin   OPTIONAL parallel Read-only panel-run inspector
PR-A1     bc-admin   AFTER PR-E2       Write/action UI
```

PR-G2 prerequisites are now precisely:

1. PR-G1 merged to bc-core main
2. PR-G1.5 evidence committed showing `mcf_author` granted to operator via the new endpoint
3. Fresh Cognito token for operator carries `mcf_author` (verified)
4. PR-G2 authorization DBCP authored in bc-docs-v3
5. bc-core running locally with `ANTHROPIC_API_KEY` + `OPENAI_API_KEY` + `GOOGLE_API_KEY` loaded
6. Substrate confirmed: target intake `4d849778-3989-4caf-8a71-7d44b782d98e` still `pending`; no in-flight proposal within `DUPLICATE_PROPOSAL_WINDOW_MS`

## 10. Risk register

| ID | Risk | Mitigation |
|---|---|---|
| R1 | Bootstrap deadlock — no `super_admin` exists, endpoint unreachable | D-6 names this as separate DBCP; this DBCP does NOT authorize but acknowledges. PR-G1 implementation tests against a fixture user with `super_admin`. |
| R2 | `admin` bypass widens scope unintentionally | `@RequireSuperAdmin()` decorator EXPLICITLY rejects `admin` bypass for this endpoint (D-4 / §4.4 guard layer) |
| R3 | Audit INSERT failure → orphan Cognito grant | HR3 + 500 response on audit failure; operator's idempotent re-attempt (D-4 + 409) cleanly recovers without duplicate audit row |
| R4 | Audit table schema drift if placement changes later | OPEN-Q-1 resolved at PR-G1 implementation DBCP; placement LOCKED before code merges |
| R5 | Operator forgets the service, uses AWS Console out-of-band | HR1 names this as deviation requiring its own DBCP; CloudTrail captures the AWS event for detection |
| R6 | Cross-pool `target_user_uid` accepted | Pre-update `getUserAttributes` call validates user exists in the configured pool; 404 if not |
| R7 | Endpoint becomes backdoor for arbitrary role grants | Allowlist enforced in service layer + DBCP-encoded; allowlist expansion requires DBCP |
| R8 | Token re-issuance lag — fresh `mcf_author` not visible in cached token | PR-G1.5 §9 step 4 re-fetches token explicitly; operator-side discipline |
| R9 | Region misconfiguration → call to wrong Cognito pool | Region pinned in config + this DBCP; PR-G1 tests assert region constant matches PR-G1 IAM resource scope |
| R10 | bc-core IAM lacks `cognito-idp:AdminUpdateUserAttributes` | PR-G1 implementation DBCP includes IAM policy snippet + names the resource as a prerequisite for first successful endpoint call |
| R11 | Concurrent-grant race — `AdminUpdateUserAttributes` is a full-attribute replace on `custom:roles`; two simultaneous grants against the same `target_user_uid` last-write-wins on Cognito while leaving two non-merged audit rows. The 409 `no_op_grant` guard does NOT serialize concurrent writers; it only short-circuits when desired equals current at read time | PR-G1 v1: name the constraint in the audit-table column comment and the endpoint docstring (operator-side serialization expected — one `super_admin` operator at a time per target). PR-G1 v2 follow-up: service-side advisory lock keyed on `target_user_uid` for the duration of the read-diff-write-audit sequence (e.g., `pg_advisory_xact_lock(hashtext(target_user_uid))`) |

## 11. Standing gate state

### Pre-DBCP (bc-docs-v3 main `fa1b719`, bc-core main `2a7a1e5`)

- MCF service surface live (PR-C4) ✓
- MCF roles defined as `UserRole` literals (PR-C4) ✓
- No service path to grant MCF roles ✗
- PR-G2 hard-blocked on Cognito attribute change ✗
- Only paths to grant: AWS Console / CLI / raw MCP (REJECTED per HR1 going forward)

### Post-DBCP (this PR merged)

- Architectural lock recorded; PR-G1 implementation authorized
- PR-G2 prerequisites enumerated (§9)
- Bootstrap path named as separate scope (D-6)
- HR1–HR7 in force going forward

### Post-PR-G1 (next bc-core PR merged)

- `POST /api/admin/mcf/role-grants` live in bc-core
- Audit table populated (placement decided in PR-G1)
- ALL MCF role grants flow through service

### Post-PR-G1.5 (operator-attested first invocation)

- `mcf_author` granted to operator via service path; audit row exists
- Operator's fresh token carries `mcf_author`
- PR-G2 cleared to proceed

## 12. Open questions (resolved at PR-G1 implementation DBCP, not here)

- **OPEN-Q-1: Audit table placement.** Options: (a) new `mcf.role_grant_audit` (clean colocation with MCF substrate); (b) extend existing platform audit table if one exists; (c) emit to a generic append-only ledger. Locked at PR-G1 implementation time. Schema shape (§D-5) is locked regardless of placement.
- **OPEN-Q-2: `@RequireSuperAdmin()` design.** Decorator + RolesGuard extension vs layered custom guard. Either works; PR-G1 picks the simpler.
- **OPEN-Q-3: First-`super_admin` bootstrap DBCP.** Authored separately when needed. Not in this scope.
- **OPEN-Q-4: No-op grant semantics — LOCKED in D-5, §4.3, §7 case 8 (NOT actually open; retained here only as a cross-reference).** 409 `no_op_grant` with current state in body, no AWS call, no audit row. The alternative considered (201 with no-op audit row) was rejected — risks audit bloat from accidental re-invocations.
- **OPEN-Q-5: `mcf_reader` role addition.** Out of scope; add to allowlist when the role becomes a UserRole literal.
- **OPEN-Q-6: Integration test against localstack/sandboxed Cognito.** Out of PR-G1 v1; tracked as follow-up.
- **OPEN-Q-7: Token re-issuance UX.** Does the endpoint return guidance ("re-fetch token to see new roles")? Or is this PR-G1.5 step 4 only? Resolve at PR-G1.

## 13. Non-goals

- No bc-core code change in this DBCP (docs only)
- No AWS calls from this session
- No Cognito modification
- No role grants
- No M12 / M12.5 / M13 / M14 invocation
- No substrate mutation; no tenant DB touch
- No metric contract authored
- No supersession of DEC-7f9597 / D423 (operator stance — operator authority unchanged)
- No supersession of DEC-ebf0b4 / D268 (session discipline — PR-G1.5 still proves first invocation)
- No supersession of MCF-ERR-001 (verdict-aware intake semantics — unaffected by this DBCP)
- No supersession of PR-S1 (service-ification scope — this DBCP is a subordinate)
- No update to `mcf-auth.config.ts` (Cognito Groups projection — deferred)
- No bc-admin UI design

## 14. References

- PR-S1 (parent DBCP): `docs/implementation/metric-context-framework-service-ification-dbcp.md` (bc-docs-v3 main `fa1b719`)
- PR-C4 (bc-core implementation): bc-core main `2a7a1e5` — MCF controllers + McfModule
- Auth guard chain: `bc-core/src/auth/strategies/cognito-jwt.strategy.ts`, `bc-core/src/auth/guards/roles.guard.ts`, `bc-core/src/auth/guards/scope.guard.ts`
- MCF roles: `bc-core/src/types/enums.ts:20-21`
- Operator stance ADR: DEC-7f9597 / D423
- Session discipline ADR: DEC-ebf0b4 / D268
- MCF-ERR-001 (intake verdict-aware mutation): `bc-docs-v3/docs/errata/MCF-ERR-001.md`
- PR-E1 readiness pack (in-flight): bc-core SES-461793
