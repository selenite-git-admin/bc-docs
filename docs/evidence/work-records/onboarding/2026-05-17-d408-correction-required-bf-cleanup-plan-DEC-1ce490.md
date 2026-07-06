---
title: "D408 correction_required BF cleanup plan"
date: 2026-05-17
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
data_closeout: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md
guard_closeout: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-16-d408-service-guard-closeout-DEC-1ce490.md
session: SES-c5af8c
type: cleanup-plan
status: proposed
---

# D408 `correction_required` BF cleanup plan

**Design only. No DB writes. No SQL apply. No BF updates this session.** The artifact lists the 30 rows, classifies each, identifies governed correction paths, and names the operator decisions required before any apply.

## 1. Authority and scope

- **ADR:** [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md) — DEC-1ce490 / D408.
- **Data closeout:** [2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md](../../closeouts/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md).
- **Service-guard closeout:** [2026-05-16-d408-service-guard-closeout-DEC-1ce490.md](../../closeouts/onboarding/2026-05-16-d408-service-guard-closeout-DEC-1ce490.md).
- **Scope:** 30 BF rows currently in `catalog_state_code='correction_required'` (P0+P1+P2 from DBCP-1q-A). Each row must either be corrected and re-admitted to `certified_catalog` via the ledger, or demoted via the existing demote path.
- **Out of scope:** P3/P4 demoted rows (already terminal); 5,007 candidate_import triage (separate slice); any tenant DB / metric / CF row mutation.

### Foundation Gate

- **Repair location:** B (contract semantics — fix definition / type / family / provenance) with side at A (catalog admission boundary — emit `recertify_bf_catalog` ledger event so state moves back to `certified_catalog`).
- **Why not upper layers:** none; BF is foundational.
- **Why not lower layers:** lower-layer compensation (re-mapping CFs around bad BF types, tolerating wrong representation_term in evaluation) would violate "no compensation downstream of an upstream gap." The fix must live at the BF row.

## 2. Current state (verified 2026-05-17)

| Metric | Value |
|---|---:|
| `business_field` total | 7,062 |
| `certified_catalog` | 1,651 |
| `correction_required` | **30** |
| `demoted_catalog` | 374 |
| `candidate_import` | 5,007 |
| `recertify_pending` | 0 |
| Invariant `remediate_bf_semantics` | 1,392 ✓ held |
| `admit_bf_catalog` | 1,651 |
| `mark_bf_correction_required` | 30 |
| `demote_bf_catalog` | 374 |

## 3. The 30-row cohort

Ordered by CC-mapping count (highest first) then by reason code. `cc` = `cc_field_mapping` count; `alias` = `business_field_alias` count.

| # | name | reason | representation_term | data_type | def_len | `cc` | `alias` | `definition_standard` |
|---:|---|---|---|---|---:|---:|---:|---|
| 1 | `asset_net_book_value_amount` | type_incoherence | Text | number | 101 | **39** | 1 | – |
| 2 | `credit_type_code` | broken_fallback_definition | Code | code | 30 | **11** | 1 | OAGIS |
| 3 | `asset_cost_amount` | type_incoherence | Text | number | 93 | **10** | 1 | – |
| 4 | `xbrl_dividends_cash` | definition_too_short | Amount | number | 15 | 5 | 0 | US_GAAP |
| 5 | `asset_accumulated_depreciation_amount` | type_incoherence | Text | number | 100 | 5 | 1 | – |
| 6 | `ifrs_issued_capital` | definition_too_short | Amount | number | 14 | 3 | 0 | IFRS |
| 7 | `invoice_hdr_net_volume_measure` | broken_fallback_definition | Quantity | number | 39 | 2 | 1 | OAGIS |
| 8 | `ifrs_dividends_paid` | definition_too_short | Amount | number | 14 | 2 | 0 | IFRS |
| 9 | `freight_invoice_hdr_net_volume_measure` | broken_fallback_definition | Quantity | number | 39 | 1 | 1 | OAGIS |
| 10 | `price_list_line_type_code` | broken_fallback_definition | Code | code | 30 | 1 | 1 | OAGIS |
| 11 | `ifrs_borrowings_current` | definition_too_short | Amount | number | 19 | 1 | 0 | IFRS |
| 12 | `ifrs_current_liabilities` | definition_too_short | Amount | number | 19 | 1 | 0 | IFRS |
| 13 | `ifrs_purchase_of_property_plant_and_equipment` | definition_too_short | Amount | number | 16 | 1 | 0 | IFRS |
| 14 | `xbrl_inventory_gross` | definition_too_short | Amount | number | 16 | 1 | 0 | US_GAAP |
| 15 | `asset_salvage_value_amount` | type_incoherence | Text | number | 71 | 1 | 1 | – |
| 16 | `commercial_invoice_line_discount_amount` | type_incoherence | Text | number | 54 | 0 | 0 | – |
| 17 | `commercial_invoice_line_extended_amount` | type_incoherence | Text | number | 104 | 0 | 1 | – |
| 18 | `commercial_invoice_line_tax_amount` | type_incoherence | Text | number | 79 | 0 | 0 | – |
| 19 | `commercial_invoice_line_unit_price_amount` | type_incoherence | Text | number | 72 | 0 | 1 | – |
| 20 | `credit_transfer_payment_amount` | type_incoherence | Text | number | 88 | 0 | 1 | – |
| 21 | `debit_transfer_hdr_debit_transfer_amount` | type_incoherence | Text | number | 89 | 0 | 1 | – |
| 22 | `debit_transfer_payment_amount` | type_incoherence | Text | number | 114 | 0 | 1 | – |
| 23 | `invoice_ledger_entry_hdr_tax_amount` | type_incoherence | Text | number | 225 | 0 | 0 | – |
| 24 | `invoice_ledger_entry_hdr_total_invoice_amount` | type_incoherence | Text | number | 67 | 0 | 0 | – |
| 25 | `iso20022_camt_xchg_rate` | type_incoherence | Text | number | 57 | 0 | 0 | ISO_20022 |
| 26 | `payment_status_payment_payment_status_amount` | type_incoherence | Text | number | 172 | 0 | 0 | – |
| 27 | `warranty_claim_hdr_parts_cost_amount` | type_incoherence | Text | number | 64 | 0 | 0 | – |
| 28 | `warranty_claim_hdr_service_cost_amount` | type_incoherence | Text | number | 83 | 0 | 0 | – |
| 29 | `warranty_claim_line_repair_cost_amount` | type_incoherence | Text | number | 63 | 0 | 0 | – |
| 30 | `warranty_claim_line_unit_price_amount` | type_incoherence | Text | number | 101 | 0 | 1 | – |

All 30 rows have `bo_req_or_bk=0` and `sda_evidence=0`. None are business-keys.

## 4. Family breakdown

### 4.1 P0 — broken-fallback definition AND CC-mapped (4 rows)

| name | cc | example CC fields affected |
|---|---:|---|
| `credit_type_code` | **11** | `cc__credit` — 11 unrelated CFs (revolving_credit_limit, credit_application_submission_date, customer_credit_risk_rating, …) |
| `invoice_hdr_net_volume_measure` | 2 | `cc__invoice_hdr` (billing_volume, invoice_processing_volume) |
| `freight_invoice_hdr_net_volume_measure` | 1 | `cc__freight_invoice_hdr` (volume_of_duplicated_data) |
| `price_list_line_type_code` | 1 | `cc__price_list_line` (product_selling_price) |

**Highest concern:** `credit_type_code` is mapped to 11 distinct CFs in `cc__credit`. The CFs span the cc subject (limits, dates, ratings, decisions, completion dates) — a single `credit_type_code` BF cannot honestly back 11 such different canonical fields. This is almost certainly a "no better BF existed during CC authoring, so the operator picked the closest available" pattern. Definition fix alone will not resolve it; **binding review is required**.

### 4.2 P1 G1 — definition_too_short, well-known financial terms (7 rows)

All 7 are standard IFRS/US-GAAP balance sheet / cash flow line items with stub definitions (14–19 chars):

- IFRS: `ifrs_issued_capital`, `ifrs_dividends_paid`, `ifrs_borrowings_current`, `ifrs_current_liabilities`, `ifrs_purchase_of_property_plant_and_equipment`.
- XBRL/US-GAAP: `xbrl_dividends_cash`, `xbrl_inventory_gross`.

Definitions are dictionary-quality terms — every one has an established external standard reference (already populated: `definition_standard='IFRS'` or `'US_GAAP'`). Fix is sourcing the standard's published definition prose and ledgering it.

### 4.3 P2 G3 — type_incoherence, `representation_term=Text` with `data_type=number` (19 rows)

Mechanical class. Every row failed G3 with `incoherent_term_vs_type:Text/number`. All are `*_amount` or `*_rate` fields where `data_type='number'` is correct but `representation_term='Text'` was wrong (should be `Amount` for monetary; `Rate` for `iso20022_camt_xchg_rate`).

Sub-split by CC-mapping:

| Sub-class | Count | Notes |
|---|---:|---|
| Type-incoherence ∩ CC-mapped (P1+P2 overlap) | 4 | `asset_net_book_value_amount` (39 cc), `asset_cost_amount` (10), `asset_accumulated_depreciation_amount` (5), `asset_salvage_value_amount` (1) — all `asset_*_amount` |
| Type-incoherence, no CC | 15 | commercial_invoice_line_* (4), debit/credit_transfer_* (3), warranty_claim_* (4), invoice_ledger_entry_hdr_* (2), iso20022_camt_xchg_rate, payment_status_payment_payment_status_amount |

The fix for all 19 is a single `representation_term` correction. Most go to `Amount`; the one exception is `iso20022_camt_xchg_rate` which is a true rate → `Rate`. None require `data_type` change (the underlying value is correctly `number`).

### 4.4 Overlaps

- **None between P0 and P1.** P0 = broken_fallback (G1), P1 = definition_too_short (G1) — distinct G1 reasons; mutually exclusive per row.
- **P1 ∩ P2:** 4 rows (the asset_*_amount group) are both type-incoherent AND CC-mapped. These show up under P2 type_incoherence in the table because that's their assigned `catalog_state_reason_code`, but they also satisfy the "T4 hard-fail" cohort definition. They are classified P1 in DBCP-1q-A backfill semantics.
- **P0 ∩ P2:** zero. P0 rows are not type-incoherent (their reps/types are fine; only the definition is broken).

## 5. Risk ranking

Priority order for any apply (high → low):

1. **P0 (4 rows)** — bad definition AND active in canonical pipelines. Risk of CC mapping correctness already realised today; every metric evaluation that flows through these CCs is reading a BF with a junk definition.
2. **P1+P2 overlap, 4 `asset_*_amount` rows** — type-incoherent AND heavily CC-mapped (39 + 10 + 5 + 1 = 55 cc references). `asset_net_book_value_amount` alone backs 39 canonical fields; type incoherence here means every consumer reads `representation_term=Text` when reality is monetary.
3. **P1 7 definition-too-short** — 5 of 7 are CC-mapped (5 + 3 + 2 + 1 + 1 + 1 + 1 = 14 cc references across the cohort). External-standard prose available; fix is sourcing not authoring.
4. **P2 type-incoherence, no CC (15 rows)** — mechanical fix; no downstream consumer to disturb. Safest cohort.

**No metric or CF changes are in this slice.** Even when a CC field's underlying BF type representation changes from `Text` to `Amount`, the canonical_field's stored `data_type` and the metric formula are untouched. The fix lives entirely on the BF row.

## 6. Needed governed operations

### 6.1 Existing endpoints

| Endpoint | Mutates | Covers |
|---|---|---|
| `POST /api/business-fields/:id/remediate-semantics` (`bc-core` §12, DEC-a49413 v5) | `semantic_family`, `unit_type_code`, `definition_standard`, `standard_ref` | None of the 30 corrections directly — those fields are out of scope for this cohort (already populated or not the failing axis). |

### 6.2 Missing endpoints / paths

| Capability | Status | Recommended path |
|---|---|---|
| **Definition correction (definition text only)** | **Missing.** | New narrow endpoint `POST /api/business-fields/:id/correct-definition` mirroring §12's pattern: atomic UPDATE of `definition` only + paired `certification_record` row with `action_code='recertify_bf_catalog'` AND `gate_signals_json` snapshot. Refuses if BF is not `correction_required` or if new definition still fails G1. |
| **Type / representation_term correction** | **Missing.** | New narrow endpoint `POST /api/business-fields/:id/correct-type`. Mutates `representation_term` and/or `data_type`. Refuses if pair is still G3-incoherent. **Pre-write CC impact check:** scan `cc_field_mapping` for `business_field_id=<id>`; if any CF has `data_type` differing from the new BF `data_type`, refuse with structured payload listing affected CCs (operator chooses to fix CFs first or override). For the 19 rows in this cohort the `data_type=number` is already correct, so only `representation_term` changes; no CF impact expected. |
| **Combined definition + type correction** | **Missing.** | Composable: call both endpoints in operator-chosen order; the ledger records two separate `recertify_bf_catalog` rows (each a complete event per Invariant VI). No "atomic both" endpoint needed; the state machine tolerates intermediate states because `recertify_bf_catalog` only mints `certified_catalog` once gates pass. |
| **Recertify ledger action** | **Exists** in `certification_record.action_code` CHECK (added by DBCP-1q-A `bc-core@513404d`). | Action code `recertify_bf_catalog` is already valid. No DBCP needed for it. |
| **Demote ledger action** | **Exists** — used by DBCP-1q-B (`demote_bf_catalog`). | Available if operator chooses to demote a row instead of correcting (e.g. if P0 `credit_type_code` binding review concludes "this BF should not exist; demote and re-bind CFs elsewhere"). |

### 6.3 New DBCPs / action_codes needed

**None.** All required ledger actions exist in the post-DBCP-1q-A CHECK enum. The only new artifacts are the two narrow endpoints in §6.2.

## 7. Per-row recommended disposition

Dispositions: `fix-definition` / `fix-type` / `fix-definition-and-type` / `demote` / `operator-evidence-required` (binding review before any data change).

| name | reason | cc | disposition | rationale |
|---|---|---:|---|---|
| `credit_type_code` | broken_fallback | 11 | **operator-evidence-required** | 11-CF spread strongly suggests CC binding error. Review whether each CF should re-bind to a more specific BF (e.g. `credit_facility_type_code`, `credit_decision_type_code`) before correcting the definition. |
| `invoice_hdr_net_volume_measure` | broken_fallback | 2 | fix-definition | Sourcable from OAGIS BIE description for `InvoiceHdr.NetVolumeMeasure`. CC bindings to billing_volume / invoice_processing_volume look semantically consistent with a volume measure. |
| `freight_invoice_hdr_net_volume_measure` | broken_fallback | 1 | fix-definition | Same shape as above for freight invoice. `volume_of_duplicated_data` CF binding name is odd — flag for operator confirmation but a definition fix is the primary action. |
| `price_list_line_type_code` | broken_fallback | 1 | fix-definition | Sourcable from OAGIS. CC binding to `product_selling_price` looks semantically dubious — flag for operator confirmation. |
| `asset_net_book_value_amount` | type_incoherence | 39 | fix-type | `representation_term: Text → Amount`. Definition (101 chars) is good. No CF impact (data_type stays `number`). |
| `asset_cost_amount` | type_incoherence | 10 | fix-type | Same as above. |
| `asset_accumulated_depreciation_amount` | type_incoherence | 5 | fix-type | Same. |
| `asset_salvage_value_amount` | type_incoherence | 1 | fix-type | Same. |
| `xbrl_dividends_cash` | def_too_short | 5 | fix-definition | Sourceable from US-GAAP taxonomy. Standard ref needed. |
| `ifrs_issued_capital` | def_too_short | 3 | fix-definition | Sourceable from IFRS. |
| `ifrs_dividends_paid` | def_too_short | 2 | fix-definition | Sourceable from IFRS. |
| `ifrs_borrowings_current` | def_too_short | 1 | fix-definition | Sourceable from IFRS. |
| `ifrs_current_liabilities` | def_too_short | 1 | fix-definition | Sourceable from IFRS. |
| `ifrs_purchase_of_property_plant_and_equipment` | def_too_short | 1 | fix-definition | Sourceable from IFRS. |
| `xbrl_inventory_gross` | def_too_short | 1 | fix-definition | Sourceable from US-GAAP taxonomy. |
| `commercial_invoice_line_discount_amount` | type_incoherence | 0 | fix-type | `Text → Amount`. Safest cohort. |
| `commercial_invoice_line_extended_amount` | type_incoherence | 0 | fix-type | Same. |
| `commercial_invoice_line_tax_amount` | type_incoherence | 0 | fix-type | Same. |
| `commercial_invoice_line_unit_price_amount` | type_incoherence | 0 | fix-type | Same. |
| `credit_transfer_payment_amount` | type_incoherence | 0 | fix-type | Same. |
| `debit_transfer_hdr_debit_transfer_amount` | type_incoherence | 0 | fix-type | Same. |
| `debit_transfer_payment_amount` | type_incoherence | 0 | fix-type | Same. |
| `invoice_ledger_entry_hdr_tax_amount` | type_incoherence | 0 | fix-type | Same. |
| `invoice_ledger_entry_hdr_total_invoice_amount` | type_incoherence | 0 | fix-type | Same. |
| `iso20022_camt_xchg_rate` | type_incoherence | 0 | fix-type | `representation_term: Text → Rate` (not Amount; it's an FX rate). Note divergence from the other 18. |
| `payment_status_payment_payment_status_amount` | type_incoherence | 0 | fix-type | `Text → Amount`. |
| `warranty_claim_hdr_parts_cost_amount` | type_incoherence | 0 | fix-type | Same. |
| `warranty_claim_hdr_service_cost_amount` | type_incoherence | 0 | fix-type | Same. |
| `warranty_claim_line_repair_cost_amount` | type_incoherence | 0 | fix-type | Same. |
| `warranty_claim_line_unit_price_amount` | type_incoherence | 0 | fix-type | Same. |

**Disposition totals:** 1 operator-evidence-required + 9 fix-definition + 20 fix-type + 0 fix-definition-and-type + 0 demote.

## 8. Proposed execution cadence

1. **Plan + AI-panel design** (this artifact + AI panel section §11). Operator approves disposition table.
2. **Author the two narrow correction endpoints** (`correct-definition` + `correct-type`) in `bc-core`. Each endpoint: §12-pattern atomic update + paired `recertify_bf_catalog` ledger row + pre-write gate-pass check.
3. **Author the AI-panel review packet builder** (`bc-core/scripts/build-d408-correction-required-review-packet.mjs`) — read-only, generates per-row packet (§11 shape).
4. **AI panel pass** — packet to operator with AI recommendation per row; operator records verdict.
5. **Dry-run apply packet** — for each operator-approved row, generate the exact UPDATE + INSERT pair preview; show what the row will look like post-write. No DB write.
6. **Capped apply** — small batches (5–10 rows) via the correction endpoints; verify post-batch.
7. **Verification** per §9.
8. **Final state assertion:** after all 30 rows processed, `correction_required = 0`; net delta is up-to-30 rows moved to `certified_catalog` (minus any demoted, minus any held back as operator-evidence-required pending separate work).

## 9. Verification plan

For each correction batch:

- **State transition only via ledger.** A BF moves out of `correction_required` only after a `recertify_bf_catalog` ledger row is inserted with `gate_signals_json` showing all hard gates pass on the new row. No direct UPDATE of `catalog_state_code` allowed.
- **Atomic per row.** UPDATE BF + INSERT certification_record in one transaction (§12 pattern).
- **No `cc_field_mapping` changes.** This slice does not modify CC bindings (separate operator-evidence work for `credit_type_code`).
- **No `canonical_field` changes.** CF `data_type` is independently governed; if a BF type fix would diverge from a CF's stored type, the correction endpoint refuses.
- **No `metric_contract` changes.**
- **No tenant DB touches.** DATABASE_URL targets `bc_platform_dev` only.
- **Invariant preserved:** `remediate_bf_semantics` count stays at 1,392.
- **Post-batch state read:** `correction_required` count decreases by exactly N (N corrected this batch); `certified_catalog` increases by N; `recertify_bf_catalog` ledger rows increase by N.

## 10. Open operator decisions

These must be made before any code is authored beyond this plan.

1. **`credit_type_code` binding review (P0, 11 CC).** Confirm: should the 11 `cc__credit` CF mappings remain bound to `credit_type_code`, or should each CF re-bind to a more specific BF (e.g. `credit_facility_type_code`, `credit_decision_type_code` if they exist; otherwise new BFs must be admitted)? This is the largest individual risk in the cohort. Decision blocks the P0 disposition.
2. **`freight_invoice_hdr_net_volume_measure` / `price_list_line_type_code` CF binding review.** The bound CFs (`volume_of_duplicated_data`, `product_selling_price`) look semantically loose. Confirm bindings are intentional before fixing definitions.
3. **External-standard prose policy for the 7 IFRS/XBRL definition fixes.** Are operator-authored summaries acceptable (with `standard_ref` link), or must the definition text be verbatim from the standard? Choice affects definition correction endpoint payload requirements.
4. **`iso20022_camt_xchg_rate` `representation_term`.** Confirm `Rate` (not `Amount`) — it's a foreign-exchange rate per ISO 20022 `BaseOneRate`. Pre-flagged for divergence from the other 18 type-incoherence rows.
5. **Endpoint authorization scope.** Should `correct-definition` and `correct-type` require platform-admin role (same as `remediate-semantics`)? Assumed yes for parity, but confirm.
6. **AI panel provider choice.** Use existing bc-ai cf_classifier pattern (Gemini Maker + OpenAI Checker + Claude Moderator per TSK-8c3e7c), or simpler single-model advisory? Affects review packet builder shape.
7. **Apply cadence.** Capped batches of 5? 10? Or each row individually? Affects review-queue UI design (out of scope here but informs the AI panel iteration loop).

## 11. AI panel usage

The 30-row cohort should be reviewed through an AI-assisted packet before any correction apply. **The packet is advisory only.** No auto-certification. No DB writes from the AI step. No fabricated provenance.

### 11.1 Per-row packet shape

```json
{
  "field_id": "uuid",
  "name": "credit_type_code",
  "current": {
    "object_class": "credit",
    "property": "type_code",
    "representation_term": "Code",
    "data_type": "code",
    "definition": "type_code from OAGIS undefined",
    "definition_standard": "OAGIS",
    "semantic_family": null,
    "unit_type_code": null,
    "standard_ref": null
  },
  "gate_signals": {
    "g1": { "pass": false, "reasons": ["banned_template:oagis_undefined"] },
    "g3": { "pass": true, "reasons": [] },
    "catalog_state_reason_code": "broken_fallback_definition"
  },
  "downstream": {
    "cc_mapping_count": 11,
    "canonical_fields_affected": ["revolving_credit_limit", "credit_application_submission_date", "..."],
    "cc_names": ["cc__credit"],
    "alias_count": 1,
    "bo_required_or_bk": false,
    "sda_evidence": false
  },
  "evidence": {
    "oagis_field_path": "Credit/CreditTypeCode (lookup if present in bc-seed)",
    "external_standard_text": "<verbatim text from OAGIS if available>",
    "operator_notes": null
  },
  "proposed_corrections": [
    { "kind": "fix-definition", "new_definition": "<AI suggestion 1>", "rationale": "..." },
    { "kind": "fix-definition", "new_definition": "<AI suggestion 2>", "rationale": "..." },
    { "kind": "demote", "rationale": "11-CF spread suggests binding error; demote and rebind CFs" }
  ],
  "ai_recommendation": {
    "preferred_kind": "operator-evidence-required",
    "confidence": "medium",
    "reasoning": "11 distinct CFs in cc__credit cannot all be backed by a single type_code BF; recommend binding review before definition fix"
  },
  "operator_verdict": {
    "decided_by": null,
    "decided_at": null,
    "approved_kind": null,
    "approved_payload": null,
    "rationale": null
  }
}
```

### 11.2 Constraints

- **No auto-certification.** AI cannot write to `certification_record`. Only the governed endpoint can, and only after operator approval.
- **No DB writes from the packet builder.** The builder is read-only; it generates the packet file and exits.
- **No fabricated provenance.** If the OAGIS / IFRS / XBRL source for an evidence field cannot be located, the packet records `evidence.external_standard_text: null` — never inferred text.
- **Operator must approve each row.** Every `operator_verdict.approved_kind` is set by a human action (UI button, CLI confirmation, signed JSON). The correction endpoint refuses if the verdict is absent or unsigned.
- **Final correction must be ledgered via the governed endpoint.** No backdoor SQL. The endpoint computes `gate_signals_json` post-update and refuses to insert the ledger row if any hard gate still fails — guaranteeing a correction never moves a still-broken row to `certified_catalog`.

### 11.3 Next artifact

`bc-core/scripts/build-d408-correction-required-review-packet.mjs` — read-only Node script that:

- Queries the 30 `correction_required` rows.
- For each, joins `cc_field_mapping` to enumerate affected CFs + CCs.
- Looks up OAGIS / IFRS / XBRL source text via existing `bc-seed` collections where the row carries a `definition_standard`.
- Calls the chosen AI provider per §10.6 with a per-row prompt that asks for definition or type corrections (never both at once unless the operator opts in).
- Writes one JSONL packet per row to `bc-core/scripts/audit-output/d408-correction-required-review-<ts>.jsonl`.
- **Does not write to the DB.**
- Defer authoring to a separate session after this plan + the §10 operator decisions are approved.

## 11a. Operator decision addendum (locked 2026-05-17)

The seven blocking decisions in §10 are resolved here. Evidence is grounded in two read-only queries run against dev this session (no DB writes).

### 11a.1 `credit_type_code` binding — DISPOSITION: REMOVE THE 11 MAPPINGS

**Evidence (11 rows, all on `cc__credit`, all rule `assert_equal`):**

| `cf_name` | `cf_data_type` | mc_bindings |
|---|---|---:|
| `automated_credit_decisions_count` | number | 6 |
| `available_credit_lines` | number | 6 |
| `credit_application_submission_date` | date | 6 |
| `credit_approval_completion_date` | date | 6 |
| `customer_credit_risk_rating` | number | 6 |
| `drawn_credit_facility_amount` | number | 6 |
| `revolving_credit_drawn` | number | 6 |
| `revolving_credit_limit` | number | 6 |
| `total_credit_decisions_count` | number | 6 |
| `total_credit_deployed` | number | 6 |
| `total_credit_facility_limit` | number | 6 |

**`credit_type_code` BF is `data_type='code'` (categorical).** Every one of the 11 CFs is `data_type='number'` or `'date'`. The `assert_equal` rule cannot meaningfully assert a categorical code equal to a numeric measurement or a date — these mappings are structurally broken regardless of `credit_type_code`'s definition quality. They were almost certainly placeholder picks during `cc__credit` authoring when no better BF was available.

**Decision: option (b) — remove all 11 cc_field_mapping rows that bind `credit_type_code`.**

- These removals are CF-side cleanup, not BF correction.
- After removal, `credit_type_code` becomes un-CC-mapped. Its `catalog_state_code` stays `correction_required` (still G1 fail on the templated definition).
- Then **option (a)** applies to `credit_type_code` itself: fix the definition from OAGIS field-level prose (the OAGIS `Credit/CreditTypeCode` BIE) via the new `correct-definition` endpoint, then `recertify_bf_catalog` → `certified_catalog`. The BF is semantically valid; only the mappings were wrong.
- Each of the 11 un-bound CFs must be triaged separately: re-bind to a more specific BF (`credit_facility_type_code`, `credit_decision_type_code`, etc. if they exist or get admitted), OR convert to a `compute` mapping, OR leave un-bound until a proper BF is admitted. **This triage is out of scope for the 30-row cohort and is tracked as a follow-up.**

**Ledger:** mapping removal is itself a governed write and needs a small DBCP (data-only, no DDL). Filed as **DBCP-1q-C** in the implementation order below.

**Blast radius note:** each removed mapping invalidates the cc__credit CC for 6 metric bindings (66 MC references total). MC evaluations against `cc__credit` will degrade or fail for the affected CFs until they are re-bound. **Operator must accept this degradation window** as a precondition to the removal. The alternative (leave broken mappings in place) means `cc__credit` continues to produce incoherent evaluations against a code-vs-number assert_equal — strictly worse.

### 11a.2 P1 definition correction policy — LOCKED

For the 7 `definition_too_short` rows (5 IFRS + 2 XBRL/US-GAAP):

- Definitions must trace to an authoritative external standard source: **IFRS Foundation taxonomies**, **FASB ASC / XBRL US-GAAP Financial Reporting Taxonomy**, or **SEC EDGAR taxonomy** entries. No other sources permitted for these 7.
- **AI may draft** a candidate definition from those sources but must include the source URL / standard reference and **may not paraphrase to the point of altering meaning**.
- **Operator must approve verbatim** before the `correct-definition` endpoint accepts it.
- If the standard offers verbatim prose, prefer it; if the standard offers only a label + element id, the operator-authored definition must cite the element id and use the standard's reporting context.
- `standard_ref` on the BF must be populated alongside the definition fix (use the existing §12 `remediate-semantics` endpoint to add the `standard_ref` in a separate atomic call, OR extend `correct-definition` to optionally accept a `standard_ref` payload — decision deferred to endpoint authoring).
- **No invented definitions, no offline-only prose, no paraphrase that drops a clause from the standard.**

### 11a.3 P2 type correction policy — LOCKED, ZERO CF CONFLICTS

Read-only check across the 4 CC-mapped P2 rows (`asset_net_book_value_amount`, `asset_cost_amount`, `asset_accumulated_depreciation_amount`, `asset_salvage_value_amount`) confirmed:

- All 55 bound CFs have `cf_data_type='number'`.
- All 4 BFs already carry `data_type='number'`.
- **Zero data_type conflicts.** The proposed fix is `representation_term: 'Text' → 'Amount'` only; `data_type` is untouched.

The remaining 15 P2 rows have zero CC mappings, so the pre-write CC impact check is trivially clean.

**Mechanical mapping locked:**

| Cohort | `representation_term` after fix | `data_type` after fix |
|---|---|---|
| 18 `*_amount` BFs | `Amount` | `number` (unchanged) |
| 1 `iso20022_camt_xchg_rate` | `Rate` (per ISO 20022 `BaseOneRate`) | `number` (unchanged) |

`iso20022_camt_xchg_rate → Rate` confirmed; it is a foreign-exchange rate per ISO 20022 `camt.053.001.12 XchgRate`.

`correct-type` endpoint still performs the pre-write CC impact check on every call; the result is "no conflict" for all 19 today, but the check is required as defence-in-depth.

### 11a.4 Endpoint strategy — LOCKED

Two narrow endpoints, both mirroring §12 `remediate-semantics`:

1. **`POST /api/business-fields/:id/correct-definition`**
   - Mutates `definition` (and optionally `standard_ref` if the operator's source requires it).
   - Pre-write G1 dry-evaluation: rejects if the proposed definition still fails G1 (banned templates, datatype boilerplate, restatement, length).
   - Refuses if `catalog_state_code` ≠ `correction_required` (this endpoint is for correction, not for new authoring).
   - On success: atomic UPDATE + INSERT `certification_record` (`action_code='recertify_bf_catalog'`, `gate_results_json` snapshot including all G1–G5 verdicts on the new row) + UPDATE `catalog_state_code='certified_catalog'` + `catalog_state_reason_code='manual_correction_applied'` (new reason code value; needs addition to CHECK enum — see §11a.6).

2. **`POST /api/business-fields/:id/correct-type`**
   - Mutates `representation_term` and/or `data_type`.
   - Pre-write G3 dry-evaluation: rejects if the proposed pair is still incoherent.
   - **Pre-write CC impact check:** queries `cc_field_mapping JOIN canonical_field` for any bound CF whose `data_type` differs from the proposed BF `data_type`. If any conflict, refuses with `409 cc_field_data_type_conflict` and a structured payload listing the conflicting CFs.
   - Refuses if `catalog_state_code` ≠ `correction_required`.
   - On success: same atomic UPDATE + INSERT pattern as `correct-definition`.

Both endpoints require **platform-admin role** (parity with §12 `remediate-semantics`).

### 11a.5 AI panel role — LOCKED

- **Advisory only.** AI never writes to the DB. AI never calls the correction endpoints. AI never sets `operator_verdict`.
- AI may **propose** definition text (with cited source) and type pairs.
- Operator approves each row individually. Approval is recorded in the packet's `operator_verdict` block AND is the input that the correction endpoint operator (the human invoking the endpoint) uses to author the request body.
- The correction endpoint itself does **not** read the AI packet. It accepts a request body authored by a human (or by an operator script using human-approved verdicts). This keeps the AI step strictly advisory; the endpoint cannot be tricked into accepting an AI-suggested value that the operator did not approve.
- AI provider choice: use the existing `bc-ai` `cf_classifier` pattern (Gemini Maker + OpenAI Checker + Claude Moderator per `TSK-8c3e7c`) for definition drafts. For type fixes the proposal is mechanical (no AI needed); the packet still includes a one-line AI sanity check ("does Text/number → Amount/number still describe this field?") but the bar to approve is "yes / unsure".

### 11a.6 Implementation order (post-decisions)

1. **Author DBCP-1q-C** — small data-only DBCP that DELETEs the 11 `credit_type_code → cc__credit` mappings and emits 11 `certification_record` rows with a new action code `unmap_cc_field_mapping` (or reuse `supersede` against the cc_field_mapping primitive type if the existing enum supports it — to be confirmed during DBCP authoring). Operator-approved mapping list per §11a.1.
2. **Apply DBCP-1q-C** in dev with read-only verification: cc__credit MC bindings now reference CFs with no BF backing — flag this clearly so the operator triages the orphaned CFs in a follow-up.
3. **Author `correct-definition` + `correct-type` endpoints** per §11a.4. Single bc-core commit with both, mirroring §12 pattern, with unit tests covering the gate-pass refusal + CC-conflict refusal paths.
4. **Add `catalog_state_reason_code='manual_correction_applied'`** to the CHECK enum if the operator wants to distinguish post-correction certified rows from grandfathered/standard certified rows. This is a tiny additive DBCP; or alternatively reuse `legacy_hard_pass_grandfathered` semantics — **operator decision needed at endpoint-authoring time, not now.**
5. **Author `bc-core/scripts/build-d408-correction-required-review-packet.mjs`** (read-only) per §11.3.
6. **Run packet builder; operator AI panel pass** for the 7 definition fixes. Type fixes can skip the AI step (mechanical).
7. **Capped apply via the correction endpoints**, batches of 5. Verify per §9.
8. **Final assertion:** `correction_required = 0` after all 30 are processed (1 P0 may stay until DBCP-1q-C lands; 19 P2 + 7 P1 + 3 remaining P0 = 29 should clear; the 11 cc__credit CFs become a separate orphan-CF triage task).

### 11a.7 Endpoint implementation is now UNBLOCKED

All blocking decisions in §10 are resolved. The remaining open items (CHECK enum addition for `manual_correction_applied`, AI panel provider's exact prompt shape) are endpoint-authoring details, not blockers.

The single hard dependency is **DBCP-1q-C must be authored and applied before `credit_type_code` itself can be corrected**, because credit_type_code's CC mappings should be removed before its definition is fixed (don't strengthen a row whose downstream bindings are about to be removed).

## 11b. Post-endpoint probe decision — Path A / Path C sub-cohort split (locked 2026-05-17)

After the correction endpoints landed (`bc-core@9243984`) and the AI-panel verdicts produced 19 APPROVE rows (`bc-core@d1638b3`), a sequential capped apply was attempted (`bc-core@8ff2a9f`). It halted on the first row.

### 11b.1 What the probe showed

- **Halted 19-row apply (`bc-core@8ff2a9f`).** Row 1 `asset_net_book_value_amount` with body `{ representationTerm: 'Amount', dataType: 'number' }` returned **HTTP 422** — *"projected SDA gates still fail: G4, G5, G6. Amend the input and re-run."* No rows mutated. Invariants identical to baseline pre/post.
- **Single-row iso probe (`bc-core@a82a63b`).** `iso20022_camt_xchg_rate` (the only cohort row carrying any `definition_standard`, value `ISO_20022`) was retried in isolation with body `{ representationTerm: 'Rate', dataType: 'number' }`. Endpoint refused with **HTTP 422** — *"projected SDA gates still fail: G1, G4, G5, G6, G7."* Even partial uplift is insufficient; stricter projection also re-fails G1 on the existing 57-char definition.
- **Cohort-wide blocking confirmed.** None of the 19 type-incoherence rows can be re-admitted via `correct-type` without prior SDA uplift (`definition_standard` + `standard_ref` + `semantic_family` + `unit_type_code` + SDA evidence) AND a definition that passes G1 under the stricter projection.

### 11b.2 Why full G1–G8 projection is retained (Path B rejected)

The operator's decision is explicit: **`correct-type` and `correct-definition` continue to project the full SDA G1–G8 on the post-edit row before re-admission.** Narrowing the projection to only the corrected axis (Path B in the halted-apply report) was considered and **rejected**. Rationale, restated:

- D408 admission discipline says the certified_catalog axis is the *post-edit row is fully admissible* invariant — not *the operator changed one column*. A row that re-enters `certified_catalog` must satisfy every hard gate as if it were being admitted for the first time. Otherwise `certified_catalog` becomes a weighted bucket, and downstream consumers (CC bindings, MC evaluations, future authoring surfaces) cannot trust the state code.
- Narrowing the projection would convert `correct-*` into a compensation surface (Repair-location F per CLAUDE.md Foundation Gate) hiding upstream-trust gaps. The fix must live at the source of the gap (Repair-locations A/B/C — provenance, semantic family, unit type, SDA evidence), not at the admission boundary.
- The §12 `remediate-semantics` pattern already enforces full projection; symmetric enforcement on `correct-*` is the only consistent posture.

The endpoints stay as-is. No code change. No gate weakening.

### 11b.3 Sub-cohort decision table

The 30 `correction_required` rows split as follows after the probe. (The 11 NEEDS_EVIDENCE definition rows from §11a are unchanged — listed here for completeness only.)

| Sub-cohort | Rows | CC blast radius | Chosen path | Rationale |
|---|---:|---:|---|---|
| **A1.** `asset_*_amount` (`net_book_value`, `cost`, `accumulated_depreciation`, `salvage_value`) | 4 | 55 CFs | **Path A — uplift then correct-type.** Do not demote. | High CC blast radius (39 + 10 + 5 + 1 = 55 CFs reading a `Text`-typed BF today). Demotion would orphan all 55 mappings and force re-binding work later. Authoritative US-GAAP fixed-asset terminology exists and is well-known; sourcing standard_ref per row is tractable. |
| **A2.** `iso20022_camt_xchg_rate` | 1 | 0 | **Path A — hold (conditional).** Apply only if authoritative ISO 20022 `camt.053 XchgRate` definition + standard_ref can be sourced. Otherwise **remain `correction_required` in evidence-needed hold.** Do not force correction. | No CC blast radius today; no urgency. Source citation must be verbatim ISO 20022 message-catalogue entry. If sourcing stalls, the row stays where it is — `correction_required` is a terminal-until-evidence state, not a degradation. |
| **C1.** No-CC type-incoherence rows (commercial_invoice_line_×4, debit_transfer_×2, credit_transfer_×1, warranty_claim_×4, invoice_ledger_entry_hdr_×2, payment_status_payment_payment_status_amount) | 14 | 0 | **Path C — `demote_bf_catalog`.** Unless operator later supplies evidence/need, they will be demoted. | Zero CC mappings — nothing in the platform currently depends on them. Re-admitting them would require sourcing standard_ref per row across 4 different OAGIS/ISO 20022 contexts for BFs that no consumer references. Demotion is cheaper, reversible (demoted_catalog → re-admit via re-authoring if a future need emerges), and honest about the actual coverage requirement. |
| (Reference only — unchanged) NEEDS_EVIDENCE definition rows | 11 | 14 CF refs | Already on the §11a.2 evidence track. | Out of scope for this addendum. |

Cohort accounting after this addendum (no DB change yet):

- **Path A targets:** 4 (A1) + up to 1 (A2 conditional) = up to 5 rows that may move `correction_required` → `certified_catalog`.
- **Path C targets:** 14 rows that will move `correction_required` → `demoted_catalog`.
- **Hold:** 1 row (A2) that may remain `correction_required` indefinitely until ISO evidence is sourced.
- **Untouched by this addendum:** 11 NEEDS_EVIDENCE definition rows.

Final-state expectation if all paths execute cleanly: `correction_required` 30 → 11 (or 12 if iso row holds), `certified_catalog` 1,651 → 1,655 (+4) or 1,656 (+5), `demoted_catalog` 374 → 388.

### 11b.4 Implementation sequence

Strictly ordered. No step starts until the preceding step closes.

| # | Step | Authority surface | Output / artifact |
|---|---|---|---|
| **A** | Author uplift evidence packet for the 4 A1 asset rows. Per-row JSON: proposed `definition_standard`, `standard_ref`, `semantic_family`, `unit_type_code`, plus an SDA-evidence plan (which `business_field_alias`, `source_origin_ref`, or aligned `cc_field_mapping` will count as G6/G7 evidence) and a new G1-compliant `definition`. **Docs / read-only.** | `bc-core/scripts/audit-output/d408-asset-uplift-evidence-packet-<ts>.{md,jsonl}` |
| **B** | Operator sources US-GAAP / fixed-asset standard prose and citations per row. Operator approves each row's packet entry. **Operator work, off-platform sourcing.** | Approved packet rows; citations recorded. |
| **C** | Apply remediate-semantics uplift for approved A1 rows via `POST /api/business-fields/:id/remediate-semantics` (DEC-a49413 §12). Capped batch (≤5). Pre/post invariant check; halt on first refusal. | Audit JSONL of remediate-semantics calls; `remediate_bf_semantics` ledger count +N. |
| **D** | Re-run `correct-type` for the same A1 rows with the previously-approved bodies. Capped batch (≤5). Halt on first refusal. | Audit JSONL of correct-type apply; `recertify_bf_catalog` ledger count +N; `correction_required` -N; `certified_catalog` +N. |
| **E** | Author a small data-only DBCP / governed script for demoting the 14 C1 no-CC rows via the existing `demote_bf_catalog` ledger action. Operator-approved list. **Forward-only governed write**, mirroring DBCP-1q-B; no DDL. | DBCP-1q-D plan + reverse + script + audit JSONL. |
| **F** | Keep the iso row (A2) in evidence-needed hold until ISO 20022 message-catalogue prose + standard_ref are sourced. No action this slice. | No artifact; status quo. |

Each step ends in a fresh checkpoint and (where applicable) a commit. None of the steps may be reordered to bypass the §12-then-correct-type sequencing on A1 rows.

### 11b.5 Tracking task

- **`TSK-eae922` — D408 type corrections require SDA uplift before recertify** is the **active tracking task** for steps A → F of this workflow. Status `planned/now`.
- `TSK-926c77` — D408 bc-ai correction panel endpoint — remains `planned/next`; primarily unblocks the 11 NEEDS_EVIDENCE definition cohort (separate track) by drafting citation-backed candidate prose. Not on the critical path for the §11b sub-cohort split.

### 11b.6 What this addendum does NOT change

- §1–§11a stand as written. Disposition tables in §7 and §11a are superseded for the 19 type-incoherence rows only — the dispositions there assumed `fix-type` alone was sufficient; §11b records that finding is wrong and replaces it.
- The 11 NEEDS_EVIDENCE definition rows remain on the §11a.2 evidence track. This addendum does not propose any new policy for them.
- `correct-definition` and `correct-type` endpoint signatures and gate-projection scope are unchanged.

## 12. Hard boundaries observed by this slice

- Docs only. No code. No DB writes. No SQL. No remediation calls. No metric promotion. No tenant DB. No service-code changes.
- SES-03f268 untouched (already closed in superseding session).
- Unrelated WIP preserved.

## 13. References

- ADR: [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md)
- DBCP design: [2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md](../../dbcp/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md)
- 1q-A verification plan: [2026-05-16-d408-dbcp-1q-a-verification-plan.md](../../dbcp/onboarding/2026-05-16-d408-dbcp-1q-a-verification-plan.md)
- 1q-B verification plan: [2026-05-16-d408-dbcp-1q-b-verification-plan.md](../../dbcp/onboarding/2026-05-16-d408-dbcp-1q-b-verification-plan.md)
- Data-side closeout: [2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md](../../closeouts/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md)
- Service-guard plan: [2026-05-16-d408-service-guards-plan-DEC-1ce490.md](2026-05-16-d408-service-guards-plan-DEC-1ce490.md)
- Service-guard closeout: [2026-05-16-d408-service-guard-closeout-DEC-1ce490.md](../../closeouts/onboarding/2026-05-16-d408-service-guard-closeout-DEC-1ce490.md)
- DEC-a49413 §12 `remediate-semantics` endpoint (DBCP-1p pattern referenced).
- Foundation invariants: `bc-docs-v3/docs/foundation/the-invariants.md`
