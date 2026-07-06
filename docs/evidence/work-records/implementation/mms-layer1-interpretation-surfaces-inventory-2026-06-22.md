---
uid: mms-layer1-interpretation-surfaces-inventory-2026-06-22
title: "MMS Layer 1 — Interpretation Surfaces — Expanded Inventory (Clusters A–G)"
description: "Read-only inventory of legacy workflow-code occurrences across the full Layer 1 (Interpretation Surfaces) surface under ADR DEC-54f221 / D449. Expands the prior Cluster A/B/C inventory (bc-admin aria-labels, bc-admin visible UI strings, onboarding runbook prose) with Cluster D (inline source comments), Cluster E (test descriptions / spec names), Cluster F (error / log / exception / backend toast strings), and Cluster G (bc-ai prompt files). Cluster G is special — model-input territory, gated on a regression discipline before any rename. Inventory captures file counts, occurrence counts, risk tiers, proposed replacement pattern, explicit exclusion list, and recommended execution sequence. NO renames performed."
status: draft
date: 2026-06-22
project: bc-docs
domain: contracts
subdomain: catalog
focus: mms-layer1-inventory
scope_locks: documentation-only; read-only sweeps; no substrate mutation; no runtime change; no code patch; no DB write; no bc-ai prompt edit; no test edit; no PR; no rename / refactor executed
parent_adr: ../adrs/ADR-54f221.md
predecessor_inventory: ./mms-step2-operator-facing-docs-ui-labels-inventory-2026-06-22.md
parent_doctrine: ../operating-model/metric-management-system.md
audit_pointer: ./mcf-framework-audit-2026-06-22.md
---

# MMS Layer 1 — Interpretation Surfaces — Expanded Inventory (Clusters A–G)

> **Authority pointer.** Filed under [ADR DEC-54f221 (D449)](../../../governance/adrs/ADR-54f221.md) (three-layer model: Interpretation Surfaces / Implementation Names / Compatibility Names). The prior [Step 2 inventory](mms-step2-operator-facing-docs-ui-labels-inventory-2026-06-22.md) covered Clusters A/B/C under DEC-7a1c98's six-step framing; that inventory remains valid as the Cluster A/B/C subset of Layer 1 and is referenced verbatim here. This document is the **expanded inventory** covering Clusters D, E, F, G — and consolidates the cross-cluster execution order under the new ADR.

## 1. Posture

This document **only inventories**. No renames executed. No code edits. No bc-ai prompt edits. No test edits. No DB writes. No runtime change. No business / platform substrate mutation. The two stuck Metric Contract Versions on `bc_platform_dev` are untouched.

Execution of any Layer 1 rename is a separate operator-authorized session that cites this inventory as input. Cluster G specifically cannot proceed without the regression discipline (§7 below) running green; even within an operator-authorized session.

## 2. Cluster definitions and boundaries

Layer 1 under DEC-54f221 covers all **Interpretation Surfaces** — human-readable text that conveys meaning to a reader. The seven clusters partition that surface:

| Cluster | Surface | What it means concretely | Boundary against adjacent clusters |
|---|---|---|---|
| **A** | bc-admin aria-labels | `aria-label="…"` attributes on JSX components | Distinct from B (visible text) — accessibility-only emission. |
| **B** | bc-admin visible UI strings | JSX paragraph copy, subtitles, toast/notification strings rendered by frontend components | Distinct from F (backend-emitted toast/error strings) — B is what bc-admin TSX renders; F is what bc-core / bc-ai code emits via throw / log / response payload. |
| **C** | Onboarding runbook prose | Chapter prose in `bc-docs-v3/docs/onboarding/` and section headings | Distinct from D (source comments) — C is operator-readable doctrine; D is code-internal. |
| **D** | Inline source comments | `//`, `/* */`, JSDoc, Python `#`, docstrings inside source files | Distinct from C (doctrine prose) — D is read by engineers, not operators. |
| **E** | Test descriptions / spec names | `describe('…')`, `it('…')`, `test('…')`, Python `def test_*`, fixture identifiers inside test files | Distinct from D — test-file filenames containing legacy codes are a **sub-category of E** (higher rename risk because filenames are addressed by CI tooling). |
| **F** | Backend error / log / toast / response strings | `throw new Error('…')`, `logger.{info,warn,error}('…')`, `raise ValueError('…')`, `res.status(N).json({ error: '…' })`, backend-emitted toast / detail / message payloads | Distinct from B (frontend JSX-rendered strings). Also distinct from D (comments). |
| **G** | bc-ai prompt files | `.md` system prompt files under `bc-ai/app/prompts/**` and `bc-ai/app/housekeeping/prompts/**` | Distinct from D — prompts are model input; renaming changes model interpretation, not just developer reading. Inline prompt strings in Python files would also be in G but the bc-ai layout uses file-based prompts exclusively. |

## 3. Authority and inputs

| Input | Role |
|---|---|
| [ADR DEC-54f221 (D449)](../../../governance/adrs/ADR-54f221.md) | Three-layer model — Layer 1 = Interpretation Surfaces. Layer 1 sub-cluster G (bc-ai prompts) is explicitly gated on regression discipline. |
| [Metric Management System chapter](../../../operating-model/metric-management-system.md) | Source of the semantic vocabulary that replaces the legacy codes. §6.1 stage names, §6.2 gate names, §6.3 artifact names. |
| [Metric Management System — Recovery Track chapter](../../../operating-model/metric-management-system-recovery-track.md) | Source of route names (R1–R8). |
| [MCF Framework Audit](../../audits/implementation/mcf-framework-audit-2026-06-22.md) §6.5, §7A | Evidence base for the rename. |
| [Prior Step 2 inventory](mms-step2-operator-facing-docs-ui-labels-inventory-2026-06-22.md) | A/B/C content preserved verbatim (this document does not restate the per-occurrence A/B/C tables). |
| [ADR DEC-7a1c98 (D448)](../../../governance/adrs/ADR-7a1c98.md) — superseded | Source of the legacy ↔ semantic mapping table §4 below. DEC-7a1c98 Decision 3's "inline source comments preserved" rule is **changed** under DEC-54f221 — comments are renamed at Layer 1 with transition-window annotation. |

## 4. Legacy → semantic mapping (re-stated from the Cluster A/B/C inventory)

| Legacy code | Semantic replacement | Notes |
|---|---|---|
| `M12` | Metric Draft Review | Stage 3 in MMS Creation Track. |
| `M12.5` | Metric Contract Materialization | Stage 4 in MMS Creation Track. |
| `M13` | Publication Eligibility Evaluation | Stage 6 in MMS Creation Track. |
| `M14` | Metric Activation | Stage 8 in MMS Creation Track. |
| `M15` | Metric Supersession | Stage 10 (cross-track touchpoint, Evolution Track). |
| `M11` | Metric Intake / Reservoir Ingestion | Stage 1. |
| `M16` / `M17` / `M18+` | **NOT YET LOCKED** | Operator console family; semantic names deferred. |
| `PE-MC-1` | G9 Provenance Grounding Gate | |
| `PE-MC-2`/3/4/6/7 | G2 Binding Integrity Gate (family merger) | |
| `PE-MC-5` | absorbed into G5 Self-Verification Gate | |
| `PE-MC-8` | retired from publication gating; relocated to Stage 9 Runtime Evaluation | |
| `PE-MC-9` | G8 Duplicate Intent Gate | |
| `PE-MC-10` | G5 Self-Verification Gate | |
| `PE-MC-11` | G3 Source-Chain Resolvability Gate | |
| `PE-MC-12` | G4 Source-Vocabulary Discipline Gate | |
| `L-V1*` (family) | Materialization Precondition checks (family name) | Per-code semantic naming **deferred** to verifier-portfolio work. |
| `C-FX-*` (family) | Fixture Structural Check codes (family name) | Per-code semantic naming deferred. |
| `B6` | Business Concept Draft Review | BCF stage. |
| `C5` | Operator Certification | BCF action. |
| `F3` | Registry Write / Registry Transition | BCF action. |
| `C1` / `C2` / `F1` / `F2` | **NOT YET LOCKED** | Per-code mapping deferred until BCF-side doctrine produces it. **Skipped from the D / E / F / G scans below** because the two-character codes are too generic for safe blanket grep; need targeted manual review. |

## 5. Proposed replacement pattern (Layer 1 universal rule)

For every occurrence renamed in Layer 1:

- **Semantic name primary**, in the position where the legacy code was.
- **Legacy code in parentheses** only on **first mention per file / page / paragraph context**, where downstream traceability is useful (e.g. an onboarding chapter that's the operator's first introduction to the concept). Form: `Metric Draft Review (legacy: M12)`.
- After first mention, subsequent uses are semantic-only.
- For source comments specifically (Cluster D): inline annotation `// legacy: M12` is permitted on the first source-line that references the concept; not required on every line.
- For tests (Cluster E): describe / it text uses semantic name only. The legacy code is not retained in test descriptions (test descriptions exist for grepping the rename target; preserving the legacy code defeats the purpose).
- For prompt files (Cluster G): replacement follows the regression-discipline outputs — exact substitution text is verified against the baseline, not pre-determined.

## 6. Cluster A/B/C — preserved subset of Layer 1

Per the [predecessor inventory](mms-step2-operator-facing-docs-ui-labels-inventory-2026-06-22.md), Clusters A/B/C are inventoried verbatim. Summary numbers:

| Cluster | Files | Occurrences | Risk tier |
|---|---|---|---|
| **A** — bc-admin aria-labels | 3 | 3 lines | Tier 1 — accessibility-only emission |
| **B** — bc-admin visible UI strings | 2 | 4 lines | Tier 1–2 — operator-visible on next page load; needs changelog |
| **C** — onboarding runbook prose | 1 | 11 lines in `metric-registration.md` | Tier 2 — section header rename requires anchor-link sweep |

No re-counting performed here. The predecessor inventory is the single source of truth for A/B/C per-occurrence tables.

## 7. Cluster D — Inline source comments

### 7.1 Top-line numbers

| Repo | Files with legacy-code comments | Occurrence count |
|---|---|---|
| bc-core/src | 245 | 4,959 |
| bc-admin/src | 12 | 47 |
| bc-portal/apps/web/src | 5 | 13 |
| bc-ai/ (Python `#` + docstrings) | 6 | 24 |
| barecount-devhub/src | 0 | 0 |
| **Total** | **268** | **5,043** |

> **False-positive caveat.** A separate sweep that included `bc-core/src/registry/seed/s4/*.json` raised the raw count to ~5,082 occurrences across 289 files. The additional ~2,500 occurrences are JSON-seed numeric data (SAP table catalog metadata where `M`-like patterns appear in source-system identifiers) — these are **not** workflow-code comments. The table above excludes JSON-seed data; the figure to use for execution planning is **~5,043 occurrences / 268 source files**.

### 7.2 Concentration

Comment occurrences are concentrated in the bc-core MCF service layer:

| File (bc-core/src) | Occurrences | Dominant code |
|---|---|---|
| `registry/mcf/metric-publication-eligibility-evaluator.service.ts` | 215 | PE-MC-1..PE-MC-12 |
| `registry/mcf/metric-publication-eligibility-evaluator.service.spec.ts` | 177 | PE-MC + M13 |
| `registry/mcf/mcf-publication-activation.controller.spec.ts` | 70 | M14 |
| `registry/mcf/metric-authoring-materialization.service.ts` | 68 | M12.5 + M13 + M14 |
| `registry/mcf/mcf-read.service.ts` | 63 | M12 + M13 |
| `registry/mcf/mcf-cert-writer.service.ts` | 61 | M4 + M13 |
| `registry/mcf/fixture-structural-check.service.spec.ts` | 57 | M9 + M10 |
| `registry/metric-authoring/m12-panel-run-writer.service.spec.ts` | 51 | M12 |
| `registry/metric-authoring/m12-panel-run-writer.service.ts` | 47 | M12 |
| `registry/mcf/metric-authoring-materialization.service.integration.spec.ts` | 47 | M13 |
| `registry/mcf/metric-authoring-materialization.service.spec.ts` | 44 | M13 + M14 |
| `registry/mcf/mcf-publication-activation.controller.ts` | 43 | M14 |
| `registry/mcf/fixture-structural-check.service.ts` | 36 | M9 |
| `registry/mcf/metric-authoring-panel.service.ts` | 35 | M12 |

Long tail: ~230 additional source files with 1–30 occurrences each, concentrated in MCF service layer (`mcf/*.ts`), database schema layer (`database/schema/mcf/`), boundary layer (`boundary/`), and registry authoring panel.

### 7.3 Comment-type breakdown

- **JSDoc file-headers** — typical pattern: `/** ... M13 unit tests. Authority: MCF M14/M12 governance DBCP ... */`. High frequency in `.spec.ts` files.
- **JSDoc method comments** — typical pattern: `/** Materialize an APPROVE_FOR_DRAFT panel proposal into MCF substrate. Mirrors L-V1c precondition. */`
- **Inline single-line comments** — typical pattern: `// M12 panel writer phase`, `// PE-MC-1 evaluator step`, `// L-V1e precondition check`.

### 7.4 Risk tier

**Tier 1 — cosmetic.** No comment found drives external API generation, doc-site generation, or code-logic behavior. Renaming is mechanical text substitution. The risk is reading clarity if the rename is incomplete; the mitigation is to do the rename as a single atomic pass per file (not file-by-file, but with a coherent replacement pattern).

### 7.5 Notes

- `C1` / `C2` / `F1` / `F2` were skipped in this scan as discussed in §4.
- `B6` / `C5` / `F3` matches found in bc-ai Python comments (3 files) — these are legitimate BCF context references.
- JSDoc references to **DBCP** identifiers (e.g. `DBCP §12.3`) are NOT workflow codes and are preserved.
- JSDoc references to **ADR** UIDs (e.g. `DEC-c3e57f`, `D414`) are explicitly not renamed per DEC-54f221 (decision identifiers preserved).

## 8. Cluster E — Test descriptions / spec names

### 8.1 Top-line numbers

| Repo | Test files with legacy codes | Occurrences |
|---|---|---|
| bc-core/src | 83 | 1,019 |
| bc-ai/tests/ | 2 | 6 |
| bc-admin/src | 0 | 0 |
| bc-portal | 0 | 0 |
| barecount-devhub | 0 | 0 |
| **Total** | **85** | **1,025** |

By code family:

| Family | Occurrences | Unique test files |
|---|---|---|
| M-track (M0–M20, M12.5) | 532 | 74 |
| PE-MC-* | 230 | 22 |
| L-V1* | 177 | 8 |
| C-FX-* | 86 | 9 |
| B6 / C5 / F3 in BCF context | 0 | 0 |

### 8.2 Test files with legacy codes IN THE FILENAME (sub-category — higher risk)

| File | Occurrences inside | Why higher risk |
|---|---|---|
| `bc-core/src/registry/metric-authoring/m12-panel-run-writer.service.spec.ts` | 51 | Filename addressed by `jest --testPathPattern`, CI dashboards, coverage reports |
| `bc-core/src/registry/mcf/pe-mc-12-evaluation.spec.ts` | 3 | Same |

Rename impact for these two files: filename rename requires CI workflow update (test-path patterns), coverage dashboard verification, and any grep-based test selection in scripts. **Treat these two as a separate sub-pass within Cluster E**, executed with explicit CI verification.

### 8.3 Top test files (by occurrence) — description-level rename

| File | Occurrences | Dominant code | Sample describe/it text |
|---|---|---|---|
| `mcf/metric-publication-eligibility-evaluator.service.spec.ts` | 183 | PE-MC-1..12 | `describe('PE-MC-12 evaluator gate', …)` |
| `m12-panel-run-writer.service.spec.ts` | 51 | M12 | `describe('M12PanelRunWriterService (real body)', …)` |
| `mcf/metric-authoring-materialization.service.integration.spec.ts` | 47 | L-V1 | `// L-V1c parity — mirrors the M12.5 materializer precondition` |
| `mcf/metric-authoring-materialization.service.spec.ts` | 42 + 93 | L-V1 + M13 | `it('does NOT call the M12.5 materializer …')` |
| `mcf/mcf-publication-activation.controller.spec.ts` | 40 + 34 | PE-MC-1 + M14 | `describe('McfPublicationActivationController — M14 unit tests …')` |

### 8.4 Risk tier

**Tier 1** for description-level rename (text in `describe('…')` / `it('…')`).
**Tier 2** for the 2 filename-level renames (m12-panel-run-writer, pe-mc-12-evaluation) because CI tooling pins on filenames.

### 8.5 Notes

- All 1,025 occurrences are confined to bc-core test files except 6 in bc-ai (documentation-style references in test docstrings, not test descriptions).
- bc-admin, bc-portal, barecount-devhub: zero matches in test files.
- No CI dashboard external integration depends on test description text (heuristic from grep of `package.json` test scripts and `.github/workflows/` if present).
- The 2 test-file filename renames need a single coordinated commit: rename file + update any `import` references + run `jest --listTests` to confirm CI selectors still resolve.

## 9. Cluster F — Backend error / log / toast / response strings

### 9.1 Top-line numbers

| Repo | Files with legacy-code strings | Occurrences |
|---|---|---|
| bc-core/src | 53 | ~95 |
| bc-admin/src | 7 | ~12 |
| bc-ai | 3 | ~5 |
| barecount-devhub/src | 0 | 0 |
| **Total** | **63** | **112** |

### 9.2 Critical finding — **Layer 1 surface is effectively empty for Cluster F**

A by-emission-type breakdown shows **zero** backend-emitted runtime strings contain legacy codes:

| Emission type | Occurrences |
|---|---|
| `throw new Error(...)`, `throw new TypeError(...)`, custom-error messages | **0** |
| `logger.{info,warn,error,debug}(...)`, `console.error/warn(...)` | **0** |
| Python `raise ValueError(...)`, `raise RuntimeError(...)` | **0** |
| `return { error: '...' }`, `res.status(N).json({ error: '...' })` | **0** |
| Backend-emitted toast / detail / message payloads | **0** |
| **Comments / docstrings / design-document anchors** (overlap with Cluster D) | 110 |
| **DB enum constant values** (SQL constraint string list) | 1 — `PE-MC-1..12` in `metric-publication-eligibility-result.ts:70` |
| **Python static constant tuple** | 1 — `_CHECKLIST_ITEM_KEYS = ("M1", "M2", ..., "M10")` in `registry_authoring_panel.py` |

### 9.3 The two non-comment items are NOT Layer 1

Both items are persistent constants whose surface is downstream:

| Item | Layer it belongs to | Why |
|---|---|---|
| `PE-MC-1` … `PE-MC-12` as values inside an SQL enum constraint (`peCheckCode IN (…)`) | **Layer 3 — Compatibility Names** | These are DB-persisted enum values. Renaming them changes the persisted shape and requires migration + dual-read + compatibility window per DEC-54f221's Layer 3 discipline. Out of scope for Layer 1 entirely. |
| `_CHECKLIST_ITEM_KEYS = ("M1", "M2", ..., "M10")` in `bc-ai/app/agents/registry_authoring_panel.py` line ~104 | **Layer 2 — Implementation Names** | Python identifier referenced by validation guards within bc-ai. Rename is a code change, not a comment / string change. Belongs to Layer 2. |

### 9.4 Operator-visibility scoring

Estimated **0%** of Layer-1-relevant Cluster F items reach operators. The 110 comment / docstring matches are pure code-internal; the two non-comment items are substrate (DB enum + Python identifier).

### 9.5 Risk tier

**Tier 0 — no Layer 1 work.** Cluster F under Layer 1 is empty. The 110 comment hits collapse into Cluster D (they were already counted there). The 2 substrate items are noted here as forward-pointers to Layer 2 / Layer 3 inventories.

### 9.6 Recommendation

Cluster F **does not require its own execution sub-pass** at Layer 1. Its only role in this inventory is the explicit cross-check: confirms that **no backend code emits legacy codes to operators today**, and surfaces the two substrate items for the Layer 2 / Layer 3 inventories.

## 10. Cluster G — bc-ai prompt files (special handling)

### 10.1 Top-line numbers

| Surface | Total | With legacy codes |
|---|---|---|
| bc-ai prompt files (`.md`) | 50 | 3 (genuine) + 2 (false positives) |
| Inline prompt strings in Python files | 0 | 0 |
| bc-ai fixture archive on disk | **None found** | n/a |

### 10.2 Genuine matches

| File | Role | Legacy codes referenced |
|---|---|---|
| `bc-ai/app/prompts/registry-authoring/v1.0/maker.md` | system prompt — Maker agent | B6 (BCF panel ID), F3 (service method), M1–M10 (vocabulary admission checklist) |
| `bc-ai/app/prompts/registry-authoring/v1.0/moderator.md` | system prompt — Moderator / Judge | B6, F3, M1–M10 |
| `bc-ai/app/prompts/registry-authoring/v1.0/checker.md` | system prompt — Checker agent | B6, F3, M1–M10 |

### 10.3 False positives flagged (no rename)

| File | Match | Why it's a false positive |
|---|---|---|
| `bc-ai/app/prompts/kpi-ask/v1.0/composer.md` line 31 | "C1" | Example of variable naming convention ("I1, I2, C1, O1") — not a workflow code. |
| `bc-ai/app/housekeeping/prompts/mkdocs-maintainer/v1.0/reasoner.md` lines 6–7 | F01–F06, P01–P10, C01–C02 | Documentation-site nav codes (Foundation, Platform, Common) — not workflow codes. |

### 10.4 Critical sub-finding — M1–M10 may be functioning as positional signals

The Maker prompt's M1–M10 references are the **Vocabulary Admission Checklist** — the model is instructed to "answer every MUST (M1–M10)". The Checker independently attacks the same checklist; the Moderator verifies each item passes. The ordinal sequence M1 → M10 may be functioning as a **learned positional anchor** for the model: it's not just a label, it's a sequence count that organizes the verification ritual.

Renaming M1–M10 to e.g. "VOCAB-CHECK-01" through "VOCAB-CHECK-10" preserves the ordinal signal. Renaming to non-positional names (e.g. semantic per-criterion names like "Entity Identity Check", "Characteristic Uniqueness Check") would lose the ordinal signal. Either path is possible, but the regression discipline must measure the consequence — this is the centerpiece of Cluster G safety.

### 10.5 Fixture infrastructure — does not exist in bc-ai

bc-ai has **no fixture archive on disk**. Prior panel-run outputs are posted to bc-core's telemetry endpoint (`/api/ai-telemetry/bcf-panel-run/from-summary`) and persisted in bc-core's `ai_ledger.bcf_panel_runs` table. No local copy is retained.

Implication: the regression discipline must include a **fixture-import step** that pulls a representative sample from bc-core's ledger into `bc-ai/fixtures/registry-authoring-baseline-{date}.jsonl` before any prompt edit.

### 10.6 Proposed regression discipline — four phases

**Phase 1 — Baseline capture (BEFORE any prompt edit).**
1. Query bc-core's `ai_ledger.bcf_panel_runs` for the last 30–60 days of registry-authoring panel runs (or the most recent complete admission wave).
2. Export each run as a fixture row: `{input_context, maker_output, checker_output, moderator_verdict, confidence, reasoning_text}`. Save to `bc-ai/fixtures/registry-authoring-baseline-{date}.jsonl`.
3. Tag the bc-ai git ref before any prompt edit: `legacy-codes-baseline-2026-06-22`.
4. Record baseline metrics: verdict distribution (counts by code), confidence distribution, reasoning length distribution.

**Phase 2 — Prompt rewrite on a feature branch.**
1. Scope strictly to the three registry-authoring prompt files.
2. Mechanical substitution per the §5 replacement pattern. The actual new names are operator-specified — see §10.7 below for the recommendation.
3. Single feature-branch commit covering all three prompt files.
4. Do NOT merge yet.

**Phase 3 — Regression run.**
1. Set all panel LLM calls to `temperature=0` for determinism on both old and new sides of the comparison.
2. For each baseline fixture: invoke Maker / Checker / Moderator with the REWRITTEN prompts. Capture outputs.
3. Compute per-fixture deltas:
   - **Verdict code match** — exact match required. Threshold: ≥98% agreement across fixtures; 100% on `APPROVE_FOR_DRAFT` verdicts (rejecting an accepted item, or accepting a rejected item, is a hard failure).
   - **Structured-field equality** — `f3_input` JSON (entity_name, characteristic_id, representation_term, data_type, semantic_role) must be byte-exact match per fixture.
   - **Confidence delta** — `|new − baseline| ≤ 0.05` per fixture.
   - **Reasoning length** — `|new − baseline| / baseline ≤ 0.10` per fixture.
   - **Risk flag set** — new flag set must equal baseline flag set (additions OK if justified; removals are a hard failure).
4. Human spot-check 5–10 reasoning texts for coherence (not garbled, not misdirected to a different task).
5. Stochastic source: if non-determinism is unavoidable (model routing, sampling), run each fixture N=3 times and report median verdict + std deviation. Document the source.

**Phase 4 — Canary + roll-out.**
1. Deploy to staging. Run a new wave of registry-authoring panels (same candidate set as baseline). Compare staging outputs vs. feature-branch regression outputs.
2. Exit criterion for full roll-out: ≥95% verdict agreement between staging-fresh-runs and feature-branch regression-runs.
3. Merge to main. Monitor verdict distributions in bc-core telemetry for the week following deployment.

### 10.7 Naming recommendation for Cluster G

Three sub-decisions, each with the regression discipline as the gating mechanism:

- **B6** → rename to "BCF Registry Authoring Panel" (semantic) with `(legacy: B6)` parenthetical on first mention per prompt file. Low semantic-shift risk because B6 is a panel-ID anchor, not a verbal action.
- **F3** → rename to "Registry Write" / "Registry Transition" per the §4 mapping. The prompt currently says "F3 service method" (Maker line 12; Moderator lines 33–39) which gives the model a positional anchor that may be load-bearing — flagged for the regression discipline to measure.
- **M1–M10 (Vocabulary Admission Checklist)** — **preserve the ordinal-N suffix**, rename only the prefix: `M1` → `VOCAB-CHECK-01`, `M2` → `VOCAB-CHECK-02`, …, `M10` → `VOCAB-CHECK-10`. This preserves the positional anchor while removing the opaque "M" prefix. Alternative — full semantic per-criterion rename ("Entity Identity Check", "Characteristic Uniqueness Check", etc.) — is rejected because it loses the ordinal signal; the regression discipline would likely flag verdict drift.

### 10.8 Risk tier

**Tier 4 — model behavior.** Explicit per DEC-54f221. Cluster G CANNOT proceed without the regression discipline (Phase 1–4 above) running green.

## 11. Explicit exclusion list (out of scope for Layer 1)

The following are explicitly excluded from this inventory and from any Layer 1 rename:

| Surface | Why excluded | Belongs to |
|---|---|---|
| **Historical audit artifacts** in `bc-docs-v3/docs/implementation/` (e.g. `mcf-m12-implementation-closeout.md`, `mcf-m13-implementation-closeout.md`, etc.) | Foundation Invariant III — historical evidence is never rewritten. | Permanently excluded (preserved per Invariant III) |
| **Persisted database rows** — `mcf.*`, `metric.*`, `contract.*` columns containing legacy codes (e.g. `governance_state_code`, `verdict_code`, `pe_check_code`, `action_code` values) | Layer 3 territory (Compatibility Names). Renaming is additive-only with telemetry pre-inventory per DEC-54f221. | Layer 3 |
| **DB enum CHECK constraint values** (e.g. `peCheckCode IN ('PE-MC-1', …, 'PE-MC-12')` in `metric-publication-eligibility-result.ts:70`) | Same as above — DB-persisted. | Layer 3 |
| **Telemetry keys / dashboard filter values / log emission keys** | Layer 3 territory — requires the pre-inventory step listed in DEC-54f221. | Layer 3 (pre-inventory not yet performed) |
| **Code identifiers** — class names, service names, controller filenames, route alias variables, non-persisted symbols (e.g. `M12PanelRunWriterService`, `McfPublicationActivationController`, `metricAuthoringPanelService`) | Layer 2 territory (Implementation Names). | Layer 2 |
| **HTTP route paths** (e.g. `/api/mcf/metric-contract-versions/:uid/m13-evaluate`) | Layer 2 (internal aliases) / Layer 3 (external-facing route deprecation). | Layer 2 + Layer 3 |
| **Per-metric controller quarantine** (e.g. `mcf-arpi-materialization.controller.ts`, `billing-volume-retry-unlock/`) | Layer 2 territory. | Layer 2 |
| **Decision identifiers** (`DEC-…`, `D-…`, ADR UIDs) | Explicitly preserved per DEC-54f221 Decision 1 (UID continuity). | Permanently preserved |
| **JSON seed data** (`bc-core/src/registry/seed/s4/*.json`) where M-like patterns appear in source-system identifiers | Not workflow codes; false positives. | Not in scope at any layer |
| **C1 / C2 / F1 / F2 codes** | Per DEC-54f221 (and predecessor DEC-7a1c98 Decision 6.4) — semantic naming not yet locked. Skipped from all D/E/F/G grep scans because two-char codes generate too many false positives. | Deferred to a future inventory pass after the per-code mapping lands |
| **M16 / M17 / M18+** | Per §4 mapping — semantic names not yet locked. Flagged in §6 (preserved A/B/C inventory) for follow-up. | Deferred |
| **bc-ai prompt false positives** (`kpi-ask/composer.md` C1 example; `mkdocs-maintainer` F01–F06 nav codes) | Not workflow codes. | Not in scope |

## 12. Cross-cluster risk and execution-order analysis

| Cluster | Files | Occurrences | Risk tier | Operator visibility | Blast radius | Prerequisite |
|---|---|---|---|---|---|---|
| A — aria-labels | 3 | 3 | Tier 1 | Screen-reader only | Smallest | none |
| B — bc-admin visible UI strings | 2 | 4 | Tier 1–2 | Yes — next page load | Small | Changelog discipline |
| C — onboarding runbook prose | 1 | 11 | Tier 2 | Yes — reading the chapter | Medium (section header anchors) | Anchor-link sweep |
| D — inline source comments | 268 source files | ~5,043 | Tier 1 | Engineer-only | Largest (volume) | none |
| E — test descriptions | 85 | 1,025 | Tier 1 (descriptions), Tier 2 (2 filenames) | CI dashboards if filenames | Medium (CI integration for 2 filenames) | Filename rename = CI selector verification |
| F — backend strings | 0 (Layer-1-relevant) | 0 (Layer-1-relevant) | Tier 0 | n/a | None | n/a — no work |
| G — bc-ai prompts | 3 | ~30 across 3 files (M1–M10 × 3 + B6 × 3 + F3 × 3 + scattered) | **Tier 4** | Indirect (model outputs) | Bounded but model-behavior risk | **Regression discipline (§10.6) green** |

### 12.1 Should Cluster A still be first?

**Yes — Cluster A remains the recommended first execution sub-pass.** Three reasons:

1. **Smallest blast radius** — 3 lines across 3 files; aria-label-only emission; immediately reversible at the prop layer; no cross-file dependencies.
2. **Accessibility wins, no operator-visible regression** — screen-reader announcements become more descriptive (e.g. "Metric Activation certificate present" reads more naturally than "M14 activation certificate present").
3. **Builds rename muscle for the team** — a small first pass is a safe place to validate the §5 replacement pattern before applying it at scale in D/E.

The expanded clusters (D, E, G) do not displace A; they add **parallel tracks**.

### 12.2 Recommended overall execution order

Three parallel tracks; G runs on its own gated track.

**Track 1 — Operator-visible surfaces (serial).**
1. Cluster A (aria-labels). Single small commit. Reversible.
2. Cluster B (bc-admin subtitle / paragraph / toast strings). Bundle with operator changelog entry.
3. Cluster C (`metric-registration.md` runbook prose). Include anchor-link sweep across `bc-docs-v3/` in the same commit.

**Track 2 — Engineer-visible surfaces (parallel to Track 1; can start immediately).**
4. Cluster D (inline source comments). Bulk mechanical rewrite, file-by-file, atomic per file. Recommend automated tooling (a small node script that walks the legacy ↔ semantic mapping per §4 and rewrites comment text) — but the script itself is OUT of scope of this inventory.
5. Cluster E description-level rename — concurrent with D. Same automated rewrite tooling can cover both.
6. Cluster E filename rename (2 files) — separate sub-commit per filename, with CI verification before merge. Should be the LAST sub-pass within Track 2.

**Track 3 — bc-ai prompts (gated; runs independently on its own schedule).**
7. Cluster G — only after the regression discipline (§10.6 Phase 1) baseline fixture import completes. Then Phase 2–4 in sequence on a feature branch. **Cannot start without the fixture import step.**

**Cluster F** has no Layer 1 work. Its two substrate items (PE-MC enum, Python tuple) are noted for the Layer 2 / Layer 3 inventories — not for Layer 1.

### 12.3 Bundling guidance

- **A + B + C** as a single operator-visible release — yes, if changelog can carry all three.
- **D + E (descriptions)** as a single engineer-visible mass commit — yes, mechanical and Tier 1.
- **E (filenames) separately** — yes, isolate the CI risk.
- **G strictly separate** — never bundle with anything else.

## 13. Open questions for operator

1. **Replacement-pattern verification.** §5 sets "semantic name primary, legacy code in parentheses on first mention." Confirm this applies to all four new clusters (D / E / F / G), or whether D (engineer-visible) should drop the parenthetical entirely after the rewrite. **Inventory recommendation:** keep the parenthetical for the first 60–90 days post-rename as a transition-window aid; remove during a follow-up cleanup.
2. **Cluster D automated tooling.** A small node script can handle the bulk rewrite. Should this inventory specify the script's invocation surface, or leave it to the execution session to author? **Inventory recommendation:** leave to execution session — the script is small and the mapping is in §4.
3. **Cluster E filename rename CI verification.** What CI verification gate is required before merging the `m12-panel-run-writer.service.spec.ts` → `metric-draft-review-panel-run-writer.service.spec.ts` rename? **Inventory recommendation:** (a) `jest --listTests` shows the new filename; (b) full test suite passes; (c) any grep-based test selection scripts in `package.json` or `.github/workflows/` are updated in the same commit.
4. **Cluster G fixture import scope.** How many baseline panel runs are needed for statistical confidence? §10.6 Phase 1 suggests "30–60 days" but the actual count matters more. **Inventory recommendation:** target N≥100 distinct panel runs covering both APPROVE and REJECT verdicts.
5. **Cluster G temperature determinism.** Confirm `temperature=0` is acceptable for both baseline capture and regression runs, or whether the baseline must be sampled at the production temperature for fidelity. **Inventory recommendation:** `temperature=0` for the comparison (removes noise); production temperature stays unchanged for live operation.
6. **C1 / C2 / F1 / F2 and M16 / M17 / M18+ deferred mapping.** These remain unmapped. Should a separate ADR follow-up be filed to lock the names, or wait for natural emergence? **Inventory recommendation:** defer; no urgency; flag for follow-up when the next BCF / MCF operator-console doctrine pass lands.

## 14. Scope honoured

- Documentation-only edit (this file created; the predecessor A/B/C inventory unchanged).
- Read-only sweeps across `bc-core/src/`, `bc-admin/src/`, `bc-portal/apps/web/src/`, `bc-ai/`, `barecount-devhub/src/`.
- No bc-ai prompt edits.
- No test edits.
- No code patch (other than this inventory document).
- No DB writes.
- No DevHub decision mutation.
- No business / platform substrate mutation.
- No runtime / service restart.
- No PR.
- **No rename executed.** This inventory is the input to a future execution session.
- The two stuck Metric Contract Versions on `bc_platform_dev` are untouched.
- The MCF substrate (`mcf.*` schema, `bc-core/src/registry/mcf/` code surfaces) is untouched at the substrate level.

## 15. Stop condition

Inventory complete. Locked next-step sequence (operator-gated; nothing starts without explicit authorization):

1. **Operator review of this inventory** and the open questions in §13.
2. **Cluster A execution** (aria-labels) — recommended first sub-pass per §12.
3. **Cluster B + C execution** (operator-visible UI text + runbook prose) — Track 1 continuation.
4. **Cluster D + E (descriptions) execution** — Track 2 in parallel.
5. **Cluster E filename rename** — last sub-pass within Track 2, with CI verification.
6. **Cluster G — Phase 1 fixture import** — Track 3 starts here. Cannot proceed to Phase 2 (prompt rewrite) until baseline is in place.
7. **Cluster G — Phase 2 / 3 / 4** — sequenced per §10.6, with the regression discipline as the merge gate.
8. **Layer 2 (Implementation Names)** opens after Layer 1 reaches material completion. Layer 3 (Compatibility Names) opens after the telemetry / log / dashboard pre-inventory completes per DEC-54f221.

Nothing in Layer 2 or Layer 3 is authorized by this inventory.
