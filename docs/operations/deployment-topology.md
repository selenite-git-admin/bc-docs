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

This chapter records the operational view of where the platform deploys, how the deployment procedure runs, what is deployed in the readiness baseline, and what is queued behind future formalization. It states the AWS account scope, the GitHub OIDC deployment role, the CI validate and CD deploy procedure shape, the AuthStack and dormant PlatformInfraStack split, the local development substrate every engineer runs, the local plus AWS dev plus aspirational prod environment posture, and the per-hosting-variant deployment realization status. It records the boundary between Deployment Topology and the Infrastructure chapter that catalogs the deployable resources themselves. It records the as-built drift between the procedure and the platform's current deployment state.

This chapter does not redefine the AWS account, region, or resource inventory (Infrastructure), the per-service deployable shape (Backend Services, Auxiliary Services), the hosting-variant commercial categorization (Tenant Lifecycle and Subscription), or the upgrade and migration procedures that move the platform between schema versions (Upgrade and Migration).

**Governing source.** outline.md §4.7; Infrastructure.

## What the Procedure Produces

A complete deployment cycle produces:

| Artifact | Persistent store | Created by |
|---|---|---|
| Deployed CloudFormation stack (AuthStack in the readiness baseline) | Infrastructure-owned AWS account and region | Prior-grounded `cd-deploy.yml` GitHub Actions run |
| CDK change set per stack | AWS CloudFormation change-set queue | The change-set creation step in `cd-deploy.yml` |
| Cognito user pool with multi-tenant attributes | Cognito service in `ap-south-1` | `AuthStack` synthesis from `cdk/lib/stacks/auth-stack.ts` |
| SSM parameters for service consumers | AWS Systems Manager parameter store | AuthStack synth-time output |
| GitHub deployment record | The repository's Deployments view | `cd-deploy.yml` post-deploy step |

The procedure produces no tenant-side artifacts. Tenant database creation, Connection authoring, and Subscription record activation run from bc-core application code per the Tenant Onboarding sequence.

**Governing source.** Infrastructure.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| GitHub OIDC trust to AWS account `546549546538` | The deploy procedure assumes role `arn:aws:iam::<ACCOUNT>:role/GitHubCICDInfraRole` via OIDC; absence of trust blocks GitHub Actions execution at the assume-role step |
| Approved branch and Environment gate in GitHub | `cd-deploy.yml` requires GitHub Environment approval (the `dev` or `prod` environment) before change-set execution |
| `cdk synth` passes locally and in CI | `ci-validate.yml` runs `cdk synth` against the dev environment and `cdk diff` with replacement guard; a failure here blocks merge |
| Target environment context | `cdk.json` defines `dev` only; `prod` is referenced by code paths and CI inputs but has no committed configuration in the readiness baseline |

A precondition that fails is not bypassed. The OIDC role and the GitHub Environment approval are the deploy boundary; manual `aws cloudformation create-change-set` from a developer laptop is not the platform's deployment surface.

**Governing source.** Infrastructure.

## The GitHub Actions Surface

> **Residual risk (audit GAP-009).** The deployment-surface, AuthStack-deployed-footprint, and PlatformInfraStack-dormancy claims in this chapter (and in "Readiness-Baseline Deployment: AuthStack Only" and "Defined But Not Deployed: PlatformInfraStack" below) depend on `platform-infra-stack/` files that were not readable in the platform code/docs gap audit. They rest on prior grounding, not on this-pass verification. Treat as unverified until a dedicated readable infra-stack audit confirms the workflow shapes, the deployed stack list, and the README-vs-entry-point drift. Source: `bc-docs/reports/platform-code-doc-gap-report.md` GAP-009.

The platform deployment surface is described by prior grounding as two GitHub Actions files under `platform-infra-stack/.github/workflows/`; that repository was not readable in this review.

| File | Trigger | Effect |
|---|---|---|
| `ci-validate.yml` | All branches and pull requests | Checkout, Node 20, AWS OIDC assume-role, `npm ci`, `cdk synth` against the dev environment, `cdk diff` with replacement guard. Fails the procedure if any REPLACE or Replacement is detected |
| `cd-deploy.yml` | Manual dispatch | Inputs: target environment (`dev` or `prod`), stacks (comma-separated list), `allow_replacements` (`Y` or `N`). Creates change sets without execute, then executes change sets after GitHub Environment approval. Sequential stack deployment |

A third GitHub Actions file `deploy.yml` is present in the repository; it is a precursor to the current `cd-deploy.yml` shape and is not the active deployment surface.

The deployment is gated three ways: CI validation must pass on the branch (replacement guard), GitHub Environment approval must land before change-set execution, and OIDC trust must be in place for the infrastructure-owned AWS account.

**Governing source.** Infrastructure; prior-grounded `platform-infra-stack` GitHub Actions files (repo not readable in this review).

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

## Local Development Topology

The local development environment is fully formalized. Every engineer brings up the same substrate via `bc-core/docker-compose.yml`:

| Service | Container | Host port | Initialization |
|---|---|---|---|
| PostgreSQL | `postgres:17.8-alpine` | 5434 | Three DDL files in `bc-core/docker/redesign/` mount into `/docker-entrypoint-initdb.d/` and run on first start |
| Redis | `redis:7.4.7-alpine` | 6379 | None |

A parallel `docker-compose.redesign.yml` brings up an isolated PostgreSQL on port 5435 with the same DDL files (container name `bc-postgres-redesign`); the two compose files are not run concurrently in normal operation.

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

The local-development discipline (per CLAUDE.md): start DevHub first, keep it running for the entire dev session; start application services on demand only; pm2 was removed (DEC supersedes a prior pm2-based service management decision) and each service starts independently in its own repo.

**Governing source.** `bc-core/docker-compose.yml`; `bc-core/docker/redesign/`; CLAUDE.md operational sections; DEC-e50b83.

## Environment Posture: Local plus dev plus Aspirational prod

The platform operates against three environment postures.

| Posture | Status | Form |
|---|---|---|
| Local | Fully formalized | Every engineer runs the substrate above; primary platform runtime in the readiness baseline |
| AWS `dev` | Partial; AuthStack only | One Cognito user pool exists in account `546549546538`, region `ap-south-1`; no other deployed AWS infrastructure |
| AWS `prod` | Aspirational | `cdk.json` defines `dev` only; `prod` is referenced as a context value at deploy time and the GitHub `prod` Environment exists for approval gates; no `prod` deployment has occurred |

The intent stated in `platform-infra-stack/README.md` (stack policies that restrict destructive prod changes; rollback configuration with CloudWatch alarms requiring a 15-minute monitoring window; GitHub `prod` Environment for approval) is the queued shape for prod once the readiness-to-onboard milestone for the first paying tenant lands.

The current posture is intentional during platform development; the cost of maintaining unused prod infrastructure has not been justified. Per DEC-005ea7, when prod arrives, every tenant operates against one production environment; there are no per-tenant dev or pre-production tiers, and a trial tenant on purchase is deleted and recreated rather than promoted in place.

**Governing source.** Infrastructure; DEC-005ea7; `platform-infra-stack/cdk/cdk.json`.

## Tenant Database Provisioning: Application Code, Not IaC

Tenant database provisioning runs from bc-core application code, not from `platform-infra-stack` IaC. The active path is `bc-core/src/registry/seed/seed-tenant-dbs.ts`. For each tenant, the script:

1. Inserts the tenant identity row into `tenant.tenants` in the platform database with slug, schema name, and status.
2. Issues `CREATE DATABASE tbc_{slug}_{env} OWNER barecount` against the PostgreSQL instance, producing a separate per-tenant database.
3. Reads `bc-core/docker/redesign/03-tenant-db.sql` and applies it to the new database via the `postgres.js` `sql.unsafe()` driver path; psql meta-commands (`\connect`, `\c`) are stripped so the same DDL applies to any tenant database the connection targets.

This produces the seven per-tenant schemas (`envelope`, `progression`, `fact`, `evidence`, `admin`, `organization`, `tenant_dim`); dynamic `fact.*` tables are created per activated contract by `SchemaProvisionerModule`. The implementation honors DEC-1918d0 and DEC-771baf: one Tenant DB per tenant, named `tbc_{slug}_dev` for the dev environment.

The runtime nature of tenant onboarding is the reason the path lives in application code rather than CDK. A new tenant arrives at runtime; CDK runs at deploy time; the two cadences are different. Recording the gap is the chapter's discipline; closing it (e.g., wrapping the provisioning in a Lambda invoked by an admin API) is queued.

**`TenantProvisioningService` is legacy and is not part of the active path.** A reader inspecting `bc-core/src/tenant-management/tenant-provisioning.service.ts` will see file-header comments and per-method comments (lines 7-16 and 38-64 at the time of writing) describing it as the provisioning entry point that is "called during tenant creation" and as the surface that "creates per-tenant schemas." Those comments are stale relative to the current architecture: the active path is `seed-tenant-dbs.ts` (above), which creates per-tenant **databases** (one DB per tenant per DEC-1918d0 + DEC-771baf), not per-tenant schemas. The legacy service's schema-provisioning shape predates the per-tenant-DB model and is no longer invoked by the tenant-creation flow. The discrepancy is a code-comment-vs-architecture drift, not a runtime divergence — the legacy service has no callers in the active flow. Closing the discrepancy is a code-comment cleanup followup that is out of scope for this chapter; the active reading anchored to `seed-tenant-dbs.ts` and `03-tenant-db.sql` is canonical.

**Governing source.** `bc-core/src/registry/seed/seed-tenant-dbs.ts`; `bc-core/docker/redesign/03-tenant-db.sql`; DEC-1918d0; DEC-771baf. Legacy reference: `bc-core/src/tenant-management/tenant-provisioning.service.ts` (no active callers; comment cleanup is queued).

## Per-Hosting-Variant Realization Status

Per DEC-324d9e, the platform recognizes four hosting variants. The deployment-procedural view of each:

| Variant | Realization status |
|---|---|
| AWS Shared | Closest to the dev posture; the deployed AuthStack supports the auth boundary; tenant DB lives in shared PostgreSQL infrastructure (local Docker Postgres in the readiness baseline; Aurora cluster in a future prod-AWS posture); no per-variant deployment procedure exists yet |
| AWS Separate | Per-tenant dedicated database under platform AWS account; no IaC; no realization |
| BYO-DB | Tenant-managed database in customer infrastructure; no platform-side IaC needed for the database, but the connection-secrets surface, network reachability, and Onboarding Record gate (per DEC-a67518) all need realization beyond their current spec form |
| BC-Agent | Local agent runtime in customer environment; no agent runtime built; no agent-to-platform protocol implemented |

The chapter records this honestly per pattern 81. The hosting-variant inventory authority remains Tenant Lifecycle and Subscription; this chapter records only the deployment-procedural realization status per variant.

**Governing source.** Tenant Lifecycle and Subscription; DEC-324d9e.

## Failure Modes

| Cause | System response |
|---|---|
| `cdk diff` detects a destructive replacement during CI | `ci-validate.yml` fails; the PR cannot merge until the replacement is intentional and `allow_replacements=Y` is supplied at deploy time |
| GitHub Environment approval not granted on deploy | `cd-deploy.yml` blocks at the change-set execution step; the change set remains uncreated until approval lands |
| Cognito user pool deletion attempted | Removal policy `RETAIN` for prod prevents accidental deletion; for dev the policy is `DESTROY`; deletion of a dev user pool is reversible only by reseeding the pool and rebinding the application clients |
| `aws codeartifact login` token expires (twelve-hour TTL) | `npm ci` rejects with HTTP 401 or 403 in CI and locally; renewal is a manual operation per the CodeArtifact runbook owned by Build and Release (queued chapter) |
| Local Postgres container fails to start | bc-core, DevHub document scans, and bc-pg-mcp reject database connections; no platform request can complete until the container is healthy |
| Local Postgres data volume corruption | The `postgres_data` named volume must be removed and the container restarted; the three DDL files re-initialize the database on first start |
| `PlatformInfraStack` re-instantiation drifts from dormant code | The stack would deploy with the configuration as-coded in the readiness baseline (Aurora `t3.micro`, Lambda demo, single VPC); a deployment without a pre-deploy review of the dormant code may produce a configuration that no longer matches the current architectural intent |

**Governing source.** Infrastructure; `platform-infra-stack/`; `bc-core/docker-compose.yml`.

## Drift Inventory

| Drift item | Form |
|---|---|
| README aspirational against the deployed state | `platform-infra-stack/README.md` describes `PlatformInfraStack` resources as deployed; the dormant entry point makes the description aspirational. README reconciliation is queued |
| `prod` environment never formalized | `cdk.json` defines `dev` only; the `prod` Environment exists in GitHub for approval gates; no committed `prod` CDK config; no `prod` deployment |
| Historical Cognito local callback | Prior-grounded AuthStack callback drift; exact values are Infrastructure-owned and queued for the next AuthStack change-set |
| Tenant provisioning is application-code, not IaC | `seed-tenant-dbs.ts` runs from bc-core; no Lambda or admin-API wrapper; the runtime cadence of tenant onboarding makes pure-IaC awkward, so the gap is intentional but recorded |
| BC-Agent and BYO-DB realization absent | The two non-AWS hosting variants have no platform-side deployment artifacts; both are aspirational against the current AWS-only posture |
| `bc-ai` has no cloud deployment | Local FastAPI service; no Dockerfile, no Lambda handler, no ECS task found in the readable repo; production AI surface depends on replacing the local-service posture |
| GitHub OIDC trust assumed | The trust policy on `GitHubCICDInfraRole` is configured at the AWS account level; if the role's trust drifts, all CI validation and deployment fails closed |

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

**Governing source.** The owning Operations chapters; outline.md §4.7.

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
- `platform-infra-stack/.github/workflows/ci-validate.yml` (prior-grounded; repo not readable in this review)
- `platform-infra-stack/.github/workflows/cd-deploy.yml` (prior-grounded; repo not readable in this review)
- `platform-infra-stack/cdk/lib/stacks/auth-stack.ts`
- `bc-core/src/registry/seed/seed-tenant-dbs.ts`
- `bc-core/docker/redesign/03-tenant-db.sql`
- outline.md §4.7: Operations





