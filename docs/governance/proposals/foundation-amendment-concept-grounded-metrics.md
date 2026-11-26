---
uid: foundation-amendment-concept-grounded-metrics
title: "Foundation amendment proposal: every metric group is grounded in one business entity's governed concepts"
description: "Draft revision 4, after the owner's answers to revision 3's two questions (masters frozen insert-only; the 15 unhostable groups split). Earlier: revision 3 applied the auditor's answer (gen-52eda8-01) and the owner's rulings. Proposes a named Foundation grammar commitment, its ADR draft and a design sketch: semantic references are pinned entity or concept versions, governed parameters are typed, breakdowns are a separately versioned set pinned by the metric contract, and allowed values become typed rows. Nothing is recorded, built or written."
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

*Draft revision 4, 2026-11-26. Not an ADR and not Foundation text yet. Order (owner, 2026-11-26): draft, red team, auditor, then the group design (TSK-09855b). Counts were read live from `bc_platform_dev` on 2026-11-26; re-read before acting.*

**Revision 3.** Applies the auditor's answer, bc-external-audit `RESPONSE-Codex-gen-52eda8-01` (ACCEPTED WITH BOUNDARY, origin/main 2657f2d7), points 1 to 5 and its ADR-set paragraph. Applies the owner's rulings in barecount-devhub `artifacts/operator-review/DECISIONS-workflow-review.md` on branch `claude/operator-review-content`, entries 5b12384f (the leans) and dfffb1a9 (ruled, "Yes to all"). Revision 2's open questions are answered and removed. Two questions remain (section 11).

**Revision 4.** Applies the owner's answer to revision 3's two questions ("Yes, both", recorded 2026-11-26 08:40 IST), in the same file and branch, entry "Masters and the 15 groups that cannot count themselves". (1) The currency and country masters stay insert-only, with deactivation; their codes and the currency's decimal places are frozen by trigger (section 6.4, Unit V). (2) The 15 groups on entities that cannot count themselves are split: 6 wait for identity concepts by a concept act, 8 Legal Entity groups stay derived with a declared output grain, 1 Cost Center group becomes a slice (section 8.1, re-read live). No questions remain open (section 11).

## 1. The problem

A metric group names its grain and, sometimes, its date. Its other parts are free JSON. Its members already have a typed layer.

| Fact (live) | Value |
|---|---|
| Groups / group versions | 143 / 114 (29 groups have no version) |
| `group.grain_entity_id` | FK to `concept_registry.entity`, set on all 143 |
| `group.temporal_anchor_concept_id` | FK to `business_concept` (not a version), set on 69 |
| `group_version` grain and anchor | same columns, no foreign key on either |
| `template_json` | 24 distinct documents in 7 key shapes; 11 carry `closing_concept_id` inside JSON |
| `member_version_discriminator` | concept version FK (`fk_disc_bcv`); values in `governed_values_json`; 2 rows |
| `business_concept_version.canonical_value_set` | JSONB array on 182 versions; read by 39 bc-core files |
| Currency and country code concepts | 29 currency, 4 country; none carries a value set |
| `master.dim_currency` / `master.dim_country` | 40 / 50 rows, all active; keys `currency_code`, `alpha2` (`alpha3` unique); no FK points at either |

Two live groups (`recognition_event_line_counts`, `recognition_event_revenue_amounts`) have a grain that is wrong in meaning: Recognition Event is employee recognition, not revenue recognition.

## 2. Status of the rule

The rule is a **named Foundation grammar commitment**, "Concept grounding of metric groups". It is not a seventh invariant. It lives in `the-contract-grammar.md` (Metric Directory Member family), with coordinated explanation in `the-invariants.md` and a correction of `metric-directory.md` §6 item 2.

The invariants govern authoritative evaluation and references. A group is governed intent, admitted by DEC-5a9dee 2c. Two distinctions follow:

- **Invariant IV** states the rule for references to authoritative objects. It does not by itself require every directory column to be a concept-version foreign key. The grammar imposes that stronger version-pinning rule on governed directory intent.
- **Invariant I** gives the boundary rule: meaning is evaluated once, at the canonical boundary. A member that classifies records breaks that boundary. The enforcement for the directory is the new grammar.

The ADR (section 5) records both. The erratum is the next free `FND-ERR` number at landing: FND-ERR-009 is claimed by open bc-docs PR 266, so FND-ERR-010 today.

## 3. The rule

### 3.1 The rule text

> **Concept grounding.** A metric group version is made of semantic references and typed governed parameters.
>
> Its **semantic references** are pinned versions of entities or business concepts: the grain, the measure concept, the anchors, the axes, the breakdowns (held in a separate versioned set, section 3.6), the event input's entity, reference, key, date and amounts, and any one-step target. Each is reached on the grain entity, or by one declared step along one of the grain's reference concepts.
>
> Its **typed governed parameters** are not business concepts: the measure kind, the time class, age bounds, signs, period offsets and constants. Each is a typed column or row with a governed value.
>
> Members select governed values on axes and never classify records. Selection relative to the evaluation point P is declared in the metric contract and never computed by a member. A group states the directory's intent. A metric contract realizes a member only when its bindings equal the member's grounded parts, role by role (section 3.5).

### 3.2 The base grammar

| Part | Kind | Rule |
|---|---|---|
| Grain | reference: entity version | required; active |
| Measure kind | parameter: `entity_count`, `count_distinct`, `sum` | required |
| Measure concept | reference: concept version | absent for `entity_count`; a reference concept for `count_distinct`; an amount, quantity or measure concept for `sum` |
| Context | reference: the measure concept's currency or unit context | required for `sum` |
| Time class | parameter: `flow` or `stock_as_of` (ADR-952faa master) | required |
| Period anchor | reference: date concept version | required for `flow` |
| Closing | reference: date concept version | optional; `stock_as_of` only; gross and binary open test (DEC-3926bf D1) |
| Age bands | parameters: lower and upper days; reference: age anchor date concept | optional; `stock_as_of` only |
| Axes | references: code concept versions | 0..n; values from typed rows or a master (section 6.4) |
| Event input | references and parameters (section 3.7) | 0..1; for residual measures (DEC-3926bf amendment 2) |

Breakdowns are not in the group version. They are a separate, versioned set (section 3.6).

### 3.3 The derived grammar

| Part | Kind | Rule |
|---|---|---|
| Output grain | reference: entity version | required |
| Derivation | parameter: `ratio`, `percentage_of_total`, `delta` | required |
| Inputs | references: pinned input member versions, each with a role (`numerator`, `denominator`, `operand`) | required |
| Period offsets | parameter: integer periods per input | default 0 |
| Constants | parameters: role, value type, value | 0..n |
| Reporting anchor | declared (owner ruling 1) | required |

**The anchor rule (owner ruling 1).** A derived group declares its own anchor, checked against its inputs. If all inputs share one anchor, the declared anchor must equal it. If they differ, the declaration names the reporting anchor, and each input keeps its own.

**Output grain.** Each input must be evaluated at the output grain. So each input member's metric contract must partition its output by a breakdown that reaches the output grain (section 3.6). A derived group never rolls up records itself.

**DSO, worked through.**

| Element | Value |
|---|---|
| Output grain | Legal Entity, pinned entity version |
| Numerator | the open AR member version: base group on Customer Invoice, `sum` of the residual amount, `stock_as_of`, event input as for open AR (section 4) |
| Denominator | the invoiced revenue member version: base group on Customer Invoice, `sum` of the invoice amount, `flow` over 365 days ending P, period anchor invoice date |
| Partitions | both input metric contracts break down by the invoice's legal entity reference and by currency |
| Constant | role `days_in_period`, integer, 365 |
| Derivation | `ratio` × constant |
| Reporting anchor | period end P; the numerator keeps its as-of P, the denominator keeps its invoice-date anchor |
| Currency | numerator and denominator must share one currency partition; otherwise refused |

### 3.4 Classification and temporal selection

**Classification** gives a record a governed value that does not depend on P, such as a document type or a status. A canonical contract does it once. A member selects the result.

**Temporal selection relative to P** decides which records count at P: `as_of`, `open_at` or `age_band`. The metric contract declares it in its temporal gate. P stays an evaluation input. bc-core `predicateFromAsOfGate` and `outstandingAgedPredicate` (`src/boundary/governed-selection.ts`) show this behaviour today. That is evidence of current behaviour, not of the proposed schema.

**An age band is a typed temporal choice, not an axis.** The group declares its bands and age anchor. A member selects one band. The selection is a typed row on the member, separate from axis selections. Neither the group nor the member computes or stamps a record's age. `metric-directory.md` §6 item 2, which makes aging buckets canonical values, is corrected.

**Gross or residual.** Each open-item group declares which open model it uses. Gross and binary uses the closing concept (DEC-3926bf D1). Residual uses the event input (DEC-3926bf amendment 2). The two never mix in one group.

### 3.5 Realization equality

A metric contract realizes a member version only when, for every role the grammar models, its binding equals the member's grounded part. Equality is by **semantic role and pinned version**, not by matching concept identities or counts of binding rows.

| Role | Group or member side | Metric contract side |
|---|---|---|
| Grain | grain entity version | grain entity version |
| Measure | measure kind and concept version | aggregation operator and measure variable's concept version |
| Time class and anchor | time class; anchor concept version | temporal gate kind; anchor role's concept version |
| Open test | closing concept version, or event input | `open_at` closing role, or the schedule |
| Age band | selected band bounds and age anchor | `age_band` gate bounds and anchor |
| Axis selection | axis concept version and selected value rows | governed selection (DEC-c4c742), same concept version and values |
| Event schedule | section 3.7, all parts | DEC-45200d schedule, all parts |
| Output context | currency or unit partition or pin; breakdown set version | output context: the same partition or pin; the same breakdown set version, or a subset of it |
| Derived inputs | input member versions, offsets, constants | the input metric contract versions realizing those members; the same offsets and constants |

The gate checks the realization of **this member only**. A metric contract may hold other governed bindings in roles the directory does not model. Those are outside the gate. This is not a global limit on metric contract grammar. It is a condition on DEC-5a9dee 2c's realization relation, and the metric contract stays the sole metric authority.

### 3.6 Breakdowns (owner ruling 3)

A dimension comes only from a governed code or reference concept on the grain, or on one directly linked entity. Never through a chain. Adding one is a concept act in the registry.

A group's allowed breakdowns are kept apart from its members' meaning. Two designs were weighed. (A) A versioned set on the group that members do not pin: but if nothing authoritative pins it, an evaluation reads "the current set", an implicit reference. (B) The metric contract's output context pins the breakdowns: explicit, but then nothing in the directory governs which breakdowns a group allows.

**Chosen: both parts, joined.** A breakdown set is a separately versioned, immutable record keyed to a group version (`group_version_breakdown_set_version`). Members do not pin it. The metric contract's output context pins one breakdown set version and partitions by some or all of its entries.

Why:

- **Invariant III.** A set version never changes. Adding a breakdown makes a new set version. No member version changes, because a breakdown partitions the same value and does not change its meaning.
- **Invariant IV.** The authoritative object, the metric contract, pins an exact set version. No evaluation reads a "current" set.
- **Governance.** The directory says which breakdowns a group allows; the gate checks the metric contract against it. Only a metric that wants a new breakdown needs a new metric contract version.

Currency and unit partitions are not breakdowns. They belong to the measure (section 3.8).

### 3.7 One-step reach and the event input

**One step.** A step names three pinned versions: the grain's reference concept version, its target entity version, and the target concept version. The reference concept's `target_entity_id` must equal the target entity. The target concept's `entity_id` must equal it too.

- **Cardinality.** A step is a lookup from each grain record to at most one target record. It never adds rows. A count or a sum is never multiplied by a step.
- **Several targets.** If a grain record's key resolves to more than one target record at P, the evaluation is refused. It does not pick one and does not multiply.
- **No target.** The grain record still counts in the total. It matches no selected axis value. In a breakdown it falls in a declared `unmatched` partition. The matched and unmatched counts are emitted as evidence (Invariant VI).
- **One-to-many is not a step.** Reaching from an invoice to its lines is a different grain or an event input.

**The event input.** It is a separately pinned, event-grain canonical input. It has its own admission, canonical contract, proof and lineage. A member never reads raw events.

| Part | Kind |
|---|---|
| Event entity version | reference |
| Event canonical contract version | reference |
| Reference to the grain | reference concept version on the event entity; `target_entity_id` equals the grain |
| Grain key | the grain's identity concept version |
| Event date | date concept version on the event entity |
| Anchor amount and date | the group's measure concept and anchor |
| Anchor sign | parameter, −1 or +1, declared, never defaulted (DEC-45200d (1)) |
| Legs | 1..n, each a key concept version, an amount concept version and a sign of −1 or +1; no repeated pair |

The group and the metric contract must agree on the event entity, key, date, amount, every leg sign and the anchor sign. Otherwise one grounded group could give a reversed or overstated residual.

**Partial payments.** The outstanding amount at P is the anchor sign times the anchor amount, plus each leg sign times each leg amount dated on or before P. The dated schedule decides it, not the single full-settlement `closing_date`. This keeps DEC-3926bf's distinction between gross and binary (D1) and residual (amendment 2).

DEC-45200d is proposed, so its schedule is not treated as adopted. It is decided with this ADR as one decision unit (owner ruling 6).

### 3.8 Currency and unit

- A `sum` of a monetary concept is either partitioned by its currency context or pinned to one currency by an axis selection on the currency code concept.
- A record whose currency is empty, or not in `master.dim_currency`, refuses the evaluation. Nothing is dropped silently.
- A sum across currencies is refused. No conversion is implied.
- A derived `ratio` or `delta` requires its inputs to share one currency partition. Mixed inputs are refused.
- A quantity and its unit follow the same rules.

### 3.9 Role-specific checks

A bare foreign key proves only that a row exists. It cannot prove that a date is an eligible date for the grain. So each role has a foreign key and a check. The checks read live columns: `business_concept.entity_id`, `kind`, `representation_term`, `data_type`, `target_entity_id`, and `business_concept_version.semantic_role`, `measure_class`, `context_concept_id`.

| Role | Foreign key | Check |
|---|---|---|
| Grain | `entity_version` | entity active |
| Measure, `count_distinct` | `business_concept_version` | reference concept; on the grain |
| Measure, `sum` | `business_concept_version` | amount, quantity or measure; on the grain; `context_concept_id` set |
| Period anchor, closing, age anchor | `business_concept_version` | `data_type` date; on the grain or the step target; semantic role in the role's eligible set |
| Axis | `business_concept_version` | code concept; on the grain or the step target; a declared value source |
| Breakdown | `business_concept_version` | code or reference concept; same reachability as an axis |
| Step | three FKs (section 3.7) | `target_entity_id` and `entity_id` match the target entity |
| Event parts | `entity_version`, `canonical_contract_version`, `business_concept_version` | reference targets the grain; key, date and leg concepts on the event entity; signs are −1 or +1 |
| Any concept version | `business_concept_version` | its concept is active, not archived |

## 4. Finance metrics under revision 3

| Metric | Grain | Measure | Time class and selection | Axes, event, output | Metric contract |
|---|---|---|---|---|---|
| Invoices for customers in segment X | Customer Invoice | `entity_count` | `flow`, anchor invoice date | axis Customer segment, one step through the customer reference | member selects X |
| Open AR at P | Customer Invoice | `sum` residual amount | `stock_as_of` | event: application entity; anchor sign +1; legs debit −1, credit +1 (DEC-45200d); partitioned by currency | `as_of` with schedule equal to the event input |
| DSO | derived, Legal Entity | none | reporting anchor period end P | section 3.3 | `ratio` × 365 |
| Aging 31 to 60 | Customer Invoice | `sum` residual amount | `stock_as_of`; bands on due date | event as for open AR; member selects band 31 to 60 | `age_band` gate |

## 5. The ADR text (draft)

**Title.** Concept grounding of metric groups: a Foundation grammar commitment.

**Context.** Section 1. The owner ruled on 2026-11-26 that the structured group is concept-first and that this is a Foundation addition.

**Decision.**

1. Sections 3.1 to 3.9 are adopted as a named grammar commitment in `the-contract-grammar.md`, with Foundation erratum FND-ERR-010 (or the next free number at landing). No invariant is added.
2. **Standing.** The invariants govern authoritative evaluation and references. A group is governed intent under DEC-5a9dee 2c. Invariant IV governs references to authoritative objects; this grammar imposes the stronger version pin on directory intent. Invariant I gives the boundary rule; this grammar enforces it for members.
3. `the-invariants.md` gains two explanatory disallowed behaviours. Under IV: a directory part named by free text, by a key inside JSON, or by a concept identity without a version. Under I: a member that classifies, signs or ages records.
4. The design rules of section 3 follow: every semantic reference is a foreign key with its role check; every parameter is a typed column; `template_json`, `temporal_intent_json` and `member.measure_concept_id` are retired; the member layer is extended, with no parallel tables (DEC-1918d0 rule 4); breakdowns are a set the metric contract pins; realization is by section 3.5; re-pointing a grain creates a new group and archives the old one, whose code stays reserved.

**Relations.**

- **Amends DEC-5a9dee 2c**, its grammar description only. The directory still holds no metric authority.
- **Amends DEC-b5c7ff**: the template and member schema; D7's dependency source becomes `member_version_dependency`.
- **Amends DEC-3926bf** only to align: the group declares its closing concept or event input. Its gross and binary versus residual distinction is kept.
- **Decided together with DEC-45200d** (proposed), as one decision unit. Neither claims the other is already effective.
- Consistent with DEC-02f5a9, DEC-67f399, DEC-ca8943, DEC-c4c742. Supersedes none of the four amended or aligned ADRs wholesale.

## 6. Design sketch

Tables only. DDL is authored as bc-db migrations with the owner's database yes.

### 6.1 Group version

Each row of section 3.2 or 3.3 becomes a typed column or child table on the group version: a `*_concept_version_id` or `*_entity_version_id` foreign key for each semantic reference, a coded column for each parameter. Child tables hold age bands, axes (with an optional three-key step) and the event input with its legs. Derived inputs live on the derived member's `member_version_dependency`.

### 6.2 Breakdown set

`group_version_breakdown_set_version` (group version FK, version number, created at) and `group_version_breakdown` (set version FK, concept version FK, optional step). Insert only. The metric contract's output context gains a breakdown set version FK and a list of chosen entries.

### 6.3 Member layer

The live tables are extended. `member_version_discriminator` may select only on the pinned group version's axes, with typed value rows (6.4). A new `member_version_age_band` holds the selected band. `member_version_direct_input` holds the grounded parts for the gate. `member_version_dependency` gains a role and a period offset. `member_version_constant` gets a typed value column in place of `value_json`.

### 6.4 Allowed values: Unit V (owner rulings 2 and 5)

**Unit V, "Typed allowed values"**, is its own unit. It comes after the grounding decision unit and the group design, before the group schema and the sweep. The group schema needs it, because a member's selection points at a value row.

- A code concept version declares its **value source**: `enumerated` or `master`.
- `enumerated`: rows in `concept_registry.business_concept_value` (concept version FK, value code, label). They replace `canonical_value_set`.
- `master`: a row in `concept_registry.value_master` names the master table and key column. Two rows to start: `master.dim_currency.currency_code` and `master.dim_country.alpha2`. The concept version references it by FK.
- A member selection row has exactly one of `concept_value_id`, `currency_code` (FK to `master.dim_currency`) or `country_alpha2` (FK to `master.dim_country`). A check enforces one, and a trigger enforces that it matches the concept's value source.
- A value outside a master is refused until the master adds it.
- **The masters are frozen insert-only (owner, revision 4).** Rows are never deleted. Once a row exists its identity is frozen; only the label and the active flag may change. A `BEFORE UPDATE OR DELETE` trigger on `master.dim_currency` refuses any change to `currency_code` or `decimal_places`, and any delete. A trigger on `master.dim_country` refuses any change to its codes (`alpha2`, and `alpha3` and `numeric_code`, which name the same country), and any delete. `currency_label`, `country_label`, `symbol`, `is_active` and `updated_at` stay writable. A currency whose decimal places change gets a new row with a new code; the old row is deactivated. Deactivation refuses new selections and never breaks a pinned one. Both triggers are in Unit V.
- The 29 currency and 4 country code concepts are given the `master` source.
- Ripple: the 39 bc-core files that read `canonical_value_set` and the 2 that read `governed_values_json` move to the typed rows in this unit.

## 7. The version cascade

A new governed value makes a new concept version, then a new group version that pins it, then new member versions. A new breakdown makes only a new breakdown set version. Where a member's grounded parts change, the gate needs a metric contract version whose bindings equal them. Nothing is edited in place.

## 8. Order of units

| # | Unit |
|---|---|
| 1 | This ADR and DEC-45200d, one decision unit, with FND-ERR-010 and the Foundation text edits (owner's landing go) |
| 2 | The group design, TSK-09855b |
| 3 | Unit V, typed allowed values |
| 4 | The group, breakdown and member schema |
| 5 | The sweep: all 143 groups move first (owner ruling 4) |
| 6 | New metrics, on the metric lane |

**The sweep** (counts from revision 2): 63 groups fit; 14 base groups need an anchor date and 47 derived groups declare one; 15 sit on entities that cannot count themselves and are split (section 8.1); 2 Recognition Event groups are replaced; 2 test leftovers are archived. The 29 versionless groups get a grounded v1. Groups whose members differ only by measure split. Every change goes through the directory commands.

### 8.1 The 15 groups that cannot count themselves (owner, revision 4)

Re-read live on 2026-11-26. None of the 15 has a member. Each has one group version.

| Entity | Group | Class | Disposition |
|---|---|---|---|
| Tax Return | `tax_return_counts` | base | identity concept first (concept act), then grounded v2 |
| Tax Return | `tax_return_ratios` | derived | derived, after its base inputs exist |
| Financial Close | `financial_close_counts` | base | identity concept first (concept act), then grounded v2 |
| Financial Close | `financial_close_ratios` | derived | derived, after its base inputs exist |
| GL Account Reconciliation | `reconciliation_record_counts` | base | identity concept first (concept act), then grounded v2 |
| GL Account Reconciliation | `reconciliation_event_ratios` | derived | derived, after its base inputs exist |
| Legal Entity | `free_cash_flow_metrics`, `profitability_margins`, `profitability_subtotals`, `receivable_control_derived`, `return_ratios`, `solvency_ratios`, `tax_rate_metrics`, `working_capital_metrics` | derived (8) | stay derived; output grain Legal Entity, declared reporting anchor (section 3.3); inputs break down by a `recording_legal_entity` or `issuing_legal_entity` reference (11 such references live) |
| Cost Center | `cost_center_master` | base | becomes a slice: a breakdown on the Journal Entry Line `cost_center` reference; the group is archived and its code reserved |

In counts: 6 groups on 3 entities wait for an identity concept, a concept act through the business concept path, never a metric act. 8 stay derived. 1 becomes a slice. Live, the three entities hold one date concept each and no identity or measure concept.

## 9. Proof cases

These are design requirements against wrong values, not a live metric act.

| Case | Input | Expected |
|---|---|---|
| Partial payment | invoice 1,000; payment 400 dated before P | open AR 600; gross model 1,000 only where the group declares gross |
| Reversal | payment 400, then its reversal, both before P | open AR 1,000; flipping a leg sign or the anchor sign changes the schedule hash and the value |
| One-step fan-out | a customer key matching two customer records at P | refused; never doubled |
| No matching reference | an invoice with no customer record | counts in the total; matches no segment; `unmatched` partition; counts emitted |
| Mixed-currency sum | INR and USD invoices, no partition or pin | refused; with a partition, two values |
| Derived period offset | `delta` with offsets 0 and −1 on one input | value at P minus value at the previous period; refused if the input has no period length |

## 10. Foundation gate (DEC-79b62f)

1. **Location.** B for the grammar (a missing declaration), E for the typed columns that hold it.
2. **Not upper.** A does not declare a metric's shape. Concept gaps are fixed first by BCF acts.
3. **Not lower.** A lint (F) or an evaluation check (D) would be a net. The member layer, the governed selection, the resolver and the DEC-45200d schedule are extended, not bypassed.
4. **Design act.** A missing declaration, named in this amendment, its ADR, its erratum and TSK-09855b.

## 11. Open questions for the owner

None open. Revision 3's two questions were answered by the owner on 2026-11-26 (revision 4 note): the masters are frozen insert-only (section 6.4), and the 15 groups are split (section 8.1).
