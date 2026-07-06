---
title: BCF × OAGIS Pass-1 Retrofit Checker-First Preflight v2 Doctrine (2026-06-25)
description: Revised Checker-First Preflight rubric for Pass-1 characteristic admission (retrofit-specific). 8-Q core + admission-scope mandatory appendix. Adds M6 rep-term leakage / M8 circular definition / M9 source-field-copy / admission-scope evidence rigor / closed-enum validation to the v1 5-Q rubric, after Session 11 retrofit batch 1 surfaced systemic v1 gaps (5/5 OPERATOR_REVIEW; full diagnosis in companion failure-closeout doc). Retrofit-scope only. Does NOT amend Pass-2 entity doctrine (PR #62).
status: doctrine_active
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-retrofit-checker-first-preflight-v2
related_docs:
  - bcf-oagis-pass-1-retrofit-batch-1-failure-closeout-2026-06-25.md
  - bcf-oagis-pass-1-retrofit-scoping-ledger-2026-06-25.md
  - bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-1-c2-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-2-entry-note-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
---

# BCF × OAGIS Pass-1 Retrofit Checker-First Preflight v2 — Doctrine

> Scope: **Pass-1 characteristic admission / retrofit doctrine only.** Does NOT amend Pass-2 entity doctrine. PR #62 (Pass-2 entry note Q-F amendment) stands unchanged.

> Authored after Session 11 retrofit batch 1 failed 5/5 OPERATOR_REVIEW under the v1 5-Q rubric. The failure modes (M6 rep-term leakage, M8 circular definition, M9 source-field-copy, admission-scope evidence rigor, invented industry-enum value) were known patterns documented in C1 v2 + C2 calibration corpora but not imported into the retrofit Preflight rubric. v2 closes the gap.

> Companion failure closeout: `bcf-oagis-pass-1-retrofit-batch-1-failure-closeout-2026-06-25.md`.

## 1. Why v2

The v1 rubric was a 5-question gauntlet covering substrate-sibling search, precision-tail strip, why-not-bc-binding, ≥2 standards anchors, and AMBER classification. It was Pass-2-entity-Checker-First-Preflight adapted to characteristic admission by stripping Q-F (fast-lane-acceptable) on the rationale that characteristics admit at draft, not active.

What v1 missed: the Vocabulary Admission Checklist M-rules (M6 / M8 / M9) that the live panel Checker enforces as MUST-pass gates for createCharacteristic, plus admission-scope evidence rigor and closed-enum validation. v1 had no question equivalent to these, so the worksheet was structurally non-panel-equivalent.

The C1 v2 closeout corpus (the C1 mechanical-transliteration trap) and the C2 closure-checkpoint calibration corpus already documented these patterns. They were not imported into the retrofit Preflight. v2 imports them.

## 2. v2 rubric — 8-Q + mandatory admission-scope appendix

A row SURVIVES if and only if **all 8 questions pass AND the admission-scope appendix is satisfied**. Any failure → HOLD or DOWNGRADE (re-author or re-scope).

### Q-A — Substrate sibling / synonym

Does any active or draft characteristic share the candidate's canonical_term, semantic root after rep-term strip, or known synonym? Search live substrate.

- **Active characteristic match by term:** map_to_existing (if route is map-to-existing, no panel — proceed to operator confirm gate).
- **Draft characteristic match by term:** must activate the draft first; then either map or re-author.
- **Semantic-root match after rep-term strip:** flag for Q-C analysis (may be a BC-binding candidate instead of new characteristic).
- **No match:** pass Q-A; proceed.

### Q-B — Role-only / precision-tail strip

If you strip role prefixes (`parent_`, `child_`, `planner_`, `supervisor_`, `actual_`, `estimated_`, `required_`) AND precision tails (`_description`, `_specification`, `_duration`, `_amount`, `_count`, `_total`, `_indicator`, `_code`), does the remainder reveal a sibling already in substrate?

- If yes: the candidate is a role-qualified or precision-qualified variant of an existing characteristic. Strongly favour BC-binding (with role_qualifier) over new-characteristic authoring.
- If no: pass Q-B.

### Q-C — Why not map-to-existing BC?

If Q-A or Q-B surfaced a sibling, you must justify why this row must be a new characteristic rather than a BC binding on the existing one. Acceptable rationales:

- The new characteristic carries a structurally distinct semantic that cannot be expressed by role-qualifying the existing one.
- The existing characteristic's value-property is incompatible with the new row's value-property at the shape level (different representation term).
- Multi-source standards convergence on the new concept (Q-D) treats it as a first-class business concept, not a sub-variant.

If no such rationale exists → DOWNGRADE to BC binding (no new characteristic; bind via existing).

### Q-D — Evidence strength

The candidate's `candidateEvidence` must cite:

- **≥2 independent published standards** anchoring the concept at the value-property level (not just the source-field name).
- Each standard cited must use the **value-property semantic** (the business meaning), not merely the source-field name. (e.g., citing "OAGIS has a `product-name` field" is not evidence of a shared business concept — it's evidence of a source-field name.)
- Standards must span **>1 organizational scope** (regulatory + industry-conventional, or multi-industry, or multi-region).

If only one standard, or all standards are single-jurisdiction-single-industry, or standards merely cite the source-field name → fail Q-D. Strengthen evidence or re-scope.

### Q-E — AMBER classification / slice stability

- Per A0.5 §5: confirm AMBER (not RED composite-identity).
- Confirm target slice is available in current substrate (post-E1/E2 state).
- If slice newly unblocked (e.g., asset-maintenance-simple post-E2 partial admission), confirm the binding doesn't require Equipment specifically (Equipment held per Equipment decision packet PR #65).

### Q-F — M6 rep-term leakage

> **New in v2.** This is the canonical trap that surfaced in retrofit batch 1 rows 1 + 3.

Does the proposed term end with a representation-term word?

Closed list of representation-term words (extend as catalog grows):
`name | code | identifier | description | amount | quantity | measure | date | time | text | value | number | flag | indicator | type | percent | rate | duration | count | total | status | reason | note`

If yes:

- The Checker is likely to flag the term as a **domain-qualified use of the representation term**, not a substantive business concept.
- The proposed term is a candidate for re-framing using a substantive head noun.
- **Example fixes:**
  - `product name` → `marketed product label` or `product identification name` (with the substantive head describing the role)
  - `brand name` → `commercial brand` (drops the rep-term suffix; `brand` is itself a substantive concept)
  - `serial number specification description` → `serialisation scheme` (drops both rep-term `specification` and rep-term `description`; `serialisation scheme` is the substantive concept)
  - `lot number specification` → `lot-numbering scheme` or `batch identification rule`
  - `shelf life duration` → `shelf life specification` (still ends in rep-term; better: `product shelf life`)

**Hard fail** if the rep-term word is the only semantic-bearing token after the qualifier (e.g., `name` alone, `code` alone, `amount` alone).

**Soft fail (DOWNGRADE)** if the rep-term word is present but the qualifier carries substantive semantic weight (e.g., `serial number` carries semantic weight; `specification` and `description` are rep-term tails to be stripped).

Pass condition: the term reads as a substantive business concept that an enterprise architect would recognise as a first-class member of the BareCount vocabulary catalog, not as "OAGIS field X transliterated."

### Q-G — M8 circular definition

> **New in v2.** Surfaced in row 1.

Does the definition body use any token from the proposed term — especially rep-term tokens — to define the concept?

- "product name = the name of a product as held in product master data" → circular (uses `name` to define `product name`).
- "shelf life duration = the duration over which a product is expected to remain usable" → circular (uses `duration` to define `shelf life duration`).

Fix: write the definition body using **different vocabulary** than the proposed term tokens. Describe what the concept IS by its operational role / business consequence / chain-of-custody position, not by tautological restatement.

- Anti-pattern: "Lot number specification = the specification of how lot numbers are assigned."
- Pattern: "Lot number specification = the master-data record governing how batch boundaries and identifiers are assigned during production runs. Distinguishes batch traceability under GS1, FDA 21 CFR 211.130, and ISO 22005 frameworks."

Q-G passes if the definition body avoids tokens from the proposed term (except where forced by trade vocabulary, e.g., naming the standard's own term — and only in standard-name citations, not in the definition's substantive body).

### Q-H — M9 source-field-copy / transliteration

> **New in v2.** The defining trap of retrofit batch 1 (rows 1, 2, 3).

Is the proposed term a trivial punctuation-or-case transformation of the cited source-field path's last element?

Mechanical checks:

- OAGIS path `noun.component.field-with-hyphens` → proposed term `field with hyphens` (hyphens-to-spaces). **Hard fail.**
- OAGIS path `noun.component.fieldCamelCase` → proposed term `fieldCamelCase` (no change). **Hard fail.**
- OAGIS path `noun.component.field-name` → proposed term `field name`. **Hard fail** (also Q-F rep-term).

Fix: the proposed term must use **BareCount business vocabulary**, not OAGIS source-field vocabulary. The OAGIS path is **evidence of the concept's existence**, not a naming source.

- Anti-pattern: OAGIS `item-master.item-master.brand-name` → `brand name`.
- Pattern: OAGIS `item-master.item-master.brand-name` evidence → BareCount canonical term `commercial brand` (with definition body citing OAGIS as source of the underlying concept, not as the source of the term).

Pass condition: the proposed term is genuinely authored using BareCount enterprise-architect vocabulary, demonstrably distinct from the source-field path's last element. The Checker test: "if I removed the OAGIS source-field name from the panel inputs, would the proposed term still make sense as a BareCount governed concept?"

## 3. Admission-Scope Appendix (mandatory)

Every characteristic admission MUST declare `admission_scope` AND satisfy the evidence-rigor and closed-enum requirements for the declared scope.

### 3.1 admission_scope values

| Value | Definition | Evidence required |
|---|---|---|
| `cross_function` | The value-property is observed across **≥2 distinct business functions** | Enumerate the ≥2 functions, with per-function evidence citation. E.g., "procurement (cited in PO source paths) + sales (cited in SO source paths)." Not "product-master crosses all functions". |
| `function_scoped` | The value-property is scoped to **a single business function** | Name the specific business_function from BareCount's published closed enumeration (see §3.3). |
| `industry_scoped` | The value-property is scoped to **a single industry** (regulatory or domain-specific) | Name the specific industry from BareCount's published closed enumeration (see §3.4). |

### 3.2 Function-by-function evidence rigor (cross_function)

If declaring cross_function, the worksheet MUST enumerate ≥2 functions with concrete per-function evidence. Not acceptable:

- "Product-master is a master-data attribute, so cross-function."
- "Used across procurement / sales / inventory."

Required:

- "Function 1: procurement — evidence: OAGIS `purchase-order.purchase-order-header.product-name` cited in 4 PO subtypes. Function 2: sales — evidence: OAGIS `sales-order.sales-order-header.product-name` cited in 6 SO subtypes."

Two functions with concrete citations. Three+ is better. If you can only name one function with citations → re-scope as function_scoped.

### 3.3 business_function closed enumeration

To be published by operator. Until published, function_scoped admission cannot proceed for novel function values. Existing BareCount canonical functions (from prior session context, treat as authoritative until catalog publishes): procurement / sales / inventory / production / quality / finance / hr / asset_management / logistics.

A function value NOT in this list is an invented enum → fail Admission-Scope appendix.

### 3.4 industry closed enumeration

To be published by operator. Until published, industry_scoped admission cannot proceed for novel industry values. Examples of **invented** industry values seen in retrofit batch 1: `regulated_perishables` (Maker-generated, not in any BareCount enum). Use of such values → fail Admission-Scope appendix.

If the candidate spans multiple regulated industries (e.g., pharmaceuticals + foodstuffs + agriculture — see retrofit batch 1 row 4 `lot number specification`), the worksheet author must:

- Pick the single most-relevant industry, OR
- Re-scope as cross_function with concrete function-by-function evidence (not industry-by-industry evidence — those are different axes), OR
- HOLD pending operator framing on whether to extend the industry catalog with a new closed-enum value.

### 3.5 Invented-enum check (final guard)

The Maker / Preflight author MUST verify that any `business_function` or `industry` value in the recommendation is from the published closed enumeration. New enum values require:

1. A separate operator-decision packet (analogous to the Equipment decision packet) proposing the new enum value with rationale.
2. Operator approval to extend the enumeration.
3. The enumeration update lands in BareCount catalog SSOT.
4. THEN the characteristic admission can use the new enum value.

Inline admission with invented enum values → fail.

## 4. Per-row verdict shape (revised)

Worksheets under v2 produce per-row verdicts in this shape:

| Field | Domain |
|---|---|
| Q-A | pass / fail-with-sibling |
| Q-B | pass / fail-strip-reveals-sibling |
| Q-C | pass / DOWNGRADE-to-bc-binding |
| Q-D | pass / fail-evidence-thin |
| Q-E | pass / fail-slice-unavailable / fail-Equipment-dependent |
| Q-F | pass / soft-fail-rep-term / hard-fail-rep-term-only |
| Q-G | pass / fail-circular |
| Q-H | pass / hard-fail-transliteration |
| Admission-Scope | pass / fail-scope-rigor / fail-invented-enum |

**Overall verdict:**
- 8/8 pass + scope pass → SURVIVE
- Any soft-fail or DOWNGRADE → DOWNGRADE (re-frame or re-scope before transport)
- Any hard-fail → HOLD (do not transport; genuine re-authoring required)

## 5. What v2 does NOT change

- v1 5-Q rubric for Pass-2 **entity** admission (PR #62) remains unchanged. Q-F (fast-lane-acceptable) applies to entities, not characteristics.
- The orchestrator surface (`POST /api/bcf/registry-authoring-runs` with `operation: 'createCharacteristic'`) is unchanged. No code changes required.
- The panel rubric (the Vocabulary Admission Checklist M1-M10 enforced by the live Checker) is unchanged. v2 brings local Preflight into parity with the live Checker's M-rules — it does NOT relax or extend the live Checker.

## 6. Adoption — gate / pilot

Per operator 2026-06-25 framing:

1. **Harness fix first** — transport script's shared-rejection-pattern check must run mid-flight (after row 2 or 3 trigger), not post-hoc. **Hard precondition before any next panel.** Implemented in `barecount-devhub/scripts/_pass1-retrofit-batch-1-transport-v2.mjs`.

2. **One-row pilot under v2** — `shelf_life_duration` first. Rationale: row 5's panel rationale was "characteristic meaning is well-grounded … industry value `'regulated_perishables'` appears to be an unverified or newly invented BareCount industry code." This isolates the v2 admission-scope appendix as the discipline-under-test, without simultaneously fighting M6/M8/M9. Validates the revised scope discipline.

3. **Do NOT retry** `product name`, `brand name`, `serial number specification description` until genuinely re-authored under v2 Q-F + Q-H. Hyphens-to-spaces transliteration is not authoring; new terms must be substantive BareCount business vocabulary.

4. **After `shelf_life_duration` pilot validates v2**, subsequent retrofit batches resume under v2 doctrine. Future batch worksheets carry the 8-Q + admission-scope appendix verbatim.

## 7. Scope locks honoured authoring this doctrine

- 0 panel calls.
- 0 substrate writes.
- 0 transport script invocations.
- 0 DDL changes.
- 0 ADR authoring (this is implementation doctrine, not a DEC — may warrant a DEC after pilot validates).
- 0 BC-coverage ledger changes.
- 0 A0.5 catalogue changes.
- 0 amendments to active / draft entities or characteristics.
- 0 amendments to PR #62 (Pass-2 entity doctrine kept separate per operator framing).

## 8. Held — next gate

`shelf_life_duration` v2 pilot worksheet authoring is the next session shape, after this PR lands and the v2 harness script is in place. Operator gates the pilot transport.
