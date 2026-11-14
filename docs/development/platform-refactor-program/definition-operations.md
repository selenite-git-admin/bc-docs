---
id: platform-refactor-program-definition-operations
order: 45.13
title: "The Definition of Operations"
status: drafting
authority: reference
depends_on: [devhub, documentation-system, decision-and-change-procedure]
governing_sources:
  - Platform Refactor Program (the method; the order of work; the reference run; the hold on the engine)
  - Function Dossiers (OP, Operations)
  - Vocabulary (live act; live window)
governing_adrs:
  - DEC-71f15e (the Platform Refactor Program)
  - DEC-4c1396 (bc-db is the only place schema changes are written and applied)
  - DEC-ecd55c (credentials live in AWS Secrets Manager)
  - DEC-e50b83 (the port table)
  - DEC-5b760c (quality checks run in each repository's CI)
errata_referenced: []
v2_sources: []
diagrams: []
---

# The Definition of Operations

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md). It is the written definition that the Define step of function OP, Operations, calls for: what Operations is, the things it keeps, the acts it performs, the states those things pass through, and the design and limits of the reference run. The Chief wrote it in phase 3. The operator approves it; that approval is the exit of the Define step. It is changed afterwards only by a ruling.

## How to read this definition

It is a design. It says what Operations will be when the function is locked; it does not describe what is done today. Each section has up to four parts.

- **Today** gives the facts the section starts from, each with the file and line, the command, or the query behind it.
- **The definition** states what holds once Operations is locked.
- **What must change** lists the repairs, in the order the Modify step will take them. An item marked **the operator's act** is on the hard line (a kept copy of a database, a database change, a cloud change, a credential, serving the engine): approving this definition does not approve it, and it is done only under its own recorded grant.
- **Left to the operator** holds only what the definition does not settle. Where a ruling in the register covers a question, the ruling is named and the question is not asked again.

Seven rulings are due in this phase: G12, G13, G14, G15, the first part of G35, B1 and B2. They are put to the operator in the rulings annex with a recommendation each. This definition is written as if each recommendation were accepted, and each section says what changes if the operator rules the other way.

## What was checked, and by whom

Four readers gathered the facts on 2026-11-14 between 17:09 and 17:15 UTC, read-only: bc-docs at `9f463527`, the engine (bc-core) at `df52506d`, bc-db at `814603e2`, bc-infra at `81ace477`, barecount-devhub at `7330083f`, the folder `~/bc-stack` on the development machine, the platform database and the Kaveri tenant database with read-only queries, and the cloud account with listing calls only. No secret value was read.

The Chief read at source: the ledger's row count and kinds, the absence of a ledger row and of every checked object for migrations 0032, 0034, 0035 and 0038, and the one superuser role (one query, 2026-11-14); the serve-move comments and the served build in `~/bc-stack/process-compose.yaml`; the rule that derives a database name's suffix (`src/database/tenant-connection.service.ts:202-210`); the loader's default secret name and profile (`scripts/dev-secrets/dev-secrets-lib.mjs:15, 42`); the flags of the two dump scripts; the checks GitHub requires on the main branch of bc-core and bc-db; the form of an exception record in the hold on the engine (`scripts/engine-guard/hold.mjs:1-33`); the status of four ADRs; that pull request 128 of barecount-devhub is closed and unmerged; and the two rows the Kaveri tenant holds for `total_journal_entries` in one period. Every other fact carries its citation and was not re-read by the Chief. **Every count read from a database or from the cloud account is a reader's report:** it explains why a part of the definition is needed and is never to be used as a gate. A fact found wrong is corrected here, and a part of the definition that rested on it is put to the operator again.

Since the dossier for OP was written on 2026-11-13, four of its facts have changed. The folder `~/MyProjects/_wt` holds two build trees of the engine, `freeze-1052` and `freeze-1055`, where the dossier counted 239 folders (phase 0 removed the rest). bc-db has a hold of its own: a pull request that changes `migrations/`, `rollback/`, `baseline/`, `releases/` or `tools/runner/` is refused unless it carries an exception record (bc-db `.github/workflows/engine-hold.yml`; required on main). The backup bucket holds 136 objects. And a restore **is** proven for the platform database, though not for a nightly backup: see "Backup and restore".

## What Operations is

Operations is how the platform is run and changed on the machines it runs on. It keeps eight things:

1. **Environments:** where the platform runs and what each place is called.
2. **Services:** the programs that run in an environment, and the supervisor that keeps them running.
3. **Builds:** the exact code of the engine that a service runs, and the act of changing it (a serve move).
4. **Settings and secrets:** how a running service is given them.
5. **The schema-change path:** how the structure of a database changes, and the ledger that records it.
6. **Backups:** copies of the databases, and the proof that a copy can be restored.
7. **The checks on every change** (continuous integration, CI), as far as where they run.
8. **Cloud infrastructure:** what is defined, what is deployed, and how a deployment is made.

It also keeps one thing no other function has: **the reference run**, the check that a change to the engine has not moved a value.

Operations does not decide what a tenant is or who may sign in (S1, S2, S3), what a contract means (the authoring lanes), or what a session may do (DV). It serves the operator and every session. Where an act of Operations changes live state it is a **live act**, in the vocabulary's sense, and is performed in a **live window** under the operator's recorded grant.

## 1. Environments

**Today.**
- One suffix is in use, `_dev`, on `bc_platform_dev` and on each tenant database. The engine does not name its environment: it copies the suffix from the database name in its settings, accepting `dev`, `staging`, `prod` or `test` (`src/database/tenant-connection.service.ts:202-210`; the same rule in `src/database/tenant-owner/tenant-owner-connection.service.ts:192-199` and `src/registry/seed/seed-tenant-dbs.ts:44-51`). The platform database's name is written into the code once (`src/database/served-identity/platform-session-identity.ts:25`).
- bc-infra names its deployments by a code in each resource name: `dev` and `stg` are defined (`cdk/cdk.json:4-25`); its deploy definitions offer `dev` and `prod` (`.github/workflows/cd-prepare.yml:14-18`). Three deployed units carry `dev` in their names, and all three serve the development machine: sign-in, secrets, and the machines that run CI.
- The chapters use "Local", "AWS dev" and "AWS prod" (`docs/operations/deployment-topology.md:131-139`), and separately "live" and "rehearsal" for the served platform and a copy of it (`docs/operations/serve-moves-and-live-windows.md:47-52`). Request bodies carry an environment code whose default differs between parts of the engine, `dev` in one and `production` in another (`docs/operations/runtime-runbook.md:41-57`; reader's report).

**The definition.**
- There is one list of environment names: **`dev`**, **`stg`**, **`prod`**.
- **`dev`** is the development environment: the development machine, and the cloud resources named `dev` that serve it. It is the only environment that exists.
- **`stg`** and **`prod`** are names kept for a platform hosted in the cloud. Neither is built, and the program builds neither.
- **Live** is not an environment. It describes the served platform inside an environment: on `dev`, the services on their fixed ports and the databases they use. A **disposable copy** is a restored copy of the databases on other ports, with a build served against it, made for one check and then destroyed. "Rehearsal", "clone" and "kit" in older texts mean a disposable copy.
- `test` is not an environment. It is a suffix that automatic checks give to databases they create and destroy.
- An environment's name is declared once, in the settings a service is given, and every part of the engine reads that one value. No part has a default of its own.

**What must change.**
1. The chapters and the local runbook use the three names and the two words "live" and "disposable copy".
2. The engine reads one declared environment name, and the differing defaults are removed. How the engine's own code and its requests spell that name is ruling B17, due in phase 5; this change is made when B17 is, by the function that owns the code. Where a file is under the hold on the engine, the change is made after the reference run exists and passes on it.

**If ruling G13 goes the other way** (the development machine is given a name of its own, such as `local`): the list gains that name, and the three cloud resources named `dev` are described as shared by it. Nothing else in this definition changes.

## 2. Services

**Today.** One supervisor, kept running by the machine's own launcher, runs five services from `~/bc-stack/process-compose.yaml`: the database containers, DevHub, the engine, the operator console and the customer portal. The engine runs from a build tree of its own (`~/MyProjects/_wt/freeze-1055` at `ec72438b`). DevHub, the console and the portal run from the shared copies of their repositories. The local runbook `~/bc-stack/README.md` disagrees with the supervisor's file on the served build, the return build, which services start, and how DevHub starts; a reader listed fifteen differences.

**The definition.**
- The supervisor's file is the one statement of what runs on the development machine. The runbook is produced from it and cannot disagree with it.
- Every service runs from a copy of its own, at a commit that is written down. No service runs from a shared copy. A shared copy is then only a mirror of the main branch, as the program's rule on repositories requires.
- A service is **stopped**, **running** or **ready**. Ready means its own check answers; for the engine it also means the database login it holds is the one expected.
- The ports are those of DEC-e50b83 and are declared in one place.

**What must change.**
1. DevHub, the console and the portal are each given a build tree and a pinned commit, served by the same procedure as the engine (section 3).
2. The runbook is produced from the supervisor's file.

## 3. Builds, and the serve move

**Today.**
- The launcher refuses to start the engine unless the build tree is clean, its commit equals the pinned commit, the list of built files hashes to the pinned value, and no settings file in the tree holds a database address (`~/bc-stack/serve-core-ref-v2.sh:26-41`).
- The chapter describes a move in ten steps: two identical build trees, a rehearsal on a copy with a forced failure, the auditor's clearance of the move, the operator's grant, one runner script, verification, and a return path that reports by exit code (`docs/operations/serve-moves-and-live-windows.md:103-311`).
- The six moves of 2026-11-11 to 2026-11-13 were done otherwise: one build tree, the supervisor's file edited by hand, the engine alone restarted through the supervisor, a folder of before and after records, and the operator's recorded grant. No script performs this move; the committed tools perform the documented one, by a supervisor command that restarts every service. The six folders hold six different sets of files.
- **One of the six moves never took effect.** The move to `freeze-1048` on 2026-11-12 changed the file and restarted the engine, the supervisor reused the definition it held in memory, and the old build went on serving. The move's record read the file, not the running server, and reported success (`~/bc-stack/process-compose.yaml`, the correction above the 2026-11-12 entry).
- The return to the previous build is a note in a comment. The build trees that four of those notes name no longer exist; only `freeze-1052`, the return build of the current move, does.

**The definition.**
- A **build** is one commit of a repository's main branch, built once in a tree of its own, identified by the commit and by the hash of the list of its built files. A build is **built**, then **served**, then **previous** (kept as the return build), then **removed**.
- A **serve move** changes the build a service runs. There is one procedure, for every service, performed by one command:
  1. **Check.** The commit is on the main branch. The build tree is clean and its hash is the one stated. Its settings file has the same names as the served one and holds no database address. The build needs no schema change that is not applied. If the build changes a file under the hold on the engine, the reference run has passed on that exact commit. The operator's grant for this move is recorded and names the commit and the hash.
  2. **Record before.** The supervisor's definition of the service and what the running server reports are saved.
  3. **Do.** The service's definition is changed through the supervisor, for that service alone. No other service restarts.
  4. **Verify.** The verification reads **the running server**, never the file: the directory it runs from, the commit of that directory, the hash of its built files, its readiness check, and the database login it holds. A fixed read of one known value answers as before.
  5. **Return.** If any verification fails, the command restores the definition saved in step 2 through the supervisor and verifies again in the same way. It reports "returned" only after it has observed the previous build serving.
- The previous build is kept, untouched, until the next move has been verified. It is the only build a move may return to.
- The serve move of a build that changes no file under the hold needs no disposable copy. A build that does is shown unchanged by the reference run, which serves it against a disposable copy (section 9). The twin trees and the rehearsal with a forced failure are retired: the return path is exercised by the command's own test and once in phase 3.
- **The auditor's clearance of each serve move.** The operator's recorded grant `2026-09-29T08-34-38-377Z-ead781aa` says that the auditor keeps reviewing changes to the engine, serve moves included. This definition proposes that the auditor's review of a change at its merge, together with its attested reference run where held files change, takes the place of a separate clearance of each move. **That takes effect only if the operator's grant for ruling G14 says, in express words, that it supersedes that part of the standing instruction.** Until such a grant is recorded, every serve move of the engine keeps the auditor's clearance as one of the checks of step 1, and the command refuses a move without it.
- A serve move of the engine is a live act and needs the operator's recorded grant each time, until ruling G1 is made.

**What must change.**
1. The one command is written, with status, check, do and verify, and is tested against a disposable copy, including a move that fails and returns.
2. It is run once for a real move and once for a return to the previous build (**the operator's acts**: each serves the engine). Neither has been built or tested yet; nothing in this definition is evidence that the command works.
3. The chapter is rewritten to this procedure; the committed tools for the older procedure are removed.

**If ruling G14 goes the other way** (the documented twin-tree procedure is the one procedure): steps 1 to 5 stay, the build is made twice and compared, and every move is first performed on a disposable copy with a forced failure and cleared by the auditor. The command then performs those steps too. **If the operator accepts the procedure and keeps the auditor's clearance:** nothing else changes; the clearance stays a check of step 1.

## 4. Settings and secrets

**Today.**
- The served engine is given its secrets one way: the launcher starts a loader that reads one secret, `bcp-dev-aps1-sct-secret`, from the cloud account's secret store and passes its keys to the server (`scripts/with-dev-secrets.mjs`; `scripts/dev-secrets/dev-secrets-lib.mjs:15`). The launcher and the engine each refuse to start if a database address is found in a settings file.
- Beside that route there are others. The loader's own default identity is a short-lived role, `bc-dev`, which does not work yet; the development machine overrides it with `default`, a long-lived key of the operator's own user (`dev-secrets-lib.mjs:42`; `process-compose.yaml:14`). The shared copy of the engine has a settings file, readable by every user of the machine, that names two database addresses. A second loader names a secret that does not exist in the account (`scripts/with-demo-secrets.mjs:25`). Two files of credentials lie in `~/bc-stack/secrets` and nothing that was searched reads them. The tool through which sessions read the database connects as the database's one superuser, with the password written into a settings file of the session program; it starts every connection read-only.
- Three texts contain a literal example password: `docs/implementation/infrastructure.md:110`, and two files of the database-reading tool.
- No script in `~/bc-stack` contains a secret value. The nightly backup files contain the stored form of every database password and are readable by every user of the machine.

**The definition.**
- A service is given its secrets by **one route**: the secret store, read by the one loader when the service starts, under one named identity. A settings file holds names and values that are not secret, and never a database address or a password.
- The identity is named in one place, the supervisor's file.
- No tool and no session connects to a database as a superuser. Sessions read through a login that can only read.
- No document holds a real or example password.
- Changing a secret's value, or the identity that reads it, is the operator's act.

**What must change.**
1. The second loader and the unread credential files are removed, or their one user is found and brought onto the one route.
2. The shared copy's settings file loses its database addresses.
3. The session read tool connects through a read-only login (**the operator's act**: it changes a stored credential).
4. The backup files and their folder are readable by the owner only.
5. The three literal passwords are removed from the texts.

**Left to the operator.** Which identity is the one identity on the development machine. Options: `default`, the long-lived key in use today; or `bc-dev`, the short-lived role that needs the sign-in to be repaired. Recommendation: `bc-dev` is the target, and `default` stays, named as a known exception on the lock list, until the sign-in works. Phase 3's condition "secrets are loaded one way" is then met by the one route; the identity is settled when Operations is locked.

## 5. The schema-change path

**Today.**
- The path as practised, read from the newest apply (migrations 0070 and 0071, 2026-11-12): a number is claimed; one forward migration is written in bc-db with its header, its own check of the state it expects, and a rollback file; the operator approves the database change at the desk; the auditor reviews it at an exact commit and it is merged; it is proven on a restored copy of the platform database, through the real runner, with the served login's permissions tested; a window script, committed with the migration, checks that it is on the right database server, takes and restores a backup, runs the proof again, applies the one migration through the runner, and checks the result. The runner writes the migration and its ledger row in one transaction (bc-db `tools/runner/README.md:3-11`; `docs/dbcp/apply-0070-0071/`).
- The ledger holds 74 rows: 70 applied, 3 excepted, 1 adopted.
- **Four migrations on bc-db's main branch have no ledger row and none of their objects exists:** 0032, 0034, 0035 and 0038. Each waits for engine code that is not built, and each was merged with its apply still to be approved. Two would change behaviour if applied alone: 0032 makes every new metric contract version need a declaration that nothing writes; 0034 refuses a tenant's move to active without a verdict that nothing records. A comment in the engine already describes 0034's refusal as if it existed (`src/tenant-management/dto/update-tenant.dto.ts:13-16`).
- The rule that migrations are applied in number order rests on an ADR still proposed (DEC-bd6894), and the ledger already departs from it.
- Nothing automatic compares the migration files with the ledger. The proofs on a restored copy are not part of CI; they need the development machine.
- The written accounts disagree with the practice. Two chapters still give the frozen folder `docker/redesign` as the path (`docs/implementation/data-model-and-schema.md:68`; `docs/operations/upgrade-and-migration.md:40-46`). bc-db's own README says the repository is an empty scaffold. Its roles document describes four roles that do not exist and says the owner login is not a superuser; it is.

**The definition.**
- The path is the one practised, written once: **claim, write, approve, review and merge, prove on a restored copy, apply in a window, record.** DEC-4c1396 stands.
- A migration is **merged**, then **awaiting apply**, then **proven**, then **applied**; or it is **excepted** (it never applies to this database, and the ledger says why); or it is **withdrawn** (removed from the main branch before it was applied).
- The ledger in the live database is the only record of what was applied (DEC-4c1396). The runner writes a row in the same transaction as the change, so a row never exists before its apply, and none is ever written to stand for one.
- **Awaiting apply is a declared state.** Between its merge and its apply a migration has no ledger row. For that interval it has one line in a register kept in bc-db, `docs/migrations-awaiting-apply.md`, added by the pull request that merges the migration. The line names the migration, the engine change that needs it, and the window planned for it. The line is removed by the change that records the apply's evidence.
- **Every migration file on the main branch has a ledger row or a line in that register.** A file with neither is a defect. A file that is not going to be applied does not stay on the main branch: its text is kept with its design record, and it returns under a new number when the function that needs it reaches its Modify step.
- The comparison of files, ledger and register needs the live ledger, which the checks on the hosting service cannot read. It is a command of Operations, run on the development machine with a read-only login; DevHub shows its result and the age of each register line. The checks on the hosting service verify only that the register is well formed and names files that exist.
- A migration is merged only together with, or after, the engine code that needs it, and is applied in the same window in which that code is served.
- Whether applies must follow number order is the subject of DEC-bd6894, which is still proposed. This definition does not decide it. The ledger shows that practice has already departed from number order; that is a fact for that decision, and no rule is drawn from it here.
- Every apply is a live act and the operator's, under its own recorded grant.

**What must change.**
1. Migrations 0032, 0034, 0035 and 0038 are withdrawn from bc-db's main branch (ruling G12). This changes files under bc-db's hold and needs the operator's exception; it changes no database. Before it is done, the Audit step establishes whether any automatic check builds a database from those files.
2. The two chapters, bc-db's README and its roles document are rewritten to the practice. The engine comment that describes a refusal which does not exist is corrected when S3 reaches its Modify step.
3. The register is created and the comparison command is written; it is run once.
4. DEC-bd6894 is put to the operator as its own decision, to be decided or withdrawn. It is not decided by this definition or by ruling G12.
5. Decisions DEC-cf6d3b and DEC-103acb, both decided, state the condition for a tenant to be active differently: the first a verified admin and one active Subscription, the second the identity fields, a legal entity and a fiscal calendar. DEC-cf6d3b cites DEC-103acb and does not amend that condition. The conflict is settled in the Define step of S3, in phase 4, before any successor to migration 0034 is written.

**If ruling G12 goes the other way** (the four are applied): each needs its own approval and window, 0032 and 0034 cannot be applied before the engine code that satisfies them is built, and until then each has a line in the register of migrations awaiting apply.

## 6. Backup and restore

**Today.**
- Every night a script copies the whole database server into one compressed file, keeps the newest seven on the machine, and uploads each with a checksum to a private bucket (`~/bc-stack/pg-backup.sh`). The copy covers every database, tenants included. It does not cover DevHub's own database, the cache, or the demonstration source system.
- No restore of a nightly file has been recorded. Between 2026-11-05 and 2026-11-09 no backup was made, because the container host was down, and nothing raised an alarm (reader's report from the backup log).
- A restore of the platform database is proven, routinely: every apply first copies the platform database, restores the copy into a fresh container, and compares a fingerprint of the two (bc-db `docs/dbcp/apply-0053-0060/backup-gate.zsh`; twenty such records). That copy holds the platform database only.
- bc-db holds a fuller backup tool with a restore drill and an age monitor (`tools/backup/`). It is exercised in CI and is not what runs each night.

**The definition.**
- A **backup** is a copy of every database of the live platform, identified by its hash. It is **taken**, then **stored** (on the machine and off it), then **proven** when it has been restored to a disposable copy and its fingerprint compared.
- A backup is taken at least daily. An alarm is raised when the newest backup is older than a stated bound.
- A backup is proven on a schedule, and before any live window that changes a database. The result is recorded.
- There is one backup tool. It is the tool that is tested.
- What is outside the backup is stated in the chapter: today, DevHub's database, the cache and the source system.

**What must change.**
1. A restore command restores a nightly backup to a disposable copy and compares a fingerprint. It is run once.
2. The age alarm is put in place.
3. The nightly script and bc-db's backup tool become one tool.

## 7. The checks on every change

**Today.** Each repository's checks run on a pull request and on a push. Where they run is chosen at the start of each run: bc-core is set to short-lived cloud machines, bc-db has no setting, and the last run of each fell back to the hosting service's own machines (reader's report). The CI chapter says both are set (`docs/development/continuous-integration.md:58`). The checks GitHub requires before a merge are `quality-gate`, `engine-hold` and `code-rule-baseline` on bc-core, and `quality-gate` and `engine-hold` on bc-db.

**The definition.** Which checks a repository runs is each function's and Development's matter (DEC-5b760c). Operations keeps where they run: one written statement, per repository, of the machines used and the setting that selects them, true to the settings. The checks that hold the engine are described in section 9.

**What must change.** The chapter and the settings are made to agree.

## 8. Cloud infrastructure

**Today.** bc-infra defines six units. Three are deployed: sign-in, secrets, and the machines that run CI. Three are not: the network, a managed database, and the unit that would apply the schema to it. The account has no managed database. The two ADRs that the undeployed units follow are still proposed (DEC-e39ed3, DEC-c40e7a). A deployment is made by two definitions started by hand, the second of which can change the account; or from the development machine under the operator's long-lived key. bc-infra's README omits the unit for CI machines.

**The definition.**
- The chapter states, unit by unit, what is **deployed** and what is **designed and not built**. The three undeployed units are designed and not built (ruling G15).
- A deployment is the operator's act, under its own recorded grant, by one written procedure.
- Deployment of the platform to the cloud is outside the program.

**What must change.** The infrastructure chapter and bc-infra's README are rewritten to this. The two proposed ADRs are decided when a deployment of those units is first asked for, not before.

**If ruling G15 goes the other way** (the three definitions are removed): they are deleted from bc-infra and kept in its history, and the chapter says so.

## 9. The reference run

The program requires one command that evaluates a fixed set of metrics through the real engine on a fixed copy of the databases, and fails on any difference from recorded values. Nothing of it is built. This section is its design and its limits.

**Today.**
- **Evaluating needs a running engine.** A metric is evaluated for a tenant only through a request to a served engine, which needs a signed token, the tenant's name, a legal entity, a reader and a date (`src/boundary/metric-evaluation-orchestrator.controller.ts:34-52`). No command evaluates a tenant's metric without a server. Evaluation reads only the databases: nothing in it calls the source system.
- **What Kaveri holds.** 74 recorded metric values in 17 tables, for 5 periods: 73 distinct pairs of metric and period, one metric holding two recorded values for one period. The newest was recorded on 2026-10-25 (reader's queries on the tenant database). The doubled pair is `total_journal_entries` for FY2026-27/P05: two rows, recorded on 2026-09-23 and 2026-09-27 by two evaluations, both with the value 212 (the Chief's read-only query, 2026-11-14). These counts are reports about the live tenant database; the reference set is drawn from the copy, as stated below.
- **Evaluation adds and never replaces.** Evaluating a metric again for the same period records a second value beside the first. A canonical resolution that finds its objects already present does nothing and reports success.
- **The expected values are of two kinds.** For eight metrics, at five dates each, a scouting document records values worked out from the source system apart from the platform (`artifacts/spine-review/STEP-0-reference-harness-scouting.md`, section 2). The files for three of them, the receivable metrics, are on barecount-devhub's main branch (`artifacts/metric-audit/foundry-tally/reference-receivables.json`); the files for the other five are in commits that were never merged. For the remaining metrics the recorded values were worked out from rows the platform had itself admitted, or from a constructed fixture. **Ruling B5's text says that every expected value recorded so far is of the second kind. For the three receivable metrics the files say otherwise.** This definition does not settle which is right: B5 is due in phase 8, and the reference run does not depend on the answer.
- **The scouting document's set does not add up.** Its heading says twelve metrics and 51 values; its table lists thirteen metrics and 47 values. Three of the thirteen belong to the demo plane, which is parked; one of those has no version in force.
- **A dump script exists.** It takes the platform database, each tenant database and the roles, **without passwords**, and writes their hashes (`artifacts/w9-serve-move-4/tools/take-fresh-dumps-2.zsh:21-29`). Tools exist that restore such a set into fresh containers on other ports and serve a build there. They were last used on 2026-09-30 and are not checked against today's schema.
- **The hold on the engine cannot see the development machine.** It is a check on the hosting service that compares the files a pull request changes with the list of held files, and passes a held change only if the pull request adds one exception record carrying the operator's grant (`scripts/engine-guard/hold.mjs:1-33`). No exception has been recorded. The check cannot read the desk, the development machine, or the result of any run.

**The definition.**

*The fixed input.* One copy is taken once: the platform database, the Kaveri tenant database, and the roles without passwords. It holds demo-tenant data. Its roles file holds no role password, because the dump leaves them out. Whether the platform and tenant databases themselves hold any value that is a password, a key or a token is checked on the copy when it is taken, by a search that the command keeps and whose result is recorded; a copy that holds one is not kept until the operator has ruled on it. Its files are hashed; the hashes are committed to the DevHub repository; the files are kept on the development machine outside every repository, readable only by the owner and by the auditor's account, and go nowhere else (ruling B1). No other tenant's database is in it.

*The reference set.* It is the Kaveri tenant's metrics only, in two tiers that are never mixed in a report.
- **The baseline tier** is every recorded metric value Kaveri holds in the copy: every row, not every pair. Today's reading is 74 rows. Each row is one expected value, identified by its metric, its period and the identifier of the evaluation that recorded it, and carrying the value held. A run evaluates each pair of metric and period once. The result for a pair is compared with **every** row held for that pair, and each comparison is reported on its own line; the pair passes only if every one of its rows agrees. Where the rows held for one pair differ among themselves, no result can pass, and the pair is reported at the first run for the operator's choice under ruling B2. No row is left out. The tier shows that a value has not moved. It does not show that the value is right.
- The list of expected rows is produced from the copy itself when the copy is taken, by a query that the command keeps, and is committed with its hash and with the counts of rows, pairs and tables. The command recounts the copy at every run and refuses to run if the counts or the hash differ. The figures in this definition are not the authority; the committed list is.
- **The independent tier** is the values worked out from the source system apart from the platform, each with its file, the date it was worked out, and the method. It starts with the three receivable metrics at the dates their files give. It includes the thread's metric, `receivable_control_balance`. The five other metrics join it only when their files are found and merged.
- The demo plane is not in the set. The count "thirteen" in the program text is replaced by these two tiers.

*One run.* The command:
1. checks the copy's hashes against the committed ones;
2. restores the copy into fresh database containers on ports that are not the live ones, and refuses if it would touch a live port, name or database server;
3. applies to the copy, through the real runner, any migration the candidate build needs that the copy lacks;
4. removes from the copy the canonical objects and the metric values of the reference set, so that nothing can pass by being already present;
5. builds the candidate commit and serves it against the copy, with the evaluation schedule off and with stand-in credentials that exist only for the copy;
6. resolves the canonical objects, then evaluates every pair of metric and period of the set once, the simple metrics before the ones built on them;
7. compares each result with every expected value held for its pair: exactly, to the smallest unit, for amounts and counts; to the stated number of decimal places for a ratio;
8. runs four cases that must fail: an expected value changed by one unit, a sign reversed, a period shifted, and a mapping changed. If any of the four passes, the run fails;
9. writes one record: the hashes of the copy, the commit of the candidate, the state of the contracts used, each value with its tier, expected value and source, and the verdict;
10. destroys the copy and the containers, whatever the verdict.

*Its states.* For a commit of the engine the reference run is **not run**, **passed** or **failed**. A pass belongs to one commit and one copy.

*Where it lives.* In the DevHub repository, as the program states, so that a change to the engine cannot change the thing that checks it. It runs on the development machine.

*The first run is a qualification.* The contracts have moved since Kaveri's values were recorded: two versions of one canonical contract are in force together, and every held value was produced over the older one (scouting document, risk 1; not re-read). Whether today's engine reproduces the held values is not known. If the first run does not, the Chief reports each difference with its cause, and the operator chooses the baseline under ruling B2: the values the engine gives today with the contracts in force, or the values held, with the contract state that produced them restored in the copy. Until that choice is made there is no baseline and the phase's exit is not met.

*How the hold comes to require it.* A passed run is attested by a party that the author of a change does not control, and the attestation is bound to the exact commit.

- **Who attests.** The auditor. The reference run for a proposed change to held files is performed under the auditor's own account on the development machine, from the command as committed on the DevHub repository's main branch, on the exact head commit of the pull request, against the fixed copy, whose hashes it checks. This is the same independent party that reviews and merges every change to the engine.
- **What the attestation is.** A check run on the hosting service, named `reference-run`, on that head commit, with the conclusion "success", created by the auditor's own App. Its text carries the SHA-256 of the run's record, and the record is committed in the auditor's repository beside the auditor's response for that pull request.
- **What `engine-hold` accepts.** From the end of phase 3, `engine-hold` on bc-core, which runs from the base tree and never from the proposed one, passes a change to held files only if the hosting service returns, for the exact head commit, a check run named `reference-run` whose conclusion is "success" **and whose creating App is the auditor's App**, by the App's identifier, which is written in a held file of the base tree. Nothing else is accepted: not a commit status of that name, not a check run of that name created by any other App, and not a record file added by the pull request.
- **Why it cannot be had without a run by the auditor.** A commit status can be posted by anyone holding a token for the repository, for any commit and under any name; that is why a commit status is not accepted. A check run can be created only by an App, and the hosting service itself records which App created it. A workflow in a pull request can create a check run named `reference-run`, but it is created by the hosting service's own Actions App, whose identifier is not the auditor's. The private key of the auditor's App is held only in the auditor's account; no session and no workflow holds it. A new commit on the pull request has no check run, so the attestation never carries over from one head to the next.
- **The negative tests,** kept with the check and run in its own test suite and once against the hosting service before the switch: a commit status named `reference-run` with the state "success" on the head does not clear the hold; a check run of that name created by the Actions App does not clear it; a record file added by the pull request does not clear it; a genuine check run on an earlier head of the same pull request does not clear it; and a check run with the conclusion "failure" from the auditor's App does not clear it.
- **What stays as it is.** The exception record remains as the operator's override, for the case where the reference run itself must change with the engine. Any session may run the command for its own information; such a run attests nothing.
- **What this needs, each the operator's act:** the auditor's App is given the permission to create check runs on bc-core; the auditor's account is given what it needs to perform a run (read access to the fixed copy and the means to start the disposable containers); and the change to `engine-hold`, which is itself a change to held files, is made under one exception. Whether the auditor's account can perform a run on the development machine as it is set up today is not established; the Audit step establishes it. If it cannot be made to, the phase's condition that the check requires the reference run is not met, and the Chief puts that to the operator.

*Who owns it.* Operations owns the reference run: its command, its fixed copy, its expected values and its chapter. The DevHub repository is where its code is kept. The auditor performs the attested runs and owns the attestation.

*bc-db.* The hold on bc-db stays as it is: an exception from the operator for each change. A migration is not shown harmless by the reference run alone; it is shown by its proof on a restored copy and, where the engine uses it, by the reference run of the build that needs it.

**Its limits.** They are stated in the chapter and on every record.
1. A pass shows that values have not moved. Only the independent tier says anything about whether a value is right, and it covers three metrics.
2. It covers one tenant, the metrics that tenant holds, and the periods it holds them for (five today).
3. It starts from rows already admitted. It does not exercise the reading of a source system or admission.
4. It does not exercise authoring, certification, the demo plane, delivery to a user, or the creation of a tenant.
5. It runs on the development machine only. How long a run takes is not known; the scouting document expects twelve to twenty minutes and nothing has been measured.
6. Its trust rests on the copy being unchanged, which the hashes show, and on the attestation being created only by the auditor's App after a run the auditor performed. `engine-hold` checks who created the attestation and for which commit; it does not itself read the run's record. The record's content is checked by the auditor, who made it.

**What must change.**
1. The command is written in the DevHub repository with its tests, using the restore and serve tools that exist after they have been checked against today's schema.
2. The copy is taken (**the operator's act**, under ruling B1).
3. The first run is made and reported; the baseline is chosen if the run requires it (ruling B2).
4. The auditor's App is given the permission to create check runs on bc-core, the auditor's account is enabled to perform a run, and `engine-hold` is changed with its negative tests (**the operator's acts**).
5. The program document records the hashes of the copy, the engine commit, the source of each expected value, and the result.

**If ruling B1 goes the other way** (no copy may be kept): the copy is taken afresh for every run and destroyed after it. The run can then show only that a build gives the values the live databases hold at that moment; no pass can be compared with an earlier one, and phase 3's condition that the program records the hash of the copy cannot be met as written.

## 10. Where Operations' commands are kept

**Today.** `~/bc-stack` is in no repository. A reader counted 34 scripts at its top level: 12 in use by the supervisor or the machine's launcher, 12 run by hand, 2 that nothing refers to, and 8 written for single past merges; with ten backup copies of files. The tool through which sessions read the database is in no repository either. Some scripts for the development machine are already kept in the DevHub repository, and are installed from it: the supervisor's keeper, the outage watchdog, the tools for the documented serve move, and the script that changes the database superuser's password.

**The definition.** Operations' commands are kept in bc-infra, with the cloud definitions (ruling G35, part one), each with its four verbs. A command there has no authority to change the cloud: that authority stays with the two deploy definitions and the operator's grant. The reference run is the one exception, kept in the DevHub repository for the reason given in section 9. Before a script enters a repository its text and its output are checked, so that no secret value, no local secret file and no logged value enters with it. Scripts written for one past act are not moved; they are recorded and removed.

Operations' acts, each a command with status, check, do and verify:

| Act | Changes live state | Whose grant |
|---|---|---|
| Start, stop or restart a service | yes | covered by the standing grant, for services other than the engine |
| Serve a build; return to the previous build | yes | the operator's, each time, for the engine |
| Show what a service was given (names only) | no | none |
| Prove a migration on a restored copy | no | none |
| Apply a migration | yes | the operator's, each time |
| Take a backup | no | none |
| Restore a backup to a disposable copy | no | none |
| Take the fixed copy for the reference run | no; it makes a kept copy of data | the operator's, once |
| Run the reference run | no | none |
| Deploy a cloud unit | yes | the operator's, each time |

**If part one of ruling G35 goes the other way** (the DevHub repository holds them): the commands join the scripts already there, and bc-infra holds cloud definitions only.

## What this definition asks the operator to approve

1. The eight things Operations keeps, and their states (sections 1 to 8).
2. The one serve procedure of section 3.
3. The one route for secrets of section 4, with the identity `bc-dev` as the target and `default` as the named exception until the sign-in works.
4. The schema-change path of section 5, with its rule that every migration file on the main branch has a ledger row.
5. The reference run of section 9: its fixed input, its two tiers, its ten steps, its limits, and the auditor's attestation by which the hold comes to require it.
6. The table of acts in section 10.

Approving it approves no database change, no cloud change, no credential, no serve move and no copy of a database. Each of those is asked for when it is to be done.
