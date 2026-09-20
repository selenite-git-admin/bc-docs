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
- **Live UI (added 2026-09-19):** for capability/"is-it-done" claims, static inspection is
  necessary but **not sufficient** — it establishes component-presence, not working capability,
  and can mislabel a by-design pattern as a gap. The L4/L5 authoring **surface** was inspected by
  **running bc-core (:3100) + bc-admin (:3010) and driving the actual UI** — this establishes
  navigation + form presence + the demand-pull design, **not** a successful author execution (no
  dry-run digest / run-id / resulting chain refs were captured; see the L4/L5 rows + the addendum).
  A "complete/tested-in-UI" claim needs an actual execution record, not route-reading and not a form visit.
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
| L4 OC | `author-observation-chain.controller.ts:21` | `contract.observation_contract`=7; `observation_field_map`=0 (retired legacy resolver table — mappings in OC body) | authoring surface present + wired — the metric-pulled observation-chain console (metric detail → "Author observation chain (OC + reader + CC)"); standalone `registry/contracts/observation` list-only by design. **Verified this pass: navigation + form presence only** — no dry-run digest, author run-id, or resulting OC/CC refs recorded (execution unverified) | form/navigation verified |
| L5 CC | `author-observation-chain.controller.ts:21`; `publish-chain.controller.ts:18` (CC leg) | `contract.canonical_contract`=5 (fields+mappings populated); `canonical_mapping`=0 (retired legacy resolver table) | CC-v2 body authoring in the same console; standalone `registry/contracts/canonical` list-only + dedicated wizards removed (D418) — both by design. **Verified this pass: navigation + form presence only**, not a successful author run | form/navigation verified |
| L6 MCF | ~40 `mcf/*` controllers (`mcf-intake`, `mcf-publication-activation`, …) | `mcf.metric_contract`=432; `metric_contract_version`=432; `metric_variable_binding`=738; `mcf.certification_record`=1316 | `catalog/metrics`,`/register`,`/governed/:uid` | verified |
| L7 Reader | `reader.controller.ts:35`; `connector.controller.ts:22`; `connection.controller.ts:23` | `runtime.reader`=5; `connector`=3; `connection`=1; `reader_observation_binding`=5 | `registry/readers`(+`/new`),`connectors`,`connections` | verified |
| L8 Metric Directory | `metric-directory.controller.ts:107` (@PlatformOnly, DEC-b5c7ff/D506) | `metric_directory` family=47/group=135/member=415/member_version=247/realization_event=263; `mcf.seed_metric`=12507 | **live-verified (post-audit-fix, bc-admin `04b796f`):** Metric Directory UI at `catalog/metrics/directory`. Auditor findings addressed across two rounds: **group create w/ required grain** (Groups 135→136 live), **derived realization** via `members/realized`, **contract links → `catalog/metrics/governed/:uid`** (governed detail, not the retired 410), **rejection text** (no contract materialized; intake+run retained); and the r2 remainder — **Realized facet on `realization_source`** so `audit_pending` realized rows count (Realized **246 live**, was 53; lifecycle labels preserved), and **GroupsPane read-failure handling** (error state, not silent "No groups"). Green pinned to PR #45, pending auditor re-review of `04b796f` | verified + live UI |
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

## Update 2026-09-19 (sync — seam closures + S4/L10 dispositions)

Post-grounding deltas verified the same day. The bc-core pin above (`b80f10a7`) predates the
seam-#2/#3 merges below; `main` has advanced past it.

**RT seam class — CLOSED (all merged to bc-core `main`, each RED→GREEN on real Postgres + disposable-DB CI regression):**
- seam #1 `source_key` — PR #726.
- seam #2 provisioner `findSourceContractsForCanonical` → `COALESCE(sc_contract_id, sc_version_id)` — PR #770, merge `15cdbc37`; regression spec `schema-provisioner.source-contract-key.integration.spec.ts` in the `e6b-db-integration` job.
- seam #3 admission `fact.so_` SC-keying — batch PR #769 merge `eeb3d161`; HTTP single-record + repository fail-closed guard PR #772 merge `9fb10d98`; regression spec `admission.repository.dual-write.integration.spec.ts` added to `e6b-db-integration` (verified executed, not skipped: CI log `✓ 3 tests`).
- Auditor dispositions byte-verified (SHA-256) per merge; TSK-338f06 completed.

**S4 Pricing — grounded, confirms deferred-by-decision / out of readiness scope:**
- `pricing.package`=7 rows: a `Free` row (`tier_order`=0, `status_code`=active, `reader_manifest_json`=**NULL**) + `custom` (active) + 5 tiers (finance-essentials/complete, full-erp, crm, hr) all `deprecated`+`archived_at`=2026-08-13.
- **The `Free` package's seed/genesis provenance is a Platform DB Foundation matter, not adjudicated here.** It is present in the live catalog and in `docker/redesign/golden-snapshot-source.sql`; it is **not** in the two application-seed files inspected (`seed-v2/data/pricing/packages.csv`, `src/registry/seed/seed-packages.ts DEFAULT_PACKAGES`, both emit the six tiers). Whether the from-zero **canonical seed layer** deterministically reproduces it is a DB-Foundation genesis-reconciliation question ([[TSK-ca2f7d]]). (Correction: an earlier draft of this addendum called it "seed drift" from the seed-file check alone — that check did not cover the golden-snapshot/genesis path and the conclusion is retracted; schema/seed provenance and any change route through DB Foundation under the Database Change Protocol.)
- **No tenant→plan binding anywhere:** no `package_id`/plan column or FK on `tenant.tenants`, `tenant.onboarding_record`, or `tenant.tenant_binding` (that binds source contracts); 0 informal refs in `tenants.config_json` / `onboarding_record.detail_json`. Operator package-catalog CRUD (`/packages` + bc-admin `registry/packages`) is wired; the tenant "Subscription" page (bc-portal) is a hardcoded mock. Consistent with `tenant-onboarding.md` v1 = single flat band, no subscription instantiated.

**L10 Tenant Onboarding — onboarding lane READY; operational tabs → S5 (deferred):**
- E2E proof `src/tenant-management/tenant-provisioning-api.integration.spec.ts` **runs in the `e6b-db-integration` CI job** (BCCORE_INTEGRATION_DB=1) — provisions a throwaway tenant, asserts `status:'active'` + evidence + D575 immutability triggers. (Corrects the "gated/skipped" reading — it is in the explicit vitest list.)
- BE `tenant-management.controller.ts` + `tenant-provisioning-api.service.ts` fail-closed; DB tenant-skeleton (6 schemas, 26 tables) hash-verified. `onboarding_record`=0 is an empty-state (no tenant onboarded yet), not a schema gap.
- The four operational tabs (`configuration/health/scoping/infrastructure`, `PlaceholderPage`) are post-onboarding tenant operations → reclassified to **S5** operator-console, deferred.

**E6-B / FND-VI — closure DEFERRED (not closeable from the dev host):** emit is unconditional on `main` (`governed-metric-persistence.adapter.ts:216`), DBCP applied to `tbc_pilot1_dev`. But `tbc_pilot1_dev` is **not on the local host** (only a throwaway `tbc_probe_unit4_dev` is local) — pilot1 is remote. Closure requires an *observed* real metric finalize + auditor-store health (operator-only); a synthetic local metric is the documented rabbit-hole.

**L4/L5 OC/CC — live-UI verification (2026-09-19), correcting a static-only 🟡.** Ran bc-core (:3100) + bc-admin (:3010) and drove the UI: (1) standalone **Observation Contracts** and **Canonical Contracts** pages are **list-only by design** (filters/search/pagination, no create button; 3 active OCs, 3 active CCs with fields+mappings). (2) OC+CC are authored **on-demand from a metric** — the metric detail page carries "**Author observation chain (OC + reader + CC) for this metric's entity →**", and the console header reads *"Chain for Customer Invoice — pulled by Accounts Receivable Turnover"* (demand-pull confirmed). The console renders a real form (entity/function/source fields + `observations` legs + `canonical` CC-v2 body + a Dry-run action). (3) **Execution boundary (auditor PR#39):** this pass recorded **navigation + form presence only** — no successful dry-run response/plan digest, no authoring outcome/run-id, and no resulting OC/CC chain references were captured; the authoring *execution* is therefore **unverified** here. The Metric Catalog's **335 contracted / 70 active** are catalog counts (`metric_contract` count × `governance_state_code`) and do **not** establish which OC/CC authoring path ran — that inference is withdrawn. Conclusion: the **demand-pull / list-only design** is confirmed, and the authoring **door is present + wired** (L4/L5 UI 🟢 = *door present* per the matrix legend); a successful author *run* was not established here and remains a separate verification. The earlier 🟡 (from static route-reading) mislabeled a deliberate demand-pull flow as a gap.

## Execution records (OC/CC/directory) — 2026-09-20 (SES-9c706c)

Lifts the L4/L5/L8 "execution unverified / door present only" boundary recorded above. Method:
**run-the-app against the governed endpoints on the running server** (not source-read, not a form
visit) + **read-only substrate reads** of the durable execution ledgers. Pins: bc-core `b80f10a7`
(`main`), bc-admin `93c4c4d`, DB `bc_platform_dev`, endpoint `POST /api/contracts/observation-chains`
(`@PlatformOnly` + `@Roles('platform_admin')`), token minted for `platform_admin`. **No new residue
this pass** — the L4/L5 evidence is a dry-run (Inv V, zero write) plus reads of pre-existing rows.

### L4/L5 — observation-chain authoring (OC + reader + CC), `POST /api/contracts/observation-chains`

**(a) This-pass observed dry-run (rung 2 — successful execution, zero write).** Replayed the
known-good `jeSpec` from `src/registry/substrate/author-observation-chain.dryrun.integration.spec.ts`
(journal_entry exemplar, entity `6e47ef23`, `account.move` SC `019fe42b-7f2b`@1.0.0 / AC
`019fe42b-7fe8`**@1.1.0**) through the running endpoint:

- HTTP **200**; response `data.outcome` = `dry_run`; `data.dryRunPlan.businessObjectCode` = `journal_entry`;
  `data.planDigest` = `2a61aa5675b6e31e3c9e68ab667250dc97606efb763565fb862ef9097048e068` (64-hex).
- **Deterministic:** two consecutive calls returned the identical digest.
- **Inv V (no write):** `SELECT count(*) FROM runtime.chain_authoring_run WHERE admitted_entity_id='6e47ef23…'`
  = **1 before AND after** both dry-runs (unchanged).

**(b) Fail-closed active-pin proof (bonus — the door is an evaluation boundary, not a form).** The
first attempt pinned the AC at its *historical* version `@1.0.0` and was **refused 400**: *"leg
je_primary: admission contract 019fe42b-7fe8-776d-a9af-19517b6bb43d@1.0.0 is not active."* Substrate
confirms why: that AC version is `superseded` (supersede_after 2026-09-09); the **active** version is
`1.1.0` (created 2026-09-07); SC `019fe42b-7f2b`@1.0.0 remains active. The dry-run resolved only after
repinning to the active AC — i.e. the authoring boundary enforces contract-version currency.

**(c) Historical committed author runs (rung 3 — durable ledger).** `runtime.chain_authoring_run`
holds **3 `committed` runs (2026-08-14, env dev)**, each with `state_code='committed'`, a recorded
`plan_digest`, and `chain_authoring_step` rows for `canonical_contract` + `observation_contract` +
`reader_flavor` (all `written`):

| run_id | plan_digest (16) | entity (refId) | OC (live) | CC (live) | reader |
|---|---|---|---|---|---|
| `2ba35ba6` | `492453a2ed7b34fc` | `6e47ef23` (je_primary) | `45f8b60c` ✓ | `7fa4b84f` ✓ | `13a0bc42` |
| `85edf073` | `6ca8f36ba1a5c032` | `0e1a0035` (cost_center_primary) | `9bd23f1e` ✓ | `cbe39b9e` ✓ | `919b5dc3` |
| `9fd9bd92` | `0afdfac4538a8f62` | `dae813b3` (product_primary) | `16839a7a` ✓ | `48aca58b` ✓ | `16a1abfc` |

All 3 OC targets are live in `contract.observation_contract` and all 3 CC targets in
`contract.canonical_contract` (`archived_at IS NULL` verified). (Plus 2 `abandoned` OC-only runs
2026-08-15 — the abandoned-run recovery path.) **Conclusion:** the L4/L5 door has authored 3 real
chains end-to-end with recorded digests → live OC+CC+reader, and reproduces a deterministic dry-run
digest this pass. "No author execution recorded" is retired; L4/L5 UI legend → **author execution recorded**.

### L8 — Metric Directory create doors (executed 2026-09-19, SES-b20b26; rows verified live this pass)

Governed rows authored through the shipped Metric Directory UI (bc-admin PR #45 → `800cdca`), all by
`anant@selenite.co`, confirmed live by read-only substrate query:

| door | table | uid | identity | created_at |
|---|---|---|---|---|
| New Family | `metric_directory.family` | `7fa70579-ba4e-4728-9e46-32a9a6e1d845` | finance/treasury · theme `fx_exposure_and_hedging` | 2026-09-19T15:52Z |
| New Group | `metric_directory.group` | `d8014337-d2ca-4631-87da-26d8c6233206` | `je_line_grain_probe` (grain-entity required) | 2026-09-19T16:43Z |
| Author metric (M12 panel) | `mcf.metric_authoring_panel_run` | `cf6f50ea-26a8-4275-bb79-4af0c7c4a4bd` | verdict `APPROVE_FOR_DRAFT` | 2026-09-19T15:35Z |
| Materialize (M12.5) | `mcf.metric_contract` | `177b865b-253b-4132-8c1c-b06bedec3403` | `supplier_invoice_cycle_time` (draft) | 2026-09-19T16:24Z |

### Reproduction

- Dry-run: `POST /api/contracts/observation-chains` with `{dryRun:true, spec:<jeSpec, AC@1.1.0>}` and a
  `platform_admin` bearer token → 200 `data.outcome=dry_run`, `data.planDigest` as above. (Probe:
  session scratchpad `oc-cc-dryrun-probe.mjs`; response is wrapped under `data`.)
- Ledger: `SELECT run_id,state_code,plan_digest FROM runtime.chain_authoring_run WHERE state_code='committed'`
  and join `runtime.chain_authoring_step` on `run_id` for the per-target uids; verify targets live in
  `contract.observation_contract` / `contract.canonical_contract` (`archived_at IS NULL`).
- Directory rows: `SELECT … FROM metric_directory.family|group`, `mcf.metric_authoring_panel_run`,
  `mcf.metric_contract` filtered to `created_at::date >= '2026-09-19'`.

**Verifiability note:** rung-3 for L4/L5 is *historical* (committed runs are 2026-08-14, `created_by_name`
NULL); this pass adds a *live-observed* dry-run + the fail-closed proof, not a fresh committed author
(which would write new OC/CC/reader residue). That remains available as a further step if an auditor
requires a this-pass committed author; it is intentionally not run here to avoid avoidable residue.
