---
id: platform-refactor-program-functions-lanes
order: 45.2
title: "Function Dossiers: The Authoring Lanes"
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

# Function Dossiers: The Authoring Lanes

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md).

This annex holds the dossiers of the ten authoring functions of the main document's functional map: L1, Source Catalog; L2, Source and Admission Contracts; L3, Vocabulary; L4, Observation Contracts; L5, Canonical Contracts; L6, Metric Contracts and certification; L7, Readers and connections; L8, Metric Directory; L9, Chain integrity; and L10, Tenant onboarding. Before the dossiers, the section "Findings that recur across lanes" lists nine findings that appear in more than one dossier. Every dossier has the same eleven headings, in this order: "What it is", "How bc-docs defines it", "What it owns", "The acts it performs", "What it receives and what it hands on", "State today", "Known defects and risks", "Governing ADRs", "Chapters to fold in, rewrite or retire", "Open questions for the operator" and "What "locked" will mean here". The commits and the date of what was read are given in the next paragraph, and every citation in this annex is to one of them. Three limits apply to the whole annex: repositories were read at origin/main only, the platform database was read with SELECT only and tenant databases were not read, and no step of any procedure chapter was run.

**Read on 2026-11-13, at origin/main only:** bc-core `ec72438b`, bc-db `c6de1c4`, bc-admin `d37b241`, bc-docs `f4f5edd`, barecount-devhub `93cc1ea5`. Live data: the platform database `bc_platform_dev`, SELECT only, 2026-11-13. Tenant databases were not read.

**What this annex holds.** The authoring lanes are the ten lanes in which the platform's governed definitions are written, from the catalog of a source system to the hand-off to a tenant. A lane is one family of authored records with one owner (ADR DEC-ce4314, amended by ADR DEC-a67bae: "STRICT ONE-LANE-PER-SURFACE", `bc-docs:docs/governance/adrs/ADR-a67bae.md:23 @ f4f5edd`). bc-docs lists the ten as functions L1 to L10 (`bc-docs:docs/implementation/platform-readiness-program.md:94-111 @ f4f5edd`). Each dossier below has the same eleven sections.

**How to read the citations.** A code or document citation is `repo:path:line @ short-sha`. Where a table says so, a bare path and line belongs to the file and sha cited just before it in the same dossier. Live data is given as the query and its result. A claim that was not checked at source carries the marker "not re-checked". Words inside double quotes are exact.

**Other function codes used.** S3, Tenant lifecycle and management; S4, Pricing and subscription; RT, Runtime; EV, Evidence and lineage; PV, Proof against the source; DL, Delivery to a tenant; TS, Tenant self-service; PR, Privacy and retention; OP, Operations; AI, AI services. They are the functions of the main document, under "The functional map".

## Findings that recur across lanes

Each is cited in the dossier named.

1. **A superseded version is never finished.** Bringing a new version of a source, admission, observation or canonical contract into force stamps the prior version with a 48-hour mark, and no code completes the supersession. Several versions of one contract are in force at once in three families (L2, L4, L5).
2. **One column holds the wrong identity.** `runtime.reader_binding.source_contract_id` holds admission contract ids. The forward request for a tenant's source-object tables joins it to source contracts and matches nothing (L2, L7, L10).
3. **A retired table is still read.** `contract.canonical_mapping` holds no rows, and connector onboarding still looks for canonical contracts through it (L5, L7, L10).
4. **Three surfaces serve several lanes at once,** against the one-owner rule: the `contracts` controller and `ContractService` (L2, L4, L5); the chain authoring call, which writes an observation contract, a reader and a canonical contract (L4, L5, L7); and `src/schema-provisioner` (L5, L6, L7, L10), which the lane taxonomy lists as not a lane.
5. **The chain verdict is a gate in code and "gates nothing" in the vocabulary page** (L6, L9).
6. **The environment is spelled three ways** in the records that pass between lanes: `dev`, `development`, `apex`, and `production` on some bindings (L2, L7, L10).
7. **The admin console calls routes that refuse or are retired:** reader creation (L7), tenant creation (L10), the legacy metric catalog (L8), chain detail (L9).
8. **Three ADRs cited by code have no file at origin/main:** DEC-1bb88e, DEC-d2583f, DEC-66ef36 (L5, L10).
9. **Procedure chapters, by the share of steps that can be followed** (judged by matching each step's route, table and body key to origin/main and the live database; no step was run):

| Lane | Procedure chapter | Share that can be followed |
|---|---|---|
| L1 | `onboarding/source-registration.md` | 0 of 3 steps |
| L2 | `onboarding/source-and-admission-contract-creation.md` | 1 section of 7 |
| L3 | `onboarding/business-field-and-business-object-onboarding.md` | 6 of 6 action families have routes; four acts are missing from it |
| L4 | `onboarding/observation-contract-creation.md` | 2 of 8 steps |
| L5 | `onboarding/canonical-contract-creation.md` | 0 of 9 steps |
| L6 | `onboarding/metric-workstream.md` | no authoring step in it |
| L7 | `onboarding/reader-creation.md` | 5 of 5 steps |
| L8 | none in force | none |
| L9 | none in force (archived) | none |
| L10 | `onboarding/tenant-onboarding.md`; `onboarding/tenant-metric-binding.md` | 2 of 11 steps; 6 of 6 sections |

## The dossiers

### L1, Source Catalog

**What it is.** The Source Catalog is the platform's record of the structure of the external systems it can read. It holds no business data. It has six levels, each pointing to the one above: source provider, source system, source version, source module, source table and source field. Every later lane starts from it: a contract can only be written over a source table that the catalog holds.

**How bc-docs defines it.**

- The defining chapter is `docs/operating-model/sources-and-the-catalog.md`: "This chapter defines the Source Catalog, the platform-scoped registry of observable external source structure." (`bc-docs:docs/operating-model/sources-and-the-catalog.md:31 @ f4f5edd`). It adds: "The catalog is platform-scoped. It records what source structure the platform knows about. It does not record which catalog entries a tenant has connected or activated." (same file, line 47).
- The approved words are in the vocabulary page, slice 3. A catalog entry for a table is a "source table"; the term "source object" is kept for an admitted observation (`bc-docs:docs/reference/vocabulary.md:397-400 @ f4f5edd`). The four catalog states are `registered`, `approved`, `deprecated`, `archived` (same file, lines 402-409).
- The procedure chapter is `docs/onboarding/source-registration.md`, with `docs/onboarding/seed-catalog-management.md` beside it.
- **The documents contradict the build in three places.**
  1. The operating-model chapter says verification "is AI-assisted review of catalog entities" (`sources-and-the-catalog.md:206`). The built act is mechanical: it compares rows with a hash-identified extract and writes the log (`bc-core:src/registry/source-extract/extract-admission.controller.ts:52-57 @ ec72438b`).
  2. The procedure chapter's steps 1 to 3 call `POST /api/ai/suggest/source-verify` and `table-verify` (`source-registration.md:72, 90`). Its own amendment note says these routes do "not exist in bc-core" and that the step matrix "describes the retired model and is retained as historical record pending the chapter's rewrite" (`source-registration.md:192-200`). No such route exists (command: `git grep -n -E "source-verify|table-verify" origin/main -- src` in bc-core -> no match).
  3. The seed chapter's banner says the store it describes "is retiring as *forage*, and nothing replaces it" (`bc-docs:docs/onboarding/seed-catalog-management.md:23 @ f4f5edd`).
- All three chapters carry `status: drafting` (line 5 of each file).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Module | `src/registry/source-catalog/` (catalog service, six CRUD controllers, discovery, retirement) | `bc-core:src/registry/source-catalog/source-catalog.controller.ts:37-427 @ ec72438b` |
| Module | `src/registry/source-extract/` (extract admission, the per-system adapter registry, the Odoo adapter) | `bc-core:src/registry/source-extract/extract-admission.module.ts:14-26 @ ec72438b` |
| Route prefix | `source-catalog/extract-admissions` (admit, `/verifications`, `/approvals`) | `bc-core:src/registry/source-extract/extract-admission.controller.ts:23-73 @ ec72438b` |
| Route prefix | `source-catalog`, `source-catalog/providers`, `/systems`, `/versions`, `/modules`, `/objects`, `/fields` | `source-catalog.controller.ts:37, 58, 127, 217, 281, 347, 427` |
| Route prefix | `source-catalog/retirement` (`GET plan`, `POST execute`) | `bc-core:src/registry/source-catalog/retirement/catalog-retirement.controller.ts:27-48 @ ec72438b` |
| Route prefix | `discovery` (scans, objects, fields, diffs) | `bc-core:src/registry/source-catalog/discovery.controller.ts:21-153 @ ec72438b` |
| Route prefix | `onboarding`, `sap-reference/tables`, `/cds`, `/field-mappings` (read-only; on the taxonomy's retirement list, still in code) | `bc-core:src/registry/source-catalog/source-reference.controller.ts:18, 36, 79, 120 @ ec72438b` |
| Route prefix | `seed-catalog/metrics` (lives in this folder; reads metric seeds) | `bc-core:src/registry/source-catalog/seed-metrics.controller.ts:18 @ ec72438b` — shared with L8, to be split |
| Route prefix | `source-catalog/stacks` (carries the catalog prefix but writes contracts) | `bc-core:src/registry/substrate/register-source-stack.controller.ts:17 @ ec72438b` — shared with L2, to be split |
| Schema | `source` (12 tables): the six levels, `source_catalog_artefact`, `source_field_derivation`, `source_field_typing`, `source_type_mapping`, `catalog_expunge_log`, `catalog_retirement_log` | query (bc_platform_dev, 2026-11-13): `SELECT table_name FROM information_schema.tables WHERE table_schema='source' AND table_type='BASE TABLE'` -> 12 rows |
| Tables | `operations.extract_manifest_log`, `operations.catalog_verification_log`, `operations.discovered_object`, `discovered_field`, `discovery_scan`, `discovery_diff` | same query on schema `operations` -> 6 rows. The lane taxonomy gives all of `operations.*` to PR, Privacy and retention (`barecount-devhub:artifacts/lanes/LOCKED-LANE-TAXONOMY-2026-08-24.md:52 @ 93cc1ea5`) — shared with PR, to be split |
| Screens (bc-admin) | `sources/catalog/systems`, `sources/catalog/objects/:objectId`, `sources/catalog/versions/:versionId`, `sources/discovery`, `sources/discovery/:scanId` | `bc-admin:src/components/AppRouter.tsx:148-157 @ d37b241` |
| Command | `npm run seed:registry` | `bc-core:package.json:41 @ ec72438b` |
| Scripts | `scripts/enrich-empty-modules.sql`, `enrich-module-functions.sql`, `enrich-objects-only.sql`, `scripts/archive/s4-catalog-import/` | command: `git ls-tree -r --name-only origin/main -- scripts` in bc-core |
| Documents | `operating-model/sources-and-the-catalog.md`; `onboarding/source-registration.md`; `onboarding/seed-catalog-management.md`; `reference/data-dictionary/source.md`; `reference/source-systems/` | command: `git ls-tree -r --name-only origin/main -- docs` in bc-docs |

Two corrections to the lane kit. The kit lists `business-catalog` and `connectors` under L1 (`barecount-devhub:artifacts/lanes/L1-source-catalog/README.md:10 @ 93cc1ea5`). `business-catalog` is a "domain-organized view of canonical objects" (`bc-core:src/registry/business-catalog.controller.ts:6 @ ec72438b`) and belongs with L5, Canonical Contracts. Connectors belong to L7, Readers and connections, in the taxonomy (`LOCKED-LANE-TAXONOMY-2026-08-24.md:36`). The kit also names `contract.source_contract` as L1's record (README line 14); that table is L2's.

**The acts it performs.**

| Act | Who | Entry point as built | States and writes |
|---|---|---|---|
| Admit an extract | `platform_admin` | `POST /api/source-catalog/extract-admissions`; "dryRun (default true)" (`extract-admission.controller.ts:27-46`) | Creates the identity chain, tables and fields "born registered/unverified" (controller line 34; service `extract-admission.service.ts:247-259, 390`); writes `operations.extract_manifest_log` and `source.source_catalog_artefact` |
| Verify | `platform_admin` | `POST …/extract-admissions/verifications` (controller 49-60) | `verification_status` `unverified` to `verified` on tables and fields (`extract-admission.service.ts:169-170`); writes `operations.catalog_verification_log` (service line 570) |
| Approve | `platform_admin` | `POST …/extract-admissions/approvals` (controller 62-73) | `catalog_status` `registered` to `approved`; refused while any row is unverified (`extract-admission.service.ts:183-189`) |
| Retire | `platform_admin` or `operator` | `GET /source-catalog/retirement/plan`, `POST …/execute` with the echoed manifest hash (`catalog-retirement.controller.ts:31-60`) | Emits evidence, then deletes; log in `source.catalog_retirement_log` |
| Create, edit, delete one entry by hand | per route | The six CRUD controllers (`source-catalog.controller.ts:58-484`) | See the defects below |
| Discovery scan | per route | `POST /discovery/scans`, `/objects`, `/fields`, `/diffs` (`discovery.controller.ts:28-146`) | Writes `operations.discovered_*`; not registration |

Approval of a system, version or module is never an act. ADR DEC-3b2ff9 makes it a read-time derivation: "identity-tier approval is DERIVED, never asserted" (`bc-docs:docs/governance/adrs/ADR-3b2ff9.md:25 @ f4f5edd`).

**What it receives and what it hands on.**

| Direction | With | What passes, in which record | Defined in bc-docs | Built |
|---|---|---|---|---|
| In | Outside the platform | A manifest and extract files (`manifestText`, `files`: controller lines 42-43). The producer of the extract is not in bc-core and was not found in this reading | Named only (`source-registration.md:61`) | Receiver built; producer not found |
| Out | L2, Source and Admission Contracts | `source_object_id` and `source_version_id` on the contract parent, with foreign keys to `source.source_object` and `source.source_version`; the field list read from the catalog (`register-source-stack.service.ts:101-145, 269`) | Yes (`sources-and-the-catalog.md:239-247`) | Yes |
| Out | L4, Observation Contracts | Source field names used in field mappings | Yes (`source-registration.md:135`) | Not re-checked here |
| Out | L7, Readers and connections | The source system identity, through the connector | Yes (`source-registration.md:136`) | Not re-checked here |

The chapter states a rule for the hand-off to L2: "Contracts may only reference approved structure" (`sources-and-the-catalog.md:242`). The code does not enforce it (defect 2).

**State today.**

- **What works.** The three-call route was used for the whole live catalog. Live counts: query (bc_platform_dev, 2026-11-13): `SELECT catalog_status, count(*) FROM source.<level> GROUP BY 1` for each level -> provider 1 `registered`; system 1 `registered`; version 1 `registered`; module 37 `registered`; table 305 `approved`; field 9,850 `approved`. All 305 tables are `verified`, veracity `authoritative`, type `table`. The one system is `odoo`. The log holds 39 `verified` and 5 `failed` manifest rows, 4 artefacts and 1,116 verification rows.
- **The identity levels read `registered` by design** (DEC-3b2ff9, above). A reader of the raw table will see an unapproved system over approved tables.
- **Duplicated.** There are four ways to create a catalog row: the extract admission route; the six CRUD `POST` routes; `npm run seed:registry`; raw SQL scripts (three `enrich-*.sql` files). bc-admin uses only the CRUD routes (`bc-admin:src/api/sources.ts:517-572 @ d37b241`) and has no screen for the governed three-call route (command: `git grep -n -E "extract-admissions" origin/main -- src` in bc-admin -> no match).
- **Hard-coded.** One adapter is registered, for Odoo (`extract-admission.module.ts:24-25`). An extract for any other system is refused: "no source-catalog adapter registered for source system" (`bc-core:src/registry/source-extract/source-catalog-adapter.ts:52 @ ec72438b`). A second source system needs code.
- **Not used.** Discovery: query: `SELECT count(*) FROM operations.discovery_scan` -> 0.

**Known defects and risks.**

1. **A row can be born approved through the CRUD routes.** The create DTOs accept `catalogStatus` with `approved` in the allowed list (`bc-core:src/registry/dto/create-source-object.dto.ts:65-66 @ ec72438b`), and the service passes it through (`source-catalog.service.ts:272, 357`). The database guard is an UPDATE trigger only (query: `information_schema.triggers` for schema `source` -> `trg_source_object_status_guard` on UPDATE, `trg_source_field_status_guard` on UPDATE), so an INSERT is not checked. This contradicts ADR DEC-3078ce, whose title ends "no born-approved rows".
2. **Nothing checks that a table is approved before a contract is written over it.** The stack service checks only that the object exists and is of type `table` (`register-source-stack.service.ts:101-124`); `createContract` checks only veracity (`bc-core:src/registry/contracts/contract.service.ts:303-320 @ ec72438b`). Neither file mentions `catalog_status` (command: `git grep -n -E "catalog_status|catalogStatus" origin/main -- src/registry/contracts/contract.service.ts src/registry/substrate/register-source-stack.service.ts` -> no match).
3. **Seeds create approved rows.** `seed-tally-prime.ts:220, 246, 264, 282` and `seed-roadmap-sources.ts:68` pass `catalogStatus: 'approved'`; `seed-cli.ts` shows no environment guard (command: `git grep -n -E "NODE_ENV|refus" origin/main -- src/registry/seed/seed-cli.ts` -> no match).
4. **A caller who omits `dryRun: false` on admission writes nothing** and still gets a plausible result (controller line 45).
5. **The retired SAP reference controllers are still served** (`source-reference.controller.ts:18-124`), against the retirement list of ADR DEC-a67bae.
6. **The table of source tables is named `source.source_object`**, a mismatch the vocabulary records as a defect (`vocabulary.md:465`).
7. **The source system row reads `unverified`** while its tables are verified (query: `SELECT system_name, verification_status FROM source.source_system` -> `odoo`, `unverified`).

**Governing ADRs.**

| ADR | Plain summary | Status at origin/main |
|---|---|---|
| DEC-3078ce | Rows are born registered and unverified; verification and approval are explicit acts | implemented |
| DEC-3b2ff9 | A system is approved only as a derivation from its approved tables | implemented (system level only) |
| DEC-05140c | One unified catalog; status-driven approval | implemented |
| DEC-0b5a4c | Extract admission replaces the seed store | decided |
| DEC-e1241a | Catalog artefacts carry identity by hash | implemented |
| DEC-3d4304 | Governed field data types and field kinds | decided |
| DEC-12558e | Odoo is a JSON-RPC connector (belongs with L7) | implemented |
| DEC-908a69 | The stack call writes over the admitted catalog (belongs with L2) | implemented |

Status read from line 5 of each `bc-docs:docs/governance/adrs/ADR-<uid>.md @ f4f5edd`. No two of these conflict. The code conflicts with DEC-3078ce (defect 1).

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/operating-model/sources-and-the-catalog.md` | keep nearly as is | Hierarchy, states and the catalog-versus-contract split match the build; rewrite the verification and discovery sections |
| `docs/onboarding/source-registration.md` | rewrite | None of its three numbered steps can be followed: each depends on a route that does not exist. The working route is one paragraph in an amendment note. Share of steps that work: 0 of 3, judged by checking each step's route in code |
| `docs/onboarding/seed-catalog-management.md` | history | Its own banner says the store is retiring and nothing replaces it |
| `docs/reference/data-dictionary/source.md` | rewrite | Not re-checked line by line; the live schema has 12 tables |

**Open questions for the operator.**

1. Should the six CRUD create routes stay as a second way in (forced to `registered` and `unverified`), or be removed so that extract admission is the only way to create a catalog row?
2. Should bc-admin get a screen for the admit, verify and approve acts, or do these stay command-only?
3. Do the discovery routes and tables stay (unused today), or go to the retirement list?
4. Do the extract and verification logs move out of the `operations` schema's owner (PR, Privacy and retention) into L1's ownership on the map?
5. Who owns producing the extract and its manifest for a new source system: L1, or the demo-world tooling?

**What "locked" will mean here.**

1. One route creates catalog rows; a CI guard fails if another writer to `source.*` appears.
2. No catalog row can be created `approved`: the DTOs refuse it and an INSERT trigger enforces it.
3. A contract cannot be written over a table that is not `approved` and `verified`; a test proves the refusal.
4. A second adapter can be added by declaration, or the chapter states plainly that a new source system needs code.
5. The chapter's steps are the three built calls, and a fresh session admits, verifies and approves one table from the chapter alone.
6. The retired SAP reference routes, the seed chapter and the raw SQL scripts are deleted or marked as history.

### L2, Source and Admission Contracts

**What it is.** A Source Contract declares the structure of one source table: its fields, types and key. An Admission Contract declares the rules under which rows observed from that table are admitted or rejected. They are written as a pair over one catalog table. Without them the platform has no governed statement of what it reads and what it accepts.

**How bc-docs defines it.**

- Foundation: "A Source Contract declares the structural shape of one source table or API endpoint: field inventory, field types, primary key, and whether a field is a standard field or a tenant-scoped extension." (`bc-docs:docs/foundation/the-contract-grammar.md:131 @ f4f5edd`). "An Admission Contract declares the rules under which observed source state is admitted at the admission boundary: identity semantics, required fields, structural validation, temporal rules, and rejection policy." (same file, line 148).
- The lifecycle is Foundation's frozen five states: `draft`, `review`, `approved`, `active`, `superseded` (`the-contract-grammar.md:345-351`). The vocabulary says the value `active` is spoken as "in force" (`bc-docs:docs/reference/vocabulary.md:347-350 @ f4f5edd`).
- Application at run time is in `docs/operating-model/admission-and-observation.md` (lines 42-58).
- The procedure chapter is `docs/onboarding/source-and-admission-contract-creation.md`. **It contradicts itself and the build.** Its steps 1 to 6 teach named contracts (`"name": "sc__ecc__bkpf"`, line 85) while its own banner says those names "are **RETIRED**" (line 54). It names stores that do not exist: `contract.contract_version` and `contract.contract_version_governance` (lines 43-46; query: `SELECT to_regclass('contract.contract_version'), to_regclass('contract.contract_version_governance')` -> both null). It claims the service checks `catalogStatus: approved` (line 94) and that "an active SC exists" before an Admission Contract is created (line 160); the code has neither check (defects 1 and 2). It cites DEC-242d60 as Source Contract body purity (line 16); that ADR's title is "AC Body Purity", and Source Contract purity is DEC-8a6acb.
- Its last section, on `POST /api/source-catalog/stacks`, matches the build (lines 224-240).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Module | `src/registry/substrate/register-source-stack.*` (the one-call writer for the pair) | `bc-core:src/registry/substrate/register-source-stack.service.ts:75-221 @ ec72438b` |
| Module | `src/registry/contracts/contract.service.ts` and `contract.controller.ts` (create, version, lifecycle for every contract family) | `bc-core:src/registry/contracts/contract.controller.ts:28-360 @ ec72438b` — shared with L4 and L5, to be split |
| Route | `POST /api/source-catalog/stacks` | `bc-core:src/registry/substrate/register-source-stack.controller.ts:17-32 @ ec72438b` |
| Route prefix | `contracts` (24 handlers: create, list, versions, `submit`, `approve`, `activate`, `supersede`, `revert`, `bulk-transition`, `archive`, `expunge`, approvals) | `contract.controller.ts:36-360` — shared with L4 and L5, to be split |
| Route | `POST /api/harness/apply` (writes Admission Contract drafts from a plan) | `bc-core:src/registry/harness-apply/harness-apply.controller.ts:25-29 @ ec72438b` — shared with L4, to be split |
| Tables | `contract.source_contract`, `source_contract_version`, `source_contract_approval`; `contract.admission_contract`, `admission_contract_version`, `admission_contract_approval` | query (bc_platform_dev, 2026-11-13): `information_schema.tables` for schema `contract` |
| Table | `contract.contract_meta_schema` (the grammar for every family; 1 row each for source and admission) | query: `SELECT category_code, count(*) FROM contract.contract_meta_schema GROUP BY 1` -> admission 1, canonical 2, metric 1, observation 2, source 1, intervention 1 — shared with L4 and L5, to be split |
| Files | `src/registry/meta-schemas/admission-v1.schema.json` and the source schema | `bc-core:src/registry/meta-schemas/admission-v1.schema.json:15-20 @ ec72438b` |
| Screens (bc-admin) | `registry/contracts/source`, `/source/new`, `registry/contracts/admission`, `/admission/new`, `registry/contracts/:contractId` | `bc-admin:src/components/AppRouter.tsx:162-176 @ d37b241` |
| DevHub tool | `devhub_register_source_stack` (calls `/api/source-catalog/stacks`) | `barecount-devhub:src/mcp-server.js:3770-3781 @ 93cc1ea5` |
| Scripts | `scripts/seed-source-contracts-v2.mjs`, `seed-source-admission-contracts.mjs`, `seed-source-admission-contracts.sql`, `seed-ac-dqc-enrichment.mjs` | command: `git ls-tree -r --name-only origin/main -- scripts` in bc-core |
| Migration | bc-db `0037_contract_version_freeze_approved_onward.sql` | command: `git grep -l "source_contract" origin/main -- migrations` in bc-db |
| Documents | `foundation/the-contract-grammar.md` (Source Contract, Admission Contract); `operating-model/admission-and-observation.md` (application only); `onboarding/source-and-admission-contract-creation.md` | bc-docs paths above |

The taxonomy row gives L2 "`contract.source_contract*`, `contract.admission_contract*`; `contracts` ctrl" (`barecount-devhub:artifacts/lanes/LOCKED-LANE-TAXONOMY-2026-08-24.md:31 @ 93cc1ea5`). The `contracts` controller serves every family, so that part of the row breaks the one-owner rule.

**The acts it performs.**

| Act | Who | Entry point as built | States and writes |
|---|---|---|---|
| Write and bring into force the pair, in one call | `platform_admin` | `POST /api/source-catalog/stacks` with `{dryRun, spec}`; `dryRun` defaults to false here (`register-source-stack.controller.ts:31`) | Finds an existing contract by `(source_object_id, source_version_id)`, else creates the parent with no name, creates version `1.0.0`, then activates unless `activate` is false (`register-source-stack.service.ts:175-221, 230`). A failure halts the stack (line 199) |
| Create a parent | per route | `POST /api/contracts` (`contract.controller.ts:36`) | One row in the family's parent table |
| Create a version | per route | `POST /api/contracts/:contractId/versions` (line 213) | A `draft` version, checked against the meta-schema |
| Submit, approve | per route | `…/versions/:version/submit` (272), `/approve` (287) | `draft` to `review` to `approved` |
| Activate | per route | `…/versions/:version/activate` (302) | To `active`. For source and admission, `draft` to `active` directly is allowed (state machine: `contract.service.ts:55`; the refusal of that skip applies only to canonical and metric, lines 889-900) |
| Supersede | per route | `…/versions/:version/supersede` (317) | `active` to `superseded` |
| Revert | `platform_admin` or `operator` | `…/versions/:version/revert` (332) | `review` to `draft` |
| Bulk transition | per route | `POST /api/contracts/bulk-transition` (128) | Many versions in one call |
| Archive, unarchive, delete, expunge | `platform_admin` or `operator` | `contract.controller.ts:170-202` | Parent `archived_at`; delete; evidence on expunge |

A version's body is frozen by a database trigger once it is `approved` or later (query: `pg_get_functiondef` of `contract.fn_cv_immutable_gov_check` -> raises on a changed `contract_json` when the old state is `approved`, `pending_provisioning`, `active` or `superseded`).

**What it receives and what it hands on.**

| Direction | With | What passes, in which record | Defined in bc-docs | Built |
|---|---|---|---|---|
| In | L1, Source Catalog | The table and its fields: `source_object_id`, `source_version_id` on the parent (foreign keys; query: `pg_constraint` on `contract.source_contract`) | Yes (`sources-and-the-catalog.md:247`) | Yes |
| Out | L4, Observation Contracts | The pair pin in `source_references[]`: `sc_contract_id`, `sc_version_code`, `ac_contract_id`, `ac_version_code` | Not in the chapter read; named in the lane kit | Yes (`bc-core:src/registry/meta-schemas/observation-v2.schema.json:34-41 @ ec72438b`) |
| Out | L7, Readers and connections | `runtime.reader_binding.source_contract_id`, which in fact holds Admission Contract ids | Chapter says "Active SC (for `runtime.reader_binding.source_contract_id`)" (`source-and-admission-contract-creation.md:266`) — wrong | Built, mis-named: query: reader bindings matching an admission contract -> 19 of 19; matching a source contract -> 0 of 19 |
| Out | RT, Runtime (admission) | The Admission Contract version's body; the parent Source Contract found from the pair `source_contract_id`, `source_version_code` in that body (`admission-v1.schema.json:15-20`; `bc-core:src/boundary/admission.service.ts:82-86 @ ec72438b`) | Yes (`admission-and-observation.md:42-58`) | Yes |
| Out | L10, Tenant onboarding | A tenant's adoption of a Source Contract version: `tenant.tenant_binding`, open while effective-to is empty | Yes (`vocabulary.md:549`) | Record exists: query: `SELECT count(*), count(*) FILTER (WHERE effective_to IS NULL) FROM tenant.tenant_binding` -> 28, 27 |

**State today.**

- **What works.** The one-call route was used for the whole estate. Live counts: query (bc_platform_dev, 2026-11-13): `SELECT governance_state_code, count(*) FROM contract.source_contract_version GROUP BY 1` -> `active` 305. The same on `admission_contract_version` -> `active` 306, `approved` 1, `superseded` 2. Parents: 305 source, 306 admission, none archived. Every name has the opaque form (`^sc-…`: 305 of 305; `^ac-…`: 306 of 306). The 305 Source Contracts cover 305 distinct tables.
- **Duplicated.** There are five ways to write a pair: the stacks route; the manual `POST /api/contracts` sequence (which bc-admin calls: `bc-admin:src/api/contracts.ts:472-493 @ d37b241`); `POST /api/harness/apply`; the registry seed; and four scripts. One script, `scripts/seed-source-contracts-v2.mjs`, is committed with unresolved merge markers (command: `git grep -n -E "^(<<<<<<<|=======|>>>>>>>)" origin/main -- scripts/seed-source-contracts-v2.mjs` -> lines 89, 116, 126, 135, 142, 156, 174, 188, 221, 232). bc-admin has no screen for the stacks route.
- **Broken: supersession is never finished.** Activating a new version marks the prior one with `supersede_after = now() + interval '48 hours'` (`bc-core:src/registry/contracts/contract-version.repository.ts:214-221 @ ec72438b`). No code moves a marked version to `superseded` (command: `git grep -n -i -E "supersede_after\s*(<|<=)" origin/main -- src scripts` -> no match). Live result: `ac-vtg83` has versions `1.0.0` and `1.1.0` both `active`; `1.0.0` was due on 2026-11-04 (query on `contract.admission_contract_version` joined to its parent).
- **Not built: a record of each transition.** Canonical and observation versions have a transition table; source and admission do not (query: `SELECT to_regclass('contract.source_contract_version_transition'), to_regclass('contract.admission_contract_version_transition')` -> both null). Approval rows: source 0, admission 1.
- **Environment words differ between the records this lane hands to:** `tenant.tenant_binding.environment_code` holds `apex`, `dev`, `development`; `runtime.reader_binding.environment_code` holds `dev`, `production` (query: `string_agg(DISTINCT environment_code)` on each).

**Known defects and risks.**

1. **No check that the catalog table is approved.** `createContract` checks veracity only (`contract.service.ts:303-320`); the stacks service checks existence and type only (`register-source-stack.service.ts:101-124`). The chapter claims the check exists (line 94).
2. **No check that an Admission Contract has a Source Contract in force.** `createContract` has no admission-specific check (command: `git grep -n "'admission'" origin/main -- src/registry/contracts/contract.service.ts` -> no match). The chapter claims it (line 160). Live: `ac-6bm7v` has no source table at all (`source_object_id` null) and one `approved` version.
3. **Two versions of one Admission Contract are in force at once** (`ac-vtg83`, above). No unique index limits a contract to one `active` version (query: `pg_indexes` for the four tables -> primary keys and name indexes only). Which of the two an admission run uses was not re-checked.
4. **Source and admission versions can go from `draft` straight to `active`** (`contract.service.ts:55`). Foundation records this as historical looseness (`the-contract-grammar.md:341-343`); the chapter's gate table says the transitions are `draft` to `review` to `approved` to `active` (line 253).
5. **A semantic name can still be given** on `POST /api/contracts` (`contract.service.ts:296-301`), against DEC-3fe389.
6. **`runtime.reader_binding.source_contract_id` holds Admission Contract ids** and has no foreign key; a walk that joins it to `contract.source_contract` returns nothing (`bc-core:src/schema-provisioner/schema-provisioner.repository.ts:458-472 @ ec72438b`; live 0 of 19 match). The fix is in L7 and the schema provisioner; the hand-off is L2's.
7. **A script that rewrites Admission Contract bodies in place is still in the repository,** behind a refusal that an environment variable lifts (`bc-core:scripts/seed-ac-dqc-enrichment.mjs:26-30 @ ec72438b`).
8. **A sixth state value, `pending_provisioning`, is allowed on both version tables** (query: the `governance_state_code` CHECK on each) and is not named by Foundation for these families (`vocabulary.md:364`).

**Governing ADRs.**

| ADR | Plain summary | Status at origin/main |
|---|---|---|
| DEC-426b24 | The pair is the entry-boundary pattern | implemented |
| DEC-8a6acb | A Source Contract body declares structure only | implemented |
| DEC-242d60 | An Admission Contract body carries no readiness predicate | implemented |
| DEC-ca4c1e | The Admission Contract body shape is fixed, with quality rules | implemented |
| DEC-baaa09 | Source Contracts carry no business function | implemented |
| DEC-3fe389 | Identity is the UUID plus an opaque short name; no semantic names | decided |
| DEC-f4084d | Governed writing calls, including the stacks call | implemented |
| DEC-908a69 | The stacks call writes only over an admitted table of type `table` | implemented |
| DEC-7b15c7 | A version's body is frozen once published (cited by the trigger) | decided |
| DEC-f7d4fc | A tenant's adoption of a Source Contract is in `tenant.tenant_binding` | decided |
| DEC-e27625 | Every tenant gets its own Admission Contracts | implemented (by its file) |

Status from line 5 of each `bc-docs:docs/governance/adrs/ADR-<uid>.md @ f4f5edd` (DEC-f4084d: line 23). **DEC-e27625 conflicts with the build and with DEC-f7d4fc.** It says "Admission contracts are always tenant-specific" (`ADR-e27625.md:27`). The live Admission Contract table has no tenant column (query: `information_schema.columns` for `contract.admission_contract` with a name like `%tenant%` -> 0), and all 306 are platform records adopted through bindings. The readiness chapter still lists it for L2 (`bc-docs:docs/implementation/platform-readiness-program.md:103 @ f4f5edd`).

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/foundation/the-contract-grammar.md` (Source Contract, Admission Contract, legacy lifecycle) | keep nearly as is | Matches the records; the lifecycle text already notes the looseness |
| `docs/operating-model/admission-and-observation.md` | keep nearly as is | Belongs to Runtime; L2 only cites it |
| `docs/onboarding/source-and-admission-contract-creation.md` | rewrite | Steps 1 to 6 teach retired names and name two stores that do not exist; two of its six gates are not in code. The calls in steps 1 to 6 still run, but produce what DEC-3fe389 retired. Share of the procedure that is right: 1 section of 7 (the stacks section), judged by checking each step's call, store and gate in code and in the live database |

**Open questions for the operator.**

1. Is the stacks call the only way to write a pair (the manual create pages in bc-admin and the name field are removed), or does the manual sequence stay for corrections?
2. When a new Admission Contract version comes into force, is the prior version superseded at once, or after a stated window with a finisher that is built?
3. Is DEC-e27625 (an Admission Contract per tenant) marked superseded by the binding model, or is it still intended?
4. Must source and admission versions pass review and approval like canonical versions, or is `draft` to in force accepted for these two families and written into Foundation?
5. Should every transition of a source or admission version write an append-only record, as canonical and observation versions do?

**What "locked" will mean here.**

1. One command writes a pair; a CI guard fails on any other writer to the four contract tables.
2. A pair cannot be written over a table that is not approved and verified, and an Admission Contract cannot exist without its Source Contract in force; tests prove both refusals.
3. At most one version of a contract is in force, enforced in the database, and the live count of contracts with two `active` versions is zero.
4. Every transition writes a record, and the chapter names the real tables.
5. The hand-off to readers is a named, foreign-keyed column that says it holds an Admission Contract.
6. The four scripts are deleted, DEC-e27625 is dispositioned, and the procedure chapter is the stacks call alone.

### L3, Vocabulary

**What it is.** L3 authors the business concept registry: the one governed list of the things the business talks about. An **entity** is a governed business thing such as Customer or Invoice. A **characteristic** is the meaning part of a name, such as "credit limit". A **business concept** is one property of one entity, and it is the unit that every contract refers to by identity. The platform needs this lane because a metric can mean one thing only if each concept it reads has exactly one identity; candidates are shaped by an AI panel (a maker, a checker and a moderator model) and written only after a certification record exists.

**How bc-docs defines it.**

- Foundation: "The platform's business vocabulary is one governed registry of Business Concepts — not three separate primitives (Business Object, Business Field, Canonical Field) joined by a Canonical Mapping." (`bc-docs:docs/foundation/the-contract-grammar.md:264 @ f4f5edd`)
- The model chapter: "Every entry is a business concept identified as `entity.property`. Duplication and merging become **structurally impossible**, not detected." (`bc-docs:docs/implementation/business-concept-registry.md:58-60 @ f4f5edd`)
- The panel's role: "It is a **concept-placement assistant.**" and "**it does not own identity.**" (`bc-docs:docs/implementation/business-concept-registry.md:230,238 @ f4f5edd`)
- The approved words are in the vocabulary page, slice 4, S4.1 (`bc-docs:docs/reference/vocabulary.md:509-538 @ f4f5edd`). BCF means "Business Concept Framework: the registry together with its authoring and certification" (`vocabulary.md:562`).
- The procedure is `docs/onboarding/business-field-and-business-object-onboarding.md`, retitled "Business Concept Authoring (BCF)" (`:4,23 @ f4f5edd`). The lane kit points instead to the model chapter and calls the onboarding chapter stale (`barecount-devhub:artifacts/lanes/L3-bcf-enrichment/README.md:6 @ 93cc1ea5`); that note predates the rewrite.

bc-docs contradicts itself in four places:

1. `business-vocabulary.md` gives the states `proposed`, `reviewing`, `certified`, `superseded`, `withdrawn` (`bc-docs:docs/operating-model/business-vocabulary.md:146-152 @ f4f5edd`). The database allows `draft`, `review`, `approved`, `active`, `superseded`, `archived` (query (bc_platform_dev, 2026-11-13): `SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='concept_registry.business_concept'::regclass AND contype='c'` -> the six-value CHECK). The vocabulary page already names this defect (`vocabulary.md:592`).
2. Three chapters say the old business-field tables "persist physically" (`business-vocabulary.md:171-173`; `business-field-and-business-object-onboarding.md:148-149,173`; `the-contract-grammar.md:274`). They do not exist (query: `SELECT table_schema, table_name FROM information_schema.tables WHERE table_name IN ('business_field','business_object','canonical_field','cc_field_mapping')` -> 0 rows).
3. The chapters and the vocabulary page list eight representation terms (`business-vocabulary.md:61-63`; `vocabulary.md:522`). The table holds 15 (query: `SELECT string_agg(term, ',') FROM concept_registry.representation_term` -> amount, code, count, date, date_time, duration, identifier, indicator, measure, name, percentage, quantity, rate, ratio, text).
4. The model chapter says entities and concepts follow "the Foundation five-state lifecycle" (`business-concept-registry.md:177-178`); concepts and characteristics have six states and entities five (CHECK constraints, same query on `concept_registry.entity` and `concept_registry.characteristic`).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Database schema | `concept_registry`, 13 tables: `alias`, `business_concept`, `business_concept_supersession`, `business_concept_version`, `characteristic`, `characteristic_definition_amendment`, `characteristic_supersession`, `concept_source_reference`, `entity`, `entity_supersession`, `entity_version`, `representation_term`, `supersession_proposal` | query: `SELECT table_name FROM information_schema.tables WHERE table_schema='concept_registry'` -> 13 |
| Database schema | `bcf`, 5 tables: `panel_output_record`, `certification_record`, `authoring_panel_rejection_log`, `calibration_event`, `oagis_seed`. The taxonomy's "13" and the readiness matrix's "18" (`platform-readiness-program.md:149`) are the same estate: 13 + 5 | query: same, `table_schema='bcf'` -> 5 |
| Module | `src/registry/concept-registry/` (the single writer `RegistryAuthoringService` and the read service) | `bc-core:src/registry/concept-registry/registry-authoring.service.ts:483-2246 @ ec72438b` |
| Module | `src/registry/bcf/` (panel, publication, adjudication, recommendations, orphan repair, telemetry) | `bc-core:src/registry/bcf/panel/registry-authoring-orchestrator.service.ts:1-39 @ ec72438b` |
| Module | `src/registry/framework-approval/` (issues and confirms the certification record). Shared with L6, to be split if the metric panels use it | `bc-core:src/registry/bcf/panel/registry-publication.service.ts:45 @ ec72438b` |
| Route prefix | `bcf/registry` (reads: 11 GET routes) | `bc-core:src/registry/concept-registry/registry-read.controller.ts:47-153 @ ec72438b` |
| Route prefix | `bcf/registry` (direct governed writes: 8 POST routes) | `bc-core:src/registry/concept-registry/registry-authoring.controller.ts:128-747 @ ec72438b` |
| Route prefix | `bcf/registry/.../*-recommendations` (operator-direct, 11 POST routes in 8 controllers) | `bc-core:src/registry/bcf/recommendations/correction/bcf-correction-recommendation.controller.ts:65-138 @ ec72438b` and its seven siblings |
| Route prefix | `bcf/registry-authoring-runs`, `bcf/registry-panel-runs`, `bcf/registry-publications`, `bcf/registry-shape-certifications`, `bcf/registry/provenance`, `bcf/panel-output-records` | `bc-core:src/registry/bcf/panel/registry-authoring-run.controller.ts:24`; `registry-panel-run-read.controller.ts:28`; `registry-publication.controller.ts:30`; `registry-shape-certification-confirm.controller.ts:35`; `registry-provenance.controller.ts:36`; `src/registry/panel-output-record.controller.ts:24 @ ec72438b` |
| Route prefix | `bcf` (review queue, operator adjudication, run disposition) | `bc-core:src/registry/bcf/adjudication/panel-operator-adjudication.controller.ts:49-121 @ ec72438b` |
| Route prefix | `bcf/registry/phase3-orphan-repair`, `bcf/registry/d443-phase2-cert-mint` (one-time repair routes; candidates for retirement) | `bc-core:src/registry/bcf/phase3-orphan-repair/bcf-phase3-orphan-repair.controller.ts:43-47`; `src/registry/d443-phase2-cert-supply/d443-phase2-cert-supply.controller.ts:37-41 @ ec72438b` |
| Route prefix | `concept-registry/source-references` (advisory link from a concept to a source field). Shared with L1, to be split | `bc-core:src/registry/concept-registry/source-reference/concept-source-reference.controller.ts:1-34 @ ec72438b` |
| Route prefix | `ai-telemetry`. Shared with AI, AI services, to be split | `bc-core:src/registry/bcf/telemetry/bcf-telemetry.controller.ts:43 @ ec72438b` |
| Screen | bc-admin `/business-concepts` and ten routes under it (browse, review queue, run detail, entity, concept, identity concept, shape correction, characteristic) | `bc-admin:src/components/AppRouter.tsx:271-281 @ d37b241` |
| Command | DevHub tools `devhub_bcf_search_entity`, `devhub_bcf_read_entity`, `devhub_bcf_search_concept`, `devhub_bcf_read_concept` | `barecount-devhub:src/mcp-server.js:3543,3584,3615,3657 @ 93cc1ea5` |
| Script | 11 files in barecount-devhub `scripts/` that call `/api/bcf/` routes | command: `git grep -l "api/bcf/" origin/main -- scripts \| wc -l` -> 11 |
| Prompts | `src/registry/bcf/panel/prompts/v1.3`, `v1.4`, `v1.5`; `v1.5` is the one loaded | `bc-core:src/registry/bcf/panel/in-process/panel-agents.ts:99 @ ec72438b` |
| Document | `implementation/business-concept-registry.md`, `operating-model/business-vocabulary.md`, the onboarding chapter above, `operating-model/finance-core-vocabulary-manifest.md`, `operating-model/gl-vocabulary-enrichment-design.md`, 17 technical notes named `business-concept-registry-*`, `business-context-framework-*`, `bcf-*` | command: `git ls-tree -r origin/main --name-only -- docs/reference/technical-notes/implementation` -> 17 matching files @ f4f5edd |

**The acts it performs.**

| Act | Who | Entry point as built | States and writes |
|---|---|---|---|
| Run the authoring panel on a candidate | `platform_admin` or `operator` | `POST /api/bcf/registry-authoring-runs` (`registry-authoring-run.controller.ts:28-29`) | Writes one `bcf.panel_output_record`. On `APPROVE_FOR_DRAFT` the orchestrator issues a certification record and calls the writer (`registry-authoring-orchestrator.service.ts:6-11`) |
| Shape a candidate without a model (operator-direct) | platform actor | the eleven `*-recommendations` routes | Writes a `panel_output_record` with operator-direct provenance; no registry write |
| Confirm a high-risk authoring act | `operator` only | `POST /api/bcf/registry-shape-certifications/confirm` (`registry-shape-certification-confirm.controller.ts:39-40`) | Writes `bcf.certification_record`, then the registry row |
| Create an entity, concept or characteristic | the writer only, never a route | `createEntity`, `createBusinessConcept`, `registerCharacteristic` (`registry-authoring.service.ts:483,874,1377`) | New row in `draft`. An entity created on the panel path is then made active automatically; a concept is not (`registry-authoring-orchestrator.service.ts:18-30`) |
| Publish (draft to active) | `platform_admin` or `operator`, two calls | `POST /api/bcf/registry-publications`, then `/confirm` (`registry-publication.controller.ts:34-48`) | `draft` to `active`; certification action `registry_transition` (`registry-publication.service.ts:8-19`) |
| Add a version, supersede, amend a definition, withdraw | `platform_admin` | `POST /api/bcf/registry/entities/:id/versions`, `/supersede`, `concepts/:id/versions`, `/supersede`, `/withdraw-draft`, `characteristics/:id/supersede`, `/amend-definition`, `/withdraw` (`registry-authoring.controller.ts:141,290,386,458,536,632,702,746`) | `active` to `superseded` or `archived`; rows in the three supersession tables |
| Adjudicate a run sent to operator review | `platform_admin` | `GET /api/bcf/review-queue`; `POST /api/bcf/registry-panel-operator-adjudications`; `POST /api/bcf/registry-panel-runs/:uid/disposition` (`panel-operator-adjudication.controller.ts:56,88,120`) | A new operator-direct panel record and a certification; no registry write (`panel-operator-adjudication.service.ts:33`) |

**What it receives and what it hands on.**

| Direction | Neighbour | What passes | Defined in bc-docs | Built |
|---|---|---|---|---|
| In | L8, Metric Directory and L6, Metric Contracts and certification | The demand: "a metric (L8/L6) pulls the exact chains (L4/L5) that pull the concepts (L3)" (`bc-docs:docs/governance/adrs/ADR-ce4314.md:46 @ f4f5edd`) | As a rule only; no record or trigger is named | Neither: no field records which metric asked for a concept |
| In | AI, AI services | Three model calls per run | `ADR-ffee4e` | Built; models are code defaults (`panel-agents.ts:57,67,88`) |
| In | Standards seed | `bcf.oagis_seed`, 133 rows | `business-concept-registry.md:208-219` | Built (query: `SELECT count(*) FROM bcf.oagis_seed` -> 133) |
| Out | L4, Observation Contracts | `business_concept_id` in each `field_mappings[]` entry | `business-field-and-business-object-onboarding.md:144` | Both (`bc-core:src/registry/meta-schemas/observation-v2.schema.json:126-129 @ ec72438b`) |
| Out | L5, Canonical Contracts | the grain entity and the selected concepts | `...onboarding.md:145` | Both (`bc-core:src/registry/contracts/contract.service.ts:975-977 @ ec72438b`) |
| Out | L6, Metric Contracts and certification | concept inputs and the metric grain entity | `...onboarding.md:146`; `vocabulary.md:545-548` | Both (not re-checked in code; reported in artifacts/spine-review/REVIEW-3-metric-lifecycle.md) |
| Out | Dependents of a superseded concept | `concept_registry.supersession_proposal` | Not defined | Table exists, 0 rows (query: `SELECT count(*) FROM concept_registry.supersession_proposal` -> 0) |

**State today.**

- **Live counts** (query: `SELECT lifecycle_state, count(*) FROM concept_registry.<table> GROUP BY 1`): entities 149 active, 6 superseded; business concepts 756 active, 62 superseded, 21 archived, 1 draft; characteristics 232 active, 7 superseded, 6 archived. Concept versions 1,057; entity versions 309; aliases 0; source references 0.
- **Panel records:** 2,743 rows in `bcf.panel_output_record`: 2,124 `APPROVE_FOR_DRAFT`, 602 `OPERATOR_REVIEW`, 12 `REJECT`, 4 `REJECT_DEFECT`, 1 `PASS`. The newest is dated 2026-11-12; 72 are from the last 30 days (query: `SELECT verdict_code, count(*) FROM bcf.panel_output_record GROUP BY 1`).
- **Certification records:** 6,333 rows in `bcf.certification_record`. Of these 2,837 have scope `registry`; 3,496 are for the retired `business_field` and `canonical_field` subjects (query: `SELECT coalesce(subject_kind, primitive_type), action_code, count(*) FROM bcf.certification_record GROUP BY 1,2`).
- **What works:** the panel route, the confirm route, publication and the review queue all exist and have recent rows. The registry has one writer; no script or other module at origin/main writes `concept_registry` by SQL except the source-reference service (command: `git grep -l -E "INSERT INTO concept_registry|UPDATE concept_registry" origin/main -- scripts src` -> one file, `concept-source-reference.service.ts`).
- **Duplicated:** a concept can be shaped by two makers (panel, or operator-direct) and reach `active` by two ends (automatic for entities on the panel path, the two-call publication otherwise). Three tables are named `certification_record` and two `panel_output_record`; the `contract` copies stopped on 2026-05-26 (query: `SELECT max(created_at) FROM contract.certification_record` -> 2026-05-26).
- **Hard-coded:** the model for each panel seat and the prompt version (`panel-agents.ts:57,67,88,99`).
- **Not built:** a version table for characteristics (query: `SELECT to_regclass('concept_registry.characteristic_version')` -> null; `registry-publication.service.ts:25-26` records the block); an `archived` state for entities.

**Known defects and risks.**

1. **The panel host defaults to a retired service.** Unless `BCF_PANEL_MODE=in-process` is set, the module builds the HTTP client for bc-ai (`bc-core:src/registry/bcf/panel/registry-authoring-panel.module.ts:75-87 @ ec72438b`). bc-ai is retired (ADR DEC-ffee4e).
2. **The reference chapter says a new concept cannot be authored from a screen.** "authoring a new concept has no UI" (`bc-docs:docs/reference/platform-workflow-catalog.md:41 @ f4f5edd`). bc-admin has five authoring screens (`AppRouter.tsx:274-280`).
3. **602 runs carry the verdict `OPERATOR_REVIEW`;** 166 records are dispositioned `pending_action` (query: `SELECT disposition_code, count(*) FROM bcf.panel_output_record GROUP BY 1`). Nothing in bc-docs says who clears them or by when.
4. **Role names differ by route.** Confirm needs `operator`; supersede needs `platform_admin`; source references need `mcf_publisher` (`registry-shape-certification-confirm.controller.ts:39`; `registry-authoring.controller.ts:142`; `concept-source-reference.controller.ts:34`).
5. **The four contradictions in bc-docs listed above.**
6. **One concept is in `draft` with no chapter saying what happens to it** (count above).

**Governing ADRs.**

| ADR | Plain summary | Status in the file |
|---|---|---|
| DEC-02f5a9 | One registry of concepts replaces business object, business field and canonical field | decided |
| DEC-149ab2 | Authority to approve registry content is delegated to the framework | decided |
| DEC-65dc86 | BCF is the forward model; the old vocabulary is legacy | decided |
| DEC-6c57e2 | The old vocabulary tables are "physically retained" | decided; **conflicts with the live database, where they are gone** |
| DEC-ffee4e | The panel runs inside bc-core; the roster is locked | implemented |
| DEC-61850f | Semantic role and value set are stored on the concept version | implemented |
| DEC-5a9dee | Foundation admits BCF, MCF and the Metric Directory as authority-creating families | implemented |
| DEC-1fbaf1 | Withdrawal archives vocabulary admitted in error | decided |

(Statuses read from `bc-docs:docs/governance/adrs/ADR-<uid>.md @ f4f5edd`, front matter.)

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/implementation/business-concept-registry.md` | keep nearly as is | The model is right; correct the lifecycle and the "persist physically" lines |
| `docs/operating-model/business-vocabulary.md` | rewrite | Its lifecycle matches no record; fold the rest into the model chapter |
| `docs/onboarding/business-field-and-business-object-onboarding.md` | rewrite | Its six action families all have routes in code (6 of 6, checked by route, not run). It omits publication, the review queue, supersede and withdraw, and it names tables that are gone |
| `docs/onboarding/canonical-field-seeding.md` | history | Eleven steps for a primitive that no longer exists (`:29-35`) |
| `docs/onboarding/multi-standard-onboarding.md` | history | Seven steps that create business fields and business objects |
| `docs/operating-model/finance-core-vocabulary-manifest.md`, `gl-vocabulary-enrichment-design.md` | history | Dated work logs, not definitions |
| The 17 technical notes | history | Design notes for slices already built |

**Open questions for the operator.**

1. Should a concept reach `active` only through the two-call publication, or also automatically as entities do on the panel path?
2. Is the operator-direct maker a permanent second door, or is it folded into one command with the panel as an optional step?
3. Should entities gain an `archived` state, or is supersession the only exit?
4. Who owns the 602 runs awaiting operator review: close them in bulk as history, or adjudicate each?
5. Is the panel roster a declaration in data (changed by a governed act) or does it stay in code?

**What "locked" will mean here.**

1. One command set creates, publishes, versions, supersedes and withdraws each of the three kinds; the two one-time repair routes are deleted.
2. The panel host has no default that points at bc-ai; the roster and prompt version are read from a declaration.
3. The lifecycle in the chapter equals the CHECK constraints, tested in CI.
4. A CI guard fails if any file outside the writer service writes `concept_registry`.
5. The `contract` copies of `certification_record` and `panel_output_record` are retired or marked as history in the data dictionary.
6. A fresh session authors one concept from the chapter alone.

### L4, Observation Contracts

**What it is.** An observation contract declares how one source table is read into business concepts: which source fields are selected, which concept each one carries, which rows are selected, and the shape of the source object that admission preserves. A **source object** is one admitted observation of source state. The platform needs this lane because it is the only place where a source's own field names meet the governed vocabulary; everything later reads concepts, never source fields.

**How bc-docs defines it.**

- Foundation: "An Observation Contract declares field selection from a Source Contract to business-vocabulary fields and defines the resulting Source Object shape preserved at admission." (`bc-docs:docs/foundation/the-contract-grammar.md:167 @ f4f5edd`)
- Foundation forbids that "A source slice is expressed anywhere other than the Observation Contract's `source_filter`" (`the-contract-grammar.md:183`).
- The vocabulary page names the **observation field mapping**: "How an observation contract reads each source field into a business concept: type, unit and form", recorded "inside the observation contract version's body" (`bc-docs:docs/reference/vocabulary.md:554 @ f4f5edd`). Its state value `active` is said "in force" (`vocabulary.md:347-350`).
- Runtime use is in `operating-model/admission-and-observation.md` (`:68-81`). The procedure is `onboarding/observation-contract-creation.md`.

bc-docs is stale and contradicts itself here:

1. The procedure describes grammar `barecount/observation/v1` and says so: "A full chapter rewrite for v2 is pending" (`bc-docs:docs/onboarding/observation-contract-creation.md:289 @ f4f5edd`). Every version that is not superseded uses v2 (query: `SELECT contract_json->>'$contract', count(*) FROM contract.observation_contract_version WHERE governance_state_code<>'superseded' GROUP BY 1` -> `barecount/observation/v2`, 22).
2. `contract-chain-assembly.md` says the contract maps to "Business Field code" and that "The chain operates with two vocabularies" (`bc-docs:docs/operating-model/contract-chain-assembly.md:113,214 @ f4f5edd`). `admission-and-observation.md:75` says the map is to "Business Concept property values". The second is what the code does.
3. The procedure's step 4 declares joins inside the contract (`observation-contract-creation.md:115-126`). Activation refuses any join: "an OC carries no join ... the multi-source join belongs to the Canonical Contract" (`bc-core:src/registry/contracts/contract.service.ts:1007 @ ec72438b`).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Database table | `contract.observation_contract`, `observation_contract_version`, `observation_contract_version_transition`, `observation_contract_approval` | query: `SELECT table_name FROM information_schema.tables WHERE table_schema='contract' AND table_name LIKE 'observation%'` -> 5 |
| Database table | `contract.observation_field_map` (0 rows; retired; mappings are held in the version body) | query: `SELECT count(*) FROM contract.observation_field_map` -> 0; `vocabulary.md:554` |
| Database table | `runtime.chain_authoring_run`. Shared with L5 and L7, to be split | query below |
| Database table | `runtime.reader_observation_binding` (21 rows). Shared with L7, to be split | query: `SELECT count(*) FROM runtime.reader_observation_binding` -> 21 |
| Module | `src/registry/substrate/author-observation-chain.*`, `chain-authoring-run.ts`, `abandoned-run-recovery.service.ts`. Shared with L5 and L7, to be split: one call authors "the OC(s) + reader provisioning ... + the CC" | `bc-core:src/registry/substrate/author-observation-chain.service.ts:2-8 @ ec72438b` |
| Module | `src/registry/contracts/` (`ContractService`, the lifecycle for five contract families). Shared with L2 and L5, to be split | `bc-core:src/registry/contracts/contract.service.ts:813-879 @ ec72438b` |
| Module | `src/registry/contracts/publish-chain.*`. Shared with L5, to be split: "authors a full OC-v2 + CC-v2 chain" | `bc-core:src/registry/contracts/publish-chain.service.ts:4-11 @ ec72438b` |
| Module | `src/registry/resolvers/observation-concept-resolver.service.ts` (field-to-concept integrity) | `bc-core:src/registry/contracts/contract.service.ts:676-687 @ ec72438b` |
| Module | `src/registry/meta-schemas/observation-v1.schema.json`, `observation-v2.schema.json` | `bc-core:src/registry/meta-schemas/observation-v2.schema.json:15 @ ec72438b` |
| Route prefix | `contracts/observation-chains` (`POST`, and `POST runs/:runId/reconcile`). Shared with L5 and L7, to be split | `bc-core:src/registry/substrate/author-observation-chain.controller.ts:21-49 @ ec72438b` |
| Route prefix | `contracts/chains`. Shared with L5, to be split | `bc-core:src/registry/contracts/publish-chain.controller.ts:18-23 @ ec72438b` |
| Route prefix | `contracts` (create, versions, submit, approve, activate, supersede, revert, bulk-transition, archive, expunge). Shared with L2 and L5, to be split | `bc-core:src/registry/contracts/contract.controller.ts:28-360 @ ec72438b` |
| Route prefix | `registry/substrate` (`POST resolve`: names to identities). Shared with L3 and L5, to be split | `bc-core:src/registry/substrate/substrate-resolve.controller.ts:19-24 @ ec72438b` |
| Screen | bc-admin `/registry/contracts/observation` (list) | `bc-admin:src/components/AppRouter.tsx:166 @ d37b241` |
| Screen | bc-admin `/catalog/metrics/governed/:metricContractUid/author-chain`. Shared with L5, to be split | `bc-admin:src/components/AppRouter.tsx:205`; `src/api/observation-chains.ts:128 @ d37b241` |
| Command | DevHub tools `devhub_publish_chain`, `devhub_substrate_resolve`. Shared with L5 | `barecount-devhub:src/mcp-server.js:3788,3732 @ 93cc1ea5` |
| Script | `scripts/author-arpi-oc-v2-slice.mjs`, `scripts/mcf/partc-author-oc-kurgv.mjs`, `scripts/fix-oc-field-mappings.mjs`, `scripts/fix-oc-relevance.mjs`, and 28 more files in `scripts/` that name `observation_contract` | command: `git grep -l -iE "observation_contract" origin/main -- scripts \| wc -l` -> 32 @ ec72438b |
| Document | `onboarding/observation-contract-creation.md`; the Observation sections of `operating-model/admission-and-observation.md` and `contract-chain-assembly.md` | cited above |

The taxonomy's ownership row is `contract.observation_contract*`, `observation_field_map`; `contracts/observation-chains` (`barecount-devhub:artifacts/lanes/LOCKED-LANE-TAXONOMY-2026-08-24.md:33 @ 93cc1ea5`). Against today's code the route it names is not L4's alone, and three further routes also author observation contracts.

**The acts it performs.**

| Act | Who | Entry point as built | States and writes |
|---|---|---|---|
| Create the contract and a version | `platform_admin` or `operator` | `POST /api/contracts`, `POST /api/contracts/:id/versions` (`contract.controller.ts:35-36,212-213`) | Version in `draft`. The body is checked against the meta-schema and for field-to-concept integrity (`contract.service.ts:676-687`) |
| Submit, approve, activate | same roles | `POST .../versions/:version/submit`, `/approve`, `/activate` (`contract.controller.ts:271-302`) | `draft` to `review` to `approved` to `active`. Activation requires exactly one source reference and no join, and re-runs the integrity check (`contract.service.ts:982-1020`). Each move writes a row to the transition table by trigger |
| Supersede | same roles | `POST .../versions/:version/supersede` (`contract.controller.ts:316-317`) | `active` to `superseded` |
| Author a whole chain | `platform_admin` | `POST /api/contracts/observation-chains`, dry run first (`author-observation-chain.controller.ts:28-38`) | Claims a run, creates the contract, the version and activates it in one step (`author-observation-chain.service.ts:293-318`), then the reader, flavor, bindings and the canonical contract. Writes `runtime.chain_authoring_run` |
| Reconcile an abandoned run | operator only | `POST /api/contracts/observation-chains/runs/:runId/reconcile` (`author-observation-chain.controller.ts:48-49`) | Archives the run's leftover reader and empty contract shell; sets `reconciled_at` |
| Publish a chain (older service) | `platform_admin` | `POST /api/contracts/chains` (`publish-chain.controller.ts:22-23`) | Create or reuse, version, activate, supersede the prior version (`publish-chain.service.ts:6-7`) |

**What it receives and what it hands on.**

| Direction | Neighbour | What passes | Defined in bc-docs | Built |
|---|---|---|---|---|
| In | L1, Source Catalog | `source_version_id`; `source_table`, `source_field` | `observation-contract-creation.md:85` | Both (`observation-v2.schema.json:15,126`) |
| In | L2, Source and Admission Contracts | pinned pair `sc_contract_id`, `sc_version_code`, `ac_contract_id`, `ac_version_code` in `source_references[]` | The chapter gives the older shape `sc_version_id`, `ac_version_id` (`:87`) | Built in the newer shape (`observation-v2.schema.json:34`); the document is wrong |
| In | L3, Vocabulary | `business_concept_id` per mapping | `vocabulary.md:554` | Both (`observation-v2.schema.json:126-129`) |
| Out | L5, Canonical Contracts | the canonical version's `observation_references[]` pins `observation_contract_id` and `observation_version` | Not in the L4 chapter | Built (`contract.service.ts:122-127`) |
| Out | L7, Readers and connections | `runtime.reader_observation_binding`; the reader flavor's derived copy | `admission-and-observation.md:83-92` | Built (`bc-core:src/registry/readers/reader-chain-resolution.service.ts:182 @ ec72438b`) |
| Out | RT, Runtime (admission) | field map, identity semantics, `source_filter`, `so_schema` | `admission-and-observation.md:60-81` | (not re-checked; reported in artifacts/spine-review/REVIEW-1-source-to-so.md) |
| Out | What starts admission after a version comes into force | nothing | Not defined | Not built in this lane |

**State today.**

- **Live counts.** 17 contracts, 5 archived. 29 versions: 19 `active`, 7 `superseded`, 2 `draft`, 1 `approved` (query: `SELECT governance_state_code, count(*) FROM contract.observation_contract_version GROUP BY 1`). All 17 parent rows say `status_code = 'draft'` (query: `SELECT status_code, count(*) FROM contract.observation_contract GROUP BY 1` -> draft, 17). All 17 have `reader_id` null.
- **More than one version in force per contract.** One contract (`oc-3kgrr`) has six versions in state `active`; two others have two each (query: `SELECT observation_contract_name, version_code, governance_state_code, supersede_after FROM ... WHERE governance_state_code='active'`). Activating a successor only stamps the older version with `supersede_after = now() + interval '48 hours'` (`bc-core:src/registry/contracts/contract-version.repository.ts:204-220 @ ec72438b`). No code in `src` reads that column to complete the supersession (command: `git grep -n "supersede_after" origin/main -- src` -> the stamp, schema files, fixtures and two resolvers that sort by it). Six versions are `active` with the window already past (query: `SELECT count(*) ... WHERE governance_state_code='active' AND supersede_after < now()` -> 6).
- **Which route is used.** The transition table holds 45 rows since 2026-09-27. 44 came through the plain contract routes, all by one authenticated subject who submitted, approved and activated. One came from the chain service, as `draft` to `active` in one step (query: `SELECT transition_cause_code, actor_kind_code, from_state_code, to_state_code, count(*) FROM contract.observation_contract_version_transition GROUP BY 1,2,3,4`). None came from `publish-chain`.
- **Chain runs.** 12 rows: 7 `committed`, 5 `abandoned` (3 reconciled). The last is dated 2026-10-06 (query: `SELECT state_code, count(*), max(created_at) FROM runtime.chain_authoring_run GROUP BY 1`).
- **Alternate routes: six.** (1) the plain contract routes; (2) `contracts/observation-chains`; (3) `contracts/chains`, also reached by `devhub_publish_chain`; (4) `contracts/bulk-transition` for state moves (`contract.controller.ts:127-128`); (5) scripts that boot the application and call `ContractService` directly (`bc-core:scripts/author-arpi-oc-v2-slice.mjs:6-9 @ ec72438b`); (6) scripts that write version rows by SQL (`bc-core:scripts/fix-oc-field-mappings.mjs:184-187`, an `UPDATE`; `scripts/fix-oc-relevance.mjs:121`, a `DELETE`).
- **Coverage.** 51 distinct concepts are mapped by in-force versions (query: `SELECT count(DISTINCT fm->>'business_concept_id') FROM contract.observation_contract_version v, jsonb_array_elements(v.contract_json->'body'->'field_mappings') fm WHERE v.governance_state_code='active'` -> 51), against 756 active concepts. 14 of the 19 in-force versions declare a `source_filter`.
- **Not built:** the two routes the procedure names for mapping, `POST /api/ai/suggest/oc-field-mapping` and `POST /api/field-mapping/confirm` (command: `git grep -n "oc-field-mapping\|field-mapping/confirm" origin/main -- src` -> no match), and the table `contract.business_field_alias` (query -> absent).

**Known defects and risks.**

1. **Several versions of one contract are in force at once, and nothing ends the 48-hour window** (citations above). Which version a reader or a canonical contract uses then depends on a sort order, not on a state.
2. **Two lifecycles for the same act.** The plain route passes review and approval; the chain service moves `draft` to `active` directly (`author-observation-chain.service.ts:318`). The closure of that skip covers canonical and metric contracts only (`contract.service.ts:430-431`).
3. **No separation of author and approver** is evidenced: one subject made all 14 submissions, 14 approvals and 13 activations.
4. **The parent state field is never kept true** (all `draft`); the vocabulary page records it (`vocabulary.md:365`).
5. **The version state field has no CHECK** on the observation table (query: `SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='contract.observation_contract_version'::regclass AND contype='c'` -> version format and `transition_declaration_json IS NULL` only); `vocabulary.md:369` records it.
6. **Scripts at origin/main change version rows by SQL** (route 6 above). The immutability trigger `trg_cv_immutable` is present today, but the scripts remain.
7. **ADR DEC-585edb adds a `sum` strategy to joins in the observation grammar; activation refuses any join there.** The ADR is marked implemented.
8. **The procedure cannot be followed** (next table).

**Governing ADRs.**

| ADR | Plain summary | Status in the file |
|---|---|---|
| DEC-5fd322 | The observation contract is the design-time artifact; readers execute it | implemented |
| DEC-36d78f | A reader observes selected fields under standard names | implemented |
| DEC-0e3c64 | The observation contract belongs to the canonical side of the chain | implemented |
| DEC-4a17e0 | Each mapping carries a governed concept identity | decided |
| DEC-585edb | A `sum` reduce strategy for joins in the observation grammar | implemented; **conflicts with the activation rule that an observation contract carries no join** |
| DEC-f4084d | One governed call authors a chain (`publishChain`, source stack, resolver) | implemented; overlaps the newer chain service |
| DEC-fbc085 | Each state change of a contract version writes an append-only transition row | decided |

(Statuses read from `bc-docs:docs/governance/adrs/ADR-<uid>.md @ f4f5edd`. The procedure chapter cites DEC-d72560, the two-vocabulary model, as governing (`observation-contract-creation.md:15`); `business-vocabulary.md:17` lists the same ADR as superseded.)

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/onboarding/observation-contract-creation.md` | rewrite | Two of its eight steps can be followed as written (2 and 3). Steps 1, 4, 5 and 6 name a retired primitive, a refused construct or routes that do not exist; steps 7 and 8 describe the v1 body and wrong table names. Judged by checking each named route, table and body key at origin/main and in the live database, not by running the steps |
| `docs/operating-model/admission-and-observation.md` (Observation sections) | keep nearly as is | Matches the code on concepts, single source and `source_filter` |
| `docs/operating-model/contract-chain-assembly.md` (Observation Contract; Vocabulary Transition) | rewrite | Teaches business fields, canonical mapping and two vocabularies |
| `artifacts/lanes/L4-oc-bcf-catalog-map/README.md` and its two notes (barecount-devhub) | history | August state; three in-force contracts then, 19 in-force versions now |

**Open questions for the operator.**

1. Which is the one door for authoring an observation contract: the plain contract routes, or the chain call that also authors the reader and the canonical contract?
2. If the chain call stays, is it split so that L4, L5 and L7 each have their own act, or kept as one act owned by one lane?
3. May an observation contract go from `draft` to `active` without review and approval, or must every route pass both?
4. Should exactly one version per contract be in force, with the 48-hour window ended by a governed act, or removed?
5. Is the parent `status_code` retired, or defined and kept true?

**What "locked" will mean here.**

1. One command set creates, versions, brings into force and supersedes an observation contract; `contracts/chains`, the direct-service scripts and the SQL scripts are deleted.
2. At most one version per contract is in state `active`, enforced in the database, and the live rows meet it.
3. `governance_state_code` on the version table has a CHECK, and the parent field is retired or true.
4. The chapter describes the v2 body and names only routes and tables that exist, checked in CI against the meta-schema.
5. The hand-off to L5 (`observation_references[]`) and to L7 (the reader observation binding) is written in the chapter with its fields.
6. A fresh session authors one observation contract over an existing source and admission pair from the chapter alone.

### L5, Canonical Contracts

**What it is.** A canonical contract declares the business meaning of one entity (a governed business thing such as a customer invoice) independent of any source system. Each version of the contract names the business concepts it selects, the source legs it reads, the derivations it computes, and the shape of the table that will hold the result. The platform needs it because a canonical object, the record a metric is evaluated from, is produced only by applying one canonical contract version to admitted source objects. This lane authors those versions, moves them through their states, has their tables created for each tenant, and fixes which version an evaluation reads.

**How bc-docs defines it.**

- Foundation: "A Canonical Contract declares the canonical form of one Entity (formerly Business Object; DEC-02f5a9): its grain, field selection, resolution rules across multiple Source Objects, resolved output schema, semantic rules, and temporal gate." (`bc-docs:docs/foundation/the-contract-grammar.md:189 @ f4f5edd`). The same section lists eight required body keys (`:191`).
- Vocabulary: canonical grain is "The set of values that identifies one canonical object: two canonical objects with the same grain values in the same period are the same observation" (`bc-docs:docs/reference/vocabulary.md:544 @ f4f5edd`). The field value `active` on a canonical contract version is said "in force" (`vocabulary.md:347-350`).
- Governing chapters: `docs/operating-model/canonical-evaluation.md`, `docs/operating-model/contract-chain-assembly.md`, and the procedure `docs/onboarding/canonical-contract-creation.md`. All three carry `status: drafting` (`canonical-evaluation.md:5`, `contract-chain-assembly.md:5`, `canonical-contract-creation.md:5 @ f4f5edd`).
- bc-docs is stale here. The procedure teaches the `barecount/canonical/v1` envelope and `contract.cc_field_mapping` (`canonical-contract-creation.md:44-45, 248`); every live version is `barecount/canonical/v2` and that table does not exist (queries under "State today"). The operating-model chapter says the evaluator "applies a Canonical Contract version and Canonical Mapping version" (`canonical-evaluation.md:45`), while the vocabulary page says "Canonical mapping is retired" (`vocabulary.md:558`).
- bc-docs is silent on what the code enforces. `legal_entity_key_form`, `ccv2-resolve` and `provisioning:worker` occur in no file under `docs/` outside governance and the generated reference (command: `git -C bc-docs grep -l -e <term> origin/main -- docs ':!docs/governance' ':!docs/reference/api' ':!docs/reference/code-index' ':!docs/reference/data-dictionary'` -> no file for each of the three). `pending_provisioning` appears only in the vocabulary page as a defect, in `tenant-metric-binding.md`, and in evidence files (same command).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Module | `ContractService` (version write, state changes); shared with L2, L4 and L6, to be split by family | `bc-core:src/registry/contracts/contract.service.ts:588-600, 813-875 @ ec72438b` |
| Module | `ContractVersionRepository` (48-hour supersession mark) | `bc-core:src/registry/contracts/contract-version.repository.ts:201-220 @ ec72438b` |
| Module | `ProvisioningReadinessService`, its controller and its 5-minute scheduler | `bc-core:src/registry/contracts/provisioning-readiness.service.ts:83-107`; `provisioning-readiness.controller.ts:17-33`; `provisioning-readiness.scheduler.ts:4, 24 @ ec72438b` |
| Module | `canonical-contract-pool-readiness.ts` (two "which version" predicates) | `bc-core:src/registry/contracts/canonical-contract-pool-readiness.ts:31-76 @ ec72438b` |
| Module | `AuthorObservationChainService`; shared with L4, to be split | `bc-core:src/registry/substrate/author-observation-chain.service.ts:71, 403, 505-516 @ ec72438b` |
| Module | `PublishChainService`; shared with L4, to be retired | `bc-core:src/registry/contracts/publish-chain.service.ts:147-151 @ ec72438b` |
| Module | Successor runner and its command line | `bc-core:src/registry/concept-registry/le-classification/le-cc-successor.runner.ts:128-285, 312-321, 641 @ ec72438b` |
| Module | `src/schema-provisioner/` (table name, table definition, activation fan-out, command store, worker); shared with L6 and L10, to be split | `bc-core:src/schema-provisioner/fact-table-name.ts:80-94`; `ddl-generator.service.ts:157-188`; `contract-activation.service.ts:73-112 @ ec72438b` |
| Module | Plane pins (which version each demo world reads) | `bc-core:src/database/plane/plane-cc-version-binding.ts:26-35 @ ec72438b` |
| Module | `CcV2CanonicalResolverService` and `t/ccv2-resolve`; shared with RT, Runtime, to be split: L5 owns the version choice, RT owns the run | `bc-core:src/boundary/ccv2-canonical-resolver.service.ts:735-775`; `ccv2-canonical-resolver.controller.ts:22-39 @ ec72438b` |
| Route prefix | `contracts` (shared with L2, L4), `contracts/observation-chains`, `contracts/chains`, `schema-provisioner/provisioning`, `t/ccv2-resolve` | `bc-core:src/registry/contracts/contract.controller.ts:28`; `author-observation-chain.controller.ts:21`; `publish-chain.controller.ts:18`; `provisioning-readiness.controller.ts:18 @ ec72438b` |
| Table | `contract.canonical_contract`, `canonical_contract_version`, `canonical_contract_version_transition`, `canonical_contract_approval`; `canonical_mapping`, `canonical_mapping_version` (retired, empty) | query (bc_platform_dev, 2026-11-13): `SELECT table_name FROM information_schema.tables WHERE table_schema='contract' AND table_name LIKE 'canonical%'` -> these six |
| Table | `schema_provisioner.provisioning_command` and its transitions (canonical rows); `tenant.contract_binding`; shared with L6 and L10 | queries under "State today" |
| Database guard | Body frozen from `approved` onward; key form set once; grain pin set once | `bc-db:migrations/0037_contract_version_freeze_approved_onward.sql:4-9`; `0044_contract_version_legal_entity_key_form.sql:7-23`; `0045_canonical_contract_version_grain_entity_version_pin.sql:12-30 @ c6de1c4` |
| Screen | Canonical contracts list (`registry/contracts/canonical`); chain authoring page, reached from a metric (shared with L4) | `bc-admin:src/components/AppRouter.tsx:167, 205 @ d37b241` |
| Command | `npm run provisioning:worker`, `provisioning:sweep`, `seed:registry` | `bc-core:package.json:26, 28, 41 @ ec72438b` |
| DevHub tool | `devhub_publish_chain` | `barecount-devhub:src/mcp-server.js:3788-3799 @ 93cc1ea5` |
| Document | The three chapters above; `docs/onboarding/canonical-field-seeding.md`; the lane kit `artifacts/lanes/L5-cc/README.md` | paths as given |

The lane taxonomy's row is corrected in two places. `canonical_mapping*` is retired and holds no rows. The provisioning modules, the readiness pass and the plane pins were not listed and belong here or are shared.

**The acts it performs.**

| Act | Who | Entry point as built | States | Writes |
|---|---|---|---|---|
| Create a version | `platform_admin` or `operator` | `POST /api/contracts/:contractId/versions` (`contract.controller.ts:212-221`) | born `draft` (`contract.service.ts:770`) | one row in `canonical_contract_version` |
| Create the first version with its observation contracts | `platform_admin` | `POST /api/contracts/observation-chains`, dry run available (`author-observation-chain.controller.ts:28-38`) | `draft`, then the three acts below (`author-observation-chain.service.ts:514-516`) | version `1.0.0` only (`:71`) |
| Submit | same roles | `POST …/versions/:version/submit` (`contract.controller.ts:271-272`) | `draft` to `review` | a transition row, written by a database trigger |
| Approve | same roles | `POST …/versions/:version/approve` (`:286-287`) | `review` to `approved`; the body is frozen from here (bc-db 0037) | a transition row |
| Activate | same roles | `POST …/versions/:version/activate` (`:301-302`) | `approved` to `pending_provisioning`, never straight to `active` (`contract.service.ts:1036-1037`); from `draft` it is refused (`:889-900`) | one provisioning command per affected tenant and a contract binding (`contract-activation.service.ts:92-112`). The dossier for L10, Tenant onboarding, reads the same service as writing the binding when the version becomes `active`; the two readings differ, and the Define step of L5 settles it |
| Create the tenant's table | the owner-privileged worker | `npm run provisioning:worker` (`package.json:26`) | command `pending` to `provisioned` or `failed` | `fact.co_<contract>_v<version>` in the tenant database (`fact-table-name.ts:80-94`) |
| Bring into force | the readiness pass | worker after a drain (`provisioning-worker-cli.ts:74`), `POST /api/schema-provisioner/provisioning/resolve-readiness`, or the scheduler | `pending_provisioning` to `active`, under a lock on the grain entity (`contract.service.ts:1090-1094`) | stamps `supersede_after = now() + 48 hours` on other versions in force (`contract-version.repository.ts:216-220`) |
| Supersede | same roles | `POST …/versions/:version/supersede` (`contract.controller.ts:316-317`) | `active` to `superseded` | a transition row |
| Hold a demo-plane version | command line only | `holdForProvisioning` (`contract.service.ts:873-875`); its only caller is the successor runner (`le-cc-successor.runner.ts:321`) | `approved` to `pending_provisioning`, no fan-out | a transition row |

All citations in this table are `bc-core … @ ec72438b`.

**What it receives and what it hands on.**

| Direction | With | What passes | In bc-docs | In code |
|---|---|---|---|---|
| In | L3, Vocabulary | Business concepts in force on one grain entity; an optional pin to one entity version | Yes, in old words (`canonical-contract-creation.md:52-58`) | Yes (`contract.service.ts:659-660`) |
| In | L4, Observation Contracts | Each selected concept must be observable from an observation contract already in force | No | Yes (`contract.service.ts:670-673`) |
| Out | RT, Runtime | The version an evaluation reads | Foundation only: "Every reference to an authoritative object identifies its type, its identity, and its version. Implicit references are forbidden." (`the-invariants.md:105 @ f4f5edd`) | Yes, by a different rule (`ccv2-canonical-resolver.service.ts:742-749`) |
| Out | L10, Tenant onboarding | A provisioning command and a contract binding per affected tenant | The binding is defined as the tenant's adoption (`tenancy-and-binding.md:98 @ f4f5edd`) | The command is built; the binding is written and never read to choose a version |
| Out | L6, Metric Contracts and certification; L9, Chain integrity | "Approved and beyond" as the version a metric declaration may rest on | ADR only (DEC-b36e15) | Yes (`canonical-contract-pool-readiness.ts:38-50`) |
| Out | PV, Proof against the source | The version each demo world pins | ADR only (DEC-3f6b1b) | Yes, as a code constant (`plane-cc-version-binding.ts:26-35`) |

**State today.**

- **Works.** One version write, one state write and one table generator serve every route. The resolver reads `field_selection`, `derivations`, `observation_references`, `join_semantics` and `posting_date_field` from the body (command: `git show origin/main:src/boundary/ccv2-canonical-resolver.service.ts | grep -c <key>` -> 11, 21, 24, 15, 6).
- **Live counts.** 11 contracts, 2 archived; 25 versions, all `barecount/canonical/v2`. query (bc_platform_dev, 2026-11-13): `SELECT governance_state_code, count(*), count(DISTINCT canonical_contract_id) FROM contract.canonical_contract_version GROUP BY 1` -> active 9 (7 contracts), approved 4 (4), pending_provisioning 3 (2), superseded 9 (3). `canonical_mapping` 0 rows, `canonical_mapping_version` 0 rows, `canonical_contract_approval` 1 row, transitions 42 (query: counts of each table).
- **Provisioning commands.** query: latest transition per command in `schema_provisioner.provisioning_command`, family `canonical` -> provisioned 14, pending 2, failed 1. The two pending are `fact.co_cc_das36_v4_0_0` (requested 2026-10-29) and `fact.co_cc_das36_v5_0_0` (2026-11-01), both for Kaveri.
- **Duplicated: five routes write a canonical version at main.** (1) `POST /api/contracts/:id/versions`. (2) `POST /api/contracts/observation-chains`. (3) The successor runner, `le-cc-successor-run-cli --mode=apply`, with one code constant per version (`le-cc-successor.runner.ts:128, 142, 180, 230, 271`). (4) `POST /api/contracts/chains` and the DevHub tool `devhub_publish_chain`. (5) `npm run seed:registry` (`seed-registry-full.ts:1416`). A sixth, a grain-binding command line, is not at main (command: `git grep -c declareCanonicalGrainBinding origin/main -- src` -> no match).
- **Broken.** Route 4 calls create and then activate from `draft` (`publish-chain.service.ts:149-151`), which the service refuses for a canonical contract (`contract.service.ts:889-900`). Read, not executed.
- **Hard-coded.** The route in (1) passes no options (`contract.controller.ts:221`), so the grain pin and the key form (how a canonical table carries the legal entity: `canonical_id_v1` or `label_v1`, `ddl-generator.service.ts:117`) can be declared only through the runner. Demo-world pins are a code constant with four worlds. The demo producer routine is chosen by version string alone (`bc-core:src/boundary/plane/demo-co-producer.ts:17-33`). Grain entities must be listed in a code manifest (`le-classification-manifest.ts:50-58`).
- **Not built.** Nothing ends the 48-hour window: `supersede_after` is written at `contract-version.repository.ts:216` and read only by the ordering predicates (command: `git grep -n supersede_after origin/main -- src`). No route starts canonical resolution on its own: `resolveForContract` has two callers, the controller and the demo command line (`git grep -n "resolveForContract(" origin/main -- src`).

**Known defects and risks.**

1. The tenant plane reads the globally in-force version, ordered by `supersede_after IS NULL` and then by version number (`ccv2-canonical-resolver.service.ts:742-749`). Foundation requires an explicit version (`the-invariants.md:105`). The tenant's contract binding takes no part.
2. The readiness pass tries every `pending_provisioning` canonical version (`provisioning-readiness.service.ts:83-98`) and treats "zero affected tenants" as complete (`provisioning-readiness-assessor.service.ts:19`). The exclusion for demo-pinned versions is applied only in the fan-out (`contract-activation.service.ts:84-88, 103-106`; command: `git grep -n isPlanePinnedCcVersion origin/main -- src` -> that file and its definition only). A held version can therefore be brought into force by any run of the pass. Three versions are held today: cc-das36 5.0.0 and 5.1.0, cc-apl 1.0.0 (query: versions in `pending_provisioning`).
3. Two contracts each have two versions in force, both past their window: cc-das36 3.0.0 and cc-x13pb 2.0.0 carry `supersede_after` 2026-10-26 (query: versions in `active`, with `supersede_after`).
4. cc-das36 4.0.0 is in force and is the version a tenant resolve would select, while its only tenant table command is still `pending` (queries above).
5. The world `kaveri-demo-v3lc5-v2` pins cc-das36 5.2.0 (`plane-cc-version-binding.ts:34`); no such version exists (query: versions by contract).
6. All 17 rows of `tenant.contract_binding` are `is_active = true` with no end date, including superseded versions (query: `SELECT contract_family, is_active, count(*), count(effective_to) FROM tenant.contract_binding GROUP BY 1,2` -> canonical, true, 17, 0).
7. The meta-schema requires `grain`, `resolution_rules`, `semantic_rules`, `temporal_gate`, `business_object_code` and `evaluation_tier` (`bc-core:src/registry/meta-schemas/canonical-v2.schema.json`, `body.required`); the resolver reads none of them (grep count 0 for each).
8. Approval needs no approval record: 1 approval row exists for 25 versions.
9. The resolver controller's header says "@PlatformOnly"; the decorator is `@TenantScoped()` (`ccv2-canonical-resolver.controller.ts:4-6, 22`).
10. The table generator names the tenant schema directly (`ddl-generator.service.ts:160, 188`), so demo-plane tables are written by hand per version (`bc-db:migrations/0050, 0053, 0060, 0069, 0070 @ c6de1c4`).

**Governing ADRs.** Status is from each ADR file's front matter at bc-docs `f4f5edd`.

| ADR | Plain summary | Status |
|---|---|---|
| DEC-acce2b (D476) | The resolver reads canonical-v2 and observation-v2 bodies; it replaced the canonical mapping resolver | implemented |
| DEC-a6258b (D430) | Each canonical field is one concept; one grain entity per contract | decided |
| DEC-4a17e0 (D431) | Each concept must be observable from an observation contract | decided |
| DEC-3785f8 (D513) | Value normalization happens at the canonical boundary | implemented |
| DEC-c05551 (D574) | Legal entity is resolved through a source-to-entity binding | decided |
| DEC-ffbc24 | Legal entity is a system axis; key form and grain pin | decided |
| DEC-0a187d | Declared joins across source legs | decided |
| DEC-7d2f8c | One-hop derivations live at the canonical boundary | implemented |
| DEC-b36e15 | Platform reads bind to "approved and beyond"; no skip from draft | decided |
| DEC-3f6b1b | A demo plane pins its own version | decided |
| DEC-fbc085 | A transition record for every state change | decided |
| DEC-29b518 | Activation gates fail closed | decided |
| DEC-a7c0f9, DEC-f5018a | Earlier resolution and contract-split designs | implemented |
| DEC-35b34b, DEC-9d1f4b | Aggregation authority; shared dimension normalization | decided |

Conflicts and gaps:
- DEC-3f6b1b keeps "global active-version selection" for tenants, against Invariant IV and against ruling T3 (decided; the main document, under "The rulings").
- DEC-f5018a and DEC-35b34b are written against the canonical mapping and `cc_field_mapping`, which DEC-02f5a9 (decided) retired.
- DEC-1bb88e (hold and fan-out exclusion) has no file at origin/main, yet 107 source files cite it (command: `git grep -l DEC-1bb88e origin/main -- src | wc -l` -> 107). DEC-d2583f and DEC-66ef36 also have no file.
- D305 (the 48-hour window) resolves to DEC-bebaec, whose file is a different, superseded decision (the D-code mapping is from `adr-triage.tsv`, not re-checked; the file status was re-read).

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/onboarding/canonical-contract-creation.md` | rewrite | None of its nine steps (1 to 4, 4b, 5 to 8) can be followed as written. Judged step by step: each names the v1 envelope, a table that does not exist (`cc_field_mapping`, `contract_version`), a route that does not exist (`/api/onboarding/cm/*`, `/api/canonical-fields`; `git grep` in bc-core src -> no match), or body keys the resolver does not read. Step 8 expects version 1.0.0 `active`; the code writes `pending_provisioning`. |
| `docs/onboarding/canonical-field-seeding.md` | history | Its store is gone; its own bridging note says the concept registry supersedes it (`:31`). |
| `docs/operating-model/canonical-evaluation.md` | rewrite | Describes canonical mapping and `resolution_rules[]` as executed steps (`:45, 78, 87-103`). |
| `docs/operating-model/contract-chain-assembly.md` (canonical part) | rewrite | Business Field and Canonical Field vocabulary (`:51, 140-157, 214-225`). |
| `docs/foundation/the-contract-grammar.md`, "Canonical Contract" | keep nearly as is | Add the v2 body keys, the key form and the grain pin. |
| `docs/operating-model/tenancy-and-binding.md`, "Contract binding" | rewrite, following ruling T3 | States adoption that the code does not read. |
| `docs/onboarding/metric-workstream.md:171` | rewrite | Describes version-pinned bindings that do not exist on the tenant plane. |

**Open questions for the operator.**

1. Which version does a tenant evaluation read: the tenant's adopted version in its contract binding (ruling T3), or the globally in-force version as built?
2. Where do demo-world pins live: a code constant as today, or a governed record?
3. Should a version read only by a demo plane share the tenant version line and be "held", or have its own declaration?
4. Which authoring route survives: the versions route extended with grain pin and key form, with the chain route for first versions, and the other three deleted?
5. Should the 48-hour window end automatically, or stay a manual supersede act?
6. Must approval require an approval record from a second person?

**What "locked" will mean here.**

1. One route creates a canonical version and can declare the grain pin and the key form; the runner constants, the chain-publish route, its DevHub tool and the v1 seeds are deleted, and a CI guard fails on a new caller of the version write.
2. The readiness pass skips or refuses every held version, with a test that fails if it does not.
3. No contract has two versions in force past the window, checked by a query in CI or in DevHub.
4. The version an evaluation reads is one written rule, implemented in one predicate, and the tenant's binding agrees with it.
5. The body keys the meta-schema requires and the keys the resolver reads are the same set.
6. One chapter replaces the four listed above, and a session new to the lane authors a successor version from it without reading code.

### L6, Metric Contracts and certification

**What it is.** A Metric Contract is the governed declaration of one metric: its formula, the business concepts its variables read, its metric grain (the entity one value describes) and its filters. This lane authors that contract as a version, carries the version through review and approval, and has it certified. "Certified" is the approved status word for a version that passed the certification gate and may be evaluated for a tenant; the state field then holds the value `active`. The platform needs the lane because the runtime evaluates only a version that is current and holds that state (`bc-core:src/boundary/metric-spec-loader.ts:229-238 @ ec72438b`).

**How bc-docs defines it.**

- Foundation: "Seven states: `draft`, `review`, `approved`, `audit_pending`, `active`, `audit_blocked`, `superseded`. Certification gates activation: an MCV reaches `active` only with a certification record (DEC-c48b0f). The ten-transition matrix — including the C6 invalidation cascade, the C7 reintake gate, and the C8 activation gate — is enforced by substrate triggers" (`bc-docs:docs/foundation/the-contract-grammar.md:361-365 @ f4f5edd`).
- The readiness chapter's row: "**L6** | MCF Metric (+ certification) | `mcf.metric_contract*` + bindings + `certification_record`" with "cert = an L6 *capability*, not a lane" (`bc-docs:docs/implementation/platform-readiness-program.md:107 @ f4f5edd`).
- The status words are in the vocabulary page, group 4: "the status people say is **certified**, and it means deployable to a tenant. "Active" is not said as a status" (`bc-docs:docs/reference/vocabulary.md:119 @ f4f5edd`).
- The enforced transitions are rendered in `docs/reference/lifecycle-map.md`, a generated page dated 2026-09-30 (`bc-docs:docs/reference/lifecycle-map.md:3-5,21-32 @ f4f5edd`). The meaning of each state is in `docs/operating-model/metric-lifecycle.md`, which calls itself "a LEVEL-5 descriptive document" (`bc-docs:docs/operating-model/metric-lifecycle.md:9 @ f4f5edd`).
- **No procedure chapter governs the lane.** The only onboarding chapter is `docs/onboarding/metric-workstream.md`, status `drafting`, authority `reference` (lines 5-6). It defers procedure to three chapters, `metric-contract-creation.md`, `metric-registration.md` and `mc-chain-integrity.md` (lines 15-18, 37), and all three exist only under `docs/archive/onboarding/` (command: `git ls-tree -r origin/main --name-only | grep -E "metric-contract-creation|metric-registration|mc-chain-integrity"` -> three paths, all under `docs/archive/onboarding/`).
- **bc-docs contradicts itself on the gate.** The companion says certification is a second panel whose output "the C8 gate requires for activation" (`metric-lifecycle.md:76-78`). ADR DEC-346ae7 says "the panel does not gate certification" (`bc-docs:docs/governance/adrs/ADR-346ae7.md:6 @ f4f5edd`). No chapter carries the later rule.
- **The project instructions point to wrong paths.** The re-entry index is at `docs/reference/technical-notes/implementation/mcf-re-entry-index.md` and the build plan at `docs/evidence/work-records/implementation/metric-context-framework-build-plan.md`, not under `docs/implementation/` (same `git ls-tree` command).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| Module | `src/registry/mcf/` (508 files); the one certificate writer `mcf-cert-writer.service.ts` (4,278 lines) | command: `git ls-tree -r origin/main --name-only -- src/registry/mcf \| wc -l` -> 508; `git show origin/main:src/registry/mcf/mcf-cert-writer.service.ts \| wc -l` -> 4278 |
| Module | `src/registry/metric-audit/` (67 files): certification runs, decision writer. Holds the certification code in use and the retired external exchange; to be split | same command on that path -> 67; `bc-core:src/registry/metric-audit/decision/certification-panel-decision.lane.ts:1-3 @ ec72438b` |
| Module | `src/common/formula/as-of-schedule-declaration.ts` (one file); imported by L6 and by the runtime assembler. Shared with RT, to be split | `bc-core:src/common/formula/as-of-schedule-declaration.ts:1-3 @ ec72438b`; command: `git grep -l "common/formula/as-of-schedule-declaration" origin/main -- src` -> `src/boundary/metric-spec-assembler.ts`, `src/boundary/metric-spec-loader.ts`, six `src/registry/mcf/` files |
| Route prefix | `mcf/intakes` (intake, list, reject) | `bc-core:src/registry/mcf/mcf-intake.controller.ts:36,45,247 @ ec72438b` |
| Route prefix | `mcf/panel-runs` (admission panel; drafting from an approved proposal) | `mcf-panel-run.controller.ts:39,52,109,216`; `mcf-materialization.controller.ts:28,32` |
| Route prefix | `mcf/authoring` (`validate-envelope`) | `mcf-authoring-validate.controller.ts:43,47` |
| Route prefix | `mcf/metric-contracts` (catalog reads, publication-eligibility checks, rename) | `mcf-publication-eligibility.controller.ts:29,68,118`; `mcf-metric-rename.controller.ts:53,57` |
| Route prefix | `mcf/metric-contract-versions`, 14 controllers: request-audit, certification runs and reproofs, panel-decision, admission-evidence, admit, supersede, retire, abandon, retire-rejected, retire-demoted-duplicate, restore, rebind, append-fixture, the retired `activate` | `mcf-request-audit.controller.ts:50,59`; `mcf-reproducibility-reproof.controller.ts:58,87,117,152`; `mcf-certification-panel-decision.controller.ts:37,41`; `mcf-admission-evidence.controller.ts:31,35`; `mcf-admit.controller.ts:43,50,100`; `mcf-mcv-supersede.controller.ts:58,65`; `mcf-mcv-retire.controller.ts:42,46`; `mcf-mcv-abandon.controller.ts:46,50`; `mcf-mcv-retire-rejected.controller.ts:52,59`; `mcf-mcv-retire-demoted-duplicate.controller.ts:54,58`; `mcf-mcv-restore.controller.ts:44,48`; `mcf-mcv-rebind.controller.ts:55,59`; `mcf-mcv-fixture-append/mcf-mcv-fixture-append.controller.ts:43,47`; `mcf-publication-activation.controller.ts:22,24` |
| Route prefix | `mcf` (`reclassification`, `classification-alignment`), `mcf/formula-explanation-bindings`, `mcf/audit-panel` (certification panel roster) | `mcf-mcv-reclassification.controller.ts:81,88,129`; `mcf-formula-binding-read.controller.ts:21`; `audit-panel/audit-panel-roster.controller.ts:26` |
| Route prefix | `mcf/metric-audit-reintake`, and `audit-claim-withdrawals` under `mcf/metric-audit-exchange` (withdrawing a certificate) | `directory-audit/metric-audit-reintake.controller.ts:101,218`; `directory-audit/audit-claim-withdrawal.controller.ts:30,34` |
| Route prefix | `registry/mcf/readiness-projection` (the certified count). Shared with L9, to be split | `readiness-projection.controller.ts:13`; `readiness-projection.service.ts:135-136` |
| Route prefix | `mcf/metric-contract-versions/:mcvUid/realization-projection`; `mcf/metric-audit-drive`; `mcf/seed-ledger`. Shared with L8, to be split | `mcf-realization-projection.controller.ts:22,26`; `mcf-metric-audit-drive.controller.ts:40,44`; `seed-metric-ledger.controller.ts:30` |
| Route prefix | `mcf/metric-contract-versions/:mcvUid/demoed-bridge`, `demoed-claim`. Shared with PV, to be split | `demoed-evidence-bridge.controller.ts:34,38,83` |
| Route prefix | `mcf/chain-audit`, `mcf/chain-enrichment`, `registry/mcf/chain-status`: L9, not L6 | `chain-audit/chain-audit.controller.ts:39`; `chain-enrichment/chain-enrichment.controller.ts:34`; `mcv-chain-status.controller.ts:13` |
| Route prefix | Retirement list: `mcf/metric-audit/feed`, `mcf/metric-audit/requests`, the rest of `mcf/metric-audit-exchange` (4 controllers), `mcf/arpi-materialization`, `mcf/ops`, `metric-catalog`, `metric-catalog/definitions`, `metric-reference` | `mcf-feed-import.controller.ts:36`; `mcf-feed-project.controller.ts:58`; `mcf-request-publish.controller.ts:36`; `directory-audit/metric-audit-exchange.controller.ts:29`; `directory-audit/metric-audit-rehearsal.controller.ts:24`; `src/registry/metric-audit/decision/checker-verdict-import.controller.ts:36`; `mcf-arpi-materialization.controller.ts:48`; `billing-volume-retry-unlock/billing-volume-retry-unlock.controller.ts:42`; `src/registry/metric-catalog.controller.ts:17`; `src/registry/metric-definition.controller.ts:26`; `src/registry/metric-reference.controller.ts:22` |
| Schema | `mcf`: 36 tables and the view `mcv_live`. L6 holds the contract, version, revision, variable, filter, computed-dimension, fixture, result, eligibility-result, package-snapshot, supersession, rejected-retirement, intake, panel-run, transcript, knowledge-profile and `certification_record` tables. `mcv_chain_status`, `chain_audit_evidence`, `chain_dependency_epoch`, `chain_enrichment_plan` are L9; the four `demoed_*` tables are PV; `seed_metric` is L8 | query (bc_platform_dev, 2026-11-13): `SELECT table_name, table_type FROM information_schema.tables WHERE table_schema='mcf' ORDER BY 1` -> 37 rows |
| Schema | `metric_audit` (39 tables). The lifecycle trigger calls into it, so it cannot be dropped whole. Shared with the retirement list, to be split | query (same day): `SELECT count(*) FROM information_schema.tables WHERE table_schema='metric_audit'` -> 39; `bc-db:baseline/candidate/0000_baseline.sql:8817,8836-8839 @ c6de1c4` |
| Database function | `mcf.fn_mcv_state_transition_check` and trigger `trg_mcf_mcv_state_transition` | `bc-db:baseline/candidate/0000_baseline.sql:8786-8921,13986 @ c6de1c4` |
| Screen (bc-admin) | Metric catalog and detail (request-audit, admit, supersede); candidate authoring (intake, panel, drafting) | `bc-admin:src/api/mcf-catalog.ts:194-242 @ d37b241`; `bc-admin:src/api/metricAuthoring.ts:64-112 @ d37b241`; `bc-admin:src/pages/MetricDetailPage.tsx:125 @ d37b241` |
| Command | `advance-materialized-mcv-cli.ts` (draft to awaiting certification); not an npm script | `bc-core:src/registry/mcf/advance-materialized-mcv-cli.ts:1-11 @ ec72438b`; command: `git show origin/main:package.json \| grep -n -i -E "mcf\|metric\|advance"` -> no match |
| DevHub tools | `devhub_metric_preflight`, `devhub_metric_drive`, `devhub_metric_workflow`; skill `metric-lifecycle` | `barecount-devhub:src/mcp-server.js:3100,3139,3239 @ 93cc1ea5`; `barecount-devhub:.claude/skills/metric-lifecycle/SKILL.md @ 93cc1ea5` |
| Document | the grammar's MCF section; `lifecycle-map.md`; `enforcement-surface-map.md`; `metric-lifecycle.md`; vocabulary groups 4 and 5 | cited above |

**The acts it performs.** Every act runs on the platform side, and every state change is written by `McfCertWriterService`, which writes a `mcf.certification_record` row first; the trigger then checks for that row.

| Act | Who (role) | Entry point as built | States | Writes |
|---|---|---|---|---|
| Intake | `mcf_author` | `POST /api/mcf/intakes` (`mcf-intake.controller.ts:45-46`) | none | `mcf.metric_authoring_intake_queue` |
| Admission panel (three AI roles judge the proposal) | `mcf_author` | `POST /api/mcf/panel-runs`, `…/with-maker` (`mcf-panel-run.controller.ts:52-53,109-110`) | none | `metric_authoring_panel_run`, `…_transcript` |
| Drafting from an approved proposal | `mcf_publisher` | `POST /api/mcf/panel-runs/:panelRunUid/materialize` (`mcf-materialization.controller.ts:32-33`; service `metric-authoring-materialization.service.ts:493`; writer `mcf-cert-writer.service.ts:1960`) | new row at `draft` | contract, version, variables, filters, fixture, `metric_create` certificate |
| Submit for review and approve | `mcf_publisher` | one call: `POST /api/mcf/metric-contracts/:metricContractUid/evaluate-pe-mc` (`mcf-publication-eligibility.controller.ts:118-119`; writer lines 2098, 2258) | `draft` to `review` to `approved` | eligibility results, `metric_approve` certificate, approval package snapshot (trigger lines 8862-8881) |
| Request certification | `mcf_publisher` | `POST …/:mcvUid/request-audit` (`mcf-request-audit.controller.ts:59-60`; writer line 2561) | `approved` to `audit_pending` | `audit_migrate` certificate (trigger lines 8884-8889) |
| Open a certification run | `mcf_publisher` | `POST …/:mcvUid/certification-runs` (`mcf-reproducibility-reproof.controller.ts:87-89`) | none | `metric_audit.audit_run` |
| Decision | `mcf_publisher` | `POST …/:mcvUid/certification-runs/:runUid/panel-decision` (`mcf-certification-panel-decision.controller.ts:41-43`). The verdict is "PASS iff green" on the chain judge (`certification-panel-decision.lane.ts:55-59`) | none | panel run, `metric_audit.decision` |
| Admission evidence | `mcf_publisher` | `POST …/:mcvUid/admission-evidence` (`mcf-admission-evidence.controller.ts:35-36`) | none | `metric_audit.admission_recomputation_evidence` |
| Admit (the version becomes certified) | `mcf_publisher` | `POST …/:mcvUid/admit` (`mcf-admit.controller.ts:50-51`; writer line 2839) | `audit_pending` to `active`; `is_current` set true (trigger lines 8816-8828) | `audit_admit` certificate |
| Invalidate | no route; a database cascade | `metric_audit.fn_c6_run_cascade` (query, same day: present). No TypeScript writes `audit_block` (command: `git grep -n "audit_block'" origin/main -- src` -> one snapshot file) | `active` or `audit_pending` to `audit_blocked` | `audit_block` certificate (trigger lines 8900-8906) |
| Withdraw a certificate (reintake) | `mcf_publisher` | `POST /api/mcf/metric-audit-reintake/batches/:id/members/:mcvUid/intake` (`metric-audit-reintake.controller.ts:218-219`); `POST /api/mcf/metric-audit-exchange/audit-claim-withdrawals` (`audit-claim-withdrawal.controller.ts:34-35`) | `active` to `audit_pending`; `is_current` cleared (trigger lines 8834-8855) | `audit_reintake` certificate |
| Supersede | `mcf_publisher` | `POST …/:metricContractVersionUid/supersede` (`mcf-mcv-supersede.controller.ts:65-66`) | `active` to `superseded`; needs a certified, current successor (trigger lines 8909-8917) | `metric_supersession`, `metric_supersede` certificate |
| Retire, abandon, retire a rejected version, retire a demoted duplicate | `mcf_publisher` | `…/retire` (`mcf-mcv-retire.controller.ts:46-47`), `…/abandon` (`mcf-mcv-abandon.controller.ts:50-51`), `…/retire-rejected` (`mcf-mcv-retire-rejected.controller.ts:59-60`), `…/retire-demoted-duplicate` (`mcf-mcv-retire-demoted-duplicate.controller.ts:58-59`) | no state change; the parent's `archived_at` is set | for the rejected exit, also `mcf.rejected_version_retirement` (writer lines 3940-3950) |

**What it receives and what it hands on.**

| Direction | Neighbour | What crosses, and where it is recorded | Defined in bc-docs | Built |
|---|---|---|---|---|
| In | L8, Metric Directory | the directory entry: `directory_member_uid` on the intake | Yes: ADR DEC-fa9424; vocabulary line 108 | Partly. The field is optional (`bc-core:src/registry/mcf/dto/mcf-dtos.ts:53 @ ec72438b`; `operator-direct-adapter.ts:48`) |
| In | L3, Vocabulary | concept identities on `mcf.metric_variable_binding`; the grain entity version | Yes: grammar | Yes: trigger `trg_mcv_grain_entity_version_guard` (query, same day: triggers on `mcf.metric_contract_version` -> seven names) |
| In | L5, Canonical Contracts, through L9 | the chain verdict, judged again inside the admit transaction (`mcf-cert-writer.service.ts:990`) | Partly. Vocabulary line 134 says the chain verdict "gates nothing" | Yes, and it does gate: the decision is "PASS iff green" |
| In | AI, AI services | the two panels | Yes: `metric-lifecycle.md:72-78` | Yes; the certification panel is now advisory in code |
| Out | L8 | realization of the directory entry by a version | Yes: vocabulary line 105 | Yes (owned by L8) |
| Out | RT, Runtime | the certified current version, read as `is_current = TRUE AND governance_state_code = 'active'` | No chapter says which version an act uses | Yes (`metric-spec-loader.ts:236-237`) |
| Out | L10 and DL | "released" and "metric available" | Yes: vocabulary line 129, "no record yet" | No |
| Out | PV | "validated against" a source | Yes: vocabulary line 128, "No record yet" | Partly (the `demoed_*` tables) |

**State today.**

- **Works.** One trigger guards the state field. Its allow-list has ten edges, counted in the baseline (lines 8801-8810) and in the live function (query, 2026-11-13: `SELECT substring(pg_get_functiondef(p.oid) from 'IF NOT \((.*?)\) THEN\s+RAISE EXCEPTION ''invalid mcf state') FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='mcf' AND p.proname='fn_mcv_state_transition_check'` -> the same ten lines). Nine can pass; the tenth, `audit_blocked` to `audit_pending`, is listed and then always refused (lines 8858-8859). Direct activation is closed in the route (HTTP 410, `mcf-publication-activation.controller.ts:24-38`) and in the service (`mcf-cert-writer.service.ts:2538-2543`).
- **Live counts** (query, bc_platform_dev, 2026-11-13: `SELECT governance_state_code, is_current, count(*) FROM mcf.metric_contract_version GROUP BY 1,2`): `active` 93, `approved` 55, `audit_pending` 281, `draft` 19, `review` 14, `superseded` 1; none `audit_blocked`. Contracts: 365 not archived, 98 archived. `mcf.mcv_live`: 82 rows. Of the versions holding `active` under a non-archived parent, 68 are certified (a standing `audit_admit` record) and 14 are "marked active without a certificate (defect)", each with an old `metric_transition` record; 11 more sit under archived parents. Of the 281 awaiting certification, 69 sit under archived parents.
- **Certificates by action** (same day, standing/archived): `metric_create` 471; `metric_transition` 343; `audit_reintake` 324/25; `metric_approve` 92; `audit_admit` 68/37; `audit_migrate` 37; `metric_supersede` 1; `metric_correction` 1; `audit_rerequest` 1.
- **Nothing has been certified since 2026-09-30.** The latest `audit_admit` record and the latest `metric_audit.decision` are both dated 2026-09-30 (query: `SELECT max(created_at) FROM mcf.certification_record WHERE action_code='audit_admit'` -> 2026-09-30 10:03:40; `SELECT max(created_at) FROM metric_audit.decision` -> 2026-09-30 10:03:40; 110 decisions, 82 runs). Drafting continued: the latest `metric_create` is 2026-11-10 and the latest approval 2026-11-04. The main document's sentence on this date, under "What the evidence says", is exact for certification only.
- **A version is not a version.** Every contract has exactly one version, and every version code is `v1` (query: `SELECT max(c) FROM (SELECT count(*) c FROM mcf.metric_contract_version GROUP BY metric_contract_uid) q` -> 1; `SELECT string_agg(DISTINCT version_code, ',') …` -> `v1`). A successor is a new contract; 72 contract names carry a `__` suffix.
- **Broken.** Both DevHub tools end at the retired route: `barecount-devhub:src/lib/metric-drive.js:370 @ 93cc1ea5` and `src/lib/metric-workflow.js:76-78` call `…/activate`. The restore act writes `superseded` to `active` (`mcf-cert-writer.service.ts:4098-4109`), an edge the trigger does not list.
- **Duplicated: four authoring doors besides the directory-anchored one.** (1) `POST /api/mcf/intakes` with no directory entry; 502 of 521 intake rows are `operator_direct`. (2) `POST /api/mcf/intakes/from-seed`, HTTP 410 (`mcf-intake.controller.ts:214-227`). (3) `POST /api/mcf/intakes/from-metric-definition` (line 139), which reads `metric.metric_definition`, 0 rows. (4) `POST /api/metric-catalog/definitions`, HTTP 410 (`src/registry/metric-definition.controller.ts:31-35`). There are also two ways from `approved` to awaiting certification: the route and `metric-audit-drive/members/:memberUid/drive-approved`.
- **Not built.** No composed command covers a certification run through admit. bc-admin calls none of those four routes (command: `git grep -n -c -E "evaluate-pe-mc|certification-runs|panel-decision|admission-evidence|retire-rejected|/abandon|/retire|reintake" origin/main -- src` in bc-admin -> one unrelated hit in `src/api/runtime.ts`). The records for "released" and "validated against" do not exist.

**Known defects and risks.**

1. The DevHub drive and the DevHub step guide both end at a route that returns 410 (`metric-drive.js:370`; `metric-workflow.js:78`).
2. The restore act targets an edge the trigger refuses (`mcf-cert-writer.service.ts:4098-4109` against baseline lines 8801-8810).
3. `audit_blocked` has no exit (baseline lines 8858-8859). No version is in that state today.
4. Fourteen versions are marked active without a certificate and remain selectable by the runtime rule (`metric-spec-loader.ts:236-237`; count above).
5. The directory-first rule of ADR DEC-fa9424 is not enforced at intake (`mcf-dtos.ts:53`).
6. The certification decision rests on the chain verdict (`certification-panel-decision.lane.ts:58-59`), while the vocabulary page says the chain verdict "gates nothing" (line 134).
7. The retired external-audit code is still routable, and the lifecycle trigger depends on `metric_audit` functions, so retirement needs a careful split (baseline lines 8817, 8836-8839).
8. The project instructions describe a legacy bridge with a `Sunset` header; the code removed it (`src/registry/metric-definition.controller.ts:4-11`).
9. `metric-workstream.md` names records that do not exist: `contract.metric_contract`, `contract.canonical_field`, `contract.business_field`, `cc_field_mapping`, `metric_binding` (lines 102-107; query, same day: `to_regclass` of each -> not present).

**Governing ADRs.** Status is read from each file under `bc-docs:docs/governance/adrs/ @ f4f5edd`.

| ADR | Plain summary | Status |
|---|---|---|
| DEC-c3e57f | Founds the Metric Context Framework | decided |
| DEC-542722 | Drafts are independent of the chain; one eligibility check couples them | decided |
| DEC-09f86b | Shape of the admission panel (maker, checker, judge) | implemented |
| DEC-327d4e | Identity hash includes computed dimensions | implemented |
| DEC-31c212 | Function and subfunction classification comes from the master list | implemented |
| DEC-c48b0f | Certification is a lifecycle act; a second panel certifies before a version reaches `active` | decided |
| DEC-793e13 | Retires the external audit exchange | decided |
| DEC-346ae7 | The panel is a flagger; the deterministic gate proves calculation | decided |
| DEC-b01ed4 | The deterministic gate must predict evaluation | decided |
| DEC-fa9424 | Authoring starts from a directory entry | implemented |
| DEC-21ca17 | Disposition of versions made active before certification existed | implemented |
| DEC-c897cd | The vocabulary page is the only authority for status words | decided |
| DEC-414ba2, DEC-545a4d | Exactness and reproducibility bases for certification | implemented |

Conflicts: DEC-c48b0f (panel 2 certifies) against DEC-346ae7 ("the panel does not gate certification"); DEC-346ae7 "amends" but does not supersede, and the Foundation grammar still says "`active` asserts panel certification". DEC-346ae7 also uses "VALIDATED" alone as a tier name (line 30), which the vocabulary page does not approve. DEC-fa9424 is marked implemented while its rule is not enforced. DEC-21ca17 is marked implemented while 14 versions remain.

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/reference/vocabulary.md` (groups 4, 5; section 3a) | keep nearly as is | Matches the records; correct the "gates nothing" sentence |
| `docs/reference/lifecycle-map.md`, `enforcement-surface-map.md` | keep nearly as is | Generated; the ten edges match the live function; regenerate |
| `docs/operating-model/metric-lifecycle.md` | rewrite | Sound on meaning; its two-panel gate predates DEC-346ae7 |
| `docs/foundation/the-contract-grammar.md` (MCF family) | rewrite (one sentence) | "asserts panel certification" needs the operator's decision |
| `docs/onboarding/metric-workstream.md` | rewrite | Of the eight steps of its work sequence (lines 100-126), three (2, 3, 5) direct the reader to records that do not exist, and step 4 names an engine class that is not in the code (command: `git grep -c "class MetricEvaluationEngine" origin/main -- src` -> no match). Four steps (1, 6, 7, 8) are discipline rules that still hold. None of the eight is an authoring step; the chapter holds no usable procedure for this lane |
| `docs/operating-model/metric-management-system.md` | history | Carries a standing freeze (line 732) that the program replaces |
| `docs/operating-model/mcf-legacy-bridge.md` | history | The bridge's write routes return 410 |
| `docs/archive/onboarding/metric-contract-creation.md`, `metric-registration.md` | history | Already archived; still cited as governing by the playbook |
| `docs/reference/technical-notes/implementation/mcf-re-entry-index.md` | rewrite into the guide | It is the real entry point and sits outside the chapter tree |

**Open questions for the operator.**

1. What certifies a metric: the deterministic gate alone (DEC-346ae7, as coded), or a panel verdict as well (DEC-c48b0f and Foundation's wording)?
2. Should a changed metric be a new version of the same contract, or stay a new contract with a new name, as every case is today?
3. For the 14 versions marked active without a certificate: finish the decided reintake route, retire them, or leave them until the deadline in DEC-c220e4?
4. Should intake refuse a proposal with no directory entry now, or keep the open door until L8 is locked?
5. Does `audit_blocked` get an exit, or is the state removed?
6. Is the external-audit code deleted in this lane's Modify step, or fenced until RT and EV are locked?

**What "locked" will mean here.**

1. One command takes a directory entry to a certified version, and its `check` verb reports every refusal of the admit gate before any write.
2. A CI guard fails on any new write to `governance_state_code` outside `McfCertWriterService`, and on any new `mcf/*` route outside the lane's declared list.
3. The 410 routes, the from-metric-definition intake, the restore act (or its missing edge) and the external-exchange routes are deleted or decided, and DevHub calls no retired route.
4. The query for versions marked active without a certificate returns zero.
5. The certification rule is one sentence in Foundation, the chapter and the code, and ADRs DEC-c48b0f and DEC-346ae7 are folded into it.
6. A fresh session, given only the chapter and the command, certifies one metric on the development host without help from memory.

### L7, Readers and connections

**What it is.** This lane authors the definitions that let the platform read a source system. A connector is the technical ability to reach one kind of source system over a declared protocol. A connection is one tenant's access to one source system through a connector. A reader is the admission definition for one business entity, and a reader flavor specialises it for one source system. Two bindings pin, for each source table, the admission contract version and the observation contract version a run uses. Without these records no source object can be admitted, so nothing later in the chain has data.

**How bc-docs defines it.**
- The defining chapter is `docs/operating-model/connectors-and-readers.md` (status `drafting`, authority `authoritative`; `bc-docs:docs/operating-model/connectors-and-readers.md:5-6 @ f4f5edd`). Its scope: "This chapter defines the platform's adapter inventory: Connector, Reader, Reader Flavor, Reader Binding, Reader Observation Binding, and Connection." (`:31`). It fixes the reader as a definition and not a machine: "This chapter defines the Reader as a **governed definition**, not as a runtime machine." (`:33`). The machine that executes it is called the Runner and belongs to runtime.
- The status words are in the vocabulary page: "**reader** | The admission definition for one business entity, reused by every tenant" and "**connection** | One tenant's access to one source system through a connector. Its credentials live outside our records" (`bc-docs:docs/reference/vocabulary.md:420-421 @ f4f5edd`). For readers and flavors "the field value `active` is said **\"in force\"**" (`:425`).
- The procedure is `docs/onboarding/reader-creation.md` (status `drafting`; `bc-docs:docs/onboarding/reader-creation.md:5 @ f4f5edd`).
- **Where bc-docs is silent.** No chapter gives a procedure for creating a connector or a connection, or for creating the tenant's source-object table (`fact.so_…`). The reader-creation chapter itself records that connection resolvability "is **not** checked by the activation resolver" (`reader-creation.md:227`).
- **Where bc-docs is stale.** `docs/development/metric-readiness-toolkit.md:170,186` still presents `POST /api/schema-provisioner/onboard-connector` as the way to enable a whole connector for a tenant. That route returns nothing today (see State today).
- **A column that says the wrong thing, documented as such.** The chapter states that `reader_binding.source_contract_id` "carries an **admission-contract id** (historical column name)" (`connectors-and-readers.md:46`).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| module | `src/registry/readers` (reader, flavor, bindings; governed authoring) | `bc-core:src/registry/readers/reader-authoring.controller.ts:40 @ ec72438b` |
| module | `src/registry/connections` (connector, connection, credential resolver) | `bc-core:src/registry/connections/connection.controller.ts:13`; `connector.controller.ts:23 @ ec72438b` |
| module | `src/boundary/reader-runtime` (executor registry, protocol executors, run service) — shared with RT, to be split: the registry and executors are L7, the run is RT | `bc-core:src/boundary/reader-runtime/executor-registry.service.ts:16 @ ec72438b` |
| route prefix | `reader-authoring` (7 POST routes: create reader, create flavor, activate flavor, archive flavor, archive reader, observation binding, admission binding) | `bc-core:src/registry/readers/reader-authoring.controller.ts:45,60,73,95,104,113,121 @ ec72438b` |
| route prefix | `readers` (reads; reader-level bind, unbind, repoint; four closed legacy writes) | `bc-core:src/registry/readers/reader.controller.ts:36,43,51,141,171,199,217,233 @ ec72438b` |
| route prefix | `connectors` (create, list, governance, usage, read, update, delete) | `bc-core:src/registry/connections/connector.controller.ts:28-96 @ ec72438b` |
| route prefix | `connections` (create, record owning tenant, read, update, delete, checks, health) | `bc-core:src/registry/connections/connection.controller.ts:20-149 @ ec72438b` |
| route prefix | `t/connections` (a tenant creates and checks its own connection); `t/readers-catalog`, `t/connectors-catalog` (tenant reads) — shared with TS, to be split | `bc-core:src/tenant-views/tenant-views.controller.ts:224,302,335,339 @ ec72438b` |
| route prefix | `t/readers` (`:readerId/execute`, run reconcile, release held tail) — shared with RT, to be split | `bc-core:src/boundary/reader-runtime/reader-execution.controller.ts:32,37,65,87 @ ec72438b` |
| route prefix | `admission-runs`, `boundaries`, `evaluation`, `metric-evaluation`, `actions` (platform reads declared in the reader controller file) — shared with RT, to be split | `bc-core:src/registry/readers/reader.controller.ts:282,369,382,395,408 @ ec72438b` |
| route prefix | `tenant-bindings` (a tenant's source binding, declared in the reader controller file) — shared with L10, to be split | `bc-core:src/registry/readers/reader.controller.ts:421 @ ec72438b` |
| route | `POST schema-provisioner/onboard-connector` (forward request for source-object tables) — shared with L10, to be split | `bc-core:src/schema-provisioner/connector-onboarding.controller.ts:50 @ ec72438b` |
| tables | `runtime.connector`, `connector_protocol`, `connector_provenance`, `connection`, `connection_config`, `connection_check`, `connection_tenant_assignment_event`, `reader`, `reader_flavor`, `reader_binding`, `reader_observation_binding` | query (bc_platform_dev, 2026-11-13): `SELECT table_name FROM information_schema.tables WHERE table_schema='runtime'` -> 17 tables, these 11 among them |
| tables | `runtime.admission_run`, `admission_run_context`, `admission_run_disposition` — shared with RT, to be split | same query |
| table | `admin.connection` in every tenant database (a second connection table; no non-test reference in `src`) — retirement candidate | `bc-core:src/registry/seed/tenant-skeleton/0000_tenant_skeleton.sql:144 @ ec72438b`; command: `git grep -c "admin\.connection\b" origin/main -- src ':!*.spec.ts'` -> no match |
| migration | `0021_connection_owning_tenant.sql` (the write-once owner of a connection) | `bc-db:migrations/0021_connection_owning_tenant.sql @ c6de1c4` |
| screens | bc-admin `registry/connectors` (list, new, detail), `registry/connections` (list, detail), `registry/readers` (list, new, detail) | `bc-admin:src/components/AppRouter.tsx:186-196 @ d37b241` |
| script | `scripts/seed-reader-bindings.mjs` (inserts into the reader tables directly) | command: `git grep -l -i "INSERT INTO runtime\.(reader|connection|connector)" origin/main -- scripts` -> this one file |
| documents | `operating-model/connectors-and-readers.md`; `onboarding/reader-creation.md` | cited above |

Corrections to the lane taxonomy's row:
- The taxonomy gives `connections` to both L7 and L10 (`barecount-devhub:artifacts/lanes/LOCKED-LANE-TAXONOMY-2026-08-24.md:36,39 @ 93cc1ea5`). The code supports L7: the controller is platform-only and sits in `src/registry/connections`, the table is the platform's `runtime.connection`, and the connection is owned by a tenant through a recorded owner, not through the tenant database. L10 should keep only the act of creating a tenant's connection during onboarding.
- The L7 kit lists `devhub_register_source_stack` as a reader tool (`artifacts/lanes/L7-reader/README.md:16`). The tool calls `/api/source-catalog/stacks` and authors source and admission contracts (`barecount-devhub:src/mcp-server.js:3770-3781 @ 93cc1ea5`). It belongs to L2. L7 has no DevHub tool.

**The acts it performs.**

| Act | Who | Entry point as built | States and writes |
|---|---|---|---|
| Register a connector | platform admin or operator | `POST /api/connectors` (`connector.controller.ts:28`) | `runtime.connector.status_code`, default `draft` (`connector.repository.ts:117`); values `draft`, `available`, `deprecated`, `retired` (`connector.controller.ts:39`) |
| Create a connection | platform admin or operator; or a tenant user | `POST /api/connections`, then `POST /api/connections/:id/owning-tenant` (`connection.controller.ts:20,31`); or `POST /api/t/connections`, owned at creation (`tenant-views.controller.ts:339-354`) | `runtime.connection`, `connection_config`; one row in `connection_tenant_assignment_event` |
| Check a connection | operator or tenant | `POST /api/connections/:id/checks`; `POST /api/t/connections/:id/checks` | `connection_check`; sets `connection_status` to `connected` or `disconnected` unless it is `paused` or `disabled` (`connection.service.ts:247-248`) |
| Create a reader | platform admin or operator | `POST /api/reader-authoring/readers` (`reader-authoring.controller.ts:45`) | `runtime.reader`, `draft`; one non-archived reader per entity |
| Create a flavor | same | `POST /api/reader-authoring/flavors` (`:60`); also written by the observation-chain authoring service (`bc-core:src/registry/substrate/author-observation-chain.service.ts:329 @ ec72438b`) | `runtime.reader_flavor`, `draft` |
| Bind an observation contract | same | `POST /api/reader-authoring/observation-bindings` (`:113`) | `runtime.reader_observation_binding` |
| Bind an admission contract | same | `POST /api/reader-authoring/admission-bindings` (`:121`); reader-level fallback `POST /api/readers/:readerId/bindings` (`reader.controller.ts:199`) | `runtime.reader_binding`; the admission contract id goes into `source_contract_id` (`reader-authoring.service.ts:402-405`) |
| Bring a flavor into force | same | `POST /api/reader-authoring/flavors/:flavorId/activate` (`:73`) | `draft` to `active`; refused with the named breaks if the contract chain does not resolve |
| Repoint or unbind a binding | operator only | `POST /api/readers/:readerId/bindings/repoint`, `…/unbind` (`reader.controller.ts:217,233`) | closes the binding (`unbound_at`) and, for repoint, inserts the successor pins |
| Archive a flavor or reader | platform admin or operator | `POST /api/reader-authoring/flavors/:flavorId/archive`, `…/readers/:readerId/archive` (`:95,104`) | `archived_at` |

There is no act that brings a reader itself into force. The chapter says so: "There is **no Reader-activation endpoint**" (`reader-creation.md:172`).

**What it receives and what it hands on.**

| Direction | Neighbour | What passes | In which record | Defined in bc-docs | Built |
|---|---|---|---|---|---|
| in | L3, Vocabulary | the entity a reader admits | `runtime.reader.admitted_entity_id` | yes (`reader-creation.md:90`) | yes |
| in | L2, Source and Admission Contracts | the admission contract version per source table | `reader_binding.(source_contract_id, version_code)` | yes (`connectors-and-readers.md:46`) | yes; the column has no foreign key (query: `SELECT conname FROM pg_constraint WHERE conrelid='runtime.reader_binding'::regclass AND contype='f'` -> only `flavor_id` and `reader_id`) |
| in | L4, Observation Contracts | the observation contract version per source table | `reader_observation_binding` | yes (`:47`) | yes |
| in | L1, Source Catalog | the source system version | `connection.source_version_id`, `reader_flavor.source_version_id` | not stated | yes (foreign keys, same query on those tables) |
| out | RT, Runtime | the resolved chain for one run: flavor, connection, executor, both pins | read at `bc-core:src/boundary/reader-runtime/reader-runtime.service.ts:268-276 @ ec72438b` | yes ("Binding resolution", `connectors-and-readers.md:54`) | yes |
| out | L10, Tenant onboarding | which source-object tables a tenant needs | `tenant.tenant_binding`, then `schema_provisioner.provisioning_command` | no chapter | route exists and returns nothing (below) |
| out | OP, Operations | where the secret is kept | `connection_config.authentication_json.credentialRef` | ADR DEC-ecd55c says AWS Secrets Manager | code resolves `env:` references only |

**State today.**

*Works.* Governed authoring of readers, flavors and both bindings is mounted, and the four ungoverned legacy writes refuse with `ForbiddenException` (`bc-core:src/registry/readers/reader.service.ts:103-107,214-218,239-243,630-637 @ ec72438b`). A reader run resolves its executor through the connection's connector (`reader-runtime.service.ts:268-276`).

*Broken: the forward request for source-object tables matches nothing.* `POST /schema-provisioner/onboard-connector` walks connector, then readers, then source contracts (`bc-core:src/schema-provisioner/connector-chain-walk.service.ts:84-102 @ ec72438b`). The second hop is `findSourceContractsForReader`, which joins `reader_binding.source_contract_id` to `contract.source_contract.source_contract_id` (`bc-core:src/schema-provisioner/schema-provisioner.repository.ts:458-478`, the join at `:469`). That column holds admission contract ids. query (bc_platform_dev, 2026-11-13): `SELECT count(*) FILTER (WHERE EXISTS (SELECT 1 FROM contract.admission_contract a WHERE a.admission_contract_id=rb.source_contract_id)), count(*) FILTER (WHERE EXISTS (SELECT 1 FROM contract.source_contract s WHERE s.source_contract_id=rb.source_contract_id)) FROM runtime.reader_binding rb WHERE unbound_at IS NULL` -> 16 match an admission contract, 0 match a source contract. So the walk returns an empty list at `:97-101`, records no source binding and requests no table. Its fourth hop would also fail: it finds canonical contracts through `contract.canonical_mapping` (`schema-provisioner.repository.ts:536-545`), which holds 0 rows (query: `SELECT count(*) FROM contract.canonical_mapping` -> 0).

*What is used instead.* Every source-family provisioning command was requested by the metric route. query: `SELECT requested_by, tenant_key, fact_table_name, <latest to_state> FROM schema_provisioner.provisioning_command WHERE contract_family_code='source'` -> 4 rows, all `metric-onboarding`, all `provisioned`; two (kaveri) carry the placeholder name `unresolved:source:<uuid>:v1.0.0`, two (kaveridemo, kaveridemo2) carry `fact.so_sc_929yc_v1_0_0`. Bringing a source contract into force requests no table: only canonical and metric contracts do (`bc-core:src/registry/contracts/contract.service.ts:1035-1036,1054 @ ec72438b`). A missing table is found only when the first batch is written (`bc-core:src/schema-provisioner/typed-fact-writer.service.ts:210`).

*Live counts* (bc_platform_dev, 2026-11-13; `SELECT status, count(*) … GROUP BY status` on each table):

| Record | Counts |
|---|---|
| `runtime.connector` by `status_code` | available 3 (`odata-v2`, `odoo-jsonrpc`, `odoo-ent-v19`; only `odoo-ent-v19` is referenced by flavors, 8) |
| `runtime.connector_protocol` | 3 rows; executor classes `ODataV2ProtocolReader`, `OdooJsonRpcProtocolReader` |
| `runtime.connection` by `connection_status` | connected 1, draft 1, disabled 1; all three `odoo`, all owned by a tenant, all `development` |
| `runtime.reader` by `status_code` | draft 9 (1 of them archived) |
| `runtime.reader_flavor` by `status_code` | active (in force) 10, deprecated 1; 3 flavors in force have no `connection_id`; 0 carry the retired `observation_contract_id` |
| `runtime.reader_binding` | 19 rows, 16 open (13 `dev`, 3 `production`), none reader-level |
| `runtime.reader_observation_binding` | 21 rows, 16 open (13 `dev`, 3 `production`) |
| `runtime.admission_run` by `run_status` | completed 17, failed 5 (2026-09-07 to 2026-11-05) |
| `runtime.connection_check` | 2, both `success` |

*Duplicated.*
- Create a reader: three routes, one open. `POST /reader-authoring/readers` works; `POST /readers` and `POST /readers/create-from-oc` are mounted and refuse (`reader.controller.ts:43,51`).
- Create a flavor: two open writers (`reader-authoring/flavors`; the observation-chain authoring service) and one closed route (`POST /readers/:id/flavors`).
- Bind an admission contract: two open routes with different field names (`reader-creation.md:163`), plus repoint, plus the seed script.
- Create a connection: two routes (`connections`, `t/connections`), and a second, unused connection table in each tenant database.
- The bc-admin "new reader" screen still posts to the closed `create-from-oc` route (`bc-admin:src/api/readers.ts:335-340 @ d37b241`). bc-admin makes no call to `reader-authoring` (command: `git grep -c "reader-authoring" origin/main -- src` in bc-admin -> no match). So the console cannot create a reader.

*Hard-coded.*
- The executor list is registered in code at start-up: six protocol classes and five legacy flavor-name keys (`bc-core:src/boundary/boundary.module.ts:185-198 @ ec72438b`). Adding a protocol is a code change. Only two of the eleven keys are named by a live connector protocol.
- If a connector names no executor class, the lookup uses the flavor's name (`reader-runtime.service.ts:270`).
- Credentials: `credential-resolver.service.ts` supports `none`, `api_key`, `basic`, `oauth2_password` (`:84-93`), reads `env:` references from the environment of the served application (`:125-127`), and throws "not yet implemented" for `ssm:` (`:145-150`). All live connections use `basic` with `env:` references (query: `SELECT string_agg(DISTINCT authentication_json->>'method', ','), bool_and((authentication_json->>'credentialRef') LIKE 'env:%') FROM runtime.connection_config` -> `basic`, true).

*Not built.* A governed bulk route for readers (`reader-creation.md:263`); retirement of the flavor's own connector and connection columns (`connectors-and-readers.md:52`); a state for a reader other than `draft`; a secret store reference other than `env:`.

**Known defects and risks.**
1. The forward request for source-object tables is dead, as shown above (`schema-provisioner.repository.ts:469`). A source can be read only after a metric has pulled its table.
2. `reader_binding.source_contract_id` holds admission contract ids, has no foreign key, and is read as a source contract id by at least one caller (same citation; `reader-authoring.service.ts:402-405`).
3. Credentials are resolved after the run rows are opened (`reader-runtime.service.ts:318-326`), so a missing environment variable leaves a failed run instead of a refusal before the run.
4. An unsupported authentication method logs a warning and returns empty credentials (`credential-resolver.service.ts:95-100`). It should refuse.
5. Flavor activation does not check that a connection exists (`reader-creation.md:227`); three flavors in force have none (query above).
6. `runtime.connection.connection_status` has no CHECK rule (query: `SELECT count(*) FROM pg_constraint WHERE conrelid='runtime.connection'::regclass AND contype='c'` -> 0); one live row is `draft`, a value the code never writes (`vocabulary.md:472`).
7. Every reader says `draft` while its flavors are in force (`vocabulary.md:473`; counts above).
8. Three spellings of the environment are in use: `dev` and `production` on the reader bindings, `development` on connections, and `apex`, `dev`, `development` on `tenant.tenant_binding` (query: `SELECT environment_code, count(*) FROM tenant.tenant_binding GROUP BY 1` -> apex 4, dev 13, development 11). The forward walk filters bindings by this value (`schema-provisioner.repository.ts:473`).
9. The console's reader screen calls a closed route (`bc-admin:src/api/readers.ts:340`).
10. Two kaveri provisioning commands carry a placeholder table name (query above).

**Governing ADRs.**

| ADR | Plain summary | Status in the file |
|---|---|---|
| DEC-0d5b39 | One reader per registry entity; a flavor is (source system, scenario); the connector is reached through the connection; the reader is a definition and the Runner executes it | decided |
| DEC-17112b | The governed reader-authoring surface: four layers, per-entity observation binding, the activation gate | decided; its grouping rule is amended by DEC-0d5b39 |
| DEC-f656a6 | Protocol readers are universal; a connector is reclassified as a protocol capability | implemented |
| DEC-f0866a | Connector ecosystem: transport abstraction, dynamic registry, test harness, scaffold command | implemented |
| DEC-ecd55c | Connection configuration in the platform's `runtime.connection`; credentials in AWS Secrets Manager by reference | implemented |
| DEC-81cd26 | Connections are platform-scoped | implemented |
| DEC-12558e | Odoo 19 is a JSON-RPC connector with its own executor | implemented |
| DEC-95687d | Typed tenant tables; connector onboarding as the primary trigger for creating them | implemented |

Statuses read from `bc-docs:docs/governance/adrs/ADR-<uid>.md:5 @ f4f5edd`.

Conflicts:
- DEC-95687d is marked `implemented`, and its primary trigger returns nothing today.
- DEC-f0866a is marked `implemented` and names a dynamic registry; the registry is filled by eleven literal lines of code.
- DEC-ecd55c names AWS Secrets Manager; the resolver reads only environment variables, and the tenant skeleton still creates `admin.connection`, which DEC-81cd26 moved to the platform.
- DEC-0d5b39 decides that the flavor's connector edge is retired; the columns are still written (`connectors-and-readers.md:52`).

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/operating-model/connectors-and-readers.md` | keep nearly as is | Matches the code read here, including the column mismatch and the unfinished retirement; add connector and connection acts and the credential rule |
| `docs/onboarding/reader-creation.md` | keep nearly as is | All 5 of its 5 steps name routes that are mounted today (checked route by route against `reader-authoring.controller.ts:45,60,73,113,121` and `reader.controller.ts:199`; not executed, this reading is read-only). It lacks connector, connection and source-object table steps |
| `docs/development/metric-readiness-toolkit.md` (lines 170, 186) | rewrite | Recommends the dead forward route |
| `docs/reference/data-dictionary/runtime.md` | rewrite | To be regenerated from the live schema (not re-checked line by line) |

**Open questions for the operator.**
1. Should a source-object table be requested by a forward act of this lane (repair `onboard-connector`), or only when a metric is enabled for a tenant (delete `onboard-connector`)?
2. Is the secret store for the program the environment of the served application, filled from AWS Secrets Manager at start, or a direct Secrets Manager reference per connection as DEC-ecd55c states?
3. Should a reader have a state of its own, or should the reader's `status_code` be retired and its standing read from its flavors?
4. Is a new protocol added by code only (keep the literal list, and say so) or by registration (build the dynamic registry of DEC-f0866a)?
5. Which single spelling of the environment is kept: `dev` or `development`?

**What "locked" will mean here.**
1. Each act in the table above has exactly one mounted write route; the closed legacy routes, the seed script and the tenant `admin.connection` table are deleted, and a CI guard fails on a new writer of the eleven tables.
2. `reader_binding` names an admission contract in a column with that name and a foreign key, and no code joins it to a source contract.
3. A fresh session, using only the chapter and the commands, creates a connection, a reader, a flavor and both bindings for one source table, obtains the tenant's source-object table by the one decided route, and completes a run with admitted rows.
4. A flavor cannot be brought into force without a connection, and a run refuses before any run row is written when its credential reference cannot be resolved or its method is unsupported.
5. `connection_status` and the environment code each have one checked list of values, and no live row is outside it.
6. The bc-admin reader, connector and connection screens call only the governed routes.

### L8, Metric Directory

**What it is.** The Metric Directory is the governed list of the metrics that should exist. Each entry (a "member") states one intended metric: what it measures, at which metric grain, and why. A member is **registered** when it has a row in the directory, and **realized** when a specific metric contract version has been asserted, by a governed act, to fulfil it. The platform needs the directory because the acts that withdraw or re-certify a metric find it by its directory entry, and because it is the list that authoring starts from.

**How bc-docs defines it.**
- The chapter is `docs/operating-model/metric-directory.md`. It says: "The **Metric Directory** is a governed **dictionary / blueprint** that answers one question: *\"What metrics should exist, organized by value, and how is each one specified?\"*" (`bc-docs:docs/operating-model/metric-directory.md:30 @ f4f5edd`).
- Its boundary rule: "The directory references the contract for realized semantics; it never restates, re-derives, or competes with them." (`bc-docs:docs/operating-model/metric-directory.md:42 @ f4f5edd`).
- The status words are in the vocabulary page: "**registered** | The metric has an identity in the Metric Directory: what should exist, and why | a row in `metric_directory.member`" (`bc-docs:docs/reference/vocabulary.md:104 @ f4f5edd`), and "realized" is true when the entry's current member version has an operative row in `metric_directory.realization_operative` (`bc-docs:docs/reference/vocabulary.md:105 @ f4f5edd`).
- **The chapter is stale on what is built.** Its front matter says "ratification: operator-aligned in design session 2026-07-08; no ADR filed yet" and its text says the doctrine is "not yet reflected in any substrate" (`bc-docs:docs/operating-model/metric-directory.md:18,38 @ f4f5edd`). ADR DEC-b5c7ff is decided, and the live database holds 29 directory tables (see State today). Its section 11 lists as "parked" the persistence, the realization link and lifecycle ownership, all of which are built (`bc-docs:docs/operating-model/metric-directory.md:145 @ f4f5edd`).
- **bc-docs contradicts itself on the catalog.** `docs/operating-model/metric-catalog.md` names `metric.metric_definition` and `metric.metric_contract` as the stores and gives a `seed`, `register`, `review`, `approve`, `active`, `superseded` lifecycle (`bc-docs:docs/operating-model/metric-catalog.md:40-41,138-143 @ f4f5edd`). `metric.metric_definition` is empty today and `metric.metric_contract` does not exist (queries below).
- **No procedure chapter governs the lane.** The lane kit names `docs/onboarding/metric-workstream.md` (`barecount-devhub:artifacts/lanes/L8-metric-registration-directory/README.md:6 @ 93cc1ea5`). That chapter calls itself "reference guidance" and defers "substantive procedure" to three procedures (`bc-docs:docs/onboarding/metric-workstream.md:29,41 @ f4f5edd`); all three are in the archive (`command: git ls-tree -r origin/main --name-only | grep metric-registration -> docs/archive/onboarding/metric-registration.md`, same for `metric-contract-creation.md` and `mc-chain-integrity.md`). The chapter does not contain the word "directory" as a step.

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| module | `src/registry/metric-directory/` (controller, service, `realization.service.ts`, `member-versioning.service.ts`, two projection services) | `command: git ls-tree -r origin/main --name-only -- src/registry/metric-directory @ ec72438b -> 21 non-test files` |
| route prefix | `metric-directory` (39 routes: 21 writes, 18 reads; roles `operator`, `platform_admin`) | `bc-core:src/registry/metric-directory/metric-directory.controller.ts:126-699 @ ec72438b` |
| route prefix | `seed-catalog/metrics` (4 reads over `mcf.seed_metric`) | `bc-core:src/registry/source-catalog/seed-metrics.controller.ts:18-69 @ ec72438b`; shared with L1 by file location, to be split |
| route prefix | `registry/mcf/readiness-projection` (1 read; "never verdicts, never gates") | `bc-core:src/registry/mcf/readiness-projection.controller.ts:4,13 @ ec72438b`; shared with L6, to be split |
| database schema | `metric_directory`: 29 tables and 11 views | `query (bc_platform_dev, 2026-11-13): SELECT table_type, count(*) FROM information_schema.tables WHERE table_schema='metric_directory' GROUP BY 1 -> BASE TABLE 29, VIEW 11` |
| database table | `mcf.seed_metric` (the seed reservoir) | `bc-docs:docs/reference/vocabulary.md:82 @ f4f5edd` |
| scripts | `a2-0-apply-cli.ts`, `a2-backfill/a2-runner-cli.ts`, `metric-directory-backfill-cli.ts` (one-off backfills inside the module) | same `git ls-tree` as above |
| schema source | bc-core `docker/redesign/27-`, `30-`, `37-metric-directory-*.sql` (frozen); bc-db migrations 0033, 0035, 0036 | `command: git grep -l "metric_directory\." origin/main -- migrations @ c6de1c4` |
| screens | bc-admin `/directory`, `/directory/families/new`, `/directory/families/:familyId`, `/directory/families/:familyId/members/new`, `/directory/groups/new`, `/directory/groups/:groupId/members/new`, `/directory/members/:memberUid`, `/directory/members/:memberUid/author` | `bc-admin:src/components/AppRouter.tsx:229-236 @ d37b241` |
| DevHub tools | `devhub_metric_drive` (reads `GET /api/metric-directory/members/:uid/envelope`), `devhub_readiness_dial` | `barecount-devhub:src/lib/metric-drive.js:430 @ 93cc1ea5`; `barecount-devhub:src/mcp-server.js:3070-3075 @ 93cc1ea5` |
| documents | `operating-model/metric-directory.md`; vocabulary groups 1 to 3 | cited above |
| retirement list, still present | route prefixes `metric-catalog`, `metric-catalog/definitions`, `metric-reference`; schema `metric` (7 tables) | `bc-core:src/registry/metric-catalog.controller.ts:17`, `metric-definition.controller.ts:26`, `metric-reference.controller.ts:22 @ ec72438b` |

The taxonomy's ownership row says "`metric_directory.*` (all ~23)" (`barecount-devhub:artifacts/lanes/LOCKED-LANE-TAXONOMY-2026-08-24.md:37 @ 93cc1ea5`). Today it is 29 tables. The taxonomy also names a controller `metric-definitions`; no such prefix exists, the prefix is `metric-catalog/definitions`.

**The acts it performs.** All are performed by a platform operator through `metric-directory` routes (`bc-core:src/registry/metric-directory/metric-directory.controller.ts @ ec72438b`).

| Act | Entry point | Writes |
|---|---|---|
| Create a family; edit it; set its industries | `POST families` (134), `PATCH families/:familyId` (155), `PUT families/:familyId/industries` (177) | `family`, `family_industry` |
| Create a group; set its temporal anchor and gate | `POST groups` (189), `PATCH groups/:groupId/temporal-anchor` (213), `PATCH …/temporal-gate` (230) | `group` |
| Register a member (two routes) | `POST members` (249), `POST members/from-spec` (279) | `member`; intent state `planned` or `blocked`, decided by a feasibility check |
| Author a version of a member, family or group | `POST members/:memberUid/version` (534), `POST families/:familyId/version` (550), `POST groups/:groupId/version` (560) | `member_version`, `family_version`, `group_version` (immutable) |
| Realize | `PATCH members/:memberUid/realize` (570); needs the exact version, an authority reference and a rationale | an `assert` row in `realization_event`; database triggers check the member version is current, the metric version is `approved` or `active`, and the grain matches (`bc-core:src/registry/metric-directory/realization.service.ts:9-12 @ ec72438b`) |
| Supersede a realization | `PATCH members/:memberUid/realization/supersede` (595) | a new `assert` that cites the head |
| Revoke a realization | `PATCH members/:memberUid/realization/revoke` (616) | a `revoke` row |
| Archive an unrealized member | `PATCH members/:memberUid/archive` (659) | `member.archived_at` |
| Record knowledge, a decision, a derivation, a regroup, a feasibility re-check | lines 448, 462, 511, 521, 629, 652 | `member_knowledge`, `directory_decision`, `member`, `member_feasibility_*` |
| Reject an entry | **not built** in bc-core (`command: git grep -n -E "85fd8d|rejectMember|members/:memberUid/reject" origin/main -- src @ ec72438b -> no match`) | none |

**What it receives and what it hands on.**

| Hand-off | What passes | Defined in bc-docs | Built |
|---|---|---|---|
| In, from L3, Vocabulary | concept and entity identities for a member's measure and grain (`member.measure_concept_id`, `group.grain_entity_id`) | yes, the "feasibility edge" (`bc-docs:docs/operating-model/metric-directory.md:114,139 @ f4f5edd`) | yes |
| In, from seeds | seed rows as evidence only | yes ("Seeds are *evidence and coverage*, never the worklist authority", line 113) | yes |
| Out, to L6, Metric Contracts and certification | `directory_member_uid` on the authoring intake, `POST /mcf/intakes` | ADR only (DEC-fa9424) | yes, but optional: `directory_member_uid: submission.directory_member_uid ?? null` (`bc-core:src/registry/mcf/operator-direct-adapter.ts:48 @ ec72438b`) |
| In, from L6 | the metric contract version uid, by the realize act | vocabulary (`vocabulary.md:105`) | yes |
| Out, to L6 certification acts | the directory identity that reintake and retirement look up | vocabulary (`vocabulary.md:108`) | yes |
| Out, to DL, Delivery to a tenant (function and subfunction for a package) | named only in the main document, under "The rulings": ruling T1 (decided) binds metrics to packages, and open ruling T6 asks whether a package names its metrics by a list or by function and subfunction | neither | neither |

**State today.**
- **Works.** Family, group and member creation, member versions and realization are built and have data. `query (bc_platform_dev, 2026-11-13): counts over metric_directory -> family 49; group 143; member 435 (399 not archived, 36 archived); member_version 276; realization_event assert 282, revoke 0; realization_operative 265; directory_decision 135`.
- **Every member is `planned`.** `query (bc_platform_dev, 2026-11-13): SELECT intent_state_code, count(*) FROM metric_directory.member GROUP BY 1 -> planned 435`. No member is blocked.
- **159 members have no member version,** so they cannot be realized: `query (bc_platform_dev, 2026-11-13): SELECT count(*) FROM metric_directory.member m WHERE NOT EXISTS (SELECT 1 FROM metric_directory.member_version v WHERE v.member_uid=m.member_uid) -> 159`.
- **15 of the 82 versions in `mcf.mcv_live` have no operative realization:** `query (bc_platform_dev, 2026-11-13): SELECT count(*) FROM mcf.mcv_live lv WHERE NOT EXISTS (SELECT 1 FROM metric_directory.realization_operative o WHERE o.metric_contract_version_uid=lv.metric_contract_version_uid) -> 15` (67 have one).
- **Seeds.** `query (bc_platform_dev, 2026-11-13): SELECT status_code, count(*) FROM mcf.seed_metric GROUP BY 1 -> candidate 12430; superseded 52; in_review 13; deferred 6; published 6`. The value `superseded` is not in the vocabulary's list of seed statuses (`vocabulary.md:92-94`).
- **Duplicated.** Three routes create an authoring intake: `POST mcf/intakes` (live, member optional), `POST mcf/intakes/from-metric-definition` (live, reads the empty legacy table), `POST mcf/intakes/from-seed` (refuses with HTTP 410) (`bc-core:src/registry/mcf/mcf-intake.controller.ts:45,139,214-228 @ ec72438b`). Two routes register a member (above).
- **The legacy metric surface is still mounted and still read.** `metric-catalog` has 6 reads; `metric-catalog/definitions` has 2 retired writes and 17 routes that still answer, including `PATCH :id` and five gate writes; `metric-reference` has 4 reads and 3 retired writes (`bc-core:src/registry/metric-definition.controller.ts:31-186`, `metric-reference.controller.ts:26-121 @ ec72438b`). bc-admin still calls all three (`bc-admin:src/api/metric-catalog.ts:111-161`, `src/api/metric-definitions.ts:207-378`, `src/api/metric-reference.ts:98-184 @ d37b241`). `metric.metric_definition` holds 0 rows (`query (bc_platform_dev, 2026-11-13): SELECT count(*) FROM metric.metric_definition -> 0`).
- **The `metric` schema is not all dead.** It has 7 tables; `metric.mls_state_event` holds 3330 rows and `metric.readiness_ledger` 926 (`query (bc_platform_dev, 2026-11-13): counts -> mls_state 7; mls_state_event 3330; readiness_ledger 926`), and a registered probe reports the chain verdict into the MLS read model (`bc-core:src/mls/probes/chain-status-mls-probe.service.ts:1-19 @ ec72438b`).
- **Not applied.** bc-db migration `0035_directory_entry_rejected_state.sql` is on main and has no apply record; the live rule still allows only `planned` and `blocked` (`query (bc_platform_dev, 2026-11-13): SELECT migration_name FROM infrastructure.schema_migration_event WHERE migration_name ~ '^0035' -> 0 rows`; `query: pg_get_constraintdef of chk_member_intent -> intent_state_code = ANY (ARRAY['planned','blocked'])`).

**Known defects and risks.**
1. The rule "nothing is drafted before it is registered" is not enforced: the intake accepts a proposal with no member (`operator-direct-adapter.ts:48`). Live, 214 of 502 operator-direct intakes carry no member (`query (bc_platform_dev, 2026-11-13): SELECT (reservoir_provenance_source_json->>'directory_member_uid') IS NOT NULL, count(*) FROM mcf.metric_authoring_intake_queue WHERE reservoir_name='operator_direct' GROUP BY 1 -> false 214; true 288`).
2. The vocabulary says ADR DEC-fa9424 "makes the directory entry the only door to writing a metric" (`vocabulary.md:108`). The ADR itself says "The Member is the sole UI authoring entry" and "The programmatic leg (`devhub_metric_drive`, operator-direct API) is untouched" (`bc-docs:docs/governance/adrs/ADR-fa9424.md:48,52 @ f4f5edd`). The two texts disagree on scope.
3. ADR DEC-85fd8d (entry rejection) is decided; its migration is unapplied and no route exists (State today).
4. The realize guard accepts an `approved` version, so "realized" does not mean certified (`realization.service.ts:10`; `vocabulary.md:110`).
5. `member.realized_metric_contract_uid` is a frozen legacy pointer that still holds values on 261 rows beside the event ledger (`realization.service.ts:5-7`; `query (bc_platform_dev, 2026-11-13): SELECT count(*) FROM metric_directory.member WHERE realized_metric_contract_uid IS NOT NULL -> 261`).
6. bc-admin calls legacy routes whose stores are empty or retired (State today), so those screens read stores that are empty or retired (the screens themselves were not opened in a running application for this dossier).
7. The chapter and the catalog chapter describe stores that do not match the database (How bc-docs defines it).

**Governing ADRs.**

| ADR | Summary | Status at `bc-docs @ f4f5edd` |
|---|---|---|
| DEC-b5c7ff | The directory is built in bc-core as its own subsystem | decided |
| DEC-5842d4 | Knowledge and governance layer on members | implemented |
| DEC-fa9424 | Authoring starts from a directory member; the seed-first entry is retired | implemented |
| DEC-85fd8d | A terminal "rejected" state for an entry | decided; not built |
| DEC-b049f6 | The readiness projection replaces the legacy funnel and dials | implemented |
| DEC-80eade | Legacy metric corpus retirement | implemented; legacy routes still mounted |
| DEC-375e6b, DEC-37967b | Seed enrichment rules; function and subfunction taxonomy | implemented |
| DEC-e8a4d2, DEC-ecec75 | Metric Definition as the parent of a contract (legacy model) | implemented; **conflicts** with the directory-first model of DEC-fa9424 and should be marked history |

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/operating-model/metric-directory.md` | rewrite | The concept text is sound; "no ADR", "not in any substrate" and section 11 are false today; no acts, routes or states are given |
| `docs/operating-model/metric-catalog.md` | history | Describes `metric.metric_definition` and a lifecycle that no record holds |
| `docs/onboarding/metric-workstream.md` | history | An overlay on three archived procedures; its 8-step sequence names `contract.canonical_field`, `contract.business_field`, `cc_field_mapping` and `metric_binding` (lines 102-107), which the lane ADR records as dropped (`bc-docs:docs/governance/adrs/ADR-ce4314.md:37 @ f4f5edd`). Judged by reading each step: 0 of 8 steps name a directory act; steps 2, 3 and 5 cannot be followed |
| `docs/archive/onboarding/metric-registration.md` | history | Already archived |
| `docs/reference/vocabulary.md` groups 1 to 3 | keep nearly as is | Matches the records; correct the DEC-fa9424 wording (defect 2) and add the seed status `superseded` |

**Open questions for the operator.**
1. Should the intake refuse a proposal with no directory member (make the rule a guard), or does the programmatic route stay open as DEC-fa9424 wrote it?
2. Should the realize guard accept only a certified version, or keep accepting `approved`?
3. Apply migration 0035 and build the reject act, or withdraw DEC-85fd8d?
4. The 15 certified-state versions with no operative realization and the 159 members with no version: repair them through the directory acts, or record them as residue?
5. Do the MLS tables in the `metric` schema stay (and move to another function), or retire with the rest of the schema?

**What "locked" will mean here.**
1. One route registers a member and one route creates an authoring intake; the intake refuses a missing member; a CI guard fails on a new route under `metric-directory` or `mcf/intakes`.
2. `metric-catalog`, `metric-catalog/definitions` and `metric-reference` are deleted from bc-core and bc-admin, and the `metric` schema is dropped or reassigned.
3. Every version in `mcf.mcv_live` has an operative realization (a query that returns 0).
4. The reject act is either built and applied or removed from the ADR set.
5. One guide chapter states each act, its route and its record, and `metric-catalog.md` and `metric-workstream.md` are marked as history in the same change.

### L9, Chain integrity

**What it is.** Chain integrity answers one question for each metric contract version: do the contracts and vocabulary it depends on line up today? The answer is the **chain verdict**: green, amber or red, with the result of each check. It says nothing about values. The platform needs it so that a broken dependency is found by a check and not by a failed evaluation.

**How bc-docs defines it.**
- The approved wording is in the vocabulary page: "**The chain verdict is a separate question.** `mcf.mcv_chain_status.verdict_code` is green, amber or red. It says whether the contracts a metric depends on line up. It says nothing about values, it is not a certificate, and it gates nothing. Say \"chain verdict green\", never \"ready\" or \"chain complete\"." (`bc-docs:docs/reference/vocabulary.md:134 @ f4f5edd`).
- The operating-model chapter is `docs/operating-model/chain-completeness-and-verdict.md`. Its own header says it is historical: "This chapter describes the D305 `contract.chain_status` model. That table was never populated and was DROPPED; the live chain-status surface is **`mcf.mcv_chain_status`**" (`bc-docs:docs/operating-model/chain-completeness-and-verdict.md:26 @ f4f5edd`). Its body still defines four verdicts, `complete`, `partial`, `broken`, `unlinked` (lines 108-111), and a seven-link chain coded "L1-L7" (lines 56-64). Neither exists in code. The "L1-L7" link codes collide with the lane codes L1 to L10.
- A second chapter, `docs/operating-model/quality-gates-and-chain-integrity.md`, defines a "Chain Integrity Check" with six rules over "Business Fields" and "Canonical Fields" (`bc-docs:docs/operating-model/quality-gates-and-chain-integrity.md:216-229 @ f4f5edd`). Those primitives are retired (`bc-docs:docs/governance/adrs/ADR-ce4314.md:37 @ f4f5edd`).
- **bc-docs has no live procedure for the lane.** The only procedure, `mc-chain-integrity.md`, is in `docs/archive/onboarding/` (`command: git ls-tree -r origin/main --name-only | grep mc-chain-integrity -> docs/archive/onboarding/mc-chain-integrity.md @ f4f5edd`), and the reference catalog of platform procedures confirms the metric-side procedures are archived (`bc-docs:docs/reference/platform-workflow-catalog.md:73-75 @ f4f5edd`).
- **bc-docs contradicts the code on two points:** the number of checks (the chapter header names five, the vocabulary none, the code seven or eight) and "it gates nothing" (see Known defects 1 and 2).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| module | `McvChainStatusService`, `chain-status-fingerprint.ts`, `metric-declaration-checks.ts` | `bc-core:src/registry/mcf/mcv-chain-status.service.ts:1-28,39-54 @ ec72438b` |
| route prefix | `registry/mcf/chain-status`: `POST refresh`, `GET summary`, `GET` (list), `GET candidate/:mcvUid` | `bc-core:src/registry/mcf/mcv-chain-status.controller.ts:13-52 @ ec72438b` |
| module and route prefix | `mcf/chain-audit`: `POST runs`, `GET evidence/:uid`, `GET evidence`, `GET summary` (the Chain Audit Service) | `bc-core:src/registry/mcf/chain-audit/chain-audit.controller.ts:39-97 @ ec72438b` |
| database table | `mcf.mcv_chain_status` (7 columns; `verdict_code` checked to green, amber, red) | `query (bc_platform_dev, 2026-11-13): pg_get_constraintdef of mcv_chain_status_verdict_code_check -> verdict_code = ANY (ARRAY['green','amber','red'])` |
| database table | `mcf.chain_audit_evidence` (append-only audit findings) | same query set; `audit_mode_code` has five allowed values |
| database table | `mcf.chain_dependency_epoch` (locks taken while a candidate is judged) | `bc-core:src/registry/mcf/mcf-cert-writer.service.ts:979-983 @ ec72438b`; shared with L6, to be split |
| schedule | nightly step `chain_status` at 02:00 and weekly `regression_audit`, both behind `BC_SCHEDULER_ENABLED` | `bc-core:src/boundary/runtime-scheduler.service.ts:58-68,84-89 @ ec72438b`; shared with RT, to be split |
| probe | MLS-13 chain status probe ("a PROBE (reporter), not a gate") | `bc-core:src/mls/probes/chain-status-mls-probe.service.ts:18-19 @ ec72438b` |
| screen | bc-admin `/catalog/metrics/chain-health` (`ChainHealthPage`: verdict list, summary, the act button, chain-audit evidence) | `bc-admin:src/components/AppRouter.tsx:223 @ d37b241`; `bc-admin:src/pages/ChainHealthPage.tsx:22,147 @ d37b241` |
| DevHub tool | `devhub_chain_status` (reads summary and list; can call `refresh`) | `barecount-devhub:src/mcp-server.js:2748-2803 @ 93cc1ea5` |
| DevHub gate | the session close gate reads `GET …/chain-status?verdict=red` | `barecount-devhub:src/lib/close-gather.js:120-128 @ 93cc1ea5` |
| schema source | bc-db migration `0042_mcv_chain_status_dependency_fingerprint.sql` | `bc-db:migrations/0042_mcv_chain_status_dependency_fingerprint.sql:1-53 @ c6de1c4` |
| deprecated, still mounted | `registry/integrity` (5 reads, `IntegrityService`); `registry/metric-readiness` (2 routes, both HTTP 410) | `bc-core:src/registry/integrity.controller.ts:2,20-95 @ ec72438b`; `bc-core:src/registry/metric-readiness.controller.ts:18-26 @ ec72438b` |

The taxonomy row also lists `registry/mc-integrity` (`barecount-devhub:artifacts/lanes/LOCKED-LANE-TAXONOMY-2026-08-24.md:38 @ 93cc1ea5`). No such controller exists today (`command: git grep -n "@Controller(" origin/main -- src | grep integrity -> registry/integrity only @ ec72438b`).

**The acts it performs.**

| Act | Who | Entry point | Writes |
|---|---|---|---|
| Judge every version in `mcf.mcv_live` and persist the verdicts | operator or platform admin; the nightly schedule when enabled | `POST /api/registry/mcf/chain-status/refresh` (`mcv-chain-status.controller.ts:17-23`); `runtime-scheduler.service.ts:68` | upserts one row per version in `mcf.mcv_chain_status`; rows are never deleted (`mcv-chain-status.service.ts:400-404`) |
| Read verdicts | any platform user | `GET summary`, `GET ?verdict=` | nothing; a row whose dependency fingerprint is old is returned as `stale` (`mcv-chain-status.service.ts:419-440`) |
| Judge one candidate version, read-only | operator | `GET candidate/:mcvUid` | nothing (`mcv-chain-status.controller.ts:38-47`) |
| Judge one candidate inside its certification and admit acts | the certification services (L6) | `judgeCandidate`, `refreshCandidate` (`mcv-chain-status.service.ts:256-321`) | the candidate's row, inside the admit transaction |
| Run a chain audit | platform admin; weekly schedule when doubly enabled | `POST /api/mcf/chain-audit/runs` | one row in `mcf.chain_audit_evidence` |

The checks written per version are `bindings_resolve`, `grain_cc_active`, `spec_assembles`, `currency_policy_supported`, `closed_set_conformance`, `pe_current`, `self_verification`, and `schedule_cc_active` when the metric declares a schedule (`mcv-chain-status.service.ts:462-514 @ ec72438b`). Any check starting `fail` gives red; otherwise any `amber` gives amber; otherwise green (lines 516-520).

**What it receives and what it hands on.**

| Hand-off | What passes | Defined in bc-docs | Built |
|---|---|---|---|
| In, from L6 | variable, filter and dimension references, evaluator results, self-verification results of each version | historical chapter only | yes |
| In, from L5 and L3 | which canonical contract is in force for the grain entity; whether each concept is active | historical chapter only | yes |
| Out, to L6 certification | the candidate's verdict as the deterministic gate: "PASS iff green" | **not in bc-docs** | yes (`bc-core:src/registry/metric-audit/decision/certification-panel-decision.lane.ts:55-59 @ ec72438b`) |
| Out, to L6 admit (the act that sets `active`) | verdict, fingerprint and time, bound into `metric_audit.transition_evidence` | **not in bc-docs** | yes (`bc-core:src/registry/mcf/mcf-cert-writer.service.ts:990-1012 @ ec72438b`) |
| Out, to DevHub | red verdicts since the session started block a session close | CLAUDE.md only | yes (`barecount-devhub:src/lib/close-gates.js:150-152 @ 93cc1ea5`) |
| Out, to DL, Delivery to a tenant | none: evaluation does not read the verdict | vocabulary ("gates nothing") | none found |

**State today.**
- **Live verdicts.** 82 versions are in `mcf.mcv_live` and each has a row: `query (bc_platform_dev, 2026-11-13): SELECT cs.verdict_code, count(*) FROM mcf.mcv_chain_status cs JOIN mcf.mcv_live lv USING (metric_contract_version_uid) GROUP BY 1 -> green 21; amber 7; red 54`. So 54 of 82 are red.
- **The table holds three times more history than current rows.** `query (bc_platform_dev, 2026-11-13): SELECT verdict_code, count(*) FROM mcf.mcv_chain_status GROUP BY 1 -> green 204; amber 44; red 84` (332 rows); `query: rows with no match in mcf.mcv_live -> 250`. A plain count of the table is therefore wrong; the service excludes these as `stale_excluded` (`mcv-chain-status.service.ts:410-415`).
- **Last written.** `query (bc_platform_dev, 2026-11-13): SELECT max(computed_at) FROM mcf.mcv_chain_status -> 2026-11-11 03:15:46+00`. All 82 current rows carry the seven check keys (`query: jsonb_object_keys over current rows -> 7 keys, 82 each`).
- **The nightly schedule is off on the development host.** The step returns unless `BC_SCHEDULER_ENABLED === '1'` (`runtime-scheduler.service.ts:58-64`), and the variable is not set in the serve configuration (`command: grep -n BC_SCHEDULER_ENABLED ~/bc-stack/process-compose.yaml -> no match`; a local file, not a repository). The lane kit's "Refresh nightly + on demand" (`barecount-devhub:artifacts/lanes/L9-chain-integrity/README.md:22 @ 93cc1ea5`) is not true there.
- **Chain audit evidence is frozen.** `query (bc_platform_dev, 2026-11-13): SELECT count(*), max(computed_at) FROM mcf.chain_audit_evidence -> 127; 2026-07-11 09:38:56+00`. By mode and verdict: regression audit 56 PASS, 34 OPERATOR_REVIEW, 17 FAIL on versions, 2 PASS on concepts; pre-M13 audit 3 PASS, 15 OPERATOR_REVIEW.
- **The retired tables are gone.** `query (bc_platform_dev, 2026-11-13): SELECT table_schema, table_name FROM information_schema.tables WHERE table_name ~ 'chain_status|mc_integrity|l_node' -> mcf.mcv_chain_status only`. bc-db migration `0009_drop_mc_integrity_state` has an apply record dated 2026-09-20 (`query: infrastructure.schema_migration_event -> applied`).
- **Duplicated: four things are called "chain".** (1) The chain verdict in `mcf.mcv_chain_status`. (2) Chain audit evidence in `mcf.chain_audit_evidence`, a separate audit with its own verdict words PASS, FAIL, OPERATOR_REVIEW. (3) The contract chain of L4 and L5, authored at `contracts/chains` and `contracts/observation-chains`, plus `mcf/chain-enrichment` (`command: git grep -n "@Controller(" origin/main -- src | grep chain @ ec72438b -> 5 prefixes`). (4) The deprecated `IntegrityService` at `registry/integrity`, which still has callers in the contract service and the test bench (`bc-core:src/registry/contracts/contract.service.ts:19,75`; `src/test-bench/test-bench.controller.ts:30,40 @ ec72438b`) and in bc-admin (`bc-admin:src/api/metric-catalog.ts:207,249 @ d37b241`). This reading counts four.
- **Three routes answer "what is this version's verdict":** the persisted list, the fresh candidate read, and the deprecated `registry/integrity/kpi/:contractId`.
- **Broken.** bc-admin still calls `GET /registry/metric-readiness/chain-detail/:mcId` (`bc-admin:src/api/formula-audit.ts:111 @ d37b241`; used by `src/components/metric/ChainReadinessJourney.tsx:35`), which bc-core answers with HTTP 410 (`metric-readiness.controller.ts:24-26`).

**Known defects and risks.**
1. **The vocabulary says the verdict "gates nothing"; the code gates on it twice.** Certification's deterministic gate passes only on green (`certification-panel-decision.lane.ts:58-59`), and the admit act refuses unless the candidate is green with a fingerprint: "chain status is '…', not green; cannot activate" (`mcf-cert-writer.service.ts:990-996`). ADR DEC-346ae7 and DEC-b01ed4 decided this; the vocabulary page was not updated.
2. **The check count differs in four texts:** four in CLAUDE.md, in the lane kit (`L9-chain-integrity/README.md:14`) and in the DevHub tool description (`mcp-server.js:2749`); five in the chapter header; seven or eight in code.
3. **Red is the common case** (54 of 82), so the DevHub close gate would block often; it reads only reds written since the session began (`close-gather.js:10-12`) and fails open when bc-core cannot be reached (`close-gather.js:120-128`).
4. Verdicts are written only when someone asks, on this host. Between writes a row can be out of date; the read marks it `stale` only when the fingerprint differs.
5. `self_verification` can pass on credit from a demo-plane proof (`mcv-chain-status.service.ts:23-24,152-164`), so a green verdict on the platform depends on the parked proof plane.
6. The two operating-model chapters teach verdict words (`complete`, `partial`, `broken`, `unlinked`) that the vocabulary forbids and no record holds.
7. `IntegrityService` is deprecated in its own header and still wired into `ContractService` (`integrity.controller.ts:2`; `contract.service.ts:75`).
8. A second schedule flag, `BC_SCHEDULE_REGRESSION_AUDIT`, is read from the environment in code (`runtime-scheduler.service.ts:87`); such switches are hard-coded configuration, not declarations.

**Governing ADRs.**

| ADR | Summary | Status at `bc-docs @ f4f5edd` |
|---|---|---|
| DEC-9c0da7 | Runtime doctrine; the live chain status is the MCF-native table (cited in the service header) | decided |
| DEC-b01ed4 | Green must predict evaluation: the spec assembles and closed-set values are canonical | decided |
| DEC-346ae7 | Certification's calculation leg is the deterministic gate; the admit act re-judges the candidate | decided |
| DEC-eb612b | Self-verification credit from a demo-plane proof | decided |
| DEC-1e55d3 | Post-certification audit (chain audit), and the split of authority with the chain verdict | decided |
| DEC-b049f6 | Legacy readiness diagnostics retired | implemented |
| DEC-29b518, DEC-354552, DEC-762336 | Listed for L9 in the readiness chapter (`bc-docs:docs/implementation/platform-readiness-program.md:110 @ f4f5edd`): activation gate fixes; reader and chain gates; chain reconciliation | decided; decided; implemented |
| DEC-bebaec, DEC-804874 | The old chain-completeness store and the L-node verdicts | superseded; both still listed as governing by `quality-gates-and-chain-integrity.md:12,14` and `chain-completeness-and-verdict.md:18` |

Conflict: DEC-c897cd makes the vocabulary page the only authority for status words, and that page's "gates nothing" contradicts DEC-346ae7 and DEC-b01ed4.

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/operating-model/chain-completeness-and-verdict.md` | history | Its own header says the model was dropped; verdict words and tables do not exist |
| `docs/operating-model/quality-gates-and-chain-integrity.md` (section "Chain Integrity Check") | rewrite | Six rules over retired primitives; governed by two superseded ADRs |
| `docs/archive/onboarding/mc-chain-integrity.md` | history | Already archived; no live procedure replaces it, so 0 steps can be followed from bc-docs today |
| `docs/reference/vocabulary.md` line 134 | rewrite (one sentence) | "gates nothing" is no longer true |
| lane kit `artifacts/lanes/L9-chain-integrity/README.md` | history | Its three-step playbook (write, read reds, repair) still works, judged by matching each step to a live route; the check list and "nightly" are out of date |

**Open questions for the operator.**
1. Is the chain verdict a gate on certification and on the admit act (as built), or a diagnostic that gates nothing (as the vocabulary says)?
2. Should verdicts be written on a schedule on every host, or only by an explicit act and by the certification acts?
3. Does chain audit evidence stay as a second audit inside this lane, move to EV, Evidence and lineage, or retire (nothing has been written since July)?
4. Should the 250 rows for versions no longer in `mcf.mcv_live` stay in the same table as history, or move out so that a plain count is true?
5. Should the DevHub close gate keep blocking on red verdicts while the metric estate is frozen?
6. Which of the four uses of "chain" keeps the word?

**What "locked" will mean here.**
1. One written list of checks, generated from the code, appears in the guide chapter, the vocabulary page and the DevHub tool, and a test fails when they differ.
2. `registry/integrity`, `IntegrityService` and `registry/metric-readiness` are deleted, with their bc-admin callers.
3. The vocabulary page and the guide state the same rule on what the verdict gates, and a test covers each gate.
4. Every version in `mcf.mcv_live` has a row whose read state is not `stale` after the lane's verify command runs.
5. A red verdict names the failing check and the lane that owns the repair.
6. `chain-completeness-and-verdict.md` is marked as history in the change that merges the guide chapter.

### L10, Tenant onboarding

**What it is.** L10, Tenant onboarding, is the hand-off from the platform to one tenant. A tenant is one organization's identity on the platform, with its own database. The lane records which contract versions a tenant has adopted (the source binding and the contract binding), issues a provisioning command for each table the tenant needs, and runs the worker that creates those tables in the tenant's database. When the current commands for a metric and the tables it depends on are `provisioned`, the metric is "enabled for" that tenant. The platform needs this lane because every contract is authored once on the platform side, and nothing can be evaluated on a tenant's data until the tenant's tables and bindings exist.

**How bc-docs defines it.**

- The function list gives one row: "**L10** | Tenant Onboarding | tenant DB provisioning, `admin.connection*` (Platform→Tenant boundary, MLS-14→15)" (`bc-docs:docs/implementation/platform-readiness-program.md:111 @ f4f5edd`). The lane ADR says: "L10 Tenant Onboarding (one tenant onto the operational chain) — tenant-scope" (`bc-docs:docs/governance/adrs/ADR-ce4314.md:33 @ f4f5edd`).
- The vocabulary page defines the record: "**Enabled:** the **current** provisioning command for the metric's current version is `provisioned`, and so are the current commands for the canonical and source tables it depends on, with their bindings recorded" (`bc-docs:docs/reference/vocabulary.md:166 @ f4f5edd`).
- The binding model: "A tenant is bound to a source contract version if and only if it holds a source binding for that version whose effective-to date is empty" and "A tenant holds at most one active adoption per contract" (`bc-docs:docs/operating-model/tenancy-and-binding.md:96,104 @ f4f5edd`).
- Two procedure chapters govern it: `docs/onboarding/tenant-onboarding.md` and `docs/onboarding/tenant-metric-binding.md`. A third chapter, `docs/implementation/tenant-onboarding.md`, describes the operator's steps in the admin console.
- **bc-docs contradicts the code on tenant creation.** The procedure says "The governed entry point is the **`POST /tenants`** API" (`bc-docs:docs/onboarding/tenant-onboarding.md:124 @ f4f5edd`). That route refuses (see State today). The same route is named as working in `docs/reference/platform-workflow-catalog.md:45,59` and `docs/implementation/platform-db-foundation-requirements.md:93,169` (both `@ f4f5edd`), and in `barecount-devhub:CLAUDE.md:109 @ 93cc1ea5`.
- **bc-docs contradicts itself on scope.** The binding chapter says "Binding declares which MCs are scoped for evaluation in a tenant" (`tenant-metric-binding.md:28`). ADR DEC-c220e4 calls that statement untrue (`ADR-c220e4.md:41`) and rules that "nothing reads it as entitlement" (`ADR-c220e4.md:52`).
- The lane taxonomy's ownership row is stale: it lists "`admin.connection*`; `tenants`, `connections`" (`barecount-devhub:artifacts/lanes/LOCKED-LANE-TAXONOMY-2026-08-24.md:39 @ 93cc1ea5`). It omits `schema-provisioner`, where every L10 act lives today, and places `schema-provisioner` in the not-a-lane register (same file, line 54).

**What it owns.**

| Kind | Name | Citation |
|---|---|---|
| module | `src/schema-provisioner/` (onboarding services, binding writer, command store, table generator, worker) | `bc-core:src/schema-provisioner/` (29 non-test files, `git ls-tree`) `@ ec72438b` |
| module | `src/tenant-management/` (tenant registry, creation, retirement). Shared with S3, Tenant lifecycle and management, to be split | `bc-core:src/tenant-management/tenant-management.controller.ts:21 @ ec72438b` |
| route prefix | `schema-provisioner` (`onboard-metric`, `onboard-connector`, `tenants/:slug/provisioning`, `provisioning/commands/:id/reissue`) | `bc-core:src/schema-provisioner/connector-onboarding.controller.ts:42-105 @ ec72438b` |
| route prefix | `schema-provisioner/provisioning` (`resolve-readiness`). Shared with L5, Canonical Contracts, to be split: it moves contract versions to `active` | `bc-core:src/registry/contracts/provisioning-readiness.controller.ts:18-31 @ ec72438b` |
| route prefix | `tenant-bindings` (create, list, deactivate a source binding). Hosted in the reader controller; shared with L7, Readers and connections, to be split | `bc-core:src/registry/readers/reader.controller.ts:421-459 @ ec72438b` |
| route prefix | `tenants`. Shared with S3, to be split | `bc-core:src/tenant-management/tenant-management.controller.ts:21-114 @ ec72438b` |
| route prefix | `connections`, `t/connections`. Shared with L7, to be split | `bc-core:src/registry/connections/connection.controller.ts:13`; `src/tenant-views/tenant-views.controller.ts:335 @ ec72438b` |
| route prefix | `t/legal-entities` (the tenant's legal entities and fiscal calendars). Shared with RT, Runtime, to be split | `bc-core:src/registry/legal-entity/legal-entity.controller.ts:35-65 @ ec72438b` |
| route prefix | `admin/tenant-metrics` (retired; both routes answer 410) | `bc-core:src/tenant-metrics/tenant-metrics.controller.ts:17-25 @ ec72438b` |
| table | `tenant.tenant_binding`, `tenant.contract_binding`. Shared with DL, Delivery to a tenant, to be split: they are the enablement records | query (bc_platform_dev, 2026-11-13): `SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema IN ('schema_provisioner','tenant')` -> 10 tables |
| table | `schema_provisioner.provisioning_command`, `provisioning_command_transition`. Shared with DL, to be split | same query |
| table | `tenant.tenants`, `tenant.tenant_infrastructure`, `tenant.onboarding_record`, `tenant.tenant_classification_transition`, `tenant.tenant_schema_fence_event`. Shared with S3, to be split | same query |
| table | `tenant.gl_account_classification_binding` | same query |
| command | `npm run provisioning:worker`, `npm run provisioning:sweep` | `bc-core:package.json:26,28 @ ec72438b` |
| command | `npm run tenant:lifecycle` (`create`, `retire-prepare`, `retire-record`, `retire-drop`). Shared with S3, to be split | `bc-core:package.json:27`; `src/tenant-management/lifecycle/tenant-lifecycle-cli.ts:7-9 @ ec72438b` |
| screen | bc-admin tenant create page. Shared with S3, to be split | `bc-admin:src/pages/TenantCreatePage.tsx:1-22 @ d37b241` |
| screen | none for `onboard-metric`, `onboard-connector` or the worker | command: `git -C bc-admin grep -n -E "onboard-metric\|onboard-connector\|schema-provisioner" origin/main -- src` -> no match |
| document | `docs/onboarding/tenant-onboarding.md`, `docs/onboarding/tenant-metric-binding.md`, `docs/implementation/tenant-onboarding.md`, `docs/operating-model/tenancy-and-binding.md` | `bc-docs @ f4f5edd` |

`src/platform` holds libraries, master data and vendor costs; none of it is L10 (command: `git ls-tree -r origin/main --name-only -- src/platform`).

**The acts it performs.**

| Act | Who | Entry point as built | States and writes |
|---|---|---|---|
| Create a tenant and its database (shared with S3) | The operator, at a terminal | `npm run tenant:lifecycle -- create <slug> …` (`tenant-lifecycle-cli.ts:56-62`) | Registry row `provisioning`, then CREATE DATABASE, the tenant skeleton, bc-db runs, checks, then `completeProvisioning` sets "tenant active" and stamps the onboarding record `activated` (`tenant-birth.service.ts:3-7`; `tenant-management.repository.ts:132`) |
| Tenant metric onboarding | A platform admin, by direct API call | `POST /schema-provisioner/onboard-metric` (`connector-onboarding.controller.ts:61-70`) | Resolves an active tenant; walks back from the metric to one canonical contract and its source contracts; writes source bindings and canonical contract bindings; issues commands for the source, canonical and metric tables; answers 202 (`metric-onboarding.service.ts:78-124`) |
| Connector onboarding | A platform admin | `POST /schema-provisioner/onboard-connector` (`connector-onboarding.controller.ts:50-59`) | Walks forward from a connector; writes source and canonical bindings; issues commands |
| Source binding, direct | Platform admin or operator role | `POST /tenant-bindings`, `POST /tenant-bindings/deactivate` (`reader.controller.ts:425-459`) | Writes or ends a row in `tenant.tenant_binding` |
| Contract binding on activation | No person: a side effect of a canonical version becoming `active` | `ContractActivationService.enqueueProvisioning` (`contract-activation.service.ts:94-145`) | Adds a contract binding and a command for every affected tenant; skips versions pinned to the demo plane (lines 103-106). The dossier for L5, Canonical Contracts, reads the binding as written at the activate call (`approved` to `pending_provisioning`), not when the version becomes `active`; the two readings differ, and the Define step of L5 settles it |
| Run the worker | The operator, at a terminal, holding the tenant owner credential | `provisioning-worker-cli.ts` (default drain, `--sweep`, `--command=<id>`, `--no-readiness`) (lines 11-30, 110-124) | Each command: `pending`, `provisioning`, then `provisioned` or `failed`. The worker is the only program that creates tenant tables |
| Readiness pass | The worker after each run; or `POST /schema-provisioner/provisioning/resolve-readiness`; or a five-minute timer when `BC_SCHEDULER_ENABLED=1` | `ProvisioningReadinessService.resolve` (`provisioning-readiness.service.ts:83-107`; `provisioning-readiness.scheduler.ts:24-31`) | Moves every `pending_provisioning` canonical or metric version whose affected tenants are all `provisioned` to `active` |
| Reissue a failed command | A platform admin, with a rationale | `POST /schema-provisioner/provisioning/commands/:id/reissue` (`connector-onboarding.controller.ts:83-105`) | Opens the next attempt; history is kept |
| Legal-entity declaration | Operator, tenant admin or platform admin | `POST /t/legal-entities` (`legal-entity.controller.ts:36-40`) | Tenant-side rows. The route that writes the legal-entity binding itself was not traced in this reading |
| Unbind or disable a metric | Not built | No route (command: `git grep -n -i -E "unbind\|offboard-metric\|disable-metric\|deactivate" origin/main -- src/schema-provisioner src/tenant-management` -> no match) | — |

**What it receives and what it hands on.**

| Direction | From or to | What passes | Defined in bc-docs | Built |
|---|---|---|---|---|
| in | L6, Metric Contracts and certification | The metric's current `active` version and its grain entity | Yes, as the walk (`ADR-c220e4.md:52`) | Yes (`metric-chain-reverse-walk.service.ts:10-16`). The dependency is inferred from grain, not read from a declaration |
| in | L5, Canonical Contracts | "the single active Canonical Contract" for that grain; an activation event | Partly | Yes (`contract-activation.service.ts:94`) |
| in | L2, Source and Admission Contracts | The source contract versions the canonical contract depends on | Yes (`tenancy-and-binding.md:96`) | Yes |
| in | S3, Tenant lifecycle and management | A tenant whose status is `active` | Named only | Yes (`schema-provisioner.repository.ts:82-88`) |
| in | S4, Pricing and subscription | The tenant's entitlement | Yes (`tenant-onboarding.md:112-118, 149-155`) | No. No Subscription record exists (`ADR-c220e4.md:35`) |
| in | L7, Readers and connections | A connection owned by the tenant | Yes (`tenant-onboarding.md:157-173`) | Yes, on separate routes |
| out | L5, L6 | The readiness pass moves held versions to `active` | No | Yes |
| out | RT, Runtime | The tenant's `fact.so_`, `fact.co_` and `fact.ms_` tables | Yes (vocabulary, line 166) | Yes. Evaluation reads no binding (`vocabulary.md:174`) |
| out | DL, Delivery to a tenant | "Enabled for (tenant)", read from the command store | Yes (vocabulary, line 166) | Yes, as a read (`connector-onboarding.controller.ts:72-81`) |
| out | TS, Tenant self-service | The admin invite and readiness view | Yes (`implementation/tenant-onboarding.md:61-65`) | Not checked here |

**State today.**

- **Works:** tenant metric onboarding, the command store, the worker and the reissue route. Live commands: 45 in all; 40 `provisioned`, 3 `pending`, 2 `failed` (query (bc_platform_dev, 2026-11-13): `SELECT c.tenant_key, c.requested_by, l.to_state, count(*) FROM schema_provisioner.provisioning_command c LEFT JOIN (latest transition per command) l … GROUP BY 1,2,3` -> kaveri 33, kaveridemo 4, kaveridemo2 8).
- **Tenants:** 4 rows: 1 `active` (`kaveri`), 2 `suspended`, 1 `archived` (query: `SELECT status_code, count(*) FROM tenant.tenants GROUP BY 1`). Tenant databases: `tbc_kaveri_dev`, `tbc_kaveridemo_dev`, `tbc_kaveridemo2_dev` (query: `SELECT datname FROM pg_database WHERE datname LIKE 'tbc_%'`). Onboarding records: 3, all `activated`.
- **The served creation route refuses by design.** `POST /tenants` and `GET /tenants/target-preview` throw 403 with "Tenant database creation is not served: it runs on the operator plane" (`bc-core:src/tenant-management/tenant-provisioning-api.service.ts:14-36 @ ec72438b`). The controller's own description still says it provisions (`tenant-management.controller.ts:28-35`). The admin console's create page posts to it (`bc-admin:src/api/tenants.ts:211 @ d37b241`).
- **Tenant creation paths counted: three.** One works (the `tenant:lifecycle` command). One refuses (the served route, with its screen). One is a test harness that a guard keeps out of non-test code (`provisionTenantDb`, `bc-core:src/registry/seed/seed-tenant-dbs.ts:17-21`).
- **Duplicated: five origins issue provisioning commands.** `onboard-metric`, `onboard-connector`, canonical activation, an evaluation that commits to a missing table (`governed-metric-persistence.adapter.ts:530-543`), and the worker's sweep (`provisioning-sweep.service.ts:6-15`). Live commands by origin: `metric-onboarding` 30, `activation` 13, `evaluation` 2, `connector-onboarding` 0.
- **Duplicated: two routes write a source binding** (`onboard-*` and `POST /tenant-bindings`).
- **Bindings:** `tenant.contract_binding` has 17 rows, all family `canonical`, all `is_active`, none of family `metric` (query: `SELECT contract_family, is_active, count(*) FROM tenant.contract_binding GROUP BY 1,2`). `kaveri` holds 13 rows over 4 contracts, with up to 6 active versions of one contract. `tenant.tenant_binding` has 28 rows: 27 open, 1 closed.
- **Hard-coded or inferred:** the walk assumes one active canonical contract per grain entity and fails otherwise (`metric-chain-reverse-walk.service.ts:10-25`). The environment code is a free request field; live rows carry `dev`, `development` and `apex`.
- **Not built:** unbind, disable, the Subscription record, the entitlement check, the activation gate (bc-db migration `0034_onboarding_completeness_result.sql` has no applied event: query `SELECT count(*) FROM infrastructure.schema_migration_event WHERE migration_name LIKE '0034%'` -> 0), any screen for enabling a metric, and the DevHub tool the lane kit names (`devhub_tenant_bind_metrics` is retired: `barecount-devhub:src/mcp-server.js:3062-3064 @ 93cc1ea5`).

**Known defects and risks.**

1. Five or more documents name a creation route that refuses (citations under "How bc-docs defines it").
2. The readiness pass has no exclusion for versions pinned to the demo plane. Only the fan-out and the sweep call `isPlanePinnedCoordinate` (command: `git grep -n isPlanePinnedCoordinate origin/main -- src` -> `contract-activation.service.ts:84,103`, `provisioning-sweep.service.ts:157`, one comment). A version with zero affected tenants gets the outcome `ready` (`provisioning-readiness-assessor.service.ts:19`). The pass is global and runs by default after every worker run (`provisioning-worker-cli.ts:74, 122-124`). A held version can therefore become `active` without anyone asking.
3. 24 open source bindings belong to five tenant ids that are not in `tenant.tenants` (query: `SELECT b.tenant_id, t.slug, b.environment_code, count(*) FROM tenant.tenant_binding b LEFT JOIN tenant.tenants t ON t.id::text=b.tenant_id::text GROUP BY 1,2,3` -> 5 ids with no slug: 11, 4, 4, 4, 1). The table has no foreign key to the tenant registry (query on `pg_constraint` -> primary key only).
4. No act ends a prior contract binding. The design rule of one active adoption per contract is broken live (6 active versions of one contract for `kaveri`), and the chapter admits "the writers do not enforce it yet" (`tenancy-and-binding.md:104`).
5. No metric-family contract binding is ever written (`metric-chain-reverse-walk.service.ts:18-22`), although the chapter says metric adoption is recorded there (`tenancy-and-binding.md:98`). The command store is the only record of which metrics a tenant has, and DEC-c220e4 item 3 forbids reading scope from it.
6. Connector onboarding finds canonical contracts through `contract.canonical_mapping` (`schema-provisioner.repository.ts:505-537`), which holds 0 rows (query: `SELECT count(*) FROM contract.canonical_mapping` -> 0). It has issued 0 live commands. It cannot reach a canonical contract today.
7. An evaluation can issue a provisioning command, so a metric can become enabled for a tenant without the onboarding act (2 live commands, 1 still `pending`).
8. Tenant birth stamps the onboarding record `activated` at once; the update comment describes a database trigger that refuses `active` without a verdict (`update-tenant.dto.ts:12-17`), and that trigger is not in the live database (query on `pg_trigger` for `tenant.tenants` -> `trg_tenants_database_name_default`, `trg_tenants_class_frozen` only).
9. `tenant.tenant_infrastructure` shows 2 rows `provisioning` for tenants that are active or archived (query: `SELECT status_code, count(*) FROM tenant.tenant_infrastructure GROUP BY 1` -> active 2, provisioning 2).
10. Code cites ADR DEC-1bb88e (`contract.service.ts:866`); no such file exists in bc-docs at origin/main.

**Governing ADRs.**

| ADR | Plain summary | Status in file |
|---|---|---|
| DEC-ce4314 | Ten lanes; L10 is the tenant-scope lane | decided |
| DEC-a67bae | One owner per surface; lane boundaries locked | decided |
| DEC-c220e4 | Every active tenant gets every active metric until the Subscription is built; the onboarding walk sets a metric up and entitles nothing | decided; supersedes DEC-4aa2fd |
| DEC-f7d4fc | Source adoption in `tenant_binding`; canonical and metric adoption and all overrides in `contract_binding` | decided |
| DEC-95687d | The provisioner creates typed tenant tables; connector onboarding is the primary trigger | implemented |
| DEC-7df811 | Onboarding record, tenant status and subscription are three lifecycles | decided |
| DEC-cf6d3b | "Tenant active" means a verified admin and an assigned subscription | decided |
| DEC-a67518 | A checklist gate for the bring-your-own-database tiers | decided |
| DEC-771baf, DEC-f02230 | One database per tenant; its schema layout | implemented |
| DEC-005ea7 | One production environment per tenant | implemented |
| DEC-3f6b1b | A demo-plane proof resolves its canonical version on the plane | decided |
| DEC-1918d0 | Database rules, including mandatory foreign keys | implemented |

Conflicts: DEC-95687d names connector onboarding as the primary trigger, while the built and used act is metric onboarding under DEC-c220e4. DEC-cf6d3b's meaning of "tenant active" is not what the birth act does. DEC-005ea7 leaves `environment_code` without meaning, yet it is part of the source binding's key and carries three values. DEC-ad76e9 (three-phase onboarding, marked implemented) describes a commercial journey that no code implements; it does not govern this lane today.

**Chapters to fold in, rewrite or retire.**

| bc-docs path | Verdict | Reason |
|---|---|---|
| `docs/onboarding/tenant-metric-binding.md` | keep nearly as is | All six sections of its live path match the code read today (two routes, worker, status read, reissue, no unbind). Correct the scope sentence at line 28 and the words "Platform Ready" |
| `docs/onboarding/tenant-onboarding.md` | rewrite | Of its 11 steps, 2 can be followed as written (6, connection authoring; 9, first run). Steps 1, 1.5, 2 and 5 need records that do not exist; steps 3 and 4 name the refusing route and a test-only script; step 10 checks a Subscription state. Steps 7 and 8 were not re-checked. Judged by matching each step's named entry point to a route or command at origin/main |
| `docs/implementation/tenant-onboarding.md` | rewrite | Its "single governed provisioning call" in the admin console (line 55) refuses today |
| `docs/operating-model/tenancy-and-binding.md`, "Contract Binding" | keep nearly as is | Matches DEC-f7d4fc and states its own enforcement gap |
| `docs/implementation/tenant-readiness-program.md` | history | A dated run log of the Kaveri walk; true when written |
| `docs/reference/platform-workflow-catalog.md` (tenant row) | rewrite | Says tenant creation by `POST /tenants` is "Now closed" (line 59) |
| `artifacts/lanes/L10-tenant-onboarding/README.md` (barecount-devhub) | history | Names a refusing route, a retired tool and a tenant that no longer exists |

**Open questions for the operator.**

1. Should L10 own tenant creation, or only bind, provision and enable, with creation moved wholly to S3?
2. Should the dependency of a metric be read from a declaration on the metric version, or stay inferred from grain?
3. Should a metric-family adoption record be written per tenant, or should the command store be accepted as the enablement record?
4. Which single origin may issue provisioning commands: the onboarding act alone, or also activation and evaluation?
5. Should connector onboarding be repaired or deleted?
6. Should the 24 source bindings with no tenant be removed by a governed act, or kept as history?
7. Should the readiness pass stay a default part of every worker run?

**What "locked" will mean here.**

1. One command creates a tenant, and every document and screen names that command and no other.
2. One act enables a metric for a tenant; `git grep` finds one origin that issues provisioning commands, and a CI guard fails on a second.
3. Every source binding and contract binding row points to a tenant in the registry, enforced by a foreign key, and no tenant holds two active adoptions of one contract.
4. The readiness pass refuses a version pinned to the demo plane, with a test that can go red.
5. A disable act exists, or the guide lists it under "designed, not built".
6. A fresh session, using only the chapter and the commands, enables one metric for one tenant and reads "enabled for (tenant)" from the status command.
