---
uid: foundation-amendment-concept-grounded-metrics
title: "Foundation amendment proposal: every metric group is grounded in one business entity's governed concepts"
description: "Draft revision 2, after an independent red team. Proposes a named Foundation grammar commitment, its ADR draft and a design sketch that extend the typed member layer and replace the free-form group template with typed references to business concept versions. Nothing is recorded, built or written."
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

*Draft revision 2, 2026-11-26. Not an ADR and not Foundation text yet. Order (owner, 2026-11-26): this draft, a red-team attack, the auditor's view, then the group design (TSK-09855b). Counts were read live from `bc_platform_dev` today; re-read before acting.*

The owner's rulings: barecount-devhub branch `claude/operator-review-content`, `artifacts/operator-review/DECISIONS-workflow-review.md`, the last three entries (38a47a2e, 48e188b2). Evidence: barecount-devhub `artifacts/chief/concept-hygiene-study-2026-11-26.md`.

**Revision 2.** Applies the findings of an independent red team, 2026-11-26 (verdict: unsound as written, fixable):

1. One event input is allowed, so open AR, cash application and the DSO numerator stay expressible.
2. Aging is temporal selection relative to the evaluation date P, declared in the metric contract. `metric-directory.md` §6 item 2 is wrong on this.
3. Every part references a concept version (Invariant IV).
4. The live typed member layer is extended; revision 1's parallel tables are removed.
5. The measure moves to the group; the member-level measure is retired.
6. The measure gains temporality, distinct count, and currency or unit context.
7. A part may be reached by one declared step along a reference of the grain.
8. A realization gate replaces the binding limit on metric contracts.
9. The rule is a named grammar commitment, outside the invariant list.
10. The resolver, the repair location (B plus E), the version cascade, derived anchors, period offsets, constants and grain re-pointing are stated.

## 1. The problem

A metric group names its grain and, sometimes, its date. Its other parts are free JSON. Its members already have a typed layer.

| Fact (live) | Value |
|---|---|
| Groups / group versions | 143 / 114 (29 groups have no version) |
| `group.grain_entity_id` | FK to `concept_registry.entity`, set on all 143 |
| `group.temporal_anchor_concept_id` | FK to `business_concept` (not a version), set on 69 |
| `group_version` grain and anchor | same columns, **no foreign key** on either |
| `template_json` | 24 distinct documents in 7 key shapes; 11 carry `closing_concept_id` inside JSON |
| `member_version_discriminator` | `concept_id, concept_version_id, operator_code, governed_values_json`; FK `fk_disc_bcv` to `business_concept_version`; 2 rows |
| `member_version_direct_input` | concept version and entity version, both FK (`fk_di_bcv`, `fk_di_ev`); 2 rows |
| `member_version_dependency` | input member version, FK to `member_version`; 0 rows |
| `member_version_constant` | `role_code, value_type, value_json`; 0 rows |
| `member_version` | `grain_entity_version_id`; JSONB `temporal_intent_json`, `output_intent_json` |
| Member measure | `member.measure_concept_id` exists; 0 of 1 member sets it |
| Monetary amount concepts (latest version) | 57; 54 carry a currency `context_concept_id` |

The member layer holds concept-version keys; only its values and its temporal and output intent are JSONB. The group holds only the grain by key. Two live groups (`recognition_event_line_counts`, `recognition_event_revenue_amounts`) have a grain that is wrong in meaning: Recognition Event is employee recognition, not revenue recognition.

## 2. Status of the rule

The rule is a **named Foundation grammar commitment**: "Concept grounding of metric groups". It is recorded with its own ADR and its own Foundation errata entry (the next free `FND-ERR` number at landing; FND-ERR-009 on `origin/main` today; check open PRs first). It amends DEC-5a9dee 2c, DEC-b5c7ff and DEC-3926bf. It stays **out of the invariant list**.

Why not an invariant. The invariants govern authoritative objects. A group is a directory record of intent (DEC-5a9dee 2c). The failures the rule prevents already fail Invariants I and IV.

Why the owner's "foundational" reading is right. The rule changes Foundation text (`the-contract-grammar.md`, `the-invariants.md`). It decides what a metric may mean before any metric contract exists, and every later act reads it. Foundation's own change mechanism (ADR, errata, coordinated edits) is the only lawful way to make it, as with DEC-5a9dee.

## 3. The rule

### 3.1 The rule text

> **Concept grounding.** Every metric group version names one entity version as its grain. Every other part is a typed, versioned reference to a business concept version. It is reached on the grain entity, or by one declared step along one of the grain entity's reference concepts. The parts are:
> - a **measure**: the count of the grain entity; the distinct count of a reference concept; or the sum of one amount, quantity or measure concept, with its currency or unit context;
> - a **temporality**: `flow` over a period anchor (a date concept), or stock as of the evaluation date P, optionally with a closing concept and declared age bands;
> - **axes**: code concepts with a governed or declared-standard value set;
> - **slices**: reference concepts;
> - **at most one event input**: one entity that references the grain through a declared reference concept, carrying dated, signed legs.
>
> Members select governed values on axes and never classify records. Selection relative to P is declared in the metric contract's temporal gate and never computed by a member. A derived group declares its anchor. Derived members reference input member versions, declared constants and declared period offsets. A group states the directory's intent. A metric contract realizes a member only when its bindings equal the member's grounded parts. This is a realization gate, not a limit on what a metric contract may bind.

Further rules that the text implies:

- **Currency and unit.** A monetary sum is partitioned by its currency context, or pinned to one currency by an axis selection. Sums across currencies are refused. The same holds for a quantity and its unit.
- **One step.** A step names one reference concept of the grain and one concept of its target, such as an order line header's date or an invoice customer's segment. Two steps are refused.
- **Measure on the group.** Members that differ only by measure become separate groups.
- **Event legs.** Each leg names its key concept, its amount concept and a declared sign of +1 or −1 (DEC-45200d (2)). A declared leg sign is part of the definition. It is not a member signing records.
- **Families select.** No group is generated because its concepts exist. A group exists only on an entity that can host it (section 6.3).

### 3.2 Classification and temporal selection are different acts

**Classification** gives a record a governed value that does not depend on P, such as a document type or a status. It happens at the canonical boundary. Members select the result.

**Temporal selection relative to P** decides which records count at P: `as_of` (exists by P), `open_at` (not closed by P), `age_band` (aged between two bounds at P). Age changes every day, so it cannot be a canonical value. The metric contract declares it in its temporal gate; the engine applies it (`predicateFromAsOfGate` and `outstandingAgedPredicate`, bc-core `src/boundary/governed-selection.ts:193-250`). P is the evaluation input, never a contract value.

Age bands are a **declared selection on the group**, not an axis value. The group declares the bands and the age anchor; a member selects one band; the metric contract carries it in its `as_of` gate.

`metric-directory.md` §6 item 2 makes aging buckets canonical values. That is wrong and is corrected in the same change.

### 3.3 Concepts, not fields

A metric contract binds concepts. The resolver maps each to exactly one canonical field and refuses none or more than one (bc-core `src/boundary/metric-variable-resolver.ts`). The canonical layer is not skipped.

## 4. Finance metrics under revision 2

| Metric | Grain | Measure | Temporality | Axes, slices, event | Member and metric contract |
|---|---|---|---|---|---|
| Invoices for customers in segment X | Customer Invoice | entity count | `flow`, anchor invoice date | axis: Customer segment, one step through the customer reference | member selects X |
| Open AR at a date | Customer Invoice | sum of invoice amount, by currency | stock as of P, closing concept clearing date (DEC-3926bf) | event input for partial payments: the application entity, legs debit −1 and credit +1 (DEC-45200d) | gate `as_of`, `open_at`; schedule equals the event input |
| DSO | derived, output grain Legal Entity | none | declared anchor: period end P | inputs: open AR member (stock), invoiced revenue member (`flow` over the period ending P); constant: days in period | `ratio` × constant |
| Aging buckets | Customer Invoice | sum of open amount, by currency | stock as of P, closing concept, age anchor due date, bands 0-30, 31-60, 61-90, 90+ | none | member selects one band; gate `age_band` |
| Period-over-period change | derived, grain of the input | none | inherited from the one input | input: one member version, period offsets 0 and −1 | `delta` |
| Distinct customers invoiced | Customer Invoice | distinct count of the customer reference | `flow`, anchor invoice date | none | total member |
| Ledger balance | Journal Entry Line | sum of signed balance amount, by currency | stock as of P, anchor posting date | slice: GL account; axis: account type, one step through the account reference | the canonical boundary signs the amount; the member selects only |

## 5. The ADR text (draft)

**Title.** Concept grounding of metric groups: a Foundation grammar commitment.

**Context.** Section 1. The owner ruled on 2026-11-26 that the structured group is concept-first and that this is a Foundation addition.

**Decision.**
1. The text of section 3.1 is adopted as a named grammar commitment in `the-contract-grammar.md` (Metric Directory Member family), with an errata entry. No invariant is added.
2. Two disallowed behaviours are added to `the-invariants.md`. Under IV: a group or member names a part by free text, by a key inside a JSON document, or by a concept identity without a version. Under I: a member classifies or signs records itself, instead of selecting a governed value the canonical boundary produced.
3. Every group part is a foreign key to a concept version or an entity version. `template_json` is retired. The member layer is extended; no parallel table is made (DEC-1918d0 rule 4).
4. The measure is a group part. `member.measure_concept_id` is retired. `metric-directory.md` §5 and §6 are rewritten, and §6 item 2 is corrected.
5. A metric contract realizes a member only through the realization gate of section 3.1.
6. Re-pointing a grain creates a new group. The old group is archived and its code stays reserved.

**Consequences.** Every existing group is re-versioned, replaced or archived (section 8). The entry gate's G1, G3 and G5 checks (DEC-ca8943) become foreign keys. Concept hygiene comes first. Foundation edits merge only on the owner's go.

**Relations.**
- Amends DEC-5a9dee 2c. The realization gate stays within 2c: the directory still holds no metric authority and still only references MCF authority through the realization relation. The gate is a condition on that relation. The amendment is to the grammar paragraph 2c admitted.
- Amends DEC-b5c7ff: `template_json` and `discriminator_json` are retired, and D7's `depends_on` is read from `member_version_dependency`.
- Amends DEC-3926bf: the group now also declares its closing concept and event input, so the gate can compare them with the metric contract.
- Aligns with DEC-45200d (proposed): its schedule is the metric contract side of the event input.
- Consistent with DEC-02f5a9, DEC-67f399, DEC-ca8943 and DEC-c4c742 (the governed selection). Supersedes none.

closes:

## 6. Design sketch

Tables only. No migration is proposed here. DDL goes through bc-db with the owner's database yes.

### 6.1 What a group version carries, replacing `template_json`

| Part | Column or child table | References | Base | Derived |
|---|---|---|---|---|
| Grain | `grain_entity_version_id` | `entity_version` | required | required (output grain) |
| Measure | `measure_kind_code` (`entity_count`, `count_distinct`, `sum`); concept version; context concept version | `business_concept_version` | required | absent |
| Temporality | `temporality_class_code` (`flow`, `stock_as_of`) | master (ADR-952faa) | required | required |
| Anchor | anchor concept version | `business_concept_version` (date) | required | declared |
| Closing | `closing_concept_version_id` | `business_concept_version` (date) | optional, stock only | absent |
| Age bands | child `group_version_age_band` (lower and upper days, age anchor concept version) | `business_concept_version` | optional, stock with closing | absent |
| Axes and slices | child `group_version_part` (role `axis` or `slice`, concept version, optional step reference concept version) | `business_concept_version` | 0..n | output slicing only |
| Event input | child `group_version_event` (event entity version, reference, date, legs with key, amount and sign) | `entity_version`, `business_concept_version` | 0..1 | absent |
| Derivation | `derivation_code` (`ratio`, `percentage_of_total`, `delta`) | master | absent | required |

A trigger refuses an inactive concept version, a part off the grain without a declared step, a second step, and a sum without a context.

### 6.2 The member layer, extended

| Live table | Today | Revision 2 |
|---|---|---|
| `member_version_discriminator` | concept version FK; values in `governed_values_json` | the axis must be one of the pinned group version's axes; values become typed rows (Q4) |
| `member_version_direct_input` | concept version and entity version FK | holds the member's grounded parts, copied from the group version for the gate |
| `member_version_dependency` | member version FK | derived inputs; gains a declared period offset |
| `member_version_constant` | `value_json` | declared constants, such as days in period |

An empty selection is the total member. `temporal_intent_json` gives way to the group's typed temporality and a typed age-band selection.

### 6.3 The readiness rule

A base group may be created on an entity version only if the entity is active, has an active date concept, and has an identity concept (for a count) or an eligible measure concept. Each axis needs a governed or declared-standard value set. Live: 66 of 149 entities can host a group; Finance 18 of 19.

## 7. The version cascade

A new source that needs a new governed value makes a new concept version, then a new group version that pins it, then new member versions. Where a member's grounded parts change, the gate needs a metric contract version whose bindings equal them. Nothing is edited in place.

## 8. Migration path for the 143 groups

| Category | Base | Derived | Path |
|---|---|---|---|
| Grain and anchor fit | 61 | 2 | new group version adds measure, temporality, axes and slices |
| Needs an anchor date | 14 | 47 | base: declare the date (Customer Invoice 9, Supplier Invoice 5); derived: declare the anchor |
| Entity cannot host (Legal Entity, Cost Center, Financial Close, GL Account Reconciliation, Tax Return) | 4 | 11 | derived groups on Legal Entity declare their anchor; the other entities first need an identity concept |
| Mis-pointed grain (Recognition Event) | 2 | 0 | new group on the revenue-recognition grain; the old group is archived |
| Test leftovers (`zz_trackA_cefa537`, `je_line_grain_probe`) | 2 | 0 | archive; codes stay reserved |
| **Total** | **83** | **60** | 143 |

The 29 groups with no version get a grounded v1. The 11 `closing_concept_id` keys become typed. Groups whose members differ only by measure split. Each change goes through the directory commands.

## 9. Foundation gate (DEC-79b62f)

1. **Why this location?** B for the grammar text: what a group must reference is a missing declaration. E for the typed columns that hold it. B without E leaves the parts in JSON; E without B would be a schema with no rule behind it.
2. **Why not an upper layer?** A does not declare a metric's shape. Concept gaps are fixed in the registry by BCF acts first.
3. **Why not a lower layer?** A lint (F) or an evaluation check (D) would be a net. The working mechanisms are extended: the member layer's keys, the governed selection, the resolver.
4. **Design act or execution act?** A design act: a missing declaration. The acts are this amendment, its ADR, its errata entry and the group design (TSK-09855b).

## 10. Open questions for the owner

1. **Declared-standard value sets:** 30 ISO currency and country codes have no value set. Does the registry declare the standard (ISO 4217, ISO 3166-1) and its edition as the value set, so members may select on them?
2. **The existing 143:** re-version all before any new metric is placed, or admit new groups grounded and move the 143 by family as each is next authored?
3. **Event input breadth:** is one event input enough, or does a known Finance metric need two (for example, payments and credit notes against one invoice)?
4. **Governed values:** typed value rows in the concept registry, so a member's selection is a foreign key, or the JSONB value set with a membership trigger?
5. **DEC-45200d order:** decide DEC-45200d before this ADR, or record both in one act so the event input and the schedule declaration land together?

Q1 (derived anchor) of revision 1 is answered: declared. Q3 (slices across a reference) is answered: one declared step.
