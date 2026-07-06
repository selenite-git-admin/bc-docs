---
title: MMS Layer 2d — Route-Alias / Compatibility-Boundary Inventory (2026-06-23)
description: Read-only inventory of all MMS / MCF HTTP route paths, controller method names, Swagger / @ApiTags decorators, and active callers that still expose legacy stage codes (M11–M15, PE-MC, etc.). Classifies each finding for downstream route-alias work. NO route changes executed.
status: draft
authority: implementation-inventory
date: 2026-06-23
project: bc-docs-v3
domain: mms
subdomain: layer2-route-aliases
focus: inventory
supersedes: []
governing_adr: DEC-54f221
---

# MMS Layer 2d — Route-Alias / Compatibility-Boundary Inventory

## 0. Scope, Method, and Non-Goals

**Governing ADR:** DEC-54f221 / D449 — three-layer model (Interpretation Surfaces / Implementation Names / Compatibility Names).

**Layer 2d definition.** HTTP route paths, controller method names, Swagger / OpenAPI documentation labels (`@ApiTags`, `@ApiOperation`), and active callers that still expose legacy MMS stage codes (`M11`, `M12`, `M12.5`, `M13`, `M14`, `M15`, `PE-MC-*`). Layer 2d is the **compatibility-boundary** surface — any change here affects external consumers (frontends, tools, operators using Swagger UI, runbook procedures).

**Method.** Parallel ripgrep + Glob across:
- `bc-core/src/**/*.controller.ts` (NestJS `@Controller`, `@Get/Post/Put/Patch/Delete`, `@ApiTags`, `@ApiOperation` decorators)
- `bc-admin/src` (active frontend `apiFetch` / `useQuery` call sites)
- `bc-portal/apps/web/src` (customer frontend)
- `bc-ai/app` (Python HTTP clients)
- `bc-core/scripts` (operator-triggered scripts, retry scripts, audit-output)
- `bc-docs-v3/docs/implementation/*.md` (runbook + DBCP chapters)

**Sources used (exact patterns):**
```
rg '@Controller\(['"`]' bc-core/src/registry/mcf bc-core/src/registry/metric-authoring
rg '@(Get|Post|Put|Delete|Patch)\(['"`]' bc-core/src/registry/mcf bc-core/src/registry/metric-authoring
rg '@ApiOperation|@ApiTags' bc-core/src/registry/mcf
rg '/api/mcf/|/api/bcf/|pe-mc' bc-admin/src bc-portal bc-ai
rg 'pe-mc-status|evaluate-pe-mc|/mcf/panel-runs|/mcf/intakes' bc-core/src bc-core/scripts bc-docs-v3
```

**Hard non-goals (operator scope-locks).**
- No route changes. No code edits. No alias additions. No legacy-path removals.
- No script edits. No DB writes. No env-var changes. No telemetry changes. No prompt edits. No PR.
- Inventory and recommendation only.

---

## 1. Summary Counts by Classification

| Classification | Items | Notes |
|---|---:|---|
| **ROUTE_ALIAS_REQUIRED** | **2 routes** | The only HTTP route paths in `bc-core` MCF that embed legacy-stage codes |
| **INTERNAL_ONLY_SAFE_RENAME** | 6 Swagger `@ApiTags` strings; 3 test-description strings | Documentation surfaces + spec descriptions |
| **LAYER_3_COMPATIBILITY** | The persisted `PE-MC-1..12` enum *values* that the two ROUTE_ALIAS paths echo | DB column `metric_publication_eligibility_result.pe_check_code` |
| **HISTORICAL_ONE_SHOT** | 50+ references in audit-output `.md`/`.json`/`.jsonl` files; runbook DBCP chapters | Foundation Invariant III preserved |
| **DO_NOT_TOUCH** | DEC- / D-NNN identifiers, ADR references throughout | Decision IDs preserved |

**Headline finding.** The MMS route surface is **substantially cleaner** than feared. Of the **14 MCF controllers + 1 metric-authoring controller** surveyed, only **one controller** (`mcf-publication-eligibility.controller.ts`) embeds legacy-stage codes in its actual route paths (the two `pe-mc` routes). Every other MCF route uses semantic vocabulary (`intakes`, `panel-runs`, `materialize`, `activate`, `supersede`, `abandon`, `rebind`). The remaining legacy-stage presence in HTTP surfaces is documentation-tier (Swagger `@ApiTags`) and JSDoc.

---

## 2. ROUTE_ALIAS_REQUIRED — The Two PE-MC Route Paths

### 2.1 `GET /api/mcf/metric-contracts/:metricContractUid/pe-mc-status`

| Field | Value |
|---|---|
| **Current path** | `GET /api/mcf/metric-contracts/:metricContractUid/pe-mc-status` |
| **Owning controller** | `bc-core/src/registry/mcf/mcf-publication-eligibility.controller.ts:91` |
| **Controller class** | `McfPublicationEligibilityController` |
| **Method name** | `readStatus(...)` (already semantic) |
| **Proposed semantic path** | `GET /api/mcf/metric-contracts/:metricContractUid/publication-eligibility-status` |
| **Active callers (cross-repo sweep)** | bc-admin: **0** &nbsp;\|&nbsp; bc-portal: **0** &nbsp;\|&nbsp; bc-ai: **0** |
| **Internal callers** | Spec `mcf-publication-eligibility.controller.spec.ts:57` (description string mirrors the route); the controller's own spec exercises the method |
| **Operator-visible references** | 18 docs in `bc-docs-v3/docs/implementation/`; `scripts/audit-output/*.md` historical evidence |
| **Compatibility recommendation** | **Add semantic alias and keep legacy.** Even though no bc-admin / bc-ai caller hits this path today, operators may invoke it via Swagger UI or curl based on runbook documentation. Removing the legacy path is a breaking change for any external consumer (operator scripts, ad-hoc curl, integration tests). |
| **Risk level** | LOW-MEDIUM. Adding an alias is a one-line `@Get(...)` decorator addition on the same method. Removing the legacy alias later requires a deprecation window. |
| **Suggested batch order** | After at least one external consumer survey confirms zero ad-hoc usage. |

### 2.2 `POST /api/mcf/metric-contracts/:metricContractUid/evaluate-pe-mc`

| Field | Value |
|---|---|
| **Current path** | `POST /api/mcf/metric-contracts/:metricContractUid/evaluate-pe-mc` |
| **Owning controller** | `bc-core/src/registry/mcf/mcf-publication-eligibility.controller.ts:99` |
| **Controller class** | `McfPublicationEligibilityController` |
| **Method name** | (verb in line 99, paired with `readStatus`) |
| **Proposed semantic path** | `POST /api/mcf/metric-contracts/:metricContractUid/evaluate-publication-eligibility` |
| **Active callers (cross-repo sweep)** | bc-admin: **0** &nbsp;\|&nbsp; bc-portal: **0** &nbsp;\|&nbsp; bc-ai: **0** |
| **Internal callers** | Spec `mcf-publication-eligibility.controller.spec.ts:63,72` (descriptions mirror route); active runbook chapters reference it |
| **Operator-visible references** | Multiple runbook DBCP chapters list this as **step 7** of the activation flow (`f1-a2-s2-a-track-paid-customer-invoice-count-seed-dbcp-held-2026-06-14.md:223`, etc.) |
| **Compatibility recommendation** | **Add semantic alias and keep legacy.** Same reasoning as 2.1. The path is part of multiple active and historical runbook procedures. |
| **Risk level** | LOW-MEDIUM. Same shape as 2.1. |
| **Suggested batch order** | Same batch as 2.1 (both routes on the same controller — natural cluster). |

### 2.3 Important note on the legacy stem

The path tokens `pe-mc-status` and `evaluate-pe-mc` **echo** the persisted enum-value family (`'PE-MC-1'`, `'PE-MC-2'`, ..., `'PE-MC-12'`) stored in `metric_publication_eligibility_result.pe_check_code`. The persisted values are **Layer 3 compatibility values** (Foundation Invariant III preserved). Changing the path stem from `pe-mc-status` → `publication-eligibility-status` is a Layer 2 concern (HTTP surface vocabulary); it does NOT require a Layer 3 enum-value migration. Both can move independently.

---

## 3. INTERNAL_ONLY_SAFE_RENAME — Swagger `@ApiTags` (6 stage-coded tags)

These are documentation-tier labels shown in Swagger UI. They are NOT part of the HTTP wire contract (URL/headers/body) but ARE part of the generated OpenAPI spec consumed by external doc tooling and operators browsing endpoints.

| File | `@ApiTags` value (legacy) | Proposed semantic value |
|---|---|---|
| `mcf-intake.controller.ts:36` | `MCF / M11 Intake` | `MCF / Metric Intake` |
| `mcf-panel-run.controller.ts:36` | `MCF / M12 Panel Run` | `MCF / Metric Draft Review Panel Run` |
| `mcf-materialization.controller.ts:25` | `MCF / M12.5 Materialization` | `MCF / Metric Drafting Materialization` |
| `mcf-publication-eligibility.controller.ts:25` | `MCF / M13 Publication Eligibility` | `MCF / Publication Review Eligibility` |
| `mcf-publication-activation.controller.ts:67` | `MCF / M14 Publication Activation` | `MCF / Metric Activation` |
| `mcf-mcv-supersede.controller.ts:56` | `MCF / M15 Metric Supersession` | (already semantic; no change) |

Note `mcf-mcv-supersede` already uses the semantic name; only "M15" prefix is legacy.

`@ApiOperation` summary strings (`'Create operator-direct M11 intake'`, `'List M11 intakes ...'`, `'Read PE-MC evaluation results for an MC (PE-MC-1..10 rows)'`, etc.) similarly embed stage codes in their summary text. These are operator-visible Swagger documentation, classified as **operator-facing surface (Layer 1)** — partially already-mapped in earlier Track 1 + Track 2 Layer 1 work, but Swagger summaries were out of scope at that point.

**Compatibility recommendation:** rename the labels directly (they are not wire-contract). Document changes via OpenAPI spec changelog if external doc consumers exist.

**Risk level:** LOW. These are display-only strings.

---

## 4. INTERNAL_ONLY_SAFE_RENAME — Test Description Strings

The publication-eligibility controller spec file has 3 `it(...)` descriptions that literally mirror the route path tokens:

| File:Line | Description string | Coherence fix |
|---|---|---|
| `mcf-publication-eligibility.controller.spec.ts:57` | `'GET /pe-mc-status delegates to read service'` | Update to `'GET /publication-eligibility-status delegates to read service'` once route alias is added |
| `mcf-publication-eligibility.controller.spec.ts:63` | `'POST /evaluate-pe-mc resolves active MCV + invokes evaluator with actorSub'` | Update similarly |
| `mcf-publication-eligibility.controller.spec.ts:72` | `'POST /evaluate-pe-mc throws NotFoundException when no active MCV exists'` | Update similarly |

These are test-description coherence updates tied to the route alias batch. Not stand-alone.

---

## 5. Full Controller Inventory (15 controllers)

The complete MCF + metric-authoring controller surface in `bc-core/src`:

| Controller | Base path | Stage in path? | Stage in `@ApiTags`? |
|---|---|:---:|:---:|
| `mcf-intake.controller.ts` | `mcf/intakes` | NO | M11 |
| `mcf-panel-run.controller.ts` | `mcf/panel-runs` | NO | M12 |
| `mcf-materialization.controller.ts` | `mcf/panel-runs` | NO | M12.5 |
| `mcf-publication-eligibility.controller.ts` | `mcf/metric-contracts` | **YES (`pe-mc-status`, `evaluate-pe-mc`)** | M13 |
| `mcf-publication-activation.controller.ts` | `mcf/metric-contract-versions` | NO | M14 |
| `mcf-mcv-supersede.controller.ts` | `mcf/metric-contract-versions` | NO | M15 |
| `mcf-mcv-abandon.controller.ts` | `mcf/metric-contract-versions` | NO | NO |
| `mcf-mcv-rebind.controller.ts` | `mcf/metric-contract-versions` | NO | NO |
| `mcf-mcv-fixture-append.controller.ts` | `mcf/metric-contract-versions` | NO | NO |
| `mcf-arpi-materialization.controller.ts` | `mcf/arpi-materialization` | NO | NO (D429 tag) |
| `mcf-role-grant.controller.ts` | `admin/mcf/role-grants` | NO | NO |
| `billing-volume-retry-unlock.controller.ts` | `mcf/ops` | NO | NO |
| `chain-audit.controller.ts` | `mcf/chain-audit` | NO | NO |
| `chain-enrichment.controller.ts` | `mcf/chain-enrichment` | NO | NO |
| `metric-authoring/` (no controller — service-only) | — | — | — |

**Net stage codes in HTTP paths: 2 (both in `mcf-publication-eligibility.controller.ts`).**
**Net stage codes in `@ApiTags`: 6 (in `MCF / M{11,12,12.5,13,14,15}` tags).**

---

## 6. Active Callers — Cross-Repo Sweep

### 6.1 bc-admin (active operator frontend)

| File:Line | Endpoint hit | Notes |
|---|---|---|
| `api/seed-metrics.ts:129` | `apiFetch('/mcf/intakes/from-seed', ...)` | ACTIVE — metric-intake creation from seed catalog. Path is **already semantic**. No alias work needed for this caller. |
| `api/mcf-catalog.ts:4` (JSDoc) | References `GET /api/mcf/metric-contracts` | ACTIVE — read endpoint. Path is semantic. No alias work needed. |
| `pages/MetricRegistrationPage.tsx:7` (JSDoc) | References `POST /mcf/intakes/from-seed` | ACTIVE caller of the seed intake endpoint. Semantic path. |

**bc-admin does NOT call the 2 PE-MC paths.** Confirmed via the sweep — only the SC/AC `/contracts/:id/versions/:v/activate` paths surface, which are **unrelated** (Source/Admission contract activation, not MCF M14).

### 6.2 bc-portal (customer frontend)

**Zero matches.** No `/api/mcf/` or `/api/bcf/` calls in bc-portal. The customer frontend does not consume MCF authoring endpoints.

### 6.3 bc-ai (Python HTTP clients)

| File:Line | Endpoint hit | Notes |
|---|---|---|
| `app/pipeline/panel_output_emitter.py:51` | `EMIT_PATH = "/api/bcf/panel-output-records"` | ACTIVE — BCF panel-output emission (registry-authoring, not MCF metric-authoring). **Path is semantic** (`panel-output-records`). No stage code. |
| `app/pipeline/panel_output_builder.py:121` (docstring) | References same path | ACTIVE — emission helper |
| `app/clients/bc_core_auth.py:8` (docstring) | References same path | ACTIVE — auth client |
| `tests/test_orchestrator_panel_emit.py:62`, `test_registry_authoring_panel.py:314` | Mock the same path | Test fixtures |

**bc-ai does NOT call any MCF path.** It only writes to the BCF panel-output-records endpoint (semantic).

### 6.4 Implication for the two PE-MC routes

**No external active caller exists for either `pe-mc-status` or `evaluate-pe-mc` in any of the three downstream repos.** The routes are exercised by:
- The controller's own unit spec
- Possibly the operator via Swagger UI / curl based on runbook documentation
- Active runbook DBCP chapters that document them as procedure steps

Per the operator's rule "If yes (bc-admin / bc-ai use the route), default to additive alias, not direct rename" — **the rule does NOT trigger for these two routes** because no bc-admin / bc-ai caller exists. Direct rename would be technically safe from a code-graph perspective.

**However:** Swagger UI, operator runbooks, and historical evidence files all reference the legacy path. Additive alias remains the safer choice to avoid surprising the operator who consults runbooks. Recommend **additive alias** despite the lack of cross-repo callers.

---

## 7. Scripts and Tests

### 7.1 Active operator-triggered scripts (potentially live)

| File:Line | What it does | Status assessment |
|---|---|---|
| `scripts/ipct-m12-retry.mjs:8,10` | `POST /api/mcf/panel-runs` with `allow_retry=true` for a given intake | **POSSIBLY ACTIVE** — this is an IPCT-pattern operator retry script. Not in `package.json` scripts but invocable manually. Path used (`/api/mcf/panel-runs`) is **already semantic** — no alias work needed. |

### 7.2 Historical scripts (HISTORICAL_ONE_SHOT per Sub-batch A precedent)

The MCF M11/M12/M14 scripts surveyed in earlier Layer 2b work (`mcf-m11-first-real-intake.mjs`, `mcf-m12-first-real-run.mjs`, `mcf-m14-unblock-apply.mjs`, etc.) reference `/api/mcf/panel-runs` and `/api/mcf/intakes` paths. All **semantic** — no stage code in URL. No alias work needed.

### 7.3 Tests asserting route paths

| Spec | Asserts |
|---|---|
| `mcf-publication-eligibility.controller.spec.ts:57,63,72` | 3 `it(...)` descriptions mirror `pe-mc-status` / `evaluate-pe-mc` (covered in §4) |
| Other MCF controller specs | Exercise routes but don't embed path strings in descriptions |

---

## 8. Operator-facing documentation references (bc-docs-v3)

**18 files** in `bc-docs-v3/docs/implementation/` reference `/api/mcf/` paths. Categorized:

### 8.1 Active runbook chapters

| File | Use |
|---|---|
| `mcf-re-entry-index.md` | Re-entry index — current operator-procedure document |
| `core-chain-golden-path.md` | Golden-path operating procedure |
| `chain-engines-design-packet-2026-06-15.md` | Chain engines design |
| `chain-engine-loop-milestone-2026-06-16.md` | Chain engine loop milestone |
| `mcf-readiness-bridge-writer-honesty-dbcp-2026-06-09.md` | MCF readiness bridge DBCP |
| `mcf-rebind-successor-governed-abandon-dbcp-2026-06-08.md` | MCV rebind/abandon DBCP |
| `mcf-gate0-seed-reservoir-dbcp.md` | MCF Gate-0 seed reservoir DBCP |
| `metric-context-framework-m14-invocation-surface-dbcp.md` | M14 invocation-surface DBCP |
| `mcf-role-grant-service-dbcp.md` | Role-grant service DBCP |

These chapters reference the routes as **current procedure**. Path renames in this batch would create doc-coherence cost — runbook chapters quoting `pe-mc-status` would become stale.

### 8.2 Historical / closeout DBCPs (HISTORICAL_ONE_SHOT)

`metric-context-framework-m14-unblock-apply-dbcp.md`, `metric-context-framework-service-ification-dbcp.md`, `platform-role-catalog-dbcp.md`, `pr-g2-first-service-surface-m12-authz.md`, `mcf-framework-audit-2026-06-22.md`, the MMS Layer 1/2 inventory chapters themselves — frozen evidence chapters.

---

## 9. Layer 3 Forward-Pointers (out of Layer 2d scope)

The two PE-MC route paths sit alongside **persisted Layer 3 artifacts** that share the same legacy stem:

| Artifact | Layer | Status |
|---|---|---|
| `metric_publication_eligibility_result.pe_check_code` (DB column) | Layer 3 | Persisted; Foundation III preserves |
| Enum values `'PE-MC-1' … 'PE-MC-12'` stored in that column | Layer 3 | Persisted historical rows |
| `PE_MC_CODES` TS array in `metric-publication-eligibility-evaluator.service.ts:163` | Layer 3 (variable holds the enum values) | Per Sub-batch B inventory recommendation, variable identifier + value move together in a future Layer 3 batch |
| Telemetry kind `'mcf_m12_*'`, `'mcf_m14_activation_eval'`, etc. | Layer 3 | Persisted in `ai_call_ledger` |
| Persisted `evaluator_version`, `verifier_version` values `'mcf-m13-v6'`, `'mcf-m14-v2'` | Layer 3 | Frozen on PE rows |
| `mcf-m12-5/` idempotency prefix value | Layer 3 | Frozen |

**Route-path rename does NOT require any Layer 3 value migration.** The two layers can move independently — the HTTP path token `pe-mc-status` is independent of the persisted enum value `'PE-MC-1'`.

---

## 10. Historical evidence — preserved per Foundation III

The audit-output directory contains 50+ references to MCF route paths across DBCPs and evidence files. All preserved.

Examples (not exhaustive):
- `scripts/audit-output/c1-trust-chain-derivation-dbcp-2026-06-10.md` — `GET /api/mcf/metric-contracts/<uid>` historical proofs
- `scripts/audit-output/d438-refactor-arc-audit-packet-2026-06-10.md` — full M11→M12→M12.5→M13→M14 happy-path procedure with route calls
- `scripts/audit-output/f1-a2-s2-*-dbcp-held-2026-06-14.md` (multiple files) — track-paid-customer-invoice-count seed flow procedure
- `scripts/audit-output/m12.5-filter-clause-materialization-packet-2026-06-13.md` — materialization preflight evidence
- `scripts/audit-output/mcf-gate0-liveproof-2026-06-07.json` — Gate-0 live proof JSON evidence
- `scripts/audit-output/pr-e1-readiness-2026-05-31T02-11-30Z.summary.md` — PR-E1 readiness table mapping endpoints to required roles + HTTP status codes
- `scripts/audit-output/pr-abandon-body.md`, `pr-billing-volume-retry-unlock-body.md`, `commit-msg-abandon.txt` — PR body drafts

All HISTORICAL_ONE_SHOT, preserved.

---

## 11. Risk Assessment

| Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|
| External operator using Swagger UI / curl on the legacy paths breaks after rename | MEDIUM | MEDIUM | Add semantic alias, keep legacy live during deprecation window |
| Runbook chapters referencing the legacy paths become stale | LOW | HIGH | Update runbook chapter language after alias is added; preserve original path for historical reference |
| Test descriptions referencing `pe-mc-status` / `evaluate-pe-mc` become stale | LOW | HIGH | Coherence update in same batch as alias addition (3 test descriptions) |
| Swagger `@ApiTags` rename surfaces in generated OpenAPI spec; downstream doc tools may rebuild against the new tag names | LOW | LOW | OpenAPI changelog entry; no wire-shape change |
| Generated OpenAPI spec changes break automated client SDK generation | LOW | LOW | No SDK generation currently in scope for these paths |
| Audit-output files referencing legacy paths become "stale" relative to current code | NONE | n/a | Historical evidence is **expected** to be frozen; not a risk |
| `ipct-m12-retry.mjs` script's path use breaks if `/api/mcf/panel-runs` is renamed | n/a | n/a | The script targets a **semantic** path; not in this batch's rename scope |

---

## 12. Recommended Batch Order (no execution authorized in this batch)

If the operator authorizes Layer 2d route-alias work, recommended sequencing:

### 12.1 Sub-batch L2d-1 — Two PE-MC route aliases (additive, recommended first)

**Scope:** add semantic alias `@Get('publication-eligibility-status')` alongside `@Get(':metricContractUid/pe-mc-status')`; same for the POST. Keep both routes live. Update 3 test descriptions. Risk: LOW. Estimated edits: 1 controller file (2 alias additions) + 1 spec file (3 description updates).

### 12.2 Sub-batch L2d-2 — Swagger `@ApiTags` rename (5 tags, direct rename)

**Scope:** rename 5 `@ApiTags` strings (`MCF / M11 Intake` → `MCF / Metric Intake`, etc.). Tags are documentation surface only; no wire-shape impact. Risk: LOW. Estimated edits: 5 controller files.

`mcf-mcv-supersede.controller.ts`'s tag is **already partially semantic** (`MCF / M15 Metric Supersession`) — only the M15 prefix is legacy. Decide whether to drop the prefix entirely or keep parenthetical `(legacy: M15)`.

### 12.3 Sub-batch L2d-3 — `@ApiOperation` summary strings (operator decision)

**Scope:** ~15 summary strings reference stage codes (`'Create operator-direct M11 intake'`, `'List M11 intakes ...'`, `'Read PE-MC evaluation results for an MC (PE-MC-1..10 rows)'`). These are operator-visible Swagger descriptions. Renaming is a Layer 1 operator-vocabulary concern — partially covered by Track 1+2 Layer 1 work earlier, but Swagger summaries were not specifically swept. Surface here so the operator can decide whether to fold into Layer 2d or treat as a Layer 1 follow-up.

### 12.4 Sub-batch L2d-4 — Legacy-alias retirement (deferred indefinitely)

**Scope:** after sufficient deprecation period, remove the legacy `pe-mc-status` / `evaluate-pe-mc` paths. **Not recommended within this Layer 2 program** — defer until external consumers (Swagger users, operator runbooks) have migrated.

### 12.5 Cross-batch invariants (apply to every Layer 2d batch)

- No DB writes. No persisted-value changes. Foundation Invariant III preserved.
- No bc-admin / bc-portal / bc-ai code changes — confirmed zero cross-repo callers for the affected paths.
- Each batch produces its own commit with `npm run typecheck` + `npx vitest run` over affected modules + Swagger spec regeneration if `@ApiTags` change.
- The two stuck MCV rows on `bc_platform_dev` remain untouched.
- Active runbook chapters in `bc-docs-v3` may need follow-up updates to reference the new path tokens — schedule separately as Layer 1 docs coherence.

---

## 13. Explicit No-Execution Statement

This document is **inventory and recommendation only**. No route was changed, no alias was added, no legacy path was removed, no test was modified, no Swagger decorator was edited, no script was touched, no PR was opened.

The two stuck MCV rows on `bc_platform_dev` are untouched.

Layer 2a (constants), Layer 2b (interfaces/methods/classes/sibling types), and Layer 2c (filename) are closed for the M12 Metric Draft Review semantic mapping. Layer 2d execution requires explicit operator authorization naming the sub-batch (L2d-1 / L2d-2 / L2d-3 / L2d-4).

### Cross-reference summary — Layer 2 program scope

| Tier | Surface | Status |
|---|---|---|
| 2a | M-stage constants + env-var family (deferred to Layer 3) | ✅ closed (M12/M12.5/M13/M14) |
| 2b — class | `M12PanelRunWriterService` | ✅ closed (Sub-batch A) |
| 2b — sibling types | 6 `M12*` sibling types in writer file | ✅ closed (Sub-batch B) |
| 2b — interfaces/methods | `M14ActivationGateInputs`, `M14PeRow`, `M15SupersessionGateInputs`, M13 method trio | ✅ closed (batches 2b #1/#2/#3) |
| 2c | Production filename + 8 import paths + 1 regex assertion | ✅ closed |
| **2d** | **HTTP route paths + Swagger labels (this inventory)** | **inventoried; awaiting authorization** |
| 3 | DB enum values, env-var keys, persisted version strings, JSON field names, telemetry kinds | deferred indefinitely |
