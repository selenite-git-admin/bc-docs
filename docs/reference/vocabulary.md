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

**Second slice: the object chain, the acts and the states of the other contracts.** Approved by the operator on 2026-10-01, desk grant `2026-10-01T11-24-00-154Z-db431e4e` (text SHA-256 `db431e4e78fefa72fd771e3c74f8beb0a952bd1a78e70efd28d4d3ad48e9d80a`), as written on the Architect page in barecount-devhub pull request 201 at commit `42dcbaf6fa3da2e110002cebf2f7a5ff911f457e`. It is carried below as slice 2 with two changes only: its question is replaced by the operator's answer ("in force"), and its section headings are numbered S2.1 to S2.7. Its approval route and next-slices section are left out. It was read at bc-docs `origin/main` 3ce3b52, bc-core `origin/main` 43c8f67b2 and the live platform and demo tenant databases, read-only.

**Third slice: sources and tenants.** Approved by the operator on 2026-10-02, desk grant `2026-10-02T06-27-21-496Z-7584571d` (text SHA-256 `7584571d9b2e732ac98f181cbb8829415a221479ea3e14e7e907597a4a29f3da`), as written on the Architect page in barecount-devhub pull request 218 at commit `42de889af65d154043a3e4b6a5a13194ecbb4704` (revision 3). His earlier grant of revision 2, `2026-10-02T06-20-25-640Z-e7d71682`, is replaced by this one: revision 3 adds only the closing of slice 1's open point 7. It is carried below as slice 3, with these changes only:
- its section headings are numbered S3.0 to S3.9;
- its S3.7 corrections are applied to slices 1 and 2 above, and the section itself is kept as the record of what changed;
- its question on ADR DEC-c220e4 is replaced by the operator's answer (S3.9);
- its approval route is left out.

It was read at bc-docs `origin/main` 5e64c2f, bc-core `origin/main` 44828a95c and the live platform database, read-only.

**Fourth slice: business concepts and the contract grammar.** Approved by the operator on 2026-10-02, desk grant `2026-10-02T07-04-13-353Z-08123cd1` (text SHA-256 `08123cd1b71e84895f9057146960eff5d3b5dace04c05e6bc1707db433a0a8d5`), as written on the Architect page in barecount-devhub pull request 223 at commit `01b766a9a81ec6c357a2026cb072ff2de6d761eb` (revision 1), with the three proposals of its section 3. It is carried below as slice 4, with these changes only:
- its section headings are numbered S4.1 to S4.6;
- its questions are replaced by the operator's answers, and the words "if the operator agrees" are removed from its not-approved list;
- its approval route is left out.

It was read at bc-docs `origin/main` 9dca4a5, bc-core `origin/main` 05cbe79c and the live platform database, read-only.

**Fifth slice: AI panels and their verdicts.** Approved by the operator on 2026-10-02, desk grant `2026-10-02T07-28-50-143Z-e395cf73` (text SHA-256 `e395cf73148f229475cb139252341aeece6f09c164c529009eae0aa61c31ac13`), as written on the Architect page in barecount-devhub pull request 224 at commit `9b20363311fe1ad92f3587aadbfe0c146d804e0a` (revision 1), with the four proposals of its section 3. It is carried below as slice 5, with these changes only:
- its section headings are numbered S5.1 to S5.6;
- its questions are replaced by the operator's answers, and the words "if the operator agrees" are removed from its not-approved list;
- its approval route is left out.

It was read at bc-docs `origin/main` 9dca4a5, bc-core `origin/main` 05cbe79c and the live platform database, read-only.

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
4. **A state word is always said with its subject** (slice 3, S3.0). No state word is reserved to one kind of thing: "metric available", "connector available", "tenant archived". A word for one tenant names the tenant: "Enabled for Kaveri", never "enabled".
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

**Which word "available" equals** (the operator's answer, grant `2026-10-01T06-36-21-158Z-648f1a32`): **metric available means released.** A tenant is offered what the platform has released, not everything it has certified. Until the release record is built, the two are the same set.

The operator's ladder, with his answer of the same day: "enabled/disabled is producing state. We need one more - Visible/hidden". So there are **two separate switches**: one says whether the metric is produced for the tenant, the other says whether the tenant's users see it. Each step needs the ones before it.

| Word | Plain meaning | True when | Made true by | What the tenant sees |
|---|---|---|---|---|
| **metric available** | In the platform's portfolio: any tenant could have it. It is the tenant-side word for a released metric | the same record as **released** (group 4); until that record exists, the same as **certified** | The platform's release | The metric exists in the catalog |
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

**What it does today.** These versions are in every tenant's list, and the evaluation act will evaluate one if asked. None of the metrics enabled for Kaveri is among them (the Architect's read-only query of 2026-10-01, comparing Kaveri's provisioning commands with the line named below).

**Where to read it.** The group: the `residue_legacy_active` line of `GET /api/registry/mcf/readiness-projection`, and by name in DEC-21ca17 item 3 and its manifest (excluded cohort `pre_c8_member_identity_unresolvable`). A second line, `unattributed_active` (marked active with no record at all), must stay empty; it was empty on 2026-10-01.

**The options for clearing it.**

| Option | What is done | What a tenant sees | Cost and limits |
|---|---|---|---|
| **1. Finish the decided route (recommended)** | Mint the missing directory identity for each, then a second manifest moves each to awaiting certification through the governed reintake act. Each is certified only through the certification panel (DEC-21ca17 items 3 and 5) | They leave the list until certified. Nothing changes for Kaveri's set-up metrics | Directory work per metric, then one operator-authorized batch. It is already decided; it needs to be scheduled with the Metric Controller |
| **2. Retire each** | The governed retire act archives the whole metric | They leave the list and do not return unless restored or written again | Quick, and it needs no directory identity. But the retire act is for a metric authored in error, and these are candidates for certification, not errors. Using it here would need the operator's decision to widen what that act is for |
| **3. Leave them until the deadline** | Nothing now; clear them before the moment DEC-c220e4 sets | They stay listed with no value, and can be evaluated without a certificate | No work now. It keeps the state the operator has just called a problem |

**Why option 1.** It is the route the operator already decided, it uses only governed acts, and it leaves each metric able to earn its place through certification. A filter that hides these versions in the list or in evaluation is not offered: the defect is in the state they carry, and the repair is to change that state through the governed act, not to read around it.

## 4. Words that are not approved, and what to say instead

| Not approved | Why | Say instead |
|---|---|---|
| activated | No record holds an activation for a metric | "was certified" (platform); "subscribed" or "enabled", whichever is meant |
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
| archived (of a metric) | It is a field that both retired and abandoned set; "tenant archived" is approved (slice 3) | "retired" or "abandoned" |
| blocked (alone) | Two records use it: certification, and the directory | "certification blocked"; "registered, blocked in the directory" |
| queued, published (of a metric) | They are statuses of a seed on a retired route | the metric's own word from section 3 |
| second tenant, first customer, customer tenant | Ordinals and "customer" miscount the demo tenant | "Kaveri" or "demo tenant"; for another tenant, name it |

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

| Word | Meaning | True when |
|---|---|---|
| **demo tenant** | `kaveri`: the tenant on which the platform is proven and shown. It is not counted as a customer | the operator's word (slice 3); no field records it |
| **tenant active** | A tenant whose registration is active | `tenant.tenants.status_code` is `active` |

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
| 1 | **Where "done" is recorded.** One named list of metrics done for the demo tenant, with the six reads and their dates, and an owner. Without it, "done" stays a claim | Metric Controller with the Demo Controller; the operator approves the shape |
| 2 | **Reads 3 and 4 of "done" need their records named exactly:** the proof record the evaluation act writes, and where the agreement with the expected value is written | Metric and Platform Controllers |
| 3 | **The acts in section 3 are named by what they do.** The exact governed endpoint for each belongs in the metric procedure, which the Metric Controller checks against practice | Metric Controller |
| 4 | **The live metric procedure still names retired tables** (`docs/onboarding/metric-workstream.md`, section 3, lists `contract.metric_contract` and related legacy tables as places to search) | Docs and Metric Controllers, in the clean-up |
| 5 | **Seeds and the directory.** Whether any live act still writes the seed statuses queued, in review, authored and published; whether a seed "queued to be entered in the directory" should become a recorded step (it is not one today); the remaining words of the Metric Directory | Architect with the Metric Controller |
| 6 | **The 25-step ladder** (ADR DEC-c9e623) describes much of section 3 in older words. Whether it stays as the detailed form of the life, or is retired with a notice, is a decision for the next slice | Architect with the Metric Controller |
| 7 | **Closed (slice 3, 2026-10-02).** No field records a tenant's kind, and none is to be added. Kaveri is the demo tenant. Activating a tenant for a party outside BareCount, the moment DEC-c220e4 gates, is the operator's own decision, case by case; nothing infers it | (closed) |
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

## Slice 2: the object chain, the acts and the states of the other contracts

### S2.1 The chain, in Foundation's words

Foundation fixes one order: external **source state** is observed, then admitted as **source objects**; those are evaluated into **canonical objects**; those into **metric snapshots**; those into **action objects**. Every evaluation act also records **evidence** (that the act happened, and its outcome) and **lineage** (what it referenced). Nothing is skipped, nothing points backwards, nothing is changed after it is recorded (`the-object-model.md`, "Object inventory"; the six invariants).

The verbs for this chain are the approved ones: observe, admit, evaluate, resolve, preserve, record, reference, bind, finalize, surface. Words such as ingest, transform, process, refresh and recompute are not used for it.

### S2.2 The objects: what each word means, and the record that holds it

| Word | Plain meaning | Where it is recorded (in the tenant's own database) |
|---|---|---|
| **source state** | What the source system holds. Not a record of ours | none |
| **source object** | One observation of source state that was admitted, kept exactly as received, never changed | an `admitted` row in `progression.admission`, with its row in the matching `fact.so_` table |
| **rejected observation** | An observation that failed admission. It is not a source object; the rejection is kept as evidence | a `rejected` row in `progression.admission` |
| **canonical object** | Business meaning resolved from one or more source objects, under one canonical contract version | an `accepted` row in `progression.canonical_evaluation`, with its row in the matching `fact.co_` table, which names it by foreign key |
| **metric snapshot** | A metric's value for a period, evaluated from canonical objects | an `accepted` row in `progression.metric_evaluation`, with its row in the matching `fact.ms_` table. When a metric has one, the tenant word is "reporting" (slice 1) |
| **action object** | A declared intent bound to metric snapshots, with its outcome | **not built.** `progression.intervention_evaluation` exists with the values `triggered` and `not_triggered`, and holds no rows. Foundation's action object has a lifecycle those two values do not express (S2.6, defect 4) |
| **evidence** | The record that an evaluation act happened, with its outcome | `evidence.evidence_object` |
| **lineage** | The record of what an act referenced | `evidence.lineage_object`, and for one case a progression table (S2.6, defect 3) |

"Object" alone is not a status. A count of objects is read from the record named, for one tenant.

### S2.3 Acts, runs and their outcomes

| Word | Plain meaning | Record |
|---|---|---|
| **evaluation act** | One governed act at one boundary: admitting, resolving canonical meaning, evaluating a metric, evaluating an intervention | Foundation's term; its result is one of the records in S2.2 |
| **run** | One invocation that performs many acts and is recorded as a whole | `progression.admission_run`, `metric_run`, `intervention_run` (and `canonical_run`, which nothing writes: S2.6, defect 5) |
| **admitted / rejected** | The outcome of admitting one observation | `progression.admission.status` |
| **accepted / rejected** | The outcome of one canonical or metric evaluation act | `progression.canonical_evaluation.status`, `progression.metric_evaluation.status` |
| **run states:** pending, running, completed, failed, cancelled | Where a run is, or how it ended | the `status_code` of each run table |
| **deferred** (of a metric run) | The run did not evaluate because its inputs were not available. Nothing was recorded as a value | `progression.metric_run.status_code` = `deferred_inputs_unavailable` |

**Not approved for the chain:** "processed" or "ingested" (say admitted or evaluated); "landed" (say recorded); "materialized" for a fact row (say recorded); "succeeded" for an act (say accepted); "deferred" without saying what was deferred.

### S2.4 The states of the contracts other than metrics

Five contract families keep the legacy lifecycle Foundation names for them (`the-contract-grammar.md`, "Legacy contract-family envelope (frozen)"): **source, admission, observation, canonical, intervention**. The field is `governance_state_code` on the source, admission, observation and canonical version tables. Intervention versions carry `status_code` instead, with no rule on its values and no rows today (S2.6, defect 6).

| Field value (Foundation) | Plain meaning |
|---|---|
| `draft` | Being written |
| `review` | Under review |
| `approved` | Review complete, not yet in force |
| `active` | **In force:** the version runtime uses now |
| `superseded` | Replaced by a newer version; what was produced under it stays as it was |

**The operator's answer** (grant `2026-10-01T11-24-00-154Z-db431e4e`): for the source, admission, observation, canonical and intervention contracts, the field value `active` is said as **in force**, in speech and on screens, so that "active" is never said of anything.

### S2.5 Words not approved here, and what to say instead

| Not approved | Say instead |
|---|---|
| live (of a contract or a version) | "in force" |
| deprecated (of a contract version) | "superseded"; `deprecated` is a value of two parent-level fields only (S2.6, defect 2) |
| pending provisioning (as a contract state) | not a Foundation state (S2.6, defect 1) |
| SO, CO, MS, AO in text for the operator | the full words: source object, canonical object, metric snapshot, action object |
| canonical run | "the canonical evaluations of one resolution", with its evidence (ruling TSK-29e34a) |

### S2.6 Defects found while reading, named, not fixed here

1. **A sixth state value not named by Foundation.** The live database allows `pending_provisioning` on the version tables of source, admission, canonical, the mapping and the provisional AI contract (CHECK constraints in `contract`), beside Foundation's five. No version holds it today. Either Foundation names it (an erratum) or a migration removes it. Architect with the DB Controller; the operator decides.
2. **A second state field that says something else.** `contract.observation_contract.status_code` (`draft`, `active`, `deprecated`) sits on the parent. On 2026-10-01 every observation contract parent says `draft` while its versions are `active` or `superseded`. The same parent-level field exists on `canonical_mapping` and `contract_meta_schema`. Retire the parent field, or define it and keep it true. DB with Platform.
3. **Canonical evaluation writes no lineage object.** Foundation says every boundary emits evidence and lineage (`the-object-model.md`, "Object-boundary mapping"). On the demo tenant, `evidence.lineage_object` holds `observed_as` rows for admissions and `evaluated_by` rows for metric evaluations, and nothing for canonical evaluations. The canonical resolver records its references in foreign keys and in `progression.source_legal_entity_binding_lineage`, not as lineage objects. FND-005 is decided (DEC-48d222, no proof, no record); the canonical boundary is brought to it under TSK-1e8eaa.
4. **The action object is not built.** The table that would record it carries `triggered` and `not_triggered`, which do not express Foundation's lifecycle (a terminal state, or non-closure recorded explicitly). Its words are settled when its design is (the readiness program's action lane).
5. **`progression.canonical_run` is vestigial.** Nothing writes or reads it (ruling TSK-29e34a). Retire it with a later migration.
6. **The intervention contract's state field is named and checked differently.** `contract.intervention_contract_version.status_code` has no rule on its values, while the `governance_state_code` of source, admission and canonical (and of the mapping and AI contract versions) is checked; the observation version table has no rule on its values either (only source, admission, canonical, the mapping and the AI contract are checked). Bring the five families under one checked field. DB Controller.

### S2.7 Where counts are read

| To know how many | Read |
|---|---|
| source objects, canonical objects, metric snapshots for a tenant | the tenant's `progression.admission`, `progression.canonical_evaluation`, `progression.metric_evaluation`, by status |
| contract versions in each state | each family's version table, `governance_state_code` |
| evidence and lineage for a tenant | `evidence.evidence_object` by type; `evidence.lineage_object` by relationship |

## Slice 3: sources and tenants

### S3.0 The rule this slice adds: a state word is said with its subject

State words such as available, active, approved, archived and activated are **not reserved** to one kind of thing. Each is always said **with its subject**, for example "metric available", "connector available", "source table approved" or "tenant archived". The meaning comes from the subject and the word together, and each pair has one record.

A bare state word with no subject is not approved. A word for one tenant also names the tenant: "enabled for Kaveri". This replaces slice 1's rule 4 (S3.7).

### S3.1 What can be read: the source catalog

The catalog describes the structure of the systems we can read. It holds no business data. It has six levels, each pointing to the one above (`sources-and-the-catalog.md`):

| Word | Plain meaning | Record |
|---|---|---|
| **source provider** | The vendor or organization that makes a source system | `source.source_provider` |
| **source system** | A product we can read, for example an ERP | `source.source_system` |
| **source version** | One version of that product | `source.source_version` |
| **source module** | A functional area inside it | `source.source_module` |
| **source table** | One table, model or object of a source system | `source.source_object`. The field name does not match the word; this is recorded as a known mismatch (defect 1) |
| **source field** | One field of a source table | `source.source_field` |

**"Source object" keeps only Foundation's meaning:** one admitted observation (slice 2). It is never said of a catalog entry.

**Catalog states** (field `catalog_status` on all six levels), said with the entry, for example "source table approved":

| Field value | Plain meaning |
|---|---|
| `registered` | Known, not yet approved for building contracts on |
| `approved` | Approved for building contracts on |
| `deprecated` | Kept, no longer preferred for new contracts |
| `archived` | Kept for history, out of every default view |

Two further fields record checks on a catalog entry. They are evidence about the entry, not its state, and are said only with the entry named:
- `verification_status`: whether its existence and shape were confirmed against the source (unverified, verified, disputed, manually verified, rejected);
- `validation_status`: not validated, validated.

### S3.2 How a tenant reaches a source

| Word | Plain meaning | Record and its state words |
|---|---|---|
| **connector** | Our technical ability to reach a kind of source system over a declared protocol. Platform-wide, not a tenant's | `runtime.connector.status_code`: `draft`, `available`, `deprecated`, `retired`, said "connector available" and so on |
| **connection** | One tenant's access to one source system through a connector. Its credentials live outside our records | `runtime.connection.connection_status`: the code writes `connected`, `disconnected`, `paused`, `disabled`; the database default is `draft`, and the field has no rule (defect 4) |
| **reader** | The admission definition for one business entity, reused by every tenant | `runtime.reader.status_code`: `draft`, `active`, `deprecated` |
| **reader flavor** | A reader specialised for one source system and scenario | `runtime.reader_flavor.status_code`: `draft`, `active`, `deprecated` |
| **reader binding** | Which admission contract a reader uses for a source entity | `runtime.reader_binding` (bound, then unbound) |

For readers and flavors, as for the contracts in slice 2, the field value `active` is said **"in force"**.

### S3.3 Tenants

| Word | Plain meaning | Record and its state words |
|---|---|---|
| **tenant** | One organization's identity on the platform, with its own database | `tenant.tenants.status_code`, said with the tenant: "tenant provisioning" (being created), "tenant active", "tenant suspended", "tenant archived", "tenant failed" (creation failed) |
| **demo tenant** | `kaveri`: the tenant on which the platform is proven and shown. It is not counted as a customer | the operator's word; no field records it |
| **tenant infrastructure** | The database and compute a tenant runs on | `tenant.tenant_infrastructure.status_code`: `provisioning`, `active`, `decommissioning`, `decommissioned`, said "infrastructure active" and so on (defect 3) |
| **subscription** | The tenant's plan and its lifecycle, as the chapter declares it: active, suspended, terminated | **not built** (slice 1; DEC-c220e4). When built, its end is said "subscription terminated" |

A tenant's end is "tenant archived"; a subscription's end is "subscription terminated". Each word is said with its own subject.

**A tenant's kind is not recorded, and no field is to be added for it.** Kaveri is the demo tenant, by the operator's word. Activating a tenant for a party outside BareCount, the moment DEC-c220e4 gates, is the operator's own decision, made case by case. Nothing infers it from a tenant's data or name.

### S3.4 The operator's decisions on revision 1 (2026-10-02)

1. A catalog entry is a **source table**: a table, model or object of a source system. "Source object" keeps only Foundation's meaning. The field name `source.source_object` is a known mismatch. Renaming it is a separate database decision.
2. **Generic words are not reserved.** A state word is always said with its subject (S3.0). "Open for connections" is dropped: it is "connector available". Slice 1 is corrected where it reserved "available" for metrics.
3. **Demo tenant** is the word for Kaveri, and "pilot" in any form is retired. The onboarding-record row is dropped from this page, and so are the classifications pilot tenant, tenant for a prospect or client, and proof tenant. Slice 1 is corrected where it introduced them.
4. "Tenant archived" and "subscription terminated", each said with its subject.
5. Not approved: "source object" for a catalog entry, and any bare state word without its subject. "In force" stays for readers and flavors.
6. The six defects go to their owners as tasks. Those that touch the database need the operator's yes. Defect 3 goes to Platform's plan PLN-940b0c (Tenant readiness).
7. The slice 2 wording corrections (S3.7).

### S3.5 Words not approved, and what to say instead

| Not approved | Say instead |
|---|---|
| source object (meaning a catalog entry) | "source table". "Source object" means one admitted observation (slice 2) |
| a bare state word without its subject ("available", "active", "archived", "activated") | the word with its subject: "metric available", "connector available", "tenant archived" |
| pilot, pilot tenant, the pilot (any form) | "demo tenant", or "Kaveri" |
| live, up (of a connection) | "connected", or the connection's other state |
| active (of a reader or reader flavor) | "in force" |
| onboarded, provisioned (of a tenant) | "tenant active", or "infrastructure active" |

### S3.6 Defects found while reading, named, not fixed here

Each goes to its owner as a task once this slice is approved. A defect that touches the database needs the operator's yes before any change.

1. **The catalog's table of source tables is named `source.source_object`.** The chapter calls the entity "Source Table", and Foundation uses "source object" for an admitted observation, so the name invites exactly the confusion this page exists to end. It is recorded as a known mismatch. Renaming is a separate database decision (DB Controller; the operator's yes). Until then, always say "source table".
2. **Two records are named "admission run", with different states.**
   - The platform's `runtime.admission_run.run_status` allows `running`, `completed`, `failed`, `cancelled`, `reconciled`.
   - Each tenant's `progression.admission_run.status_code` allows `pending`, `running`, `completed`, `failed`, `cancelled`.

   Say which one is meant, every time. Whether both should exist is to be settled by Platform with DB.
3. **The tenant infrastructure record is not kept true.** On 2026-10-02 the demo tenant is "tenant active" while its infrastructure record says `provisioning`. An archived tenant made for a test also shows `provisioning`. Either the act that changes the infrastructure maintains the record, or the record is retired. Platform, under plan PLN-940b0c, with Infra & CI.
4. **The connection's state has no rule.** `runtime.connection.connection_status` has no CHECK. The code writes `connected`, `disconnected`, `paused` and `disabled`, and the database default is `draft`, which is not in the code's list. DB with Platform; the operator's yes for the change.
5. **Readers say `draft` while their flavors are in force.** Every reader parent reads `draft` while the flavors under it are `active`. It is the same parent-and-child mismatch as the observation contracts in slice 2. DB with Platform; the operator's yes for any change to the record.
6. **Tenant states and subscription states differ.** The registry's five tenant states and the chapter's three subscription states overlap in name (`active`, `suspended`), but they are different records. Keep them apart, each said with its subject, until the subscription is built. Owner: Architect, with the subscription design.

### S3.7 Corrections to slices 1 and 2, made in `vocabulary.md` with this slice

**Slice 1:**
1. **Rule 4** is replaced by section 0 of this page: a state word is always said with its subject, and a word for one tenant names the tenant.
2. **Group 6, "Which word 'available' equals":** it reads "**metric available** means released". The row for **available** reads "metric available". Nothing reserves "available" to metrics: "connector available" is its own pair with its own record.
3. **Not-approved list, "activated":** the reason reads "no record holds an activation for a metric". The tenant clause is removed. The say-instead is unchanged.
4. **Not-approved list, "archived (as a status)":** it reads "archived (of a metric)". "Tenant archived" is approved by this slice.
5. **Not-approved list, "second tenant, first customer, customer tenant":** the reason reads "ordinals and 'customer' miscount the demo tenant". The say-instead reads "'Kaveri' or 'demo tenant'; for another tenant, name it".
6. **Section 6, "The tenant kinds":** the opening paragraph and the rows pilot tenant, tenant for a prospect or client, and proof tenant are removed. A **demo tenant** row is added, as in S3.3. The **active tenant** row reads "tenant active".
7. **Every other "pilot":** it becomes "demo tenant" or "Kaveri", with no change of meaning. This covers the deadlock section, its option table, and open points 1 and 7.
8. **Open point 7 is closed.** Its row reads "**Closed (slice 3, 2026-10-02).** No field records a tenant's kind, and none is to be added. Kaveri is the demo tenant. Activating a tenant for a party outside BareCount, the moment DEC-c220e4 gates, is the operator's own decision, case by case; nothing infers it."
9. **Option 3 of the deadlock table:** "before the first tenant for a prospect or client" reads "before the moment DEC-c220e4 sets".

**Slice 2:**
1. **S2.6 defect 1:** "A seventh state not named by Foundation" reads "**A sixth state value** not named by Foundation". The database allows `pending_provisioning` beside Foundation's five, six values in all.
2. **S2.6 defect 6:** "the other four families' `governance_state_code` is checked" reads "the `governance_state_code` of source, admission and canonical (and of the mapping and AI contract versions) is checked". The observation version table has no rule, and neither does intervention.
3. **S2.6 defect 3:** the last sentence reads "FND-005 is decided (DEC-48d222, no proof, no record); the canonical boundary is brought to it under TSK-1e8eaa". This is a fact update from 2026-10-02.

### S3.8 Where counts are read

| To know how many | Read |
|---|---|
| catalog entries in each state | each `source.*` table, `catalog_status` |
| connectors, readers, flavors in each state | `runtime.connector`, `runtime.reader`, `runtime.reader_flavor`, `status_code` |
| connections by state, for a tenant | `runtime.connection.connection_status` |
| tenants by state | `tenant.tenants.status_code` |

### S3.9 The operator's answer on ADR DEC-c220e4

"Amend the wording of ADR DEC-c220e4 as proposed there, with the rule unchanged" (the operator's grant below). ADR DEC-c220e4 now says: "Kaveri is the demo tenant and is not counted as a customer. The metric entitlement record, with its evaluation and catalog checks, must be live before any tenant is activated for a party outside BareCount, on any source system, or before a plan narrower than the whole catalog is sold."

## Slice 4: business concepts and the contract grammar

### S4.1 The business vocabulary: what a concept is

The business vocabulary is **one governed registry** (DEC-02f5a9; `the-contract-grammar.md`, "Vocabulary: the Business Concept Registry"). It replaced the earlier three primitives: business object, business field and canonical field, joined by a canonical mapping.

| Word | Plain meaning | Record |
|---|---|---|
| **business concept registry** | The one governed list of everything the business talks about, which contracts refer to by identity | the `concept_registry` schema |
| **entity** | A governed business thing that plays a role, such as Customer, Supplier or Invoice. Customer and Supplier are different entities even when one party plays both. It was called "business object" before | `concept_registry.entity`, named and defined on `entity_version` |
| **business concept** | The unit contracts refer to: one property of one entity, identified as **entity.property** (for example `invoice.bill_to`) | `concept_registry.business_concept` |
| **value concept** | A business concept that holds a value, such as a credit limit or a balance | `business_concept.kind` = `value` |
| **reference concept** | A business concept that points to another entity and names the role it plays (`invoice.bill_to` points to Customer) | `business_concept.kind` = `reference`, with `reference_role` and `target_entity_id` |
| **identity-bearing / descriptive** | Whether the concept is part of what identifies its entity. Changing an entity's identity-bearing set makes a new entity; adding a descriptive concept does not | `business_concept.identity_role` |
| **characteristic** | The meaning part of a concept's name, such as "credit limit", "balance" or "status" | `concept_registry.characteristic` |
| **representation term** | The form part of the name, from a small closed list: amount, date, code, quantity, count, indicator, identifier, text | `concept_registry.representation_term` |
| **concept version** | One fixed wording of a concept. Versions never change; a change of meaning is a new version or a new concept | `concept_registry.business_concept_version`. It has no state field of its own: its state is read from its concept |
| **semantic role** | What a concept does in analysis. Eight values: amount, identity, status, temporal, reference, dimension, diagnostic, strategic filter | `business_concept_version.semantic_role` (S4.6 defect 2) |
| **value set** | The governed list of allowed values for a concept, required for the roles status and strategic filter | `business_concept_version.canonical_value_set` |

**Registry states** (`lifecycle_state`, said with the subject, for example "concept active" or "entity superseded"):

| Field value | Plain meaning |
|---|---|
| `draft` | Being written |
| `review` | Under review |
| `approved` | Reviewed, not yet in force |
| `active` | In force: contracts may refer to it |
| `superseded` | Replaced for new work. What already refers to it keeps referring to it |
| `archived` | Withdrawn because it was admitted in error (DEC-1fbaf1). Concepts and characteristics have it; entities do not (S4.6 defect 3) |

**"Property"** is the docs' name for the second half of entity.property. The registry has no record of its own for it: the business concept row is the property (S4.6 defect 4). Say "concept" for the record, and "property" only when explaining the entity.property name.

### S4.2 The contract grammar: the words that tie things together

| Word | Plain meaning | Record |
|---|---|---|
| **canonical grain** | The set of values that identifies one canonical object: two canonical objects with the same grain values in the same period are the same observation (`canonical-contract-creation.md`, "Grain: The Key Decision") | `grain[]` inside the canonical contract version's body |
| **metric grain** | The entity one instance of which a metric's value describes, for example Legal Entity or Customer | `mcf.metric_contract_version.grain_entity_version_id` (and `metric_contract.grain_entity_id`) |
| **composition metric** | A metric computed only from other metrics' values: at least one metric input, and otherwise only calendar context or constants. It reads no source data of its own (DEC-fa7c63 amendment 4) | no field: a test over its variable bindings (bc-core `src/registry/mcf/pure-composition.ts`) |
| **metric variable** | One named input or output of a metric's formula, tied to what it reads | `mcf.metric_variable_binding` |
| **concept input / metric input** | A metric variable that reads a business concept, or one that reads another metric's value | `role_kind_code` = `input` or `metric_input` |
| **contract binding** | A tenant's adoption of one contract version, with the variation the tenant is allowed (`tenancy-and-binding.md`, "Contract Binding") | `tenant.contract_binding` (and see S4.6 defect 6) |
| **reader binding** | Which admission contract a reader uses for a source entity (slice 3) | `runtime.reader_binding`; for observation contracts, `runtime.reader_observation_binding` |
| **legal-entity binding** | Which legal entity a source's company code belongs to, for one tenant | in each tenant's database (`tenant_dim.source_legal_entity_binding_revision`) |
| **account classification binding** | How a tenant's general ledger account range is classified (class, type, cash-flow category) | `tenant.gl_account_classification_binding` |
| **observation field mapping** | How an observation contract reads each source field into a business concept: type, unit and form | inside the observation contract version's body |

**"Binding" is never said alone.** Each binding above is a different record with a different meaning, so it is always said with what it ties: "contract binding", "reader binding", "legal-entity binding".

**Canonical mapping is retired.** The canonical mapping, which tied a business field to a canonical field, was eliminated by DEC-02f5a9, because one business concept now serves both sides. Its tables still exist, empty (TSK-68722f). Field-reading content lives in the observation and canonical contract bodies.

### S4.3 The operator's answers (2026-10-02)

1. **The registry's name.** The record is the **business concept registry**. **BCF** means **Business Concept Framework**: the registry together with its authoring and certification. "Business Context Framework" is retired.
2. **"Certified" for a concept: no.** A concept says its own state, "concept active". "Certified" stays a metric word only.
3. **"Reporting grain" is retired.** "Metric grain" is said for every metric. A composition metric's metric grain is declared, never inherited.

### S4.4 Words not approved, and what to say instead

| Not approved | Say instead |
|---|---|
| business object | "entity" |
| business field, canonical field | "business concept" |
| canonical mapping (as a live thing) | retired: "observation field mapping", or the canonical contract's resolution rules, whichever is meant |
| binding (alone), metric binding, CO bindings | the binding with what it ties: "metric variable", "contract binding", "reader binding", "legal-entity binding" |
| grain (alone) | "canonical grain" or "metric grain" |
| reporting grain | "metric grain" |
| field role | "semantic role" (of a concept version) or "metric variable" (of a metric). No record holds a "field role" |
| semantic input | "concept input" |
| Business Context Framework | "business concept registry", or "BCF" |
| certified (of a concept) | "concept active" |

### S4.5 Where counts are read

| To know how many | Read |
|---|---|
| entities, concepts, characteristics in each state | `concept_registry.entity`, `business_concept`, `characteristic`, `lifecycle_state` |
| concept versions by semantic role | `concept_registry.business_concept_version.semantic_role` |
| a metric's variables by kind | `mcf.metric_variable_binding.role_kind_code` |
| a tenant's contract bindings | `tenant.contract_binding` |

### S4.6 Defects found while reading, named, not fixed here

1. **The business vocabulary chapter has a lifecycle that matches no record.** `business-vocabulary.md` ("Certification Lifecycle") gives proposed, reviewing, certified, superseded, withdrawn. The grammar and the registry's CHECK rules give draft, review, approved, active, superseded, archived. The chapter is to be corrected to the record. Owner: Docs.
2. **Two different lists are both called "semantic role".**
   - `canonical-contract-creation.md` ("BF semantic role", the default resolution rule per role) lists identifier, dimension, measure, temporal, descriptor.
   - The registry's CHECK lists eight values: amount, identity, status, temporal, reference, dimension, diagnostic, strategic filter.

   Only two values are shared. The chapter's table is to be restated against the registry's list. Owner: Docs, with the Architect.
3. **Entities have no `archived` state, while concepts and characteristics do.** The grammar gives "registry concepts" six states. Whether an entity can be withdrawn for an admission error, and so needs `archived`, is to be decided. Owner: Architect, with DB; a schema change needs the operator's yes.
4. **"Property" is a construct in the docs with no record.** The grammar says concept identity is unique as `UNIQUE(entity_id, property_id)`. The registry has no property table: the business concept row carries the property's kind and identity role. Either the grammar text is corrected to the record, or a design act adds the record. Owner: Architect.
5. **Docs name records that do not exist.**
   - The grammar's metric contract section names `metric_binding`, and `data-model-and-schema.md` lists it among the `mcf` tables; the record is `mcf.metric_variable_binding`.
   - `metric-workstream.md` uses `co_bindings`.

   Owner: Docs.
6. **Two records for a tenant adopting a source contract.** `tenant.tenant_binding` (source contract, version, tenant, environment) and `tenant.contract_binding` (any family, including source) both say that a tenant adopted a contract version. Today only canonical rows are in `contract_binding`. Which one is the record is to be settled. Owner: Platform, with DB; a schema change needs the operator's yes.
7. **A metric variable's role has no rule, and one kind is ambiguous.** `mcf.metric_variable_binding.variable_role_code` is free text. `role_kind_code` = `input` means a concept input, beside `metric_input`, which means a metric input. Owner: Metric, with DB.
8. **Handed to slice 5:**
   - three tables named `certification_record` (`bcf`, `contract`, `mcf`) and two named `panel_output_record` (`bcf`, `contract`);
   - the act called `createCharacteristic` in the docs and `registerCharacteristic` in the code;
   - "park" in the docs (`awaiting_operator_confirm`), which is a different outcome from `parked` in the code;
   - verdict codes with no value rule.

## Slice 5: AI panels and their verdicts

### S5.1 The panels

An **AI panel** is a fixed set of AI models, each in a named seat, that answers one question about one case. The panels run inside bc-core (DEC-ffee4e). A panel advises or decides only as far as its governing decision says; the operator's acts and the gates stay in force.

| Panel | The question it answers | Seats | Record of a run |
|---|---|---|---|
| **registry authoring panel** | May this act on the business concept registry be drafted: a new concept, characteristic, version or supersession? | maker, checker, moderator | `bcf.panel_output_record` |
| **metric authoring panel** | Is this metric contract draft admissible as written? | maker, checker, judge (DEC-09f86b) | `mcf.metric_authoring_panel_run`, with one transcript per seat; its verdict is also written to `bcf.panel_output_record` |
| **certification panel** | Does the frozen metric package pass certification, which gates the metric's activation (DEC-c48b0f)? | assessor, adversary, moderator | `mcf.audit_contextual_panel_run`; its decision is in `metric_audit.decision` |
| **ABC reasoning panel** | Bounded reasoning inside the Autonomous Business Chain orchestrator (DEC-cff0cf) | maker, checker, judge | no record of its runs found (S5.6 defect 7) |

"AI panel" in `the-dual-layer-interaction-model.md` names the advisory conversation surface of the user interface. That is a screen, not a panel in this sense. Say "conversation panel" for it.

### S5.2 The words of a panel run

| Word | Plain meaning | Record |
|---|---|---|
| **panel run** | One call of one panel on one case | the run's `panel_run_uid` in the record named in S5.1 |
| **roster** | Which model sits in each seat of one panel. It is **calibration-locked**: it changes only with the operator's recorded sign-off | registry panel: ADR DEC-ffee4e, amended by DEC-53629b; certification panel: one row in `mcf.audit_panel_roster_registration`, authorized by the operator with its calibration evidence (DEC-d3b916); metric authoring panel: the model defaults in code (DEC-e87701) |
| **seat** | One position on a panel, with its job: the maker drafts, the checker challenges, the moderator or judge decides; the assessor, adversary and moderator certify | the seat columns of the roster, or `model_role_code` on a transcript |
| **panel verdict** | The panel's answer for one run (S5.2a) | `verdict_code` on the run's record |
| **defect code** | Why a draft was rejected, from a fixed list | `defect_code` (registry panel: nine values; metric panel: `MC_DEFECT_*`) |
| **sent to operator review** | The panel did not decide and hands the case to the operator, with a reason | verdict `OPERATOR_REVIEW`, with `operator_review_reason` where recorded |
| **operator disposition** | The operator's recorded handling of a run sent to operator review: resolved in the registry, rejected by design, obsolete, replaced by a re-run, pending action, or unclassifiable | `bcf.panel_output_record.disposition_code`, written once |
| **waiting for operator confirm** | A high-consequence registry act the panel approved, which is written only when the operator confirms it with a rationale of at least 40 characters | the API outcome `awaiting_operator_confirm`; the confirmation is kept in the registry certification record |
| **re-run** | A new panel run on the same case, replacing an earlier one. The metric authoring panel allows two | `superseded_by_rerun` disposition; the metric panel's re-run count |
| **vendor failure** | A model's vendor did not answer. The registry panel then writes nothing; the metric panel sends the case to operator review with the reason | the metric panel's `operator_review_reason` (for example `vendor_timeout`) |
| **calibration** | The measured evidence that a roster's models are fit for their seats; for the registry panel, also the operator's sampled check of panel outputs | `calibration_evidence_ref` on a roster row; `bcf.calibration_event` |
| **operator-direct entry** | A registry act written by the operator through a governed route, with no panel run. It is not a panel verdict, even where it is stored beside them (S5.6 defect 2) | rows in `bcf.panel_output_record` whose provider is operator-direct |

#### S5.2a Panel verdicts

Each verdict is said with its panel, for example "registry panel: approved for draft".

| Field value | Plain meaning |
|---|---|
| `APPROVE_FOR_DRAFT` | **approved for draft.** The draft may be written as a draft; nothing is in force yet |
| `OPERATOR_REVIEW` | **sent to operator review** |
| `REJECT` / `REJECT_DEFECT` | **rejected, with a defect code.** Two spellings of one result (S5.6 defect 1) |
| `PASS`, `REJECT`, `REVOKE` (certification panel) | **certification passed, rejected, or revoked** |

**"Verdict" is never said alone.** Six records use a field called `verdict_code`, each with different values. These include the chain verdict (green, amber, red), self-verification (pass, fail) and publication eligibility. Say "panel verdict", "chain verdict" and so on.

### S5.3 The operator's answers (2026-10-02)

1. **The third seat keeps each panel's decided word,** always said with the panel: "moderator" for the registry and certification panels, "judge" for the metric authoring panel (DEC-09f86b). The metric panel's record is to be corrected to say judge (S5.6 defect 4).
2. **"Park" is retired for panel outcomes.** Say "sent to operator review" or "waiting for operator confirm", whichever is meant. "Parked" stays a DevHub task state only.
3. **"Certification" alone means metric certification** by the certification panel. The registry's records are said as **"registry certification record"**.
4. **"Consensus", "quorum" and "dissent" are retired as panel words.** Say "the judge's holding" or "the moderator's verdict".

### S5.4 Words not approved, and what to say instead

| Not approved | Say instead |
|---|---|
| verdict (alone) | "panel verdict", "chain verdict", "certification decision", whichever is meant |
| park, parked (of a panel outcome) | "sent to operator review" or "waiting for operator confirm" |
| approved (of a panel draft) | "approved for draft". Nothing a panel approves is in force until its governed act and gates have run |
| certification (of a registry act) | "registry certification record" |
| consensus, quorum, dissent | "the judge's holding", "the moderator's verdict" |
| gate (for the third seat) | "moderator" (DEC-149ab2 retired "gate" for this seat) |
| unverified, degraded (of a panel) | "vendor failure" and the run's outcome. "Unverified" is a source catalog word (slice 3) |
| AI panel (for the conversation surface) | "conversation panel" |
| bc-ai | retired (DEC-ffee4e): "the registry authoring panel, in bc-core" |

### S5.5 Where counts are read

| To know how many | Read |
|---|---|
| registry panel runs by verdict | `bcf.panel_output_record.verdict_code`, excluding operator-direct rows |
| runs waiting for an operator disposition | `bcf.panel_output_record` where the verdict is `OPERATOR_REVIEW` and `disposition_code` is empty |
| metric authoring panel runs | `mcf.metric_authoring_panel_run` |
| certification panel runs and decisions | `mcf.audit_contextual_panel_run`; `metric_audit.decision` |
| the certification roster in force | `mcf.audit_panel_roster_registration` where `valid_to` is empty |

### S5.6 Defects found while reading, named, not fixed here

1. **The registry panel's verdict has no value rule, and one result has two spellings.** `bcf.panel_output_record.verdict_code` has no CHECK. ADR DEC-ffee4e names `REJECT_DEFECT`, while the registry panel's code writes `REJECT`; one row holds `PASS`. Owner: Platform, with DB; a schema change needs the operator's yes.
2. **One table holds panel verdicts and entries no panel made.** `bcf.panel_output_record` also stores operator-direct entries and operator adjudications, written as `APPROVE_FOR_DRAFT`. So "approved for draft" in that table does not always mean a panel approved. Separate them, or record the origin in a field that every read must use. Owner: Architect, with Platform.
3. **The documented roster is not the roster that runs.** The procedure and ADR DEC-ffee4e name GPT-5.5 as the registry panel's moderator; DEC-53629b replaced it with GLM-5. The metric panel's model-defaults header names models other than its constants. Docs and code headers are to be corrected to the decided rosters. Owner: Docs, with Platform.
4. **The metric panel's third seat is a judge by decision but a moderator by record.** `mcf.metric_authoring_panel_transcript.model_role_code` allows maker, checker, moderator; DEC-09f86b's judge is stored as `moderator`. Owner: Metric, with DB; a schema change needs the operator's yes.
5. **"Certification record" is three tables.** `bcf.certification_record` (registry and older business-field acts), `contract.certification_record` (frozen since 2026-05-26, yet cited by DEC-c48b0f) and `mcf.certification_record` (metric acts, still named `audit_*` although DEC-c48b0f retired "audit"). Its links to panel runs point into both `contract.` and `bcf.panel_output_record`. Owner: Architect, with DB and Metric.
6. **One act, four names.** Adding a characteristic is `createCharacteristic` in the procedure and packet, `registerCharacteristic` in the registry service, `registry_author_vocabulary` as the certification action, and "characteristic admission" in the prompt. Owner: Platform, with Docs.
7. **The ABC reasoning panel keeps no record of its runs.** No table holds ABC panel runs. Either its runs are recorded like the others, or the ADR states why not. Owner: Architect.
8. **Retired material is still marked authoritative.** `docs/ai/` pages carry `authority: authoritative` and describe bc-ai, which DEC-ffee4e retired. ADR DEC-149ab2's title still says "Business Context Framework", retired by slice 4. Owner: Docs.

**Raised separately, and not a vocabulary matter:** the off-pool maker's evidence records a vendor, a latency and timestamps that did not occur (Invariant VI). That is TSK-9e0b6e, owned by Metric with Platform.
