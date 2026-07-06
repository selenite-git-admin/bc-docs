---
uid: business-concept-registry-f2-schema-dbcp
title: Business Concept Registry — F2 schema DBCP packet
description: Database Change Protocol packet for the Business Concept Registry schema (Phase F item F2). Proposal for review — no DDL authored, no migration executed. Authorizes nothing until operator-approved.
status: approved
date: 2026-05-21
project: bc-docs
domain: contracts
subdomain: catalog
focus: schema
---

# Business Concept Registry — F2 schema DBCP packet

> **What this is — and what it is not.** Phase F item **F2** of the BCF build
> plan: the Database Change Protocol packet for the Business Concept Registry
> schema. It is a **proposal for review**. **No DDL is authored, no migration
> file is written, nothing is applied to any database.** Approving this packet
> authorizes the *next* step — authoring the DDL and migration — which is itself
> reviewed before execution (§10). It builds on the accepted F1 forward-design
> note (`business-concept-registry-f1-forward-design.md`) and implements
> DEC-02f5a9 §1–§3.
>
> **Rev 5 (2026-05-21)** — revs 2-4 applied the schema fixes, resolved the five
> open questions (§9), and locked the schema name **`concept_registry`**; rev 5
> adds two hardening constraints from the DDL-authoring review — alias
> normalized-uniqueness and the active-version-required CHECK (§4). **`status:
> approved`** — approved for DDL authoring; the authored DDL returns for review
> before execution (§10).

## 1. Change posture — additive only

F2 creates a new **`concept_registry`** schema in the platform database
(`bc_platform_dev`). It is **purely additive**:

- It adds new tables in a new schema. The current redesign DDL does not define a
  `concept_registry` schema, so F2 creates it clean.
- It **changes nothing** in the existing `contract` schema — no column on
  `contract.business_field`, `contract.business_object`,
  `contract.canonical_field`, or any other existing table is added, altered, or
  dropped.
- **No foreign key crosses** between the new `concept_registry` schema and any existing
  table, in either direction.

The Registry is built alongside the running existing chain (DEC-02f5a9 §6); the
existing chain is untouched and keeps serving the demo tenant.

## 2. The `concept_registry` schema — nine tables

Each versioned subject (entity, business concept) splits into an **anchor** and
an **immutable version** table. This is how the F1.2 dual-ID model and the F1.2
immutability rule become structural (§3):

- the **anchor** holds the stable semantic identity, the **immutable
  meaning**, and the transitioning lifecycle pointers;
- the **version** table holds only immutable descriptive content; a version row,
  once written, is never updated.

| Table | Concern |
|---|---|
| `concept_registry.entity` | Entity anchor — stable identity + lifecycle pointers |
| `concept_registry.entity_version` | Immutable entity descriptive versions |
| `concept_registry.business_concept` | Concept anchor — stable identity + **immutable meaning** + lifecycle pointers |
| `concept_registry.business_concept_version` | Immutable concept descriptive versions |
| `concept_registry.characteristic` | Property-characteristic vocabulary (governed-open, F1.3) |
| `concept_registry.representation_term` | Representation-term vocabulary (closed set, F1.3) |
| `concept_registry.alias` | Governed aliases for entities and characteristics (F1.3) |
| `concept_registry.entity_supersession` | Entity supersession lineage |
| `concept_registry.business_concept_supersession` | Concept supersession lineage |

There is no separate `property` table: a property belongs to exactly one entity
(Registry §5), so a property *is* a Business Concept — one table, not two. The
build plan's "entity / property / business_concept" reconciles as
entity + business_concept, with the property's semantics carried on the concept
anchor (review Fix 1, §9).

### 2.1 `concept_registry.entity` — entity anchor

| Column | Type | Notes |
|---|---|---|
| `entity_id` | uuid PK | Stable semantic identity |
| `lifecycle_state` | enum | `draft`/`review`/`approved`/`active`/`superseded` — transitions |
| `active_version_id` | uuid null | Current descriptive version — composite FK to `entity_version` (§4 active-version integrity) |
| `archived_at` | timestamptz null | Soft delete (D162 rule 8) |
| `created_at` | timestamptz | |
| `created_by` | text | Cognito `sub` |

An entity carries no immutable "meaning" columns — its grain *is* the set of its
`identity_bearing` concepts (F1.1), derived, not stored. `is_composite` is a
view (D162 rule 2).

### 2.2 `concept_registry.entity_version` — immutable entity versions

| Column | Type | Notes |
|---|---|---|
| `entity_version_id` | uuid PK | Immutable version-row id |
| `entity_id` | uuid FK→`entity` | The anchor this version belongs to |
| `canonical_name` | text | Self-disambiguating name (Registry §3); never namespace-prefixed |
| `definition` | text | |
| `family_code` | text null | Classification only — not identity (Registry §3) |
| `owner_domain` | text null | Stewardship classification |
| `provenance_json` | jsonb null | Opaque provenance evidence |
| `created_at` | timestamptz | |
| `created_by` | text | |

**Wholly immutable** — no row is updated after insert (§3). Carries `UNIQUE(entity_id, entity_version_id)` for the §4 active-version composite FK.

### 2.3 `concept_registry.business_concept` — concept anchor (identity + meaning)

| Column | Type | Notes |
|---|---|---|
| `concept_id` | uuid PK | Stable semantic identity |
| `entity_id` | uuid FK→`entity` | Owning entity — a concept belongs to exactly one entity (Registry §5) |
| `kind` | enum | `value` / `reference` |
| `identity_role` | enum | `identity_bearing` / `descriptive` — structural-grain sense (F1.1) |
| `characteristic_id` | uuid null FK→`characteristic` | `value` kind — required; `reference` — null |
| `representation_term` | text null FK→`representation_term` | `value` kind — required; `reference` — null |
| `data_type` | text null | `value` kind |
| `unit` | text null | `value` kind |
| `semantic_role` | text null | `value` kind |
| `reference_role` | text null | `reference` kind — required (e.g. `bill-to`) |
| `target_entity_id` | uuid null FK→`entity` | `reference` kind — required |
| `lifecycle_state` | enum | five-state — transitions |
| `active_version_id` | uuid null | Current descriptive version — composite FK to `business_concept_version` (§4 active-version integrity) |
| `archived_at` | timestamptz null | Soft delete |
| `created_at` | timestamptz | |
| `created_by` | text | |

The columns `entity_id` through `target_entity_id` are the concept's **meaning**
— **immutable, write-once** (§3, review Fix 1). `lifecycle_state`,
`active_version_id`, `archived_at` are the transitioning governance pointers.

### 2.4 `concept_registry.business_concept_version` — immutable concept versions

| Column | Type | Notes |
|---|---|---|
| `concept_version_id` | uuid PK | Immutable version-row id |
| `concept_id` | uuid FK→`business_concept` | The anchor this version belongs to |
| `definition` | text | |
| `provenance_json` | jsonb null | |
| `created_at` | timestamptz | |
| `created_by` | text | |

**Wholly immutable** — descriptive content only; no lifecycle column (review
Fix 4). Carries `UNIQUE(concept_id, concept_version_id)` for the §4 active-version composite FK.

### 2.5 Vocabulary and lineage tables

**`concept_registry.characteristic`** — `characteristic_id` uuid PK, `term` text unique,
`definition` text, `lifecycle_state` enum, `created_at`, `created_by`,
`archived_at`. Governed-open: rows added through the authoring panel + operator
confirm.

**`concept_registry.representation_term`** — `term` text PK, `definition` text,
`added_by` text, `added_at` timestamptz. Closed: seeded with the F1.3 §3 v1 set;
additions require a governance act (review Q(c) — reference table + FK chosen).

**`concept_registry.alias`** — `alias_id` uuid PK, `alias_text` text,
`alias_normalized` text (generated: lowercased, trimmed, separator-collapsed),
`target_kind` enum (`entity` / `characteristic`), `target_entity_id` uuid null
FK→`entity`, `target_characteristic_id` uuid null FK→`characteristic`,
`added_by`, `added_at`. `UNIQUE(target_kind, alias_normalized)` — a normalized
alias resolves to one concept within a kind, so the synonym-control surface
stays unambiguous (DEC-02f5a9 §6 homonym rule). First-class governed aliases
(F1.3) — the bounded set the panel's synonym check tests against.

**`concept_registry.entity_supersession`** — `supersession_id` uuid PK,
`predecessor_entity_id` uuid FK→`entity`, `successor_entity_id` uuid FK→`entity`,
`reason` text, `superseded_at` timestamptz, `superseded_by` text.

**`concept_registry.business_concept_supersession`** — `supersession_id` uuid PK,
`predecessor_concept_id` uuid FK→`business_concept`, `successor_concept_id` uuid
FK→`business_concept`, `reason` text, `superseded_at` timestamptz,
`superseded_by` text.

Supersession is **two typed tables with real FKs**, not one polymorphic table
(review Fix 3 — D162 rule 3: every reference to a PK is an explicit FK).

## 3. Identifiers, the versioning model, and immutability

- **Surrogate uuid PKs throughout** (D162 / ISO 11179 naming: `{noun}_id`).
- **Dual-ID model (F1.2).** A stable **semantic identity** (`entity_id`,
  `concept_id`) is the anchor PK; an **immutable version-row id**
  (`entity_version_id`, `concept_version_id`) is the version-table PK.
- **What is immutable, precisely** (review Fix 4):
  - A concept's **meaning** — the `business_concept` columns `entity_id` through
    `target_entity_id` — is **write-once**. A `BEFORE UPDATE` trigger rejects any
    change to a meaning column (§4). A meaning change therefore *cannot* drift a
    `concept_id`; it can only be a new anchor row = a new `concept_id` (review
    Fix 1).
  - Every **version row** (`entity_version`, `business_concept_version`) is
    **wholly immutable** — inserted once, never updated. Lifecycle does not live
    on version rows.
  - The anchor's **lifecycle pointers** (`lifecycle_state`, `active_version_id`,
    `archived_at`) transition — these are the only mutable columns in the
    schema, and they are governance pointers, not meaning or content. This
    mirrors Foundation's contract grammar (an immutable body, a transitioning
    `governance.state`).
- **Change taxonomy → rows:**
  - *Descriptive change* (definition, provenance) → a new immutable version row;
    the anchor's `active_version_id` is re-pointed. Same `concept_id`.
  - *Meaning-bearing change* → a new anchor (new `concept_id`) + a
    `business_concept_supersession` row. The predecessor's `lifecycle_state`
    moves to `superseded`.
- **Audit pins versions; resolution resolves identity** (F1.2). Contracts and
  evidence reference a `*_version_id` (immutable — Invariants V, VI). Authoring
  and resolution work with the `*_id` and resolve via `active_version_id`.

## 4. Constraints

| Constraint | Table | Effect |
|---|---|---|
| Primary keys | all | The `*_id` / `*_version_id` / `term` columns above |
| **Anti-synonym, value concepts** | `business_concept` | Partial unique `UNIQUE(entity_id, characteristic_id) WHERE kind='value' AND lifecycle_state='active' AND archived_at IS NULL` — at most one active value concept per `(entity, characteristic)` (review Q(a) — representation term is *not* in the key) |
| **Anti-synonym, reference concepts** | `business_concept` | Partial unique `UNIQUE(entity_id, reference_role, target_entity_id) WHERE kind='reference' AND lifecycle_state='active' AND archived_at IS NULL` — reference identity is `(role, target)` (review Fix 2); `bill-to → Customer` and `ship-to → Customer` coexist, two `bill-to → Customer` do not |
| Meaning immutability | `business_concept` | `BEFORE UPDATE` trigger rejects any change to a meaning column (`entity_id`…`target_entity_id`); permits `lifecycle_state` / `active_version_id` / `archived_at` |
| Version immutability | `entity_version`, `business_concept_version` | `BEFORE UPDATE` and `BEFORE DELETE` triggers reject all changes — version rows are append-only |
| `kind` / metadata disjoint | `business_concept` | CHECK — `value` rows: `characteristic_id` + `representation_term` non-null, reference columns null; `reference` rows: `reference_role` + `target_entity_id` non-null, value columns null |
| Foreign keys | all | Every cross-table reference is FK-constrained (D162 rule 3) — concept→entity, concept→characteristic, concept→representation_term, reference-concept→target entity, alias targets, both supersession tables |
| **Active-version integrity** | `entity`, `business_concept` | The anchor's `active_version_id` must reference a version of the **same anchor** — a composite FK, not a plain one (see below) |
| Active-version required | `entity`, `business_concept` | CHECK `(lifecycle_state = 'draft' OR active_version_id IS NOT NULL)` — a non-draft anchor must point at a descriptive version (review Fix 3) |
| Closed representation set | `business_concept.representation_term` | FK → `representation_term.term` — only governed terms admissible |
| Alias target exclusivity | `alias` | CHECK — exactly one of `target_entity_id` / `target_characteristic_id` non-null, matching `target_kind` |
| Alias uniqueness | `alias` | `UNIQUE(target_kind, alias_normalized)` on the generated normalized form (lowercase, trim, separator-collapse) — a normalized alias is unambiguous within a target kind (review Fix 2) |
| Acyclic identity graph | `business_concept` | See §5 |

**Active-version integrity.** A plain `active_version_id` FK cannot guarantee the
referenced version belongs to the same anchor. The DDL enforces it with composite
uniqueness on the version tables and composite FKs from the anchors:

- `entity_version` carries `UNIQUE(entity_id, entity_version_id)`; `entity`
  carries `FOREIGN KEY (entity_id, active_version_id) REFERENCES
  entity_version(entity_id, entity_version_id)`.
- `business_concept_version` carries `UNIQUE(concept_id, concept_version_id)`;
  `business_concept` carries `FOREIGN KEY (concept_id, active_version_id)
  REFERENCES business_concept_version(concept_id, concept_version_id)`.

Bootstrapping order: insert the anchor with `active_version_id` NULL, insert the
first version row, then update only the anchor's `active_version_id` pointer.

Indexes follow the query patterns (D162 rule 7): the anchor FKs, the two
anti-synonym partial indexes, and `alias_text` for the panel's synonym lookup.

## 5. Acyclic identity-graph enforcement

The identity-reference graph (F1.1): a `business_concept` that is
`kind='reference'` **and** `identity_role='identity_bearing'` is an
identity-bearing edge from `entity_id` to `target_entity_id`. That graph must be
a DAG.

PostgreSQL cannot express a cross-row acyclic constraint declaratively.
**Proposed strategy — two layers:**

1. **A `BEFORE INSERT` trigger** on `business_concept`: when an
   `identity_bearing` reference concept is inserted, a recursive CTE walks the
   identity-bearing reference edges from `target_entity_id`; if the walk reaches
   the concept's own `entity_id`, the trigger raises and the write is rejected.
2. **An F3 application-level pre-check** running the same walk, for a clean,
   explained rejection — the trigger is the guarantee, the pre-check is the good
   error message.

## 6. Coexistence with the existing BF/BO/CF tables

Until the Phase G cutover, the Registry and the existing vocabulary tables run
side by side:

- The `concept_registry` schema and the `contract` schema are **independent** — no FK,
  no view, no trigger crosses between them.
- `contract.business_field` / `business_object` / `canonical_field` and the
  existing chain are **untouched** and keep operating.
- New authoring goes to the Registry; the existing chain keeps the demo tenant
  alive (DEC-02f5a9 §6; build plan §16.2).
- **Phase G** retires or compatibility-wraps the old tables — a **separate
  DBCP** (build plan item G6), not F2.

## 7. Rollback and retirement posture

- **Rollback of F2.** Because F2 is additive-only, rollback is
  `DROP SCHEMA concept_registry CASCADE` — it removes only the new schema and has **zero
  impact** on the existing `contract` schema, the running chain, or the demo
  tenant. No existing data is touched.
- **Pre-cutover**, the Registry can be dropped and rebuilt freely while it holds
  only authored vocabulary and no chain depends on it.
- **Retirement of the old tables** is *not* F2 — it is Phase G item G6, a
  separate operator-approved DBCP.

## 8. Compliance

**D162 database rules.** No JSONB for queryable data — only `provenance_json` is
JSONB and it is opaque, never filtered/joined (rule 1). No denormalized counters
— `is_composite` is a view (rule 2). FK on every reference, including the two
typed supersession tables (rule 3). `alias` is a shared table (rule 5); the two
typed supersession tables trade rule 5's "shared" for rule 3's "real FK", the
correct precedence and the operator's chosen resolution. Every table ≤ 20
columns — `business_concept` is the largest at 16 (rule 6). Soft delete via
`archived_at` (rule 8). `snake_case`, `{noun}_id` PKs, `idx_` / `fk_` naming
(D148).

**Foundation invariants.** Invariant III is upheld structurally: version rows
are append-only and trigger-protected; a concept's meaning is write-once and
trigger-protected; supersession is a new anchor + a lineage row, never a
rewrite. The only mutable columns are the anchor lifecycle pointers — governance
state, not content, mirroring the contract grammar. The schema is
repair-location **E (storage)** — it stores the model DEC-02f5a9 and F1 decided.

## 9. Review resolution — rev 2 (2026-05-21)

**Four schema fixes applied:**

1. **Meaning on the concept anchor.** All meaning-bearing attributes
   (`characteristic_id`, `representation_term`, `kind`, `unit`, …) move from the
   version table to the `business_concept` anchor and are write-once
   (trigger-enforced). A stable `concept_id` can no longer drift semantically; a
   meaning change is structurally a new `concept_id` (§2.3, §3).
2. **Kind-based identity rule.** Value concepts key on
   `(entity_id, characteristic_id)`; reference concepts key on
   `(entity_id, reference_role, target_entity_id)`. `representation_term` is
   nullable, required only for `value` kind (§4).
3. **Typed supersession tables.** `concept_registry.supersession` (polymorphic) is
   replaced by `concept_registry.entity_supersession` and
   `concept_registry.business_concept_supersession`, each with real typed FKs (§2.5).
4. **Lifecycle vs immutability.** Lifecycle leaves the version rows entirely —
   version rows are wholly immutable; `lifecycle_state` / `active_version_id` /
   `archived_at` live on the anchor as the only mutable columns, precisely
   scoped (§3).

**Five questions — resolved:**

- **(a)** Value-concept key is `(entity_id, characteristic_id)`; representation
  term is **not** in the key. Reference concepts get their own rule (Fix 2).
- **(b)** Anchor + version split — kept.
- **(c)** Representation term — governed reference table + FK.
- **(d)** Cascade-proposal queue — deferred to F3 / service workflow; no F2
  table.
- **(e)** `concept_registry` schema in the Platform DB — confirmed; F2 creates it.

## 10. What approval of this packet authorizes

Approving this packet authorizes **only** the next step: authoring the actual
DDL and migration — landing in `bc-core/docker/redesign/` and the bc-core
Drizzle schema, matching this packet. **That written DDL returns for a final
review before it is executed against any database.** Approval of this packet is
*not* approval to run DDL.

This packet is **approved** (rev 5, 2026-05-21) for DDL authoring. F2 proceeds
to DDL authoring; the written DDL returns for review before execution. F3 (the
authoring service) and F4 (the governed-vocabulary seed) build against this
schema.
