---
title: ARPI Editorial-Rebind Arc — Closeout
description: Closeout record for the live ARPI (average_revenue_per_invoice) editorial-rebind arc executed end-to-end through the governed MCF lifecycle — abandon of the failed successor 9ffed384, mint of fresh successor b1933c30 (D434 evidence carry-forward), M13 pass, M14 activation, M15 supersession of predecessor 8c088f55. Records the final lineage, what D434/D435 proved, the exact substrate state, the no-materialization / no-tenant-runtime boundary, follow-ups, and the recommended narrow first Step-5 materialization-resume slice. Record of completed work; authorizes nothing further.
status: complete
date: 2026-06-09
project: bc-core
domain: contracts
subdomain: metric-runtime
focus: editorial-rebind-closeout
governs: DEC-957fb0 (D434 editorial-rebind evidence) · DEC-bd6ceb (D435 Model A) · DEC-c3e57f (D422 MCF) · DEC-a6258b (D430) · DEC-4a17e0 (D431)
change_record: CHG-3daea8 (TSK-bb5cd4)
---

# ARPI Editorial-Rebind Arc — Closeout

> **What this is.** A record of completed, live, governed work — not authority and not an instruction. The ARPI metric contract was rebound from superseded BCF concept anchors to their active successors, end-to-end through the MCF lifecycle (abandon → rebind → M13 → M14 → M15), leaving exactly one clean active ARPI MCV. It authorizes nothing further; the next step (Step-5 materialization) is recommended at the end and tracked as a held task. Change record: **CHG-3daea8** (`TSK-bb5cd4`).

## 1. Why the arc existed

ARPI's active MCV `8c088f55` bound its three variables to **superseded** BCF concepts (`a42d3fc0` amount, `095afe86` identifier, `d05f24b3` date). The active OC-v2/CC-v2 for the Customer Invoice grain (`cc__customer_invoice_arpi_slice`) declares their **active successors** (`1a2ac2f2`, `51482979`, `61e19048`). Per Invariant III the active MCV is immutable, so the fix is a **new governed MCV** that supersedes it with refreshed bindings — an *identity-preserving* change (same name, grain `e3963e45`, formula `divide(sum(numerator_source), count_distinct(denominator_key))`; only the variable→concept bindings move). This is the precondition for **D429 Step 5** (resume D428 MCF materialization): the synthesis proof (`mcf-arpi-contract-json-synthesis-proof-2026-06-07.md`) blocked ARPI's evaluable envelope on exactly this superseded-binding gap.

## 2. Final lineage (live, 2026-06-09 — read-only census of all 5 ARPI MCVs)

| MCV | governance | is_current | parent MC | mc_name | note |
|---|---|---|---|---|---|
| **`b1933c30`** | **active** | **true** | `7596213d` | `average_revenue_per_invoice__rebind_8c088f55` | **the one current ARPI** |
| `8c088f55` | superseded | false | `49cdde1a` | `average_revenue_per_invoice` | retired predecessor (this arc) |
| `9ffed384` | review | false | `e3c6ef6c` (archived) | `…__rebind_8c088f55` | failed prior successor — governed-abandoned |
| `5e7cce21` | draft | false | `7528f9c9` (archived) | `average_revenue_per_invoice` | earlier draft |
| `b2c5c028` | draft | false | `196b4c8a` (archived) | `average_revenue_per_invoice` | earlier draft |

**Exactly one `active`/`is_current` ARPI MCV: `b1933c30`.** (Census: `mc_name ILIKE '%revenue%invoice%'` → 5 rows, 1 active.)

## 3. What D434 (and D435) proved

The arc was the first real exercise of the **editorial-rebind evidence-handling** machinery (DEC-957fb0 / D434) and the **Model A** publication-readiness stance (DEC-bd6ceb / D435):

- **Evidence carry-forward, not silent default-pass.** M13 PE-MC eligibility for a rebind successor is satisfied by a *governed* carry-forward gated on the §0 editorial-equivalence precondition (only `variable_binding_set_hash` may differ; same `representation_term`/`data_type`):
  - **PE-MC-1 (grounding):** the predecessor's whole **NF1 panel-attestation tuple** (six fields, all-or-none per `mcf_cert_nf1_all_or_none_chk`) is stamped onto the successor's `metric_create` cert — inherited by explicit reference, never fabricated.
  - **PE-MC-5/10 (fixture + verifier):** the predecessor's fixture is **copied** but the verifier is **re-run fresh and bound to the successor's package signature** (`a72bc168…` ≠ predecessor `6354f1d5…`), because the rebind changes the binding-set hash and a copied verdict would be stale proof (Invariant VI — evidence emitted, not inferred).
  - **Partial-state observability:** if carry-forward fails mid-way (draft committed, fixture/verifier not), the outcome is surfaced (`carryForwardFailed`/`failureStage`), never silently left half-built.
- **Abandon is governed, not a hand-edit.** The failed prior successor `9ffed384` was retired by a **cert-less soft-archive of its parent MC** (frees the derived `mc_name`); the MCV row is untouched. The path did not exist — it was surfaced as a mini-DBCP and built (PR #249) rather than improvised.
- **Model A (D435).** PE-MC-8 (`default-pass-pending-m18+`) is **OPERATOR_REVIEW** as a framework placeholder; it is **PASS-equivalent at M13 and at platform M14**. Tenant-runtime-readiness enforcement belongs to tenant binding / M18+, not platform publication. M13 therefore auto-advanced `b1933c30` draft→approved by design — confirmed intentional, not a defect.

**Net:** the rebind is provable as an *editorial correction* (meaning-preserving), and the chain of evidence behind the active metric is real (inherited grounding + fresh successor-bound verifier), not asserted.

## 4. Exact substrate state (verified, read-only)

| Object | Value |
|---|---|
| Active ARPI MCV | `b1933c30-c708-4ebe-b2b3-b2a82242f331` (`active`, `is_current=true`, parent `7596213d`) |
| Retired predecessor | `8c088f55-5cd2-41f0-a1e6-501dce0fe104` (`superseded`, `is_current=false`, parent `49cdde1a`) |
| `mcf.metric_supersession` row | `supersession_uid 0cb30b6c-e3c5-4ef0-ac2e-a8a66b5db36e`; pred `8c088f55` → succ `b1933c30`; `correction_class_code=editorial`; `operator_sub=8bdb9bd0-8827-4cc8-b640-2087658f1eb6`; `superseded_at=2026-06-09T03:53:25Z` |
| M15 cert | `89045e6e-228e-4d7f-b00f-f43fb2b46287` — `action_code=metric_supersede`, `active → superseded`, `subject_kind=metric_supersession`, `primitive_id=8c088f55`, `certifier_role_at_action=operator` |
| M14 cert (intact) | `a2586f9b-de56-448f-8318-b089c381e77a` — `metric_transition` `approved → active` + 10 M14 PE rows |
| Rebound bindings | `numerator_source → 1a2ac2f2` (amount), `denominator_key → 51482979` (identifier), `temporal_anchor → 61e19048` (date) |
| `metric_supersession` total | **1** |

PRs (all SHA-pinned squash-merged to bc-core `main`): **#248** carry-forward `0ca8afe` · **#249** governed abandon `7f83267` · **#250** M15 supersession endpoint `d92dda3`.

## 5. Boundary held — no materialization, no tenant runtime evaluation

The arc was confined to the **metric-contract layer** (`mcf.*`): variable bindings + governed MCV transitions + supersession cert/row. Explicitly **not** crossed:

- **No MCF materialization (M12.5 / Step 5).** Successor fixture count stayed `1`; no new materialized substrate. `synthesizeContractJson` was not run; no `contract.metric_contract*` row was written.
- **No tenant runtime evaluation.** No `progression.*` / `fact.ms_*` rows; no `metric_snapshot`. The platform `mcf.*` transitions do not evaluate metrics into tenant facts.
- **D428 §9 guardrail intact** — no contract.* materialization, no legacy wipe.

## 6. Follow-ups

| Task | What |
|---|---|
| **TSK-09505d** | M13 retry/cache reporting inconsistency — `findExistingEvaluation` uses a flat `every(===PASS)` that doesn't special-case PE-MC-8 default-mode the way the primary aggregate path does. |
| **TSK-2f8d82** | Persist non-override lifecycle rationale on MCF transition certs — `certification_record` has only `override_rationale_text` (null for non-override); M14/M15 operator rationale lands on the `metric_supersession` row but not on the transition cert itself. |
| **TSK-a8bedb** | Step-5 Slice 0 (read-only) — re-prove ARPI `contract_json` synthesis against the now-clean `b1933c30` (see §7). |
| **TSK-0ba31e** | Step-5 ARPI-only `synthesizeContractJson` + `contract.*` writer DBCP (held, D428 §9). |

## 7. Recommended narrow first Step-5 (materialization-resume) slice

ARPI is now the single clean active MCV with **active** bindings that the D430 resolver maps to the active CC-v2 field — the exact gap the 2026-06-07 synthesis proof said blocked Bar 2 (evaluation readiness). So the materialization door is unblocked *for ARPI only*. The narrowest safe first slice is **read-only proof, not a writer**:

**Slice 0 (read-only, go/no-go) — TSK-a8bedb.** Re-run the ARPI `contract_json` synthesis proof against `b1933c30`: for each rebound concept, `CanonicalConceptResolverService.resolve(e3963e45, concept)` → active CC-v2 field, and confirm the previously-`UNRESOLVED@C` envelope fields (`co_bindings.canonical_contract`, `fields_used`, `variables[].field_code`, `grain[].field_code`, `temporal_gate.field_code`) are now all derivable → an **evaluation-grade envelope is synthesizable**. No writes; no `synthesizeContractJson` implementation; D428 §9 guardrail untouched. This is the explicit go/no-go gate.

**Then (held) — TSK-0ba31e.** Only on a "go", design the ARPI-only `synthesizeContractJson` (MCF normalized → runtime `contract.metric_contract_version.contract_json`) + the materialization writer as a held DBCP per Option B (D428 single clean published store). The D432 legacy-authoring guard already recognizes this governed MCF writer as an authorized path. Known open sub-question: `contract.metric_contract.metric_definition_id` is `NOT NULL` — the synthesis proof flagged the FK handling; resolve it in the writer DBCP, not before.

**Why this ordering.** Prove the unblock on the one metric, read-only, before building any writer — the one-then-many / read-before-write discipline. ARPI is the right specimen because it is exactly the metric the synthesis proof was blocked on, and it is now provably clean.
