---
id: source-variability-and-field-provenance
order: 22
title: "Source Variability and Field Provenance"
status: drafting
authority: derived
depends_on: [the-invariants, the-contract-grammar, the-evaluation-boundaries, data-model-and-schema]
governing_sources:
  - Foundation
  - The Contract Grammar
  - The Evaluation Boundaries
  - DEC-e1241a (D553)
  - DEC-8849c8
  - DEC-b51b48
  - DEC-296505 (D564)
  - DEC-908a69 (D565)
---

# Source Variability and Field Provenance

**This chapter decides nothing.** It is a synthesis map: it assembles, with citations, how already-decided
platform architecture answers one composite question that no single artifact answers alone. Where this
chapter and a governing source disagree, the governing source wins — report the drift, do not follow this
chapter.

## The question

In every source system the platform observes, an object's field set is not fixed — it is the **union of
contributions from extension layers**:

- **SAP** — a transparent table = standard fields + APPEND structures + `CI_`/`.INCLUDE` includes + customer
  `Y*/Z*/ZZ*` fields.
- **Salesforce** — an SObject = standard fields + managed-package fields (namespaced) + tenant `__c` fields.
- **Odoo** — a model = the defining module's fields + every installed module's `_inherit` contributions.

Consequence: **the "same" object differs per installation.** Measured on pilot_ent (Odoo 19 Enterprise,
2026-08-09): `res.partner` carries 219 fields contributed by 28 modules; the India localization (`l10n_in`)
alone injects 9 GST/PAN/TAN fields into that core table. A German installation would not have them — and
would have `l10n_de` contributions instead.

Two failure modes follow if this is mishandled:
1. A Source Contract authored naively from one installation silently becomes **instance-specific** (a
   "universal" `res.partner` SC that is actually India-flavored).
2. Chains and metrics built on variant-contributed fields are **not realizable everywhere**, and nothing
   would say so.

## The answer — six parts, all decided

### 1. One universal union SC per (system-version, object)

The Source Contract declares **everything the source can emit** — core and variant-contributed fields
together, each typed under the governed vocabulary. There is **one active version at a time** (governance
state machine: `active → superseded`; activation marks the prior active with a 48h `supersede_after`
window — D305). Variants are **never** parallel active versions. When the union genuinely grows (a new
module's fields first observed), that is a normal version increment; the nightly reconciler (D369,
`@Cron 02:00`) propagates activation fan-out to tenant environments within 24h — and it is **DDL-only**
(`CREATE TABLE IF NOT EXISTS`): fact rows are never recalculated or rewritten (Invariant III).

*Live proof:* the active `account.move` SC contains all 23 `l10n_in`-contributed fields, typed.

### 2. Field → contributing module is **derivation identity** (DEC-e1241a / D553 pt 8)

Every admitted field's contributing module is recorded at admission in
`source.source_field_derivation.module_name`, from the extract's per-field `via_module`. This is a
**structural identity table** — first-class and queryable — deliberately separate from `source_field`
(which sits at the D162 20-column cap). It is the **single source of truth** for field origin.

> **Anti-pattern (rejected 2026-08-09):** duplicating `module_name` onto `source_field_typing` or the SC
> body "for convenience." That violates DB Rule 4 (one source of truth per value). Consumers that need
> origin — SC authoring, precondition authoring, realizability checks — **join the derivation identity**,
> never copy it.

### 3. The installation's module set is **artefact identity** (DEC-e1241a / D553 pt 2)

Verbatim from the ADR: *"MODULE SET IS IDENTITY, NOT METADATA. `module_set_json` is NOT NULL. A catalog
extracted from an instance with `mrp` installed describes a different system from one without."*

`source.source_catalog_artefact.module_set_json` records exactly which modules the extracted installation
had. *Live proof:* pilot_ent's artefact carries its full 177-module set, hash-identified. "Which variant is
this install?" is therefore **already answered per admission** — no separate "variant" entity exists or is
needed. **Variant = module membership.**

### 4. Context lives at the Canonical Contract — not at the source layer

Per the contract grammar: the **Observation Contract** is mechanical field-selection to business vocabulary
(universal); the **Canonical Contract** declares grain, `field_selection[]`, and resolution rules across N
Source Objects — **context is its job**. A GST-liability canonical selects concepts backed by `l10n_in`
fields; a DSO canonical selects only core-backed concepts. An installation that lacks a module simply never
emits those observations; canonicals that need them are unrealizable *there* — a chain-resolution outcome,
not a contract fork. This is the D513 doctrine (meaning at the canonical boundary) and D502–D504 (regional
semantics are classified at canonical, not at source).

**Invariant guard (Inv I):** field origin is *declarative* (catalog) and *evidential* (admission). It is
**never a semantic discriminator** inside CC/MC logic — a metric may depend on concepts that happen to be
module-backed; it must not branch on "which module."

### 5. Absence is declared and verified — preconditions + Scanner (DEC-8849c8, DEC-b51b48)

What happens when an installation lacks a module whose fields the union SC declares? Decided:

- **DEC-8849c8 (decided):** AC/OC grammars gain `semantic_preconditions[]` — each entry declares
  `subject_kind` (including **`module_presence`**, e.g. `module:mrp`), `expected_value`, and
  `on_violation: block | warn`. Preconditions are versioned with the contract and are part of its meaning
  (Inv I). Declared absence is handled by the declared policy — expected absence is not an error.
- **DEC-b51b48 (planned):** the Landscape Scanner discovers an installation's actual modules/entities and
  produces the compatibility report (active modules, coverage, activatable KPIs). **The Scanner verifies
  declarations; it never invents them.**

Realizability is therefore **variant-gated**: a chain is realizable on an installation iff its required
origin modules ⊆ the installation's module set (artefact identity) — checked, not assumed.

### 6. Tenant-custom is a **separate, deferred axis** (`z_extension`)

`z_extension` on the SC field body means *tenant-scoped custom* (SAP `Y*/Z*`, Salesforce `__c`) — one
specific tenant's additions, carried via `contract_binding.extensions_json`. It is **not** the variant
axis: a variant module (`l10n_in`) is shared by every tenant on that installation and is nobody's
customization. The platform's standing position (standard-tables-first) defers tenant-custom metrics;
nothing in this chapter changes that. **Do not overload the tenant mechanism to represent variants.**

## The three origin axes, side by side

| axis | belongs to | example | where modeled |
|---|---|---|---|
| **standard** | everyone | `res.partner.name` | union SC; derivation identity → core module |
| **system-variant** | every tenant on that install | `l10n_in_gst_treatment` | derivation identity (field) + artefact `module_set_json` (install) + preconditions (absence) |
| **tenant-custom** | one tenant | a `ZZ_`/`x_`/`__c` field | `z_extension` + `contract_binding.extensions_json` (deferred) |

## Anti-patterns (each nearly happened, 2026-08-09)

1. **Per-variant SC versions or per-geography SCs** — forbidden: one active version; variants resolve by
   module membership within the one union SC.
2. **A new "variant" entity or SC layering/composition construct** — unnecessary: the Module level of the
   6-level source hierarchy (`Provider → System → Version → Module → Object → Field`) plus artefact
   module-set identity already express it.
3. **Duplicating field origin into a second table or the SC body** — violates Rule 4; join the derivation
   identity instead.
4. **Using origin as a semantic discriminator in CC/MC** — violates Inv I; origin gates *realizability*,
   never *meaning*.
5. **Solving variant absence through the tenant mechanism** — wrong axis; use `module_presence`
   preconditions (DEC-8849c8).

## Why this chapter exists

On 2026-08-09 this composite question was worked from scratch during Odoo onboarding. Every answer above
already existed — but distributed across D553, DEC-8849c8, DEC-b51b48, the contract grammar, and the
tenant-custom deferral — and the assembly gap produced confident false beliefs ("attribution is dropped,"
"variant is unmodeled") that nearly led to re-deciding decided architecture. This map closes the retrieval
gap at the seam where those decisions compose. If you are about to design source-variability machinery,
**cite this chapter's governing sources first**.
