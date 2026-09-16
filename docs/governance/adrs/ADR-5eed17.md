---
uid: DEC-5eed17
title: "Master-data seeding through the spine"
description: "Deterministic master data (e.g. the Free pricing package) is seeded by idempotent forward migrations on the same governed spine — not a separate mechanism, an app-startup seed, or a direct insert — so build == dump == live holds for data-of-record."
status: proposed
subdomain: spine
focus: master-data-seed
date: 2026-09-16
project: platform
domain: platform
refs:
  - type: decision
    uid: DEC-b1a286
    label: "Schema source of truth — live DB is ground truth; docker/redesign is the change mechanism"
  - type: decision
    uid: DEC-7df811
    label: "Tenant onboarding state model — the flow needs the single flat Free package present"
---

# Master-data seeding through the spine

## Context

Some platform tables hold **master data / data-of-record** — reference catalogs the system needs before any tenant activity: the pricing package catalog (`pricing.package`), enumerations, and similar. The tenant-onboarding flow requires the single flat **`Free`** pricing package to exist and be `active` so the intake tier-picker has something to offer; the onboarding design states it must be "seeded as deterministic master data through the spine, not a direct insert."

The Platform DB Foundation program has, to date, a spine of **DDL forward migrations** only (`bc-db migrations/NNNN_*.sql`), applied by the runner, recorded in the migration ledger, hash-pinned, reviewed at an exact head, and adopted live under a witnessed gate. There is **no master-data seed mechanism**. A decision is needed on how master data is seeded so that the program's core property — **build == dump == live** — holds for data-of-record, not only for schema.

## Decision

Master data is seeded by **forward migrations on the same spine**, using the identical runner, ledger, hash-pinning, plane model, and reviewed-at-exact-head governance as DDL migrations — carrying idempotent **data** statements instead of DDL. No new seed subsystem is introduced.

A **seed migration**:

1. Is an ordinary numbered forward migration file (`NNNN_seed_<name>.sql`), transactional, in the appropriate plane for the table it writes, and header-marked as a seed (a `-- kind: seed` line) so a reviewer sees at a glance that it carries data, not DDL.
2. Uses **idempotent, deterministic** writes: `INSERT ... ON CONFLICT (<natural key>) DO NOTHING`, with **fixed primary keys and fixed column values** (never `gen_random_uuid()` / `now()` / random for any identity or seeded value) so the seeded rows are byte-identical in every environment and reproducible from source. A seed never `UPDATE`-overwrites operator-editable columns — post-seed edits are operational state the seed must not clobber.
3. Seeds only **reference / master-data** tables (catalogs, bands, enumerations). It never writes tenant, transactional, or per-customer data.
4. Is applied and adopted through the **identical governed path** — runner apply, ledger record, and (for the live platform DB) a witnessed Gate-② step — and once adopted is part of the golden baseline. Thus build == dump == live extends to master data: what a from-zero build produces, what a backup restores, and what runs live are the same seeded rows.

## Alternatives considered

- **A separate seed subsystem** (a distinct seed runner / registry) — rejected. It is a second mechanism to build, govern, digest-bind, and keep in lockstep with the migration spine; it splits the "one governed spine" model and adds surface for drift, for no capability the migration path lacks.
- **Direct inserts** by an operator or ad-hoc script — rejected. Not governed, not reproducible, not part of build == dump == live. This is precisely the ad-hoc pattern the program exists to retire.
- **Application-startup seeding** (the app inserts master data on boot) — rejected. It couples data-of-record to application deploys, is not digest-bound or independently reviewable, and races/duplicates across multiple instances.

## Not decided here

- The concrete **`Free` package seed migration** — its exact bytes, its fixed `package_id`, and its live Gate-② application — is a separate reviewed unit built once this mechanism is accepted.
- **Ongoing changes** to operator-editable master data after it is seeded are operational (through the normal admin surfaces), not seeds; a seed establishes the initial deterministic row and never fights operator edits.
- Whether any *tenant-database* master data is seeded the same way is out of scope here (this ADR is the platform spine); it would follow the same principle if needed, decided in the tenant-database units.

## First application

The single flat **`Free`** pricing package (`pricing.package`): `package_name = 'Free'` (the unique natural key), `status_code = 'active'`, a fixed `tier_order`, and a fixed `package_id`, inserted idempotently. This is the v1 single-band catalog the onboarding intake picker offers; real bands and billing arrive later under the subscription authority (DEC-7df811 §Subscription).

## Consequences

1. Master data is **versioned, reproducible, and independently audited on the same spine** as schema — one mechanism, one application path, one review flow.
2. `build == dump == live` covers data-of-record, not just DDL: a from-zero rebuild and a restored backup both contain the seeded rows, and the live DB reaches them only through the witnessed gate.
3. Seed migrations are clearly marked (`-- kind: seed`), idempotent, and deterministic, so re-runs are safe and cross-environment rows are identical.
4. No new subsystem is added; the intake tier-picker gains an `active` package to offer once the first seed lands.
