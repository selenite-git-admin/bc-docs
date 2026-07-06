---
uid: business-concept-registry-b10b-characteristic-supersession-dbcp-design
title: Business Concept Registry — B10b-S1 immutable-characteristic / supersession DBCP design
description: B10b-S1 design for the additive DB / provenance model that unblocks characteristic publication under ADR DEC-26b6e2 (Immutable Characteristic Atoms). Resolves D1–D10. Specifies the characteristic_supersession table, the characteristic.term partial-uniqueness rule, the F3 transitionCharacteristicLifecycle + supersedeCharacteristic methods, and the BusinessConcept impact. Additive — no characteristic_version, no definition relocation, no data migration of existing rows. Design only — no code, no migration authored, no DB writes. status accepted.
status: accepted
date: 2026-05-23
project: bc-docs
domain: contracts
subdomain: catalog
focus: lifecycle
---

# Business Concept Registry — B10b-S1 immutable-characteristic / supersession DBCP design

> **What this is.** The **B10b-S1** design slice — the additive database /
> provenance model that unblocks **Characteristic publication** under
> **ADR DEC-26b6e2 / D415 *Immutable Characteristic Atoms*** (which reversed the
> originally-accepted B10 D5 recommendation to add `characteristic_version`).
> It is a **design note, not an ADR**, and **design only** — no code, no
> migration authored, no DB writes, no publication, no bc-ai. It elaborates
> DEC-26b6e2 and B10 design §D5 (amended). `status: proposed` — awaiting
> operator review-back.

## Scope

B10b-S1 designs the **smallest additive shape** that makes a published
Characteristic correctable in an Invariant-III-safe way **without** versioning.
It states what to build; the migration packet (B10b-S2), the publication path
(B10b-S3) and the live `lead time` publication (B10b-S4) are later, separately
gated slices.

## 1. Findings from the live code and live data

- **`concept_registry.characteristic` is flat** —
  `(characteristic_id, term, definition, lifecycle_state, created_at,
  created_by, archived_at)`. `term` is `NOT NULL UNIQUE` today.
- **The lifecycle CHECK already includes `superseded`** —
  `lifecycle_state IN ('draft','review','approved','active','superseded')` on
  `entity`, `business_concept`, **and `characteristic`**. **No CHECK migration
  is needed for the `superseded` state.**
- **No `characteristic_supersession` table exists.** `entity_supersession` and
  `business_concept_supersession` exist; characteristic does not. The
  cross-subject `*_supersession` proposal-workflow table
  (`supersession_proposal`) is entity-scoped and is not on B10b's path.
- **F3 has no characteristic transition or supersede method.**
  `registerCharacteristic` creates a `characteristic` row at `draft`; there is
  no `transitionCharacteristicLifecycle` and no `supersedeCharacteristic`.
- **F5 active-only default already excludes `superseded`.** `lifecycleScopeConditions`
  applied to `characteristic.lifecycle_state` returns only `active` rows when
  the default scope is used; no F5 default change is needed for supersession
  hiding.
- **Live data.** 25 characteristics: 24 `active` seed terms + 1 `draft`
  (`lead time`). 0 `superseded`. All 25 carry unique `term`s today.
- **Entity_supersession is the base pattern.** Columns: `supersession_id`,
  `predecessor_entity_id`, `successor_entity_id`, `reason`, `superseded_at`,
  `superseded_by`; `CHECK predecessor <> successor`; two indexes; no
  `archived_at`, no `certification_record_id` (entity_version carries the
  provenance soft-refs).

## 2. Decisions D1–D10 — recommendations

### D1 — Supersession table shape

**Recommendation.** Add `concept_registry.characteristic_supersession`,
mirroring `entity_supersession` and adding the operator-decision-relevant
provenance the entity supersession does not carry.

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `supersession_id` | `uuid` PK | `DEFAULT gen_random_uuid()` | Mirrors `entity_supersession.supersession_id`. |
| `predecessor_characteristic_id` | `uuid` | `NOT NULL`, FK → `characteristic.characteristic_id` | The characteristic being retired. |
| `successor_characteristic_id` | `uuid` | `NOT NULL`, FK → `characteristic.characteristic_id` | The replacement characteristic. |
| `correction_class` | `text` | `NOT NULL`, `CHECK IN ('editorial','meaning_bearing')` | The classification ADR DEC-26b6e2 requires on every supersession. Audit metadata on a single authority — **not** a non-authoritative definition layer. |
| `rationale` | `text` | `NOT NULL` | Operator's prose rationale. The cert's `gate_results_json.operator_confirm.rationale_text` is the authoritative one; this column is the supersession-row mirror for fast read. |
| `certification_record_id` | `uuid` | **soft ref**, nullable in DDL, **operationally required** by F3 | Cross-schema soft ref (no FK), consistent with `entity_version.certification_record_id`. The supersession-authorizing cert. |
| `panel_run_uid` | `uuid` | soft ref, nullable | The authoring panel run for the successor, where available. Optional — supersession may not require a fresh panel run if the successor was already F4-v2-authored. |
| `superseded_at` | `timestamptz` | `NOT NULL DEFAULT now()` | Event timestamp. |
| `superseded_by` | `text` | `NOT NULL` | The operator (Cognito sub) who confirmed. |

**Naming** mirrors `entity_supersession` (`supersession_id`, `superseded_at`,
`superseded_by`) rather than the generic `created_at` / `created_by` so the
two supersession tables read identically.

**No `archived_at` on the supersession row.** A supersession event is an
immutable historical fact (Invariant III); it is not archived. Aligns with
`entity_supersession`.

**Indexes / composite-level constraints.** The predecessor and successor
`UNIQUE` constraints (§D2 — both required for v1's one-predecessor-to-one-successor
rule) provide their own indexes; no explicit object indexes are needed. The
provenance reverse-lookup index is:

- `idx_characteristic_supersession_certification (certification_record_id) WHERE certification_record_id IS NOT NULL`
  (parity with `entity_version`'s cert index).

### D2 — Supersession constraints

| Rule | Where enforced | Reason |
|---|---|---|
| `predecessor ≠ successor` | DB `CHECK` | A characteristic cannot supersede itself. Mirrors `entity_supersession_distinct_chk`. |
| Predecessor and successor exist | DB FK | Standard referential integrity. |
| `correction_class ∈ {'editorial','meaning_bearing'}` | DB `CHECK` | The two classes ADR DEC-26b6e2 names. |
| **Predecessor must be `active` at supersession time** (not archived) | F3 service | A draft is mutable (edit it directly); a `superseded` row is already history (see next row); only an `active` characteristic has a frozen, authoritative meaning that needs replacement. |
| **Successor must be `active` at supersession time** (not archived) | F3 service | The supersession event publishes the lineage "this predecessor is replaced by this *authoritative* successor". A draft successor would mean "replaced by something not yet authoritative" — confusing for binders. The flow is: author successor draft → publish successor (`draft → active`) → supersede predecessor with the active successor. |
| **At most one supersession per predecessor** — `UNIQUE(predecessor_characteristic_id)` | DB `UNIQUE` | Supersession is terminal for the predecessor: once superseded, it cannot be superseded again. A second supersede attempt on the same predecessor fails closed at the DB. |
| **At most one supersession per successor — v1 only** — `UNIQUE(successor_characteristic_id)` | DB `UNIQUE` | **v1 supersession is one predecessor → one successor — a correction lineage, not a semantic merge.** Many-to-one merges (two predecessors → one successor) are a distinct curation operation with their own semantic-equivalence governance and are **deferred to a future design gate**. A second supersession pointing at the same successor in v1 fails closed at the DB. |
| **No cycles in the supersession graph** | **F3 service** (DB cannot prove it) | DB constraints prevent **self-supersession** (`predecessor ≠ successor`) and **duplicate predecessor supersession** (`UNIQUE(predecessor_characteristic_id)`). These do **not** prove global acyclicity — a chain A → B, B → C, C → A passes every per-row DB constraint. **F3 enforces acyclicity by traversing the predecessor / successor lineage before writing**: before `supersedeCharacteristic` inserts a row, F3 walks the existing supersession graph and **rejects any write whose `successor` already reaches `predecessor` through any path** (i.e. any write that would close a cycle). v1 F3 rejects all such attempts. |

### D3 — Characteristic term uniqueness

**Problem.** `characteristic.term` is `NOT NULL UNIQUE` today (full unique). A
successor characteristic carrying the same `term` as a superseded predecessor
would violate the constraint — but the whole point of Option B is that a
successor *can* carry the same term (corrected `unit price` replaces the
predecessor `unit price`).

**Recommendation.** Drop the full `UNIQUE(term)` and add a **partial unique
index** scoped to live rows:

```sql
ALTER TABLE concept_registry.characteristic
  DROP CONSTRAINT characteristic_term_unique;

CREATE UNIQUE INDEX uq_characteristic_term_live
  ON concept_registry.characteristic (term)
  WHERE lifecycle_state <> 'superseded'
    AND archived_at IS NULL;
```

**Meaning.** At most one *live* characteristic per `term`, where *live* =
not `superseded` and not archived. A `superseded` or archived characteristic
**frees its `term`** for re-use by a successor or a fresh draft.

**Live-data fit.** All 25 current characteristics are non-superseded and
non-archived; the partial unique covers exactly the same set the current full
unique covers. The forward migration is **safe with no data conflict**.

**`lead time` fit.** `lead time` is `draft`, non-archived → included in the
partial unique → still unique among live characteristics → publication is
unaffected.

### D4 — Lifecycle states

**No CHECK migration.** `characteristic_lifecycle_chk` already permits
`('draft','review','approved','active','superseded')`. `superseded` is already
valid — the F4-v2 / F2 schema landed it.

**Allowed Characteristic transitions in B10b:**

| From | To | Path | Notes |
|---|---|---|---|
| `draft` | `active` | F3 `transitionCharacteristicLifecycle` | Publication (B10b-S3). High-risk; operator-confirmed; semantic-finality affirmation required. |
| `active` | `superseded` | F3 `supersedeCharacteristic` | Always paired with a `characteristic_supersession` row written in the same transaction. |
| any state | `archived_at IS NOT NULL` | (out of B10b-S1 scope — orthogonal to `lifecycle_state`) | Archiving a `draft` is "abandon"; archiving an `active` is **not** a B10b path — correction of an active is supersession, not archive. B10b-S3 may decline to expose archive-of-active. |
| `review` / `approved` | — | (not used in v1) | Reserved by the five-state CHECK; B10 v1 does not use them. |
| `superseded` | (any) | (terminal) | A superseded characteristic does not transition out; it is history. |

**Interaction.** `supersedeCharacteristic` writes the supersession row **and**
flips `predecessor.lifecycle_state` from `'active'` to `'superseded'` in **one
transaction**. The supersession event is the governing act; the lifecycle flip
is the side effect.

### D5 — F3 support

Two new F3 methods, both governed by C5 (high-risk, operator-confirm
mandatory), no in-place edits:

**(a) `transitionCharacteristicLifecycle(characteristicId, toState, auth)`** —
mirrors `transitionEntityLifecycle` / `transitionBusinessConceptLifecycle`.
B10b v1 supports only `draft → active`. Verifies a publication cert
(`action_code = 'registry_transition'`, `subject_kind = 'characteristic'`,
`governance_scope = 'registry'`, `target_registry_id = characteristicId`,
`from_state_code = 'draft'`, `to_state_code = 'active'`) via the existing
`CertificationVerifier`; updates the anchor's `lifecycle_state` to `active`;
stamps `target_registry_id` on the cert. Returns
`{ characteristicId, lifecycleState }`.

**(b) `supersedeCharacteristic({ predecessorId, successorId, correctionClass, rationale }, auth)`** —
a new authoring method. Verifies the supersession cert
(`action_code = 'registry_supersede'`, `subject_kind = 'characteristic'`,
`governance_scope = 'registry'`, `target_registry_id = predecessorId`); within
one transaction:

1. checks the predecessor is `active` and not archived; successor is `active`
   and not archived; `predecessor ≠ successor`; **and traverses the existing
   supersession lineage to confirm the new write would not close a cycle**
   (§D2 — DB constraints alone do not prove global acyclicity, so this
   service-side check is mandatory and rejects the write on any reachable
   `successor → … → predecessor` path);
2. inserts the `characteristic_supersession` row (with `certification_record_id`,
   `correction_class`, `rationale`, `superseded_by = auth.actorSub`);
3. updates `predecessor.lifecycle_state` from `'active'` to `'superseded'`;
4. stamps `target_registry_id = predecessorId` on the cert.

Two atomic DB guards back the F3 service-side checks:
`UNIQUE(predecessor_characteristic_id)` prevents a double-supersede race on
the same predecessor (two concurrent `supersedeCharacteristic` calls — one
wins, one fails closed); `UNIQUE(successor_characteristic_id)` enforces v1's
one-predecessor-to-one-successor rule (a second `supersedeCharacteristic`
aimed at the same successor fails closed at the DB even if F3 checks raced).
The cycle check is service-side only — the DB cannot enforce it.

**Action-code wiring.** `'registry_supersede'` exists in the action-code CHECK
already. Add the pair `(registry_supersede, characteristic)` to the TS
`REGISTRY_ACTION_SUBJECT_COMPAT` matrix (DB CHECKs permit both values
independently). **TS-only — no DDL.**

**Certification requirements.** Both methods are high-risk under
`classifyRegistryRiskTier` (`registry_transition` is locked high-risk;
`registry_supersede` should be high-risk for the same reason — it changes the
authoritative vocabulary). Both go through the C5 operator-confirm fork. The
operator confirm captures the `correction_class` (supersede) or the
**semantic-finality affirmation** (publication) — see §D5 below for where the
affirmation lives.

**Provenance stamping.** Standard registry-shape stamping —
`target_registry_id` is the predecessor on a supersession cert (the object
whose state changed); the supersession row's `certification_record_id` is the
soft back-link.

**Idempotency / retry.** Same Fork-ii idempotent-resume pattern as B10a
publication (a cert issued but the F3 write did not land → resume on next
call). Mechanics specified in B10b-S3.

**No `addCharacteristicVersion`. No in-place definition edits on active
rows.** The only post-publication correction path is
`supersedeCharacteristic` + author a new characteristic. F3 is the sole-write
path; no method exists (and none will be added in B10b) to UPDATE
`characteristic.definition` on an `active` row. (A DB trigger blocking such
UPDATEs is a possible belt-and-suspenders hardening but is **not** in B10b-S1
scope — service-layer F3 discipline matches how entity / concept versions are
governed.)

### D6 — F5 support

- **Active-only default** already excludes `superseded` — no F5 default change.
  The publication of a successor and the supersession of the predecessor
  together produce a clean active-only read: the successor appears, the
  predecessor disappears.
- **Admin / draft reads** continue via the existing
  `lifecycleState: 'superseded' | 'draft' | …` / `includeAllStates: true`
  filters. No new F5 method is required for the *state filter*.
- **Supersession lineage reads** — new F5 read methods (parallel to
  `listEntitySupersessions` / `listConceptSupersessions`):
  - `listCharacteristicSupersessions(filter)` — by predecessor / successor;
  - `resolveCharacteristicSupersession(supersessionId)`.

  Add to `SupersessionReadRepository` + `RegistryReadService`. HTTP exposure
  via the F5-S2 read controller and / or the provenance-inspection read —
  **deferred to B10b-S3** (not B10b-S1 DBCP scope).
- **BusinessConcept resolve view (informational hint).** `ResolvedConcept` may
  gain an optional `characteristicSupersession: { successorCharacteristicId, correctionClass } | null` —
  populated when the bound characteristic has been superseded; `null`
  otherwise. The concept's `characteristicTerm` / `displayLabel` continue to
  reflect the **predecessor** (the meaning the concept was authored against);
  the supersession field is a UI hint, never a silent rebind. **Deferred to
  B10b-S3.**

### D7 — BusinessConcept impact

- **No `business_concept` schema change.** `business_concept.characteristic_id`
  continues pointing at the predecessor characteristic — the meaning the
  concept was authored and certified against. This is historically correct.
- **Adopting the successor = a new `business_concept_version`** through normal
  concept authoring (panel + cert + operator confirm), re-binding
  `characteristicId = successor_characteristic_id`. A characteristic-meaning
  change always re-enters concept-level governance. No silent rebind exists
  anywhere in the system.
- **Read surfaces** make the lineage visible (D6 above) without rebinding.
- **Live impact** — the `Unit Price` concept (active) binds the active
  `unit price` characteristic; this binding is **unchanged** by the B10b-S1
  DBCP. The `unit price` characteristic is `active`, never superseded — the
  lineage column would be `null`.

### D8 — Publication of `lead time`

`lead time` is currently `draft` with **no predecessor**. Its publication
under B10b-S3 / B10b-S4 is the **first-publication** case, not a supersession:

- F3 `transitionCharacteristicLifecycle(lead_time_id, 'active', auth)`.
- Publication cert: `governance_scope = 'registry'`, `subject_kind =
  'characteristic'`, `action_code = 'registry_transition'`,
  `from_state_code = 'draft'`, `to_state_code = 'active'`,
  `target_registry_id = lead_time_id`, `panel_run_uid` = the original F4-v2
  authoring panel run resolved server-side from the `registry_author_vocabulary`
  authoring cert (the existing B10a evidence-resolution pattern, extended for
  `characteristic`).
- Operator-confirm captures the **semantic-finality affirmation** (ADR
  DEC-26b6e2): an explicit operator statement that `(term, definition)` is
  final. The affirmation lives in the operator-confirm block — either as the
  `rationale_text` itself (the operator's published rationale phrased as
  "this meaning is final because …") or as a structured boolean
  `semantic_finality_affirmed: true` on the publication request DTO with the
  rationale separately. **DTO / cert shape is B10b-S3 scope**, but the
  affirmation requirement is locked here.
- **No `characteristic_supersession` row** is written — there is no predecessor.

After publication: `lead time` is `active`, immutable. Any subsequent
correction (editorial or meaning-bearing) follows the supersession path.

### D9 — Revert strategy

The forward migration is **purely additive** (a new table, an index swap on
the existing table) and **safe with the current data** (no existing rows
violate the partial unique).

| Object | Forward | Revert |
|---|---|---|
| `characteristic_supersession` table | `CREATE TABLE …` | `DROP TABLE …` (no cross-schema FKs; `certification_record_id` is a soft uuid ref). |
| `characteristic.term` uniqueness | `DROP CONSTRAINT characteristic_term_unique; CREATE UNIQUE INDEX uq_characteristic_term_live … WHERE non-superseded, non-archived` | `DROP INDEX uq_characteristic_term_live; ALTER TABLE … ADD CONSTRAINT characteristic_term_unique UNIQUE (term)` |

**Revert is safe only while `concept_registry.characteristic_supersession` is
empty.** Once any supersession row exists, automatic revert is **not safe** —
a superseded predecessor and a live successor may share the same `term`, and
the full `UNIQUE(term)` constraint cannot be restored without first unwinding
that collision. Unwinding a supersession is itself a meaning-bearing curation
act, not an automatic operation.

**Revert script rule.** The revert script
`SELECT count(*) FROM concept_registry.characteristic_supersession` and
**aborts unconditionally if non-zero**. **There is no force flag.** A
destructive revert from a non-empty state would require a **separate
operator-authored data-remediation DBCP** that explicitly unwinds the
supersession rows (and any term collisions or concept versions they produced)
under governed review. That data-remediation DBCP is **not** part of the
normal B10b-S2 revert file — it is a distinct operator gate, authored only if
and when needed.

### D10 — Tests / verification (for B10b-S2, the migration slice)

Pre-check (against the live DB before applying):

- `SELECT count(*) = count(DISTINCT term) FROM concept_registry.characteristic`
  (expect true — currently 25 unique terms).
- `\d concept_registry.characteristic_supersession` returns "Did not find" (the
  table does not yet exist).

Post-check (after applying):

- `\d concept_registry.characteristic_supersession` shows the columns,
  `CHECK`s, FKs, and indexes per §D1 / §D2.
- `uq_characteristic_term_live` exists; the original
  `characteristic_term_unique` constraint is gone.
- All 25 existing characteristics still resolve unchanged through F5
  (`RegistryReadService.listCharacteristics()` returns 24 active; `lead time`
  appears under `lifecycleState: 'draft'`).
- **Live-term collision is blocked** — attempting to `INSERT INTO
  concept_registry.characteristic (term, definition, lifecycle_state, created_by)
  VALUES ('unit price', 'x', 'draft', 'tester')` fails on the partial unique
  (`unit price` is the active term of the live seed row).
- **Term re-use after supersede is allowed** — within a rollback'd test
  transaction: `UPDATE characteristic SET lifecycle_state = 'superseded' WHERE
  term = 'unit price' AND lifecycle_state = 'active'`; then the same INSERT
  succeeds. `ROLLBACK`.
- `business_concept.characteristic_id` for the live `Unit Price` concept
  still equals the live `unit price` characteristic id — **unchanged**.
- `lead time` remains `draft` — **no publication runs in this slice**.
- `characteristic_supersession` is **empty** — supersession is a separate F3
  act in B10b-S3.
- **No new tsc errors**; baseline preserved.

**Constraint / governance tests (B10b-S2 / B10b-S3).**

- **Cycle attempt rejected by F3.** With a chain `A → B` already written, an
  attempt `B → A` is rejected by `supersedeCharacteristic` (cycle check, §D2 /
  §D5); any longer attempt `B → A` that would close a cycle (e.g.
  `A → B`, `B → C`, then `C → A`) is rejected the same way. F3 returns a
  refusal; **no row is written**.
- **Second predecessor → same successor rejected (v1 — no merges).** With
  `A → B` already written, an attempt `C → B` **fails closed at the DB** on
  `UNIQUE(successor_characteristic_id)`; F3 also rejects it pre-write with a
  "v1: one predecessor → one successor" refusal. Confirms merges are deferred.
- **Second successor for the same predecessor rejected.** With `A → B` already
  written, an attempt `A → C` **fails closed at the DB** on
  `UNIQUE(predecessor_characteristic_id)`; F3 also rejects it pre-write (the
  predecessor is already `superseded` and is no longer a valid input).
- **Revert aborts unconditionally on a non-empty supersession.** A revert
  dry-run against a state with one or more `characteristic_supersession` rows
  aborts with `revert requires concept_registry.characteristic_supersession to
  be empty; supersession-data remediation is a separate operator-authored DBCP`
  — **no force flag exists** (§D9).

## 3. Source-of-authority check

This DBCP is the direct implementation of **ADR DEC-26b6e2 / D415** (Immutable
Characteristic Atoms) and **B10 implementation design §D5 (amended
2026-05-22)**.

- **Foundation Invariant III** (all state immutable; failure prevented:
  historical rewrite): ✓ — published `characteristic.(term, definition)` is
  never edited; supersession appends new immutable rows; concept bindings are
  preserved (concept_version is append-only); corrections mint a new
  characteristic.
- **Foundation Invariant IV** (all references explicit): ✓ — supersession is
  an explicit `predecessor_characteristic_id` → `successor_characteristic_id`
  row; the concept → characteristic binding stays the explicit
  `characteristic_id` column on `business_concept`; cert → characteristic via
  `target_registry_id`.
- **Foundation Invariant V** (evaluation is non-replayable): ✓ — no evaluation
  here; F5 reads are SELECT-only.
- **Foundation Invariant VI** (evidence is emitted, not inferred): ✓ —
  supersession events are typed rows + a `certification_record`;
  `correction_class` is a typed field, not inferred from prose.
- **DEC-02f5a9 §3** (identity is structural, not detected; identity is chosen
  from the governed vocabulary; definitions participate in keeping homographs
  distinct): ✓ — characteristic identity remains structural via
  `characteristic_id`; supersession is an explicit lineage of identity
  replacements; no detection-based identity is introduced.
- **F1 §2** (two nested versioning units — Entity, BusinessConcept): ✓ —
  Characteristic is **not** added as a versioning unit; the F1 model needs no
  amendment.
- **F4-v2 §12** (resolved 2026-05-22 in favour of the flat atom): ✓ — the
  flat row stays flat; supersession is the correction path.
- **B10 implementation design D6** (per-object F3 transition pattern,
  `RegistryPublicationService`): ✓ — `transitionCharacteristicLifecycle`
  mirrors the two existing methods; characteristic publication wires into the
  existing `RegistryPublicationService` (B10b-S3 build).

No Foundation invariant and no ADR is contradicted. DEC-02f5a9 is unchanged.

## 4. Risks

| Risk | Mitigation |
|---|---|
| Partial-unique `WHERE` clause misconfigured | The WHERE must read exactly `lifecycle_state <> 'superseded' AND archived_at IS NULL`; B10b-S2 includes a positive and negative test covering both branches (live-collision blocked; superseded-term re-use allowed). |
| Many invariants are service-layer (predecessor `active`, successor `active`, no in-place definition edits) | Cover with F3 service tests in B10b-S2 / B10b-S3. A future hardening pass may add DB triggers; not in B10b-S1. |
| Post-supersession revert is unsafe | Documented (§D9); revert script aborts when `characteristic_supersession` is non-empty unless force-flagged. |
| A future bug silently rebinds `business_concept.characteristic_id` from predecessor to successor | `business_concept_version` rows are immutable (F1 §2 doctrine); concept versions are append-only — no F3 method UPDATEs the binding on an existing version. Tested by F3-level invariants. |
| `correction_class` mis-classification (a meaning-bearing change filed as `editorial`) | A governance risk, not a system risk: the supersession still creates a new `characteristic_id`, so concepts remain pinned to the predecessor's meaning either way. The classification is audit metadata; mis-classifying it does **not** rebind concept meaning. |

## 5. Out of B10b-S1 scope (deferred)

- The migration packet itself (forward / revert SQL, Drizzle mirror): **B10b-S2**.
- F3 `transitionCharacteristicLifecycle` + `supersedeCharacteristic`
  implementations: **B10b-S2 / B10b-S3**.
- The characteristic publication path (`RegistryPublicationService` extension,
  the publication cert + semantic-finality affirmation DTO, the controller
  wiring): **B10b-S3**.
- F5 supersession-lineage reads + the `ResolvedConcept`
  `characteristicSupersession` hint: **B10b-S3**.
- Provenance-inspection read extension to `characteristic`: **B10b-S3**.
- Live proof — publish `lead time`: **B10b-S4**.
- Archive-of-active characteristic policy (intentionally left out — correction
  of an active is supersession, not archive): future B10b extension if needed.

## Status

`accepted` — operator review-back 2026-05-23. B10b-S1 immutable-characteristic /
supersession DBCP design: the additive `characteristic_supersession` table per
§D1, the partial-unique-on-`term` rule per §D3, no CHECK migration (§D4 —
`superseded` already in the lifecycle CHECK), and the two new F3 methods per
§D5.

> **Review-back tightening — 2026-05-23 (applied before acceptance).**
>
> - **Acyclicity is enforced by F3 traversal, not by the DB.** DB constraints
>   only prevent self-supersession (`predecessor ≠ successor`) and duplicate
>   predecessor supersession (`UNIQUE(predecessor)`); they do not prove global
>   acyclicity (a chain `A → B, B → C, C → A` passes every per-row constraint).
>   F3 `supersedeCharacteristic` traverses the existing supersession lineage
>   before writing and rejects any write that would close a cycle (§D2 / §D5).
> - **v1 supersession is one predecessor → one successor; semantic merges are
>   deferred.** `UNIQUE(successor_characteristic_id)` is part of the DBCP (§D2),
>   so v1 forbids many-to-one merges at both the DB and F3 layers. Merges are a
>   distinct curation operation with their own semantic-equivalence governance
>   — a future design gate.
> - **Normal revert aborts unconditionally if `characteristic_supersession` is
>   non-empty.** There is **no force flag** in the B10b-S2 revert file. A
>   destructive revert from a non-empty state requires a **separate
>   operator-authored data-remediation DBCP** that unwinds the supersession
>   rows under governed review (§D9).

No code, no migration authored, no DB writes, and no activation follow from
this note. The next gate is **B10b-S2** — the migration packet (forward /
revert SQL + Drizzle mirror) implementing this design — to be opened separately
by the operator.
