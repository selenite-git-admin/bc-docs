---
id: glossary
title: "Glossary"
status: drafting
authority: reference
collection: glossary
---

# Glossary

## A

**Action Contract.** See `Intervention Contract`.

**Action Evaluation.** The fourth evaluation boundary, where Intervention Contracts are applied to Metric Snapshots to emit Action Objects representing declared platform intent. First-use: [The Evaluation Boundaries](../../foundation/the-evaluation-boundaries.md). Related: [Action Evaluation](../../operating-model/action-evaluation.md); [Evidence and Lineage](../../operating-model/evidence-and-lineage.md).

**Action Object.** An authoritative object representing declared intent bound at creation time to one or more Metric Snapshots. Produced at the action evaluation boundary. First-use: [The Object Model](../../foundation/the-object-model.md). Related: [The Invariants](../../foundation/the-invariants.md); [Action Evaluation](../../operating-model/action-evaluation.md).

**ADR (Architecture Decision Record).** A markdown file in `docs/adrs/` recording a single architectural decision with status, rationale, and consequences. Per `DEC-a4e550`, the ADR file is the source of truth; DevHub holds metadata that points at it. First-use: [Decision and Change Procedure](../../development/decision-and-change-procedure.md). Related: [DevHub](../../development/devhub.md); [Documentation System](../../development/documentation-system.md).

**Admission and Observation.** The runtime acts at the first evaluation boundary that produce Source Objects from external state under governed Admission and Observation Contracts. First-use: [Admission and Observation](../../operating-model/admission-and-observation.md). Related: [The Evaluation Boundaries](../../foundation/the-evaluation-boundaries.md); [Connectors and Readers](../../operating-model/connectors-and-readers.md).

**Admission Contract.** A contract family declaring the rules under which observed source state is admitted at the admission boundary, including identity semantics, required fields, structural validation, and rejection policy. First-use: [The Contract Grammar](../../foundation/the-contract-grammar.md). Related: [Admission and Observation](../../operating-model/admission-and-observation.md); [Sources and the Catalog](../../operating-model/sources-and-the-catalog.md).

**AI Gate.** A governance entry point where AI verdicts from maker-checker-gate triplets are routed into bc-core's gate substrate, with routing semantics in green-amber-red. First-use: [AI Gates](../../ai/ai-gates.md). Related: [AI Architecture](../../ai/ai-architecture.md); [AI Trust and Verification](../../ai/ai-trust-and-verification.md).

**AuthStack.** The CDK stack that provisions AWS Cognito for platform authentication. Per Infrastructure, AuthStack is the deployed stack in the readiness baseline; PlatformInfraStack code exists but is not in the entry point. First-use: [Infrastructure](../../implementation/infrastructure.md). Related: [Operations: Deployment Topology](../../operations/deployment-topology.md); [InfoSec and Access Control](../../compliance/infosec-and-access-control.md).

## B

**bc-admin.** The platform's React and Vite admin frontend. The canonical reader for the documentation per `DEC-b97390`. First-use: [Frontend Experience](../../implementation/frontend-experience.md). Related: [Documentation System](../../development/documentation-system.md); [Developer Experience](../../development/developer-experience.md).

**bc-ai.** The platform's Python and FastAPI AI service. Hosts agents, gates, evidence, and housekeeping. First-use: [AI Architecture](../../ai/ai-architecture.md). Related: [Backend Services](../../implementation/backend-services.md); [AI Agents](../../ai/ai-agents.md).

**bc-core.** The platform's NestJS runtime service. Hosts the contract-execution boundaries, the auth gate, the docs surface, the per-tenant connection routing. First-use: [Backend Services](../../implementation/backend-services.md). Related: [Architecture](../../implementation/architecture.md); [API Surface](../../implementation/api-surface.md).

**bc-portal.** The platform's React and Vite customer frontend. Carries three incomplete UI iterations under active redesign per the corpus's drift inventory. First-use: [Frontend Experience](../../implementation/frontend-experience.md). Related: [Architecture](../../implementation/architecture.md).

**bc-qa.** The platform's standalone quality-assurance repository per `DEC-ee6018`. Holds the audit harness, pre-commit hooks, eslint-config package, and NC register shared across all platform repos. First-use: [Quality Assurance](../../development/quality-assurance.md). Related: [Build and Release](../../development/build-and-release.md); [InfoSec and Access Control](../../compliance/infosec-and-access-control.md).

**Business Field (BF).** An atomic business-side field definition that contracts reference when selecting, validating, or mapping data. Composed into Business Objects with required, key, and role flags. First-use: [Business Vocabulary](../../operating-model/business-vocabulary.md). Related: [The Contract Grammar](../../foundation/the-contract-grammar.md); [Canonical Evaluation](../../operating-model/canonical-evaluation.md).

**Business Object (BO).** A named composition of Business Fields representing a domain concept, with tier classification (basic or derived) and standards provenance. First-use: [Business Vocabulary](../../operating-model/business-vocabulary.md). Related: [The Contract Grammar](../../foundation/the-contract-grammar.md); [Metric Catalog](../../operating-model/metric-catalog.md).

## C

**Canonical Contract (CC).** A contract family declaring field selection, grain, resolution rules, and the canonical-side schema that governs canonical evaluation to produce Canonical Objects. First-use: [The Contract Grammar](../../foundation/the-contract-grammar.md). Related: [Canonical Evaluation](../../operating-model/canonical-evaluation.md); [Contract Chain Assembly](../../operating-model/contract-chain-assembly.md).

**Canonical Evaluation.** The second evaluation boundary, where Canonical Contracts and Canonical Mappings are applied to Source Objects to emit Canonical Objects carrying business meaning. First-use: [The Evaluation Boundaries](../../foundation/the-evaluation-boundaries.md). Related: [Canonical Evaluation](../../operating-model/canonical-evaluation.md); [Business Vocabulary](../../operating-model/business-vocabulary.md).

**Canonical Field (CF).** An atomic canonical-side field definition produced at canonical evaluation and referenced by Metric Contracts and Canonical Mappings. First-use: [Business Vocabulary](../../operating-model/business-vocabulary.md). Related: [The Contract Grammar](../../foundation/the-contract-grammar.md); [Metric Evaluation](../../operating-model/metric-evaluation.md).

**Canonical Mapping (CM).** A supporting governed artifact that translates Business Fields to Canonical Fields at canonical evaluation time. Versioned independently from Canonical Contracts and applied per Canonical Contract version. First-use: [The Contract Grammar](../../foundation/the-contract-grammar.md). Related: [Canonical Evaluation](../../operating-model/canonical-evaluation.md); [Contract Chain Assembly](../../operating-model/contract-chain-assembly.md).

**Canonical Object (CO).** An authoritative object representing business-meaningful state derived from one or more Source Objects by applying a Canonical Contract at the canonical evaluation boundary. First-use: [The Object Model](../../foundation/the-object-model.md). Related: [The Invariants](../../foundation/the-invariants.md); [Metric Evaluation](../../operating-model/metric-evaluation.md).

**CCPA.** The California Consumer Privacy Act of 2018, amended by the CPRA in 2020. Per `DEC-bd5492`, the platform implements the right to delete (Section 1798.105) with a forty-five-day deadline through sentinel-based nullification. First-use: [Privacy and the Immutable Fact](../../compliance/privacy-and-the-immutable-fact.md). Related: [InfoSec and Access Control](../../compliance/infosec-and-access-control.md).

**Chain Completeness.** The platform's governance verdict for whether a Metric Contract can compute end-to-end against its sources, by verifying seven-link variable resolution and per-contract structural checks. SSOT per `DEC-bebaec`. First-use: [Chain Completeness and Verdict](../../operating-model/chain-completeness-and-verdict.md). Related: [Quality Gates and Chain Integrity](../../operating-model/quality-gates-and-chain-integrity.md); [Metric Catalog](../../operating-model/metric-catalog.md).

**Change Record.** An ISO 27001 plan-and-report pair recorded for each session per `DEC-ebf0b4`. Plan side records intent at session open; report side records outcome at session close. Both share the session UID as `ref_uid`. First-use: [Decision and Change Procedure](../../development/decision-and-change-procedure.md). Related: [DevHub](../../development/devhub.md); [ISO 27001 Conformance](../../compliance/iso-27001-conformance.md).

**Cognito.** AWS Cognito, the platform's authentication substrate. Issues JWTs that bc-core's `JwtAuthGuard` validates. First-use: [InfoSec and Access Control](../../compliance/infosec-and-access-control.md). Related: [Backend Services](../../implementation/backend-services.md); [Infrastructure](../../implementation/infrastructure.md).

**Connection.** A tenant-scoped artifact pairing a Reader Flavor with a Source System catalog entry, carrying credentials and per-tenant access configuration. First-use: [Connectors and Readers](../../operating-model/connectors-and-readers.md). Related: [Tenancy and Binding](../../operating-model/tenancy-and-binding.md); [Admission and Observation](../../operating-model/admission-and-observation.md).

**Connector.** A technical-capability artifact declaring the protocol-level ability to reach a Source System over a defined protocol with supported authentication methods. First-use: [Connectors and Readers](../../operating-model/connectors-and-readers.md). Related: [Admission and Observation](../../operating-model/admission-and-observation.md); [Sources and the Catalog](../../operating-model/sources-and-the-catalog.md).

**Contract Binding.** A tenant-scoped artifact pairing one tenant with one platform contract version under bounded variation permitted by the three-level governance model. First-use: [Tenancy and Binding](../../operating-model/tenancy-and-binding.md). Related: [The Contract Grammar](../../foundation/the-contract-grammar.md); [Tenant Extensions and Overrides](../../operating-model/tenant-extensions-and-overrides.md).

**Contract Chain.** The end-to-end alignment of Source, Admission, Observation, Canonical, and Metric Contracts that supports metric evaluation against source data. First-use: [Contract Chain Assembly](../../operating-model/contract-chain-assembly.md). Related: [Chain Completeness and Verdict](../../operating-model/chain-completeness-and-verdict.md); [Quality Gates and Chain Integrity](../../operating-model/quality-gates-and-chain-integrity.md).

**CodeArtifact.** AWS CodeArtifact, the platform's npm registry mirror per `DEC-441665`. Mitigates the supply-chain risk recorded as `RSK-cb8929`. First-use: [Build and Release](../../development/build-and-release.md). Related: [InfoSec and Access Control](../../compliance/infosec-and-access-control.md); [Risk and Vendor Management](../../compliance/risk-and-vendor-management.md).

## D

**DevHub.** The platform's engineering-coordination registry. A Node and Express HTTP server backed by SQLite, paired with a stdio MCP server exposing sixty tools across eighteen domains to a Claude Code session. First-use: [DevHub](../../development/devhub.md). Related: [Decision and Change Procedure](../../development/decision-and-change-procedure.md); [Audit and Activity Logging](../../implementation/audit-and-activity-logging.md).

**DEC-UID.** The canonical six-hex-character identifier (`DEC-xxxxxx`) for an Architecture Decision Record. Generated atomically by `generateUid('DEC')` at registry insert time. Used as the load-bearing identifier in code, ADR filenames, and registry keys. First-use: [Decision and Change Procedure](../../development/decision-and-change-procedure.md). Related: [DevHub](../../development/devhub.md).

**D-code.** A monotonic decimal nickname (`Dxxx`) allocated atomically by the DevHub D-code allocator under `db.transaction()`. Used as a human-readable nickname in conversation and v2 SOP shorthand. Per `DEC-633b2a`, D-codes carry historical duplicates and are not load-bearing identifiers in published content. First-use: [Decision and Change Procedure](../../development/decision-and-change-procedure.md). Related: [DevHub](../../development/devhub.md).

**DPDP Act.** India's Digital Personal Data Protection Act of 2023. Per `DEC-bd5492`, the platform implements the right to erasure (Section 12) with a thirty-day deadline through sentinel-based nullification. First-use: [Privacy and the Immutable Fact](../../compliance/privacy-and-the-immutable-fact.md). Related: [InfoSec and Access Control](../../compliance/infosec-and-access-control.md).

**Drift Inventory.** A chapter section per pattern 81 listing the gaps between the substrate as documented and the substrate as implemented. The chapter's canonical claim must match its drift inventory. First-use: most chapters carry one. Related: [Documentation System](../../development/documentation-system.md); the AWS rewrite checklist's pattern 81.

**DSAR.** Data Subject Access Request, a legal right under GDPR Article 15, DPDP Act Section 11, and CCPA Section 1798.100 allowing individuals to request their personal data. First-use: [Privacy and the Immutable Fact](../../compliance/privacy-and-the-immutable-fact.md). Related: [InfoSec and Access Control](../../compliance/infosec-and-access-control.md).

**Dual-Layer Interaction Model.** The Foundation framing distinguishing the Conversation Surface (operator-facing, advisory, AI-bearing) from the Trust Surface (governed authoring; only humans write here). First-use: [The Dual-Layer Interaction Model](../../foundation/the-dual-layer-interaction-model.md). Related: [The Authority Model](../../foundation/the-authority-model.md); [AI Gates](../../ai/ai-gates.md).

## E

**Errata.** A first-class governance peer under `docs/errata/`. Each entry records a Foundation contradiction or correction. The errata register is the source of truth for active entries. First-use: [Documentation System](../../development/documentation-system.md). Related: outline.md §4.9.

**Evidence (Object).** A proof object that records what occurred at an evaluation boundary, including evaluation type, inputs, outputs, evaluation context, outcome, and timestamp. Emitted at the same act that produces the authoritative object per Invariant VI. First-use: [The Object Model](../../foundation/the-object-model.md). Related: [The Invariants](../../foundation/the-invariants.md); [Evidence and Lineage](../../operating-model/evidence-and-lineage.md).

**Evaluation Boundaries.** The four governed acts at which authoritative state is produced: admission, canonical evaluation, metric evaluation, action evaluation. First-use: [The Evaluation Boundaries](../../foundation/the-evaluation-boundaries.md). Related: [The Object Model](../../foundation/the-object-model.md); [The Invariants](../../foundation/the-invariants.md).

## F

**Foundation.** The platform's locked architectural authority. Nine chapters define the Problem, the Solution, the Invariants, the Object Model, the Contract Grammar, the Evaluation Boundaries, the Authority Model, and the Dual-Layer Interaction Model, plus the section opener. First-use: [Foundation: Overview](../../foundation/foundation-overview.md). Related: [Operating Model: Overview](../../operating-model/operating-model-overview.md); outline.md §4.1.

## G

**GDPR.** The European Union's General Data Protection Regulation 2016/679. Per `DEC-bd5492`, the platform implements the right to erasure (Article 17) and the right of access (Article 15) with thirty-day deadlines through sentinel-based nullification and DSAR discovery. First-use: [Privacy and the Immutable Fact](../../compliance/privacy-and-the-immutable-fact.md). Related: [InfoSec and Access Control](../../compliance/infosec-and-access-control.md).

**Governing Source.** A footer convention per outline §2.7. Every substantive prose section ends with a `Governing source.` line naming the authoritative references (Foundation chapter, ADR, Errata entry, drafted chapter elsewhere). First-use: outline.md §2.7. Related: AWS rewrite checklist patterns 35, 52, 53.

## I

**Intervention Contract.** Also called Action Contract. A contract family declaring activation mode, trigger conditions, assignee pool, closure window, and evaluation rules for action evaluation at the fourth boundary. First-use: [The Contract Grammar](../../foundation/the-contract-grammar.md). Related: [Action Evaluation](../../operating-model/action-evaluation.md).

**Invariant I.** Business meaning is produced exactly once per Canonical Object version at the canonical evaluation boundary. First-use: [The Invariants](../../foundation/the-invariants.md). Related: [The Object Model](../../foundation/the-object-model.md); [Canonical Evaluation](../../operating-model/canonical-evaluation.md).

**Invariant II.** The platform produces four authoritative progression-object types in a fixed non-skippable sequence: Source Object, Canonical Object, Metric Snapshot, Action Object. First-use: [The Invariants](../../foundation/the-invariants.md). Related: [The Object Model](../../foundation/the-object-model.md); [The Evaluation Boundaries](../../foundation/the-evaluation-boundaries.md).

**Invariant III.** Once produced, authoritative objects are never altered. Corrections are expressed only as new object versions; all versions coexist. First-use: [The Invariants](../../foundation/the-invariants.md). Related: [The Object Model](../../foundation/the-object-model.md); [Privacy and the Immutable Fact](../../compliance/privacy-and-the-immutable-fact.md).

**Invariant IV.** Every reference to an authoritative object identifies its type, identity, and version. Implicit references are forbidden. First-use: [The Invariants](../../foundation/the-invariants.md). Related: [The Object Model](../../foundation/the-object-model.md); [Evidence and Lineage](../../operating-model/evidence-and-lineage.md).

**Invariant V.** Each evaluation boundary evaluates exactly once per object version it produces. Re-evaluation of the same inputs yields a new version, not a mutation of the same version. First-use: [The Invariants](../../foundation/the-invariants.md). Related: [The Evaluation Boundaries](../../foundation/the-evaluation-boundaries.md).

**Invariant VI.** Evidence and Lineage are emitted with every evaluation boundary act and preserved in the authoritative evidence chain. Never reconstructed or inferred from other state. First-use: [The Invariants](../../foundation/the-invariants.md). Related: [The Object Model](../../foundation/the-object-model.md); [Evidence and Lineage](../../operating-model/evidence-and-lineage.md).

## L

**L-node Semantic Verdict.** A semantic verification gate per `DEC-804874`. Runs at session close to detect chain semantic state regression during the session window. Routes green-amber-red across L1 through L8 verdicts. First-use: [Chain Completeness and Verdict](../../operating-model/chain-completeness-and-verdict.md). Related: [Decision and Change Procedure](../../development/decision-and-change-procedure.md); [DevHub](../../development/devhub.md).

**Lineage (Object).** A proof object recording the explicit reference relationships established at an evaluation boundary act, including produced object to input objects and to contract versions applied. First-use: [The Object Model](../../foundation/the-object-model.md). Related: [The Invariants](../../foundation/the-invariants.md); [Evidence and Lineage](../../operating-model/evidence-and-lineage.md).

## M

**Maker-Checker-Gate triplet.** The bc-ai agent pattern: a maker model proposes; a checker model (cross-family where applicable) verifies; the gate routes a verdict to bc-core. First-use: [AI Architecture](../../ai/ai-architecture.md). Related: [AI Agents](../../ai/ai-agents.md); [AI Trust and Verification](../../ai/ai-trust-and-verification.md).

**MCP Server.** A Model Context Protocol server. An independent runtime that registers a family of tools and exposes them to a Claude Code session over stdio. First-use: [DevHub](../../development/devhub.md). Related: [Developer Experience](../../development/developer-experience.md); [Backend Services](../../implementation/backend-services.md).

**MCP Tool Family.** A logical grouping of MCP tools addressing one domain (session, task, decision, plan, risk, QA NC). DevHub exposes eighteen families across sixty tools. First-use: [DevHub](../../development/devhub.md). Related: [Quality Assurance](../../development/quality-assurance.md); [Decision and Change Procedure](../../development/decision-and-change-procedure.md).

**Metric Catalog.** The platform-scoped registry of metric definitions classified across five dimensions plus function and discipline taxonomy. The pre-contract registry from which Metric Contracts are authored. First-use: [Metric Catalog](../../operating-model/metric-catalog.md). Related: [Metric Evaluation](../../operating-model/metric-evaluation.md); [Contract Chain Assembly](../../operating-model/contract-chain-assembly.md).

**Metric Contract (MC).** A contract family declaring formula, variables, Canonical Object bindings, grain, temporal gate, and outcome thresholds. Governs metric evaluation at the third boundary. First-use: [The Contract Grammar](../../foundation/the-contract-grammar.md). Related: [Metric Evaluation](../../operating-model/metric-evaluation.md); [Chain Completeness and Verdict](../../operating-model/chain-completeness-and-verdict.md).

**Metric Evaluation.** The third evaluation boundary, where Metric Contracts are applied to Canonical Object versions to emit Metric Snapshots. First-use: [The Evaluation Boundaries](../../foundation/the-evaluation-boundaries.md). Related: [Metric Evaluation](../../operating-model/metric-evaluation.md); [Evidence and Lineage](../../operating-model/evidence-and-lineage.md).

**Metric Snapshot.** An authoritative object representing a numeric assertion over one or more Canonical Object versions, produced at the metric evaluation boundary. First-use: [The Object Model](../../foundation/the-object-model.md). Related: [Metric Evaluation](../../operating-model/metric-evaluation.md); [Action Evaluation](../../operating-model/action-evaluation.md).

## N

**NC (Non-Conformity Record).** A QA governance record raised when code-quality checks find violations. Tracked through the bc-qa register and the DevHub `qa_nc_records` table with status (open, investigating, resolved, accepted, waived) and resolution path. First-use: [Quality Assurance](../../development/quality-assurance.md). Related: [DevHub](../../development/devhub.md); [ISO 27001 Conformance](../../compliance/iso-27001-conformance.md).

**Nullification.** See `Sentinel Nullification`.

## O

**Observation Contract.** A contract family declaring field selection from Source Contract structure to Business Field codes. Bridges structural source observation to business vocabulary. First-use: [The Contract Grammar](../../foundation/the-contract-grammar.md). Related: [Admission and Observation](../../operating-model/admission-and-observation.md); [Connectors and Readers](../../operating-model/connectors-and-readers.md).

## P

**`@PlatformOnly()`.** A NestJS decorator at `bc-core/src/common/decorators/scope.decorator.ts`. Marks a controller or route as platform-scope only; tenant-scope users receive 403 from `ScopeGuard`. First-use: [InfoSec and Access Control](../../compliance/infosec-and-access-control.md). Related: [Backend Services](../../implementation/backend-services.md); [API Surface](../../implementation/api-surface.md).

**PII Tier Model.** The five-tier classification per `DEC-bd5492` governing nullification priority and DSAR treatment: T1 direct identifier, T2 indirect identifier, T3 behavioral, T4 sensitive business, T5 structural (never nullified). First-use: [Privacy and the Immutable Fact](../../compliance/privacy-and-the-immutable-fact.md). Related: [InfoSec and Access Control](../../compliance/infosec-and-access-control.md).

**Platform DB.** The `bc_platform_dev` database; one of two database tiers per `DEC-1918d0`. Holds eleven schemas covering registry, contract, source, runtime, master, metric, operations, tenant, infrastructure, pricing, support. First-use: [Data Model and Schema](../../implementation/data-model-and-schema.md). Related: [Backend Services](../../implementation/backend-services.md); [InfoSec and Access Control](../../compliance/infosec-and-access-control.md).

## R

**Reader.** A platform-scoped Business-Object-oriented admission component implementing the UniBAT pattern. Orchestrates Connector access, Admission Contract validation, and Source Object emission. First-use: [Connectors and Readers](../../operating-model/connectors-and-readers.md). Related: [Admission and Observation](../../operating-model/admission-and-observation.md); [Sources and the Catalog](../../operating-model/sources-and-the-catalog.md).

**Reader Flavor.** A Reader variant bound to one Connector, one Observation Contract, and one Source System version context. Creates a specific admission capability. First-use: [Connectors and Readers](../../operating-model/connectors-and-readers.md). Related: [Admission and Observation](../../operating-model/admission-and-observation.md); [Tenancy and Binding](../../operating-model/tenancy-and-binding.md).

**RSK-cb8929.** The platform's known supply-chain risk: npm registry compromise, package yanking, dependency compromise. Mitigated by AWS CodeArtifact per `DEC-441665`. First-use: [Risk and Vendor Management](../../compliance/risk-and-vendor-management.md). Related: [Build and Release](../../development/build-and-release.md); [InfoSec and Access Control](../../compliance/infosec-and-access-control.md).

## S

**`ScopeGuard`.** A NestJS guard at `bc-core/src/auth/guards/scope.guard.ts`. Registered globally as `APP_GUARD`. Classifies every authenticated request as platform-scope or tenant-scope and routes accordingly. First-use: [InfoSec and Access Control](../../compliance/infosec-and-access-control.md). Related: [Backend Services](../../implementation/backend-services.md).

**Sentinel Nullification.** A field-overwrite mechanism per `DEC-bd5492`. Replaces personal-data field values with the deterministic sentinel `[NULLIFIED:NUL-xxxxxx]` on DSAR or erasure request, preserving row existence, primary key, foreign keys, chain shape, and audit evidence. First-use: [Privacy and the Immutable Fact](../../compliance/privacy-and-the-immutable-fact.md). Related: [InfoSec and Access Control](../../compliance/infosec-and-access-control.md); [The Object Model](../../foundation/the-object-model.md).

**Session UID.** A unique identifier (`SES-xxxxxx`) allocated atomically by DevHub for each engineering session. Used to track work, checkpoints, plans, and change records. First-use: [DevHub](../../development/devhub.md). Related: [Decision and Change Procedure](../../development/decision-and-change-procedure.md); [ISO 27001 Conformance](../../compliance/iso-27001-conformance.md).

**Source Catalog.** The platform-scoped registry of observable external source structure. Organized in a six-tier hierarchy: Source Provider, Source System, Source System Version, Module, Source Table, Source Field. First-use: [Sources and the Catalog](../../operating-model/sources-and-the-catalog.md). Related: [The Contract Grammar](../../foundation/the-contract-grammar.md); [Contract Chain Assembly](../../operating-model/contract-chain-assembly.md).

**Source Contract (SC).** A contract family declaring the structural shape of a source table or API endpoint, including field inventory, types, primary key, and tenant-extension flags. First-use: [The Contract Grammar](../../foundation/the-contract-grammar.md). Related: [Sources and the Catalog](../../operating-model/sources-and-the-catalog.md); [Admission and Observation](../../operating-model/admission-and-observation.md).

**Source Field.** An observable data element within a Source Table, registered in the Source Catalog with type, nullability, and tenant-scoped extension flags. First-use: [Sources and the Catalog](../../operating-model/sources-and-the-catalog.md). Related: [Business Vocabulary](../../operating-model/business-vocabulary.md); [Admission and Observation](../../operating-model/admission-and-observation.md).

**Source Object.** An immutable record of external state from a named Source System at a specific point in time. Emitted at the admission boundary as the first progression object. First-use: [The Object Model](../../foundation/the-object-model.md). Related: [The Invariants](../../foundation/the-invariants.md); [Admission and Observation](../../operating-model/admission-and-observation.md).

**Source System.** A named software system offered by one Source Provider, registered in the Source Catalog with versions, modules, and observable tables. First-use: [Sources and the Catalog](../../operating-model/sources-and-the-catalog.md). Related: [Connectors and Readers](../../operating-model/connectors-and-readers.md); [The Contract Grammar](../../foundation/the-contract-grammar.md).

**Subscription.** A tenant's entitlement to a metric or metric family. Governs access visibility and execution scope at runtime under the tenant-scoped permission model. First-use: [Tenant Lifecycle and Subscription](../../operations/tenant-lifecycle-and-subscription.md). Related: [Tenancy and Binding](../../operating-model/tenancy-and-binding.md); [Tenant Entitlement Enforcement](../../operating-model/tenant-entitlement-enforcement.md).

## T

**Tenant.** A platform-scoped identity owning one tenant database (`tbc_{slug}_dev`). Holds tenant-scoped artifacts (Bindings, Connections, Run records, Evidence, Lineage) under one-directional platform dependency. First-use: [Tenancy and Binding](../../operating-model/tenancy-and-binding.md). Related: [Tenant Lifecycle and Subscription](../../operations/tenant-lifecycle-and-subscription.md); [Tenant Onboarding](../../onboarding/tenant-onboarding.md).

**Tenant DB.** A per-tenant database (`tbc_{slug}_dev`); one per tenant per `DEC-771baf`. During the D369 M4.4 transition, the schema set includes envelope (deprecated, dropped at cleanup), progression (D369 metadata-only events that replaces envelope), fact, evidence, admin, organization, and tenant_dim. First-use: [Data Model and Schema](../../implementation/data-model-and-schema.md). Related: [InfoSec and Access Control](../../compliance/infosec-and-access-control.md).

**Tenant Extension.** A per-family override surface allowing bounded tenant customization of platform contracts beyond the tenant Override layer. Each configured surface is governed by the family's master schema. First-use: [Tenant Extensions and Overrides](../../operating-model/tenant-extensions-and-overrides.md). Related: [The Contract Grammar](../../foundation/the-contract-grammar.md); [Tenancy and Binding](../../operating-model/tenancy-and-binding.md).

**Truth Surface.** See `Trust Surface`.

**Trust Surface.** Per the Dual-Layer Interaction Model, the surface where governed authoring lives. Only humans write here; AI may read but never writes. First-use: [The Dual-Layer Interaction Model](../../foundation/the-dual-layer-interaction-model.md). Related: [The Authority Model](../../foundation/the-authority-model.md); [AI Gates](../../ai/ai-gates.md).

## U

**UniBAT.** Universal Business-Aware Transactions Reader. The architectural pattern under which Readers perform admission: source-system-agnostic on input (protocol handled by Connectors) and Business-Object-oriented on output. First-use: [Connectors and Readers](../../operating-model/connectors-and-readers.md). Related: [Admission and Observation](../../operating-model/admission-and-observation.md); [Business Vocabulary](../../operating-model/business-vocabulary.md).

---

**Source.** Walked across the eighty-four chapters under `docs/`. Per pattern 67 the chapter is the authority for each term; this glossary indexes them.
