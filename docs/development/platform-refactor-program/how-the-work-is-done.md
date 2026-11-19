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

### The command shape of the engine

This section fixes the shape that every command of bc-core takes. It describes the code as built, on bc-core `main` at commit `7d735a84`. Every pull request it names is merged there: the shared code of pull request 1064 (merge commit `37f9f035`, folder `src/common/command/`), the roster declaration and check of pull request 1066 (merge commit `0001515e`, `src/registry/ai-panel-roster/`), the registry panel step of pull request 1069 (merge commit `f7322337`), the commands of A4 and A5 and the shared changes of pull request 1068 (merge commit `d1ac544c`), the command of A2 of pull request 1070 (merge commit `d14e02d9`) and the certification panel step and the flag of pull request 1071 (merge commit `7d735a84`). **Corrected on 2026-11-19, at the Prove step of AI:** the earlier text of this section, checked at `f7322337`, called 1068, 1070 and 1071 open.

The function AI builds the first commands in phase 4. The functions L3, L4 and L6 build theirs on the same code.

#### What a command is on bc-core

A command is a set of four routes on the served engine, under one prefix:

| Verb | Route | Input |
|---|---|---|
| status | `GET /api/commands/<name>/status` | query fields that name the thing |
| check | `POST /api/commands/<name>/check` | a body, the same one `do` takes |
| do | `POST /api/commands/<name>/do` | the body |
| verify | `GET /api/commands/<name>/verify?reference=` | the reference that `do` returned |

There is no command-line form. The reasons:
- The operator console must use the same commands, and the console reaches the engine only over HTTP.
- DevHub already drives the engine over HTTP with a signed-in identity.
- A command run from a shell would take the actor from whoever types it. The engine takes the actor from the signed-in identity.
- A command line would be a second program holding the vendor keys and the database. That is a second host of each panel, which the lock of AI forbids.

Check is a POST only because it carries a body. It writes nothing.

#### What each verb does and returns

- **status.** Reads in a read-only transaction. Says where the thing stands and what is required next, in words. Calls no vendor and triggers no evaluation.
- **check.** Reads in a read-only transaction, so the database itself refuses a write. Calls no vendor and triggers no evaluation. Takes exactly the body `do` takes. Returns every refusal the act would meet now, not the first. The answer is HTTP 200 whether the act is allowed or not, because a refusal is an answer.
- **do.** Runs check first. If check refuses, `do` answers HTTP 409 with the same refusals and performs nothing. Otherwise it performs the act once and answers HTTP 201 with a reference to the record that proves the act: for `register-certification-roster` and `run-metric-authoring-panel` the uid of that record, and for `calibrate-certification-roster` the evidence reference of the transcript, `<path>=sha256:<64 hex>`, the form a registration cites (`audit-panel-calibration.command.ts:11-15`). All three commands built so far answer 201 on success.
- **verify.** Takes the reference `do` returned. Reads the records that prove the act. It is verified only when nothing is missing and at least one proof was found. A reference that proves nothing, or an unknown one, is answered as not verified, with a named refusal in `missing`. It is never a crash.

A body that is malformed, or that carries a field the command does not declare, is refused by the engine's own validation with HTTP 400. The guards answer 401 and 403.

The shared code gives each verb one answer object (`src/common/command/command-answer.ts`):
- status: `command`, `verb`, `subject`, `state`, `next`.
- check: `command`, `verb`, `allowed`, `refusals`, `notes`.
- do: `command`, `verb`, `outcome` (`done`, `refused` or `failed`), `reference`, `refusals`, `failure`, `flags`, `result`.
- verify: `command`, `verb`, `reference`, `verified`, `proof`, `missing`.

**The answer is the whole body.** The served engine wraps every returned value in `{ data, timestamp }`. A command answer is not wrapped. A command controller sends its answer through the raw response with `sendAnswer` (`src/common/command/command-http.ts`), which the wrapper leaves alone. The controllers of all three commands use it. Refusals and failures still go through the engine's exception filter.

#### How the read verbs are held read-only

The read verbs (status, check, verify) run in one read-only transaction on one dedicated connection. The code is `runReadOnlyOnDedicatedConnection` in `src/common/command/dedicated-connection.ts`.
- It uses the driver's own transaction scope, `$client.begin('read only', …)`, on the engine's postgres.js pool. The driver takes one connection, sends `BEGIN READ ONLY`, hands the body that connection alone and sends `ROLLBACK` when the scope throws.
- The wrapper throws a private marker at the end of the scope, so the transaction is rolled back in every case, and the body's value still comes out.
- It does not reserve a connection, because the tenant seam gate (`src/__architecture__/d575-tenant-tx-seam.spec.ts`) forbids `.reserve(` anywhere in `src`.
- A write made by a read verb is refused by the database itself (SQLSTATE 25006), not by this code.
- The earlier wrapper, `read-only-tx.ts` (added in 1064, sent `BEGIN`, the body and `ROLLBACK` through one executor), was deleted in 1068, so one wrapper remains.
- **A carried point: the status verb of `run-metric-authoring-panel` does not read only through this wrapper.** It reads the run, its transcripts and the intake row through `McfReadService`, the engine's shared read service, outside the dedicated read-only connection; only its re-run rule is read inside it (`metric-panel-run.command.ts:265-298`). Its check and verify use the wrapper. Carried by name as DevHub task TSK-77981c.

#### The refusal and the HTTP answers

A refusal has four members, all non-empty text: `code`, `reason`, `cure` and `rule_owner` (`command-answer.ts`; the builder `refusal` in `command-refusal.ts` throws on an empty member). The `rule_owner` names the function that owns the rule, for example AI, L3 or L6. One command can then report another function's refusals next to its own, each with its owner named.

- **409, refused.** `do` was refused by check. The answer carries the same refusals check reported (`runCommandDo` in `command-do.ts`).
- **502, a vendor seat failed.** The answer names the seat, the vendor and the model, with the message and a plain statement of what the platform left recorded (`VendorFailure` in `command-answer.ts`). An act signals this by throwing `VendorSeatError`. Any other error is not caught by the helper.

Both answers use the engine's existing error envelope, `application/problem+json`. The exceptions carry the answer in an `extensions` object. The engine's `ProblemDetailFilter` copies those members onto the top level of the problem body, so the members `command`, `verb`, `outcome`, `refusals` and `failure` sit beside the standard problem members (`command-refusal.ts`, `problem-detail.filter.ts`).

**502 has its own type and title.** The filter gives it the type `https://barecount.dev/problems/bad-gateway` and the title `Bad Gateway` (added in 1068).

#### Declared arguments, and the actor

- Every argument is a declared field of the body, validated by the engine's `ValidationPipe` with `whitelist` and `forbidNonWhitelisted`. An unknown field is refused. The body of check and the body of `do` are the same.
- The identifier of the thing acted on is a body field for check and `do`. For status and verify it is a query field: status of the metric panel run takes `intake_queue_uid` or `panel_run_uid`, and verify takes `reference`. It is never a path parameter, so a command has exactly four routes.
- The actor is never a body field. It is taken from the signed-in identity as the email, or the user id when there is no email (`actorFrom` in `command-contract.ts`). An identity with neither cannot act. The actor also carries the signed-in user id as an optional member, `userId`, for an act that records the id and not the email (added in 1068).
- Authentication stays the engine's: real sign-in, the global guards, and a declared role on every route. A command copies today's roles and changes none. Roles are ruled in phase 9.

#### Where the code lives

- **The shared code is `src/common/command/`.** It is owned by no function, as the register of shared code in the annex "Every Repository and Where It Belongs" has it. Its files: `command-answer.ts` (the answers), `command-refusal.ts` (the refusal and the two exceptions), `command-contract.ts` (the `Command` contract and the actor), `command-do.ts` (the helper that makes `do` run check first), `dedicated-connection.ts` (the read-only wrapper, which replaced `read-only-tx.ts` in 1068), `command-http.ts` (`sendAnswer`) and `command-conformance.ts` (the test helper), each with a spec; and `command-spec-support.fixtures.ts`, which holds the recording pool and the small HTTP application the controller specs use. There is no `index.ts`: a command imports the file it needs.
- **Each command lives in its function's folder** with its own controller. The command class has the four methods and no HTTP types. The controller parses the request, asserts the role and calls the method. There is no one controller that dispatches for all commands, because every function would then edit one file.
- **The roster declaration is AI's** (`src/registry/ai-panel-roster/`): one committed file of the three panels' seats and a check that the seats the code would run equal the declared seats (ruling B18). Every `check` of a panel command includes it.

#### How a command is proven

Each command has a spec that calls the shared helper `assertCommandConformance` (`command-conformance.ts`) over its own fixtures. The helper asserts that:
- check refuses the refusing input with complete refusals and no write and no vendor call;
- `do` on that input answers 409 with exactly the refusals check gave, and writes and calls nothing;
- a failing seat gives 502 that names the seat, the vendor and the model;
- verify of an unknown reference is a named refusal;
- status writes and calls nothing;
- an unknown body field is refused by validation.

Only the vendor seats are stubbed. The helper does not watch the database or the vendors itself: it reads two counters, writes seen and vendor calls seen, that the fixture's own stubs advance. A fixture whose stubs do not advance them proves nothing.

Proven as built (1068, 1070 and 1071):
- **The read-only transaction on one connection.** A recording-pool spec shows `BEGIN READ ONLY`, the body and `ROLLBACK` all run on the same connection and never on the pool, that two concurrent reads get two connections, and that the transaction is rolled back and never committed. An integration spec against real PostgreSQL (`dedicated-connection.integration.spec.ts`, added to the `e6b-db-integration` check of CI) shows the statements of one read run on one backend, that a write inside a read verb is refused by the database with SQLSTATE 25006 and writes nothing, and that the connection returns to the pool idle. On the head of 1068 the `e6b-db-integration` check passed.
- **A controller on the wire.** Each command controller has a spec that boots only that controller on a real HTTP port, with the global validation, the problem filter, the response wrapper and the roles guard around it. It shows the route set, the role, an unknown field refused (including an actor in the body), the actor taken from the signed-in identity, 200 on check, 409 with the refusals at the top level on a refused `do`, 201 on `do`, and that the answer is the body itself.

Still not proven:
1. **A command against the real platform schema.** The integration spec proves the wrapper on a probe table. The wire specs run the command over a recording pool and stub the services that write, so the SQL that the read verbs send to the platform tables has not run against real PostgreSQL.
2. **A command on the served engine.** No command has been called through the running engine with a real sign-in, and the three commands have not run a vendor seat for real. Nothing real was run for any of them.
3. **The 502 on the wire from a real seat failure.** The type and title are covered by a filter spec; no seat has failed for real under a command.
4. **The long act.** See "The long act".
5. **A calibration through the command.** The `do` verb of `calibrate-certification-roster` can succeed on no engine today. Its check refuses the platform database by name (`audit-panel-calibration.command.ts:220-225`), and the engine's guard on every platform session refuses every database of another name (`src/database/served-identity/platform-session-identity.ts:101`, in `platformIdentityViolations`). The repair is carried by ruling G53 to the next change of the certification roster, no later than phase 11 (the Definition of AI services, A5, Carried).

The real-database test of the commands belongs to the lock (part 3 of "How a lock works"). Until it exists, the command specs run on fixtures.

#### The commands and steps built so far

Three commands and two steps. Each wraps the existing service; none re-implements it.

| Name | Act | Routes | Role | Wraps | State |
|---|---|---|---|---|---|
| `register-certification-roster` | A4 | the four routes | `mcf_publisher` | `AuditPanelRosterService` | merged, 1068 |
| `calibrate-certification-roster` | A5 | the four routes | `mcf_publisher` | `AuditPanelCalibrationService` | merged, 1068 |
| `run-metric-authoring-panel` | A2 | the four routes | `mcf_author` | `MetricAuthoringPanelService` | merged, 1070 |
| registry panel step | A1 | no route | none | the registry panel client | merged, 1069 |
| certification panel step | A3 | no route | none | the certification panel run | merged, 1071 |

**register-certification-roster** (A4, ruling G45). Registers the certification panel's roster as the gate authority, citing the calibration transcript.
- Check returns every refusal the registration would meet: the shape of the calibration reference, the authorizer, the target database (a scratch database, or the production interlock with its block), the seats the engine is wired to run, their equality with the committed declaration (ruling B18) and a duplicate live registration.
- `do` registers once and returns the registration uid. Verify re-reads the row: it exists, is live, equals the seats wired now, and those seats equal the declaration.
- The recorded authorizer stays what the existing route records: the signed-in user id in the production block, and the email for the registration itself. The existing route `POST /api/mcf/audit-panel/roster-registrations` stays for now, as does its current-registration read.

**calibrate-certification-roster** (A5, ruling G45). Runs the certification panel's seats over the calibration corpus on a scratch copy of the database and keeps the transcript that a registration must cite.
- Check refuses before any vendor call: the source provenance, the platform database, the scratch-proof capability and allowlist, a scratch-guard claim that disagrees with the environment, a roster that does not build, and seats that differ from the declaration.
- `do` calibrates once with the real, paid vendors and returns the evidence reference that the registration requires: `<path>=sha256:<64 hex>`, the path and hash of the transcript, not a record uid. If a seat cannot be reached, the service records that in the transcript and the command answers 502 naming the first unreachable seat.
- Verify reads the transcript back from its reference and checks the hash again.
- No other route into the calibration service was found in `src` or `scripts`.

**run-metric-authoring-panel** (A2, ruling G44). Runs the metric authoring panel on an intake row.
- `maker_source` is a declared argument: `paid` (the panel's own maker seat runs) or `supplied` (the caller supplies the maker's output, and only the checker and the judge are paid).
- A supplied maker records itself as supplied: its stored identity says `supplied`, names who supplied it and when, carries a fingerprint of the transcript as received, and holds null for vendor, endpoint, times, latency, tokens and request ids. No schema changes. The service is not edited.
- Check reads only: the roster difference (B18), seats that cannot be built, the intake row's state, and then one of two rules: the re-run rule when `allow_retry` is set, or a run in flight when it is not (`metric-panel-run.prechecks.ts:88`). It never reports both.
- A seat that fails while it runs is recorded by the service as operator review. `do` then answers `done`, not 502, and adds a `panel_flag` when the park reason is partial transcripts. A configuration error before any seat runs is a 502 naming the seat, vendor and model. A rejection with no defect code (ruling B40) is a named refusal.
- Verify re-reads the run, its three transcripts and its anchor row and says whether they agree.
- The existing routes `POST /mcf/panel-runs` and `POST /mcf/panel-runs/with-maker` stay for now. Their callers are bc-admin, DevHub's metric drive and `scripts/mcf/offpool-maker.mjs`.

**The registry panel step** (A1, merged in 1069, `src/registry/bcf/panel/registry-authoring-panel.step.ts`). It is not a command and has no route. L3's authoring command calls it (rulings B32 and B34). It offers three functions:
- `checkPanel` reads only and returns every refusal the run would meet: the roster difference (B18), an unknown provider word (B42), a vendor key that is absent for a seat that needs one, and a role prompt that cannot be read. A key is checked by presence only, and a value is never read into a message.
- `runPanel` runs `checkPanel` and, if it refuses, throws `PanelStepRefusedError` with the same refusals before any vendor call. Otherwise it calls the panel client once and returns the run uid and the verdict. A seat failure is thrown as `VendorSeatError` naming seat, vendor and model, so the command can report it (ruling G43). The step adds no write.
- `verifyPanelRun` re-reads the record row by its uid and says whether its verdict is one of the three values that ruling B39 allows for a new row.
- Behaviour change: an unknown word in `BCF_PANEL_MAKER_PROVIDER` or `BCF_PANEL_MODERATOR_PROVIDER` used to resolve silently to the default. The roster check now refuses it by name, and the panel code stops a run with a 503 before any vendor call. A failed seat now raises `PanelSeatFailedException` (in `in-process/panel-seat-failed.exception.ts`), a subclass of the same 503 exception with the same message, that names seat, vendor and model.
- Today's registry run service is not rewired to the step.

**The certification panel step** (A3, merged in 1071, `certification-panel-step.ts`). It has no route. The decision command is L6's, in phase 6, and it will call the step. It offers four functions:
- `checkPanel`: every refusal before the first vendor call: the wired seats against the declaration (B18), seats that cannot be built (a missing key or region is named, its value is not), the wired seats against a live registration, the panel substrate and, when a subject is given, whether its frozen package can be put to the panel. It writes nothing and calls no vendor.
- `runPanel`: the panel run for one metric contract version. A seat that fails after its retries is reported with seat and vendor named and what the platform left recorded.
- `statusPanel` and `verifyPanelRun`: where a case stands, the stored rows that prove the panel ran, and the flag when it is due.
- A failed certification panel leaves no row: the row is written only after every seat has answered. That is unchanged.

#### The other ways in that still exist

The new commands do not remove the existing ways in. Each is deleted in a later step, after its callers move.
- `POST /api/mcf/audit-panel/roster-registrations` and its current-registration read (stays beside A4).
- `POST /mcf/panel-runs` and `POST /mcf/panel-runs/with-maker` (stay beside A2).
- The existing panel-decision route of the certification run (stays; see "Ruling B31's flag").
- The registry authoring run service, which does not call the new step yet.

#### Who uses the shape

- **AI** builds the first commands in phase 4: the three above, and the two steps.
- **L3, Vocabulary** builds the one authoring command of the registry (rulings B32 and B34). Its check returns the step's refusals followed by its own. Its `do` calls `runPanel` only when the maker is the panel, and a vendor failure goes into its own answer. The maker is a declared argument, `panel` or `operator` (ruling B34). The activation that ends authoring is L3's and follows ruling B32. Not yet built.
- **L4, Observation Contracts** builds the one door for writing an observation version (ruling B20).
- **L6** builds the commands of metric contracts and certification in phase 6, including the decision command that calls the certification panel step.

#### The long act

Ruling G49 (the operator, 2026-11-19; desk grant `2026-11-19T11-33-17-658Z-0d647f67`, text SHA-256 `0d647f672a8b81aa45ddf1810599d10d9c662ec429822a3d30c8c57c0de53f90`, desk request 532): in phase 4 the `do` verb of a command that runs an AI panel is synchronous. It answers when the panel run has ended (35 to 90 seconds as measured), and its answer carries the reference that the `status` and `verify` verbs take. The rule "A long act returns at once with a reference that can be asked for its status", in the rules for commands above, is not met by these commands in phase 4. It stays open by name, due no later than phase 11, and no background run mechanism is built in phase 4.

The commands as built answer when the act has ended: `do` returns once the seats have run. The code isolates that choice in each command's `do`, so a ruling can change it in one place.

#### Ruling B31's flag

Ruling B31 keeps the certification panel as a flagger: where its ruling disagrees with a passing decision, the decision is flagged. The flag is advisory and decides nothing. As built (1071):
- **The collector.** `CertificationPanelDecisionService.decideWithFlags` supplies the lane's `onPanelFlag` hook. The hook is an in-memory collector that cannot throw: its body is wrapped, and a failure of the collector itself is kept as a named problem (`flag_collection_failed` or `flag_not_collected`) and can never change the decision.
- **The condition** is the lane's own: the decision code is `PASS` and the panel's ruling is not `PANEL_VERIFIED`.
- **The existing decision route** returns its outcome as before and now returns `flags` and `flag_problems` beside it. When a panel run fails after the first write, its refusal body also carries `failedSeat`: the seat, model and family that was running, or null when no seat act threw (`mcf-certification-panel-decision.controller.ts:97`; `audit-panel-failed-seat.ts`). No caller of that route was found in bc-admin, DevHub or bc-core scripts. A due flag is a `panel_flag` with the subject and the two uids. DevHub records it as a panel-flag task when it drives the call. This follows the pattern of ruling G43, which has the command report a vendor failure and DevHub record it.
- **The step re-derives a due flag** from the stored decision and panel rows: a passing decision whose cited panel run did not end as verified. A flag raised through a caller that recorded nothing is therefore still shown by `statusPanel` and `verifyPanelRun`.
- No platform table is changed.
- **The lane file of L6 is not edited** (`certification-panel-decision.lane.ts`). Two points are carried to L6's Modify step in phase 6 by name: its comment near lines 95 to 97, which still says the production wiring emits a task and that a failure is swallowed, and the `.catch` near line 329, where its call swallows an error.
- **Not yet built:** the flag in the `do` answer of L6's decision command. That command is L6's.

Whether extending G43's pattern to B31 needs the operator is for the Chief to name in the Modify report.

## How a lock works

A **lock** is what keeps a finished function finished. It has four parts, and all four must be in place.

1. **A guard on doors.** A test in continuous integration lists the entry points that may perform the function's acts. It fails when another appears. bc-core already has this kind of test for retired modules, with a baseline that may only shrink.
2. **A guard on quality.** The function's files pass the code rules shown on DevHub's hotspots page, and the baseline for those files is set to zero failures.
3. **A contract test.** The function's commands are exercised against a real database in continuous integration, so a change that alters their behaviour fails.
4. **A locked chapter.** The chapter's status in bc-docs becomes `locked`. By the documentation's own rule, a chapter binds only when it is both authoritative and locked. A locked chapter changes only together with the code it describes, in the same pull request.

A lock is opened only by a ruling of the operator, recorded as a decision, and closed again by the same four parts.

By ruling G37 (the operator, 2026-11-18) Operations is not locked in phase 3: its Lock step stays open by name after that phase exits and is done when condition P3-C7 of phase 3 is met, as the main document states under "The method".

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

- **Fixed input.** One copy of the platform database, the database roles without their passwords, and the database of every tenant the engine's start-up check requires (ruling B1 as corrected), taken once, identified by its hash, and restored to a disposable database for each run.
- **Reference set.** The Kaveri tenant's metrics in two tiers: every value the tenant holds, as a baseline that shows a value has not moved; and the values worked out from the source system's own rows, apart from the rows the platform admitted, by queries that follow the platform's declared formula, each with its source; neither tier shows that a value is right. The set, the steps of a run and its limits are defined in the annex "The Definition of Operations", section 9, which replaces the earlier proposal of thirteen metrics.
- **Where it lives.** In the DevHub repository, outside the engine's repository, so that a change to the engine cannot change the thing that checks it.
- **The first run is a qualification.** The contracts have moved since the expected values were recorded. Whether today's engine reproduces them is unknown until the first run.

The reference run is built in the third phase of work. No engine code is modified before it exists and passes. The dossier for OP, Operations, records only that it is not built, and makes it a condition of that function's lock. Its design and its limits are written in the Define step of Operations.

**How the hold on the engine is enforced.** From phase 1, an automatic check on the engine's repository refuses any change to the files that produce values unless the operator has recorded an exception for that change. Once the reference run has passed once, the check instead requires that the reference run has passed on the exact commit proposed. That was to hold from the end of phase 3; the first reference run, on 2026-11-18, failed, and by ruling B2 the check stays as it is until a reference run has passed. The main document records the hash of the database copy, the engine commit, where each expected value came from, and the result of that first run. A passing reference run shows that values have not moved; it does not show that they are correct. Correctness is tested by comparison with a value worked out independently, which is part of "done" and of the test that ends the program.

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

**The model a worker runs on** (the operator's direction of 2026-11-19). A worker is started on the model its task needs, and the Chief names that model each time it starts one, because a worker otherwise runs on the Chief's own model. The default is Sonnet. Opus is used where the task is judgement: a steward, a check of a design, a hard review. No worker runs on the Chief's own model, whose weekly allowance is the limit of the program's bandwidth: by one worker's count from the local session transcripts, not recounted, workers ran on that model from 17 to 19 November 2026 and wrote about 3.9 million tokens on it; the transcripts record the model used, not whether it was inherited. The Chief keeps its own context short for the same reason: it gives a worker any task of more than a few reads, and resets at the exit of a step.

**What a step asks of the operator is asked together.** The acts of one step that need the operator's recorded approval go to the approval desk as one request where they can be decided together, and work that does not depend on the answer continues. In phases 1 to 3, by the Chief's count, at least one request was open for 41 of 115 hours.

**Before a step that ends in a real run,** the Chief checks, by reading only, that the run can pass on the data and contracts as they stand. **Before the operator is asked to approve a chapter,** a worker that took no part and has no memory files reads it against the commands, without performing an act that needs a grant.

**The hard line** is the set of acts that are never performed without a recorded approval from the operator: a change applied to a database; an act on data that cannot be undone; a change to cloud resources; and the writing of any credential. During the program the present approval rules stay in force for every other act as well, until ruling G1 is made.

## Risks

| # | Risk | What would show it | What the program does about it |
|---|---|---|---|
| 1 | The refactor becomes another loop: defining and re-defining with nothing locked. | A phase without a locked function after its first function's Define step. | Each step has an exit. The Chief reports the count of locked functions at every checkpoint. No new definition of "done". |
| 2 | Scope grows through "while we are here". | Work that belongs to no function and step. | The anchor requires each act to name its function and step. Anything else is listed for later. |
| 3 | A change to the engine alters a number unnoticed. | The reference run fails. | No engine change before the reference run exists; it runs at every Modify exit. |
| 4 | The guide becomes one more text beside the others. | A merged chapter with no retirement list. | A chapter merges only with its retirement list; the lock requires the replaced texts to be gone. |
| 5 | Delivery to a tenant is again left for later. | Phase 4 begins with stitch contract 2 or 6 unapproved. | The contracts are a phase 2 exit; phase 4 cannot begin without them. |
| 6 | The first reference run does not reproduce the recorded values. | The qualification run fails. | Ruling B2; the baseline is then set from evidence before any change. |
| 7 | DevHub work expands and delays everything. | Phase 1 without its exit after its Define step. | Phase 1 is limited to the items in its exit; the rest of DevHub is phase 17. |
| 8 | Context is lost between sessions, as before. | A session acts against this document. | The pinned anchor points here; the Chief's brief points here; DevHub holds the state. |
| 9 | Approvals for many small acts slow the work. | Waiting time at the approval desk. | Ruling G1; until it is made the present rules stand. |
| 10 | A committed credential is used by someone else. | Unexpected sign-ins or usage. | The operator rotates the two credentials, which sit on three lines [17a]; the files are removed in phase 3. |

## What happens to what exists

| Thing | What happens |
|---|---|
| The pinned anchor of the Demoed drive | Replaced by this program's anchor when the operator approves the pin at the approval desk. |
| `blueprints/goal.md` and `blueprints/demoed-terminal.md` | Kept as history. |
| The Chief's brief | Carries a first block pointing to this document. |
| The other controllers' briefs and the memory files | Unchanged until phase 17, except that each is checked against a chapter when its function is locked. No new program state is written to memory. |
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
- **A standing halt in bc-docs.** The chapter on the metric management system still says that no further metric is to be made active and no further vocabulary authored until a sequence completes. This program's hold replaces it; the text is retired in phase 6.
- **Instructions that are wrong today.** The project instruction file names a demo tenant that does not exist, a tenant route that refuses, a count of schemas that is too low (11 against a measured 22 [16a]), and a naming rule for boolean columns that the data does not follow (not re-checked; reported in artifacts/spine-review/DOCS-3A-implementation.md). They are corrected in phase 1.
- **The documentation reader** is broken on the build now being served. Its repair is not held and is done with the serving procedure in phase 3.
- **Open pull requests of the parked drive.** barecount-devhub 325 and 326; bc-core 1053 and 1054; bc-docs 206, 212 and 214. They are on the disposal list of phase 0.
- **Leftover worktrees, branches and open pull requests.** They are dealt with in phase 0, on a list the operator approves; see "Keeping the repositories clean".
