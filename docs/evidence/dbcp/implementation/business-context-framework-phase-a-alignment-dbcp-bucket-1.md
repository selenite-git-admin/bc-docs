---
uid: business-context-framework-phase-a-alignment-dbcp-bucket-1
title: Business Context Framework — Phase A alignment DBCP packet (Bucket 1)
description: Database Change Protocol packet for the Phase A Bucket-1 governance scope-alignment — framework_policy, operator_confirm_rule, phase_state, certification_record. Adds the `registry` governance scope and the Model A Registry operation shape to the certification ledger. Specification only — the DDL build step follows separately. Approved rev 2, 2026-05-21.
status: approved
date: 2026-05-21
project: bc-docs
domain: contracts
subdomain: governance
focus: schema
---

# Business Context Framework — Phase A alignment DBCP packet (Bucket 1)

> **What this is.** The Database Change Protocol packet for the **Bucket 1**
> surfaces of the accepted Phase A governance scope-alignment design note —
> `framework_policy`, `operator_confirm_rule`, `phase_state`, and
> `certification_record`. It specifies, table by table, what changes and why.
> **It contains no DDL.** Per the Database Change Protocol no migration is
> written; the DDL build step (§5) follows separately.
> `status: approved` — rev 2, operator-approved 2026-05-21 (§8).

## 1. Scope, authority, constraints

**Authority.** DEC-02f5a9 (D414); the accepted Phase A governance
scope-alignment design note (`business-context-framework-phase-a-governance-scope-alignment-design.md`)
— locks **L1–L4** and **O1 = Model A** (operator review-back 2026-05-21).

**In scope — Bucket 1 (4 tables).** The critical-path-for-B6 governance
surfaces: `contract.framework_policy`, `contract.operator_confirm_rule`,
`contract.phase_state`, `contract.certification_record`.

**Out of scope.**

- **Bucket 2** — `authoring_panel_rejection_log`, `intake_queue` — waits for
  the B6 design (design-note O2, still open).
- **Bucket 3** — `primitive_provenance` and the legacy BF/BO/CF paths — Phase G.
- **No DDL.** This packet does not write the migration SQL, the Drizzle schema
  mirrors, or the F3 / C5 service code. Those are the build step that follows
  approval (§5).
- **No `framework_policy` / `phase_state` row authoring.** Creating the first
  `registry`-scoped policy or phase rows is a later authoring act, not a DDL
  change.

**Locked inputs from the design note.**

- **L2** — one governance scope, `registry`.
- **L4** — the old `bf_bo` / `cf` / `mapping` scope values and the
  `business_field` / `business_object` / `canonical_field` primitive-type
  values are **kept**; this packet is purely additive / loosening. The old
  values are dropped only at the Phase G cutover.
- **O1 = Model A** — a Registry certification row identifies the **authorized
  Registry authoring operation**, not an already-existing primitive row.

## 2. Bucket-1 table change specification

### 2.1 `contract.framework_policy`

| | |
|---|---|
| **Change** | Extend the `framework_policy_scope_code_chk` CHECK to admit `registry`. |
| **From** | `scope_code IN ('bf_bo','cf','mapping','all')` |
| **To** | `scope_code IN ('bf_bo','cf','mapping','all','registry')` |
| **Why** | L2 — `registry` is the one governance scope for Registry authoring; a `registry`-scoped `framework_policy` row is what governs every B6 panel run. L4 — old values retained. |
| **Other impact** | None. The `framework_policy_active_per_scope_uniq` index (one active policy per scope) extends automatically — one active `registry` policy becomes expressible. No row changes, no data migration. |

### 2.2 `contract.operator_confirm_rule`

| | |
|---|---|
| **Change** | Extend the `operator_confirm_rule_scope_chk` CHECK to admit `registry`. |
| **From** | `scope IN ('bf','bo','cf','mapping','any')` |
| **To** | `scope IN ('bf','bo','cf','mapping','any','registry')` |
| **Why** | L2 / L4. Operator-confirm rules for Registry transitions are scoped `registry`; the `any` wildcard is retained for cross-scope rules. |
| **Other impact** | None. No row changes. |

### 2.3 `contract.phase_state`

| | |
|---|---|
| **Change** | Extend the `phase_state_scope_code_chk` CHECK to admit `registry`. |
| **From** | `scope_code IN ('bf_bo','cf','mapping','all')` |
| **To** | `scope_code IN ('bf_bo','cf','mapping','all','registry')` |
| **Why** | L2 / L4. The A14 phase tracker tracks the Phase 0/1/2 ladder for `registry` authoring per stage. |
| **Other impact** | None. The PK `(scope_code, stage_code)` is unchanged; the value simply admits up to three new rows (`registry` × {`authoring`, `publication`, `lifecycle_audit`}). Those rows are created by the A14 tracker service when panels begin writing — not by this DBCP. |

### 2.4 `contract.certification_record` — the Registry operation shape (Model A)

The substantive change. `certification_record` must carry two row shapes:

- the **legacy shape** — `primitive_type` + `primitive_id`, a poly-ref to an
  already-existing BF/BO/CF row (every row that exists today; kept per L4);
- the **Registry shape** — Model A: the row identifies the *authorized Registry
  authoring operation*, and the final Registry target id does not exist when
  C5 issues the row.

**2.4.1 New columns** (all nullable, added with no default):

| Column | Type | Purpose |
|---|---|---|
| `governance_scope` | `text` | Row-shape discriminator. `NULL` on legacy rows; `'registry'` on Registry-shape rows. |
| `subject_kind` | `text` | The Registry subject kind the operation authorizes. |
| `target_registry_id` | `uuid` | The final Registry id. `NULL` at cert issuance; stamped by F3 on completion (poly-ref across the six subject tables — no DB FK, same convention as `primitive_id`). |

**2.4.2 Nullability change.** `primitive_type` and `primitive_id` drop
`NOT NULL` (become nullable). Legacy rows keep their values (L4); Registry-shape
rows leave both `NULL`. This is a loosening — no existing row is affected.

**2.4.3 CHECK constraints.**

- `certification_record_primitive_type_chk` — made `NULL`-tolerant:
  `primitive_type IS NULL OR primitive_type IN ('canonical_field','business_field','business_object')`.
  (Legacy values kept per L4.)
- **New** `certification_record_governance_scope_chk`:
  `governance_scope IS NULL OR governance_scope = 'registry'` (one Registry
  scope, L2).
- **New** `certification_record_subject_kind_chk`:
  `subject_kind IS NULL OR subject_kind IN ('entity','business_concept','characteristic','alias','supersession_proposal')`.
  (`representation_term` is **not** a v1 subject kind — see §2.4.6.)
- **New** `certification_record_row_shape_chk` — exactly one shape per row:

  ```
  (   governance_scope   IS NULL
  AND primitive_type     IS NOT NULL
  AND primitive_id       IS NOT NULL
  AND subject_kind       IS NULL
  AND target_registry_id IS NULL )
  OR
  (   governance_scope   IS NOT DISTINCT FROM 'registry'
  AND subject_kind       IS NOT NULL
  AND primitive_type     IS NULL
  AND primitive_id       IS NULL
  AND panel_run_uid      IS NOT NULL )
  ```

  The Registry branch requires `panel_run_uid` — it is the authorization spine
  (O1). `target_registry_id` is intentionally unconstrained by shape: `NULL`
  pre-stamp, non-`NULL` post-stamp — its lifecycle is trigger-enforced (§2.4.5).
  The Registry branch uses the NULL-safe `IS NOT DISTINCT FROM` — a plain
  `= 'registry'` would let a malformed row escape (see the §9 erratum).
- **New** `certification_record_scope_action_chk` — couples the row shape to
  the action-code family, so neither shape can borrow the other's codes:

  ```
  (   governance_scope IS NOT DISTINCT FROM 'registry'
  AND action_code IN     ( the seven registry codes — §2.4.4 ) )
  OR
  (   governance_scope IS NULL
  AND action_code NOT IN ( the seven registry codes — §2.4.4 ) )
  ```

  A Registry-shape row carrying a legacy `action_code`, or a legacy-shape row
  carrying a `registry_*` `action_code`, fails this constraint.
- `certification_record_action_code_chk` — extended with the seven Registry
  operation codes (§2.4.4) alongside the retained legacy codes (L4).
- `certification_record_nf1_all_or_none_chk` — **unchanged**. A Registry-shape
  row has `panel_run_uid IS NOT NULL` (row-shape CHECK), so the existing
  all-or-none invariant forces the other six NF1 fields non-`NULL` too —
  Registry rows are always fully NF1-populated. Consistent, no change.

**2.4.4 `action_code` — the authorized operation (locked, rev 2).** O1
specifies an "action/operation code for the authorized write." This packet
**extends the existing `action_code` enum** rather than adding a separate
column — F3's `CertificationVerifier` already matches on `action_code`, so no
verifier restructure is needed. The Registry operation-code set is **final**
(seven coarse codes; `subject_kind` carries the subject):

| `action_code` | Covers |
|---|---|
| `registry_create` | create an entity / business_concept anchor |
| `registry_add_version` | add an entity / business_concept version |
| `registry_transition` | an entity / business_concept lifecycle transition |
| `registry_supersede` | supersede an entity / business_concept |
| `registry_author_vocabulary` | author a characteristic / alias |
| `registry_action_supersession_proposal` | action a supersession proposal |
| `registry_dismiss_supersession_proposal` | dismiss a supersession proposal |

`certification_record_action_code_chk` gains exactly these seven values
alongside the retained legacy codes (L4). Which `subject_kind` each code admits,
and the id F3 stamps, is §2.4.6; the matrix's *validity* half (the legal
operation × `subject_kind` pairs) is service-enforced by F3, not a DB CHECK.

**2.4.5 The born-null + one-time completion-stamp invariant (O1, mandatory).**
`target_registry_id` carries a two-part lifecycle invariant a CHECK cannot
express — a CHECK cannot tell `INSERT` from `UPDATE`, nor police a transition.
It is enforced by one trigger, `certification_record_target_registry_id_guard`
(`BEFORE INSERT OR UPDATE`), plus F3 service discipline. `certification_record`
is append-only by convention (no UPDATE path exists today); the trigger makes
the single bounded exception explicit.

- **Born-null on `INSERT`.** A Registry-shape row (`governance_scope =
  'registry'`) **must be inserted with `target_registry_id IS NULL`.** C5 issues
  every Registry cert row born-null; F3 is the only path that completes it. The
  trigger rejects an `INSERT` of a Registry-shape row whose `target_registry_id`
  is non-`NULL`. (Legacy-shape rows always have `target_registry_id NULL` —
  forced by `certification_record_row_shape_chk` — so the `INSERT` guard is a
  no-op for them.)
- **Write-once on `UPDATE`.** The only `UPDATE` the trigger permits is
  `target_registry_id` `NULL` → non-`NULL` with **every other column
  unchanged**. It rejects any change to `target_registry_id` once it is
  non-`NULL`, and any change to any other column. The ledger stays append-only
  except this one write-once stamp.
- **F3 service discipline.** F3 stamps `target_registry_id` only on the
  `certification_record` row it verified for that operation, in the **same
  transaction** as the authorized Registry write, exactly once.

Together: born-null at issuance and write-once at completion are storage-enforced
(trigger); correct-target and atomicity are service-enforced (F3). With
representation-term authoring out of Bucket 1 v1 (§2.4.6), the invariant is
uniform and admits no exemption — **every** Registry-shape certification row has
`target_registry_id` `NULL` at issuance and non-`NULL` after F3 completion,
exactly once.

**2.4.6 Operation × `subject_kind` → `target_registry_id` semantics (locked).**
For every Registry operation, the id F3 stamps into `target_registry_id` on
completion:

| Operation | `action_code` | `subject_kind` | `target_registry_id` F3 stamps |
|---|---|---|---|
| create entity | `registry_create` | `entity` | the new `entity.entity_id` (the anchor) |
| add entity version | `registry_add_version` | `entity` | the new `entity_version.entity_version_id` |
| entity lifecycle transition | `registry_transition` | `entity` | the transitioned `entity.entity_id` |
| supersede entity | `registry_supersede` | `entity` | the new `entity_supersession.supersession_id` |
| create business_concept | `registry_create` | `business_concept` | the new `business_concept.concept_id` (the anchor) |
| add business_concept version | `registry_add_version` | `business_concept` | the new `business_concept_version.concept_version_id` |
| business_concept lifecycle transition | `registry_transition` | `business_concept` | the transitioned `business_concept.concept_id` |
| supersede business_concept | `registry_supersede` | `business_concept` | the new `business_concept_supersession.supersession_id` |
| author characteristic | `registry_author_vocabulary` | `characteristic` | the new `characteristic.characteristic_id` |
| author alias | `registry_author_vocabulary` | `alias` | the new `alias.alias_id` |
| action supersession proposal | `registry_action_supersession_proposal` | `supersession_proposal` | the actioned `supersession_proposal.proposal_id` |
| dismiss supersession proposal | `registry_dismiss_supersession_proposal` | `supersession_proposal` | the dismissed `supersession_proposal.proposal_id` |

`target_registry_id` holds the id of the artifact the operation **produces**
(create → the new anchor; add-version → the new immutable version; supersede →
the new supersession-lineage row) or the id of the artifact it **acts on**
(lifecycle transition → the anchor; proposal action / dismiss → the proposal).
Across both it is a poly-ref — no DB foreign key, the same convention as the
legacy `primitive_id`. The internal artifacts of a compound operation (e.g. the
`resolution_supersession_id` an actioned proposal produces) are recorded on
their own Registry rows; they are not the cert's `target_registry_id`.

**Representation-term authoring is out of Bucket 1 v1.**
`concept_registry.representation_term` currently has a natural **text** primary
key (`term`) and no uuid identity, so it has no `target_registry_id`-shaped
target. Special-casing it with a permanently-`NULL` `target_registry_id` would
break the Model A completion-stamp meaning — every Registry-shape row completes
`NULL` → non-`NULL` exactly once. Rather than carry that contradiction,
representation-term additions are **excluded from this DBCP**: `representation_term`
is not a `subject_kind` value, and `registry_author_vocabulary` covers
`characteristic` and `alias` only. Representation-term additions remain the
F2-seeded closed-set governance act they are today. A future representation-term
governance path requires its own **mini-DBCP** — either adding a uuid identity
to `representation_term`, or defining a separate target-key shape for it — and
is out of scope here.

**2.4.7 Index — Registry audit lookup.** A partial index supports the forward
audit query Model A exists to enable — "which certification row authorized
Registry id X":

- `idx_certification_record_target_registry` — on `target_registry_id`,
  `WHERE target_registry_id IS NOT NULL`.

Partial because only stamped Registry-shape rows carry a value — legacy rows and
not-yet-stamped Registry rows are excluded, keeping the index small. It mirrors
the existing `idx_certification_record_panel_run` partial-index pattern.

## 3. Write choreography (context — not part of the DDL)

1. B6 panel runs → emits a `panel_output_record` (A5).
2. On `APPROVE`, **C5 (Framework Approval)** issues a Registry-shape
   `certification_record`: `governance_scope='registry'`, `subject_kind`,
   `action_code` = the Registry operation, `panel_run_uid`, the seven NF1
   fields; `target_registry_id` `NULL` (born-null — trigger-enforced, §2.4.5).
3. **F3 (`RegistryAuthoringService`)** verifies that cert row, performs the
   authorized `concept_registry` write, and — in the same transaction —
   stamps `target_registry_id` on that cert row (`NULL` → the new id).
4. The `concept_registry` version row also records `certification_record_id` +
   `panel_run_uid` (existing F3 columns) — the reverse link is unchanged.

## 4. Migration safety

- **Purely additive / loosening.** New nullable columns; CHECK extensions; two
  `DROP NOT NULL`. Nothing is tightened against existing data.
- **No data migration, no row rewrite, no backfill.** Every existing row has
  `governance_scope NULL` (new column), `primitive_type` / `primitive_id`
  non-`NULL`, and `subject_kind` / `target_registry_id` `NULL` (new columns) —
  so every existing row satisfies the **legacy branch** of
  `certification_record_row_shape_chk`. The new CHECK validates clean at
  `ADD` time; no `NOT VALID` needed.
- **The trigger** fires on future `INSERT`s and `UPDATE`s only — no existing-row
  impact. The `UPDATE` guard has no current path to break (`certification_record`
  is append-only today); the `INSERT` guard constrains only new Registry-shape
  rows, of which none exist yet.
- **The partial index** builds over a table that holds no Registry-shape rows
  yet — effectively an empty index at apply time.
- **Reversible.** Each change is a single constraint / column / trigger / index;
  rollback drops the additions and restores the two `NOT NULL`s (safe while no
  Registry-shape row exists yet).

## 5. Accompanying code work (named for sequencing — not in this DBCP)

On packet approval, the build step is, in order:

1. The migration SQL (`bc-core/docker/redesign/migrations/`) + the four Drizzle
   schema mirrors (`framework-policy.ts`, `operator-confirm-rule.ts`,
   `phase-state.ts`, `certification-record.ts`) updated in lockstep — the
   mirrors must not drift from the DDL.
2. F3 `CertificationVerifier` — recognise the Registry `action_code` set and
   the Registry cert shape (`governance_scope='registry'`, `subject_kind`).
3. F3 `RegistryAuthoringService` — the `target_registry_id` stamp, in the
   authorized write's transaction.
4. C5 Framework Approval — issue Registry-shape cert rows on B6 `APPROVE`.

Steps 2–4 are separate PRs and are not gated by this packet beyond the schema
it defines.

## 6. Foundation note

The design preserves Invariant III (immutable state) and V (evidence emitted,
not inferred): `certification_record` remains append-only; the **sole**
exception is the bounded, trigger-guarded, write-once `target_registry_id`
stamp — a deliberate, storage-enforced exception, not general mutability. The
Foundation invariant gate is run at apply time, when the migration is a
concrete change.

## 7. Decisions resolved (rev 2)

Rev 1's three open items are closed:

| # | Resolution |
|---|---|
| **P1** | The Registry `action_code` set is **locked** — the seven coarse codes in §2.4.4. No "finalized at DDL time" deferral remains. |
| **P2** | `action_code` is **extended** (not a new column) — committed; the §2.4.3 coupling CHECK and the §2.4.4 set are written against `action_code`. |
| **P3** | The born-null + write-once trigger ships **in this DBCP** (§2.4.5) — mandatory under O1. |

No open items remain in this packet. The only DBCP-external dependency is that
F3's cert-gated method surface matches the §2.4.6 matrix — confirmed in the §5
build step, not a packet open question.

## 8. Status

`approved` — rev 2, operator-approved 2026-05-21. Rev 2 over rev 1:

1. **Born-null on `INSERT`** — Registry-shape rows must be inserted with
   `target_registry_id IS NULL`; trigger-enforced (§2.4.5).
2. **Row-shape ↔ action-code coupling** — `certification_record_scope_action_chk`:
   a Registry shape may carry only `registry_*` codes, a legacy shape only
   legacy codes (§2.4.3).
3. **`action_code` set locked** — the seven coarse Registry codes; P1 closed
   (§2.4.4).
4. **Operation × `subject_kind` → `target_registry_id` matrix** — the twelve
   in-scope operations (§2.4.6).
5. **Partial index** `idx_certification_record_target_registry` for the
   Registry forward-audit lookup (§2.4.7).
6. **Representation-term scope correction** — `representation_term` is removed
   from `subject_kind` and from the matrix; representation-term additions are
   out of Bucket 1 v1 (text PK, no uuid target). The completion-stamp invariant
   is now uniform — every Registry-shape row completes `NULL` → non-`NULL`
   exactly once, no exemption.

No DDL, no Drizzle change, no service code is part of this packet. The build
step is §5; the future representation-term governance path is a separate
mini-DBCP (§2.4.6); Bucket 2 follows the B6 design (design-note O2); Bucket 3
is Phase G.

## 9. Erratum — rev 2, scope-coupling CHECK NULL semantics (2026-05-21)

**Defect.** The §2.4.3 `certification_record_row_shape_chk` and
`certification_record_scope_action_chk` were authored with
`governance_scope = 'registry'` in the Registry branch. SQL three-valued
logic makes that unsound: for a legacy row (`governance_scope IS NULL`) the
comparison `NULL = 'registry'` yields **NULL**, not FALSE; the Registry branch
is then NULL, and `<legacy branch FALSE> OR NULL` = **NULL** — and a `CHECK`
constraint **passes on NULL** (it fails only on FALSE). So a legacy-shape row
carrying a `registry_*` action code, and a malformed legacy row with a stray
`subject_kind` / `target_registry_id`, both escaped the CHECKs.

**How it was found.** The alignment migration's own post-condition negative
test T6 (a legacy-shape row with a `registry_*` action code) returned
`INSERT 0 1` — accepted — where a rejection was required.

**Correction.** Both Registry branches now use the NULL-safe
`governance_scope IS NOT DISTINCT FROM 'registry'`, which yields FALSE (not
NULL) for a legacy row. The §2.4.3 predicates above are shown corrected. The
fix is the corrective migration
`20260521-phase-a-bucket-1-fix-scope-coupling-null-semantics.sql` (drop +
re-ADD both CHECKs); the Drizzle mirror `certification-record.ts` is updated to
match. The trigger (§2.4.5) was unaffected — plpgsql `IF` treats NULL as
false, which is the intended behaviour there.

**Lesson.** A `CHECK` whose expression can evaluate to NULL is not enforcing
what it appears to. Any disjunction-of-shapes `CHECK` must use NULL-safe
discriminators (`IS NULL`, `IS NOT DISTINCT FROM`) in every branch.
