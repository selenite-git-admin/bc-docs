---
id: platform-refactor-program-how
order: 45.06
title: "How the Work Is Done"
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

# How the Work Is Done

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md).

This annex sets out in full how the program works: the method with a worked example, the commands each function ends with, how a lock holds, how the codebase is stabilised, the reference run, what changes in DevHub and in bc-docs, who does what, the risks, what happens to what exists today, how the program document is kept, and the items that lie outside the program. The main document carries a short version of each.

## The method

One function at a time. Each function passes five steps in order. A step is finished only when its exit holds.

| Step | What is done | The exit that must hold |
|---|---|---|
| **Define** | The chapters of bc-docs that govern the function are read first. The function's logic, its acts, its states and its stitch contracts are written in plain terms. Each open question goes to the operator as a ruling. | The operator has approved the written definition. |
| **Audit** | Every surface that touches the function is listed in DevHub and given one of three marks: the one path, a duplicate, or dead. The findings of the code rules for its files are sorted into real defects and noise. | The list is complete. Every surface has one owner and one mark. |
| **Modify** | Breaks are repaired. Duplicates and dead code are deleted. Values written into code move into declarations. The function's commands are built. | Continuous integration passes, and the reference run gives the same numbers as before. |
| **Prove** | A session that took no part in the work is given only the chapter and the commands. It performs the function's acts and walks the function's part of the thread. | It succeeds with no ruling, no change to code and no help from memory files. |
| **Lock** | A guard is added to continuous integration. The chapter is merged and marked locked. The texts it replaces are retired in the same change. | The guard fails when a second path is added. The function's files pass the code rules. The replaced texts are deleted or marked as history. |

Rules that hold throughout:
- **Read before designing.** No unit of work begins until its governing chapters and the earlier work on the same subject have been read. The first draft of this program broke this rule and had to be rewritten.
- **One path for each act.** A second way to do the same thing is a defect.
- **No new capability.** The program removes, repairs and joins. The one exception is ruling T2. Anything designed and not built is listed in the guide as such and stays unbuilt.
- **A chapter is merged together with the list of texts it retires.**
- **A rule that matters becomes a guard.** Written rules were repeated and not followed; rules built into hooks and continuous integration held.
- **What others stand on is locked first.**

### A worked example: creating a tenant

This example shows the five steps on one act of the function Tenant lifecycle and management. The facts are from the dossier for S3; the outcome shown is what the method is expected to produce and is not yet done.

- **Define.** bc-docs is read: the chapters on tenant onboarding, tenancy and binding, and tenant lifecycle and subscription, and the decision record DEC-cf6d3b. The definition states that a tenant is created by one governed act, and that it becomes "tenant active" when an admin has been verified and a Subscription assigned (DEC-cf6d3b). Today the act writes the tenant as `provisioning` and then sets it `active`; neither the admin nor the Subscription is checked. A further state for a tenant whose onboarding is not complete is authored in bc-db migration 0034, which is not applied. The open questions are which route performs the act (ruling T4) and whether that migration is applied or withdrawn (ruling G12); the operator rules.
- **Audit.** Three things that create or claim to create a tenant are found: a served route that refuses every call, a command run by the operator, and a seeding helper that is now used by tests only. Four bc-docs documents and the project instruction file name the route that refuses [11c], and the console's "create tenant" screen calls it. Each is marked: the command is the one path; the route is dead; the helper is not a path for creating a tenant.
- **Modify.** The route that refuses is removed, or kept as a refusal that names the command. The command is exposed through the function's commands. The console screen is repointed. The chapters are corrected.
- **Prove.** A fresh session, given the chapter, creates a throwaway tenant, checks it and retires it.
- **Lock.** A test in continuous integration fails if any new route can write a tenant record. The chapter is marked locked. The older descriptions it replaces are retired.

## Commands: the platform used like an application

Today a governed act is performed by calling several routes in the right order from memory. Taking one metric from a directory entry to the state `active` takes eleven calls across seven controllers (not re-checked; reported in artifacts/spine-review/REVIEW-3-metric-lifecycle.md). The dossier for L6, Metric Contracts and certification, lists nine of those calls, from intake to admission, each in its own controller. The earlier attempt to give sessions a single tool for this kept its own copy of the platform's routes inside DevHub. The copy was last changed on 2026-07-09 (command: `git -C ~/MyProjects/barecount-devhub log -1 --format='%h %cs' origin/main -- src/lib/metric-drive.js src/lib/metric-workflow.js` -> `f810d7e04 2026-07-09`), and the seventh of its eight steps calls a route the platform has since retired [10a, 10c].

Each function therefore ends with a small set of **commands** that are the only way to perform its acts. They are part of the platform's own code, so a change that breaks them fails continuous integration.

Every command offers the same four verbs:

| Verb | What it answers | Changes anything? |
|---|---|---|
| **status** | Where does this thing stand, and what is required next? | No |
| **check** | If I asked for the act now, would it be refused, and why? | No |
| **do** | Perform the governed act. | Yes |
| **verify** | Did the act take effect, and what is the proof? | No |

Rules for commands:
- The platform puts the calls in order. The caller names the act and the thing acted on.
- A refusal states the reason and what would cure it.
- A long act returns at once with a reference that can be asked for its status.
- A session, the operator console and DevHub all use the same commands. DevHub drives them and records the result; it keeps no copy of the platform's routes or states.
- The other ways in are deleted.
- The commands of a function are designed after its Define step, so that they express the decided logic and not today's accidents.

An illustration of the intended shape, for the act of enabling a metric for a tenant (the names are illustrative; the real commands are designed in the function's Define step):

```
enable-metric status  --tenant kaveri --metric <metric id>
  -> subscribed: yes (package "Pre Launch Exclusive")
     enabled: no
     next required: provision 2 tables (canonical object store, snapshot store)

enable-metric check   --tenant kaveri --metric <metric id>
  -> would succeed

enable-metric do      --tenant kaveri --metric <metric id>
  -> accepted; reference 7f3a…

enable-metric verify  --reference 7f3a…
  -> enabled: yes; 2 provisioning commands in state "provisioned"; bindings recorded
```

## How a lock works

A **lock** is what keeps a finished function finished. It has four parts, and all four must be in place.

1. **A guard on doors.** A test in continuous integration lists the entry points that may perform the function's acts. It fails when another appears. bc-core already has this kind of test for retired modules, with a baseline that may only shrink.
2. **A guard on quality.** The function's files pass the code rules shown on DevHub's hotspots page, and the baseline for those files is set to zero failures.
3. **A contract test.** The function's commands are exercised against a real database in continuous integration, so a change that alters their behaviour fails.
4. **A locked chapter.** The chapter's status in bc-docs becomes `locked`. By the documentation's own rule, a chapter binds only when it is both authoritative and locked. A locked chapter changes only together with the code it describes, in the same pull request.

A lock is opened only by a ruling of the operator, recorded as a decision, and closed again by the same four parts.

## Keeping the repositories clean

Ruling G36 (operator, 2026-11-14) adds a clean-up before phase 1 and three standing rules.

**What was measured.** On 2026-11-14 the Chief ran, for each repository under `~/MyProjects`, `git rev-list --count HEAD..origin/main` (commits the shared copy is behind its main branch), `git branch --show-current`, `git status --porcelain | wc -l` (uncommitted and untracked files), `git branch -r | wc -l` (branches on GitHub) and `gh pr list --state open` (open pull requests).

| Repository | Behind main | Current branch | Uncommitted or untracked | Branches on GitHub | Open pull requests |
|---|---|---|---|---|---|
| bc-docs | 141 | main | 24 | 35 | 16 |
| bc-db | 122 | a feature branch | 3 | 61 | 6 |
| barecount-devhub | 0 | main | 152 | 134 | 26 |
| bc-core | 3 | main | 2 | 119 | 8 |
| bc-portal | 36 | main | 0 | 3 | 0 |
| bc-infra | 23 | main | 1 | 1 | 0 |
| bc-demo | 5 | a feature branch | 5 | 6 | 0 |
| bc-admin | 2 | main | 0 | 3 | 0 |

Three services run from a shared copy: DevHub, the operator console (bc-admin) and the customer portal (bc-portal) (`command: grep -n working_dir ~/bc-stack/process-compose.yaml`, 2026-11-14). The engine runs from a frozen worktree of its own. So the customer portal was being served 36 commits behind its main branch. The annex "Every Repository and Where It Belongs" counts 323 worktrees. bc-docs already deletes a branch when its pull request merges (`gh api repos/selenite-git-admin/bc-docs -q .delete_branch_on_merge` returned `true`); the setting was not read for the other repositories.

**Phase 0, in two parts.**
- *Without loss.* Each shared copy that no service runs from is returned to its main branch and brought level with it. A shared copy that a service runs from is not changed by housekeeping: it is brought level only through that service's own serving procedure, with the operator told beforehand, because changing its files changes what is being served. Before that, every untracked file in the copy is compared with main: a file already on main is left to be replaced by it; a file that is not is committed through a pull request or put on the disposal list. bc-docs needs this care most, because its shared copy holds decision records written by earlier sessions and never committed. Deleting a branch on merge is turned on wherever it is off.
- *Disposal, on one list the operator approves.* The Chief draws up a list of every open pull request, branch and worktree with a proposed fate: merge, close with a note that says where the work is recorded, keep with a named owner and next step, or remove. A worktree that serves the engine, or is kept as a frozen build to return to, is never on the list. For each worktree proposed for removal the list states whether it holds uncommitted or untracked content; such content is committed and pushed, or recorded, before the worktree is removed. Nothing is closed or removed before the operator approves the list.

**The standing rules.**
1. A shared copy is a read-only mirror of the main branch. No session commits in it. DevHub shows the lag of every shared copy and offers the act that removes it. It keeps level on a timer only the copies that no service runs from. A copy that a service runs from is brought level by that service's serving procedure and by nothing else, until phase 3 gives each service a copy of its own; from then on every shared copy is kept level by the timer.
2. All work is done in a worktree. When its pull request is merged or closed, the worktree and its branch are removed, but only after it is confirmed that nothing in it would be lost: uncommitted or untracked content is first committed and pushed, or recorded. A worktree that serves the engine, or is kept as a frozen build to return to, is never removed during the program.
3. No pull request stays open without a named owner and a next step. DevHub lists any that do.

**Where the rules are checked.** The Lock step refuses a function that still has an open pull request, or a branch or worktree other than one that serves the engine or is kept as a frozen build. The ninth condition of the definition of done requires the same of the whole platform at the end.

## Stabilising the codebase

The codebase is unstable in two ways. The first is churn: the engine's central file was changed twenty times in thirty days to serve one metric's proof. The park ends that; from now on the engine's code changes only through this program. The second is accumulated debt: duplicated blocks, very long files, queries built by joining text.

The debt is paid in this order and never by a single sweep across the codebase. A sweep would polish code that is about to be deleted, and would change the engine before anything can prove its numbers still match.

1. **Hold the line.** Today's count of failures for each code rule is recorded as a baseline in continuous integration that may only shrink. From then on the codebase cannot get worse.
2. **Delete before repairing.** Code with no caller goes first.
3. **Repair by function.** A function's files must pass the rules before the function can be locked.
4. **Split the very long files inside their own function's Modify step,** when the reference run exists to prove the numbers have not moved.

The counts on the hotspots page guide the work; they are not a target. Each function's Audit step separates real defects from noise for its own files.

## The reference run

The **reference run** is one command that evaluates a fixed set of metrics through the real engine on fixed input, compares each result with a recorded expected value, and fails on any difference. Nothing like it exists today. Without it, a change to the engine could alter a number and nobody would know for weeks.

- **Fixed input.** One copy of the platform database, the Kaveri tenant database and the database roles, taken once, identified by its hash, and restored to a disposable database for each run.
- **Reference set.** Thirteen metrics whose expected values are recorded, covering sums, balances, a trailing window, a ratio and counts; and every value the Kaveri tenant holds today, as a baseline. (The set is a proposal. It is not re-checked, and no annex verifies it; the scouting behind it is in artifacts/spine-review/STEP-0-reference-harness-scouting.md. Tenant databases were not read for this document.)
- **Where it lives.** In the DevHub repository, outside the engine's repository, so that a change to the engine cannot change the thing that checks it.
- **The first run is a qualification.** The contracts have moved since the expected values were recorded. Whether today's engine reproduces them is unknown until the first run.

The reference run is built in the third phase of work. No engine code is modified before it exists and passes. The dossier for OP, Operations, records only that it is not built, and makes it a condition of that function's lock. Its design and its limits are written in the Define step of Operations.

**How the hold on the engine is enforced.** From phase 1, an automatic check on the engine's repository refuses any change to the files that produce values unless the operator has recorded an exception for that change. From the end of phase 3, the check instead requires that the reference run has passed on the exact commit proposed. The exit of phase 3 records the hash of the database copy, the engine commit, where each expected value came from, and the result of the run. A passing reference run shows that values have not moved; it does not show that they are correct. Correctness is tested by comparison with a value worked out independently, which is part of "done" and of the test that ends the program.

## DevHub: observe, act, prevent

DevHub is the tool through which development is coordinated: it records sessions, tasks, plans and decisions, and it shows the state of the repositories. The operator calls it the spine. Today it shows a great deal and can do almost nothing, and part of what it shows is no longer true.

The rule for every DevHub screen and tool from now on:

- **Observe.** Show the true state, with the age of the reading.
- **Act.** Where the state is a problem, offer the act that fixes it on the same screen.
- **Prevent.** Where the problem can be designed out, remove its cause.

A screen that shows a problem and offers none of these is a defect. DevHub acts directly on the development environment: checkouts, scans, services, tasks, plans and the pinned anchor. An act on the platform itself goes through the platform's own commands, which DevHub drives and records.

DevHub also holds the program: one plan; a task for each function and step; each ruling as a decision; and the inventory of surfaces with their owner, mark and lock.

DevHub stays on its present database, SQLite, for the length of the program (ruling G5). The risk of losing its record is met directly: a backup that has been restored once as a test; a ledger of its schema changes; write requests that refuse unknown fields; and a single layer through which the code reaches the database, which keeps a later move possible.

The dossier for DV, Development, sets out what DevHub contains today, its defects and the conditions of its lock. It also records that the DevHub database is outside the nightly backup.

**The program as a record a session can act on.** Today a session is shown the anchor, a short text, and must work out its own position in the program. From phase 1 DevHub holds the program itself: its phases, the function and step in hand, each exit with its conditions, the rulings and the evidence of each completed step. A session reaches it through four verbs. Status returns the current phase, function and step, the conditions of the exit not yet met, the open rulings, the chapters to read and the next act. Check says whether an intended act belongs to the program and whether what it depends on is in place. Do records a completed step with its evidence. Verify compares an exit with its conditions. The anchor then carries only a pointer and the instruction to begin with status. Recording a step does not approve anything: it does not meet an exit, settle a ruling or move the program to its next phase. Status shows apart the evidence a session has recorded, the exits the Chief has judged, and the approvals the operator has given. Verify reports the conditions that are not met and never turns a session's claim into an approval.

## bc-docs: read first, and kept true

bc-docs is the platform's documentation and, by decision DEC-3395bc, its single source of truth. The program found that it had stopped being consulted and stopped being kept current, and that the cause was structural: memory files and the pinned anchor are loaded into every session automatically, a chapter is not, and nothing obliged a session to read a chapter or to correct one. The project instruction file has never contained a step that says to read the governing chapter before working.

The program changes that by mechanism, not by exhortation:

- **At the start of a session** the anchor names bc-docs as the design and points to the map of the guide.
- **When a plan is saved and when a session is closed,** DevHub records which chapters were consulted.
- **A decision record does not merge** without the change to the chapter it affects, in the same pull request. This is the program's intent; open ruling G33 asks the operator to confirm it.
- **A design or ruling written anywhere else** creates a task to move it into a chapter.
- **DevHub's index of documents reads bc-docs at its main branch,** never a local copy.

**The guide.** The program's lasting product is one new section of bc-docs, `docs/guide/`, with one chapter for each function and the functional map as its index. It is the only authority for how the platform is operated. A chapter that is already sound is moved into it nearly as it stands; the chapters annex gives the verdict on each: of 131 chapter files, 25 are "keep nearly as is", 57 "rewrite", 46 "history" and 3 "designed, not built". After a function is locked, each decision record and memory file that touches it is checked against its chapter and is folded in, marked as history, or deleted.

## Who does what

| Role | Who | Decides | Does |
|---|---|---|---|
| The operator | The owner of BareCount | Every ruling; approval of each definition and each chapter; every act under the hard line | Gives approvals at the approval desk; rotates credentials |
| The Chief | One session at a time, carrying the Chief's brief | The order of units inside a phase; when a step's exit holds | Edits this document; opens and closes workers; verifies each claim at source before reporting it |
| A worker | A session opened for one unit of work | Nothing beyond its unit | Performs one step for one function and closes |
| The auditor | Codex, an independent reviewer running under a separate account | Whether a change to engine or migration code may merge | Reviews those changes; its findings are answered before merge |

**The hard line** is the set of acts that are never performed without a recorded approval from the operator: a change applied to a database; an act on data that cannot be undone; a change to cloud resources; and the writing of any credential. During the program the present approval rules stay in force for every other act as well, until ruling G1 is made.

## Risks

| # | Risk | What would show it | What the program does about it |
|---|---|---|---|
| 1 | The refactor becomes another loop: defining and re-defining with nothing locked. | A phase without a locked function after its first function's Define step. | Each step has an exit. The Chief reports the count of locked functions at every checkpoint. No new definition of "done". |
| 2 | Scope grows through "while we are here". | Work that belongs to no function and step. | The anchor requires each act to name its function and step. Anything else is listed for later. |
| 3 | A change to the engine alters a number unnoticed. | The reference run fails. | No engine change before the reference run exists; it runs at every Modify exit. |
| 4 | The guide becomes one more text beside the others. | A merged chapter with no retirement list. | A chapter merges only with its retirement list; the lock requires the replaced texts to be gone. |
| 5 | Delivery to a tenant is again left for later. | Phase 5 begins with stitch contract 2 or 6 unapproved. | The contracts are a phase 2 exit; phase 7 cannot begin without them. |
| 6 | The first reference run does not reproduce the recorded values. | The qualification run fails. | Ruling B2; the baseline is then set from evidence before any change. |
| 7 | DevHub work expands and delays everything. | Phase 1 without its exit after its Define step. | Phase 1 is limited to the items in its exit; the rest of DevHub is phase 12. |
| 8 | Context is lost between sessions, as before. | A session acts against this document. | The pinned anchor points here; the Chief's brief points here; DevHub holds the state. |
| 9 | Approvals for many small acts slow the work. | Waiting time at the approval desk. | Ruling G1; until it is made the present rules stand. |
| 10 | A committed credential is used by someone else. | Unexpected sign-ins or usage. | The operator rotates the two credentials, which sit on three lines [17a]; the files are removed in phase 3. |

## What happens to what exists

| Thing | What happens |
|---|---|
| The pinned anchor of the Demoed drive | Replaced by this program's anchor when the operator approves the pin at the approval desk. |
| `blueprints/goal.md` and `blueprints/demoed-terminal.md` | Kept as history. |
| The Chief's brief | Carries a first block pointing to this document. |
| The other controllers' briefs and the memory files | Unchanged until phase 12, except that each is checked against a chapter when its function is locked. No new program state is written to memory. |
| DevHub's plans and open tasks | Swept under ruling G2 in phase 1. The tasks of the parked drive are already parked with a dated reason. |
| The decision records | Unchanged until their function is locked; then folded in, marked as history, or deleted. |
| Open pull requests of the parked drive | Each is closed or completed in the phase of the function it belongs to. They are listed in "Items outside the program". |
| The evidence of this program | Kept in `barecount-devhub:artifacts/spine-review/`. It is the record of how the program was reached; it is not an authority. |

## How this document is kept

- **One editor.** The Chief edits this document. Anyone else proposes a change to the Chief.
- **A ruling edits this document.** It is never recorded only in a side document, a memory file or a message.
- **Every change is a pull request to bc-docs** and names the DevHub session that made it.
- **The decision itself is recorded as a decision record** in bc-docs, as the decision procedure requires. This document is its full statement.
- **Its status is `drafting` until the operator approves it,** and `locked` once approved. After that it changes only by a ruling.
- **The slim anchor** in `barecount-devhub:blueprints/platform-refactor.md` is a pointer to this document. It is shown to every session once the operator approves its pin; until then DevHub still shows the anchor of the parked drive. Where the two differ, this document governs and the anchor is corrected.

## Items outside the program

- **Committed credentials.** Two credentials are present in bc-core's history on three lines: one account password in two files, and one API key. The account password was replaced by the operator on 2026-11-14; the reset tool reported the change and a sign-in with the stored new value succeeded (seen by the Chief in the terminal output; not re-checked by the auditor). The API key is not confirmed dead: a request the operator made with it was answered with HTTP status 400, and it was not among the keys listed in the operator's provider account. That suggests it is no longer valid and does not establish it. The item stays open until the provider's answer is confirmed to name the key as invalid, or the key is found and deleted. The files are removed in phase 3; deleting them does not remove the values from history.
- **The provisioning worker** must not be run with its readiness pass until the gap described in the dossiers for L5, Canonical Contracts, and L10, Tenant onboarding, is closed, because the pass could make a contract version active that was authored for the demo plane.
- **A standing halt in bc-docs.** The chapter on the metric management system still says that no further metric is to be made active and no further vocabulary authored until a sequence completes. This program's hold replaces it; the text is retired in phase 7.
- **Instructions that are wrong today.** The project instruction file names a demo tenant that does not exist, a tenant route that refuses, a count of schemas that is too low (11 against a measured 22 [16a]), and a naming rule for boolean columns that the data does not follow (not re-checked; reported in artifacts/spine-review/DOCS-3A-implementation.md). They are corrected in phase 1.
- **The documentation reader** is broken on the build now being served. Its repair is not held and is done with the serving procedure in phase 3.
- **Open pull requests of the parked drive.** barecount-devhub 325 and 326; bc-core 1053 and 1054; bc-docs 206, 212 and 214. They are on the disposal list of phase 0.
- **Leftover worktrees, branches and open pull requests.** They are dealt with in phase 0, on a list the operator approves; see "Keeping the repositories clean".
