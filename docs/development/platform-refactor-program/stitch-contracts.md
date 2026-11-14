---
id: platform-refactor-program-stitch-contracts
order: 45.11
title: "The Stitch Contracts"
status: drafting
authority: reference
depends_on: [devhub, documentation-system, decision-and-change-procedure]
governing_sources:
  - Platform Refactor Program (the hand-offs between functions)
  - Vocabulary (the status words and the definition of done)
governing_adrs:
  - DEC-71f15e (the Platform Refactor Program)
  - DEC-a67bae (the locked lane taxonomy; one owner per surface)
  - DEC-c220e4 (the interim rule on which metrics a tenant sees)
  - DEC-cf6d3b (the tenant activation model; tenant-to-package assignment)
errata_referenced: []
v2_sources: []
diagrams: []
---

# The Stitch Contracts

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md). It holds the twelve stitch contracts that the program's section "The hand-offs between functions" calls for. The Chief wrote them in phase 2; each is approved by the operator, and is changed afterwards only by a new ruling made before the functions it joins are locked.

## How to read a contract

A stitch contract is a design. It says what the functions that meet at a hand-off will be changed to do; it does not describe what they do today. Each has five parts.

- **Today** gives the facts the contract starts from, each with the file and line, or the query, behind it. The engine was read at commit `df52506d`, bc-docs at `1860bf65`, the platform database with read-only queries on 2026-11-14. No tenant database was read.
- **The contract** answers the seven questions the program sets: which functions meet; what passes across, and in which record; who acts; what starts the act; which version is used; what happens when the act fails; what each side may assume.
- **What must change to meet it** lists the repairs and the new records. A new record is a database change and needs the operator's approval when it is made; approving a contract does not approve it. Items marked "needed by the thread" are built in the program; the rest are designed and not built (ruling T2).
- **Left to the operator** holds only what the contract does not settle. Where a ruling already in the register covers a question, the ruling is named and the question is not asked again.

No contract adds a capability beyond what its hand-off needs. Every contract keeps four rules: a read starts no evaluation; nothing recorded is altered; a reference names its version; Evidence is written with the act.

## What was checked, and by whom

The facts under "Today" were gathered by readers working from the dossiers, the engine and the platform database. The Chief read at source: the path by which a tenant binding is written when a canonical contract version is activated (contract 3); the order of the scheduled cycle, its use of the run date and of environment variables, the absence of any listener that starts work on a completed admission, and the callers of canonical resolution (contract 1); and the claim levels the proof read returns (contract 8). The other facts carry their citation and were not re-read by the Chief. A fact found wrong is corrected here, and a contract that rested on it is put to the operator again.

**Stitch point 3 is settled.** Two dossiers disagreed on the moment a tenant binding is written. The engine writes it at the activate call, when the version moves to `pending_provisioning`, before the version is `active`; the later move to `active` writes none. The write only adds a row and ends no earlier one.

## Stitch contract 1: What starts each boundary act
**Between:** L7 Readers, connectors and connections; RT Runtime.

**Today (read at bc-core df52506d, bc-docs 1860bf65):**
- Canonical resolution starts only by `POST t/ccv2-resolve`, which declares no role (`bc-core:src/boundary/ccv2-canonical-resolver.controller.ts:21-39 @ df52506d`). Only a demo command line also calls it (`git grep -n "resolveForContract(" origin/main -- src ':!*.spec.ts'`).
- A completed admission only writes an event, and that event starts tickets and webhooks and nothing else (`bc-core:src/boundary/runtime-event.service.ts:58-76 @ df52506d`). A code comment says resolution follows admission; the code does not (`reader-runtime.service.ts:418-422`).
- The 02:00 cycle runs admissions, campaign, chain status, seed ledger and value audit. It has no resolution step. A failing step is logged and the next one runs (`bc-core:src/boundary/runtime-scheduler.service.ts:62-74, 152-158 @ df52506d`).
- The scheduled campaign passes today's date as period start and end, for legal entities named in the environment variable `BC_SCHEDULE_LEGAL_ENTITY`, with environment fixed to `'dev'` (`runtime-scheduler.service.ts:107-140`).
- A hand-started metric run takes `asOfDate` and a legal entity; the fiscal calendar gives the period, and a missing calendar or period refuses the act (`bc-core:src/boundary/fiscal-calendar.service.ts:145-173 @ df52506d`).
- Metric acts read existing canonical objects. Nothing checks that resolution came first (`co-candidate-reader.ts:294-358`).

**The contract**
1. L7 (admission) and RT (canonical resolution, metric evaluation) meet.
2. Admission writes its completion record (`admission_run_completed`). Resolution writes its own (`canonical_resolution_completed`). These are Evidence and are read by the check in point 6. They start nothing. What they carry is not established. No period passes between the acts.
3. The scheduled cycle, or a person holding a role the command declares. The cycle acts for the tenant's declared legal entities.
4. A command only (ruling B7). The scheduled cycle issues the resolve command after its admissions and before its metric evaluations. A completed admission starts nothing.
5. A scheduled evaluation uses the period the fiscal calendar gives for each declared legal entity: the one containing the run date (ruling B6). A run started by hand takes a period from the operator. Canonical resolution has no period; it stamps each object from its posting date.
6. A failed admission or a refused resolution group is recorded and the cycle goes on. Before a metric evaluation, the act reads whether resolution has completed since the last completed admission for that tenant. If not, the evaluation is deferred: it records that outcome with the reason ("resolution not run since the last admission") and evaluates nothing. It never starts resolution itself. The next cycle tries again. A missing calendar or period still refuses.
7. Admission may assume nothing about what follows. Evaluation may assume resolution ran after the last admission only if the check in point 6 passed. Nothing may assume an event started anything.

**What must change to meet it:**
- RT, repair: add the resolve step to the cycle between admissions and evaluations.
- RT, repair: read the tenant's declared legal entities, not the environment variable; remove the fixed `'dev'`.
- RT, repair: add the check of point 6 to the single-metric and campaign acts. If the existing completion records cannot answer it, a new record is needed (database change: the operator's approval).
- RT, repair: declare a role on the resolve route.
- L7, repair: correct the comment that says admission starts resolution.

**Left to the operator:**
- Nothing new. Who may start a resolution or an evaluation is ruling B8. The spelling and source of the environment are rulings B17 and G13.

## Stitch contract 2: Which version an act uses
**Between:** L5 Canonical Contracts; L6 Metric Contracts and certification; RT Runtime; DL Delivery to a tenant.

**Today (read at bc-core df52506d, bc-docs 1860bf65):**
- The canonical resolver reads the version in state `active`, unstamped first, then highest number. It reads no binding (`bc-core:src/boundary/ccv2-canonical-resolver.service.ts:735-749 @ df52506d`).
- The metric loader reads the one version with `is_current` and state `active` (`bc-core:src/boundary/metric-spec-loader.ts:229-241 @ df52506d`). The campaign list takes every `active` version, with no `is_current` filter (`campaign-evaluation.service.ts:164-181`).
- A canonical binding row exists per tenant, contract and version code, with `is_active` and no end date (`schema-provisioner.repository.ts:625-654`). No metric binding row exists (a reader's check, 2026-11-14). A tenant is onboarded to an MCF metric by a command row (`tenant-provisioning-enqueue.service.ts:129-140`).
- A new metric version is a new row under the same `metric_contract_uid`, optionally carrying `supersedes_version_uid` (`bc-core:src/registry/mcf/dto/mcf-dtos.ts:222, 277 @ df52506d`). Becoming current demotes the sibling to `is_current = FALSE`, still `active` (`mcf-cert-writer.service.ts:2408-2417`, code comment).
- Up to six bindings are open for one contract on one tenant (`bc-docs:docs/development/platform-refactor-program/functions-authoring-lanes.md:1321 @ 1860bf65`; not re-queried).

**The contract**
1. L5 and L6 (versions), DL (adoption), RT (the act) meet.
2. The tenant's adoption record: tenant, family, contract, exact version code, accepted at, ended at. For a metric it is a record of the same kind, naming the metric contract and exact version.
3. RT, at each evaluation, by a read. Reads start nothing.
4. Each resolve or evaluation command.
5. Under ruling T3 the act uses the version the tenant adopted, never the platform's newest. There is at most one open adopted version per tenant per contract. A new version of a metric contract is a new version row under the same parent metric contract. A metric that replaces another metric is a different parent and is not a new version. The adopted version is read by its exact version code whatever its state.
6. If the tenant has no adoption, or more than one is open, the act refuses and records why. It never falls back to the platform's current version. If the adopted version is incompatible with its source or bindings, new evaluation for that tenant is refused, nothing is reported in its place, and the tenant is shown the reason (ruling T3). The run record names the version used.
7. RT may assume one adopted version. DL may assume RT reads only accepted adoptions. Neither may assume the adopted version is the platform's newest.

**What must change to meet it:**
- RT, repair: resolver, metric loader and campaign scope read the adopted version. Remove the ordering rule from tenant reads.
- DL, needs a new record (database change: the operator's approval): an adoption record with acceptance and end, or the same fields on the binding. A metric adoption record.
- DL/RT, repair: a compatibility check and the message to the tenant (none exists today).
- L6, repair: the parent-and-version rule above written into the metric contract chapter.

**Left to the operator:**
- Nothing new. Who classifies a change as value-affecting is ruling T16; the form of the acceptance record is ruling T17. This contract fixes only that an act reads the adopted version and never falls back.
- The demo plane keeps its own pin of versions and is outside this contract.

## Stitch contract 3: A contract version becoming active
**Between:** L5 Canonical Contracts; L6 Metric Contracts and certification; L10 Tenant onboarding.

**Today (read at bc-core df52506d, bc-docs 1860bf65):**
- Settled: the tenant binding is written at the activate call, when the version moves to `pending_provisioning`, not when it becomes `active` (`bc-core:src/registry/contracts/contract.service.ts:1033-1037, 1054 @ df52506d`; `contract-activation.service.ts:94-145`). The L5 dossier is right; the L10 dossier is wrong on the moment.
- The write is insert only. No earlier binding is ended; no code updates `tenant.contract_binding` (`schema-provisioner.repository.ts:625-654`). Live: 17 of 17 bindings open.
- Binding and command are separate statements outside the state write. A failure is logged and swallowed; the sweep repairs it (`contract.service.ts:1116-1130`; `provisioning-sweep.service.ts:151-173`).
- The move to `active` is refused until each affected tenant's command is provisioned (`contract.service.ts:1137-1151`) and writes no binding.
- An MCF metric version becoming `active` writes no tenant binding and calls nothing in L10 (`bc-core:src/registry/mcf/mcf-cert-writer.service.ts:2828-2845 @ df52506d`).
- Demo-plane versions are skipped (`contract-activation.service.ts:103-106`).

**The contract**
1. L5 and L6 (activation), L10 (tenant tables and bindings) meet.
2. Two separate records. (a) Becoming active on the platform: the state of the version row. (b) A tenant adopting it: an offer and then an adoption record (see contract 2). Activation writes no adoption.
3. The platform acts for (a). For (b): the tenant's admin or designated role accepts a value-affecting version (ruling T3). A version marked not value-affecting is adopted automatically.
4. (a): the activate call, then the readiness move. L10 builds each affected tenant's tables when the activate call moves the version to `pending_provisioning`, as today. (b): after the version is `active`, L10 writes an offer for each tenant that holds the earlier version. A not value-affecting version is adopted with the offer.
5. Each offer names the exact new version and the version it follows. Accepting ends the earlier adoption and records the new one in one transaction. Nothing recorded is altered; how the ending is recorded is not established.
6. A failed table build leaves the version in `pending_provisioning`, refused for `active`, as today. A failed offer is recorded and retried by the sweep. A failed offer never changes the platform state. Evidence is written with each act.
7. L5 and L6 may assume activation touches no tenant's reported values. L10 may assume a tenant moves only by its own acceptance or by a not value-affecting version.

**What must change to meet it:**
- L5, repair: stop writing the binding at the activate call.
- L10, needs a new record (database change: the operator's approval): the offer, and the end of an adoption.
- L10, repair: offers and adoptions written with the state change or retried by the sweep, never swallowed.
- L6, repair: an MCF version becoming `active` creates offers like a canonical one.
- Not established: whether a version that affects no tenant is treated as complete at once.

**Left to the operator:**
- Nothing new. A tenant's first adoption of a version is made by the enabling act of contract 6. Rulings T16 and T17 cover classification and acceptance.

## Stitch contract 4: The set of metrics that can be offered
**Between:** L6 (Metric Contracts and certification), L8 (metric directory), S4 (Pricing and subscription). DL (Delivery to a tenant) reads the result.
**Today (read at bc-core df52506d, bc-docs 1860bf65):**
- No record of "released" exists. No table or column in bc_platform_dev holds it (a reader's check, 2026-11-14).
- "Offerable" is a state test, written three times: `bc-core:src/boundary/metric-spec-loader.ts:236-237`, `bc-core:src/tenant-views/beyond-metrics.service.ts:113-116`, `bc-core:src/boundary/campaign-evaluation.service.ts:168-170`. None reads a certificate; the third omits `is_current`.
- Live: 93 current versions are `active`; 82 rows in `mcf.mcv_live` (query, 2026-11-14). The dossier says 14 of the `active` ones hold no certificate (dossier figure, not re-checked).
- `pricing.package` has no metric column (a reader's check, 2026-11-14).
- The directory's `realization_operative` guard also accepts `approved` versions (dossier figure, not re-checked).

**The contract**
1. L6 certifies. L8 describes. S4 holds packages. DL offers. Only DL reads the offered set.
2. A new platform-side release record: metric, released from, released until, who, why (vocabulary.md:129). It sits beside the metric contract, not inside its state. It is appended, never altered; ending a release writes a new row. Per ruling T14 (open) it may instead be implied by package membership; this contract assumes the record.
3. A platform operator writes it, through a governed act separate from certification. The exact role is not established.
4. A person calls the act. Certification never writes it.
5. The release names the metric contract. The version offered is the current certified version at the time of each read. Per vocabulary.md:137, a new certified version of a released metric stays released.
6. The act refuses a metric that is not certified (state `active`, current, standing `audit_admit`, parent not archived: `bc-core:src/registry/mcf/certified-active-predicate.ts:17-38`). If certification is later withdrawn, the metric leaves the offered set at the next read. Tenants that already enabled it keep their tables (vocabulary.md:137).
7. Offered set = certified and currently released. One predicate, read by all three readers. Subscription (contract 6) may assume every offered metric is certified. Nobody may assume more. Under ruling T6, the interim package says "all" and means "all released".

**What must change to meet it:**
- L6/DL: one shared predicate replaces the three state tests. Repair. Needed by the thread.
- L6: the 14 `active` versions without a certificate are cleared first. Repair. Needed by the thread (not established: whether the thread's metric is one of them).
- DL: the release record and its act. Needs a new record (database change: the operator's approval). Designed, not built in the program (ruling T2); until built, "every certified metric is treated as released" stays.
- L8: the realization guard accepts `active` only. Repair. Designed, not built in the program.

**Left to the operator:**
- Release attaches to the metric contract or to a version. Options: metric contract; version. Recommendation: metric contract (vocabulary.md:136).
- Whether the release record is built for the thread or "treated as released" stays. Options: build; stay. Recommendation: stay, by T2.
- DEC-c220e4 says every active metric is seen; it needs amending once release exists (vocabulary.md:293).
- Whether "released" is a record for each metric or is implied by membership of a package is ruling T14; this contract is written for a record and is amended if T14 decides otherwise.

## Stitch contract 5: What a metric version requires
**Between:** L6 (Metric Contracts and certification), L9 (chain status), L10 (tenant onboarding: bindings and provisioning). L5 (canonical contracts) and L2 (source contracts) sit between.
**Today (read at bc-core df52506d, bc-docs 1860bf65):**
- No record says what a version requires. The walk goes from `grain_entity_id` to the one active canonical contract, then to its source contracts (`bc-core:src/schema-provisioner/metric-chain-reverse-walk.service.ts:46-105`).
- The chain judge derives the same thing again (`bc-core:src/registry/mcf/mcv-chain-status.service.ts:445-522`, `grain_cc_active` at 471-476).
- The walk refuses if zero or more than one canonical contract is active (`metric-chain-reverse-walk.service.ts:58-68`).
- Schema holds no canonical or source contract reference on the metric tables (a reader's check, 2026-11-14) item 5).
- The approval package freezes the version's own digests only (`mcf.mcv_package_snapshot`; a reader\'s check on 2026-11-14).
- Evaluation does not read the chain verdict (`functions-authoring-lanes.md`:1181, dossier).

**The contract**
1. L6 declares. L10 and L9 read the declaration. L5 and L2 are named by it.
2. One declaration on the metric version: the canonical contract and the source contracts it requires, each with its version. A metric made only of other metrics declares those metrics instead (the code already treats this as a separate case: `mcv-chain-status.service.ts:470-473`).
3. The metric's author writes it as part of the version. Certification records it in the approval package.
4. Writing the version, and certification, which checks it.
5. Each entry names a contract and a version. The declaration belongs to one metric version and is never altered. A changed requirement is a new version.
6. L10 refuses to enable a metric whose declaration is not met, and names the missing item in the refusal. It never writes a guess in its place. Whether certification also refuses such a version is ruling B23 and is not decided here.
7. L10 may assume the declaration is complete and read it without walking. L9 may assume the same. Neither may assume the declared contracts are still active later; the judge records that.

**What must change to meet it:**
- L6: the declaration record. Needs a new record (database change: the operator's approval). Needed by the thread.
- L10: read the declaration, with the walk kept only as a check. Repair. Needed by the thread.
- L9: judge the declaration, not a second derivation. Repair. Designed, not built in the program.
- L6: certification records the declaration in the approval package. Repair. Needed by the thread.

**Left to the operator:**
- This contract answers the first half of ruling T19: what a metric version requires is declared on the version, not inferred each time. Recommendation: approve it so.
- Whether the chain verdict is a gate on certification is ruling B23, not re-asked.

## Stitch contract 6: From subscribed to enabled
**Between:** S4 (Pricing and subscription), DL (Delivery to a tenant), L10 (tenant onboarding: bindings and provisioning).
**Today (read at bc-core df52506d, bc-docs 1860bf65):**
- No Subscription, entitlement or package-to-tenant record exists (query, 2026-11-14; a reader\'s check on 2026-11-14)). `tenant.subscription` and `tenant.subscription_event` do not exist.
- Three chapters assume three acts: adoption by `tenant.contract_binding` (`bc-docs:docs/operating-model/tenancy-and-binding.md:98`); entitlement on a Subscription (`bc-docs:docs/operating-model/tenant-entitlement-enforcement.md:58`, "Not yet wired"); state alone (`bc-docs:docs/operating-model/metric-lifecycle.md:52-53`).
- The act that exists: `POST /schema-provisioner/onboard-metric`, which writes bindings and enqueues commands (`bc-core:src/schema-provisioner/metric-onboarding.service.ts:78-124`). It checks no subscription or release, and answers "accepted" for a metric with no active version (`tenant-provisioning-enqueue.service.ts:107`).
- No metric-family binding is ever written; only canonical rows exist, 17 (query, 2026-11-14).
- Other origins also enqueue: evaluation, the sweep, canonical activation (`bc-core:src/boundary/governed-metric-persistence.adapter.ts:530-543`; `provisioning-sweep.service.ts:236`).
- Evaluation reads none of these records.

**The contract**
1. S4 says what is subscribed. DL owns the one act. L10 carries it out.
2. The one act is "enable a metric for a tenant". It replaces the three assumed today. Adoption, entitlement and state stop being acts of their own. They become checks inside it.
3. The contract fixes the act and not the actor. Until ruling T18 is decided and built, a platform admin starts it, as today.
4. A person calls the act. Evaluation, the sweep and activation no longer start it (reads never start an act; ruling T3).
5. The act uses the current certified version of the metric and the declaration in contract 5. It records that version in the tenant's metric binding, so evaluation and enablement use the same version (ruling T3).
6. It refuses, with a named reason and writing nothing, if the metric is not offered (contract 4), is not in the tenant's package (ruling T6: a listed metric, or "all" for the interim package), or its declared requirements are not met (contract 5). A failed provisioning command is recorded and its reason is readable by contract 7.
7. Evaluation may assume that a metric with a binding and tables was enabled by this act alone. It must not assume it is still offered.

**What must change to meet it:**
- S4: a Subscription for one tenant to the interim package, and a package-to-metric record (ruling T6). Needs a new record (database change: the operator's approval). The Subscription is needed by the thread; the full package design is designed, not built in the program (ruling T2).
- L10: the act checks release, subscription and declaration, and refuses instead of answering "accepted". Repair. Needed by the thread.
- L10: write the metric-family binding with the version. Needs a new record only if the table rejects the family: not established. Needed by the thread.
- L10/RT: evaluation and the sweep stop enqueueing. Repair. Needed by the thread.
- DL: disable and unbind. Designed, not built in the program.

**Left to the operator:**
- This contract answers the first half of ruling T20: the enabling act is the only origin of a provisioning command; evaluation, the sweep and activation no longer start one. Recommendation: approve it so.
- Who starts the act is ruling T18. The package table and the interim row are rulings T11 and T12.

## Stitch contract 7: From enabled to visible to reporting
**Between:** DL (Delivery to a tenant), RT (evaluation), TS (customer portal).
**Today (read at bc-core df52506d, bc-docs 1860bf65):**
- "Visible" is recorded nowhere, and no choice exists (a reader's check, 2026-11-14); bc-docs:docs/reference/vocabulary.md:167, "treated as visible").
- The tenant list returns `snapshotBacked` (true or false) and a null snapshot; it has no reason field (`bc-core:src/tenant-views/beyond-metrics.service.ts:64-81, 163-177`).
- A read error on the list is logged and looks like "not reporting" (`beyond-metrics.service.ts:100-103`).
- The portal prints "Available" or "Not available" (`bc-portal:apps/web/src/pages/beyond/BeyondCanvas.tsx:613`).
- RT already gives outcomes with a reason: deferred, refused, unsupported (`bc-core:src/boundary/metric-evaluation-orchestrator.service.ts:55`). A missing table ends the run `failed` (`governed-metric-persistence.adapter.ts:139-141`). The tenant list does not read run rows (`beyond-metrics.service.ts:96-98`).
- Ruling T3 says the tenant is shown the reason. No code does it. What the tenant database holds for run rows: not established.

**The contract**
1. DL owns the tenant's choice to show a metric. RT owns the reason a metric has no value. TS shows both.
2. Reporting: an `accepted` row in the tenant's `progression.metric_evaluation` (vocabulary.md:168). Not reporting: the latest run row, with its status and reason. Visible: a tenant-owned record (tenant, metric, visible or hidden, who chose, when), appended and never altered. It is held with the tenant's data; the exact place is not established.
3. The tenant's admin writes visibility. Evaluation writes the run row. TS only reads.
4. The admin's choice starts the visibility record. An evaluation, however started, writes its run row. Reading the list starts nothing.
5. The list names the metric version each value belongs to. Hiding never stops production (vocabulary.md:167).
6. A tenant is told one of: not enabled; enabled, not yet evaluated; evaluated, inputs not available; refused, data not valid for the metric; refused, entity not in scope; not supported; or "could not be read". The last is never shown as "not reporting". A failed read is an error, not a value.
7. TS may assume every listed metric is enabled and visible. It may assume nothing about a value. It does not print "subscribed", "visible" or "hidden" (vocabulary.md:178).

**What must change to meet it:**
- RT/TS: the list returns the latest run status and reason, and shows an error when the read fails. Repair. Needed by the thread (ruling T3).
- TS: the portal prints a sentence for each reason. Repair. Needed by the thread.
- DL: the visibility record and the admin's route. Needs a new record (database change: the operator's approval). Designed, not built in the program (ruling T2); "treated as visible" stays.

**Left to the operator:**
- Whether "reporting" is always said with its period. Recommendation: yes, "reporting for (period)", as the vocabulary page already allows.
- The words a tenant is shown for each reason are ruling T22; this contract fixes only that a reason is recorded and can be shown, and that a failed read is never shown as "not reporting".

## Stitch contract 8: From certified to released, and where proof sits
**Between:** L6 (Metric Contracts and certification), PV (proof), DL (Delivery to a tenant).
**Today (read at bc-core df52506d, bc-docs 1860bf65):**
- Proof is a pin on the demo plane, `demo.metric_proof_pin`, 4 rows, all `match`. It has no foreign key to the metric version (query, 2026-11-14).
- The join is `mcf.demoed_evidence_bridge`, by approval package hash, with a foreign key to the version and the pin held as a uuid plus a sha256. 2 rows, both `partial` (query, 2026-11-14).
- The read is `readClaim`: `VALIDATED`, `CERTIFIED` or `NONE` (`bc-core:src/registry/mcf/demoed-evidence-bridge.service.ts:469-492`). Only a controller calls it.
- Neither "released" nor "proven" is readable by DL (``functions-runtime-delivery-support.md`:313`).
- A failed proof never rejects or decertifies (`bc-docs:docs/governance/adrs/ADR-eb612b.md`, BR6; vocabulary.md:230). A proof does not carry to a new version (`ADR-025bfc.md:25-29`).
- ADR DEC-ec1434 designs a tenant-side record for the same claim; its own text says nothing was built (`ADR-ec1434.md:29, 47`).

**The contract**
1. L6 certifies. PV produces proof. DL reads both and offers.
2. The proof record is the bridge row with its attestation. It sits beside the metric version, not inside it. It names the version by its approval package hash, and the pin by uuid and sha256. Proof for a tenant's own source is a separate record, not built.
3. A session under a recorded operator grant writes the bridge and the attestation (as today). Nobody else.
4. A person runs the command. Nothing starts proof when a version is certified.
5. A proof belongs to one certified version. A new version has no proof until it is bridged again.
6. A proof that does not match, or is stale, changes nothing: the metric stays certified and reads as not proven. It is never "done" for a tenant (ruling F8: "Demoed" names proof on the demo plane only).
7. DL may assume nothing about proof unless the bridge head is current and covers the metric. L6 may assume proof never changes a certificate.

**What "released" requires of proof:** nothing. Released needs a certified version (contract 4). Proof is read and shown beside it. This follows the decision records, which make proof a claim read at the time and not a gate.

**What must change to meet it:**
- PV/L6: name the bridge and attestation as the proof record in the vocabulary, and put the status word "validated against (source)" on that read, with "Demoed" the name of the demo-plane proof (ruling F8). Repair. Needed by the thread.
- DL: a read of the proof claim beside each offered metric. Repair. Designed, not built in the program (ruling T2).
- PV: a foreign key from the pin to the metric version. Needs a new record (database change: the operator's approval). Designed, not built in the program.
- PV: a record per tenant for the fourth condition of "done" (agreement with the tenant's own source). Needs a new record (database change: the operator's approval). Designed, not built in the program.

**Left to the operator:**
- Whether release should require a current proof. Options: no requirement; require it. Recommendation: no requirement, as written above.
- How proof is produced, from what an expected value is worked out, and whether proof on demonstration data counts toward "done" are rulings B4, B5 and B11, not re-asked.

## Stitch contract 9: From a snapshot to an action

**Between:** RT (Runtime) and A1 (Action and intervention).

**Today (read at bc-core df52506d, bc-docs 1860bf65):**
- Nothing of A1 is built. The action boundary was retired in commit 4ab0ea0b (2026-09-29); `git grep` for `ActionRepository`, `createActionObject` and `ActionEvaluator` finds nothing.
- RT writes five event types and none concerns an action (`src/boundary/runtime-event.service.ts:21-26`). The `event` trigger mode "is not an evaluation invoker" (`docs/operations/runtime-operations.md:44-53`).
- `contract.intervention_contract`, its version table and its approval table hold 0 rows (queried 2026-11-14).
- The design exists: an Action Object is "bound at creation time to one or more Metric Snapshots" (`docs/foundation/the-object-model.md:132-142`; `docs/operating-model/action-evaluation.md:91-100`).
- The program lists A1 as designed and not built (`platform-refactor-program.md:224`). RT's lock conditions do not mention it (dossier `functions-runtime-delivery-support.md`:176`).

**The contract.** Nothing in this contract is built in this program. It records what RT must keep true so that RT can be locked without closing the door.
1. RT (the snapshot) and A1 (the action). Evidence (EV) is read by both.
2. A Metric Snapshot passes by reference: its identifier, with the metric contract version, the canonical contract version, the period, the legal entity and the tenant. The record that holds the reference on A1's side is not defined.
3. Not defined. The design names an "Action Evaluator"; none exists.
4. Not defined. A completion event from RT, a schedule or a command only are all possible; none is chosen.
5. The snapshot is referenced at the version it was produced under and is never rebound (`action-evaluation.md:99`). The intervention contract version is the active one at creation; how a tenant adopts it is not defined.
6. Not defined beyond the design: a failed trigger check ends with no Action Object and a terminal outcome on the Run (`action-evaluation.md:98`).
7. RT may assume nothing about actions. A1 may assume snapshots are preserved, never changed and carry Evidence.

**What must change to meet it**
- RT, lock condition: a Metric Snapshot is immutable, carries the six identifiers in item 2, and has Evidence. Repair, by writing it into RT's chapter and its lock test. Not established whether today's records already hold all six.
- RT: keep the completion event `metric_run_completed`. Repair (nothing to add).
- A1: nothing is built. The function goes on the "designed and not built" list at phase 11.

**Left to the operator:**
- Nothing now. What starts an action is decided in the Define step of Action and intervention. Rulings B29 and T23 are not re-asked.

## Stitch contract 10: A version being superseded
**Between:** L5 Canonical Contracts; L6 Metric Contracts and certification; DL Delivery to a tenant.

**Today (read at bc-core df52506d, bc-docs 1860bf65):**
- Activating a successor stamps the old version `supersede_after = now() + 48 hours` (`bc-core:src/registry/contracts/contract-version.repository.ts:204-222 @ df52506d`). Nothing compares that stamp to the clock; only a person's supersede call sets `superseded` (a search of the engine for a reader of that stamp finds none).
- Live: two canonical contracts each have two versions `active`, stamps past (contract `0947b25a-f7a6-4175-89a0-11220ce07336` 3.0.0 beside 4.0.0; contract `26e063b7-beed-4a97-86ae-24a258335b6b` 2.0.0 beside 3.0.0). Their bindings are not ended.
- The metric supersede route needs two different parent metrics, each `active` and `is_current` (`bc-core:src/registry/mcf/mcf-cert-writer.service.ts:3235-3266 @ df52506d`). A new version under the same parent is not superseded by any act; the sibling stays `active` (`:2408-2417`).
- No metric has been in two-in-force yet: 93 `active` and `is_current`, none `active` without it (a reader's check, 2026-11-14).
- The 48-hour window cites a decision now marked superseded (`bc-docs:docs/development/platform-refactor-program/functions-runtime-delivery-support.md:463 @ 1860bf65`).

**The contract**
1. L5 and L6 (state), DL (tenant adoptions) meet.
2. The platform's record: state `superseded` with its transition record, and for metrics the supersession record. A tenant's record: its adoption of the successor (contract 3).
3. L5 and L6 act on the platform state. The tenant's admin or designated role acts on its own adoption.
4. For the platform: a command issued by the scheduled cycle when the window has passed. A person may also issue it. For the tenant: acceptance of the offer.
5. The version superseded is named: for a metric, by the successor's `supersedes_version_uid`. A successor under the same parent supersedes its predecessor in the act that makes it current. The different-parent route remains for a replacement metric.
6. If the pair is invalid, the act is refused and the version stays `active`; the cycle records the refusal and tries again. A version already adopted by a tenant stays readable by its exact version whatever its state (contract 2).
7. Two versions are in force for the platform from the successor becoming `active` until the old version is `superseded`. For one tenant, from the offer until it accepts. Superseding never ends a tenant's adoption. Only acceptance ends it. If the adopted version becomes incompatible, evaluation is refused with a reason (ruling T3).

**What must change to meet it:**
- L5, repair: a built finisher moves a stamped version to `superseded` at the window's end. The window length moves into a declaration.
- L6, repair: the same-parent successor supersedes its predecessor in one transaction.
- RT, repair: campaign scope stops listing a version that is not current for its tenant.
- DL, needs a new record (database change: the operator's approval): the end of an adoption (contract 3).

**Left to the operator:**
- Nothing new. Whether a tenant may stay on an earlier version without limit, or a final date is named in the offer, is part of ruling T17; recommendation when it is put: no limit, as ruling T3 is written. Whether the earlier version is superseded at once or after a window is ruling B13.

## Stitch contract 11: A tenant's first user, and a tenant's end

**Between:** S3 (Tenant lifecycle), S2 (User and access), S1 (Authentication), PR (Privacy and retention).

**Today (read at bc-core df52506d, bc-docs 1860bf65):**
- Creating a tenant is an operator command with no flag for an administrator (`src/tenant-management/lifecycle/tenant-lifecycle-cli.ts:7-10,56-62`); it ends the tenant `active` (`tenant-management.repository.ts:382-433`).
- Creating a user writes one Cognito user and does not check that the tenant exists (dossier `functions-shared-services-operations-development.md`:187; handler not re-read). "The two acts are separate and nothing links them" (`functions-shared-services-operations-development.md`:200).
- The decided design (`ADR-cf6d3b.md:66-73,96`): birth ends in `onboarding_incomplete`; `active` needs a verified admin and a Subscription. Migration 0034 is said to be unapplied (not re-checked).
- Retirement is three commands and keeps the registry row (`tenant-retirement.service.ts:1-9`); no retention code is called. `operations.retention_policy` has 0 rows; no schedule runs retention.

**The contract**
1. S3 creates; S2 and S1 supply the first admin; PR receives the end.
2. At creation, one record: the tenant slug and the first admin's email, written in one act. At the end, the `tenant_retired` evidence row (tenant, date, receipt) is the record PR reads. What PR keeps is not defined (ruling T26).
3. Creation: the operator, by one command. The end: the operator, with the separate recorded grant for the drop. PR: an operator command (G24 open).
4. The operator's command. Nothing else starts either act.
5. Creation uses the bc-db commit and release the operator names. The admin carries the tenant slug as a claim.
6. The tenant is created in a waiting state and becomes `active` only when its first admin is verified, as decision DEC-cf6d3b says. If the admin cannot be created, the tenant stays waiting or the act undoes what it did; it is never `active`. Whether today's creation service can undo a database it made is not established.
7. S3 may assume a first admin exists once creation reports success. S2 may assume the tenant exists. PR may assume a retirement record exists before it acts.

**What must change to meet it**
- S3: the creation act takes the admin email and calls S2. Repair.
- S2: the user route checks the tenant exists. Repair.
- S3: the waiting state until the admin is verified. Needs a new record (database change: the operator's approval), if migration 0034 is withdrawn (G12).
- PR: reads `tenant_retired`. Repair.

**Left to the operator:**
- Whether the drop of a retired tenant's database is refused until Privacy and retention has recorded what is kept. Options: yes; no. Recommendation: yes.
- Not re-asked: rulings T4, T5, T7 to T10, T25, T26, G7 to G12 and G24.

## Stitch contract 12: A change in the platform reaching the guide

**Between:** DV (Development) and every function.

**Today (barecount-devhub b00e9f85, bc-docs 1860bf65, bc-core df52506d):**
- At plan save and close, DevHub records the chapters a session says it consulted, each checked at `origin/main` (`src/lib/chapters-consulted.js:1-11,47`). Sessions opened before 2026-11-14T14:00Z are exempt. It does not compare the list with the files the commits changed (not seen).
- The close gate demands each changed durable file be registered (`src/lib/close-gates.js:72-106`). It does not say which chapter a code change obliges.
- bc-docs has one workflow, `adr-hygiene.yml`; neither audit checks that a chapter changed. No pull-request template or CODEOWNERS file exists in four repositories. bc-core has no check naming bc-docs.
- "Nothing obliges a session to read or update a chapter" (dossier `functions-shared-services-operations-development.md`:759). `docs/guide/` does not exist.

**The contract**
1. DV, and each function that changes.
2. The change record carries, for each commit that changes a function's surface, the function code, the chapter path, and either the chapter's changed commit or a stated reason for no chapter change.
3. The session records it. The Chief judges. DevHub refuses.
4. Session close, and the pull request. A merge starts nothing.
5. The chapter is read and compared at bc-docs `origin/main`, with the head recorded.
6. Before a function is locked, a missing chapter change is recorded and shown. After lock, the close is refused, unless a ruling reopens the function (program: "A locked function is reopened only by a ruling"). A reason of at least 40 characters is the only other way through, and it spawns a task.
7. A session may assume a locked chapter is current. It may not assume it of an unlocked one (F5).

**What must change to meet it**
- DV: the assignment of surfaces to functions (phase 1) becomes the table the check reads. Repair.
- DV: a close gate that compares changed files with the chapter of their function. Needs a new record only if the "reason" is stored apart from the change record (database change: the operator's approval); otherwise repair.
- DV and all: a decided ADR carries its chapter change in the same pull request (G33).

**Left to the operator:**
- Where the check lives. Options: DevHub's close gate; a check on each repository's pull requests. Recommendation: DevHub's close gate, because every session passes it.
- Not re-asked: rulings G33, G30, G32.
