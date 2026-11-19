---
id: platform-refactor-program-definition-observation-contracts
order: 45.16
title: "The Definition of Observation Contracts"
status: drafting
authority: reference
depends_on: [platform-refactor-program, platform-refactor-program-definition-operations, platform-refactor-program-definition-ai, platform-refactor-program-definition-vocabulary]
governing_sources:
  - Platform Refactor Program (the method; commands; the hold on the engine; the order of work, phases 4 and 5; the hand-offs between functions)
  - Function Dossiers (L4, Observation Contracts; L3, Vocabulary; L5, Canonical Contracts; L7, Readers and connections)
  - The Stitch Contracts (contracts 1, 2, 3 and 10)
  - The Contract Grammar (Observation Contract); The Invariants (III, IV, VI)
  - Vocabulary (S2.4, the states of the contracts other than metrics; S2.6, defects)
  - Observation Contract Creation, the onboarding chapter
governing_adrs:
  - DEC-71f15e (the Platform Refactor Program)
  - DEC-5fd322 (the observation contract is the design-time artifact; readers bind to it)
  - DEC-0e3c64 (the observation contract belongs to the canonical side of the chain)
  - DEC-4a17e0 (each field mapping carries a governed concept identity)
  - DEC-585edb (a `sum` reduce strategy for joins in the observation grammar; in conflict with activation)
  - DEC-f4084d (one governed call authors a chain: publish-chain, source stack, resolver)
  - DEC-fbc085 (each state change of an observation version writes one append-only transition row)
errata_referenced: []
v2_sources: []
diagrams: []
---

# The Definition of Observation Contracts

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md). It is the written definition that the Define step of function L4, Observation Contracts, calls for in phase 4, where ruling G39 takes L4 **whole**, after AI in part and L3 in part. Every act of L4 is named here and passes all five steps; no act of L4's own is carried to a later phase. Surfaces that touch L4 but are another function's are named in section 5 with their owner, or, for one of them, with the step that names its owner. The operator's approval of this definition is the exit of the Define step. **This definition authorises nothing**: it describes, and every act it names that needs a grant is asked for when it is to be done.

## In plain words

- An observation contract says how one source table is read: which fields, which business concept each field carries, and which rows. A reader binds to one exact version of it, and a canonical contract reads that version.
- Four ways can write a version today. This definition keeps one: L4's own command. Publish-chain, DevHub's tool for it and the harness's observation branch are deleted. A larger call that also builds the reader and the canonical contract stays, split now: its observation step uses L4's command, its reader steps are L7's and the rest is L5's (question 1).
- Today a version can go into force with no review, and one person can write, approve and put in force the same version. Question 2 asks that every version pass review, with the approver's identity recorded. One person may still approve their own version; the record shows it. The bulk route can no longer move observation versions. A version that was approved but then cannot be put in force is returned to draft.
- When a new version comes into force, the old one stays in force. A 48-hour mark is written and nothing ever acts on it. Question 3 asks how an old version ends. If it ends at once, every canonical contract that reads it stops resolving until it is re-pinned. The recommended answer avoids that, at a price: an old version stays in force for as long as something still reads it, with no end date, so **one contract can have several versions in force**, and the dossier's rule of at most one is dropped for L4. Until the nightly cycle is given that step (Runtime's work, phase 7), a person or a session ends old versions.
- Some of L4's files are on the list of files held while the reference run cannot pass. Changing them in phase 4 needs your recorded exception for each change. Question 4 asks whether to make those changes now (two exceptions), or wait until the run passes in phase 5.
- Every observation contract carries a second state field that has never been kept true. Question 5 asks whether it is removed. Removing it also changes the act that cleans up an abandoned chain run, which reads that field.
- Question 6 asks how an observation contract is removed. The recommended answer: a test contract can be removed, a governed one is only archived, never removed. Today the database has no mark for a test observation contract, so under that answer **none can be removed at all**; one made in error is archived and stays.
- Under the recommended answers, two database changes follow: a rule on the version's state values, and (question 5) the removal of the parent field. Each is asked for when it is to be done; approving this definition approves neither.

## How to read this definition

It is a design. It says what L4 will be when it is locked, not what is done today. Each act in section 3 has four parts, as in the Definition of AI services.

- **Today** gives the facts the act starts from, each with its file and line.
- **The definition** states what holds once L4 is locked.
- **What must change** lists the repairs the Modify step makes. An item marked **held** touches a file under the hold on the engine (section 7). An item marked **the operator's act** is on the hard line (a database change, a change to an ADR, a stored meta-schema): approving this definition does not approve it.
- **Carried** names what the act leaves to another function, with its phase. No act of L4's own is carried; shared surfaces are handed to their owners (section 5).

A statement marked **(inferred)** is a reading of the code or texts that no line states. Everything else is established at the line cited.

## What was checked, and by whom

A worker gathered the facts on 2026-11-19, read-only, from git objects at origin/main: barecount-devhub `artifacts/chief/L4-define-inputs-2026-11-19.md`. A second worker, who wrote this definition, opened at source every fact used here and corrected the gathering where it was wrong (listed at the end). The held files were computed again with the engine's own guard code (section 7). An independent cold reader then opened about 115 of the citations and found 7 wrong, plus gaps (barecount-devhub `artifacts/chief/L4-definition-cold-read-2026-11-19.md`). Each finding was verified at source, from git objects at the same commits, before it was applied; one detail it gave was not taken (the closure's family list is at `contract.service.ts:895`, not 896). The workers queried no database. The Chief read the whole, opened citations at source, and made read-only queries of the live platform database on 2026-11-19: the observation shell `contract.observation_contract` has the column `status_code` and has **no** column `lifecycle_stage`; migrations 0037 and 0062 are recorded as applied in `infrastructure.schema_migration_event` (2026-10-06 and 2026-11-09); of 17 shells, three have more than one version in force; the versions are 19 `active`, 7 `superseded`, 2 `draft` and 1 `approved`. No route was called, no service was run, and no setting's value was read. This definition depends on the Vocabulary Definition, merged as a draft at bc-docs `9b5c9548`. The row counts the dossier quotes (read on 2026-11-13) are not repeated or re-read.

**Commits read.** bc-docs `f1a20074`; bc-core `fd4b55ca`; bc-admin `d37b241`; bc-db `ca1aabd1`; barecount-devhub `3f4684fc`. Every bc-core citation is at `fd4b55ca` unless stated.

## 1. What L4 is

An **observation contract** "declares field selection from a Source Contract to business-vocabulary fields and defines the resulting Source Object shape preserved at admission" (`bc-docs:docs/foundation/the-contract-grammar.md:167 @ f1a20074`). Its body may declare:

- the pinned source and admission contract versions, as native version pairs (`the-contract-grammar.md:169`);
- one entry per source field, binding it to one business concept with a role and nullability (`:169`);
- `semantic_preconditions[]` (`:171`);
- a `source_filter`, an AND-only row selection over the leg's own fields; "Changing a slice means a new Observation Contract version" (`:173`).

It may not declare canonical evaluation logic, may not map one source field to several concepts without a role, and may not carry a row selection anywhere but `source_filter` (`:180-183`). Once a version is in force its body does not change (Invariant III, `bc-docs:docs/foundation/the-invariants.md:85`); a reader and a canonical contract name the exact version they use (Invariant IV, `:103`).

**Its states.** A version is `draft`, `review`, `approved`, `active` or `superseded`; `active` is said **in force** (`bc-docs:docs/reference/vocabulary.md:345-352`). The machine shared by five families also allows `pending_provisioning` (`bc-core:src/registry/contracts/contract.service.ts:55-58 @ fd4b55ca`), which is not a Foundation state (`vocabulary.md` S2.6 item 1); an observation activation never enters it, because only canonical and metric activations are redirected there (`contract.service.ts:1035-1036`).

**Its records.** `contract.observation_contract` (the shell), `contract.observation_contract_version`, `contract.observation_contract_approval`, and `contract.observation_contract_version_transition`, written by a trigger on each state change (`bc-db:migrations/0023_contract_version_transition_evidence.sql:164 @ ca1aabd1`; DEC-fbc085). The grammar in use is `barecount/observation/v2` (`bc-core:src/registry/resolvers/observation-concept-resolver.service.ts:54`). The body is checked against the meta-schema stored in the database, not the file (`bc-core:src/registry/contracts/contract-validation.service.ts:18-21`).

**What a version does not do.** Bringing it into force writes no tenant binding and starts no provisioning: "AC/OC don't produce tenant-side tables" (`contract.service.ts:1113-1115`). It starts no admission either; stitch contract 1 says what does.

## 2. The acts at a glance

| # | Act | One command, four verbs |
|---|---|---|
| O1 | Author a contract and a version, first or later | `status`, `check`, `do`, `verify` |
| O2 | Submit a version for review, or return it to draft | same |
| O3 | Approve a version, with the approval recorded | same |
| O4 | Bring a version into force | same |
| O5 | End a superseded version | same |
| O6 | Archive, unarchive, edit or remove a contract shell | same |
| O7 | Resolve names to identities (read only) | `status`, `check` |

The command is engine code; a session, the operator console and DevHub use it, and the other ways in are deleted (`bc-docs:docs/development/platform-refactor-program.md:261`). One command with several acts is one path for each act.

## 3. The acts

### O1. Author a contract and a version

**Today.**
- Plain door: `POST /api/contracts` and `POST /api/contracts/:id/versions`, roles `platform_admin` or `operator`, on a `@PlatformOnly` class (`bc-core:src/registry/contracts/contract.controller.ts:27-36, 212-213`). A version is born `draft` (`contract.service.ts:770`). It needs a semver and is checked against the stored meta-schema, then for field-to-concept integrity (`:676-688`): every concept exists and is active, all on one entity, concept-unique, its frozen snapshot equal to the live concept, and no source field re-typed against its parent source contract (`observation-concept-resolver.service.ts:116-161`). A later version is compared with the latest version in force and must carry the increment the change implies (`contract.service.ts:690-719`).
- Three more doors write an observation version:
  - **The chain call**, `POST /api/contracts/observation-chains`, `platform_admin` (`bc-core:src/registry/substrate/author-observation-chain.controller.ts:28-29`). One run writes the shell, the version and its activation, then the reader, flavor and bindings, then the canonical contract (`author-observation-chain.service.ts:1-14, 298-321`). Its version is the constant `1.0.0` (`:71`), and a committed run with a different fingerprint for the same entity refuses (`bc-core:src/registry/substrate/chain-authoring-run.ts:12-13`). So **it cannot author a second version**. bc-admin's chain-author page calls it (`bc-admin:src/components/AppRouter.tsx:205 @ d37b241`).
  - **Publish-chain**, `POST /api/contracts/chains`, `platform_admin` (`bc-core:src/registry/contracts/publish-chain.controller.ts:18-23`), and DevHub's `devhub_publish_chain` (`barecount-devhub:src/mcp-server.js:3906-3918 @ 3f4684fc`). It versions major + 1 (`publish-chain.service.ts:186-190`), activates the observation version, supersedes the prior ones, then does the same for the canonical version (`:94-95, 147-161`). The canonical activation goes from `draft` straight to `active`, which the skip-path closure refuses for canonical contracts (`contract.service.ts:889-900`). **(inferred)**: the call cannot finish today, and leaves an observation version in force with no canonical version. It was not run.
  - **The harness**, `POST /api/harness/apply`, `platform_admin` (`bc-core:src/registry/harness-apply/harness-apply.controller.ts:29-30`). For a plan of mode `observation_contract_gap_plan` it writes a draft through the contract service (`harness-apply-from-plan.service.ts:90, 181-184`), behind a setting named `HARNESS_OC_APPLY` (`:561-562`). The L4 dossier does not list it; the L2 dossier lists the route as "shared with L4, to be split" (`functions-authoring-lanes.md:208`).
- Scripts: of the 32 files under `scripts/` that name `observation_contract`, 22 are under `scripts/archive/` (git grep at `fd4b55ca`). Live ones boot the engine and drive the service (`scripts/author-arpi-oc-v2-slice.mjs:5-8`), call the HTTP routes with pasted identifiers (`scripts/mcf/partc-author-oc-kurgv.mjs:7-14`), or write version rows by SQL: an `UPDATE` (`scripts/fix-oc-field-mappings.mjs:184-186`) and a `DELETE` (`scripts/fix-oc-relevance.mjs:121`).
- The mapping body is written by a person or a worker. The chapter's two routes for AI-suggested mapping do not exist (git grep for `oc-field-mapping` and `field-mapping/confirm` in `src`: no match).

**The definition.**
- O1 is the one door for writing an observation version, first or later (question 1). A second version is O1 with a new version code; it is born `draft` and must carry the increment the comparison requires.
- `check` reports, before any write: the meta-schema result, every integrity refusal, the increment required, and whether the pinned source and admission versions are in force. `do` writes the shell (first version only) and the version. `verify` reads the version row and its state.
- The body is written by its author. No AI act is part of L4. The AI Definition agrees: AI hands L4 nothing (`bc-docs:docs/development/platform-refactor-program/definition-ai-services.md:226`).

**What must change.**
1. The command is built. Publish-chain and DevHub's tool are deleted; the harness's observation branch is deleted; every live script that writes or drives an observation version, including the two that write rows by SQL, is moved to `scripts/archive/`. The lock's guard does not read the archive.
2. The chain call's observation step calls O1, O2, O3 and O4 instead of the service (question 1). Its file is not held.
3. `check` refuses a version whose pinned source or admission version is not in force. Today only the chain call checks this (`author-observation-chain.resolve.ts:71-86`); the plain door reads the source version with no state filter (`observation-concept-resolver.service.ts:151-154`).
4. `check` refuses a `source_filter` predicate on a field that the pinned source contract does not declare. **(inferred)**: no code under `src/registry` was found that checks filter fields; the gathering's search was not repeated in full.

### O2. Submit a version for review, or return it to draft

**Today.** `POST .../versions/:v/submit` (`draft` to `review`) and `POST .../versions/:v/revert` (`review` to `draft`) (`contract.controller.ts:271-272, 331-332`; `contract.service.ts:857-859, 877-879`). Each writes a transition row by trigger. A version at `approved` has no way back: the shared machine allows only `active` or `pending_provisioning` from there (`contract.service.ts:55-58`), and supersede starts only from `active`. bc-db migration 0037, applied on 2026-10-06 (the Chief's read), freezes the body from `approved` on and says "author a new version instead" (`bc-db:migrations/0037_contract_version_freeze_approved_onward.sql:47-52 @ ca1aabd1`).

**The definition.** One command for three moves: submit (`draft` to `review`), return from `review` to `draft`, and return from `approved` to `draft`. The last is allowed only when O4's `check` refuses the version, and it records the refusal it answers. So no state of an observation version that is not in force lacks an act that leaves it. `check` reports the current state and whether the move is allowed. `verify` reads the state and the transition row. A body returned to `draft` can be changed again (the freeze of 0037 reads the state before the update, `0037:47`; one version sits at `approved` today, by the Chief's read); no version that was in force is touched, so Invariant III holds (`the-invariants.md:85`).

**What must change.** The command is built. The edge `approved` to `draft` is added for the observation family only, in `contract.service.ts:55-58` (not held; the machine is shared with L2 and L5, whose edges do not change).

### O3. Approve a version

**Today.**
- `POST .../versions/:v/approve` moves `review` to `approved` and checks nothing else (`contract.service.ts:861-863`).
- A separate route, `POST .../versions/:v/approvals` (`contract.controller.ts:359-360`), writes `contract.observation_contract_approval` with the approver taken from a body field `by`, not from the verified subject (`contract.service.ts:1155-1170`). No gate reads that row.
- No code compares the approver with the author.
- No panel reviews or writes an observation contract **(inferred)**. A git grep for `observation_contract` in `src/registry/concept-registry`, `src/registry/mcf`, `src/registry/metric-audit` and `src/registry/abc` finds fifteen non-test files. Those opened are reads or plans: the ABC desktop maker lists observation contract authoring among the authorities it must not take (`bc-core:src/registry/abc/desktop-maker/forbidden-authority-fields.ts:61`); the registry's concept supersession reads active observation versions to refuse (`registry-authoring.service.ts:1817-1849`, section 6); the chain-enrichment planner plans a mode `observation_contract_gap_plan` (`mcf/chain-enrichment/chain-enrichment.dto.ts:37`). The chain-audit, chain declaration and metric-audit wire files were not opened; no `INSERT` or `UPDATE` of an observation table occurs in those folders outside tests. AI hands L4 nothing (the Definition of AI services, section 6).

**The definition (for question 2, answer a).** `check` runs every check of O4, so a version that could not be put in force now is not approved. The approve act writes the approval row itself, in the same transaction as the state change: `decided_by_name` is the verified subject, `approver_role_name` that subject's role at the act, `decision_code` the approval, `comment_text` optional (columns at `contract-families.ts:172-179`). There is no second route for recording an approval. Whether the approver must be a different subject is ruled with B22 (L5, phase 5) and the roles rulings of phase 9; L4 changes no one's permissions.

**What must change.** The command is built. The `approvals` write route is deleted. **(inferred)**: no schema change is needed, as the four columns take these values; their types were not read.

### O4. Bring a version into force

**Today.**
- `POST .../versions/:v/activate` (`contract.controller.ts:301-302`), from `draft` or `approved` (`contract.service.ts:55-57`). The skip-path closure that refuses `draft` to `active` covers canonical and metric only, on the single route (`:889-900`) and on `POST /api/contracts/bulk-transition` (`:425-436`). So an observation version can go into force with no review on every route.
- The gate checks six body keys (`:987-988`; the comment above says seven, `:981`), exactly one source reference (`:998-1003`), no join (`:1004-1009`), and repeats the integrity check (`:1013-1021`).
- Before any check runs, the activation stamps every other version in force with `supersede_after = now() + 48 hours` (`contract.service.ts:829-831`; `contract-version.repository.ts:204-221`).
- The meta-schema keeps `join_semantics` with `maxItems: 0` beside a `sum` strategy (`bc-core:src/registry/meta-schemas/observation-v2.schema.json:71-73, 111`). DEC-585edb, marked implemented, adds that strategy; Foundation and activation say an observation contract carries no join.

**The definition.**
- In force only from `approved`, on every route (question 2).
- `check` reports every activation refusal before any write. The stamp of the prior version is written only after the checks pass, in the same transaction.
- `verify` reads the state, the transition row, and the versions of the same contract still in force.
- An observation contract carries no join. The grammar says so once.

**What must change.**
1. The closure is extended to the observation family, on the single route and on bulk. Bulk is refused for the observation family, so that route no longer moves observation versions (a second way to perform O2 to O5); the bulk route itself belongs to L2 and L5 as well (section 5).
2. The stamp moves after the checks. **(inferred)**: this can be done in `contract.service.ts`, which is not held.
3. The required keys are declared once, by the stored meta-schema, not repeated in code; the wrong comment is corrected.
4. `sum` and `join_semantics` are removed from the observation meta-schema, through the meta-schema change route. **The operator's act**: a stored meta-schema change.
5. DEC-585edb is amended for its observation part only. It is not marked superseded: its `sum` reducer is also the canonical grammar's (`canonical-v2.schema.json:245-248`) and is tested there (`bc-core:src/boundary/ccv2-canonical-resolver.join.spec.ts:216`), which is L5's. **The operator's act**: an ADR's change needs his recorded grant.

### O5. End a superseded version

**Today.** `POST .../versions/:v/supersede` moves `active` to `superseded`, by a person's call (`contract.controller.ts:316-317`). Nothing completes the 48-hour mark: in `src` the column is written once (`contract-version.repository.ts:216`) and otherwise only sorted on, for canonical versions (`bc-core:src/boundary/ccv2-canonical-resolver.service.ts:748`; `bc-core:src/registry/contracts/canonical-contract-pool-readiness.ts:47-48, 73-74`). Publish-chain supersedes prior versions itself and records failures in a list without raising them (`publish-chain.service.ts:153-160`). After a version is superseded, a reader still bound to it reads it as not in force (`bc-core:src/registry/readers/reader-chain-resolution.service.ts:170-181`) until L7 repoints it, and **every canonical version in force that pins it refuses to resolve**: the canonical resolver selects the pinned observation version only when it is `active` and its shell is not archived, and throws otherwise (`bc-core:src/boundary/ccv2-canonical-resolver.service.ts:887-905`). A canonical version cannot pin a successor before the successor is in force, for the same reason. The nightly cycle exists in code, behind a setting whose value was not read (`bc-core:src/boundary/runtime-scheduler.service.ts:58-74`); it has no supersede step.

**The definition (for question 3, answer b).**
- A version stays in force from its successor's activation until two things hold: its declared window has passed, and nothing in force pins it (an active reader observation binding, or a canonical version in force whose `observation_references[]` names it).
- So **several versions of one contract can be in force at once, with no end date while a pin stays**. The dossier's lock condition "at most one version per contract is in state `active`, enforced in the database" (`functions-authoring-lanes.md:557`) is replaced for L4 by section 8, item 3. Stitch contract 10 already allows two in force for L5 until the old one is superseded (`stitch-contracts.md:324`).
- O5 `do` is issued by a person or a session, from O5 `status`, until the nightly cycle carries the step that stitch contract 10 gives it (`stitch-contracts.md:321`); adding that step is Runtime's repair (RT, phase 7) **(inferred)**, as for the resolve step of ruling B7 (`platform-refactor-program.md:374`). O5 refuses while anything pins the version, and names what does. A refusal is recorded and the act is tried again.
- `status` lists every version past its window, with what still pins it.

**What must change.**
1. The finisher is built for the observation family. **(inferred)**: in new code outside the held files.
2. The window length moves from code into a declaration. **Held**: `contract-version.repository.ts:216` (question 4).
3. A CHECK on the version state of `contract.observation_contract_version`, which has none (`vocabulary.md:371`): the five Foundation states, `draft`, `review`, `approved`, `active`, `superseded`. Whether `pending_provisioning` is allowed too is vocabulary defect 1 (`vocabulary.md:366`), the operator's to decide; an observation activation never enters it (section 1). **The operator's act**: a bc-db migration. It follows from L4's lock condition, not from a question.

### O6. Archive, unarchive, edit or remove a contract shell

**Today.** `PATCH`, `DELETE`, `POST .../expunge`, `POST .../archive`, `POST .../unarchive` (`contract.controller.ts:158-202`). Expunge needs a reason and refuses while any dependent exists, including an active reader observation binding (`bc-core:src/registry/contracts/contract.repository.ts:505-568`). Delete refuses when referenced (`contract.service.ts:527-540`).
- The two removals are for different shells. Expunge refuses unless the shell's `lifecycle_stage` is `testing` and no version is in force: "a governed contract archives/supersedes, it is never expunged" (`contract.repository.ts:605-627`); it writes an evidence row. The generic delete refuses a `testing` shell and "emits NO evidence" (`contract.repository.ts:451-465`), so it is today the only removal of a governed shell.
- The column `lifecycle_stage` (`testing`, `governed`) is added to the observation shell by the frozen baseline (`bc-core:docker/redesign/58-contract-testing-lifecycle-phase-a.sql:37, 45`) and is absent from the Drizzle type (`src/database/schema/contract/observation-contract.ts`). The live table does not have it (the Chief's read, 2026-11-19). So today expunge cannot run on an observation contract **(inferred)**: its query names the column (`contract.repository.ts:612`); and the generic delete's refusal of a `testing` shell is skipped when the column is absent (`contract.repository.ts:454-459`), so today every observation shell is treated as governed and the generic delete is its only removal.

**The definition (for question 6, answer a).** One command for the shell. A `testing` shell is removed by expunge only, with its evidence row. A governed shell is never removed: it is archived. Because the live shell has no `lifecycle_stage`, every observation contract is governed today, so under this answer **no observation contract can be removed at all** until a bc-db migration adds the column (**the operator's act**, asked for only if a `testing` observation contract is wanted; L4's lock does not need it). `check` names every dependent that would refuse the act, and the shell's `lifecycle_stage`.

**What must change.** The command is built. The generic delete is refused for the observation family (the route is shared with L2 and L5, whose use does not change).

### O7. Resolve names to identities

**Today.** `POST /api/registry/substrate/resolve`, `platform_admin` or `operator`, read only: entities, concepts, characteristics, source fields, contracts and source versions; an ambiguous name returns candidates (`bc-core:src/registry/substrate/substrate-resolve.controller.ts:1-29`). DevHub calls it (`barecount-devhub:src/mcp-server.js:3850`).

**The definition.** Kept as one read. O1's `check` uses it. The dossier shares it with L3 and L5; this definition proposes L4 as its owner **(inferred)**: most of what it resolves is what an observation body names.

### One new observation contract, from nothing to a version a reader can bind

This is the walk of the Prove step, for the recommended answers of section 9. A worker given only the chapter and the commands takes one new contract over an existing source and admission pair to in force.

| Step | Act | Who | What records it | Where it can stop |
|---|---|---|---|---|
| 0 | The source table and fields are in the catalog (L1); a source and admission pair is in force (L2); the entity and concepts are active (L3) | the owners of those functions | their records | outside L4 |
| 1 | O7: names to identities | the worker | nothing | an ambiguous name |
| 2 | The worker writes the body | the worker | nothing | |
| 3 | O1 `check`, then `do`: shell and version `1.0.0`, `draft` | the worker | the shell; the version row | a concept not active or drifted; a pin not in force; a re-typed field |
| 4 | O2 `do`: submit | the worker | a transition row | |
| 5 | O3 `check`, then `do`: approve | the approver | a transition row; an approval row with the verified subject | any refusal O4 would make |
| 6 | O4 `check`, then `do` | the worker | a transition row | a missing key; two sources; a join; a pin no longer in force (then O2 returns the version to `draft`) |
| 7 | O4 `verify` | the worker | the version `active` | |

Binding a reader (L7, `POST /reader-authoring/observation-bindings`) and pinning the version in a canonical contract (L5) are outside L4. L4's Prove ends at step 7, and its `verify` reads the version the way the canonical side reads a pin: an exact version that must be in force (`observation-concept-resolver.service.ts:370`). L4 has no step of the thread of its own **(inferred)**: its part is O4 `verify` on the version the thread's canonical contract pins, read without change. Steps 3 to 6 write a real contract and put it in force on the platform database. Ruling G39 authorises no act on a contract (`rulings.md:91`). So the worker performs steps 3 to 6 for real only under a grant the operator records for the Prove step; without it, it performs them only through `status`, `check` and `verify`, as the Prove step of Operations did (`platform-refactor-program.md:269`). Who approves at step 5 is named in that grant's request.

## 4. The rest

None. L4 is taken whole, so no act of L4's own is carried to a later phase. The shared surfaces of section 5 are handed to their owners.

## 5. What is not L4's

| Surface | Today | Owner |
|---|---|---|
| The chain call as a whole: run claim, reader, flavor, bindings, canonical contract, reconcile of an abandoned run (`author-observation-chain.controller.ts:48-49`, operator only) | one call, `runtime.chain_authoring_run`; the reconcile refuses unless the observation shell's parent field reads `draft` (`bc-core:src/registry/substrate/abandoned-run-recovery.service.ts:180-185`) | under question 1 (a): the observation step is L4's; the reader, flavor and binding steps are L7's (phase 8, in part); the call itself (run claim, lease, reconcile) and its canonical step are L5's (phase 5) |
| The chain-enrichment planner's mode `observation_contract_gap_plan`, left with no applier once the harness branch is deleted | `mcf/chain-enrichment/chain-enrichment.dto.ts:37` | L9 (`functions-authoring-lanes.md:736`; phase 6 in part, or phase 12) |
| Bind a reader to an observation version; repoint; unbind; `POST /readers/create-from-oc` | `bc-core:src/registry/readers/reader-observation-binding.repository.ts:53-80` checks nothing about the version's state | L7 (phase 8, in part) |
| A canonical version's `observation_references[]` pin | `contract.service.ts:122-131, 178` | L5 (phase 5) |
| The bulk-transition route for the other families | `contract.controller.ts:127-128` | L2 (phase 10) and L5 (phase 5); L4 only refuses its own family |
| The harness's admission branch | `harness-apply-from-plan.service.ts` | L2 (phase 10) |
| The meta-schema change routes (`/admin/meta-schema/change-request*`) | shared by every contract family | not established; the Audit step names its owner before L4's Lock |
| The bc-admin list and the generic transition buttons | `bc-admin:src/api/contracts.ts:687-706` | S5 (phase 15); they call the routes the commands replace **(inferred)** |
| Admission's use of the field map, identity and `source_filter` | `bc-core:src/boundary/reader-runtime/resolved-admission-context.ts` (held) | RT (phase 7); stitch contract 1 for what starts admission |
| Schema changes | bc-db forward migrations | OP, under the Database Change Protocol |

## 6. Hand-offs

| Neighbour | L4 receives | L4 hands on | Record |
|---|---|---|---|
| L1 | `source_version_id`, `source_table`, `source_field` | nothing | the version body (`observation-v2.schema.json:15`) |
| L2 | the pinned pair `sc_contract_id`, `sc_version_code`, `ac_contract_id`, `ac_version_code`; the source contract's field declarations | nothing | `source_references[0]` (`observation-v2.schema.json:34`); `contract.source_contract_version` |
| L3 | a concept at `active`, found by id. The resolver reads and checks: `lifecycle_state`, `entity_id` (one entity for the body), `kind` (against the entry's binding kind), `representation_term`, `data_type`, `unit`, `reference_role` and `target_entity_id` (against the frozen copy), and the closed value set of the concept's active version | nothing as an act; L3's concept supersession reads L4's active versions and refuses while one maps the concept (`registry-authoring.service.ts:1817-1849`, reached from the supersession at `:1090` through `:1763-1782`) | `concept_registry.business_concept`, the record L3's Definition names, and `concept_registry.business_concept_version` for the value set (`observation-concept-resolver.service.ts:116-135, 531-545, 584-625, 706-720`) |
| AI | nothing | nothing | none |
| L5 | nothing | an exact version in force, for `observation_references[]` | `contract.observation_contract_version` |
| L7 | nothing | an exact version, for a reader observation binding | `runtime.reader_observation_binding` (L7's) |

**No stitch contract names L4**, and this definition proposes **no new one**, for three reasons **(inferred)**. First, both hand-offs out are an exact pin to a version row, and the readers of the pin already require it in force; nothing about the pin is undecided. Second, the one undecided point, how long a superseded version stays readable, is ruling B13 (question 3), and stitch contract 10, between L5, L6 and DL, already gives L5 the same window and finisher in its repair list (`stitch-contracts.md:327`). Third, stitch contracts 2 and 3 concern a tenant's adopted version and tenant bindings, and an observation version writes neither (section 1). If the operator answers question 3 otherwise than stitch contract 10 does for L5, the two answers must be made one before L5 is locked in phase 5.

## 7. Values written into code, and the files under the hold

**Values that Modify moves into declarations.**

| Value | Where |
|---|---|
| The 48-hour window | `contract-version.repository.ts:216` (held) |
| The lifecycle edges, and the skip-path closure's list of families | `contract.service.ts:55-58, 430-431, 895` |
| The required body keys, repeated beside the meta-schema | `contract.service.ts:987-988`; `observation-v2.schema.json:15` |
| Version `1.0.0` in the chain call; major + 1 in publish-chain | `author-observation-chain.service.ts:71`; `publish-chain.service.ts:186-190` |
| The chain call's header values and the default policy `strict_backward` | `author-observation-chain.service.ts:589-591`; `contract.service.ts:699` |
| The default environment `dev` | `author-observation-chain.service.ts:110`; `reader-observation-binding.repository.ts:54` |
| The run lease of 900 seconds | `chain-authoring-run.ts:23` (with the chain call, section 5) |
| The harness setting name | `harness-apply-from-plan.service.ts:561-562` (deleted with the branch) |

**The files under the hold.** The hold is defined by `bc-core:governance/engine-value-surface.json` (roots and `also_held`, counted at `ec72438b`). The held set is the roots, every non-test file they reach by value imports, and the `also_held` paths (`bc-core:scripts/engine-guard/surface.mjs:1-6, 181-208`). This worker ran that code's `computeSurface` over an export of `fd4b55ca`: 314 files are held, and no root or `also_held` entry is missing. The guard's own run on a proposed commit is the authority. L4's held files are eleven:

1. `src/registry/contracts/contract-version.repository.ts`
2. `src/registry/contracts/contract.repository.ts`
3. `src/registry/contracts/contract-families.ts`
4. `src/registry/contracts/contract-uid.ts`
5. `src/registry/contracts/transition-context.ts`
6. `src/registry/contracts/canonical-contract-pool-readiness.ts` (read by L5)
7. `src/registry/substrate/chain-authoring-reservation.ts`
8. `src/registry/resolvers/concept-observability.ts`
9. `src/database/schema/contract/observation-contract.ts` (all 24 files of that folder are held)
10. `drizzle/0019_observation_schema.sql`
11. `drizzle/0022_immutability_triggers.sql` (all 45 files of `drizzle/` are held)

Each reaches the roots through admission: for example `contract.repository.ts` by way of `src/boundary/reader-runtime/reader-runtime.service.ts`, `src/boundary/orchestrator.service.ts` and `src/boundary/observation.service.ts`. Not held: `contract.service.ts`, `contract.controller.ts`, `observation-concept-resolver.service.ts`, the chain call's files, publish-chain, the harness folders, the meta-schemas, `reader-observation-binding.repository.ts` and `reader-chain-resolution.service.ts`.

**Changes in section 3 that touch a held file:** O5 item 2 (the window length, file 1), and, if question 5 is answered (a), the type for the removed column (file 9). The reconcile's read of that column (`abandoned-run-recovery.service.ts:180-185`) is not held: only the chain call's unheld controller and module import it (git grep at `fd4b55ca`) **(inferred)**, from the list above. Until the reference run has passed (phase 5), each such change needs the operator's recorded exception, and L4's Modify exit reads: "automatic checks pass, and every change to a held file carries the operator's recorded exception" (`platform-refactor-program.md:267`). Every other change of section 3 is in files that are not held.

## 8. What the lock will mean

1. O1 to O7 are performed by L4's command alone. A guard fails when a second way appears: a route, a DevHub tool, a script that writes an observation version, or bulk-transition on the observation family.
2. No observation version reaches in force except from `approved`, on any route, and every approval records its verified subject. Every state of a version not in force has an act that leaves it (O2).
3. No version is in force past its declared window unless something in force pins it, and `status` names what does. Several versions of one contract may be in force while pins hold; this replaces the dossier's condition of at most one (question 3). The version state has a CHECK.
4. The parent field is retired, or written true (question 5). A governed shell is archived, never removed (question 6).
5. The chapter `observation-contract-creation.md` is rewritten for the v2 body and names only routes and tables that exist, and is marked locked. Its listed verdict is rewrite (`bc-docs:docs/development/platform-refactor-program/chapters.md:213`). The Observation sections of `contract-chain-assembly.md` are corrected in L9's rewrite (`chapters.md:120`). The barecount-devhub notes `artifacts/lanes/L4-oc-bcf-catalog-map/` are marked history.
6. L4's files pass the code rules, and its commands are tested against a real database.

## 9. Questions for the operator

Each is put as a proposed ruling. Where the register's ruling covers more functions than L4, the question says what the answer settles and what stays open. Questions 4 to 6 had no row in the register. The six questions were recorded on 2026-11-19 as ruling B20 (question 1), rulings B14 and B13, each for observation contracts (questions 2 and 3), and rulings G47, B36 and B37 (questions 4 to 6), on the operator's desk grant `2026-11-19T07-06-49-011Z-ee28e46a` (text SHA-256 `ee28e46acc9093c5db3e4aa19fe5914092261ca72639359a086469ec5abc10b4`, desk request 527).

**1. The one door, and the split of the chain call (ruling B20).** Four doors write an observation version (O1, "Today"). The register asks: "Which is the one door, and is the call split across L4, L5 and L7?", needed by phase 4 (`rulings.md:152`). B20 is L4's alone; this answer settles both halves.
- Options:
  - (a) L4's command is the one door. Publish-chain, DevHub's tool and the harness's observation branch are deleted. The chain call stays as one call and is split now: its observation step calls L4's command; its reader, flavor and binding steps are L7's (phase 8, in part); the call itself (run claim, lease, reconcile) and its canonical step are L5's (phase 5).
  - (b) As (a) for the door, but the split of the rest is ruled at L5's Define step. B20's second half then stays open past phase 4, the phase the register names.
  - (c) The chain call is the one door for a new contract, owned whole by one function. Second versions would still need the plain door, because the chain call can only write `1.0.0`.
  - (d) The chain call is deleted now.
- Recommendation: (a). It is the only option with one path for every act and no ruling left open: (b) leaves half of B20 open, (c) leaves two doors for creating a version, and (d) removes what L5 and L7 have not yet defined.
- What follows: (a) the observation step is rewritten in phase 4, the call keeps working, and the Definitions of L5 and L7 take their steps as named; (b) the same in phase 4, and the split is put to you again in phase 5; (c) L4 cannot lock its authoring act alone; (d) the bc-admin chain-author page stops working until L5 and L7 replace it.
- Cost to you: none beyond approving this definition.

**2. Review before in force (ruling B14).** The register asks, for L2 and L4: "May a version go from `draft` to in force without a review?" (`rulings.md:146`). This answer settles it for observation contracts (L4) only. For source and admission contracts (L2, phase 10) B14 stays open.
- Options:
  - (a) Every route passes `review` and `approved` before in force, and the approve act records the approver's verified subject. Whether the approver must be another person follows ruling B22 (L5, phase 5).
  - (b) As (a), and the approver must be a different subject now.
  - (c) As today: `draft` to in force is allowed.
- Recommendation: (a). It closes the skip that canonical and metric contracts already refuse, and changes no one's permissions. Under (a) one subject can still submit and approve; the record shows it.
- What follows: (a) the chain call's observation step submits and approves before it activates, as it already does for the canonical contract (`author-observation-chain.service.ts:505-527`); the bulk route no longer moves observation versions (O4 item 1); approval runs the activation checks first, and a version that is approved but later refused at activation is returned to `draft` by O2; (b) the same, and every version waits for a second subject, in practice you **(inferred)**: the dossier found one subject performing every act; (c) the lock cannot name one lifecycle.
- Cost to you: none under (a); under (b), one act for every version.

**3. How a superseded version ends (ruling B13).** The register asks, for L2, L4 and L5: "Is the prior version superseded at once, or after a window that code completes?" (`rulings.md:145`). This answer settles it for observation contracts (L4) only. For L2 (phase 10) and L5 (phase 5) B13 stays open; stitch contract 10 already gives L5 the window, without the pin refusal of (b). If L5's answer differs, the two are made one before L5 is locked.
- Options:
  - (a) At once: activating the successor supersedes the prior version in the same act.
  - (b) After a declared window, by a built finisher, and not while a reader binding or a canonical version in force still pins it.
  - (c) After a declared window, by a built finisher, whatever still pins it.
  - (d) As today: only a person's supersede call ends it.
- Recommendation: (b), with its cost said plainly: an old version stays in force for as long as something pins it, with no end date, so several versions of one contract can be in force at once. The dossier's lock condition of at most one version in force per contract (`functions-authoring-lanes.md:557`) is dropped for L4 and replaced by section 8, item 3; `status` lists every version past its window and what pins it. Under (a) and (c), every canonical version in force that pins the old version refuses to resolve at once (`ccv2-canonical-resolver.service.ts:887-905`) and every bound reader reads it as not in force, until L5 re-pins and L7 repoints; and a canonical version cannot pin the successor before it is in force, so under (a) the two cannot happen in one act. Under (d) the defect stays.
- What follows: (b) the finisher is built in phase 4; the window keeps its 48 hours, moved into a declaration (question 4); a person or a session issues O5 until Runtime adds the step to the nightly cycle (phase 7) **(inferred)**; (a) canonical resolution and readers break at each new version until re-pinned; (c) the same, after 48 hours; (d) no change.
- Cost to you: under (b), several versions of one contract may stay in force; someone (a session, or you) must issue O5 until phase 7; nothing else beyond question 4.

**4. Changes to held files in phase 4.** Under the recommended answers, two changes touch held files (section 7).
- Options:
  - (a) Make them in phase 4, each with your recorded exception.
  - (b) Carry them by name until the reference run has passed in phase 5. L4 then locks with both named as open, and they are made without exceptions once the guard asks for a passing run instead.
- Recommendation: (a). Neither change alters a value: one keeps 48 hours as a declared value, the other follows a migration you will already have approved. Under (b), L4 is locked with known open items, and reopening it needs your ruling.
- What follows: (a) two exception requests at the Modify step; (b) none now, the window stays in code, and the removed column stays in the type until phase 5.
- Cost to you: two exception approvals under (a).

**5. The parent's state field.** `contract.observation_contract.status_code` (`draft`, `active`, `deprecated`) has never been kept true (`vocabulary.md:367`). One engine reader exists outside the repository: the reconcile of an abandoned chain run refuses unless the field reads `draft` (`abandoned-run-recovery.service.ts:180-185`); a git grep of `src` at `fd4b55ca` finds no other.
- Options:
  - (a) Retire it with a bc-db migration.
  - (b) Define it and have L4's commands keep it true.
- Recommendation: (a). The version's state is the one source of truth for in force, and a second field that restates it breaks rule 4 of the database rules.
- What follows: (a) a migration and a held type change (question 4); in the same change the reconcile's test is restated on the version state (for example, no version beyond `draft`), in an unheld file of the chain call, which L5 is told of; (b) code in `contract.repository.ts`, a held file, a definition of what each value means, and the reconcile then refuses any abandoned run whose version came into force, so its rule must be restated too.
- Cost to you: one migration approval under (a).

**6. How an observation contract is removed.** Expunge removes only a `testing` shell, with evidence; the generic delete removes only a governed shell, with no evidence (O6, "Today").
- Options:
  - (a) A `testing` shell is removed by expunge only; a governed shell is never removed, only archived. The generic delete is refused for the observation family.
  - (b) Both stay: expunge for `testing` shells, delete for governed ones, and delete is made to write an evidence row.
- Recommendation: (a). It matches the code's own rule that "a governed contract archives/supersedes, it is never expunged" (`contract.repository.ts:616-619`), and no removal is left without evidence (Invariant VI).
- What follows: (a) a governed observation contract made in error stays forever as an archived record; and since the live shell has no `lifecycle_stage` column, that is every observation contract until a migration adds it, so in phase 4 nothing removes one; (b) a new evidence write for delete, in `contract.repository.ts`, a held file (a third exception under question 4).
- Cost to you: none under (a); under (b), one more exception.

## 10. What this definition asks the operator to approve

1. The seven acts, O1 to O7, with their definitions in section 3, and L4 taken whole with no act of its own carried.
2. The owners named in section 5, including the split of the chain call under question 1 (a), and that the owner of the meta-schema change routes is named by the Audit step before L4's Lock.
3. That no new stitch contract is needed (section 6).
4. The answers to the six questions of section 9. Under the recommended answers you accept: publish-chain, DevHub's tool for it and the harness's observation branch are deleted, and the live scripts that write versions are moved to the archive; the chain call is split now between L4, L5 and L7; every version passes review, one person may still approve their own, the bulk route no longer moves observation versions, and an approved version that cannot be put in force is returned to `draft`; several versions of one contract may stay in force, with no end date, while something pins the old one, and the dossier's rule of at most one is dropped for L4; a person or a session ends old versions until the nightly cycle has the step (phase 7); two exception requests for held files; the parent field is removed by a migration and the abandoned-run reconcile is restated; a governed observation contract is never removed, only archived, which today means no observation contract can be removed at all. B13 and B14 stay open for the other functions they name.

**What approving this definition does not cover.**
- The schema changes Modify will ask for, each under the Database Change Protocol: a CHECK on the version state (O5 item 3, from the lock, not a question), and, under question 5 (a), the removal of the parent field.
- Any change to a file under the hold on the engine (section 7). Each is asked for as an exception, or waits, as question 4 rules.
- Any act on an existing contract version: no version is put in force, superseded, rewritten or deleted, and the versions the dossier found in force together are not touched.
- The Prove step's acts on the platform database (section 3, the walk): each needs its own grant.
- The stored meta-schema change (O4 item 4) and the change to DEC-585edb (O4 item 5).
- Anything that changes who may do something: no role, permission or approver rule is changed.
- Any run of the chain call, the harness, a script or a reference run.

## Where this definition differs from the Definitions of AI services and of Vocabulary

There is no disagreement on the line between the functions. AI hands L4 nothing (`definition-ai-services.md:226`). L3 hands L4 "a concept at `active`, found by id", in `concept_registry.business_concept` (Vocabulary Definition, section 6); this definition names the same record. One difference of detail, not of record: the Vocabulary Definition does not list the fields L4 reads. L4's resolver reads and checks `lifecycle_state`, `entity_id`, `kind`, `representation_term`, `data_type`, `unit`, `reference_role`, `target_entity_id`, and the closed value set held on the concept's active version in `concept_registry.business_concept_version` (`observation-concept-resolver.service.ts:116-135, 531-545, 584-625, 706-720`). A change to any of them in L3 makes the resolver refuse an observation body whose frozen copy differs. The Vocabulary Definition also does not name the dependency the other way: L3's concept supersession refuses while an active observation version maps the concept (`registry-authoring.service.ts:1817-1849`). Both were added to the Vocabulary Definition (section 6) in the change that recorded the rulings on 2026-11-19.

## What is not established

- The live state beyond the Chief's reads ("What was checked"): the stored meta-schema text and active reader bindings. The Audit step reads them, and reads again what the Chief read.
- Whether publish-chain or the harness has ever been used, and the value of `HARNESS_OC_APPLY`.
- Whether the nightly cycle is switched on (`BC_SCHEDULER_ENABLED`, value not read), and whether the file that holds it is under the hold.
- Whether any database rule refuses the new edge `approved` to `draft`: none was found in bc-db's migrations; the frozen baseline was not searched.
- DEC-1bb88e, which the code cites for the re-typing refusal, has no file in `bc-docs:docs/governance/adrs/` at `f1a20074`.
- Not opened: the chain-audit, chain declaration and metric-audit wire files that name `observation_contract`, beyond the search for writes.
- Not read: the archive service body; the compatibility rule for observation bodies beyond `bc-core:src/registry/contracts/compatibility.ts:336-342`, which compares the whole body; the admission runtime; bc-admin pages beyond their routes; tests; bc-portal and bc-infra.

**Facts of the gathering found wrong or not verified.**
- Wrong: 22 of the 32 script files are under `scripts/archive/`, not 14.
- Wrong: `contract.repository.ts:511-568` is the expunge guard against dependents, not an archive guard; no archive guard was verified.
- Omitted: publish-chain's canonical activation from `draft` is refused by the skip-path closure, so the call cannot finish (inferred, not run).
- Omitted: the meta-schema itself carries the conflict of DEC-585edb in one file (`observation-v2.schema.json:73, 111`); the gathering saw it, the dossier did not.
- Not verified: the expunge reason at `:552-557`; the bc-db baseline lines on `trg_cv_immutable`, the parent CHECK and the binding table; the bc-admin hook and page lines other than those cited here; `admission-and-observation.md` lines.
- Confirmed: the delete refusal at `contract.service.ts:527-540`; the eleven held files; the six required keys beside a comment saying seven; the stamp written before the checks; the chain call's constant version and its fingerprint refusal; the missing mapping routes.
