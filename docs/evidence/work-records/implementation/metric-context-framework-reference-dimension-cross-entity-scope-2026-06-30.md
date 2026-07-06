---
uid: mcf-reference-dimension-cross-entity-scope
title: MCF Reference-Dimension + Cross-Entity + Secondary-Metric Grammar — Scope
description: Foundation-grounded scope for the metric-engine capability that unblocks the customer-axis (CB-008), cross-temporal (CB-007), and two-population-ratio (CB-011) metric classes. Decomposes the work into four components, each cited to the authoritative Foundation chapters and the MCF build plan. Not an ADR; scoping input for one. Grounded in the actual documents (the-invariants, the-object-model, the-contract-grammar, the-governed-selection, the MCF build plan), not memory.
status: draft
date: 2026-06-30
project: bc-core
domain: contracts
subdomain: catalog
focus: scope
---

# MCF Reference-Dimension + Cross-Entity + Secondary-Metric Grammar — Scope

## 1. What this is

A Foundation-grounded scope for the metric-engine capability surfaced as the real blocker behind CB-008 (customer-axis), CB-007 (cross-temporal), and CB-011 (two-population ratios) in the metric onboarding case book. It decomposes the work into four components, each grounded in the authoritative Foundation chapters and the MCF build plan. It is **not** an ADR and introduces no new architecture — it shows the capability is **already permitted by the Foundation** and **not yet implemented by MCF (M0–M20)**, and what implementing it requires. It is scoping input for the foundational decision (an MCF ADR in the M1 pattern).

Sources read for this scope (no claim here is from memory):
`docs/foundation/the-invariants.md`, `docs/foundation/the-object-model.md`, `docs/foundation/the-contract-grammar.md`, `docs/foundation/the-governed-selection.md`, `docs/implementation/metric-context-framework-build-plan.md`.

## 2. The finding (SES-469bf4)

The customer-axis metrics (CB-008, ~17: top-N concentration, credit-limit utilization, per-customer aging) were assumed blocked on substrate. That is now closed: the **Customer entity is active** (`705f47e1`, with credit limit, customer account identifier, payment terms), and the **Customer Invoice → Customer reference edge is authored + active** (`56a5f975`, identity_bearing, role=customer). Verified live, the metrics still cannot be authored because MCF has **no reference-dimension or cross-entity capability**: `mcf.metric_computed_dimension_ref` = 0 rows; 0 metric variable bindings to reference-kind concepts; all 28 metrics on the single Customer Invoice grain; only `role_kind_code='input'`. The blocker is the **metric grammar + evaluator**, not the substrate.

## 3. What the Foundation already permits (cited)

| Capability | Foundation authority | Verbatim grounding |
|---|---|---|
| A metric reads **multiple entities' Canonical Objects** | The Object Model, §Metric Snapshot (FND-ERR-003, DEC-29c324) | "A single evaluation may reference N Canonical Object versions **across one or more canonical contracts**." |
| **Secondary metrics** (a metric over other metrics), forming a DAG | The Object Model, §Metric Snapshot, "Primary and secondary snapshots" | "A Metric Snapshot is **secondary** when its Lineage references at least one other Metric Snapshot… Secondary snapshots form a **directed acyclic graph** of metric dependencies." |
| **References** as first-class vocabulary | The Contract Grammar, §Vocabulary | Property kind `value` **or `reference`**; `identity_role` `identity_bearing`/`descriptive`. |
| Grouping/selection by rule (not enumeration) | The Governed Selection (DEC-c4c742); Invariant IV | "a metric evaluation is one path: **a governed selection, then an aggregation over the resolved set**." |
| Generalized metric selection authority | The Governed Selection, §Generalization references | "The General Metric Runtime (**DEC-483f1e**); DEC-c4c742." |

**Conclusion:** cross-entity reads, secondary-metric DAGs, and reference vocabulary are all Foundation-defined. This work *implements* the Foundation; it does not extend it.

## 4. The binding Foundation constraints (the design must satisfy these)

1. **Invariant I — meaning once, at the canonical boundary.** The invoice→customer reference (and the customer's credit limit) are *canonical* meaning. A metric may **read** the resolved reference; it may **not resolve** the join at the metric boundary. → The reference must be **stamped on the Canonical Object** before any metric groups or joins by it. (The Invariants, Invariant I; The Object Model, §Canonical Object.)
2. **The Governed Selection predicate reads stamped immutable attributes only** — "no read-time resolution and no calendar resolution at evaluation" (The Governed Selection, §Shape, §Constraints). A grouping key (the customer reference) is admissible **iff** it is a stamped immutable attribute on the CO. The grouping rule is itself **versioned**, and the resolved/partitioned set is **recorded in Lineage** (Invariant IV/VI).
3. **Invariant II — object ordering fixed.** A primary metric derives from CO versions; a **secondary** metric derives from other Metric Snapshots. No skipping; no metric reads raw Source Objects. (The Invariants, Invariant II.)
4. **Invariant VI — Lineage emitted.** A cross-entity metric records the CO versions it joined; a secondary metric records the **Metric Snapshots** it referenced. "A secondary Metric Snapshot is produced without Lineage to the other snapshots it references" is a disallowed behavior (The Object Model, §Metric Snapshot, disallowed).
5. **Acyclicity** for the secondary DAG (The Object Model: "directed **acyclic** graph").

## 5. What MCF has today (cited build plan)

`metric-context-framework-build-plan.md`:
- M2 substrate includes `mcf.metric_computed_dimension_ref` — but the build plan scopes computed dimensions as **temporal**: representative class **#6** is "Fiscal-period computed-dimension metric (`time_anchor_resolution` … `SUM(amount) GROUP BY fiscal_period`)"; class **#7** is "Bucket-assign metric (`bucket_assign` … DSO age buckets)" (§7.1). The §6.1 BCF interface lists the computed-dimension source as "tenant fiscal calendar config."
- Representative class **#8 is explicitly same-entity**: "Two distinct concepts bound to the **same Entity**" (§7.1).
- No M-gate (M0–M20) names reference-dimension grouping, cross-entity metrics, or secondary-metric DAG implementation. The AST taxonomy classes exercised are `variable_ref`, `time_anchor_resolution`, `bucket_assign`, `window`, arithmetic/`case` (the last proven live SES-469bf4).

**Conclusion:** this capability is **beyond the current MCF build plan**. It is a new gate-family, Foundation-permitted, requiring its own foundational decision (M1-pattern ADR) before substrate/service work.

## 6. The scope — four components

### Component A — Canonical prerequisite: stamp the reference on the CO (repair location A + B + C)
The Customer Invoice Canonical Contract must surface the customer reference so the CO carries the resolved customer identity. **Required by Invariant I + the Governed Selection's stamped-attribute rule** before any grouping/join is legal.

**⚠ Verified NOT in-capability (2026-06-30) — see §11.** The reference→OC→CC→CO stamping path has never been built: `KUNNR` (the customer key) is declared in the BSAD source contract but **not observed** in OC v4; **zero** reference-kind concepts are bound in **any** OC or **any** CC; there is **no** customer-key value concept on Customer Invoice. So Component A is itself a capability gap, not a CC bump. It requires: (a) OC widening to observe `KUNNR` (repair A); and (b) a **never-exercised** mechanism for how a `reference` property (edge) becomes a stamped Canonical Object attribute (repair B — grammar) — either the edge resolves to the target identity at canonical evaluation (Foundation-correct, unbuilt), or a parallel value key is observed (in-capability, but duplicates the identity model's reference and is likely wrong). **This is a design decision + capability build, not a governed CC bump.** Unblocks nothing alone, but is the legal predicate source for B and C.

### Component B — Reference-dimension grouping (repair B+D)
Metric grammar + evaluator to **partition the aggregation by a stamped reference dimension**, producing a **distribution** (per-customer values) or a **ranked aggregate** (top-N concentration). Grounded in The Governed Selection ("governed selection, then aggregation"; the partition is aggregation over a stamped immutable attribute) and Invariant IV (the grouping is a versioned predicate; the partition is recorded in Lineage). New grammar surface: a `dimension` binding role to the reference concept; a group-by + optional top-N rank in the aggregation; a `distribution` result shape (already a recognized metric shape per the gold universe). Unblocks: top-N concentration, per-customer aging, distribution metrics. **Output is still one Metric Snapshot** (a distribution-valued one) — no new object type.

### Component C — Cross-entity binding (repair B+D)
Metric grammar + evaluator to **bind a concept on the *referenced* entity** and read its CO alongside the grain entity's CO, joined by the stamped reference. Grounded in The Object Model ("N CO versions across one or more canonical contracts"). Example: `credit_limit_utilization` = (invoice AR per customer) ÷ (the customer's credit limit `bb7d8b50` on the **Customer** CO). New grammar: a variable binding whose `bound_entity_id` is the reference **target** entity, resolved via the stamped reference edge; the metric references N CCs (invoice CC + customer CC) and emits Lineage to both CO sets. Depends on A (the reference must be stamped) and typically B (per-customer grain).

### Component D — Secondary-metric DAG (repair B+D)
Metric grammar + evaluator for **secondary metrics** whose input is another **Metric Snapshot**, forming an acyclic DAG. **The most Foundation-explicit component** — The Object Model defines primary/secondary snapshots verbatim, and DEC-483f1e (The General Metric Runtime) is the cited authority. New grammar: a binding to a Metric Snapshot (not a CO); DAG construction + acyclicity enforcement; Lineage to input snapshots (Invariant VI). Unblocks **CB-007** (DSO = AR balance ÷ net credit sales × days; turnover; CEI; collection period) and **CB-011** (overdue% = Overdue Amount ÷ AR Balance; collection efficiency) — the component metrics already exist live (AR Balance, Overdue Invoice Amount, etc.); the DAG just divides them. **Independent of A/B/C** and arguably the highest leverage (more metrics, most explicit grounding).

## 7. What each component unblocks

| Component | Case-book class | ~metrics |
|---|---|---|
| A (canonical prereq) | (enabler for B, C) | 0 directly |
| B reference-dimension grouping | CB-008 (distribution/per-customer/top-N) | ~8 |
| C cross-entity binding | CB-008 (credit-limit utilization, customer credit metrics) | ~6 |
| D secondary-metric DAG | CB-007 + CB-011 (DSO, turnover, CEI, overdue%, collection efficiency) | ~12 |

## 8. Sequencing + repair-location summary

- **A** (C — CC authoring): governed, in-capability, do first. Foundation gate: repair C; Invariant I/IV satisfied (reference produced once at canonical boundary, stamped).
- **D** (B+D): independent of A; highest leverage; most explicit Foundation grounding (Object Model + DEC-483f1e). Candidate to scope first as its own gate.
- **B** then **C** (B+D): depend on A; the customer-axis cohort.

Each of B/C/D is a **new metric-grammar + evaluator gate** beyond M0–M20 → needs an MCF ADR (M1-pattern: scope, the AST/binding extension, the governed-selection predicate shape, the Lineage/acyclicity rules) before substrate/service work. Foundation gate per component: repair **B (grammar) + D (evaluator)**; no A/C/E/F compensation; Invariants I (canonical-stamped inputs), II (ordering: CO for B/C, Snapshot for D), IV+VI (governed selection + Lineage).

## 9. Recommended first step (revised after §11 verification)

Component A is **not** in-capability (the reference→CO stamping path is unbuilt; §11), so the customer-axis chain A→B→C all sits behind a new capability and a design decision (edge-resolved vs value-key). **Therefore scope Component D (secondary-metric DAG) FIRST**: it has **no reference dependency**, is the **most Foundation-explicit** component (defined verbatim in The Object Model; authority DEC-483f1e), the **highest leverage** (~12 metrics across CB-007 + CB-011), and it **reuses the live primary metrics** (AR Balance, Overdue Amount) — DSO/turnover/CEI/overdue% are just governed divisions of snapshots that already exist. The customer-axis chain (A→B→C) is a second, larger gate that begins with the **reference-stamping design decision** (how a `reference` becomes a stamped CO attribute), which itself needs an ADR before any authoring.

## 11. Verification (2026-06-30, SES-469bf4) — what is actually built

Checked live, not assumed:

| Check | Result | Implication |
|---|---|---|
| `KUNNR` in BSAD source contract | **yes** | the customer key exists at the source |
| `KUNNR` observed in OC v4 | **no** | customer key not admitted; OC widening needed (repair A) |
| reference-kind concepts bound in any OC | **0** | reference observation never exercised |
| reference-kind concepts bound in any CC | **0** | reference→CO stamping never exercised |
| customer-key value concept on Customer Invoice | **none** | no in-capability value-key shortcut exists today |
| `reference` recognized as a `semantic_role` in canonical-v2 `field_selection` | **yes** (schema line 62) | grammar *permits* a reference field; the *runtime path* to populate it is what is missing |

**Net:** the BCF reference edge `56a5f975` is a correct registry-level declaration, but **no contract consumes any reference** — the source→OC→CC→CO reference-stamping path is unbuilt platform-wide. Component A is a capability + design gap, not a governed bump. This is the first thing the customer-axis ADR must resolve.

## 10. References

- The Invariants — Invariants I, II, IV, VI.
- The Object Model — Metric Snapshot (N:CO cardinality; primary/secondary snapshots; Lineage disallowed-behaviors).
- The Contract Grammar — Metric Contract (N:CC cardinality, DEC-29c324); Vocabulary (reference property kind).
- The Governed Selection — DEC-c4c742; the "governed selection + aggregation" model; stamped-attribute predicate; DEC-483f1e (The General Metric Runtime).
- MCF Build Plan — M2 (`metric_computed_dimension_ref`); §7.1 representative classes (#6/#7 temporal computed dimensions; #8 same-entity).
- Metric onboarding case book — CB-007, CB-008, CB-011.
