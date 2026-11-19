---
id: platform-refactor-program-definition-vocabulary
order: 45.15
title: "The Definition of Vocabulary, in Part"
status: drafting
authority: reference
depends_on: [platform-refactor-program, platform-refactor-program-definition-operations, platform-refactor-program-definition-ai]
governing_sources:
  - Platform Refactor Program (the method; a function taken in part, ruling G40; commands; the order of work, phases 4 and 11; the hand-offs between functions)
  - Function Dossiers (L3, Vocabulary; AI, AI services; L4, Observation Contracts)
  - The Definition of AI Services, in Part
  - Vocabulary (slice 4, business concepts; slice 5, AI panels and their verdicts)
  - Business Concept Authoring (BCF), the onboarding chapter
governing_adrs:
  - DEC-71f15e (the Platform Refactor Program)
  - DEC-02f5a9 (one registry of business concepts)
  - DEC-149ab2 (authority to approve registry content is delegated to the framework, under policy)
  - DEC-45c01b (characteristic admission: fast lane to draft; activation stays the operator's publication)
  - DEC-26b6e2 (an active characteristic is an immutable atom; correction by supersession)
  - DEC-1fbaf1 (withdrawal archives vocabulary admitted in error)
  - DEC-ffee4e (the registry panel runs inside bc-core; the roster is calibration-locked)
  - DEC-346ae7 (for metrics, the panel is a flagger; cited for its scope only)
errata_referenced: []
v2_sources: []
diagrams: []
---

# The Definition of Vocabulary, in Part

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md). It is the written definition that the Define step of function L3, Vocabulary, calls for in phase 4, where ruling G39 takes L3 **in part** and ruling G40 says what that means: the part is the acts this definition names, which the operator approves at the Define step; those acts pass all five steps and are locked; every other act and surface is carried here by name, with its phase, and none is dropped. A function locked in part is not locked for condition 1 of the finish. The operator's approval of this definition is the exit of the Define step. **This definition authorises nothing**: it describes, and every act it names that needs a grant is asked for when it is to be done.

## In plain words

This is the first of five steps for the vocabulary list. You are asked to approve only the five acts named below; the rest is listed and done in phase 11.

- **What the list is.** One governed list of the things the business talks about: entities (Customer, Invoice), characteristics (the meaning part of a name, such as "credit limit") and business concepts (one property of one entity, such as `invoice.bill_to`). A metric can use a concept only once it is live.
- **The five acts taken now.** Add a new entity or concept through the AI group (V1); give your yes to a risky addition (V2); put a new characteristic live (V3); deal with new cases the AI group could not decide (V4); hide a concept that never went live, without deleting it (V5). Changing what already exists waits for phase 11.
- **Question 1: who puts a concept live.** Today, when the AI group approves a new entity or concept, it goes live at once and nobody signs it off. A rule in the registry's settings table could ask for your yes; the Chief read the table on 2026-11-19 and it holds no such rule for the registry, so that is how it works today. The recommended answer keeps that. Under it you can **no longer put a draft entity or concept live by hand**, and, because nothing in this part can change the settings table, you have no way to make these additions wait for you until phase 11.
- **Question 2: the 602 old cases sent to review.** The recommendation: this part handles only cases from the day you approve; the old ones wait, untouched, until phase 11. A live read of 2026-11-19 shows 602 records with the verdict `OPERATOR_REVIEW`, of which 97 have no disposition; the Audit of L3 reads them again.
- **Question 3: adding a concept with no AI.** You can already do this yourself. The recommendation keeps it as an option of the same single command rather than a second door.
- **Question 4: a decided ADR the code contradicts.** DEC-45c01b says a new characteristic needs no yes from you to be admitted; the code asks for one. The recommendation keeps the code's stricter way, which **amends a decided record** (asked of you separately). Each new characteristic then costs you two acts: your yes to admit it (V2) and your yes to put it live (V3).
- **The roster of AI models** was decided on 2026-11-19 by desk request 523, as ruling B18; this part follows it.
- **Cost.** Proving the part means adding one real concept, which calls the paid AI group twice; that run is asked for when it is to be done. Even when the part is locked, the vocabulary function still counts as unfinished until the rest is done.

## How to read this definition

It is a design, in the form of the Definition of AI services. Each act in section 3 has four parts. **Today** gives the facts the act starts from, each with its file and line. **The definition** states what holds once the part is locked. **What must change** lists the repairs the Modify step takes; an item marked **the operator's act** is on the hard line (a database change, a policy row, an ADR's status, a run's disposition), and approving this definition does not approve it. **Carried** names what this act leaves to a later phase. Where we are guessing, we say so with **(inferred)**; everything else is established at the line cited.

Words follow the vocabulary page: "sent to operator review" and "waiting for operator confirm" for panel outcomes (the code's outcome `parked` is quoted only as an identifier); "registry certification record" for the registry's records; "concept active", never "certified", for a concept (`bc-docs:docs/reference/vocabulary.md:565, 663-664 @ 6ecfdd0c`).

## What was checked, and by whom

A worker gathered the facts on 2026-11-19, read-only, from git objects at origin/main: barecount-devhub `artifacts/chief/L3-define-inputs-2026-11-19.md`. A second worker, who wrote this definition, opened at source every fact used here and corrected the gathering where it was wrong (listed at the end). The Chief reads the whole before it goes to the operator. The writer queried no database; the Chief made one read-only query of the live platform database on 2026-11-19, of `contract.framework_policy` and `contract.operator_confirm_rule`: the policy in force for the registry, `bcf-registry-scope1` version `v1`, in force since 2026-05-22, carries no operator-confirm rule (its list of rules is empty), with sampling rate 1.0 and ADR reference DEC-02f5a9; the only two rules in the rule table belong to scope `mcf`. No route was called, and no service and no panel was run. Counts of rows quoted from the dossier (602 runs, one draft concept) were read on 2026-11-13 and are not re-read.

**Commits read.** bc-docs `6ecfdd0c`; bc-core `fd4b55ca`; bc-admin `d37b241`; barecount-devhub `3f4684fc`; bc-db `ca1aabd` (one search only). The Definition of AI services was read in its merged text, bc-docs `docs/development/platform-refactor-program/definition-ai-services.md @ f1a20074` (identical to the draft first read at `abfb0804`); a cold reader's findings on the first draft of this definition (barecount-devhub `artifacts/chief/L3-definition-cold-read-2026-11-19.md`) were applied, each verified at source. A citation that names no commit is at the commit of its repository given here.

## 1. What L3 is

L3 authors the business concept registry (`concept_registry`) and keeps the records of how each entry was admitted (`bcf.panel_output_record`, read; `bcf.certification_record`, written) (`bc-docs:docs/development/platform-refactor-program/functions-authoring-lanes.md:310, 331-332 @ 6ecfdd0c`). Contracts refer to a concept by identity, and the observation resolver refuses a concept that is not `active` (`bc-core:src/registry/resolvers/observation-concept-resolver.service.ts:128-130 @ fd4b55ca`). So for the metric spine, "usable" for a concept means **concept active**.

The line with AI is the one the Definition of AI services draws, and this definition takes the other side of it. AI's act A1 runs the registry panel and ends when the panel record is written, or when the run is refused or fails. Everything after the record is L3's: the reading of the verdict by the orchestrator, the registry certification record, the registry write, the outcome kinds, the confirm of a high-risk act, the handling of runs sent to operator review, the operator-direct routes, the direct panel-record write and the intake queue (Definition of AI services, sections 3 and 5). The one request `POST /api/bcf/registry-authoring-runs` holds both: it writes the panel record and then calls `runS1` with its uid (`bc-core:src/registry/bcf/panel/registry-authoring-run.service.ts:74-76`).

**One command for the request, built by L3.** One command performs both, as the one request does today: AI's panel run (A1) and L3's authoring that follows it (V1). L3 builds the command at its Modify step in phase 4, because its result is a registry outcome; AI's panel run is its first step, and what that step checks, calls and records is AI's, as the AI Definition states. The command's `check` reports both sides before any vendor is called: AI's vendor checks, and L3's duplicate, policy and risk-tier rules. The AI Definition does not say who builds the command; the sentence it needs is named in the section "Where this definition differs".

**What decides a registry entry.** DEC-149ab2 delegates approval within its scope to the framework: "AI consensus constitutes **Framework Approval**", under policy, with operator override as the exception (`bc-docs:docs/governance/adrs/ADR-149ab2.md:24`). The code applies it through a risk tier. `registry_create` and `registry_add_version` are low-risk (`bc-core:src/registry/framework-approval/types.ts:405-418`); a low-risk act under a registry policy with no operator-confirm rule receives its registry certification record without a human (`bc-core:src/registry/framework-approval/framework-approval.service.ts:172-199`). Every other act, or any act under a policy that carries an operator-confirm rule, waits for operator confirm (`framework-approval.service.ts:174-189`). DEC-346ae7's "the AI panel is a flagger" is stated for metric validation (`bc-docs:docs/governance/adrs/ADR-346ae7.md:3, 28`) and does not govern the registry.

## 2. The part and the rest, at a glance

| # | Act | Where |
|---|---|---|
| V1 | Author an entity, value concept or reference concept through the panel, to concept active | the part (phase 4) |
| V2 | Confirm a high-risk registry act and complete it | the part (phase 4) |
| V3 | Publish a characteristic (draft to active) | the part (phase 4) |
| V4 | Handle a run sent to operator review: adopt the maker's draft, or record a disposition | the part (phase 4), for new runs (question 2) |
| V5 | Withdraw a draft concept that never became active | the part (phase 4) |
| R1 to R11 | Six acts that change what exists (versions, supersession, definition amendment, withdrawal of a characteristic, corrections, source references) and five other surfaces (rejection-log override, one-time repairs, direct panel-record write, the registry policy, the intake queue) | carried to phase 11 (section 4) |

The part is the expected part, "new concepts through the panel and publish", with what it cannot stand without. A metric of the spine binds concepts; a new concept on a new characteristic needs V1, then V2 (characteristic admission is high-risk), then V3, then V1 for the concept. V4 is in the part because a new run sent to operator review would otherwise strand the case; V5 and V1's resume are the recovery when activation fails inside V1 (section 3). The registry reads are the `status` and `verify` verbs of these acts.

## 3. The acts of the part

Each act gets one command with the four verbs: **status**, **check**, **do**, **verify**. The command is engine code; a session, the operator console and DevHub use it, and the other ways in are deleted (the method, "Commands"; `bc-docs:docs/development/platform-refactor-program.md:261`).

### V1. Author an entity or concept through the panel

**Today.**
- Who: `platform_admin` or `operator` (`bc-core:src/registry/bcf/panel/registry-authoring-run.controller.ts:28 @ fd4b55ca`). The candidate is one of `createEntity`, `createBusinessConcept`, `createReferenceConcept`, `createCharacteristic` (`bc-core:src/registry/bcf/panel/registry-authoring-run.dto.ts:63-67`).
- Before any model call the run refuses a duplicate characteristic or concept, and refuses when no registry policy is active (`bc-core:src/registry/bcf/panel/registry-authoring-run.service.ts:67-73, 90-120`). These are registry rules, L3's, reported by the one command of section 1.
- After the record, `runS1` reads the verdict. Anything but `APPROVE_FOR_DRAFT`, or an invalid recommendation, returns outcome `parked` with no write (`bc-core:src/registry/bcf/panel/registry-authoring-orchestrator.service.ts:100-117`). The registry certification record is refused when the record is missing, quarantined, not approved, or of another policy version than the active one (`bc-core:src/registry/framework-approval/framework-approval.service.ts:421-453`). A high-risk act returns `awaiting_operator_confirm` with no write (`registry-authoring-orchestrator.service.ts:126-138`).
- **When the active registry policy carries no operator-confirm rule**, a low-risk entity or concept is written at `draft` (`bc-core:src/database/schema/concept-registry/business-concept.ts:116`) and **made active in the same request**; when the policy carries one, the act waits for operator confirm instead (`framework-approval.service.ts:174-189`), and V2 then writes it and makes it active. The policy in force carries none (the Chief's read, "What was checked"), so the first case is today's. In the code, the AI panel itself signs the go-live and no person's role is checked: `autoActivateAuthoredEntity` and `autoActivateAuthoredBusinessConcept` call the publication writer with the panel's actor `bcf-registry-authoring-panel` and no roles (`registry-authoring-orchestrator.service.ts:150-188, 593-611, 722-740`). The rationale text is fixed in code and carries the tag `B6 fast-lane auto-publication` (`bc-core:src/registry/bcf/panel/registry-authoring-panel.types.ts:65, 82-118`). The writer admits that actor without the `operator` role, and only that actor (`framework-approval.service.ts:283-288`); a code comment records an operator decision of 2026-09-29, TSK-29ce9c, "keep the fast lane" (`bc-core:src/registry/framework-approval/types.ts:297-302`), which this worker did not check against a grant.
- A failed activation does not throw: the entry stays `draft` and the outcome is `authored_activation_pending`, for an entity (`registry-authoring-orchestrator.service.ts:586-591, 612-621`) as for a concept (`:741-750`). The header's way out is the manual publication route (`:24-27`).
- **Defect: a draft entity left this way has no way out under answer A of question 1.** The withdraw-draft route takes concepts only (`bc-core:src/registry/concept-registry/registry-authoring.controller.ts:746-747`), entities have no `archived` state (`vocabulary.md:600`), and under answer A the publication route no longer takes entities.
- **What the texts say.** The orchestrator's own header says the opposite of its code: "Only the `createEntity` branch of `runS1` delegates to the publication service"; `createBusinessConcept` does "NOT auto-activate" (`registry-authoring-orchestrator.service.ts:27-30`, repeated at `:83-85`). The dossier says "a concept is not" made active automatically (`functions-authoring-lanes.md:357`). The onboarding chapter says "No write occurs without the confirm" (`bc-docs:docs/onboarding/business-field-and-business-object-onboarding.md:101-103`). The vocabulary says of a panel draft: "Nothing a panel approves is in force until its governed act and gates have run" (`vocabulary.md:673`). The publication service's header calls the operator-confirm "the publication authority" (`bc-core:src/registry/bcf/panel/registry-publication.service.ts:9-10`).
- **Callers.** bc-admin (`bc-admin:src/api/business-concepts.ts:761 @ d37b241`) and seven DevHub scripts (`barecount-devhub:scripts/_pass1-c2-transport.mjs:28`, `_pass1-c5-transport.mjs:69`, `_pass1-retrofit-batch-1-transport.mjs:166`, `_pass1-retrofit-batch-1-transport-v2.mjs:59`, `_pass2-e1-transport.mjs:48`, `_pass2-e2-transport.mjs:85`, `_pass3-item-shelf-life-bc-binding-transport.mjs:139 @ 3f4684fc`).

**The definition.**
- One command authors an entity, value concept or reference concept, with AI's A1 as its first step (section 1). L3's part begins at the panel record and ends at an outcome kind.
- **One way to concept active**, as question 1 rules. This definition is written for the recommended answer: activation is the last step of V1 (and of V2 for a concept or entity), performed by the panel's actor through the one publication writer, when the active policy carries no operator-confirm rule, as it carries none today; there is no route that makes an entity or concept active. A policy rule would make every act wait for the operator (`framework-approval.service.ts:174-176`), but no route writes the policy and the part writes none (R10).
- **A failed activation is resumed by V1.** Re-running V1's `do` on the same run uid completes the activation of the draft entity or concept through the same writer, by the same actor. That is one way to active, not a second **(inferred)**: the publication writer already resumes a confirm that did not land (`registry-authoring-orchestrator.service.ts:634-648`). A concept that should not go live is withdrawn by V5 instead.
- A characteristic candidate ends at waiting for operator confirm (V2) and is made active only by V3.
- `check` reports the duplicate, the active policy (its version and whether it carries operator-confirm rules) and the risk tier before any vendor is called. `do` returns the outcome kind. `verify` reads the registry row, its state and the registry certification records that stamp it.

**What must change.**
1. The command is built; the seven DevHub scripts are retired; bc-admin calls the command.
2. The texts that contradict the rule question 1 keeps are corrected in the Lock change: the orchestrator header (`:18-30, 80-85`), the run service header that still calls the panel record "bc-ai's" (`registry-authoring-run.service.ts:19-24`), the dossier line, the onboarding chapter and, under answer A, the vocabulary line (section 9).
3. The fast-lane actor name is held once: it is declared twice (`registry-authoring-panel.types.ts:35`; `types.ts:302`).
4. V1's `do` resumes a failed activation by run uid, for an entity and for a concept, so that the entity defect above has a way out.
5. Under answer (b) of ruling B18 (section 9), the command reads the registry panel's roster from the declaration AI builds; under the other answers, nothing here changes.

**Carried.** The calibration draw on each run (`bc-core:src/registry/framework-calibration/calibration-sampling.service.ts:54-67`) writes `contract.phase_state` (`bc-core:src/registry/framework-calibration/phase-state.write.repository.ts:2-11, 27`); it is left as built and listed under R10.

### V2. Confirm a high-risk registry act and complete it

**Today.**
- Who: `operator` only (`bc-core:src/registry/bcf/panel/registry-shape-certification-confirm.controller.ts:39-40 @ fd4b55ca`). Route: `POST /api/bcf/registry-shape-certifications/confirm`, with run uid, subject kind, action code and a rationale of at least 40 characters (`bc-core:src/registry/framework-approval/types.ts:426`; `framework-approval.service.ts:293-298`).
- It re-runs every precondition, refuses a second registry certification record for the same run and act ("one panel run authorizes one Registry write"), and writes the record with provenance `operator_confirmed` (`framework-approval.service.ts:253-310`). A duplicate resumes the write if it did not land (`registry-authoring-orchestrator.service.ts:233-267`).
- The executor then writes a characteristic at `draft`, or a concept (and makes it active, as V1), or performs a concept supersession; for five other acts it returns a "registry certification record minted, write pending" outcome that the rest's routes finish (`registry-authoring-orchestrator.service.ts:286-416, 433-464`).
- The same route completes an operator-direct entry, whose reply points to it (`bc-core:src/registry/bcf/recommendations/business-concept-authoring/bcf-business-concept-authoring-recommendation.service.ts:328-332`), and an adopted run (V4): bc-admin calls it on the adoption's run uid (`bc-admin:src/api/business-concepts.ts:957-959, 783`). Two DevHub scripts call it (`barecount-devhub:scripts/_pass1-c2-confirm.mjs:35`, `_pass1-c5-confirm.mjs:46`).

**The definition.** One command. In the part it completes characteristic admission (`registry_author_vocabulary`), a concept or entity whose policy required confirm, an operator-direct entry and an adopted run. `check` refuses before any write an actor without `operator`, a short rationale, and a run that already has its record. The part's command takes only these four cases and refuses the others.

**What must change.** The command is built; the two DevHub scripts are retired.

**Carried.** The concept supersession branch and the five "write pending" branches serve the rest (R1 to R4). They are not part of the locked command; until phase 11 they stay reachable through today's confirm route, which the lock guard names as a known exception with its phase, so that a locked command carries no unlocked branch.

### V3. Publish a characteristic

**Today.**
- Two calls: `POST /api/bcf/registry-publications`, then `/confirm`, both decorated `platform_admin` or `operator` (`bc-core:src/registry/bcf/panel/registry-publication.controller.ts:34-67 @ fd4b55ca`). The first returns `awaiting_operator_confirm` and writes nothing; the second writes a registry certification record with action `registry_transition` and moves the row from `draft` to `active` (`registry-publication.service.ts:8-19`; `framework-approval.service.ts:283-288`). For a characteristic it refuses without `semanticFinalityAffirmed=true` (`registry-publication.service.ts:263-269`), because publication freezes term and definition (DEC-26b6e2, `bc-docs:docs/governance/adrs/ADR-26b6e2.md:25`).
- The service's header still says characteristic publication is "blocked on the `characteristic_version` DBCP" (`registry-publication.service.ts:25-26`); DEC-26b6e2 decided there is no characteristic version, and the code publishes one.
- Callers: bc-admin (`bc-admin:src/api/business-concepts.ts:575, 583`) and one DevHub script (`barecount-devhub:scripts/_pass1-retrofit-batch-1-v2-pilot-activate.mjs:74, 98`).

**The definition.** One command with two verbs of `do` (request, confirm), for a characteristic. Under answer A of question 1 it refuses an entity or concept. `check` reports the state, the authoring registry certification record it publishes against, and the role.

**What must change.** The command is built; the DevHub script is retired; the stale header is corrected.

### V4. Handle a run sent to operator review

**Today.**
- The queue: `GET /api/bcf/review-queue`, runs with verdict `OPERATOR_REVIEW` and no disposition, at most 200, each with its adoptability (`bc-core:src/registry/bcf/adjudication/panel-operator-adjudication.controller.ts:56-86 @ fd4b55ca`; `bc-core:src/registry/framework-approval/repositories/panel-output-record.read.repository.ts:56`). It has no date filter.
- Adopt: `POST /api/bcf/registry-panel-operator-adjudications`, decorated `platform_admin` (`panel-operator-adjudication.controller.ts:88-118`). It runs ten gates, among them that the moderator's reason contains one of four fixed phrases and a rationale of at least 40 characters (`bc-core:src/registry/bcf/adjudication/panel-operator-adjudication.types.ts:43-60`), then writes an operator-direct panel record and a registry certification record in one transaction; the original run is never written (`controller.ts:95-111`). The writer needs the `operator` role (`bc-core:src/registry/bcf/adjudication/panel-operator-adjudication.service.ts:157, 506-512`). The registry write follows through V2.
- Dispose: `POST /api/bcf/registry-panel-runs/:panelRunUid/disposition`, `platform_admin`, write-once, one of six codes (`panel-operator-adjudication.controller.ts:120-142`; `bc-core:src/registry/bcf/adjudication/panel-operator-adjudication.dto.ts:172-179`, repeated in a CHECK at `bc-core:src/database/schema/bcf/panel-output-record.ts:102-104`).

**The definition.** One command, with `do` adopt or `do` dispose. Its `status` lists the runs in the part's scope apart from the backlog, as question 2 rules. Adopting hands to V2 by the new run uid.

**What must change.**
1. The command is built. The four phrases and the rationale floor are declared once (section 7).
2. The queue read gains a cut-off: the command's `status` and `do` take only runs whose `created_at` is on or after the date question 2 names, and `status` reports the count before it apart. The column exists and is already indexed for this queue (`bc-core:src/database/schema/bcf/panel-output-record.ts:100-101`); no schema change. Today's route reads the whole queue (`bc-core:src/registry/bcf/adjudication/panel-operator-adjudication.controller.ts:67-70`) and is deleted with the other ways in.

**Carried.** The backlog of runs before the cut-off is ruling B19, carried by name to phase 11 (question 2); until then it stays in the table, untouched.

### V5. Withdraw a draft concept that never became active

**Today.** `POST /api/bcf/registry/concepts/:conceptId/withdraw-draft`, `platform_admin`, hides one unfinished concept left at `draft`, without deleting it (it sets `archived_at`); its route description says it refuses a concept not at `draft` or bound in a live metric contract, and asks a rationale of at least 40 characters (`bc-core:src/registry/concept-registry/registry-authoring.controller.ts:746-753 @ fd4b55ca`). It is the clean-up for a failed activation (TSK-136117, same lines).

**The definition.** One command, for a draft concept that should not go live; a draft that should go live is resumed by V1. It is in the part because V1's lock cannot leave a draft with no act that ends it. It does not cover an entity (V1, the defect). The one draft concept the dossier counted (`functions-authoring-lanes.md:391`) is not touched by approving this definition; withdrawing it is asked for when it is to be done.

**Carried.** Withdrawing an active characteristic, with its dependent concepts, is R4.

### One new concept through the part

This is the walk the Prove step makes: a worker given only the chapter and the commands takes one new concept, on a new characteristic, to concept active. It is written for the recommended answers of section 9.

| Step | Act | Who | What records it | Where it can stop |
|---|---|---|---|---|
| 1 | V1 `check`: the home entity is active, no duplicate, a policy is active | the worker | nothing | no policy row (R10); a duplicate |
| 2 | V1 `do` with a `createCharacteristic` candidate | the worker | the panel record (AI) | vendor failure (AI); sent to operator review (V4) |
| 3 | V2 `do`: confirm the admission, rationale of 40 characters or more | the operator | a registry certification record; the characteristic at `draft` | an actor without `operator` |
| 4 | V3 `do`: request, then confirm with semantic finality affirmed | the operator | a `registry_transition` record; the characteristic at `active` | the characteristic not at `draft` |
| 5 | V1 `do` with a `createBusinessConcept` candidate on that characteristic | the worker | the panel record; two registry certification records; the concept at `active` | `authored_activation_pending`, resumed by V1 or ended by V5 |
| 6 | V1 `verify`, then L4 reads the concept by id | the worker | the registry row | the concept not `active` |

Steps 2 and 5 each run the paid AI panel; the walk is asked for when it is to be done, and approving this definition approves no run. Steps 3 and 4 are the operator's acts. In the Prove step they are performed only through their `status`, `check` and `verify` verbs unless the operator grants the act, as phase 3 did for Operations (`platform-refactor-program.md:269`) **(inferred)**: whether that rule carries to phase 4 is the Chief's to propose at the Prove step.

## 4. The rest, carried by name to phase 11

| # | Act or surface | Today | Why the spine does not need it |
|---|---|---|---|
| R1 | Add a version to an entity or concept, and its two recommendation routes | `bc-core:src/__architecture__/routes.snapshot.json:402-403, 409-410 @ fd4b55ca` | Changes an existing concept |
| R2 | Supersede an entity, concept or characteristic, and the characteristic supersession recommendation | `routes.snapshot.json:393-394, 401, 408` | Changes an existing concept |
| R3 | Amend a characteristic's definition, and its recommendation | `routes.snapshot.json:391-392` | Changes an existing atom |
| R4 | Withdraw a characteristic, and its recommendation | `routes.snapshot.json:395-396`; DEC-1fbaf1 | Corrects an admission error |
| R5 | The four correction recommendations (concept, reference, shape, entity) | `routes.snapshot.json:398-400, 407` | Corrects an existing concept |
| R6 | Link a concept to a source field, `mcf_publisher`; shared with L1 | `routes.snapshot.json:412` | An advisory link; no step of the thread reads it |
| R7 | Override a rejection-log entry | `routes.snapshot.json:436`; `bc-core:src/registry/framework-approval/rejection-log.controller.ts:50-51`; the registry path writes no such row (`bc-core:src/registry/bcf/panel/registry-authoring-orchestrator.service.ts:34-36`) | Proposed for deletion: dead for the registry **(inferred)** |
| R8 | Two one-time repair routes | `routes.snapshot.json:406, 411` | Proposed for deletion (`functions-authoring-lanes.md:430`) |
| R9 | Write a panel record directly, `platform_admin` or `operator` | `routes.snapshot.json:384`; `bc-core:src/registry/panel-output-record.controller.ts:28-29` | A third writer of the record; no caller found in bc-admin or DevHub scripts |
| R10 | The registry policy, its operator-confirm rules and the phase counter: `contract.framework_policy`, `contract.operator_confirm_rule`, `contract.phase_state` | read-only repositories (`bc-core:src/registry/framework-approval/repositories/framework-policy.repository.ts:1-14`; `operator-confirm-rule.repository.ts:1-14`); `phase_state` written by the calibration draw. No route writes the policy; who wrote the active row is not established | The part reads them and writes no policy. An act that records a new registry policy version is carried to phase 11, with its owner (L3, proposed); until then the policy stays as it is (question 1) |
| R11 | The intake queue: enqueue, list, read, route a panel result, age out | `routes.snapshot.json:104-105, 438-440`; `bc-core:src/registry/intake-queue.controller.ts:1-14`; its admission step was retired with the business-field catalog (`bc-core:src/registry/framework-approval/framework-approval.module.ts:3-11`) | A relic of the retired catalog **(inferred)**; whether it is used was not established |

Also carried by name: the 602-run backlog (B19, question 2); an `archived` state for entities (dossier question 3; a schema change; `vocabulary.md:600`); separating operator-direct entries from panel verdicts in `bcf.panel_output_record` (vocabulary S5.6 defect 2, with AI, as the AI Definition carries it); retiring the `contract` copies of the certification and panel tables (`functions-authoring-lanes.md:434`); the nine operator-direct routes not named in question 3; and the chapters `business-vocabulary.md` (rewrite), `canonical-field-seeding.md`, `multi-standard-onboarding.md`, the two manifests and the 17 technical notes (history) (`bc-docs:docs/development/platform-refactor-program/chapters.md:116, 122, 124, 210, 212`).

**The chapter of the part.** The Lock step merges `docs/onboarding/business-field-and-business-object-onboarding.md` for V1 to V5, marked locked in part. The two program texts differ: the dossier says rewrite (`functions-authoring-lanes.md:414`), the chapter register says keep nearly as is (`chapters.md:208`). This definition follows the register, with the corrections it names plus these: the claim that no write occurs without the confirm (`:101-103`); the claim that the panel path mints only value and descriptive concepts (`:80, 172`), since the run accepts `createReferenceConcept` with an identity role (`registry-authoring-run.dto.ts:63-67, 127-135`); orphan repair listed as an authoring action (`:119`); and the missing publication, review queue and withdraw-draft. `business-concept-registry.md` keeps its verdict (`chapters.md:150`) and is corrected for the lifecycle under the part.

## 5. What is not L3's

| Act | Owner |
|---|---|
| The panel run up to the written panel record; the host, roster, prompts, vendors and cost | AI (Definition of AI services, A1) |
| Reading a concept into an observation field mapping; refusing an inactive one | L4 (`observation-concept-resolver.service.ts:128-130`) |
| Reading concepts and the grain entity into canonical and metric contracts | L5, L6 |
| Where roles are held, and whether `admin` passes every check | S2, rulings G10 and G11, phase 9 (`bc-docs:docs/development/platform-refactor-program/rulings.md:165-166`) |
| The bc-db migration path for any schema change | OP, under the Database Change Protocol |

## 6. Hand-offs

| Neighbour | L3 receives | L3 hands on | Record |
|---|---|---|---|
| AI | The panel record, read by uid (`registry-authoring-run.service.ts:75-76`) | The candidate and the active policy version, from which AI's packet is built (`:68-74`) | `bcf.panel_output_record` |
| L4 | Nothing as an act; L3's concept supersession reads L4's active versions and refuses while one maps the concept (`registry-authoring.service.ts:1817-1849`, reached from the supersession at `:1090` through `:1763-1782`) | A concept at `active`, found by id. L4's resolver reads and checks `lifecycle_state`, `entity_id`, `kind`, `representation_term`, `data_type`, `unit`, `reference_role` and `target_entity_id`, and the closed value set held on the concept's active version | `concept_registry.business_concept`, and `concept_registry.business_concept_version` for the value set (`observation-concept-resolver.service.ts:116-135, 531-545, 584-625, 706-720`) |
| L5, L6 | Nothing | Concepts and the grain entity, by id (`functions-authoring-lanes.md:370-371`) | the same |
| The operator | Confirms, publications, adoptions, dispositions, the policy row | Outcome kinds and the queue | `bcf.certification_record`; `bcf.panel_output_record` |

A change to any of the fields L4's resolver reads makes the resolver refuse an observation body whose frozen copy differs. These two hand-offs with L4 were added to this definition on 2026-11-19, from `definition-observation-contracts.md`, section "Where this definition differs from the Definitions of AI services and of Vocabulary".

No stitch contract names L3. This definition proposes **no new stitch contract**, for the reasons the AI Definition gives (section 6 there): each hand-off is inside one engine through a named record, and "usable" for L4 is a single rule the resolver already enforces **(inferred)**. The Chief checks that the AI, L3 and L4 Definitions state the same records before any is approved.

## 7. Values written into code that Modify moves into declarations

| Value | Where |
|---|---|
| Low-risk action codes `registry_create`, `registry_add_version` | `bc-core:src/registry/framework-approval/types.ts:405-418` |
| Rationale floor of 40 characters, held twice | `types.ts:426`; `panel-operator-adjudication.types.ts:60` |
| The four phrases the adoption gate looks for | `panel-operator-adjudication.types.ts:43-48` |
| Fast-lane actor and rationale text | `registry-authoring-panel.types.ts:35, 65, 82-118`; `types.ts:302` |
| Disposition codes, in code and in a CHECK | `panel-operator-adjudication.dto.ts:172-179`; `panel-output-record.ts:102-104` |
| Review-queue limit, 200 | `panel-output-record.read.repository.ts:56` |
| Fifteen representation terms and the four-word term floor; the vocabulary lists eight | `bc-core:src/registry/bcf/panel/characteristic-term-grammar.ts:23-29`; `vocabulary.md:524` |
| Calibration ladder 50 runs, 100, 25 and 5 percent; scope `bf_bo`, a retired name | `calibration-sampling.service.ts:54-67` |

Moving a value is not a change of rule when the declared value is the value that runs. Any value whose declaration would differ is put to the operator.

## 8. What the part's lock will mean

1. Each of V1 to V5 is performed by its command alone; a guard fails when a second route, script or screen performs one of them.
2. An entity or concept reaches `active` one way only, the way question 1 keeps; a guard fails on a second.
3. No file outside the registry writer writes `concept_registry`. This guard is **new**: the comments that cite `bcf-c5-governance-state-sole-writer.spec.ts` (`bc-core:src/registry/framework-approval/repositories/rejection-log.write.repository.ts:25, 46`) name a file that is not in the tree at `fd4b55ca`.
4. The lifecycle in the part's chapter equals the CHECK (`business-concept.ts:129-130`), and the chapter says which states the part's acts set (`draft`, `active`, `archived`).
5. The part's files pass the code rules; its commands are tested against a real database.
6. The part's chapter is merged, marked locked in part, and the texts of V1 item 2 are corrected in the same change.

**Roles until phase 9.** The part changes no decorator. Publication and adoption are decorated for `platform_admin` while their writer refuses an actor without `operator` (`framework-approval.service.ts:283-288`), and the guard lets `admin` and `super_admin` pass every decorator (`bc-core:src/auth/guards/roles.guard.ts:34-37`). So the route's decorator is looser than its writer: an actor holding only `platform_admin` passes the route and is refused by the writer, today as after the lock, and nobody is newly refused. The part assumes that the operator's acts (V2, V3, V4) are done by an actor holding `operator`, and each command's `check` names the role the writer needs before any write, so the refusal comes before the call instead of inside it. Who holds `operator` today is not established (roles sit outside the repositories read). Rulings G10 and G11 decide the rest in phase 9.

**Established or not, on the other surfaces raised.**
- The policy tables sit in schema `contract`; L3's repositories read them and none writes them; no route writes `framework_policy`; no bc-db migration at `ca1aabd` names it outside the baseline. Who authored the active row is **not established**; the repository calls it operator-authored (`framework-policy.repository.ts:4-5`). Owner proposed: L3, with a writer only when R10 is taken in phase 11.
- No "taxonomy gate" exists by that name in bc-core `src` or `scripts`, bc-docs `docs`, or barecount-devhub, at the commits read. The nearest rules are the term floor (section 7) and the duplicate refusal (V1).

## 9. Questions for the operator

Each is put as a proposed ruling. They were recorded on 2026-11-19 as rulings B32, B33, B34 and B35, on the operator's desk grant `2026-11-19T07-05-41-031Z-945d99c6` (text SHA-256 `945d99c65dcbf531a64e097619ce8caaed6fbc4f59cafc0d4898a30efa295c52`, desk request 525); the amendment of DEC-45c01b that ruling B35 calls for was directed by desk grant `2026-11-19T07-06-27-510Z-b4893712` (request 526).

**Ruling B18, the roster, is not asked here.** The Definition of AI services recommends deciding it now for all three panels (its question 1, answer (b)), and the operator granted it on desk request 523 on 2026-11-19 (grant `2026-11-19T07-04-50-111Z-60d74091`), recorded as ruling B18. The registry panel's roster becomes a committed declaration that AI builds in phase 4, and L3's part does one thing: V1's command reads the seats from it (V1, item 5), which meets the dossier's lock item 2 (`functions-authoring-lanes.md:431`).

**1. One way for an entity or concept to reach `active`.** When the active policy carries no operator-confirm rule, the code makes a panel-approved entity or concept active in the same request; the program's texts say a concept waits for the operator (V1). The policy in force carries no such rule (the Chief's read of 2026-11-19, "What was checked"), so this is what happens today.
- Options: (A) keep the code's way. Activation is the last step of V1 and V2, by the panel's actor, under the policy as it stands; the publication route serves characteristics only; a failed activation is resumed by V1 or withdrawn by V5. (B) Authoring ends at `draft`; the publication command, performed by the operator, is the only way for all three kinds; the fast lane is deleted.
- Recommendation: (A). It is what runs, and it rests on DEC-149ab2's delegation under policy. A code comment also records an operator decision to keep the fast lane (TSK-29ce9c); this worker did not find it as a recorded grant.
- What follows: under (A), **the operator can no longer put a draft entity or concept live by hand**, and the Lock change corrects the dossier, the orchestrator header and the onboarding chapter, and qualifies the vocabulary's "approved for draft" (`vocabulary.md:653, 673`) for the registry. The only control over it is a rule in the policy, and nothing writes the policy: the row's author is not established, no route writes it, the part adds none, and the act that records a policy version is carried to phase 11 (R10). So until phase 11, under (A), a panel-approved entity or concept goes live with no human act, as it does today; if the operator wants a human act on each addition before then, the answer is (B). Under (B), every new entity and concept of the spine waits for two operator calls with a rationale, and V1's command ends at `draft`.

**2. Runs sent to operator review: the scope of V4 (needed by phase 4).** The question is about an act of the part, so by the rulings annex its phase is the spine phase (`bc-docs:docs/development/platform-refactor-program/rulings.md:49`); ruling B19 itself, how the backlog is closed, stays needed by phase 11 (`rulings.md:151`). The queue has no date filter, so the part's runs and the backlog are one list.
- Options: (a) the part handles runs created from the date the operator approves this definition; older runs are carried by name to phase 11 under B19, and `status` shows the two counts apart; (b) rule B19 now and take the backlog into phase 4.
- Recommendation: (a). The part needs only that no new run strands; the backlog is a judgement of 602 cases (97 of them with no disposition, on the live read of 2026-11-19) that no step of phases 4 to 8 reads.
- What follows: under (a), V4's command gains the cut-off (V4, item 2), and no historical run is adopted or disposed in phase 4; the 602 stay as they are until phase 11, the 97 undisposed among them. Under (b), the Prove step of the part waits for the backlog.

**3. The operator-direct door.** Beside the panel, `POST /api/bcf/registry/concepts/authoring-recommendations` and `POST /api/bcf/registry/characteristics/admission-recommendations` let the operator be the maker, with no model (`bcf-business-concept-authoring-recommendation.service.ts:8-21`; `routes.snapshot.json:397, 405`); both decorated `platform_admin`. One path for each act is the method's rule (`platform-refactor-program.md:253`).
- Options: (a) one authoring command with the maker as a declared argument, panel or operator, ending in the same confirm; the two routes become that argument; (b) the panel only, and the two routes deleted; (c) both kept as separate acts.
- Recommendation: (a), the same answer the AI Definition recommends for the metric panel's supplied maker (its question 5). The operator-direct entry already ends in V2 and records itself as operator-direct.
- What follows: under (a), the guard of section 8 item 1 treats the two makers as one path; under (b), bc-admin's operator-direct screen (`bc-admin:src/api/business-concepts.ts:925`) is removed; under (c), the lock has two ways to author a concept, against the method.

**4. Characteristic admission and DEC-45c01b.** DEC-45c01b, decided, says a clean panel approval of a characteristic "auto-confirms the admission cert" and writes it at `draft`, with activation left to the operator (`bc-docs:docs/governance/adrs/ADR-45c01b.md:24`). The code makes characteristic admission wait for operator confirm (`registry-authoring-orchestrator.service.ts:126-138, 189-196`); no line of `src` cites the ADR.
- Options: (a) keep the code's way, operator confirm at admission and at publication; point 2 of DEC-45c01b is recorded as not in force by an amendment, the operator's act; (b) build DEC-45c01b point 2 in the Modify step of the part.
- Recommendation: (a). A characteristic is the meaning atom every concept on it inherits, and what runs today is the stricter rule.
- What follows: under (a), a decided record is amended, which is asked of the operator separately; each new characteristic costs him two acts, his confirm to admit it (V2) and his publication to put it live (V3), each with a rationale of 40 characters or more. Under (b), one act (V3), and the list that says which actions need his yes would change.

## 10. What this definition asks the operator to approve

1. The five acts of the part, V1 to V5, and the line drawn with AI, which is the AI Definition's, with the one authoring command built by L3 (section 1).
2. The rest, R1 to R11 and the surfaces named after the table of section 4, carried by name to phase 11.
3. The owners and hand-offs of sections 5 and 6, with no new stitch contract.
4. The assumption on roles until phase 9 (section 8).
5. The answers to the four questions of section 9.

Said plainly, for the recommended answers: you can no longer put a draft entity or concept live by hand (question 1); until phase 11 nothing can change the policy that would make additions wait for you (question 1); a decided record, DEC-45c01b, is to be amended (question 4); each new characteristic costs you two acts, your confirm (V2) and your publication (V3); and the Prove walk of one new concept runs the paid AI panel twice, asked for when it is to be done.

**What approving this definition does not do.**
- It changes no data and no setting, and adds no table or column; this worker found no schema change the part needs.
- It changes no one's role or permissions.
- It does not change the registry policy, and nothing in this part can.
- It makes no ruling on the 602 records sent to operator review (97 of them with no disposition, on the live read of 2026-11-19), and adopts or closes none.
- It amends no ADR; the DEC-45c01b amendment is asked for separately.
- It runs no AI panel and makes no paid vendor call.
- It puts no entity, concept or characteristic live, and leaves the one unfinished concept untouched.
- It does not approve the Definition of AI services, which is approved on its own; the line with AI here depends on it, including AI's question 3 on where the registry panel runs.

Until AI's fix of the verdict word is in (the AI Definition, A1 item 4), L3's commands accept both ways the panel writes the word REJECT.

## Where this definition differs from the Definition of AI services

There is no disagreement on the line between the functions. One sentence of the AI Definition must change so that the two agree on who builds the one command. Its A1, "What must change", item 3 reads: "The command is built, with its four verbs." It should read: "The command is built, with its four verbs, as the first step of L3's authoring command (V1 of the Definition of Vocabulary), which L3 builds, so that one call performs both, as A3's is shared with L6." Three points of detail:
- Its section 5 cites `functions-authoring-lanes.md:357` for the confirm act; the act is at line 356, and line 357 is the creation act whose activation claim question 1 corrects.
- Its section 5 calls the intake queue "the BCF intake queue" whose use is not established; this definition adds that its admission step was retired with the business-field catalog and carries it as R11, inferred dead.
- Its A1 `check` reports the duplicate and policy refusals; this definition records that the rules behind them are L3's, reported by the one command that L3 builds (section 1).

## What is not established

- Whether the registry policy in force stays as the Chief read it on 2026-11-19 ("What was checked"); the Audit step reads it again.
- The live state: the 602 runs and the one draft concept.
- Who authored the active `framework_policy` row, and whether any intake-queue row exists.
- Whether a panel-approved value concept can be identity-bearing (the run's identity role is stated for reference concepts only).
- Whether the TSK-29ce9c decision named in a code comment is a recorded grant, and who holds the `operator` role.
- Whether V1's resume of a failed activation can be built on the publication writer's resume without a new capability (V1, item 4).
- Not read: the prompt files; `recommendation.validator.ts`; the bodies of R1 to R5; the eight other operator-direct services; bc-admin page bodies; bc-db beyond one search; bc-portal; bc-infra.

**Facts of the gathering found wrong or incomplete.** The role refusal is not at `framework-approval/types.ts:43` (that line is the `GovernanceState` type) but at `framework-approval.service.ts:283-288`. Two DevHub scripts that call the confirm route (`_pass1-c2-confirm.mjs`, `_pass1-c5-confirm.mjs`) are not listed. `certification-record.write.repository.ts:14-16` cites only "the C5 sole-writer grep test", not the missing file by name. The gathering's claim that the panel may mint identity-bearing concepts holds for reference concepts only, as far as read. It omits DEC-45c01b, the decided ADR that the code contradicts, and the intake-queue routes. Not verified at source: the gathering's line references into `functions-in-brief.md`, `repositories.md` and the bc-db baseline, and its statements on the bodies of supersession, amendment and withdrawal.
