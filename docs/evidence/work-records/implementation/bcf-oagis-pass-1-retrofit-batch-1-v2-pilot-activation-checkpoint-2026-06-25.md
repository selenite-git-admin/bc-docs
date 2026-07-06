---
title: BCF × OAGIS Pass-1 Retrofit Batch 1 v2 Pilot Activation — Closure Checkpoint (2026-06-25)
description: B10b two-phase activation of the shelf_life_duration draft characteristic (authored Session 13) to lifecycle_state='active'. semanticFinalityAffirmed=true honoured per ADR DEC-26b6e2 immutable-atom commitment. No edits to term or definition. Single characteristic transitioned; no batch. v2 doctrine empirical validation arc complete — same row that parked OPERATOR_REVIEW under v1 (Session 11) is now active substrate, available for Pass-3 BC binding.
status: closeout_complete
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-retrofit-batch-1-v2-pilot-activation
related_docs:
  - bcf-oagis-pass-1-retrofit-batch-1-failure-closeout-2026-06-25.md
  - bcf-oagis-pass-1-retrofit-checker-first-preflight-v2-doctrine-2026-06-25.md
  - bcf-oagis-pass-1-retrofit-batch-1-v2-pilot-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-1-retrofit-scoping-ledger-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
  - DEC-26b6e2
---

# BCF × OAGIS Pass-1 Retrofit Batch 1 v2 Pilot Activation — Closure Checkpoint

> One characteristic. Two B10b API calls. One active substrate characteristic. v2 doctrine empirical validation arc complete: the row that parked OPERATOR_REVIEW under v1 (Session 11) and was authored at draft under v2 (Session 13) is now `lifecycle_state='active'` (Session 14), available for Pass-3 BC binding.

> Companion docs: failure closeout PR #67 (v1 + doctrine), pilot closure-checkpoint PR #68 (v2 admission).

## 1. Activation outcome

| Step | Result |
|---|---|
| B10b Phase 1 — request | HTTP 200, 88 ms, `kind='awaiting_operator_confirm'`, `actionCode='registry_transition'`, `governingPolicyUid='bcf-registry-scope1'`, `policyVersion='v1'`, `panelRunUid='c008c8a0-bb20-4f55-8743-3522bee47349'` (re-resolved server-side from registryId) |
| B10b Phase 2 — confirm | HTTP 200, 60 ms, `kind='published'`, `lifecycleState='active'`, new `certificationRecordId='f5a2c970-e20b-431a-9308-b6c772ba57ef'` |
| Substrate verification | `GET /api/bcf/registry/characteristics?lifecycleState=active`: 63 active characteristics; `shelf life duration` (id `d4c554ce-bfd5-44a5-905e-d8666c890614`) present with `lifecycleState='active'` |
| `semanticFinalityAffirmed` | `true` (operator-affirmed; ADR DEC-26b6e2 immutable-atom commitment recorded into substrate audit) |
| Edits to term or definition | None (ADR DEC-26b6e2 honoured) |
| Halt triggered? | No |
| Pass-1 panel cap consumed | 0 (publication is not a panel call) |
| Total wall time | 148 ms across both phases |

## 2. Substrate delta

| Metric | Before activation | After activation |
|---|---:|---:|
| Active characteristics | 62 | **63** (+1: `shelf life duration`) |
| Draft characteristics | 21 | **20** (-1: `shelf life duration` transitioned out of draft) |
| Active entities | 29 | 29 |
| Active value BCs | 194 | 194 |
| Certification records (BCF) | (n) | (n+1) (publication cert `f5a2c970-…`) |
| Panel calls consumed | 81 / 270 | 81 / 270 (unchanged) |

**Single net write**: lifecycle_state transition `draft → active` on one characteristic, plus one publication certification record. ADR DEC-26b6e2 immutable-atom freeze: `(term, definition)` pair is now substrate-fixed.

## 3. Authored content — substrate-frozen at activation

Per ADR DEC-26b6e2, publication freezes the `(term, definition)` pair. The substrate now carries:

| Field | Value (frozen) |
|---|---|
| characteristic_id | `d4c554ce-bfd5-44a5-905e-d8666c890614` |
| canonical_term | `shelf life duration` |
| shape_tuple | `text\|string\|descriptor` |
| lifecycle_state | `active` |
| definition | (M8-clean v2 body — full text in `bcf-oagis-pass-1-retrofit-batch-1-v2-pilot-closure-checkpoint-2026-06-25.md` §3; verbatim from C5 confirm; not amended) |
| admission_scope | `cross_function` |
| created_at | `2026-06-25T09:31:44.442Z` (draft mint) |
| activated_at | `2026-06-25T09:55:10` (B10b confirm) |

Editorial-amendment path: if the definition later needs broadening, the `(registry_amend_definition, characteristic)` cert pairing per the in-place amendment endpoint (`POST /api/bcf/registry/characteristics/:id/amend-definition`) is the governed surface. The term remains frozen.

## 4. Operator rationale — preserved in substrate audit trail

The 844-character operator rationale supplied at Phase 2 confirm is recorded in the publication certification record `f5a2c970-…`. Verbatim:

> "Operator-approved B10b activation per pilot contract 2026-06-25 — shelf life duration draft (authored via v2 doctrine Session 13, panel_run_uid c008c8a0-bb20-4f55-8743-3522bee47349) promoted to active with semanticFinalityAffirmed=true. Term and definition NOT edited; ADR DEC-26b6e2 immutable-atom commitment honoured. Q-F rep-term suffix load-bearing exception preserved per Session 13 C5 confirm rationale: duration token here separates the relative time-span attribute from expiry date (point-in-time substrate adjacent), preventing downstream BC binding ambiguity. cross_function admission scope locked with 4-function evidence (production / inventory / quality / sales) from closed enum. Activation completes the v2 doctrine empirical validation arc: same row that parked OPERATOR_REVIEW under v1 Session 11 now active under v2 substrate."

The rationale spans both the Q-F load-bearing exception calibration note (preserved from Session 13's C5 confirm — now persisted at two cert-record sites in substrate audit) and the v1→v2 arc completion record.

## 5. v2 doctrine empirical validation arc — complete

Single-row admission→draft→active progression:

| Session | Action | Outcome | Substrate write |
|---|---|---|---|
| 10 | v1 worksheet (5 rows) | 5/5 SURVIVE locally | 0 |
| 11 | v1 transport (5 rows) | 5/5 OPERATOR_REVIEW | 0 |
| 12 | v2 pilot worksheet (1 row) | SURVIVE | 0 |
| 13 | v2 pilot transport (1 row) | APPROVE_FOR_DRAFT → C5 confirm | +1 draft |
| 14 | B10b activation (1 row) | published | +1 active (-1 draft) |
| **Net** | | | **+1 active characteristic** |

The arc validates the v2 doctrine three ways:
1. **Authoring**: v2 8-Q + admission-scope appendix produced a packet that the live panel accepted (Session 13 panel APPROVE).
2. **Persistence**: substrate accepted the draft write at admission and the lifecycle transition at activation.
3. **Calibration**: the operator's Q-F load-bearing exception is now persisted into substrate audit at two sites (C5 confirm cert + B10b confirm cert), available for future operator review when authoring rules similar terms.

The v1 5-panel waste is documented as calibration evidence; v2 1-panel + 1-confirm + 1-activation success validates the rubric end-to-end.

## 6. Pass-3 BC binding readiness

`shelf life duration` is now bindable as an active characteristic in Pass-3 BC authoring. The expected immediate BC targets per Pass-2 entry note §4 and the scoping ledger §6.2 (PR #66):

- **Item entity** (`1cd57c89-9102-4459-9374-b7dae801a41f`, active per E1 / Session 6) — natural primary binding for `shelf life duration` as a master-data attribute on product / item master.
- 2 BC targets per the scoping ledger projection (target_slices=asset-maintenance-simple + master-data-root; primary binding to master-data-root via Item).

**Next gate after this checkpoint:** operator chooses the first BC binding/retrofit that consumes the new active characteristic. The scoping ledger §6.2 named `shelf life duration` as one of the 5 first-batch BC-binding candidates; the first BC binding work can re-route the binding through the Item entity directly now that the characteristic is active.

## 7. Halt triggers — none fired

| Trigger (per operator pilot contract) | Fired? |
|---|---|
| publication confirm failure | No (HTTP 200, kind='published') |
| not_publishable return | No (kind='published') |
| Phase 1 unexpected kind | No (got expected awaiting_operator_confirm) |
| Phase 2 unexpected kind | No (got expected published) |
| Verification mismatch | No (substrate confirms lifecycle_state='active') |
| auth_error / service_error | No |

## 8. Authority + verification trail

- **Pilot contract authority:** operator 2026-06-25 — "Activate only shelf life duration. No batch activation. Use B10b publication path with semanticFinalityAffirmed=true. No edits to term/definition. If publication confirm fails or returns not_publishable, halt. Verify lifecycle_state='active'. Then decide the first BC binding/retrofit that consumes it."
- **Doctrine authority:** ADR DEC-26b6e2 (characteristic immutable-atom freeze at publication); v2 doctrine `bcf-oagis-pass-1-retrofit-checker-first-preflight-v2-doctrine-2026-06-25.md` (PR #67); pilot closure-checkpoint `bcf-oagis-pass-1-retrofit-batch-1-v2-pilot-closure-checkpoint-2026-06-25.md` (PR #68).
- **Script:** `barecount-devhub/scripts/_pass1-retrofit-batch-1-v2-pilot-activate.mjs` — two-phase B10b activation harness with hard-halt on any non-happy-path outcome.
- **Outcomes JSONL:** `barecount-devhub/.claude/pass1-retrofit-batch-1-v2-pilot-activate-outcomes-2026-06-25.jsonl` (3 records: phase1 request + phase2 confirm + substrate verify).
- **Outcomes summary:** `barecount-devhub/.claude/pass1-retrofit-batch-1-v2-pilot-activate-summary-2026-06-25.json` — `final_status='published'`, `halt_class=null`.
- **Pre-activation substrate state** (live `GET /api/bcf/registry/characteristics?lifecycleState=active|draft`): 62 active + 21 draft; `shelf life duration` present at draft.
- **Post-activation substrate state** (live `GET /api/bcf/registry/characteristics?lifecycleState=active`): 63 active; `shelf life duration` present with `lifecycleState='active'`.

## 9. Self-audit (D268)

| Rule | Honoured? |
|---|---|
| One-then-many | Honoured. Single-row activation; no batch. |
| Independent verification | Honoured. Substrate state queried live post-activation via GET endpoint; activation cert id and characteristic id matched against Phase 2 response. |
| No bulk substrate writes | Honoured. 1 lifecycle transition + 1 cert. |
| Cosmetic status changes avoided | Honoured. lifecycle_state='active' is the substantive transition, not a cosmetic flip. |
| Self-audit at session close | This document. |
| If a shortcut tempts, stop and flag it | The temptation to "skip the verification GET and trust Phase 2's response" was rejected; substrate verified independently from a separate endpoint. |
| No lower-layer compensation | Honoured. ADR DEC-26b6e2 immutable-atom freeze respected — no in-place term/definition edits. |
| Operator pilot contract scope-locked | Honoured precisely: activation only, no batch, no edits, semanticFinalityAffirmed=true, halt on any non-happy-path. |

## 10. Scope locks honoured this session

- 0 panel calls (publication is not a panel call).
- 1 lifecycle transition (draft → active for one characteristic).
- 1 publication cert (B10b confirm).
- 0 edits to term or definition.
- 0 other characteristics or entities transitioned.
- 0 BC binding decisions (operator deferred to next session).
- 0 v2 doctrine amendments (operator deferred until after activation, then "the audit rationale already preserves the calibration, and activation gets us closer to actual coverage").
- 0 DDL changes.
- 0 ADR authoring.
- 0 changes to BC-coverage ledger.
- 0 changes to A0.5 catalogue.
- 0 amendments to PR #62 / #65 / #67 / #68.

## 11. Held — next gate

Per operator pilot contract: "Then decide the first BC binding/retrofit that consumes it."

`shelf life duration` is now active substrate, available for Pass-3 BC binding. Five operator-decision options (held):

1. **First BC binding for `shelf life duration`** — author the BC that binds the new characteristic on the Item entity. Smallest possible Pass-3 step; turns activation into actual BC coverage.
2. **Reauthor the other 4 retrofit batch 1 rows under v2** — product_name / brand_name / serial_number_specification_description / lot_number_specification with substantive BareCount business vocabulary (not transliterations).
3. **Continue Pass-1 retrofit Batch 2** — pick from scoping ledger §6.4 (MO duration triplet, etc.).
4. **Pivot to E3** — master-data 8 AMBER entities.
5. **Amend v2 doctrine with Q-F load-bearing exception** — formalise the calibration note into doctrine §Q-F.

All held pending operator authorisation.

Held.
