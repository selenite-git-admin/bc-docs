---
id: onboard-one-metric-to-the-metric-catalog
order: 52
title: "Onboard one metric to the Metric Catalog"
status: drafting
authority: authoritative
depends_on: [the-invariants, the-contract-grammar, the-evaluation-boundaries, the-authority-model, onboarding-overview]
description: "The order for one metric, from its seed to an active version in the Metric Catalog: 11 steps, each a decision or a link to one of the task chapters that does it in detail."
governing_sources:
  - The Contract Grammar
  - The Authority Model
  - The Evaluation Boundaries
governing_adrs:
  - DEC-79b62f (the Foundation gate: the repair locations and the four questions)
  - DEC-89db41 (the old metric corpus is input only; nothing in it carries trust into a new metric)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Onboard one metric to the Metric Catalog

*DevGuide · end-to-end guide · drafted 2026-11-24 · read only: nothing in this guide was run.*

Workflow on the board: PW009 Manage the Metric Catalog

> **Open question** (chapter 3). The resolve under the current binding may meet the canonical rows kept from the superseded binding (G14): read, not run; probe read-only first.

## Chapter 1. Overview

This chapter describes what the guide covers. The metric is onboarded to the Metric Catalog: its business concepts, its directory entry, its contract and its active version all live on the platform. The demo world is only the independent proof source: it computes its own values for the metric, apart from the platform, and the platform's values are proven against them. The guide gives the order and the decision points; each step links to the task guide that does it in detail.

### What the guide covers

This section lists the steps of the order.

- Read the seed and the old content (steps 1 and 2).
- Decide whether the business concepts exist, and onboard the missing ones (step 3).
- Decide whether a family and group fit, with a current version (step 4).
- Add the directory member (step 5).
- Author and approve the contract (step 6).
- Realize the member (step 7).
- Prepare the proof on the demo world (step 8).
- Request certification (step 9).
- Prove on the demo world (step 10).
- Certify and activate (step 11).

### The intent, in three points

This section states the intent that the guide serves.

- 1. The demo world LC5 holds a triaged, correctly calculated list of about 900 metrics.
- 2. The platform's old metric catalog and directory were confusing and could not be used; the bc-db 0079 reset deleted them on 2026-11-24, keeping a sealed copy.
- 3. The ~900 metrics are created and activated in the Metric Catalog, and the metric directory and the business concepts registry are kept consistent.

### The seven task guides

This section lists the task guides the order links to; each is one task done in detail.

- A. Onboard a business concept (PW064, PW065).
- B. Add a directory family and group (PW080).
- C. Add a directory member (PW008).
- D. Author and approve a metric contract (PW103, PW027, PW084).
- E. Link a directory member to its contract (realize) (PW081).
- F. Prove a metric version on the demo world (PW029, DW008, DW004, PW100).
- G. Certify and activate a metric version (PW026).

> **Note.** The old corpus is input only: nothing in it carries trust into the new metric (DEC-89db41). The example is customer invoice volume on the Kaveri demo world, cells KAVERI-IN FY2026-27 P01-P04; its old contract e6438795 was deleted by the reset, so it starts again from step 1.

> **Note.** Evidence base: served engine bc-core 83b37959 (main, served since 2026-11-24 08:1x IST), which carries 1097 (role guard: each role held literally, no administrator pass), 1098 (world identity), 1099 (pins per binding) and 1100 (the G1 proof, the declaration door, world scope, trials on request certification and certify, door descriptions). bc-core paths are under `src/`. Nothing in this guide was run. bc-db: 0051, 0075, 0076, 0078 and 0079 (applied live 2026-11-24).

**Next:** Chapter 2, Before you begin.

## Chapter 2. Before you begin

This chapter describes the conditions to check once per session, before the first step.

### Sign-in and roles

This section describes the sign-in and the roles the whole path needs.

- The session signs in with its own sign-in, never a shared administrator (blueprint C2; gap G13).
- Roles: `platform_admin` and `operator` (business concepts, directory), `mcf_author` (proposal, panel), `mcf_publisher` (draft, approve, declaration, certification, certify).
- Since bc-core 1097 (served) each role must be held literally: there is no administrator pass.

### Environment

This section describes the environment.

- Development only. Every command names its environment and refuses without one (blueprint C4).
- The tool checks the engine version it was written for (served today: bc-core 83b37959). Each new metric version needs its pin on the world label in code, then a serve move (gaps G5, G9).

### Grants

This section describes which acts are free and which need a recorded desk grant.

- Free: reads, trial runs and draft acts.
- Desk grant: every live write, the proof pin, certification and any cloud act; the command takes the recorded desk grant id and checks it against the desk (blueprint C3).
- The first real run of any new act is the owner's. Secrets never go in an argument. One desk request covers the live acts of a batch, posted before the owner's night.

### The state after the reset

This section states what the bc-db 0079 reset left on 2026-11-24.

- Deleted: every old metric contract, every directory member, the demo world's hand-over and custody, and every proof pin.
- Kept: the directory's 49 families and 143 groups with their versions (29 groups have no current group version), and the demo world's canonical rows of the superseded binding.
- Copied before the delete: the sealed read-only copy `bc_metric_raw_material` (no login yet, gap G6).

> **Important.** No database apply, live act, host change or credential write without a recorded operator grant. Never stop a program by a name pattern (pkill, killall).

**Next:** Chapter 3, The order and the decision points.

## Chapter 3. The order and the decision points

This chapter describes the order of the steps for one metric. Steps 3 and 4 are decisions: when the answer is yes, nothing is added and the next step follows. Every other step links to the task guide that does it.

> **Prerequisites**
> - The metric's seed id, from bc-demo `design/metric-coverage/triage-log.csv` (909 promote-full rows).
> - The roles of chapter 2.

> **Important.** Request certification (step 9) comes before the demo world's evaluation and proof (step 10): they read only a version that is audit pending (`USABLE_MCV_STATES`, `src/database/plane/plane-metric-version-binding.ts:177`), and carrying the proof over needs audit pending (bc-db `0076:384-386`). The earlier version of this guide had certification requested after the proof: wrong.

### Steps

#### Step 1. Read the seed

Read the seed the metric starts from (its triage row in the Foundry names the seed id).

**Actor:** anyone signed in on the platform scope. **Grant:** free (read).

**Inputs:** The seed id, from bc-demo `design/metric-coverage/triage-log.csv`.

- **CLI (planned):** `bc seed show <seed-id>`. Trial: not needed (read only)
- **API (today):** `GET /api/mcf/seed-ledger/:seedMetricId` (bc-core `src/registry/mcf/seed-metric-ledger.controller.ts:80`).
- **Writes:** nothing (read only)
- **Failure modes:** 404 "Seed metric not found".
- **Next:** step 2

#### Step 2. Read the old content

Read the old content of this metric, if any, from the read-only raw-material copy made before the reset.

**Actor:** the metric author (session). **Grant:** free (read).

**Inputs:** The old contract id. The copy `bc_metric_raw_material` exists and is sealed (bc-db 0079, applied 2026-11-24); it has no login yet.

- **CLI (planned):** `bc raw show <old-contract-id>` (planned). Trial: not needed (read only)
- **API (today):** **No door.** No bc-core code reads the copy, by design, and it has no read login yet (gap G6).
- **Writes:** nothing (read only)
- **Failure modes:** None yet (no door).
- **Note:** The old content is input only: nothing in it carries trust into the new metric (DEC-89db41).
- **Next:** step 3

#### Step 3. Decision: do the business concepts exist?

Decide: does every business concept the metric names (its grain entity, its measure, each discriminator) exist and is it active? If not, onboard each one, then come back.

**Task guide:** [Onboard a business concept, step 1](business-field-and-business-object-onboarding.md#step-1)

**Actor:** `platform_admin` and the literal `operator`. **Grant:** free for the check; desk grant to onboard.

**Inputs:** The concepts the metric needs, from its seed and old content.

- **CLI (planned):** `bc concept find …`, then `bc concept author …`. Trial: see the task guide
- **API (today):** Check: `GET /api/bcf/registry/entities?q=<text>`, `GET /api/bcf/registry/concepts/:conceptId` (active only). Onboard: task guide A.
- **Writes:** see the task guide
- **Failure modes:** See the task guide's failure modes.
- **Next:** step 4

#### Step 4. Decision: does a family and group fit?

Decide: does an existing family and group fit the metric, and does the group have a current group version? If no family or group fits, add one; if the group has no version, author it.

**Task guide:** [Add a directory family and group, step 1](add-a-directory-family-and-group.md#step-1)

**Actor:** operator or platform administrator. **Grant:** free for the check; desk grant to add or author.

**Inputs:** Step 3 done (the grain entity active).

- **CLI (planned):** `bc directory family list`, `bc directory group list`, `bc directory group version --group <id>`. Trial: see the task guide
- **API (today):** Check: `GET /api/metric-directory/families`, `GET /api/metric-directory/groups`. Version: `POST /api/metric-directory/groups/:groupId/version`.
- **Writes:** see the task guide
- **Failure modes:** See the task guide's failure modes.
- **Note:** 29 of the 143 live groups have no current group version (read 2026-11-24); a member cannot be added to them until it is authored (task guide B, step 2 and Appendix B).
- **Next:** step 5

#### Step 5. Add the directory member

Add the metric's directory member and its first member version.

**Task guide:** [Add a directory member, step 2](add-a-directory-member.md#step-2)

**Actor:** operator or platform administrator. **Grant:** desk grant (live write).

**Inputs:** Steps 3 and 4.

- **CLI (planned):** `bc directory member add --group <id> --code <code> --name <text> --from-spec <file>`. Trial: see the task guide
- **API (today):** `POST /api/metric-directory/members/from-spec`
- **Writes:** see the task guide
- **Failure modes:** See the task guide's failure modes.
- **Note:** After bc-db 0079 there are no members: every metric gets a new one.
- **Next:** step 6

#### Step 6. Author and approve the contract

Author the metric contract from the member and approve its first version.

**Task guide:** [Author and approve a metric contract, step 1](author-and-approve-a-metric-contract.md#step-1)

**Actor:** `mcf_author`, then `mcf_publisher`. **Grant:** free draft acts; desk grant to approve.

**Inputs:** Step 5 (the member uid).

- **CLI (planned):** `bc metric propose`, `bc metric author`, `bc metric draft`, `bc version approve`. Trial: see the task guide
- **API (today):** `POST /api/mcf/intakes` … `POST /api/mcf/metric-contracts/:metricContractUid/evaluate-publication-eligibility`
- **Writes:** see the task guide
- **Failure modes:** See the task guide's failure modes.
- **Next:** step 7

#### Step 7. Realize the member

Link the directory member to the approved version (realize).

**Task guide:** [Link a directory member to its contract (realize), step 2](link-a-directory-member-to-its-contract.md#step-2)

**Actor:** operator or platform administrator. **Grant:** desk grant (live write).

**Inputs:** Step 6 (the version approved: realize refuses a draft).

- **CLI (planned):** `bc directory realize --member <uid> --version <mcv-uid> --authority <ref> --rationale <text>`. Trial: see the task guide
- **API (today):** `PATCH /api/metric-directory/members/:memberUid/realize`
- **Writes:** see the task guide
- **Failure modes:** See the task guide's failure modes.
- **Note:** The order approve, realize, request certification is proven on a restore by bc-core PR 1100, now served (gap G1, task guide E).
- **Next:** step 8

#### Step 8. Prepare the proof (task guide F, steps 1 to 4)

Prepare the proof on the demo world: pin the version on the world label, let the demo world work out and hand over its own values, and declare the cells to prove.

**Task guide:** [Prove a metric version on the demo world, step 1](prove-a-metric-version-on-the-demo-world.md#step-1)

**Actor:** engine change; the demo world's login; `mcf_publisher`. **Grant:** engine code through the auditor; desk grants for the hand-over and the declaration.

**Inputs:** Step 6 (the new contract uid and version).

- **CLI (planned):** `bc world pin`, `bc world sheet work-out`, `bc world sheet hand-over`, `bc version declare-demoed`. Trial: see the task guide
- **API (today):** No door for the pin (gap G5); bc-demo scripts; `POST /api/commands/declare-demoed-version/do`.
- **Writes:** see the task guide
- **Failure modes:** See the task guide's failure modes.
- **Next:** step 9

#### Step 9. Request certification (task guide G, step 1)

Request certification: the version becomes audit pending. The demo world's evaluation and proof read only an audit-pending version.

**Task guide:** [Certify and activate a metric version, step 1](certify-and-activate-a-metric-version.md#step-1)

**Actor:** `mcf_publisher`, held literally. **Grant:** desk grant (live write).

**Inputs:** Steps 7 and 8.

- **CLI (planned):** `bc version request-certification --version <mcv-uid> --cohort <code>`. Trial: see the task guide
- **API (today):** `POST /api/mcf/metric-contract-versions/:mcvUid/request-audit`
- **Writes:** see the task guide
- **Failure modes:** See the task guide's failure modes.
- **Note:** A 200 answer with `computable:false` is a refusal: the version has no realization (step 7).
- **Next:** step 10

#### Step 10. Prove on the demo world (task guide F, steps 6 to 13)

Prove the version on the demo world: serve it, admit, stop it, resolve, evaluate without writing, record the proof, carry it over and read the Demoed record.

**Task guide:** [Prove a metric version on the demo world, step 6](prove-a-metric-version-on-the-demo-world.md#step-6)

**Actor:** operator, with the act's own login for each outside command. **Grant:** desk grants (cloud act, live writes, proof pin).

**Inputs:** Steps 8 and 9.

- **CLI (planned):** `bc world serve`, `bc demo admit`, `bc world stop`, `bc demo resolve`, `bc demo evaluate --trial`, `bc demo prove`, `bc version carry-proof`, `bc version demoed`. Trial: see the task guide
- **API (today):** Governed commands outside the served engine (gap G7); `GET /api/mcf/metric-contract-versions/:mcvUid/demoed-claim`.
- **Writes:** see the task guide
- **Failure modes:** See the task guide's failure modes.
- **Note:** Important: probe the resolve read-only first: it may collide with the canonical rows kept from the superseded binding (gap G14).
- **Next:** step 11

#### Step 11. Certify and activate (task guide G, steps 2 to 7)

Certify and activate the version, then read it back in the Metric Catalog.

**Task guide:** [Certify and activate a metric version, step 2](certify-and-activate-a-metric-version.md#step-2)

**Actor:** `mcf_publisher`, held literally. **Grant:** desk grant (certification; the first real certify is the owner's).

**Inputs:** Step 10 (the version Demoed).

- **CLI (planned):** `bc version certification-run open`, `bc version certification-run decide`, `bc version certify`, `bc metric show`. Trial: see the task guide
- **API (today):** `POST /api/mcf/metric-contract-versions/:mcvUid/certification-runs` … `POST /api/mcf/metric-contract-versions/:mcvUid/admit`
- **Writes:** see the task guide
- **Failure modes:** See the task guide's failure modes.
- **Next:** The next metric, from step 1.

**Next:** Chapter 4, Troubleshooting, if a step refused; otherwise the next metric, from step 1.

## Chapter 4. Troubleshooting

This chapter lists the refusals that come from doing the steps in the wrong order. Every other refusal is in the troubleshooting chapter of the task guide that does the step.

| refusal | step | do |
|---|---|---|
| 410 "Seed-primary intake creation is retired" | 6 | The proposal starts from a directory member: do step 5 first. |
| 400 "concept(s) absent or not active", or a member recorded as blocked | 5 | Step 3 is not done for one concept. |
| 400 "has no current Group Version" | 5 | Step 4: author the group's version. |
| 400 "state 'draft' is not realizable (needs approved\|active)" | 7 | Approve first (step 6). |
| 200 `computable:false` | 9 | A refusal: realize first (step 7). |
| "its state is 'approved'; requires … audit_pending, active or superseded" | 10 | Request certification first (step 9). |
| `w3_declaration` | 10 | Declare first (step 8). |
| 422 `demoed_absent` on certify | 11 | Carry the proof over first (step 10). |
| 403 "requires the mcf_publisher role — literally" | 9-11 | The sign-in lacks the literal role (G13). |

**Next:** Chapter 5, The task guides.

## Chapter 5. The task guides and their workflows

This chapter lists, for each step of the order, the task guide that does it and its workflow on the Workflows board.

| step | task guide | workflow |
|---|---|---|
| 1, 2 | this guide | PW082 Manage Metric Seeds |
| 3 | A. Onboard a business concept | PW064, PW065, PW005 |
| 4 | B. Add a directory family and group | PW080 |
| 5 | C. Add a directory member | PW008 |
| 6 | D. Author and approve a metric contract | PW103, PW027, PW084 |
| 7 | E. Link a directory member to its contract (realize) | PW081 |
| 8, 10 | F. Prove a metric version on the demo world | PW029, DW008, DW004, PW100 |
| 9, 11 | G. Certify and activate a metric version | PW026 |

**Next:** Appendix A, Gaps.

## Appendix A. Gaps that span the path, and where every gap is

This appendix lists the gaps that belong to the whole path, and then where each of the 32 known gaps is described. Kinds: engine code goes through the auditor; a database change needs the owner's yes; a credential is the owner's; a desk grant is a recorded grant.

| gap | where |
|---|---|
| G1 | Link a directory member to its contract (realize), Appendix A |
| G2 | Prove a metric version on the demo world, Appendix A |
| G3 | Prove a metric version on the demo world, Appendix A |
| G4 | Prove a metric version on the demo world, Appendix A |
| G5 | Prove a metric version on the demo world, Appendix A |
| G6 | this guide, Appendix A |
| G7 | Prove a metric version on the demo world, Appendix A |
| G8 | Prove a metric version on the demo world, Appendix A |
| G9 | this guide, Appendix A |
| G10 | each task guide, its own part |
| G11 | each task guide, its own part |
| G12 | this guide, Appendix A |
| G13 | this guide, Appendix A |
| G14 | Prove a metric version on the demo world, Appendix A |
| G15 | Prove a metric version on the demo world, Appendix A |
| G16 | Prove a metric version on the demo world, Appendix A |
| G17 | Add a directory family and group, Appendix A |
| G18 | Add a directory family and group, Appendix A |
| G19 | Add a directory member, Appendix A |
| G20 | Add a directory member, Appendix A |
| G21 | Add a directory member, Appendix A |
| G22 | Author and approve a metric contract, Appendix A |
| G23 | Onboard a business concept, Appendix A |
| G24 | Onboard a business concept, Appendix A |
| G25 | Onboard a business concept, Appendix A |
| G26 | Onboard a business concept, Appendix A |
| G27 | Onboard a business concept, Appendix A |
| G28 | Certify and activate a metric version, Appendix A |
| G29 | Certify and activate a metric version, Appendix A |
| G30 | Certify and activate a metric version, Appendix A |
| G31 | Link a directory member to its contract (realize), Appendix A |
| G32 | Certify and activate a metric version, Appendix A |

### G6. The tool's read of the raw-material copy

- **What:** The copy `bc_metric_raw_material` exists and is sealed (bc-db 0079, applied 2026-11-24); it has no login and no served code reads it, by design.
- **Smallest fix:** One named read command in the tool with its own read-only login on the copy, reading a contract by its old id.
- **Kind:** database change (owner's yes: the login) and a credential (owner); tool code

### G9. The serve move

- **What:** The served engine is 83b37959 (main), served since 2026-11-24 under grant 616: it carries 1097 (role guard), 1098 (world identity, resolver filter), 1099 (pins per binding) and 1100 (G1 proof, declaration door, world scope, trials, door descriptions). A version is named on the world only in code (G5), so each new metric version still needs an engine landing and a serve move.
- **Smallest fix:** One serve move per batch of pins, under its own desk grant, until the pin is data (G5).
- **Kind:** desk grant (owner)

### G12. DevHub's API registry cannot give a command its kind yet

- **What:** `devhub_api_list` gives each endpoint the union of tables its controller's services name, read or write.
- **Smallest fix:** Record tables written per route, so the kind of each command is generated, not hand-kept.
- **Kind:** DevHub code (normal lane)

### G13. The session's own sign-in and roles

- **What:** The whole path needs `operator`, `platform_admin` (business concepts), `mcf_author` and `mcf_publisher`; since bc-core 1097 (served) each must be held literally; the business concepts confirms and the certification doors check the literal role even at served.
- **Smallest fix:** The session sign-in (blueprint C2) with exactly these roles.
- **Kind:** credential (owner)

## Appendix B. Build list

This appendix lists the tool and the gaps together, one path, in order.

1. Done 2026-11-24: bc-core PR 1100 landed and served with 1097, 1098 and 1099 (83b37959): the G1 restore proof, the declaration door (G2), the two world-scope fixes (G3, G4), `dryRun` on request certification and certify (G10), door descriptions (G11).
2. The first metric's pin on the P01-P04 label once its contract and version exist (G5), in an engine landing through the auditor.
3. The serve move of that pin under its own desk grant (G9).
4. A read-only probe of the resolve against the kept canonical rows (G14), before any real run on the demo world.
5. The read login on the raw-material copy (owner's yes) (G6).
6. The tool's specification brought to the owner: the steps of the seven task guides as commands, kinds generated from the registry once it records tables per route (G12), exit codes, `--trial` where the engine has one.
7. The session sign-in with its roles (G13); the five outside commands wired as they are, each with its approval mark (G7).
8. The first metric through the tool: the demo world adds its query and study row and hands over again (G8); one desk request for the batch of live acts.
9. Before the batches: the pin as data (G5), the 29 group versions as needed (G17) and the study rows for the ~900 confirmed (G8).
