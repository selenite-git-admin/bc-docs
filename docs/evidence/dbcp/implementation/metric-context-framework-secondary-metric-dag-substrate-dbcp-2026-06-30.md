---
uid: metric-context-framework-secondary-metric-dag-substrate-dbcp-2026-06-30
title: "MCF Secondary-Metric DAG — Authoring-Substrate DBCP (Component D)"
description: "Design-only Database Change Protocol for MCF secondary metrics (Component D of DEC-0f3e57/D467): the substrate to AUTHOR a Metric Contract whose formula reads upstream Metric Snapshots, forming an acyclic metric-dependency DAG. Proposes extending mcf.metric_variable_binding with a metric_input role-kind (upstream-metric ref + per-input snapshot-selection rule), the identity-hash impact, an authoring-time acyclicity gate, a closed selection-rule enum, and new PE-MC checks. Resolves the four open operator decisions in DEC-0f3e57 with recommendations. Authoring/chain-integrity scope only — runtime snapshot reading + secondary-snapshot Lineage emission is the General Metric Runtime (DEC-483f1e) tenant/SDG phase, out of scope. Status proposed; no DDL executed, no schema edited; awaits operator lock of DEC-0f3e57 + this DBCP before any execution gate."
status: proposed
date: 2026-06-30
project: bc-core
domain: metrics
subdomain: contracts/metric
focus: secondary-metric-substrate-dbcp
---

# MCF Secondary-Metric DAG — Authoring-Substrate DBCP (Component D)

> **Status: DESIGN LOCKED (operator-approved 2026-06-30) — execution still gated.** DEC-0f3e57 / D467 is now `decided`, and the four open decisions (a)–(d) are locked as recommended (§7). **No DDL is executed by this document**; no `bc-core/src/database/schema/mcf/*.ts` file is edited; no migration is written. A later **execution gate** authors the Drizzle + `docker/redesign/*.sql` DDL, the M7/M8 serializer extension, the PE-MC checks, and the acyclicity guard, and runs the migration **only after explicit operator approval of that change per the CLAUDE.md Database Change Protocol**. Locking this design ≠ approving the schema mutation — the execution gate is a distinct, separately-approved step.

## 1. Scope and status

### 1.1 Status

Design-only DBCP for the **authoring substrate** of MCF secondary metrics. The governing ADR **DEC-0f3e57 / D467** (Component D) is `proposed`; this DBCP makes its "Grammar / substrate / evaluator shape" concrete and resolves its four open operator decisions (§7 below). Both must be locked before execution.

### 1.2 In scope (authoring to chain integrity)

The platform-level substrate that lets an operator **author a secondary-metric Metric Contract to chain integrity** (draft → approved/active) and have it carry a stable, governed identity:

- A new variable-binding role-kind `metric_input` on `mcf.metric_variable_binding`, binding a formula variable to an **upstream Metric Contract** (not a Business Concept), plus the per-input **snapshot-selection rule**.
- The identity-hash consequence (the new binding columns feed `variable_binding_set_hash` → `identity_tuple_hash` → `package_signature_hash`).
- An **authoring-time acyclicity gate** (the metric-dependency graph stays a DAG).
- A closed **snapshot-selection-rule enum** (the per-input temporal-alignment vocabulary).
- New **PE-MC publication checks** for secondary metrics (upstream-active, selection-rule alignment, acyclicity).
- Drizzle / bc-core file-layout proposal (no code) + DDL sequence + rollback + verification requirements.

### 1.3 Explicitly out of scope (other gates / phases own)

- **Runtime evaluation** — actually reading the selected upstream Metric Snapshots and computing the secondary value at evaluation time. That is the **General Metric Runtime (DEC-483f1e / D465)**, exercised in the **tenant / SDG phase**, not platform authoring. Consistent with the standing discipline "design the general mechanism; verify at chain integrity; tenant snapshots are a deliberate SDG phase."
- **Secondary-snapshot Lineage substrate** — the Metric Snapshot store and its Lineage rows (Object Model §Metric Snapshot, "secondary … references at least one other Metric Snapshot") are runtime artifacts. This DBCP only ensures the **contract** declares the upstream references explicitly (Invariant IV) so that runtime can emit Lineage to them (Invariant VI). No snapshot table is created here.
- **Cross-entity inputs** — Component C (a separate ADR). A `metric_input` here references an upstream metric on the **same or any grain**, but the deferred case of binding to a *reference-resolved* upstream (customer-axis) needs the unbuilt reference→CO stamping path (scope §11) and is excluded.
- **Window/rolling composition** across multiple periods beyond the single per-input selection rule (DEC-0f3e57 "Scope boundaries").
- **M7/M8 hash-population logic changes** — this DBCP ships the **columns**; the formula-canonicalization / package-signature services (M7/M8) are extended to *serialize* the new binding fields. That service change is noted (§5) and gated separately, mirroring how M2 shipped columns that M7/M8 populate.

---

## 2. Grounding (this implements the Foundation; it does not extend it)

### 2.1 The Object Model — §Metric Snapshot (verbatim, `docs/foundation/the-object-model.md` L121, L128)

> "A Metric Snapshot is **primary** when its Lineage references only Canonical Objects. A Metric Snapshot is **secondary** when its Lineage references at least one other Metric Snapshot in addition to Canonical Objects. Secondary snapshots form a **directed acyclic graph** of metric dependencies. The graph is descriptive only. Traversal reads preserved Lineage; it does not trigger recomputation of any snapshot in the chain."

Disallowed behavior (L128): "A secondary Metric Snapshot is produced **without Lineage** to the other snapshots it references." → the contract must declare the upstream references explicitly so runtime can emit that Lineage. That is precisely what this substrate records.

### 2.2 Invariants

- **Invariant II (object ordering fixed).** A secondary metric derives only from objects of a preceding type — Metric Snapshots — never from raw Source Objects, never by skipping. The DAG flows snapshot→snapshot, acyclic by definition. The authoring-time acyclicity gate (§4.4) enforces this at the contract layer.
- **Invariant IV (references explicit).** The upstream metric and the snapshot-selection rule are **declared columns**, not inferred — the binding names exactly which upstream metric and which alignment rule each input uses.
- **Invariant I + The Governed Selection (DEC-c4c742 / D464).** Which upstream snapshot an evaluation reads is a **declared, versioned governed selection** over the upstream snapshots' stamped fields and the evaluation parameter P — never "latest", never read-time. For a secondary metric the candidate set is the upstream snapshot set; the selection rule (§4.2) is that predicate.
- **Invariant VI (evidence emitted).** Out of scope for *this* substrate (runtime emits the Lineage), but this DBCP guarantees the contract carries the explicit upstream refs that runtime Lineage must point to.

### 2.3 Authorities

- **DEC-0f3e57 / D467** — Component-D ADR (this DBCP's governing decision; `proposed`).
- **DEC-483f1e / D465** — The General Metric Runtime (the cited generalized authority; secondary metrics are its metric-over-snapshot instantiation; runtime is its phase).
- **DEC-c4c742 / D464** — The Governed Selection (selection-then-aggregation; the per-input selection rule is a governed selection).
- **DEC-c3e57f / D422** — Foundational MCF ADR (the `mcf.*` substrate, identity model §4, binding model §6).
- Scope: `docs/implementation/metric-context-framework-reference-dimension-cross-entity-scope-2026-06-30.md` §6 (Component D), §11 (why no reference dependency).

---

## 3. The substrate decision (resolves DEC-0f3e57 open decision **c**)

### 3.1 Recommended: **Option C1 — extend `mcf.metric_variable_binding`**

A `metric_input` **is a variable binding**: the formula's `variable_ref` resolves to it exactly as `input`→BC does today. It therefore must feed `variable_binding_set_hash` (which serializes every binding row by `structural_sort_key` per the M2 substrate) so that adding/changing an upstream input changes the metric's identity — satisfying DEC-0f3e57 grammar point #4 **for free**, in one ledger. Splitting `metric_input` into a separate table would force the package-signature service to read a second source for "what variables this metric binds," creating two identity inputs and a reconciliation risk. One table = one answer to "what does variable Vₙ resolve to" (BusinessConcept | Entity | constant | **upstream Metric Contract**), preserving Invariant IV in a single place.

**New columns on `mcf.metric_variable_binding`** (all nullable; populated only on `role_kind_code='metric_input'` rows):

| Column | Type | Purpose |
|---|---|---|
| `bound_metric_contract_uid` | `uuid` | The **upstream Metric Contract** (parent identity) this input reads. Physical FK to `mcf.metric_contract` (same schema → FK mandated, D162 Rule 3). |
| `bound_metric_contract_version_id` | `uuid` | Binding-time freeze of the upstream's then-active MCV (mirrors `bound_business_concept_version_id`; evidence/provenance, Invariant III). **Not** the runtime snapshot — that is selected per the rule below. |
| `snapshot_selection_rule_code` | `text` | Closed enum (§4.2 / decision **a**): the per-input temporal-alignment rule (governed selection over upstream snapshots). |
| `snapshot_selection_params_json` | `jsonb` | Opaque rule parameters (e.g. period offset). JSONB is correct here per D162 Rule 1 — `snapshot_selection_rule_code` is the queryable column; params are opaque config. |

Column count: 14 → **18** (≤ 20, D162 Rule 6). The upstream-metric reference is identity (the metric DAG edge); the rule is identity (it changes the value); both belong on the binding row that already carries identity.

**Constraint changes:**

```sql
-- 1. role-kind enum gains 'metric_input'
ALTER TABLE mcf.metric_variable_binding DROP CONSTRAINT mvb_role_kind_chk;
ALTER TABLE mcf.metric_variable_binding ADD CONSTRAINT mvb_role_kind_chk
  CHECK (role_kind_code IN ('input','output','constant','metric_input'));

-- 2. target-shape check gains a metric_input branch (exactly-one-target discipline)
ALTER TABLE mcf.metric_variable_binding DROP CONSTRAINT mvb_role_target_chk;
ALTER TABLE mcf.metric_variable_binding ADD CONSTRAINT mvb_role_target_chk CHECK (
  (role_kind_code = 'constant'
     AND constant_value_json IS NOT NULL
     AND bound_business_concept_id IS NULL AND bound_entity_id IS NULL
     AND bound_metric_contract_uid IS NULL)
  OR (role_kind_code IN ('input','output')
     AND constant_value_json IS NULL AND bound_metric_contract_uid IS NULL
     AND (bound_business_concept_id IS NOT NULL OR bound_entity_id IS NOT NULL))
  OR (role_kind_code = 'metric_input'
     AND bound_metric_contract_uid IS NOT NULL
     AND snapshot_selection_rule_code IS NOT NULL
     AND constant_value_json IS NULL
     AND bound_business_concept_id IS NULL AND bound_entity_id IS NULL)
);

-- 3. selection-rule closed enum (decision a — first cut)
ALTER TABLE mcf.metric_variable_binding ADD CONSTRAINT mvb_selection_rule_chk CHECK (
  snapshot_selection_rule_code IS NULL
  OR snapshot_selection_rule_code IN ('as_of_period_end','period_matched')
);

-- 4. real FK (same-schema) + supporting index
ALTER TABLE mcf.metric_variable_binding ADD CONSTRAINT fk_mvb_upstream_mc
  FOREIGN KEY (bound_metric_contract_uid)
  REFERENCES mcf.metric_contract(metric_contract_uid) ON DELETE RESTRICT;
CREATE INDEX idx_mcf_mvb_upstream_mc ON mcf.metric_variable_binding(bound_metric_contract_uid)
  WHERE bound_metric_contract_uid IS NOT NULL;
```

### 3.2 Considered alternative: **Option C2 — dedicated `mcf.metric_secondary_input` table**

A separate table (`metric_contract_version_uid` FK, `variable_role_code`, `upstream_metric_contract_uid`, `selection_rule_code`, `params_json`). **Rejected for the first cut** because (i) it duplicates the binding concept and forces the package-signature service to incorporate a second table into `variable_binding_set_hash`, and (ii) the exactly-one-target discipline that `mvb_role_target_chk` already expresses would have to be re-implemented across two tables. C2 becomes attractive only if `metric_variable_binding` later approaches the 20-column ceiling or if secondary inputs grow many input-specific columns; revisit then. **Operator picks C1 or C2 — this is decision (c).**

---

## 4. Grammar, gates, and the four open decisions

### 4.1 Formula AST (no change)

Reuses the existing AST (`divide`/`multiply`/`minus`/`sum`/`avg`/`case` — proven live SES-469bf4). A `variable_ref` whose role binds a `metric_input` resolves, at runtime, to the selected upstream snapshot's value. **No new AST node types** for the first cut (ratio/arithmetic over inputs). The first targets — DSO, overdue % — are `divide`/`multiply` over two `metric_input`s.

### 4.2 Snapshot-selection-rule vocabulary (decision **a**)

First-cut closed enum, each rule a governed selection aligned to an upstream temporal-gate shape:

| Rule | Meaning | Valid upstream gate | Example use |
|---|---|---|---|
| `as_of_period_end` | The upstream snapshot whose `as_of` anchor = the secondary's evaluation-period end (a point-in-time state/balance). | `as_of` | AR Balance, Overdue Invoice Amount in DSO / overdue %. |
| `period_matched` | The upstream snapshot for the **same fiscal period** P (a period flow). | `period_aggregate` | Gross Invoiced Amount in DSO. |

These two cover every §6-target (balance ÷ flow, balance ÷ balance). **Recommend shipping exactly these two**; `prior_period_end`, `trailing_window_aligned`, `period_start` are deferred extensions of the same enum (additive, no identity break for existing rows). This is decision (a).

### 4.3 The secondary metric's own temporal gate (decision **b**)

**Recommend:** the secondary metric carries its **own** `temporal_gate_shape_code = 'period_aggregate'` (evaluation parameter P = the period), and each input's selection rule aligns its upstream snapshot to P. **Do not auto-inherit** from inputs — an explicit gate keeps "what period does this metric assert over" declared at its own boundary (Invariant I, meaning evaluated once at its own boundary). This is decision (b). (A future windowed secondary could carry `trailing_window`; out of first-cut scope.)

### 4.4 Acyclicity gate (Invariant II)

The metric-dependency graph (edge = a `metric_input` binding from metric A's version to upstream metric B) must stay a **DAG**. **Recommend service-level enforcement at bind time** (matching the existing bind-time-check pattern; the result is recorded in `bind_time_check_results_json`): on authoring a `metric_input`, walk the upstream graph from B; reject if it reaches A. Rationale for service-not-trigger: a recursive-CTE `AFTER INSERT` trigger is heavy and the codebase already validates cross-row binding semantics service-side (no physical FK to `concept_registry`, M7 bind-time checks). A standing **audit query** (recursive CTE over `metric_variable_binding` where `role_kind_code='metric_input'`) backstops it for drift detection. *Operator may instead mandate a DB trigger for a hard guarantee — a sub-decision under (d); the trade-off is enforcement-strength vs insert cost.*

### 4.5 Identity-hash impact (DEC-0f3e57 point #4)

`variable_binding_set_hash` already canonically serializes every binding row by `structural_sort_key` (M2 substrate header). The M7/M8 services extend that per-binding serialization to include, for `metric_input` rows, `(bound_metric_contract_uid, snapshot_selection_rule_code, snapshot_selection_params_json)`. Consequently the upstream-metric set + selection rules flow into `identity_tuple_hash` and `package_signature_hash` automatically — adding, removing, or re-aligning an upstream input is an identity change (supersession, not a revision), exactly as DEC-0f3e57 #4 requires. **This service-serialization change is the one consuming code change outside the DDL; it is gated with the execution gate, not applied here.**

### 4.6 PE-MC checks (decision **d**)

New publication-eligibility checks for secondary metrics (proposed IDs — final numbering/G-code alignment is decision **d**):

- **PE-MC-13 (upstream-metric-active):** every `metric_input`'s `bound_metric_contract_uid` has a currently-active MCV at publication time. Fail-closed.
- **PE-MC-14 (selection-rule alignment):** each `metric_input`'s `snapshot_selection_rule_code` is valid for the upstream's `temporal_gate_shape_code` per the §4.2 table (`as_of_period_end`→`as_of`; `period_matched`→`period_aggregate`).
- **PE-MC-15 (acyclic):** the metric-dependency DAG including this version's `metric_input` edges is acyclic.

The M10 self-verification verifier handles a secondary metric by treating the upstream snapshot values as **fixture Section-A inputs** (the fixture supplies each `metric_input`'s value; the verifier computes the formula) — **no new verifier class**, only input-value substitution. *Naming note:* CLAUDE.md records a G-code scheme (e.g. G3 = legacy PE-MC-11). Whether the new checks take PE-MC-13/14/15 or G-codes is part of decision (d); this DBCP uses PE-MC-1x as working IDs.

---

## 5. Drizzle / bc-core implementation notes (no code)

- Edit `bc-core/src/database/schema/mcf/metric-variable-binding.ts`: add the four nullable columns, the `metric_input` enum value, the extended target check, the selection-rule check, the FK to `metricContract`, and the partial index.
- DDL block appended to `bc-core/docker/redesign/04-mcf-substrate.sql` (the binding table's home) — additive `ALTER TABLE`s per §3.1.
- M7 (`formula-canonicalization.service.ts`) / M8 (`package-signature.service.ts`): extend per-binding canonical serialization to include the `metric_input` fields (§4.5). Bind-time acyclicity + upstream-active checks added to the binding writer (the cert writer / M7 binding path).
- PE-MC evaluator (`metric-publication-eligibility-evaluator.service.ts`): add PE-MC-13/14/15.
- No change to `mcf.metric_contract` / `metric_contract_version` columns; secondary-ness is fully expressed by the presence of `metric_input` bindings.

---

## 6. DDL sequence, rollback, verification

### 6.1 Sequence (execution gate, post-lock)

1. `ALTER TABLE … ADD COLUMN` ×4 (nullable — safe, no rewrite, no default backfill).
2. Drop+recreate `mvb_role_kind_chk`, `mvb_role_target_chk` (additive branches; existing rows already satisfy the unchanged branches).
3. Add `mvb_selection_rule_chk`, `fk_mvb_upstream_mc`, `idx_mcf_mvb_upstream_mc`.
4. Post-apply verifier asserts: existing rows unaffected (all have `role_kind_code IN ('input','output','constant')` and NULL in the new columns); the four checks present; the FK present.

### 6.2 Rollback

Fully reversible: drop the FK + index + `mvb_selection_rule_chk`, restore the original two checks, drop the four columns. No existing row carries the new columns until a secondary metric is authored, so rollback is a clean reverse-ALTER. (Once secondary metrics exist, rollback also requires archiving those contracts — flagged as a forward-only point after first use.)

### 6.3 Verification requirements (future execution gate)

- Unit: the binding writer accepts a `metric_input` row (valid upstream + rule), rejects each malformed shape (missing upstream, missing rule, BC+metric both set), and rejects a cycle.
- Unit: package-signature serialization includes the `metric_input` fields → identity changes when an upstream/rule changes.
- Integration (chain integrity, platform-only): author a real DSO secondary contract over live primaries (AR Balance `a11a88f4` as_of period-end ÷ Gross Invoiced Amount period-matched × days) to **approved**; PE-MC-13/14/15 PASS; identity stable across re-read. **Stop at chain integrity** — no tenant snapshot evaluation (that is the SDG/runtime phase).

---

## 7. Operator decisions — LOCKED 2026-06-30

| ID | Decision | Locked outcome |
|---|---|---|
| **(a)** | Selection-rule enum | **LOCKED:** ship exactly `as_of_period_end` + `period_matched` (§4.2); extend additively later. |
| **(b)** | Secondary's own temporal gate | **LOCKED:** own `period_aggregate`, explicit, no auto-inherit (§4.3). |
| **(c)** | Substrate shape | **LOCKED — Option C1:** extend `mcf.metric_variable_binding` (§3.1), not a separate table. |
| **(d)** | New-check numbering + acyclicity enforcement | **LOCKED:** PE-MC-13/14/15; **service-level** acyclicity at bind time + audit query (§4.4) (DB trigger not mandated for the first cut). |

## 8. Risks / notes

- **Identity migration:** none for existing metrics — all current bindings are `input`/`output`/`constant`; the new columns are NULL for them, and the serialization change is a no-op for rows without `metric_input` (the serializer only emits the new fields when present). Confirm the M7/M8 serializer is written so a binding-set with zero `metric_input` rows hashes **identically** to today (regression guard).
- **Upstream supersession:** if an upstream primary is superseded after a secondary is published, PE-MC-13 (re-evaluated) and the runtime selection rule must resolve against the upstream's active line. The binding references the upstream **parent** `metric_contract_uid` (stable), not a version, so supersession of the upstream doesn't orphan the edge; `bound_metric_contract_version_id` is provenance only.
- **Runtime is the next gate, not this one.** This DBCP gets a secondary metric to *chain integrity*. Producing a secondary Metric Snapshot with Lineage to the selected upstream snapshots is DEC-483f1e runtime in the SDG/tenant phase — a separate build, separately gated.

## 9. Foundation gate (CLAUDE.md)

- **Repair location: B (contract grammar) + C (binding).** The change defines what a Metric Contract may declare (a metric-over-snapshot input) and binds it (the `metric_input` row). It is not a lower-layer compensation.
- **Why this location?** The capability is a grammar gap: MCF's contract grammar cannot express "this metric reads another metric's snapshot," though the Foundation Object Model defines it. The fix is at the grammar/binding layer where meaning is declared — not by tuning facts (E) or read filters (F).
- **Why not upper layers (A)?** Source reality is irrelevant — secondary metrics consume Metric Snapshots, not new source emissions.
- **Why not lower layers (D/E/F)?** Runtime (D) and snapshot store (E) consume this declaration; building them first would have nothing to read. The contract must declare the explicit upstream reference (Invariant IV) before runtime can emit Lineage to it (Invariant VI).
- **Invariants honored:** II (snapshot→snapshot, acyclic — §4.4), IV (explicit declared upstream + rule — §3.1), I/Governed-Selection (the rule is a declared governed selection, not "latest" — §4.2). No DB row hand-edits; all writes via the binding writer service. **No DDL applied by this document.**
