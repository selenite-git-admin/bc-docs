---
title: "MCF Materialization-Boundary — Options Memo (A1 / A2 / B)"
description: Read-only options memo for the one open MCF gate — how an MCF-published metric becomes visible to the runtime engine through contract.metric_contract* while keeping D428's "single clean published store" rule. Separates publication-visibility from evaluation-readiness, compares A1 (read-APIs only) / A2 (shadow read-model) / B (materialize into contract.metric_contract*), and recommends one. Analysis only — authorizes no code, schema, DB write, or panel.
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: metric-store
focus: materialization-boundary
---

# MCF Materialization-Boundary — Options Memo (A1 / A2 / B)

> **What this is.** A read-only decision memo for the single open MCF gate. It is **not** authority (authority = DEC-c3e57f/D422 + DEC-61f7c8/D428 + the build plan) and it **authorizes no implementation** — no code, no schema, no DB write, no panel. It ends in one recommendation; the chosen path still requires its own approved DBCP before any change. Per the D428 §Decision-9 guardrail, **no materialization into `contract.*` and no legacy wipe may occur until an implementing DBCP is separately approved** — this memo does not lift that guardrail.

## The one question

> **How should an MCF-published metric become visible to the runtime engine through `contract.metric_contract*`, while keeping D428's "single clean published store" rule?**

Everything below hangs off that. Not BCF, not the seed reservoir, not helper hardening.

## Two bars — kept strictly separate

A metric can clear one of these and fail the other. The memo evaluates every option against **both**.

| Bar | Definition | The concrete test |
|---|---|---|
| **Bar 1 — Publication visibility** | Can runtime/admin **discover** the governed metric contract? | A catalog/read surface returns the governed MC (name, version, governance state, formula intent). |
| **Bar 2 — Evaluation readiness** | Can the engine **compute it into facts**? | The evaluator loads the contract and writes `progression.metric_evaluation` + a `fact.ms_*` row. |

**Both bars fail today** — proven by ARPI (see Ground Truth §3).

## Ground truth (live, 2026-06-07)

### 1. The two stores are shaped differently — this is the crux

| | Runtime store (`contract.*`) | MCF store (`mcf.*`) |
|---|---|---|
| Header | `contract.metric_contract` (19 cols) — **`metric_definition_id` NOT NULL** | `mcf.metric_contract` (17 cols) — grain, temporal gate, identity hashes |
| Version body | `contract.metric_contract_version` — **`contract_json` jsonb NOT NULL** (the *denormalized evaluable envelope*) | `mcf.metric_contract_version` — **`formula_ast_canonical_json` jsonb NOT NULL** (no `contract_json`) |
| Bindings / filters / computed dims | folded inside `contract_json` | **normalized into sibling tables**: `mcf.metric_variable_binding`, `mcf.metric_filter_clause`, `mcf.metric_computed_dimension_ref` |
| Eligibility metadata | `audit_status_code`, joined `contract.chain_status`, `tenant.contract_binding` | `governance_state_code` (draft→review→approved→active), `certification_record`, PE-MC result |

The runtime engine consumes **one denormalized `contract_json` envelope**. MCF stores the same meaning **normalized across five tables**. There is no `contract_json` in the MCF store. **Bridging requires a synthesis function** that assembles the runtime envelope from the MCF normalized shape — that function **does not exist today** (see §4).

### 2. The runtime evaluation path reads `contract.*` exclusively (verified)

- **Discovery / eligibility:** `metric-catalog-reader.repository.ts` `listActiveMcs()` joins `contract.metric_contract` + `contract.metric_contract_version` + `contract.chain_status`; readiness gating (`metric-readiness.service.ts`) requires `chain_status.chain_verdict = 'complete'` AND `audit_status_code != 'fail'` AND an active `tenant.contract_binding`.
- **Load:** `boundary/metric.service.ts` `loadEnvelope()` reads `contract.metric_contract_version.contract_json`.
- **Evaluate:** `boundary/metric-evaluation-engine.service.ts` `MetricEvaluationEngine.evaluate(payloads, envelope)` — pure/deterministic; parses `envelope.grain | inputBindings | formula | computation | qualityRules | evaluationPeriod`.
- **Persist:** `progression.metric_evaluation` (always) + `fact.ms_*` (only when `valid`).
- **Dispatch:** operator/test-bench triggered (`POST /api/admin/test-bench/evaluate-mc-for-tenant`). No standing scheduler auto-evaluates; evaluation is dispatch-driven for legacy MCs too.
- **MCF reads at runtime: NONE.** No evaluation/runtime code references `mcf.*`. (Corrects a prior claim that M12.5 "produces the `contract.metric_contract_version` row" — it does not; see §4.)

### 3. ARPI — the live proof both bars fail

| Store | `average_revenue_per_invoice` |
|---|---|
| `mcf.metric_contract_version` | **`governance_state_code = 'active'`, `is_current = true`** (M14-published in MCF) |
| `contract.metric_contract` | **0 rows** → invisible to runtime/admin catalog (Bar 1 fails) |
| `metric.metric_definition` | 1 ancestor seed row (its pre-MCF origin) |
| `fact.ms_*` | 0 facts → never evaluated (Bar 2 fails) |

ARPI is "active" inside MCF yet **undiscoverable and uncomputable by the runtime**. This is the entire problem in one row.

### 4. What exists vs. what's missing

- **Exists:** M12.5 `MetricAuthoringMaterializationService` writes the MCF substrate (`mcf.metric_contract` + `mcf.metric_contract_version` with `formula_ast_canonical_json` + bindings + filters + computed dims + cert). M14 flips `mcf.metric_contract_version.governance_state_code → 'active'`. A `contract_json` builder exists **only on the legacy authoring path** (`POST /metric-catalog/definitions`).
- **Missing:** any function that reads the **MCF normalized shape** and emits a runtime **`contract_json`**; any writer into `contract.metric_contract(_version)` from MCF; resolution of the `metric_definition_id` NOT NULL FK for an MCF metric; a `contract.chain_status` row for a materialized MC.

### 5. Live counts (corroborated by re-entry index §3)

- `mcf.metric_contract` active = **2**: ARPI (`active`), `billing_volume` (`approved`). *(The re-entry index "5" is stale; 3 prior specimens archived/superseded.)*
- `contract.metric_contract` = **2 active / 780 total** (778 archived) — legacy corpus already archived to near-zero per D422/D428 direction.
- `contract.metric_contract_version` = 1022; `metric.metric_definition` = 1241.

**Implication:** the runtime store is *already* effectively clean-slated (2 active). Materializing MCF metrics into it does not fight a contaminated store.

---

## Options

Each option states: what changes · what stays untouched · D428 alignment · runtime-engine changes · legacy wipe now/later · risks for future engineers · minimum next DBCP.

### A1 — Expose `mcf.*` via read APIs only; runtime bridge deferred

- **What changes:** add `McfReadService` list/detail endpoints over `mcf.metric_contract*` (active); a bc-admin page reads them.
- **What stays untouched:** `contract.*`, the engine, `metric.*`, the FK, all facts. Pure read-model over existing MCF tables.
- **D428 alignment:** **Partial / sidesteps.** D428 §4 makes `contract.metric_contract*` the single *published* store; A1 leaves published truth in `mcf.*` and never reaches `contract.*`. It does not answer the question (the question requires visibility *through `contract.metric_contract*`*).
- **Runtime-engine changes:** none.
- **Legacy wipe:** not required, not enabled.
- **Bars:** Bar 1 ✅ (admin can discover) · **Bar 2 ❌** (engine still can't evaluate; ARPI stays factless).
- **Risks for future engineers:** entrenches a permanent dual-surface ("which store is truth?"); the "active-but-non-evaluable" ARPI trap persists indefinitely; a later engineer still has to build the real bridge, now atop a shipped read API that implies completeness it doesn't have.
- **Minimum next DBCP:** none for DB (read-only endpoints + UI). No schema, no writes.

### A2 — Project `mcf.*` into a NEW shadow read-model

- **What changes:** new shadow tables (or materialized views) + an idempotent projection function `mcf → shadow`; admin (and possibly runtime) read the shadow.
- **What stays untouched:** live `contract.*`, `metric.*`, the engine (if the shadow is read-only and not engine-wired).
- **D428 alignment:** **Conflicts — reverses the decided direction.** A2 *is* the "`mcf → NEW shadow` projection" that D426 proposed and **D428 explicitly amended away from** in favour of "`contract.metric_contract*` = single clean published store." Choosing A2 re-opens a superseded approach.
- **Runtime-engine changes:** none if pure read-model — but then it **cannot evaluate** (the unchanged engine reads `contract.metric_contract*`, not the shadow). If the shadow is made engine-readable, the engine must change (violating D428 §7) or the shadow must *be* `contract.*` (which collapses into B).
- **Legacy wipe:** not required now.
- **Bars:** Bar 1 ✅ · **Bar 2 ❌** (same wall as A1, plus a third surface to maintain).
- **Risks for future engineers:** builds the exact permanent translation bridge D428 sought to avoid; three metric-shaped surfaces (`metric.*`, `contract.*`, shadow, + `mcf.*`); projection drift becomes a standing correctness liability (cuts against Invariant I — meaning evaluated once).
- **Minimum next DBCP:** DDL for shadow tables/MV + a projection service + drift checks. Larger surface than A1, still no evaluation.

### B — Materialize MCF-published metrics into `contract.metric_contract*` as the single clean published store

- **What changes:** at M14 publish (or a post-publish step), a new **synthesizer** reads the MCF normalized shape (`formula_ast_canonical_json` + variable bindings + filters + computed dims + grain + temporal gate + thresholds) and emits a runtime **`contract_json`**, then writes `contract.metric_contract` + `contract.metric_contract_version`. Supporting: resolve `metric_definition_id` (drop/relax `fk_metric_contract__metric_definition`, or synthesize a definition row), seed a `contract.chain_status` row (`chain_verdict='complete'`) and `audit_status_code`.
- **What stays untouched:** **the evaluator itself** (`MetricEvaluationEngine`, `loadEnvelope`, progression + fact writers) — D428 §7 holds: once a valid `contract.metric_contract_version.contract_json` exists, evaluation is origin-agnostic. `mcf.*` remains the authoring substrate. `metric.metric_knowledge` preserved (D426 open question (b)).
- **D428 alignment:** **Aligns — this is D428's decided target architecture** (§Decision 4 + §7). "Engine unchanged" is honored *for the evaluator*; note the honest caveat below.
- **Runtime-engine changes:** **none to the evaluator** — but **new materialization/synthesis code is required**. D428's "engine unchanged" must not be misread as "free": the synthesizer + writer + FK/chain_status handling are net-new (this memo's most important correction).
- **Legacy wipe:** **not required for B to function** (B coexists with the already-archived legacy corpus). The wipe is a *later, separate* D428-sequence DBCP; B is what makes `contract.*` MCF-owned so the wipe becomes meaningful. The `metric_definition_id` FK must be resolved *before or with* any wipe of `metric.metric_definition`.
- **Bars:** **Bar 1 ✅** (admin already reads `contract.metric_contract` → ARPI appears once written) · **Bar 2 ✅ conditionally** (engine evaluates after: valid `contract_json`, `chain_status` complete, an active `tenant.contract_binding`, and resolvable canonical-object inputs).
- **Risks for future engineers:** the synthesizer is new critical-path code — `contract_json` correctness *is* metric meaning (Invariant I; Invariant VI — evidence emitted, not inferred); FK/clean-slate sequencing must be ordered carefully; must not re-entangle legacy `metric.*` as active design debt (D426's anti-contamination goal still binds).
- **Minimum next DBCP (single-metric, ARPI-only):**
  1. **Read-only synthesizer proof first** — build `synthesizeContractJson(mcvUid)` for ARPI, diff the emitted envelope against what `loadEnvelope`/the engine expects, **write nothing** (de-risks the mapping).
  2. Then a narrow write DBCP: writer into `contract.metric_contract(_version)` for ARPI; resolve `metric_definition_id` (preferred: drop the NOT-NULL FK as part of clean-slate, since legacy is being retired); seed `contract.chain_status`.
  3. One end-to-end proof: M14-active ARPI → materialize → test-bench evaluate → exactly one `fact.ms_*` row.
  4. Legacy wipe stays a separate, later DBCP. Guardrail (D428 §9) remains until each step is approved.

---

## Comparison at a glance

| Dimension | A1 read-APIs | A2 shadow | **B materialize → contract.*** |
|---|---|---|---|
| Bar 1 — visibility | ✅ (via `mcf.*`) | ✅ (via shadow) | ✅ (via `contract.*`) |
| Bar 2 — evaluation into facts | ❌ | ❌ | ✅ (conditional) |
| Answers the question ("through `contract.metric_contract*`") | ✗ | ✗ | ✔ |
| D428 alignment | partial / sidesteps | **reverses D428** | **is D428's target** |
| Evaluator code change | none | none (then can't eval) | **none to evaluator** (synthesizer is new) |
| New surfaces created | 0 (reads `mcf.*`) | +1 shadow | 0 (reuses `contract.*`) |
| Legacy wipe needed now | no | no | no (later, separate) |
| Standing correctness liability | dual-store | **triple-store + projection drift** | one store (synthesizer correctness) |

## Recommendation

**Adopt Option B**, executed as the **smallest possible first step (ARPI only), synthesizer-proof-first.**

Rationale: B is the **only** option that clears **both** bars and the **only** one that answers the question as posed (visibility *through* `contract.metric_contract*`). A1 and A2 satisfy Bar 1 but leave every MCF-"active" metric non-evaluable — perpetuating the exact ARPI trap this gate exists to close — and A2 additionally **reverses** the decided D428 direction by rebuilding the shadow-projection bridge D428 superseded. B is literally D428's target architecture, and the runtime store is already clean-slated (2 active), so B does not fight a contaminated surface.

The one caveat to carry forward, loudly: **B is not "free engine reuse."** The evaluator is untouched, but the **MCF→`contract_json` synthesizer**, the **writer**, and the **`metric_definition_id` FK / `chain_status` seeding** are net-new and are where the risk lives. Prove the synthesizer read-only on ARPI before writing a single row.

Sequence after this memo: (1) approve B as direction (annotate D426's superseded store-decisions to point at D428, per D428 §RELATIONSHIP follow-up); (2) read-only synthesizer-proof DBCP on ARPI; (3) narrow single-metric write DBCP; (4) generalize; (5) legacy wipe as its own DBCP. M15 supersession, M16–M20 console, D400/D401/D427 all remain separate and unblocked-by-this only after the boundary is settled.

## Scope guard

This memo is analysis. It authorizes **no** code, schema, DB write, or panel run, and does **not** lift the D428 §9 guardrail. The recommendation is a direction to be ratified, not an instruction to build.

## Evidence appendix

- **ADRs:** `docs/adrs/ADR-61f7c8.md` (D428, decided) §Decisions 4/7/9; `docs/adrs/ADR-3f093f.md` (D426, amended) three-store reality, schema asymmetry, M14-internal-only, knowledge-preservation open question.
- **Live DB (bc_platform_dev, 2026-06-07):** store shapes via `information_schema.columns`; `fk_metric_contract__metric_definition` via `pg_constraint`; ARPI cross-store presence; counts mcf=2 active, contract=2 active/780 total, mcv=1022, metric_definition=1241.
- **Runtime path (bc-core):** `src/registry/metric-catalog-reader.repository.ts` (`listActiveMcs`), `src/registry/metric-readiness.service.ts` (chain/audit gates), `src/boundary/metric.service.ts` (`loadEnvelope`), `src/boundary/metric-evaluation-engine.service.ts` (`evaluate`), `src/test-bench/admin-test-bench.controller.ts` (dispatch). No `mcf.*` references in the runtime path.
- **MCF write target:** `src/registry/mcf/metric-authoring-materialization.service.ts` writes `mcf.*` only; grep across `src/registry/mcf` finds no `INSERT INTO contract.metric_contract` / `metric.*` (only `contract.panel_output_record`/`framework_policy`, with tests asserting no contract-MC writes).
