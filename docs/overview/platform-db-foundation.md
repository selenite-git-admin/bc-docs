---
id: platform-db-foundation
order: 60
title: "Platform DB Foundation Program"
status: drafting
authority: authoritative
depends_on:
  - platform-overview
governing_sources:
  - "The program requirements / blueprint — docs/implementation/platform-db-foundation-requirements.md"
  - "bc-db: the platform database spine and machinery (DB as a product)"
  - Database Change Protocol
governing_adrs:
  - DEC-b1a286 (The decided platform-database foundation — forward-only migration spine; the waves this program executes)
  - DEC-1918d0 (RDS PostgreSQL decided; Aurora rejected — an engine-portable plain PostgreSQL spine)
  - DEC-75fc71 (Program mandate — execute ADR-b1a286's waves and extend the discipline to tenant DBs, object stores, durability, credentials, capacity)
  - DEC-826390 (Machinery home — dedicated repository bc-db; DB as a product; bc-core is the client)
  - DEC-0e4547 (Operating model — approval-only operator, design briefs, autonomous implementation units, auditor-gated merges)
  - DEC-c99f72 (Platform schema capture authority — reviewed read-only capture under hash-bound written operator authorization)
  - DEC-66d3ca (BC-Agent on-premises appliance tier deferred from the program)
  - DEC-3628b4 (Retire the TSK-3f52d7 schema-acquisition launcher; subsumed into W5)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Platform DB Foundation Program

## Purpose

The Platform DB Foundation Program makes the platform database a **product**: a versioned, releasable spine whose fresh build, its portable dump, and the running database are provably the same artifact — *build-from-scratch == the dump == live, by construction*. It executes the unexecuted waves of the decided foundation (DEC-b1a286) and extends the same source-of-truth, evidence and change discipline to tenant databases, object stores, durability, credentials and capacity (DEC-75fc71).

The program exists because the foundation, while decided, was incomplete and load-bearing: there was no reproducible fresh build, a stale golden dump that was not a source, a handful of ledger records against many forward-migration files, curated content with no versioned source, no proven recovery mechanism, and no source-of-truth decision for tenant databases. The program replaces "the live database is the only truth" with "the spine reproduces the live database, and every change is recorded, reviewed and recoverable."

## The model: DB as a product

- **`bc-db`** owns the schema spine (canonical baseline, forward-only migrations, roles/grants, engine/tool version contract), deterministic master-data seeds, curated-content exports, the DB-management machinery (runner, baseline capture/equivalence, backup/restore, evidence/custody tooling) and immutable release manifests. It is released on its own cadence (DEC-826390).
- **`bc-core`** is the database's primary **client**, not its owner. It consumes the machinery with a declared compatibility range and fails closed on a schema-version mismatch (never exact-version-at-boot).
- **`bc-infra`** is the instance-provisioning layer (per environment).
- The engine is plain, engine-portable **PostgreSQL 17.x** on RDS (DEC-1918d0); repository location never decides SQL privilege or deployment unit.

## Scope matrix

Platform DB (one hosting option) and Tenant DB (BareCount-hosted and BYO-DB; BC-Agent deferred, DEC-66d3ca), each across five data classes: schema, master data, curated content, transactional data, and held/rejected/archived inputs.

## Waves

| Wave | Scope | Status |
|---|---|---|
| **W0** | Program records, custody, version contract | Record work complete; independent closure pending retained coordination-acknowledgement evidence |
| **W1** | Platform migration baseline + forward-only runner + witnessed adoption (units W1.1–W1.6) | **Complete — auditor-accepted (2026-09-15)**; W1.6 (cloud) budget-parked |
| **W2** | Tenant DB source-of-truth, upgrade path, fleet and credentials | Pending product decisions |
| **W3** | Curated-content promotion (versioned source) | Pending |
| **W4** | Transactional durability, object stores, capacity | Pending (budget) |
| **W5** | Cleanup; retirement of superseded acquisition paths (subsumes DEC-3628b4) | Pending |

## What W1 established

W1 built and proved, on the pinned engine, in disposable containers and then on the live local development database:

- **A ratified canonical baseline** — a single reproducible schema artifact with a canonical scoped **parity fingerprint** (`parity_fingerprint/2`). A from-zero build of the baseline reproduces that fingerprint exactly; the fingerprint is the equivalence gate between "built" and "captured."
- **A governed migration ledger** (`infrastructure.schema_migration_event`) — append-only, review-bound, with a governed writer function. Each application is recorded through that writer; for a transactional migration the ledger write and the DDL commit together in one transaction.
- **A forward-only runner** — applies the baseline and forward migrations, recording each through the ledger. Transactional migrations run under a transaction-lifetime advisory lock, with the DDL and its `applied` ledger write atomic in a single transaction. Non-transactional migrations (`CONCURRENTLY` DDL, which cannot run inside a transaction) run under a session-lifetime advisory lock in autocommit, recording durable `attempt` / `complete` / `failed` phases with forward repair rather than an atomic DDL+ledger write. The runner refuses content drift and duplicate/inconsistent records, and never replays an adopted baseline.
- **Backup, restore-drill and recovery-readiness machinery** — a snapshot-bound, credential-free backup whose recoverable form is independently reproduced and verified before a backup is considered a recovery point; parameterized on the source cluster's bootstrap superuser.
- **Witnessed adoption** — the mechanism that records an existing live database onto the spine: under one lock-owning session it measures the live parity against the ratified baseline, and only on an exact match records the baseline as `adopted` (never replaying it). W1 performed the one local-development adoption: the live platform database is now recorded on the spine, and its post-adoption in-scope state matches the value the independent auditor predicted from the migration alone.

## Governance

- The program runs under an **approval-only operating model** (DEC-0e4547): the operator sets high-level direction, and the **builder (Claude) and independent auditor (Codex) hold full architectural responsibility**. Design and delivery proceed as **independently reviewable units** that do not need per-unit operator sign-off — each accepted by the auditor at an exact commit, and reviewed record/documentation and code units merge under the operator's **standing authorization** with green CI. Escalation to the operator is limited to a **genuine unresolved design dispute or Gate ④**; every change touching a database is applied only under the **Database Change Protocol**.
- **Four live gates.** Under the operator's standing authorization, gates ① live capture, ② DDL apply / live adoption, and ③ scope/golden/baseline ratification are **pre-approved within their recorded safeguards** (evidence conditions, machine-evidenced preflight, fail-closed); **only gate ④ — promotion beyond local development — requires direct operator authorization.** Gate ④ has not been exercised.
- Every reviewed artifact and its evidence are held in **byte-immutable custody** in the external audit mirror, independently re-verifiable.

## Where things live

- **Spine + machinery, and the authoritative technical record:** the `bc-db` repository.
- **Program requirements / blueprint:** bc-docs — `docs/implementation/platform-db-foundation-requirements.md`.
- **Decisions:** the ADR Registry (Appendix F), UIDs listed in `governing_adrs` above.
- **Reviewed-unit evidence and custody:** the external audit mirror.

## Later waves and what gates them

The later waves (W2–W5) are not started; each still requires its own design, implementation, evidence and independent acceptance. Under the operator's standing authorization the builder and independent auditor hold **full architectural responsibility**, so the material decisions those waves turn on are resolved as **reviewable proposals in the autonomous builder–auditor design process**, not held for per-unit operator sign-off:

- **Resolved in the design process:** tenant-DB source of truth and BYO-DB posture (D5), hosting-by-environment (D4), curated-content escrow (D9), recovery objectives (D10), data residency (D11), and tenant hosting preference. Escalation to the operator is limited to a genuine unresolved design dispute.
- **Directly the operator's:** the **budget** behind any cloud realization (W1.6 capture/adoption, W4 durability), and **Gate ④** — any promotion beyond local development.
