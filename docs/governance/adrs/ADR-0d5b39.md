---
uid: DEC-0d5b39
title: "The Reader Model and the Runtime Ecosystem"
description: "Reader anchored to one Business Concept Registry Entity; source-agnostic with per-source Flavors; the runtime ecosystem, its four boundaries, and the Runner/Evaluator machine split."
status: decided
date: 2026-08-18
project: bc-core
domain: runtime
subdomain: reader-model
focus: governance
supersedes:
  - DEC-129417
  - DEC-d785d4
---

# The Reader Model and the Runtime Ecosystem

## Supersession / retention lineage matrix (GOV-1 — valid status mechanics)

Status/frontmatter operate on **whole** decisions, never clauses. This ADR therefore uses whole-supersede where the predecessor is fully replaced, and an **in-body governed amendment** (the `DEC-ecd55c` in-part-amendment pattern) where the predecessor stays authoritative.

| Predecessor | Effect | Mechanism | Retained (still authoritative) | Files changed atomically |
|---|---|---|---|---|
| `DEC-129417` (per-subfunction consolidation) | **Whole supersede** | this ADR's UID in `superseded_by`; status → `superseded` | nothing | `ADR-129417.md` (status), this ADR |
| `DEC-17112b` (four-layer authoring surface) | **Partial amendment** | stays `decided`; the grouping doctrine (Decision 1 "Reader = subfunction admission boundary", Decision 6, P1 "subfunction uniqueness") is amended **in this ADR's body** + an in-body amendment note added to `DEC-17112b` | four-layer model, per-entity OC binding (`reader_observation_binding`), activation gate, P2–P6, P-F1…P-F8 | `ADR-17112b.md` (in-body note only, status unchanged), this ADR |
| `DEC-d785d4` (legacy `business_object_id` FK + BO/BF mapping enforcement) | **Whole supersede** | this ADR's UID in `superseded_by`; status → `superseded` — the Registry/cross-plane model replaces the FK and the mapping enforcement it enforced (not a "retarget") | nothing (retired mechanisms enumerated in the reconciliation plan) | `ADR-d785d4.md` (status), this ADR |
| `DEC-81cd26`, `DEC-ecd55c` (Connection authority) | **Cite/affirm** (not superseded) | governing authority for Decision 10 | both, in full | — |
| `DEC-02f5a9` (Registry supersedes BO/BF/CF) | **Cite** (vocabulary) | governs Decision 1 terminology + the B3 vocabulary marker | in full | — |
| `DEC-ada203` (composite metric runtime, `status: decided`) | **Partial amendment** | stays `decided`; in-body amendment note added; **amended clause:** its exact-selection→Lineage — the `as_of_period_end` "latest accepted upstream Snapshot at/before P" selection must record the **exact consumed Metric Snapshot IDs** in persisted Lineage (register E6/FND-R2-1), not upstream Contract UIDs | composite routing, formula execution, fail-closed missing-input behavior, and governed persistence — all **retained** | `ADR-ada203.md` (in-body note), this ADR, register E6 |
| `DEC-5ea578` (composite persistence, cited by DEC-ada203) | **Cite/affirm** | the persistence mechanism is retained and reused unchanged; the exact-Snapshot-ID requirement is an amendment to `DEC-ada203`'s selection clause, written **through** the existing `DEC-5ea578` persistence path (its shape already carries Lineage) | in full | — |

## Context

Two authoritative chapters governed the Reader contradictorily, on an undefined term ("Business Object family"). A grounded substrate study, an independent red-team, a foundation study, and a Codex review resolved it. The running code already anchors a Reader on a Registry Entity (`admitted_entity_id`, **one non-archived Reader per Entity** — the `uq_reader__active_entity WHERE archived_at IS NULL` uniqueness spans *draft and active*, not active alone; two Readers exist at full identity with zero source binding), which reverses DEC-129417/DEC-17112b's subfunction grouping in code — this ADR formalizes that and, per Codex, names exactly which **decisions it whole-supersedes** and which **clauses it amends**, and which controls it retains (see the lineage matrix).

**Why the reversal is right:** DEC-17112b grouped by sub-function *because entities are shared across sub-functions* (one source entity serves AR + billing + collections). Per-Entity anchoring is the better expression of that same insight — admit the entity **once**, and it feeds every sub-function that references it, without forcing it into one bucket. The entity is the shared unit; the sub-function is a classification over it.

## Decision

### 1. Reader anchoring — one Registry Entity
A Reader is anchored to exactly one **Business Concept Registry Entity** (colloquially a "business object"; that term is superseded by the Registry per DEC-02f5a9). **One non-archived Reader per Entity** (`admitted_entity_id`; `uq_reader__active_entity WHERE archived_at IS NULL` — the uniqueness spans *draft and active*, not active alone). Per F4, the Reader is *anchored to* an Entity — **never "grained"**; "grain" is reserved for Canonical/Metric Contracts.

### 2. Source-agnostic Reader; source specialization distributed (retains DEC-17112b four-layer)
A Reader carries no source system. Specialization is **distributed** across the four-layer model we retain: **Flavor** = `(source_system, scenario)`; **per-entity Admission Contract binding** (`reader_binding`) *and* **per-entity Observation Contract binding** (`reader_observation_binding` — the deprecated `reader_flavor.observation_contract_id` is retired; a Flavor observes **many** entities, each via its own OC binding); **Connector**; **Connection**. **Single Connector topology (D2/D3):** the Connector is reached through **`Connection.connector_id`** — the runtime resolution edge. The `reader_flavor.connector_id` edge is **retired** (register D3); this ADR does not retain an independent Flavor→Connector authority. Flavor topology P-F1…P-F8 (no tenancy in flavors, one-flavor-reads-many-entities, one active per `(reader, source_system, scenario)`) is retained.

### 3. The Reader admits; it does not compute (with precision)
Admission may **validate, select, map, and compose Source Object identity** under the Admission and Observation Contracts. It must **not resolve canonical meaning**. All computation — Canonical, Metric (incl. secondary metrics), Action — belongs to the Evaluators (Decision 6), across distinct boundaries. Naming: the **Runner** is the admission machine; the Reader is its governed definition. **(F3) This Runner/Reader naming split is introduced by this ADR — it is net-new modeling, not a claim about pre-existing Foundation doctrine (which currently attributes the admission act to the Reader).**

### 4. Function / sub-function are non-identity classification
`function_code`/`subfunction_code` are **classification / stewardship metadata**, not Reader identity or anchor. They are *not* solely consumption-side — decided doctrine also uses classification at canonical/metric surfaces — but a Reader-side value **cannot create semantic authority**. (The taxonomy `master.master_subfunction` itself needs curation for its real job — register I3.)

### 5. BCF is the authoring anchor; contracts are runtime-enforced (F1 precise)
The Reader/OC/CC are authored/activated against a BCF Registry Entity — BCF is the **authoring authority**; authoring evidence retains the active Entity/version checked. At runtime, admission **resolves the exact pinned SC/AC/OC versions once per invocation** and **re-evaluates the `source_filter` per record** (the authority; connector pushdown may be derived but is not the authority). It does **not** select "current" contracts, mint contract/BCF state, or reinterpret Entity meaning.

### 6. The Evaluator is an umbrella over three distinct boundary machines (F2 / D6)
"Evaluator" is an **umbrella term**, not one machine, for the three the platform already names: the **Canonical Evaluator**, the **Metric Evaluator**, and the **Action Evaluator**. Each is an **independently-invoked Foundation boundary act** with its own contract, inputs, gates, synchronous proof (Evidence + Lineage), and Run record. One act produces exactly one progression-object version; shared code or deployment **must not merge boundaries**.

### 7. Include the Action boundary and Intervention Contract (D7 / FND-3)
The runtime chain is the **full four-boundary spine**: Admission (SC/AC/OC → Source Object) → Canonical (CC → Canonical Object) → Metric (MC → Metric Snapshot) → **Action (Intervention Contract → Action Object)**. Metric Snapshots and Action Objects are **authoritative progression objects, not consumption.** Disambiguate **platform Reader Bindings** (which contract versions a reader applies) from **tenant Contract Bindings** (which contracts a tenant uses).

### 8. Derivation is delegated, not invented (DAG by delegation)
Two graphs, kept distinct (D8):
- The **contract dependency graph** (upstream Metric Contracts a secondary metric binds, via `DEC-0f3e57/D467`'s `metric_input` role) is a **plan** — an authoring-time acyclic graph a governed campaign *may* use to order work.
- The **Metric Snapshot Lineage graph** is **descriptive only** — a record of the exact upstream Snapshot versions a secondary act consumed.
- A secondary Metric act **selects fixed upstream Snapshot versions** (governed selection) and records them in its Lineage. It does **not** make the Metric Evaluator implicitly invoke upstream acts, and traversal **never** triggers recompute (a changed upstream yields a *new* forward act; Invariant V). If a policy schedules multiple new acts topologically, **each is an explicit, independent boundary invocation** with its own contract, proof, and Run.
- Detail is **delegated** to DEC-0f3e57 + the Object Model; runtime production/gaps are inventoried in the register (§E), not asserted here.
- **Secondary Canonical Objects (CO←CO) are excluded by design** — the Canonical boundary input is **Source-Objects-only** (Tier 1). This ADR proposes no secondary-CO mechanism.

### 9. Reader lifecycle (entry point of data — GOV-3)
Governed: activation gates (the chain-resolvability gate, retained from DEC-17112b), deprecation/archive, fail-closed chain integrity. **A new SC/AC/OC version produces a new temporal binding** (`unbound_at` the old row + a successor row); it does **not** by itself supersede the Entity-anchored Reader. **Reader supersession is reserved for a Reader-definition change** that actually requires a successor.

### 10. Connection authority (GOV-2)
Connection **configuration is platform-held** (`runtime.connection`), **tenant-owned** via `tenant_id`; **credential material is external** (AWS Secrets Manager — the row holds only a reference); execution/progression records are tenant-side. (Per `DEC-81cd26`, `DEC-ecd55c`.)

### 11. Foundation obligations at admission (D9 / FND-1/2)
The Runner/Reader must: emit **immutable** Source Objects (III); **record version-pinned** SC/AC/OC references (IV); be **non-replayable** — same observed state twice = two distinct SOs (V); never skip the Source Object to emit a CO (II); emit **Evidence on every admission including rejections** — but **rejections emit Evidence only, not Lineage** (no Source Object ⇒ no reference edge); and **admission does not produce canonical meaning — Invariant I reserves business meaning for canonical evaluation.**

## Consequences
- **Corrects/supersedes** per the lineage above; **retains** the DEC-17112b four-layer controls.
- **Requires** the expanded reconciliation plan (the authoritative surfaces named in that plan), the narrowed ecosystem chapter, the vocabulary supersession marker (register B3), and the companion Orchestration ADR.
- **Enables (follow-on units):** source-side wiring (register §D), OC→CC completion (register §E), Runner hardening (register §G).
- **Deferred (named in the register):** physical infra (§H); the **exact-consumed-Snapshot-ID Lineage repair (E6/FND-R2-1) and later secondary-metric expansion** — note the secondary-metric runtime *already exists* (composite evaluator + governed persistence + 92 `fact.ms_*` + `evidence.lineage_object`); it is the exact-snapshot proof that is missing, not the runtime; push build (C4).

## Alternatives considered (rejected)
- **Sub-function grain** — a classification taxonomy, contradicts the running code + evidence, internally inconsistent; the shared-entity rationale is better served by per-Entity anchoring.
- **BCF Registry Entity as a runtime authority** — BCF is reference at runtime; would couple runtime to the concept registry.
- **Admission-coherent source bundle as grain** — refuted: Readers exist with full identity and no source binding.
- **One integrated orchestration manager** — rejected in the Orchestration ADR (re-couples decoupled tracks; risks boundary merge).

## Foundation gate
- **Repair location:** B (contract semantics/vocabulary) + the deferred runtime-component layer. **Design act, not execution net** (DEC-c48b0f).
- **Invariant check:** Decisions 8/11 encode the derivation-DAG non-replay and the admission obligations; the ADR inherits — does not restate or re-govern — the invariants and the four-boundary model.
