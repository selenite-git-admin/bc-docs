---
uid: DEC-8391fd
title: "Cross-Model Architecture Audit — Gemini Deep Research (4-Pass)"
description: "Records the Gemini CLI 4-pass architecture audit (2026-04-05), cross-checked findings, and 4 resulting action tasks"
status: implemented
subdomain: governance-agent
focus: one-shot-arch-audit
date: 2026-04-05
decision_code: D270
project: platform
domain: platform
refs:
  - type: document
    path: "reports/gemini-architecture-audit-2026-04-05.md"
    label: "Full audit report (Gemini + Claude cross-check)"
  - type: task
    uid: TSK-8e7401
    label: "GDPR Nullification Object design"
  - type: task
    uid: TSK-5930bb
    label: "Add .defaultRandom() to source table PKs"
  - type: task
    uid: TSK-41d463
    label: "Standardize created_by_name in version tables"
  - type: task
    uid: TSK-a9f50b
    label: "Sync 02-contract.sql with admission_contract"
migrated_from: legacy v2 archive
---

# Cross-Model Architecture Audit — Gemini Deep Research (4-Pass)

## Context

As BareCount's architecture matures (199 ADRs, 10 platform modules, 6 contract families), independent verification becomes valuable. A cross-model audit — using Gemini CLI (gemini-2.5-pro) as the auditor and Claude Code as the cross-checker — was conducted to identify blind spots, contradictions, and implementation drift that might be missed by the primary development AI.

The audit was prompted by Gemini CLI's availability for deep research tasks via direct CLI invocation.

## Decision

### Methodology

Four sequential passes, each with curated context from legacy v2 archive and bc-core:

| Pass | Focus | Inputs |
|------|-------|--------|
| 1 | Philosophy & Principles | Foundation spec, patent, execution model, binding chain (~15 docs) |
| 2 | Architecture & Schemas | 6 contract schemas, P01-P10 dossier specs (~50 docs) |
| 3 | Implementation Fidelity | DDL (docker/redesign/) vs Drizzle ORM schemas |
| 4 | Synthesis | Consolidated findings from passes 1-3 |

All Gemini findings were then cross-checked by Claude Code against actual ADRs, code, and DDL.

### Platform Health Score: 8.4/10 (adjusted)

Gemini initially scored 8.2/10. After cross-check removed 1 hallucination and confirmed 1 issue as already-tracked, adjusted to 8.4/10.

### Findings Cross-Check

| # | Gemini Finding | Cross-Check Verdict | Detail |
|---|---------------|---------------------|--------|
| 1 | Metric Cardinality contradiction (1:1 vs N:1) | **Known & tracked** | FOUNDATION-CONTRADICTION-001. D021/D022 override Foundation v1. `co_bindings[]` supports N:M. TSK-c7fe0d tracks Foundation v2 fix. |
| 2 | admission_contract missing from DDL | **Partially wrong** | Missing from individual `02-contract.sql` but present in aggregated `02-platform-tables.sql` (deployment source). |
| 3 | Intervention Contract uses `body_json` | **False (hallucination)** | All 6 families use `contract_json` in both DDL and Drizzle. Verified line-by-line. |
| 4 | GDPR Nullification Object missing | **Genuine gap** | Zero ADRs, zero code, zero schema. Principles 2+8 conflict with GDPR Article 17. |
| 5 | Source table PK defaults missing in Drizzle | **Confirmed** | 6 source tables lack `.defaultRandom()`. DDL has `DEFAULT gen_random_uuid()`. |
| 6 | Version table governance inconsistency | **Confirmed** | Only `intervention_contract_version` and `canonical_mapping_version` have `created_by_name`. 4 others don't. |

### Top 5 Strengths Identified

1. **DOMNS Dual-Block Architecture** — genuinely novel (immutable attribute + mutable semantic block)
2. **ISO 11179 Naming Compliance** — world-class, integration-ready
3. **6-Family Contract Chain** — logically complete separation of concerns
4. **Bottom-Up BO Generation (D225)** — ensures platform state reflects observed facts
5. **16-Key Governance Header** — superior audit trail across all contract families

### Action Tasks Created

| Task | Priority | Scope |
|------|----------|-------|
| TSK-8e7401 — GDPR Nullification Object design | next (parked) | Architecture — needs its own ADR |
| TSK-5930bb — Add `.defaultRandom()` to 6 source PKs | next (planned) | Drizzle schema fix |
| TSK-41d463 — Standardize `created_by_name` in version tables | next (planned) | DDL + Drizzle schema fix |
| TSK-a9f50b — Sync `02-contract.sql` with admission_contract | next (planned) | DDL housekeeping |

## Options Considered

### Option A: Single-pass audit (rejected)
One large prompt with all docs. Rejected — context limits would force shallow analysis.

### Option B: Multi-pass with curated context (chosen)
4 sequential passes, each with targeted file bundles. Chosen — allows deep analysis per axis while staying within context limits.

### Option C: Manual architectural review (not considered)
Traditional architect review. Not practical for a single-developer project at this scale (199 ADRs, 120+ schema files).

## Consequences

### Positive
- Independent verification of architecture quality (8.4/10)
- 3 genuine gaps identified that were not previously tracked
- Cross-model approach caught 1 hallucination — validates the need for cross-checking AI findings
- Established a repeatable audit methodology for future use

### Negative
- Gemini hallucinated 1 finding (IC body_json) — all AI audit findings require cross-checking
- Audit is a snapshot in time — findings decay as code evolves

### Risks
- **Stale findings:** Action tasks must be executed promptly or re-verified
- **AI audit overconfidence:** Cross-checking is mandatory — never trust single-model findings for architectural decisions
