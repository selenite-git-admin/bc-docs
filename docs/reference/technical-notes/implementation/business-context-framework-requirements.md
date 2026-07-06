---
uid: business-context-framework-requirements
title: Business Context Framework (BCF) — Requirements
description: Requirements for the Business Context Framework (BCF), the AI-assisted governance discipline for the contextual accuracy of the catalog's business vocabulary and meaning-anchoring layer. Scope is three framework scopes (BF/BO, CF, BF↔CF field-level mapping). AI proposes, prepares, and approves context for these members under Framework Approval, an ADR-governed authoring path; operator overrides as exception. Not a runtime component; not part of the contracts chain. Metric concerns (MC context, formula, variable binding, chain integrity, runtime-readiness) are scoped to the future Metric Context Framework (MCF), a sibling document.
status: draft
date: 2026-05-18
project: bc-docs
domain: contracts
subdomain: catalog
focus: requirements
---

# Business Context Framework (BCF) — Requirements

## Background

The contracts chain (admission → canonical → metric → action, per Foundation §The Evaluation Boundaries) is already in place. Its mechanics work. What does not work today is the **contextual accuracy** of the business vocabulary the chain applies. A canonical object can be mechanically correct yet semantically wrong if the BFs, BOs, CFs, and BF↔CF mappings it traces back to have wrong definitions, wrong anchoring, wrong semantic family, or missing standard references.

Ensuring contextual accuracy by hand is expensive. It requires domain SMEs who know what each business concept means, what standard it should anchor to, whether a definition is precise enough, whether two members are really duplicates. That talent is scarce, slow, and a bottleneck against the throughput the platform needs.

The Business Context Framework (BCF) specifies how AI assistance is governed to do this work. AI proposes, prepares, and approves context for the framework's three scopes (defined below). The operator overrides as exception, not as routine. The contracts chain itself is unchanged; the framework is upstream of the chain, governing the contextual quality of the business vocabulary the chain applies.

Metric concerns (MC contextual attributes, formula AST, variable binding, chain integrity, runtime-readiness) sit alongside in a sibling framework, the **Metric Context Framework (MCF)**, which integrates with substantial existing services and is specified in a separate requirements document.

## What the BCF is not

- Not a runtime component. The chain runs as Foundation defines.
- Not an active participant at any evaluation boundary. Foundation §The Evaluation Boundaries is unaffected.
- Not a producer of authoritative runtime/progression state. It does author governed grammar state through the Foundation-governed authoring path defined here. Source Objects, Canonical Objects, Metric Snapshots, Action Objects, Evidence Objects, and Lineage Objects are produced only at evaluation boundaries.
- Not a replacement for Foundation's contract grammar. Foundation §The Contract Grammar continues to define the twelve grammar artifacts and their governance.
- Not in scope for SC, AC, OC, CC composition, IC, MC (any aspect), AI Contract, Extraction Contract.

The BCF is upstream governance for the business vocabulary layer. It is the authoring discipline through which AI assistance is applied to three framework scopes so that the chain's contextual accuracy improves at sustainable cost.

## Foundation grounding

Foundation §The Authority Model establishes the three-level authority ladder (Foundation; ADRs and Errata; Descriptive layers). ADRs are the governed mechanism by which configured authoring paths are established. The BCF is itself an ADR-governed mechanism: the foundational ADR (Deferral D6) declares the framework, names its authorized actors (Context Panels, operators), specifies the disciplines each actor must satisfy, and establishes Framework Approval (defined below) as the configured authority within the framework's scope.

Within this ADR-governed mechanism, AI consensus constitutes Framework Approval for in-scope members. Operator override is the explicit exception path. The framework is not a relaxation of Foundation; it is a configuration of the governed authoring mechanism that Foundation §The Authority Model permits.

The framework preserves all six Foundation invariants:

- **Invariant I.** Meaning is produced at the canonical evaluation boundary, not in the framework.
- **Invariant II.** Object ordering is unaffected; the framework operates on grammar members, not on progression objects.
- **Invariant III.** Active grammar artifacts are immutable. AI cannot mutate an active artifact. AI may propose or prepare a successor draft for an active artifact; operator approval is required to supersede the active version. Operator override of an active artifact = operator authors a superseding new version.
- **Invariant IV.** All references identify type, identity, and version.
- **Invariant V.** AI panel outputs are immutable authoring records; audit reads them, never recomputes.
- **Invariant VI.** Authoring records are emitted at every framework write. Catalog-side authoring records are distinct from Foundation Evidence Objects, which are emitted only at evaluation boundaries.

## Authority principle

**AI proposes, prepares, and approves context for in-scope grammar members under Framework Approval. Operator overrides as exception.**

For the three framework scopes (defined below), AI consensus within the BCF's governed authoring path constitutes **Framework Approval**. Operator override is the exception path. For everything outside framework scope, the Foundation default applies: operator-only approval.

The simplification is deliberate. The cost of operator-only approval for context-only work has been the bottleneck. Within bounded scope and under bounded discipline, AI is trusted to handle the routine; the operator is trusted to catch exceptions.

### Framework Approval (defined once, used throughout)

**Framework Approval** means AI consensus may advance in-scope contextual members through the framework lifecycle under policy. It does not apply outside framework scope and does not produce runtime objects.

The BCF produces governed grammar state, not runtime state. Its approvals are Framework Approvals: scoped authoring approvals for contextual grammar members under policy. Framework Approval can make BF/BO, CF, and BF↔CF mapping versions active when all framework gates pass. It cannot emit runtime objects, approve out-of-scope contract artifacts, or extend its authority to MC concerns (those belong to the sibling MCF document).

## Foundation gate

- **Repair location: B (Contract semantics / governed grammar).** The framework governs contextual accuracy of business vocabulary members.
- **Invariants in play.** I, II, III, IV, V, VI — all preserved per the grounding above.
- **Why not D/E/F.** Implementation, storage, and read-model layers cannot be specified before B is settled.

## Scope

**In scope (three framework scopes + cross-scope coherence).**

The three framework scopes are member classes the framework governs under Framework Approval. They are not three distinct artifacts; scope 1 combines BF and BO because their context is co-governed.

1. **BF/BO contextual vocabulary** — atomic Business Field vocabulary and its composition into Business Objects.
2. **CF contextual naming** — Canonical Field naming layer.
3. **BF↔CF field-level mapping** — the meaning-anchoring relation at the field level (Foundation's Canonical Mapping per-field resolution).

Plus cross-scope coherence (BF↔BO membership, BF↔CF semantic alignment).

**Out of scope (governed elsewhere).**

- Source Contract, Admission Contract, Observation Contract (Foundation default applies; operator approval).
- Canonical Contract composition (CC-level composition decisions).
- Canonical Mapping beyond the BF↔CF field-level relation.
- Intervention Contract.
- **All MC concerns** (contextual attributes, formula AST, variable binding, chain integrity, runtime-readiness, layered lifecycle, fiscal calendar resolution, MC-envelope governance) — these are scoped to the sibling **Metric Context Framework (MCF)** document.
- AI Contract (provisional Foundation slot), Extraction Contract (retired Foundation family).
- All four evaluation boundaries and their runtime apparatus.

The boundary between BCF and MCF lives at the MC artifact: BCF governs no part of the MC. The cross-framework coordination on CF↔MC variable binding (where MCF references CFs that BCF governs) is specified in MCF.

**Vocabulary discipline.**

- Foundation Contract Grammar lifecycle vocabulary throughout (`draft → review → approved → active → superseded`).
- "Admission" reserved for the runtime admission boundary per Foundation.
- "Approve" applies to AI within the framework's scope (Framework Approval); operator approval is the operator-driven exception path within the same governed authoring mechanism.
- "Contract Binding" means the tenant-scope governance layer per Foundation Contract Grammar §Three-level governance; it is itself a governed grammar instance produced by the platform tenant-onboarding workflow.
- "Authoring record" for catalog-side proof; "Evidence Object" reserved for Foundation runtime evidence.

---

## Chapter 1 — Purpose and outcomes

### Purpose of this chapter
Establish what the BCF exists to produce, who acts on it, and the outcomes that justify its existence.

### The take

The BCF is the AI-assisted governance discipline for contextual accuracy of the three vocabulary scopes listed in Scope. It operates upstream of the contracts chain. It does not run the chain.

**The problem the framework solves.** Foundation defines the contract grammar and the four evaluation boundaries that apply it. The chain mechanics work. But the *contextual quality* of the business vocabulary the chain applies determines the quality of the chain's output. A BF with a wrong semantic family produces a poorly-anchored canonical field. Ensuring this contextual quality manually requires SME effort the organization cannot sustain at the throughput the platform needs.

**The framework's answer.** Trust AI to handle context for these scopes under Framework Approval. Bound that trust by:

- A narrow scope (only BF/BO contextual vocabulary, CF contextual naming, BF↔CF field-level mapping).
- A governed authoring path (the BCF itself, ADR-governed).
- A strict consensus discipline (three-model agreement with closed-enum verdicts).
- A no-fabrication rule (every AI claim traces to seed data or row provenance; nothing invented).
- Immutable panel records (every AI act is preserved as authoring record).
- Calibration as first-class data (sampling, regression detection, override-rate tracking).
- Operator override at every state (edit non-active; supersede active).
- Operator configurability (require explicit operator confirm for specific transitions when the operator wants a stricter gate).

**Who acts on it.**

- **Operators.** Configure the framework's policy. Monitor AI activity via the dashboard. Override AI decisions on exception (edit non-active versions; author superseding versions for active artifacts). Periodically review calibration data and re-affirm or modify policy. Operators do not routinely approve artifacts; AI handles approval by default.
- **Context Panels (AI).** Run the framework's full lifecycle for in-scope members: propose intake content, prepare draft, advance through review to approved, publish to active. Three-model consensus, closed-enum verdicts, no-fabrication, immutable authoring records.
- **Auditors.** Read-only. Inspect authoring records, panel outputs, calibration data, override history. Reads do not trigger evaluation (per Foundation §The Evaluation Boundaries).

**Who references active framework members at runtime.** Per Foundation §The Evaluation Boundaries, the four boundaries reference active grammar at evaluation time. The framework does not push to the boundaries; the boundaries read active grammar when they evaluate. BCF members are referenced indirectly: the admission boundary reads OC field selections (which reference BFs); the canonical evaluation boundary reads CC field selections (which reference CFs) and CMs (which contain BF↔CF mappings). BCF is upstream; the chain is downstream; they meet only at the read.

**Outcomes the framework must produce.**

1. Active business vocabulary members for which the contextual attributes are verified, anchored, and well-defined to a documented standard.
2. A reproducible authoring-record trail from any active member back to the AI actions and panel outputs that produced it.
3. An operator workload model in which operator time is spent on exceptions, policy management, and calibration review — not on routine context approval.
4. A defect rate low enough that the contracts chain (and the sibling MCF) can apply active members as ground truth without per-evaluation remediation.

**Outcomes the framework must NOT produce.**

- Authoritative runtime state. Source Objects, Canonical Objects, Metric Snapshots, Action Objects, Evidence Objects, Lineage Objects are produced only at evaluation boundaries.
- Per-tenant grammar forks. Tenant-scope governance lives at the Contract Binding layer per Foundation Contract Grammar §Three-level governance; the framework does not author Contract Bindings.
- AI-finalized state outside the three framework scopes. For all other catalog artifacts (including any MC concern), Foundation default applies or MCF applies.
- An operator override path that AI can disable, suppress, or circumvent.

### Open questions
- Target framework-member throughput at steady state.
- Calibration thresholds that trigger automatic framework pause.

---

## Chapter 2 — Framework scopes and scope boundaries

### Purpose of this chapter
List the three framework scopes, list what is explicitly out of framework scope (but remains governed per Foundation or by the sibling MCF), and define the relations the framework must enforce.

### The take

The BCF governs three scopes. Each scope draws from Foundation §The Contract Grammar grammar artifacts; scope 1 covers two artifacts (BF and BO) because their context is co-governed; scope 3 is a relation rather than a single artifact.

**Scope 1 — BF/BO contextual vocabulary.**
- BF: atomic vocabulary unit; carries definition, object_class, property, data_type, representation_term, semantic_family, unit_type_code, definition_standard, standard_ref, aliases.
- BO: composition of BFs; carries definition, classification, BF composition list, minimum-composition requirements.
- Combined because BFs are constituents of BOs; their context is co-governed.

**Scope 2 — CF contextual naming.**
The Canonical Field naming layer that CCs reference. CF carries definition, semantic anchoring, naming convention compliance.

**Scope 3 — BF↔CF field-level mapping.**
The field-level meaning-anchoring relation. In Foundation §The Contract Grammar, this is the per-CC field mapping carried by Canonical Mapping. The framework's scope covers the BF→CF resolution per field; it does NOT cover CC-level composition decisions or any CM concern beyond this field-level relation.

### Cross-scope coherence

The framework also governs coherence across scopes where the relation matters for contextual accuracy:

- BF↔BO coherence: the BF claims membership in a BO; the BO's composition and definition should be semantically consistent with the BF's role.
- BF↔CF coherence at the mapping: the mapped BF and CF should share semantic family, compatible unit, compatible type.

CF↔MC variable binding coherence is a cross-framework concern between BCF (CF side) and MCF (MC variable side); it is specified in MCF.

Chapter 15 specifies the within-BCF cross-scope checks.

### Explicitly out of framework scope

These remain governed grammar artifacts per Foundation §The Contract Grammar (or by MCF for metric concerns); the framework simply does not provide AI-assisted contextual governance for them.

| Artifact / concern | Governed by |
|---|---|
| Source Contract | Foundation default (operator-only) |
| Admission Contract | Foundation default |
| Observation Contract | Foundation default |
| Canonical Contract composition | Foundation default |
| Canonical Mapping beyond field-level | Foundation default or MCF (TBD) |
| Intervention Contract | Foundation default |
| MC contextual attributes | MCF |
| MC formula AST and runtime | MCF |
| MC variable binding | MCF |
| Chain integrity, runtime-readiness | MCF |
| MC-envelope governance | MCF |
| AI Contract | Provisional Foundation slot; not active |
| Extraction Contract | Retired Foundation family |
| All four evaluation boundaries | Foundation runtime |

### Relations the framework must enforce

- A BF MAY map to zero or one CF.
- A CF SHOULD be referenced by ≥1 CC or accompanied by an explicit operator-confirmed stub/intent record. BCF flags orphan CFs (no active CC reference and no stub record) as a lifecycle audit signal. **BCF does not require an active CC to activate a CF** — CC composition is out of BCF scope, so insisting on an active CC reference would leak CC composition work into BCF. Operators may activate a CF with a stub/intent record when the CC that will reference it is under separate authoring elsewhere.
- (Foundation rule, observed by BCF but not authored by BCF) A CC MUST have ≥1 CF. BCF may validate and report CC/CF reference defects it observes through Lifecycle Audit, but does not author or repair CC composition (out of scope).
- A BF MUST belong to exactly one BO.
- A BO MUST contain a minimum composition after approval.
- A BF↔CF mapping MUST satisfy semantic family / unit / type coherence (chapter 15).
- Every artifact MUST carry a version; every reference MUST identify type, identity, version per Foundation Invariant IV.

### Foundation amendment proposals (out of scope for this document)

Several questions remain about whether to amend Foundation Contract Grammar. They are surfaced as candidates for separate ADRs:
- BF/CF collapse, BO necessity, AC/OC collapse, IC scope, AI Contract activation, minimum BO composition.

---

## Chapter 3 — The Publication Eligibility Contract

### Purpose of this chapter
Define what makes a framework member eligible for publication to `active`. Publication-eligibility complements Foundation Contract Grammar's family schemas; it specifies the cross-cutting contextual conditions the BCF must verify before the AI-driven `approved → active` transition (for the three BCF scopes only).

### The take

A framework member is eligible for publication if and only if it satisfies all six:

**(PE1) Provenance.** Every member traces to (a) a recognized external standard with verifiable citation, **(b) a source-system observation with verifiable alias — provisional; subject to operator-confirm until the sufficiency question is settled (see open questions),** (c) a bc-seed catalog entry with verified provenance lineage, or (d) an operator-authored bounded-domain definition with explicit business justification. Citations and aliases are **provenance**, not Foundation Evidence Objects.

**(PE2) Anchoring.** `definition_standard` from closed enum.

**(PE3) Reference.** When `definition_standard` is external, `standard_ref` points to a real, fetchable document. No fabricated URLs, ASC references, or XBRL element names.

**(PE4) Semantic family.** From closed enum.

**(PE5) Type and unit coherence.** Type-pair valid; required unit present per semantic family.

**(PE6) Definition discipline.** Definition declares what the member IS, not why it matters. Rationale in a separate field. Definitions unique per member.

### No-fabrication rule

- AI cannot invent citations, enum values, or content not traceable to a seed row, bc-seed entry, or the member's own row provenance.
- Outputs failing the no-fabrication check are quarantined as invalid (chapter 7), preserved for calibration.

### Inconsistency intolerance

Validated on every write. Examples of intolerable states:
- `definition_standard='OAGIS'` + null `standard_ref`
- Quantity-typed BF + null `unit_type_code`
- Any pair of state-encoding columns that disagree (single `governance.state` column per Foundation Contract Grammar §Lifecycle eliminates this class).

### Open questions
- Bounded-domain vocabulary for operator-authored BARECOUNT content (and whether AI may propose BARECOUNT-anchored content when bc-seed has no candidate).
- Source-aliases-alone sufficiency for provenance.
- Multi-standard members — single ref or array?

---

## Chapter 4 — Lifecycle and state

### Purpose of this chapter
Define the lifecycle the framework enforces. Lifecycle matches Foundation Contract Grammar §Lifecycle exactly. The framework operates AI-by-default through the entire lifecycle for all three scopes; there are no scope-specific carve-outs.

### Intake queue (pre-catalog)

The catalog lifecycle begins at `draft`. The intake queue is not catalog state and not part of the Foundation lifecycle.

Proposed member content entering from upstream sources (source-schema scanners, standards importers, bc-seed catalog, operator Authoring Tool) resides in an intake queue before any catalog state is created. Intake-queue entries:

- Do not carry a Foundation lifecycle state.
- Are not subject to PE1-PE6 validation until they transition out of intake into `draft`.
- Are not referenced by any evaluation boundary; the four boundaries reference only `active` grammar per Foundation Invariant IV.
- May be discarded by the Context Authoring Panel REJECT path with consensus + closed defect-code, without producing a `draft` row.

The Context Authoring Panel operates on the intake queue and routes each entry to one of three outcomes:
- **Reject** → entry written to the Authoring Panel Rejection Log; no catalog row created. AI rejects under guardrails; operator override available (chapter 6).
- **Advance to `draft`** → catalog row created; row enters Foundation lifecycle at `draft`. AI executes this transition by default unless operator-confirm policy is in effect.
- **Operator review queue** → entry routes to operator queue when panel cannot reach consensus or detects an out-of-scope concern.

Intake-queue entries not processed within a configured window are auto-aged-out; aging is an authoring record but creates no catalog row.

### Foundation Contract Grammar lifecycle (five states)

Per Foundation Contract Grammar §Lifecycle and deprecation policy:

```
draft → review → approved → active → superseded
```

Five states only. Foundation does not define `withdrawn`, `deprecated`, `retired`, or `archived` at the version level. Family-level retirement is a separate ADR-governed act.

The framework introduces no states beyond these five.

### AI-by-default lifecycle progression (uniform across all three scopes)

For all three framework scopes:
- AI runs `intake → draft → review → approved → active` under Framework Approval.
- Each transition is an immutable authoring record with panel run UID, prompt version, model identity per agent, workbench fingerprint (per chapter 7), per-agent transcript uid, verdict, grounding check result, policy version.
- Operator override is available at every state (chapter 5).

### Transition rules per Foundation

Every transition is append-only. No transition can be edited or deleted. Historical state at any past timestamp is reconstructible by replaying authoring records.

The transition gates the framework enforces:

- `intake → draft` — AI executes by default after Context Authoring Panel APPROVE_FOR_DRAFT or operator confirms if operator-confirm-required policy is in effect.
- `draft → review` — AI executes by default after Context Authoring Panel completes contextual enrichment.
- `review → approved` — AI executes by default after Context Publication Panel APPROVE consensus + PE1-PE6 deterministic publication gate pass.
- `approved → active` — AI executes by default under Framework Approval.
- `active → superseded` — operator-driven supersession with explicit successor pointer. AI cannot supersede active artifacts. Per Foundation Invariant III, supersession is the only mechanism to change active state.

### Operator override mechanisms

Per Foundation Invariant III, active artifacts are immutable. Operator override therefore takes two forms:

- **Edit a non-active version in place.** A member in `draft`, `review`, or `approved` may be edited by the operator. The version stays in its current state; the edit emits an authoring record. AI's next pass operates on the edited content.
- **Supersede an active version.** An operator may at any time author a new version of an active member. When the new version reaches `active`, the prior version moves to `superseded` per Foundation Contract Grammar §Lifecycle. The prior version remains addressable per Foundation Invariant III.

The framework MUST provide UI for both override mechanisms (chapter 6).

### Operator-confirm policy override

The operator may configure the framework to require explicit operator confirm for specific transitions of specific members under specific conditions. Examples:
- "For new BOs with no active twin, require operator confirm at `review → approved`."
- "For any BF authored by an importer that has emitted >5% rejected intake entries in the last 7 days, require operator confirm at `draft → review`."

Operator-confirm requirements are a configuration of the BCF policy (chapter 7). They are not a separate operating mode; the framework's default operation continues unchanged for all transitions not covered by an explicit operator-confirm rule.

### Open questions
- Whether `correction_required` (a workflow holding pen used outside Foundation lifecycle) should be promoted to a first-class Foundation lifecycle state via amendment ADR or remain operational vocabulary inside the framework.
- Semver bump rules per edit kind (per-family specifics).
- Intake queue aging window.
- Detailed operator-confirm rule grammar.

---

## Chapter 5 — Division of labor

### Purpose of this chapter
Define who can write what, when, why. Anchored in Foundation §The Authority Model and the Authority principle declared at the top of this document.

### Authority principle (preamble)

**AI proposes, prepares, and approves context for in-scope grammar members under Framework Approval. Operator overrides as exception.**

For framework members (members in any of the three framework scopes), AI consensus within the BCF's governed authoring path constitutes **Framework Approval** as defined at the top of this document. Operator override is the exception path. For everything outside framework scope, the Foundation default applies: operator-only approval.

### The take

**Seven actors. Two paths.**

| Actor | Authority on framework members | Authority outside framework |
|---|---|---|
| Tenants | None (data supplier only) | None |
| Source systems | None (input only) | None |
| Standards bodies | None (input only) | None |
| bc-seed catalog | None (input only — provides candidate vocabulary for AI to draw from) | None |
| Rule-based classifiers | Filter only (shortlist; never approve) | Filter only |
| Context Panels (AI) | Propose, prepare, approve (Framework Approval) | Recommend only; cannot finalize |
| Deterministic publication gates | Refuse-only | Refuse-only |
| Operators | Override (exception); configure policy; supersede active artifacts | Sole approval authority |

Tenants are listed explicitly to make the boundary clear: tenants supply observable source data via connection; the admission boundary acts on it. Tenants are not actors on the catalog.

**Three immutable rules.**

**Rule 1.** Framework Approval within the BCF is a governed authoring path established by ADR per Foundation §The Authority Model. The path requires three-model consensus, closed-enum verdict, no-fabrication check pass, immutable authoring record, calibration sampling enrollment, and an active operator override mechanism. A Framework Approval that fails any of these conditions is not a valid approval.

**Rule 2.** Operator override is always available. The framework MUST provide UI for operator to (a) edit any non-active version, (b) supersede any active version, (c) pause the framework's policy, (d) configure operator-confirm requirements for specific transitions. The framework MUST NOT disable, suppress, or circumvent any operator override mechanism.

**Rule 3.** The authoring-record trail is non-bypassable. Every framework write produces an immutable authoring record (Foundation Authority Model audit discipline). Every Framework Approval references the panel output IDs, per-agent transcript uids, workbench fingerprint, prompt version, model identity, grounding check result, and policy version that produced it.

### Implications

Under the BCF's default operation, AI is the primary actor: intake review and lifecycle progression through `active` are AI-executed under Framework Approval, subject to three-model consensus, deterministic publication gates, and the operator override mechanisms. Active-state changes (supersession) remain operator acts per Foundation Invariant III. Operators participate by configuring policy, monitoring AI activity, overriding on exception, and approving operator-confirm cases.

### Out-of-scope authority

For all catalog artifacts outside the three framework scopes (SC, AC, OC, CC composition, CM beyond field-level, IC, MC concerns of any kind, AI Contract, Extraction Contract), the Foundation default applies: AI may propose but only operator may approve. The BCF does not extend Framework Approval authority to these artifacts.

### Open questions
- Whether there is a "Super-operator" role with authority to override specific framework configurations.
- Whether bulk supersession of framework-approved active artifacts has a separate authority model.

---

## Chapter 6 — Operator Surfaces (UI requirements)

### Purpose of this chapter
Specify UI surfaces the operator needs. Under the AI-by-default model, operator UI is **monitor + override + policy management**, not routine approval.

### The take

**Default operator workflow.** The operator does NOT see every member as it progresses. The operator monitors AI activity, gets notified per configured policy, drills into exceptions, overrides when needed, and periodically reviews calibration data. The framework MUST be usable by an operator who interacts with it for an hour a day, not all day.

### Required operator surfaces

| Surface | What it does |
|---|---|
| **Activity Dashboard** | Stream of AI activity across all three framework scopes. Filterable by scope, member, action, lifecycle transition, panel verdict, sampling status, policy version. The operator's home screen. |
| **Operator Notifications** | Configurable notifications: real-time for high-stakes events; digest for routine; threshold-based for anomalies. Per-policy and per-member rules. |
| **Per-Member Detail View** | Drill into any framework member at any version. See AI's full work history: panel output records, per-agent transcripts (Maker, Checker, Moderator workbench tool-call trails) linked from each panel run, authoring records per transition, calibration sampling outcomes for this member. Operator can edit the non-active version inline or initiate a superseding version for the active version. |
| **Override Action** | One operator action per override: edit (non-active) or supersede (active). Override emits an authoring record with operator rationale text required. |
| **Policy Management** | Configure framework policy per scope: required consensus, sampling rate, operator-confirm rules, notification rules. Pause/resume any policy. Modify-and-version policy (per chapter 7). |
| **Calibration Dashboard** | Per-scope, per-stage precision over time. AI-approval-vs-operator-override rate per member. Sampling outcomes. Calibration regression alerts. This is the single most important surface for evaluating whether to trust the framework. |
| **Authoring Panel Rejection Log** | Browse intake-queue entries the Authoring Panel rejected. Operator can override individual rejections, advancing the entry to `draft` with `manual_override_after_reject` provenance. |
| **Reference Impact Viewer** | When operator considers superseding a framework member, shows which downstream artifacts (CCs, MCs in MCF scope, ICs, active Contract Bindings) reference it. Critical for impact analysis. |
| **Activity Log** | Full immutable history of every framework write, panel call, AI approval, operator action, policy change, calibration event. Per chapter 10 NF1. |
| **Authoring Tool** | Operator-driven authoring surface for cases where the operator initiates a new framework member directly (rather than relying on importer-driven intake or bc-seed proposals). Produces an intake-queue entry; AI then takes over per default. |

### Out-of-scope surfaces

- Routine "approve this artifact" surface. Operator does not approve as default; the framework approves.
- Per-member approval queue. Operator does not have a queue of members to approve; AI handles approval.

### Per-scope UI specialization

Each of the three framework scopes has specifics covered in its dedicated chapter (12-14). The generic surfaces above are extended per scope.

### Authority bounds in UI

Every UI surface enforces chapter 5's authority bounds. UI affordances must not exist for actions the current role is not authorized to take. The framework MUST NOT expose UI affordances that would disable, suppress, or circumvent operator override mechanisms.

### Operator-confirm UI

When the operator has configured "require operator confirm" for specific transitions, the framework MUST surface those pending confirms in the Operator Queue (a sub-view of the Operator Notifications surface). The operator-confirm UI presents the AI's verdict and provenance and asks for operator yes/no plus rationale.

### Open questions
- Whether UI lives in one application, separate application, or split per member family.
- Role model (operator / auditor / super-operator).
- Mobile/tablet surfaces.
- Notification UX (in-app, email, push, integration with existing operator tooling).
- Calibration dashboard alert thresholds.

---

## Chapter 7 — Context Panels (AI role specification)

### Purpose of this chapter
Specify the three AI panels that constitute the BCF's AI machinery. Each panel operates on a specific stage of the framework lifecycle across the three framework scopes. There are no scope-specific carve-outs; each panel handles all three scopes uniformly under Framework Approval. Context Curation is a function woven into the Authoring and Publication panels in v1, not a separate required panel.

### Naming

The three panels are collectively the **Context Panels**:

| Stage | Panel name |
|---|---|
| 1 | **Context Authoring Panel** — intake review and `intake → draft` transition |
| 2 | **Context Publication Panel** — review of draft/review members; `review → approved` and `approved → active` transitions |
| 3 | **Context Lifecycle Audit Panel** — periodic audit of active members for drift, duplicate accretion, boilerplate, regression |

**Context Curation is a function, not a separate required panel in v1.** It is woven into the Authoring and Publication panels' end-to-end work (proposing enrichments, recommending standard refs, suggesting reductions). A separately-invokable Curation surface may be added in a future version if operators need curation-only operations (e.g. "propose enrichment candidates for review without auto-applying"), but it is not part of v1.

### Context Panels as governed tool workbenches — framing

Each Context Panel is a **governed tool workbench**, not a packet-in / verdict-out function. Vocabulary authoring requires the panel to be aware of the live registry shape (existing entities, synonym candidates, lifecycle states, supersession history) and the allowed evidence corpora (standards, bc-seed) so it can avoid stupid proposals and ground real ones. A panel limited to a precomputed input bundle would be brittle in both directions: unable to disambiguate genuine synonyms from near-duplicates without seeing the live registry, unable to discover the right standards excerpt without searching.

The operative principle:

> **Governed tools = safe enough to reason. Raw substrate access = dangerous.**
> **The panel has complete awareness of the governed platform, not complete access to the database.**

That gives the panel enough context to make good vocabulary decisions while keeping authority clean.

#### Allowed tool surface for BCF panels (closed set, v1)

The workbench exposes a closed set of tools. Each tool call is logged, input-hashed, output-hashed, included in the panel run transcript, scoped to an allowed surface, and blocked from quarantined/dropped surfaces. Tool calls are replayable as audit evidence; they are not re-used as authority unless the panel cites them correctly through PE1.

| Tool | Purpose |
|---|---|
| `registry.search_entity` | Find existing `concept_registry.entity` rows by name / family / domain |
| `registry.search_business_concept` | Find existing `concept_registry.business_concept` rows on an entity / by kind / by representation term |
| `registry.search_characteristic` | Find existing `concept_registry.characteristic` rows by term / definition similarity |
| `registry.read_entity` | Read a specific entity by id (identity-bearing properties, lifecycle state, reachable entities via identity-references) |
| `registry.read_business_concept` | Read a specific BC by id (kind, representation term, unit, home entity, lifecycle state) |
| `registry.read_characteristic` | Read a specific characteristic by id |
| `registry.collision_probe` | Probe for synonym / homonym collision against a proposed identity tuple (e.g. duplicate `(entity_id, property_id)`) |
| `registry.lifecycle_probe` | Inspect lifecycle state, supersession lineage, prior versions |
| `registry.alias_probe` | Inspect aliases / normalized-name candidates that already exist |
| `source_reality.summarize` | Summarize what source / admission / observation contracts exist for a tenant, what fields they emit |
| `evidence.search` | Search the allowed evidence corpora (standards, bc-seed, curated standard excerpts) |
| `evidence.retrieve` | Retrieve a specific evidence document by URI from the allowlist |
| `bc_seed.read_entry` | Read a bc-seed catalog entry with its provenance lineage |
| `panel_history.read` | Read prior panel outputs / rejection-log entries / supersession history for the same candidate area |
| `cert_history.read` | Read certification records (BCF action_codes) for the same candidate area |
| `pe.check` | Run the deterministic PE1–PE6 publication-eligibility checks against a candidate proposal |
| `mcf.consumer_count` (post-MCF) | Read how many MCF MCs reference a candidate BC (consumer-count for downstream impact) |

The tool surface explicitly **does not include**:

- Raw DB / SQL access.
- Any tool that touches the historically-quarantined-now-dropped surfaces (BF, BO, BOF, BOR, BFA, CF, CM — physically gone post-D418; even if present, the working rule would forbid).
- Arbitrary application tables (no `tenant.*` data, no `runtime.*` runtime state, no random DB tables).
- Raw tenant data (admitted observation rows, source rows).
- Unscoped operator notes (operator-provided context is a tracked workbench input per below, not a free-form data plane).
- Arbitrary internet retrieval (would violate no-fabrication grounding; citations must come from the allowlist).
- Tools that write `concept_registry.*` (the substrate writes are the Framework Approval / publication path, not panel-callable).
- Tools that bypass PE1–PE6.

#### Tool-call discipline

Every tool call satisfies the six discipline conditions:

1. **Logged** — recorded in the per-model transcript with timestamp.
2. **Input-hashed** — the tool call's parameters are hashed and stored.
3. **Output-hashed** — the tool's response payload is hashed and stored.
4. **Included in the panel run transcript** — the per-model immutable transcript carries the full call/response trail.
5. **Scoped to an allowed surface** — the workbench enforces the closed tool allowlist.
6. **Blocked from quarantined/dropped surfaces** — the workbench refuses calls that would touch the post-D418 dropped substrate.

Tool calls are **replayable as audit evidence** (an auditor reads each per-agent transcript and sees exactly what that agent saw and how it reasoned) but are **not re-used as authority unless the agent cites them correctly** through PE1's grounding citation rules. A tool result the agent didn't cite in its proposal is not part of the authority chain even though it's part of the audit trail.

#### Operator-provided context

When the operator initiates a panel run, they may attach free-text business guidance ("this BF candidate is part of a regulated-disclosure context; treat synonym tolerance as zero"). Operator context is a **workbench input** — hashed into the workbench fingerprint as the operator-context-hash axis, visible in each per-agent transcript — but it is **not authority evidence**. The panel may not cite operator context as a PE1 grounding source; it informs reasoning, not authority.

### Stage 1 — Context Authoring Panel

**When it runs.** When a proposed member lands in the intake queue (from source-schema scanner, standards importer, bc-seed catalog, or operator Authoring Tool).

**What it operates on.** The intake queue (pre-catalog state).

**What it judges.** Structural coherence; definition discipline; upstream-pipeline defects; duplication against existing active members; coherence with bc-seed candidates when applicable.

**What stays operator-only.** The framework does not strictly forbid AI from proposing on any judgment dimension, but operator-confirm rules (per chapter 4) MAY be configured to require explicit operator confirm for specific high-stakes decisions (e.g. proposing a novel BARECOUNT definition with no bc-seed lineage). The discipline is configurable rather than carved-out.

**Authority.** Three possible outcomes:

- **REJECT** — Panel rejects an intake entry before it becomes a catalog row when all three models agree on REJECT_BAD_MODEL, the defect code is on the closed REJECT-eligible list, and the rejection is preserved in the Authoring Panel Rejection Log. Operator override is available via the Rejection Log surface. Operator override advances the entry from rejection-log to `draft` with `manual_override_after_reject` provenance.

- **OPERATOR_REVIEW** — Panel routes to operator queue when (a) the three models disagree, (b) the defect is out-of-list, (c) the row triggers an operator-confirm rule, or (d) no-fabrication check returns quarantined output.

- **APPROVE_FOR_DRAFT** — Each of the three agents independently proposes the row's contextual content using the governed workbench; on consensus over those proposals the framework writes the row to `draft` with that content, attaching the consensus panel output and per-agent transcript references as authoring evidence. AI executes this transition by default unless operator-confirm policy is in effect.

### Stage 2 — Context Publication Panel

**When it runs.** Periodically on draft/review members per scheduled cadence, or on-demand for ad-hoc operator request.

**What it judges.** Whether the contextual attributes are complete and coherent enough for publication. PE1-PE6 must hold. No duplicates of active members. Cross-scope coherence per chapter 15.

**Authority.** For all three scopes: the panel executes the full path `draft → review → approved → active` under Framework Approval (three-model consensus, closed-enum verdicts, no-fabrication check, operator-confirm rules). Each transition emits authoring records. Operator override available at every state.

Per-scope specifics in chapters 12-14.

### Stage 3 — Context Lifecycle Audit Panel

**When it runs.** Scheduled per audit type (daily for drift, weekly for boilerplate, monthly for duplicate accretion across active members), or on-demand.

**What it judges.** Drift in active members vs their authoring records; duplicate accretion (new active members semantically overlapping existing); boilerplate (same definition text on distinct members); calibration regression (operator override rate climbing on a given member).

**Authority.** Cannot mutate active artifacts (Foundation Invariant III). Outputs:
- Tickets in Operator Queue for operator review.
- Reports filed to the Activity Log.
- Calibration regression triggers automatic framework pause for the affected scope (chapter 9 F12).
- Drift detection on an active member triggers a supersession proposal — AI prepares a successor draft candidate; operator approves the successor's activation, and at that activation the prior active version moves to `superseded` per Foundation Invariant III.

### Three-model consensus policy

Where Maker, Checker, and Moderator independently return the same closed-enum verdict on a candidate proposal, the framework treats that verdict as consensus. Consensus alone is not sufficient for approval; it must be supported by row provenance, seed data, bc-seed lineage, deterministic validation, and closed defect-code or APPROVE-eligible code evidence appropriate to the action.

**Consensus validity requires same workbench, not same input bundle.** Maker, Checker, and Moderator each operate in the same governed tool workbench (per the framing subsection above): same allowed tool set, same evidence-source allowlist, same registry snapshot at workbench open, same policy version, same operator-provided context. Each model runs its own interactive tool transcript and produces its own proposal independently. Consensus is computed over the three proposals.

This is a deliberate shift from the earlier "same input snapshot" rule. Vocabulary authoring requires interactive registry inspection (collision probes, lifecycle reads, alias checks) that a precomputed bundle cannot supply. Same-workbench preserves the discipline (every model sees the same governance surface) while permitting each model's reasoning to take its own path through the available tools.

The framework MUST detect workbench divergence — if Maker, Checker, and Moderator open against different tool allowlist versions, different evidence-source allowlist versions, different registry snapshots, or different operator-context hashes, their proposals do not constitute consensus and the run routes to OPERATOR_REVIEW. The **workbench fingerprint** (a hash over the four versioned axes plus operator-context hash) is the artifact that's checked for equality across the three model runs.

### Panel outputs are immutable authoring records

Every Context Panel run produces an immutable record containing:

- Panel stage and panel run UID.
- Prompt version (per agent).
- Model identity (provider + model version) per agent.
- **Workbench fingerprint** — hash over (tool allowlist version + evidence-source allowlist version + registry snapshot id + policy version + operator-context hash). Equal across the three model runs is the consensus-validity precondition.
- **Per-agent transcript uid** — Maker, Checker, Moderator each produce an immutable interactive transcript containing every tool call (input hash + output hash + timestamp), every reasoning chunk, and the agent's proposal + verdict.
- Verdict (closed-enum value, computed as consensus over the three per-agent verdicts).
- Grounding check result per claim in the consensus proposal (no-fabrication validation outcome — every cited evidence trace links back to a tool call in the citing agent's per-agent transcript that retrieved an allowed source).
- Policy version under which the panel was invoked.
- Sampling status (whether this output is part of the calibration sample routed to operator review).

The per-agent transcripts ARE the audit artifact — each is replayable by an auditor reading the recorded tool calls + responses + reasoning + verdict for that agent, never by re-invoking the panel. Per-agent transcripts are append-only. Panel output records reference the three per-agent transcripts but are themselves the consensus-level summary.

Panel output records are append-only. Cannot be edited or deleted. Audit MUST read these records, MUST NOT re-invoke panels to reconstruct historical verdicts (Foundation Invariant V).

**Quarantined outputs (failed no-fabrication check) are preserved, not discarded.** Marked `quarantined: true`, blocked from action, retained for calibration analysis. The quarantine population is a first-class panel-quality signal. A common quarantine mode for the workbench era: a claim in an agent's proposal does not trace to any tool call in that agent's transcript (the model fabricated rather than searched).

### Framework policy

The BCF's operation is governed by an ADR-established policy that declares, per scope:

1. **Eligible operations** — which transitions AI can execute.
2. **Required consensus** — three-model agreement required; closed-enum verdicts.
3. **No-fabrication check** — mandatory.
4. **Sampling/audit rate** — load-bearing; defines what fraction of AI executions routes to operator review for calibration. Minimum greater than zero. Operator-tunable.
5. **Operator-confirm rules** — conditions under which AI pauses for explicit operator confirm.
6. **Reversal path** — explicit reversal mechanism per Foundation Invariant III (edit non-active; supersede active).
7. **Notification policy** — when and how the operator is notified of AI actions.
8. **Calibration regression thresholds** — operator-override rate, false-positive rate, false-negative rate at which the framework auto-pauses pending operator review.

### Framework policy execution rule (bounded-write discipline)

An AI approval may write catalog state only when ALL of the following hold:

- The policy authorizes the specific transition for the specific scope.
- The three-model consensus is valid (same-workbench rule satisfied — equal workbench fingerprint across the three model runs).
- The grounding check passes (no fabrication detected — every claim in the consensus proposal traces to a tool call in the per-agent transcripts).
- The sampling decision has been recorded (whether this write is part of the calibration sample).
- The action emits an immutable authoring record referencing policy version, panel output IDs, per-agent transcript uids, workbench fingerprint, sampling status, and any applicable operator-confirm bypass record.
- No operator pause is active on the policy.
- No operator-confirm rule applies to this specific case (or the operator has already confirmed).

Any condition failure routes the action to OPERATOR_REVIEW rather than executing.

### Operator-tunable policy bounds

Operator may configure the policy to introduce additional bounds. Examples:
- Require operator-confirm for any framework write on a member in a specific functional domain.
- Require operator-confirm before activating any successor version that would supersede an active member. (Note: per chapter 4, only operator can actually execute the supersession; this rule adds explicit confirm on the AI-proposed successor's transition to active.)
- Disable AI authority for a specific transition entirely for a specific period.

These configurations operate within the framework's normal mechanism; they tighten policy without changing the basic AI-by-default + operator-override model.

### Framework policy changes are governed authoring acts

Modifying the framework policy is itself a catalog authoring act:

- Requires recorded operator justification.
- Emits an event captured in the Activity Log.
- Carries its own ADR-style change record per Foundation §The Authority Model.
- Versioned; AI actions in flight at policy-change time complete under the version they started with.
- Activity Log entries reference the policy version that authorized each AI action.

### Sunset and review cadence

The framework policy must be reviewed at least quarterly:

- Operator reviews accumulated calibration data (sampling outcomes, override rates).
- Operator reviews calibration regressions and their resolutions.
- Operator either re-affirms (next quarter), modifies (creates new version), or sunsets (disables AI authority for affected scopes or transitions).
- Policy not re-affirmed within the review window auto-disables, requiring operator action to re-enable.

Calibration regression (chapter 9 F12) can trigger out-of-cycle review.

### Cross-cutting Context Panel policy

- **Provider diversity.** Target Gemini Maker / OpenAI Checker / Claude Moderator for high-stakes panels (Publication Panel, Lifecycle Audit Panel). Authoring Panel and Curation-style operations MAY be Claude-only initially with explicit labeling. Three-model consensus is required regardless of provider diversity.
- **Where AI runs.** Dedicated AI service. Harness-based ad-hoc invocation for development with "harness-mode" labeling. In-process API-server AI calls prohibited.
- **Cost budget.** Per chapter 10 NF5.
- **Latency budget.** Per chapter 10 NF4.
- **No-fabrication.** Enforced as system invariant. Outputs failing the check are quarantined, not discarded.
- **Panel output immutability.** All panel outputs are immutable authoring records per above.
- **Calibration as first-class.** Per chapter 10 NF7. The sampling rate is load-bearing; the operator override rate is load-bearing; both drive panel tuning and policy review.

### Open questions
- Closed list of REJECT-eligible defect codes for Authoring Panel.
- Closed list of APPROVE-eligible verdicts per stage.
- Whether Maker/Checker/Moderator triple is right for all panels or stage-specific.
- Minimum sampling rate.
- Calibration regression thresholds.
- Intake queue aging window.
- **Workbench tool-set v1 schemas** — exact request/response shapes per tool listed in the framing subsection; versioning rules.
- **Evidence-source allowlist composition and curation** — which standards / corpora are admissible; who curates; cadence; versioning for transcript reproducibility.
- **Workbench fingerprint algorithm** — exact hash construction over (tool allowlist version + evidence-source allowlist version + registry snapshot id + policy version + operator-context hash).
- **Per-agent parallel tool calls vs sequenced** — whether Maker, Checker, Moderator run in parallel against the workbench (each producing an independent transcript) or whether some tool calls are shared. Working position: parallel + independent transcripts.
- **Operator-provided context boundary** — confirm that operator context is workbench input (hashed into the workbench fingerprint via the operator-context-hash axis) but never authority evidence (not citable as PE1 grounding).
- **Tool-call output retention policy** — transcripts may grow large (especially evidence retrievals); retention vs summarization rules.

---

## Chapter 8 — How members are referenced

### Purpose of this chapter
Describe how active framework members are referenced by acts outside the framework, and how the framework consumes inputs from upstream sources. Per Foundation §The Evaluation Boundaries, reads do not trigger evaluation.

### The take

**Inputs to the framework.**

- **Source-schema scanners** — produce intake-queue entries for BF candidates from observed source systems.
- **Standards importers** — produce intake-queue entries for BF/CF candidates with citations from standard vocabularies (OAGIS, US-GAAP via XBRL, IFRS, ISO 20022, COSO, IIA).
- **bc-seed catalog** — a verified-provenance seed catalog the AI can draw from when proposing candidates. The framework treats bc-seed as a first-class candidate source: the no-fabrication rule (chapter 3) recognizes bc-seed lineage as valid provenance, meaning the AI did not invent the reference. **Publication gates still verify** that the referenced source is valid, current, and admissible — bc-seed lineage is provenance input, not approval authority. Particularly load-bearing for BFs.
- **Operator Authoring Tool** — produces intake-queue entries via operator submission.
- **Context Authoring Panel** — reviews and gates intake-queue entries.

**Reference relations the framework supports.**

Once a framework member is `active`, it is referenced by:

- **Foundation evaluation boundaries.** The four boundaries reference active grammar at runtime. For framework members:
  - Admission boundary references BFs indirectly via OC field selections.
  - Canonical evaluation boundary references active CCs (out of BCF scope) which themselves reference active CFs (BCF scope 2) and apply the BF↔CF mapping (BCF scope 3).
  - Metric evaluation boundary references active MCs (out of BCF scope, in MCF scope) which themselves reference CFs (BCF scope 2).
  - Action evaluation boundary references active ICs (out of BCF and MCF scope).
- **Sibling MCF framework.** MCF references active CFs (BCF scope 2) for MC variable binding. The cross-framework coordination protocol is specified in MCF.
- **Contract Binding layer** per Foundation Contract Grammar §Three-level governance. Contract Bindings reference active grammar versions; produced by platform tenant-onboarding workflow, not by the framework.
- **Other catalog artifacts** (CCs, CMs, MCs) that reference active CFs and BFs.
- **Operator and auditor UI** for read-only inspection.

**Sideways governance interactions.**

- Activity Log surface for every framework write.
- Decision lifecycle: ADRs reference framework members by UID per Foundation §The Authority Model. The framework's policy itself is ADR-governed.
- Foundation-compatibility validation: framework writes validated against Foundation Contract Grammar schemas.
- Semantic verdict system: active framework members that drive evaluation feed into the platform semantic verdict system where defined.

### Open questions
- Whether framework publishes change notifications (push) or boundaries poll active versions (pull).
- Read-only public API for member validation.
- In-engine vs out-of-engine documentation generation.
- bc-seed integration protocol (push from bc-seed to intake, or pull on-demand from Authoring Panel).

---

## Chapter 9 — Failure modes

### Purpose of this chapter
Enumerate failure modes; for each, define detection, notification, remediation, reversibility.

### The take

**F1 — Source drift.** Source-system schema changes; existing BF aliases invalid.
- Detection: source-schema scanner diffs.
- Notification: ticket per affected member.
- **Remediation: operator-triggered from the ticket only. AI does NOT auto-remediate active members under source drift because doing so could break live downstream dependencies (active Contract Bindings, MCF variable bindings, downstream evaluations). Operator reviews the ticket, assesses live risk, and triggers the appropriate action (re-alias, supersession, or no-action).** AI may propose remediation candidates in the ticket; the action itself is operator-triggered.
- Reversibility: prior aliases preserved as authoring records.

**F2 — Provenance decay.** Cited URL returns 404; reference withdrawn.
- Detection: scheduled link-check.
- Notification: ticket per stale citation.
- Remediation: operator-triggered from ticket. AI may propose replacement from seed catalog or bc-seed; operator decides whether to apply replacement, supersede, or accept the gap.
- Reversibility: original citation preserved.

**F3 — Duplicate accretion.** Multiple active members for same concept.
- Detection: Context Lifecycle Audit Panel duplicate-detection pass.
- Notification: ticket with proposed merge.
- Remediation: AI proposes supersession of duplicate by canonical member; operator approves the supersession (per Foundation Invariant III, only operator can author superseding active version).
- Reversibility: both preserved; merge is explicit supersession.

**F4 — Context Panel disagreement.** Maker says STRONG_FOR, Checker says REJECT, Moderator must adjudicate.
- Detection: built into panel structure.
- Notification: panel output includes disagreement flag.
- Remediation: Moderator verdict; escalation to operator via OPERATOR_REVIEW if undecidable. Disagreement precludes Framework Approval.
- Reversibility: all panel outputs preserved.

**F5 — Operator absence on override path.** AI approves a member; operator does not review the calibration sample for N days.
- Detection: sample-review-age monitor.
- Notification: SLA escalation; reminder to operator.
- Remediation: framework continues to operate; calibration data accumulates without operator review. If sample-review-age exceeds the calibration-regression threshold, framework auto-pauses the affected policy pending operator action (F12).
- Reversibility: AI actions remain reversible via the declared reversal path.

**F6 — State inconsistency.** Framework member in impossible state combination.
- Detection: state-invariant validator on every write AND periodically.
- Notification: immediate alert.
- Remediation: AI cannot reconcile; operator-driven reconciliation.
- Reversibility: full state history preserved per Foundation Invariant III.
- Prevention: single `governance.state` column per Foundation Contract Grammar eliminates this class by construction.

**F7 — Reference impact at supersession.** Superseding an active framework member that other artifacts (CCs, MCs in MCF scope, ICs, active Contract Bindings) reference.
- Detection: dependency check on every supersede attempt.
- Notification: per-referencer notification (including MCF if MC variable binding affected).
- Remediation: AI proposes the supersession; operator must approve given the impact analysis. Operator may also choose to leave the prior version active and start the new version as a parallel option per Foundation Invariant III.
- Reversibility: superseded version remains addressable per Foundation Invariant III.
- UI: Reference Impact Viewer.

**F8 — Provenance forgery attempt.** AI panel output references a fabricated citation.
- Detection: grounding check; gate fetches and verifies every external citation; sampled re-verification on active members.
- Notification: hard rejection at gate; quarantine of panel output; calibration alert.
- Remediation: rejected at write; investigation if pattern repeats.
- Reversibility: nothing was written.

**F9 — AI service outage.** Context Panel service unavailable.
- Detection: heartbeat monitor.
- Notification: alert; AI-driven transitions pause.
- Remediation: AI service restored; queue drained. During outage, operator may execute transitions manually (this is operator override, available at any time).
- Reversibility: queued work resumes from queued state.

**F10 — AI false-positive REJECT.** Authoring Panel rejects a legitimately novel intake entry.
- Detection: rejection log review; calibration alert on rising reject rate.
- Notification: operator-visible.
- Remediation: operator override via rejection log UI; panel tuning if pattern persists.
- Reversibility: override advances entry to `draft`.

**F11 — AI false-positive APPROVE.** AI approves a member whose context is wrong.
- Detection: calibration sample reveals the operator-override rate climbing on a member type or transition; lifecycle audit detects drift between an active member and standards or peer members.
- Notification: per-sample notification to operator if override is detected; framework auto-pause if rate exceeds threshold (F12).
- Remediation: operator authors superseding correct version; or operator pauses the policy, edits the affected non-active versions, and unpauses.
- Reversibility: per Foundation Invariant III, the wrong active version remains addressable but is superseded.

**F12 — Calibration regression triggers framework pause.** Per-policy operator-override rate, false-positive rate, false-negative rate, or quarantine rate exceeds the configured threshold.
- Detection: NF7 calibration regression detector.
- Notification: out-of-cycle review trigger; framework auto-pauses the affected policy.
- Remediation: operator reviews calibration data; reviews recent panel outputs; pauses, modifies, or sunsets policy.
- Reversibility: pause means AI cannot execute new transitions under that policy until operator action.

**F13 — Workbench divergence across agents.** Maker, Checker, Moderator open against different workbench configurations (different tool allowlist version, different evidence-source allowlist version, different registry snapshot id, different policy version, or different operator-context hash) and produce apparently-agreeing proposals over inequivalent governance surfaces.
- Detection: consensus-evaluation-time workbench-fingerprint comparison across the three agents (per chapter 7 §"Three-model consensus policy"). Fingerprint equality is the consensus-validity precondition.
- Notification: route to OPERATOR_REVIEW with workbench-divergence flag, naming the divergent axis.
- Remediation: operator reviews; if intentional re-run desired, operator triggers a fresh panel pass with a single workbench opened uniformly across all three agents.
- Reversibility: no AI action took place.

**F14 — Panel output corruption / loss.** Panel output record unavailable.
- Detection: audit-query integrity check.
- Notification: immediate alert; affected AI executions flagged un-auditable.
- Remediation: panel outputs are append-only and replicated per NF1; recovery from replica. If unrecoverable, affected Activity Log entries flagged `provenance_gap: true`; operator-reviewed.
- Reversibility: AI actions with unrecoverable provenance are candidates for operator-driven reversal under the policy's reversal path.

**F15 — Policy misconfiguration.** Policy permits AI authority outside framework scope or violates Rule 1/2/3.
- Detection: policy validator on every save runs against framework rules at config-time.
- Notification: hard reject at config save with cited rule.
- Remediation: operator corrects policy.
- Reversibility: misconfigured policy never activated.
- Prevention: UI affordances cannot expose configuration paths that would violate framework rules.

### Open questions
- SLA numbers for sample-review-age and operator-confirm-pending-age.
- Specific calibration regression thresholds per scope.
- F9 fast-track behavior during AI outage.
- Failure modes specific to multi-standard members.

---

## Chapter 10 — Non-functional requirements

### Purpose of this chapter
Specify behavior dimensions not covered as functional features.

### The take

**(NF1) Auditability.** Every framework write produces an immutable authoring record per Foundation §The Authority Model. AI approvals are first-class authoring events with panel output IDs, **workbench fingerprint, per-agent transcript uids** (each transcript being the model's full interactive tool-call trace + reasoning + verdict per chapter 7), sampling status, reversal path, policy version, and operator-confirm bypass record (where applicable). Panel outputs are themselves immutable authoring records per chapter 7. Per-agent transcripts are append-only; consensus panel-output records reference but never edit them. Records are replicated across storage. Full reconstructability of any catalog state at any past timestamp — audit reconstructs by reading the stored transcripts, never by re-invoking panels (Foundation Invariant V).

**(NF2) Reversibility per Foundation Invariant III.** No destructive writes. All changes append-only. Active artifacts immutable; supersession is the reversal mechanism. Non-active artifacts editable in place by operator.

**(NF3) Throughput.** Target: framework operates at sustainable rate for the target tenant population. Operator workload bounded; AI handles most volume. Throughput becomes a calibration concern, not an operator-load concern.

**(NF4) Latency (initial targets — to be calibrated with operating experience).** These are starting targets, not hard contracts. Actual targets will evolve as the framework operates and data accumulates.
- Context Authoring Panel: async-with-queue, target p50 ≤ 60s per intake entry.
- Context Publication Panel: per-member; target ≤ 60s for batch of 25; ≤ 5s for single member.
- Context Lifecycle Audit Panel: scheduled async; target ≤ 24h.
- Operator notification: real-time for high-stakes; target ≤ 5min for digest aggregation.
- Operator override action: synchronous; target ≤ 2s.
- Policy save validation: synchronous; target ≤ 1s.
- Consensus workbench-fingerprint comparison (all three agents resolved the same workbench fingerprint per chapter 7): synchronous; target ≤ 50ms.

**(NF5) Cost (initial targets — to be calibrated with operating experience).** Per-stage AI cost budget enforced. Per-member cost target ≤ $0.50 across full lifecycle (initial estimate). Cost dashboard with per-member, per-stage, per-month, per-policy breakdown. Sampling overhead included. Actual budgets will evolve as the framework operates.

**(NF6) Observability.** Every panel call, gate result, AI action, operator action, policy change, calibration event logged. Metrics: queue depths, panel verdicts, gate pass/fail rates, AI cost per member, per-policy execution rates, override rates, sample-review-age, calibration regression alerts, quarantine rates.

**(NF7) Calibration as first-class data — load-bearing.** Under AI-by-default, calibration is the operator's primary instrument for evaluating whether to trust the framework.

The framework MUST maintain:
- A calibration table that records, per member per stage: AI verdict, sample-routed-to-operator (yes/no), operator decision when sampled (confirm/override), eventual downstream signal (e.g. supersession of an AI-approved active version).
- Per-scope, per-stage precision computed continuously: of AI-approved members, what fraction were later overridden by operator? Of AI-rejected entries, what fraction were operator-overridden?
- Per-policy regression alerts: when override rate exceeds threshold week-over-week.
- Quarantine population trend: rising quarantine indicates panel-prompt drift or model regression.

Sampling rate is operator-tunable per policy. Higher sampling = more operator workload but more precise calibration. The minimum is greater than zero in all cases.

**(NF8) Engineering calibration: reproducibility for testing.** For CI / regression testing only, given the same workbench fingerprint (per chapter 7: same tool allowlist version + same evidence-source allowlist version + same registry snapshot id + same policy version + same operator-context hash) + same agent versions + same prompts, panel output reproducible within tolerance over the proposal. Per-agent transcripts will differ in tool-call sequence (each agent reasons independently); reproducibility is at the proposal + verdict layer, not at the transcript layer. Audit truth is preserved panel outputs from each run per Foundation Invariant V; audit MUST read stored transcripts and consensus records; MUST NOT re-invoke panels.

**(NF9) Backward compatibility per Foundation Invariant III.** An `active` version is immutable. Major version bumps create a new version that supersedes the prior; the prior remains addressable.

### Open questions
- NF3 throughput target (depends on target tenant population, framework-member volume).
- NF4 latency targets validation against real operating data.
- NF5 cost target validation.
- NF7 sampling rate minimum.
- NF7 calibration regression alert thresholds per scope.

---

## Chapter 11 — Negative requirements

### Purpose of this chapter
Enumerate what the framework must REFUSE. Bright lines.

### The take

The framework must refuse to:

1. **N1 — Fabricate.** AI cannot invent citations, enum values, provenance, or content not traceable to a seed row, bc-seed entry, or row provenance.
2. **N2 — Reference implicitly.** Every member cites provenance explicitly per Foundation Invariant IV.
3. **N3 — Disable operator override.** Operator MUST have a path to edit any non-active version, supersede any active version, pause any framework policy, and configure operator-confirm rules. The framework MUST NOT expose configurations that disable, suppress, or circumvent these mechanisms.
4. **N4 — Replay past evaluations.** Past panel outputs and per-agent transcripts are immutable per Foundation Invariant V; even re-running against the identical workbench fingerprint produces a new panel run record with new transcript uids, not a recreation of the prior one. Audit reads the stored transcripts; it never re-invokes panels to reconstruct historical verdicts.
5. **N5 — Approve without consensus.** Framework Approval requires three-model agreement, closed-enum verdict, no-fabrication check pass, sampling enrollment recorded, immutable authoring record emitted.
6. **N6 — Approve while operator-confirm rule applies.** If an operator-confirm rule matches the case, AI MUST route to operator-confirm UI rather than executing approval.
7. **N7 — Delete.** No hard delete per Foundation Invariant III. Supersession is the change mechanism for active artifacts.
8. **N8 — Mutate active artifacts in place.** Per Foundation Invariant III, active artifacts are immutable. Supersession occurs only when an operator approves activation of a successor version. AI may prepare or propose that successor version under policy; operator approval is the act that supersedes the prior active version.
9. **N9 — Mutate silently.** Every state change emits an authoring record.
10. **N10 — Change `definition_standard` in-place.** Switching standards is supersession (new version).
11. **N11 — Pollute platform grammar with tenant-scope content.** Tenant-scope governance lives at Contract Binding per Foundation Contract Grammar §Three-level governance; framework members themselves are tenant-agnostic. The framework does not author Contract Bindings.
12. **N12 — Publish without provenance.**
13. **N13 — Allow duplicate definitions across distinct members.**
14. **N14 — Skip the authoring-record trail.**
15. **N15 — Skip Foundation-compatibility validation.**
16. **N16 — Couple AI to the catalog API surface.** AI runs in a separate service.
17. **N17 — Allow operator override of Context Panel without recorded justification.**
18. **N18 — Issue framework members without a UID** per Foundation Invariant IV.
19. **N19 — Mix lifecycle and any orthogonal flag into one column.** Per Foundation Contract Grammar §Lifecycle, `governance.state` is the single lifecycle column.
20. **N20 — Emit Foundation Evidence Objects from framework writes.** Per Foundation §The Object Model, Evidence Objects are emitted only at evaluation boundaries. Framework writes emit authoring records.
21. **N21 — Conflate "admission" (runtime boundary) and "publication" (catalog lifecycle).**
22. **N22 — Extend Framework Approval authority outside the three framework scopes.** AI may propose for other catalog artifacts but cannot finalize. Foundation default applies (or sibling MCF applies for MC concerns).
23. **N23 — Auto-finalize active state without operator override path being active.** Every AI finalization requires the operator override mechanism to be available; if override is paused, broken, or unavailable for any reason, AI MUST route to OPERATOR_REVIEW instead.
24. **N24 — Discard invalid AI outputs silently.** Outputs failing no-fabrication check are quarantined, retained for calibration.
25. **N25 — Treat panel outputs as ephemeral.** Panel outputs are immutable authoring records. Audit reads stored records per Foundation Invariant V.
26. **N26 — Use the word "approve" for any AI action outside framework scope.** Within framework scope (the three scopes), AI's authority is named **Framework Approval** per the Authority principle. Outside framework scope, approval is operator authority and AI uses "recommend" / "propose" / "route" / "flag."
27. **N27 — Treat tenants as actors on the catalog Trust surface.** Tenants supply data; admission boundary acts on it. Tenants do not author or modify any framework member.
28. **N28 — Skip object ordering for intervention triggers.** ICs (out of framework scope) trigger from Metric Snapshots only per Foundation Invariant II.
29. **N29 — Mutate or restrict the operator's override rationale text.** Every override emits an authoring record with operator-supplied rationale text; the framework MUST preserve this text as authored, MUST NOT auto-edit or constrain it beyond minimal length validation.

### Open questions
- Whether N16 admits exceptions for trivial classifiers.
- Whether N18 extends to intake-queue entries.

---

## Chapter 12 — Scope 1: BF/BO contextual vocabulary

### Purpose of this chapter
Specify what AI handles for BF and BO end-to-end. AI is permitted to propose across all judgment dimensions; operator-confirm rules are the configurable mechanism for adding stricter gates on specific cases. There are no hard operator-only carveouts within scope.

### What AI handles

**For BF:**
- Definition quality assessment (specificity, non-boilerplate, non-rationale-style).
- Semantic family proposal from closed enum based on data type, definition, source-system context, and bc-seed lineage.
- Standard ref proposal from seed catalog and bc-seed — never fabricated.
- Unit type proposal where semantic family requires it.
- Object_class coherence (consistent with BF name and intended scope).
- Property coherence (consistent with object_class and definition).
- Duplicate detection against existing active BFs by normalized name/property and by semantic similarity.
- Alias verification: the alias to a source field is semantically defensible.
- BF→BO membership coherence: the BF's claimed BO membership is semantically consistent with the BO definition.
- **Necessity assessment:** AI may propose whether a new BF is needed (vs reuse of an existing BF). High-confidence reuse-recommendations execute; novel-BF cases with no close active match propose creation and route to operator-confirm if the operator-confirm policy applies.
- **Novel BARECOUNT-anchored content:** AI may propose definitions anchored to `definition_standard='BARECOUNT'` provided the proposal traces to row provenance (it's not invented from nothing). The operator-confirm policy SHOULD by default require operator confirm for novel BARECOUNT content, as it cannot be standard-verified.
- Full lifecycle progression: `intake → draft → review → approved → active`.

**For BO:**
- Definition quality assessment.
- Composition coherence (do these BFs naturally compose into this object?).
- Minimum composition gap detection (does this BO have required role coverage — identifier, dimension, temporal, measure?).
- BO duplicate detection against existing active BOs.
- BO/standard alignment.
- Standard ref proposal from seed catalog and bc-seed.
- **Necessity assessment:** AI may propose whether a new BO is needed (vs reuse of an existing BO or expansion of an existing BO's composition).
- Full lifecycle progression: `intake → draft → review → approved → active`.

### Configurable operator-confirm rules (per chapter 4)

The operator-confirm policy SHOULD be configured for at minimum these cases on first deployment:
- Novel BARECOUNT-anchored definitions (no external standard, no bc-seed lineage).
- New BO with composition < 4 BFs (signals likely-incomplete).
- New object_class never seen before in the catalog.
- New BF whose alias points to a source field that has never been observed in admitted data.

These are starting configurations; the operator may relax them over time as calibration data accumulates.

### Operator override mechanisms

- **Edit non-active BF/BO.** Operator can modify any attribute of a BF or BO in `draft`, `review`, or `approved` state. Edit emits an authoring record with operator rationale text.
- **Supersede active BF/BO.** Operator authors a new version of an active BF or BO. When the new version reaches `active`, the prior version moves to `superseded`. Existing references continue to address the superseded version per Foundation Invariant III.

### Per-scope calibration concerns

- Operator-override rate per object_class (high override rate may indicate the source schema or standard is poorly modeled).
- Duplicate-detection precision (false positives waste operator time; false negatives produce catalog drift).
- Standard ref proposal precision (wrong standard refs are a Foundation Invariant IV violation if they reference non-real documents).
- Alias verification precision.
- Novel-BF / novel-BO proposal precision (operator-override rate on these high-stakes cases).
- bc-seed lineage usage rate (higher is better — indicates AI is grounding proposals in verified seed content).

### Per-scope UI specialization

Extends generic detail view (chapter 6):
- Object-class browser showing all BFs grouped by object_class.
- BF→BO membership graph view.
- Alias diff viewer (compare BF semantics to source-field semantics).
- Standard ref candidate picker (operator can choose from AI's top-N proposals; bc-seed-lineage candidates marked).

### Open questions
- Specific minimum-composition rules per BO type (currently a single global ≥4 rule).
- Confidence threshold at which AI proposes novel content vs routes to operator-confirm.

---

## Chapter 13 — Scope 2: CF contextual naming

### Purpose of this chapter
Specify what AI handles for CF end-to-end.

### What AI handles

- Definition quality assessment.
- Anchoring to standards via seed catalog and bc-seed (never fabricated).
- Naming convention compliance.
- Duplicate detection across active CFs (semantic similarity and normalized name comparison).
- "Create new vs reuse existing" recommendation: when an intake entry could either be a new CF or map to an existing CF, AI proposes the reuse and routes to operator-confirm if uncertain.
- Standard ref proposal from seed catalog and bc-seed.
- **Necessity assessment:** AI may propose whether a new CF is needed (vs reusing an existing CF). High-confidence reuse-recommendations execute; novel-CF cases propose creation and route to operator-confirm if the operator-confirm policy applies.
- **Novel BARECOUNT-anchored definitions:** as with BF, AI may propose BARECOUNT-anchored CFs provided the proposal traces to row provenance. Operator-confirm policy SHOULD by default require operator confirm for these.
- Full lifecycle progression: `intake → draft → review → approved → active`.

### Configurable operator-confirm rules

- Novel BARECOUNT-anchored CF definitions.
- New CF in a functional domain that has no existing CFs (entirely new domain).
- New CF when an existing CF with high semantic similarity is found.

### Operator override mechanisms

Per chapter 5: edit non-active in place; supersede active via new version.

### Per-scope calibration concerns

- Operator-override rate on "create new vs reuse" recommendations.
- Naming-convention false negatives.
- Standard ref proposal precision.
- bc-seed lineage usage rate.

### Per-scope UI specialization

- CF browser organized by functional domain.
- Similarity-comparison view between a proposed CF and its closest active twins.
- Naming convention diff view.

### Open questions
- Similarity threshold at which AI auto-proposes reuse vs auto-proposes new CF.
- Naming convention specifics per functional domain.

---

## Chapter 14 — Scope 3: BF↔CF field-level mapping

### Purpose of this chapter
Specify what AI handles for the BF↔CF field-level mapping (Foundation's Canonical Mapping at the field-level resolution).

### What AI handles

- Mapping proposal: given a BF in scope of a CC, propose which CF (or new CF) the BF maps to based on semantic family, name similarity, unit compatibility, type compatibility, and bc-seed lineage.
- Mapping consistency check: if multiple BFs in scope of the same CC map to the same CF, flag for operator review (could be intentional reduction or could be a mapping defect).
- Reduction detection: when a CC's CF receives input from multiple BFs, propose the reduction operation (sum, first, last, max, etc.) based on semantic family and operator-defined conventions.
- Unit and type compatibility check at mapping time: BF unit + type must be compatible with CF unit + type; AI proposes unit conversion or type coercion if needed (but only from a closed list of governed conversions).
- Mapping authoring: AI authors mapping entries in a **draft CM version** for the relevant CC version. Publication creates a new active CM version (or activates the next CM version) — active CM versions are immutable per Foundation Invariant III. AI never mutates an active CM in place.
- **Final mapping proposal where business judgment is required:** AI may propose mappings even where multiple semantically-valid options exist; high-confidence cases execute; ambiguous cases route to operator-confirm.
- **Novel reduction operations:** the closed list of governed reductions remains canonical (operator must propose a new reduction type via ADR), but AI may propose using existing reductions in novel combinations.

### Configurable operator-confirm rules

- Reduction operation that combines BFs from different functional domains.
- Unit conversion that crosses unit type families.
- Mappings where the BF and CF semantic families differ.
- Mappings to a newly-created CF (one that has not yet reached `active`).

### Operator override mechanisms

- Edit a mapping in any non-active CM version.
- Supersede an active CM version with a new CM version that has the corrected mappings.

### Per-scope calibration concerns

- Mapping proposal precision per object_class.
- Reduction operation proposal precision.
- Unit/type compatibility false-positive rate.

### Per-scope UI specialization

- Mapping editor showing BF and CF side-by-side with semantic family, unit, type for each.
- Reduction operation picker with governed closed list.
- Cross-mapping consistency view (does this BF map consistently across CCs that include it?).
- Mapping impact view: which active MCs (in MCF scope) reference this CF and therefore depend on this mapping?

### Open questions
- Closed list of governed reduction operations.
- Closed list of governed unit conversions.
- Threshold for "different functional domains" that triggers operator-confirm.

---

## Chapter 15 — Cross-scope coherence

### Purpose of this chapter
Specify the cross-scope coherence checks the framework must enforce within BCF. Coherence is judged across two or more scopes. Cross-framework coherence (CF↔MC variable binding between BCF and MCF) is specified in MCF.

### Coherence checks within BCF

**BF↔BO membership coherence.**
- The BF claims membership in a specific BO. The BO's definition and composition should reflect this BF role.
- Check: does the BO's definition mention or accommodate the BF's concept? Does the BO's composition include role categories the BF fills?
- AI judges this at BF authoring (does the BF's claimed BO make sense?) and at BO authoring (does the BO accept this BF set?).

**BF↔CF coherence at the mapping.**
- A BF maps to a CF via the BF↔CF mapping. The mapped BF and CF must share semantic family, compatible unit, compatible type.
- Check: semantic_family identical or compatible via governed conversion; unit_type_code compatible; data_type compatible.
- AI judges this at mapping authoring (does this BF→CF mapping satisfy coherence?). Failure routes to operator review.

### Cross-framework coherence (BCF ↔ MCF)

**CF↔MC variable binding coherence** is a cross-framework concern jointly governed by BCF (CF side) and MCF (MC variable side). When MCF authors or approves an MC variable binding to a CF, the binding must satisfy variable-role coherence with the CF's semantic family, unit, and type. The coordination protocol is specified in MCF; from BCF's side, the CF must remain stable enough to support the MCF reference, and supersession of an active CF must trigger F7 (reference impact at supersession) with notification to MCF.

### Coherence failure handling

When AI detects coherence failure at write time:
- Pre-active member: route to OPERATOR_REVIEW with the specific coherence violation cited.
- Active member (detected at lifecycle audit): file ticket with proposed correction; operator decides whether to supersede or accept.

### Per-coherence operator-confirm rule examples

- Require operator confirm for any BF→CF mapping where semantic families differ.
- Require operator confirm for any BF↔BO membership where the BO would need composition expansion.

### UI for coherence

- Coherence check viewer per member: shows all coherence relations the member participates in with current pass/fail status.
- Coherence regression dashboard: detects coherence failures introduced by recent active-version supersessions.

### Open questions
- Closed list of governed conversions for semantic family compatibility.
- How tightly to enforce coherence vs allow operator-judgment overrides.

---

## Chapter 16 — Open questions and explicit deferrals

### Purpose of this chapter
The residue. Every open question from chapters 1-15, plus cross-cutting questions, plus explicit deferrals.

### Deferrals

**Deferral D1 — Disposition of legacy catalog content.**
The existing catalog contains members authored before BCF. Disposition: freeze legacy + apply BCF to new; remediate legacy in place using BCF; supersede unpublished and restart from active set. Decision is its own change record after these requirements converge.

**Deferral D2 — Foundation amendment proposals.**
Several questions are surfaced as candidates for Foundation amendment ADRs separate from these requirements: BF/CF collapse, BO necessity, AC/OC collapse, IC scope, AI Contract activation, minimum BO composition, direct CO → IC triggers.

**Deferral D3 — Vocabulary cleanup in existing implementation.**
Current implementation uses "admit"-family vocabulary for catalog work (conflating with Foundation runtime admission). Code may also use "approve" for AI/system actions where it should now be Framework Approval within BCF scope OR "recommend" outside framework scope. Inventory/gap pass concern.

**Deferral D4 — Context Authoring Panel REJECT defect-code closed list.**
Needs design + operator review before framework deployment.

**Deferral D5 — Foundation amendment proposal: direct CO → IC triggers.**
Per current Foundation Invariant II, IC triggers from Metric Snapshots only. The boolean-MC indirection forced by this rule is awkward for canonical conditions that are not naturally measures. Amendment proposal is operator's separate decision.

**Deferral D6 — BCF authority delegation ADR.**
The BCF as a whole, with Framework Approval authority for the three framework scopes, requires its own foundational ADR per Foundation §The Authority Model. This requirements document is the input to that ADR; the ADR itself is the governance act that establishes the framework and defines Framework Approval as a configured authoring mechanism.

**Deferral D7 — Sibling MCF requirements draft.**
The Metric Context Framework (MCF) handles all MC concerns and integrates with substantial existing services (mc-onboarding, formula-audit, metric-binding, chain-status, mc-integrity, metric-readiness, metric-knowledge, mc-envelope-governance, metric-wizard) and existing bc-ai agents (metric_verifier, chain_auditor, metric_tracer). MCF requirements are drafted in a separate document and follow the same iterative process. The boundary between BCF and MCF lives at the MC artifact. BCF requirements do not depend on MCF requirements being final; the two frameworks coordinate through CF↔MC binding (specified on MCF side per chapter 15).

### Cross-cutting open questions

Consolidated from chapters:

- Target tenant population the framework must serve.
- Calibration thresholds that trigger automatic framework pause per scope.
- Bounded-domain vocabulary for operator-authored or AI-proposed BARECOUNT content.
- Source-aliases-alone sufficiency for provenance.
- Multi-standard members — single ref or array.
- `correction_required` as Foundation lifecycle state or operational vocabulary.
- Semver bump rules per edit kind.
- Intake queue aging window.
- Detailed operator-confirm rule grammar.
- "Super-operator" role and authority.
- Bulk supersession authority model.
- UI home (single app / separate app / split per scope).
- Role model (operator / auditor / super-operator).
- Mobile/tablet surfaces.
- Notification UX.
- Closed list of REJECT-eligible defect codes.
- Closed list of APPROVE-eligible verdicts per stage.
- Minimum sampling rate per policy.
- Specific calibration regression thresholds per scope.
- F9 fast-track behavior during AI outage.
- Maker/Checker/Moderator triple right for all panels?
- Closed list of governed reduction operations (chapter 14).
- Closed list of governed unit conversions.
- Specific minimum-composition rules per BO type.
- Similarity threshold for "create new vs reuse" CF (chapter 13).
- Confidence threshold for AI-proposed novel content vs operator-confirm route.
- bc-seed integration protocol (push vs pull).
- NF4/NF5 target validation through operating experience.

### Process commitments

These are disciplines for working through the residue, not deferrals:

- Each open question gets its own ADR draft when ready to decide.
- The inventory pass (separate document) asks "what do we have that might inform this decision?" — does not pretend to settle any open question.
- The gap pass (separate document) lists what needs to be built/decided in dependency order; effort estimates may force re-scoping.
- The BCF ADR (D6) consumes this requirements document and the inventory/gap passes to formalize the authority delegation.
- The MCF requirements draft (D7) proceeds in its own session; coordination with BCF stays minimal (CF↔MC binding only) until MCF stabilizes.
