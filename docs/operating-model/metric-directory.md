---
id: metric-directory
order: 10.8
title: "The Metric Directory"
status: drafting
authority: draft-authoritative
depends_on: [business-vocabulary, metric-management-system, metric-catalog, metric-evaluation, mcf-legacy-bridge]
governing_sources:
  - Foundation (Invariant I — meaning is evaluated once, at its boundary; Invariant IV — all references are explicit)
  - Business Vocabulary (BCF — concepts, semantic roles, canonical_value_set)
  - Metric Management System (Creation Track — Stage 1 operator intent is fed by this directory)
  - The Contract Grammar (Metric Contract — the realized declaration this directory references but never restates)
governing_adrs:
  - DEC-c3e57f (D422 — MCF foundational; the Metric Contract is the realized authority)
errata_referenced: []
v2_sources: []
diagrams: []
ratification: operator-aligned in design session 2026-07-08; no ADR filed yet
scope_locks: documentation-only; no substrate mutation; no runtime change; no code patch; no DB write; no PR
related:
  - metric-catalog.md (the realized metrics — what exists)
  - metric-management-system.md (the metric lifecycle / flow)
  - business-vocabulary.md (BCF — the meaning dictionary this one is the metric-side peer of)
---

# The Metric Directory

## 1. Purpose and posture

The **Metric Directory** is a governed **dictionary / blueprint** that answers one question: *"What metrics should exist, organized by value, and how is each one specified?"* It is the metric-side peer of the **Business Concept Framework (BCF)** — where BCF is the dictionary of *business meaning*, the Metric Directory is the dictionary of *intended metrics*.

It is deliberately three things it could be confused with, and is **none** of them:

- It is **not the Metric Catalog.** The catalog records what has been *realized* (live, certified Metric Contract Versions). The directory records what *should exist* by value — the blueprint, not the built inventory.
- It is **not the Metric Contract.** The Metric Contract is the *realized, evaluated declaration*. The directory holds *intent/spec* — the input from which a contract is authored.
- It is **not a store.** This chapter defines a vocabulary and a structure. Where it is persisted, how it reconciles with existing substrate, and how it links to realized contracts are **implementation questions, deliberately out of scope here** (see §11).

This chapter is **structure first**. Naming is the language layer over the structure; it is not the structure itself. The doctrine is operator-aligned as **draft-authoritative** — binding on subsequent design work, not yet ADR-filed and not yet reflected in any substrate.

## 2. The boundary rule (governs everything below)

> **Directory parameters are intent/spec — the input an envelope is authored from. The Metric Contract is the realized declaration — the output. The directory references the contract for realized semantics; it never restates, re-derives, or competes with them.**

This is the operating form of **Invariant I** (meaning is evaluated once, at its boundary): the directory declares *what we intend to author at*, and the authoring boundary produces the realized meaning. A directory that inferred realized metric semantics rather than referencing them would be a violation, not a convenience.

## 3. The hierarchy

```
Function ─▶ Subfunction ─▶ Family(theme) ─▶ Group ─▶ Member
                                                       └─ depends_on ▶ Member   (orthogonal edge, not containment)
```

- **Strict single-parent tree.** A metric is authored **once**, in exactly one Group under one Family.
- **Cross-audience reuse is a separate commercial-Pack layer** (any-to-any composition), *out of scope for the directory*. The directory stays a clean tree; the messy many-to-many lives where it belongs — in commercial packaging.

## 4. Levels

| Level | Meaning | Parameters |
|---|---|---|
| **Function** | domain | `code`, `label` |
| **Subfunction** | sub-domain | `code`, `label`, `parent` |
| **Family** | **analytical theme** — the decision/question a set answers (e.g. "Journal & Close Quality"). *Not* a persona; persona-bundling is a commercial concern. | `theme`, `decision`, `rationale`, `priority`, `applicable_industries[]` (see §7) |
| **Group** | one authoring run — a grain + a shape | `grain`, `template` (see §5) |
| **Member** | one metric | `measure`, `discriminator`, `dimensions`, `class`, `depends_on`/`inputs` (see §6) |

## 5. Group — grain + a class-discriminated template

```
Group.grain    = BCF entity + temporal anchor
                 base    → source aggregation grain
                 derived → output grain (inherited from inputs unless the derivation coarsens it)

Group.template = a discriminated union keyed by class:
   base    → { kind: 'aggregation', op: count | sum-amount | as-of-balance, measure_concept }
   derived → { kind: 'derivation',  op: ratio | percentage-of-total | delta, inputs: [member refs] }
```

- `class` **selects which parameter grammar the Group speaks** — explicit, not a single field whose meaning flexes by a sibling flag. This mirrors BCF's own `kind: value | reference` discrimination, where `reference` carries its own grammar (`reference_role` / `target_entity_id`) rather than overloading the value fields.
- **`depends_on` falls out of** the derivation template's `inputs` — dependencies are declared once, in the template, never a second hand-kept list that can drift from the formula.
- **Members inherit grain + template** from their Group and cannot drift from them.

## 6. Member — measure + a select-only discriminator

- **measure** = a BCF concept + representation (e.g. `Journal Entry Line · debit amount` / amount).
- **discriminator** = a conjunction of predicates, each `{ a BCF dimension-or-status concept, one or more governed values from that concept's canonical_value_set }`.

The discriminator obeys one rule that makes the whole model source-agnostic:

> **It selects; it never computes.** A discriminator may only reference a governed value that *already exists*. All classification, bucketing, signing, and source-literal mapping happen upstream at the reader / canonical boundary (repair-locations A / C); the metric only picks from the result.

Consequences that fall straight out:

1. **Source-agnostic by construction.** Because a discriminator names a canonical *concept + canonical value*, a source literal (`BLART`, `SHKZG`, an ERP entry-method code) has nowhere to live in it. This is PE-MC-12 ("filters bind status/dimension roles only") and Invariant I made structural, not a lint rule.
2. **Buckets are canonical values, not metric ranges.** An aging member is `aging-bucket = '31-60'`, never `31 ≤ days < 60`. The bucketing derivation lives at canonical, where derivations belong; the metric selects the resulting value.
3. **The empty discriminator is the total/base member** — the denominator, or the whole-population count.
4. **It is a base-member parameter.** Derived members get their identity from their **input tuple** (the template's `inputs`), not from a discriminator — unless the derived *output* is further sliced.

- **class** = `base | derived`.

## 7. The applicability marker (Category / Industry)

A metric's industry applicability is **intrinsic semantics, not commercial packaging** — `gross_margin_per_hectare` is agricultural because its denominator is hectares; `gmroi` is a retail-inventory ratio; `net_operating_income` is real-estate/hospitality. That is what the metric *is*, decided by construction, so the marker belongs in the directory.

- Stored as one field on the **Family (theme)**: `applicable_industries[]` — **empty means global** (applies to every industry); a non-empty list names the industries it is specific to (a metric may serve several, e.g. `[real_estate, hospitality]`).
- `category: global | industry_specific` is a **derived view** of that field (global iff the list is empty) — one source of truth, so the two views cannot drift.
- **Members inherit** their Family's applicability and may **override** it — a global theme may hold one industry-specific variant member (e.g. a per-hectare version of an otherwise-global margin).
- **Commercial packaging composes on this marker**; it does not set it. A future "Retail" commercial pack = `global` themes ∪ `retail`-tagged themes. The composition/sale is commercial; the tag is a directory fact. Same cut as theme-vs-persona: intrinsic classification here, bundling there.

## 8. Cross-cutting rules

- **Single-membership** — one home Group / one Family per metric; reuse is a commercial-layer concern.
- **`depends_on` DAG** — an orthogonal computation edge among Members. It may cross Group and Family boundaries; a base metric is authored **once** and *referenced*, never re-authored, by derived members elsewhere.
- **Seeds are secondary.** A Member may or may not have seed material behind it; when it is absent or thin, the off-pool maker synthesizes the specification. Seeds are *evidence and coverage*, never the worklist authority. (This inverts the earlier seed-primary model.)
- **Feasibility is explicit.** A Member/discriminator is `bcf_ready` iff every referenced concept exists **and** each referenced value is in that concept's `canonical_value_set`; otherwise it is `bcf_gap` — a *surfaced* gap, never a silent skip. The directory is what lets a missing BCF concept be reported precisely rather than discovered mid-authoring.

## 9. Worked example

**Family (theme):** *Journal & Close Quality* → **Subfunction** General Ledger → **Function** Finance. `applicable_industries: []` (global).

**Group 1 — "JE-line counts"** · grain = Journal Entry Line (posting date via parent JE) · template = `{aggregation, count}`

| Member | discriminator | class | feasibility |
|---|---|---|---|
| `total_je_lines` | ∅ | base | `bcf_ready` (JE-line + line-number exist) |
| `manual_je_lines` | `entry-method = 'manual'` | base | `bcf_gap` (no entry-method concept in BCF) |
| `corrective_je_lines` | `line-type = 'corrective'` | base | `bcf_gap` |

**Group 2 — "JE quality %"** · grain = JE Line (output) · template = `{derivation, percentage-of-total}`

| Member | inputs (`depends_on`) | class |
|---|---|---|
| `manual_je%` | `manual_je_lines / total_je_lines` | derived |
| `corrective_je%` | `corrective_je_lines / total_je_lines` | derived |

This shows the model working at once: a theme-scoped Family; a base group where the *discriminator* does the work, feeding a derived group where the *input tuple* gives identity; `depends_on` crossing groups inside the family; and the feasibility gate flagging exactly which members are blocked on a missing BCF concept — precisely, not vaguely.

## 10. Relationship to neighbouring chapters

- **BCF / Business Vocabulary** — the directory *references* BCF concepts (measures, dimensions, values). BCF is the meaning dictionary; the directory is the metric dictionary. They link at the feasibility edge.
- **Metric Management System (MMS)** — the directory feeds MMS's **Creation Track at Stage 1 (operator intent)**. MMS owns the *flow* of a metric through its lifecycle; the directory owns the *structure and value-organization* of what enters that flow.
- **Metric Catalog** — the catalog is *realized* metrics (what exists); the directory is *intended* metrics (what should exist). A Member points to its realized Metric Contract once authored; coverage is the comparison between the two.

## 11. Parked — the implementation conversation (explicitly out of scope here)

Deliberately deferred until the conceptual model is ratified: where the directory is persisted (bc-core vs devhub); reconciling or retiring the existing `onboarding_candidate` store; the Member→Metric-Contract realization link; lifecycle-state ownership (own-intent / derive-realization); naming collisions with the generator's existing "family", `domain-taxonomy.ts`, and `master.semantic_family`; and any schema or service. None of these change the dictionary; they realize it.

## 12. Naming note

"Metric Directory" is distinct from **MCF** (Metric Context Framework — the runtime metric stack) and **MMS** (Metric Management System — the lifecycle). The directory is the value-organizing dictionary layered *before* authoring. The term "family" in this chapter means a directory **Family (theme)** and must not be conflated with the generator tooling's grain-template "family" (which maps to a directory **Group**) or with `master.semantic_family` (a field-level semantic type). Disambiguating these names is part of the parked implementation work (§11).
