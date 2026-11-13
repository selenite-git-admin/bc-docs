---
id: platform-refactor-program-repositories
order: 45.6
title: "Every Repository and Where It Belongs"
status: drafting
authority: reference
depends_on: [devhub, documentation-system, decision-and-change-procedure]
governing_sources:
  - Platform Readiness Program (the function list)
  - Vocabulary (the status words and the definition of done)
  - Documentation System
  - Decision and Change Procedure
governing_adrs:
  - DEC-3395bc (bc-docs is the single source of truth)
  - DEC-a67bae (the locked lane taxonomy; one owner per surface)
  - DEC-ce4314 (the ten onboarding lanes)
  - DEC-71c027 (Integrity Assurance as the platform thesis)
  - DEC-c220e4 (the interim rule on which metrics a tenant sees)
  - DEC-cf6d3b (the tenant activation model; tenant-to-package assignment)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Every Repository and Where It Belongs

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md).

This annex lists every BareCount repository and every leftover directory on the development host, and assigns each top-level part of the backend, bc-core, to one function of the functional map. One row is one repository or directory: what it is, its measured size, how it runs today, the function or functions it serves, and a status. Every repository was read at `origin/main` on 2026-11-13, bc-core at `ec72438b`; the short sha of each is in the table under "What was read". Limits that apply to the whole annex: no fetch was run, so each `origin/main` is the copy last received from GitHub; programs that run under another macOS account could not be inspected; the owner of each bc-core directory is a proposal made from names, header comments and route prefixes, for each function's Audit step to confirm, and no call graph was built; tenant databases were not read. The closing section lists everything that could not be assigned or verified.

## What this annex covers

BareCount is built from several code repositories. A repository is a folder of files whose history is kept by the version-control tool git. The functional map is the list of platform functions under "The functional map" in the main document (S1, Authentication, through DV, Development).

The annex has two tables.

- **Table 1** covers every entry under `~/MyProjects`, the folder that holds all BareCount repositories on the development host (a Mac Mini; `barecount-devhub:CLAUDE.md:7 @ 93cc1ea5`).
- **Table 2** covers one repository, bc-core, directory by directory. bc-core is the backend server of the platform and holds most of the platform's code.

All measurements were taken on 2026-11-13 on the development host.

### What was read

Each repository was read at `origin/main`. `origin/main` is the copy of the main branch that the local repository last received from GitHub. It was not updated for this annex (no fetch was run), so every number describes that copy. Files on disk were read only for directories that are not git repositories and for `~/bc-stack`, the folder of host scripts that start the services.

The short identifier (sha) of each `origin/main`, from `command: git -C ~/MyProjects/<repo> rev-parse --short origin/main`:

| Repository | origin/main |
|---|---|
| bc-docs | f4f5edd |
| barecount-devhub | 93cc1ea5 |
| bc-core | ec72438b |
| bc-db | c6de1c4 |
| bc-admin | d37b241 |
| bc-portal | 04930c8 |
| bc-demo | 91e7e6bf |
| bc-infra | 81ace47 |
| bc-external-audit | 2d23f938 |
| bc-audit-app | b5673e7 |
| bc-website-v2 | dfde654 |
| bc-exchange | 58a2e57 |

### How sizes were measured

- **Files** is the number of tracked files, meaning files git keeps history for. `command: git -C <repo> ls-tree -r --name-only origin/main | wc -l`
- **Lines** is the sum of the line counts of every tracked text file. Git decides what is text; binary files such as images are skipped. `command: git -C <repo> grep -I -c '' origin/main | awk -F: '{s+=$NF} END{print s}'`. The command prints one `origin/main:path:count` row per text file and the `awk` part adds the last field. It counts every line, including blank lines, data files and generated files.
- **Source lines** is the same sum without dependency lock files and test snapshot files. `command: git -C <repo> grep -I -c '' origin/main -- . ':(exclude,glob)**/package-lock.json' ':(exclude,glob)**/pnpm-lock.yaml' ':(exclude,glob)**/yarn.lock' ':(exclude,glob)**/*.snap' | awk -F: '{s+=$NF} END{print s}'`. This figure still includes data files (JSON, CSV, SQL dumps) and documents. Where data dominates a repository, the note under Table 1 says so.
- **First and last commit** are `command: git -C <repo> log origin/main --reverse --format=%cs | head -1` and `command: git -C <repo> log -1 --format=%cs origin/main`.
- **Commits in 30 days** is `command: git -C <repo> rev-list --count --since='30 days ago' origin/main`.
- **Commits in all** is `command: git -C <repo> rev-list --count origin/main`.

### The status rule

The status column uses one rule, applied to the measurements above.

- **live:** at least one commit on `origin/main` in the last 30 days, or a running program on this host serves from the repository today.
- **parked:** no commit in the last 30 days and not running, but the project instructions name a use that is started by hand when needed.
- **stale:** no commit in the last 30 days, not running, and no named on-demand use.
- **archive:** named as an archive in the project instructions.
- **leftover:** a directory that is not one of the twelve project repositories: a spare working copy, a tool folder or review output.

## Table 1: every repository and leftover directory under `~/MyProjects`

`command: ls -la ~/MyProjects` returned 32 directories and one `.DS_Store` file (a macOS folder-settings file, not BareCount content). Every directory appears below, alone or in a grouped row.

### The twelve project repositories

The project instructions name twelve repositories (`barecount-devhub:CLAUDE.md:156-171 @ 93cc1ea5`). A tenant, used below, is one customer organisation with its own separate database.

| Name | Purpose | Size at origin/main | First and last commit; commits | How it runs today | Functions served | Status |
|---|---|---|---|---|---|---|
| bc-core | The backend server. Its own description: "BareCount Core API — NestJS backend with multi-tenant architecture" (`bc-core:package.json:5 @ ec72438b`). | 3,989 files; 3,145,575 lines; 3,128,821 source lines | 2026-02-23 to 2026-11-13; 310 in 30 days; 3,001 in all | Port 3100, as the `bc-core` service of process-compose, a supervisor program that starts and restarts the local services (`barecount-devhub:CLAUDE.md:127 @ 93cc1ea5`). Verified listening: `command: lsof -iTCP -sTCP:LISTEN -P -n \| grep ':3100 '` -> `node 36259 … TCP *:3100 (LISTEN)`. It is served from a spare working copy, not from `~/MyProjects/bc-core`: `command: lsof -a -p 36259 -d cwd -Fn` -> `/Users/anant/MyProjects/_wt/freeze-1055`; the service definition names the same folder and the commit `ec72438b…` (`~/bc-stack/process-compose.yaml:92,95`). | Every platform function from S1, Authentication, to SU, Support. Table 2 assigns its directories. | live |
| bc-portal | The customer's browser application. "bc-portal is the tenant-scope browser app of BareCount" (`bc-portal:CLAUDE.md:3 @ 04930c8`). | 927 files; 243,919 lines; 234,609 source lines | 2026-02-21 to 2026-10-20; 9 in 30 days; 137 in all | Port 3000, process-compose service `bc-portal` (`barecount-devhub:CLAUDE.md:125 @ 93cc1ea5`; `~/bc-stack/process-compose.yaml:120-123`). Verified: `lsof` -> `node 1410 … 127.0.0.1:3000 (LISTEN)`. | TS, Tenant self-service | live |
| bc-admin | The operator's browser application. "bc-admin is the BareCount platform admin frontend." (`bc-admin:README.md:5 @ d37b241`) | 319 files; 67,287 lines; 57,124 source lines | 2026-02-28 to 2026-11-10; 49 in 30 days; 436 in all | Port 3010, process-compose service `bc-admin` (`barecount-devhub:CLAUDE.md:126 @ 93cc1ea5`; `~/bc-stack/process-compose.yaml:108-111`). Verified: `lsof` -> `node 1366 … 127.0.0.1:3010 (LISTEN)`. | S5, Operator console | live |
| bc-docs | The documentation. "Canonical documentation spine for BareCount." (`bc-docs:README.md:3 @ f4f5edd`) | 1,414 files; 308,148 lines; 308,148 source lines | 2026-07-06 to 2026-11-11; 54 in 30 days; 771 in all | Not run as a service. Its files are read through bc-core and shown in bc-admin (`bc-admin:README.md:11 @ d37b241`). One CI check, `adr-hygiene.yml` (`command: git -C bc-docs ls-tree -r --name-only origin/main -- .github/workflows`). CI means the automatic checks GitHub runs on each change. | DV, Development | live |
| barecount-devhub | DevHub, the coordination tool every working session starts from. "Development coordination hub for BareCount projects" (`barecount-devhub:package.json:4 @ 93cc1ea5`). | 8,095 files; 1,858,303 lines; 1,855,313 source lines | 2026-02-22 to 2026-11-12; 67 in 30 days; 4,002 in all | Port 4000, process-compose service `devhub`, command `npm start` (`barecount-devhub:CLAUDE.md:128 @ 93cc1ea5`; `~/bc-stack/process-compose.yaml:29-32`). Verified: `lsof` -> `node 1375 … 127.0.0.1:4000 (LISTEN)`. | DV, Development | live |
| bc-db | The platform database's schema changes and the tooling that applies them. Title: "bc-db — BareCount Platform Database (schema spine and DB-management machinery)" (`bc-db:README.md:1 @ c6de1c4`). | 571 files; 116,203 lines; 116,203 source lines | 2026-09-09 to 2026-11-12; 137 in 30 days; 547 in all | Not a service. Its migrations are applied by hand through a governed runner (`barecount-devhub:CLAUDE.md:263 @ 93cc1ea5`). One CI check, `ci.yml`. The database it describes is Postgres on port 5435 (`barecount-devhub:CLAUDE.md:132 @ 93cc1ea5`); `lsof` shows `ssh 1505 … 127.0.0.1:5435 (LISTEN)`, a forwarded port. | OP, Operations (the schema-change path) | live |
| bc-demo | Builds the demonstration business data held in a real accounting system. "The product that builds and maintains BareCount's demo estates" (`bc-demo:README.md:3 @ 91e7e6bf`). | 5,940 files; 904,435 lines; 904,435 source lines | 2026-03-02 to 2026-10-02; 0 in 30 days; 2,321 in all | On demand. A local operations screen on port 8600 is started by hand, and the Odoo demonstration system on port 8100 runs on a cloud machine that is stopped by default (`barecount-devhub:CLAUDE.md:130-131 @ 93cc1ea5`). Verified not running: `command: nc -z -w 2 127.0.0.1 8600` -> exit 1; `command: nc -z -w 2 127.0.0.1 8100` -> exit 1. | PV, Proof against the source | parked |
| bc-infra | The cloud infrastructure definitions. "CDK (TypeScript) infrastructure for the BareCount platform in AWS account `546549546538`, region `ap-south-1`." (`bc-infra:README.md:3 @ 81ace47`) | 91 files; 17,835 lines; 12,430 source lines | 2025-09-02 to 2026-10-14; 0 in 30 days; 113 in all | Not run on this host. Three CI definitions: `cd-execute.yml`, `cd-prepare.yml`, `ci-validate.yml` (`command: git -C bc-infra ls-tree -r --name-only origin/main -- .github/workflows`). Whether they have run recently was not checked. | OP, Operations | stale |
| bc-external-audit | The home of the independent reviewer of code changes, an AI program called Codex, and the mailbox of messages exchanged with it. "The home of BareCount's independent auditor." (`bc-external-audit:README.md:3 @ 2d23f938`) | 8,982 files; 555,344 lines; 554,167 source lines | 2026-07-11 to 2026-11-13; 1,410 in 30 days; 8,361 in all | The reviewer runs "as a service on the Mac under its own macOS account (`bcauditor`)" (`bc-external-audit:README.md:3 @ 2d23f938`). Programs of another macOS account are not visible to `lsof` without elevated rights, so the running state was not verified. One CI check, `service-ci.yml`. | DV, Development (review) | live |
| bc-audit-app | A screen mock-up with no backend. "Static, navigable UI concept for an enterprise audit operations console." (`bc-audit-app:README.md:3 @ b5673e7`) | 21 files; 3,288 lines; 1,597 source lines | 2026-07-15 to 2026-07-15; 0 in 30 days; 4 in all | Not run. No CI definition (`command: git -C bc-audit-app ls-tree -r --name-only origin/main -- .github` -> no output). A folder `~/bc-stack/bc-audit-app` exists (`command: ls ~/bc-stack`); its contents were not read. | None with confidence. Nearest: DV, Development. | stale |
| bc-website-v2 | A placeholder for the public website. The whole README is "# BareCount Website v2" (`bc-website-v2:README.md:1 @ dfde654`). | 2 files; 4 lines; 4 source lines | 2026-03-19 to 2026-03-19; 0 in 30 days; 1 in all | Not run. `origin/main` holds only `.gitignore` and `README.md` (`command: git -C bc-website-v2 ls-tree --name-only origin/main`). | None. The public website is outside the functional map. | stale |
| bc-exchange | The desk where the operator records approvals and where review threads are listed. "Auditor exchange desk: gen- threads, status, operator grants (TOTP). Runs as bcauditor on 127.0.0.1:3040." (`bc-exchange:package.json:5 @ 58a2e57`) | 41 files; 3,206 lines; 3,206 source lines | 2026-09-28 to 2026-10-12; 0 in 30 days; 104 in all | Port 3040 under the `bcauditor` account (`barecount-devhub:CLAUDE.md:129 @ 93cc1ea5`). Verified that the port accepts a connection: `command: nc -z -w 2 127.0.0.1 3040` -> succeeded. `lsof` cannot show the owning program for another account. | DV, Development (review and operator approval) | live |

Notes on the sizes. The line counts are dominated by data and records in five repositories. Each figure below is from `command: git -C <repo> grep -I -c '' origin/main | awk -F: '{split($2,a,"/"); c[a[1]]+=$NF} END{for(e in c) print c[e], e}' | sort -rn`.

- **bc-core:** 2,023,632 lines are 31 archived catalog files of a source system under `scripts/archive/s4-catalog-import`. Table 2 gives the detail.
- **barecount-devhub:** 1,448,097 of 1,858,303 lines are under `artifacts/` (working papers); `src/` holds 28,714 lines.
- **bc-external-audit:** 549,953 of 555,344 lines are under `docs/`, the mailbox.
- **bc-demo:** 849,525 of 904,435 lines are under `sources/`.
- **bc-docs:** 243,847 lines are under `docs/` and 55,165 under `docs-control/`.

One statement in a README is out of date. bc-db describes itself as "scaffold only" with "No schema, migration, seed or content" (`bc-db:README.md:3 @ c6de1c4`), yet `origin/main` holds 73 text files under `migrations/` with 18,802 lines (same command as above).

### Directories that are not project repositories

A worktree, used below, is an extra working copy of a repository in its own folder, checked out on its own branch. Git keeps a register of them in the parent repository. "Dirty" means the working copy has changes that are not committed; the count is `command: git -C <dir> status --porcelain | wc -l`. Disk sizes are from `command: du -sh <dir>`.

| Name | What it is | Size | How it runs today | Functions served | Status |
|---|---|---|---|---|---|
| bc-pg-mcp | Not a git repository (`command: git -C ~/MyProjects/bc-pg-mcp rev-parse --show-toplevel` -> "fatal: not a git repository"). It is a small tool that lets an AI session read the database: "Security-hardened PostgreSQL MCP server for AI agents. Read-only by default." (`~/MyProjects/bc-pg-mcp/CLAUDE.md:3`, file on disk). MCP is the protocol through which an AI session calls a tool. | 9 source files, 706 lines (`command: find bc-pg-mcp/src -type f \| xargs wc -l`); 24 MB on disk with its dependencies | Started by the AI client when a session opens; the client configuration points at `bc-pg-mcp/dist/index.js` (`~/.claude.json:2265`). It has no version history, so no commit dates exist. Source files on disk are dated April 2026 (`command: ls -la ~/MyProjects/bc-pg-mcp`). | DV, Development | leftover (in use, but not under version control) |
| `_wt` | A folder of worktrees. 290 entries (`command: ls _wt \| wc -l`): 239 worktrees and 51 loose files (build logs and commit-message drafts). The 239 by parent repository: bc-core 78, barecount-devhub 51, bc-db 51, bc-external-audit 28, bc-docs 24, bc-demo 2, bc-infra 2, bc-portal 2, bc-admin 1 (`command: for d in _wt/*; git -C $d rev-parse --git-common-dir`, grouped). | 31 GB | One of them, `_wt/freeze-1055`, is the folder bc-core is served from (see the bc-core row). The others are not run. | The function of the parent repository | leftover; one entry is served and must not be removed |
| `.worktrees` | Two worktrees: `bc-docs-vocab-0034` (bc-docs, branch `claude/vocabulary-0034-onboarding-incomplete`, head 420fa78, last commit 2026-10-02, dirty 0) and `devhub-admin-artifacts` (barecount-devhub, branch `claude/admin-portal-artifacts-custody`, head 360b8459, last commit 2026-10-20, dirty 0). | 162 MB | Not run | DV, Development | leftover |
| `bc-core-wt-*` (9 directories) | Worktrees of bc-core beside the main copy. All nine are clean (dirty 0). `das36pin`: branch `claude/demo-das36-5-0-0-pin`, head 8257fe0e. `das36pin2`: `claude/demo-das36-5-1-0-pin`, 2a94e79a. `legm`: `claude/r2-demo-leg-membership`, 0d9dc7bb. `loaderv5`: `claude/demo-loader-v5-0-0`, 364599fd. `u3`: `claude/r2-u3-plane-parametric-resolver`, c3149723. `u3b`: `claude/r2-u3b-fiscal-plane`, 3b835387. `u3c`: `claude/r2-u3c-binding-plane`, 1eb09f42. `u3d`: `claude/r2-u3e-demo-resolve-runner`, 0dab607e. `v4`: `claude/r2-demo-world-v4-cc-501-pin`, c8ce54e4. Head commits are dated 2026-11-01 or 2026-11-02. | 1.0 GB together | Not run | PV, Proof against the source (every branch name refers to the demonstration plane) | leftover |
| `bc-db-wt-gate1` (1 directory) | A worktree of bc-db with no branch (`git rev-parse --abbrev-ref HEAD` -> `HEAD`, a detached checkout), head 492bff6, last commit 2026-10-22, dirty 0. | 6.1 MB | Not run | OP, Operations | leftover |
| `bc-demo-wt-*` (5 directories) | Worktrees of bc-demo. Each has 5 uncommitted changes (dirty 5). `aws`: branch `claude/odoo-aws-u4`, head 0ec96296, 2026-09-28. `tranche-b`: `claude/odoo-aws-a0`, 42a29d73, 2026-09-27. `u1`: `claude/odoo-mac-u1`, b7e7180e, 2026-09-26. `u3`: `claude/odoo-mac-u3-lockfill`, d9c6e936, 2026-09-27. `u4`: `claude/odoo-mac-u4`, a0053886, 2026-09-27. | 601 MB together | Not run | PV, Proof against the source | leftover; holds uncommitted changes |
| `_audit` | Not a git repository itself. It holds three worktrees of bc-core used for one review (`gen-51d78d-core`, head 16d84769, dirty 1; `gen-51d78d-02-core`, head 6cf860cf, dirty 1; `gen-51d78d-03-merge`, head 857477e2, dirty 18; all detached, last commits 2026-09-26) and nine log, list and script files (`command: ls -A _audit`). | 332 MB | Not run | DV, Development (review) | leftover |
| `audit-bc-core-865-82-full` | A separate full copy (clone) of bc-core, not a worktree: its git directory is its own `.git` and its remote is the bc-core repository on GitHub (`command: git -C audit-bc-core-865-82-full remote -v`). Branch `main`, head 09d087f5, last commit 2026-09-28, dirty 0. | 177 MB | Not run | DV, Development (review) | leftover |

### Registered worktrees: the count

The count is 323 linked worktrees, the figure the evidence annex gives (row 20a) and the main document uses. An earlier count gave 322. The disk figure of 31 GB covers only part of them.

`command: git -C ~/MyProjects/<repo> worktree list | wc -l` gives, per repository: bc-docs 38, barecount-devhub 89, bc-core 99, bc-db 60, bc-admin 2, bc-portal 3, bc-demo 8, bc-infra 3, bc-external-audit 30, bc-audit-app 1, bc-website-v2 1, bc-exchange 1. The sum is 335. Each repository's own main copy is one line of its list, so 12 of the 335 are main copies and **323 are extra worktrees**. None is marked prunable (`command: git -C <repo> worktree list --porcelain | grep -c '^prunable'` -> 0 for every repository).

Where the 323 are (`command: git -C <repo> worktree list --porcelain | grep '^worktree '`, grouped by path):

| Location | Count |
|---|---|
| `~/MyProjects/_wt/` | 239 |
| Inside a repository's own folder (`.claude/worktrees/`, `_wt/`, `_wt-ci-wedge`): barecount-devhub 36, bc-docs 12, bc-core 8, bc-db 6, bc-external-audit 1 | 63 |
| Sibling directories `bc-core-wt-*`, `bc-db-wt-*`, `bc-demo-wt-*` | 15 |
| `~/MyProjects/_audit/` | 3 |
| `~/MyProjects/.worktrees/` | 2 |
| `~/bc-stack/evidence/w6p-0022/20260927T053803Z/bcdb` (a bc-db worktree outside `~/MyProjects`) | 1 |
| Total | 323 |

The 31 GB is the size of `~/MyProjects/_wt` alone (`command: du -sh ~/MyProjects/_wt` -> 31G). The sibling directories, `.worktrees` and `_audit` add about 2.1 GB (1.0 GB, 6.1 MB, 601 MB, 162 MB and 332 MB, from the table above). The 63 worktrees inside repository folders and the one under `~/bc-stack` were not measured. One worktree is served: `_wt/freeze-1055`, confirmed above.

### Archives named in the project instructions

The project instructions name these archives: "Archives: `bc-docs-v2`, `bc-website-v1`, `bc-ai`, and `_archived-repos/` (bc-qa, bc-sdg, bc-core-dashboard)." (`barecount-devhub:CLAUDE.md:173 @ 93cc1ea5`). They also call `bc-docs-archived` and `bc-docs-v2` "read-only history" (`barecount-devhub:CLAUDE.md:19 @ 93cc1ea5`).

None of them exists on this machine under `~/MyProjects`. `command: ls -d ~/MyProjects/<name>` returned "No such file or directory" for each of `bc-docs-v2`, `bc-website-v1`, `bc-ai`, `_archived-repos`, `bc-docs-archived`, `bc-qa`, `bc-sdg` and `bc-core-dashboard`. The instructions say the Windows laptop keeps "other projects" (`barecount-devhub:CLAUDE.md:8 @ 93cc1ea5`); whether the archives are there was not checked. Any instruction that tells a session to fall back to `bc-docs-v2` cannot be followed on this host.

## Table 2: bc-core, directory by directory

This table assigns each top-level part of bc-core to one function. The coverage rule, under "The functional map" in the main document, says every surface belongs to exactly one function, or is entered in a register of things that are deliberately not part of any function, or is entered in the retirement list. Where a directory clearly serves two functions, the table names the main owner and writes "split needed".

Counts are scripted. Files: `command: git -C ~/MyProjects/bc-core ls-tree -r --name-only origin/main -- <dir> | wc -l`. Lines: `command: git -C ~/MyProjects/bc-core grep -I -c '' origin/main -- <dir> | awk -F: '{s+=$NF} END{print s}'`. All at `bc-core @ ec72438b`. The owner column is a judgement made from the file names, the module header comments and the route prefixes (`command: git -C ~/MyProjects/bc-core grep -n -h -E "@Controller\(" origin/main -- <dir>`); it is a proposal for each function's Audit step to confirm, not a finding.

### Totals

| Part | Files | Lines |
|---|---|---|
| `src/` (the source tree) | 2,568 | 780,588 |
| Everything outside `src/` | 1,421 | 2,364,987 |
| Whole repository | 3,989 | 3,145,575 |

The parts sum to the repository totals of Table 1. Inside `src/`, 28 directories hold 2,562 files and 779,789 lines, and 6 files directly in `src/` hold 799 lines.

By file type inside `src/` (`command: git grep -I -c '' origin/main`, grouped by file ending): 1,443 TypeScript code files, 259,329 lines; 838 test files (`.spec.ts`), 189,484 lines; 177 JSON data files, 310,312 lines; 93 SQL files, 17,730 lines; 16 documents, 3,719 lines; 1 other file, 14 lines.

### Directories under `src/`

Terms used in this table. A contract is a governed, versioned declaration of what a piece of data means. A panel is a group of AI models that reviews a proposed declaration. The demonstration plane is a separate set of database objects on which the platform checks its own results against a demonstration source system. A route is one address of the server's programming interface.

| Directory | What it holds | Files | Lines | Owning function | Note |
|---|---|---|---|---|---|
| `src/__architecture__` | Tests that guard the code's structure (allowed imports, forbidden words, routes without a guard) and their baseline files | 107 | 8,151 | DV, Development | These are the CI guards the Lock step of the method relies on (main document, "How a lock works") |
| `src/admin-inspection` | The operator's inspector for one metric; route prefix `admin/inspection/metrics` | 9 | 1,992 | S5, Operator console | |
| `src/attestation` | Bounded reads from one tenant database on behalf of the inspector (`src/attestation/attestation.module.ts:2-9`) | 5 | 463 | S5, Operator console | Serves only the inspector |
| `src/audit` | One service, `audit.service.ts`, and its module | 2 | 61 | Not assigned with confidence. Nearest: OP, Operations | See the closing list |
| `src/auth` | Login token checking, the global guards, and creation of users in the identity service; route prefixes `auth` and `admin/users` | 20 | 1,496 | S1, Authentication | Split needed: also S2, User and access management (`admin/users`, role guard) |
| `src/boundary` | The runtime acts: admission, observation, canonical resolution, metric evaluation, snapshots, the scheduler; 14 tenant route prefixes under `t/` | 257 | 62,799 | RT, Runtime | Split needed: also L7, Readers and connections (`reader-runtime/`, 33 files, 10,029 lines); PV, Proof against the source (23 files named `demo-*` or `e3-demo-*`, 3,971 lines); NT, Notifications and webhooks (`webhook-endpoint.controller.ts`, 84 lines); SU, Support (`boundary-ticket.service.ts`) |
| `src/common` | Shared decorators, filters, guards, interceptors, pagination and validation helpers | 35 | 2,039 | Register: shared code, not a function | |
| `src/config` | Configuration readers (`app`, `auth`, `database`, `ai`, `metric-runtime`) | 7 | 313 | OP, Operations | |
| `src/database` | Database connections, the separation between platform and tenant access, the guard on the served database login, and the TypeScript description of every table (`schema/`, 215 files, 12,567 lines) | 319 | 23,610 | OP, Operations | Split needed: also PV, Proof against the source (`demo-loader`, `demo-oracle-author`, `demo-prover`, `demo-resolver`, `demo-tx`: 52 files, 4,755 lines) |
| `src/demo-oracle-author` | Command-line tools that write the independently worked expected values on the demonstration plane | 18 | 2,775 | PV, Proof against the source | |
| `src/demo-resolve` | One command-line tool that runs canonical resolution on the demonstration plane | 3 | 387 | PV, Proof against the source | |
| `src/docs` | The server side of the documentation reader shown in bc-admin (`src/docs/docs.module.ts:2-3`); route prefix `docs` | 4 | 417 | DV, Development | |
| `src/evidence` | Evidence records, lineage, and the proof projection of a metric; route prefixes `t/evidence`, `t/evidence/records`, `t/lineage` | 18 | 3,237 | EV, Evidence and lineage | |
| `src/health` | One health-check route, `health` | 2 | 32 | OP, Operations | |
| `src/mls` | The recorder of a metric's lifecycle state and its gate (`src/mls/mls.module.ts:2-5`); route prefix `mls` | 22 | 3,188 | L6, Metric Contracts and certification | |
| `src/nullification` | Privacy erasure, the register of personal-data fields, retention policy and data-subject requests (`src/nullification/nullification.module.ts:2-6`) | 21 | 2,264 | PR, Privacy and retention | |
| `src/platform` | Reference data (`masters`), the library register and the AI vendor cost report; route prefixes `masters`, `libraries`, `vendor-costs` | 34 | 3,216 | MD, Master data | Split needed: also AI, AI services (`vendor-costs/`) |
| `src/progression` | Writers of the record kept for each runtime act (admission, canonical evaluation, metric evaluation, intervention evaluation) (`src/progression/progression.module.ts:2-7`) | 22 | 3,134 | RT, Runtime | The intervention writer relates to A1, Action and intervention |
| `src/readiness` | An older readiness screen's routes; the controller refuses with "gone" responses (`command: git grep -c -E 'GoneException\|HttpStatus.GONE' origin/main -- src/readiness` -> 6 in `readiness.controller.ts`) | 4 | 212 | Retirement list | |
| `src/registry` | The registry of everything authored: source catalog, contracts, vocabulary, metric contracts, readers, the directory. 1,507 files | 1,507 | 639,913 | Split needed across L1 to L9, AI and S4 | See the next table |
| `src/schema-provisioner` | Creates and keeps a tenant's data tables in step with its active contracts (`src/schema-provisioner/schema-provisioner.module.ts:4-5`); also holds `connector-onboarding` and `metric-onboarding` services | 60 | 11,697 | L10, Tenant onboarding | Split needed: also L7, Readers and connections (connector onboarding), and DL, Delivery to a tenant (`metric-onboarding.service.ts`, `contract-activation.service.ts`). Low confidence; see the closing list |
| `src/support` | The ticket interface; route prefix `support/tickets` | 9 | 507 | SU, Support | |
| `src/tenancy` | Works out which tenant a request belongs to, and the fence between tenant schemas; route prefix `t/context` | 15 | 1,069 | S3, Tenant lifecycle and management | |
| `src/tenant-management` | The tenant register and the tenant lifecycle tools; route prefix `tenants` | 34 | 3,325 | S3, Tenant lifecycle and management | |
| `src/tenant-metrics` | An older operator view of tenant metrics; the controller refuses with "gone" responses (same command as `src/readiness` -> 3) | 2 | 48 | Retirement list | |
| `src/tenant-views` | Read-only, tenant-filtered views for the customer portal (`src/tenant-views/tenant-views.module.ts:2-5`) | 7 | 1,665 | TS, Tenant self-service | |
| `src/test-bench` | A registry of test scenarios and runs with three route prefixes (`admin/test-bench`, `t/test-bench`, `test-bench`) | 11 | 1,257 | Not assigned with confidence | See the closing list |
| `src/types` | Shared type definitions (user, roles, enumerations) | 8 | 522 | Register: shared code, not a function | |
| Files directly in `src/` | `app.module.ts`, `main.ts`, `env-files.ts`, `process-safety-nets.ts` and its two tests: the server's start-up | 6 | 799 | OP, Operations | |
| **Total `src/`** | | **2,568** | **780,588** | | |

### Inside `src/registry`

`src/registry` holds 82% of the lines of `src/` (639,913 of 780,588) and cannot have one owner. Its sub-directories are listed here. Counts are from the same line command, grouped by the third path segment; every file under `src/registry` is a text file, so the file counts equal the tracked-file counts and sum to 1,507.

| Sub-directory | What it holds | Files | Lines | Owning function | Note |
|---|---|---|---|---|---|
| `abc` | A replay harness for an AI authoring panel (`src/registry/abc/orchestrator/abc-orchestrator.ts:2`) with prompts, fixtures and telemetry | 96 | 20,185 | AI, AI services | Which authoring act it serves was not established |
| `bcf` | Authoring, panel review and publication of vocabulary; route prefixes `bcf`, `bcf/registry*`, `ai-telemetry` | 133 | 38,976 | L3, Vocabulary | Split needed: also AI, AI services (`panel/`, `telemetry/`) |
| `concept-registry` | The register of business concepts and its checks | 92 | 21,980 | L3, Vocabulary | |
| `connections` | Connectors, connections and credential lookup; route prefixes `connections`, `connectors` | 14 | 2,901 | L7, Readers and connections | |
| `contracts` | Storage, listing, governance and versioning for every contract family; route prefixes `contracts`, `contracts/chains`, `schema-provisioner/provisioning` | 62 | 13,205 | L2, Source and Admission Contracts | Split needed: also L4, Observation Contracts, and L5, Canonical Contracts (the code is shared by all families); the `schema-provisioner/provisioning` routes belong with `src/schema-provisioner` |
| `d443-phase2-cert-supply` | One certification supply module for the vocabulary; route prefix `bcf/registry` | 7 | 1,656 | L3, Vocabulary | |
| `dto` | Request shapes shared by many registry routes | 46 | 2,890 | Register: shared code, not a function | Split needed when the routes are assigned |
| `execution` | Three controllers: `execution`, `core-map`, `packages` | 11 | 1,471 | S4, Pricing and subscription | The package controller describes itself as "subscription tier CRUD endpoints" (`src/registry/execution/package.controller.ts:21`). The other two controllers were not assigned; see the closing list |
| `framework-approval` | Readers of vocabulary approval records; its former orchestrator is retired (`src/registry/framework-approval/framework-approval.module.ts:2-12`) | 18 | 3,739 | L3, Vocabulary | |
| `framework-calibration` | Calibration records and sampling for the vocabulary panel | 12 | 1,621 | L3, Vocabulary | Could also sit with AI, AI services |
| `gl-classification` | A tenant's classification of its ledger accounts; route prefix `tenant-classification/gl-accounts` | 2 | 294 | L10, Tenant onboarding | Low confidence |
| `harness` | Classifiers and appliers for admission and observation contracts | 28 | 6,629 | L4, Observation Contracts | Split needed: also L2, Source and Admission Contracts (`harness-ac-*`) |
| `harness-apply` | The route that applies a harness plan; route prefix `harness` | 6 | 1,489 | L4, Observation Contracts | Same split as `harness` |
| `legal-entity` | A tenant's legal entities and fiscal calendar revisions; route prefix `t/legal-entities` | 10 | 1,099 | L10, Tenant onboarding | Low confidence |
| `mc-envelope-governance` | Audit records and fingerprints for metric contracts | 11 | 1,935 | L6, Metric Contracts and certification | |
| `mcf` | Metric contracts: authoring, lifecycle, certification, publication, chain audit; 508 files | 508 | 145,635 | L6, Metric Contracts and certification | Split needed: also L9, Chain integrity (`mcf/chain-audit` routes, chain status) and AI, AI services (`audit-panel/`) |
| `meta-schemas` | The schemas that every contract type must satisfy (admission, canonical, extraction, intervention, AI); route prefix `admin/meta-schema` | 23 | 5,519 | L2, Source and Admission Contracts | Shared by L2, L4, L5 and L6; low confidence |
| `metric-audit` | The exchange of metric audit requests, decisions and runs; route prefix `mcf/metric-audit-exchange` | 67 | 18,922 | L6, Metric Contracts and certification | |
| `metric-directory` | The metric directory and its backfill tools; route prefix `metric-directory` | 45 | 11,275 | L8, Metric Directory | |
| `readers` | Reader authoring and reader chain resolution; route prefixes include `reader-authoring`, and also `admission-runs`, `evaluation`, `metric-evaluation`, `actions`, `boundaries` | 20 | 4,089 | L7, Readers and connections | Split needed: also RT, Runtime (the run and evaluation routes) |
| `resolvers` | Resolvers from source fields to concepts for observation and canonical contracts | 15 | 3,312 | L4, Observation Contracts | Split needed: also L5, Canonical Contracts (`canonical-concept-resolver.service.ts`) |
| `seed` | Seed data: 162 files, of which 40 are under `s4/` (a source system's catalog) and 20 under `sfdc/`; three JSON files alone hold 276,632 lines | 162 | 308,078 | L1, Source Catalog | Mostly data, not code. Also holds contract seed files and tenant seed scripts; split needed |
| `source-catalog` | The source catalog and discovery; route prefixes `discovery`, `onboarding`, `sap-reference/*`, `seed-catalog/metrics` | 18 | 6,321 | L1, Source Catalog | |
| `source-extract` | Admission of an extract of a source catalog; route prefix `source-catalog/extract-admissions` | 10 | 1,644 | L1, Source Catalog | |
| `source-identity` | A tenant's source identity; route prefix `t/source-identity` | 7 | 647 | L7, Readers and connections | Low confidence |
| `substrate` | Authoring of an observation chain in one run; route prefixes `contracts/observation-chains`, `registry/substrate`, `source-catalog/stacks` | 33 | 4,699 | L4, Observation Contracts | |
| `tax-registration` | A tenant's tax registrations; route prefix `t/tax-registrations` | 4 | 239 | L10, Tenant onboarding | Low confidence |
| `taxonomy` | Two files: the domain taxonomy and the metric taxonomy | 2 | 638 | MD, Master data | Low confidence |
| Files directly in `src/registry` | 45 files: the older metric catalog, metric definition, metric binding and metric reference services, the intake queue, the fiscal calendar service, the business catalog, `integrity.service.ts` | 45 | 8,825 | Not assigned as a group | Split needed file by file. The project instructions call `IntegrityService` "DEPRECATED" (`barecount-devhub:CLAUDE.md:204 @ 93cc1ea5`) |
| **Total `src/registry`** | | **1,507** | **639,913** | | |

### Everything outside `src/`

| Directory or file group | What it holds | Files | Lines | Owning function | Note |
|---|---|---|---|---|---|
| `scripts/` | 681 files. `scripts/archive/` holds 445 text files and 2,138,178 lines; 107 text files sit directly in `scripts/` with 68,650 lines; the rest are in ten small sub-directories (`comparator`, `mcf`, `audit-output`, `manifest`, `dev-secrets`, `abc`, `evidence`, `__fixtures__`, `lib`, `registry`) | 681 | 2,238,106 | Split needed. Main owner: OP, Operations | Of the lines, 2,023,632 are 31 JSON files under `scripts/archive/s4-catalog-import` (an archived catalog of a source system). Code files (`.mjs`, `.ts`, `.js`, `.cjs`, `.sh`, `.py`) number 304 with 94,529 lines. Each script needs its own disposition |
| `seed-v2/` | An older seed set: `data/` (61 files, 30,947 lines), `scripts/` (7 files, 16,692 lines), `seeders/`, `migrations/` | 83 | 49,768 | Retirement list | Its command is disabled: `"seed:v2": "echo 'ARCHIVED (D109): Use npm run db:restore:s3 instead.' && exit 1"` (`bc-core:package.json:44 @ ec72438b`) |
| `docker/` | SQL that once built the platform database: `redesign/` (353 files, 38,010 lines), `migration-verification/` (17 files, 2,400 lines), `init-schemas.sql` | 371 | 40,442 | OP, Operations | `redesign/` is frozen by a test: "docker/redesign FREEZE guard" (`bc-core:src/database/schema/__tests__/docker-redesign-freeze.spec.ts:2 @ ec72438b`). The guard reads the tree, so the tree is referenced |
| `docs/` | Design notes (`design/`, 138 files of which 26 are binary), evidence captures (`evidence/`), a database diagram source | 171 | 9,183 | DV, Development | The project instructions say documents belong in bc-docs (`barecount-devhub:CLAUDE.md:13-15 @ 93cc1ea5`) |
| `drizzle/` | An older set of database migration files, beginning `0000_dazzling_fabian_cortez.sql` | 45 | 5,432 | Retirement list | `db:generate` and `db:migrate` still exist in `bc-core:package.json:35-36 @ ec72438b`; the project instructions say schema changes are authored in bc-db (`barecount-devhub:CLAUDE.md:263 @ 93cc1ea5`) |
| `tools/` | The shared lint rules (`eslint-config/`), a check of database grants (`grant-drift/`), one proof script (`activation-bridge/`) | 12 | 1,165 | DV, Development | Split needed: `grant-drift/` belongs to OP, Operations |
| `.claude/` | Eight plan and hand-off notes for AI sessions | 8 | 1,452 | DV, Development | One file name carries the date 2026-04-28; candidates for the retirement list |
| `.github/` | Two CI definitions (`ci.yml`, `stale-branches.yml`) and a test of the runner picker | 6 | 804 | DV, Development | |
| `artifacts/` | Two JSON exports under `metric-audit/byte-final-export/` | 2 | 459 | L6, Metric Contracts and certification | |
| `public/` | 22 connector logo images (SVG) | 22 | 446 | L7, Readers and connections | |
| Files at the repository root | 20 files: `package.json`, `package-lock.json` (16,754 lines), TypeScript, lint and test configuration, `docker-compose.yml`, `CLAUDE.md`, `CONTRIBUTING.md`, `.env.example` | 20 | 17,730 | OP, Operations | Build and run configuration |
| **Total outside `src/`** | | **1,421** | **2,364,987** | | |

### An earlier figure of about 166,000 unreferenced lines outside the source tree

An earlier review put the code with no live reference outside the source tree at about 166,000 lines. The main document does not use that figure. The measurements above do not produce it directly. They show the following.

- Everything outside `src/` is 2,364,987 lines.
- Without the 31 archived catalog JSON files (2,023,632 lines), 341,355 lines remain.
- Three trees that the evidence above marks as disabled, frozen or superseded are `seed-v2/` (49,768), `docker/` (40,442) and `drizzle/` (5,432). Together they are 95,642 lines.
- `scripts/` without the archived catalog JSON is 214,474 lines, of which 94,529 are in code files.

The figure of 166,000 comes from a review file that adds those three trees to 70,533 lines of "`scripts/` code files with no live reference (221 of 321)" (not re-checked; reported in artifacts/spine-review/PLATFORM-1-backend-db-infra.md). With today's counts for the three trees that sum would be 166,175. This annex did not repeat the reference analysis of the scripts, so it can confirm 95,642 lines of the figure and not the remainder. Two cautions apply. First, `docker/` is frozen and is read by a CI guard, so it is not code with no reference. Second, the true size of what could be deleted from `scripts/` lies somewhere between the reviewed 70,533 lines and the 2,138,178 lines of `scripts/archive/`, depending on whether archived data files are counted.

## What could not be assigned or verified

### Directories not assigned with confidence

- `src/audit` (2 files, 61 lines). One small service. Its caller and purpose were not traced.
- `src/test-bench` (11 files, 1,257 lines). It describes itself as "E2E chain pressure test infrastructure" (`bc-core:src/test-bench/test-bench.module.ts:2 @ ec72438b`). It could belong to DV, Development, or to the retirement list.
- `src/schema-provisioner`. Assigned to L10, Tenant onboarding, but the forward route from a connector to its source tables (evidence annex, row 9) is also claimed by L7, Readers and connections; open ruling B16 concerns it. The Define step of both functions must settle the owner.
- `src/registry/execution`: the `execution` and `core-map` controllers.
- `src/registry/abc`: which authoring act the panel harness serves.
- `src/registry/meta-schemas`, `taxonomy`, `gl-classification`, `legal-entity`, `tax-registration`, `source-identity`: each is assigned above with low confidence. The four tenant-facing ones (`gl-classification`, `legal-entity`, `tax-registration`, `source-identity`) hold a tenant's own set-up data, and the functional map has no function named for that.
- The 45 files directly in `src/registry` and the 107 files directly in `scripts/`: these need a file-by-file assignment.
- `src/common`, `src/types` and `src/registry/dto` are placed in the register of shared code. The coverage rule allows such a register; the main document does not yet list what is in it.
- bc-audit-app and bc-website-v2 serve no function of the map with confidence.

### Not verified

- Whether the reviewer service of bc-external-audit is running. It runs under another macOS account, which `lsof` cannot inspect without elevated rights. For bc-exchange only the open port was confirmed.
- Whether `origin/main` in each local repository matches GitHub today. No fetch was run, by rule.
- The disk size of the 63 worktrees inside repository folders and of the one under `~/bc-stack`.
- Whether the three CI definitions of bc-infra have run recently, and whether any cloud environment built from bc-infra exists.
- Whether the named archives exist on the Windows laptop.
- The reference analysis behind the 70,533 unreferenced script lines.
- The contents of `~/bc-stack/bc-audit-app`.
- The owner assignments in Table 2 were made from names, header comments and route prefixes. No call graph was built.
