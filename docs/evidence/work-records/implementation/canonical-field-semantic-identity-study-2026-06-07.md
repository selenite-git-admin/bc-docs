---
title: "Canonical Field-Level Semantic Identity — grounded ADR/options study (read-only)"
description: D429 Step 2. A grounded options study answering six operator questions about what a Canonical Contract field must mean, what it binds to in the Business Concept Registry, how identity flows Source→Observation→Canonical→Metric, how MCF consumes that identity without inventing mappings, what happens to legacy Canonical Contracts, and the minimum ARPI/AR-pilot path. Frames the work as the implementation of an already-locked Foundation decision (DEC-02f5a9), not a new vocabulary decision. Options + a recommendation per decision. Authorizes no code, schema, DB write, migration, ADR, or panel — held for operator lock.
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: canonical-identity
focus: foundation-implementation
---

# Canonical Field-Level Semantic Identity — options study (read-only)

> **What this is.** The grounding study for D429 **Step 2** (the next governed gate after Step 1, contract-version immutability — applied & recorded `CHG-7fb0db`). It answers the six operator questions, presents options per decision, and recommends one — but **authorizes nothing**: no code, schema, DB write, migration, ADR file, or panel. The eventual artifact (an ADR) is filed only after the operator locks the decisions below.
>
> **Method.** Foundation authority (`the-contract-grammar.md`, `the-evaluation-boundaries.md`, `the-object-model.md` via DEC-02f5a9) read first-hand; this session's audit memo (finding **X2**) and ARPI synthesis proof reused; live `bc_platform_dev` substrate inventoried read-only by three subagents (`contract.*`, `concept_registry.*`, `metric.*`/`mcf.*`). Runtime objects in `tbc_sandbox1_dev` not queried.
>
> **Decision status (2026-06-07): LOCKED — A1/B1/C1/D1/E2/F1.** Recorded in the Step-2 ADR DEC-a6258b/D430 (*Canonical Contract field-level semantic identity*). This study is the grounding; the ADR is the decision of record. ADR scope = grammar + resolver decision only; DDL/meta-schema/resolver implementation deferred to a later DBCP; Observation-level concept binding deferred; archived legacy CCs not migrated; ARPI proof slice = one greenfield Customer Invoice Canonical Contract carrying the three ARPI concepts.
>
> **Scope note (DEC-d72560 BF/CF split).** D430 covers the **Canonical Field side only** of the old Business-Field / Canonical-Field split. The **Business Field side** — source/observation field → governed `business_concept.concept_id` — is a **separate Observation-side semantic-identity ADR/study** (`observation-field-semantic-identity-study-2026-06-07.md`). Full chain proof requires the Observation **and** Canonical **and** Metric Contract all sharing `concept_id`. The ARPI minimum here is therefore a **canonical-side proof only — NOT a full O→C→M proof** until the Observation-side binding lands.

---

## Headline (the reframe that changes the work)

**Foundation has already decided the direction. This ADR decides the implementation shape — which Foundation explicitly deferred.**

- **DEC-02f5a9** (Business Concept Registry) is *locked* and supersedes the Business-Field / Business-Object / Canonical-Field primitives and the Canonical Mapping identity layer. It states: *"Contracts reference Business Concepts by identity,"* and for the Canonical Contract specifically: *"the Canonical Contract references an Entity and binds Business Concepts directly, and the Canonical Mapping identity layer is eliminated."*
- The Contract Grammar chapter, describing the Canonical Contract body under DEC-02f5a9, already says `field_selection[]` *"references Business Concepts"* — and then states the one open item: **"the schema-level key naming is settled at the greenfield cutover."**

So the question is **not** "should a canonical field carry business meaning?" — that is settled. The open questions are: *which identity key, declared where, resolved how, and what is the smallest slice that proves it.* That is precisely what audit finding **X2** flagged as unimplemented ("the Canonical Contract carries no field-level semantic identity"), and it is the single upstream fix that makes the Canonical boundary correct and the Metric boundary resolvable.

**The one missing link (proven, not asserted).** Precise vocabulary first: **BCF** (the Business Concept Registry, `concept_registry.*`, DEC-02f5a9) **defines governed business meaning**. **MCF** is the authoring/governance framework — it does not *hold* meaning; it authors and governs **Metric Contracts**, which are the artifacts that record variable bindings. With that distinction, three facts from the live substrate:

1. A **Metric Contract variable binding already references a BCF Business Concept** — strong identity. Stored in the MCF substrate as `mcf.metric_variable_binding.bound_business_concept_id` → `concept_registry.business_concept.concept_id` (uuid); ARPI's three variable bindings each reference one. ✅
2. A **Canonical Contract field references no BCF Business Concept** — no identity at all: `contract.canonical_contract_version.contract_json.body.field_selection` is a flat **string array**; resolution is by string field name (`canonical-resolution.service.ts → resolveField()`); zero concept/characteristic/entity reference in the CC body or the `canonical_mapping` layer. ❌
3. **Nothing joins them.** There is no path from a `business_concept_id` to a `(canonical_contract, canonical_field)`. `concept_registry.business_concept_version` records definition/provenance but **no canonical-or-field binding**.

Stated as the gap precisely:

```
Metric Contract variable binding → BCF Business Concept   ✅
Canonical Contract field         → BCF Business Concept   ❌
```

The Metric Contract records *what each variable means* (a Business Concept). The Canonical Contract records only *what columns it has* (names). The reference that says *"this canonical field carries that Business Concept"* does not exist. **Adding that reference to the Canonical Contract field is Step 2.** Runtime resolution then matches Metric Contract variables to Canonical Contract fields by shared `business_concept.concept_id`. MCF authors/governs the Metric Contract; it invents no mappings.

---

## Grounding evidence (live, 2026-06-07)

| Layer | What it carries today | Identity strength |
|---|---|---|
| **BCF `concept_registry`** | `business_concept(concept_id uuid PK, entity_id, characteristic_id, kind, lifecycle_state, active_version_id, …)`; identity = `entity.property`, `UNIQUE(entity_id, characteristic_id)` while active. **101 active concepts, 52 active characteristics, 14 active entities.** | **Authority** — the identity source |
| **Observation Contract** | `observation_field_map`: source field → `business_field_code` (**free string**, DEC-02f5a9-pending — not yet a concept identity) | Weak (string) |
| **Canonical Contract** | `field_selection[]` = **string array**; `resolution_rules[]` = {rule, field_code}; `grain`, `resolved_schema`, `posting_date_field`, `business_object_code` (entity name string). **56 CC headers, 0 active, 83 versions.** No concept identity. | **None** ← the gap (X2) |
| **Metric Contract (legacy)** | `contract.metric_contract_version.body.co_bindings[]` = {role, `canonical_contract`:string, `fields_used`:[string]}. `metric.metric_binding` (1,133 rows): CC by **uuid**, fields by **string**. **1022 versions / 2 active** (being retired). | Weak (strings) |
| **Metric Contract (authored under MCF)** | each variable binding references a BCF Business Concept — `mcf.metric_variable_binding.bound_business_concept_id` (uuid → BCF), `bound_entity_id` (uuid grain), + `representation_term_snapshot`/`unit_code_snapshot`/`data_type_snapshot`. *(MCF is the framework that authored it; the binding is the Metric Contract's.)* | **Strong (concept uuid)** — already correct |

**ARPI specimen** (the Metric Contract `average_revenue_per_invoice`, authored under MCF; the M-track proof metric — *not* the legacy `accounts_receivable_turnover_ratio`, a different metric): grain entity `e3963e45…` (Customer Invoice); formula `divide(sum(var:numerator_source), count_distinct(var:denominator_key))`; **three variable bindings, each referencing a BCF Business Concept**, none carrying a canonical pointer:

| role | bound_business_concept_id | repr / unit / type |
|---|---|---|
| `numerator_source` | `a42d3fc0…` | amount / USD / decimal |
| `denominator_key` | `095afe86…` | identifier / — / string |
| `temporal_anchor` | `d05f24b3…` | date / — / date |

This is the exact set of `UNRESOLVED@C` bindings the ARPI synthesis proof could not resolve — because the canonical-side concept declaration does not exist.

---

## The six operator questions

### Q1 — What does Foundation require a Canonical Contract field to mean?

**A canonical field must mean exactly one Business Concept — the `entity.property` it carries — referenced by identity, not by name.**

- The Canonical Contract "declares the canonical form of one **Entity**" (its grain); each field in `field_selection[]` "references **Business Concepts**" (Contract Grammar §Canonical Contract, DEC-02f5a9 framing).
- **Invariant I** (meaning is evaluated once, at its boundary): the canonical evaluation boundary is *where canonical meaning is produced*. Therefore the canonical field is the artifact that must **anchor** that meaning. Today it anchors nothing (name only) → meaning is never anchored where Foundation requires → this is the X2 gap, an Invariant I gap at repair-location **B**.
- A field's `resolution_rules` (sum/latest/assert_equal) declare *how source values collapse into the field* — that is collapse discipline, **not meaning**. Meaning is the concept the field carries. The two are orthogonal; today only the former exists.

**Not in scope of a field's meaning:** the grain (declared once at CC level via the entity), the source columns (repair-location A, legitimately physical), or the formula (the Metric boundary's concern).

### Q2 — Should a canonical field bind to business_concept, characteristic, both, or a snapshot?

**To the `business_concept` (the `entity.property` pair), referenced by `concept_id`; with frozen representation/unit/type *snapshots* for drift defense.** A business_concept already *is* the (entity, characteristic) pairing, so binding to it captures both without redundancy — and it matches the key the **Metric Contract variable binding** already uses on the other end (`bound_business_concept_id`), making runtime resolution a trivial `concept_id = concept_id` match.

| Option | Bind key | Verdict |
|---|---|---|
| **A1 (recommended)** | `business_concept_id` (concept anchor uuid) | Single stable key; **identical to the Metric Contract variable binding's key** (`mcf.metric_variable_binding.bound_business_concept_id`) → runtime match is `concept_id = concept_id`. Survives concept *version* supersession (anchor is stable); CC-version immutability (Step 1) freezes the reference correctly at publish. |
| A2 | `(entity_id, characteristic_id)` pair | Semantically equivalent (it *is* the concept identity) but redundant — the concept anchor already encodes it, and MCF references the anchor, so A2 forces an extra lookup. Use only if a concept anchor is unavailable. |
| A3 | `(entity_code, characteristic_term)` strings | **Reject.** Terms are reusable after supersession (`uq_characteristic_term_live` frees a term when its owner is superseded) → silent rebind to the wrong successor. Human-readable but not identity. |
| A4 | reference-kind concepts (`target_entity_id`) | Applies to relationship fields, not value fields; ARPI's three are all value-kind. Note for completeness; not the pilot path. |

**Snapshot (recommended addition, E2 below):** alongside the `concept_id`, freeze `representation_term` / `unit` / `data_type` on the field at publish — mirroring the snapshot columns the Metric Contract variable binding already carries (`mcf.metric_variable_binding.*_snapshot`). The `concept_id` is **identity**; the snapshot is **drift defense** (publish-time validation can assert the CC field's snapshot matches the concept's live representation, and flag if the concept later drifts). Identity is never the snapshot.

### Q3 — How does this affect Source → Observation → Canonical → Metric?

**The `business_concept` becomes the shared identity token carried across the three semantic boundaries. Each boundary declares which concept each of its fields carries; the engine resolves by matching that identity — never by string name, never by a mapping invented downstream.**

| Boundary | Today | Under Step 2 | Change size |
|---|---|---|---|
| **Source** | physical field names | unchanged (physical is correct here — repair-location A) | none |
| **Observation** | source field → `business_field_code` (free string) | source field → `business_concept_id` (identity) — *the admission-side concept binding* | parallel hardening (see scope note) |
| **Canonical** | `field_selection` = names | each field declares `business_concept_id` (+ snapshot) — *the canonical-side concept binding* | **the core of Step 2** |
| **Metric Contract** | legacy: string `fields_used`; authored-under-MCF: each variable binding references a Business Concept (already identity) | unchanged; runtime matches MC variables to CC fields by shared `concept_id` (via the CC declaration) | **none** — the Metric Contract already binds right |

The decisive property: **runtime resolution matches a Metric Contract variable to a Canonical Contract field by shared `business_concept.concept_id`** — i.e. "find the active CC for this grain entity whose `field_selection` declares concept X → that field is the column." This closes the loop the ARPI synthesis proof proved open. It also satisfies the CLAUDE.md **cross-system portability test**: a second source system onboards via its own OC→concept and CC→concept with **no Metric Contract edit**, because the Metric Contract variable binding references the concept, not a column.

### Q4 — How does MCF consume the identity without inventing mappings?

**The Metric Contract variable binding references a BCF Business Concept; at runtime the engine matches that variable to the Canonical Contract field declaring the same concept. The concept→field mapping lives in the CC. MCF only authors/governs the Metric Contract — it declares nothing about canonical contracts or column names, and invents no mappings.** This is the operator's Foundation correction made concrete: *MCF is the framework; the Metric Contract is the artifact; BCF is the meaning; the CC must carry the same meaning.*

| Option | Where the concept→field binding lives | Verdict |
|---|---|---|
| **B1 (recommended)** | **In the Canonical Contract field declaration** (`field_selection` entry carries `business_concept_id`). A read-only resolver `(grain_entity_id, business_concept_id) → (canonical_contract_version, canonical_field)` reads it. | Foundation-correct: canonical meaning declared at the canonical boundary; the runtime engine *matches*, MCF only authors the Metric Contract. No new mapping family. |
| B2 | In a **separate binding table** (concept → canonical field), repair-location C | Reintroduces a Canonical-Mapping-shaped side layer that **DEC-02f5a9 explicitly eliminated**. The CC should declare its own meaning, not have it asserted externally. Reject unless B1 proves infeasible. |
| B3 | **In the Metric Contract / MCF layer** (the Metric Contract records a canonical field) | **Reject — this is "MCF invents mappings,"** exactly what the operator forbade and what the legacy `co_bindings` anti-pattern does (a variable bound straight to a column name). |

**Resolution determinism (Decision C).** B1 needs the resolver to return *exactly one* field. Options:

- **C1 (recommended for the pilot):** one active CC per grain entity, and a concept appears at most once in a CC's `field_selection`. With **0 active CCs today**, this is free to adopt. Deterministic.
- C2: multiple active CCs per entity with declared precedence — defer until a real multi-CC-per-entity case exists.
- C3: the metric names the CC explicitly (back to `co_bindings.canonical_contract`) — partial regression to string binding; reject.

### Q5 — What happens to legacy Canonical Contracts already missing this identity?

**Nothing is migrated. The AR pilot is greenfield.** This is the most consequential substrate fact: **there are 0 active Canonical Contracts** (all 56 headers archived Apr–May 2026).

| Option | Verdict |
|---|---|
| **D1 (recommended)** | Leave the 56 archived CCs untouched (Invariant III — they are immutable preserved state; any historical COs they produced remain valid). Author **new** active CCs with concept identity from the start. The legacy `contract.metric_contract` string door is guarded **separately** (audit step 3), not here. |
| D2 | Backfill archived CCs with concept identity | **Reject** — mutates immutable/archived versions, contradicts Step 1's immutability triggers, and yields no value (nothing reads them). |

So Q5's honest answer: **"legacy CCs are already archived → no migration; new CCs are authored greenfield with identity; legacy *metric* bindings die with the legacy retirement, on a separate track."** There is no legacy-CC remediation burden on the Step 2 critical path.

### Q6 — What is the minimum path for ARPI / AR pilot?

The smallest slice that **proves the identity model end-to-end** and **unblocks ARPI evaluation** (the `UNRESOLVED@C` set):

1. **Grammar (repair-location B):** extend `canonical-v1` so a `field_selection` entry carries `business_concept_id` (+ frozen `representation_term`/`unit`/`data_type` snapshot). This is the one schema/meta-schema change; it is the deferred "schema-level key naming" DEC-02f5a9 named. *(DBCP — separate explicit approval; not in this study.)*
2. **Author one CC, greenfield:** an active Canonical Contract for the **Customer Invoice** entity (`e3963e45…`) whose `field_selection` declares ARPI's three concepts by identity — `a42d3fc0…` (amount), `095afe86…` (identifier), `d05f24b3…` (date) — each mapped to a canonical field name + resolution rule + source binding. (Via the SERVICES-ONLY authoring path, not raw SQL.)
3. **Resolver (repair-location C, read-only):** `(grain_entity_id, business_concept_id) → (canonical_contract_version, canonical_field)`, reading the B1 declaration. Deterministic under C1.
4. **Re-run the ARPI synthesis proof:** with the resolver, the three `UNRESOLVED@C` bindings resolve → an **evaluation-grade** `contract_json` becomes synthesizable. This is the concrete unblock for **D429 Step 5** (resume materialization) — for ARPI only.

**Minimum vs full:** the minimum proves the mechanism via the *canonical* link (what the engine reads, and what ARPI is blocked on). Full Foundation soundness also binds the **Observation** side (source field → concept) so the canonical field's source provably carries the claimed concept (O→C concept consistency). The OC binding is a parallel hardening, not on the ARPI minimum critical path, but should be sequenced next so identity is consistent across all three boundaries rather than asserted only at C.

---

## Decision matrix (for operator lock)

| # | Decision | Options | Recommendation |
|---|---|---|---|
| **A** | Canonical-field identity key | A1 `concept_id` · A2 `(entity_id,characteristic_id)` · A3 strings · A4 reference-kind | **A1** |
| **B** | Where concept→field binding lives | B1 in the CC field · B2 separate table · B3 in MCF | **B1** |
| **C** | Resolution determinism | C1 one active CC/entity + concept-unique · C2 precedence · C3 metric names CC | **C1** (pilot) |
| **D** | Legacy CC treatment | D1 leave archived, author new · D2 backfill | **D1** |
| **E** | Identity vs snapshot | E1 `concept_id` only · E2 `concept_id` + frozen repr/unit/type snapshot | **E2** |
| **F** | OC concept binding | F1 minimum (CC only now, OC next) · F2 require OC+CC together before any pilot | **F1** (sequence OC immediately after) |

---

## Foundation gate (for the eventual fix this study scopes)

- **Repair location: B (contract semantics)** — extend the Canonical Contract grammar so a field declares its governed meaning (a Business Concept by identity). Secondary, read-only touch at **C (binding)** — the resolver that reads the B declaration. Explicitly **not** D/E/F (no engine/storage/read-model compensation) and **not** the Metric Contract / MCF layer (no MCF-invented mapping).
- **Why B, not A:** Source/Observation declare what the source emits/admits; *canonical meaning* is by definition produced at the Canonical boundary (Invariant I). Anchoring it anywhere downstream is compensation.
- **Why B, not C–F:** the hand-typed `co_bindings` / name-only resolution are exactly C/D **compensating** for the absent B identity. The hard rule forbids lower-layer compensation for an upper-layer semantic gap. Putting the binding in a side table (B2) or in MCF (B3) repeats that error.
- **Invariant alignment:** I (meaning anchored at its boundary) — the point of the change; III + contract-grammar immutability (Step 1, applied) — new CC versions are authored with identity and then frozen, so identity references are immutable post-publish; VI (evidence emitted) — unchanged.
- **No DB row hand-edits; SERVICES-ONLY** for any eventual authoring; greenfield CC via the onboarding service, never raw INSERT.

---

## Relationship to the D429 sequence

This study is **Step 2** of the operator-locked five-step sequence (audit memo §Recommended next actions):

1. ✅ **Step 1 — contract-version immutability** (applied, `CHG-7fb0db`).
2. **Step 2 — canonical field semantic identity** ← *this study; ADR pending operator lock of A–F.*
3. Step 3 — close/guard the legacy Metric Contract string door (separate; not gated on Step 2 completion).
4. Step 4 — fix fail-open activation/publication gates (X5/X4).
5. Step 5 — resume D428 MCF materialization (the ARPI minimum path Q6 is the first thing it unblocks).

Step 2 is the keystone: it is the single upstream fix that makes the Canonical boundary Foundation-correct **and** makes MCF-authored Metric Contracts resolvable to runtime evaluation (by giving the CC field the BCF reference the Metric Contract variable binding already has).

---

## Decisions taken (locked 2026-06-07)

1. **A1/B1/C1/D1/E2/F1 locked.** Canonical Contract fields carry one primary governed `business_concept.concept_id` (A1), declared in the CC field (B1), resolved deterministically under one active CC per grain entity with each concept at most once (C1); archived legacy CCs are not migrated (D1); identity is `concept_id` + a frozen semantic snapshot for drift defense (E2); the CC change lands now, Observation-level concept binding is deferred (F1).
2. **ADR scope = grammar + resolver decision only** (B-layer). The meta-schema/DDL change, the resolver implementation, and the greenfield-CC authoring are deferred to a subsequent DBCP — Step 1's "decide, then DBCP, then apply" rhythm.
3. **ARPI proof slice confirmed** — one greenfield Customer Invoice Canonical Contract carrying the three ARPI concepts + the resolver — before any generalization beyond one entity. **This is a canonical-side proof only; it is NOT a full O→C→M proof until the Observation-side binding (the old Business Field role) lands** (separate ADR/study).
4. **Observation-level binding deferred** — sequenced after the CC change, not folded into this ADR.

These decisions are recorded in the Step-2 ADR (*Canonical Contract field-level semantic identity*); this study is the grounding evidence behind them.

## Scope guard

Read-only options study. No code, schema, DB write, migration, ADR file, PR, or panel. No `synthesizeContractJson`, no canonical contract authored, no meta-schema edited. Runtime objects in `tbc_sandbox1_dev` not queried. This study recommends; the operator locks; only then is an ADR filed and a DBCP drafted.
