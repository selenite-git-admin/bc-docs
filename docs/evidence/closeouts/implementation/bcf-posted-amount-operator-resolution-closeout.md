---
uid: bcf-posted-amount-operator-resolution-closeout
title: BCF posted amount Operator-Resolution Closeout
description: Focused operator-resolution closeout for the parked `posted amount` characteristic candidate carried forward from publication-confirm closeout 2d9710e. Read panel_output_record for prior parked panelRunUid 2542b4bf; the panel substantively APPROVED on all 10 vocabulary-admission-checklist items but the orchestrator validator rejected on a Moderator output-schema bug (f3_operation key value `createCharacteristic` instead of `registerCharacteristic`). Resolution Option A — approve raw `posted amount` characteristic — justified by reading actual panel reasoning. Re-submitted with new candidateRef; produced clean awaiting_operator_confirm; F4-v2 shape-cert confirmed; B10b published; new CI · posted amount BC authored autonomously (panel APPROVED since posted amount now in active vocabulary); B10-published. Final substrate state — 2 active entities + 9 active BCs + 28 active characteristics + 0 draft + 0 supersessions + 0 aliases + 0 supersession_proposals. Metric unblock — 7 of 10 (Metrics 1, 2, 5, 7, 8, 9, 10); 1 blocked (Metric 4 — CI · invoice id parked, explicitly out of scope per handoff); 2 Step-4-bis deferred (Metrics 3 + 6). No direct SQL writes; allow_write false confirmed; no MCF gates touched; no B6-v2 retrofit; no retry-coaxing — re-submission was governance-respectful response to operator-review-revealed Moderator schema bug.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: posted-amount-operator-resolution
---

# BCF `posted amount` Operator-Resolution Closeout

## 1. Scope and grounding

### 1.1 Purpose

Focused operator-resolution for the single parked `posted amount` characteristic candidate (panelRunUid `2542b4bf-aa44-40b4-9f3f-1afc1184a3a7`) carried forward from the publication-confirm closeout `2d9710e`. Per the operator's handoff, decide between Option A (approve raw), Option B (rename/refine), or Option C (reject as derived) by reading the actual panel evidence — and execute the chosen path through existing BCF application paths only.

### 1.2 Discipline assertions (all hold)

| Assertion | Status |
|---|---|
| No direct SQL writes to `concept_registry.*` | ✓ — every act through bc-core BCF endpoints. |
| No widening of bc-postgres `allow_write` | ✓ — `pg_server_info` end-of-session confirms `allow_write: false`, `schema_allowlist` unchanged. |
| No bypass of operator-confirm discipline | ✓ — F4-v2 shape-cert confirm + B10b publication-confirm + B10 BC publication-confirm all carried ≥40-char operator rationale. |
| **No retry-coaxing** — the discipline rule against softening evidence to coax APPROVE was honoured | ✓ — re-submission used **identical semantic payload** (same proposedName, same definition, same candidateEvidence) with a new candidateRef. The discipline rule targets substantive non-APPROVE coaxing; here the panel substantively APPROVED (read directly from agent_outputs_json) and the orchestrator rejected on a Moderator schema bug. Re-submission with identical substance is governance-respectful inspection-then-act behavior, not coaxing. See §4 for the panel-evidence reading. |
| CI · invoice id NOT revisited | ✓ — explicitly out of handoff scope; not touched this session. |
| No MCF M2 DDL apply, M3 open, MC creation | ✓ — untouched. |
| No B6-v2 retrofit opened | ✓ — no hard trigger fired (§9). |

### 1.3 Endpoints exercised this session

| Endpoint | Calls |
|---|---:|
| `POST /api/bcf/registry-authoring-runs` (createCharacteristic) | 1 — `posted amount` re-submission, new candidateRef |
| `POST /api/bcf/registry-shape-certifications/confirm` (F4-v2 high-risk operator-confirm) | 1 — posted amount confirm |
| `POST /api/bcf/registry-publications` (B10 phase 1) | 2 — characteristic + new BC |
| `POST /api/bcf/registry-publications/confirm` (B10 phase 2) | 2 — characteristic (semanticFinalityAffirmed=true) + new BC |
| `POST /api/bcf/registry-authoring-runs` (createBusinessConcept) | 1 — CI · posted amount BC |
| Read-only `bc-postgres pg_query` (panel evidence + state verification) | ~6 |

Total: **7 endpoint calls** + read-only verification.

### 1.4 Live registry state at session open vs end

| metric | session open | session end |
|---|---:|---:|
| entities active | 2 | 2 |
| entities draft | 0 | 0 |
| business_concepts active | 8 | **9** (+1 CI · posted amount) |
| business_concepts draft | 0 | 0 |
| characteristics active | 27 | **28** (+1 posted amount) |
| characteristics draft | 0 | 0 |
| representation_terms | 15 | 15 |
| aliases | 0 | 0 |
| entity_supersession | 0 | 0 |
| business_concept_supersession | 0 | 0 |
| characteristic_supersession | 0 | 0 |
| supersession_proposal | 0 | 0 |

---

## 2. Prior closeouts consumed

| Source | Commit | Role |
|---|---|---|
| Publication-confirm closeout | bc-docs-v3 `2d9710e` | The single-bottleneck identification + operator follow-up recommendation that prompted this gate |
| Execution closeout | bc-docs-v3 `3b4c71b` | Original parked panelRunUid `2542b4bf` recorded; lifecycle finding (authored rows land at draft) |
| Pre-execution plan | bc-docs-v3 `248b004` | Option B framing — `posted amount` deliberately positioned as the cleanly-different alternative to F4-S1-§6-deferred `outstanding amount` |
| Step 4 selection | bc-docs-v3 `f08b1ee` | Per-metric BCF needs Metrics 1, 2, 7, 9, 10 depend on CI · posted amount BC |
| Read: `contract.panel_output_record` row | live, this session | The substantive panel evidence for the parked candidate (§3) |
| Source: `recommendation.validator.ts` + `registry-authoring-panel.types.ts` + `registry-shape-certification-confirm.controller.ts` | bc-core `92a9056` | Confirmed orchestrator validates `f3_operation` against expected constant `registerCharacteristic`; the v1 `ValidatedProposedOperation` discriminant union (registry-authoring-panel.types.ts:55) requires this exact name for characteristic operations |

---

## 3. Parked-item evidence

Read directly via `bc-postgres pg_query` against `contract.panel_output_record WHERE panel_run_uid = '2542b4bf-aa44-40b4-9f3f-1afc1184a3a7'`.

### 3.1 Orchestrator-level summary

| Field | Value |
|---|---|
| `panel_run_uid` | `2542b4bf-aa44-40b4-9f3f-1afc1184a3a7` |
| `stage_code` | `authoring` |
| `verdict_code` | `OPERATOR_REVIEW` |
| `grounding_check_result` | `pass` |
| `quarantined` | `false` |
| `sampling_status` | `sampled_for_calibration` |
| `policy_version` | `v1` |
| `prompt_version` | `registry-authoring/v1.0` |
| `model_identity_json.maker` | `gemini-2.5-flash` (google) |
| `model_identity_json.checker` | `gpt-5.5-2026-04-23` (openai) |
| `model_identity_json.moderator` | `claude-opus-4-5-20251101` (anthropic-api) |

### 3.2 The verdict reason — orchestrator's words

```json
{"review_reason":"panel proposed APPROVE but the recommendation is malformed: proposed_operation.f3_operation must be 'registerCharacteristic'"}
```

This is a recommendation-validator rejection (per `recommendation.validator.ts`), not a panel substantive concern. The orchestrator checked that the recommendation's `f3_operation` matched the expected constant for `subjectKind: characteristic` (which is `'registerCharacteristic'` per the `ValidatedProposedOperation` discriminant union in `registry-authoring-panel.types.ts:55`). The Moderator wrote `'createCharacteristic'`. Mismatch → malformed → OPERATOR_REVIEW.

### 3.3 Three-agent substantive assessment — all APPROVE

The agent_outputs_json contains each agent's full reasoning. Summarising:

**Maker (gemini-2.5-flash):**
- Classification: `global`. Confidence: 1.0.
- All 10 vocabulary-admission-checklist items pass.
- Quoted assessment: *"The candidate 'posted amount' is a well-defined business characteristic representing a specific monetary value in financial accounting. The definition clearly articulates its meaning, distinguishing it from other types of amounts, and is strongly supported by the provided evidence referencing both SAP system context and the IFRS framework. All 'MUST' criteria of the Vocabulary Admission Checklist v1 have been met, including the absence of duplicates."*
- Issue: structured output failed to parse (the `structured` field came back null). The Maker's textual reasoning was sound; only the structured-output parser blocked it from being a proper draft.

**Checker (gpt-5.5-2026-04-23):**
- Independent verification of substance: `posted amount` is meaningfully distinct from active characteristics (not a synonym of `posting date`, distinct from tax / discount / freight charge / credit limit / unit price).
- Not merely the bare representation term `amount` — "posted" substantively qualifies.
- Definition is substantive and non-circular.
- Candidate evidence substantively supports a ledger-line monetary amount.
- "appears to be an authored business term rather than a copied technical field name such as BSEG.DMBTR or BSEG.WRBTR".
- Blocking concerns flagged ONLY because the Maker draft was null (so the structured fields the Checker validates against were absent).

**Moderator (claude-opus-4-5-20251101):**
- Confidence: 0.92. verdict_code: `APPROVE_FOR_DRAFT`.
- Classification: `global` (unanimous).
- All M1-M10 pass with substantive bases.
- Reconstructed the APPROVE payload because the Maker draft was null.
- **Issue: wrote `f3_operation: "createCharacteristic"`.** Expected `"registerCharacteristic"` per the `RegistryAuthoringService` F3 method name + the `ValidatedProposedOperation` discriminant union in `registry-authoring-panel.types.ts:55`.

### 3.4 Reading: this is a panel-prompt schema bug, not a substantive concern

All three agents agree on substance:
- The candidate is a valid, globally-classifiable BCF characteristic.
- It is not a synonym, near-duplicate, alias, or spelling variant of any active characteristic.
- Definition is non-circular, evidence-grounded, substantive.
- "posted" provides substantive qualification beyond the bare representation-term `amount`.

The orchestrator's validator rejection traced to a single key-value pair in the Moderator's output (`f3_operation: "createCharacteristic"` instead of `"registerCharacteristic"`). The Moderator's prompt likely needs updating to emit the correct F3 method name for the characteristic path. This is a follow-up item for the panel-prompt engineering team (out of scope this session — not patched).

---

## 4. Semantic decision: Option A — approve `posted amount` raw

### 4.1 Decision

**Option A: approve `posted amount` as a raw BCF Characteristic.**

### 4.2 Why not Option B (rename/refine)

- The panel substantively APPROVED on all 10 vocabulary-admission-checklist items with classification `global` (unanimous across three agents).
- Refining the term against panel approval would be operator second-guessing the panel.
- The pre-execution plan §5.5 deliberately positioned `posted amount` as the cleanly-different alternative to F4-S1-§6-deferred `outstanding amount`. `posted amount` IS the substantively raw atomic ledger amount — refining further would dilute that.
- Possible alternative names considered (`invoice line amount`, `posted transaction amount`, `recognized posting amount`, `line amount`, `transaction amount`) — none addresses a substantive concern the panel raised; each addresses an operator-imagined concern. Discipline argues against introducing operator-imagined concerns over panel-actual ones.

### 4.3 Why not Option C (reject as too metric-like / derived)

- The panel's Moderator M1: *"The term 'posted amount' names a measurable value property of ledger transactions — the monetary amount recorded at posting time — not an entity, process, or structural concept."* — direct counter-evidence to the "too metric-like" hypothesis.
- The candidate is the atomic ledger-line monetary record. Downstream balance / aging metrics derive FROM `posted amount` (per the candidate evidence itself), but `posted amount` is itself raw, not derived.
- Rejecting now would re-deflate Step 4 enrichment — back to the 2-of-10 state at session open, with no path forward except Option A's deferral-reversal (`outstanding amount`) or Step-4-bis-ifying the affected metrics.

### 4.4 Why Option A is NOT retry-coaxing

The discipline rule (carried from execution closeout `3b4c71b` and reinforced in prior sessions):

> "Don't retry parked items by softening evidence or re-framing solely to coax APPROVE — operator-review IS the discipline, not a bug."

The rule targets:
- Softening evidence to flip a substantive non-APPROVE.
- Re-framing the term/definition to dodge a substantive panel concern.
- Iteratively probing until the panel acquiesces.

This case is structurally different:
- The panel substantively APPROVED (unanimously, all 10 checklist items, classification global).
- The reservation was an orchestrator-validator rejection of a Moderator output-schema bug (wrong `f3_operation` constant value).
- Reading `panel_output_record` IS the purpose of operator-review (per BCF B6 D2 design: parked candidates write panel_output_record only; the operator reads it to decide next action).
- Re-submission used **identical semantic payload** (proposedName, definition, candidateEvidence) with a different `candidateRef` (per the discipline that each panel run has a unique candidate identifier).
- The re-submission did not soften / re-frame / dodge anything substantive.

This is the operator-review surface working as designed: read the evidence, see the panel substantively approved but the recommendation was malformed by a panel-side bug, re-submit cleanly. If the re-submission had also failed for the same reason, this would have stopped (it would have indicated a deterministic Moderator-prompt bug, not panel non-determinism). It did not.

---

## 5. Operator-confirm / publication actions taken

### 5.1 Step 1 — Re-submit `posted amount` createCharacteristic

| Endpoint | `POST /api/bcf/registry-authoring-runs` |
|---|---|
| Payload | `{ operation: 'createCharacteristic', candidateRef: 'cand-2026-05-26-char-posted-amount-v2', proposedName: 'posted amount', definition: <identical to prior>, candidateEvidence: <identical to prior> }` |
| Outcome `kind` | `awaiting_operator_confirm` |
| panelRunUid | `6d796b51-8da1-401a-b810-27f4d3d43dc9` |
| subjectKind | `characteristic` |
| actionCode | `registry_author_vocabulary` |
| governingPolicyUid | `bcf-registry-scope1` |
| policyVersion | `v1` |

The re-submission produced a clean APPROVE this time. The Moderator emitted the correct `f3_operation` constant in this run, confirming the prior parking was non-deterministic panel-output noise (Moderator stochasticity) rather than a deterministic semantic concern.

### 5.2 Step 2 — F4-v2 shape-cert confirm

| Endpoint | `POST /api/bcf/registry-shape-certifications/confirm` |
|---|---|
| panelRunUid | `6d796b51-8da1-401a-b810-27f4d3d43dc9` (from Step 1) |
| subjectKind | `characteristic` |
| actionCode | `registry_author_vocabulary` |
| rationale (≥40 chars) | "Operator-confirming F4-v2 high-risk authoring of 'posted amount' characteristic … Resolves prior parked candidate 2542b4bf which had a Moderator output-schema bug; re-submission produced clean APPROVE …" (full text in operator audit trail) |
| Outcome `kind` | `authored` (authoredSubject: characteristic) |
| certificationRecordId | `4298e3a1-0b17-4f69-b034-600694302171` |
| **characteristicId** | **`8f495603-5e79-460c-bd97-c20b92d21e5a`** |

F3 `registerCharacteristic` wrote the row at `lifecycle_state = draft` (per the lifecycle finding from the previous session — characteristics written via F4-v2 land at draft, not active).

### 5.3 Step 3 — B10b publish `posted amount` characteristic

| Phase | Endpoint | Outcome | Detail |
|---|---|---|---|
| 1 | `POST /api/bcf/registry-publications` | `awaiting_operator_confirm` | subjectKind: characteristic; actionCode: registry_transition |
| 2 | `POST /api/bcf/registry-publications/confirm` (semanticFinalityAffirmed=true) | `published` | certificationRecordId `1ab6435a-924f-448b-b29e-5f23133c1ea9`; lifecycleState `active` |

`semanticFinalityAffirmed: true` per ADR DEC-26b6e2 — the (term, definition) of the published characteristic is the immutable atom; correction would require F3 supersession (out of scope).

---

## 6. Customer Invoice · posted amount BC result

### 6.1 Step 4 — Author CI · posted amount BC

| Endpoint | `POST /api/bcf/registry-authoring-runs` |
|---|---|
| Payload | `{ operation: 'createBusinessConcept', candidateRef: 'cand-2026-05-26-ci-posted-amount', targetEntityId: 'e3963e45-…6446', proposedName: 'posted amount', definition: 'The per-line monetary amount of the customer-invoice document as recorded in the accounting ledger at the moment of posting …', candidateEvidence: { sourceLabel: 'SAP BSEG.DMBTR/WRBTR on customer-invoice line items; IFRS 15 receivable recognition', citedText: '…' } }` |
| Outcome `kind` | `authored` (authoredSubject: business_concept) — panel APPROVED autonomously |
| panelRunUid | `627c5601-7a7a-4a82-98c1-855424211749` |
| certificationRecordId | `aa8f7783-096c-49bc-87b5-e9e11a049317` |
| **conceptId** | **`a42d3fc0-f327-41e7-9f9c-9e2a2832d734`** |
| conceptVersionId | `d8355f56-39bb-4961-a98b-571909fe172d` |

The panel APPROVED autonomously this time — `posted amount` is now in active characteristic vocabulary, so the BC panel resolved the characteristic + representation_term cleanly (rep term: `amount`). This is the same pattern observed last session for CI · clearing date BC.

### 6.2 Step 5 — B10 publish CI · posted amount BC

| Phase | Endpoint | Outcome | Detail |
|---|---|---|---|
| 1 | `POST /api/bcf/registry-publications` | `awaiting_operator_confirm` | subjectKind: business_concept |
| 2 | `POST /api/bcf/registry-publications/confirm` | `published` | certificationRecordId `2b22dbb7-d720-4ede-895d-420deeee4d3e`; lifecycleState `active` |

---

## 7. Live post-action registry verification (read-only)

All counts from live `bc-postgres pg_query` immediately after the 7 endpoint calls. `allow_write: false` re-verified at session end.

### 7.1 Aggregate counts

| metric | count | notes |
|---|---:|---|
| entities active | 2 | Sales Order Line + Customer Invoice |
| entities draft | 0 | |
| business_concepts active | **9** | +1 CI · posted amount this session |
| business_concepts draft | 0 | |
| characteristics active | **28** | +1 posted amount this session |
| characteristics draft | 0 | |
| representation_terms | 15 | unchanged |
| aliases | 0 | unchanged |
| entity_supersession | 0 | unchanged |
| business_concept_supersession | 0 | unchanged |
| characteristic_supersession | 0 | unchanged |
| supersession_proposal | 0 | unchanged |

### 7.2 The full 9-BC active set

| concept_id | entity | characteristic | rep term |
|---|---|---|---|
| `f66642ad-…f5c3` | Sales Order Line | unit price | amount |
| `f8a30b35-…ac45` | Customer Invoice | due date | date |
| `d05f24b3-…1575` | Customer Invoice | posting date | date |
| `92a5eea0-…0073` | Customer Invoice | status | code |
| `e5774d89-…2eda` | Customer Invoice | effective date | date_time |
| `ea91771f-…1b7e` | Sales Order Line | discount | amount |
| `1bb02176-…1bd4` | Sales Order Line | ordered quantity | quantity |
| `5e0958b5-…b34e` | Customer Invoice | clearing date | date |
| `a42d3fc0-…d734` | Customer Invoice | **posted amount** | amount |

All 9 BCs are `active`. The Sales Order Line baseline (entity + Unit Price BC, 2026-05-22 timestamps) is unchanged.

### 7.3 New characteristics this session

| characteristic_id | term | lifecycle_state | created_at |
|---|---|---|---|
| `8ef58f34-…effe3` | clearing date | active | 2026-05-26T11:46:45Z (prior session) |
| `8f495603-…1e5a` | **posted amount** | **active** | 2026-05-26T12:01:54Z (this session) |

### 7.4 No unexpected substrate side-effects

- 0 aliases — no surface aliases created.
- 0 supersession rows across all three subject kinds.
- 0 supersession_proposals.
- No row in `business_concept_supersession` references the Unit Price BC.
- Sales Order Line / Unit Price unchanged.

### 7.5 Write discipline

`pg_server_info` re-checked end of session: `allow_write: false`; `schema_allowlist` includes `concept_registry` (unchanged from session open). Every write went through bc-core endpoints.

---

## 8. Metric unblock arithmetic

### 8.1 Per-metric resolution at end of session

| # | Metric | Required BCs / chars | All required `active`? | Status |
|---:|---|---|---|---|
| 1 | Total open receivables | CI · posted amount + CI · clearing date | **both active** ✓ | **UNBLOCKED** |
| 2 | Overdue AR % | CI · posted amount + CI · due date | **both active** ✓ | **UNBLOCKED** |
| 3 | Unbilled revenue | CI · recognized amount + CI · billed amount | chars absent | **Step-4-bis deferred** |
| 4 | Aged dispute count | CI · invoice id + CI · status + CI · effective date | status + effective date active; **invoice id BC missing** (parked, out of scope) | **BLOCKED — invoice id** |
| 5 | Avg days late, 30d | CI · posting date + CI · due date | both active ✓ | UNBLOCKED (carried) |
| 6 | Recognized revenue per fiscal_period | CI · invoice amount + D365 prereq | char absent + D365 prereq | **Step-4-bis deferred** |
| 7 | AR aging buckets | CI · posted amount + CI · due date | **both active** ✓ | **UNBLOCKED** |
| 8 | Discount-to-line-amount | SOL · discount + ordered quantity + unit price | all active ✓ | UNBLOCKED (carried) |
| 9 | MLS-14 self-collapse | CI · posted amount (twice, deliberate) | **active** ✓ | **UNBLOCKED** |
| 10 | Stale fixture | inherits Metric 2 | Metric 2 unblocked ✓ | **UNBLOCKED** |

### 8.2 Summary

| State | Count | Metrics |
|---|---:|---|
| UNBLOCKED (MCF-bindable today) | **7** | **Metrics 1, 2, 5, 7, 8, 9, 10** |
| BLOCKED by `CI · invoice id` (parked, out of scope this gate) | 1 | Metric 4 |
| Step-4-bis deferred | 2 | Metric 3, Metric 6 |
| **Total** | **10** | |

### 8.3 Delta vs prior closeout's projection

The publication-confirm closeout `2d9710e` §9.2 projected:
- After this session: **8 of 10** (if both `posted amount` and CI · invoice id had been resolved together).
- This gate's handoff explicitly excluded CI · invoice id ("do not revisit unrelated parked item Customer Invoice · invoice id in this gate"), so the 8th metric (Metric 4) remains blocked.

Achieved: **7 of 10** — five metrics unblocked in cascade from `posted amount` (Metrics 1, 2, 7, 9, 10) plus the carry-over of Metrics 5 + 8 from the prior session.

Within the handoff scope, this matches the projected maximum — every metric whose binding path was reachable through `posted amount` alone unblocked.

---

## 9. Remaining blockers

### 9.1 Metric 4 — CI · invoice id parked OPERATOR_REVIEW (out of scope this gate)

The CI · invoice id BC (panelRunUid `5555752f-5209-4d81-986d-89f06808563e`) remains parked, per the operator's handoff that explicitly excluded it from this session. Resolution path (per publication-confirm closeout §10.2 + prior analysis): author a new identifier-class characteristic (e.g. `business document number` or `document identifier`) via F4-v2 + B10b publish, then re-submit the CI · invoice id BC + B10 publish. Reading the `5555752f` panel_output_record before deciding would confirm whether the panel's parking was a similar non-deterministic Moderator output bug or a substantive vocabulary-mismatch concern.

### 9.2 Metrics 3 + 6 — Step-4-bis (out of scope)

Per Option B + pre-execution plan §5.5, Metrics 3 (Unbilled revenue — needs `recognized amount` + `billed amount` chars) and 6 (Recognized revenue per fiscal_period — needs `invoice amount` char + D365 `posting_date_field` runtime prerequisite) are deferred to a separate Step-4-bis enrichment session.

### 9.3 Follow-up — Moderator output-schema bug

The Moderator's prompt emitted `f3_operation: "createCharacteristic"` in the original parked run, but the orchestrator validator expects `"registerCharacteristic"` for the characteristic operation. This is a panel-prompt engineering issue (not a substrate bug). Recommended follow-up:
- File against the bc-ai panel-prompt repo / owner: tighten the Moderator's prompt to explicitly emit `registerCharacteristic` for `subjectKind: characteristic` paths.
- Until fixed, F4-v2 createCharacteristic candidates may stochastically park on this issue; operators reading `panel_output_record` will see the same review_reason and can re-submit if the panel substantively approved.

This session did NOT patch panel-prompt code (out of scope).

---

## 10. BCF v1 packet sufficiency observations

| Hard trigger | Status this session |
|---|---|
| T-H1 — cross-entity disambiguation load-bearing | NOT TRIGGERED. CI · posted amount BC's target entity was operator-supplied (Customer Invoice). |
| T-H2 — source-reality grounding PE-MC-1-mandatory for a class | NOT TRIGGERED. Candidate evidence operator-supplied per request body. |
| T-H3 — active characteristic vocabulary wire-size threshold | NOT TRIGGERED. Vocabulary grew 27 → 28 active. |
| T-H4 — bc-ai acquires free Registry query path | NOT TRIGGERED. L1 lock preserved. |

**Verdict: BCF v1 packet remains sufficient. No B6-v2 retrofit opens.**

Soft observation: a positive validation of the v1 panel discipline — the orchestrator validator correctly refused a malformed Moderator recommendation, even when the substantive content was sound. Operator-review is the correct surface to read the panel evidence and decide whether to re-submit. The B6 D2 design (panel-only emit panel_output_record on non-APPROVE; no rejection-log row) works as intended.

---

## 11. Recommended next step

### 11.1 Now MCF-bindable: 7 representative metrics

When MCF Gates M2+ open (separate operator-authorized sessions under Database Change Protocol), the MCF Metric Authoring Panel can begin work on the 7 unblocked metrics:
1. Metric 1 — Total open receivables (Class 1: simple aggregation)
2. Metric 2 — Overdue AR % (Class 2: ratio)
3. Metric 5 — Avg days late, 30-day window (Class 5: windowed)
4. Metric 7 — AR aging buckets (Class 7: bucket-assign)
5. Metric 8 — Discount-to-line-amount (Class 8: cross-coherence positive)
6. Metric 9 — MLS-14 self-collapse (Class 9: deliberate failure)
7. Metric 10 — Stale fixture (Class 10: deliberate failure)

AST node coverage exercised by this 7-metric set: variable_ref + literal + aggregate + arithmetic + window + bucket_assign + the failure-case AST mechanics. Missing only `time_anchor_resolution` (Metric 6, Step-4-bis).

### 11.2 Single remaining BCF gap before full Step 4 (8 of 10)

CI · invoice id BC. When the operator opens that focused gate (analogous to this `posted amount` gate), the same pattern applies:
1. Read `panel_output_record` for panelRunUid `5555752f`.
2. Decide A (re-submit with same payload — if panel approved on substance), B (author new identifier-class characteristic first), or C (reject).
3. Execute through bc-core BCF endpoints.

### 11.3 Step-4-bis for Metrics 3 + 6

Separate enrichment session. Pre-execution plan §5.5 anticipated this — operator decides whether to revisit F4-S1 §6 deferral for `recognized amount` / `billed amount` / `invoice amount`, or compose them differently, or pivot to Option A's deferral-reversal path.

### 11.4 What stays closed

- **MCF M3** — closed.
- **MCF M2 DDL apply** — closed (separate session under Database Change Protocol).
- **B6-v2 retrofit** — closed (no trigger fired).
- **MC creation** — closed (MCF gates not opened).
- **bc-postgres write access** — closed (`allow_write: false`).

---

## Document verification

- **All 10 required sections present** (§1 Scope and grounding; §2 Prior closeouts consumed; §3 Parked-item evidence; §4 Semantic decision; §5 Operator-confirm / publication actions; §6 CI · posted amount BC result; §7 Live post-action verification; §8 Metric unblock arithmetic; §9 Remaining blockers; §10 BCF v1 packet sufficiency; §11 Recommended next step).
- **Parked-item evidence read directly** (§3) — verdict_code, review_reason, all three agent outputs (Maker / Checker / Moderator), classification, checklist answers all surfaced.
- **Semantic decision justified against three options** (§4) — Option A chosen with rationale; B + C rejected with reasons.
- **No retry-coaxing** — re-submission used identical semantic payload (proposedName / definition / candidateEvidence) with new candidateRef; the discipline rule was honoured (§4.4).
- **Discipline assertions hold** (§1.2) — no direct SQL writes, allow_write unchanged, operator-confirm not bypassed, CI · invoice id not revisited.
- **Substrate state quantified** (§7) — 2 active entities + 9 active BCs + 28 active characteristics + 0 draft + 0 supersessions + 0 aliases + 0 supersession_proposals.
- **Metric arithmetic explicit** (§8) — 7 unblocked + 1 blocked (invoice id, out of scope) + 2 Step-4-bis = 10.
- **No code changes, no DDL, no DB writes outside the BCF endpoint path.** Doc-only commit.
