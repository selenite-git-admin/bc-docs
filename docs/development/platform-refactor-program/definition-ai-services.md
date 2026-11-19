---
id: platform-refactor-program-definition-ai
order: 45.14
title: "The Definition of AI Services, in Part"
status: drafting
authority: reference
depends_on: [platform-refactor-program, platform-refactor-program-definition-operations]
governing_sources:
  - Platform Refactor Program (the method; a function taken in part, ruling G40; commands; the order of work, phases 4, 6 and 11; the hand-offs between functions)
  - Function Dossiers (AI, AI services; L3, Vocabulary; L6, Metric Contracts and certification; L9, Chain integrity)
  - The Stitch Contracts
  - Vocabulary (slice 5, AI panels and their verdicts; group 4, certified; section 5, done)
governing_adrs:
  - DEC-71f15e (the Platform Refactor Program)
  - DEC-ffee4e (bc-ai retired; the registry authoring panel runs inside bc-core; the roster is calibration-locked)
  - DEC-53629b (the registry panel's moderator; amends DEC-ffee4e)
  - DEC-c48b0f (certification is a lifecycle act; a second panel before activation; rules before judgement)
  - DEC-d3b916 (a certification roster registration binds to DEC-c48b0f)
  - DEC-346ae7 (the three-part claim; the panel is a flagger)
  - DEC-09f86b (the metric authoring panel's judge seat)
  - DEC-e87701 (the metric panel's lower-cost roster)
errata_referenced: []
v2_sources: []
diagrams: []
---

# The Definition of AI Services, in Part

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md). It is the written definition that the Define step of function AI, AI services, calls for in phase 4, where ruling G39 takes AI **in part** and ruling G40 says what that means: the part is the acts this definition names, which the operator approves at the Define step; those acts pass all five steps and are locked; every other act and surface is carried here by name, with its phase, and none is dropped. A function locked in part is not locked for condition 1 of the finish. The operator's approval of this definition is the exit of the Define step. **This definition authorises nothing**: it describes, and every act it names that needs a grant is asked for when it is to be done.

## In plain words

- AI services is the set of AI panels: fixed groups of AI models that review a proposed business concept, a proposed metric, or a metric put up for certification.
- This definition takes five acts of it now, in phase 4, because every metric passes through them: running each of the three panels, and registering and calibrating the set of models that certification uses. Reporting what the vendors cost, and one unused panel, wait for phase 11.
- Even when these five acts are locked, AI services still counts as unfinished for the program's final test, until the rest is done.
- A metric passes certification today on the automatic checks alone. The AI panel's opinion is recorded; the code has a hook that would raise a flag where it disagrees, but nothing supplies the hook, so no flag is raised today; the panel does not decide. Two older texts say otherwise; question 2 asks what the part assumes.
- The code can still be switched to call an old AI service that was retired. Question 3 asks who removes that switch.
- No AI model in a panel may be changed without the operator's recorded sign-off, and nothing here changes one.

## How to read this definition

It is a design. It says what the part will be when it is locked in part; it does not describe what is done today. Each act in section 3 has four parts, as in the Definition of Operations.

- **Today** gives the facts the act starts from, each with its file and line.
- **The definition** states what holds once the part is locked.
- **What must change** lists the repairs the Modify step takes. An item marked **the operator's act** is on the hard line (a database change, a credential, a roster change): approving this definition does not approve it.
- **Carried** names what this act leaves to a later phase.

A statement marked **(inferred)** is a reading of the code or texts that no line states. Everything else is established at the line cited.

## What was checked, and by whom

A worker gathered the facts on 2026-11-19, read-only, from git objects at origin/main: barecount-devhub `artifacts/chief/AI-define-inputs-2026-11-19.md`. A second worker, who wrote this definition, opened at source every fact used here, at the commits below, and corrected the gathering where it was wrong (listed at the end of section 10). The Chief reads the whole before it goes to the operator. No database was queried, no route was called, no service and no panel was run, and no setting's value was read. Counts of rows quoted in the dossier are not repeated here: they were read on 2026-11-13 and are not re-read.

**Commits read.** bc-docs `6ecfdd0c`; bc-core `fd4b55ca`; bc-admin `d37b241`; barecount-devhub `3f4684fc`. bc-db, bc-infra and bc-portal were not read. Every bc-core citation below is at `fd4b55ca`.

## 1. What AI services is

An **AI panel** is a fixed set of AI models, each in a named seat, that answers one question about one case; the panels run inside bc-core; a panel "advises or decides only as far as its governing decision says; the operator's acts and the gates stay in force" (`bc-docs:docs/reference/vocabulary.md:619 @ 6ecfdd0c`). One seat drafts (the **maker**); the others challenge and decide (the **checker**, and a **moderator** or **judge**). The certification panel's seats are an **assessor**, an **adversary** and a **moderator** (`vocabulary.md:623-626`). The models in the seats are the **roster**, which is **calibration-locked**: it changes only with the operator's recorded sign-off (`vocabulary.md:635`).

Four panels exist, all in bc-core:

| Panel | Its question | Its record |
|---|---|---|
| registry authoring panel | May this act on the business concept registry be drafted? | `bcf.panel_output_record` |
| metric authoring panel | Is this metric contract draft admissible as written? | `mcf.metric_authoring_panel_run`, three transcripts, and an anchor row in `bcf.panel_output_record` |
| certification panel | Does the frozen metric package pass certification? | `mcf.audit_contextual_panel_run`; the decision in `metric_audit.decision` |
| ABC reasoning panel | Bounded reasoning in the ABC orchestrator (DEC-cff0cf) | none |

AI owns the calling of vendors, the rosters, the seats' prompts and the run records. It does not own what a verdict leads to: a registry write is L3's, a metric contract draft and its certification are L6's, the chain verdict is L9's (`bc-docs:docs/development/platform-refactor-program/functions-runtime-delivery-support.md:967 @ 6ecfdd0c` leaves this line "to be split"; this definition draws it in sections 3 and 5).

**What a panel decides, and where the texts disagree.**

- A registry or metric panel verdict is `APPROVE_FOR_DRAFT`, `OPERATOR_REVIEW` or a rejection. "Approved for draft" puts nothing in force (`vocabulary.md:673`).
- The certification panel's weight is stated three ways:
  - **It gates.** DEC-c48b0f point 3: "Certification gates activation" by "a certification record" (`bc-docs:docs/governance/adrs/ADR-c48b0f.md:26`). The vocabulary asks whether the package passes certification, "which gates the metric's activation" (`vocabulary.md:625`), and defines **certified** as "Passed by the certification panel" (`vocabulary.md:129`).
  - **It flags.** DEC-346ae7: "the AI panel is a flagger, not the correctness gate"; "A flag is never an auto-reject and never a required pass; the panel does not gate certification" (`ADR-346ae7.md:3, 6`, decided 2026-10-13).
  - **The code follows DEC-346ae7.** The decision code is the deterministic gate's verdict (`bc-core:src/registry/metric-audit/decision/certification-decision-writer.ts:190 @ fd4b55ca`), which is `PASS` only when the chain verdict is green (`certification-panel-decision.lane.ts:55-59`). The lane has an optional hook, `onPanelFlag`, which would raise an advisory `panel-flag` task, best effort and never blocking, when the decision passes and the panel did not verify (`lane.ts:94-99, 325-330`). Nothing supplies the hook: the service builds the lane's inputs without it (`certification-panel-decision.service.ts:34-40`), and the only two mentions of the name in `src` are `lane.ts:99` and `:328`. So no flag is raised and nothing is swallowed. **Corrected after the Audit step.**
- So the texts that define "certified" say the panel gates, the later ADR and the code say it advises, and the chain verdict, which the vocabulary says "gates nothing" (`vocabulary.md:136`), is what decides. Ruling B23 (function L6, L9; needed by phase 6) is the open question on this. Question 2 in section 9 asks what the part assumes until then.

## 2. The part and the rest, at a glance

| # | Act | Where |
|---|---|---|
| A1 | Run the registry authoring panel | the part (phase 4); a step with no route of its own, proven inside the Prove step of L3 in phase 4 (ruling G50) |
| A2 | Run the metric authoring panel (paid maker, or supplied maker) | the part (phase 4) |
| A3 | Run the certification panel, inside the certification decision | the part (phase 4); a step with no route of its own, proven inside the Prove step of L6 in phase 6 (ruling G50) |
| A4 | Register a certification roster | the part (phase 4) |
| A5 | Calibrate a certification roster | the part (phase 4) |
| R1 | Report vendor spend | carried to phase 11 |
| R2 | Record a panel run's cost in the ledger | carried to phase 11 |
| R3 | Replay the ABC reasoning panel | carried to phase 11 |

The expected list named "the certification panel decision" as one act. This definition splits that route: the panel run is AI's (A3) and the decision it feeds is L6's (section 5), because the decision's code is written from the deterministic gate alone (`certification-decision-writer.ts:190`), not from the panel. Acts A1 to A5 are the acts a metric of the spine passes through: a concept it binds is authored by A1, the metric by A2, its certification calls A3, and A3 refuses without a registered roster (`lane.ts:159-161`), which A4 writes from the evidence A5 produces. The rest serves cost and an unused panel, which no step of phases 4 to 8 reads.

**Where each act is proven (ruling G50).** The Prove step of the part covers A2, A4 and A5, by their three commands. A1 and A3 stay in the part and are locked with it, without a Prove of their own in AI: each is proven inside the Prove step of the function whose command calls it, A1 in L3's (phase 4) and A3 in L6's (phase 6), and each is carried by name with that phase. AI owns no step of the thread, so its Prove walks none.

## 3. The acts of the part

Each act gets one command with the four verbs: **status** (where the case stands and what is next), **check** (would the act be refused, and why, before any vendor is called), **do** (the act), **verify** (did it take effect, and which record shows it). The command is engine code; a session, the operator console and DevHub use it, and the other ways in are deleted (the method, "Commands").

### A1. Run the registry authoring panel

**Today.**
- Who: `platform_admin` or `operator` (`bc-core:src/registry/bcf/panel/registry-authoring-run.controller.ts:28 @ fd4b55ca`). Route: `POST /api/bcf/registry-authoring-runs` (`:24-39`).
- Before any model call, the run refuses a duplicate characteristic or concept with 400 (`registry-authoring-run.service.ts:90-120`) and refuses with 503 when no registry policy is active (`:68-73`). Then maker (with one repair turn), checker and moderator run in sequence (`in-process/in-process-registry-authoring-panel.client.ts:147-166, 174-214`). Grounding is `pass` or `quarantined`, and the sampling status is one of three values (`src/database/schema/bcf/panel-output-record.ts:83-90`).
- It records one `bcf.panel_output_record` and, in the same transaction, one `bcf.calibration_event` (`src/registry/panel-output-record.service.ts:11-21`).
- The same request then calls L3's orchestrator with the run's uid (`registry-authoring-run.service.ts:75-76`), which returns an outcome such as `parked`, `not_issued`, `awaiting_operator_confirm` or `authored` (`registry-authoring-orchestrator.service.ts:96-140`; the full list at `registry-authoring-panel.types.ts:454-667`).
- **Vendor failure.** Any seat error aborts the run with 503, and no panel record is written: "either the record is stored or there was no panel run" (`in-process-registry-authoring-panel.client.ts:16-18, 117-124`). The failed-run cost summary goes to the telemetry emitter, which writes only when the ledger gate is on (`bcf-telemetry-emitter.service.ts:77-81`; `bcf-ledger-env-gate.ts:27-37`). With the gate off, a vendor failure leaves a 503 and a log line only. A failed repair turn falls back to the first draft, and the shape error surfaces as `OPERATOR_REVIEW` (`client.ts:195-203`). Only the OpenAI client has a timeout (`panel-vendor-clients.ts:104-105`).
- **A second way exists.** The panel host is chosen by a setting: unless `BCF_PANEL_MODE` equals `in-process`, the module builds the HTTP client of the retired bc-ai (`registry-authoring-panel.module.ts:75-87`; `registry-authoring-panel.client.ts:41-51`). Callers of the route are bc-admin (`bc-admin:src/api/business-concepts.ts:760-764 @ d37b241`) and seven DevHub scripts (`barecount-devhub:scripts/_pass1-*-transport.mjs`, `_pass2-e1-transport.mjs`, `_pass2-e2-transport.mjs`, `_pass3-item-shelf-life-bc-binding-transport.mjs @ 3f4684fc`).

**The definition.**
- AI's act ends when the panel record is written, or when the run is refused or fails. What the orchestrator does with the record is L3's (section 5).
- One host: the panel runs inside bc-core. There is no setting that selects another host.
- `check` reports the duplicate and policy refusals before any vendor is called. The rules behind those refusals are L3's, reported by the one command that L3 builds (V1 of the Definition of Vocabulary). `do` returns the run uid and the panel verdict. `verify` reads the panel record and its calibration event.
- A vendor failure is always reported by the command: `do` names the seat and vendor that failed. Where the failure is recorded is what question 4 (section 9) decides.

**What must change.**
1. The HTTP client, `BC_AI_URL`, `BC_AI_TIMEOUT_MS` and the `BCF_PANEL_MODE` switch are deleted, in the function and step that question 3 names.
2. The DevHub scripts that post to the route are retired, or rewritten to call the command.
3. The command is built, with its four verbs, as the first step of L3's authoring command (V1 of the Definition of Vocabulary), which L3 builds, so that one call performs both, as A3's is shared with L6.
4. The verdict field gets a value rule, and one rejection spelling is chosen: the registry code writes `REJECT` (`registry-authoring-verdict.logic.ts:22`), the metric panel writes `REJECT_DEFECT` (`metric-authoring-panel.service.ts:453`), DEC-ffee4e names `REJECT_DEFECT` (`ADR-ffee4e.md:27`), and there is no CHECK on `verdict_code` (`panel-output-record.ts:47`). **Ruled at the Modify step (ruling B39):** `REJECT` is the one rejection value; the metric panel stores `REJECT` in this table, with the defect code at the top level of the payload, and keeps `REJECT_DEFECT` as the word of its seats. The schema change is one bc-db migration on `bcf.panel_output_record`: it widens the check on the defect code of a `REJECT` row to the 11 codes of `MCF_DEFECT_REGISTRY_V1`, and adds a value rule on the verdict field that names five older rows as allowed, each only with the verdict it holds today (ruling B43, which amends the words of ruling B39). It is written and proven on a restore, and not applied; the apply is asked for later, under the Database Change Protocol. A rejection with no defect code is refused before any write (ruling B40).

**Carried.** Separating operator-direct entries from panel verdicts in `bcf.panel_output_record` (vocabulary S5.6 defect 2) is a schema change on a table at its 20-column ceiling (`panel-output-record.ts:67`); it is L3's, with AI, in phase 11. The 602 runs awaiting operator review are ruling B19 (L3, phase 11).

### A2. Run the metric authoring panel

**Today.**
- Who: `mcf_author` (`bc-core:src/registry/mcf/mcf-panel-run.controller.ts:52-53, 109-110 @ fd4b55ca`). Two routes: `POST /api/mcf/panel-runs` (paid maker) and `POST /api/mcf/panel-runs/with-maker`, where the caller supplies the maker's envelope and only checker and judge are paid; the second refuses an envelope whose role is not `maker` (`:123-128`). The run starts from an intake row at `pending` (`metric-authoring-panel.service.ts:488`, `:1404`).
- It records one anchor row in `bcf.panel_output_record`, one `mcf.metric_authoring_panel_run` and three transcripts (`src/registry/mcf/metric-authoring/metric-draft-review-panel-run-writer.service.ts:20-27`).
- Verdicts are `APPROVE_FOR_DRAFT`, `OPERATOR_REVIEW` or `REJECT_DEFECT` (`metric-authoring-panel.service.ts:34`). A passing draft whose fixture check fails is sent to operator review with reason `fixture_cfx_failed` (`:1084`).
- **Vendor failure.** A failing seat gets a transcript with status `vendor_failure` or `vendor_timeout` and verdict `OPERATOR_REVIEW`, and the run goes on (`:990-1033`). A missing key is a `VendorConfigurationError` (`panel-agents/panel-agent-factory.ts:110-112`). The timeout is 180 s (`metric-authoring-panel.service.ts:93`). A status `cost_ceiling_exceeded` exists (`:997`), but `CostCeilingExceededError` is declared (`src/registry/mcf/panel-role-agent.interface.ts:203`) and never thrown in `src`. The status and its error class are in four files, at six places: `panel-role-agent.interface.ts:203`, `panel-payload.types.ts:33, 142`, `panel-payload.schema.json:72` and `metric-authoring-panel.service.ts:54, 997`. No stored row has it: the transcripts hold only `completed_with_verdict` and `vendor_failure` (live read, 2026-11-19).
- **Callers.** bc-admin calls the first route (`bc-admin:src/api/metricAuthoring.ts:76-80 @ d37b241`); DevHub's drive tool calls the second (`barecount-devhub:src/lib/metric-drive.js:200 @ 3f4684fc`); beside them sit three scripts. `bc-core:scripts/mcf-m12-first-real-run.mjs` calls no route: it builds the panel service and the agent factory from `dist/` (`:182-185`) and reads the vendor key values and `DATABASE_URL` from the `.env` file itself (`:55-70`). `scripts/mcf-m12-vendor-adapter-verification.mjs` builds the vendor factory from `dist/` (`:99, 148`) and reads the key values from `.env` as well (`:51-77`); the Definition's gathering did not name it. Nothing calls either; they are second ways to run the panel and to read keys, and are live scripts. `scripts/mcf/offpool-maker.mjs` is a harness that builds the supplied envelope and posts to the with-maker route (`:6, 24`).
- The vocabulary records that the supplied maker's evidence names a vendor, a latency and timestamps that did not occur (Invariant VI; TSK-9e0b6e) (`vocabulary.md:702`).

**The definition.**
- One act, one command, with the maker's source as a declared argument: the paid maker or a supplied envelope. The two routes are one path if question 5 so rules.
- AI's act ends at the run record. Drafting a metric contract from an approved run is L6's (section 5).
- `check` reports the intake's state, the re-run rule and a missing vendor key before any call. `verify` reads the run, its three transcripts and its anchor row.
- A seat's vendor failure is recorded in its transcript and sends the case to operator review, as today.

**What must change.**
1. The command is built; the two scripts that call the vendors and read keys from `.env` are deleted; DevHub's drive tool calls the command.
2. The supplied maker's transcript records only what occurred (question 5).
3. The status `cost_ceiling_exceeded` and its error class are deleted, since nothing raises them, no stored row has the status, and DEC-ffee4e point 2 deferred any budget cap (`ADR-ffee4e.md:26`). All four files, at six places, are deleted together. No reader of the status was searched for outside `src`.
4. The judge seat is stored as `moderator`, because the CHECK allows only maker, checker and moderator (`src/database/schema/mcf/metric-authoring-panel-transcript.ts:54`). **Corrected at the Modify step (ruling B41):** no schema change is made. All 553 judge rows already store `moderator`, so nothing is owed.
5. Header comments that are no longer true are corrected: the service says it writes `contract.panel_output_record` (`metric-authoring-panel.service.ts:18`); the writer says it is "NOT wired into any runtime entry point" (`metric-draft-review-panel-run-writer.service.ts:37-40`).

### A3. Run the certification panel, inside the certification decision

**Today.**
- Who: `mcf_publisher`, asserted literally, with no admin bypass (`bc-core:src/registry/mcf/mcf-certification-panel-decision.controller.ts:43, 53-58 @ fd4b55ca`). Route: `POST /api/mcf/metric-contract-versions/:mcvUid/certification-runs/:runUid/panel-decision`, with a `basis` of `EXACT_SNAPSHOT`, `EXACT_REPROOF` or `REPRODUCIBLE` (`:41-63`).
- Before any write it refuses, with a code: the version is not `audit_pending`; the run is missing, belongs to another version, is closed or already has a panel; no registered roster matches the wired seats; no current authority pin; the claimed basis is not what the recorded evidence supports (`src/registry/metric-audit/decision/certification-panel-decision.lane.ts:144-172`).
- Then, in order: the panel runs, its row is attached to the run, the run is completed, and the decision is composed, validated and written (`lane.ts:305-324`). The panel's own ruling is `PANEL_VERIFIED` or `PANEL_REJECTED` (`src/registry/mcf/audit-panel/audit-panel-rules.ts:80-81`); the decision code is the deterministic gate's (section 1).
- **Vendor failure.** Transport faults are retried at most twice (`audit-transport-retry.ts:19`). A refusal after the first write returns 422 or 500 with a receipt read back from the database (`controller.ts:77-97`). Whether a failed panel leaves a row was not established.
- **No second way** was found: the panel service is reached only through this lane and the calibration service (search of `src` and `scripts` for `AuditPanelExportService` and `AuditContextualPanelService`). The lane replaced a driver in a DevHub artifact that booted the whole engine to call the same steps (`lane.ts:9-12`).
- **The advisory flag is never raised.** The hook `onPanelFlag` (`lane.ts:99`) is never supplied (`certification-panel-decision.service.ts:34-40`), so when the panel flags a concern and the decision passes, the call at `lane.ts:327-330` does nothing. This corrects the earlier reading that a failure to raise the flag is swallowed. The hook, and its call, belong to the decision lane, which is L6's.

**The definition.**
- AI's act is the panel run: building the seats from the registered roster, calling them and writing `mcf.audit_contextual_panel_run`. The checks before it, attaching, completing and the decision are L6's, at the same route; the chain verdict the decision reads is L9's.
- The panel's weight is what question 2 rules. Until ruling B23, the act is stated as built: the panel's ruling is recorded and, where it disagrees with a passing decision, flagged; it decides nothing.
- `check` reports every refusal of the list above before any vendor call. `verify` reads the panel row and the decision that cites it.

**What must change.**
1. The command is built, shared with L6's decision command so that one call performs both (**(inferred)**: two commands for one route would be two ways in).
2. A vendor failure after the retries is reported with the seat and vendor named, and what it leaves recorded is stated.
3. The hook is supplied, so that the flag ruling B31 keeps is raised; today it never is. Once it is supplied, a flag that fails to be raised is reported by the command and not swallowed.

### A4. Register a certification roster

**Today.**
- Who: `mcf_publisher` (`bc-core:src/registry/mcf/audit-panel/audit-panel-roster.controller.ts:30-31, 59-60 @ fd4b55ca`). Routes: `POST /api/mcf/audit-panel/roster-registrations`; `GET .../roster-registrations/current`.
- The registration reads the seats the engine is wired to run ("env proposes") and records them with the calibration reference ("registration disposes"); it refuses an Anthropic seat, duplicate families, a malformed reference (`<path>=sha256:<64 hex>`) or a duplicate live registration; it is append-only (`:33-39`; `audit-panel-roster.service.ts:35-37`). A production write needs the reintake interlock and a `productionApply` block bound to the caller (`controller.ts:7-9, 45-47`). The row binds to DEC-c48b0f (`roster.service.ts:35`; DEC-d3b916).
- A missing key or an unbuildable wiring refuses with 422 (`controller.ts:53-55, 73-75`).
- No second way in production: the calibration service writes a bootstrap registration only on a scratch copy (A5).

**The definition.** One command. `check` reports what the registration would refuse. `do` registers. `verify` reads the live row and confirms the wired seats equal it. Registering is the operator's act in substance: it carries his acceptance of the calibration evidence (DEC-d3b916 point 3).

**What must change.** The command is built. The seats are read from the roster declaration of question 1, not from settings, if question 1 takes the declaration now. A stale comment that names a prior moderator beside the current constant is corrected (`audit-seat-factory.ts:72-81`).

**Carried.** The first real registration through the command `register-certification-roster` is carried by name to the next change of the certification roster, which is the operator's act, and no later than phase 11 (ruling G53, point (d)). Until then its `do` refuses with the code `roster_already_registered` wherever a live registration names the wired seats, which is so on the platform database (`bc-core:src/registry/mcf/audit-panel/audit-panel-roster.command.ts:181 @ 7d735a84`). The Prove step performs A4 by its status, check and verify verbs and by that named refusal.

### A5. Calibrate a certification roster

**Today.** `AuditPanelCalibrationService` runs the real seats over a fixture set on a scratch copy and writes the transcript a registration must cite; it refuses `bc_platform_dev` (`bc-core:src/registry/mcf/audit-panel/audit-panel-calibration.service.ts:9-19, 359-366 @ fd4b55ca`). It is a provider of the MCF module (`mcf.module.ts:343`) and has no route; no caller was found in bc-core `src` or `scripts`.

**The definition.** One command that runs only on a scratch copy and refuses the platform database, as today; its `verify` gives the transcript's path and hash in the form A4 requires.

**Why it is in the part.** A4 cannot be performed without its evidence, and any roster change in phases 4 to 8 needs it. A calibration calls the real, paid vendors, on a scratch copy of the database; each run is asked for when it is to be done, and approving this definition approves none. Whether it stays in the part is question 6 (section 9).

**Carried.** A defect left by the Modify step: the `do` verb of `calibrate-certification-roster` cannot succeed on any engine today. Its check refuses the platform database by name (`bc-core:src/registry/mcf/audit-panel/audit-panel-calibration.command.ts:220-225 @ 7d735a84`), and the engine's served-identity guard, applied to every platform session, refuses every database of another name (`bc-core:src/database/served-identity/platform-session-identity.ts:101 @ 7d735a84`, in the function `platformIdentityViolations`, `:87-103`). So no engine can reach the scratch copy the command needs. The repair, and the first real calibration through the command, are carried by name to the next change of the certification roster, no later than phase 11, and no calibration is run before then (ruling G53, point (c); DevHub task TSK-766e7b). The Prove step performs A5 by its status, check and verify verbs and by the named refusal of its `do` verb.

## 4. The rest, carried by name to phase 11

| Act or surface | Today | Why the spine does not need it |
|---|---|---|
| R1 Report vendor spend: `GET /api/vendor-costs` and DevHub's `devhub_vendor_cost_report` | No role on the route (`bc-core:src/platform/vendor-costs/vendor-costs.controller.ts:31-37 @ fd4b55ca`); stateless, computed on read (`vendor-costs.service.ts:1-10`); DevHub is a thin caller (`barecount-devhub:src/mcp-server.js:2871-2902 @ 3f4684fc`) | Cost is not authoring, certification, enabling or evaluation |
| R2 Record a panel run's cost: the in-run emit and `POST /api/ai-telemetry/bcf-panel-run/from-summary` | Two writers of `ai_telemetry.*`; both write only when `BCCORE_AI_LEDGER_WRITE` is `ENABLE` (`bcf-telemetry.controller.ts:47-59`; `bcf-ledger-env-gate.ts:27-37`); the metric and certification panels write no ledger row (no reference to `ai_telemetry` in `src` outside `registry/abc` and `bcf/telemetry`, other than the schema) | Ruling G21 decides how cost is recorded, in phase 11; no step of the thread reads cost |
| R3 Replay the ABC reasoning panel: `scripts/abc/phase1-replay.ts` and two desktop-maker scripts | No route; "NO HTTP endpoint" (`phase1-replay.ts:21`); the orchestrator replays a fixture through a mocked panel (`src/registry/abc/orchestrator/abc-orchestrator.ts:1-12`); the client keeps no record (`abc/panel/anthropic-model-client.ts:29`) | Ruling G22 decides whether it is kept; nothing in phases 4 to 8 calls it |
| The ABC price table and model map | `abc/panel/model-pricing.ts`; `anthropic-model-client.ts:10-16` | With R3 |
| The held copies of four AI records: `src/database/schema/contract/panel-output-record.ts`, `calibration-event.ts`, `authoring-panel-rejection-log.ts`, `certification-record.ts`, and four live `contract` tables | A second definition of the four records, held under the engine hold, imported with the whole `schema/contract` module (`src/database/control-plane.provider.ts:26`). The four tables hold 19, 19, 0 and 3,530 rows (live read, 2026-11-19); every key of the 19 panel rows is also in the `bcf` copy. Four foreign keys reference `contract.panel_output_record`, all from other `contract` tables: `authoring_panel_rejection_log`, `calibration_event`, `certification_record` and `intake_queue` (`schema/contract/*.ts`; the Chief's read of 2026-11-19) | Their removal is carried by name, not in phase 4: it needs the operator's exception for held files, a bc-db migration under the Database Change Protocol, and L3's decision on the intake queue (phase 11), which is L3's table. **Added after the Audit step.** |
| One vendor client for all panels; one roster record | Vendor clients are built in three files and ABC's own client (section 7) | Ruling G20, unless question 1 takes it now |
| The seven `docs/ai/` chapters, beyond the part's chapter | All seven describe bc-ai and none cites DEC-ffee4e (count 0 in each, `bc-docs:docs/ai/*.md @ 6ecfdd0c`) | The part's chapter replaces them for A1 to A5; the rest are marked history in the Lock change (see below) |

**The chapter of the part.** The Lock step merges one chapter for A1 to A5, marked locked in part, with vocabulary slice 5 kept nearly as is. The two program texts disagree on which `docs/ai/` files are history: the dossier marks `ai-usage-visibility.md` history and `ai-overview.md` and `ai-trust-and-verification.md` rewrite (`functions-runtime-delivery-support.md:1023-1024`); the chapter register marks `ai-usage-visibility.md` rewrite and the other six history (`chapters.md:179-185`). This definition follows the chapter register, the later reading: the six are marked history in the Lock change of the part, and `ai-usage-visibility.md` is carried to phase 11 with R1 and R2, as it describes what a tenant may see of AI usage.

## 5. What is not AI's

Each surface below writes from, or into, AI's records. It is named here so that none is left without an owner.

| Act | Route | Owner |
|---|---|---|
| What follows a registry panel record: certification record, registry write, the outcome kinds | inside `POST /bcf/registry-authoring-runs`, after the panel (`registry-authoring-run.service.ts:76`) | L3 |
| Confirm a high-risk registry act | `POST /bcf/registry-shape-certifications/confirm`, `operator` (`registry-shape-certification-confirm.controller.ts:39-40`) | L3 (`functions-authoring-lanes.md:356`) |
| Adjudicate or dispose a run sent to operator review | `GET /bcf/review-queue`; `POST /bcf/registry-panel-operator-adjudications`; `POST /bcf/registry-panel-runs/:panelRunUid/disposition` (`routes.snapshot.json:57, 386, 387`) | L3 (`functions-authoring-lanes.md:360`) |
| The eleven operator-direct `*-recommendations` routes | `routes.snapshot.json:392-409` | L3 (`functions-authoring-lanes.md:355`) |
| Write a panel record directly | `POST /bcf/panel-output-records`, `platform_admin` or `operator` (`panel-output-record.controller.ts:28`) | L3, proposed (no dossier places it). It has no caller in code: none in bc-admin `d37b241`, barecount-devhub `3f4684fc` or bc-core `scripts` at `fd4b55ca`, and its header names the retired bc-ai as the caller (`panel-output-record.controller.ts:7-9`). Operator-direct records are written by services that call `PanelOutputRecordService.create` (`panel-operator-adjudication.service.ts:131`), not through this route. The engine keeps no request log, so a caller outside those repositories cannot be ruled out. **Corrected after the Audit step.** |
| Route an intake entry from a panel result | `POST /intake-queue/:id/apply-panel-result` (`intake-queue.controller.ts:1-14`) | L3, proposed: it is the BCF intake queue; whether it is used was not established |
| Intake of a metric proposal | `POST /mcf/intakes` | L6 (`functions-authoring-lanes.md:750`) |
| Draft a metric contract from an approved run | `POST /mcf/panel-runs/:panelRunUid/materialize`, `mcf_publisher` (`mcf-materialization.controller.ts:33`) | L6 (`functions-authoring-lanes.md:752`) |
| Copy a run's knowledge profile | `POST /mcf/metric-contracts/:metricContractUid/knowledge-from-panel-run/:panelRunUid` (`routes.snapshot.json:490`) | L6, proposed (not in its acts table) |
| Request certification, open a run, the decision, admit | `routes.snapshot.json:480, 471, 472, 469` | L6 |
| The chain verdict the decision reads | `McvChainStatusService.judgeCandidate` (`lane.ts:55-56`) | L9 |
| Vendor keys reaching the engine | environment variables read at start (`panel-vendor-clients.ts:130, 233`; `panel-agent-factory.ts:61-74`) | OP |
| A key-shaped string in an archived script | `scripts/archive/decision-runs-2026/d299-populate-sap-aliases.mjs:12` (value not copied) | Items outside the program (evidence annex, row 17a) |

The reads of a run's record (`GET /bcf/registry-panel-runs/:panelRunUid`, `GET /mcf/panel-runs` and its two children, `POST /mcf/panel-runs/:panelRunUid/materialization-preflight`) are surfaces of A1 and A2: their `status` and `verify` verbs replace them. The first has no role (`routes.snapshot.json:44`; dossier); roles are ruled in phase 9 (G10, G11).

## 6. Hand-offs

| Neighbour | The part receives | The part hands on | Record |
|---|---|---|---|
| L3 | A candidate packet built from the registry and the active registry policy (`registry-authoring-run.service.ts:68-74`) | The panel record, with its verdict and recommendation, read by L3's orchestrator by uid (`:75-76`) | `bcf.panel_output_record` |
| L4 | Nothing | Nothing. L3's concept reaches L4 without AI (`functions-authoring-lanes.md:369`) | none |
| L6, authoring | An intake row at `pending` | A run record; on `APPROVE_FOR_DRAFT`, L6's drafting act reads it | `mcf.metric_authoring_panel_run` and its transcripts |
| L6, certification | An open run, a version at `audit_pending`, the frozen package | The panel row, attached by L6 to the run, and its ruling | `mcf.audit_contextual_panel_run` |
| L9 | Nothing directly; L6's decision reads L9's verdict | Nothing. DEC-c48b0f point 4 keeps from the panel what a rule can check (`ADR-c48b0f.md:28`) | `mcf.mcv_chain_status` (L9's) |

**No stitch contract names AI or a panel**: the word "panel" appears in the stitch contracts only where contract 5 leaves ruling B23 open (`stitch-contracts.md:177, 188`). This definition proposes **no new stitch contract**, for three reasons **(inferred)**. First, every hand-off above happens inside one request of one engine, through a record named in vocabulary slice 5; stitch contracts were written for hand-offs that bc-docs named and never defined. Second, the one undecided point, whether certification needs the panel, is already ruling B23 under contract 5. Third, the L3 and L6 Definitions, at their Define steps, state the same records from their side; the Chief checks that the three agree before any is approved. If the operator holds that the AI to L6 certification hand-off needs a contract, it needs a ruling before L6 is locked in phase 6.

## 7. Values written into code that Modify moves into declarations

| Value | Where |
|---|---|
| Panel host selector, default the retired bc-ai at `http://localhost:4300`, 180 s | `registry-authoring-panel.module.ts:75-87`; `registry-authoring-panel.client.ts:41-51`; `.env.example:46-56` sets `bc-ai`, while `bc-core:CLAUDE.md:141` says `in-process` is the default in `.env`; the running value is `in-process` (`bc-core/.env` line 20; the engine's secret holds no panel setting), established at the Audit step |
| Registry roster: maker `claude-opus-4-7`, checker `deepseek.v3.2`, moderator `zai.glm-5` on Bedrock, which is what runs (`BCF_PANEL_MODERATOR_PROVIDER=bedrock`, `bc-core/.env` line 21, as DEC-53629b decided); the code's default without that setting is `gpt-5.5-2026-04-23` on OpenAI (`panel-agents.ts:77-92`); token caps; maker region | `in-process/panel-agents.ts:37-93`; `in-process-registry-authoring-panel.client.ts:84-105` |
| Registry prompt version `registry-authoring/v1.5`; folders v1.3, v1.4, v1.5, with v1.5 loaded | `registry-authoring-verdict.logic.ts:27`; `panel-agents.ts:99`; `src/registry/bcf/panel/prompts/` |
| Registry verdicts and the nine defect codes, repeated in a database CHECK | `registry-authoring-verdict.logic.ts:21-40`; `panel-output-record.ts:30` |
| Vendor prices per 1,000 tokens, cache multipliers, models that refuse a temperature | `panel-vendor-clients.ts:58-102` |
| Vendor addresses and timeouts | `panel-vendor-clients.ts:104-105`; `panel-agent-factory.ts:65-76, 209`; `audit-seat-factory.ts:129, 137, 311` |
| Key names (names only) | `panel-agent-factory.ts:61-74`; `audit-seat-factory.ts:66-68, 86` |
| Metric roster: maker `claude-opus-4-7` as the code default, but the paid maker that runs is `claude-sonnet-4-6` by `MCF_M12_MAKER_MODEL` (`bc-core/.env` line 19), now ruled B38; checker `gpt-5.4-mini-2026-03-17`, judge `deepseek-v4-pro`; overrides `MCF_M12_*_MODEL` | `panel-agents/model-defaults.ts:67-88`; its header names other models (`:16-19`) |
| Metric prompt version `m12-panel-v1`; timeout 180 s; rejection reason of at least 20 characters | `metric-authoring-panel.service.ts:89, 93-94` |
| Certification seats: assessor `qwen.qwen3-235b-a22b-2507-v1:0`, adversary `deepseek.v3.2`, moderator `moonshotai.kimi-k2.5`; overrides `MCF_AUDIT_PANEL_*_MODEL` | `audit-seat-factory.ts:66-81` |
| Certification thresholds `PASS_THRESHOLD = 4`, `AGREEMENT_SPREAD = 1`; two retries; 2,000-token seat cap; prompt version `audit-seat-prompt-v15-first-cert-grain-only` | `audit-panel-rules.ts:24-25`; `audit-transport-retry.ts:19`; `audit-seat-agents.ts:27`; `audit-seat-prompts.ts:111` |
| Chain verdict to decision: green gives `PASS`, otherwise `REJECT` | `certification-panel-decision.lane.ts:55-59` (L6 and L9 own it; listed so that it is not missed) |

**The calibration lock.** A roster changes only with the operator's recorded sign-off (`vocabulary.md:635`; `ADR-ffee4e.md:25`; DEC-53629b "this amendment IS the required operator sign-off"). Moving a model name from code into a declaration is not a roster change when the declared value is the value that runs. Three disagreements make that value uncertain today: the registry moderator decided by DEC-53629b is `zai.glm-5`, while the code default is `gpt-5.5-2026-04-23` and only a setting gives GLM-5 (`panel-agents.ts:77-92`); the metric roster's header and constants differ (`model-defaults.ts:16-19, 67-74`); and the settings in force were not read. So the Audit step reads the running seats (done on 2026-11-19; see "Corrected after the Audit step"), and any declaration whose value differs from what DEC-53629b, DEC-e87701 or the live registration records is put to the operator as a roster change, never made as a cleanup.

## 8. What the part's lock will mean

1. Each of A2, A4 and A5 is performed by its command alone. A1 and A3 are steps with no route of their own, performed only through the commands that call them (L3's authoring command and L6's decision command); they are locked with the part and proven inside the Prove steps of L3 (phase 4) and L6 (phase 6) (ruling G50). A guard fails when a second route, script or host performs one of the five.
2. The panel host has no setting and no client that reaches bc-ai.
3. A vendor failure is reported by the command, with the seat and vendor named, in each of the three panels, and is recorded as question 4 rules.
4. The part's files pass the code rules; its commands are tested against a real database.
5. The part's chapter is merged, marked locked in part, and the six `docs/ai/` chapters named in section 4 are marked history in the same change.

## 9. Questions for the operator

Each is put as a proposed ruling. They were recorded on 2026-11-19 as rulings B18, B31, G42, G43, G44 and G45, on the operator's desk grant `2026-11-19T07-04-50-111Z-60d74091` (text SHA-256 `60d740912f88101600f84a3375f3310102c091a9e32ce4139762084c6a78e075`, desk request 523).

**1. Rulings G20 and B18, now or in phase 11.** G20 (AI: one vendor client and roster for all panels, or one each) and B18 (L3: the roster as data or code) are due in phase 11 (`rulings.md:150, 171`), but the Modify step of the part, in phase 4, moves values written into code into declarations, and the rosters are such values.
- Options: (a) decide both now; the part declares one roster record and one vendor client for A1 to A3. (b) Decide B18 now (each panel's roster as a declaration in data) and leave G20 (one client) to phase 11. (c) Carry both by name: in phase 4 the rosters stay in code, named on the lock list as a known exception, and phase 11 moves them.
- Recommendation: (b). The method moves values written into code into declarations, and the lock needs a guard that the seats which run are the seats declared; that needs B18 and does not need one shared client. Each panel's roster becomes one committed declaration in the engine's repository, read at start and compared with the running seats, with no new table. G20 stays in phase 11, where the vendor clients are joined with the cost record of G21.
- What follows: (a) the largest Modify, touching three vendor clients before the spine's metrics are authored; (b) a declaration per panel, read at start and checked against the running seats, with the clients untouched; where the two differ, the command's `check` refuses the panel run and names the seat, and the engine still starts; (c) the smallest phase 4, with the dossier's lock items 2 and 3 open until phase 11.

**2. The weight of the certification panel before ruling B23.** The vocabulary and DEC-c48b0f say the panel gates activation; DEC-346ae7 and the code make it advisory (section 1). B23 is due in phase 6, but A3 is locked in phase 4.
- Options: (a) lock A3 as built: the panel's ruling is recorded and flagged, and decides nothing; B23 may change that by reopening A3 under its ruling. (b) Decide B23's panel half now.
- Recommendation: (a), because it is what the code and the latest decided ADR say, and it fixes nothing B23 must change; the texts that say the panel gates (`vocabulary.md:129, 625`) are corrected by L6 when B23 is ruled.
- What follows: under (a), the part's chapter states the panel as a flagger with B23 named; under (b), A3's definition changes now and L6's Define step starts from it.

**3. The registry panel's host.** The code builds the HTTP client of the retired bc-ai unless a setting says `in-process` (section 7). L3's dossier also claims "the panel host has no default that points at bc-ai" (`functions-authoring-lanes.md:431`).
- Options: (a) AI deletes the client, its two settings and the switch at its Modify step in phase 4; L3's lock guard checks it. (b) L3 deletes them at its Modify step in phase 4.
- Recommendation: (a), because choosing the host is the calling of vendors, which AI owns.
- What follows: either way the deletion lands in phase 4, after the Audit step has read the running value of the setting; if that value is `bc-ai`, the change moves the host the panel runs on, and it is put to the operator for his recorded word before it merges.

**4. Where a registry panel vendor failure is recorded.** Today it leaves a 503 and a log line, unless the ledger gate is on (A1). The vocabulary's word is "vendor failure"; "unverified" is a source catalog word, not a panel word (`vocabulary.md:643, 677`).
- Options: (a) the part turns the ledger gate on, so the failed-run summary the code already builds is written; this touches G21's subject before phase 11. (b) The command's `do` reports the failure and DevHub records it in the session's evidence; nothing is written to the platform. (c) A failure record in the platform's own tables, which is a schema change.
- Recommendation: (b). It changes none of the engine's records in phase 4 and leaves the ledger to ruling G21. Once the part is locked the command is the only way to run the panel, so no failure is silent. The cost the operator accepts: until phase 11 a registry panel vendor failure is recorded in DevHub and in the engine's log, not in the platform's own tables.
- What follows: (a) a setting change, the operator's act, and ledger rows from phase 4; (b) no change to the engine's records, and the failure is reported and recorded only for runs through the command, which after the lock is the only way to run the panel; (c) a bc-db migration under its own grant.

**5. The supplied maker.** A2 has two routes, one where the caller supplies the maker's envelope, and the vocabulary records that its evidence names a vendor, a latency and timestamps that did not occur (TSK-9e0b6e).
- Options: (a) one command with the maker's source as a declared argument; the supplied envelope records itself as supplied, with no vendor or latency it did not have. (b) Retire the supplied maker; every run pays all three seats.
- Recommendation: (a), because DEC-e87701 decided the supplied maker for cost, and the defect is in what it records, not in its existence.
- What follows: under (a), the lock guard treats the two routes as one path behind one command; under (b), the `with-maker` route, DevHub's drive tool and the harness are deleted or rewritten.

**6. Calibration, in the part or carried.** A5 has no route and no caller today (section 3).
- Options: (a) A5 is in the part: its command is built and proven in phase 4. (b) A5 is carried to phase 11; whatever registration is in force when the Audit step reads it stays the roster of the spine, and no roster changes before phase 11.
- Recommendation: (a), because a registration cannot be made or replaced without calibration evidence, and the Audit step may find that the registration in force does not equal the wired seats, which is not established today.
- What follows: under (a), the Prove step of the part includes one calibration run on a scratch copy, which calls paid vendors and is asked for then; under (b), a mismatch found at Audit cannot be repaired by a new registration until phase 11.
- **Corrected at the Prove step (ruling G53, point (c)):** the Prove step of the part includes no calibration run. The command's `do` verb cannot succeed on any engine today (A5, Carried); A5 is performed by its status, check and verify verbs and by the named refusal of its `do` verb, and the first real calibration is carried to the next change of the certification roster, no later than phase 11. A5 stays in the part.

## 10. What this definition asks the operator to approve

1. The five acts of the part, A1 to A5, with their definitions in section 3, and the line drawn at each between AI and its neighbours.
2. The rest, R1 to R3 and the surfaces of section 4, carried by name to phase 11.
3. The owners named in section 5.
4. That no new stitch contract is needed (section 6).
5. The answers to the six questions of section 9.

Approving it approves no database change, no setting or credential change, no roster change, no calibration run and no panel run. Each of those is asked for when it is to be done. Named here so that none is hidden: one schema change that the Modify step asks for under the Database Change Protocol (a value rule on the panel record's verdict field, A1 item 4, ruling B39; the second change this paragraph named, storing the judge seat as `moderator`, is not needed, ruling B41); and, under question 3, a possible move of the host the registry panel runs on, if the running setting is found to name the retired service.

## What is not established

Established at the Audit step (2026-11-19; the Audit list is in barecount-devhub `artifacts/platform-refactor/ai/audit/`, with the live reads in `artifacts/chief/AI-audit-live-reads-2026-11-19.md`). These were listed here as open and are no longer:

- The running values of `BCF_PANEL_MODE`, of every model override and of `BCCORE_AI_LEDGER_WRITE`. Established at the Audit step: the host setting is `in-process`; the model settings are `BCF_PANEL_MODERATOR_PROVIDER=bedrock` and `MCF_M12_MAKER_MODEL=claude-sonnet-4-6`, and no other override is set; the ledger switch is not set, so the ledger does not write. Each was read from the engine's sources (`bc-core/.env`, the supervisor file) and from the engine's secret under desk grant `2026-11-19T07-16-30-058Z-94e3edfb`, which holds none of the panel settings. The values the running engine holds were read from those sources, not from the engine itself.
- Whether the live certification registration equals the wired seats. Established at the Audit step: it does; the one open registration names the same three models as the code's seats.
- That the calibration evidence file the registration cites exists and matches. Established at the Audit step: its hash matches the registration's.

Still not established:

- The row counts and stored verdict values of every table named here, except those read at the Audit step: the stored verdicts are `APPROVE_FOR_DRAFT` 2,124, `OPERATOR_REVIEW` 602, `REJECT` 12, `REJECT_DEFECT` 4 and `PASS` 1 (so both rejection spellings are stored); `mcf.metric_authoring_panel_run` holds 553 rows and `mcf.audit_contextual_panel_run` 81.
- Whether a certification panel that fails at its vendor leaves a row.
- Who calls any route. The engine keeps no request log: the logs of the supervisor and of the launch agents hold no request line for any route (the third read of grant `2026-11-19T07-16-30-058Z-94e3edfb`). So the host cannot show that a route is used or unused; callers are judged from the code of bc-admin, DevHub and the scripts. This is unanswerable from the host. No caller of `AuditPanelCalibrationService` was found in code, and whether `POST /intake-queue/:id/apply-panel-result` is used stays open for the same reason.
- Not read: the prompt files; `recommendation.validator.ts`; `panel-retry-eligibility.ts`; the calibration sampling; the framework-approval service; `vendor-costs.service.ts` beyond its header; the `docs/ai/` chapters beyond their counts; bc-db, bc-infra, bc-portal.
- Facts of the gathering found wrong and corrected here: the calibration service's refusal of the platform database is at `audit-panel-calibration.service.ts:359-366`, not `:57-67`; the ABC client's "No persistence" is at `anthropic-model-client.ts:29`, not `:38`; the L6 dossier's intake act is at `functions-authoring-lanes.md:750`, not `:760`, and its first open question at `:836`, not `:812`; the registry outcome kinds also include `already_authored` (`registry-authoring-panel.types.ts:575`); the certification seat factory's header agrees with its constants, but a comment above the moderator constant still describes a prior seat (`audit-seat-factory.ts:72-81`); the gathering's chapter table gave only one side of the disagreement on `ai-usage-visibility.md`.

## Corrected after the Audit step (2026-11-19)

The Audit step of function AI re-checked the facts of this definition at source and in the live reads. Each correction is made above, marked where it stands. No act, no part, no rest and no answer to a question is changed.

- F1: the advisory-flag hook `onPanelFlag` is never supplied, so no flag is raised and nothing is swallowed (section 1; A3, Today and item 3). Ruling B31 keeps the flag, so the Modify item is that the hook is supplied.
- F2: the direct panel-record write route has no caller in code, and its header names the retired bc-ai; operator-direct records are written by services (section 5).
- F3: a second, held copy of four AI record definitions, and four live `contract` tables, were not named; their removal is carried by name (section 4).
- F4: `cost_ceiling_exceeded` is in five places and no stored row has it (A2, Today and item 3). **Corrected again at the Modify step:** the status and its error class are in four files, at six places.
- F5: `mcf-m12-first-real-run.mjs` calls no route; it builds the service from `dist/` (A2, Today).
- F6: two live scripts read vendor key values from the `.env` file, `mcf-m12-first-real-run.mjs` and `mcf-m12-vendor-adapter-verification.mjs`; both are deleted at Modify (A2, Today and item 1).
- The registry moderator that runs is `zai.glm-5` on Bedrock, by `BCF_PANEL_MODERATOR_PROVIDER=bedrock`, as DEC-53629b decided; section 7 had quoted the code's default `gpt-5.5-2026-04-23`.
- The metric panel's paid maker that runs is `claude-sonnet-4-6`, not the code default `claude-opus-4-7`; it is ruled by B38 (section 7).
- The open list above: what the Audit established is moved out of it, and the missing request log is added.

## Corrected at the Modify step (2026-11-19)

The Modify step of function AI put its questions to the operator in one desk request, answered by grant `2026-11-19T09-33-25-342Z-e02128a0` (text SHA-256 `e02128a0296290174a0ccb5bc8f9bfeb944cd68a675794707a08e0e61105d18e`, desk request 530), recorded as rulings B39, B40, B41, G48 and B42 in the annex "The Rulings". The text of this definition is corrected in these places only. No act, no part, no rest and no answer to a question is changed.

- A1, What must change, item 4: the rejection spelling is ruled (B39): `REJECT`. The schema change is one migration on `bcf.panel_output_record`, written and proven on a restore and not applied.
- A2, What must change, item 4: the second schema change is not made, because all 553 judge rows already store `moderator` (B41).
- Section 8, the approval paragraph: one schema change is named, not two.
- A2, Today and item 3: `cost_ceiling_exceeded` and its error class are in four files, at six places, not five places.

## Corrected at the Prove step (2026-11-19)

The Prove step of function AI put its questions to the operator in one desk request, answered by grant `2026-11-19T16-52-07-670Z-e3fca09d` (text SHA-256 `e3fca09d4d42162ac35545de77190c3eb867d961d66b2b16acc0e5f6ad8bf36f`, desk request 537), recorded as rulings G50, G51, G52 and G53 in the annex "The Rulings". The text of this definition is corrected in these places only. The five acts of the part, the rest and the answers to the questions are unchanged, except as ruling G50 says where A1 and A3 are proven and ruling G53 says what the Prove step performs for real.

- Section 2, the table and the paragraph under it: A1 and A3 stay in the part; A1 is proven inside the Prove step of L3 in phase 4 and A3 inside the Prove step of L6 in phase 6 (G50).
- Section 8, item 1: A2, A4 and A5 are each performed by their command alone; A1 and A3 only through the commands that call them (G50).
- A4, Carried (new): the first real registration through the command, carried to the next change of the certification roster, no later than phase 11 (G53, point (d)).
- A5, Carried (new): the defect that the `do` verb of the calibrate command can succeed on no engine today, and its carry, with the first real calibration, to the next change of the certification roster, no later than phase 11 (G53, point (c)).
- Section 9, question 6, What follows: the Prove step includes no calibration run (G53, point (c)).
