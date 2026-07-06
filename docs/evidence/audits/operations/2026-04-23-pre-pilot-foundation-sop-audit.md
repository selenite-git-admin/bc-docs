# Pre-Pilot Foundation/SOP Audit - bc-core

Date: 2026-04-23

Scope:
- Codebase: `C:\MyProjects\bc-core`
- Documentation source: `legacy-v2-docs-root`
- Focus: correctness and completeness against Foundation/SOP documents first; code standards and security second
- Pre-pilot context: last development phase before SDG-backed e2e/pressure test, then real-life pilot

## Executive Decision

The platform is not ready to treat SDG-backed pressure testing as a correctness proof yet.

That does not mean the architecture is weak. The opposite is true: the docs define a strong invariant model. The current risk is that several implementation paths and verification tools can let a run appear green while the platform has not independently proven tenant binding, chain integrity, semantic mapping, metric correctness, or simulator realism.

The immediate gate should be:

1. Fix P0/P1 runtime and auth issues before any shared tenant or pilot-like run.
2. Restore `npm run typecheck`, `npm run lint:columns`, and `npm test` to green.
3. Move preflight and pressure-test gates onto the persisted `ChainStatusService` and D335 integrity state, not the deprecated legacy `IntegrityService`.
4. Require SDG validation and drift reports as inputs to the pressure test, not optional supporting evidence.
5. Run one complete chain per SOP using D268 one-then-many discipline before expanding volume.

## Foundation/SOP Invariants Used

The audit used these doc-derived rules as the baseline:

- Runtime chain: Reader reads OC, validates against AC, emits SOs, Canonical Evaluator maps BF to CF through CC/CM, Metric Evaluator uses MC variables and `co_bindings`, and evidence/lineage exists at every boundary. See `legacy v2 archive\docs\architecture\contract-chain-assembly.md:357-365`.
- R1-R12 require field-code, mapping, grain, formula, and BF/CF continuity across MC, CC, OC, BO/BF, and source mappings. See `contract-chain-assembly.md:418-429`.
- R13 requires MC `co_bindings[].role` values to be unique when multiple bindings exist. See `contract-chain-mapping-requirements.md:399`.
- OC creation requires BF registry validation, BF-in-BO validation, source field existence, no duplicate BF mappings, identity/join validation, SO schema consistency, and meta-schema validation. See `legacy v2 archive\docs\sops\oc-creation-sop.md:84-103`.
- CC creation requires field selection validity, grain validity, resolution coverage, schema consistency, `cc_field_mapping` coverage, and semantic coherence. See `legacy v2 archive\docs\sops\cc-creation-sop.md:92-121`.
- Execution model requires fixed SO -> CO -> Metric Snapshot -> AO progression, immutable objects, and evidence/lineage as orthogonal proof. See `legacy v2 archive\docs\system\foundation\principles\execution-model.md`.
- Readers perform semantic admission but must not transform, aggregate, normalize, infer intent, compute metrics, or trigger downstream evaluation as reader behavior. See `execution-model.md:110-159`.
- SDG docs require generated data to satisfy referential integrity, temporal ordering, ID uniqueness, derived consistency, and amount consistency. See `legacy v2 archive\docs\system\platform\P09-platform-services\sdg\index.md:121-132`.
- SDG docs explicitly require drift detection from source catalog to simulator artifacts. See `sdg\index.md:260-311`.

## Go/No-Go Findings

### P0 - Tenant resolution is not bound to the authenticated user

Evidence:
- `src\tenancy\tenant.middleware.ts:48-58` resolves tenant context for `/api/t/*`.
- `src\tenancy\tenant.middleware.ts:73-78` allows `x-tenant-id`.
- `src\auth\strategies\cognito-jwt.strategy.ts:95` exposes `custom:tenant_id`, but middleware runs before guards and does not compare CLS tenant to the token tenant.

Impact:
- A tenant JWT can select another tenant by header/subdomain and receive that tenant DB context.
- This invalidates any multi-tenant pressure test because tenant isolation can be bypassed before data correctness is even considered.

Required gate:
- Tenant-scoped requests must bind resolved tenant to `request.user.tenantId` after authentication, or a guard must reject mismatches before tenant DB access.

### P0 - Repository does not typecheck

Command:

```text
npm run typecheck
```

Result:
- Failed on 2026-04-23.
- Active errors include boundary evaluation typing, metric evaluation input typing, `count_distinct` not assignable to the current aggregation union, DTO/schema drift in registry services, missing `playwright` for seed scripts included in compile, and `import.meta` incompatible with current TS module config.

Impact:
- Code contracts are not mechanically reliable.
- One error is directly foundation-relevant: docs and D335 workflows require `count_distinct`, but `metric-evaluation-engine.service.ts:427` is outside the typed aggregation union.
- Pressure-test output cannot be trusted as platform proof while compile-time contracts are broken.

Required gate:
- `npm run typecheck` green.
- Move scratch/test scripts out of `src` or exclude them cleanly.
- Align metric aggregation types with D335 and contract schemas.

### P0 - Existing D335 runway evidence says metric chain is mostly blocked upstream

Evidence:
- `scripts\d335-runway-findings-2026-04-15.md` reports 244 of 268 finance MCs blocked by upstream CF/BF semantic mismatches, 0 ready, and 0 walkable auto-fixable MCs.
- The same report says only 4 MCs could be walked to a fully verified fix in the current demo tenant.

Impact:
- The metric layer has already produced evidence that formula remediation is blocked by CC mapping hygiene.
- An SDG pressure test that selects a narrow passing route can accidentally avoid the real blocked surface.

Required gate:
- Pick one target pilot chain and prove it end-to-end with D335 diagnosis, AI/human semantic review where needed, chain-status completeness, tenant CO availability, and verified metric snapshots.
- Do not generalize from one green chain to the full finance catalog.

### P1 - Reader execution and test bench trust body `tenantId`

Evidence:
- `src\boundary\reader-runtime\reader-execution.controller.ts:34-45` forwards `dto.tenantId`.
- `src\boundary\reader-runtime\reader-runtime.service.ts:157` defaults run tenant to `demo-selenite`.
- `src\boundary\reader-runtime\reader-runtime.service.ts:255-256` writes readiness using body/default tenant.
- `src\test-bench\test-bench-execution.controller.ts:163-175` requires body `tenantId`; lines `236-243` forward it to reader runtime; lines `316-321` forward it to metric service.

Impact:
- CLS may select one tenant DB while rows, readiness, and reports are stamped with another tenant id.
- Test bench can pass for a synthetic tenant while hiding tenant mismatch defects.

Required gate:
- Remove body-level tenant authority from tenant-scoped endpoints.
- Use `@CurrentTenant()` for all tenant-scoped writes and readiness reporting.

### P1 - Boundary create DTOs broadly accept `tenantId` from body

Evidence:
- `src\boundary\dto\create-observation.dto.ts:60`
- `src\boundary\dto\create-admission.dto.ts:19`
- `src\boundary\dto\create-evaluation.dto.ts:21`
- `src\boundary\dto\create-metric-evaluation.dto.ts:23`
- `src\boundary\dto\create-action.dto.ts:40`
- Create controllers call services with the body DTO for POST paths, while list/read paths often use `@CurrentTenant()`.

Impact:
- Tenant DB routing and row tenant stamping can diverge across SO, CO, metric, and action layers.
- This is a systemic workflow risk, not just a reader-runtime bug.

Required gate:
- Treat tenant id in body as invalid for tenant-scoped routes.
- Derive tenant identity from CLS/current tenant for all boundary writes.

### P1 - Tenant id/slug confusion breaks typed fact dual writes

Evidence:
- `src\tenancy\tenant.service.ts:81-84` returns `tenantId` as registry row id and `tenantSlug` as slug.
- `src\schema-provisioner\typed-fact-writer.service.ts:60-62` expects a tenant slug.
- `src\boundary\admission.repository.ts:133-134` passes `data.tenantId` as `tenantSlug`.

Impact:
- Dual-write fact tables can target `tbc_${tenantId}` instead of `tbc_${tenantSlug}`.
- Runtime may appear to work through envelope tables while typed facts/read overlays are absent or written into a wrong/nonexistent DB.

Required gate:
- Use `tenantSlug` for DB naming and `tenantId` only for row identity.
- Add a typed fact dual-write test that asserts physical DB/schema target.

### P1 - JWT audience handling weakens auth boundary

Evidence:
- `src\auth\strategies\cognito-jwt.strategy.ts:70-82` derives client id from `aud ?? client_id`.
- It falls back to tenant scope when neither is present.
- `token_use` is typed but not enforced.

Impact:
- A valid token from the same issuer can be classified more permissively than intended in a multi-client pool.

Required gate:
- Enforce expected `token_use` and mandatory audience/client id.
- Reject tokens missing both `aud` and `client_id`.

### P1 - MC onboarding violates or risks R13 role uniqueness

Evidence:
- R13 requires unique `co_bindings[].role` values when an MC has multiple bindings: `contract-chain-mapping-requirements.md:399`.
- `src\registry\mc-onboarding.service.ts:204-210` emits `role: 'primary'` for every CC binding and `role: 'secondary'` for every MC binding.

Impact:
- Multi-CC metrics can produce duplicate roles, making `role` unusable as a stable semantic discriminator.
- This weakens metric binding explainability and can mask cross-CC binding mistakes.

Required gate:
- Generate deterministic unique roles for multi-binding MCs, or validate/reject duplicates.
- Add an R13 unit test and contract validation check.

### P1 - Test bench preflight uses deprecated legacy integrity service

Evidence:
- `src\registry\integrity.service.ts:1-8` is explicitly deprecated and lists known bugs.
- `src\test-bench\test-bench-execution.controller.ts:27` imports `IntegrityService`.
- `test-bench-execution.controller.ts:337-361` uses `getKpiIntegrity()` for pressure-test preflight.
- `src\test-bench\test-bench.controller.ts:30,158,177` also uses the legacy service.

Impact:
- The pressure-test preflight can approve/reject chains using a service that the code says has known correctness bugs.
- This is high risk because preflight is the gate that tells the team whether the run is meaningful.

Required gate:
- Replace test-bench preflight with persisted `ChainStatusService` plus D335 `mc_integrity_state`.
- Keep legacy `IntegrityService` out of pressure-test go/no-go decisions.

### P1 - Reader/test-bench single-trigger flow can mask boundary independence

Evidence:
- Foundation states readers do not trigger downstream evaluation as reader behavior.
- `src\boundary\reader-runtime\reader-runtime.service.ts:52` describes feeding into the orchestrator.
- `reader-runtime.service.ts:237` calls `orchestratorService.executeFullCycle`.
- `reader-runtime.service.ts:269` auto-resolves canonical after reader execution.
- `src\test-bench\test-bench-execution.controller.ts:157-162` exposes one trigger for reader -> admission -> canonical -> metric.

Impact:
- A single green run may prove orchestration success, but not independent boundary correctness.
- For pressure testing, the system needs per-boundary proof with independently inspectable inputs/outputs/evidence, not only an aggregate pass.

Required gate:
- Keep the full-chain convenience route, but require separate assertions for SO admission, CO resolution, metric snapshot generation, evidence, lineage, and chain-status state.

### P1 - CC creation still has warn-only gates for known production-affecting semantics

Evidence:
- `src\registry\cc-onboarding.service.ts:262-277` warns, but passes, when evaluation-period grain key is not literally `evaluation_period`.
- `cc-onboarding.service.ts:287-336` treats missing or weak `posting_date_field` semantics as warn-only in several cases.

Impact:
- These comments reference known D363/D365 bugs. For pilot readiness, warn-only lets known-bad semantics enter the contract chain.

Required gate:
- Finish migration of existing MC/CC data, then turn these warnings into blocking checks for pilot-target chains.

### P1 - SDG risk: docs require realism and drift proof, but bc-core only consumes the simulator

Evidence:
- SDG docs require deterministic generation, edge-case profiles, source-catalog-derived schema generation, and CI drift detection. See `sdg\index.md:156-180`, `sdg\index.md:251-257`, `sdg\index.md:260-311`.
- SAP simulator docs require SE-1 through SE-7 validation, including document balance, sub-ledger projection, clearing integrity, number range uniqueness, posting key consistency, temporal consistency, and amount consistency. See `sdg\simulators\sap-ecc.md:243-427`.
- Salesforce simulator docs require SF-1 through SF-7 validation. See `sdg\simulators\salesforce.md:256-440`.
- `scripts\smoke-e2e-pipeline.mjs` only checks health, preflight, nonzero counts, one sample metric shape, and re-resolve idempotency.

Impact:
- A synthetic run can pass in bc-core even if the SDG is biased, too clean, missing edge classes, or drifted from the source catalog.
- The existing smoke script proves a happy path, not adversarial correctness.

Required gate:
- Pressure-test input must include SDG validation artifacts: invariant report, drift report, profile used, seed, edge-case rates, and generated volume summary.
- Add negative and adversarial scenarios, not only clean data.

### P1 - Real-connector auth and protocol behavior is not production-grade enough to prove pilot readiness

Evidence:
- `src\registry\credential-resolver.service.ts:95-100` logs unsupported auth methods and returns empty credentials.
- `credential-resolver.service.ts:145-150` and `208-213` leave SSM resolution unimplemented.
- `src\boundary\reader-runtime\executors\sap-odata-v4.executor.ts:48` allows unauthenticated execution with only a warning.
- `src\boundary\reader-runtime\executors\sfdc-rest.executor.ts:64-77` builds SOQL from configured fields/object/conditions and logs it.

Impact:
- SDG connections can encourage permissive auth paths that should not exist in pilot-like environments.
- Protocol queries need allow-list validation for configured fields, objects, filters, and conditions.

Required gate:
- Reject `auth.method=none` outside SDG/dev allow-listed environments.
- Fail unsupported auth methods.
- Add config allow-list validation for SOQL/OData query pieces.

### P2 - Column naming linter is disabled by stale path

Command:

```text
npm run lint:columns
```

Result:
- Failed on 2026-04-23 with ENOENT for `C:\MyProjects\bc-core\apps\api\src\database\schema`.

Impact:
- A schema naming guardrail documented as active is currently not running.

Required gate:
- Point `scripts\lint-column-names.mjs` at `src\database\schema`.

### P2 - Test suite is not green

Command:

```text
npm test
```

Result:
- Normal sandbox run failed with `spawn EPERM`; escalated run completed.
- 1 failed test file, 11 failed tests, 61 passed files, 17 skipped files.
- Failing file: `src\boundary\reader-runtime\reader-runtime.service.spec.ts`.
- Failure root: `ReaderRuntimeService.executeReader` reads `this.executorRegistry.get(...)` at line 125, but the spec constructor no longer matches the service constructor order.

Impact:
- Runtime reader coverage is broken exactly in the area used by SDG and test bench.
- 62 skipped tests include multiple integration/progression tests that are directly relevant to pilot confidence.

Required gate:
- Fix reader runtime specs.
- Decide which skipped progression tests are required for pre-pilot signoff and make those run in a controlled test DB.

## SDG Pressure-Test Bias Risks

The biggest SDG risk is not random fake data. The bigger risk is friendly fake data that encodes the same assumptions as the platform code.

Concrete bias channels:

- Clean-state bias: simulator docs include valid invariants, but smoke tests do not require invalid/dirty observations that prove rejection evidence.
- Coverage bias: pressure tests may choose the few chains with CO data while hiding the 91 percent blocked D335 runway surface.
- Mapping bias: generated source fields may mirror the expected BF/CF mappings, failing to challenge ambiguous or wrong semantic mappings.
- Tenant bias: `demo-selenite` and body `tenantId` defaults can make data appear in the expected place without proving tenant isolation.
- Preflight bias: legacy integrity checks can declare readiness using a deprecated traversal with known bugs.
- Volume bias: nonzero snapshots do not prove correctness at high cardinality, duplicate grain, partial data, missing periods, multi-currency, or stale readiness.
- Auth bias: SDG no-auth/bearer-accepting behavior can normalize connector states that real systems will not allow.

Required SDG pack for each pressure run:

- SDG repo commit SHA.
- Seed and profile.
- Source catalog snapshot id or hash used by schema generator.
- Drift report: source catalog vs generated simulator schema.
- Invariant validation report: UI, SE, SF checks as applicable.
- Edge-case mix: expected vs actual counts for foreign currency, credit memo, dunning, dispute, partial payment, tax reversal, missing/null required fields, invalid references.
- Boundary report: SO accepted/rejected, CO accepted/rejected, metric snapshots, evidence count, lineage count.
- Chain-status and D335 integrity state before and after execution.

## Minimum Pre-Pilot Entry Criteria

Do not use SDG pressure testing as a go/no-go proof until all of these are true:

1. `npm run typecheck` passes.
2. `npm run lint:columns` passes.
3. `npm test` passes, or documented excluded integration tests have a separate controlled run.
4. Tenant context is bound to Cognito token tenant for every `/api/t/*` route.
5. Tenant-scoped write DTOs no longer accept authoritative `tenantId`.
6. Typed fact dual-write uses `tenantSlug` for DB selection and has a regression test.
7. JWT `token_use` and audience/client id are enforced.
8. Test bench preflight uses `ChainStatusService` and D335 integrity state.
9. R13 co-binding role uniqueness is validated.
10. Pilot-target CC warning gates are blocking or the target data is migrated.
11. SDG validation and drift artifacts are generated and attached to each run.
12. One target chain is walked by SOP from SC/AC -> OC -> CC/CM -> MC -> chain integrity -> runtime -> evidence/lineage -> metric snapshot before scaling volume.

## Recommended Execution Order

1. Security first: tenant binding, body tenant removal, JWT token/audience enforcement.
2. Mechanical correctness: typecheck, tests, column linter.
3. Contract-chain gates: R13, D363/D365 blockers, test bench preflight migration to `ChainStatusService`.
4. Target-chain proof: pick one pilot-relevant chain and walk it end-to-end with D268 one-then-many discipline.
5. SDG proof harness: require drift/invariant reports and adversarial cases.
6. Pressure test: run clean, dirty, high-volume, and cross-tenant-negative scenarios.
7. Real-life pilot readiness: only after synthetic proof includes independent failure cases, not just happy-path throughput.

## Commands Run

```text
npm run typecheck
```

Status: failed. Representative errors:
- `src/boundary/evaluation.service.ts(310,64): unknown not assignable to string`
- `src/boundary/metric-evaluation-engine.service.ts(427,12): "count_distinct" not comparable to current aggregation union`
- `src/boundary/metric.service.ts`: canonical object typing mismatch
- `src/registry/*`: DTO/schema naming drift around `sourceStandard`/`definitionStandard`
- `src/registry/seed/s4/*`: missing `playwright`

```text
npm run lint:columns
```

Status: failed. Stale path to `apps\api\src\database\schema`.

```text
npm test
```

Status: failed in sandbox due `spawn EPERM`; escalated run completed but suite failed:
- 1 failed file
- 11 failed tests
- 61 passed files
- 17 skipped files
- 859 passed tests
- 62 skipped tests

## Evidence Gaps

- I reviewed SDG requirements from `legacy v2 archive`, but I did not inspect the actual `bc-sdg` implementation in this pass because it is not present in the local `bc-core` workspace.
- I did not run live DB chain-status refreshes or smoke e2e because that requires the local Postgres, tenant DBs, Cognito token, and simulators to be running in a known state.
- The next audit pass should include actual `bc-sdg` code review and a controlled target-chain run with artifacts captured.

