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

*Design note · proposed 2026-11-25, revision 1 · nothing in this note has been built or run. Its database change is a proposal and **needs the owner's database yes** under the Database Change Protocol before any migration is written.*

Evidence base, read on 2026-11-25: bc-admin `origin/main` 6267a64, bc-portal `origin/main` 04930c8, bc-core `origin/main` df47ce00, bc-db `origin/main` 18d6884, bc-docs `origin/main` c948683, and the Demoed design amendment (bc-docs PR 272, branch `claude/demo-tests-design-amend-1`, head b8cb35d, file `docs/reference/technical-notes/implementation/metric-demo-tests-open-and-repeatable-design.md`, called "the Demoed design" below). Live rows were read read-only on `bc_platform_dev`. The owner's rulings are in barecount-devhub `artifacts/operator-review/DECISIONS-workflow-review.md` (branch `claude/operator-review-content`, head 2716b191): "Metric catalog FAQ" (2026-11-25 06:16 IST) and the rename of "test" to "Demoed" (06:35 IST).

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

| Kind | What it records | Where it sits | Why there |
|---|---|---|---|
| `fact` | What the metric means: what is counted, from which date, in which currency. | The **directory member version** (`metric_directory.member_version`). | Meaning is source-agnostic and versioned with the definition (owner's ruling; system-agnostic ruling 2026-11-24 22:21). It holds for every source type. |
| `decision` | A choice made while building, with its reason. Meaning choices sit with the member version; choices about one metric version (for example, approving it with a known gap) sit with that version. | Either home, by what it decides. | A decision belongs with the thing it decided. |
| `limitation` | A limit accepted when a version was approved. | The **metric contract version** (`mcf.metric_contract_version`), citing its **Demoed run**. | A limitation is a property of one version and of the evidence it was approved on (owner's ruling). |

### 2.3 Rules

1. **Every entry cites the governed fact it explains.** The entry is never a second source of truth (bc-docs `docs/overview/audited-metrics-differentiator.md:131`: the summary must derive from governed records). A meaning entry cites the member version by its identity and content hash, and, where it explains one rule, that rule's role code. A limitation cites the Demoed run that showed the limit.
2. **Entries are immutable.** A change is a new entry that supersedes the old one. A withdrawal is a new entry that supersedes it with a withdrawn mark. Nothing is updated or deleted.
3. **An entry is shown with the version it cites.** A meaning entry on member version `v2` is not shown for a metric version realized from `v3` until it is written again for `v3`. A new member version therefore starts with no entries; the onboarding step (section 5) carries them over by writing them again.
4. **The panel can flag a mismatch.** Because each entry names the fact it explains, a later panel check can read both and flag an entry whose text contradicts its fact (the panel is a flagger, DEC-346ae7). The flag is a separate design act; this design only makes it possible.
5. **Who may see an entry** is recorded on the entry: `customer` or `platform` (section 4.3).

### 2.4 What already exists, and why the FAQ is separate

| Table (read live) | What it holds | Why not use it |
|---|---|---|
| `metric_directory.member_knowledge` (6 columns, trigger `trg_member_knowledge_frozen`) | One definition, rationale and formula intent per member, not per version. No row for `MDM-11fab0`. | One row per member; no list of questions; not versioned with the meaning. |
| `mcf.metric_knowledge_profile` (15 columns, one row for `fe91c450`) | Panel-born summary per contract: definition summary, stakeholders and drivers as JSONB lists. Shown today on the admin detail page. | Per contract, not per version; panel-written; JSONB lists. Kept as is. |
| `metric_directory.member_version.definition_text` | The governed definition. | It is the fact an entry cites, not the entry. |

## 3. The database proposal — needs the owner's database yes

One bc-db forward migration, **0084** (number to be confirmed at authoring). On 2026-11-25 the highest merged migration is 0081, no bc-db branch carries a file numbered 0082 or higher, the only open pull request that claims a number is #177 (0073), and the Demoed design claims 0082 (demo side) and 0083 (platform side). 0084 applies **after 0083**, because the limitation table references the Demoed result table that 0083 adds. It follows the Database Change Protocol: authored once with its header contract and rollback, proven on an owner- and grant-faithful restore of a fresh read-only dump including the served-login (`bc_platform_runtime`) vectors, and applied through the governed runner under a separate recorded grant. ISO 11179 names (DEC-69f09e); at most 20 columns; FKs on every reference; no JSONB; indexes in the same migration (DEC-1918d0).

| What | Change | Why |
|---|---|---|
| `metric_directory.member_version_faq_entry` (15 columns) | add | The `fact` and `decision` entries about meaning. Columns: `member_version_faq_entry_uid` (uuid, PK); `member_version_uid` and `member_content_hash` (composite FK to the live unique key `(member_version_uid, content_hash)` of `metric_directory.member_version`, so an entry names the exact meaning it explains); `cited_discriminator_role_code` (FK with `member_version_uid` to `metric_directory.member_version_discriminator`, PK `(member_version_uid, role_code)`, nullable); `cited_direct_input_role_code` (same, to `member_version_direct_input`, nullable; at most one of the two set); `entry_kind_code` (check: `fact`, `decision`); `audience_code` (check: `customer`, `platform`); `entry_seq` (integer, display order); `question_text`, `answer_text`, `reason_text`, `impact_text` (text, non-empty; `reason_text` and `impact_text` may be NULL for a plain fact); `supersedes_entry_uid` (self FK, unique, nullable); `withdrawn_flag` (boolean; true only on a superseding row); `created_by_name`, `created_at`. |
| `mcf.metric_version_faq_entry` (15 columns) | add | The `limitation` and version `decision` entries. Columns: `metric_version_faq_entry_uid` (uuid, PK); `metric_contract_version_uid` (FK to `mcf.metric_contract_version`); `cited_demoed_result_uid` (FK to `mcf.metric_version_demoed_result`, added by 0083; NOT NULL for a `limitation`); `cited_demoed_result_element_uid` (FK to `mcf.metric_version_demoed_result_element`, added by 0083, nullable: the uncovered rule, when the limit is one); `entry_kind_code` (check: `limitation`, `decision`); `audience_code`; `entry_seq`; the four text columns; `supersedes_entry_uid` (self FK, unique); `withdrawn_flag`; `created_by_name`, `created_at`. |
| `trg_member_version_faq_entry_immutable`, `trg_metric_version_faq_entry_immutable` | add | Refuse UPDATE, DELETE and TRUNCATE, like `trg_member_version_immutable` and `trg_demoed_evidence_bridge_immutable` (read live). A superseding row must cite the same member version (or metric version) as the row it supersedes. |
| `idx_member_version_faq_entry_member_version_uid`, `idx_metric_version_faq_entry_metric_contract_version_uid` | add | The screens read entries by version. |
| Grants to `bc_platform_runtime` | add | SELECT and INSERT on both tables; no UPDATE or DELETE. |

**Not proposed:** an `archived_at` column. DEC-1918d0 rule 8 says soft delete uses `archived_at`, but setting it is an update, and the owner ruled the entries immutable. A withdrawal is a superseding row with `withdrawn_flag` true (question 3). **No change** to the Demoed design's 0082 and 0083: the FAQ references their result rows, so they need no FAQ column (as answered to the owner on 2026-11-25 06:35).

## 4. The screens

All reads go through bc-core and only read records; no read starts an evaluation.

### 4.1 The Demoed column on the bc-admin Metric Catalog

- **Screen:** `src/pages/MetricCatalogPage.tsx`, route `catalog/metrics` (`src/components/AppRouter.tsx:203`). Columns today: Metric ID, Metric Name, Function, Sub-function, Type, Description, Declaration chain (`:241`), State (`:246`).
- **What changes:** the **Demoed** column goes between Declaration chain and State, with the cell texts and the "Flagged" filter exactly as the Demoed design's section 9 lays them out. This design adds nothing to it except a small "FAQ" count in the Metric Name cell (for example "FAQ 3"), linking to the detail page.
- **Reads:** `GET /api/mcf/metric-contracts` (`McfPublicationEligibilityController.list`, bc-core `src/registry/mcf/mcf-publication-eligibility.controller.ts:70-77`, served by `McfReadService.listMetricContracts`, `src/registry/mcf/mcf-read.service.ts:426`). New fields on `McfMetricContract` (bc-admin `src/api/mcf-catalog.ts:14`): the Demoed counts (Demoed design) and `faq_entry_count`.

### 4.2 The bc-admin metric detail page

- **Screen:** it exists: `src/pages/MetricDetailPage.tsx`, route `catalog/metrics/governed/:metricContractUid` (`AppRouter.tsx:204`). Today it shows Trust, the governed actions, Definition and Metric Knowledge side by side (`:434`), Registry bindings (`:478`), Versions (`:509`), lineage and the inspector (`:558`).
- **New card "FAQ"**, full width, after Definition and Metric Knowledge. For the current version it lists the meaning entries of its operative member version, then the version's own entries. Each entry shows its question as a heading, the answer, then "Why" and "What it changes"; a kind label (Fact, Decision, Limitation); an audience label (Shown to customers, Platform only); and a "Cites" line linking to the fact: the member version and rule (to `/directory` member detail), or the Demoed run. A toggle shows superseded and withdrawn entries. Kind and audience labels come from a master hook, not a hard-coded list (coding standard 14).
- **New card "Demoed runs"**, after FAQ: the list the Demoed design's section 9 names (time, verdict pass or fail, coverage, the Demoed record it wrote, the ticket, the resolution). A failed run with no resolution shows the flag. A limitation entry that cites a run shows a link to it.
- **Reads:** `GET /api/mcf/metric-contracts/:metricContractUid` (`mcf-publication-eligibility.controller.ts:91-98`, `readMetricContractDetail`). New fields on `McfMetricContractDetail` (bc-admin `src/api/mcf-catalog.ts:142`): `faq_entries` and `demoed_runs`. The operative member version is read from `metric_directory.realization_operative` (for `b9357731` it is `d49b1b25`, read live).

### 4.3 The bc-portal metric page

- **Screen:** `apps/web/src/surfaces/workspace/pages/metrics/MetricAssetDetailPage.tsx`, route `/workspace/metrics/:metricId` (`apps/web/src/components/AppRouter.tsx:163`). Its sections (`:91-251`) are Overview, Settings, Plan / Targets, How the metric is computed, What input shape is required, What facts are produced, and six more (Drivers, Actions, Quality, Logs, Snapshots, and one whose label is a word the vocabulary rule forbids).
- **New section "Questions and answers"**, after "How the metric is computed". It shows only `customer` entries of the version this tenant is served and of that version's operative member version, in the same four parts. It shows no Demoed runs, no ticket and no rule codes; the "Cites" line reads, for example, "Part of the metric definition, version 2".
- **Reads:** a new tenant read beside `GET /api/t/metrics/:metricId` (bc-core `src/tenant-views/tenant-views.controller.ts:530-534`), for example `GET /api/t/metrics/:metricId/faq`, returning only `customer` entries.
- **Proposal for who sees what (question 1):**

| Kind | Default audience | Reason |
|---|---|---|
| `fact` | customer | It says what the number means. Hiding it would leave customers to guess. |
| `decision` about meaning | customer | The reason behind a definition choice is what a business reader asks ("why are credit notes left out?"). |
| `decision` about one version | platform | It is about approval, not about the number. |
| `limitation` | chosen per entry | A limit on what the number means ("foreign-currency invoices are counted once, not converted") is customer; a limit on how it was proven ("credit notes were not in the months shown") is platform. The audited-metrics differentiator lets customers see the facts "appropriate to the customer's access rights" (`:130`). |

## 5. The onboarding-guide step

In `docs/onboarding/onboard-one-metric-to-the-metric-catalog.md`, a new **Step 11. Write the metric's FAQ**, between Step 10 (Prove on the demo world, `:270`) and today's Step 11 (Certify and activate, `:287`), which becomes Step 12. It comes after the Demoed run, because a limitation cites one, and before certification, as the owner ruled.

- **Inputs:** the operative member version, the passed Demoed run, the questions raised in steps 3 to 10.
- **Do:** write one `fact` entry for each rule a business reader would ask about (at least each discriminator); one `decision` for each choice the build made; one `limitation` for each accepted limit, citing the Demoed run. Set the audience. If the member version is new, write again the entries of the member version it supersedes that still hold.
- **Check:** the detail page's FAQ card lists them; the portal section shows only the customer ones.
- **Certify and activate a metric version** (`docs/onboarding/certify-and-activate-a-metric-version.md`), step 6: whether certification refuses a version with no FAQ entry is question 2.

**First use, customer invoice volume (`b9357731`):** facts on `d49b1b25` for "Are credit notes counted?" (cites `disc:where#0000`), "Are customer payments counted?" and "Which date decides the month?"; one limitation, citing the every-month Demoed run once it exists, if any rule stays uncovered.

## 6. Foundation gate (DEC-79b62f)

1. **Why this location?** B, contract semantics, for the meaning entries: they explain the member version's declared meaning and cite it by content hash. E, storage, for the immutable rows. F, read model, for the screens, which only read.
2. **Why not an upper layer?** A and B are not underspecified: the meaning is fully declared (definition text and discriminator, read live). The FAQ adds explanation, not meaning, so it compensates for nothing.
3. **Why not a lower layer?** No working implementation is bypassed. `member_knowledge` and `metric_knowledge_profile` hold single summaries and stay as they are (2.4).
4. **Design act or execution act?** A design act: a new declaration (the entry) and where it lives. It changes no evaluation.

Invariants: **I**, an entry never changes what a metric means; it cites meaning evaluated once. **III**, entries are immutable and superseded (2.3 rule 2). **IV**, every citation names a versioned object (member version plus content hash, Demoed result), never a head version. **VI**, a limitation cites the Demoed run's emitted record; it never infers coverage.

## 7. Open questions for the owner

1. **Who sees which kind on the portal?** Proposal: facts and meaning decisions always; limitations chosen per entry; version decisions never (4.3).
2. **Must a version have FAQ entries before certification?** Proposal: not refused by the database in revision 1; the guide makes it a step and the detail page shows "No FAQ yet". A hard refusal can follow once the step is proven on customer invoice volume.
3. **Withdrawal without `archived_at`:** a superseding row with a withdrawn mark keeps entries immutable, but departs from DEC-1918d0 rule 8. Accept, or allow a one-time `archived_at` stamp?
4. **The detail-page placement:** FAQ as its own full-width card (proposed), or inside Metric Knowledge?

## 8. What was not grounded

- **The portal page does not yet read the governed metric.** `TenantMetricCatalogService.getDetail` (bc-core `src/tenant-views/tenant-metric-catalog.service.ts:107`) reads the legacy metric definition by `metricDefinitionId` and has no metric contract version. How the portal names the version a tenant is served is not settled here; the FAQ read needs it.
- The 0083 tables `mcf.metric_version_demoed_result` and `_result_element` do not exist yet; their key names are taken from the Demoed design, section 16.
- The master list behind the kind and audience labels (which master table or hook) was not looked up.
- The panel's mismatch flag (2.3 rule 4) is a separate design act.
- No screen was opened in a browser; the screens were read from source at `origin/main`.
