---
title: "D409 Pilot 1 closeout — cc__credit orphan CF factory run"
date: 2026-05-17
authority: DEC-b8ec00 (D409 — BF-BO Catalog Expansion Factory)
adr: bc-docs-v3/docs/adrs/ADR-b8ec00.md
sop: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md
scaffold: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-agent-prompt-scaffold.md
modeling_policy: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-credit-facility-modeling-policy.md
predecessor: DEC-1ce490 (D408)
sessions:
  - SES-abd596 (Pilot 1 packet)
  - SES-9346a2 (Pilot 1A deep dive)
  - SES-1c3ba4 (Pilot 1B batch triage)
  - SES-a51816 (modeling policy)
  - SES-d18a36 (admission+rebind packet)
  - SES-8aa8ac (gap report — candidate_import edge)
  - SES-2be973 (admit-from-candidate-import design)
  - SES-710595 (DBCP-1q-I + endpoint + apply driver + smoke batch)
  - SES-2609cd (rebind attempt — field_selection gap)
  - SES-603c6d (field-selection endpoint + final apply)
  - SES-c53953 (this closeout)
type: closeout
status: closed
hands_off_to: D409 cc__credit evidence batch (6 NEEDS_EVIDENCE + 1 HOLD), then D409 asset residuals (A1 / depreciation flow / ISO 20022)
---

# D409 Pilot 1 — cc__credit closeout

Closes Pilot 1 of the D409 BF-BO Catalog Expansion Factory. **No further apply from this thread.** The 7 remaining cc__credit rows are evidence/definition work and hand off to a sibling task.

---

## 1. Executive summary

D409 Pilot 1 proved the factory end-to-end on the cc__credit admission queue:

- **Started** with 11 orphaned `cc__credit` canonical fields (CFs) left behind when DBCP-1q-C removed the bad `credit_type_code` mappings during D408's catalog cleanup.
- **Resulted** in 2 new certified-catalog business fields (BFs), 4 governed `cc_field_mapping` rows binding the orphan CFs to those BFs (with the revolving specialisation carried as `filter_json`, not as a renamed BF), and 7 rows intentionally left unresolved as evidence/definition work for a separate session.
- **Built** the four reusable governance primitives the next admission queues will reuse with no further design ceremony: a candidate_import admission endpoint, a narrow CC field_selection extension endpoint, a generic D409 apply driver, and the D409 modeling-policy pattern.

The pilot also validated the D409 SOP discipline at every gate: agents recommended, governed endpoints (and one approved schema-only DBCP) mutated, halt-on-first-failure caught two real governance gaps before any DB write went out, and no shortcut bypassed the modeling policy or the DB Change Protocol.

---

## 2. Starting state

### 2.1 The 11 orphan CFs (Pilot 1 packet, bc-core@49eec7c)

| # | CF | data_type / unit | lane |
|---:|---|---|---|
| 1 | `automated_credit_decisions_count` | number / count | count |
| 2 | `available_credit_lines` | number / currency | count (name/unit conflict) |
| 3 | `credit_application_submission_date` | date / days | date |
| 4 | `credit_approval_completion_date` | date / days | date |
| 5 | `customer_credit_risk_rating` | number / score | risk (empty definition → HOLD) |
| 6 | `drawn_credit_facility_amount` | number / currency | facility amount |
| 7 | `revolving_credit_drawn` | number / currency | facility amount |
| 8 | `revolving_credit_limit` | number / currency | facility amount |
| 9 | `total_credit_decisions_count` | number / count | count |
| 10 | `total_credit_deployed` | number / currency | facility amount (bank perspective) |
| 11 | `total_credit_facility_limit` | number / currency | facility amount |

### 2.2 Origin

D408 cleanup (DEC-1ce490, SES-c5af8c) included DBCP-1q-C, which removed 11 `cc_field_mapping` rows that pointed the above CFs at the `credit_type_code` BF. The mappings were semantically wrong: a type-code BF cannot anchor amount/count/date/rating CFs. Removing the mappings left the CFs orphan inside `cc__credit` (zero `cc_field_mapping` rows for each), pending a defensible re-bind under the D409 factory.

### 2.3 Why direct rebind was blocked at pilot start

- No suitable certified-catalog BF existed for "credit facility maximum borrowing capacity" or "credit facility amount outstanding" (verified by broader scan in Pilot 1A).
- The remaining lanes (dates, counts, risk rating, bank-perspective amount) lacked the standards-tier evidence the SOP requires for `ADMIT_READY`.
- A new BF could not be created and bound through one governed call: the candidate_import → certified_catalog edge was not governed, and CC `field_selection` would refuse a non-listed BF even after admission.

Both gaps were discovered, named, and closed during the pilot.

---

## 3. Factory stages

The pilot took 11 operator sessions, sequenced per SOP §3 (one-then-many discipline). Each stage produced verifiable artifacts.

| # | Stage | Session | Commit / artifact |
|---:|---|---|---|
| 1 | Pilot 1 packet — broad triage (11 CFs) | SES-abd596 | bc-core@49eec7c |
| 2 | Pilot 1A — single-CF deep dive (`revolving_credit_limit`) | SES-9346a2 | bc-core@4a446a9 |
| 3 | Pilot 1B — batch triage (remaining 10) | SES-1c3ba4 | bc-core@76dda90 |
| 4 | Credit-facility modeling policy v0.1 | SES-a51816 | bc-docs-v3@400e1d1 |
| 5 | Admission + rebind packet | SES-d18a36 | bc-core@b628d9c |
| 6 | Gap report — candidate_import → certified_catalog edge missing | SES-8aa8ac | bc-core@15000ef |
| 7 | `/admit-from-candidate-import` endpoint design v0.1 | SES-2be973 | bc-docs-v3@06aa817 |
| 8a | DBCP-1q-I — `admit_bf_from_candidate_import` action_code | SES-710595 | bc-core@723baa1 |
| 8b | Endpoint implementation + 22/22 unit tests | SES-710595 | bc-core@cc8b2d9 |
| 8c | Generic apply driver + 2-BF smoke batch | SES-710595 | bc-core@531306a |
| 9 | Rebind attempt — second gap (CC field_selection) | SES-2609cd | bc-core@3275693 |
| 10a | `/onboarding/cc/:contractId/field-selection` endpoint + 15/15 tests | SES-603c6d | bc-core@33d4394 |
| 10b | Final apply — field_selection extended + 4 mappings | SES-603c6d | bc-core@0830c68 |
| 11 | This closeout | SES-c53953 | bc-docs-v3 (this file) |

The eight code/DB-write commits each preserved D408 invariants at the touched boundaries; the gap reports each halted before any DB write and named the missing edge precisely.

---

## 4. Final resolved rows

Four `cc_field_mapping` rows were inserted by Pilot 1, all via the governed `addMappings` endpoint, all with `resolution_rule_code='sum'`. Filter_json carries `facility_type=revolving` on the two revolving CFs per the modeling policy.

| CF | Target BF | rule | `filter_json` |
|---|---|---|---|
| `drawn_credit_facility_amount` | `credit_facility_amount_outstanding` | `sum` | `NULL` (aggregate) |
| `revolving_credit_drawn` | `credit_facility_amount_outstanding` | `sum` | `{"facility_type":"revolving"}` |
| `total_credit_facility_limit` | `credit_facility_maximum_borrowing_capacity` | `sum` | `NULL` (aggregate) |
| `revolving_credit_limit` | `credit_facility_maximum_borrowing_capacity` | `sum` | `{"facility_type":"revolving"}` |

Per-row shape verified by DB read-back at apply time and again at this closeout (read-only).

---

## 5. New BFs admitted

Two generic BFs admitted via `POST /api/business-fields/:id/admit-from-candidate-import` with `action_code='admit_bf_from_candidate_import'`. Both certified with full SDA evidence (semantic_family / unit_type_code / definition_standard / standard_ref / representation_term / data_type).

| BF | object_class / property | data_type / unit / representation_term | definition_standard | standard_ref | Notes |
|---|---|---|---|---|---|
| `credit_facility_amount_outstanding` | `credit_facility` / `amount_outstanding` | `number` / `currency` / `Amount` | `US_GAAP` | `us-gaap:LineOfCreditFacilityAmountOutstanding (ASC 470-10-50)` | Generic; revolving specialisation lives on cc_field_mapping.filter_json |
| `credit_facility_maximum_borrowing_capacity` | `credit_facility` / `maximum_borrowing_capacity` | `number` / `currency` / `Amount` | `US_GAAP` | `us-gaap:LineOfCreditFacilityMaximumBorrowingCapacity (ASC 470-10-50)` | Generic; revolving specialisation lives on cc_field_mapping.filter_json |

`semantic_family = 'measure-currency'` on both. Both rows carry `gate_signals_json` recording the SDA G1-G8 verdict at admit time. The admission-rule version recorded on each row is `v1`.

The XBRL axis `us-gaap:LineOfCreditFacilityAxis` with member `us-gaap:RevolvingCreditFacilityMember` is referenced in the modeling policy and on the two revolving cc_field_mapping rows via `filter_json`. The modeling policy explicitly chose to mirror the XBRL design: one element per concept, "revolving" as a dimension at the fact level, not a renamed element.

---

## 6. Remaining unresolved cc__credit rows (7)

Pilot 1 deliberately did **not** force resolution of the rows below. They are evidence or definition work — orthogonal to the modeling-policy lane that was resolved here.

### 6.1 NEEDS_EVIDENCE (6)

| CF | Why unresolved |
|---|---|
| `credit_application_submission_date` | Transactional credit-application timestamp; US-GAAP XBRL is a reporting taxonomy and does not cover this concept. OAGIS may carry a credit-application BOD with a submission datetime element, but a specific authoritative citation has not been operator-sourced. |
| `credit_approval_completion_date` | Same as above. |
| `automated_credit_decisions_count` | Operational throughput KPI; no standard reporting concept covers per-decision automation rate. Operator must decide whether this row belongs in `cc__credit` at all or in an operations-domain CC. |
| `total_credit_decisions_count` | Same as above; possibly DUPLICATE_OR_MERGE with #automated_credit_decisions_count once the operator clarifies what each measures. |
| `available_credit_lines` | Internal name/unit conflict: name (`*_lines`, plural) suggests count; `unit_type_code='currency'` suggests an amount. Operator must disambiguate before the row can be bound. |
| `total_credit_deployed` | Definition reads "Aggregate amount of loans and advances extended by the bank" — bank-perspective. `cc__credit` on BareCount is customer-perspective. Operator must either re-author the definition or DEMOTE the row. |

### 6.2 HOLD (1)

| CF | Why unresolved |
|---|---|
| `customer_credit_risk_rating` | `description_text` is empty. Per SOP §9 halt rules, this is a weak-definition blocker. The first lever is `POST /api/business-fields/:id/correct-definition` (D408 path), not a factory admit. |

---

## 7. Reusable machinery created

Pilot 1 produced a generalised toolkit. Every future D409 admission queue (asset, ISO 20022, depreciation, tax, treasury, payroll, derivatives) uses the same machinery without per-BF design ceremony.

### 7.1 Endpoints

- `POST /api/business-fields/:id/admit-from-candidate-import` ([bc-core@cc8b2d9](https://example.invalid/) — `StandardFieldController.admitBfFromCandidateImport`). Closes the `candidate_import → certified_catalog` edge atomically with full SDA G1-G8 gate.
- `POST /api/onboarding/cc/:contractId/field-selection` ([bc-core@33d4394](https://example.invalid/) — `CcOnboardingController.addFieldSelection`). Narrow in-place additive extension of an active CC version's `field_selection`; idempotent on already-present BFs; no CM re-pin, no tenant onboarding.

### 7.2 Schema

- `certification_record.action_code` enum value `admit_bf_from_candidate_import` (added by DBCP-1q-I, bc-core@723baa1). The CHECK constraint is now 17 values; the new value is fully reversible via the paired revert SQL (refuses if any row uses it).

### 7.3 Scripts

- `bc-core/scripts/apply-d409-admit-ready-bfs.mjs` — generic apply driver for any D409 packet JSONL with `moderator_verdict='ADMIT_READY'`; dry-run by default; halt-on-first-failure; per-target JSONL + summary; reusable across all admission queues.
- `bc-core/scripts/apply-d409-cc-credit-rebind-4.mjs` — cc__credit-specific mapping apply with per-mapping post-verify and pre/post invariant check; the pattern (single batched `addMappings` call + DB read-back) is reusable.
- `bc-core/scripts/build-d409-*.mjs` — packet builders (orphan-CF triage, single-row evidence deep dive, batch triage, admission+rebind plan). The factory's read-only packet templates.

### 7.4 Governance artifacts

- D409 SOP v0.1, agent prompt scaffold v0.1, credit-facility modeling policy v0.1 (the generic-first hybrid).
- `/admit-from-candidate-import` endpoint design v0.1 (sibling pattern for any future state-machine edge that needs a narrow governed primitive).
- Two gap reports recording the exact governance gaps and the discipline of halting before any DB write.

---

## 8. Lessons learned

The eleven sessions produced concrete operational discipline that should propagate to every future D409 queue.

1. **Batch triage works; single-row deep dives should be exceptions.** Pilot 1A took one full session for one CF (`revolving_credit_limit`); Pilot 1B did the remaining 10 in one session, at the same evidence bar, via lane batching. The throughput multiplier was real (10× per session) and the verdict quality did not drop. Future queues should default to lane-batched triage and reserve deep-dives for genuinely ambiguous rows.
2. **Generic-first modeling avoids duplicate BF proliferation.** The first packet's verdict (3 ADMIT_READY new BFs, including two revolving-specific ones) would have created parallel BFs (generic + revolving subtype) and required a future merge. The modeling policy collapsed those four in-flight rows to 2 generic BFs + 4 CF rebinds, with the revolving specialisation carried at the mapping layer. The XBRL taxonomy already models the distinction this way; mirroring its design avoided a catalog drift.
3. **`field_selection` is a real governance boundary.** Admitting a BF to `certified_catalog` is necessary but not sufficient to bind it; the active CC version's `field_selection` is a second gate. The narrow add-field-selection endpoint formalises this edge without dragging in the heavyweight version-bump orchestrator's CM/tenant side-effects.
4. **No direct SQL patching.** Both governance gaps tempted a one-line SQL fix (`UPDATE business_field SET catalog_state_code=...` or `UPDATE canonical_contract_version SET contract_json=...`). Both were declined per the SOP write boundaries + CLAUDE.md DB Change Protocol + foundation hard rule "No DB row hand-edits". The clean fix was a new governed primitive each time.
5. **Agents recommend; endpoints/scripts mutate.** The D409 core rule held across 11 sessions. Even the deterministic-no-LLM packet builders produced only recommendations; every state change went through a governed endpoint or an explicitly approved DBCP.
6. **Coverage pressure must not return.** Three explicit refusals during the pilot:
   - The Pilot 1B builder forcibly downgraded heuristic-only ADMIT_READY verdicts to NEEDS_EVIDENCE (the script will never emit ADMIT_READY from heuristics alone).
   - The modeling policy refused parallel generic + subtype BFs unless a §3-C escape condition is satisfied.
   - The gap reports refused the "DBCP-for-this-one-BF" shortcut in favour of a generalising endpoint.
7. **Halt-on-first-failure is not an inconvenience — it is the contract.** Two real defects were caught at the apply boundary (uppercase `piiClassification`, then `field_selection` refusal). In both cases halt-on-first-failure prevented partial writes and gave the operator a clear gap to close. A retry-and-fix-up loop would have produced silently-broken state.
8. **Audit-trail honesty matters more than completeness.** The field_selection update mutates `contract_json` in place; no `certification_record` primitive exists for canonical_contract changes. The pilot recorded that gap honestly in the commit message and surfaced it as a follow-up rather than inventing a parallel ledger.

---

## 9. Invariants / final counts

Verified read-only at closeout time (SES-c53953, 2026-05-17). All match the expected post-Pilot-1 state exactly.

| Counter | Expected at closeout | Verified at closeout |
|---|---:|---:|
| `bf_total` | 7064 | 7064 |
| `cf_total` | 3097 | 3097 |
| `mc_total` | 780 | 780 |
| `cc_field_mapping_total` | 1607 | 1607 |
| `business_field.catalog_state_code = candidate_import` | 5007 | 5007 |
| `business_field.catalog_state_code = certified_catalog` | 1657 | 1657 |
| `business_field.catalog_state_code = correction_required` | 12 | 12 |
| `business_field.catalog_state_code = demoted_catalog` | 388 | 388 |
| `certification_record.action_code = admit_bf_from_candidate_import` | 2 | 2 |
| `certification_record.action_code = admit_bf_from_correction_required` | 0 | 0 |
| `certification_record.action_code = remediate_bf_semantics` | 1396 | 1396 |
| `certification_record.action_code = admit_bf_catalog` | 1651 | 1651 |
| `certification_record.action_code = mark_bf_correction_required` | 30 | 30 |
| `certification_record.action_code = demote_bf_catalog` | 388 | 388 |
| `certification_record.action_code = recertify_bf_catalog` | 4 | 4 |

Deltas from the D408 closeout baseline (SES-c5af8c):

| Counter | D408 closeout | D409 Pilot 1 closeout | Δ |
|---|---:|---:|---:|
| `bf_total` | 7062 | 7064 | **+2** (two generic facility BFs) |
| `certified_catalog` | 1655 | 1657 | **+2** |
| `admit_bf_from_candidate_import` | 0 | 2 | **+2** |
| `cc_field_mapping_total` | 1603 | 1607 | **+4** (four cc__credit rebinds) |
| every other counter | — | — | unchanged |

---

## 10. Next recommended work

### 10.1 Preference

**Finish the cc__credit evidence batch first, then move to the asset residuals.** Reasoning:

- The 6 NEEDS_EVIDENCE + 1 HOLD cc__credit rows are the smallest, most narrowly-scoped pending work. Closing them keeps the cc__credit lane fully resolved on both the modeling side (already done) and the evidence side, giving the factory a fully-cleared first canonical contract.
- The asset residual queue is larger (~50 rows including the depreciation flow and the A1 MISMATCH orphans), spans multiple modeling questions (new BF for depreciation expense, axis vs object_class for asset subclasses), and benefits from being attacked after the operator workflow has been validated end-to-end on cc__credit's evidence batch. Evidence-sourcing fatigue is real; doing cc__credit first builds operator confidence on a known shape.
- The ISO 20022 modeling row (`iso20022_camt_xchg_rate`) is precedent-setting (DEMOTE + sibling bo-modeling packet) and benefits from being run *after* both cc__credit and asset experience, not in parallel. Run it third.

### 10.2 Option A — cc__credit evidence batch (recommended next)

Process the 6 NEEDS_EVIDENCE rows and 1 HOLD row in one or two sessions. Tactics:

- For the 4 operational rows (`*_decisions_count` ×2, `available_credit_lines`, `total_credit_deployed`): operator decides whether each belongs in cc__credit at all. Possible verdicts: DEMOTE_RECOMMENDED (route to operations-domain CC), re-author definition (if customer-perspective intent), or NEEDS_EVIDENCE staying parked.
- For the 2 date rows (`credit_application_submission_date`, `credit_approval_completion_date`): operator sources OAGIS credit-application BOD elements or domain SDA. If sourced, the existing `apply-d409-admit-ready-bfs.mjs` runs them.
- For the 1 HOLD row (`customer_credit_risk_rating`): operator runs `POST /api/business-fields/:id/correct-definition` with the real definition (D408 path), then a separate rebind cycle if the row's binding needs updating.

### 10.3 Option B — Asset residuals (recommended after Option A)

Process the asset queue from D408 SES-c5af8c residuals:

- 45 A1 orphan CFs from DBCP-1q-E (asset_*_amount MISMATCH cc_field_mapping removal).
- 1 REVIEW row (`change_in_value_of_underlying_asset`).
- 1 INSUFFICIENT_CONTEXT row (`total_asset_value`).
- 3 P&L depreciation flow CFs — operator decides whether to admit a new `asset_depreciation_expense_amount` BF (likely yes, generic, via the now-standing apply chain).

The reusable machinery from Pilot 1 covers every step end-to-end. The only new design likely needed is a depreciation-flow modeling-policy note (analogous to the credit-facility one) if the asset subclasses raise an axis-vs-object_class question.

### 10.4 Option C — ISO 20022 modeling (defer)

`iso20022_camt_xchg_rate` — defer to a third session after cc__credit evidence batch and asset residuals are clear. This row is precedent-setting and benefits from the prior two queues' lessons.

---

## 11. References

- [ADR-b8ec00](../../../governance/adrs/ADR-b8ec00.md) — DEC-b8ec00 (D409)
- [D409 SOP v0.1](../../work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md)
- [D409 agent prompt scaffold v0.1](../../work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-agent-prompt-scaffold.md)
- [D409 credit-facility modeling policy v0.1](../../work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-credit-facility-modeling-policy.md)
- [D409 admit-from-candidate-import design v0.1](../../work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-admit-from-candidate-import-design-DEC-b8ec00.md)
- [D408 correction_required closeout (parent)](2026-05-17-d408-correction-cleanup-closeout-DEC-1ce490.md)
- [the-invariants.md](../../../foundation/the-invariants.md) — Foundation invariants
- CLAUDE.md §Foundation Invariant Check, §Database Change Protocol, §SOP Compliance, §Coding Standards

### Changelog

| Version | Date | Note |
|---|---|---|
| 1.0 | 2026-05-17 | Initial closeout (SES-c53953). Pilot 1 closed; 4 rows resolved, 7 rows handed off; reusable machinery shipped. |
