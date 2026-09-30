---
id: serve-moves-and-live-windows
order: 33.7
title: "Serve Moves and Live Windows"
status: drafting
authority: authoritative
depends_on: [the-invariants, upgrade-and-migration, dev-workstation-mac-mini, decision-and-change-procedure, lessons-platform-readiness-umbrella]
governing_sources:
  - The Invariants (Invariant III, Invariant VI)
  - barecount-devhub serve-move tooling (branches claude/serve-move-7, -8, -9; artifacts/serve-move, artifacts/combined-rehearsal, artifacts/w9-serve-move-4 on main)
  - The rehearsal kit (~/.bc-serve-kit) and the Mac stack (~/bc-stack)
  - bc-exchange recorded operator grants
  - Mac Auditor Operations (who authorizes what)
governing_adrs:
  - DEC-4c1396 (bc-db spine is the sole platform schema authoring and apply path)
  - DEC-081931 (the permanent gen- exchange)
  - DEC-44456d (the auditor's home and the Mac auditor service; grants recorded in bc-exchange)
  - DEC-eea376 (platform scope follows the user; the env delta of serve move 7)
  - DEC-b1e9eb (metric output declaration; proposed; the joint-window example)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Serve Moves and Live Windows

How BareCount changes its **live** platform: the bc-core build that serves port 3100, the platform and tenant databases, and the metrics a tenant reads. It describes the procedure as practised in serve moves 7, 8 and 9 (2026-09-29/30) and cites the tooling that enforces each step. Where the tooling and the written practice differ, the chapter says so under Open points.

**Domain owner:** the Platform Controller session (TSK-94f365). The DB Controller schedules migration applies with it, and the Metric Controller runs metric go-lives inside the slots it orders (Platform Controller state capture, 2026-09-30, §B).

**How to read the citations.** Tooling citations name a repository, a ref and a line range:
- `devhub SM9` is barecount-devhub branch `claude/serve-move-9` at `c4f9be13` (draft PR #151);
- `devhub SM8` is `claude/serve-move-8` at `3cdf5dc8` (draft PR #142);
- `devhub SM7` is `claude/serve-move-7` at `7e924a7e` (draft PR #137);
- `devhub main` is barecount-devhub `main` at `750b421c`;
- `audit main` is bc-external-audit `origin/main` at `0412bbfd` (the gen- mailbox);
- `bc-db main` is bc-db `main` at `0d1fb97`;
- a grant is cited by its bc-exchange `grant_id` (the suffix is the first 8 hex of its `text_sha256`).

The "state capture" is the Platform Controller's own state capture of 2026-09-30 ~09:25 UTC (SES-bc9863; barecount-devhub working tree `.claude/briefs-view/platform-state-capture.md`). It is not committed anywhere (see Open points).

---

## Purpose and scope

**A live act** is any act that changes live state. There are three kinds:
- **a serve move:** switching the running bc-core on port 3100 to a new build;
- **a DB migration apply:** a bc-db migration applied to `bc_platform_dev` or a tenant database;
- **a metric go-live:** authoring, certifying, admitting and evaluating metrics for a live tenant.

A **live window** is one announced, operator-granted run of one or more live acts, executed once by a runner script that stops at the first red step. Examples: the W9 U9.5 window ran a migration apply, a serve move and a metric go-live in one granted sequence (grant `2026-09-29T10-04-27-482Z-70963140`); serve move 8 was a window with one act (`devhub SM8`, `artifacts/serve-move-8/live-closure/LIVE.txt`).

**What is not a live act.** Merging code. The operator's standing merge grant says: "Merging never deploys anything: serve moves, database applies and cloud changes still each need my own grant" (grant `2026-09-29T12-44-11-637Z-4e95a6b8`; extended to bc-docs by `2026-09-30T04-11-41-012Z-1bea8fcd`).

**Out of scope:**
- the auditor's own service and desk (see Mac Auditor Operations);
- the day-to-day port and service list (see Development Workstation: Mac Mini and Laptop);
- cloud changes;
- authoring a migration or a metric (see the Onboarding chapters). This chapter covers only how such work reaches live.

**Governing source.** TSK-94f365; grants `70963140`, `4e95a6b8`, `1bea8fcd`; Mac Auditor Operations, "Who authorizes what" ("Anything live (database apply, serve move, cloud, secrets) … Your own recorded grant for that act").

---

## Why it is done this way

Two Foundation invariants shape the procedure.

- **Invariant III, all state is immutable.** "Corrections, adjustments, and reinterpretations are expressed only as new object versions", and supersession "changes future use. It does not modify the retired version" (The Invariants, Invariant III). A live act that produces a wrong object cannot be undone by editing rows. It can only be followed by a governed successor, supersession or retirement. So the act is proven on a throwaway copy first and run once.
- **Invariant VI, evidence is emitted, not inferred.** "If no Evidence or Lineage artifact exists in the authoritative evidence chain for an evaluation, the platform treats that evaluation as not having occurred" (The Invariants, Invariant VI). The live window therefore must not produce evaluations whose evidence is missing or reconstructed afterwards.

The tooling applies the same idea to the operational record of the window itself:
- every runner writes a timestamped transcript as it goes (`devhub SM9`, `run-live-sm9.zsh` l.26–27);
- every rollback writes its observed end state (`rollback-sm9.zsh` l.38–40);
- the transcripts are committed as closure evidence (`devhub SM8`, `artifacts/serve-move-8/live-closure/`).

These transcripts are operational records, not Evidence Objects. The invariants bind the platform's objects; the procedure borrows their discipline for the acts that change the platform.

**Governing source.** The Invariants (Invariant III, Invariant VI); `devhub SM9` `run-live-sm9.zsh`, `rollback-sm9.zsh`.

---

## Terms

| Term | Meaning | Where it is enforced |
|---|---|---|
| **Serve move** | Switching port 3100 from one pinned bc-core build (a clean detached worktree at one commit) to another. Only the `bc-core` block of `~/bc-stack/process-compose.yaml` changes: `working_dir`, `D623_CORE_REF`, the launcher's commit and manifest arguments, the description, and the leading comment. | `devhub main` `artifacts/serve-move/live/make-candidate-2.zsh` l.2–6, l.31–40; any other diff line refuses (l.49–54) |
| **Freeze tree / twin trees** (`freeze-<letter>`, `freeze-<letter>-b`) | Two detached bc-core worktrees under `~/MyProjects/_wt/`, built from the same main commit (for example `freeze-q` and `freeze-q-b` at `802fdee3`). Their dist manifests must be byte-identical. The letters so far run n, o, p, q (serve moves 6 to 9). | `devhub SM9` `build-freeze.zsh` l.4, l.28–39 |
| **Dist manifest** | One line per file under `dist/` (sha256 and relative path, source maps excluded), sorted. The sha256 of that listing is the build's identity. | `devhub main` `artifacts/serve-move/dist-manifest.js` l.2–6 |
| **The kit** | The rehearsal kit. It has two parts: `~/.bc-serve-kit/` (the clone maker `fresh-clone.zsh`, per-rehearsal state directories `state-<name>-<n>`, run directories) and the combined rehearsal harness in devhub (`artifacts/combined-rehearsal/run-combined.sh`, `slots/`). | `~/.bc-serve-kit/fresh-clone.zsh` l.2–5; `devhub SM9` `rehearse-sm9.zsh` l.28, l.56–75 |
| **kit.owner claim** | The file `~/bc-stack/watch/kit.owner`. A rehearsal writes it with noclobber and refuses when another session holds it; teardown deletes it only if it holds the rehearsal's own session id. One kit user at a time. | `devhub SM9` `rehearse-sm9.zsh` l.30, l.36, l.38–40 |
| **Live window** | See Purpose and scope. | Runner scripts `run-live-*.zsh` |
| **EXECUTION CLEARED** | Codex's disposition on a `gen-` thread for "one … window at the exact bytes below": the runner commit and hash, the build commit, the manifest and the inputs. The runner looks the committed response up by its raw sha256 and requires the line `Disposition: EXECUTION CLEARED`. | `audit main` `docs/RESPONSE-Codex-gen-0d0726-01-serve-move-8-execution-cleared-2026-09-30.md`; `devhub SM9` `run-live-sm9.zsh` l.62–67 |
| **Operator grant** | A text the operator approves with a phone code in bc-exchange (`http://127.0.0.1:3040`). It is recorded with `grant_id`, `text` and `text_sha256`. A request is never authority; only a recorded grant is. | bc-exchange `5876541` `src/grants.mjs` l.35–53; DEC-44456d |
| **Conditional grant** | A grant whose text makes its own start depend on an earlier result, so a sequence can continue without the operator present. Example: "after serve move 9 is green, continue the W9 U9.6 window … only if the approved U9.6 continuation rehearsal on that build is green" (grant `2026-09-30T09-25-09-883Z-0cd4fa75`). | The grant text; the continuation's runner must check the condition (see Open points) |
| **Verified rollback** | A rollback that is reported as done only after each restoration is observed independently: the listener's working directory is the old tree and `/api/health` answers 200. A failed or unobserved restoration is reported as HALT with the observed state, never as "rolled back". Exit 12 = rolled back and verified; exit 40 = HALT. | `devhub SM9` `rollback-sm9.zsh` l.2–12, l.31–40 |

**Governing source.** The files named in the table.

---

## The procedure, step by step

Every serve move since serve move 7 has had the same shape. The step names below follow the order the tooling enforces.

### Merge

Engine code is reviewed by Codex and merged by the auditor App under the standing merge grant: "Codex may merge any pull request in bc-core, bc-db, bc-portal and barecount-devhub that it has accepted, at the exact head it accepted, with all required checks green and a passing auditor app attestation" (grant `4e95a6b8`; bc-docs by `1bea8fcd`). A merge is not a live act.

**Governing source.** Grants `4e95a6b8`, `1bea8fcd`.

### Build the twin trees from one pinned commit

`build-freeze.zsh <full main sha> <name>` (`devhub SM9`) builds `_wt/<name>` and `_wt/<name>-b`. It refuses unless:
- the sha is a full 40-hex commit on `origin/main` (l.20–22);
- neither tree exists yet (l.23);
- the tree now serving :3100 has a `.env` (l.24–25).

For each twin, it:
- adds a detached worktree at the sha (l.29);
- runs `npm ci` (l.30);
- builds with `npx rimraf dist && npx nest build && node scripts/validate-build-output.mjs`, not `npm run build`, whose prebuild bin-count guard is stale (l.7–8, l.31);
- copies the served `.env` and appends only the one line in `SM_ENV_ADD`, when set (l.32);
- requires a clean `git status` (l.34);
- writes the dist manifest (l.35).

It ends `BUILD GREEN` only if the two manifests are byte-identical (l.38–39). Example: `freeze-q` and `freeze-q-b` at `802fdee3`, 2145 files, manifest `e44a3c7a…` (`devhub SM9` `evidence/BUILD-freeze-q.txt`).

**The env rule.** `env-delta-check.py` compares by key name and never prints a value (`devhub SM9` l.2). It is green only if all of these hold:
- the new `.env` is byte-for-byte the served one, or the served one plus exactly the one `SM_ENV_ADD` line;
- no `DATABASE_URL`, `TENANT_DATABASE_URL` or `TENANT_OWNER_DATABASE_URL` is present;
- `COGNITO_ISSUER_URL`, when set, ends with `COGNITO_USER_POOL_ID`;
- `BCCORE_NUMERIC_PROFILE` equals the served value (l.4–9, l.29–38).

The one explicit delta so far was serve move 7's `COGNITO_PLATFORM_GROUP=bc-platform`, which bc-core #871 requires (DEC-eea376, decision 1). The grant named it: "Add only the one platform group setting (bc-platform) … and change nothing else" (grant `2026-09-29T17-18-36-345Z-038ea90f`). Serve moves 8 and 9 ran with the env byte-equal (`devhub SM8` `live-closure/LIVE.txt` l.4; `devhub SM9` `evidence/PREFLIGHT-live-4efba252.txt` l.4).

The launcher enforces the same rules again at start. `serve-core-ref-v2.sh` refuses unless:
- the tree is clean and `HEAD` equals the pinned commit;
- the dist manifest equals the pinned manifest;
- no dotenv file it reads carries a DB URL key; the served secret is the only source of DB URLs (`~/bc-stack/serve-core-ref-v2.sh` header l.1–17, checks l.24–40).

**Governing source.** `devhub SM9` `build-freeze.zsh`, `env-delta-check.py`, `evidence/BUILD-freeze-q.txt`; `~/bc-stack/serve-core-ref-v2.sh`; grant `038ea90f`; DEC-eea376.

### Pre-checks on what the build contains

Two written checks precede the rehearsal. Both are read-only.

- **No code that needs unapplied DDL.** The build must not reference any object that a not-yet-applied migration creates. For serve move 9 the check:
  - listed the unapplied migrations from the live ledger (0026 and 0027 applied; no event for 0028, 0029 or 0030) and the objects 0029 and 0030 create;
  - ran `git grep` over `src/` at `802fdee3` for those names, with 0 hits (`devhub SM9` `evidence/NO-UNAPPLIED-DDL-CHECK.md`, "The unapplied DDL", "The search").

  The state capture records why: code needing unapplied DDL "nearly" reached a serve build on 30 Sep, and the rule became "pin the build sha; grep for migration objects" (state capture §D).
- **Check what a removal takes away.** A merged PR that removes or retires something is included only after its live dependents are checked. For serve move 8, PR #896 (retiring the legacy canonical-resolution path) was included only after:
  - read-only queries showed every Kaveri canonical-resolution evidence row was the CC-v2 resolver's `canonical_resolution_run`, with zero rows of the legacy types;
  - a search of the likely callers found no use of the 12 removed routes (`devhub SM8` `evidence/PR896-RESOLVER-CHECK.md` §2–§4).

**Governing source.** `devhub SM9` `evidence/NO-UNAPPLIED-DDL-CHECK.md`; `devhub SM8` `evidence/PR896-RESOLVER-CHECK.md`; state capture §C, §D.

### The kit clone rehearsal, with the forced-failure rollback proof

`rehearse-sm9.zsh <out-dir>` (`devhub SM9`) runs the same live drivers on a throwaway clone of a fresh dump of live.

1. **Snapshot first.** It copies itself and every devhub artifact directory it uses into the run directory, then re-executes from that copy, "so a working-tree edit can never reach a running execution" (l.20–27).
2. **Claim the kit** with `kit.owner` (l.38–40).
3. **Check the builds.** It requires the old twin, the new tree and the new twin each to be clean at their head with their pinned manifest (l.45–48), and the new `.env` to pass the env check (l.49).
4. **Fresh dump.** `take-fresh-dumps-2.zsh` takes a read-only dump of live: `pg_dump` / `pg_dumpall --roles-only` only. It is bound to the live cluster's system identifier and refuses on any other. It reads the tenant databases from the cluster instead of a fixed list, and fails on any empty dump (`devhub main` `artifacts/w9-serve-move-4/tools/take-fresh-dumps-2.zsh` l.2–26).
5. **Fresh clone.** `fresh-clone.zsh` makes a new Postgres container and volume and a new Redis on non-live loopback ports. It refuses:
  - the live name or ports;
  - an existing container or volume (a reused volume keeps its old password);
  - a remaining :3199 listener;
  - a clone that reports the live system identifier.

  It seeds a Secrets Manager stand-in from one read-only read of the served secret's pre-activation version, never printing values (`~/.bc-serve-kit/fresh-clone.zsh` l.8–33).
6. **Restore and serve the old build.** The dump is restored, and the combined kit serves **live's current build from its `-b` twin** (never the live path) on :3199 under the runtime logins (l.51–80; `REHEARSAL-GREEN-FAILPATH-802fdee3.txt` l.8).
7. **Run the move.** `make-candidate-2.zsh` and `window-serve-2.sh` run in `rehearsal` mode, byte-unchanged from live (l.82–88). The same files refuse a rehearsal target that names the live stack (`make-candidate-2.zsh` l.17–18; `serve-move-live.sh` l.30–32).
8. **Check the result.**
   - The clone serves the new tree under the runtime logins.
   - `/api/health` reports `numericProfile` `scaled-decimal-int-v1`, the exact-arithmetic mode (l.90–94).
   - A platform-group token reads a platform route (l.96–100).
   - A Kaveri user reads the Receivable Control Balance detail and sees FY2026-27/P05 = 1997244184.68 with 5 snapshots (l.102–104; `post-check-portal.zsh`).
9. **Forced-failure rollback proof (`FAILPATH=1`).** The rehearsal runs the rollback twice.
   - With an invalid backup, the rollback must **HALT with exit 40** while the clone still serves the new tree, and report "core FAILED".
   - With the real backup, it must end **ROLLED BACK with exit 12**, the clone on the old tree and health 200 (l.105–120).
10. **Teardown.** It removes the clone's containers and volume and releases the claim (l.31–36, l.122).

Serve move 9's rehearsal ran GREEN on 2026-09-30, 08:50–08:56Z, including both failure-path proofs (`devhub SM9` `REHEARSAL-GREEN-FAILPATH-802fdee3.txt` l.22–28).

**Governing source.** `devhub SM9` `rehearse-sm9.zsh`, `REHEARSAL-GREEN-FAILPATH-802fdee3.txt`, `post-check-portal.zsh`; `devhub main` `take-fresh-dumps-2.zsh`, `make-candidate-2.zsh`, `window-serve-2.sh`, `serve-move-live.sh`; `~/.bc-serve-kit/fresh-clone.zsh`.

### A read-only live preflight

Running the live runner before the clearance exists is a full read-only preflight. Every step-0 check runs against the real platform, and the run stops at the missing clearance, "Nothing after this point ran; nothing was changed by this run" (`devhub SM9` `run-live-sm9.zsh` l.62; `evidence/PREFLIGHT-live-4efba252.txt` l.7–8). The preflight transcript is part of what Codex reviews (`audit main` `RESPONSE-Codex-gen-0d0726-01…`, "The read-only live preflight recorded …").

**Governing source.** `devhub SM9` `run-live-sm9.zsh` l.62, `evidence/PREFLIGHT-live-4efba252.txt`.

### The Codex serve review and EXECUTION CLEARED

The executor sends the package on a `gen-` thread (DEC-081931; `Depth: full` for anything that changes platform behaviour, DEC-081931 point 6). Serve move 8's clearance shows what Codex checks:
- the pinned runner commit and its raw SHA-256;
- the grant, re-hashed independently;
- the exact first-parent merges between the served build and the new build;
- the auditor App's attestation of each PR;
- the changed boundary code;
- the removal evidence;
- the runner, rollback, env checker, pin query and portal checker;
- both committed dist manifests;
- the rehearsal and preflight records.

It clears "one serve move 8 window at the exact bytes below" and lists the authorized runner inputs (`audit main` `docs/RESPONSE-Codex-gen-0d0726-01-serve-move-8-execution-cleared-2026-09-30.md`). A clearance authorizes nothing else: "No database migration, cloud change, signing, PR merge, portal deployment, or second serve window is cleared" (same file).

**Codex may hold.** Serve move 7:
- was held first for a custody gap (`RESPONSE-Codex-gen-c5cb9f-01-serve-move-7-changes-required-2026-09-29.md`);
- was then halted because the runner's rollback reported "rolled back" even when a restoration failed. At round two Codex escalated to the operator "rather than opening a third round" (`RESPONSE-Codex-gen-c5cb9f-02-serve-move-7-halt-2026-09-29.md`);
- ran only after a successor runner with verified rollback was cleared, under an added operator grant (`2026-09-30T00-46-47-364Z-a8aeb3c9`; `RESPONSE-Codex-gen-c5cb9f-03-…-execution-cleared-…`).

**Governing source.** DEC-081931 points 3, 5, 6 and 8; the named Codex responses on `audit main`; grant `a8aeb3c9`.

### The operator grant in bc-exchange

The session posts the exact text as a request (`POST /api/requests` with `text`, `requestedBy`, `thread`). The operator approves it with a phone code, and bc-exchange records the grant with the exact stored request text (bc-exchange `src/grants.mjs` l.17–21, l.35–53; `src/server.mjs` l.216–233).

The serve-move grants so far share one wording shape. Example, serve move 8: "run serve move 8 on the Mac platform, stopping at the first red step and rolling back on red. Take a fresh read-only backup. Serve bc-core main commit acc30c6d… on port 3100; on top of the served build it adds pull requests 860, 893, 894, 895 and 896 and nothing else. Keep the served environment exactly as it is and leave bc-portal unchanged. Serve it only after Codex records EXECUTION CLEARED for exactly those bytes. If any listed pull request is missing from that commit, or the cleared bytes differ, do not start." (grant `2026-09-30T05-07-40-089Z-eb2b8c1a`). Serve move 9 uses the same shape (grant `2026-09-30T09-25-39-033Z-c8632c8e`).

**Text rules:**
- **No underscores** in grant text. The desk's own input says "(no underscores)" (bc-exchange `public/index.html` l.306).
- The Platform Readiness lessons add: avoid email addresses and links, "so that nothing in them can be changed by a chat window" (Lessons: Platform Readiness umbrella, lesson 6).
- The grant text itself is not validated for these characters (see Open points).

**Conditional grants.** A grant may make its own start depend on earlier results, for example grant `0cd4fa75` (see Terms). The condition is part of the granted text. A stop "stands on its own and continuing past it needs a new grant" (same grant; also grant `70963140`).

**Mistaken grants** are withdrawn by a counter-grant, never edited. Example: grant `2026-09-30T04-16-40-014Z-bed807b6` was withdrawn by `2026-09-30T04-19-43-857Z-1df55ae8` ("approved by mistake").

**Governing source.** DEC-44456d decision 1; bc-exchange `5876541` `src/grants.mjs`, `src/server.mjs`, `public/index.html`; grants `eb2b8c1a`, `c8632c8e`, `0cd4fa75`, `70963140`, `bed807b6`, `1df55ae8`; Lessons: Platform Readiness umbrella.

### Announce the window

Before the run, the executor commits a `LIVE WINDOW STARTING` message on a `gen-` thread. It names:
- the grant and the clearance (file, commit, raw SHA-256);
- the runner and its steps;
- the rollback exits;
- what is not touched.

When the run ends, the executor commits `LIVE WINDOW ENDED` with the end state (`audit main` `docs/MSG-Claude-gen-dcff33-01-serve-move-8-window-start-2026-09-30.md`, `…-02-serve-move-8-window-ended-2026-09-30.md`).

The announcement is what pauses DevHub merges. The operator's standing clarification says: "The umbrella session announces live windows on the exchange before they start and when they end; do not merge DevHub during an announced live window" (grant `2026-09-28T14-36-38-930Z-ce08a39b`; the merge go it clarifies is `2026-09-28T15-47-38-822Z-9603bf05`).

DevHub's Servers page also refuses to start, stop or restart bc-core while a live window is open. It fails closed when it cannot check (`devhub main` `src/lib/server-control.js` l.8–10, l.31–66; `src/index.js` l.700–713). Its detection has a gap (see Open points).

**Governing source.** The named gen- messages; grants `ce08a39b`, `9603bf05`; `devhub main` `src/lib/server-control.js`, `src/index.js`.

### Run the window; roll back on red

The runner (`run-live-sm9.zsh`, `devhub SM9`) takes every script it runs from the **cleared** devhub commit by `git archive`, never from the working tree (l.3–4, l.40–43). It runs these steps in order:

**Step 0, verify; changes nothing** (l.40–67):
- the grant exists in bc-exchange and its text re-hashes to its `text_sha256`;
- the build commit is on `origin/main`;
- every PR the grant lists is merged into it;
- :3100 serves the old tree;
- both new trees are at the build commit, clean, with the cleared manifest;
- both new `.env` files are byte-equal to the served one;
- the newest 5 accepted Kaveri evaluations are pinned `scaled-decimal-int-v1` (`eval-profile-pins.sql`);
- **last**, the committed Codex response whose raw sha256 equals `DISPOSITION` says `EXECUTION CLEARED`.

**Step 1, backup:** a fresh read-only dump with `take-fresh-dumps-2.zsh` (l.69–72).

**Step 2, the serve move** (l.74–85). `make-candidate-2.zsh live` derives the candidate yaml and `pins.env`. `window-serve-2.sh live` then:
- **C0**, a read-only package check (`serve-move-live.sh check`);
- **G**, the old serve healthy and ready under both runtime logins, with the served secret version and runtime verifiers recorded;
- **S1**, stop bc-core;
- **A5/A6**, via `serve-move-live.sh move`:
  - back up the yaml and install the reviewed candidate;
  - start and require health and readiness;
  - require the listener's cwd to be the new tree;
  - require the served-identity boot line;
  - require the runtime sessions;
  - require 60 s in which no governed work fires.

  Any failure after the install restores the byte-identical pre-move yaml (`window-serve-2.sh` l.44–83; `serve-move-live.sh` l.89–117). Exits: 0 green; 10 not started (nothing changed); 12 rolled back; other values HALT.

**Step 3, post-serve** (l.87–93):
- the :3100 cwd is the new tree;
- `/api/health` 200 with `numericProfile` `scaled-decimal-int-v1`;
- the pins are still 5/5.

**Step 4, read-only regression:** the Kaveri detail through the served portal on :3000 (l.95–98).

**On red after step 2:** `rollback_core` runs `rollback-sm9.zsh live`. Exit 12 means rolled back and verified, and the runner says "Continuing needs a new operator grant"; exit 40 is HALT, "touch nothing further" (l.32–38).

A red step before the serve changes nothing ("Nothing after this point ran; nothing was changed by this run", l.28).

Serve move 8 ran this way on 2026-09-30, 05:15:02–05:16:46Z, GREEN at every step (`devhub SM8` `live-closure/LIVE.txt`).

**Governing source.** `devhub SM9` `run-live-sm9.zsh`, `rollback-sm9.zsh`, `eval-profile-pins.sql`; `devhub main` `make-candidate-2.zsh`, `window-serve-2.sh`, `serve-move-live.sh`; `devhub SM8` `live-closure/LIVE.txt`.

### Independent read-only verification

The executor's report is not proof. The controller verifies the result read-only and independently:
- which tree the :3100 listener runs;
- that tree's `HEAD`;
- `/api/health` and its numeric profile;
- the relevant live data.

This is the last link of the grant chain: "the coordinator checks the live result read-only" (Lessons: Platform Readiness umbrella, lessons 6 and 7).

The end-of-window message records such a re-check. Example: "End state, re-checked read-only at 05:16:53Z: :3100 serves `_wt/freeze-p` …" (`audit main` `…gen-dcff33-02-serve-move-8-window-ended-2026-09-30.md`). Codex then reviews the closure evidence: the backup hashes, the transcript, the listener and health, the pins, the portal checkout and the Kaveri check (`RESPONSE-Codex-gen-0d0726-01…`, last paragraph; `RESPONSE-Codex-gen-0d0726-02-serve-move-8-closure-accepted-2026-09-30.md`).

Read-only database checks run inside `BEGIN READ ONLY` (`devhub SM9` `run-live-sm9.zsh` l.30; `devhub SM8` `evidence/PR896-RESOLVER-CHECK.md`, "Method").

**Governing source.** Lessons: Platform Readiness umbrella (lessons 6, 7); the named gen- messages and responses.

---

## DB migration applies in this frame

**Where DDL comes from.** "Every platform schema change is authored once as a bc-db forward migration … and applied to every environment only by the spine runner with one infrastructure.schema_migration_event row per apply"; bc-core `docker/redesign` is frozen (DEC-4c1396, Decision). A migration apply is a live act. It needs the operator's database "yes" (the Database Change Protocol) and its own apply grant. Example: bc-db 0027's DBCP lists the recorded "yes" grants and, separately, "Operator's direct grant for the apply (the first step of the one W9 U9.5 window)" (bc-db main `docs/dbcp/DBCP-platform-0027-mcf-served-execute-2026-09-29.md`, table rows 1 and 5). The same DBCP records the clone proof: the runner applied the migration "from a staged directory holding only 0027"; a second run was skipped; the governed rollback and re-apply were checked (same file, "the clone" and the proof table).

**Number order.** Migrations are applied to live in number order. This is a Platform Controller ruling with the DB Controller (state capture §C), and the reason is visible in the live ledger. A read-only query of `infrastructure.schema_migration_event` on 2026-09-30 shows:
- `0000_baseline` adopted;
- 0004–0007, 0009–0019, 0021–0024, 0026 and 0027 applied;
- no event for 0001, 0002, 0003 or 0008.

0020 and 0025 do not exist on bc-db main, so those are numbering gaps, not holes. 0001, 0002, 0003 and 0008 are on main but were never applied on live. The state capture records the consequence: CI and clones have objects that live lacks (state capture §A; the DB Controller's finding).

**Merge order is not number order.** On bc-db main, 0029 is merged (`0d1fb97`) while 0028 is still an open PR (bc-db #95). An apply that followed merge order would put 0029 on live before 0028. The state capture records that "the runner has no ordering gate" (§C). This chapter could not confirm that from the runner's code (see Open points).

**Joint windows.** When a migration and a code change each break something without the other, they go live in one window. The example is bc-db 0030 (metric output declaration, ADR DEC-b1e9eb, proposed).
- **Why the DDL can't go first.** Once 0030 is applied, a new metric version needs a declaration. Only the new authoring slice writes one. Applied alone, 0030 would block new-metric authoring (state capture §C).
- **What the DBCP says.** bc-db #98: "apply only in the same window as the bc-core build whose `mcf-cert-writer` writes declarations. The DB yes comes after that build is accepted."
- **Why the code can't go first.** The pre-check above keeps such code out of a serve build until its DDL is applied (`devhub SM9` `evidence/NO-UNAPPLIED-DDL-CHECK.md`).

So neither half can go alone, and the grant names both.

**Governing source.** DEC-4c1396; bc-db main `docs/dbcp/DBCP-platform-0027-mcf-served-execute-2026-09-29.md`; bc-db #95, #98; live ledger read-only query (2026-09-30); state capture §A, §C; DEC-b1e9eb.

---

## Metric go-live windows

A metric go-live is a live window in the same frame:
- rehearsal on a clone;
- an operator grant;
- an announced window;
- a runner that stops at the first red step;
- read-only verification.

The W9 U9.5 and U9.6 windows were announced like serve moves (`audit main` `MSG-Claude-gen-d2e52d-05-live-window-start-u95-2026-09-29.md`, `…-06-live-window-ended-u95-…`; `MSG-Claude-gen-afb098-01-live-window-start-u96-2026-09-30.md`, `…-02-live-window-ended-u96-…`).

**Codex has no role in metric onboarding.** The grant: "Codex has no role in metric onboarding. Authoring, certifying, admitting, binding and evaluating metric contracts, and the source reads they need, run under my grants and the platform's own gates, including the independent source value check before a batch goes live. Codex does not review, clear or audit those acts. Codex keeps reviewing engine changes: code, schema, database grants, auth, cloud and serve moves." (grant `2026-09-29T08-34-38-377Z-ead781aa`). So a metric go-live has no EXECUTION CLEARED step. Its authority is the operator's grant and the platform's own gates.

**Order in the live sequence.** A metric window that needs a new build waits for that build's serve move, and its grant can say so. Example: grant `0cd4fa75` starts only "after serve move 9 is green", and only if a continuation rehearsal on that build is green.

**Accepted exposure.** For synthetic Kaveri, the operator accepted that "one accepted live metric value may be served before its comparison with the reviewed clone value". Before any real customer tenant, "a hold that keeps a value unseen until checked is required" (grant `2026-09-29T08-01-36-596Z-1fa98663`).

**Governing source.** Grants `ead781aa`, `0cd4fa75`, `1fa98663`; the named gen- messages.

---

## Rules that must never be broken

Each rule comes from an incident.

| Rule | Incident behind it | Enforced by |
|---|---|---|
| Never report "rolled back" unless each restoration was observed. | Serve move 7's first runner ignored rollback failures and reported "rolled back" unconditionally; Codex halted it (`RESPONSE-Codex-gen-c5cb9f-02…`). | `rollback-sm9.zsh` exits 12 or 40 only (`devhub SM9` l.2–3, l.39–40); rehearsal FAILPATH proof |
| Run scripts from a snapshot, never from a working tree. | Executors edited scripts mid-run twice (state capture §D); rehearsal lesson "2026-09-29, r22" (`rehearse-sm9.zsh` l.20–21). | Rehearsal re-executes from a copy (l.22–27); live runner uses `git archive` of the cleared commit (`run-live-sm9.zsh` l.42) |
| Never serve code that needs DDL not yet applied on live. | Code needing unapplied DDL nearly reached a serve build (30 Sep; state capture §D). | Pin the build sha (`build-freeze.zsh` l.20–22); the written grep check (`NO-UNAPPLIED-DDL-CHECK.md`) |
| Never dump live while a live window runs; never overlap kit use. | A coverage rehearsal dump (r9) started at the U9.6 window start, 2026-09-30 01:12Z (state capture §D). | `kit.owner` noclobber claim (`rehearse-sm9.zsh` l.38–40); a live-quiet `pgrep` guard exists in the coverage and U9.6 drivers only (see Open points) |
| Never reuse a rehearsal volume. | A reused named volume kept its old password and five rehearsals failed like a flake (Lessons: Platform Readiness umbrella, lesson 8). | `fresh-clone.zsh` refuses an existing container or volume (l.13–16) |
| Only a recorded bc-exchange grant is authority, and it is re-hashed. | A grant approved by mistake (`bed807b6`) was withdrawn by counter-grant `1df55ae8`. | `run-live-sm9.zsh` l.45–47 re-hashes the grant from `/api/grants-list`; DEC-081931 point 8 |
| A stop stands; continuing needs a new grant. | U9.6 window 1 stopped when a reviewer passed a malformed uuid, postgres log 01:17:43Z (state capture §D). | Runner exit messages (`run-live-sm9.zsh` l.28, l.37); grant texts `70963140`, `0cd4fa75` |
| Never re-roll a semantic REJECT; never take a pass after a fail on identical bytes. | A DSO rehearsal was REJECTED (cr2) and then VERIFIED (cr3) on identical bytes; cr3 was not used (state capture §C). | Operator rule "keep gates, re-run only structural parks" (state capture §C); no tooling cited |
| Do not merge DevHub during an announced live window. | (Standing operator rule.) | Grant `ce08a39b`; DevHub bc-core controls guard (`server-control.js`) |
| Do not push to a PR while Codex is in its approve-then-merge step; update stacked branches before approval. | A push dismissed Codex's approval; bc-docs #105 approvals were dismissed on a merge-base change (state capture §D). | No tooling cited |
| Apply migrations in number order. | 0001, 0002, 0003, 0008 were never applied on live (live ledger, 2026-09-30). | Ruling only (state capture §C); a DB Controller gate is planned |

**Governing source.** The files, grants and responses named in the table; state capture §C, §D; Lessons: Platform Readiness umbrella.

---

## Open points

These are places where the sources are silent or disagree. They are recorded here, not resolved.

1. **Live-quiet guard.** The rule "never dump live while a `run-live-*` script executes" is enforced by a `pgrep` guard in three drivers, all on unmerged branches:
   - `artifacts/coverage-arc/tool/rehearse-pilot.zsh` (branch `claude/coverage-arc-groundwork`, l.50–53);
   - `artifacts/w9-u96-dso-grain/live/rehearse-u96.zsh`;
   - `artifacts/tsk-b14769-calibration/calib-clone.zsh` (branch `claude/w9-u96-dso-grain-note`).

   The serve-move rehearsal (`rehearse-sm9.zsh`) and the shared dump tool (`take-fresh-dumps-2.zsh` on devhub main) have no such guard. They rely on the `kit.owner` claim, which only serializes kit users and does not detect a live window.
2. **DevHub's live-window detector misses serve moves.** `openLiveWindow` treats a grant as a window only if its text matches `/live window/i`. The "window ended" marker is a committed file matching `docs/MSG-Claude-*live-window-ended*` (`devhub main` `src/lib/server-control.js` l.41; `src/index.js` l.711). The serve-move grants (`038ea90f`, `eb2b8c1a`, `c8632c8e`) and the U9.6 continuation grant (`0cd4fa75`, "U9.6 window") do not contain "live window". The serve-move end messages are named `…-window-ended-…`, not `…live-window-ended…`. So the bc-core control guard does not see a serve-move window. The DevHub merge pause itself rests on the announcement and grant `ce08a39b`, not on this code.
3. **The migration runner's ordering.** The state capture says the spine runner has no ordering gate and that the DB Controller's "M3 gate" will enforce number order (§C). This chapter did not find the runner's source in bc-db main (`scripts/` holds only `check-layout.sh`), so the claim is not verified against code here.
4. **Grant text characters.** The no-underscore rule is guidance in the desk's placeholder text and in the lessons chapter. `addRequest` and `recordGrant` do not check the characters (bc-exchange `src/grants.mjs` l.17–53).
5. **Conditional grants have no generic check.** Grant `0cd4fa75`'s conditions (serve move 9 green; the approved continuation rehearsal on that build green) must be checked by that window's own runner. No shared tool verifies a grant's conditions, and this chapter did not read the U9.6 continuation runner.
6. **Which twin a rehearsal uses.** The written practice says one twin is served and the other is used by rehearsals. In the tooling:
   - the clone starts on the **currently served** build's `-b` twin (`freeze-p-b`);
   - it moves to the **new** build's primary tree (`freeze-q`), the same path the live runner will serve (`rehearse-sm9.zsh` l.6, l.41, l.80; `REHEARSAL-GREEN-FAILPATH-802fdee3.txt` l.14);
   - the new `-b` twin is checked (clean, head, manifest) but not served.

   The live tree is never touched by a rehearsal. The tree that will become live is.
7. **Portal steps.** bc-portal is not a pinned build. Serve move 7 fast-forwarded the shared checkout and restarted it inside the window (`devhub SM7` `live-closure/LIVE.txt` l.16). Serve moves 8 and 9 left it unchanged. No written rule yet says when a portal change needs its own rehearsal.
8. **Stale runbook.** `~/bc-stack/README.md` ("bc-core :3100 is a PINNED build") still describes the v1 launcher, `_wt/core-ref-9d0dc5aa` as served, and a manual move procedure. The live yaml runs `serve-core-ref-v2.sh` from `_wt/freeze-p` (the bc-core block of `~/bc-stack/process-compose.yaml`).
9. **Tooling is on draft branches.** The serve-move 7–9 runners, rollbacks and evidence are on draft PRs #137, #142 and #151, not on devhub main. Each move has a copied, renamed runner (`run-live-sm7/8/9.zsh`). The shared drivers they call are on main.
10. **The state capture is not committed.** The number-order ruling, the incident list and the controller ownership come from an uncommitted working-tree file. They have no durable citation until they are recorded in DevHub or bc-docs.
11. **Missing voice checklist.** Documentation System cites `bc-docs/scripts/reference/aws-rewrite-checklist.md` for voice and forbidden vocabulary. That file is not on bc-docs main.

**Governing source.** The files named in each point.

---

## Boundaries with other chapters

- **Upgrade and Migration** covers schema evolution in general. This chapter covers only how an apply is scheduled and run as a live act.
- **Mac Auditor Operations** covers the auditor service, the desk, and who authorizes what.
- **Development Workstation: Mac Mini and Laptop** covers services, ports and the stack scripts.
- **Decision and Change Procedure** covers ADRs and the DevHub change-record pair each session writes.
- **Lessons: Platform Readiness umbrella** records the grant chain (lesson 6) that this chapter details for serve moves.
