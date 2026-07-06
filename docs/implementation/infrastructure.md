---
id: infrastructure
order: 20
title: "Infrastructure"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-authority-model, operating-model-overview, architecture, backend-services, internal-modules, auxiliary-services]
governing_sources:
  - Foundation
  - The Authority Model
  - Operating Model
  - Architecture
  - Backend Services
  - Internal Modules
  - Auxiliary Services
governing_adrs:
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules)
  - DEC-771baf (Tenant database topology; platform-tenant one-way dependency)
  - DEC-e50b83 (Master port reservation)
  - DEC-324d9e (Subscription tiers and hosting variants)
  - DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact)
  - DEC-c06f41 (Spine expansion to eight sections plus home)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Infrastructure

## Scope

This chapter records where the BareCount platform runs in the readiness baseline: the AWS account it deploys into, the region and profile that bind it, the local development infrastructure that supports day-to-day engineering, and an explicit accounting of what is deployed, what is defined in infrastructure-as-code but not deployed, what is not in infrastructure-as-code at all, and what was never formalized. The chapter records reality and the gaps; it does not describe an aspirational deployed topology.

This chapter sits between Auxiliary Services and Data Model and Schema. Auxiliary Services records the smaller deployables; Data Model and Schema enumerates the table and column shape that the databases described here host. The hosting-variant inventory (the four variants per DEC-324d9e: AWS Shared, AWS Separate, BYO-DB, BC-Agent) is owned by Tenant Lifecycle and Subscription in the Operations section per the variant-authoring rule; this chapter records only the architectural invariants every variant must preserve and notes the readiness-baseline per-variant IaC realization status.

This chapter does not redefine Foundation invariants, the Authority Model, or the Architecture chapter's commitments. It does not enumerate the tenant database schema (deferred to Data Model and Schema), the per-environment deployment SOP (deferred to Deployment Topology in the Operations section), the hosting variant inventory (deferred to Tenant Lifecycle and Subscription), the security operations procedure (deferred to Security Operations), or the per-service deployment shape that lives in Backend Services and Auxiliary Services.

**Governing source.** Architecture; Backend Services; Auxiliary Services; outline.md §4.3.

## AWS Account, Region, Profile

| Property | Value | Source |
|---|---|---|
| AWS account | 546549546538 | `cdk/cdk.context.json` (availability-zones cache) |
| Region | `ap-south-1` (Asia Pacific, Mumbai) | `cdk/cdk.json`; CI workflows |
| Local CLI profile | `barecount` | CLAUDE.md operational rule; not referenced in IaC |
| Deployment auth | GitHub OIDC role `arn:aws:iam::<ACCOUNT>:role/GitHubCICDInfraRole` | `.github/workflows/cd-deploy.yml` |

The `barecount` profile is a local CLI convenience for engineers running `aws codeartifact login` and similar manual operations. The deployment workflow does not use the named profile; it uses GitHub OIDC to assume a role inside the AWS account, which removes the need for long-lived credentials in CI.

**Governing source.** `platform-infra-stack` repository; CLAUDE.md.

## Deployed Baseline

The platform's AWS deployment in the readiness baseline comprises one CDK stack: AuthStack. AuthStack provisions the Cognito user pool and a single web application client.

| Resource | Detail |
|---|---|
| Cognito user pool | `cognito-pool-platform-dev-aps1`; admin-provisioned only, no self-signup; email-based sign-in; password policy minimum 12 characters with complexity; MFA optional in dev and required in prod |
| Multi-tenant custom attributes | `custom:tenant_id`, `custom:roles`, `custom:display_name` |
| Token validity | AuthStack-configured access, ID, and renewal-token windows |
| Web app client | `cognito-client-platform-dev-aps1-web`; SRP plus AdminInitiateAuth; no client secret (public SPA client); OAuth callbacks to `http://localhost:5173` and `http://localhost:3000` |
| SSM parameters published | `/bc/dev/auth/cognito-user-pool-id`, `/bc/dev/auth/cognito-client-id`, `/bc/dev/auth/cognito-issuer-url` |
| Issuer URL | `https://cognito-idp.ap-south-1.amazonaws.com/{userPoolId}` |
| JWKS URL | `https://cognito-idp.ap-south-1.amazonaws.com/{userPoolId}/.well-known/jwks.json` |
| CDK bootstrap S3 bucket | `cdk-hnb659fds-assets-546549546538-ap-south-1` (CDK asset staging) |

bc-core's CognitoJwtStrategy validates incoming tokens against the JWKS URL listed above. The user pool ID and client ID are read from SSM at deploy time and injected into bc-core's environment configuration.

The `localhost:5173` callback is a historical development callback for a Vite-hosted frontend and is not a reserved service identity in DEC-e50b83. The reserved frontend service identities remain in the 3000 to 3099 range; the callback should be removed or replaced by the reserved frontend port when the Cognito app client is reconciled with the current port reservation.

**Governing source.** `platform-infra-stack/cdk/lib/constructs/cognito-user-pool.ts`; `cdk/lib/auth-stack.ts`.

## Defined But Not Deployed

The repository defines a second CDK stack, `PlatformInfraStack`, that would provision the platform's compute and database infrastructure. The stack class is preserved in code but was removed from the deployment entry point in commit `6b01fab`. It is dormant.

| Resource (defined, not deployed) | Configured shape |
|---|---|
| Network (VPC) | Private VPC across ap-south-1a and ap-south-1b for dev; isolated subnets; no NAT by default; VPC traffic logs to CloudWatch |
| Aurora PostgreSQL | PostgreSQL engine for the dormant platform database shape; dev-sized instance class; database name `platform`; IAM authentication enabled; KMS encryption at rest; secret rotation, backup retention, and removal policies vary by environment |
| Demo Lambda | Node.js runtime; bounded memory and timeout; placed in PRIVATE_ISOLATED subnets; restricted-egress security group; explicit CloudWatch log group |
| HTTP API (API Gateway v2) | Single route `GET /ping` with optional IAM authorization; access logs to CloudWatch |
| S3 SecureBucket construct | Encryption enforced; SSL-only access policy; not instantiated by any deployed stack |
| SES email outbox construct | Defined; not instantiated by any deployed stack |

The `PlatformInfraStack` code is operational and would deploy if the entry point were restored, but no commit since `6b01fab` has done so. The README continues to describe these resources as deployed; the description is aspirational against the deployment entry point.

**Governing source.** `platform-infra-stack/cdk/lib/platform-infra-stack.ts`; `cdk/bin/platform-infra.ts`.

## Not In Infrastructure-As-Code

Several resources the platform depends on are not provisioned by `platform-infra-stack`. Each is recorded here as a gap; the platform runs against the resource via account-level enablement, application code, or local-developer configuration.

| Resource | Where it lives | Gap |
|---|---|---|
| Bedrock model access | AWS account-level enablement; bc-ai uses inference profile IDs (`apac.*` and `global.*` prefixes) via boto3 | No CDK construct provisions Bedrock model access policies, inference profile bindings, or per-model IAM grants |
| Redis (cloud) | Local-only via `docker-compose.yml` on port 6379; no cloud Redis provisioned | No ElastiCache or self-managed Redis in IaC; bc-core's `REDIS_URL` for non-local environments is undefined |
| S3 buckets the platform uses | The `SecureBucket` construct exists but instantiates no buckets; bc-core's S3 archiver targets bucket names supplied via env vars | No CDK creates the evidence-archive bucket, the SAP scraper bucket, or the typed-fact archive bucket |
| Tenant DB provisioning | bc-core application code (`src/registry/seed/seed-tenant-dbs.ts`); not in IaC | Provisioning honors the two-database architecture per DEC-1918d0: each tenant gets a separate `tbc_{slug}_dev` database created via `CREATE DATABASE` with `docker/redesign/03-tenant-db.sql` applied. The gap recorded here is only that provisioning runs from application code rather than IaC, which is intentional given the runtime nature of tenant onboarding |
| bc-ai cloud deployment | Local-only via uvicorn under pm2 on port 4300; no Dockerfile, no Lambda handler, no ECS task | bc-ai has no cloud deployment posture; production AI surface depends on the local-pm2 model not being the long-term posture |

**Governing source.** `platform-infra-stack/cdk/lib/`; `bc-core/src/registry/seed/seed-tenant-dbs.ts`; `bc-core/docker/redesign/03-tenant-db.sql`; `bc-ai/main.py`.

## Local Development Infrastructure

The local development environment is fully formalized and serves as the primary platform runtime in the readiness baseline. `bc-core/docker-compose.yml` brings up two containerized services that bc-core, DevHub, bc-pg-mcp, and bc-ai consume.

| Service | Image | Port | Volume | Initialization |
|---|---|---|---|---|
| PostgreSQL | `postgres:17.8-alpine` | 5434 (host) to 5432 (container) | `postgres_data:/var/lib/postgresql/data` | Three DDL files in `bc-core/docker/redesign/` mount into `/docker-entrypoint-initdb.d/` and run on first start |
| Redis | `redis:7.4.7-alpine` | 6379 | `redis_data:/data` | None |

The PostgreSQL container creates the `bc_platform` database with user `barecount` and password `barecount_dev` on first start. The three DDL files initialize the schema:

| DDL file | Effect |
|---|---|
| `01-platform-schemas.sql` | Enables `pgcrypto`; creates the platform schema set |
| `02-platform-tables.sql` | Creates the platform table set; generated from the bc-docs architecture DBML; ISO 11179 snake_case naming throughout |
| `03-tenant-db.sql` | Creates the tenant schema set plus fixed tables for the tenant database pattern; dynamic fact tables are created per contract activation by the SchemaProvisionerModule |

A parallel `docker-compose.redesign.yml` exists for schema redesign work; it brings up an isolated PostgreSQL instance on port 5435 with the same DDL files, container name `bc-postgres-redesign`. The two compose files are not run concurrently in normal operation.

The DDL files are the authoritative schema source per CLAUDE.md; the Drizzle schema definitions in `bc-core/src/database/schema/` mirror them and are reconciled at build time.

**Governing source.** `bc-core/docker-compose.yml`; `bc-core/docker/redesign/01-platform-schemas.sql`; `bc-core/docker/redesign/02-platform-tables.sql`; `bc-core/docker/redesign/03-tenant-db.sql`.

## bc-ai Local Runtime

bc-ai runs locally under uvicorn on port 4300, supervised by pm2. The runtime stack is Python 3.12 with FastAPI, plus Anthropic SDK, Google Gemini SDK, and boto3 for Bedrock. There is no cloud deployment posture for bc-ai at the time of writing.

| Property | Value |
|---|---|
| Runtime | Python 3.12 with FastAPI; uvicorn on port 4300 |
| Supervision | pm2 (local development) |
| Bedrock client | boto3 with `Session(profile_name='barecount', region_name='ap-south-1').client('bedrock-runtime')`; uses inference profile IDs (`apac.anthropic.claude-sonnet-4-...`, `global.anthropic.claude-haiku-4-5-...`, `apac.amazon.nova-pro-v1:0`, etc.); no raw model IDs |
| Anthropic SDK direct | `anthropic.Anthropic(api_key=settings.anthropic_api_key)`; routes used when `entry.provider == "anthropic-api"`; bare model IDs (correct for the Anthropic SDK path) |
| Gemini SDK | `google.generativeai`; default model `gemini-2.5-flash`; the auditor agent is configured with `gemini-2.5-pro` |
| Agents registered | 12 maker-checker-gate triplets (bf-dedup, bf-pii-classify, bo-suggest, bo-dedup, field-map, metric-trace, eval-advise, cc-field-audit, chain-audit, table-verify, source-verify, metric-verify); 8 housekeeping agents (DocStaleness, SessionHygiene, TaskTriage, NcAging, RegistryRefresh, RiskReview, QaPatrol, MkDocsMaintainer) |
| Budget controls | `BUDGET_DAILY_LIMIT=10.0` USD and `BUDGET_ALERT_THRESHOLD=8.0` USD per `config.py` |
| Cloud deployment | None at the time of writing |

The model registry defaults are heavily weighted toward Gemini at the time of writing (with a comment in `registry.py` noting "Nova-only until Anthropic marketplace is resolved"); the AI Architecture chapter in the AI section will record the routing semantics in detail.

**Governing source.** `bc-ai/pyproject.toml`; `bc-ai/clients/bedrock.py`; `bc-ai/clients/anthropic_client.py`; `bc-ai/clients/gemini.py`; `bc-ai/agents/__init__.py`; `bc-ai/housekeeping/__init__.py`.

## Tenant Database Provisioning

Tenant provisioning runs from bc-core application code, not from infrastructure-as-code. The active provisioning path is `src/registry/seed/seed-tenant-dbs.ts` (rewritten in commit `489a600` per D368). For each new tenant, the script:

1. Inserts the tenant identity row into `tenant.tenants` in the platform database (recording slug, schema name, status).
2. Issues `CREATE DATABASE tbc_{slug}_{env} OWNER barecount` against the PostgreSQL instance, producing a separate per-tenant database.
3. Reads `docker/redesign/03-tenant-db.sql` (the single source of truth for the tenant database schema) and applies it to the new database via the `postgres.js` `sql.unsafe()` driver path. The script strips psql meta-commands (`\connect`, `\c`) so the same DDL file can be applied to any tenant database the connection targets.

This produces the seven per-tenant schemas (envelope, progression, fact, evidence, admin, organization, tenant_dim) plus the fixed tables across them; dynamic `fact.*` tables are created per activated contract by SchemaProvisionerModule. The implementation honors the two-database architectural commitment per DEC-1918d0 and DEC-771baf: one Tenant DB per tenant, named `tbc_{slug}_dev` for the dev environment.

The active deployment at the time of writing has one tenant: `sandbox1`. The corresponding database `tbc_sandbox1_dev` exists in the local PostgreSQL instance and serves as the development and test target for D369 M4.2e progression-table read migration and related work.

A legacy schema-per-tenant path exists in `src/tenant-management/tenant-provisioning.service.ts` (per D084 and D087); this file remains in the repository but is not the active tenant-database provisioning path under D368. New tenant onboarding goes through `seed-tenant-dbs.ts` and the `scripts/provision-tenant.mjs` wrapper.

**Governing source.** `bc-core/src/registry/seed/seed-tenant-dbs.ts`; commit `489a600`; DEC-1918d0; DEC-771baf.

## Hosting Variants

The four hosting variants per DEC-324d9e (AWS Shared, AWS Separate, BYO-DB, BC-Agent) are commercial and operational categories owned by Tenant Lifecycle and Subscription. Each variant declares a different residency model, a different operator-responsibility model, and a different commercial categorization.

The chapter that authors the variants holds the inventory. This chapter records only the architectural invariants every variant must preserve once its IaC realization exists:

| Invariant | What it requires |
|---|---|
| Execution spine | The four boundary acts produce the same authoritative state regardless of where bc-core runs |
| Two-database split | Platform definitions and tenant data remain separate physical scopes; a hosting variant may move where a scope lives, but it cannot collapse the two scopes into one authority domain |
| Auth boundary | Cognito JWT validation against the issuer JWKS remains the request boundary unless a later governed security architecture records an equivalent boundary |
| Proof emission | Evidence and Lineage are emitted at the same proof-emitting acts regardless of hosting variant |
| Contract reference | Runtime acts use explicit bound contract versions regardless of hosting variant |

At the time of writing, no hosting variant has committed IaC. The AWS Shared variant most closely matches the dev environment that AuthStack populates, but no dev tenant has been onboarded against the deployed Cognito user pool through the full provisioning sequence in production AWS.

**Governing source.** Architecture; DEC-324d9e.

## Staging and Production Environments

Staging and production environments were never formalized. `cdk/cdk.json` defines `dev` only. The `prod` environment value is referenced in code paths and CI workflow inputs but exists only as a runtime CDK context value supplied at deploy time, with no committed configuration. The README documents prod guardrails (stack policies that restrict destructive changes; rollback configuration with CloudWatch alarms requiring a minimum 15-minute monitoring window) and the GitHub `prod` environment exists for approval gates, but no prod CDK deployment has occurred.

The current state is intentional during platform development; no production tenant has been onboarded, and the cost of maintaining unused prod infrastructure has not been justified. Formalization of staging and production environments is queued behind the readiness-to-onboard milestone for the first paying tenant; until then, the deployment posture is dev-only.

**Governing source.** `platform-infra-stack/cdk/cdk.json`; `platform-infra-stack/README.md`.

## Deployment Workflow

The deployment workflow targets only AuthStack at the time of writing.

| Phase | Workflow | Trigger | Effect |
|---|---|---|---|
| Validation | `.github/workflows/ci-validate.yml` | All branches and pull requests | Checkout, Node 20, AWS OIDC assume-role, `npm ci`, `cdk synth` against the dev environment, `cdk diff` with replacement guard. Fails the workflow if any REPLACE or Replacement is detected |
| Deploy | `.github/workflows/cd-deploy.yml` | Manual `workflow_dispatch` | Inputs: target environment (dev or prod), stacks (comma-separated list), allow_replacements (Y or N). Creates change sets without execute, then executes change sets after GitHub Environment approval. Sequential stack deployment |

The deployment role is `arn:aws:iam::<ACCOUNT_ID>:role/GitHubCICDInfraRole`, granted via GitHub OIDC. No long-lived AWS credentials are stored in the repository.

**Governing source.** `platform-infra-stack/.github/workflows/ci-validate.yml`; `.github/workflows/cd-deploy.yml`.

## Failure Modes

| Cause | System response |
|---|---|
| `cdk diff` detects a destructive replacement during CI | The validation workflow fails; the PR cannot merge until the replacement is intentional and `allow_replacements=Y` is supplied at deploy time |
| GitHub Environment approval not granted on deploy | The deploy workflow blocks at the change-set execution step; the change set remains uncreated until approval lands |
| Cognito user pool deletion attempted | Removal policy `RETAIN` for prod prevents accidental deletion; for dev the policy is `DESTROY`; deletion of a dev user pool is reversible only by reseeding the pool and rebinding the application clients |
| `aws codeartifact login` token expires | `npm ci` rejects with HTTP 401 or 403 in CI and locally; renewal is a manual operation per the CodeArtifact runbook owned by Build and Release |
| Local Postgres container fails to start | bc-core, DevHub document scans, and bc-pg-mcp reject database connections; no platform request can complete until the container is healthy |
| Local Postgres data volume corruption | The `postgres_data` named volume must be removed and the container restarted; the three DDL files re-initialize the database on first start |
| `PlatformInfraStack` re-instantiation drifts from dormant code | The stack would deploy with the dormant as-coded configuration; a deployment without a pre-deploy review of the dormant code may produce a configuration that no longer matches the target architectural intent |

**Governing source.** `platform-infra-stack/`; `bc-core/docker-compose.yml`.

## Governing Decisions

| Decision | Title | Infrastructure impact |
|---|---|---|
| DEC-1918d0 | Deployment and database architecture; ten normalization rules | Two-database split is the architectural commitment and the operational reality; tenant provisioning runs through `seed-tenant-dbs.ts` per D368 |
| DEC-771baf | Tenant database topology; platform-tenant one-way dependency | The infrastructure preserves asymmetric ownership: each tenant database is created and owned per-tenant; the platform database holds only platform-side definitions and the tenant identity registry |
| DEC-e50b83 | Master port reservation | Local development binds bc-core on 3100, DevHub on 4000, bc-ai on 4300, Postgres on 5434, Redis on 6379 |
| DEC-324d9e | Subscription tiers and hosting variants | Hosting variants exist as commercial and operational categories per Tenant Lifecycle and Subscription; per-variant IaC realization is queued |
| DEC-441665 | NPM supply chain mitigation via AWS CodeArtifact | All npm installations route through `barecount/npm-mirror` in ap-south-1; CI uses CodeArtifact via OIDC |
| DEC-c06f41 | Spine expansion to eight sections plus home | The Infrastructure chapter exists in the reshaped Implementation section per DEC-c06f41 |

**Governing source.** The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Authority Model
- Operating Model: Overview
- Architecture
- Backend Services
- Internal Modules
- Auxiliary Services
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-e50b83: Master port reservation
- DEC-324d9e: Subscription tiers and hosting variants
- DEC-441665: NPM supply chain mitigation via AWS CodeArtifact
- DEC-c06f41: Spine expansion to eight sections plus home
- outline.md §4.3: Implementation
- Decisions: ADR Registry
