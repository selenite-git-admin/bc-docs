---
uid: DEC-5c39ea
title: "Golden DB snapshot replaces seed scripts as primary dev setup method"
description: "Dev DB setup uses pg_dump/pg_restore from a golden snapshot instead of running seed scripts. Stored in S3 + local .gitignored dump."
status: implemented
subdomain: dev-tooling
focus: db-bootstrap
date: 2026-03-22
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


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
