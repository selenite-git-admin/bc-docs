---
title: MMS Layer 3 — Compatibility-Names Inventory (2026-06-23)
description: Read-only inventory of MMS / MCF legacy-coded compatibility names that must NOT be renamed directly — persisted DB values, idempotency / hash inputs, API wire-contract field names, telemetry enum keys, deployment-config env vars, and historical evidence. Maps each compatibility surface to its migration risk and recommended treatment. NO migration executed.
status: draft
authority: implementation-inventory
date: 2026-06-23
project: bc-docs-v3
domain: mms
subdomain: layer3-compatibility-names
focus: inventory
supersedes: []
governing_adr: DEC-54f221
---

# MMS Layer 3 — Compatibility-Names Inventory

## 0. Scope, Method, Non-Goals

**Governing ADR:** DEC-54f221 / D449 — three-layer model (Interpretation Surfaces / Implementation Names / **Compatibility Names**).

**Layer 3 definition.** Runtime-observable identifiers whose **values** carry legacy MMS / MCF tokens and whose external consumers (DB substrate, replay machinery, frontends, telemetry dashboards, deployment automation) depend on stable values. Layer 3 is the *outermost* shell: any rename here is a wire-contract migration, not a refactor.

**Method.** Three parallel `Explore` subagents executed:
- bc-core deep sweep (DDL, Drizzle, services, scripts, indices)
- bc-admin + bc-portal frontend sweep (TS interfaces, API consumers, UI bindings)
- bc-ai + env-config sweep (Python wire payloads, `.env*` files, `ecosystem.*`)

Synthesized below.

**Hard non-goals.** No code edits. No doc edits. No DB writes. No migrations. No env-var changes. No prompt edits. No PR.

---

## 1. Summary by Classification

| # | Classification | Items | Cross-repo coupling | Migration risk |
|---:|---|---:|---|---|
| 1 | **PERSISTED_DB_VALUE** | 18 | DDL ⇄ Drizzle ⇄ service ⇄ historical rows | CRITICAL — schema lock; persisted rows are immutable evidence (Invariant III) |
| 2 | **IDEMPOTENCY_OR_HASH_INPUT** | 6 | service constants ⇄ DB-stored idempotency keys / hash anchors | CRITICAL — replay-breaking; deterministic re-execution required |
| 3 | **API_WIRE_CONTRACT** | 4 properties / 13 use sites | bc-core JSON ⇄ bc-admin TS interface ⇄ UI bindings | HIGH — silent runtime break if renamed independently |
| 4 | **TELEMETRY_OR_DASHBOARD_KEY** | 5 | DB enums + dashboard queries | MEDIUM-HIGH — append-only enums; query / aggregate breakage on rename |
| 5 | **DEPLOYMENT_CONFIG** | 1 documented env var + 10 documented-not-set env vars | runbook + operator environments | MEDIUM — requires transition window / dual-name read |
| 6 | **INTERNAL_IDENTIFIER_ALREADY_LAYER2** | 0 | n/a — all such items were closed in Layer 2 batches | n/a |
| 7 | **HISTORICAL_EVIDENCE** | 45+ artifacts in `scripts/audit-output/` + dormant phase scripts | none (frozen) | NONE — preserve forever per Foundation III |
| 8 | **SAFE_DOC_ONLY** | extensive (already at `(legacy: MN)` dual-label form) | none (operator-visible docs) | NONE — Layer 1 surface already complete |

**Headline finding.** The persisted compatibility surface for MMS / MCF is **wider than feared but mostly append-only**. Of the 28 truly load-bearing items (rows 1–5), nearly all are protected by Foundation Invariant III (immutable evidence): they cannot legally be migrated in place. Migration paths exist for some (additive aliases, version bumps, dual-write) but ALL are non-trivial and require operator-runbook coordination. **No Layer 3 migration is recommended at this time.**

---

## 2. PERSISTED_DB_VALUE — Schema-lock surfaces

### 2.1 `mcf.metric_publication_eligibility_result.pe_check_code` — CHECK constraint enum

| Layer | Location | Tokens |
|---|---|---|
| DDL | `bc-core/docker/redesign/06-mcf-lifecycle-certification.sql:50` | `PE-MC-1` … `PE-MC-10` (initial vocabulary) |
| DDL amendment | `bc-core/docker/redesign/18-mcf-pe-mc-11-vocabulary.sql:36` | adds `PE-MC-11` (G3 Source-Chain Resolvability Gate) |
| DDL amendment | `bc-core/docker/redesign/19-mcf-pe-mc-12-vocabulary.sql:40` | adds `PE-MC-12` (G4 Source-Vocabulary Discipline Gate) |
| Drizzle | `bc-core/src/database/schema/mcf/metric-publication-eligibility-result.ts:70` | mirror CHECK |
| TS runtime | `bc-core/src/registry/mcf/metric-publication-eligibility-evaluator.service.ts:163` | `PE_MC_CODES = ['PE-MC-1', …, 'PE-MC-12']` |
| TS runtime | `bc-core/src/registry/mcf/mcf-publication-activation.controller.ts:58–59` | `REQUIRED_PASS_CODES = ['PE-MC-1', …, 'PE-MC-11']` |
| TS runtime | `bc-core/src/registry/mcf/mcf-publication-activation.controller.ts:271, 279, 282` | `'PE-MC-8'` literal comparisons (special-case verdict) |

**What depends on it:** every persisted PE-eligibility row, all activation-gate logic, the partial unique index `idx_mcf_mper_mcv_check_eval_pkg`, controller spec assertions, runbook procedures, operator dashboards.

**Migration treatment:** **PRESERVE FOREVER.** Adding a new code (PE-MC-13+) is permitted via the established amendment-DDL pattern (sync DDL + Drizzle + TS array + spec assertions). Removing or renaming is structurally forbidden — historical rows would violate the post-rename CHECK constraint.

**Risk:** CRITICAL.

### 2.2 `mcf.chain_audit_evidence.audit_mode_code` — CHECK constraint enum

| Layer | Location | Tokens |
|---|---|---|
| DDL | `bc-core/docker/redesign/migrations/d445-cas-v0-evidence-substrate.sql:13–15` | `pre_m12_audit`, `pre_m13_audit`, `pre_m14_audit`, `pre_runtime_release_audit`, `regression_audit` |
| TS runtime | `bc-core/src/registry/mcf/chain-audit/chain-audit.types.ts:20` | `CAS_V0_MODES = ['pre_m13_audit']` (current single-mode v0) |
| Swagger | `bc-core/src/registry/mcf/chain-audit/chain-audit.controller.ts:46` | `'v0 scope: pre_m13_audit on MCF MCV'` (operator-facing summary text mirrors the persisted value — DEFER per L2d-3 decision) |

**What depends on it:** chain-audit DTO validators, audit-evidence rows, audit-report queries.

**Migration treatment:** **PRESERVE.** Append new modes if needed; never rename existing ones.

**Risk:** MEDIUM (smaller blast radius than PE-MC since the v0 set is narrow, but still wire-contract).

### 2.3 `ai_telemetry.ai_run_ledger.run_kind` — CHECK constraint enum

| Layer | Location | Tokens |
|---|---|---|
| DDL | `bc-core/docker/redesign/migrations/ai-telemetry-ledger-v0-substrate.sql:109–118` | `'mcf_m12_panel'`, `'mcf_m14_activation_eval'` (plus 6 non-MMS values) |
| Test assertion (schema-lock) | `bc-core/src/database/schema/ai-telemetry/ai-ledger.spec.ts:54` | asserts `'mcf_m14_activation_eval'` literal |

**What depends on it:** all ai_telemetry queries grouping/filtering by `run_kind`; operator dashboards segmenting AI cost by stage; schema-lock test that pins the enum.

**Migration treatment:** **PRESERVE.** Append-only enum; never rename.

**Risk:** MEDIUM-HIGH — any query like `WHERE run_kind = 'mcf_m12_panel'` breaks on rename.

---

## 3. IDEMPOTENCY_OR_HASH_INPUT — Replay-locked values

### 3.1 Idempotency key prefixes (3)

| Constant identifier (semantic, Layer 2 closed) | Persisted prefix VALUE | File |
|---|---|---|
| `METRIC_DRAFTING_IDEMPOTENCY_KEY_PREFIX` | `'mcf-m12-5/'` | `metric-authoring-materialization.service.ts:236` |
| `PUBLICATION_REVIEW_IDEMPOTENCY_KEY_PREFIX` | `'mcf-m13-pe-mc/'` | `metric-publication-eligibility-evaluator.service.ts:155` |
| (composed 4-segment key) | `'mcf-m14-activate/' + mcvUid + '/' + packageSignatureHash + '/' + m13EvaluationSignatureHash` | `mcf-publication-activation.controller.ts:198` |

**What depends on them:** the M4 cert-writer cache. A second call with the same idempotency key returns the cached cert UID instead of writing a new row. Change the prefix → the cache lookup misses → a new cert row is written that duplicates an existing one (Foundation Invariant III violation).

**Migration treatment:** **PRESERVE FOREVER.** A new materialization/publication/activation logic line introduces a NEW prefix (e.g., `mcf-metric-drafting-v2/`); the old prefix's cache stays live forever to keep historical replays deterministic.

**Risk:** CRITICAL.

### 3.2 Version-stamped hash inputs (3)

| Constant identifier | Persisted value | Role |
|---|---|---|
| `METRIC_DRAFTING_HASH_ALGORITHM_VERSION` and `PUBLICATION_REVIEW_HASH_ALGORITHM_VERSION` (both refer to same value) | `'mcf-hash-v1'` | Foundation D-M9-A1 forever-lock; stamped on every materialized fixture row's `hash_algorithm_version`. Golden-anchor identity for the metric.* hash recipe. |
| `PUBLICATION_REVIEW_EVALUATOR_VERSION` | `'mcf-m13-v6'` | Stamped on `metric_publication_eligibility_result.verifier_version` and `.evaluator_version`. Bumped by semantic policy change (`mcf-m13-v3 → v4 → v6` history). |
| `METRIC_ACTIVATION_VERIFIER_VERSION` | `'mcf-m14-v2'` | Stamped on Metric Activation PE rows; partial unique index `idx_mcf_mper_mcv_check_eval_pkg` keys on this value to keep M14 rows distinct from M13 rows on the same `(mcv_uid, pe_check_code)`. |
| `M10_VERIFIER_ALGORITHM_VERSION` | `'mcf-verifier-v1'` | Preserve list (M10 is Foundation anchor, not legacy). |

**What depends on them:**
- `mcf-hash-v1`: every persisted hash in the system was computed under this recipe. Renaming triggers golden-anchor break + index rebuild + Foundation Invariant VI violation.
- `mcf-m13-v6` / `mcf-m14-v2`: the partial unique index logic; external consumers querying by `verifier_version`; audit chains.

**Migration treatment:**
- `mcf-hash-v1`: **PRESERVE FOREVER**. Hash recipe is locked by Foundation D-M9-A1.
- `mcf-m13-v6` / `mcf-m14-v2`: BUMP on semantic change per D-M13-9 / D-M14-IS-6 policy. The current values stay on existing rows; new evaluations stamp the new version.

**Risk:** CRITICAL (mcf-hash-v1) → HIGH (verifier/evaluator versions, mitigated by bump-policy).

---

## 4. API_WIRE_CONTRACT — JSON field names that mirror wire shape

### 4.1 `m14_activated` (the canonical Layer 3 frontend coupling)

| Side | File:Line | Surface |
|---|---|---|
| bc-core — emit | `mcf-read.service.ts:120` (JSDoc), `:137` (`SELECT … AS m14_activated`), `:162` (column selection), `:224` (object literal) | Drizzle query AS-alias → response JSON field |
| bc-admin — TS interface | `src/api/mcf-catalog.ts:27` (`McfMetricContract.m14_activated: boolean`), `:132` (`McfMetricContractDetail.m14_activated: boolean`) | Wire-shape contract |
| bc-admin — UI binding | `src/pages/MetricCatalogPage.tsx:128, 130` | DataTable column key + render conditional |
| bc-admin — UI binding | `src/pages/MetricDetailPage.tsx:187` | JSX boolean conditional |
| bc-admin — UI binding | `src/pages/MetricLandscapePage.tsx:150, 476, 478` | filter logic + DataTable column key + render conditional |

**Total: 1 field name, 8 active bc-admin use sites + 4 bc-core emission sites = 12 lines coupled.**

**What depends on it:** bc-admin TypeScript expects `m14_activated` literally; the field flows from the SQL `AS` alias through the JSON response into UI rendering. bc-portal does NOT reference it (UI shows zero matches; only false-positive matches in node_modules `DOMMatrix.m11` etc.).

**Migration treatment:** **PRESERVE in current shape. Migration option (deferred):**
1. bc-core adds new field `activation_evidence_exists` (or similar semantic name) alongside `m14_activated` in the API response.
2. bc-admin reads both for one release; new code path uses the semantic name.
3. Deprecation header on legacy field.
4. After 2+ releases, drop `m14_activated`.

**Risk:** HIGH (silent runtime break if renamed independently in either repo).

### 4.2 Certification-record evidence JSON keys

| File:Line | Token |
|---|---|
| `mcf-publication-activation.controller.ts:209–213` | `gateResultsJson` keys: `m13_evaluator_version`, `m13_pe_check_codes_observed`, `m13_package_signature_hash` |

**Persisted in:** `mcf.certification_record.gate_results_json` (JSONB column) — certificate evidence under Foundation Invariant IV (immutable evidence).

**What depends on them:** cert audit trail readers, external compliance queries on `gate_results_json`, any cert-introspection tooling. The certificate rows themselves are immutable, so even renaming the JSON keys going forward leaves the legacy keys on existing rows.

**Migration treatment:** **PRESERVE in current shape.** If rename desired: add new keys alongside, keep old keys on the write path for 2+ release cycles, then deprecate.

**Risk:** MEDIUM.

### 4.3 bc-ai → bc-core wire payload `checklist_answers` keys

| File:Line | Token |
|---|---|
| `bc-ai/app/pipeline/registry_authoring_panel.py:103–105` | `_CHECKLIST_ITEM_KEYS = ("M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10")` |

**Important distinction.** These `M1`…`M10` keys are NOT MMS-stage codes. They are **BCF Vocabulary Admission Checklist v1** items per the F4-v2 framework — a separate identifier family (Business Concept Framework, not Metric Management System). Semantically unrelated to MMS M11/M12/M12.5/M13/M14/M15 despite sharing letter-number shape.

**What depends on them:** bc-core's `panel_output_record` DTO validator enforces presence of exactly these 10 keys in `verdictPayloadJson.checklist_answers`. Renaming any key breaks panel-output emission with HTTP 4xx.

**Migration treatment:** **PRESERVE.** Out of MMS Layer 3 scope strictly speaking (different framework); included here for cross-reference because the keys would surface in any token-pattern search.

**Risk:** HIGH (within BCF surface) — but **not within MMS Layer 3 governance**.

---

## 5. TELEMETRY_OR_DASHBOARD_KEY — Append-only enum values

Covered above in §2.2 (audit_mode_code) and §2.3 (ai_run_ledger.run_kind). All append-only enum values on persisted CHECK constraints. Same PRESERVE treatment.

Additional telemetry-layer items in bc-ai (per agent 3 report):
- `bc-ai/app/pipeline/bcf_telemetry.py:175` — `BcfPanelCallRecord.role` enum `'maker' | 'checker' | 'moderator' | 'judge'` — these are **semantic** role names (not legacy stage codes). No legacy token to migrate.
- HTTP endpoints `/api/bcf/panel-output-records`, `/api/ai-telemetry/bcf-panel-run/from-summary` — already semantic. No stage code.

**No additional MMS-tagged telemetry keys outside the run_kind / audit_mode_code enums.**

---

## 6. DEPLOYMENT_CONFIG — Env-var family

### 6.1 Actual `.env` file inventory (confirmed by sweep)

| File | MMS-tagged env vars present? |
|---|---|
| `bc-core/.env` | **None.** `MCF_M12_*` not set. |
| `bc-core/.env.example` | `BCCORE_MCF_LEGACY_SUNSET_DATE` documented at L43–44, commented (unset). No `MCF_M12_*`. |
| `bc-ai/.env` | **None.** |
| `bc-ai/.env.template` | **None.** |
| `bc-admin/.env*` | **None.** |
| `bc-portal/.env*` | **None.** |
| `ecosystem.config.cjs` (root) | **None.** |

### 6.2 Documented but never set (10 env vars)

The following env vars are referenced by `model-defaults.ts` reader functions and JSDoc, but **none is set on disk in any actual `.env` file**:

- `MCF_M12_MAKER_MODEL`, `MCF_M12_CHECKER_MODEL`, `MCF_M12_JUDGE_MODEL`, `MCF_M12_MODERATOR_MODEL`
- `MCF_M12_MAKER_MAX_OUTPUT_TOKENS`, `MCF_M12_CHECKER_MAX_OUTPUT_TOKENS`, `MCF_M12_MODERATOR_MAX_OUTPUT_TOKENS`
- `MCF_M12_VENDOR_TIMEOUT_MS`, `MCF_M12_PER_ROLE_TOKEN_BUDGET`, `MCF_M12_USE_JUDGE_ROLE`

Each has a code default that the runtime falls back to when the env var is unset. Per `model-defaults.ts:88–97`, the TS identifier names (`MAKER_MODEL_ENV_VAR`, etc.) are **already semantic**; the legacy `MCF_M12_*` strings live only as RHS string values that the runtime reads from `process.env`.

**What depends on them:** any operator who would set these env vars in production (AWS Parameter Store, deployment automation, runbooks) — but no such operator currently exists per the disk sweep. The runbook chapters in `bc-docs-v3/docs/implementation/` document the env-var names; if/when operators procure them, the documented names are what they would set.

**Migration treatment options:**
- **Option A (status quo):** Leave the env-var key strings as `MCF_M12_*`. Since they aren't set anywhere on disk, the migration cost is purely documentation (runbook chapter updates).
- **Option B (semantic rename + fallback chain):** Rename the documented env-var keys to `MCF_METRIC_DRAFT_REVIEW_*` and ship a fallback-chain reader that accepts both names during a transition window. Updates: code (model-defaults.ts) + `.env.example` + 7 runbook chapters in bc-docs-v3. Operator notification.

**Risk:** LOW-MEDIUM (nothing currently breaks; cosmetic migration unless operators have set the env vars locally).

### 6.3 The only documented env var actively read with a legacy stem

| Env var | Defined in | Read by | Status |
|---|---|---|---|
| `BCCORE_MCF_LEGACY_SUNSET_DATE` | `.env.example:43–44` (commented) | `bc-core/src/registry/metric-definition.controller.ts:32` (RFC 9745 Sunset header for legacy metric endpoints) | Documented; unset on disk; failsafe behavior (header omitted) if unset |

**Migration treatment:** **PRESERVE.** This env-var name embeds `MCF_LEGACY_SUNSET_DATE` semantically — it documents that the legacy metric endpoints are being sunset. Renaming would obscure the deprecation signal. The name is self-explanatory and not subject to MMS stage-code drift.

**Risk:** NONE.

---

## 7. HISTORICAL_EVIDENCE — Frozen artifacts

Per Sub-batch A operator decision (in Layer 2b M12-class rename closeout):

- `bc-core/scripts/bcf-phase-a3-import-lockfile.mjs` + 3 invoking phase-A3 orchestration scripts — DORMANT (A3 superseded by A4/A5 closeouts in `bc-docs-v3/docs/implementation/`). 38+ regex assertions hardcode legacy identifier names.
- `bc-core/scripts/mcf-m{11,12,14}-*.mjs` — one-shot operator scripts with timestamped evidence. 6+ files.
- `bc-core/scripts/audit-output/*.md` and `*.jsonl` — historical evidence emitted by those scripts. ~50+ files reference MMS / MCF legacy tokens.

**Migration treatment:** **PRESERVE FOREVER** per Foundation Invariant III.

**Risk:** NONE (frozen).

---

## 8. SAFE_DOC_ONLY — Already at dual-label form

Layer 1 work (Tracks 1 + 2 + Cluster A/B residual) already established `(legacy: MN)` dual-label form in:
- All top-of-file controller JSDoc (`McfMaterializationController — Metric Drafting (legacy: M12.5) endpoint`)
- All operator-facing chapter prose in `bc-docs-v3/docs/`
- All inline code comments referencing stages

The L2d-3 batch (this turn, just-completed) added semantic wording to all `@ApiOperation` summary/description strings.

**Migration treatment:** No further action needed at the documentation tier.

**Risk:** NONE.

---

## 9. Cross-repo coupling map

| From | To | Surface | Coupling strength |
|---|---|---|---|
| bc-core DDL | bc-core Drizzle | `pe_check_code` CHECK + Drizzle CHECK literal | TIGHT — must move together |
| bc-core DDL | bc-core TS runtime | `PE_MC_CODES` array vs. CHECK | TIGHT — schema-lock test pins both |
| bc-core service constants | bc-core DB rows | idempotency prefix VALUES | TIGHT (replay) |
| bc-core service constants | bc-core DB rows | hash/evaluator/verifier version VALUES | TIGHT (Foundation IV/VI) |
| bc-core API JSON | bc-admin TS interface | `m14_activated` field name | TIGHT (silent break if mismatched) |
| bc-core DTO validator | bc-ai wire payload | `checklist_answers` keys (BCF, not MMS) | TIGHT (HTTP 4xx if mismatched) |
| bc-core env reader code defaults | operator environments | `MCF_M12_*` env-var key strings | LOOSE (no current operator dependency confirmed) |
| bc-core run_kind / audit_mode_code enum | dashboards / operator queries | telemetry enum values | LOOSE-MEDIUM (depends on dashboard ownership) |

**Tight couplings (5 categories) require coordinated change across both endpoints. Loose couplings (2 categories) can move semi-independently with a transition window.**

---

## 10. Recommendation — Defer all Layer 3 migration

**Recommend: DEFER all Layer 3 migration until after product/substrate work resumes.**

Rationale:
1. **Foundation Invariant III enforces preservation of persisted evidence.** The PE-MC-* check codes, idempotency prefixes, hash algorithm version, verifier/evaluator versions, telemetry enum values, and audit_mode_code values are all already protected by Foundation III. Renaming requires a migration that the Foundation explicitly forbids in place; the only allowed pattern is **additive** (new value alongside old, never replacement).
2. **No active break.** The current state is functionally correct. All Layer 1 / Layer 2 work has eliminated the operator-visible and engineer-visible stage-code drift. The remaining legacy tokens live in:
   - persisted DB substrate (immutable)
   - replay-locked service constants (immutable)
   - one wire-contract field (`m14_activated`) with stable bc-core ⇄ bc-admin coupling
   - documented env vars that no operator has set
   - historical audit evidence
   None of these is causing operator confusion or developer ambiguity at the moment.
3. **Migration cost is high and value is low.** A full Layer 3 migration touches ~28 load-bearing surfaces, requires coordinated bc-core + bc-admin (and possibly bc-ai) deployment, demands a deprecation window for the wire-contract field, and produces no functional change — only naming change at the value tier. The risk/reward is poor while product work is paused.
4. **Two specific items can be revisited tactically without a full migration:**
   - The `m14_activated` JSON field — IF a future bc-core API revision is undertaken, the operator can elect to add `activation_evidence_exists` alongside as a coordinated bc-core + bc-admin patch. Estimated effort: 1 day. Not recommended unless other API changes already cluster nearby.
   - The `MCF_M12_*` env-var family — IF operators decide to procure these env vars in production for the first time, they should be procured under the semantic names (`MCF_METRIC_DRAFT_REVIEW_*`). Estimated effort: 4 hours (code + runbook + .env.example update). Not urgent.
5. **Persisted enum additions ARE permitted** under the established amendment-DDL pattern (PE-MC-13+ if needed, new audit_mode_code values, new run_kind values). These are forward-compatible additions, not Layer 3 migrations.

### When to reconsider Layer 3 migration

Re-evaluate Layer 3 migration if any of the following triggers occur:
- An external integration partner requires the API response field rename.
- Operators procure `MCF_M12_*` env vars in production for the first time.
- A new evaluator semantic change requires `mcf-m13-v7` bump (routine — no migration required).
- A regulatory / compliance audit requires explicit deprecation timeline for `m14_activated`.
- Layer 3 surface coherence becomes a documented onboarding friction point for new engineers.

Until any of these triggers fire, **the recommendation is no action.**

---

## 11. Explicit No-Execution Statement

This document is **inventory and risk map only**. No file was edited, no DB row touched, no env var changed, no migration run, no PR opened. The two stuck MCV rows on `bc_platform_dev` are untouched.

The three subagents that produced this inventory had read-only tool grants (Glob, Grep, Read; no Edit / Write). All findings cited file:line for verification.

### Layer 2 program — final state snapshot (for cross-reference)

| Tier | Status |
|---|---|
| Layer 1 (Tracks 1 + 2 + Cluster A/B residual) | ✅ closed |
| Layer 2a constants | ✅ closed (8 constants renamed) |
| Layer 2b interfaces / methods / classes | ✅ closed (16 identifiers renamed across 5 batches) |
| Layer 2c filename + import paths | ✅ closed (1 filename + 9 importers) |
| Layer 2d route aliases + `@ApiTags` + `@ApiOperation` | ✅ closed (2 routes aliased + 6 tags renamed + 23 Swagger strings rewritten) |
| **Layer 3 compatibility names (this inventory)** | **inventoried; deferred** |

The MMS / MCF Layer 2 program is operationally complete at the identifier tier; Layer 3 is the persisted-substrate tier and is deliberately preserved per Foundation Invariant III.
