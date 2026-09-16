---
uid: DEC-5eed17
title: "Master-data seeding through the spine"
description: "Deterministic master data (e.g. the Free pricing package) is seeded by idempotent forward migrations on the same governed spine — not a separate mechanism, an app-startup seed, or a direct insert — so build == dump == live holds for data-of-record."
status: decided
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
2. Declares, for each seeded row, two field classes:
   - **Seed-owned invariant fields** — the natural key, the fixed primary key, and every column whose value *defines the seeded identity* (for the Free package: `package_id`, `package_name`, `status_code`, `tier_order`). The seed writes fixed, deterministic values for these (never `gen_random_uuid()` / `now()` / random), so they are byte-identical in every environment and reproducible from source.
   - **Operator-editable fields** — columns an operator may later change through admin surfaces (e.g. `display_name`, `description_text`, `tags`). The seed sets an initial value but **never overwrites** them on a rerun; post-seed edits are operational state the seed must not clobber.
3. Is **fail-closed on divergence** — this is the load-bearing rule. `ON CONFLICT (<natural key>) DO NOTHING` alone is **insufficient**: if a row already exists under the natural key but carries a *different primary key or different seed-owned invariant value*, `DO NOTHING` succeeds silently and the migration records its hash in the ledger, while environments now hold *different* data — silently breaking build == dump == live. Therefore a seed migration, **in the same transaction**, after the idempotent insert, **verifies** that the row under the natural key matches the seed's declared invariant fields exactly, and **RAISES (rolls back, nothing recorded)** on any mismatch. This verification is a **machine-verifiable postcondition** carried in the seed file (e.g. an `ASSERT`/`RAISE`-on-mismatch guard); the runner/validator accepts a seed migration only when it carries this fail-closed form. A convergent rerun (identical row) is a no-op; a divergent existing row fails the migration.
4. Seeds only **reference / master-data** tables (catalogs, bands, enumerations). It never writes tenant, transactional, or per-customer data.
5. Is applied and adopted through the **identical governed path** — runner apply, ledger record, and (for the live platform DB) a witnessed Gate-② step — and once adopted is part of the golden baseline. Thus build == dump == live extends to master data: what a from-zero build produces, what a backup restores, and what runs live are the same seeded rows *and* any divergence is refused rather than silently absorbed.

## Alternatives considered

- **A separate seed subsystem** (a distinct seed runner / registry) — rejected. It is a second mechanism to build, govern, digest-bind, and keep in lockstep with the migration spine; it splits the "one governed spine" model and adds surface for drift, for no capability the migration path lacks.
- **Direct inserts** by an operator or ad-hoc script — rejected. Not governed, not reproducible, not part of build == dump == live. This is precisely the ad-hoc pattern the program exists to retire.
- **Application-startup seeding** (the app inserts master data on boot) — rejected. It couples data-of-record to application deploys, is not digest-bound or independently reviewable, and races/duplicates across multiple instances.

## Not decided here

- The concrete **`Free` package seed migration** — its exact bytes, its fixed `package_id`, and its live Gate-② application — is a separate reviewed unit built once this mechanism is accepted.
- **Ongoing changes** to operator-editable master data after it is seeded are operational (through the normal admin surfaces), not seeds; a seed establishes the initial deterministic row and never fights operator edits.
- Whether any *tenant-database* master data is seeded the same way is out of scope here (this ADR is the platform spine); it would follow the same principle if needed, decided in the tenant-database units.

## First application

The single flat **`Free`** pricing package (`pricing.package`), inserted idempotently with the fail-closed verification of rule 3:
- **Seed-owned invariant fields:** `package_name = 'Free'` (natural key), a fixed `package_id`, `status_code = 'active'`, `tier_order = 0`.
- **Operator-editable fields:** `display_name`, `description_text`, `tags` (seeded once, never overwritten).

This is the v1 single-band catalog the onboarding intake picker offers; real bands and billing arrive later under the subscription authority (DEC-7df811 §Subscription). The concrete Free-package unit is a separate reviewed unit and **must prove both**: (a) a convergent rerun is a no-op, and (b) a divergent existing row (a `Free` row with a different `package_id` or invariant value) makes the migration **fail closed** rather than silently record as applied.

## Consequences

1. Master data is **versioned, reproducible, and independently audited on the same spine** as schema — one mechanism, one application path, one review flow.
2. `build == dump == live` covers data-of-record, not just DDL: a from-zero rebuild and a restored backup both contain the seeded rows; the live DB reaches them only through the witnessed gate; and any **divergence is refused (fail closed), never silently absorbed** — the guarantee is enforced, not assumed.
3. Seed migrations are clearly marked (`-- kind: seed`), idempotent, deterministic, and carry a machine-verifiable fail-closed postcondition distinguishing seed-owned invariant fields from operator-editable ones; the runner/validator accepts only this form.
4. No new subsystem is added; the intake tier-picker gains an `active` package to offer once the first seed lands.
