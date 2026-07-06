---
title: "D408 correction_required cleanup — closeout and D409 handoff"
date: 2026-05-17
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
plan: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md
design: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-admit-from-correction-required-design-DEC-1ce490.md
session: SES-c5af8c
task: TSK-eae922
type: closeout
status: closed
hands_off_to: D409 — BF-BO Catalog Expansion Factory
---

# D408 `correction_required` cleanup — closeout

Closes the D408 `correction_required` cleanup thread driven through `SES-c5af8c` and `TSK-eae922`. **No further writes from this thread.** The remaining 12 rows in `correction_required` hand off to D409.

## 1. Final D408 catalog admission state (verified `2026-05-17`)

| `certification_record.action_code` (BF-scoped) | count |
|---|---:|
| `remediate_bf_semantics` | 1,396 |
| `admit_bf_catalog` | 1,651 |
| `mark_bf_correction_required` | 30 |
| `demote_bf_catalog` | 388 |
| `recertify_bf_catalog` | 4 |
| `admit_bf_from_correction_required` | **0** |

| `business_field.catalog_state_code` | count |
|---|---:|
| `candidate_import` | 5,007 |
| `certified_catalog` | 1,655 |
| `correction_required` | 12 |
| `demoted_catalog` | 388 |
| `business_field` total | **7,062** |

| other primitives | count |
|---|---:|
| `canonical_field` | 3,097 |
| `metric_contract` | 780 |
| `cc_field_mapping` | 1,603 |

## 2. Cohort dispositions (per plan §11b)

### 2.1 A1 — `asset_*_amount` (4 rows) — **COMPLETED**

All 4 rows are now `certified_catalog` with `definition_standard='US_GAAP'`, `semantic_family='measure-currency'`, `unit_type_code='currency'`, cited `standard_ref`, `representation_term='Amount'`, `data_type='number'`. Each carries a paired `recertify_bf_catalog` ledger row (4 total).

| BF | retained CC mappings (post 1q-E) |
|---|---:|
| `asset_net_book_value_amount` | 5 (3 FIT + 1 REVIEW + 1 INSUFFICIENT_CONTEXT) |
| `asset_cost_amount` | 2 (2 FIT) |
| `asset_accumulated_depreciation_amount` | 2 (2 FIT) |
| `asset_salvage_value_amount` | 1 (1 FIT) |

### 2.2 DBCP-1q-E — 45 A1 MISMATCH `cc_field_mapping` rows — **APPLIED**

The deterministic A1 CF re-binding audit classifier flagged 45 of the original 55 A1 bindings as MISMATCH (unit-type contradictions and strong-mismatch name patterns on `cc__asset`). All 45 were removed via a single transaction; 10 FIT/REVIEW/INSUFFICIENT_CONTEXT bindings retained. Full-fidelity reverse SQL exists.

### 2.3 C1 — 14 no-CC type-incoherence rows (DBCP-1q-D) — **APPLIED**

`commercial_invoice_line_*` ×4, `debit_transfer_*` ×2, `credit_transfer_*` ×1, `warranty_claim_*` ×4, `invoice_ledger_entry_hdr_*` ×2, `payment_status_payment_payment_status_amount`. All 14 now `demoted_catalog` with `catalog_state_reason_code='type_incoherence_no_active_anchor'`. Reversible via paired re-admit ledger.

### 2.4 A2 — `iso20022_camt_xchg_rate` (1 row) — **HANDED OFF TO D409**

Authoritative ISO 20022 evidence sourced (`BaseOneRate` datatype + `CurrencyExchange` parent structure + `camt.053` schema path). DBCP-1q-G CHECK-enum extension applied. New `/admit-from-correction-required` endpoint designed, implemented, and unit-tested (20/20 pass). Single-row admit attempt halted at HTTP 422 with **G1 (`not_bo_scoped`) + G7** under the stricter projection — a pre-D408 authoring defect on the row itself:

```
name         = 'iso20022_camt_xchg_rate'
object_class = 'iso20022_bank_to_customer_statement_v12'   ← does not prefix name
property     = 'XchgRate'                                  ← not snake_case
```

Zero mutation. The row remains `correction_required`. This is a `name` / `object_class` realignment problem; no governed endpoint mutates either column. Handed to D409 modeling review (rename, reassign object_class, or admit a new short-named BO).

### 2.5 B1 — 11 NEEDS_EVIDENCE definition rows — **HANDED OFF TO D409**

The 7 IFRS / 2 XBRL US-GAAP / 1 OAGIS / 1 credit_type_code rows still require operator-sourced verbatim authoritative prose (per plan §11a.2). DBCP-1q-C removed all 11 credit_type_code CC mappings earlier in the session, so `credit_type_code` is bind-orphaned but still `correction_required`. Handed to D409 BF-BO Catalog Expansion Factory evidence workflow alongside the bc-ai panel endpoint design (`TSK-926c77`, still `planned/next`).

## 3. Remaining 12 `correction_required` rows

| sub-cohort | rows | handed to |
|---|---:|---|
| A2 — `iso20022_camt_xchg_rate` (G1 name/object_class defect) | 1 | D409 modeling review |
| B1 — IFRS / XBRL US-GAAP / OAGIS / credit_type_code | 11 | D409 evidence workflow + TSK-926c77 |
| **total** | **12** | (=`correction_required` count above) |

## 4. Net D408 delta over the session

| metric | session-start (DBCP-1q-A pre-apply) | session-end (this closeout) |
|---|---:|---:|
| `correction_required` | 30 | **12** |
| `certified_catalog` | 1,651 | **1,655** (+4 A1) |
| `demoted_catalog` | 374 | **388** (+14 C1) |
| `remediate_bf_semantics` ledger | 1,392 | **1,396** (+4 A1 Step C) |
| `recertify_bf_catalog` ledger | 0 | **4** (A1 Step D) |
| `cc_field_mapping` | 1,648 | **1,603** (−45 DBCP-1q-E) |
| `business_field` total | 7,062 | 7,062 |
| `canonical_field` | 3,097 | 3,097 |
| `metric_contract` | 780 | 780 |

**No tenant DB touched at any point. No metric promotion at any point. No metric_contract or canonical_field row mutated at any point.**

## 5. Artifacts and commits from this correction sequence

### 5.1 bc-core commits

| step | hash | summary |
|---|---|---|
| Plan §11a.1 / DBCP-1q-C — credit_type_code mapping removal applied | _earlier in session_ | 11 cc__credit mappings removed |
| Plan §11b sub-cohort C1 / DBCP-1q-D — author + apply demotion of 14 no-CC rows | _earlier in session_ + applied | 14 rows demoted, `type_incoherence_no_active_anchor` reason added |
| §11b A1 / Step B US-GAAP source review | `723c24d` | 4 rows APPROVE with verbatim XBRL US-GAAP element evidence |
| §11b A1 / Step C — `/remediate-semantics` apply for 4 asset rows | `1902d5d` | 4 HTTP 200 |
| §11b A1 / Step D probe — single-row `/correct-type` on salvage row | `c5cdb85` | HTTP 200, 9/9 gates pass |
| §11b A1 / Step D remaining — 3 asset rows | `b23122d` | 3 HTTP 200 |
| A1 CF re-binding audit packet (read-only) | `752d66b` | 55 bindings → 8 FIT / 1 REVIEW / 45 MISMATCH / 1 INSUFFICIENT_CONTEXT |
| DBCP-1q-E artifacts — 45 A1 MISMATCH mapping removal | `2c84aca` | target JSON + apply script + forward + reverse SQL |
| DBCP-1q-E applied | (next commit after `2c84aca`) | a1_bindings 55 → 10 |
| A2 evidence packet — iso row read-only | `cea5695` | ISO 20022 BaseOneRate + CurrencyExchange verbatim |
| A2 3-step uplift halted — §12 `status_code='certified'` precondition | `397d9b3` | exposed state-machine gap; zero mutation |
| DBCP-1q-G SQL pair — additive CHECK enum | `ef63fa5` | adds `admit_bf_from_correction_required` action_code |
| `/admit-from-correction-required` endpoint implementation | `ec681c7` | DTO + service + repo tx + controller + 20 unit tests pass |
| A2 endpoint apply halted — G1/G7 name/object_class defect | `9d374f5` | exposed pre-D408 BF authoring defect; zero mutation |
| **This closeout** | _this commit_ | docs only |

### 5.2 bc-docs-v3 commits

| artifact | hash |
|---|---|
| §11b sub-cohort split lock (Path A / Path C decision) | `2d8a544` |
| DBCP-1q-D verification plan | `d09251c` |
| DBCP-1q-E verification plan | `599d84f` |
| Admit-from-correction-required endpoint design | `2c457a8` |
| DBCP-1q-G verification plan | `91f3f9f` |
| **This closeout** | _this commit_ |

### 5.3 DevHub tasks

| UID | title | status |
|---|---|---|
| `TSK-eae922` | D408 type corrections require SDA uplift before recertify | active — to be closed alongside this closeout |
| `TSK-926c77` | D408 bc-ai correction panel endpoint | `planned/next` — hand off to D409 |

## 6. Honest residuals

These were quantified during the session but **not actioned**, per the closeout posture:

1. **A1 orphan CFs (≈45 from DBCP-1q-E removal).** Now unbound from any A1 BF on `cc__asset`. Same pattern as the post-1q-C credit_type_code orphan-CF triage. Handed to D409 CF rebinding workflow.
2. **3 P&L depreciation flow CFs** (`annual_depreciation_expense`, `depreciation_expense`, `total_depreciation_expense_for_period`) — flagged in Step B as balance-vs-flow split candidates; need a separate `asset_depreciation_expense_amount` BF if re-binding is desired. Handed to D409.
3. **1 INSUFFICIENT_CONTEXT row** (`total_asset_value` — empty CF `description_text`) flagged in the A1 audit packet; needs CF description enrichment before re-classification. Handed to D409 CF-governance workflow.
4. **1 REVIEW row** (`change_in_value_of_underlying_asset`) — operator semantic-fit decision still pending. Handed to D409.
5. **iso row name / object_class defect** (§2.4) — needs a governed rename or BO reassignment endpoint, or a deliberate demote. Handed to D409.
6. **B1 11 NEEDS_EVIDENCE rows** — operator-sourced authoritative IFRS / XBRL US-GAAP / OAGIS prose required; `TSK-926c77` bc-ai panel endpoint can accelerate. Handed to D409.

None of these residuals is a defect of the D408 catalog admission machinery; they are downstream operator-workflow + new-governance-surface items appropriately scoped to D409.

## 7. Confirmation — no further writes from this thread

This closeout commits **markdown only**.

- No `business_field` mutation.
- No `certification_record` insert.
- No `canonical_field` mutation.
- No `cc_field_mapping` mutation.
- No `metric_contract` mutation.
- No tenant DB touched.
- No endpoint invocation.

Counts immediately after this closeout commit are identical to §1.

## 8. Hand-off to D409 — BF-BO Catalog Expansion Factory

D408 was a cleanup decision for the 30-row `correction_required` cohort produced by DBCP-1q-A backfill. The 12 remaining rows + the residuals in §6 hand off to D409 — the BF-BO Catalog Expansion Factory workstream. D409 owns:

- BF rename / object_class reassignment governance (resolves §2.4).
- BF-BO creation governance for short-named BOs (resolves §2.4 via a different path).
- CF re-binding triage workflow (resolves §6.1, §6.2, §6.4).
- CF `description_text` enrichment workflow (resolves §6.3).
- Evidence sourcing workflow for IFRS / XBRL US-GAAP / OAGIS / ISO 20022 prose, including the `TSK-926c77` bc-ai panel endpoint (resolves §2.5 / §6.6).

The endpoints + DBCP patterns built in this session are the substrate D409 inherits:

| substrate | available to D409 |
|---|---|
| `POST /api/business-fields/:id/remediate-semantics` (DEC-a49413 §12) | uplift legacy-certified BFs |
| `POST /api/business-fields/:id/correct-definition` (DEC-1ce490) | one-axis def fix on correction_required rows |
| `POST /api/business-fields/:id/correct-type` (DEC-1ce490) | one-axis type fix on correction_required rows |
| `POST /api/business-fields/:id/admit-from-correction-required` (DEC-1ce490 / DBCP-1q-G) | atomic admit of (draft, correction_required) rows |
| DBCP-1q-D / DBCP-1q-E patterns | governed cc_field_mapping removal + governed BF demotion |
| `bf-correction.helper.ts` | pure G1 + G3 validators reusable in new endpoints |
| `evaluateCertificationGates` projection | full SDA G1-G8 evaluator usable from any new admission boundary |

D409 should not need to weaken any of these to do its work.

## 9. Session close

This work-record is the final D408 closeout. `SES-c5af8c` and `TSK-eae922` close after this commit + checkpoint. `TSK-926c77` (bc-ai panel) carries forward to D409.

## 10. References

- Plan: `bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md`
- §11b sub-cohort decision: `bc-docs-v3@2d8a544`
- A1 audit packet: `bc-core@752d66b`
- A1 Step C / D commits: `bc-core@1902d5d`, `c5cdb85`, `b23122d`
- DBCP-1q-E artifacts: `bc-core@2c84aca`; verification plan: `bc-docs-v3@599d84f`
- A2 evidence packet: `bc-core@cea5695`
- A2 halted apply (§12 gap): `bc-core@397d9b3`
- Admit-from-correction-required design: `bc-docs-v3@2c457a8`
- DBCP-1q-G SQL pair: `bc-core@ef63fa5`; verification plan: `bc-docs-v3@91f3f9f`
- Admit endpoint implementation: `bc-core@ec681c7`
- A2 endpoint apply halt: `bc-core@9d374f5`
- Foundation invariants: `bc-docs-v3/docs/foundation/the-invariants.md`
- ADR: `bc-docs-v3/docs/adrs/ADR-1ce490.md`
