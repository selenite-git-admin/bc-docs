---
id: ADR-ERR-001
title: "D559 reference coherence over-constrained: polymorphic references have no fixed target"
status: adopted
authority: authoritative
affected: DEC-3d4304 (D559) — reference-kind coherence rule (typing CHECK + source-v1 grammar mirror)
resolution: bc-core PR #672 (merge 3bb21a41, 2026-08-10) — three-surface amendment
opened: 2026-08-10
---

# ADR-ERR-001 — D559 reference coherence over-constrained: polymorphic references

## Contradiction summary

D559 (DEC-3d4304) declared reference-kind coherence as *"a reference names its target"* — enforced by
`ck_source_field_typing_coherence` (`reference ⇒ reference_target_object NOT NULL`) and mirrored in the
`source-v1` meta-schema reference arm. Real sources disprove the universal: **polymorphic references**
carry no fixed target. Observed on pilot_ent (Odoo 19, Phase-A extract): `many2one_reference` — an integer
join key whose target model varies **per row** (e.g. `product.document.res_id`; 12 fields instance-wide) —
and `reference` — `'model,id'` text (4 fields). Both **are** join keys (kind `reference`; coarsening to
scalar would lose exactly the knowledge D559 preserves), but declaring a fixed target for them would be
fabrication (an Invariant VI violation: synthesized rather than emitted knowledge).

## Amendment

The reference arm's target is **capture-where-present**: a plain reference (e.g. `many2one`) names its
target; a polymorphic reference carries NULL / omits `reference_target`. All other D559 coherence is
unchanged — reference still requires the stored key's scalar type and cardinality `one`, and still forbids
relation linkage; scalar and relation arms are byte-identical. Same discipline as the D559 u3b
all-or-nothing junction rule (never fabricate, never coarsen).

Amended surfaces (bc-core PR #672, Codex-ACCEPTED at reviewed head `3682411`, Foundation-checked against
all six invariants): the DB CHECK (migration `tsk-1e2fde-typing-polymorphic-reference.sql` + verbatim
rollback), the `source-v1` meta-schema reference arm, and the D559 round-trip specs (a polymorphic
reference validates and emits **no fabricated target**; the arm stays tight otherwise).

## Residual (recorded, not built)

NULL target is semantically overloaded (polymorphic vs. capture-failure); the discrimination is explicit in
`native_type_text` and rests on extractor discipline, not schema enforcement. No observed defect justifies
a net; if one appears, the declarative tightening is a polymorphism marker on the governed per-version type
mapping.
