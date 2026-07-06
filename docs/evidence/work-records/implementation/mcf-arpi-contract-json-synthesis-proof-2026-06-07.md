---
title: "MCF ARPI contract_json Synthesis Proof (read-only)"
description: Read-only feasibility proof — can the runtime contract.metric_contract_version.contract_json envelope be synthesized for the already-published MCF ARPI metric from the normalized mcf.* tables without losing meaning? Produces a proposed synthesized envelope, a field-by-field comparison vs the runtime shape, the non-derivable fields, the translation-needed fields, the metric_definition_id FK analysis, an engine-change feasibility verdict, and the minimum DBCP scope. Analysis only — no code, no schema, no DB write, no materialization, no panel.
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: metric-store
focus: materialization-boundary
---

# MCF ARPI `contract_json` Synthesis Proof (read-only)

> **What this is.** A read-only feasibility proof for the first step of Option B (per `mcf-materialization-boundary-options-2026-06-07.md`). It answers one question for **one** metric (ARPI), writes nothing, and authorizes nothing. No `synthesizeContractJson` is implemented; no `contract.*` row is written; no legacy cleanup is started. Follows D428 §9 guardrail.

## Question

> Can we synthesize the runtime `contract.metric_contract_version.contract_json` envelope for the already-published MCF ARPI metric from the normalized `mcf.*` tables, **without losing meaning**?

## Headline answer

**Partially — and NOT to an evaluable state today.**

- The envelope **structure and identity** (formula text from the AST, variable skeleton, temporal-gate shape, header name/description/governance) **are derivable/translatable** from `mcf.*`. → enough for **Bar 1 (publication visibility)**.
- The envelope's **evaluation-critical field bindings** — `co_bindings.canonical_contract`, `co_bindings.fields_used`, `variables[].field_code`, `grain[].field_code`, `temporal_gate.field_code` — **cannot be derived from `mcf.*` or anywhere else in the live platform today**, because they all reduce to one missing resolution: **BCF business-concept → canonical-contract field**. → blocks **Bar 2 (evaluation readiness)**.

So *meaning is partially lost*: specifically the **source-field binding** meaning. The metric's *intent* survives synthesis; its *computability* does not.

## Evidence base (live, 2026-06-07)

**ARPI MCF substrate** (`mc_name = average_revenue_per_invoice`, `metric_contract_uid = 49cdde1a…`, `mcv = 8c088f55…`, `governance_state_code = active`, `is_current = true`):

- `formula_ast_canonical_json`: `divide( sum(var:numerator_source), count_distinct(var:denominator_key) )`
- `temporal_gate_shape_code = period_aggregate`; `temporal_gate_params_json = {"period_type":"fiscal_period"}`
- `grain_entity_id = e3963e45…` (a `concept_registry.entity`, active — the Customer Invoice entity)
- `function_code = NULL`, `subfunction_code = NULL`, `threshold_json = NULL`, `owner_json = NULL`, `tags = NULL`
- **3 variable bindings** (`mcf.metric_variable_binding`), all on entity `e3963e45`, **all bound to BCF business concepts**, none carrying a canonical pointer:

| role | role_kind | bound_business_concept_id | repr term | unit | data type |
|---|---|---|---|---|---|
| `numerator_source` | input | `a42d3fc0…` | amount | USD | decimal |
| `denominator_key` | input | `095afe86…` | identifier | — | string |
| `temporal_anchor` | input | `d05f24b3…` | date | — | date |

- **0** `mcf.metric_filter_clause` rows, **0** `mcf.metric_computed_dimension_ref` rows. (The "customer invoices / posted within the period" scoping is implicit in the entity + temporal gate, not explicit filter rows.)

**Runtime envelope shape** (`contract.metric_contract_version.contract_json`, all 1022 rows): top-level `{version, header, $contract, body}`; `loadEnvelope()` → `normalizeEnvelope()` (metric.service.ts:814) flattens `body.{computation, co_bindings|inputBindings, formula, variables, temporal_gate, thresholds, grain}` into the engine envelope. The engine's formula parser is **text/token-based** (`SUM`, `COUNT_DISTINCT`); `resolveInputBindings()` consumes `body.co_bindings` of the form `{role, fields_used:[...], canonical_contract:"cc__…"}`.

**The missing resolution (the crux), proven by absence:**
- `information_schema`: **0 columns** named `%concept%` in `contract` / `canonical` / `metric` / `progression`. The canonical-contract layer the engine evaluates is **not linked to BCF concepts**.
- `concept_registry.business_concept_version` = `{concept_version_id, concept_id, definition, provenance_json, certification_record_id, panel_run_uid, …}` — **no canonical/field/source binding**. `concept_registry` carries only `entity_version.canonical_name` (a display string).
- ∴ there is **no join path** from ARPI's `bound_business_concept_id` → a `canonical_contract` + `field_code`. This is a missing **binding layer (Foundation repair-location C)**, not an engine defect.

## 1. Proposed synthesized ARPI `contract_json` (read-only — written nowhere)

`UNRESOLVED@C` marks a value that requires the absent BCF-concept→canonical-field resolution.

```jsonc
{
  "$contract": "barecount/metric/v1",
  "version": "1.0.0",
  "header": {
    "kind": "metric",
    "category": "metric",
    "name": "average_revenue_per_invoice",
    "display_name": "Average Revenue per Invoice",
    "description": "The average amount of revenue generated per invoice over a fiscal period, computed as sum(posted amount) / count_distinct(invoice document number) for customer invoices posted within the period.",
    "domain": null,           // mcf function_code is NULL → no domain
    "subdomain": null,        // mcf subfunction_code is NULL
    "owner": null,            // mcf owner_json is NULL
    "governance": { "state": "active" },   // ← mcf governance_state_code
    "contract_id": "<new contract uuid>",  // minted on write (not from mcf)
    "tenant_scope": { "scope": "global" }
  },
  "body": {
    "unit": "currency",                    // derivable from numerator unit USD
    "direction_code": "higher-is-better",  // from seed/default (not in active MCV)
    "formula": { "text": "O1 = SUM(I1) / COUNT_DISTINCT(I2)" },  // ← AST translation
    "variables": [
      { "role": "output", "var_code": "O1", "field_code": "average_revenue_per_invoice" },
      { "role": "input",  "var_code": "I1", "field_code": "UNRESOLVED@C (numerator_source → canonical field)" },
      { "role": "input",  "var_code": "I2", "field_code": "UNRESOLVED@C (denominator_key → canonical field)" }
    ],
    "grain": [
      { "key": "fiscal_period", "source": "business_field", "field_code": "UNRESOLVED@C (period field on canonical)" }
    ],
    "co_bindings": [
      { "role": "primary",
        "canonical_contract": "UNRESOLVED@C (which cc carries the invoice posted-amount / doc-number / posting-date)",
        "fields_used": ["UNRESOLVED@C", "UNRESOLVED@C", "UNRESOLVED@C"] }
    ],
    "temporal_gate": {
      "field_code": "UNRESOLVED@C (temporal_anchor → canonical posting-date field)",
      "required_periods": 1,
      "completeness_threshold": 0.8
    }
  }
}
```

Everything outside `UNRESOLVED@C` is derivable from `mcf.*` today. Every `UNRESOLVED@C` is the **same** missing resolution.

## 2. Field-by-field comparison (mcf.* → runtime envelope)

| Runtime field | Source in `mcf.*` | Status |
|---|---|---|
| `$contract`, `version` | constants | ✅ constant |
| `header.name` / `display_name` / `description` | `mc_name` / `display_name` / `description_text` | ✅ direct |
| `header.kind` / `category` | constant `"metric"` | ✅ constant |
| `header.governance.state` | `governance_state_code` | ✅ direct |
| `header.domain` / `subdomain` / `owner` | `function_code` / `subfunction_code` / `owner_json` | ⚠️ all NULL on ARPI (cosmetic gap) |
| `header.contract_id` | — | 🟡 minted on write |
| `body.unit` | `unit_code_snapshot` (numerator = USD) | 🟠 translate (USD→"currency") |
| `body.direction_code` | not on active MCV | 🟡 seed/default |
| `body.formula.text` | `formula_ast_canonical_json` | 🟠 **translate** (AST→text) |
| `body.variables[].var_code` / `role` | `variable_role_code` / `role_kind_code` | 🟠 translate (role→var_code) |
| `body.variables[].field_code` | — | 🔴 **UNRESOLVED@C** |
| `body.grain[]` | `grain_entity_id` + temporal gate | 🔴 partial: know "by fiscal_period"; `field_code` UNRESOLVED@C |
| `body.co_bindings[].canonical_contract` | — | 🔴 **UNRESOLVED@C** |
| `body.co_bindings[].fields_used` | — | 🔴 **UNRESOLVED@C** |
| `body.temporal_gate.field_code` | `temporal_anchor` BC | 🔴 **UNRESOLVED@C** |
| `body.temporal_gate.required_periods` / `completeness_threshold` | `temporal_gate_shape_code` + params | 🟠 translate (`period_aggregate`→{1, 0.8}) |
| `body.thresholds` | `threshold_json` (NULL) | ✅ omit (ARPI has none) |

✅ direct/constant · 🟡 minted/default · 🟠 derivable-with-translation · 🔴 **not derivable today**

## 3. Required runtime fields that CANNOT be derived from `mcf.*` today

All 🔴 rows collapse to **one root cause** — the absent BCF-concept → canonical-field resolution:

1. `body.co_bindings[].canonical_contract` — which `cc__…` carries ARPI's inputs.
2. `body.co_bindings[].fields_used` — the canonical field names.
3. `body.variables[].field_code` (I1, I2) — each variable's canonical source field.
4. `body.grain[].field_code` — the canonical period field to GROUP BY (grain is **mandatory** in the engine; metric-evaluation-engine.service.ts:181).
5. `body.temporal_gate.field_code` — the canonical posting-date field (from `temporal_anchor`).

Plus two **non-envelope** runtime requirements not in `mcf.*`:
6. `contract.metric_contract.metric_definition_id` — **NOT NULL FK** to `metric.metric_definition` (see §5).
7. Evaluation-eligibility artifacts the engine's discovery gates require but `mcf.*` does not produce: a `contract.chain_status` row (`chain_verdict='complete'`), `audit_status_code`, and an active `tenant.contract_binding`.

## 4. Fields derivable but needing translation logic

- **Formula AST → engine text.** `divide(sum(var:numerator_source), count_distinct(var:denominator_key))` → `"O1 = SUM(I1) / COUNT_DISTINCT(I2)"`. Mechanical: `divide`→`/`, `sum`→`SUM()`, `count_distinct`→`COUNT_DISTINCT()` (both in the engine's `AGG_FUNCTIONS`), `variable_ref.role`→`var_code`. *(Note: the operands' `field_code` is still 🔴 — the text shape translates, the bindings do not.)*
- **Variable skeleton.** `variable_role_code`/`role_kind_code` + representation/unit/data-type snapshots → `body.variables[]` roles + var_codes + (eventually) types.
- **Temporal gate.** `temporal_gate_shape_code='period_aggregate'` + `{period_type:'fiscal_period'}` → `body.temporal_gate {required_periods, completeness_threshold}` and a `fiscal_period` grain intent.
- **Unit.** `unit_code_snapshot='USD'` → `body.unit='currency'`.
- **Header identity + governance.** name/display/description/state → `header`.
- **Constants/mint/default.** `$contract`, `version`, `category`, `contract_id` (mint), `direction_code` (seed/default).

## 5. The `metric_definition_id` NOT NULL FK problem

Constraint: `fk_metric_contract__metric_definition` — `contract.metric_contract.metric_definition_id` is **NOT NULL** and FK→`metric.metric_definition`. ARPI has no MCF-side `metric_definition_id`; it does have an ancestor seed in `metric.metric_definition` (1 row matching `revenue_per_invoice`), but binding to legacy contradicts the clean-slate intent.

| Option | What it means | Assessment |
|---|---|---|
| **(a) Keep a clean `metric.metric_definition` stub** | Mint a minimal definition row per MCF metric, point the FK at it | Re-introduces the legacy table as a live dependency MCF must keep writing → **re-entangles legacy** (against D426 anti-contamination + D428 clean-slate). Reject. |
| **(b) Relax/drop the FK (and make column nullable)** | Drop `fk_metric_contract__metric_definition`; allow `metric_definition_id` NULL | Cleanest under D428 (legacy is being retired). Schema change under DBCP; must confirm no other code joins on it as NOT NULL. **Preferred** as part of clean-slate. |
| **(c) Different source pointer** | Replace the FK target with an MCF pointer (e.g. `mcf_metric_contract_version_uid` provenance column) | Most "correct" long-term (records true origin), but a larger schema change + write-path change. Defer to the generalize step, not the ARPI proof. |
| **(d) Defer to DBCP** | Decide at write-DBCP time | The decision itself is (b) vs (c); deferring the *choice* is fine, deferring the *analysis* is not — this section is the analysis. |

**Recommendation: (b) for the ARPI proof** (drop the NOT-NULL FK as a clean-slate step), with **(c)** as the durable shape during generalize. Either is a schema change requiring its own approved DBCP — **out of scope here.**

## 6. Is ARPI materialization feasible without changing the engine?

**The engine needs no change — but that is not the binding constraint.**

- **Evaluator:** unchanged and capable. It reads `contract.metric_contract_version.contract_json` origin-agnostically (verified: `MetricEvaluationEngine.evaluate(payloads, envelope)`, no `mcf.*` references in the runtime path). If a *valid, fully-resolved* `contract_json` existed, ARPI would evaluate.
- **Blocker is upstream of the engine:** the synthesizer cannot produce a *resolved* `contract_json` because the **BCF-concept→canonical-field resolution does not exist** (proven by absence in §Evidence). This is a missing **binding layer (Foundation repair-location C)**, fully consistent with — not a defect of — the MCF design (MCF correctly binds metric variables to *meaning* (BCF concepts), per the Foundation rule "Metric Contracts declare semantic inputs, not column names"; the canonical resolution is a separate, deferred layer).

**Verdict:**
- **Visibility-grade ARPI materialization** (Bar 1) — **feasible today**, no engine change, no resolution needed (the derivable fields carry the meaning a catalog/read surface shows).
- **Evaluation-grade ARPI materialization** (Bar 2) — **NOT feasible today**, regardless of the engine, until the BCF-concept→canonical-field resolution is established for ARPI's 3 concepts.

## 7. Minimum DBCP scope (if pursued) — staged, ARPI-only

The options memo's "synthesizer-first" step is necessary but **not sufficient**: it surfaced a deeper gap. The minimum path is now:

1. **(read-only, do first) BCF↔canonical resolution probe for ARPI's 3 concepts.** Confirm whether a canonical contract carries the invoice posted-amount / document-number / posting-date, and whether *any* path (naming, representation-term, a to-be-built binding) can map BC `a42d3fc0`/`095afe86`/`d05f24b3` → (`canonical_contract`, `field_code`). **If this fails, B-evaluation is blocked at the binding layer and that — not the synthesizer — is the next gate.** *(This is the true blocker; sequence it before any writer work.)*
2. **Binding-layer DBCP** (only if step 1 shows no existing path): design the BCF-concept→canonical-field binding (repair-location C) — a new mapping that records, per MCF variable binding, its canonical contract + field. Schema + service.
3. **Synthesizer** `synthesizeContractJson(mcvUid)` (read-only proof first: emit envelope, diff against a known-good evaluated envelope, write nothing).
4. **Writer DBCP**: write `contract.metric_contract(_version)` for ARPI; resolve the FK via §5(b); seed `contract.chain_status` + `audit_status_code`.
5. **One ARPI end-to-end proof**: bind to a tenant, test-bench evaluate, assert exactly one `fact.ms_*` row.
6. Legacy wipe stays a separate, later DBCP. D428 §9 guardrail holds throughout.

**The reordering is the key output of this proof:** the first real gate is **the BCF↔canonical binding layer (step 1/2)**, not the synthesizer. The synthesizer is mechanical once resolution exists.

## Two bars (kept separate)

| Bar | ARPI today | Why |
|---|---|---|
| **Publication visibility** | **Achievable now** | name/display/description/formula-AST/governance/temporal-gate/variable-roles all present in `mcf.*` → a read surface (or a visibility-only `contract_json`) can show *what ARPI means*. |
| **Evaluation readiness** | **Blocked** | `co_bindings`/`field_code`/`grain` unresolved → engine cannot bind COs to formula variables → no facts. |

## Scope guard

Read-only. No `synthesizeContractJson` implemented. No `contract.*` row written. No schema change, no materialization, no legacy cleanup, no panel run. D428 §9 guardrail intact. This proof recommends the *next read-only step* (BCF↔canonical resolution probe), not a write.
