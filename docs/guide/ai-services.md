---
id: guide-ai-services
order: 46.28
title: "AI Services, in Part"
status: drafting
authority: authoritative
depends_on: [platform-refactor-program, platform-refactor-program-definition-ai, vocabulary, guide-operations]
governing_sources:
  - Platform Refactor Program (the method; a function taken in part, ruling G40; rulings B18, G43, G44, G45, B39, B40, G49, and G50 to G53)
  - The Definition of AI Services, in Part (the design this chapter must agree with), as amended at the Prove step
  - How the Work Is Done, section "The command shape of the engine" (the shape every command of bc-core takes)
  - bc-core at commit 7d735a8417209270e661addbfe716ef370db943f (the commands as built and as served)
  - Vocabulary (slice 5, AI panels and their verdicts)
governing_adrs:
  - DEC-71f15e (the Platform Refactor Program)
  - DEC-ffee4e (bc-ai retired; the panels run inside bc-core; the roster is calibration-locked)
  - DEC-c48b0f (certification is a lifecycle act)
  - DEC-d3b916 (a certification roster registration binds to DEC-c48b0f)
  - DEC-346ae7 (the panel is a flagger)
  - DEC-09f86b (the metric authoring panel's judge seat)
  - DEC-e87701 (the metric panel's lower-cost roster)
errata_referenced: []
v2_sources: []
diagrams: []
---

# AI Services, in Part

> **Status of this chapter.** It is a draft. The auditor has not reviewed it. What it says the Prove worker does is decided: the operator's rulings G50 to G53 (grant `2026-11-19T16-52-07-670Z-e3fca09d`, text SHA-256 `e3fca09d4d42162ac35545de77190c3eb867d961d66b2b16acc0e5f6ad8bf36f`, desk request 537), recorded in the annex [The Rulings](../development/platform-refactor-program/rulings.md) by bc-docs pull request 258. The operator's approval of this chapter's exact bytes for the Prove worker is asked separately (ruling G51) and is **not yet given**. AI services (function AI of the [Platform Refactor Program](../development/platform-refactor-program.md), decision DEC-71f15e) is taken in part in phase 4 and is not locked, so this chapter binds nothing yet.

## How to read this chapter

It is written for a worker that did not build the commands of AI services and is given only this chapter and the commands. For each call it gives the exact line, the body, the expected answer, every listed refusal, and what to do on any other answer.

- **The design** is the annex [The Definition of AI Services, in Part](../development/platform-refactor-program/definition-ai-services.md), and the shape of every command is in the annex [How the Work Is Done](../development/platform-refactor-program/how-the-work-is-done.md), section "The command shape of the engine". Where this chapter and either annex differ, the difference is a defect to report, not to resolve.
- **The code** is bc-core at commit `7d735a8417209270e661addbfe716ef370db943f`, cited as `bc-core:<path>:<line> @ 7d735a84`; a bare `<file>:<line>` refers to the file the section names. It was read from git objects only.
- **"Derived from the code, not yet observed"** marks every expected answer of a route. Nobody has seen the engine send it. If the engine sends something else, the worker stops; it never decides that the chapter was wrong and the engine right.

## What AI services is

An **AI panel** is a fixed set of AI models, each in a named seat, that answers one question about one case. The panels run inside bc-core. The models in the seats are the panel's **roster**; a roster is calibration-locked and changes only with the operator's recorded sign-off (Vocabulary, S5.2). AI services owns the calling of the vendors, the rosters, the seats' prompts and the records of each panel run. What a verdict leads to is not AI's: a registry write is L3's, a metric contract draft and its certification are L6's (Definition, section 1).

| Word | Meaning here |
|---|---|
| The engine | bc-core as served on this machine at `http://127.0.0.1:3100` (port table, DEC-e50b83) |
| Platform database | `bc_platform_dev`, the database of the served engine |
| Command | Four routes, `status`, `check`, `do` and `verify`, under `/api/commands/<name>/` |
| Refusal | One reason an act would not be performed: `code`, `reason`, `cure`, `rule_owner` (`bc-core:src/common/command/command-answer.ts:12-18 @ 7d735a84`) |
| Reference | The text `do` returns and `verify` takes |
| Seat | Maker, checker and judge on the metric authoring panel; assessor, adversary and moderator on the certification panel |
| Roster declaration | The committed file of each panel's seats (ruling B18; `bc-core:src/registry/ai-panel-roster/panel-rosters.json @ 7d735a84`) |
| The desk | The approval desk at `http://127.0.0.1:3040`, where the operator records a grant |
| The brief | The written instruction the worker is given with this chapter |

## The acts of the part, and what the Prove run does with each

The Prove step of the part covers A2, A4 and A5, by their three commands (ruling G50). A1 and A3 are steps with no route of their own; each is proven inside the Prove step of the function whose command calls it. AI owns no step of the thread, so its Prove walks none.

| Act | Command (role) | What the Prove worker does (ruling G53) |
|---|---|---|
| A1 Run the registry authoring panel | none: the step `RegistryAuthoringPanelStep` (`bc-core:src/registry/bcf/panel/registry-authoring-panel.step.ts @ 7d735a84`) | Nothing. Proven inside L3's Prove, phase 4 |
| A2 Run the metric authoring panel | `run-metric-authoring-panel` (`mcf_author`) | `status`, `check`, `verify` for real. One real `do`, on one pending intake row, only when the brief names a recorded grant that names the route, the intake row and the maker source |
| A3 Run the certification panel | none: the step `CertificationPanelStep` (`bc-core:src/registry/mcf/audit-panel/certification-panel-step.ts @ 7d735a84`) | Nothing. Proven inside L6's Prove, phase 6 |
| A4 Register a certification roster | `register-certification-roster` (`mcf_publisher`) | `status`, `check`, `verify` for real; one `do`, sent once, which refuses with 409 and writes nothing |
| A5 Calibrate a certification roster | `calibrate-certification-roster` (`mcf_publisher`) | `status`, `check`, `verify` for real; one `do`, sent once, which refuses with 409 and writes nothing |

The two refused `do` calls call no vendor and write nothing: `do` runs `check` first and, when it refuses, answers 409 with the same refusals and never calls the act (`bc-core:src/common/command/command-do.ts:22-28 @ 7d735a84`).

**Why no real registration or calibration is possible today.** The `do` of `calibrate-certification-roster` refuses the platform database by name (`bc-core:src/registry/mcf/audit-panel/audit-panel-calibration.command.ts:220-225 @ 7d735a84`), and the engine's served-identity guard, applied to every platform session, refuses every database of another name (`bc-core:src/database/served-identity/platform-session-identity.ts:101 @ 7d735a84`, in `platformIdentityViolations`, `:87-103`). So no engine can reach the scratch copy the command needs. The `do` of `register-certification-roster` refuses wherever a live registration names the wired seats, which is so on the platform database. Both first real acts are carried (see "What is carried"). The worker makes no scratch copy, starts no second engine and runs no calibration.

## The worker, and the hard line

The Prove worker is started outside the `barecount-devhub` folder, with no memory files (ruling G52). It opens no DevHub unit, holds no grant of its own, and posts, commits and pushes nothing. It reads the desk and posts nothing to it.

Never, in any form:

- a `do` other than the three this chapter names (the two refused ones, and the one panel run under its grant);
- a second call of any `do`, or of any call, to see whether it passes;
- a change of a setting, a vendor key, the roster declaration, a file of the engine or a database row; a start, stop or restart of a service;
- a call of another route, such as `POST /api/mcf/panel-runs`, `POST /api/mcf/panel-runs/with-maker`, `POST /api/mcf/audit-panel/roster-registrations` or `POST /api/bcf/registry-authoring-runs`.

## Before any call

### What is known of the engine

- The engine serves bc-core `7d735a84` since the serve move of 2026-11-19 at about 15:09 UTC (move record folder `~/bc-stack/serve-moves/20261119T150853Z-5bb730f2`). The three commands' routes are in that build (`bc-core:src/__architecture__/routes.snapshot.json:65-70, 418-423 @ 7d735a84`). A 404 on a command route is not expected; if one comes, stop.
- The served engine's database is the platform database. Migration 0072 of bc-db is applied on it since the same window.
- One live roster registration exists and names the three wired certification seats (read from the database on 2026-11-19).
- 127 intake rows were `pending` in `mcf.metric_authoring_intake_queue` on 2026-11-19. That count moves; the worker never relies on it.

### Sign-in

The brief names a file, readable only by its owner, that holds a bearer token of the demo user (ruling G52). In the lines below `<token file>` is that path. The worker passes the token to each call as `"Authorization: Bearer $(cat "$T")"`, inside the line, so that its value never appears in any output.

- Never `cat`, `echo`, `head`, `less` or copy the file by itself; never print `$T`'s contents; never use `curl -v`, `--trace` or `set -x`; never write the token into a report.
- First check the file without reading it:

      zsh -l -c 'T=<token file>; stat -f "%Sp" "$T"; stat -f "%Su" "$T"; id -un; echo "exit $?"'

  Expected: `-rw-------`, then the same user name twice, then `exit 0`. Anything else: stop and make no call.
- A call that answers **401**: stop. The token may have expired; the worker does not get another.
- A call that answers **403**: stop, and report the role the route needs (given in each command's section) and the problem's `detail`. Every route of the three commands also needs the platform scope (`bc-core:src/auth/guards/scope.guard.ts:40-47 @ 7d735a84`); `admin` or `super_admin` passes any role check (`bc-core:src/auth/guards/roles.guard.ts:34-37 @ 7d735a84`).

### The lines

Each line is run in a login shell, one at a time, and prints the answer's body, then `HTTP <code>`, then `exit <n>`. Every line below holds no single quote and goes inside the single quotes as it stands.

**Read line** (`status`, `verify`):

    zsh -l -c 'T=<token file>; curl -sS -m 30 -w "\nHTTP %{http_code}\n" -H "Authorization: Bearer $(cat "$T")" "http://127.0.0.1:3100/api/commands/<name>/<verb><query>"; echo "exit $?"'

**Post line** (`check`, and the two refused `do` calls; `<verb>` is `check` or `do`):

    zsh -l -c 'T=<token file>; curl -sS -m 30 -w "\nHTTP %{http_code}\n" -H "Authorization: Bearer $(cat "$T")" -H "Content-Type: application/json" --data-binary @<body file> http://127.0.0.1:3100/api/commands/<name>/<verb>; echo "exit $?"'

**Panel-run line** (the one real `do`, only under its grant):

    zsh -l -c 'T=<token file>; curl -sS -m 900 -w "\nHTTP %{http_code}\n" -H "Authorization: Bearer $(cat "$T")" -H "Content-Type: application/json" --data-binary @<body file> http://127.0.0.1:3100/api/commands/run-metric-authoring-panel/do; echo "exit $?"'

- **A body file** holds the body exactly as given here, with placeholders filled, in a folder of the worker's own outside every repository. It never holds a token or a key.
- `curl` exits 0 when it got an answer of any status. Exit 28 means the time bound was reached. Any exit other than 0 stops the run.
- A command's answer is the whole body, not wrapped in `{ data, timestamp }` (`bc-core:src/common/command/command-http.ts @ 7d735a84`). A 409, a 502 and every other error is a problem document (`Content-Type: application/problem+json`; `type`, `title`, `status`, `detail`, `instance`), and for 409 and 502 the members of the `do` answer sit beside them: `command`, `verb`, `outcome`, `reference`, `refusals`, `failure` (`bc-core:src/common/filters/problem-detail.filter.ts:92-106 @ 7d735a84`; `bc-core:src/common/command/command-refusal.ts:42-65 @ 7d735a84`).

### The answer of each verb

| Verb | HTTP | Members |
|---|---|---|
| `status` | 200 | `command`, `verb`, `subject`, `state`, `next` |
| `check` | 200, allowed or not | `command`, `verb`, `allowed`, `refusals`, `notes` |
| `do`, done | 201 | `command`, `verb`, `outcome` `"done"`, `reference`, `refusals` `[]`, `failure` `null`, `flags`, `result` |
| `do`, refused | 409 | `outcome` `"refused"`, `reference` `null`, the refusals `check` gave; nothing performed |
| `do`, failed | 502 | `outcome` `"failed"`, `reference` `null`, `failure` with `seat`, `vendor`, `model`, `message`, `left_recorded`; problem `type` `https://barecount.dev/problems/bad-gateway` |
| `verify` | 200, verified or not | `command`, `verb`, `reference`, `verified`, `proof`, `missing` |

`allowed` is `true` exactly when `refusals` is empty; `verified` is `true` exactly when `missing` is empty and `proof` holds at least one item (`command-answer.ts:83-85, 115-122`). A `proof` item has `record`, `key` and `value`; a `missing` item is a refusal. A refusal's `reason` and `cure` are reported, not compared.

### How a grant is read

Used for the approval of these bytes and, for the one panel run, for its grant. `<grant id>` is a grant's id; `<64 hex>` a SHA-256. These are the lines of [Operations](operations.md), "How a grant is read".

    zsh -l -c 'curl -sS -m 10 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3040/api/grants-list; echo "exit $?"'
    zsh -l -c 'curl -sS -m 10 http://127.0.0.1:3040/api/grants-list | ID=<grant id> jq -r ".grants[] | select(.grant_id == env.ID) | .grant_id, .method, .text_sha256"; echo "exit $?"'
    zsh -l -c 'curl -sS -m 10 http://127.0.0.1:3040/api/grants-list | ID=<grant id> jq -j ".grants[] | select(.grant_id == env.ID) | .text" | shasum -a 256; echo "exit $?"'
    zsh -l -c 'curl -sS -m 10 http://127.0.0.1:3040/api/grants-list | ID=<grant id> jq -r ".grants[] | select(.grant_id == env.ID) | .text"; echo "exit $?"'
    zsh -l -c 'curl -sS -m 10 http://127.0.0.1:3040/api/grants-list | H=<64 hex> jq -r ".grants[] | select(.text | contains(env.H)) | .grant_id, .method, .text_sha256"; echo "exit $?"'

1. Prints `200`. Anything else: the desk did not answer; stop.
2. Prints the grant's id, `method` and `text_sha256`, or nothing when there is no such grant.
3. Prints the SHA-256 of the text as the worker works it out. It must equal the `text_sha256` of line 2, and `method` must be `totp`; otherwise stop. `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` means an empty text: no grant of that id.
4. Prints the text, to be read. The worker cites a grant by its id and text SHA-256.
5. Finds every grant whose text names a given SHA-256, three lines each.

## The command `run-metric-authoring-panel` (act A2)

Runs the metric authoring panel once on one intake row. The maker's source is declared: `paid` (the maker seat runs) or `supplied` (the caller supplies the maker's output; only checker and judge are paid) (ruling G44; `bc-core:src/registry/mcf/metric-authoring/metric-panel-run.command.ts @ 7d735a84`). Role `mcf_author` on all four routes (`metric-panel-run.command.controller.ts`).

| Verb | Route | Input |
|---|---|---|
| status | `GET /api/commands/run-metric-authoring-panel/status` | query `intake_queue_uid` or `panel_run_uid`, a uuid, or none |
| check | `POST /api/commands/run-metric-authoring-panel/check` | the body |
| do | `POST /api/commands/run-metric-authoring-panel/do` | the same body |
| verify | `GET /api/commands/run-metric-authoring-panel/verify` | query `reference`: a panel run uid |

**The body** (`metric-panel-run.command.ts:62-68`): `intake_queue_uid` (a uuid, required), `maker_source` (`"paid"` or `"supplied"`, required), `allow_retry` (optional boolean), `supplied_maker` (an object, with `supplied` only). Any other field answers 400; the actor is never a body field (it is the signed-in email, or user id).

### status

- No query: `subject` `"none"`, `state` `{ "subject_kind": "none", "found": false }`, `next` `Give intake_queue_uid (an intake row) or panel_run_uid (a panel run), as a uuid.` (`:129-138`).
- `?intake_queue_uid=<uuid>`: `subject` `"intake <uuid>"`; unknown row: `state` `{ "subject_kind": "intake", "found": false }`; known row: `state` has `found` `true`, `intake_status`, `runnable_now` (`true` only for `pending`), `rerun_rule` (words, reported), `prior_run_count`, `latest_panel_run_uid` (`:280-298`).
- `?panel_run_uid=<uuid>`: `subject` `"panel run <uuid>"`; `state` has `subject_kind` `"panel_run"`, `found`, `verdict_code`, `defect_code`, `operator_review_reason`, `transcript_count` (`:265-278`).

### check

200, writes nothing, calls no vendor. Refusals, in this order: maker source, roster, seats, intake row (`:239-243`). With `supplied`, `notes` is the one line `The maker seat is not run and not compared with the roster: the supplied output stands in for it (ruling G44).` (`:143-146`); otherwise `[]`. Every refusal has `rule_owner` `"AI"`.

| Code | Meaning |
|---|---|
| `paid_with_supplied_maker` / `supplied_without_maker` | the maker source and `supplied_maker` disagree (`:100-106`) |
| `supplied_maker_role_invalid`, `supplied_maker_transcript_missing` | the supplied object is not a maker's envelope (`metric-panel-supplied-maker.ts:35-43`) |
| `declaration_file_missing`, `declaration_file_malformed`, `declaration_panel_missing`, `seat_not_running`, `seat_not_declared`, `seat_model_differs`, `seat_vendor_differs` | the running seats differ from the roster declaration (ruling B18); with `supplied`, the maker seat is not compared (`:246-251`) |
| `seat_not_buildable` | a seat cannot be built now, usually an absent vendor key (`:253-255`) |
| `vendor_diversity_violated` | with `paid`, the three seats name fewer than two vendors (`:256-261`) |
| `intake_not_found` | no intake row has that uid; no other intake refusal follows (`metric-panel-run.prechecks.ts:77-80`) |
| `intake_status_conflict` | the row is not `pending` (with `allow_retry`, not `consumed_by_panel`) (`metric-panel-run.prechecks.ts:82-87`) |
| `panel_retry_refused` | with `allow_retry` only: the re-run rule refuses (`metric-panel-run.prechecks.ts:53-60`) |
| `duplicate_proposal_in_flight` | without `allow_retry` only: a run for the same reservoir entry is approved for draft, or was made in the last ten minutes (`metric-panel-run.prechecks.ts:62-73, 88`) |

### do (the one real panel run)

Only under the grant described in "The order of the Prove run", step 5, and only after a `check` of the same body in the same run answered `allowed` `true`.

`do` runs `check` again, then builds all three seats before any seat runs, then runs them in order, maker, checker, judge (`bc-core:src/registry/mcf/metric-authoring-panel.service.ts:813-847 @ 7d735a84`). Each seat's time bound is 180 seconds (`:96`). A run has taken about 35 to 180 seconds; by the code a `paid` run can last up to about three times 180 seconds. The panel-run line therefore waits up to 900 seconds. **The call is sent once. It is never cut, never repeated and never retried**, whatever it answers: a `do` that is cut may still be recorded.

The writes, in one transaction (`metric-panel-run.command.ts:164-174`): one anchor row in `bcf.panel_output_record`, one row in `mcf.metric_authoring_panel_run`, three rows in `mcf.metric_authoring_panel_transcript`; on `REJECT_DEFECT` the intake row's state becomes `rejected` (`metric-authoring-panel.service.ts:466-468, 1346-1362`). On `APPROVE_FOR_DRAFT` and `OPERATOR_REVIEW` the intake row stays `pending`.

A fact the brief's grant has already weighed, on which the worker does not act: a rejection row with a metric defect code makes the rollback of bc-db migration 0072 refuse.

**Every outcome** (derived from the code, not yet observed):

| Answer | Meaning | Rows written | Then |
|---|---|---|---|
| 201, `outcome` `"done"`, `result.verdict_code` `APPROVE_FOR_DRAFT`, `flags` `[]` | the panel approved a draft | the five rows | `verify` and the two `status` reads below |
| 201, `"done"`, `OPERATOR_REVIEW`, `operator_review_reason` a reason, `flags` `[]` | the panel sent the case to review | the five rows | the same |
| 201, `"done"`, `OPERATOR_REVIEW`, `operator_review_reason` `partial_transcripts`, `flags` one item: `kind_code` `"panel_flag"`, `subject_uid` the run uid, `record_with` `"devhub_task"`, `detail.park_reason` `"partial_transcripts"` | a seat failed or timed out while it ran; its transcript records `vendor_failure` or `vendor_timeout` (`metric-panel-run.command.ts:193-206`) | the five rows | the same; the worker records nothing itself and reports the flag to whoever gave the brief |
| 201, `"done"`, `REJECT_DEFECT`, `defect_code` a code | the panel rejected the draft for a named defect | the five rows, and the intake row becomes `rejected` | the same |
| 409, one of `intake_not_found`, `intake_status_conflict`, `panel_retry_refused`, `duplicate_proposal_in_flight`, or any refusal `check` lists | the state changed between `check` and `do`; no vendor was called (`:209-217`) | none: the transaction was not committed | stop |
| 409, `reject_without_defect_code` | the panel's consensus rejected with no defect code (ruling B40); the vendors were called | none (`:218-220`; `metric-authoring-panel.service.ts:1156`) | stop |
| 502, `outcome` `"failed"`, `failure.seat` `maker`, `checker`, `judge` or `roster`, `left_recorded` `Nothing: the panel stopped before any seat ran and before any write, and the transaction was rolled back.` | a seat's configuration failed before any seat ran (`:221, 225-233`) | none | stop |
| any other status, or `curl` exit not 0 (28 included) | not named by the command | not known | stop; say that whether a run was recorded is not known; make no other call |

After a 201, in this order, with `<run>` the `reference`:

1. `verify?reference=<run>`: 200, `verified` `true`, `missing` `[]`, and `proof`, in order: `mcf.metric_authoring_panel_run` `panel_run_uid` `<run>`; `mcf.metric_authoring_panel_run` `verdict_code` equal to `result.verdict_code`; `mcf.metric_authoring_panel_transcript` `transcripts`, three `<role>:<status>` values for maker, checker and the judge (stored as `moderator`); `mcf.metric_authoring_panel_transcript` `maker_source` (`supplied`, or `not marked supplied` for `paid`); `bcf.panel_output_record` `verdict_code`; `bcf.panel_output_record` `verdict_form`, which is `REJECT (ruling B39 form)` for a `REJECT_DEFECT` run (`metric-panel-run.proof.ts:87-110`).
2. `status?panel_run_uid=<run>`: `found` `true`, `verdict_code` equal to the `do` answer's, `transcript_count` `3`.
3. `status?intake_queue_uid=<the row>`: `latest_panel_run_uid` `<run>`, `prior_run_count` one more than before the `do`, `intake_status` `rejected` and `runnable_now` `false` after `REJECT_DEFECT`, otherwise `pending` and `true`.

### verify

`GET .../verify?reference=<uid>`, on the read-only connection (`metric-panel-run.command.ts:155-162`). Refusals in `missing`: `reference_malformed` (not a uuid; an absent `reference` is read as empty text), `panel_run_not_found`, `transcripts_incomplete`, `supplied_maker_claims_vendor`, `anchor_row_missing`, `verdict_disagrees`, `defect_code_disagrees` (`metric-panel-run.proof.ts`). Any of the last five after a real run means the run record is not whole: report it and stop.

## The command `register-certification-roster` (act A4)

Registers the certification panel's wired seats as the roster in force, citing a calibration transcript (ruling G45). The seats registered are the seats the engine is wired to run, never seats in the body (`bc-core:src/registry/mcf/audit-panel/audit-panel-roster.command.ts @ 7d735a84`). Role `mcf_publisher` on all four routes (`audit-panel-roster.command.controller.ts:22`).

| Verb | Route | Input |
|---|---|---|
| status | `GET /api/commands/register-certification-roster/status` | none |
| check | `POST /api/commands/register-certification-roster/check` | the body |
| do | `POST /api/commands/register-certification-roster/do` | the same body |
| verify | `GET /api/commands/register-certification-roster/verify` | query `reference`: a registration uid |

**The body of the Prove run** (`:50-57`). `check` reads only the form of the reference, `<path>=sha256:<64 lowercase hex>` (`:141-145`; pattern at `audit-panel-calibration.service.ts:192`), and never opens the file, so a fixed well-formed reference is used. No `productionApply` block is sent.

    { "calibration_evidence_ref": "prove-run-probe=sha256:0000000000000000000000000000000000000000000000000000000000000000" }

### status

`state` (`:208-222`): `current_database`, `wiring`, `wiring_detail`, `wired_seats` (three items `seat`, `model`, `family`), `declaration_equal`, `live_registration_uid`.

**Expected** (derived from the code, not yet observed): 200, `subject` `"certification roster"`, `current_database` `bc_platform_dev`, `wiring` `buildable`, `wiring_detail` `the three seats build`, `wired_seats` `assessor`, `adversary`, `moderator` with the models of `panel-rosters.json` (`qwen.qwen3-235b-a22b-2507-v1:0`, `deepseek.v3.2`, `moonshotai.kimi-k2.5`), `declaration_equal` `true`, `live_registration_uid` a uuid, `next` `The wired seats are registered; nothing is required.` The `family` words are reported, not compared.

### check, and the refused do

`check` and `do` run the same function (`:108-116`, `:139-155`). Its refusals, in this order:

| Code | When |
|---|---|
| `calibration_reference_malformed` | the reference is not `<path>=sha256:<64 hex>` (`:141-145`) |
| `authorizer_missing` | the signed-in identity is under three characters (`:146-149`) |
| `scratch_target_refused` | no `productionApply` block, and the scratch-proof guard refuses: the capability is off, or the database is `bc_platform_dev`, or the allowlist is empty or omits it (`:157-168`; `bc-core:src/registry/mcf/metric-audit-workflow.service.ts:781-795 @ 7d735a84`) |
| `production_apply_refused` | a block was sent and the production interlock refuses it (`:157-168`) |
| `roster_not_buildable` | the seats cannot be built; no later refusal follows (`:188-195`) |
| the seven declaration codes | the wired seats differ from the declaration (`:176-178`) |
| `roster_already_registered` | a live registration names exactly the wired seats (`:179-184, 197-206`) |

**Expected for the body above** (derived from the code, not yet observed):

- `check`: 200, `allowed` `false`, `refusals` exactly `scratch_target_refused`, then `roster_already_registered`; `notes` `[]`. On the platform database `scratch_target_refused` comes whichever way the capability is set, since the guard refuses `bc_platform_dev` by name after the capability test; its `reason` says which test refused, and is reported.
- `do`, sent once with the same body file: 409, `outcome` `"refused"`, `reference` `null`, `refusals` the same two codes in the same order. Nothing is written; no vendor is called.

### verify

`GET .../verify?reference=<uid>` (`:224-263`). **Expected with the `live_registration_uid` of `status`** (derived from the code, not yet observed): 200, `verified` `true`, `missing` `[]`, four `proof` items, each `record` `mcf.audit_panel_roster_registration`: `registration_uid` (the uid), `calibration_evidence_ref`, `authorized_by`, `live` `"true"`. `authorized_by` names a person: the report says it is present and does not copy it. **Expected with no `reference`:** `verified` `false`, `missing` exactly `reference_malformed`.

Other refusals in `missing`: `registration_not_found`, `roster_not_buildable`, `wired_seats_differ_from_registration`, the seven declaration codes, `registration_not_live`.

## The command `calibrate-certification-roster` (act A5)

Runs the certification panel's real seats over the calibration set on a scratch copy and keeps the transcript a registration must cite (ruling G45). Today its `do` can succeed on no engine (see "Why no real registration or calibration is possible today"). Role `mcf_publisher` on all four routes.

| Verb | Route | Input |
|---|---|---|
| status | `GET /api/commands/calibrate-certification-roster/status` | none |
| check | `POST /api/commands/calibrate-certification-roster/check` | the body |
| do | `POST /api/commands/calibrate-certification-roster/do` | the same body |
| verify | `GET /api/commands/calibrate-certification-roster/verify` | query `reference`: an evidence reference |

**The body of the Prove run** (`audit-panel-calibration.command.ts:58-68`). The two hashes are the SHA-256 of each file's bytes at `7d735a84`, worked out with `git -C ~/MyProjects/bc-core show 7d735a84:<path> | shasum -a 256`; `check` tests their form only.

    {
      "harness_commit": "7d735a8417209270e661addbfe716ef370db943f",
      "source_hash_basis": "raw-git-blob-bytes",
      "corpus_file": { "path": "src/registry/mcf/audit-panel/audit-panel-calibration.fixtures.ts", "sha256": "18ec5f8e5152f4b93aa020302bfffcdab5cdb3df4fe9965b7f6aa642497668b7" },
      "service_file": { "path": "src/registry/mcf/audit-panel/audit-panel-calibration.service.ts", "sha256": "a0676d832702359d8e47c9a108064da6fc73d965db67197d4573a0ea8b6e5364" }
    }

### status

**Expected** (derived from the code, not yet observed; `:119-133`): 200, `subject` `"certification roster calibration"`, `state` `current_database` `bc_platform_dev`, `platform_database` `true`, `scratch_target_allowed` `false`, `wiring` `buildable`, `declaration_equal` `true`, `next` `Calibration runs only on a scratch copy listed in the scratch allowlist; this database is not one.`

### check, and the refused do

Refusals, in this order (`:210-251`): `source_provenance_malformed`; then either `platform_database_refused` alone (the database is `bc_platform_dev`) or `scratch_target_refused` and `scratch_guard_claim_mismatch`; then `roster_not_buildable` or the seven declaration codes.

**Expected for the body above** (derived from the code, not yet observed):

- `check`: 200, `allowed` `false`, `refusals` exactly `platform_database_refused`, `notes` `[]`.
- `do`, sent once with the same body file: 409, `outcome` `"refused"`, `reference` `null`, `refusals` exactly `platform_database_refused`. Nothing is written; no vendor is called; no transcript is written.

### verify

Reads a transcript file back by its reference; it reads no database (`:150-170`). **Expected with no `reference`** (derived from the code, not yet observed): 200, `verified` `false`, `missing` exactly `reference_malformed` (`audit-panel-calibration-transcript.store.ts:56-58`). Other refusals: `transcript_outside_store`, `transcript_unreadable`, `transcript_hash_differs`, `transcript_not_calibration`, `transcript_from_platform_database`.

## The order of the Prove run

One call at a time. Each answer is compared with its section before the next call. A listed answer is reported and the run goes on; any other answer stops it (next section).

**0. Before any call to the engine**, in this order. If one is not established, make no call to the engine; stop and say which.

1. **The bytes.** The brief names a commit of bc-docs and this file's SHA-256 there. `zsh -l -c 'git -C ~/MyProjects/bc-docs show <commit>:docs/guide/ai-services.md | shasum -a 256; echo "exit $?"'` must print the same 64 characters.
2. **The approval.** Grant line 5 with that SHA-256 finds a grant whose text approves this chapter as the chapter given to the Prove worker of AI services; lines 2 to 4 on its id show `method` `totp` and equal hashes. Report its id and text SHA-256.
3. **The token file**, by its check under "Sign-in".

**1. `register-certification-roster`:** `status`; `verify?reference=<live_registration_uid of status>`; `verify` with no query; `check` with its body; `do` with the same body file (expect 409).

**2. `calibrate-certification-roster`:** `status`; `verify` with no query; `check` with its body; `do` with the same body file (expect 409).

**3. `run-metric-authoring-panel`, reads only.** Expected answers derived from the code, not yet observed. `00000000-0000-4000-8000-000000000000` is chosen because no intake row is expected to have it.

| Call | Expected |
|---|---|
| `status` with no query | as in its section, `subject` `"none"` |
| `check` `{ "intake_queue_uid": "00000000-0000-4000-8000-000000000000", "maker_source": "paid" }` | 200, `allowed` `false`, `refusals` exactly `intake_not_found`, `notes` `[]` |
| `check` `{ "intake_queue_uid": "00000000-0000-4000-8000-000000000000", "maker_source": "supplied" }` | 200, `refusals` exactly `supplied_without_maker`, then `intake_not_found`; `notes` the one line of ruling G44 |
| `check` `{ "intake_queue_uid": "00000000-0000-4000-8000-000000000000", "maker_source": "paid", "actor": "x" }` | 400; the problem's `errors` names the field `actor` (`bc-core:src/main.ts:82-90 @ 7d735a84`) |
| `verify` with no query | `verified` `false`, `missing` exactly `reference_malformed` |

The `paid` probe expects no roster, seat or vendor refusal, which assumes the served metric seats equal the declaration and their keys are present.

**4. Report.** If the brief names no grant for a panel run, the run ends here, and the report says that act (b) of ruling G53 was not performed because no grant was named.

**5. The one real panel run** (ruling G53, point (b)), only when the brief names a grant id. Every expected answer in this step, and in the section of the command's `do`, is derived from the code, not yet observed.

1. Read that grant with grant lines 2 to 4. Its text must name the route `POST /api/commands/run-metric-authoring-panel/do`, one intake row uid, and a maker source. If it names `supplied`, the brief must also name a file holding the `supplied_maker` object and its SHA-256, which the worker checks with `shasum -a 256`; without it, stop. Anything missing or unclear: stop.
2. `status?intake_queue_uid=<row>`: `found` `true`, `intake_status` `pending`, `runnable_now` `true`. Note `prior_run_count`.
3. `check` with `{ "intake_queue_uid": "<row>", "maker_source": "<paid or supplied>" }` (with `supplied`, add `"supplied_maker": <the object>`): `allowed` `true`, `refusals` `[]`. Any refusal: stop; do not send `do`.
4. `do` with the same body file, on the panel-run line, once. Compare with "Every outcome".
5. After a 201: the three reads under "After a 201".

## What to do on an unexpected answer

**Any answer this chapter does not list stops the run:** an HTTP status the section does not give for that call; a refusal code not listed for that call, or listed codes in another order or with one missing; a member absent, unnamed or with a different compared value; a line whose exit code is not 0; a `do` answer not in its table.

**On a stop:** run nothing more, not the next call and not the same call again. Write the question down: what was called, the body as sent, what came back, and what this chapter said would come back. Give it to whoever gave the brief.

**Always:** never call a `do` to cure a `check`; never repeat a call; never change anything to make an answer clean; never copy into the report a value that looks like a key or a token (say where it was, and stop). Report each call with its method, route, body, HTTP status, answer and exit code, and say whether this chapter lists it.

## What is carried

Each item is carried by name; none is dropped.

- **A1**, the registry authoring panel step: proven inside L3's Prove, phase 4, through L3's authoring command (ruling G50).
- **A3**, the certification panel step: proven inside L6's Prove, phase 6, through L6's decision command (ruling G50).
- **The first real registration** through `register-certification-roster`: to the next change of the certification roster, the operator's act, no later than phase 11 (ruling G53, point (d)).
- **The calibration defect** (DevHub task TSK-766e7b): the `do` of `calibrate-certification-roster` can succeed on no engine. Its repair and the first real calibration, with the durable custody of its transcript (the code writes it under the engine's temporary folder, `audit-panel-calibration-transcript.store.ts:18, 45-53`, and no text names where it is kept), go to the next change of the certification roster, no later than phase 11; no calibration is run before then (ruling G53, point (c)).
- **The metric status read** (DevHub task TSK-77981c): the `status` of `run-metric-authoring-panel` reads the run, its transcripts and the intake row through `McfReadService`, outside the dedicated read-only connection (`metric-panel-run.command.ts:265-298`; How the Work Is Done, "A carried point").
- **The long act** (ruling G49): every `do` is synchronous in phase 4; the rule for a long act stays open, due no later than phase 11.

## What is not established

- **The real answers of every route.** None of the three commands has been called on the served engine with a real sign-in. Every expected answer of a route above is derived from the code: 27 in all (five for A4, four for A5, five probes of A2, and for the panel run two before `do`, eight outcome rows and three reads after it).
- **The sign-in.** Whether the demo user holds `mcf_publisher` and `mcf_author` (or `admin`), and the platform scope. If not, the first call answers 403 and the run stops.
- **The text of a 403 for a missing role.** Only the scope guard's text was read.
- **The served settings.** Whether the metric seats' vendor keys are present and equal the declaration, and how the scratch-proof capability is set, were not read. The first changes the `paid` probe; the second only the `reason` of `scratch_target_refused`.
- **How long a real panel run lasts.** About 35 to 180 seconds as reported; by the code up to about three times 180 seconds for `paid`.
- **Other writes of the panel service** to the intake row besides the rejected state were not traced.
- **The certification seats' authority.** The declaration names `DEC-05815d; DEC-d3b916` for the certification seats (`panel-rosters.json:22`), while the registration row binds to `DEC-c48b0f` (`audit-panel-roster.service.ts:39`); whether they should agree was not established.

## Sources

- bc-docs, read through git on 2026-11-19: `docs/guide/operations.md` at `origin/main` (for form and the grant lines); at `df6c0ee03a06e10a218e4510a8b438e1a48678de` (the head of pull request 258), `docs/development/platform-refactor-program/rulings.md` rows G40 and G50 to G53, and the changes there to `definition-ai-services.md`, `how-the-work-is-done.md` and `repositories.md`.
- bc-core at `7d735a8417209270e661addbfe716ef370db943f`, read through git objects only: `src/common/command/`; the three commands and their controllers; `metric-panel-run.prechecks.ts`, `metric-panel-run.proof.ts`, `metric-panel-supplied-maker.ts`; of `metric-authoring-panel.service.ts`, the constants, the seat order, the rejection update and ruling B40's test; `audit-panel-calibration.service.ts` (the reference pattern), `audit-panel-calibration-transcript.store.ts`; `assertScratchProofTarget` in `metric-audit-workflow.service.ts`; `platformIdentityViolations` in `src/database/served-identity/platform-session-identity.ts`; `roles.guard.ts`, `scope.guard.ts`, `problem-detail.filter.ts`, `main.ts`. The two SHA-256 values under A5 were worked out from the blobs at that commit.
- Given by the brief of this revision, not read by its writer: the serve move of 2026-11-19, the database name of the served engine, the apply of migration 0072, the live registration, the count of pending intake rows, and the effect of a rejection row on the rollback of 0072.
- Not read: the desk, DevHub, the served engine, any database, any setting or secret.
