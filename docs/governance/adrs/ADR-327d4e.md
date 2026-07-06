---
uid: DEC-327d4e
title: "MCF identity_tuple_hash v2 — include the computed-dimension kernel (amends hash-authority D-M7-8)"
description: "A grouped (distribution/top-N) metric is a distinct metric identity from its ungrouped scalar base, so the §10 identity_tuple_hash includes the computed-dimension kernel (appended only when non-empty -> ungrouped v2 is byte-identical to v1). Bumps mcf-hash-v1 -> v2, NO restamp (the v1 corpus is immutable per Invariant III); L-V1h dedup compares stored hashes across versions. Unblocks the CB-008 customer-axis grouping cohort (DEC-2c2849/D469). Amended 2026-06-30: restamp design rejected by the immutability trigger; replaced with the backward-compatible tuple."
status: decided
date: 2026-06-30T10:59:40.517Z
project: bc-core
domain: metrics
subdomain: contracts/metric
focus: identity-hash
---

# MCF identity_tuple_hash v2 — include the computed-dimension kernel (amends hash-authority D-M7-8)

## Context

No rationale recorded.

## Decision

AMENDS the M7/M8 formula-hash-authority DBCP decision D-M7-8 (bc-docs-v3/docs/implementation/metric-context-framework-m7-m8-formula-hash-authority-dbcp.md §10.2), which deliberately EXCLUDED computed-dimension refs from identity_tuple_hash ("computed-dim refs belong in package signature, not identity").

PROBLEM: a reference-dimension grouping metric (CB-008 Component B, DEC-2c2849/D469) shares grain + formula_intent + variable_binding_set + filter_set + temporal_gate with its ungrouped base, differing ONLY in the computed_dimension_ref (group_by + rank). Because the §10 identity_tuple_hash = JCS([formula_intent_hash, variable_binding_set_hash, filter_set_hash, grain_entity_id, temporal_gate_shape_code, temporal_gate_params_kernel]) (6 elements) excludes the computed dim, the grouped metric COLLIDES with its base at the L-V1h materialize gate (verified: top_10_customer_ar_concentration -> identity_tuple_hash_collision_with_active_mc:a11a88f4 = ar_balance). This blocks the entire "group an existing AR metric by customer" class (top-N concentration, per-customer aging).

WHY AMEND D-M7-8: a grouped metric (distribution / top-N) is a GENUINELY DISTINCT metric from its ungrouped scalar base — different output shape, different meaning ("the ten largest customers" is not "the total"). Its identity MUST include the grouping. D-M7-8's exclusion was reasonable when computed dimensions were only TEMPORAL granularity (a fiscal-period view ~ the same metric at a finer grain); it does not hold for REFERENCE-dimension grouping. We generalize: ANY computed-dimension grouping is identity-distinguishing (the cleaner rule; zero existing metrics carry a temporal computed_dimension_ref, so generalizing costs nothing).

DECISION:
1. identity_tuple_hash gains a 7th JCS element = the sorted computed-dimension kernel set (the SAME projection §11.2 readComputedDimKernelSet already produces for the grain_filter_temporal_dimension_signature_hash: per mcf.metric_computed_dimension_ref row -> {dimension_class, role_in_formula, source_business_concept_id}, JCS-sorted; [] when no rows). v2 tuple = JCS([formula_intent_hash, variable_binding_set_hash, filter_set_hash, grain_entity_id, temporal_gate_shape_code, temporal_gate_params_kernel, sorted_computed_dimension_ref_kernel_set]) (7 elements). The §11.1 intermediate + package_signature_hash are UNCHANGED (they already include the dim kernel).
2. Bump the algorithm version MCF_HASH_ALGORITHM_VERSION 'mcf-hash-v1' -> 'mcf-hash-v2' (substrate regex ^mcf-[a-z-]+-v[0-9]+$). §10.4 partial UNIQUE on (identity_tuple_hash, hash_algorithm_version) WHERE archived_at IS NULL already namespaces by version.
3. MIGRATION (operator pre-approved): recompute + restamp identity_tuple_hash + hash_algorithm_version='mcf-hash-v2' for all 48 non-archived mcf.metric_contract rows (service-driven recompute via the v2 PackageSignatureService). Ungrouped metrics get an empty ([]) dim element, so their RELATIVE uniqueness is preserved (two ungrouped duplicates still collide); grouped metrics become distinct from their base. Verify-first runner (dry-run/apply/rollback, before/after hash probe). REQUIRED, not optional: without it L-V1h would compare a v2 candidate hash against stale v1 stored hashes and silently stop detecting duplicates.
4. L-V1h collision gate (metric-authoring-materialization.service.ts ~755 + the mcf-read.service.ts preflight mirror): both already call the SSOT PackageSignatureService.computeIdentityTupleHashFromInputs — extend its signature with the dim kernel (substrate-read path reads it via readComputedDimKernelSet; the proposal path projects it from candidate.computed_dimension_refs via a shared pure projection helper). Add an explicit hash_algorithm_version='mcf-hash-v2' filter to the collision SELECT (same-version compare; future-proof).
5. Golden anchors: the one hardcoded golden (§14.7) is the M9 fixture hash — UNAFFECTED. The identity_tuple_hash tests are determinism/parity (no hardcoded value). Re-baseline any exact identity assertion + verify the AIV/ARPI collision specimen still behaves (it has no computed dim, so unchanged). Add a NEW golden/behaviour test: a grouped vs ungrouped pair now has DISTINCT identity_tuple_hash (the fix), and two identical grouped metrics still collide.

FOUNDATION GATE: repair location B (metric IDENTITY grammar / contract semantics). The gap is in the identity composition itself (it under-distinguished grouped metrics); not a storage (E) or read (F) fix, and the computed_dimension_ref grammar (B, DEC-2c2849) is already correct — only its omission from identity is wrong. No lower-layer compensation. Touches metric-identity uniqueness (Invariant I — a metric's meaning/identity is produced once, at the metric boundary).

VERIFICATION: package-signature unit (new determinism/parity + the grouped-vs-ungrouped distinctness + identical-grouped-collision tests); migration verify-first (48 MCs restamped, before/after probe, independent DB check); then E2E re-run the prepared grouping specs (top10-customer-ar-concentration.json, per-customer-overdue-amount-0-30.json) -> materialize past L-V1h -> activate -> the CB-008 customer-axis grouping cohort unblocks.

SCOPE: identity_tuple_hash + its version + L-V1h ONLY. package_signature_hash / grain_filter_temporal_dimension_signature_hash / formula-side M7 hashes UNCHANGED. The hash-authority DBCP §10.2 + D-M7-8 are amended (companion doc edit, §10.6).

## Amendment (2026-06-30, post-implementation) — backward-compatible v2, NO restamp

Decision points 2–4 above (bump version + **restamp the 48 MCs** + add a same-version `hash_algorithm_version='mcf-hash-v2'` filter to L-V1h) were **revised during implementation** when the restamp was rejected by the substrate.

**What changed and why.** The restamp APPLY was blocked by `mcf.fn_mc_active_immutability_check()`: `identity_tuple_hash` + `hash_algorithm_version` are **immutable** once an MC has any past-draft version. All 48 active MCs are past-draft, so an in-place restamp is a historical rewrite — Foundation **Invariant III**. The trigger is correct; the restamp design was the violation. Nothing was written (the migration tx rolled back atomically).

**Corrected design (operator-approved, A — backward-compatible tuple):**

1. **Conditional append.** The computed-dimension kernel is appended to the identity tuple **only when non-empty**. An ungrouped metric omits the element → the 6-element tuple is **byte-identical to v1**. A grouped metric is a distinct 7-element identity. (Supersedes point 1's unconditional 7-element form.)
2. **No restamp, no migration.** The immutable v1 corpus is never touched. v2's byte-compatibility for the ungrouped case is what makes this safe. (Replaces point 3 entirely — the verify-first restamp runner was written, proven Foundation-invalid by the trigger, and removed.)
3. **Cross-version dedup — NO version filter.** L-V1h (materialization) + the mcf-read preflight mirror compare the candidate's stored hash across **all** algorithm versions. ungrouped v2==v1 → dedup against the frozen corpus preserved; grouped → distinct → admitted. Only **emitted** stored hashes are compared, never a re-inferred v2 identity for a v1 metric (Foundation **Invariant VI**). (Reverses point 4's same-version filter.)
4. **Residual (accepted by design, 2026-06-30).** The one pre-v2 grouped metric (`top5-customers-by-gross-invoiced-amount`, `e73c91d7-…`, minted dim-blind under v1) permanently carries the identity of its *exact* ungrouped base (`SUM(gross_amount)` at the same grain/gate/filter). Concrete cost: that one specific ungrouped base cannot be authored while top5 is active (its v2 identity == top5's stored v1 identity → L-V1h collision); any base differing in grain/gate/filter is unaffected, and all *new* grouped metrics are correct. **This is NOT correctable through any governed path** — supersession (the rebind service) is identity-PRESERVING, materialize forces `supersedes_version_uid=null`, and active metrics cannot be abandoned (DRAFT/REVIEW only). Changing an active metric's identity would require purpose-built active-metric-replacement machinery, which is unwarranted for this narrow case. **Accepted as a known limitation** (operator decision); top5 stays as-is. The original "re-mint via supersession" remedy was based on a mechanism that does not exist — supersession cannot change identity (Invariant III + identity-evaluated-once). Task TSK-da7528 closed won't-fix-by-design.

Foundation gate unchanged (repair location **B**, metric-identity grammar). The version-bump + conditional-append + cross-version-compare honour Invariants I, III, and VI together. Full detail: hash-authority DBCP §10.6.
