---
uid: metric-context-framework-requirements
title: Metric Context Framework (MCF) — Requirements
description: Requirements for the Metric Context Framework (MCF), the AI-assisted governance discipline for the contextual accuracy of the platform's metric meaning. Sibling of BCF (DEC-149ab2 / D411). Defines the post-D418 scope; the BCF/MCF boundary as stored-meaning vs computed-meaning; MCF identity (grain + formula intent hash + variable bindings + temporal gate + filters); the separation of metric intent (preserved KPI catalog) from metric binding (re-authored greenfield against BCF); formula AST as governed first-class artifact (executable + deterministic); formula normalization + identity hash + composite package signature hash; computed dimensions including fiscal-period derivation with resolver fixture config; the MCF Self-Verification Fixture mechanism (deterministic verifier, structural fixture shape derived from package signature, stale-fixture rule, panel-proposes-verifier-decides); the MCF lifecycle and immutability model; the MCF authority model inheriting Framework Approval from BCF; the MC publication eligibility contract (PE-MC-1 through PE-MC-10); tenant binding and readiness requirements (MLS overlay); runtime/evaluation boundary requirements; the migration-free greenfield re-authoring stance after the D418 closeout; the substrate tables MCF needs (described conceptually only, deferred to implementation DBCPs); operator console requirements including fixture authoring + verifier run surfaces; open questions and the full-implementation gate prerequisites. Status proposed.
status: proposed
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: requirements
---

# Metric Context Framework (MCF) — Requirements

> **What this is.** The full requirements document for the **Metric Context Framework (MCF)** — the sibling of the Business Context Framework (BCF, `business-context-framework-requirements.md`). MCF is the AI-assisted governance discipline for the platform's metric meaning. This document expands the prior **MCF Requirements Sketch** (`metric-context-framework-requirements-sketch.md`) into a full requirements specification.
>
> **Status**: `proposed`. This is a requirements document, not an ADR and not an implementation plan. It defines what MCF must be; it does not yet specify substrate tables, panel mechanics, publication endpoints, or UI implementation. Those are deferred to implementation DBCPs that this document **enables but does not contain**.
>
> **Working rule binding for this document and any session that opens it to extend it.** No BF (Business Field), BO (Business Object), CF (Canonical Field), or CM (`cc_field_mapping`) artifact may appear as evidence, candidate source, lineage, bridge, migration input, compatibility shim, design input, or inspiration. The legacy vocabulary primitives are not in quarantine — they are **physically gone** (D418 Gate 5 closeout, May 2026; ledger in §1.2). They appear in this document only as the negation that defines what MCF must replace. The carve-outs of ADR DEC-02f5a9 §5 — bc-seed, Source Contracts, Admission Contracts, Observation Contracts, source-reality evidence, and metric definition knowledge as intent — survive and are citable.

---

## 1. Scope and post-D418 grounding

### 1.1 Purpose

The Metric Context Framework (MCF) is the **AI-assisted governance discipline for the contextual accuracy of the platform's metric meaning**: what a metric *is*, what it measures, over what grain, against what context, using what formula, under what runtime conditions, evaluated against what data.

Where BCF governs the platform's business **vocabulary** (Entities, Characteristics, BusinessConcepts), MCF governs the platform's metric **computation context** — Metric Contracts (MC) and the surrounding metric artifacts (formula AST, variable bindings, grain declarations, temporal gates, thresholds, fiscal-calendar resolution, runtime-readiness gates). The two frameworks meet at the MC artifact: BCF supplies the BusinessConcepts and Entities the MC binds to; MCF authors the MC and everything that surrounds it.

### 1.2 Post-D418 grounding — the legacy substrate is gone

MCF is specified against a platform DB in which the legacy vocabulary stack **no longer exists**. The D418 retirement arc closed in May 2026 across 20 merged PRs:

| Gate | What was retired |
|---|---|
| D417 (DEC-6c57e2) | Quarantined the BF/BO/CF/CM tables (legacy vocabulary stack) |
| D418 (DEC-a19428) | Pre-production legacy active-runtime retirement |
| D419 (DEC-f48f99) | Historical FK sink classification (Path C: preserve audit context via denormalized snapshot columns) |
| Gate 1.1 / 1.2 (PRs #87 / #88) | Active-runtime archival |
| Gate 1.3.1 / 1.3.3 (PRs #89-#92, #94) | Static read cleanup + audit script |
| Gate 2 / 2.5 / 2.6 / 2.7 (bc-admin #11-#14; bc-core #93, #95) | UI surface + wizard retirement |
| Gate 5.0 (DBCP design) | Physical disposition design doc |
| Gate 5.1 (PR #96) | DDL target update + dry-run script |
| Gate 5.2 (PR #97) | Live DB DDL apply: 7 quarantined tables dropped + 3 dependent columns dropped + 2 historical FK constraints dropped + 6 Path C snapshot columns added + populated (4,135 + 401 audit rows preserved verbatim) |
| Gate 5.2-A (PR #99) | bc-core consumer cleanup preserving BCF greenfield |
| Gate 5.2-C (bc-admin PR #15) | bc-admin canonical-fields page retirement |
| Gate 5.3 (PR #100) | Disposed-state verification: 7/7 checks PASS |

The verified end state at the time of this document:

- `contract.business_field`, `contract.business_object`, `contract.business_field_alias`, `contract.business_object_field`, `contract.business_object_relation`, `contract.canonical_field`, `contract.cc_field_mapping` — **ABSENT**.
- `contract.canonical_contract.object_id`, `contract.observation_field_map.business_field_id`, `runtime.reader.business_object_id` — **columns dropped**.
- `operations.bo_enrichment_log`, `operations.bo_verification_log` — **preserved** with 4,135 + 401 audit rows verbatim and 3 Path C snapshot columns each (`object_name_snapshot`, `object_display_name_snapshot`, `object_function_code_snapshot`), no remaining FK to dropped `contract.business_object`.
- `metric.metric_definition`, `metric.metric_knowledge` — **preserved** as KPI catalog intent carve-out (DEC-02f5a9 §5).
- `concept_registry.entity`, `concept_registry.business_concept`, `concept_registry.characteristic` — **intact** as the successor BCF substrate.

MCF requirements therefore speak from the post-disposition world. The historically-quarantined-now-dropped surfaces appear in this document only where MCF must explicitly **not** reconstitute them.

### 1.3 Foundation grounding

Foundation `the-authority-model.md` establishes the three-level authority ladder (Foundation; ADRs and Errata; Descriptive). ADRs are the governed mechanism by which configured authoring paths are established. MCF is itself an ADR-governed mechanism: a foundational MCF ADR (the future sibling of DEC-149ab2 / D411) will declare the framework, name its authorized actors (Metric Authoring Panel, operators), specify the disciplines each actor must satisfy, and establish Framework Approval as the configured authority within the framework's scope.

Within this ADR-governed mechanism, AI consensus constitutes Framework Approval for in-scope members. Operator override is the explicit exception path. The framework is not a relaxation of Foundation; it is a configuration of the governed authoring mechanism that Foundation §The Authority Model permits.

MCF preserves all six Foundation invariants. The application of each to MCF is recorded in §10.3.

### 1.4 Source-of-authority documents

| Reference | Role |
|---|---|
| `the-invariants.md` | Six invariants — MCF preserves all six |
| `the-object-model.md` | Six object types — MCF authors grammar; never produces progression objects |
| `the-contract-grammar.md` | Twelve grammar artifacts incl. Metric Contract |
| `the-evaluation-boundaries.md` | Four boundaries incl. the metric evaluation boundary |
| `the-authority-model.md` | Three-level authority ladder |
| `business-context-framework-requirements.md` | Sibling BCF requirements — patterns MCF inherits |
| `metric-context-framework-requirements-sketch.md` | This document's prior sketch |
| ADR `DEC-02f5a9` | BCF Registry — governs the BCF/MCF boundary, §1 + §5 |
| ADR `DEC-149ab2` / D411 | BCF authority delegation — template for MCF authority |
| ADR `DEC-26b6e2` / D415 | Immutable Characteristic Atoms — pattern MCF may adopt for formula AST |
| ADR `DEC-65dc86` / D416 | BCF forward / BF-BO legacy compatibility — operational posture (now historical post-D418) |
| ADR `DEC-6c57e2` / D417 | Legacy Vocabulary Stack Quarantine |
| ADR `DEC-a19428` / D418 | Pre-production Legacy Active-Runtime Retirement |
| ADR `DEC-f48f99` / D419 | Historical FK Sink Classification |
| Gate 5.0 DBCP | `d418-gate-5-physical-disposition-dbcp-design.md` |
| D363 (DEC-1efa47) | Grain key-source mismatch — fiscal calendar groundwork |
| D364 (DEC-d7e7a0) | Fiscal calendar stack (`date_dim` + tenant config + `FiscalCalendarService`) |
| D365 (DEC-a8e8fc) | CC declares `posting_date_field`; canonical resolution enriches payload |
| DEC-bebaec | Chain Completeness SSOT (7-link definition) |
| D316 | Readiness scheduler (`mc_dependency` + `readiness_ledger`) |
| D366 (DEC-804874) | L-node semantic gate |
| D389 (DEC-c9e623) | Metric Lifecycle States (MLS) framework |
| D390 (DEC-9d7a5c) | MLS failure vocabulary |
| D391 (DEC-b8b825) | MLS-14 gate |
| D392 (DEC-e7b7b3) | MLS substrate |
| D393 (DEC-29f134) | Runtime drift detection |

### 1.5 Vocabulary discipline

- Foundation Contract Grammar lifecycle vocabulary throughout: `draft → review → approved → active → superseded`.
- "Admission" reserved for the runtime admission boundary per Foundation.
- "Approve" applies to AI within MCF's scope (Framework Approval); operator approval is the operator-driven exception path within the same governed authoring mechanism.
- "Authoring record" for catalog-side proof; "Evidence Object" reserved for Foundation runtime evidence.
- "Metric Snapshot" reserved for the boundary-produced authoritative object; never used for an MCF-side artifact.
- "Active MCF metric" means lifecycle_state `active` AND a `metric_transition` certification record AND PE-MC-1..PE-MC-9 satisfied (full definition in §10.7).
- The legacy vocabulary stack is referred to as "the historically-quarantined-now-dropped surfaces" or simply "the dropped surfaces". The historical names BF/BO/CF/CM appear only in negation contexts (e.g. "MCF does not bind to BF").

---

## 2. MCF purpose and non-goals

### 2.1 Three facts that produce the requirement

**First.** Foundation Invariant I applied to metrics has no governed surface today. Invariant I says *meaning is evaluated once, at the canonical evaluation boundary.* For business meaning this is satisfied by BCF + the canonical evaluation boundary. For *metric meaning* — the meaning produced at the metric evaluation boundary — the governing artifact is the Metric Contract, but the Metric Contract has no framework around it. Free-text formula authority, ad-hoc variable binding, drift-prone grain semantics, and uncodified runtime-readiness gates exist as scattered ADRs and helper scripts. Each is an implicit meaning authority unto itself.

**Second.** The legacy BF/BO/CF/CM substrate has been physically removed (per §1.2). The platform now has no semantic binding layer for metrics. Without MCF, every new metric chain repair would either (a) attempt to reconstitute the dropped surfaces (forbidden), or (b) accumulate again into scattered ADRs and helper scripts (the failure mode of the dropped substrate).

**Third.** Drifting metric-context work has no architectural home. Substantial existing ADRs name pieces of what MCF would own — fiscal calendar (D363/D364/D365), chain completeness SSOT (DEC-bebaec), readiness scheduler (D316), L-node semantic gate (D366), MLS framework (D389–D393), runtime drift detection (D393). Each is correct in its slice. None has a sibling-of-BCF framework to live in. The result is an accretion pattern eerily similar to what the legacy stack showed before BCF: many correct slices, no governed authority binding them. MCF gives those slices a home.

### 2.2 What MCF is

MCF is the **ADR-governed authoring mechanism** for metric-context artifacts. Under MCF, AI proposes, prepares, and approves metric-context content for in-scope members under **Framework Approval** (the same authority pattern BCF uses per ADR DEC-149ab2 / D411). Operator override is the exception, not the routine.

MCF is *upstream* of the metric evaluation boundary: it authors the governed grammar state — Metric Contracts and the artifacts that surround them — that the metric evaluation boundary reads at runtime.

### 2.3 Non-goals (what MCF is not)

- **Not a runtime component.** The metric evaluation boundary runs as Foundation defines.
- **Not an active participant at any evaluation boundary.** Foundation §The Evaluation Boundaries is unaffected.
- **Not a producer of authoritative runtime state.** MCF authors grammar state. Metric Snapshots, Evidence Objects, and Lineage Objects are produced only at the metric evaluation boundary.
- **Not a replacement for Foundation Contract Grammar.** The twelve grammar artifacts and their governance continue per The Contract Grammar.
- **Not in scope for BCF concerns.** Entity / Characteristic / BusinessConcept authoring is BCF's. MCF consumes BCF artifacts; it does not author them.
- **Not in scope for the four evaluation boundaries** (admission, canonical, metric, action) — these are Foundation.
- **Not in scope for Intervention Contracts.** Those govern the action boundary, downstream of metric. A separate framework or Foundation default applies.
- **Not a migration mechanism.** There is no migration from the historically-quarantined-now-dropped surfaces. Re-authoring is greenfield (see §16).
- **Not a substrate redesign of the metric evaluation engine.** Per DEC-02f5a9 §5: the KPI catalog intent survives; the bindings are re-authored. The engine itself is preserved.

The complete non-goals enumeration is consolidated in §21.

---

## 3. Boundary with BCF — stored meaning vs. computed meaning

The single most important architectural line in MCF is the one with BCF. It is named in ADR DEC-02f5a9 §1 and `business-concept-registry.md` §8. This section is the operational discipline that line resolves to.

### 3.1 The line: stored vs. computed

> **BCF governs observable concepts; MCF governs computed metrics.** The boundary is *who computes the value*: a value that arrives stored is a BCF Business Concept; a value the platform computes over grain, time, filter, and formula is an MCF metric.

This is the operational test. For any value the platform encounters:

| Test | If yes | If no |
|---|---|---|
| Does this value arrive in the platform pre-computed by an external system? | **BCF Business Concept.** Even if the source system derived it internally (e.g. `invoice.net_amount` already net of discounts at the source) | Continue test |
| Does the platform compute this value at the metric evaluation boundary, over grain, time, filter, and formula? | **MCF metric.** | Continue test |
| Is it a structural/identity property of an entity (an `entity.property` tuple expressible without computation)? | **BCF Business Concept.** | Continue test |
| Is it a runtime-only artifact (evidence, lineage, snapshot)? | Neither BCF nor MCF — Foundation runtime state. | Re-examine the test; the value may be miscategorized |

### 3.2 What MCF consumes from BCF (one-way)

MCF consumes BCF Registry artifacts by id, never by name:

- **Entity** (typed reference) — as the grain of a metric.
- **BusinessConcept** (typed reference) — as a metric variable binding (numerator, denominator, filter input, time anchor, reference pivot).
- **Characteristic** (typed reference, indirectly) — through the BusinessConcept the characteristic appears in.

MCF does **not** consume BCF Registry artifacts by name lookup, by free-text reference, or by partial match. All MCF→BCF references are by Registry id. This is Invariant IV applied to the MCF/BCF boundary.

### 3.3 What MCF does not author

MCF cannot author Entity, Characteristic, or BusinessConcept. If an MC requires a BusinessConcept that does not yet exist in the Registry, the authoring path is:

1. Operator (or the MCF authoring panel as an advisory step) routes the candidate to BCF for authoring through the BCF B6 panel.
2. The BCF authoring path runs greenfield (per ADR DEC-02f5a9 §4).
3. The resulting BusinessConcept becomes available in the Registry.
4. MCF authoring resumes against the now-available BC.

MCF cannot reach into BCF to create or modify Registry rows. The Registry's authoring surface is BCF-only.

### 3.4 What BCF does not author

BCF cannot author Metric Contracts, formulas, variable bindings, grain declarations, fiscal-calendar bindings, temporal gates, thresholds, or any MCF artifact. The metric chain is MCF-only.

### 3.5 The boundary lives at the MC artifact

> *"The boundary between BCF and MCF lives at the MC artifact: BCF governs no part of the MC. The cross-framework coordination on variable binding (where MCF references BusinessConcepts that BCF governs) is specified in MCF."* — adapted from BCF requirements §Scope.

This document is the coordination specification.

### 3.6 Computed values that look like stored values

Edge case worth naming explicitly:

**`fiscal_period`** — a tenant SAP source system stores `fiscal_period` directly on every line (e.g. SAP's `MONAT` field). Is this BCF or MCF?

**Answer: MCF.** The platform's authoritative `fiscal_period` is the value the platform's `FiscalCalendarService.resolve(posting_date)` computes from the tenant's governed fiscal calendar configuration (per D364). The source system's `MONAT` is *raw observation data*, admissible as a Source Object field, but the **authoritative platform fiscal_period** is a platform computation. Per the §3.1 test: "the platform computes this value at the metric evaluation boundary over grain, time, filter, and formula" — yes. **MCF.**

If a tenant's source system's `MONAT` disagrees with the platform's computed `fiscal_period`, the platform's computation is authoritative (Invariant I — meaning is evaluated at the canonical boundary, and the canonical boundary uses the platform's fiscal calendar resolution per D365). The source value is preserved as observation; it is not the authority.

### 3.7 Reference properties that look like metric inputs

Reverse edge case:

**`order_line.product`** — a reference property on `Order Line`. Looks like a metric input ("what product did this line sell"). Is it BCF or MCF?

**Answer: BCF.** It is a structural identity property of `Order Line` (per `business-concept-registry.md` §5 — reference properties are first-class BCF Business Concepts, addressable as `order_line.product`). MCF may *bind a variable* to `order_line.product` (e.g. "this metric is grouped by product"), but the property itself is BCF authoritative.

**Principle: structural identity is BCF's. Computation over structural identity is MCF's.**

### 3.8 Cross-framework coordination

Where BCF and MCF must coordinate:

- When BCF authors a new BusinessConcept, MCF may want to know (e.g. to suggest new MCs that could bind to it). This is a notification concern, not a write coupling.
- When BCF supersedes a BusinessConcept (under the immutable-atom model for Characteristics per ADR DEC-26b6e2; under the standard supersession path for concepts), MCF's MCs that bound to the superseded BC may need re-authoring. This is a cross-framework supersession concern.
- When MCF authors a new MC referencing a BusinessConcept, BCF may want to track the consumer (e.g. the BCF F5 read surface could surface "this BC is referenced by N MCs"). This is a read concern, not a write coupling.

**Hard rule: no cross-framework write coupling.** Neither framework writes into the other's owned substrate to mutate the other's state. Coordination flows via events or pull-side reads, not via cross-framework writes.

**This rule does not forbid shared *Foundation-governance* substrate.** Certification records, framework policy rows, and operator-confirm rule rows live in **Foundation Governance Substrate** tables (`contract.certification_record`, `contract.framework_policy`, `contract.operator_confirm_rule`). Both frameworks write rows scoped by `framework_code` or by their own `action_code` namespace. This is *parallel writes into a shared governance table*, not *cross-framework mutation*. The substrate provides cross-framework audit uniformity; neither framework's writes mutate the other's framework state. §17.3 specifies the ownership boundary in detail.

The exact event/coordination mechanics (event bus vs polling vs subscription) are deferred to implementation DBCPs (§17, §20; open questions in §19.8).

---

## 4. MCF identity model

### 4.1 Why identity must be structural

ADR DEC-02f5a9 §3 made BCF identity *structural, not detected*. Synonyms (many names, one meaning) are blocked by `UNIQUE(entity_id, property_id)`. Homonyms (one name, many meanings) are blocked by forced-distinct entity ids with distinct definitions. These are structural impossibilities, not gate-time detections.

The same discipline applies to MCF. Without it, MCF will re-create the contamination the legacy stack showed: two MCs that compute the same thing under different names (synonym contamination), one MC name that means two things to two operators (homonym contamination).

### 4.2 MC structural identity tuple

The active Metric Contract identity is the tuple:

```
MC identity = (
  grain_entity,           -- typed reference to a Registry Entity (DEC-02f5a9 §1)
  formula_intent_hash,    -- structural hash of the normalized formula AST (§8)
  variable_binding_set,   -- ordered/named set of (role, BusinessConcept) bindings
  temporal_gate_shape,    -- the temporal-evaluation shape from a closed enum (§4.4)
  filter_set              -- structural filter list, set-semantic (§4.5)
)
UNIQUE(grain_entity, formula_intent_hash, variable_binding_set, temporal_gate_shape, filter_set)
  WHERE lifecycle_state = 'active' AND archived_at IS NULL
```

The claim this constraint supports: two `active` MCs cannot have identical (grain, formula intent, variable bindings, temporal shape, filters) — i.e. they cannot mean the same thing. If an authoring attempt would produce a duplicate identity tuple, the substrate rejects the second insert.

This is a substrate-enforced uniqueness, not a panel-time advisory check.

### 4.3 What the identity constraint blocks

- **MC synonyms** — two MCs that compute the same value over the same grain with the same bindings and temporal shape, under different display names. Blocked by the UNIQUE constraint.
- **MC homonyms** — one display name covering two distinct identity tuples. Permitted at the display layer (operators may use the same display name for genuinely distinct metrics) but the *identity* surface forces the distinction to be explicit at authoring time.
- **Drift via free-text formula re-keying** — preventing two MCs from claiming distinct identity by giving them subtly different formula text that hashes to a different `formula_intent_hash`. The structural hash operates on normalized AST (§8), not on rendered text.

### 4.4 Temporal gate shape — closed enum

The `temporal_gate_shape` field is a closed enum. Initial values:

| Value | Semantics |
|---|---|
| `point_in_time` | Metric evaluated as of a single timestamp; no window |
| `trailing_window(N, unit)` | Metric evaluated over a trailing N-unit window (`unit ∈ {day, week, month, fiscal_period, fiscal_year}`) |
| `as_of(reference_kind)` | Metric evaluated as-of a reference (`reference_kind ∈ {posting_date, period_end, evaluation_at, custom_field}`) |
| `period_end(grain_period_type)` | Metric evaluated at the end of a `grain_period_type` (`grain_period_type ∈ {day, week, month, fiscal_period, fiscal_quarter, fiscal_year}`) |
| `cumulative_to_date(reference_kind)` | Metric accumulated from inception to a reference date (e.g. YTD; QTD; FYTD) |

The closed enum forecloses free-form temporal expressions; it makes temporal shape part of identity; it constrains what the metric evaluation engine must support.

Adding a new shape value is a Foundation Grammar change (ADR-governed). Adding a parameter to an existing shape (e.g. a new `unit` value for `trailing_window`) is an MCF Grammar change (open question in §19.2; working position: ADR-governed within MCF).

### 4.5 Filter set canonicalization

The `filter_set` is a set of structural filter clauses, each clause expressed against BCF BusinessConcepts. Filters are **set-semantic** for identity purposes: filter ordering does not participate in identity.

Each filter clause has the shape:
```
(business_concept_id, operator, value)
```
where `operator ∈ {=, !=, <, <=, >, >=, IN, NOT_IN, LIKE, IS_NULL, IS_NOT_NULL}` (closed enum) and `value` is a typed literal whose representation term must be compatible with the BC's representation term.

The canonicalization rule for identity: sort filter clauses by `(business_concept_id, operator, hash(value))`; concatenate; hash. Two `filter_set`s with the same clauses in different orders hash to the same identity tuple component.

### 4.6 What identity changes are supersession vs. revision

Analogue of BCF's identity-bearing vs. descriptive distinction:

| Change | Type | Mechanism |
|---|---|---|
| Change any field of the identity tuple (grain / formula intent / variable bindings / temporal gate shape / filter set) | **Supersession** | New MC under new identity tuple; old MC moves to `superseded`; `metric_supersession` row recorded |
| Add a descriptive attribute (display name, owner, narrative description, prose business intent, dashboard tagging) | **Revision** | Active MC body updated; descriptive fields only; identity tuple unchanged; recorded as a versioned revision row, not as supersession |
| Change a threshold value (target, alert level) | **Revision** | Threshold is descriptive metadata, not part of identity (per §4.7) |
| Change runtime-readiness intent (PE-MC-8 declaration; see §13) | **Revision** | Intent is a forward declaration, not part of identity |

The full rule per field is recorded in §10 (lifecycle).

### 4.7 What is NOT in the identity tuple

Explicit non-membership prevents accidental inclusion at substrate design time:

- **Display name** — descriptive, not identity. Operators may rename without supersession.
- **Definition prose / business intent** — descriptive.
- **Owner** — operational metadata.
- **Threshold values** — operational metadata; thresholds may shift without changing what the metric *is*.
- **Dashboard tags / categorization** — read-side metadata.
- **MC version code** — versioning is orthogonal to identity (a successor MC has a new identity tuple; revisions of a descriptive field bump the version code without changing identity).

### 4.8 Composite-grain edge case

A metric whose grain is a composite Entity (e.g. `Inventory Position` with identity `(Material, Warehouse, Batch)`) has a grain that is itself structurally complex. The MC's `grain_entity` reference is to the composite Entity by id, not to the constituent identity-bearing properties separately. The MC inherits the composite Entity's identity discipline through the reference.

If the composite Entity is later superseded (per BCF supersession discipline — changing its identity-bearing property set creates a new Entity), every MC whose `grain_entity` referenced the old composite must be re-authored against the new composite (or explicitly retained as a historical MC on the superseded Entity). This is a cross-framework supersession concern; mechanics deferred to implementation DBCP (open question in §19.8 Q19).

### 4.9 Identity model is structural, not detection

Restating for emphasis: the identity tuple is a **substrate-enforced UNIQUE constraint**, not a panel-time check. The substrate rejects duplicate inserts at write time. The panel can advise on identity collisions (`MC_DEFECT_IDENTITY_COLLISION`) but cannot decide; the substrate decides at the database boundary. Same discipline as BCF per ADR DEC-02f5a9 §3.

---

## 5. Metric intent vs. metric binding separation

This is the operational position the post-D418 world rests on.

### 5.1 The two halves of a Metric Contract

Per ADR DEC-02f5a9 §5: *"Metric definitions / knowledge (the KPI catalog) — Survive as knowledge — only the binding to concepts is rebuilt."*

A Metric Contract has two distinguishable halves:

| Half | Examples | Disposition |
|---|---|---|
| **Metric intent** (knowledge) | Display name, prose definition, business owner, threshold (target value), unit semantics (display unit), formula prose (what we want to compute, in English/math notation), source citation (e.g. "this is the standard DSO formula per industry practice"), references to operational SOPs, ownership domain | **Survives.** Per ADR §5 carve-out. The intent the KPI catalog accumulated (`metric.metric_definition`, `metric.metric_knowledge`) is preserved as knowledge. |
| **Metric binding** (substrate coupling) | Pre-D418: rows in `metric_binding`, `cc_field_mapping`, `runtime.reader.business_object_id`. **All physically gone post-D418.** | **No longer exists as data.** MCF authors metric binding fresh, against the BCF Registry, with no migration from the dropped substrate. |

### 5.2 What "survives as knowledge" operationally means

The KPI catalog's metric intent can be read by the MCF panel and by operators during MCF authoring **as background knowledge** — the same way an operator might consult an industry reference, an analyst report, or a working paper. Intent fields may **seed draft suggestions** in the authoring panel: a draft display name, a draft threshold default, a draft formula prose to help compose the AST. Every seeded suggestion is then re-authored under MCF discipline and independently grounded against a PE-MC-1 source.

What does NOT flow from the KPI catalog row:

- **Binding** — the MC's BCF variable bindings are authored fresh against the BCF Registry; no binding is inherited from the legacy substrate (which is gone anyway).
- **Authority** — the MC's PE-MC-1 grounding citation points at the authoritative source (recognized standard, bc-seed entry, operator-authored bounded-domain definition, source-system observation), never at the KPI catalog row. The KPI row is not auditable as evidence.
- **Identity** — the MC's identity tuple (§4.2) is constructed from the freshly-authored grain, formula AST, bindings, temporal gate, and filters; the KPI row does not contribute to identity.

The distinction:

- **Seed / background knowledge** — operator memory, KPI catalog prose, narrative context. May inform draft suggestions. Not auditable as evidence; not citable in the publication-eligibility check.
- **Authoritative evidence** — PE-MC-1 sources (recognized external standards, bc-seed catalog entries with provenance lineage, source-system observations with verifiable alias, operator-authored bounded-domain definitions with explicit business justification). Auditable, citable, gate-checked.

The KPI catalog may *seed* MCF drafts; the MC's authority chain never *includes* it.

Operationally: MCF substrate reads of `metric.metric_definition` and `metric.metric_knowledge` are permitted for authoring assistance. MCF substrate reads of the dropped surfaces are impossible (the tables don't exist) and would in any case be forbidden by the working rule.

### 5.3 What "the binding is rebuilt" operationally means

The MC's variable bindings under MCF point at BCF Business Concept ids by id. There is no path through `business_field_id`, no path through `cc_field_mapping`, no path through `canonical_field`. The legacy binding chain is structurally absent.

If an old metric existed under the legacy chain that bound to (say) an `unit_price_amount` BF, and the BCF Registry has a BusinessConcept `Sales Order Line · unit price (amount)` with id Y, MCF authoring does **not** migrate the binding to Y. MCF authors a new MC under the new identity discipline (§4), with bindings pointed at Y.

There is no `(old_mc_id, new_mc_id)` mapping table. There is no `(business_field_id, business_concept_id)` mapping table. The legacy binding identity layer was retired; reconstituting it in any form is a working-rule violation.

### 5.4 The KPI catalog ~1,819 KPIs as intent

The platform's KPI catalog contains ~1,819 metric intents across 18 functions (rows in `metric.metric_definition` / `metric.metric_knowledge`). Under MCF:

- The intent of each (display name, prose definition, owner, threshold) **survives** as background knowledge. MCF authoring sessions may consult it.
- The bindings of each are **absent** (substrate dropped). MCF re-authors each MC under the new identity discipline, against BCF Registry objects.
- The KPI catalog as a *list* is preserved — it tells us what we want to measure. The bindings the list once pointed at are not.

The work to re-author N MCs is **MCF execution scope**, sequenced over the lifetime of the MCF program. It is not a single-event migration. There is no migration timeline because there is no migration.

---

## 6. BCF variable-binding model

### 6.1 The binding act

A Metric Variable Binding is a structural reference from a position in an MC's formula AST to a BCF BusinessConcept (or, where the position requires it, a BCF Entity). The binding is:

- **By id, never by name** — Invariant IV.
- **Type-checked at bind time** — the variable's expected representation term / data type / unit must be compatible with the BusinessConcept's representation term / data type / unit. Incompatible binds are rejected at the substrate, not at runtime.
- **Role-explicit** — every binding carries a role label drawn from the MC's formula AST (e.g. `numerator`, `denominator`, `filter_input.region`, `time_anchor`). Two bindings to the same BusinessConcept under different roles are two distinct bindings.

### 6.2 Binding shapes

| Binding role | Expected target | Example |
|---|---|---|
| **Grain** | BCF Entity (typed reference) | `Sales Order Line` |
| **Variable (value)** | BCF BusinessConcept of kind `value` | `Sales Order Line · unit price (amount)` |
| **Variable (reference)** | BCF BusinessConcept of kind `reference` (used for joining / pivoting along an identity-reference edge) | `order_line.product` |
| **Filter input** | BCF BusinessConcept of either kind, with the filter condition specified | `Sales Order Line · region (text)` filtered to `'EMEA'` |
| **Time anchor** | A BCF BusinessConcept that carries a date or timestamp representation term (used as input to the fiscal calendar resolution per §9) | `Sales Order Line · posting date (date)` |

### 6.3 Bind-time compatibility checks (5 checks, substrate-enforced)

At bind time the substrate (or the authoring service that wraps the substrate) verifies:

1. **Existence** — the referenced BC id exists in the Registry and is `active` or (for `draft` MC) `draft`. Binding to `superseded` is rejected for `active` MCs; permitted only for historical MC versions (read-only).
2. **Kind compatibility** — a value-kind binding role targets a value-kind BC; a reference-kind role targets a reference-kind BC; a grain role targets an Entity (not a BC).
3. **Representation term compatibility** — the variable's expected representation term (declared in the formula AST) is identical to or compatible with the BC's representation term (per the BCF representation-term closed set).
4. **Unit compatibility** — for value-kind bindings, the variable's expected unit semantics (currency / count / duration / etc.) is identical to or convertible to the BC's unit semantics. Conversion rules live in OC/CC bodies (per ADR DEC-02f5a9 §2 "field-resolution logic survives"); MCF does not author conversion rules.
5. **Grain alignment** — the BC's home entity is reachable from the MC's grain entity via identity-bearing reference properties (per BCF identity-reference DAG, `business-concept-registry.md` §122-148). Bindings to BCs on entities unreachable from the grain are rejected. This is the structural shape of "the metric's grain must be coherent with its inputs."

Failure of any check rejects the binding at the substrate. The authoring panel may advise; the panel cannot bypass.

### 6.4 What MCF does not do in binding

MCF does **not**:

- Author resolution rules (type coercion, unit conversion, reduction-over-grain, temporal interpretation) — those live in OC/CC bodies per ADR DEC-02f5a9 §2.
- Author BCF artifacts — see §3.3.
- Read dropped substrate during binding — the dropped substrate doesn't exist; even if it did, the working rule forbids it.
- Permit free-text binding ("bind variable X to a field called `unit_price`") — bindings are by BCF id only.
- Maintain a name-resolution shim from legacy names to BCF ids — explicitly forbidden by the working rule + ADR DEC-02f5a9 §4 ("shim is the corruption preserved, not a fix").

### 6.5 Grain as typed Entity reference

Per ADR DEC-02f5a9 §1 and `business-concept-registry.md` §8:

> *"In MCF, grain therefore becomes a typed reference to a registry entity, not a free-text parameter — MCF cannot declare an incoherent grain."*

This is the load-bearing structural constraint that distinguishes MCF from the legacy metric chain. Legacy MCs declared grain as free text (e.g. `grain="invoice"`); the engine then tried to resolve "invoice" to a Business Object, sometimes succeeding, sometimes drifting. Under MCF, `grain_entity` is a Registry Entity id; resolution is unambiguous; "incoherent grain" is structurally impossible.

### 6.6 Binding lifecycle and binding-to-draft rules

- An MC whose `lifecycle_state` is `draft` may bind to BCs that are `draft` or `active`.
- An MC whose `lifecycle_state` is `review` may bind to BCs that are `approved` or `active`.
- An MC whose `lifecycle_state` is `approved` may bind only to BCs that are `active`.
- An MC whose `lifecycle_state` is `active` may bind only to BCs that are `active`.
- An MC whose `lifecycle_state` is `superseded` may carry historical bindings to `superseded` BCs (read-only; non-mutable).

Publication ordering: if an MC and a new BC both transit `draft → active` together (e.g. a new BC is required for a new MC), the BC must reach `active` before the MC may transition to `approved`. This is enforced by PE-MC-3 (binding completeness) and PE-MC-4 (type and unit coherence) at publication time (§13).

---

## 7. Formula AST requirements

### 7.1 Why an AST, not free text

Legacy metrics carried formulas as free-text strings (e.g. `"sum(NETPR) / count(distinct VBELN)"`). Free text is the failure mode the dropped substrate's `definition_standard` problem had: every consumer parses, interprets, and potentially mis-applies the text. Drift is silent. Inconsistency is undetectable.

Under MCF, the formula is a structured **abstract syntax tree** (AST):

- Authored as AST, not parsed from text.
- Validated against a closed set of operators.
- Type-checked against bound BCs at bind time.
- Identity-hashed for the MC identity tuple (§4.2; normalization rules in §8).

The AST is the authoritative representation. A rendered text form may exist for display (`"SUM(unit_price) / COUNT(line_number)"`) but the AST is the structural truth. Two MCs with identical ASTs but different rendered text are the same MC; two MCs with different ASTs but identical rendered text are different MCs.

### 7.2 AST node taxonomy (closed set, v1)

The v1 closed set of AST node types:

| Node | Role | Type signature |
|---|---|---|
| `variable_ref` | Reference to a bound MC variable (which points at a BCF BC) | Returns the BC's representation term + unit |
| `literal` | Constant value with explicit representation term and unit | Returns the literal's type |
| `aggregate` | `SUM`, `AVG`, `COUNT`, `COUNT_DISTINCT`, `MIN`, `MAX`, `MEDIAN`, `PERCENTILE(p)`. Operates over the set defined by grain + filters | Returns a value-kind aligned with the operand |
| `arithmetic` | `+`, `-`, `*`, `/`, `MOD`. Type-checked operands | Returns the dominant operand type (per type-promotion rules in §7.5) |
| `comparison` | `<`, `<=`, `=`, `>=`, `>`, `!=`. Returns boolean; usable in `case` or `filter` | Returns boolean |
| `case` | `CASE WHEN <comparison> THEN <expr> ELSE <expr> END`. Typed branches must agree | Returns the common type of the branches |
| `window` | `LAG`, `LEAD`, `MOVING_AVG(window)`. Window semantics specified by `temporal_gate_shape` | Returns the operand type |
| `time_anchor_resolution` | Resolves a BC bound to `time_anchor` role to a fiscal period / fiscal year via the fiscal calendar resolver (per D364, D365) | Returns `(fiscal_period, fiscal_year)` tuple |
| `bucket_assign` | Maps a numeric/date value to a closed-enum bucket label (e.g. DSO age buckets `0-30 / 30-60 / 60-90 / 90+`) | Returns text-kind bucket label |

Adding a node type to the taxonomy is an ADR-governed MCF Grammar change.

### 7.3 What the AST forbids

- **Arbitrary SQL** — no raw query embedding.
- **External function calls** — no `EXEC(...)` or external code invocation. The AST is closed.
- **Side effects** — no AST node may write state.
- **Free-text reference resolution** — no `"resolve('unit_price')"` operators; references are by BCF id only.
- **Implicit unit conversion** — type/unit must match at bind time, or the bind is rejected (per §6.3 check 4).
- **Aggregation outside grain** — every aggregate operates within the metric's grain; cross-grain aggregation is supersession to a new MC (`MC_DEFECT_CROSS_GRAIN_AGGREGATION`).
- **Recursion / self-reference** — an MC's formula cannot reference the MC itself (no `variable_ref` to the MC's own output).

### 7.4 Formula immutability

Per Foundation Invariant III applied to MCs: an active MC's formula AST is immutable. Changing the AST is supersession to a new MC (per §4.6). Whether MCF additionally adopts a publication-time semantic-finality affirmation analogous to ADR DEC-26b6e2 for Characteristics is an open question (§19.5 Q14). This document's working position is that the identity tuple already carries the immutability force, but a per-publication operator affirmation may be added as a high-risk gate (analogous to BCF's C5-HR) if formula authority is judged downstream-load-bearing for action contracts.

### 7.5 Type promotion rules

When `arithmetic` nodes combine operands of different types:

- `currency × number` → `currency` (unit preserved).
- `currency × currency` → forbidden (no currency-squared unit; raises `MC_DEFECT_UNIT_PROMOTION`).
- `count × number` → `count`.
- `duration × number` → `duration`.
- `date - date` → `duration`.
- `date + duration` → `date`.
- All other promotions: explicit literal conversion required, expressed as a `case` or as a wrapped `literal` node with declared target type/unit.

Implicit promotions beyond this list are forbidden; the AST type-check rejects.

### 7.6 Formula verification is executable and deterministic

The formula AST is **executable** under a closed, deterministic interpretation. Given a typed input rowset that matches the AST's declared variable signature, the formula evaluates to a typed output. Two consequences follow:

- **The formula is not "asserted correct" — it is verifiable.** A claim about what a formula computes is not authority; the execution of that formula against a fixture (§12) is. AI assertion that a formula is correct is not proof; the deterministic verifier's pass against a self-verification fixture bound to the formula's package hash is proof. This is the metric-side instance of the BCF discipline that AI consultative reasoning is not authority (`business-context-framework-requirements.md` §Chapter 7 after commit `1d7d209`).
- **The interpretation is closed.** Every node in the closed taxonomy (§7.2) has a single deterministic execution semantics. There are no "implementation-defined" results. Two evaluations of the same AST against the same input under the same resolver fixture config (§12.4 Section C) must produce identical output.

This subsection is forward-referenced by §12 (Self-Verification Fixtures) and PE-MC-10 (§13). Executability is a property of the AST itself; verification is the act of exercising it against a fixture.

---

## 8. Formula normalization and identity hash requirements

### 8.1 Why normalization

The `formula_intent_hash` in the MC identity tuple (§4.2) is a structural hash over the *normalized* AST. Without normalization, two semantically-identical formulas with cosmetic differences would hash differently — creating drift through accidental "new identity tuples" that actually share meaning.

### 8.2 Normalization rules

The normalizer applies, in order:

1. **Commutative operator ordering**. For commutative operators (`+`, `*`, `=`, `!=`, `IN`), operands are sorted by a stable structural sort key (per §8.3). `A + B` and `B + A` normalize to the same canonical form.
2. **Constant folding**. Literal-only sub-expressions are pre-computed at normalization time. `(2 + 3)` becomes `5` in the canonical AST.
3. **Variable-rename invariance**. Variable names within the AST are placeholders for the bound BCs; the canonical form uses the bound BC id, not the variable label. Renaming a variable from `numerator` to `top` without changing its BC binding preserves the hash.
4. **De Morgan canonicalization**. `NOT (A AND B)` normalizes to `(NOT A) OR (NOT B)` (consistent direction).
5. **CASE branch ordering**. Within a `case` node, branches with equivalent comparisons are sorted by the comparison's left-side BC id.
6. **Empty-filter elimination**. A `filter` clause whose value is a no-op (e.g. `field IS NOT NULL` when the field's BC kind already excludes nulls) is removed.
7. **Aggregate operand canonicalization**. Within an `aggregate` node, the operand sub-AST is recursively normalized before the aggregate's own normalization.

### 8.3 Structural sort key

The stable sort key for commutative-operand ordering is the deterministic serialization of the sub-AST:

```
sort_key(node) =
  case node.kind:
    'variable_ref' → 'v:' + bound_bc_id
    'literal'      → 'l:' + repr_term + ':' + value_serialized
    'aggregate'    → 'a:' + op + ':' + sort_key(operand)
    'arithmetic'   → 'r:' + op + ':' + sort_key(left) + ':' + sort_key(right_canonicalized)
    'comparison'   → 'c:' + op + ':' + sort_key(left) + ':' + sort_key(right)
    'case'         → 'k:' + canonical_branches
    'window'       → 'w:' + op + ':' + sort_key(operand) + ':' + window_spec
    'time_anchor_resolution' → 't:' + sort_key(time_anchor)
    'bucket_assign' → 'b:' + sort_key(operand) + ':' + bucket_spec_hash
```

The sort key is lexicographic-comparable; ordering operands by their sort keys produces a deterministic canonical form.

### 8.4 Identity hash construction

After normalization:

```
canonical_serialization(ast) = serialize(normalized_ast)
formula_intent_hash = sha256(canonical_serialization)
```

The hash is computed in the substrate (authoring service or DB trigger), not on the client. The hash construction algorithm is part of MCF specification and must be reproducibly versioned — the algorithm version is recorded with the hash so future algorithm changes are auditable (analogous to how content hashes carry an algorithm identifier).

### 8.5 What normalization does NOT do

- **Does not** evaluate the formula. The canonical AST is structural, not computed. Two formulas that compute the same value for all inputs (e.g. `2 * x` and `x + x`) hash differently because their AST structures differ. This is intentional: distinct authoring choices should be distinct identity, even if they compute equivalently.
- **Does not** infer commutativity for operators it doesn't know about. New operators added to the taxonomy must declare their commutativity in the AST node type registration.
- **Does not** apply algebraic simplification. `x * 1` and `x` are distinct identities.

### 8.6 Hash algorithm versioning

The hash algorithm version is recorded alongside the hash:

```
formula_identity = {
  algorithm_version: 'mcf-formula-hash-v1',
  hash: 'sha256:abc123...'
}
```

If the normalization rules change (e.g. v2 adds a new normalization step), the algorithm version increments. Existing MCs retain their `v1` hash; new MCs receive `v2` hashes. The substrate UNIQUE constraint includes the algorithm version, so cross-version collisions are impossible.

This is parallel to how container image manifests version their content-hashing algorithm.

### 8.7 Package signature hash (composite identity for verification)

The `formula_intent_hash` covers only the formula AST. A Metric Contract is more than its formula — it is the formula + variable bindings + grain entity + filter set + temporal gate + computed-dimension references. Self-verification fixtures (§12) bind to the *whole package*, not just to the formula. MCF therefore declares a composite **package signature hash** that combines the formula's structural identity with the other hashable axes:

```
package_signature_hash = sha256(
  formula_ast_hash + ':' +
  variable_binding_set_hash + ':' +
  grain_filter_temporal_dimension_signature_hash
)
```

Where:

- **`formula_ast_hash`** = the `formula_intent_hash` from §8.4 (covers the normalized AST).
- **`variable_binding_set_hash`** = sha256 of the canonical serialization of the ordered/named variable binding set (per §4.2 and §6); each binding contributes `(role_label, bound_entity_or_bc_id, bind_time_check_result_signature)`.
- **`grain_filter_temporal_dimension_signature_hash`** = sha256 over the canonical serialization of `(grain_entity_id, sorted_filter_clause_set, temporal_gate_spec, sorted_computed_dimension_ref_set)`.

The composite hash carries an algorithm version (e.g. `mcf-package-hash-v1`) parallel to §8.6's formula-hash versioning.

The package signature hash is the binding key for self-verification fixtures: a fixture is authored against a specific package signature hash and becomes stale (§12.7) the moment any contributing axis changes. The hash is computed in the substrate, not the client, so the binding cannot be forged by client-side construction.

The `formula_intent_hash` alone remains the identity-tuple component for MC identity (§4.2). The composite `package_signature_hash` is for verification binding only; it does not replace MC identity. Two MCs with identical formula AST but different filter sets are distinct MCs at the identity layer AND have distinct package signature hashes at the verification layer.

---

## 9. Computed dimensions and derived grain transforms

### 9.1 Why computed dimensions belong to MCF

A **computed dimension** is a value derived from observed values (or from grain coordinates) at the platform's canonical or metric evaluation boundary, not stored on the source. Examples:

- `fiscal_period` from `posting_date` × tenant fiscal calendar.
- `fiscal_year` from `posting_date` × tenant fiscal calendar.
- `calendar_quarter` from a date.
- `derived_grain` (e.g. "rolling 30-day window over Sales Order Line" — a derived grain from a base grain).
- `bucket_label` (e.g. "DSO bucket: 0-30, 30-60, 60-90, 90+" computed from a numeric value).

These are MCF concerns because:

- They are computed (per §3.1 test).
- They depend on governed configuration (the tenant fiscal calendar; the bucket boundaries) that has its own lifecycle.
- They are referenced by MC formulas (a metric grain `fiscal_period`; a metric filter `bucket_label = '0-30'`).

### 9.2 What MCF must specify for each computed-dimension class

For each computed-dimension class, MCF specification carries:

- **Source**: the BCF input(s) the computation reads (e.g. `fiscal_period` reads `Sales Order Line · posting date (date)` or whichever entity supplies a posting date).
- **Governing configuration**: the artifact that supplies the computation rules (e.g. `tenant.fiscal_calendar_config` per D364, owned by tenant onboarding).
- **Resolver service**: the runtime component that performs the computation (e.g. `FiscalCalendarService.resolve(posting_date)` per D364-D365).
- **Identity semantics**: how the computed dimension participates in MC identity (e.g. a `fiscal_period` filter on an MC is part of `filter_set` in the MC identity tuple).
- **Lifecycle interaction**: what happens to MCs that filter or grain on a computed dimension when the governing configuration is superseded (e.g. tenant changes fiscal calendar). Working position: MCs do not automatically re-evaluate; supersession of governing config triggers an audit of affected MCs and may require operator review.

The v1 closed set of computed dimensions:

| Dimension | Source BC kind | Governing config | Resolver |
|---|---|---|---|
| `fiscal_period` | date / timestamp | `tenant.fiscal_calendar_config` | `FiscalCalendarService.resolve()` |
| `fiscal_year` | date / timestamp | `tenant.fiscal_calendar_config` | `FiscalCalendarService.resolve()` |
| `fiscal_quarter` | date / timestamp | `tenant.fiscal_calendar_config` | `FiscalCalendarService.resolve()` |
| `calendar_quarter` | date / timestamp | none (Gregorian calendar) | platform date utility |
| `calendar_week_iso` | date / timestamp | none (ISO 8601) | platform date utility |
| `derived_grain(base_grain, window)` | base_grain (Entity) + window param | none (rule expressed in MC) | metric evaluation engine |
| `bucket_label(value, bucket_spec)` | numeric / date / duration BC | `bucket_spec` (closed enum or operator-defined within MC) | metric evaluation engine |

Adding a new computed dimension is an ADR-governed MCF Grammar change.

#### Resolver fixture config requirement

Every computed-dimension class that an MC references MUST be exercisable through a **deterministic resolver fixture config** at verification time (§12). The fixture config is a fixture-scoped substitute for the runtime governing configuration:

- For `fiscal_period` / `fiscal_year` / `fiscal_quarter`: a fixture-scoped fiscal calendar (e.g. period boundaries, start day) sufficient to deterministically resolve every date input the fixture supplies.
- For `bucket_label`: the fixture's chosen bucket spec.
- For `derived_grain`: the derivation params for the fixture run.
- For `calendar_*`: no fixture config needed (rules are platform-fixed and tenant-independent).

This requirement makes computed-dimension behavior reproducible without depending on live tenant config. It is a precondition for §12.6 (verifier behavior) — without resolver fixture config, a metric that filters on `fiscal_period` could not be verified deterministically because runtime fiscal calendar config is tenant-specific. The fixture config substitutes for the tenant config at verification time, exercising the resolver's logic in isolation.

A computed dimension that cannot be expressed as a resolver fixture config is a defect at the dimension's definition layer; the MC cannot pass PE-MC-10 (§13).

### 9.3 The fiscal calendar stack (existing work, MCF absorbs)

D363, D364, D365 are existing-ADR work on fiscal calendar that MCF absorbs as a sub-discipline:

- **D363 (DEC-1efa47)** identified the grain key-source mismatch (engine conflating business calendar period with engine runtime context). MCF's identity model (§4) and bind-time grain check (§6.3) make this class of mismatch structurally impossible.
- **D364 (DEC-d7e7a0)** locked the fiscal calendar stack: platform `date_dim` + per-entity tenant fiscal calendar config + optional `fiscal_period_boundary` + `FiscalCalendarService`. This stack is what MCF computed-dimension authoring consults for `fiscal_period` / `fiscal_year` derivation.
- **D365 (DEC-a8e8fc)** specified that CC declares `posting_date_field` and canonical resolution enriches payload. This is the *canonical-boundary* expression of fiscal resolution; MCF expresses the *metric-boundary* consumption (metric grain `fiscal_period`, metric filter `fiscal_year`, etc.).

MCF does not re-implement the fiscal calendar stack. MCF specifies how MCs consume it.

### 9.4 Derived grain transforms

A `derived_grain` is a metric grain that is computed from a base grain via a structural rule. Example: "rolling 30-day window over Sales Order Line" — base grain `Sales Order Line`; window rule `trailing_30_day`.

Derived grain identity composes:

```
derived_grain_identity = (
  base_grain_entity,        -- BCF Entity reference
  derivation_rule_code,     -- closed enum: rolling_window, period_aggregate, ...
  derivation_params         -- typed params; e.g. window length + unit
)
```

A derived grain enters the MC identity tuple's `grain_entity` slot as a typed reference, not as raw text. The substrate stores the derivation tuple; the metric evaluation engine resolves it at evaluation time.

The v1 set of derivation rules:

| Rule | Params |
|---|---|
| `rolling_window` | `length`, `unit` (e.g. 30, `day`) |
| `period_aggregate` | `period_type` (e.g. `fiscal_period`, `fiscal_quarter`) |
| `composite_join` | `target_entity_id` (e.g. lift `Order Line` to `Order` via the parent reference) |
| `filter_subset` | `filter_set` (e.g. "Sales Order Line where region = EMEA" as a derived grain) |

Adding a derivation rule is an ADR-governed MCF Grammar change.

### 9.5 The MLS framework (existing work, MCF absorbs)

D389-D393 (Metric Lifecycle States) is existing-ADR work on the 25-step activation ladder for metrics. MCF absorbs it as the **MC lifecycle / readiness sub-discipline** (see §14):

- **D389 (DEC-c9e623)**: MLS framework — 25 steps; platform MLS 1-14, tenant MLS 15-25; state ledger schema; probe-vs-gate separation; cross-boundary code rule.
- **D390 (DEC-9d7a5c)**: MLS failure vocabulary.
- **D391 (DEC-b8b825)**: MLS-14 gate.
- **D392 (DEC-e7b7b3)**: MLS substrate — `metric.mls_state` ledger + event log + trigger binding + queue recorder.
- **D393 (DEC-29f134)**: Runtime drift detection — admission probe + S3 quarantine + ticket service.

Under MCF, MLS becomes the **lifecycle-overlay** for the MC: platform MLS 1-14 governs MC authoring readiness (Framework Approval gates), tenant MLS 15-25 governs MC binding readiness for a specific tenant. The integration is specified in §14; the substrate is specified in §17.

---

## 10. MCF lifecycle and immutability model

### 10.1 Five states only

Per Foundation Contract Grammar §Lifecycle and as adopted by BCF:

```
draft → review → approved → active → superseded
```

MCF introduces no states beyond these five. The MLS framework (§9.5, §14) is a **readiness overlay** on top of the lifecycle — it tells you whether an `active` MC is runtime-ready in a tenant; it does not introduce new contract-grammar states.

**`intake` is pre-lifecycle, not a sixth state.** "Intake" describes a candidate MC artifact that has been proposed by the Metric Authoring Panel but has not yet been written to the MC substrate. An intake-state candidate has no `mcf.metric_contract` row, no identity tuple, no certification record. The first substrate write is the `intake → draft` transition (§10.2), which creates the MC row. Before that write, the candidate exists only as a panel proposal artifact.

### 10.2 AI-by-default lifecycle progression

For every MCF write:

| Transition | Default actor | Condition |
|---|---|---|
| `intake → draft` (first substrate write) | AI by default | Metric Authoring Panel returns `APPROVE_FOR_DRAFT` |
| `draft → review` | AI by default | MC envelope completeness check passes |
| `review → approved` | AI by default | Metric Publication Panel returns `APPROVE` AND PE-MC-1..PE-MC-9 deterministic publication gate pass |
| `approved → active` | **Operator confirm (always)** | `metric_transition` is the authority-bearing publication moment; operator-confirm with ≥40-char rationale per §11.4. Matches the BCF publication pattern (always-confirm for `registry_transition`). |
| `active → superseded` | **Operator only** | Explicit successor pointer required (per §10.5) |

Activation (`approved → active`) is the moment the MC becomes the read authority for the metric evaluation boundary. Per the BCF publication pattern, this moment requires explicit operator confirm — there is no low-risk variant. The "high-risk" framing in earlier drafts was a misnomer; activation is uniformly authority-bearing, and the only authority answer is operator confirm. §11.4 enumerates the additional MCF actions (supersession, binding change, etc.) that also require operator confirm.

### 10.3 Foundation invariants applied to MCF

| Invariant | Application to MCF |
|---|---|
| I. Meaning is evaluated once | Meaning is produced at the metric evaluation boundary, not in MCF. MCF authors the MC; the boundary evaluates. |
| II. Object ordering is fixed | MCF operates on grammar members (MC and surrounding artifacts), not on progression objects. |
| III. All state is immutable | Active MCs are immutable. AI cannot mutate an active MC. AI may propose a successor draft; operator approval is required to supersede the active version. |
| IV. All references are explicit | MC references to BusinessConcepts and Entities are by id, never by name. |
| V. Evaluation is non-replayable | AI panel outputs are immutable authoring records; audit reads them, never recomputes. |
| VI. Evidence is emitted, not inferred | Authoring records are emitted at every framework write. Catalog-side MCF authoring records are distinct from Foundation Evidence Objects, which are emitted only at evaluation boundaries. |

### 10.4 Immutable-active discipline

Active MCs are immutable. Operator override of an active MC = operator authors a superseding new MC (per §4.6 — supersession discipline rooted in the identity tuple).

There is no `UPDATE` on an active MC body that changes identity-tuple fields. The substrate enforces this via a `BEFORE UPDATE` trigger that rejects mutation of identity-bearing columns when the row's `lifecycle_state = 'active'` (the BCF analogue is the `business_concept` meaning-immutability trigger).

Descriptive-only updates (per §4.6) are permitted on active MCs as versioned revisions and recorded in an `mc_revision` ledger (substrate detail in §17).

### 10.5 Supersession with explicit successor pointer

`active → superseded` requires:

- The successor MC exists in `lifecycle_state = active` at the moment of supersession (no orphan supersession).
- An `mc_supersession` row is created with:
  - `predecessor_mc_id`
  - `successor_mc_id`
  - `correction_class` (editorial vs meaning-bearing — analogue of `characteristic_supersession` per DEC-26b6e2)
  - `operator_sub` (Cognito sub from authenticated JWT)
  - `rationale_text` (≥40-char floor for high-risk supersession)
  - `panel_run_uid` (the panel run that proposed the supersession, if AI-proposed)
  - `superseded_at` timestamp
- The predecessor's `lifecycle_state` flips to `superseded` atomically with the supersession-row insert.

The `mc_supersession` table is the safety net for the immutable-atom model. Substrate detail in §17.

### 10.6 Possible MCF analogue of ADR DEC-26b6e2 (Characteristic atoms)

ADR DEC-26b6e2 established that Characteristics are immutable atoms (no version; supersession-only correction; operator semantic-finality affirmation at publication).

**Open question**: which MCF sub-artifact, if any, needs the same atom-level immutability?

Candidates:

| Candidate | Strength |
|---|---|
| Formula AST | Strongest. The formula is the meaning-bearing core. "Editing the formula" is semantically equivalent to "minting a new metric." |
| Variable binding set | Strong. Re-binding a variable changes what the MC computes over. |
| Grain | Strong. Changing grain redefines the metric entirely. |
| Temporal gate shape | Moderate. Changes may sometimes be additive (extending a trailing window). |
| Filter set | Weakest. Filter additions are often legitimate refinements. |

**Working position**: the identity tuple (§4.2) already carries the immutability force — any change to grain / formula intent / variable bindings / temporal gate shape / filter set is supersession to a new MC. **Whether MCF additionally adopts a publication-time semantic-finality affirmation analogous to ADR DEC-26b6e2 is an open question for an implementation DBCP** (§19.5 Q14). The case for adoption is strongest when the MC is the source of an action (an Intervention Contract trigger) — at that point the metric's interpretation is downstream-load-bearing in a way analogous to a characteristic's term being immutable.

### 10.7 Definition of "active MCF metric"

An MC is *active* if and only if:

1. `lifecycle_state = 'active'` in the substrate.
2. `archived_at IS NULL`.
3. A `certification_record` row exists with `action_code = 'metric_transition'`, `from_state = 'approved'`, `to_state = 'active'`, linked to the MC's panel run.
4. PE-MC-1 through PE-MC-10 (§13) all evaluated to PASS at the certification time (recorded in the cert's `gate_results_json`).
5. The MC identity tuple satisfies the partial-unique substrate constraint (no duplicate active MC with the same tuple).

The lifecycle_state column is display only; the cert + PE-MC pass is the authority. This mirrors BCF UI-S5's "lifecycle state is display; cert is authority" rule.

### 10.8 Tenant-side lifecycle (binding-binding)

Distinct from MC lifecycle: the lifecycle of a tenant's binding to an active MC. An active MC may be runtime-ready for tenant A and not for tenant B. The MLS framework (§9.5) is the binding lifecycle: platform MLS 1-14 is "is this MC governed?" (= the MC is `active` per §10.7); tenant MLS 15-25 is "is this MC operational for this tenant?". §14 specifies the tenant-binding artifact.

---

## 11. MCF authority model / Framework Approval inheritance

### 11.0 Framing — broad reasoning, narrow authority

The Metric Authoring Panel is **not** a packet-in / verdict-out function. Metric authoring requires combinatorial reasoning across general knowledge, BCF Registry contents, evidence corpora, source-reality observations, and operator-supplied business intent. A panel limited to a precomputed input bundle would be brittle by construction — unable to compose answers that require discovering which BCF concept supplies a needed variable, or which external standard grounds a formula choice.

MCF therefore distinguishes two layers — the **thinking/proposal layer** (broad) and the **binding/authority layer** (narrow):

> **Reasoning can be broad.**
> **Authority must be narrow.**
> **Binding must be structural.**
> **Publication must be certified.**

The thinking layer is a **governed authoring workspace** — the panel has interactive access to a closed set of allowed tools (BCF Registry search, PE-MC-1 evidence retrieval, source-reality summaries, operator-provided business context, general model knowledge). The authority layer is the deterministic post-proposal pipeline (PE-MC checks; substrate constraints; cert-backed publication; operator confirm). The two layers are explicitly separated to keep the reasoning surface adequate for the work while keeping the publication surface incorruptible.

What this rules out:

- **The panel does not browse raw DB.** All substrate access is via allowed tools, not free SQL.
- **The panel cannot access the historically-quarantined-now-dropped surfaces** under any tool (they don't exist; even if they did, the working rule forbids).
- **The panel cannot fabricate citations.** Every PE-MC-1 grounding citation must trace back to a tool call that retrieved the cited source.
- **The panel cannot bind by name** — BCF binding is by id, mediated by the BCF search tool which returns id + canonical name + lifecycle state.
- **The panel cannot author outside the AST taxonomy** — the formula must compose from the closed node set in §7.2.

### 11.1 Mirror of BCF Framework Approval (D411)

MCF authority follows the BCF pattern established by ADR DEC-149ab2 / D411. Within MCF scope:

- **AI consensus constitutes Framework Approval.** AI proposes, prepares, and approves MCF members through the framework lifecycle under policy.
- **Operator override is the exception path.** Operator approval remains the sole authority for everything outside MCF scope.
- **Framework Approval requires, for every framework write**:
  1. Three-model consensus with closed-enum verdict on the **proposal** (not on the input — each model runs its own interactive tool transcript; consensus is per-proposal).
  2. **Same-workspace rule** — all three models work in the same governed authoring workspace: same allowed tool set, same evidence-source allowlist, same operator-provided context, same BCF Registry snapshot at workspace open. (This replaces the simpler same-input-snapshot rule inherited from BCF, which suits classification panels but not authoring panels with interactive tooling.)
  3. **No-fabrication grounding check pass** — every claim in the proposal traces to a tool call in that model's transcript that retrieved an allowed PE-MC-1 source.
  4. **Immutable authoring transcript** for each model (full tool-call trace + each tool's response + reasoning + verdict) + immutable consensus record. The transcript is the audit artifact per Invariant V; it replaces the single-bundle "input hash" of packet-style panels.
  5. Calibration sampling enrollment recorded.
  6. Active operator override mechanism (operator may override at any time).

### 11.2 Three immutable MCF rules

| Rule | Statement |
|---|---|
| **Rule 1 — Framework Approval discipline** | Every MCF write requires the six discipline conditions in §11.1. Any failure routes to operator review. |
| **Rule 2 — Operator override always available** | At every MCF lifecycle state, the operator may override the AI's decision (edit non-active versions; supersede active versions). The override path cannot be disabled, suppressed, or circumvented. |
| **Rule 3 — Non-bypassable authoring-record trail** | Every MCF act is preserved as an immutable authoring record. No MCF write may occur without a corresponding record. |

### 11.3 The Metric Authoring Panel — a governed workspace with bounded tools

Mirrors BCF's Context Panels architecture (per `business-context-framework-requirements.md` Chapter 7 §"Context Panels as governed tool workbenches"): a governed tool workbench, not a packet-in / verdict-out function. The two frameworks share the same workbench discipline (logged + input-hashed + output-hashed + transcript-included + scoped + dropped-surface-blocked tool calls; workbench fingerprint for consensus validity; per-agent immutable transcripts as audit artifacts). They differ in the **tool set composition** — BCF's tools serve vocabulary authoring (registry collision probes, alias probes, lifecycle history, bc-seed lookup); MCF's tools serve metric authoring (BCF search for variable candidates, AST validity probes, grain reachability checks, fiscal-calendar resolution, MLS readiness probes).

The panel is a **governed authoring workspace** for three models running in parallel. Each model has access to a closed set of allowed tools (the workspace boundary) and produces an immutable per-model transcript. Consensus is computed over the three proposals, not over a shared input.

#### 11.3.1 Thinking / proposal layer — what the panel may use

When proposing a candidate MC, each model may use:

- **General pretrained knowledge** of accounting, finance, operations, supply chain, manufacturing, and other domains relevant to the KPI being authored.
- **The KPI catalog row as prompt seed** — the operator's intent (display name, prose definition, threshold default, formula prose). Per §5.2: may seed draft suggestions; not citable as authority.
- **The BCF Registry**, accessed through the BCF search/read tools (§11.3.3). The panel discovers which Entities and BusinessConcepts exist that could supply the variables the proposed MC needs.
- **Allowed evidence corpora** — recognized external standards (GAAP, IFRS, XBRL, OAGIS, ISA-95, industry methodologies), bc-seed catalog entries, accessed through the evidence-retrieval tool.
- **Source-reality summaries** — descriptions of what source contracts the tenant has admitted and what observation contracts they emit, accessed through the source-reality tool. Used to inform realistic binding (an MC whose required BC has no admitted source for the target tenant will fail at PE-MC-8 / MLS).
- **Operator-provided business context** — free-text guidance the operator attaches when initiating the panel run ("this DSO must be weighted by customer segment for the Tier-1 client").

This is where the panel reasons: *"For DSO, the likely grain is Customer Invoice; numerator is outstanding receivable; denominator is average daily sales over a trailing window; fiscal calendar resolution matters."* The reasoning cannot be limited to a tiny precomputed bundle without producing mechanical garbage.

#### 11.3.2 Binding / authority layer — what constrains the output

Regardless of how broadly the panel reasons, every proposal must satisfy:

- **Formula must be a governed AST** per §7 (closed taxonomy of nodes; no free-text formula).
- **Variables must bind to active BCF BusinessConcept ids** per §6 (no name binding; no string lookup).
- **Grain must bind to a BCF Entity id** per §6.5.
- **Evidence citations must come from allowed sources** per PE-MC-1 (a–d).
- **The KPI catalog row cannot be cited as authority** — it may seed the proposal but not appear in the grounding chain.
- **The historically-quarantined-now-dropped surfaces (BF/BO/CF/CM) cannot be used** under any tool.
- **PE-MC-1..PE-MC-9 deterministic checks decide** whether the proposal can progress past the panel verdict.
- **Operator confirm is required at publication** (`approved → active`) per §10.2 / §11.4.

The panel's three closed-enum verdicts:

- **`APPROVE_FOR_DRAFT`** — the proposal satisfies the binding/authority layer; all three models agree; PE-MC-1..9 preliminary check passes; the MC progresses to `draft`.
- **`OPERATOR_REVIEW`** — the proposal has a defect that requires human judgment (uncertain grain, ambiguous BC choice between candidates, novel formula not clearly grounded). Routes to the operator console.
- **`REJECT_<defect_code>`** — the proposal violates a hard constraint (formula type mismatch, unbindable variable, identity collision, etc.). Recorded; not advanced.

#### 11.3.3 Allowed tool surfaces (closed set, v1)

The workspace exposes a closed set of tools. Each tool call is recorded in the model's transcript. Adding a tool to the set is an ADR-governed MCF change.

| Tool | Purpose | Example queries |
|---|---|---|
| `bcf.search_entity` | Find Registry Entities by name / family / domain | "Find entities related to Sales Order" |
| `bcf.search_business_concept` | Find BusinessConcepts on an Entity by kind / representation term / unit | "What value-kind BCs exist on Customer Invoice with currency unit?" |
| `bcf.read_entity` | Read a specific Entity by id (canonical name, identity-bearing properties, reachable entities via identity-references) | "What identity-bearing properties does `Sales Order Line` have? What entities are reachable from it?" |
| `bcf.read_business_concept` | Read a specific BC by id (kind, representation term, unit, home entity, lifecycle state) | "Is concept_id `f66642ad-...` an active value-kind BC?" |
| `bcf.reachability_check` | Verify the BCF identity-reference DAG path between a grain entity and a candidate BC's home entity | Used by the proposal step before declaring a variable binding |
| `evidence.search` | Search the allowed evidence corpora for a metric topic | "What does GAAP say about Days Sales Outstanding?" |
| `evidence.retrieve` | Retrieve a specific evidence document by URI from the allowlist | Retrieves the cited standard / bc-seed entry for grounding |
| `source_reality.summarize` | Summarize what source/admission/observation contracts a tenant has, and what fields are emitted | Informs whether a proposed binding is realistic for the tenant context |
| `kpi_catalog.read_intent` | Read the KPI catalog row's intent fields as background-knowledge seed | Returns display name, prose definition, threshold default, formula prose; explicitly tagged as **non-citable** in the response |
| `mc.identity_probe` | Check whether a candidate identity tuple would collide with an existing active MC | Used to surface `MC_DEFECT_IDENTITY_COLLISION` before proposal |

The tool surface explicitly **does not include**:

- Raw DB / SQL access.
- Any tool that touches the historically-quarantined-now-dropped surfaces (per working rule).
- Arbitrary internet retrieval (would violate no-fabrication grounding — citations must come from the evidence allowlist).
- Tools that write to BCF substrate (BCF authoring is BCF's; MCF reads only — per §3.3).
- Tools that bypass PE-MC checks.

#### 11.3.4 Closed-enum defect-code taxonomy

MC-specific defects that may be cited in `REJECT_<defect_code>` or `OPERATOR_REVIEW` verdicts:

- `MC_DEFECT_GRAIN_INCOHERENT` — grain entity does not exist or is not reachable from required bindings.
- `MC_DEFECT_VARIABLE_UNBINDABLE` — no BCF BC satisfies the variable's expected representation term / unit.
- `MC_DEFECT_FORMULA_TYPE_MISMATCH` — AST type-check failure.
- `MC_DEFECT_UNIT_PROMOTION` — implicit unit promotion attempted (per §7.5 forbidden).
- `MC_DEFECT_CROSS_GRAIN_AGGREGATION` — aggregate operates outside the metric's declared grain (per §7.3).
- `MC_DEFECT_IDENTITY_COLLISION` — proposed identity tuple would collide with an existing active MC.
- `MC_DEFECT_TEMPORAL_GATE_INCOHERENT` — temporal gate shape uses parameters not present in the binding set (e.g. trailing window with no time-anchor variable).
- `MC_DEFECT_COMPUTED_DIMENSION_UNRESOLVED` — computed dimension references a governing configuration that is absent or superseded.
- `MC_DEFECT_BC_SUPERSEDED` — proposed binding targets a `superseded` BC.
- `MC_DEFECT_PE_MC_1_UNGROUNDED` — proposed citation does not trace to an allowed evidence source.
- `MC_DEFECT_TRANSCRIPT_FABRICATION` — a claim in the proposal does not trace to a tool call in the transcript (no-fabrication grounding violation).

#### 11.3.5 Same discipline as BCF, transcript-shaped

Every panel run records:

- `panel_run_uid`, `prompt_version`, `policy_version`.
- Per model: `model_identity` (vendor + version + tier), `transcript_uid` (the immutable tool-call trace + reasoning + verdict), `verdict_code`, `defect_code` (if rejected).
- Workspace fingerprint: `workspace_fingerprint_hash` over (allowed tool set version + evidence-source allowlist version + BCF Registry snapshot id + operator-provided context hash).
- Consensus computation: how the three per-model verdicts combined into the panel-level outcome.
- Grounding-check result per claim in the consensus proposal.

All immutable per Invariant V — neither MCF nor the operator may amend a recorded transcript or verdict after the fact. The transcript IS the audit artifact; subsequent re-evaluation is forbidden per Invariant V.

#### 11.3.6 Implementation DBCP scope

The exact prompts, model selection (Gemini / Claude / GPT trio or specialization), tool set v1 schema, evidence-source allowlist composition, calibration sampling rate, workspace-fingerprint algorithm, and consensus computation rule are implementation DBCP scope (§19.6 Q15-Q16; §19.10 new questions Q32-Q34 below).

### 11.4 Operator-confirm MCF actions

Analogous to BCF's C5-HR (high-risk operator-confirm extension; ADR DEC-149ab2 §HR). The following MCF actions require operator confirm with ≥40-char rationale. All entries are **always-confirm** — there is no low-risk variant:

| Action | Rationale floor | Why always confirm |
|---|---|---|
| `metric_transition` (`approved → active`) | ≥40 chars | Authority-bearing publication moment. The MC becomes the read authority for the metric evaluation boundary. Matches BCF's `registry_transition` always-confirm. |
| `metric_supersede` (`active → superseded` with successor) | ≥40 chars | Retires an active read authority and points consumers at a successor. |
| `metric_binding_change` (re-bind a draft MC's variable across BCs of different home entities) | ≥40 chars | Changes the semantic meaning of the variable; pre-publication but consequence-bearing. |
| Cross-framework supersession ripple (BCF supersedes a BC; affected MCs require operator review) | ≥40 chars per affected MC | Cross-framework consequence; the affected MC's interpretation depends on a BC that is no longer the active authority. |
| Threshold change on an MC bound to an active Intervention Contract | ≥40 chars | Downstream action consequence; threshold movement triggers different IC firing behavior. |

The complete operator-confirm rule set (analogous to BCF's `operator_confirm_rule` table) is implementation DBCP scope.

**No "low-risk" lifecycle-progression action is AI-confirmed past `approved`.** AI executes the inner-lifecycle transitions (`intake → draft → review → approved`) under Framework Approval; the operator owns the final authority-bearing transition (`approved → active`) and every subsequent authority-bearing action.

### 11.5 Cert-backed authority

Mirror of BCF's `certification_record`-backed authority. Every governed MCF action emits a certification record. The lifecycle state of an MC is display only; the certification record is the authority.

The cert table is **Foundation Governance Substrate** per §17.3 — neither BCF nor MCF owns it. MCF writes cert rows scoped by MCF `action_code` values (`metric_create`, `metric_transition`, `metric_supersede`, `metric_revision_descriptive`, `metric_binding_change`, etc.); BCF writes cert rows scoped by its own `action_code` values. The shared table provides cross-framework audit uniformity without violating the §3.8 no-cross-framework-write-coupling rule (each framework writes its own rows; neither reads or mutates the other's).

If the column shape diverges enough between BCF and MCF needs (open question §19.10 Q26-Q27) that the shared shape becomes brittle, the operator may decide to split into `bcf.certification_record` and `mcf.certification_record` siblings.

### 11.6 What MCF inherits from BCF (consolidated)

The full inheritance ledger:

| Domain | Inheritance |
|---|---|
| Authority model | Framework Approval (DEC-149ab2 / D411); AI-by-default; operator override as exception; three immutable rules |
| Panel pattern | Governed tool workbench architecture; three-model consensus on the proposal; same-workbench rule (workbench fingerprint equality across agents); per-agent immutable interactive transcripts (tool calls + responses + reasoning + verdict); no-fabrication grounding (every claim traces to a tool call that retrieved an allowed source); calibration sampling; three-vendor model identity per panel run. MCF differs from BCF only in the tool-set composition (§11.3.3). |
| Lifecycle | Foundation five states; immutable-active; supersession-only correction; no new states beyond the five |
| Publication path | Two-phase request → operator confirm; high-risk lock for `metric_transition`; Fork-ii idempotent resume on duplicate cert; server-resolved evidence; cert-backed authority |
| Operator console UI | Single-session request → review → confirm; Step A evidence bundle re-render; Step B operator rationale with ≥40 char floor; Step C semantic-finality affirmation (if §10.6 adopted); Phase 1 skip on already-published; shared loading/error/empty primitives; a11y on publish flow; read-only verification journey before write gates |
| Cert-backed authority | Cert is the authority; lifecycle state is display only; operator-confirm block on cert; operator sub from JWT; rationale verbatim on cert |
| Substrate discipline | Partial-unique constraint on identity tuple; meaning-immutability `BEFORE UPDATE` trigger; active-version-required check; supersession table with predecessor→successor + correction_class + operator confirm |
| Evidence framework | Vocabulary Evidence Framework + Admission Checklist pattern (BCF `business-concept-registry-vocabulary-evidence-framework.md`) — adapted to metric authoring as Formula Evidence Framework + MC Admission Checklist |

### 11.7 What MCF does NOT inherit

- BCF's PE1-PE6 verbatim — MCF has its own PE-MC-1..PE-MC-10 (§13). The discipline is the same; the checks are MC-specific.
- BCF's three scopes (BF/BO, CF, BF↔CF) — these were BCF's own scopes; MCF's scope is the MC and its surrounding artifacts.
- ADR DEC-26b6e2 verbatim — whether MCF adopts a publication-time semantic-finality affirmation is an open question per §10.6.

---

## 12. MCF Self-Verification Fixtures

### 12.1 Purpose

A Metric Contract package is a structured artifact — a formula AST (§7), variable bindings to BCF (§6), grain entity (§4.3), filter set (§4.5), temporal gate (§4.4), and computed-dimension references (§9), with an expected output shape derived from all of the above. The PE-MC well-formedness checks (§13) verify that the package is *structurally* sound; they do not verify that the package *executes correctly* against any concrete input.

The **MCF Self-Verification Fixture** is the executable test that closes that gap. It is a structured set of (declared-input rowset → expected-output) pairs bound to an exact package signature hash (§8.7). A platform deterministic verifier executes the package against the fixture inputs and confirms outputs match. A passing fixture is package-internal proof that the formula, bindings, grain, filters, temporal gate, and computed-dimension resolution all behave as the author asserts.

The fixture's shape is **derived from the package signature, not invented**. If the package declares variables `v1`, `v2`, `v3` then the fixture must supply rowsets for `v1`, `v2`, `v3` — no more, no less, with declared type/unit/cardinality matching the bindings. The fixture is a structural contract over the package signature, not free-form test data.

### 12.2 Working principle: panel proposes, platform verifies

The Metric Authoring Panel may propose fixture rows using the governed MCF workbench (§11.3) — for example, by retrieving representative data shapes from `source_reality.summarize` or by drafting boundary cases against bc-seed lineage. Fixture proposal is a panel act, subject to the same governed-tool discipline as any other panel proposal: per-agent transcripts, workbench fingerprint, grounding citations, three-model consensus.

The platform's **deterministic verifier** executes the fixtures and produces a `pass | fail | structural_reject` result. AI assertion of fixture passage is not proof; only the deterministic verifier's result is proof. The fixture mechanism therefore enforces the BCF/MCF discipline that AI is consultative and the platform (executable AST + deterministic verifier) is the verdict authority for arithmetic correctness. This mirrors the BCF workbench framing (`business-context-framework-requirements.md` Chapter 7 after commit `1d7d209`) where the panel reasons inside a governed tool surface but the substrate is the authority on what gets written.

### 12.3 What a passing fixture proves — and does not prove

A passing self-verification fixture proves **package-internal metric semantics**:

- The formula AST executes against the declared input shape under the closed deterministic interpretation (§7.6).
- The variable bindings, grain, filters, temporal gate, and computed-dimension resolvers all participate as the author asserts.
- The output type, unit, and cardinality match the declared output shape.

A passing fixture does NOT prove:

- That any tenant has the source data the package needs.
- That any tenant's OCs / CCs / readers admit, canonicalize, or evaluate the package's inputs correctly.
- That tenant-binding gates (MLS 15-25 per §14) will pass.
- That the package's prose interpretation matches the formula's actual computation (that is PE-MC-9 (§13) definition-discipline territory, not fixture territory).

**Operational consequence for tenant onboarding failures.** Because a verified package proves package-internal semantics, an onboarding failure on a verified package should first route to **tenant data / source / binding / readiness investigation** (OC/CC/reader/admission/MLS layers per §15-§16), not to formula-correctness doubt. The fixture has already proven formula-correctness within the declared input shape; the failure is therefore almost certainly outside the formula layer. This reverses the legacy posture where formula text alone was the carrier of computation intent and every onboarding failure plausibly implicated the formula.

### 12.4 Fixture shape (three sections derived from the package signature)

The fixture body has three sections, each structurally derived from the package signature (§8.7):

**Section A — Declared inputs.** A typed rowset per declared variable binding. For each variable:

- `variable_name` — matches the package's variable binding label.
- `type` and `unit` — match the binding's resolved BC representation term + unit (§6.3 check 3).
- `cardinality` — `scalar`, `rowset_by_grain`, or `rowset_by_grain_and_dimension` per the package's expected shape.
- `rows` — typed values keyed by grain keys + grouping dimension keys + filter input values.
- `nullability` — explicit per variable (`nullable: true` if the package permits null at that variable; `nullable: false` otherwise).

**Section B — Declared expected output.** A typed value or rowset:

- `type` and `unit` — match the formula AST's resolved output type per §7.5.
- `cardinality` — `scalar` | `one_per_grain_instance` | `one_per_grain_dimension_tuple` per the formula's grain × dimension projection.
- `value(s)` — expected per the formula evaluated over Section A.
- `tolerance` — explicit numeric tolerance for floating-point comparisons (default policy in §12.6).
- `null_match_policy` — explicit (`exact` | `null_if_any_input_null` | `null_skipped`).

**Section C — Resolver fixture config.** Per §9.2, every computed-dimension class the package references requires a fixture-scoped resolver config:

- `fiscal_period` / `fiscal_year` / `fiscal_quarter` — a fixture-scoped fiscal calendar config (start day, period boundaries) sufficient for the fixture's date inputs.
- `bucket_label` — the bucket spec the fixture exercises.
- `derived_grain` — derivation params.
- `calendar_*` — no fixture config needed (platform-fixed).

Resolver fixture config is part of the fixture, not part of the package. A package may have multiple fixtures, each pinning a different resolver config to test sensitivity (e.g. a DSO metric exercised against a 4-4-5 fiscal calendar vs a calendar-month fiscal calendar).

### 12.5 Structural checks at fixture authoring (C-FX-1 .. C-FX-11)

Before any execution, the fixture authoring layer validates the fixture's shape against the package signature:

| Check | Rule |
|---|---|
| **C-FX-1 Variable presence** | Every declared variable in the package has a corresponding rowset in Section A. |
| **C-FX-2 No extra variables** | No Section A rowset has a name not declared in the package's binding set. |
| **C-FX-3 Type/unit/cardinality match** | Each variable's type, unit, and cardinality match the binding's resolved BC and the package's expected cardinality. |
| **C-FX-4 Rowset length alignment** | Where the package's formula requires aligned rowsets (e.g. paired `numerator` and `denominator` rowsets grouped by the same grain), the fixture's rowsets have aligned lengths or the verifier rejects. |
| **C-FX-5 Grain keys present** | Every row in every input rowset carries the grain entity's identity-bearing key(s). |
| **C-FX-6 Grouping dimensions present or computable** | Every grouping dimension the formula references is either present in the rowset or computable from a Section C resolver config. |
| **C-FX-7 Filter inputs present** | Every filter clause's referenced BC has a corresponding value in the input row. |
| **C-FX-8 Temporal anchor inputs present** | For temporal-gate shapes that require a time-anchor variable (§4.4), that variable is supplied in Section A. |
| **C-FX-9 Resolver fixture config present** | Every computed dimension the package references has a resolver fixture config in Section C (per §9.2 resolver fixture config requirement). |
| **C-FX-10 Expected output shape match** | Section B output type, unit, and cardinality match the package's declared output shape. |
| **C-FX-11 Nullability explicit** | Every variable and the output declare nullability explicitly; no implicit nullability. |

Failure of any C-FX check rejects the fixture at authoring time, before any execution. The reject is recorded as a `structural_reject` verification result (§12.6).

### 12.6 Verifier behavior

The platform deterministic verifier:

1. Reads the package by `package_signature_hash` (§8.7) — formula AST + bindings + grain + filters + temporal gate + computed-dimension refs.
2. Reads the fixture by `self_verification_fixture_hash`.
3. Confirms the fixture's bound `package_signature_hash` equals the package's current `package_signature_hash` (stale-fixture check; §12.7). If unequal, the verifier returns `structural_reject` with reason `stale_fixture`.
4. Re-validates the structural checks C-FX-1..C-FX-11.
5. Executes the package against Section A inputs, applying Section C resolver fixture configs.
6. Compares actual output to Section B expected output under the declared tolerance and null-match policy.
7. Produces a deterministic verdict `pass | fail | structural_reject` with per-row diff trace if `fail`.

The verifier is deterministic: given the same package hash + fixture hash + resolver fixture config, the verdict is invariant across runs and across executors. The verifier is the authority on fixture passage; AI assertion of passage is not authority.

The verifier emits an immutable verification result record (§17). Audit reads the record; never re-executes the verifier as a substitute for reading (Foundation Invariant V).

### 12.7 Fixture is bound to an exact package hash — stale-fixture rule

A fixture carries four hashes:

- `formula_ast_hash` — from §8.4.
- `variable_binding_set_hash` — from §8.7.
- `grain_filter_temporal_dimension_signature_hash` — from §8.7.
- `self_verification_fixture_hash` — sha256 over the canonical serialization of Sections A + B + C.

The fixture also persists the bound `package_signature_hash` (§8.7) at authoring time. The fixture vouches for the package whose `package_signature_hash` matches its bound hash.

If any of the following changes:

- The formula AST (changes `formula_ast_hash`).
- A variable binding — added, removed, or rebound (changes `variable_binding_set_hash`).
- The grain entity (changes the composite signature hash).
- A filter clause — added, removed, or modified (changes the composite signature hash).
- The temporal gate spec (changes the composite signature hash).
- A computed-dimension reference (changes the composite signature hash).

...then the `package_signature_hash` changes, the fixture's bound hash no longer matches, and the fixture becomes **stale**. A stale fixture cannot satisfy PE-MC-10 (§13). The package's author must:

1. Regenerate the fixture's structural shape from the new package signature (Section A variable list, Section B output shape, Section C resolver requirements may change).
2. Re-author or re-propose Section A/B/C values (panel proposal or operator authoring).
3. Re-execute the verifier and obtain a fresh `pass` result against the new `package_signature_hash`.

Stale fixtures are preserved (Foundation Invariant III); they cannot vouch for the post-change package but they remain addressable as historical artifacts. Past verification results are immutable per Invariant V.

### 12.8 Fixture coverage — multiple fixtures per package

A package may have multiple fixtures, each exercising a different aspect:

- A **null-handling fixture** exercising the null path of each nullable variable.
- A **boundary fixture** exercising minimum / maximum / zero / negative values.
- A **resolver-sensitivity fixture** exercising different computed-dimension resolver configurations against the same package.
- A **grain-coverage fixture** exercising single-row vs multi-row grain instances.
- A **filter-coverage fixture** exercising rows that pass and rows that fail each filter clause.

The minimum coverage discipline per formula class (e.g. ratio metrics require both a non-zero-denominator and a zero-denominator fixture; window metrics require both fully-populated-window and partial-window fixtures) is an open question (§19.13 Q37).

For PE-MC-10 (§13), at least one fixture per package must pass; the minimum-coverage rule above is a strengthening for specific formula classes and ships with the implementation DBCP (§20).

### 12.9 Fixture immutability and supersession

Per Invariant III applied to fixtures:

- A fixture that has vouched for an `active` package version is immutable in its bound-hash columns. The fixture's `pass` result against the matching `package_signature_hash` is historical truth.
- Fixture supersession follows the MC supersession pattern (§10.5 for MC supersession; §12.9 for fixture immutability and supersession): a new fixture is authored against the new `package_signature_hash`; the predecessor remains addressable but does not vouch for the new package.
- Fixture revision (editing tolerance, null-match policy, or Section A/B values without changing `package_signature_hash`) is permitted only before the fixture has produced a `pass` result that has been cited by a PE-MC-10 evaluation. Once cited, the fixture is immutable; further changes are supersession to a new fixture.

### 12.10 Downstream onboarding benefit — triage default-route reversal

A verified package — formula AST + bindings + grain + filters + temporal gate + computed-dimension refs — with at least one passing self-verification fixture is **internally proven**. When a tenant binding subsequently fails (MLS 15-25 per §14; runtime drift per §10.5; readiness scheduler per D316), the operator's default-route triage is:

1. **First: tenant data shape** — do the admitted source rows match the OC's admission contract?
2. **Second: source contract gaps** — do the SC/AC/OC emit the BCs the package's variable bindings expect?
3. **Third: canonical contract gaps** — does the CC supply the canonical fields the package's bindings target?
4. **Fourth: reader-flavor mismatch** — does the active reader flavor support the package's grain entity?
5. **Fifth: MLS readiness gates** — D389-D393 per §10.5.

**Formula doubt is the last resort**, not the first. This reverses the legacy posture where formula text alone was the carrier of computation intent and every onboarding failure plausibly implicated the formula. The fixture has already pinned formula correctness to a deterministic hash; an onboarding failure on a verified package is, by elimination, almost certainly outside the formula layer.

The fixture is therefore both a **publication gate** (PE-MC-10) and an **onboarding-triage artifact** that bounds the search space when things go wrong in production.

---

## 13. MCF publication eligibility contract (PE-MC-1 through PE-MC-10)

Analogue of BCF's PE1-PE6 publication eligibility, adapted for metric semantics. A Metric Contract is eligible for publication to `active` if and only if it satisfies all nine PE-MC checks plus the cross-cutting no-fabrication and inconsistency-intolerance rules.

### PE-MC-1. Provenance (no-fabrication)

Every claim in the MC traces to a recognized evidence source:

- (a) a **recognized external standard** with verifiable citation (e.g. GAAP, IFRS, XBRL, an industry methodology like Toyota's lean operations, an academic source);
- (b) a **bc-seed catalog entry** with verified provenance lineage (e.g. a bc-seed metric entry like `metric.dso` with documented origin);
- (c) an **operator-authored bounded-domain definition** with explicit business justification (e.g. a BareCount-internal metric where the operator declares "this is our methodology and the justification is X");
- (d) a **source-system observation** with verifiable alias — **provisional**, subject to operator-confirm until the sufficiency question is settled (mirrors BCF's PE1 open question).

**Explicitly NOT a PE-MC-1 source**:
- The historically-quarantined-now-dropped surfaces (BF / BO / CF / CM rows). These do not exist as data and are forbidden as evidence by the working rule.
- The KPI catalog (`metric.metric_definition`, `metric.metric_knowledge`) **as intent** — background knowledge per §5.2, **not citable as PE-MC-1 evidence**.

### PE-MC-2. Grain coherence

The MC's `grain_entity` resolves to a Registry Entity. Every variable binding's target BC is reachable from the grain entity via identity-bearing reference properties (per §6.3 check 5). Grain incoherence is blocked at PE-MC-2.

### PE-MC-3. Binding completeness

Every variable position in the formula AST is bound to a BCF BusinessConcept (or, for the grain position, a BCF Entity). Unbound variables fail PE-MC-3.

### PE-MC-4. Type and unit coherence

Every binding passes the §6.3 bind-time compatibility checks (existence, kind, representation term, unit, grain alignment). Failures fail PE-MC-4.

### PE-MC-5. Formula AST validity

The formula AST contains only nodes from the closed taxonomy (§7.2). No free text. No external function calls. No side effects. Type checking succeeds across the AST. Failures fail PE-MC-5.

### PE-MC-6. Temporal gate well-formedness

The `temporal_gate_shape` is from the closed enum (§4.4). For shapes that require a time-anchor variable, the binding exists and resolves through the fiscal calendar (§9.3). For shapes that require a window, the window parameter is present and valid.

### PE-MC-7. Computed-dimension coherence

For each filter or grain that uses a computed dimension (e.g. `fiscal_period`), the governing configuration is named (e.g. `tenant.fiscal_calendar_config`) and exists in active state at the metric's intended evaluation context. Cross-tenant compatibility (whether an MC that filters on `fiscal_period` can serve tenants with different fiscal calendars) is an open question (§19.7 Q23).

### PE-MC-8. Runtime-readiness intent

The MC declares its intended runtime-readiness profile — a forward declaration for the MLS framework to act on per §9.5: what data the MC expects to be available, what gates it expects to pass for a tenant binding. This is intent at publication time, not yet a runtime check.

Working position: PE-MC-8 is **publication-deferred** — an MC may reach `active` based on its own form; tenant bindings handle runtime-readiness separately via MLS 15-25. The alternative (PE-MC-8 publication-blocking) is open question §19.7 Q24.

### PE-MC-9. Definition discipline

The MC's prose definition declares what the metric IS, not why it matters. Business intent is in a separate field. Definitions are unique per MC identity (no two MCs may have identical prose definitions for distinct identity tuples).

### PE-MC-10. Self-verification fixture passes

At least one Self-Verification Fixture (§12) authored against the MC's current `package_signature_hash` (§8.7) has produced a deterministic `pass` verdict from the platform verifier (§12.6). The passing verification result record is cited by the publication eligibility evaluation.

The fixture's bound `package_signature_hash` MUST equal the MC's current `package_signature_hash` at PE-MC-10 evaluation time. A stale fixture (§12.7) cannot satisfy PE-MC-10. Implementation-DBCP-deferred: minimum-coverage rules per formula class (§12.8 / §19.13 Q37) may strengthen PE-MC-10 to require N fixtures rather than at least one for specific formula classes.

PE-MC-10 is the proof check that distinguishes a *well-formed* package (PE-MC-1..PE-MC-9 pass) from a *verified* package (well-formed + deterministically exercised). It is not folded into PE-MC-5 (formula AST validity) because PE-MC-5 is structural — it confirms the AST conforms to the closed taxonomy and type-checks — whereas PE-MC-10 is executable — it confirms the AST + the whole package actually computes what the author asserts. Neither check subsumes the other.

Failure routes to OPERATOR_REVIEW with the verifier's diff trace attached. The operator may either revise the package (which invalidates the fixture; supersession path) or revise the fixture (within the immutability bounds of §12.9) and re-verify.

### Cross-cutting: No-fabrication rule

AI cannot invent citations, formulas, variable bindings, or content not traceable to a PE-MC-1 source. Outputs failing the no-fabrication check are quarantined as invalid panel runs, preserved for calibration.

### Cross-cutting: Inconsistency intolerance

Validated on every write. Examples of intolerable states:

- `temporal_gate_shape = 'trailing_window(30, day)'` + no `time_anchor` binding.
- Variable binding to a `superseded` BC on an `active` MC (without explicit historical-MC carve-out per §6.6).
- Formula AST contains an `aggregate` node whose grain disagrees with the MC's `grain_entity`.
- Two `active` MCs with identical identity tuples (blocked at the substrate per §4.2, but PE-MC ensures the panel doesn't try).
- A computed-dimension reference whose governing configuration is `superseded` or absent.

### PE-MC summary table

| Check | Subject | Pass condition | Failure routes to |
|---|---|---|---|
| PE-MC-1 | Provenance | Every claim cites an authorized source (a–d) | OPERATOR_REVIEW |
| PE-MC-2 | Grain coherence | Grain Entity exists; all BC bindings reachable | OPERATOR_REVIEW |
| PE-MC-3 | Binding completeness | All variable positions bound | OPERATOR_REVIEW |
| PE-MC-4 | Type/unit coherence | All 5 bind-time checks pass | REJECT |
| PE-MC-5 | Formula AST validity | Closed taxonomy; type-checks | REJECT |
| PE-MC-6 | Temporal gate well-formedness | Closed enum shape; required params present | OPERATOR_REVIEW |
| PE-MC-7 | Computed-dimension coherence | Governing config active | OPERATOR_REVIEW |
| PE-MC-8 | Runtime-readiness intent | Forward declaration well-formed (publication-deferred) | OPERATOR_REVIEW |
| PE-MC-9 | Definition discipline | Prose distinct from intent; uniqueness per identity tuple | OPERATOR_REVIEW |
| PE-MC-10 | Self-verification fixture pass | ≥1 non-stale fixture with deterministic `pass` against current `package_signature_hash` | OPERATOR_REVIEW (with verifier diff trace) |

---

## 14. Tenant binding and readiness requirements

### 14.1 Tenant binding is distinct from MC lifecycle

The MC lifecycle (§10) is the platform-side governance of what the metric IS. Tenant binding is the per-tenant governance of whether the metric IS OPERATIONAL for a given tenant. The two lifecycles are coupled but distinct.

An `active` MC may be:

- **Bound and operational** for tenant A (the tenant has the source data, the source contract is admitting, the canonical resolution is producing, the metric evaluation engine can compute).
- **Bound but not operational** for tenant B (the tenant has the source data but the canonical chain is incomplete).
- **Not bound** for tenant C (the tenant has not registered interest in this MC).

### 14.2 MLS as the binding lifecycle

The MLS framework (D389-D393) is the binding lifecycle:

- **MLS 1-14 (platform)**: governs MC authoring readiness. This corresponds to MCF's lifecycle progression toward `active` (§10) and the PE-MC publication gate (§13). An MC at MLS 14 is published — `active` with cert.
- **MLS 15-25 (tenant)**: governs MC binding readiness for a specific tenant. An MC at tenant MLS 25 is fully operational for that tenant.

Under MCF, MLS 1-14 are first-class MCF lifecycle concerns; MLS 15-25 are tenant-binding lifecycle concerns. The MLS state ledger (`metric.mls_state`, per D392) records the per-MC and per-(MC, tenant) state.

### 14.3 The tenant binding artifact

A tenant binding is a substrate row that connects an `active` MC to a tenant context. The binding records:

- `tenant_id`
- `metric_contract_id`
- `binding_state` (one of the MLS 15-25 states)
- `bound_at` timestamp
- `bound_by` (operator sub OR `framework_approval` sentinel for AI-bound)
- Required-data manifest (which source contracts the binding depends on)
- Drift posture (per D393 runtime drift detection — what the binding expects)

The substrate detail is implementation DBCP scope (§17).

### 14.4 Binding readiness checks

For a tenant binding to advance through MLS 15-25, the following must hold:

| Stage | Requirement |
|---|---|
| MLS 15 | The MC's required source contracts are bound to the tenant |
| MLS 16-18 | The tenant's source contracts admit the required fields |
| MLS 19-21 | The canonical resolution produces the required BC values |
| MLS 22-23 | The metric evaluation engine produces snapshots without runtime drift |
| MLS 24 | First successful snapshot recorded |
| MLS 25 | Steady-state operational (snapshot cadence per the MC's temporal gate) |

The per-stage requirements are owned by D389-D393. MCF specifies that the binding lifecycle integrates with MCF substrate via the binding artifact (§14.3) and via runtime-readiness intent at publication (PE-MC-8, §13).

### 14.5 Drift detection at tenant binding

Per D393: tenants binding to an MC are subject to runtime drift detection (admission probe + S3 quarantine + ticket service). MCF specifies that:

- The runtime drift posture is **declared at publication** (PE-MC-8 intent).
- The runtime drift detection runs **at the boundary**, not in MCF.
- Drift findings emit tickets to the operator; MCF does not auto-mutate active MCs in response to drift (Invariant III).
- Drift may trigger operator-initiated supersession (§10.5).

### 14.6 Multi-tenant MC patterns

A single `active` MC may serve N tenants concurrently. Each tenant has its own binding row and its own MLS 15-25 state. The MC itself has no per-tenant variation; the binding carries the tenant-specific runtime context.

Exception: an MC whose computed dimensions depend on tenant-specific configuration (e.g. tenant fiscal calendar). The MC's formula references `fiscal_period` generically; the tenant's binding resolves to its specific fiscal calendar config. The cross-tenant compatibility question (whether an MC may be bound to two tenants whose configs would produce semantically different `fiscal_period` values for the same input) is open question §19.7 Q23.

---

## 15. Runtime / evaluation boundary requirements

### 15.1 MCF is upstream of the metric evaluation boundary

The metric evaluation boundary (per Foundation `the-evaluation-boundaries.md`) reads the active Metric Contract at evaluation time and produces a Metric Snapshot. MCF authors the active Metric Contract. The two never touch directly: MCF writes governed grammar; the boundary reads governed grammar; they meet only at the read.

### 15.2 Reads do not trigger evaluation

Per Foundation boundary-independent rule: *"Reading a progression object, a Canonical Mapping, or a Contract does not cause a boundary act. Evaluation is explicitly invoked, not implicit in access."*

MCF reads (in the operator console, in the panel, in audit) never trigger metric evaluation. A diagnostic that re-runs evaluation to "fix" a metric snapshot value is a violation, not a fix.

### 15.3 The metric evaluation boundary resolves and records the exact MC version

The metric evaluation boundary resolves the active MC version at invocation time and **records the exact MC version (id + version code + identity hash) in the Metric Snapshot's evidence and lineage objects**. Per Foundation Invariant IV, every reference identifies type, identity, and version. The boundary does not implicitly read "latest active"; it resolves the active version explicitly at the moment of invocation and pins that resolution into the snapshot's audit trail.

Operational consequence: if the MC is superseded between two evaluations (per §10.5), each Metric Snapshot carries the exact MC version it evaluated against. Snapshot A pre-supersession cites the predecessor MC; Snapshot B post-supersession cites the successor MC. There is no version ambiguity in the snapshot record. Re-evaluating the predecessor MC (forbidden per Invariant V — evaluation is non-replayable) is never the path to "fix" a snapshot.

MCF does not push to the boundary; the boundary reads the resolved-and-recorded grammar at invocation time. MCF is upstream; the chain is downstream; they meet only at the explicit read.

### 15.4 MCF does not own runtime state

MCF does not own:

- **Metric Snapshot rows** — produced by the metric evaluation boundary, immutable per Invariant III.
- **Evidence Objects** for metric evaluations — emitted at the boundary per Invariant VI.
- **Lineage Objects** for metric evaluations — emitted at the boundary per Invariant VI.
- **`mc_dependency` runtime tables** (per D316 readiness scheduler) — these are derived from MC authoring + tenant binding; MCF authoring produces inputs to the derivation but does not own the table.
- **L-node semantic verdicts** (per D366) — these are evaluation-boundary verdicts about active MCs, not MCF authoring state.
- **Runtime drift detection findings** (per D393) — these are boundary observations, not MCF artifacts.

MCF may *consume* runtime state for readiness gates and calibration — but it does not own or produce it.

### 15.5 The metric evaluation engine is preserved

Per ADR DEC-02f5a9 §5: *"Metric definitions / knowledge (the KPI catalog) — Survive as knowledge — only the binding to concepts is rebuilt."*

The metric evaluation engine (the runtime that reads active MCs and produces Metric Snapshots) is preserved. MCF re-authors the bindings an MC carries (variable bindings → BusinessConcepts; grain → Entity); it does not rewrite the engine.

What this means concretely: when MCF authors an MC against the BCF Registry, the MC produces the same kind of numeric value through the same engine that legacy MCs produced. The MC body changes (BCF bindings replace the dropped substrate bindings); the engine runs unchanged. This is the "fold-into-engine" principle inherited from BCF re-authoring.

### 15.6 Chain status SSOT integration

Per DEC-bebaec (Chain Completeness SSOT, 7-link definition of complete): the chain status SSOT is the authoritative read for "is this MC complete in this tenant?". MCF authoring reads the SSOT for tenant-binding readiness gating (MLS 15-25 stage transitions consume chain-status results). MCF does not write to the SSOT.

### 15.7 Readiness scheduler integration

Per D316 (`mc_dependency` + `readiness_ledger` + event hooks): the readiness scheduler observes binding/runtime events and updates the ledger. MCF authoring registers its MC dependencies (when an MC is published, the dependency edges are derived from its variable bindings and recorded in `mc_dependency`). MCF does not own the scheduler.

### 15.8 L-node semantic gate integration

Per D366 (DEC-804874): the L-node semantic gate produces verdicts on active MCs based on cross-cutting semantic analyses. MCF authoring consumes verdicts as inputs to operator-confirm dialogs (e.g. "L-node verdict is RED on this MC; confirm supersession with rationale"). MCF does not produce L-node verdicts.

---

## 16. Migration-free re-authoring stance after D418

### 16.1 The principle: greenfield, not migration

After the D418 closeout, there is no legacy substrate to migrate from. The historically-quarantined surfaces no longer exist. MCF re-authoring is **greenfield** — every active MC under MCF is authored fresh against the BCF Registry, with no path traced back through the dropped surfaces.

This is the operationalization of DEC-02f5a9 §4 ("shim is the corruption preserved, not a fix") in the post-disposition world.

### 16.2 What "no migration" means concretely

| Forbidden | Why |
|---|---|
| A `(legacy_mc_id, mcf_mc_id)` mapping table | Re-introduces the legacy identity layer that D418 retired |
| A `(legacy_business_field_id, business_concept_id)` mapping table | Re-introduces the BF identity layer that D418 retired (and the dropped column would have no source anyway) |
| A name-resolution shim that resolves legacy MC names to MCF MC ids | Shim is the corruption preserved per DEC-02f5a9 §4 |
| A "compatibility wrapper" that emulates the legacy binding API for new MCF MCs | Reverse-direction shim; same prohibition |
| Importing legacy MC bodies into MCF as candidate drafts | Imports the dropped substrate's binding shape; violates working rule |
| Reading the dropped surfaces during MCF authoring | The tables don't exist; also forbidden by working rule |
| Lineage edges from legacy MCs to MCF MCs | No legacy MC artifact exists to lineage from |

### 16.3 How KPI catalog intent becomes a candidate MCF artifact

The preserved KPI catalog (`metric.metric_definition`, `metric.metric_knowledge`) survives as **metric intent only** (per §5). MCF authoring sessions may use KPI catalog rows as **background knowledge** — the way an operator might consult an industry reference.

The operational workflow:

1. **Triage.** The MCF authoring program identifies a KPI catalog row (e.g. "Days Sales Outstanding (DSO)") as a candidate for MCF re-authoring.
2. **Background read.** The MCF panel reads the KPI catalog row's intent fields (display name, prose definition, owner, threshold, formula prose). This is *reading*, not *citing*.
3. **PE-MC-1 evidence sourcing.** The panel seeks **authoritative** evidence for the MC — a recognized standard (e.g. "DSO per the AICPA accounting practice"), a bc-seed entry (e.g. `bc-seed/metrics/dso.yaml` if present), an operator-authored bounded-domain definition, or a source-system observation with verifiable alias.
4. **MCF MC drafted.** The panel proposes an MC under the new identity discipline (§4): grain = a Registry Entity (e.g. `Customer Invoice`); variables bound to Registry BCs (e.g. `Customer Invoice · outstanding amount`, `Customer Invoice · invoice date`); formula AST authored; temporal gate selected; filters specified.
5. **PE-MC-1..PE-MC-9 evaluated.** The panel runs all nine checks. The grounding citation traces to the PE-MC-1 source from step 3 — NOT to the KPI catalog row. The KPI catalog row remains as background reading; the cert's grounding URL is the authoritative source.
6. **Publication.** If all PE-MC checks pass and the panel returns `APPROVE`, the MC progresses through `draft → review → approved → active` per §10.2. Operator-confirm fires at `approved → active` per §11.4.
7. **Tenant binding.** Operators bind tenants to the new MC; MLS 15-25 advances per §14.

The KPI catalog row is the *seed* of the operator's intent; the MCF MC is the *governed re-authoring*. **No binding or authority flows from the KPI catalog row to the MC.** Intent fields (display name, prose definition, owner, threshold default, formula prose) may seed draft suggestions in the authoring panel; every suggestion must be re-authored under MCF discipline (PE-MC-1..PE-MC-9) and independently grounded against a PE-MC-1 evidence source. The KPI row never appears in the MC's authority chain — not in its identity tuple, not in its variable bindings, not in its formula AST, not in its certification record's grounding citations.

The MC's bindings, formula AST, and identity tuple are authored fresh. The MC's PE-MC-1 grounding cites the authoritative source (recognized external standard, bc-seed entry, operator-authored bounded-domain definition, source-system observation), not the KPI row that seeded the draft.

### 16.4 What KPI catalog data is permitted to read

| Field | Permitted read context | Citable as PE-MC-1? |
|---|---|---|
| `metric.metric_definition.display_name` | Background reading during MCF authoring | No |
| `metric.metric_definition.prose_definition` | Background reading | No |
| `metric.metric_definition.owner` | Background reading; may inform operator routing | No |
| `metric.metric_definition.threshold_value` | Background reading; may inform MC threshold default | No |
| `metric.metric_definition.formula_prose` | Background reading | No |
| `metric.metric_knowledge.notes` | Background reading | No |
| `metric.metric_knowledge.industry_references` | If they point at a recognized external standard, the standard itself is a PE-MC-1 (a) source. The KPI catalog row that pointed to the standard is not. | Indirectly — cite the standard, not the catalog row |

### 16.5 The dropped substrate is forbidden as evidence

Restated for emphasis (this is the load-bearing constraint of post-D418):

**No MCF artifact, panel output, certification record, lineage edge, or substrate read may cite the historically-quarantined-now-dropped surfaces** (BF, BO, BOF, BOR, BFA, CF, CM) as evidence, source, lineage, migration input, bridge, compatibility shim, design input, or inspiration.

The substrate cannot violate this constraint because the tables don't exist; the working rule binds session-level discipline so even diagnostic queries against information_schema for these tables are not permitted authoring-context reads.

### 16.6 The pace of MCF re-authoring

There is no fixed timeline. The KPI catalog has ~1,819 entries; MCF re-authoring proceeds at the cadence the framework can sustain Framework Approval discipline for. The operational sequencing — which functions first, which industries first, which tenants first — is program management, not requirements.

Requirements: the post-D418 platform begins with zero `active` MCs under MCF (because every MC the legacy chain held was bound through the now-dropped substrate). MCF authoring grows the active set one MC at a time, under Framework Approval. The platform is operationally functional for whichever active MCs MCF has authored at any point in time.

---

## 17. Required substrate tables (conceptual only)

This section describes the substrate MCF requires at the **conceptual** level. Exact column lists, indexes, triggers, constraints, and migration sequencing are implementation DBCP scope. The conceptual descriptions below are sufficient to scope implementation gates (§20) but are not themselves a substrate design.

### 17.1 Tables MCF requires

| Table | Purpose | Notes |
|---|---|---|
| `mcf.metric_contract` | The MC's identity-bearing row | Identity tuple from §4.2 enforced as partial UNIQUE; immutable on identity-bearing columns when `lifecycle_state = 'active'` via `BEFORE UPDATE` trigger |
| `mcf.metric_contract_version` | Per-version MC body (formula AST, variable binding set, temporal gate spec, filter set, descriptive metadata) | Versions are append-only; one `active` version per MC |
| `mcf.metric_contract_revision` | Descriptive-only revisions to active MCs (display name, owner, threshold, etc.) | Per §4.6; versioned but does not bump identity |
| `mcf.metric_supersession` | Predecessor → successor edges; correction class; operator sub; rationale; panel run uid | Per §10.5; safety net for the immutable-atom model |
| `mcf.metric_variable_binding` | Per-MC-per-variable binding to BCF (Entity or BC by id, role, bind-time check results) | Per §6; bind-time checks materialized as columns for audit |
| `mcf.metric_formula_ast` | The AST itself (serialized canonical form) plus the formula identity hash | Per §7 / §8 |
| `mcf.metric_filter_clause` | Per-filter row, set-semantic for identity | Per §4.5 |
| `mcf.metric_computed_dimension_ref` | When an MC references a computed dimension, the governing-config link | Per §9 |
| `mcf.metric_package_signature` | Per-MC-version composite package signature hash (formula_ast_hash + variable_binding_set_hash + grain_filter_temporal_dimension_signature_hash) per §8.7 | Per §8.7 + §12; substrate-computed on MC write; UNIQUE per (mc_version_uid, algorithm_version); immutable per Invariant III |
| `mcf.metric_self_verification_fixture` | Per-MC-version fixture body: Section A declared inputs, Section B declared expected output, Section C resolver fixture config (per §12.4); bound `package_signature_hash` and `self_verification_fixture_hash` | Per §12; UNIQUE per (mc_version_uid, self_verification_fixture_hash); fixture content stored as canonical serialization; immutable once cited by a passing verification result (§12.9) |
| `mcf.metric_self_verification_result` | Per-(fixture, package_signature_hash, verifier_version) deterministic verification record: verdict (`pass` | `fail` | `structural_reject`), per-row diff trace if fail, reject reason if structural_reject, executed-at timestamp, verifier algorithm version | Per §12.6; append-only per Invariant V; one row per execution; cited by `mcf.metric_publication_eligibility_result` rows for PE-MC-10 |
| `mcf.tenant_binding` | Per-tenant binding to an active MC | Per §14; MLS 15-25 state |
| `mcf.metric_publication_eligibility_result` | Per-publication PE-MC-1..PE-MC-10 evaluation results (PE-MC-10 row cites the `mcf.metric_self_verification_result` it was satisfied by) | Per §13; immutable per Invariant V |
| `mcf.metric_authoring_panel_run` | Panel run record (run uid, prompt version, policy version, workspace fingerprint hash, per-model transcript uids, per-model verdicts, consensus computation result, grounding-check result per claim) | Per §11.3; transcript-shaped — each model's interactive tool-call trace + reasoning is the immutable audit artifact (not a single static "input hash"); all immutable per Invariant V |
| `mcf.metric_authoring_panel_transcript` | Per-model immutable transcript: full tool-call trace, each tool's response, model reasoning chunks, verdict + defect code if rejected | Per §11.3.5; one row per (panel_run, model); transcript content stored verbatim |
| `mcf.workspace_tool_allowlist` | Versioned allowlist of tools the workspace exposes (BCF search, evidence retrieval, source-reality summary, etc.) | Per §11.3.3; allowlist version is part of workspace fingerprint |
| `mcf.evidence_source_allowlist` | Versioned allowlist of evidence sources the workspace may cite (standards URIs, bc-seed entries) | Per §11.3.3; allowlist version is part of workspace fingerprint |
| `contract.certification_record` (Foundation Governance Substrate) | Cert-backed authority records. MCF writes rows scoped by MCF `action_code` values (`metric_create`, `metric_transition`, `metric_supersede`, `metric_revision_descriptive`, `metric_binding_change`). | Per §11.5 + §17.3; shared with BCF as Foundation Governance Substrate; neither framework owns; each writes its own scoped rows |
| `contract.framework_policy` (Foundation Governance Substrate) | Policy rows for MCF operator-confirm and panel discipline. MCF writes rows scoped by `scope_code = 'mc'`. | Per §17.3; whether MCF needs an `mcf.framework_policy` sibling instead is open question §19.10 Q26 |
| `contract.operator_confirm_rule` (Foundation Governance Substrate) | Operator-confirm rule rows for MCF actions per §11.4. MCF writes rows scoped by `scope_code = 'mc'`. | Per §17.3 |

### 17.2 Tables MCF does NOT need

- **No mapping table** from legacy MC ids to MCF MC ids (per §16.2).
- **No mapping table** from legacy BF/CF ids to BC ids (per §16.2).
- **No compatibility view** that emulates the legacy binding shape for MCF MCs.
- **No `mc_dependency`** ownership — `mc_dependency` is the D316 readiness scheduler's table; MCF authoring registers entries via the scheduler API but does not own the table.

### 17.3 Substrate ownership

Three ownership classes:

**Framework-owned substrate.** Each framework owns its own substrate tables. The owning framework writes, reads, and evolves; the other framework reads only.

- **`mcf.*` tables**: MCF-owned. MCF writes, reads, evolves. BCF does not write.
- **`concept_registry.*` tables** (BCF Registry): BCF-owned. BCF writes, reads, evolves. MCF reads only (variable binding targets per §6).

**Foundation Governance Substrate.** Shared tables that record governance acts of either framework. Neither framework owns the table; each framework writes rows scoped by its own `framework_code` or `action_code` namespace. The substrate provides cross-framework audit uniformity (one cert table queryable across frameworks). Per §3.8, this is parallel writes into a shared governance table, not cross-framework mutation.

- **`contract.certification_record`**: Foundation Governance Substrate. BCF writes rows with BCF `action_code` values (`registry_transition`, `registry_supersede`, etc.); MCF writes rows with MCF `action_code` values (`metric_transition`, `metric_supersede`, `metric_create`, `metric_binding_change`, `metric_revision_descriptive`). Neither framework reads or mutates the other's rows.
- **`contract.framework_policy`**: Foundation Governance Substrate. Each framework's policy rows are scoped by `scope_code` (e.g. `bf_bo`, `registry`, `mc`); each framework reads only its own scope.
- **`contract.operator_confirm_rule`**: Foundation Governance Substrate. Each framework's rule rows scoped by `scope_code`; same read discipline.

If, during implementation DBCP design, the column shape diverges enough between BCF and MCF needs (open question §19.10 Q26-Q27) that the shared shape becomes brittle, the operator may decide to split into `bcf.*` and `mcf.*` siblings. The default assumption is shared Foundation Governance Substrate; the alternative is operator-decided substrate refactor.

**External-system substrate.** Tables owned by other components MCF integrates with. MCF reads only; the owning component handles writes.

- **`metric.metric_definition`, `metric.metric_knowledge`** (KPI catalog): operator-tenant onboarding owns. MCF reads only (background knowledge per §5).
- **`metric.mls_state`** (per D392): MLS framework owns. MCF integrates via the MLS framework's API; ownership boundary in §14.
- **`mc_dependency`, `readiness_ledger`** (per D316): readiness scheduler owns. MCF authoring registers dependency edges via the scheduler API.
- **L-node semantic verdict tables** (per D366): L-node semantic gate owns. MCF reads at operator-confirm time.

### 17.4 Implementation DBCP scope

For each table above that MCF owns (`mcf.*`), an implementation DBCP must specify:

- Column list with types and constraints.
- Indexes for the substrate UNIQUE constraints and the lookup query patterns.
- Triggers for immutability enforcement (per Invariant III) and identity tuple enforcement (per §4.2).
- Migration sequencing (greenfield create; no data migration).
- Drizzle schema additions.
- Read repository / write repository pattern (analogous to BCF's `framework-approval/repositories/*`).
- Test coverage for the substrate constraints.

For `mcf.metric_package_signature` + `mcf.metric_self_verification_fixture` + `mcf.metric_self_verification_result`, the implementation DBCP additionally specifies the **deterministic verifier service**: the executable component that reads a package by `package_signature_hash`, reads a fixture by `self_verification_fixture_hash`, runs C-FX-1..C-FX-11 structural checks (§12.5), executes the package against Section A inputs with Section C resolver fixture configs, compares against Section B expected output, and emits a `pass | fail | structural_reject` row to `mcf.metric_self_verification_result`. The verifier service carries its own algorithm version and is itself reproducibility-tested.

§20 enumerates the implementation gates that consume these DBCPs.

---

## 18. Operator console requirements (conceptual only)

MCF requires an operator console mirroring the BCF UI-S1..S5 arc. This section specifies the console at the **conceptual** level. Exact React component shapes, route paths, API endpoint definitions, and visual design are implementation scope.

### 18.1 The console's purpose

The MCF operator console is the human surface through which operators:

1. Review MCF authoring panel outputs (proposed MC drafts, supersession proposals, binding-change proposals).
2. Confirm high-risk MCF actions with rationale (operator-confirm dialogs).
3. Inspect active MCs, their identity tuples, their PE-MC results, their bindings.
4. Track tenant bindings and MLS 15-25 progression.
5. Audit the panel-run trail and certification history.
6. Override AI decisions when the exception path is warranted.

### 18.2 UI surface inventory

| Surface | Purpose | Inherited pattern |
|---|---|---|
| **MC List** | Browse active / draft / superseded MCs; filter by function, owner, grain entity, bound tenants | BCF Business Concept list |
| **MC Detail (read)** | Inspect an MC: identity tuple, formula AST visualization, variable bindings, temporal gate, filter set, package signature hash, PE-MC results (PE-MC-10 row links to the satisfying verification result), panel run history, cert history, tenant bindings, fixture list with verifier verdicts | BCF Business Concept detail |
| **MC Draft Edit** | Edit a draft MC: formula AST builder, variable binding picker (BCF search), grain entity picker, temporal gate selector, filter editor, descriptive metadata | New — formula AST builder is novel UI |
| **MC Self-Verification Fixture Authoring** | Inspect, propose, or operator-author the fixture body for a draft MC: Section A declared inputs (rowsets per variable), Section B declared expected output, Section C resolver fixture config; live structural check pass/fail (C-FX-1..C-FX-11); panel-proposed fixtures presented for operator review; operator may revise within immutability bounds (§12.9) | New — derived from §12 fixture shape |
| **MC Self-Verification Run** | Trigger a deterministic verifier execution against a fixture; deterministic `pass | fail | structural_reject` verdict surfaced with per-row diff trace on `fail` and reject reason on `structural_reject`; verifier result record link; stale-fixture banner if fixture's bound `package_signature_hash` mismatches the MC's current hash | New — wraps §12.6 verifier behavior |
| **MC Publication Confirm** | Operator confirms `approved → active`: re-renders Step A evidence bundle (PE-MC-1..PE-MC-10 results including the cited self-verification result for PE-MC-10, bindings, formula); Step B operator rationale (≥40 chars); Step C semantic-finality affirmation if §10.6 adopted | BCF UI-S1..S5 publication flow |
| **MC Supersession** | Operator initiates supersession: select successor MC; correction class; rationale ≥40 chars | New — analogue of BCF characteristic supersession |
| **Tenant Binding List** | Per-tenant view of which MCs are bound, MLS state, drift status | New — surfaces MLS 15-25 substrate |
| **Tenant Binding Detail** | Per-binding view; manual intervention dialogs (acknowledge drift, request re-evaluation, supersede binding) | New |
| **Panel Run Audit** | Browse panel runs; per-run view with prompt version, model identity, per-agent verdicts, grounding citations, verdict, policy version | BCF panel audit |
| **Cert Audit** | Browse certification records (filter by action_code, MC id, operator) | BCF cert audit |
| **MLS Operations** | Operational view of platform MLS 1-14 and per-tenant MLS 15-25 progression for active MCs | New — D389-D393 surfaces |

### 18.3 UI inheritance from BCF UI-S1..S5

The console inherits, without re-derivation:

- Single-session request → review → confirm flow for high-risk actions.
- Step A evidence bundle re-render (server-resolved, never client-supplied).
- Step B operator rationale with ≥40-char floor.
- Step C semantic-finality affirmation (if §10.6 adopted).
- Phase 1 skip on already-published (idempotent resume on duplicate cert per Fork-ii).
- Shared loading / error / empty primitives.
- A11y on publish flow (focus management, screen reader labels, keyboard nav).
- Read-only verification journey BEFORE write gates (the operator inspects the panel run, the PE-MC results, the bindings — then commits to confirm).

### 18.4 The formula AST builder (novel UI)

The formula AST builder is the one significant net-new UI surface MCF needs. Its requirements:

- **Visual tree composition** — operators (and AI panel previews) compose the AST by adding nodes from the closed taxonomy (§7.2).
- **Type-aware binding** — at each `variable_ref` insertion point, the picker shows BCF BusinessConcepts whose representation term + unit are compatible with the node's expected type (per §6.3 checks).
- **Aggregate scoping** — at each `aggregate` node, the engine renders the grain context so operators see what set the aggregate operates over.
- **Real-time identity hash** — as the AST is composed, the formula identity hash (per §8) is computed and displayed. Operators see when their authoring change would collide with an existing MC's identity tuple.
- **Read-back** — the canonical AST renders to a human-readable form (`"SUM(unit_price) / COUNT(line_number)"`) for review.
- **No free text** — the builder does not accept formula text input. The AST is composed structurally.

### 18.5 Pre-write verification journey

For every operator-confirm dialog (MC publication, MC supersession, binding change), the operator first proceeds through a verification journey:

1. Server-rendered evidence bundle (the PE-MC results, the panel run summary, the BCF bindings shown by name + id).
2. Read-only display of the proposed change (the MC draft body in canonical form).
3. Server-rendered consequence summary (what tenant bindings this would affect; what L-node verdicts are present; whether downstream Intervention Contracts trigger).
4. Operator rationale field (≥40 chars; pre-submit validation).
5. Optional semantic-finality affirmation (§10.6 if adopted).
6. Confirm button (gated until rationale is valid).

This journey is the same shape as BCF UI-S1..S5 publication confirm.

### 18.6 What the console does NOT do

- **Does not** allow editing active MCs (Invariant III; edit a draft, then supersede).
- **Does not** allow free-text formula input (per §18.4).
- **Does not** show or allow read of the historically-quarantined-now-dropped surfaces (working rule; substrate tables don't exist).
- **Does not** trigger evaluation as a side effect of viewing an MC (per §15.2).
- **Does not** auto-resolve panel rejections (operator decides routing).

---

## 19. Open questions and full-plan markers

Items the requirements surface but defer. Each becomes an implementation DBCP topic or an open question for the foundational MCF ADR.

### 19.1 Identity model

- **Q1 — Formula intent hash normalization completeness.** §8 specifies the v1 rules. Implementation DBCP refines the per-operator commutativity/associativity rules and locks the canonical serialization format.
- **Q2 — Variable binding set ordering.** Working position: ordered for positional (numerator/denominator); named for non-positional (filter inputs). Implementation DBCP settles the role-label vocabulary.
- **Q3 — Composite-grain supersession ripple mechanics.** When a composite BCF Entity is superseded, what is the per-MC re-authoring obligation? Per §4.8; implementation DBCP specifies the substrate signals.

### 19.2 Formula AST

- **Q4 — Closed operator taxonomy completeness.** §7.2 lists v1. Implementation DBCP enumerates the full per-operator strict typing rules and identifies which operators are commutative for normalization.
- **Q5 — Window semantics for `window` AST node.** How `temporal_gate_shape = 'trailing_window(N, day)'` interacts with `LAG / LEAD / MOVING_AVG` nodes. Implementation DBCP specifies.
- **Q6 — Cross-grain aggregation prohibition exceptions.** §7.3 forbids cross-grain aggregation. Implementation DBCP specifies whether legitimate derived-grain aggregation patterns (e.g. line → header) become a new derivation rule (§9.4) instead.

### 19.3 Variable binding to BCF

- **Q7 — Reachability check algorithm.** §6.3 check 5 requires the bound BC be reachable from the grain entity via identity-bearing reference properties. Implementation DBCP specifies the DFS algorithm (depth limit; cycle detection though the DAG is acyclic per BCF).
- **Q8 — Unit conversion at bind time.** Working position: unit must match at bind time, or the bind is rejected; conversion is OC/CC body responsibility. Implementation DBCP settles edge cases (currency conversion, time-unit conversion).
- **Q9 — Bind to draft BCs publication ordering.** Per §6.6, an MC and its required-new BC must reach `active` together. Implementation DBCP specifies the coordination protocol.

### 19.4 Computed dimensions

- **Q10 — Computed dimension closed set boundaries.** §9.2 lists v1. Implementation DBCP enumerates the platform-supported set and the rules for tenant-specific computed dimensions (whether tenants can author their own).
- **Q11 — Tenant-specific computed dimensions.** Working position: tenant-specific configs (e.g. tenant fiscal calendar) are governed at the tenant config layer; MCF MCs reference the dimension generically; the tenant binding resolves through tenant config. Implementation DBCP specifies the cross-tenant compatibility.

### 19.5 Lifecycle and immutability

- **Q12 — Revision vs supersession boundary per identity-tuple field.** §4.6 declares the principle; implementation DBCP enumerates per-field detail.
- **Q13 — Threshold change and downstream action consequence.** §11.4 flags threshold changes on MCs bound to active Intervention Contracts as high-risk. Implementation DBCP specifies the substrate trigger that detects the consequence.
- **Q14 — MCF analogue of ADR DEC-26b6e2 (Characteristic atoms).** Whether MCF adopts publication-time semantic-finality affirmation for some MC sub-element (formula AST? grain commitment?). Implementation DBCP decides.

### 19.6 Authority model

- **Q15 — MCF panel prompts / model selection.** BCF B6 uses a three-model trio. MCF may use the same or specialize. Implementation DBCP specifies.
- **Q16 — Calibration sampling rate.** BCF samples for calibration at some rate. MCF rate may differ given the differing failure modes of metric vs vocabulary work. Implementation DBCP specifies.
- **Q17 — Operator-confirm rule completeness.** §11.4 names initial high-risk actions. Implementation DBCP enumerates the complete operator-confirm rule set.

### 19.7 Publication eligibility (PE-MC)

- **Q18 — PE-MC-1 (d) operator-authored definitions confirm policy.** Whether bounded-domain operator-authored definitions require explicit operator-confirm at publication. Mirrors BCF's PE1 open question.
- **Q19 — PE-MC-7 cross-tenant calendar metrics.** Whether MCs that span tenants with different fiscal calendars need a special PE-MC sub-rule. Working position: cross-tenant fiscal-calendar mismatch is per-tenant-binding concern (MLS 15-25), not publication-blocking. Implementation DBCP revisits.
- **Q20 — Multi-tenant fiscal-calendar semantic divergence.** When two tenants of the same MC have fiscal calendars that produce semantically different `fiscal_period` values for the same input — is this acceptable or is it a defect? Working position: acceptable as a tenant-config diversity surface, but operator-visible. Implementation DBCP revisits.

### 19.8 Boundary with BCF

- **Q21 — Cross-framework coordination mechanics.** §3.8 sketches events / pull-side reads. Implementation DBCP specifies (event bus? polling? subscription model?).
- **Q22 — BCF notification of MC supersession.** When MCF supersedes an MC that bound to a BC, does BCF need to know? Working position: yes, for consumer-count reads in BCF UI. Implementation DBCP specifies.
- **Q23 — Reference-property bind semantics.** §6.2 names reference-kind variable bindings. Implementation DBCP specifies the exact reference-binding semantics (does the MC operate on the reference target's entity, or on the reference itself as a join column?).

### 19.9 Runtime integration

- **Q24 — Runtime-readiness intent publication-blocking vs publication-deferred.** PE-MC-8 working position is publication-deferred. Implementation DBCP revisits.
- **Q25 — Drift-induced supersession workflow.** When D393 runtime drift detection identifies an active MC whose binding is drifting, what is the operator workflow? Working position: ticket + operator-initiated supersession proposal; no auto-mutation. Implementation DBCP specifies.

### 19.10 Substrate

- **Q26 — Cert table reuse vs new.** Whether MCF reuses `contract.certification_record` with new `action_code` values or gets its own `mcf.certification_record` sibling. Working position: reuse; minimizes substrate churn. Implementation DBCP decides.
- **Q27 — Authoring panel substrate.** Whether MCF reuses BCF's `panel_output_record` sibling pattern or has its own `mcf.metric_authoring_panel_run`. Working position: own table; the field set differs (formula-related, not concept-related).
- **Q28 — `mc_dependency` integration.** Per D316 readiness scheduler. Implementation DBCP specifies how MCF authoring registers dependency edges.
- **Q29 — `mcf.tenant_binding` ownership boundary with MLS substrate.** Where MLS substrate ends and MCF substrate begins. Implementation DBCP specifies the seam.

### 19.11 UI

- **Q30 — Formula AST builder UX details.** §18.4 lists requirements. Implementation scope (separate UI program of work).
- **Q31 — Operator console phasing.** Whether MCF console ships in phases (MC List + Detail first; AST builder later; tenant binding later) or as a single MVP. Implementation scope.

### 19.12 Workspace + tools mechanics (panel architecture)

- **Q32 — Tool-set v1 composition.** §11.3.3 lists the v1 tool set conceptually. Implementation DBCP specifies the exact tool schemas (request/response shapes), tool versioning rules, and the workspace fingerprint algorithm that hashes tool-set version + evidence-source allowlist version + BCF Registry snapshot id + operator-context hash.
- **Q33 — Evidence-source allowlist composition and curation.** Which standards/corpora are admissible (GAAP, IFRS, XBRL, OAGIS, ISA-95, industry methodologies, academic sources, bc-seed)? Who curates the allowlist? Curation cadence? Versioning of the allowlist for transcript reproducibility?
- **Q34 — Workspace-fingerprint vs per-transcript hash.** The workspace fingerprint covers the *inputs available to the panel*; per-model transcripts cover the *actual tool calls made*. Implementation DBCP specifies how the two combine into the consensus record's audit trail (e.g. is consensus rejected if two models used wildly different tool subsets even though both proposals satisfy PE-MC?). Working position: divergent tool-trace shape is acceptable as long as proposals converge on identity tuple + grounding citations; consensus is on proposal, not on transcript.
- **Q35 — Per-model parallel tool calls vs sequenced.** Whether the three models run in parallel against the workspace (each producing an independent transcript) or whether some tool calls are shared across the trio (e.g. a single BCF search result is read by all three). Working position: parallel + independent transcripts; consensus computed over independent proposals. Implementation DBCP revisits if cost/latency makes parallel infeasible.
- **Q36 — Operator-provided business context handling.** When the operator attaches free-text guidance to the panel run, is that text part of the workspace fingerprint (yes, hashed; see §11.3.5) and how does it factor into PE-MC-1 grounding (it does not — operator guidance is workspace input, not authority evidence)?

### 19.13 Self-verification fixtures

- **Q37 — Minimum fixture coverage by formula class.** §12.8 lists candidate coverage profiles (null-handling, boundary, resolver-sensitivity, grain-coverage, filter-coverage). PE-MC-10 currently requires at least one passing fixture. Implementation DBCP specifies the per-formula-class minimum (e.g. ratio metrics require both non-zero-denominator and zero-denominator fixtures; window metrics require both fully-populated-window and partial-window fixtures; metrics that filter on a computed dimension require fixtures exercising both pass-filter and fail-filter rows). Working position: minimum-coverage rules are an additive strengthening of PE-MC-10, not a replacement.
- **Q38 — Floating-point tolerance and null-match policy defaults.** Section B (expected output) declares per-fixture tolerance and null-match policy (§12.4). Implementation DBCP specifies the platform default tolerance per type/unit (e.g. currency to two decimal places vs ratio metrics to a relative epsilon) and the platform default null-match policy. Authoring may override per fixture; defaults govern when authoring is silent.
- **Q39 — Panel-proposed vs operator-authored fixtures.** §12.2 says the panel may propose fixtures using the governed workbench. Implementation DBCP specifies what proportion of fixtures are panel-proposed vs operator-authored at first deployment, the operator-confirm rules for panel-proposed fixtures (whether operator confirm is always required for fixture acceptance or only for novel-coverage cases), and how panel-proposed fixtures cite their grounding (e.g. fixture rows drawn from `source_reality.summarize` results vs bc-seed lineage). Working position: hybrid — panel proposes the structural shape and a starter row set; operator authors or confirms before the fixture is accepted as a PE-MC-10-eligible artifact.
- **Q40 — Fixture retention and versioning.** Stale fixtures are preserved per §12.7. Implementation DBCP specifies retention policy (indefinite? bounded by N successor versions? archived to cold storage after N years?), version-display rules in the operator console, and whether a stale fixture's `pass` result remains queryable as historical proof for the package version it bound to.
- **Q41 — Verifier algorithm versioning.** §12.6 verifier carries its own algorithm version. Implementation DBCP specifies how verifier upgrades interact with existing passing verification result records (do existing records remain authoritative for their package version under their verifier version, with a forward-compatibility rule for new package versions? do they require re-verification under the new verifier?). Working position: existing records remain authoritative; new package versions execute under the current verifier; verifier supersession is itself a Foundation-Invariant-V act with auditable algorithm-version migration.
- **Q42 — Cross-tenant fixture sensitivity.** A package that references a computed dimension (e.g. `fiscal_period`) is bound to a fixture-scoped resolver config (Section C). When the package binds to multiple tenants whose actual resolver configs differ, does a single Section C fixture suffice or does each per-tenant config require its own fixture? Working position: the fixture proves package-internal semantics under a chosen resolver config; per-tenant resolver divergence is a tenant-binding concern (MLS 15-25; §14) not a package-fixture concern. Implementation DBCP revisits if cross-tenant divergence patterns motivate per-tenant-config fixtures.

---

## 20. Implementation gate prerequisites

This section enumerates the implementation gates the foundational MCF ADR (and its successor implementation DBCPs) must satisfy before MCF authoring may begin. These gates are the operational sequence between this requirements document and a running MCF.

### 20.1 Prerequisite: foundational MCF ADR

Before any implementation, a foundational MCF ADR must be authored and decided (analogue of BCF's DEC-149ab2 / D411). It declares:

- The framework's scope (per §2).
- The framework's actors (Metric Authoring Panel, operators).
- The framework's disciplines (per §11).
- Framework Approval as the configured authority within the framework's scope.
- The relationship to the dropped substrate (per §16: no migration, no shim).

### 20.2 Implementation gates (sequenced)

| Gate | Scope | Prerequisites |
|---|---|---|
| **Gate M1 — Foundational MCF ADR** | Decide the foundational ADR | This requirements document accepted |
| **Gate M2 — Substrate DBCP: identity layer** | `mcf.metric_contract` + identity-tuple UNIQUE + `mcf.metric_contract_version` + `mcf.metric_formula_ast` + `mcf.metric_variable_binding` + `mcf.metric_filter_clause` + `mcf.metric_computed_dimension_ref` + `mcf.metric_package_signature` (composite signature hash per §8.7) | Gate M1; BCF Registry stable |
| **Gate M3 — Substrate DBCP: lifecycle layer** | `mcf.metric_contract_revision` + `mcf.metric_supersession` + immutability trigger; cert reuse pattern for `metric_create` action | Gate M2 |
| **Gate M4 — Substrate DBCP: publication layer** | `mcf.metric_publication_eligibility_result` + cert reuse for `metric_transition` action + operator-confirm rule policy entries for high-risk MCF actions | Gate M3 |
| **Gate M5 — Substrate DBCP: panel layer** | `mcf.metric_authoring_panel_run` + framework policy entries for MCF panel discipline | Gate M4 |
| **Gate M6 — Substrate DBCP: tenant binding layer** | `mcf.tenant_binding` + MLS 15-25 state integration with D392 substrate | Gate M5; MLS substrate stable per D392 |
| **Gate M7 — Formula AST authoring service** | Authoring service that constructs valid ASTs, runs normalization, computes identity hash, performs bind-time checks, computes composite package signature hash | Gate M2 |
| **Gate M8 — Self-verification fixture substrate DBCP** | `mcf.metric_self_verification_fixture` + `mcf.metric_self_verification_result` + structural-check engine (C-FX-1..C-FX-11 per §12.5) + stale-fixture rule enforcement (per §12.7) | Gate M2; Gate M7 |
| **Gate M9 — Deterministic verifier service** | Verifier component that executes packages against fixtures, applies resolver fixture configs (§9.2), emits `pass | fail | structural_reject` verification result rows; carries its own algorithm version; reproducibility-tested | Gate M8 |
| **Gate M10 — Metric Authoring Panel implementation** | Three-model panel; closed-enum verdicts; PE-MC-1 grounding; defect-code taxonomy implementation; panel-side fixture proposal capability against the verifier service | Gate M5; Gate M7; Gate M9 |
| **Gate M11 — PE-MC publication gate implementation** | Deterministic publication-gate evaluator for PE-MC-1 through PE-MC-10 (PE-MC-10 cites a passing `mcf.metric_self_verification_result` against the MC's current `package_signature_hash`) | Gate M9; Gate M10 |
| **Gate M12 — MCF publication path (Fork-i / Fork-ii)** | Two-phase request → operator confirm path for `metric_transition` (analogue of BCF B10 publication path) | Gate M11 |
| **Gate M13 — MCF supersession path** | Operator-initiated supersession with successor pointer; cross-framework supersession from BCF; supersession invalidates the predecessor's fixture (per §12.7 stale-fixture rule) and requires a fresh passing fixture for the successor before PE-MC-10 | Gate M3; Gate M12 |
| **Gate M14 — Operator console (MC List + Detail read)** | Read-only surfaces for MC inspection; PE-MC-10 result and fixture verdict surfacing on MC Detail | Gate M5 (panel run audit data exists); Gate M9 |
| **Gate M15 — Operator console (Draft Edit + AST builder)** | Authoring surfaces | Gate M7; Gate M14 |
| **Gate M16 — Operator console (Self-Verification Fixture Authoring + Run)** | Fixture authoring surface (Section A/B/C composition; C-FX structural-check feedback) + fixture run surface (verifier verdict + per-row diff trace) per §18.2 | Gate M9; Gate M15 |
| **Gate M17 — Operator console (Publication Confirm + Supersession)** | Write surfaces with operator-confirm dialogs; PE-MC-10 evidence in Step A bundle | Gate M12; Gate M16 |
| **Gate M18 — Tenant Binding console + MLS integration UI** | Tenant binding surfaces; MLS operations view | Gate M6; Gate M17 |
| **Gate M19 — Cross-framework coordination (BCF/MCF events)** | Event mechanics per §3.8 | Gates M13 + corresponding BCF readiness |
| **Gate M20 — KPI catalog re-authoring program** | Operational program (not a substrate gate) to re-author KPI intents into MCF MCs | Gate M17; ongoing |

### 20.3 Cross-cutting requirements per gate

Every implementation gate must satisfy:

- **Foundation invariant preservation** (per §10.3).
- **bc-qa shift-left coding standards** (per CLAUDE.md / bc-qa gate config).
- **Pre-commit ESLint clean** (no `--no-verify`).
- **Test coverage** for the substrate constraints and the publication eligibility logic.
- **Read-only verification artifact** (analogue of Gate 1.3.3 / Gate 5.3 verifier) demonstrating post-gate state matches the gate's intent.
- **Operator-reviewable PR** with explicit scope, evidence, and rollback story.

### 20.4 Non-prerequisites

These are explicitly NOT prerequisites for any MCF implementation gate:

- Restoration of any dropped substrate table.
- Creation of any `(legacy, mcf)` mapping table.
- Bridge / shim / compatibility wrapper to the dropped substrate.
- Re-implementation of the metric evaluation engine.
- Re-implementation of the fiscal calendar stack (D364 stack is consumed as-is).
- Re-implementation of the MLS framework (D389-D393 substrate is integrated, not reimplemented).
- Re-implementation of the chain status SSOT (DEC-bebaec is consumed).
- Re-implementation of the readiness scheduler (D316 is consumed).

---

## 21. Non-goals

Consolidated non-goals across the document. This list is the negative space that bounds MCF.

### 21.1 Substrate non-goals

- **No substrate DBCP in this document.** Substrate design is implementation DBCP scope (§17, §20).
- **No data migration from dropped surfaces.** Greenfield re-authoring only (§16).
- **No mapping table** between legacy ids and MCF ids (§16.2).
- **No bridge / shim / compatibility wrapper** to the dropped substrate (§16.2).
- **No reuse of dropped surface schemas** for new MCF tables.
- **No restoration of dropped surface tables** under any disguise.

### 21.2 Runtime non-goals

- **MCF is not a runtime component.** The metric evaluation boundary runs as Foundation defines (§15).
- **MCF does not own Metric Snapshots, Evidence Objects, Lineage Objects, or runtime ledger tables.**
- **MCF reads do not trigger evaluation** (§15.2).
- **MCF does not re-implement the metric evaluation engine** (§15.5).
- **MCF does not re-implement the fiscal calendar stack** (§9.3; D364 consumed as-is).
- **MCF does not re-implement MLS** (§9.5; D389-D393 substrate integrated).
- **MCF does not re-implement chain status SSOT** (§15.6; DEC-bebaec consumed).
- **MCF does not re-implement the readiness scheduler** (§15.7; D316 consumed).

### 21.3 Framework boundary non-goals

- **MCF does not author BCF artifacts** (Entity, Characteristic, BusinessConcept) — §3.3.
- **BCF does not author MCF artifacts** — §3.4.
- **MCF does not own Intervention Contracts** — separate framework or Foundation default (§2.3).
- **MCF does not own Source Contract, Admission Contract, Observation Contract, or Canonical Contract composition** — Foundation default applies (per BCF requirements §Scope).
- **No shared mutable state between BCF and MCF** (§3.8).

### 21.4 KPI catalog non-goals

- **KPI catalog rows are not citable as PE-MC-1 evidence** (§5.2; §13 PE-MC-1).
- **KPI catalog row content is not imported into MCF MC bodies** (§16.3).
- **The legacy MC bodies (which the dropped substrate held) are not importable** because the substrate no longer exists; even if it did, the working rule would forbid the import.

### 21.5 Authority non-goals

- **MCF does not relax Foundation invariants** — all six are preserved (§10.3).
- **MCF Framework Approval does not extend to non-MCF artifacts** (§11; analogue of BCF Framework Approval boundary).
- **MCF does not bypass operator override** at any lifecycle state (Rule 2 of §11.2).
- **MCF does not silently apply changes without authoring records** (Rule 3 of §11.2).

### 21.6 UI non-goals

- **MCF operator console does not allow active MC edits** (§18.6; Invariant III).
- **MCF operator console does not show or allow read of dropped surfaces** (§18.6; working rule).
- **MCF operator console does not trigger evaluation as a side effect** (§18.6; §15.2).
- **MCF operator console does not auto-resolve panel rejections** — operator decides routing (§18.6).
- **No free-text formula input in the MCF authoring UI** (§18.4; AST is structurally composed).

### 21.7 Implementation non-goals

- **No implementation plan in this document.** Implementation gates are enumerated in §20; the gates themselves consume implementation DBCPs that this document enables but does not contain.
- **No prompts, model selection, calibration sampling rates** for the Metric Authoring Panel in this document. Implementation DBCP scope.
- **No UI component specifications, route paths, API endpoint shapes** in this document. Implementation scope.
- **No bc-qa rule enforcement specification** in this document. The working-rule discipline (no reads of dropped surfaces from MCF authoring code) is a session-level discipline that bc-qa rules may enforce; the rule specification is operational scope.

---

## Status

`proposed` — requirements awaiting acceptance and the foundational MCF ADR.

This document is the requirements specification for the Metric Context Framework. It defines what MCF must be, in sufficient detail that an implementer can scope substrate DBCPs, panel implementations, publication paths, and operator console programs of work. It does not specify those implementations.

When this document is accepted, the next gate (Gate M1 in §20.2) is the foundational MCF ADR. Implementation DBCPs follow per §20.2.

**Bound for this document and any session that extends it**: the working rule (no BF/BO/CF/CM as evidence, source, lineage, migration input, bridge, compatibility shim, design input, or inspiration). The dropped substrate is past; MCF is the post-D418 future.
