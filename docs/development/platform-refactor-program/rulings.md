---
id: platform-refactor-program-rulings
order: 45.07
title: "The Rulings"
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

# The Rulings

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md).

## The decision, in the operator's words

The operator's words at each step of the decision of 2026-11-13 are given exactly; an ellipsis marks words left out. They are an attributed record, taken from the transcript of the Chief's session of that day (Claude session `49b1f545-76dd-4dcb-bf1f-cf152b36c347`) and from checkpoints 974 to 982 of DevHub session SES-7decb4. The auditor could not authenticate them independently. The operator confirms them by approving the program.

| # | The operator's words | What the program takes from them |
|---|---|---|
| 1 | "I think the spine is built but not clear/well defined/published and each time at each junction we either reinvent or go in wrong direction. May be a deep code/services review (and critical refactoring too) and one SINGLE dev guide (in specific chapters) will solve this issue permanently. … Clear memory (MD) line by line, check and fix ADRs one by one. There is no short cut." | A deep review; a refactor of what is critical; one guide; a check of every decision record and memory file. |
| 2 | "It evolved organically needs an deep audit. We will create chapters for each workflow - define the logic, flow, evaluate-modify-lock the code/service. I think before locking the platform completely we should not have started building metric directory/catalog. IMO there is huge duplication and ambiguity which keeps biting us." | The method. The hold on the metric estate. |
| 3 | "Yes, park both and start with step zero. we will create a document about this first." | The park of the demo drive and of the controller fleet; this document. |
| 4 | "Note: Devhub is our spine" … "DevHub is mostly read only we need to make it actually functional." | DevHub carries the program and must be able to act. |
| 5 | "Study DevHub first - look at the bigger picture 'the platform' (metric is core of it but they are not the only candidate)" | The scope is the whole platform. |
| 6 | "let us adjust/modify services so that you can use them like an application to finally onboard metric/business concepts" | Each function ends in commands. |
| 7 | "IMO this is time to stabilize the codebase too." | The rules for stabilising the code. |
| 8 | "This is mostly operational but the functional side coverage/integrity is missing. … e.g. subscription and tenant management are missing and stitching them later is not considered/designed well enough I guess." | The functional map; hand-offs designed first. |
| 9 | "Study bc-docs in depth first. IMO last few month we moved away from consulting bc-docs frequently could be a major lap." | bc-docs is read before design. |

## The register

A ruling is a decision that belongs to the operator. This annex is the full register: the rulings already decided, the open rulings of the program as a whole, and the open questions raised by the dossier of each function. The main document carries the decided rulings and the open rulings needed first.

A **ruling** is a decision that belongs to the operator. Each is recorded here when made and is then written into the guide. Rulings are numbered in four series: F for the frame and the product; T for tenants, subscription and delivery; B for the engine, the contracts and proof; G for governance, access, operations and development. "Needed by" names the phase of the order of work that cannot finish without the ruling.

### Decided

| # | Subject | The ruling | Date |
|---|---|---|---|
| F1 | What the product is | Metrics are not positioned as the product. bc-docs states that BareCount is "an enterprise data observation platform", and the adopted thesis is Integrity Assurance (DEC-71c027). Metrics are how governed state is consumed. The exact statement was written in phase 2 and is in the main document under "The platform in brief". Texts that position metrics as the product are corrected. | 2026-11-13; the statement in phase 2 |
| T1 | What a tenant subscribes to | A tenant subscribes to a package. Metrics are bound to packages: one package holds many metrics, and a metric may be in more than one package. | 2026-11-13 |
| T2 | How much of subscription is built in the program | It is designed in full. Only the minimum the thread needs is built. | 2026-11-13 |
| T3 | How a new version reaches a tenant | A change that can affect a reported value reaches a tenant only when the tenant's admin, or a role or user the tenant designates, accepts it (the operator's words). Added by the Chief and confirmed by the operator on 2026-11-14: until it accepts, the tenant stays on the version it adopted; while that version remains compatible with its source and its bindings it continues to be evaluated; when the adopted version's source or binding becomes incompatible, new evaluation for that tenant is refused, nothing is reported in its place, and the tenant is shown the reason; values already reported are never altered or worked out again; a change whose effect is uncertain is treated as value-affecting; a change that cannot affect a value is automatic. This ruling takes precedence over the older policy in `docs/operating-model/source-change-classification.md`, which is amended in phase 2. | 2026-11-13 |
| G2 | The DevHub backlog | Abort the automatically created review tasks, return to "parked" the in-progress tasks that have no session, and replace the stale plans with one. Done in phase 1 as one recorded act in DevHub with the list attached. | 2026-11-13 |


On 2026-11-14 the operator confirmed the rulings above, with what the Chief had added to each, and decided four more with the words "All approved.": G5 (DevHub stays on its present database for the length of the program), G3 (DevHub's unused tools and tables are stopped in phase 1 and removed after one function has been locked without them), G30 (the rules for sessions live in a bc-docs chapter, and the project instruction file points to it), and G34 (the Chief owns every function until phase 12, when a standing owner for each is proposed). The decision is recorded as decision record DEC-71f15e.

Later on 2026-11-14 the operator decided ruling G36: a clean-up, phase 0, comes before phase 1, and three standing rules keep the repositories clean from then on (a shared copy is a read-only mirror of its main branch, and one that a service runs from is brought level only by that service's serving procedure; work is done in worktrees that are removed with their branch when their pull request is merged or closed, after their content is committed and pushed or recorded, and never if they serve the engine or are kept as a frozen build; no pull request stays open without a named owner and a next step). The operator's words were "Shall we add housekeeping/cleaning before program starts and at appropriate positions (mainly PR and branch hygiene -- to avoid bc-docs 141 lagging kind of issues)?" and, to the Chief's proposal, "Go ahead". G36 amended the program after it was locked.

In phase 2 the operator decided the first rulings of the frame, put to him as one pull request to bc-docs and decided by his grant, recorded at the approval desk, for that pull request at its exact commit. Each is stated in full, with what the Chief added, in the main document under "The rulings".

| # | Subject | The ruling |
|---|---|---|
| F1 | What the product is: the statement | BareCount is an enterprise data observation platform. Its product is governed, provable state: a permanent record of what was read from a company's business systems, what that data means in business terms, and what was worked out from it, each written once, at one place, with Evidence of the act. BareCount assures the method by which each record is produced and kept; the result is only as good as the data supplied. Metrics are how that state is consumed. They are not the product. |
| F2 | The definition of "done" | Section 5 of the vocabulary page is adopted as it stands. The words plane, package and value-affecting change are added to that page. |
| F3 | The functional map | The map of the main document, with its nine additions, is the platform's list of functions; it becomes the index of `docs/guide/`. The closed chapter that held the earlier list is history. |
| F4 | The scale of a metric's progress | The vocabulary page's status words are the only scale. The three tiers, the ladder of 25 rungs and the parked drive's ladder become history; the lanes remain as names of functions. |
| F5 | What makes a chapter binding | A chapter is locked when its function is locked, in the pull request that meets the Lock exit. A document of the frame is locked by the operator's recorded approval of it. |
| F7 | Public claims | No public text states a count, a badge or a certification that the platform's records do not show on the day it is published. The claims found on the website are removed; the operator decides the replacing words. |
| F9 | The word "auditor" | It names Codex and nothing else. The outside person of an ISO 27001 or SOC 2 engagement is "the external assessor"; the subsystem that audits metric versions is "the metric audit service". |
| F6 | What Integrity Assurance gives a customer | For each number: the definition and formula it was produced under, by version; the Evidence that the governed acts produced it; the assurance that the declared formula was computed as declared and repeatably; and a number never altered afterwards. Not given: assurance that the supplied data is right, or any external audit or certification. |
| F8 | The word for proof | Two words. "Validated against" a named source is the status word. "Demoed" names proof on the demo plane and is never "done" for a tenant. |
| T6 | How a package names its metrics | By a list, one record for each metric in each package. Function and subfunction choose the list; they do not name the metrics. The interim package says "all" without a list. |
| B6 | The period of a scheduled evaluation | The fiscal calendar supplies it: for each legal entity the tenant has declared, the period that contains the date of the run. The operator supplies a period only for a run started by hand. |
| B7 | What starts canonical resolution | A command only. A completed admission starts nothing. The scheduled cycle issues the command after its admissions and before its metric evaluations. |
| G12 | Merged migrations that are not applied | 0032, 0034, 0035 and 0038 are withdrawn from bc-db's main branch; each returns under a new number with the engine code that needs it. No database is changed. Every migration file on the main branch then has a ledger row or a line in the register of migrations awaiting apply. DEC-bd6894 is not decided by this. | Phase 3 |
| G13 | The names of environments | One list: `dev`, `stg`, `prod`. `dev` is the development machine and the cloud resources named `dev` that serve it; the other two are kept and not built. "Live" and "disposable copy" are not environments. | Phase 3 |
| G14 | The one serve procedure | The single-tree move, performed by one command that verifies from the running server and returns to the previous build. The twin trees and the forced-failure rehearsal are retired. The auditor's separate clearance of a move is retired only if the grant says so in express words, superseding that part of grant `2026-09-29T08-34-38-377Z-ead781aa`. | Phase 3 |
| G15 | The bc-infra stacks that are not deployed | Kept as designed and not built. | Phase 3 |
| G35, the first part | Where Operations' commands are kept | In bc-infra, with no authority to change the cloud; the reference run alone in the DevHub repository. The second part stays open (below). | Phase 3 |
| B1 | The fixed input of the reference run | Yes: one copy, taken once, of the platform database, the Kaveri tenant database and the roles without passwords; kept on the development machine only, identified by committed hashes, and checked for any password, key or token before it is kept. Taking it is a later act of the operator. | Phase 3 |

### Open


| # | Subject | The question | The Chief's recommendation | Needed by |
|---|---|---|---|---|
| G35, the second part | A platform operations application | Does Operations have a screen of its own? (The first part, where its commands are kept, was decided in phase 3.) | Decide with ruling G4; a new screen or a new operating act needs its own ruling. | Phase 12 |
| T4 | Creating a tenant | Which is the one route? | The operator's command, reachable from the console. | Phase 4 |
| T5 | Tenant class | Does creating a tenant of class "customer" count as activating a tenant for an outside party? Two tenants of that class exist today, both suspended, and the vocabulary page says no tenant kind is recorded. | Yes; and correct the vocabulary page. | Phase 4 |
| B2 | The baseline | If the first reference run does not reproduce the values the Kaveri tenant holds, which is the baseline: the values the engine gives today with the contracts in force, or the values held, with the contract state that produced them restored in the copy? | Decide on the evidence of the first run; the Chief reports each difference with its cause. | Phase 3 |
| B3 | A new canonical contract version | When is one warranted? | Only for a changed output field, the meaning of a field, the grain or the key form. | Phase 7 |
| B4 | How proof against the source is produced | On the separate demo plane, or on a demo tenant through the ordinary path? | Decide after phase 2. | Phase 8 |
| B5 | The expected value | From what is it worked out? The vocabulary says "worked out independently from the same source data". Every expected value recorded so far was worked out from a synthetic fixture or from the rows the platform had already admitted. | From the source system's own data, read independently of the platform. This is a stricter reading than the vocabulary's words and needs the ruling. | Phase 8 |
| G1 | Approvals on the development machine | Which acts need the operator's code? | Changes applied to a database and acts on data that cannot be undone. Standing permission for merges the auditor has accepted and for serving a new build. | Phase 12 |
| G4 | One surface for the operator | Should the approval desk and DevHub become one? | Decide after phase 1. | Phase 12 |
| G6 | Decision records with no file | Three records that code cites have no file on the main branch (not re-checked; no annex verifies the count). DevHub holds 663 decision rows and bc-docs holds 659 ADR files [8f]. | Land them as history, then fold them into the guide. | Phase 12 |

### Open: raised by the function dossiers

Each dossier ends with "Open questions for the operator". The questions that are real decisions and are not already in the tables above are listed here, numbered on in the same four series: F for the frame and the product; T for tenants, subscription and delivery; B for the engine, the contracts and proof; G for governance, access, operations and development. The function named is the one whose dossier raises the question. Where the recommendation says "Define step", it is to be proposed in the function's Define step, because the dossier does not support one.

Some dossier questions are already covered above: the one route for creating a tenant (T4), the tenant class column (T5), how a package names its metrics (T6, decided in phase 2), how proof is produced and from what the expected value is worked out (B4, B5), and the approvals, the fixed input, the binding chapter and the single operator surface (G1; B1, decided in phase 3; A5; G4). The four questions of the Operations dossier on unapplied migrations, environment names, the serve procedure and the undeployed cloud units (G12 to G15) were decided in phase 3.

| # | Function | Subject | The question | Recommendation | Needed by |
|---|---|---|---|---|---|
| T7 | S2 | A tenant's later users | Who creates them, the operator only or the tenant admin, and is the users screen in the program? | Define step | Phase 4 |
| T8 | S3 | Resuming a suspended tenant | Is resuming a governed act in the program, and what record does it write? | Define step | Phase 4 |
| T9 | S3 | The two tenants of class `customer` | Are `kaveridemo` and `kaveridemo2` retired, or kept for the thread? | Define step | Phase 4 |
| T10 | S3 | The tenant infrastructure record | Is `tenant.tenant_infrastructure` kept true by the creation act, or retired? | Define step | Phase 4 |
| T11 | S4, DL | The package record | Is `pricing.package` reshaped to hold metrics, or kept for readers while a new table carries the offer? | Define step | Phase 9 |
| T12 | S4 | The interim package | Is it the existing `Free` row or a new `pre_launch_exclusive` row? | Define step | Phase 9 |
| T13 | S4 | Four tiers and external billing | Does DEC-324d9e remain the decided commercial model? DEC-cf6d3b treats its interim package as outside those four tiers, so ruling T1 conflicts with neither record. | Amend a decided record only if the design chosen under ruling T6 changes it. | Phase 9 |
| T14 | DL | The record of "released" | Is it kept for each metric, or implied by membership of a package? | Define step | Phase 9 |
| T15 | DL | A metric in two packages | Does it stay enabled for a tenant that leaves one of them? | Define step | Phase 9 |
| T16 | DL | Classifying a change | Who decides that a change is value-affecting: its author, the certification panel or a rule in the database? | Define step | Phase 7 |
| T17 | DL | How acceptance works | What is the acceptance record, what does the tenant see meanwhile, is there a cut-off date, does it cover metric contract versions, and does the activation fan-out stop or wait? | Define step | Phase 9 |
| T18 | DL | Who enables a metric | The operator or the tenant admin? | The tenant admin, as the vocabulary page says. | Phase 9 |
| T19 | L10 | What a metric needs, and its adoption | Is what a metric version needs declared on the version, with an adoption record for each tenant and metric? | Define step | Phase 9 |
| T20 | L10 | Where provisioning commands come from | Is there one origin, and does the readiness pass stay a default of every worker run? | Define step | Phase 9 |
| T21 | TS | The tenant admin's switches | Which of enable, disable, show and hide are in the program? | Define step | Phase 10 |
| T22 | TS | A metric that is not reporting | Is the tenant told why, in one sentence for each reason, or nothing yet? | Define step | Phase 10 |
| T23 | TS, A1 | Pages that show sample data | Are they removed until they are real, or kept with a notice? | Define step | Phase 10 |
| T24 | NT | Telling a tenant of a pending change | In the portal only, or also by email? | Define step | Phase 10 |
| T25 | PR | A data-subject request | May a tenant admin file one in the portal? | Define step | Phase 11 |
| T26 | PR | A tenant's end | What is retained, for how long, and what is erased? | Define step | Phase 11 |
| T27 | SU | Tickets from a tenant | Are they raised in the portal, or by email only? | Define step | Phase 11 |
| B8 | RT | Who may start an evaluation | The platform operator only, or the tenant admin too? | Define step | Phase 8 |
| B9 | EV | Evidence written with the act | Are admission and canonical evaluation brought to the same all-or-nothing write as metric evaluation, or listed as designed and not built? | Define step | Phase 8 |
| B10 | EV | The HTTP routes for evidence | Removed, or kept for a named caller? | Define step | Phase 8 |
| B11 | PV | Proof on demonstration data and "done" | Does it count for a tenant, or must each tenant have its own proof? | Define step | Phase 8 |
| B12 | L1 | One way into the source catalog | Are the six create routes removed, so that admitting an extract is the only way? | Define step | Phase 5 |
| B13 | L2, L4, L5 | The end of a superseded version | Is the prior version superseded at once, or after a window that code completes? | Define step | Phase 5 |
| B14 | L2, L4 | Review of source, admission and observation contract versions | May a version go from `draft` to in force without a review? | Define step | Phase 5 |
| B15 | L2 | DEC-e27625 | Is an admission contract for each tenant superseded by the binding model? | Define step | Phase 5 |
| B16 | L7, L10 | The broken forward route [9] | Is `onboard-connector` repaired or deleted? | Define step | Phase 5 |
| B17 | L7 | The spelling of the environment | `dev` or `development`? | Define step | Phase 5 |
| B18 | L3 | The panel roster | Is it a governed declaration held as data, or code? | Define step | Phase 6 |
| B19 | L3 | 602 review runs | Closed together, or judged one by one? | Define step | Phase 6 |
| B20 | L4 | The call that authors an observation chain | Which is the one door, and is the call split across L4, L5 and L7? | Define step | Phase 6 |
| B21 | L5 | The demo-world pins | A constant in code or a governed record; and do held versions share the tenants' line of versions? | Define step | Phase 7 |
| B22 | L5 | The approval record | Must an approval carry a second person's record? | Define step | Phase 7 |
| B23 | L6, L9 | What certifies a metric | The deterministic gate alone, or a panel too; and is the chain verdict a gate? | Define step | Phase 7 |
| B24 | L6 | A changed metric | A new version of the same metric contract, or a new contract? | Define step | Phase 7 |
| B25 | L6 | 14 versions that are `active` without certification | Taken in again, retired, or left? | Define step | Phase 7 |
| B26 | L8, L6 | Directory first | Does intake refuse a proposal that has no directory entry? | Define step | Phase 7 |
| B27 | L8 | Marking an entry realized | For a certified version only, or for an `approved` one too? | Define step | Phase 7 |
| B28 | L8 | DEC-85fd8d | Is the reject act built, or the ADR withdrawn? | Define step | Phase 7 |
| B29 | A1 | The empty intervention tables | Kept as reserved, or dropped? | Define step | Phase 11 |
| G7 | S1 | The Cognito pool of record | Is the served pool brought under bc-infra, or does the platform move to the pool the stack already owns? | Define step | Phase 4 |
| G8 | S1 | The token type accepted | Access tokens, as the chapter says, or ID tokens only, as the code does? | Define step | Phase 4 |
| G9 | S1 | The second factor | Mandatory for platform-scope users, or optional as DEC-912f4f states? | Define step | Phase 4 |
| G10 | S2 | Where roles are held | In the Cognito attribute, or in a platform table with history? | Define step | Phase 4 |
| G11 | S2 | The `admin` override | Does `admin` keep passing every role check, or is `super_admin` the only override? | Define step | Phase 4 |
| G16 | L7 | Where a connection's secret is held | In the environment of the served application, or as a reference to the secrets service for each connection? | Define step | Phase 5 |
| G17 | S5 | A screen for each act | Does every governed act get a screen, or only the acts of the thread; and what becomes of the ten placeholder pages? | Define step | Phase 10 |
| G18 | S5 | How the console is served | From a fixed build, or from a development server as today? | Define step | Phase 10 |
| G19 | L9 | The close gate on chain verdicts | Does DevHub keep refusing a session close when a chain verdict turned red? | Define step | Phase 7 |
| G20 | AI | The vendor client and the roster | One shared by all panels, or one for each? | Define step | Phase 6 |
| G21 | AI | Recording cost | For each run in the ledger, or from invoices only? | Define step | Phase 6 |
| G22 | AI | The ABC reasoning panel | Kept with a run record, or retired? | Define step | Phase 6 |
| G23 | NT | Outbound webhooks | Approved by an ADR or removed; and may a tenant register an endpoint? | Define step | Phase 10 |
| G24 | PR | What starts retention | A schedule, or an operator act only? | Define step | Phase 11 |
| G25 | MD | Changing a master list | A governed act with a record, or a reviewed change to code? | Define step | Phase 11 |
| G26 | MD | `master.master_status` | Kept, or is the vocabulary page the only list of status words? | Define step | Phase 11 |
| G27 | MD | What belongs in schema `master` | Do the library register and `semantic_family` leave it? | Define step | Phase 11 |
| G28 | SU | Tickets the platform raises itself | Are they support, or a log of runtime failures? | Define step | Phase 11 |
| G29 | SU | The open tickets | Who owns them, and are they closed together? | Define step | Phase 11 |
| G31 | DV | Memory files | A separate store, or folded into chapters as functions are locked? | Define step | Phase 12 |
| G32 | DV | Which close gates are kept | All of them, or only the report, the commits, the deliverables and the auditor threads? | Define step | Phase 12 |
| G33 | DV | A decision record and its chapter | May a decided ADR merge without the change to its chapter? | Define step | Phase 12 |
