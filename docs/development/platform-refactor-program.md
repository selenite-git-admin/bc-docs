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

> **Status of this document.** It is a draft awaiting the operator's approval. By the documentation's rule a chapter binds only when it is both authoritative and locked [21b]; the Foundation chapters are the one exception, and bind through the Authority Model (decision DEC-e0a8ca). So nothing here binds until it is approved. What approval does is stated under "What the operator is asked to do now".

## Summary

On 2026-11-13 the operator decided to stop the drive to prove metrics on demo data, and to refactor the BareCount platform instead. This document is the record of that program: why it was decided, what will be done, in what order, and how anyone can tell when a part is finished.

The reviews behind the decision found the same pattern in every part of the platform that was read. For each act the platform performs there are several ways to do it. A few small breaks block the obvious way. The documents describe a system that has since changed. And the hand-offs between the platform's parts were never designed. A session — one working conversation of the AI assistant that does the development — therefore reaches a point where no single written path exists, and it invents one or takes a wrong one.

The reviews also read the central mechanisms: the service that resolves business meaning, the generator of a tenant's tables, the trigger that guards a metric's lifecycle, the separation of one tenant's data from another's. Each was found to exist once and to be driven by declarations, not by code written for one case (the dossiers of L5, L6 and RT in the annexes). That is a finding about structure. Whether the platform computes correct values is not proven by anything that exists today, and the program builds the test for it before it changes the engine.

The program does five things.

1. **It works from a functional map of the whole platform:** a list of every function the platform performs, from signing a user in to showing a tenant a number. The list is taken from the platform's own documentation, where a version of it already existed [22]. Every route, table, screen, script and document is assigned to exactly one function.
2. **It designs the hand-offs first.** Where one function hands to another, it writes down what passes across, who acts and what starts the act, before the functions that meet there are changed.
3. **It takes one function at a time through five steps:** define, audit, modify, prove, lock. Each step has an exit that can be checked.
4. **It leaves each function usable like an application:** a small set of commands that are the only way to perform its acts, one chapter in a single developer guide, and a lock that fails the build if a second way appears.
5. **It makes the two things every session depends on trustworthy:** DevHub, the tool that coordinates development, and bc-docs, the documentation.

The program is finished when the eight conditions under "When the program is finished" hold. Until a function is locked, nothing it owns is authored or repaired outside the program.

## What the operator is asked to do now

| # | Act | What it does |
|---|---|---|
| 1 | Approve this document, or say what to change. | Its status becomes `locked`. The decision is recorded as a decision record, whose number is then added here. The holds under "What is parked and what is held" begin to bind. |
| 2 | Approve, at the approval desk, the pin of the program's anchor. | Every session is then shown this program at each turn, in place of the parked drive's goal. |
| 3 | Confirm or correct the five decided rulings, the parts the Chief added to them, and the record of the operator's words (under "The rulings" and in the annex of that name). | They become final. |
| 4 | Rule on the four open rulings listed under "Open, and needed in phase 1". | Phase 1 can then start. |
| 5 | Replace the two credentials that are present in the engine's history on three lines [17a]. | The exposure ends. Deleting the files does not remove them from history. |

## How to read this document

This file is the program. It is meant to be read from start to finish and to stand on its own. Ten annexes hold detail that is looked up when needed; they are listed at the end. Where an annex and this file differ, this file governs and the difference is a defect to be corrected in whichever is wrong.

- **Evidence.** A number in square brackets, such as [9], is a row of the annex "Evidence, Verified at Source". The row gives the measured value and the file and line, the query or the command behind it. A statement marked "not re-checked" was reported by a review and was not re-established at its source.
- **Citations.** A citation written `bc-docs:docs/overview/platform-overview.md:45 @ f4f5edd` names the repository, the file, the line, and the commit that was read.
- **Codes.** A code such as S3, L5 or RT names a function of the platform; the codes are listed under "The functional map". A code such as F2, T3, B1 or G5 names a ruling: F for the frame, T for tenants and delivery, B for the build, G for governance.
- **What was read.** Each repository was read on 2026-11-13 at the copy of its main branch then held on the development machine. The platform database and the DevHub database were read the same day with read-only queries. Tenant databases were not read; every statement about a tenant's own data is therefore marked not re-checked, and phase 3 removes that limit by building the reference run.

## The decision

**Decided by:** the operator, on 2026-11-13. **Recorded by:** the Chief. **DevHub task:** TSK-e5bf83.

The decision was reached in nine steps during one session. In order, the operator: judged that the platform is built but not defined or published, and asked for a deep review, a refactor of what is critical, one developer guide, and a check of every decision record and memory file; set the method of defining, auditing, modifying and locking one part at a time, and said the metric catalog should not have been started before the platform was locked; parked the demo drive and the controller fleet; named DevHub the spine and required it to act and not only show; widened the scope to the whole platform; asked that the services be usable like an application; asked that the code be stabilised; required functional coverage, naming subscription and tenant management and the design of how parts are joined; and required bc-docs to be studied first.

The operator's exact words at each step are in the annex [The Rulings](platform-refactor-program/rulings.md), under "The decision, in the operator's words". They are an attributed record: they were taken from the transcript of the Chief's session of that day (Claude session `49b1f545-76dd-4dcb-bf1f-cf152b36c347`) and from checkpoints 974 to 982 of DevHub session SES-7decb4, and the auditor could not authenticate them independently. The operator confirms them by approving this document.

## The platform in brief

BareCount's documentation states what it is: "BareCount is an enterprise data observation platform." (`bc-docs:docs/overview/platform-overview.md:45 @ f4f5edd`). In plain terms, it reads data from a company's business systems, records what it read, records what that data means in business terms, and records the numbers worked out from it. It keeps each record permanently, and at the moment of each act it writes a record that the act happened, called Evidence.

It exists to prevent three failures (`bc-docs:docs/foundation/the-problem.md:28-34 @ f4f5edd`): the same value coming to mean different things in different places; a past number being explained by re-running old work; and a reference that names a thing without naming its version. Six rules that must never be broken, called invariants, follow from these; they are listed in the annex on terms.

It produces four kinds of record, called objects, in a fixed order: a **Source Object** (what was read from the source system), a **Canonical Object** (its business meaning), a **Metric Snapshot** (a metric's value for a period), and an **Action Object** (a recorded intent tied to a metric's value; designed and not built). Each is produced at exactly one place, called a boundary. How each boundary works is declared in a **contract**: a versioned definition that is never changed once in force.

A **tenant** is one organization on the platform, with its own database. What all tenants share is held in the platform database. The platform database holds four tenant records; one is active, Kaveri, which is the demo tenant [16b].

The platform's thesis is **Integrity Assurance** (decision record DEC-71c027): it guarantees the method by which a number is produced and recorded, and states that the result is only as good as the data supplied. By the operator's ruling F1, metrics are how this recorded state is consumed; they are not positioned as the product.

## Words this document uses

| Word | Meaning here |
|---|---|
| The operator | The owner of BareCount. The operator makes every ruling. |
| Session | One working conversation of the AI assistant that develops the platform. A session keeps nothing from an earlier one except what is written down. |
| The Chief | The one session at a time that coordinates the work and edits this document. |
| Worker | A session opened for one unit of work and closed when it is done. |
| The auditor | Codex, an independent AI reviewer that runs under a separate account. (The documents also use "auditor" for two other things; ruling F9.) |
| DevHub | The tool that coordinates development: it records sessions, tasks, plans and decisions, and shows the state of the repositories. |
| bc-docs | The platform's documentation and, by decision DEC-3395bc, its single source of truth. A unit of it is a chapter. |
| Decision record | A file in bc-docs that records one decision, named DEC- and six characters. Also called an ADR. |
| Memory files | Notes loaded into every session automatically. They are not an authority. |
| The anchor | A short text DevHub shows a session at each turn, naming the current program. |
| The engine | bc-core, the repository that holds the platform's services. |
| Governed | Done only through an act the platform defines, checks and records. |
| Package; Subscription; entitlement | A package is a named set of metrics offered to tenants. A Subscription is the record that a tenant has a package. Entitlement is what the Subscription allows. None of the three is built [16c, 16d]. |
| The demo plane | A separate area of the platform database where, from 2026-10-26, metrics were compared with expected values on demo data. A metric that matched was called "Demoed". "Plane" has other meanings in the documents; ruling F2. |
| Proof record | The record that a metric's value matched an expected value. It is distinct from Evidence. |
| Guard | A test, run automatically on every proposed change, that fails when a rule is broken. |
| Code rules | The checks DevHub's "hotspots" page runs on each file, such as length, duplication and unsafe queries. |
| The frame | The things every function inherits: what the product is, the map, the words, the stitch contracts and the thread. Phase 2 settles it. |
| The hard line | The acts never performed without the operator's recorded approval: a change applied to a database; an act on data that cannot be undone; a change to cloud resources; the writing of a credential. |

**A metric's standing.** bc-docs has a page of approved words, here called the vocabulary page [23a]. It fixes these:

| Word | Meaning |
|---|---|
| Certified | The metric's definition has passed the platform's certification. |
| Released; available | The platform offers the metric; any tenant could have it. |
| Subscribed | The tenant's package includes the metric. |
| Enabled | The metric is produced for that tenant: its tables and bindings exist there. |
| Visible | The tenant's admin has chosen to show it to the tenant's users. |
| Reporting | The metric has at least one accepted value on the tenant's own data. |
| Done | For one metric on one tenant, six conditions: certified and released; enabled by the governed act alone; reporting for a stated period; in agreement with an expected value worked out independently from the same source data, with the agreement written down; seen by a user of the tenant in the portal; and no workaround at any step [23b]. |

The same page retires "onboarded" and "validated" used alone [23c]; this document does not use them.

## What the evidence says

Each item was re-established at its source on 2026-11-13. The annex "Evidence, Verified at Source" gives the full account.

- **The code is unstable.** Of 2,610 engine files DevHub scanned, 731 pass every code rule and 542 share duplicated blocks; the most-changed file in thirty days is the service that resolves business meaning [13].
- **Small breaks block the obvious route.** The route that prepares a tenant's tables for a source matches none of the 19 records it should [9]. DevHub's tool for a metric's lifecycle calls a retired route [10a, 10c]. The served route for creating a tenant refuses by design, and four bc-docs documents and the project instruction file still name it [11a, 11c].
- **Metric work stopped advancing.** Of 463 metric contract versions, 430 date from June and July and none has become active since 2026-09-30 [2a, 2b, 2c]. Four proof records exist, for three metrics [3]. Proof was built by hand for each contract version [4c, 6].
- **bc-docs holds a list of functions and the approved words, and neither was in use** [22, 23a]. No chapter outside Foundation is locked [21a]. Of 13 procedure chapters, two name only, or nearly only, routes and tables that exist today [28].
- **Delivery to a tenant is designed and not built.** The Subscription is defined, every point of enforcement is marked "Not yet wired", and no table exists [25a, 25b, 16d]. The rule in force is decision DEC-c220e4: every active tenant sees every active metric [24a].
- **Chapters stopped being read and kept.** The share of session records citing a chapter fell from 20.7% in May to 0.4% in October, and commits to chapters fell from 107 in September to none in November [29a, 29b].
- **DevHub does not tell the truth today.** Its anchor names the parked drive, its start-of-session text reports figures last written on 2026-07-07, and its index reads a copy of bc-docs 141 commits behind [31, 32c, 33].

## What is parked and what is held

**Parked** means kept as recorded and not worked on. Parked work resumes only by a new ruling after the program.
- The Demoed drive, begun 2026-10-26, and the work in flight under it. Its seven open pull requests are listed in the annex "How the Work Is Done".
- The controller fleet: the method, begun 2026-09-30, of thirteen standing sessions each owning an area.

**Held** means: nothing owned by a function is authored, repaired or removed until that function reaches its Modify step. After that, acts on what it owns are performed only through the function's commands.
- Held with their functions: every metric contract, canonical contract, observation contract and business concept; the existing proof records.
- Not begun during the program: new features in the customer portal, the operator console, the demo-world tooling, the website and the audit application; and any decision record that would redefine "done".

**Continuing:** work on DevHub and bc-docs, which is phase 1.

**Standing rules that remain in force:** the six invariants; no database change without the operator's explicit approval; every commit names its DevHub session; real authentication, with no bypass; no secret in a repository.

**An urgent defect in something held** is repaired only by a ruling of the operator, by the smallest change, and is recorded in this document.

## The functional map

A **function** is one thing the platform does that has inputs, outputs and acts of its own. The **functional map** is the list of all of them. It is assembled from three things bc-docs holds.
- **The list of functions** in `docs/implementation/platform-readiness-program.md`: five shared services (S1 to S5), ten lanes of authoring (L1 to L10, fixed by decisions DEC-ce4314 and DEC-a67bae), and runtime, evidence, tenant self-service and action [22]. That chapter belongs to an earlier program and is marked closed; no current chapter holds a list.
- **The approved words** of the vocabulary page.
- **The coverage rule** of decision DEC-a67bae: every surface has exactly one owner.

Nine functions are added because the dossiers found the platform performs them and the list lacks them. They are marked "added", and join the list in bc-docs if the operator approves (ruling F3).

| Code | Function | What it does |
|---|---|---|
| | **Shared services** | |
| S1 | Authentication | Establishes who a user is |
| S2 | User and access management | Establishes what a user may do |
| S3 | Tenant lifecycle and management | Creates a tenant, provisions its database, moves it through its states, retires it |
| S4 | Pricing and subscription | Defines the packages offered, records which a tenant has, and bills for it |
| S5 | Operator console | Gives the operator a screen over every other function |
| | **Authoring** | |
| L1 | Source Catalog | Holds the description of a source system's tables and fields |
| L2 | Source and Admission Contracts | Declares what is admitted from a source table |
| L3 | Vocabulary | Holds the registry of business concepts that every contract refers to |
| L4 | Observation Contracts | Ties a source's fields to business concepts |
| L5 | Canonical Contracts | Declares business meaning, the level at which it is recorded, and its versions |
| L6 | Metric Contracts and certification | Declares a metric, certifies it and makes it active |
| L7 | Readers, connectors and connections | Declares how a source system is reached and read |
| L8 | Metric Directory | Holds the list of metrics the platform recognises |
| L9 | Chain integrity | Judges whether everything a metric depends on is in place |
| L10 | Tenant onboarding | Performs the act that makes a metric enabled for a tenant: its tables and bindings |
| | **Runtime and proof** | |
| RT | Runtime | Runs a tenant's data through admission, canonical evaluation and metric evaluation |
| EV | Evidence and lineage | Records that each act happened and what it referred to |
| PV | Proof against the source (added) | Compares a reported value with a value worked out independently |
| | **Delivery** | |
| DL | Delivery to a tenant (added) | Keeps a metric's standing for a tenant (subscribed, visible, reporting) and governs how a new version reaches the tenant |
| TS | Tenant self-service | Gives a tenant's users their screen |
| A1 | Action and intervention | Records an action tied to a metric's value; designed, not built |
| NT | Notifications and webhooks (added) | Sends events out of the platform |
| | **Support** | |
| PR | Privacy and retention (added) | Erases, retains and reports personal data |
| MD | Master data (added) | Holds reference data the other functions use |
| AI | AI services (added) | Runs the AI panels that propose and check authored content |
| SU | Support (added) | Handles requests for help |
| | **Running the platform** | |
| OP | Operations (added) | Environments, serving the engine, secrets, schema change, backup. It has no application today: its acts are performed with scripts kept in a folder that is in no repository |
| DV | Development (added) | DevHub, bc-docs, review, and the rules for working |

**The coverage rule.** A **surface** is anything a person or a program can act through or read: a route, a service, a script, a command, a table, a screen, a document. Every surface belongs to exactly one function. A surface deliberately outside every function is entered in a register with one line saying why. A dead surface is entered in a retirement list and deleted in its function's Modify step. A surface that seems to serve two functions means responsibility must be split. The assignment, the register and the retirement list do not exist yet; DevHub will hold them, and that is part of phase 1's exit.

**The applications.** The engine (bc-core) is shared: every function has code in it, and each of its surfaces has one owning function. Four other applications each belong to one function: the operator console (bc-admin), S5; the customer portal (bc-portal), TS; DevHub, DV; and the approval desk (bc-exchange), DV. Operations has none. The scripts that start the services, check their health, serve a new build of the engine and reach the demo source system are kept in the folder `~/bc-stack` on the development machine, which is not a repository (`command: git -C ~/bc-stack rev-parse --is-inside-work-tree -> "fatal: not a git repository"`, 2026-11-14), so they have no history, no review and no test. Whether Operations gets an application of its own is ruling G35.

**Who owns a function.** For the length of the program the Chief owns every function, and the operator decides. Naming a standing owner for each function is ruling G34.

The annex "The Functions in Brief" gives each function's state today, its main defects and what "locked" will mean for it. Each function also has a full dossier.

## The hand-offs between functions

The dossiers list, for each function, what it receives and hands on, and mark many hand-offs as named in bc-docs and never defined. A place where one function hands to another is a **stitch point**, and the written agreement for it is a **stitch contract**. The undefined hand-offs reduce to twelve stitch contracts. Each states: which functions meet; what passes across, in which record; who acts; what starts the act; which version is used; what happens when the act fails; and what each side may assume. A stitch contract is changed only by a new ruling, made before the functions it joins are locked. The Chief writes them in phase 2 and the operator approves each. The functions that meet at a stitch point are not modified before its contract is approved.

| # | Stitch point | Between | What is undecided |
|---|---|---|---|
| 1 | What starts each boundary act | L7, RT | Who supplies the period, and what links canonical evaluation to metric evaluation |
| 2 | Which version an act uses | L5, L6, RT, DL | How the resolver reads the version a tenant adopted; what a "new version" is for a metric contract |
| 3 | A contract version becoming active | L5, L6, L10 | Today a binding is added for each bound tenant automatically and the old one is never ended |
| 4 | The set of metrics that can be offered | L6, L8, S4 | "Released" has no record behind it |
| 5 | What a metric version requires | L6, L9, L10 | Its sources and contracts are inferred each time, not declared |
| 6 | From subscribed to enabled | S4, DL, L10 | Three chapters assume three different acts [26] |
| 7 | From enabled to visible to reporting | DL, RT, TS | What a tenant is told when a metric is not reporting |
| 8 | From certified to released, and where proof sits | L6, PV, DL | Proof is produced apart from the metric and joined to it by a separate record |
| 9 | From a snapshot to an action | RT, A1 | Designed and not built; recorded so RT is not locked against it |
| 10 | A version being superseded | L5, L6, DL | Nothing ends the period in which two versions are both in force |
| 11 | A tenant's first user, and a tenant's end | S1, S2, S3, PR | Nothing links creating a tenant to creating its admin; what is kept and erased at the end is undesigned |
| 12 | A change in the platform reaching the guide | DV, all | Nothing connects a merged change to its chapter |

The facts behind each row are in the dossiers of the functions named. One difference between two dossiers is open: for stitch point 3 they disagree on the moment the tenant binding is written. The Chief settles it in phase 2 by reading the code.

## The thread

The thread is one tenant and one metric, followed from the metric being available to a user of the tenant seeing its value. It is the program's running test that the parts join. From phase 4 on, a function's Prove step includes walking its own part of the thread.

The tenant is Kaveri. The metric is chosen in phase 2 from the reference set described under "The method". The list of the thread's steps, with the function that owns each and whether it can be performed today, is written in phase 2 and is one of that phase's exits. By ruling T2, what the thread needs and does not exist is built inside the program; nothing else of subscription is.

## The method

Each function passes five steps in order. The Chief judges each exit and reports it to the operator.

| Step | What is done | The exit |
|---|---|---|
| **Define** | The governing chapters of bc-docs are read first. The function's logic, acts and states are written in plain terms, consistent with the stitch contracts. Open questions go to the operator. | The operator has approved the definition. |
| **Audit** | Every surface that touches the function is listed in DevHub and marked: the one path, a duplicate, or dead. The code-rule findings for its files are sorted into defects and noise. | The list names the commit of each repository it was taken from. Every route, table and script that DevHub's scans attribute to the function at that commit has an owner and a mark, and each surface left deliberately unassigned is named with its reason. |
| **Modify** | Breaks are repaired. Duplicates and dead code are deleted. Values written into code move into declarations. The function's commands are built. | Automatic checks pass, and the reference run gives the same values as before. |
| **Prove** | A worker that took no part in the work, started with memory files switched off, is given only the chapter and the commands. It performs the function's acts and its part of the thread. | It succeeds with no ruling and no change to code; its transcript is kept. |
| **Lock** | The four parts of the lock are put in place: a guard that fails when a second way to perform an act appears; a guard that the function's files pass the code rules; a test of its commands against a real database; and its chapter merged and marked locked, with the texts it replaces retired in the same change. | All four exist, and the replaced texts are deleted or marked as history. |

Rules that hold throughout: read the governing chapters before designing; one path for each act; no new capability, except what ruling T2 allows; a rule that matters becomes a guard; what others stand on is locked first.

**Commands.** A function's commands are part of the engine's own code. Each has four verbs: **status** (where this stands and what is required next), **check** (would the act be refused, and why), **do** (the act), **verify** (did it take effect, and what shows it). A session, the operator console and DevHub all use the same commands, and the other ways in are deleted.

**The reference run.** Before the engine is changed, one command must exist that evaluates a fixed set of metrics on a fixed copy of the databases and fails on any difference from recorded values. The proposed set is thirteen metrics (not re-checked; proposed in the annex "How the Work Is Done"). Phase 3 builds it. Its first run shows whether today's engine reproduces the recorded values; that is not known.

**The hold on the engine is enforced, not only stated.** From phase 1, an automatic check on the engine's repository refuses any change to the files that produce values (the services of admission, canonical evaluation and metric evaluation, and the migrations they depend on) unless the operator has recorded an exception for that change. From the end of phase 3, the same check instead requires that the reference run has passed on the exact commit proposed. A passing reference run shows that values have not moved; it does not show that they are correct. Correctness is tested only by comparison with a value worked out independently, which is part of "done" and of the finish test.

**The first three phases are preparation,** and the method applies to them in part. Phase 1 changes DevHub and bc-docs, not the engine, so the reference run and the thread do not apply to it; its exit is the list in "The order of work", and Development is locked only in phase 12. Phase 2 produces rulings and contracts, not code. Phase 3 follows the method except that it builds the reference run it will later be checked by. From phase 4 on the method applies in full.

**Stabilising the code.** The count of failures of each code rule in the engine is recorded as a baseline that may only shrink. Dead code is deleted before anything is repaired. Files are repaired one function at a time, never in one sweep.

**Decision records and memory files.** The operator's instruction is to check each one. bc-docs holds 659 decision records [8f] and there are 396 memory files [30]; a first sorting of both is in the evidence of this program. When a function is locked, each record and file that touches it is checked against the function's chapter and is folded into it, marked as history, or deleted. DevHub keeps the count of those checked and those remaining. Phase 12 ends when none remains.

A worked example, and each of these subjects in full, is in the annex "How the Work Is Done".

## The order of work

The order is fixed. A phase begins when the one before it has met its exit.

| Phase | Functions | The exit |
|---|---|---|
| 1 | DV: DevHub and bc-docs | DevHub's start-of-session text states only what is true. The anchor is pinned to this program. DevHub holds the program's plan, its rulings, and the assignment of surfaces with the register and the retirement list. The backlog is swept (ruling G2). DevHub records the chapters consulted when a plan is saved and when a session is closed. The code-rule baseline for the engine is enforced automatically. The check that holds changes to the engine's value-producing files is in force. DevHub's dead tools are stopped (ruling G3). |
| 2 | The frame | The operator has approved: the statement of what the product is (F1); the definition of "done" (F2); the map (F3); the twelve stitch contracts; the thread's metric and steps; and rulings F4 to F9, T6, B6 and B7. |
| 3 | OP: Operations | One list of environment names is approved and in use. One written procedure serves the engine and has been followed once. Secrets are loaded one way. The schema-change path is written as practised. Operations' scripts have been checked for secrets, are in a repository, and its acts are performed by commands that have been run once, including the return to the previous build of the engine. The reference run has passed once, and this document records the hash of the database copy, the engine commit, where each expected value came from, and the result. The check on the engine requires the reference run from then on. Rulings G12 to G15 and G35 are made. |
| 4 | S1, S2, S3 | Each function is locked. |
| 5 | L1, L2, L7 | Each is locked; a source table can be registered and read by commands alone. |
| 6 | AI, L3, L4 | Each is locked. |
| 7 | L5, L6, L8, L9 | Each is locked; the resolver reads the version a tenant adopted. |
| 8 | RT, EV, PV | Each is locked; an expected value is compared by a declared procedure, with no code written for one contract version. |
| 9 | L10, DL, S4 | Each is locked; every step of the thread listed in phase 2 can be performed by commands; and the thread is walked with the same choice of adopted version that was used to meet phase 7's exit, so that the resolver and delivery are shown to agree. |
| 10 | TS, S5, NT | Each is locked; a user of the tenant sees the thread's value; the console performs every act through commands. |
| 11 | PR, MD, SU, A1 | Each is locked, or is on the operator-approved list "designed and not built" and is described as such in the guide. |
| 12 | DV: the rules for working | The rules for sessions, review and approvals are one locked chapter. No decision record or memory file remains unchecked. |

Durations are not given, because none can be estimated honestly before one function has passed through the method. After phase 3 the Chief amends this document with measured durations.

**Reporting.** At each exit, and at least weekly, the Chief reports to the operator the count of functions at each step and the count of open rulings.

**If an exit cannot be met,** the Chief stops and puts the choice to the operator: change the exit, change the order, or end the program. A locked function is reopened only by a ruling.

**Deployment to the cloud is outside the order.** It is not built, and no function needs it to be locked on the development machine.

## The rulings

A ruling is a decision that belongs to the operator. It is recorded in this document, and DevHub keeps it as a decision. The full register is the annex "The Rulings".

### Decided

| # | The operator's words (2026-11-13) | The ruling | What the Chief added, to be confirmed |
|---|---|---|---|
| F1 | "I do not want to position 'metrics' as product." | Metrics are not positioned as the product. | The statement of what the product is; written in phase 2. |
| T1 | "There will be subscription 'packages' and metrics will be bound to them. One to many." Asked whether a metric may belong to more than one package: "Yes." | A tenant subscribes to a package. A package holds many metrics. A metric may be in more than one package. | How a package names its metrics is not yet designed (ruling T6). Decision DEC-cf6d3b treats its "Pre Launch Exclusive" package as interim, outside the four tiers of DEC-324d9e, so neither record conflicts with this ruling; a decided record is amended only if the chosen design changes it. |
| T2 | "Agree", to the recommendation "designing it in full and building the minimum the thread needs". | Subscription and entitlement are designed in full; only what the thread needs is built. | The list of what the thread needs; written in phase 2. |
| T3 | "I think a change which will affect value (value affecting change?) should be accepted by tenant admin/designated role/user." And "Agree", to "any change able to move a reported number should never be automatic". | A value-affecting change reaches a tenant only when the tenant's admin, or a role or user the tenant designates, accepts it. | Until it accepts, the tenant stays on the version it adopted. While that version remains compatible with its source and its bindings, it continues to be evaluated. When the adopted version's source or binding becomes incompatible, new evaluation for that tenant is refused, nothing is reported in its place, and the tenant is shown the reason. Values already reported are never altered or worked out again. A change whose effect is uncertain is treated as value-affecting. A change that cannot affect a value is automatic. These additions are the Chief's, not the operator's words. Where they differ from the older policy in `docs/operating-model/source-change-classification.md` [27a, 27d], this ruling takes precedence once confirmed, and that chapter is amended in phase 2. |
| G2 | "Agree", to the sweep of DevHub's backlog. | The review tasks DevHub created itself are aborted, in-progress tasks with no session are returned to parked, and the stale plans are replaced by one. | Done in phase 1 as one recorded act with the list attached. |

### Open, and needed in phase 1

| # | The question | The Chief's recommendation | Phase |
|---|---|---|---|
| G5 | Is DevHub moved to a Postgres database? The operator said there is "no specific pain … just aspiration/fear factor". | Not now. Meet the fear directly: a backup restored once as a test, a record of schema changes, and requests that refuse unknown fields. | 1 |
| G3 | Are DevHub's unused tools and tables retired? (About 35 tools and 27 tables; not re-checked.) | Stop them in phase 1; remove them after one function is locked without them. | 1 |
| G30 | Where do the rules for sessions live: a bc-docs chapter with the project instruction file pointing to it, or the instruction file alone? | The chapter. | 1 |
| G34 | Who is the standing owner of each function after the program? | To be proposed in phase 12; the Chief until then. | 1 |

### Open, and needed in phases 2 and 3

Each is stated in full, with the Chief's recommendation, in the annex "The Rulings". They are put to the operator when their phase begins.

- **Phase 2:** F2, whether the vocabulary page's definition of "done" is adopted as it stands; F3, the map; F4, which of three scales of a metric's progress is kept; F5, when a chapter becomes locked; F6, what Integrity Assurance gives a customer; F7, the website's claims; F8, the word for proof; F9, which of three things keeps the word "auditor"; T6, how a package names its metrics; B6 and B7, what starts canonical evaluation and who supplies the period.
- **Phase 3:** B1, keeping one copy of the databases as the reference run's fixed input; B2, the baseline if the first run does not reproduce the recorded values; G12 to G15, the unapplied migrations, the names of environments, the one serving procedure, and the undeployed cloud resources; G35, which has two parts. The first is decided in phase 3: in which repository Operations' scripts are kept, and which function owns each command. The Chief recommends that they move into a repository as the commands of Operations, which is repair and not new capability. The second part, whether Operations has a screen of its own (a "platform ops" application), is decided with ruling G4 in phase 12; a new screen or a new operating act needs its own ruling.

The rulings needed in later phases, and the questions each dossier raises, are in the same annex. Each is put to the operator in the Define step of the function it belongs to.

## What is not yet known

- Whether today's engine reproduces the values recorded for Kaveri. The first reference run answers it.
- What a tenant database holds. No tenant database was read.
- How long a function takes to pass through the method.
- The thread's metric and steps, and the moment the tenant binding is written (stitch point 3). Phase 2 settles both.
- Several figures reported by reviews and not re-established at source. Each is marked "not re-checked" where it appears.

## The chief risks

| Risk | Its sign | What is done |
|---|---|---|
| The refactor becomes another loop. | A phase with no locked function. | Every step has an exit; the count of locked functions is reported. |
| Scope grows. | Work that belongs to no function and step. | The anchor requires each act to name its function and step. |
| A change to the engine alters a value unnoticed. | The reference run fails. | No engine change before the reference run exists. |
| Delivery to a tenant is again left for later. | Phase 5 begins without stitch contracts 2 and 6. | The contracts are an exit of phase 2. |
| The program depends on one Chief session and one operator. | Work waits on either. | The state is in DevHub and this document, not in a session; rulings are grouped by phase; ruling G1 will reduce approvals. |

The full list is in the annex "How the Work Is Done".

## When the program is finished

This section is the definition of done for the program. The program is finished when all eight conditions hold. Each can be checked by a third person. The Chief reports each with its evidence, and the operator confirms the whole.

1. **Every function is locked.** All 28 functions of the map are locked, except what is on a closed list, "designed and not built", that the operator has approved by name. An entry on the list is a whole function or a named part of one. Today the list would hold the function Action and intervention, and one named part of Pricing and subscription: billing and the tiers, which the thread does not need.
2. **Every hand-off is agreed and tested.** All twelve stitch contracts are approved, and each has at least one test that fails when the contract is broken.
3. **The finish test has passed.** A worker that did not build the platform, using only the guide and the commands, takes one metric from a source table not used before to "done" for a tenant; then a second metric of a different shape; then one business concept; with no change to code and no ruling. The operator names the two metric shapes in phase 2. The transcript of the run is kept.
4. **The route is proven on the operator's four conditions,** each marked met with its evidence: it used the mandated route alone; it repeats from a clean start by the written procedure alone, in a session that did not build it; each part and each hand-off has tests that can fail, kept and re-run; and a second, different case passes with no change to any part [23b].
5. **There is one guide.** `docs/guide/` has a locked chapter for each locked function, and each of the 124 chapters that exist today [21a] has been kept, rewritten or retired.
6. **Every decision record and memory file has been checked.** DevHub's count of those remaining is zero.
7. **Values are held and the code is clean where it is locked.** The reference run passes on the final commit of the engine, and the files of every locked function have no failure of a code rule.
8. **DevHub tells the truth.** Its start-of-session text, its anchor and its scans have each been compared with their sources and found to agree.

Condition 3 rests on "done", which requires agreement with an expected value worked out independently. What counts as independent is ruling B5, which must be made before phase 8.

## Annexes

The annexes are part of this document. All are in the folder `platform-refactor-program/` beside this file.

| Annex | What it holds |
|---|---|
| [The Platform in Brief, and Terms](platform-refactor-program/terms.md) | The longer account of the platform, the six invariants, every term defined |
| [How the Work Is Done](platform-refactor-program/how-the-work-is-done.md) | The method with a worked example, commands, locks, the reference run, DevHub, bc-docs, roles, all risks, what happens to what exists, items outside the program |
| [The Rulings](platform-refactor-program/rulings.md) | Every ruling: decided, open, and raised by a dossier |
| [The Functions in Brief](platform-refactor-program/functions-in-brief.md) | A short summary of each of the 28 functions |
| [Function Dossiers: Shared Services, Operations, Development](platform-refactor-program/functions-shared-services-operations-development.md) | The dossiers of S1 to S5, OP and DV |
| [Function Dossiers: The Authoring Lanes](platform-refactor-program/functions-authoring-lanes.md) | The dossiers of L1 to L10 |
| [Function Dossiers: Runtime, Proof, Delivery and Support](platform-refactor-program/functions-runtime-delivery-support.md) | The dossiers of the other eleven functions |
| [Evidence, Verified at Source](platform-refactor-program/evidence.md) | Every numbered row cited in square brackets |
| [The State of Every bc-docs Chapter](platform-refactor-program/chapters.md) | Each chapter, its verdict and its function |
| [Every Repository and Where It Belongs](platform-refactor-program/repositories.md) | Each repository and each directory of the engine, with its function |

A dossier is the detailed record of a function as it stands today. It is used in that function's Define and Audit steps, and the function's chapter in the guide replaces it when the function is locked.
