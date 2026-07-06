---
id: synthetic-data-and-testing
order: 26
title: "Synthetic Data and Testing"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-authority-model, operating-model-overview, evidence-and-lineage, architecture, backend-services, internal-modules, infrastructure, api-surface, audit-and-activity-logging]
governing_sources:
  - Foundation
  - The Authority Model
  - Operating Model
  - Evidence and Lineage
  - Architecture
  - Backend Services
  - Internal Modules
  - Infrastructure
  - API Surface
  - Audit and Activity Logging
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; this chapter exists in the reshaped Implementation section)
  - DEC-e50b83 (Master port reservation; bc-sdg's main and SAP ECC simulator ports are out-of-band against this reservation)
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules)
  - DEC-771baf (Tenant database topology; platform-tenant one-way dependency; qa-bench would be a separate tenant database)
  - DEC-ee6018 (bc-qa standalone repo; QA tooling enforces lint and code guards but does not run application tests)
  - DEC-bebaec (Chain Status SSOT; the substrate the TestBench preflight is queued to migrate to from the older IntegrityService path)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Synthetic Data and Testing

## Scope

This chapter records the platform's synthetic data and testing surface in its readiness-baseline state: the synthetic data generator (bc-sdg), the in-platform test bench (bc-core's TestBenchModule), the dedicated test tenant (qa-bench, aspirational in the readiness baseline), and the unit and integration test suites across the platform repositories. The chapter is rationale; per-test-case inventory and per-flavor synthetic-fixture inventory are deferred per pattern 74. The chapter records reality and the gaps; per pattern 81, the canonical-claim scope at the lead matches the chapter's own drift inventory: bc-sdg is functional, TestBenchModule is functional, qa-bench is aspirational, and the platform's testing surface as a whole is at an early phase.

This chapter sits between Audit and Activity Logging and the Implementation section's overview. Audit and Activity Logging records the operational governance trail (who did what when); this chapter records the substrate that lets the platform exercise its contract chain against generated data before real source observation. The relation between this chapter and Operating Model: Evidence and Lineage is the central scoping line and requires a careful clarification recorded in the next section: TestBenchModule does emit real Evidence and Lineage rows when it runs the chain, so the discipline that protects production tenants is tenant isolation, not invariant suppression.

This chapter does not redefine Foundation invariants, the Authority Model, or the Architecture chapter's commitments. It does not enumerate the runtime proof emission acts (deferred to Evidence and Lineage), the per-flavor synthetic field-by-field schema (deferred to bc-sdg's own profile files and the future Contract Schemas reference), the QA audit emissions and non-conformance records (covered in Audit and Activity Logging), the AI gate verdict trust model (deferred to AI Trust and Verification when drafted in the AI section), the per-environment deployment posture for bc-sdg (deferred to Infrastructure and Operations), or the security operations procedure for the test tenant lifecycle (deferred to Security Operations when drafted).

**Governing source.** Architecture; Backend Services; Audit and Activity Logging; outline.md §4.3.

## Test Bench Emits Real Runtime Proof

A clarification anchored at the front of this chapter to prevent a common misreading: TestBenchModule does emit real Evidence and Lineage when it runs the contract chain. There is no synthetic-mode flag in bc-core that suppresses Evidence under test execution. The full reader-to-admission-to-canonical-to-metric path that the test bench drives goes through the same `OrchestratorService` that production admission uses, and the same `EvidenceService.createEvidence()` call with `evidence_type='admission_run'` lands in the same `evidence` schema in whatever tenant database the request addresses.

The discipline that prevents test runs from contaminating a production tenant's runtime evidence is therefore not invariant suppression. It is tenant isolation: TestBenchModule writes to the addressed tenant database (resolved through the standard `TenantMiddleware` plus continuation-local storage chain), and the design intent is to address a dedicated test tenant (qa-bench) so that production tenants stay clean. The readiness baseline provisions `sandbox1`; the qa-bench tenant exists in a SQL comment as design intent but is not seeded. Pointing TestBenchModule at any provisioned tenant produces real runtime Evidence in that tenant's database, a readiness-baseline risk recorded in the drift inventory below.

The chapter therefore frames its work in two layers. The first layer is the substrates that produce or consume synthetic data (bc-sdg) or that exercise the contract chain against generated inputs (TestBenchModule). The second layer is the discipline that keeps these substrates from polluting production governance state. The two layers are separable and they are at different maturity levels.

**Governing source.** `bc-core/src/test-bench/`; `bc-core/src/boundary/orchestrator.service.ts`; Evidence and Lineage.

## bc-sdg: The Synthetic Data Generator

bc-sdg is a standalone TypeScript service running as a Fastify HTTP server plus a CLI. It generates synthetic data for SAP source systems against a fixed set of industry profiles, persists the rows to its own PostgreSQL database, and serves the data through OData endpoints that bc-core's reader-runtime can consume the same way it consumes a real SAP system.

| Surface | State | Detail |
|---|---|---|
| SAP S/4HANA Cloud landscape | Wired and live | OData V4 endpoint; profile shapes for `mfg-co` (manufacturing) and `fmcg` |
| SAP S/4HANA On-Premise landscape | Wired and live | OData V4 endpoint with same entity schema as Cloud; profile shape for `pharma-co` |
| SAP ECC EHP8 landscape | Wired and live | OData V2 endpoint with classic table names (T001, KNA1, LFA1, BKPF, BSEG, BSID, BSIK, ANLA, FAGL_POSE, RBKP, COSP); profile shapes for `real-estate-co` and `auto-parts` |
| SAP ECC standalone simulator | Code present, run separately | Optional standalone OData V2 server for isolated testing; in-memory event graph with sub-ledger derivation; not started by the main server |
| Salesforce Sales Cloud | Code present, profile-gated | Generators for Accounts, Contacts, Leads, Opportunities, OpptyLineItems, Tasks, Events, Campaigns, CampaignMembers; enabled in `fmcg` and `real-estate-co` profiles only |
| MES (Manufacturing Execution) | Code present, profile-gated | Discrete (Siemens Opcenter) or continuous-manufacturing (AVEVA) variants; enabled in `mfg-co` and `fmcg` profiles only |
| ECB SDMX, OER, FRED data sources | Absent | Reference-data sources are not yet generated by bc-sdg |
| Cloud deployment posture | Absent | No Dockerfile, no IaC, no CI/CD; local development machine only |
| Internal test suite | Functional | Custom integration runner (`sdg test`) walks all three SAP landscapes and asserts entity-set responses; no vitest or pytest harness |

The CLI exposes `init`, `generate`, `reset`, `serve`, `check`, `schedule start`, `schedule run`, `sfdc-generate`, and `mes-generate` commands. The HTTP server exposes a management API (`/api/profiles`, `/api/profiles/:slug/runs`, `/api/profiles/:slug/watermarks`, `/api/profiles/:slug/counts`) plus the three SAP landscape OData endpoints. Random generation is deterministic: a Mulberry32 pseudo-random generator is seeded by a CLI flag (default seed 42) so that the same profile and the same date range produce the same rows across runs.

Volume control is per-profile and per-month with fiscal-period multipliers for month-end, quarter-end, and year-end load shapes. Integrity checks run via `sdg check <profile>` and cover three categories: referential (foreign-key validation), temporal (date-range bounds), and financial (journal balance per the SAP ECC invariants in `src/simulators/sap-ecc/validate.ts`). The integrity surface is part of the as-built generator and is named here so a reader does not assume bc-sdg is a one-way producer with no self-validation.

bc-sdg runs against its own PostgreSQL instance (separate from bc-core's local Postgres) and does not call bc-core; bc-core's readers call bc-sdg, not the other way around. The integration is one-way pull. Master plan PLN-3ff708 (Full-Scale SAP Synthetic Data Generator) anticipated a broader synthetic generator surface; the readiness baseline realizes the SAP-side and the cross-system Salesforce/MES correlations but does not yet realize the reference-data sources or any cloud deployment posture. The chapter records this as drift, not as a gap in the as-built description.

**Grounding caveat.** Per pattern 75, the bc-sdg detail in this section rests on a behavior-search grounding agent's report at the time of drafting; `C:\MyProjects\bc-sdg` was not directly readable to subsequent reviewers in this drafting cycle. The CLI command names, the OData mount paths, the profile shapes, the seeded-RNG choice, the volume scheduler multipliers, and the integrity-check categories are subject to verification when the bc-sdg repository is fully readable to the chapter's reviewers. The general substrate description (TypeScript Fastify service plus CLI; SAP-side flavors realized; reference-data flavors and cloud posture absent) is the load-bearing claim and is unlikely to drift; the per-component detail carries residual risk until re-grounded.

**Governing source.** `bc-sdg/` (residual risk; see grounding caveat).

## Cross-Service Wiring

The platform's reader-runtime in bc-core consumes bc-sdg's OData endpoints the same way it would consume a real SAP system. Per pattern 82, both ends of this cross-service surface are recorded explicitly so that the chapter does not promise wiring that is not symmetric.

| Concern | Source side (bc-core reader-runtime) | Destination side (bc-sdg HTTP server) |
|---|---|---|
| Protocol | OData V4 for S/4HANA flavors; OData V2 for SAP ECC | Fastify routes mounted at `/s4cloud`, `/s4onprem`, `/ecc` per landscape |
| Authentication | Reader-side credential resolution per Connectors and Readers; no special test-mode auth | bc-sdg accepts the OData call without authentication at the time of writing |
| Selection | Reader query parameters per the executor (`$filter`, `$top`, `$skip`, `$orderby`, `$select`, `$count`) | OData handler translates the parameters to Drizzle queries against the local Postgres |
| Watermark | Reader's per-source watermark logic per Connectors and Readers | bc-sdg also tracks generation watermarks per profile, but the two watermark concepts are independent: bc-sdg's watermark advances when it generates new rows; the reader's watermark advances when it admits new rows |

The TestBenchModule does not invoke bc-sdg directly. Test bench requests pass a `tenantId` and a contract reference; the reader resolved against that contract is run by the standard `ReaderRuntimeService`, which calls whatever URL the contract's connector and reader instance specify. If that connector points at bc-sdg, the test bench observes synthetic data; if it points at a real SAP system, the test bench observes real source data. The chapter records this as a behavior-level finding, not as a wiring guarantee: the test bench's data source is whatever the bound contract says.

**Governing source.** `bc-core/src/registry/reader-runtime.service.ts`; `bc-sdg/src/server/odata/handler.ts`; Connectors and Readers.

## bc-core TestBenchModule

TestBenchModule is the in-platform test bench. It exposes two NestJS controllers and one service plus a report collector. The module imports `BoundaryModule` and `ContractModule` and uses the same orchestration path that production admission uses; the test-bench surface differs from production by entry-point only, not by execution semantics.

| Controller | Path | Scope | Endpoints |
|---|---|---|---|
| `TestBenchController` | `/test-bench` | `@PlatformOnly()` | Scenario CRUD; run lifecycle (`POST /runs`, `GET /runs`); per-MC preflight (`GET preflight/:metricContractId`, `POST preflight`) |
| `TestBenchExecutionController` | `/t/test-bench` | `@AnyScope()` (tenant-context path) | `POST execute-reader` (reader to observation to admission); `POST resolve-canonical`; `POST evaluate-metric`; `POST execute-chain` (full reader to admission to canonical to metric) |

The preflight surface consults `IntegrityService.getKpiIntegrity()` to verify chain-completeness verdicts before admitting a metric contract for test execution. A note recorded as drift below: `IntegrityService` is the older preflight authority; the platform also has `ChainStatusService` (per the SSOT recorded in DEC-bebaec), and a migration from the former to the latter is anticipated. The current TestBench preflight uses the older path; the migration is queued.

The execute-chain endpoint runs the reader, the orchestrator, the canonical resolution, and the metric evaluation in sequence. Each phase writes through the production code path: `OrchestratorService.processObservations()` invokes `EvidenceService.createEvidence()` with `evidence_type='admission_run'`; canonical resolution writes the bound CO; metric evaluation writes the metric snapshot to the per-tenant fact table per the activated contract. There is no synthetic-mode branch.

Test-bench scenarios are stored in the platform database under the `test_bench` schema (per `bc-core/docker/redesign/02-platform-tables/12-test-bench.sql`). A `test_bench.run` row is created when a scenario is explicitly run through the run-lifecycle endpoint (`POST /test-bench/runs`). Per-step records (`test_bench.run_step`) carry a `run_id` foreign-key that must point at an existing `test_bench.run`. The `execute-chain` endpoint does not auto-create a parent `test_bench.run`: it uses the admission run identifier returned by `ReaderRuntimeService` and then calls `benchRepo.createRunStep()` with that identifier. If the caller has not first created a parent test-bench run with the same identifier, the step persistence fails the foreign-key check and is logged as a warning rather than raised. The chain execution itself still emits real runtime proof to the addressed tenant database in either case; the platform-side scenario ledger is durable only when the lifecycle endpoint is used to create the parent run before `execute-chain` is invoked.

The fact rows produced by a test-bench chain execution live in whatever tenant database the request addresses; the platform-side scenario row references the run by tenant slug (`scenario.tenantSlug` text column) but does not constrain the slug to a specific test-only tenant.

**Governing source.** `bc-core/src/test-bench/test-bench.module.ts`; `bc-core/src/test-bench/test-bench.controller.ts`; `bc-core/src/test-bench/test-bench-execution.controller.ts`; `bc-core/src/boundary/orchestrator.service.ts`; `bc-core/docker/redesign/02-platform-tables/12-test-bench.sql`.

## qa-bench Tenant

qa-bench is a tenant identifier that appears in the test-bench DDL comment as the design-intent test tenant ("Tenant (qa-bench) runs the chain; report collector publishes here"), but the tenant is not provisioned in the readiness baseline. The active dev environment carries `sandbox1` as its provisioned tenant. No `tenant.tenants` row for `qa-bench` exists; no `tbc_qa_bench_dev` database is created; no seed script provisions it.

The implication for test-bench discipline is direct. If a test-bench scenario is created with `tenantSlug = 'sandbox1'` (the readiness-baseline provisioned slug) and execute-chain runs against it, the resulting Source Object, Canonical Object, Metric Snapshot, Evidence, and Lineage rows land in `tbc_sandbox1_dev`. Those rows are indistinguishable from production runtime rows in `sandbox1`'s scope. The chapter records this as an Open drift item: the qa-bench tenant must be provisioned before the test bench can be used safely against any tenant other than a deliberately-disposable one.

A future provisioning of qa-bench would follow the standard tenant onboarding path per `seed-tenant-dbs.ts` (tenant identity row in `tenant.tenants`; per-tenant `tbc_qa_bench_dev` database; tenant schemas applied from `docker/redesign/03-tenant-db.sql`; dynamic fact tables created per activated contract by `SchemaProvisionerModule`). The Tenant Onboarding chapter (queued in the Onboarding section) owns the operational procedure; this chapter records only the structural design intent and the readiness-baseline absence.

**Governing source.** `bc-core/docker/redesign/02-platform-tables/12-test-bench.sql`; `bc-core/src/registry/seed/seed-tenant-dbs.ts`; Infrastructure.

## Unit and Integration Tests

The platform's automated test surface is concentrated in bc-core; other repositories range from minimal coverage to none. The chapter records the substrates and the discipline; per-test inventory belongs to the future Test Inventory reference (queued; not yet built).

| Repository | Framework | Inventory posture | Shape |
|---|---|---|---|
| bc-core | Vitest | Unit and integration specs present | Unit specs use mocks for fast isolation; integration specs hit real PostgreSQL via `postgres-js`; gated by `BCCORE_INTEGRATION_DB=1` env so unit runs stay fast |
| bc-ai | pytest with pytest-asyncio | Small mock-oriented suite | Filesystem fixtures via `tmp_path`; `monkeypatch` for env; `unittest.mock.MagicMock` and `patch` decorators; no real DB hits |
| bc-portal | Vitest reportedly configured | No specs reported in prior grounding | Prior grounding reports test-scaffolding present and no specs authored; bc-portal repository not readable for independent verification in this drafting pass (see grounding caveat below) |
| bc-admin | None | No specs reported | No test framework in `package.json`; no testing-library dependencies |
| barecount-devhub | None for application code; Playwright in devDeps | No application specs reported; Playwright unused | Pre-commit hook validates MCP tool registry shape (`scripts/check-mcp-tools.mjs`) but is not a test runner |
| bc-qa | None (config and audit only) | n/a | Hosts `@barecount/eslint-config` plus the pre-commit hook installation script; runs lint and code guards, not tests |

bc-core's testing discipline keeps mocks restricted to unit specs and requires real PostgreSQL connections for integration specs. The integration suite is gated by an environment variable (`BCCORE_INTEGRATION_DB=1`) so that the default unit run stays fast and the integration suite only runs when explicitly requested. A representative integration spec (`typed-fact-writer.integration.spec.ts`) creates a real `postgres-js` pool, runs DDL generation against a real database, performs INSERT and DELETE, and cleans up; no mocked repository sits between the test and the database.

**Governing source.** `bc-core/vitest.config.ts`; `bc-core/vitest.config.e2e.ts`; `bc-core/src/**/*.integration.spec.ts`; `bc-ai/pyproject.toml`; `bc-ai/tests/`.

## CI Test Execution

The platform does not at the time of writing run automated tests in continuous integration. The repositories independently verified in this drafting pass (bc-core, bc-ai, bc-admin, DevHub, bc-qa) carry no `.github/workflows/` directory with a test-execution CI definition. bc-sdg and bc-portal were not directly readable in this pass; the no-CI claim for them is inherited from prior grounding and carries residual risk until re-verified. The pre-commit hook installed by `bc-qa/hooks/install-hooks.sh` runs ESLint, ruff, and code guards (no `@ts-ignore`, no `eval()`, no `console.log` in `src/`), but the hook does not run vitest or pytest. The DevHub repository's pre-commit hook validates the MCP tool registry but does not run tests.

The current model relies on local test execution before the developer commits or pushes. This is an Open drift item; an automated CI test execution surface is anticipated but not yet implemented.

**Grounding caveat.** Per pattern 75, the bc-portal row in the testing table above and the bc-portal-and-bc-sdg portion of the no-CI claim rest on prior grounding inherited from earlier drafting cycles; `C:\MyProjects\bc-portal` and `C:\MyProjects\bc-sdg` were not directly readable in this drafting pass. The other repositories' claims are independently verified.

**Governing source.** `bc-qa/hooks/install-hooks.sh`; `bc-qa/hooks/pre-commit`; `barecount-devhub/scripts/hooks/pre-commit`.

## End-to-End and Cross-Service Coverage

The platform has no end-to-end or cross-service integration tests at the time of writing. No Playwright or Cypress specs exist. No vitest spec in any repository starts multiple platform services and asserts an end-to-end execution. bc-core's integration specs are confined to the bc-core boundary; they do not call bc-ai, bc-portal, bc-admin, or DevHub. bc-ai's pytest suite is unit-only. bc-portal and bc-admin have no test files.

The implication is that the platform's full cross-service execution (a tenant-scoped request from bc-portal hitting bc-core, traversing the boundary acts, calling bc-ai for an AI gate decision, recording to DevHub, and producing a metric snapshot) is not exercised by automated tests. The sequence is exercised manually and through ad-hoc scripts; the durable verification substrate is the unit and integration suite within each individual service plus the test-bench's in-platform chain execution.

**Governing source.** Architecture; `bc-core/src/`; `bc-ai/tests/`.

## Failure Modes

| Cause | System response |
|---|---|
| TestBenchModule executes against the only provisioned tenant (`sandbox1`) | Real Evidence, Lineage, SO, CO, MS rows land in `tbc_sandbox1_dev`; indistinguishable from production runtime rows in that tenant's scope. The current discipline relies on the developer naming the right `tenantSlug`; no platform-side guard prevents the contamination |
| bc-sdg unreachable when a reader points at it | The reader returns the underlying connection error; admission run is recorded as failed; no Source Object emitted; the test-bench scenario records the failure in its run record |
| bc-sdg's Postgres becomes inconsistent (stale generation, FK violations) | `sdg check <profile>` surfaces violations; the developer reseeds via `sdg reset` plus `sdg init`; bc-core's reader does not detect synthetic-side inconsistency unless the response shape itself is malformed |
| TestBench preflight via `IntegrityService` reports a chain gap for the target metric contract | The execute-chain request returns early with the preflight verdict; no admission is attempted; the run record captures the gap |
| `execute-chain` invoked without a prior `POST /test-bench/runs` (no parent `test_bench.run`) | Per-step persistence fails the foreign-key check on `test_bench.run_step.run_id`; failure is logged as a warning, not raised; chain execution still emits real runtime proof to the addressed tenant database; the platform-side scenario ledger is missing the per-step trail |
| Pre-commit hook blocks a commit on a lint or guard violation | The commit exits non-zero; the developer fixes the violation and re-commits; no test execution occurs because no test execution is part of the hook |
| Unit test mocks drift away from the real interface they mock | A unit-only run still passes; an integration run (`BCCORE_INTEGRATION_DB=1`) catches the drift if the integration spec exercises the same interface; integration suite must be run explicitly to detect this class of drift |
| qa-bench tenant is referenced in a scenario but does not exist | The execute-chain request fails at `TenantMiddleware` resolution because no `tenant.tenants` row matches; the failure is loud, not silent |

**Governing source.** `bc-core/src/`; `bc-sdg/src/`; CLAUDE.md.

## Drift Inventory

Per pattern 69, gaps between the design intent recorded above and the current state are surfaced explicitly.

| Gap | Severity | Detail |
|---|---|---|
| qa-bench tenant is not provisioned | Open | Test-bench DDL comment documents qa-bench as the dedicated test tenant; no seed script creates it; pointing test-bench at sandbox1 contaminates sandbox1's runtime evidence |
| TestBench preflight uses `IntegrityService`, not the SSOT `ChainStatusService` | Open | The chain-status SSOT per DEC-bebaec is the authoritative chain-completeness substrate; TestBench's preflight predates the SSOT and has not been migrated. Migration is queued |
| bc-sdg does not implement reference-data flavors (ECB, OER, FRED) | Open | PLN-3ff708 anticipated all reference-data sources; the SAP-side flavors are realized; the reference-data flavors are queued |
| bc-sdg has no cloud deployment posture | Open | No Dockerfile, no IaC, no CI/CD; production AI surface depends on the local-only model not being the long-term posture |
| bc-sdg ports (4200 main, 6100 SAP ECC simulator) are not in DEC-e50b83 | Low | The master port reservation does not list 4200 or 6100; the bc-sdg ports are out-of-band against the platform's port discipline. Either DEC-e50b83 is amended to include them or bc-sdg's ports move into the reserved range |
| bc-sdg has no vitest or pytest suite | Low | The custom integration runner (`sdg test`) is the only test surface; standard test conventions are absent |
| No CI workflows run automated tests | Open | No `.github/workflows/` test-execution file in any repository; pre-commit hook is lint-only |
| bc-portal has no test specs reported | Open | The frontend testing scaffolding is present but no specs are authored |
| bc-admin has no test framework | Open | No vitest or testing-library dependency; no specs exist |
| DevHub has no application test suite | Open | Playwright is in devDeps but unused; no vitest or other test runner is configured |
| bc-ai pytest suite is mock-only | Low | No real-DB integration spec; the maker-checker-gate triplets are exercised via mocks; cross-family verification has no automated regression test |
| End-to-end and cross-service tests are absent | Open | The full bc-portal -> bc-core -> bc-ai -> DevHub -> tenant DB chain is not exercised by automated tests; manual exercise is the readiness-baseline substrate |
| TestBench scenarios accept any `tenantSlug` text | Low | The scenario's tenantSlug is a free text column; no platform-side allowlist constrains it to test-only tenant slugs. A future hardening would constrain it once qa-bench (and any other test-only tenants) are provisioned |
| Synthetic data and runtime data share the same fact tables in the addressed tenant | Open | A consequence of the no-synthetic-mode design. If the test bench writes to a tenant that also receives production runtime, the two streams cannot be distinguished without an external marker (tag column, scenario reference, or per-row provenance). No such marker exists in the readiness baseline |

**Governing source.** Architecture; Backend Services; Infrastructure; Audit and Activity Logging.

## Boundaries with Adjacent Chapters

Several adjacent chapters have surfaces that resemble synthetic data or testing but are not part of this chapter's scope.

| Adjacent surface | Where it lives | Why it is not this chapter |
|---|---|---|
| Evidence and Lineage | Operating Model | Owns the runtime proof chain at the four governed boundary acts. This chapter records that test-bench writes through the same proof-emission path; the proof commitment itself is the Operating Model chapter's authority |
| Connectors and Readers | Operating Model | Owns the contract grammar for source connectors and the reader execution semantics. This chapter records that a connector pointed at bc-sdg observes synthetic data; the connector contract is owned there |
| Quality Gates and Chain Integrity | Operating Model | Owns the chain-status SSOT (per DEC-bebaec) that the test-bench preflight is queued to migrate to. The current TestBench preflight uses `IntegrityService`; the SSOT migration is the gate chapter's authority |
| Audit and Activity Logging | Implementation section | Records the operational governance trail for sessions, plans, change records, and audit families. Test-bench runs that produce platform-side scenario and run records are operational governance state; the audit chapter is the substrate authority. This chapter records only the synthetic-data execution semantics |
| AI Gates, AI Trust and Verification | AI section, queued | bc-ai's maker-checker-gate triplets are tested with mocks in bc-ai's pytest suite; the AI trust model and the cross-family verification regression substrate are owned by the AI section |
| Tenant Onboarding | Onboarding section, queued | Owns the provisioning sequence for qa-bench and any other tenant. This chapter records only that qa-bench is design intent, not that it is provisioned |
| bc-qa | bc-qa repository per DEC-ee6018 | Hosts the lint and audit infrastructure (ESLint config, pre-commit hooks, audit drivers). bc-qa does not run application tests |

**Governing source.** Operating Model; Audit and Activity Logging; outline.md §4.

## Governing Decisions

| Decision | Title | Synthetic data and testing impact |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus home | The Synthetic Data and Testing chapter exists as a first-class platform-feature chapter in the reshaped Implementation section per DEC-c06f41 |
| DEC-e50b83 | Master port reservation | bc-sdg's main HTTP server (4200) and the standalone SAP ECC simulator (6100) are not in the reservation table; recorded as drift |
| DEC-1918d0 | Deployment and database architecture; ten normalization rules | Governs the schema shape of bc-sdg's local PostgreSQL store and bc-core's `test_bench` platform-side schema |
| DEC-771baf | Tenant database topology; platform-tenant one-way dependency | Governs that any provisioned tenant (including a future qa-bench) gets its own `tbc_{slug}_dev` database; cross-tenant writes go through governed runtime acts only |
| DEC-ee6018 | bc-qa standalone repo | Lint and audit infrastructure lives in bc-qa; bc-qa does not run application tests, so the testing surface per repo is independent of bc-qa |
| DEC-bebaec | Chain Status SSOT | The TestBench preflight consults `IntegrityService` in the readiness baseline; migration to the chain-status SSOT (`ChainStatusService`) is queued. The readiness-baseline path is recorded as drift, not as the canonical preflight authority |

**Governing source.** The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Authority Model
- Operating Model: Overview
- Evidence and Lineage
- Architecture
- Backend Services
- Internal Modules
- Infrastructure
- API Surface
- Audit and Activity Logging
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-e50b83: Master port reservation
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-ee6018: bc-qa standalone repo
- DEC-bebaec: Chain Status SSOT
- outline.md §4.3: Implementation
- Decisions: ADR Registry
