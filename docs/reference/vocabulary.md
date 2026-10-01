---
id: vocabulary
title: "Vocabulary: status words"
status: approved
authority: authoritative
governing_adrs:
  - DEC-c897cd (this page is the only authority for status words)
  - DEC-c220e4 (a tenant's metric scope)
  - DEC-21ca17 (the versions marked active without a certificate)
  - DEC-fa9424 (the directory entry as the only authoring door)
---

# Vocabulary: status words

**The only authority for status words** (ADR DEC-c897cd). Where another document, screen, memory or tool output disagrees with this page, this page wins and the other is corrected. A new status word enters here first, in the same change that first uses it.

**First slice: the words for a metric's life.** Approved by the operator on 2026-10-01, desk grant `2026-10-01T06-36-21-158Z-648f1a32` (text SHA-256 `648f1a32faeea25c5c2639d91617b00a6582ead9c8ccc7d3826db8d9c117d498`), as written on the Architect page in barecount-devhub pull request 187 at commit `141b1af35366c92bf0468fdb074c112ca82b15a4`. This page carries that text with three changes only: this header replaces the page's draft status line, and the two questions the operator answered in that grant (what "available" means; what happens when a release is reversed) now state his answers. Everything marked "not built", "no record yet" or "a design act" below is still so.

**The operator's direction (2026-10-01, to the Chief):** "there is too much noise about number of metric and overlapping terms (active/avilable/active certified -- a huge trap) ... Numbers should never go in memory. Define what is done for metric and its life (not lifecycle)" and "Let us build and maintain approved vocabulary / taxonomy and end this mess?"

**Read at:** bc-docs `origin/main` a6f4fc7; bc-core `origin/main` 4f163044; the live platform database, read-only, 2026-10-01. The Chief's helper census of where each word is used (barecount-devhub `.claude/briefs-view/drafts/clean-slate-inventory-2026-10-01.md`, part D) was used as a list of leads, not as a source.

**This page holds no counts.** Section 6 says where each count is read.

## 1. Why the words became a trap

One word has been used for four different things:

| The thing | Example of the confusion |
|---|---|
| **A candidate:** an idea for a metric that is not yet written as a contract | "published" is a status of a candidate in the reservoir, and was also the old name for marking a version active |
| **A metric on the platform:** a Metric Contract and its versions | "active" has meant a database state, "certified", "in use", and "the end of authoring", and some versions were marked active with no certificate |
| **A metric for one tenant:** whether the tenant has it, shows it, and gets values for it | "active on Kaveri", "live", "producing", "bound" and "activated" have all been used for this, and no record holds any of them |
| **The route itself:** whether the way a metric is produced can be trusted | "proven" has meant "went green once" and "works by the mandated route with no workaround" |

The repair is the same for every word: **say which thing the word describes, and tie it to the one record that makes it true.**

## 2. The rules of this page

1. **One word, one meaning, one record.** A status word is approved only when a named record and field makes it true. If no record does, the word is not approved, however useful it sounds.
2. **A count is a read, never a memory.** Anyone who needs a number reads the field named beside the word, at that moment, and says where it was read. No count is written into memory, a brief, a chapter or a task title.
3. **Foundation's state names stay as the values of the state field.** The seven states of a Metric Contract version are named in `docs/foundation/the-contract-grammar.md` ("MCF Metric Contract family"), and this page renames none of them and adds none. For six of them the plain word and the field value go together. For one they differ: the field value is `active`, and the word people say is "certified". Changing the Foundation state name itself, so that the field says what people say, would be a change to Foundation: a design act for the operator to decide, named here and not done.
4. **A word for a tenant always names the tenant.** "Enabled for Kaveri", never "enabled".
5. **A new status word enters through this page first,** in the same change that first uses it.

## 3. A metric's life, in the operator's six groups

The operator's own outline (2026-10-01, through the Chief, verbatim): "to me a metric life cycle: 1. Seed (lives in seed resvoier) 2. Queued/Candidate (to be entered in the metric directory) other states - Rejected/Seeded etc 3. Registered (in the directory) 4. Then the onboarding flow: Draft, In Review, Approved, Awaiting Certification (need this?), certified, blocked, 5. General management: superseded, retired, abandoned (need this?), archived (was there, but should be used for legitimate entries only not for mistakes) 6. Tenant: Certified=Available (same), Subscribed/Enrolled, Enabled/Disabled, Reporting".

The page follows those six groups. Each word is tied to its record, or the page says that no record holds it.

### Group 1. Seed

| Word | Plain meaning | True when | Made true by |
|---|---|---|---|
| **seed** | An idea for a metric, kept as raw material. It is evidence, never a to-do list | a row in `mcf.seed_metric` (the reservoir) | The import of the seed catalogue |

A tenant sees nothing.

### Group 2. Candidate, and the other seed statuses

These are statuses of a **seed**, in `mcf.seed_metric.status_code`. They are never said of a metric.

| Word | Plain meaning | True when | Made true by |
|---|---|---|---|
| **candidate** | A seed nobody has picked yet | status is `candidate` | The import |
| **deferred**, **rejected** (of a seed) | Set aside for later; will not be written as a metric | status is `deferred`; `rejected` | A decision on the seed |
| queued, in review, authored, published (of a seed) | The seed's progress on the old seed-first route: an intake was created from it; it was under review; a draft was written from it; a contract from it was marked active | status is `queued`, `in_review`, `authored`, `published` | That route, which is retired: since ADR DEC-fa9424 writing starts from a directory entry, the from-seed intake is refused, and seeds stay as evidence |

- **What the record does not have: "queued, to be entered in the directory".** No field says a seed has been picked for the Metric Directory. If that step should be visible, it is new (section 8).
- **"Seeded" is not a status.** Say "seed".
- Whether any live act still writes the four old statuses is to be confirmed (section 8).

### Group 3. Registered

| Word | Plain meaning | True when | Made true by |
|---|---|---|---|
| **registered** | The metric has an identity in the Metric Directory: what should exist, and why | a row in `metric_directory.member` | The governed directory acts |

- **The rule: nothing is drafted before it is registered.** It is decided: ADR DEC-fa9424 makes the directory entry the only door to writing a metric. It matters because the governed acts that withdraw or re-admit a certified metric find it by its directory entry; the defect in section 3a exists because older versions were written without one.
- **It is not fully enforced.** The direct-submission intake still accepts a proposal with no directory entry (bc-core `src/registry/mcf/operator-direct-adapter.ts`, where the member reference is optional). Making it required is a build act for the Platform Controller, named here and not done.
- **A second "blocked".** A registered metric can be held for a named reason (`metric_directory.member.intent_state_code` is `blocked`, with a blocker code). Say "registered, blocked in the directory", never plain "blocked", which belongs to certification (group 4).

A tenant sees nothing.

### Group 4. Onboarding: from draft to certified

The record is the version row, `mcf.metric_contract_version`, field `governance_state_code`, with `is_current`, and the parent row `mcf.metric_contract`. The transitions are enforced in the database (`docs/reference/lifecycle-map.md`, section 1) and each is written by a governed service, never by hand.

**The rule, in the operator's words:** "before certification a metric can not be active", and "certified (is deployable to tenant so in a way "active" for platform)". So the status people say is **certified**, and it means deployable to a tenant. "Active" is not said as a status. It is the value the state field carries for a certified version, and Foundation gives that value the same meaning: "`active` asserts panel certification" (`the-contract-grammar.md`, "MCF Metric Contract family").

| Word | Plain meaning | True when | Made true by |
|---|---|---|---|
| **draft** | Written down as a contract. Nothing is claimed about whether it is right | state is `draft` | The admission panel approves a proposal and the governed writer creates the version |
| **in review** | Being reviewed. Still no claim that it is right | state is `review` | The governed transition from draft |
| **approved** | Review is complete and it may be sent for certification. **Approval is not a certificate** | state is `approved` | The governed approve act |
| **awaiting certification** | Waiting to be judged by the certification panel. Nothing in this state is evaluated for any tenant | state is `audit_pending` | The request for certification, or the withdrawal of an earlier certificate |
| **certified** | Passed by the certification panel and **deployable to a tenant** | state field `active`, `is_current`, parent not archived, **and** a standing certification record whose action is `audit_admit` (the `certified_active` line of the readiness projection) | The certification panel's pass, then the governed admit act, which the database allows only with that record |
| **released** | The platform has chosen to offer this certified metric in its portfolio. Reversing a release returns it to certified, with nothing else changed | **no record yet. This is new.** Proposed: a separate portfolio record on the platform side (metric, released from, released until, who, why), not an eighth state. Until it is built, every certified metric is treated as released | The platform's own choice, by a governed act that does not exist yet |
| **certification blocked** | Its certification was invalidated. It is not evaluated | state is `audit_blocked` | The invalidation act |

- **"Awaiting certification (need this?)" Yes. The enforced transitions need it**, for three reasons. (1) An approved version cannot become certified directly: the database allows only `approved` to `audit_pending`, and `audit_pending` to `active`; the direct door was closed on 2026-07-15. (2) It is where a certified version returns when its certificate is withdrawn (`active` to `audit_pending`). (3) It is where the defect versions of section 3a go. Folding it into "approved" would change the enforced state machine and would mix "reviewed, not yet sent to the panel" with "certificate withdrawn". Not proposed.
- **Blocked has no way out today.** The database lists the exit from `audit_blocked` and then refuses it. bc-db migration 0029 is **not** that exit: 0029 is the recorded exit for a version awaiting certification that the panel **rejected**, which otherwise waits forever and holds its name. 0029 is on bc-db `main` and was not applied to the live database when read on 2026-10-01. No version was blocked on that date. The way out of blocked is an open design item (section 8).
- **The chain verdict is a separate question.** `mcf.mcv_chain_status.verdict_code` is green, amber or red. It says whether the contracts a metric depends on line up. It says nothing about values, it is not a certificate, and it gates nothing. Say "chain verdict green", never "ready" or "chain complete".
- **"Active" is not a second status.** Nobody reports "active metrics"; they report certified metrics, read from the certified line.
- **Why "released" is a separate record and not a new state.** The seven states are Foundation's, and they say how far a version has come through governance; release is the platform's choice about its portfolio, and the operator wants its reversal to "simply go back as certified". A record beside the metric does exactly that and leaves the certificate and the state machine untouched. An eighth state would change Foundation and the enforced transitions for a choice that is not about correctness. Release is proposed for the metric as a whole, so a new certified version of a released metric stays released.
- **When a release is reversed** (the operator's answer, grant `2026-10-01T06-36-21-158Z-648f1a32`): the metric goes back to certified, and tenants that already have it enabled keep it. Taking a metric away from tenants that rely on it is what "retired" is for.

A tenant sees nothing until the metric is released (today: certified, since every certified metric is treated as released).

### Group 5. General management

| Word | Plain meaning | True when | Made true by |
|---|---|---|---|
| **superseded** | Replaced by a newer certified version. Values already produced stay as they were and are never rewritten | state is `superseded` | The governed supersede act, paired with the new version being certified |
| **retired** | A certified metric withdrawn from the portfolio, with its history kept | parent `archived_at` is set, and the version's state field was `active` | The governed retire act (see the gap below) |
| **abandoned** | Dropped without ever being certified: a draft, or a version in review; and, once 0029 is applied, a version the panel rejected | parent `archived_at` is set, and the version was draft or in review (for a rejected version: also a row in `mcf.rejected_version_retirement`, once 0029 is applied) | The governed abandon act; the rejected exit of 0029 |
| archived | **Not a spoken status.** It is the field, `archived_at` on `mcf.metric_contract`, that both retired and abandoned set | (the field) | (the acts above) |

- **"Abandoned (need this?)" Yes.** A draft or a version in review can only move forward in the state machine, and the version table has no abandoned state: the governed abandon act archives the parent. Without this word, every dropped draft would be called retired or archived, which is the mixing the operator wants to end. It is the word that keeps mistakes out of "retired".
- **"Archived for legitimate entries only": the record does the opposite today. This is a gap.** Every act that sets `archived_at` is written as an exit for a mistake or a rejection: abandon (a failed draft or review), retire ("governed withdrawal of an ACTIVE metric authored in error", bc-core `src/registry/mcf/mcf-mcv-retire.controller.ts`), retire-demoted-duplicate, and the rejected exit of 0029. No act is written as the legitimate end of a certified metric, and the field cannot tell a legitimate retirement from the removal of a mistake.
- **The proposal, a design act named and not done:** "retired" means a legitimate withdrawal only. A certified metric found to be wrong is not retired: its certificate is withdrawn, it returns to awaiting certification, and it is then corrected by a new version or abandoned through the rejected exit. The retire act's stated purpose, and a reason on its record, would change to match. Until the operator decides that, "retired" on this page means only what the record can show: archived while certified.

A tenant stops seeing a retired metric. A superseded version's values remain as records.

### Group 6. Tenant

**Which word "available" equals** (the operator's answer, grant `2026-10-01T06-36-21-158Z-648f1a32`): **available means released.** A tenant is offered what the platform has released, not everything it has certified. Until the release record is built, the two are the same set.

The operator's ladder, with his answer of the same day: "enabled/disabled is producing state. We need one more - Visible/hidden". So there are **two separate switches**: one says whether the metric is produced for the tenant, the other says whether the tenant's users see it. Each step needs the ones before it.

| Word | Plain meaning | True when | Made true by | What the tenant sees |
|---|---|---|---|---|
| **available** | In the platform's portfolio: any tenant could have it. It is the tenant-side word for a released metric | the same record as **released** (group 4); until that record exists, the same as **certified** | The platform's release | The metric exists in the catalog |
| **subscribed** | The tenant's package includes the metric | **no record yet.** It will be the metric entitlement on the tenant's Subscription record, which is not built (ADR DEC-c220e4 sets the latest moment). Until then, by that ADR's rule and not by any record, every active tenant is treated as subscribed to every available metric | A platform-side governed act on the tenant's Subscription. The tenant does not write it | The metric is in the tenant's own list |
| **enabled / disabled** | Whether the metric is **produced** for that tenant: its tables and contract bindings exist there, so it can be evaluated on the tenant's data | **Enabled:** the **current** provisioning command for the metric's current version is `provisioned`, and so are the current commands for the canonical and source tables it depends on, with their bindings recorded (`schema_provisioner.provisioning_command` and its transitions; `tenant.contract_binding`; `tenant.tenant_binding`). An accepted request, or an obsolete or historical command, does not count. **Disabled: not built.** Nothing switches production off for one tenant today: there is no governed unbind (`docs/onboarding/tenant-metric-binding.md`, "Rollback / unbind"), and evaluation reads no binding. Until it is built, a metric is either enabled or "not enabled" | **The tenant's admin** (the operator, 2026-10-01). **That route is not built:** today only a platform operator can start the governed onboarding act, and the provisioning worker then creates the tables. An admin's choice would have to be recorded and then start that same act and worker | While the tables are being created: "being enabled". Then: enabled. If it fails: not enabled, with the failure shown |
| **visible / hidden** | The tenant's admin chooses whether an enabled metric is shown to the tenant's users. It never stops production | **no record today, and no such choice exists today. This is new.** It needs a record the tenant owns (tenant, metric, visible or hidden, who chose, when) and a route for the tenant's admin. Until it is built, every metric is treated as visible | The tenant's admin (the operator, 2026-10-01) | Visible: shown to the tenant's users. Hidden: not shown; it is still produced, and its values are kept |
| **reporting** | The metric has at least one accepted value on the tenant's own data. With a period: "reporting for (period)" | an `accepted` row in the tenant's `progression.metric_evaluation` with its snapshot row in the tenant's `fact.ms_` table; for a period, that row's fiscal period | The governed evaluation act | The value, for each period it is reporting for |

- **"Subscribed" is kept.** The record it will live in is the Subscription, and the catalog chapter already says tenants "subscribe to a subset". "Entitled" is dropped as a status; "entitlement" stays as the name of that part of the Subscription record. "Enrolled" is not needed.
- **"Enabled" replaces "set up for (tenant)"**, the operator-side word of earlier revisions. The records are the same.
- **"Reporting" replaces "working".** "Working" suggests the number is right, and that is what "done" is for (section 5). "Reporting" says only that a value exists and was accepted.
- **Both switches belong to the tenant's admin** (the operator's answer). Neither route exists today: "enabled" is started by a platform operator, "disabled" is not built, and "visible / hidden" has no record.
- **Today, as built:** evaluation does not check that a metric is released, enabled, subscribed or visible before it runs (ADR DEC-c220e4 records the rule in force). A metric that is not enabled cannot report, because its table does not exist.

**Subscribed, enabled and visible, but the tenant's data cannot support it.** The tenant sees the metric in its list, **not reporting**, with no value. That is true to the records. Today the screen gives no reason. The reasons exist as separate facts (no source data for it; evaluated, and the result deferred or rejected), and the words a tenant is shown for each are a later slice (section 8).

Until the records for "subscribed" and "visible" exist, a tenant-facing screen does not print "subscribed", "visible" or "hidden" against a metric (DEC-c220e4, the ruling on tenant-facing surfaces).

"Shown in the portal" is not a status word. It is something a person checks in the running application and reports as a check, with the date.

## 3a. A defect, not a status: versions marked active with no certificate

**What it is.** Some versions carry the state `active` in the database and have no standing certificate. Under the rule above they are **not certified**, and so not deployable to a tenant. They are a defect, and this page gives them no status word. In reports they are named in full: "marked active without a certificate (defect)".

**How it happened, from the record** (`docs/operating-model/metric-lifecycle.md`, section 3; ADR DEC-21ca17):

1. Until July 2026, making a version active did not need certification. The act recorded a `metric_transition` record and meant "published".
2. On 2026-07-15 the database closed that door: a version reaches `active` only with a certification record.
3. On 2026-08-02 the operator dispositioned the versions that had been made active the old way (DEC-21ca17): they are raw material for certification, and they were moved to awaiting certification through the governed reintake act.
4. **The deadlock.** That act identifies a metric by its entry in the Metric Directory. A named group had no usable entry (no directory member, or a member with no member version), so the act could not move them. DEC-21ca17 item 3 left them marked active, named in the manifest, pending the minting of their directory identities and a second manifest. Item 4 set the deadline: the disposition must be complete before the first real tenant onboards. The follow-up (DevHub TSK-fa743d, owner Metric) is parked.

**What it does today.** These versions are in every tenant's list, and the evaluation act will evaluate one if asked. None of the metrics enabled for the pilot tenant is among them (the Architect's read-only query of 2026-10-01, comparing the pilot's provisioning commands with the line named below).

**Where to read it.** The group: the `residue_legacy_active` line of `GET /api/registry/mcf/readiness-projection`, and by name in DEC-21ca17 item 3 and its manifest (excluded cohort `pre_c8_member_identity_unresolvable`). A second line, `unattributed_active` (marked active with no record at all), must stay empty; it was empty on 2026-10-01.

**The options for clearing it.**

| Option | What is done | What a tenant sees | Cost and limits |
|---|---|---|---|
| **1. Finish the decided route (recommended)** | Mint the missing directory identity for each, then a second manifest moves each to awaiting certification through the governed reintake act. Each is certified only through the certification panel (DEC-21ca17 items 3 and 5) | They leave the list until certified. Nothing changes for the pilot's set-up metrics | Directory work per metric, then one operator-authorized batch. It is already decided; it needs to be scheduled with the Metric Controller |
| **2. Retire each** | The governed retire act archives the whole metric | They leave the list and do not return unless restored or written again | Quick, and it needs no directory identity. But the retire act is for a metric authored in error, and these are candidates for certification, not errors. Using it here would need the operator's decision to widen what that act is for |
| **3. Leave them until the deadline** | Nothing now; clear them before the first tenant for a prospect or client | They stay listed with no value, and can be evaluated without a certificate | No work now. It keeps the state the operator has just called a problem |

**Why option 1.** It is the route the operator already decided, it uses only governed acts, and it leaves each metric able to earn its place through certification. A filter that hides these versions in the list or in evaluation is not offered: the defect is in the state they carry, and the repair is to change that state through the governed act, not to read around it.

## 4. Words that are not approved, and what to say instead

| Not approved | Why | Say instead |
|---|---|---|
| activated | No record holds an activation, for a tenant or for a metric | "was certified" (platform); "subscribed" or "enabled", whichever is meant |
| active on (tenant) | "Active" is a value of the platform's state field. It has no tenant form | "subscribed", "enabled" or "reporting", whichever is meant |
| active (as a status people say), active certified | "Active" is the state field's value, and it has also been true of versions with no certificate | "certified" |
| entitled (as a status) | Two words for one record | "subscribed". "Entitlement" stays as the name of that part of the Subscription record |
| live (as a metric status) | Used for a platform state, a tenant result, a running service and a current corpus | "certified" (platform) or "reporting" (tenant). "Live" stays for running systems and the live database |
| working, producing, has data, has a value, snapshot-backed, runtime-live | Each means a value exists; "working" also suggests it is right | "reporting", or "reporting for (period)" |
| onboarded, bound, set up, enrolled (a metric to a tenant) | Several words for one fact | "enabled for (tenant)" |
| admitted | Three different acts: source rows admitted at the admission boundary; a proposal approved by the admission panel; a version certified | Name the act: "source rows admitted", "proposal approved by the admission panel", "certified" |
| published | A candidate's status, and the old name for marking a version active without certification | "certified" for a metric; "published" only for a candidate in the reservoir |
| ready, platform ready, runtime-ready | Each bundled several facts into one word with no record behind it | Name the fact: "certified", "chain verdict green", "enabled for (tenant)", "reporting" |
| complete, chain complete | The chain record has a verdict, not a completion | "chain verdict green" |
| proven (for one metric) | Has meant "went green once" | "done for (tenant)" as defined in section 5; "proven" is kept for the route |
| seeded | Not a status in any record | "seed" |
| archived (as a status) | It is a field that both retired and abandoned set | "retired" or "abandoned" |
| blocked (alone) | Two records use it: certification, and the directory | "certification blocked"; "registered, blocked in the directory" |
| queued, published (of a metric) | They are statuses of a seed on a retired route | the metric's own word from section 3 |
| second tenant, first customer, customer tenant | Ordinals and "customer" miscount the pilot | "pilot tenant", "tenant for a prospect or client" (section 6) |

## 5. What "done" means

Two words, for two different things.

**Done, for one metric on one tenant.** A metric is done for a tenant when all six hold, and each is read from its record on the day it is claimed:

1. It is **certified** and **released**.
2. It is **enabled** for that tenant, by the governed onboarding act alone.
3. It is **reporting** for a stated period, by the governed evaluation act alone, with the proof that act writes.
4. That value **agrees with the expected value** worked out independently from the same source data for the same period, and the agreement is written down where it can be read again.
5. A tenant user **sees that value** in the portal, checked in the running application.
6. **No workaround was used at any step.** A direct edit, a bypass, an override, a hand fix or a one-off script at any step means the metric is not done, and the step's owner has a defect to fix.

**Proven, for the route.** The way metrics are produced is proven when, in the operator's four conditions: (a) it used the mandated route alone; (b) it repeats from a clean start by the written procedure alone, in a session that did not build it; (c) each stage and each handoff has its own tests that can go red, kept and re-run; (d) a second, different case passes with no change to any stage.

So "a Kaveri-proven metric" means: a metric that is **done for Kaveri**, through a route that is **proven**. One metric going green does not prove the route, and a proven route does not make any one metric done.

**No record holds "done" today.** Until one does, "done" is written only together with its six reads and their date. Section 8 names this as the first thing to build.

## 6. The tenant kinds, and where counts are read

The first three rows are **the operator's classifications, not yet status words under rule 1:** no field records a tenant's kind. They are used only as the operator defined them, and nothing may decide that a tenant is "for a prospect or client" by inference. Until a record names the kind, the act that DEC-c220e4 gates is decided by the operator, case by case.

| Word | Meaning | True when |
|---|---|---|
| **pilot tenant** | `kaveri`. It proves the mechanism and is not counted as a customer | the operator's grant of 2026-10-01 recorded in DEC-c220e4. No field records it |
| **tenant for a prospect or client** | Any tenant activated for a party outside BareCount, on any source system | no field records a tenant's kind today (open point 7) |
| **proof tenant** | A disposable tenant made for a test. Never counted as a customer | no field records a tenant's kind today (open point 7) |
| **active tenant** | A tenant whose registration is active | `tenant.tenants.status_code` is `active` |

| To know how many metrics are | Read |
|---|---|
| in each platform state; certified (the `certified_active` line); marked active without a certificate (the `residue_legacy_active` line, a defect) and with no record at all (`unattributed_active`, which must be empty); at each chain verdict | `GET /api/registry/mcf/readiness-projection` (a read model over the records above) |
| enabled for a tenant | `GET /api/schema-provisioner/tenants/<slug>/provisioning` |
| released; subscribed; visible or hidden; disabled | no record exists yet (section 3, groups 4 and 6) |
| reporting for a tenant | **for one metric:** the tenant's own `GET /api/t/beyond/metrics/<metric id>`, which returns every accepted snapshot with its value, fiscal period and period end date (bc-core `src/tenant-views/beyond-metrics.service.ts`, `governedSnapshots` and `metricDetail`; `src/tenant-views/governed-snapshot-reads.ts`). **Across metrics for a period: no single read exists yet** (section 8). The list's `snapshotBacked` flag is weaker: it is true when the tenant has any accepted evaluation of the metric, for any period, and it does not check the snapshot row. It is never reported as "reporting" |
| done for a tenant | no single read exists yet (section 8) |

## 7. How the page is kept (design only; nothing here is built)

- **One page in bc-docs** carries this vocabulary and is the only authority for status words. Because it binds every other document, an ADR establishes it.
- **A new word enters through the page first,** in the same change that first uses it.
- **A check that can go red:** the forbidden-vocabulary gate in bc-core is the pattern. The words in section 4 are refused as status words in documents and in screen text, with the approved word named in the failure.
- **DevHub's own output** (boot lines, tool results, task titles written by tools) uses only approved words and prints no remembered counts.
- **The existing glossary** (`docs/reference/glossary/README.md`) stays as the A to Z of nouns. It has no entry for any status word in this slice. It gets a notice pointing here for status words, and its entry for "Subscription" is corrected to match the chapter that owns the Subscription record.

## 8. Not settled in this slice

| # | Open point | Whose |
|---|---|---|
| 1 | **Where "done" is recorded.** One named list of metrics done for the pilot tenant, with the six reads and their dates, and an owner. Without it, "done" stays a claim | Metric Controller with the Demo Controller; the operator approves the shape |
| 2 | **Reads 3 and 4 of "done" need their records named exactly:** the proof record the evaluation act writes, and where the agreement with the expected value is written | Metric and Platform Controllers |
| 3 | **The acts in section 3 are named by what they do.** The exact governed endpoint for each belongs in the metric procedure, which the Metric Controller checks against practice | Metric Controller |
| 4 | **The live metric procedure still names retired tables** (`docs/onboarding/metric-workstream.md`, section 3, lists `contract.metric_contract` and related legacy tables as places to search) | Docs and Metric Controllers, in the clean-up |
| 5 | **Seeds and the directory.** Whether any live act still writes the seed statuses queued, in review, authored and published; whether a seed "queued to be entered in the directory" should become a recorded step (it is not one today); the remaining words of the Metric Directory | Architect with the Metric Controller |
| 6 | **The 25-step ladder** (ADR DEC-c9e623) describes much of section 3 in older words. Whether it stays as the detailed form of the life, or is retired with a notice, is a decision for the next slice | Architect with the Metric Controller |
| 7 | **A tenant's kind is not recorded.** Pilot, prospect or client, and proof are words with no field behind them, and the trigger of DEC-c220e4 depends on telling them apart. Where the kind is recorded is to be decided; a schema change would need the operator's yes | Architect, with the Platform and DB Controllers |
| 8 | **No read counts the metrics reporting for a tenant and a period.** The list's flag is the weaker "ever accepted" signal | Platform Controller, after the page is approved |
| 9 | **The versions marked active without a certificate** are cleared by the option the operator chooses in section 3a | Metric Controller, on the operator's choice |
| 10 | **The tenant admin's two switches are not built.** Enabling: a record of the admin's choice that starts the governed onboarding act and the provisioning worker, which only a platform operator can start today. Disabling: a governed act that switches production off for one tenant, which does not exist. Visible or hidden: the record the tenant owns and the admin's route. Any schema change needs the operator's yes | Architect for the design; Customer Portal, Platform and DB Controllers to build |
| 11 | **The words a tenant is shown when a metric is not reporting,** one per reason | Architect with the Customer Portal Controller, a later slice |
| 12 | **"Retired" for legitimate withdrawals only.** Today every act that archives a metric is written for a mistake or a rejection. Deciding that a certified metric found wrong is withdrawn and abandoned, never retired, and changing the retire act's purpose and record to match, is a design act | The operator decides; Architect designs; Platform and Metric Controllers build |
| 13 | **Registered before drafted is not fully enforced:** the direct-submission intake accepts a proposal with no directory entry | Platform Controller |
| 14 | **Certification blocked has no way out.** The exit is listed and refused in the database | Architect with the Metric Controller |
| 15 | **bc-db migration 0029** (the exit for a version the panel rejected) is on `main` and not applied; "abandoned" covers rejected versions only once it is | DB Controller, on the operator's grant |
| 16 | **"Released" is new.** The portfolio record and its governed act are not built. ADR DEC-c220e4 says tenants see every certified metric; once release exists it would say every released metric, which is a change to that ADR for the operator | The operator decides; Architect designs; Platform and DB Controllers build |

## 9. Sources read in this unit

- bc-docs: `docs/foundation/the-contract-grammar.md` (the seven states); `docs/operating-model/metric-lifecycle.md` (what each state asserts; the history of "active"; the two panels); `docs/reference/lifecycle-map.md` (the enforced transitions); `docs/onboarding/tenant-metric-binding.md`; `docs/implementation/metric-catalog-and-source-reference.md`; `docs/implementation/tenant-readiness-program.md`; ADR DEC-c9e623; ADR DEC-c220e4; `docs/reference/glossary/README.md`.
- bc-core: `src/registry/mcf/readiness-projection.service.ts` (the three-line split of active); `src/registry/mcf/mcf-read.service.ts` (the catalog tiers); `src/registry/mcf/mcf-mcv-retire.controller.ts`; `src/registry/mcf/mcf-cert-writer.service.ts` (abandon); `src/tenant-views/beyond-metrics.service.ts` (what "has a value" reads); `src/database/schema/mcf/` (certification actions; candidate statuses).
- Also for revision 6: ADR DEC-fa9424 (the directory entry as the only authoring door); ADR DEC-21ca17; bc-core `src/registry/mcf/mcf-seed-metric-status.ts` (the seed statuses), `src/registry/mcf/reservoir-ingestion.service.ts` (the retired from-seed intake), `src/registry/mcf/operator-direct-adapter.ts`; bc-db `migrations/0029_mcf_retire_rejected_exit.sql` at `origin/main`; `metric_directory.member` in the lifecycle map.
- Live, read-only: the view `mcf.mcv_live`; the state and status columns of `mcf`, `metric`, `tenant` and `schema_provisioner`; the action codes in `mcf.certification_record`; the check names in `mcf.mcv_chain_status`.
