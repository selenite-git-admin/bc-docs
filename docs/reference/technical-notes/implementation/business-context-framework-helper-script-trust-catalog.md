---
uid: business-context-framework-helper-script-trust-catalog
title: Business Context Framework (BCF) — Helper-Script Trust Catalog (E2)
description: Evidence document for build-plan item E2, converting gap-research G24 from coarse "default-untrusted" (138/156 hardcoded scope) into a per-script trust catalog with four bands and a defect-surface verdict that CI can consume as its second defect-tag source besides gap-research G-findings.
status: draft
date: 2026-05-19
project: bc-docs
domain: contracts
subdomain: catalog
focus: evidence
session: SES-2cfa45
---

# Business Context Framework (BCF) — Helper-Script Trust Catalog (E2)

## Verdict

**Default-untrusted classification refined to per-script banding with a defect-surface verdict CI can consume.**

160 source scripts under `bc-core/scripts/` audited (134 .mjs + 22 .js + 2 .ts + 1 .py + 1 .sh; .sql migration bodies intentionally excluded). 113 of 160 (71%) carry at least one hardcoded tenant / schema / env pattern — consistent with Codex §8.1's 138/156 finding at the prior baseline.

**13 scripts (8.1%) are active defect surfaces** — unsafe band AND invoked by runbook / package.json / other script. These become CI's second defect-tag source (besides gap-research G-findings) once the combined inventory update lands.

Inventory §2.9 verdict shifts from coarse `default-untrusted` to **per-script-banded with defect-surface verdict**, with the 13 defect surfaces listed as the operative CI tag-grep target.

## Method

- **Scope:** all source-language files under `C:/MyProjects/bc-core/scripts/` (recursive, `.mjs|.js|.ts|.sh|.py`). `.sql` files excluded — they are migration/seed bodies, not executable scripts.
- **Hardcoding grep:** tenant patterns (`tbc_\w+_dev`, `demo[-_]\w+`, `selenite`, `\bapex\b`), schema patterns (`\bboundary\.`, `\bcanonical_object\b` — pre-DEC-f02230), env patterns (`localhost`, `127.0.0.1`, `version 1.0`, hardcoded ports `:3100`, `:5432`, `:5435`, `:27017`).
- **Side-effect classification (static):** writes:sql (INSERT/UPDATE/DELETE/DROP/TRUNCATE/ALTER/CREATE), writes:mongo (insertOne/updateOne/deleteOne/replaceOne/bulkWrite/etc.), spawns (execSync/spawn/fork/child_process), external_api (fetch/axios/http.request/etc.). Default: read-only.
- **Git log:** `git log -1 --pretty=format:"%ad|%an" --date=short` per file for last-modified date + author.
- **Call-site grep:** in-memory scan across the 5 surveyed repos (bc-core, bc-admin, bc-ai, bc-portal, bc-docs) — package.json scripts, bc-docs markdown runbooks (665 files), sibling scripts in bc-core/scripts/.
- **Banding rules** (deterministic):
  - **trusted** — no hardcoding; read-only
  - **diagnostic** — hardcoded; read-only
  - **unsafe** — `writes + hardcoding` OR uses stale schema (`boundary.` / `canonical_object`)
  - **deprecated** — >6 months old AND not-invoked
- **Defect-surface verdict** = `band ∈ {unsafe, deprecated} AND invocation ∈ {invoked-by-ci, invoked-by-package-json, invoked-by-runbook, invoked-by-other-script}`.
- **No mutations.** Reads only. Audit script (`bcf-e2-script-audit.mjs`) is removed in the same commit as this document landing per §13 / G24 discipline.

## 0. Bootstrap discipline (audit script profile)

Per build-plan §9 (the script auditing scripts must itself pass the audit), the audit script's profile:

| Field | Value |
|---|---|
| Path | `bc-core/scripts/bcf-e2-script-audit.mjs` |
| Band (self-classified) | unsafe |
| Hardcoded tenant | `selenite` (regex pattern literal) |
| Hardcoded env | `localhost`, `:3100`, `:5432`, `:27017` (regex pattern literals) |
| Side effects (false positive) | `writes:sql\|writes:mongo\|spawns\|external_api` — false positive: the script contains the pattern definitions for these classes (e.g. `/\b(INSERT INTO|...)/i`), which the side-effect classifier matched against its own source. Manual inspection confirms the script is strictly read-only. |
| Call-site count | 0 |
| Defect-surface verdict | **no** (band=unsafe but invocation=not-invoked) |

The false-positive side-effect classification is sub-finding S3 below. The script is **removed in the same commit as this document**; the bootstrap problem is the reason it does not enter the catalog as a persistent row.

## 1. N30-disciplined summary (band × hardcoding × invocation × defect-surface)

### 1.1 Bands

| Band | Count | % | Notes |
|---|---:|---:|---|
| **trusted** | 38 | 23.8% | No hardcoding; read-only. Safe to invoke without per-call audit. |
| **diagnostic** | 67 | 41.9% | Hardcoded tenant/schema/env; read-only. Useful for one-shot lookups; do NOT treat output as evidence per zero-claims policy. |
| **unsafe** | 55 | 34.4% | Writes + hardcoding, OR stale schema reference. Operator-approved-call-only. |
| **deprecated** | 0 | 0.0% | Rule requires >6 months old AND not-invoked. Oldest file is `test-canonical-evoluation.js` from 2026-02-28 (~2.7 months); rule will start firing around Sept 2026. See S2 below. |
| **Total** | **160** | 100% | |

### 1.2 Hardcoding (paired with bands per N30)

| Hardcoded pattern type | Count | % of total |
|---|---:|---:|
| Tenant (`tbc_*_dev`, `demo-*`, `selenite`, `apex`) | 23 | 14.4% |
| Schema (`boundary.`, `canonical_object` — pre-DEC-f02230) | 12 | 7.5% |
| Env (`localhost`, ports, version) | 106 | 66.3% |
| **Any hardcoding** | **113** | **70.6%** |

### 1.3 Invocation status

| Invocation | Count | Notes |
|---|---:|---|
| `invoked-by-ci` | **0** | **No CI workflows exist in any surveyed repo.** Sub-finding S1. |
| `invoked-by-package-json` | 5 | `golden-snapshot.mjs`, `lint-column-names.mjs`, `smoke-e2e-pipeline.mjs`, `validate-build-config.mjs`, `validate-build-output.mjs` |
| `invoked-by-runbook` | 30 | Referenced from bc-docs markdown |
| `invoked-by-other-script` | 8 | Referenced from another script in bc-core/scripts/ |
| `not-invoked` | 117 | No invocation surface found |
| **Total** | **160** | |

### 1.4 Defect-surface verdict (the load-bearing CI input)

| Verdict | Count |
|---|---:|
| **yes** (unsafe/deprecated AND invoked) | **13** |
| no | 147 |

## 2. Defect surfaces (the 13)

These are the load-bearing CI tag-grep targets. Any PR modifying one of these files must carry a `CURRENT DEFECTIVE behavior` characterization tag per §13.5, or the modification must explicitly dispose of the defect (move script to trusted band, remove the unsafe pattern, or deprecate the call site).

| # | Script | Band | Invocation | Call sites | Hardcoded | Side effects | Last modified |
|---:|---|---|---|---:|---|---|---|
| 1 | `scripts/d369-m1c-sandbox1-probe.mjs` | unsafe | invoked-by-runbook | 1 | tenant: `tbc_sandbox1_dev` | writes:sql | 2026-04-22 |
| 2 | `scripts/d408-backfill-bf-catalog-state-1q-a.mjs` | unsafe | invoked-by-runbook | 2 | tenant: `selenite` | writes:sql | 2026-05-16 |
| 3 | `scripts/d408-demote-bf-catalog-state-1q-b.mjs` | unsafe | invoked-by-runbook | 2 | tenant: `selenite` | writes:sql | 2026-05-16 |
| 4 | `scripts/d408-demote-correction-required-no-cc-1q-d.mjs` | unsafe | invoked-by-runbook | 1 | tenant: `selenite` | writes:sql | 2026-05-17 |
| 5 | `scripts/d408-remove-a1-mismatch-cc-mappings-1q-e.mjs` | unsafe | invoked-by-runbook | 1 | (writes-only triggers unsafe) | writes:sql | 2026-05-17 |
| 6 | **`scripts/evaluate-ready-mcs.mjs`** | unsafe | invoked-by-runbook | 3 | tenant: `tbc_selenite_dev`, `demo-selenite`, `selenite`; schema: `boundary.`, `canonical_object` | external_api | 2026-04-29 |
| 7 | `scripts/golden-snapshot.mjs` | unsafe | invoked-by-package-json | 2 | none in source; writes:sql\|spawns | writes:sql\|spawns | 2026-03-29 |
| 8 | `scripts/mc-diagnose.mjs` | unsafe | invoked-by-runbook | 5 | tenant: `tbc_selenite_dev`, `selenite`; schema: `boundary.` | read-only (unsafe via schema) | 2026-05-08 |
| 9 | `scripts/mc-verify.mjs` | unsafe | invoked-by-runbook | 4 | tenant: `tbc_selenite_dev`, `demo-selenite`, `selenite`; schema: `boundary.`, `canonical_object` | read-only (unsafe via schema) | 2026-05-08 |
| 10 | `scripts/oc-sc-pairing-review.mjs` | unsafe | invoked-by-other-script | 1 | (writes-only triggers unsafe) | writes:sql | 2026-05-09 |
| 11 | `scripts/seed-fi-readers-week2.mjs` | unsafe | invoked-by-runbook | 1 | env: `version 1.0` | writes:sql | 2026-03-15 |
| 12 | `scripts/seed-reader-bindings.mjs` | unsafe | invoked-by-other-script | 1 | (writes-only triggers unsafe) | writes:sql | 2026-04-17 |
| 13 | `scripts/smoke-e2e-pipeline.mjs` | unsafe | invoked-by-package-json | 2 | schema: `boundary.` | read-only (unsafe via schema) | 2026-04-12 |

**Canonical example from Codex §8.1:** `evaluate-ready-mcs.mjs` (#6) is the named canonical defect surface — hardcoded `tbc_selenite_dev`, pre-DEC-f02230 `boundary.canonical_object` schema, `localhost:5435`, invoked from 3 runbooks. Codex confirmed at lines 14–21, 37, 80–85.

## 3. Unsafe-but-not-invoked (cleanup candidates, not active defect surfaces)

42 scripts are unsafe but not currently invoked. Not CI defect-tag targets today (defect-surface = no) but they are cleanup candidates. Listed for traceability:

| Script | Last modified | Reason flagged unsafe |
|---|---|---|
| `bench-metric-engine.mjs` | 2026-04-12 | tenant: `tbc_qa_bench_dev`; schema: `boundary.`, `canonical_object` |
| `build-mega-kpi-csv.py` | 2026-03-28 | writes:sql |
| `build-semantic-review-packet.mjs` | unknown | schema: `boundary.` |
| `d087-backfill-tenant-schemas.mjs` | 2026-03-20 | tenant: `selenite`; schema: `canonical_object`; writes:sql |
| `d087-migrate-to-tenant-schemas.ts` | 2026-03-17 | schema: `boundary.`, `canonical_object`; writes:sql |
| `d225-generate-canonical-chain.js` | 2026-04-10 | writes:sql + hardcoded env |
| `d225-generate-phases-4-7.js` | 2026-03-29 | env: `version 1.0`; writes:sql |
| `d228-create-primary-bfs.js` | 2026-03-31 | writes:sql + hardcoded env |
| `d228-generate-source-chain.js` | 2026-03-31 | writes:sql + hardcoded env |
| `d228-populate-field-map.js` | 2026-03-31 | writes:sql + hardcoded env |
| `d299-populate-sap-aliases.mjs` | 2026-04-09 | writes:sql\|spawns |
| `d364-seed-date-dim.mjs` | 2026-04-20 | writes:sql + hardcoded env |
| `d364-seed-fiscal-calendars.mjs` | 2026-04-21 | tenant: `demo-selenite`; writes:sql |
| `demo-full-lifecycle.mjs` | 2026-03-15 | tenant: `demo-full`, `demo-selenite`; schema: `boundary.`; env: `version 1.0`; spawns |
| `finance-co-versions.js` | 2026-03-31 | env: `version 1.0`; writes:sql\|spawns |
| `finance-kpi-phase2-4.js` | 2026-03-31 | writes:sql\|spawns |
| `finance-kpi-promote.js` | 2026-03-31 | writes:sql + hardcoded env |
| `fix-binding-entity-names.mjs` | 2026-04-17 | writes:sql + hardcoded env |
| `fix-metric-subdomains.mjs` | 2026-03-15 | writes:sql + hardcoded env |
| `fix-missing-sap-ocs.mjs` | 2026-04-05 | env: `version 1.0`; writes:sql |
| `fix-oc-relevance.mjs` | 2026-04-05 | writes:sql + hardcoded env |
| `mc-diagnose-runway.mjs` | 2026-05-08 | tenant: `tbc_selenite_dev`, `demo-selenite`, `selenite`; schema: `boundary.`, `canonical_object`; writes:sql |
| `migrate-5d-classification.mjs` | 2026-04-05 | writes:sql |
| `migrate-maturity-5stage.mjs` | 2026-04-05 | writes:sql |
| `provision-apex.ts` | 2026-05-08 | tenant: `tbc_apex_dev`, `apex`; writes:sql |
| `seed-catalog-greenfield.mjs` | 2026-04-04 | writes:mongo + hardcoded env |
| `seed-fi-reader-multi-table.mjs` | 2026-03-15 | writes:sql + hardcoded env |
| `seed-import-archives.mjs` | 2026-04-04 | writes:mongo + hardcoded env |
| `seed-metric-references.js` | 2026-03-20 | writes:sql + hardcoded env |
| `seed-metrics-load-mega-csv.mjs` | 2026-04-05 | writes:mongo + hardcoded env |
| `seed-metrics-merge-internet.mjs` | 2026-04-05 | writes:mongo + hardcoded env |
| `seed-metrics-merge-ts-packs.mjs` | 2026-04-05 | writes:mongo + hardcoded env |
| `seed-observation-contracts-v2.mjs` | 2026-04-05 | env: `version 1.0`; writes:sql |
| `seed-observation-contracts.mjs` | 2026-03-15 | env: `version 1.0`; writes:sql |
| `seed-readers-flavors.mjs` | 2026-04-29 | writes:sql + hardcoded env |
| `seed-source-admission-contracts.mjs` | 2026-03-15 | env: `version 1.0`; writes:sql |
| `seed-source-contracts-v2.mjs` | 2026-04-06 | env: `version 1.0`; writes:sql |
| `seed-standard-fields.mjs` | 2026-04-10 | writes:sql |
| `sweep-evaluate-mcs.mjs` | 2026-04-17 | tenant: `tbc_selenite_dev`, `demo-selenite`, `selenite`; schema: `boundary.`, `canonical_object`; spawns |
| `test-canonical-evaluation.js` | 2026-02-28 | schema: `boundary.`, `canonical_object`; env: `version 1.0`; writes:sql |
| `universal-kpi-promote.js` | 2026-03-31 | writes:sql\|spawns |

Cleanup priority for these is operator decision; not in this session's scope.

## 4. Trusted scripts (38)

Read-only, no hardcoding, safe to invoke. Listed for completeness:

`audit-bf-admission-d408-calibrated.mjs`, `audit-bf-admission-d408.mjs`, `audit-d409-bf-first-scan1-calibration.mjs`, `bf-bo-sourcing.js`, `build-d408-a1-asset-cf-binding-audit-packet.mjs`, `build-d408-asset-uplift-evidence-packet.mjs`, `build-d408-correction-required-review-packet.mjs`, `build-d408-iso-xchg-rate-evidence-packet.mjs`, `build-d409-asset-batch2-source-family-packet.mjs`, `build-d409-asset-model-conflict-sublane-packet.mjs`, `build-d409-asset-orphan-cf-batch1-packet.mjs`, `build-d409-bf-first-high-signal-scan1.mjs`, `build-d409-cc-credit-generic-bf-admission-rebind-packet.mjs`, `build-d409-cc-credit-orphan-cf-packet.mjs`, `build-d409-cc-credit-remaining-evidence-batch-packet.mjs`, `build-d409-cc-credit-remaining-orphan-cf-batch-packet.mjs`, `build-d409-cc-credit-revolving-credit-limit-evidence-packet.mjs`, `build-d409-cc-credit-total-credit-deployed-decision-packet.mjs`, `build-d409-intangible-asset-scoping-packet.mjs`, `build-phase1-final-acceptance-packet.mjs`, `build-phase2-run1-review-packet.mjs`, `d225-bo-clustering.js`, `d365-enrich-cc-posting-date.mjs`, `enrich-remaining-234.mjs`, `finance-enrich-formulas.js`, `finance-kpi-mapping.js`, `finance-secondary-bindings.js`, `lint-column-names.mjs`, `m3-preflight-inventory.mjs`, `mc-ai-eval.mjs`, `qa-sample-dry-run-30.mjs`, `review-apply-25.mjs`, `run-chain-batch.mjs`, `run-d408-correction-required-ai-panel.mjs`, `seed-classify-modules.mjs`, `seed-kpi-specs.js`, `validate-build-config.mjs`, `validate-build-output.mjs`.

## 5. Diagnostic scripts (67)

Read-only but with hardcoded tenant/schema/env. Useful for one-shot lookups; output is **not evidence** per the zero-claims policy. Not enumerated individually here (67 rows would bloat the document); full enumeration available by re-running the audit script (which is intentionally removed per §13/G24 — re-derive when needed).

Common hardcoding pattern: `localhost` + a port (`:3100`, `:5435`, `:27017`).

## 6. Sub-findings

| # | Finding | Severity | Action |
|---|---|---|---|
| **S0** | File-count drift: 156 baseline (Codex §8.1) → 160 (this audit). 4 new scripts added between 2026-05-18 and 2026-05-19. Not a defect — just baseline drift to record. Future audits should re-derive the count rather than carrying it forward. | low | Document |
| **S1** | **Zero CI workflow files in any surveyed repo.** No `.github/workflows/` exists in bc-core, bc-admin, bc-ai, bc-portal, or bc-docs. The §13 trailer enforcement gate cannot be wired into CI today because **CI does not exist as a substrate yet**. The CI harness session (next in the queue) is therefore the work that creates the CI substrate, not just configures it. | **high** | CI harness session scope clarified: it builds CI from scratch, not adds checks to existing CI |
| **S2** | Banding rule "deprecated" never fires today. Rule requires >6 months old AND not-invoked. Oldest file in tree is `test-canonical-evaluation.js` from 2026-02-28 (~2.7 months at 2026-05-19). Rule will start producing `deprecated` band hits around Sept 2026 against the current cohort. Catalog reports 0 deprecated correctly — that's the rule firing as designed, not a missing classification. | low | Document; re-run audit periodically |
| **S3** | Side-effect false-positive risk: any script whose source contains literal SQL/Mongo keywords (e.g. an audit script defining `PATTERNS = { writes_sql: /\b(INSERT|...)/i }`) gets flagged as having those side effects. Limited blast radius — only audit/lint/grep helper scripts hit this. Mitigation: manual triage when band doesn't match expected behavior. Observed self-classification of the audit script itself; defect-surface verdict was still `no` because call-site count was 0. | medium | Document; per-script manual triage when ambiguous |
| **S4** | `\bapex\b` regex correctly identifies the apex tenant in this audit but would catch false positives like the word "apex" in a comment in future. Severity low because no false positives observed in this run. | low | Document |
| **S5** | Bootstrap concern from build-plan §9 honoured: the audit script's own profile recorded in §0; script deleted in same commit as this document. Evidence preserved in this document only; the bootstrap script does not enter the persistent catalog. | n/a | Action complete in this session |
| **S6** | 117 of 160 scripts (73%) are not invoked from CI, package.json, runbooks, or other scripts. Many are genuinely one-shot artifacts of past sessions (e.g. `d228-*`, `d225-*`, `d087-*` series). They are not defect surfaces today but represent latent risk if a future operator re-invokes one without per-script audit. Not actionable in E2; flag for future "tree cleanup" session if operator decides scope reduction is worth doing. | medium | Document; future cleanup session candidate |

## 7. CI integration shape (handoff to CI harness session)

The CI harness session reads **two defect-tag sources**:

| Source | Where it lives | Update cadence |
|---|---|---|
| **gap-research G-findings** | `business-context-framework-inventory-gap-research.md` §2 G-findings table (G1, G6b, G7 + any future additions per ADR amendment) | When gap-research updates |
| **§2.9 defect-surface verdicts** | After combined inventory update lands: `business-context-framework-inventory.md` §2.9; this document's §2 (13 defect surfaces) is the source-of-truth feed | When E2 is re-run, or when an unsafe script is modified |

CI defect-tag-grep rule (specified in build-plan §13.5 + §13.7):

> Any modified file matching either source — a known defective service per G-findings, OR a defect-surface script per §2.9 — must carry a `CURRENT DEFECTIVE behavior` characterization tag in any new `describe(...)` block in a `*.characterization.spec.ts` file in the same PR.

Without the §2.9 source, CI's defect-tag enforcement misses the 13 helper-script defect surfaces — exactly the FEM F42 / PLN-c028cd helper-script-trust failure mode that produced the original 9h-wasted incident.

**S1 caveat:** since no CI workflows exist anywhere today, the CI harness session is creating the CI substrate, not configuring it. The trailer-presence check, build-plan-ID validator, defect-tag grep, and Phase0Impact validator are all net-new infrastructure.

## 8. Verdict downgrade decision (G24)

**Inventory §2.9 verdict shifts from coarse `default-untrusted` to:**

> **Per-script-banded with defect-surface verdict.** Helper scripts under `bc-core/scripts/` (160 source files as of 2026-05-19) are catalogued per `business-context-framework-helper-script-trust-catalog.md` (E2). Bands: trusted (38) / diagnostic (67) / unsafe (55) / deprecated (0). Hardcoding rate: 113/160 (70.6%). **Active defect surfaces: 13** (unsafe + invoked). The 13 defect surfaces are the CI tag-grep target for the second defect-tag source (besides gap-research G-findings) per build-plan §13.5/§13.7. Cleanup-candidate count: 42 unsafe-but-not-invoked scripts (not active defect surfaces today). No deprecated-band scripts currently (rule fires only on files >6 months old AND not-invoked; oldest file in tree is 2026-02-28).

The combined inventory update driver session (after E1 + E2 both land) carries this verbatim into §2.9.

## 9. What this evidence does NOT do

- Does not remediate any script. Catalog only. Per-band remediation is separate execution work outside this session's scope.
- Does not modify the inventory document — that lands in the combined inventory update driver session.
- Does not implement CI. CI harness is the next session in the queue; this document is the input it consumes.
- Does not classify `.sql` migration files or `.json` output artifacts. Source scripts only.
- Does not detect runtime invocation (e.g. dynamic `require(variable)`, scripts started via `node -e`). Static call-site grep only.
- Does not detect side effects performed by external libraries the script calls. Static keyword grep only.

## 10. Cross-reference

| Document | Why referenced |
|---|---|
| `business-context-framework-inventory.md` §2.9 | Holds the coarse `default-untrusted` verdict this document refines |
| `business-context-framework-inventory-gap-research.md` §8.1 G24 | Original gap finding (Codex 138/156 baseline) |
| `business-context-framework-failure-evidence.md` F42 | PLN-c028cd helper-script-trust failure mode; canonical example of why default-untrusted is correct |
| `business-context-framework-build-plan.md` §13.5, §13.7 | CI integration spec — defect-tag-grep rule, CI-vs-reviewer split |
| `docs/adrs/ADR-149ab2.md` | The authority context this audit informs (no direct ADR position, but the discipline pattern is from ADR Q9 + N30) |
| `business-context-framework-bc-seed-operational-state.md` (E1) | Sibling evidence document; combined inventory update lands both together |
