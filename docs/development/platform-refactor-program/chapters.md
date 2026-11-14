---
id: platform-refactor-program-chapters
order: 45.5
title: "The State of Every bc-docs Chapter"
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

# The State of Every bc-docs Chapter

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md).

This annex lists every chapter file in the BareCount documentation repository, bc-docs, and gives each one a chapter verdict: keep it, rewrite it, mark it as history, or keep it as a design that is not built. A reader can use it to decide whether a chapter can be trusted before opening it. One row is one chapter: its path, title, authority, status, the date of its last commit, its verdict, the function of the functional map it mainly belongs to, and the reason with the reading report that gave it. bc-docs was read at `origin/main`, commit `f4f5edd`, dated 2026-11-11; the reading reports are dated 2026-11-13. Limits that apply to the whole annex: the verdicts and reasons are the reading reports' findings and were not re-checked against code or data; the reports are working files and cannot be cited at a commit; the copy of bc-docs on disk was not read; the assignment of a chapter to a function is this annex's own reading. The annex counts 131 chapter files in ten folders; the evidence annex (row 21a) counts 124 in nine folders, because it leaves out the seven files of `docs/archive`.

Sources read for this annex:
- bc-docs at `origin/main`, commit `f4f5edd` (`command: git -C ~/MyProjects/bc-docs rev-parse --short origin/main -> f4f5edd`; the commit is dated 2026-11-11). Every file was read with `git show origin/main:<path>`. The copy of bc-docs on disk was not read.
- The seven reading reports in `barecount-devhub:artifacts/spine-review/` (`DOCS-1`, `DOCS-2A`, `DOCS-2B`, `DOCS-3A`, `DOCS-3B`, `DOCS-4`, `DOCS-5`), all dated 2026-11-13. They are working files in the DevHub working directory and are not at a commit.
- The function codes and names of the table under "The functional map" in the main document.

## What this annex covers

**bc-docs** is the repository that holds the written description of the BareCount platform. Its own chapter on the documentation system says: "Per `DEC-3395bc`, bc-docs is the documentation source of truth. Filesystem layout plus YAML frontmatter authority is the discipline; nothing else is consulted as the authoritative content." (`bc-docs:docs/development/documentation-system.md:37 @ f4f5edd`).

A **chapter** here means one markdown file under one of ten folders of `docs/`: `overview`, `foundation`, `operating-model`, `implementation`, `ai`, `development`, `onboarding`, `operations`, `compliance` and `archive`. There are 131 such files at `origin/main`.

**Frontmatter** is the short block of labelled fields at the top of a markdown file, between two lines of three dashes. Two of its fields matter here.

- **authority** says what kind of statement the file makes. The documentation system chapter gives four values: "`authoritative` (the file is where a rule, structure or procedure is declared), `reference` (the file describes, indexes or projects something whose authority lives elsewhere), `evidentiary` (the file records what happened and is not edited after it is finalised) or `generated` (a generator emitted the file from a named source at a named commit; it is regenerated, never edited by hand)" (`bc-docs:docs/development/documentation-system.md:43 @ f4f5edd`).
- **status** says where the file is in its life. For chapters the same chapter lists five values: "chapters and reference notes `drafting`, `reviewing`, `locked`, `superseded`, `retired`" (`bc-docs:docs/development/documentation-system.md:44 @ f4f5edd`).

The two fields together decide whether a chapter binds a builder. The rule is: "Binding force requires `authority: authoritative` plus `status: locked`." (`bc-docs:docs/development/documentation-system.md:44 @ f4f5edd`). The platform overview states the same rule: "Binding force equals `authority == authoritative` and `status == locked`. Any other combination is non-binding." (`bc-docs:docs/overview/platform-overview.md:107 @ f4f5edd`). The summary below shows that no chapter in the ten folders has `status: locked`.

## The four chapter verdicts

Each chapter gets exactly one chapter verdict.

| Chapter verdict | Meaning |
|---|---|
| keep nearly as is | The chapter is accurate enough to go into the new developer guide after the small fixes its reading report names. |
| rewrite | The subject belongs in the guide, but the text is stale, wrong or incomplete and must be written again, usually from the code. |
| history | The chapter records something finished, retired or overtaken. It is kept as a dated record and is not guidance. |
| designed, not built — keep as such | The chapter describes a design that the platform does not yet have. It is kept, and labelled as a design. |

**Where the verdicts come from.** Seven reading reports each read one or two folders in full and judged every chapter. This annex takes each verdict from the report that read the chapter and cites the report file and its section. The reports use their own words. They are mapped to the four verdicts as follows.

| Chapter verdict | Report wording mapped to it |
|---|---|
| keep nearly as is | "Could go in nearly as they are" (DOCS-1 §6.2); "Guide-ready" and "Nearly as-is" (DOCS-2A §6); "as-is" (DOCS-2B §6); "Could seed the developer guide" (DOCS-3A §7.1, when it applies to the whole chapter); "Keep" (DOCS-3B §7); "Seed nearly as-is" and "Seed with edits" (DOCS-4 §7.1); "Guide-ready" and its variants (DOCS-5 §9.1, §9.3, §9.4) |
| rewrite | "Need a rewrite" (DOCS-1 §6.2); "Rewrite", also "small", "light" or "lightly" (DOCS-2A, DOCS-2B, DOCS-5); "Needs a rewrite from code" (DOCS-3A §7.2); "Rewrite from code" (DOCS-3B §7, DOCS-4 §7.1); "Needs rewrite" (DOCS-5 §9.3, §9.4); "Split: keep the method, rewrite the mechanics" (DOCS-4 §7.1) |
| history | "Should become history" (DOCS-1 §6.2, DOCS-3A §7.3); "History" (DOCS-2A, DOCS-2B, DOCS-3B, DOCS-4, DOCS-5 §9.1); "History-only" (DOCS-5 §9.3, §9.4) |
| designed, not built — keep as such | "Guide as \"designed, not built\"" (DOCS-2A §6); "Designed-not-built entry" (DOCS-2B §6) |

Three mapping rules were applied by this annex and are not the reports' own.

1. **Split verdicts.** Several reports judge parts of one chapter differently. The row then carries the verdict for the larger part as the report describes it, and the reason begins "Split verdict" and names the other part. These rows are listed again after the tables.
2. **A light rewrite is still a rewrite.** "Rewrite (light)", "Rewrite, small" and "Rewrite, lightly" are all mapped to "rewrite".
3. **Four judgement calls.** `development/lessons-platform-readiness-umbrella.md` is "Guide-ready as history" in DOCS-5 §9.1 and is mapped to "keep nearly as is", because the text is kept unchanged. `operating-model/quality-gates-and-chain-integrity.md` is "Rewrite or history." in DOCS-2B §6 and is mapped to "rewrite", because DOCS-2B §6a lists it under rewrite. `implementation/tenant-onboarding.md` is "Best seed for the tenancy chapter." in DOCS-3B §7 with grade C+ in DOCS-3B §5, and is mapped to "rewrite", because the report says its mechanism must be updated. `implementation/metric-catalog-and-source-reference.md` is kept in part and moved to history in part by DOCS-3B §7, and is mapped to "rewrite".

## How the tables were built

- **The file list.** `command: git -C ~/MyProjects/bc-docs ls-tree -r --name-only origin/main -- docs/overview docs/foundation docs/operating-model docs/implementation docs/ai docs/development docs/onboarding docs/operations docs/compliance docs/archive | grep '\.md$' | wc -l -> 131`.
- **Title, authority, status.** A script ran `git -C ~/MyProjects/bc-docs show origin/main:<path>` for each file and read the `title`, `authority` and `status` fields from the frontmatter. Where a field is not present the cell says "absent". Each value can be re-read at `bc-docs:<path>` frontmatter `@ f4f5edd`.
- **Last commit date.** `command: git -C ~/MyProjects/bc-docs log -1 --format=%cs origin/main -- <path>`, once per file. A late date does not prove a late revision of the content. For example, the last commit to `docs/ai/ai-agents.md` is a frontmatter correction (`command: git -C ~/MyProjects/bc-docs log -1 --format='%h %cs %s' origin/main -- docs/ai/ai-agents.md -> 36347fa 2026-10-01 docs: round 2 — restore bidirectional frontmatter parity for DEC-3395bc; three wording fixes (TSK-b143b2)`).
- **Chapter verdict and reason.** Taken from the reading report cited in the row. The report's own wording is given in double quotes. The reasons are the reports' findings. This annex did not re-check them against code or data; it re-opened each cited report section and nothing more.
- **Function.** The function code and name, from the table under "The functional map" in the main document, that the chapter mainly belongs to. A function is one named area of responsibility in the platform, such as "L5, Canonical Contracts". A second code after "also" is given by code alone; its name is in that table. Chapters that describe the platform as a whole are marked "the frame (no single function)". One chapter describes only retired services and is marked "the retirement list (no function)". The assignment of a chapter to a function is this annex's own reading of the chapter's subject. No report assigns chapters to these codes.

In each table the path is given inside its folder. The full path is `docs/<folder>/<path>`.

## docs/overview (5 files)

| path | title | authority | status | last commit date | chapter verdict | function | reason and source |
|---|---|---|---|---|---|---|---|
| `audited-metrics-differentiator.md` | Audited Metrics Differentiator | reference | drafting | 2026-10-01 | rewrite | the frame (no single function) | Its banner contradicts its body; the report says to rewrite the body to the banner or retire the chapter, and to keep the product-role and claim-control sections. Report wording: "Need a rewrite" (DOCS-1 §6.2). |
| `platform-db-foundation.md` | Platform DB Foundation Program | authoritative | implemented | 2026-09-21 | history | OP, Operations (schema change and database ownership) | A closure record of a finished program with a 2026-09-21 snapshot. Split verdict: the report lists its database-ownership model under "Could go in nearly as they are". Report wording: "Should become history" (DOCS-1 §6.2). |
| `platform-overview.md` | Platform Overview | authoritative | drafting | 2026-10-01 | rewrite | the frame (no single function) | Mostly about the documentation, not the platform; its chapter inventory is out of date. The report says to split it into a frame chapter and documentation rules. Report wording: "Need a rewrite" (DOCS-1 §6.2). |
| `platform-readiness.md` | Platform Readiness & Legibility — Overview | absent | closed | 2026-09-26 | history | DV, Development (a closed program record; also the frame, because it holds the function list) | Status record of a closed program. The report says to lift its function list into the functional map first. Report wording: "Should become history" (DOCS-1 §6.2). |
| `structural-differentiators.md` | Structural Differentiators | reference | drafting | 2026-10-01 | history | the frame (no single function) | Proof paragraphs and gap list are dated 2026-07-06 and carry fixed counts. Split verdict: nine rationale paragraphs can be kept beside the invariants. Report wording: "Should become history" (DOCS-1 §6.2). |

## docs/foundation (10 files)

| path | title | authority | status | last commit date | chapter verdict | function | reason and source |
|---|---|---|---|---|---|---|---|
| `foundation-overview.md` | Foundation: Overview | authoritative | drafting | 2026-10-01 | rewrite | the frame (no single function) | Says Foundation is locked while its frontmatter says drafting; counts of sections disagree inside the chapter. The report wants a one-page opener. Report wording: "Need a rewrite" (DOCS-1 §6.2). |
| `the-authority-model.md` | The Authority Model | authoritative | drafting | 2026-09-30 | keep nearly as is | the frame (no single function); also DV | The authority ladder is usable as written; frontmatter is behind the body. The decision-record mechanics move to the development chapter. Report wording: "Could go in nearly as they are" (DOCS-1 §6.2). |
| `the-contract-grammar.md` | The Contract Grammar | authoritative | drafting | 2026-08-22 | rewrite | the frame (no single function); also L2, L4, L5, L6 | Reported as self-contradictory and the Foundation chapter most in need of a rewrite: current grammar and retired grammar are mixed. Report wording: "Need a rewrite" (DOCS-1 §6.2). |
| `the-dual-layer-interaction-model.md` | The Dual-Layer Interaction Model | authoritative | drafting | 2026-07-06 | keep nearly as is | the frame (no single function); also AI | Clear as a rule. Condition: "the governed authoring path" must be defined and "panel" given one meaning first. Report wording: "Could go in nearly as they are" (DOCS-1 §6.2). |
| `the-evaluation-boundaries.md` | The Evaluation Boundaries | authoritative | drafting | 2026-07-06 | rewrite | the frame (no single function); also RT | Split verdict: the canonical section uses retired vocabulary and needs a rewrite; the inventory table, the six rules and the read-access table are listed under "Could go in nearly as they are". Report wording: "Need a rewrite" (DOCS-1 §6.2). |
| `the-governed-selection.md` | The Governed Selection | authoritative | drafting | 2026-10-02 | keep nearly as is | the frame (no single function); also RT | The most recent Foundation chapter (2026-10-02) and internally consistent apart from one wording conflict on evidence and lineage. Report wording: "Could go in nearly as they are" (DOCS-1 §6.2). |
| `the-invariants.md` | The Invariants | authoritative | drafting | 2026-09-30 | keep nearly as is | the frame (no single function) | Reported as the firmest chapter. Two fixes named: the ordering test for secondary snapshots and references to an older structure. Report wording: "Could go in nearly as they are" (DOCS-1 §6.2). |
| `the-object-model.md` | The Object Model | authoritative | drafting | 2026-09-30 | rewrite | the frame (no single function); also RT, A1 | Ambiguous in four places and contradicted by the build on actions; the Action Object must be marked as designed, not built. Report wording: "Need a rewrite" (DOCS-1 §6.2). |
| `the-problem.md` | The Problem | authoritative | drafting | 2026-07-06 | keep nearly as is | the frame (no single function) | Clear; no contradiction found. Usable with The Solution as a short preface. Report wording: "Could go in nearly as they are" (DOCS-1 §6.2). |
| `the-solution.md` | The Solution | authoritative | drafting | 2026-07-06 | keep nearly as is | the frame (no single function) | Clear; one stale table (the "three-rung authority ladder" line) to fix. Report wording: "Could go in nearly as they are" (DOCS-1 §6.2). |

## docs/operating-model (26 files)

| path | title | authority | status | last commit date | chapter verdict | function | reason and source |
|---|---|---|---|---|---|---|---|
| `action-evaluation.md` | Action Evaluation | authoritative | drafting | 2026-08-19 | designed, not built — keep as such | A1, Action and intervention | Clear prose and honest that the implementation is absent; four conflicts with other chapters need a ruling first. Report wording: "Guide as "designed, not built"" (DOCS-2A §6). |
| `admission-and-observation.md` | Admission and Observation | authoritative | drafting | 2026-08-19 | keep nearly as is | RT, Runtime; also L2 | The admission path it describes matches the code review; it lacks an as-built section and the route that starts an admission. Report wording: "Guide-ready as the doctrine section" (DOCS-2A §6). |
| `business-vocabulary.md` | Business Vocabulary | authoritative | drafting | 2026-09-07 | rewrite | L3, Vocabulary | The model is sound; the state names are inconsistent and the chapter gives no route, table or act for authoring. Report wording: "Rewrite, small" (DOCS-2A §6). |
| `canonical-evaluation.md` | Canonical Evaluation | authoritative | drafting | 2026-09-08 | rewrite | RT, Runtime; also L5 | Six of nine application steps describe contract keys the engine does not read. DISAGREEMENT: DOCS-2A §6 records that REVIEW-5 listed this chapter as "good enough to keep nearly as is". Report wording: "Rewrite" (DOCS-2A §6). |
| `chain-completeness-and-verdict.md` | Chain Completeness and Verdict | authoritative | drafting | 2026-10-02 | history | L9, Chain integrity | Declared historical by its own banner; refers to a dropped table. Two ideas are to be carried forward by ruling. Report wording: "History" (DOCS-2A §6). |
| `connectors-and-readers.md` | Connectors and Readers | authoritative | drafting | 2026-08-19 | keep nearly as is | L7, Readers and connections | Mostly matches the code and carries its own as-built notes; the unbuilt Connection features move to "designed, not built". Report wording: "Guide-ready as the inventory" (DOCS-2A §6). |
| `contract-chain-assembly.md` | Contract Chain Assembly | authoritative | drafting | 2026-09-08 | rewrite | L9, Chain integrity; also L2, L4, L5, L6 | The six-link table and the integrity rules are worth keeping; the rest is written in retired vocabulary. Report wording: "Rewrite" (DOCS-2A §6). |
| `evidence-and-lineage.md` | Evidence and Lineage | authoritative | drafting | 2026-09-27 | keep nearly as is | EV, Evidence and lineage | Reported as the best chapter of its half. Needs one conflict with Foundation ruled and a paragraph on planes. Report wording: "Guide-ready" (DOCS-2A §6). |
| `finance-core-vocabulary-manifest.md` | Finance-core BCF Vocabulary Manifest + Dedup (gap sizing) | authoritative | drafting | 2026-10-01 | history | L3, Vocabulary | A session record with identifiers, counts and dated passes; five lessons are to be lifted into the vocabulary chapter. Report wording: "History" (DOCS-2A §6). |
| `fiscal-time-and-temporal-gates.md` | Fiscal Time and Temporal Gates | authoritative | drafting | 2026-07-07 | keep nearly as is | RT, Runtime; also MD | Clear and matches the code where checked; two internal conflicts and the title need fixing. Report wording: "Guide-ready" (DOCS-2A §6). |
| `gl-vocabulary-enrichment-design.md` | GL Vocabulary Enrichment — design (Metric Directory GL gaps) | authoritative | drafting | 2026-10-01 | history | L3, Vocabulary; also L8 | A proposal overtaken by the finance-core manifest; one retry rule and one sentence on the authoring path are worth keeping. Report wording: "History" (DOCS-2A §6). |
| `mcf-legacy-bridge.md` | MCF Legacy Bridge — Read-Fallback Policy + Sunset Semantics | absent | retired | 2026-10-01 | history | L6, Metric Contracts and certification | Already marked retired in its frontmatter, and the report confirms that is correct. Report wording: "History" (DOCS-2A §6). |
| `metric-catalog.md` | Metric Catalog | authoritative | drafting | 2026-07-06 | history | L6, Metric Contracts and certification; also L8 | Describes a metric definition model whose corpus was dropped; no as-built note. Three ideas are to be re-decided. Report wording: "History" (DOCS-2A §6). |
| `metric-directory.md` | The Metric Directory | authoritative | drafting | 2026-10-01 | rewrite | L8, Metric Directory | Says it is unbuilt, yet a directory exists in code. Split verdict: sections 2 to 8 can go in nearly as they are; sections 1, 11 and 12 must be replaced. Report wording: "Rewrite, lightly." (DOCS-2B §6). |
| `metric-evaluation.md` | Metric Evaluation | authoritative | drafting | 2026-10-02 | rewrite | RT, Runtime; also L6 | Reported as the most honest chapter read; it contradicts itself on snapshots per act and conflicts with Foundation Invariant VI by its own account. Report wording: "Rewrite on a sound base." (DOCS-2B §6). |
| `metric-lifecycle.md` | The Metric Lifecycle — Companion | reference | absent | 2026-10-01 | rewrite | L6, Metric Contracts and certification | The only place the seven states are explained; three sections need correction against the code. Split verdict: sections 3 and 9 become history. Report wording: "Rewrite, as the base of the F7 chapter." (DOCS-2B §6). |
| `metric-management-system-recovery-track.md` | Metric Management System — Recovery Track | authoritative | drafting | 2026-07-06 | history | L6, Metric Contracts and certification | Built on a state model that was replaced; its ledger table and service do not exist. One extract (the R1 to R8 vocabulary) may be kept. Report wording: "History" (DOCS-2B §6). |
| `metric-management-system.md` | Metric Management System | authoritative | drafting | 2026-07-07 | history | L6, Metric Contracts and certification | A June design that was partly overtaken; its five-state lifecycle with direct activation was closed. Report wording: "History." (DOCS-2B §6). |
| `operating-model-overview.md` | Operating Model: Overview | authoritative | drafting | 2026-10-01 | rewrite | the frame (no single function) | Its chapter map omits six files of its own folder. Split verdict: its six claims and seven constraints can be lifted nearly as they are. Report wording: "Rewrite." (DOCS-2B §6). |
| `quality-gates-and-chain-integrity.md` | Quality Gates and Chain Integrity | authoritative | drafting | 2026-07-06 | rewrite | L9, Chain integrity; also L3, AI | Describes one gate mechanism that no code review found in that form. The report gives two verdicts in §6 and lists it under rewrite ("principles only") in §6a. Report wording: "Rewrite or history." (DOCS-2B §6 and §6a). |
| `source-change-classification.md` | Source Change Classification and Version-Bump Policy | authoritative | drafting | 2026-09-30 | rewrite | L2, Source and Admission Contracts; also L1, L4, L5 | The three-kind classification and bump tables are useful as a policy proposal; the cascade sections describe machinery that is not built. Report wording: "Rewrite." (DOCS-2B §6). |
| `sources-and-the-catalog.md` | Sources and the Catalog | authoritative | drafting | 2026-07-06 | keep nearly as is | L1, Source Catalog | Reported as "Closest to guide-ready in this half"; two enforcement gaps and the missing registration procedure are named. Report wording: "As-is for the model, plus a new procedure section." (DOCS-2B §6). |
| `tenancy-and-binding.md` | Tenancy and Binding | authoritative | drafting | 2026-10-12 | rewrite | DL, Delivery to a tenant; also S3, L10 | Wrong on where a Connection is held and on adoption by binding; assignee and retention are to be marked designed, not built. Report wording: "Rewrite." (DOCS-2B §6). |
| `tenant-entitlement-enforcement.md` | Tenant Entitlement Enforcement | authoritative | drafting | 2026-07-06 | designed, not built — keep as such | S4, Pricing and subscription; also DL | Entirely unbuilt by its own account; its wiring-status table is reported as a model of how to state an unbuilt design. Report wording: "Designed-not-built entry, nearly as-is." (DOCS-2B §6). |
| `tenant-extensions-and-overrides.md` | Tenant Extensions and Overrides | authoritative | drafting | 2026-07-06 | designed, not built — keep as such | DL, Delivery to a tenant; also S3 | Consistent within itself, with no as-built statement; to be held as the specification of tenant variation, not as current behaviour. Report wording: "Designed-not-built entry after a terminology pass." (DOCS-2B §6). |
| `the-runtime-ecosystem.md` | The Runtime Ecosystem | authoritative | drafting | 2026-08-19 | keep nearly as is | RT, Runtime | Clear and short; one statement about secondary snapshots conflicts with the metric evaluation chapter. Report wording: "As-is as a glossary page, after fixing RE:50." (DOCS-2B §6). |

## docs/implementation (29 files)

| path | title | authority | status | last commit date | chapter verdict | function | reason and source |
|---|---|---|---|---|---|---|---|
| `api-surface.md` | API Surface | authoritative | drafting | 2026-10-01 | keep nearly as is | S1, Authentication; also S2 | Graded B+: the guard chain, tenant-route table and error format are accurate. Two corrections are named. Report wording: "Could seed the developer guide" (DOCS-3A §7.1 and §5.1). |
| `architecture.md` | Architecture | authoritative | drafting | 2026-10-01 | rewrite | the frame (no single function) | Split verdict: the commitments, surfaces and end-to-end path sections can seed the guide; the composition, port and evolution sections become history. Report wording: "grade D for composition, sound as concept" (DOCS-3A §7.1, §7.3 and §5.2). |
| `audit-and-activity-logging.md` | Audit and Activity Logging | authoritative | drafting | 2026-10-01 | rewrite | DV, Development; also EV, S2 | Half the chapter describes retired services. Split verdict: the two-logging-surfaces and change-record sections can seed the guide. Report wording: "Needs a rewrite from code" (DOCS-3A §7.2). |
| `auxiliary-services.md` | Auxiliary Services | authoritative | drafting | 2026-10-01 | history | the retirement list (no function) | All three services it describes are retired, archived or renamed. Report wording: "Should become history" (DOCS-3A §7.3). |
| `backend-services.md` | Backend Services | authoritative | drafting | 2026-10-01 | rewrite | OP, Operations; also DV | Start commands, supervisor, AI dependency, database port and host paths are behind. Split verdict: the database-tool section is accurate. Report wording: "Needs a rewrite from code" (DOCS-3A §7.2). |
| `business-concept-registry.md` | The BareCount Business Concept Registry | absent | accepted | 2026-07-06 | keep nearly as is | L3, Vocabulary | Reported as the clearest chapter of its half; it needs standard frontmatter and two corrections. Report wording: "Could seed the developer guide" (DOCS-3A §7.1). |
| `data-model-and-schema.md` | Data Model and Schema | authoritative | drafting | 2026-10-01 | rewrite | OP, Operations; also MD | Seven schemas are missing and the schema-change path is superseded. Split verdict: the ten rules and the naming table can seed the guide. Report wording: "Needs a rewrite from code" (DOCS-3A §7.2). |
| `demo-estate-max-coverage-rescope.md` | Demo-Estate Max-Coverage Re-scope — bc-demo v2.1 build reoriented to widest metric horizon | reference | approved | 2026-10-01 | history | PV, Proof against the source (the demo source world) | A record of the August 2026 bc-demo v2.1 program; paths no longer resolve and status lines contradict the frontmatter. Report wording: "Should become history" (DOCS-3A §7.3). |
| `demo-estate-metric-coverage.md` | Demo-Estate Metric Coverage — finance deep, adjacent worlds one layer thick (coverage → metrics) | reference | approved | 2026-10-01 | history | PV, Proof against the source (the demo source world) | A record of the August 2026 bc-demo v2.1 program; paths no longer resolve and status lines contradict the frontmatter. Report wording: "Should become history" (DOCS-3A §7.3). |
| `demo-estate-module-coverage.md` | Demo-Estate Module Coverage — Odoo apps/modules exercised, mapped to metric functions | reference | approved | 2026-10-01 | history | PV, Proof against the source (the demo source world) | A record of the August 2026 bc-demo v2.1 program; paths no longer resolve and status lines contradict the frontmatter. Report wording: "Should become history" (DOCS-3A §7.3). |
| `demo-estate-program-status.md` | Demo-Estate Simulator — bc-demo v2.1 program status (as-built current state) | reference | approved | 2026-10-01 | history | PV, Proof against the source (the demo source world) | A record of the August 2026 bc-demo v2.1 program; paths no longer resolve and status lines contradict the frontmatter. Report wording: "Should become history" (DOCS-3A §7.3). |
| `demo-estate-simulator-requirements.md` | Demo-Estate Simulator (bc-demo v2) — Requirements & Disposition Registers | authoritative | approved | 2026-09-30 | history | PV, Proof against the source (the demo source world) | To be kept as the bc-demo product's own requirements record, moved out of platform Implementation; two ideas are reusable. Report wording: "Should become history" (DOCS-3A §7.3). |
| `frontend-experience.md` | Frontend Experience | authoritative | drafting | 2026-10-01 | rewrite | S5, Operator console; also TS | The chapter calls itself a stub and lacks the screen inventory. Split verdict: the tenant-route and tenant-context sections can seed the guide. Report wording: "Needs a rewrite from code" (DOCS-3A §7.1 and §7.2). |
| `implementation-overview.md` | Implementation: Overview | authoritative | drafting | 2026-10-01 | rewrite | the frame (no single function) | The chapter count, the group table and the "locked" statements are wrong; the folder has 29 files of five kinds. Report wording: "Needs a rewrite from code" (DOCS-3A §7.2). |
| `infrastructure.md` | Infrastructure | authoritative | drafting | 2026-10-01 | rewrite | OP, Operations | Repository name, stack list, containers, tenant provisioning and secrets are all behind; its four-way frame is worth keeping. Report wording: "Needs a rewrite from code" (DOCS-3A §7.2). |
| `internal-modules.md` | Internal Modules | authoritative | drafting | 2026-10-01 | rewrite | the frame (no single function) | The module catalogue should be generated from code; only the cluster idea and six cross-module patterns are kept as prose. Report wording: "Rewrite from code." (DOCS-3B §7). |
| `metric-catalog-and-source-reference.md` | Metric Catalog, Chain-on-Demand & the Source-Reference Layer | authoritative | drafting | 2026-07-07 | rewrite | L8, Metric Directory; also L1, L6 | Split verdict: sections 1 to 3 are kept after reconciling; sections 4 and 5 become history. Report wording: "Keep §1–§3, reconcile tiers to the MLS ladder and lanes; move §4–§5 to history." (DOCS-3B §7). |
| `notifications-and-webhooks.md` | Notifications and Webhooks | authoritative | drafting | 2026-10-01 | rewrite | NT, Notifications and webhooks | Its "Nothing is wired" section is wrong: an event outbox, a webhook registry and deliveries exist. Nine invariants are worth keeping. Report wording: "Rewrite from code." (DOCS-3B §7). |
| `platform-db-foundation-requirements.md` | Platform DB Foundation — Requirements and Technical Design | authoritative | implemented | 2026-09-21 | history | OP, Operations | A requirements record; named requirements are to be extracted into the guide with a built or designed mark each. Report wording: "History, with rules lifted out." (DOCS-3B §7). |
| `platform-readiness-evidence-2026-09-19.md` | Platform Readiness — Evidence Manifest (2026-09-19 grounding) | absent | evidence | 2026-09-20 | history | DV, Development (a program record) | A dated evidence manifest; the report says it should sit under docs/evidence. Report wording: "History." (DOCS-3B §7). |
| `platform-readiness-program.md` | Platform Readiness & Legibility — Program (SSOT) | absent | closed | 2026-09-21 | history | DV, Development (a closed program record; also the frame, because its section 2 is the function list) | A closed program. Its section 2 is reported as the best seed for the functional map. Report wording: "History, with §2 lifted and completed" (DOCS-3B §7). |
| `source-variability-and-field-provenance.md` | Source Variability and Field Provenance | reference | drafting | 2026-10-01 | keep nearly as is | L1, Source Catalog; also L2, L4 | Usable nearly as it is; two mechanics need correcting and one feature is to be marked designed, not built. Report wording: "Keep; fix two mechanics" (DOCS-3B §7). |
| `structural-integrity-packages/SI-B-1-doctrine-without-adr.md` | SI-B-1 — Doctrine-without-ADR (backfill the missing decision records) | absent | reviewing | 2026-10-01 | history | DV, Development | An executed design package. Report wording: "History" (DOCS-3B §7). |
| `structural-integrity-packages/SI-D-1-doc-number-reconciliation.md` | SI-D-1 — Point docs at the source; never freeze a stat | absent | reviewing | 2026-10-01 | history | DV, Development | An executed design package; only its rule (point documents at the source, never fix a count in text) carries forward. Report wording: "History; the rule becomes a guard" (DOCS-3B §7). |
| `structural-integrity-packages/doc-integrity-register.md` | Structural Integrity — Document Integrity Register | absent | living | 2026-09-21 | history | DV, Development | A register; the report offers reviving it as the retirement list each chapter must carry. Report wording: "History" (DOCS-3B §7). |
| `structural-integrity-program.md` | Structural Integrity — Program (SSOT) | absent | drafting | 2026-09-21 | history | DV, Development | A program document; its method section and one route rule feed the audit step of each function. Report wording: "History." (DOCS-3B §7). |
| `synthetic-data-and-testing.md` | Synthetic Data and Testing | authoritative | drafting | 2026-10-01 | rewrite | DV, Development; also PV | Sections on a retired data generator become history; its claims about CI and test counts are wrong. Report wording: "Rewrite from code." (DOCS-3B §7 and §5 (grade F)). |
| `tenant-onboarding.md` | Tenant Onboarding and Provisioning | authoritative | drafting | 2026-09-15 | rewrite | S3, Tenant lifecycle and management; also L10 | The two-boundary model, three lifecycles and hand-off contract are sound; the mechanism is out of date and each need must be marked built or not built. Report wording: "Best seed for the tenancy chapter." (DOCS-3B §7 and §5 (grade C+)). |
| `tenant-readiness-program.md` | Tenant Readiness — Program (SSOT) | absent | drafting | 2026-09-28 | history | L10, Tenant onboarding; also S3, L7, RT | A dated program log. Its section 2 ladder is reported as the best existing end-to-end list of hand-offs. Report wording: "History for §3 and §8; lift §2." (DOCS-3B §7). |

## docs/ai (7 files)

| path | title | authority | status | last commit date | chapter verdict | function | reason and source |
|---|---|---|---|---|---|---|---|
| `ai-agents.md` | AI Agents | authoritative | drafting | 2026-10-01 | history | AI, AI services | An inventory of idle and retired agents; it omits the one path that was in use. Report wording: "history-only" (DOCS-5 §9.4 G). |
| `ai-architecture.md` | AI Architecture | authoritative | drafting | 2026-10-01 | history | AI, AI services | Describes a retired Python service; nothing about the panels that run inside bc-core. Report wording: "history-only" (DOCS-5 §9.4 G). |
| `ai-gates.md` | AI Gates | authoritative | drafting | 2026-10-01 | history | AI, AI services; also L6 | Its central gate reads a table the chapter itself marks retired; it contradicts a later decision on the role of panels. Report wording: "history-only" (DOCS-5 §9.4 G). |
| `ai-overview.md` | AI: Overview | authoritative | drafting | 2026-10-01 | history | AI, AI services | Defines the whole section as the retired service. Two principles are worth keeping. Report wording: "history-only" (DOCS-5 §9.4 G). |
| `ai-trust-and-verification.md` | AI Trust and Verification | authoritative | drafting | 2026-10-01 | history | AI, AI services | The mechanics are retired; one principle and the idea of an explicit trust level are worth carrying into a new chapter. Report wording: "history-only, with salvage" (DOCS-5 §9.4 G). |
| `ai-usage-visibility.md` | AI Usage Visibility | authoritative | drafting | 2026-10-01 | rewrite | AI, AI services; also TS | Its list of what a tenant cannot see is still true and is the only requirements statement on that subject; the built parts depend on the retired service. Report wording: "needs rewrite" (DOCS-5 §9.4 G). |
| `bedrock-and-inference-profiles.md` | Bedrock and Inference Profiles | authoritative | drafting | 2026-10-01 | history | AI, AI services | Describes the retired service's clients and a vendor interface the current code does not use. Report wording: "history-only" (DOCS-5 §9.4 G). |

## docs/development (12 files)

| path | title | authority | status | last commit date | chapter verdict | function | reason and source |
|---|---|---|---|---|---|---|---|
| `build-and-release.md` | Build and Release | authoritative | drafting | 2026-10-01 | rewrite | DV, Development; also OP | Its schema claim contradicts the current schema-change path and it names retired services; two points survive. Report wording: "Rewrite" (DOCS-5 §9.1). |
| `continuous-integration.md` | Continuous Integration and CI Runners | authoritative | drafting | 2026-09-30 | keep nearly as is | DV, Development | Accurate for 2026-09-30 and candid about limits; the required-checks table and a token renewal date need a re-read. Report wording: "Guide-ready" (DOCS-5 §9.1). |
| `decision-and-change-procedure.md` | Decision and Change Procedure | authoritative | drafting | 2026-10-02 | rewrite | DV, Development | The decision-record and change-record rules are sound and current; one section describes a gate that no longer exists. Report wording: "Rewrite (light)" (DOCS-5 §9.1). |
| `dev-workstation-mac-mini.md` | Development Workstation: Mac Mini and Laptop | authoritative | drafting | 2026-09-29 | rewrite | DV, Development; also OP | A good runbook frozen at 2026-09-25 to 29; two sections contradict later sections and the project instructions. Report wording: "Rewrite (light)" (DOCS-5 §9.1). |
| `developer-experience.md` | Developer Experience | authoritative | drafting | 2026-10-01 | rewrite | DV, Development | Stale on procedure location, AWS profile, tools, schema path, retired repositories and Windows paths. Report wording: "Rewrite" (DOCS-5 §9.1). |
| `development-overview.md` | Development: Overview | authoritative | drafting | 2026-10-01 | rewrite | DV, Development | Gives two different chapter counts; three of nine constraints are reported false. Report wording: "Rewrite" (DOCS-5 §9.1). |
| `devhub.md` | DevHub | authoritative | drafting | 2026-10-01 | rewrite | DV, Development | Tool and table counts, the close gate, the start command and the scanners are stale; two sections are worth keeping. Report wording: "Rewrite" (DOCS-5 §9.1). |
| `documentation-system.md` | Documentation System | authoritative | drafting | 2026-10-02 | rewrite | DV, Development | The two-axis frontmatter rule and the reader path are current; paths are stale and no rule says who reads and who corrects. Report wording: "Rewrite (light)" (DOCS-5 §9.1). |
| `lessons-platform-readiness-umbrella.md` | Lessons: Platform Readiness umbrella (2026-09-25 to 27) | reference | drafting | 2026-10-01 | keep nearly as is | DV, Development | Short, dated and true; it is kept as it is, as a dated record of lessons. Four lessons are the refactor program's own method. Report wording: "Guide-ready as history" (DOCS-5 §9.1). |
| `metric-readiness-toolkit.md` | Metric Readiness Toolkit | authoritative | drafting | 2026-09-06 | history | L6, Metric Contracts and certification; also DV | Written before the current metric framework; two of three wrappers it describes are gone. Report wording: "History" (DOCS-5 §9.1). |
| `quality-assurance.md` | Quality Assurance | authoritative | drafting | 2026-10-01 | keep nearly as is | DV, Development | Reported as the model chapter of its folder: every claim is tied to a file and line. TENSION inside DOCS-5: §1.12 lists it as "Stale" from the controller charters. Report wording: "Guide-ready" (DOCS-5 §9.1). |
| `the-controller-operating-model.md` | The Controller Operating Model | authoritative | drafting | 2026-10-01 | history | DV, Development | Describes a fleet that was mostly unbuilt and is now parked; its verification remarks should be harvested before it is retired. Report wording: "History" (DOCS-5 §9.1). |

## docs/onboarding (13 files)

| path | title | authority | status | last commit date | chapter verdict | function | reason and source |
|---|---|---|---|---|---|---|---|
| `business-field-and-business-object-onboarding.md` | Business Concept Authoring (BCF) | authoritative | drafting | 2026-09-07 | keep nearly as is | L3, Vocabulary | Chain and routes are correct. Edits named: rename the file, delete one claim about legacy tables, add the operator routes and a check query. Report wording: "Seed with edits" (DOCS-4 §7.1). |
| `canonical-contract-creation.md` | Canonical Contract Creation | authoritative | drafting | 2026-10-01 | rewrite | L5, Canonical Contracts | Teaches the first contract grammar, not the one the code enforces; the grain discussion should be restated. Report wording: "Rewrite from code" (DOCS-4 §7.1). |
| `canonical-field-seeding.md` | Canonical Field Seeding | authoritative | drafting | 2026-10-02 | history | L3, Vocabulary | Its subject no longer exists. One idea survives: author only what a metric needs. Report wording: "History" (DOCS-4 §7.1). |
| `metric-workstream.md` | Metric Workstream Playbook | reference | drafting | 2026-10-01 | rewrite | L6, Metric Contracts and certification | Split verdict: the work types, the Foundation gate and the anti-patterns are kept; every table name, route and checklist is rewritten. Report wording: "Split: keep the method, rewrite the mechanics" (DOCS-4 §7.1). |
| `multi-standard-onboarding.md` | Multi-Standard Onboarding | authoritative | drafting | 2026-10-01 | history | L3, Vocabulary; also L5 | Its subject no longer exists; the overlap-detection idea is now structural in the registry. Report wording: "History" (DOCS-4 §7.1). |
| `observation-contract-creation.md` | Observation Contract Creation | authoritative | drafting | 2026-10-01 | rewrite | L4, Observation Contracts | Teaches the first contract grammar; the sign-indicator section and one disposition table are kept as design content. Report wording: "Rewrite from code" (DOCS-4 §7.1). |
| `onboarding-overview.md` | Onboarding: Overview | authoritative | drafting | 2026-10-01 | history | the frame (no single function); spans L1 to L10 | Its chapter map is wrong and it gives no order of work. Report wording: "History; replace" (DOCS-4 §7.1). |
| `reader-creation.md` | Reader Creation | authoritative | drafting | 2026-10-01 | keep nearly as is | L7, Readers and connections | Routes, bodies, error codes, gates and known gaps all match the code. Report wording: "Seed nearly as-is" (DOCS-4 §7.1). |
| `seed-catalog-management.md` | Seed Catalog Management | authoritative | drafting | 2026-10-01 | history | L1, Source Catalog | The chapter says itself that it is history. Report wording: "History" (DOCS-4 §7.1). |
| `source-and-admission-contract-creation.md` | Source and Admission Contract Creation | authoritative | drafting | 2026-10-02 | rewrite | L2, Source and Admission Contracts | One section (registering a source stack) is the real procedure; steps 1 to 6 and the naming section are history. Report wording: "Rewrite from code; keep one section" (DOCS-4 §7.1). |
| `source-registration.md` | Source Registration | authoritative | drafting | 2026-10-01 | rewrite | L1, Source Catalog | The current procedure (admit, verify, approve) exists in code and in two sentences of this chapter. Report wording: "Rewrite from code" (DOCS-4 §7.1). |
| `tenant-metric-binding.md` | Tenant Metric Binding | authoritative | drafting | 2026-09-21 | keep nearly as is | DL, Delivery to a tenant; also L10 | Checked against a named commit and has a table of known traps; to be retitled to the approved word "enable". Report wording: "Seed nearly as-is" (DOCS-4 §7.1). |
| `tenant-onboarding.md` | Tenant Onboarding | authoritative | drafting | 2026-10-01 | rewrite | L10, Tenant onboarding; also S3, S4 | A statement of intent for a commercial lifecycle that is not built; the functional map must rule on most of it. Report wording: "Rewrite from code and from rulings" (DOCS-4 §7.1). |

## docs/operations (16 files)

| path | title | authority | status | last commit date | chapter verdict | function | reason and source |
|---|---|---|---|---|---|---|---|
| `demo-operations.md` | Demo Operations | authoritative | drafting | 2026-08-19 | history | OP, Operations; also PV | Says itself that it is history; the estate it describes is gone, yet frontmatter still says authoritative. Report wording: "History-only" (DOCS-5 §9.3 F1). |
| `deployment-topology.md` | Deployment Topology | authoritative | drafting | 2026-10-01 | rewrite | OP, Operations | Describes a repository and services that do not exist and omits the Mac host; one table on hosting variants is reusable. Report wording: "Needs rewrite" (DOCS-5 §9.3 F1). |
| `evaluation-evidence-dbcp-application.md` | Evaluation-Evidence DBCP Application (E6-B singleton index, Invariant VI) | authoritative | authoritative | 2026-08-25 | history | OP, Operations; also EV | A one-off runbook against a frozen tree; its shape is a good template. Report wording: "History-only" (DOCS-5 §9.3 F1). |
| `incident-and-change-management.md` | Incident and Change Management | authoritative | drafting | 2026-10-01 | rewrite | OP, Operations; also DV | Change-record mechanics are right; the close gate is described through a retired table and there is no incident procedure. Report wording: "Needs rewrite" (DOCS-5 §9.3 F1). |
| `mac-auditor-operations.md` | Mac Auditor Operations | authoritative | active | 2026-10-01 | keep nearly as is | DV, Development; also OP (independent review) | Current, procedural and consistent with the project instructions; it carries dated facts that need an owner. Report wording: "Guide-ready" (DOCS-5 §9.3 F1). |
| `observability-and-telemetry.md` | Observability and Telemetry | authoritative | drafting | 2026-10-01 | rewrite | OP, Operations | Half the emission surfaces belong to a retired service; its list of what is absent is honest and still true. Report wording: "Needs rewrite" (DOCS-5 §9.3 F1). |
| `odoo-enterprise-subscription.md` | Odoo Enterprise Subscription: the Licensed Demo Database | authoritative | drafting | 2026-09-28 | keep nearly as is | OP, Operations; also PV | Current and matches the running system; it depends on a superseded chapter and needs a home under demo operations. Report wording: "Guide-ready" (DOCS-5 §9.3 F1). |
| `operations-overview.md` | Operations: Overview | authoritative | drafting | 2026-10-01 | rewrite | OP, Operations | Maps 8 of 15 chapters and cites a missing checklist; its constraints are sound. Report wording: "Needs rewrite" (DOCS-5 §9.3 F1). |
| `performance-and-scale.md` | Performance and Scale | authoritative | drafting | 2026-10-01 | rewrite | OP, Operations | Its target-against-built rows are current; the AI limits section describes a retired service. Report wording: "Needs rewrite" (DOCS-5 §9.3 F1). |
| `runtime-operations.md` | Runtime Operations — engines, triggers, runs, campaigns, retirement | authoritative | active | 2026-08-19 | keep nearly as is | RT, Runtime; also OP | Reported as the clearest target-against-built writing in its folder; three small repairs are named. Report wording: "Guide-ready after small repair" (DOCS-5 §9.3 F1). |
| `runtime-runbook.md` | Runtime Runbook | authoritative | active | 2026-08-19 | rewrite | OP, Operations; also RT | Right shape and right chain-status commands; the services table and the backup section are stale. Report wording: "Needs rewrite" (DOCS-5 §9.3 F1). |
| `security-operations.md` | Security Operations | authoritative | drafting | 2026-10-01 | rewrite | OP, Operations; also S1, S2 | Reported wrong against code on five points and built on retired services; two sections are still usable. Report wording: "Needs rewrite" (DOCS-5 §9.3 F1). |
| `serve-moves-and-live-windows.md` | Serve Moves and Live Windows | authoritative | drafting | 2026-09-30 | rewrite | OP, Operations | Reported as the best raw material in its folder, but frozen at 2026-09-30; the rules table should carry forward. Report wording: "Needs rewrite" (DOCS-5 §9.3 F1). |
| `support-and-escalation.md` | Support and Escalation | authoritative | drafting | 2026-10-01 | rewrite | SU, Support | Honest that nothing exists; contradicts the runbook on tickets; the incident-class table is reusable. Report wording: "Needs rewrite" (DOCS-5 §9.3 F1). |
| `tenant-lifecycle-and-subscription.md` | Tenant Lifecycle and Subscription | authoritative | drafting | 2026-07-06 | rewrite | S3, Tenant lifecycle and management; also S4 | The only full statement of the tenant commercial design, unrevised since 2026-07-06; written as built while its own drift list says nothing is built. Report wording: "Needs rewrite" (DOCS-5 §9.3 F1). |
| `upgrade-and-migration.md` | Upgrade and Migration | authoritative | drafting | 2026-10-01 | history | OP, Operations | Governs a frozen schema path and contradicts the current one; its clean-slate section needs an explicit ruling. Report wording: "History-only" (DOCS-5 §9.3 F1). |

## docs/compliance (6 files)

| path | title | authority | status | last commit date | chapter verdict | function | reason and source |
|---|---|---|---|---|---|---|---|
| `compliance-overview.md` | Compliance: Overview | authoritative | drafting | 2026-10-01 | rewrite | DV, Development (compliance records) | Sound as a map; still names a retired quality harness and a retired gate. Report wording: "needs rewrite (light)" (DOCS-5 §9.4 G). |
| `infosec-and-access-control.md` | InfoSec and Access Control | authoritative | drafting | 2026-10-01 | rewrite | S2, User and access management; also S1 | The right subject and mostly right mechanics, but omits two of four guards and misstates the bypasses. Report wording: "needs rewrite" (DOCS-5 §9.4 G). |
| `iso-27001-conformance.md` | ISO 27001 Conformance | authoritative | drafting | 2026-10-01 | keep nearly as is | DV, Development (compliance records) | Current to 2026-09-30 and candid. TENSION inside DOCS-5: §1.12 lists it as "Stale" from the controller charters. Report wording: "guide-ready as a status report; needs trimming for the guide" (DOCS-5 §9.4 G). |
| `privacy-and-the-immutable-fact.md` | Privacy and the Immutable Fact | authoritative | drafting | 2026-10-01 | rewrite | PR, Privacy and retention | Clear design and an honest drift list, but it reads as built where little is; one internal contradiction on evidence. Report wording: "needs rewrite" (DOCS-5 §9.4 G). |
| `risk-and-vendor-management.md` | Risk and Vendor Management | authoritative | drafting | 2026-10-01 | rewrite | DV, Development; also AI (compliance records) | The register half is accurate; the vendor inventory lists services that are not consumed and misses one that is. Report wording: "needs rewrite" (DOCS-5 §9.4 G). |
| `soc-2-conformance.md` | SOC 2 Conformance | authoritative | drafting | 2026-10-01 | rewrite | DV, Development (compliance records) | Stale against its sibling chapters and overstates privacy as implemented. Report wording: "needs rewrite" (DOCS-5 §9.4 G). |

## docs/archive (7 files)

| path | title | authority | status | last commit date | chapter verdict | function | reason and source |
|---|---|---|---|---|---|---|---|
| `assets/diagrams/_deferred/README.md` | absent | reference | deferred | 2026-07-06 | history | DV, Development (documentation) | A note on two diagrams held back because they teach the wrong boundary. No title in frontmatter; first heading is "Deferred Diagrams". Report wording: "History" (DOCS-4 §7.1 and §1.2 (A7)). |
| `development/historical-plans/v1-contract-objects-migration.md` | absent | absent | absent | 2026-07-06 | history | OP, Operations (schema change) | A nine-step coding plan to replace one contract table with per-family tables. No frontmatter at all. Report wording: "History" (DOCS-4 §7.1 and §1.2 (A6)). |
| `onboarding/data-seeding-and-build-order.md` | Data Seeding and Build Order | reference | retired | 2026-08-19 | history | the frame (no single function); spans L1 to L10 | Retired by its own banner. It was the only chapter that ordered the whole chain; its level table is worth carrying as an idea. Report wording: "History" (DOCS-4 §7.1 and §1.2 (A1)). |
| `onboarding/mc-chain-integrity.md` | MC Chain Integrity | authoritative | drafting | 2026-07-06 | history | L9, Chain integrity; also L6 | A procedure before the current metric framework; still marked authoritative and drafting, so it needs a retired banner. Report wording: "History" (DOCS-4 §7.1 and §1.2 (A4)). |
| `onboarding/metric-contract-creation.md` | Metric Contract Creation | authoritative | drafting | 2026-07-06 | history | L6, Metric Contracts and certification | The procedure before the current metric framework; still marked authoritative and drafting, so it needs a retired banner. Report wording: "History" (DOCS-4 §7.1 and §1.2 (A3)). |
| `onboarding/metric-registration.md` | Metric Registration | authoritative | drafting | 2026-07-06 | history | L6, Metric Contracts and certification | A retired registration procedure; its later addendum is the only step list for the current authoring path in these folders. Needs a retired banner. Report wording: "History" (DOCS-4 §7.1 and §1.2 (A2)). |
| `onboarding/metric-seed-catalog-management.md` | Metric Seed Catalog Management | authoritative | drafting | 2026-07-06 | history | L6, Metric Contracts and certification; also L8 | Loading a seed store by script; still marked authoritative and drafting, so it needs a retired banner. Report wording: "History" (DOCS-4 §7.1 and §1.2 (A5)). |

## Summary

All counts in this section were computed by script from the rows above and from the frontmatter values read at `origin/main`, not counted by eye.

### Chapter verdicts by folder

| folder | keep nearly as is | rewrite | history | designed, not built — keep as such | total |
|---|---|---|---|---|---|
| docs/overview | 0 | 2 | 3 | 0 | 5 |
| docs/foundation | 6 | 4 | 0 | 0 | 10 |
| docs/operating-model | 6 | 10 | 7 | 3 | 26 |
| docs/implementation | 3 | 12 | 14 | 0 | 29 |
| docs/ai | 0 | 1 | 6 | 0 | 7 |
| docs/development | 3 | 7 | 2 | 0 | 12 |
| docs/onboarding | 3 | 6 | 4 | 0 | 13 |
| docs/operations | 3 | 10 | 3 | 0 | 16 |
| docs/compliance | 1 | 5 | 0 | 0 | 6 |
| docs/archive | 0 | 0 | 7 | 0 | 7 |
| **all ten folders** | **25** | **57** | **46** | **3** | **131** |

The total is 131 files. 25 are "keep nearly as is", 57 are "rewrite", 46 are "history" and 3 are "designed, not built — keep as such".

### Status and authority values

The script that read the frontmatter counted each `status` value and each `authority` value across the 131 files.

| status value | files |
|---|---|
| drafting | 108 |
| approved | 5 |
| active | 3 |
| absent | 2 |
| closed | 2 |
| implemented | 2 |
| retired | 2 |
| reviewing | 2 |
| accepted | 1 |
| authoritative | 1 |
| deferred | 1 |
| evidence | 1 |
| living | 1 |

| authority value | files |
|---|---|
| authoritative | 108 |
| reference | 12 |
| absent | 11 |

**Files with `status: locked`: 0.** The exact value counted is the string `locked` in the `status` field of the frontmatter. No file among the 131 carries it. The combination the rule requires for binding force, `authority: authoritative` with `status: locked`, therefore occurs 0 times.

The check can be repeated with this command, which prints every `status` line found in the frontmatter of the 131 files and counts each value:

```
for f in $(git -C ~/MyProjects/bc-docs ls-tree -r --name-only origin/main -- docs/overview docs/foundation docs/operating-model docs/implementation docs/ai docs/development docs/onboarding docs/operations docs/compliance docs/archive | grep '\.md$'); do
  git -C ~/MyProjects/bc-docs show origin/main:$f | tr -d '\r' | awk 'NR==1&&$0!="---"{exit} NR>1&&$0=="---"{exit} /^status:/{print}'
done | sort | uniq -c
```

The `tr -d '\r'` step is needed because one file, `docs/development/metric-readiness-toolkit.md`, has Windows line endings. Without it the command reports 107 files with `status: drafting` where the true count is 108.

Three more facts follow from the same counts.

- 112 of the 131 files carry one of the five status values the documentation system chapter allows for chapters (`drafting` 108, `reviewing` 2, `retired` 2, `locked` 0, `superseded` 0).
- 17 files carry a status value that is not in that list: `approved` 5, `active` 3, `closed` 2, `implemented` 2, `accepted` 1, `authoritative` 1, `deferred` 1, `evidence` 1, `living` 1.
- 2 files have no `status` field: `docs/archive/development/historical-plans/v1-contract-objects-migration.md`, which has no frontmatter, and `docs/operating-model/metric-lifecycle.md`.

### Where reading reports disagree

**Between the seven reading reports: no disagreement was found.** Each of the ten folders was read by one report, and the two halves of `docs/operating-model` and of `docs/implementation` do not overlap. A script searched every report for the file name of every chapter outside that report's own folders, on lines that also contain a verdict word. It found no second verdict for any chapter. Two different files share the name `tenant-onboarding.md` (one in `docs/implementation`, one in `docs/onboarding`). DOCS-4 §7.1 compares them and says the implementation file "is closer to what exists", which agrees with DOCS-3B §7.

**Disagreements that the reports themselves record with other sources** are these.

| chapter | the disagreement | where it is recorded |
|---|---|---|
| `docs/operating-model/canonical-evaluation.md` | DOCS-2A gives "Rewrite". It records that an earlier code review, REVIEW-5, "listed CE as \"good enough to keep nearly as is\"", and that the DOCS-2A reader disagrees after a line-by-line read. | DOCS-2A §6 |
| `docs/development/quality-assurance.md` | DOCS-5 §9.1 gives "Guide-ready". The stale-chapter register that DOCS-5 extracts from the controller operating model chapter lists the same file as "Stale". | DOCS-5 §9.1 and §1.12 |
| `docs/compliance/iso-27001-conformance.md` | DOCS-5 §9.4 gives "guide-ready as a status report". The same register lists the file as "Stale". | DOCS-5 §9.4 and §1.12 |

The table rows for these three chapters carry the reading report's verdict. Each of the three needs a re-read before the verdict is relied on.

**Chapters with a split verdict inside one report** (the report judges parts of the chapter differently; the row carries the verdict for the larger part):

- `docs/overview/platform-db-foundation.md` (DOCS-1 §6.2)
- `docs/overview/structural-differentiators.md` (DOCS-1 §6.2)
- `docs/foundation/the-evaluation-boundaries.md` (DOCS-1 §6.2)
- `docs/operating-model/metric-directory.md` (DOCS-2B §6)
- `docs/operating-model/metric-lifecycle.md` (DOCS-2B §6)
- `docs/operating-model/operating-model-overview.md` (DOCS-2B §6)
- `docs/operating-model/quality-gates-and-chain-integrity.md` (DOCS-2B §6 and §6a)
- `docs/implementation/architecture.md` (DOCS-3A §7.1, §7.3 and §5.2)
- `docs/implementation/audit-and-activity-logging.md` (DOCS-3A §7.2)
- `docs/implementation/backend-services.md` (DOCS-3A §7.2)
- `docs/implementation/data-model-and-schema.md` (DOCS-3A §7.2)
- `docs/implementation/frontend-experience.md` (DOCS-3A §7.1 and §7.2)
- `docs/implementation/metric-catalog-and-source-reference.md` (DOCS-3B §7)
- `docs/onboarding/metric-workstream.md` (DOCS-4 §7.1)

### Files no reading report covers

None. Every one of the 131 files has a verdict in one of the seven reports, so no row carries a provisional verdict. The generating script stops if any listed file lacks a verdict or if a verdict names a file that is not in the list.

## The other folders of docs/

The ten chapter folders are not the whole of `docs/`. The remaining top-level entries at `origin/main` are listed here with file counts only, except `docs/reference`, which has its own inventory below.

`command: git -C ~/MyProjects/bc-docs ls-tree --name-only origin/main -- docs/` lists 14 folders and 2 files. File counts per folder come from `git -C ~/MyProjects/bc-docs ls-tree -r --name-only origin/main -- docs/<folder> | wc -l`, and markdown counts from the same listing with `grep -c '\.md$'`.

| entry | files | of which markdown | note |
|---|---|---|---|
| `docs/governance` | 688 | 688 | 660 under `adrs` (659 decision records and one README), 27 under `errata`, 1 under `plans` |
| `docs/evidence` | 346 | 292 | by sub-folder: `work-records` 160, `dbcp` 97, `closeouts` 50, `audits` 34, `ledgers` 5 |
| `docs/reference` | 157 | 156 | inventory below |
| `docs/assets` | 24 | 1 | diagrams and other assets |
| `docs/README.md` | 1 | 1 | DOCS-1 §6.2 lists it under "Should become history" and says to replace it |
| `docs/NAVIGATION.md` | 1 | 1 | DOCS-1 §6.2 lists it under "Should become history" and says to regenerate it |

There is no `docs/data-dictionary` folder at `origin/main`. The documentation system chapter names one (`bc-docs:docs/development/documentation-system.md:42 @ f4f5edd` and `:123`), but the data dictionary files are under `docs/reference/data-dictionary` (21 files).

## docs/reference: a grouped inventory

`docs/reference` holds 157 files and 289,875 words at `origin/main`. The files are grouped by kind below. The grouping follows the folder layout and the frontmatter of the files, and matches the grouping in DOCS-4 §6.

Words were counted per file and summed per group. The per-file command is `git -C ~/MyProjects/bc-docs show origin/main:<path> | wc -w`; the script used the same whitespace split and its total, 289,875, equals the total DOCS-4 §6 reports.

DOCS-4 §6 gives each group a trust rating, not one of the four chapter verdicts. The chapter verdict in the last column is therefore provisional: it is this annex's mapping of the DOCS-4 §6 rating, and each is marked "(provisional, this annex)". For a generated file, "rewrite" means run the generator again from the current source.

| kind | files | words | last commit dates | chapter verdict | basis in DOCS-4 §6 |
|---|---|---|---|---|---|
| Technical notes (`technical-notes/implementation/`): design surveys, requirements and decisions for the business concept registry and the metric framework | 26 | 108,557 | 2026-07-06 to 2026-10-01 | history (provisional, this annex) | "History of how BCF and MCF were designed. Not procedure." |
| Generated maps (`enforcement-surface-map.md`, `lifecycle-map.md`) | 2 | 46,225 | 2026-09-30 | rewrite (provisional, this annex) | Generated from the database on 2026-09-30; "High at generation date; six weeks old." To be generated again before use. |
| Source-system flat pages (`source-systems/*.md`, one page per external system) | 52 | 45,474 | 2026-07-06 to 2026-07-13 | designed, not built — keep as such (provisional, this annex) | The report says all carry `proof_status: designed`. Measured here: 50 of the 52 carry `proof_status: designed` and 2 carry `proof_status: shape_tested` (first `proof_status:` line of each file at `origin/main`). |
| Source-system dockets (`source-systems/<system>/`, seven systems, five files each) | 35 | 41,598 | 2026-07-13 to 2026-08-10 | rewrite (provisional, this annex) | "No docket records a real onboarding"; the Odoo log has not been updated since 2026-08-10. |
| Vocabulary (`vocabulary.md`, the approved status words) | 1 | 13,754 | 2026-10-13 | keep nearly as is (provisional, this annex) | Rated high; named as current and usable as a definition source. |
| API reference (`api/`) | 1 | 9,232 | 2026-07-06 | rewrite (provisional, this annex) | Generated in July and rated stale. To be generated again. |
| Code index (`code-index/`) | 5 | 5,316 | 2026-07-06 to 2026-10-01 | rewrite (provisional, this annex) | Generated at the same July commit and rated stale. To be generated again. |
| Source-system index and licensing (`source-systems/index.md`, `source-systems/sap-licensing-reference.md`) | 2 | 3,990 | 2026-07-13 | history (provisional, this annex) | "The proof-status ladder is a useful idea; the content is superseded". |
| Glossary (`glossary/`) | 1 | 3,021 | 2026-10-01 | rewrite (provisional, this annex) | Rated stale. |
| Docket template (`source-systems/_template/`) | 6 | 2,964 | 2026-07-13 | keep nearly as is (provisional, this annex) | Rated "Usable". |
| Runbook (`runbooks/`, one identity remediation task) | 1 | 2,799 | 2026-07-06 | history (provisional, this annex) | "The only runbook; one-off task". |
| Schemas (`schemas/`, one generated index and one JSON data file) | 2 | 2,798 | 2026-08-01 to 2026-09-30 | rewrite (provisional, this annex) | The index is rated stale. To be generated again. |
| Data dictionary (`data-dictionary/`, one page per database schema) | 21 | 2,272 | 2026-07-06 to 2026-10-01 | rewrite (provisional, this annex) | "Stale and thin (no columns)." To be generated again from the database. |
| Known-limitations register (`mfg-in-world-known-limitations.md`) | 1 | 1,108 | 2026-08-22 | keep nearly as is (provisional, this annex) | "Useful in kind". |
| Catalog of platform procedures (`platform-workflow-catalog.md`) | 1 | 767 | 2026-09-08 | keep nearly as is (provisional, this annex) | Rated "Summary only"; named as current and usable as a definition source. |
| **total** | **157** | **289,875** | | | |

Totals by provisional chapter verdict, computed by script from the table: keep nearly as is: 9 files, 18,593 words; rewrite: 67 files, 110,462 words; history: 29 files, 115,346 words; designed, not built — keep as such: 52 files, 45,474 words.

One reference file is cited by the project instructions at a path where it does not exist. DOCS-4 §6 reports that `mcf-re-entry-index.md` is under `docs/reference/technical-notes/implementation/`, while the DevHub project instructions cite it under `docs/implementation/`. This annex confirmed where the file is: `command: git -C ~/MyProjects/bc-docs ls-tree -r --name-only origin/main -- docs | grep mcf-re-entry-index -> docs/reference/technical-notes/implementation/mcf-re-entry-index.md` (one result).

## What could not be verified

- The reasons in the tables are the reading reports' findings. They were not re-checked against code or data by this annex.
- The reading reports are working files, not committed files, so they cannot be cited at a commit.
- The last commit date is the date of the last commit that touched the file on `origin/main`. It was not checked whether that commit changed the content or only the frontmatter, except for the one example given above.
- The assignment of each chapter to a function is this annex's own reading and has not been reviewed.
