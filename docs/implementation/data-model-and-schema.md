---
id: data-model-and-schema
order: 21
title: "Data Model and Schema"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, operating-model-overview, architecture, backend-services, internal-modules, infrastructure]
governing_sources:
  - Foundation
  - The Object Model
  - The Contract Grammar
  - The Evaluation Boundaries
  - The Authority Model
  - Operating Model
  - Architecture
  - Backend Services
  - Internal Modules
  - Infrastructure
governing_adrs:
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules)
  - DEC-771baf (Tenant database topology; platform-tenant one-way dependency)
  - DEC-69f09e (ISO 11179 naming convention)
  - DEC-bebaec (Chain completeness SSOT — retired; replaced by mcf.mcv_chain_status per DEC-9c0da7)
  - DEC-804874 (L-node semantic verification gate at session close — verdict table dropped R3/R6)
  - DEC-9c58c6 (Operating Model section name; fiscal-period rename)
  - DEC-ee6018 (bc-qa standalone repo; QA tooling)
  - DEC-f02230 (Tenant database schema reorganization; D368 originally introduced as a six-schema layout, currently seven schemas in the live DDL after the progression schema landed under D369)
  - DEC-c06f41 (Spine expansion to eight sections plus home)
  - DEC-02f5a9 (BCF greenfield registry — concept_registry schema)
  - DEC-61850f (BCF adoption — semantic_role relocation to business_concept_version)
  - DEC-14f5b6 (Measurement semantics — measure_class and context_concept_id on BCV)
  - DEC-1fbaf1 (BCF withdrawal ceremony — archived_at soft-delete)
  - DEC-c3e57f (Foundational MCF ADR — mcf schema)
  - DEC-9c0da7 (Runtime Spine R0-R6 — mcv_chain_status, webhook endpoints, reader watermarks)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Data Model and Schema

## Scope

This chapter records the database design rationale: the two-database split, the authoritative DDL discipline, the ten database rules that govern every table, the ISO 11179 naming convention, the schema-grouping shape at the family level, the Drizzle ORM mirroring discipline, the schema evolution methodology, and the current drift inventory. It is the design-and-discipline authority for the data model.

This chapter does not enumerate every table or every column. The per-schema, per-table, per-column inventory is the role of the **Data Dictionary** reference (`docs/data-dictionary/`, queued; auto-generated from `bc-core/docker/redesign/*.sql`); when the Data Dictionary lands, a reader who needs per-table detail consults it. This chapter records the structural shape and the rules; the Data Dictionary will record the structural inventory.

This chapter sits between Infrastructure and API Surface. Infrastructure records where the databases run and how they are provisioned; API Surface records the endpoints that read and write them; this chapter records the structural shape of what is stored. It does not redefine boundary semantics (deferred to Operating Model), the contract grammar (deferred to The Contract Grammar), per-endpoint shapes (deferred to API Surface), per-module catalog (deferred to Internal Modules), or the operational procedures that maintain the schema (deferred to Operations).

**Governing source.** Architecture; Infrastructure; outline.md §4.3.

## The Two-Database Model

Per DEC-1918d0 and DEC-771baf, the platform splits its data into two databases:

| Database | Naming | Holds | Owner |
|---|---|---|---|
| Platform DB | `bc_platform_dev` (one per environment) | All contract definitions, the Source Catalog, master and reference data, governance records, tenant identity records | Platform side; written through governed control-plane acts inside bc-core |
| Tenant DB | `tbc_{slug}_dev` (one per tenant) | Per-tenant runtime state: boundary objects, evidence and lineage, run records, connections, contract bindings, tenant-scoped extension content | Tenant scope; written through governed runtime acts and governed tenant-scoped authoring acts inside bc-core |

The two-database split is the architectural commitment recorded in Architecture and Infrastructure. The asymmetric ownership rule is one-directional: platform contracts feed into tenant runtime acts; tenant runtime acts do not feed back into platform contracts. Discovery acts read tenant state read-only without writing. Tenant DBs are physically separate Postgres databases provisioned at tenant onboarding via `seed-tenant-dbs.ts`.

**Governing source.** Architecture; Infrastructure; DEC-1918d0; DEC-771baf.

## Authoritative DDL

The authoritative source for all schema definitions is three SQL files plus a migrations directory under `bc-core/docker/redesign/`. The Drizzle ORM definitions in `bc-core/src/database/schema/` mirror the DDL and are the runtime-side type surface; when the two diverge, the DDL wins.

| File | Role |
|---|---|
| `01-platform-schemas.sql` | Creates the twelve platform schemas; enables `pgcrypto` |
| `02-platform-tables.sql` | Creates all platform tables, indexes, and foreign keys; assembled from `02-platform-tables/00-master.sql` through `_all.sql` |
| `03-tenant-db.sql` | Creates the seven tenant schemas and the fixed tenant tables; applied to each tenant database after `CREATE DATABASE` |
| `migrations/` | Per-decision migration files that add, alter, or rename objects after the initial DDL was set |

Migrations are date-prefixed (`YYYYMMDD-*`) or decision-prefixed (`dec-*`, `tsk-*`, `bcf-*`). Notable recent migrations beyond the initial `20260421-d366-d368-schema-reorg.sql`:

- `20260521-f2-concept-registry-schema.sql` — BCF schema (DEC-02f5a9): 9 tables in `concept_registry`
- `bcf-oagis-seed-v0-substrate.sql` — `bcf.oagis_seed` table
- `ai-telemetry-ledger-v0-substrate.sql` — `ai_telemetry` schema (2 tables)
- `d369-m4-progression.sql` — tenant `progression` schema
- `20260613-d443-bcf-semantic-role-relocation-phase1/3.sql` — semantic_role on BCV (DEC-61850f)
- `20260706-g10-withdrawal-lifecycle-encoding.sql` — BCF withdrawal coherence CHECKs
- `20260706-bcf-panel-run-disposition.sql` — 4 disposition columns on panel_output_record
- `20260707-d496-measure-context.sql` — measure_class + context_concept_id on business_concept_version (DEC-14f5b6)
- `dec-9c0da7-mcv-chain-status.sql` — `mcf.mcv_chain_status` (replaces retired `contract.chain_status` / `contract.l_node_semantic_verdict`)

A reader who needs the full migration list runs `ls bc-core/docker/redesign/migrations/`.

**Governing source.** `bc-core/docker/redesign/01-platform-schemas.sql`; `bc-core/docker/redesign/02-platform-tables.sql`; `bc-core/docker/redesign/03-tenant-db.sql`; `bc-core/docker/redesign/migrations/`.

## The Ten Database Rules

Per DEC-1918d0, every database change in bc-core honors ten rules. The rules apply equally to Platform DB and Tenant DB.

| # | Rule | Detail |
|---|---|---|
| 1 | No JSONB for queryable data | If a column is used in WHERE, ORDER BY, GROUP BY, or JOIN, it is a column not JSONB. JSONB is for opaque payloads, flexible config, and frozen snapshots only |
| 2 | No denormalized counters | Never store a count derivable from child rows; use a view or compute on read |
| 3 | FK constraints mandatory | Every reference to another table's PK must have an explicit FK constraint |
| 4 | One source of truth per value | Don't duplicate parent columns in child tables; query via FK |
| 5 | Shared patterns use shared tables | Tags use a tag table plus an entity_tag junction; owners use an owner_assignment table; not inline JSONB per entity |
| 6 | Max 20 columns per table | Split by concern if exceeded (core identity vs config vs governance) |
| 7 | Indexes follow query patterns | The index ships in the same migration as the list endpoint it supports |
| 8 | Soft deletes via `archived_at` | NULL means active; set means archived; no `is_deleted` columns; no `status = 'deleted'` |
| 9 | Temporal via `effective_from` and `effective_to` | NULL `effective_to` means currently active |
| 10 | New table checklist | Confirm naming standard, FK constraints, no queryable JSONB, no counters, no duplicates, shared tags and owners, ≤20 columns, indexes defined |

The rules are enforced by code review and by `bc-qa` audits per DEC-ee6018. Verified compliance against the current DDL: rules 1, 2, 3, 5, 7, 8, and 9 PASS; rule 6 sample-verified on the largest tables; rule 10 is procedural.

**Governing source.** DEC-1918d0; CLAUDE.md.

## ISO 11179 Naming Convention

Per DEC-69f09e, every name in the schema follows ISO 11179 in `snake_case`. The convention is mechanical and uniform; a reader who knows the convention can predict the name of a column from its role.

| Role | Pattern | Example |
|---|---|---|
| Primary key | `{entity}_id` | `tenant_id`, `contract_id`, `evidence_record_id` |
| Code identifier | `{noun}_code` | `domain_code`, `status_code`, `subdomain_code` |
| Boolean | `is_{adj}` | `is_active`, `is_archived`, `is_published` |
| Timestamp | `{verb}_at` | `created_at`, `updated_at`, `archived_at`, `evaluated_at` |
| JSON column | `{noun}_json` | `contract_json`, `payload_json`, `evidence_json` |
| Table name | singular | `tenant`, `contract_binding`, `metric_snapshot` (not `tenants`) |
| Index | `idx_{table}_{cols}` | `idx_observed_record__tenant_time`, `idx_source_object__contract_time` |
| Unique constraint | `uq_{table}_{cols}` | `uq_source_system__provider_name` |
| Foreign key | `fk_{table}_{ref}` | inline `REFERENCES` statements without explicit name; constraint resolution by Postgres default |

A note on table naming: the repository historically uses `tenants` (plural) in `tenant.tenants` for the tenant identity registry; this is a known exception to the singular convention and predates the locked DEC-69f09e discipline.

**Governing source.** DEC-69f09e; CLAUDE.md.

## Schema Groupings

The Platform DB carries fifteen schemas (twelve original plus `concept_registry`, `bcf`, and `ai_telemetry` added via migrations). The Tenant DB carries seven schemas, separating governed boundary state, dynamic typed projections, proof, per-tenant operational state, and per-tenant dimensions. The schemas below are listed at the family level only; per-table and per-column inventory will live in the Data Dictionary reference.

### Platform DB schemas

| Schema | Concern |
|---|---|
| `contract` | The contract registry: the seven contract families with their version histories and approvals, the Canonical Mapping supporting schema, legacy Business Object vocabulary primitives (Business Object, Business Field, Canonical Field — superseded by `concept_registry` for semantic identity; retained for OC/CC field_selection binding), CC field mapping, chain lineage and meta-schema bookkeeping. **Retired tables:** `contract.chain_status` (D305, dropped R3/R6 — replaced by `mcf.mcv_chain_status`), `contract.l_node_semantic_verdict` (D366, never populated, dropped R3/R6). `contract.l_node_semantic_trace` retained for historical reference only |
| `concept_registry` | The Business Concept Framework (BCF) — the platform's semantic identity spine. Replaces legacy BO/BF vocabulary (DEC-02f5a9 greenfield, DEC-61850f adoption). Tables: `characteristic`, `representation_term`, `entity`, `entity_version`, `business_concept`, `business_concept_version`, `alias`, `entity_supersession`, `business_concept_supersession`, `supersession_proposal`, `characteristic_supersession`, `characteristic_definition_amendment`. Governed by AI panel (Maker/Checker/Moderator) + C5 operator-confirm + F3 write ceremony |
| `bcf` | BCF operational support: `oagis_seed` (the OAGIS standard seed corpus for vocabulary derivation) |
| `master` | Reference and master data shared across the platform: dimensions (country, currency, fiscal periods), the master function and subfunction taxonomy, industry classifications, source-classification dimensions (criticality, pattern, velocity, veracity, volume), status, system type, library |
| `source` | The Source Catalog hierarchy: the six-tier walk from `source_provider` down through `source_system`, `source_version`, `source_module`, `source_object`, to `source_field` |
| `runtime` | Platform-authored Reader and Connector definitions: connector protocols, readers, reader flavors, reader bindings. The per-tenant Connection records live in tenant DBs |
| `metric` | Metric authoring surface: metric definitions, metric bindings, metric formulas and formula variables, formula verification, the metric knowledge catalogue, MLS state and trigger bindings |
| `mcf` | The Metric Context Framework — the live metric stack (DEC-c3e57f/D422). 18+ tables: `metric_contract`, `metric_contract_version`, `metric_binding`, `metric_filter`, `metric_computed_dimension`, `metric_formula_ast`, `metric_formula_package_signature`, `metric_fixture`, `metric_fixture_verifier_result`, `seed_metric`, `metric_intake`, `metric_certification`, `panel_run`, `panel_output`, `panel_consensus`, `mcv_chain_status`, and others. Governed end-to-end via M0–M20 gate sequence |
| `ai_telemetry` | AI observability: `ai_run_ledger` (per-panel-run cost/latency) and `ai_call_ledger` (per-vendor-call detail) |
| `operations` | Platform-side operational state: governance activity log (distinct from per-tenant activity log in `admin`), BO and catalog verification logs, discovery scans and discovered objects/fields |
| `execution` | Platform-side run-tracking aggregates: `boundary_progression` (per-tenant × per-contract × per-object-type runtime counts; renamed from `chain_status` 2026-05-09 per audit C-3 / DEC-bebaec errata), boundary health, boundary rollups, run and rejection summaries |
| `tenant` | Platform-side tenant identity and binding: the tenant registry, the bound contract version per tenant, contract bindings, tenant infrastructure |
| `infrastructure` | Cross-cutting platform infrastructure: email templates, feature flags, idempotency keys, notification log |
| `support` | Internal support: ticket and ticket comment |
| `pricing` | Package definitions |
| `users` | Platform user identity |

### Tenant DB schemas

| Schema | Concern |
|---|---|
| `envelope` | The original boundary objects in JSONB-payload form. **Deprecated per D369 M4; planned drop in M4.4** |
| `progression` | The D369 metadata-only boundary events that replace `envelope`: admission, canonical evaluation, metric evaluation, intervention evaluation, plus per-run records |
| `fact` | Dynamic typed projections; one fact table per activated Canonical Contract. Empty at provisioning time; populated by `SchemaProvisionerService` at Canonical Contract activation |
| `evidence` | The proof chain: evidence objects, evidence records, lineage objects |
| `admin` | Per-tenant operational state: activity log, connections, connection config, connection checks, tenant users |
| `organization` | Per-tenant organizational state: organization profile, fiscal calendar configuration (SCD Type 2 with `effective_from` / `effective_to`) |
| `tenant_dim` | Tenant-side dimension tables (currently `dim_legal_entity` at MVP) |

The envelope-to-progression migration per D369 is in progress at the time of writing. Envelope and progression coexist; the read migration (D369 M4.2e and subsequent phases) is moving consumers onto progression plus typed `fact.*` tables; M4.4 is the planned envelope drop after the migration completes.

Per-table, per-column, per-index, and per-constraint detail will live in the Data Dictionary reference (`docs/data-dictionary/`, queued; auto-generated from the DDL files in `bc-core/docker/redesign/`). Until the Data Dictionary lands, a reader who needs that detail reads the DDL files directly: `01-platform-schemas.sql` for schema declarations, `02-platform-tables.sql` for platform tables, `03-tenant-db.sql` for tenant tables, `migrations/` for the per-decision migration files.

**Governing source.** `bc-core/docker/redesign/01-platform-schemas.sql`; `bc-core/docker/redesign/02-platform-tables.sql`; `bc-core/docker/redesign/03-tenant-db.sql`.

## Dynamic fact.* Tables

Tenant DB provisioning creates the empty `fact` schema and no tables inside it. Dynamic `fact.*` tables are added later, at Canonical Contract activation, by `SchemaProvisionerService` (per Internal Modules SchemaProvisionerModule). For each activated Canonical Contract, a typed table is generated whose column shape mirrors the contract's Canonical Field bindings. The table name follows the pattern `fact.co_{contract_slug}_{version}` for canonical observations, with progression rows pointing to fact rows by identifier.

The DDL for these dynamic tables is generated by `DdlGeneratorService` (per Internal Modules SchemaProvisionerModule) from the bound Canonical Contract version. Drift is detected by `DriftDetectorService`; the nightly reconciler `NightlyReconcilerService` reapplies the canonical DDL when drift is detected.

The chapter does not enumerate the dynamic fact tables; they vary per tenant and per activated contract. The dynamic-table generation logic and the drift detection semantics belong to the SchemaProvisionerModule chapter at module-internal level (Internal Modules) and to Operating Model Canonical Evaluation at the runtime-act level.

**Governing source.** `bc-core/src/schema-provisioner/`; Internal Modules.

## Indexes and Constraints Discipline

Per rule 7, indexes ship in the same migration as the list endpoint they support. The most common pattern is a multi-column index on `(tenant_id, {time_column})` for tenant-DB boundary tables and `(contract_id, {time_column})` for canonical-evaluation tables. Per-table index and constraint detail will live in the Data Dictionary reference; this chapter records the discipline.

| Discipline | Realization |
|---|---|
| Soft delete | Tables that need a soft-delete state carry `archived_at timestamptz` (nullable; NULL means active). No `is_deleted` columns or `status = 'deleted'` patterns exist in the DDL |
| Temporal validity | Tables that carry temporal validity use `effective_from` (NOT NULL) and `effective_to` (nullable; NULL means currently active) with a CHECK constraint enforcing `effective_to IS NULL OR effective_to > effective_from`. SCD Type 2 uniqueness is enforced by a unique constraint on `(entity_code, effective_from)` |
| FK enforcement mode | Tenant-DB FKs use `ON DELETE RESTRICT` per D232 cross-tenant safety; platform-DB FKs default to RESTRICT unless an explicit cascade is justified by the migration |
| JSONB use | JSONB columns are opaque payloads (contract bodies, evidence envelopes, metric formula computation snapshots), frozen snapshots, or lineage pointers. None are queryable in WHERE, ORDER BY, GROUP BY, or JOIN clauses; queryable values live in their own columns per rule 1 |
| Denormalized counters | None present. Aggregate-table counters (in tables whose purpose is aggregation, like `rejection_summary`) are not denormalized counters per rule 2; that rule forbids denormalization on transactional tables |
| Indexes on master tables | Reference tables in `master` are accessed primarily by primary key; many have no secondary indexes. This is a deliberate exception to rule 7 because the dominant query pattern is PK lookup |

**Governing source.** `bc-core/docker/redesign/`; DEC-1918d0.

## Schema Evolution and Migrations

The `bc-core/docker/redesign/migrations/` directory holds the per-decision migration files that add, alter, or rename objects after the initial DDL was set. Each migration is a single SQL file named for its governing decision: D-code prefix (`d{N}-...`) for migrations before 20260421, date prefix (`YYYYMMDD-...`) for migrations from 20260421 onward (the date prefix supports reorderable application). Reverts ship as paired `.revert.sql` files alongside the forward migration.

The migrations directory is the SSOT for schema evolution. When a migration lands:

1. The migration file is added to `migrations/` and committed.
2. The cumulative DDL files (`01-platform-schemas.sql`, `02-platform-tables.sql`, `03-tenant-db.sql`) are updated so a fresh installation gets the post-migration schema in one pass.
3. The Drizzle definitions in `bc-core/src/database/schema/` are updated to match.
4. The Data Dictionary reference (when built) regenerates from the updated DDL.

Each migration's governing decision is recorded in the migration's filename (D-code or date prefix) and in the corresponding ADR under `docs/adrs/`. The migration list itself is not enumerated here; a reader who needs the full migration list runs `ls bc-core/docker/redesign/migrations/`.

**Governing source.** `bc-core/docker/redesign/migrations/`.

## Drizzle ORM Mirroring

`bc-core/src/database/schema/` holds Drizzle schema definitions that mirror the DDL. The Drizzle definitions are the runtime-side type surface used by repositories. When DDL and Drizzle disagree, the DDL is authoritative; the Drizzle definitions are realigned.

The Drizzle directory is organized by schema. Top-level subdirectories under `src/database/schema/` correspond to platform-side schemas (`master/`, `contract/`, `metric/`, `operations/`, `infrastructure/`, `execution/`, `runtime/`, `source/`, `tenant/`, `support/`, `pricing/`, `users/`, `test-bench/`); a `tenant-db/` subdirectory holds Drizzle definitions for selected tenant-DB schemas (`organization/`, `tenant_dim/`). Other tenant-DB schemas (envelope, progression, fact, evidence, admin) live elsewhere in the tree as the tenant-DB Drizzle layout has evolved. The `concept_registry` schema Drizzle definitions live under `src/database/schema/concept-registry/`. The `bcf` schema Drizzle definitions live under `src/database/schema/bcf/`. Per-schema TS file counts vary as the schema evolves; this chapter does not assert exact counts because the count drifts faster than the chapter can be re-edited. A reader who needs a current count runs `find src/database/schema -name '*.ts' | wc -l` against the live tree.

A planned reorganization per D089 moves Drizzle into `src/database/schema/registry/`; the directory exists but is not yet wired. Active consumers continue to import from `src/database/schema/{schema-name}/` directly.

## Drift Inventory

Per pattern 69 (Foundation-invariant claims require code verification), the gaps between DDL and Drizzle are recorded explicitly here rather than glossed.

| Gap | Severity | Detail |
|---|---|---|
| `metric.metric_knowledge` defined in DDL but no Drizzle TS file found | Low | The DDL declares the table; no `*.ts` file exists in `src/database/schema/metric/` for it. Either the table is unused at runtime (vestigial in DDL) or a Drizzle definition is missing. Closing the gap requires identifying which |
| `master.dim_fiscal_calendar` referenced in tenant DDL as cross-DB soft-ref but no Drizzle TS file found | Low | Cross-DB references are not enforced as FKs (cross-DB FKs are not supported in Postgres); the reference is documentary. The Drizzle absence is consistent with it being a soft-ref, but a Drizzle definition would aid type-safe reads |
| Drizzle `source/` consolidates 6 DDL source tables into 3 TS files | Intentional | `source_catalog.ts` and `source_reference.ts` aggregate the six-tier hierarchy for ergonomic consumption; the underlying tables remain six in the DDL |
| Index naming drift: DDL uses `idx_*` prefix; Drizzle internal naming uses `ix_*` | Cosmetic | Both prefixes are valid Postgres identifier names; no functional impact. The DDL prefix is the canonical declaration; the Drizzle internal name is its representation of the same index |
| `execution.boundary_progression` Drizzle definition in `execution/run-summary.ts` | Cosmetic | The two are the same table; the rename disambiguates from the retired `contract.chain_status`. The Drizzle export is `boundaryProgression` |
| `01-platform-schemas.sql` still says "Platform DB schemas (12)" | Low | The file creates the original 12; `concept_registry`, `bcf`, and `ai_telemetry` are added by migrations. The comment count is stale but harmless — the schemas exist. Updating the base DDL file is queued |
| `contract.l_node_semantic_trace` DDL present but table is historical-only | Low | The trace table was never dropped (only the verdict table was); it remains as a reference artifact with no active writers. Drizzle definitions reference it for read-only historical queries |

The drift inventory is stable as of the survey date; future migrations will either close gaps or surface new ones.

**Governing source.** `bc-core/docker/redesign/`; `bc-core/src/database/schema/`.

## Failure Modes

| Cause | System response |
|---|---|
| DDL change applied but Drizzle definition not updated | TypeScript build fails when a repository reads from the unaligned table; the runtime cannot start until the Drizzle definition is reconciled |
| Drizzle definition added without DDL change | The runtime defines a table type that does not exist in the database; the first query against it returns a relation-does-not-exist error |
| Migration applied to one environment but not another | Schema drift between environments; queries that depend on the migrated table fail in the unmigrated environment |
| Tenant DB provisioning script applied to a database that already has the schema | `CREATE SCHEMA IF NOT EXISTS` and `CREATE TABLE IF NOT EXISTS` make the script idempotent at the schema and table level; column-level changes require an explicit migration |
| Dynamic `fact.*` table generation fails because the bound Canonical Contract is malformed | `DdlGeneratorService` rejects the activation; the contract is not activated; no partial table is created |
| Drift detected by `DriftDetectorService` overnight | The nightly reconciler logs the drift; depending on configuration, it either auto-corrects or surfaces the drift for governed correction |

**Governing source.** `bc-core/src/schema-provisioner/`; Internal Modules.

## Governing Decisions

| Decision | Title | Schema impact |
|---|---|---|
| DEC-1918d0 | Deployment and database architecture; ten normalization rules | The two-database split, the ten DB rules that govern every table |
| DEC-771baf | Tenant database topology; platform-tenant one-way dependency | The one-directional ownership rule that constrains where each table lives |
| DEC-69f09e | ISO 11179 naming convention | Every column, table, index, and constraint name follows the convention |
| DEC-bebaec | Chain completeness SSOT — **retired** | `contract.chain_status` dropped (R3/R6); replaced by `mcf.mcv_chain_status` per DEC-9c0da7. The `execution.boundary_progression` table (renamed from `execution.chain_status` per 2026-05-09 errata) carries per-tenant runtime boundary counts |
| DEC-804874 | L-node semantic verification gate at session close | `contract.l_node_semantic_verdict` dropped (never populated, R3/R6); `contract.l_node_semantic_trace` retained as historical reference. Session-close gate now reads `mcf.mcv_chain_status` per DEC-9c0da7 |
| DEC-9c58c6 | Operating Model section name; fiscal-period rename | The `master.dim_fiscal_period` table is the renamed `fiscal_period` per DEC-9c58c6 |
| DEC-ee6018 | bc-qa standalone repo; QA tooling | The ten DB rules are audited post-hoc by `bc-qa` per DEC-ee6018 |
| DEC-f02230 | Tenant database schema reorganization (D368) | The seven-schema tenant DB layout (envelope, progression, fact, evidence, admin, organization, tenant_dim) per DEC-f02230 |
| DEC-c06f41 | Spine expansion to eight sections plus home | The Data Model and Schema chapter exists in the reshaped Implementation section per DEC-c06f41 |
| DEC-02f5a9 | BCF greenfield registry — Entity/Property/Business Concept model | The `concept_registry` schema (12 tables): characteristic, representation_term, entity, entity_version, business_concept, business_concept_version, alias, entity/bc/characteristic supersession, supersession_proposal, characteristic_definition_amendment |
| DEC-61850f | BCF adoption — semantic_role relocation to BCV | `business_concept_version.semantic_role` column (phase 1+3 migrations); identity_role × semantic_role coherence gate at admission |
| DEC-14f5b6 | Measurement semantics for amount and quantity BCs (D496) | `business_concept_version.measure_class` and `context_concept_id` columns; closed-vocabulary CHECK; coherence CHECK; FK to `concept_registry.business_concept`; partial index on active monetary rows |
| DEC-1fbaf1 | BCF withdrawal ceremony | `archived_at`-based soft-delete on entity, business_concept, characteristic; coherence CHECKs linking lifecycle_state to archived_at |
| DEC-c3e57f | Foundational MCF ADR (Gate M1) | The `mcf` schema (18+ tables): metric_contract through mcv_chain_status. Canonical authority for the live metric stack |
| DEC-9c0da7 | Runtime Spine program (R0–R6) | `mcf.mcv_chain_status` replaces `contract.chain_status` + `contract.l_node_semantic_verdict`; webhook endpoints; reader watermarks; metric value audit; evaluation campaign; envelope schema retirement |

**Governing source.** The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model
- The Contract Grammar
- The Evaluation Boundaries
- The Authority Model
- Operating Model: Overview
- Architecture
- Backend Services
- Internal Modules
- Infrastructure
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-69f09e: ISO 11179 naming convention
- DEC-bebaec: Chain completeness SSOT (retired — replaced by DEC-9c0da7)
- DEC-804874: L-node semantic verification gate (verdict table dropped R3/R6)
- DEC-9c58c6: Operating Model section name; fiscal-period rename
- DEC-ee6018: bc-qa standalone repo
- DEC-f02230: Tenant database schema reorganization
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-02f5a9: BCF greenfield registry
- DEC-61850f: BCF adoption — semantic_role
- DEC-14f5b6: Measurement semantics (D496)
- DEC-1fbaf1: BCF withdrawal ceremony
- DEC-c3e57f: Foundational MCF ADR
- DEC-9c0da7: Runtime Spine program
- BCF Audit Remediation Closeout (`docs/implementation/bcf-audit-remediation-closeout-2026-07-07.md`)
- outline.md §4.3: Implementation
- Decisions: ADR Registry
