---
uid: DEC-ec341c
title: "Admission scope as primary policy axis (cross_function / function_scoped / industry_scoped)"
description: "Replace the F4-v2 v1 binary \"global vs everything-else\" admission gate with admission_scope as the primary policy axis. Three valid scopes (cross_function, function_scoped, industry_scoped) admit; five invalid scopes (source_system_specific, local_alias, implementation_artifact, source_field_copy, semantic_duplicate) reject. Function-scoped and industry-scoped admissions each carry five explicit preconditions. The non-APPROVE writer guard at registry-authoring-orchestrator.service.ts:293 stays intact — the fix is in the verdict-policy rubric (bc-ai Maker/Checker/Moderator) and the parallel bc-core validator (recommendation.validator.ts validateVocabularyFields), not in the writer-side authorization. classification ('global' / 'industry_specific' / 'system_specific' / 'alias_localization_candidate' / 'reject') becomes derived from admission_scope during a compat window, then removed. References §1.5 doctrine correction in bcf-oagis-pass-1-c1-rp2-parked-row-analysis-2026-06-25.md."
status: decided
date: 2026-06-24T12:54:50.003Z
project: bc-docs
domain: contracts
subdomain: bcf-admission-policy
focus: governance
---

# Admission scope as primary policy axis (cross_function / function_scoped / industry_scoped)

## Context

See decision text below.

# Context

Pass 1 C1 RP-3 transport (2026-06-24) provided empirical evidence that the F4-v2 v1 admission policy mis-routes valid scoped governed characteristics to OPERATOR_REVIEW. Of 13 transport calls: 1 APPROVE, 12 parked. Of the 12 parked, 7 were rejected explicitly because their classification was non-Global; the panel's own rejection text reads "F4-v2 v1 admits Global only; industry_specific / domain-scoped characteristics must be routed to operator review." (Wage type code, schedule type code, negotiated price authorization reference, transaction analysis code, product formulation reference, expiration control code, quality action resource category code.)

The §1.5 doctrine correction recorded in `bc-docs-v3/docs/implementation/bcf-oagis-pass-1-c1-rp2-parked-row-analysis-2026-06-25.md` (acknowledged inline 2026-06-25; taxonomy refined the same day to `cross_function` / `function_scoped` / `industry_scoped`) identified the root cause: the Global-only / Industry-Specific guard was authored to prevent source-system-specific, implementation-specific, local-alias, and source-field leakage. It is being mis-applied to also reject valid system-agnostic, evidence-backed characteristics whose scope is a single business function (workforce_payroll, accounting, quality_management) or a single industry (process_manufacturing). The anti-leakage instinct is correct; the binary `global` axis is wrong.

This ADR formalises the corrected admission rubric as the primary policy axis.

# Decision

## 1. Admission scope is the primary policy axis

A `registerCharacteristic` recommendation carries `admission_scope`, drawn from three valid scopes:

| Scope | Definition |
|---|---|
| `cross_function` | The value-property is substantively observed across two or more business functions. |
| `function_scoped` | The value-property is substantively observed across two or more systems / standards / frameworks within a single business function or subfunction, with the function stated explicitly. |
| `industry_scoped` | The value-property is required because a specific industry or regulatory context demands it (use only when the scope is truly an industry or regulatory regime, not merely a business function). |

A `function_scoped` recommendation additionally carries `business_function` (a stable BareCount business-function code). An `industry_scoped` recommendation additionally carries `industry` (a stable BareCount industry code). `cross_function` carries neither.

## 2. Five invalid scopes (reject targets)

The Maker / Checker / Moderator rubric must reject any candidate that reads as:

| Scope | What it is |
|---|---|
| `source_system_specific` | Value-property exists only in one source system; no cross-system evidence. |
| `local_alias` | Deployment-specific renaming of an existing governed characteristic. |
| `implementation_artifact` | Value-property exists only because of a particular implementation choice. |
| `source_field_copy` | Literal or near-literal rename of an OAGIS / SAP / Oracle source-field name without substantive conceptual reframing. |
| `semantic_duplicate` | Near-duplicate of an existing governed characteristic at the value-property layer. |

## 3. Function-scoped admission preconditions (all five required)

1. **Business function is explicit** — packet's `business_function` is a stable BareCount code, not free text.
2. **Term is system-agnostic** — proposed name and definition do not name a specific source system, product, or implementation.
3. **Definition is not source-narrow** — survives onboarding a second source system in the same function.
4. **Evidence is substantive** — citedText cites at least two systems / standards / frameworks in the same function. One OAGIS reference alone is insufficient.
5. **No accidental cross-function widening** — citation set and proposed scope agree.

## 4. Industry-scoped admission preconditions (all five required)

1. **Industry is explicit** — packet's `industry` is a stable BareCount code, not free text.
2. **Term is system-agnostic.**
3. **Definition is not source-narrow.**
4. **Evidence is substantive** — citedText cites at least two systems / standards / regulatory anchors within the same industry.
5. **No accidental cross-industry widening, no presenting an industry-driven characteristic as function-scoped or cross-function.**

## 5. Writer guard unchanged

`bc-core/src/registry/registry-authoring-panel/registry-authoring-orchestrator.service.ts:293` refuses to author any panel result whose `verdictCode !== APPROVED_VERDICT_V1`. **This guard stays intact.** The fix is upstream — make the verdict policy emit APPROVE_FOR_DRAFT for valid function-scoped and industry-scoped candidates that meet their preconditions; do not relax the writer-side authorization.

## 6. Compatibility plan for `classification`

The legacy enum (`global` / `industry_specific` / `system_specific` / `alias_localization_candidate` / `reject`) becomes derived from `admission_scope`:

| admission_scope | derived classification |
|---|---|
| `cross_function` | `global` |
| `function_scoped` | `domain_specific` (new derived value) or `industry_specific` (legacy) |
| `industry_scoped` | `industry_specific` |
| any invalid scope | `reject` |

`classification` continues to be persisted for one compat window, then is removed in a follow-up ADR. Packet JSON may continue to carry `classification` until the runtime fix lands; this is the residue documented in the §1.5 terminology note.

# Touchpoints (read-only inspection 2026-06-24)

## bc-ai (verdict-policy enforcement)

| File | Line(s) | What changes |
|---|---|---|
| `app/pipeline/registry_authoring_panel.py` | 94–98 (`_VOCABULARY_CLASSIFICATIONS`) | Extend or replace with `_ADMISSION_SCOPES = {"cross_function", "function_scoped", "industry_scoped", "source_system_specific", "local_alias", "implementation_artifact", "source_field_copy", "semantic_duplicate"}`; keep legacy set for the compat window. |
| `app/pipeline/registry_authoring_panel.py` | 824–852 (`_characteristic_recommendation_checks`) | Replace the `classification == "global"` check (lines 843–847) with: admission_scope ∈ {cross_function, function_scoped, industry_scoped}; when function_scoped → require business_function; when industry_scoped → require industry; emit OPERATOR_REVIEW only when an invalid scope is asserted or preconditions fail. |
| `app/prompts/registry-authoring/v1.0/maker.md` | (whole file) | Teach the three-scope rubric + five invalid scopes + ten preconditions. |
| `app/prompts/registry-authoring/v1.0/checker.md` | (whole file) | Same. |
| `app/prompts/registry-authoring/v1.0/moderator.md` | (whole file) | Same. |

## bc-core (parallel validator + persistence)

| File | Line(s) | What changes |
|---|---|---|
| `src/registry/registry-authoring-panel/recommendation.validator.ts` | 715–723 (`VOCABULARY_CLASSIFICATIONS`) | Mirror bc-ai admission-scope set. |
| `src/registry/registry-authoring-panel/recommendation.validator.ts` | 774–812 (`validateVocabularyFields`) | Replace the `rec.classification !== 'global'` check (lines 800–806) with the admission-scope validator. |
| `src/registry/registry-authoring-panel/registry-authoring-run.types.ts` + `.dto.ts` | (whole files) | Add `admission_scope`, `business_function`, `industry` to the recommendation type and DTO. |
| `src/registry/registry-authoring-panel/registry-authoring-orchestrator.service.ts` | **293 (writer guard)** | **No change.** Writer guard stays intact. |
| `bcf.panel_output_record` schema | (Database Change Protocol) | Persist three minimum fields as nullable columns: `admission_scope` (enum: cross_function / function_scoped / industry_scoped), `business_function_code` (text), `industry_code` (text). `business_function_code` is set only when `admission_scope = function_scoped`; `industry_code` is set only when `admission_scope = industry_scoped`; both are null for `cross_function`. **Do not pre-model subfunction or industry taxonomy tables in this DDL** — verdicting needs only the three text/enum values; if a closed subfunction or industry vocabulary becomes verdicting-relevant later, it lands in a follow-up ADR + DDL. Keep the DDL minimum. |

# Consequences

- **Function-scoped and industry-scoped governed characteristics can panel-approve.** RP-3's 7 policy-rejected rows (wage type, schedule type, negotiated price authorization reference, transaction analysis, product formulation reference, expiration control, quality action resource category) become re-transportable under the corrected rubric.
- **The Global-only assumption is removed from the verdict policy.** Cross-function characteristics still admit; function- and industry-scoped characteristics gain a legitimate APPROVE path that meets their explicit preconditions.
- **Writer-side authorization is unchanged.** The orchestrator service.ts:293 guard continues to refuse non-APPROVE authorings. Operator confirm flow (C5) is unchanged.
- **`classification` becomes derived.** Packet authors and downstream consumers may continue to read `classification` during the compat window. A follow-up ADR retires it once the compat window closes.
- **C1 RP-3 retry wave becomes possible.** Once bc-ai + bc-core land the policy change, the 12 transport-pending RP-3 packets (held in `barecount-devhub/.claude/desktop-prep-output-c1-rp3-2026-06-25/packets/c1-rp3/`) can re-transport with their existing admission_scope metadata. The 2 held rows (receipt routing code, job code) and the bc-ai Maker-null defect remain independent threads.
- **The §1.5 doctrine correction is now durable.** The inline doctrine acknowledgement in the rp2 analysis doc becomes formal at this ADR's `decided` flip; the analysis doc's §1.5.2 refinement-event record continues to capture the in-session evolution.

# Source-of-truth references

- `bc-docs-v3/docs/implementation/bcf-oagis-pass-1-c1-rp2-parked-row-analysis-2026-06-25.md` §1.5 — corrected admission rubric (terminology note, three valid scopes, five invalid scopes, function-scoped preconditions, industry-scoped preconditions).
- `bc-docs-v3/docs/implementation/bcf-oagis-pass-1-c1-rp3-packet-prep-2026-06-25.md` — 15 packets prepared under the corrected rubric; 13 panel-ready (1 confirmed, 12 transport-pending); 2 held.
- RP-3 r2 transport outcomes JSONL (`barecount-devhub/.claude/pass1-c1-rp3-transport-outcomes-2026-06-25.jsonl`) — empirical evidence of the policy gap (7 of 12 parked rows rejected for non-Global classification).
- Foundation Invariant VI ("Evidence is emitted, not inferred", `bc-docs-v3/docs/foundation/the-invariants.md`) — admission evidence including scope and business_function / industry must be emitted in the recommendation, not inferred at audit time.

# Implementation phasing (after `decided`)

The four implementation steps must land in this order to keep risk staged:

1. **bc-ai policy and rubric first.** Update `_VOCABULARY_CLASSIFICATIONS` and `_characteristic_recommendation_checks` in `app/pipeline/registry_authoring_panel.py`; rewrite the three rubric prompts in `app/prompts/registry-authoring/v1.0/` to teach the three valid scopes, the five invalid scopes, and the function-scoped / industry-scoped preconditions. This is the change that converts function-scoped and industry-scoped recommendations from OPERATOR_REVIEW to APPROVE_FOR_DRAFT. Verdict-side first because it is the policy decision; downstream cannot accept what upstream still rejects.

2. **bc-core validator and types second.** Mirror the scope set and validator change in `recommendation.validator.ts`; add `admission_scope`, `business_function_code`, `industry_code` to `registry-authoring-run.types.ts` and the corresponding DTO. The validator change keeps the two services in step so a bc-ai APPROVE_FOR_DRAFT is not rejected by the bc-core mirror.

3. **DBCP persistence third.** Database Change Protocol step: add the three nullable columns to `bcf.panel_output_record` per the touchpoints table above. Minimum scope; no subfunction or industry taxonomy. Run after (1) and (2) so the columns persist real values immediately, not empty placeholders.

4. **RP-3 retry wave last.** Re-transport the 12 transport-pending RP-3 packets from `barecount-devhub/.claude/desktop-prep-output-c1-rp3-2026-06-25/packets/c1-rp3/`. Packets already carry `admission_scope`, `business_function`, and `industry` metadata; no prep rework is needed.

The orchestrator writer guard at `registry-authoring-orchestrator.service.ts:293` is unchanged in every step. It is the seatbelt that refuses to author any non-APPROVE row, regardless of how the upstream policy decides. Do not weaken it.

# Status note

Decided 2026-06-24. Implementation begins in a separate controlled session in the four-step phased order specified above. Moves to `implemented` once bc-ai and bc-core ship the verdict-policy fix, the panel rubric updates land, and the DBCP persistence DDL applies. RP-3 retry wave is gated on `implemented`.
