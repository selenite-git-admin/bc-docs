---
title: BCF × OAGIS Pass-1 Retrofit Batch 1 v2 Pilot — Closure Checkpoint (2026-06-25)
description: Closeout of the operator-approved one-row Checker-First Preflight v2 pilot for shelf_life_duration. Single panel call APPROVE_FOR_DRAFT; C5 high-risk operator-confirm POST; one draft characteristic authored (lifecycle_state='draft'). v2 8-Q + admission-scope appendix doctrine validated empirically — first retrofit batch 1 substrate write under the revised rubric. Captures operator calibration note "rep-term suffix can be acceptable when it encodes primitive shape and prevents a worse map."
status: closeout_complete
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-retrofit-batch-1-v2-pilot-closure
related_docs:
  - bcf-oagis-pass-1-retrofit-batch-1-failure-closeout-2026-06-25.md
  - bcf-oagis-pass-1-retrofit-checker-first-preflight-v2-doctrine-2026-06-25.md
  - bcf-oagis-pass-1-retrofit-scoping-ledger-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
---

# BCF × OAGIS Pass-1 Retrofit Batch 1 v2 Pilot — Closure Checkpoint

> One row. One panel call. One C5 confirm. One draft characteristic. v2 doctrine empirically validated by the live panel — the same row that parked OPERATOR_REVIEW under v1 (Session 11) now lands at draft under v2 (Session 13). The defect was operational (invented industry enum); v2 fixed it (closed-enum cross_function with function-by-function evidence).

> Companion failure closeout `bcf-oagis-pass-1-retrofit-batch-1-failure-closeout-2026-06-25.md` (PR #67) documents what went wrong. This document closes the v2 pilot recovery.

## 1. Pilot outcome

| Step | Result |
|---|---|
| Panel | HTTP 200, 136.1 s, `kind='awaiting_operator_confirm'`, `panel_run_uid='c008c8a0-bb20-4f55-8743-3522bee47349'` |
| C5 high-risk operator-confirm | HTTP 200, `kind='authored'`, characteristic written at draft |
| Substrate write | 1 draft characteristic, `characteristic_id='d4c554ce-bfd5-44a5-905e-d8666c890614'`, `certification_record_id='828f7e70-0295-46bb-af9c-e6a6a8f3fb95'`, `lifecycle_state='draft'`, `created_at='2026-06-25T09:31:44.442Z'`, `created_by='bcf-registry-authoring-panel'` |
| Halt triggered? | No |
| Pass-1 cap consumed | 1 / 270 (cumulative 81 / 270 = 30.0%) |

**Verbatim flow:**

1. Panel: `POST /api/bcf/registry-authoring-runs` operation=createCharacteristic; response `{kind: 'awaiting_operator_confirm', panelRunUid: 'c008c8a0-...', subjectKind: 'characteristic', actionCode: 'registry_author_vocabulary', governingPolicyUid: 'bcf-registry-scope1', policyVersion: 'v1'}`. No substrate write yet — the C5 high-risk gate held the cert mint pending operator confirm per `RegistryAuthoringOrchestrator.completeHighRiskConfirm` flow at `bc-core/src/registry/registry-authoring-panel/registry-shape-certification-confirm.controller.ts:38`.

2. C5 confirm: `POST /api/bcf/registry-shape-certifications/confirm` body `{panelRunUid, subjectKind: 'characteristic', actionCode: 'registry_author_vocabulary', rationale: 480-char operator-supplied}`. Response `{kind: 'authored', authoredSubject: 'characteristic', certificationRecordId: '828f7e70-...', characteristicId: 'd4c554ce-...'}`.

3. Substrate verification (live `GET /api/bcf/registry/characteristics?lifecycleState=draft`): 21 draft characteristics (was 20). `shelf life duration` present at `lifecycle_state='draft'`.

## 2. Substrate state delta

| Metric | Before pilot | After pilot |
|---|---:|---:|
| Active characteristics | 62 | 62 |
| Draft characteristics | 20 | **21** (+1: `shelf life duration`) |
| Active entities | 29 | 29 |
| Active value BCs | 194 | 194 |
| Certification records (BCF) | (n) | (n+1) |
| Panel-output-records (BCF) | (n) | (n+1) |
| Pass-1 panel cap consumed | 80 / 270 | 81 / 270 |

Single draft write — exactly what the operator pilot contract specified ("If approve, confirm/write one draft characteristic only").

## 3. Authored content (verbatim)

| Field | Value |
|---|---|
| operation | `createCharacteristic` |
| proposedName | `shelf life duration` (Path A, retained per operator approval 2026-06-25) |
| shape_tuple | `text\|string\|descriptor` |
| candidateEvidence.sourceLabel | OAGIS Standard 10.12 — `item-master.item-master.shelf-life-duration` + ISO 22000:2018 food safety + FDA 21 CFR 117 preventive controls + EU 1169/2011 food information + Codex Alimentarius CAC/GL 50 + ASTM F1980 medical device shelf life |
| admission_scope (declared) | `cross_function` |
| business_function (cross_function declaration) | `null` (function-by-function evidence carried in candidateEvidence.citedText) |
| industry | `null` (NOT industry_scoped — that was the row-5 v1 trap) |

Definition body (M8-clean, verbatim sent):

> "A master-data attribute specifying how long a product remains usable, safe, or saleable under stated storage conditions before degradation, expiry, or regulatory ineligibility takes effect. Held in product / item master data as a property of the product line, not the per-batch instance. Distinguishes the design intent / regulatory-allowed window (this characteristic) from the per-instance expiry date (a separate active substrate characteristic carrying the calendar date when a specific batch goes off). Used by inventory turnover analysis, batch traceability, regulatory compliance reporting, and customer-facing date marking on consumer products. Typically expressed as an ISO 8601 period string (e.g., 'P24M' for twenty-four months) or as a free-text time-span statement. Excludes lead time (the procurement-to-receipt interval, an active substrate characteristic with operationally distinct semantics)."

Verification: token `duration` does not appear in the body. Token `shelf life` does not appear. Concept described operationally (storage conditions, degradation, expiry, ineligibility); substrate adjacents (`expiry date`, `lead time`) named for explicit disambiguation. Q-G M8 PASS confirmed at panel evaluation.

## 4. v2 doctrine empirical validation

Same row, same OAGIS source path, same target entity (Item), different rubric:

| Outcome | v1 (Session 11) | v2 (Session 13) |
|---|---|---|
| Panel verdict | OPERATOR_REVIEW (parked) | APPROVE_FOR_DRAFT (proceeded to C5 confirm gate) |
| Defect cited by live Checker | invented industry-enum value `'regulated_perishables'` | none |
| Substrate write | 0 | **1 draft** |
| Panel calls consumed | 1 (wasted) | 1 (productive) |

**Net read:** v2 fixed the operational defect. The Checker accepted everything else under v1 already (meaning well-grounded, term not a synonym, M9 not triggered). The only difference between v1 and v2 was the admission-scope appendix: v1 declared `industry_scoped` with invented value; v2 declared `cross_function` with closed-enum 4-function evidence.

## 5. C5 operator-confirm flow — observation

This was the first Session-11-onward characteristic admission to traverse the C5 high-risk operator-confirm gate. The orchestrator returned `kind='awaiting_operator_confirm'` rather than `kind='authored'` directly. Per the C1 v2 closeout (`bcf-oagis-pass-1-c1-v2-closeout-2026-06-24.md` §F4-v2 S2b post-confirm semantics), this is the expected behaviour when the panel APPROVES but registry policy categorises the operation as high-risk.

Operator rationale supplied at confirm (480 chars, well above the 40-char minimum per `MIN_OPERATOR_CONFIRM_RATIONALE_CHARS`):

> "Operator-approved v2 pilot per pilot contract 2026-06-25 — Path A retained, M8-clean definition, cross_function with 4-function evidence (production / inventory / quality / sales) from closed enum. Shelf-life duration is regulatory-standard vocabulary (ISO 22000, FDA 21 CFR 117, EU 1169/2011, Codex CAC/GL 50, ASTM F1980); Q-F rep-term suffix tolerated per operator calibration note that rep-term suffix can be acceptable when it encodes primitive shape and prevents a worse map."

The rationale records the Q-F operator framing in the substrate audit trail itself.

## 6. Calibration note — Q-F rep-term suffix rule refinement

Per operator framing 2026-06-25 (preserved as substrate-audit-trail rationale and amended into v2 doctrine):

> **"Rep-term suffix can be acceptable when it encodes primitive shape and prevents a worse map."**

Worked example for `shelf life duration`:
- The token `duration` is on the v2 doctrine §Q-F closed list of representation-term words.
- Strict v2 reading would soft-fail Q-F and recommend DOWNGRADE to `shelf life`.
- BUT: `duration` here is doing real shape work — it separates the relative time-span attribute (this characteristic) from `expiry date` (active substrate, point-in-time / date shape).
- Dropping `duration` to satisfy Q-F strictly would push ambiguity into BC binding, requiring role-qualifier disambiguation downstream.
- The live Checker corroborates: row 5 in Session 11 was the only row where Checker explicitly said "the characteristic meaning is well-grounded and the term is not a synonym of the active governed vocabulary" — Q-F-equivalent concerns were NOT raised.

**Doctrine refinement:** Q-F's soft-fail applies when the rep-term word is decorative (no shape-distinguishing function). When the rep-term word is load-bearing — i.e., it encodes primitive shape (duration vs date vs descriptor) AND its removal would create downstream ambiguity at BC binding — the soft-fail is tolerated.

This refinement is **calibration-driven**, not pre-doctrinal. v2 doctrine §Q-F should be amended to add this Q-F load-bearing exception in a future doctrine update (deferred to next operator-decision packet).

## 7. Halt triggers — none fired

Per pilot contract halt conditions:

| Trigger | Fired? |
|---|---|
| OPERATOR_REVIEW (park) | No — APPROVE_FOR_DRAFT received |
| service_error (HTTP 0/5xx) | No — HTTP 200 on both calls |
| shared_rejection_pattern_mid_flight (v2 harness mid-flight check) | Not applicable — single packet |
| auth_error | No |
| panel_not_found | No |
| not_issued | No |

v2 harness mid-flight halt machinery was not exercised by this pilot (single packet), but the harness remains primed for future multi-row batches.

## 8. Authority + verification trail

- **Program authorization:** DEC-f94895 — unchanged. Pass-1 panel cap consumed 1 / 270 = 0.37%; cumulative 81 / 270 = 30.0%.
- **Doctrine authorization:** `bc-docs-v3/docs/implementation/bcf-oagis-pass-1-retrofit-checker-first-preflight-v2-doctrine-2026-06-25.md` (PR #67).
- **Worksheet:** `barecount-devhub/.claude/bcf-pass-1-retrofit-batch-1-v2-pilot-shelf-life-checker-first-worksheet-2026-06-25.md` (Session 12, gitignored per prior practice).
- **Transport script:** `barecount-devhub/scripts/_pass1-retrofit-batch-1-transport-v2.mjs` (v2 harness, PR #11). PACKETS array populated inline at run-time with the pilot row, then reverted to empty fail-safe post-run to preserve PR #11 audit chain.
- **Outcomes JSONL:** `barecount-devhub/.claude/pass1-retrofit-batch-1-v2-outcomes-2026-06-25.jsonl` (2 records — panel + C5 confirm).
- **Outcomes summary:** `barecount-devhub/.claude/pass1-retrofit-batch-1-v2-summary-2026-06-25.json`.
- **Pre-transport substrate-collision check** (live `GET /api/bcf/registry/characteristics?lifecycleState=active|draft` paged): 0 matches for `shelf life duration` in both active and draft, confirmed at session 12 and session 13 starts.
- **Post-pilot substrate verification** (live `GET /api/bcf/registry/characteristics?limit=200&lifecycleState=draft`): 21 draft characteristics, `shelf life duration` resolved by id `d4c554ce-...` to `lifecycle_state='draft'`.

## 9. Self-audit (D268)

| Rule | Honoured? |
|---|---|
| One-then-many | **Honoured.** Single-row pilot under operator-approved contract; the v2 doctrine's first substrate write was the smallest possible test of the rubric. |
| Independent verification | Honoured. Substrate state queried live post-transport via API; Q-F load-bearing rationale recorded in C5 confirm rationale at the substrate-audit layer. |
| No bulk substrate writes | Honoured trivially. 1 write. |
| Cosmetic status changes avoided | Honoured. |
| Self-audit at session close | This document. |
| If a shortcut tempts, stop and flag it | The temptation to "skip the C5 confirm rationale and just send 40 chars of boilerplate" was rejected — full 480-char operator-supplied rationale recorded the Q-F framing into substrate audit. |
| No lower-layer compensation | Honoured. v2 doctrine is the upper-layer fix; pilot validates it without compensating at lower layers. |

## 10. Pass-1 retrofit batch 1 cumulative tally

| Session | Action | Outcome | Substrate writes | Panel calls |
|---|---|---|---:|---:|
| Session 10 | v1 worksheet (5 rows) | 5/5 SURVIVE locally | 0 | 0 |
| Session 11 | v1 transport (5 rows) | 5/5 OPERATOR_REVIEW parks | **0** | 5 |
| Session 12 | v2 pilot worksheet (1 row) | SURVIVE | 0 | 0 |
| Session 13 | v2 pilot transport (1 row) | APPROVE_FOR_DRAFT + C5 confirm | **+1 draft** | 1 |
| **Total** | | | **+1 draft** | **6** |

Net: 6 panel calls + 1 C5 confirm consumed → 1 draft characteristic written. The v1 5-panel waste is documented as calibration evidence; v2 1-panel success validates the rubric. Calibration-driven progress.

## 11. Held — next gate

`shelf life duration` is at lifecycle_state='draft'. Per Pass-1 discipline, draft→active transition is a separate operator gate (the same pattern as C1 v2 / C5 confirms in prior sessions). This pilot session does NOT bundle that transition.

**Next gate options** (held pending operator framing):

1. **Activate the `shelf life duration` draft** — separate session, separate operator-gated draft→active confirm. The active state would make the characteristic available for Pass-3 BC binding immediately.

2. **Reauthor the other 4 retrofit batch 1 rows under v2** — `product name`, `brand name`, `serial number specification description`, `lot number specification`. Per operator framing, these need genuine re-authoring (not transliteration). v2 Q-F + Q-H rigor applies. Author worksheets one-at-a-time or in a small batch under v2 doctrine.

3. **Continue Pass-1 retrofit Batch 2** — pick from the scoping ledger §6.4 proposed waves (MO duration triplet, MO planner/supervisor, amount-family, etc.). Apply v2 doctrine.

4. **Pivot to E3** — master-data 8 AMBER entities. Equipment held; batch-1 partially validated; E3 is independent.

5. **Amend v2 doctrine with Q-F load-bearing exception** — formalise §6's calibration note into v2 doctrine §Q-F refinement, with explicit `duration / amount / quantity / measure / period` exception when the rep-term word encodes primitive shape and prevents downstream BC-binding ambiguity.

## 12. Scope locks honoured this session

- 1 panel call (operator-approved pilot of exactly 1).
- 1 C5 confirm (path required it per `awaiting_operator_confirm` orchestrator response).
- 1 substrate write (draft characteristic — exactly one).
- 0 retry attempts.
- 0 other rows transported.
- 0 active-state transitions (draft → active is a separate gate per operator framing).
- 0 DDL changes.
- 0 ADR authoring.
- 0 amendments to v2 doctrine (PR #67 stands; this closeout records the Q-F refinement as proposed for future amendment).
- 0 amendments to PR #62 (Pass-2 entity doctrine).
- 0 changes to BC-coverage ledger.
- 0 changes to A0.5 catalogue.
- 0 amendments to active entities or other characteristics.

Held.
