---
title: "D430 Canonical Field Semantic Identity — implementation change proposal (grammar + resolver; NO DDL)"
description: Implementation proposal for DEC-a6258b/D430 (D429 Step 2). Adds a new canonical grammar version whose field_selection entry declares canonical_field + one governed business_concept.concept_id (A1, pure — no lineage-aware resolver) + a frozen representation_term/unit/data_type snapshot (E2); v1 (string[] field_selection) retained read-only for archived bodies; adds a read-only (grain_entity_id, business_concept_id) → (canonical_contract_version, canonical_field) resolver (B1/C1); replaces the D433 canonical fail-closed activation stub with the real field→concept integrity check that REFUSES on snapshot drift; proves it with one greenfield Customer Invoice Canonical Contract after the ARPI MC bindings are governed-rebound to active successors. Meta-schema + service + resolver + tests only; NO table/column DDL, NO migration, NO data change; legacy CCs not migrated (D1); no D431; no MCF materialization.
status: draft
date: 2026-06-08
project: bc-core
domain: contracts
subdomain: canonical-identity
focus: schema
---

# D430 Canonical Field Semantic Identity — change proposal (grammar + resolver)

> Implements **DEC-a6258b / D430** (D429 **Step 2**). Scope = the deferred "schema-level key naming" from DEC-02f5a9, at the **Canonical Field side only**. **No table/column DDL, no migration, no data change, no DB trigger.** The persisted-shape change is to the `contract_json` JSONB **body grammar** (canonical meta-schema), governed here. Grounding: `canonical-field-semantic-identity-study-2026-06-07.md`; decision: `docs/adrs/ADR-a6258b.md`. **This document proposes; it applies nothing.** The implementation open items **O1–O4 are LOCKED (2026-06-08)** — see §1a and §10. The ADR DEC-a6258b remains the decision of record; this DBCP is the locked implementation plan, **not yet built (held)**.

## 1. Decision recap (ADR-locked — A1/B1/C1/D1/E2/F1)

- **A1** — a canonical field carries exactly ONE primary governed `business_concept.concept_id` (the same key `mcf.metric_variable_binding.bound_business_concept_id` uses).
- **B1** — the concept→field binding lives **in the Canonical Contract field declaration**, not a side table, not MCF.
- **C1** — runtime resolution is deterministic under *one active CC per grain entity* + *each concept at most once per CC*.
- **D1** — archived legacy CCs are **not migrated** (immutable preserved state; 0 active CCs today).
- **E2** — store `concept_id` (identity) **plus** a frozen `representation_term`/`unit`/`data_type` snapshot (drift defense, never identity).
- **F1** — Observation-side concept binding is **deferred** (D431, separate). Canonical-side proof only — **not** a full O→C→M proof.

## 1a. Operator decisions incorporated into this proposal (2026-06-08 — implementation decisions; ADR unchanged)

1. **A1 stays pure `business_concept.concept_id`.** The runtime resolver is **not** lineage-aware. If a Metric Contract binding points to a **superseded** concept_id, it must be governed to the active successor via a **new Metric Contract version before proof** (not an in-place binding update). Concept lineage may be **advisory only** (display/audit) — **never** a runtime match key.
2. **ARPI proof precondition** — the ARPI MC bindings currently point to superseded concepts; a governed **new Metric Contract version** binding to the **active successors** (amount `1a2ac2f2`, identifier `51482979`, date `61e19048`) is required **before** the O→C→M proof.
3. **Archived `canonical-v1` bodies are never retroactively invalidated** — introduce a **new canonical grammar version**; archived CCs with `field_selection: string[]` remain valid/readable as **historical grammar**.
4. **New canonical field entry shape** = `canonical_field` name + `business_concept_id` + `representation_term` + `unit` + `data_type` (the last three frozen snapshots, E2).
5. **Snapshot drift on activation → REFUSE** (not warn): concept_id active but `representation_term`/`unit`/`data_type` differs from the stored snapshot ⇒ activation **fails**.
6. **C1 enforced at authoring/activation:** active concept only · concept belongs to the CC grain entity · one active CC per grain entity (deterministic resolver) · concept unique within the CC.
7. **O1 — new immutable `canonical-v2` grammar file.** `canonical-v1` stays **unchanged** for archived/historical bodies and is **not** made polymorphic (no `string|object` union in v1).
8. **O2 — ARPI rebind is a governed new Metric Contract version**, not an in-place binding update; the existing MCV stays **historical**.
9. **O3 — one active Canonical Contract per grain entity** is enforced by a **code-level activation guard that reads active CC bodies**. No `entity_id` projection / DDL in this step.
10. **O4 — the validator/meta-schema is selected by the envelope `$contract`**, not by header semver.

## 2. Live substrate grounding (read-only, 2026-06-08)

| Surface | Fact | Source |
|---|---|---|
| `canonical-v1.schema.json` `body.field_selection` | `array<string>`, `x-governance: fixed`; body `additionalProperties:false`, "entirely fixed (D233)"; envelope const `$contract: barecount/canonical/v1` | meta-schema |
| `contract.canonical_contract` (header) | **no `entity_id` column**; grain/entity carried as `business_object_code` (string) + `grain[]` in the body | `pg_describe_table` |
| `contract.canonical_contract_version` | `contract_json jsonb` holds `field_selection`; `governance_state_code`; immutable post-publish (Step 1) | `pg_describe_table` |
| `concept_registry.business_concept` | `concept_id` PK, `entity_id` NOT NULL, `characteristic_id`, **`representation_term`/`unit`/`data_type`** (= the E2 triple), `lifecycle_state`, `active_version_id` | `pg_describe_table` |
| Active CCs | **0** (all 56 headers archived Apr–May 2026) → greenfield only | study |
| `mcf.metric_variable_binding` | `bound_business_concept_id` (uuid→BCF), `bound_entity_id`, `*_snapshot` triple — the **MC-side analog** D430 mirrors on the CC side | study |
| **D433 canonical activation gate** | `contract.service.ts:517–531` throws fail-closed; comment: *"canonical field→concept integrity gate is delivered by D430 (DEC-a6258b)… fail-closed until then."* | source |

### 2a. ⚠ ARPI anchors are superseded — proof precondition (decision §1a.1/§1a.2)

The study (2026-06-07) recorded the three ARPI MC variable bindings against `a42d3fc0` (amount), `095afe86` (identifier), `d05f24b3` (date). **As of 2026-06-08 all three are `lifecycle_state='superseded'`.** BCF supersession **minted new `concept_id`s**; the `(entity, characteristic)` pairs are stable:

| ARPI role | study anchor (now superseded) | characteristic | **active successor anchor** | snapshot (repr / unit / type) |
|---|---|---|---|---|
| numerator_source | `a42d3fc0` | `8f495603` | **`1a2ac2f2`** | amount / null / decimal |
| denominator_key | `095afe86` | `40433e4f` | **`51482979`** | identifier / null / string |
| temporal_anchor | `d05f24b3` | `338c601a` | **`61e19048`** | date / null / date |

BCF supersession does **not** keep `concept_id` stable across supersession (it re-mints). Per **decision §1a.1**, A1 stays pure and the resolver is **not** lineage-aware; therefore the ARPI MC bindings must be moved to the active successors via a **governed new Metric Contract version before the proof** (decisions §1a.2/§1a.8 — not an in-place binding update; the existing MCV stays historical). A pure `concept_id = concept_id` match against a CC declaring the active anchors will correctly return **no match** until that new MC version lands — expected behavior, not a resolver bug.

## 3. Change set (proposed — nothing applied here)

### CS-1 — Grammar (repair-location **B**) · new canonical grammar version
Per **decision §1a.3**, do **not** mutate `canonical-v1.schema.json` in place (that would invalidate archived string[] bodies). Instead:

- **Add `src/registry/meta-schemas/canonical-v2.schema.json`** — `$id: …/canonical/v2`, envelope const `$contract: barecount/canonical/v2`, identical to v1 except `body.field_selection.items`:

```jsonc
"items": {
  "type": "object",
  "required": ["canonical_field", "business_concept_id", "representation_term", "data_type"],
  "additionalProperties": false,
  "properties": {
    "canonical_field":     { "type": "string" },          // CO output column (== a resolved_schema property)
    "business_concept_id": { "$ref": "#/$defs/uuid" },    // A1 identity → concept_registry.business_concept.concept_id
    "representation_term": { "type": "string" },          // E2 frozen snapshot
    "unit":                { "type": ["string","null"] }, // E2 frozen snapshot — nullable (null for the ARPI three)
    "data_type":          { "type": "string" }            // E2 frozen snapshot
  }
}
```
- **Retain `canonical-v1.schema.json` unchanged** (string[] `field_selection`) as **historical grammar** — **not** made polymorphic (O1). The meta-schema validator **selects the schema by the envelope `$contract`** (O4): legacy `barecount/canonical/v1` bodies validate against v1 (remain valid/readable); new CCs are authored under `barecount/canonical/v2`. Archived bodies are never re-validated against v2 and never rewritten (D1, Step-1 immutability).

  **Locked (O1/O4):** `canonical-v2` is a new **immutable** file; v1 stays unchanged and **non-polymorphic** (no `string|object` union); validation is keyed on the envelope **`$contract`**, never header semver. Blast-radius: every hardcoded `barecount/canonical/v1` const (envelope builder, family/category detection, validator registry) must learn v2 — enumerated in the implementation PR.

### CS-2 — Authoring validation (repair-location **B/C**, SERVICES-ONLY, C1 = decision §1a.6) · canonical authoring/synthesis path
At the canonical contract_json build/author path (the `canonical` family write via `ContractVersionRepository.createVersion` + the envelope/synthesis builder — **exact service method pinned in the PR; never a raw INSERT**), enforce on each `field_selection` entry:
1. `business_concept_id` resolves to an **active** `concept_registry.business_concept` (C1);
2. that concept's `entity_id` = the **CC's grain entity** (C1);
3. **concept-unique** within `field_selection` (C1);
4. freeze `representation_term`/`unit`/`data_type` from the concept's live values at author time (E2);
5. `canonical_field` matches a `resolved_schema` property (existing consistency rule, retained).

### CS-3 — Resolver (repair-location **C**, read-only, NEW, pure A1 = decision §1a.1) · `src/registry/…` (registry layer)
`CanonicalConceptResolver.resolve(grainEntityId, businessConceptId) → { canonicalContractVersionId, canonicalField } | null`:
- load active `canonical_contract_version`(s); select the one whose grain entity = `grainEntityId` (C1 ⇒ exactly one);
- within its body `field_selection`, select the entry whose `business_concept_id = businessConceptId` (C1 ⇒ at most one);
- return its `canonical_field`, else `null`.

**Pure `concept_id` match — no lineage traversal** (decision §1a.1). Pure read of the immutable `contract_json` body (whole-row fetch + in-app match) — **no SQL filter into JSONB**, consistent with DB Rule 1. **Reads do not trigger evaluation.** Distinct from `boundary/canonical-resolution.service.ts → resolveField()` (a payload getter).

### CS-4 — Activation gate (enforcement of C; drift = REFUSE per decision §1a.5) · `src/registry/contract.service.ts:517–531`
Replace the D433 unconditional fail-closed `throw` for `category === 'canonical'` with the **real field→concept integrity check**, run across the version's `field_selection`:
- every entry's `business_concept_id` is an **active** concept on the CC's **grain entity** (C1);
- **concept-unique** within the CC (C1); and the CC is the **only active CC for its grain entity** (C1 — read active CC bodies to detect a grain collision; no DDL);
- **snapshot equality (REFUSE on drift, §1a.5):** the entry's frozen `representation_term`/`unit`/`data_type` **equals** the live concept's values; **any difference ⇒ `ForbiddenException`** (activation fails), even when the concept_id is active.

All pass ⇒ allow activation. Any fail ⇒ `ForbiddenException` naming the offending field/concept. Fail-closed remains the default for malformed CCs; the dead-signal IntegrityService path stays retired.

## 4. Why no DDL (scope fidelity)
The ADR scopes D430 to **B (grammar) + read-only C (resolver)**, explicitly **not D/E/F**. `field_selection` persists in `contract_json` JSONB, so identity rides the existing column — **no new table/column, no migration, no Drizzle change.** An `entity_id` projection column on `canonical_contract` (an E/storage change for query speed) is **out of scope**; with 0→few active CCs the body read (incl. the C1 grain-collision check) is trivial. Revisit only if many active CCs make the scan a real cost (future, separate DBCP).

## 5. Database Change Protocol classification
- **No DDL, no migration file, no `docker/redesign/*.sql`, no Drizzle edit, no table/column/index/constraint change, no DB trigger, no data write.**
- Governance-significant change = the **new `canonical-v2` meta-schema** (it defines the shape of data later persisted in `contract_json`; v1 retained unchanged). A **contract-grammar version add**, governed by this DBCP + DEC-a6258b — **not** a schema/DDL change under the DB Change Protocol's DDL clause. Archived v1 bodies remain valid (decision §1a.3).

## 6. ARPI proof slice (greenfield) + precondition
1. **Precondition (gating, separate track, decisions §1a.2/§1a.8):** author a **governed new Metric Contract version** binding the ARPI variables to the **active successors** — amount `1a2ac2f2`, identifier `51482979`, date `61e19048`. **Not** an in-place rebind; the existing MCV stays historical. Until this lands, the resolver correctly returns no match.
2. Author **one greenfield active Customer Invoice CC** (grain entity `e3963e45`) under `barecount/canonical/v2` via the SERVICES-ONLY path, `field_selection` declaring the three concepts by their **active anchors** (`1a2ac2f2`/`51482979`/`61e19048`), each with `canonical_field` + resolution rule + frozen snapshot.
3. Resolver (CS-3) resolves each ARPI MC variable's bound (now-active) concept → the CC field. Re-run the ARPI synthesis proof; the three `UNRESOLVED@C` bindings resolve → an evaluation-grade `contract_json` becomes synthesizable. Concrete unblock for **D429 Step 5** (ARPI only) — once the Observation side (D431) also lands for a full O→C→M proof.

## 7. Foundation gate
- **Repair location: B (grammar)** primary + **C (resolver + the field→concept integrity check enforced at activation)**. Explicitly **not A** (source/observation = D431, deferred), **not E** (no storage/DDL), **not F** (no read-model patch), **not the MCF/Metric Contract layer** (no MCF-invented mapping).
- **Q1 — why here:** canonical meaning must be anchored at the canonical boundary (Invariant I); the field grammar is where a field declares its concept; today it anchors nothing (X2).
- **Q2 — why not upper layers:** B *is* the upper layer being fixed; A (observation/source) is the sibling D431, deferred (F1). B is being specified, not left underspecified.
- **Q3 — why not lower layers:** name-only resolution + hand-typed `co_bindings` are exactly C/D **compensating** for absent B identity; fixing B removes the compensation. No engine hack, no DDL, no read filter.
- **Hard rules:** no lower-layer compensation; no fact-shape-tied formulas (N/A); **no DB row hand-edits** — greenfield CC via SERVICES-ONLY authoring; **reads don't trigger evaluation** (resolver read-only); **Foundation-stop honored** — the superseded-anchor finding is surfaced as a precondition, not worked around (decision §1a keeps A1 pure rather than bending the resolver).
- **Invariants:** I (meaning anchored at boundary) — the point; III + grammar immutability (Step 1) + decision §1a.3 (archived v1 bodies preserved) — history is never rewritten; VI — unchanged.

## 8. Gates / rollback
- `tsc` (changed files) + `eslint` (changed src) + focused `vitest`: v2 meta-schema validation (object `field_selection` accepted; v1 string bodies still validate under v1); authoring validation (active-concept + grain-match + concept-unique + snapshot-freeze, C1); resolver determinism (hit / no-match / pure-concept_id, no lineage); activation gate (pass on valid CC; **refuse on snapshot drift**; refuse on inactive/foreign/duplicate concept; refuse on second active CC for a grain entity).
- **Rollback** = `git revert` (code + meta-schema only; nothing in the DB). Reverting restores the D433 fail-closed stub (CS-4) — canonical activation returns to refuse-by-policy, the safe state. v1 bodies are untouched throughout.

## 9. Out of scope
D431 / Observation-side binding (F1); OC→concept; legacy CC migration (D1); MCF materialization (Step 5); `entity_id` projection column / any DDL (O3); making `canonical-v1` polymorphic (O1 forbids it); lineage-aware runtime resolver (decision §1a.1 forbids it; lineage advisory-only); the ARPI MC new-version rebind itself (precondition, separate track — O2/§1a.8); generalization beyond the one Customer Invoice entity.

## 10. Locked decisions O1–O4 (2026-06-08)
All four open items are now **locked**; **no open items remain.** With §1a.1–6 already incorporated, the implementation shape is fully specified — the DBCP is a complete, locked plan (not yet built; held).

- **O1 — LOCKED:** introduce a new **immutable** `canonical-v2` grammar file; keep `canonical-v1` **unchanged** for archived/historical bodies; v1 is **not** made polymorphic (no `string|object` union).
- **O2 — LOCKED:** the ARPI rebind is a **governed new Metric Contract version**, not an in-place binding update; the existing MCV stays **historical**.
- **O3 — LOCKED:** enforce **one active Canonical Contract per grain entity** with a **code-level activation guard that reads active CC bodies**; **no** `entity_id` projection / DDL in this step.
- **O4 — LOCKED:** select the validator/meta-schema by the envelope **`$contract`**, **not** by header semver.

## 11. PR shape (after lock)
Branch off `main` → CS-1 (`canonical-v2` immutable meta-schema + `$contract`-keyed validator selection, O1/O4) + CS-2 authoring validation (C1) + CS-3 resolver (pure A1) + CS-4 activation-gate replacement (drift = refuse, grain-collision guard O3) + tests → gates → open PR **holding** (no merge). The ARPI MC new-version rebind (precondition, O2) and the greenfield CC authoring + ARPI re-run are **separate** steps after merge.
