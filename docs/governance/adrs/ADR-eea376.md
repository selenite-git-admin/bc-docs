---
uid: DEC-eea376
title: "Platform scope follows the user: admin-client tokens need the bc-platform Cognito group; explicit roles on every platform write; operator-only registry-shape confirm"
description: "Amends DEC-3a6f74 Current State: platform scope is no longer granted by the admin app client alone; it also requires membership of the Cognito group named by COGNITO_PLATFORM_GROUP (bc-platform)."
status: decided
date: 2026-09-29T05:29:52.189Z
project: bc-core
domain: auth
subdomain: auth/cognito-pool
focus: platform-scope-admission
amends: DEC-3a6f74
---

# Platform scope follows the user: admin-client tokens need the bc-platform Cognito group; explicit roles on every platform write; operator-only registry-shape confirm

## Context

DEC-3a6f74 (keep one bc-core service, separate platform and tenant with guard decorators) records under Current State that platform scope is detected from the JWT `aud` claim: a token issued to the admin app client (bc-admin-portal) is platform scope, and a token issued to the portal client (bc-core-api) is tenant scope. The code comment in `cognito-jwt.strategy.ts` cited this as "D065"; no recorded decision carries that code, and the rule traces to DEC-3a6f74 (the earlier DEC-58bf7f, a role-claim mechanism, was superseded and never adopted).

On 2026-09-28 (TSK-29ce9c) this was found to be a pre-production security flaw: the admin client allows public password and SRP sign-in, so any user in the pool could sign in through bc-admin and receive a platform-scope token. The first estimate (619 routes, 475 platform scoped, 21 without a scope) was replaced by the metadata inventory in the design review: 620 routes, 476 platform scoped, 18 without a scope (two of them public). The fix added explicit roles to 117 platform writes that had none. The pool also allowed self sign-up, and neither app client restricted which attributes a user could write, so custom:roles and custom:tenant_id were user-mutable.

## Decision

1. **Platform scope follows the user, not the client.** bc-core accepts an admin-client token only if its `cognito:groups` claim is an array that contains the group named by `COGNITO_PLATFORM_GROUP` (bc-platform on pool ap-south-1_bM5xehxIx); otherwise the request gets 401. Portal-client tokens keep tenant scope, unchanged. bc-core refuses to start if the issuer, either client ID or the platform group is not configured; the old fallback pool and client IDs are removed from code.
2. **Group membership is an operator act.** bc-platform members are anant, bc-dbadmin and bcauditor (bcauditor keeps its viewer role and stays read-only), plus the DevHub service login bc-ai-service. Adding or removing a member needs a recorded operator grant.
3. **The pool itself is closed.** Self sign-up is off (AllowAdminCreateUserOnly). Both app clients may write only email and custom:display_name, and read only email, email_verified, custom:roles, custom:tenant_id and custom:display_name; a user cannot write their own roles or tenant.
4. **Every route declares its scope and every platform write declares its roles.** Each route is @PlatformOnly, @TenantScoped, @Public, or on a pinned @AnyScope list (GET auth/me and the four t/test-bench POSTs). Every platform write carries @Roles or a route guard. The ScopeGuard and RolesGuard treat missing metadata as "allow", so a missing declaration is a build failure, not an open route: the architecture test `src/__architecture__/route-scope-roles.metadata.spec.ts` reads the metadata the way the guards do, has zero exceptions and is proven to go red.
5. **Only the operator role may confirm a high-risk registry-shape certification** (operator ruling, grant 2026-09-29T02-42-13-699Z-98769398). The route is @Roles('operator'), and `FrameworkApprovalService.confirmRegistryShapeCertification` itself refuses (403) any caller without operator before it reads or writes, on every path that reaches it. The single exception is the BCF panel's in-process fast lane, actor `bcf-registry-authoring-panel`, which never arrives from a login (operator ruling, grant 2026-09-29T05-14-40-388Z-6cf80979). The RolesGuard's existing super_admin/admin bypass does not reach past this check.

This amends DEC-3a6f74's Current State ("platform scope: detected via JWT aud claim"). DEC-3a6f74's decision to keep a single service with guard decorators is unchanged and stays authoritative.

## Rationale

Scope granted by the choice of app client is a property of the client, which any pool user can pick; a security boundary must rest on something the user cannot choose. A Cognito group is issued only by an operator, travels in the verified token, and needs no Lambda trigger. The missing-metadata-is-allow behaviour of the guards made every forgotten declaration an open route, so the fix pairs the admission change with a zero-exception build gate. Operator-only confirmation at the write point, not just the route, closes every path to an operator-confirmed certificate, including the ones reached without the confirm controller.

## Implementation and evidence

- bc-core PR 871 (head aecdc46d, one commit), reviewed by Codex at full depth (gen-f3c411-03, ACCEPTED WITH BOUNDARY) and approved and merged by the auditor App at merge commit 03153973.
- Cognito changes, each under its own recorded operator grant: self sign-up closed (429ab235); client read/write attribute lists (d77e1e01); group bc-platform with its three members (08e67a88); bc-ai-service added (fa0170ba). S1 was verified by operator sign-ins through both clients.
- Tests: strategy unit tests (16), RSA-signed token tests against a local JWKS (7), operator-authority tests at the write point (4), and the zero-exception route metadata gate with a prove-it-reds fixture.

## Consequences

- Status stays `decided` until the served bc-core runs a build containing 03153973 with COGNITO_PLATFORM_GROUP and COGNITO_ADMIN_CLIENT_ID set. That serve move needs its own recorded operator grant, and the ADR flips to `implemented` with it.
- Any new controller must declare scope, and any new platform write must declare roles, or CI fails.
- A platform admin who is not in bc-platform can no longer use bc-admin; membership is managed through Cognito under an operator grant.
- Follow-ups (TSK-846529): require the user pool ID at boot independently of the issuer URL; stop the route gate from accepting an unrelated route guard in place of @Roles; fix the stale "D065" citation in the strategy comment to DEC-3a6f74 and this ADR. Later: bind bc-core to 127.0.0.1 (F5), inventory GET routes with side effects, and review whether bc-ai-service can drop to viewer.
