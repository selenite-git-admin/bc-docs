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

A ruling is a decision that belongs to the operator. This annex is the full register: the rulings already decided, the open rulings of the program as a whole, and the open questions raised by the dossier of each function. The main document carries the decided rulings and the open rulings needed first.

A **ruling** is a decision that belongs to the operator. Each is recorded here when made and is then written into the guide. Rulings are numbered in four series: A for the frame and the product; T for tenants, subscription and delivery; B for the engine, the contracts and proof; G for governance, access, operations and development. "Needed by" names the phase of the order of work that cannot finish without the ruling.

### Decided

| # | Subject | The ruling | Date |
|---|---|---|---|
| F1 | What the product is | Metrics are not positioned as the product. bc-docs states that BareCount is "an enterprise data observation platform", and the adopted thesis is Integrity Assurance (DEC-71c027). Metrics are how governed state is consumed. The exact statement is written in phase 2 and confirmed by the operator. Texts that position metrics as the product are corrected. | 2026-11-13 |
| T1 | What a tenant subscribes to | A tenant subscribes to a package. Metrics are bound to packages: one package holds many metrics, and a metric may be in more than one package. | 2026-11-13 |
| T2 | How much of subscription is built in the program | It is designed in full. Only the minimum the thread needs is built. | 2026-11-13 |
| T3 | How a new version reaches a tenant | A change that can affect a reported value reaches a tenant only when the tenant's admin, or a role or user the tenant designates, accepts it. Until then the tenant stays on the version it adopted and continues to report on it. A change that cannot affect a value reaches bound tenants automatically. A change whose effect is uncertain is treated as value-affecting. Values already reported are never worked out again. | 2026-11-13 |
| G2 | The DevHub backlog | Abort the automatically created review tasks, return to "parked" the in-progress tasks that have no session, and replace the stale plans with one. Done in phase 1 as one recorded act in DevHub with the list attached. | 2026-11-13 |

### Open

Ruling G5 (moving DevHub to Postgres) is open: the operator said there is "no specific pain … just aspiration/fear factor", and the Chief recommends "not now". Ruling F9 (which of three things keeps the word "auditor") and ruling G34 (the standing owner of each function after the program) were added when the main document was revised; both are stated in the main document under "Open, and needed in phases 1 to 3".

| # | Subject | The question | The Chief's recommendation | Needed by |
|---|---|---|---|---|
| F2 | The definition of "done" | Is section 5 of the vocabulary page adopted as it stands? | Yes. Add the missing words through that page: plane, package, value-affecting change. | Phase 2 |
| F3 | The functional map | Is the functional map of the main document, with its nine additions, the platform's list of functions? | Yes; amend the chapter in bc-docs to match. | Phase 2 |
| F4 | The scale of a metric's progress | Three scales exist (three tiers, a ladder of 25 rungs, the lanes). Which is kept? | The vocabulary's status words; the others become history. | Phase 2 |
| F5 | What makes a chapter binding | No chapter is locked today. | A chapter is locked when its function is locked. | Phase 2 |
| F6 | What Integrity Assurance gives a customer, and who "the auditor" is | Three different things carry the word "auditor". | Proposed in phase 2. | Phase 2 |
| F7 | Public claims | The website states counts and badges the platform does not have. | Correct them; the operator decides the wording. | Phase 2 |
| T4 | Creating a tenant | Which is the one route? | The operator's command, reachable from the console. | Phase 4 |
| T5 | Tenant class | Does creating a tenant of class "customer" count as activating a tenant for an outside party? Two tenants of that class exist today, both suspended, and the vocabulary page says no tenant kind is recorded. | Yes; and correct the vocabulary page. | Phase 4 |
| T6 | How a package names its metrics | By a list, or by function and subfunction? The package table that exists today lists readers, not metrics, and has no row for the interim package that DEC-cf6d3b names. | Proposed in phase 2. | Phase 2 |
| B1 | The fixed input of the reference run | May one copy of the databases be kept outside the repositories? It holds demo-tenant data and password verifiers. | Yes. | Phase 3 |
| B2 | The baseline | If the first reference run does not reproduce the recorded values, which state of the contracts is the baseline? | Decide on the evidence of the first run. | Phase 3 |
| B3 | A new canonical contract version | When is one warranted? | Only for a changed output field, the meaning of a field, the grain or the key form. | Phase 7 |
| B4 | How proof against the source is produced | On the separate demo plane, or on a demo tenant through the ordinary path? | Decide after phase 2. | Phase 8 |
| B5 | The expected value | From what is it worked out? The vocabulary says "worked out independently from the same source data". Every expected value recorded so far was worked out from a synthetic fixture or from the rows the platform had already admitted. | From the source system's own data, read independently of the platform. This is a stricter reading than the vocabulary's words and needs the ruling. | Phase 8 |
| G1 | Approvals on the development machine | Which acts need the operator's code? | Changes applied to a database and acts on data that cannot be undone. Standing permission for merges the auditor has accepted and for serving a new build. | Phase 12 |
| G3 | Retiring dead DevHub tools and tables | About 35 of DevHub's 110 tools and about 27 of its 66 tables (the two "about" figures are not re-checked; reported in artifacts/spine-review/DEVHUB-2-as-platform-spine.md). | Stop them first; remove them after one function has been locked without them. | Phase 1 |
| G4 | One surface for the operator | Should the approval desk and DevHub become one? | Decide after phase 1. | Phase 12 |
| G6 | Decision records with no file | Three records that code cites have no file on the main branch (not re-checked; no annex verifies the count). DevHub holds 663 decision rows and bc-docs holds 659 ADR files [8f]. | Land them as history, then fold them into the guide. | Phase 12 |

### Open: raised by the function dossiers

Each dossier ends with "Open questions for the operator". The questions that are real decisions and are not already in the tables above are listed here, numbered on in the same four series: A for the frame and the product; T for tenants, subscription and delivery; B for the engine, the contracts and proof; G for governance, access, operations and development. The function named is the one whose dossier raises the question. Where the recommendation says "Define step", it is to be proposed in the function's Define step, because the dossier does not support one.

Some dossier questions are already covered above: the one route for creating a tenant (T4), the tenant class column (T5), how a package names its metrics (T6), how proof is produced and from what the expected value is worked out (B4, B5), and the approvals, the fixed input, the binding chapter and the single operator surface (G1, B1, A5, G4).

| # | Function | Subject | The question | Recommendation | Needed by |
|---|---|---|---|---|---|
| F8 | PV | The word for proof | Is the status word "validated against (source)", as the vocabulary page has it, or "Demoed"? | Define step | Phase 2 |
| T7 | S2 | A tenant's later users | Who creates them, the operator only or the tenant admin, and is the users screen in the program? | Define step | Phase 4 |
| T8 | S3 | Resuming a suspended tenant | Is resuming a governed act in the program, and what record does it write? | Define step | Phase 4 |
| T9 | S3 | The two tenants of class `customer` | Are `kaveridemo` and `kaveridemo2` retired, or kept for the thread? | Define step | Phase 4 |
| T10 | S3 | The tenant infrastructure record | Is `tenant.tenant_infrastructure` kept true by the creation act, or retired? | Define step | Phase 4 |
| T11 | S4, DL | The package record | Is `pricing.package` reshaped to hold metrics, or kept for readers while a new table carries the offer? | Define step | Phase 9 |
| T12 | S4 | The interim package | Is it the existing `Free` row or a new `pre_launch_exclusive` row? | Define step | Phase 9 |
| T13 | S4 | Four tiers and external billing | Does DEC-324d9e remain the decided commercial model? | Ruling T1 needs DEC-324d9e or DEC-cf6d3b amended. | Phase 9 |
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
| B6 | RT | The period of a scheduled evaluation | Who supplies it: the fiscal calendar, a tenant setting or the operator? | Define step | Phase 2 |
| B7 | RT | What starts canonical resolution | A completed admission, a schedule, or a command only? | Define step | Phase 2 |
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
| G12 | OP, S3 | Merged migrations that are not applied | Are 0032, 0034, 0035 and 0038 applied or withdrawn? | Define step | Phase 3 |
| G13 | OP | The names of environments | Is the Mac "dev", and what is a cloud environment called? | Define step | Phase 3 |
| G14 | OP | The one serve procedure | The documented rehearsal on twin trees, or the single-tree move now practised? | Define step | Phase 3 |
| G15 | OP | The bc-infra stacks that are not deployed | Kept as designed and not built, or removed? | Define step | Phase 3 |
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
| G30 | DV | The home of the session rules | A bc-docs chapter with `CLAUDE.md` as a pointer, or `CLAUDE.md` alone? | Define step | Phase 1 |
| G31 | DV | Memory files | A separate store, or folded into chapters as functions are locked? | Define step | Phase 12 |
| G32 | DV | Which close gates are kept | All of them, or only the report, the commits, the deliverables and the auditor threads? | Define step | Phase 12 |
| G33 | DV | A decision record and its chapter | May a decided ADR merge without the change to its chapter? | Define step | Phase 12 |
