---
title: Platform Readiness — Evidence Manifest (2026-09-19 grounding)
status: evidence
date: 2026-09-19
supports: implementation/platform-readiness-program.md §3 (the function readiness matrix)
session: SES-982650
---

# Platform Readiness — Evidence Manifest (2026-09-19)

Durable, reproducible evidence for the function × {backend, DB, UI} readiness matrix in
`platform-readiness-program.md` §3. Every RAG rating there resolves to a row below. Where an
input could **not** be verified (notably the tenant-DB runtime plane), the matrix marks the
cell **unknown (❓)**, not green — see §Verifiability limits.

## Method

- **Backend / UI:** read-only static inspection of the repositories at the pinned commits
  (below), by three read-only agents (no writes, no execution). Evidence is `file:line`.
- **DB:** live counts against `bc_platform_dev` via the `bc-postgres` MCP, **read-only**
  (`information_schema` + read-only `SELECT count(*)`; the `pg_list_tables` helper was broken
  and `pg_count`/`pg_describe_table` were allowlist-limited, so enumeration used
  `information_schema.tables`/`.columns` and counts used `SELECT count(*) FROM <relation>`).
- **ADR statuses:** read from the DevHub decision registry **and** the ADR files under
  `docs/governance/adrs/`, with all 588 ADRs reconciled to functions (6 read-only agents) plus
  the Tier-1 hygiene audit (`scripts/docs-control/audit_adrs.py`).
- **Collection date:** 2026-09-19. Counts are a **snapshot**; live status remains git/PR/DevHub.

## Environment & commit pins (reproduction basis)

| Surface | Identifier |
|---|---|
| Platform/registry DB | `bc_platform_dev` (PostgreSQL 17.11), schemas: `bcf, concept_registry, contract, master, mcf, metric, runtime, source, tenant, users, pricing, operations, schema_provisioner, infrastructure, execution` |
| **Tenant DB(s)** (`tbc_*`: `fact.*`, `progression.*`) | **NOT accessible** under the MCP allowlist → **unverified** |
| bc-core | `b80f10a79259e59e58858c1160b71505722823d1` (local HEAD; shared tree — bounded corroboration, not deployed-state attestation) |
| bc-admin | `0c94e241ecc4d2db24c84115f61e034e1517c1cb` |
| bc-portal | `3db7f0e57f1e93450bfe5d7023fc3b233d803462` |
| bc-docs (this PR head) | `adb1d0a4a6f2aa2d7c4f4c8ffd9599562eabbfcc` |

## Cert populations — two distinct relations (do not conflate)

- **L6** cites `mcf.certification_record` = **1316** rows — the MCF-native metric-certification substrate.
- **EV** cites `contract.certification_record` = **3530** rows — the contract-family certification records (matches the "3,530 rows" cited in DEC-c48b0f).
These are different relations in different schemas; both counts are registry-side (verified).

## Per-function evidence

| Fn | Backend (file:line @ bc-core) | DB relation · live count (bc_platform_dev) | UI (route/page @ bc-admin unless noted) | Verifiability |
|---|---|---|---|---|
| S1 Auth | `auth/auth.module.ts:27-30` (4 global guards) · `auth/strategies/cognito-jwt.strategy.ts` | `users.platform_user`=0 (Cognito is IdP; minimal by design) | `LoginPage.tsx` (admin + portal) | verified |
| S2 User/access | `auth/cognito-admin/user-provisioning.controller.ts` (POST /admin/users) | no roles/permissions/`owner_assignment` tables; `users.platform_user`=0 | `/platform/users` → `PlaceholderPage` (AppRouter.tsx:264) | verified |
| S3 Tenant lifecycle | `tenant-management.controller.ts:21`; `schema-provisioner/*` | `tenant.tenants`=1; `status_code` CHECK={active,suspended,archived,provisioning,failed}; `tenant_binding`=24; `onboarding_record`=0; `contract_binding`=0; `tenant_infrastructure`=1 | `TenantsPage`/`TenantDetailPage`/`TenantCreatePage`; `tenant/{configuration,health,scoping,infrastructure}`→Placeholder (AppRouter:232-235) | verified (registry) |
| S4 Pricing | no Stripe in `package.json`; `registry/execution/package.service.ts` = D086 reader tiers | `pricing.package`=7 (reader-manifest tiers; no price/amount/currency cols) | pricing subpages→Placeholder (AppRouter:275-277); `PackagesPage` real | verified |
| S5 Operator console | bc-admin app (~75 pages, 255 commits) | — | `LeftSidebar.tsx`/`AppRouter.tsx` | verified |
| L1 Source Catalog | `source-catalog.controller.ts:36-411`; `register-source-stack.controller.ts:17` | `source.*`=12 tables; `source_system`=1; `source_object`=305; `source_field`=9850 | `sources/onboard`,`sources/catalog/systems` | verified |
| L2 SC+AC | `contract.controller.ts:26`; `register-source-stack.controller.ts:17` | `contract.source_contract`=305; `admission_contract`=305 | `registry/contracts/{source,admission}`(+`/new`) | verified |
| L3 BCF | `bcf/registry-authoring.controller.ts:128`; `registry-read.controller.ts:47` | `concept_registry.*`=18 tables; `business_concept`=815; `entity`=154; `characteristic`=234 | `business-concepts/*` console | verified |
| L4 OC | `author-observation-chain.controller.ts:21` | `contract.observation_contract`=7; `observation_field_map`=**0** | `registry/contracts/observation`; author via metric `author-chain` | verified |
| L5 CC | `ccv2-canonical-resolver.controller.ts:23`; `publish-chain.controller.ts:18` | `contract.canonical_contract`=5; `canonical_mapping`=**0** | `registry/contracts/canonical` (list only; CC wizards removed, AppRouter:152-153) | verified |
| L6 MCF | ~40 `mcf/*` controllers (`mcf-intake`, `mcf-publication-activation`, …) | `mcf.metric_contract`=432; `metric_contract_version`=432; `metric_variable_binding`=738; `mcf.certification_record`=1316 | `catalog/metrics`,`/register`,`/governed/:uid` | verified |
| L7 Reader | `reader.controller.ts:35`; `connector.controller.ts:22`; `connection.controller.ts:23` | `runtime.reader`=5; `connector`=3; `connection`=1; `reader_observation_binding`=5 | `registry/readers`(+`/new`),`connectors`,`connections` | verified |
| L8 Directory | `metric-directory.controller.ts:107` (@PlatformOnly, DEC-b5c7ff/D506) | `metric_directory` family=47/group=135/member=415/member_version=247/realization_event=263; `mcf.seed_metric`=12507 | `catalog/metrics/register` (registration) present; **directory tree = no door** (0 bc-admin refs) | verified |
| L9 Chain Integrity | `mcv-chain-status.controller.ts:13`; `chain-audit.controller.ts:37` | `mcf.mcv_chain_status`=318; `chain_audit_evidence`=127; `mcv_package_snapshot`=312; `mcv_live`=70 | `catalog/metrics/readiness` (status); `chain_audit_evidence` = **no door** | verified |
| L10 Tenant Onboarding | `tenant-management.controller.ts:21`; `schema-provisioner/connector-onboarding.controller.ts:42` | `tenant.onboarding_record`=0; `tenant_infrastructure`=1 | `platform/tenants`(+`new-tenant`,`:slug`); 4 tenant tabs=stubs | verified (registry) |
| RT Runtime engine | `boundary/admission.repository.ts`; `admission-batch.service.ts`; `reader-runtime/resolved-admission-context.ts`; `governed-metric-evaluation.service.ts` (wired `boundary.module.ts:107`) | **registry substrate verified:** `runtime.admission_run`=5; `admission_run_context`=5. **tenant-runtime UNVERIFIED:** `fact.*`, `progression.*` not accessible | no bc-core UI; `admin-inspection.controller.ts` (backend) | **split**: registry verified / tenant-runtime **unknown** |
| EV Evidence/audit | `evidence/evidence.service.ts:147-240` (hash-chain, atomic proof, PR #704 live) | `contract.certification_record`=3530; `mcf.mcv_chain_status`=318 | `readiness.controller.ts`,`admin-inspection.controller.ts` (no inspector UI verified) | verified (registry) |
| TS Tenant self-service | bc-portal `surfaces/auth`, `dashboard`, `workspace/*` | — (tenant data plane, unverified) | `MetricCatalogListPage` (API-driven) real; `setup/OrganizationPage.tsx` static shell | verified (code); data plane unverified |
| A1 Action/Intervention | — (no design) | — | — | design pending (no artifact) |

## Verifiability limits (unknowns preserved)

- **Tenant-DB runtime plane** (`fact.so_*`, `fact.ms_*`, `progression.*`) is **not inspectable**
  under the current MCP allowlist. Any rating that would depend on it is marked **❓ unknown**,
  never green. RT DB is therefore recorded as **registry-verified / tenant-runtime unknown**.
- **Code reads are same-day working-tree snapshots** on shared repos at the pins above —
  bounded corroboration of source, not attestation of deployed/runtime state.
- **ADR statuses** are a 2026-09-19 snapshot of the registry + files; the reconciliation of all
  588 ADRs and its punch-list are recorded as DevHub tasks (tag `platform-readiness-punchlist`).

## Reproduction

1. Check out the pins above. 2. For each DB relation, run `SELECT count(*) FROM <schema>.<relation>;`
against `bc_platform_dev`. 3. For backend/UI, open the cited `file:line`. 4. For ADR status, read
`docs/governance/adrs/ADR-<uid>.md` frontmatter and cross-check the DevHub registry. Counts may
have advanced since the snapshot date; treat divergence as drift to reconcile, not as error.
