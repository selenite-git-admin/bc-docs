---
uid: platform-role-catalog-dbcp
title: Platform Role Catalog DBCP — lock the 12-role inventory + allowlist enforcement (JWT + DTO) + super_admin bootstrap path + service-first discipline generalized from MCF to all platform role grants (tenant roles + Cognito groups + unified audit table explicitly out of scope)
description: Governance DBCP authored after operator surfaced that the platform `UserRole` taxonomy at `bc-core/src/types/enums.ts:5-21` accumulated ad-hoc — 12 role literals exist with DBCP-level governance for only 2 of them (`mcf_author`, `mcf_publisher` added by PR-C4 §4.3 + PR-G1 design DBCP D-3 §I-1; PR #34 merge `d60a742`). The remaining 10 roles (`super_admin`, `admin`, `platform_admin`, `tenant_admin`, `schema_author`, `schema_reviewer`, `schema_approver`, `operator`, `analyst`, `viewer`) were added by individual PRs over time with no documented semantics, no allowlist enforcement at the JWT strategy or DTO layer, no bootstrap path for first instances, no lifecycle governance, and no service-mediated grant path. PR-G1.1 (bc-core main `f8e8042`, PR #174) shipped the role-grant SERVICE for MCF roles only via `POST /api/admin/mcf/role-grants` with allowlist `{mcf_author, mcf_publisher}`; the broader catalog gap remained. This DBCP locks the catalog and generalizes the service-first discipline locked at PR-G1 design DBCP HR1 to all platform role grants going forward. Records 10 locked decisions PR-1..PR-10 covering: (PR-1) authoritative catalog of 12 platform roles with documented semantics; (PR-2) JWT-layer allowlist enforcement at `CognitoJwtStrategy.validate()` — unknown roles dropped with structured warning; (PR-3) DTO-layer allowlist enforcement via `@IsIn(KNOWN_PLATFORM_ROLES)` for any DTO accepting role-typed input; (PR-4) `super_admin` bootstrap path — one-time AWS-side action by a named operator authorized via a SEPARATE bootstrap DBCP with attestation committed to `bc-docs-v3/docs/operations/role-bootstrap-evidence/`; (PR-5) future role additions REQUIRE a per-role-family DBCP authorizing both the type literal addition and the grant-service-allowlist expansion; (PR-6) role deprecation / rename / removal procedure (soft-deprecation; Cognito-side migration; audit historical preservation); (PR-7) service-first discipline generalized — after the implementation PR lands, ALL platform role grants must flow through `POST /api/admin/<family>/role-grants` (today only MCF; new families inherit the pattern); AWS Console / CLI / raw MCP for platform role grants becomes a documented HR1 deviation; (PR-8) `super_admin` / `admin` / `platform_admin` 3-tier disambiguation — `super_admin` is identity-mutating bypass (highest); `admin` is routine-ops bypass excluding identity mutations; `platform_admin` carries NO bypass but holds platform scope as the default for human platform operators; the `RolesGuard:35` admin bypass behavior is preserved; the new `SuperAdminGuard` (PR-G1.1) is the canonical identity-mutation gate; (PR-9) audit table architecture — keep `mcf.role_grant_audit` for v1; defer unified `audit.role_grant_audit` to a separate DBCP that ships with the second role family's grant service (premature unification rejected — first concrete second family proves the shape); (PR-10) anant@selenite.co existing role declaration documenting what the canonical operator currently carries per PR-E1 JWT decode evidence (`[platform_admin, schema_author, operator, analyst]`), enabling the catalog to be validated against a real production user. NOT EXECUTED — docs-only catalog lock. No bc-core code change. No DDL applied. No AWS calls. No Cognito modification. No role grants. No M12 / M12.5 / M13 / M14 invocation. No provider calls. No substrate mutation. No tenant DB touch. No metric contract authored. PAUSES PR-G1.5 (operator-attested first MCF role grant) until (a) this DBCP merges, (b) bc-core implementation PR for PR-2 + PR-3 JWT/DTO allowlist enforcement merges, (c) `super_admin` bootstrap DBCP merges + bootstrap executed with attestation. The `mcf_author` grant becomes the FIRST grant under the new governance regime, validating the end-to-end pattern. Explicitly out of scope (deferred to separate DBCPs): tenant-side role taxonomy (bc-portal roles), Cognito group → role projection (`mcf-auth.config.ts` from PR-S1 §4.3.2 TODO), unified `audit.role_grant_audit` substrate change, bc-core implementation PR (separate next session), super_admin bootstrap execution DBCP (separate sibling DBCP), and PR-G1.5 invocation.
status: proposed
date: 2026-05-31
project: bc-docs
domain: contracts
subdomain: catalog
focus: platform-role-catalog
supersedes:
superseded_by:
---

# Platform Role Catalog DBCP

> Sibling of PR-S1 (`docs/implementation/metric-context-framework-service-ification-dbcp.md`, merged `fa1b719`), PR-G1 design DBCP (`docs/implementation/mcf-role-grant-service-dbcp.md`, merged `d60a742`), and PR-G1.0 implementation DBCP (`docs/implementation/mcf-role-grant-service-implementation-dbcp.md`, merged `ec7053d`). Locks the platform role CATALOG itself, not the MCF role-grant service (which PR-G1.1 already shipped at bc-core `f8e8042`).
>
> Generalizes PR-G1 design DBCP §HR1 ("service-first invocation") from MCF roles only to ALL platform roles going forward.
>
> Does NOT supersede any of the above. Adds rules. Pauses PR-G1.5 until the implementation PR + bootstrap DBCP ship.

## 1. Scope

### 1.1 Question this DBCP answers

> The platform `UserRole` taxonomy at `bc-core/src/types/enums.ts:5-21` accumulated 12 role literals over time with DBCP-level governance for only 2 (`mcf_author`, `mcf_publisher` via PR-C4 §4.3 + PR-G1 design DBCP §I-1 §D-3). The remaining 10 roles were added by individual PRs with no documented semantics, no allowlist enforcement at the JWT strategy or DTO layer, no bootstrap path for first instances, no lifecycle procedure, and no service-mediated grant path. PR-G1.1 (bc-core `f8e8042`, PR #174) shipped the role-grant SERVICE for MCF roles only. The broader catalog gap remained. **What does the locked governance for the platform role catalog look like, and how does PR-G1's service-first discipline generalize to all platform roles going forward?**

### 1.2 In scope

- Authoritative catalog of the 12 existing platform `UserRole` literals with documented semantics, allowlist membership, bypass behavior, and default-user-target
- JWT-layer allowlist enforcement at `CognitoJwtStrategy.validate()` (unknown roles dropped silently with structured warning; token does NOT reject — robust to Cognito-side typos)
- DTO-layer allowlist enforcement via `@IsIn(KNOWN_PLATFORM_ROLES)` for any DTO accepting role-typed input
- `super_admin` bootstrap path — one-time AWS-side action by a named operator authorized via a SEPARATE bootstrap DBCP with attestation
- Lifecycle governance — role addition, deprecation, rename, removal procedures
- Service-first discipline generalized from MCF (PR-G1) to all platform roles
- `super_admin` / `admin` / `platform_admin` 3-tier disambiguation
- Audit table architecture decision (defer unified table; keep MCF-specific table for v1)
- anant@selenite.co existing role declaration (factual baseline)

### 1.3 Explicitly out of scope

- **Tenant-side role taxonomy** — `bc-portal` (scope=tenant) carries `tenant_admin` and presumably other tenant roles that are not enumerated. Separate DBCP.
- **Cognito group → role projection** — `mcf-auth.config.ts` from PR-S1 §4.3.2 TODO. Separate follow-up DBCP.
- **Unified `audit.role_grant_audit` substrate change** — defer until second role family ships; the first concrete second family proves the shape; premature unification rejected.
- **bc-core implementation PR** for PR-2 + PR-3 JWT/DTO allowlist enforcement — separate next session against this DBCP.
- **`super_admin` bootstrap execution DBCP** — separate sibling DBCP that authorizes the one-time AWS-side action with attestation; not authored here.
- **PR-G1.5 invocation** — paused until (a) this DBCP merges, (b) bc-core implementation PR merges, (c) bootstrap DBCP merges + executed.
- **Modifying anant@selenite.co's existing roles** — only documenting them factually.
- **AWS calls, Cognito modification, role grants, M12 / M12.5 / M13 / M14, substrate mutation, tenant DB.**

## 2. Current finding (factual baseline)

### 2.1 The 12 `UserRole` literals as of bc-core `f8e8042`

From `bc-core/src/types/enums.ts:5-21`:

```ts
export type UserRole =
  | 'super_admin'
  | 'admin'
  | 'platform_admin'
  | 'tenant_admin'
  | 'schema_author'
  | 'schema_reviewer'
  | 'schema_approver'
  | 'operator'
  | 'analyst'
  | 'viewer'
  // MCF roles introduced by PR-C4 per bc-docs-v3 PR-S1 §4.3
  | 'mcf_author'
  | 'mcf_publisher';
```

### 2.2 Governance gaps identified

| Gap | Evidence | Severity |
|---|---|---|
| **No DBCP for 10 of 12 roles** — only `mcf_author` + `mcf_publisher` have governance trail | PR-C4 §4.3 + PR-G1 §D-3 cover only MCF roles; no DBCP files reference `schema_*`, `operator`, `analyst`, `viewer`, `tenant_admin`, `platform_admin`, `admin`, or `super_admin` as authored roles | High — invisible role creep |
| **No JWT-layer allowlist** | `bc-core/src/auth/strategies/cognito-jwt.strategy.ts:85-90` parses `custom:roles` as `JSON.parse` and assigns the result verbatim to `AuthUser.roles`. No filter, no allowlist | High — typos/inventions become valid roles |
| **No DTO-layer allowlist** | No `@IsIn(KNOWN_PLATFORM_ROLES)` decorator pattern exists for DTOs accepting role-typed input. The new `GrantMcfRolesDto` (PR-G1.1) uses `@IsIn(MCF_ROLE_ALLOWLIST)` for MCF-only allowlist | Medium — MCF endpoint enforces; nothing else does |
| **Two bypass roles in RolesGuard** with undocumented distinction | `bc-core/src/auth/guards/roles.guard.ts:35` bypasses on `super_admin OR admin`. The distinction between them is undocumented anywhere | High — security-critical ambiguity |
| **`platform_admin` semantics unclear** | Carried by canonical operator (anant) per PR-E1 evidence; not a bypass role; no documented purpose | Medium — defaults work, but unclear what it grants |
| **No bootstrap path for `super_admin`** | D-6 of PR-G1 design DBCP names this as "separate DBCP" but no bootstrap DBCP exists | High — blocks PR-G1.5 if no `super_admin` exists |
| **No lifecycle procedure** | No DBCP names how a role is deprecated, renamed, or removed | Medium — accumulates dead roles |
| **No service-first for non-MCF roles** | PR-G1's `POST /api/admin/mcf/role-grants` covers MCF only. All 10 non-MCF roles require AWS Console / CLI for grants today | High — out-of-band grants for 10 role families |
| **No tenant-side role catalog** | Only `tenant_admin` listed; no enumeration of what tenant roles SHOULD exist | High but out of scope here — separate DBCP |

### 2.3 Canonical operator's current roles (anant@selenite.co)

From PR-E1 JWT decode evidence (bc-core PR #173 merged `3adacbd`):

```
sub:           8bdb9bd0-8827-4cc8-b640-2087658f1eb6
email:         anant@selenite.co
custom:roles:  ["platform_admin", "schema_author", "operator", "analyst"]
custom:tenant_id: demo-selenite
```

Notable: **No `super_admin`. No `admin`. No `mcf_author` or `mcf_publisher`.** The operator carries 4 of the 12 cataloged roles.

## 3. Locked decisions (PR-1 through PR-10)

### PR-1: Authoritative role catalog

Section 4 below is the authoritative catalog. Every platform `UserRole` literal MUST be enumerated there with: documented semantics, bypass behavior, default-user-target, allowlist family, and governance authority.

Any future addition to `bc-core/src/types/enums.ts` UserRole MUST be accompanied by an amendment to this catalog OR a sibling role-family DBCP per PR-5.

### PR-2: JWT-layer allowlist enforcement

`CognitoJwtStrategy.validate()` MUST filter `custom:roles` against the catalog at runtime. Unknown roles are:
- DROPPED from `AuthUser.roles` (NOT rejected at JWT level — robust to Cognito-side data drift)
- Logged via the structured logger with `severity: warning`, `event: 'unknown_role_in_jwt'`, `target_user_uid`, `unknown_role_values` (array of unknown role strings observed in this JWT), `known_role_count` (count of catalog-known roles that survived the filter)
- NEVER logged with the role VALUE in `info` or `debug` (HR7 secret-logging hygiene; the warning entry contains the unknown value, which is operationally necessary for diagnosis)

The implementation lives in a NEW constant `KNOWN_PLATFORM_ROLES: ReadonlySet<UserRole>` exported from `src/types/enums.ts` alongside the literal type. The strategy imports the set and filters.

### PR-3: DTO-layer allowlist enforcement

Every DTO accepting role-typed input from a request body MUST use `@IsIn(KNOWN_PLATFORM_ROLES_ARRAY, { each: true, message: 'role_not_in_catalog' })` for the role field. The MCF role-grant DTO (`GrantMcfRolesDto.desired_mcf_roles`) already does this for the MCF allowlist; this rule generalizes the pattern.

Where a sub-allowlist is needed (e.g., the MCF grant service accepts only `{mcf_author, mcf_publisher}`, NOT the full catalog), the sub-allowlist must be a SUBSET of `KNOWN_PLATFORM_ROLES_ARRAY` validated at module load (assertion). PR-G1.1's existing `MCF_ROLE_ALLOWLIST` satisfies this.

### PR-4: `super_admin` bootstrap path

If no `super_admin` exists in the Cognito user pool, no one can call any platform role-grant endpoint. The first `super_admin` MUST be provisioned via a SEPARATE bootstrap DBCP that:

- Is authored as a one-shot governance document (~50-150 lines)
- Names the AWS-side action (Cognito Console OR AWS CLI `admin-update-user-attributes`)
- Names the target user (`sub` + `email`)
- Names the authorizing operator (and confirms cross-check on attestation)
- Includes an explicit attestation block signed by the operator
- Commits the executed evidence to `bc-docs-v3/docs/operations/role-bootstrap-evidence/<YYYY-MM-DD>-super-admin-bootstrap.md` after execution
- Records the AWS CloudTrail event id for cross-correlation
- Is reviewed before merge but executed only after merge

This DBCP does NOT authorize the bootstrap. The bootstrap DBCP is sibling work.

### PR-5: Future role additions require DBCP

Adding a new platform `UserRole` literal to `bc-core/src/types/enums.ts` MUST be accompanied by a role-family DBCP that:

1. Names the family (e.g., "MCF role family" = `{mcf_author, mcf_publisher}`)
2. Documents semantics for each role
3. Identifies the endpoint(s) the role gates
4. Specifies the grant-service allowlist additions
5. Specifies the audit-table additions (or reuses existing table)
6. Specifies the bootstrap path (if grants of this role need a non-`super_admin` operator)
7. Updates this catalog DBCP by amendment OR explicitly cross-references this catalog as the parent

PR-C4 §4.3 + PR-G1 design DBCP §D-3 satisfy this for the MCF role family retroactively. Future families inherit the pattern from PR-G1.0 §I-1 + §I-3.

### PR-6: Role lifecycle — deprecation, rename, removal

**Deprecation** (soft):
- Documented in this catalog under the role's entry: `status: deprecated`, `deprecated_at: <date>`, `replaced_by: <new role name or NONE>`
- Role remains in `UserRole` literal type AND in `KNOWN_PLATFORM_ROLES`
- Role is REMOVED from any DTO allowlist (cannot be granted via service)
- Existing Cognito users with the role continue to function
- DBCP required to deprecate

**Rename**:
- Requires DBCP + migration plan
- Migration: AWS-side bulk Cognito update to swap role names; CognitoJwtStrategy ALLOWLIST temporarily includes BOTH names; audit table preserves historical names verbatim
- Both names remain in catalog with cross-reference; rollback is the inverse

**Removal**:
- Requires DBCP + soft-deprecation period of at least one calibration arc cycle
- Cognito audit confirms zero remaining users with the role before removal
- UserRole literal removed from `enums.ts`
- `KNOWN_PLATFORM_ROLES` updated
- Audit table preserves historical role values verbatim (never delete audit rows)

### PR-7: Service-first discipline generalized to all platform role grants

After the implementation PR for PR-2 + PR-3 lands at bc-core, ALL platform role grants MUST flow through a BareCount service endpoint matching the PR-G1 pattern:

- Path: `POST /api/admin/<family>/role-grants`
- Class-level `@PlatformOnly()`
- Method-level `@RequireSuperAdmin()` (for identity-mutating grants — every platform role grant qualifies)
- Allowlist enforcement in DTO via `@IsIn(<family>_ALLOWLIST)`
- Preservation of non-family roles via the D-4 formula
- Immutable audit row in the family-specific or unified audit table
- Token re-issuance `note` field

AWS Console / CLI / raw AWS MCP for platform role grants is a documented HR1 deviation requiring its own DBCP after this catalog merges.

The MCF family (`mcf.role_grant_audit` + `POST /api/admin/mcf/role-grants`) is the V1 implementation. Future role families either reuse `mcf.role_grant_audit` (if their semantics fit) or author a new family-specific table. The latter option **surfaces** — but does NOT unilaterally obligate — the PR-9 unified-table discussion; whether to unify across families or keep family-specific tables is the discretion of the second family's DBCP author, with PR-9's "defer unification" recommendation as the default.

### PR-8: 3-tier disambiguation of super_admin / admin / platform_admin

| Role | Bypass scope | Use case | Carried by |
|---|---|---|---|
| **`super_admin`** | RolesGuard + ScopeGuard + `SuperAdminGuard` (the PR-G1.1 strict guard); bypasses ALL gates including identity mutations | Emergency operations; identity changes (role grants); bootstrap operations | RARE — emergency / bootstrap operators only |
| **`admin`** | RolesGuard ONLY (per `roles.guard.ts:35`). Does NOT bypass `ScopeGuard` (per `scope.guard.ts:41-49` — ScopeGuard's bypass check at line 41 fires on `super_admin` only, NOT `admin`; the scope match at lines 43-49 reads the JWT audience-derived scope, not roles, so `admin` in `user.roles` cannot satisfy a scope mismatch). Does NOT bypass `SuperAdminGuard` (`admin` users cannot call the MCF role-grant endpoint per PR-G1.1 §I-3). | Routine cross-tenant operations that don't mutate platform identity (e.g., bulk metric runs, schema approvals across tenants). Strictly NOT for role grants. | Limited set of ops staff |
| **`platform_admin`** | NO bypass. Carries platform scope (`scope=platform`) BUT must explicitly hold the role required by each endpoint's `@Roles()` decorator. | Default for human platform operators. Day-to-day platform work. | Human operators (anant carries this) |

**Locked behavior:** The PR-G1.1 `SuperAdminGuard` is the canonical identity-mutation gate going forward. The global `RolesGuard:35` bypass on `super_admin OR admin` is PRESERVED for non-identity endpoints (compatibility), but every new identity-mutation endpoint MUST use `@RequireSuperAdmin()` (NOT `@Roles('super_admin')`) to exclude `admin` bypass.

### PR-9: Audit table architecture — defer unification

- Keep `mcf.role_grant_audit` as the v1 audit destination for MCF role grants (PR-G1.1 already shipped)
- Defer authoring a unified `audit.role_grant_audit` substrate until the SECOND role family's grant service ships
- Rationale: premature unification optimizes against a shape we don't yet know; the second family's concrete needs reveal what fields the unified table actually needs
- The unification DBCP, when authored, will name the migration from `mcf.role_grant_audit` (and any other family-specific tables) to the unified table; until then, MCF-specific is correct

### PR-10: anant@selenite.co existing role declaration

Factual baseline (from PR-E1 JWT decode):
- `sub`: `8bdb9bd0-8827-4cc8-b640-2087658f1eb6`
- `email`: `anant@selenite.co`
- `custom:roles`: `["platform_admin", "schema_author", "operator", "analyst"]`
- `custom:tenant_id`: `demo-selenite`

This declaration is documentation only; this DBCP does NOT mutate Cognito or change anant's roles. The declaration enables a reviewer to validate the catalog against a real production user and surfaces what the canonical operator can and cannot do today (cannot call any `@RequireSuperAdmin()` endpoint; cannot call MCF role-grant endpoint because no `super_admin`; can call `@Roles('platform_admin' | 'schema_author' | 'operator' | 'analyst')` endpoints).

## 4. Authoritative role catalog (12 entries)

Format: each row documents one role.

| # | Role | Bypass scope | Documented semantic | Default-user-target | Allowlist family | Governance authority |
|---|---|---|---|---|---|---|
| 1 | `super_admin` | RolesGuard + ScopeGuard + SuperAdminGuard (PR-G1.1) | Identity mutations + emergency operations. Bypasses all gates. Required for: role grants, bootstrap. | RARE — emergency operators only | `KNOWN_PLATFORM_ROLES` (bypass tier 1) | THIS DBCP (PR-1, PR-8) |
| 2 | `admin` | RolesGuard only (`roles.guard.ts:35`) | Routine cross-tenant ops that don't mutate identity. Excluded from identity mutations by `SuperAdminGuard`. | Limited ops staff | `KNOWN_PLATFORM_ROLES` (bypass tier 2) | THIS DBCP (PR-1, PR-8) |
| 3 | `platform_admin` | No bypass; carries platform scope | Day-to-day platform admin work; default for human platform operators | Human platform operators (anant) | `KNOWN_PLATFORM_ROLES` (scope) | THIS DBCP (PR-1, PR-8) |
| 4 | `tenant_admin` | No bypass; carries tenant scope | Tenant-side administration — single-tenant user + config management | Tenant administrators | `KNOWN_PLATFORM_ROLES` (cross-scope reference) | THIS DBCP (PR-1) — tenant-side cataloging is separate scope |
| 5 | `schema_author` | No bypass | Authors source / admission / observation / canonical contract definitions | Schema authors | `KNOWN_PLATFORM_ROLES` (work) | THIS DBCP (PR-1) |
| 6 | `schema_reviewer` | No bypass | Reviews schema PRs before approval; can comment / request changes but not approve | Schema reviewers | `KNOWN_PLATFORM_ROLES` (work) | THIS DBCP (PR-1) |
| 7 | `schema_approver` | No bypass | Final approver for schema lifecycle changes; can mark `decided` | Schema approvers | `KNOWN_PLATFORM_ROLES` (work) | THIS DBCP (PR-1) |
| 8 | `operator` | No bypass | Day-to-day operations — kicks off pipelines, monitors runs, inspects evidence | Platform + tenant operators (anant) | `KNOWN_PLATFORM_ROLES` (work) | THIS DBCP (PR-1) |
| 9 | `analyst` | No bypass | Read-only access to evidence + dashboards | Analysts (anant) | `KNOWN_PLATFORM_ROLES` (read) | THIS DBCP (PR-1) |
| 10 | `viewer` | No bypass | Read-only access to UI surfaces only | Viewers | `KNOWN_PLATFORM_ROLES` (read) | THIS DBCP (PR-1) |
| 11 | `mcf_author` | No bypass | Authors MCF metric proposals via M11 intake + M12 panel (per PR-S1 §4.3, PR-G1 D-3) | MCF authors | `MCF_ROLE_ALLOWLIST` (grant-service-mediated) | PR-S1 §4.3 + PR-G1 §D-3 + THIS DBCP (PR-1) |
| 12 | `mcf_publisher` | No bypass | Publishes MCF drafts via M12.5 materialization + M13 PE-MC (per PR-S1 §4.3, PR-G1 D-3) | MCF publishers | `MCF_ROLE_ALLOWLIST` (grant-service-mediated) | PR-S1 §4.3 + PR-G1 §D-3 + THIS DBCP (PR-1) |

`KNOWN_PLATFORM_ROLES` is the union of all 12 entries. `MCF_ROLE_ALLOWLIST` is a subset of size 2.

## 5. Allowlist enforcement design (PR-2 + PR-3 in detail)

### 5.1 JWT-layer (PR-2)

Add to `bc-core/src/types/enums.ts`:

```ts
export const KNOWN_PLATFORM_ROLES: ReadonlySet<UserRole> = new Set([
  'super_admin', 'admin', 'platform_admin', 'tenant_admin',
  'schema_author', 'schema_reviewer', 'schema_approver',
  'operator', 'analyst', 'viewer',
  'mcf_author', 'mcf_publisher',
]);

export const KNOWN_PLATFORM_ROLES_ARRAY: readonly UserRole[] = [
  ...KNOWN_PLATFORM_ROLES,
];
```

Modify `CognitoJwtStrategy.validate()` to filter:

```ts
const rawRoles: string[] = JSON.parse(payload['custom:roles'] || '[]');
const knownRoles: UserRole[] = [];
const unknownRoles: string[] = [];
for (const r of rawRoles) {
  if (KNOWN_PLATFORM_ROLES.has(r as UserRole)) {
    knownRoles.push(r as UserRole);
  } else {
    unknownRoles.push(r);
  }
}
if (unknownRoles.length > 0) {
  this.logger.warn({
    event: 'unknown_role_in_jwt',
    target_user_uid: payload.sub,
    unknown_role_values: unknownRoles,
    known_role_count: knownRoles.length,
  });
}
return { ...authUser, roles: knownRoles };
```

The token is NOT rejected. The user receives a degraded `roles` list. This is robust to Cognito-side typos and rolls deprecated roles out gracefully.

### 5.2 DTO-layer (PR-3)

For any DTO accepting role-typed input:

```ts
@ApiProperty({ type: [String], enum: KNOWN_PLATFORM_ROLES_ARRAY })
@IsArray()
@IsString({ each: true })
@IsIn(KNOWN_PLATFORM_ROLES_ARRAY as readonly string[], {
  each: true,
  message: 'role_not_in_catalog',
})
roles!: UserRole[];
```

Sub-allowlists (like `MCF_ROLE_ALLOWLIST` in `GrantMcfRolesDto.desired_mcf_roles`) MUST validate at module load:

```ts
// Module-load-time assertion: every MCF role is also a known platform role.
for (const r of MCF_ROLE_ALLOWLIST) {
  if (!KNOWN_PLATFORM_ROLES.has(r as UserRole)) {
    throw new Error(`MCF_ROLE_ALLOWLIST entry '${r}' is not in KNOWN_PLATFORM_ROLES catalog`);
  }
}
```

Where to put the assertion: a new test file `src/types/role-catalog.spec.ts` that runs the assertion at vitest time. This guarantees CI catches any drift between sub-allowlists and the catalog.

## 6. Bootstrap path (PR-4 in detail)

The bootstrap DBCP is authored as a separate file in this same `docs/implementation/` directory when needed. Suggested name: `super-admin-bootstrap-dbcp.md`.

Required sections:
1. Authority + subordination to this catalog DBCP
2. Target identification (sub + email)
3. Operator attestation block (signed by an operator authorized for one-time AWS-side actions)
4. Pre-bootstrap verification (the user does NOT carry `super_admin` today; confirmed via CognitoJwtStrategy decoded token or AWS Cognito Console read)
5. AWS-side action (Cognito Console OR AWS CLI `aws cognito-idp admin-update-user-attributes ... custom:roles=["...","super_admin"]`)
6. Post-bootstrap verification (re-fetch token; assert `super_admin` present)
7. Evidence commit to `bc-docs-v3/docs/operations/role-bootstrap-evidence/<YYYY-MM-DD>-super-admin-bootstrap.md`
8. AWS CloudTrail event id for cross-correlation
9. Rollback path (the inverse AWS action; reasonable only mid-bootstrap-attempt)

This catalog DBCP does NOT authorize the bootstrap. The bootstrap DBCP, when authored, references this DBCP as its parent.

## 7. Service-first discipline generalized (PR-7 in detail)

**PR-G1 design DBCP §HR1 today reads:** "after PR-G1 merges, ALL MCF role grants flow through `POST /api/admin/mcf/role-grants`."

**This DBCP generalizes:** after the bc-core implementation PR for PR-2 + PR-3 lands, ALL platform role grants MUST flow through a BareCount service endpoint per the PR-G1 pattern. New role families inherit the same template:

- Endpoint path: `POST /api/admin/<family>/role-grants`
- DTO: `Grant<Family>RolesDto` with `target_user_uid`, `desired_<family>_roles`, `reason_text >= 20`, `source_pr_or_dbcp_text >= 10`
- Service: `<Family>RoleGrantService` with the 10-step pattern from PR-G1.0 §6
- Guard: `@PlatformOnly()` + `@RequireSuperAdmin()`
- Audit: row inserted into family-specific table (or unified table per PR-9)
- Response: 201 success with `note` field (token re-issuance text)
- Errors: 404 `target_user_not_found`, 409 `no_op_grant` + current state, 500 ProblemDetail for AWS failures
- Concurrency: `pg_advisory_xact_lock(hashtext(target_user_uid))` at transaction start

The first family to ship under this generalization is MCF (already live at bc-core `f8e8042`). Future families author a sibling implementation DBCP that points back to this catalog DBCP.

## 8. Hard rules (HR1–HR8)

- **HR1 — service-first invocation for platform role grants:** after bc-core PR-2+PR-3 implementation lands, all platform role grants flow through `POST /api/admin/<family>/role-grants`. AWS Console / CLI / raw MCP becomes a documented HR1 deviation requiring its own DBCP. This generalizes PR-G1 design DBCP §HR1 from MCF to all roles.
- **HR2 — thin controller, allowlist-bounded service:** every role-grant controller is a thin delegate to a service that enforces the family-specific allowlist via the D-4 preservation formula. Allowlist values are constants in code AND in this DBCP.
- **HR3 — audit-before-response:** audit row INSERT commits before the 201 response is sent. Already locked at PR-G1 design DBCP §HR3.
- **HR4 — no tenant DB:** role grant endpoints are platform-only. Already locked at PR-G1 design DBCP §HR4.
- **HR5 — no role outside the catalog:** unknown roles dropped at JWT layer (PR-2); allowlist-enforced at DTO layer (PR-3); sub-allowlists validated at module load.
- **HR6 — preserve unrelated roles:** every grant preserves non-family roles via the D-4 formula. Already locked at PR-G1 design DBCP §HR6.
- **HR7 — never log secrets (with one narrow amendment to PR-G1 §HR7):** controller, service, AWS-wrapper, and tests MUST NOT log Authorization, raw JWT, `custom:roles` known-role values (at any log level), or AWS response bodies. PR-G1 design DBCP §HR7 is the parent rule and otherwise stands unchanged. **Narrow amendment from this DBCP (amendment v2 explicit):** the PR-2 JWT-layer warning log MAY include the UNKNOWN role string(s) at `severity: warning` ONLY (NOT at `info`/`debug`) because the unknown value is operationally necessary for diagnosing Cognito-side data drift. Known role values, JWT raw, and Authorization remain prohibited at all log levels. This is a narrowly scoped relaxation of PR-G1 §HR7, not a re-state of it.
- **HR8 — no role identifier reuse after removal:** once a role is removed (per PR-6), its identifier MUST NOT be re-added with different semantics. New roles get new identifiers. Audit historical rows continue to carry the old identifier verbatim.

## 9. Implementation scope (next bc-core PR — NOT in this session)

Next bc-core PR (post-merge of this DBCP):

1. **`src/types/enums.ts`** — add `KNOWN_PLATFORM_ROLES` Set + `KNOWN_PLATFORM_ROLES_ARRAY` const
2. **`src/auth/strategies/cognito-jwt.strategy.ts`** — filter `custom:roles` against the Set; log warning for unknown roles. **Implementation note (added by amendment v2):** the strategy currently has NO `Logger` field. PR-CAT-1 MUST add `private readonly logger = new Logger(CognitoJwtStrategy.name)` (NestJS built-in `Logger` from `@nestjs/common`; no DI change needed) before the first `this.logger.warn(...)` call; otherwise the warn call throws `TypeError: Cannot read properties of undefined (reading 'warn')` at runtime on the first unknown-role JWT.
3. **`src/registry/mcf/dto/mcf-dtos.ts`** — add module-load assertion that `MCF_ROLE_ALLOWLIST ⊆ KNOWN_PLATFORM_ROLES`
4. **`src/types/role-catalog.spec.ts`** (NEW) — vitest assertion that the catalog has exactly the documented 12 roles + the assertion fires for sub-allowlists
5. **Documentation comment update** in `enums.ts` referencing this DBCP
6. Tests:
   - JWT strategy filters unknown roles (logged warning, no crash)
   - JWT strategy accepts all known roles
   - Module-load assertion passes for `MCF_ROLE_ALLOWLIST`
   - The catalog test enumerates exactly the 12 expected role literals
7. ~150-200 lines total. Bounded scope.

After that PR merges, the bootstrap DBCP can be authored.

After bootstrap executes, PR-G1.5 (operator-attested first MCF role grant) can proceed.

## 10. Sequencing update

```
PR-S1     bc-docs-v3 fa1b719          MCF service-ification DBCP                [MERGED]
PR-C4     bc-core    2a7a1e5          MCF controllers + McfModule               [MERGED]
PR-E1     bc-core    3adacbd          PR-E1 readiness evidence                  [MERGED]
PR-G1     bc-docs-v3 d60a742          MCF role-grant design DBCP                [MERGED]
PR-G1.0   bc-docs-v3 ec7053d          MCF role-grant impl DBCP                  [MERGED]
PR-G1.1   bc-core    f8e8042          MCF role-grant service live               [MERGED]
THIS      bc-docs-v3                  Platform role catalog DBCP                [IN-FLIGHT]
PR-CAT-1  bc-core    NEXT             KNOWN_PLATFORM_ROLES + JWT filter + DTO allowlist + tests
PR-BS-1   bc-docs-v3 AFTER PR-CAT-1   super_admin bootstrap DBCP (sibling)
PR-BS-X   operator   AFTER PR-BS-1    Execute bootstrap; commit evidence
PR-G1.5   operator   AFTER PR-BS-X    First MCF role grant via new service (mcf_author for anant)
PR-G2     bc-docs-v3 AFTER PR-G1.5    First-real service-surface M12 authz DBCP
PR-E2     bc-core    AFTER PR-G2      Execute POST /api/mcf/panel-runs; evidence
PR-A0     bc-admin   OPTIONAL ||      Read-only panel-run inspector
PR-A1     bc-admin   AFTER PR-E2      Write/action UI
```

PR-G1.5's prerequisites are now (was 6 in PR-G1 design DBCP §9; PR-G1.0 §R12 added bc-infra IAM as a 7th; this DBCP adds 2 more — THIS DBCP merged + PR-CAT-1 merged — for a total of **9**):

1. PR-G1.1 merged ✓
2. **THIS DBCP merged** (NEW)
3. **bc-core PR-CAT-1 merged** (NEW)
4. **super_admin bootstrap DBCP merged + bootstrap executed with evidence** (NEW)
5. Fresh Cognito token for invoking operator carries `super_admin` AND for target user carries the operator's target roles
6. PR-G2 authorization DBCP authored
7. bc-core running with vendor API keys
8. Substrate confirmed pending for target intake (was prerequisite 6 in old numbering)
9. **bc-infra IAM policy PR** (carried forward from PR-G1.0 §R12 — load-bearing prerequisite, not new in this DBCP) attaching `cognito-idp:AdminUpdateUserAttributes` + `cognito-idp:AdminGetUser` scoped to `arn:aws:cognito-idp:ap-south-1:546549546538:userpool/ap-south-1_bM5xehxIx` has merged and evidence committed. Required for AWS-dev PR-G1.5 invocation; local-dev unblocked via developer credentials per CLAUDE.md `barecount` AWS profile. Amendment v2 adds this item explicitly to prevent operators following §10 from missing the IAM prerequisite when executing PR-G1.5 against AWS-dev.

PR-CAT-1 + bootstrap DBCP add 2-3 days of additional work before PR-G1.5 can fire. This is the cost of closing the catalog gap.

## 11. Risk register

| ID | Risk | Mitigation |
|---|---|---|
| R1 | JWT filter rejects valid roles after Cognito-side data drift | Drop-with-warn approach (PR-2); token is NOT rejected; user gets degraded role list; structured warning logged for ops |
| R2 | DTO allowlist breaks existing endpoints that use roles | PR-3 applies only to DTOs that ACCEPT role-typed input; existing endpoints reading `user.roles` from JWT continue unchanged |
| R3 | Implementation PR is larger than 200 lines and creeps | Scope is bounded by §9; any creep triggers amendment to this DBCP, not silent expansion |
| R4 | `admin` role's broad bypass causes accidental privilege escalation | PR-8 documents and BOUNDS the `admin` bypass scope; new identity-mutation endpoints use `@RequireSuperAdmin()` not `@Roles('admin')`; existing `admin` users are NOT auto-revoked |
| R5 | `platform_admin` semantics confused with `admin` | PR-8 explicitly: `platform_admin` carries NO bypass; the distinction is the bypass behavior. Documentation in catalog row 3 makes this canonical. |
| R6 | super_admin bootstrap blocked indefinitely | PR-4 names the bootstrap-DBCP path; without it, no PR-G1.5; surfacing this gap is half the fix |
| R7 | New role families bypass the catalog (e.g., adding `xyz_author` without amending catalog) | PR-5 mandates DBCP for additions; the role-catalog.spec.ts test catches drift between catalog and enums.ts |
| R8 | Tenant role catalog gap remains | Out of scope here; named as deferred follow-up; visible in §1.3 |
| R9 | Audit-table unification deferred indefinitely | PR-9 names the trigger: second role family ships → unified table DBCP authored |
| R10 | Role rename / removal procedures untested | PR-6 documents the process; first real rename / removal will validate; until then, theoretical |
| R11 | Lifecycle policy added but not enforced in CI | role-catalog.spec.ts enforces catalog↔enums.ts consistency; deprecation/rename/removal is operator-driven discipline + DBCP-mandated |
| R12 | bc-infra dependency for PR-G1.5 (carried from PR-G1.0 R12) | Still required; unchanged by this DBCP |

## 12. Standing gate state

### Pre-DBCP (bc-docs-v3 main `ec7053d`, bc-core main `f8e8042`)

- 12 platform `UserRole` literals exist; 2 governed, 10 ungoverned ✗
- No JWT-layer allowlist ✗
- No DTO-layer allowlist generalization (MCF-only) ✗
- No bootstrap path documented (D-6 named separate-DBCP-territory but not authored) ✗
- No lifecycle procedure ✗
- No tier disambiguation for super_admin / admin / platform_admin ✗
- MCF role-grant service live (PR-G1.1) ✓
- `mcf.role_grant_audit` table live, empty ✓

### Post-DBCP (this PR merged)

- Authoritative catalog locked
- PR-2 + PR-3 JWT/DTO allowlist enforcement authorized (implementation in next bc-core PR)
- super_admin bootstrap path named (separate sibling DBCP authorized)
- Lifecycle procedure documented
- 3-tier disambiguation locked
- Service-first discipline generalized from MCF to all platform roles
- PR-G1.5 prerequisites expanded to 8 items

### Post-PR-CAT-1 (next bc-core PR merged)

- `KNOWN_PLATFORM_ROLES` Set lives in `enums.ts`
- `CognitoJwtStrategy.validate()` filters unknown roles
- DTO allowlist validated at module load for sub-allowlists
- role-catalog.spec.ts CI gate live

### Post-PR-BS-1 + bootstrap execution

- First `super_admin` exists in the Cognito user pool
- Evidence committed
- PR-G1.5 unblocked

## 13. Remaining open questions

- **OPEN-Q-CAT-1** — **PR-1 LOCKS `tenant_admin` IN the platform catalog as of this DBCP (Section 4 row 4).** The open question is only whether a future tenant-role DBCP will add a separate tenant-side semantic layer ALONGSIDE this platform-catalog cross-scope reference (it would not REMOVE the platform-side entry; the platform catalog needs the reference for cross-scope auth discussions). Recommend: KEEP the platform-catalog entry; the future tenant DBCP (when authored) authoritatively defines tenant-side semantics independently. PR-G1.5 / PR-CAT-1 do not depend on resolution.
- **OPEN-Q-CAT-2** — Should `admin` be deprecated? Recommend: KEEP for v1 with PR-8 clarification; revisit after PR-CAT-1 ships and the actual usage of `admin` in production becomes visible.
- **OPEN-Q-CAT-3** — Should `platform_admin` be the ONLY admin-scope role going forward (with new roles like `mcf_publisher` being granted on top)? Recommend: defer; the role catalog is large enough already and re-architecture is a separate concern.
- **OPEN-Q-CAT-4** — Cognito Groups → role projection (`mcf-auth.config.ts` from PR-S1 §4.3.2 TODO). Recommend: defer to a separate "Identity & Access" DBCP that includes tenant roles + Cognito groups + unified audit. PR-CAT-1 + bootstrap + PR-G1.5 do not need Cognito groups to function.
- **OPEN-Q-CAT-5** — How is the catalog rendered for human consumption (e.g., bc-admin user-management UI)? Recommend: not this DBCP's concern; bc-admin work eventually exposes the catalog read-only.

## 14. Non-goals

- No bc-core code change in this DBCP (docs only)
- No DDL applied; no substrate mutation
- No AWS calls; no Cognito modification; no role grants
- No M12 / M12.5 / M13 / M14 invocation
- No metric contract authored
- No tenant DB touch
- No tenant-side role catalog (separate DBCP)
- No Cognito group integration (`mcf-auth.config.ts` deferred)
- No unified audit table substrate change (PR-9 defers)
- No bc-core implementation PR (separate next session)
- No super_admin bootstrap execution (separate sibling DBCP)
- No PR-G1.5 invocation
- No mutation of anant@selenite.co's existing roles
- No bc-admin UI work
- No bc-infra IAM change
- No supersession of PR-S1, PR-G1 design DBCP, PR-G1.0 impl DBCP, PR-C4, MCF-ERR-001, DEC-7f9597/D423, or DEC-ebf0b4/D268

## 15. References

- PR-S1 (MCF service-ification DBCP): `docs/implementation/metric-context-framework-service-ification-dbcp.md` (merged `fa1b719`, PR #33). §4.3 introduced mcf_author + mcf_publisher.
- PR-G1 design DBCP (MCF role-grant service): `docs/implementation/mcf-role-grant-service-dbcp.md` (merged `d60a742`, PR #34). §D-3 locked MCF role allowlist; §D-6 named super_admin bootstrap as separate-DBCP-territory.
- PR-G1.0 implementation DBCP (MCF role-grant impl): `docs/implementation/mcf-role-grant-service-implementation-dbcp.md` (merged `ec7053d`, PR #35).
- PR-G1.1 (bc-core MCF role-grant service): bc-core merge `f8e8042` (PR #174). Live endpoint at `POST /api/admin/mcf/role-grants`.
- PR-E1 (bc-core readiness evidence): bc-core merge `3adacbd` (PR #173). JWT decode evidence shows anant's roles.
- PR-C4 (bc-core MCF as service): bc-core merge `2a7a1e5` (PR #172). §4.3 named mcf_author / mcf_publisher.
- Auth chain: `bc-core/src/auth/strategies/cognito-jwt.strategy.ts`, `bc-core/src/auth/guards/roles.guard.ts:35`, `bc-core/src/auth/guards/scope.guard.ts`, `bc-core/src/auth/guards/super-admin.guard.ts` (NEW in PR-G1.1).
- UserRole literal: `bc-core/src/types/enums.ts:5-21`.
- MCF audit table: `bc-core/src/database/schema/mcf/role-grant-audit.ts` + `bc-core/docker/redesign/14-mcf-role-grant-audit.sql`. Live in `bc_platform_dev`; row_count=0 as of `f8e8042`.
- Operator stance ADR: DEC-7f9597 / D423.
- Session discipline ADR: DEC-ebf0b4 / D268.
- Database Rules: CLAUDE.md §Database Rules (D162).
- Database Change Protocol: CLAUDE.md §Database Change Protocol.
- Cognito user pool: `ap-south-1_bM5xehxIx` (AWS account `546549546538`, region `ap-south-1`, profile `barecount`).
