---
id: deployment-topology
order: 31
title: "Deployment Topology"
status: drafting
authority: authoritative
depends_on: [the-authority-model, infrastructure, backend-services, auxiliary-services, tenant-lifecycle-and-subscription]
governing_sources:
  - Infrastructure
  - Backend Services
  - Tenant Lifecycle and Subscription
governing_adrs:
  - DEC-3395bc (bc-docs SSOT cutover: the documentation layout, chapter list, voice discipline and editorial gates)
  - DEC-1918d0 (Deployment and database architecture; two-database split; ten normalization rules)
  - DEC-771baf (Tenant database topology; one tenant database per tenant)
  - DEC-005ea7 (Single production environment per tenant; trial equals real tenant)
  - DEC-e50b83 (Master port reservation)
  - DEC-324d9e (Stripe billing; four hosting variants)
  - DEC-f02230 (Tenant DB schema organization)
  - DEC-3b86ea (Section renames; Operations as the section name; clean slate migration moved into Upgrade and Migration)
  - DEC-a67518 (Tenant Onboarding Gate; checklist-based readiness for BYO-DB and BC-Agent tiers)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Deployment Topology

## Scope

This chapter records the operational view of where the platform deploys, how the deployment procedure runs, what is deployed in the readiness baseline, and what is queued behind future formalization. It states the AWS account scope, the GitHub OIDC deployment role, the CI validate and CD deploy procedure shape, the AuthStack and dormant PlatformInfraStack split, the development substrate every engineer runs, the environment names (`dev`, `stg`, `prod`) and what each is today, and the per-hosting-variant deployment realization status. It records the boundary between Deployment Topology and the Infrastructure chapter that catalogs the deployable resources themselves. It records the as-built drift between the procedure and the platform's current deployment state.

This chapter does not redefine the AWS account, region, or resource inventory (Infrastructure), the per-service deployable shape (Backend Services, Auxiliary Services), the hosting-variant commercial categorization (Tenant Lifecycle and Subscription), or the upgrade and migration procedures that move the platform between schema versions (Upgrade and Migration).

**Governing source.** DEC-3395bc; Infrastructure.

## What the Procedure Produces

A complete deployment cycle produces:

| Artifact | Persistent store | Created by |
|---|---|---|
| Deployed CloudFormation stack (AuthStack in the readiness baseline) | Infrastructure-owned AWS account and region | The `cd-prepare.yml` and `cd-execute.yml` GitHub Actions runs (bc-infra `.github/workflows/`) |
| CDK change set per stack | AWS CloudFormation change-set queue | The change-set creation step in `cd-prepare.yml` |
| Cognito user pool with multi-tenant attributes | Cognito service in `ap-south-1` | `AuthStack` synthesis from `cdk/lib/stacks/auth-stack.ts` |
| SSM parameters for service consumers | AWS Systems Manager parameter store | AuthStack synth-time output |
| GitHub deployment record | The repository's Deployments view | Not re-verified in this change; the file `cd-deploy.yml` that earlier text named is not in bc-infra |

The procedure produces no tenant-side artifacts. Tenant database creation, Connection authoring, and Subscription record activation run from bc-core application code per the Tenant Onboarding sequence.

**Governing source.** Infrastructure.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| GitHub OIDC trust to AWS account `546549546538` | The deploy procedure assumes role `arn:aws:iam::546549546538:role/GitHub-OIDC` via OIDC (`cd-prepare.yml` line 36), and `cd-execute.yml` then chains into the CDK deploy role (lines 29 and 49-51); absence of trust blocks GitHub Actions execution at the assume-role step |
| Two-step deploy gate | Both workflows set `environment:` to their `stage` input (`dev` or `prod`; `cd-prepare.yml` line 41, `cd-execute.yml` line 34) and the file states that required reviewers are not used (`cd-prepare.yml` lines 3-9). The control is the two-step gate: prepare creates change sets only, a person reviews them, then execute applies the same change sets |
| `cdk synth` passes locally and in CI | `ci-validate.yml` runs `cdk synth` against the dev environment and `cdk diff` with replacement guard; a failure here blocks merge |
| Target environment context | `cdk.json` defines `dev` and `stg` under its `stages` key and has no `prod` entry; the deploy definitions `cd-prepare.yml` and `cd-execute.yml` offer `dev` and `prod` as the choice of environment (bc-infra `cdk/cdk.json`; `.github/workflows/cd-prepare.yml` lines 14-18; `cd-execute.yml` lines 12-16) |

A precondition that fails is not bypassed. The OIDC role and the two-step gate (prepare change sets, review, execute the same change sets) are the deploy boundary; manual `aws cloudformation create-change-set` from a developer laptop is not the platform's deployment surface.

**Governing source.** Infrastructure.

## The GitHub Actions Surface

> **Residual risk (audit GAP-009).** The deployment-surface, AuthStack-deployed-footprint, and PlatformInfraStack-dormancy claims in this chapter (and in "Readiness-Baseline Deployment: AuthStack Only" and "Defined But Not Deployed: PlatformInfraStack" below) depend on `platform-infra-stack/` files that were not readable in the platform code/docs gap audit (the GitHub Actions workflow files were re-read from bc-infra on 2026-11-15 and no longer depend on prior grounding). They rest on prior grounding, not on this-pass verification. Treat as unverified until a dedicated readable infra-stack audit confirms the workflow shapes, the deployed stack list, and the README-vs-entry-point drift. Source: `bc-docs/reports/platform-code-doc-gap-report.md` GAP-009.

The platform deployment surface is three GitHub Actions files under bc-infra `.github/workflows/`, read at bc-infra origin/main on 2026-11-15.

| File | Trigger | Effect |
|---|---|---|
| `ci-validate.yml` | All branches and pull requests | Checkout, Node 20, AWS OIDC assume-role, `npm ci`, `cdk synth` against the dev environment, `cdk diff` with replacement guard. Fails the procedure if any REPLACE or Replacement is detected |
| `cd-prepare.yml` | Manual dispatch | Inputs: `stage` (`dev` or `prod`), `stacks` (comma-separated list), `allow_replacements` (`false` or `true`). Runs the replacement guard and creates change sets without executing them |
| `cd-execute.yml` | Manual dispatch | Inputs: `stage` (`dev` or `prod`), `stacks`. Executes the change sets that `cd-prepare.yml` created; a stale or missing change set fails there (`cd-execute.yml` lines 3-7) |

bc-infra at origin/main holds three workflow files: `ci-validate.yml`, `cd-prepare.yml` and `cd-execute.yml`. The files `cd-deploy.yml` and `deploy.yml` that earlier text named are not among them.

The deployment is gated three ways: CI validation must pass on the branch (replacement guard), the change sets must be prepared and reviewed before `cd-execute.yml` applies them, and OIDC trust must be in place for the infrastructure-owned AWS account.

**Governing source.** Infrastructure; bc-infra `.github/workflows/`.

## Readiness-Baseline Deployment: AuthStack Only

The prior-grounded deployed footprint at the time of writing comprises one CDK stack: `AuthStack`. AuthStack provisions the Cognito user pool that bc-core's `CognitoJwtStrategy` validates JWT tokens against, plus the SSM parameters that later services read at deploy time.

The full per-resource breakdown lives in Infrastructure under the deployed-footprint section. This chapter records the deployment-procedural view: AuthStack is reached only through the GitHub Actions surface above; no other path admits Cognito user pool changes to the dev or prod environment.

A historical local Cognito callback is not a reserved frontend service identity per DEC-e50b83. The callback is queued for reconciliation during the next AuthStack change-set window; exact callback values remain Infrastructure-owned.

**Governing source.** Infrastructure; `platform-infra-stack/cdk/lib/stacks/auth-stack.ts`.

## Defined But Not Deployed: PlatformInfraStack

A second stack class `PlatformInfraStack` exists in the repository under `cdk/lib/platform-infra-stack.ts` and `cdk/lib/constructs/` (network, aurora-postgres, demo-lambda, http-api, s3-bucket, ses email-outbox, security-groups, iam-role). The stack class is operational; it would deploy if `cdk/bin/platform-infra.ts` re-instantiated it. Commit `6b01fab` removed the stack from the deployment entry point.

The deployment-procedural consequence is that any resource defined in `PlatformInfraStack` (Aurora PostgreSQL, demo Lambda, HTTP API Gateway v2, secure S3 bucket construct, SES email-outbox construct, VPC with private subnets) is not part of the platform's deployed AWS footprint in the readiness baseline. A future re-instantiation is a deliberate decision recorded in a new commit; the current dormancy is the intentional posture.

The README in `platform-infra-stack` continues to describe `PlatformInfraStack` resources as deployed. The README is aspirational against the current entry point; the deployed truth is AuthStack only.

**Governing source.** `platform-infra-stack/cdk/lib/platform-infra-stack.ts`; `cdk/bin/platform-infra.ts`; `platform-infra-stack/README.md`.

## Development Machine Topology

The development machine of the `dev` environment is fully formalized. Every engineer brings up the same substrate via `bc-core/docker-compose.yml`:

| Service | Container | Host port | Initialization |
|---|---|---|---|
| PostgreSQL | `postgres:17.11-alpine` | 5435 | No init scripts are mounted; the container starts with an empty `bc_platform_dev`, and the platform schema is restored with `npm run db:restore:s3` (bc-core `docker-compose.yml`, comment lines 9-11 and volume comment) |
| Redis | `redis:7.4.7-alpine` | 6379 | None |

The active stack is `docker-compose.yml` (container `bc-postgres`, port 5435). On the development machine the containers are started through `~/bc-stack/up.sh`, which adds `mac-ports.yml` (127.0.0.1-only ports; compose project `bc-core`); see the workstation runbook ([Development Workstation: Mac Mini and Laptop](../development/dev-workstation-mac-mini.md)). The compose file alone publishes both ports on every interface. The former `docker-compose.redesign.yml` / `bc-postgres-redesign` instance is retired.

Services running on the engineer's host:

| Service | Port | Start command |
|---|---|---|
| DevHub (MCP backbone) | 4000 | `npm run dev` from `barecount-devhub` (Node `--watch`) |
| bc-core | 3100 | `npm run start:dev` from `bc-core` (NestJS `--watch` via SWC) |
| bc-portal (customer frontend) | 3000 | `npm run dev` from `bc-portal` |
| bc-admin (admin frontend) | 3010 | `npm run dev` from `bc-admin` |
| bc-ai | none | Local FastAPI service via uvicorn |
| bc-core-dashboard | 4100 | optional, started on demand |

These ports are reserved by DEC-e50b83. No project changes its port without updating the reservation. The current per-port assignment is recorded in CLAUDE.md and in Infrastructure.

The development-machine discipline (per CLAUDE.md): start DevHub first, keep it running for the entire dev session; start application services on demand only; pm2 was removed (DEC supersedes a prior pm2-based service management decision) and each service starts independently in its own repo.

**Governing source.** `bc-core/docker-compose.yml`; CLAUDE.md operational sections; DEC-e50b83.

## Environment Names

There is one list of environment names: `dev`, `stg`, `prod` ([The Definition of Operations](../development/platform-refactor-program/definition-operations.md), section 1; ruling G13). Three further words are not environment names. "Live" describes the served platform inside an environment (see Serve Moves and Live Windows). A "disposable copy" is a restored copy of the databases on other ports, with a build served against it, made for one check and then destroyed; older texts call it a rehearsal, a clone or a kit. `test` is not an environment: it is a suffix that automatic checks give to databases they create and destroy. `NODE_ENV` is a Node.js convention that bc-core reads at run time (`src/main.ts` line 75, used at line 103 to omit the API documentation page when it is `production`; `src/database/served-identity/platform-session-identity.ts` line 52, which refuses a role override when it is `production`). A Vite mode is a setting of bc-admin's build tool (`src/config/env.ts` lines 25-27). Neither is an environment name.

| Environment | Status | Form |
|---|---|---|
| `dev` | The only environment that exists | The development machine (every engineer runs the substrate above; primary platform runtime in the readiness baseline) and the cloud resources named `dev` that serve it. In the cloud, this chapter records one Cognito user pool in account `546549546538`, region `ap-south-1`; the definition of Operations (section 1) says: "Three deployed units carry `dev` in their names, and all three serve the development machine: sign-in, secrets, and the machines that run CI." |
| `stg` | A name kept for a platform hosted in the cloud; not built | `cdk.json` defines `stg` under its `stages` key; it is not built (definition of Operations, section 1; ruling G13) |
| `prod` | A name kept for a platform hosted in the cloud; not built | `cdk.json` has no `prod` entry; the deploy definitions offer `prod` as an input named `stage`; it is not built (definition of Operations, section 1; ruling G13) |

The intent stated in `platform-infra-stack/README.md` (stack policies that restrict destructive prod changes; rollback configuration with CloudWatch alarms requiring a 15-minute monitoring window; GitHub `prod` Environment for approval) is the queued shape for `prod` once the readiness-to-onboard milestone for the first paying tenant lands.

The current posture is intentional during platform development; the cost of maintaining unused prod infrastructure has not been justified. Per DEC-005ea7, when `prod` is built, every tenant operates against that one environment; there are no per-tenant dev or pre-production tiers, and a trial tenant on purchase is deleted and recreated rather than promoted in place.

**Governing source.** Infrastructure; DEC-005ea7; `platform-infra-stack/cdk/cdk.json`.

## Tenant Database Provisioning: Application Code, Not IaC

Tenant database provisioning runs from bc-core application code, not from `platform-infra-stack` IaC. Tenant birth is the governed operator-plane command `npm run tenant:lifecycle -- create` (`bc-core/src/tenant-management/lifecycle/`). The file `bc-core/src/registry/seed/seed-tenant-dbs.ts` is a harness that integration specs use to build throwaway tenants on a disposable cluster; it is not a production path (its header, TSK-dc2d1c). Its function `provisionTenantDb`, per that file:

1. Creates the database `tbc_{slug}_{env}` owned by `bc_tenant_owner` through a maintenance connection, if it does not exist. The suffix is copied from the platform database's name.
2. Applies the ratified tenant skeleton, a digest-pinned copy under `src/registry/seed/tenant-skeleton/`, verbatim under `SET ROLE bc_tenant_owner`. It refuses to apply it to a database that is not named `tbc_*`.
3. Counts the tables in the six schemas `progression`, `fact`, `evidence`, `admin`, `organization` and `tenant_dim`.

The onboarding chapter (`docs/onboarding/tenant-onboarding.md`, line 124) and the platform workflow catalog (`docs/reference/platform-workflow-catalog.md`, lines 45 and 59) still describe the served `POST /tenants` as the entry point. They are not corrected by this change; DEC-4aa1ff says "the served `POST /tenants` stays refused by design".

Dynamic `fact.*` tables are created per activated contract by `SchemaProvisionerModule`. The implementation honors DEC-1918d0 and DEC-771baf: one Tenant DB per tenant, named `tbc_{slug}_dev` for the `dev` environment.

The runtime nature of tenant onboarding is the reason the path lives in application code rather than CDK. A new tenant arrives at runtime; CDK runs at deploy time; the two cadences are different. Recording the gap is the chapter's discipline; closing it (e.g., wrapping the provisioning in a Lambda invoked by an admin API) is queued.

**`TenantProvisioningService` is legacy and is not part of the active path.** A reader inspecting `bc-core/src/tenant-management/tenant-provisioning.service.ts` will see file-header comments and per-method comments (lines 7-16 and 38-64 at the time of writing) describing it as the provisioning entry point that is "called during tenant creation" and as the surface that "creates per-tenant schemas." Those comments are stale relative to the current architecture: the active path is the `tenant:lifecycle` command (above), which creates per-tenant **databases** (one DB per tenant per DEC-1918d0 + DEC-771baf), not per-tenant schemas. The legacy service's schema-provisioning shape predates the per-tenant-DB model and is no longer invoked by tenant creation. The discrepancy is a code-comment-vs-architecture drift, not a runtime divergence — the legacy service has no callers in the active path. Closing the discrepancy is a code-comment cleanup followup that is out of scope for this chapter; the active reading anchored to `src/tenant-management/lifecycle/` is canonical.

**Governing source.** `bc-core/src/tenant-management/lifecycle/`; `bc-core/src/registry/seed/seed-tenant-dbs.ts`; DEC-1918d0; DEC-771baf. Legacy reference: `bc-core/src/tenant-management/tenant-provisioning.service.ts` (no active callers; comment cleanup is queued).

## Per-Hosting-Variant Realization Status

Per DEC-324d9e, the platform recognizes four hosting variants. The deployment-procedural view of each:

| Variant | Realization status |
|---|---|
| AWS Shared | Closest to the `dev` environment; the deployed AuthStack supports the auth boundary; tenant DB lives in shared PostgreSQL infrastructure (Docker Postgres on the development machine in the readiness baseline; an Aurora cluster once a platform is hosted in the cloud under `stg` or `prod`); no per-variant deployment procedure exists yet |
| AWS Separate | Per-tenant dedicated database under platform AWS account; no IaC; no realization |
| BYO-DB | Tenant-managed database in customer infrastructure; no platform-side IaC needed for the database, but the connection-secrets surface, network reachability, and Onboarding Record gate (per DEC-a67518) all need realization beyond their current spec form |
| BC-Agent | Local agent runtime in customer environment; no agent runtime built; no agent-to-platform protocol implemented |

The chapter records this honestly per pattern 81. The hosting-variant inventory authority remains Tenant Lifecycle and Subscription; this chapter records only the deployment-procedural realization status per variant.

**Governing source.** Tenant Lifecycle and Subscription; DEC-324d9e.

## Failure Modes

| Cause | System response |
|---|---|
| `cdk diff` detects a destructive replacement during CI | `ci-validate.yml` fails; the PR cannot merge until the replacement is intentional and `allow_replacements` is set to `true` when `cd-prepare.yml` is run |
| Change set stale or missing at execute | `cd-execute.yml` fails rather than deploying something else (`cd-execute.yml` lines 3-7) |
| Cognito user pool deletion attempted | Removal policy `RETAIN` for prod prevents accidental deletion; for dev the policy is `DESTROY`; deletion of a dev user pool is reversible only by reseeding the pool and rebinding the application clients |
| `aws codeartifact login` token expires (twelve-hour TTL) | `npm ci` rejects with HTTP 401 or 403 in CI and locally; renewal is a manual operation per the CodeArtifact runbook owned by Build and Release (queued chapter) |
| The `dev` Postgres container fails to start | bc-core, DevHub document scans, and bc-pg-mcp reject database connections; no platform request can complete until the container is healthy |
| `dev` Postgres data volume corruption | Stop and assess; do not remove the volume. The one data volume (`redesign_data` in the compose file) holds `bc_platform_dev`, every `tbc_*_dev` tenant database and `bc_sdg` (bc-core `docker-compose.yml`, the comment above the volume mount), while `npm run db:restore:s3` restores `bc_platform_dev` only (bc-core `package.json`). Removing the volume would discard the tenant databases, and the platform restore does not bring them back. Preserve the volume where possible. Any destructive removal needs a verified recoverable copy of every affected database and a governed recovery procedure first, and is the operator's act under its own recorded grant |
| `PlatformInfraStack` re-instantiation drifts from dormant code | The stack would deploy with the configuration as-coded in the readiness baseline (Aurora `t3.micro`, Lambda demo, single VPC); a deployment without a pre-deploy review of the dormant code may produce a configuration that no longer matches the current architectural intent |

**Governing source.** Infrastructure; `platform-infra-stack/`; `bc-core/docker-compose.yml`.

## Drift Inventory

| Drift item | Form |
|---|---|
| README aspirational against the deployed state | `platform-infra-stack/README.md` describes `PlatformInfraStack` resources as deployed; the dormant entry point makes the description aspirational. README reconciliation is queued |
| `prod` and `stg` environments not built | `cdk.json` defines `dev` and `stg` and no `prod`; the deploy definitions offer `dev` and `prod`; neither `stg` nor `prod` is built (definition of Operations, section 1) |
| Historical Cognito local callback | Prior-grounded AuthStack callback drift; exact values are Infrastructure-owned and queued for the next AuthStack change-set |
| Tenant provisioning is application-code, not IaC | `tenant:lifecycle` runs from bc-core (`seed-tenant-dbs.ts` is a test harness); no Lambda or admin-API wrapper; the runtime cadence of tenant onboarding makes pure-IaC awkward, so the gap is intentional but recorded |
| BC-Agent and BYO-DB realization absent | The two non-AWS hosting variants have no platform-side deployment artifacts; both are aspirational against the current AWS-only posture |
| `bc-ai` has no cloud deployment | Local FastAPI service; no Dockerfile, no Lambda handler, no ECS task found in the readable repo; production AI surface depends on replacing the local-service posture |
| GitHub OIDC trust assumed | The trust policy on `GitHub-OIDC` is configured at the AWS account level; if the role's trust drifts, all CI validation and deployment fails closed |

**Governing source.** `platform-infra-stack/`; `bc-core/`; `bc-ai/`; Infrastructure.

## Boundary with Other Operations Chapters

| Chapter | Relationship |
|---|---|
| Tenant Lifecycle and Subscription | Owns the four hosting variants and their commercial categorization; this chapter records each variant's deployment realization status |
| Security Operations | Owns Cognito user pool operational governance, credential rotation, secret management; this chapter records the deploy-time provisioning of the user pool, not its operational discipline |
| Upgrade and Migration | Owns the procedures for moving the platform between schema versions, the clean-slate path, and the source-catalog export per DEC-3b86ea; this chapter records the deploy-time DDL application, not the upgrade procedure |
| Observability and Telemetry | Owns log groups, metrics, traces, alarms, dashboards; this chapter records the AuthStack and HTTP API access log retention as a deploy-time configuration |
| Performance and Scale | Independent at the deploy layer; this chapter records the deploy-layer shape without claiming current performance |
| Incident and Change Management | Owns the change-record substrate this chapter's deploys produce; deploy events are governed-change events the substrate records |
| Support and Escalation | Independent at the deploy layer |

**Governing source.** The owning Operations chapters; DEC-3395bc.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-1918d0 | Establishes deployment and database architecture; the two-database split is the operational reality the deployment procedure honors |
| DEC-771baf | Establishes tenant database topology; one tenant database per tenant; the platform-tenant dependency is one-way |
| DEC-005ea7 | Establishes single production environment per tenant; no per-tenant dev or pre-production tiers; trial-to-purchase is delete-and-recreate, not promotion |
| DEC-e50b83 | Establishes the master port reservation; local development binds the platform's services on the reserved ports |
| DEC-324d9e | Establishes the four hosting variants whose deployment realization this chapter records |
| DEC-f02230 | Establishes the tenant DB schema organization the deploy-time DDL application produces |

**Governing source.** Decisions: ADR Registry.

### Additional governing decisions

| Decision | Operational effect |
| --- | --- |
| DEC-3b86ea | Establishes the Operations section name and explicitly moves Clean Slate Migration into Upgrade and Migration; this chapter's deployment-procedural view honors the section scope |
| DEC-a67518 | Establishes the Tenant Onboarding Gate (checklist-based readiness for BYO-DB and BC-Agent tiers); deployment topology defers the gate's procedural shape to Tenant Onboarding while honoring the gate as a prerequisite for the two non-AWS hosting variants |

## References

- Infrastructure
- Backend Services
- Auxiliary Services
- Tenant Lifecycle and Subscription
- Security Operations
- Upgrade and Migration
- Observability and Telemetry
- Performance and Scale
- Incident and Change Management
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-005ea7: Single production environment per tenant
- DEC-e50b83: Master port reservation
- DEC-324d9e: Stripe billing; four hosting variants
- DEC-f02230: Tenant DB schema organization
- bc-infra `.github/workflows/ci-validate.yml`
- bc-infra `.github/workflows/cd-prepare.yml` and `cd-execute.yml`
- `platform-infra-stack/cdk/lib/stacks/auth-stack.ts`
- `bc-core/src/tenant-management/lifecycle/`
- `bc-core/src/registry/seed/seed-tenant-dbs.ts`
- DEC-3395bc: Operations





