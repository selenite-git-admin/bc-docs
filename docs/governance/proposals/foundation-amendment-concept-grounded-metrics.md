---
uid: foundation-amendment-concept-grounded-metrics
title: "Foundation amendment proposal: every metric group is grounded in one business entity's governed concepts"
description: "Draft for the red team, then the auditor, then the owner. Proposes grammar text, an ADR draft and a design sketch that replace the free-form group template with typed references to the Business Concept Registry. Nothing is recorded, built or written."
status: drafting
authority: reference
date: 2026-11-26
project: bc-docs
domain: metrics
subdomain: metric-directory/grounding
focus: design
governing_adr: DEC-79b62f
---

# Proposal: metrics grounded in business concepts

*Draft, 2026-11-26. Not an ADR and not Foundation text yet. Order (owner, 2026-11-26): this draft, a red-team attack, the auditor's view, then the group design (TSK-09855b). Counts were read live from `bc_platform_dev` today; re-read before acting.*

The owner's rulings: barecount-devhub branch `claude/operator-review-content`, `artifacts/operator-review/DECISIONS-workflow-review.md`, the last three entries (38a47a2e, 48e188b2). Evidence: barecount-devhub `artifacts/chief/concept-hygiene-study-2026-11-26.md`.

## 1. The problem

A metric group names its grain and, sometimes, its date. Everything else is free JSON.

| Fact (live) | Value |
|---|---|
| Groups / group versions | 143 / 114 (29 groups have no version) |
| `group.grain_entity_id` | FK to `concept_registry.entity`, set on all 143 |
| `group.temporal_anchor_concept_id` | FK to `business_concept`, set on 69 (67 base, 2 derived); every set anchor is a temporal concept of the grain entity |
| `group_version` grain and anchor | same columns, **no foreign key** on either |
| `template_json` | 24 distinct documents in 7 key shapes; `op` takes `count`, `sum`, `ratio`, `formula`, `derivation`; 11 carry `closing_concept_id`, a concept reference inside JSON |
| Measure on the group | none: no template names a measure concept |
| Axes on the group | none; the one member's selection is `discriminator_json` |
| Member measure | `member.measure_concept_id` exists; 0 of 1 member sets it |

The grain is the only part held by a key; the measure, axes and derived inputs cannot be checked by the database. Two live groups (`recognition_event_line_counts`, `recognition_event_revenue_amounts`) have a grain that is wrong in meaning: Recognition Event is employee recognition (human resources), not revenue recognition.

## 2. The proposed Foundation text

### 2.1 Invariant or grammar rule

**A grammar rule under Invariants I and IV, not a new invariant.** The six invariants govern authoritative objects and their evaluation. A metric group is a directory record: intent, not an authoritative object (DEC-5a9dee 2c). The failures this rule prevents are already failures under the existing tests: an axis written as free text is an implicit reference (IV), and an axis computed by the metric is meaning produced outside the canonical boundary (I). A seventh invariant would restate I and IV for one family. The addition is still Foundation: it changes `the-contract-grammar.md` and adds two disallowed behaviours to `the-invariants.md`, with an ADR.

### 2.2 The Contract Grammar, Metric Directory Member family (line 379)

**Before:**

> A governed intent/directory family — not a contract family, and never realized metric authority. A Member owns its intent state (`planned` | `blocked` + reason) and its versioned spec; realized state is DERIVED from the MCF substrate through the realization relation, never cached (DEC-b5c7ff). Directory identity is load-bearing for lifecycle acts: governed reintake requires the member identity tuple (DEC-21ca17 records the operative proof).

**After:** the paragraph above, unchanged, followed by:

> **Grounding.** Every metric group is selected from one business entity's governed concepts. A base group version MUST reference, by key into the Business Concept Registry: its grain, one entity version; its measure, either the count of that entity or one active amount, quantity or measure concept of that entity; its period anchor, one active date concept of that entity; its axes, zero or more active code concepts of that entity, each with a governed value set; and its slices, zero or more active reference concepts of that entity. A member selects governed values on its group's axes; it never computes them. A group MUST NOT carry free text or a JSON document in place of any of these parts, MUST NOT declare a computed or bucketed axis, and, if base, MUST NOT reference a concept of another entity. A derived group references its input groups and grounds through them. The family's question selects which groups become metrics; no group is generated because its concepts exist. A group exists only on an entity that can host it.

### 2.3 The Contract Grammar, Metric Contract body elements (line 210)

**Before:**

> Under DEC-02f5a9, Metric Contract inputs reference Business Concepts and the grain is a typed reference to a Registry entity.

**After:**

> Under DEC-02f5a9, Metric Contract inputs reference Business Concepts and the grain is a typed reference to a Registry entity. A Metric Contract version that realizes a directory member binds only the grain, measure, period anchor, axis values and slices that the member's pinned group version and member version reference; a binding to any other concept is refused.

### 2.4 The Contract Grammar, Vocabulary (line 272)

**Before:** "Contracts reference Business Concepts by identity."

**After:** "Contracts reference Business Concepts by identity, and metric groups are selected from them (Metric Directory Member family)."

### 2.5 The Invariants, disallowed behaviours

Added under Invariant IV (after line 122):

> - A metric group or member names its grain, measure, date, axis, axis value or slice by free text, or by a key inside a JSON document, rather than by a typed reference to the Business Concept Registry.

Added under Invariant I (after line 64):

> - A metric member classifies, buckets or signs records itself, rather than selecting a governed value that the canonical boundary already produces.

### 2.6 Derived groups (open question 1)

A derived group has no measure, axes or slices of its own. It names its input groups by key; its grain is its inputs' common grain unless the derivation coarsens it. Its anchor is either **inherited** (all inputs share one anchor concept) or **declared** (one date concept of the output grain).

## 3. The ADR text (draft)

**Title.** Metric groups are grounded in one business entity's governed concepts.

**Context.** Groups carry free-form `template_json` (24 shapes). The grain is the only part held by a key; the measure, axes and derived inputs are unchecked, and two live groups have a grain wrong in meaning. The owner ruled on 2026-11-26 that the structured group is concept-first and that this is a Foundation addition.

**Decision.**
1. The grammar text of section 2 is adopted, as a grammar rule under Invariants I and IV; no invariant is added.
2. Every group and member part is a foreign key (base: entity version, measure, date, axes, slices; derived: input groups; member: selected values). `template_json` and `discriminator_json` are replaced; no JSONB carries a part (DEC-1918d0 rule 1).
3. A family selects groups; none is generated from the registry. A group exists only on an entity that passes the readiness rule (section 4.4).

**Consequences.** Every existing group is re-versioned or archived (section 5). The entry gate's G1, G3 and G5 checks (DEC-ca8943) become foreign keys for the group's parts. Concept hygiene comes first: value sets on Finance type codes, the ISO-code rule, and identity concepts on four entities. `metric-directory.md` sections 5 and 6 are rewritten: the measure moves from member to group. Foundation edits merge only on the owner's go.

**Relations.** Amends DEC-b5c7ff (the schema sketch's `template_json` and `discriminator_json`; D7, so `depends_on` is read from typed input rows) and DEC-5a9dee item 2c (the Directory family section). Consistent with DEC-02f5a9, DEC-67f399 and DEC-ca8943. Supersedes none.

closes:

## 4. Design sketch

Tables only. No migration is proposed here; DDL goes through bc-db with the owner's database yes.

### 4.1 What a group version carries, replacing `template_json`

| Part | Column or child table | References | Base | Derived |
|---|---|---|---|---|
| Grain | `grain_entity_version_id` | `concept_registry.entity_version` | required | required (output grain) |
| Measure | `measure_kind_code` (`entity_count` \| `concept_sum`) and `measure_concept_id` | master code; `business_concept` (semantic role `amount`, representation `amount`, `quantity` or `measure`) | required; concept NULL iff `entity_count` | absent |
| Period anchor | `anchor_concept_id` | `business_concept` (semantic role `temporal`, `date` or `date_time`) | required | inherited or declared (Q1) |
| Time class | `temporality_class_code` | master (ADR-952faa) | required | required |
| Axes | child `group_version_axis(group_version_uid, axis_concept_id, ordinal)` | `business_concept`, code, with a value set | 0..n | absent |
| Slices | child `group_version_slice(group_version_uid, slice_concept_id)` | `business_concept`, `kind = reference` | 0..n | absent |
| Inputs | child `group_version_input(group_version_uid, input_group_version_uid, role_code)` | `group_version` | absent | 1..n |
| Derivation | `derivation_code` (`ratio`, `percentage_of_total`, `delta`) | master | absent | required |

A trigger refuses any part whose concept is inactive or belongs to another entity than the grain, and any base row with inputs or derived row with a measure.

### 4.2 How members select axis values

| Record | Columns | Rule |
|---|---|---|
| `member_version_selection` | `member_version_uid`, `axis_concept_id`, `concept_version_id`, `value_code` | the axis is one of the pinned group version's axes; the value is in that concept version's governed set |
| empty selection | no rows | the total member |
| derived member | its group's inputs, by member version | no selection unless the output is sliced |

Today the governed set is `business_concept_version.canonical_value_set`, a JSONB array, so a value cannot be a foreign key. Either a trigger checks membership against the pinned concept version, or the registry gains typed value rows (Q5).

### 4.3 How families select groups

A group stays under one family version (`fk_group_version_family`). The family's question decides which groups are authored; there is no "all groups of an entity" command. A derived group's inputs may sit in other families (`metric-directory.md` section 8).

### 4.4 The readiness rule

A base group may be created on an entity version only if the entity is active and has at least one active date concept and either an identity concept (for a count) or an eligible measure concept. Each axis needs a value set. Live: 66 of 149 entities can host a group, 62 with a governed axis; Finance 18 of 19, 16 with an axis.

## 5. Migration path for the 143 groups

| Category | Base | Derived | Path |
|---|---|---|---|
| Grain and anchor fit | 61 | 2 | new group version adds measure, axes and slices |
| Needs an anchor date | 14 | 47 | base: declare the date (Customer Invoice 9, Supplier Invoice 5); derived: per Q1 |
| Entity cannot host (Legal Entity, Cost Center, Financial Close, GL Account Reconciliation, Tax Return) | 4 | 11 | Legal Entity's 8 derived groups stand only if derived groups need no own anchor; the other entities first need an identity concept |
| Mis-pointed grain (Recognition Event) | 2 | 0 | re-point to the revenue-recognition grain through a new group version |
| Test leftovers (`zz_trackA_cefa537`, `je_line_grain_probe`) | 2 | 0 | archive; codes stay reserved |
| **Total** | **83** | **60** | 143 |

All 29 groups with no version get a grounded v1. The 11 `closing_concept_id` keys become typed references. No row is edited in place; each change is a new group version through the directory commands.

## 6. Foundation gate (DEC-79b62f)

1. **Why this location?** B, contract semantics. The missing thing is a declaration in the grammar: what a group must reference. Without it, the parts live in free JSON.
2. **Why not an upper layer?** A (source and admission) is not where a metric's shape is declared. The concept gaps (missing value sets, missing identity concepts) are fixed in the registry by BCF acts first, not compensated in groups.
3. **Why not a lower layer?** A lint on `template_json` (F) or a check at evaluation (D) would be a net. The working mechanism, foreign keys for grain and anchor, is extended, not bypassed.
4. **Design act or execution act?** A design act: a missing declaration. The design acts are this amendment, its ADR and the group design (TSK-09855b).

## 7. Open questions for the owner

1. **Derived anchor:** inherited from the inputs (all inputs must share one date concept) or declared on the derived group?
2. **Externally governed codes** (30 ISO currency and country codes with no value set): a declared standard reference, or an "open axis" that members may not select on?
3. **Slices across a reference:** may a slice reach one step to the target entity's code concept (for example, invoice by customer industry), or only the entity's own reference?
4. **The existing 143:** re-version all before any new metric is placed, or admit new groups grounded and move the 143 by family as each is next authored?
5. **Governed values:** typed value rows in the concept registry, so a member's selection is a foreign key, or the JSONB value set with a membership trigger?
