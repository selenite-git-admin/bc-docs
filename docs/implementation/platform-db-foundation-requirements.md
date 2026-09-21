---
id: platform-db-foundation-requirements
order: 62
title: "Platform DB Foundation — Requirements and Technical Design"
status: implemented
authority: authoritative
depends_on:
  - platform-db-foundation
governing_sources:
  - "Platform DB Foundation Program overview (docs/overview/platform-db-foundation.md)"
  - "ADR-b1a286 — the governing bootstrap source-of-truth decision"
  - "bc-db: the platform database spine and machinery"
governing_adrs:
  - DEC-b1a286 (Database bootstrap source-of-truth model — the governing decision)
  - DEC-75fc71 (Program mandate)
  - DEC-826390 (Machinery home bc-db)
  - DEC-1918d0 (RDS PostgreSQL deployment/architecture)
provenance: "Migrated verbatim from bc-core docs/design/platform-db-foundation-requirements.md, v0.7 at commit 2407b04b (retrievable historical revision), consolidated into bc-docs per the documentation-home policy. FR/NFR substance unchanged; only the §1.1 program-status re-anchor, the status metadata row, the §11 W0 exit-row State, the §13.4 status pointer and this front matter were reconciled to the landed state (originally d597 RESPONSE-148; program-closure reconciliation 2026-09-21, binding DEC-fbf6ab / DEC-9dd4eb / DEC-568d0b / DEC-9b2e64 / DEC-80eade / DEC-4c1396 and d597 RESPONSE-147 / RESPONSE-469 / RESPONSE-471)."
errata_referenced: []
v2_sources: []
diagrams: []
---

# Platform Database Foundation — Requirements and Technical Design

| | |
|---|---|
| **Status** | Migrated into bc-docs (documentation-home policy) from bc-core `docs/design/platform-db-foundation-requirements.md` v0.7 (`2407b04b`, the retrievable historical revision). FR/NFR substance is unchanged from v0.7; only §1.1, this row and the front matter were reconciled to the landed state (originally d597 RESPONSE-148; program-closure reconciliation 2026-09-21). **Current program status (2026-09-21): the Platform DB Foundation program is CLOSED** — foundation objectives met and independently auditor-accepted (program closure DEC-fbf6ab / D614; operator formal acceptance DEC-9dd4eb / D616). W1 auditor-accepted for local development (2026-09-15, d597 RESPONSE-147). **W0 CLOSED** — the retained coordination-acknowledgement evidence that d597 RESPONSE-148 required now exists as an immutable governed record (DEC-568d0b, from the Platform/Tenant Readiness session, source SES-b5c14b), resolving the "conversation-only" gap; the operator accepted W0 closure on it (DEC-9dd4eb). **W2** disposed closed-at-substance as a governed decision (DEC-9dd4eb, superseding the 2026-09-20 session-message basis); **W3** closed at the governed vocabulary (DEC-9b2e64); **W5** done — legacy `contract.metric_contract*` world drained (DEC-80eade / DEC-4c1396; d597 RESPONSE-469 / RESPONSE-471; ledger seq 19–27). The go-live track (W1.6/W4 cloud realization, productization gates D5/D9/D10/D11, Gate ④) is a separate deferred phase, not unfinished foundation work. Acceptance of this document ratifies no recovery objective (D10), baseline or wave design; those remain their own records. |
| **Program** | Platform DB Foundation Program (DevHub TSK-cc348a) |
| **Governing decision** | ADR-b1a286 *Database bootstrap source-of-truth model* (2026-08-24) |
| **Evidence base** | `docs/design/db-schema-foundation-study.md` — accepted by the independent auditor and merged to `main` (commit `3e7a69d7`); see Appendix A for what it covers and Appendix E for the provenance of claims added since |
| **Authorizes** | Nothing. This document proposes; every implementation wave is separately reviewed and gated by the Database Change Protocol; merge of this document is the operator's act. *(v0.7 wording, retained as provenance; superseded — see §1.1 "Operating authority (current)".)* |
| **Date** | 2026-09-09 |

---

## 1. Executive summary

BareCount's platform database is the system of record for everything the platform *knows*: its schema, its master data, its curated catalogs and contracts, and — as tenants go live — their transactional data and the inputs it holds, rejects or archives. Today that database cannot be rebuilt from source. The two documented ways to build it fresh both fail on the first run; the golden backup in S3 is five and a half months old; the migration ledger records nine applications against roughly one hundred and forty forward migration files on disk (what else was applied is not proven either way); and the platform's most valuable content — metric definitions, business concepts, the metric directory — has no versioned source; the copies we know of are the live database and that stale backup.

This is not because nobody decided how the database should work. The decision exists: ADR-b1a286 (August 2026) declares, layer by layer, what the source of truth is and names the implementation waves needed to make that true. One of those waves — safe restore into disposable scratch databases — is implemented; the rest are not. This document is the plan to execute them, and to extend the same discipline to what b1a286 does not cover: the tenant databases, the object stores the platform uses for held and rejected inputs, durability, credentials, and capacity.

The program runs in five waves under an operating model designed for a one-person company: the operator approves this document, each wave's short design brief, and any application to a live database — nothing else. Implementation runs against machine-checkable acceptance criteria and is reviewed by the independent auditor at exact commits. The end state is simple to state: **any environment can be built from source, what is built can be proven equal to what is running, and the platform can be recovered — or rebuilt elsewhere — from what is versioned and backed up.**

### 1.1 Program status — re-anchor 2026-09-15; program-closure reconciliation 2026-09-21

This reconciles status against what has landed. It updates status only; **no requirement (FR/NFR) text below is changed** (d597 RESPONSE-148). **As of 2026-09-21 the Platform DB Foundation program is CLOSED** — the foundation waves are resolved (W1 accepted, W3 closed, W5 done, W2 disposed) and the remaining work is the deliberately-deferred go-live track, not open foundation debt; see the Status row above and the closure statement at the end of this section. Ground truth: `selenite-git-admin/bc-db` `main` at `6f103d9` (through PR #25) for the W1 exit; the W5 drain advanced the live ledger to seq 27. Gate ③ (baseline ratification) was crossed once under operator authorization; **gate ② was crossed** for the accepted local-development witnessed adoption (below) and, subsequently, for the W5 legacy-table DROP slices (ledger seq 19–27, d597 RESPONSE-469 / RESPONSE-471); no gate ④ has been crossed (no promotion beyond local development).

**W0 — bind governing records.** D1 (mandate, DEC-75fc71), D2 (bc-docs PR #15 custody), D3 (`bc-db`, DEC-826390), D6 (BC-Agent deferral, DEC-66d3ca), D7 (launcher retired, DEC-3628b4), D8 (operating model, DEC-0e4547), D12 (capture authority = B, DEC-c99f72), D13 (CI engine pin) all ratified. **State (2026-09-21): CLOSED.** The retained coordination-acknowledgement evidence that d597 RESPONSE-148 required now exists as an immutable governed record — **DEC-568d0b** (Platform/Tenant Readiness re-affirmation, source session SES-b5c14b), which resolves the "conversation-only" gap that had held W0 open (§13.4) — and the operator accepted W0 closure on that record (**DEC-9dd4eb / D616**). This supersedes the earlier "record work complete; acknowledgement reported; independently verified closure pending retained evidence" state.

**W1 — migration baseline + runner + witnessed adoption: COMPLETE, auditor-accepted for local development (2026-09-15, d597 RESPONSE-147).**
- **W1.1** (custody, scope, capture design; engine/tool version contract, NFR-4) — **done.** Engine was pinned `postgres:17.8-alpine` and subsequently bumped to `postgres:17.11-alpine` (CVE-2026-18408) in `versions/contract.json`, proven in CI; capture tool live; first live read-only capture custody-verified. The live development database remains 17.8, and the ratified parity fingerprint `c309ea3d…` reproduces identically on both engines.
- **W1.2** (canonical baseline, mapping, equivalence gate; FR-4/6/7, FR-4b interim) — **done and ratified (gate ③).** Baseline sha256 `e16f501e…` (3539 statements; parity fingerprint `c309ea3d…`); from-zero build passes the equivalence gate in CI; the two bootstrap defects (FR-7) corrected; scratch dropped under operator authorization.
- **W1.3** (runner, roles/grants, release manifest, runtime contract; FR-2/3/5/14/17/23, NFR-8) — **done** (a forward-only runner + ledger writer, b apply planes + spine roles `0002`, c non-transactional `CONCURRENTLY` path + non-txn ledger `0003`, d release manifest + runtime schema contract). W1.3-e (witnessed adoption) folded into W1.5 by operator decision.
- **W1.4** (minimum recovery for the platform DB + recoverable-unit definition; NFR-5 minimum, FR-26) — **done** (a–d merged): backup capture (single lock-owning control session, snapshot-bound cutoff, no-credential globals, tablespace preflight) + per-category retention; scheduler-independent bound monitor; restore-drill + parity verification against the snapshot-bound recoverable form; recoverable-unit definition + fail-closed readiness predicate. The recoverable-form/restore path is parameterized on the source cluster's bootstrap superuser.
- **W1.5** (live adoption of the development database under DBCP, gate ②) — **done.** After a machine-evidenced local preflight (verified backup + restore-drill + recovery-readiness + live parity `c309ea3d…`), one lock-owning control session / one repeatable-read transaction re-measured `c309ea3d…`, applied the reviewed additive `0004` ledger-vocabulary migration, and recorded `0004 applied` then `0000_baseline adopted` atomically (ledger 9→11; no baseline replay). Post-`0004` in-scope canonical parity `1af439cc…`, matching the value the independent auditor predicted from the migration alone. Independently accepted (d597 RESPONSE-147).
- **W1.6** (cloud realization of the version contract + bc-infra realignment, §8.6) — **not started**; selected only when a budgeted cloud profile is approved (D4). It is not part of the accepted local W1 exit.

**W1 exit status: ACCEPTED for local development** (d597 RESPONSE-147). Pinned/proven engine ✓, from-zero equivalence ✓, runner + roles + runtime contract ✓, platform backup/retention/bound-monitor/restore-drill ✓, live adoption witnessed and recorded ✓. The cloud realization (W1.6) remains budget-gated (D4) and is outside this accepted local exit.

**W2–W5 — status as of 2026-09-21 (reconciled from the earlier "not started"; each disposition is bound to its own immutable decision/response record, and none changes an FR/NFR requirement below).** These are resolved; none remains open foundation work.
- **W2 — disposed closed-at-substance** as a governed decision (**DEC-9dd4eb / D616**, superseding the 2026-09-20 session-message basis). Its productization inputs — D4 (hosting-by-environment), D5 (BYO-DB posture) — and the tenant-onboarding immutable-version dependency (open question 8) are deferred to a go-live decision; the tenant/W2 convergence dependency is recorded in DEC-568d0b, tracked as a dependency, not a block.
- **W3 — closed at the governed vocabulary** (**DEC-9b2e64**); the content-promotion machinery is parked, not removed.
- **W4 — deferred** to a budgeted go-live decision (transactional durability, object stores, capacity).
- **W5 — done** (2026-09-21): the superseded acquisition paths were retired and the legacy `contract.metric_contract*` world drained under **DEC-80eade** and **DEC-4c1396** — 15 tables dropped across governed slices (14 ratified + `tenant.tenant_override`; ledger seq 19–27; finale accepted at d597 RESPONSE-469 / RESPONSE-471), the `docker/redesign` monolith retired, and the unified authoring path ratified.

**Anchoring notes:**
1. *NFR-5(a) "tested schedule".* The capture **mechanism** and **retention** policy (W1.4) are not a running scheduler. The schedule's automated realization is environment-bound and lands with deployment (W1.6 for cloud; a documented, CI-exercised invocation locally), while enforcement of the recovery bound rests on the **scheduler-independent monitor** (W1.4-b, NFR-5(c)) — which by design detects a silently-stopped scheduler through the age of the newest verified backup, not through a job-failure event. This matches NFR-5(c)'s intent and the "dev, single actor, one-time" scope.
2. *FR-26 staging.* W1.4-d defines the recoverable unit and W1.4-c drills it for the **platform DB**; the tenant supported-profile service drill remains W2 and the all-profiles/account-loss drill remains W4, exactly as FR-26/NFR-5 stage them.
3. *Retained threads.* The FR-4b interim rule (modular edited / monolith kept in lockstep, checked by the equivalence gate) stands until W5. The retained adoption WIP (former bc-db PR #18) was superseded by the merged W1.5 and closed; bc-core PR #753 (FR-4b lockstep) status is tracked separately.

**Operating authority (current) — supersedes the v0.7 operating-model wording retained elsewhere in this document.** Under the operator's standing autonomy authorization (the program operating model, DEC-0e4547, and its standing-authority extension): the operator sets high-level direction, and **the builder (Claude) and the independent auditor (Codex) hold full architectural responsibility**. The material decisions the later waves turn on — including D4, D5, D9, D10, D11 — are resolved as **reviewable proposals in the autonomous builder–auditor design process**, not held for per-unit operator sign-off; each design brief and implementation unit is accepted by the **independent auditor** at an exact commit, and reviewed record/documentation and code units **merge under the operator's standing authorization** with green CI. **Escalation to the operator is limited to a genuine unresolved design dispute or Gate ④.** **Live gates:** ① live capture, ② DDL apply / live adoption, and ③ scope/golden/baseline ratification are **pre-approved within their recorded safeguards** (evidence conditions, machine-evidenced preflight, fail-closed, ledger-recorded); **only gate ④ — promotion beyond local development — requires direct operator authorization** (it has not been exercised). The operating-model wording carried verbatim from v0.7 elsewhere in this migrated document — the *Authorizes* row above, §1's "the operator approves … each wave's short design brief … nothing else," §4's "the operator approves; the operator does not operate," §9's "four operator-only gates," and §13 — is retained as historical provenance and is superseded by this note.

## 2. Background

### 2.1 What the platform database is

BareCount runs one **platform database** (`bc_platform_dev` in development; the same shape in every environment) and one **tenant database per customer** (`tbc_<slug>_<env>`). The platform database holds the control plane: source catalogs, contracts and their versions, metric definitions and the metric directory, business-concept vocabularies, master data, the tenant registry, and operational ledgers. A tenant database holds that customer's data: boundary events, typed fact tables, evidence chains, metric snapshots, and the tenant's own master data. Around both sit **object stores** — S3 buckets the application writes to for the evidence archive, the progression (raw-payload) archive and privacy nullification, each named by an environment variable or a hard-coded default.

The two databases are deliberately separated (ADR-771baf, D575): the platform owns all contracts; the tenant owns all data; the served API never holds a credential that can alter a tenant's schema — only a separate owner-plane worker can.

### 2.2 How the database is built today

Six things each describe or produce the platform schema, and none is derived from another:

1. **The live database** — declared by b1a286 to be the authority on *current state*.
2. **A folder of SQL files** (`docker/redesign/`): a base schema file, a hand-maintained "monolith" of base tables, a modular set of the same base tables split by schema, further numbered files, and a `migrations/` folder of 262 SQL files (140 forward, 122 rollback). b1a286 declares the modular set the authoritative *source* for base tables and the ordered migrations the authoritative *mechanism* for changing the schema, each application recorded in a ledger table.
3. **The migration ledger** (`infrastructure.schema_migration_event`) — an append-only event log. It currently holds nine events.
4. **The application's type definitions** (Drizzle): a type surface derived from the database, not a schema authority; its own migration mechanism was abandoned.
5. **A golden `pg_dump`** in S3, restored by `npm run db:restore:s3` — the documented standard bootstrap for a developer. b1a286 declares it an accelerator and recovery artifact, never the logical authority.
6. **Seed pipelines** — `seed:registry` regenerates reference data, source catalogs and contracts from JSON files checked into the repository; b1a286 declares this the generative authority for that content.

For tenant databases, fresh creation is sound: the `POST /tenants` API applies one DDL file and then verifies, fail-closed, that the six expected schemas, the required tables and the evidence-immutability triggers are physically present before the tenant is marked active. Per-contract fact tables are then generated inside the tenant database by the owner-plane worker from the registry, under its own per-command execution fencing. What tenant databases lack is any *upgrade* path for the static schema other than an operator applying hash-bound "apply kits" by hand, one database at a time.

The object stores are decided but not built as a foundation: the write-once archive principle (DEC-14592e), a per-tenant Object-Lock archive bucket created during tenant onboarding (DEC-3ee0f6), S3 as the only opaque-payload store (DEC-95687d) and a quarantine prefix inside that per-tenant bucket for drifted payloads (DEC-29f134) are all decided; no code creates any bucket, and the quarantine route has no implementation at the admission boundary.

### 2.3 How we got here

The schema grew decision by decision. Documents that once described it were archived when the documentation system was migrated and were never carried forward, though live decisions still cite them. The declared source-of-truth model (b1a286) is only two weeks old and is correct; what is missing is most of the work it calls for. The retired external store (Mongo) was an early inbox for collecting unknown data sources instead of CSVs — no design intent — and the role it played by accident is what the held-inputs store in this document replaces by design.

## 3. Problem statement

**The platform database has a decided foundation that is incomplete, and the gap is now load-bearing.**

- **No reproducible fresh build.** A fresh `docker compose up` fails: the mounted base-tables file references a table it never creates. The modular set meant to replace it also fails: one file uses an expression inside a `UNIQUE` constraint, which PostgreSQL rejects.
- **The backup is not a source.** The only golden dump is from March 2026 (the S3 listing proves its date and size; its contents were not inspected by the study). It is not proven to reproduce the current intended state and must not be relied upon without the manifest and equivalence checks this program introduces.
- **Applied history is largely unverified.** The ledger holds nine retained application records; 140 forward migration files exist on disk. Filename inventory, ledger-name matching and proven application history are three different things; only the first two exist today, and neither establishes which of the other files were or were not applied — that verification is pending (FR-5).
- **Curated content has no versioned source.** Metric definitions, the metric directory, business concepts and the concept registry are not regenerable; the copies known to the study are the live database and the stale dump. This is the platform's core value.
- **No recovery mechanism was found.** Within the inspected repositories and records there is no backup schedule, no restore drill, no point-in-time recovery and no retention policy for either database category. Even a single onboarded tenant would be exposed.
- **Held and rejected inputs have no foundation.** Four decisions describe the object stores; none is realized as infrastructure. Buckets are named by environment variables or a hard-coded default, nothing creates them, and the decided quarantine route is unimplemented.
- **Documentation disagrees with the code** on table counts, ports, mounted files, and which type surface is wired.
- **Tenant databases have no source-of-truth decision**, no upgrade engine for their static schema, and no designed credential storage or rotation.
- **Cloud deployment is undefined in code.** The decided target (ECS Fargate + RDS PostgreSQL, DEC-1918d0) is not expressed in the infrastructure repository, whose platform stack still instantiates the *rejected* option (Aurora) on a different PostgreSQL major than development uses.
- **No capacity model.** Read/write ratios, connection budgets and pooling have never been stated; at a hundred tenants the platform database would be hit by a hundred processes' connection pools.

## 4. Goals, non-goals and tenets

### 4.1 Goals

- **G1 — Reproducibility.** Any environment (developer, CI, staging, production, a new tenant) is built from versioned source by one mechanism, and the result is provably equal to the intended state. The human form of this: a new engineer clones the repository, runs one command, and has a working platform database *with content*.
- **G2 — One source of truth per data class.** Schema, master data, curated content, transactional data, and held/rejected/archived inputs each have exactly one declared source and one declared lifecycle.
- **G3 — Evidence for every change.** Every schema change is recorded, reviewable and verifiable after the fact.
- **G4 — Protect the platform's value.** Curated content becomes reproducible, versioned and promotable between environments, with provenance preserved.
- **G5 — Tenant safety.** Tenant databases can be created, upgraded, backed up and restored without data loss, across the hosting options the business sells, with credentials that never leak.
- **G6 — Recoverable, and rebuildable elsewhere.** Data can be recovered from backups within stated objectives, and the whole platform can be rebuilt on any PostgreSQL from what is versioned and escrowed.
- **G7 — Honest documentation.** Documentation is generated from, or continuously checked against, the code and the database.

### 4.2 Non-goals

- Changing the platform/tenant separation, the two-plane identity model, or the evidence-immutability guarantees.
- Redesigning the application's data model or normalization rules.
- Building business continuity (multi-region failover, hot standby) in this program; defining it is in scope, building it is not.
- Running the platform on a second cloud provider.
- Restoring or reviving the retired Mongo store.
- Executing any live acquisition, signature, DDL, backup/restore, ratification or retirement as part of design work.

### 4.3 Tenets

- **AWS-native for hosting; portable by construction.** The production stack is AWS. The spine and content target plain PostgreSQL so the platform can be rebuilt anywhere — that, not a second cloud, is the disaster posture.
- **Local by default; cloud spend is opt-in and budgeted.** Development stays on the operator's machine for as long as that works. No standing cloud spend exists without an approved, budgeted environment profile. Moving an environment to the cloud is a configuration switch, not a project.
- **The operator approves; the operator does not operate.** The operator's role is program and wave-boundary approval, plus any application to a live database. Mechanics never reach the operator.
- **Small units, exact commits.** Each wave is a sequence of independently reviewable units, each with machine-checkable acceptance criteria, accepted by the auditor at an exact commit.
- **Capture is not ratification.** Observing the live state never makes it canonical; a reviewed mapping does.
- **Fail closed, record everything.** No silent fallbacks; every change and every proof leaves evidence.

## 5. Scope

The program is organized as a matrix. **Rows** are the two database categories plus the object stores that belong with them. **Columns** are the hosting options that actually change requirements. **Inside each cell** are five classes of data, each with its own source of truth and lifecycle.

| | **Platform DB** — one hosting option (BareCount-hosted) | **Tenant DB — BareCount-hosted** (AWS Shared / AWS Separate) | **Tenant DB — BYO-DB** (customer-hosted, platform-managed) |
|---|---|---|---|
| **1 · Schema** | Migration spine (W1) | Static baseline + upgrade path; dynamic fact tables stay with the owner worker under a declared contract (W2) | Baseline applied into a customer database; DDL identity and privileges negotiated (W2) |
| **2 · Master data** | Deterministic, digest-bound seeds (W1/W3) | Tenant-authored (`tenant_dim`, `organization`); must survive upgrades (W2) | Same, in the customer's database |
| **3 · Curated content** | Content promotion (W3) — the platform's value core | Not applicable — contracts are platform-owned | Not applicable |
| **4 · Transactional data** | Append-only ledgers; backup and retention (W1 exit, W4) | Immutable evidence, never-ALTER fact tables; backup and retention (W2 exit, W4) | Recovery responsibility to be defined (W2/W4) |
| **5 · Held, rejected and archived inputs** (object stores) | Platform-side archive (W4) | Per-tenant archive bucket with quarantine prefix, created at onboarding (DEC-3ee0f6, DEC-29f134): durability minimum W2, full lifecycle W4 | Per-tenant, placement negotiated at onboarding (DEC-3ee0f6 leaves this to the onboarding record) (W2/W4) |

**Deferred:** the BC-Agent on-premises appliance tier. It is decided in ADR-edd9bb (status "decided", marked evolving) with a design that conflicts with a later operating chapter; the deferral was ratified by the operator on 2026-09-09 as DEC-66d3ca (decision D6): ADR-edd9bb is unchanged, the conflict is parked, and reinstating the tier requires its own record.

**The platform database needs only one hosting option.** No business tier relocates it; its only axis is environment (local → staging → production).

## 6. Current state by data class

### 6.1 Schema

| | Platform DB | Tenant DB |
|---|---|---|
| **Source of truth** | Declared: the modular SQL set for base tables, evolved by ordered migrations (b1a286) | Not declared. One DDL file for fresh creation; migrations applied by hand to existing tenants |
| **Fresh build** | **Broken** (two defects, §3) | **Works** via `POST /tenants` with a verified fail-closed post-condition. The older seed-CLI path only counts tables and still names a schema (`envelope`) that was renamed (`progression`) |
| **Upgrade path** | Manual application of migration files; nine of 140 recorded | Manual per-tenant apply kits for the static schema; dynamic fact tables reconciled by the owner worker; a drift guard exists in tests |
| **Verification** | None from zero; a partial DDL parity test exists in CI for tenant indexes | CI provisions a real tenant and applies real migration files; no full platform parity gate |
| **What is implemented** | The safe-restore wave: an exact-restore tool into disposable scratch databases, fail-closed, tested (PR #713) | The provisioning API and its post-condition probe; dynamic per-contract tables generated from the registry by the owner worker, fenced per provisioning command by a transaction-scoped advisory lock (`ProvisioningExecutionLockService`) |

### 6.2 Master data

Reference data, source catalogs and contracts regenerate from JSON files in the repository (`seed:registry`); this path has no dependency on the retired Mongo store. The genesis vocabulary (26 tables) and date/fiscal dimensions are seeded deterministically and digest-bound. **Gap:** it has never been proven that the live database equals what the seeds would produce.

### 6.3 Curated content

b1a286 itself splits this class. Reference, catalog and contract data (above) have a live, versioned source. **Metrics, the metric directory, business concepts and the concept registry have none.** The BCF OAGIS content was collected through the retired Mongo inbox and mirrored into PostgreSQL; the mirror is the only copy known to the study. Nothing versions, diffs, reviews or promotes this content today. Where content carries certification fields, the sole producer of verified coordinates is the existing feed importer, which validates signatures and registration; nothing else may mint verified state.

### 6.4 Transactional data

Tenant evidence is append-only and hash-chained; typed fact tables are never altered. Platform-side ledgers are append-only. **Gap:** no backup, point-in-time recovery, restore drill or retention policy was found for either category; for a customer-hosted tenant database the recovery responsibility is undefined.

### 6.5 Held, rejected and archived inputs

Three S3 writers exist in the application: the evidence archiver (`BC_EVIDENCE_S3_BUCKET`; disabled when unset; upload failures are logged and swallowed, never raised), the progression archiver (`S3_ARCHIVE_BUCKET`; disabled when unset; best-effort; object key derived from run id, or an hour bucket when no run context exists, so records sharing a run share a key) and the privacy-nullification service (hard-coded default bucket `barecount-data` with the pre-DEC-3ee0f6 `{tenant_id}/archive/…` prefix layout). No bucket is created by bc-infra or by tenant onboarding; the per-tenant Object-Lock bucket decided in DEC-3ee0f6 (`bc-archive-{slug}-{env}`, region `ap-south-1`, COMPLIANCE mode, seven-year default retention, created at onboarding step 3/4 rather than ahead of time) does not exist as code. The quarantine route decided in DEC-29f134 (a `quarantine/` prefix inside that bucket, inheriting its lock and retention; admit-with-flag / quarantine / block per contract policy) has no implementation at the admission boundary. Retention enforcement, provenance linkage, completion linkage between object and database record, and re-admission are undefined. The privacy erasure design (DEC-bd5492: PII registry, sentinel nullification, data-subject requests, retention policies) and source-field PII marking (DEC-490520, DEC-743186) are decided; enforcement across tenant databases and object stores is not part of any provisioning path, and a nullification marker on an object is not physical erasure of a locked version.

### 6.6 Tenant-facing preference surfaces

The tenant portal's screen set (catalogued in the DevHub screen registry; inventory supplied by the tenant-onboarding design session on 2026-09-09, Appendix C; not independently audited) has **no backend for any tenant preference except source connections**. The data-infrastructure cluster — Data Backup, Data Residency, Data Retention, Data Compliance, Data Policies — and the Organization screen's residency and compliance tab promise backup, residency, retention and lifecycle semantics with nothing behind them. These are exactly the promises the foundation cannot yet honor (§6.4, §6.5). The onboarding design under review already treats this as a rule ("the UI only promises what the foundation can honor") and holds those screens; FR-21 makes the rule a requirement. `tenant.tenant_infrastructure` is defined in the DDL (`02-platform-tables/05-tenant.sql:50`, with deployment code, database host, bucket name, region and an approval workflow); its presence in the live database is not established by retained evidence (the study's table inventory counts per schema without naming tables) and is carried as unverified until W1.1 captures it. No writer for it was found in the application, and `POST /tenants` does not populate it.

### 6.7 Credentials, environments and hosting

Tenant database URLs live in environment files; the owner/runtime credential split is enforced in code, but there is no designed storage, per-tenant separation or rotation. Connection pools are capped at ten runtime and four owner connections per tenant per process — lazy upper bounds, not measured utilization. Environments are a naming convention (a database-name suffix) with three other, inconsistent definitions in various records. The infrastructure repository's entry point deploys only the Cognito user-pool stack; its platform stack — not instantiated — still encodes the rejected Aurora construct on PostgreSQL 16 with a single Aurora-managed secret, no S3 bucket and no application secrets (an AWS account inventory was not performed; the claim is about infrastructure code). Development and the live database run PostgreSQL 17.8; CI pins the floating `postgres:17` image tag, not a patch or digest. Connection pooling and read replicas were noted as future work and never designed.

## 7. Requirements

Requirements are numbered for traceability. "Must" is binding on the wave that implements it; "should" is a design preference the wave may trade off with justification.

### 7.1 Functional requirements

| ID | Requirement | Wave |
|---|---|---|
| FR-1 | The platform database **must** be buildable from versioned source into a fresh, empty PostgreSQL instance by a single documented mechanism, in every environment class. | W1 |
| FR-2 | Static schema change **must** be expressed only as forward-only migrations applied by a runner; the runner **must** record every application in the migration ledger with the migration's content hash and review binding. Dynamic per-tenant fact tables are governed by FR-25, not by the runner. | W1 |
| FR-3 | The runner **must** distinguish transactional migrations from approved non-transactional operations (for example `CREATE INDEX CONCURRENTLY`), record attempt and completion separately for the latter, detect partial failure, and define restart and recovery. It **must** use maintenance connections separate from runtime pools, with declared pooling mode, lock and statement timeouts, reconnect behavior, and tests that exercise the exact advisory-lock lifetime (session vs transaction) used by non-transactional migrations. | W1 |
| FR-4 | **Baseline authority contract.** A baseline **must** be produced in three distinguishable steps, each with its own evidence: (a) an *immutable captured observation* of the live schema under an accepted capture authority (FR-4c); (b) a *reviewed canonical baseline* derived from it by a recorded mapping — owned scope (platform vs tenant; auditor and scratch schemas on the shared cluster excluded), approved corrections (including the two bootstrap defects), excluded volatile surfaces, dependency objects (roles, privileges, extensions, content) with their provenance — capturing the live state is never ratification of it; (c) *ratification* of the canonical baseline by the operator under the Database Change Protocol. | W1 |
| FR-4b | **Post-cutoff authority.** After the baseline cutoff, the edited source for base tables remains the modular SQL set (b1a286 clause 4); the monolith is a generated artifact; until the assembly rule is implemented (W5, per DEC-591eb7) the interim rule is *modular edited, monolith regenerated or kept in lockstep and checked by the equivalence gate*. If the program concludes the authority should change, it **must** name the amendment to b1a286 rather than replace it silently. | W1 |
| FR-4c | **Capture authority.** Live schema capture for the baseline **must** run under an accepted gated path: either the existing schema-acquisition launcher package (parked, not retired — its accepted operator-signed path) or a separately reviewed alternative accepted before capture. No waiver follows from this document. | W1 |
| FR-5 | **Adoption predicate.** Existing databases **must** be adopted onto the spine without replaying `CREATE` statements, and only after the target's *measured* schema state and dependency hashes match the approved adoption precondition; any unexplained difference refuses adoption. The ledger entry for adoption **must** be distinguishable from a DDL execution ("witnessed adoption at hash X" vs "applied migration Y") and prior event history **must** be preserved, not rewritten (unrecorded ≠ not applied). | W1 |
| FR-6 | **Schema equivalence** **must** be defined and mechanically checked in CI against immutable reviewed baselines and upgrade paths — never arbitrary live state, never live credentials in pull-request jobs. | W1 |
| FR-7 | The two known bootstrap defects **must** be fixed as approved corrections in the canonical baseline (FR-4b), with tests that would catch their recurrence. | W1 |
| FR-8 | Master data **must** be seeded deterministically from versioned, digest-bound sources; CI **must** prove a fresh build's master data equals the source. | W1 / W3 |
| FR-9 | Tenant databases **must** have a declared source of truth for their static schema and a versioned **upgrade path** that reaches existing tenants without manual per-database application; fresh creation, existing-tenant upgrade and registry-generated dynamic tables **must** be distinguished and each versioned. | W2 |
| FR-10 | The seed-CLI provisioning path **must** enforce the same post-condition as the API path, or be retired. | W2 |
| FR-11 | For customer-hosted (BYO-DB) tenants, the program **must** specify the DDL identity the platform requires, the privileges and extensions the customer must grant, the supported PostgreSQL major, object-store placement, and the recovery responsibility split. Until specified, BYO-DB remains unsupported for provisioning. | W2 |
| FR-12 | Curated content **must** be exportable per collection into a canonical, deterministic, digest-bound, version-controlled form; importable and promotable between environments by the same runner; and CI **must** prove parity per collection against an *authorized, immutable, scoped capture* of live content (consistent with FR-6 — no live credentials in ordinary CI). Provenance and certification fields are carried as evidence with their source identity and digests verified through the governed path; carrying them confers no new trust and cannot mint verified state. | W3 |
| FR-13 | Authoring through the governed UI and panels **must** remain the front door; promotion is the step that exports, reviews and commits what was authored. | W3 |
| FR-14 | The spine and content promotion **must** publish a **version**; consumers **must** declare compatible ranges; rollout **must** support old/new overlap through expand/contract sequencing — not exact-version equality at boot. A schema or content release is not a distributed transaction across the fleet; per-target state is tracked (FR-18). | W1 |
| FR-15 | Environments **must** have one definition, used identically by the application, the infrastructure code and the tooling. | W1 |
| FR-16 | Documentation of schema shape, counts and mounted files **should** be generated from the spine or checked against it in CI. | W5 |
| FR-17 | **Environment promotion.** A change (schema, content, configuration) **must** flow dev → staging → production as the *same immutable release artifact* — a release manifest binding schema, content, configuration and tool versions, compatibility preconditions, and crash-resume / forward-repair criteria — applied to each target with *fresh target-specific* authorization, pre-state and execution evidence. Development authority is never production authority. Secrets never travel in the artifact. | W1 |
| FR-18 | **Tenant fleet operations.** Applying a migration or content promotion to *all* tenants **must** be an orchestrated operation with per-tenant ledger state, partial-failure isolation, per-tenant lag reporting, canaries with stop thresholds, handling of a slow or unreachable tenant, and resumability — not a loop over manual kits. | W2 |
| FR-19 | **Credentials.** Per-tenant database credentials **must** be stored in a secrets manager, separated per tenant into owner and runtime credentials, rotatable, and absent from repositories and environment files in cloud environments. | W2 |
| FR-20 | **Held, rejected and archived inputs.** The object stores **must** be realized as decided — per-tenant Object-Lock bucket created during tenant onboarding with the decided region and retention (DEC-3ee0f6), quarantine as a prefix inside it (DEC-29f134), a platform-side archive bucket — through an infrastructure library invoked by onboarding under an onboarding-scoped role (not ahead-of-time provisioning, not application-held `CreateBucket`). Any change to decided placement, region, retention or lifecycle (for example residency-driven placement) **must** be proposed as an amendment to those decisions (D11), never introduced by requirement. **Delivery contract:** every archived or quarantined object **must** have a stable per-object identity, version and digest; completion linkage to its database record; retry and reconciliation after either side commits; duplicate and replay handling; and tenant isolation — best-effort writes that swallow failures do not satisfy this. **Re-admission** from quarantine **must** revalidate under an identified contract version and emit a new linked event, never overwrite the original or duplicate effects. The interaction of retention and legal holds, nullification markers and restored backups **must** be specified across *all* read and replay paths; a marker is not erasure, and compliance-mode locks prevent deletion before expiry. | W2 (durability minimum) / W4 (full) |
| FR-21 | **Data lifecycle and PII enforcement.** The platform's PII-registry, nullification and data-subject-request policies **must** be enforceable across tenant databases and object stores, and the tenant-facing preference screens (residency, backup, endpoints, lifecycle) **must** only offer what the foundation can honor and enforce. | W2 (study) / W4 |
| FR-22 | **Tenant placement.** The tenant registry **must** record which instance hosts each tenant database, so tenant databases can be distributed across instances without schema change; no cross-database joins. | W2 |
| FR-23 | **Runtime schema contract.** The application and the owner worker **must** verify the published schema/content version and declared capabilities at startup and on a schedule, with an explicit stale/unknown policy, bounded caching (no version query per request), and a drain barrier that prevents incompatible work from starting during a contract migration — refusing or degrading per the compatibility range. | W1 |
| FR-24 | **Production drift observation.** A scheduled, read-only check **must** compare each deployed database against its intended state — for a tenant database, the intended *per-tenant* state including its declared dynamic tables — and report drift; this is distinct from the build-time equivalence gate. Legitimate versioned fact tables are never reported as drift. | W4 |
| FR-25 | **Static / dynamic schema contract.** The runner owns the *static* schema; the owner-plane worker retains authority over *dynamic* per-tenant fact tables generated from the registry, under its existing per-command fencing. The contract **must** specify: a generated-object manifest (name, version, generating contract, digest) per tenant; collision and compatibility rules between static migrations and generated objects; coordinated exclusion when a migration or adoption needs the dynamic path paused (a runner lock alone does not serialize with the worker's locks); and how FR-24 compares against the manifest. | W2 |
| FR-26 | **Recoverable unit.** Recovery **must** be defined as restoring a *consistent unit*: compatible platform and tenant database states, content and contract versions, object references with their object versions or markers, roles and extensions, secrets and key material, in a declared order with validation before service returns. Independent dumps are not automatically a consistent cross-store point; a declared cutoff and reconciliation strategy is required, and cross-store atomicity is never implied. | W1 (defined) / W2 (supported-profile service drill) / W4 (all profiles, account loss) |

### 7.2 Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-1 | **No live mutation without the Database Change Protocol.** Design and study work never alters the live development database. |
| NFR-2 | **Fail-closed.** Every tool refuses on any precondition failure; no silent fallback to a different credential. |
| NFR-3 | **Evidence and custody.** Every change and proof produces retained, hash-bound evidence, hashed as committed bytes; machine evidence is produced by checked-in tooling that records the exact command it executed. |
| NFR-4 | **Engine target pinned and proven.** PostgreSQL 17 today, pinned to an explicit patch or image digest — together with client and tool versions — as a version contract established in W1.1 *before* any equivalence proof or rehearsal, proven in CI, verified compatible with the measured live target before live adoption, and carried in every release manifest; cloud environments realize the same contract when they exist. Portability to a customer-supplied PostgreSQL is evaluated (extensions, roles, privileges), not assumed. |
| NFR-5 | **Recovery, staged with measurable cuts.** *Minimum before any real tenant* (exit criterion for W1 for the platform database and W2 for tenant databases), for each supported hosting profile: (a) an **automated logical backup on a tested schedule** for every platform and tenant database, with a **backup retention policy** (provisional: daily backups retained 30 days, the last backup of each month retained 12 months); (b) **provisional objectives** that D10 may tighten — maximum recoverable age / data-loss window **24 hours**, measured from the backup's *data cutoff* (the snapshot's consistent point), not from job or upload completion; (c) **enforcement of the bound**: a scheduler-independent monitor evaluates the age of the newest *verified* backup for every database continuously, raises a **breach alert at 24 hours** and marks the database *not recovery-ready* (which the tenant-readiness gate reads), with 26 hours as an escalation threshold — so a scheduler that silently stops is detected by the bound itself, not by a failure event; any failed backup also alerts; (d) a **service recovery drill for the supported profile** before real-tenant activation — not a single database restored in isolation: restore the required platform and tenant state, content and contract versions, object versions or markers, and identity/key dependencies under the declared cutoff and reconciliation strategy (FR-26), and validate the service-level result, with a provisional **4-hour** target from decision to validated service; (e) the object-store durability and read/recovery controls for archives whose declared source is an object store (FR-20 durability minimum). Where any part of the minimum is missing for a profile, that profile is held and real-tenant activation is refused by readiness, not by prose. *Full* (W4): point-in-time recovery on managed hosting; account-loss and full-profile exercises through escrow; operator-set objectives per database category (D10); the complete recoverable-unit drill across all profiles. Business continuity (failover) is defined in W4 and built separately. The 24 h / 4 h / retention values are design proposals for the wave brief and gates, not ratified business guarantees. |
| NFR-6 | **Escrow.** Encrypted backups and the content repository **must** be copied outside the primary cloud account on a schedule, with decryption and bootstrap access that does not depend on the lost account (key material escrowed separately — object locks protect objects, not key availability), least-privilege access at the destination, and a recovery drill through that path. |
| NFR-7 | **Independent review.** Each wave's design brief and each implementation unit are reviewed by the independent auditor at an exact commit before merge. |
| NFR-8 | **Least privilege, structurally, with tests.** Named narrow roles for the served API (runtime), the owner worker, the runner and administration, each with its actual capabilities stated and tested; the served API never holds owner credentials and has no DDL capability; all DDL runs under the owner plane or the runner. A grant cannot distinguish an approved API request from arbitrary SQL under the same principal, so "writes only through the API" is enforced by keeping write-capable principals out of any interactive or backdoor path, not claimed as an impossibility. |
| NFR-9 | **Capacity model.** The program **must** state expected read/write ratios per database category (the platform database is a read-dominated control plane; tenant databases carry runtime writes); a connection budget per *physical instance* across tenants × replicas × runtime and owner pools plus migrations, backups and monitoring; bounded active pools with backpressure and noisy-tenant limits; cacheable versioned platform reads; and a synthetic 100-tenant benchmark harness with a defined workload and thresholds, results recorded. Read replicas are deferred until measurements justify them. |
| NFR-10 | **Scale seams preserved.** Nothing in the foundation precludes read replicas, connection pooling, or distributing tenant databases across instances; those are designed seams, not retrofits. |
| NFR-11 | **Observability.** The runner and promotion tooling emit structured logs and metrics for every apply, failure and recovery. |
| NFR-12 | **Cost posture.** Local is the default; no standing cloud spend exists without an approved, budgeted environment profile; non-production cloud environments are opt-in and sized to the smallest viable instance. |

## 8. Proposed architecture

### 8.1 The migration spine

```
 versioned source (git)                                 any environment
 ┌──────────────────────────────┐    runner (owner plane)  ┌───────────────────────┐
 │ 0000_baseline  (canonical,   │ ───────────────────────► │ platform DB           │
 │   from reviewed capture)     │   applies in order,      │  + ledger row per     │
 │ 0001 … NNNN forward migr.    │   records ledger row,    │    applied migration  │
 │ roles/   (grants, privileges)│   promotes content,      │    or witnessed       │
 │ seeds/   (master data)       │   publishes version,     │    adoption           │
 │ content/ (curated exports)   │   emits release manifest │  + content promoted   │
 │ tenant/  (static baseline+   │ ───────────────────────► │ tenant DBs (fleet)    │
 │          upgrades)           │                          │  static: runner       │
 └──────────────────────────────┘                          │  dynamic: owner worker│
                 │                                         └───────────────────────┘
                 ├──── CI: build from zero ── equivalence ──────────┤
                 │     (immutable baselines/captures; no live creds)│
                 └──── escrow: encrypted backups + content + keys ──┘ (off-account)
```

- **Source:** one versioned tree — canonical baseline, forward migrations, roles and grants, master-data seeds, curated-content exports, the tenant static baseline and upgrades.
- **Baseline:** captured once under an accepted capture authority, mapped to a reviewed canonical baseline, ratified; existing databases are adopted by *witnessed adoption* after their measured state matches the precondition (FR-4, FR-5).
- **Runner:** the only thing that changes the *static* schema. Runs under the owner identity on maintenance connections. Records every application in the ledger in the same transaction, or — for approved non-transactional operations — records attempt and completion with recovery semantics. Advisory locking prevents concurrent runs; coordinated exclusion with the owner worker's dynamic path is part of the static/dynamic contract (FR-25). Publishes the schema/content version and a release manifest (FR-17).
- **Equivalence gate:** CI builds from zero and compares to the intended state on defined surfaces. Production **drift observation** is a separate, scheduled, read-only check against the intended per-target state.
- **Golden dump:** demoted to a cache and recovery artifact; regenerated from the spine and proven reproducible before it may be relied upon.
- **Type surface:** the application's Drizzle definitions are regenerated from the database or checked against it.

### 8.2 The DB-management machinery

Designed now, built unit by unit: runner, baseline capture-mapping and equivalence check, content export/import/parity, tenant provisioning and fleet upgrade, backup and restore rehearsal, evidence collection and custody verification, drift observation. It consolidates what already exists in bc-core (the schema comparator, the exact-restore tool, the governed-apply harness, the apply-kit convention, the provisioner, the evidence generator and verifier). It is packaged and **versioned as one unit** with explicit *runtime*, *owner* and *tool* entry points: API imports never pull in owner credentials or cloud administration clients, and compatibility tests cover mixed versions.

**Home — decided by the operator on 2026-09-09 (D3, DEC-826390, versioned in bc-docs at `a9eadc13`): a dedicated repository, `bc-db`**, created the same day as a scaffold (`selenite-git-admin/bc-db`, private; CI quality gate; bc-core-parity branch protection; DevHub project). The spine, seeds, content exports, machinery and release manifests land there wave by wave through reviewed units under the Database Change Protocol; nothing lives there yet. bc-core remains the database's primary *client* and consumes the machinery package with a declared compatibility range (FR-14). The earlier proposed default — a governed package inside bc-core — is superseded by this decision. Repository location never decides SQL privilege or deployment unit; the cross-repository cost is accepted deliberately.

### 8.3 Object stores as a data class

Realized as decided: one Object-Lock bucket per tenant (`bc-archive-{slug}-{env}`, `ap-south-1`, COMPLIANCE mode, seven-year default retention) created during onboarding by an infrastructure library under an onboarding-scoped role, with the `quarantine/` prefix inside it; a platform-side archive bucket; the three existing writers re-pointed and brought under the delivery contract (identity, version, digest, completion linkage, retry/reconciliation, replay handling). Residency-driven placement and per-tenant retention are future amendments to DEC-3ee0f6 (D11), not requirements of this program. This replaces, by design, the role the retired Mongo inbox played by accident.

### 8.4 Tenant databases and the fleet

Fresh creation stays as it is. Static-schema upgrades become the runner applying versioned tenant migrations across the fleet with per-tenant ledger state, partial-failure isolation, canaries, lag reporting and resumability; dynamic fact tables stay with the owner worker under the static/dynamic contract (FR-25). Each tenant's owner and runtime credentials live in the secrets manager and rotate. The registry records each tenant's hosting instance. BYO-DB is specified (FR-11) before it is supported; the tenant-preference screens in bc-portal are studied in W2 so the UI promises only what the foundation honors.

### 8.5 Environments, promotion and hosting

One environment definition shared by application, infrastructure code and tooling. A change is promoted dev → staging → production as one immutable release artifact with fresh per-target evidence (FR-17). The platform database has one hosting option. **Production runs on RDS PostgreSQL** (managed backups, point-in-time recovery, patching — the operator should not personally be the disaster-recovery plan); non-production cloud environments, when an approved profile exists, run on the smallest RDS or a small self-managed instance; development stays local. The engine is pinned at 17.x with an explicit patch or digest. Not Aurora.

### 8.6 Infrastructure code (bc-infra)

bc-infra remains the **instance-provisioning layer** — VPC, database instances, secrets, the SSM contract, IAM — and is realigned as a W1 unit that is *selected only when a budgeted cloud profile is approved*: retire the dormant Aurora construct, target RDS PostgreSQL 17, add a schema-apply deployment stage that invokes the runner, provide the onboarding-invoked bucket library and roles (FR-20) and the secrets store, and adopt the single environment definition. The spine itself lives with the application.

### 8.7 Capacity and pooling

The platform database is a **read-dominated control plane**; tenant databases carry the **runtime writes**, isolated per tenant. Today each process holds up to ten runtime and four owner connections *per tenant*; at a hundred tenants across several processes that is thousands of potential connections against instances that serve many tenant databases — a pooler only in front of the platform database does not solve tenant-instance saturation. Design consequences: a connection budget per physical instance; bounded active pools with backpressure and noisy-tenant limits; platform reads cached and keyed on the published content version (promotion invalidates caches); migration canaries and stop thresholds; a synthetic 100-tenant benchmark with a defined workload before the numbers are needed; read replicas deferred until measured.

## 9. Program plan

Waves are program milestones. Each wave is delivered as **independently reviewable units** in a stated order; W1's sequence is listed explicitly because it is the largest.

| Wave | Scope | Exit criteria | Gate |
|---|---|---|---|
| **W0** | Bind governing records: study merged (done); this document merged; track DEC-591eb7 (bc-docs PR #15, merged); ratify the program mandate as a decision record (D1, done); formalize BC-Agent deferral (D6, done); coordinate with the Platform Readiness session (§13.4) | Records merged/ratified; coordination note acknowledged. **State (2026-09-21): CLOSED** — record work complete (bc-docs PR #17 merged, `734574fa`); the coordination acknowledgement is now retained as an immutable governed record (**DEC-568d0b**, Platform/Tenant Readiness re-affirmation, source SES-b5c14b), satisfying the d597 RESPONSE-148 retained-evidence gate; operator accepted W0 closure on it (**DEC-9dd4eb / D616**) | Operator |
| **W1** | Migration baseline + runner, in units: **W1.1** custody, scope definition and capture design (FR-4a/4c, FR-15), **and the engine and tool version contract** — the exact PostgreSQL patch or image digest and client/tool versions used locally and in CI, pinned and verified compatible with the measured live target (NFR-4); **W1.2** canonical baseline, mapping and equivalence gate on the pinned engine (FR-4, FR-6, FR-7, FR-4b interim rule); **W1.3** runner, roles and grants, release manifest carrying the tested versions, runtime contract, adoption rehearsal on scratch (FR-2, FR-3, FR-5, FR-14, FR-17, FR-23, NFR-8); **W1.4** minimum recovery for the platform DB — backup schedule, retention, bound monitor, drill — and the recoverable-unit definition (NFR-5 minimum, FR-26); **W1.5** live adoption of the development database under DBCP, after compatibility with the measured live engine is confirmed (separately gated); **W1.6** cloud realization of the version contract and bc-infra realignment (§8.6) — only when a budgeted profile is selected | Engine and tool versions pinned and proven in CI; from-zero build passes equivalence; runner rehearsed on scratch; ledger authoritative going forward; platform backup, retention, bound monitor and service drill proven at the provisional objectives; live adoption witnessed and recorded | Operator (design brief; W1.5 live apply); auditor (each unit at exact head) |
| **W2** | Tenant static source of truth + upgrade path + fleet + credentials: FR-9–FR-11, FR-18, FR-19, FR-22, FR-25; tenant-preference contract (FR-21, Appendix C); onboarding substrate requested by the tenant-onboarding design — one platform table (onboarding record) delivered through the spine under the Database Change Protocol, one master-data seed (a single "Free" package row in `pricing.package`, deterministic and digest-bound per FR-8, not an ad hoc insert), and population of `tenant.tenant_infrastructure` at provisioning; the subscription-instance table is deferred until pricing bands exist (reported operator decision, 2026-09-09); **minimum recovery for tenant DBs including archive durability and the supported-profile service drill (NFR-5, FR-20 minimum)** | Tenant upgrades run by the runner across the fleet; seed-CLI path fixed or retired; BYO-DB specified; credentials in the secrets manager; tenant backup schedule, retention and bound monitor live; service recovery drill for the AWS-Shared profile passed; unsupported profiles held; onboarding substrate landed | Operator (design brief + live apply); auditor |
| **W3** | Content promotion: FR-12, FR-13; master-data parity (FR-8); cache keys on content version | Every curated collection versioned, digest-bound, promotable; parity green in CI against an authorized capture | Operator (design brief); auditor |
| **W4** | Durability, object stores, capacity: full NFR-5 (PITR, D10 objectives, BC defined, FR-26 full drill); NFR-6 escrow incl. key escrow drill; FR-20 full lifecycle; FR-21 enforcement; FR-24 drift observation; NFR-9 benchmark | Policies decided and drilled; buckets created per decision and governed; benchmark results recorded | Operator (design brief); auditor |
| **W5** | Cleanup: modular→monolith assembly per DEC-591eb7 (the interim rule of FR-4b ends here); rename `docker/redesign`; retire dead paths; generated documentation (FR-16) | Retirements executed only by this wave's review | Auditor |

Retained from the prior program: the schema-acquisition launcher package built under the earlier de-drift task (an operator-signed, evidence-chained way to capture the live schema; internally labelled "F7") is neither used nor retired by this document; the operator selected path B for FR-4c on 2026-09-09 (D12, DEC-c99f72) — a lightweight script whose corrected brief and script must still be independently accepted, and whose every run needs the separate per-run authorization — so the launcher stays parked; its long-term disposition is its own decision (D7). A pending fix to that package (bc-core PR #746) stays parked with it. The earlier task's scope is subsumed into W5 under the ratified mandate (D1, DEC-75fc71). The four operator-only gates (acquisition authorization, DDL apply, scope/golden ratification, production promotion) apply throughout.

## 10. Decisions required

| # | Decision | Owner | Needed by |
|---|---|---|---|
| D1 | Ratify the program mandate as a decision record — **ratified 2026-09-09, DEC-75fc71** (includes the subsumption of the earlier de-drift task into W5); ADR custody merged to bc-docs `main` (`734574fa`, PR #17) | Operator | done |
| D2 | Merge bc-docs PR #15 to track DEC-591eb7 — **done 2026-09-09** (merged by the auditor App under operator authorization, commit `2d60a4b8`; custody only — DEC-591eb7 remains `proposed`) | Operator | done |
| D3 | Machinery home — **decided 2026-09-09: dedicated repository `bc-db`** (scaffold created; content arrives by wave). Recorded as DEC-826390; ADR custody merged to bc-docs `main` (`a9eadc13`, PR #16) | Operator | done |
| D4 | Hosting by environment: production on RDS PostgreSQL 17 (reconfirming DEC-1918d0, not Aurora); non-production cloud on the smallest RDS or a small instance under a budgeted profile; development local | Operator | W1 |
| D5 | BYO-DB posture: specify (FR-11) or defer the tier | Operator / product | W2 |
| D6 | Formalize the BC-Agent deferral against ADR-edd9bb — **ratified 2026-09-09, DEC-66d3ca** (ADR-edd9bb unchanged; the appliance-vs-hosted conflict parked; reinstatement needs its own record); ADR custody merged to bc-docs `main` (`734574fa`, PR #17) | Operator | done |
| D7 | Disposition of the schema-acquisition launcher package from the prior task — **ratified 2026-09-09, DEC-3628b4: retired** without ever having run; bc-core PR #746 closed unmerged; the schema comparator core is retained and quarantined pending W1.2's adopt-or-replace decision; grounded survey of every trace in `docs/design/f7-launcher-retirement-survey.md` | Operator | done |
| D8 | Operating model (§13) — **ratified 2026-09-09, DEC-0e4547**; plus the operator's standing authority (2026-09-09) for the auditor to review and merge documentation and record units at exact heads with green CI; ADR custody merged to bc-docs `main` (`734574fa`, PR #17) | Operator | done |
| D9 | Escrow target and key-escrow arrangement outside the primary account (NFR-6) | Operator | W4 (target chosen in W1) |
| D10 | Recovery objectives (acceptable data loss and downtime) per database category — confirms or tightens the provisional NFR-5 numbers | Operator | W4 |
| D11 | Whether residency-driven object-store placement and per-tenant retention are wanted — an amendment to DEC-3ee0f6 if so | Operator / product | W4 |

## 11. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Baseline capture ratifies accidental live objects | Wrong schema becomes canonical | Three-step baseline (capture → reviewed mapping → ratification, FR-4); auditor review of the mapping |
| Runner applied to live before rehearsal | Data loss or a hybrid state | Scratch rehearsal mandatory (W1.3); adoption predicate (FR-5); DBCP approval per application (W1.5) |
| Static migration races dynamic table generation | Corrupted tenant schema | Static/dynamic contract with coordinated exclusion (FR-25) |
| Curated content lost before W3 lands | Loss of core platform value | Take and verify a fresh, manifest-bound dump early in W1 as an interim recovery artifact |
| Real tenant onboarded before recovery exists | Unrecoverable customer data | Minimum recovery with measurable objectives is a W1/W2 exit criterion (NFR-5), enforced in tenant readiness; archive durability included |
| Backups exist but the unit is not restorable | Recovery fails at the first outage | Recoverable-unit definition (FR-26); drill through the escrow path (NFR-6) |
| Account-level loss (compromise, billing, region) | Platform loss | Off-account escrow incl. key material (NFR-6); rebuildable-anywhere spine |
| Program ceremony exceeds the operator's capacity | Program stalls | Operating model (§13): approval-only operator; small units; correction to acceptance without operator involvement |
| Builder drifts from design | Wasted auditor rounds | Design briefs produce machine-checkable acceptance criteria; fail-closed tests; exact-head auditor gate |
| UI built on provisioning semantics W2 will change | Rework in bc-portal/bc-admin | Coordination with the Platform Readiness session (§13.4); preference screens held until honored |
| Connection explosion at scale | Instance saturation | Per-instance connection budget, bounded pools, backpressure; benchmark (NFR-9) before it is needed |
| Engine mismatch between environments | Migrations valid in dev fail in production | Version contract pinned in W1.1 before any proof; CI proves the spine on the pin; live compatibility confirmed before adoption (NFR-4) |
| Documentation drifts again | Repeated wasted sessions | Generated or CI-checked documentation (FR-16) |

## 12. Open questions

1. What exactly is "volatile" per curated collection, and how is UI-authored content captured into promotion without a manual step?
2. Which extensions and cluster roles must a customer-hosted database provide, and can evidence-immutability be enforced there?
3. Is one equivalence definition sufficient for both database categories?
4. Which secrets manager for development (local) vs cloud, so the code path is identical?
5. Recovery objectives per category (D10) — the operator's business call; provisional numbers in NFR-5 until then.
6. Which fields in the bc-portal tenant-preference screens map to foundation capabilities, and which must be removed or deferred? (Appendix C is the starting inventory, not an audited one.)
7. Record contradictions reported by the tenant-onboarding requirements study (2026-09-09) that the W2 design brief must settle explicitly: the tenant schema count (four, six or seven across records — the live and verified answer is six); and isolation-model records that still mark schema-per-tenant (`t_<slug>`) authoritative while the live model is database-per-tenant (`tbc_<slug>`).
8. The subscription and onboarding-record state model: the onboarding session reports operator ratification on 2026-09-09. That report is carried as **provisional** here — the onboarding design document is untracked (no immutable version) and no decision record was cited. Before W2 lifts any column, constraint or readiness semantics from it, the design must be committed at an immutable version and the ratification bound to a record; state-model approval does not approve column design.

## 13. Operating model

### 13.1 Roles

- **Operator** — approves this document; approves each wave's design brief (one page per unit: scope, acceptance criteria, gates); approves any application to a live database under the Database Change Protocol; ratifies decisions D1–D11. Nothing else reaches the operator.
- **Builder** — executes each unit against the approved acceptance criteria, self-verifies every claim, produces evidence with the checked-in tooling, and submits exact-commit units.
- **Auditor (independent)** — reviews each design brief and each implementation unit at an exact commit; contributes architectural omissions and risks as a platform/DB architect, not only defect findings.

### 13.2 Unit shape and review

Every wave splits into a **design brief** (judgment-heavy; short; one operator approval; auditor review) and **implementation units** (mechanical against acceptance criteria; no operator involvement; auditor review at exact head). Approval binds the actual scope and the machine-checkable contract; it does not make review a one-round ceremony. **One review round is the target; correction to acceptance is normal** — finite implementation or evidence repairs continue until the auditor accepts. Escalation to the operator is reserved for a *genuine design dispute* unresolved after two rounds, per the standing exchange rule. All explicit operator gates and unsafe-operation stops are retained regardless of who executes a unit.

### 13.3 Model tiering

Design briefs are produced with careful reasoning (a frontier model or equivalent review). Implementation units may run on a capable non-frontier model: the acceptance criteria are machine-checkable, tests are fail-closed, evidence tooling is checked in and hardened, and the auditor gate catches error. The earlier de-drift task's failure mode — the operator burdened with mechanics while gaps went unseen — is what this separation prevents.

### 13.4 Coordination with the Platform Readiness session

That session continues platform-side work. The coordination note (continue platform-side; build only on `POST /tenants`; hold BYO-DB flows and unhonored preference fields) was sent on 2026-09-09 and acknowledged the same day by session message — originally carried here as **reported** because that acknowledgement existed only as a conversation. **[Status update 2026-09-21: the acknowledgement is now retained as an immutable governed record — DEC-568d0b (Platform/Tenant Readiness re-affirmation, source session SES-b5c14b) — which closes the W0 gate that d597 RESPONSE-148 held open; W0 is CLOSED, see §1.1 and §11. The narrative below is preserved as the historical coordination record.]** It reported that its onboarding design (two documents under `barecount-devhub/artifacts/tenant-onboarding/`, currently *untracked* in that repository, in operator review) builds on the verified `POST /tenants` contract, targets the AWS-Shared tier only in its first version, and holds BYO-DB, BC-Agent and AWS-Separate flows and every unhonored preference. It is not blocked. What it needs from this program, all placed in W2: the tenant source-of-truth and upgrade-path decision (so its flow never hard-wires a DDL file or the seed path); the onboarding-record table through the spine (its column design exists in §9b of that session's design and is input to the W2 brief under the conditions of open question 8 — schema placement and the opaque JSON column against the no-queryable-JSONB rule are W2's decisions), plus a single "Free" package seed row in `pricing.package` as class-2 master data — the subscription-instance table is deferred until pricing bands are decided (reported operator decision, 2026-09-09; tenant lifecycle stays on `tenant.tenants.status_code` meanwhile); population of `tenant.tenant_infrastructure` at provisioning; a platform-scoped tenant-readiness projection; and — added 2026-09-09 from the external auditor's review of bc-admin PR #41 (finding F3, upheld twice) — an **authoritative target-preview contract**: a `GET` endpoint on bc-core that returns the tenant database name for a slug computed by the *same* derivation the provisioner executes (`deriveDbName`, today private in `tenant-provisioning-api.service.ts`), and a `POST /tenants` that accepts the expected target and **refuses at the write boundary on mismatch**, so configuration drift between preview and provisioning cannot silently switch targets (the same pin-and-validate pattern as FR-17's per-target evidence). bc-admin PR #41 is parked until that contract exists. Its remaining needs — a create-tenant-admin endpoint honoring the admin/member distinction, and authoring Odoo into the source catalog — are platform acts outside this program.

## 14. Architect's additions

Beyond the operator's review points, the following were added on the builder's judgment and refined by the auditor's first review: environment promotion as one immutable release artifact with per-target evidence (FR-17); tenant fleet operations with canaries (FR-18); a runtime schema contract with stale policy and drain barrier (FR-23); production drift observation against per-tenant intended state (FR-24); the static/dynamic schema contract (FR-25); the recoverable unit (FR-26); the object-store data class realized per its decisions with a delivery contract (FR-20); PII and lifecycle enforcement tied to the tenant-preference contract (FR-21); tenant placement recorded for horizontal distribution (FR-22, NFR-10); the per-instance capacity model and benchmark (NFR-9); escrow including key material (NFR-6); cache invalidation keyed on the promoted content version (§8.7); and the golden developer path as the human form of reproducibility (G1). **Standing ask of the auditor:** review each wave brief as an architect — what is missing, what is over-built, what will hurt at a hundred tenants or at the first outage — in addition to validating consistency with the accepted study.

## Appendix A — Evidence and provenance

The audit-grade record for the factual claims **that appear in the accepted study** is `docs/design/db-schema-foundation-study.md` (merged to `main`, commit `3e7a69d7`). It cites, per claim, a source line or a machine-evidence block. Machine evidence is produced by `scripts/evidence/db-foundation-evidence.sh`, which records the exact command executed per block and stores raw output; the manifest records the hash of each raw file; `scripts/evidence/verify-evidence-custody.sh <commit>` re-verifies those hashes against committed bytes (it is a diagnostic today and is hardened for unattended use in W1.1). The classified inventory of the 262 migration files is `docs/design/evidence/db-foundation-migration-inventory-2026-09-09.tsv`.

Claims added in this document after the study — the object-store decisions and writers, the infrastructure stack, the tenant-preference inventory, connection-pool bounds, the provisioning lock, and the directions reported by the operator and by the tenant-onboarding session — are **not** covered by the study's audit. Their provenance is listed in Appendix E; where a source is not immutable (an untracked document, a reported conversation) the claim is carried as reported or provisional and says so.

## Appendix B — Glossary

- **Adoption (witnessed)** — recording that an existing database already matches the canonical baseline at a measured hash, without executing DDL; distinct from applying a migration.
- **Baseline (canonical)** — the reviewed, ratified migration that represents the schema at a chosen cutoff, derived from an immutable capture by a recorded mapping; the start of forward-only history.
- **Content promotion** — exporting curated data in canonical, versioned form and applying it to another environment with provenance intact.
- **DBCP** — Database Change Protocol: no schema change without presenting the change, obtaining approval, and applying with evidence.
- **Dynamic tables** — per-tenant fact tables generated from the registry by the owner worker; versioned by a generated-object manifest, not by the runner.
- **Equivalence** — a defined comparison between a built schema and an intended schema over an explicit set of surfaces.
- **Escrow** — a copy of backups, versioned content and key material held outside the primary cloud account.
- **Fleet** — the set of all tenant databases operated as one unit for upgrades and promotions.
- **Ledger** — `infrastructure.schema_migration_event`, the append-only record of migration applications and witnessed adoptions.
- **Owner plane** — the identity (`bc_tenant_owner`) and processes permitted to change tenant schema; never the served API.
- **Quarantine** — the `quarantine/` prefix of a tenant's archive bucket, holding inputs that were rejected or could not be admitted, with a governed path back into admission.
- **Recoverable unit** — the set of database states, versions, objects, roles and secrets that must be restored together, in order, for service to return.
- **Release manifest** — the immutable artifact binding schema, content, configuration and tool versions with compatibility preconditions, applied per target with fresh evidence.
- **Runner** — the single tool that applies static migrations, promotes content and records both.
- **Spine** — the versioned, forward-only sequence of baseline plus migrations from which any environment is built.

## Appendix C — Tenant-preference surfaces (inventory, 2026-09-09; reported, not audited)

Supplied by the tenant-onboarding design session from the DevHub screen registry (`bc-portal`), which catalogues the earlier mockup route set; the live application implements a re-architected subset under `/workspace/*`. Both agree on the fact that matters here: **no tenant-preference backend exists except connections.** This inventory has not been independently audited and is the *starting point* of the W2 study, not its result.

| Cluster | Screens (registry uid) | Backend today | Foundation dependency |
|---|---|---|---|
| Account | Subscription (SCR-4711fa), Users & Seats (SCR-a93aea), Security (SCR-891230) | None (stub) | Subscription-instance table **deferred** until pricing bands are decided (reported operator decision, 2026-09-09); subscription functionality stays held; v1 offers the single Free package (W2 seed) and tenant lifecycle on `tenant.tenants.status_code` |
| Workspace | Organization (SCR-9a3413: identity, industry, platform controls, data compliance incl. residency and DPA), Data Context (SCR-c6635c), Exchange Rates (SCR-e248c4), Business Functions (SCR-3d070b), Teams (SCR-a5522b) | None (mock; master-data API pending) | Residency-driven placement is not decided (D11); master data (class 2) |
| Data infrastructure | Data Backup (SCR-834650), Data Residency (SCR-b74d2e), Data Retention (SCR-0eca75), Data Compliance (SCR-fb47c6), Data Policies (SCR-712a8e) | None | **Promise without foundation** — backup/restore (NFR-5), placement (D11), retention and lifecycle (FR-20, FR-21), per-tenant credentials (FR-19); must not ship live before W2/W4 |
| Source data | Add Connection (SCR-48ee39), Connected Sources (SCR-95f7ad) | Live: `POST /api/t/connections`, credentials by reference only | Credential store (FR-19) |

## Appendix D — Related records

ADR-b1a286 (source-of-truth model); DEC-591eb7 (modular SoT → generated monolith + parity gate, proposed; bc-docs PR #15); DEC-1918d0 (deployment and database architecture); DEC-771baf, D575 (tenant topology and two-plane identity); DEC-324d9e (hosting tiers); DEC-a67518 (BYO-DB/BC-Agent onboarding gate); DEC-edd9bb (BC-Agent appliance; deferred by DEC-66d3ca, D6, ratified 2026-09-09); object stores: DEC-14592e (write-once archive, JSONL, COMPLIANCE lock, seven-year retention), DEC-3ee0f6 (per-tenant Object-Lock archive bucket created at onboarding, `ap-south-1`), DEC-95687d (S3 as the only opaque-payload store), DEC-2658ff and DEC-20eefe (typed tables in the database, raw payloads and detailed evidence in S3), DEC-29f134 (runtime drift detection; quarantine prefix inside the tenant bucket); privacy: DEC-bd5492 (nullification object, PII registry, data-subject requests, retention), DEC-490520 and DEC-743186 (source-field PII marking); existing tasks folded in: TSK-620cf3 (role-lock DB write access, pre-production gate), TSK-4ab20e (platform-runtime least privilege), TSK-7dd19f (credential rotation and Secrets Manager migration), TSK-3da1f0 (Secrets Manager credential resolver); TSK-cc348a (this program); TSK-3f52d7 (prior de-drift task; subsumed into W5 by DEC-75fc71, D1, ratified 2026-09-09); program decisions: DEC-75fc71 (mandate, D1), DEC-66d3ca (BC-Agent deferral, D6), DEC-0e4547 (operating model, D8), DEC-826390 (machinery home `bc-db`, D3), DEC-c99f72 (capture authority, D12); bc-core PR #747 (study and evidence, merged); PR #713 (safe-restore wave); PR #730 (genesis seed layer); PR #746 (parked fix to the capture package).

## Appendix E — Provenance of claims added after the accepted study

All repository references are at the revisions stated; "reported" means the claim rests on a conversation or an untracked document and is carried as provisional.

| Claim | Source | Revision / immutability |
|---|---|---|
| Object-store decisions: per-tenant bucket created at onboarding, `ap-south-1`, COMPLIANCE, 7-year retention; quarantine as a prefix inside it | bc-docs `docs/governance/adrs/ADR-3ee0f6.md` (§Decision, §Provisioning sequence, §IAM); `ADR-29f134.md` (D-4) | bc-docs `main` `196423c1d94a702d37ac006570064f47900959a0` (tracked ADRs) |
| Three S3 writers and their failure semantics | bc-core `src/evidence/evidence-archive.service.ts:73-87`; `src/progression/s3-archiver.service.ts:17-18,50-51,99-126,193`; `src/nullification/s3-nullification.service.ts:9-11,33` | bc-core `main` `3e7a69d7` |
| No quarantine implementation at the admission boundary | no match for `quarantine` under `src/boundary/` | bc-core `main` `3e7a69d7` |
| bc-infra entry point deploys AuthStack only; platform stack instantiates the Aurora construct; no bucket, single Aurora secret | bc-infra `cdk/bin/platform-infra.ts:30-35`; `cdk/lib/platform-infra-stack.ts:8,61-62,96-98,138-145` | bc-infra `c218787` |
| `tenant.tenant_infrastructure` defined in DDL; no application writer found; live presence **unverified** | `docker/redesign/02-platform-tables/05-tenant.sql:50`; `02-platform-tables.sql:1259`; grep of `src/` finds only the Drizzle type; no retained live observation names the table | bc-core `main` `3e7a69d7` |
| Connection pool bounds 10 runtime / 4 owner per tenant per process | `src/database/tenant-connection.service.ts:69,106`; `src/database/tenant-owner/tenant-owner-connection.service.ts:86` | bc-core `main` `3e7a69d7` |
| Per-command dynamic-DDL fencing | `src/schema-provisioner/owner/provisioning-execution-lock.service.ts:64-97` | bc-core `main` `3e7a69d7` |
| CI database image is the floating `postgres:17` tag | `.github/workflows/ci.yml` service definitions (study block E7b) | bc-core `main` `3e7a69d7` |
| Existing security/credential tasks | DevHub TSK-620cf3, TSK-4ab20e, TSK-7dd19f, TSK-3da1f0 | DevHub task registry, read 2026-09-09 — **reported** until the registry exposes a record version |
| Privacy decisions | DevHub DEC-bd5492, DEC-490520, DEC-743186 (tracked ADRs `docs/governance/adrs/ADR-bd5492.md` etc. in bc-docs) | DevHub decision registry, read 2026-09-09 — **reported**; ADR files bind at bc-docs `196423c1d94a702d37ac006570064f47900959a0` |
| Operator review points and approval in principle | operator message, this session, 2026-09-09 | **reported** |
| Tenant-preference inventory; onboarding design; state-model ratification | tenant-onboarding session messages, 2026-09-09; `barecount-devhub/artifacts/tenant-onboarding/*.md` | **reported; documents untracked** (open question 8) |
| Program mandate (D1), BC-Agent deferral (D6), operating model (D8) | DevHub DEC-75fc71, DEC-66d3ca, DEC-0e4547 (ratified 2026-09-09); ADRs `docs/governance/adrs/ADR-75fc71.md` sha256 `ccf442300775784d97b2a55aa359ceb1977859b992e19c3d2f32c600354392bd`, `ADR-66d3ca.md` `4617cbff7ffae495a809f6506d5203c437213c71c742fa423b05843f4f9e7877`, `ADR-0e4547.md` `1a44a34b738dba32066f2c6ab396166f306cf00943b8136c248a46355857f828` | versioned in bc-docs `main` at `734574fa01ce2d0b8993d7569afaa432d2df02ec` (PR #17, accepted head `d659c725`, merged by the auditor App) |
| Capture authority (D12 = B) and CI engine pin (D13) | operator approval of the W1.1 brief, 2026-09-09 (verbatim: "approve W1.1 brief; D12 = B; D13 = yes; Codex may review and merge W1.1 units A–D at exact heads with green CI"); DevHub DEC-c99f72 for D12 | operator statement relayed verbatim (d597 message 31, mirrored); decision record (registry) — ADR custody to follow |
| Machinery home = `bc-db` (D3); repository scaffold | DevHub DEC-826390 (decided 2026-09-09) — ADR `docs/governance/adrs/ADR-826390.md`, raw sha256 `2223562be7c39686a8c0edbfae585d3350d7f76f64a38484bbd5292e9dc6d03c`, versioned in bc-docs `main` at `a9eadc13a4481a64506b35dcea83141557b40e57` (PR #16, accepted head `d7de9f4f`, merged by the auditor App); `selenite-git-admin/bc-db` initial commit `4359985cfb15ba0289d9db189501afdbd47e1ecb` | committed ADR at an immutable bc-docs revision; repository state immutable at that commit |
| Subscription-instance table deferred; single Free package seed | tenant-onboarding session message, 2026-09-09 | **reported** operator decision |
