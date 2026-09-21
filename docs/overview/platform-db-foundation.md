---
id: platform-db-foundation
order: 60
title: "Platform DB Foundation Program"
status: implemented
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
  - DEC-fbf6ab (Program CLOSED — foundation objectives met, D614)
  - DEC-9dd4eb (Operator formal acceptance of closure; W0/W2 dispositioned, D616)
  - DEC-568d0b (W0 coordination acknowledgement retained — closes the W0 gate)
  - DEC-9b2e64 (W3 closed at the governed vocabulary)
  - DEC-80eade (Legacy metric corpus retirement — W5 drops)
  - DEC-4c1396 (bc-db spine is the sole platform schema authoring/apply path)
  - DEC-615cbd (Operator-backed U7 staging-cloud unit cancellation, D618)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Platform DB Foundation Program

## Program closure (2026-09-21)

**The Platform DB Foundation program is CLOSED — its foundation objectives are met.** The platform database is a governed product: a live, adopted, forward-only spine with a ratified engine-portable baseline, an append-only review-bound change ledger (currently at sequence 27), proven migration/backup/restore/adoption machinery, and the historical wrong turns retired. The provable engineering is complete and independently auditor-accepted. Closure is recorded as **DEC-fbf6ab (D614)** and formally accepted by the operator as **DEC-9dd4eb (D616)**.

What is **not** in scope was designed to hold for a deliberate operator decision and is **not unfinished foundation work**: cloud **standing** go-live (W1.6 realization, W4 durability), the productization gates (D5 BYO-DB, D9 escrow, D10 recovery objectives, D11 residency — legal-gated), and the **Gate ④** production cutover. Closing the program strands none of it: pursuing go-live later reopens a *distinct*, separately-scoped phase, not a debt from this one. Dev stays local at zero standing cost; the staging pilot (u7) was deployed, fully torn down, and its unit formally cancelled by operator decision (**DEC-615cbd / D618**; d597 MSG-473) with verified zero live/billable orphan.

**Each wave's disposition is bound to a retrievable immutable record** (decisions in the ADR Registry; d597 responses byte-immutable on both exchange mirrors):

| Claim | Retrievable evidence |
|---|---|
| W0 closed (coordination acknowledgement retained) | DEC-568d0b (source SES-b5c14b); the gate it satisfies: d597 RESPONSE-148 |
| W1 complete, auditor-accepted (local development) | d597 RESPONSE-147 (W1 exit accepted, 2026-09-15) |
| W2 disposed closed-at-substance (governed) | DEC-9dd4eb / D616 (supersedes the 2026-09-20 session-message basis) |
| W3 closed at the governed vocabulary | DEC-9b2e64 |
| W5 done — legacy `contract.metric_contract*` world drained | DEC-80eade, DEC-4c1396; finale accepted d597 RESPONSE-469 / RESPONSE-471; ledger seq 19–27 |
| Cloud mechanism proven (u1–u6), zero standing cost | DEC-c40e7a; RDS-portable parity `c309ea3d` proven in W1.2/W1.5 (d597 RESPONSE-147) |
| U7 staging cancelled, zero-orphan | DEC-615cbd / D618; d597 MSG-473 (Codex disposition pending) |

**Live end-state (verified read-only 2026-09-21):** `bc_platform_dev` baseline `adopted`, 23 applied ledger events, ledger max seq 27, one unbound event = the documented genesis exemption, engine PostgreSQL 17.11, cluster `7619260324391063586`; the W5 drain removed all 14 ratified legacy `contract.metric_contract*` tables + `tenant.tenant_override` across governed slices whose ledger events (seq 19–27) and finale post-apply parity `8bb2b0b7` are the ones accepted at d597 RESPONSE-469 / RESPONSE-471 (post-drain program check = 0); zero standing `bcp-*` cloud stacks. These abbreviated fingerprints identify the live state; the independently accepted closure package is the set of decision and d597 response records tabulated above.

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
| **W0** | Program records, custody, version contract | **Closed (2026-09-21)** — the retained coordination-acknowledgement evidence that d597 RESPONSE-148 required now exists as an immutable governed record (DEC-568d0b, Platform/Tenant Readiness re-affirmation, source SES-b5c14b); operator accepted W0 closure on it (DEC-9dd4eb / D616) |
| **W1** | Platform migration baseline + forward-only runner + witnessed adoption (units W1.1–W1.6) | **Complete — auditor-accepted (2026-09-15)**; W1.6 (cloud) budget-parked |
| **W2** | Tenant DB source-of-truth, upgrade path, fleet and credentials | **Disposed closed-at-substance** (operator, 2026-09-20); productization gates (D5/D9/D10/D11) deferred to a go-live decision |
| **W3** | Curated-content promotion (versioned source) | **Closed at the governed vocabulary** (DEC-9b2e64); machinery parked, not removed |
| **W4** | Transactional durability, object stores, capacity | Pending (budget) — a go-live decision |
| **W5** | Cleanup; retirement of superseded acquisition paths + the legacy `contract.metric_contract*` world | **Done (2026-09-21)** — 15 tables dropped (14 ratified + `tenant.tenant_override`, ledger seq 19–27), the `docker/redesign` monolith retired, unified authoring path ratified (DEC-4c1396) |

**Cloud realization (DEC-c40e7a).** Units u1–u6 done (RDS PostgreSQL 17 IaC stack + Aurora-construct retirement, schema-apply stage, `cdk deploy`, in-VPC apply + schema-copy drill with the baseline made RDS-portable — NFR-4 proven, parity `c309ea3d`, and credentials/rotation model). Cloud footprint held at zero standing cost; the standing go-live (W1.6/W4) and production cutover (Gate ④) remain a deliberate operator decision.

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

The foundation waves are resolved: W1 complete, W3 closed at the governed vocabulary, W5 (cleanup + legacy-metric retirement) done, and W2 disposed closed-at-substance. What remains is **not further foundation work** — it is the deliberately-deferred go-live track, resolved as reviewable proposals in the autonomous builder–auditor design process where it is engineering, and the operator's where it is budget, legal or production:

- **Resolved in the design process:** tenant-DB source of truth and BYO-DB posture (D5), hosting-by-environment (D4), curated-content escrow (D9), recovery objectives (D10), data residency (D11), and tenant hosting preference. Escalation to the operator is limited to a genuine unresolved design dispute.
- **Directly the operator's:** the **budget** behind any cloud realization (W1.6 capture/adoption, W4 durability), and **Gate ④** — any promotion beyond local development.
