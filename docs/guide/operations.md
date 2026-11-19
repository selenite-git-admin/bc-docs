---
id: guide-operations
order: 46.27
title: "Operations"
status: drafting
authority: authoritative
depends_on: [platform-refactor-program, platform-refactor-program-definition-operations, vocabulary, decision-and-change-procedure]
governing_sources:
  - Platform Refactor Program (the method; the order of work; the reference run; the hold on the engine; rulings G12 to G15, G35, B1, B2, G37 and G38)
  - The Definition of Operations (the design this chapter must agree with)
  - bc-infra ops/README.md and each ops/<command>/README.md (the commands as built)
  - barecount-devhub scripts/reference-run/README.md (the reference run and the taking of the fixed copy, as built)
  - bc-db README.md, tools/runner/README.md and docs/dbcp/ (the schema-change path as practised)
  - Vocabulary (the approved words)
governing_adrs:
  - DEC-71f15e (the Platform Refactor Program)
  - DEC-4c1396 (bc-db is the only place schema changes are written and applied)
  - DEC-ecd55c (credentials live in AWS Secrets Manager)
  - DEC-e50b83 (the port table)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Operations

> **Status of this chapter.** It is a draft. It was merged as a draft by bc-docs pull request 241 (merge commit `22357686b8c3010a0e76b228002e1c4fe4fbca0b`). The auditor reviewed that draft: the reply on exchange thread gen-f7124c is ACCEPTED WITH BOUNDARY. The operator approved this chapter as merged at commit `98cd7d3cd242aa74c6db9f5cc726e80daa156e75` (file SHA-256 `4e37f3b036538e27cac7852f4efc70f74a68ae2808424223229cae7ece66f6e1`) as the chapter given to the Prove worker, by grant `2026-11-19T00-23-25-024Z-cfaca707` (text SHA-256 `cfaca7073ee49f8bf9edb57ea125a7ca04fcbb170ff10c97935ba6a92bf2ec85`). **The text you are reading is later than the bytes the operator approved under that grant (desk request 515). It is NOT approved for Prove until the operator approves it at its new hash.** It alters the section "The script scan" and the sentences listed under "How to read this chapter", "Changed since the approved bytes". That grant approves the earlier bytes only, so the operator's approval is asked again for the new bytes. The auditor accepted an earlier form of the later text as an unapproved draft (bc-docs pull request 243, merge commit `1b5d44fab8c0037ee49567e9d1f4b7ed74961971`; the reply on exchange thread gen-ddcf4d is ACCEPTED WITH BOUNDARY) and required one correction to this chapter before that approval is asked: the script scan's result is compared file by file with the triaged list, not by folder, rule and count. This text makes that correction. It is also brought level with four changes merged on 2026-11-19 (bc-infra pull requests 88, 89 and 90 and barecount-devhub pull request 400), and every result it quotes from a command of bc-infra `ops/` was read again after them. The auditor has not reviewed the text in this form. Operations (function OP of the [Platform Refactor Program](../development/platform-refactor-program.md), decision DEC-71f15e) is not locked, so this chapter binds nothing yet. By ruling F5 a chapter is locked when its function is locked. By ruling G37 (the operator's grant `2026-11-18T15-40-34-728Z-0914e87d`) Operations is not locked in phase 3: its Lock step stays open by name and is done when condition P3-C7 is met. The same ruling says this chapter is reviewed by the auditor before the Prove run, and that the operator's approval of it is asked separately. Until Operations is locked this chapter is the best description available, and each statement is checked against the commands before it is relied on.

## How to read this chapter

This chapter is written for a person or a session that did not build Operations' commands. It says, for each act of Operations, what the act is, the one command that performs it, what the command reads and writes, its exit codes, whose grant it needs, where its record is kept, and what a clean result looks like today.

- **The design** is the annex [The Definition of Operations](../development/platform-refactor-program/definition-operations.md). Where this chapter and that annex differ, the difference is a defect to be reported, not resolved by the reader.
- **The commands** are in the repository bc-infra, folder `ops/`. Each has a README of its own. This chapter gives what is needed to run each command and read its result. The README holds the full account. Three acts are performed by commands kept in two other repositories, barecount-devhub and bc-db; their sections say so.
- **"Today"** means 2026-11-19. Unless a line says otherwise, a result of a command of bc-infra `ops/` printed below was read that day between 02:18 and 02:20 UTC, with the read-only verbs only, from the shared copy of bc-infra at commit `7e16520d3bfeda1549baa88b27c3bd9dd749210a`, which was level with its main branch. That is the fifth reading, and the only one made after the four changes named under "What changed on 2026-11-19" below. In it every verb this chapter quotes a result for was run again: `status`, `check` and `verify` of `ops/host-files`, `ops/backup`, `ops/secrets-identity`, `ops/reference-host` and `ops/reference-runtime`; `status` and `check` of `ops/secrets-route`, `ops/script-scan` (its `check` in both forms), `ops/environments`, `ops/schema-compare` and `ops/launch-agents`; `status` and `verify` of `ops/serve-move`. No `do`, `retire`, `put-back` or `undo` was run. A result of today is a reading, not a promise: run the verb and compare.
- **What was not read again.** Some statements rest on a look that is not a verb of a command: the desk, DevHub's program record, the supervisor's file, the local runbook, the kept copy of the login profile file, the records folder of the reference run, the calendar entry of a launch agent, and a repository variable. They stand as read on 2026-11-18, and each such sentence gives that date. Read again on 2026-11-19, between 02:17 and 02:21 UTC: `launchctl list`, the main branches of bc-docs, bc-infra, bc-db, bc-core, barecount-devhub and bc-external-audit after a fetch of each, and bc-db's register of migrations awaiting apply. bc-demo was not read again.
- **What changed on 2026-11-19.** Four changes were merged that day, each reviewed by the auditor at its exact head.
  - bc-infra pull request 88 (merge commit `f79be43b5469e6c84ae4a35c5edaa99ea946d041`; exchange thread gen-3e7cd4): all twenty host files of the custody manifest have their bytes in bc-infra, and none is named from barecount-devhub.
  - bc-infra pull request 89 (merge commit `bc0ff75be03fb588c6649071d33776bfe3fdb429`; thread gen-9551ac): `ops/launch-agents` and `ops/dev-secrets` were added. See "The launch agents check" and "The secret writers in custody".
  - barecount-devhub pull request 400 (merge commit `5614f134557b51e45251dc666634af9284ec10dc`; thread gen-3d04e4): the host installer, the five host sources, the three secret writers, the script that changed the database superuser's password, and the two request-file helpers left that repository.
  - bc-infra pull request 90 (merge commit `7e16520d3bfeda1549baa88b27c3bd9dd749210a`; thread gen-c2b172): the inventory of readers of `ops/secrets-route` follows those moves.
- **The auditor has not read the host.** The auditor reviewed those four changes by commit. Its replies report no read of the development machine, and two of them say so in words. Every statement in this chapter about the host is a reading of the Chief or of a worker.
- **Earlier readings, kept as history.** The draft merged by pull request 241 gave the readings of 2026-11-18, 16:54 to 16:57 UTC, from bc-infra `18cd69e0e4c4778942c47c4981ab543809057776`. A second reading was made that day between 17:12 and 17:16 UTC, after the retire of 17:10 UTC (see "Host-file custody"). A third was made on 2026-11-19 between 00:47 and 00:48 UTC, from bc-infra `f5cfc291f181f30fccc5f314eb52b6ff573c86bd` (pull request 87, which records the first run of the installed nightly backup script). A fourth, of the script scan only, was made between 01:08 and 01:09 UTC from the same commit. Where a sentence below names one of those times, it is the record of that reading and not today's result.
- **Changed since the approved bytes.** Against the chapter as merged at `98cd7d3c`, this text changes:
  - the status note, one line of the front matter (the rulings named), and the bullets of this section from "Today" to this one;
  - under "The acts of Operations", the paragraph on ruling G38 and the paragraph after it on the two folders that are not acts;
  - two rows of the table under "The hard line" (a launch agent; a secret);
  - under "Before any act", the sentences on bc-infra's commit and on the worktrees, and, under "What to do on WRONG or COULDNOT", the place of a listed line, the sentence on a shrinking, and one halt case;
  - under "What is special to a Prove run", one sentence of the rule, the last two rows of the worker's table, the date of the second read of the register, and the last sentence of the Chief's statement;
  - under "Start, stop or restart a service", the paragraph on a restart of the supervisor, the end of "Older texts", and the date of one read of the desk;
  - in the secrets route check, the result today, the date of one read of the desk, the line the draft raised, and point 6 of its list;
  - one sentence of "The secrets identity hook" and two of the section on the schema comparison (dates only);
  - in "Take a backup", the paragraphs "What has been done", "A clean result today" and "The nightly backup"; in "Restore a backup to a disposable copy", "A clean result today";
  - one sentence of "The record" under "The reference run" (a date only);
  - the whole of "The script scan" from "Line words of its own" on;
  - in "Host-file custody", "What it is", "A clean result today", and the date of one read of the desk in the paragraph on the retire;
  - the two new sections "The launch agents check" and "The secret writers in custody";
  - in "What is not yet true", the dates of the reads, the items on the function as a whole, and items of sections 1, 2, 3, 6, 7 and 10;
  - and "Sources".

  Nothing else is changed. The rules of the Prove run are as the operator approved them: no reference run, no preflight, no proof of a migration while the register is empty, and no act that needs the operator's grant other than through its read-only verbs.
- **What to do on a non-clean result** is one rule for every command and is given once, under "Before any act". A section adds to it only the lines that are known for its command today.
- **A source outside bc-docs** is cited by repository, path and commit. The commits are listed under "Sources".
- **A line that starts `OPEN:`** would mark a point that needs the operator's or the auditor's decision. The chapter holds no such line today. A thing that is simply not established is said in a plain sentence. Nothing is guessed.

## What Operations is

Operations is how the platform is run and changed on the machines it runs on. It keeps eight things: environments, services, builds, settings and secrets, the schema-change path, backups, where the checks on every change run, and cloud infrastructure. It also keeps the reference run, the check that a change to the engine has not moved a value (Definition, "What Operations is").

Operations does not decide what a tenant is or who may sign in, what a contract means, or what a session may do.

### Words

| Word | Meaning | Source |
|---|---|---|
| `dev`, `stg`, `prod` | The one list of environment names. `dev` is the development machine together with the cloud resources named `dev` that serve it. It is the only environment that exists. | Ruling G13; Definition, section 1 |
| Live | Not an environment. The served platform inside one: on `dev`, the services on their fixed ports and the databases they use. | Definition, section 1 |
| Disposable copy | A restored copy of the databases on other ports, made for one check and then destroyed. "Rehearsal", "clone" and "kit" in older texts mean this. | Definition, section 1 |
| `test` | Not an environment. A suffix that automatic checks give to databases they create and destroy. | Definition, section 1 |
| Live act | An act of Operations that changes live state. | Definition, "What Operations is" |
| Live window | The announced, granted run in which a live act is performed. | Definition, "What Operations is" |
| The supervisor | The one program that keeps the services of the development machine running. Its file, `~/bc-stack/process-compose.yaml`, is the one statement of what runs. | Definition, section 2 |
| Build | One commit of a repository's main branch, built once in a tree of its own, identified by the commit and by the hash of the list of its built files. | Definition, section 3 |
| The desk | The approval desk, where the operator records a grant. | Program, "Words this document uses" |
| The Chief | The one session that decides the order of units inside a phase, opens and closes workers, and reports to the operator. | The annex "How the Work Is Done", "Who does what" |
| A worker | A session opened for one unit of work. It decides nothing beyond its unit. | The annex "How the Work Is Done", "Who does what" |

## The acts of Operations

The table is the Definition's (section 10), unchanged. Each act has a section of its own below, in the table's order.

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

**The operator's ruling on this table** (grant `2026-11-18T14-11-21-285Z-ca66e1ef`, text SHA-256 `ca66e1eff3611c343a8b327ee48e2ab195b83d0b15f8699403c77edfdd107be8`; Definition, section 10). The table stands as approved for three acts: taking a backup, restoring a backup to a disposable copy, and running the reference run. None of them changes live state, and none needs the operator's grant each time, once its command has been reviewed, switched on where it has a switch, and run for real once. The first real run of each of those commands is the operator's to grant. For the reference run that was grant `2026-11-18T09-34-48-980Z-b0a93f42`; for the backup take and the restore proof it is grant `2026-11-18T14-10-38-847Z-8fa8e994`. After that first run the Chief makes further runs of the same command without a new grant and reports each to the operator. A reference run still decides nothing by itself. The ruling covers only those three acts as the committed commands perform them. Taking a new fixed copy, any write to a live database, applying a migration, serving a build, restarting the engine, any cloud change other than the upload the backup has always made to its one prefix, any change to a launch agent, and any credential or secret write keep the grant the table gives them.

Which acts have a command with the four verbs today:

| Act | Command today |
|---|---|
| Start, stop or restart a service | none with four verbs; the host script `~/bc-stack/servers.sh`, in custody |
| Serve a build; return to the previous build | bc-infra `ops/serve-move` |
| Show what a service was given (names only) | bc-infra `ops/secrets-route` (`status`, `check`) |
| Prove a migration on a restored copy | none of Operations; bc-db's proof scripts and runner. `ops/schema-compare` performs the comparison only |
| Apply a migration | bc-db's governed runner, inside a window script |
| Take a backup | bc-infra `ops/backup do take` |
| Restore a backup to a disposable copy | bc-infra `ops/backup do restore-proof` |
| Take the fixed copy for the reference run | barecount-devhub `scripts/reference-run/run.js --take-copy`; `ops/reference-host` guards the folder |
| Run the reference run | barecount-devhub `scripts/reference-run/run.js --run`; `ops/reference-runtime` guards the runtime |
| Deploy a cloud unit | bc-infra's two deploy definitions; outside the program |

**How condition P3-C5 reads the four acts that have no such command (ruling G38; the operator's grant `2026-11-19T00-38-29-443Z-2788b232`, text SHA-256 `2788b232b7c4939be9bd419ab428be35ce57683765d64dd86cdb9a2d21513b6c`).** Condition P3-C5 of phase 3 says that the acts of Operations "are performed by commands that have been run once". The operator ruled on 2026-11-19 that, for the judgement of that condition: starting, stopping or restarting a service counts as performed by the host script `servers.sh`, which is in the custody of `ops/host-files` and has been run; proving a migration on a restored copy counts as performed by the proof scripts and the window script of bc-db, as practised at the apply of migrations 0070 and 0071; applying a migration counts as performed by the governed runner of bc-db inside a window script, as practised at that apply; and deploying a cloud unit is outside the order of work and is not counted. A command of Operations with the four verbs for each of the first three acts, and the convergence to one backup tool, stay carried by name in the Definition and are done no later than the Lock step of Operations. Nothing else in P3-C5 changes, and the ruling authorises no act. The cost the operator accepted: Operations enters phase 4 with three acts on live services and the live database still performed by a script and by bc-db's runner, without the status, check, do, verify form and without Operations' own record of each run, until its Lock step. The ruling changes nothing in how any act of this chapter is performed or in whose grant it needs.

**Two folders of bc-infra `ops/` that perform no act of the table.** Both were added on 2026-11-19 by bc-infra pull request 89. `ops/launch-agents` has two verbs, `status` and `check`, and no `do`: it only looks at three launch agents. `ops/dev-secrets` is not a command: it holds three scripts that write a development credential or secret, which only the operator runs, each run under his grant for that act. Each has a section under "Commands of Operations that are not rows of the table". Neither gives any session a new act.

## The hard line

The hard line is the set of acts that are never performed without the operator's recorded approval: a change applied to a database; an act on data that cannot be undone; a change to cloud resources; the writing of a credential (Program, "Words this document uses").

For Operations this means that no session performs any of the following without the operator's recorded desk grant for that act:

| Never without a recorded grant | Command and verb |
|---|---|
| Serve a build of the engine, or return it to the previous build | `ops/serve-move do --live` |
| Restart the engine | `~/bc-stack/servers.sh restart bc-core`; see "Start, stop or restart a service" |
| Apply a migration to any database | bc-db's governed runner, in a live window |
| Take a new fixed copy for the reference run | `run.js --take-copy do`; see "Take the fixed copy for the reference run" |
| Deploy a cloud unit, or make any cloud change other than the upload the backup has always made to its one prefix | bc-infra's two deploy definitions |
| Install, put back or retire a host file | `ops/host-files do`, `put-back`, `retire` |
| Install the login-shell hook | `ops/secrets-identity do` |
| Set up the reference folder | `ops/reference-host do` |
| Install or remove the runtime guard | `ops/reference-runtime do`, `undo` |
| Change a launch agent: write its file, load it, unload it or restart it | no command of Operations does this. `ops/launch-agents` only looks and has no `do`; the hand lines its README gives are the operator's |
| Write or change a secret, a credential, or the identity that reads them | no command of Operations does this. The three scripts held in `ops/dev-secrets` are run by the operator only, never by a session |
| Any write to a live database | no command of Operations does this outside a migration apply |

The list is taken from the operator's ruling on the table of acts, given above, and from the READMEs of the commands named.

**Three acts need no new grant after their first real run, and each run is reported:** a backup taken by the command, a restore proof of a dump in a disposable container, and a reference run. The ruling is quoted under "The acts of Operations".

**Who may make such a run.** The ruling names the Chief. Ruling G37 names one more: a backup take and a restore proof in a disposable container made by the Prove worker "are within point three of grant `2026-11-18T14-11-21-285Z-ca66e1ef`", and the Chief reports each (Program, "The rulings", G37; Definition, "The steps of Operations in phase 3"). No text names any other session. The commands themselves read no grant, so this rule is kept by the people and sessions that run them, not by the code.

**The read-only verbs need no grant.** `status`, `check` and `verify` of every command of bc-infra `ops/` change nothing. One exception in cost, not in kind: `ops/serve-move check` makes one read of the cloud secret store (key names only), so it is run only when a move is being prepared.

### How a grant is read

A request is never authority. Only the recorded grant is.

1. Read the list: `GET http://127.0.0.1:3040/api/grants-list`. The answer has the form `{grants:[{grant_id, text, text_sha256, method}, ...]}` (bc-infra `ops/README.md`, "Authority").
2. Find the grant by its `grant_id`.
3. Work out the SHA-256 of the grant's `text` yourself and compare it with the `text_sha256` the desk gives. If they differ, stop.
4. Cite the grant by its `grant_id` and its `text_sha256` in whatever you write about the act.

The commands that act under a grant do the same reading themselves. `ops/serve-move` reads the desk at that one address, works out the hash again, requires `method` to be `totp`, and requires the grant's first non-empty line to be the exact line the command builds for that act. A grant is single use (bc-infra `ops/README.md`, "Authority").

A worker does not post a request to the desk and does not hold a grant. The Chief posts the request. The operator approves it.

The read is a plain request to an address on the development machine itself. On 2026-11-18 at 17:19 UTC the list was read, and for each of the eighteen grants this chapter cites by id the hash was worked out again and found equal to the desk's, with `method` `totp`. If the desk does not answer, stop and report. Never act on a grant you could not read.

## Before any act

- **Where the commands are.** `~/MyProjects/bc-infra`, the shared copy, which is a mirror of the main branch. Run every command of bc-infra from that folder, the repository root. Do not edit it. The two commands kept elsewhere, `run.js` and `servers.sh`, say in their sections where they are run from.
- **The shell.** A login shell. From a session: `zsh -l -c 'cd ~/MyProjects/bc-infra && node ops/<command>/cli.mjs <verb> ...'`.
- **Check the copy first.** Fetch (`git -C ~/MyProjects/bc-infra fetch origin`), then `git -C ~/MyProjects/bc-infra rev-parse HEAD origin/main` must print the same commit twice. The main branch moves within a day: on 2026-11-18 it was at `1e7b87d9` at 16:10 UTC (the custody record of that minute) and at `18cd69e0` at 16:54 UTC and still at 17:12 UTC; on 2026-11-19 it was at `f5cfc291` at 00:47 UTC and at `7e16520d` at 02:18 UTC, three merges later. If the two commits differ from each other, or from the commit this chapter names, the results below may not be the results you get; report the commits.
- **The copy is not clean today, and that is known.** `git -C ~/MyProjects/bc-infra status --porcelain` prints one line, `?? _wt/`. The folder holds the worktrees of the builders' branches (`git worktree list` named twenty-eight beside the checkout itself on 2026-11-19 at 02:18 UTC; the number moves as branches are opened and closed). By the standing rule a worktree is removed when its pull request is merged or closed, after it is confirmed that nothing in it would be lost (the annex "How the Work Is Done", the standing rules, rule 2). That is not an act of this chapter. Its one effect here: `ops/host-files status` says in its preview that a retire would refuse at this checkout because the checkout is not clean. The retire of 17:10 UTC was run from a clean checkout of the main branch, not from the shared copy (DevHub's program record, row PRG-fec959).
- **The result words.** The commands print one line for each thing they looked at. `OK` means it is as specified. `WRONG` means it is not. `COULDNOT` means the command could not look. `NOTE` and `INFO` are information and do not change the exit code. Some commands add words of their own, given in their sections.
- **The exit code is part of the result.** Always print it: `; echo "exit $?"`.

### What to do on WRONG or COULDNOT

One rule holds for every command of this chapter. It separates a line this chapter lists from every other line.

**A listed line: report it and continue.** A `WRONG` or `COULDNOT` line is listed when all of the following hold.

- The section of that command names the line as known today.
- The line is unchanged in its rule and in its place. The place is the file the section gives. Where the section also gives a line number, the line number is part of the place, with one exception that its section states: in the script scan, a listed file under the same rule id, with no more findings than its list gives, whose line number has changed is reported with the old and the new number and does not halt the sequence.
- The number of such lines is not above the counts the section gives. A count alone never makes a line listed: the line must also be one the section names, by file and by rule.
- The exit code is the one the section gives as today's for that verb.

Report a listed line as listed, with the command line and the exit code, and go on to the next act. Today two commands print listed lines and exit 1: `ops/secrets-route check` and `ops/script-scan check`. A result with fewer listed lines than the section gives, or a cleaner exit code because listed lines have gone, is reported as a shrinking and is not a reason to stop. A line that has gone never makes room for a new one.

**Any other line: the sequence halts.** Each of these halts it:

- a `WRONG` or `COULDNOT` line that the section does not list, and, in the script scan, a `FOUND` or `WRONG` line for a file that is not on its triaged list, whatever the counts are;
- a count above the counts the section gives;
- a line whose exception the section gives as closed, printed again;
- an exit code that this chapter does not give for that command and verb, or a `do` that ends other than as its section says a good run ends.

On a halt, nothing further is run: not the next act, and not the same verb a second time. The Chief is told at once, with the line as printed, the command line and the exit code. The Chief decides whether the sequence is taken up again.

**In both cases:**

1. Never repair by hand. Do not edit a host file, a settings file, `~/bc-stack/process-compose.yaml`, a lock or a record folder. Do not restart a service to "see if it clears". A session prepares and reads. The operator decides and repairs (bc-infra `ops/README.md`, the runbook, "Rules of the window").
2. Never run a `do` verb to cure a `check`.
3. A `NOTE`, `INFO`, `HELD`, `NOTJUDGED`, `UNKNOWN`, `EXCEPTION` or `ACCEPTED` line does not halt the sequence. Where a section gives a count for such lines, a different count is reported.

---

## What is special to a Prove run

The Prove step of Operations is run in phase 3 under ruling G37. Everything else in this chapter holds for any operator of the commands. This section alone is for the Prove worker.

**When the run may start.** Only once the Chief has judged condition P3-C5 and the Modify step of Operations and reported both to the operator (the operator's grant `2026-11-19T00-23-25-024Z-cfaca707`, request 515), and only with a chapter whose exact bytes the operator has approved.

**Who the worker is.** A worker that took no part in the work, started without memory files and given only this chapter and the commands. It may be started outside the `barecount-devhub` folder for this purpose only (ruling G37).

**The rule.** The worker performs for real every act that needs no grant of the operator. It performs every act that needs the operator's grant only through its `status`, `check` and `verify` verbs. It makes no reference run, and no serve move, install, migration, credential or cloud act. It never runs a script of `ops/dev-secrets`, and it never writes, loads, unloads or restarts a launch agent. The ruling authorises no run against a live database, no install, no serve move, no credential write and no cloud change.

| Act | What the Prove worker does |
|---|---|
| Start, stop or restart a service | Reads state only: `~/bc-stack/servers.sh ps` and `~/bc-stack/servers.sh info <name>`. It starts, stops and restarts nothing; see "Whose grant" in that act's section. |
| Serve a build; return to the previous build | `ops/serve-move status` and `verify`. |
| Show what a service was given | `ops/secrets-route status` and `check`; `ops/secrets-identity status`, `check` and `verify`. This act needs no grant and both of its verbs are performed. |
| Prove a migration on a restored copy | The act has no instance today, because no migration awaits apply. The worker performs what exists of it: it reads the register and reports that it holds no line, and it runs `ops/schema-compare status`, `check` and `do` without `--record`; that `do` is read-only. If the register holds a line, the worker stops and tells the Chief. See the Chief's statement below. |
| Apply a migration | Not performed. |
| Take a backup | `ops/backup do take`, for real, once. The Chief reports it to the operator. |
| Restore a backup to a disposable copy | `ops/backup do restore-proof <file>`, for real, once, on the dump just taken. The Chief reports it. |
| Take the fixed copy | `run.js --take-copy status` and `verify`, and `ops/reference-host status`, `check` and `verify`. Never `do`. |
| Run the reference run | Not made, and its preflight is not run; see the Chief's statement below. `ops/reference-runtime status`, `check` and `verify` are run. |
| Deploy a cloud unit | Not performed. |
| Commands that are not rows of the table | `status` of `ops/script-scan`, and its `check` in both forms: the default run, and the complete walk with `--exclude odoo-move` (see "The script scan"). `status` and `check` of `ops/environments`; `status`, `check` and `verify` of `ops/host-files`; `status` and `check` of `ops/launch-agents`, which has no other verb. Never `do`, `put-back`, `retire` or `undo`. |
| The secret writers held in `ops/dev-secrets` | Not run, in any form. They are not commands and have no read-only verb. The worker does not start one, with or without an argument. |

The worker reports each result to the Chief as printed, with the command line and the exit code, and says for each non-clean line whether this chapter lists it. A listed line does not stop the run: the worker reports it and performs the remaining acts. Any other non-clean result halts the run, by the one rule under "What to do on WRONG or COULDNOT".

**The Chief's statement on two points of the Prove run.** Ruling G37 says the worker performs for real every act that needs no grant of the operator. Two things are not run in the Prove run, and ruling G37 does not name either. What follows is the Chief's reasoning, stated as the Chief's. It is not a ruling of the operator.

1. **Proving a migration on a restored copy.** The act is performed on a migration that is merged and awaits apply. The register of migrations awaiting apply is bc-db `docs/migrations-awaiting-apply.md`. Read at bc-db's main branch, commit `ca1aabd18b1d93f6578c12e1aea66a1c7dbea523`, on 2026-11-18 at 17:13 UTC after a fetch, and again at the same commit on 2026-11-19 at 02:20 UTC, its table holds no line. So the act has no instance to perform. The worker performs what exists of it:
   - it reads the register (`git -C ~/MyProjects/bc-db fetch origin`, then `git -C ~/MyProjects/bc-db show origin/main:docs/migrations-awaiting-apply.md`) and reports the commit and that the table holds no line;
   - it runs the comparison, `ops/schema-compare do` without `--record`, which is read-only.

   If the register holds a line when the Prove run is made, the worker stops and tells the Chief, who decides with the operator. The worker does not run a proof script of bc-db or the `scratch` mode of a window script on its own judgement.
2. **The preflight of the reference run.** The preflight (`run.js --preflight`) is a form of the reference-run command. It is not a row of the table of acts. Ruling G37 says that no reference run is made in the Prove step. The preflight creates one network and two containers, and removes them. The Chief holds it to be part of the reference run's own procedure, and so outside the Prove run. The worker does not run it.

Both points are put to the operator when his approval of this chapter is asked, and his word governs. He decided both as they are written here, in grant `2026-11-19T00-23-25-024Z-cfaca707`, which was given for the chapter as merged at `98cd7d3c`.

---

## Start, stop or restart a service

**What it is.** Starting, stopping or restarting one of the services the supervisor runs: the database containers, DevHub, the engine, the operator console and the customer portal (Definition, section 2). Their ports are those of DEC-e50b83.

**The command.** There is no command of Operations with the four verbs for this act. The act is performed with the host script `~/bc-stack/servers.sh`, which is one of the twenty host files in the custody of `ops/host-files`. Its committed bytes are bc-infra `ops/host-files/files/servers.sh`, and `ops/host-files check` today reads the host copy as equal to them. From any folder, in a login shell: `zsh -l -c '~/bc-stack/servers.sh ps; echo "exit $?"'`. bc-infra `ops/README.md` says of the custody command: "no act of section 10 is a four-verb command because of them".

The script speaks to the supervisor through the socket `~/bc-stack/pc.sock`. Its verbs, from its own text:

| Verb | What it does | Changes |
|---|---|---|
| `servers.sh ps` | lists the services and their state | nothing |
| `servers.sh info <name>` | state, pid, start time and restart count of one service, as JSON | nothing |
| `servers.sh logs <name>` | the last 200 log lines of one service | nothing |
| `servers.sh ui` | opens the supervisor's own screen, from which a service can be started, stopped or restarted | what is done in it |
| `servers.sh start <name>` | starts one service | that service |
| `servers.sh stop <name>` | stops one service | that service |
| `servers.sh restart <name>` | restarts one service | that service |
| `servers.sh up` | starts the supervisor with every service of `~/bc-stack/process-compose.yaml` | every service |
| `servers.sh down` | stops every service the supervisor runs; the database containers keep running | every service |

The names are those of `~/bc-stack/process-compose.yaml`: `docker-stack`, `devhub`, `bc-core`, `bc-admin` and `bc-portal`. Always give a verb: with none, the script opens the supervisor's screen, as `ui` does.

**Exit codes.** The script documents two of its own. An unknown verb prints the usage lines and exits 2. `down` refuses with exit 3 while the launch agent `com.barecount.process-compose` keeps the supervisor running, and prints what the operator must run first. For every other verb the exit code is the supervisor program's own, and the script states no meaning for it.

**Whose grant.** The table says: "covered by the standing grant, for services other than the engine". A restart of the engine keeps the operator's grant, each time (Definition, section 10).

The Definition does not give the standing grant's id. The Chief states it, on 2026-11-18: it is the operator's standing grant for the program, `2026-11-14T02-58-16-873Z-e925518f` (desk request 443; text SHA-256 `e925518f9a0f8362d5cb9a5f5948f2577eb28e0d3646ba86082c863e4da2d3b8`, read at the desk on 2026-11-18), item 3. That statement of the Chief is not written in bc-docs or in bc-infra. What the texts themselves say:

- Item 3 of the grant: "Shared and served copies. The Chief may bring every shared copy level with its main branch, and may bring the three copies a service runs from level through that service's serving procedure and restart that service on the development machine, telling me beforehand in its report."
- The three are named in the annex "How the Work Is Done", "Keeping the repositories clean": "Three services run from a shared copy: DevHub, the operator console (bc-admin) and the customer portal (bc-portal)". The same annex says that the engine runs from a tree of its own.
- The grant names the Chief and no other session. It speaks of a restart made when a copy is brought level; the words "start" and "stop" are not in it.

So the act is the Chief's, for those three services, and the Chief tells the operator beforehand. **A worker other than the Chief does not start, stop or restart any service.** It reads state only: `servers.sh ps` and `servers.sh info <name>`. `servers.sh up`, `down` and `ui` are not a worker's either.

**Rules.** No session restarts the engine without the operator's grant. No session starts, stops or restarts any service, or runs `servers.sh` at all, while a serve move is in its window (bc-infra `ops/README.md`, the runbook, "Quiet"). A restart of the engine ends every evaluation and every panel run in flight.

**A restart of the supervisor itself is not this script's act.** It stops and starts every service at once. Until 2026-11-19 it was a mode of the host installer kept in barecount-devhub, which ran it twice on 2026-09-30. That installer left barecount-devhub by pull request 400 and was not moved to bc-infra. The one written route today is bc-infra `ops/README.md`, "The last resort: restart the supervisor", which is labelled there as derived and not run as written: its steps were read from the installer and have never been run as that text gives them. Ruling G38 counts this act as performed by `servers.sh`; by the README's own words, and the auditor's (the reply on exchange thread gen-fc4135, second message, point 2), that ruling does not validate the sequence and does not authorise its use. It is the operator's act, under a grant for that act. No session runs it. A command with the four verbs for this act, with the restart of the supervisor, is carried to the Lock step.

**The record.** The script writes none. What can be read afterwards is the start time and restart count that `servers.sh info <name>` prints. No text in bc-docs or bc-infra names a record of this act.

**A clean result today.** For the engine the reading of record is `ops/serve-move status`; see "Serve a build; return to the previous build". For the other services no text states a clean result, and `servers.sh` was not run for this chapter.

**On a failure.** No non-clean result of `servers.sh` is listed. If a verb of `servers.sh` exits with a code other than 0, or `ps` shows a service that is not running, the sequence halts: report the output and the exit code to the Chief. Do not start or restart the service.

**Older texts on this act are stale.** The host file `~/bc-stack/README.md` (lines 34 and 35) and `docs/development/dev-workstation-mac-mini.md` (section 3, "Start / stop BareCount on the Mac") both describe this script. Both say the operator console and the customer portal start switched off; `~/bc-stack/process-compose.yaml` had `disabled: false` for both when it was read on 2026-11-18. The host file also names, as "served now", a serve move of 2026-09-30 (line 52). Read the supervisor, not those texts. One line of `servers.sh` itself is known to be wrong and is not corrected: its guard on `down` says that after the launch agent is unloaded "servers.sh up brings it back". `servers.sh up` starts the supervisor; it does not load the agent (bc-infra `ops/launch-agents/README.md`).

---

## Serve a build; return to the previous build

**What it is.** A serve move changes the build a service runs. There is one procedure, in five steps: Check, Record before, Do, Verify, Return (ruling G14; Definition, section 3). The verification reads the running server, never the file. If any verification fails, the command restores the previous definition and reports "returned" only after it has observed the previous build serving.

**The command.** `ops/serve-move`, from the root of bc-infra:

    node ops/serve-move/cli.mjs status --service bc-core --port 3100 --socket /Users/anant/bc-stack/pc.sock
    node ops/serve-move/cli.mjs verify --service bc-core --port 3100 --socket /Users/anant/bc-stack/pc.sock \
        --commit <40 hex> --manifest <64 hex> --expected-role bc_platform_runtime
    node ops/serve-move/cli.mjs check  <the options of a move>
    node ops/serve-move/cli.mjs do --live <the options of a move>

`status`, `check` and `verify` only read. Only `do` changes anything. There is no `return` verb: a return to the previous build on demand is a second `do`, with its own grant.

**A session without a grant runs `status` and `verify` only.** The full procedure for a real move, with every option, is the runbook in bc-infra `ops/README.md`, "Runbook: one real move of the engine, and the return", parts A to G. It is not repeated here.

**What it reads.** `status` and `verify` read the supervisor through its socket, the listener on the port, the tree the listener runs from, and the engine's readiness answer. `check` also reads the desk, the auditor's clearance file in a local checkout of bc-external-audit, the key names of the two trees' settings files, and, once, the key names of the served secret in the cloud secret store.

**What `do` writes.** The supervisor's definition of the one service; the engine is stopped and started from the new tree; a lock file for the length of the run; one new evidence folder; and, only after the move is verified, the lines of `~/bc-stack/process-compose.yaml` that name the build.

**Exit codes** (bc-infra `ops/README.md`, "Exit codes"):

| Code | Meaning |
|---|---|
| 0 | moved and verified; or every check passed; for `status`, the supervisor's file agrees with what the supervisor holds |
| 10 | refused at check or at the command line; nothing was sent. For `status`: it printed `supervisor file: WRONG`. For `verify`: not verified |
| 11 | an error before anything was sent, or in a command that only reads; nothing changed |
| 12 | the move failed and the previous build was returned, and observed serving |
| 40 | halt: the return did not complete; nothing more is sent to the supervisor |
| 41 | an error in `do` that is not a result; the effect on the service is unknown; read the evidence folder |
| 42 | moved and verified, but the after-record could not be written |
| 43 | moved and verified, but the supervisor's file could not be brought into line with the new build |

**Whose grant.** The operator's, each time, for the engine, until ruling G1 is made (ruling G14). Each `do` needs: a recorded, unused desk grant whose first non-empty line is the authorise line the command builds for that exact move (`AUTHORIZE serve move | service=... | commit=... | manifest=... | from=...`); the auditor's clearance file for that commit and hash; every line of `check`; and the real supervisor's socket. A return needs a second grant and a second clearance.

**The auditor's clearance stays required.** Ruling G14 retires the separate clearance only if a grant says so in express words. bc-infra `ops/README.md` states that no recorded desk grant holds the line that retires it (the desk grant list, read 2026-11-18).

**A build that changes engine source cannot be moved by this command today.** The command works out whether engine source differs between the served commit and the new one. If it does, the move is refused. A passed reference run on the exact commit would lift that refusal, and none exists (bc-infra `ops/README.md`, "Whether engine source differs is computed, not asserted"; see "The reference run" below).

**The record.** One folder for each move under `~/bc-stack/serve-moves/`, named by the command with a UTC timestamp and eight hex digits. It holds twelve files and `SHA256SUMS`. To read one: `(cd <folder> && shasum -a 256 -c SHA256SUMS)` must print `OK` for every file; `result.json` gives the result; `move.json` gives the mode, the grant id and the auditor file read. The folder holds names of settings, never their values. Two folders exist from the first real move and its return, both of 2026-11-18: `20261118T021826Z-14c68601` and `20261118T021927Z-40d3a09c`.

**What has been done.** On 2026-11-18 the command moved `bc-core` from commit `ec72438baa2e84a9814f4e39f3f79324e5edf96a` to `fd4b55ca8090b6ba7b4fb9d992f83fe46fb78bbc` and returned it, each act under its own recorded grant (`2026-11-18T00-46-40-794Z-a974ceb4` and `2026-11-18T00-47-37-010Z-8c59b8e3`) and with the auditor's clearance. The evidence, and its boundary: the move and its return are shown by the two act records made at the time and by the operator's own read-only transcript of 13:21 UTC that day. The fixed read was not repeated after the return. No independent party observed the host afterwards; the operator accepted closure on that basis (grant `2026-11-18T13-30-43-000Z-618a0405`). A failed live move, and a live return after a failure, have not happened (Definition, section 3).

**A clean result today.**

- `status` exits 0. It prints `supervisor file: AGREES with what the supervisor holds`, then three lines: the running build, the supervisor's memory, and the supervisor's file. All three name the tree `/Users/anant/MyProjects/_wt/freeze-1055`, the commit `ec72438baa2e84a9814f4e39f3f79324e5edf96a` and the built-files hash `0d1e794db835d2d39b4212f6e83e763daca932fc967ff7ad5217dfd59d62d46b`. The running build line ends `ready true, database login bc_platform_runtime`.
- `verify`, given that commit, that hash and `--expected-role bc_platform_runtime`, exits 0, prints `outcome: verified` and eleven lines that start `pass`. The line on the fixed read says that no read was made before to compare with. That is the expected wording for `verify`; a move always makes the read.

No line of `status` or `verify` is known to be non-clean today.

**What to trust.** The line `running build` is the only truth about what serves: it is read from the running server. The supervisor's memory is what a restart of the service alone would serve. The supervisor's file is what a restart of the supervisor would serve (bc-infra `ops/README.md`, runbook, part F).

**On any other result.** No non-clean line of this command is listed. If `status` exits other than 0 or prints `WRONG`, or `verify` exits other than 0, the sequence halts: report the lines as printed. Every repair after a run that did not end with 0 is the operator's act, by the exact commands of part F of the runbook.

---

## Show what a service was given (names only): the secrets route check

**What it is.** A service is given its secrets by one route: the secret store, read by the one loader when the service starts, under one named identity (DEC-ecd55c). A settings file holds names and values that are not secret, and never a database address or a password (Definition, section 4). This command tells, by name only, how each service on the machine is given its settings and secrets, and fails on what section 4 forbids.

**The command.** `ops/secrets-route`, from the root of bc-infra:

    node ops/secrets-route/cli.mjs status
    node ops/secrets-route/cli.mjs check

There is no `do` and no `verify`. Both verbs only look.

**What it reads.** `~/bc-stack/process-compose.yaml`, the login profile file `~/.zprofile`, the settings files of the served tree and of the shared copy of the engine, the tool settings of the session program, the tracked files of each repository at its HEAD (through read-only git), the top level of `~/bc-stack`, and what each running child of the supervisor received (through `ps`). It makes no network call and no call to the cloud. It never prints a value: a finding is a rule id and a line number.

**What it writes.** Nothing.

**Exit codes.** 1 if any line is `WRONG`; otherwise 2 if any is `COULDNOT`; otherwise 0. A usage error is 2 (bc-infra `ops/secrets-route/README.md`, "What `check` reports and fails on").

**Result words of its own.** `UNKNOWN` (cannot be told from names), `HELD` (another function's file, named and counted, not counted as wrong) and `NOTJUDGED` (counted and not judged). Only `WRONG` and `COULDNOT` decide the exit code.

**Whose grant.** None.

**The record.** None is written. The result is the printed output.

**The result today is not clean, and the operator has ruled on it.** `status` exits 0. `check` exits 1. Read on 2026-11-19 at 02:18 UTC from bc-infra `7e16520d`, `check` ended `check: not as specified (6 wrong)` and printed 53 `OK`, 6 `WRONG`, 2 `COULDNOT`, 3 `UNKNOWN`, 16 `HELD` and 1 `NOTJUDGED`, and `NOTE` lines, which are information. Every `WRONG` and `COULDNOT` line was one of the eight of the table below, word for word. The count of `OK` lines was 54 at the earlier readings. The inventory of readers was changed between them and this one by bc-infra pull requests 89 and 90; which entry accounts for the one line was not worked out for this text, and a count of `OK` lines decides nothing. The earlier readings follow, as history. Read at 17:13 UTC on 2026-11-18 the check ended `check: not as specified (7 wrong)` and printed 54 `OK`, 7 `WRONG`, 2 `COULDNOT`, 3 `UNKNOWN`, 16 `HELD` and 1 `NOTJUDGED`, and `NOTE` lines, which are information. Six of the seven `WRONG` lines and both `COULDNOT` lines belong to the exceptions below. The seventh was raised by this chapter's own draft; see "The line this chapter's draft raised" below. With that line gone the check ends `check: not as specified (6 wrong)`, as the draft's reading of 16:54 to 16:57 UTC gave it, before the draft was merged. That is what the check printed at the read of 2026-11-19, 00:47 UTC, from bc-infra `f5cfc291`: exit 1, `check: not as specified (6 wrong)`, with 54 `OK`, 6 `WRONG`, 2 `COULDNOT`, 3 `UNKNOWN`, 16 `HELD` and 1 `NOTJUDGED`, and every `WRONG` and `COULDNOT` line one of the eight of the table below.

**The ruling.** The operator ruled that phase 3's condition "secrets are loaded one way" is met in this form: the check, run from the main branch, reads no line as wrong or unreadable other than four named exceptions (grant `2026-11-18T08-00-10-163Z-96f0254f`, text SHA-256 `96f0254f438606493edcb9c4990e08e4704d90aa770c942932b6526b5bb347af`, read at the desk on 2026-11-18; DevHub's program record, row PRG-2e0ba9, with the evidence row PRG-087bea). The exceptions stay as they are and may only shrink. The ruling authorises no write to a secret, a credential, a settings file, a host script or a database, and no serve move.

**One exception is closed; three remain.** When the ruling was made the check printed 7 `WRONG` and 2 `COULDNOT` (row PRG-087bea). Today 6 `WRONG` and 2 `COULDNOT` lines belong to the exceptions. Every one of those eight lines belongs to a remaining exception:

| Exception, in the ruling's order | State today | Lines today |
|---|---|---|
| One: two database addresses that carry a password stand in settings files and not in the secret store. The ruling: the audit exchange database address stands in the served tree and in the shared copy of the engine, and the demo database address in the shared copy; moving them is a design question for the function that owns each, not an act of phase 3. | open | 3 `WRONG`: `served-tree dotenv tree#1/.env line 26: rule url-with-password`; `shared-copy dotenv /Users/anant/MyProjects/bc-core/.env line 26: rule url-with-password`; the same file, `line 31`, the same rule. 2 `COULDNOT`: `names withheld: file is not simple`, one for each of those two files. |
| Two: the hand-run script `bc-core-signin.sh` keeps its default profile until the reviewed change is installed (the operator's grant `2026-11-17T00-47-48-357Z-7802d65f`). | **closed** | None. The line `WRONG  to-change bc-stack:bc-core-signin.sh` is gone. The check now prints `OK  requires bc-stack:bc-core-signin.sh: reads the variable, no default, no literal profile`. |
| Three: the record script `rotate-authoring-vendor-keys.sh` calls for a secret on the default chain. The ruling: it is a record and is not run. | open | 1 `WRONG`: `default-chain barecount-devhub:artifacts/chief/rotate-authoring-vendor-keys.sh`. |
| Four: the identity is still named in more than one place, in more than one form, until the engine is next served from a build at or after bc-core commit `b38de288` and exception two is cleared. No serve move is made for this alone. | open, and smaller | 2 `WRONG`: `the secrets identity is named in 3 places (section 4: one place, the supervisor's file)`, and `the profile values form 2 classes (they differ)`. |

**How exception two was closed.** On 2026-11-18 at 16:10 UTC `ops/host-files do` installed the reviewed `bc-core-signin.sh`, which has no default profile, from bc-infra `1e7b87d9`, under the operator's grant `2026-11-18T16-09-22-055Z-9533e033` (custody record `20261118T161007397Z-1e7b87d928da.json`; see "Host-file custody"). bc-infra pull request 86, merged as `18cd69e0`, then listed the installed script as `requires` in the inventory of readers.

**Why exception four is smaller and still open.** Before the install the count in its first line was 4; the sign-in script's default was the fourth place. The three places today are named by `NOTE` lines of the check: `~/bc-stack/process-compose.yaml` (class A), and two loader files of the served tree, `scripts/dev-secrets/dev-secrets-lib.mjs` and `scripts/with-demo-secrets.mjs` (class B). The second half of the ruling's condition is met, since exception two is cleared. The first half is not: the engine is served from commit `ec72438b` (`ops/serve-move status`, today), which holds those two loader files. The exception closes with a serve move, which is the operator's to grant.

**The lines that do not decide the exit code,** each under a ruling of its own or stated by the command:

| Line today | Count | Reason |
|---|---|---|
| `HELD` | 16 | Fifteen files of the repository bc-demo and one summary line. They belong to function PV, which is parked and held, by the operator's grant `2026-11-17T14-33-59-809Z-a3df3d6e`. A listed bc-demo file whose content changes, and any bc-demo file that is not listed, stays `WRONG`. |
| `NOTJUDGED` | 1 | The message documents of the exchange mirror (bc-external-audit), by the operator's grant `2026-11-16T14-29-25-560Z-ac1a63f3`. |
| `UNKNOWN` | 3 | Two files whose names are withheld (`~/bc-stack/process-compose.yaml` and `~/.zprofile`), and one tool whose database login cannot be told from names. |

**The line this chapter's draft raised.** At 17:13 UTC the check also printed `WRONG  unlisted reader bc-docs:docs/guide/operations.md line 452`. The check searches every tracked file of each repository for the names by which an identity is chosen. A file that holds one and is not in bc-infra's inventory of readers is reported as an unlisted reader (bc-infra `ops/secrets-route/README.md`). The draft merged by bc-docs pull request 241 named the identity's variable once, in the section "Take a backup". The line appeared when that draft reached the shared copy of bc-docs. The draft's own readings were taken before its merge and did not show it. The line is not one of the four exceptions, so while it is printed the check does not read in the form in which the operator ruled the condition met. This text no longer names the variable. When the shared copy of bc-docs holds this text, the line is expected to go and the count of `WRONG` lines to return to 6. At the read of 17:13 UTC that had not been observed. It was observed on 2026-11-19 at 00:47 UTC: the line was not printed and the count of `WRONG` lines was 6.

**How to tell a listed line from any other.** This applies the one rule of "What to do on WRONG or COULDNOT".

1. A `WRONG` or `COULDNOT` line that is one of the eight in the table above, word for word in its rule and its place, is a listed line. With only listed lines the exit code is 1. Report each as listed and continue with the next act.
2. A count below 6 `WRONG` or below 2 `COULDNOT`, with every line still one of the eight, is a shrinking exception. It is reported as such, and the worker continues.
3. Any other `WRONG` or `COULDNOT` line halts the sequence. So does a count above 6 `WRONG` or above 2 `COULDNOT`. So does an exit code other than 1 while a listed line is printed.
4. The line `to-change bc-stack:bc-core-signin.sh`, if it is printed again, halts the sequence: its exception is closed.
5. The line `unlisted reader bc-docs:docs/guide/operations.md`, at any line number, halts the sequence. It means that the shared copy of bc-docs is older than this text, or that the chapter names an identity again.
6. One further line is known and is not an exception: `COULDNOT  repository bc-infra: bc-infra content changed since the inventory was drawn`. The inventory of readers is pinned to bc-infra's content, so the line appears whenever bc-infra's content changes without the pin being drawn again. It is not printed at `18cd69e0`, nor was it at `f5cfc291` or at `7e16520d` at the reads of 2026-11-19, so it is not a listed line today. The auditor named one interval in which this check is not a clean result: between the merge of barecount-devhub pull request 400 and that of bc-infra pull request 90, when the inventory still named files that had left barecount-devhub (the replies on exchange threads gen-fc4135 and gen-3d04e4). Pull request 90 ended it. What the check printed in that interval was not read for this text. If it is printed, the sequence halts and the Chief is told by that name.

The last `NOTE` line of the output today reads `point of use: 4 children of 1 supervisor(s): equal 4, differs 0, absent 0, not readable or not comparable 0`. That part is clean: each running child received the identity the one place names.

---

## The secrets identity hook

**What it is.** `~/bc-stack/process-compose.yaml` names the identity in one place. This command installs and checks a fixed block in the login profile file `~/.zprofile` that reads that one entry, so that a login shell does not repeat it (bc-infra `ops/secrets-identity/README.md`). It is not a row of the table of acts; it serves the secrets route.

**The command.**

    node ops/secrets-identity/cli.mjs status
    node ops/secrets-identity/cli.mjs check
    node ops/secrets-identity/cli.mjs verify

`status` changes nothing and does not run the login shell. `check` and `verify` change nothing, but each runs the reader and the operator's own login shell once. `do` is the operator's: only the operator runs it, under a recorded desk grant. That grant is bound to the file's path and to the hash of the block; the README says it is not single use and does not expire.

**Exit codes.** 0 ok; 1 something wrong (`check`, `verify`); 2 refused, stopped or could not look, with nothing installed. For `do` only: 4 restored, 3 not restored.

**The record.** `do` writes no record folder. Before it changes the profile it keeps a copy of the whole old profile beside it, named `<profile>.bak-<UTC stamp>`, mode 600, and puts that copy back if its own check fails (bc-infra `ops/secrets-identity/README.md`, "do"). One such copy was seen on 2026-11-18, `~/.zprofile.bak-20261116T095412Z`. It may hold other secrets and is not to be opened or printed.

**A clean result today.** `check` exits 0 and ends `check: the hook is as specified`. `verify` exits 0 and ends `verify: the hook is in place and the reader answers`. One `NOTE` line says the login profile file's mode is 644. It is information and does not change the exit code. No line of the three verbs is known to be non-clean today, so none is listed: an exit of 1 or 2 halts the sequence and is reported, and the profile is not edited.

---

## The schema comparison, and proving a migration on a restored copy

**The schema-change path.** The path is the one practised, written once: claim, write, approve, review and merge, prove on a restored copy, apply in a window, record (DEC-4c1396). A migration is merged, then awaiting apply, then proven, then applied; or it is excepted; or it is withdrawn. The ledger in the live database is the only record of what was applied. Between its merge and its apply a migration has one line in a register kept in bc-db, `docs/migrations-awaiting-apply.md`. Every migration file on the main branch has a ledger row or a line in that register; a file with neither is a defect (Definition, section 5). bc-db's `README.md`, "The schema-change path as practised", gives the seven steps in full.

**Proving a migration on a restored copy** has no command of Operations today. As practised, each migration is merged with a proof script of its own, `tools/tests/platform-<number>-restore-proof.sh` in bc-db. The script takes a read-only dump of the live platform database, restores it into a disposable container of its own, applies the migration there through the real runner, and prints a line that starts `== RESULT: GREEN` when every check passed. The window script of an apply has a second mode, `scratch`, that runs the whole window against a restored copy and never against the live database, and a further script tests the served logins' permissions on the result (bc-db `docs/dbcp/apply-0070-0071/RUNBOOK-apply-0070-0071.md`, "Evidence in this packet"). The act changes no live state and needs no grant (Definition, section 10). It reads the live database and starts containers.

There is no one command line for this act: each migration has its own proof script and each window its own script. **Nothing awaits a proof today.** The register at bc-db `ca1aabd18b1d93f6578c12e1aea66a1c7dbea523`, read again on 2026-11-19 at 02:20 UTC after a fetch, holds no line; bc-db's main branch has not moved since the read of 2026-11-18.

**The comparison** is a command of Operations. It compares the platform migration files on bc-db's main branch with the live ledger and with the register.

    node ops/schema-compare/cli.mjs status --bc-db /Users/anant/MyProjects/bc-db
    node ops/schema-compare/cli.mjs check  --bc-db /Users/anant/MyProjects/bc-db
    node ops/schema-compare/cli.mjs do     --bc-db /Users/anant/MyProjects/bc-db [--out <file>] [--record]
    node ops/schema-compare/cli.mjs verify --bc-db /Users/anant/MyProjects/bc-db --out <file> | --from <file>

Here `do` is itself read-only: it changes no database, service, cloud resource or checkout.

**What it reads.** Git objects of the bc-db checkout at `origin/main` (never the working tree, and it never fetches: fetch the checkout yourself first and compare the commit it prints). The ledger, once, through the container `bc-postgres` with the read-only login `bc_capture_ro`, inside a read-only transaction. The register at the same commit.

**What it writes.** Its report to the output. With `--out`, that one file. With `--record` to `do`, a record of the attempt.

**Exit codes** (bc-infra `ops/schema-compare/README.md`, "Verbs"):

| Verb | Exit |
|---|---|
| `status` | 0 |
| `check` | 0 ok, 2 could not |
| `do` | 0 PASS; 1 FAIL (a verdict of FAIL, or a register that is malformed or missing at that commit); 2 could not look; 130 or 143 a signal |
| `verify` | reads a report a previous `do` wrote. A FAIL record that is still true is `current`, exit 0: read the verdict it prints, not the exit code |

**Whose grant.** None.

**The record.** With `--record`, one fixed folder, `~/bc-stack/state/schema-compare/`. An attempt that produced a verdict leaves `schema-compare-<sequence>-result-<UTC time>-<bc-db commit>.json` and the same name with `.txt`, which holds the report lines exactly as printed. An attempt with no verdict leaves `schema-compare-<sequence>-attempt-<UTC time>.json`.

**Reading a report.** Each finding is one line with a code. A line marked DEFECT makes the verdict FAIL: for example `FILE-NO-LEDGER-NO-REGISTER` (a file on main with no ledger row and no register line), `REGISTER-STALE`, `REGISTER-NO-FILE`, `HASH-DRIFT`. `AWAITING-APPLY` and `EXCEPTED` are information. The tenant migrations are not compared; the report says so with their count. The last line starts `SUMMARY` and ends with the verdict.

**A clean result today.** `status` exits 0 and prints three lines that say what it would read. `check` exits 0 and prints two lines: that bc-db is a git checkout with `origin/main` at `ca1aabd18b1d93f6578c12e1aea66a1c7dbea523`, and that the ledger is readable (74 rows, source live).

**The verdict of `do`.** `do` was not run for this chapter. The newest recorded run is sequence 2, of 2026-11-17 (the names in the record folder were read again on 2026-11-19; the file's text was read on 2026-11-18): its `.txt` ends `SUMMARY platform files 63, defects 0, info 14, bc-db commit c5bb3264175e7f9b929e4435230f283eb07417a6, ... verdict PASS`. bc-db's main branch has moved four commits since, to `ca1aabd1`; none of them changes a file under `migrations/` or the register. A run today without `--record` is read-only and may be made by any session.

**On FAIL.** A FAIL is a defect of the repository or of the register, not of the machine. No DEFECT line is listed today, so a verdict of FAIL, or an exit of `do` other than 0, halts the sequence. Report the DEFECT lines as printed. Do not add or remove a register line, and do not touch the ledger.

---

## Apply a migration

**What it is.** A forward migration of bc-db applied to a database through bc-db's governed runner, which writes the migration and its ledger row in one transaction (Definition, section 5; DEC-4c1396).

**Whose grant.** The operator's, each time. Every apply is a live act. The operator also approves the database change at the desk before the migration is merged.

**No session applies a migration without that grant, and a worker never does.**

**The command.** bc-db's runner, `tools/runner/runner.js apply`, started by a window script that is committed with the migration. No one runs the runner against the live database by hand. The newest window is the pattern (bc-db `docs/dbcp/apply-0070-0071/`, files `RUNBOOK-apply-0070-0071.md` and `window-0070-0071.sh`):

    export BCDB_MERGE=<the reviewed bc-db commit, 40 hex>
    export DISPOSITION_<number>=<the SHA-256 of that migration's approving review response>
    zsh docs/dbcp/apply-<numbers>/window-<numbers>.sh live

It is run in a login shell, from a clean checkout of bc-db of its own, never from a shared copy. As practised, the window script checks that it is on the right database server, takes and restores a backup, runs the proof again, applies the migration through the runner, and checks the result (Definition, section 5, "Today"). Each window script is written for its own migrations: its pins, its options and its checks are its own, and its runbook is the authority for it. Applies are not required to follow number order.

**Exit codes of that window script** (its runbook): 0 green; 3 refused; 10 not started, nothing changed in the step that failed; 20 applied, then a check failed, hold; 30 halt, the runner's outcome is not assumed. On 20 or 30 there is no retry and no automatic rollback: report the exit code and the window's transcript. A rollback is a separate act under the operator's grant; the runner never runs one.

**The record.** The ledger row, `infrastructure.schema_migration_event` in the live database, read by `ops/schema-compare`. The window writes its evidence to a folder under `~/bc-stack/evidence/`. The evidence of the apply is then committed in bc-db under `docs/dbcp/`, and the change that records it removes the migration's register line.

---

## Take a backup

**What it is.** A backup is a copy of every database of the live platform, identified by its hash. It is taken, then stored on the machine and off it, then proven when it has been restored to a disposable copy and its fingerprint compared (Definition, section 6). What is outside the backup: DevHub's database, the cache and the source system.

**The command.** `ops/backup`, from the root of bc-infra:

    node ops/backup/cli.mjs status
    node ops/backup/cli.mjs check
    node ops/backup/cli.mjs do take
    node ops/backup/cli.mjs verify [<record file name>]

**What `do take` reads and writes.** It reads the live database server through the container `bc-postgres` and takes one whole dump. It writes: the dump and its `.sha256` in `~/bc-stack/backups/pg`; the two `latest` links; one record; and, to the cloud, the dump and its `.sha256` under the one prefix `mac-mini-pg/` of the backup bucket. It prunes the dump folder to the newest seven dumps. It takes a lock that it shares with the nightly script, and refuses at once if a backup is running.

Two effects to know before taking one. It uploads two files. And because seven dumps are kept, each take pushes the oldest dump out of the local folder.

**What it needs.** The variable that names the secrets identity set, not empty and a plain name (a login shell provides it; `status` prints the variable's name as the setting `upload_identity_variable`); the two backup folders real, of this account and closed to others; the lock free; the live container answering. It takes no argument.

**Exit codes** (bc-infra `ops/backup/README.md`, "The verbs"):

| Verb | Exit |
|---|---|
| `status` | 0 |
| `check` | 0 clean, 1 any WRONG, 2 a COULDNOT and no WRONG |
| `do take` | 0 taken, 1 the act ran and its result is WRONG, 2 could not, 130, 143 or 129 a signal |
| `verify` | 0 still true, 1 no longer true, 2 could not |

**Whose grant.** None after the first real run, which was the operator's to grant (`2026-11-18T14-10-38-847Z-8fa8e994`). A further take is made by the Chief, or by the Prove worker under ruling G37, and each is reported to the operator. The command itself reads no grant: unlike `ops/serve-move` and `ops/host-files`, it takes no confirmation flag and knows no window, so whether a run is authorised is decided outside the code (bc-infra `ops/backup/README.md`, "The real path is switched on").

**The record.** One JSON file for each attempt, in the one folder `~/bc-stack/state/backup/`, named `take-<UTC stamp>-<8 hex>.json`. An attempt that stops before the lock leaves a record too, with the outcome `refused`. `status` names the newest record of each verb and its outcome. `verify` reads one record and the files it names. A take record holds the file name, size and SHA-256, the fingerprint and its SHA-256, the upload keys and their read-back, and the pruned names. It holds no secret.

**What has been done.** Two real takes on 2026-11-18, at 14:17 and 15:22 UTC, each exit 0, each uploaded and read back (bc-infra `ops/backup/README.md`, "The real runs of 2026-11-18"). Their records are `take-20261118T141827171Z-6e68eb41.json` and `take-20261118T152305157Z-533d5515.json`. The installed nightly script then made its first run on 2026-11-18 at 20:30 UTC; its record is `take-20261118T203105000Z-16839c02.json`, with the outcome taken (bc-infra pull request 87, merged as `f5cfc291`; `ops/backup status`, read 2026-11-19).

**A clean result today.**

Read on 2026-11-19 at 02:18 UTC, from bc-infra `7e16520d`, after the nightly script's first run and before its second:

- `status` exits 0. It lists the settings, seven dumps, `lock: free`, and `last take: take-20261118T203105000Z-16839c02.json, outcome taken, finished 2026-11-18T20:31:05Z`. The newest dump is `pg_dumpall-20261118T203005Z.sql.gz`; the oldest of the seven is `pg_dumpall-20261116T133228Z.sql.gz`. Every dump is mode 0600. `status` prints the age of each dump in hours as of the minute it is run: at that read, 5.8 h for the newest and 60.8 h for the oldest.
- `check` exits 0 and ends `check: clean`. Its fifteen `OK` lines: both folders real and closed to others; each of the seven dumps hashes to its `.sha256`; `age: the newest backup pg_dumpall-20261118T203005Z.sql.gz is <n> h old, within the bound of 20 h` (5.8 at that read); `record: take-20261118T203105000Z-16839c02.json names the newest backup`; the proof is within 7 days; `last-run: the newest take record take-20261118T203105000Z-16839c02.json ended as taken`; `lock: free`; `script: the installed pg-backup.sh equals its custody bytes`.
- `verify`, given no argument, reads the newest record of either verb. At that read it was the take record of the nightly run: it exits 0, names `take-20261118T203105000Z-16839c02.json` with the SHA-256 of the record, says the dump `pg_dumpall-20261118T203005Z.sql.gz` hashes to the recorded SHA-256, and ends `verify: still true`.

These names and ages hold only for that minute. The same results, with ages of 4.3 h and 59.2 h, were read at 00:47 UTC that day from bc-infra `f5cfc291`. The age grows with the clock, and every take changes the newest dump, the newest record and the oldest dump kept. The nightly script is due each day at 20:30 UTC (see below); after each run, expect a newer dump and a newer take record than the ones named here. The reading of 2026-11-18, 17:12 UTC, before that first nightly run, named `pg_dumpall-20261118T152216Z.sql.gz` as the newest dump, 1.8 h old, and `take-20261118T152305157Z-533d5515.json` as the last take. No line of `check` is known to be non-clean today. `status` prints four settings with the words "today's value, not yet the operator's decision": the age bound, how often a restore is proven, whether a dump keeps the roles' stored password forms, and the upload identity. These are information.

**The nightly backup is still taken by the host script,** `pg-backup.sh`, which the launch agent `com.barecount.pg-backup` runs. The agent's calendar entry is 02:00 in the machine's time zone, which is 20:30 UTC (`plutil -p` of the agent's file, 2026-11-18); three of the seven dumps carry the stamps `20261116T203005Z`, `20261117T203003Z` and `20261118T203005Z`. The script installed from custody on 2026-11-18 has run once, at 20:30 UTC that day: it wrote the record `take-20261118T203105000Z-16839c02.json` to the same folder as the command's records, with the outcome taken, and it takes the same lock. bc-db holds a further backup tool, `tools/backup/`. The Definition asks for one tool; there is not one yet (bc-infra `ops/backup/README.md`, "One tool"). By ruling G38 that convergence stays carried by name and is done no later than the Lock step of Operations.

**On WRONG.** No `WRONG` or `COULDNOT` line of this command is listed today, so any such line, or an exit of `do take` other than 0, halts the sequence. `check` printing `WRONG  last-run: ... the last backup run took no backup` means the newest attempt failed or was refused. Report the line with its two code words. Do not delete a `.part` file, a lock or a record.

---

## Restore a backup to a disposable copy

**What it is.** The proof that a backup restores: one dump is restored into a disposable container that the command creates and removes, and the restored databases and row counts are compared with the fingerprint of the file.

**The command.**

    node ops/backup/cli.mjs do restore-proof <pg_dumpall-<stamp>.sql.gz>

The file is named by its name only, a dump of the dump folder. A path, or any other name, is a usage error.

**What it reads and writes.** It reads the named dump and its `.sha256`, and the take record of that file if one exists. It starts one container from a pinned image with no network. It does not touch the live database server or the cloud. It writes one record and removes the container. It takes no lock.

**Exit codes.** 0 proven, 1 WRONG, 2 could not, 130, 143 or 129 a signal.

**Whose grant.** None after the first real run (grant `2026-11-18T14-10-38-847Z-8fa8e994`). As for `do take`: the Chief or the Prove worker makes a further proof, each is reported to the operator, and the command reads no grant.

**The record.** `~/bc-stack/state/backup/proof-<UTC stamp>-<8 hex>.json`. It holds the file, its SHA-256, the take record it was checked against, the fingerprint's SHA-256, the counts, the container's name and whether it was removed. When the restore failed, the record holds where the restore stopped (the error code, the line of the dump, the database and the kind of statement) and none of the restoring program's text. `node ops/backup/cli.mjs verify` reads the newest record of either verb.

**What a proof shows.** The file is complete; it restores without an error on the pinned engine; the restored copy holds every database the file names and every row the file holds, table by table; the restored copy is not the live one. **What it does not show:** that the rows are byte-equal to the live ones; that the copy in the cloud restores; that the roles' passwords work; that the engine can start on the restore (bc-infra `ops/backup/README.md`, "What a proof shows, and what it does not").

**What has been done.** Three real proofs on 2026-11-18. The first two ended WRONG; the second named a leftover test database that could not be restored. Two leftover test databases were then dropped from the live server under the operator's grant `2026-11-18T15-21-45-938Z-b5dcc2ce`, a second take was made, and the third proof ended PROVEN: 11 databases and 1177 tables hold the rows the file holds (bc-infra `ops/backup/README.md`, "The real runs of 2026-11-18").

**A clean result today.** Read on 2026-11-19 at 02:18 UTC, from bc-infra `7e16520d`: `status` prints `last proof: proof-20261118T152340837Z-ecf63aad.json, outcome proven, finished 2026-11-18T15:23:40.837Z`. `check` prints `OK  proof: proof-20261118T152340837Z-ecf63aad.json proved pg_dumpall-20261118T152216Z.sql.gz, <n> days ago, within 7 days`; the number is the age of the proof at the minute of the run (0.5 at that read; 0.1 on 2026-11-18 at 17:12 UTC). The nightly take of 20:30 UTC did not change that line: the dump it took has not been proven.

To read the proof record, name it: `node ops/backup/cli.mjs verify proof-20261118T152340837Z-ecf63aad.json`. Read at 02:19 UTC, it exits 0, names that record with the SHA-256 of the record, says that the proved dump `pg_dumpall-20261118T152216Z.sql.gz` still hashes to the recorded SHA-256 and that the take record `take-20261118T152305157Z-533d5515.json` is unchanged, and ends `verify: still true`. With no argument `verify` reads the newest record of either verb, which since the nightly run is a take record and not this proof. The proof stays the newest proof until another is made; a later take does not change it. The proved dump leaves the dump folder when seven newer dumps exist; what `verify` prints for its record after that was not observed.

**A proof that ends WRONG is a result, not a fault of the worker.** A dump is a faithful copy of the server; if the server holds a database that cannot be restored, the proof says so. It is not a listed line, so the sequence halts. Report the record's name and its reason. Do not drop a database, and do not repeat the proof on the same file to see whether it passes.

**If a container is left behind.** The container is named `bc-backup-proof-<16 hex>`. The command removes a container only when an inspection of that name shows this run's own label; anything else it refuses and leaves alone, with its name printed so that a person can look. It reports "removed" only when it has seen the name absent from the list of containers; otherwise it records that the removal is not known and fails the step (bc-infra `ops/backup/README.md`, "The disposable container"). No text says who removes a container that remains. A session reports the container's name and removes nothing.

---

## Take the fixed copy for the reference run, and the reference folder

**What it is.** The fixed input of the reference run: the platform database, the roles without their passwords, and the database of every tenant that the engine's start-up check requires. It is taken once, kept on the development machine only, outside every repository, readable only by its owner and by the auditor's account, and identified by hashes committed to the DevHub repository (ruling B1; Definition, section 9).

**Whose grant.** The operator's, once. Taking a new fixed copy keeps that grant (Definition, section 10). **No session takes a copy without it, and a worker never does.**

**The command** is kept in the DevHub repository (barecount-devhub `scripts/reference-run/README.md`, "The take-copy command"). From the root of `~/MyProjects/barecount-devhub`:

    node scripts/reference-run/run.js --take-copy status --destination /Users/Shared/bc-reference
    node scripts/reference-run/run.js --take-copy check  --source-container bc-postgres --source-user <user>
    node scripts/reference-run/run.js --take-copy do     --source-container bc-postgres --source-user <user> \
         --destination /Users/Shared/bc-reference --baseline-tenant <slug> --grant-line "<the exact line status prints>"
    node scripts/reference-run/run.js --take-copy verify --destination /Users/Shared/bc-reference [--expect-manifest-sha256 <64 hex>]

`status` and `verify` only read. `check` reads the live database server: it names every session it sees and never a value. `do` is the taking. It takes the real copy only from the container `bc-postgres` into `/Users/Shared/bc-reference`; any other source or destination is refused. It needs a recorded desk grant whose text holds the exact line `status` prints. The operator stops the services first, the engine first; the command never stops or starts a service. Only the Chief runs `do`, inside the window the grant names. The procedure is that README's "The runbook of a real taking", parts A to F.

**Exit codes of `do`** (that README): 0 a complete, verifying copy is kept; 3 the taking failed its own proofs and everything it wrote was discarded, the destination observed empty; 4 the placed files were removed and the destination is not observed empty; 5 the placed folder was set aside whole, in quarantine, with its reasons; 6 a state the command cannot classify. The section of the README states no exit code for `status` and `verify`.

**A clean result today.** None is recorded here: no form of `run.js` was run for this chapter. A session that runs `--take-copy status` or `--take-copy verify` reports what is printed and the exit code. `verify` without `--expect-manifest-sha256` checks only that the copy agrees with its own manifest, and says so; with the hash given under "What has been done" it checks the copy against the manifest the Definition names.

**What has been done.** DevHub's program record says that the third real taking, on 2026-11-18 from 06:46 to 06:55 UTC, was kept, under the operator's grant `2026-11-18T06-41-47-654Z-80ec84bd`, and that two services were down for about eight minutes (row PRG-4a6fb6). The manifest of the kept copy has the SHA-256 `9f21a74c5b15a4e1b5cbda0e07d47859ff74f1f050d00ceb0f42ec3af03a0376` (Definition, section 9). The README of the command still says in its own section that no real copy has been taken; that sentence is older than the taking.

**The folder is guarded by a command of Operations.** `ops/reference-host` sets up and checks the folder `/Users/Shared/bc-reference`, whose group holds exactly the owner and the auditor's account.

    node ops/reference-host/cli.mjs status
    node ops/reference-host/cli.mjs check
    node ops/reference-host/cli.mjs verify

`status`, `check` and `verify` change nothing. `do` changes the host and only the operator can run it (root through sudo, under a recorded desk grant whose line begins `AUTHORIZE reference host setup`). No verb removes anything.

**Exit codes.** `status` 0. `check`: its lines are `OK`, `MISSING` or `WRONG`; 0 all as specified, 1 missing or wrong, 2 could not look. `verify`: 0, 1 or 2. `do`: 0 done, 2 refused or stopped (bc-infra `ops/reference-host/README.md`, "Verbs").

**The record.** The README of `ops/reference-host` names no record that `do` writes. `do` prints each step before it runs and reads it back after; on a failure it stops and prints what was done so far. Its printed output is its only record.

**A clean result today.** `check` exits 0 and ends `check: as specified (group bcreference: anant, bcauditor; bcauditor reads /Users/Shared/bc-reference)`. It prints eight lines that start `ACCEPTED`, one for the folder and one for each of seven files: each carries the one permitted extended attribute. Those lines are expected. `verify` exits 0, says the current account can list the folder (7 entries), and prints a command for the operator to run from the auditor's account. The auditor's own listing is the proof of record; this command cannot produce it. No `MISSING`, `WRONG` or could-not-look result of this command is listed today: an exit of 1 or 2 halts the sequence.

---

## The reference run

**What it is.** One command that evaluates a fixed set of metrics through the real engine on a fixed copy of the databases, and fails on any difference from recorded values (Program, "The method"). Its fixed input, its set in two tiers, its ten steps and its limits are the Definition, section 9. It is kept in the DevHub repository, so that a change to the engine cannot change the thing that checks it. Operations owns it. It runs on the development machine.

**Its states.** For a commit of the engine the reference run is not run, passed, failed or unresolved. A pass belongs to one commit and one copy. An unresolved run is not a pass.

**What a pass shows, and what it does not.** A pass shows that values have not moved, and, on the source tier, that the engine reproduces its declared definition from the source's rows for three metrics. No tier shows that a value is right (Definition, section 9, "Its limits").

### The command

From the root of `~/MyProjects/barecount-devhub`, in a login shell (barecount-devhub `scripts/reference-run/README.md`; every path is absolute):

    node scripts/reference-run/run.js --plan --commit <40 hex> --copy <dir>
    node scripts/reference-run/run.js --run --dry <the options of a run>
    node scripts/reference-run/run.js --preflight > report.json
    node scripts/reference-run/run.js --run --candidate-repo <abs> --candidate-commit <40 hex> --set <abs> --copy <abs> \
         --bc-db-repo <abs> --bc-db-commit <40 hex> --tools-manifest <abs> --review-disposition-sha256 sha256:<64 hex>
    node scripts/reference-run/run.js --sweep <run id>

| Form | What it does | Creates |
|---|---|---|
| `--plan` | prints the plan | nothing |
| `--run --dry` | makes every check a run makes before it creates anything, prints the checks and the steps it would run; exits 0 or 2 | nothing: no container, no file, no folder |
| `--preflight` | proves that the container network a run uses has no way off itself; prints one JSON report | one network and two containers, which it removes; no file |
| `--run` | one reference run, the ten steps of the Definition | the disposable containers, which it removes whatever the verdict; one records folder, which stays |
| `--sweep <run id>` | clears what a dead run left | removes that run's containers, network and volumes |

No option of `--run` names a committed input: the expected set, the manifest of the copy and the other committed inputs are read from the command's own commit, which must be on the DevHub repository's main branch with the command's folder clean.

**Exit codes of `--run`.** 0 passed; 1 failed, or no record; 2 refused before anything was created; 3 unresolved; 64 wrong arguments; 130 or 143 on a signal. The summary line names the verdict. "FAILED" is printed only for a failed run, and an unresolved run is printed with the words "NOT a pass". The preflight exits 0 passed, 1 failed, 2 refused before anything was created.

**Whose grant.** None after the first real run, which was the operator's to grant; each further run is the Chief's and is reported to the operator (the ruling on the table of acts). A run for the Chief's own information attests nothing: the attested runs that the hold on the engine will come to require are performed under the auditor's account (Definition, section 9, "How the hold comes to require it").

**The record.** One folder for each run, `<the running account's home>/.bc-reference-run-disposable/records/<run id>/`, mode 700. It holds `record-<its SHA-256>.json`, `report-<its SHA-256>.json`, the candidate's and the issuer's logs with secrets removed, and the census of the runtime tree. To read one: the SHA-256 of each of the two JSON files equals the hash in its name (`shasum -a 256 <file>`); the record gives the verdict, each compared line with its tier, the five cases and the check of the binding freeze. The folder of the first run was seen on 2026-11-18: `~/.bc-reference-run-disposable/records/rn-20261118t103559z-fa4cd1/`, with the record and the report whose hashes the Definition gives. It is outside every repository.

### Where it stands today

**The first reference run was made on 2026-11-18 and failed, and no recorded value was shown to have moved** (Program, "The method").

- The run: `rn-20261118t103559z-fa4cd1`, under the operator's grant `2026-11-18T09-34-48-980Z-b0a93f42`.
- The command: barecount-devhub commit `1d30655c038e1d264eafeeab5d05a9581f246a16`.
- The engine: bc-core commit `fd4b55ca8090b6ba7b4fb9d992f83fe46fb78bbc`. bc-db: commit `ca1aabd18b1d93f6578c12e1aea66a1c7dbea523`.
- The fixed copy: manifest SHA-256 `9f21a74c5b15a4e1b5cbda0e07d47859ff74f1f050d00ceb0f42ec3af03a0376`.
- The run's record: SHA-256 `fb9c11fe3205988877f9a0a07653f872ed2b1578bc4d2369d79cb8ab79a02bf5`. It is kept on the development machine, outside every repository.
- The verdict: **failed**. Of 86 compared lines (74 of the baseline tier, 12 of the source tier), 3 agreed and 83 held no result. The engine produced no value for 15 of the 17 metrics. The input case and the check of the binding freeze were not run. No held value was shown to have moved, and none was shown to be right.

**The two causes** (Definition, section 9):

1. **No canonical contract projects a local currency code.** The engine refuses, before it reads any row, a metric whose currency policy is `local_currency` when the canonical contract of the metric's grain declares no field named `local_currency_code`. Thirteen of Kaveri's metrics declare that policy. A fourteenth returned no value because it is built on one of them. The refusal does not depend on the copy or on the data.
2. **The Kaveri tenant has no legal-entity key declaration for its journal-line source.** In the run, the canonical resolution of `cc-x13pb` version 3.0.0 wrote no canonical object. That this is the path the rows took is inferred, as the Definition states.

**Ruling B2** (the operator's grant `2026-11-18T10-48-54-157Z-faed2708`, text SHA-256 `faed2708be1d64ba3c5578fbf10a3db3ffa0d0bc420e6d41847c4fc2281ad7e3`):

- The baseline is the values held, every row of the 74. No row is left out of the reference set, no held value is replaced by a value of the first run, and the contract state that produced the held values is not restored in the copy.
- The two defects are repaired by the functions that own them, at their Modify steps, by the governed procedures and under their own grants. Neither is repaired in Operations, by changing the engine's rule, by changing a metric's currency policy, or by a change to the reference run or its inputs that would let these metrics pass or be skipped.
- The conditions that the reference run has passed once (**P3-C6**) and that the check on the engine requires it from then on (**P3-C7**) stay open by name until those repairs are made and one reference run has passed.
- Until P3-C7 is met, the check `engine-hold` stays as it is: the operator's recorded exception for each change to a held file.
- The grant authorises no reference run, no taking of a copy, no write to any database, and no change to a contract, a metric, a binding or the engine.

**What the merged texts say about a further run.**

- Ruling B2 authorises no run. The ruling on the table of acts lets the Chief make a further run without a new grant and report it to the operator.
- Ruling G37 says that in the Prove step of Operations no reference run is made.
- No merged text forbids the Chief a further run, and none says that one is planned before the repairs. A run on the same engine commit meets the first cause again, because that refusal does not depend on the copy or on the data.

**What this means for any session.**

- **Nothing of the reference run is changed:** not its command, not its inputs, not its expected set.
- Until P3-C7 is met, no reference run stands behind a change to the engine, and the Modify step of a function cannot show that values did not move (Program, "The method"; ruling B2).
- A worker makes a reference run only when the Chief has told it to. The Prove worker makes none, and it does not run the preflight either, for the reason the Chief states under "What is special to a Prove run".

### The runtime guard

**What it is.** One guard inside the container machine that a reference run uses: four packet rules that reject TCP port 22 from the container bridges, and a unit inside the machine that restores them at every start. The auditor ruled that no candidate may run on a runtime until that exposure is removed and a fresh preflight passes (bc-infra `ops/README.md`, "reference-runtime").

**The command.**

    node ops/reference-runtime/cli.mjs status
    node ops/reference-runtime/cli.mjs check
    node ops/reference-runtime/cli.mjs verify

`status`, `check` and `verify` only look. `do` and `undo` change that one machine. They are run by the account that owns the profile, under a recorded desk grant whose first line is the line `status` prints. **A worker runs neither.**

**Exit codes** (bc-infra `ops/reference-runtime/README.md`):

| Code | Meaning |
|---|---|
| 0 | done and read back, or every check passed |
| 10 | refused; nothing was sent that changes anything |
| 11 | could not look, or an unexpected error; nothing changed |
| 12 | `check` or `verify`: something is missing or wrong |
| 13 | a change command failed, or the read-back after it failed; the machine may be partly changed; nothing was undone |

**The record.** One folder for each act under `~/bc-stack/reference-runtime/`. One exists today, `20261115T093625Z-d7246513`.

**A clean result today.** `check` exits 0, prints twelve `OK` lines (each of the four rules present exactly once; the guard rules first in each family; the two files equal to the fixed text with the fixed owner and mode; the unit enabled and active), one `INFO` line that lists the listeners on port 22, and ends `check: as specified`. `verify` exits 0 and ends with a reminder to run the reference run's preflight. The `INFO` line is expected: the guard does not stop the listener, it rejects the bridges.

The guard does not survive a deletion of the container machine, only a stop and a start. `check` shows only that the rules and the unit are in place. The preflight is the proof. No line of the three verbs is known to be non-clean today, so none is listed. An exit of 12 means the guard is missing or wrong; it halts the sequence and is reported, since `do` is not a worker's. So does an exit of 10 or 11.

---

## Deploy a cloud unit

**What it is.** A deployment of one of the units bc-infra defines. Three are deployed: sign-in, secrets, and the machines that run the checks. Three are not: the network, a managed database, and the unit that would apply the schema to it. Those three are designed and not built (ruling G15; Definition, section 8).

**Whose grant.** The operator's, each time. **No session deploys without it, and a worker never does.** Deployment of the platform to the cloud is outside the program.

**The command.** Two deploy definitions of bc-infra, `.github/workflows/cd-prepare.yml` and `.github/workflows/cd-execute.yml`, started by hand, the second of which can change the account (Definition, section 8, "Today"). No command under `ops/` has any authority to change the cloud (ruling G35, the first part).

**The written procedure.** The Definition asks for one written procedure for a deployment. It is not written in this chapter. The existing description is `docs/operations/deployment-topology.md`, "The GitHub Actions Surface", in a chapter that the chapters annex marks for rewriting; this chapter has not checked it against the two definitions.

---

## Commands of Operations that are not rows of the table

### The script scan

**What it is.** The check ruling G35 asks for before a script enters a repository: every file under a folder is classed, scanned and listed with its name, size, kind, mode, owner and findings. It never prints the content of a file.

    node ops/script-scan/cli.mjs status
    node ops/script-scan/cli.mjs check [<folder>] [--json] [--exclude <path>]...

The default folder is `~/bc-stack`. Both verbs only look. There is no `do`.

**Exit codes** (bc-infra `ops/script-scan/README.md`):

| Code | Outcome | Meaning |
|---|---|---|
| 0 | `clean` | every file was scanned or deliberately not opened, nothing was excluded, the walk was complete, and no listed rule matched |
| 1 | `findings` | a rule matched; or a file named like a credential is open to others; or a file could not be read |
| 1 | `partial` | nothing found, but part of the tree was not searched. A partial scan never exits 0 |
| 2 | `could-not-look` | the folder is missing or is a link, an `--exclude` matched nothing, or the usage is wrong |

**Line words of its own.** `FOUND` (a rule matched; the line gives each rule id with a line number, as `url-with-password@12`), `CREDENTIAL` (a file named like a credential, mode 600 or narrower, not opened), `WRONG` (a file named like a credential that is open to others, not opened; or a walk that was not complete), `SKIPPED`, `EXCLUDED`, `NOTSEARCHED`.

**Whose grant.** None. **The record.** None is written.

**The folder is read in two forms, and the Prove worker runs both.** One run cannot read all of `~/bc-stack`: the walk stops at a bound of 10,000 entries, and the folder `odoo-move` alone holds far more. So there are two forms of `check`, both read-only, and neither needs a grant.

    node ops/script-scan/cli.mjs check
    node ops/script-scan/cli.mjs check --exclude odoo-move

- **The default run** stops at the bound inside `odoo-move`. It is the only form this chapter gave until 2026-11-19.
- **The complete walk** leaves `odoo-move` out and reads every other folder to the end. It is the only form that reaches `bc-audit-app`, `evidence` and the folders after them.

Any session that operates this command runs the two, in that order, and reports each with its exit code. A walk of `odoo-move` itself needs one run for each of its subfolders. The Chief made that walk once, for the triage named below; a worker does not repeat it.

**The result today is not clean in either form, and every non-clean line is listed.** `status` exits 0. Both forms of `check` exit 1 with the outcome `findings` and end with a line that says the scan is PARTIAL. The results below were read on 2026-11-19 at 02:19 UTC from bc-infra `7e16520d3bfeda1549baa88b27c3bd9dd749210a`. They are the same, line for line and figure for figure, as those read at 00:47 and at 01:08 UTC that day from bc-infra `f5cfc291f181f30fccc5f314eb52b6ff573c86bd`: the two folders added to bc-infra in between are not under `~/bc-stack`, which is the folder this scan reads.

**The default run.** Its summary line: `check: 10000 entries; 7754 scanned; 10 credential-by-name files not opened; 1 links or special files skipped; 0 excluded; 8 with findings; 1520 not (fully) searched; 609 hard-linked (scanned under their own names); 8 wrong`.

| Line today | Count | Folder | Rule id | Class, by the triage | Owner |
|---|---|---|---|---|---|
| `WRONG  the walk of /Users/anant/bc-stack was not complete: 10000 entries reached; stopped at` a path below `odoo-move`, `(entry limit 10000 reached); nothing past it was checked` | 1 line | `odoo-move` | none: the bound | Not a finding in a file. The default run stops at the entry bound, so it is partial (bc-infra `ops/script-scan/README.md`). | None |
| `FOUND` | 7 files | `odoo-move/u4aws-rehearsal/r4`, in its two clones `granted` and `clean` | `high-entropy-assignment` | 6 false matches (three files, each in both clones). 1 true exposure: lines 16 and 26 of `_archive/pilots/systems/odoo/infra/ec2-userdata.sh` in the clone `granted`. | The operator |
| `FOUND` | 1 file | the same, clone `granted` | `cli-password-flag` | Test fixture: line 542 of `_archive/pilots/systems/odoo/runtime/deploy_runtime.sh`. | The operator |
| `CREDENTIAL` | 10 lines | 2 at the top level, 2 in `secrets`, 6 below `odoo-move` | none: the name | Not opened by the scan or by the triage. Each is mode 600. | Not classed |
| `NOTSEARCHED` | 3 lines, 1,520 files | all but five below `odoo-move` | `binary-not-searched` 1,509; `file-too-large-not-searched` 9; `line-too-long-not-searched` 2 | Not searched, so not covered by any result. | Not classed |
| `SKIPPED` | 1 line | the top level | none | The supervisor's socket, never opened. | None |

**The complete walk.** Its summary line: `check: 5736 entries; 4885 scanned; 13 credential-by-name files not opened; 4 links or special files skipped; 1 excluded; 25 with findings; 61 not (fully) searched; 0 hard-linked (scanned under their own names); 25 wrong`. The 25 are 17 `FOUND` lines and 8 `WRONG` lines. It prints no line on an incomplete walk.

| Line today | Count | Folder | Rule id | Class, by the triage | Owner |
|---|---|---|---|---|---|
| `FOUND` | 3 files | `evidence/actc-kit-20261025` | `url-with-password` | True exposure, of one value: the password of a disposable database container of a past act, published on the loopback address only. | The operator |
| `FOUND` | 1 file | `bc-audit-app/src/github-app` (`service.js`, line 134) | `auth-header-literal` | The triage classes it as a template that inserts a variable. The auditor has read the line in the pinned source, bc-external-audit commit `694c2de9a6779b16f648c42f7ed91d77bdda0262`: it builds the Authorization header from a variable and holds no literal credential (reply on exchange thread gen-ddcf4d). That the deployed copy equals that commit is the Chief's triage reading; the auditor has not verified it. | The auditor side |
| `FOUND` | 8 files | `bc-audit-app/node_modules` | `url-with-password` | Third-party packages: 7 test fixtures and 1 documentation example. | The auditor side |
| `FOUND` | 3 files | `bc-audit-app/node_modules` | `high-entropy-assignment` | Third-party packages: 2 false matches and 1 test fixture (a value the package's own authors published). | The auditor side |
| `FOUND` | 1 file | `bc-audit-app/node_modules` | `jwt` | Third-party package: a test fixture. | The auditor side |
| `FOUND` | 1 file | `bc-audit-app/node_modules` | `private-key-block` | Third-party package: a false match. | The auditor side |
| `WRONG  <path>  kind=credential size=<n> mode=644 owner=anant  credential by name, mode 644: a mode with any bit outside owner read and write is wider than 600 (700 fails, 000 passes); not opened` | 8 lines | `bc-audit-app/node_modules/@modelcontextprotocol/sdk/dist`: for each of `esm` and `cjs`, the files `server/auth/handlers/token.d.ts.map` and `token.js.map`, and `examples/client/simpleClientCredentials.d.ts.map` and `simpleClientCredentials.js.map` | none: the name and the mode | Third-party source maps, named after the words "token" and "credentials". Never opened. False matches. | The auditor side |
| `CREDENTIAL` | 5 lines | 2 at the top level, 2 in `secrets`, 1 below `evidence/w9-u94` | none: the name | Not opened by the scan or by the triage. Each is mode 600. | Not classed |
| `NOTSEARCHED` | 3 lines, 61 files | `backups`, `evidence`, `logs`, `state`, `bc-audit-app` and the top level | `binary-not-searched` 8; `file-too-large-not-searched` 51; `line-too-long-not-searched` 2 | Not searched, so not covered by any result. | Not classed |
| `EXCLUDED` | 1 line | `odoo-move` | none | Left out by `--exclude`. | None |
| `SKIPPED` | 4 lines | the top level, `backups/pg` and `bc-audit-app/node_modules/.bin` | none | One socket and three links, never opened or followed. | None |

The complete walk found nothing in `laptop` and nothing in any folder the tables do not name.

**The triage behind the classes.** The classes are from the Chief's triage of 2026-11-19, a read-only reading of every `FOUND` and `WRONG` line that holds no value. Its file is kept outside every repository, so it cannot be cited as a repository source; this chapter gives what it says as the Chief's reading. It tested no credential and connected to nothing. What it found:

- **Two distinct values are true exposures.** One is the password of the disposable loopback database container of a past act, in the three files of the evidence kit. The other is the database password of the archived Odoo pilot, in the rehearsal clones under `odoo-move`; the same bytes are tracked in the repository bc-demo. The complete walk of `odoo-move`, which the triage made folder by folder, printed 140 `FOUND` lines and no `WRONG` line: the same five files in each of 28 rehearsal clones. The default run's eight lines are part of that set.
- **Nothing found is a live credential in a file that another local account can read.** That is the triage's statement. Its ground for the files under `~/bc-stack` is that the home folder of the operator's account is mode 700.
- **Every other line** is a test fixture, a documentation example, a template or a false match, as the tables give it.
- **Whose decision each is.** The auditor side decides for `bc-audit-app`. The operator decides for the evidence kit, for `odoo-move` and for the file tracked in bc-demo. bc-demo belongs to function PV, which is parked and held. The findings that need someone's act are listed, each with its owner, in the Definition, in the table "Findings of the script scan that are not Operations' scripts". No session acts on any of them.

**The Chief's scope calls.** Four folders under `~/bc-stack` hold none of Operations' scripts. The scan's findings in them are reported by file, rule id and count, and are neither accepted nor repaired by Operations.

- **`odoo-move` and `laptop`.** On 2026-11-18 the Chief made this scope call (DevHub, checkpoint 1520 of session SES-7decb4, recorded at 11:51 UTC): the folders `~/bc-stack/odoo-move` and `~/bc-stack/laptop` are not Operations' scripts. The first is the record and the data of a finished move of the source system; the second holds one script written for one past act. The scope call is a session's record in DevHub. It is not written in bc-infra; bc-infra's list of known entries describes both folders only as data folders, `odoo-move` as "the Odoo move records, the licence scripts and the package copy of odoo.sh" and `laptop` as holding a script of "a past act of 2026-09-30" (bc-infra `ops/host-files/known-entries.json`). DevHub's program record adds that the scan of the two folders was completed for scripts folder by folder (row PRG-a770dc).
- **`bc-audit-app` and `evidence`.** On 2026-11-19 the Chief made a second scope call: `~/bc-stack/bc-audit-app`, a deployed copy of the auditor's application with its third-party packages, and `~/bc-stack/evidence`, the records of past acts, hold none of Operations' scripts. The auditor agreed on a condition (exchange thread gen-fc4135, reply `RESPONSE-Codex-gen-fc4135-01-p3c5-design-boundary-2026-11-19.md`, point 9): "Third-party packages in the deployed auditor app and a record of a past act need not become Operations commands", provided the `FOUND` lines are triaged file by file without publishing a value. The triage above is that triage. This scope call is stated here on the Chief's word; no record of it in DevHub was read for this text.

Condition P3-C5, which asks that Operations' scripts have been checked for secrets, is not judged by this chapter.

**The triaged list.** These are the files in which the triage read a finding, one row for each file and rule. A result is compared with this list file by file. The two tables above, which count by folder, are a summary for the report and are not what a result is compared with.

How to read a printed line against the list:

- A `FOUND` line prints the file's whole path, and then each finding as a rule id and a line number, `rule@line`. A path in the list is relative to the scanned folder: the scan prints `/Users/anant/bc-stack/` before it.
- **Findings** is the number of `rule@line` items the line carries for that rule.
- **Lines at the reading** are the line numbers printed on 2026-11-19. They are given so that a moved finding can be told from a new one. A line number alone is not part of what makes a finding listed.
- The class is the triage's. The owner is the one the summary tables give for the folder.

The complete walk (`check --exclude odoo-move`): seventeen `FOUND` files.

| File, relative to `~/bc-stack` | Rule id | Findings | Lines at the reading | Class, by the triage |
|---|---|---|---|---|
| `evidence/actc-kit-20261025/README.md` | `url-with-password` | 1 | 12 | True exposure |
| `evidence/actc-kit-20261025/standup.out` | `url-with-password` | 3 | 2, 3, 5 | True exposure |
| `evidence/actc-kit-20261025/standup.sh` | `url-with-password` | 3 | 19, 20, 22 | True exposure |
| `bc-audit-app/src/github-app/service.js` | `auth-header-literal` | 1 | 134 | Template |
| `bc-audit-app/node_modules/zod/src/v4/mini/tests/string.test.ts` | `jwt` | 2 | 326, 329 | Test fixture |
| `bc-audit-app/node_modules/zod/src/v4/classic/tests/string.test.ts` | `url-with-password` | 1 | 338 | Test fixture |
| `bc-audit-app/node_modules/zod/src/v4/classic/tests/template-literal.test.ts` | `url-with-password` | 8 | 655, 656, 657, 658, 660, 662, 663, 689 | Test fixture |
| `bc-audit-app/node_modules/jose/dist/webapi/key/import.js` | `private-key-block` | 1 | 19 | False match |
| `bc-audit-app/node_modules/ip-address/README.md` | `high-entropy-assignment` | 1 | 1 | Test fixture (a value the package's own authors published) |
| `bc-audit-app/node_modules/hono/dist/utils/basic-auth.js` | `high-entropy-assignment` | 1 | 13 | False match |
| `bc-audit-app/node_modules/hono/dist/cjs/utils/basic-auth.js` | `high-entropy-assignment` | 1 | 34 | False match |
| `bc-audit-app/node_modules/fast-uri/README.md` | `url-with-password` | 1 | 39 | Documentation example |
| `bc-audit-app/node_modules/fast-uri/test/parse.test.js` | `url-with-password` | 1 | 159 | Test fixture |
| `bc-audit-app/node_modules/fast-uri/test/serialize.test.js` | `url-with-password` | 1 | 38 | Test fixture |
| `bc-audit-app/node_modules/fast-uri/test/uri-js.test.js` | `url-with-password` | 4 | 183, 316, 474, 496 | Test fixture |
| `bc-audit-app/node_modules/fast-uri/test/fixtures/uri-js-parse.json` | `url-with-password` | 3 | 78, 91, 104 | Test fixture |
| `bc-audit-app/node_modules/fast-uri/test/fixtures/uri-js-serialize.json` | `url-with-password` | 1 | 74 | Test fixture |

The complete walk: eight `WRONG` files. Each is named like a credential, is mode 644 and is not opened, so its line carries no rule id and no line number. All eight are below `bc-audit-app/node_modules/@modelcontextprotocol/sdk/dist/`. The triage classes each as a false match.

| File, relative to that folder |
|---|
| `esm/server/auth/handlers/token.d.ts.map` |
| `esm/server/auth/handlers/token.js.map` |
| `esm/examples/client/simpleClientCredentials.d.ts.map` |
| `esm/examples/client/simpleClientCredentials.js.map` |
| `cjs/server/auth/handlers/token.d.ts.map` |
| `cjs/server/auth/handlers/token.js.map` |
| `cjs/examples/client/simpleClientCredentials.d.ts.map` |
| `cjs/examples/client/simpleClientCredentials.js.map` |

The default run (`check`): files below `odoo-move`. The triage read the same five files in each of 28 rehearsal clones, with the same line numbers in every clone. A file of this part of the list is a clone root followed by one of the five paths.

| File, relative to a clone root | Rule id | Findings | Lines at the reading | Class, by the triage |
|---|---|---|---|---|
| `sources/odoo19ee/tests/slice/test_slice3.py` | `high-entropy-assignment` | 2 | 75, 76 | False match |
| `sources/odoo19ee/tests/slice/test_slice4.py` | `high-entropy-assignment` | 2 | 73, 78 | False match |
| `sources/odoo19ee/estates/demo-mfg-in/evidence/v2.1.0-rc7/schema-capture-verifier-v6/verify_schema_capture.py` | `high-entropy-assignment` | 1 | 35 | False match |
| `_archive/pilots/systems/odoo/runtime/deploy_runtime.sh` | `cli-password-flag` | 1 | 542 | Test fixture |
| `_archive/pilots/systems/odoo/infra/ec2-userdata.sh` | `high-entropy-assignment` | 2 | 16, 26 | True exposure |

The 28 clone roots, each relative to `~/bc-stack/odoo-move`:

- `u4aws-rehearsal/r1`, `r2`, `r3` and `r4`, each with `clean` and `granted` (8);
- `rt-rehearsal/u2/clones` and `rt-rehearsal/u2b/clones`, each with `clean`, `granted`, `autocrlf`, `granted-crlf`, `granted-denial` and `granted-other` (12);
- `u3-rehearsal/r1` to `r7`, each with `pkg` (7);
- `u4-rehearsal/r1/pkg3` (1).

Which of these the default run prints depends on where its walk stops. At the reading of 2026-11-19 it printed eight: all five files of `u4aws-rehearsal/r4/granted`, and the first three of `u4aws-rehearsal/r4/clean`, where the walk stopped. The default run also prints one `WRONG` line on the incomplete walk itself; that line is listed, and the path at which it says the walk stopped is not compared.

**Where the list comes from, and how far it was checked.** The files, rule ids, counts and line numbers of the complete walk, and the eight lines of the default run, were printed by the scan on 2026-11-19 at 01:08 UTC from bc-infra `f5cfc291`, and again at 02:19 UTC from bc-infra `7e16520d`, and are the same as the triage's, file by file: seventeen `FOUND` files and eight `WRONG` files in the complete walk, eight `FOUND` files and the one `WRONG` line on the walk in the default run, each with the rule ids, counts and line numbers the list gives. The other 27 clone roots and their files are from the triage alone: the walk of `odoo-move` was not made again for this text. The classes, and the statement that nothing found is a live credential in a file another local account can read, are the Chief's reading. No independent party has proven them; the auditor said so in the reply on exchange thread gen-ddcf4d.

**How to tell a listed line from any other.** This applies the one rule of "What to do on WRONG or COULDNOT". A finding is known by the file that holds it and by its rule id. Folder, rule id and count are not enough: a new file can be matched on the day an old finding goes, and the counts would not move. The listed result today, for each form, is exit 1 with the outcome `findings` and a PARTIAL scan.

1. **Listed: report it and pass on.** A `FOUND` line whose file is on the triaged list, which carries only the rule ids the list gives for that file, each with no more findings than the list gives. A `WRONG` line that names one of the eight listed files with the reason "credential by name". In the default run, the one `WRONG` line on the incomplete walk. Report each by file, rule id and count, with the line numbers as printed, the class the list gives, the owner, and the words "outside Operations' scripts by the Chief's scope call".
2. **A changed line number: report it and pass on.** A listed file, under the same rule id, with no more findings than the list gives, where a line number differs from the list's. Report the file, the rule id, and the old and the new line numbers. It does not halt the sequence.
3. **A new or changed finding halts the sequence.** Each of these does:
   - a `FOUND` or `WRONG` line for a file that is not on the triaged list, in any folder, and whatever the counts by folder and rule are;
   - a `FOUND` line for a listed file that carries a rule id the list does not give for that file;
   - more findings for a listed file and rule than the list gives;
   - a `FOUND` line below `odoo-move` whose clone root is not one of the 28, or whose path below the clone root is not one of the five;
   - a `WRONG` line for one of the eight listed files with any other reason;
   - a `WRONG` line on an incomplete walk in the complete walk, which lists none;
   - an exit of 2.

   Report at once by file, rule id, count and line numbers, as printed. Nothing further is run. The finding is then triaged without publishing a value: that triage is the Chief's to arrange, and a worker does not make it. The file is not opened, and no text of it is printed or copied.
4. **A listed finding that is gone is reported.** A listed file that the run no longer prints, or a listed file with fewer findings than the list gives, is reported by file and rule id as gone or as fewer. It is no reason to stop. It never makes room for a new finding: rule 3 holds whatever has gone. The default run prints fewer `FOUND` lines when new entries elsewhere move the place where its walk stops, and may print other listed files when that place moves the other way.
5. **Lines that are counted and do not halt.** `CREDENTIAL`, `NOTSEARCHED`, `SKIPPED` and `EXCLUDED` lines decide nothing here; a count other than the summary table's is reported. A file named like a credential that is open to others is not printed as `CREDENTIAL`: it is printed as `WRONG`, and rule 3 holds for it. The figures of the summary line for entries and files scanned move from day to day, as records and logs are written; they are reported and not compared.

A class is not something a worker checks. The list gives it so that the report can carry it. Do not open a file the scan names, in any folder, to see whether its class is right.

**What a clean result means.** Only that no listed rule matched in the files that were scanned. It does not mean there is no secret.

### Host-file custody: check, install, put back and retire

**What it is.** Custody of the host scripts under `~/bc-stack`. A manifest says, for each of twenty host files, the hash and mode the host must hold, what starts it, and where its bytes come from: all twenty have their bytes in bc-infra, under `ops/host-files/files/`, and none is named from barecount-devhub. Seven of the twenty were named from barecount-devhub until bc-infra pull request 88 moved their bytes into bc-infra with no byte changed and no install, because the host copies already equalled them (merge commit `f79be43b5469e6c84ae4a35c5edaa99ea946d041`). Five of the seven were written to the host by an installer kept in barecount-devhub. That installer and its five sources left barecount-devhub by pull request 400 (merge commit `5614f134557b51e45251dc666634af9284ec10dc`), so `ops/host-files do` is now the only command that writes any of the twenty. The copies of two of the seven that stay in barecount-devhub, `artifacts/serve-move/serve-guard.mjs` and `dist-manifest.js`, are historical records and not the source the host is checked against. A copy of the retired installer may survive in an old checkout or worktree of barecount-devhub: it is never run, because a run that cannot read its sources leaves a host file empty (bc-infra `ops/launch-agents/README.md`). Twenty-one further scripts are judged retired. Every other entry at the top level of the folder is on a list of known entries. Custody is not an act of the table: these are the scripts Operations' acts will be built from (bc-infra `ops/host-files/README.md`).

**The command.**

    node ops/host-files/cli.mjs status
    node ops/host-files/cli.mjs check
    node ops/host-files/cli.mjs verify
    node ops/host-files/cli.mjs do <name>... --i-am-the-operator <desk grant id>
    node ops/host-files/cli.mjs put-back <name>... --i-am-the-operator <desk grant id>
    node ops/host-files/cli.mjs retire [<name>...] --i-am-the-operator <desk grant id>

| Verb | What it does | Changes |
|---|---|---|
| `status` | for each manifest entry: present, bytes equal, mode equal; then a preview of what `retire` would do | nothing |
| `check` | every manifest entry equal and its source right; every entry at the top level of `~/bc-stack` and in `~/bc-stack/host/` in exactly one of four lists: the manifest, the pending list, the retired list and the known entries | nothing |
| `verify` | reads the host again and compares it with the last custody record, the manifest and the last retire record | nothing |
| `do` | installs the named entries from committed bytes of the main branch | the named host files; the record folder |
| `put-back` | reverses a completed install from the bytes `do` kept | the named host files; the record folder |
| `retire` | moves judged retired scripts into `~/bc-stack/archive/retired-host-files` | the moved scripts; the archive folder; the record folder |

**A session without a grant runs `status`, `check` and `verify` only.** `do`, `put-back` and `retire` each need the operator's recorded desk grant, single use, whose line names the entries: `AUTHORIZE host files install | ...`, `AUTHORIZE host files put back | ...`, `AUTHORIZE host files retire | ...`. `do` also requires a clean checkout whose HEAD equals the remote's main branch. A retire is a reversible move, not disposal.

**Exit codes.** `status`, `check` and `verify`: 0 clean, 1 on any WRONG, 2 on a COULDNOT with no WRONG. For `do`: 0 installed; 2 refused or stopped with no host file changed; 3 changed and restored; 4 not restored; 5 installed but the record could not be written. For `put-back`: 0; 2; 3 restored; 4 not restored; 5. For `retire`: 0 retired; 2 unchanged; 3 put back; 4 not put back (bc-infra `ops/host-files/README.md`).

**The record.** `~/bc-stack/state/host-files/`. Four records exist from real runs:

| Record | Act |
|---|---|
| `20261117T092337697Z-f8f420785401-retire.json` | The retire of 2026-11-17: twenty scripts moved to the archive folder (grant `2026-11-17T09-20-51-660Z-ee76a3a5`, as `verify` prints it). |
| `20261118T022203060Z-f9d0274d00e4.json` | The install of 2026-11-18, 02:22 UTC: `pg-backup.sh`. |
| `20261118T161007397Z-1e7b87d928da.json` | The install of 2026-11-18, 16:10 UTC: `bc-core-signin.sh` (mode 0700), `odoo.sh` (the script itself, no longer five lines that start another file) and `serve-core-ref-v2.sh`, from bc-infra `1e7b87d928daa67aae6760bc4703a3578c7838bc`, under the operator's grant `2026-11-18T16-09-22-055Z-9533e033`. |
| `20261118T171044670Z-18cd69e0e4c4-retire.json` | The retire of 2026-11-18, 17:10 UTC: `serve-core-ref.sh` moved to the archive folder, from bc-infra `18cd69e0e4c4778942c47c4981ab543809057776`, under the operator's grant `2026-11-18T17-09-57-991Z-407d6e2d` (desk request 514). |

The folder also holds the claim files of each grant used, named `install-claim-...` and `retire-claim-...`. `put-back` has not been run on the real host. `verify` is how a record is read: it compares the host with the last custody record, the manifest and the last retire record, and prints the record's result, source commit, time and grant.

The grant of 16:09 UTC also authorised one edit by hand: line 79 of `~/bc-stack/README.md` was replaced, and the README as it was is kept beside it as `README.md.bak-20261118T1611Z`. Line 79 now says that `serve-core-ref.sh` is retired and that a return to a previous build is made by `ops/serve-move`. That edit is not an act of the command; the kept copy is a known entry of the custody lists since bc-infra `18cd69e0` (bc-infra `ops/host-files/README.md`).

**A clean result today.**

- `status` exits 0. It prints `20 of 20 present with bytes and mode equal to the manifest`, then the preview of a retire. The preview names each of the twenty-one retired scripts as `not in the act: ... it is in the archive only, with the recorded bytes`, and says `nothing would move: no retired entry that is not held is at its active path`.
- `check` exits 0. Its first line: `check: 20 manifest entries (20 with bytes in bc-infra, 0 named from barecount-devhub); 21 judged retired; 0 pending (not judged into the manifest or the retired list); 41 known entries`. Its summary: `64 OK; 6 NOTE; 0 WRONG; 0 COULDNOT`, and it ends `check: clean`, followed by one line that starts `check: limit`.
- `verify` exits 0. It names the last custody record (the install of 16:10 UTC) and the last retire record (the retire of 17:10 UTC, with its grant), says of `serve-core-ref.sh` that it is `absent at its active path, as the record says` and that the archive copy `holds the recorded bytes, mode 0600`, and ends `verify: the host matches the last custody record and the manifest (bytes and modes re-read now), and the last retire record`. Among its `OK` lines, three retired scripts are read as `replaced by barecount-devhub 1e571f34cae5:...`: those are pins in barecount-devhub's history, kept as the record of what was read when the scripts were retired. They still read `OK` now that two of the three pinned files have left that repository's main branch, and they do not say where a command is kept today (bc-infra `ops/dev-secrets/README.md`).

These three results were read on 2026-11-19 at 02:18 UTC from bc-infra `7e16520d`. They equal the results of 2026-11-18, 17:12 UTC, but for the first line of `check`: until bc-infra pull request 88 seven of the twenty entries were named from barecount-devhub. The Chief read `check` from the same commit at 02:16 to 02:17 UTC, with the same result. No line of the three verbs is `WRONG` or `COULDNOT` today. The lines that are not `OK` are known, and none changes the exit code:

| Line today | Reason |
|---|---|
| `NOTE  ~/bc-stack/<name>.kept-<stamp>  the kept copy of an earlier do`, four lines | The previous bytes kept by the two installs: `pg-backup.sh.kept-20261118T022203060Z`, and `bc-core-signin.sh`, `odoo.sh` and `serve-core-ref-v2.sh` each with `.kept-20261118T161007397Z`. `put-back` would read them. |
| `NOTE  retired list: 21 judged (18 retire, 3 replace); 0 still at their active path ...; 21 moved to ~/bc-stack/archive/retired-host-files; 0 in neither honest state` | Every judged script is in the archive folder. Until 17:10 UTC this line read 1 and 20. |
| `NOTE  19 listed folders ... are not walked` | A stated limit: what is inside them is the script scan's to read. |
| `check: limit: 0 retired scripts are still at their active path and still runnable` | The same count. The line is printed on every run and adds that "clean" does not mean a retired script was moved. |
| `retire-preview: retire would refuse at this checkout: this checkout is not clean` (in `status`) | The untracked folder `_wt/` in the shared copy of bc-infra; see "Before any act". A retire is run from a clean checkout of the main branch. Nothing awaits a retire today. |

**The retire of `serve-core-ref.sh`, 2026-11-18.** `serve-core-ref.sh`, the older launcher of the engine, was held back from the retire of 2026-11-17 because two host texts named it as needed for a rollback: line 3 of the host copy of `serve-core-ref-v2.sh` and line 79 of `~/bc-stack/README.md`. Both were corrected on 2026-11-18 under grant `2026-11-18T16-09-22-055Z-9533e033`, the first by the install and the second by the edit. bc-infra pull request 86, merged as `18cd69e0`, removed the hold from the script's entry (bc-infra `ops/host-files/README.md`). At 17:10 UTC the same day `ops/host-files retire` moved the script to `~/bc-stack/archive/retired-host-files`, from a clean checkout of bc-infra at `18cd69e0e4c4778942c47c4981ab543809057776`, under the operator's desk grant `2026-11-18T17-09-57-991Z-407d6e2d` (desk request 514; text SHA-256 `407d6e2dbce632604724fe06c0b3ca589b6bdae6cea76a088302841caa13df13`, read at the desk on 2026-11-18). The custody record is `~/bc-stack/state/host-files/20261118T171044670Z-18cd69e0e4c4-retire.json`. `check` then read clean, with `0 still at their active path` and `21 moved`. The engine was not restarted (DevHub's program record, row PRG-fec959). No retired script is at its active path today. A retire is a move, not disposal: the script's bytes are kept in the archive folder, mode 0600.

**On any WRONG.** No `WRONG` or `COULDNOT` line of this command is listed today, so one halts the sequence. A host file that differs from its manifest entry is reported with its line. So is an entry at the top level of `~/bc-stack` that is in none of the four lists. Neither is put right by copying, moving or deleting a file by hand: `do` is the only way to install and `retire` the only way to move, and both are the operator's to grant.

### The launch agents check

**What it is.** Three launch agents of the operator's account keep parts of the development machine running: `com.barecount.process-compose` keeps the supervisor, `com.barecount.devhub-watchdog` runs the outage watchdog, and `com.barecount.backup-watch` calls the backup's age check on a schedule. Their three files were placed by the host installer that barecount-devhub held until pull request 400. bc-infra now holds the three files as data, with a command that only looks at them (bc-infra pull request 89; bc-infra `ops/launch-agents/README.md`). It is not a row of the table of acts.

    node ops/launch-agents/cli.mjs status
    node ops/launch-agents/cli.mjs check

**There is no `do` and no `verify`.** `status` reads the committed list and nothing on the host. `check` reads the three committed files, the three files under `~/Library/LaunchAgents` and the manifest of `ops/host-files`, and runs one program, `/bin/launchctl print gui/<uid>/<label>`, once for each label. That is a read-only listing. Nothing is written, loaded, unloaded or started.

**Three looks, kept apart.** For each agent `check` prints one line for each look, and each line has its own verdict:

| Look | What is compared | What it does not show |
|---|---|---|
| (a) committed | the file in the checkout against the hash, label, program and arguments recorded in `agents.json` | anything about the host |
| (b) host | the file under `~/Library/LaunchAgents` against the same recorded hash and mode | what the launcher holds; the file may have been written after the agent was loaded |
| (c) loaded | what the launcher holds for the label: its program, its arguments and the file it says it loaded | every other key of the agent, and whether the file still has the bytes that were loaded |
| (d) | each host file the agent names is an entry of the custody manifest with its bytes in bc-infra | the host file's bytes, which `ops/host-files check` judges |

**None of the looks proves another.** A committed file equal to the record does not show the host file. An equal host file does not show what is loaded. A loaded agent with the right program does not show that its file is the reviewed one. The check prints this as a `NOTE` on every run.

**Exit codes.** 0 no `WRONG` and no `COULDNOT`; 1 a `WRONG`; 2 a `COULDNOT` or bad usage.

**Whose grant.** None for the two verbs. Writing an agent's file, loading an agent, unloading one and restarting one are each a separately granted act of the operator. No command of Operations performs any of them. The README gives hand lines for them; it marks them as derived from the installer's text and not run as written. No session runs one.

**The record.** None is written. The README records each past act of the installer on this host, each marked as recorded (a record of the act is named) or derived (inferred from what the host and the repositories hold).

**A clean result today.** `status` exits 0 and names the three agents. `check` exits 0. It prints twelve `OK` lines, four for each agent, and three `NOTE` lines, and ends `result: 12 ok, 3 note, 0 wrong, 0 could not look`. The Chief read the same closing line from the same commit at 02:16 to 02:17 UTC that day. The three `NOTE` lines are known and do not change the exit code:

| Line today | Reason |
|---|---|
| `NOTE  ~/Library/LaunchAgents: 9 other com.barecount.* plist(s) are there, not held by this command and NOT judged: ...` | Nine further agents' files are in the folder: `pg-backup`, `pg-backup-catchup`, six named `relay-...` and `shallow-watchdog`. The command names and counts them and judges none. The agent that runs the nightly backup, `com.barecount.pg-backup`, is one of the nine. |
| `NOTE  the results (a) committed, (b) host and (c) loaded are three separate looks: ...` | The fixed statement that none proves another. |
| `NOTE  this command has no do: ...` | The fixed statement that a change of an agent is the operator's act. |

**On WRONG or COULDNOT.** No such line of this command is listed today, so one halts the sequence. Report the line as printed. Do not write, load, unload or restart an agent. A change of the path of Node, or of the home folder, makes look (b) or (c) read `WRONG` until the data in bc-infra is changed by review: the README calls that the intended signal.

**Carried to the Lock step** (the README's own list): a `do` for a launch agent, if one is wanted; the nine other agents' files; the command with the four verbs for "start, stop or restart a service", with the restart of the supervisor; and the DevHub entry of the supervisor's file.

### The secret writers in custody

**What it is.** Not a command. bc-infra `ops/dev-secrets` holds three scripts that write a development credential or secret, taken into custody from barecount-devhub by bc-infra pull request 89, with the private request-file helper all three use and the pinned file that names the development sign-in pool (bc-infra `ops/dev-secrets/README.md`). They left barecount-devhub by pull request 400.

| Script, below `ops/dev-secrets` | What a run writes |
|---|---|
| `scripts/ops/reset-dev-cognito-password.sh` | a permanent password for one user of the development sign-in pool, and the same value under one existing key of the development secret |
| `scripts/ops/set-dev-secret-key.sh` | one existing key of the development secret |
| `scripts/fill-billing-secret.sh` | the whole of the billing secret |

**Who runs them.** Only the operator, in his own Terminal, each run under his grant for that act. No session runs one, in any form, and the Prove worker never does. They are not commands with the four verbs: there is no `status`, `check`, `do` or `verify` here. Moving them changed where their bytes are kept and nothing else. In the README's words, no script gains authority by it.

**What is recorded.** `custody.json` gives, for each of the five files, its path in barecount-devhub, the source commit `6f8498b7b82126d8a8286bd5f903d0a522c70ad0`, the hash of the source bytes, the hash of the bytes held, and every line that differs. One line of one file differs: line 78 of the reset script, which now prints the path of the finishing script in the checkout it runs from, where it printed a path that was true only inside barecount-devhub. The auditor required that change. Every other byte is the source's, and a test holds that.

**No script was run for real from bc-infra.** The barecount-devhub bytes of the reset script ran once, on 2026-11-16, by the operator, under desk grant `2026-11-16T11-16-56-065Z-dd4fbf42` (DevHub's program record, row PRG-d873b0, as `custody.json` cites it); the bytes held now differ by that one line and have not run. No real run of the second script is recorded, and the auditor answered that condition P3-C5 needs none: a secret write is the operator's granted act, not an act of the table. Whether the third has run is not established. The tests run the scripts against a stand-in for the cloud command line, with no call to the cloud.

**The script that was not moved.** barecount-devhub also held `rotate-pg-superuser.mjs`, the script that changed the database superuser's password; the host evidence the README gives dates that act 2026-09-28. It was written for one past act, so by ruling G35 it is recorded and removed, not moved: `custody.json` records its exact source bytes, the README records its past act and why a new run fails its own checks today, and it left barecount-devhub by pull request 400. Its bytes stay readable in that repository's history as a record. They are not a route for any act. A new change of that password needs a new command, built and reviewed when one is next wanted; it is the operator's act, a credential write and a database change.

**What stayed in barecount-devhub.** `scripts/ops/check-dev-signin.js` and `scripts/ci-runner-collector.js` stay there as Development's: the first signs in the way DevHub does and writes nothing, and the second is called by DevHub's own code. barecount-devhub also keeps its own copy of the pool file, which one of its pages reads. So two copies of that file exist, with the same bytes, held equal by a test on each side.

**Carried to the Lock step.** A form of each writer with the four verbs, its `do` under a desk grant line. One copy of the pool file. The new command for a change of the superuser's password, when one is wanted.

**What the auditor did and did not review.** The auditor accepted the change with a boundary (the reply on exchange thread gen-9551ac): it read the files by commit and made no real call to the cloud, no credential or secret write, and no change of an agent. It has not read the host.

### The environment names check

**What it is.** The one list of environment names (`dev`, `stg`, `prod`; ruling G13), committed as `ops/environments/environments.json`, checked against the known places in the repositories that declare an environment.

    node ops/environments/cli.mjs status
    node ops/environments/cli.mjs check [--repos-dir <folder>] [--ref <git ref>] [--only <repository>]...

Both verbs only look, through read-only git at `origin/main` of each repository beside bc-infra. There is no `do`. Nothing is written.

**Exit codes.** 0 no `WRONG` and no `COULDNOT`; 1 a `WRONG`; 2 a `COULDNOT` or bad usage.

**Line words of its own.** `EXCEPTION`: a name off the list that the list of exceptions names for that repository, path and value, with its reason.

**A clean result today.** `status` exits 0 and prints `25 places in 6 repositories; 17 exceptions`. `check` exits 0 and ends `result: 20 ok, 17 exception, 0 wrong, 0 could not look (ref origin/main)`.

**The 17 `EXCEPTION` lines are known and expected.** Every one is in the engine (bc-core) or in the operator console's copy of the engine's codes (bc-admin): the words `staging`, `production` and `development`. How the engine's code and requests spell an environment is ruling B17, due in phase 5, and several of the files are under the hold on the engine. The list of exceptions only shrinks (bc-infra `ops/environments/README.md`).

It is a list of known places, not a search of every text. A new place that declares an environment is added to the list by hand. A `WRONG` line names a place whose environment name is off the list and is not a listed exception. No `WRONG` or `COULDNOT` line of this command is listed today: one halts the sequence and is reported with its repository and path. A count of `EXCEPTION` lines other than 17 is reported.

---

## What is not yet true

**Operations is not locked in phase 3.** By ruling G37 its Lock step stays open by name, as conditions P3-C6 and P3-C7 do under ruling B2, and is done when P3-C7 is met; phase 3 exits without it. The cost the operator accepted: Operations enters phase 4 unlocked, with no guard yet against a second way to perform an act and no code-rule baseline for its files, until P3-C7 is met. This chapter is `drafting` until then.

**DevHub says the same.** DevHub's definition of the program is level with bc-docs `852b3b5c` since barecount-devhub pull request 398 was merged as `6f8498b7` and DevHub was restarted (row PRG-41c880). Read on 2026-11-18 at 17:15 UTC, `GET http://127.0.0.1:4000/api/program/status` gave the definition's state as `current` at that commit (bc-docs' main branch was then one merge further, at `22357686`, the merge of this chapter's draft), and listed the Lock step of OP under `carried_lock_steps`: carried by ruling G37, done when condition P3-C7 is met, with two things missing, that the Chief has not judged P3-C7 met and has not judged the Lock step complete. The same answer gave P3-C5, P3-C6 and P3-C7 as not met, the last two carried by ruling B2, and the other six conditions of phase 3 as met. That is the read of 2026-11-18, and it was not made again for this text. Since then barecount-devhub pull request 399 (merge commit `35a736934c4ed4880ceea187c0538dcd40103fe6`) drew DevHub's definition again after bc-docs pull request 243; what the program record answers today was not read.

**This section is not the carried list.** Ruling G37 says that every item of the Definition's lists "What must change" that is not done when condition P3-C5 is met is carried by name in the Definition, with its owner and when it is taken. That list is in the Definition, in the section "What is carried past phase 3". It was drawn on 2026-11-18 and is merged by the same change as this text. Where this section and that list differ, the list is the one to follow and the difference is a defect to be reported. DevHub's program record held no judgement of P3-C5 at the read of 17:15 UTC on 2026-11-18. What follows is what this chapter could ground, item by item: by the reading of 2026-11-19 where the item rests on a command of bc-infra `ops/` or on a main branch, and by the looks of 2026-11-18 where it rests on a file of the host, as each item says. A statement without a "not established" is something read at a main branch or seen through a read-only look.

**Of the function as a whole.**

- bc-infra `ops/README.md` still opens with the words "DRAFT: prepared before the design is approved."
- Start, stop or restart a service; prove a migration on a restored copy; apply a migration; and deploy a cloud unit have no command of Operations with the four verbs. By ruling G38 the first three count, for condition P3-C5, as performed as they are performed today, and the fourth is not counted; a command with the four verbs for each of the first three stays owed, no later than the Lock step of Operations (see "The acts of Operations").
- A restart of the supervisor has one written route, bc-infra `ops/README.md`, "The last resort". It is labelled derived and has not been run as written. The installer whose steps it repeats left barecount-devhub on 2026-11-19.
- The launch agents have no command that changes them. `ops/launch-agents` looks at three and has no `do`; nine further agents' files of the same account are named by its check and not judged. A `do`, if one is wanted, and the nine are carried to the Lock step.
- The three secret writers are in custody in bc-infra `ops/dev-secrets` and are not commands with the four verbs. None was run for real from there. A form of each with the four verbs is carried to the Lock step.
- Two copies of the file that names the development sign-in pool exist, bc-infra's and barecount-devhub's, held equal by a test on each side. One copy is carried to the Lock step.
- The auditor has not read the host. Each host fact in this chapter is a reading of the Chief or of a worker.

**Section 1, environments.**

- Item 1, the chapters and the local runbook use the three names and the two words. The 25 known places agree (the environment names check, today). The local runbook did not when it was read on 2026-11-18: line 70 of `~/bc-stack/README.md` said "rehearsal". Line 79 said it too until it was replaced on 2026-11-18 (see "Host-file custody").
- Item 2, the engine reads one declared environment name: not done. The 17 exceptions stand, and the change waits for ruling B17.

**Section 2, services.**

- Item 1, DevHub, the console and the portal each given a build tree and a pinned commit: not done. In `~/bc-stack/process-compose.yaml`, read on 2026-11-18, those three run from the shared copies of their repositories. Only the engine runs from a tree of its own.
- Item 2, the runbook produced from the supervisor's file: not done. `~/bc-stack/README.md` is written by hand and names, as served now, a serve move of 2026-09-30. bc-infra `ops/` holds no command that produces it.

**Section 3, builds.**

- Item 2 is done: one real move and one return, 2026-11-18. A failed live move, and a live return after a failure, have not happened.
- Item 3, the chapter rewritten: not done. `docs/operations/serve-moves-and-live-windows.md` still describes the twin trees and the rehearsal with a forced failure, which ruling G14 retired. The committed tools for the older procedure removed: not done. They are still on barecount-devhub's main branch at `5614f134`, in `artifacts/serve-move/toolkit/` and `artifacts/w9-serve-move-4/tools/`. Pull request 400 did not remove them: it removed the host installer and the host sources, which are another thing.
- The auditor's separate clearance of each serve move is still required.
- A move that changes engine source cannot be made by the command until a reference run has passed on its commit.
- The Definition gives one procedure for every service. Only a move of `bc-core` has been made.

**Section 4, settings and secrets.**

- The identity is named in three places and the values form two classes (exception four of the ruling on the secrets condition). It closes when the engine is served from a build at or after bc-core commit `b38de288`. Which identity is the one identity is left to the operator (Definition, section 4).
- Item 1, the second loader removed: done on the engine's main branch (bc-core `fd4b55ca` lists `scripts/with-dev-secrets.mjs` and no second loader). The served build, `ec72438b`, is older and still holds `scripts/with-demo-secrets.mjs`. The unread credential files removed: not done. `~/bc-stack/secrets` holds two files, by name and mode only.
- Item 2, the shared copy's settings file loses its database addresses: not done (exception one).
- Item 3, the session read tool connects through a read-only login (the operator's act): not established by this chapter. The check prints `UNKNOWN` for it.
- Item 4, the backup files and their folder readable by the owner only: true today for the folders (`ops/backup check`) and for the seven dumps (mode 0600 in `ops/backup status`).
- Item 5, the three literal passwords removed from the texts: not done for `docs/implementation/infrastructure.md`, which still prints one at line 115 at the main branch. The two files of the database-reading tool were not read for this chapter; that tool is in no repository (Definition, section 10).

**Section 5, the schema-change path.**

- Item 1, migrations 0032, 0034, 0035 and 0038 withdrawn: done. At bc-db `ca1aabd1` none is under `migrations/`, and the text of each is kept under `docs/withdrawn-migrations/`.
- Item 2, the two chapters, bc-db's README and its roles document rewritten. `docs/implementation/data-model-and-schema.md` now gives the bc-db path and calls the older folder frozen. `docs/operations/upgrade-and-migration.md` carries a dated banner of 2026-11-15 that classes it as history. bc-db's `README.md` and `tools/runner/ROLES.md` each say they replace the earlier text. The correction of the engine comment waits for S3's Modify step, as the item says.
- Item 3, the register created and the comparison command written and run once: done. The register exists and holds no line. Two recorded runs are in `~/bc-stack/state/schema-compare/`; the newest, of 2026-11-17, has the verdict PASS. Its limits: an empty register means that no real line's age has been through a run; the comparison is run by hand; the tenant migrations are not compared.

**Section 6, backup and restore.**

- Item 1, a restore of a backup proven once: done, 2026-11-18. The file proven was taken by the command a minute earlier, not by the nightly run. The dump that the installed nightly script took at 20:30 UTC on 2026-11-18, `pg_dumpall-20261118T203005Z.sql.gz`, has not been proven. At the read of 2026-11-19, 02:18 UTC, `ops/backup check` named as the last proof `proof-20261118T152340837Z-ecf63aad.json`, which proved `pg_dumpall-20261118T152216Z.sql.gz`. So no dump taken by the nightly script has been restored and compared.
- Item 2, the age alarm: `check` is the alarm in form. The launch agent that calls it on a schedule, `com.barecount.backup-watch`, is loaded with a last exit of 0 (`launchctl list`, read on 2026-11-19 at 02:19 UTC), and `ops/launch-agents check` reads its committed file, its host file and its loaded state each as recorded. Four settings, the age bound among them, are not yet the operator's decision.
- Item 3, one backup tool: not done. The nightly script, `ops/backup` and bc-db's `tools/backup/` all exist. By ruling G38 the convergence is carried to the Lock step.
- A proof before every live window that changes a database: not done. The README says `check` does not know the windows yet.

**Section 7, the checks on every change.** The chapter and the settings made to agree: not done. `docs/development/continuous-integration.md`, line 58, says the setting is set on both repositories. Read on 2026-11-18, the repository variable `CI_RUNNER_MODE` is set on bc-core and is not found on bc-db.

**Section 8, cloud infrastructure.** The infrastructure chapter and bc-infra's README rewritten unit by unit: not done. `docs/implementation/infrastructure.md` still describes a repository named `platform-infra-stack` and has no words "designed and not built". bc-infra's `README.md` lists five units, omits the unit for the machines that run the checks, and does not say which are deployed.

**Section 9, the reference run.**

- Conditions P3-C6 and P3-C7 are open by name.
- Item 4, the auditor's App permission, the auditor's account enabled to perform a run, and the change to `engine-hold`: by ruling B2 the change to `engine-hold` is not made before one reference run has passed. Whether the first two are done is not established by this chapter.
- Whether the live Kaveri tenant fails the canonical resolution of `cc-x13pb` version 3.0.0 as the run's copy did is not known (Program, "What is not yet known").
- The README of the command, barecount-devhub `scripts/reference-run/README.md`, still says in its title that no real run has been made.

**Section 10, where the commands are kept.** Host scripts are in custody and not yet commands. All twenty host files of the manifest have their bytes in bc-infra and equal them on the host today; none is named from barecount-devhub, and no install is awaited. The host installer, the five host sources, the three secret writers, the script that changed the superuser's password and the two request-file helpers have left barecount-devhub (pull request 400); `scripts/ops/check-dev-signin.js` and `scripts/ci-runner-collector.js` stay there as Development's, and the two helper copies under `artifacts/serve-move/` stay as historical records. The three launch agents' files are held as data and only looked at. The secret writers are held and are not commands. All twenty-one retired scripts are in the archive folder since the retire of 17:10 UTC on 2026-11-18; none is at its active path. The previous bytes that the two installs kept, the package copy of `odoo.sh` below `~/bc-stack/odoo-move`, and the twenty-one archived scripts stay on the host: their disposal is a later act that bc-infra `ops/host-files/README.md` names as not done. The script scan of `~/bc-stack` is not clean: its listed lines, their classes and their owners are under "The script scan", and the findings that need someone's act are in the Definition, in the table "Findings of the script scan that are not Operations' scripts". None of them is closed.

---

## Texts this chapter retires or replaces in part

By the program's rule, a chapter is merged together with the list of texts it retires, and at the Lock step the replaced texts are deleted or marked as history in the same change. This is that list, as a proposal. **No file named here is changed by this draft.** The owner of each file is the one the chapters annex gives (`docs/development/platform-refactor-program/chapters.md`). The functional map of the program text names functions; it assigns no document and no rule.

| File | Part | Proposed | Why |
|---|---|---|---|
| `docs/operations/serve-moves-and-live-windows.md` | "Terms": the rows Freeze tree / twin trees, The kit, kit.owner claim, Verified rollback | mark as history | Ruling G14 retired the twin trees and the rehearsal with a forced failure. The exits 12 and 40 are now those of `ops/serve-move`. |
| same | "The procedure, step by step", every subsection from "Build the twin trees from one pinned commit" to "Independent read-only verification" | mark as history, as the dated record of serve moves 7, 8 and 9 | Replaced by "Serve a build; return to the previous build" here and by the runbook in bc-infra `ops/README.md`. |
| same | "DB migration applies in this frame" | mark as history | Replaced in part by "The schema comparison" and "Apply a migration" here. Its ledger reading is of 2026-09-30. |
| same | "Rules that must never be broken" | not replaced by this chapter; stays until the chapter of the function that owns it | The chapters annex gives this file to OP and says the rules table should carry forward. This chapter states the rules that a command of Operations now enforces, each in its act's section: a return is reported only when observed; only a recorded grant is authority and its hash is worked out again; a stop stands. The other rows name retired tools, or concern authoring gates, DevHub merges and pull requests. No text assigns those rows to a function. |
| same | "Open points", items 1, 3, 6, 8 and 9 | mark as history | Each concerns the retired procedure or its tooling. |
| same | "Metric go-live windows" | not replaced by this chapter; stays until the chapter of the function that owns it | Not an act of Operations. The functional map gives making a metric active to L6, Metric Contracts and certification, and enabling a metric for a tenant to L10, Tenant onboarding. No text assigns this section to either. |
| same | "Purpose and scope", the paragraph "Words used here" and the definitions of live act and live window | replaced by "Words" here | One place for the words. |
| `docs/development/dev-workstation-mac-mini.md` | Section 3, "Start / stop BareCount on the Mac" | replaced | The act "Start, stop or restart a service" is here, with the script's verbs read from its committed bytes. The section's statement that the two front ends start switched off is no longer true. |
| same | Section 4, "Files on the Mac" and "Settings files" | mark as history | The custody manifest of `ops/host-files` is the list of host files. The statement that the login profile file sets the identity is no longer true: the profile holds the hook block (`ops/secrets-identity check`, today). |
| same | Section 5, "Secrets and AWS access", the items on app secrets and on AWS access | replaced in part | The one route and the identity are "The secrets route check" here. The package registry item is not replaced. |
| same | Section 7, "The database", the item "Taking a copy" | delete | A second way to take a dump beside `ops/backup do take`. |
| same | Section 11, "Open items", item 3 | replaced | Stated under "What is not yet true", section 4. |
| same | Sections 1, 2, 6, 8, 9, 10 and 12, the rest of section 7, and the package registry item of section 5 | not replaced by this chapter; stays until the chapter of the function that owns it | Machines, network, security, the laptop, maintenance, the auditor and records are not acts of the table. The chapters annex gives this file to DV, Development, also OP. The functional map gives DV "DevHub, bc-docs, review, and the rules for working"; it names no function for machines, the network or the laptop. |
| `docs/development/platform-refactor-program/functions-shared-services-operations-development.md` | The dossier of OP | mark as history when Operations is locked | The program says a function's chapter in the guide replaces its dossier when the function is locked. |
| `docs/operations/upgrade-and-migration.md` | whole | already carries a dated banner as history | Named here so that the Lock change confirms it. The chapters annex gives it the verdict "history" and says its clean-slate section needs an explicit ruling; that ruling is not this chapter's. |
| `docs/implementation/data-model-and-schema.md` | "Schema Authority and the Frozen DDL" and "Schema Evolution and Migrations": the seven steps of the path and the states of a migration | replaced in part, by pointing here | The path is stated once, in "The schema comparison, and proving a migration on a restored copy" and "Apply a migration" here. The sections were rewritten to the practice on 2026-11-15 and agree with this chapter. |
| same | Every other section: the two-database model, the ten rules, the naming, the schema groupings, the fact tables, indexes, the type surface | not replaced by this chapter; stays until the chapter of the function that owns it | The chapters annex gives this file to OP, also MD, with the verdict "rewrite". Rules for designing a table are not acts of Operations. No text says which function's chapter takes them. |
| `docs/implementation/infrastructure.md` | "Local Development Infrastructure", with the literal password at line 115 | mark as history; the password is removed whatever else is decided | It gives the frozen folder as the schema-change path and an older container image. The services are "Start, stop or restart a service" here. |
| same | "Defined But Not Deployed", "The `stg` and `prod` Environments", "Deployment Workflow" | replaced in part | "Deploy a cloud unit" here states what is deployed and what is designed and not built. The section on the workflow names a file, `cd-deploy.yml`, that is not in bc-infra today. |
| same | "AWS Account, Region, Profile", "Deployed Baseline", "Not In Infrastructure-As-Code", "bc-ai Local Runtime", "Tenant Database Provisioning", "Hosting Variants" | not replaced by this chapter | The chapters annex gives this file to OP with the verdict "rewrite". The Definition, section 8, asks for a rewrite unit by unit, which is not done and is not this chapter. The sections on a retired service become history in that rewrite. |
| `docs/operations/runtime-runbook.md` | Section 1, "Services" | mark as history | It starts each service by hand from its repository. The supervisor runs them; see "Start, stop or restart a service" here. |
| same | Section 9, "Backup and recovery (`dev`)" | delete | A second way to take a backup, one database at a time. It names a tenant database that the workstation runbook says exists on neither machine. Replaced by "Take a backup" and "Restore a backup to a disposable copy" here. |
| same | Sections 2 to 8, 9b and 10: the nightly cycle, admission, evaluation campaigns, chain status, value audit, tickets, the evidence archive, datasets, the load test, limitations | not replaced by this chapter; stays until the chapter of the function that owns it | The chapters annex gives this file to OP, also RT. These sections are acts of Runtime (RT), Chain integrity (L9), Evidence and lineage (EV) and Notifications (NT) by the functional map's descriptions. No text assigns each section. |
| `docs/operations/operations-overview.md` | "What Operations Means" and "The Eight Chapters That Follow" | replaced | "What Operations is" here, by the Definition. The older text describes Operations as a section of chapters, not as a function, and maps chapters of other functions. |
| same | "Reading Sequence", "Boundaries with Other Sections", "Cross-Cutting Concerns", "Constraints" | not replaced by this chapter | They are rules for writing chapters of the older section. The functional map gives bc-docs to DV. |
| `docs/operations/deployment-topology.md` | "Development Machine Topology" | mark as history | It starts each service by hand and lists two services that `~/bc-stack/process-compose.yaml` does not hold. Replaced by "Start, stop or restart a service" here. |
| same | "Environment Names" | kept | It already states the one list of ruling G13 and is one of the 25 places the environment names check reads. "Words" here agrees with it. |
| same | "The GitHub Actions Surface", "Readiness-Baseline Deployment", "Defined But Not Deployed" | not replaced by this chapter | They are the only description of a deployment. The one written procedure the Definition asks for is not written; see "Deploy a cloud unit". |
| same | "Tenant Database Provisioning", "Per-Hosting-Variant Realization Status" | not replaced by this chapter; stays until the chapter of the function that owns it | By the functional map, provisioning a tenant's database is S3, Tenant lifecycle and management. No text assigns the hosting variants. |

Outside bc-docs, and so outside this list's reach: the local runbook `~/bc-stack/README.md`, which the Definition says is to be produced from the supervisor's file; bc-infra `ops/README.md`, which stays as the commands' own page and loses its opening word "DRAFT" when the design is approved; barecount-devhub `scripts/reference-run/README.md`, whose title and take-copy section are older than the first run and the kept copy; and the project instruction file of the DevHub repository, which ruling G30 makes a pointer to a chapter.

## Sources

- bc-docs at commit `852b3b5cc96da7fef5a0e3419dc30d5ee7988cf2`, which was its main branch when the draft was written. The main branch is now `22357686b8c3010a0e76b228002e1c4fe4fbca0b`, the merge of bc-docs pull request 241; the one file that differs between the two commits is this chapter. Read at `852b3b5c`: `docs/development/platform-refactor-program.md`; the annexes `definition-operations.md` (read whole), `how-the-work-is-done.md`, `rulings.md` and `chapters.md`; `docs/operations/serve-moves-and-live-windows.md`; `docs/development/dev-workstation-mac-mini.md` (sections 3, 4, 5, 7 and 11); the section headings of `docs/implementation/data-model-and-schema.md`, `docs/implementation/infrastructure.md`, `docs/operations/runtime-runbook.md`, `docs/operations/operations-overview.md` and `docs/operations/deployment-topology.md`, and the sections of each that the table above names.
- bc-infra at `origin/main`, commit `18cd69e0e4c4778942c47c4981ab543809057776`: `ops/README.md` (part F of the runbook not read line by line); the head and the verb, exit-code and record sections of each `ops/<command>/README.md`; `ops/host-files/manifest.json`, `ops/host-files/known-entries.json` and `ops/host-files/files/servers.sh`; `README.md`; the file names under `.github/workflows/`.
- barecount-devhub at `origin/main`, commit `6f8498b7b82126d8a8286bd5f903d0a522c70ad0`: `scripts/reference-run/README.md`, the head, "Ports, home and paths", "Work directory", the preflight's lines, "The executor, slice 5" (the command, the exit codes, the record, the dry form) and "The take-copy command"; the file names under `artifacts/serve-move/` and `artifacts/w9-serve-move-4/tools/`.
- bc-db at `origin/main`, commit `ca1aabd18b1d93f6578c12e1aea66a1c7dbea523`: `README.md`; `tools/runner/README.md` and the head of `tools/runner/ROLES.md`; `docs/migrations-awaiting-apply.md`; `docs/dbcp/apply-0070-0071/RUNBOOK-apply-0070-0071.md` and the head of `window-0070-0071.sh`; the file names under `migrations/`, `docs/withdrawn-migrations/` and `tools/backup/`.
- bc-core at `origin/main`, commit `fd4b55ca8090b6ba7b4fb9d992f83fe46fb78bbc`, and at the served commit `ec72438baa2e84a9814f4e39f3f79324e5edf96a`: the file names under `scripts/` only.
- The desk, read 2026-11-18 at 17:19 UTC, `GET http://127.0.0.1:3040/api/grants-list`: the eighteen grants this chapter cites by id, each with its hash worked out again and its `method` read. The texts of four were read whole: the ruling on the secrets condition (`...96f0254f`), the standing grant (`...e925518f`) and the grant of the three installs (`...9533e033`) at the draft's read of 16:55 UTC, and the grant of the retire (`...407d6e2d`) at 17:15 UTC. What this chapter says of the other grants is taken from the program text and the Definition, which quote them. `GET http://127.0.0.1:3040/api/requests`, read at 17:15 UTC, listed no request.
- DevHub's program record, `GET http://127.0.0.1:4000/api/program/status`, read 2026-11-18 at 17:15 UTC: the state of the definition, the conditions of phase 3 with their judgements, the carried conditions and the carried Lock step, and the rows PRG-2e0ba9, PRG-087bea, PRG-4a6fb6, PRG-a770dc, PRG-41c880 and PRG-fec959. A row is what a session recorded; it is not a judgement of the operator.
- DevHub's session record, read the same day from DevHub's own database, read-only: checkpoint 1520 of session SES-7decb4, the Chief's scope call on two folders. It is in no repository.
- Read-only command output of 2026-11-18, on the development machine, from bc-infra at `18cd69e0`, in two readings. The draft's reading, 16:54 to 16:57 UTC, and the second reading, 17:12 to 17:13 UTC, after the retire of 17:10 UTC: `status`, `check` and `verify` of `ops/backup`, `ops/host-files`, `ops/secrets-identity`, `ops/reference-host` and `ops/reference-runtime`; `status` and `check` of `ops/environments`, `ops/secrets-route`, `ops/script-scan` and `ops/schema-compare`; `status` and `verify` of `ops/serve-move`. The results printed in this chapter are those of the second reading. Between the two readings three results changed: those of `ops/host-files` (the retire), the age that `ops/backup check` prints, and the seventh `WRONG` line of `ops/secrets-route check`. No `do`, `retire`, `put-back` or `undo` was run by either reading. `ops/serve-move check`, `ops/schema-compare do`, `servers.sh` and every form of `run.js` were not run.
- Read-only looks at the development machine, the same day. All were made again at the second reading except the calendar entry of the launch agent; of `~/bc-stack/README.md` the second reading read lines 34, 35, 52, 70 and 79 and made a word search. The looks: the text of `~/bc-stack/README.md` (the text of `servers.sh` was read from its committed bytes, which `ops/host-files check` reads as equal to the host's); the service names and the `working_dir` and `disabled` lines of `~/bc-stack/process-compose.yaml`; the names and modes of the files in `~/bc-stack/secrets`, `~/bc-stack/state/schema-compare`, `~/bc-stack/state/host-files`, `~/bc-stack/state/backup`, `~/bc-stack/serve-moves` and `~/.bc-reference-run-disposable/records`; the names of `~/bc-stack/README.md` and its dated copies; `launchctl list`; the calendar entry of the launch agent `com.barecount.pg-backup` (`plutil -p`); `git worktree list` in the shared copy of bc-infra; and the repository variable `CI_RUNNER_MODE` of bc-core and bc-db (`gh variable list`). No file under `~/bc-stack/secrets` and no settings file was opened.
- The reading of 2026-11-19, 00:47 to 00:48 UTC, from the shared copy of bc-infra at `origin/main`, commit `f5cfc291f181f30fccc5f314eb52b6ff573c86bd` (the merge of pull request 87; against `18cd69e0` it changes `ops/README.md`, `ops/backup/README.md`, `ops/host-files/README.md`, `ops/host-files/manifest.json` and `ops/secrets-route/identity-inventory.json`), read-only: `status` and `check` of `ops/backup`; `check` of `ops/host-files` (`64 OK; 6 NOTE; 0 WRONG; 0 COULDNOT`, as before) and of `ops/secrets-route` (6 wrong); `check` of `ops/script-scan`, once with no option and once with `--exclude odoo-move`. No other verb was run again, and no file the scan names was opened. Of bc-infra at that commit only `ops/script-scan/README.md` was read again, for its exit codes and its bound.
- The Chief's triage of the script scan, of 2026-11-19: a file kept outside every repository, which holds no value. It is not citable as a repository source. The classes, the owners, the two true exposures, the count of 140 `FOUND` lines for the folder-by-folder walk of `odoo-move`, and the statement that nothing found is a live credential readable by another local account are taken from it. The counts of the two forms of `check` were read again for this text and agree with it. The triaged list under "The script scan" is drawn from it; its files, rule ids, counts and line numbers were compared with the scan's output of 2026-11-19, 01:08 UTC, except for the 27 clone roots below `odoo-move` that the default run does not reach.
- The auditor's reply on exchange thread gen-fc4135, `docs/RESPONSE-Codex-gen-fc4135-01-p3c5-design-boundary-2026-11-19.md` in bc-external-audit at `origin/main`, commit `0b5d7a5aaff6e4f02321d87f9dec4d7a953a3499`: points 9 and 10.
- The auditor's reply on exchange thread gen-ddcf4d, `docs/RESPONSE-Codex-gen-ddcf4d-01-bcdocs243-g38-scan-landing-2026-11-19.md` in bc-external-audit, added by commit `29c30c967c7e9b2674f266542ed3989325e653a1`: the paragraph "Boundary and required next correction", and the auditor's reading of line 134 of `src/github-app/service.js` at bc-external-audit `694c2de9a6779b16f648c42f7ed91d77bdda0262`.
- The reading of 2026-11-19, 01:08 to 01:09 UTC, from the shared copy of bc-infra at `f5cfc291f181f30fccc5f314eb52b6ff573c86bd`, read-only: `check` of `ops/script-scan`, once with no option and once with `--exclude odoo-move`, each also with `--json`. Both exited 1 and printed the summary lines given under "The script scan". No file the scan names was opened.
- bc-infra pull request 88, read at its head `2312d8f43453ede5081a3c8485dc084ace748318`: `ops/host-files/manifest.json` (twenty entries, each with its bytes in bc-infra) and the paragraphs of `ops/host-files/README.md` on the seven files barecount-devhub held. From a worktree at that head, on 2026-11-19 at 01:10 UTC, `status`, `check` and `verify` of `ops/host-files` were run, read-only: `20 of 20 present with bytes and mode equal to the manifest`; `64 OK; 6 NOTE; 0 WRONG; 0 COULDNOT`; and the closing line of `verify` as given under "Host-file custody".
- The desk, read again on 2026-11-19 at about 00:50 UTC: the grants `2026-11-19T00-23-25-024Z-cfaca707` (the approval of the chapter at `98cd7d3c`; its text read whole) and `2026-11-19T00-38-29-443Z-2788b232` (ruling G38), each with its hash worked out again and `method` `totp`. The text of ruling G38 was read from the Chief's request file, whose `text` hashes to the grant's SHA-256.
- bc-infra at `origin/main`, commit `7e16520d3bfeda1549baa88b27c3bd9dd749210a`, read on 2026-11-19 (the merges of pull requests 88, 89 and 90, in that order, after `f5cfc291`): the table "Commands" of `ops/README.md` and its text "The last resort: restart the supervisor"; `ops/launch-agents/README.md` (whole); `ops/dev-secrets/README.md` (whole) and `ops/dev-secrets/custody.json`; the paragraphs of `ops/host-files/README.md` on the seven files barecount-devhub held. Those texts still speak of barecount-devhub's installer as present "until its follow-up change"; that change is pull request 400 and is merged, so those words are older than the fact.
- barecount-devhub at `origin/main`, commit `5614f134557b51e45251dc666634af9284ec10dc` (the merge of pull request 400), read on 2026-11-19 through git: the file names under `scripts/host/`, `scripts/ops/`, `scripts/`, `artifacts/serve-move/` and `artifacts/w9-serve-move-4/tools/`; the list of files the merge changed; the title and line 1890 of `scripts/reference-run/README.md`. The installer `scripts/host/install-host-agents.sh`, the five host sources, the three secret writers, `scripts/ops/rotate-pg-superuser.mjs`, `scripts/lib/request-file.sh` and `src/lib/request-file.js` are not at that commit. `scripts/ops/check-dev-signin.js`, `scripts/ci-runner-collector.js`, `config/dev-tools.json` and the two helper copies under `artifacts/serve-move/` are.
- The auditor's replies on the four changes of 2026-11-19 and on their design, in bc-external-audit `docs/` at `origin/main`, commit `2b703f5b4b5e8d6a42ca9ba1ad24b681a3e5282c`: `RESPONSE-Codex-gen-fc4135-02-installer-and-ops-design-2026-11-19.md` (ACCEPTED WITH BOUNDARY; its nine points), `RESPONSE-Codex-gen-3e7cd4-01-bcinfra88-seven-files-landing-2026-11-19.md` (ACCEPTED WITH BOUNDARY), `RESPONSE-Codex-gen-9551ac-01-bcinfra89-launch-agents-dev-secrets-2026-11-19.md` (ACCEPTED WITH BOUNDARY), `RESPONSE-Codex-gen-3d04e4-01-devhub400-unit-d-landing-2026-11-19.md` (ACCEPTED WITH BOUNDARY) and `RESPONSE-Codex-gen-c2b172-01-bcinfra90-unit-c-inventory-landing-2026-11-19.md` (ACCEPTED). None reports a read of the host: the replies on gen-fc4135 and gen-3e7cd4 say in words that no live host was verified, and the other three review commits and CI records only. None judges condition P3-C5.
- The fifth reading, of 2026-11-19, 02:18 to 02:20 UTC, from the shared copy of bc-infra at `7e16520d3bfeda1549baa88b27c3bd9dd749210a`, level with its main branch after a fetch, read-only, each with its exit code. Exit 0: `status`, `check` and `verify` of `ops/host-files`, `ops/backup` (and `verify` of the proof record by name), `ops/secrets-identity`, `ops/reference-host` and `ops/reference-runtime`; `status` and `check` of `ops/launch-agents`, `ops/environments` and `ops/schema-compare`; `status` of `ops/secrets-route` and of `ops/script-scan`; `status` and `verify` of `ops/serve-move`. Exit 1: `check` of `ops/secrets-route` (6 wrong) and `check` of `ops/script-scan` in its two forms, each also with `--json`. No `do`, `retire`, `put-back` or `undo` was run. `ops/serve-move check`, `ops/schema-compare do`, `servers.sh`, every form of `run.js` and every script of `ops/dev-secrets` were not run. No file the scan names was opened.
- Read-only looks of 2026-11-19, 02:17 to 02:21 UTC: `git worktree list` and `git status --porcelain` in the shared copy of bc-infra; the main branch of bc-docs (`1b5d44fab8c0037ee49567e9d1f4b7ed74961971`), bc-infra, bc-db (`ca1aabd1`, unmoved), bc-core (`fd4b55ca`, unmoved), barecount-devhub and bc-external-audit after a fetch of each; bc-db `docs/migrations-awaiting-apply.md` at `ca1aabd1`; `launchctl list`; the names of the entries of `~/bc-stack/serve-moves`, `~/bc-stack/reference-runtime` and `~/bc-stack/state/schema-compare`. The desk, DevHub's program record, the supervisor's file, the local runbook, the files of `~/bc-stack/secrets` and the repository variables were not read again; what this chapter says of them is the read of 2026-11-18.
- The Chief's own readings of 2026-11-19, 02:16 to 02:17 UTC, from bc-infra `7e16520d`, as the Chief gave them to the writer of this text: `ops/host-files check` exit 0 and clean, with no `WRONG` and no `COULDNOT`; `ops/launch-agents check` ending `12 ok, 3 note, 0 wrong, 0 could not look`; `ops/secrets-route check` ending 6 wrong, with the six `WRONG` and two `COULDNOT` lines of the table. The fifth reading agrees with each.
