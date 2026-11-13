---
id: platform-refactor-program
order: 45
title: "Platform Refactor Program"
status: drafting
authority: authoritative
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

# Platform Refactor Program

## Summary

On 2026-11-13 the operator decided to stop the drive to prove metrics on demo data and to refactor the BareCount platform instead. This document is the whole record of that program: why it was decided, what the platform is, what will be done, in what order, and how anyone can tell when a part is finished.

The finding behind the decision is simple. The platform's core works: its engine, its contracts and its isolation of tenant data are sound wherever they were read. What fails is everything around the core. There are many ways to perform the same act, a few small breaks block the obvious way, the documents describe a system that has since changed, and the hand-offs between the platform's parts were never designed. A session that reaches a junction finds no single written path, so it invents one or takes a wrong one. Eight months of work show the result: the definition of a finished metric was replaced about a dozen times (not re-checked; reported in artifacts/spine-review/retrospective-2026-11-13/study-B-objective-churn.md), and one metric today passes all three of the checks the project has used (not re-checked; reported in artifacts/spine-review/retrospective-2026-11-13/study-C-metric-traces.md).

The program does five things.

1. **It works from a functional map of the whole platform.** The map lists every function the platform performs, from signing a user in to delivering a governed number to a tenant. It is taken from the platform's own documentation, where it already existed and had stopped being read. Every route, table, screen, script and document is assigned to exactly one function.
2. **It designs the hand-offs first.** Where one function hands to another, the program writes down what passes across, who acts and what triggers the act, before either side is changed.
3. **It takes one function at a time through five steps:** define, audit, modify, prove, lock. Each step has an exit that can be checked.
4. **It leaves each function usable like an application.** Each function ends with a small set of commands that are the only way to perform its acts, one chapter in a single developer guide, and a guard in continuous integration that fails if a second way appears.
5. **It makes the two things every session depends on trustworthy:** DevHub, the tool that coordinates development, and bc-docs, the documentation. DevHub must tell the truth and be able to act. bc-docs must be read before any design and corrected whenever the platform changes.

The program is finished when a session that did not build the platform can take one metric from a new source to a tenant's screen, using only the guide and the commands, with no change to the code and no decision from the operator; and can then do it again for a different kind of metric and for one business concept.

Until then, no metric, contract or vocabulary is authored, and the engine's code changes only through this program.

## How to read this document

This file is the program. It is written to be read from start to finish in about half an hour, and to stand on its own. Ten annexes hold the detail that is looked up when needed; they are listed at the end under "Annexes".

- A term with a special meaning is defined under "Words this document uses". The full list of terms is in the annex [The Platform in Brief, and Terms](platform-refactor-program/terms.md).
- A number in square brackets, such as [9], is a row of the annex [Evidence, Verified at Source](platform-refactor-program/evidence.md). That row gives the measured value and the file and line, the query or the command behind it.
- A code such as S3 or L5 is a function of the platform. The codes are listed under "The functional map".
- Every repository was read at its main branch as last received from GitHub on 2026-11-13. The platform database and the DevHub database were read the same day with read-only queries. Tenant databases were not read. A statement that could not be re-checked says so.

## The decision

**Decided by:** the operator, in the Chief Controller session, on 2026-11-13. **Recorded by:** the Chief, the session that coordinates the project's work. **DevHub task:** TSK-e5bf83.

The decision was reached in steps during one working session. The operator's own words at each step are given here, because the program's shape follows from them.

| # | The operator's words (2026-11-13) | What the program takes from them |
|---|---|---|
| 1 | "I think the spine is built but not clear/well defined/published and each time at each junction we either reinvent or go in wrong direction. May be a deep code/services review (and critical refactoring too) and one SINGLE dev guide (in specific chapters) will solve this issue permanently. … We need to evaluate and fix the framework and make it simple/clear enough to follow. Clear memory (MD) line by line, check and fix ADRs one by one. There is no short cut." | A deep review, a refactor of what is critical, one guide, and a one-by-one check of the decision records and the memory files. |
| 2 | "I am leaning towards refactoring the codebase. It evolved organically needs an deep audit. We will create chapters for each workflow - define the logic, flow, evaluate-modify-lock the code/service. I think before locking the platform completely we should not have started building metric directory/catalog. IMO there is huge duplication and ambiguity which keeps biting us. Without fixing it no new/modified methods will work." | The method: define, audit, modify, lock, one chapter per function. The metric estate is held unchanged until the platform under it is locked. |
| 3 | "Yes, park both and start with step zero. we will create a document about this first." (in answer to parking the demo drive and the controller method) | The park, and this document. |
| 4 | "Note: Devhub is our spine" and, later, "DevHub is mostly read only we need to make it actually functional." | DevHub carries the program and must be able to act, not only show. |
| 5 | "Study DevHub first - look at the bigger picture 'the platform' (metric is core of it but they are not the only candidate)" | The scope is the whole platform. |
| 6 | "let us adjust/modify services so that you can use them like an application to finally onboard metric/business concepts (in platform stabilization/lanes arc we worked on that but could not stick to it)" | Each function ends in commands that are its only door. |
| 7 | "IMO this is time to stabilize the codebase too." | The rules for stabilising the codebase. |
| 8 | "This is mostly operational but the functional side coverage/integrity is missing. … e.g. subscription and tenant management are missing and stitching them later is not considered/designed well enough I guess." | The functional map, complete coverage, and hand-offs designed first. |
| 9 | "Study bc-docs in depth first. IMO last few month we moved away from consulting bc-docs frequently could be a major lap." | bc-docs is read before design, and the program makes that the default. |

Four rulings on substance were also given the same day; they are recorded in full under "The rulings":
- "I do not want to position 'metrics' as product."
- "There will be subscription 'packages' and metrics will be bound to them. One to many."
- "I think a change which will affect value (value affecting change?) should be accepted by tenant admin/designated role/user."
- On moving DevHub's database to Postgres: "There is a no specific pain behind the Postgres idea, just aspiration/fear factor."

## The platform in brief

BareCount's documentation states what it is in one sentence: "BareCount is an enterprise data observation platform." (`bc-docs:docs/overview/platform-overview.md:45 @ f4f5edd`). In plain terms, it reads data from a company's business systems, records what it read, records what that data means in business terms, and records the numbers worked out from it. It keeps each record permanently and writes a proof of each act at the moment of the act.

It exists to prevent three failures named in its Foundation chapters (`bc-docs:docs/foundation/the-problem.md:28-34 @ f4f5edd`): the same value coming to mean different things in different places; a past number being explained by re-running old work; and a reference that names a thing without naming its version.

It produces four kinds of record, called objects, in a fixed order: a **Source Object** (what was read from the source system), a **Canonical Object** (its business meaning), a **Metric Snapshot** (a metric's value for a period), and an **Action Object** (a recorded intent tied to a metric's value; designed, not built). Each is produced at exactly one place, called a boundary, and a proof record is written with it. How each boundary works is declared in a **contract**: a versioned definition, never changed once in force.

A **tenant** is one organization on the platform, with its own database. What all tenants share is held in the platform database. There is one tenant today, Kaveri, which is the demo tenant.

The platform's thesis is **Integrity Assurance** (decision record DEC-71c027): it guarantees the method by which a number is produced and proved, and states that the result is only as good as the data supplied. By the operator's ruling A1, metrics are how this governed state is consumed; they are not positioned as the product.

The longer account, with the six invariants and each kind of contract, is in the annex [The Platform in Brief, and Terms](platform-refactor-program/terms.md).

## Words this document uses

| Word | Meaning here |
|---|---|
| The operator | The owner of BareCount, who makes every ruling. |
| The Chief | The one session that coordinates the project's work and edits this document. |
| The auditor | Codex, an independent reviewer that runs under a separate account. |
| DevHub | The tool that coordinates development: it records sessions, tasks, plans and decisions, and shows the state of the repositories. |
| bc-docs | The platform's documentation and, by decision DEC-3395bc, its single source of truth. A unit of it is a chapter. |
| Decision record (ADR) | A file in bc-docs that records one decision, named DEC- followed by six characters. |
| Memory files | Notes that are loaded into every session automatically. They are not an authority. |
| The anchor | A short text DevHub shows to a session at every turn, naming the current program. |
| The engine | bc-core, the repository that holds the platform's services. |
| The demo plane | A separate area of the platform database where, since 2026-10-26, metrics were proven on demo data. A metric proven there was called "Demoed". |
| Function | One thing the platform does that has an owner, inputs, outputs and acts of its own. |
| Functional map | The list of all functions. |
| Surface | Anything a person or a program can act through or read: a route, a service, a script, a command, a table, a screen, a document. |
| Stitch point; stitch contract | A place where one function hands something to another; the written agreement for it. |
| The thread | One tenant and one metric, followed from offer to a user's screen. |
| Command | The one way to perform a function's act, with four verbs: status, check, do, verify. |
| Lock | What keeps a finished function finished: two guards, a contract test and a locked chapter. |
| Guard | A test in continuous integration that fails when a rule is broken. |
| Reference run | One command that evaluates a fixed set of metrics on fixed input and fails if any result differs from its recorded value. |
| The hard line | The acts never performed without the operator's recorded approval: a change applied to a database, an act on data that cannot be undone, a change to cloud resources, the writing of a credential. |
| Certified, released, available, subscribed, enabled, visible, reporting | The approved words for a metric's standing, from the vocabulary page of bc-docs. The last five are a tenant's ladder: each needs the ones before it. |
| Done | For one metric on one tenant, six conditions from the vocabulary page of bc-docs: it is certified and released; it is enabled for that tenant by the governed act alone; it is reporting for a stated period; its value agrees with an expected value worked out independently from the same source data, and the agreement is written down; a user of the tenant sees the value in the portal; and no workaround was used at any step [23b]. |
| Value-affecting change | A change to a contract that can alter a value already reported or about to be reported to a tenant (ruling T3). |

## What the evidence says

Each statement was re-established at its source on 2026-11-13. The number in square brackets is its row in the evidence annex, where the full account is given.

- **The core is sound and the surroundings are not.** Of 2,610 files scanned in the engine, 731 pass every code rule, and 542 share duplicated blocks with other files [13]. The file changed most often in the last thirty days is the central canonical resolver, with 20 commits [13].
- **Small breaks block the obvious route.** The route that should prepare a tenant's tables for a source matches none of the 19 reader bindings [9]. DevHub's tool for driving a metric calls a route the engine has retired [10a, 10b, 10c]. The served route for creating a tenant refuses by design, and four chapters and the project instruction file still name it [11a, 11b, 11c].
- **Metric work stopped advancing.** The platform holds 463 metric contract versions; 430 were created in June and July, and none has become active since 2026-09-30 [2a, 2b, 2c]. Four proof records exist, for three metrics [3].
- **Proof was built by hand for each contract version.** Sixteen of 67 platform migrations name a table made for one canonical contract version, and the choice of what to prove is written in three code files [4b, 6].
- **bc-docs already holds the functional map.** One chapter lists the platform's functions under the heading "The platform functions — the stable spine" [22]. The vocabulary page holds the tenant's ladder and a six-condition definition of "done", and retires the words "onboarded" and "validated" used alone [23a, 23b, 23c].
- **No chapter binds.** A chapter binds only when it is both authoritative and locked; none of the 124 chapters is locked [21a, 21b]. Two of 13 procedure chapters name mostly routes and tables that exist today [28].
- **Delivery to a tenant is designed and not built.** The Subscription and its entitlement are defined, every enforcement point is marked "Not yet wired", and the database has no table for either [25a, 25b, 16d]. Three chapters each name a different act that puts a metric before a tenant [26].
- **Chapters stopped being read and kept.** The share of session checkpoints and plans that cite a chapter fell from 20.7% in May to 0.4% in October [29a]. Commits touching a chapter fell from 107 in September to none in November [29b]. The project instruction file never told a session to read the governing chapter first [29d].
- **DevHub does not tell the truth today.** Its anchor still names the parked drive [31]. Its start-of-session text reports figures from tables last written on 2026-07-07 [32b, 32c]. Its index of documents reads a copy of bc-docs that is 141 commits behind [29e, 33]. Of its 2,006 open tasks, 992 are review tasks it created itself [8a, 8b].

## What is parked and what is held unchanged

"Parked" means kept exactly as recorded and not worked on. "Held unchanged" means nothing is added, repaired or removed until the function that owns it reaches its own turn in the order of work.

**Parked**
- The Demoed drive: the effort, begun on 2026-10-26, to prove each metric on a separate demo plane and give it the status "Demoed". Its goal file (`barecount-devhub:blueprints/goal.md`) and its pinned anchor (`blueprints/demoed-terminal.md`) become history.
- The work in flight under that drive: the second version of the receivables balance metric ("AR Balance v2") and the second part of the bridge that carries a demo proof into a metric's record.
- The controller fleet: the method, begun on 2026-09-30, of thirteen standing sessions each owning an area, with their inboxes, messages and transfers.

**Held unchanged**
- The metric estate: every metric contract, canonical contract, observation contract and vocabulary entry. None is authored, repaired or certified.
- The proofs and pins that exist. They stay as they are, as history.
- New features in the customer portal, in the operator console's screens for sources, readers, contracts and metrics, in the demo-world tooling, the website and the audit application.
- Decision records that would redefine what "done" means.

**Not parked**
- DevHub and bc-docs, which the program works on first.
- The six Foundation invariants.
- The rule that no database change is made without the operator's explicit approval.
- The rule that every commit names the open DevHub session it belongs to.
- Real authentication; no bypass.
- The rule that secrets never enter a repository.

## The functional map

A **function** is one thing the platform does that has an owner, inputs, outputs and acts of its own. The **functional map** is the list of all of them. It is the program's table of contents and the developer guide's index.

The map is assembled from three things that bc-docs already holds:
- **The function list.** The chapter `docs/implementation/platform-readiness-program.md` has a section headed "The platform functions — the stable spine". It lists five shared services (S1 to S5), ten lanes of authoring (L1 to L10), and four more: runtime, evidence, tenant self-service and action. That chapter is the record of an earlier program and its own status is `closed`; the list is taken from it because no current chapter holds one.
- **The status words and the definition of "done".** The page `docs/reference/vocabulary.md` was approved by the operator in six parts. It fixes one word for each state a metric can be in and says what "done" means.
- **The coverage rule.** The decision record DEC-a67bae gave every surface exactly one owning lane.

Nine functions are added here because the list in bc-docs does not have them and the reviews found that the platform performs them. They are marked "added". They join the list in bc-docs when the operator approves the frame (ruling A3).

| Code | Function | What it does | Group |
|---|---|---|---|
| S1 | Authentication | Establishes who a user is | Shared services |
| S2 | User and access management | Establishes what a user may do | Shared services |
| S3 | Tenant lifecycle and management | Creates a tenant, provisions its database, moves it through its states, retires it | Shared services |
| S4 | Pricing and subscription | Defines what is offered, records what a tenant has subscribed to, and bills for it | Shared services |
| S5 | Operator console | Gives the operator a screen over every other function | Shared services |
| L1 | Source Catalog | Holds the raw description of a source system's tables and fields | Authoring |
| L2 | Source and Admission Contracts | Governs what is admitted from a source table | Authoring |
| L3 | Vocabulary (named "BCF Enrichment" in the bc-docs list) | Holds the business concepts every contract refers to | Authoring |
| L4 | Observation Contracts | Binds a source's fields to business concepts | Authoring |
| L5 | Canonical Contracts | Declares business meaning, its grain and its versions | Authoring |
| L6 | Metric Contracts and certification (named "MCF Metric (+ certification)" in the bc-docs list) | Declares a metric, certifies it and makes it active | Authoring |
| L7 | Readers and connections (named "Reader" in the bc-docs list) | Declares how a source is reached and read | Authoring |
| L8 | Metric Directory | Holds the directory of metrics of record | Authoring |
| L9 | Chain integrity | Judges whether everything a metric depends on is in place | Authoring |
| L10 | Tenant onboarding | Hands what was authored to a tenant | Authoring |
| RT | Runtime | Runs a tenant's data through admission, canonical evaluation and metric evaluation | Runtime and proof |
| EV | Evidence and lineage | Records proof of each act at the moment of the act | Runtime and proof |
| PV | Proof against the source (added) | Compares a reported value with a value worked out independently from the source | Runtime and proof |
| DL | Delivery to a tenant (added) | Takes a metric from available to subscribed, enabled, visible and reporting for one tenant, and governs how a new version reaches that tenant | Delivery |
| TS | Tenant self-service | Gives a tenant's users their screen | Delivery |
| A1 | Action and intervention | Turns a metric's value into a recorded action; designed, not built | Delivery |
| NT | Notifications and webhooks (added) | Sends events out of the platform | Delivery |
| PR | Privacy and retention (added) | Erases, retains and reports personal data as the law requires | Support |
| MD | Master data (added) | Holds reference data the other functions use | Support |
| AI | AI services (added) | Runs the AI panels that propose and check authored content | Support |
| SU | Support (added) | Handles a tenant's requests for help; today it holds only tickets the platform raises itself, and no tenant route exists | Support |
| OP | Operations (added) | Runs the platform: environments, serving, secrets, schema change, backup | Running the platform |
| DV | Development (added) | The tools and rules by which the platform is built: DevHub, bc-docs, review | Running the platform |

**The coverage rule.** Every surface belongs to exactly one function. A **surface** is anything a person or a program can act through or read: a route, a service, a script, a command, a database table, a screen, a document. A surface that is deliberately not part of any function is entered in a register of such things with one line saying why. A surface that is dead is entered in the retirement list and deleted when its function is modified. A surface that seems to serve two functions is a sign that responsibility must be split; it is never assigned twice. DevHub holds the assignment and shows anything unassigned.

**Where the detail is.** The annex [The Functions in Brief](platform-refactor-program/functions-in-brief.md) gives a short summary of each function: its state today, its main defects and what "locked" will mean for it. Each function also has a full dossier in one of the three dossier annexes.

## The hand-offs between functions

A **stitch point** is a place where one function hands something to another. A **stitch contract** is the written agreement for one stitch point. It states five things: which two functions meet; what passes across, in which record and field; who acts; what triggers the act; and what each side may assume about the other.

The readings of bc-docs found more than thirty hand-offs that are named and never defined. Sessions filled those gaps with their own choices, differently each time. The program therefore writes the stitch contracts before any function is modified. They are written in the second phase of work and each is approved by the operator.

The twelve stitch contracts the program must write:

| # | Stitch point | Between | What is undecided today |
|---|---|---|---|
| 1 | What triggers each boundary act | L7, RT | One operations chapter states the intended ways an act is triggered, set against what is built. Nothing states who supplies the period, or what links canonical evaluation to metric evaluation. |
| 2 | Which version an act uses | L5, L6, RT, DL | Foundation says a reference names its version and that resolving to the head version at the time of reading is "not admitted" (`docs/foundation/the-solution.md`); the engine uses the version that is current for everyone. Ruling T3 settles the rule. The contract must state how the resolver reads a tenant's adopted version, and what a new version means for a metric contract, since every metric contract has exactly one version today. |
| 3 | A contract version becoming active | L5, L6, L10 | Making a canonical contract version active adds a binding for each bound tenant automatically and never ends the old one. Ruling T3 requires this to change for any value-affecting change. |
| 4 | The set of metrics that can be offered | L6, L8, S4 | "Released" is a word with no record behind it. Routes that retire a metric contract exist, and nothing ties them to what is offered. |
| 5 | What a metric version requires | L6, L9, L10 | The chains and sources a metric needs are inferred each time, not declared. |
| 6 | From subscribed to enabled | S4, DL, L10 | Three chapters assume three different acts that make a metric available to a tenant. |
| 7 | From enabled to visible to reporting | DL, RT, TS | Nothing says what a tenant is told when a metric is not reporting. |
| 8 | From certified to released, and where proof sits | L6, PV, DL | Proof is produced on a separate plane and joined to the metric's record by a bridge. The bridge holds two rows today, both marked `partial`. |
| 9 | From a snapshot to an action | RT, A1 | Designed and not built. The contract records the design so that RT is not locked against it. |
| 10 | A version being superseded | L5, L6, DL | Nothing ends the period in which two versions are both active: the prior version is given a 48-hour mark and no code completes it. |
| 11 | A tenant's first user, and a tenant's end | S1, S2, S3, PR | bc-docs states, as a design, that a tenant's admin is created when the tenant is created. The built acts are separate and nothing links them. What is retained and erased at a tenant's end is undesigned. |
| 12 | A change in the platform reaching the guide | DV, every function | Nothing connects a merged change to the chapter that describes it. |

In the table, a code such as L7 or RT is a function of the functional map. Each dossier lists the hand-offs of its function in full, under its heading "What it receives and what it hands on". Where the list above and a dossier differ, the dossier is the detailed record and this table is corrected. One difference is known and not yet settled: for stitch point 3, the dossier for L5, Canonical Contracts, says the tenant binding is written when the version is sent for activation, and the dossier for L10, Tenant onboarding, says it is written when the version becomes `active`.

## The thread

The **thread** is one tenant and one metric, followed from the moment the metric is offered to the moment a user of that tenant sees its value. It is the program's running test of integration.

Each function is proven by walking its own part of the thread, so the parts are joined from the first function onward and not only at the end. The thread uses the demo tenant, Kaveri, and one metric from the reference set. The dossier for DL, Delivery to a tenant, lists the acts that take a metric from available to reporting and says whether each is built today. The full list of the thread's steps, with the function that owns each, is written in phase 2 and is one of that phase's exits.

Ruling T2 decides how much is built for the thread: subscription and entitlement are designed in full, and only the minimum the thread needs is built inside the program.

## The method

One function at a time. Each function passes five steps in order. A step is finished only when its exit holds.

| Step | What is done | The exit that must hold |
|---|---|---|
| **Define** | The chapters of bc-docs that govern the function are read first. The function's logic, its acts, its states and its stitch contracts are written in plain terms. Each open question goes to the operator as a ruling. | The operator has approved the written definition. |
| **Audit** | Every surface that touches the function is listed in DevHub and given one of three marks: the one path, a duplicate, or dead. The findings of the code rules for its files are sorted into real defects and noise. | The list is complete. Every surface has one owner and one mark. |
| **Modify** | Breaks are repaired. Duplicates and dead code are deleted. Values written into code move into declarations. The function's commands are built. | Continuous integration passes, and the reference run gives the same numbers as before. |
| **Prove** | A session that took no part in the work is given only the chapter and the commands. It performs the function's acts and walks the function's part of the thread. | It succeeds with no ruling, no change to code and no help from memory files. |
| **Lock** | A guard is added to continuous integration. The chapter is merged and marked locked. The texts it replaces are retired in the same change. | The guard fails when a second path is added. The function's files pass the code rules. The replaced texts are deleted or marked as history. |
Six rules hold throughout: read the governing chapters before designing; one path for each act; no new capability, except what ruling T2 allows; a chapter is merged together with the list of texts it retires; a rule that matters becomes a guard; and what others stand on is locked first.

A worked example, on creating a tenant, is in the annex [How the Work Is Done](platform-refactor-program/how-the-work-is-done.md).

## How the work is done, in brief

Each of these is set out in full in the annex [How the Work Is Done](platform-refactor-program/how-the-work-is-done.md).

- **Commands.** Each function ends with a small set of commands that are the only way to perform its acts. Every command has four verbs: status, check, do and verify. The commands are part of the engine's own code, so a change that breaks them fails continuous integration. A session, the operator console and DevHub all use the same commands.
- **Locks.** A finished function is held by four things: a guard that fails when a second way in appears; a guard that its files pass the code rules; a test of its commands against a real database; and its chapter marked locked. A lock is opened only by a ruling.
- **Stabilising the codebase.** The count of failures of each code rule is recorded as a baseline that may only shrink. Dead code is deleted before anything is repaired. Files are repaired function by function, never in one sweep.
- **The reference run.** Before any change to the engine, one command must exist that evaluates a fixed set of metrics on fixed input and fails on any difference from the recorded values.
- **DevHub.** Every DevHub screen must show the true state, offer the act that fixes a problem, or remove the problem's cause. DevHub holds the program's plan, rulings and the list of surfaces. It stays on its present database (ruling G5).
- **bc-docs.** Reading the governing chapter becomes part of the procedure: DevHub records the chapters consulted when a plan is saved and when a session is closed, and a decision record does not merge without its chapter. The program's lasting product is one new section, `docs/guide/`, with a chapter for each function.
- **Who does what.** The operator rules and approves. The Chief sets the order of units and edits this document. A worker performs one step for one function. The auditor reviews changes to the engine and to migrations.
- **Risks.** The chief risks are that the refactor itself becomes a loop, that scope grows, and that delivery to a tenant is again left for later. Each has a named sign and a named counter-measure in the annex.

## The order of work

The order is fixed. A phase begins when the phase before it has met its exit, except where the table says two may overlap. Each function inside a phase follows the method.

| Phase | Functions | Purpose | Exit |
|---|---|---|---|
| 1 | Development (DevHub and bc-docs) | Make the two things every session depends on trustworthy. | DevHub's start-of-session output states only what is true today. The anchor is pinned to this program. The program's plan, tasks, rulings and inventory are in DevHub. The backlog sweep (ruling G2) is done. Chapters consulted are recorded at plan and close. The code-rule baseline is in continuous integration. |
| 2 | The frame | Settle what everything else inherits. No code. | The operator has approved: the statement of what the product is; the functional map; the additions to the vocabulary; the twelve stitch contracts; the thread. |
| 3 | Operations | Give the work a floor to stand on. | One set of names for environments. One procedure to serve the engine. One way secrets are loaded. The schema-change path written as it is. The reference run exists and has passed once. The full lock of Operations, which its dossier also ties to a restore of a backup proven on a schedule, a ledger row for every migration and read-only logins for sessions, may finish later. |
| 4 | Authentication; User and access management; Tenant lifecycle | Fix who may act and what a tenant is. | Each function locked. |
| 5 | Source Catalog; Source and Admission Contracts; Readers and connections | The way in from a source system. | Each function locked; a source table can be registered and read by commands alone. |
| 6 | AI services; Vocabulary; Observation Contracts | Business concepts and their binding to source fields. | Each function locked. |
| 7 | Canonical Contracts; Metric Contracts and certification; Metric Directory; Chain integrity | Meaning, metrics and their lifecycle. | Each function locked; the resolver reads a tenant's adopted version (stitch contract 2). |
| 8 | Runtime; Evidence and lineage; Proof against the source | Running the chain and proving its result. | Each function locked; the proof of a value is produced by a declared procedure with no code written for one contract version. |
| 9 | Tenant onboarding; Delivery to a tenant; Pricing and subscription | From authored to a tenant's own data. | The thread can be walked end to end by commands. Subscription is built as far as ruling T2 allows. |
| 10 | Tenant self-service; Operator console; Notifications | The screens. | A tenant user sees the thread's value; the console performs every act through the commands. |
| 11 | Privacy and retention; Master data; Support; Action and intervention | The remaining functions. | Each locked, or recorded as designed and not built. |
| 12 | Development (the method) | The rules for working, in their final form. | The session rules, review and approvals are one chapter; the remaining decision records and memory files have been checked. |

Notes on the order:
- **Delivery to a tenant is designed in phase 2 and built in phase 9.** Its stitch contracts bind phases 5 to 8.
- **Deployment to the cloud is outside the order.** It is not built, and no function needs it to be locked on the development machine. The dossier for OP, Operations, records what exists: of six stack definitions, three are deployed [19].
- **Durations are not given.** They cannot be estimated honestly before the first function has passed through the method once. After phase 3 this document is amended with measured durations.

## The rulings

A **ruling** is a decision that belongs to the operator. Each is recorded here when made and is then written into the guide.

### Decided

| # | Subject | The ruling | Date |
|---|---|---|---|
| A1 | What the product is | Metrics are not positioned as the product. bc-docs states that BareCount is "an enterprise data observation platform", and the adopted thesis is Integrity Assurance (DEC-71c027). Metrics are how governed state is consumed. The exact statement is written in phase 2 and confirmed by the operator. Texts that position metrics as the product are corrected. | 2026-11-13 |
| T1 | What a tenant subscribes to | A tenant subscribes to a package. Metrics are bound to packages: one package holds many metrics, and a metric may be in more than one package. | 2026-11-13 |
| T2 | How much of subscription is built in the program | It is designed in full. Only the minimum the thread needs is built. | 2026-11-13 |
| T3 | How a new version reaches a tenant | A change that can affect a reported value reaches a tenant only when the tenant's admin, or a role or user the tenant designates, accepts it. Until then the tenant stays on the version it adopted and continues to report on it. A change that cannot affect a value reaches bound tenants automatically. A change whose effect is uncertain is treated as value-affecting. Values already reported are never worked out again. | 2026-11-13 |
| G2 | The DevHub backlog | Abort the automatically created review tasks, return to "parked" the in-progress tasks that have no session, and replace the stale plans with one. Done in phase 1 as one recorded act in DevHub with the list attached. | 2026-11-13 |
| G5 | Moving DevHub to Postgres | Not now. It is reconsidered if contention for the database is measured or DevHub must be reached from another machine. | 2026-11-13 |

### Open, and needed first

| # | Subject | The question | The Chief's recommendation | Needed by |
|---|---|---|---|---|
| A2 | The definition of "done" | Is section 5 of the vocabulary page adopted as it stands? | Yes. Add the missing words through that page: plane, package, value-affecting change. | Phase 2 |
| A3 | The functional map | Is the map above, with its nine additions, the platform's list of functions? | Yes; amend the chapter in bc-docs to match. | Phase 2 |
| A4 | The scale of a metric's progress | Three scales exist (three tiers, a ladder of 25 rungs, the lanes). Which is kept? | The vocabulary's status words; the others become history. | Phase 2 |
| A5 | What makes a chapter binding | No chapter is locked today. | A chapter is locked when its function is locked. | Phase 2 |
| A6 | What Integrity Assurance gives a customer, and who "the auditor" is | Three different things carry the word "auditor". | Proposed in phase 2. | Phase 2 |
| A7 | Public claims | The website states counts and badges the platform does not have. | Correct them; the operator decides the wording. | Phase 2 |
| T6 | How a package names its metrics | By a list, or by function and subfunction? The package table that exists today lists readers, not metrics, and has no row for the interim package that DEC-cf6d3b names. | Proposed in phase 2. | Phase 2 |
| B1 | The fixed input of the reference run | May one copy of the databases be kept outside the repositories? It holds demo-tenant data and password verifiers. | Yes. | Phase 3 |
| B2 | The baseline | If the first reference run does not reproduce the recorded values, which state of the contracts is the baseline? | Decide on the evidence of the first run. | Phase 3 |
| G3 | Retiring dead DevHub tools and tables | About 35 of DevHub's 110 tools and about 27 of its 66 tables (the two "about" figures are not re-checked; reported in artifacts/spine-review/DEVHUB-2-as-platform-spine.md). | Stop them first; remove them after one function has been locked without them. | Phase 1 |

The remaining open rulings of the program, and the open questions raised by each function's dossier, are in the annex [The Rulings](platform-refactor-program/rulings.md). Each is put to the operator in the Define step of the function it belongs to.

## When the program is finished

The vocabulary page states when the way metrics are produced is "proven", in four conditions set by the operator: it used the mandated route alone; it repeats from a clean start by the written procedure alone, in a session that did not build it; each part and each hand-off has its own tests that can fail, kept and re-run; and a second, different case passes with no change to any part (VOC:245; quoted in full in the evidence annex under "Quotations").

The program is finished when those four conditions hold for the whole functional map. Concretely: a session that did not build the platform, using only the guide and the commands, takes one metric from a new source table to "done" for a tenant; then a second metric of a different kind; then one business concept; and every function is locked or recorded as designed and not built.

## Annexes

The annexes are part of this document.

| Annex | What it holds |
|---|---|
| [The Platform in Brief, and Terms](platform-refactor-program/terms.md) | The longer account of the platform, every term defined, and the keys used in citations |
| [How the Work Is Done](platform-refactor-program/how-the-work-is-done.md) | The method with a worked example, commands, locks, the reference run, DevHub, bc-docs, roles, risks, and items outside the program |
| [The Rulings](platform-refactor-program/rulings.md) | Every ruling: decided, open, and raised by a function's dossier |
| [The Functions in Brief](platform-refactor-program/functions-in-brief.md) | One short summary of each of the 28 functions |
| [Function Dossiers: Shared Services, Operations, Development](platform-refactor-program/functions-shared-services-operations-development.md) | The full dossier of S1 to S5, Operations and Development |
| [Function Dossiers: The Authoring Lanes](platform-refactor-program/functions-authoring-lanes.md) | The full dossier of L1 to L10 |
| [Function Dossiers: Runtime, Proof, Delivery and Support](platform-refactor-program/functions-runtime-delivery-support.md) | The full dossier of the remaining eleven functions |
| [Evidence, Verified at Source](platform-refactor-program/evidence.md) | Every factual claim with its measured value and its citation |
| [The State of Every bc-docs Chapter](platform-refactor-program/chapters.md) | Each chapter with its verdict and the function it belongs to |
| [Every Repository and Where It Belongs](platform-refactor-program/repositories.md) | Each repository and each directory of the engine, with the function that owns it |

A function's dossier is working material. It is opened when the function reaches its Define and Audit steps, and it is replaced by the function's chapter in the guide when the function is locked.
