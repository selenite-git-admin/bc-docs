---
title: Editorial rebind evidence handling (M13 PE-MC carry-forward) — DBCP
status: locked
date: 2026-06-08
project: bc-core
domain: implementation
governs: DEC-957fb0 (D434 editorial rebind evidence) · DEC-c3e57f (D422 MCF) · DEC-a6258b (D430) · DEC-4a17e0 (D431)
kind: governed-write-path DBCP (carry-forward; DDL-assessment inside)
parent: mcf-mcv-binding-refresh-rebind-dbcp-2026-06-08.md
---

# Editorial rebind evidence handling (M13 PE-MC carry-forward) — DBCP

**Documentation only. Do not implement.** Locks the implementation plan for the decision **DEC-957fb0 (D434)**:
how M13 PE-MC eligibility evidence is satisfied for **editorial rebind** successors (MCVs minted by
`MetricMcvRebindService`) via a **governed carry-forward** — never a silent default-pass, never a copied
verifier result. Implementation is a **separate held PR** after this DBCP is approved.

## Execution status — IMPLEMENTED & EXECUTED (2026-06-09)

> **This DBCP is fully discharged.** The carry-forward was implemented and SHA-pinned-merged (bc-core PR #248
> `0ca8afe`); the governed abandon path it assumed (§5) was surfaced + built (PR #249 `7f83267`); the M15
> supersession endpoint was added (PR #250 `d92dda3`). The plan was then **executed live on ARPI**: failed
> successor `9ffed384` abandoned → fresh successor **`b1933c30`** minted with carry-forward applied (NF1
> grounding inherited from panel `2d6987bd`; fixture carried from `8585648a` → **fresh** verifier bound to the
> successor package hash `a72bc168…`, verdict PASS) → M13 PASS (PE-MC-1/5/10) → M14 active → M15 superseded
> predecessor `8c088f55`. Final: exactly one active ARPI MCV = `b1933c30`; `metric_supersession` row
> `0cb30b6c…` (`correction_class_code=editorial`). The §4 PE-MC-8 stance was corrected to **non-blocking at
> platform M14** and locked as **DEC-bd6ceb / D435 (Model A)**. Full record:
> `mcf-arpi-editorial-rebind-arc-closeout-2026-06-09.md` · change record **CHG-3daea8** (`TSK-bb5cd4`).

## Grounding (live, read-only — 2026-06-08)
First live M13 on the ARPI rebind successor **`9ffed384`** (parent `e3c6ef6c`, derived
`mc_name=average_revenue_per_invoice__rebind_8c088f55`, state advanced **draft → review**) returned:
- **PASS:** PE-MC-2 (grain), -3 (roles), -4 (types), -6 (temporal), -7 (computed dims), -9 (identity) — the metric is semantically sound.
- **REJECT:** PE-MC-1 `no panel_run_uid on metric_create cert`; PE-MC-5 + PE-MC-10 `no fixture present on MCV`.
- **OPERATOR_REVIEW:** PE-MC-8 `default-pass-pending-m18+` (framework gap, all metrics).
- `approved=false`, predecessor `8c088f55` untouched, **0** `metric_supersession`, no M14.

The predecessor **8c088f55** carries the inheritable source: create-cert `panel_run_uid=2d6987bd` (panel run
has `consensus_payload_json`), fixture `8585648a` (bound `sha256:6354f1d5…`), passing verifier `b16096a6`.
**Crux:** the successor's package signature is **different** (`sha256:a72bc168…`) because the rebind changes
`variable_binding_set_hash`; so the predecessor's verifier result is **stale** for the successor and cannot be
inherited as proof.

## 0. Editorial-equivalence precondition (gate — all must hold vs predecessor)
Carry-forward is permitted ONLY when:
- `formula_intent_hash` unchanged · `filter_set_hash` unchanged · grain (`grain_entity_id`) unchanged ·
  temporal gate (`temporal_gate_shape_code` + params) unchanged · variable **roles** unchanged ·
  each rebound concept passes the same `representation_term` + `data_type` gate (**unit may refresh**).
- Computed deterministically: compare the successor's M7/M8 `formula_intent_hash` + `filter_set_hash` to the
  predecessor's; assert grain/temporal/roles equality; assert the rebind's gate-5 result. **Only
  `variable_binding_set_hash` may differ** (and only by same-`representation_term`/`data_type` successors).
- If any fail → **no carry-forward**; the metric is treated as fresh (full M12 → M12.5 → M13). Refuse with a
  clear error; do not partially carry forward.

## 1. PE-MC-1 (provenance / grounding) — inherit by explicit reference
- **Mechanism (primary):** at rebind draft creation, `MetricMcvRebindService` resolves the predecessor's
  `metric_create` cert panel attestation and **stamps it onto the successor's `metric_create` cert**, gated on §0.
  **NF1 all-or-none (refinement 2026-06-08 — implemented):** the substrate `mcf_cert_nf1_all_or_none_chk` CHECK +
  `validateNf1PanelAttestation` require the SIX panel-attestation fields to be all-null or all-non-null. Grounding
  inheritance therefore carries the **whole NF1 tuple** — `panel_run_uid`, `prompt_version`, `model_identity_json`,
  `input_hash`, `sampling_status`, `grounding_check_result` — **not `panel_run_uid` alone** (a partial stamp would be
  rejected by the CHECK). `RebindEvidenceCarryForwardService.readPredecessorNf1Attestation` returns all six or null
  (and throws on the substrate-impossible partial state); the rebind service stamps all six or none. PE-MC-1 then
  reads `ctx.panelRunUid` normally, loads the predecessor's grounding signals, and PASSes iff grounding is clean
  (claims grounded, no quarantine).
- **Provenance (required):** PE-MC-1 `evidence_json.verdict_signals` MUST include
  `grounding_inherited_from_panel_run: <uid>` and `rebind_predecessor_mcv: <8c088f55>`; the cert
  `gate_results_json` records the same. **No silent default-pass** — if no inheritable panel_run resolves, PE-MC-1 REJECTs.
- **Why valid:** grounding is package-independent + semantic; an editorial rebind introduces no new claims.
- **Alt (deferred):** check-time resolution in `runPeMc1Provenance` via `supersedes_version_uid` + rebind
  provenance. Not used for the 9ffed384 repair (its cert is immutable — see §5) but acceptable for a future
  in-place model. The rebind-time stamp (primary) keeps the successor self-contained + auditable.

## 2. PE-MC-5 / PE-MC-10 (fixture + self-verification) — copy content, re-bind, re-verify
- **Do NOT** copy the predecessor verifier result as proof.
- At rebind draft creation (after §0): **copy fixture CONTENT** from the predecessor's fixture
  (`section_a_inputs_json` / `section_b_expected_output_json` / `section_c_resolver_config_json`) into a **new**
  `mcf.metric_self_verification_fixture` on the successor MCV, with `bound_package_signature_hash =` the
  **successor's** package signature, and provenance `carried_from_fixture: <8585648a>`.
- **Run a fresh self-verification** (existing `MetricSelfVerificationService`) against the new fixture →
  `mcf.metric_self_verification_result` bound to the successor's `package_signature_hash_at_run`. Because the
  metric computes equivalently (§0), the fresh verdict should be `pass`.
- PE-MC-5 then finds a structurally-valid fixture; PE-MC-10 finds a fresh `pass` verifier whose
  `bound_package_signature_hash_at_run == currentPackageHash` → PASS.
- **Provenance (required):** PE-MC-5/-10 `evidence_json` MUST include `carried_from_fixture: <uid>` and the new
  `verifier_result_uid` + its bound hash.

## 2.1 Partial-state + atomicity (refinement 2026-06-08 — implemented)
The successor **draft + cert** (carrying any inherited NF1 grounding) commit FIRST; the **fixture + fresh verifier**
commit AFTER — **three commit points**, mirroring M12.5's deliberately staged boundary
(`createMetricDraft` tx → fixture tx → verifier tx). M12.5 splits fixture/verifier on purpose: the idempotent fixture
`catch-unique → SELECT` must commit before the verifier runs in a fresh tx (a UNIQUE violation aborts the current
Postgres tx). The rebind carry-forward mirrors this exactly.

**Full draft-level all-or-none is NOT adopted (feasibility-assessed).** It would require making M4's private
`createMetricDraftInTx` public — breaching the rebind service's "compose the EXISTING public `createMetricDraft`
primitive" discipline — AND diverging from M12.5's canonical staging AND multiplying the tx-abort surface across the
combined draft+fixture idempotency paths. The rebind successor is therefore **no less atomic than any other MCF
draft** (M12.5 has the identical property).

**Failure modes + treatment:**

| Stage outcome | Resulting draft | M13 | Treatment |
|---|---|---|---|
| §0 not equivalent | draft, no grounding, no fixture | PE-MC-1/5/10 REJECT | designed (mint-as-today); abandon or full M12 |
| §0 holds, no inheritable NF1 grounding | draft, no grounding, no fixture | PE-MC-1/5/10 REJECT | designed; abandon or full M12 |
| fixture mint / fresh verify **RAISES** | draft + grounding, **no / partial fixture+verifier** | PE-MC-5/10 REJECT | **partial-state → governed-abandon** |
| fresh verify returns `fail` / `structural_reject` | draft + grounding + fixture + verifier(fail) | PE-MC-10 REJECT | complete evidence, failing verdict; abandon |
| all succeed | draft + grounding + fixture + fresh `pass` verifier | PE-MC-1/5/10 PASS | M13-ready |

The genuine partial state is **only** the RAISE case. It is made **emitted, not inferred** (Invariant VI): the rebind
result carries `editorialCarryForward.carryForwardFailed=true` + `failureStage` + the committed draft uid (the
governed-abandon target) **instead of propagating a bare 500**. M13 PE-MC-5/10 REJECT is the persisted backstop if
that response is lost — **a partial successor can never silently pass M13.** Governed-abandon = the existing
draft/review reject path (`archived_at`; Invariant III — history appended, never rewritten), which also frees the
derived `mc_name` for a fresh re-invocation. Tested in `metric-mcv-rebind.service.spec.ts`
(§2.1 partial-state describe block: RAISE → `carryForwardFailed=true` + draft uid returned + no throw; null result →
designed `carryForwardFailed=false`).

## 3. Provenance fields (exact)
| Surface | Field | Value |
|---|---|---|
| cert (`metric_create`) | NF1 tuple (6 fields) | predecessor's `panel_run_uid` + `prompt_version` + `model_identity_json` + `input_hash` + `sampling_status` + `grounding_check_result`, stamped **all-or-none** (§1) |
| cert `gate_results_json` | `editorial_carry_forward` | `{ predecessor_mcv, grounding_inherited_from_panel_run, carried_from_fixture, equivalence:{formula_intent_hash_match,filter_set_hash_match,grain_match,temporal_match,roles_match,concept_compat_pass} }` |
| fixture | `carried_from_fixture` | predecessor fixture uid (storage — see §8 DDL assessment) |
| PE-MC-1 evidence | `grounding_inherited_from_panel_run`, `rebind_predecessor_mcv` | as above |
| PE-MC-5/-10 evidence | `carried_from_fixture`, `verifier_result_uid`, `bound_package_signature_hash_at_run` | as above |

## 4. PE-MC-8 — non-blocking at M13 AND platform M14 (Model A — locked by DEC-bd6ceb / D435)
`default-pass-pending-m18+` is OPERATOR_REVIEW for **every** metric and is a **tenant/runtime-readiness
placeholder**, not a metric-package defect. It is out of scope for rebind evidence handling and must not be
folded into it.

**Corrected policy** (this supersedes the prior, inaccurate claim that PE-MC-8 *"will continue to block
auto-approve"* — that contradicted the implemented SSOT and the M13/M14 DBCPs):
- PE-MC-8 default-mode OPERATOR_REVIEW is **PASS-equivalent at M13 approval** (draft→review→approved). SSOT:
  M13 DBCP §4.5 aggregation rule (`PASS_OR_DEFAULT_OR={8}`); evaluator `runPeMc8RuntimeReadinessIntent` +
  `aggregateApproveEligible`.
- PE-MC-8 default-mode OPERATOR_REVIEW is **PASS-equivalent at platform M14 activation** (approved→active). SSOT:
  M14 DBCP §6 gate; `McfPublicationActivationController.assertActivationGate` → `checkPeMc8Verdict`.
- It therefore **blocks neither** platform gate today. Runtime-readiness enforcement is **deferred to tenant
  binding (M18+ / MLS-15-25)** — platform activation establishes the metric definition as canon, which is not a
  runtime-readiness concern.
- Only a future explicit **`operator-reject`** mode (PE-MC-8 evidence `mode='operator-reject'`, currently
  unimplemented per M13 DBCP §4.3 D-M13-10b) would emit `VERDICT_REJECT` and block aggregation at both gates.

Locked as **Model A** by **DEC-bd6ceb (D435)**. **No code change is required** — the implemented behavior already
matches. Consequence: an approved successor (e.g. ARPI `b1933c30`) can be activated (M14) today with only an
operator rationale; no PE-MC-8 acknowledgement/override is needed.

## 5. Treatment of the existing reviewed successor `9ffed384` — Option A (governed abandon + fresh successor)
- After implementation: **governed-abandon** `9ffed384` via the existing draft/review abandon (reject) path
  (sets `archived_at`; no raw DELETE/UPDATE — Invariant III). This frees the deterministic derived
  `mc_name average_revenue_per_invoice__rebind_8c088f55` (the rebind collision-guard, gate 8, will then permit a
  fresh successor under the same derived name).
- Re-invoke the rebind (now carry-forward-aware) → a **fresh** successor draft that stamps inherited grounding +
  carries+re-verifies the fixture at creation → M13 PASSes PE-MC-1/5/10 (PE-MC-8 still OPERATOR_REVIEW per §4).
- **Option B rejected for `9ffed384`:** its `metric_create` cert is immutable (cannot retroactively stamp
  `panel_run_uid`, forcing check-time-only grounding) and an in-place PE-MC re-run leaves a mixed
  REJECT-then-PASS ledger. A is preferred unless a future change makes safe in-place PE-MC re-run on `review`
  explicitly supported. The current `9ffed384` REJECT rows remain as an immutable audit record of the gap.

## 6. Tests (held PR)
- **Editorial-equivalence gate:** passes for ARPI rebind; refuses when formula/filter/grain/temporal/roles
  differ; refuses when a rebound concept fails representation_term/data_type; unit-only drift allowed.
- **PE-MC-1 inherit:** cert carries predecessor `panel_run_uid`; evidence records
  `grounding_inherited_from_panel_run` + `rebind_predecessor_mcv`; REJECT when no inheritable panel_run.
- **PE-MC-5/10:** new fixture carries content + binds to successor package hash + provenance
  `carried_from_fixture`; fresh verifier result binds to successor hash; PE-MC-10 PASS only when the fresh
  verifier `bound_hash == currentPackageHash` (regression: a copied predecessor verifier with the OLD hash must
  NOT pass).
- **End-to-end (integration, SAVEPOINT-rolled-back):** rebind → carry-forward → M13 → PE-MC-1/2/3/4/5/6/7/9 PASS,
  PE-MC-8 OPERATOR_REVIEW, PE-MC-10 PASS; MCV advances to `review`/`approved`; predecessor untouched; no supersede; no M14.
- **PE-MC-8 untouched** (still OPERATOR_REVIEW) — proves §4.

## 7. Rollback
- Pre-merge: docs-only; nothing to roll back. The held PR is revertable (no DDL if §8 resolves to jsonb).
- Post-merge, pre-use: feature is inert until a rebind is invoked.
- A carried-forward fresh successor that fails is abandoned via the governed draft/review reject path (Invariant
  III: history appended, never rewritten). The abandoned `9ffed384` is **not** un-abandoned.

## 8. Implementation surfaces + DDL assessment
- **`MetricMcvRebindService`** (or a new `RebindEvidenceCarryForwardService` it composes): §0 equivalence check;
  resolve + stamp predecessor `panel_run_uid`; copy fixture content + mint successor fixture; invoke
  `MetricSelfVerificationService` for the fresh verifier result. All via **existing** governed primitives.
- **M13 evaluator:** minimal/no change under the rebind-time-stamp model (PE-MC-1/5/10 read the stamped cert +
  carried fixture + fresh verifier normally). Add provenance assertions in evidence only.
- **DDL assessment:** the carry-forward uses existing tables + jsonb evidence. The single open item is where
  `carried_from_fixture` provenance lives on `mcf.metric_self_verification_fixture`. **Preferred: a jsonb
  metadata field if one exists; else propose the smallest additive `provenance_json jsonb` column under the
  Database Change Protocol (explicit approval) — NOT applied in this DBCP.** No other DDL anticipated.

## 9. Explicit exclusions
- No runtime evaluation · no tenant fact / `metric_snapshot` / `contract.*` writes · no M14 activation · no M15
  supersession · no MCF materialization (M12.5) · no fresh M12 panel · no mutation of the predecessor or of
  `9ffed384`'s existing immutable cert/PE rows · PE-MC-8 not addressed here.
