---
metric: sda-c1-bf-cf-compatibility-amendment
metric_version: n/a
tenant: platform
source_system: n/a
work_type: adr-amendment-draft
session_uid: SES-594568
date: 2026-05-12
status: decision-pending
related_commits: []
related_tasks: []
related_adrs:
  - DEC-a17d0f
  - DEC-804874
  - DEC-69f09e
  - DEC-d72560
related_mwrs:
  - 2026-05-12-semantic-definitions-authority-design-SES-a223ea.md
  - 2026-05-12-pool1-trust-audit-46-producing-SES-594568.md
  - 2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md
  - 2026-05-12-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md
related_change_records:
  - CHG-28ab0c
repair_location: B
affected_boundary: contract_authoring
foundation_gate: passed
---

# Lane C C1 — BF-CF semantic compatibility gate (G11) — amendment draft to DEC-a17d0f

> **Filed as [DEC-b7affa](../../../../../governance/adrs/ADR-b7affa.md) (D404) on 2026-05-12.**

> **Draft only. Not filed as an ADR yet.** This MWR is the substance of an amendment to DEC-a17d0f (D403) that adds a deterministic gate **G11 — BF-CF semantic-family compatibility** to the SDA gate set, and the supporting schema decisions. After operator review, the substance is filed via `devhub_decision_record` with `amends: DEC-a17d0f` carried in the body. No schema execution proposed; one future DBCP is named (DBCP-1g) for the BF.semantic_family column.

## 0. Stance

This amendment closes the gap surfaced by the Apex Phase 0 walkthrough and confirmed by the Pool 1 trust audit:

> *G6 catches `data_type × unit_type` mismatch. G10 catches Meaning-once collisions. Neither catches "balance CF mapped to fiscal-year BF" because both are technically `number` and the cc_field_mapping signature is unique. — Phase 0 walkthrough §3 governance gap #1*

The Pool 1 audit then quantified the failure mode: **14 of 46 producing Apex MCs** map measure-currency CFs through fiscal-year or exchange-rate BFs without G1-G10 raising any objection. The chain is "complete" in the structural sense; the values are nonsense.

G11 closes this gap. It is **deterministic**, **most cases non-overridable**, fires at **cc_field_mapping authoring time**, and is independent of source-data inspection (it operates purely on declared metadata).

The amendment does **not** modify the SDA's six-state lifecycle, the five naming profiles, the existing G1-G10 specifications, or the phased rollout plan. It adds one gate. Per operator direction: *do not reopen DEC-a17d0f.*

## 1. The three failure cases this amendment addresses

Concrete examples from the Apex audit (per `chain-detail` traces):

### Case A — fiscal_year as a monetary measure

```
MC: mc__roa_return_on_assets (capital_structure_optimization)
Formula: O1 = (SUM(I1) / SUM(I2)) * C1
Variable I2.fieldCode = average_total_assets         (CF.semantic_family ≈ measure-currency)
cc_field_mapping target BF = actual_ledger_fiscal_year  (BF semantic = fiscal-year code, GJAHR)
resolution_rule_code = latest
Source: FAGLPOSE.GJAHR
```

The engine returns "the latest fiscal-year code" as the value of "average total assets". This is structurally impossible — a fiscal-year code is not a monetary amount. **G11 must reject this non-overridably.**

Companion case: `mc__accounts_payable_turnover_ratio` maps `average_accounts_payable` to the same BF. `mc__complete_the_monthly_consolidated_financial_statements` maps `days_to_consolidated_statements` to a fiscal-year BF.

### Case B — exchange-rate as a monetary cost

```
MC: mc__finance_function_it_costs_allocated_to_controls_and_risk_management
Variable I1.fieldCode = total_finance_function_it_costs  (CF.semantic_family ≈ measure-currency)
cc_field_mapping target BF = journal_entry_hdr_exchange_rate  (BF semantic = currency exchange rate ratio, KURSF)
resolution_rule_code = sum
Source: BKPF.KURSF
```

The engine sums exchange rates and presents the sum as "IT costs". A ratio is not a currency amount. **G11 must reject this non-overridably.**

Companion cases: `mc__overhead_rate.total_indirect_costs`, `mc__maintenance_cost_pct_of_asset_value.total_asset_value` — all map measure-currency CFs to exchange-rate BFs.

### Case C — credit_type_code as a credit-risk rating

```
MC: mc__high_risk_ar_exposure (accounts_receivable)
Variable I2.fieldCode = customer_credit_risk_rating  (CF.semantic_family ≈ code, code_vocabulary = credit_risk_rating)
cc_field_mapping target BF = credit_type_code  (BF semantic = code, code_vocabulary = credit_type)
resolution_rule_code = latest
```

The MC's formula filters by `customer_credit_risk_rating = 'HIGH'`. The BF supplies credit-type codes (e.g. wholesale/retail/government), not risk ratings. The numbers produced are unrelated to "high-risk AR exposure".

**G11 at the semantic_family level alone DOES NOT catch this case** because both CF and BF are in family `code`. Catching it deterministically requires a **subfamily / code-vocabulary identifier** on both sides. This amendment names that extension as **G11b** (deferred — schema work in a future DBCP), but does not implement it here.

## 2. Decision §1 — Add G11 to the SDA deterministic gate set

A new deterministic gate **G11 — BF-CF semantic-family compatibility** is added to DEC-a17d0f §4 alongside G1–G10. Its placement in the gate-ordering sequence:

- G1–G8 evaluate at primitive certification time (when a BF / BO / CF transitions `reviewing → certified`).
- G9 evaluates at reference-authoring time (when a new authoring entry — cc_field_mapping, MC variable binding, CM field-resolution, OC field-selection — is created/replaced).
- G10 evaluates at cc_field_mapping authoring time (Meaning-once collision check).
- **G11 evaluates at cc_field_mapping authoring time, alongside G9 and G10.** It runs after G9 (which checks that the target CF and BF are both certified) and before G10 (which checks signature collision).

G11 is deterministic: same input `(BF.semantic_family, CF.semantic_family, resolution_rule_code)` always produces the same verdict. It does not depend on bc-ai. It is computed from the compatibility matrix in §4 (decision §3).

## 3. Decision §2 — `semantic_family` on Business Fields

Per operator direction: `semantic_family` applies to BFs too, but as a **semantic-classification field** — not necessarily with the same usage as on CFs.

### 2.1 Conceptual scope

For CFs, `semantic_family` declares **what the metric variable expresses** (e.g. `measure-currency`, `dim-fiscal-period`). For BFs, `semantic_family` declares **what the underlying source-side concept represents** (e.g. `measure-currency` for an invoice amount column; `dim-fiscal-period` for a fiscal-year code column; `measure-ratio` for an exchange rate column).

The two usages are **structurally identical but semantically different in framing**: CF.semantic_family is read by the metric engine to verify the value-shape; BF.semantic_family is read by G11 to verify that the source-side wire-shape is compatible.

The closed enum is the same 24-value set from DEC-804874 (D366), seeded by DBCP-1a. **No new enum values** are introduced by this amendment.

### 3.5 Categorical ratings are `code`, not `measure-score`

Per matrix-review §5 M3: categorical ratings (HIGH / MEDIUM / LOW credit-risk ratings, customer-tier codes, performance-grade codes) are classified as `code` family — not as `measure-score`. `measure-score` is reserved for **numeric scores** (NPS 0-10, FICO 300-850, satisfaction 1-5). The Apex Case C example (`customer_credit_risk_rating` with values HIGH/MEDIUM/LOW) is therefore `code` family with `code_vocabulary_code = 'credit_risk_rating'`; its BF `credit_type_code` is also `code` with `code_vocabulary_code = 'credit_type'`. **Both are `code`; G11 passes at the family level; G11b (deferred) catches the code-vocabulary mismatch.** This classification keeps `measure-score`'s `compatible_data_types = {'number'}` (per DBCP-1a) clean and aligned with its numeric-score usage.

### 2.2 Schema implication — DBCP-1g (future, not in this amendment)

Adding `semantic_family` to `contract.business_field` requires a new DBCP. **This amendment names but does not author it:**

- **DBCP-1g** — Add `semantic_family TEXT` column to `contract.business_field`. Initially nullable. CHECK constraint references the closed enum once `master.semantic_family` exists via DBCP-1a. No backfill at execution time; population happens incrementally via the SDA's BF certification flow.

DBCP-1g sequences **after** DBCP-1a (`master.semantic_family` must exist before the CHECK on `business_field.semantic_family` references it) and **after** DBCP-1b (the BF table's status_code CHECK must already be broadened so BFs can be put through the certification flow). Recommended position in the DBCP sequence: 1a → 1c → 1f → 1b → 1g.

**Author timing:** DBCP-1g should be drafted alongside the Phase 1 service work, not in this amendment.

### 2.3 BF semantic_family population strategy

Three population paths, in order of authority:

1. **Operator-authored at BF certification (primary path).** When a BF is submitted for certification (currently 7,062 BFs, all in `draft`), the operator declares its `semantic_family` as part of the certification payload. The deterministic gate at certification (G5 on the BF side — newly applied per this amendment) requires the value to be present.
2. **AI-advisory pre-fill (assist path).** bc-ai's `POST /ai/api/semantic-definitions/semantic-family-suggest` proposes a `semantic_family` based on the BF's name, definition, source-field path, data_type, and any standards citation. The operator accepts or overrides. This is **advisory only** per DEC-a17d0f §5 — the lock is the operator's acknowledgement, not the AI verdict.
3. **Source-side heuristic projection (read-only convenience, not authoritative).** A diagnostic projection can derive a tentative `semantic_family` from the BF's `source_field_path` + source-system column-type metadata (e.g. SAP NETWR → measure-currency, GJAHR → dim-fiscal-period, KURSF → measure-ratio). This is **never written as the authoritative value**; it is shown to the operator as evidence during step (1).

For dev/pilot, paths (1) + (2) are sufficient. Path (3) is a future convenience surface and is out of this amendment's scope.

### 2.4 G5 on the BF side — new clarification, not new gate

DEC-a17d0f §4 G5 says "*`semantic_family` populated and in enum (CF only)*". This amendment **extends G5 to BFs**: a BF cannot be certified without `semantic_family` populated. Same gate code, broader scope. Non-overridable on both BF and CF sides (no change to the non-overridable status).

## 4. Decision §3 — Compatibility matrix

G11 evaluates a tuple `(BF.semantic_family, CF.semantic_family, resolution_rule_code)` against a **closed compatibility matrix**. The matrix is expressed by inclusion (accept patterns explicitly listed; everything else rejects).

### 4.1 Rule taxonomy

The 5 currently-supported resolution rules from DEC-d72560 are grouped by their effect on the BF value:

| Rule | Effect | Output shape |
|---|---|---|
| `sum` | Numeric aggregation across rows | inherits BF family if numeric |
| `latest` | Pick most-recent BF value | inherits BF family exactly |
| `assert_equal` | All rows must share BF value (dimension-only) | inherits BF family exactly |
| `count_distinct` | Count distinct BF values across rows | always `measure-count` |
| `count_where_not_null` | Count rows where BF is non-null | always `measure-count` |

The matrix uses the rule to determine what CF families are admissible.

### 4.2 Compatibility matrix (by CF family)

For each CF.semantic_family value, the matrix lists `(BF.semantic_family, rule)` accept patterns. Anything not listed is reject. Cells marked `review` are accept with rationale (overridable). Cells marked `accept` are non-overridable accept.

| CF.semantic_family | Accept patterns `(BF.family, rule)` |
|---|---|
| **`identifier`** | (identifier, latest) accept; (identifier, assert_equal) accept; (code, latest) review |
| **`code`** | (code, latest) accept *(subject to G11b code-vocabulary sub-check — see §7)*; (code, assert_equal) accept *(subject to G11b)*; (identifier, latest) review |
| **`name`** | (name, latest), (text, latest), (identifier, latest) accept |
| **`text`** | (text, latest), (name, latest) accept |
| **`measure-currency`** | (measure-currency, sum) accept; (measure-currency, latest) accept; (measure-currency, count_distinct) review; (measure-currency, count_where_not_null) review |
| **`measure-count`** | (identifier\|code\|name\|text\|measure-count, count_distinct/count_where_not_null) accept *(true counts of identifiers/categorical values)*; (measure-currency\|measure-ratio\|measure-percent\|measure-score, count_distinct/count_where_not_null) **review** *(counting rows-where-amount-is-non-null is funnel-padding at the rule layer — see matrix-review §3 M1)*; (date\|datetime\|period\|dim-*, count_distinct/count_where_not_null) **review** *(temporal/dimensional row-counts may be valid distinct-period counts but require rationale)*; (measure-count, sum/latest) accept |
| **`measure-ratio`** | (measure-ratio, latest) accept; (measure-ratio, sum) review *(summing ratios is unusual; flagged)* |
| **`measure-percent`** | (measure-percent, latest) accept; (measure-percent, sum) review |
| **`measure-score`** | (measure-score, latest) accept; (measure-score, sum) review *(summing scores is unusual)*. **Reserved for true numeric scores** (NPS 0-10, FICO 300-850 etc.). **Categorical ratings** (HIGH/MEDIUM/LOW etc.) are classified as `code` family with `code_vocabulary_code` per G11b, **not** as `measure-score` — see §3.5 |
| **`date`** | (date, latest), (date, assert_equal), (datetime, latest) accept |
| **`period`** | (period, latest), (period, assert_equal), (dim-fiscal-period, latest), (dim-calendar-date, latest) accept |
| **`datetime`** | (datetime, latest), (datetime, assert_equal) accept |
| **`duration`** | (duration, sum) accept; (duration, latest) accept |
| **`dim-calendar-date`** | (dim-calendar-date, latest), (dim-calendar-date, assert_equal), (date, latest) accept |
| **`dim-fiscal-period`** | (dim-fiscal-period, latest), (dim-fiscal-period, assert_equal), (period, latest) accept |
| **`dim-currency`** | (dim-currency, latest), (dim-currency, assert_equal) accept |
| **`dim-country`** | (dim-country, latest), (dim-country, assert_equal) accept |
| **`dim-legal-entity`** | (dim-legal-entity, latest), (dim-legal-entity, assert_equal) accept |
| **`dim-gl-account`** | (dim-gl-account, latest), (dim-gl-account, assert_equal) accept |
| **`dim-cost-center`** | (dim-cost-center, latest), (dim-cost-center, assert_equal) accept |
| **`dim-customer`** | (dim-customer, latest), (dim-customer, assert_equal) accept |
| **`dim-vendor`** | (dim-vendor, latest), (dim-vendor, assert_equal) accept |
| **`dim-product`** | (dim-product, latest), (dim-product, assert_equal) accept |

**Total cells:** ~50 accept + ~12 review patterns out of 24 × 24 × 5 = 2,880 possible cells. **The remaining ~2,800 cells reject.**

### 4.3 Matrix encoding

The matrix is encoded as either:
- a static config in the SDA service (recommended for Phase 1 — code is the source of truth, audit-reviewable in PR), or
- a `master.semantic_family_compatibility` table seeded via DBCP (deferred; more elaborate than Phase 1 needs).

Recommendation: **static config in Phase 1**, table-driven in a later phase if the matrix grows complex enough to justify it. Per DEC-a17d0f §7 the matrix lives in `bc-core/src/registry/semantic-definitions/gates.ts`.

### 4.4 Matrix governance

Changes to the matrix require an **amendment ADR** (same pattern as this one). The matrix is a closed-set artifact — adding a new accept cell or downgrading a reject to a review is a governance decision, not a code change. The compatibility matrix in DBCP-1a (`compatible_data_types` / `compatible_unit_types` per family) is a different, lower-level matrix concerned with the type/unit dimension; **the two matrices are independent and live in different surfaces.**

## 5. Decision §4 — Overridability classification

Per operator direction: classify which cases are non-overridable vs overridable.

### 5.1 Non-overridable G11 (Sev-1, hard reject)

A G11 reject is non-overridable when:

- The CF family is a **measure** (currency / count / ratio / percent / score) AND the BF family is a **temporal** (date / period / datetime / duration) or a **dimension** (any `dim-*`). E.g. averaging a fiscal year. **Structurally impossible.**
- The CF family is a **measure-currency** AND the BF family is **measure-ratio**, **measure-percent**, or **measure-score**, with `rule = sum`. E.g. summing exchange rates and calling the result a cost. **Type-shape mismatch under aggregation.**
- The CF family is a **temporal** (date / period / datetime) AND the BF family is a **measure**. E.g. taking a sum-of-amounts as a date. **Inversion of the above.**
- The CF family is a **dimension** AND the BF family is a **measure**. E.g. the customer dimension resolved from an amount column. **Identity vs measure inversion.**

These six families × six families ≈ 14 pattern classes form the **hard reject region** of the matrix. No operator override path exists for them. The rationale is that these patterns produce arithmetically defined but business-meaningless values — exactly the Apex Cases A and B in §1.

### 5.2 Overridable G11 (Sev-2, review-fail)

A G11 reject is overridable when:

- The CF family is `measure-*` AND the BF family is `measure-*` of a **different** measure type, with a rule that could plausibly bridge them (e.g. `measure-percent` CF from `measure-currency` BF via a derived calculation — rare but possible).
- The CF family is `name` or `text` AND the BF family is `identifier` or `code`. Defensible — a "name" CF might legitimately resolve to an identifier BF if the identifier IS the name in this source.
- Any cell marked `review` in the §4.2 matrix.

Override mechanic follows DEC-a17d0f §4 G2b pattern: rationale ≥ 40 chars + auto-spawned follow-up task tagged `sda-g11-override`. The override is recorded on the cc_field_mapping creation's certification-record-equivalent (since cc_field_mapping is not a primitive, the override row is persisted on a `cc_field_mapping_authoring_record` table — to be specified in a future DBCP; deferred).

### 5.3 The advisory tier (G11 cannot decide)

When the matrix cell is `review` AND the operator has already provided rationale during cc_field_mapping creation, G11 records the rationale and emits an `amber` advisory verdict. AI advisory may additionally evaluate the mapping for semantic plausibility per DEC-a17d0f §5; **the AI is non-blocking** per the SDA's permanent rule.

## 6. Decision §5 — Interaction with G6 and G10

Per operator direction: clarify how G11 interacts with the adjacent gates.

### 6.1 G6 — Data type / unit compatibility

G6 (DEC-a17d0f §4) compares `(CF.data_type, CF.unit_type_code, CF.semantic_family)` against the compatibility matrix in `master.semantic_family.compatible_data_types` / `compatible_unit_types`. **G6 operates on the CF side only.** It does not look at BF.

G11 operates on the BF↔CF pair. The two are independent and run independently:

- G6 evaluates at CF certification (BF / CF can be certified independently of each other; G6 catches "a measure-currency CF declared with data_type=string" before the CF is ever referenced).
- G11 evaluates at cc_field_mapping authoring (G6 must have passed for both BF and CF for the mapping to be authored; G11 verifies the BF-CF pair is compatible *given* their already-validated individual metadata).

**There is no double-counting.** G6 is "is each primitive internally consistent?". G11 is "is the binding between them semantically defensible?".

### 6.2 G10 — Meaning-once collision

G10 evaluates the canonical-JSON signature `(cc_id, bf_id, rule, filter_canonical, compute_canonical)` for collisions across already-certified CFs (Class-A, non-overridable) or under-review CFs (Class-B, overridable).

G11 evaluates the **type-semantic compatibility** of a single proposed mapping, irrespective of whether other mappings collide on the same signature.

Run order at cc_field_mapping authoring time (per DEC-a17d0f §4 gate ordering):

1. **G9** — both target CF and BF are in admissible certification states. Fails if either is not certified.
2. **G11** — BF.semantic_family ↔ CF.semantic_family compatibility per §4.2 matrix. Fails if reject.
3. **G10** — Meaning-once signature check. Fails Class-A if a certified CF already resolves through this signature.

**G9 → G11 → G10** is the recommended sequence. G11 must run after G9 because it depends on certified `semantic_family` values on both sides; it must run before G10 so a structurally invalid mapping is rejected before signature-collision is even evaluated (cheaper rejection path).

A mapping that passes all three is admissible. A mapping that passes G9 and G11 but fails G10 Class-A is a Meaning-once collision (the mapping is *type-compatible* with the CF, but another certified CF already owns the signature). A mapping that passes G9 but fails G11 is a type mismatch — independent of collision status.

### 6.3 Exclusion — G11 does not apply to `compute__derived` inputs

When the `cc_field_mapping` target BF is `compute__derived` (engine-derived, not source-mapped), G11 **skips evaluation** entirely. Engine-derived inputs are governed by the engine's derivation logic — a separate concern from BF-CF mapping type-shape compatibility. The CF's own `semantic_family` (e.g. `measure-count` for `number_of_overdue_invoices`) still applies to downstream evaluations; G11 only abstains on the BF-side comparison.

Concretely: G11 verdict for any `(compute__derived BF, *, *)` triple is **`n/a`** (not `accept`, not `reject`). The cc_field_mapping row is allowed to proceed through the remaining gates (G10 still runs on signature collision; G9 still runs on certification states). Engine-side correctness of the derivation is **governed elsewhere** — the engine-derivation governance is a future scope-gap candidate (the fourth named gap, surfaced in Pool 1 audit §5 R3), tracked as a separate amendment to DEC-a17d0f, **not in this amendment**.

Apex precedent: `mc__average_days_delinquent` (the 1 HIGH-trust producing MC from Pool 1) has both inputs as `compute__derived`. G11 abstains on these mappings; the metric's trust depends on the engine's derivation logic, not on G11.

### 6.4 Worked verdict for Apex Cases A, B, C

| Case | G9 | G11 | G10 | Net |
|---|---|---|---|---|
| **A** — `average_total_assets` (measure-currency) → `actual_ledger_fiscal_year` (dim-fiscal-period) | (n/a — neither certified yet) | **REJECT (non-overridable)** | (not reached) | Reject |
| **B** — `total_finance_function_it_costs` (measure-currency) → `journal_entry_hdr_exchange_rate` (measure-ratio), rule=sum | (n/a) | **REJECT (non-overridable)** | (not reached) | Reject |
| **C** — `customer_credit_risk_rating` (code) → `credit_type_code` (code), rule=latest | (n/a) | **PASS** at semantic_family level | Pass | **Pass at G11** — falls to G11b sub-gate (deferred) |

G11 catches Cases A and B with no override. Case C requires G11b.

## 7. Decision §6 — Deferred sub-gate: G11b code-vocabulary check

For mappings where both BF and CF are in family `code` (or both in family `identifier`), G11 cannot deterministically verify they reference the same code-vocabulary. The Apex Case C example (`customer_credit_risk_rating` mapped to `credit_type_code`) is precisely this shape.

**G11b — code-vocabulary identity check** is named here but **deferred for implementation**. It requires:

- A new `code_vocabulary_code` column (or equivalent) on `contract.business_field` and `contract.canonical_field` when `semantic_family = 'code'` or `semantic_family = 'identifier'`.
- A master table or controlled vocabulary catalog enumerating known code-vocabulary values (`credit_type`, `credit_risk_rating`, `account_class`, `material_type`, etc.). Closed by category, open by extension per ADR amendment.
- A deterministic check at cc_field_mapping authoring: if both BF and CF have `code_vocabulary_code` populated, the values must match (or be declared compatible via a small subfamily-compatibility matrix).

**This amendment does not author G11b.** It is named so that the gap is explicit; the schema work and gate-logic work belong in a later amendment + DBCP pair. Until G11b lands, **Case C is not caught deterministically**; it can only be caught by AI-advisory at cc_field_mapping authoring time (per DEC-a17d0f §5 advisory surface `mapping-meaning-once-explain`, which would need a code-vocabulary-aware prompt).

**Honest acknowledgement:** the operator's question ("how does C1 catch credit_type_code-as-risk-rating") gets a partial answer. G11 alone does not catch it; G11b is the deterministic answer; until G11b ships, AI-advisory is the only safety net for code-vs-code mismatches. Pilot-stage acceptable, but flagged.

## 8. Decision §7 — Where G11 fires + the Phase 2 integration

Per DEC-a17d0f §6 / §8, the cc_field_mapping authoring endpoints are:

- `POST /api/onboarding/cc/:id/field-mappings` (create)
- `POST /api/onboarding/cc/:id/field-mappings/:mid/replace` (D330-R5 replace)

G11 fires synchronously at both. The fail-response shape follows DEC-a17d0f §4 G10 convention: `{verdict: 'pass'|'fail-blocking'|'fail-review', gate_code: 'G11', detail: {bf_family, cf_family, rule, matrix_cell}, can_override: bool}`.

**Phase 2 integration:** G11 ships as part of Phase 2 (onboarding integration), alongside G9 and G10 preflight. It does not require a separate phase. Until Phase 2 ships, G11 is **observable** via a read-only projection (the SDA's stale-cc-field-mapping-references projection can be extended to surface G11 violations on existing mappings) but **does not block writes**. This mirrors the Phase 0 → Phase 2 enforcement curve already in the design.

**Phase 0 observability extension** (no code change yet, just a named diagnostic):
- `GET /api/semantic-definitions/projections/g11-violations` — lists cc_field_mapping rows where BF.semantic_family ↔ CF.semantic_family ↔ rule fails the §4 matrix. Useful for pre-Phase-2 cleanup planning. **Cannot run until both BF.semantic_family and CF.semantic_family are populated** — depends on DBCP-1g + BF certification flow.

## 9. Decision §8 — Implementation status + sequencing

| Step | Type | Authority | Status |
|---|---|---|---|
| This amendment | ADR amendment to DEC-a17d0f | Operator approval pending | Draft (this MWR) |
| DBCP-1a + 1b + 1c + 1f | Phase 1 substrate | Operator approval pending | Drafts on file |
| DBCP-1g (BF.semantic_family column) | New schema | Operator approval pending | **Named here, not authored** |
| BF certification flow (G5 extended to BFs) | Phase 1 service code | Phase 1 implementation | Pending Phase 1 start |
| G11 gate code | Phase 1 service code | Phase 1 implementation | Pending Phase 1 start |
| G11b code-vocabulary sub-gate | Future amendment | Future | **Deferred** |
| Phase 2 preflight integration (G9 / G10 / G11) | Phase 2 service code | Phase 2 | Per DEC-a17d0f §9 Phase 2 |

**Recommended DBCP sequence with G11 included:** DBCP-1a → DBCP-1c → DBCP-1f → DBCP-1b → DBCP-1g. DBCP-1g sits last because it depends on (i) `master.semantic_family` (1a), and (ii) the BF table's broadened status_code CHECK (1b).

## 10. Decision §9 — Decision boundary

This amendment **decides:**

- Adds G11 to the SDA deterministic gate set as defined in §2-§4 above.
- Extends G5 to apply to BFs (same gate code, broader scope).
- Names DBCP-1g for the BF.semantic_family column as a future operator-approved schema change.
- Establishes the compatibility matrix encoding pattern (static config in service code; promotable to a master table if needed).
- Classifies non-overridable vs overridable G11 cases (§5).
- Sequences G11 between G9 and G10 at cc_field_mapping authoring (§6).
- Catches Apex Cases A and B deterministically; defers Case C to G11b.

This amendment **does not decide:**

- The G11b code-vocabulary identity sub-gate (specified but deferred).
- The cc_field_mapping authoring record schema (where overrides are persisted; named but deferred).
- Backfill strategy for the 7,062 existing BFs' semantic_family values (population per certification flow; bulk-backfill is a later DBCP).
- Migration of existing cc_field_mapping rows that would fail G11 (the existing 144 collision groups + the fiscal_year/exchange_rate mappings — Phase 2 cleanup workflow per DEC-a17d0f §9 Phase 4).
- The exact wording of the AI-advisory prompt extensions for `mapping-meaning-once-explain` to be code-vocabulary aware (Phase 1 service code).
- Any change to G1, G2a, G2b, G3, G4, G6, G7, G8, G9, G10 specifications — unchanged.

## 11. Closing note

G11 is the missing piece between G6 (each primitive is internally consistent) and G10 (no two certified primitives collide). It is the **type-semantic correctness of the binding itself** — the gate that catches "balance mapped to fiscal-year" before it becomes a producing-but-untrustworthy metric.

The amendment is small in scope (one new gate + one named future schema column) but large in coverage. Per the Pool 1 audit, G11 would have rejected at least 14 of the 46 currently-producing Apex MCs at cc_field_mapping authoring time — the fiscal-year-as-source cluster alone — preventing them from ever entering the "producing dial" with semantically broken bindings.

The deferral of G11b (code-vocabulary) is honest: it acknowledges that the Apex Case C type of failure remains AI-advisory-only until further schema work. This is acceptable for dev/pilot; a follow-up amendment when the code-vocabulary catalogue is scoped will close it.

## 12. References

- **Anchor:** [DEC-a17d0f](../../../../../governance/adrs/ADR-a17d0f.md) (D403) — Semantic Definitions Authority. This amendment **does not supersede** DEC-a17d0f; it **adds** G11 to its gate set.
- **Closed enum source:** [DEC-804874](../../../../../governance/adrs/ADR-804874.md) (D366) — L-Node Semantic Gate. semantic_family closed enum, 24 values, hyphenated kebab-style.
- **Naming standard:** [DEC-69f09e](../../../../../governance/adrs/ADR-69f09e.md) (D148) — ISO 11179. P5 hyphenation divergence carried forward.
- **Canonical Field primitive:** [DEC-d72560](../../../../../governance/adrs/ADR-d72560.md) (D301, now superseded by DEC-a17d0f on lifecycle) — cc_field_mapping schema, 5 resolution rules.
- **Evidence MWRs:**
  - [Apex Phase 0 readiness walkthrough](2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md) — first surfaced the BF-CF compatibility gap as governance scope #1.
  - [Pool 1 trust audit](../../../../audits/onboarding/2026-05-12-pool1-trust-audit-46-producing-SES-594568.md) — quantified 14/46 producing Apex MCs as fiscal-year-bound; provided Cases A, B, C examples.
  - [Phase 1 DBCP drafts](../../../../dbcp/onboarding/2026-05-12-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md) — DBCP-1g named here sits after this draft sequence.
- **Foundation:** [the-invariants.md](../../../../../foundation/the-invariants.md) (I — Meaning is evaluated once; G11 is the type-shape complement to G10's identity-shape Meaning-once invariant).

## 13. Operator review checklist

- [ ] §1 three failure cases — confirmed Cases A, B caught; Case C deferred to G11b
- [ ] §2 G11 placement at cc_field_mapping authoring time, after G9 and before G10
- [ ] §3 BF.semantic_family added as a semantic-classification field; DBCP-1g named but not authored
- [ ] §3 G5 extended to BFs (same gate, broader scope) — clarification, not new gate
- [ ] §4 compatibility matrix encoding pattern (static config in service code)
- [ ] §4 specific accept/review patterns per CF family — operator review of the matrix table
- [ ] §5 non-overridable vs overridable classification accepted
- [ ] §6 G9 → G11 → G10 sequence accepted
- [ ] §7 G11b code-vocabulary sub-gate explicitly deferred
- [ ] §8 G11 ships in Phase 2 alongside G9/G10 preflight
- [ ] §10 decision boundary accepted (what this amendment decides / does not decide)
- [ ] Approved for filing as ADR amendment to DEC-a17d0f: _yes / no_

## 14. After this draft is approved

Two follow-ups, in order:

1. **File as ADR amendment** via `devhub_decision_record` with `decision_text` reproducing the substance of §2-§10. Title: "Amendment to DEC-a17d0f: BF-CF semantic-family compatibility gate (G11)". status=decided. No `supersedes_ref` (this is an amendment, not a supersession). The body references DEC-a17d0f as the anchor.
2. **Return to DBCP-1a matrix review using real Apex examples** (operator's named next step). The `compatible_data_types` / `compatible_unit_types` seed in DBCP-1a is currently "provisional"; reviewing it against the Apex chain-detail traces collected in the Pool 1 audit + Phase 0 walkthrough is the next read-only artifact.
