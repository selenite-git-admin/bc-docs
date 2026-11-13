---
id: platform-refactor-program-functions-brief
order: 45.08
title: "The Functions in Brief"
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

# The Functions in Brief

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md).

This annex gives one short summary of each of the 28 functions of the functional map: what it is, its state today, its main defects, and what "locked" will mean for it. Each summary is drawn only from the function's full dossier and links to it. Citations are copied from the dossiers.

One summary for each of the 28 functions follows, in the order of the table above and under the same group names. Each is drawn only from the function's dossier, and each citation is the dossier's own. "Locked means" gives the most important conditions for the function's Lock step; the dossier gives all of them. Terms such as "in force", "readiness pass" and "proof pin" are defined in "Terms used in this document".

**Shared services**

### S1, Authentication
- **What it is:** Authentication answers one question: who is calling. bc-core checks a token issued by Amazon Cognito on every request and derives the caller's scope, tenant and roles from it.
- **State today:**
  - Four global guards run in a fixed order: token, scope, tenant claim, role (bc-core:src/auth/auth.module.ts:25-30 @ ec72438b).
  - Only two controllers are public: the health check and the served-identity probe (command: `git grep -n -F '@Public()' origin/main -- 'src/**/*.controller.ts'` -> 2 lines: `src/health/health.controller.ts:7`, `src/database/served-identity/served-identity.controller.ts:12` @ ec72438b).
  - The served pool is not the pool that bc-infra defines; the account holds four pools (command: `aws cognito-idp list-user-pools` -> 4 pools).
- **Main defects:**
  - The pool that decides who is admitted is not defined in bc-infra.
  - The chapter says access tokens are handled; the code rejects them.
  - Credentials are committed in bc-core scripts.
- **Locked means:**
  - The served pool id equals the pool defined in bc-infra, and a check fails when they differ.
  - A CI scan fails on any committed credential in any repository.
- **Full dossier:** [S1, Authentication](platform-refactor-program/functions-shared-services-operations-development.md#s1-authentication)

### S2, User and access management
- **What it is:** This function decides what an authenticated caller may do. It covers creating users, giving them roles, and keeping platform routes and tenant routes apart.
- **State today:**
  - 118 of 138 controller files carry the platform-only marker and 17 carry the tenant marker (command: `git grep -l -F '@PlatformOnly()'` -> 118; `'@TenantScoped()'` -> 17; `ls-tree | grep -c controller.ts` -> 138 @ ec72438b).
  - Roles are held only in a Cognito attribute; the one user table is empty (query (bc_platform_dev, 2026-11-13): `select count(*) from users.platform_user` -> 0).
  - Both `super_admin` and `admin` pass every role check (bc-core:src/auth/guards/roles.guard.ts:34-35 @ ec72438b).
- **Main defects:**
  - The `admin` role passes every role check, and no chapter says so.
  - A user can be created for a tenant slug that does not exist.
  - No record shows who held which role and when.
- **Locked means:**
  - One route creates a user, and it refuses a tenant slug that is not in the registry.
  - A CI test fails when a platform write route has no role marker.
- **Full dossier:** [S2, User and access management](platform-refactor-program/functions-shared-services-operations-development.md#s2-user-and-access-management)

### S3, Tenant lifecycle and management
- **What it is:** This function creates a tenant, changes its state and retires it. Creating a tenant means writing its row in the registry and creating its own database.
- **State today:**
  - Four tenants are registered; only `kaveri` is active (query (bc_platform_dev, 2026-11-13): `select slug, status_code, tenant_class_code, schema_name, database_name from tenant.tenants` -> 4 rows).
  - The operator creates a tenant at a terminal with `npm run tenant:lifecycle -- create <slug>` (bc-core:src/tenant-management/lifecycle/tenant-lifecycle-cli.ts:7-8, 56-62 @ ec72438b).
  - The served route `POST /api/tenants` always answers 403, and the console's create screen calls it (bc-core:src/tenant-management/tenant-provisioning-api.service.ts:14-16, 30-36 @ ec72438b; bc-admin:src/api/tenants.ts:199-215 @ d37b241).
- **Main defects:**
  - Documents and the console name a creation route that refuses.
  - A suspended tenant cannot be resumed by any governed act.
  - Migration 0034, a sixth tenant state and a gate, is not applied.
- **Locked means:**
  - Tenant creation has exactly one entry point, and the existing CI guard fails if a second creator appears.
  - Each state change (create, suspend, resume, retire) has one governed act that writes a record.
- **Full dossier:** [S3, Tenant lifecycle and management](platform-refactor-program/functions-shared-services-operations-development.md#s3-tenant-lifecycle-and-management)

### S4, Pricing and subscription
- **What it is:** This function is meant to define what a tenant buys and to record that it bought it: packages, the Subscription, entitlement and billing. Today only a small package table and its screens exist.
- **State today:**
  - `pricing.package` holds 7 rows, two of them active (query (bc_platform_dev, 2026-11-13): `select package_name, status_code from pricing.package` -> custom active; Free active; finance-essentials, finance-complete, full-erp, crm, hr deprecated).
  - No Subscription record exists (query (bc_platform_dev, 2026-11-13): `select to_regclass('tenant.subscription')` -> null).
  - Until the Subscription is built, every active tenant may see and evaluate every active platform metric (bc-docs:docs/governance/adrs/ADR-c220e4.md:16 @ f4f5edd).
- **Main defects:**
  - The built table models readers per tier, not metrics per package.
  - Two ADRs are decided and not built: DEC-324d9e and DEC-cf6d3b.
  - Three console screens under "pricing" are placeholders.
- **Locked means:**
  - One Subscription record per tenant exists, and tenant creation writes it.
  - Entitlement is checked in exactly one place, with a test that fails when the check is removed.
- **Full dossier:** [S4, Pricing and subscription](platform-refactor-program/functions-shared-services-operations-development.md#s4-pricing-and-subscription)

### S5, Operator console
- **What it is:** The operator console is the web application bc-admin. An operator uses it to see and administer everything else on the platform; each screen calls bc-core, and the console holds no data of its own.
- **State today:**
  - The router holds 132 route elements; ten render a placeholder page (command: `grep -c '<Route'` on bc-admin:src/components/AppRouter.tsx -> 132 @ d37b241; bc-admin:src/components/AppRouter.tsx:175, 262-265, 296, 299, 307-309 @ d37b241).
  - The console is served from a shared working copy by a development server, not from a fixed build (command: `~/bc-stack/process-compose.yaml` lines 108-111 -> `working_dir: ~/MyProjects/bc-admin`, `npm run dev -- --host 127.0.0.1`).
  - The documentation reader's folder is absent from the served tree (command: `ls ~/MyProjects/_wt/freeze-1055/private-docs` -> no such directory).
- **Main defects:**
  - The tenant create screen cannot succeed.
  - The documentation reader has no documents on the served build.
  - bc-docs does not say which acts must have a screen.
- **Locked means:**
  - A generated table lists every governed act and its screen, command or "none by decision"; CI fails when an act has no entry.
  - No screen calls a route that is retired or always refuses.
- **Full dossier:** [S5, Operator console](platform-refactor-program/functions-shared-services-operations-development.md#s5-operator-console)

**Authoring**

### L1, Source Catalog
- **What it is:** The Source Catalog is the platform's record of the structure of the external systems it can read. It holds no business data, and it has six levels, from source provider down to source field.
- **State today:**
  - The governed route of three calls (admit, verify, approve) was used for the whole live catalog: 305 tables and 9,850 fields are `approved`. query (bc_platform_dev, 2026-11-13): `SELECT catalog_status, count(*) FROM source.<level> GROUP BY 1` for each level -> provider 1 `registered`; system 1 `registered`; version 1 `registered`; module 37 `registered`; table 305 `approved`; field 9,850 `approved`
  - There are four ways to create a catalog row, and bc-admin uses only the six CRUD routes (`bc-admin:src/api/sources.ts:517-572 @ d37b241`).
  - One adapter is registered, for Odoo, so a second source system needs code (`bc-core:src/registry/source-extract/source-catalog-adapter.ts:52 @ ec72438b`).
- **Main defects:**
  - A row can be born `approved` through the CRUD routes.
  - Nothing checks that a table is approved before a contract is written over it.
  - None of the procedure chapter's three steps can be followed.
- **Locked means:**
  - One route creates catalog rows, and no row can be created `approved`.
  - A contract cannot be written over a table that is not `approved` and `verified`.
- **Full dossier:** [L1, Source Catalog](platform-refactor-program/functions-authoring-lanes.md#l1-source-catalog)

### L2, Source and Admission Contracts
- **What it is:** A Source Contract declares the structure of one source table. An Admission Contract declares the rules under which rows observed from that table are admitted or rejected. They are written as a pair over one catalog table.
- **State today:**
  - The one-call route was used for the whole estate: 305 Source Contract versions are in force. query (bc_platform_dev, 2026-11-13): `SELECT governance_state_code, count(*) FROM contract.source_contract_version GROUP BY 1` -> `active` 305
  - A new version only stamps the prior one with a 48-hour mark, and no code completes the supersession (`bc-core:src/registry/contracts/contract-version.repository.ts:214-221 @ ec72438b`).
  - The reader binding column named for a source contract holds admission contract ids. query (bc_platform_dev, 2026-11-13): reader bindings matching an admission contract -> 19 of 19; matching a source contract -> 0 of 19
- **Main defects:**
  - Two versions of one Admission Contract are in force at once.
  - No check that the catalog table is approved.
  - Five ways exist to write a pair.
- **Locked means:**
  - One command writes a pair, and a CI guard fails on any other writer.
  - At most one version of a contract is in force, enforced in the database.
- **Full dossier:** [L2, Source and Admission Contracts](platform-refactor-program/functions-authoring-lanes.md#l2-source-and-admission-contracts)

### L3, Vocabulary
- **What it is:** L3 authors the business concept registry: the one governed list of entities, characteristics and business concepts that every contract refers to by identity. Candidates are shaped by an AI panel and written only after a certification record exists.
- **State today:**
  - The registry holds 149 active entities, 756 active business concepts and 232 active characteristics. query (bc_platform_dev, 2026-11-13): `SELECT lifecycle_state, count(*) FROM concept_registry.<table> GROUP BY 1`
  - The registry has one writer. command: `git grep -l -E "INSERT INTO concept_registry|UPDATE concept_registry" origin/main -- scripts src` -> one file, `concept-source-reference.service.ts`
  - The panel has 2,743 records, the newest dated 2026-11-12. query (bc_platform_dev, 2026-11-13): `SELECT verdict_code, count(*) FROM bcf.panel_output_record GROUP BY 1`
- **Main defects:**
  - The panel host defaults to the retired bc-ai service.
  - 602 runs carry the verdict `OPERATOR_REVIEW`, and nothing says who clears them.
  - bc-docs contradicts itself in four places, including the lifecycle states.
- **Locked means:**
  - One command set creates, publishes, versions, supersedes and withdraws each of the three kinds.
  - A CI guard fails if any file outside the writer service writes `concept_registry`.
- **Full dossier:** [L3, Vocabulary](platform-refactor-program/functions-authoring-lanes.md#l3-vocabulary)

### L4, Observation Contracts
- **What it is:** An observation contract declares how one source table is read into business concepts: which fields and rows are selected, which concept each field carries, and the shape of the source object that admission preserves.
- **State today:**
  - There are 17 contracts and 29 versions: 19 `active`, 7 `superseded`, 2 `draft`, 1 `approved`. query (bc_platform_dev, 2026-11-13): `SELECT governance_state_code, count(*) FROM contract.observation_contract_version GROUP BY 1`
  - One contract has six versions in state `active`; a successor only stamps the older version with a 48-hour mark (`bc-core:src/registry/contracts/contract-version.repository.ts:204-220 @ ec72438b`).
  - The procedure describes the v1 grammar: "A full chapter rewrite for v2 is pending" (`bc-docs:docs/onboarding/observation-contract-creation.md:289 @ f4f5edd`).
- **Main defects:**
  - Several versions of one contract are in force at once.
  - The chain service moves `draft` to `active` with no review or approval.
  - Six alternate routes exist, including scripts that change version rows by SQL.
- **Locked means:**
  - One command set creates, versions, brings into force and supersedes an observation contract.
  - At most one version per contract is in state `active`, enforced in the database.
- **Full dossier:** [L4, Observation Contracts](platform-refactor-program/functions-authoring-lanes.md#l4-observation-contracts)

### L5, Canonical Contracts
- **What it is:** A canonical contract declares the business meaning of one entity, independent of any source system. This lane authors its versions, moves them through their states, has their tables created for each tenant, and fixes which version an evaluation reads.
- **State today:**
  - There are 11 contracts and 25 versions. query (bc_platform_dev, 2026-11-13): `SELECT governance_state_code, count(*), count(DISTINCT canonical_contract_id) FROM contract.canonical_contract_version GROUP BY 1` -> active 9 (7 contracts), approved 4 (4), pending_provisioning 3 (2), superseded 9 (3)
  - Five routes write a canonical version. The HTTP route passes no options, so the grain pin and the key form can be declared only through a runner (`bc-core:src/registry/contracts/contract.controller.ts:221 @ ec72438b`).
  - A tenant evaluation reads the globally in-force version; the tenant's contract binding takes no part (`bc-core:src/boundary/ccv2-canonical-resolver.service.ts:742-749 @ ec72438b`).
- **Main defects:**
  - Any run of the readiness pass can bring a held demo-plane version into force.
  - Two contracts each have two versions in force, both past their window.
  - None of the procedure chapter's nine steps can be followed.
- **Locked means:**
  - One route creates a canonical version and can declare the grain pin and the key form.
  - The readiness pass skips or refuses every held version, with a test.
- **Full dossier:** [L5, Canonical Contracts](platform-refactor-program/functions-authoring-lanes.md#l5-canonical-contracts)

### L6, Metric Contracts and certification
- **What it is:** A Metric Contract is the governed declaration of one metric: its formula, the concepts its variables read, its metric grain and its filters. This lane authors a version, carries it through review and approval, and has it certified.
- **State today:**
  - Versions by state: `active` 93, `approved` 55, `audit_pending` 281, `draft` 19, `review` 14, `superseded` 1. query (bc_platform_dev, 2026-11-13): `SELECT governance_state_code, is_current, count(*) FROM mcf.metric_contract_version GROUP BY 1,2`
  - Nothing has been certified since 2026-09-30. query (bc_platform_dev, 2026-11-13): `SELECT max(created_at) FROM mcf.certification_record WHERE action_code='audit_admit'` -> 2026-09-30 10:03:40
  - Direct activation is closed with HTTP 410 (`bc-core:src/registry/mcf/mcf-publication-activation.controller.ts:24-38 @ ec72438b`).
- **Main defects:**
  - Both DevHub metric tools end at the retired route.
  - Fourteen versions hold `active` with no certificate, and the runtime can select them.
  - bc-docs contradicts itself on whether a panel gates certification.
- **Locked means:**
  - One command takes a directory entry to a certified version.
  - A CI guard fails on any new write to `governance_state_code` outside `McfCertWriterService`.
- **Full dossier:** [L6, Metric Contracts and certification](platform-refactor-program/functions-authoring-lanes.md#l6-metric-contracts-and-certification)

### L7, Readers and connections
- **What it is:** This lane authors the definitions that let the platform read a source system: connectors, connections, readers, reader flavors, and the two bindings that pin the admission contract version and the observation contract version a run uses.
- **State today:**
  - Governed authoring of readers, flavors and both bindings is mounted, and the four legacy writes refuse (`bc-core:src/registry/readers/reader.service.ts:103-107,214-218,239-243,630-637 @ ec72438b`).
  - The forward request for a tenant's source-object tables matches nothing, because it joins the reader binding to source contracts (`bc-core:src/schema-provisioner/schema-provisioner.repository.ts:458-478 @ ec72438b`).
  - The bc-admin "new reader" screen still posts to a closed route (`bc-admin:src/api/readers.ts:335-340 @ d37b241`).
- **Main defects:**
  - A source can be read only after a metric has pulled its table.
  - `reader_binding.source_contract_id` holds admission contract ids and has no foreign key.
  - Three spellings of the environment are in use.
- **Locked means:**
  - Each act has exactly one mounted write route.
  - `reader_binding` names an admission contract in a column with that name and a foreign key.
- **Full dossier:** [L7, Readers and connections](platform-refactor-program/functions-authoring-lanes.md#l7-readers-and-connections)

### L8, Metric Directory
- **What it is:** The Metric Directory is the governed list of the metrics that should exist. An entry is registered when it has a row, and realized when a governed act asserts that a specific metric contract version fulfils it.
- **State today:**
  - Creation, member versions and realization are built and have data. `query (bc_platform_dev, 2026-11-13): counts over metric_directory -> family 49; group 143; member 435 (399 not archived, 36 archived); member_version 276; realization_event assert 282, revoke 0; realization_operative 265; directory_decision 135`
  - 159 members have no member version, so they cannot be realized. `query (bc_platform_dev, 2026-11-13): SELECT count(*) FROM metric_directory.member m WHERE NOT EXISTS (SELECT 1 FROM metric_directory.member_version v WHERE v.member_uid=m.member_uid) -> 159`
  - The intake accepts a proposal with no directory member (`bc-core:src/registry/mcf/operator-direct-adapter.ts:48 @ ec72438b`).
- **Main defects:**
  - The rule that nothing is drafted before it is registered is not enforced.
  - The legacy metric routes are still mounted, and bc-admin still calls them.
  - The chapter says nothing is built; 29 directory tables exist.
- **Locked means:**
  - One route registers a member, one creates an intake, and the intake refuses a missing member.
  - Every version in `mcf.mcv_live` has an operative realization.
- **Full dossier:** [L8, Metric Directory](platform-refactor-program/functions-authoring-lanes.md#l8-metric-directory)

### L9, Chain integrity
- **What it is:** Chain integrity answers, for each metric contract version, whether the contracts and vocabulary it depends on line up today. The answer is the chain verdict: green, amber or red. It says nothing about values.
- **State today:**
  - 54 of 82 current versions are red. `query (bc_platform_dev, 2026-11-13): SELECT cs.verdict_code, count(*) FROM mcf.mcv_chain_status cs JOIN mcf.mcv_live lv USING (metric_contract_version_uid) GROUP BY 1 -> green 21; amber 7; red 54`
  - Certification passes only on a green verdict: "PASS iff green" (`bc-core:src/registry/metric-audit/decision/certification-panel-decision.lane.ts:55-59 @ ec72438b`).
  - The nightly write runs only when `BC_SCHEDULER_ENABLED` is set, and it is not set on the development host (`bc-core:src/boundary/runtime-scheduler.service.ts:58-64 @ ec72438b`).
- **Main defects:**
  - The vocabulary page says the verdict "gates nothing"; the code gates on it twice.
  - The number of checks differs in four texts.
  - Four different things are called "chain".
- **Locked means:**
  - One list of checks, generated from the code, appears in the chapter, the vocabulary page and the DevHub tool.
  - The vocabulary page and the guide state the same rule on what the verdict gates.
- **Full dossier:** [L9, Chain integrity](platform-refactor-program/functions-authoring-lanes.md#l9-chain-integrity)

### L10, Tenant onboarding
- **What it is:** L10 is the hand-off from the platform to one tenant. It records which contract versions a tenant has adopted, issues a provisioning command for each table the tenant needs, and runs the worker that creates those tables in the tenant's database.
- **State today:**
  - Four tenants exist; one is `active` (`kaveri`). query (bc_platform_dev, 2026-11-13): `SELECT status_code, count(*) FROM tenant.tenants GROUP BY 1`
  - The served route `POST /tenants` refuses by design; only the `tenant:lifecycle` command creates a tenant (`bc-core:src/tenant-management/tenant-provisioning-api.service.ts:14-36 @ ec72438b`).
  - All 17 contract bindings are canonical and active; none is for a metric. query (bc_platform_dev, 2026-11-13): `SELECT contract_family, is_active, count(*) FROM tenant.contract_binding GROUP BY 1,2`
- **Main defects:**
  - The readiness pass has no exclusion for versions pinned to the demo plane.
  - No act ends a prior contract binding.
  - Five origins issue provisioning commands.
- **Locked means:**
  - One command creates a tenant, and every document and screen names it.
  - One act enables a metric for a tenant, from one origin of provisioning commands.
- **Full dossier:** [L10, Tenant onboarding](platform-refactor-program/functions-authoring-lanes.md#l10-tenant-onboarding)

**Runtime and proof**

### RT, Runtime
- **What it is:** Runtime is the set of acts that take one tenant's source data to governed values: observe the source, admit Source Objects, resolve Canonical Objects, evaluate metrics and record a Metric Snapshot. Each act happens only when it is explicitly invoked.
- **State today:**
  - The three engines are present, and the legacy metric path was retired on 2026-09-29 (command: `git log -1 4ab0ea0b` -> "retire the legacy metric evaluation path and the action boundary (Unit R1)").
  - Metric evaluation reads the version that is current and `active` for everyone, not the tenant's adopted version (`bc-core:src/boundary/metric-spec-loader.ts:237 @ ec72438b`).
  - The scheduler is off unless `BC_SCHEDULER_ENABLED=1` (`bc-core:src/boundary/runtime-scheduler.service.ts:58-91 @ ec72438b`).
- **Main defects:**
  - Two evaluation routes name no roles, and the roles guard allows that.
  - Version selection is global, against Invariant IV and ruling T3.
  - No chapter says who supplies the period.
- **Locked means:**
  - Each of the three acts has exactly one entry point, and a CI guard fails on a second.
  - Each act reads the contract version from the tenant's adoption record, proven by a test.
- **Full dossier:** [RT, Runtime](platform-refactor-program/functions-runtime-delivery-support.md#rt-runtime)

### EV, Evidence and lineage
- **What it is:** Evidence is the record that a boundary act happened, with its outcome. Lineage is the record of what that act referenced. Both are written by the act itself and are never rebuilt afterwards.
- **State today:**
  - Evidence is atomic at the metric boundary only: "**The other boundaries remain best-effort** per DEC-ebb3cd (D387) until their own governed units bring them to the atomic posture." (`bc-docs:docs/operating-model/evidence-and-lineage.md:37-38 @ f4f5edd`).
  - At admission the write is "Awaited but non-fatal — returns 'recorded' if both land, 'degraded' if either fails." (`bc-core:src/boundary/admission.service.ts:321-324 @ ec72438b`).
  - Two routes accept an evidence or lineage record from any tenant-scoped caller (`bc-core:src/evidence/evidence.controller.ts:24-117 @ ec72438b`).
- **Main defects:**
  - Best-effort evidence at two boundaries contradicts Invariant VI.
  - Evidence can be written by hand, outside any boundary act.
  - Canonical evaluation writes no lineage object.
- **Locked means:**
  - Every boundary act writes its evidence and lineage in the same transaction as its object, and a test fails when evidence is missing.
  - No route creates evidence or lineage outside a boundary act; a CI guard fails on a new one.
- **Full dossier:** [EV, Evidence and lineage](platform-refactor-program/functions-runtime-delivery-support.md#ev-evidence-and-lineage)

### PV, Proof against the source
- **What it is:** Proof against the source asks whether the value the platform produced agrees with a value worked out independently from the same source data for the same period. Today it is done on the demo plane.
- **State today:**
  - Four proof pins exist, all with outcome `match` (query (bc_platform_dev, 2026-11-13): `select demo_world_version, metric_contract_version, comparison_outcome, created_at::date from demo.metric_proof_pin` -> four rows, all `match`, each at version `1.0.0`).
  - No expected value is worked from the source system (query (bc_platform_dev, 2026-11-13): `select demo_world_version, period_label, independent_author, authored_at::date from demo.oracle_custody` -> three rows; independence tier `synthetic-fixture` on two and `admitted-recompute` on one).
  - Version pins are constants in code (`bc-core:src/database/plane/plane-metric-version-binding.ts:52 @ ec72438b`).
- **Main defects:**
  - No bc-docs chapter defines the function.
  - The expected value is not worked from the source system (open ruling B5).
  - Each new contract version needs a hand-written migration and table.
- **Locked means:**
  - One chapter defines the proof, its record and its words, and the vocabulary names the record for condition 4 of "done".
  - A new contract version can be proven with no new migration and no hand-written table.
- **Full dossier:** [PV, Proof against the source](platform-refactor-program/functions-runtime-delivery-support.md#pv-proof-against-the-source)

**Delivery**

### DL, Delivery to a tenant
- **What it is:** Delivery to a tenant is how a certified metric reaches one tenant and is consumed there. Its ladder has five steps: available, subscribed, enabled or disabled, visible or hidden, and reporting. It also covers the package and the Subscription record.
- **State today:**
  - Only enablement is built, as a direct API call (`bc-core:src/schema-provisioner/connector-onboarding.controller.ts:40-61 @ ec72438b`).
  - No table exists for a Subscription, an entitlement, a release or visibility (query (bc_platform_dev, 2026-11-13): `select table_schema, table_name from information_schema.tables where table_name ~ 'subscription|entitlement|visibility|metric_release|portfolio'` -> no rows).
  - A newly active contract version is delivered to every bound tenant automatically (`bc-core:src/schema-provisioner/contract-activation.service.ts:1-21 @ ec72438b`).
- **Main defects:**
  - Nothing checks subscription, enablement or visibility before evaluation.
  - A new version reaches tenants with no acceptance, against ruling T3.
  - The package table cannot express the model of ruling T1.
- **Locked means:**
  - One resolver answers "may this tenant run this metric, at which version", and evaluation and the tenant's list both call it.
  - A value-affecting version change does not reach a tenant without an acceptance record, proven by a test.
- **Full dossier:** [DL, Delivery to a tenant](platform-refactor-program/functions-runtime-delivery-support.md#dl-delivery-to-a-tenant)

### TS, Tenant self-service
- **What it is:** Tenant self-service is the customer portal, the application a tenant's own users sign in to. They see their metrics and values, declare legal entities and fiscal calendars, and register connections. The portal is the repository bc-portal.
- **State today:**
  - Sign-in, the dashboard, the metric pages, legal entities and connections work (`bc-portal:apps/web/src/components/AppRouter.tsx:119-184 @ 04930c8`).
  - Five files show sample data under a notice (command: `git grep -l SampleDataNotice origin/main -- apps/web/src`, excluding `_archived`).
  - When a metric is not reporting, "the screen gives no reason" (`bc-docs:docs/reference/vocabulary.md:176 @ f4f5edd`).
- **Main defects:**
  - One dashboard page mixes sample facts with governed values.
  - The support page calls a platform-only route.
  - The governing chapter calls itself a stub.
- **Locked means:**
  - Every page shows either governed data or nothing; no page mixes sample facts with a tenant's values.
  - The portal calls only tenant-scoped routes, checked by a test over its API clients.
- **Full dossier:** [TS, Tenant self-service](platform-refactor-program/functions-runtime-delivery-support.md#ts-tenant-self-service)

### A1, Action and intervention
- **What it is:** An Action Object is a declared intent bound to one or more Metric Snapshots, with its outcome recorded. An intervention contract says when an action is created and how its outcome is resolved. This boundary is designed in Foundation and is not built.
- **State today:**
  - The governing chapter carries the note "As-built: implementation absent (fail-closed)." (`bc-docs:docs/operating-model/action-evaluation.md:33 @ f4f5edd`).
  - The platform tables are empty (query (bc_platform_dev, 2026-11-13): `select count(*) from contract.intervention_contract`; `select count(*) from contract.intervention_contract_version` -> 0 contracts, 0 versions).
  - The portal's intervention pages read a static file (`bc-portal:apps/web/src/surfaces/dashboard/dashboardIntervention.data.ts:1-12 @ 04930c8`).
- **Main defects:**
  - The portal shows intervention pages for a capability that does not exist.
  - No decided ADR designs the action evaluator.
  - A chapter names a reversed ADR as the future authority.
- **Locked means:**
  - The guide lists the function as designed, not built, with the Foundation text as its definition.
  - No screen presents an action as real.
- **Full dossier:** [A1, Action and intervention](platform-refactor-program/functions-runtime-delivery-support.md#a1-action-and-intervention)

### NT, Notifications and webhooks
- **What it is:** Notifications and webhooks are how the platform tells someone outside an act that the act happened. As built, it records a completion event for each runtime act, raises a support ticket from some events, and can deliver signed webhooks. It sends no email.
- **State today:**
  - The event outbox, the ticket consumer and webhook delivery are built (`bc-core:src/boundary/runtime-event.service.ts:1-10 @ ec72438b`).
  - The governing chapter says the opposite: "The surface is not stubbed-with-disabled-deliveries; it is structurally absent." (`bc-docs:docs/implementation/notifications-and-webhooks.md:56 @ f4f5edd`).
  - No endpoint is in use (query (bc_platform_dev, 2026-11-13): `select is_active, (archived_at is not null), (tenant_id is null), event_types from runtime.webhook_endpoint` -> 3 rows, all inactive and archived, none tied to a tenant).
- **Main defects:**
  - The chapter says the function is absent, so a session may build a second.
  - No ADR authorizes outbound webhooks.
  - Nothing tells a tenant about a pending version, which ruling T3 needs.
- **Locked means:**
  - The chapter matches the code, and an ADR authorizes each channel that exists.
  - The notice ruling T3 requires has a defined record and channel, or is listed as designed, not built.
- **Full dossier:** [NT, Notifications and webhooks](platform-refactor-program/functions-runtime-delivery-support.md#nt-notifications-and-webhooks)

**Support**

### PR, Privacy and retention
- **What it is:** Privacy and retention is how the platform erases a person's data on request and limits how long personal data is kept, while its records stay immutable. The mechanism is nullification: a field is overwritten with a sentinel value while the row remains.
- **State today:**
  - The request lifecycle is built, and every route is platform-only (`bc-core:src/nullification/nullification.controller.ts:24-93 @ ec72438b`).
  - The only request on record changed nothing (query (bc_platform_dev, 2026-11-13): `select request_type, legal_basis_code, status_code, fields_scanned, fields_nullified, s3_objects_handled, submitted_at::date from operations.nullification_request` -> one erasure, `completed`, 0 fields scanned, 0 nullified, 0 S3 objects handled).
  - No schedule invokes retention (command: `git grep -n "@Cron(" origin/main -- src`, excluding specs -> 3 matches, none in `src/nullification`).
- **Main defects:**
  - The mechanism has no recorded real run.
  - Retention runs only when an admin calls the route, and no policy exists.
  - Archived copies still show original personal data to readers.
- **Locked means:**
  - One erasure has been run end to end on a test subject, with action rows and evidence, by the written procedure.
  - Every table that holds personal data is in the registry, checked by a CI guard over the schema.
- **Full dossier:** [PR, Privacy and retention](platform-refactor-program/functions-runtime-delivery-support.md#pr-privacy-and-retention)

### MD, Master data
- **What it is:** Master data is the reference data that other functions look up and do not author: countries, currencies, dates, fiscal calendars, business functions and subfunctions, industries and lists of allowed values. It also includes the legal entities a tenant declares.
- **State today:**
  - Its routes are read only; platform lists change only through seed scripts run by hand (`bc-core:src/platform/masters/masters.controller.ts:13-142 @ ec72438b`).
  - Three fiscal calendars are named (query (bc_platform_dev, 2026-11-13): `select to_jsonb(d)->>'fiscal_calendar_code' from master.dim_fiscal_calendar d` -> `IN-APR-MAR-MONTHLY`, `US-CAL-MONTHLY`, `UK-APR-MAR-QUARTERLY`).
  - The generated dictionary is dated 2026-07-06 (`bc-docs:docs/reference/data-dictionary/master.md:1-14 @ f4f5edd`).
- **Main defects:**
  - No chapter defines the function or names its owner.
  - A change to a master list has no act, evidence or review route.
  - The scheduler takes legal entities from an environment variable, not the tenant's record.
- **Locked means:**
  - One chapter lists every master table with its owner and the one act that changes it.
  - No evaluation setting names a legal entity or calendar outside its record.
- **Full dossier:** [MD, Master data](platform-refactor-program/functions-runtime-delivery-support.md#md-master-data)

### AI, AI services
- **What it is:** AI services are the AI panels the platform uses to draft and to judge governed content, the vendors those panels call, and the record of what each call cost. There are four panels, and all run inside bc-core.
- **State today:**
  - The panels run (query (bc_platform_dev, 2026-11-13): `select max(created_at)::date from bcf.panel_output_record`; `select max(created_at) from mcf.metric_authoring_panel_run`; `select max(created_at) from mcf.audit_contextual_panel_run` -> 2026-11-12, 2026-11-04 and 2026-09-30).
  - The cost ledger stopped in June (query (bc_platform_dev, 2026-11-13): `select min(started_at)::date, max(started_at)::date, round(sum(actual_cost_usd)::numeric,2) from ai_telemetry.ai_run_ledger` -> 2026-06-17 to 2026-06-19, 38.86 USD).
  - Seven chapters still describe the retired service: "bc-ai is the platform's single AI service." (`bc-docs:docs/ai/ai-architecture.md:41 @ f4f5edd`).
- **Main defects:**
  - The documented roster is not the roster that runs.
  - Cost is not recorded per run after June 2026.
  - A vendor change must be made in up to four places.
- **Locked means:**
  - One chapter describes the panels as they run; the bc-ai chapters are marked as history.
  - One module calls vendors; a CI guard fails on a vendor address outside it.
- **Full dossier:** [AI, AI services](platform-refactor-program/functions-runtime-delivery-support.md#ai-ai-services)

### SU, Support
- **What it is:** Support is how a problem with the platform or a tenant's data becomes a tracked ticket and is resolved. As built, the platform raises tickets automatically when a runtime act fails or a contract is violated, and operators work them. A tenant cannot open a ticket.
- **State today:**
  - The ticket routes are platform only (`bc-core:src/support/support.controller.ts:20-84 @ ec72438b`).
  - Every ticket was raised by the platform (query (bc_platform_dev, 2026-11-13): `select category_code, source_code, status_code, count(*) from support.ticket group by 1,2,3` -> 6,227 tickets, all with source `system`; `contract_violation` 6,171 closed and 33 open).
  - The portal's support page calls `GET /support/tickets?limit=100` (`bc-portal:apps/web/src/api/support.ts:52-53 @ 04930c8`).
- **Main defects:**
  - The portal's support page depends on a platform-only route (refusal not tested).
  - 39 tickets are open; none has been created since 2026-10-20.
  - The governing chapter does not mention the built ticket store.
- **Locked means:**
  - The chapter describes the ticket store, its automatic triggers and who works it.
  - The portal's support page either calls a tenant-scoped route or is removed.
- **Full dossier:** [SU, Support](platform-refactor-program/functions-runtime-delivery-support.md#su-support)

**Running the platform**

### OP, Operations
- **What it is:** Operations is how the platform is run and changed: environments, serving a build of bc-core, settings and secrets, schema changes, database logins, backup and restore, CI and cloud infrastructure.
- **State today:**
  - bc-core on port 3100 runs from `~/MyProjects/_wt/freeze-1055` at `ec72438b` (command: `lsof -a -p <pid of the listener on 3100> -d cwd` -> that path; `~/bc-stack/process-compose.yaml` lines 91-95).
  - Four migrations on bc-db `main` have no ledger row: 0032, 0034, 0035 and 0038 (command: `ls-tree migrations` @ c6de1c4 compared with the ledger query).
  - Of six stack definitions, three are deployed; the platform runs only on the Mac (command: `aws cloudformation list-stacks` -> those three among BareCount names; `aws rds describe-db-instances` -> none).
- **Main defects:**
  - No restore of a nightly backup has been shown to work.
  - The serve procedure in use is undocumented and has no committed script.
  - No reference run exists to show engine changes leave results unchanged.
- **Locked means:**
  - One written serve procedure has one committed script.
  - The reference run exists, runs from a fixed input, and its result is required before engine code merges.
- **Full dossier:** [OP, Operations](platform-refactor-program/functions-shared-services-operations-development.md#op-operations)

### DV, Development
- **What it is:** Development is the set of tools and rules by which the platform is changed: DevHub, bc-docs, ADRs, the auditor exchange with the approval desk, and memory files with change records.
- **State today:**
  - DevHub has 66 tables and 110 tools (query (devhub.db, 2026-11-13): `select count(*) from sqlite_master where type='table' and name not like 'sqlite_%'` -> 66; `select count(*) from mcp_tool_registry` -> 110).
  - The anchor shown to a session points at the parked drive (query (devhub.db, 2026-11-13): `select program_uid, blueprint_path_text, substr(blueprint_commit_sha,1,8), pinned_at from active_program where retired_at is null` -> `demoed-terminal | blueprints/demoed-terminal.md | 77d882af`).
  - The document index reads a bc-docs copy 141 commits behind `main` (command: `git -C bc-docs rev-list --count HEAD..origin/main` -> 141).
- **Main defects:**
  - A session is shown the parked program on every turn.
  - The document index cannot be trusted.
  - Nothing obliges a session to read or update a chapter.
- **Locked means:**
  - The anchor is the current program, and a check fails when the pinned document is not on `main`.
  - The document index is built from bc-docs `main` and states its age.
- **Full dossier:** [DV, Development](platform-refactor-program/functions-shared-services-operations-development.md#dv-development)
