---
title: BCF × OAGIS Pass-1 Retrofit Batch 1 — Failure Closeout (2026-06-25)
description: Honest closeout of retrofit batch 1 — 5/5 packets OPERATOR_REVIEW, 0 substrate writes, 5 panel calls consumed. Documents the systemic Checker-First Preflight v1 gap (M6 rep-term leakage / M8 circular definition / M9 source-field-copy / admission-scope evidence rigor / invented industry enum) AND the transport-harness defect (shared rejection pattern detection ran post-hoc rather than mid-flight). Preserved as calibration evidence; no immediate rerun. Companion v2 doctrine doc + harness fix authored in same PR.
status: failure_closeout
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-retrofit-batch-1-failure
related_docs:
  - bcf-oagis-pass-1-retrofit-scoping-ledger-2026-06-25.md
  - bcf-oagis-pass-1-retrofit-checker-first-preflight-v2-doctrine-2026-06-25.md
  - bcf-oagis-pass-1-c1-v2-closeout-2026-06-24.md
  - bcf-oagis-pass-1-c2-closure-checkpoint-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
---

# BCF × OAGIS Pass-1 Retrofit Batch 1 — Failure Closeout

> **5/5 panels parked OPERATOR_REVIEW. 0 substrate writes. 5 panel calls consumed. Systemic Checker-First Preflight v1 gap identified. Transport-harness shared-rejection-pattern halt was post-hoc, not mid-flight. Retrofit halted per operator 2026-06-25.**

> This document records the failure as calibration evidence per BareCount session discipline (D268). Companion doctrine doc `bcf-oagis-pass-1-retrofit-checker-first-preflight-v2-doctrine-2026-06-25.md` formalises the lessons.

## 1. Transport outcome

| Row | proposedName | HTTP | wall ms | outcome | panel_run_uid | char_id | lifecycle |
|---:|---|---:|---:|---|---|---|---|
| 1 | `product name` | 200 | 148,916 | parked OPERATOR_REVIEW | `bea43944-bba4-4e76-82f9-15ca8acae253` | (null) | (null) |
| 2 | `brand name` | 200 | 74,496 | parked OPERATOR_REVIEW | `601a8d22-eb58-4c31-8487-d2c7e07609a0` | (null) | (null) |
| 3 | `serial number specification description` | 200 | 136,735 | parked OPERATOR_REVIEW | `43c1b468-8488-4180-8327-31e42d0cef8a` | (null) | (null) |
| 4 | `lot number specification` | 200 | 124,417 | parked OPERATOR_REVIEW | `31ad859a-ebe3-4037-821b-06accbe742a7` | (null) | (null) |
| 5 | `shelf life duration` | 200 | 170,252 | parked OPERATOR_REVIEW | `382a47d3-0a9d-4e3f-94b6-74b21c82d935` | (null) | (null) |

Total wall time: 382 s (concurrency 2). 5/5 OPERATOR_REVIEW. 0 substrate writes.

Substrate verified live post-transport: 62 active + 20 draft characteristics (unchanged from session open). All 5 candidate terms absent from both active and draft listings. 5 rows added to `bcf.panel_output_record` (recorded panel events); no `concept_registry.characteristic_definition` writes; no `bcf.certification_record` writes.

Pass-1 panel cap consumed: 5 / 270 (cumulative across program now 80 / 270 = 29.6%).

## 2. Per-row Checker rationale (verbatim, from `bcf.panel_output_record.verdict_payload_json.review_reason`)

### 2.1 `product name`

> "Material Maker/Checker disagreement on createCharacteristic admission. Checker raises blocking Vocabulary Admission Checklist concerns: **M6 rep-term leakage** because 'product name' may be a domain-qualified use of the representation term 'name'; **M8 circular definition** because the definition uses 'name' to define 'product name'; **M9 source-field-copy risk** because the term appears directly in cited source artefacts such as OAGIS item-master.product-name and EDI product-name usage. Checker also disputes the Maker's cross_function admission_scope, noting the evidence may be product/commerce-function scoped rather than clearly observed across two or more business functions. Because createCharacteristic approval requires every M1-M10 MUST to pass and a valid scope with preconditions met, this cannot be auto-approved."

**Defect classes:** M6 + M8 + M9 + admission_scope dispute.

### 2.2 `brand name`

> "Material Maker/Checker disagreement on createCharacteristic Vocabulary Admission Checklist M9. Maker asserts 'brand name' is a system-agnostic authored business concept because it is anchored across OAGIS, GS1, ISO 22005, WIPO, ANSI X12, and EDIFACT; Checker raises a blocking concern that the proposed term may be a **direct source-field copy of OAGIS 'brand-name' with only punctuation normalized**."

**Defect classes:** M9 source-field-copy.

### 2.3 `serial number specification description`

> "createCharacteristic is not APPROVE-eligible because the proposed term appears to be a **source-field copy**: 'serial number specification description' is a trivial space-separated transformation of the OAGIS element name 'serial-number-specification-description'. The other cited standards provide topical support for serialisation-scheme documentation but do not establish the proposed term as shared governed business vocabulary. The term also has **representation-term leakage because it ends with 'description'**, a text/prose representation framing, rather than naming the business property itself. Admission scope is unclear and undeclared: the evidence suggests function_scoped item master / product data management or possibly industry_scoped traceability, but no valid admission_scope with required business_function or industry is present."

**Defect classes:** M9 + M6 (description rep-term) + admission_scope undeclared.

### 2.4 `lot number specification`

> "createCharacteristic is not approve-eligible because **admission_scope is absent/undeclared and cannot be responsibly inferred**: the evidence spans multiple regulated industries/regimes (pharmaceuticals, foodstuffs, agriculture, traceability standards) without a single declared industry for industry_scoped admission, and the concept does not clearly qualify as cross_function or function_scoped. Operator judgment is required on scope and industry-taxonomy granularity before governed-vocabulary expansion."

**Defect classes:** admission_scope rigor failure (multiple industries cited, none declared as scope).

### 2.5 `shelf life duration`

> "The characteristic meaning is well-grounded and the term is not a synonym of the active governed vocabulary, but the industry-scoped recommendation cannot be responsibly auto-approved because the supplied industry value **'regulated_perishables' appears to be an unverified or newly invented BareCount industry code**. Operator must confirm or normalize the industry/regulatory-scope value before vocabulary admission."

**Defect classes:** invented industry-enum value (Maker-side recommendation chose an industry code not in BareCount's closed enumeration). Note: meaning was judged well-grounded.

## 3. Cross-row pattern analysis

| Defect class | Rows affected | Count |
|---|---|---:|
| M9 source-field-copy | 1, 2, 3 | 3 |
| M6 representation-term leakage | 1, 3 | 2 |
| M8 circular definition | 1 | 1 |
| admission_scope evidence-rigor failure | 1, 3, 4 | 3 |
| invented industry-enum value | 5 | 1 |
| Meaning well-grounded but operationally blocked | 5 | 1 |

The dominant pattern is **M9 source-field-copy + admission-scope rigor**. The C1 "mechanical transliteration" trap surfaced repeatedly in late-2026-06-24 C1 retry passes (see `bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md` §3 and the C2 calibration corpus in `bcf-oagis-pass-1-c2-closure-checkpoint-2026-06-25.md`). It resurfaced here at the retrofit-batch-1 layer.

Row 5 (`shelf life duration`) is the cleanest signal: Checker explicitly said meaning is well-grounded; the failure was operational (admission_scope value `'regulated_perishables'` not in BareCount's industry enumeration). This identifies row 5 as the highest-confidence pilot for v2 doctrine validation (per operator 2026-06-25 framing).

Rows 1, 2, 3 are blocked by M6 + M9 + admission-scope — they require **genuine re-authoring** with substantive head nouns and BareCount business vocabulary, not transliteration of OAGIS source-field names. Operator framing 2026-06-25: "do not retry `product name`, `brand name`, or `serial number specification description` until their terms are genuinely re-authored, not transliterated."

Row 4 (`lot number specification`) blocked by admission_scope rigor (multiple industries cited without picking one). Potentially salvageable with operator framing on whether to declare a specific industry or to re-scope as cross_function with rigorous function-by-function evidence.

## 4. Root-cause analysis — Checker-First Preflight v1 gap

The Session 10 worksheet (`bcf-pass-1-retrofit-batch-1-checker-first-worksheet-2026-06-25.md`) used a **5-Q Pass-1 Checker-First rubric**:

- Q-A: substrate-sibling search
- Q-B: precision-tail / role-qualifier strip
- Q-C: why-not-bc-binding
- Q-D: ≥2 standards anchors
- Q-E: AMBER classification stable

All 5 packets passed 5/5 SURVIVE locally. None of the 5 questions covered the defect classes the live Checker actually raised:

| Defect raised by live Checker | v1 Q covering it | v1 verdict |
|---|---|---|
| M6 rep-term leakage | (none) | not checked |
| M8 circular definition | (none) | not checked |
| M9 source-field-copy / transliteration | (none) | not checked |
| admission_scope evidence rigor | (none — Q-D checks standards count but not function-evidence) | not checked |
| invented industry-enum value | (none) | not checked |

The 5-Q rubric was insufficient as a panel-equivalent local Checker.

**This was a Session 10 authoring miss.** The C1 v2 closeout and C2 closure-checkpoint had documented the M6/M8/M9 + admission-scope-rigor patterns in their calibration corpus. The Session 10 worksheet did not import them. Per operator: "This is a real miss, and the transcript's self-audit is basically right."

## 5. Root-cause analysis — Transport-harness defect

`scripts/_pass1-retrofit-batch-1-transport.mjs` v1 carried a `shared_rejection_pattern` detection check but ran it **post-hoc**, only after all 5 packets completed:

```javascript
// Post-hoc: shared-rejection-pattern detection
const parkedRows = state.outcomes.filter(o => o.outcome.class === 'parked');
let sharedPattern = null;
if (parkedRows.length >= 3 && parkedRows.length === state.outcomes.length) {
  const codes = new Set(parkedRows.map(o => o.outcome.verdictCode));
  if (codes.size === 1) sharedPattern = { verdictCode: [...codes][0], parkedAll: true, rows: parkedRows.length };
}
```

The check ran correctly — it detected `verdictCode='OPERATOR_REVIEW'` shared across all 5 rows — but only AFTER all 5 panels had executed. By the time the pattern was detected, the cost was already paid.

Per operator framing pre-transport ("halt on any service error or unexpected shared rejection pattern"), the check should have run after EACH row's outcome was recorded, with the trigger condition firing after row 2 (or 3) had returned the same parking verdict, halting remaining packets. **3 panel calls wasted** because the check was post-hoc.

This is an operator-stated hard precondition: "Fix the transport harness before any next panel."

## 6. Substrate state (verified live)

| Metric | Pre-batch-1 | Post-batch-1 | Delta |
|---|---:|---:|---:|
| Active characteristics | 62 | 62 | 0 |
| Draft characteristics | 20 | 20 | 0 |
| Active entities | 29 | 29 | 0 |
| Active value BCs | 194 | 194 | 0 |
| Active certification records | (n) | (n) | 0 |
| `bcf.panel_output_record` rows | (n) | (n+5) | **+5** |
| Pass-1 panel cap consumed (cumulative) | 75 / 270 | 80 / 270 | +5 |

Foundation invariant III (immutability) honoured: no substrate state corrupted; panel records are append-only audit data.

## 7. Self-audit (D268)

| Discipline rule | Honoured? | Note |
|---|---|---|
| One-then-many | **Failed in spirit.** The 5-row batch transported without a 1-row pilot first. C2 closeout established this discipline; retrofit did not carry it forward. Operator's revised framing reasserts 1-row-pilot-first for `shelf_life_duration`. |
| Independent verification | Honoured. Substrate state queried live post-transport via API; panel rationale read direct from `bcf.panel_output_record.verdict_payload_json` via SQL. No reliance on summary docs. |
| No bulk substrate writes | Honoured trivially (0 writes). |
| Cosmetic status changes avoided | Honoured. |
| Self-audit at session close | This document. |
| If a shortcut tempts, stop and flag it | The transport-script post-hoc halt WAS the shortcut. It satisfied a literal reading of "detect shared rejection pattern" without satisfying the operational intent. Flagged here; fixed in companion harness v2 commit. |
| No lower-layer compensation | The temptation to "tune the definitions until they pass" would be lower-layer compensation for upper-layer doctrine gap. Avoided. Doctrine v2 is the right repair location. |

The script-side defect (post-hoc shared-pattern halt) is the second-order miss the operator caught. Worth noting because it's the kind of "checkbox completed" failure mode that hides under literal compliance.

## 8. Files committed

- `bc-docs-v3/docs/implementation/bcf-oagis-pass-1-retrofit-batch-1-failure-closeout-2026-06-25.md` — this document
- `bc-docs-v3/docs/implementation/bcf-oagis-pass-1-retrofit-checker-first-preflight-v2-doctrine-2026-06-25.md` — companion v2 doctrine (8-Q + admission-scope appendix)
- `barecount-devhub/scripts/_pass1-retrofit-batch-1-transport.mjs` — v1 transport script (preserved for audit; harness defect noted in §5)
- `barecount-devhub/scripts/_pass1-retrofit-batch-1-transport-v2.mjs` — v2 transport script with mid-flight halt-on-shared-pattern (fix-forward; no amend)
- `barecount-devhub/.claude/pass1-retrofit-batch-1-transport-outcomes-2026-06-25.jsonl` — per-row outcomes
- `barecount-devhub/.claude/pass1-retrofit-batch-1-transport-summary-2026-06-25.json` — summary

## 9. Held — operator framing for next gate

Per operator 2026-06-25:
- **Halt retrofit transport. No immediate rerun.**
- **One-row pilot only** after v2 doctrine + harness fix lands: `shelf_life_duration` first.
- **Do not retry `product name`, `brand name`, `serial number specification description`** until genuinely re-authored (not transliterated).
- **PR #62 (Pass-2 entity doctrine) NOT amended.** This failure is Pass-1 characteristic admission / retrofit doctrine — kept separate.

Next session shape: one-row Checker-First Preflight v2 worksheet for `shelf_life_duration` under the new 8-Q + admission-scope appendix. Operator gate before transport. If `shelf_life_duration` survives v2 panel run and operator approves, that validates the revised rubric; further retrofit batches can resume under v2.

Held.
