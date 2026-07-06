---
title: "D431 Observation Field Semantic Identity — implementation change proposal (grammar + O↔C check; NO DDL)"
description: Implementation proposal for DEC-4a17e0/D431 (sibling to D430). Adds a new immutable observation-v2 grammar whose field_mappings entry declares one governed business_concept.concept_id (O-A1, semantic authority) + a frozen representation_term/unit/data_type snapshot (O-E), with business_field_code demoted to an optional label; an OC-side author-time field→concept integrity check; and the author-time O↔C consistency check (O-C1) that requires every active canonical-v2 field's concept to be declared by an active observation-v2 OC for the same grain entity (identity-equality, concept-mediated — the canonical claim becomes provable-from-source). observation-v1 retained for the 95 free-string active versions; legacy OCs not migrated (O-D). Service + resolver + tests only; NO table/column DDL, NO migration, NO data change; no canonical-v2 seeding; no greenfield OC/CC authoring; no ARPI MC rebind; no MCF materialization.
status: draft
date: 2026-06-08
project: bc-core
domain: contracts
subdomain: observation-identity
focus: schema
---

# D431 Observation Field Semantic Identity — change proposal (grammar + O↔C check)

> Implements **DEC-4a17e0 / D431** — the **Observation-side** sibling of **DEC-a6258b / D430** (canonical side, now on `main`, merge `a3d41ea`). Scope = the deferred Observation declaration (the old Business Field role after DEC-02f5a9 collapsed BF+CF into one Business Concept) **plus** the author-time **O↔C consistency check**. **No table/column DDL, no migration, no data change, no DB trigger.** The persisted-shape change is to the `contract_json` JSONB **body grammar** (new `observation-v2` meta-schema), governed here. Grounding: `observation-field-semantic-identity-study-2026-06-07.md`; decision: `docs/adrs/ADR-4a17e0.md`. **This document proposes; it applies nothing.** DO1–DO6 are **LOCKED (2026-06-08)** — see §10; the §11 source-agnosticism guardrail is locked. The ADR DEC-4a17e0 remains the decision of record; this DBCP is the locked implementation plan, **not yet built**.

## 1. Decision recap (ADR-locked — O-A1/O-B/O-C1/O-D/O-E/O-F)

- **O-A1** — an OC field-map entry carries one governed `business_concept.concept_id` (identity, the same anchor D430's CC field and the MC variable binding use → join is `concept_id = concept_id`).
- **O-B** — the binding lives **in the OC field-map entry** (the OC declares it; symmetric with D430's B1).
- **O-C1** — **author-time O↔C consistency check is REQUIRED**: if a Canonical Contract field is sourced from an Observation Contract field, their `business_concept_id` MUST match — enforced at canonical authoring (SERVICES-ONLY). This makes a canonical field's concept claim **provable from source**, not merely asserted.
- **O-D** — legacy/archived OCs are **not migrated** (greenfield; the 95 free-string active versions are preserved).
- **O-E** — store `concept_id` (identity) **plus** a frozen `representation_term`/`unit`/`data_type` snapshot (drift defense); `business_field_code` is demoted to an **optional label** / back-compat display field, **not** semantic authority.
- **O-F** — sequenced **after** D430's CC change (now merged). The combined OC+CC ARPI slice is the first full **O→C→M** concept-identity proof.

## 2. Live substrate grounding (read-only, 2026-06-08)

| Surface | Fact | Source |
|---|---|---|
| `observation-v1.schema.json` `body.field_mappings` item | required `["business_field_code","source_table","source_field","transform"]`; `additionalProperties:false`; body "all fixed (D233)"; envelope const `$contract: barecount/observation/v1` | meta-schema |
| OC field-map entry today | `{transform, source_field, source_table, business_field_code}` — `business_field_code` is a **free string**, zero FK/code path to `concept_registry` | study |
| Active OCs | headers **0 active** / versions **95 active** (free-string `business_field_code`; SAP corpus) — greenfield only; parent/version desync is a separate follow-up | study |
| OC→CC linkage today | by **name string** in legacy `canonical_mapping_version.mapping_json.field_resolutions[].observation_contract` — **not** a uuid, **not** a concept. (DEC-02f5a9 eliminated the Canonical Mapping; the new check is identity-equality, not this legacy linkage.) | study |
| D430 (on main) | `canonical-v2` grammar + `CanonicalConceptResolverService` (resolver + CS-2 authoring + CS-4 activation, fail-closed); `concept_registry.business_concept` carries the E2 triple | merge `a3d41ea` |
| `contract.service.ts` OC activation | the observation block checks the 7 required body keys (structural). No field→concept gate yet. | source |

### 2a. ⚠ Anchor reconciliation — use the ACTIVE successors (same as D430)

ADR-4a17e0 item 8 and the study list the ARPI OC concepts as `a42d3fc0` (amount) / `095afe86` (identifier) / `d05f24b3` (date). As established by the D430 DBCP (§2a), **these three are now `superseded`** — BCF supersession re-minted them. The **active successors** (same `(entity, characteristic)` pairs, entity `e3963e45`) are:

| ARPI source field | concept (active) | repr / unit / type |
|---|---|---|
| `NETWR` (amount) | **`1a2ac2f2`** | amount / null / decimal |
| `VBELN` (identifier) | **`51482979`** | identifier / null / string |
| `FKDAT` (date) | **`61e19048`** | date / null / date |

The OC slice (§6) declares the **active** anchors — identical to the D430 CC slice — so the O↔C check holds. Per your instruction this DBCP uses the active anchors, not the ADR-listed superseded ones. The full O→C→M proof still requires the ARPI MC bound to these active anchors (a governed **new MC version**, D430 O2 precondition — separate track).

## 3. Change set (proposed — nothing applied here)

### CS-1 — Observation grammar (repair-location **B**; O-A1/O-E) · new immutable `observation-v2` grammar
Mirror D430's O1: add **`src/registry/meta-schemas/observation-v2.schema.json`** — `$id: …/observation/v2`, envelope const `$contract: barecount/observation/v2`, identical to v1 except `body.field_mappings.items`:

```jsonc
"items": {
  "type": "object",
  "required": ["business_concept_id", "source_table", "source_field", "transform", "representation_term", "data_type"],
  "additionalProperties": false,
  "properties": {
    "business_concept_id":  { "$ref": "#/$defs/uuid", "description": "O-A1: the governed business_concept.concept_id this source field carries — semantic authority" },
    "business_field_code":  { "type": "string", "description": "O-E: optional label / back-compat display only — NOT semantic authority" },
    "source_table":         { "type": "string" },
    "source_field":         { "type": "string" },
    "transform":            { "type": "string", "enum": ["direct","date_iso8601","currency_normalise","boolean_flag","code_lookup"] },
    "role":                 { "type": "string", "description": "Role distinction (DEC-02f5a9: 'one source field to one Business Concept together with role'); REQUIRED only to disambiguate when one source_field maps to >1 Business Concept (see §11.6)" },
    "representation_term":   { "type": "string", "description": "O-E: frozen snapshot COPIED FROM THE BCF CONCEPT's representation_term — never the physical source field type (§11.5)" },
    "unit":                 { "type": ["string","null"], "description": "O-E: frozen snapshot copied from the BCF concept's unit (nullable) — never the source field type (§11.5)" },
    "data_type":            { "type": "string", "description": "O-E: frozen snapshot copied from the BCF concept's data_type — never the source field type (§11.5)" }
  }
}
```
`business_field_code` moves from **required** to **optional** (O-E demotion). The new **optional `role`** field carries the role distinction the contract-grammar requires for a source_field that maps to more than one concept (§11.6). `observation-v1` stays **unchanged** and **non-polymorphic** — the 95 free-string active versions remain valid under v1 (O-D). Register `observation-v2` in the `seed-registry-full` `META_SCHEMAS` list (code) — **the `contract_meta_schema` v2 row seeds at apply, not in this PR** (mirror D430). The validator already selects by envelope `$contract`. **Snapshot provenance (§11.5):** the three snapshot fields are copied from the BCF concept at author time, never from the source field's physical type.

### CS-2 — OC authoring/activation field integrity (repair-location **B**; O-A1/O-E; fail-closed) · new `ObservationConceptResolverService`
Mirror `CanonicalConceptResolverService`: a registry-layer, read-only service over the shared control-plane connection. `assertObservationFieldIntegrity(body)`: for each `field_mappings` entry — `business_concept_id` is an **active** concept; all entries' concepts share **one entity** (the OC's grain); **concept-unique** within `field_mappings`; frozen snapshot **equals** the live BCF concept's `representation_term`/`unit`/`data_type` — verified against the **concept, never the source field type** (drift **REFUSES**, §11.5); and if one `source_field` appears in more than one entry (mapping to >1 concept), each such entry MUST carry a **distinct `role`**, else **refuse** (§11.6). Wired into:
- `ContractService.createVersion` for `category==='observation' && $contract===barecount/observation/v2` — **fail-closed** when the resolver is unavailable (apply the D430 CS-2 lesson from the start: never author a v2 body without the check).
- `ContractService.transitionState` (activation) for `category==='observation'` v2 bodies — extend the existing OC structural gate with the field→concept integrity check; fail-closed when the resolver is unavailable.

### CS-3 — O↔C consistency check (repair-location **B/C**; O-C1) · extend the canonical gate
This is the keystone. **Interpretation of O-C1 under DEC-02f5a9 (mapping eliminated → identity-equality):** for each canonical-v2 `field_selection` concept, require that an **active observation-v2 OC declares the same `business_concept_id`** in its `field_mappings`. Because a concept_id intrinsically carries its `entity_id`, "for the same grain entity" is automatic (D430 already asserts the CC's concepts belong to its grain entity). So the check is **concept-mediated**: *at least one active OC-v2 mapping must declare the canonical field's concept as observable from a source* — making the claim provable-from-source. **No per-field source pointer is added to the canonical-v2 grammar (D430 stays unamended).**
- New `ObservationConceptResolverService.isConceptObservableFromSource(businessConceptId): Promise<boolean>` (true iff ≥1 active observation-v2 `field_mappings` entry declares the concept).
- `CanonicalConceptResolverService.assertCanonicalFieldIntegrity` (D430) gains an O↔C clause **or** the canonical gate calls the observation resolver: each CC concept must be declared observable from a source by at least one active OC-v2 mapping, else `ForbiddenException` (fail-closed). Enforced at **CC authoring (createVersion)** and **CC activation (transitionState)** — extends, does not replace, D430's checks.
- **Sequencing consequence:** a canonical-v2 CC cannot author/activate until an active observation-v2 OC declares its concepts. For ARPI: author+activate the OC slice **before** the CC slice. (This couples the existing D430 CC gate to OC presence — see open item DO3.)
- **Agnosticism (locked, §11):** the check asserts **concept identity, not OC identity** — it does not bind the CC to that OC, source system, or source field. It is an **authoring/provability gate** ("at least one active OC-v2 mapping declares this concept as observable from a source"), **not** a runtime source-selection rule. Runtime evaluation still resolves through the selected tenant/source Observation Contract path at the admission boundary (no runtime coupling added).

### CS-4 — module wiring + tests
Register `ObservationConceptResolverService` in `ContractModule` (provider + export); inject (optional) into `ContractService` alongside `CanonicalConceptResolverService`. Tests mirror D430: an `observation-concept-resolver.service.spec.ts` (active/drift/unique/multi-entity/observable-from-source lookup) + `contract.service.createVersion`/`transitionState` cases for OC-v2 authoring/activation fail-closed and the CC-side O↔C refusal.

## 4. Why no DDL (scope fidelity)
The ADR scopes D431 to **B (grammar) + read-only governance at C (the O↔C check)**, explicitly not D/E/F. `field_mappings` persists in `contract_json` JSONB, so identity rides the existing column — **no new table/column, no migration, no Drizzle change.** OC grain entity is derived from the field_mappings concepts (no `entity_id` column), mirroring D430.

## 5. Database Change Protocol classification
- **No DDL, no migration file, no Drizzle edit, no table/column/index/constraint change, no DB trigger, no data write.**
- Governance-significant change = the **new `observation-v2` meta-schema** (defines the shape of data later persisted in `contract_json`; v1 retained unchanged). A contract-grammar version add, governed by this DBCP + DEC-4a17e0 — **not** a DDL change. The `contract_meta_schema` v2 row is an **apply step** (mirror D430; not in the PR). Archived v1 OC bodies remain valid (O-D).

## 6. ARPI OC slice (greenfield) + preconditions
1. **Precondition A (grammar live):** the `observation-v2` **and** `canonical-v2` meta-schema rows must be seeded (apply step — D430's v2 row is also not yet seeded). Until then, neither v2 body validates.
2. **Precondition B (active anchors / MC rebind):** the ARPI MC must bind the **active** successors `1a2ac2f2`/`51482979`/`61e19048` via a governed **new MC version** (D430 O2, separate track).
3. Author **one greenfield active Customer Invoice OC-v2** (entity `e3963e45`) via the SERVICES-ONLY path, `field_mappings` declaring: `NETWR→1a2ac2f2`, `VBELN→51482979`, `FKDAT→61e19048` (each with source_table, transform, frozen snapshot).
4. Author+activate the D430 greenfield **Customer Invoice CC-v2** (same three active concepts). The CS-3 O↔C check passes (each CC concept is now declared observable from a source by the OC slice).
5. Re-run the ARPI synthesis proof → with O (NETWR/VBELN/FKDAT → concepts) ∧ C (canonical fields → concepts) ∧ M (variables → concepts) all sharing `concept_id`, this is the **first full O→C→M concept-identity proof** for ARPI.

## 7. Foundation gate
- **Repair location: B (Observation contract semantics)** — the OC field-map declares its governed concept by identity. `source_field`/`source_table`/`transform` stay **A** (legitimately physical). The O↔C check is **read-only governance at C**.
- **Q1 — why here:** admission is where the source→concept reference is anchored once (Invariant I); today it anchors a free string (Invariant IV unmet). 
- **Q2 — why not upper layers:** A (source) is physical and correct; B is the layer being specified.
- **Q3 — why not lower layers:** name-only `business_field_code` + the legacy Canonical Mapping are C-layer compensation for the absent B identity; fixing B removes it. No engine hack, no DDL, no read filter.
- **Hard rules:** no lower-layer compensation; **no DB row hand-edits** — greenfield OC via SERVICES-ONLY authoring; **reads don't trigger evaluation** (resolvers read-only); the O↔C check is author/activation-time governance, not a read-time evaluation (O-C1 chosen over the runtime-gate O-C2 for exactly this reason).
- **Invariants:** I (meaning anchored at the admission boundary); IV (explicit references — concept identity replaces the free string); III + grammar immutability (Step 1) — new OC-v2 authored with identity then frozen; v1 bodies preserved (O-D).

## 8. Out of scope
Canonical-v2 / observation-v2 meta-schema **row seeding** (apply step); greenfield OC or CC authoring; the ARPI MC new-version rebind (O2, separate track); MCF materialization (Step 5); legacy OC migration (O-D); the 0-active-headers/95-active-versions parent/version desync (separate governance follow-up); any `entity_id` projection / DDL; amending D430's canonical-v2 grammar (sibling, not amending); runtime O↔C gate (O-C2 deferred).

## 9. PR shape (after lock)
Branch off `main` → CS-1 (`observation-v2` meta-schema + seeder registration) + CS-2 (`ObservationConceptResolverService` + OC-v2 authoring/activation fail-closed) + CS-3 (O↔C check wired into the canonical authoring + activation gate) + CS-4 (module wiring + tests) → gates (tsc/eslint/vitest) → open PR **holding**. The OC/CC greenfield authoring + ARPI MC rebind + re-run are **separate** post-merge steps.

## 10. Locked decisions DO1–DO6 (operator lock 2026-06-08)

**All six are LOCKED as the recommended option**; the §11 guardrail is likewise locked. The bullets keep their original proposal rationale — the lock adopts each recommendation (the "Confirm…" framing is historical).
- **DO1 — grammar-versioning.** New immutable `observation-v2` file (recommended — mirror D430 O1; `observation-v1` unchanged + non-polymorphic). Confirm vs version-gating v1.
- **DO2 — O↔C check semantics (the keystone).** Concept-mediated **identity-equality** (each canonical-v2 concept must be declared by an active observation-v2 OC) — **recommended**, faithful to DEC-02f5a9 (mapping eliminated). Confirm vs adding an explicit per-field source pointer to the canonical grammar (rejected — would amend the locked D430 v2).
- **DO3 — O↔C fail-closed coupling.** Fail-closed: a canonical-v2 CC cannot author/activate until its concepts are declared observable from a source by an active OC-v2 (recommended; matches O-C1 "REQUIRED"). **Implication:** D430's CC activation gate gains an OC-presence dependency, so the ARPI CC can't activate before the ARPI OC-v2 is active. Confirm the sequencing coupling is acceptable.
- **DO4 — `business_field_code` demotion.** Make it **optional** (label / back-compat) in observation-v2 per O-E. Confirm.
- **DO5 — OC grain-entity derivation.** Derive the OC's grain entity from its field_mappings concepts (no `entity_id` column / DDL; mirror D430 O3). Confirm.
- **DO6 — check placement.** O↔C check at CC **authoring + activation**; OC field integrity at OC **authoring + activation** — both in the generic `ContractService` path (the ADR's "canonical onboarding service" maps to this, as D430 established no dedicated onboarding service exists). Confirm.

## 11. Source-agnosticism guardrail (LOCKED for implementation — tightens DO2/DO3)

The O↔C check is source-agnostic **at the contract-grammar level**. These invariants are binding on CS‑1/CS‑2/CS‑3 and MUST hold; they are **locked**, not open:

1. **CC stays source-agnostic.** A canonical-v2 `field_selection` entry references a Business Concept only — never a `source_field`, `source_table`, source system, provider, tenant, or OC identity. (D430 already so; D431 adds none.)
2. **OC remains source-specific.** The Observation Contract is the one boundary that names a source (`source_table` / `source_field` / `transform`). All source-specificity is confined here (DEC-02f5a9 §5: "a source field is not vocabulary — it is bound to a concept at the admission boundary").
3. **O↔C consistency is concept identity, not OC identity.** The CC-side check asserts only that the concept is declared by **at least one** active observation-v2 mapping — proving the concept is *observable from source*. It does **not** bind the CC to that OC, that source system, or that source field. "At least one active OC-v2 mapping declares this concept as observable from a source" is an **authoring/provability gate**, never a runtime source-selection rule.
4. **Runtime is unchanged.** Evaluation still resolves through the **selected tenant/source Observation Contract path** at the admission boundary. D431 adds no runtime source-selection coupling and no read-time evaluation (O-C1 is author/activation-time; the O-C2 runtime gate stays deferred). A second source system onboards via its **own** OC mapping its **own** columns to the **same** `concept_id`, with **no** CC/MC edit (cross-system portability).
5. **Snapshot provenance.** OC and CC frozen snapshots (`representation_term` / `unit` / `data_type`) are **copied from the BCF concept** at author time — **never** from the physical source field's type. A source-derived snapshot would silently reintroduce source-specificity and is forbidden; the integrity check verifies the snapshot against the **concept** (drift → refuse).
6. **Source-field / role distinction.** If one `source_field` maps to more than one Business Concept within an OC's `field_mappings`, each such entry MUST carry a **distinct declared `role`** (observation-v2 adds the optional `role` field, CS‑1); absent a role distinction, **refuse** — the contract-grammar disallowed behavior: "an Observation Contract maps the same source field to multiple Business Concepts without a declared role distinction."

These six are the load-bearing guarantees that keep the metric chain portable across source systems while making the canonical concept claim provable-from-source.
