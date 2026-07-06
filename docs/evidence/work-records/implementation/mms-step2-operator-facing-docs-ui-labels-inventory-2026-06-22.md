---
uid: mms-step2-operator-facing-docs-ui-labels-inventory-2026-06-22
title: "MMS Step 2 — Operator-Facing Docs + UI Labels Rename Inventory"
description: "Read-only inventory of legacy workflow-code occurrences in operator-facing surfaces — runbook chapters in bc-docs-v3/docs/onboarding/, bc-admin UI strings (aria-labels, subtitles, paragraph copy, toast messages), audit-artifact filenames in bc-docs-v3/docs/implementation/. Step 2 of the Controlled Semantic Refactor (per ADR DEC-7a1c98 Decision 4). This inventory captures what needs renaming, the proposed semantic replacement per occurrence, the in-scope vs out-of-scope discipline (inline source comments remain legacy per Decision 3; historical audit-artifact filenames are never rewritten per Foundation Invariant III), and a recommended execution order. NO renames are performed by this inventory; execution requires a separate operator-authorized session."
status: draft
date: 2026-06-22
project: bc-docs
domain: contracts
subdomain: catalog
focus: mms-step2-inventory
scope_locks: documentation-only; read-only sweeps; no substrate mutation; no runtime change; no code patch; no DB write; no PR; no rename / refactor executed
parent_adr: ../adrs/ADR-54f221.md
predecessor_adr: ../adrs/ADR-7a1c98.md (superseded by DEC-54f221 on 2026-06-22; this inventory was authored against DEC-7a1c98's Step 2 framing and remains valid as the subset covering Layer 1 Clusters A/B/C under DEC-54f221)
parent_doctrine: ../operating-model/metric-management-system.md
audit_pointer: ./mcf-framework-audit-2026-06-22.md
---

# MMS Step 2 — Operator-Facing Docs + UI Labels Rename Inventory

> **Authority pointer (added 2026-06-22).** This inventory was authored against the Step 2 framing of [DEC-7a1c98](../../../governance/adrs/ADR-7a1c98.md), which was superseded the same day by **[DEC-54f221 / D449](../../../governance/adrs/ADR-54f221.md)**. Under DEC-54f221's three-layer model, this inventory's scope (`bc-docs-v3/docs/onboarding/` runbook prose + bc-admin UI strings + historical audit-artifact filenames) is the **Cluster A/B/C subset of Layer 1 (Interpretation Surfaces)**. The full Layer 1 surface under DEC-54f221 is broader — it also includes inline source comments, test descriptions, error messages, generated operator reports, developer docs, and the gated bc-ai prompt sub-cluster — recorded here as **Clusters D / E / F / G** which will need their own inventory pass before Layer 1 execution opens. The "Inline comments preserved per ADR Decision 3" rule cited below in §3 and §5.2 is **changed** under DEC-54f221 (Decision: inline comments are renamed at Layer 1 with transition-window annotation only) — those references are preserved as historical context; the live discipline is DEC-54f221.

## 1. Purpose and posture

This is the **inventory phase** of Step 2 of the Controlled Semantic Refactor sequence locked by [ADR DEC-7a1c98](../../../governance/adrs/ADR-7a1c98.md) Decision 4. Per that ADR's Decision 4 Step 2 description:

> *"Rename runbook chapter titles in `bc-docs-v3/docs/onboarding/`, operator console labels, audit-artifact filenames (new artifacts only — historical artifact filenames are never rewritten per Foundation Invariant III), and the bc-admin Metric Lifecycle / Metric Chain surface labels. UI rename is operator-visible but reversible at the label layer."*

This document **only inventories** the surfaces that fall under Step 2. It does not perform any rename. Execution of the renames is a separate operator-authorized session that cites this inventory as input. Until that session opens, the surfaces below remain as they are today.

The inventory is structured to answer four questions for the operator before any execution:

1. **What needs renaming?** (per-surface, per-file, per-line)
2. **What is the proposed semantic replacement?** (per occurrence, drawn from [ADR DEC-7a1c98 Decision 6](../../../governance/adrs/ADR-7a1c98.md) mapping)
3. **What is explicitly OUT of scope under Step 2?** (inline source comments per ADR Decision 3; historical audit-artifact filenames per Foundation Invariant III; code identifiers / route names / DB enums per Steps 3–5)
4. **What risk / order of execution does the operator need to consider?**

## 2. Authority and inputs

| Input | Role |
|---|---|
| [ADR DEC-7a1c98](../../../governance/adrs/ADR-7a1c98.md) | The Vocabulary Lock. Decision 4 names the six-step sequence; Decision 6 carries the legacy ↔ semantic mapping this inventory uses. |
| [Metric Management System chapter](../../../operating-model/metric-management-system.md) | Source of the semantic vocabulary that replaces the legacy codes. §6.1 stage names, §6.2 gate names, §6.3 artifact names. |
| [Recovery Track chapter](../../../operating-model/metric-management-system-recovery-track.md) | Source of route names (R1–R8) — relevant where operator-facing copy refers to recovery actions. |
| [Audit](../../audits/implementation/mcf-framework-audit-2026-06-22.md) §6.5, §7A.3 | Evidence for why Step 2 exists; §7A.3 step 2 is the canonical authority. |

## 3. Scope discipline (per ADR Decision 3 + Decision 4)

**IN scope for Step 2 renames:**

- Operator-facing **UI strings** rendered by bc-admin — paragraph copy, subtitles, aria-label attributes, toast / notification messages.
- Operator-facing **runbook chapter prose** in `bc-docs-v3/docs/onboarding/` (chapter headings, paragraph copy, table cells).
- **New** audit-artifact filenames authored after ADR filing date 2026-06-22.
- bc-admin **route page titles** (the human-readable title in the page header), where they currently embed legacy codes. **Note: the actual URL route paths are Step 4 work, not Step 2.** Step 2 covers visible page-title text; Step 4 covers the URL alias.

**OUT of scope under Step 2 (deferred or excluded entirely):**

- **Inline source code comments** in `bc-admin/src/` (and elsewhere) that mention legacy codes. Per ADR Decision 3, inline comments are an explicitly allowed alias context. They are NOT renamed under Step 2. They may be renamed during Step 3 (code identifiers) at the engineer's option, with `// legacy: M12` style annotation, but Step 2 leaves them alone.
- **Historical audit-artifact filenames** already filed in `bc-docs-v3/docs/implementation/` (e.g. `mcf-m12-implementation-closeout.md`, `mcf-m13-implementation-closeout.md`, etc.). Per Foundation Invariant III, historical artifact filenames are never rewritten. Inventory surface 5.3 records them as "preserved" rather than "to rename."
- **Code identifiers / class names / service names / controller filenames** in `bc-admin/src/` and `bc-core/src/`. These are Step 3 work.
- **HTTP route URL paths** (e.g. `/api/mcf/metric-contract-versions/:uid/abandon`). These are Step 4 work.
- **Database enum values, persisted-code aliases** (`governance_state_code`, `verdict_code`, `pe_check_code`, `action_code`). These are Step 5 work.
- **Per-metric controllers** (`mcf-arpi-materialization.controller.ts`, `billing-volume-retry-unlock/`). Step 6.
- **Persisted historical evidence** — database rows, log rows, audit-row metadata. Never rewritten per Invariant III, regardless of step.

## 4. Legacy → semantic mapping reference

Drawn from [ADR DEC-7a1c98 Decision 6](../../../governance/adrs/ADR-7a1c98.md). The inventory below uses this table as the replacement source.

| Legacy code | Semantic replacement | Notes |
|---|---|---|
| `M12` | Metric Draft Review | Stage 3 in MMS Creation Track. |
| `M12.5` | Metric Contract Materialization | Stage 4 in MMS Creation Track. |
| `M13` | Publication Eligibility Evaluation | Stage 6 in MMS Creation Track. |
| `M14` | Metric Activation | Stage 8 in MMS Creation Track. |
| `M15` | Metric Supersession | Stage 10 cross-track touchpoint (owned by Evolution Track). |
| `M11` | Reservoir Ingestion / Metric Intake | Per MMS Stage 1 (Metric Intake) — note: M11 was the substrate gate; the operator-facing semantic is "intake" or "register". |
| `M16`, `M17`, `M18+` | **Semantic name NOT YET LOCKED** | These are the operator console family per Audit §6.4. Their semantic names are not in ADR Decision 6's mapping table. Inventory flags them; rename is deferred until names are locked in a follow-up. |
| `PE-MC-1` | G9 Provenance Grounding Gate | Promoted gate. |
| `PE-MC-2`/3/4/6/7 | merged into G2 Binding Integrity Gate | Family merger. |
| `PE-MC-5` | absorbed into G5 Self-Verification Gate | Fixture-presence sub-check. |
| `PE-MC-8` | **retired from publication gating**; relocated to Stage 9 Runtime Evaluation | Operator-facing copy referencing PE-MC-8 should remove the gate reference entirely. |
| `PE-MC-9` | G8 Duplicate Intent Gate | Renamed; predicate preserved. |
| `PE-MC-10` | G5 Self-Verification Gate | Renamed; absorbs PE-MC-5. |
| `PE-MC-11` | G3 Source-Chain Resolvability Gate | Renamed; predicate preserved. |
| `PE-MC-12` | G4 Source-Vocabulary Discipline Gate | Renamed; predicate preserved. |
| `L-V1*` (family) | **Materialization Precondition checks** (family name) | Per-code semantic naming **deferred** to verifier-portfolio work (Audit §6.4). Operator-facing copy uses the family name "Materialization Precondition check" with the legacy `L-V1*` in parentheses on first mention. |
| `C-FX-*` (family) | **Fixture Structural Check codes** (family name) | Per-code semantic naming deferred. Same family-name + parenthetical pattern. |
| `B6` | Business Concept Draft Review | BCF stage. |
| `C5` | Operator Certification | BCF action. |
| `F3` | Registry Write / Registry Transition | BCF action. |
| `C1`, `C2`, `F1`, `F2` (process-name uses) | **Semantic naming NOT YET LOCKED** | Per ADR Decision 6.4, per-code mapping deferred until BCF-side doctrine produces it. Inventory flags them; the same letters used as in-document section identifiers inside ADRs and chapters are out of scope. |

## 5. Surface inventory

### 5.1 Operator runbook prose — `bc-docs-v3/docs/onboarding/`

**Files swept:** 19 chapters under `bc-docs-v3/docs/onboarding/` (excluding the `metric-work-records/` directory which contains session-work records, not runbooks).

**Files with legacy code occurrences:** **1 chapter** — `metric-registration.md` only. The other 18 onboarding chapters carry no legacy workflow-code references at the prose level.

**Per-occurrence inventory in `metric-registration.md`:**

| Line | Current text (verbatim, abridged) | Legacy codes | Proposed semantic replacement |
|---|---|---|---|
| 240 | `## MCF M12.5 — new authoring path (operator runbook addition)` | `M12.5` | `## MCF Metric Contract Materialization — new authoring path (operator runbook addition)` — preserve "MCF" qualifier per Decision 5 (MCF is the grammar layer name). |
| 242 | `**Added per M12.5 PR-2 (DBCP §12.3 operator runbook update).**` | `M12.5` | `**Added per Metric Contract Materialization PR-2 (DBCP §12.3 operator runbook update).**` |
| 244 | `Effective from MCF M12.5 closeout, new metric authoring follows the MCF intake → panel → materialization sequence:` | `M12.5` | `Effective from MCF Metric Contract Materialization closeout, new metric authoring follows the MCF intake → panel → materialization sequence:` |
| 247 | `**M12 panel** — three-model panel (Maker / Checker / Moderator) produces a consensus proposal in 'mcf.metric_authoring_panel_run.consensus_payload_json'. Operator reviews the proposal via the M16 audit UI (when shipped).` | `M12`, `M16` | `**Metric Draft Review panel** — three-model panel (Maker / Checker / Moderator) produces a consensus proposal in 'mcf.metric_authoring_panel_run.consensus_payload_json'. Operator reviews the proposal via the M16 audit UI (when shipped).` **M16 left as-is** — semantic name not yet locked; flag for follow-up. |
| 248 | `**M12.5 materialization** — 'MetricAuthoringMaterializationService.runMaterialization(panelRunUid, opts)' materializes an 'APPROVE_FOR_DRAFT' panel proposal into MCF substrate.` | `M12.5` | `**Metric Contract Materialization** — 'MetricAuthoringMaterializationService.runMaterialization(panelRunUid, opts)' materializes...` — service identifier unchanged (Step 3 territory). |
| 250 | `Validates preconditions (L-V1 / L-V2 / L-V3)` | `L-V1`, `L-V2`, `L-V3` | `Validates Materialization Precondition checks (L-V1* / L-V2* / L-V3* family)` — family-name + parenthetical pattern. |
| 253 | `Calls 'McfCertWriterService.createMetricDraft' (with real canonical AST per D-M12.5-AST AST-A)` | `M12.5` (inside a decision-letter code `D-M12.5-AST`) | `D-M12.5-AST` is a decision-letter code, not a process name in this position — possibly leave or footnote. Inventory recommendation: leave `D-M12.5-AST` as-is per ADR Decision 1 ("Decision identifiers are NOT renamed") — the `D-` prefix marks it as a decision code, not a process name. |
| 259 | `**Operator workflow (M12.5 PR-2 ship):**` | `M12.5` | `**Operator workflow (Metric Contract Materialization PR-2 ship):**` |
| 263 | `The materialized MCV stops at 'governance_state_code='draft''. PE-MC evaluation is M13. Publication ('approved → active') is M14.` | `PE-MC`, `M13`, `M14` | `The materialized MCV stops at 'governance_state_code='draft''. Publication Eligibility Evaluation is Stage 6 (legacy: M13). Activation ('approved → active') is Stage 8 (legacy: M14).` Note the "(legacy: M12)" form satisfies ADR Decision 3 alias contexts (this is doctrine prose, not code comment, but the parenthetical-on-first-mention form from ADR §7.2 applies). |
| 271 | `### Tenant runtime — unchanged during M12.5` | `M12.5` | `### Tenant runtime — unchanged during Metric Contract Materialization` |
| 273 | `Tenant runtime evaluation [...] continues to read against the legacy 'metric.metric_definition' corpus during M12.5. Tenant runtime MCF awareness ships in M18+.` | `M12.5`, `M18+` | `Tenant runtime evaluation [...] continues to read against the legacy 'metric.metric_definition' corpus during Metric Contract Materialization. Tenant runtime MCF awareness ships in M18+.` **M18+ left as-is** — semantic name not yet locked. |

**Out-of-scope from runbook scope:** the `metric-work-records/` subdirectory contains 4 files matched by the legacy-code grep — these are session-work records dated 2026-05-12 and 2026-05-14, **historical audit-artifact territory** (not active operator runbooks). They are preserved as-is per Foundation Invariant III.

### 5.2 bc-admin UI labels — operator-facing strings (NOT inline comments)

**Files swept:** all of `bc-admin/src/` recursively for the legacy-code pattern.

**Files with legacy-code occurrences:** 9 files. Of these, **6 occurrences are operator-facing UI text** (in scope for Step 2) and **the rest are inline source comments** (out of scope per ADR Decision 3; allowed alias context).

**Per-occurrence inventory of in-scope UI text:**

| File | Line | Element type | Current text (verbatim, abridged) | Legacy codes | Proposed semantic replacement |
|---|---|---|---|---|---|
| `bc-admin/src/pages/MetricCatalogPage.tsx` | 131 | `aria-label` attribute on `<CheckCircle2 />` icon | `aria-label="M14 activation certificate present"` | `M14` | `aria-label="Metric Activation certificate present"` |
| `bc-admin/src/pages/MetricCatalogPage.tsx` | 159 | `subtitle` prop (visible page subtitle) | `Governed metric contracts — ${contracts?.length ?? 0} contracted, ${activeCount} active. New metrics enter via Register (seed → MCF intake → M12 panel).` | `M12` | `... → MCF intake → Metric Draft Review panel).` |
| `bc-admin/src/pages/MetricDetailPage.tsx` | 187 | `aria-label` attribute on inline icon | `aria-label="M14 activation certificate present"` | `M14` | `aria-label="Metric Activation certificate present"` |
| `bc-admin/src/pages/MetricLandscapePage.tsx` | 479 | `aria-label` attribute on `<CheckCircle2 />` icon | `aria-label="M14 activation certificate present"` | `M14` | `aria-label="Metric Activation certificate present"` |
| `bc-admin/src/pages/MetricRegistrationPage.tsx` | 140 | paragraph copy (visible page text) | `The M12 Maker/Checker/Judge panel is the verification step and runs against each intake in MCF.` | `M12` | `The Metric Draft Review (Maker / Checker / Judge) panel is the verification step and runs against each intake in MCF.` |
| `bc-admin/src/pages/MetricRegistrationPage.tsx` | 504 | toast / notification `detail` field | `intake ${res.intake_queue_uids[0] ?? ''} (queued — M12 panel verifies next)` | `M12` | `intake ${res.intake_queue_uids[0] ?? ''} (queued — Metric Draft Review panel verifies next)` |
| `bc-admin/src/pages/MetricRegistrationPage.tsx` | 551 | `subtitle` prop (visible page subtitle) | `Browse the seed reservoir and register metrics into the governed MCF flow (intake → M12 panel verification).` | `M12` | `Browse the seed reservoir and register metrics into the governed MCF flow (intake → Metric Draft Review panel verification).` |

**Out-of-scope under Step 2 — inline source comments in the same 9 files (legacy codes survive per ADR Decision 3):**

| File | Approx line(s) | Content type |
|---|---|---|
| `bc-admin/src/pages/MetricCatalogPage.tsx` | 8 | JSDoc / file-header comment about M14 activation evidence |
| `bc-admin/src/pages/MetricDetailPage.tsx` | 231 | inline comment about M12 panel knowledge profile |
| `bc-admin/src/pages/MetricRegistrationPage.tsx` | 7, 18 | JSDoc file-header + intra-method comments about M12 panel |
| `bc-admin/src/api/mcf-catalog.ts` | 6, 26 | JSDoc comments about M14 activation evidence |
| `bc-admin/src/api/seed-metrics.ts` | 6, 118 | JSDoc comments about M11 intake + M12 panel |
| `bc-admin/src/api/business-concepts.ts` | 435 | inline comment about F3 transition |
| `bc-admin/src/pages/business-concepts/PublicationConfirmModal.tsx` | 12 | JSDoc comment about F3 cert / transition |
| `bc-admin/src/components/metric/FormulaExpression.tsx` | 6 | JSDoc parameter comment about L-V1f |

These comments may be optionally renamed during Step 3 (code identifiers) by the engineer with `// legacy: M12` style annotation. They are NOT touched by Step 2.

### 5.3 Audit-artifact filenames — `bc-docs-v3/docs/implementation/`

**Historical filenames (NEVER renamed per Foundation Invariant III):**

The following files exist today with legacy codes in their names and are preserved as-is:

| Pattern | Files matching |
|---|---|
| `mcf-m{N}-*.md` (closeouts) | `mcf-m2-ddl-apply-closeout.md`, `mcf-m3-ddl-apply-closeout.md`, `mcf-m3-cert-amendment-apply-closeout.md`, `mcf-m4-ddl-apply-closeout.md`, `mcf-m5-apply-closeout.md`, `mcf-m7-m8-apply-closeout.md`, `mcf-m9-apply-closeout.md`, `mcf-m10-apply-closeout.md`, `mcf-m11-apply-closeout.md`, `mcf-m12-implementation-closeout.md`, `mcf-m12-5-implementation-closeout.md`, `mcf-m13-implementation-closeout.md` (12 files) |
| `metric-context-framework-m{N}-*.md` (DBCPs / preflights) | 14 files spanning M12 / M12.5 / M13 / M14 |
| `mcf-final-operating-flow-*` | 1 file (pre-doctrine note) |

These are historical work products of the M-track build sequence; their filenames are part of the audit ledger and cannot be rewritten under Invariant III. References to them in newer chapters continue to use the existing filenames.

**Going-forward policy (per ADR Decision 4 Step 2 + Decision 6.1):**

- **New audit-artifact filenames authored after 2026-06-22** use semantic names. Examples of the going-forward pattern:
  - Closeout for a Metric Draft Review change: `mms-metric-draft-review-{topic}-closeout-{date}.md` (not `mcf-m12-{topic}-closeout-{date}.md`).
  - Closeout for a Metric Contract Materialization change: `mms-metric-contract-materialization-{topic}-closeout-{date}.md`.
  - Closeout for a Publication Eligibility Evaluation change: `mms-publication-eligibility-evaluation-{topic}-closeout-{date}.md`.
- The `mcf-*` prefix may be retained where the artifact is specifically about the MCF grammar layer (substrate-and-grammar work). For artifacts that are about the operating flow (stages, gates, routes), use `mms-*` prefix.

**No renames performed for Surface 5.3** — historical files preserved; new-file policy noted.

### 5.4 bc-admin Metric Lifecycle / Metric Chain surfaces

**Route paths and page titles:**

`bc-admin/src/components/AppRouter.tsx` — swept; **no legacy-code occurrences** in route definitions. The bc-admin router uses semantic route names already (e.g. `/catalog/metrics/landscape`, `/catalog/metrics/registration`, `/catalog/metrics/:uid`).

**Page-title `PageHeader title=` props:**

- `MetricCatalogPage.tsx` — title "Metric Catalog" (semantic; no rename needed).
- `MetricLandscapePage.tsx` — title "Metric Landscape" (semantic; no rename needed).
- `MetricRegistrationPage.tsx` — title "Register Metric" (semantic; no rename needed).
- `MetricDetailPage.tsx` — title varies per metric (no static legacy code).

The Metric Lifecycle / Metric Chain surfaces named in [ADR DEC-7a1c98 Decision 4 Step 2](../../../governance/adrs/ADR-7a1c98.md) are already operating under semantic titles. The legacy-code occurrences in these surfaces are confined to subtitle copy and aria-labels (covered in §5.2 above).

**No additional renames identified for Surface 5.4 beyond what §5.2 already lists.**

## 6. Risk and impact assessment

| Risk | Surface(s) | Impact | Mitigation |
|---|---|---|---|
| **aria-label change alters screen-reader announcements** | §5.2 (3 aria-label occurrences) | Operators using assistive tech hear new wording. | Reversible at the label layer per ADR Decision 4 Step 2; can be rolled back by reverting the prop value. No accessibility regression — semantic name is more descriptive than the legacy code. |
| **subtitle / paragraph copy change is visible to operators on next page load** | §5.2 (4 subtitle / paragraph / toast occurrences) | Operators see new wording in catalog, registration, landscape, detail pages. Toast messages on intake registration change. | Visual diff is small (M12 → "Metric Draft Review"). Operator training / changelog note recommended at execution time. |
| **runbook chapter prose change is visible to onboarding readers** | §5.1 (11 prose occurrences in `metric-registration.md`) | Operators reading the runbook see semantic names. Section headers change (line 240, 271). Cross-references to these section anchors (`#mcf-m125-—-new-authoring-path-operator-runbook-addition`) break if renamed. | **Risk surface:** anchor-link rewriting. Mitigation: when executing, search bc-docs-v3 for incoming links to these anchors and update them in the same commit. Alternative: keep the section header's slug stable while changing the visible header (markdown allows custom slug discipline). |
| **`L-V1*`, `C-FX-*`, `M16/M17/M18+`, `C1/C2/F1/F2` family-name uses with deferred per-code mapping** | §5.1 line 250, §5.1 line 247 (M16), §5.1 line 273 (M18+) | Semantic name is the family designation but the specific letter-code remains; readers may find it half-renamed. | Inventory recommends: rename to family-name + retain the legacy code in parentheses on first mention. Example: `Materialization Precondition checks (L-V1* family)`. This satisfies ADR Decision 3 alias rules while signaling that per-code rename is deferred. |
| **References to legacy codes in operator-facing copy that span step-boundaries** | §5.1 line 253 mentions `McfCertWriterService.createMetricDraft` (a code identifier — Step 3 territory) | If Step 2 renames "M12.5" in the surrounding sentence, the code-identifier `MetricAuthoringMaterializationService` stays. The reader sees mixed vocabulary in the same paragraph. | Acceptable — this is the steady-state Step 2 ↔ Step 3 boundary. The mixed vocabulary is honest: process name renamed at Step 2; service name renamed at Step 3. |
| **`PE-MC` mention without specific gate number** | §5.1 line 263 (`PE-MC evaluation is M13`) | The phrase "PE-MC evaluation" refers to the publication eligibility evaluation family but doesn't name a specific gate. | Rename to "Publication Eligibility Evaluation is Stage 6 (legacy: M13)" — drops the `PE-MC` prefix entirely since Stage 6 already names the operation. |

## 7. Recommended execution order (when Step 2 opens)

This is **inventory recommendation only** — the execution session may reshape it.

1. **Cluster A — aria-labels only** (3 lines across 3 files in bc-admin). Smallest blast radius, accessibility-only impact, fully reversible. Suggested first execution sub-pass.
2. **Cluster B — bc-admin subtitle / paragraph / toast strings** (4 lines across 2 files). Visible to operators on next page load. Coordinate with a changelog note for operator awareness.
3. **Cluster C — `metric-registration.md` runbook prose** (11 lines in 1 file). Larger semantic change; section header rename requires anchor-link audit across `bc-docs-v3/docs/onboarding/` to update incoming links. Suggested third sub-pass.
4. **Deferred (separate decision)** — `M16` / `M17` / `M18+` and `C1`/`C2`/`F1`/`F2` family per-code semantic names. These are not yet locked in ADR Decision 6; rename can land when names are locked.

Each sub-pass is its own operator-authorized execution session, citing this inventory.

## 8. Out-of-scope confirmations (what this inventory does NOT cover)

- **Code identifiers** — class names, service names, controller filenames in `bc-core/src/registry/mcf/`, `bc-admin/src/`. Step 3 work.
- **HTTP route URL paths** in bc-admin or bc-core. Step 4 work.
- **Database enum values** — `governance_state_code`, `verdict_code`, `pe_check_code`, `action_code`. Step 5 work.
- **Per-metric controllers** — `mcf-arpi-materialization.controller.ts`, `billing-volume-retry-unlock/`. Step 6 work.
- **Inline source comments** mentioning legacy codes — preserved per ADR Decision 3 throughout Steps 2–6; may be annotated with `// legacy: M12` style notes at the engineer's option during Step 3.
- **Historical audit-artifact filenames** in `bc-docs-v3/docs/implementation/` — preserved per Foundation Invariant III.
- **Persisted historical evidence** — database rows, log rows, audit-row metadata — never rewritten regardless of step.
- **Decision identifiers** (`DEC-…`, `D-…`, ADR UIDs) — explicitly not renamed per ADR Decision 1.

## 9. Open questions for operator

1. **Should `M16` / `M17` / `M18+` references in operator-facing copy** be renamed now to a holding name (e.g. "Audit UI", "Operator Console", "Runtime Track surfaces") or left as `M16` / `M17` / `M18+` until the semantic names are locked in a follow-up to ADR DEC-7a1c98? Inventory recommendation: **leave as-is** for now; flag for follow-up; the rename is small when names land.
2. **Should `C1` / `C2` / `F1` / `F2` references be handled similarly?** Per ADR Decision 6.4 these are deferred. The current inventory found **zero occurrences** in bc-admin UI strings or `bc-docs-v3/docs/onboarding/metric-registration.md` for `C1` / `C2` / `F1` / `F2`. May appear elsewhere; not material to Step 2 today.
3. **Anchor-link rewriting policy.** When `metric-registration.md` line 240 / 271 section headers are renamed (Cluster C), incoming markdown anchor links break. Should the inventory's execution session include an automated anchor-link sweep across `bc-docs-v3/`? Inventory recommendation: **yes** — execute a `grep` for the old anchor slugs across `bc-docs-v3/` before committing, and update incoming links in the same commit.
4. **Operator changelog convention.** Subtitle and paragraph copy changes in bc-admin pages are visible to operators on next page load. Should the execution session emit an operator-facing changelog entry (e.g. a note in `bc-docs-v3/docs/operations/` or a banner on the affected pages)? Inventory recommendation: **yes** for Cluster B and C; not needed for Cluster A (aria-labels).
5. **Cross-reference to ADR.** Operator-facing copy at `metric-registration.md` line 263 currently reads "PE-MC evaluation is M13". The recommended rename adds a "(legacy: M13)" parenthetical. Should every legacy-code rename in operator-facing copy carry the parenthetical, or only the first mention per page? Inventory recommendation: **first mention per page only**, per ADR Decision 2 and the pattern established in MMS §1A.

## 10. Scope honoured

- Documentation-only edit.
- Read-only sweeps of `bc-docs-v3/docs/onboarding/`, `bc-admin/src/`, and `bc-docs-v3/docs/implementation/`.
- No substrate mutation.
- No runtime change.
- No code patch.
- No DB write (DevHub registry not invoked by this inventory).
- No PR.
- **No rename executed.** This inventory is the input to a future execution session, not a rename itself.
- The two stuck Metric Contract Versions on `bc_platform_dev` are untouched.
- The MCF substrate (`mcf.*` schema, `bc-core/src/registry/mcf/` code surfaces) is untouched.

## 11. Stop condition

Inventory complete. Locked next-step sequence:

1. **Operator review of this inventory** — including the 5 open questions in §9.
2. **Execution session 2a — Cluster A (aria-labels)** — smallest blast radius; suggested first sub-pass.
3. **Execution session 2b — Cluster B (bc-admin subtitle / paragraph / toast strings)** — visible-on-next-load; may bundle with operator changelog entry.
4. **Execution session 2c — Cluster C (`metric-registration.md` runbook prose)** — section-header rename + anchor-link sweep.
5. **Deferred — `M16` / `M17` / `M18+` and `C1`/`C2`/`F1`/`F2` per-code semantic naming** — separate ADR follow-up to lock the names before rename.

Steps 3 through 6 of the Controlled Semantic Refactor (code identifiers, route URL paths, DB enums, per-metric controller cleanup) remain operator-gated and are not authorised by this inventory.
