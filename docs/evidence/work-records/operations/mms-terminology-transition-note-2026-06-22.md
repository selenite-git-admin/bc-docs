---
title: "MMS Terminology Transition Note — Layer 1 Track 1 (Clusters A / B / C) complete"
description: "Operator-facing note: legacy workflow codes (M12 / M12.5 / M13 / PE-MC / M14 and related L-V / M11 codes) are now displayed with their semantic names in bc-admin and the metric-registration onboarding runbook. Legacy codes survive only as parenthetical aliases on first mention. No implementation identifiers, persisted codes, DB enums, telemetry keys, or historical evidence were touched."
date: 2026-06-22
project: bc-docs
domain: governance
subdomain: terminology
focus: transition-note
authority: reference
governing_adrs:
  - DEC-54f221 (Controlled Semantic Refactor — three-layer model; live authority)
  - DEC-7a1c98 (predecessor; superseded by DEC-54f221 on 2026-06-22)
parent_doctrine: ../operating-model/metric-management-system.md
references:
  - ../implementation/mms-layer1-interpretation-surfaces-inventory-2026-06-22.md
  - ../implementation/mcf-framework-audit-2026-06-22.md
  - ../implementation/mms-step2-operator-facing-docs-ui-labels-inventory-2026-06-22.md
---

# MMS Terminology Transition Note — Layer 1 Track 1 complete

**Effective:** 2026-06-22.
**Authority:** [ADR DEC-54f221 / D449](../../../governance/adrs/ADR-54f221.md) — Controlled Semantic Refactor, Layer 1 (Interpretation Surfaces).

## What changed

The five legacy workflow codes that operators saw most often in the catalog, registration, and onboarding runbook surfaces have been replaced with semantic names. Legacy codes still appear, but only as parenthetical aliases on first mention per page so that anyone who knew the old vocabulary can bridge to the new one without losing context.

| Legacy code | New semantic name |
|---|---|
| `M12` | **Metric Draft Review** |
| `M12.5` | **Metric Drafting** |
| `M13` | **Publication Review** |
| `PE-MC` | **Publication Eligibility checks** |
| `M14` | **Metric Activation** |

The same execution pass also surfaced related codes that share the same surfaces. They are renamed under the same pattern; the operator-facing inventory ([`mms-layer1-interpretation-surfaces-inventory-2026-06-22.md`](../implementation/mms-layer1-interpretation-surfaces-inventory-2026-06-22.md)) carries the per-occurrence detail.

| Legacy code | New semantic name | Note |
|---|---|---|
| `M11` | **Metric Intake** | Stage 1 in the MMS Creation Track; renamed for consistency. |
| `L-V1 / L-V2 / L-V3` | **Materialization Preconditions** (family) | Family-name rename only; per-code semantic naming deferred to a future verifier-portfolio pass. |

Codes deliberately **not renamed** in this pass — semantic names not yet locked:

- `M16` / `M17` / `M18+` (operator console family — semantic names pending)
- `M10` (verifier sub-stage — no authority-mapped name)
- `C-FX-*` family (fixture structural check codes — per-code naming deferred)
- `C1` / `C2` / `F1` / `F2` (BCF process names — per-code mapping deferred)

## Where the change is visible

| Surface | File(s) | What an operator sees |
|---|---|---|
| Metric Catalog page subtitle and aria-label | `bc-admin/src/pages/MetricCatalogPage.tsx` | "Metric Activation certificate present" aria-label and "Metric Draft Review panel (legacy: M12)" in the page subtitle. |
| Metric Detail page aria-label | `bc-admin/src/pages/MetricDetailPage.tsx` | "Metric Activation certificate present" aria-label next to the version code. |
| Metric Landscape page aria-label | `bc-admin/src/pages/MetricLandscapePage.tsx` | "Metric Activation certificate present" aria-label in the Activated column. |
| Register Metric page subtitle, paragraph copy, intake toast | `bc-admin/src/pages/MetricRegistrationPage.tsx` | "Metric Draft Review panel verification (legacy: M12)" subtitle; "The Metric Draft Review (Maker/Checker/Judge) panel is the verification step…" paragraph copy; "(queued — Metric Draft Review panel verifies next)" toast. |
| Metric Registration runbook prose | `bc-docs-v3/docs/onboarding/metric-registration.md` | Section heading "MCF Metric Drafting — new authoring path"; sub-section "Tenant runtime — unchanged during Metric Drafting"; per-stage list using "Metric Intake", "Metric Draft Review panel", "Metric Drafting materialization", "Publication Review", "Metric Activation"; "Materialization Preconditions" replacing the L-V family alias. |

## What was deliberately NOT changed

- **Implementation identifiers** — service / class / controller / module names (e.g. `MetricAuthoringMaterializationService`, `McfCertWriterService`, `MetricPublicationEligibilityEvaluatorService`, `M12PanelRunWriterService`). These are Layer 2 (Implementation Names) work under DEC-54f221 and are out of scope for Layer 1.
- **Source code comments and JSDoc** — Cluster D in the inventory. Approximately 5,000 occurrences across ~268 source files. Not executed in this pass.
- **Test descriptions and spec names** — Cluster E in the inventory (~1,025 occurrences across 85 test files, plus 2 test-file filename renames). Not executed.
- **bc-ai prompt files** — Cluster G in the inventory. Special handling: requires a regression discipline against baseline panel-run fixtures before any prompt rename. Gated; not executed.
- **Persisted compatibility names** — DB enum values, `governance_state_code`, `verdict_code`, `pe_check_code`, `action_code` values inside the database. These are Layer 3 (Compatibility Names) work and require a telemetry pre-inventory before opening. Untouched.
- **Telemetry keys, dashboard filter values, log emission keys** — Layer 3 territory. Untouched.
- **Historical audit artifacts** — filenames in `bc-docs-v3/docs/implementation/` carrying legacy codes (`mcf-m12-implementation-closeout.md`, `mcf-m13-implementation-closeout.md`, etc.). Preserved per Foundation Invariant III — historical evidence is never rewritten.
- **Decision identifiers** — `DEC-…`, `D…`, ADR UIDs. Explicitly preserved per DEC-54f221 Decision 1.

## Track / cluster status

- **Track 1 — operator-visible surfaces:** Cluster A (aria-labels) ✓, Cluster B (visible UI strings) ✓, Cluster C (runbook prose) ✓. **Complete.**
- **Track 2 — engineer-visible surfaces:** Cluster D (inline source comments) and Cluster E (test descriptions / spec names + 2 filename renames). **Not yet executed.**
- **Track 3 — bc-ai prompts:** Cluster G. **Gated on regression discipline** (baseline fixture import from bc-core's `ai_ledger.bcf_panel_runs`, then before/after panel comparison at `temperature=0` with ≥98% verdict-match threshold). **Not yet executed.**
- **Cluster F (backend error / log / toast / response strings):** **No-op for Layer 1.** The grep sweep confirmed zero matches in actual `throw` / `logger.*` / response-payload strings. Two substrate items (the `peCheckCode` enum constraint and a Python `_CHECKLIST_ITEM_KEYS` tuple) surfaced but belong to Layer 2 / Layer 3.

## Reading the parenthetical alias

When an operator-facing string carries `(legacy: M12)`, that is the **first-mention bridge** for that page or section. The same page will refer to the same concept without the parenthetical on subsequent mentions. The legacy code is preserved only as long as it carries traceability value; future cleanup passes may remove the parenthetical once the new name is established.

## What this note does NOT authorize

- Layer 2 (Implementation Names) rename — class / service / controller / route alias work.
- Layer 3 (Compatibility Names) migration — DB enums, telemetry keys, dashboard filter values, persisted codes.
- Cluster G bc-ai prompt rename — requires the regression discipline.
- Filesystem rename of historical audit artifacts.
- Any database write.

## Addendum — Cluster B visible-UI residuals resolved (2026-06-22)

After the Track 2 proof-batch (Cluster D + E) verification ran, three additional **visible bc-admin UI strings** were discovered that the original Cluster B inventory had miscategorized as inline comments. They were corrected the same day under a small Cluster B residual follow-up:

- `bc-admin/src/pages/MetricDetailPage.tsx` line 231 — rendered `<p>` text — **M12** → **Metric Draft Review (legacy: M12)**.
- `bc-admin/src/pages/MetricRegistrationPage.tsx` line 184 — `<DialogDescription>` rendered text — **M11** → **Metric Intake (legacy: M11)**.
- `bc-admin/src/pages/business-concepts/ProvenancePanel.tsx` line 200 — `<div>` rendered label — **Checklist (M1–M10)** → **Vocabulary Admission Checklist (legacy: M1–M10)**.

This completes the known bc-admin visible-UI Layer 1 cleanup.

Data fields, checklist item keys, implementation identifiers, and payload keys remain untouched — the per-checklist-item grid keys (`M1`/`M2`/…/`M10` rendered from runtime checklist data on `ProvenancePanel.tsx:205`), the `m14_activated` property name, the `f3_operation` field name, service / class / controller names, DB enums, telemetry keys, and persisted codes are all Layer 2 / Layer 3 territory and out of scope for this transition.

## Addendum — Track 2 complete (2026-06-22)

Layer 1 Track 2 (engineer-visible surfaces) is now complete alongside Track 1 (operator-visible surfaces). The seven Track 2 batches landed in this order: proof (D1+D2+D3+E1) → D4 → D5 → D6 → E2 → E3 → E4. Across bc-core, bc-admin, bc-portal, and bc-ai non-prompt source, source-code comments and JSDoc, test descriptions inside `describe('…')` / `it('…')` / `test('…')` / `context('…')` calls, and **two spec filenames** now use semantic vocabulary as the primary form with `(legacy: X)` or `; legacy: X` aliases on first meaningful mention per file.

Spec filename renames (E4, via `git mv`, history preserved):

- `bc-core/src/registry/metric-authoring/m12-panel-run-writer.service.spec.ts` → `metric-draft-review-panel-run-writer.service.spec.ts`
- `bc-core/src/registry/mcf/pe-mc-12-evaluation.spec.ts` → `publication-eligibility-check-12.spec.ts`

Production source files (`*.service.ts`, `*.controller.ts`, etc.) were NOT renamed. Only comments and test-descriptions inside them.

What this addendum does NOT authorize, restated for clarity:

- **No implementation classes / services / methods / module / controller / repository / function / variable identifiers** were renamed. `MetricAuthoringMaterializationService`, `McfCertWriterService`, `McfPublicationActivationController`, `M12PanelRunWriterService`, `m14_activated`, `f3_operation`, `mcf-m14-activate` runtime keys, and all similar identifier-shape symbols are preserved verbatim — these are Layer 2 (Implementation Names) territory per ADR DEC-54f221, operator-gated.
- **No persisted / DB / telemetry names** changed. DB enum values (e.g. `pe_check_code IN ('PE-MC-1', …, 'PE-MC-12')`), `governance_state_code` values, `verdict_code` values, `verifier_version` strings (`'mcf-m13-v2'`, `'mcf-m14-v2'`), index names (`idx_mcf_*`), CHECK constraint names (`mcf_cert_state_transition_chk`), telemetry payload keys, dashboard filter values — all preserved exactly. These are Layer 3 (Compatibility Names) territory per ADR DEC-54f221, operator-gated, and require a separate telemetry / log / dashboard pre-inventory before opening.
- **bc-ai prompt files** were NOT touched. The three registry-authoring prompts (`maker.md`, `checker.md`, `moderator.md`) referenced under `app/prompts/registry-authoring/v1.0/` remain unchanged. Prompt renames are Cluster G of Layer 1 — gated on a regression discipline (baseline fixture import from bc-core's `ai_ledger.bcf_panel_runs`, before/after panel comparison at `temperature=0`, ≥98% verdict-match threshold, byte-exact `f3_input` field equality, operator-authorized canary deployment). Independent track; not authorized by this addendum.

Verification across Track 2: zero TypeScript errors introduced (42 pre-existing baseline preserved throughout), zero vitest failures introduced, zero non-comment / non-test-description / non-filename changes detected by the identifier-integrity scan.

Layer 1 surfaces (Track 1 operator-visible + Track 2 engineer-visible) are now uniformly using semantic vocabulary with legacy aliases where traceability matters. Cluster G (bc-ai prompts) remains the only Layer 1 surface not yet under semantic vocabulary, gated on regression discipline.

## Cross-references

- **Authority:** [ADR DEC-54f221 / D449](../../../governance/adrs/ADR-54f221.md).
- **Expanded inventory (Layer 1 source-of-truth for surface-by-surface counts):** [`mms-layer1-interpretation-surfaces-inventory-2026-06-22.md`](../implementation/mms-layer1-interpretation-surfaces-inventory-2026-06-22.md).
- **Cluster A/B/C predecessor inventory:** [`mms-step2-operator-facing-docs-ui-labels-inventory-2026-06-22.md`](../implementation/mms-step2-operator-facing-docs-ui-labels-inventory-2026-06-22.md).
- **MMS doctrine:** [Metric Management System chapter](../../../operating-model/metric-management-system.md).
- **Foundational audit that drove the rename:** [`mcf-framework-audit-2026-06-22.md`](../../audits/implementation/mcf-framework-audit-2026-06-22.md).
