---
title: MMS Layer 2 — Implementation-Name Inventory (2026-06-22)
description: Read-only inventory of code identifiers that still carry legacy MMS workflow codes (M11/M12/M12.5/M13/M14/M15, PE-MC-*, L-V*, C-FX-*, B6/C5/F3/B10, C1/C2/F1/F2). Maps every Layer 2 candidate to a classification (SAFE_RENAME_CANDIDATE / ROUTE_ALIAS_REQUIRED / PERSISTED_OR_COMPATIBILITY / DEFER_UNMAPPED / DO_NOT_RENAME) so a downstream execution batch can be authorized one cluster at a time.
status: draft
authority: implementation-inventory
date: 2026-06-22
project: bc-docs-v3
domain: mms
subdomain: layer2-implementation-names
focus: inventory
supersedes: []
governing_adr: DEC-54f221
---

# MMS Layer 2 — Implementation-Name Inventory (2026-06-22)

## 0. Scope, Method, and Non-Goals

**Governing ADR:** DEC-54f221 / D449 — three-layer model (Interpretation Surfaces / Implementation Names / Compatibility Names).

**Layer 2 definition.** Code identifiers — class / service / controller / module / interface / type / generic / enum / method / function / constant / variable / property / file / directory names, plus internal HTTP route paths and route-alias variables — that still carry legacy MMS workflow codes. Layer 2 is the engineer-visible surface and is governed at compile-time and import-time, not at the serialization boundary.

**Out of Layer 2 (delegated forward):**

- Layer 1 (operator-visible surfaces): comments, JSDoc, test-description strings, page headings, modal copy, operator-facing docs — **closed** (Track 1 + Track 2 + Cluster F no-op + Cluster G deferred).
- Layer 3 (compatibility names): DB column physical names, persisted enum *values*, JSON field names returned on the wire, telemetry keys, idempotency-key prefix values, persisted version-strings. These appear in this inventory as **PERSISTED_OR_COMPATIBILITY forward-pointers** but are not Layer 2 candidates.
- Cluster G (model-input gated): prompt templates, model output schemas, checklist-key contracts validated against model output — **planned and deferred** under `mms-layer1-cluster-g-prompt-regression-plan-2026-06-22.md`.

**Repos surveyed (read-only):**
- `bc-core/src` (production source; `.spec.ts`/`.test.ts` files excluded — see §8 for the test-file follow-up note).
- `bc-admin/src`.
- `bc-ai/app` and `bc-ai/tests`.
- `bc-portal/apps/web/src`.

**Method.** Four parallel `Explore` subagents, one per repo, run with identical-shape prompts. Each agent ran identifier-shape greps (PascalCase / camelCase / snake_case / kebab-case / CONSTANT_CASE / route-string literals) for the legacy-code families and classified each finding. Comments / JSDoc / test descriptions and decision identifiers (`DEC-*`, `D-NNN`) were explicitly excluded.

**Hard non-goals (operator scope-locks).**
- No file edits, no renames, no route changes, no test edits, no prompt edits.
- No runtime restart, no DB writes, no PR.
- The two stuck Metric Contract Versions on `bc_platform_dev` are untouched.
- Inventory and recommendation only. **No execution.**

---

## 1. Summary Counts by Repo and Classification

| Repo | SAFE_RENAME | ROUTE_ALIAS | PERSISTED_OR_COMPATIBILITY | DEFER_UNMAPPED | DO_NOT_RENAME | Repo total |
|---|---:|---:|---:|---:|---:|---:|
| **bc-core/src** | 18 | 4 | 4 | 0 | 1 | 27 |
| **bc-admin/src** | 0 | 0 | 1 (× 8 use sites) | 0 | 0 | 1 |
| **bc-ai/app & /tests** | 0 | 0 | 1 (× 1 tuple, 10 keys) | 0 | 0 | 1 |
| **bc-portal/apps/web/src** | 0 | 0 | 0 | 0 | 0 | 0 |
| **All repos** | **18** | **4** | **6** | **0** | **1** | **29** |

**Distribution observation.** Layer 2 mass is overwhelmingly in **bc-core/src**. The two frontends (bc-admin, bc-portal) and the AI service (bc-ai) are *clean of Layer 2 SAFE_RENAME candidates*: their only legacy-code touchpoints are **PERSISTED_OR_COMPATIBILITY** items — property names mirroring bc-core's API JSON contract (bc-admin) or wire-payload keys validated against model output shape (bc-ai). These cannot be Layer-2-renamed in isolation; they must wait for Layer 3 to act on the corresponding bc-core column / JSON field / model-contract key.

This means **Layer 2 is effectively a bc-core/src refactor** governed by the same DEC-54f221 doctrine, with secondary cleanup in two co-located bc-core script files (§3.6).

---

## 2. Top 15 SAFE_RENAME Candidates by Blast Radius (bc-core/src)

Ordered approximately by transitive import / DI / cross-module reach. "Blast radius" is the count of distinct files importing or referencing the identifier (low-resolution from agent output, not a precise tsc-graph trace).

| # | Identifier | Kind | File | Blast radius | Proposed semantic target |
|---:|---|---|---|---:|---|
| 1 | `M12PanelRunWriterService` | Class (NestJS service) | `src/registry/metric-authoring/m12-panel-run-writer.service.ts` | ~3 (module + controller + sibling service) | `MetricDraftReviewPanelRunWriterService` |
| 2 | `M13_EVALUATOR_VERSION` | Const string | `src/registry/mcf/metric-publication-eligibility-evaluator.service.ts:152` | ~3 (controller + read service + tests) | `PUBLICATION_REVIEW_EVALUATOR_VERSION` |
| 3 | `M14_VERIFIER_VERSION` | Const string | `src/registry/mcf/mcf-cert-writer.service.ts:406` | ~2 (controller + tests) | `METRIC_ACTIVATION_VERIFIER_VERSION` |
| 4 | `M14ActivationGateInputs` | TS interface | `src/registry/mcf/mcf-read.service.ts:1259` | ~1 (controller) | `MetricActivationGateInputs` |
| 5 | `M14PeRow` | TS interface | `src/registry/mcf/mcf-read.service.ts:1295` | ~1 (controller) | `MetricActivationPublicationEligibilityRow` |
| 6 | `M15SupersessionGateInputs` | TS interface | `src/registry/mcf/mcf-read.service.ts:1304` | ~1 (controller) | `MetricSupersessionGateInputs` |
| 7 | `M13_HASH_ALGORITHM_VERSION` | Const string | `src/registry/mcf/metric-publication-eligibility-evaluator.service.ts:93` | ~1 (local + stamped on parent MC) | `PUBLICATION_REVIEW_HASH_ALGORITHM_VERSION` |
| 8 | `M12_5_HASH_ALGORITHM_VERSION` | Const string | `src/registry/mcf/metric-authoring-materialization.service.ts:227` | ~1 | `METRIC_DRAFTING_HASH_ALGORITHM_VERSION` |
| 9 | `M12_5_POLICY_UID` | Const string | `src/registry/mcf/metric-authoring-materialization.service.ts:230` | ~1 | `METRIC_DRAFTING_POLICY_UID` |
| 10 | `M12_5_IDEMPOTENCY_KEY_PREFIX` | Const string | `src/registry/mcf/metric-authoring-materialization.service.ts:236` | local; the **VALUE** `'mcf-m12-5/'` is Layer 3 | `METRIC_DRAFTING_IDEMPOTENCY_KEY_PREFIX` (identifier only — value preserved) |
| 11 | `PANEL_PROMPT_VERSION` | Const string | `src/registry/mcf/metric-authoring-panel.service.ts:81` | ~1 (locally) | `METRIC_DRAFT_REVIEW_PROMPT_VERSION` |
| 12 | `computeM13EvaluationSignatureHash` | Exported function | `src/registry/mcf/metric-publication-eligibility-evaluator.service.ts:2033` | ~2 (read service + controller spec) | `computePublicationReviewEvaluationSignatureHash` |
| 13 | `readM13Summary` | Private method | `src/registry/mcf-readiness-bridge.service.ts:152` | 1 (intra-class) | `readPublicationReviewSummary` |
| 14 | `MCF_M12_{MAKER,CHECKER,JUDGE,MODERATOR}_MODEL` | Env-var constant set | `src/registry/mcf/panel-agents/model-defaults.ts:88–97` | env-config surface (operator-visible) | `MCF_METRIC_DRAFT_REVIEW_{MAKER,CHECKER,JUDGE,MODERATOR}_MODEL` |
| 15 | `pe-mc-12-evaluation.ts` / `pe-mc-12-result-codes.ts` | Filenames | `src/registry/mcf/` | 1–2 importers each | `source-vocabulary-discipline-gate-evaluation.ts` / `-result-codes.ts` |

Three additional bc-core findings (not in top 15 but real SAFE_RENAME items):

16. `M12PanelRunWriter*` test-helper / DI-mock identifiers in spec files siblings. (Test-file work — §8.)
17. `M14_` / `M13_` / `M12_5_` other local constants in the same files as items 7–11 above; rolled up under the same per-file batch.
18. `mcf-m12-5-preflight.mjs` script (forward-pointer; lives under `bc-core/scripts/`, not `bc-core/src/`). See §3.6.

---

## 3. SAFE_RENAME Surfaces by Kind (bc-core/src)

### 3.1 Class / Service identifiers (1)
- `M12PanelRunWriterService` — covered in §2 #1. Production file rename required (§3.5 / §3.6).

### 3.2 Method / Function identifiers (2)
- `computeM13EvaluationSignatureHash` (§2 #12)
- `readM13Summary` (§2 #13)

### 3.3 Interface / Type identifiers (3)
- `M14ActivationGateInputs`, `M14PeRow`, `M15SupersessionGateInputs` (§2 #4–#6)

### 3.4 Constant identifiers (8)
- `M13_EVALUATOR_VERSION`, `M14_VERIFIER_VERSION`, `M13_HASH_ALGORITHM_VERSION`, `M12_5_HASH_ALGORITHM_VERSION`, `M12_5_POLICY_UID`, `M12_5_IDEMPOTENCY_KEY_PREFIX`, `PANEL_PROMPT_VERSION`, env-var set `MCF_M12_*` (§2 #2, #3, #7–#11, #14)

**Crucial Layer 2 vs Layer 3 distinction for these constants.** The **identifier names** (left-hand side, e.g. `M13_EVALUATOR_VERSION`) are Layer 2. The **string values** (right-hand side, e.g. `'mcf-m13-v6'`, `'mcf-m12-5/'`, `'mcf-hash-v1'`) are **persisted** — they are stamped onto Metric Contract / MCV rows in `bc_platform_dev` and feed idempotency keys that already exist in DB. **Values must be preserved verbatim under Foundation Invariant III.** Layer 2 renames the LHS; Layer 3 (or a deliberate value-frozen approach) handles the RHS.

### 3.5 Filename identifiers in bc-core/src (3)
- `m12-panel-run-writer.service.ts` (paired with already-renamed spec)
- `pe-mc-12-evaluation.ts`
- `pe-mc-12-result-codes.ts`

Each rename requires:
- Filename change.
- `from './…'` import-path updates across the importer set (TypeScript will complain at compile time).
- NestJS DI registration check (no DI-by-string-path expected, but verify).

### 3.6 Filenames outside bc-core/src (1, forward-pointer)
- `bc-core/scripts/mcf-m12-5-preflight.mjs` — script-tier file that is not under `src/` and was therefore out of agent scope. Per the consolidation checkpoint §7, this is a known Layer 2 filename candidate. Treat as Layer 2c batch overflow when filename batch is authorized.

### 3.7 Directory names — none found
No `m12*` / `pe-mc-*` / etc. directory exists under `bc-core/src`. `src/registry/mcf/` is semantic (Metric Contract Framework). `src/registry/metric-authoring/` is semantic. **Zero directory renames needed.**

### 3.8 DEFER_UNMAPPED — none
All 18 bc-core SAFE_RENAME candidates fall under the ratified Layer 1 mapping (M11→Metric Intake, M12→Metric Draft Review, M12.5→Metric Drafting, M13→Publication Review, M14→Metric Activation, M15→Metric Supersession, PE-MC-12→Source-Vocabulary Discipline Gate). No identifier landed in unmapped families (M16/M17/M18+, C1/C2/F1/F2 in BCF context, L-V1*).

### 3.9 DO_NOT_RENAME (1)
- `M10_VERIFIER_ALGORITHM_VERSION` at `src/registry/mcf/metric-self-verification.service.ts:44` — on the Layer 1 preserve list (M10 is stable framework anchor, not legacy). Identifier and value both preserved.

---

## 4. ROUTE_ALIAS_REQUIRED Candidates (bc-core/src)

Four NestJS HTTP route paths embed legacy stage codes. These are **runtime URL surfaces** — even if no external client currently consumes them, the operator may want to keep the legacy path live as a backward-compatible alias for at least one publication cycle before retirement.

| # | Method + path | Controller method | Legacy stage | Proposed semantic path | Alias retention |
|---:|---|---|---|---|---|
| 1 | `POST /api/mcf/panel-runs` | `McfPanelRunController.runPanel()` | M12 | `POST /api/mcf/metric-draft-review/panel-runs` | Keep legacy as alias |
| 2 | `GET /api/mcf/metric-contracts/:uid/pe-mc-status` | `McfPublicationEligibilityController.readStatus()` | M13 / PE-MC family | `GET /api/mcf/metric-contracts/:uid/publication-review-status` | Keep legacy as alias |
| 3 | `POST /api/mcf/metric-contracts/:uid/evaluate-pe-mc` | `McfPublicationEligibilityController` activate | M13 / PE-MC family | `POST /api/mcf/metric-contracts/:uid/evaluate-publication-eligibility` | Keep legacy as alias |
| 4 | `POST /api/mcf/metric-contract-versions/:mcvUid/activate` | `McfPublicationActivationController.activate()` | M14 | (Path already semantic; only **route-key constant** `mcf-m14-activate` if present internally needs review) | n/a (path is fine) |

**Layer 2 doctrine for route aliases.** Add the semantic route as the canonical handler. Register the legacy path as a NestJS alias pointing to the same controller method. Mark legacy path with a `Deprecated` response header. Do **not** delete the legacy path in the Layer 2 batch — alias retirement is a separate downstream batch.

**Open question for the operator (§9, item 4):** does the alias retention period get locked in this batch, or is alias retirement deferred to a "Layer 2f route-alias retirement" follow-up?

---

## 5. PERSISTED_OR_COMPATIBILITY Forward-Pointers (Layer 3 scope)

These are listed for completeness so the operator can see the downstream Layer 3 surface. **None are Layer 2 SAFE_RENAME candidates.**

### 5.1 bc-core/src (4)

| Item | Location | Why Layer 3 |
|---|---|---|
| `PE_MC_CODES` array (values `'PE-MC-1' … 'PE-MC-12'`) | `metric-publication-eligibility-evaluator.service.ts:163` | Values persisted in DB column `pe_check_code`; rename of the ARRAY VARIABLE is Layer 2-eligible **only if** the array values themselves are NOT also identifier-shape strings on the wire. Recommend: defer to Layer 3 together with the column rename. |
| Column `pe_check_code` on `metric.metric_publication_eligibility_result` | `src/database/schema/mcf/metric-publication-eligibility-result.ts` | DB column name; Foundation Invariant III preserves historical rows; Layer 3 territory. |
| Column `verifier_version` / `evaluator_version` on the same table | Same file | Holds the Layer-3 *values* `'mcf-m14-v2'` / `'mcf-m13-v6'`. Column names already generic; **values** are the persisted artifact. Layer 3 chooses whether to migrate or freeze. |
| `PE_MC_12_RESULT_CODES` verdict enum values | `pe-mc-12-result-codes.ts:29` (e.g. `'GRANDFATHERED_LEGACY_NULL_BCV_POINTER'`, `'OPERATOR_REVIEW_MISSING_BCV_POINTER_ON_NEW_MCV'`) | Values appear in `evidence_json`; persisted; Layer 3. |
| `CAS_V0_MODES = ['pre_m13_audit']` | `chain-audit/chain-audit.dto.ts:25` | Mode value persisted in chain-audit records. Layer 3. |

### 5.2 bc-admin/src (1 property name, 8 use sites)

| Item | Use sites (count) | Why Layer 3 |
|---|---:|---|
| `m14_activated` property on `McfMetricContract` / `McfMetricContractDetail` | 8 (interface decls + DataTable column keys + JSX boolean conditions across `MetricCatalogPage`, `MetricDetailPage`, `MetricLandscapePage`, `mcf-catalog.ts`) | Mirrors the JSON field name returned by bc-core's `GET /api/mcf/metric-contracts/*` endpoints. Renaming the bc-admin TS field without renaming the bc-core JSON key breaks runtime data binding. Must move with Layer 3 JSON-field migration. |

**Important.** bc-admin has **zero** Layer 2 SAFE_RENAME candidates. Every legacy code in bc-admin code is either a comment (already done in Layer 1) or this one persisted-shape property. **No bc-admin Layer 2 batch is required.**

### 5.3 bc-ai/app (1 wire-payload contract)

| Item | Location | Why Layer 3 / Cluster G |
|---|---|---|
| `_CHECKLIST_ITEM_KEYS = ("M1", "M2", …, "M10")` Python tuple | `app/pipeline/registry_authoring_panel.py:103–105` | Drives validation of the Moderator model's `recommendation.checklist_answers` dict structure on the F4-v2 Vocabulary Admission Checklist v1 path. Values flow to bc-core via `verdictPayloadJson` and to telemetry sidecar. Renaming requires synchronized changes in: (a) the bc-ai validator; (b) the Moderator prompt at `app/prompts/registry-authoring/v1.0/moderator.md`; (c) the bc-core `panel_output_record` DTO validator. **This is partly Layer 3 (wire payload) and partly Cluster G (model-output contract).** Do not move in Layer 2. |

**Important.** bc-ai has **zero** Layer 2 SAFE_RENAME candidates. The python module/class/function/file names are already semantic (`registry_authoring_panel.py`, `RegistryAuthoringMaker`, `RegistryAuthoringChecker`, `RegistryAuthoringModerator`, `BfDedupMaker`). All legacy-code references in bc-ai are either comments (Layer 1 done) or the persisted-wire `_CHECKLIST_ITEM_KEYS` tuple. **No bc-ai Layer 2 batch is required.**

### 5.4 bc-portal — genuinely empty

Every `M*` / `F*` / `B*` match in bc-portal is a confirmed false positive: SVG path coordinates (`M10`/`M11`/`M13`/`M15` in `brandLogos.ts` are SVG `MoveTo`/`LineTo` commands), SAP business-domain codes (`M1`/`M2`/`M3` for Malfunction / Maintenance Request / Activity Report in `data/catalog/sap/pm.ts`), and browser keyboard-shortcut codes (`F1`–`F3`, `F12`). 22,143 TypeScript/JavaScript files scanned. **No bc-portal Layer 2 batch is required.**

---

## 6. Dependency / Import / Route Implications

### 6.1 TypeScript imports
- The class rename (#1 `M12PanelRunWriterService`) propagates to: `metric-authoring.module.ts`, `mcf-panel-run.controller.ts`, `metric-authoring-panel.service.ts`. NestJS DI is class-token-based — the class **identifier** is the DI key, so the rename plus the import-path update lands cleanly. Existing spec already renamed in Track 2 E4.
- The interface renames (#4, #5, #6) propagate to one controller each (`mcf-publication-activation.controller.ts`, `mcf-mcv-supersede.controller.ts`). Pure type-level; no DI / runtime impact.
- The constant renames (#2, #3, #7–#11, #14) are intra-file or intra-module; importers are explicit `import { … }` declarations.
- The function rename (#12 `computeM13EvaluationSignatureHash`) is an exported helper; importers are explicit.

### 6.2 NestJS DI tokens
- All NestJS providers in scope register via class token (the class identifier), not via string token. **A class rename = a DI-token rename in one step.** No `@Inject('legacy-string-token')` patterns observed in the candidate set.

### 6.3 Route registrations
- The four ROUTE_ALIAS_REQUIRED routes (§4) are registered via `@Controller(...)` + `@Get|Post|Put(...)` decorator strings. Adding the semantic route alongside the legacy alias is a two-line change per route in the controller file.

### 6.4 Filename renames vs case-insensitive filesystem
- Windows filesystem is case-insensitive by default. Avoid case-only renames. The three proposed filename renames in §3.5 are full lexeme changes, so no case-folding hazard.

### 6.5 Cross-repo impact
- **Zero cross-repo impact** from any Layer 2 candidate in this inventory. bc-admin / bc-ai / bc-portal contain no Layer 2 SAFE_RENAME items, so Layer 2 work in bc-core/src does not require coordinated edits in any other repo. (Cross-repo coordination is a Layer 3 concern when JSON field names, route paths, or persisted enum values migrate.)

### 6.6 ai_telemetry impact
- bc-core ai_telemetry tables (`ai_run_ledger`, `ai_call_ledger`) store hashes only. No identifier-name dependency. Layer 2 renames do not touch telemetry-stored content.

---

## 7. Open Naming Questions

1. **M12 vs M12.5 semantic split.** Layer 1 ratified M12→**Metric Draft Review** (panel-run execution) and M12.5→**Metric Drafting** (materialization). The constant prefix `M12_5_*` becomes `METRIC_DRAFTING_*`. The constant prefix `M12_*` (if any standalone exists; in the inventory the `MCF_M12_*` env vars and the `M12PanelRunWriterService` class belong here) becomes `METRIC_DRAFT_REVIEW_*` / `MetricDraftReview*`. **Confirm: keep this naming split, or collapse both under a single prefix?** Recommend: keep the split — it is the Layer 1 ratified semantic distinction.

2. **`PANEL_PROMPT_VERSION` rename target.** Two valid candidates: `METRIC_DRAFT_REVIEW_PROMPT_VERSION` (specific to M12-stage panel) or a generic `MCF_PANEL_PROMPT_VERSION` (if the constant is/will be shared across other MCF panels). The constant is currently in `metric-authoring-panel.service.ts` (M12-only). Recommend: specific name.

3. **`PE_MC_CODES` array rename.** This is a Layer 2 *variable* whose *value-list* is Layer 3 *persisted enum strings*. Option A — rename the variable to `PUBLICATION_ELIGIBILITY_CHECK_CODES` in Layer 2 while keeping the value strings frozen. Option B — defer the variable rename to Layer 3 so identifier and values move together. Recommend: **Option B** — keep identifier and values coupled to a single Layer 3 migration so reviewers see one coherent change.

4. **Route-alias retirement horizon.** When we add `POST /api/mcf/metric-draft-review/panel-runs` etc., how long does the legacy `POST /api/mcf/panel-runs` alias stay live? Recommend: keep aliases through one publication cycle + 30 days, then remove in a dedicated Layer 2f follow-up. Operator decision required.

5. **Env-var migration policy.** `MCF_M12_*` env vars (item #14) are deployment-config artifacts. Renaming requires coordinating .env.example, AWS Parameter Store, CI config, and operator runbook. Two options: (a) Rename + accept both names during a transition window; (b) keep legacy names indefinitely and add a comment-only Layer 1 alias note. Recommend: (a) with transition window — operator runbook is the gate.

6. **`M12_5_IDEMPOTENCY_KEY_PREFIX` value preservation.** The VALUE `'mcf-m12-5/'` is used as an idempotency-key prefix and is persisted in DB rows. Identifier rename is Layer 2. Value preservation under Foundation Invariant III is mandatory. Confirm operator wants identifier rename in Layer 2 with value frozen (recommended), or full move to Layer 3 with both identifier and value.

7. **Test-file companion sweep.** The 18 SAFE_RENAME candidates in `bc-core/src` each have one or more `.spec.ts` companions. Two specs were renamed in Track 2 E4 (`m12-panel-run-writer.service.spec.ts` and `pe-mc-12-evaluation.spec.ts`). The remainder were untouched (test descriptions only). When Layer 2 executes and class/constant/method identifiers move, the spec-file IMPORTS automatically need updating — TypeScript will catch missing identifiers. **No separate test-file inventory needed** — but the executing batch must include `.spec.ts` files in its file set.

---

## 8. Test-file Layer 2 Note

The agent scope excluded `.spec.ts` files because:
- Test-description strings are Layer 1 (already done).
- Test-INTERNAL helper identifiers and DI-mock identifiers will be renamed mechanically when the production identifier they reference is renamed (TypeScript compile error otherwise).

A separate Layer 2g "tests-only identifier" batch is **not** anticipated. The two renamed specs (`metric-draft-review-panel-run-writer.service.spec.ts`, `publication-eligibility-check-12.spec.ts`) are filename-only events from Track 2 E4 — their internal identifiers tracked their production counterparts.

If, on execution, additional test-only identifiers are discovered (e.g. a test fixture named `m12FixtureForPanelRunWriter`), they fold into the same batch as the production identifier rename.

---

## 9. Recommended Execution Order (no execution authorized in this batch)

The five sub-batches preserve the Layer 1 doctrine pattern (small batches, single Foundation invariant in view per batch, no surprise blast radius).

### 9.1 Layer 2a — Local constants / helper names (no class moves)
**Scope.** Items #2, #3, #7, #8, #9, #10, #11, #14 (constants), #12, #13 (function + private method). All intra-file or single-importer.

**Files touched** (production source — no specs in this batch except for compile-fix follow-ups TypeScript surfaces):
- `metric-publication-eligibility-evaluator.service.ts` (constants #2, #7, function #12)
- `mcf-cert-writer.service.ts` (constant #3)
- `metric-authoring-materialization.service.ts` (constants #8, #9, #10)
- `metric-authoring-panel.service.ts` (constant #11)
- `mcf-readiness-bridge.service.ts` (private method #13)
- `panel-agents/model-defaults.ts` (env-var constant set #14)

**Why first.** Smallest blast radius, no class-identifier or filename change. Pure compile-time symbol churn. tsc + vitest are the gates. Recoverable in a single rollback commit if needed.

**Value preservation.** All RHS string values frozen verbatim under Foundation III.

### 9.2 Layer 2b — Service class + interface identifiers (no filenames yet)
**Scope.** Items #1 (`M12PanelRunWriterService`), #4 (`M14ActivationGateInputs`), #5 (`M14PeRow`), #6 (`M15SupersessionGateInputs`).

**Files touched.** Service class declarations + their NestJS module registration + the controllers that import the renamed interfaces. Class identifier change propagates via TypeScript imports and DI tokens.

**Why second.** Slightly higher blast radius than 2a but still confined to identifier-and-import work. Filename stays on disk as `m12-panel-run-writer.service.ts` in this batch — file rename comes in 2c.

### 9.3 Layer 2c — Production filenames
**Scope.** Items #15 (the two `pe-mc-12-*.ts` files), the production sibling `m12-panel-run-writer.service.ts` from §3.5, and the bc-core scripts-tier file `mcf-m12-5-preflight.mjs` from §3.6.

**Files touched.** Four file renames + import-path updates in their importers. NestJS module wiring re-points by import path.

**Why third.** Filename moves require git-mv discipline, branch hygiene, and an explicit verification that no other file references the path-as-string anywhere (e.g. dynamic require, lazy import, deploy-time include list). Each rename gets its own commit.

### 9.4 Layer 2d — Internal route aliases (HTTP path semantics)
**Scope.** Items #1–#3 from §4 — add semantic routes alongside legacy aliases. Item #4 from §4 is a no-op (path already semantic).

**Files touched.** Two controllers (`McfPanelRunController`, `McfPublicationEligibilityController`).

**Why fourth.** Runtime route surface change. Even when alias-preserving, a smoke test against `npm run start:dev` + a curl/fetch of the new path is required before merge. Operator gate: alias retention window from §7-Q4.

### 9.5 Layer 2e — Remaining ambiguous items + open-question resolutions
**Scope.** Resolved-decision items from §7 — env-var migration policy (Q5), `PE_MC_CODES` array variable rename if Option A chosen (Q3), idempotency-key value freeze confirmation (Q6).

**Why fifth.** This batch absorbs anything the operator wants to revisit after seeing 2a–2d land. It is also the natural slot for a Layer 2g test-fixture sweep if §8 surfaced anything during 2a–2d execution.

### 9.6 Cross-batch invariants (apply to every Layer 2 batch)
- No DB writes. No persisted-value changes. Foundation Invariant III preserved.
- No bc-admin / bc-ai / bc-portal edits — all Layer 2 work is bc-core internal.
- Each batch produces its own PR + commit, runs `npm run typecheck`, runs `npx vitest run` over affected modules, and updates the Layer 2 closeout note before merge.
- The two stuck MCV rows on `bc_platform_dev` remain untouched.

---

## 10. Recommended First Proof Batch

**Proposal: Layer 2a-pilot = constant #11 (`PANEL_PROMPT_VERSION`) only.**

Why this single constant:
- Smallest scope of any Layer 2a item: one file, one local importer, one straightforward rename to `METRIC_DRAFT_REVIEW_PROMPT_VERSION`.
- Exercises the value-preservation pattern explicitly (RHS string `'m12-panel-v1'` frozen under Foundation III).
- Demonstrates the tsc + vitest + import-update workflow against the smallest possible target.
- Establishes the per-commit pattern and a closeout-note template usable for 2a-rest, 2b, 2c, 2d, 2e.

If the pilot succeeds and operator authorizes, the rest of Layer 2a follows in a single commit (constants are independent and naturally batch together).

---

## 11. Compatibility-Names Layer (Layer 3) Surface Summary

For completeness — Layer 3 work surfaced incidentally by this inventory but **not** in this batch:

| Surface | Count | Touchpoint |
|---|---:|---|
| Persisted DB column names with legacy stem | 1 | `pe_check_code` on `metric.metric_publication_eligibility_result` |
| Persisted DB enum *values* | ~20 | `PE-MC-1`..`PE-MC-12`, `PE_MC_12_RESULT_CODES` verdicts, `pre_m13_audit` chain-audit mode |
| Persisted version-string values | 4 | `'mcf-m13-v6'`, `'mcf-m14-v2'`, `'mcf-hash-v1'`, `'mcf-verifier-v1'` |
| Persisted idempotency-key prefix | 1 | `'mcf-m12-5/'` |
| API JSON field names (bc-core ↔ bc-admin) | 1 | `m14_activated` |
| Model-contract checklist keys (Cluster G overlap) | 1 tuple, 10 keys | `_CHECKLIST_ITEM_KEYS = ("M1"..."M10")` |
| Telemetry sidecar keys | 0 confirmed | (Likely none — telemetry stores hashes per bc-core ai_telemetry contract) |

Layer 3 batching is out of scope for this inventory. Surface is captured here so the operator can size the next gated batch.

---

## 12. Explicit No-Execution Statement

This document is **inventory and recommendation only**. No file was edited, no rename was executed, no route was changed, no test was modified, no prompt was edited, no DB row was touched, no runtime service was restarted, no PR was opened. The four `Explore` subagents that produced this inventory were read-only by tool grant (Glob, Grep, Read, WebFetch, WebSearch, NotebookRead — no Edit, no Write).

The two stuck Metric Contract Versions on `bc_platform_dev` are untouched.

Layer 1 (Track 1 + Track 2 + Cluster F + Cluster G) is closed-or-deferred per the consolidation checkpoint. Layer 2 execution requires an explicit operator authorization naming the sub-batch (2a-pilot / 2a-rest / 2b / 2c / 2d / 2e).
