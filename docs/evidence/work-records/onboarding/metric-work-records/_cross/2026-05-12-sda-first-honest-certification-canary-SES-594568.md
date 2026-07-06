---
title: "SDA first honest certification canary — credit_status_customer_identifier"
session: SES-594568
date: 2026-05-12
status: complete
type: canary-record
authority: DEC-a17d0f
related:
  - DEC-a17d0f # SDA umbrella
  - DBCP-1k    # Tranche 2 lifecycle alignment (applied)
  - DBCP-1l    # BF.semantic_family support (applied)
---

# SDA first honest certification — canary record

**One business_field, end-to-end through SDA-4, every gate verdict computed from real persisted state. No operator-asserted bypass, no DB hand-edits, no overrides.**

## 1. Primitive

| field | value |
|---|---|
| primitive_type | `business_field` |
| field_id | `019d7050-4513-792c-8fb1-c307fbdeaebe` |
| name | `credit_status_customer_identifier` |
| object_class | `credit_status_customer` |
| parent BO (via `business_object_field`) | `credit_status` (certified) |
| data_type | `string` |
| pii_classification | `indirect_identifier` |

## 2. Final state

### 2.1 Metadata

- `semantic_family = 'identifier'`
- `definition_standard = 'BARECOUNT'`
- `standard_ref = NULL` (BARECOUNT is the only internal definition-standard; no ref required)

### 2.2 Lifecycle

- `status_code = 'certified'`
- `updated_at = 2026-05-12 15:40:03 UTC`

### 2.3 Ledger — `contract.certification_record`

Exactly **2 rows** for this primitive, ordered by `created_at`:

| # | action_code | from → to | gate_count | override? | created_at |
|---|---|---|---|---|---|
| 1 | `submit_for_review` | `proposed → reviewing` | 0 | all 3 override cols NULL | 2026-05-12 15:23:22 |
| 2 | `certify` | `reviewing → certified` | **9** | all 3 override cols NULL | 2026-05-12 15:40:03 |

Both rows: same certifier identity (`anant@selenite.co`, role `platform_admin`, sub `8bdb9bd0-…`). No `supersedes_primitive_id`. No `advisory_verdicts`. Atomic dual-write (status flip + ledger insert in one transaction) verified by `business_field.updated_at` matching the certify ledger's `created_at` to the millisecond.

### 2.4 Gate verdicts on the certify row

All 9 `pass`, all sourced from real persisted state (no `detail.unevaluable` flag anywhere):

| Gate | Verdict | Source-of-truth |
|---|---|---|
| G1 | pass | name shape (snake_case + `credit_status_customer_` prefix) |
| G2a | pass | 0 exact name collisions in `contract.business_field` |
| G2b | pass | 0 normalized-form collisions |
| G3 | pass | 199-char definition, no banned tokens, sentence-punctuated |
| G4 | pass | `definition_standard='BARECOUNT'` ∈ `DEFINITION_STANDARDS_SET`; internal → no ref required |
| G5 | pass | `semantic_family='identifier'` ∈ `SEMANTIC_FAMILY_ENUM` |
| G6 | pass | `data_type='string'` ∈ `master.semantic_family['identifier'].compatible_data_types=['string']` |
| G7 | pass | name starts with `BF.object_class` prefix |
| G8 | pass | CF-only gate; N/A for BF |

## 3. Commits this canary produced

All on `bc-core/main`, pushed.

| Commit | Scope |
|---|---|
| `4fcb03f` | Service-layer pass-through bug — `dto.definitionStandard` was being mapped from a nonexistent `dto.sourceStandard` field. Single-line functional fix in `StandardFieldService.updateField`. |
| `20674ef` | G4 vocabulary split — new uppercase `DEFINITION_STANDARDS` / `EXTERNAL_DEFINITION_STANDARDS` constants in `gates.ts` mirroring `master.master_definition_standard.slug` verbatim. `evaluateG4` switched to the new set. Lowercase `SOURCE_STANDARDS` retained for the provenance-record domain (DBCP-1f) — provenance-domain code and tests untouched. |
| `72f22a9` | `@Allow()` decorator on `GateResultDto.detail` so the global `ValidationPipe` (with `forbidNonWhitelisted: true`) passes the free-form diagnostic payload through. 6-case DTO-contract spec added to prevent regression. |

Of the three commits, only `4fcb03f` used the operator-authorized `--no-verify` (pre-existing ESLint debt in `standard-field.service.ts`, TSK-c94055). The other two passed the pre-commit hook cleanly.

## 4. Bugs surfaced and fixed during the canary

Each was uncovered by attempting the next honest forward step, surfaced as a real error rather than a manufactured assertion.

### 4.1 `definitionStandard` DTO/service pass-through dropped silently

**Symptom:** PATCH `{"definitionStandard":"bc_standard"}` returned HTTP 200 with `"definitionStandard":null` in the response. DB column stayed NULL.

**Root cause:** `StandardFieldService.updateField` mapped `sourceStandard: dto.sourceStandard` — but `UpdateStandardFieldDto` has no `sourceStandard` field. Wire name was `definitionStandard`. The mapping was a pre-existing tsc error (one of several `sourceStandard` errors in that file) that had been masked because the line `value` was always `undefined` and Drizzle's `set(...)` skips undefined fields.

**Fix:** commit `4fcb03f`. Changed the one mapping line. Side effect: cleared 2 pre-existing tsc errors at lines 172/174.

### 4.2 G4 vocabulary conflation between metadata and provenance domains

**Symptom:** After fixing 4.1, PATCH `{"definitionStandard":"bc_standard"}` returned HTTP 500 — DB FK rejected `bc_standard` because `master.master_definition_standard` doesn't have that slug (the master uses `BARECOUNT`). Worse, even setting `BARECOUNT` directly via SQL would fail G4 because `gates.ts:SOURCE_STANDARDS` was lowercase only.

**Root cause:** two governed vocabularies for two different concepts, conflated under one in-code constant:

- `contract.primitive_provenance.source_standard` — lowercase, governed by its own CHECK constraint (DBCP-1f). Provenance ledger domain.
- `business_field.definition_standard` — uppercase, governed by FK to `master.master_definition_standard`. Primitive metadata domain.

Both used the same `gates.ts:SOURCE_STANDARDS` set, which modeled only the lowercase one. G4 read the wrong SSOT for the column it was evaluating.

**Fix:** commit `20674ef`. Path X from the in-session discussion — split the in-code vocabulary in two:

- Kept `SOURCE_STANDARDS` (lowercase, 7 values incl. `bc_standard`, `computed`) for the provenance-record domain. **Provenance-domain code and tests deliberately untouched.**
- Added `DEFINITION_STANDARDS` (uppercase, 7 values: `BARECOUNT, COSO, IFRS, IIA, ISO_20022, OAGIS, US_GAAP`) for `evaluateG4`. `BARECOUNT` is the only internal standard (no `standard_ref` required). No `computed` analog exists in the master table; operator decision was to not invent one — future "computed provenance" semantics must use the provenance ledger, not the `definition_standard` column.
- Updated only G4 tests + one orchestrator fixture + one certification-record fixture. Provenance-record specs preserved verbatim.

### 4.3 `GateResultDto.detail` blocked by global `ValidationPipe`

**Symptom:** First certify call returned HTTP 400 with 9 errors of the form `gateResults.N.property detail should not exist`. State was at `reviewing` (from the prior successful submit-for-review) but certify couldn't proceed.

**Root cause:** `GateResultDto.detail` carried no class-validator decorator. The global `ValidationPipe` runs with `forbidNonWhitelisted: true`, so any property without a decorator is treated as "not declared, reject". The service-level spec (`state-transition.spec.ts`) drives the orchestrator via the InMemory repo directly, bypassing the HTTP validation pipeline — which is why the regression slipped through.

**Fix:** commit `72f22a9`. `@Allow()` on `detail` — narrowest class-validator decorator that says "permitted, do not inspect internals". Added a 6-case DTO-contract spec (`state-transition.controller.spec.ts`) using `plainToInstance` + `validateSync` with the same options the global pipe uses, so this class of bug fails at `npm test` rather than in production traffic.

## 5. Follow-ups already logged (no action in this canary)

| Task | Title | Status |
|---|---|---|
| [TSK-84d81c](mcp://devhub) | Decide on `data_type='code'` legitimacy across the BF registry (779 BFs) | `planned/later` |
| [TSK-000fa7](mcp://devhub) | Investigate BF `object_class` vs linked BO `object_name` mismatch | `planned/later` |
| [TSK-c94055](mcp://devhub) | Clear pre-existing ESLint debt in `standard-field.service.ts` | `planned/later` |

The first two were surfaced during this canary (not actionable here without scope creep). The third predates the canary; the `4fcb03f` commit's `--no-verify` references it.

## 6. Boundaries honoured

- **One primitive only.** Exactly `credit_status_customer_identifier` touched at the row level. Every other BF/CF/BO row in the registry remains unchanged.
- **No backfill.** The new `semantic_family` column from DBCP-1l still has 7,061 rows at `NULL` (was 7,062; the canary BF accounts for the one row at `'identifier'`).
- **No CF or BO certification.** Out of scope; CF/BO gate-evaluation surfaces don't exist yet.
- **No DBCP execution in this canary step.** DBCPs 1k and 1l were already applied in earlier turns; this canary used the resulting schema as-is.
- **No metric repair writes.** Nothing in `metric.*` / `tenant.*` / `runtime.*` was touched.
- **No supersede, archive, or unarchive.** Out of scope for SDA-4 Tranche 2 per DBCP-1k §6.4.
- **Provenance ledger untouched.** No `primitive_provenance` rows written by this canary. The vocabulary split in commit `20674ef` deliberately preserved the provenance-domain lowercase constants.

## 7. What this proves

1. The end-to-end SDA-4 flow works honestly on real persisted state — gates are computed from DB columns, not asserted by the caller.
2. DBCP-1l's `business_field.semantic_family` column materially influenced certify verdicts (G5/G6 evaluation depended on it). The structural gap from earlier sessions is functionally closed.
3. The G4 vocabulary split (commit `20674ef`) was the correct resolution to the metadata-vs-provenance conflation. After the split, real `BARECOUNT` values from the FK-governed column flow cleanly through G4.
4. The certification ledger's atomic dual-write contract holds under live writes — every state flip on the primitive is paired with exactly one ledger row, both committed in the same Postgres transaction.

## 8. Next gates (not in scope for this canary)

- Replicating the canary on a second BF to confirm the pattern beyond a single specimen.
- Bringing more draft BFs to certified status (operator-driven, one at a time, each with platform-computed gateResults).
- CF and BO equivalents of `gate-evaluation.service.ts` + a possible CF/BO `semantic_family` schema slice mirroring DBCP-1l.
- SDA-4 supersede / archive / unarchive endpoints (deferred per DBCP-1k §6.4).

Each is its own slice — none authorized by this MWR.

---

**End of canary record.**
