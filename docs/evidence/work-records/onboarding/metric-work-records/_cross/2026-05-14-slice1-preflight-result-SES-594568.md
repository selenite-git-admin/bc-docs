---
title: "Slice (1) pre-flight result — §14 resolved + plan amendments"
session: SES-594568
date: 2026-05-14
status: complete
type: preflight-result
authority: DEC-a17d0f
related:
  - 2026-05-14-slice1-promotion-gate-plan-SES-594568.md
  - 2026-05-14-pass1-calibration-q1-q4-SES-594568.md
---

# Slice (1) pre-flight result

Read-only resolution of the ten §14 questions in the slice (1)
plan, plus three architectural findings that surfaced during
pre-flight and require plan amendments before execution.

## 1. §14 resolutions

### 14.1 — `metric.metric_definition.status_code` CHECK

CHECK exists: `status_code ∈ {draft, active, deprecated}`. No
`promoted` value. **Decision implied:** seed advances `draft → active`.

(Also discovered, same query: parallel CHECKs on
`composition_code ∈ {primary, derived, composite}`,
`direction_code ∈ {higher_is_better, lower_is_better, target_is_optimal}`,
`maturity_code ∈ {registered, classified, enriched, verified, locked}`.
These constrain the §2 candidate-selection query — see §3.4 below.)

### 14.2 / 14.9 — `contract_json` storage

Lives in **`contract.metric_contract_version`** as a JSONB column,
keyed by `(metric_contract_id, version_code)`. Columns:
`metric_contract_id`, `version_code`, `contract_json`,
`governance_state_code`, `success_score`, `last_validated_at`,
`created_at`, `supersede_after`.

The parent `contract.metric_contract` row carries identity and
classification (per DEC-01df6b — catalog table); the version
row carries the contract body. **Slice (1) writes both — one
parent + one version row** (the first version of the new MC).

### 14.3 — bc-core derivation path

Exists. `contract.service.ts`, `metric-catalog-reader.repository.ts`,
`metric-definition.repository.ts`, and 12 other files reference
`contract_json` / `metric_contract_version`. A
`recordFormulaVerification(data)` writer is already implemented
on `MetricDefinitionRepository` (line 606,
`db.insert(metricFormulaVerification).values(data).returning()`).

What is **not yet present**: a single end-to-end promotion act
that (a) inserts the contract parent + version pair, (b) calls
the verifier, (c) writes the verification row, (d) advances the
seed status. The plumbing exists piecewise; the orchestrating
service method is the slice's actual code work.

### 14.4 — bc-ai endpoint

Exists: `POST /api/ai/suggest/metric-verify` in
`bc-ai/main.py:368`. bc-core client wired:
`BcAiClient.invokeMetricVerifier(body)` in
`registry/semantic/bc-ai-client.service.ts:88` (calls the
`metric-verify` pipeline). Already used by
`l-node-semantic.service.ts`.

### 14.5 — Inference profiles

Configured in `bc-ai/app/config.py`:

| Role | Model alias | Bedrock inference profile |
|---|---|---|
| Maker A | `claude-haiku-4-5-20251001` | `global.anthropic.claude-haiku-4-5-20251001-v1:0` |
| Maker B | `claude-sonnet-4-5-20250929` | `global.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| Moderator | `claude-haiku-4-5-20251001` | (same as Maker A profile) |

Cross-family discipline (Haiku 4.5 vs Sonnet 4.5) is configured.
Moderator on Haiku 4.5 is acceptable per
`docs/ai/ai-trust-and-verification.md` (the moderator's role is
disambiguation, not authority).

### 14.6 — Seed target `status_code`

`active` (only valid CHECK target — see 14.1).

### 14.7 — FK shape for verification → formula

**Resolved by 14.10 finding:** `metric.metric_formula` is keyed
by `metric_definition_id`, not `metric_contract_id`. Formulas
already exist at the **seed level** before any promotion — see
§2 finding A below. Verification row's `metric_formula_id` FK
references an **already-existing** row. **No formula creation
in this slice; §11.1 Option A/B no longer applies. Two-transaction
model in §11 simplifies (no formula or variable write).**

### 14.8 — Master-shape JSON vs DEC-01419c

No ADR supersedes or amends DEC-01419c. 9-key body shape
(`input_type`, `formula`, `variables`, `co_bindings`,
`temporal_gate`, `unit`, `direction_code`, `thresholds`, `grain`)
is current.

### 14.10 — Actual columns

`metric.metric_formula`: `metric_formula_id` (uuid PK),
`metric_definition_id` (uuid FK, NOT `metric_contract_id`),
`formula_text` (text), `unit_type_code` (text FK),
`maturity_code` (text, default `'registered'`), `version_seq`
(int), `is_current` (bool), audit columns. Unique on
`(metric_definition_id, version_seq)`.

`metric.metric_formula_variable`: `metric_formula_variable_id`
(uuid PK), `metric_formula_id` (uuid FK), `var_code` (text),
`role` (text), `field_name` (text), `description` (text),
`unit_type_code` (text), `sort_order` (int), `constant_value`
(numeric).

`metric.metric_binding`: keyed by `metric_contract_id` AND
`canonical_contract_id`, with `binding_role_code` and
`fields_used` (array). **This is the contract-layer binding**
(MC → CC), distinct from variable definitions which live on
the formula.

## 2. Architectural findings from pre-flight

### Finding A — Formulas live at the seed level

All 1,216 `draft` seeds already have at least one `metric_formula`
row. 1,210 of those formulas already have `metric_formula_variable`
rows. The seed/definition layer **owns** formula + variables;
the contract layer is a wrapper that adds (a) governance state,
(b) versioned body (`contract_json`), and (c) CC bindings.

This contradicts the plan's TX2, which assumed promotion writes
the formula + variables. Those rows already exist.

### Finding B — Today's promotion path does not advance seed `status_code`

778 of 1,216 `draft` seeds already have a `contract.metric_contract`
row. Yet all 1,216 are still in `status_code='draft'`. Whatever
path creates contracts today does **not** flip seed status. So
the live system has a divergence between "has a contract" and
"is `active` per CHECK." 438 seeds with no contract are eligible
candidates for slice (1).

This is a real-state finding; the plan must decide whether to
match today's behavior (leave seed in `draft`) or to introduce
the seed-status advance (`draft → active`) as part of the slice's
formal gate — and if so, do that **only for the one slice metric**,
not retroactively for the 778 already-promoted-without-flip seeds.

**Recommended:** slice (1) writes the seed-status advance for
the one candidate. The 778 are surfaced as Pass 1 §3.3.6
territory — count divergence — and addressed later, not by this
slice.

### Finding C — Contract is two rows, not one

Promoting writes **both** `contract.metric_contract` (parent,
identity/classification) and `contract.metric_contract_version`
(body with `contract_json`, `governance_state_code='active'`,
`version_code='1.0.0'`). Plan §3 assumed one row; correction
required.

## 3. Plan amendments required

### 3.1 §3 / §4 / §5 — Target state and body fields

The MC body's `variables` and `co_bindings` content come **from
the existing `metric_formula` / `metric_formula_variable` rows**
on the seed, projected into the JSON body. The promotion act
**reads** them, not creates them. Body construction is a
**projection** of the seed-side artifact into JSON, written into
the version row's `contract_json` column.

### 3.2 §11 — Transactional model (simpler)

Revised two-transaction model:

- **TX1 — audit (always commits).** Insert one row into
  `metric.metric_formula_verification` with the maker outputs,
  cross-validation, moderator verdict, and `verdict_code`. The
  `metric_formula_id` FK points to the **existing** formula row
  on the seed. No formula or variable write.
- **TX2 — state advance (commits only on `verdict_code='pass'`).**
  Three writes, atomic:
  1. Insert one `contract.metric_contract` row referencing
     `metric_definition_id`.
  2. Insert one `contract.metric_contract_version` row with
     `contract_json` (the 9-key body projected from the seed),
     `version_code='1.0.0'`, `governance_state_code='active'`.
  3. Update `metric.metric_definition`: `status_code='active'`,
     `verification_result_code='pass'`,
     `verification_evidence_id` = the TX1 verification UUID.

TX1's verification row stands on its own evidence-ledger logic
(Invariant VI). TX2's three writes are atomic. No FK issue.

### 3.3 §10 — Code paths (refined)

| Layer | Path | Change |
|---|---|---|
| Service | `bc-core/src/registry/metric-definition.service.ts` (or new `metric-contract-promotion.service.ts`) | Add `promoteDefinition(metricDefinitionId, testData, expectedOutput, options)` orchestrating TX1 + TX2. |
| Service | bc-core | Add `buildContractJsonFromDefinition(metricDefinitionId)` — pure projection of seed-side rows into the 9-key body. No new column reads required (all data is on existing rows). |
| Service | bc-core `BcAiClient.invokeMetricVerifier` | **Already exists** — used as-is. May need a small payload shape adjustment to include test data + expected output; confirm against the v1.0 metric-verify prompt contract before execution. |
| Repository | `MetricDefinitionRepository.recordFormulaVerification` | **Already exists** — used as-is for TX1. |
| Repository | bc-core | Add or use existing inserts on `metric_contract` + `metric_contract_version` (TX2). |
| Controller | bc-core platform endpoint | Add `POST /metric-definitions/{id}/promote` — `@PlatformOnly()`, body `{testData, expectedOutput}`. |

### 3.4 §2 — Candidate-selection query (corrected vocabulary)

Use actual CHECK-allowed values; drop the wrong `composition_code`
and `function_code` references:

```sql
SELECT md.metric_definition_id, md.metric_name, md.display_name,
       md.composition_code, md.category_code, mf.formula_text,
       (SELECT COUNT(*) FROM metric.metric_formula_variable mfv
        WHERE mfv.metric_formula_id = mf.metric_formula_id) AS n_vars,
       LENGTH(md.description_text) AS desc_len
FROM metric.metric_definition md
JOIN metric.metric_formula mf
  ON mf.metric_definition_id = md.metric_definition_id
 AND mf.is_current = true
LEFT JOIN contract.metric_contract mc
  ON mc.metric_definition_id = md.metric_definition_id
WHERE md.status_code = 'draft'
  AND mc.metric_contract_id IS NULL          -- no contract yet
  AND md.composition_code = 'primary'        -- simplest composition
  AND md.category_code IN ('cost','volume','time')  -- simple aggregations
  AND md.description_text IS NOT NULL
  AND LENGTH(md.description_text) >= 80
ORDER BY md.metric_seq
LIMIT 20;
```

438 seeds in the unpromoted pool; the filters above shortlist to
the safest candidates.

### 3.5 §9 — DBCP question resolved

No DB schema change required. The existing CHECK on
`status_code` already permits `active`. No new column needed.
**No DBCP filed.**

### 3.6 §12 — Postflight queries updated

12.2 should query `contract.metric_contract_version.contract_json`,
not a non-existent `contract.metric_formula` projection. Revised:

```sql
-- 12.2 contract_json body shape conforms to master-shape
SELECT (mcv.contract_json -> 'body') ?& ARRAY[
  'input_type','formula','variables','co_bindings',
  'temporal_gate','unit','direction_code','thresholds','grain'
] AS body_has_all_9_keys
FROM contract.metric_contract_version mcv
JOIN contract.metric_contract mc
  ON mc.metric_contract_id = mcv.metric_contract_id
WHERE mc.metric_definition_id = $1
  AND mcv.version_code = '1.0.0';
-- expect true
```

```sql
-- 12.2b body.formula.text matches seed-side formula_text
SELECT (mcv.contract_json -> 'body' -> 'formula' ->> 'text') =
       (SELECT mf.formula_text FROM metric.metric_formula mf
        WHERE mf.metric_definition_id = mc.metric_definition_id
          AND mf.is_current = true) AS formula_matches
FROM contract.metric_contract_version mcv
JOIN contract.metric_contract mc
  ON mc.metric_contract_id = mcv.metric_contract_id
WHERE mc.metric_definition_id = $1
  AND mcv.version_code = '1.0.0';
-- expect true
```

12.3 already correct against the live schema.

## 4. Remaining work before execution

| # | Item | Status |
|---|---|---|
| A | Apply plan amendments §3.1–§3.6 to slice (1) plan MWR (edits, not a new plan) | Pending operator approval |
| B | Run the corrected §3.4 candidate query; pick one UID | Pending — operator picks from query output |
| C | Confirm bc-ai `metric-verify` v1.0 prompt accepts `{testData, expectedOutput}` in its payload, or that this slice needs a small prompt update | Pending — read `bc-ai/app/prompts/metric-verify/v1.0/*.md` before execution |
| D | Decide on `metric_contract_version.version_code` initial value (`'1.0.0'` proposed) and `governance_state_code` initial value (`'active'` proposed; verify this is the allowed initial state vs `'review'`/`'approved'` first) | Pending — verify against `contract.metric_contract_version`'s CHECK on `governance_state_code` |

(D) is the only remaining factual unknown; the rest are
operator-facing decisions.

## 5. Boundaries honoured

- No code change.
- No DB write.
- All queries `SELECT` only.
- No new ADR, DBCP, task.
- One candidate-pool query and one schema introspection per
  table; nothing speculative.
- No changes to the 1,216 existing seeds or 778 existing
  contracts.

---

**End of pre-flight result.**
