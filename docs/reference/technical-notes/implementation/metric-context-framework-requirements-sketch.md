---
uid: metric-context-framework-requirements-sketch
title: Metric Context Framework (MCF) — Requirements Sketch
description: A sketch of the Metric Context Framework (MCF) requirements. The sibling framework to BCF for the governance discipline of metric meaning. Defines scope, boundary with BCF, identity model proposal, variable binding to Business Concepts, formula AST as a governed first-class artifact, computed dimensions, the authority model, the lifecycle, the MC publication eligibility contract (PE-MC), the working positions on the boundary questions the future Legacy Vocabulary Stack Quarantine ADR will need, and the inheritance from BCF discipline that MCF will not re-derive. Working rule binding for this sketch — no BF/BO/CF/CM as evidence, candidate source, lineage, bridge, migration input, or design input. status proposed.
status: proposed
date: 2026-05-24
project: bc-docs
domain: contracts
subdomain: catalog
focus: requirements
---

# Metric Context Framework (MCF) — Requirements Sketch

> **What this is.** A **sketch** of MCF requirements — the sibling framework to BCF. The full requirements document (when written) will mirror the depth of `business-context-framework-requirements.md`. This sketch establishes the spine — the structural positions and the working answers to the boundary questions the future Legacy Vocabulary Stack Quarantine ADR will need to be sharp. Marked content gaps are explicit ("to be specified in the full plan"). This is a **design note, not an ADR**; `status: proposed`. No code, no DB writes, no implementation follows from it.
>
> **Working rule binding for this sketch (and for any session that opens this doc to extend it).** No BF/BO/CF/CM as evidence, candidate source, lineage, bridge, migration input, or design input. The legacy vocabulary primitives appear only as quarantined risk. The carve-outs from ADR DEC-02f5a9 §5 — bc-seed, Source Contracts, Admission Contracts, Observation Contracts, and metric definition knowledge as intent — are not in the quarantine and may be cited.

---

## 1. Scope and grounding

### 1.1 Purpose

The Metric Context Framework (MCF) is the AI-assisted governance discipline for the contextual accuracy of the platform's **metric meaning**: what a metric *is*, what it measures, over what grain, against what context, using what formula, under what runtime conditions, evaluated against what data.

The Business Context Framework (BCF) governs the platform's business **vocabulary** — Entities, Characteristics, BusinessConcepts. The Metric Context Framework (MCF) governs the platform's metric **computation context** — Metric Contracts (MC) and the surrounding metric artifacts (formula AST, variable bindings, grain, temporal gate, thresholds, fiscal-calendar resolution, runtime-readiness gates). The two frameworks meet at the MC artifact: BCF supplies the BusinessConcepts and Entities the MC binds to; MCF authors the MC and everything that surrounds it.

### 1.2 Why MCF must exist

Three facts produce the requirement.

**First, Foundation Invariant I applied to metrics has no governed surface today.** Invariant I says *meaning is evaluated once, at the canonical evaluation boundary.* For business meaning this is satisfied by BCF + the canonical evaluation boundary. For *metric meaning* — the meaning produced at the metric evaluation boundary — the governing artifact is the Metric Contract, but the Metric Contract has no framework around it. Free-text formula authority, ad-hoc variable binding, drift-prone grain semantics, and uncodified runtime-readiness gates all live as scattered ADRs and helper scripts. Each is an implicit meaning authority unto itself. The platform's metric meaning is currently "evaluated more than once" in the sense that interpretation can shift between authoring time, binding time, evaluation time, and read time — exactly the failure Invariant I exists to prevent.

**Second, the BF/BO/CF stack is being quarantined.** ADR DEC-02f5a9 declared the legacy vocabulary untrustworthy and ordered greenfield rebuild. The metric chain still binds to that stack today through `cc_field_mapping`, `metric_binding`, and `runtime.reader.business_object_id`. Without MCF, every metric chain repair flows back into BF/BO/CF — reinforcing the contamination the Quarantine ADR exists to prevent.

**Third, drifting metric-context work has no architectural home.** Substantial ADRs name pieces of what MCF would own — fiscal calendar work (D363, D364, D365), chain completeness SSOT (DEC-bebaec), readiness scheduler (D316), L-node semantic gate (D366), MLS framework (D389–D393), runtime drift detection (D393). Each is correct in its slice. None has a sibling-of-BCF framework to live in. The result is an accretion pattern eerily similar to what BF/BO/CF showed before BCF: many correct slices, no governed authority binding them.

### 1.3 What MCF is

MCF is the **ADR-governed authoring mechanism** for metric-context artifacts. Under MCF, AI proposes, prepares, and approves metric-context content for in-scope members under **Framework Approval** (the same authority pattern BCF uses per ADR DEC-149ab2 / D411). Operator override is the exception, not the routine.

MCF is *not* a runtime component. The metric evaluation boundary runs as Foundation defines (The Evaluation Boundaries). MCF is upstream of the metric evaluation boundary: it authors the governed grammar state — Metric Contracts and the artifacts that surround them — that the metric evaluation boundary reads at runtime.

MCF is *not* a re-implementation of the metric evaluation engine. The engine is real today and is preserved (per ADR DEC-02f5a9 §5: "Metric definitions / knowledge (the KPI catalog) — Survive as knowledge — only the binding to concepts is rebuilt"). MCF re-authors the bindings against the BCF Registry; it does not rewrite the evaluation engine.

### 1.4 What MCF is not

- **Not a runtime component.** The metric evaluation boundary runs as Foundation defines.
- **Not an active participant at any evaluation boundary.** Foundation §The Evaluation Boundaries is unaffected by MCF.
- **Not a producer of authoritative runtime state.** MCF authors grammar state. Metric Snapshots, Evidence Objects, and Lineage Objects are produced only at the metric evaluation boundary.
- **Not a replacement for Foundation Contract Grammar.** The twelve grammar artifacts and their governance continue per The Contract Grammar.
- **Not in scope for BCF concerns.** Entity / Characteristic / BusinessConcept authoring is BCF's. MCF consumes BCF artifacts; it does not author them.
- **Not in scope for the four evaluation boundaries** (admission, canonical, metric, action) — these are Foundation.
- **Not in scope for Intervention Contracts** — those govern the action boundary, downstream of metric. A separate framework or Foundation default applies.

### 1.5 Foundation grounding

Foundation §The Authority Model establishes the three-level authority ladder (Foundation; ADRs and Errata; Descriptive). ADRs are the governed mechanism by which configured authoring paths are established. MCF is itself an ADR-governed mechanism: a foundational MCF ADR (the future sibling of DEC-149ab2 / D411) will declare the framework, name its authorized actors (Metric Panels, operators), specify the disciplines each actor must satisfy, and establish Framework Approval as the configured authority within the framework's scope.

Within this ADR-governed mechanism, AI consensus constitutes Framework Approval for in-scope members. Operator override is the explicit exception path. The framework is not a relaxation of Foundation; it is a configuration of the governed authoring mechanism that Foundation §The Authority Model permits.

MCF preserves all six Foundation invariants:

- **Invariant I.** Meaning is produced at the metric evaluation boundary, not in the framework. MCF authors the Metric Contract that the boundary applies; it does not produce Metric Snapshots.
- **Invariant II.** Object ordering is unaffected. MCF operates on grammar members (MC and surrounding artifacts), not on progression objects.
- **Invariant III.** Active grammar artifacts are immutable. AI cannot mutate an active MC. AI may propose or prepare a successor draft for an active MC; operator approval is required to supersede the active version.
- **Invariant IV.** All references identify type, identity, and version. MC references to BusinessConcepts and Entities are by id, never by name.
- **Invariant V.** AI panel outputs are immutable authoring records; audit reads them, never recomputes.
- **Invariant VI.** Authoring records are emitted at every framework write. Catalog-side MCF authoring records are distinct from Foundation Evidence Objects, which are emitted only at evaluation boundaries.

### 1.6 Source-of-authority documents

MCF requirements are grounded against:

- **Foundation chapters**: `the-invariants.md` (six invariants), `the-object-model.md` (six object types), `the-contract-grammar.md` (twelve grammar artifacts including Metric Contract), `the-evaluation-boundaries.md` (four boundaries including the metric evaluation boundary), `the-authority-model.md` (three-level authority ladder).
- **ADR DEC-02f5a9** (Business Concept Registry — governs the BCF/MCF boundary; especially §1 and §5).
- **ADR DEC-149ab2 / D411** (BCF authority delegation — template for MCF authority).
- **ADR DEC-26b6e2 / D415** (Immutable Characteristic Atoms — template for any MCF immutability analogue).
- **ADR DEC-65dc86 / D416** (BCF forward, BF/BO legacy compatibility — operational posture for the legacy stack).
- **BCF requirements doc** (`business-context-framework-requirements.md`) — sibling artifact this sketch mirrors.
- **BCF backend MVP close-out** + **BCF UI MVP close-out** — proven discipline to inherit.
- **Metric Workstream Playbook** (`onboarding/metric-workstream.md`) — existing operational overlay.
- **Drifting metric-context work that MCF will absorb**:
  - **D363** (DEC-1efa47): grain key-source mismatch — grain semantics drift.
  - **D364** (DEC-d7e7a0): platform `date_dim` + per-entity tenant fiscal calendar + `FiscalCalendarService` — the fiscal calendar stack.
  - **D365** (DEC-a8e8fc): CC declares `posting_date_field`; canonical resolution enriches payload with fiscal_period + fiscal_year.
  - **DEC-bebaec**: chain completeness SSOT — 7-link definition of complete.
  - **D316**: readiness scheduler — `mc_dependency` + `readiness_ledger` + event hooks.
  - **D366** (DEC-804874): L-node semantic gate.
  - **D389** (DEC-c9e623): Metric Lifecycle States (MLS) framework — 25 steps; platform 1-14, tenant 15-25.
  - **D390** (DEC-9d7a5c): MLS failure vocabulary.
  - **D391** (DEC-b8b825): MLS-14 gate.
  - **D392** (DEC-e7b7b3): MLS substrate.
  - **D393** (DEC-29f134): runtime drift detection.

### 1.7 Vocabulary discipline

- Foundation Contract Grammar lifecycle vocabulary throughout: `draft → review → approved → active → superseded`.
- "Admission" reserved for the runtime admission boundary per Foundation.
- "Approve" applies to AI within MCF's scope (Framework Approval); operator approval is the operator-driven exception path within the same governed authoring mechanism.
- "Authoring record" for catalog-side proof; "Evidence Object" reserved for Foundation runtime evidence.
- "Metric Snapshot" reserved for the boundary-produced authoritative object; never used for an MCF-side artifact.

---

## 2. Boundary with BCF

The single most important architectural line in MCF is the one with BCF. It is named in ADR DEC-02f5a9 §1 and `business-concept-registry.md` §8 — this section expands the named line into operational discipline.

### 2.1 The line: stored vs. computed

> **BCF governs observable concepts; MCF governs computed metrics.** The boundary is *who computes the value*: a value that arrives stored is a BCF Business Concept; a value the platform computes over grain, time, filter, and formula is an MCF metric.

This is the operational test. For any value the platform encounters:

| Test | If yes | If no |
|---|---|---|
| Does this value arrive in the platform pre-computed by an external system? | **BCF Business Concept.** Even if the source system derived it internally (e.g. `invoice.net_amount` already net of discounts) | Continue test |
| Does the platform compute this value at the metric evaluation boundary, over grain, time, filter, and formula? | **MCF metric.** | Continue test |
| Is it a structural/identity property of an entity (an `entity.property` tuple expressible without computation)? | **BCF Business Concept.** | Continue test |
| Is it a runtime-only artifact (evidence, lineage, snapshot)? | Not BCF, not MCF — this is Foundation runtime state. | Re-examine the test; the value may be miscategorized |

### 2.2 What MCF consumes from BCF (one-way)

MCF consumes BCF Registry artifacts by id, never by name:
- **Entity** (typed reference) — as the grain of a metric.
- **BusinessConcept** (typed reference) — as a metric variable binding (numerator, denominator, filter input, etc.).
- **Characteristic** (typed reference, indirectly) — through the BusinessConcept the characteristic appears in.

MCF does **not** consume BCF Registry artifacts by name lookup, by free-text reference, or by partial match. All MCF→BCF references are by Registry id. This is Invariant IV applied to the MCF/BCF boundary.

### 2.3 What MCF does not author

MCF cannot author Entity, Characteristic, or BusinessConcept. If an MC requires a BusinessConcept that does not yet exist in the Registry, the authoring path is: (1) operator routes the candidate to BCF for authoring through the B6 panel; (2) the BCF authoring path runs greenfield (per ADR DEC-02f5a9 §4); (3) the resulting BusinessConcept becomes available in the Registry; (4) MCF authoring resumes against the now-available BC.

MCF cannot reach into BCF to create or modify Registry rows. The Registry's authoring surface is BCF-only.

### 2.4 What BCF does not author

BCF cannot author Metric Contracts, formulas, variable bindings, grain declarations, fiscal-calendar bindings, temporal gates, thresholds, or any MCF artifact. The metric chain is MCF-only.

### 2.5 The boundary lives at the MC artifact

> *"The boundary between BCF and MCF lives at the MC artifact: BCF governs no part of the MC. The cross-framework coordination on variable binding (where MCF references BusinessConcepts that BCF governs) is specified in MCF."* — BCF requirements §Scope, adapted for the post-DEC-02f5a9 model.

This sketch is the beginning of that coordination specification.

### 2.6 Computed values that look like stored values

Edge case worth naming explicitly because it is the operative test for several drift cases:

**`fiscal_period`** — a tenant SAP source system stores `fiscal_period` directly on every line (e.g. SAP's `MONAT` field). Is this BCF or MCF?

Answer: **MCF**. The platform's authoritative `fiscal_period` is the value the platform's `FiscalCalendarService.resolve(posting_date)` computes from the tenant's governed fiscal calendar configuration (per D364). The source system's `MONAT` is *raw observation data*, admissible as a Source Object field, but the **authoritative platform fiscal_period** is a platform computation. Per the §2.1 test, "the platform computes this value at the metric evaluation boundary over grain, time, filter, and formula" — yes. **MCF.**

If a tenant's source system's `MONAT` disagrees with the platform's computed `fiscal_period`, the platform's computation is authoritative (Invariant I — meaning is evaluated at the canonical boundary, and the canonical boundary uses the platform's fiscal calendar resolution per D365). The source value is preserved as observation; it is not the authority.

**This is why fiscal_period belongs in MCF, not BCF.** A naive reading might place `fiscal_period` as a BCF characteristic of a Sales Order Line. That naive reading fails the §2.1 test because the authoritative value is computed, not stored.

### 2.7 Reference properties that look like metric inputs

Reverse edge case:

**`order_line.product`** — a reference property on `Order Line`. Looks like a metric input ("what product did this line sell"). Is it BCF or MCF?

Answer: **BCF**. It is a structural identity property of `Order Line` (per `business-concept-registry.md` §5 — reference properties are first-class BCF Business Concepts, addressable as `order_line.product`). MCF may *bind a variable* to `order_line.product` (e.g. "this metric is grouped by product"), but the property itself is BCF authoritative.

The principle: **structural identity is BCF's. Computation over structural identity is MCF's.**

### 2.8 Cross-framework coordination

Where BCF and MCF must coordinate (deferred to full plan for mechanics):

- When BCF authors a new BusinessConcept, MCF may want to know (e.g. to suggest new MCs that could bind to it). This is a notification concern, not a write coupling.
- When BCF supersedes a BusinessConcept (under the immutable-atom model for Characteristics, ADR DEC-26b6e2; under the standard supersession path for concepts), MCF's MCs that bound to the superseded BC may need re-authoring. This is a cross-framework supersession concern.
- When MCF authors a new MC referencing a BusinessConcept, BCF may want to track the consumer (the F5 read could surface "this BC is referenced by N MCs"). This is a read concern, not a write coupling.

The full plan specifies the mechanics. The sketch's working position: **no shared mutable state between BCF and MCF; coordination via events or pull-side reads, never via write coupling.**

---

## 3. Boundary with runtime and Foundation evaluation boundaries

### 3.1 MCF is upstream of the metric evaluation boundary

The metric evaluation boundary (per Foundation §The Evaluation Boundaries) reads the active Metric Contract at evaluation time and produces a Metric Snapshot. MCF authors the active Metric Contract. The two never touch directly: MCF writes governed grammar; the boundary reads governed grammar; they meet only at the read.

### 3.2 Reads do not trigger evaluation

Per Foundation boundary-independent rule: *"Reading a progression object, a Canonical Mapping, or a Contract does not cause a boundary act. Evaluation is explicitly invoked, not implicit in access."*

MCF reads (in the operator console, in the panel, in audit) never trigger metric evaluation. A diagnostic that re-runs evaluation to "fix" a metric snapshot value is a violation, not a fix.

### 3.3 The four boundaries reference active MCF grammar at evaluation time

MCF members are referenced by the metric evaluation boundary at evaluation time. MCF does not push to the boundary; the boundary reads active grammar when it evaluates. MCF is upstream; the chain is downstream; they meet only at the read.

### 3.4 MCF does not own runtime state

Specifically, MCF does not own:
- **Metric Snapshot rows** — produced by the metric evaluation boundary, immutable per Invariant III.
- **Evidence Objects** for metric evaluations — emitted at the boundary per Invariant VI.
- **Lineage Objects** for metric evaluations — emitted at the boundary per Invariant VI.
- **`mc_dependency` runtime tables** (per D316 readiness scheduler) — these are derived, not authored; MCF may consume them for readiness gating.
- **L-node semantic verdicts** (per D366) — these are evaluation-boundary verdicts about active MCs, not MCF authoring state.

MCF may *consume* runtime state for readiness gates and calibration — but it does not own or produce it.

### 3.5 The metric evaluation engine is preserved

Per ADR DEC-02f5a9 §5: *"Metric definitions / knowledge (the KPI catalog) — Survive as knowledge — only the binding to concepts is rebuilt."*

The metric evaluation engine (the runtime that reads active MCs and produces Metric Snapshots) is preserved. MCF re-authors the *bindings* an MC carries (variable bindings → BusinessConcepts; grain → Entity); it does not rewrite the engine.

What this means concretely: when MCF re-authors an MC against the BCF Registry, the new MC produces the same numeric value through the same engine. The MC body changes; the engine runs unchanged. This is the "fold-into-engine" principle from BCF re-authoring — the value is preserved across the re-authoring.

---

## 4. MCF identity model

### 4.1 Why identity must be structural

ADR DEC-02f5a9 §3 made BCF identity *structural, not detected*. Synonyms (many names, one meaning) are blocked by `UNIQUE(entity_id, property_id)`. Homonyms (one name, many meanings) are blocked by forced-distinct entity ids with distinct definitions. These are structural impossibilities, not gate-time detections.

The same discipline must apply to MCF. Without it, MCF will re-create the contamination BF/BO/CF showed: two MCs that compute the same thing under different names (synonym contamination), one MC name that means two things to two operators (homonym contamination).

### 4.2 Working hypothesis: MC structural identity

Proposed identity tuple for an active Metric Contract:

```
MC identity = (
  grain_entity,           -- typed reference to a Registry Entity (DEC-02f5a9 §1)
  formula_intent_hash,    -- structural hash of the formula AST (§7), not the rendered text
  variable_binding_set,   -- ordered or named set of (role, BusinessConcept) bindings
  temporal_gate_shape,    -- the temporal-evaluation shape (point-in-time, trailing window, as-of, period-end, etc.)
  filter_set              -- structural filter list, each filter expressed against BCF objects
)
UNIQUE(grain_entity, formula_intent_hash, variable_binding_set, temporal_gate_shape, filter_set)
  WHERE lifecycle_state = 'active' AND archived_at IS NULL
```

This is a **working hypothesis** for the full plan to refine. The claim it must support: two active MCs cannot have identical (grain, formula intent, variable bindings, temporal shape, filters) — i.e. they cannot mean the same thing. If they do, one is a synonym and the structural constraint rejects the second insert.

### 4.3 What the hypothesis blocks (working positions)

- **MC synonyms** — two MCs that compute the same value over the same grain with the same bindings and temporal shape, under different display names. Blocked by the UNIQUE constraint.
- **MC homonyms** — one display name covering two distinct identity tuples. Permitted at the display layer (operators may use the same display name for genuinely distinct metrics) but the *identity* surface forces the distinction to be explicit at authoring time.
- **Drift via free-text formula re-keying** — preventing two MCs from claiming the same identity by giving them subtly different formula text that hashes to a different `formula_intent_hash`. This is the analogue of BCF's "definition prose can vary; identity is the tuple" — formula prose can vary; identity is the AST structure.

### 4.4 What the hypothesis leaves open

- **The exact shape of `formula_intent_hash`** — what AST normalizations count as identity-preserving (e.g. is `A + B` the same identity as `B + A` for a commutative operator?). To be specified in the full plan, likely with an explicit normalization rule per operator.
- **The exact shape of `variable_binding_set`** — ordered vs named, how role labels participate in identity. Working position: ordered for positional binding (e.g. numerator / denominator), named for non-positional roles (e.g. filter inputs).
- **`temporal_gate_shape`** — must be a closed enum, not free text. Candidate values: `point_in_time`, `trailing_window(N)`, `as_of(timestamp)`, `period_end(grain_period_type)`. To be specified in the full plan.
- **`filter_set`** — how to canonicalize a set of structural filters into an identity-comparable form. The full plan must decide whether filter order participates in identity (working position: no — filters are set-semantic).
- **What changes are supersession vs. revision** — the analogue of BCF's identity-bearing vs. descriptive distinction. Working position (parallel to ADR DEC-26b6e2 for characteristics): changing any identity-tuple field is supersession to a new MC; adding a descriptive attribute (display name, owner, narrative) is a non-superseding revision. The full plan refines this.

### 4.5 Composite-grain edge cases

A metric whose grain is a composite Entity (e.g. `Inventory Position` with identity `(Material, Warehouse, Batch)`) has a grain that is itself structurally complex. The MC's `grain_entity` reference is to the composite Entity by id, not to the constituent identity-bearing properties separately. The MC inherits the composite Entity's identity discipline through the reference.

If the composite Entity is later superseded (per BCF supersession discipline — changing its identity-bearing property set creates a new Entity), every MC whose `grain_entity` referenced the old composite must be re-authored against the new composite (or explicitly retained as a historical MC on the superseded Entity). Cross-framework supersession concern, deferred to full plan.

### 4.6 Identity model is not detection

Restating for emphasis: the identity tuple is a **structural constraint**, not a panel-time check. The substrate enforces uniqueness at write time. The panel can advise; it cannot decide. Same discipline as BCF per ADR DEC-02f5a9 §3.

---

## 5. Metric intent vs. metric binding

This section is the load-bearing operational position for the Quarantine ADR's §11 boundary questions (see §12 below).

### 5.1 The two halves of a Metric Contract

Per ADR DEC-02f5a9 §5: *"Metric definitions / knowledge (the KPI catalog) — Survive as knowledge — only the binding to concepts is rebuilt."*

A Metric Contract has two distinguishable halves:

| Half | Examples | Disposition under quarantine |
|---|---|---|
| **Metric intent** (knowledge) | Display name, prose definition, business owner, threshold (target value), unit semantics (display unit), formula prose (what we want to compute, in English/math notation), source citation (e.g. "this is the standard DSO formula per industry practice"), references to operational SOPs, ownership domain | **Survives.** Per ADR §5 carve-out. Operator intent that the KPI catalog has accumulated for 1,819 metrics is preserved as knowledge. |
| **Metric binding** (BF/CF coupling) | The `metric_binding` rows that point at `business_field` ids; the `cc_field_mapping` rows that the metric chain currently resolves through; the `runtime.reader.business_object_id` that backs the canonical evaluation | **Discarded.** Quarantined. Re-authored against the BCF Registry. |

### 5.2 What "survives as knowledge" operationally means

The KPI catalog's metric *intent* (the survives-half) can be read by the MCF panel and by operators during MCF authoring **as background knowledge** — the same way an operator might consult an industry reference, an analyst report, or a working paper. It is **not citable as PE-MC-1 evidence** (see §11) — the panel cannot cite "KPI catalog row #4172" as the grounding for an MCF assertion the same way it might cite "OAGIS § 1.2.3" or "bc-seed metric entry uid:metric.dso".

The distinction:
- **Inspiration / background knowledge** — operator memory, KPI catalog prose definitions, narrative context. Not auditable as evidence; not citable in the publication-eligibility check.
- **Authoritative evidence** — PE-MC-1 sources (recognized external standards, bc-seed catalog entries with provenance lineage, source-system observations with verifiable alias, operator-authored bounded-domain definitions with explicit business justification). Auditable, citable, gate-checked.

The KPI catalog is *background knowledge* under MCF, not authoritative evidence. The MCF panel may consult it during authoring; the panel's PE-MC grounding may not cite it.

### 5.3 What "the binding is rebuilt" operationally means

The MC's variable bindings under MCF point at BCF Business Concept ids by id. There is no path through `business_field_id`, no path through `cc_field_mapping`, no path through `canonical_field`. The legacy binding chain is structurally replaced, not bridged.

If an old MC under the legacy chain bound to `business_field_id = X` (say, an `unit_price_amount` BF), and the BCF Registry now has a BusinessConcept `Sales Order Line · unit price (amount)` with id Y, MCF authoring **does not migrate** the binding from X to Y. MCF authors a *new* MC under the new identity discipline (§4), with bindings pointed at Y. The old MC remains physically present (operational continuity, per Quarantine ADR §4) until the metric chain is fully re-authored and the legacy retirement DBCP opens.

There is no `(old_mc_id, new_mc_id)` mapping table. There is no `(business_field_id, business_concept_id)` mapping table (per §12.4 below — explicit position for the Quarantine ADR).

### 5.4 The 1,819 KPIs as intent

The platform's KPI catalog contains ~1,819 KPIs across 18 functions (per MEMORY). Under MCF:

- The intent of each (display name, prose definition, owner, threshold) **survives** as background knowledge. MCF authoring sessions may consult it.
- The bindings of each are **discarded**. MCF re-authors each MC under the new identity discipline, against BCF Registry objects.
- The KPI catalog as a *list* is preserved (it tells us what we want to measure). The bindings the list points at are not.

The work to re-author 1,819 MCs is **MCF execution scope**, not Quarantine ADR scope. The Quarantine ADR only needs to lock the operational position: intent survives as knowledge, bindings are discarded. The execution timeline is the full plan + the eventual MCF UI MVP.

---

## 6. Variable binding to BCF

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
| **Time anchor** | A BCF BusinessConcept that carries a date or timestamp representation term (used as input to the fiscal calendar resolution per §8) | `Sales Order Line · posting date (date)` |

### 6.3 Bind-time compatibility checks

At bind time the substrate (or the authoring service) verifies:

1. **Existence** — the referenced BC id exists in the Registry and is `active` or `draft` (binding to `superseded` is rejected for active MCs; permitted for historical MC versions).
2. **Kind compatibility** — a value-kind binding role targets a value-kind BC; a reference-kind role targets a reference-kind BC.
3. **Representation term compatibility** — the variable's expected representation term (declared in the formula AST) is identical to or compatible with the BC's representation term (per the BCF representation-term closed set).
4. **Unit compatibility** — for value-kind bindings, the variable's expected unit semantics (currency / count / duration / etc.) is identical to or convertible to the BC's unit semantics. Conversion rules live in the OC/CC bodies (per ADR DEC-02f5a9 §2 "field-resolution logic survives"); MCF does not author conversion rules.
5. **Grain alignment** — the BC's home entity is reachable from the MC's grain entity via identity-bearing reference properties (per BCF identity-reference DAG, `business-concept-registry.md` §122-148). Bindings to BCs on entities unreachable from the grain are rejected. This is the structural shape of "the metric's grain must be coherent with its inputs."

### 6.4 What MCF does not do

MCF does **not**:
- Author resolution rules (type coercion, unit conversion, reduction-over-grain, temporal interpretation) — those live in OC/CC bodies per ADR DEC-02f5a9 §2.
- Author BCF artifacts — see §2.3 above.
- Read BF/BO/CF/CM rows during binding — see Quarantine working rule.
- Permit free-text binding ("bind variable X to a field called `unit_price`") — bindings are by BCF id only.

### 6.5 Grain as typed Entity reference (re-stated for emphasis)

Per ADR DEC-02f5a9 §1 and `business-concept-registry.md` §8:

> *"In MCF, grain therefore becomes a typed reference to a registry entity, not a free-text parameter — MCF cannot declare an incoherent grain."*

This is the load-bearing structural constraint that distinguishes MCF from the legacy metric chain. Legacy MCs declared grain as free text (e.g. `grain="invoice"`); the engine then tried to resolve "invoice" to a Business Object, sometimes succeeding, sometimes drifting. Under MCF, `grain_entity` is a Registry Entity id; resolution is unambiguous; "incoherent grain" is structurally impossible.

---

## 7. Formula AST as governed first-class artifact

### 7.1 Why an AST, not free text

Legacy MCs carried formulas as free-text strings (e.g. `"sum(NETPR) / count(distinct VBELN)"`). Free text is the failure mode BCF's `definition_standard` problem had: every consumer parses, interprets, and potentially mis-applies the text. Drift is silent. Inconsistency is undetectable.

Under MCF, the formula is a structured **abstract syntax tree** (AST):
- Authored as AST, not parsed from text.
- Validated against a closed set of operators.
- Type-checked against bound BCs at bind time.
- Identity-hashed for the MC identity tuple (§4.2).

The AST is the authoritative representation. A rendered text form may exist for display (`"SUM(unit_price) / COUNT(line_number)"`) but the AST is the structural truth. Two MCs with identical ASTs but different rendered text are the same MC; two MCs with different ASTs but identical rendered text are different MCs.

### 7.2 AST node taxonomy (working position; full plan refines)

Proposed initial node types:

| Node | Role |
|---|---|
| **`variable_ref`** | Reference to a bound MC variable (which points at a BCF BC). |
| **`literal`** | Constant value with explicit representation term and unit. |
| **`aggregate`** | `SUM`, `AVG`, `COUNT`, `COUNT_DISTINCT`, `MIN`, `MAX`, `MEDIAN`, `PERCENTILE(p)`. Operates over a set defined by grain + filters. |
| **`arithmetic`** | `+`, `-`, `*`, `/`, `MOD`. Type-checked operands. |
| **`comparison`** | `<`, `<=`, `=`, `>=`, `>`, `!=`. Returns boolean; usable in `CASE` or `filter`. |
| **`case`** | `CASE WHEN <comparison> THEN <expr> ELSE <expr> END`. Typed branches must agree. |
| **`window`** | `LAG`, `LEAD`, `MOVING_AVG(window)`. Window semantics specified by `temporal_gate_shape`. |
| **`time_anchor_resolution`** | Resolves a BC bound to `time_anchor` role to a fiscal period / fiscal year via the fiscal calendar resolver (per D364, D365). |

This is a sketch; the full plan specifies the complete set and the strict typing rules.

### 7.3 What the AST forbids

- **Arbitrary SQL** — no raw query embedding.
- **External function calls** — no `EXEC(...)` or external code invocation. The AST is closed.
- **Side effects** — no AST node may write state.
- **Free-text reference resolution** — no `"resolve('unit_price')"` operators; references are by BCF id only.
- **Implicit unit conversion** — type/unit must match at bind time, or the bind is rejected.
- **Aggregation outside grain** — every aggregate operates within the metric's grain; cross-grain aggregation is supersession to a new MC.

### 7.4 Formula immutability

Per Foundation Invariant III applied to MCs: an active MC's formula AST is immutable. Changing the AST is supersession to a new MC (per §4.4). The full plan specifies whether this triggers the MCF analogue of ADR DEC-26b6e2 (semantic-finality affirmation for some MC sub-element).

### 7.5 Formula intent hash

The `formula_intent_hash` in the MC identity tuple (§4.2) is a structural hash over the *normalized* AST. Normalization handles:
- Commutative operator ordering (working position: alphabetical operand order for commutative ops).
- Constant folding (working position: literals computed at AST-build time, not at hash time).
- Variable rename invariance (working position: variable bindings participate in identity through `variable_binding_set`, not through hash; renaming a variable in the AST without changing its BC binding preserves hash).

The full plan specifies the exact normalization.

---

## 8. Computed dimensions

### 8.1 Why computed dimensions belong to MCF

Per §2.6, fiscal_period is the canonical computed-dimension example. The general class:

A **computed dimension** is a value derived from observed values (or from grain coordinates) at the platform's canonical or metric evaluation boundary, not stored on the source. Examples:
- `fiscal_period` from `posting_date` × tenant fiscal calendar.
- `fiscal_year` from `posting_date` × tenant fiscal calendar.
- `calendar_quarter` from a date.
- `derived_grain` (e.g. "rolling 30-day window over Sales Order Line" — a derived grain from a base grain).
- `bucket_label` (e.g. "DSO bucket: 0-30, 30-60, 60-90, 90+" computed from a numeric value).

These are MCF concerns because:
- They are computed (per §2.1 test).
- They depend on governed configuration (the tenant fiscal calendar; the bucket boundaries) that has its own lifecycle.
- They are referenced by MC formulas (a metric grain `fiscal_period`; a metric filter `bucket_label = '0-30'`).

### 8.2 What MCF must specify (full plan)

For each computed dimension class:
- **Source**: the BCF input(s) the computation reads (e.g. fiscal_period reads `Sales Order Line · posting date (date)`).
- **Governing configuration**: the artifact that supplies the computation rules (e.g. `tenant.fiscal_calendar_config` per D364, owned by tenant onboarding).
- **Resolver service**: the runtime component that performs the computation (e.g. `FiscalCalendarService.resolve(posting_date)` per D364-D365).
- **Identity semantics**: how the computed dimension participates in MC identity (e.g. a `fiscal_period` filter on an MC is part of `filter_set` in the MC identity tuple).
- **Lifecycle interaction**: what happens to MCs that filter or grain on a computed dimension when the governing configuration is superseded (e.g. tenant changes fiscal calendar). Working position: MCs do not automatically re-evaluate; supersession of governing config triggers an audit of affected MCs.

### 8.3 The fiscal calendar stack (existing work, MCF absorbs)

D363, D364, D365 are existing-ADR work on fiscal calendar that MCF will absorb as a sub-discipline:

- **D363 (DEC-1efa47)** identified the grain-key-source mismatch (engine conflating business calendar period with engine runtime context). MCF's identity model (§4) and bind-time grain check (§6.3) make this class of mismatch structurally impossible.
- **D364 (DEC-d7e7a0)** locked the fiscal calendar stack: platform `date_dim` + per-entity tenant fiscal calendar config + optional `fiscal_period_boundary` + `FiscalCalendarService`. This stack is what MCF computed-dimension authoring consults for fiscal_period / fiscal_year derivation.
- **D365 (DEC-a8e8fc)** specified that CC declares `posting_date_field` and canonical resolution enriches payload. This is the *canonical-boundary* expression of fiscal resolution; MCF expresses the *metric-boundary* consumption (metric grain `fiscal_period`, metric filter `fiscal_year`, etc.).

The full plan formalizes how MCF consumes the existing fiscal stack without re-authoring it.

### 8.4 The MLS framework (existing work, MCF absorbs)

D389-D393 (Metric Lifecycle States) is existing-ADR work on the 25-step activation ladder for metrics. MCF will absorb it as the **MC lifecycle / readiness sub-discipline**:

- **D389 (DEC-c9e623)**: MLS framework — 25 steps; platform MLS 1-14, tenant MLS 15-25; state ledger schema; probe-vs-gate separation; cross-boundary code rule.
- **D390 (DEC-9d7a5c)**: MLS failure vocabulary.
- **D391 (DEC-b8b825)**: MLS-14 gate.
- **D392 (DEC-e7b7b3)**: MLS substrate — `metric.mls_state` ledger + event log + trigger binding + queue recorder.
- **D393 (DEC-29f134)**: Runtime drift detection — admission probe + S3 quarantine + ticket service.

MLS today is implemented as standalone ADRs without an MCF home. Under MCF, MLS becomes the lifecycle-overlay for the MC: platform MLS 1-14 governs MC authoring readiness (Framework Approval gates), tenant MLS 15-25 governs MC binding readiness for a specific tenant. The MCF full plan specifies the integration; the sketch's position is that MLS becomes a first-class MCF concern, not a parallel framework.

---

## 9. MCF authority model

### 9.1 Mirror of BCF Framework Approval (D411)

MCF authority follows the BCF pattern established by ADR DEC-149ab2 / D411. Within MCF scope:

- **AI consensus constitutes Framework Approval.** AI proposes, prepares, and approves MCF members through the framework lifecycle under policy.
- **Operator override is the exception path.** Operator approval remains the sole authority for everything outside MCF scope.
- **Framework Approval requires, for every framework write**:
  1. Three-model consensus with closed-enum verdict.
  2. Same-input-snapshot rule.
  3. No-fabrication grounding check pass (per PE-MC-1, §11).
  4. Immutable authoring record with the full NF1 field set.
  5. Calibration sampling enrollment recorded.
  6. Active operator override mechanism.

### 9.2 Three immutable MCF rules (adopted from BCF, adapted)

| Rule | Statement |
|---|---|
| **Rule 1 — Framework Approval discipline** | Every MCF write requires the six discipline conditions above. Any failure routes to operator review. |
| **Rule 2 — Operator override always available** | At every MCF lifecycle state, the operator may override the AI's decision (edit non-active versions; supersede active versions). The override path cannot be disabled, suppressed, or circumvented. |
| **Rule 3 — Non-bypassable authoring-record trail** | Every MCF act is preserved as an immutable authoring record. No MCF write may occur without a corresponding record. |

### 9.3 The Metric Authoring Panel (working position)

Analogous to the BCF B6 Context Authoring Panel. Working position:

- **Three-model consensus** with closed-enum verdicts (`APPROVE_FOR_DRAFT`, `OPERATOR_REVIEW`, `REJECT_<defect_code>`).
- **No-fabrication grounding check** — every claim traces to a PE-MC-1 evidence source (§11).
- **Closed-enum verdict codes** including MC-specific defects (e.g. `MC_DEFECT_GRAIN_INCOHERENT`, `MC_DEFECT_VARIABLE_UNBINDABLE`, `MC_DEFECT_FORMULA_TYPE_MISMATCH`).
- **Same panel discipline as BCF**: panel run uid, prompt version, model identity per agent, input hash, per-agent outputs, verdict, grounding check result, policy version. All immutable per Invariant V.

The full plan specifies the panel mechanics (prompts, model selection, calibration). The sketch's position is that MCF inherits BCF's panel pattern wholesale and adds MC-specific checks.

### 9.4 Operator confirm for high-risk MCF actions

Analogous to BCF's C5-HR (high-risk operator-confirm extension; ADR DEC-149ab2 §HR). Working position: the following MCF actions are high-risk and require operator confirm with ≥40-char rationale:

- **`metric_transition`** — publishing an MC from `draft` to `active` (analogous to BCF B10 publication).
- **`metric_supersede`** — superseding an active MC with a new MC under a different identity (per §4.4).
- **Cross-framework supersession ripple** — superseding a BCF BusinessConcept that has bound MCs requires operator confirm on the MCF side for each affected MC (mechanics deferred to full plan).

### 9.5 Cert-backed authority

Mirror of BCF's `certification_record`-backed authority. Every governed MCF action emits a certification record (the same `contract.certification_record` table can be reused with new `action_code` values such as `metric_create`, `metric_transition`, `metric_supersede` — or MCF gets its own table; full plan decides).

The principle (already proven in BCF UI-S5): **lifecycle state is display only; the certification record is the authority.** An MC is "published" because its `metric_transition` cert exists with `from='draft'`, `to='active'`, operator-confirm rationale, panel_run_uid linked — not because some field says `lifecycle_state='active'`.

---

## 10. Lifecycle

### 10.1 Five states only

Per Foundation Contract Grammar §Lifecycle and as adopted by BCF:

```
draft → review → approved → active → superseded
```

MCF introduces no states beyond these five. The MLS framework (§8.4) is a *readiness overlay* on top of the lifecycle — it tells you whether an `active` MC is runtime-ready in a tenant; it does not introduce new contract-grammar states.

### 10.2 AI-by-default lifecycle progression

For every MCF write:
- `intake → draft` — AI executes by default after Metric Authoring Panel `APPROVE_FOR_DRAFT`.
- `draft → review` — AI executes by default after MC envelope completeness check.
- `review → approved` — AI executes by default after Metric Publication Panel `APPROVE` + PE-MC-1..PE-MC-N deterministic publication gate pass.
- `approved → active` — AI executes by default under Framework Approval **or** operator confirm for high-risk transitions (§9.4).
- `active → superseded` — operator-driven supersession with explicit successor pointer.

### 10.3 Immutable-active discipline (Invariant III)

Active MCs are immutable. Operator override of an active MC = operator authors a superseding new MC (per §4.4 — supersession discipline rooted in the identity tuple).

### 10.4 Possible MCF analogue of ADR DEC-26b6e2 (open question)

ADR DEC-26b6e2 established that Characteristics are immutable atoms (no version; supersession-only correction; operator semantic-finality affirmation at publication).

**Open question**: which MCF sub-artifact, if any, needs the same atom-level immutability?

Candidates considered:

- **Formula AST** — strongest candidate. The formula is the meaning-bearing core of an MC; "editing the formula" is semantically equivalent to "minting a new metric." A semantic-finality affirmation at publication would force the operator to explicitly affirm the formula's published meaning.
- **Variable binding set** — strong candidate. Re-binding a variable is semantically equivalent to creating a new MC.
- **Grain** — strong candidate. Changing grain redefines the metric entirely.
- **Temporal gate shape** — weaker candidate; changes here may sometimes be additive (e.g. extending a trailing window).
- **Filter set** — weakest; filter additions are often legitimate refinements.

**Sketch working position**: the identity tuple (§4.2) carries the immutability. Any change to grain / formula intent / variable bindings / temporal gate shape / filter set is supersession to a new MC, parallel to characteristic supersession. **Whether MCF additionally adopts a publication-time semantic-finality affirmation analogous to ADR DEC-26b6e2 is an open question for the full plan.** The case for it is strongest when the MC is the source of an action (an Intervention Contract trigger) — at that point the metric's interpretation is downstream-load-bearing in a way analogous to a characteristic's term being immutable.

### 10.5 The metric-side analogue of the supersession safety-net

ADR DEC-26b6e2 established `characteristic_supersession` as the safety-net for the immutable-atom model. The MCF analogue: `metric_supersession`, with `predecessor_mc_id`, `successor_mc_id`, `correction_class` (editorial vs meaning-bearing — same distinction as characteristic supersession), `operator_sub`, `rationale`, panel_run_uid, etc. Substrate work deferred to full plan.

### 10.6 Tenant-side lifecycle (binding-binding)

Distinct from MC lifecycle: the lifecycle of a *tenant's binding to* an active MC. An active MC may be readiness-ready for tenant A and not for tenant B. The MLS framework (§8.4) is the binding lifecycle: platform MLS 1-14 is "is this MC governed?", tenant MLS 15-25 is "is this MC operational for this tenant?". Full plan specifies the substrate.

---

## 11. MC publication eligibility contract (PE-MC)

Analogue of BCF's PE1-PE6 publication eligibility, adapted for metric semantics. A Metric Contract is eligible for publication to `active` if and only if it satisfies all of:

### PE-MC-1. Provenance (no-fabrication)

Every claim in the MC traces to a recognized evidence source:
- (a) a **recognized external standard** with verifiable citation (e.g. GAAP, IFRS, XBRL, an industry methodology like Toyota's lean operations, an academic source);
- (b) a **bc-seed catalog entry** with verified provenance lineage (e.g. a bc-seed metric entry like `metric.dso` with documented origin);
- (c) an **operator-authored bounded-domain definition** with explicit business justification (e.g. a BareCount-internal metric where the operator declares "this is our methodology and the justification is X");
- (d) a **source-system observation** with verifiable alias — **provisional**, subject to operator-confirm until the sufficiency question is settled (mirrors BCF's PE1 open question).

**Explicitly NOT a PE-MC-1 source**: BF/BO/CF/CM rows (per Quarantine working rule). The legacy KPI catalog *as intent* is background knowledge per §5.2, **not citable as PE-MC-1 evidence**.

### PE-MC-2. Grain coherence

The MC's `grain_entity` resolves to a Registry Entity. Every variable binding's target BC is reachable from the grain entity via identity-bearing reference properties (per §6.3 check 5). Grain incoherence is blocked at PE-MC-2.

### PE-MC-3. Binding completeness

Every variable position in the formula AST is bound to a BCF BusinessConcept (or, for grain, a BCF Entity). Unbound variables fail PE-MC-3.

### PE-MC-4. Type and unit coherence

Every binding passes the §6.3 bind-time compatibility checks (existence, kind, representation term, unit, grain alignment). Failures fail PE-MC-4.

### PE-MC-5. Formula AST validity

The formula AST contains only nodes from the closed taxonomy (§7.2). No free text. No external function calls. No side effects. Type checking succeeds across the AST. Failures fail PE-MC-5.

### PE-MC-6. Temporal gate well-formedness

The `temporal_gate_shape` is from the closed enum (§4.4). For shapes that require a time-anchor variable, the binding exists and resolves through the fiscal calendar (§8.3). For shapes that require a window, the window parameter is present and valid.

### PE-MC-7. Computed-dimension coherence

For each filter or grain that uses a computed dimension (e.g. `fiscal_period`), the governing configuration is named (e.g. `tenant.fiscal_calendar_config`) and exists in active state at the metric's intended evaluation context.

### PE-MC-8. Runtime-readiness intent

The MC declares its intended runtime-readiness profile (a forward declaration for the MLS framework to act on per §8.4 — what data the MC expects to be available, what gates it expects to pass for a tenant binding). This is intent, not yet runtime check; MLS substrate enforces the actual readiness check at tenant binding time.

### PE-MC-9. Definition discipline

Definition declares what the metric IS, not why it matters. Business intent in a separate field. Definitions unique per MC identity (no two MCs may have identical definitions for distinct identity tuples).

### No-fabrication rule

AI cannot invent citations, formulas, variable bindings, or content not traceable to a PE-MC-1 source. Outputs failing the no-fabrication check are quarantined as invalid, preserved for calibration.

### Inconsistency intolerance

Validated on every write. Examples of intolerable states:
- `temporal_gate_shape = 'trailing_window(30)'` + no time-anchor binding.
- Variable binding to a `superseded` BC on an `active` MC (without explicit historical-MC carve-out).
- Formula AST contains an `aggregate` node whose grain disagrees with the MC's `grain_entity`.
- Two `active` MCs with identical identity tuples (blocked at the substrate, but PE-MC ensures the panel doesn't try).

### Open questions for PE-MC (to be specified in full plan)

- Whether PE-MC-1 (d) (operator-authored bounded-domain definitions) requires explicit operator-confirm at publication, like BCF PE1.
- Whether PE-MC-7 (computed-dimension coherence) needs sub-rules for cross-tenant-calendar metrics.
- Whether PE-MC-8 (runtime-readiness intent) is publication-blocking or publication-deferred (i.e. MC can be `active` without being runtime-ready in any tenant).

---

## 12. Boundary questions for the future Quarantine ADR — working positions

This section answers the precision-relevant questions the Legacy Vocabulary Stack Quarantine ADR will need. These are working positions — the ADR itself should adopt them or amend them when written, but the sketch records the MCF-side answers so the ADR doesn't have to re-derive them.

### 12.1 What does "operational continuity" mean during phased cutover?

**Working position: continuity is one-direction.** The existing legacy chain (`canonical_contract` → `cc_field_mapping` → BF/BO/CF) continues to resolve at runtime for tenants who bound to it under the legacy regime. MCF re-authoring produces new MCs that bind to BCF objects; the new MCs run on the same metric evaluation engine alongside the legacy MCs. There is no shared state, no migration, no bridge. A tenant whose MCs are all re-authored is fully on MCF; a tenant whose MCs are mixed has each MC resolve independently through whichever binding chain its specific MC carries.

**Operational continuity is NOT**:
- new adapter code that reads BF/BO/CF
- new sync between legacy and MCF
- shared lookup tables
- name-resolution shims
- "make legacy easier to use" improvements

**Operational continuity IS**:
- existing rows continue to resolve as they always did
- no new code that touches BF/BO/CF beyond bug-fix maintenance
- existing services keep running unchanged

### 12.2 End condition for legacy cutover — binary or mixed-state?

**Working position: mixed-state-permitted during cutover; binary at end.**

During the MCF re-authoring program, the platform runs both chains:
- Tenants A, B with all-MCF MCs: fully on MCF.
- Tenant C with half-MCF, half-legacy MCs: mixed; each MC resolves through its own binding.
- Tenants D, E with all-legacy MCs: fully on legacy.

This mixed state is permitted and operationally normal during cutover. The Quarantine ADR's "no shared state" rule still holds: each MC carries its own binding chain; no MC mixes BCF and legacy in its own body.

**End condition (the binary moment)**: when no `active` MC anywhere in the platform binds to a quarantined surface (BF/BO/CF/CM). At that point the physical disposition DBCP opens: drop / archive / freeze the quarantined tables. The end condition is the *single trigger* for that DBCP.

Working test for "end reached":
```
SELECT COUNT(*) FROM contract.metric_binding
  WHERE business_field_id IS NOT NULL
  AND mc IN (SELECT contract_id FROM contract.metric_contract WHERE lifecycle_state = 'active')
  = 0
AND analogous queries for cc_field_mapping, observation_field_map, runtime.reader.business_object_id.
```

(Schema names approximate; the full plan specifies the exact test.)

### 12.3 One-time reads from preserved-knowledge surfaces — permitted or not?

**Working position: permitted for KPI catalog as background knowledge; not permitted as PE-MC-1 evidence.**

The MCF Metric Authoring Panel may consult the legacy KPI catalog's *intent* fields (display name, prose definition, owner, threshold, formula prose, references) as **background knowledge** during authoring. This is operator-equivalent: an operator authoring an MC for "DSO" remembers the legacy KPI catalog had a DSO entry; they consult it the way they might consult an industry reference.

**But** the panel's PE-MC-1 grounding citations may not cite KPI catalog rows. The grounding must trace to an authorized PE-MC-1 source (recognized external standard, bc-seed entry, operator-authored bounded-domain definition, source-system observation). KPI catalog rows are background reading, not authoritative evidence.

This distinction makes the Quarantine ADR's PE-MC-1 prohibition tractable: the prohibition is on the *evidence trace*, not on background reading. The substrate-level guardrail (bc-qa rule to flag imports from `contract.business_field` / `contract.business_object` / `contract.canonical_field` / `contract.cc_field_mapping`) catches the contamination vector; the KPI catalog (a separate logical surface — `contract.metric_definition`, `contract.metric_definition_knowledge`) is not affected.

### 12.4 Exact quarantine scope of legacy tables

**Working position: in-scope vs. carve-out per table.**

| Schema.Table | Quarantine status | Rationale |
|---|---|---|
| `contract.business_field` | **In quarantine** | BF identity layer — contaminated |
| `contract.business_object` | **In quarantine** | BO identity layer — contaminated |
| `contract.business_object_field` | **In quarantine** | BO/BF composition; quarantined by transitivity |
| `contract.business_object_relation` | **In quarantine** | BO/BO relations; quarantined by transitivity |
| `contract.business_field_alias` | **In quarantine** | BF alias layer; quarantined by transitivity |
| `contract.canonical_field` | **In quarantine** | CF identity layer — contaminated |
| `contract.cc_field_mapping` | **In quarantine** | The BF↔CF mapping layer that ADR DEC-02f5a9 eliminated |
| `contract.observation_field_map` | **In quarantine on the BF reference side**; the OC binding act survives (per ADR §5 OC family survives) | OC-side binding to BF is quarantined; the OC family itself is not |
| `contract.canonical_contract` (existing rows with BF/CF bindings) | **In quarantine on the bindings**; CC family + body resolution-rule content survives (per ADR §2, §5) | Legacy CCs are discardable as binding artifacts; body content re-authored under MCF re-binding |
| `contract.metric_contract` (existing rows with `metric_binding` to BFs) | **In quarantine on the bindings**; MC family + intent/knowledge survives (per ADR §5) | Legacy MCs discardable as binding artifacts; intent re-bound under MCF |
| `contract.metric_binding` | **In quarantine** | The binding artifacts MCF rebuilds against BCF |
| `contract.metric_definition` | **Carve-out — preserved as knowledge** | KPI intent; ADR §5 "Survive as knowledge" |
| `contract.metric_definition_knowledge` | **Carve-out — preserved as knowledge** | KPI intent metadata |
| `runtime.reader.business_object_id` | **In quarantine on the column**; the `runtime.reader` table itself survives | Reader column references the quarantined BO; the reader runtime survives, the BO link is the quarantine surface |
| `contract.bc_seed_*` (bc-seed catalog) | **Carve-out — PE-MC-1 evidence source** | ADR §5; PE-MC-1 (b) |
| `contract.source_contract`, `contract.admission_contract`, `contract.observation_contract` (family-level) | **Carve-out — families survive** | ADR §5 |
| `contract.tenant.fiscal_calendar_config` | **Carve-out — not part of the legacy semantic stack** | D364 fiscal calendar stack; not BF/BO/CF |

The Quarantine ADR should adopt this table or amend it with rationale.

### 12.5 Metric intent vs binding separation — operative form

Per §5 above. The Quarantine ADR's §3 operative prohibitions should adopt the §5.2/§5.3 working positions verbatim:

- KPI catalog (intent) is background knowledge; survives; non-citable as PE-MC-1 evidence.
- Bindings (BF/CF/CM/legacy metric_binding) are quarantined; not migratable; replaced greenfield.
- No mapping table is created (no `(old_mc_id, new_mc_id)`; no `(business_field_id, business_concept_id)`).

### 12.6 Summary table for the Quarantine ADR §3 operative prohibitions

Working position the ADR should adopt:

| MCF/BCF authoring activity | Permitted | Notes |
|---|---|---|
| Read `contract.business_field` rows from any BCF/MCF authoring code | **No** | Quarantine violation; bc-qa rule flags imports |
| Read `contract.business_object` rows from any BCF/MCF authoring code | **No** | Same |
| Read `contract.canonical_field` rows from any BCF/MCF authoring code | **No** | Same |
| Read `contract.cc_field_mapping` rows from any BCF/MCF authoring code | **No** | Same |
| Read `contract.metric_definition` rows (KPI catalog intent) as background knowledge during MCF authoring | **Yes, with discipline** | Not citable as PE-MC-1 evidence; operator-consultable; substrate read permitted |
| Read `contract.bc_seed_*` rows as PE-MC-1 evidence source | **Yes** | ADR §5 carve-out; PE-MC-1 (b) authorized |
| Read `runtime.reader` rows that reference `business_object_id` as part of evaluating chain status | **Yes** | The chain-status SSOT (DEC-bebaec) is a read concern, not an authoring concern |
| Create a `(business_field_id, business_concept_id)` mapping table | **No** | Identity layer eliminated; the table re-introduces it |
| Create lineage edges from legacy MCs to MCF MCs | **No** | No migration; greenfield re-author |
| Create a name-resolution shim that resolves legacy MC names to MCF MC ids | **No** | ADR DEC-02f5a9 §4 "shim is the corruption preserved, not a fix" |
| Author new BF/BO/CF rows from any BCF/MCF authoring code | **No** | Per ADR DEC-65dc86 §7 "maintenance fixes only" on BF/BO surfaces; extend to substrate |

---

## 13. Inheritance from BCF

MCF inherits the following from BCF; the full plan does **not** re-derive any of these unless an MCF-specific reason emerges.

### 13.1 Authority model

- Framework Approval (ADR DEC-149ab2 / D411).
- AI-by-default; operator override as exception.
- Three immutable rules (Framework Approval discipline, always-available operator override, non-bypassable authoring-record trail).

### 13.2 Panel pattern (B6)

- Three-model consensus with closed-enum verdicts.
- Same-input-snapshot rule.
- No-fabrication grounding check.
- Immutable panel output records.
- Calibration sampling enrollment.
- Three-vendor model identity per panel run (maker / checker / moderator).

### 13.3 Lifecycle

- Foundation five states (`draft → review → approved → active → superseded`).
- Immutable-active discipline (Invariant III).
- Supersession-only correction for active members.
- No new states beyond the five.

### 13.4 Publication path (B10)

- Two-phase request → operator confirm.
- High-risk lock for `metric_transition` (analogous to `registry_transition`).
- Fork-ii idempotent resume on duplicate cert.
- Server-resolved evidence (no client-supplied panel_run_uid).
- Cert-backed authority (the cert is the publication authority, not the lifecycle state).

### 13.5 Operator console UI pattern (UI-S1..S5)

- Single-session request → review → confirm flow.
- Step A evidence bundle re-render.
- Step B operator rationale with ≥40 char floor.
- Step C semantic-finality affirmation (if MCF adopts the §10.4 analogue).
- Phase 1 skip on already-published.
- Shared loading/error/empty primitives.
- A11y on publish flow.
- Read-only verification journey before write gates.

### 13.6 Cert-backed authority discipline

- The publication cert is the authority; lifecycle state is display only.
- Operator-confirm block stored on cert.
- Operator sub from authenticated JWT, never client-supplied.
- Rationale verbatim on cert.

### 13.7 Substrate discipline

- Anti-synonym partial unique constraint on identity tuple (analogue of BCF's `UNIQUE(entity_id, characteristic_id) WHERE kind='value' AND lifecycle_state='active' AND archived_at IS NULL`).
- Meaning immutability `BEFORE UPDATE` trigger (analogue of BCF's meaning-columns immutability).
- Active-version-required check.
- Supersession table with `predecessor → successor` + correction_class + operator confirm.

### 13.8 Evidence framework

- Vocabulary Evidence Framework + Admission Checklist pattern (BCF's `business-concept-registry-vocabulary-evidence-framework.md`) — adapted to metric authoring (Formula Evidence Framework + MC Admission Checklist).

### 13.9 What MCF does NOT inherit

- BCF's PE1-PE6 verbatim — MCF has its own PE-MC-1..PE-MC-9 (§11). The discipline is the same; the checks are MC-specific.
- BCF's three scopes (BF/BO, CF, BF↔CF) — these are BCF's own scopes; MCF's scope is the MC and its surrounding artifacts.
- ADR DEC-26b6e2 verbatim — whether MCF adopts a publication-time semantic-finality affirmation is an open question per §10.4.

---

## 14. Non-goals

This sketch does NOT specify:

- **Substrate DBCP** — what tables MCF needs, what columns, what indexes, what triggers. Full plan content.
- **Panel implementation** — the actual prompts, model selection, calibration sampling rate, defect-code taxonomy. Full plan content.
- **Publication path implementation** — the actual API endpoints, request/response shapes, Fork-ii mechanics. Full plan content.
- **UI implementation** — the operator console for MCF. Mirror of BCF UI-S1..S5 arc; full plan content.
- **BF/BO/CF migration** — there is no migration; greenfield re-author per ADR DEC-02f5a9 §4. Non-goal of MCF entirely.
- **Legacy bridge** — there is no bridge; no shim; no compatibility wrapper. Non-goal entirely.
- **Re-implementation of the metric evaluation engine** — preserved per ADR DEC-02f5a9 §5; MCF re-authors bindings only.
- **Re-implementation of the fiscal calendar stack** — preserved per D364; MCF consumes the existing stack as a sub-discipline.
- **Re-implementation of MLS** — preserved per D389-D393; MCF absorbs MLS as the MC readiness-overlay sub-discipline.
- **Re-implementation of chain status SSOT** — preserved per DEC-bebaec; MCF reads it for readiness gating.

---

## 15. Open questions and "to be specified in full plan" markers

Items the sketch surfaces but does not resolve. Each becomes a section in the full MCF requirements doc.

### 15.1 Identity model

- **Q1 — Formula intent hash normalization.** What AST normalizations preserve identity? Working position: alphabetical commutative ordering + constant folding + variable-rename invariance. Full plan settles the exact normalization rules per operator class.
- **Q2 — Variable binding set ordering.** Ordered for positional bindings (numerator/denominator); named for non-positional (filter inputs). Full plan settles role-label vocabulary.
- **Q3 — Temporal gate shape enum.** Candidate values listed (§4.4); full plan settles the closed set and the per-shape required parameters.
- **Q4 — Filter set canonicalization.** Working position: filters are set-semantic (order does not participate in identity). Full plan settles the canonicalization rule.
- **Q5 — Supersession boundary.** Working position parallel to BCF: changing any identity-tuple field is supersession; descriptive changes are revisions. Full plan settles the per-field rule.

### 15.2 Formula AST

- **Q6 — Closed operator set.** Initial list in §7.2; full plan settles the complete taxonomy and per-node strict typing rules.
- **Q7 — Window semantics.** How `temporal_gate_shape = 'trailing_window(N)'` interacts with `window` AST nodes. Full plan specifies.
- **Q8 — Cross-grain aggregation prohibition.** Working position: forbidden — aggregation outside grain is supersession to a new MC. Full plan specifies the exact rule (e.g. how a metric over `Order Line` aggregates to `Sales Order` for a derived metric).

### 15.3 Variable binding to BCF

- **Q9 — Reachability check.** §6.3 check 5 requires the bound BC be reachable from the grain entity via identity-bearing reference properties. Full plan specifies the reachability algorithm (DFS over the identity-reference DAG; depth limit; cycle detection — though the DAG is acyclic per `business-concept-registry.md` §122-148).
- **Q10 — Unit conversion at bind time.** Working position: unit must match at bind time, or the bind is rejected; conversion is the OC/CC body's responsibility. Full plan settles edge cases (e.g. currency conversion, time-unit conversion).
- **Q11 — Bind to draft BCs.** Working position: an `active` MC cannot bind to a `draft` BC. A `draft` MC may bind to a `draft` BC; both must reach `active` together (publication ordering). Full plan specifies.

### 15.4 Computed dimensions

- **Q12 — Computed dimension taxonomy.** Initial list in §8.1 (fiscal_period, fiscal_year, calendar_quarter, derived_grain, bucket_label). Full plan enumerates the closed set MCF supports, with per-dimension governing config / resolver / identity semantics.
- **Q13 — Tenant-specific computed dimensions.** Working position: tenant-specific computed dimensions (e.g. tenant-specific fiscal calendar via D364 `tenant.fiscal_calendar_config`) are governed at the tenant config layer; MCF MCs reference the computed dimension generically (e.g. `fiscal_period`), and the tenant binding resolves through the tenant's specific config. Full plan specifies the cross-tenant compatibility.
- **Q14 — Custom computed dimensions per tenant.** Whether tenants can author their own custom computed dimensions beyond the platform-supported set. Working position: no, in the MVP; tenant customization is via configuration of platform-supported dimensions, not via author-your-own. Full plan revisits.

### 15.5 Authority model

- **Q15 — MCF panel prompts / model selection.** The B6 panel uses three models (Gemini / GPT / Claude). MCF panel may use the same trio or specialize. Full plan specifies.
- **Q16 — Calibration sampling rate.** BCF samples for calibration at some rate. MCF rate may differ given the differing failure modes of metric vs vocabulary work. Full plan specifies.
- **Q17 — Operator-confirm rule policy.** Which MCF actions trigger operator-confirm vs. AI auto-approve. Working position in §9.4 names three high-risk actions. Full plan settles the complete operator-confirm rule set (analogous to BCF's `operator_confirm_rule` table).

### 15.6 Lifecycle

- **Q18 — MCF analogue of ADR DEC-26b6e2.** Whether MC publication requires an operator semantic-finality affirmation for some MC sub-element (formula AST? grain commitment?). Sketch working position §10.4 leaves open; full plan decides.
- **Q19 — Cross-framework supersession.** When BCF supersedes a BusinessConcept, what happens to bound MCs? Working position: MCs are notified via cross-framework event; affected MCs enter a "supersession-pending" sub-state; operator confirms whether to re-author each MC against the successor BC or to retain as a historical MC on the superseded BC. Full plan specifies the mechanics and the substrate.
- **Q20 — Tenant binding lifecycle.** MLS 15-25 governs tenant binding readiness. Full plan integrates MLS into MCF's substrate (per §8.4) and specifies the tenant-binding artifact (whether it lives in MCF or in a tenant-binding sibling).

### 15.7 Publication eligibility (PE-MC)

- **Q21 — PE-MC-1 (d) operator-authored definitions.** Whether bounded-domain operator-authored definitions require explicit operator-confirm at publication. Mirrors BCF's PE1 open question.
- **Q22 — PE-MC-7 cross-tenant calendar metrics.** Whether MCs that span tenants with different fiscal calendars need a special PE-MC sub-rule.
- **Q23 — PE-MC-8 runtime-readiness.** Whether runtime-readiness intent is publication-blocking (MC cannot reach `active` until at least one tenant binding can fulfill it) or publication-deferred (MC reaches `active` based on its own form; tenant bindings handle runtime-readiness separately). Working position: publication-deferred. Full plan revisits.

### 15.8 Boundary with BCF

- **Q24 — Cross-framework coordination mechanics.** §2.8 sketches events / pull-side reads. Full plan specifies (event bus? polling? subscription model?).
- **Q25 — BCF notification of MC supersession.** When MCF supersedes an MC that bound to a BC, does BCF need to know? Working position: yes, for consumer-count reads in BCF UI. Full plan specifies.
- **Q26 — Reference-property bind shapes.** §6.2 names reference-kind variable bindings. Full plan specifies the exact reference-binding semantics (does the MC operate on the reference target's entity, or on the reference itself as a join column?).

### 15.9 Quarantine ADR coordination

- **Q27 — bc-qa rule mechanics.** §12.6 names the rule (flag imports from BF/BO/CF/CM in BCF/MCF authoring paths). Quarantine ADR + bc-qa work together; full plan specifies which file path patterns the rule covers.
- **Q28 — PE evidence-trace check enforcement.** §12.3 says the panel grounding cannot cite quarantined surfaces. Full plan specifies the substrate-level check (e.g. citation URIs validated against an allow-list at publication gate).

### 15.10 Substrate

- **Q29 — MC substrate table design.** Full plan + later DBCP.
- **Q30 — `metric_supersession` table.** Analogue of `characteristic_supersession`. Full plan + later DBCP.
- **Q31 — `mc_dependency` integration.** D316 readiness scheduler. Full plan specifies how MCF authoring interacts with the existing `mc_dependency` table.
- **Q32 — Cert table reuse vs new.** Whether MCF reuses `contract.certification_record` with new `action_code` values (`metric_create`, `metric_transition`, `metric_supersede`) or gets its own table. Working position: reuse; minimizes substrate churn. Full plan decides.

### 15.11 UI

- **Q33 — MCF operator console.** Full mirror of BCF UI-S1..S5 arc as a separate program of work.

---

## Status

`proposed` — sketch awaiting expansion into the full MCF requirements doc.

This sketch grounds the Legacy Vocabulary Stack Quarantine ADR by providing concrete working positions on §12 boundary questions. The Quarantine ADR can now adopt those positions (or amend them with explicit rationale). The Greenfield BCF Enrichment Plan sketch can adopt §2's BCF/MCF boundary as its forward constraint. The full MCF requirements doc takes this sketch as its skeleton and fills in §15 open questions.

**Next gates (sequenced per operator's earlier decision)**:

1. **Greenfield BCF Enrichment Plan sketch** — 1-2 days, docs only, smaller artifact, references §2 of this sketch for the BCF↔MCF boundary it must respect.
2. **Legacy Vocabulary Stack Quarantine ADR** — decided/accepted, grounded in this sketch's §12 working positions.
3. **Full MCF requirements doc + Full Greenfield BCF Plan** — parallel, after the Quarantine ADR locks the operational rules.
