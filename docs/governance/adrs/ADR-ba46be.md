---
uid: DEC-ba46be
title: "resolve_legal_entity_attribute: a governed canonical derivation projecting a declared attribute of the runtime-resolved legal entity (D330 compute-library addition; realizes DEC-7dca63 D1)"
description: "Adds a 1-hop canonical-boundary derivation resolve_legal_entity_attribute (v1 attribute set = {currency_code}) that projects an attribute of the §2-resolved legal entity (dim_legal_entity) onto a canonical field, resolved after enrichLegalEntity, fail-closed on unresolved/NULL. Code-level canonical-v2 enum add (contract_json is jsonb; no DB type). Realizes DEC-7dca63 D1's LE-derived local_currency_code; no lower-layer compensation."
status: proposed
date: 2026-10-25T02:12:19.333Z
project: bc-core
domain: contracts
subdomain: canonical/compute-library
focus: grammar
---

# resolve_legal_entity_attribute: a governed canonical derivation projecting a declared attribute of the runtime-resolved legal entity (D330 compute-library addition; realizes DEC-7dca63 D1)

## Context

Grounding the Act C cc-x13pb 4.0.0 envelope (the governed per-LE DSO proof) revealed that DEC-7dca63 D1's decided LE-derived local_currency_code is NOT expressible in the current canonical-v2 grammar: it is not OC-observable (the journal-entry-line fact carries no functional currency); no derivation function projects an LE attribute (resolve_source_entity_binding emits only the open LE code; derivation inputs must be OC-observable, and the LE currency is not); and the resolver never assigns payload[local_currency_code] — local-currency-cross-check.ts only ASSERTS a present value and refuses local_currency_code_absent. So a CC projecting local_currency_code fails validate-envelope / refuses at resolve. The compute library (D330/DEC-637072) grows additively by ADR only (R3); this ADR adds the one missing governed function that realizes DEC-7dca63 D1. Grounded at bc-core main 335624da + bc_platform_dev (no DB enum for derivation functions; contract_json is jsonb). DESIGN ONLY — it authorizes no build or live act; the bc-core implementation keeps its own review + Codex platform-lane + a later operator ratification (same as DEC-7dca63).

## Decision

Add **`resolve_legal_entity_attribute`** to the D330 canonical compute library (DEC-637072; the library grows additively by ADR only — D330-R3). It is the governed realization of DEC-7dca63 D1's declaration that, on the GL / journal-entry-line chain, `local_currency_code` is **derived from the runtime-resolved legal entity**, not observed. It is a design act (DEC-c48b0f): a missing declaration — the compute-library function plus its grammar entry — is supplied; it is not a detector.

**D1. The function.** `resolve_legal_entity_attribute` is a 1-hop canonical-boundary derivation that projects a single declared attribute of the legal entity resolved at runtime (the same entity the universal DEC-ffbc24 §2 selector / `resolve_source_entity_binding` resolves) onto a named canonical field.
- **Inputs:** none from the OC — it reads the resolved legal entity, not an observed source field. It resolves in the same async pass as `resolve_source_entity_binding`, AFTER `enrichLegalEntity` has set the CO's `legal_entity_id` / `legal_entity_code`.
- **`params.attribute`:** a CLOSED set, minimal in v1 — exactly `currency_code` (the LE's declared functional/reporting currency, `tenant_dim.dim_legal_entity.currency_code`). Further attributes are added only by a later additive ADR (D330-R3). No over-build.
- **Output:** the attribute value on the derivation's `canonical_field` (open string; for `currency_code` an ISO 4217 code with no `canonical_value_set`, consistent with the existing `local currency code` characteristic). 1-hop and terminal (never itself a derivation input — D462).
- **Exactly one** `resolve_legal_entity_attribute` per attribute per contract (mirrors the `resolve_source_entity_binding` single-instance rule).

**D2. Fail-closed (Inv VI — never fabricate).** The derivation REFUSES the canonical resolution (no CO) when the legal entity is unresolved, its `dim_legal_entity` row is missing, or the named attribute is NULL/blank. No wildcard, no default. For `currency_code` it reuses the existing `le_functional_currency_undeclared` refusal and the `readCurrentFunctionalCurrency` read. **Current-not-as-of basis:** read as CURRENT (DEC-4aa1ff D10 as-of revision pending TSK-739801); the interim single-LE / time-invariant proof carries the current-not-as-of label and refuses a historically changed attribute.

**D3. Grammar (repair B) — canonical-v2 enum, CODE-LEVEL.** Add `resolve_legal_entity_attribute` to `derivations.function` in `bc-core/src/registry/meta-schemas/canonical-v2.schema.json`. This is a CODE artifact: the function string lives inside `contract_json` (jsonb); there is NO Postgres enum/type backing it (verified — no matching `pg_type` enum; `contract_json` is `jsonb`). So the enum addition rides the bc-core PR and is **NOT** a bc-db migration / Database-Change-Protocol act.

**D4. Engine (repair D).** Implement the resolver branch in `ccv2-canonical-resolver.service.ts`, resolved after `enrichLegalEntity` and BEFORE `crossCheckLocalCurrencyIfProjected`, so that when a CC declares `local_currency_code` via this derivation the field is SET from the resolved LE and the existing cross-check then passes by construction. On the GL/JEL chain the cross-check is therefore satisfied-by-construction — there is no independent observed currency to verify, an honest limitation; integrity rests on the governed LE declaration plus the source booking the GL in the company currency. The Customer-Invoice chain, where `local_currency_code` is OBSERVED, keeps its independent observed-vs-LE cross-check unchanged.

**D5. Relationship to DEC-7dca63.** DEC-7dca63 D1/D2 DECLARE the GL `local_currency_code` is LE-derived; this ADR supplies the single governed mechanism that makes that declaration expressible and resolvable. It does not change DEC-7dca63's decision or DEC-6e951e's gate. cc-x13pb 4.0.0 then declares `local_currency_code` as a `resolve_legal_entity_attribute(currency_code)` derivation (plus its `field_selection` entry bound to the BCF `local currency code` concept) — and carries **no** `assert_equal` resolution_rule (a reference-derived field has no multi-SO conflict to resolve).

## Invariants engaged

- **I — meaning produced once at its boundary:** the LE attribute is projected by the CC at the canonical evaluation, from the governed §2 resolution — not manufactured at a lower layer.
- **IV — references are explicit:** the resolved LE and its versioned `dim_legal_entity` row.
- **VI — evidence emitted, not inferred:** the attribute is a governed declared value, fail-closed, never fabricated or defaulted.

## Foundation gate (DEC-79b62f)

1. **Why B (+D)?** The gap is a missing grammar construct (B — the compute-library function + enum) and its engine (D — the resolver branch). DEC-7dca63 D1 (the upper-layer declaration) is decided and correct; realizing it needs the sanctioned canonical-boundary extension point (the compute library), not compensation elsewhere.
2. **Why not an upper layer?** The sourcing semantics are already decided (DEC-7dca63 D1; DEC-6e951e; DEC-7bccf6 no-FX). This is their realization, not a new semantic.
3. **Why not a lower layer?** Projecting the LE currency below the canonical boundary (at observation, or post-hoc at the read model) would manufacture canonical meaning outside the CC (Inv I). The canonical derivation is the correct layer.
4. **Design act or execution act (DEC-c48b0f)?** DESIGN ACT — a missing declaration (the compute-library function + its grammar) is supplied; its fail-closed refusals are part of the mechanism, not a net substituting for a fix. The bc-core implementation is the execution act under it.

## Scope and status

Scope: the `resolve_legal_entity_attribute` derivation (v1 attribute set = {`currency_code`}); its canonical-v2 enum entry; its resolver branch; and the cc-x13pb 4.0.0 use for the DSO. **Minimal** — general in FORM (an LE-attribute derivation) but with a minimal permitted attribute set, extensible only by a later additive ADR. Authorizes no build or live act; the bc-core build keeps its own review + Codex platform-lane + the operator ratification before decided/merge. **Status: proposed**; ratification is a later operator grant (same as DEC-7dca63). Realizes DEC-7dca63 D1; amends nothing; supersedes nothing (additive to the D330 library).

## References

DEC-7dca63 (the LE-derived currency declaration this realizes); DEC-637072 / D330 (the compute library; R3 ADR-additive rule); DEC-c05551 / D574 (`resolve_source_entity_binding` — the sibling pattern, resolved after `enrichLegalEntity`); DEC-ffbc24 §2 (universal LE resolution selector); DEC-4aa1ff D5/D10 (LE functional-currency attribute; no cross-LE aggregation); DEC-6e951e / DEC-7bccf6 (observed-never-converted; no FX); Foundation `the-invariants.md` I, IV, VI; DEC-c48b0f (design act vs execution act). Grounded at bc-core main 335624da (`canonical-v2.schema.json` `derivations.function`; `ccv2-canonical-resolver.service.ts` `enrichLegalEntity` / `crossCheckLocalCurrencyIfProjected`; `local-currency-cross-check.ts`) and bc_platform_dev (no DB enum for derivation functions; `contract_json` jsonb).
