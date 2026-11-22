---
uid: DEC-5c39ea
title: "Golden DB snapshot replaces seed scripts as primary dev setup method"
description: "Dev DB setup uses pg_dump/pg_restore from a golden snapshot instead of running seed scripts. Stored in S3 + local .gitignored dump."
status: superseded
superseded_by: DEC-4c1396
subdomain: dev-tooling
focus: db-bootstrap
date: 2026-03-22
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---

> **SUPERSEDED by [DEC-4c1396](ADR-4c1396.md)**, recorded on 2026-11-22 on the owner's approval of desk request 570 (grant GRANT-ID-PENDING-REQUEST-570).
>
> What no longer holds: restoring the golden dump in place into the live platform database (`bc_platform_dev`) as the way to set up or reset it, and making structure changes directly on the live database (the "ALTER TABLE on live DB" step below).
>
> What a reader does instead: every change to the platform database's structure is a bc-db forward migration, reviewed and applied by the bc-db runner, which records each apply in `infrastructure.schema_migration_event` (DEC-4c1396). The golden dump stays an accelerator and recovery artifact, never the authority (DEC-b1a286 clause 6, which amended this record and still stands). It is restored only into a fresh scratch database (bc-core `npm run db:restore:exact -- --target scratch_<name>`, which refuses the platform and tenant databases) or into a disposable container, for proof.
>
> The original text below is kept unchanged as the record of the decision taken on 2026-03-22.

# Golden DB snapshot replaces seed scripts as primary dev setup method

## Context

Seed scripts broke repeatedly when schema changed (column renames, status value changes, constraint updates). Keeping seeds in sync consumed significant session time with zero business value. A golden snapshot eliminates the sync problem — the dump IS the DB, always consistent by definition.

## Decision

Platform DB dev setup uses pg_dump/pg_restore instead of running seed scripts.

- Golden snapshot: `docker/snapshots/golden-platform.dump` (12MB compressed, .gitignored)
- S3 archive: `s3://barecount-dev-artifacts/db-snapshots/golden-platform-{date}.dump`
- Latest pointer: `s3://barecount-dev-artifacts/db-snapshots/golden-platform-latest.dump`
- npm scripts: `db:dump`, `db:restore`, `db:dump:s3`, `db:restore:s3`

Workflow:
- Fresh setup: `npm run db:restore:s3` (pulls latest from S3, restores)
- After schema change: ALTER TABLE on live DB → `npm run db:dump:s3` (new snapshot)
- Seed scripts stay in repo as historical reference, not actively run

Scope: Platform DB only. Tenant DB seeding stays programmatic (simpler, per-tenant).

## Options Considered

N/A

## Consequences

N/A
