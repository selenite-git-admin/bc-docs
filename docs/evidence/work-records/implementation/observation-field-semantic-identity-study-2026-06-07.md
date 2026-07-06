---
title: "Observation-Field Semantic Identity — grounded ADR/study (read-only)"
description: The Observation-side half of canonical/observation field semantic identity — the old Business Field role after DEC-02f5a9 collapsed Business Field + Canonical Field into one Business Concept. An Observation Contract field-map entry must bind one source field to a governed business_concept.concept_id; today business_field_code is a free string and insufficient. Complements the canonical-side decision DEC-a6258b/D430. Full chain proof requires Observation + Canonical + Metric Contract all sharing concept_id. Read-only options study; answers six questions with options + a recommendation; authorizes no code, schema, DB write, migration, ADR, or panel — held for operator lock.
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: observation-identity
focus: foundation-implementation
---

# Observation-Field Semantic Identity — options study (read-only)

> **What this is.** The grounding study for the **Observation-side** half of field semantic identity — the next architecture item after DEC-a6258b/D430 (which covered the **Canonical** side only). It is the **old Business Field role** (DEC-d72560) after **DEC-02f5a9** collapsed Business Field + Canonical Field into one Business Concept. It **authorizes nothing**: no code, schema, DB write, migration, ADR file, or panel. The eventual ADR is filed only after the operator locks the decisions below.
>
> **Why now.** D430 makes a Canonical Contract field carry `business_concept.concept_id`. But the canonical field's concept claim is currently *asserted by the CC author*, not *proven from the source*, because the Observation Contract — the admission-boundary artifact that maps a source field to business meaning — still uses a **free-string `business_field_code`** with no concept identity. Closing this makes the chain's concept identity provable end to end.
>
> **Method.** Foundation grammar (`the-contract-grammar.md` §Observation Contract, §Vocabulary; `the-evaluation-boundaries.md` §Admission boundary) read first-hand; this session's contract-governance audit (Observation finding) reused; live `bc_platform_dev` OC substrate + meta-schema inventoried read-only (2026-06-07).
>
> **Decision status (2026-06-07): LOCKED — O-A..O-F as proposed.** Recorded in the **sibling** Observation-side ADR (filed alongside; D430 is **not** amended or combined). ADR scope = grammar + consistency-check decision only; the `observation-v1` meta-schema change + author-time O↔C check + greenfield ARPI OC slice are deferred to a later DBCP. `business_concept_id` is the semantic authority; `business_field_code` is kept only as an optional label / back-compat display field. ARPI OC slice = NETWR/VBELN/FKDAT → the same three BCF concepts as the D430 CC slice.

---

## Headline

**The Business Field role is the missing admission-side half of concept identity.** DEC-d72560 split field vocabulary into a source-side **Business Field** (carried by the Observation Contract) and a canonical-side **Canonical Field** (carried by the Canonical Contract), joined by the **Canonical Mapping**. DEC-02f5a9 collapsed both into **one Business Concept** and eliminated the Canonical Mapping — so there is no longer a BF→CF *mapping*, only the requirement that **each boundary declare which concept its field carries**, with runtime joining by **identity equality** (`concept_id = concept_id`).

D430 implemented the **Canonical** declaration. This study scopes the **Observation** declaration. With the Metric declaration already in place (the Metric Contract variable binding references a concept), the three boundaries share one identity:

```
Observation Contract field-map → BCF Business Concept   ❌ (this study)   ← old Business Field role
Canonical Contract field       → BCF Business Concept   ✅ DEC-a6258b/D430 ← old Canonical Field role
Metric Contract variable       → BCF Business Concept   ✅ already (MCF-authored)
```

**Full chain proof = Observation ∧ Canonical ∧ Metric all sharing `concept_id`.** Until the Observation declaration lands, the D430 ARPI slice is a **canonical-side proof only**, not a full O→C→M proof.

---

## The gap (proven, live 2026-06-07)

An Observation Contract field-map entry carries **no** BCF concept identity. Real active-OC entry:

```json
{ "transform": "direct", "source_field": "KUNRG", "source_table": "TYPE_SD_S_MAP",
  "business_field_code": "commercial_invoice_hdr_bill_to_party_identifier" }
```

- Keys present (exhaustive): `transform`, `source_field`, `source_table`, `business_field_code`. **Absent:** `business_concept_id` / `concept_id` / `characteristic_id` / `entity_id`.
- `business_field_code` is a **free string** — no FK to `concept_registry`, no code path maps it to a Business Concept anywhere in bc-core or the DB.
- Meta-schema `observation-v1.schema.json` requires `["business_field_code","source_table","source_field","transform"]`; `transform` enum = `["direct","date_iso8601","currency_normalise","boolean_flag","code_lookup"]`.

**Substrate counts:** `contract.observation_contract` headers = 63 total / **0 active** (`archived_at IS NULL`); `contract.observation_contract_version` = 154 total / **95 active** (`governance_state_code='active'`). *(The 0-active-headers vs 95-active-versions split is the same parent/version governance desync flagged in the audit — a separate follow-up, not in scope here.)*

**OC → CC linkage today:** by **name string** — `contract.canonical_mapping_version.mapping_json.field_resolutions[].observation_contract` carries the OC name (e.g. `"oc__s4hana__type_sd_s_map__invoice_hdr"`), not a uuid and not a concept.

**ARPI-relevant OCs (active):** invoice OCs exist with the three ARPI source fields — e.g. `commercial_invoice_hdr`: `NETWR → …_net_amount` (amount), `VBELN → …_commercial_invoice_number` (identifier), `FKDAT → …_document_date_time` (date) — all with free-string `business_field_code` and no concept binding.

---

## The six questions

### Q1 — What must an Observation Contract field-map entry mean?

**It binds exactly one source field to exactly one governed Business Concept, by identity.** Foundation already says so: under DEC-02f5a9, "each `observation_field_map` entry binds one source field to **one Business Concept** together with role and nullability." The Observation Contract is the admission-boundary artifact that selects source fields into the business vocabulary (Invariant IV — references are explicit). Today the binding target is a free string, so the explicit reference Foundation requires is **not** expressed.

The physical `source_field` / `source_table` / `transform` stay (repair-location A — legitimately physical at admission). The **addition** is the concept identity the field carries.

### Q2 — Bind to what, and how?

**To `business_concept_id` — the same concept anchor the Canonical field (D430) and the Metric variable already use — plus a frozen semantic snapshot.** Symmetric with D430 by design, so the join is `concept_id = concept_id` across all three boundaries.

| Option | Verdict |
|---|---|
| **O-A1 (recommended)** `business_concept_id` (concept anchor uuid) | Identity-equal to D430 + the Metric variable binding → trivial cross-boundary match. Stable across concept-version supersession; frozen by contract-version immutability (Step 1). |
| O-A2 `(entity_id, characteristic_id)` | Redundant — the concept anchor already encodes it; D430 chose the anchor, so match this. |
| O-A3 keep only `business_field_code` (string) | **Reject** — the status quo; not identity (free, collision-prone). |
| **O-E (recommended)** add a frozen `representation_term`/`unit`/`data_type` snapshot | Mirrors D430's E2 and the Metric variable binding's `*_snapshot`; drift defense, not identity. `business_field_code` is demoted to an optional display label (additive — does not break the 95 active versions). |

### Q3 — How does this affect Source → Observation → Canonical → Metric?

**It supplies the admission-side anchor that makes the canonical field's concept claim provable from source.** The concept token now enters at admission (source field → concept), is re-declared at canonical (canonical field → concept), and is consumed at metric (variable → concept) — one identity across three boundaries. The old BF→CF *mapping* stays gone; consistency is **identity equality**, checked, not mapped.

| Boundary | Today | With this study | Change |
|---|---|---|---|
| Source | physical field names | unchanged (A) | none |
| **Observation** | source field → `business_field_code` (string) | source field → `business_concept_id` (+ snapshot) | **the core of this study** |
| Canonical | field → `business_concept_id` (D430) | unchanged | none |
| Metric | variable → `business_concept_id` (MCF) | unchanged | none |

### Q4 — How is O↔C consistency enforced (the new value)?

This is what the Observation declaration *adds*: the ability to prove that a canonical field's declared concept actually comes from a source field carrying that same concept.

| Option | Verdict |
|---|---|
| **O-C1 (recommended)** author-time check in the canonical onboarding service | When a CC field declares concept X and resolves from an OC field, assert that OC field's `business_concept_id == X`. Deterministic, fails closed at authoring (SERVICES-ONLY). |
| O-C2 runtime gate at canonical evaluation | Possible but later/heavier; a read-time check risks coupling reads to evaluation (boundary-independent rule). Defer. |
| O-C3 no check (rely on author discipline) | **Reject** — that is today's "asserted, not proven" state. |

### Q5 — What happens to legacy Observation Contracts?

**Greenfield, mirroring D1 — do not migrate.** 95 active OC versions carry free-string `business_field_code` (the SAP corpus); their parent headers are archived. They are preserved state. New OCs are authored with concept identity; legacy free-string OCs are not backfilled. *(The 0-active-headers/95-active-versions desync is a separate governance follow-up.)*

### Q6 — Minimum ARPI path (pairs with D430)

Bind the **three ARPI Customer Invoice source fields** to their concepts at the Observation boundary, so the D430 greenfield CC's concept claims are source-provable:

1. `NETWR` → concept `a42d3fc0` (amount / numerator_source)
2. `VBELN` → concept `095afe86` (identifier / denominator_key)
3. `FKDAT` → concept `d05f24b3` (date / temporal_anchor)

authored greenfield on the Customer Invoice OC (entity `e3963e45`), via the onboarding service. **Together with D430's CC slice this yields the first full O→C(→M) concept-identity proof for ARPI** — the canonical fields' concepts now provably trace to source fields carrying the same concepts. (The Metric side already binds these three concepts.)

---

## Decision matrix (for operator lock)

| # | Decision | Recommendation |
|---|---|---|
| **O-A** | OC field-map identity key | **O-A1** `business_concept_id` |
| **O-B** | where the binding lives | **in the OC field-map entry** (the OC declares it — symmetric with D430's B1) |
| **O-C** | O↔C consistency enforcement | **O-C1** author-time check in the canonical onboarding service |
| **O-D** | legacy OC treatment | **greenfield, no migration** (mirror D1) |
| **O-E** | identity vs snapshot | **concept_id + frozen representation/unit/type snapshot** (mirror E2); `business_field_code` → optional label |
| **O-F** | sequencing | **after D430's CC change**; the combined OC+CC ARPI proof is the full O→C→M proof |

---

## Foundation gate (for the eventual fix)

- **Repair location: B (contract semantics)** — extend the Observation Contract grammar so a field-map entry declares its governed Business Concept by identity. The `source_field`/`source_table` remain repair-location A (legitimately physical). The author-time O↔C check is read-only governance at C.
- **Invariants:** I (meaning anchored at its boundary — admission declares the source→concept reference once); IV (references are explicit — replaces the free string with a governed identity). III + contract-grammar immutability (Step 1): new OC versions are authored with identity then frozen.
- **No DB row hand-edits; SERVICES-ONLY.** Greenfield OC authoring via the onboarding service; the meta-schema (`observation-v1`) change and the check are a later, explicitly-approved DBCP.

---

## Relationship to D430 and the D429 sequence

This study is the **Observation-side complement to DEC-a6258b/D430** (canonical side). D430 stands as filed; this does not amend it. Together, plus the already-correct Metric binding, they deliver **full O→C→M concept identity by shared `concept_id`**. Sequence within D429: Step 1 (immutability) ✅; Step 2 canonical (D430) decided; **this Observation-side item is the immediate next architecture decision**; Steps 3 (guard legacy metric door), 4 (fix fail-open gates), 5 (resume materialization) follow. MCF materialization remains paused.

## Decisions taken (locked 2026-06-07)

1. **O-A..O-F locked as proposed.** Observation Contract field-map entries carry `business_concept_id` (O-A1), declared in the OC field-map entry (O-B); `business_field_code` is kept only as a label / back-compat display field, **not semantic authority**; identity is `concept_id` + a frozen semantic snapshot for drift defense (O-E).
2. **Author-time O↔C consistency check is required (O-C1):** if a Canonical Contract field is sourced from an Observation Contract field, their `business_concept_id` values **must match** — enforced at authoring in the canonical onboarding service. This turns a canonical field's concept claim from *asserted* into *provable from source*.
3. **Legacy/archived OCs are not migrated (O-D).** New OCs are authored with concept identity; the 95 free-string active versions are preserved, not backfilled.
4. **Filed as a SIBLING ADR to D430** (not combined, not amending D430). Scope = grammar + consistency-check decision only; implementation deferred to a later DBCP (O-F: sequenced after D430's CC change).
5. **ARPI OC slice = NETWR/VBELN/FKDAT → the same three BCF concepts as the D430 CC slice** (`a42d3fc0` amount, `095afe86` identifier, `d05f24b3` date) on Customer Invoice entity `e3963e45` — pairs with D430 for the first full O→C→M concept-identity proof.

These decisions are recorded in the sibling Observation-side ADR; this study is the grounding evidence behind them.

## Scope guard

Read-only options study. No code, schema, DB write, migration, ADR file, PR, or panel. No OC authored, no meta-schema edited. Runtime objects in `tbc_sandbox1_dev` not queried. This study recommends; the operator locks; only then is an ADR filed and a DBCP drafted.
