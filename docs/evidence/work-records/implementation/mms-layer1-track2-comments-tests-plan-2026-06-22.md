---
title: "MMS Layer 1 Track 2 — Comments + Tests Execution Plan"
description: "Reviewable batch plan for Cluster D (inline source comments) and Cluster E (test descriptions / spec names) under DEC-54f221 Layer 1. Re-stratifies the raw inventory counts to separate true source comments from test-file content and JSON-seed false positives. Identifies the smallest-safest proof batch, lists per-batch files / counts / risk tier / verification needs, and isolates filename renames as a Tier 2 sub-pass. Planning only — no rewrites executed."
date: 2026-06-22
project: bc-docs
domain: governance
subdomain: terminology
focus: track2-execution-plan
authority: reference
scope_locks: planning-only; no comment rewrites; no test rewrites; no filename renames; no code behavior changes; no prompt edits; no DB writes; no runtime change; no PR
parent_adr: ../adrs/ADR-54f221.md
predecessor_inventory: ./mms-layer1-interpretation-surfaces-inventory-2026-06-22.md
parent_doctrine: ../operating-model/metric-management-system.md
references:
  - ./mms-layer1-interpretation-surfaces-inventory-2026-06-22.md
  - ../operations/mms-terminology-transition-note-2026-06-22.md
---

# MMS Layer 1 Track 2 — Comments + Tests Execution Plan

> Planning document. No code, no comments, no tests, no filenames, no prompts edited by this document. Cluster G (bc-ai prompts) remains Track 3 territory; out of scope here.

## 1. Source data and re-stratification

The [Layer 1 inventory](mms-layer1-interpretation-surfaces-inventory-2026-06-22.md) §7–§8 reported raw counts that this plan **re-stratifies** because the original Cluster D sweep did not filter `.spec.ts` files (which live alongside source code, not under `**/test/`), so Cluster D and Cluster E shared overlap.

### 1.1 Cluster D — re-stratified (source comments only)

Excluded from this plan because they were miscounted as Cluster D in the inventory:

| Surface | Inventory count | Where it actually belongs |
|---|---|---|
| JSON-seed data files (`bc-core/src/registry/seed/s4/*.json`) | ~2,616 occurrences across 5 files | **False positives.** Not source code; M-like patterns are SAP table identifiers (e.g. `M`, `M_`, numeric M-suffixes) in source-system catalog data. Excluded from Cluster D entirely. |
| `.spec.ts` files inside the inventory's "top 20 by occurrence" list | ~487 occurrences across 7 top files (long tail likely adds ~300+) | **Cluster E**, not Cluster D. Moved below. |

Remaining true Cluster D scope (production source comments):

| Repo | Files | Occurrences (estimated, post-cleanup) | Notes |
|---|---|---|---|
| bc-core/src (non-test, non-seed) | ~140 files | ~1,800 | Majority concentrated in `registry/mcf/` service layer; long tail in `database/schema/mcf/`, `boundary/`, `registry/metric-authoring/`. |
| bc-admin/src | 12 | 47 | JSDoc file-headers + inline TSX comments. No JSON seed contamination. |
| bc-portal/apps/web/src | 5 | 13 | Data-seed references in TSX/TS comments. |
| bc-ai (Python `#` and docstrings, **prompts excluded**) | 6 | 24 | Code-side Python only; the 3 registry-authoring prompt files belong to Track 3. |
| barecount-devhub/src | 0 | 0 | — |
| **Cluster D total (post-cleanup)** | **~163 files** | **~1,884** | About 37% of the inventory's raw 5,043. |

### 1.2 Cluster E — re-stratified (test files only)

Adding back what Cluster D miscounted:

| Repo | Test files with legacy codes | Occurrences | Notes |
|---|---|---|---|
| bc-core/src (`.spec.ts` files) | 83 | 1,019 (per Cluster E sweep) + ~487 from Cluster D overcount (these are the JSDoc / inline-comment portion inside .spec.ts files) | Cluster E's original count covered describe/it/fixture strings; Cluster D's overcount covered comments inside the same spec files. Combined, the bc-core test surface carries roughly 1,500 occurrences across 83 files. |
| bc-ai/tests/ | 2 | 6 | Docstring-style references in test files; small surface. |
| bc-admin, bc-portal, barecount-devhub | 0 | 0 | No matches. |
| **Cluster E total** | **85 files** | **~1,500** | Includes both describe/it strings AND comment-style content inside spec files. |

### 1.3 Test files with legacy codes in the filename itself (separate Tier 2 batch)

| File | Occurrences inside | Why higher tier |
|---|---|---|
| `bc-core/src/registry/metric-authoring/m12-panel-run-writer.service.spec.ts` | 51 | Filename addressed by `jest --testPathPattern` and any CI selector that pins on the filename. |
| `bc-core/src/registry/mcf/pe-mc-12-evaluation.spec.ts` | 3 | Same. |

These are **NOT** part of the first execution pass; isolated as **Batch E4** below.

## 2. Replacement policy (re-stated, scoped to Track 2)

- Semantic name primary.
- Legacy code in parenthetical only on **first meaningful mention per file or local block** — `(legacy: M12)`.
- For comments and tests where traceability matters more (e.g. JSDoc file-header citing a DBCP that operator may search by old name), use the alias on first mention; subsequent mentions in the same file are semantic-only.
- **Do not invent names** for unmapped codes: `M16` / `M17` / `M18+` / `M10` / `C-FX-*` / `C1` / `C2` / `F1` / `F2`. Preserve verbatim.
- **Decision identifiers preserved** — `DEC-…`, `D…`, ADR UIDs, DBCP references (`DBCP §X.Y`) never renamed.
- **Code identifiers preserved** — class / service / controller / module names (e.g. `M12PanelRunWriterService`, `McfPublicationActivationController`) are Layer 2 territory; NOT renamed during Track 2.
- **Filenames preserved in non-test files** — script files like `bc-core/scripts/mcf-m12-5-preflight.mjs`, `bc-core/src/registry/mcf/metric-authoring-materialization.service.ts` (containing `m12-5` or `materialization` as filename slugs) are Layer 2. Track 2 only renames text inside the file, not the filename itself.

## 3. Cluster D — proposed batches

### D1 — bc-admin source comments (smallest D batch — recommended proof)

| Property | Value |
|---|---|
| Files | 12 |
| Occurrences | 47 |
| Risk tier | **Tier 1 — cosmetic** |
| Operator visibility | Engineer-only |
| Blast radius | Single repo, frontend only, no runtime impact |
| Existing CI exposure | bc-admin already passed Cluster A/B/C TypeScript checks (zero errors introduced); the same 12 files are likely a subset of those |
| Verification | (a) targeted grep before/after; (b) `npx tsc --noEmit` scoped (baseline = 25 unrelated errors); (c) `grep -nE "aria-label\|>[A-Z]" <changed files>` to confirm no JSX-rendered text touched |

Files (representative top 8 from inventory + the long tail):
- `bc-admin/src/pages/MetricCatalogPage.tsx` (file-header JSDoc — M14)
- `bc-admin/src/pages/MetricDetailPage.tsx` (line 231 inline — M12)
- `bc-admin/src/pages/MetricRegistrationPage.tsx` (lines 7, 18 JSDoc — M12)
- `bc-admin/src/api/mcf-catalog.ts` (lines 6, 26 JSDoc — M14)
- `bc-admin/src/api/seed-metrics.ts` (lines 6, 118 JSDoc — M11/M12)
- `bc-admin/src/api/business-concepts.ts` (line 435 inline — F3)
- `bc-admin/src/pages/business-concepts/PublicationConfirmModal.tsx` (line 12 JSDoc — F3)
- `bc-admin/src/components/metric/FormulaExpression.tsx` (line 6 JSDoc — L-V1f)

### D2 — bc-portal source comments

| Property | Value |
|---|---|
| Files | 5 |
| Occurrences | 13 |
| Risk tier | Tier 1 |
| Operator visibility | Engineer-only |
| Blast radius | Single repo, frontend |
| Verification | Same pattern as D1 |

Smaller than D1; could be bundled with D1 in a single commit to cover bc-admin + bc-portal frontends together.

### D3 — bc-ai source comments (non-prompt)

| Property | Value |
|---|---|
| Files | 6 |
| Occurrences | 24 |
| Risk tier | Tier 1 |
| Operator visibility | Engineer-only |
| Blast radius | Python source (not prompts); does not affect model behavior |
| Verification | (a) grep; (b) `python -m py_compile <files>` for syntax-only check; (c) confirm no docstring content drives runtime behavior (e.g. used by `inspect.getdoc` or vendored as prompt). Quick spot-check of `app/agents/registry_authoring.py` line 1 + `app/pipeline/bcf_telemetry.py` line 28 confirmed they're design-context comments, not runtime-consumed. |

### D4 — bc-core MCF service layer source comments — top 10 production files

| Property | Value |
|---|---|
| Files | ~10 production .ts files (the concentrated MCF service layer; see candidate list) |
| Occurrences | ~580 |
| Risk tier | Tier 1 — comments / JSDoc only, no runtime |
| Operator visibility | Engineer-only |
| Blast radius | Single repo, single service layer (`registry/mcf/`), concentrated; no behavior change |
| Verification | (a) grep; (b) `npx vitest run --reporter=basic` scoped to affected paths (sanity — comments don't affect behavior, but confirms no JSDoc-driven type generation broke); (c) `npx tsc --noEmit` whole-project |

Candidate files (from inventory):
- `bc-core/src/registry/mcf/metric-publication-eligibility-evaluator.service.ts` (215 — PE-MC-1..12)
- `bc-core/src/registry/mcf/metric-authoring-materialization.service.ts` (68 — M12.5 / M13 / M14)
- `bc-core/src/registry/mcf/mcf-read.service.ts` (63 — M12 / M13)
- `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` (61 — M4 / M13)
- `bc-core/src/registry/mcf/mcf-publication-activation.controller.ts` (43 — M14)
- `bc-core/src/registry/mcf/fixture-structural-check.service.ts` (36 — M9)
- `bc-core/src/registry/mcf/metric-authoring-panel.service.ts` (35 — M12)
- `bc-core/src/registry/metric-authoring/m12-panel-run-writer.service.ts` (47 — M12)
- 2 more from the inventory's top-by-occurrence list

### D5 — bc-core MCF service layer source comments — long tail

| Property | Value |
|---|---|
| Files | ~50 .ts files with 5–30 occurrences each |
| Occurrences | ~700 |
| Risk tier | Tier 1 |
| Blast radius | Same surface as D4; same verification |
| Verification | Same as D4 |

### D6 — bc-core non-MCF source comments

| Property | Value |
|---|---|
| Files | ~80 .ts files |
| Occurrences | ~500 |
| Risk tier | Tier 1 |
| Surfaces | `database/schema/mcf/` (DDL phasing comments), `boundary/` (D369 M4.2 dual-write phase comments), `registry/seed/` (excluding the JSON files), `registry/authoring/`, other registry sub-packages |
| Verification | Same as D4/D5 |

## 4. Cluster E — proposed batches

### E1 — bc-ai test descriptions and comments (smallest E batch — recommended proof)

| Property | Value |
|---|---|
| Files | 2 |
| Occurrences | 6 |
| Risk tier | **Tier 1 — cosmetic** |
| Operator visibility | Test runner output only |
| Blast radius | Smallest; covers Python test files |
| Verification | (a) grep; (b) `pytest <changed files>` runs; (c) confirm CI selectors don't pin on these descriptions |

### E2 — bc-core MCF spec files — top 7 (excludes filename-bearing test)

| Property | Value |
|---|---|
| Files | 7 (the top spec files by occurrence, excluding the 2 filename-renaming candidates) |
| Occurrences | ~440 (describe/it/fixture text + JSDoc inside spec files) |
| Risk tier | Tier 1 for descriptions; Tier 2 for any test-output-grep CI rule (see verification) |
| Verification | (a) grep before/after; (b) `npx vitest run <changed files>` — every test still passes with new descriptions; (c) `grep -r "M12\|PE-MC\|M14" .github/workflows/` to confirm no CI step pins on legacy test description text |

Candidate files (post-stratification, excluding the 2 filename-bearing ones):
- `bc-core/src/registry/mcf/metric-publication-eligibility-evaluator.service.spec.ts` (133 + 50 — PE-MC-1..12, M13)
- `bc-core/src/registry/mcf/metric-authoring-materialization.service.integration.spec.ts` (47 — L-V1, M13)
- `bc-core/src/registry/mcf/metric-authoring-materialization.service.spec.ts` (42 + 93 — L-V1, M13)
- `bc-core/src/registry/mcf/mcf-publication-activation.controller.spec.ts` (40 + 34 — PE-MC-1, M14)
- `bc-core/src/registry/mcf/metric-publication-eligibility-evaluator.service.integration.spec.ts` (37 + 8 — PE-MC, M13)
- `bc-core/src/registry/mcf/mcf-read.service.spec.ts` (24 + 67 — L-V1, M7 / M12.5)
- `bc-core/src/registry/mcf/mcf-cert-writer.service.integration.spec.ts` (18 + 9 — PE-MC, M13)

### E3 — bc-core MCF spec files — long tail

| Property | Value |
|---|---|
| Files | ~70 spec files with 1–30 occurrences each |
| Occurrences | ~500 |
| Risk tier | Tier 1 |
| Verification | Same as E2 |

### E4 — Filename renames (separate Tier 2 batch — explicitly NOT first)

| Property | Value |
|---|---|
| Files | 2 file renames |
| Risk tier | **Tier 2 — CI / coverage integration** |
| Files to rename | `m12-panel-run-writer.service.spec.ts` → semantic name; `pe-mc-12-evaluation.spec.ts` → semantic name |
| Suggested replacements | `metric-draft-review-panel-run-writer.service.spec.ts`; `publication-eligibility-check-12.spec.ts` (preserves the ordinal `12` even though the per-PE-MC numeric naming will be re-examined under the deferred mapping — for now keep ordinal continuity) |
| Verification | (a) `git mv` rather than delete+create to preserve history; (b) `npx jest --listTests` confirms new filenames discovered; (c) grep `bc-core/package.json` and `.github/workflows/` for legacy filename references; (d) grep `bc-core/src/` for any `import` referencing the old `.spec.ts` filename (unusual but possible); (e) full test suite `npx vitest run` passes after rename |

**Hard rule:** E4 runs only after E2 + E3 (description rename) lands. Doing E4 first would mean renaming filenames that still contain legacy-code text inside — a half-done state that confuses readers.

## 5. Recommended first execution batch (proof)

**D1 + D2 + D3 + E1 — multi-repo, frontends-and-Python proof batch.**

| Combined batch | Files | Occurrences | Why this is the safest proof |
|---|---|---|---|
| D1 — bc-admin source comments | 12 | 47 | Same files as Cluster A/B/C — TypeScript-verified surface |
| D2 — bc-portal source comments | 5 | 13 | Adjacent frontend repo; identical risk profile |
| D3 — bc-ai non-prompt comments | 6 | 24 | Python comments; smallest blast radius across bc-ai |
| E1 — bc-ai test comments | 2 | 6 | 2 Python test files |
| **Total** | **25** | **90** | **<2% of the Track 2 total — proves the rewrite tooling + workflow before committing to bc-core scale** |

Why combined rather than D1-alone:

- **D1 alone is the absolute minimum** (12 files, 47 occurrences). Acceptable too.
- **D1 + D2 + D3 + E1 (25 files, 90 occurrences)** proves the rewrite across **three repos and two languages (TypeScript + Python)** without touching the heavy bc-core surface. Catches more class-of-issue (e.g., Python docstring formatting differences) in one pass.
- bc-core scale (D4 onward) only starts after the proof batch survives review and verification.

### Proof-batch execution rhythm

1. **Single commit per repo** within the proof batch — three commits across bc-admin, bc-portal, bc-ai. Easier to review and revert.
2. **Grep verification** before commit per repo: old codes only remain inside `(legacy: …)` aliases or unmapped codes (`M16` / `M17` / `M18+` / `M10` / `C-FX-*` / etc.).
3. **TypeScript / pytest verification** per repo: zero new errors / failures introduced.
4. **Operator review** of the rewrite quality on the proof batch before bc-core scale opens.

## 6. Proposed tooling for the rewrite

Track 2 is bulk mechanical work. A small Node script (suggested ~150 lines) would walk a YAML mapping of legacy ↔ semantic names and rewrite comments + test descriptions across a glob of files. Suggested shape:

```yaml
# bc-docs-v3/scripts/track2-rewrite/mapping.yaml (illustrative — not authored by this plan)
- legacy: "M12"
  semantic: "Metric Draft Review"
  first_mention_alias: "(legacy: M12)"
- legacy: "M12.5"
  semantic: "Metric Drafting"
  first_mention_alias: "(legacy: M12.5)"
- legacy: "M13"
  semantic: "Publication Review"
  first_mention_alias: "(legacy: M13)"
- legacy: "PE-MC"
  semantic: "Publication Eligibility checks"
  first_mention_alias: "(legacy: PE-MC)"
- legacy: "M14"
  semantic: "Metric Activation"
  first_mention_alias: "(legacy: M14)"
- legacy: "M11"
  semantic: "Metric Intake"
  first_mention_alias: "(legacy: M11)"
- legacy: "L-V1"
  semantic: "Materialization Preconditions"
  first_mention_alias: "(legacy: L-V1)"
# Codes deliberately NOT in the mapping (preserve verbatim):
#   M10, M16, M17, M18+, C-FX-*, C1, C2, F1, F2
# Code identifiers preserved (Layer 2):
#   M12PanelRunWriterService, McfCertWriterService, etc.
# Filenames preserved in source files (Layer 2):
#   mcf-m12-5-preflight.mjs, m12-panel-run-writer.service.ts
```

Script invocation surface (illustrative, not implemented):

```
node bc-docs-v3/scripts/track2-rewrite/rewrite-comments.mjs \
  --mapping bc-docs-v3/scripts/track2-rewrite/mapping.yaml \
  --target "bc-admin/src/**/*.{ts,tsx}" \
  --comment-context-only \
  --first-mention-per-file \
  --dry-run | tee track2-d1-dry-run.diff
```

The script's responsibilities:
- Parse TS / TSX / JS / Python comments only (not JSX rendered text, not string literals, not identifiers).
- Apply the legacy ↔ semantic substitution with first-mention alias discipline.
- Skip lines containing decision identifiers (`DEC-`, `D{NNN}`, `DBCP §`).
- Skip lines containing the explicit "preserve" codes.
- Emit a diff for human review before any file write.

**Out of scope for THIS document — the script itself.** The plan only describes its shape; authoring the script is a separate operator-authorized task.

For Cluster E spec-file rewrites, the same script applies inside `describe('…')` / `it('…')` strings — the script needs to detect when it's inside a test-string vs a comment, but the rename rules are the same.

For Cluster E filename renames (E4), a separate `git mv` script handles those — outside the comment-rewrite tool.

## 7. Verification matrix per batch

| Batch | Targeted grep (old codes) | Targeted grep (new terms) | TypeScript / lint / pytest | CI selector check | Operator review gate |
|---|---|---|---|---|---|
| D1 | ✓ | ✓ | `npx tsc --noEmit` (whole-project baseline = 25 unrelated errors) | n/a | optional |
| D2 | ✓ | ✓ | `npx tsc --noEmit` scoped if available | n/a | optional |
| D3 | ✓ | ✓ | `python -m py_compile <files>` + spot check no docstring is runtime-consumed | n/a | optional |
| D4 | ✓ | ✓ | `npx vitest run` scoped to MCF service layer | n/a | **required** (largest Tier 1 batch in bc-core) |
| D5 | ✓ | ✓ | `npx vitest run` scoped | n/a | optional |
| D6 | ✓ | ✓ | `npx vitest run` whole bc-core | n/a | optional |
| E1 | ✓ | ✓ | `pytest <changed test files>` — every test still passes | n/a | optional |
| E2 | ✓ | ✓ | `npx vitest run <changed spec files>` | grep `.github/workflows/` for legacy test description text — confirm none | **required** |
| E3 | ✓ | ✓ | `npx vitest run` scoped | grep CI | optional |
| E4 | ✓ | ✓ | `npx jest --listTests` confirms new filenames; full suite passes | grep `package.json` + `.github/workflows/` for legacy filename refs; grep `bc-core/src/` for any `import` reference | **required** |

## 8. Explicit exclusions (out of scope for Track 2 entirely)

| Exclusion | Reason | Belongs to |
|---|---|---|
| JSON seed files (`bc-core/src/registry/seed/s4/*.json`) | False positives — not source comments | Not at any layer |
| bc-ai prompt files (`bc-ai/app/prompts/**`, `bc-ai/app/housekeeping/prompts/**`) | Special handling required | Track 3 / Cluster G |
| Code identifiers (class / service / controller / module names) | Layer 2 (Implementation Names) | Layer 2 |
| Filenames of non-test source files (e.g. `mcf-m12-5-preflight.mjs`, `metric-authoring-materialization.service.ts` if they contain legacy slugs) | Layer 2 | Layer 2 |
| HTTP route URL paths | Layer 2 (internal aliases) + Layer 3 (external deprecation) | Layer 2 + Layer 3 |
| DB enum values (`pe_check_code IN ('PE-MC-1', …)`) | Layer 3 (Compatibility Names) | Layer 3 |
| Telemetry keys, dashboard filter values, log emission keys | Layer 3 | Layer 3 |
| Historical audit-artifact filenames in `bc-docs-v3/docs/implementation/` | Foundation Invariant III | Permanently excluded |
| Decision identifiers (`DEC-…`, `D{NNN}`, ADR UIDs) | DEC-54f221 Decision 1 — UID continuity | Permanently preserved |
| DBCP references (`DBCP §12.3`) | Decision-like identifiers | Permanently preserved |
| `M10` (verifier sub-stage), `M16` / `M17` / `M18+` (operator console family), `C-FX-*` (per-code), `C1` / `C2` / `F1` / `F2` (BCF per-code) | No authority-mapped semantic name | Deferred — future inventory pass after mapping lands |
| Cluster F (backend error / log / toast / response strings) | Verified empty for Layer 1 in the inventory | No Track 2 work; substrate items already forwarded to Layer 2 / 3 |

## 9. Recommended execution order (Track 2 only)

1. **Proof batch — D1 + D2 + D3 + E1** (25 files, 90 occurrences). One commit per repo (three commits). Operator reviews diff quality before scaling.
2. **D4 — bc-core MCF service layer top 10** (~580 occurrences). Operator review required after this batch — establishes the rewrite pattern at scale in the highest-density area.
3. **D5 + D6 — bc-core MCF long tail + non-MCF surfaces** (~1,200 occurrences combined). May bundle into a single commit per surface if the pattern is stable.
4. **E2 — bc-core MCF spec files top 7** (~440 occurrences). Operator review required.
5. **E3 — bc-core MCF spec long tail** (~500 occurrences).
6. **E4 — Filename renames** (the 2 spec-file rename pair). Last sub-pass within Track 2; explicit CI verification required.

Track 3 (Cluster G — bc-ai prompts) opens on its own gated schedule per Layer 1 inventory §10; not affected by Track 2's progression.

## 10. Stop condition

Plan complete. Locked next-step sequence:

1. **Operator approval of this plan** — adjust batch boundaries or replacement-rule details as needed.
2. **Authoring of the rewrite script** (out of this plan's scope) — a separate operator-authorized session that builds `bc-docs-v3/scripts/track2-rewrite/rewrite-comments.mjs` (or equivalent) following the shape in §6.
3. **Execution of the proof batch (D1 + D2 + D3 + E1)** — single operator-authorized session with the script + review.
4. **Bc-core scale (D4 → D5/D6 → E2 → E3 → E4)** — staged operator-authorized sessions.
5. **Track 3 (Cluster G)** remains independent; not authorized by this plan.

Layer 2 (Implementation Names) and Layer 3 (Compatibility Names) remain operator-gated and are not authorized by this plan.

## 11. Scope honoured

- Planning / report only.
- No comment rewrites.
- No test rewrites.
- No filename renames.
- No code behavior changes.
- No bc-ai prompt edits.
- No DB writes.
- No runtime / service restart.
- No PR.
- No DevHub decision mutation.
- No business / platform substrate mutation.
- The two stuck Metric Contract Versions on `bc_platform_dev` are untouched.

Stop after this plan.

## 12. Execution log

This section appended post-plan to record actual execution events as Track 2 batches landed. It supplements the forward-looking plan above with the as-executed record so a future operator opening this document for D5/D6/E2/E3/E4 can see what's already complete.

### 12.1 Proof batch (D1 + D2 + D3 + E1) — completed 2026-06-22

- **Files processed:** 25 total per plan; **16 actually had legacy-code comment occurrences** post-triage (bc-portal's 5 files turned out to be false positives — SVG `M` path coordinates and SAP business-domain notification codes, not MMS workflow codes).
- **Replacements applied:** ~50 across bc-admin (7 files), bc-ai non-prompt Python (6 files), bc-ai tests (3 files).
- **bc-portal:** 0 files modified — scope confirmed empty after manual triage.
- **Verification:** bc-admin `npx tsc --noEmit` — 25 pre-existing errors, **zero in changed files**. bc-ai `python -m py_compile` — all 9 files parse. bc-ai venv `pytest` — **111 / 111 passed**.
- **Cluster B residual sub-pass** (operator-authorized same day): 3 visible UI strings the original Cluster B inventory had miscategorized as comments — `MetricDetailPage.tsx:231`, `MetricRegistrationPage.tsx:184`, `ProvenancePanel.tsx:200` — corrected; recorded in [`mms-terminology-transition-note-2026-06-22.md`](../operations/mms-terminology-transition-note-2026-06-22.md) Addendum.

### 12.2 D4 — bc-core MCF service-layer top-10 production files — completed 2026-06-22

| Surface | Value |
|---|---|
| Target files | 10 |
| Files modified | 9 (one is a confirmed no-op — `mcf-hash-computer.interface.ts` has 19 raw legacy-code hits but all live in TypeScript interface declarations, not comment regions) |
| Total comment-side replacements applied | **273** (9 pilot + 147 second-batch + 117 evaluator) |
| Total preservation skips | **17** (2 + 5 + 10) — distributed across `decision-id`, `quoted-string` (DB enum values), `runtime-context` (proximity to `verifier_version='mcf-m13-v2'` etc.), `preserve-list` (PE-MC-8 retired check + M4 / M9 / M10 unmapped codes), and `identifier-prefix`/`-suffix` (snake_case / PascalCase boundary) |
| Manual polishes (article-grammar + word-duplication artifacts) | **10** across 5 files |

**Files in D4 (final order):**

| # | File | Applied | Skipped |
|---|---|---:|---:|
| 1 | `mcf-publication-activation.controller.ts` (pilot) | 9 | 2 |
| 2 | `mcf-cert-writer.service.ts` | 23 | 2 |
| 3 | `mcf-read.service.ts` | 36 | 0 |
| 4 | `metric-authoring-materialization.service.ts` | 37 | 0 |
| 5 | `metric-authoring-panel.service.ts` | 18 | 0 |
| 6 | `m12-panel-run-writer.service.ts` | 18 | 0 |
| 7 | `metric-mcv-rebind.service.ts` | 12 | 3 |
| 8 | `package-signature.service.ts` | 3 | 0 |
| 9 | `mcf-hash-computer.interface.ts` | 0 (no-op) | 0 |
| 10 | `metric-publication-eligibility-evaluator.service.ts` | 117 | 10 |

**Runtime behaviour:** unchanged. All changes are inside `/* */`, `/** */`, JSDoc continuation, or `//` comment regions. The identifier-integrity scan (`git diff --unified=0 | grep "^[+-]" | filter out comment-marker lines`) returned **empty** for every D4 file.

**Verification:**

- `cd bc-core && npx tsc --noEmit` — **42 total errors in bc-core, zero in any D4 changed file**. The 42 errors are the pre-existing baseline in unrelated files (`RegisterProviderDialog`, `BoundariesPage`, `ConnectionsPage`, `MetricDefinitionDetailPage`, `MetricReferencePage`, `ReaderDetailPage`, `SeedCatalogPage`, etc. — same set reported in every prior closeout this session).
- `npx vitest run <14 affected spec files>` — **504 passed, 14 skipped (518 total)**. The 14 skips are all pre-existing `.skip()` annotations in integration specs.

**Manual polishes recorded (10 sites across 5 files):**

| File | Line | Category | Before → After |
|---|---|---|---|
| `mcf-publication-activation.controller.ts` | 181 | article-grammar | `an Publication Review evaluator-version` → `a Publication Review evaluator-version` |
| `mcf-publication-activation.controller.ts` | 286 | article-grammar | `an Metric Activation PE row` → `a Metric Activation PE row` |
| `mcf-read.service.ts` | 697 | article-grammar | `an Metric Activation source change` → `a Metric Activation source change` |
| `mcf-read.service.ts` | 774 | word-duplication | `Metric Activation activation gate` → `Metric Activation gate` |
| `mcf-read.service.ts` | 1257 | word-duplication | `// ─── Metric Activation activation gate types ───` → `// ─── Metric Activation gate types ───` |
| `mcf-cert-writer.service.ts` | 386 | word-duplication | `stamped on Metric Activation activation PE rows` → `stamped on Metric Activation PE rows` |
| `metric-authoring-materialization.service.ts` | 1311 | word-duplication | `(b) Metric Intake intake transition` → `(b) Metric Intake transition` |
| `metric-publication-eligibility-evaluator.service.ts` | 11 | word-duplication | `the 10 Publication Eligibility checks publication eligibility checks against` → `the 10 Publication Eligibility checks against` |
| `metric-publication-eligibility-evaluator.service.ts` | 432 | article-grammar | `AFTER an Publication Review evaluation` → `AFTER a Publication Review evaluation` |
| `metric-publication-eligibility-evaluator.service.ts` | 805 | article-grammar | `AFTER an Publication Review evaluation` → `AFTER a Publication Review evaluation` |

### 12.3 Helper script status

- **Path:** `barecount-devhub/.claude/scripts/mms-layer1-track2-rewrite-preview.mjs`
- **Status:** Temporary / session-local (lives in `.claude/scripts/`, gitignored). Apply-ready for D5/D6/E2/E3/E4.
- **Final capabilities** (post-D4 hardening):
  - `--target <file>` filter (per-file dry-run or apply)
  - `--apply` flag (writes back; otherwise dry-run only)
  - Compound PE-MC range/list pattern (single-unit rewrite for `PE-MC-1..PE-MC-10` / `PE-MC-1..7,9,10,11`)
  - Nested-paren flattening via outward-scan heuristic (uses semicolon-form alias when inside existing parens)
  - Loosened lookahead boundary that allows trailing hyphen (fixed `M12.5-staged` style)
  - PE-MC-8 added to `MAPPING_ORDERED` as self-mapping (consumed by regex, then skipped via `PRESERVE_TOKENS`)
  - `already-aliased` preservation check (skips matches preceded by `legacy:` — idempotent on re-runs)
  - Skip-reason taxonomy: `decision-id`, `identifier-prefix`/`-suffix`, `filename-slug`, `quoted-string`, `runtime-context`, `preserve-list`, `already-aliased`

### 12.4 Remaining Track 2 batches

| Batch | Surface | Est. occurrences | Status |
|---|---|---:|---|
| **D5** | bc-core MCF service-layer long tail (~50 production .ts files with 5–30 occurrences each) | ~700 | not started |
| **D6** | bc-core non-MCF source comments (`database/schema/mcf/`, `boundary/`, `registry/authoring/`, etc.) | ~500 | not started |
| **E2** | bc-core MCF spec files top 7 (describe/it texts + JSDoc inside spec files) | ~440 | not started |
| **E3** | bc-core MCF spec files long tail | ~500 | not started |
| **E4** | Filename renames — `m12-panel-run-writer.service.spec.ts`, `pe-mc-12-evaluation.spec.ts` | 2 files | not started; runs **last**, with CI-selector verification |

**Cluster F** — confirmed no-op for Layer 1 (per inventory §9). The substrate items it surfaced (`pe_check_code` DB enum, `_CHECKLIST_ITEM_KEYS` Python tuple) are Layer 2/3 territory.

**Cluster G (bc-ai prompts)** — remains gated on regression discipline (Layer 1 inventory §10). Independent of D5/D6/E2/E3/E4 progression.

### 12.5 Open as-executed observations

A few small things surfaced during D4 worth noting before D5 opens:

1. **Word-duplication is the most common rewrite artifact.** When a legacy code's original surrounding text already contained the spelled-out semantic name (e.g. `M14 activation`, `PE-MC publication eligibility checks`, `M11 intake`), the rewrite produces `Metric Activation activation`, `Publication Eligibility checks publication eligibility checks`, `Metric Intake intake`. The helper does not detect this; it requires a manual rescan + polish after each batch. Suggested scan regex for future batches: `\b(Metric Activation activation|Metric Drafting drafting|Metric Draft Review draft review|Metric Intake intake|Publication Review publication|Publication Eligibility checks publication eligibility)\b`.

2. **`an Metric|an Publication` article-grammar is the second-most-common artifact** — easy regex to spot post-apply: `\ban (Metric|Publication|Materialization|Vocabulary|G[0-9])`.

3. **A pre-apply word-duplication check could be added to the helper.** Not required for D5/D6 (manual rescan is fast), but worth considering if E2/E3 surface many more cases since test-description rewrites have higher density.

4. **Conservative `runtime-context` proximity** (30-char window around `verifier_version=…`, `evidence_json.…`, etc.) sometimes preserves legitimate workflow-code references on the same line. Acceptable trade-off — better to under-rewrite than mis-rewrite a runtime string adjacent.

5. **The helper's `--target <file>` flag accepts a substring match against the canonical D4 target list.** For D5/D6/E2/E3, either extend `TARGETS` in the helper to include the new file lists, or invoke per-file with full paths and a flag like `--target-path <abs>`. (Minor — easy to extend.)

### 12.6 Stop condition (post-D4)

D4 complete. Pause checkpoint accepted by operator. Next-step sequence:

1. **Operator review of the complete D4 surface** in the working tree before opening D5.
2. **(Optional) Local dev-server smoke test** — comment-only changes have zero runtime impact, but a quick smoke confirms.
3. **D5** when operator authorizes — same helper, per-file workflow established by D4 pilot.
4. **D6, E2, E3** in order. E4 last with CI-selector verification.
5. **Cluster G (bc-ai prompts)** on its own schedule with the prerequisite regression discipline (Layer 1 inventory §10).

No Layer 2 or Layer 3 work is authorized by this plan or this execution log.

## 12.7 Post-D4 batches and Track 2 close

Operator-authorized continuation past the §12.6 D4 pause checkpoint. D5, D6, E2 landed in sequence (covered briefly here for context); E3 and E4 recorded in detail per operator instruction.

### 12.7.1 D5 / D6 / E2 — interim batches (summary)

| Batch | Surface | Candidates | Modified | Applied | Skipped | Polishes |
|---|---|---:|---:|---:|---:|---:|
| D5 | bc-core MCF service-layer long tail | 65 files | 50 | 177 | 2 | 3 |
| D6 | bc-core non-MCF source comments (`database/schema/mcf/`, `boundary/`, `progression/`, `registry/concept-registry/`, `schema-provisioner/`, etc.) | 75 files | 25 | 65 | 1 | 9 |
| E2 | bc-core MCF spec files top 7 | 7 files | 7 | 175 | 16 | 3 |

Helper extension this period: added `--targets-from <file>` flag (used by D5/D6/E2/E3/E4) to keep the hardcoded D4 array stable while accepting per-batch target lists; added test-description detection (describe/it/test/context call arguments) with context-sensitive `quoted-string` preservation that activated for the E-series batches.

### 12.7.2 E3 — bc-core MCF spec long tail — completed 2026-06-22

| Surface | Value |
|---|---|
| Candidate files | 38 (after excluding the 7 E2 files and 2 E4 filename-rename candidates) |
| Files modified | 25 (13 no-ops — raw hits all in import statements, fixture data, code identifiers, or quoted DB enum values) |
| Total comment + test-description replacements applied | **65** |
| Preservation skips | **2** (both `runtime-context` proximity to `idx_mcf_*`) |
| Manual polishes | **2** (1 word-duplication: `Metric Intake intake row` → `Metric Intake row`; 1 multi-line nested-paren in JSDoc converted to `[legacy: M14]` square-bracket form) |

**Verification:**

- `npx vitest run <38 E3 spec files>` — **900 passed, 5 skipped** across 36 unit specs + 2 integration specs. The 5 skips are pre-existing `.skip()` annotations.
- `npx tsc --noEmit` — 42 baseline errors, **zero in any E3 file**.
- Identifier-integrity scan — zero non-comment / non-test-description changes.
- Article-grammar / word-duplication / nested-parens scans — all empty post-polish.

### 12.7.3 E4 — spec filename renames — completed 2026-06-22

Two `.spec.ts` file renames via `git mv` (history preserved):

| Old filename | New filename |
|---|---|
| `bc-core/src/registry/metric-authoring/m12-panel-run-writer.service.spec.ts` | `bc-core/src/registry/metric-authoring/metric-draft-review-panel-run-writer.service.spec.ts` |
| `bc-core/src/registry/mcf/pe-mc-12-evaluation.spec.ts` | `bc-core/src/registry/mcf/publication-eligibility-check-12.spec.ts` |

**Inbound-reference sweep (pre-rename):**

- `bc-core/src/**/*.ts`: 1 active comment reference at `b2-binding-capture-sentinel.ts:30` (updated in-pass to point at the new filename); 1 self-reference inside the renamed `pe-mc-12-evaluation.spec.ts:2` JSDoc header (updated post-rename to the new name).
- `bc-core/package.json`, `vitest.config.ts`, `vitest.config.e2e.ts`: **zero** references.
- `.github/workflows/`: none present in bc-core or repo root.
- `bc-core/scripts/`: references found only to the PRODUCTION `m12-panel-run-writer.service.ts` (NOT the spec being renamed) — preserved as historical evidence per Foundation Invariant III.
- `bc-docs-v3/docs/`: 9 historical inventory/planning references in `mms-layer1-interpretation-surfaces-inventory-2026-06-22.md` and `mms-layer1-track2-comments-tests-plan-2026-06-22.md` — preserved per Foundation Invariant III (they describe the rename target by its historical name).

**Content rewrites inside the two renamed files** (executed via the helper post-rename — the renamed files were excluded from E2/E3 as filename-rename candidates so their content had never been processed):

| File | Proposed | Applied | Skipped |
|---|---:|---:|---:|
| `metric-draft-review-panel-run-writer.service.spec.ts` | 3 | 3 | 0 |
| `publication-eligibility-check-12.spec.ts` | 3 | 3 | 0 |

**Manual polish (1 site):** `publication-eligibility-check-12.spec.ts:54` — `describe('G4 Source-Vocabulary Discipline Gate evaluator gate', …)` → `describe('G4 Source-Vocabulary Discipline Gate evaluator', …)` (dropped trailing redundant "gate" word).

**Verification:**

- `npx vitest run <2 renamed spec files>` — **52 passed** (23 in `publication-eligibility-check-12.spec.ts` + 29 in `metric-draft-review-panel-run-writer.service.spec.ts`). Vitest auto-discovers `*.spec.ts` files; no test-path config update was needed.
- `npx tsc --noEmit` — 42 baseline errors, **zero in the renamed files or in `b2-binding-capture-sentinel.ts`**.
- `git status` confirms both renames detected as `R` (renames, not delete+create).
- Post-rename grep for old filenames in `bc-core/src/`: **clean** — no lingering active code references.

### 12.7.4 Track 2 cumulative totals (end of execution)

| Metric | Total |
|---|---:|
| Total Track 2 comment + test-description + content replacements applied | **~821** (proof ~50 + D4 273 + D5 177 + D6 65 + E2 175 + E3 65 + E4 content 6 + ~10 manual polishes) |
| Total preservation skips (documented) | **~40** |
| Manual polishes (article-grammar / word-duplication / nested-parens) | **~30** |
| Files modified across all batches | ~165 in bc-core + ~16 in bc-admin / bc-portal / bc-ai (proof batch) |
| Filename renames (E4) | 2 |
| Active code / CI references updated | 1 (`b2-binding-capture-sentinel.ts:30` comment) |
| TypeScript errors introduced | **0** (42 pre-existing baseline preserved throughout) |
| Vitest failures introduced | **0** across all batches |
| Production code / runtime behaviour changes | **None** — Layer 1 is comment / JSDoc / test-description / spec-filename rename only |

### 12.7.5 Track 2 status

**Track 2 is complete.** All seven batches (proof, D4, D5, D6, E2, E3, E4) executed and verified. The Track 2 plan §1–§11 contract is fulfilled; this execution log (§12.1–§12.7) is the as-executed record.

### 12.7.6 Remaining MMS Layer 1 work

| Surface | Status |
|---|---|
| **Cluster G — bc-ai prompts** | **Gated on regression discipline.** Independent track per Layer 1 inventory §10. Requires: baseline fixture import from bc-core's `ai_ledger.bcf_panel_runs`, before/after panel comparison at `temperature=0`, ≥98% verdict-match threshold, byte-exact `f3_input` field equality, operator-authorized canary deployment. Not started. |
| **Layer 2 — Implementation Names** | **Operator-gated per DEC-54f221.** Class / service / controller / route alias / non-persisted symbol renames. Not authorized by this Track 2 closeout. |
| **Layer 3 — Compatibility Names** | **Operator-gated per DEC-54f221.** Persisted codes, DB enum values, telemetry keys, dashboard filter values. Requires the telemetry / log / dashboard pre-inventory called out by DEC-54f221 as a precondition. Not authorized by this Track 2 closeout. |

### 12.7.7 Helper script disposition

`barecount-devhub/.claude/scripts/mms-layer1-track2-rewrite-preview.mjs` — Track 2 final state. Capabilities at close:

- `--target <file>` per-file mode; `--targets-from <file>` batch-list mode; `--apply` write-back mode (otherwise dry-run only).
- Compound PE-MC range/list pattern (`PE-MC-1..PE-MC-10`, `PE-MC-1..7,9,10,11` as single units).
- Nested-paren flattening via intra-line outward-scan; semicolon-form alias when inside parens.
- Loosened lookahead boundary (allows trailing hyphen — fixed `M12.5-staged` boundary case).
- PE-MC-8 self-mapping (consumed by regex, then skipped via `PRESERVE_TOKENS`).
- `already-aliased` preservation (idempotent on re-runs).
- Test-description detection (`describe`/`it`/`test`/`context`/`xdescribe`/`xit`/`fdescribe`/`fit` with optional `.skip`/`.only`).
- Context-sensitive `quoted-string` preservation (off in describe/it call args; on elsewhere).
- 7 skip-reason taxonomy: `decision-id`, `identifier-prefix`/`-suffix`, `filename-slug`, `quoted-string`, `runtime-context`, `preserve-list`, `already-aliased`.

Status: temporary, session-local (gitignored `.claude/scripts/`). Operator disposition pending — keep across Layer 2 polish passes, repurpose for Cluster G work (would need significant extension for prompt-regression workflow), or delete. Not deleted by this Track 2 closeout.
