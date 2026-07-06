---
uid: business-concept-registry-f3-dbcp
title: Business Concept Registry — F3 DBCP packet
description: Database Change Protocol packet for the F3 Registry authoring service's two additive schema changes (Phase F item F3) — the supersession_proposal table and the version-row provenance columns. Proposal for review — no DDL authored, no migration executed. Additive on the F2 concept_registry schema; sequences after the F2 migration is executed.
status: approved
date: 2026-05-21
project: bc-docs
domain: contracts
subdomain: catalog
focus: schema
---

# Business Concept Registry — F3 DBCP packet

> **What this is — and what it is not.** Phase F item **F3** of the BCF build
> plan carries a small additive DBCP alongside the `RegistryAuthoringService`.
> This is the **Database Change Protocol packet** for that DBCP. It is a
> **proposal for review**. **No DDL is authored, no migration file is written,
> nothing is applied to any database.** Approving this packet authorizes the
> *next* step — authoring the F3 forward / revert migration and the Drizzle
> mirror — which is itself reviewed before execution (§9). It builds on the
> accepted F3 authoring-service design note
> (`business-concept-registry-f3-authoring-service-design.md`) and is additive
> on the F2 `concept_registry` schema (PR #50, merged to `bc-core/main`; **not
> yet executed**).
>
> **Rev 2 (2026-05-21)** — operator review-back resolved the four §8 questions:
> the `resolution_supersession_id` outcome link is **adopted** (§2.1, §3); no
> write-once trigger; dependent-distinctness is an F3 service pre-check;
> `resolved_at` / `resolved_by` naming kept. **`status: approved`** — approved
> for DDL authoring; the authored DDL returns for review before execution (§9).

## 1. Change posture — additive only

F3's DBCP makes **two additive changes**, both inside the existing F2
`concept_registry` schema. It is purely additive:

- It adds **one new table** — `concept_registry.supersession_proposal`.
- It adds **four new nullable columns** — two provenance columns on each of
  `concept_registry.entity_version` and
  `concept_registry.business_concept_version`.
- It **restructures nothing**. No existing `concept_registry` column is altered
  or dropped; no existing constraint, index, or trigger is changed.
- **No foreign key crosses** out of `concept_registry` — not to `contract.*`,
  not anywhere. The F2 coexistence rule (DEC-02f5a9 §6) holds unchanged.

The F3 DBCP sequences **after the F2 migration is executed** — it is additive on
F2's tables, and the new table's FKs plus the `ALTER TABLE … ADD COLUMN`
statements need those tables to exist (§5).

## 2. The two changes

### 2.1 `concept_registry.supersession_proposal` — the supersession cascade table

The table behind the F3 design note §3. A meaning-bearing change to an entity
mints a new `entity_id` and an `entity_supersession` row (F1.2). Every entity
whose identity-bearing reference points at the superseded entity must re-point —
and F1.2 locked that this is **governed proposals, never auto-rewrite**. F3
writes one proposal row per affected dependent entity; an operator actions or
dismisses each one. The table makes the cascade auditable and operator-paced.

| Column | Type | Notes |
|---|---|---|
| `proposal_id` | uuid PK | Surrogate id |
| `entity_supersession_id` | uuid FK→`entity_supersession` | The supersession event that spawned this proposal — carries the superseded → successor pair |
| `dependent_entity_id` | uuid FK→`entity` | The affected dependent — it holds an identity-bearing reference at the superseded entity |
| `proposal_status` | text | `open` / `actioned` / `dismissed` — default `open` |
| `created_at` | timestamptz | When F3 raised the proposal |
| `created_by` | text | The triggering supersession's author (Cognito `sub`) |
| `resolved_at` | timestamptz null | When an operator actioned or dismissed it; NULL while `open` |
| `resolved_by` | text null | Who resolved it; NULL while `open` |
| `resolution_supersession_id` | uuid null FK→`entity_supersession` | The re-author this proposal produced — the dependent's own supersession (D → D′). Set iff `proposal_status = 'actioned'`; NULL for `open` / `dismissed` (§3) |

Nine columns. Design points:

- **The superseded → successor pair is referenced, not copied.** That pair is
  already an `entity_supersession` row; the proposal FK-references it rather than
  duplicating both ids as columns (D162 rule 4 — one source of truth). The
  "proposed re-point" the F3 note §3 names is fully determined by
  `(entity_supersession_id, dependent_entity_id)`: the dependent's
  identity-bearing reference(s) at the superseded entity should re-point to the
  successor.
- **The cascade is an entity-supersession phenomenon.** The identity-reference
  graph is entity → entity; superseding a *concept* does not fan out the same
  way. One `supersession_proposal` table, tied to `entity_supersession` — the
  name follows the F3 design note §3.
- **`proposal_status`** — `open` (raised by F3, awaiting an operator) → either
  `actioned` (the operator re-authored the dependent so it re-points) or
  `dismissed` (the operator decided the dependent should not re-point). Both
  terminal states are governed decisions; dismissal is what keeps the cascade
  *governed* rather than *delayed auto-rewrite*.
- **Actioning a proposal is a governed re-author** of the dependent entity —
  itself an F3 operation requiring an authorization reference (F3 note §1).
  Re-pointing an identity-bearing reference changes the dependent's
  identity-bearing property set: a meaning-bearing change, which mints a new
  `entity_id` for the dependent and its own `entity_supersession` row (F1.2).
  `resolution_supersession_id` records exactly that row — the cascade outcome
  is **emitted, not reconstructed** (Invariant VI). The actioning's
  certification provenance is reachable through it (proposal →
  `resolution_supersession_id` → the successor entity's `entity_version` → the
  §2.2 `certification_record_id`), so no separate provenance column is
  duplicated onto the proposal (D162 rule 4).
- **The cascade graph is fully traversable.** Each proposal links the
  supersession that *spawned* it (`entity_supersession_id`) and the
  supersession it *produced* (`resolution_supersession_id`) — both into
  `entity_supersession`. The recursive cascade — a re-author triggering
  further proposals — is a graph of `entity_supersession` ↔
  `supersession_proposal` edges, every edge an explicit FK (Invariant IV).

### 2.2 Provenance columns on the two version tables

The F3 design note §5 stamps each F3-written version row with its authorizing
provenance. Four new columns — the same pair on each version table:

| Column | On table | Type | Notes |
|---|---|---|---|
| `certification_record_id` | `entity_version` | uuid null | Primary — the governed-approval artifact (`contract.certification_record`); operationally mandatory (§4) |
| `panel_run_uid` | `entity_version` | uuid null | Optional — the AI-panel evidence (`contract.panel_output_record`); supplementary |
| `certification_record_id` | `business_concept_version` | uuid null | As above |
| `panel_run_uid` | `business_concept_version` | uuid null | As above |

Both are **plain `uuid` soft references — no foreign key.**
`certification_record` and `panel_output_record` live in the `contract` schema;
the F2 coexistence rule forbids an FK crossing `concept_registry` → `contract`.
F3 verifies the `certification_record` at the service layer before it writes
(F3 note §1); the database holds the value, not a constraint on it (§4).

Because both version tables are already append-only — the F2
`tg_reject_version_mutation` trigger rejects every `UPDATE`/`DELETE` — the new
provenance columns are **immutable for free**: set once at `INSERT`, never
updatable. F3's DBCP adds **no trigger**; Invariant III holds unchanged.

## 3. Constraints

| Constraint | Table | Effect |
|---|---|---|
| Primary key | `supersession_proposal` | `proposal_id` |
| Foreign keys | `supersession_proposal` | `entity_supersession_id` and `resolution_supersession_id` → `entity_supersession(supersession_id)`; `dependent_entity_id` → `entity(entity_id)` — D162 rule 3 |
| Status domain | `supersession_proposal` | CHECK — `proposal_status IN ('open','actioned','dismissed')` |
| Resolution consistency | `supersession_proposal` | CHECK — `open` ⇒ `resolved_at` and `resolved_by` both NULL; `actioned`/`dismissed` ⇒ both NOT NULL |
| Outcome-link presence | `supersession_proposal` | CHECK — `resolution_supersession_id` IS NOT NULL **iff** `proposal_status = 'actioned'`; NULL for `open` / `dismissed`. A plain same-row CHECK — the database enforces it cleanly |
| One open proposal per pair | `supersession_proposal` | Partial unique — `UNIQUE(entity_supersession_id, dependent_entity_id) WHERE proposal_status = 'open'` — no duplicate open proposal for one (supersession, dependent) pair |

`superseded ≠ successor` needs no CHECK here — it is already guaranteed by
`entity_supersession`'s own `entity_supersession_distinct_chk`, reached through
the FK. Dependent-distinctness is an F3 service pre-check, not a DB CHECK (§8).

**Indexes** follow the query patterns (D162 rule 7):

- `idx_supersession_proposal_dependent` on `dependent_entity_id` — "proposals
  affecting dependent D".
- `idx_supersession_proposal_supersession` on `entity_supersession_id` —
  "proposals from supersession S".
- `idx_supersession_proposal_resolution` on `resolution_supersession_id WHERE
  resolution_supersession_id IS NOT NULL` — the cascade-graph reverse lookup
  ("which proposal produced supersession S").
- the partial unique `uq_supersession_proposal_open` doubles as the
  open-proposal worklist index.
- `idx_entity_version_certification` on
  `entity_version(certification_record_id) WHERE certification_record_id IS NOT
  NULL`, and `idx_business_concept_version_certification` likewise — the
  provenance reverse lookup ("which versions did certification X authorize").
  `panel_run_uid` is supplementary and stays unindexed.

## 4. Why the provenance columns are nullable

The F3 design note §1 makes `certification_record_id` **operationally
mandatory** — F3 writes no version row without a verified reference — yet the
column is **nullable**. These are not in tension; they are two layers doing two
different jobs.

- **The database is the structural floor.** It can hold a `uuid`. It cannot
  resolve that `uuid` to a valid, approved `certification_record` — that record
  lives in the `contract` schema, and the F2 coexistence rule forbids a
  cross-schema FK. A `NOT NULL` would let the database assert *presence* while
  remaining unable to assert *validity* — half an invariant, which reads as a
  guarantee the database cannot keep.
- **F3 is the verification layer.** F3 owns provenance end to end — presence
  *and* cross-schema validity. It resolves the reference against
  `contract.certification_record` and rejects the write on failure (F3 note §1).
- **Nullable keeps the ownership line clean.** The column makes no claim; F3
  makes the claim. This mirrors the F2 split exactly — the database is the
  structural floor, F3 adds what the database cannot express.

The one operational exemption (F3 note §1 — the F4 governed-vocabulary seed)
touches `characteristic`, not the version tables, so it does not bear on these
columns: every `entity_version` / `business_concept_version` row is written by a
governed, certification-bearing F3 operation.

## 5. Sequencing — additive on the executed F2 schema

The F3 DBCP sequences after the F2 migration is **executed**, not merely merged:

- `supersession_proposal` carries FKs into `concept_registry.entity` and
  `concept_registry.entity_supersession` — those tables must exist.
- The provenance columns are `ALTER TABLE … ADD COLUMN` on
  `concept_registry.entity_version` and `business_concept_version` — likewise.

Because the F3 migration runs on a freshly-built `concept_registry` (greenfield —
F2 having just created it) the version tables are **empty** when the columns are
added: `ADD COLUMN` has nothing to backfill, and no default is needed. Should
the F3 migration ever run against a populated `concept_registry`, the columns
still add cleanly as nullable; pre-existing rows would carry NULL provenance —
the honest record for rows written before the columns existed.

## 6. Rollback

F3's DBCP is additive, so its revert is mechanical and lossless of F2 state:

- `DROP TABLE concept_registry.supersession_proposal` — the table is F3-only;
  nothing in F2 references it.
- `ALTER TABLE … DROP COLUMN certification_record_id, DROP COLUMN panel_run_uid`
  on each version table.

The revert touches nothing else — no F2 table, constraint, index, or trigger,
and nothing in any other schema. It pairs with the forward migration as a
`.revert.sql`, exactly as F2's did. As with F2, this is a **pre-production**
posture: while the Registry holds only authored vocabulary and no chain depends
on it, it can be reverted freely. Once `supersession_proposal` carries
operational cascade history, retiring it would be a separate governed change,
not a mechanical revert.

## 7. Compliance

**D162 database rules.** `supersession_proposal` has 9 columns — well under 20
(rule 6). Every reference is FK-constrained — `entity_supersession_id`,
`resolution_supersession_id`, `dependent_entity_id` (rule 3). No
JSONB (rule 1); no counter (rule 2). The superseded → successor pair is **not**
copied onto the proposal — it is reached through the `entity_supersession` FK
(rule 4, one source of truth). The provenance columns of §2.2 are deliberate
cross-schema **soft** references — the one sanctioned departure from rule 3,
forced by the F2 coexistence rule and documented as such (§4). Proposals are
never deleted — a resolved proposal is retained as audit history — so no
`archived_at` is needed (rule 8 governs *how* to soft-delete, not *that* every
table must). `snake_case`, `{noun}_id` PK, `fk_` / `idx_` / `uq_` naming (D148).

**Foundation invariants.** The DBCP *strengthens* the invariants:

- **Invariant VI (evidence emitted, not inferred).** The provenance columns make
  each version row's authorizing approval **emitted** onto the row — the
  certification reference is recorded at the write, not reconstructed later.
- **Invariant IV (references explicit).** Provenance is an explicit named column
  holding an explicit id; the supersession cascade is explicit proposal rows,
  not an implicit or inferred fan-out.
- **Invariant III (state immutable).** `supersession_proposal` has a mutable
  `proposal_status` lifecycle — but that is governance state, not meaning or
  evaluation content, exactly like the F2 anchor lifecycle pointers. The
  provenance columns are immutable for free (§2.2).

Repair-location: **E (storage)** — it stores the supersession-cascade and
provenance mechanisms the F3 design note locked (a B-level governance surface).
Additive substrate.

## 8. Review resolution — rev 2 (2026-05-21)

Operator review-back resolved the four questions this packet raised:

1. **Proposal → outcome link — adopted.** `supersession_proposal` carries
   `resolution_supersession_id` (nullable FK → `entity_supersession`), set when
   a proposal is actioned. An actioned cascade outcome is **emitted, not
   reconstructed** (Invariant VI). The link targets `entity_supersession`, not
   `business_concept_supersession`: re-pointing an identity-bearing reference is
   a meaning-bearing change to the *dependent entity*, so the outcome is the
   dependent's own supersession (D → D′). Reflected in §2.1, §3.
2. **Write-once guard — not added.** F3 sole-write-path discipline plus the
   `proposal_status` transitions are sufficient for v1; no `BEFORE UPDATE`
   trigger is added unless a real bypass risk surfaces. The DBCP stays "a new
   table plus new columns" — no procedural weight.
3. **Dependent-distinctness — an F3 service pre-check.** The database cannot
   CHECK `dependent_entity_id` against the superseded / successor entities
   without denormalizing them out of `entity_supersession`. F3 pre-checks
   `dependent ≠ superseded` and `dependent ≠ successor` and rejects with a
   clean, explained error — the acyclic-pre-check family (F3 note §1).
4. **Naming — `resolved_at` / `resolved_by` kept.** One timestamp/actor pair
   covers both terminal states; `proposal_status` records which.

**One added guard (operator review-back).** `resolution_supersession_id` is
required **iff** `proposal_status = 'actioned'` — NOT NULL when actioned, NULL
for `open` and `dismissed`. This is a plain same-row, multi-column CHECK (the
shape of F2's `business_concept_kind_metadata_chk`); the database enforces it
cleanly, so it is a **DB CHECK**, not only an F3 service invariant — §3,
"Outcome-link presence."

## 9. What approval of this packet authorizes

Approving this packet authorizes **only** the next step: authoring the F3
forward / revert migration and the Drizzle-mirror update — landing in
`bc-core/docker/redesign/migrations/` and
`bc-core/src/database/schema/concept-registry/`, matching this packet. **That
written DDL returns for a final review before it is executed against any
database.** Approval of this packet is *not* approval to run DDL.

The F3 migration sequences after the F2 migration is executed (§5). The
`RegistryAuthoringService` — the other half of the F3 build — builds against
this schema.

This packet is **`approved`** (rev 2, 2026-05-21) for DDL authoring — the four
§8 questions resolved and the outcome-link guard added in the operator
review-back. The authored DDL returns for review before execution.
