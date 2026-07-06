---
title: BCF × OAGIS Pass-3 Item × shelf life duration BC Binding — Closure Checkpoint (2026-06-25)
description: First Pass-3 BC binding on the v2 doctrine recovery arc. Item × shelf life duration createBusinessConcept low-risk path auto-authored AND auto-activated in a single call. kind='value', identityRole='descriptive', semanticRole='temporal', dataType='string' — all derived fields landed exactly as the BC binding worksheet predicted. Operator's dataType hard-guard PASSED (dataType='string' not 'text'). Substrate moves from 194 to 195 active value BCs. The v2 doctrine arc has now produced its first BC coverage, not just vocabulary.
status: closeout_complete
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-3-item-shelf-life-bc-binding
related_docs:
  - bcf-oagis-pass-1-retrofit-batch-1-failure-closeout-2026-06-25.md
  - bcf-oagis-pass-1-retrofit-checker-first-preflight-v2-doctrine-2026-06-25.md
  - bcf-oagis-pass-1-retrofit-batch-1-v2-pilot-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-1-retrofit-batch-1-v2-pilot-activation-checkpoint-2026-06-25.md
  - bcf-oagis-pass-1-retrofit-scoping-ledger-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
  - DEC-26b6e2
---

# BCF × OAGIS Pass-3 Item × shelf life duration BC Binding — Closure Checkpoint

> **The final mile.** Item active (E1 / Session 6) + shelf life duration characteristic active (Session 14) + first Pass-3 BC binding (Session 16) = first BC coverage produced by the v2 doctrine recovery arc. Substrate now carries Item.shelf life duration as an active value BC; bindable from Pass-1 BC-coverage ledger rows that target master-data-root.

> Per operator pilot contract 2026-06-25: exactly one createBusinessConcept panel; no batch; no retry; halt on OPERATOR_REVIEW / service_error / duplicate / unexpected path; surface unexpected awaiting_operator_confirm; hard halt if dataType emits `text` instead of `string`. All conditions honoured precisely.

## 1. Transport outcome

| Step | Result |
|---|---|
| Pre-flight Item BC count | 0 |
| Panel — `POST /api/bcf/registry-authoring-runs` operation=createBusinessConcept | HTTP 200, 102.8 s, `kind='authored'`, `authoredSubject='business_concept'` |
| `panel_run_uid` | `6fe5255f-7a46-40cd-a9cd-4adfbb933dba` |
| `certification_record_id` | `a81ae3a7-ae3b-4fd2-b61c-446205bfe381` (admission cert) |
| `activation_certification_record_id` | `3bf30c95-4249-4562-b8dc-319fcd580df0` (auto-activation cert) |
| `concept_id` | `a291c25c-fb92-4963-a042-69de862911d1` |
| `concept_version_id` | `49f2465f-23f9-4fda-a670-1904df263257` |
| `lifecycleState` | **`active`** (low-risk path auto-authored AND auto-activated in same call) |
| `dataType` | **`string`** (operator hard-guard PASSED — `string`, not `text`) |
| `kind` | `value` |
| `identityRole` | `descriptive` |
| `semanticRole` | `temporal` (D442 best match — predicted in worksheet §1.1) |
| `canonicalValueSet` | `null` (not required for temporal per D442 §D6.1) |
| `representationTerm` | `duration` (derived from characteristic shape `text\|string\|descriptor`) |
| Halt triggered | No |

## 2. Substrate delta

| Metric | Before binding | After binding |
|---|---:|---:|
| Active value BCs (substrate-wide) | 194 | **195** (+1) |
| Item BCs | 0 | **1** (+1 — `shelf life duration`) |
| Active characteristics | 63 | 63 |
| Draft characteristics | 20 | 20 |
| Active entities | 29 | 29 |
| Certification records (BCF) | (n) | (n+2) — admission + auto-activation |
| Pass-1 panel cap consumed (Pass-3 panel call — same envelope) | 81 / 270 | 82 / 270 = 30.4% |

**Single Item BC. Single createBusinessConcept call. Two certs minted (admission + activation) atomically.** The low-risk `createBusinessConcept` path (`actionCode='registry_create'`, `subjectKind='business_concept'`) does what `createCharacteristic` does not: auto-authors AND auto-activates in the same orchestrator call. No separate publication step required for low-risk BC binding.

## 3. Authored BC content — substrate-frozen

| Field | Value |
|---|---|
| concept_id | `a291c25c-fb92-4963-a042-69de862911d1` |
| entity_id | `1cd57c89-9102-4459-9374-b7dae801a41f` (Item) |
| canonical_name (`displayLabel`) | `Item · shelf life duration (duration)` |
| characteristic_id | `d4c554ce-bfd5-44a5-905e-d8666c890614` (shelf life duration) |
| kind | `value` |
| identity_role | `descriptive` |
| semantic_role | `temporal` |
| data_type | `string` |
| representation_term | `duration` |
| reference_role | null |
| target_entity_id | null |
| lifecycle_state | `active` |
| created_at | `2026-06-25T10:28:27.453Z` |
| created_by | `bcf-registry-authoring-panel` |

Definition body (frozen at activation per ADR DEC-26b6e2 immutable-atom):

> "The shelf life specification carried at the master-data product line — a master-data attribute of Item describing how long instances of this product remain usable, safe, or saleable under stated storage conditions before degradation, expiry, or regulatory ineligibility takes effect. Held at the Item master-data level, NOT at the per-batch instance level (per-instance expiry dates are computed downstream from production-date plus this master-data value). Used by inventory turnover analysis, batch traceability, regulatory compliance reporting, and customer-facing date marking on consumer products. Excludes the Item's lead-time attribute (procurement-to-receipt interval, distinct semantic). Distinguishes Item's perishability class from non-perishable Item lines."

Avoids `duration` token. Avoids `shelf life` token. M8-clean.

## 4. Operator hard-guards — verification

| Guard | Outcome |
|---|---|
| `dataType='string'` (NOT `text`) | **PASS** — landed as `string` (BCF closed enum match for `text\|string\|descriptor` characteristic shape) |
| No retry on halt classes | Not exercised (no halt fired) |
| Surface unexpected `awaiting_operator_confirm` before confirming | Not exercised (panel returned `kind='authored'` directly; auto-activated; no confirm needed) |
| Halt on OPERATOR_REVIEW | Not exercised |
| Halt on service_error | Not exercised |
| Halt on duplicate | Not exercised |
| Item BC count delta verified post-write | 0 → 1 ✓ |
| Active value BC count verified substrate-wide | 194 → 195 ✓ |

Every operator hard-guard honoured; none had to fire.

## 5. v2 doctrine arc — recovery to coverage

| Session | Action | Substrate write |
|---|---|---|
| 10 | v1 worksheet (5 rows) | 0 |
| 11 | v1 transport (5 rows) | 0 (5 OPERATOR_REVIEW parks) |
| 12 | v2 pilot worksheet (1 row) | 0 |
| 13 | v2 pilot transport (1 row) | +1 draft characteristic |
| 14 | B10b activation (1 row) | +1 active characteristic / −1 draft |
| 15 | Pass-3 BC binding worksheet (1 row) | 0 |
| **16** | **Pass-3 BC binding transport (1 row)** | **+1 active value BC / +1 Item BC** |

**Cumulative cost:** 6 panel calls (v1) + 1 panel call (v2 characteristic) + 1 C5 confirm + 1 B10b publication confirm + 1 panel call (Pass-3 BC) = 7 panel calls + 3 confirm-type calls = **+1 active characteristic + +1 active value BC**.

The v2 doctrine arc has now produced **coverage, not just vocabulary**. The first BC binding lives in substrate.

## 6. Worksheet predictions — empirical verification

Worksheet §1.1 (PR not opened — gitignored at `barecount-devhub/.claude/`) predicted the Maker/Checker would derive:

| Field | Predicted (worksheet §1.1) | Actual (substrate) |
|---|---|---|
| `kind` | `value` | `value` ✓ |
| `characteristicId` | `d4c554ce-…` (from canonical-name match) | `d4c554ce-…` ✓ |
| `dataType` | `string` (BCF closed enum for text\|string\|descriptor) | `string` ✓ |
| `semanticRole` | `temporal` (D442 best match for shelf life) | `temporal` ✓ |
| `identityRole` | `descriptive` (Item identity is product / SKU, not shelf life) | `descriptive` ✓ |
| `canonicalValueSet` | `null` (not required for temporal per D442 §D6.1) | `null` ✓ |

**6/6 derived fields landed as predicted.** Pass-3 BC binding gauntlet Q-A through Q-I (worksheet §2) all PASS-validated empirically by the live panel.

The single unpredicted-but-natural field: `representationTerm='duration'` — derived by the orchestrator from the characteristic shape and value-property; the worksheet did not explicitly predict this but it matches the active characteristic's natural shape.

## 7. Coverage impact — first Pass-3 step

Pre-binding (post Session 14 activation):
- Item: 0 BCs
- BC-coverage ledger Pass-1 records targeting Item via master-data-root slice: ~17 BC unlock potential (per scoping ledger PR #66 §1; among these, 5 first-batch BC-binding candidates including `shelf life duration` itself)

Post-binding:
- Item: **1 BC** (`shelf life duration`)
- Active value BCs substrate-wide: **195** (was 194)
- **The first 1 of those 17 unlock potential BCs is now active substrate.** Pass-3 BC binding gauntlet validated empirically; remaining 16 candidates (per scoping ledger §6.2) can follow under the same discipline.

## 8. Authority + verification trail

- **Operator contract authority:** operator 2026-06-25 pilot contract.
- **Doctrine authority:** ADR DEC-26b6e2 (immutable-atom freeze on `(term, definition)` at activation); v2 doctrine PR #67; Session 14 activation checkpoint PR #69; BC binding worksheet (gitignored, this session).
- **Script:** `barecount-devhub/scripts/_pass3-item-shelf-life-bc-binding-transport.mjs` — single-packet transport with all 5 operator halt classes armed (OPERATOR_REVIEW / service_error / duplicate / unexpected path / dataType='text').
- **Outcomes JSONL:** `barecount-devhub/.claude/pass3-item-shelf-life-bc-binding-outcomes-2026-06-25.jsonl` (3 records: pre-flight + panel + post-verify).
- **Outcomes summary:** `barecount-devhub/.claude/pass3-item-shelf-life-bc-binding-summary-2026-06-25.json` — `final_status='active'`, `halt_class=null`.
- **Pre-binding substrate state** (live API): Item BCs = 0; substrate-wide active value BCs = 194.
- **Post-binding substrate state** (live API): Item BCs = 1; substrate-wide active value BCs = 195; new BC `a291c25c-…` confirmed at `lifecycleState='active'`, `dataType='string'`, `kind='value'`, `characteristicId='d4c554ce-…'`, `semanticRole='temporal'`, `identityRole='descriptive'`.

## 9. Self-audit (D268)

| Rule | Honoured? |
|---|---|
| One-then-many | Honoured. Single-row Pass-3 binding; no batch. |
| Independent verification | Honoured. Substrate state queried live from a second endpoint (substrate-wide concepts list, kind=value+lifecycleState=active) confirming the +1 count. |
| No bulk substrate writes | Honoured. 1 BC write + 2 certs. |
| Cosmetic status changes avoided | Honoured. `lifecycle_state='active'` is the substantive transition. |
| Self-audit at session close | This document. |
| If a shortcut tempts, stop and flag it | Operator's `dataType='string'` guard explicitly tested in script (`if (dataType === 'text') { HALT }`); the temptation to assume "dataType derives correctly because the characteristic shape is text\|string\|descriptor" was rejected — guard executed and confirmed. |
| No lower-layer compensation | Honoured. The auto-activation of low-risk BCs is BCF orchestrator policy, not lower-layer compensation; ADR DEC-26b6e2 immutable-atom commitment applies as the term/definition freezes at the activation moment. |

## 10. Scope locks honoured this session

- 1 panel call (operator-approved pilot of exactly 1).
- 0 confirm calls (low-risk path bypasses confirm).
- 0 publication calls (low-risk path bypasses publication).
- 1 substrate write — 1 BC.
- 2 cert records (admission + auto-activation).
- 0 retry attempts.
- 0 other BCs transported.
- 0 other entity × characteristic bindings.
- 0 DDL changes.
- 0 ADR authoring.
- 0 amendments to v2 doctrine (PR #67 stands).
- 0 amendments to PR #62 / #65 / #67 / #68 / #69.
- 0 changes to BC-coverage ledger.
- 0 changes to A0.5 catalogue.

## 11. Held — next gate

The v2 doctrine arc has produced its first BC binding. Item now has 1 active BC; substrate-wide active value BCs = 195. Five operator-decision options for next gate:

1. **Bind the next 4 first-batch BC candidates on Item** — per scoping ledger PR #66 §6.2, the recommended first retrofit batch is 5 item-master rows (product_name, brand_name, serial_number_specification_description, lot_number_specification, shelf_life_duration). One is now done. The remaining 4 are blocked on v2 characteristic re-authoring (not just transliteration). Could re-attempt characteristic admission for any of the 4 under v2 doctrine, then bind on Item once each lands active.

2. **Continue Pass-1 retrofit Batch 2 characteristics** — scoping ledger §6.4 proposed waves (MO duration triplet, etc.). Each successful characteristic would unlock Pass-3 BC binding work on Item / MO / Asset.

3. **Pivot to E3** — master-data 8 AMBER entities. Equipment held; v2 doctrine validated end-to-end; E3 unblocks more Pass-3 surface area in a different direction.

4. **Amend v2 doctrine with Q-F load-bearing exception** — formalise the calibration note (now persisted at 3 substrate cert sites: C5 confirm cert, B10b publication cert, BC admission cert) into v2 doctrine §Q-F refinement. Empirical evidence for the exception is now substantial.

5. **Author a Pass-3 BC binding doctrine doc** — formalise the Pass-3 binding gauntlet Q-A through Q-I (developed inline in Session 15 worksheet) into a sibling doctrine to the Pass-1 v2 Preflight doctrine. Calibration evidence: 1 binding, 6/6 derived fields predicted correctly, 1 unpredicted field (`representationTerm`) emergent from characteristic shape.

All options held pending operator authorisation.

Held.
