---
uid: metric-catalog-faq-design
title: The metric FAQ, decided facts and accepted limitations in business language, and the screens that show it with the Demoed runs (design)
description: "Design for the owner's ruling of 2026-11-25: a plain-text FAQ on the metric catalog that records the questions answered and decided while a metric is built, and the limitations accepted, each entry citing the governed fact it explains. Places the entries in the database, adds a step to the onboarding guide, and lays out three screens: the Demoed column on the bc-admin Metric Catalog, the bc-admin metric detail page, and the bc-portal metric page. Nothing is built."
status: drafting
authority: reference
date: 2026-11-25
project: bc-docs
domain: metrics
subdomain: metric-catalog/faq
focus: design
governing_adr: DEC-79b62f
---

# The metric FAQ: decided facts and accepted limitations

*Design note · proposed 2026-11-25, revision 2 · nothing in this note has been built or run. Its database change is a proposal and **needs the owner's database yes** under the Database Change Protocol before any migration is written.*

Revision 2 applies the nine fixes of an independent Foundation check (verdict "fits with fixes"), each checked again against live, and writes the checker's recommendations into section 7 as proposals for the owner.

Evidence base, read on 2026-11-25: bc-admin `origin/main` 6267a64, bc-portal `origin/main` 04930c8, bc-core `origin/main` df47ce00, bc-db `origin/main` 18d6884, bc-docs `origin/main` c948683, and the Demoed design amendment (bc-docs PR 272, branch `claude/demo-tests-design-amend-1`, head f0f45eb, file `docs/reference/technical-notes/implementation/metric-demo-tests-open-and-repeatable-design.md`, called "the Demoed design" below). Live rows were read read-only on `bc_platform_dev`. The owner's rulings are in barecount-devhub `artifacts/operator-review/DECISIONS-workflow-review.md` (branch `claude/operator-review-content`, head 2716b191): "Metric catalog FAQ" (2026-11-25 06:16 IST) and the rename of "test" to "Demoed" (06:35 IST).

## 1. The problem

While a metric is built, people answer questions about it. For **customer invoice volume** (metric contract `fe91c450`, version `b9357731`, `audit_pending`) one was: are credit notes counted? The answer is no. The reason is that the metric counts customer invoices only. The effect is that a month with many credit notes shows a higher count than the net business.

Today the answer lives in three places, none of them a record a reader can find:

- the definition text of directory member `MDM-11fab0` version `v2` (member version `d49b1b25`): "Customer payments and credit notes are not counted" (read live);
- the governed rule that enforces it: discriminator `disc:where#0000`, `eq ["customer_invoice"]` on that member version (read live);
- the Demoed design's section 1, which found that the four declared months held no credit memo, so the rule was never put to the test: an accepted limitation until the every-month Demoed run passes.

Nothing records the question, the reason and the effect in words a business reader understands, or the limitations the platform accepted when it approved a version.

## 2. The model

### 2.1 An entry

Each entry is one question and its answer, in plain business words, in the style of the AWS developer guides. It has four text parts: the **question**, the **answer**, **why** and **what it changes**. Example:

| Part | Text |
|---|---|
| Question | Are credit notes counted? |
| Answer | No. Only customer invoices are counted. |
| Why | The metric measures how many invoices you issue, not your net sales. |
| What it changes | In a month with many credit notes, the count is higher than your net business. |

### 2.2 Three kinds, two homes

| Kind | What it records | Where it sits | What it must cite |
|---|---|---|---|
| `fact` | What the metric means: what is counted, from which date, in which currency, how it is rounded. | The **directory member version** (`metric_directory.member_version`). Meaning is source-agnostic and versioned with the definition (owner's ruling; system-agnostic ruling 2026-11-24 22:21). | Exactly one declared element of that member version: a rule (a discriminator or a direct input, by role code) or a named intent (the temporal intent or the output intent). An entry that cannot cite one is not a fact. |
| `decision` | A choice made while building, with its reason. A meaning choice sits with the member version; a choice about one metric version (for example, approving it with a known gap) sits with that version. | Either home, by what it decides. | A meaning decision cites one item of the member version's `decision_evidence_refs` by its position, rather than restating it. A version decision cites a Demoed run. |
| `limitation` | A gap in the evidence: what the Demoed runs did not exercise. | The **metric contract version** (`mcf.metric_contract_version`). | The Demoed run that showed the gap and, where the gap is one rule, its coverage element. |

What the metric does, in every case, is meaning, so it is a `fact` on the member version, never a `limitation`. "Foreign-currency invoices are counted once, not converted" is a fact (it cites the output intent). "No month shown held a credit note" is a limitation (it cites the Demoed run whose coverage left the document-type rule unexercised).

Read live for member version `d49b1b25`: the discriminator `disc:where#0000` (`eq ["customer_invoice"]`); the temporal intent `{"shape_code": "period_aggregate", "params": {"period_type": "fiscal_period"}}`; the output intent (integer, count, no rounding); and four `decision_evidence_refs` items, the fourth being the owner's ruling on the plain-language definition.

### 2.3 Rules

1. **Every entry cites the governed fact it explains.** The entry is never a second source of truth (bc-docs `docs/overview/audited-metrics-differentiator.md:131`: the summary must derive from governed records). Every citation names a versioned object: the member version with its content hash, or the Demoed run with its declaration and metric version.
2. **The bound: an answer states only what its citation carries.** The onboarding step (section 5) refuses a `fact` whose answer states meaning its cited element does not carry. A person checks each answer against its citation before the entry is written. This check is what stops the FAQ from becoming a second source of truth. The panel's mismatch flag (DEC-346ae7: the panel is a flagger) is a separate, later design act; it adds a net, it does not replace the check.
3. **Entries are immutable.** A change is a new entry that supersedes the old one. A withdrawal is a new entry that supersedes it with a withdrawn mark. Nothing is updated or deleted.
4. **An entry is shown with the version it cites.** A meaning entry on member version `v2` is not shown for a metric version realized from `v3` until it is written again for `v3`. A new member version starts with no entries; the onboarding step writes again those that still hold.
5. **Entries name no source system.** A metric is proven once and holds for every source (system-agnostic ruling). A limitation of a source mapping belongs with that source's observation or canonical contract version, in a separate design, never with the metric.
6. **Who may see an entry** is recorded on the entry: customer or platform (section 4.3).

### 2.4 What already exists, and why the FAQ is separate

| Table (read live) | What it holds | Decision |
|---|---|---|
| `metric_directory.member_knowledge` (6 columns; 0 rows in total; one row per member; `bc_platform_runtime` holds INSERT, UPDATE and SELECT; `trg_member_knowledge_frozen` freezes definition and formula intent once a governed member version exists, and leaves `rationale_text` mutable) | One definition, rationale and formula intent per member, not per version. | **Kept, untouched and out of scope.** It is mutable and per member, so the FAQ cannot live there; nothing in live grounding calls for retiring it in this design. |
| `mcf.metric_knowledge_profile` (15 columns, one row for `fe91c450`) | Panel-born summary per contract, with JSONB lists. Shown today on the admin detail page. | Kept as is. Per contract, not per version. |
| `metric_directory.member_version` (`definition_text`, the intents, `decision_evidence_refs`) | The governed meaning. | It is what an entry cites, not the entry. |

## 3. The database proposal — needs the owner's database yes

One bc-db forward migration, **0084** (number to be confirmed at authoring). On 2026-11-25 the highest merged migration is 0081, no bc-db branch carries a file numbered 0082 or higher, the only open pull request that claims a number is #177 (0073), and the Demoed design claims 0082 (demo side) and 0083 (platform side). 0084 applies **after 0083**, because the limitation table references the Demoed result tables that 0083 adds. **0083 is not changed** (the owner has said yes to it): the unique keys that 0084's composite FKs need on 0083's tables are added by 0084 itself, with `ALTER TABLE … ADD CONSTRAINT … UNIQUE`.

It follows the Database Change Protocol: authored once with its header contract and rollback, proven on an owner- and grant-faithful restore of a fresh read-only dump including the served-login (`bc_platform_runtime`) vectors, and applied through the governed runner under a separate recorded grant. ISO 11179 names (DEC-69f09e); at most 20 columns; FKs on every reference; no JSONB; indexes in the same migration (DEC-1918d0). The master tables follow the live pattern of `master.master_metric_shape` (`shape_code` PK, `label`, `description`, `sort_order`, `archived_at`), served by bc-core `/api/masters/*` (`src/platform/masters/masters.controller.ts:14`) to the bc-admin `useMaster*` hooks (`src/api/masters.ts`).

| What | Change | Why |
|---|---|---|
| `master.master_faq_entry_kind` (5 columns: `entry_kind_code` PK, `label`, `description`, `sort_order`, `archived_at`; rows `fact`, `decision`, `limitation`) | add | The kind list the screens read through a `useMaster*` hook (coding standard 14), instead of a CHECK. |
| `master.master_faq_audience` (5 columns: `audience_code` PK, same shape; rows `customer`, `platform`) | add | The audience list, the same way. |
| `metric_directory.member_version_faq_entry` (18 columns) | add | The `fact` and meaning `decision` entries. Columns: `member_version_faq_entry_uid` (uuid PK); `member_version_uid` and `member_content_hash` (composite FK to the live unique key `(member_version_uid, content_hash)` of `metric_directory.member_version`); `cited_discriminator_role_code` (with `member_version_uid`, FK to `member_version_discriminator`, PK `(member_version_uid, role_code)`); `cited_direct_input_role_code` (same, to `member_version_direct_input`); `cited_intent_code` (`temporal_intent` or `output_intent`: the member version's own `temporal_intent_json` or `output_intent_json`); `cited_decision_evidence_ordinal` (integer, the 1-based position in `decision_evidence_refs`); `entry_kind_code` (FK to `master.master_faq_entry_kind`); `audience_code` (FK to `master.master_faq_audience`); `entry_seq` (display order); `question_text`, `answer_text`, `reason_text`, `impact_text`; `supersedes_entry_uid` (self FK, unique); `withdrawn_flag`; `created_by_name`; `created_at`. A CHECK fixes the home: kind `fact` or `decision` only; a fact sets exactly one of the three element citations; a decision sets the ordinal. |
| `mcf.metric_version_faq_entry` (16 columns) | add | The `limitation` and version `decision` entries. Columns: `metric_version_faq_entry_uid` (uuid PK); `metric_contract_version_uid`; `cited_demoed_declaration_uid`; `cited_demoed_result_uid` (NOT NULL); `cited_demoed_result_element_uid` (nullable: the unexercised rule, when the gap is one); `entry_kind_code` and `audience_code` (FKs to the masters); `entry_seq`; the four text columns; `supersedes_entry_uid` (self FK, unique); `withdrawn_flag`; `created_by_name`; `created_at`. A CHECK fixes the home: kind `limitation` or `decision` only. |
| Composite FK `(cited_demoed_declaration_uid, metric_contract_version_uid)` to `mcf.metric_version_demoed_declaration (metric_version_demoed_declaration_uid, metric_contract_version_uid)` | add, with `ALTER TABLE mcf.metric_version_demoed_declaration ADD CONSTRAINT uq_metric_version_demoed_declaration_uid_mcv UNIQUE (…)` in 0084 | Ties the cited run to the same metric version as the entry. The 0083 result table has no metric-version column (Demoed design 5.1 item 2); it reaches the version through its declaration, which 0076 keeps unique per version (`uq_metric_version_demoed_declaration_mcv`, read live). |
| Composite FK `(cited_demoed_result_uid, cited_demoed_declaration_uid)` to `mcf.metric_version_demoed_result (metric_version_demoed_result_uid, metric_version_demoed_declaration_uid)` | add, with `ALTER TABLE mcf.metric_version_demoed_result ADD CONSTRAINT … UNIQUE (…)` in 0084 (0083 unchanged) | The cited run belongs to that declaration. |
| Composite FK `(cited_demoed_result_element_uid, cited_demoed_result_uid)` to `mcf.metric_version_demoed_result_element (element uid, result uid)` | add, with `ALTER TABLE mcf.metric_version_demoed_result_element ADD CONSTRAINT … UNIQUE (…)` in 0084 (0083 unchanged) | The cited element belongs to the cited run. |
| `trg_member_version_faq_entry_guard`, `trg_metric_version_faq_entry_guard` | add | Refuse UPDATE, DELETE and TRUNCATE, like `trg_member_version_immutable` (read live). A superseding row cites the same member version (or metric version) as the row it supersedes. On the member table, refuse an ordinal beyond the length of `decision_evidence_refs` (an FK cannot reach an item of a JSON list). |
| `idx_member_version_faq_entry_member_version_uid`, `idx_metric_version_faq_entry_metric_contract_version_uid` | add | The screens read entries by version. |
| Grants to `bc_platform_runtime` | add | SELECT and INSERT on both entry tables; SELECT on both masters; no UPDATE or DELETE. |

**Withdrawal without `archived_at`.** DEC-1918d0 rule 8 says soft delete uses `archived_at`, but setting it is an update, and the owner ruled the entries immutable. A withdrawal is a superseding row with `withdrawn_flag` true. The migration header records this exception. The master tables keep `archived_at`, like the other masters. **No change** to the Demoed design's 0082 and 0083 (as answered to the owner on 2026-11-25 06:35).

## 4. The screens

All reads go through bc-core and only read records; no read starts an evaluation.

### 4.1 The Demoed column on the bc-admin Metric Catalog

- **Screen:** `src/pages/MetricCatalogPage.tsx`, route `catalog/metrics` (`src/components/AppRouter.tsx:203`). Columns today: Metric ID, Metric Name, Function, Sub-function, Type, Description, Declaration chain (`:241`), State (`:246`).
- **What changes:** the **Demoed** column goes between Declaration chain and State, with the cell texts and the "Flagged" filter exactly as the Demoed design's section 9 lays them out. This design adds only a small "FAQ" count in the Metric Name cell (for example "FAQ 3"), linking to the detail page.
- **Reads:** `GET /api/mcf/metric-contracts` (`McfPublicationEligibilityController.list`, bc-core `src/registry/mcf/mcf-publication-eligibility.controller.ts:70-77`, served by `McfReadService.listMetricContracts`, `src/registry/mcf/mcf-read.service.ts:426`). New fields on `McfMetricContract` (bc-admin `src/api/mcf-catalog.ts:14`): the Demoed counts (Demoed design) and `faq_entry_count`.

### 4.2 The bc-admin metric detail page

- **Screen:** it exists: `src/pages/MetricDetailPage.tsx`, route `catalog/metrics/governed/:metricContractUid` (`AppRouter.tsx:204`). Today it shows Trust, the governed actions, Definition and Metric Knowledge side by side (`:434`), Registry bindings (`:478`), Versions (`:509`), lineage and the inspector (`:558`).
- **New card "FAQ"**, its own full-width card after Definition and Metric Knowledge. For the current version it lists the meaning entries of its operative member version, then the version's own entries. Each entry shows its question as a heading, the answer, then "Why" and "What it changes"; a kind label and an audience label from the `useMaster*` hooks; and a "Cites" line linking to the fact: the member version and its rule or intent (to the `/directory` member detail), the decision-evidence item, or the Demoed run. A toggle shows superseded and withdrawn entries.
- **New card "Demoed runs"**, after FAQ: the list the Demoed design's section 9 names (time, verdict pass or fail, coverage, the Demoed record it wrote, the ticket, the resolution). A failed run with no resolution shows the flag. A limitation that cites a run links to it.
- **Reads:** `GET /api/mcf/metric-contracts/:metricContractUid` (`mcf-publication-eligibility.controller.ts:91-98`, `readMetricContractDetail`). New fields on `McfMetricContractDetail` (bc-admin `src/api/mcf-catalog.ts:142`): `faq_entries` and `demoed_runs`. The operative member version is read from `metric_directory.realization_operative` (for `b9357731` it is `d49b1b25`, read live).

### 4.3 The bc-portal metric page

- **Screen:** `apps/web/src/surfaces/workspace/pages/metrics/MetricAssetDetailPage.tsx`, route `/workspace/metrics/:metricId` (`apps/web/src/components/AppRouter.tsx:163`). Its sections (`:91-251`) are Overview, Settings, Plan / Targets, How the metric is computed, What input shape is required, What facts are produced, and six more (Drivers, Actions, Quality, Logs, Snapshots, and one whose label is a word the vocabulary rule forbids).
- **New section "Questions and answers"**, after "How the metric is computed". It shows only `customer` entries of the version this tenant is served and of its operative member version, in the same four parts. It shows no Demoed runs, no ticket and no rule codes; the "Cites" line reads, for example, "Part of the metric definition, version 2".
- **Reads:** a new tenant read beside `GET /api/t/metrics/:metricId` (bc-core `src/tenant-views/tenant-views.controller.ts:530-534`), for example `GET /api/t/metrics/:metricId/faq`, returning only `customer` entries. Open item: the portal page reads the legacy definition today (section 8).
- **Proposed audience by kind (for the owner's confirmation):**

| Kind | Audience | Reason |
|---|---|---|
| `fact` | customer | It says what the number means. Hiding it would leave customers to guess. |
| meaning `decision` | customer | The reason behind a definition choice is what a business reader asks ("why are credit notes left out?"). |
| version `decision` | platform | It is about approval, not about the number. |
| `limitation` | platform, always | After rule 2.2, a limitation is only a gap in the Demoed evidence, which is about how the version was proven, not what the number means. Everything a customer needs about the number is a fact. |

## 5. The onboarding-guide step

In `docs/onboarding/onboard-one-metric-to-the-metric-catalog.md`, a new **Step 11. Write the metric's FAQ**, between Step 10 (Prove on the demo world, `:270`) and today's Step 11 (Certify and activate, `:287`), which becomes Step 12. It comes after the Demoed run, because a limitation cites one, and before certification, as the owner ruled.

- **Inputs:** the operative member version, the Demoed runs, the questions raised in steps 3 to 10.
- **Do:**
  1. Write one `fact` for each declared element a business reader would ask about (at least each discriminator, the temporal intent and the output intent), citing that element.
  2. Write one meaning `decision` for each item of `decision_evidence_refs` a reader would ask about, citing it by position.
  3. Write one `limitation` for each rule or case the Demoed runs did not exercise, citing the run and, where there is one, its coverage element.
  4. If the member version is new, write again the entries of the member version it supersedes that still hold.
- **Check (refuse on failure):** a person reads each answer against its citation. Refuse a `fact` whose answer states meaning its cited element does not carry; write the missing meaning into a new member version first, or narrow the answer. Refuse an entry that names a source system (rule 2.3.5).
- **Read back:** the detail page's FAQ card lists the entries; the portal section shows only the customer ones.
- **Certify and activate a metric version** (`docs/onboarding/certify-and-activate-a-metric-version.md`), step 6: no database refusal in revision 1 (question 2).

**First use, customer invoice volume (`b9357731`), on member version `d49b1b25`:**

| Question | Cites |
|---|---|
| Are credit notes counted? | discriminator `disc:where#0000` |
| Are customer payments counted? | discriminator `disc:where#0000` |
| Which date decides the month? | temporal intent |
| Is the count rounded or converted? | output intent |
| Why is the definition written this way? (meaning decision) | `decision_evidence_refs` item 4 |

Plus one limitation on `b9357731` if the every-month Demoed run leaves a rule unexercised, citing that run.

## 6. Foundation gate (DEC-79b62f)

1. **Why this location?** B, contract semantics, for the meaning entries: they explain the member version's declared meaning, cite one declared element of it by content hash, and may state nothing it does not carry. E, storage, for the immutable rows. F, read model, for the screens, which only read.
2. **Why not an upper layer?** A and B are not underspecified: the meaning is declared (definition text, discriminator, intents, decision evidence, read live). The FAQ adds explanation, not meaning; a meaning the element does not carry is refused and goes into a new member version (rule 2.3.2), so the FAQ compensates for nothing.
3. **Why not a lower layer?** No working implementation is bypassed. `member_knowledge` and `metric_knowledge_profile` stay as they are (2.4).
4. **Design act or execution act?** A design act: a new declaration (the entry) and where it lives. It changes no evaluation. The panel's mismatch flag, when designed, is a net, not the fix; the fix is the bound in rule 2.3.2.

Invariants: **I**, an entry never changes what a metric means; it cites meaning evaluated once. **III**, entries are immutable and superseded (rule 2.3.3). **IV**, every citation names a versioned object (member version plus content hash; Demoed run tied by composite FKs to its declaration and the same metric version), never a head version. **VI**, a limitation cites the Demoed run's emitted record; it never infers coverage.

## 7. Proposals for the owner's confirmation

The independent Foundation check recommended each of these; they are written in as proposals, not yet confirmed.

1. **Who sees what on the portal:** customers see facts and meaning decisions; every limitation and every version decision is platform-only (4.3).
2. **Certification:** no database refusal of a version without FAQ entries in revision 1; the guide makes it a step and the detail page shows "No FAQ yet". A refusal can follow once the step is proven on customer invoice volume.
3. **Withdrawal:** a superseding row with a withdrawn mark, not `archived_at`; the exception to DEC-1918d0 rule 8 is recorded in the migration header.
4. **Placement:** the FAQ is its own full-width card on the detail page.

**Still open:** the portal page reads the legacy definition, not the governed metric (section 8).

## 8. What was not grounded

- **The portal page does not read the governed metric yet.** `TenantMetricCatalogService.getDetail` (bc-core `src/tenant-views/tenant-metric-catalog.service.ts:107`) reads the legacy metric definition by `metricDefinitionId` and has no metric contract version. How the portal names the version a tenant is served is not settled here; the portal FAQ read needs it.
- The 0083 tables do not exist yet. Their key names come from the Demoed design (5.1 items 2 and 3); the result element's column naming its result is described there only as "result FK", so the exact column name is settled at authoring.
- Whether `member_version.content_hash` covers `decision_evidence_refs` was not checked; the ordinal citation relies on the member version being immutable (`trg_member_version_immutable`, read live) either way.
- An FK cannot reach an item of a JSON list, so the decision-evidence citation is checked by the insert trigger, not by an FK.
- The panel's mismatch flag is a separate design act.
- No screen was opened in a browser; the screens were read from source at `origin/main`.
