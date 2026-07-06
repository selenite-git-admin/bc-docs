---
id: upgrade-and-migration
order: 33
title: "Upgrade and Migration"
status: drafting
authority: authoritative
depends_on: [the-authority-model, infrastructure, deployment-topology, data-model-and-schema, audit-and-activity-logging]
governing_sources:
  - The Authority Model
  - Infrastructure
  - Deployment Topology
governing_adrs:
  - DEC-3b86ea (Section renames; clean slate migration absorbed into this chapter)
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules)
  - DEC-bebaec (Chain Completeness SSOT; version-aware tracing)
  - DEC-da4c51 (Contract trust chain; upward trust propagation across the contract chain)
errata_referenced: []
v2_sources:
  - sops/clean-slate-migration.md
diagrams: []
---

# Upgrade and Migration

## Scope

This chapter records the operational procedures for moving the platform between schema versions, between contract versions, between major architectural decisions, and through the clean-slate reset path that DEC-3b86ea moved into this chapter. It states the per-migration types (DDL migration, contract migration, contract chain rebuild, golden-snapshot reseed, clean-slate reset, source catalog export), the dependency direction between platform schema migrations and tenant schema migrations, the per-migration evidence the procedure produces, the rollback paths per migration type, and the source catalog export procedure that moves unverified bulk data out of the platform database into MongoDB for SOP-driven re-admission. It records the boundary between Upgrade and Migration and the build-time DDL application (Deployment Topology). It records the as-built drift between the procedure and the platform's current upgrade-and-migration state.

This chapter does not redefine the schema itself (Data Model and Schema in Implementation), the per-contract-family creation procedures (the Onboarding section's contract-creation chapters), or the deploy-time DDL application that runs on first container start (Deployment Topology).

**Governing source.** outline.md §4.7; DEC-3b86ea.

## What the Procedure Produces

A complete upgrade-or-migration cycle produces:

| Artifact | Persistent store | Created by |
|---|---|---|
| Migration SQL file | `bc-core/docker/redesign/migrations/{date}-{ticket}.sql` plus paired `.revert.sql` | The migration author per the migration discipline |
| Updated DDL canonical files | `bc-core/docker/redesign/01-platform-schemas.sql`, `02-platform-tables.sql`, `03-tenant-db.sql` after the migration is folded in | The migration author at fold-in time |
| Updated golden snapshot files | `bc-core/docker/redesign/golden-snapshot-{schema}.sql.gz` | `bc-core/scripts/golden-snapshot.mjs` after material schema change |
| Per-tenant migration application record | `tenant.tenant_migrations` (queued; not yet wired in every per-tenant migration path) | The tenant migration runner |
| Change record (ISO 27001 plan and report) | DevHub `change_record_save` per session UID | The migration session per CLAUDE.md session protocol |

The procedure produces no automatic rollback artifact at runtime; the `.revert.sql` paired file is the rollback path the operator runs manually if needed. The runtime does not auto-revert a migration on failure.

**Governing source.** Data Model and Schema; Infrastructure.

## Migration Types

The chapter records six migration types. Each has its own discipline.

| # | Type | Form | Authority |
|---|---|---|---|
| 1 | DDL migration (additive) | New table, new column, new index; recorded as a migration SQL plus paired `.revert.sql`; folded into the canonical DDL files at the next deploy cycle | Pattern: D162 normalization rules per DEC-1918d0 |
| 2 | DDL migration (breaking) | Column type change, column drop, table drop, FK constraint addition that affects existing rows; same shape as additive plus an explicit data-correctness step | Same authority |
| 3 | Contract migration | Existing contract version superseded by a new active version; runs through `McOnboardingService.createVersion` (or the equivalent service per family) | Per DEC-bebaec; chain status SSOT records the version-aware trace |
| 4 | Contract chain rebuild | The full chain is reseeded after a clean slate; runs through Data Seeding and Build Order (Onboarding) | Per DEC-da4c51 trust chain |
| 5 | Golden-snapshot reseed | The platform database is reset to a known-good golden state via `bc-core/scripts/golden-snapshot.mjs` and the `.sql.gz` files in `bc-core/docker/redesign/` | Snapshot is project-managed; not contract-managed |
| 6 | Clean-slate reset plus source catalog export | Per DEC-3b86ea; export unverified bulk data to MongoDB, flush the contract chain, retain master data, restart from SOP-driven re-entry | This chapter (next section) |

A migration that does not fit one of these six types is outside this chapter's governed type set; new types are added to the table as they surface.

**Governing source.** Data Model and Schema; The Contract Grammar; DEC-3b86ea.

## DDL Migration Discipline

The migration directory `bc-core/docker/redesign/migrations/` holds dated migration SQL files. The naming convention:

```
{YYYYMMDD}-{ticket-or-decision}-{summary}.sql
{YYYYMMDD}-{ticket-or-decision}-{summary}.revert.sql
```

Recent examples in the directory: `20260421-d366-d368-schema-reorg.sql`; `20260421-d366-l-node-semantic-tables.sql`; `d299-bf-alias-table.sql`; `d369-m4-progression.sql`. Each migration is paired with a `.revert.sql` where reversibility is meaningful; some migrations (data corrections, irreversible drops) carry no `.revert.sql`.

The migration discipline:

| Step | Form |
|---|---|
| 1. Author | Migration SQL plus paired `.revert.sql` are written and reviewed |
| 2. Apply locally | The author runs the migration against the local Postgres container; verifies the schema state matches expectations |
| 3. Verify Drizzle alignment | The Drizzle schema definitions in `bc-core/src/database/schema/` are updated to mirror the new DDL state; type compilation must succeed |
| 4. Apply to dev tenant DBs | The migration runs against the local tenant DB (`tbc_sandbox1_dev`) where applicable |
| 5. Fold into canonical DDL | At the next deploy cycle, the migration is folded into the canonical DDL files (`01-platform-schemas.sql`, `02-platform-tables.sql`, `03-tenant-db.sql`); the migration file remains in the `migrations/` directory as a historical record |
| 6. Update golden snapshot | If the schema change is material, the author runs `bc-core/scripts/golden-snapshot.mjs` to produce updated `.sql.gz` files |
| 7. Change record | The migration session writes a DevHub change record (plan and report per CLAUDE.md session protocol) |

A migration that violates step 5 (the canonical DDL is not folded in) leaves the platform with a drift between the migration history and the canonical DDL; the next first-run container initialization replays the canonical DDL but skips the un-folded migration. The fold-in is the discipline that prevents replay drift.

**Governing source.** `bc-core/docker/redesign/migrations/`; `bc-core/scripts/golden-snapshot.mjs`; CLAUDE.md (Database Change Protocol section).

## Contract Migration Discipline

A contract version migration runs through the contract-creation services, not through SQL. The path:

| Step | Form |
|---|---|
| 1. Author the new contract version | New version created via the family's onboarding service (`McOnboardingService.createVersion` for MCs; analogous for SC, AC, OC, CC) |
| 2. Run the family's quality gate | The validation gate runs all checks (e.g., MC validation runs sixteen checks; CC validation runs thirteen) |
| 3. Activate the new version | The version transitions from `draft` to `active` via `POST /api/contracts/{contractId}/versions/{version}/activate` |
| 4. Auto-supersede the prior active version | The chain status SSOT (DEC-bebaec) records the supersession; the prior version transitions to `superseded` |
| 5. Re-evaluate later | If the contract is a CC or MC, the metric engine re-evaluates the affected snapshots at the next scheduled run |

Per DEC-bebaec, the chain status SSOT carries version-aware traces; a later MC that bound to the prior CC version is re-evaluated against the new CC version on the next chain run. The MC Chain Integrity chapter governs the diagnostic that catches mis-bindings the migration may surface.

**Governing source.** The Contract Grammar; DEC-bebaec; MC Chain Integrity.

## Clean-Slate Reset and Source Catalog Export

DEC-3b86ea moved the Clean Slate Migration procedure into this chapter. The procedure is the platform's reset path when bulk-loaded data in the platform database cannot be trusted and the chain needs to rebuild via the SOP-driven re-entry.

The procedure runs in four phases:

| Phase | Action | Reversibility |
|---|---|---|
| Phase 1 | Export source catalog from PostgreSQL to MongoDB `bc_seed` (the six source-side tables: `source_provider`, `source_system`, `source_version`, `source_module`, `source_object`, `source_field`); UUIDs are stripped; the data lands in the MongoDB collections `pg_source_providers`, `pg_source_systems`, etc., as raw reference material for future SOP-driven re-admission | Additive; no data destroyed |
| Phase 2 | Flush contract chain data (Source Contracts, Admission Contracts, Observation Contracts, Canonical Contracts, Metric Contracts, Canonical Mappings, Readers, Reader Flavors, Reader Bindings) from PostgreSQL | Reversible only via golden snapshot restore |
| Phase 3 | Flush source catalog from PostgreSQL (the same six tables Phase 1 exported) | Reversible only via golden snapshot restore |
| Phase 4 | Verify clean state via the chain status SSOT and per-table count queries | Read-only |

**What stays in PostgreSQL after the reset:**

- Master data (functions, subfunctions, industries, currencies, countries, system types)
- Contract meta-schemas (the six locked foundation entries)
- Business Objects, Business Fields, Canonical Fields (the vocabulary substrate that the SOP-driven re-entry will compose against)
- Metric definitions and metric formulas (the metric ecosystem that the new MC creation will bind against)
- Tenant identity, operations, pricing, support data

**What moves to MongoDB:**

The source catalog (six tables listed in Phase 1). The catalog is the substrate the new SOP-driven Source Registration consumes; its presence in MongoDB allows re-admission without re-scraping or re-extracting from authoritative sources.

**What gets deleted (no migration target):**

The contract chain (Source Contracts, Admission Contracts, Observation Contracts, Canonical Contracts, Metric Contracts) plus all version rows. The chain is rebuilt from the SOP-driven path post-reset.

The procedure honors the D268 (session discipline) rule that data without verified provenance is not authoritative; the reset is the path to remove unverified bulk data and rebuild through governed sequences.

**Governing source.** DEC-3b86ea; legacy-v2/docs/sops/clean-slate-migration.md (predecessor SOP).

## Golden-Snapshot Reseed

`bc-core/scripts/golden-snapshot.mjs` produces dump files for the four major schemas (`contract`, `master`, `metric`, `source`) at `bc-core/docker/redesign/golden-snapshot-{schema}.sql.gz`. The snapshot is the project's reference state for re-seeding after a clean-slate reset or for restoring a known-good state during development.

The snapshot is not a backup. It is a project-managed reference state captured at a specific point in time after material enrichment (per CLAUDE.md golden_snapshot memory). Production backups are governed by the database-substrate procedure (Aurora automated backups when the prod posture exists) recorded in Infrastructure when the prod posture lands.

The snapshot is regenerated after material enrichment of the platform vocabulary (BFs, BOs, CFs, contracts) so the next clean-slate reset starts from a richer baseline rather than from empty schemas. The cadence of regeneration is project judgment, not automatic.

**Governing source.** `bc-core/scripts/golden-snapshot.mjs`; `bc-core/docker/redesign/golden-snapshot-*.sql.gz`; CLAUDE.md.

## Per-Tenant Migration Application

When a platform DDL migration affects the tenant schema (`03-tenant-db.sql` changes), every existing tenant database needs the same migration applied. The current procedure:

| Step | Form |
|---|---|
| 1. Apply the platform migration | The new platform DB version reflects the change |
| 2. Apply the tenant migration to each existing tenant DB | The migration script iterates `tenant.tenants` and runs the tenant DDL against each `tbc_{slug}_dev` database |
| 3. Update `seed-tenant-dbs.ts` and `03-tenant-db.sql` | New tenants provisioned after the migration get the new DDL state at provisioning time |

The per-tenant migration runner is not yet a formalized service; it runs as a script per migration. The readiness-baseline local-dev posture uses `sandbox1`, which makes the iteration trivial; at scale (many tenants, prod), the runner needs to be a governed service with concurrency control, per-tenant verification, and an audit trail.

A migration that the runner applies to some tenants but not others leaves the platform with per-tenant schema drift; the chain status SSOT does not catch tenant-DB drift in the readiness baseline. The drift is a queued risk in the per-tenant migration runner formalization.

**Governing source.** `bc-core/src/registry/seed/seed-tenant-dbs.ts`; `bc-core/docker/redesign/03-tenant-db.sql`.

## Failure Modes

| Cause | System response |
|---|---|
| Migration SQL fails partway | Postgres rolls back the transaction (when the migration is in a transaction); operator runs the paired `.revert.sql` to restore the prior state |
| Migration not in transaction (e.g., `CREATE INDEX CONCURRENTLY`) | Failure leaves a partial index; operator runs `DROP INDEX IF EXISTS` and re-runs the migration with the failure cause addressed |
| Drizzle schema not updated to match new DDL | TypeScript compilation fails on next bc-core build; CI catches before the change ships |
| Canonical DDL not folded in after migration | First-run container initialization replays the canonical DDL only; the un-folded migration is missing from new local environments and from the next clean-slate restart; the fold-in discipline catches this |
| Golden snapshot stale after material enrichment | The next clean-slate reset starts from an outdated baseline; the SOP-driven re-entry has more work to do; not a correctness failure but an efficiency one |
| Per-tenant migration applied to some tenants but not others | Per-tenant schema drift; queries that depend on the new schema fail on the un-migrated tenants; current single-tenant posture makes this rare but the risk is real at scale |
| Clean-slate reset run without prior approval | Per CLAUDE.md Database Change Protocol, the reset is a destructive operation requiring explicit user approval; running without approval is a session-discipline violation recorded in the change record |

**Governing source.** `bc-core/docker/redesign/`; CLAUDE.md (Database Change Protocol).

## Drift Inventory

| Drift item | Form |
|---|---|
| Per-tenant migration runner is script-only | Readiness-baseline local-dev posture uses `sandbox1`; runner is a script per migration; formalization queued |
| Golden snapshot regeneration is manual | Project judgment when to regenerate; no automation; CLAUDE.md memory file `golden_snapshot.md` records when last regenerated |
| Clean-slate reset has no automated trigger | Operator-initiated only; the discipline is to confirm with the founder per CLAUDE.md before running |
| Migration history vs canonical DDL drift | A migration not folded into the canonical DDL is missed by first-run initialization; the fold-in is the discipline that prevents this; no automated check in the readiness baseline |
| `tenant.tenant_migrations` table not yet wired | A planned audit row per tenant per migration applied; not implemented in the readiness baseline; per-tenant migration is recorded in the migration script's run log only |
| Aurora automated backups not provisioned | The dormant `PlatformInfraStack` `aurora-postgres.ts` construct configures environment-specific backup retention but the stack is not deployed; no automated production backup posture exists in the readiness baseline |
| `04-tbc-selenite-missing-tables.sql` is a one-off correction | A historical correction file in `bc-core/docker/redesign/` that fixed a specific tenant's missing tables; not part of the canonical first-run initialization; recorded here as a known historical artifact |

**Governing source.** `bc-core/docker/redesign/`; Audit and Activity Logging.

## Boundary with Other Operations Chapters

| Chapter | Relationship |
|---|---|
| Tenant Lifecycle and Subscription | Owns the Subscription artifact; this chapter migrates the artifact's schema when the migration touches `tenant.subscription` |
| Deployment Topology | Owns the deploy-time DDL application on first container start; this chapter owns the migration cycle that produces new DDL |
| Security Operations | Owns the secrets-rotation procedure when migrations touch the secrets surface |
| Observability and Telemetry | Owns the migration-event log that records when a migration ran and what it touched |
| Performance and Scale | Owns the impact-assessment of a migration on query plans, index sizes, vacuum cadence |
| Incident and Change Management | Owns the change-record substrate that records each migration as a governed change event |
| Support and Escalation | Owns the customer-side communication when a migration affects tenant data structure |

**Governing source.** The owning Operations chapters; outline.md §4.7.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-3b86ea | Establishes the section rename (Onboarding, Operations) and explicitly moves Clean Slate Migration into this Upgrade and Migration chapter |
| DEC-1918d0 | Establishes the deployment and database architecture; the ten normalization rules govern the DDL migrations this chapter produces |
| DEC-bebaec | Establishes the chain completeness SSOT with version-aware tracing; the contract migration procedure honors the version model |
| DEC-da4c51 | Establishes the contract trust chain with upward trust propagation; the contract chain rebuild after a clean-slate reset honors the trust progression |

**Governing source.** Decisions: ADR Registry.

## References

- The Authority Model
- Infrastructure
- Deployment Topology
- Data Model and Schema
- Audit and Activity Logging
- Tenant Lifecycle and Subscription
- Security Operations
- Observability and Telemetry
- Performance and Scale
- Incident and Change Management
- Support and Escalation
- MC Chain Integrity
- DEC-3b86ea: Section renames; clean slate migration absorbed into this chapter
- DEC-1918d0: Deployment and database architecture; ten normalization rules
- DEC-bebaec: Chain Completeness SSOT
- DEC-da4c51: Contract trust chain
- `bc-core/docker/redesign/migrations/`
- `bc-core/docker/redesign/01-platform-schemas.sql`
- `bc-core/docker/redesign/02-platform-tables.sql`
- `bc-core/docker/redesign/03-tenant-db.sql`
- `bc-core/scripts/golden-snapshot.mjs`
- `bc-core/src/registry/seed/seed-tenant-dbs.ts`
- legacy-v2/docs/sops/clean-slate-migration.md (predecessor SOP)
- outline.md §4.7: Operations


