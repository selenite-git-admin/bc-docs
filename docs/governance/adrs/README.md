---
id: appendix-f-adrs
title: "Appendix F — ADR Registry"
appendix: F
status: drafting
authority: authoritative
generator: scripts/docs-control/generate_adr_registry.py
---


# Appendix F — ADR Registry

The ADR Registry is the canonical index of platform decisions. Each entry has a structurally unique UID (`DEC-xxxxxx`) used in cross-references throughout the documentation. The ADR files are the source of truth (DEC-a4e550); this registry is generated from their frontmatter and is never edited by hand.

**Counts at generation.** 620 records: accepted 1, decided 202, implemented 270, proposed 12, reversed 8, superseded 127. Quarantined duplicates (not counted): 1 (ADR-DEC-e82f0a.md). Non-canonical filenames: 4 (ADR-DEC-e82f0a.md, ADR-chain-invariants.md, ADR-d315ve.md, ADR-d316mr.md).

**Hygiene.** The supersession pair rule (DEC-623f8f rule 1) is enforced on every push and pull request by `.github/workflows/adr-hygiene.yml` running `scripts/docs-control/audit_adrs.py`. That auditor's report is `docs-control/reports/adr-hygiene.md`. See erratum ADR-ERR-005 for the rules DEC-623f8f names that are not built.

| UID | Title | Status | Supersedes | Superseded by | Note |
|---|---|---|---|---|---|
| `DEC-000001` | [Platform Host Services — control plane and shared services foundation](./ADR-000001.md) | superseded |  |  |  |
| `DEC-000002` | [Contract lifecycle in Admin app, enforcement in Platform Host](./ADR-000002.md) | superseded |  |  |  |
| `DEC-000003` | [Three-contract model — Raw, GDP, KPI](./ADR-000003.md) | superseded |  |  |  |
| `DEC-000004` | [Worker pool architecture for contract execution](./ADR-000004.md) | superseded |  |  |  |
| `DEC-005ea7` | [Single production environment — no dev/staging/prod per tenant](./ADR-005ea7.md) | implemented |  |  |  |
| `DEC-00bba0` | [Discovery scan counts are frozen snapshots, not denormalized counters](./ADR-00bba0.md) | implemented |  |  |  |
| `DEC-010bf9` | [Connection simulation — bc-sdg serves as mock SAP system for end-to-end demo](./ADR-010bf9.md) | superseded |  | DEC-b390ef |  |
| `DEC-011c93` | [Schema contracts managed via DB + Admin UI, not repo seed files](./ADR-011c93.md) | implemented |  |  |  |
| `DEC-011ed2` | [Catalog admission architecture: thin orchestrator + per-source adapters + shared ingest (no global monolith)](./ADR-011ed2.md) | decided |  |  |  |
| `DEC-01419c` | [MC Body Purity — Catalog Fields Out, Formula as Object, sql_logic Parked](./ADR-01419c.md) | implemented |  |  |  |
| `DEC-018138` | [Curated-content promotion through the spine (W3)](./ADR-018138.md) | proposed |  |  |  |
| `DEC-01bd6b` | [Runtime Orchestration](./ADR-01bd6b.md) | decided |  |  |  |
| `DEC-01df6b` | [Metric Catalog Tables are Derived from contract_json — JSON Authored, Catalog Decomposed](./ADR-01df6b.md) | implemented |  |  |  |
| `DEC-026fae` | [bc-portal Naming Convention — route equals component equals nav label, no legacy suffixes](./ADR-026fae.md) | superseded |  | DEC-162de5 |  |
| `DEC-027ef6` | [Structural Integrity program — execution, method & sequencing](./ADR-027ef6.md) | decided |  |  |  |
| `DEC-02f5a9` | [Business Concept Registry: vocabulary identity model and greenfield rebuild](./ADR-02f5a9.md) | decided | DEC-a17d0f |  |  |
| `DEC-03cf97` | [Radix UI + Tailwind v4](./ADR-03cf97.md) | implemented |  |  |  |
| `DEC-03db11` | [Contract Body Principle — JSON-First, Catalog-Separate](./ADR-03db11.md) | superseded |  | DEC-ec9e89 |  |
| `DEC-049cb1` | [Apex Generator Architecture for Permanent CFO Pack Demo](./ADR-049cb1.md) | superseded |  | DEC-076521 |  |
| `DEC-04dade` | [bc-portal architecture & patterns](./ADR-04dade.md) | superseded |  | DEC-6cdceb |  |
| `DEC-05140c` | [Unified Source Catalog — drop Landscape, status-driven approval, scope attribute](./ADR-05140c.md) | implemented |  |  |  |
| `DEC-057c1f` | [Mapping is embedded in contract constructors — no standalone mapping entity](./ADR-057c1f.md) | implemented |  |  |  |
| `DEC-05815d` | [In-process contextual audit panel: the semantic axis of metric audits must be a recorded machine act](./ADR-05815d.md) | implemented |  |  |  |
| `DEC-063b5e` | [Formula Rendering — AST Parser Replaces Regex for LaTeX Generation](./ADR-063b5e.md) | decided |  |  |  |
| `DEC-0659d9` | [Screen Registry: design_rationale captures scope — no separate scope columns](./ADR-0659d9.md) | implemented |  |  |  |
| `DEC-068fe7` | [Mock/Real dual-path via env.useMock](./ADR-068fe7.md) | implemented |  |  |  |
| `DEC-06cb2c` | [Two sectors in bc-portal: CXO Portal + Control Plane (gated)](./ADR-06cb2c.md) | decided |  |  |  |
| `DEC-075dd3` | [Old readers/flavors retired — fresh assets with SDG executor configs](./ADR-075dd3.md) | implemented |  |  |  |
| `DEC-076521` | [Apex Tenant Binds to SAP S/4HANA Reader Chain; bc-sdg as Profile-Parameterised SDG-SAP Service](./ADR-076521.md) | superseded | DEC-049cb1 | DEC-b390ef |  |
| `DEC-081931` | [Standing Claude↔Codex exchange family gen- (thread-addressed, permanent)](./ADR-081931.md) | implemented |  |  |  |
| `DEC-08dc92` | [Platform/Tenant Route Isolation — /api/* vs /api/t/* with schema-per-tenant DB fence](./ADR-08dc92.md) | implemented |  |  |  |
| `DEC-093e56` | [Governed primary within a pinned leg: one admission run per grain group, lowest admission_id, row-local inputs must agree (minimal DEC-a57eb8 amendment; latest-by and CO succession stay deferred)](./ADR-093e56.md) | decided |  |  |  |
| `DEC-09b8e6` | [Unified Source Catalog — status-driven 6-tier hierarchy with object/view support](./ADR-09b8e6.md) | implemented |  |  |  |
| `DEC-09f86b` | [M12 Metric Authoring Panel — Judge role + Exhibit-ID abstraction + admissibility-scoped retrieval (replaces Moderator-as-witness shape)](./ADR-09f86b.md) | implemented |  |  |  |
| `DEC-09fb2f` | [Tenant evidence-chain immutability + runtime identity separation (platform prerequisite)](./ADR-09fb2f.md) | decided |  |  |  |
| `DEC-0a0843` | [Open-Standard Publication Protocol Architecture](./ADR-0a0843.md) | decided |  |  |  |
| `DEC-0a187d` | [Multi-source canonical join in CcV2CanonicalResolverService — honor declared secondary source_references](./ADR-0a187d.md) | decided |  |  |  |
| `DEC-0a5947` | [bc-admin Information Architecture — 5 navigation groups](./ADR-0a5947.md) | superseded |  |  |  |
| `DEC-0a614d` | [Retain the real-SAP OData executors dormant (do not retire) — corollary of D524](./ADR-0a614d.md) | decided |  |  |  |
| `DEC-0a75b5` | [Registry schema circular import fix — pg-schema.ts extraction](./ADR-0a75b5.md) | implemented |  |  |  |
| `DEC-0b3c08` | [D053: Master/Tenant-Override contract pattern — platform defines, tenant tunes](./ADR-0b3c08.md) | implemented |  |  |  |
| `DEC-0b5a4c` | [Source schema admission: direct, manifest-bound extract admission replaces the seed store — Mongo bc_seed retires as forage; no Postgres seed store (Amendment 1 governs)](./ADR-0b5a4c.md) | decided |  |  |  |
| `DEC-0cdfed` | [Drift Visibility & Chapter Conformance — citation lint, loud-warn, structured drift inventory, anti-revisionism gate](./ADR-0cdfed.md) | decided |  |  |  |
| `DEC-0d5b39` | [The Reader Model and the Runtime Ecosystem](./ADR-0d5b39.md) | decided | DEC-129417, DEC-d785d4 |  |  |
| `DEC-0e3c64` | [Contract Chain Clarification — Observation Contract is Canonical-Chain (Mapping Binding), not Source-Chain](./ADR-0e3c64.md) | implemented |  |  |  |
| `DEC-0e4547` | [Platform DB Foundation Program operating model — approval-only operator, design briefs, autonomous implementation units, auditor-gated merges](./ADR-0e4547.md) | decided |  |  |  |
| `DEC-0f15a7` | [date_add — additive D330 compute function for net-due-date derivation](./ADR-0f15a7.md) | implemented |  |  |  |
| `DEC-0f3e57` | [MCF Secondary Metrics — metric-over-metric-snapshot DAG (Component D)](./ADR-0f3e57.md) | decided |  |  |  |
| `DEC-0f61dd` | [Source system catalog uses business function names, not tech abbreviations](./ADR-0f61dd.md) | implemented |  |  |  |
| `DEC-1002c9` | [MCF trust-chain resolution — concept-mediated MC→CC derivation, PE-MC-11 resolvability evidence, honest chain-green semantics](./ADR-1002c9.md) | implemented |  |  |  |
| `DEC-103528` | [SFDC Source Catalog — Salesforce native cloud grouping, CPQ deferred](./ADR-103528.md) | implemented |  |  |  |
| `DEC-103acb` | [Tenant onboarding mandatory-field policy + completeness gate (block activation until identity is complete)](./ADR-103acb.md) | decided |  |  |  |
| `DEC-116641` | [A profile is a parent manifest plus typed children — composition, not one file](./ADR-116641.md) | proposed |  |  |  |
| `DEC-12558e` | [Odoo 19 EE is a JSON-RPC Connector over http transport with an OdooJsonRpcProtocolReader executor, reusing basic auth](./ADR-12558e.md) | implemented |  |  |  |
| `DEC-129417` | [Reader consolidation — per-subfunction with system flavors](./ADR-129417.md) | superseded |  | DEC-0d5b39 |  |
| `DEC-136a23` | [Observation Contract stays reader-scoped, field_affinity is the sharing layer](./ADR-136a23.md) | decided |  |  |  |
| `DEC-1392ee` | [Demo tier — 2 weeks free on AWS Shared only](./ADR-1392ee.md) | decided |  |  |  |
| `DEC-13a260` | [Frontend SDK: amazon-cognito-identity-js (not Amplify)](./ADR-13a260.md) | implemented |  |  |  |
| `DEC-142237` | [bc-portal Design System Governance](./ADR-142237.md) | superseded |  | DEC-9a3c6a |  |
| `DEC-14592e` | [S3 Boundary Archive — WORM storage for raw payloads and detailed evidence](./ADR-14592e.md) | superseded |  | DEC-3ee0f6 |  |
| `DEC-149ab2` | [BCF Authority Delegation — Framework Approval for the Business Context Framework](./ADR-149ab2.md) | decided |  |  |  |
| `DEC-14f5b6` | [Measurement semantics for amount and quantity Business Concepts — currency is row-data, vocabulary declares the dependency](./ADR-14f5b6.md) | implemented |  |  |  |
| `DEC-14fb98` | [bc-ai uses own SQLite database, not shared with DevHub](./ADR-14fb98.md) | superseded |  | DEC-ffee4e |  |
| `DEC-162de5` | [bc-portal naming convention — one name, three places](./ADR-162de5.md) | implemented |  |  |  |
| `DEC-164830` | [DB Change Protocol — mandatory user approval for all schema changes, overrides Bypass permissions](./ADR-164830.md) | implemented |  |  |  |
| `DEC-17112b` | [UniBAT Reader Authoring Surface — Four-Layer Model, Per-Entity Observation Contract Binding & Chain-Resolvability Activation Gate](./ADR-17112b.md) | decided |  |  |  |
| `DEC-176a8e` | [Contracts are platform-only — tenant customization via contract_binding](./ADR-176a8e.md) | implemented |  |  |  |
| `DEC-177c52` | [Operational tables moved from Platform DB to Tenant DB](./ADR-177c52.md) | superseded |  |  |  |
| `DEC-1918d0` | [Deployment & Database Architecture — staging topology, DB separation, naming standard, normalization rulebook](./ADR-1918d0.md) | implemented |  |  |  |
| `DEC-192116` | [Source system tabs by business category, not transport mechanism](./ADR-192116.md) | implemented |  |  |  |
| `DEC-195bbd` | [Human-readable 4-character metric UID for MCF metric contracts](./ADR-195bbd.md) | superseded |  | DEC-3fe389 |  |
| `DEC-1ab381` | [Platform ticket system — failed runs auto-create incidents](./ADR-1ab381.md) | decided |  |  |  |
| `DEC-1ac398` | [Metric Catalog rebuild — governed attributes, panel-time enrichment, knowledge import, and the two-strip trust view](./ADR-1ac398.md) | implemented |  |  |  |
| `DEC-1b32a9` | [Canonical contracts are source-agnostic — not part of Source Chain](./ADR-1b32a9.md) | implemented |  |  |  |
| `DEC-1bad13` | [Execution schema — carve out from operations](./ADR-1bad13.md) | implemented |  |  |  |
| `DEC-1c5af4` | [Demo World Foundry is Odoo-scoped; source-generality deferred to rule-of-two](./ADR-1c5af4.md) | decided |  |  |  |
| `DEC-1cdc5e` | [Drop bc_tenant database — orphan with t_xxx schemas replaced by tbc_xxx](./ADR-1cdc5e.md) | implemented |  |  |  |
| `DEC-1ce490` | [contract.business_field is the certified BF-BO catalog](./ADR-1ce490.md) | superseded |  | DEC-b390ef |  |
| `DEC-1db1c7` | [Open-item / as-of canonical semantics — temporal projection for balance metrics](./ADR-1db1c7.md) | superseded |  | DEC-83fda0 |  |
| `DEC-1db6e9` | [Rooth: backend homed in bc-core as a config-gated module; UI stays in bc-portal](./ADR-1db6e9.md) | proposed |  |  |  |
| `DEC-1e55d3` | [Post-Activation Integrity Audit — CAS regression_audit build-out, BCF-subject lens, invariant-tagged findings, SSOT split with mcv_chain_status](./ADR-1e55d3.md) | decided |  |  |  |
| `DEC-1e9fd1` | [Observed Indicators — compositionCode 'observed' for External Reference Metrics](./ADR-1e9fd1.md) | superseded |  | DEC-9dce29 |  |
| `DEC-1edaaa` | [One Observation Contract Per System Per Reader + Source Entity Provenance on Field Map](./ADR-1edaaa.md) | implemented |  |  |  |
| `DEC-1efa47` | [Grain key-source mismatch: fiscal_period vs evaluation_period must be disambiguated](./ADR-1efa47.md) | superseded |  |  |  |
| `DEC-1f6659` | [Safe Delete Guard — Referential Integrity Check Before Any Hard Delete](./ADR-1f6659.md) | implemented |  |  |  |
| `DEC-1fa08f` | [Chain Audit Service (CAS) — read-only verifier with 5-mode lifecycle gating](./ADR-1fa08f.md) | decided |  |  |  |
| `DEC-1fbaf1` | [BCF admission-error withdrawal — archival of vocabulary admitted in error, distinct from supersession](./ADR-1fbaf1.md) | decided |  |  |  |
| `DEC-1fcbc0` | [AWS Cognito for authentication](./ADR-1fcbc0.md) | implemented |  |  |  |
| `DEC-20d545` | [Curated-content export — relational reference canonicalization (W3 increment)](./ADR-20d545.md) | proposed |  |  |  |
| `DEC-20eefe` | [Evidence as Structural Lineage — per-run summaries in RDS, detailed archive on S3](./ADR-20eefe.md) | implemented |  |  |  |
| `DEC-21ca17` | [Pre-C8 legacy-active disposition — cohort demotion to audit_pending as raw material; named residue; pre-launch stopping condition](./ADR-21ca17.md) | implemented |  |  |  |
| `DEC-22eaaf` | [bc-core serves both bc-admin and bc-portal frontends](./ADR-22eaaf.md) | implemented |  |  |  |
| `DEC-22ed4b` | [Material Master vs Product Master — distinct readers](./ADR-22ed4b.md) | implemented |  |  |  |
| `DEC-2342bf` | [Backfill and batch execution model — distinct from live observation](./ADR-2342bf.md) | decided |  |  |  |
| `DEC-2347a3` | [Filesystem-Derived Doc Registry — Single Root from mkdocs.yml + Frontmatter](./ADR-2347a3.md) | implemented |  |  |  |
| `DEC-2411e4` | [Bump self-verifier algorithm to mcf-verifier-v2: apply declared metric filter clauses during fixture playback](./ADR-2411e4.md) | decided |  |  |  |
| `DEC-242d60` | [AC Body Purity — Remove readiness_predicate](./ADR-242d60.md) | implemented |  |  |  |
| `DEC-246a24` | [Stack naming: bc-{stage}-{series}-{domain}](./ADR-246a24.md) | implemented |  |  |  |
| `DEC-24b4ec` | [Contract Registry — 7 Contract Types](./ADR-24b4ec.md) | superseded |  |  |  |
| `DEC-24f6da` | [Temporal values are absolute — cron + timezone + ISO 8601 durations](./ADR-24f6da.md) | implemented |  |  |  |
| `DEC-253be2` | [External metric audit — intrinsic vs source-realization audit-request split, per-realization claim scoping, SAP ECC as first realization-audit ground](./ADR-253be2.md) | superseded |  | DEC-b390ef |  |
| `DEC-2589d0` | [Port 4200 for bc-sdg OData server (D014 dev tools range)](./ADR-2589d0.md) | superseded |  | DEC-76aea4 |  |
| `DEC-2658ff` | [Contract-Typed Payload Tables — real columns in RDS, raw payloads archived to S3](./ADR-2658ff.md) | implemented |  |  |  |
| `DEC-26b6e2` | [Immutable Characteristic Atoms](./ADR-26b6e2.md) | decided |  |  |  |
| `DEC-26f75a` | [period_aggregate anchor_field — event-date period membership for flow metrics (temporal grammar ADR #2)](./ADR-26f75a.md) | implemented |  |  |  |
| `DEC-28741f` | [Source Contract Correction — Platform Template (Full Schema) + Observation Contract Per Flavor (Field Selection)](./ADR-28741f.md) | implemented |  |  |  |
| `DEC-28b176` | [Metric Readiness Model — three independent dials + per-formula-token audit](./ADR-28b176.md) | superseded |  | DEC-b049f6 |  |
| `DEC-291614` | [Canonical-value filters are permissible at the Metric Contract layer](./ADR-291614.md) | decided |  |  |  |
| `DEC-29477a` | [PostgreSQL schema-per-tenant](./ADR-29477a.md) | superseded |  | DEC-40c29f |  |
| `DEC-296505` | [Contamination expunge: whitelist-failing catalog rows get a governed delete path (not archive-forever)](./ADR-296505.md) | implemented |  |  |  |
| `DEC-29b518` | [Fix fail-open activation/publication gates X5/X4 (D429 Step 4)](./ADR-29b518.md) | decided |  |  |  |
| `DEC-29c324` | [Metric contracts reference N canonical objects, not one](./ADR-29c324.md) | implemented |  |  |  |
| `DEC-29c80b` | [Single-plane audit lifecycle — audit_pending before active; active means externally audited + calculator-grade](./ADR-29c80b.md) | superseded | DEC-6caf62 | DEC-793e13 |  |
| `DEC-29e378` | [BareCount project taxonomy — 7 projects](./ADR-29e378.md) | implemented |  |  |  |
| `DEC-29f134` | [Runtime Drift Detection — payload vs catalog probe, classification dispatch, S3 quarantine route, ticket lodging](./ADR-29f134.md) | decided |  |  |  |
| `DEC-2b5a82` | [Readiness assessment rules for master_data and integration](./ADR-2b5a82.md) | decided |  |  |  |
| `DEC-2bd5d6` | [Monorepo with npm workspaces](./ADR-2bd5d6.md) | superseded |  |  |  |
| `DEC-2c2849` | [MCF Reference-Dimension Grouping — group-by / top-N over a stamped reference dimension (CB-008 Component B)](./ADR-2c2849.md) | decided |  |  |  |
| `DEC-2c79c8` | [Full per-tenant SQL isolation — all boundary + evidence tables move to tenant schemas](./ADR-2c79c8.md) | superseded |  | DEC-7df811 |  |
| `DEC-2cf250` | [BareCount visual language — bare/confident/light; color as information, not decoration](./ADR-2cf250.md) | decided |  |  |  |
| `DEC-2d5418` | [Hardened meta-schema change control: batch-atomic CAS approvals, principal-bound review, DB-frozen terminal evidence, agent-author identity](./ADR-2d5418.md) | implemented |  |  |  |
| `DEC-2d5df2` | [Drop dark mode from bc-portal](./ADR-2d5df2.md) | implemented |  |  |  |
| `DEC-2dab98` | [Use postgres.js (not pg/node-postgres) as PostgreSQL driver](./ADR-2dab98.md) | implemented |  |  |  |
| `DEC-2e4cb3` | [BO/BF is organizational grouping, not computational node in contract chain](./ADR-2e4cb3.md) | superseded |  | DEC-b390ef |  |
| `DEC-2e801a` | [Lock Beyond canvas as the post-dashboard interface for bc-portal](./ADR-2e801a.md) | superseded |  | DEC-7e76b9 |  |
| `DEC-2f0967` | [CB-008 Component C — cross-entity governed selection (credit-limit utilization)](./ADR-2f0967.md) | implemented |  |  |  |
| `DEC-2f406b` | [D230 Addendum — Dossier ID scheme, frontmatter, diagrams, awesome-pages](./ADR-2f406b.md) | implemented |  |  |  |
| `DEC-3016e4` | [Fiscal-calendar window is half-open [effective_from, effective_to); the '*' calendar row is retired by refusal](./ADR-3016e4.md) | decided |  |  |  |
| `DEC-3078ce` | [Source catalog onboarding workflow — evidence-bound verification, explicit transitions, no born-approved rows](./ADR-3078ce.md) | implemented |  |  |  |
| `DEC-316f3c` | [bc-seed — Standalone Catalog Sourcing Service (MongoDB, Port 4200)](./ADR-316f3c.md) | superseded |  | DEC-b390ef |  |
| `DEC-3196eb` | [Drop operational schema — discovery to operations, connections tenant-only](./ADR-3196eb.md) | superseded |  |  |  |
| `DEC-31c212` | [MCF metric function/subfunction classification: master-authoritative, not_defined sentinel, DB-enforced](./ADR-31c212.md) | implemented |  |  |  |
| `DEC-31dc55` | [GL sign-convention and currency-declaration doctrine — ledger-signed canonical, metric-layer presentation, mandatory declarations](./ADR-31dc55.md) | implemented |  |  |  |
| `DEC-324d9e` | [Stripe Billing integration — subscription and payment management from day 1](./ADR-324d9e.md) | decided |  |  |  |
| `DEC-327d4e` | [MCF identity_tuple_hash v2 — include the computed-dimension kernel (amends hash-authority D-M7-8)](./ADR-327d4e.md) | implemented |  |  |  |
| `DEC-32a56e` | [MCF M12 Context Judge — semantic grounding via LLM, not regex](./ADR-32a56e.md) | decided |  |  |  |
| `DEC-3300f3` | [MCF authoring panel admits direct-API third-party LLMs; customer data confined to the runtime layer](./ADR-3300f3.md) | decided |  |  |  |
| `DEC-3395bc` | [v3 docs reader: drop book wrapper, drop mkdocs, flat sections under docs/](./ADR-3395bc.md) | decided |  |  |  |
| `DEC-339c97` | [External standards provenance on Business Objects and Business Fields](./ADR-339c97.md) | superseded |  | DEC-b390ef |  |
| `DEC-33d436` | [Platform Readiness & Legibility — program mandate, platform/tenant readiness split, and SSOT consolidation](./ADR-33d436.md) | decided |  |  |  |
| `DEC-351108` | [Contract-Typed Payload Tables + Reader Batch Write Model](./ADR-351108.md) | superseded |  |  |  |
| `DEC-354552` | [Reader Path Robustness + Chain Integrity Gates — fail-fast contracts, locked SOPs, end-to-end smoke gate](./ADR-354552.md) | decided |  |  |  |
| `DEC-3562a5` | [RDS-portable canonical baseline — the versioned spine applies under a non-superuser cloud principal](./ADR-3562a5.md) | accepted |  |  |  |
| `DEC-35b34b` | [Aggregation Authority — Metric Formulas Own Aggregation; cc_field_mapping.resolution_rule_code Becomes Documentary](./ADR-35b34b.md) | decided |  |  |  |
| `DEC-3628b4` | [Retire the TSK-3f52d7 schema-acquisition launcher (F7) and its acquisition execution package; close bc-core PR #746; quarantine the schema comparator core for W1.2 (D7)](./ADR-3628b4.md) | decided |  |  |  |
| `DEC-365f51` | [DevHub Housekeeping Agents — Intelligent Autonomous Platform Maintenance](./ADR-365f51.md) | superseded |  | DEC-38b354 |  |
| `DEC-36913d` | [Canonical row-arithmetic + fiscal date construction (D330/D513-additive): linear_sum and fiscal_period_end_date derivations; GL balance chain v1 at (account, fiscal year) year-end stock over GLT0](./ADR-36913d.md) | implemented |  |  |  |
| `DEC-36d78f` | [Reader Observation Schema — selective observation with standard field naming](./ADR-36d78f.md) | implemented |  |  |  |
| `DEC-375e6b` | [KPIDepot Enrichment — Classification & Formula Decomposition Rules](./ADR-375e6b.md) | implemented |  |  |  |
| `DEC-376587` | [Section rename: The Platform → Implementation](./ADR-376587.md) | decided |  |  |  |
| `DEC-376c9c` | [DevHub as separate repo + EC2](./ADR-376c9c.md) | implemented |  |  |  |
| `DEC-3785f8` | [Canonical value normalization — raw source-signal inputs to CC-body derivations; meaning is produced at the canonical boundary, never by the Reader](./ADR-3785f8.md) | implemented |  |  |  |
| `DEC-37967b` | [Function/Subfunction Taxonomy — APQC PCF Alignment Adjustments](./ADR-37967b.md) | implemented |  |  |  |
| `DEC-37ee92` | [D235: Documentation RAG Layer — Vector Retrieval from legacy v2 archive for AI Grounding and Help Assistant](./ADR-37ee92.md) | reversed |  |  |  |
| `DEC-3805f6` | [Screen Registry workflow taxonomy: split dataspace into canonical-data, evidence, data-infra](./ADR-3805f6.md) | implemented |  |  |  |
| `DEC-381254` | [Source Catalog: Admissions → Source Contracts (extraction + source + admission)](./ADR-381254.md) | superseded |  |  |  |
| `DEC-388129` | [Domain Taxonomy as Platform Master](./ADR-388129.md) | superseded |  | DEC-7bbdba |  |
| `DEC-38b354` | [Housekeeping Agents Migration — bc-ai APScheduler → Claude Code Scheduled Tasks](./ADR-38b354.md) | implemented | DEC-365f51 |  |  |
| `DEC-38c8bb` | [bc-website v2 Direction — Marketing-First, Separate Voice Register](./ADR-38c8bb.md) | decided |  |  |  |
| `DEC-39514f` | [Demo world-builder pivots to a model-driven compiler (Foundry): one typed world model, everything else a projection](./ADR-39514f.md) | decided |  |  |  |
| `DEC-3a6f74` | [Platform/Tenant: Keep single service, formalize with guard decorators](./ADR-3a6f74.md) | implemented |  |  |  |
| `DEC-3aa336` | [MCF code layout — mcf/ is the consolidated home; two strays move in, five look-alikes deliberately stay out](./ADR-3aa336.md) | implemented |  |  |  |
| `DEC-3ac7d6` | [Reader backfill configuration at flavor level](./ADR-3ac7d6.md) | decided |  |  |  |
| `DEC-3b23de` | [sandbox1 demo scenario — 3 fiscal years of real-estate AR data via bc-sdg + canonical AR slice](./ADR-3b23de.md) | superseded |  | DEC-b390ef |  |
| `DEC-3b2ff9` | [Source-system approval is a derived projection of leaf approval — the identity tier is never asserted approved](./ADR-3b2ff9.md) | implemented |  |  |  |
| `DEC-3b86ea` | [Section renames + scope cleanup: Onboarding, Operations; drop Demo Execution; move Clean Slate Migration to Upgrade and Migration](./ADR-3b86ea.md) | decided |  |  |  |
| `DEC-3c1084` | [V2 Seed Engine — dedicated, complete, AWS-ready](./ADR-3c1084.md) | superseded |  |  |  |
| `DEC-3c2917` | [Connection belongs on reader_flavor, not observation_contract](./ADR-3c2917.md) | implemented |  |  |  |
| `DEC-3cc8a1` | [Metis — AI-Driven Function CounterParts at the Intervention Boundary](./ADR-3cc8a1.md) | reversed |  |  |  |
| `DEC-3d4304` | [Source field typing for ORM/relational sources — governed data-type vocabulary + field-kind model (Odoo first)](./ADR-3d4304.md) | decided |  |  |  |
| `DEC-3d4949` | [Backend lives in separate bc-core repo](./ADR-3d4949.md) | implemented |  |  |  |
| `DEC-3d6e11` | [DAG Support in Contract JSON Shapes — Derived CO Evaluation + Secondary Metric Evaluation](./ADR-3d6e11.md) | implemented |  |  |  |
| `DEC-3d6eeb` | [External metric-correctness audit as a permanent pre-release gate — two engines, one store, signature-bound certification](./ADR-3d6eeb.md) | superseded |  | DEC-c48b0f |  |
| `DEC-3e9829` | [QA Shift-Left — Coding Standards in CLAUDE.md](./ADR-3e9829.md) | implemented |  |  |  |
| `DEC-3ee0f6` | [Per-tenant S3 archive bucket — provisioned at tenant onboarding](./ADR-3ee0f6.md) | decided | DEC-14592e |  |  |
| `DEC-3f093f` | [MCF Canonicality and Legacy Runtime Boundary](./ADR-3f093f.md) | decided |  |  |  |
| `DEC-3f4105` | [Database naming convention — _dev/_prod suffix for environment safety](./ADR-3f4105.md) | implemented |  |  |  |
| `DEC-3fc279` | [Source Landscape — per-source reference indexes, separate from Source Catalog](./ADR-3fc279.md) | superseded |  | DEC-05140c |  |
| `DEC-3fe389` | [One contract-identity doctrine: UUID authority + opaque speakable uid, no semantic names, all families](./ADR-3fe389.md) | decided | DEC-ea5074, DEC-195bbd |  |  |
| `DEC-40a68b` | [Full OData V4/V2 protocol fidelity — $metadata, $filter, $expand, $top/$skip, delta](./ADR-40a68b.md) | implemented |  |  |  |
| `DEC-40b510` | [Demo-estate simulator v2 as a product (bc-demo): two-stream architecture, clone-and-strip, release-versioned governance](./ADR-40b510.md) | decided |  |  |  |
| `DEC-40b650` | [AI-assisted catalog verification — hybrid model with gated enterprise controls](./ADR-40b650.md) | implemented |  |  |  |
| `DEC-40c29f` | [Control Plane / Data Plane DB Split — Registry to Platform, Boundary+Evidence to Tenant](./ADR-40c29f.md) | implemented |  |  |  |
| `DEC-414ba2` | [Correctly-rounded reproducibility is a distinct, labelled basis for metric audit eligibility](./ADR-414ba2.md) | implemented |  |  |  |
| `DEC-41e4bc` | [Session protocol for controllers: roster, responsibility map, work binding, review ledger, close gates, daily seal](./ADR-41e4bc.md) | decided |  |  |  |
| `DEC-422db8` | [Multi-source connector generation — not Airbyte-only, intermediate spec, risk mitigations](./ADR-422db8.md) | implemented |  |  |  |
| `DEC-42421d` | [Contract-Typed Payload Tables — known schema gets real columns, JSONB payload columns dropped](./ADR-42421d.md) | superseded |  |  |  |
| `DEC-426b24` | [Contract Creation Framework — SC + AC Entry Boundary Pattern](./ADR-426b24.md) | implemented |  |  |  |
| `DEC-4282d7` | [Admin Portal IA v3 — Catalog/Chain/AI-ML separation](./ADR-4282d7.md) | superseded |  |  |  |
| `DEC-42b9c0` | [Admin-provisioned users only (no self-signup)](./ADR-42b9c0.md) | implemented |  |  |  |
| `DEC-42ca56` | [MCP Tool Registry — scanner-derived catalog of DevHub MCP tools with side-effect metadata](./ADR-42ca56.md) | implemented |  |  |  |
| `DEC-43e93f` | [5 schema categories: extractor, source, gdp, kpi, ai](./ADR-43e93f.md) | superseded |  |  |  |
| `DEC-43fd36` | [bc-admin = Contracts view, bc-portal = Catalog view — audience-based rendering](./ADR-43fd36.md) | implemented |  |  |  |
| `DEC-441665` | [NPM supply chain mitigation via AWS CodeArtifact](./ADR-441665.md) | implemented |  |  |  |
| `DEC-44456d` | [Revive bc-external-audit as the auditor's home: exchange protocol and mailbox, auditor instructions, Mac auditor service (courier stays retired)](./ADR-44456d.md) | decided |  |  |  |
| `DEC-4472ca` | [Reader Batch Write Model — per-run operations, not per-row](./ADR-4472ca.md) | implemented |  |  |  |
| `DEC-457ed1` | [Prong (b) licensed rounding operations: any single correctly-rounded arithmetic operation](./ADR-457ed1.md) | decided |  |  |  |
| `DEC-459a9e` | [Zod v4 syntax rule for MCP tool schemas + tools/list regression guard](./ADR-459a9e.md) | implemented |  |  |  |
| `DEC-45c01b` | [BCF characteristic admission — reduce ceremony: panel M5/M6/M9 calibration (v1.1) + fast-lane APPROVE to draft](./ADR-45c01b.md) | decided |  |  |  |
| `DEC-468d01` | [Registry root layout — dead-code removal + six-folder consolidation of the loose root files (D484/D485 companion)](./ADR-468d01.md) | implemented |  |  |  |
| `DEC-46ff0a` | [D442 Amendment 1 — resolve lineage-vs-version semantic_role collision discovered at Packet 1+2 entry](./ADR-46ff0a.md) | decided |  |  |  |
| `DEC-47a4e7` | [C5 operator-driven transition expansion (operatorAdvance)](./ADR-47a4e7.md) | decided |  |  |  |
| `DEC-482fa1` | [BYO-DB portability boundary — defer the flow, hold the engine-portability invariant](./ADR-482fa1.md) | proposed |  |  |  |
| `DEC-483f1e` | [The General Metric Runtime — substrate-driven, shape-dispatched governed-selection → aggregation](./ADR-483f1e.md) | decided |  |  |  |
| `DEC-489492` | [W5 assembly rule — the bc-db spine is the platform schema authority; retire the docker/redesign modular↔monolith lockstep (amends DEC-591eb7)](./ADR-489492.md) | decided | DEC-591eb7 |  |  |
| `DEC-48d222` | [Atomic Proof for Metric Evaluation — local Evidence+Lineage join the Snapshot transaction; WORM archive best-effort (resolves FND-AUTH-001)](./ADR-48d222.md) | decided |  |  |  |
| `DEC-490520` | [PII Classification at Source Field Level — Observe at Source, Propagate Through Chain](./ADR-490520.md) | decided |  |  |  |
| `DEC-495eaf` | [AWS Target Deployment Topology — Design Now, Deploy After E2E](./ADR-495eaf.md) | implemented |  |  |  |
| `DEC-4a17e0` | [Observation Contract field-level semantic identity (sibling to DEC-a6258b; old Business Field role)](./ADR-4a17e0.md) | decided |  |  |  |
| `DEC-4a515b` | [All 4 process chains from day one — P2P, O2C, R2R, Plan-to-Produce](./ADR-4a515b.md) | implemented |  |  |  |
| `DEC-4a8abb` | [MC Constant Value Propagation — End-to-End](./ADR-4a8abb.md) | decided |  |  |  |
| `DEC-4aa2fd` | [Subscription-plan-driven contract binding automation (metric entitlement is the control surface)](./ADR-4aa2fd.md) | reversed |  |  |  |
| `DEC-4bff1c` | [Reader \"flavors\" are \"Target Sources\](./ADR-4bff1c.md) | decided |  |  |  |
| `DEC-4c1396` | [bc-db spine is the sole platform schema authoring and apply path](./ADR-4c1396.md) | decided | DEC-b1a286 |  |  |
| `DEC-4ca5a5` | [Metric Landscape — single-page UI consolidation of three overlapping metric-lifecycle surfaces](./ADR-4ca5a5.md) | superseded |  | DEC-b049f6 |  |
| `DEC-5017fe` | [Standard Field Registry — ISO 11179 MDR for observation vocabulary](./ADR-5017fe.md) | superseded |  | DEC-a17d0f |  |
| `DEC-50995f` | [Source Catalog shows system cards, not provider cards](./ADR-50995f.md) | implemented |  |  |  |
| `DEC-520b33` | [bc-admin port: 3010 (reassigned from Datajettyadminportal)](./ADR-520b33.md) | implemented |  |  |  |
| `DEC-5213e3` | [Open-source connector strategy — npm libs as transport, ReaderExecutor as containment boundary](./ADR-5213e3.md) | implemented |  |  |  |
| `DEC-523a5d` | [S/4HANA CDS View Catalog — Three Public Sources + Two Customer Access Models](./ADR-523a5d.md) | superseded |  | DEC-b390ef |  |
| `DEC-53629b` | [BCF panel roster amendment: GLM-5 (Bedrock) replaces GPT-5.5 as Moderator (amends DEC-ffee4e)](./ADR-53629b.md) | decided |  |  |  |
| `DEC-542722` | [Catalog-first metric authoring — draft MCVs are chain-independent; PE-MC-11 is the sole chain coupling](./ADR-542722.md) | decided |  |  |  |
| `DEC-545a4d` | [Numeric admission classes v2: scaled-decimal exactness + correctly-rounded reproducibility](./ADR-545a4d.md) | implemented |  |  |  |
| `DEC-54f221` | [Controlled Semantic Refactor — three-layer model (Interpretation Surfaces / Implementation Names / Compatibility Names) — supersedes DEC-7a1c98](./ADR-54f221.md) | decided | DEC-7a1c98 |  |  |
| `DEC-552ddd` | [Separate catalog_status and verification_status on source entities](./ADR-552ddd.md) | implemented |  |  |  |
| `DEC-568d0b` | [W0 coordination acknowledgement — Platform/Tenant Readiness re-affirmed (retained record, closes the W0 gate)](./ADR-568d0b.md) | decided |  |  |  |
| `DEC-57c6d9` | [Platform metric trust strip ends at Activated; tenant-runtime stages move to bc-portal](./ADR-57c6d9.md) | implemented |  |  |  |
| `DEC-57d540` | [Registry tables aligned with UinBAT Reader terminology](./ADR-57d540.md) | implemented |  |  |  |
| `DEC-5842d4` | [Metric Directory Knowledge & Governance Layer (extends D506)](./ADR-5842d4.md) | implemented |  |  |  |
| `DEC-585edb` | [OC-v2 join reduce strategy 'sum' — many→one numeric aggregation over join children](./ADR-585edb.md) | implemented |  |  |  |
| `DEC-586ccb` | [F06 Service Catalog — Catalog SVS as First Service](./ADR-586ccb.md) | implemented |  |  |  |
| `DEC-58b56c` | [First pilot source-system pair: D365 Business Central + Odoo — platform-proof over GTM optics](./ADR-58b56c.md) | decided |  |  |  |
| `DEC-58bf7f` | [Platform vs Tenant API Scope — Role-Based Middleware Bypass](./ADR-58bf7f.md) | superseded |  |  |  |
| `DEC-591eb7` | [Single modular SoT → generated platform monolith + CI parity gate vs live/golden](./ADR-591eb7.md) | superseded |  | DEC-489492 |  |
| `DEC-594211` | [Source System Simulators — Per-System-Type Synthetic Data Architecture](./ADR-594211.md) | superseded |  | DEC-76aea4 |  |
| `DEC-5a9dee` | [Foundation grammar taxonomy admits the live authority-creating families — MCF, BCF, Metric Directory — with states-plus-delegation; five-level authority ladder (F-032 disposition)](./ADR-5a9dee.md) | implemented |  |  |  |
| `DEC-5b760c` | [QA enforcement consolidates into per-repo CI; DevHub is the sole NC authority; bc-qa repo retires and archives](./ADR-5b760c.md) | decided |  |  |  |
| `DEC-5bfa81` | [bc-website Versioning — Branch Model in Single Repo](./ADR-5bfa81.md) | implemented |  |  |  |
| `DEC-5c39ea` | [Golden DB snapshot replaces seed scripts as primary dev setup method](./ADR-5c39ea.md) | implemented |  |  |  |
| `DEC-5cb154` | [M12 Panel Composition v3 + Transport-Agnostic Envelope Harvest + Pre-Adoption Canary Policy](./ADR-5cb154.md) | decided |  |  |  |
| `DEC-5cef91` | [Navigation IA v5 — Final locked structure (AUTHORITATIVE)](./ADR-5cef91.md) | implemented |  |  |  |
| `DEC-5d3f0f` | [Phase 5 route architecture refactor — do now](./ADR-5d3f0f.md) | implemented |  |  |  |
| `DEC-5d4b1b` | [bc-website v2 tech stack — Astro + React islands + Tailwind](./ADR-5d4b1b.md) | implemented |  |  |  |
| `DEC-5dfee7` | [Public data sources auto-connect without credentials; per-connector legal file](./ADR-5dfee7.md) | implemented |  |  |  |
| `DEC-5ea578` | [Metric Evaluation Boundary — Unification & Wiring (governed runtime promotion, run object, transactional idempotent act)](./ADR-5ea578.md) | implemented |  |  |  |
| `DEC-5eed17` | [Master-data seeding through the spine](./ADR-5eed17.md) | decided |  |  |  |
| `DEC-5f11f8` | [Canonical evaluation has internal layering — primary COs (from SOs) and derived COs (from other COs)](./ADR-5f11f8.md) | implemented |  |  |  |
| `DEC-5fa096` | [Landscape vs Catalog: superset/subset with promotion-approval workflow](./ADR-5fa096.md) | superseded |  |  |  |
| `DEC-5fd322` | [Observation Contract is the central design-time artifact, readers are runtime executors](./ADR-5fd322.md) | implemented |  |  |  |
| `DEC-615b87` | [Intervention contract — 6th contract family in platform contract schema](./ADR-615b87.md) | implemented |  |  |  |
| `DEC-615cbd` | [Operator-backed U7 staging-cloud unit CANCELLATION (revokes RESPONSE-450 staging authority; zero-orphan verified)](./ADR-615cbd.md) | decided |  |  |  |
| `DEC-616e02` | [Business Object Model — independent canonical entity definitions as contract infrastructure](./ADR-616e02.md) | superseded |  | DEC-b390ef |  |
| `DEC-61850f` | [D441 Foundation-shape lock — BC semantic_role + canonical_value_set storage](./ADR-61850f.md) | implemented |  |  |  |
| `DEC-61f7c8` | [MCF Clean Single Published Metric-Contract Store (amends D426)](./ADR-61f7c8.md) | decided |  |  |  |
| `DEC-623f8f` | [ADR Hygiene Policy — closure process for the 351-ADR registry](./ADR-623f8f.md) | decided |  |  |  |
| `DEC-625d0b` | [Reader contract readiness: bound flavors / total flavors](./ADR-625d0b.md) | implemented |  |  |  |
| `DEC-633b2a` | [D-code monotonic allocator - prevent concurrent-session drift](./ADR-633b2a.md) | implemented |  |  |  |
| `DEC-637072` | [Derived Canonical Fields — Compute Rules in CC Field Mapping](./ADR-637072.md) | superseded |  | DEC-b390ef |  |
| `DEC-64ad7c` | [Company-scoped canonical party names for cross-company duplicates (supersedes shared party master)](./ADR-64ad7c.md) | decided | DEC-e4eb7c |  |  |
| `DEC-65dc86` | [BCF is the forward governance model for business meaning; BF/BO is legacy compatibility](./ADR-65dc86.md) | decided |  |  |  |
| `DEC-6636ae` | [Canonical derivation 'group_sum_where' — grain-group-scoped conditional aggregation for co-located plan/actual fields](./ADR-6636ae.md) | implemented |  |  |  |
| `DEC-663a46` | [BCF metric-seed-driven characteristic discovery — broadened admission evidence + base-vs-derived gate](./ADR-663a46.md) | decided |  |  |  |
| `DEC-66d3ca` | [BC-Agent on-premises appliance tier deferred from the Platform DB Foundation Program and tenant onboarding](./ADR-66d3ca.md) | decided |  |  |  |
| `DEC-67a7df` | [Contract TESTING lifecycle stage with a governed delete disposition](./ADR-67a7df.md) | decided |  |  |  |
| `DEC-67f399` | [Metric Directory class doctrine — base/derived only, hybrid forbidden](./ADR-67f399.md) | decided |  |  |  |
| `DEC-683cf3` | [Business Object tiers — basic (business events) vs derived (accounting artifacts)](./ADR-683cf3.md) | superseded |  | DEC-b390ef |  |
| `DEC-68f2c7` | [company_code is a shared dimension BF (5th D292 exception)](./ADR-68f2c7.md) | superseded |  | DEC-b390ef |  |
| `DEC-69a24a` | [Foundation Boundary Precision — tighten conceptual model to match implementation reality](./ADR-69a24a.md) | decided |  |  |  |
| `DEC-69f09e` | [ISO 11179 Technical Naming Standard — all internal technical names](./ADR-69f09e.md) | implemented |  |  |  |
| `DEC-6a1b47` | [Add OER flavor as second exchange rate source to prove CO convergence](./ADR-6a1b47.md) | decided |  |  |  |
| `DEC-6a9777` | [Inline ownerJson retained — owner_assignment table deferred until RBAC owner queries needed](./ADR-6a9777.md) | decided |  |  |  |
| `DEC-6b35e0` | [Source vocabulary discipline at the Metric Contract boundary](./ADR-6b35e0.md) | implemented |  |  |  |
| `DEC-6bc7ef` | [Graph DB for lineage, bindings, and contract relationships](./ADR-6bc7ef.md) | implemented |  |  |  |
| `DEC-6be41d` | [DevHub credential map and credential-rotation helper: credentials stay in AWS Secrets Manager, never in DevHub](./ADR-6be41d.md) | decided |  |  |  |
| `DEC-6c1bd2` | [system_type_code on source_system, not source_provider](./ADR-6c1bd2.md) | implemented |  |  |  |
| `DEC-6c57e2` | [Legacy Vocabulary Stack Quarantine — BF/BO/CF/CM physically retained, semantically non-authoritative](./ADR-6c57e2.md) | decided |  |  |  |
| `DEC-6caf62` | [Calculator-grade release plane — external audit gates active→released via a two-pointer release-admission plane](./ADR-6caf62.md) | superseded |  | DEC-29c80b |  |
| `DEC-6cb4f3` | [Source Systems documentation framework (bc-docs-v3)](./ADR-6cb4f3.md) | implemented |  |  |  |
| `DEC-6cdceb` | [bc-portal surface split — Beyond (viewing) + Settings/Workspace + Settings/Data Infra (plumbing)](./ADR-6cdceb.md) | superseded | DEC-04dade | DEC-c562d5 |  |
| `DEC-6d8be5` | [D225: Bottom-Up Canonical Chain Generation from Metric Formula Variables](./ADR-6d8be5.md) | superseded |  | DEC-f1dae0 |  |
| `DEC-6edbe3` | [D409 catalog factory — four-stage division of labor (Rules shortlist → AI panel → Endpoint gates → Operator approval)](./ADR-6edbe3.md) | decided |  |  |  |
| `DEC-6ee36c` | [Metric discipline taxonomy — function sub-grouping on metric_definition](./ADR-6ee36c.md) | implemented |  |  |  |
| `DEC-6f5199` | [D226: bc-docs Restructuring — Essentials/Domains/Tier Documentation Model](./ADR-6f5199.md) | superseded |  | DEC-b80330 |  |
| `DEC-6f7d38` | [Fresh bc-admin repo — Datajettyadminportal stays as Figma reference](./ADR-6f7d38.md) | implemented |  |  |  |
| `DEC-6fc629` | [Build All Custom UinBAT Readers — No Airbyte Runtime Dependency](./ADR-6fc629.md) | implemented |  |  |  |
| `DEC-6fd09d` | [Evaluation-context inputs: metric variables that take governed fiscal-calendar facts (calendar_context), and fiscal-period rolling windows](./ADR-6fd09d.md) | decided |  |  |  |
| `DEC-70573b` | [Navigation IA v4 — Source Catalog, Source Chain, Canonical Map, Metric Chain](./ADR-70573b.md) | superseded |  |  |  |
| `DEC-705f76` | [bc-portal Naming Convention](./ADR-705f76.md) | superseded |  | DEC-162de5 |  |
| `DEC-71c50d` | [Universal Protocol Readers — Connector Reclassification & Onboarding-Embedded Provisioning](./ADR-71c50d.md) | superseded |  |  |  |
| `DEC-72d723` | [Editorial Amendment of Active Characteristic Definitions — Refinement of DEC-26b6e2](./ADR-72d723.md) | decided |  |  |  |
| `DEC-731c15` | [Pilot source-infra pre-staging workstream — BC + Odoo on AWS, build-prove-hibernate; parallel to platform, metric-independent](./ADR-731c15.md) | decided |  |  |  |
| `DEC-737b58` | [Developer Guides — per-repo codebase guides and code reviews in dev-guides/](./ADR-737b58.md) | implemented |  |  |  |
| `DEC-739207` | [Information Architecture v3 — Contracts group, Scoping removed, nav reorder](./ADR-739207.md) | superseded |  |  |  |
| `DEC-739e23` | [Chain Enrichment Engine (CEE) v0 — planner-only over harness v1.1 governed-apply](./ADR-739e23.md) | decided |  |  |  |
| `DEC-743186` | [Tenant Business Data PII Detection — Source Catalog Field-Level Marking](./ADR-743186.md) | implemented |  |  |  |
| `DEC-75cb8a` | [Machine-enforced metric-authoring drift guard — two layers: bc-core deterministic gates (authority) + DevHub MCP preflight/orchestrator (ergonomics)](./ADR-75cb8a.md) | implemented |  |  |  |
| `DEC-75fc71` | [Platform DB Foundation Program — mandate (execute ADR-b1a286's waves and extend the discipline to tenant databases, object stores, durability, credentials and capacity)](./ADR-75fc71.md) | decided |  |  |  |
| `DEC-762336` | [Contract Chain Reconciliation — 3 active chains + AI provisional, 4 execution boundaries](./ADR-762336.md) | implemented | DEC-ac05fc |  |  |
| `DEC-7696ea` | [D315 — Metric Evaluation Verification Framework](./ADR-7696ea.md) | implemented |  |  |  |
| `DEC-76a91b` | [Cloud-agnostic architecture — no cloud vendor lock-in](./ADR-76a91b.md) | decided |  |  |  |
| `DEC-76aea4` | [Supplement to the legacy-doctrine supersession register (DEC-b390ef) — 3 bc-sdg/SAP ADRs missed by the 2026-08-23 sweep](./ADR-76aea4.md) | decided | DEC-b0839a, DEC-594211, DEC-2589d0 |  |  |
| `DEC-771baf` | [Tenant Database Architecture — 4 schemas, platform→tenant one-way dependency, all contracts platform-owned](./ADR-771baf.md) | implemented |  |  |  |
| `DEC-77f4b5` | [Demo-to-Contract Strategy — Synthetic Data Hook + SAP Licensing Gate](./ADR-77f4b5.md) | superseded |  | DEC-b390ef |  |
| `DEC-7896b2` | [DQC Integration — Global QC Rulebook as Foundation F04, Three-Tier Rule Model for AC](./ADR-7896b2.md) | implemented |  |  |  |
| `DEC-78b437` | [Email OTP MFA deferred — TOTP retained with UX improvements](./ADR-78b437.md) | implemented |  |  |  |
| `DEC-793e13` | [Retire the external metric-audit exchange; metric audit collapses into bc-core as self-certification](./ADR-793e13.md) | decided | DEC-29c80b |  |  |
| `DEC-794023` | [Scoped lift of the D555 OC/CC-authoring hold for the finance/Odoo lane; metric activation stays certification-gated](./ADR-794023.md) | decided |  |  |  |
| `DEC-79b62f` | [The Foundation gate: the repair-location vocabulary, the four pre-action questions, the hard rules and the override path](./ADR-79b62f.md) | proposed |  |  |  |
| `DEC-7a18af` | [Source field capability is empirically probed and stored in a source_field_capability satellite — never derived from type](./ADR-7a18af.md) | proposed |  |  |  |
| `DEC-7a1c98` | [Vocabulary Lock for the Opaque Workflow-Code Family — MMS / MCF doctrinal renaming policy](./ADR-7a1c98.md) | superseded |  | DEC-54f221 |  |
| `DEC-7a8cbc` | [Binding-realized issuer identity: a source-key component on the pinned primary leg may realize an identity-bearing issuer reference whose canonical value is the binding-resolved legal-entity code (amends DEC-a57eb8)](./ADR-7a8cbc.md) | decided |  |  |  |
| `DEC-7ab22b` | [MCF-materialized metrics governed by MCF M13/M14, not legacy D305 chain_status](./ADR-7ab22b.md) | implemented |  |  |  |
| `DEC-7b15c7` | [Pause MCF materialization until contract governance hardening completes](./ADR-7b15c7.md) | decided |  |  |  |
| `DEC-7bbdba` | [4-Level KPI Taxonomy: Industry Category → Industry → Business Function → Business Sub-function](./ADR-7bbdba.md) | implemented |  |  |  |
| `DEC-7bccf6` | [Retire platform-computed FX conversion — the source's own booked conversion is authoritative](./ADR-7bccf6.md) | decided | DEC-f6527b |  |  |
| `DEC-7bdd03` | [Guard the legacy Metric Contract authoring door (D429 Step 3)](./ADR-7bdd03.md) | decided |  |  |  |
| `DEC-7c4c39` | [Source Catalog Status Lifecycle — 4-state catalog_status](./ADR-7c4c39.md) | implemented |  |  |  |
| `DEC-7d0116` | [Frontend is React 18 + Vite, not Angular](./ADR-7d0116.md) | implemented |  |  |  |
| `DEC-7d2f8c` | [D461 derivation home — canonical-boundary 1-hop derived fields; cross-concept comparison at the metric boundary (corrects DEC-bc6be2 observation-boundary mechanism + design-doc L2/L3)](./ADR-7d2f8c.md) | implemented |  |  |  |
| `DEC-7df811` | [Tenant onboarding state model and isolation model](./ADR-7df811.md) | decided | DEC-2c79c8 |  |  |
| `DEC-7e3779` | [Source Catalog Dual-System Strategy — ECC Primary, S/4HANA Overlay](./ADR-7e3779.md) | superseded |  | DEC-b390ef |  |
| `DEC-7e76b9` | [Retire v2 dashboards entirely — single Beyond surface, no toggle](./ADR-7e76b9.md) | superseded | DEC-2e801a | DEC-c562d5 |  |
| `DEC-7eec2e` | [Chain-based navigation for bc-admin v1.0.0](./ADR-7eec2e.md) | implemented |  |  |  |
| `DEC-7f2e73` | [MCF Reference-Stamping — edge-resolved reference attributes on the Canonical Object (customer-axis Component A)](./ADR-7f2e73.md) | decided |  |  |  |
| `DEC-7f9597` | [Rulebook-first execution stance — reduce ceremony, not standards](./ADR-7f9597.md) | decided |  |  |  |
| `DEC-804874` | [Persisted L-node verification with semantic-family classification](./ADR-804874.md) | superseded |  | DEC-b390ef |  |
| `DEC-80eade` | [Legacy metric corpus retirement — single MCF corpus, bc-core re-points, W5 drops](./ADR-80eade.md) | implemented |  |  |  |
| `DEC-81cd26` | [Connections are platform-scoped — reverse D163 for connection tables](./ADR-81cd26.md) | implemented |  |  |  |
| `DEC-824ae2` | [Data Sources UI — redesign from execution model, not pipeline thinking](./ADR-824ae2.md) | implemented |  |  |  |
| `DEC-826390` | [Platform DB machinery home: dedicated repository bc-db (DB as a product)](./ADR-826390.md) | decided |  |  |  |
| `DEC-8391fd` | [Cross-Model Architecture Audit — Gemini Deep Research (4-Pass)](./ADR-8391fd.md) | implemented |  |  |  |
| `DEC-83fda0` | [Route B — As-of/Stock/Balance metrics via open-item canonical (postings−clearings netting) + unified temporal-gate grammar](./ADR-83fda0.md) | implemented | DEC-c012c0, DEC-1db1c7 |  |  |
| `DEC-85565c` | [D316 — Metric Readiness Scheduler](./ADR-85565c.md) | implemented |  |  |  |
| `DEC-855b77` | [TanStack Query for server state](./ADR-855b77.md) | implemented |  |  |  |
| `DEC-856d61` | [Split RegistryModule into 6 domain modules](./ADR-856d61.md) | decided | DEC-a5df75 |  |  |
| `DEC-8570d4` | [Source-System Docket structure — folder-per-system co-located onboarding bundle (extends D385)](./ADR-8570d4.md) | decided |  |  |  |
| `DEC-861a88` | [Providers are status-free containers — lifecycle lives on systems](./ADR-861a88.md) | reversed |  |  |  |
| `DEC-8672d0` | [Conformed dimension tables (dim_*) as platform SSOT for grain](./ADR-8672d0.md) | implemented |  |  |  |
| `DEC-87ab35` | [18-month backfill covering 2 full fiscal years (April 2024 — September 2025)](./ADR-87ab35.md) | decided |  |  |  |
| `DEC-8849c8` | [AC/OC declare semantic preconditions in the contract — the Scanner verifies declarations, never invents them](./ADR-8849c8.md) | decided |  |  |  |
| `DEC-88870a` | [Source-catalog admission scope: only real source objects; non-table models are contamination, rejected at admission](./ADR-88870a.md) | decided |  |  |  |
| `DEC-889238` | [MC Envelope Governance — deduplication policy](./ADR-889238.md) | decided |  |  |  |
| `DEC-890417` | [pm2 for multi-project dev service management](./ADR-890417.md) | superseded |  | DEC-9b23a7 |  |
| `DEC-8a6acb` | [SC Body Purity — Remove extraction_rules and effective_period](./ADR-8a6acb.md) | implemented |  |  |  |
| `DEC-8b17b1` | [Demo estates, not pilots: few-deep flagships per (domain × geography), Odoo-base, isolated per install](./ADR-8b17b1.md) | decided |  |  |  |
| `DEC-8ba0ea` | [Onboarding lifecycle-state SSOT = bc-core; DevHub onboarding is a thin planning view (D501-sibling; amends D494)](./ADR-8ba0ea.md) | decided |  |  |  |
| `DEC-8c232d` | [Metric Catalog: 2-page flat navigation, drop domain/module drill-down](./ADR-8c232d.md) | implemented |  |  |  |
| `DEC-8c489b` | [Evidence as Structural Lineage — FK chain IS the evidence, no separate evidence table](./ADR-8c489b.md) | superseded |  |  |  |
| `DEC-8cbae7` | [bc-portal Design System Governance — canonical source, token rule, component registry](./ADR-8cbae7.md) | superseded |  | DEC-9a3c6a |  |
| `DEC-8d180b` | [Three-Level Source Model — Source System / Connector Type / Connection](./ADR-8d180b.md) | implemented |  |  |  |
| `DEC-8dc51d` | [bc-portal: resolve x-tenant-id from JWT claim at runtime, not from build-time env](./ADR-8dc51d.md) | decided |  |  |  |
| `DEC-8e5f5a` | [Canonical classification: multi-input classify compute in CcV2CanonicalResolverService](./ADR-8e5f5a.md) | decided |  |  |  |
| `DEC-8e857a` | [Design-system screen consolidation: 42 individual demos → 13 section pages](./ADR-8e857a.md) | implemented |  |  |  |
| `DEC-8eb2b4` | [Execution schema carved from operations for boundary aggregation](./ADR-8eb2b4.md) | implemented |  |  |  |
| `DEC-8f09d9` | [Restore Computation Grain to Metric Contract Body](./ADR-8f09d9.md) | implemented |  |  |  |
| `DEC-908548` | [Track-C hold condition satisfied by D541 successor state — release Odoo SC/AC + source soft-references; ratify Odoo-first sequencing](./ADR-908548.md) | decided |  |  |  |
| `DEC-908a69` | [registerSourceStack authors OVER the admitted catalog — no catalog creation, object_type='table' gate](./ADR-908a69.md) | implemented |  |  |  |
| `DEC-909e64` | [Tenant DB: single schema per tenant, no sub-schemas](./ADR-909e64.md) | superseded |  | DEC-771baf |  |
| `DEC-90faff` | [Canonical-Driven Reader Creation Flow — Top-Down Assembly of the BareCount Machine](./ADR-90faff.md) | implemented |  |  |  |
| `DEC-912f4f` | [Cognito-managed TOTP MFA (optional, admin-enforceable)](./ADR-912f4f.md) | implemented |  |  |  |
| `DEC-9361cd` | [CC Field Mapping: 1-BF-to-Many-CFs + Filter + Canonical Uniqueness](./ADR-9361cd.md) | superseded |  | DEC-b390ef |  |
| `DEC-938450` | [Universal Two-Layer Contract Scoping — Platform Master + Tenant Instance](./ADR-938450.md) | superseded |  | DEC-176a8e |  |
| `DEC-9428e0` | [BCF code layout — consolidate the bcf-* module family under src/registry/bcf/](./ADR-9428e0.md) | implemented |  |  |  |
| `DEC-952faa` | [Metric Temporality Class & Inspector — close the semantic gap and lock a first-class trust surface](./ADR-952faa.md) | decided |  |  |  |
| `DEC-95687d` | [Typed-First Tenant Runtime — Schema Provisioner as declarative reconciler, connector onboarding as primary trigger, S3 WORM as the only opaque-payload store](./ADR-95687d.md) | implemented | DEC-a25931 |  |  |
| `DEC-957fb0` | [Editorial rebind evidence handling — PE-MC carry-forward](./ADR-957fb0.md) | decided |  |  |  |
| `DEC-958d3a` | [Platform-readiness engine-conformance is satisfied by compositional CI evidence; the single continuous end-to-end run is reclassified to tenant-readiness (governance is interlocked)](./ADR-958d3a.md) | decided |  |  |  |
| `DEC-96cc78` | [Platform Runtime/Operations surfaces are tenant-attributed; admission-run records stay platform metadata](./ADR-96cc78.md) | decided |  |  |  |
| `DEC-973363` | [E2E Execution Flow — Step-by-Step Runbook](./ADR-973363.md) | superseded |  | DEC-1edaaa |  |
| `DEC-97445d` | [Feed-epoch supersession: successor enforcement feed after transport-ledger divergence (enforcement-2 cut)](./ADR-97445d.md) | implemented |  |  |  |
| `DEC-974ff3` | [Source-Chain Contract Binding Model & Meta-Schema Correction](./ADR-974ff3.md) | superseded |  |  |  |
| `DEC-97bb94` | [Canonical Object resolves N Source Objects — multi-source canonical evaluation](./ADR-97bb94.md) | implemented |  |  |  |
| `DEC-98871b` | [D268 Structured Self-Audit — session close enforces structured discipline report + backend stats](./ADR-98871b.md) | implemented |  |  |  |
| `DEC-9a3c6a` | [bc-portal Design System governance](./ADR-9a3c6a.md) | implemented |  |  |  |
| `DEC-9a5dc0` | [CF Boundary — Reporting Standards Promote to Canonical Fields](./ADR-9a5dc0.md) | superseded |  | DEC-b390ef |  |
| `DEC-9ab097` | [Metric Catalog: flat table, not card catalog](./ADR-9ab097.md) | implemented |  |  |  |
| `DEC-9b23a7` | [Remove pm2 — independent service startup](./ADR-9b23a7.md) | implemented | DEC-890417 |  |  |
| `DEC-9b2e64` | [Curated-content promotion — scope disposition (a product decision to close the wave at the governed vocabulary)](./ADR-9b2e64.md) | decided |  |  |  |
| `DEC-9bffcd` | [BF-SF aliases as relational table, not JSONB](./ADR-9bffcd.md) | superseded |  | DEC-b390ef |  |
| `DEC-9c0da7` | [Runtime Doctrine — four engines, trigger modes, run lifecycle, period close, dry-run, campaigns (Runtime Spine R0)](./ADR-9c0da7.md) | decided |  |  |  |
| `DEC-9c430b` | [Tax semantics — tenant tax-registration model + canonical tax-type classification (observe/classify/measure, not a tax engine)](./ADR-9c430b.md) | decided |  |  |  |
| `DEC-9c58c6` | [Article-drop refinement: 'The Operating Model' → 'Operating Model' in label positions](./ADR-9c58c6.md) | decided |  |  |  |
| `DEC-9c5dbe` | [Operations group removed — ops monitoring lives on Dashboard + object detail pages](./ADR-9c5dbe.md) | implemented |  |  |  |
| `DEC-9d1f4b` | [Shared Dimension Normalization in CC Field Selection](./ADR-9d1f4b.md) | decided |  |  |  |
| `DEC-9d27a9` | [BCF supersession-cascade: fail-closed guard on supersede + systematic consumer remediation](./ADR-9d27a9.md) | implemented |  |  |  |
| `DEC-9d7a5c` | [OLS Failure Vocabulary — registry shape, namespace discipline, definitions-vs-occurrences split, seeded codes](./ADR-9d7a5c.md) | decided |  |  |  |
| `DEC-9dce29` | [Metric Specification Framework — 5-Dimensional Classification](./ADR-9dce29.md) | implemented | DEC-1e9fd1 |  |  |
| `DEC-9dd4eb` | [Operator formal acceptance — Platform DB Foundation program CLOSURE (W0/W2 dispositioned)](./ADR-9dd4eb.md) | decided |  |  |  |
| `DEC-9e0cd0` | [Contract-Typed Payload Tables — known schema gets real columns, not JSONB](./ADR-9e0cd0.md) | superseded |  |  |  |
| `DEC-9e68e0` | [Period close is an idempotent act on (company, period), not a step inside the backfill driver](./ADR-9e68e0.md) | proposed |  |  |  |
| `DEC-9eb783` | [Pin all dependency versions exactly — no caret/tilde ranges](./ADR-9eb783.md) | decided |  |  |  |
| `DEC-9ec48f` | [Six customer profiles across industries — configurable company simulation](./ADR-9ec48f.md) | implemented |  |  |  |
| `DEC-9f7c18` | [D531 authority caps are origin-scoped: not applicable to panel-origin certification payloads, retained for external-evidence origins](./ADR-9f7c18.md) | implemented |  |  |  |
| `DEC-9f801c` | [Connector tenant usage: read-only visibility in platform admin](./ADR-9f801c.md) | implemented |  |  |  |
| `DEC-9f8c13` | [Contract Registry — dedicated menu group with per-type surfaces](./ADR-9f8c13.md) | implemented |  |  |  |
| `DEC-a0e92e` | [Contract Requirements Correction + Master Shape as Unified Artifact](./ADR-a0e92e.md) | implemented |  |  |  |
| `DEC-a1110e` | [Support schema — internal ticketing for platform & tenant issues](./ADR-a1110e.md) | implemented |  |  |  |
| `DEC-a1290e` | [v3 tenant metric read surface (/beyond) is MCF-native, not a legacy bridge](./ADR-a1290e.md) | decided |  |  |  |
| `DEC-a17d0f` | [Semantic Definitions Authority for governed vocabulary primitives](./ADR-a17d0f.md) | superseded | DEC-5017fe, DEC-d72560 | DEC-02f5a9 |  |
| `DEC-a19428` | [Pre-production Legacy Active-Runtime Retirement — authorize archival ahead of MCF re-authoring; preserve carve-outs](./ADR-a19428.md) | implemented |  |  |  |
| `DEC-a25931` | [JSONB-first for boundary payloads, typed tables immediately after via D210](./ADR-a25931.md) | superseded |  | DEC-95687d |  |
| `DEC-a280da` | [Process Auditor Agent — Gemini-Powered Independent Session Governance](./ADR-a280da.md) | implemented |  |  |  |
| `DEC-a2af9e` | [Single Cognito User Pool with custom:tenant_id](./ADR-a2af9e.md) | implemented |  |  |  |
| `DEC-a466c5` | [NestJS for backend API](./ADR-a466c5.md) | implemented |  |  |  |
| `DEC-a49413` | [SDA Phase 1 implementation profile: CF semantic_family classification with multi-vendor advisory panel](./ADR-a49413.md) | superseded |  | DEC-02f5a9 |  |
| `DEC-a4e550` | [Documentation Registry in DevHub + Standard ADR File Format](./ADR-a4e550.md) | implemented |  |  |  |
| `DEC-a537bf` | [Cognito JWT end-to-end token strategy](./ADR-a537bf.md) | implemented |  |  |  |
| `DEC-a560bf` | [Platform DB never queries tenant DB — orchestrator pushes summaries](./ADR-a560bf.md) | implemented |  |  |  |
| `DEC-a57eb8` | [BareCount is not a system of record: canonical record identity is the faithful carry of the source's complete record key; the reporting fiscal period is a derived dimension, never identity](./ADR-a57eb8.md) | decided | DEC-f4e9a0 |  |  |
| `DEC-a5df75` | [Contract Registry — separate service vs API monolith](./ADR-a5df75.md) | superseded |  | DEC-856d61 |  |
| `DEC-a6258b` | [Canonical Contract field-level semantic identity (implements DEC-02f5a9 schema-key)](./ADR-a6258b.md) | decided |  |  |  |
| `DEC-a67518` | [Tenant Onboarding Gate — checklist-based readiness for BYO-DB and BC-Agent tiers](./ADR-a67518.md) | decided |  |  |  |
| `DEC-a67bae` | [Locked lane taxonomy — L1–L10 boundaries, not-a-lane register, retirement list (amends D581)](./ADR-a67bae.md) | decided |  |  |  |
| `DEC-a6cdae` | [Metric program split: chain-readiness (per-metric) vs data-readiness (SDG table-level program)](./ADR-a6cdae.md) | decided |  |  |  |
| `DEC-a7c0f9` | [Canonical Resolution — Run-scoped, multi-SO, CO DAG support](./ADR-a7c0f9.md) | implemented |  |  |  |
| `DEC-a7f3d2` | [Contract Chain Invariants — Machine-Checkable Integrity Rules](./ADR-chain-invariants.md) | implemented |  |  | non-canonical filename |
| `DEC-a7fe72` | [Finance Package v0 — scope lock, gold-universe planning SSOT, and execution sequence](./ADR-a7fe72.md) | decided |  |  |  |
| `DEC-a8b33e` | [Metric Lifecycle Funnel — canonical 7-stage ladder + single-service ownership](./ADR-a8b33e.md) | superseded |  | DEC-b049f6 |  |
| `DEC-a8e8fc` | [CC declares posting_date_field; canonical resolution enriches payload with fiscal_period + fiscal_year](./ADR-a8e8fc.md) | implemented |  |  |  |
| `DEC-aa286c` | [Multi-binding MC evaluation end-to-end](./ADR-aa286c.md) | implemented |  |  |  |
| `DEC-aa6251` | [Contract Primitives — BO and BF as First-Class Governed Artifacts](./ADR-aa6251.md) | superseded |  | DEC-b390ef |  |
| `DEC-ab0b7c` | [bc-admin stack: React 18 + Vite + Radix UI + TailwindCSS v4 (same as bc-portal)](./ADR-ab0b7c.md) | implemented |  |  |  |
| `DEC-ab1546` | [Shared types via @barecount/types npm package](./ADR-ab1546.md) | reversed |  |  |  |
| `DEC-ac05fc` | [Three contract chains: Source → Metric → AI (layered, feed-forward)](./ADR-ac05fc.md) | superseded |  | DEC-762336 |  |
| `DEC-acce2b` | [CC-v2 canonical resolution engine — runtime SO→CO for field_selection contracts (replaces canonical_mapping resolver)](./ADR-acce2b.md) | implemented |  |  |  |
| `DEC-ace519` | [Tech stack: Node.js + TypeScript + PostgreSQL + Fastify + Drizzle](./ADR-ace519.md) | implemented |  |  |  |
| `DEC-ad76e9` | [Three-Phase Tenant Onboarding — instant value, gap closure, consulting](./ADR-ad76e9.md) | implemented |  |  |  |
| `DEC-ada203` | [Composite (metric-of-metrics) evaluation — resolve upstream snapshots + reuse the formula engine](./ADR-ada203.md) | decided |  |  |  |
| `DEC-ada431` | [Source Category — Reader/Provider trust-tier classification](./ADR-ada431.md) | implemented |  |  |  |
| `DEC-ade703` | [Drop monorepo — single-project NestJS for bc-core](./ADR-ade703.md) | implemented |  |  |  |
| `DEC-adeba8` | [Connector category: external_source for non-operational reference data sources](./ADR-adeba8.md) | implemented |  |  |  |
| `DEC-ae0d33` | [Source contracts pivot on SO Detail page, not standalone nav](./ADR-ae0d33.md) | superseded |  |  |  |
| `DEC-ae331f` | [Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria](./ADR-ae331f.md) | decided |  |  |  |
| `DEC-af8247` | [Cross-domain metric scope and tenant applicability policy](./ADR-af8247.md) | decided |  |  |  |
| `DEC-afdb59` | [BareCount Component Architecture Diagram — canonical reference](./ADR-afdb59.md) | implemented |  |  |  |
| `DEC-affb24` | [17 shared services as NestJS modules in bc-core](./ADR-affb24.md) | implemented |  |  |  |
| `DEC-b049f6` | [MCF-native readiness projection replaces the legacy metric funnel, dials, and Landscape source — F-021/F-023 disposition](./ADR-b049f6.md) | implemented | DEC-a8b33e, DEC-28b176, DEC-4ca5a5 |  |  |
| `DEC-b0839a` | [SDG Coherent Snapshots and Multi-Projection Architecture](./ADR-b0839a.md) | superseded |  | DEC-76aea4 |  |
| `DEC-b10dad` | [Exchange Rate Reader: One reader, flavor-detected, source-specific contracts](./ADR-b10dad.md) | implemented |  |  |  |
| `DEC-b1a286` | [Database bootstrap source-of-truth model](./ADR-b1a286.md) | superseded |  | DEC-4c1396 |  |
| `DEC-b1e9eb` | [Metric output declaration: unit of measure, decimal places and rounding, with currency only for monetary output](./ADR-b1e9eb.md) | proposed |  |  |  |
| `DEC-b228ec` | [Two independent trees: Source Catalog and Integration — contracts reference provider](./ADR-b228ec.md) | implemented |  |  |  |
| `DEC-b28b13` | [Connector lifecycle: status enum replaces available boolean](./ADR-b28b13.md) | implemented |  |  |  |
| `DEC-b2da18` | [bc-portal Architecture and Patterns](./ADR-b2da18.md) | superseded |  | DEC-04dade |  |
| `DEC-b36558` | [Operational config and connections are tenant-scoped, not on reader definition](./ADR-b36558.md) | implemented |  |  |  |
| `DEC-b390ef` | [Legacy-doctrine supersession register — retired-design ADRs formally superseded by family](./ADR-b390ef.md) | decided | DEC-1ce490, DEC-2e4cb3, DEC-339c97, DEC-616e02, DEC-683cf3, DEC-68f2c7, DEC-9361cd, DEC-9bffcd, DEC-aa6251, DEC-b8ec00, DEC-c338b3, DEC-f1dae0, DEC-f66378, DEC-9a5dc0, DEC-b7affa, DEC-637072, DEC-010bf9, DEC-523a5d, DEC-77f4b5, DEC-7e3779, DEC-b51b48, DEC-d2cdb9, DEC-d53320, DEC-d5c352, DEC-e93a19, DEC-fc41a3, DEC-076521, DEC-e9294b, DEC-bebaec, DEC-804874, DEC-253be2, DEC-3b23de, DEC-316f3c |  |  |
| `DEC-b39a00` | [bc-admin Platform Audit — Menu Restructure, Tenant Group, TopBar+LeftBar Layout](./ADR-b39a00.md) | decided |  |  |  |
| `DEC-b51b48` | [SAP Landscape Scanner — connector-level discovery + compatibility report](./ADR-b51b48.md) | superseded |  | DEC-b390ef |  |
| `DEC-b54a43` | [Core chain consolidation: canonical context/onboarding/execution/store path, mark-don't-delete cleanup, core-then-tenant sequencing](./ADR-b54a43.md) | decided |  |  |  |
| `DEC-b5631b` | [Field Data Type Quality Gate — Mandatory Validation at AI Verify and Registration](./ADR-b5631b.md) | implemented |  |  |  |
| `DEC-b5bedb` | [Execution run tables for all 4 evaluation boundaries](./ADR-b5bedb.md) | implemented |  |  |  |
| `DEC-b5c7ff` | [Metric Directory — realized value-organizing subsystem (bc-core)](./ADR-b5c7ff.md) | decided | DEC-f90ba3 |  |  |
| `DEC-b7349d` | [Reader execution: dev in-process, prod Fargate — no infra planning needed now](./ADR-b7349d.md) | decided |  |  |  |
| `DEC-b79d16` | [Source docs at bc-docs/sources/ (root level, not architecture/)](./ADR-b79d16.md) | implemented |  |  |  |
| `DEC-b7affa` | [Amendment to DEC-a17d0f: BF-CF semantic-family compatibility gate (G11)](./ADR-b7affa.md) | superseded |  | DEC-b390ef |  |
| `DEC-b7d74b` | [Retire the signed audit courier; preserve dual-model maker/checker trust and the admission gate at full strength](./ADR-b7d74b.md) | implemented |  |  |  |
| `DEC-b80330` | [Documentation Implementation — Greenfield with Split Dossiers, Diagram Layer, Foundation Stream](./ADR-b80330.md) | implemented | DEC-6f5199 |  |  |
| `DEC-b8b825` | [OLS-14 Semantic Activation Gate — refusal rules, signature-hash comparison, intentional reuse pattern, MT-04971 specimen](./ADR-b8b825.md) | decided |  |  |  |
| `DEC-b8ec00` | [BF-BO Catalog Expansion Factory](./ADR-b8ec00.md) | superseded |  | DEC-b390ef |  |
| `DEC-b97390` | [Embedded documentation reader in bc-admin with native React implementation](./ADR-b97390.md) | decided |  |  |  |
| `DEC-baaa09` | [Source contracts are business-function-agnostic — function_code belongs on canonical/metric layer only](./ADR-baaa09.md) | implemented |  |  |  |
| `DEC-bacbf5` | [Source-system onboarding completeness: every tenant connection maps its company identity to the tenant's declared legal entities before it may feed evaluation](./ADR-bacbf5.md) | decided |  |  |  |
| `DEC-bae0ef` | [IC Simplification — Remove action_templates, Single Intervention with Numeric Target](./ADR-bae0ef.md) | implemented |  |  |  |
| `DEC-bc6be2` | [Finance Package v0 — advance the date-derivation unlock; sanction date_offset OC transform for the date-diff family](./ADR-bc6be2.md) | decided |  |  |  |
| `DEC-bc7281` | [Connections reversed from tenant DB to platform runtime schema](./ADR-bc7281.md) | reversed |  |  |  |
| `DEC-bd5492` | [GDPR/DPDP/CCPA Nullification Object — Privacy Erasure for Immutable-Fact Architecture](./ADR-bd5492.md) | decided |  |  |  |
| `DEC-bd5fed` | [Orphaned routes — remove from router](./ADR-bd5fed.md) | implemented |  |  |  |
| `DEC-bd6ceb` | [Platform M14 activation does not gate on PE-MC-8 default-mode (Model A)](./ADR-bd6ceb.md) | decided |  |  |  |
| `DEC-be4ff9` | [Serverless deployment: Lambda + Fargate split](./ADR-be4ff9.md) | superseded |  |  |  |
| `DEC-bebaec` | [Chain Completeness SSOT — Definition of Complete + Persisted Chain Status](./ADR-bebaec.md) | superseded |  | DEC-b390ef |  |
| `DEC-beef5c` | [Record-identity doctrine: three-class rulebook for BC identity_role + additive-first-declaration (amends DEC-02f5a9)](./ADR-beef5c.md) | decided |  |  |  |
| `DEC-bef347` | [Structural Completeness — All Contract Instance Keys Required, No Structural Optionality](./ADR-bef347.md) | implemented |  |  |  |
| `DEC-bf5e61` | [Reader Configuration Presets — fixed option lists, foundation-aligned](./ADR-bf5e61.md) | implemented |  |  |  |
| `DEC-bf7842` | [DevHub is dev/ops coordination; bc-core owns the metric-authoring domain (generation, pre-spend validation, enforcement)](./ADR-bf7842.md) | decided |  |  |  |
| `DEC-c012c0` | [Metric Contract grammar v1.1 — per-variable temporal input selection](./ADR-c012c0.md) | superseded |  | DEC-83fda0 |  |
| `DEC-c027fb` | [Identity tuple v3: aggregation currency policy is a metric identity element](./ADR-c027fb.md) | implemented |  |  |  |
| `DEC-c0290f` | [Metric Evaluation Engine — Universal Formula Engine with Schedule-Driven Orchestration](./ADR-c0290f.md) | implemented |  |  |  |
| `DEC-c05551` | [Governed legal-entity dimension: separate canonical identity from per-source company key via a source-to-entity binding](./ADR-c05551.md) | decided |  |  |  |
| `DEC-c06f41` | [Spine expansion: add AI and Development sections; split Services into three chapters; add Notifications and Webhooks and Audit Logging chapters](./ADR-c06f41.md) | decided |  |  |  |
| `DEC-c10d05` | [bc-core Base Refactoring — Build, Type Safety, Error Handling, Module Structure](./ADR-c10d05.md) | decided |  |  |  |
| `DEC-c19242` | [bc-admin UI Development Freeze — Runtime Over Registry](./ADR-c19242.md) | superseded |  | DEC-b39a00 |  |
| `DEC-c193a1` | [Server-Side Onboarding Orchestrator — SSE streaming for all onboarding workflows](./ADR-c193a1.md) | implemented |  |  |  |
| `DEC-c2f499` | [Control Plane / Data Plane Architecture Split](./ADR-c2f499.md) | superseded |  |  |  |
| `DEC-c318b2` | [Tenant Database Segregation — separate DB per tenant](./ADR-c318b2.md) | superseded |  |  |  |
| `DEC-c338b3` | [BF/BO versioning model for supersede-active (Model E)](./ADR-c338b3.md) | superseded |  | DEC-b390ef |  |
| `DEC-c3e57f` | [Foundational Metric Context Framework (MCF) — sibling of BCF for metric meaning and metric-context packages](./ADR-c3e57f.md) | decided |  |  |  |
| `DEC-c3fef3` | [Runner dual-write — operational logs to platform, business data to tenant](./ADR-c3fef3.md) | superseded |  |  |  |
| `DEC-c40e7a` | [Cloud realization of the DB foundation — RDS PostgreSQL 17 on the versioned spine (W1.6 + the W2/W4 cloud items)](./ADR-c40e7a.md) | proposed |  |  |  |
| `DEC-c4619b` | [Deterministic numeric execution profile: scaled-integer exact arithmetic for metric evaluation](./ADR-c4619b.md) | decided |  |  |  |
| `DEC-c46354` | [Tenant GL account classification binding (D514 companion, D502-aligned): classify_by_binding derivation, platform defaults with onboarding/FSV override, onboarding-mandatory enforcement](./ADR-c46354.md) | implemented |  |  |  |
| `DEC-c48b0f` | [Metric certification is an MCF lifecycle act — second panel certifies before activation; the \"external audit\" framing is retired](./ADR-c48b0f.md) | decided | DEC-3d6eeb |  |  |
| `DEC-c4c742` | [The Governed Selection — defining the Invariant-IV reserved selection artifact (as-of/state selection)](./ADR-c4c742.md) | decided |  |  |  |
| `DEC-c562d5` | [Canonical bc-portal design: Dashboard and Workspace, with the Rooth canvas as its metric view](./ADR-c562d5.md) | decided | DEC-7e76b9, DEC-6cdceb |  |  |
| `DEC-c566f3` | [D223: KPI Catalog AI Assistant — Structured Retrieval + Grounded LLM](./ADR-c566f3.md) | decided |  |  |  |
| `DEC-c6180d` | [Business Chain — nav group + onboarding workbench + bulk monitor](./ADR-c6180d.md) | implemented |  |  |  |
| `DEC-c800d2` | [bc-admin v1.0.0 Lock — Scope & Architecture](./ADR-c800d2.md) | implemented |  |  |  |
| `DEC-c8dd31` | [Reference-to-Source Catalog promotion — governed copy with draft status](./ADR-c8dd31.md) | implemented |  |  |  |
| `DEC-c99f72` | [Platform schema capture authority: reviewed read-only capture script with hash-bound written operator authorization (D12 = B)](./ADR-c99f72.md) | decided |  |  |  |
| `DEC-c9b838` | [From-seed-only authoring + reservoir status ledger as progress SSOT for MCF enrichment](./ADR-c9b838.md) | decided |  |  |  |
| `DEC-c9e623` | [BareCount Object Life States — framework, state ledger schema, probe-vs-gate separation, cross-boundary code rule](./ADR-c9e623.md) | decided |  |  |  |
| `DEC-ca4c1e` | [AC Master Shape Locked — DQC-Integrated Admission Contract Body v1](./ADR-ca4c1e.md) | implemented |  |  |  |
| `DEC-cafc1b` | [UinBAT Reader operational shape — schedule, retries, backfill, failure policy](./ADR-cafc1b.md) | implemented |  |  |  |
| `DEC-cb906b` | [master_system_type reference table for software system categories](./ADR-cb906b.md) | implemented |  |  |  |
| `DEC-cbc07b` | [Type Conformance Enforcement — Source Object through Metric Snapshot](./ADR-cbc07b.md) | reversed |  |  |  |
| `DEC-cc8fd9` | [E2E Chain Test Bench — Tenant-Publishes-to-Platform QA Architecture](./ADR-cc8fd9.md) | implemented |  |  |  |
| `DEC-ccb7f7` | [Source Discovery Model — reconnaissance, not extraction](./ADR-ccb7f7.md) | implemented |  |  |  |
| `DEC-cce1d3` | [bc-portal Architecture and Patterns — routing, state, data-fetching, auth, error handling](./ADR-cce1d3.md) | superseded |  | DEC-04dade |  |
| `DEC-ccfa3f` | [SFDC flavor fixes — drop ar-invoice-item→OpportunityLineItem, flag material-master rename](./ADR-ccfa3f.md) | implemented |  |  |  |
| `DEC-cd3046` | [V2 seed data format — CSV, not JSON](./ADR-cd3046.md) | implemented |  |  |  |
| `DEC-ce3e7a` | [bc-core authentication — no auth-bypass; real Cognito only (backfill)](./ADR-ce3e7a.md) | decided |  |  |  |
| `DEC-ce4314` | [Onboarding Runway Lanes — source-classified workstreams for onboarding a source system (BCF/MCF vocabulary)](./ADR-ce4314.md) | decided |  |  |  |
| `DEC-ce6e2b` | [Section rename: The Runtime → The Operating Model](./ADR-ce6e2b.md) | decided |  |  |  |
| `DEC-ced5dc` | [BCF Enrichment Program-2 — non-finance vocabulary buildout to max coverage](./ADR-ced5dc.md) | implemented |  |  |  |
| `DEC-cf2cbc` | [Foundation naming compliance + schema integrity for boundary tables](./ADR-cf2cbc.md) | superseded |  | DEC-f02230 |  |
| `DEC-cff0cf` | [ABC = Autonomous Business Chain — deterministic orchestrator over governed factories + bounded retrieval-first reasoning panel](./ADR-cff0cf.md) | decided |  |  |  |
| `DEC-d214ed` | [BO-CO Enrichment Engine — Claude Code Generation + Gemini Verification + Audit Trail](./ADR-d214ed.md) | superseded |  | DEC-e9294b |  |
| `DEC-d2cdb9` | [SAP data admission stance under SAP API Policy v.4/2026](./ADR-d2cdb9.md) | superseded |  | DEC-b390ef |  |
| `DEC-d2eeb8` | [Schema namespace reorganization + table pluralization — sequence with tenant isolation](./ADR-d2eeb8.md) | superseded |  |  |  |
| `DEC-d308de` | [Re-scale Profile #1 (mfg-in) to a Tier-1 auto-component supplier at target-buyer scale, with an OEM-concentrated customer master](./ADR-d308de.md) | decided |  |  |  |
| `DEC-d315ve` | [D315 — Metric Evaluation Verification Framework](./ADR-d315ve.md) | decided |  |  | non-canonical filename |
| `DEC-d316mr` | [D316 — Metric Readiness Scheduler](./ADR-d316mr.md) | decided |  |  | non-canonical filename |
| `DEC-d3492b` | [as_of selection mode 'latest_observation' — per-series latest-snapshot governed selection (per-period balances)](./ADR-d3492b.md) | implemented |  |  |  |
| `DEC-d3b916` | [Certification roster registrations are governed by D541: the roster-pin CHECK moves from DEC-05815d to DEC-c48b0f](./ADR-d3b916.md) | decided |  |  |  |
| `DEC-d468e2` | [Reference BCs deferred until Reference BC End-to-End DBCP](./ADR-d468e2.md) | decided |  |  |  |
| `DEC-d4a383` | [Infrastructure lives in dedicated infra repo](./ADR-d4a383.md) | implemented |  |  |  |
| `DEC-d53320` | [Three SAP landscapes: S/4HANA Public Cloud, S/4HANA On-Premise, ECC EHP8](./ADR-d53320.md) | superseded |  | DEC-b390ef |  |
| `DEC-d5c352` | [SAP Data Acquisition Strategy — Phase 1: sapdatasheet.org](./ADR-d5c352.md) | superseded |  | DEC-b390ef |  |
| `DEC-d5fb43` | [Contract Version Format — Semver, Release Notes, Tenant Notifications](./ADR-d5fb43.md) | implemented |  |  |  |
| `DEC-d6a1d4` | [Contract Generation Service — programmatic, not hand-built JSON](./ADR-d6a1d4.md) | implemented |  |  |  |
| `DEC-d6f6e1` | [DevHub as MCP server](./ADR-d6f6e1.md) | implemented |  |  |  |
| `DEC-d72560` | [Canonical Field as 3rd Contract Primitive — Two-Vocabulary Model with CC as Translator](./ADR-d72560.md) | superseded |  | DEC-a17d0f |  |
| `DEC-d785d4` | [Reader → Business Object FK — SO Shape Enforcement via BO Constraint](./ADR-d785d4.md) | superseded |  | DEC-0d5b39 |  |
| `DEC-d7c1dd` | [Hybrid tenant isolation — schema-per-tenant standard, database-per-tenant premium](./ADR-d7c1dd.md) | superseded |  | DEC-1cdc5e |  |
| `DEC-d7e7a0` | [Platform date_dim + per-entity tenant fiscal calendar + FiscalCalendarService](./ADR-d7e7a0.md) | implemented |  |  |  |
| `DEC-d894de` | [Workflow Governance: SOP + Programmatic Flow + UI Control Plane](./ADR-d894de.md) | implemented |  |  |  |
| `DEC-d9578e` | [Dashboard route slugs — keep short](./ADR-d9578e.md) | superseded |  | DEC-7e76b9 |  |
| `DEC-d9fa49` | [Legacy metric-contract activation retired with a governed refusal — F-018 disposition (accidental dead-signal freeze replaced)](./ADR-d9fa49.md) | implemented |  |  |  |
| `DEC-da4c51` | [Contract Trust Chain — Lifecycle Stages with Upward Trust Propagation](./ADR-da4c51.md) | decided |  |  |  |
| `DEC-db1c63` | [Metric as Data Product — KPI Output tab with consumable endpoints and AI activation metadata](./ADR-db1c63.md) | decided |  |  |  |
| `DEC-dbb511` | [DB role separation — barecount_app vs barecount_ops, executed at pre-staging provisioning](./ADR-dbb511.md) | decided |  |  |  |
| `DEC-dc5d52` | [Authority by derivation — platform-internal evidence is the sole intrinsic authority class](./ADR-dc5d52.md) | decided |  |  |  |
| `DEC-dd11e3` | [Certification is withdrawable, and machine-checkable defect classes must be structural gates rather than panel discretion](./ADR-dd11e3.md) | decided |  |  |  |
| `DEC-ddbce8` | [Unified Business Domain Taxonomy](./ADR-ddbce8.md) | superseded |  | DEC-7bbdba |  |
| `DEC-ddc13e` | [Concept↔source soft-reference layer — catalog-anchored, advisory, drives SDG + chain generation](./ADR-ddc13e.md) | decided |  |  |  |
| `DEC-deac26` | [Canonical mapping — rename mapping_binding, move from master to contract schema](./ADR-deac26.md) | implemented |  |  |  |
| `DEC-deb4d4` | [Feed-integrity hardening package: rehearsal lane, zero-deferral rule, lane-retired supersession, enforcement-3 cut, evidence retention, vector siblings](./ADR-deb4d4.md) | implemented |  |  |  |
| `DEC-def930` | [Pilot master-data framework — shared profile spine + real-system seeding adapters + living data (extends DEC-b0839a, DEC-9ec48f)](./ADR-def930.md) | decided |  |  |  |
| `DEC-e01fcf` | [Chain enrichment doctrine — autonomous sequencing across BCF / SC / AC / OC / CC / MC / CAS / PE-MC](./ADR-e01fcf.md) | decided |  |  |  |
| `DEC-e1241a` | [Source catalog artefacts carry identity; derivability verifies but never substitutes](./ADR-e1241a.md) | implemented |  |  |  |
| `DEC-e1312a` | [Governed retirement as a distinct deletion class — a sibling carve-out in the source-catalog delete guard, with its own evidence relation](./ADR-e1312a.md) | implemented |  |  |  |
| `DEC-e27625` | [Tenant-Scoped Admission Contracts — no shared production contracts](./ADR-e27625.md) | implemented |  |  |  |
| `DEC-e29de9` | [BareCount is anti-pipeline: contract-first lifecycle system](./ADR-e29de9.md) | implemented |  |  |  |
| `DEC-e39ed3` | [AWS resource naming and tagging convention — scope/stage/region/domain, immutable tenant id, Aspect-enforced](./ADR-e39ed3.md) | proposed |  |  |  |
| `DEC-e44afd` | [Function Admin Console — decentralized RBAC and tabbed envelope for function-scoped governance](./ADR-e44afd.md) | decided |  |  |  |
| `DEC-e4eb7c` | [Multi-company shared party master for the demo group (join-key identity successor-6)](./ADR-e4eb7c.md) | superseded |  | DEC-64ad7c |  |
| `DEC-e50b83` | [Master port reservation — all local dev services](./ADR-e50b83.md) | implemented |  |  |  |
| `DEC-e6d5f0` | [Platform-scoped tenant-readiness projection](./ADR-e6d5f0.md) | proposed |  |  |  |
| `DEC-e7a4f5` | [Readers are domain-bound, not source-bound](./ADR-e7a4f5.md) | implemented |  |  |  |
| `DEC-e7b1c9` | [E2E Execution Chain — Issues Found and Permanent Fixes](./ADR-e7b1c9.md) | implemented |  |  |  |
| `DEC-e7b7b3` | [MLS State Substrate — current ledger, append-only event log, declarative trigger binding, queue-based recorder](./ADR-e7b7b3.md) | decided |  |  |  |
| `DEC-e82f0a` | [bc-portal AI Assistant — unified drawer replacing help, dual retrieval (catalog + articles) [QUARANTINED DUPLICATE FILE]](./ADR-DEC-e82f0a.md) | superseded |  | DEC-e82f0a | quarantined duplicate |
| `DEC-e82f0a` | [bc-portal AI Assistant — unified drawer replacing help, dual retrieval (catalog + articles)](./ADR-e82f0a.md) | implemented |  |  |  |
| `DEC-e87701` | [MCF cheap panel roster: gate-2 residency APPROVED for the direct-API DeepSeek judge; proceed to off-pool mega-plan execution](./ADR-e87701.md) | decided |  |  |  |
| `DEC-e8a4d2` | [Definition is the canonical parent — fold contract page into definition page, drop reverse FK](./ADR-e8a4d2.md) | implemented |  |  |  |
| `DEC-e9294b` | [bc-ai — Platform AI Orchestration Service (MCP + REST)](./ADR-e9294b.md) | superseded | DEC-d214ed | DEC-b390ef |  |
| `DEC-e93a19` | [SAP Table Reference — separate catalog table](./ADR-e93a19.md) | superseded |  | DEC-b390ef |  |
| `DEC-e9a1a7` | [join_context Scope — same-source-system only, no cross-system joins](./ADR-e9a1a7.md) | implemented |  |  |  |
| `DEC-e9bba0` | [Tenant infrastructure table — per-tenant deployment configuration on platform DB](./ADR-e9bba0.md) | implemented |  |  |  |
| `DEC-ea4523` | [Canonical fiscal resolver must be source-agnostic: derive fiscal period from declared posting-date + resolved legal-entity calendar; delete the bukrs/'*' literal; dereference source m2o FKs](./ADR-ea4523.md) | decided |  |  |  |
| `DEC-ea5074` | [SC/AC Naming Convention — sc__{system}__{table}](./ADR-ea5074.md) | superseded |  | DEC-3fe389 |  |
| `DEC-ea9bdc` | [The SAP source catalogs (ECC + S/4HANA) and the contract chain over them are declared CONTAMINATION and authorised for governed retirement](./ADR-ea9bdc.md) | decided |  |  |  |
| `DEC-eaba02` | [Validation Status — Tenant-Scoped Execution Proof for Catalog Objects](./ADR-eaba02.md) | implemented |  |  |  |
| `DEC-eba2aa` | [Register all 66 auto-generated dashboard routes in Screen Registry](./ADR-eba2aa.md) | implemented |  |  |  |
| `DEC-ebb3cd` | [Evidence and Lineage Write Semantics — Best-Effort + Degraded Marker, Per-Evaluation Lineage with Snapshot Fan-Out](./ADR-ebb3cd.md) | decided |  |  |  |
| `DEC-ebf0b4` | [Session Discipline & Data Integrity Rules (NOT-TO-DO)](./ADR-ebf0b4.md) | implemented |  |  |  |
| `DEC-ec00f2` | [Dual-model execution for judgment-bearing audit acts](./ADR-ec00f2.md) | decided |  |  |  |
| `DEC-ec341c` | [Admission scope as primary policy axis (cross_function / function_scoped / industry_scoped)](./ADR-ec341c.md) | implemented |  |  |  |
| `DEC-ec9e89` | [Contract Governance Model — Master Shape, Platform Instance, Tenant Override](./ADR-ec9e89.md) | implemented | DEC-03db11 |  |  |
| `DEC-ecd55c` | [Connection authority reconciled — config in platform runtime.connection (D168), credentials in AWS Secrets Manager](./ADR-ecd55c.md) | implemented |  |  |  |
| `DEC-ecec75` | [Metric contract architecture — one contract per KPI, not per module](./ADR-ecec75.md) | implemented |  |  |  |
| `DEC-edd9bb` | [BC-Agent On-Premises Appliance — premium tier with branded hardware](./ADR-edd9bb.md) | decided |  |  |  |
| `DEC-ee6018` | [Power of Ten — Adapted Coding Rules for BareCount](./ADR-ee6018.md) | implemented |  |  |  |
| `DEC-eea376` | [Platform scope follows the user: admin-client tokens need the bc-platform Cognito group; explicit roles on every platform write; operator-only registry-shape confirm](./ADR-eea376.md) | implemented |  |  |  |
| `DEC-efb5bf` | [Canonical-v1 meta-schema body structure finalized](./ADR-efb5bf.md) | implemented |  |  |  |
| `DEC-efe97f` | [Inline text[] tags retained — junction tables deferred until cross-entity tag querying needed](./ADR-efe97f.md) | decided |  |  |  |
| `DEC-f02230` | [Tenant DB schema organization — 6 schemas with data/identity/admin separation](./ADR-f02230.md) | implemented |  |  |  |
| `DEC-f0866a` | [Connector Ecosystem — transport abstraction, dynamic registry, test harness, scaffold CLI](./ADR-f0866a.md) | implemented |  |  |  |
| `DEC-f0c0f7` | [No Hardcoded Enums — All Dropdowns Must Be API-Driven](./ADR-f0c0f7.md) | implemented |  |  |  |
| `DEC-f0e78e` | [Platform/tenant authority boundary — distinct classes; narrow platform-inspection carve-out](./ADR-f0e78e.md) | decided |  |  |  |
| `DEC-f0eb14` | [System Documentation Framework — 4-Stream, Module-Component Architecture](./ADR-f0eb14.md) | implemented |  |  |  |
| `DEC-f1565d` | [Multi-Table Executor — Backward-Compatible Interface Extension](./ADR-f1565d.md) | implemented |  |  |  |
| `DEC-f1dae0` | [Standards-First BF/BO Creation — OAGIS Primary, Metrics Validate](./ADR-f1dae0.md) | superseded | DEC-6d8be5 | DEC-b390ef |  |
| `DEC-f26528` | [Governance lifecycle uses 'in_review' not 'submitted](./ADR-f26528.md) | implemented |  |  |  |
| `DEC-f275d7` | [Ghost Data Infra routes — add placeholder pages](./ADR-f275d7.md) | superseded |  |  |  |
| `DEC-f28021` | [Reference Landscape vs Source Catalog — separation of concerns](./ADR-f28021.md) | superseded |  | DEC-05140c |  |
| `DEC-f4084d` | [Governed chain-authoring capability: publishChain + registerSourceStack + substrate resolver (logic in bc-core)](./ADR-f4084d.md) | implemented |  |  |  |
| `DEC-f44a71` | [Tenant Readiness Program — execution & sequencing (Kaveri MLS 15-25 walk; route (a) source-bounded DSO fix)](./ADR-f44a71.md) | decided |  |  |  |
| `DEC-f48f99` | [D418 Historical FK Sink Classification](./ADR-f48f99.md) | decided |  |  |  |
| `DEC-f4a6b9` | [Engineering rule catalogue and responsibility registry (one job, one owner)](./ADR-f4a6b9.md) | decided |  |  |  |
| `DEC-f4b2b0` | [Aggregation-currency declaration for amount metrics](./ADR-f4b2b0.md) | implemented |  |  |  |
| `DEC-f4e9a0` | [Customer Invoice identity = composite {Legal Entity (ref), document number, document fiscal year}; introduce Legal Entity entity](./ADR-f4e9a0.md) | superseded |  | DEC-a57eb8 |  |
| `DEC-f5018a` | [Canonical Contract Split — universal form vs tenant-scoped mapping binding](./ADR-f5018a.md) | implemented |  |  |  |
| `DEC-f5111d` | [Retire Accountability Boundary, Responsibility object, and Accountable state from Foundation Specification](./ADR-f5111d.md) | implemented |  |  |  |
| `DEC-f6527b` | [Currency normalization for metrics — canonical FX rate store + normalize_currency policy](./ADR-f6527b.md) | superseded |  | DEC-7bccf6 |  |
| `DEC-f656a6` | [Universal Protocol Readers — Connector Reclassification & Onboarding-Embedded Provisioning](./ADR-f656a6.md) | implemented |  |  |  |
| `DEC-f66378` | [BO-Scoped BF Composition — No Shared Observation Fields Across BOs](./ADR-f66378.md) | superseded |  | DEC-b390ef |  |
| `DEC-f6c2e5` | [Global auth guard on bc-core with @Public() exceptions](./ADR-f6c2e5.md) | implemented |  |  |  |
| `DEC-f82a8a` | [Dynamic schema-per-tenant provisioning on tenant creation](./ADR-f82a8a.md) | superseded |  | DEC-1cdc5e |  |
| `DEC-f83b8a` | [Source Specification Framework — 5-Dimensional Classification for Source Tables](./ADR-f83b8a.md) | implemented |  |  |  |
| `DEC-f8f925` | [Foundational Metric Context Framework (MCF) — sibling of BCF for metric meaning and metric-context packages](./ADR-f8f925.md) | reversed |  | DEC-c3e57f |  |
| `DEC-f90ba3` | [MCF Onboarding Orchestration Schema — DevHub-side queue for 12K metric reservoir](./ADR-f90ba3.md) | superseded |  | DEC-b5c7ff |  |
| `DEC-f94895` | [A1–A5 Program Authorization — BCF × OAGIS Broad Foundation Buildout](./ADR-f94895.md) | decided |  |  |  |
| `DEC-fa7c63` | [DSO family meaning: receivable balance from dated application events, net billing, calendar days (W9 U9.1)](./ADR-fa7c63.md) | decided |  |  |  |
| `DEC-fa9424` | [Metric authoring is Directory-primary — Member-anchored M12 door in bc-admin; retire the seed-primary Register entry](./ADR-fa9424.md) | implemented |  |  |  |
| `DEC-faef79` | [Customer data isolation — data plane architecture](./ADR-faef79.md) | implemented |  |  |  |
| `DEC-fb0b12` | [Editorial Amendment of Active Characteristic Definitions — Refinement of DEC-26b6e2](./ADR-fb0b12.md) | decided |  |  |  |
| `DEC-fbc085` | [Platform-plane evidence home for contract-version governance transitions (Inv VI): an append-only transition record written by a trigger in the same transaction](./ADR-fbc085.md) | decided |  |  |  |
| `DEC-fbe2c2` | [bc-core-dashboard retirement — superseded by bc-admin (backfill)](./ADR-fbe2c2.md) | decided |  |  |  |
| `DEC-fbf6ab` | [Platform DB Foundation program CLOSED — foundation objectives met](./ADR-fbf6ab.md) | decided |  |  |  |
| `DEC-fc41a3` | [Source Chain Contract Generation — SAP ECC Finance](./ADR-fc41a3.md) | superseded |  | DEC-b390ef |  |
| `DEC-ffee4e` | [Retire bc-ai — port the BCF registry-authoring panel in-process into bc-core, roster preserved](./ADR-ffee4e.md) | implemented | DEC-14fb98 |  |  |

*Generated by `scripts/docs-control/generate_adr_registry.py` from bc-docs `aa5b743` at 2026-09-30T12:41:45Z.*
