---
id: platform-refactor-program-terms
order: 45.05
title: "The Platform in Brief, and Terms"
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

# The Platform in Brief, and Terms

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md).

This annex gives the longer account of what the platform is, the full list of terms, and the keys used for citations. The main document carries a short version of each.

## How citations are written

The full form is `repository:path:line @ sha` for code and documents, `query (database, date): SQL -> result` for live data, and `command: … -> result` for anything else. To keep the text and the glossary readable, the main document writes a citation to a much-cited file as a key and a line number, for example `VOC:166`. A number in square brackets, for example [16a], is a row of the evidence annex.

| Key | Stands for |
|---|---|
| OV | `bc-docs:docs/overview/platform-overview.md @ f4f5edd` |
| PB | `bc-docs:docs/foundation/the-problem.md @ f4f5edd` |
| INV | `bc-docs:docs/foundation/the-invariants.md @ f4f5edd` |
| OM | `bc-docs:docs/foundation/the-object-model.md @ f4f5edd` |
| EB | `bc-docs:docs/foundation/the-evaluation-boundaries.md @ f4f5edd` |
| CG | `bc-docs:docs/foundation/the-contract-grammar.md @ f4f5edd` |
| GS | `bc-docs:docs/foundation/the-governed-selection.md @ f4f5edd` |
| AM | `bc-docs:docs/foundation/the-authority-model.md @ f4f5edd` |
| VOC | `bc-docs:docs/reference/vocabulary.md @ f4f5edd` (the vocabulary page: the approved status words) |
| RP | `bc-docs:docs/implementation/platform-readiness-program.md @ f4f5edd` |
| TB | `bc-docs:docs/operating-model/tenancy-and-binding.md @ f4f5edd` |
| RE | `bc-docs:docs/operating-model/the-runtime-ecosystem.md @ f4f5edd` |
| TLS | `bc-docs:docs/operations/tenant-lifecycle-and-subscription.md @ f4f5edd` |
| DH | `bc-docs:docs/development/devhub.md @ f4f5edd` |
| DS | `bc-docs:docs/development/documentation-system.md @ f4f5edd` |
| COM | `bc-docs:docs/development/the-controller-operating-model.md @ f4f5edd` |
| QA | `bc-docs:docs/development/quality-assurance.md @ f4f5edd` |
| MAO | `bc-docs:docs/operations/mac-auditor-operations.md @ f4f5edd` |
| SM | `bc-docs:docs/operations/serve-moves-and-live-windows.md @ f4f5edd` |
| ADR-xxxxxx | `bc-docs:docs/governance/adrs/ADR-xxxxxx.md @ f4f5edd` (the file of decision DEC-xxxxxx) |
| CL | `barecount-devhub:CLAUDE.md @ 93cc1ea5` (the project instruction file) |
| GOAL | `barecount-devhub:blueprints/goal.md @ 93cc1ea5` (the goal file of the parked drive) |

Two kinds of statement carry no bc-docs citation, and say so: a term that bc-docs does not define (written "not defined in bc-docs; defined here as …"), and an operator ruling of 2026-11-13, which is recorded in this document under "The rulings".

## The platform in brief

**What it is.** The documentation's home page states it in one sentence: "BareCount is an enterprise data observation platform." (OV:45). In plain terms, BareCount reads data from a company's business systems, for example an accounting system. It records what it read, what that data means in business terms, and the numbers worked out from it. It keeps every one of those records permanently and writes a proof record at the same moment (OV:45, OV:47).

**The three failures it exists to prevent.** The Foundation chapter "The Problem" names them (PB:28-34):

- **"Meaning drift after observation."** Different parts of a system interpret the same value differently, so "the same value carries different meanings across the architecture" (PB:32).
- **"Reconstruction-based audit."** A past number is explained by re-running old work, so "reconstructed answers are approximations built from remaining fragments" (PB:33).
- **"Implicit reference."** A reference names a thing but not its version, so "the same reference returns different values at different times" (PB:34).

**The six invariants.** An invariant is a rule the platform must never break. There are six (INV:43-48):

1. "Meaning is evaluated once." Business meaning is produced once, at one place.
2. "Object ordering is fixed." Records are produced in one order, and no step is skipped.
3. "All state is immutable." A record is never altered. A correction is a new version.
4. "All references are explicit." A reference names the type, the identity and the version.
5. "Evaluation is non-replayable." Evaluating again produces a new version; it never rewrites the old one.
6. "Evidence is emitted, not inferred." Proof is written with the act, never rebuilt afterwards.

**The objects, in order.** The platform produces four kinds of record, called objects, in a fixed order (OM:40-47):

1. A **Source Object** is what was read from the source system, kept exactly as received.
2. A **Canonical Object** is the business meaning resolved from Source Objects.
3. A **Metric Snapshot** is a metric's value for a period.
4. An **Action Object** is a declared intent tied to Metric Snapshots. It is designed and not built (VOC:319).

Two more objects hold the proof. **Evidence** records that an act happened and its outcome. **Lineage** records what the act referenced (OM:48-49).

**The four boundaries.** A boundary is the one place where a kind of object may be produced. There are four: admission, canonical evaluation, metric evaluation and action evaluation. Each produces one kind of object and writes Evidence and Lineage with it. "No other operation produces authoritative state" (EB:37-44). Reading a record never causes an evaluation (EB:164).

**Contracts.** A contract is "a versioned, governed definition of how a boundary evaluation is performed" (OM:210). It is a definition, not data. Six kinds are in use (CG:50):

- a **Source Contract** declares the shape of one source table (CG:131);
- an **Admission Contract** declares the rules for accepting what was read (CG:148);
- an **Observation Contract** ties each source field to a business concept (CG:167);
- a **Canonical Contract** declares the business meaning of one entity (CG:189);
- a **Metric Contract** declares a metric's formula and inputs (CG:208);
- an **Intervention Contract** declares when an Action Object is created (CG:227).

Contracts refer to one shared list of business terms, the business concept registry (VOC:515). A contract version that is in force is never changed (CG:308).

**Tenants and the two databases.** A tenant is "one organization's identity on the platform, with its own database" (VOC:431). There are two kinds of database. The **platform database** (`bc_platform_dev`) holds what all tenants share: the contracts, the catalog of source systems, and each tenant's identity (TB:55, TB:65-66, CL:290). Each **tenant database** (`tbc_{slug}_dev`) holds that tenant's own objects and proof, and nothing crosses between tenants (TB:55, TB:67-68, VOC:312, CL:290). The platform database holds four tenant records; one is active, Kaveri (evidence row 16b). It is the demo tenant and is not counted as a customer (VOC:255).

**Integrity Assurance: what is claimed and what is not.** Integrity Assurance is the name of the platform's thesis (ADR-71c027:21, VOC:710). The platform claims that a metric's meaning and formula match a stated standard, and that its own mechanism computed the declared formula correctly and repeatably (ADR-346ae7:28). It does not claim that a value is externally correct. The approved wording is: "the method is guaranteed, the result is only as good as the data supplied" (VOC:714). For that reason "certified" is not used as a product claim, although it remains the internal status word for a metric that has passed certification (VOC:714-716).

**Metrics are how governed state is consumed.** By operator ruling F1 of 2026-11-13, metrics are not positioned as the product. The product is the governed, provable state described above, and metrics are how that state is consumed (ruling F1, under "The rulings"). The exact statement of the product is still to be written and confirmed by the operator in phase 2 (the same ruling).


## Terms used in this document

The glossary is grouped by subject. Each group is one table with the same four columns. Where bc-docs retires a word, the note says what to say instead. Where bc-docs gives no definition, the row says so and gives the definition this document uses.

One rule from the approved vocabulary applies to every status word below: a state word is always said with its subject, and a word about one tenant names the tenant, for example "metric available" or "enabled for Kaveri" (VOC:383-385).

### The platform and its people

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| platform | BareCount itself: the shared software, contracts and catalog that serve every tenant. | OV:45 | "Platform" is also used as an adjective for what is shared, as opposed to what belongs to one tenant: "platform database", "platform act". |
| operator | "The founder, today the only human in the loop." The operator is the only source of authority for acts on live systems. | COM:92 | Two other uses exist. "Platform operator" names the role that performs platform acts on a tenant (ADR-cf6d3b:64). The overview lists "Operator" as a reader who runs the platform (OV:80). Today one person holds all three. |
| tenant | "One organization's identity on the platform, with its own database." | VOC:431 | Its states are said with the subject: "tenant provisioning", "tenant active", "tenant suspended", "tenant archived", "tenant failed" (VOC:431). |
| tenant admin | The user in a tenant's own organization who administers that tenant. It is a login created by the platform for the tenant, carrying the tenant's identity and the tenant-admin role. | ADR-cf6d3b:68, ADR-cf6d3b:94 | The vocabulary gives the tenant admin two switches, enabled and visible; neither is built (VOC:173). |
| demo tenant | "`kaveri`: the tenant on which the platform is proven and shown. It is not counted as a customer." | VOC:255, VOC:432 | "Pilot" in any form is retired; say "demo tenant" or "Kaveri" (VOC:444, VOC:456). No field records a tenant's kind (VOC:438). |
| Kaveri | The name of the demo tenant. Its slug is `kaveri`. | VOC:255 | CLAUDE.md names a different demo tenant, `demo-selenite` (CL:246). No tenant has that slug [16b]. It is listed under "Items outside the program" as an instruction to correct. |
| Odoo | A commercial business-management system (an ERP). BareCount uses one Odoo installation, filled with made-up company data, as the source system that Kaveri reads. | CL:131, COM:107 | The installation is called `v3_lc5`, often shortened to "LC5". It runs on demand and is stopped by default (CL:131). |
| platform database | The one database that holds what all tenants share: contracts, the source catalog, and each tenant's identity. Its name on the development host is `bc_platform_dev`. | TB:55, TB:65-66, CL:290 | CLAUDE.md says it has 11 schemas (CL:290). The measured figure is 22 schemas and 329 tables [16a]. |
| tenant database | One database per tenant, holding that tenant's objects and proof. Named `tbc_{slug}_dev`. | TB:55, VOC:312, CL:290 | "The platform does not contact a tenant database for tenant-state reads at runtime" (TB:68). |
| plane | Not defined in bc-docs: the vocabulary page does not contain the word (command: `git -C ~/MyProjects/bc-docs show origin/main:docs/reference/vocabulary.md \| grep -c -i plane` -> 0). Defined here as: a separated area in which a kind of work or data lives. This document always says which plane it means. | — | The word has at least four meanings in the documents. (1) Runtime plane: where evaluated data lives, either a tenant or the demo plane (ADR-89db41:23). (2) Activation plane and Onboarding plane: platform acts versus tenant acts when a tenant is created (ADR-cf6d3b:60-62, ADR-cf6d3b:80). (3) Design plane versus execution plane: declaring something versus running it (ADR-79b62f:44; RP:117). (4) "Platform-plane proof" versus the "tenant zone" (GOAL:10). Open ruling F2 recommends adding the word to the vocabulary page. |
| demo plane | A set of tables (schema `demo`) inside the platform database, shaped like a tenant's tables, used to evaluate metrics on demonstration data without touching any tenant. It is reached only through a guarded transaction under its own database login. | ADR-89db41:23-25 | Decided 2026-10-26. No chapter mentions it (command: `git grep -n -i "demo plane" origin/main -- docs ':!docs/governance' ':!docs/archive'` in bc-docs -> 0 lines). |
| demo world | Not defined in a chapter. Defined here as: a fixed, versioned set of made-up company data used for demonstration and proof. | ADR-025bfc:25; GOAL:10; CL:131 | Used for two things: the Odoo installation itself ("Odoo demo world `v3_lc5`", CL:131) and the frozen copy of its data held in the demo plane ("frozen/versioned demo world", ADR-025bfc:25). |

### Sources and reading them

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| source system | "A product we can read, for example an ERP." | VOC:394 | |
| source catalog | The platform's description of the structure of the systems it can read. "It holds no business data." It has six levels: provider, system, version, module, table, field. | VOC:389-398 | A catalog entry for a table is a "source table". The database table that stores it is named `source.source_object`, a known mismatch (VOC:397). |
| connector | "Our technical ability to reach a kind of source system over a declared protocol. Platform-wide, not a tenant's." | VOC:419 | |
| connection | "One tenant's access to one source system through a connector. Its credentials live outside our records." | VOC:420 | |
| reader | "The admission definition for one business entity, reused by every tenant." | VOC:421 | The reader is a definition. The machine that runs it is called the Runner (RE:43). Older text calls the reader "UniBAT Reader" (CL:177). |
| observation | Reading what a source system holds. It is the input to admission and is not a boundary of its own. | EB:48; OM:44 | An observation that fails admission is a "rejected observation"; it is kept as evidence and is not a Source Object (VOC:316). |
| admission | The act, at the first boundary, of accepting an observation under its contracts and recording it as a Source Object. | EB:41 | "Admitted" alone is not approved, because it has meant three acts. Name the act: "source rows admitted", "proposal approved by the admission panel", "certified" (VOC:218). |

### Objects, boundaries and invariants

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| Source Object | "One observation of source state that was admitted, kept exactly as received, never changed." | VOC:315; OM:44 | Never said of a catalog entry (VOC:400). In text for the operator, write the full words, not "SO" (VOC:359). |
| Canonical Object | "Business meaning resolved from one or more source objects, under one canonical contract version." | VOC:317; OM:45 | Full words, not "CO" (VOC:359). |
| Metric Snapshot | "A metric's value for a period, evaluated from canonical objects." | VOC:318; OM:46 | When a metric has one on a tenant, the tenant word is "reporting" (VOC:318). |
| Action Object | "A declared intent bound to metric snapshots, with its outcome." | VOC:319; OM:47 | Not built (VOC:319). |
| Evidence | "The record that an evaluation act happened, with its outcome." | VOC:320; OM:48 | |
| Lineage | "The record of what an act referenced." | VOC:321; OM:49 | |
| boundary | One of the four places where authoritative records are produced: admission, canonical evaluation, metric evaluation, action evaluation. | EB:37-44 | An older Foundation text counts five; the four-boundary reading governs (EB:48). |
| invariant | One of six rules that define the platform's correctness. Each prevents one named failure. | INV:43-48 | A change that would break one is stopped and presented as a violation, not built (ADR-79b62f:29). |
| governed selection | "A declared, versioned rule that, given a selection parameter, resolves from the immutable authoritative-object set the specific object versions that constitute a named state, and records the resolved set in Lineage." In plain terms: a recorded rule for choosing which versions an evaluation reads, so the choice is never made at read time. | GS:32 | |

### Contracts

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| contract | "A versioned, governed definition of how a boundary evaluation is performed." | OM:210 | A contract is grammar, not one of the six objects (OM:210). |
| source contract | Declares "the structural shape of one source table or API endpoint". | CG:131 | |
| admission contract | Declares "the rules under which observed source state is admitted at the admission boundary". | CG:148 | |
| observation contract | Declares which source fields are read into which business concepts, and the resulting shape of the Source Object. | CG:167 | |
| canonical contract | Declares "the canonical form of one Entity": its grain, the fields it selects, and the rules that resolve several Source Objects into one meaning. | CG:189 | |
| metric contract | Declares "a numeric assertion over one or more Canonical Object versions": the formula, its inputs, its grain and its units. | CG:208 | The family in use is called the MCF Metric Contract. An older "legacy" family is frozen (CG:60-61). |
| contract version | One fixed wording of a contract, identified by the contract's identity plus a version. | CG:304 | A version that is in force is never modified (CG:308). For source, admission, observation and canonical contracts the field value `active` is said "in force" (VOC:350). |
| grain | Never said alone (VOC:574). **Canonical grain** is "the set of values that identifies one canonical object" (VOC:544). **Metric grain** is "the entity one instance of which a metric's value describes" (VOC:545). | VOC:544-545 | "Reporting grain" is retired; say "metric grain" (VOC:564). |
| key form | Not defined in bc-docs chapters (command: `git grep -n -i -E "key form\|key-form" origin/main -- docs ':!docs/governance' ':!docs/archive'` in bc-docs -> 0 lines). Defined here as: the declared format of the key that identifies a legal entity in a contract version's output. Two values exist: `canonical_id_v1` and `label_v1`. | `bc-db:migrations/0044_contract_version_legal_entity_key_form.sql:7 @ c6de1c4` | Used in open ruling B3. The HTTP route for a new canonical contract version cannot declare it [12]. |
| binding | Never said alone (VOC:556). A binding is a record that ties two things together. This document names which one: "source binding", "contract binding", "reader binding", "legal-entity binding". | VOC:549-556 | A **source binding** is a tenant's adoption of a source contract version (VOC:549). A **contract binding** is a tenant's adoption of a canonical or metric contract version, or a tenant's override (VOC:550). |
| adoption | The fact that a tenant uses one specific contract version. It is recorded as a source binding or a contract binding. | TB:93-98 | Not the same as acceptance of a value-affecting change, defined below. |

### The business vocabulary and metrics

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| vocabulary (the registry) | "The one governed list of everything the business talks about, which contracts refer to by identity." Its proper name is the business concept registry. | VOC:515 | Older text calls it "BCF". BCF means Business Concept Framework: the registry together with its authoring and certification. "Business Context Framework" is retired (VOC:562). Do not confuse it with the vocabulary page, `docs/reference/vocabulary.md`, which is the list of approved status words. |
| entity | "A governed business thing that plays a role, such as Customer, Supplier or Invoice." | VOC:516 | "Business object" is retired; say "entity" (VOC:570). |
| business concept | "The unit contracts refer to: one property of one entity, identified as entity.property (for example `invoice.bill_to`)." | VOC:517 | "Business field" and "canonical field" are retired (VOC:571). |
| characteristic | "The meaning part of a concept's name, such as 'credit limit', 'balance' or 'status'." | VOC:521 | |
| MCF | The metric context framework: the `mcf` database schema and the services that author, certify, bind and evaluate metric contracts. | COM:106 | "MCV" means a metric contract version (COM:106). |
| metric directory | The list of metrics that should exist, and why. A metric with an entry is "registered". | VOC:104; CG:381-383 | A directory entry is the only door to writing a metric (VOC:108). It is not a contract family (CG:381). |
| chain verdict | A green, amber or red reading that says whether the contracts a metric depends on line up. "It says nothing about values, it is not a certificate, and it gates nothing." | VOC:134 | "Chain complete" and "ready" are not approved; say "chain verdict green" (VOC:134, VOC:221). "Verdict" is never said alone (VOC:656). |

### Status words for a metric

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| certified | "Passed by the certification panel and deployable to a tenant." | VOC:127 | The database field says `active`; people say "certified" (VOC:119). "Active" is not said as a status (VOC:213). "Certified" is not used as a product claim (VOC:714). |
| released | "The platform has chosen to offer this certified metric in its portfolio." | VOC:129 | No record exists yet. Until one does, every certified metric is treated as released (VOC:129). |
| available | Said as "metric available": the tenant-side word for a released metric. | VOC:158, VOC:164 | |
| subscribed | "The tenant's package includes the metric." | VOC:165 | No record exists yet. Until one does, every active tenant is treated as subscribed to every available metric (VOC:165). "Entitled" is dropped as a status (VOC:170). |
| enabled | Said as "enabled for (tenant)": the metric is produced for that tenant, because its tables and contract bindings exist there. | VOC:166 | "Disabled" is not built (VOC:166). Replaces "onboarded", "bound", "set up" and "enrolled" (VOC:217). |
| visible | The tenant's admin has chosen to show an enabled metric to the tenant's users. | VOC:167 | No record and no such choice exist today. Until built, every metric is treated as visible (VOC:167). |
| reporting | "The metric has at least one accepted value on the tenant's own data." | VOC:168 | Replaces "working", "producing" and "live" as a metric status (VOC:215-216). |
| done (for a metric on a tenant) | All six hold: certified and released; enabled by the governed act alone; reporting for a stated period; in agreement with an independently worked expected value, written down; seen by a tenant user in the portal; no workaround at any step. | VOC:236-243 | "No record holds 'done' today" (VOC:249). "Proven" is not said of one metric (VOC:222). |
| proven (for the route) | The way metrics are produced is proven when: it used the mandated route alone; it repeats from a clean start by the written procedure alone, in a session that did not build it; each step and hand-off has tests that can fail; and a second, different case passes with no change. | VOC:245 | The source text uses the words "stage" and "handoff"; they are paraphrased here. |
| Demoed | A status of the parked drive: "a metric is `Demoed` when proven end-to-end against the in-platform, synthetic, frozen/versioned demo world, with no per-metric tenant crossing." | ADR-025bfc:25 | Not in the approved vocabulary and not in any chapter (command: `git grep -n "Demoed" origin/main -- docs ':!docs/governance' ':!docs/archive'` in bc-docs -> 0 lines). Which word names proof, "Demoed" or "validated against (source)", is open ruling F8. It is not the same as "done". |

### Tenants and delivery

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| Subscription | A platform-side record of what one tenant is allowed to use. One active Subscription per tenant. | TLS:38, TLS:42-43 | Designed, not built (VOC:434). Its end is said "subscription terminated" (VOC:436). |
| entitlement | The part of the Subscription that lists what the tenant may use: which business areas, metrics and source systems. | TLS:78-85 | Kept as the name of that part of the record. "Entitled" is not a status; say "subscribed" (VOC:170, VOC:214). |
| tier | One of four planned commercial levels of Subscription: Demo, Starter, Professional, Enterprise. | TLS:54-61 | Not built. The interim model has "no billing, no tiers" (ADR-cf6d3b:77). |
| package | The named offer a tenant subscribes to. Metrics are bound to packages, one package to many metrics, and a metric may sit in more than one package. | Operator ruling T1, 2026-11-13 (under "The rulings"); VOC:165 | Not defined as a term in the vocabulary; open ruling F2 recommends adding it. The interim package is "Pre Launch Exclusive", meaning all metrics allowed (ADR-cf6d3b:67). A table `pricing.package` exists and ties no tenant to a plan or metric (ADR-c220e4:35). The certification panel also judges a "frozen metric package" (VOC:623); that is a different thing. |
| provisioning | Creating the database objects something needs. Used for two subjects: creating a tenant and its database ("tenant provisioning", VOC:431), and creating in a tenant's database the tables a metric needs (a "provisioning command", VOC:166). | VOC:166, VOC:431 | "Provisioned" is not approved as a tenant's status; say "tenant active" or "infrastructure active" (VOC:459). |
| value-affecting change | A change to a contract that can affect a reported value. It reaches a tenant only when the tenant's admin, or a role or user the tenant designates, accepts it. Until then the tenant stays on the version it adopted. When it is uncertain whether a change affects a value, it is treated as value-affecting. | Operator ruling T3, 2026-11-13 (under "The rulings") | Not yet in the vocabulary; open ruling F2 recommends adding it. One ADR uses the phrase "value-affecting semantics" for a related test (ADR-025bfc:29). |

### Proof

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| Integrity Assurance | "The platform's product thesis: the deterministic machine gate is the primary, hard guarantee, with a residual true-meaning panel behind it." | VOC:710; ADR-71c027:21 | "A philosophy label"; "never a state word and names no record" (VOC:710). What it hands a customer is open ruling F6. |
| expected value | The value a metric should have for a period, "worked out independently from the same source data". | VOC:241 | This is the approved phrase, and the one this document uses. |
| proof against the source | Not defined in bc-docs; defined here as: the act of comparing a metric's governed value with its expected value, and the written record of that comparison. It is function PV, Proof against the source, of the functional map. | "The functional map" in this document | The vocabulary's status phrase is "validated against (source)", for example "validated against Odoo LC5"; its record is not built (VOC:128). "Validated" alone is not approved (VOC:230). |
| oracle | An older word for the source of an expected value. This document says "expected value" instead. | VOC:128 (the only use on the vocabulary page) | It names two things that are not connected. (1) In bc-demo: 946 SQL files that compute figures directly from the Odoo database (command: `git -C ~/MyProjects/bc-demo ls-tree -r --name-only origin/main \| grep metric-coverage \| grep -c '\.sql$'` -> 946). (2) In bc-core: a row in the table `demo.oracle_custody` (`bc-core:src/boundary/__fixtures__/bc-db-demo-plane/0051_demo_proof_substrate.sql:20 @ ec72438b`). bc-core's source tree never names the bc-demo files (command: `git -C ~/MyProjects/bc-core grep -c 'metric-coverage' origin/main -- src` -> no matching file). Separately, "Oracle" is also a vendor whose products appear in the source catalog. |
| the Demoed drive and its ladder | The program this document parks. Its demo plane was decided on 2026-10-26 (ADR-89db41:6) and it was parked on 2026-11-13 (under "The decision" and "What is parked and what is held unchanged"). Its goal: "Every metric in the validation corpus reaches `Demoed`" on the platform's own demo data. Its ladder is five rungs, R1 to R5, from one metric on a made-up fixture (R1) to the whole set (R5). | GOAL:8-10, GOAL:21-35 | Parked by this program. R1 is recorded as done and R2 as current (GOAL:24-26). |
| AI panel | "A fixed set of AI models, each in a named seat, that answers one question about one case." | VOC:617 | There are four: registry authoring, metric authoring, certification, and one inside an orchestrator (VOC:621-624). |
| flagger | The role of the AI panel since 2026-10-13: it may raise a concern, and each concern is resolved against the standard or the machine evidence. "A flag is never an auto-reject and never a required pass." | ADR-346ae7:6 | Not a vocabulary word. |

### Development: DevHub and its records

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| DevHub | "The coordination registry": a small server and database (repository `barecount-devhub`, port 4000) that records sessions, tasks, plans, decisions and reviews. | COM:93; DH:38 | It "does not run contract evaluation" and holds no tenant data (DH:48). |
| session | "The unit of governed engineering work in DevHub. A session is opened, carries a saved plan, records checkpoints, and closes with a report and a self-audit." | COM:94; DH:84 | In practice a session is one conversation of an AI coding assistant, identified `SES-xxxxxx` (DH:88). |
| unit | Not defined in bc-docs; defined here as: one bounded piece of work, done under one DevHub session that is bound to one task. | CL:311 uses "your open unit" without defining it | "The method" and "Who does what" write "unit of work". |
| checkpoint | A progress entry a session records at a milestone: what is done and what remains. | DH:90 | |
| plan | Two things. (1) The plan a session saves before any work, which is also half of its change record (DH:89, DH:93). (2) A standing plan record in DevHub, identified `PLN-xxxxxx`, with its own tools (DH:61). | DH:61, DH:89 | |
| task | "A unit of work recorded in DevHub (`TSK-xxxxxx`), with a lifecycle of parked, planned, in progress, and completed, aborted or failed." | COM:95 | |
| anchor (the pinned blueprint) | A short text that DevHub shows to every session at its start, stating the current goal. It is pinned: it changes only under a recorded operator grant. It points to a longer reference file. | GOAL:3, GOAL:38; `barecount-devhub:src/routes/active-program.js:3-4 @ 93cc1ea5` | Not defined in bc-docs. Today's anchor is `blueprints/demoed-terminal.md`, limited to 2048 bytes (GOAL:3). This program's anchor is to be `blueprints/platform-refactor.md` (see "How this document is kept"); that file is not on `origin/main` yet [31]. |
| memory files | Notes an AI session keeps between conversations, stored on the developer's machine outside every repository and loaded automatically at the start of each session. | CL:311; `bc-docs:docs/development/developer-experience.md:252 @ f4f5edd` | Not an authority. This document cites a memory file only as a memory record. |
| hotspots page | A DevHub page that shows, for each repository, file size, how often files change, and a per-file scan against ten code rules. It is "a mirror, not a gate". | QA:49; `barecount-devhub:src/index.js:480-484 @ 93cc1ea5` | |

### Development: bc-docs and decisions

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| bc-docs | "The documentation repository and the single source of truth for platform documentation." | COM:97 | The copy on the development host's disk is behind `origin/main`; this document reads `origin/main` only. |
| chapter | One markdown file in one of the eight sections of bc-docs (Foundation, Operating Model, Implementation, AI, Development, Onboarding, Operations, Compliance) or the home page. | OV:55-68; DS:45 | |
| authority (of a chapter) | A label in the chapter's header: `authoritative` (its statements bind once it is locked), `reference` (explanatory), or `evidentiary` (kept as proof). | OV:93-97 | |
| status (of a chapter) | A second label in the header: `drafting`, `reviewing`, `locked`, `superseded` or `retired`. | OV:99-105 | The vocabulary page carries `status: approved`, a value outside this list (VOC:4). |
| locked | For a chapter: all checks passed and the founder approved. "Binding force equals `authority == authoritative` and `status == locked`." | OV:103, OV:107 | No chapter is locked today [21a] (see the chapters annex). The word has two other uses: the "locked" lane taxonomy (ADR-a67bae:21) and a "calibration-locked" panel roster (VOC:633). For this program's use, see "lock" below. |
| ADR | "An architecture decision record, a file under `docs/governance/adrs/ADR-{uid}.md` in bc-docs, identified by a `DEC-xxxxxx` UID." | COM:96 | The `DEC-` identifier is the name to use. Short codes such as "D581" are nicknames and are not unique (CL:297). |
| erratum | A record of a contradiction between an authoritative text and the reading currently in force, usually between a Foundation text and current practice. Identified `FND-ERR-XXX`. | AM:139; DS:156 | |

### Roles, review and authority

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| controller | "A long-lived Claude session that owns one area of the BareCount platform." | COM:89 | |
| controller fleet | "A set of long-lived Claude sessions, each answering for one area of the platform, coordinated by one of them." Thirteen controllers were named. | COM:85; ADR-41e4bc:43 | Parked by this program as a method (see "What is parked and what is held unchanged"). |
| the Chief | "The controller of controllers." In this program, the one driving session and the single editor of this document. | COM:91; "Who does what" in this document | |
| worker | "A short-lived session that a controller spawns for one bounded task." | COM:90 | |
| the auditor (Codex) | "The independent auditor: a separate model session that reviews engine changes it did not author." It runs on the same machine under a separate account, `bcauditor`. | COM:99; MAO:19 | A different meaning exists: the overview's "Auditor" is an outside person performing an ISO 27001 or SOC 2 audit (OV:81). Who "the auditor" is for a customer is open ruling F6. |
| the exchange | "The permanent message protocol between a session and Codex." Each conversation is a thread named `gen-xxxxxx`. | COM:100; ADR-081931:29-33 | |
| the desk | "The auditor exchange desk, a service on port 3040 … where the operator records grants." Its repository is `bc-exchange`. | COM:101; MAO:30 | "A request on the desk is never authority. Only a grant recorded with your phone code is" (MAO:53). |
| grant | "An operator authorisation recorded on the desk by entering the current six-digit code from an authenticator app." | COM:102 | |
| the hard line | Not defined in bc-docs (command: `git grep -n -i "hard line" origin/main -- docs` in bc-docs -> 0 lines). Defined in the parked drive's reference as: no gated act on a live system (a database apply, a merge, a serve-move, a cloud change, a tenant activation, contract or metric authoring) without a recorded operator grant; "a chat 'yes' is never the scoped go". | GOAL:43-44 | "Who does what" states the set this program uses. Which acts stay under it on the development host is open ruling G1. |
| lane | In this document: one of the ten families of authoring work, L1 to L10, from the source catalog to tenant onboarding. | ADR-ce4314:21-33; RP:94-111 | A second meaning exists: a review lane is the order in which the auditor takes messages, where `Lane: platform` goes first (CL:193; MAO:37). |

### Operations

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| serve-move | "Switching port 3100 from one pinned bc-core build (a clean detached worktree at one commit) to another." Port 3100 is where the platform's main service answers. | SM:88; COM:103 | The chapters write "serve move". |
| freeze worktree | A separate checkout of bc-core at one exact commit, kept under `~/MyProjects/_wt/` and named `freeze-<letter>`. The served build runs from one. Each is built twice, and the two builds must be identical. | SM:89 | The chapter's term is "freeze tree / twin trees". |
| migration | One numbered SQL file in the `bc-db` repository that changes the platform database's structure. It is the only way such a change is authored and applied. | ADR-4c1396:22 | Each apply is recorded as one row in `infrastructure.schema_migration_event` (ADR-4c1396:22). |
| restore-proof | Not defined in bc-docs; defined here as: proving a migration by applying it to a restored copy of a fresh read-only dump of the live database, with the same owners and permissions, and never to the live database. | CL:262 | |
| apply window | Not defined in bc-docs under that name; defined here as: the announced period in which a migration is applied to the live database. | COM:104 defines "live window"; SM:317 | "A migration apply is a live act" and needs the operator's database approval and its own grant (SM:317). |

### Terms the function summaries and dossiers use

Each of these is used in the function summaries or in a dossier. The third column gives the citation, or names the dossier that carries it.

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| platform scope; tenant scope | The two kinds of caller bc-core recognises: an operator of the platform, or a user of one tenant. | Dossier for S1, Authentication | |
| platform group | The Cognito group whose members are given platform scope. | `bc-core:src/auth/strategies/cognito-jwt.strategy.ts:116-127 @ ec72438b` | Cognito is the managed sign-in service the platform uses. |
| tenant class | A column of the tenant registry with two values, `fixture` or `customer`. | `bc-db:migrations/0040_fixture_classification_and_datname_authority.sql:5-13 @ c6de1c4` | The vocabulary page says no field records a tenant's kind (VOC:438); see open ruling T5. |
| placeholder page | A route of the operator console that shows no working screen. | `bc-admin:src/components/AppRouter.tsx:175, 262-265, 296, 299, 307-309 @ d37b241` | |
| in force | The spoken form of the field value `active` on a source, admission, observation or canonical contract version. | VOC:350 | For a metric contract version the spoken word is "certified" (VOC:119). |
| 48-hour mark | The time stamped on the prior contract version (`supersede_after`) when a new version is made active. Nothing completes the supersession afterwards. | `bc-core:src/registry/contracts/contract-version.repository.ts:214-221 @ ec72438b` | See stitch point 10. |
| activation fan-out | The automatic writing of a binding to a newly active contract version for each tenant bound to the prior version. | `bc-core:src/schema-provisioner/contract-activation.service.ts:1-21 @ ec72438b` | Ruling T3 requires it to change for a value-affecting change. |
| held version | A canonical contract version kept in the state `pending_provisioning` for the demo plane, with no fan-out to tenants. | Dossier for L5, Canonical Contracts | |
| readiness pass | The run that moves contract versions from `pending_provisioning` to `active`. | `bc-core:src/registry/contracts/provisioning-readiness.service.ts:83-107 @ ec72438b` | "Readiness" is the name of the run, not a status. See "Items outside the program". |
| provisioning command | The record that asks for one table to be created in one tenant's database. | Dossier for L10, Tenant onboarding; VOC:166 | |
| grain pin | A pin from a canonical contract version to one version of the entity that is its grain. | Dossier for L5, Canonical Contracts | The HTTP route cannot declare it [12]. |
| realized | Said of a metric directory entry: asserted as fulfilled by a metric contract version. | VOC:105 | |
| proof pin | The unchangeable record of one comparison between a value the platform produced and an expected value. | Table `demo.metric_proof_pin` [3]; dossier for PV, Proof against the source | |
| independence tier | A label on an expected value that says how independently of the platform it was worked out. | Dossier for PV, Proof against the source | |
| bridge | The record that joins a proof made on the demo plane to a metric contract version. | Dossier for PV, Proof against the source (ADR DEC-eb612b) | Two rows exist, both marked `partial`. |
| trigger mode | The declared way a runtime act is started. | `bc-docs:docs/operations/runtime-operations.md:44 @ f4f5edd`; dossier for RT, Runtime | See stitch point 1. |
| campaign | One run that evaluates many metrics. | `bc-core:src/boundary/campaign-evaluation.controller.ts:63-93 @ ec72438b` | |
| nullification | Overwriting a field of personal data with a fixed marker while the row itself remains. | Dossier for PR, Privacy and retention | |
| data-subject request | A person's request to see or erase the data held about them. | Dossier for PR, Privacy and retention | |
| live act; live window | A live act is "any act that changes live state" (SM:47). A live window is one announced run of live acts under an operator grant (SM:52). | SM:47, SM:52 | "Live" here describes a system in use. It is never a metric's status. |
| migration ledger | The table `infrastructure.schema_migration_event`, with one row for each apply of a migration. | ADR-4c1396:22 | |
| served build | The fixed checkout, commit and build of bc-core that answers on port 3100. | Dossier for OP, Operations | Today it is `_wt/freeze-1055` at `ec72438b` [20b]. |
| close gates | The checks DevHub runs when a session closes. | `barecount-devhub:src/lib/close-gates.js:49-189 @ 93cc1ea5` | |
| change record | One DevHub record, identified `CHG-xxxxxx`, that joins a session's plan to its closing report. | `bc-docs:docs/development/decision-and-change-procedure.md:122 @ f4f5edd` | |

### Words this program adds

None of these is defined in bc-docs. Three were checked by search (commands, each run in bc-docs: `git grep -n -i "functional map" origin/main -- docs` -> 0 lines; `git grep -n -i "reference run" origin/main -- docs` -> 0 lines; `git grep -n -i ratchet origin/main -- docs ':!docs/governance' ':!docs/archive' ':!docs/evidence'` -> 0 lines). Each is defined by this document, under the heading named in the third column.

| Term | Plain definition | Where it is defined | Notes |
|---|---|---|---|
| function | One thing the platform must do, with a code and a name, for example "S1, Authentication" or "L5, Canonical Contracts". | RP:79-120 (the list "the platform functions"); "The functional map" | The functional map adds nine functions that are not in the bc-docs list. |
| functional map | The table of every function, with what it does and its group. | "The functional map" | Built from three bc-docs sources: the function list (RP:77), the vocabulary page, and the coverage rule (ADR-a67bae:23). |
| dossier | The full record of one function under eleven fixed headings, held in one of the three function-dossier annexes. A summary of each is under "The functional map". | "The functional map" | |
| surface (as in "every surface has one owner") | Anything a person or a program can act through or read: a route, a service, a script, a command, a table, a screen or a document. | "The functional map" (the coverage rule) | The lane taxonomy's rule covers controllers and tables: "a controller/table belongs to exactly one lane" (ADR-a67bae:23). This program widens it to every kind of surface and to every function. |
| stitch point | A hand-off between one function and its neighbour. | "The hand-offs between functions" | Twelve are listed there. |
| stitch contract | The written agreement for one stitch point. It states which two functions meet; what passes across, in which record and field; who acts; what triggers the act; and what each side may assume. | "The hand-offs between functions" | Not a contract in the platform's sense (see "contract"). |
| the thread | One tenant and one metric, followed from offer to seen in the portal. Each function is proven by walking its part of it. | "The thread" | Not the same as a `gen-` thread of the exchange. |
| application command (status, check, do, verify) | One of the small set of commands that are the only way to perform a function's acts. Each has four verbs: status (where this stands and what is required next), check (a dry run that says what would be refused and why), do (the governed act), verify (proof that it worked). | "Commands: the platform used like an application" | |
| phase | One of the twelve numbered groups of functions in the order of work. | "The order of work" | |
| step (of the method) | One of the five things done to each function, in order: Define, Audit, Modify, Prove, Lock. Each has an exit that can be checked. | "The method" | |
| ruling | A decision that belongs to the operator, numbered in one of four series (A, T, B, G). | "The rulings" | |
| parked; held unchanged | "Parked" means kept exactly as recorded and not worked on. "Held unchanged" means nothing is added, repaired or removed until the owning function reaches its turn. | "What is parked and what is held unchanged" | |
| the guide | The one new section of bc-docs, `docs/guide/`, with one chapter for each function and the functional map as its index. It does not exist yet. | "bc-docs: read first, and kept true" | |
| lock | The last step of the method for a function: its code gets a CI guard, its chapter merges and is marked locked, and the texts it replaces are retired in the same change. | "The method"; "How a lock works" | Open ruling F5 proposes that a chapter is locked when its function is locked. |
| guard | An automated check that fails a change when a rule is broken. In this document it means a check in CI (continuous integration), the automated checks that run on every proposed change. | "How a lock works"; an existing example at QA:101 | The word has two other uses on the platform: a login check on a route (RP:88) and a database trigger that refuses a write (ADR-cf6d3b:54). |
| ratchet (shrink-only baseline) | A recorded count of today's rule failures that may go down and may never go up. A new failure fails the build. | "Stabilising the codebase" | bc-docs describes the same mechanism as "shrink-only registers" (QA:101; CL:226). |
| reference run | A repeatable run that evaluates a fixed set of metrics from a fixed copy of the databases and compares the results with stored expected values. It does not exist yet. | "The reference run" | It is to be built before any engine code is modified. |
