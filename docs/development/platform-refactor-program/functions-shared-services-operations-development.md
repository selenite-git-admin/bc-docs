---
id: platform-refactor-program-functions-shared
order: 45.1
title: "Function Dossiers: Shared Services, Operations, Development"
status: drafting
authority: reference
depends_on: [devhub, documentation-system, decision-and-change-procedure]
governing_sources:
  - Platform Readiness Program (the function list)
  - Vocabulary (the status words and the definition of done)
  - Documentation System
  - Decision and Change Procedure
governing_adrs:
  - DEC-3395bc (bc-docs is the single source of truth)
  - DEC-a67bae (the locked lane taxonomy; one owner per surface)
  - DEC-ce4314 (the ten onboarding lanes)
  - DEC-71c027 (Integrity Assurance as the platform thesis)
  - DEC-c220e4 (the interim rule on which metrics a tenant sees)
  - DEC-cf6d3b (the tenant activation model; tenant-to-package assignment)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Function Dossiers: Shared Services, Operations, Development

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md).

This annex holds seven function dossiers: S1, Authentication; S2, User and access management; S3, Tenant lifecycle and management; S4, Pricing and subscription; S5, Operator console; OP, Operations; and DV, Development. Every dossier has the same eleven headings, in this order: "What it is", "How bc-docs defines it", "What it owns", "The acts it performs", "What it receives and what it hands on", "State today", "Known defects and risks", "Governing ADRs", "Chapters to fold in, rewrite or retire", "Open questions for the operator" and "What "locked" will mean here". Everything was read on 2026-11-13, each repository at the short sha given in the table below. Three limits apply to the whole annex. Every source was read without changing it: the databases by SELECT or a read-only connection, the cloud account by list calls. A source that was listed but not opened, or a figure taken from a review file and not re-checked, is marked so where it appears. Chapters that were not read are given the verdict "not assessed in this annex".

**Read on 2026-11-13.** Every repository was read at `origin/main` only. The short shas are:

| Repository | origin/main |
|---|---|
| bc-core | `ec72438b` |
| bc-admin | `d37b241` |
| bc-db | `c6de1c4` |
| bc-infra | `81ace47` |
| bc-docs | `f4f5edd` |
| barecount-devhub | `93cc1ea5` |
| bc-exchange | `58a2e57` |
| bc-external-audit | `2d23f938` |

Other sources, all read-only: the live platform database `bc_platform_dev` (PostgreSQL 17.11, SELECT only); the DevHub database (`sqlite3 -readonly data/devhub.db`); the local runtime folder `~/bc-stack`; read-only AWS list calls in account 546549546538, region ap-south-1.

**Citation forms used below.** `repo:path:line @ sha` for code and documents. `query (bc_platform_dev, 2026-11-13): SQL -> result` for live data. `query (devhub.db, 2026-11-13): SQL -> result` for DevHub data. `command: ... -> result` for anything else. A statement marked "(not re-checked; reported in artifacts/spine-review/<file>)" was not opened at source for this annex.

**Terms used in every dossier.**
- **bc-core** is the backend API server (port 3100). **bc-admin** is the operator's web console (port 3010). **bc-portal** is the customer's web application (port 3000).
- **bc-db** is the repository that holds the platform database's schema changes. **bc-infra** holds the cloud infrastructure code. **bc-docs** holds the documentation. **DevHub** (repository barecount-devhub, port 4000) is the coordination service for development sessions.
- An **ADR** is an Architecture Decision Record: one file per decision in bc-docs, named by a `DEC-xxxxxx` identifier.
- A **tenant** is one organization's identity on the platform, with its own database (bc-docs:docs/reference/vocabulary.md:431 @ f4f5edd).
- **Platform scope** and **tenant scope** are the two kinds of caller bc-core recognises: an operator of the platform, or a user of one tenant.

---

### S1, Authentication

**What it is.** Authentication answers one question: who is calling. Every request to bc-core carries a token issued by Amazon Cognito, the managed sign-in service. bc-core checks the token and derives three facts from it: the caller's scope (platform or tenant), the caller's tenant, and the caller's roles. It serves operators signing in to bc-admin, tenant users signing in to bc-portal, and development sessions that call the API.

**How bc-docs defines it.**
- The function list defines S1 as "Who are you — Cognito login, JWT, MFA/TOTP, global guards" (bc-docs:docs/implementation/platform-readiness-program.md:88 @ f4f5edd). Its matrix row reads "4 global guards + Cognito TOTP; mature" (same file:142).
- The governing chapter is `docs/compliance/infosec-and-access-control.md`, with `status: drafting` and `authority: authoritative` (bc-docs:docs/compliance/infosec-and-access-control.md:5-6 @ f4f5edd). Its defining sentence: "bc-core authenticates every API request through an AWS Cognito-issued JWT." (same file:38).
- **The chapter contradicts the code on the token type.** It says `token_use` is "Typed as `id` or `access`; the strategy handles both" (same file:44). The code rejects every token that is not an ID token (bc-core:src/auth/strategies/cognito-jwt.strategy.ts:104-106 @ ec72438b).
- **The chapter is silent on the platform group.** Its claims table lists six claims and no group claim (same chapter:40-47). The code gives platform scope only to a member of a named Cognito group (bc-core:src/auth/strategies/cognito-jwt.strategy.ts:116-127 @ ec72438b). A search of the chapter for `cognito:groups` or "platform group" returns nothing (command: `grep -n -i -E "cognito:groups|platform group"` on the chapter at f4f5edd -> no match). A second chapter does state the rule (bc-docs:docs/implementation/frontend-experience.md:56 @ f4f5edd).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| module | `src/auth/` (20 files) | command: `git -C bc-core ls-tree -r --name-only origin/main src/auth` -> 20 paths @ ec72438b |
| module | the token check `strategies/cognito-jwt.strategy.ts` | bc-core:src/auth/strategies/cognito-jwt.strategy.ts:57-132 @ ec72438b |
| module | `JwtAuthGuard`, the global guard that requires a token | bc-core:src/auth/guards/jwt-auth.guard.ts:13-28 @ ec72438b |
| module | `ScopeGuard`, `TenantClaimGuard`, `RolesGuard` (shared with S2, to be split) | bc-core:src/auth/auth.module.ts:27-30 @ ec72438b |
| module | configuration `src/config/auth.config.ts` (four Cognito variables, no fallback values) | bc-core:src/config/auth.config.ts:3-16 @ ec72438b |
| route prefix | `GET /api/auth/me` (the only route in the module's own controller) | bc-core:src/auth/auth.controller.ts:9-21 @ ec72438b |
| module | the public-path list in the tenant middleware (shared with S3, to be split) | bc-core:src/tenancy/tenant.middleware.ts:26-31 @ ec72438b |
| cloud resource | Cognito user pool `ap-south-1_bM5xehxIx`, the pool the served bc-core trusts | command: `grep '^COGNITO_USER_POOL_ID=' ~/MyProjects/_wt/freeze-1055/.env` -> that id |
| cloud resource | stack `bc-dev-0200-auth`, which owns a different pool, `ap-south-1_pbyZXWjGs` (shared with OP) | command: `aws cloudformation describe-stack-resources --stack-name bc-dev-0200-auth` -> `ap-south-1_pbyZXWjGs`; bc-infra:cdk/lib/stacks/auth-stack.ts @ 81ace47 |
| screen | bc-admin `/login` and its Cognito client (`src/services/cognito.ts`, `src/services/auth.service.ts`, `src/adapters/auth.adapter.ts`, `src/hooks/useAuthService.ts`, `src/pages/LoginPage.tsx`) | bc-admin:src/services/cognito.ts:22-27 @ d37b241; bc-admin:src/components/AppRouter.tsx @ d37b241 (path `/login`) |
| script or command | `~/bc-stack/bc-core-signin.sh`, `check-cognito-signin.sh`, `set-cognito-password.sh` (operator-only, mode 700; contents not read) | command: `ls -la ~/bc-stack` |
| script or command | DevHub tool `devhub_get_cognito_token`, which issues tokens for API checks (shared with DV; source not opened) | barecount-devhub:CLAUDE.md:246 @ 93cc1ea5 |
| document | `docs/compliance/infosec-and-access-control.md` (shared with S2) | cited above |
| document | `docs/reference/runbooks/operations/cognito-identity-remediation.md` (`status: drafting`; body not read for this annex) | command: frontmatter scan of bc-docs `docs/` @ f4f5edd |

**The acts it performs.**
1. **Sign in.** Performed by a user in the browser. bc-admin talks to Cognito directly with the pool id and client id from its build settings, and handles the time-based one-time code (bc-admin:src/services/cognito.ts:22-27, 96-126 @ d37b241). bc-core takes no part. Nothing is written on the platform.
2. **Check a token.** Performed by bc-core on every request that is not marked public. It checks signature, issuer and expiry (bc-core:src/auth/strategies/cognito-jwt.strategy.ts:77-88 @ ec72438b), then token type, issuing client and group (same file:100-132). It reads Cognito's public keys and writes nothing.
3. **Return the caller's identity.** `GET /api/auth/me` returns the facts derived from the token (bc-core:src/auth/auth.controller.ts:15-21 @ ec72438b).
4. **Refuse to start without configuration.** bc-core does not boot if any of four Cognito settings is missing, or if the issuer names a different pool (bc-core:src/auth/strategies/cognito-jwt.strategy.ts:65-75 @ ec72438b).

No route in bc-core signs a user out, resets a password or enrols a second factor. Those happen in Cognito.

**What it receives and what it hands on.**

| Direction | Other function | What passes | Defined in bc-docs | Built |
|---|---|---|---|---|
| in | S2 | the user's attributes `custom:tenant_id` and `custom:roles`, and group membership, set on the Cognito user | partly: the two attributes are listed (infosec chapter:46-47); the group is not | yes (bc-core:src/auth/cognito-admin/cognito-admin.service.ts:151-175 @ ec72438b) |
| out | S2 | the caller record `{scope, tenantId, roles}` attached to the request | yes (infosec chapter:57-65) | yes (strategy:115-132) |
| out | S3 | the tenant named by the request must equal the token's tenant | no: the chapter's tenant section (71-85) does not mention the check | yes (bc-core:src/auth/guards/tenant-claim.guard.ts:63-65 @ ec72438b) |
| in | OP | the four Cognito settings, through the environment | no | yes (bc-core:src/config/auth.config.ts:5-16 @ ec72438b) |
| out | DV | test tokens for sessions | named only (barecount-devhub:CLAUDE.md:246 @ 93cc1ea5) | not opened |

**State today.**
- **Works.** Four global guards run in a fixed order: token, scope, tenant claim, role (bc-core:src/auth/auth.module.ts:25-30 @ ec72438b). The served bc-core answers its health probe (command: `curl http://127.0.0.1:3100/api/health/ready` -> 200).
- **Only two controllers are public.** They are the health check and the served-identity probe (command: `git grep -n -F '@Public()' origin/main -- 'src/**/*.controller.ts'` -> 2 lines: `src/health/health.controller.ts:7`, `src/database/served-identity/served-identity.controller.ts:12` @ ec72438b).
- **No bypass switch exists.** A search for `BYPASS_AUTH` in bc-core `src` returns nothing (command: `git grep -n -i BYPASS_AUTH origin/main -- src` -> no match @ ec72438b).
- **Tests exist for the token check and three guards,** and for neither `ScopeGuard` nor `JwtAuthGuard` (command: `ls-tree src/auth` -> spec files for the strategy (2), tenant-claim, roles and operator guards only @ ec72438b).
- **The pool in use is not in infrastructure code.** The served pool is `ap-south-1_bM5xehxIx`; the stack defined in bc-infra owns `ap-south-1_pbyZXWjGs`. The account holds four pools, two of them named `barecount-dev` (command: `aws cognito-idp list-user-pools` -> 4 pools).
- **Not built in bc-core:** sign-out, password reset and second-factor enrolment routes.

**Known defects and risks.**
1. The pool that decides who is admitted is not defined in bc-infra (citations in State today).
2. The chapter says access tokens are handled; the code rejects them (citations above).
3. The tenant middleware lists `/api/auth/login` and `/api/auth/callback` as public paths. Neither is a route (bc-core:src/tenancy/tenant.middleware.ts:26-31; bc-core:src/auth/auth.controller.ts:9-21 @ ec72438b).
4. With no `x-tenant-id` header, the middleware takes the first label of any host name that contains a dot. For the host `127.0.0.1` that yields the tenant slug `127` (bc-core:src/tenancy/tenant.middleware.ts:80-87 @ ec72438b).
5. Credentials are committed in bc-core scripts. A line matching a quoted password or key assignment is present at `scripts/enrich-bos-from-verification.mjs:61` and at `scripts/archive/decision-runs-2026/d299-populate-sap-aliases.mjs:12` (command: pattern search at ec72438b; values not printed). The evidence annex confirms a third line (row 17a: `bc-core:scripts/demo-full-lifecycle.mjs:103 @ ec72438b`); the pattern used for this dossier did not match it.
6. The comment in `auth.config.ts` records that a missing setting used to fall back to another pool's id (bc-core:src/config/auth.config.ts:3-4 @ ec72438b). The fallback is removed; the risk is recorded as history.

**Governing ADRs.**

| ADR | Summary | Status in the file |
|---|---|---|
| DEC-1fcbc0 | Cognito is the sign-in service | implemented |
| DEC-a537bf | Cognito tokens are used end to end | implemented |
| DEC-f6c2e5 | One global guard; exceptions are marked public | implemented |
| DEC-912f4f | Second factor by authenticator app, optional and enforceable by an administrator | implemented |
| DEC-13a260 | The browser uses the `amazon-cognito-identity-js` library | implemented |
| DEC-a2af9e | One user pool, with the tenant carried as an attribute | implemented |
| DEC-8dc51d | The customer portal takes the tenant from the token, not from build settings | decided |
| DEC-78b437 | Second factor by email is deferred | implemented |
| DEC-eea376 | Platform scope follows the user: the admin client's tokens need the platform group | implemented |

(Statuses: command: frontmatter `status:` of each `docs/governance/adrs/ADR-<uid>.md` @ f4f5edd.) No two of these conflict. DEC-a2af9e's "single pool" does not match the account, which holds four.

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/compliance/infosec-and-access-control.md` | rewrite | Wrong on token type; silent on the group rule; mixes S1, S2 and the database split. |
| `docs/implementation/frontend-experience.md` (section "Authentication Sequence", line 84) | rewrite | The chapter calls itself "deliberately a stub" (line 41); the sign-in part moves to the S1 chapter. |
| `docs/reference/runbooks/operations/cognito-identity-remediation.md` | not assessed in this annex | Body not read. |

**Open questions for the operator.**
1. Which pool is the pool of record: bring `ap-south-1_bM5xehxIx` under bc-infra, or move the platform to the pool the stack already owns?
2. Are access tokens to be accepted (as the chapter says) or ID tokens only (as the code does)?
3. Is the second factor mandatory for platform-scope users, or optional as DEC-912f4f states?

**What "locked" will mean here.**
1. The served pool id equals the pool defined in bc-infra, and a check fails when they differ.
2. The list of public controllers is exactly the two named above; a CI test fails if a third appears.
3. The chapter's claims table matches the checks in the code, line for line, including token type and group.
4. The middleware's public-path list names only routes that exist.
5. A CI scan fails on any committed credential in any repository.

---

### S2, User and access management

**What it is.** This function decides what an authenticated caller may do. It covers creating users, giving them roles, and keeping platform routes and tenant routes apart. Today a user exists only as a Cognito record; roles are a list held in a Cognito attribute; bc-core enforces them with guards and with markers on each route.

**How bc-docs defines it.**
- The function list defines S2 as "What may you do — users, roles, permissions, invites, platform/tenant scoping" (bc-docs:docs/implementation/platform-readiness-program.md:89 @ f4f5edd). Its matrix row reads "admin-provision only; no RBAC tables; UI placeholder" (same file:143). The closure note records the users screen as deferred: "**S2 users door DEFERRED** (solo-founder — no multi-user need; TSK-905844)" (the quotation runs across a line break in the source) (same file:39-40).
- The governing chapter is again `docs/compliance/infosec-and-access-control.md` (drafting). It defines scope: "`ScopeGuard` reads the `REQUIRED_SCOPE_KEY` metadata set by the decorator and compares it against the request's resolved scope" (line 65).
- **The chapter is silent on roles.** It does not mention `RolesGuard`, the `@Roles` marker or the role list (command: `grep -n -i -E "RolesGuard|@Roles"` on the chapter @ f4f5edd -> no match).
- **The chapter understates the overrides.** It says of `super_admin`: "this is the only scope override" (line 65). That is true of scope. For roles, both `super_admin` and `admin` pass every role check (bc-core:src/auth/guards/roles.guard.ts:34-35 @ ec72438b).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| module | `ScopeGuard` (platform or tenant) | bc-core:src/auth/guards/scope.guard.ts:16-50 @ ec72438b |
| module | `TenantClaimGuard` (request tenant equals token tenant; shared with S3, to be split) | bc-core:src/auth/guards/tenant-claim.guard.ts:27-68 @ ec72438b |
| module | `RolesGuard` | bc-core:src/auth/guards/roles.guard.ts:14-38 @ ec72438b |
| module | `OperatorGuard` and `SuperAdminGuard` (strict checks with no override) | bc-core:src/auth/guards/operator.guard.ts:23-24 @ ec72438b; command: `ls-tree src/auth/guards` |
| module | the role list: twelve roles in one type and one set, with a test that keeps them equal | bc-core:src/types/enums.ts:24-67 @ ec72438b; `src/types/role-catalog.spec.ts` (listed, not opened) |
| route prefix | `POST /api/admin/users` (create a user) | bc-core:src/auth/cognito-admin/user-provisioning.controller.ts:40-57 @ ec72438b |
| module | `CognitoAdminService` (read attributes, update roles, create user) | bc-core:src/auth/cognito-admin/cognito-admin.service.ts:73, 116, 151 @ ec72438b |
| route prefix | `POST /api/admin/mcf/role-grants` (shared with L6, Metric Contracts and certification, to be split) | bc-core:src/registry/mcf/mcf-role-grant.controller.ts:45-51 @ ec72438b |
| database table | `users.platform_user` (16 columns, 0 rows) | query (bc_platform_dev, 2026-11-13): `select count(*) from users.platform_user` -> 0 |
| database table | `mcf.role_grant_audit` (1 row; shared with L6) | query (bc_platform_dev, 2026-11-13): `select count(*) from mcf.role_grant_audit` -> 1 |
| cloud resource | Cognito group `bc-platform` | command: `grep '^COGNITO_PLATFORM_GROUP=' ~/MyProjects/_wt/freeze-1055/.env` -> `bc-platform` |
| screen | bc-admin `platform/users`, a placeholder page | bc-admin:src/components/AppRouter.tsx:296 @ d37b241 |
| document | `docs/compliance/infosec-and-access-control.md` (shared with S1) | cited above |

**The acts it performs.**
1. **Create a user.** Performed by a caller with the `platform_admin` role, through `POST /api/admin/users`. It writes one Cognito user carrying the tenant slug and the roles; Cognito emails a temporary password (bc-core:src/auth/cognito-admin/cognito-admin.service.ts:151-175 @ ec72438b). It writes nothing to the platform database. It does not check that the tenant exists, and it does not add the user to the platform group (same lines). No screen calls it (command: `git grep -n "admin/users" origin/main -- src` in bc-admin -> no match @ d37b241).
2. **Grant a metric-authoring role.** Performed by `super_admin` only, through `POST /api/admin/mcf/role-grants` (bc-core:src/registry/mcf/mcf-role-grant.controller.ts:50-51 @ ec72438b). The handler body was not read for this annex.
3. **Add a user to the platform group.** No route. The code comment says the group is "writable only through the Cognito admin API" (bc-core:src/auth/strategies/cognito-jwt.strategy.ts:117-119 @ ec72438b).
4. **Check each request.** Scope, then tenant claim, then role (bc-core:src/auth/auth.module.ts:27-30 @ ec72438b).

Not built: listing users, changing a user's general roles, disabling a user, resending an invitation, and any act by which a tenant's administrator manages that tenant's users.

**What it receives and what it hands on.**

| Direction | Other function | What passes | Defined in bc-docs | Built |
|---|---|---|---|---|
| in | S1 | the caller record `{scope, tenantId, roles}` | yes (infosec chapter:57-65) | yes |
| in | S3 | the tenant slug stamped on a new user | no | partly: the slug is free text, not checked against the tenant registry |
| in | S3 | "tenant creation to first user": the tenant administrator is created as part of creating a tenant | yes, as a design: "**Create tenant admin** — a governed identity user is created for the tenant administrator" (bc-docs:docs/implementation/tenant-onboarding.md:56 @ f4f5edd); ADR DEC-cf6d3b makes a verified administrator a condition of "tenant active" | no: the two acts are separate and nothing links them |
| out | every function | the role required on each route | no | yes: 303 `@Roles(` uses in 109 controller files (command: `git grep -F '@Roles(' origin/main -- 'src/**/*.controller.ts'` @ ec72438b) |
| out | L7, L4 | strict operator-only acts | no | yes: 5 handlers in 2 controllers (command: `git grep -n -E '@RequireOperator' ...` -> reader.controller.ts:219, 235, 334, 348; author-observation-chain.controller.ts:49 @ ec72438b) |

**State today.**
- **Works.** 118 of 138 controller files carry the platform-only marker and 17 carry the tenant marker (command: `git grep -l -F '@PlatformOnly()'` -> 118; `'@TenantScoped()'` -> 17; `ls-tree | grep -c controller.ts` -> 138 @ ec72438b).
- **Three marker families gate routes:** `@Roles`, `@RequireOperator` and `@RequireSuperAdmin` (citations above).
- **Roles live only in a Cognito attribute.** The one user table in the database is empty and is referenced only by its schema file and by privacy code (command: `git grep -l "platformUser\|platform_user" origin/main -- src` -> 6 files, none in `src/auth` @ ec72438b).
- **An unknown role in a token is dropped, not refused** (bc-core:src/auth/strategies/cognito-jwt.strategy.ts:134-138 @ ec72438b).
- **Not built:** a users screen (placeholder), and every act listed as not built above.

**Known defects and risks.**
1. The role `admin` passes every role check, and no chapter says so (bc-core:src/auth/guards/roles.guard.ts:35 @ ec72438b; chapter search above).
2. There is no record of who held which role and when, except one audit table for metric-authoring grants (queries above).
3. `users.platform_user` is an empty table with no writer (query and search above).
4. A user can be created for a tenant slug that does not exist (act 1).
5. Whether every platform write route carries an explicit role, as DEC-eea376 requires, was not measured for this annex.

**Governing ADRs.**

| ADR | Summary | Status in the file |
|---|---|---|
| DEC-42b9c0 | Users are created by an administrator only; no self sign-up | implemented |
| DEC-f0e78e | Platform authority and tenant authority are distinct classes | decided |
| DEC-6a9777 | The owner-assignment table is deferred until role queries need it | decided |
| DEC-eea376 | Platform scope follows the user; explicit roles on every platform write | implemented |
| DEC-cf6d3b | "Tenant active" requires a verified administrator and an assigned subscription | decided |

DEC-cf6d3b is decided and not built (see S3 and S4). No direct conflict among the five.

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/compliance/infosec-and-access-control.md` | rewrite | Silent on roles and on the `admin` override; shared with S1. |
| `docs/implementation/tenant-onboarding.md` (step 3 and "The handoff contract") | rewrite | States the first-user hand-off as a design; the built route is unconnected. |

**Open questions for the operator.**
1. Where do roles live: stay in the Cognito attribute, or move to a platform table with history?
2. Does the `admin` override stay, or does `super_admin` become the only one?
3. Who creates a tenant's later users: the operator only, or the tenant's administrator?
4. Is the users screen in the program, or listed as designed and not built?

**What "locked" will mean here.**
1. There is one route that creates a user; it refuses a tenant slug that is not in the registry.
2. A CI test fails when a platform write route has no role marker.
3. The roles that override checks are named in one file and in the chapter, and the two agree.
4. `users.platform_user` is either written by the user-creation act or removed by a bc-db migration.
5. The first-user hand-off from S3 has one written contract and one test.

---

### S3, Tenant lifecycle and management

**What it is.** This function creates a tenant, changes its state, and retires it. Creating a tenant means writing its row in the registry and creating its own database. The operator performs these acts; every other function relies on the result, because a tenant's database is where its admitted data, results and evidence are kept.

**How bc-docs defines it.**
- The function list defines S3 as "Provision container/DB, states, config, health, scoping, retirement" (bc-docs:docs/implementation/platform-readiness-program.md:90 @ f4f5edd).
- Three chapters govern it, all `status: drafting`: `docs/operations/tenant-lifecycle-and-subscription.md`, `docs/onboarding/tenant-onboarding.md` and `docs/implementation/tenant-onboarding.md` (command: frontmatter scan @ f4f5edd).
- The state model is stated once clearly: "**Tenant status** — `provisioning → active → suspended → archived`, plus `failed`. The operational state of the container itself, carried on the tenant registry." (bc-docs:docs/implementation/tenant-onboarding.md:45 @ f4f5edd). The vocabulary gives the same five words, each said with its subject (bc-docs:docs/reference/vocabulary.md:431 @ f4f5edd).
- **The procedure chapter names a route that refuses.** "The governed entry point is the **`POST /tenants`** API (`TenantProvisioningApiService`, bc-core PR #727, merged)" (bc-docs:docs/onboarding/tenant-onboarding.md:124 @ f4f5edd). The same service today throws a refusal for every call (bc-core:src/tenant-management/tenant-provisioning-api.service.ts:30-36 @ ec72438b). The catalog of platform procedures repeats the stale claim (bc-docs:docs/reference/platform-workflow-catalog.md:45, 59-60 @ f4f5edd), and so does the DevHub instruction file (barecount-devhub:CLAUDE.md:109 @ 93cc1ea5).
- **The lifecycle chapter says a record is missing that exists.** Its drift list says "Onboarding record persistence not located" (bc-docs:docs/operations/tenant-lifecycle-and-subscription.md:229 @ f4f5edd). The table exists and holds three rows (query (bc_platform_dev, 2026-11-13): `select count(*) from tenant.onboarding_record` -> 3).
- **The vocabulary and the database disagree on a tenant's kind.** The vocabulary says "No field records a tenant's kind, and none is to be added" (bc-docs:docs/reference/vocabulary.md:284 @ f4f5edd). The registry has the column `tenant_class_code`, limited to `fixture` or `customer` (query (bc_platform_dev, 2026-11-13): `select conname, pg_get_constraintdef(oid) from pg_constraint where conrelid='tenant.tenants'::regclass and contype='c'` -> `chk_tenants_class CHECK (tenant_class_code = ANY (ARRAY['fixture','customer']))`). It was added by migration 0040 under ADR DEC-c3a47e (bc-db:migrations/0040_fixture_classification_and_datname_authority.sql:5-13 @ c6de1c4).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| module | `src/tenant-management/` (controller, service, repository, refusal service, `lifecycle/` with 11 files) | command: `ls-tree src/tenant-management` @ ec72438b |
| route prefix | `/api/tenants`: 8 handlers (create, stats, list, target preview, read one, onboarding status, cancel onboarding, update) | bc-core:src/tenant-management/tenant-management.controller.ts:21-114 @ ec72438b |
| script or command | `npm run tenant:lifecycle -- create \| retire-prepare \| retire-record \| retire-drop` | bc-core:package.json:27 @ ec72438b; bc-core:src/tenant-management/lifecycle/tenant-lifecycle-cli.ts:7-10, 56-64 @ ec72438b |
| module | `src/tenancy/` (tenant middleware, tenant lookup, database naming, schema fence; the middleware's public-path list is shared with S1) | command: `ls-tree src/tenancy` @ ec72438b |
| route prefix | `GET /api/t/context` | bc-core:src/tenancy/tenant-context.controller.ts:16-22 @ ec72438b |
| database table | `tenant.tenants` (4 rows), `tenant.onboarding_record` (3), `tenant.tenant_infrastructure` (4), `tenant.tenant_classification_transition` (0), `tenant.tenant_schema_fence_event` (19) | query (bc_platform_dev, 2026-11-13): counts per table -> as shown |
| database table | `tenant.tenant_binding` (28), `tenant.contract_binding` (17), `tenant.gl_account_classification_binding` (shared with L10, Tenant onboarding, and DL, Delivery to a tenant; to be split) | same query |
| database | one database per tenant: `tbc_kaveri_dev`, `tbc_kaveridemo_dev`, `tbc_kaveridemo2_dev` | query (bc_platform_dev, 2026-11-13): `select datname from pg_database where datname ~ '^tbc_'` -> 3 |
| document (schema) | the tenant database's starting schema `baseline/tenant/0000_tenant_skeleton.sql`, tenant migrations `migrations/tenant/`, tenant releases r1 to r7 | command: `git -C bc-db ls-tree -r --name-only origin/main` @ c6de1c4 (shared with OP) |
| module | `src/registry/seed/seed-tenant-dbs.ts`, a test-only helper since 2026-09-27 | bc-core:src/registry/seed/seed-tenant-dbs.ts:17-21 @ ec72438b |
| module | CI guard `src/__architecture__/tenant-lifecycle-operator-plane.spec.ts` | command: `ls-tree` @ ec72438b (not opened) |
| screen | bc-admin `platform/tenants`, `platform/tenants/new-tenant`, `platform/tenants/:slug` | bc-admin:src/components/AppRouter.tsx:289-295 @ d37b241 |
| screen | bc-admin `tenant/configuration`, `tenant/health`, `tenant/scoping`, `tenant/infrastructure`: four placeholders (shared with S5) | bc-admin:src/components/AppRouter.tsx:262-265 @ d37b241 |
| document | the three chapters above; `docs/operating-model/tenancy-and-binding.md` (shared with L10) | cited above |

**The acts it performs.**
1. **Create a tenant.** Performed by the operator at a terminal with `npm run tenant:lifecycle -- create <slug>` and six required flags (bc-core:src/tenant-management/lifecycle/tenant-lifecycle-cli.ts:7-8, 56-62 @ ec72438b). It writes the registry row as `provisioning`, creates the database, applies the starting schema and the tenant migrations through the bc-db runner, checks the result, then records evidence and sets `active` (bc-core:src/tenant-management/lifecycle/tenant-birth.service.ts:1-7, 58-81 @ ec72438b).
2. **Refuse creation on the served API.** `POST /api/tenants` and `GET /api/tenants/target-preview` always answer 403 (bc-core:src/tenant-management/tenant-provisioning-api.service.ts:14-16, 30-36 @ ec72438b).
3. **Suspend a tenant.** Performed by `platform_admin` through `PATCH /api/tenants/:idOrSlug`. The request may set the status to `suspended` and nothing else (bc-core:src/tenant-management/dto/update-tenant.dto.ts:12-22 @ ec72438b). It updates the registry row and writes no other record (bc-core:src/tenant-management/tenant-management.service.ts:93-104 @ ec72438b).
4. **Retire a tenant,** in three commands: `retire-prepare` (backup and a proof that it restores), `retire-record` (registry row to `archived`, with evidence), `retire-drop` (drop the database; the registry row is kept) (bc-core:src/tenant-management/lifecycle/tenant-retirement.service.ts:4-8, 42-45 @ ec72438b).
5. **Cancel an onboarding record.** `POST /api/tenants/:idOrSlug/onboarding/cancel` (bc-core:src/tenant-management/tenant-management.controller.ts:97-103 @ ec72438b).
6. **Resolve the tenant on a request.** Only a tenant whose status is `active` resolves; any other answers "not found" (bc-core:src/tenancy/tenant.service.ts:35-38 @ ec72438b).

Not built: **resuming** a suspended tenant. No code path sets `suspended` back to `active` (command: `git grep -n -i -E "resume|reactivat|unsuspend" origin/main -- src/tenant-management` -> only tenant-creation re-run lines @ ec72438b).

**What it receives and what it hands on.**

| Direction | Other function | What passes | Defined in bc-docs | Built |
|---|---|---|---|---|
| in | OP | the tenant starting schema, tenant migrations and the runner, pinned by a bc-db commit | no | yes (flags `--bcdb-dir`, `--bcdb-commit`; tenant-lifecycle-cli.ts:58-59) |
| in | S4 | the Subscription that tenant creation should make `active` | yes (tenant-lifecycle-and-subscription.md:141, 164) | no (no subscription table; see S4) |
| out | S2 | the tenant's first administrator | yes, as a design | no (see S2) |
| out | S1, RT | the active tenant and its database name, on every tenant request | partly (infosec chapter:71-85) | yes (tenant.service.ts:85-91) |
| out | L10, DL | a tenant that can receive connections and contract bindings | named (bc-docs:docs/implementation/tenant-onboarding.md:36-38 @ f4f5edd, "provision, then hand off") | partly: the bindings tables exist and are written by other functions |
| out | PR, EV | retirement to retention and erasure | named only (tenant-lifecycle-and-subscription.md:168) | retirement is built; retention after it is not linked |

**State today.**
- **Four tenants are registered.** `kaveri` is active (class `fixture`); `probe_unit4` is archived (class `fixture`); `kaveridemo` and `kaveridemo2` are suspended (class `customer`) (query (bc_platform_dev, 2026-11-13): `select slug, status_code, tenant_class_code, schema_name, database_name from tenant.tenants` -> 4 rows).
- **The tenant named in the DevHub instruction file does not exist.** It names `demo-selenite` (barecount-devhub:CLAUDE.md:246 @ 93cc1ea5); the query above returns no such slug.
- **The operator console's create screen calls the refusing route.** It posts to `/tenants` and reads the target preview (bc-admin:src/api/tenants.ts:199-215 @ d37b241; bc-admin:src/pages/TenantCreatePage.tsx:50, 231 @ d37b241).
- **The route's own description is stale.** It still says the route "provisions tbc_<slug>_<env>" (bc-core:src/tenant-management/tenant-management.controller.ts:28-35 @ ec72438b).
- **A decided design is not applied.** bc-db migration 0034 adds a sixth tenant state and a gate that refuses `active` without a completeness verdict (bc-db:migrations/0034_onboarding_completeness_result.sql:4-6 @ c6de1c4). It has no row in the live ledger (query (bc_platform_dev, 2026-11-13): `select migration_name, event_kind from infrastructure.schema_migration_event` -> no 0034), the table is absent (query: `select to_regclass('tenant.onboarding_completeness_result')` -> null), and the live constraint lists five states. A comment in bc-core says the gate exists (bc-core:src/tenant-management/dto/update-tenant.dto.ts:13-16 @ ec72438b); the registry has two triggers and neither is that gate (query: `pg_trigger` on `tenant.tenants` -> `trg_tenants_database_name_default`, `trg_tenants_class_frozen`).
- **The infrastructure record is not kept true.** Two of four rows say `provisioning` (query: `select status_code from tenant.tenant_infrastructure` -> provisioning, provisioning, active, active). The vocabulary already names this defect (bc-docs:docs/reference/vocabulary.md:471 @ f4f5edd).
- **One column holds two formats.** `schema_name` is `tbc_kaveri` for one tenant and `tbc_probe_unit4_dev` for another (tenants query above); the code warns never to use it (bc-core:src/tenancy/tenant.service.ts:80-84 @ ec72438b).

**Known defects and risks.**
1. Three documents cited above name a creation route that refuses; the evidence annex (row 11c) verifies four bc-docs documents and the DevHub instruction file (citations above).
2. The console's create screen cannot succeed (citations above).
3. A suspended tenant cannot be resumed by any governed act.
4. Suspension leaves no record beyond the changed row.
5. The create command's default reference release is `r5` (bc-core:src/tenant-management/lifecycle/tenant-lifecycle-cli.ts:60 @ ec72438b) while bc-db holds releases up to r7 (command: `ls-tree releases/tenant` @ c6de1c4).
6. Two tenants of class `customer` exist. ADR DEC-c220e4 requires the entitlement record "before any tenant is activated for a party outside BareCount" (bc-docs:docs/governance/adrs/ADR-c220e4.md:3 @ f4f5edd). Both are suspended today; nothing in code enforces the condition.
7. The vocabulary and the registry disagree on whether a tenant's kind is recorded (citations above).

**Governing ADRs.**

| ADR | Summary | Status in the file |
|---|---|---|
| DEC-7df811 | The three lifecycles: onboarding record, tenant status, subscription | decided |
| DEC-cf6d3b | "Tenant active" means a verified administrator and an assigned subscription; amends DEC-7df811 | decided |
| DEC-103acb | Mandatory fields and a completeness gate before activation | decided |
| DEC-a67518 | Onboarding record as a gate for two hosting variants | decided |
| DEC-771baf | One database per tenant; the platform does not depend on tenant data | implemented |
| DEC-f02230 | The schemas inside a tenant database | implemented |
| DEC-09fb2f | Tenant evidence cannot be changed; the served login is separate from the owner | decided |
| DEC-3ee0f6 | One archive bucket per tenant, created at onboarding | decided |
| DEC-c3a47e | Fixture tenants can be archived and re-created; adds the tenant class | decided |
| DEC-c220e4 | Every active tenant gets every active metric until the Subscription exists | decided |

**Conflicts to settle.** DEC-cf6d3b endorses a sixth tenant state that the vocabulary does not list. DEC-c3a47e adds a tenant-kind column that the vocabulary says is not to be added. The lifecycle chapter cites DEC-2c79c8 as governing (bc-docs:docs/operations/tenant-lifecycle-and-subscription.md:17 @ f4f5edd); that ADR's status is `superseded`. The readiness chapter lists DEC-09fb2f as "proposed" (platform-readiness-program.md:90); the file says `decided`.

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/operations/tenant-lifecycle-and-subscription.md` | rewrite | Split between S3 and S4; its drift list is out of date; cites a superseded ADR. |
| `docs/onboarding/tenant-onboarding.md` | rewrite | Names the refusing route and a retired schema file (lines 124, 132). |
| `docs/implementation/tenant-onboarding.md` | rewrite | The clearest statement of the model, but it describes "a single governed provisioning call" (line 55) from the console that does not exist. |
| `docs/reference/platform-workflow-catalog.md` (tenant row) | rewrite | Repeats the stale route. |
| `docs/operating-model/tenancy-and-binding.md` | not assessed in this annex | Only its headings were read. |

**Open questions for the operator.**
1. Ruling T4: is tenant creation the terminal command exposed through the console, or a served route with a separate owner-side worker?
2. Is resuming a suspended tenant a governed act in the program, and what record does it write?
3. Does the tenant class column stay (and the vocabulary change), or is it withdrawn?
4. Is migration 0034 applied, or withdrawn until DEC-cf6d3b is built?
5. What happens to `kaveridemo` and `kaveridemo2`: retire them, or keep them for the program's thread?
6. Is `tenant.tenant_infrastructure` kept true by the creation act, or retired?

**What "locked" will mean here.**
1. Tenant creation has exactly one entry point. The served route is removed or refuses, the console does not call a refusing route, and the existing CI guard fails if a second creator appears.
2. Each state change (create, suspend, resume, retire) has one governed act that writes a record.
3. The vocabulary's tenant states equal the live constraint on `tenant.tenants.status_code`.
4. No chapter and no instruction file names a creation route other than the one that works.
5. The create command's default release equals the newest tenant release in bc-db, checked in CI.

---

### S4, Pricing and subscription

**What it is.** This function is meant to define what a tenant buys and to record that it bought it: the packages on offer, the tenant's Subscription, what the Subscription entitles the tenant to, and billing. It serves the operator, who sets the offer, and every runtime act that should check a tenant's entitlement. Today only a small package table and its screens exist.

**How bc-docs defines it.**
- The function list defines S4 as "Packages, entitlements, tier gating, billing" (bc-docs:docs/implementation/platform-readiness-program.md:91 @ f4f5edd). Its matrix row marks all three columns absent and says "deferred-by-decision / out of readiness scope" (same file:145).
- The governing chapter is `docs/operations/tenant-lifecycle-and-subscription.md` (drafting). It defines the central record: "Subscription is a platform-scoped governance record." (line 38) with "One active Subscription per tenant at any time." (line 43). It lists four entitlement axes, among them "Metric entitlement | The subset of platform-registered metrics the tenant may evaluate." (line 84).
- The consuming chapter is `docs/operating-model/tenant-entitlement-enforcement.md` (drafting). It says "Seven enforcement surfaces in contract execution consult the Subscription record." (line 51), and its status table marks eight rows "Not yet wired" (lines 126-133). Seven and eight do not agree inside the one chapter.
- The vocabulary defines the tenant-side word: "**subscribed** | The tenant's package includes the metric | **no record yet.**" (bc-docs:docs/reference/vocabulary.md:165 @ f4f5edd).
- **bc-docs contradicts itself on whether a record exists in the first version.** The implementation chapter says "no subscription record is instantiated" (bc-docs:docs/implementation/tenant-onboarding.md:46 @ f4f5edd). ADR DEC-cf6d3b, decided later, lifts that deferral "to the minimal extent needed" (bc-docs:docs/governance/adrs/ADR-cf6d3b.md:77 @ f4f5edd). The chapter was not updated.

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| database schema or table | `pricing.package`: 1 table, 15 columns, 7 rows | query (bc_platform_dev, 2026-11-13): `select package_name, status_code from pricing.package` -> custom active; Free active; finance-essentials, finance-complete, full-erp, crm, hr deprecated |
| module | the table's type definition, described as "reader auto-provisioning tier definitions" | bc-core:src/database/schema/pricing/package.ts:2, 14-17 @ ec72438b |
| route prefix | `/api/packages`: 6 handlers (shared with L7, Readers and connections, because a package row holds a reader list; to be split) | bc-core:src/registry/execution/package.controller.ts:27-90 @ ec72438b |
| screen | bc-admin `registry/packages`, `registry/packages/:packageId`; `pricing/plans` redirects there | bc-admin:src/components/AppRouter.tsx:306 @ d37b241; route list of the same file |
| screen | bc-admin `pricing/entitlements`, `pricing/usage`, `pricing/billing`: three placeholders | bc-admin:src/components/AppRouter.tsx:307-309 @ d37b241 |
| document | `docs/operations/tenant-lifecycle-and-subscription.md` (shared with S3), `docs/operating-model/tenant-entitlement-enforcement.md`, the generated `docs/reference/data-dictionary/pricing.md` | frontmatter scan @ f4f5edd |

Nothing else exists. There is no subscription table, no entitlement table and no billing code.

**The acts it performs.**
1. **Create, change, list or remove a package.** Performed by a caller with `platform_admin` or `operator`, through `/api/packages` (bc-core:src/registry/execution/package.controller.ts:32-33, 67-68, 89-90 @ ec72438b). It reads and writes `pricing.package`.

No other act is built: none assigns a package to a tenant, none records a Subscription, none checks entitlement, none bills.

**What it receives and what it hands on.**

| Direction | Other function | What passes | Defined in bc-docs | Built |
|---|---|---|---|---|
| in | L6, L8 | the set of metrics that may be offered | no | no |
| out | S3 | the Subscription made `active` at tenant creation | yes (tenant-lifecycle-and-subscription.md:141) | no |
| out | DL | "subscribed": the tenant's package includes the metric | yes (vocabulary.md:165), record not built | no |
| out | RT, L7 | entitlement and limits read before each act | yes (tenant-entitlement-enforcement.md:51, 126-133) | no: every row "Not yet wired" |
| in | external billing service | billing events that cause a state change | yes (tenant-lifecycle-and-subscription.md:178-189) | no |

**State today.**
- **No Subscription record exists** (query (bc_platform_dev, 2026-11-13): `select to_regclass('tenant.subscription')` -> null; a search of table names for `subscription`, `entitle`, `billing`, `invoice` or `plan` returns only `mcf.chain_enrichment_plan` and PostgreSQL's own catalog tables).
- **Nothing ties a tenant to a package.** `tenant.tenants` has no package column (query: columns of `tenant.tenants` -> id, slug, tenant_name, schema_name, status_code, config_json, four audit columns, tenant_class_code, database_name).
- **The interim package named by the decided ADR is absent.** DEC-cf6d3b prefers a row named `pre_launch_exclusive` and accepts reuse of `Free` (bc-docs:docs/governance/adrs/ADR-cf6d3b.md:116 @ f4f5edd). The table holds `Free` and no `pre_launch_exclusive` (package query above).
- **No billing integration exists.** A search of bc-core `src` and `package.json` for "stripe" matches two unrelated source files and no dependency (command: `git grep -l -i stripe origin/main -- src package.json` -> `src/registry/bcf/panel/in-process/panel-json.util.ts`, `src/registry/seed/seed-roadmap-sources.ts` @ ec72438b).
- **The rule in force is the default.** "until the subscription model is built, every active tenant may see and evaluate every active platform metric on its own data" (bc-docs:docs/governance/adrs/ADR-c220e4.md:16 @ f4f5edd).

**Known defects and risks.**
1. The built table models readers per tier, not metrics per package, so it does not fit ruling T1 (the main document, under "The rulings") (bc-core:src/database/schema/pricing/package.ts:2 @ ec72438b; columns `reader_manifest_json`, `tier_order` from the column query).
2. Three console screens under "pricing" are placeholders (citation above).
3. The enforcement chapter counts seven surfaces and lists eight (citation above).
4. Two ADRs are decided and unbuilt: DEC-324d9e (billing) and DEC-cf6d3b (the Subscription tables it names at lines 120-121 do not exist).
5. The readiness chapter calls DEC-4aa2fd "reversed" (platform-readiness-program.md:91); the ADR file says `superseded`, by DEC-c220e4 (bc-docs:docs/governance/adrs/ADR-4aa2fd.md:5, 11 @ f4f5edd).

**Governing ADRs.**

| ADR | Summary | Status in the file |
|---|---|---|
| DEC-324d9e | An external billing service handles payment; four tiers | decided (not built) |
| DEC-1392ee | A two-week demonstration tier | decided |
| DEC-4a515b | Four business chains offered from the start | implemented |
| DEC-c220e4 | Every active tenant gets every active metric until the Subscription exists; supersedes DEC-4aa2fd | decided |
| DEC-cf6d3b | The minimal Subscription: a tenant-to-package assignment with three states, and an interim all-metrics package | decided (not built) |
| DEC-4aa2fd | The plan's metric entitlement drives contract binding | superseded |

**Conflict.** DEC-324d9e's four tiers and DEC-cf6d3b's single interim package are both in force; DEC-cf6d3b says its package "sits outside" the four tiers (ADR-cf6d3b.md:115). The program's ruling T1 (a tenant subscribes to a package of many metrics) needs one of them amended.

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/operations/tenant-lifecycle-and-subscription.md` | rewrite | Sound as a design of the Subscription; must be marked designed and not built, and split from S3. |
| `docs/operating-model/tenant-entitlement-enforcement.md` | rewrite | Keep the model; fix the count; reduce to the one check ruling T2 builds. |
| `docs/implementation/tenant-onboarding.md` (section "Subscription and pricing surfaces") | rewrite | Predates DEC-cf6d3b. |
| `docs/reference/data-dictionary/pricing.md` | keep nearly as is | Generated; regenerate after any schema change. |

**Open questions for the operator.**
1. Ruling T6: how does a package name its metrics: an explicit list, or by business function and subfunction?
2. Is `pricing.package` reshaped for this, or kept for readers while a new table carries the offer?
3. Is the interim package the existing `Free` row or a new `pre_launch_exclusive` row?
4. Do the four tiers and the external billing service of DEC-324d9e remain the decided commercial model?

**What "locked" will mean here.**
1. One Subscription record per tenant exists, and tenant creation writes it.
2. A package's metrics are a record that can be read by one query.
3. Entitlement is checked in exactly one place, with a test that fails when the check is removed.
4. The enforcement chapter's table matches the code row for row; unbuilt rows are in the guide's "designed, not built" list. (The guide is the new bc-docs section `docs/guide/` that the main document describes under "bc-docs: read first, and kept true".)
5. Each pricing screen either performs its act or is removed.

---

### S5, Operator console

**What it is.** The operator console is the web application bc-admin. An operator uses it to see and administer everything else on the platform: sources, contracts, the business vocabulary, metrics, tenants and the documentation. It holds no data and performs no act of its own; each screen calls bc-core.

**How bc-docs defines it.**
- The function list defines S5 as "The operator's cockpit surfacing/administering everything below" (bc-docs:docs/implementation/platform-readiness-program.md:92 @ f4f5edd). Its matrix row reads "mature (255 commits); placeholder doors (users, pricing) + **tenant operational tabs (config/health/scoping/infra) reclassified here from L10, deferred**" (same file:146).
- The governing chapter is `docs/implementation/frontend-experience.md` (drafting). It says of itself: "The chapter is deliberately a stub." (line 41) and of the console: "bc-admin is the more matured of the two frontends." (line 159). It defers every screen to a reference that does not exist: "No generator for that reference exists." (line 43).
- bc-docs therefore does not define what the console must offer. No chapter lists its screens or says which acts must have one.

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| repository | bc-admin: 299 files under `src`, 110 page files outside tests | command: `git -C bc-admin ls-tree -r --name-only origin/main src \| wc -l` -> 299; pages count -> 110 @ d37b241 |
| screen | 132 route elements in one router file | command: `grep -c '<Route'` on bc-admin:src/components/AppRouter.tsx -> 132 @ d37b241 |
| screen | 10 routes that render a placeholder page | command: `grep -n -E '<Route[^>]*PlaceholderPage'` on the same file -> 10 lines (175, 262-265, 296, 299, 307-309) @ d37b241 |
| module | the API layer `src/api/` (29 modules, one per backend area) | command: `ls-tree src/api` @ d37b241 |
| module | the documentation reader pages (`src/pages/docs/`, 5 files; shared with DV) | command: pages per folder @ d37b241 |
| script or command | `npm run sync-docs` (`scripts/sync-docs.js`; shared with DV) | bc-admin:package.json:13 @ d37b241 |
| script or command | `npm run dev`, served on port 3010, forwarding `/api` to port 3100 | bc-admin:package.json:7; bc-admin:vite.config.ts:29-33 @ d37b241 |
| document | `docs/implementation/frontend-experience.md` (shared with TS, Tenant self-service) | cited above |

The sign-in screen belongs to S1. The tenant screens belong to S3. The package screens belong to S4.

**The acts it performs.** None of its own. For each governed act of another function, the console either offers a screen that calls the act's route, offers a placeholder, or offers nothing. Three cases verified for this annex:
1. **Tenant creation:** a screen exists and calls a route that always refuses (see S3).
2. **User creation:** a route exists and no screen calls it (see S2).
3. **Reading documentation:** screens exist; the backend's document folder is absent on the served build (see State today).

**What it receives and what it hands on.**

| Direction | Other function | What passes | Defined in bc-docs | Built |
|---|---|---|---|---|
| in | S1 | the operator's token, attached to each call | yes (frontend-experience.md:56) | yes |
| in | every function | that function's routes | no chapter lists which acts need a screen | partly (see State today) |
| in | DV | the documentation set, copied by `sync-docs` into bc-core's `private-docs/` folder | yes (bc-docs:docs/development/documentation-system.md:98-100 @ f4f5edd) | the script exists; the served folder does not |
| out | DV | the screen list, to DevHub's screen registry | named (frontend-experience.md:43) | DevHub holds 118 screen rows (query (devhub.db, 2026-11-13): `select count(*) from screen_registry` -> 118); their truth was not checked |

**State today.**
- **bc-core exposes 598 route handlers; 284 of them write.** (command: `git grep -E "^[[:space:]]*@Get\("` and the same for Post, Put, Patch, Delete over `src/**/*.controller.ts` -> 314, 233, 1, 33, 17 @ ec72438b.) This figure is counted from route decorators; the route snapshot `src/__architecture__/routes.snapshot.json` holds 600 entries (evidence annex, row 14). An earlier review's figure, "220 of 285 write routes have no screen", was not re-checked (reported in artifacts/spine-review/PLATFORM-2-frontends-demo-audit.md); the count of write handlers measured here is 284.
- **Ten routes are placeholders:** one contract family page, four tenant tabs, users, infrastructure and three pricing pages (bc-admin:src/components/AppRouter.tsx:175, 262-265, 296, 299, 307-309 @ d37b241).
- **The console is served from a shared working copy by a development server,** not from a fixed build (command: `~/bc-stack/process-compose.yaml` lines 108-111 -> `working_dir: ~/MyProjects/bc-admin`, `npm run dev -- --host 127.0.0.1`).
- **The documentation reader cannot find its documents on the served build.** bc-core reads them from `private-docs/` beside its build, or from a path in `BC_CORE_PRIVATE_DOCS` (bc-core:src/docs/docs.service.ts:21-22 @ ec72438b). That folder is ignored by git (bc-core:.gitignore:101 @ ec72438b), it is absent from the served tree (command: `ls ~/MyProjects/_wt/freeze-1055/private-docs` -> no such directory), and the variable is not set for the served server (command: `grep -c BC_CORE_PRIVATE_DOCS` on the served `.env` and on `process-compose.yaml` -> 0 and no match).

**Known defects and risks.**
1. The tenant create screen cannot succeed (S3).
2. The documentation reader, which bc-docs calls the canonical reader, has no documents on the served build (citations above).
3. bc-docs does not say which acts must have a screen, so "complete" cannot be checked.
4. The console changes whenever its shared working copy changes, with no build identity (citation above).
5. Other console calls that end at retired or refusing routes are listed in a review file and were not re-checked here (reported in artifacts/spine-review/PLATFORM-2-frontends-demo-audit.md, section 2.2).

**Governing ADRs.**

| ADR | Summary | Status in the file |
|---|---|---|
| DEC-5cef91 | The navigation structure, version 5, "final locked" | implemented |
| DEC-7eec2e | Navigation organised by business chain | implemented |
| DEC-b39a00 | Menu restructure, tenant group, top bar and left bar | decided |
| DEC-c800d2 | The console's version 1.0.0 scope | implemented |
| DEC-b97390 | The documentation reader is built into the console | decided |

**Possible conflict.** Three ADRs each set the console's navigation (DEC-5cef91, DEC-7eec2e, DEC-b39a00) and none is marked superseded. Only their titles and statuses were read; which one the router follows was not determined.

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/implementation/frontend-experience.md` | rewrite | A stub by its own statement; the console part becomes the S5 chapter with the list of acts and screens. |
| `docs/development/documentation-system.md` (reader sections) | rewrite | Describes the copy step; does not say how the documents reach a served build. |

**Open questions for the operator.**
1. Must every governed act have a screen, or only the acts on the program's thread, with the rest reached by command?
2. Is the console served from a fixed build like bc-core, or does it stay a development server?
3. Are the ten placeholder routes removed, or kept as a list of intended screens?

**What "locked" will mean here.**
1. A generated table lists every governed act and its screen, command or "none by decision"; CI fails when an act has no entry.
2. No screen calls a route that is retired or always refuses; a CI test compares the console's calls with bc-core's routes.
3. The served console has a build identity that can be read, like the served bc-core.
4. The documentation reader shows the documents of bc-docs `main` on the served build.
5. No placeholder route remains without a recorded decision.

---

### OP, Operations

**What it is.** Operations is how the platform is run and changed. It covers where the platform runs and what each environment is called; how a new build of bc-core is put into service; how settings and secrets reach a running server; how the database schema changes; which database logins exist and what each may do; backup and restore; the automated checks on every change (continuous integration, CI); and the cloud infrastructure. It serves the operator and every development session.

**How bc-docs defines it.**
- The function list in the readiness chapter has no Operations function (bc-docs:docs/implementation/platform-readiness-program.md:86-120 @ f4f5edd). OP is one of the functions the main document adds, under "The functional map".
- bc-docs holds a section of 16 operations chapters (command: files per folder @ f4f5edd). The one that matches practice most closely is `docs/operations/serve-moves-and-live-windows.md` (drafting). It defines the central term: "**A live act** is any act that changes live state." (line 47). It names three kinds: a serve move, a database migration apply, and a metric go-live (lines 48-50). It also defines "**A live window** is one announced, operator-granted run of one or more live acts" (line 52).
- The schema-change rule is stated by ADR and quoted in that chapter: "Every platform schema change is authored once as a bc-db forward migration … and applied to every environment only by the spine runner with one infrastructure.schema_migration_event row per apply" (line 317, quoting DEC-4c1396).
- **Three chapters describe an environment that does not exist.** `docs/operations/deployment-topology.md` and `docs/implementation/infrastructure.md` name a repository `platform-infra-stack`, a file `cd-deploy.yml`, the supervisor pm2 and the service bc-ai (command: pattern search @ f4f5edd -> deployment-topology lines 43, 68, 101, 122, 127 and others; infrastructure lines 48, 52, 98, 102, 131 and others). The repository is bc-infra, its files are `cd-prepare.yml`, `cd-execute.yml` and `ci-validate.yml` (command: `ls-tree .github` @ 81ace47), and the DevHub instruction file records pm2 and bc-ai as retired (barecount-devhub:CLAUDE.md:135, 154 @ 93cc1ea5).
- **The upgrade chapter names a retired method.** It directs a reset "via `bc-core/scripts/golden-snapshot.mjs`" (bc-docs:docs/operations/upgrade-and-migration.md:60 @ f4f5edd). That script exists only under `scripts/archive/` (command: `ls-tree scripts | grep golden-snapshot` -> `scripts/archive/mcf-decision-drivers-2026/golden-snapshot.mjs` @ ec72438b). The chapter cites the frozen folder `docker/redesign` in 16 places (same pattern search).
- **Schema counts disagree in three places.** The infosec chapter says "Eleven schemas" (docs/compliance/infosec-and-access-control.md:93); the data-model chapter says "fifteen schemas" (docs/implementation/data-model-and-schema.md:136); the DevHub instruction file says 11 (barecount-devhub:CLAUDE.md:290 @ 93cc1ea5). The live database has 22 (query (bc_platform_dev, 2026-11-13): `select table_schema, count(*) from information_schema.tables where table_type='BASE TABLE' and table_schema not in ('pg_catalog','information_schema') group by 1` -> 22 schemas, 329 tables).
- **Backup is not described.** The workstation chapter mentions backups only of `.env` files (bc-docs:docs/development/dev-workstation-mac-mini.md:158, 203 @ f4f5edd; command: `grep -n -i -E 'pg-backup|backup|restore'` -> those 2 lines).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| repository | bc-db: 68 files under `migrations/` (this listing counts 67 SQL files and the `tenant` folder; the evidence annex, row 4a, counts 67 platform migrations plus 6 tenant migrations, 73 SQL files), 47 under `rollback/`, 181 under `tools/`, 230 under `docs/` | command: `ls-tree` counts @ c6de1c4 |
| script or command | the migration runner `tools/runner/runner.js` and its three entry points (owner, runtime, tool) | bc-db:tools/runner/README.md:1-36 @ c6de1c4; command: `ls-tree tools/runner` |
| database table | the migration ledger `infrastructure.schema_migration_event` (74 rows: 70 applied, 3 excepted, 1 adopted) | query (bc_platform_dev, 2026-11-13): `select event_kind, count(*) from infrastructure.schema_migration_event group by 1` -> as shown |
| document | bc-db `docs/migration-number-gaps.md`, `tools/runner/ROLES.md`, `docs/dbcp/` (158 files) | bc-db:docs/migration-number-gaps.md:1-15 @ c6de1c4 |
| module | the bc-core guard that freezes `docker/redesign` | bc-core:src/database/schema/__tests__/docker-redesign-freeze.spec.ts (listed) @ ec72438b |
| database roles | 20 roles; the served logins `bc_platform_runtime` and `bc_tenant_runtime`; the owner `bc_schema_owner` | query (bc_platform_dev, 2026-11-13): `select rolname, rolsuper, rolcanlogin from pg_roles where rolname !~ '^pg_'` -> 20 rows |
| repository | bc-infra: 91 files; six stack definitions (auth, CI runner, database, database apply, network, secrets) | command: `ls-tree` @ 81ace47; bc-infra:cdk/lib/stacks/ (6 files) |
| script or command | bc-infra deploy files `cd-prepare.yml`, `cd-execute.yml`, `ci-validate.yml` | bc-infra:.github/workflows/ @ 81ace47 |
| local runtime | `~/bc-stack/process-compose.yaml` (five services: `docker-stack`, `devhub`, `bc-core`, `bc-admin`, `bc-portal`), `servers.sh`, `up.sh`, `health.sh` | command: read of `~/bc-stack/process-compose.yaml` lines 20-130; `~/bc-stack/servers.sh` lines 1-30 |
| script or command | the serve launcher `~/bc-stack/serve-core-ref-v2.sh` with `serve-guard.mjs` and `dist-manifest.js` | command: read of `~/bc-stack/serve-core-ref-v2.sh` lines 1-62 |
| script or command | the serve-move toolkit `artifacts/serve-move/toolkit/` (10 files; last changed 2026-10-12) | command: `git -C barecount-devhub log -1 --format='%h %cs' origin/main -- artifacts/serve-move/toolkit` -> `37c10eb6 2026-10-12` |
| script or command | secrets loaders `scripts/with-dev-secrets.mjs`, `scripts/dev-secrets/dev-secrets-lib.mjs`, `scripts/with-demo-secrets.mjs`; `npm run start:dev:aws`, `dev-secrets:fill` | bc-core:package.json:13-14; bc-core:scripts/with-dev-secrets.mjs:3-14 @ ec72438b |
| module | the served-credential checks `src/env-files.ts` and `src/database/served-identity/` | bc-core:src/database/served-identity/served-credential-source.ts:5-13 @ ec72438b |
| script or command | backup `~/bc-stack/pg-backup.sh` and `pg-backup-catchup.sh`, run by two launch agents | command: read of `~/bc-stack/pg-backup.sh` lines 1-40; `ls ~/Library/LaunchAgents` -> `com.barecount.pg-backup.plist`, `com.barecount.pg-backup-catchup.plist` |
| script or command | bc-core `db:dump`, `db:restore`, `db:restore:exact`, `db:dump:s3`, `db:restore:s3` | bc-core:package.json:45-49 @ ec72438b |
| script or command | CI definitions: `ci.yml` in bc-core, bc-admin, bc-db, barecount-devhub, bc-exchange; `service-ci.yml` in bc-external-audit; `adr-hygiene.yml` in bc-docs | command: `ls-tree .github/workflows` in each repository |
| document | the 16 chapters under `docs/operations/`; `docs/implementation/infrastructure.md`; `docs/development/dev-workstation-mac-mini.md`, `continuous-integration.md`, `build-and-release.md`; `~/bc-stack/README.md` | frontmatter scan @ f4f5edd |
| not built | the reference run (a fixed set of metrics evaluated again and compared with expected values) | command: `git -C barecount-devhub ls-tree -r --name-only origin/main \| grep -i -E 'reference-run\|reference-harness'` -> no match |

**The acts it performs.**
1. **Start and stop local services.** Performed by the operator or a session with `~/bc-stack/servers.sh up|start|stop|restart|ps` (lines 17-29). A launch agent keeps the supervisor running (`com.barecount.process-compose.plist`).
2. **Serve bc-core from a fixed build.** The launcher refuses unless the tree is clean, its commit equals the pinned commit, the build's file list hashes to the pinned value, and no settings file holds a database address (command: `~/bc-stack/serve-core-ref-v2.sh` lines 26-41). It then loads secrets and starts the server (line 62).
3. **Move the serve to a new build (a serve move).** As documented: build two identical trees, rehearse on a copy, obtain the auditor's clearance and the operator's recorded grant, run one runner script, verify, and keep a rollback (bc-docs:docs/operations/serve-moves-and-live-windows.md:86-97 @ f4f5edd). As practised on 2026-11-13: one tree `freeze-1055`, an evidence folder with a before and after record, and a recorded grant (command: `head ~/bc-stack/serve-move-20261113-1055/verify-after.txt` -> "serve-move freeze-1052 -> freeze-1055 GREEN at 2026-11-13T09:26:33Z", grant id `2026-11-13T09-23-35-983Z-2900e8fd`).
4. **Load secrets.** `scripts/with-dev-secrets.mjs` reads one secret from AWS Secrets Manager, named `bcp-dev-aps1-sct-secret`, and passes its keys to the server's environment (bc-core:scripts/with-dev-secrets.mjs:3-12 @ ec72438b; bc-core:scripts/dev-secrets/dev-secrets-lib.mjs:15, 42 @ ec72438b).
5. **Change the schema.** Write one forward migration in bc-db; have it reviewed at an exact commit; prove it on a restored copy; apply it with the runner, which writes the migration and its ledger row in one transaction (bc-db:tools/runner/README.md:9-11, 20-24 @ c6de1c4). The operator's approval is required before each apply (bc-db:README.md:22-23 @ c6de1c4).
6. **Back up.** Nightly at 02:00, `pg_dumpall` of the whole database server, compressed, uploaded with a checksum to `s3://barecount-dev-artifacts/mac-mini-pg/`; the newest seven are kept locally (command: `~/bc-stack/pg-backup.sh` lines 2-5, 15-38).
7. **Check every change.** Each repository's CI runs on a pull request and on a push (for example bc-core:.github/workflows/ci.yml:29-31 @ ec72438b; checks `static-analysis`, `vitest-shard`, `quality-gate`, `e6b-db-integration` at lines 170-313).
8. **Deploy cloud infrastructure.** By hand-started GitHub Actions in two steps, prepare then execute (bc-infra:.github/workflows/cd-prepare.yml:1, 11-12; cd-execute.yml:1, 9-10 @ 81ace47), or by a local `cdk deploy` (bc-infra:README.md:38 @ 81ace47).

Not built: a restore of a nightly backup; an application deployment to the cloud; the reference run.

**What it receives and what it hands on.**

| Direction | Other function | What passes | Defined in bc-docs | Built |
|---|---|---|---|---|
| in | every function | a merged change to serve, or a migration to apply | yes (serve-moves chapter) | yes |
| in | DV | the auditor's clearance and the operator's recorded grant | yes (serve-moves chapter:94-95) | yes (grant cited in act 3) |
| out | every function | the served build's identity (tree, commit, build hash) | yes (serve-moves chapter:88-90) | yes: readable from the running server's working directory |
| out | S3 | the tenant starting schema, tenant migrations and runner | no | yes |
| out | S1 | the Cognito settings | no | yes |
| out | every function's Modify step | the reference run's verdict | named in the main document only, under "The reference run" | no |
| out | PR, S3 | a restorable backup | no | backup yes; restore not proven |

**State today.**
- **What is served.** bc-core on port 3100 runs from `~/MyProjects/_wt/freeze-1055` at `ec72438b` (command: `lsof -a -p <pid of the listener on 3100> -d cwd` -> that path; `~/bc-stack/process-compose.yaml` lines 91-95). Its probe reports the served login as `bc_platform_runtime` with no violations (command: `curl http://127.0.0.1:3100/api/health/ready` -> `"expectedRole":"bc_platform_runtime","ok":true`).
- **Three serve procedures coexist.** The chapter describes twin trees named by letter. No twin tree exists today (command: `find ~/MyProjects/_wt -maxdepth 1 -type d -name 'freeze-*-b'` -> 0), and current trees are named by pull-request number (8 `freeze-*` folders). The toolkit on barecount-devhub `main` was last changed on 2026-10-12. The practice since 2026-11-11 leaves an evidence folder per move (6 folders `~/bc-stack/serve-move-2026111*`); no committed script for it was found.
- **The local runbook is stale.** `~/bc-stack/README.md` says the served tree is `freeze-q` from 2026-09-30 (lines 52-56), that bc-admin and bc-portal start disabled (lines 34-35) and that DevHub runs `npm run dev` (line 32). The supervisor file says `freeze-1055`, `disabled: false` and `npm start` (lines 32, 92, 112, 124).
- **Worktrees.** `~/MyProjects/_wt` holds 239 folders using 31 GB (command: `find ... -type d | wc -l` -> 239; `du -sh` -> 31G). bc-core alone has 99 registered worktrees (command: `git -C bc-core worktree list | wc -l` -> 99). These two counts measure other things than the evidence annex (row 20a), which counts 323 linked worktrees across the twelve repositories; 239 of them are under `~/MyProjects/_wt` (repositories annex).
- **Secrets have two sources in practice.** The loader's default profile is `bc-dev`, a short-lived role (bc-core:scripts/dev-secrets/dev-secrets-lib.mjs:42 @ ec72438b). The Mac overrides it to `default` (`process-compose.yaml` line 14), and the backup uses `--profile default` too (`pg-backup.sh` lines 29-31). The second loader's default secret, `bcp-dev-aps1-demo-runtime-secret` (bc-core:scripts/with-demo-secrets.mjs:25 @ ec72438b), is not among the 13 secret names in the account (command: `aws secretsmanager list-secrets --query "SecretList[].Name"` -> 13 names, none matching).
- **Schema change works and is recorded.** The newest ledger row is `0071_demo_proof_schedule_v5`, applied 2026-11-12 (query (bc_platform_dev, 2026-11-13): newest row by `event_seq`). 327 of 329 tables are owned by `bc_schema_owner` (query: `select tableowner, count(*) from pg_tables ... group by 1` -> bc_schema_owner 327, barecount 2).
- **Four migrations on bc-db `main` have no ledger row:** 0032, 0034, 0035 and 0038 (command: `ls-tree migrations` @ c6de1c4 compared with the ledger query). Three others are recorded as `excepted`: 0001, 0002 and 0008 (ledger query).
- **Roles.** The live database has no `bc_spine_*` role (roles query), although bc-db documents four of them as introduced by migration 0002 (bc-db:tools/runner/ROLES.md:3-9, 28-31 @ c6de1c4); 0002 is one of the excepted rows. One role is a superuser: `barecount` (roles query). The read tool used by sessions connects as that superuser (query: `select current_user` -> barecount), although a read-only login `bc_capture_ro` exists.
- **Backup runs; restore is unproven.** The bucket prefix holds 132 objects, the newest dated 2026-11-13 (command: `aws s3api list-objects-v2 --bucket barecount-dev-artifacts --prefix mac-mini-pg/` -> 132, newest `pg_dumpall-20261113T013704Z.sql.gz.sha256`). No script that restores one of these dumps was found in `~/bc-stack`. bc-core's `db:restore` prints a warning that it can leave "a hybrid stale/current DB" (bc-core:package.json:46 @ ec72438b), and `db:dump:s3` uses a profile named `barecount` that the DevHub instruction file says exists only on the laptop (bc-core:package.json:48 @ ec72438b).
- **Cloud.** Of the six stack definitions, three are deployed: `bc-dev-0200-auth`, `bcp-dev-aps1-sct` (secrets) and `bcp-dev-aps1-cir` (CI runners). No network, database or database-apply stack is deployed, and the account has no managed database (command: `aws cloudformation list-stacks` -> those three among BareCount names; `aws rds describe-db-instances` -> none). The platform runs only on the Mac.
- **CI.** bc-core and bc-db choose where to run through a `pick-runner` check (bc-core:.github/workflows/ci.yml:67-68 @ ec72438b; bc-db:.github/workflows/ci.yml:58-59 @ c6de1c4). Which runner each repository uses today depends on a repository setting that was not read for this annex.
- **Environment names.** One suffix is in use: `_dev` on `bc_platform_dev` and on each tenant database. The code derives it by pattern from a settings value (bc-core:src/registry/seed/seed-tenant-dbs.ts:46-49 @ ec72438b). bc-infra uses `stage=dev` (bc-infra:README.md:12, 37 @ 81ace47). The deployment chapter speaks of "Local", "AWS `dev`" and "AWS `prod`" (bc-docs:docs/operations/deployment-topology.md:131-139 @ f4f5edd). So "dev" names both the Mac's databases and a cloud environment that mostly does not exist.

**Known defects and risks.**
1. No restore of a nightly backup has been shown to work (State today).
2. The serve procedure in use is not the documented one and has no committed script (State today).
3. The bc-db README still says "scaffold only ... No schema, migration, seed or content lives here yet" (bc-db:README.md:3 @ c6de1c4).
4. Four merged migrations are not applied, and code comments already assume one of them (see S3, migration 0034).
5. The number-order rule for applies rests on an ADR that is still `proposed` (DEC-bd6894).
6. A long-lived administrator profile is the working credential on the Mac (State today).
7. Sessions read the live database as a superuser (State today).
8. Three operations chapters describe retired or absent things (How bc-docs defines it).
9. There is no reference run, so a change to engine code cannot be shown to leave results unchanged.
10. The DevHub database, the cache server and the cloud demonstration machine are outside the nightly backup, which dumps only the PostgreSQL server (`pg-backup.sh` lines 14-15).

**Governing ADRs.**

| ADR | Summary | Status in the file |
|---|---|---|
| DEC-4c1396 | bc-db is the only place schema changes are written and applied | decided |
| DEC-b1a286 | The earlier database source-of-truth model | superseded |
| DEC-bd6894 | Apply migrations in number order; schema and code that need each other go together | proposed |
| DEC-1918d0 | Database separation, naming and the ten database rules | implemented |
| DEC-e50b83 | The port table | implemented |
| DEC-ecd55c | Credentials live in AWS Secrets Manager | implemented |
| DEC-441665 | Packages are installed through AWS CodeArtifact | implemented |
| DEC-e39ed3 | Naming and tagging of cloud resources | proposed |
| DEC-c40e7a | A managed cloud database for the platform | proposed |
| DEC-5b760c | Quality checks run in each repository's CI | decided |
| DEC-005ea7 | One production environment; no per-tenant development copy | implemented |
| DEC-890417 | The pm2 supervisor | superseded |

**Conflicts.** Two ADRs that bc-infra's code and README follow are still `proposed` (DEC-e39ed3, DEC-c40e7a). The build chapter still lists DEC-890417 among its governing ADRs (bc-docs:docs/development/build-and-release.md:14 @ f4f5edd).

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/operations/serve-moves-and-live-windows.md` | rewrite | The right frame and terms; the steps describe twin trees and a toolkit no longer used; it lists eleven open points of its own (lines 382-406). |
| `docs/operations/deployment-topology.md` | history | Describes a repository, files and services that do not exist. |
| `docs/implementation/infrastructure.md` | rewrite | Same stale names; becomes the short "what is deployed" page. |
| `docs/operations/upgrade-and-migration.md` | history | Built on the frozen `docker/redesign` folder and an archived script. |
| `docs/implementation/data-model-and-schema.md` | rewrite | Wrong schema count; cites the frozen folder as source. |
| `docs/development/dev-workstation-mac-mini.md` | keep nearly as is | Matches the Mac; add backup and restore. |
| `docs/development/continuous-integration.md` | keep nearly as is | Detailed and recent; confirm the runner per repository. |
| `docs/development/build-and-release.md` | rewrite | Cites a superseded ADR and retired services. |
| `docs/operations/operations-overview.md`, `security-operations.md`, `incident-and-change-management.md`, `runtime-operations.md`, `runtime-runbook.md`, `observability-and-telemetry.md`, `performance-and-scale.md` | not assessed in this annex | Not read. |

**Open questions for the operator.**
1. What are the environment names: is the Mac "dev", and what is a cloud environment called when one exists?
2. Which serve procedure is the one procedure: the documented twin-tree rehearsal, or the single-tree move now practised, written down and scripted?
3. Does a serve move on the development host still need the operator's code each time (ruling G1)?
4. Are migrations 0032, 0034, 0035 and 0038 applied, or withdrawn from `main`?
5. Is the cloud infrastructure in bc-infra kept as designed and not built, or removed until needed?
6. Ruling B1: is one fixed dump set kept outside the repositories as the reference run's input?

**What "locked" will mean here.**
1. One written serve procedure has one committed script; the local runbook is generated from the supervisor file and cannot disagree with it.
2. A nightly backup is restored to a throwaway copy on a schedule, and the result is recorded.
3. Every migration file on bc-db `main` has a ledger row or a line in a register of exceptions; CI fails otherwise.
4. Secrets reach a server by one route and one profile; no working credential is a long-lived administrator key.
5. Sessions read the database through a read-only login.
6. The reference run exists, runs from a fixed input, and its result is required before engine code merges.

---

### DV, Development

**What it is.** Development is the set of tools and rules by which the platform is changed. It has five parts. DevHub records each working session, its plan, its tasks and its result. bc-docs is the documentation. ADRs record decisions. The auditor exchange sends work to Codex, an independent reviewer, and the approval desk records the operator's consent. Memory files and change records keep what a session learned and what it changed. It serves every session and the operator.

**How bc-docs defines it.**
- The readiness chapter's function list has no Development function (bc-docs:docs/implementation/platform-readiness-program.md:86-120 @ f4f5edd). DV is added by the main document, under "The functional map".
- bc-docs has a section of 12 development chapters, all `status: drafting` (command: frontmatter scan @ f4f5edd).
- **DevHub** is defined in `docs/development/devhub.md`: "DevHub is a single Node service plus a single SQLite database plus a stdio MCP server." (line 38) and "DevHub is deliberately a coordination registry, not a runtime." (line 48). The chapter's numbers are out of date: it says "thirty-six tables" (line 44) and "sixty `devhub_*` tools" (line 45). DevHub has 66 tables and 110 tools (query (devhub.db, 2026-11-13): `select count(*) from sqlite_master where type='table' and name not like 'sqlite_%'` -> 66; `select count(*) from mcp_tool_registry` -> 110; command: distinct `'devhub_*'` names in barecount-devhub:src/mcp-server.js -> 110 @ 93cc1ea5).
- **The documentation system** is defined in `docs/development/documentation-system.md`: "bc-docs is the documentation source of truth. Filesystem layout plus YAML frontmatter authority is the discipline" (line 37). A chapter's status is one of "`drafting`, `reviewing`, `locked`, `superseded`, `retired`" (line 44). DevHub's document index is derived: "When the registry contradicts the file, the file wins and the registry is rescanned." (line 142).
- **No chapter is locked.** The only files with `status: locked` are eight evidence records (command: `git grep -l -E '^status: locked' origin/main -- docs` -> 8 paths, all under `docs/evidence/` @ f4f5edd); this is a line search, and the evidence annex (row 21a) counts seven by reading frontmatter only. Several files carry statuses outside the declared list, such as `approved`, `closed`, `active`, `accepted` and `implemented` (frontmatter scan).
- **Decisions** are defined in `docs/development/decision-and-change-procedure.md`: "the ADR file is the source of truth; the DevHub `decisions` table row is metadata that points at the file" (bc-docs:docs/development/decision-and-change-procedure.md:38 @ f4f5edd).
- **Change records** are defined in the same chapter: "The two sides share a `ref_uid` ... and produce a single `CHG-xxxxxx` row in the `change_records` table." (same file:122).
- **The auditor and the desk** are defined in `docs/operations/mac-auditor-operations.md` (`status: active`): "A request on the desk is never authority. Only a grant recorded with your phone code is." (bc-docs:docs/operations/mac-auditor-operations.md:53 @ f4f5edd).
- **The session method is defined twice.** The chapter `docs/development/the-controller-operating-model.md` (drafting, 675 lines) describes the method of thirteen controllers, which the program parks. The rules a session actually follows are in barecount-devhub `CLAUDE.md`, not in bc-docs.
- **Memory files are not defined in bc-docs.** No development chapter governs them; they are named only in the DevHub instruction file (barecount-devhub:CLAUDE.md, section "Session discipline (DEC-ebf0b4 / D268 — MANDATORY)" @ 93cc1ea5; line not recorded).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| repository | barecount-devhub: 8,095 tracked files; server, 244 route lines, the tool server `src/mcp-server.js` (3,820 lines) | command: `ls-tree -r | wc -l` -> 8095; `git grep -c -E "^(app|router)\.(get|post|put|patch|delete)\("` summed -> 244; `wc -l` -> 3820 @ 93cc1ea5 |
| database | `data/devhub.db`: 66 tables | query above |
| module | session rules `src/lib/controllers.js` (`checkSessionOpen`, `checkPlanBinding`) and close gates `src/lib/close-gates.js` | barecount-devhub:src/lib/controllers.js:136, 156; src/lib/close-gates.js:49-189 @ 93cc1ea5 |
| module | scans: `doc-scanner.js`, `code-scan*.js` (5 files), `mcp-tool-scanner.js` | command: `ls-tree src/lib` @ 93cc1ea5 |
| script or command | hooks: `scripts/claude-hooks/blueprint-inject.js`, `memory-write-hook.js`, `session-start-reminder.js`; `scripts/host/devhub-stop-hook.js`, `devhub-watchdog.js`, `bc-driver.js`; the global commit hook in `~/.config/barecount/git-hooks` | command: `ls-tree scripts`; `git config --global core.hooksPath` -> `~/.config/barecount/git-hooks` |
| document | the anchors `blueprints/demoed-terminal.md`, `goal.md`, `oct-02-drive.md` | command: `ls-tree blueprints` @ 93cc1ea5 |
| repository | bc-docs: 659 ADR files (the evidence annex, row 8f, counts 660 markdown files in the folder, which includes its README), 27 errata, 26 operating-model, 26 implementation, 16 operations, 13 onboarding, 12 development, 10 foundation chapters | command: files per folder @ f4f5edd |
| script or command | bc-docs checks `scripts/docs-control/audit_adrs.py` and `audit_frontmatter.py`, run by `adr-hygiene.yml` | bc-docs:.github/workflows/adr-hygiene.yml:25-28 @ f4f5edd |
| route prefix | the documentation reader `GET /api/docs/manifest`, `/file/*`, `/asset/*` in bc-core (shared with S5) | bc-core:src/docs/docs.controller.ts:36-72 @ ec72438b |
| script or command | the `codex-exchange` skill: `gen-new-thread`, `gen-send`, `gen-wait`, `gen-open-threads`, `gen-close` | command: `ls-tree scripts/exchange/codex-exchange-skill/bin` @ 93cc1ea5 |
| repository | bc-exchange, the approval desk: 41 files; requests, grants, questions, comments | bc-exchange:README.md:3-20; bc-exchange:src/grants.mjs:25, 58, 64 @ 58a2e57 |
| repository | bc-external-audit, the auditor's mailbox and service: 8,940 files under `docs/`, of which 3,122 messages and 3,572 responses | command: `ls-tree -r docs` counts @ 2d23f938 |
| files | memory: 397 files, an 84-line index, 86 archived files (397 is 396 memory files plus the index `MEMORY.md`; evidence annex, row 30; the archive folder has 86 entries, 84 of them markdown) | command: `ls ~/.claude/projects/-Users-anant-MyProjects-barecount-devhub/memory/*.md | wc -l` -> 397 |
| database table | compliance records: `change_records` (2,626 rows), `activity` (38,393), `session_commit` (1,576), `memory_write` (1,101), `qa_nc_records` (1,584), `risks` (22) | query (devhub.db, 2026-11-13): counts per table -> as shown |
| document | the 12 chapters under `docs/development/`; `docs/operations/mac-auditor-operations.md`; `docs/compliance/` (6 chapters); barecount-devhub `CLAUDE.md` | frontmatter scan @ f4f5edd |

**The acts it performs.**
1. **Open a session.** Performed by a session through the DevHub tool `devhub_session_open`. The rule checks role and controller, allows one open controller session per controller, and requires a worker's controller to be open (barecount-devhub:src/lib/controllers.js:136-155 @ 93cc1ea5). It writes one `sessions` row.
2. **Save the plan.** `devhub_session_save_plan`. It needs an open task bound to the session (controllers.js:156) and writes the plan side of the change record (bc-docs:docs/development/devhub.md:82-90 @ f4f5edd).
3. **Checkpoint.** `devhub_session_checkpoint` appends a row; 9,223 exist (query (devhub.db, 2026-11-13): `select count(*) from session_checkpoints` -> 9223).
4. **Close through the gates.** `devhub_session_close` evaluates the report, deliverables, auditor threads, self-audit, role rules, chain status, memory and commit collisions (barecount-devhub:src/lib/close-gates.js:49, 71, 107, 123, 137, 148, 155, 173, 189 @ 93cc1ea5).
5. **Commit with a session line.** A global commit hook requires each commit message to name an open session (command: `ls ~/.config/barecount/git-hooks` -> `commit-msg`, `commit-msg-check.js`). 1,576 commits are attributed (query above).
6. **Record a decision.** `devhub_decision_record` writes the registry row and the ADR file (bc-docs:docs/development/decision-and-change-procedure.md:47 @ f4f5edd).
7. **Send work to the auditor.** A session publishes a message on a `gen-` thread with the skill and waits for a reply (command: skill files listed above). The mailbox holds 2,339 such messages (command: `ls-tree -r docs | grep -c 'MSG-Claude-gen-'` @ 2d23f938).
8. **Ask for the operator's consent.** A session posts a request to the desk; "**A request becomes a grant** only when the operator enters the current 6-digit code from the authenticator app on their phone." (bc-exchange:README.md:21 @ 58a2e57). The grant stores the exact text and its SHA-256 (bc-exchange:src/grants.mjs:79-80 @ 58a2e57).
9. **Pin the anchor.** One row in `active_program` names the document shown to a session on each turn (query below).
10. **Scan.** DevHub scans the documents, the code and its own tools into registry tables (modules listed above).

**What it receives and what it hands on.**

| Direction | Other function | What passes | Defined in bc-docs | Built |
|---|---|---|---|---|
| in | every function | commits carrying a session line; changed chapters and ADRs | yes (decision-and-change-procedure.md) | yes |
| out | OP | the auditor's clearance and the operator's grant for a live act | yes (mac-auditor-operations.md, section 2) | yes |
| out | every function | the anchor and the tasks a session is shown at start | no | yes, and stale (State today) |
| out | S5 | the documents for the reader, by `sync-docs` | yes (documentation-system.md) | script exists; served folder absent (see S5) |
| in | S5, every function | screens and routes, by scan | partly (frontend-experience.md:43) | built for bc-core routes; age not shown |
| out | every function | "code change to chapter": a change in the platform reaches its chapter | no chapter states an obligation | no |

**State today.**
- **DevHub is running** (command: `curl http://127.0.0.1:4000/health` -> 200) and so is the desk (command: `curl http://127.0.0.1:3040/` -> 200; `GET /api/grants-list` -> 430 grants).
- **The anchor points at the parked drive.** The one row not retired is `demoed-terminal | blueprints/demoed-terminal.md | 77d882af`, pinned 2026-11-01 (query (devhub.db, 2026-11-13): `select program_uid, blueprint_path_text, substr(blueprint_commit_sha,1,8), pinned_at from active_program where retired_at is null` -> that row). No refactor anchor is on `main` (command: `ls-tree blueprints` -> three files, none for the refactor @ 93cc1ea5).
- **Fourteen sessions are open,** the oldest since 2026-10-12 (query: `select uid, role_code, controller_code, substr(started_ts,1,10) from sessions where ended_ts is null` -> 14 rows, 3 controller and 11 worker).
- **The task list is mostly machine-made backlog.** 5,007 tasks: 1,466 planned, 57 in progress, 483 parked, 1,347 completed, 1,654 aborted (query: `select task_status, count(*) from tasks group by task_status`). 960 open tasks are titled "Review DLV-..." (query: `select count(*) from tasks where title_text like 'Review DLV-%' and task_status in ('planned','wip','parked')` -> 960). The evidence annex (row 8b) counts 992 automatic review tasks by adding 32 titled "Review bundle", and (row 8c) finds that 56 of the 57 in-progress tasks have no open session.
- **Plans stopped.** Of 98 plans, 10 are active (with one `draft` plan, eleven are not closed; evidence annex, row 8d); the last write to any plan was 2026-10-02 (query: `select max(updated_ts) from plans` -> 2026-10-02 04:11:41).
- **Deliverables are registered and not reviewed.** 904 deliverables; 844 have no review row (query: `select count(*) from deliverable d where not exists (select 1 from deliverable_review r where r.deliverable_id=d.deliverable_id)` -> 844).
- **The document index reads an old copy of bc-docs.** The scanner reads the path in `BC_DOCS_PATH` (barecount-devhub:src/lib/doc-scanner.js:25 @ 93cc1ea5), which the supervisor sets to the shared working copy (`process-compose.yaml` line 12). That copy is 141 commits behind `main` (command: `git -C bc-docs rev-list --count HEAD..origin/main` -> 141). The index holds 4,900 rows, 3,664 of them `retired` (query: `select status_code, count(*) from documents group by status_code` -> retired 3664, unvalidated 1236).
- **The decision registry and the ADR files differ.** DevHub holds 663 decisions; bc-docs holds 659 ADR files (660 markdown files in the folder with its README; evidence annex, row 8f). By status: registry proposed 13, reversed 14; files proposed 11, reversed 9 (query: `select decision_status, count(*) from decisions group by decision_status`; command: `git grep -h -E '^status:' origin/main -- 'docs/governance/adrs/ADR-*.md' | sort | uniq -c` @ f4f5edd).
- **A tracker frozen in July is still held.** `onboarding_candidate` has 12,562 rows, last written 2026-07-07 (query: `select count(*), max(updated_ts) from onboarding_candidate`).
- **One gate has never fired.** `unattributed_change` has 0 rows (query above).
- **Chapters stopped changing.** Commits touching the chapter folders and the vocabulary page: 137 in September, 11 in October, 0 in November (command: `git -C bc-docs log origin/main --since=<month start> --until=<month end> -- <the nine chapter folders and docs/reference/vocabulary.md> | wc -l`). The main document, under "What the evidence says", gives 107 for September on a different count.
- **The project registry is wider than the platform.** 24 projects, 13 active (query: `select project_status, count(*) from projects group by project_status`); the instruction file says 12 repositories (barecount-devhub:CLAUDE.md:3 @ 93cc1ea5).
- **The memory hook is tied to one user's path** (barecount-devhub:scripts/claude-hooks/memory-write-hook.js:14 @ 93cc1ea5).

**Known defects and risks.**
1. A session is shown the parked program on every turn (State today).
2. The document index cannot be trusted, because it reads a copy 141 commits old (State today).
3. The DevHub chapter states 36 tables and 60 tools against 66 and 110 (citations above).
4. No chapter is locked, so by the documentation system's own status list no chapter is finished (citations above).
5. The frontmatter check runs against a baseline that only shrinks, yet statuses outside the declared list remain on `main` (bc-docs:.github/workflows/adr-hygiene.yml:27-28 @ f4f5edd; frontmatter scan).
6. The method chapter describes the parked fleet method (citation above).
7. The instruction file carries errors a session will act on: a tenant that does not exist (line 246), a creation route that refuses (line 109), a schema count of 11 (line 290).
8. Nothing obliges a session to read or update a chapter; consultation is by habit only.
9. The registry and the ADR files disagree on four decisions and on status counts (State today).
10. The findings that the Chief's session cannot close, that 35 tools are unused and that the scans are 22 days old were not re-checked here (reported in artifacts/spine-review/DEVHUB-1-internals.md and DEVHUB-2-as-platform-spine.md).

**Governing ADRs.**

| ADR | Summary | Status in the file |
|---|---|---|
| DEC-a4e550 | The ADR file is the record; DevHub keeps metadata | implemented |
| DEC-633b2a | One allocator gives decision numbers | implemented |
| DEC-623f8f | ADR hygiene: supersession pairs, no ADR left proposed past 30 days | decided |
| DEC-ebf0b4 | Session discipline and the self-audit at close | implemented |
| DEC-79b62f | The Foundation gate: four questions before a change | decided |
| DEC-3395bc | bc-docs is the single source; flat sections; reader served by bc-core | decided |
| DEC-e0a8ca | One frontmatter vocabulary for authority and status, checked in CI | decided |
| DEC-c897cd | The vocabulary page is the only authority for status words | decided |
| DEC-b97390 | The reader is built into the operator console | decided |
| DEC-081931 | The permanent `gen-` exchange with the auditor | implemented |
| DEC-44456d | The auditor's home on the Mac; grants recorded on the desk | decided |
| DEC-5b760c | Quality checks in each repository's CI; DevHub holds non-conformities | decided |
| DEC-a67bae | The ten lanes and the rule that every surface has one owner | decided |
| DEC-804874 | The earlier chain check at session close | superseded |

**Conflicts.** The DevHub chapter cites DEC-804874 as governing (bc-docs:docs/development/devhub.md:17 @ f4f5edd); it is superseded. DEC-623f8f forbids leaving an ADR proposed past 30 days, and 11 ADR files are `proposed` (count above), among them DEC-bd6894, DEC-e39ed3 and DEC-c40e7a, which Operations follows in practice.

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/development/devhub.md` | rewrite | Counts and gates out of date; cites a superseded ADR. |
| `docs/development/documentation-system.md` | rewrite | The authority and status model stays; add how a chapter becomes locked and how documents reach the served reader. |
| `docs/development/decision-and-change-procedure.md` | keep nearly as is | Matches the ADR and change-record practice; remove the retired chain-check section. |
| `docs/development/the-controller-operating-model.md` | history | Describes the parked method. |
| `docs/operations/mac-auditor-operations.md` | keep nearly as is | The only `active` runbook; matches the desk. |
| `docs/development/continuous-integration.md`, `dev-workstation-mac-mini.md` | keep nearly as is | Belong to OP. |
| `docs/development/development-overview.md`, `developer-experience.md`, `quality-assurance.md`, `metric-readiness-toolkit.md`, `lessons-platform-readiness-umbrella.md` | not assessed in this annex | Not read. |
| `docs/compliance/iso-27001-conformance.md` and the other compliance chapters | not assessed in this annex | Not read. |
| barecount-devhub `CLAUDE.md` | rewrite | Corrected at the program's first phase; its rules move into the guide and it becomes a pointer. |

**Open questions for the operator.**
1. Ruling A5: is a chapter locked when its function is locked, and who sets the status?
2. Where do the session rules live: in a bc-docs chapter with `CLAUDE.md` as a pointer, or in `CLAUDE.md` alone?
3. Do memory files remain a separate store, or is each one folded into a chapter or deleted as its function locks?
4. Ruling G4: do the approval desk and DevHub become one surface?
5. Which close gates stay for a method of one driving session: all of them, or only report, commits, deliverable registration and auditor threads?
6. Is a decided ADR allowed to merge without its chapter change in the same pull request?

**What "locked" will mean here.**
1. The anchor shown to a session is the current program, and a check fails when the pinned document is not on `main`.
2. DevHub's document index is built from bc-docs `main` and states its age; the count of indexed chapters equals the count of files.
3. Every chapter's status is one of the declared values, and the CI check passes with an empty baseline.
4. The decision registry and the ADR files agree in count and in status, checked in CI.
5. The session rules exist in one text; any other copy is a pointer.
6. Every open task has an owner and belongs to the program's plan; no task is created by a gate.
