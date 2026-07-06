---
title: "DBCP — Seed canonical-v2 + observation-v2 contract meta-schema rows"
description: "Database Change Protocol proposal to seed the two D430/D431 v2 contract meta-schema rows into contract.contract_meta_schema. Step 1 of the D429 apply/proof sequence. Read-only proposal — no DB change applied."
status: proposed
date: 2026-06-08
project: bc-core
domain: contract-governance
subdomain: meta-schema
focus: apply
---

# DBCP — Seed `canonical-v2` + `observation-v2` contract meta-schema rows

**Status:** PROPOSED — held for review. **No DB change is applied by this document.**
**Step:** 1 of the D429 apply/proof sequence (seed v2 grammars → ARPI MC rebind → OC-v2 slice → CC-v2 slice → O→C→M proof → MCF materialization).
**Authorities:** DEC-a6258b (D430, canonical-v2, merged `a3d41ea`) · DEC-4a17e0 (D431, observation-v2, merged `495c45a`).

---

## 0. Purpose & one-paragraph summary

D430 and D431 are merged **as code**: the immutable `canonical-v2` and `observation-v2`
meta-schema files exist on `main`, are registered in the seeder's `META_SCHEMAS` list, and
are exercised by unit tests. They are **not yet loadable at runtime**: `ContractValidationService`
selects a meta-schema by the envelope `$contract` via
`ContractGovernanceRepository.findMetaSchema(category, metaVersion)`, which reads a **DB row**
from `contract.contract_meta_schema`. No `canonical/2` or `observation/2` row exists, so any
attempt to author a v2 body would fail validation. This DBCP seeds exactly those **two rows**,
via the existing idempotent service method, so the v2 grammars become selectable — the
prerequisite for authoring the ARPI v2 OC/CC slices. Nothing else.

---

## 1. Exact target rows

Table: **`contract.contract_meta_schema`** · Primary key: **`(category_code, meta_version)`** (composite).
Columns: `category_code text`, `meta_version int`, `json_schema jsonb`, `status_code text`,
`description_text text`, `created_at timestamptz DEFAULT now()`.

### Row A — canonical-v2
| Field | Value |
|---|---|
| `category_code` | `canonical` |
| `meta_version` | `2` |
| `json_schema` | **byte-for-byte** the contents of `bc-core/src/registry/meta-schemas/canonical-v2.schema.json` (SSOT). Envelope identity inside: `$id = https://barecount.dev/contracts/canonical/v2`, `$contract const = barecount/canonical/v2`. |
| `status_code` | `active` |
| `description_text` | `Canonical contract master shape v2 — field-level semantic identity (D430/DEC-a6258b)` |
| `created_at` | DB default `now()` — **not part of row identity**, not asserted. |

### Row B — observation-v2
| Field | Value |
|---|---|
| `category_code` | `observation` |
| `meta_version` | `2` |
| `json_schema` | **byte-for-byte** the contents of `bc-core/src/registry/meta-schemas/observation-v2.schema.json` (SSOT). Envelope identity inside: `$id = https://barecount.dev/contracts/observation/v2`, `$contract const = barecount/observation/v2`. |
| `status_code` | `active` |
| `description_text` | `Observation contract master shape v2 — field-level semantic identity (D431/DEC-4a17e0)` |
| `created_at` | DB default `now()` — **not part of row identity**, not asserted. |

**Schema payload source = the two merged SSOT JSON files**, identical to the `canonicalMetaV2` /
`observationMetaV2` imports already in `seed-registry-full.ts` (`META_SCHEMAS` entries, lines 94 & 97).
No hand-authored JSON; the apply imports the same files the seeder does.

---

## 2. Write mechanism — SERVICES-ONLY (no raw INSERT behind the service)

The canonical writer already exists and is idempotent:

```
ContractGovernanceRepository.upsertMetaSchema({ category, metaVersion, jsonSchema, status, description })
  → existing = findMetaSchema(category, metaVersion)
  → if existing: UPDATE json_schema/status_code/description_text  (← we will NOT reach this branch)
  → else:        INSERT (category_code, meta_version, json_schema::jsonb, status_code, description_text)
```

The apply is a small, env-gated, dry-run-default script (mirroring the Phase A apply-script
pattern) that, **for the two v2 entries only**:
1. reads `findMetaSchema(category, 2)`;
2. applies the §3 idempotency rule (absent → insert; identical → skip; different → **refuse**);
3. calls `upsertMetaSchema(...)` only for an absent row (so only the INSERT branch runs).

**Rejected alternative:** running full `npm run seed` / `seedMetaSchemas()`. That upserts **all**
`META_SCHEMAS` entries, issuing an `UPDATE` against the six existing v1 rows — a v1 mutation,
violating §4. It also runs the entire registry seed. Out of scope. The apply touches the two v2
entries and nothing else.

> The apply script itself is **not authored by this DBCP**. It is the next gated artifact, written
> only after this proposal is locked, and run dry-run first.

---

## 3. Idempotency rule

Keyed on the PK `(category_code, meta_version)`:

- **Absent** → INSERT the row (normal path).
- **Present AND canonically JSON-identical** (`json_schema` deep-equals the SSOT file; `status_code='active'`;
  `description_text` equals the string in §1) → **SKIP** (log `already-present-identical`, exit 0 for that row).
- **Present AND any field differs** → **REFUSE**: abort without writing, emit the drift, exit non-zero.
  Do **not** UPDATE/overwrite — re-running must never silently mutate an existing meta-schema row.

This makes the apply safe to re-run and prevents an accidental overwrite of a v1 (or a hand-touched v2) row.

---

## 4. Apply plan

1. Pre-apply verification (§5) must PASS (exactly 6 v1 rows; no v2 of any category).
2. Insert **only** Row A (`canonical/2`) and Row B (`observation/2`) via the service's INSERT branch.
3. **No `UPDATE`, no `DELETE`, no DDL.** The six v1 rows are not read-for-write and not modified.
4. Env-gated (e.g. `BCCORE_APPLY_V2_META_SCHEMA_SEED=1`); dry-run by default; pre/post evidence
   artifacts written under `scripts/audit-output/`.
5. Order within the apply is irrelevant (the two rows are independent; neither FKs the other).

---

## 5. Pre-apply verification (must hold before any write)

Captured read-only at draft time (`bc_platform_dev`, 2026-06-08) and to be re-asserted at apply time:

```sql
-- Exactly 6 rows, all v1, all active; NO v2 of any category:
SELECT category_code, meta_version, status_code
FROM contract.contract_meta_schema ORDER BY category_code, meta_version;
-- EXPECT: admission/1, canonical/1, intervention/1, metric/1, observation/1, source/1   (6 rows, all 'active')

-- No v2 contract versions exist yet (also the rollback-safety baseline):
SELECT count(*) FROM contract.canonical_contract_version    WHERE contract_json->>'$contract' = 'barecount/canonical/v2';     -- EXPECT 0
SELECT count(*) FROM contract.observation_contract_version  WHERE contract_json->>'$contract' = 'barecount/observation/v2';   -- EXPECT 0
```

Draft-time result: **6 v1 rows exactly; canonical-v2 versions = 0; observation-v2 versions = 0.** ✅

---

## 6. Post-apply verification

```sql
-- 8 rows total; canonical and observation each carry v1 AND v2; other categories untouched:
SELECT category_code, array_agg(meta_version ORDER BY meta_version) AS versions, count(*)
FROM contract.contract_meta_schema GROUP BY category_code ORDER BY category_code;
-- EXPECT: admission {1}, canonical {1,2}, intervention {1}, metric {1}, observation {1,2}, source {1}

-- The two new rows carry the correct $contract identity and active status:
SELECT category_code, meta_version, status_code,
       json_schema->>'$id'        AS schema_id,
       json_schema->'properties'->'$contract'->>'const' AS contract_const
FROM contract.contract_meta_schema
WHERE (category_code,meta_version) IN (('canonical',2),('observation',2));
-- EXPECT canonical/2 → barecount/canonical/v2 ; observation/2 → barecount/observation/v2 ; both 'active'
```

Acceptance: the four non-v2 categories (`admission`, `intervention`, `metric`, `source`) remain
**v1-only**; `canonical` and `observation` each gain exactly one v2 row; both v2 `json_schema`
payloads byte-match their SSOT files (verified by `$contract const` + a hash/deep-equal of the
stored jsonb against the file).

---

## 7. Rollback

Reverse is a delete of **only the two v2 rows**, guarded by a no-reference precondition:

```sql
-- Guard: refuse rollback unless NO contract version references either v2 grammar.
SELECT count(*) FROM contract.canonical_contract_version    WHERE contract_json->>'$contract' = 'barecount/canonical/v2';    -- must be 0
SELECT count(*) FROM contract.observation_contract_version  WHERE contract_json->>'$contract' = 'barecount/observation/v2';  -- must be 0

-- Only if BOTH are 0:
DELETE FROM contract.contract_meta_schema WHERE category_code='canonical'   AND meta_version=2;
DELETE FROM contract.contract_meta_schema WHERE category_code='observation' AND meta_version=2;
```

If any v2 contract version exists, **rollback is refused** (deleting the grammar a live version
validates against would orphan it). No v1 row is ever deleted. There is no FK from version tables
to `contract_meta_schema`; the reference is the logical `$contract` envelope match used above.

---

## 8. Scope exclusions (hard)

- ❌ No DDL (the table and PK already exist).
- ❌ No Drizzle schema changes.
- ❌ No contract-instance authoring (no SC/AC/OC/CC/MC versions created).
- ❌ No ARPI MC rebind.
- ❌ No greenfield OC/CC.
- ❌ No MCF materialization.
- ❌ No v1 mutation; no other category touched; no UPDATE/DELETE in the apply.
- Blast radius = **two INSERTs** into one platform table.

---

## 9. Sequencing confirmation — OC-v2 active slice must precede CC-v2 authoring

This seed unblocks v2 authoring; it does **not** relax ordering downstream. The D431 O↔C check is
**fail-closed at BOTH canonical-v2 authoring and activation** (`ContractService` →
`ObservationConceptResolverService.assertConceptsObservableFromSource`): every concept a `canonical-v2`
CC selects must already be declared observable by **≥1 active `observation-v2` mapping**. Therefore,
in the apply/proof sequence:

1. Seed v2 meta-schema rows (**this DBCP**) — prerequisite for any v2 body to validate.
2. ARPI observation-v2 OC slice authored **and activated** first.
3. ARPI canonical-v2 CC slice authored only **after** (2) is active — else the O↔C gate refuses it.

(The ARPI MC version may be authored against the active BCF anchors independently, but the
O→C→M chain can only be proven once the OC→CC slices exist beneath it.)

---

## 10. Foundation Invariant Check (data/boundary change)

**Repair location: B → E.** The meta-schema row is the storage materialization (E) of a contract
grammar (B) whose semantics were decided and merged in D430/D431. This apply makes an already-locked
grammar **selectable** by the validator (D); it introduces no new meaning.

- **Why this location?** Without the DB row, `findMetaSchema(category, 2)` returns nothing and the
  v2 grammar is unreachable at the admission/validation boundary. The row is the storage projection
  of the locked grammar — the correct and only place this belongs.
- **Why not upper layers (A/B)?** B (the grammar) is fully specified and merged; A (source reality)
  is irrelevant — meta-schemas are platform definitions, not source-emitted.
- **Why not lower layers?** This *is* the storage layer; no working implementation is bypassed — the
  apply uses the existing `upsertMetaSchema` service, not a hand INSERT.

Invariants I–VI: meaning is still produced once, at the contract boundary (I); no ordering, mutation,
implicit reference, replay, or inferred-evidence concern is introduced — this is an additive,
governed apply of a locked artifact. **No invariant is violated.**

---

## 11. Decision requested

Approve/lock this DBCP so the env-gated dry-run apply script (the next gated artifact) can be authored.
**No DB change is applied until you explicitly approve the apply step after reviewing the dry-run.**
