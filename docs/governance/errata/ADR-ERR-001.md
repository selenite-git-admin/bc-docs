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

## Amendment 1 (2026-08-10) — a FOURTH surface was missed at merge

The original three-surface fix (DB CHECK, source-v1 file, specs) was INCOMPLETE. Contract authoring
validates against the **runtime `contract.contract_meta_schema` DB row**, not the JSON file (the file is
compiled only in tests). The runtime store still carried the pre-amendment reference arm
(`required: [type, reference_target, cardinality]`), so the first live SC author (`product.document`,
Phase B) failed on `res_id` with 422 — while the dry-run (which only builds, never validates) passed.

Synced 2026-08-10 via the governed meta-schema change-request path (proposal → approve, which UPDATEs the
row + invalidates the AJV validator cache); runtime reference arm now `[type, cardinality]`. **Process gap:**
amending a meta-schema FILE must be paired with a migration/seed update to `contract.contract_meta_schema`,
or the amendment is enforced only in tests, not at runtime. Tracked for a reproducible seed/migration.
