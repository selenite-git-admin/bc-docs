---
uid: business-concept-registry-greenfield-enrichment-plan-sketch
title: Business Concept Registry — Greenfield Enrichment Plan (sketch)
description: Operational sketch for greenfield BCF vocabulary enrichment after the BCF backend + operator console MVP. Defines the forcing function (the first MCF re-author target), the authoring path (re-affirms B6 panel + C5 confirm + B10 publication + UI-S1..S5 + ADR DEC-26b6e2), evidence sources (PE1 only — explicit BF/BO/CF/CM prohibition), the route-to-MCF drift-prevention test, the composite-entity substrate prerequisite, target-boxed enrichment cadence, and the first enrichment unit's concrete candidate list. Sales-first domain prioritization extending from the Sales Order Line foothold. Companion to MCF requirements sketch. Status proposed.
status: proposed
date: 2026-05-24
project: bc-docs
domain: contracts
subdomain: catalog
focus: enrichment
---

# Business Concept Registry — Greenfield Enrichment Plan (sketch)

## 1. Scope and grounding

This sketch is the operational companion to the MCF Foundation Requirements sketch
(`metric-context-framework-requirements-sketch.md`, commit `a967970`). The MCF sketch
defined the boundary between BCF (stored business meaning) and MCF (computed metric
meaning) and named, in MCF §2.3, the rule that *"if an MC requires a BusinessConcept that
does not yet exist in the Registry, the authoring path is: (1) operator routes the
candidate to BCF for authoring through the B6 panel"*. **This sketch defines the BCF half
of that handshake** — how greenfield vocabulary enrichment proceeds, from what evidence,
in what order, under what authoring gates, and how to avoid drifting into MCF/computed
territory.

It is a **sketch**, not a full plan. It is operationally actionable for the next two or
three enrichment units; everything beyond that is named as "to be specified in full plan"
(§11). It is short by design — the heavy lifting on identity, lifecycle, authority, and
publication discipline is already done in:

- **ADR DEC-02f5a9** (Business Concept Registry adoption; greenfield rebuild; cleavage
  plane) — the governing architectural decision this sketch sits under.
- **ADR DEC-26b6e2 / D415** (Immutable Characteristic Atoms) — the semantic-finality
  affirmation discipline characteristic publication requires.
- **ADR DEC-65dc86 / D416** (BCF forward / BF-BO legacy compatibility) — direction
  statement; this sketch operationalizes its forward-investment clause.
- **BCF requirements doc** — the framework's PE1-PE6 publication eligibility contract,
  Framework Approval discipline, three-model consensus, no-fabrication rule.
- **BCF backend MVP close-out** (`business-concept-registry-backend-mvp-closeout.md`) —
  the proven backend authoring chain (F3 + F4-v2 + B6 + C5 + B10).
- **BCF UI MVP close-out** (`business-concept-registry-ui-mvp-shipped.md`) — the proven
  operator console (UI-S1..S5; the cycle time live publication through the UI).
- **MCF Foundation Requirements sketch** (`metric-context-framework-requirements-sketch.md`)
  — the sibling framework this sketch's forcing function points to.

The sketch does not re-derive any of these. It operationalizes them for vocabulary
enrichment.

**Status.** `proposed` — sketch awaiting full-plan expansion. The full plan opens as a
separate gate once the Legacy Vocabulary Stack Quarantine ADR lands (the next gate after
this sketch).

### 1.1 What this sketch is not

- Not a substrate design (no DDL, no DBCP).
- Not a panel-mechanics design (B6 is unchanged; the three-model consensus + no-fabrication
  + immutable authoring records are inherited).
- Not a publication-path design (B10 is unchanged; `draft → active` via C5 high-risk
  operator-confirm is inherited).
- Not a UI design (the UI MVP is shipped; new authoring UI is a separate later gate).
- Not a migration plan (per the working rule below, migration from BF/BO/CF is the
  forbidden frame).
- Not the Quarantine ADR (that's the next gate; this sketch is one of its inputs).

### 1.2 Working rule (binding through this sketch and the Quarantine ADR drafting)

- **No BF/BO/CF/Canonical Mapping as evidence, candidate source, lineage, bridge, migration
  input, or design input.** BF/BO/CF/CM may only be named as quarantined risk.
- **No CF→BusinessConcept conversion framing.**
- **No BF/BO→Entity/BusinessConcept conversion framing.**
- **No legacy bridge / mapping / shim framing.**
- **bc-seed, Source Contracts, Admission Contracts, Observation Contracts, source-reality
  evidence, and the KPI catalog (as operator intent) are NOT in quarantine** per ADR
  DEC-02f5a9 §5 carve-outs. The KPI catalog's metric *intent* (names, prose definitions,
  owners, thresholds) survives; the old BF/CF *bindings* do not.

---

## 2. Enrichment objective — the forcing function

Greenfield BCF enrichment without a forcing function is asymptotic. There are always more
concepts to author; "complete" is never reached. The MEMORY note from earlier in the BCF
arc — *"Finance done. 18 functions remaining (1,819 KPIs, 120 COs need BOs)"* — is the
shape of unbounded enrichment under the *old* model. We will not repeat it under the new.

**The forcing function: greenfield BCF enrichment proceeds only as far as the next
concrete MCF re-author exercise requires.** The objective is not "build a deep BCF
catalog"; the objective is "build the precise BCF coverage the next MCF gate needs to
prove its first end-to-end re-author through the new chain." Coverage beyond that target
is deferred to subsequent enrichment units, each pulled by its own MCF re-author target.

### 2.1 The first MCF re-author target — Average Sales Order Line Value (ASOLV)

The chosen target for the first MCF re-author exercise is the canonical Sales KPI
**Average Sales Order Line Value**:

> ASOLV is the average monetary value of a sales-order line item across a temporal
> window, computed as the sum of (unit price × ordered quantity) across qualifying lines
> divided by the count of qualifying lines.

In MCF-shaped form:

```
grain_entity = Sales Order Line          -- BCF Entity (id-typed reference)
formula      = SUM(unit_price * quantity) / COUNT(line)
                                         -- AST: two BC variable bindings, two reductions
variable_bindings = {
  unit_price : BC[Sales Order Line · unit price (amount)],
  quantity   : BC[Sales Order Line · ordered quantity (count)]
}
temporal_gate = trailing_window(period_quarter)
                                         -- MCF computed dimension; see §7
```

### 2.2 Why ASOLV is the right first MCF re-author target

Four converging reasons:

1. **Extends the existing BCF foothold without inventing new architecture.** We already
   have Entity `Sales Order Line` (active, B10a-S3) and BusinessConcept `Sales Order Line ·
   unit price (amount)` (active, B10a-S3). ASOLV adds one new characteristic (`ordered
   quantity`) and one new BusinessConcept (`Sales Order Line · ordered quantity (count)`)
   — a tractable enrichment unit (§9.2).

2. **Clean stored-vs-computed decomposition.** ASOLV is the textbook case for the §7
   route-to-MCF test:
   - **Stored (BCF):** `unit price`, `ordered quantity` — both arrive per-line from the
     source system; both are structural properties of `Sales Order Line`.
   - **Computed (MCF):** `SUM`, `COUNT`, the `/` aggregation, the temporal window
     `trailing_window(period_quarter)`. None of these are observable on a single line; all
     emerge at the metric evaluation boundary.

   This decomposition is so clean it can serve as the canonical teaching example in the
   full plan. An operator presented with a new candidate KPI can ask *"what's the ASOLV
   shape here?"* and route correctly.

3. **Universally recognised Sales KPI.** Not an idiosyncratic invention. Operators
   reviewing the panel evidence for the new vocabulary will not be puzzled by why the
   target exists. The KPI is independently meaningful; the re-author exercise inherits
   that meaning rather than manufacturing it.

4. **Exercises the cross-framework handshake end-to-end.** ASOLV requires:
   (a) BCF to author the missing characteristics and concepts through the proven path
   (B6 → C5 → B10 → UI);
   (b) MCF to consume those BCs by id and author an MC that binds to them;
   (c) the metric evaluation boundary to read the active MC and produce a Metric Snapshot
   from real source data;
   (d) the Metric Snapshot's value to be inspectable in evidence + lineage.

   ASOLV touches each stage of the chain just hard enough to prove it works. Heavier KPIs
   (multi-grain, multi-entity-join, fiscal-window-conditional, currency-normalised) are
   deferred to later units — the first re-author exercise should not also be the first
   stress test.

### 2.3 BCF coverage backward-derived from ASOLV

Required vocabulary, classified by current state:

| Subject | Term / label | Status | Notes |
|---|---|---|---|
| Entity | `Sales Order Line` | **active** | B10a-S3 publication cert `6ab6be07-…` |
| BusinessConcept | `Sales Order Line · unit price (amount)` | **active** | B10a-S3 publication cert `0f999280-…` |
| Characteristic | `unit price` | implicit-active | Embedded in the existing concept (concept binds entity × characteristic × rep term); promote to first-class Characteristic if the substrate doesn't already expose it (sketch open question §11) |
| Characteristic | `ordered quantity` | **NEW** | Atom; rep term `count` (or `decimal` if fractional quantities are in scope); first authoring act of the first unit |
| BusinessConcept | `Sales Order Line · ordered quantity (count)` | **NEW** | Second authoring act; binds entity × characteristic × rep term `count` |

What is **explicitly NOT** in the BCF coverage list (these are MCF's responsibility):
- The `SUM(…) / COUNT(…)` aggregation — MCF formula AST
- The temporal window `trailing_window(period_quarter)` — MCF temporal gate + computed
  dimension
- The grain alignment (`Sales Order Line`) — already on the MC body, just a typed Entity
  reference to a BCF object
- Any currency normalisation (e.g. converting line currency to USD) — MCF body work
- Any filter (e.g. "exclude voided lines") — MCF filter set

This decomposition is the working ground truth for the §7 route-to-MCF test below.

### 2.4 Definition of "enough BCF" for this unit

The first enrichment unit is complete when:

1. `ordered quantity` characteristic is `active` in `concept_registry.characteristic` with
   an `registry_author_vocabulary` authoring cert + `registry_transition` publication cert
   following the proven B10b-S4 / UI-S4b path.
2. `Sales Order Line · ordered quantity (count)` BusinessConcept is `active` in
   `concept_registry.business_concept` with `registry_create` authoring cert +
   `registry_transition` publication cert following the proven B10a-S3 / UI-S4b path.
3. Optionally: `unit price` is exposed as a first-class Characteristic if not already so
   (sketch open question §11.1).

When all three are met, MCF has the BCF surface it needs to author its first MC against
ASOLV. The unit closes; the next unit opens against whatever MCF asks for next.

---

## 3. Authoring path — re-affirms, does not invent

Every enrichment unit runs through the existing, proven authoring chain. The plan does
not modify any of these stages.

| Stage | Service / surface | Authority |
|---|---|---|
| Candidate intake | B6 Track 2 registry-authoring panel | `business-concept-registry.md`, B6 Track 2 design |
| Panel evidence | three-model consensus, M1–M10 checklist, no-fabrication, model identity recorded | BCF requirements PE1 + B6 panel spec |
| Low-risk auto-issuance | C5 `issueRegistryShapeCertification` for low-risk action codes | C5 framework-approval spec |
| High-risk operator confirm | C5 `confirmRegistryShapeCertification` for `registry_author_vocabulary` / `registry_transition` | C5-HR spec |
| F3 lifecycle write | `registerCharacteristic` / `createEntity` / `createBusinessConcept` / `transition*Lifecycle` | F3 spec |
| Publication transition | B10a (entity / concept) + B10b (characteristic) `draft → active` via `RegistryPublicationService` | B10 implementation design |
| Semantic-finality affirmation | characteristic publication requires `semanticFinalityAffirmed: true` | ADR DEC-26b6e2 |
| Operator UI | `bc-admin /business-concepts/*` — browse, publication queue, detail with provenance panel, publication confirm modal with Step C affirmation | UI-S1..S5 |
| Provenance bundle | `/api/bcf/registry/provenance/publication/:subjectKind/:registryId` — the publication evidence bundle the UI binds the confirm action to | Provenance-Inspection Read |

**Inheritance, not re-derivation.** Each enrichment act traces back to the precedents
already proven: characteristic authoring proven by `lead time` (B10b-S4), characteristic
UI publication proven by `cycle time` (UI-S4b), entity authoring + publication proven by
`Sales Order Line` (B10a-S3), concept authoring + publication proven by
`Sales Order Line · unit price (amount)` (B10a-S3).

If a new authoring act requires a backend or UI capability that doesn't exist (e.g. a new
authoring UI for an operator to draft a candidate from scratch rather than from a
curl-style API call), that capability is its own separate gate, not part of this
enrichment plan.

---

## 4. Authoring order inside an enrichment unit

Within any enrichment unit, the order is fixed by structural dependency:

1. **Characteristics first.** Atoms (per ADR DEC-26b6e2 — immutable, no version,
   `(term, definition)` IS the meaning). They have no structural dependency on entity or
   concept. Cheapest to author; most reusable; foundational.
2. **Entities second.** Role-bearing concepts with their own identity. May depend on
   already-active characteristics for identity-bearing properties (composite entities —
   see §8 substrate prerequisite). Simple entities have no characteristic dependency.
3. **BusinessConcepts third.** Bind entity × characteristic × representation term. Strict
   dependency on both predecessors being `active`.

A unit that needs new vocabulary at all three levels authors them in this order. A unit
that needs vocabulary only at one or two levels skips the others.

For the first ASOLV unit (§2.3): no new entity needed (Sales Order Line is already
active); two new artifacts — characteristic `ordered quantity`, then BusinessConcept
`Sales Order Line · ordered quantity (count)`. Order: char first, then BC.

---

## 5. Domain prioritization — Sales first

### 5.1 Why Sales

Per ADR DEC-02f5a9 §1, the Registry is the single vocabulary identity model across all
domains; there is no domain-specific Registry. Domain prioritization is therefore a
*sequencing* concern, not an *identity* concern — what to author first, not what to
classify under.

**Sales is the first domain.** Three reasons:

1. **The existing foothold is in Sales.** Entity `Sales Order Line`, BusinessConcept
   `Sales Order Line · unit price (amount)` — both authored and published through the
   proven path. The first new enrichment unit extends what already works.

2. **The §2.1 forcing function is a Sales KPI.** ASOLV operates at the Sales Order Line
   grain and consumes Sales characteristics. The vocabulary the first unit needs is by
   construction Sales vocabulary.

3. **Sales is the universal across industries — a discipline pre-test.** Sales vocabulary
   is shared by every customer (retail, manufacturing, services, SaaS, distribution). If
   we cannot author Sales BCs cleanly without contamination, we cannot author any other
   domain cleanly. Sales is the discipline pre-test for the framework.

### 5.2 What "Sales first" does not mean

- It does not mean Sales must be "complete" before any other domain is opened. The unit
  cadence is target-boxed (§9), not domain-boxed. A later MCF re-author target in a
  different domain (e.g. a Finance KPI like DSO, an Operations KPI like inventory turns)
  pulls the unit it needs in that domain.
- It does not mean Sales vocabulary takes priority over MCF runtime concerns. If MCF
  decides its first re-author target is in a different domain for structural reasons
  (e.g. the simplest MC to prove the new chain is actually a Finance KPI), the BCF
  enrichment plan revises §2.1 — the forcing function is MCF's call, not BCF's.
- It does not mean Sales BCs may inherit from BF/BO/CF sales artifacts. The working rule
  (§1.2) forbids that. Sales-first means "Sales-domain greenfield first", not "migrate
  Sales BF/BO/CF first".

### 5.3 The next domain handoff

The full plan settles the rule for opening the second domain. Working position: the
second domain opens when the second MCF re-author target is named and that target's
forcing function points outside Sales. The full plan may add additional triggers (e.g.
operator-driven priority).

---

## 6. Evidence sources — PE1 only

Greenfield BCF authoring accepts only the four authorized evidence sources from BCF
requirements PE1 (Publication Eligibility — Provenance). The B6 panel's no-fabrication
rule rejects any candidate whose grounding does not trace to one of these:

| Source | What counts | Examples for Sales |
|---|---|---|
| **(a) Recognized external standards** with verifiable citation | OAGIS BODs / Nouns, ISO 11179 representation terms, XBRL element names, UN/CEFACT, industry standards (e.g. for retail: ARTS) | OAGIS `SalesOrder` BOD; ISO 11179 representation term `amount` |
| **(b) bc-seed catalog entries** with verified provenance lineage | bc-seed rows with intact provenance back to a recognized source | bc-seed entry derived from an industry-methodology source |
| **(c) Source-system observations** with verifiable alias (provisional per PE1 open question — operator-confirm) | a source field name + sample value that grounds the candidate's meaning | "SAP VBAP-NETPR — Net price of the sales document item in document currency" |
| **(d) Operator-authored bounded-domain definitions** with explicit business justification | an operator-supplied definition with explicit rationale for why no external standard applies | Operator rationale: "ASOLV is universally used in retail / DTC; ISO 11179 and OAGIS define the constituents; the composition itself is a domain-recognized derivation, not a vocabulary standard" |

### 6.1 Explicit prohibition — BF/BO/CF/CM

**No candidate may cite a Business Field row, Business Object row, Canonical Field row, or
`cc_field_mapping` row as evidence.** Doing so would resolve grounding onto a vocabulary
the governing ADR DEC-02f5a9 §4 declares untrustworthy. The B6 panel's PE1
no-fabrication check must reject any such citation. This is the load-bearing
contamination-prevention rule; it must be enforced both by panel discipline and (in the
full plan) by a substrate-level check on citation URIs.

### 6.2 bc-seed is not BF/BO/CF

bc-seed is structurally similar to BF/BO/CF (catalog rows, semantic content, AI-tooling
adjacent) but is on the *opposite* side of the contamination line. Per ADR DEC-02f5a9 §5:
*"Source registration / seed catalogs — Survive — source knowledge and candidate inputs."*

bc-seed is curated, evidence-bearing, and was never authored at the contamination scale
BF/BO/CF was. It is an input to greenfield BCF enrichment, not a source to migrate from.
The distinction is important enough that the Quarantine ADR should state it
unambiguously.

### 6.3 KPI catalog metric intent is not vocabulary

The existing KPI catalog (`contract.metric_definition`, `contract.metric_definition_knowledge`)
contains metric names, prose definitions, owners, thresholds, formula prose. Per ADR
DEC-02f5a9 §5: *"Metric definitions / knowledge (the KPI catalog) — Survive as knowledge —
only the binding to concepts is rebuilt."*

This is MCF's input, not BCF's. The BCF panel must not cite KPI catalog rows as BCF
vocabulary evidence — those rows describe *metrics*, not *business concepts*. If a KPI's
prose definition implies the existence of a BC the Registry lacks, the implication
becomes a candidate via the operator (PE1 (d)), not via direct citation of the KPI row.
The full plan refines this rule.

---

## 7. Route-to-MCF test — drift prevention

This is the operational sieve that prevents BCF enrichment from quietly absorbing what
properly belongs to MCF. It is the per-candidate version of MCF sketch §2.1 (the stored
vs. computed test).

### 7.1 The test

For any candidate proposed for BCF authoring, the panel (and the operator at confirm
time) applies the following sieve in order. The first matching condition decides:

| Condition | If yes | Authoring path |
|---|---|---|
| 1. Is the candidate a value the platform **computes** at the metric evaluation boundary (over grain, time, filter, formula)? | YES → MCF | Reject from BCF; route to MCF authoring |
| 2. Is the candidate a **derived dimension** (fiscal_period, fiscal_year, calendar window, derived grain transform, bucket label)? | YES → MCF | Reject from BCF; route to MCF (MCF sketch §8) |
| 3. Does the candidate carry **aggregation semantics** in its definition (sum, average, count, max, min, percentile, ratio, growth rate)? | YES → MCF | Reject from BCF; the aggregation IS computation |
| 4. Is the candidate **formula-shaped** in its prose (e.g. "X minus Y", "X / Y", "X over the last N days")? | YES → MCF | The formula IS the meaning; route to MCF formula AST |
| 5. Is the candidate **runtime-context-shaped** (e.g. "the current month's", "year-to-date", "as of the most recent quarter close")? | YES → MCF | Temporal-gate-shaped; route to MCF temporal gate |
| 6. Is the candidate a **structural identity property of an entity** expressible as `(entity, characteristic, representation term)` without computation? | YES → BCF | Author through BCF |
| 7. Is the candidate a **reference property** (a typed link from one entity to another)? | YES → BCF | Reference-kind BusinessConcept; author through BCF |
| 8. Is the candidate an **entity** in its own right (role-bearing, identifiable)? | YES → BCF | Author through BCF as Entity |
| 9. Is the candidate a **vocabulary atom** (a term + definition standing alone, not bound to an entity)? | YES → BCF | Author through BCF as Characteristic |
| (default) None match | Reject as out-of-scope | Route to operator review |

### 7.2 Worked examples (Sales domain)

| Candidate | Test result | Authoring path | Rationale |
|---|---|---|---|
| `unit price` | (9) atom | BCF Characteristic | Vocabulary atom; the line stores it directly |
| `Sales Order Line · unit price (amount)` | (6) structural identity property | BCF BusinessConcept | Bound to entity Sales Order Line as a value property |
| `ordered quantity` | (9) atom | BCF Characteristic | Vocabulary atom |
| `Sales Order Line · ordered quantity (count)` | (6) structural identity property | BCF BusinessConcept | Bound to entity Sales Order Line as a value property |
| `Sales Order Line · line value` (= unit_price × quantity) | (4) formula-shaped in prose, (1) computed at evaluation boundary | **MCF metric** | The "value" of a line is a per-line computation. If the source system stores it pre-computed, that is admission-side data; the *authoritative* line value is MCF's |
| `average order line value` (ASOLV) | (3) aggregation, (1) computed, (5) runtime-context-shaped | **MCF metric** | The §2.1 forcing-function target |
| `currency code` | (9) atom | BCF Characteristic | Vocabulary atom (the code itself); ISO 4217 anchored |
| `Sales Order Line · currency code` | (6) structural identity property | BCF BusinessConcept | The currency the line was recorded in; structural |
| `current month sales` | (5) runtime-context, (3) aggregation, (1) computed | **MCF metric** | All three MCF flags |
| `fiscal_period` (the platform's authoritative value) | (2) derived dimension, (1) computed by `FiscalCalendarService.resolve(posting_date)` | **MCF computed dimension** | MCF sketch §2.6 worked example — even though the source SAP system stores `MONAT`, the *authoritative* fiscal_period is computed |
| `posting date` (the source's `BUDAT`) | (6) structural identity property | BCF BusinessConcept | The posting date observed on the line; raw stored fact (per MCF sketch §8.3 — the resolver input, not the resolved value) |
| `is voided` | (6) structural identity property | BCF BusinessConcept | Boolean property of the line; stored fact |
| `lines voided in window` (a filter result) | (5) runtime-context, (1) computed | **MCF filter** | Filter expression over the BC `is voided` |

### 7.3 The ambiguous middle — pre-computed source fields

Edge case worth naming. A source system may emit a value that is *internally* the result
of the source's own computation (e.g. SAP's `NETPR` is a net price already net of
discounts, computed by SAP). Is `net price` BCF or MCF?

**Answer:** BCF, if the platform consumes the value as a stored fact and does not
re-derive it. The source's internal derivation is opaque to the platform; the source's
value is the platform's stored datum. This is MCF sketch §2.1 test row 1 — *"Does this
value arrive in the platform pre-computed by an external system? If yes → BCF Business
Concept. Even if the source system derived it internally."*

But: if the platform decides to *re-derive* net price from gross price minus discount at
the canonical or metric boundary (because it does not trust SAP's net), the platform's
authoritative net price moves to MCF. The platform's *authority claim* is what decides,
not the source's behavior.

### 7.4 The §7 test is the panel's discipline, not just the operator's

The B6 panel applies this sieve to every candidate before producing an APPROVE verdict.
A candidate that fails the sieve receives a REJECT verdict with a closed-enum defect
code (e.g. `routes_to_mcf_aggregation`, `routes_to_mcf_temporal`,
`routes_to_mcf_computed`). The operator may override, but the override must be
operator-confirmed with explicit rationale (BCF requirements PE1 (d) bounded-domain
operator-authored). Override-by-default is forbidden.

The full plan specifies the panel prompt instructions, the defect-code closed set, and
the operator-override rationale shape.

---

## 8. Substrate prerequisite — identity-DAG acyclicity

### 8.1 The gap

`business-concept-registry.md` §§5, 122-148 establishes that **the identity-reference
graph is acyclic**: a composite entity's identity is an ordered or named set of
identity-bearing properties (value or reference), and the references form a DAG. MCF
sketch §15-Q9 cites the same acyclicity claim — its reachability algorithm depends on it.

What the current substrate (`concept_registry.entity` + `concept_registry.business_concept`
+ `concept_registry.characteristic` + their version tables) enforces structurally is the
`UNIQUE(entity_id, property_id)` constraint on the BusinessConcept identity tuple (ADR
DEC-02f5a9 §3). It does **not**, as of the BCF backend MVP close-out, enforce *DAG
acyclicity* on the reference-kind identity-bearing property graph at write time. The
acyclicity is asserted by design; it is not enforced by the substrate.

### 8.2 Why this matters for greenfield enrichment

The first enrichment unit (§2.3) and the next handful are very unlikely to introduce
composite entities or reference-kind identity-bearing properties — they extend
already-active simple entities with value properties only. The acyclicity gap is not in
the critical path for those units.

However, the moment a unit introduces a **composite entity** (one whose identity is
defined by reference-kind identity-bearing properties to other entities — e.g. an
`Inventory Position` whose identity is `(Material, Warehouse, Batch)`), the substrate's
inability to structurally enforce acyclicity becomes a live risk. A subtle authoring
mistake could create `A.identity_refs_B AND B.identity_refs_A`, producing a cyclic
identity graph that the design forbids but the substrate allows.

### 8.3 Action — flag as prerequisite DBCP gate

**Before the first composite entity is authored through any enrichment unit, a substrate
DBCP must add a structural acyclicity check** (working candidate: a deferred check
constraint or a trigger that walks the reference graph and rejects an insert/update that
would create a cycle).

This sketch does not design the DBCP — that is its own gate, with its own DDL review and
its own DB approval. The sketch only flags it as a prerequisite.

If an enrichment unit proposes a composite entity before this DBCP lands, the panel
rejects with a closed-enum defect code (e.g. `substrate_prerequisite_unmet:
identity_dag_acyclicity`). The full plan specifies the exact gate name and the panel
behavior.

### 8.4 What is NOT a substrate prerequisite

The first enrichment unit (§2.3) does **not** trigger this gate. It introduces no
composite entity and no reference-kind identity-bearing property. The first unit
proceeds against the current substrate.

---

## 9. Cadence and goal-setting — target-boxed enrichment units

### 9.1 The unit, defined

An **enrichment unit** is:
- A specific, enumerated list of candidate vocabulary (characteristics, entities,
  business concepts) named in advance.
- A specific MCF re-author target that the unit's candidate list backward-derives from
  (§2.1 mechanism).
- A completion criterion expressed as "every listed candidate is `active` in the Registry
  through the proven authoring path".

A unit is **completion-defined, not time-defined.** A unit closes when its candidate
list is exhausted. There is no time-box; if a unit's candidates take longer than
expected (e.g. because an operator-confirm review surfaces new evidence), the unit
extends until done. If a unit's candidates land quickly, the unit closes early.

This mirrors UI-S4a's discipline (one specific draft characteristic specimen, completion
on cert + state flip) and is the operational counterpart to BCF's panel-driven
authoring rhythm.

### 9.2 First enrichment unit — concrete candidate list

**Unit name:** `ASOLV-1` — first ASOLV-backing enrichment unit.

**MCF re-author target:** Average Sales Order Line Value (§2.1).

**Candidate list (ordered per §4):**

| # | Subject | Term / label | Authoring action code | Notes |
|---|---|---|---|---|
| 1 | Characteristic | `ordered quantity` | `registry_author_vocabulary` | Atom. Definition working draft: "The numeric quantity ordered on a single line of a sales order, expressed in the line's unit of measure." Representation term: `count` (or `decimal` if fractional quantities are in scope). Evidence: PE1 (a) — OAGIS / ISO 11179 anchoring. |
| 2 | BusinessConcept | `Sales Order Line · ordered quantity (count)` | `registry_create` | Binds entity `Sales Order Line` (already active) × characteristic `ordered quantity` (from step 1) × representation term `count`. |

**Optional (sketch open question §11.1):**

| # | Subject | Term / label | Authoring action code | Notes |
|---|---|---|---|---|
| 0a | Characteristic | `unit price` | `registry_author_vocabulary` | Promote to first-class Characteristic if not already exposed by the substrate. Definition: "The monetary price per single unit." Rep term: `amount`. Evidence: PE1 (a) — ISO 11179 `amount` |

**Completion criterion:** rows 1 and 2 are `active` in `concept_registry.*` with
publication certs of `action_code='registry_transition'` and `from_state_code='draft'` /
`to_state_code='active'`. Row 0a may close optionally depending on the §11.1 resolution.

**Estimated effort:** two B10 publication cycles (each ~5 minutes operator time + panel
run latency), plus characteristic semantic-finality affirmation on row 1.

**Handoff at unit close:** the BCF coverage is sufficient for MCF's first re-author
exercise (`MCF-S4a`-equivalent — author one MC binding to the new BCs).

### 9.3 Subsequent units — pulled, not pushed

Unit `ASOLV-2`, if needed, would expand BCF coverage to support a second MCF re-author
target (perhaps a related Sales KPI). Unit `ASOLV-2` opens only when MCF names its next
re-author target and that target asks for vocabulary the Registry does not yet have.

The full plan defines the cross-framework signal for "MCF needs new vocabulary"
(working position from MCF sketch §2.8: events or pull-side reads, never write coupling).
For the sketch, the rule is simpler: **the operator manually opens the next BCF
enrichment unit when the next MCF target is named.** Automation comes later.

### 9.4 Anti-pattern: open-ended seed catalog import

A predictable temptation: "while we're at it, let's import all of OAGIS into BCF
characteristics." This is exactly the unbounded enrichment trap §2 is designed to
prevent. Open-ended bulk seeding violates:

- **The forcing function (§2):** there is no MCF re-author target driving the import; the
  resulting vocabulary has no immediate consumer.
- **The PE1 evidence discipline (§6):** bulk seeding does not produce per-candidate
  evidence at the level of detail the B6 panel requires.
- **The target-boxed unit discipline (§9.1):** a bulk seed is by definition not a unit.

The full plan may eventually specify a *narrower* seed-import path for vocabulary that an
operator has explicitly committed to use in a near-term MCF target. The sketch does not
authorize it.

---

## 10. Non-goals and handoffs

### 10.1 Explicit non-goals

- **No MCF implementation work.** All MCF work — formula AST, variable binding, panel
  mechanics, publication path, UI — is MCF's territory. This sketch's only contact with
  MCF is the §2.1 forcing function and the §7 route-to-MCF test, both of which are
  read-only references to the MCF sketch.
- **No substrate work** beyond naming the §8 acyclicity prerequisite as a future
  prerequisite DBCP gate.
- **No UI work.** The existing UI MVP (UI-S1..S5) is sufficient for the first
  enrichment units. A future authoring UI (operator-facing draft authoring rather than
  curl-style API calls) is a separate later gate, not in this sketch's scope.
- **No BF/BO/CF migration.** Per the binding working rule (§1.2).
- **No legacy bridge** or shim or lineage. Per the binding working rule.
- **No Quarantine ADR drafting** — that is the next gate.

### 10.2 Handoffs

| Handoff target | Trigger | What the sketch hands off |
|---|---|---|
| **MCF authoring (first MC against ASOLV)** | Unit `ASOLV-1` closes (§9.2 completion criterion met) | The two BC ids the MC will bind to; the Entity id for the MC's grain; the publication cert ids of the new BCs |
| **Legacy Vocabulary Stack Quarantine ADR (next gate)** | This sketch's commit lands | The §6 evidence sources allow-list; the §6.1 explicit prohibition; the §7 route-to-MCF test; the §11 open questions that overlap with Quarantine ADR concerns |
| **Composite-entity substrate DBCP** | First enrichment unit that proposes a composite entity (not the first few units) | The §8.3 prerequisite specification |
| **Full Greenfield BCF Enrichment Plan** | After the Quarantine ADR lands | The full §11 open question list |

---

## 11. Open questions and "to be specified in full plan" markers

Items the sketch surfaces but does not resolve. Each becomes a section in the full
Greenfield BCF Enrichment Plan.

### 11.1 First-class Characteristic exposure

- **Q1 — Is `unit price` a first-class Characteristic in the current substrate?**
  The existing BC `Sales Order Line · unit price (amount)` references a characteristic
  by id (per the F2 schema); whether that characteristic row is browsable via the
  current F5-S2 `/characteristics` endpoint and the UI Characteristics tab is a
  substrate / data question the full plan should verify before opening unit `ASOLV-1`.
  If `unit price` is *not* exposed as a first-class Characteristic, row 0a in §9.2
  becomes mandatory rather than optional.

### 11.2 PE1 evidence allow-list precision

- **Q2 — bc-seed allow-list rule.** §6 says "bc-seed entries with verified provenance
  lineage" are PE1 (b). What counts as "verified provenance lineage"? The full plan
  defines the per-bc-seed-row criterion (e.g. "non-null `provenance_json.standard_ref`
  with a fetchable URL"). Mirrors the equivalent rule for direct standard citations
  (PE1 (a)).
- **Q3 — Source-system observation citation shape.** PE1 (c) is provisional pending
  operator-confirm sufficiency review (BCF requirements PE1 open question). The full
  plan settles the citation shape (e.g. `sourceLabel + citedText + provenance to the
  Source Contract row`).
- **Q4 — Operator-authored bounded-domain definition shape.** PE1 (d) requires explicit
  business justification. The full plan defines the minimum rationale length and
  required structure.

### 11.3 Route-to-MCF test precision

- **Q5 — Defect-code closed set.** §7.4 names a few candidate defect codes
  (`routes_to_mcf_aggregation`, `routes_to_mcf_temporal`, `routes_to_mcf_computed`).
  The full plan enumerates the closed set the panel uses.
- **Q6 — Override rationale shape.** §7.4 permits operator override of a route-to-MCF
  reject. The full plan defines the override rationale's minimum content (working
  position: must cite the §7 row the override contradicts and the reason).
- **Q7 — Re-classification of an already-active BC.** What happens if a BC is `active`
  in BCF but, on later inspection, fits the §7 route-to-MCF criteria? Working position:
  it stays active in BCF (Foundation Invariant III — historical state preserved); MCF
  may be informed not to consume it; future authoring may supersede with the correct
  classification. The full plan specifies the mechanics.

### 11.4 Substrate prerequisite (§8)

- **Q8 — DBCP design for identity-DAG acyclicity.** The full plan or a separate DBCP
  gate designs the structural check (deferred constraint? trigger? application-side
  invariant?). Substrate decision; out of sketch scope.
- **Q9 — When the first composite entity arrives.** Speculation: not in unit `ASOLV-1`,
  probably not in `ASOLV-2`. The full plan adds a "watch for composite entities" item
  to the enrichment-unit intake template so the substrate gate is checked before each
  unit opens.

### 11.5 Cadence (§9)

- **Q10 — Cross-framework signal for "MCF needs new vocabulary".** Working position:
  operator manually opens the next unit. The full plan or the full MCF plan specifies
  the automated signal mechanics (event bus? polling? a `bcf_authoring_request` table
  written by MCF and consumed by the BCF authoring UI?).
- **Q11 — Parallelism between units.** Working position: units run serially under
  operator attention to keep the panel evidence focused. The full plan revisits if
  operator throughput becomes a bottleneck.

### 11.6 Domain expansion (§5)

- **Q12 — Trigger for opening the second domain.** Working position: a named MCF
  re-author target outside Sales. The full plan may add additional triggers (operator
  priority, customer demand, dependency reachability).
- **Q13 — Cross-domain BC reachability.** A BC in one domain (e.g. `Customer · name`)
  may be referenced from another domain's metric (a Sales KPI segmented by customer).
  The full plan specifies the cross-domain referencing rules — working position:
  BC references are domain-agnostic since the Registry is single-namespaced.

### 11.7 KPI catalog handoff (§6.3)

- **Q14 — Reading the KPI catalog for MCF intent.** §6.3 says BCF must not cite KPI
  catalog rows as BCF vocabulary evidence. The MCF sketch §5 separates metric intent
  (survives) from binding (discarded). The full plan + MCF plan jointly specify which
  table reads MCF authoring may perform on `contract.metric_definition` /
  `metric_definition_knowledge`, with what discipline. This is cross-cutting between
  BCF and MCF — likely belongs in the Quarantine ADR.

---

## Status

`proposed` — operational sketch for greenfield BCF vocabulary enrichment. Companion to
the MCF Foundation Requirements sketch (commit `a967970` on bc-docs-v3 main). Input to
the Legacy Vocabulary Stack Quarantine ADR (next gate). The full Greenfield BCF
Enrichment Plan opens as a separate gate after the Quarantine ADR lands.

This sketch does not authorize any code, schema, migration, Docker, endpoint, UI, panel,
or substrate change. It is operational guidance for the next two or three enrichment
units, plus the inputs the Quarantine ADR and the full plan need.
