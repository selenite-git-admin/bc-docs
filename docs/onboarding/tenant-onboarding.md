---
id: tenant-onboarding
order: 64
title: "Tenant Onboarding"
status: drafting
authority: authoritative
depends_on: [the-authority-model, the-object-model, tenancy-and-binding, tenant-entitlement-enforcement, tenant-lifecycle-and-subscription, source-registration, reader-creation, ai-gates, infrastructure]
governing_sources:
  - Tenant Lifecycle and Subscription
  - Tenancy and Binding
  - Tenant Entitlement Enforcement
governing_adrs:
  - DEC-324d9e (Stripe Billing integration; four subscription tiers; four hosting variants)
  - DEC-1392ee (Demo tier policy; AWS Shared only; 14-day trial; 30-day data retention)
  - DEC-a67518 (Tenant Onboarding Gate; BYO-DB and BC-Agent prerequisite)
  - DEC-771baf (Tenant database architecture; ownership boundary)
  - DEC-005ea7 (Single production environment per tenant; trial equals real tenant)
  - DEC-f02230 (Tenant DB schema organization)
  - DEC-b97390 (bc-admin embedded documentation reader)
  - DEC-3ee0f6 (Per-tenant S3 archive bucket; provisioned at onboarding)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Tenant Onboarding

## Scope

This chapter records the governed sequence by which a new tenant is brought onto the platform from contract signing through the first Metric Snapshot. It names the subscription tiers and hosting variants the procedure honors (DEC-324d9e), the demo-tier short-circuit path (DEC-1392ee), the Onboarding Record gate that BYO-DB and BC-Agent variants require before tenant creation (DEC-a67518), the tenant identity and tenant database provisioning steps, the Subscription record creation, the Connection authoring (per-tenant credentials for source systems), the bc-admin reader access provisioning, the first chain run that produces SOs, COs, and Metric Snapshots, and the verification that the tenant is operational. It records the boundary between Tenant Onboarding and the platform-side artifact authority that Tenant Lifecycle and Subscription owns. It records the as-built drift between the procedure and the tenant onboarding state captured by the readiness baseline.

This chapter does not redefine the Subscription artifact or the lifecycle state machine (Tenant Lifecycle and Subscription), the tenant identity and ownership boundary (Tenancy and Binding), the runtime entitlement enforcement surfaces (Tenant Entitlement Enforcement), or the per-artifact onboarding chapters (Source Registration, BF and BO Onboarding, contract creation chapters, Reader Creation) that produce platform-scope artifacts the tenant consumes.

This chapter is the procedural authority for tenant creation. Tenant Lifecycle and Subscription is the authority for the Subscription artifact this procedure produces.

**Governing source.** outline.md §4.6; Tenant Lifecycle and Subscription.

## What the Procedure Produces

| Artifact | Persistent store | Created by |
|---|---|---|
| Tenant identity record | Platform tenant identity table | Step 3 |
| Tenant database (per `tbc_{slug}_dev` pattern, or attached BYO-DB connection) | PostgreSQL or external (per hosting variant) | Step 4 |
| Tenant archive bucket (`bc-archive-{slug}-{env}`, Object Lock COMPLIANCE, 7yr retention) | S3 in ap-south-1 | Step 4 (AWS Shared / AWS Separate); negotiated for BYO-DB / BC-Agent |
| Subscription record (active) | Platform Subscription table | Step 2 (provisional at signup; activated at Step 5) |
| Onboarding Record (BYO-DB and BC-Agent only) | Platform Onboarding table | Step 1.5 (sales-led) |
| Tenant Connections (per source system) | `runtime.connection` (tenant-scoped) | Step 6 |
| Reader-Connection bindings | Runtime binding | Step 7 (paired with platform Reader Flavors) |
| bc-admin reader access (Cognito user; sub-to-tenant claim) | Cognito User Pool plus `custom:tenant_id` | Step 8 |
| First Metric Snapshot | `metric.metric_snapshot` (in tenant DB) | Step 9 first run |

The procedure does not produce platform-scope contract artifacts (those exist independent of any tenant). The procedure produces the tenant-scope substrate that consumes the platform contracts.

**Governing source.** Tenant Lifecycle and Subscription; Tenancy and Binding.

## The Four Tiers and Four Hosting Variants

Per DEC-324d9e, the platform recognizes four subscription tiers. Per DEC-1392ee and the platform's hosting governance, four hosting variants exist. Tier and hosting variant pair on the Subscription record:

| Tier | Hosting variants admissible | Activation path |
|---|---|---|
| Demo | AWS Shared only | Self-service signup; auto-suspend at Day 14; data retained 30 days then purged |
| Starter | AWS Shared | Self-service via external billing platform |
| Professional | AWS Shared or AWS Separate | Self-service or sales-assisted via external billing platform |
| Enterprise | BYO-DB or BC-Agent | Sales-led with invoice billing; Onboarding Record prerequisite |

The hosting variants:

| Variant | Tenant database placement | Activation prerequisites |
|---|---|---|
| AWS Shared | Auto-provisioned tenant database on shared infrastructure under the platform's AWS account | None; lightweight provisioning at signup |
| AWS Separate | Per-tenant dedicated database on platform-managed infrastructure under the platform's AWS account | None at the tenant lifecycle level; infrastructure provisioning is a deployment concern |
| BYO-DB | Tenant-managed database in the customer's own infrastructure, accessed by the platform under negotiated connectivity | Onboarding Record in `ready` state per DEC-a67518 |
| BC-Agent | Local agent runtime in the customer's environment; data movement governed by the agent | Onboarding Record in `ready` state per DEC-a67518 |

A Subscription record carrying a tier and hosting variant pair the tier does not admit is rejected at the authoring act.

**Governing source.** Tenant Lifecycle and Subscription; DEC-324d9e; DEC-1392ee; DEC-a67518.

## Per DEC-005ea7: Single Production Environment

The platform operates one production environment per tenant. There are no per-tenant dev or pre-production tiers. A trial tenant is a real tenant; on purchase, the trial tenant is deleted and recreated rather than promoted in place. The chapter records this as the lifecycle's environmental discipline; it shapes the cleanup behavior at Day 14 of a Demo tier and at trial-to-purchase transitions.

**Governing source.** Tenant Lifecycle and Subscription.

## Step 1: Contract Signing or Self-Service Signup

For Self-Service Tiers (Demo, Starter, Professional with AWS Shared or AWS Separate), the path is the external billing platform plus the platform's signup surface. The actor (the tenant) provides organization name, tenant slug request (subject to uniqueness constraint), tier selection, and billing details. The platform records a provisional Subscription pending Step 2 confirmation.

For Sales-Led Tiers (Enterprise with BYO-DB or BC-Agent), the path is a signed master agreement plus an Order Form. The platform records the contractual artifacts and the negotiated tier and hosting variant choice.

**Governing source.** Tenant Lifecycle and Subscription.

## Step 1.5: Onboarding Record (BYO-DB and BC-Agent Only)

For BYO-DB and BC-Agent variants, an Onboarding Record gates tenant creation per DEC-a67518. The Onboarding Record records the prerequisite work the customer must complete before the platform can provision the tenant:

| Prerequisite | Form |
|---|---|
| Connectivity established | Network path from the platform to the customer database (BYO-DB) or from the customer environment to the platform (BC-Agent) |
| Credentials issued | Service account or API key the platform uses to access the customer's database (BYO-DB) or that the agent uses to authenticate to the platform (BC-Agent) |
| Schema readiness | The customer database has the schemas the platform expects to read from (BYO-DB) or the agent runtime is installed (BC-Agent) |
| Security review complete | Customer security team has approved the integration |

The Onboarding Record progresses through states (`pending`, `in_progress`, `ready`, `cancelled`). Tenant provisioning (Step 3) is blocked until the Onboarding Record reaches `ready`. AWS Shared and AWS Separate variants do not require an Onboarding Record; tenant provisioning runs immediately after Step 2.

**Governing source.** DEC-a67518; Tenant Lifecycle and Subscription.

## Step 2: Subscription Record Creation

The platform creates the Subscription record with the tier, the hosting variant, the catalog entitlement (chain entitlement, function and subfunction entitlement, metric entitlement, source system entitlement), and the operational envelope (admission rate limits, concurrent admission caps, evaluation cadence). The record's lifecycle state is `provisioned-pending-tenant`. The record activates at Step 5 once the tenant exists.

The catalog entitlement defaults vary by tier. Demo and Starter use platform-declared subsets; Professional and Enterprise record explicit subsets per Subscription. The chapter does not enumerate the per-tier defaults here; Tenant Lifecycle and Subscription owns that authority.

**Governing source.** Tenant Lifecycle and Subscription.

## Step 3: Tenant Identity Provisioning

The platform creates the tenant identity record with the tenant slug (validated for uniqueness; lowercase, snake_case or kebab-case per the slug convention) and the tenant's display name. The slug is the immutable tenant identifier that later artifacts (Connections, runtime rows, audit records) reference.

For AWS Shared, AWS Separate, and BYO-DB variants, the tenant database is provisioned in this step. Active tenant DB provisioning is `bc-core/src/registry/seed/seed-tenant-dbs.ts`: the script creates a separate tenant database and applies `docker/redesign/03-tenant-db.sql`. The tenant database schema baseline includes the `progression` schema. BYO-DB provisioning attaches the customer's database via a connection string recorded in the Onboarding Record.

For BC-Agent, no tenant database is provisioned in this step; the agent runtime in the customer environment writes to the platform's tenant database via the agent protocol.

**Governing source.** Tenancy and Binding; Infrastructure; `bc-core/src/registry/seed/seed-tenant-dbs.ts`; `bc-core/docker/redesign/03-tenant-db.sql`; DEC-771baf; DEC-f02230.

## Step 4: Tenant Database Schema Creation

The tenant database receives the approved tenant schema set through `docker/redesign/03-tenant-db.sql`. The creation is automated: `seed-tenant-dbs.ts` runs the tenant DDL against the new separate database; for BYO-DB, the platform runs the approved tenant DDL against the attached customer database subject to the customer approval recorded in the Onboarding Record.

The seven schemas are created in dependency order by the active DDL. A failed creation blocks completion and leaves the tenant in a repair state; the chapter does not claim an automatic rollback unless the provisioning script implements that rollback for the failing path.

Step 4 also provisions the tenant's S3 archive bucket per DEC-3ee0f6. The bucket is the per-tenant WORM vault for raw payloads under the D369 three-layer architecture (`progression.*` metadata + `fact.*_v*` typed projection + S3 raw archive). The bucket is created with Object Lock enabled at creation time (Object Lock cannot be added retroactively), default retention COMPLIANCE 7 years, encrypted with the shared `bc-archive` KMS CMK.

| Sub-step | What | Form |
|---|---|---|
| 4a | Compute bucket name | `bc-archive-{sanitised_slug}-{env}` where `env ∈ {dev, prod}`. Slug sanitisation: lowercase, `_` rewritten to `-`. The platform asserts AWS bucket-naming compliance (3-63 chars) before attempting create |
| 4b | `CreateBucket` | with `ObjectLockEnabledForBucket=true` in `ap-south-1`. Failure leaves the tenant in repair state |
| 4c | `PutObjectLockConfiguration` | COMPLIANCE mode, 7-year default retention |
| 4d | `PutBucketEncryption` | SSE-KMS with the shared `bc-archive` CMK |

For BYO-DB and BC-Agent variants, archive bucket placement is negotiated per the Onboarding Record (DEC-a67518) — the platform's bucket may not be the appropriate target if the customer requires sovereignty over archive data. This chapter does not enumerate the BYO-DB archive variants.

**Governing source.** Tenancy and Binding; Infrastructure; `bc-core/src/registry/seed/seed-tenant-dbs.ts`; `bc-core/docker/redesign/03-tenant-db.sql`; `bc-core/src/progression/s3-archiver.service.ts`; DEC-771baf; DEC-f02230; DEC-3ee0f6.

## Step 5: Subscription Activation

With the tenant identity provisioned, the Subscription record transitions from `provisioned-pending-tenant` to `active`. The activation runs the catalog entitlement resolution (the platform binds the tenant to the entitled chains, functions, subfunctions, metrics, and source systems) and persists the resolved entitlement as the runtime read source.

For Demo tier, the activation also schedules the auto-suspend task for Day 14 and the data-purge task for Day 44 per DEC-1392ee.

**Governing source.** Tenant Lifecycle and Subscription.

## Step 6: Tenant Connection Authoring

For each source system the tenant intends to observe, the actor creates a Connection record. The Connection is tenant-scoped (`runtime.connection`); it carries the credentials the platform uses to access the source system at runtime. A Connection references a platform-cataloged Source System and Source Version (Source Registration); it does not duplicate the catalog identity.

The Connection authoring runs through the bc-admin Connection surface or via the API. Credentials are encrypted at rest in the platform secrets store; the Connection record carries a reference to the secret, not the secret itself.

A Connection without a corresponding Reader Flavor (Reader Creation) cannot drive observation; the chapter records the pairing as the runtime relationship that enables the chain. A tenant whose source system has a Reader Flavor in the platform but no Connection in the tenant has no observation path; the gap is recorded as an onboarding-incomplete state.

**Governing source.** Tenancy and Binding; Reader Creation.

## Step 7: Reader-Connection Pairing

For each Connection authored at Step 6, the platform pairs the Connection with the matching Reader Flavor. The pairing is the runtime binding the Reader uses at execution time; it does not modify the Reader's platform-scope definition.

Pairing is automatic when the Reader Flavor for the source system exists in the platform; if no Flavor exists, the pairing fails and the tenant is in a state where the source system is connected but cannot be observed. The remediation routes back to Reader Creation (the platform team adds a Flavor for the source system).

**Governing source.** Reader Creation; Tenancy and Binding.

## Step 8: bc-admin Reader Access Provisioning

Per DEC-b97390, the bc-admin embedded documentation reader is the canonical reader. The procedure provisions Cognito user records for the tenant's named users with `custom:tenant_id` claim binding each user to the tenant identity. Cognito groups are used for role assignment within the tenant (admin, viewer, etc.); the platform does not create per-tenant role taxonomies, only the standard roles.

bc-admin reader access is independent of the tenant database. A tenant with provisioning failures at Steps 3 to 7 may still have bc-admin access if Step 8 ran first; the chapter records this as the recommended ordering (Step 8 last so reader access reflects working tenant state).

**Governing source.** Infrastructure.

## Step 9: First Chain Run

With Connections paired and bc-admin access provisioned, the actor triggers the first chain run. The Reader's Flavor binds to the tenant Connection at runtime; the Reader executes against the source system, produces SOs, the canonical evaluator produces COs, the metric engine produces Metric Snapshots. The first Metric Snapshot in the tenant database is the chapter's success criterion: the tenant is operational.

The first chain run typically reveals connection issues (credential drift, network rules, rate limits) that did not surface at Step 6 authoring time. The platform's operational alerting consumes the first run's logs to surface failures to the actor for remediation.

**Governing source.** Reader Creation; Admission and Observation; Metric Evaluation.

## Step 10: Verify the Tenant Is Operational

The actor confirms operational state via three checks:

| Check | How |
|---|---|
| Tenant database is accessible | The tenant's Subscription state is `active`; the platform's tenant connection pool reports the database as reachable |
| First chain run completed | At least one Metric Snapshot exists in the tenant database for at least one entitled metric |
| bc-admin reader access works | The tenant's named user can log in and see the metric catalog; the reader's tenant scope is correctly enforced |

A tenant that passes the three checks is operational. A tenant that fails any check is in an onboarding-incomplete state with the specific remediation routed back to the corresponding step.

**Governing source.** Tenant Entitlement Enforcement; Tenancy and Binding.

## Boundary with Other Onboarding Chapters

| Chapter | Relationship |
|---|---|
| Source Registration | Independent; the catalog is platform-scoped and exists independent of any tenant. Tenant Connections reference catalog rows |
| Seed Catalog Management | Independent; same as Source Registration |
| Business Field and Business Object Onboarding | Independent; BFs and BOs are platform-scoped |
| Canonical Field Seeding | Independent; CFs are platform-scoped |
| Source and Admission Contract Creation | Independent; SC and AC are platform-scoped |
| Observation Contract Creation | Independent; OC is platform-scoped |
| Canonical Contract Creation | Independent; CC is platform-scoped |
| Metric Contract Creation | Independent; MC is platform-scoped |
| Reader Creation | Provides the Reader Flavors the tenant Connections pair with at runtime |
| Metric Registration | Independent; metric definitions are platform-scoped |
| MC Chain Integrity | Operates on platform MCs; tenant onboarding does not trigger chain integrity walks |
| Data Seeding and Build Order | The build sequence the platform runs to make MCs operational; tenant onboarding consumes the operational chain. A tenant brought onto a chain that is not operational at the platform level inherits the chain's gaps |
| Multi-Standard Onboarding | Independent; multi-standard concerns vocabulary, not tenancy |

**Governing source.** The per-artifact and per-procedure onboarding chapters.

## Drift Inventory

| Drift item | Form |
|---|---|
| Demo-tier auto-purge schedule reliability belongs to Operations | DEC-1392ee declares 14-day auto-suspend and 30-day data retention; this chapter records the policy, while Operations owns evidence that scheduled purge execution is reliable |
| BYO-DB connectivity verification is manual | The Onboarding Record records that connectivity is "established" but the platform does not run an automated connectivity probe before Step 3. A manual verification by the platform team confirms; an automated probe is queued |
| BC-Agent runtime is largely aspirational | The BC-Agent variant is recorded in DEC-324d9e as a supported hosting variant; the agent runtime, the agent-to-platform protocol, and the agent's local data movement are not built in the readiness baseline. A BC-Agent tenant onboarding cannot complete past the Onboarding Record gate until that runtime exists |
| Tenant database schema creation order | The seven tenant schemas, including `progression`, are created in dependency order through `seed-tenant-dbs.ts` and `03-tenant-db.sql`. A schema added after the script and DDL are updated is not created for new tenants until both surfaces are updated |
| First chain run failures are common | First chain run typically surfaces credential, network, or source-side schema drift issues. The chapter records this as expected; the procedure includes the remediation loop, not just the success path |
| qa-bench tenant is not a real tenant | The qa-bench tenant is a design intent for test isolation; it is not provisioned through this procedure in the readiness baseline. Test Bench Module writes evidence into the live tenant rather than a dedicated qa-bench tenant; the qa-bench provisioning is a queued surface |
| Trial-to-purchase delete-and-recreate | Per DEC-005ea7, on purchase a trial tenant is deleted and recreated rather than promoted in place. The customer's trial-period configuration (Connections, custom thresholds) does not automatically migrate; the customer re-authors against the new tenant |
| Archive bucket creation in seed script | DEC-3ee0f6 / D379 establishes the per-tenant bucket as Step 4's responsibility, but the seed script `bc-core/src/registry/seed/seed-tenant-dbs.ts` does not yet invoke the AWS SDK to create the bucket. As-built form: the platform team creates the bucket manually (or via a one-shot script) until the seed script integration ships. Sandbox1 was created under this manual path; new tenants should expect the same until the gap closes |

**Governing source.** Tenant Lifecycle and Subscription; Tenant Entitlement Enforcement; Tenancy and Binding; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-324d9e | Establishes the four subscription tiers and four hosting variants; this chapter is the operational onboarding form |
| DEC-1392ee | Establishes the demo-tier policy (AWS Shared only; 14-day trial; 30-day retention); this chapter records the demo-tier short-circuit path |
| DEC-a67518 | Establishes the Onboarding Record gate for BYO-DB and BC-Agent variants; this chapter is the procedural form of the gate |
| DEC-771baf | Establishes the tenant database architecture and ownership boundary; this chapter's tenant database provisioning honors it |
| DEC-005ea7 | Establishes single production environment per tenant; this chapter's trial-to-purchase delete-and-recreate is the operational form |
| DEC-f02230 | Establishes tenant DB schema organization; this chapter records the readiness-baseline DDL application rather than the older six-schema wording |
| DEC-b97390 | Establishes the bc-admin embedded documentation reader; this chapter records the tenant-user provisioning boundary that consumes it |
| DEC-3ee0f6 | Establishes the per-tenant S3 archive bucket (D379); this chapter's Step 4 sub-steps are the operational form of the bucket-provisioning sequence |

**Governing source.** Decisions: ADR Registry.

## References

- Tenant Lifecycle and Subscription
- Tenancy and Binding
- Tenant Entitlement Enforcement
- The Authority Model
- Source Registration
- Reader Creation
- Connectors and Readers
- Admission and Observation
- Metric Evaluation
- AI Gates
- Infrastructure
- Audit and Activity Logging
- DEC-324d9e: Stripe Billing integration; four subscription tiers; four hosting variants
- DEC-1392ee: Demo tier policy
- DEC-a67518: Tenant Onboarding Gate
- DEC-771baf: Tenant database architecture
- DEC-005ea7: Single production environment per tenant
- DEC-f02230: Tenant DB schema organization
- DEC-3ee0f6: Per-tenant S3 archive bucket (D379)
- outline.md §4.6: Onboarding


