---
title: BCF × OAGIS Pass 1 C2 — Closure Checkpoint (2026-06-25)
description: Closeout checkpoint for the C2 (date|temporal) cluster of the BCF × OAGIS broad foundation buildout. 1 draft characteristic authored (estimated arrival date time). 7 panel parks held as residuals — 5 share the same defect (precision-tail trap) and are reclassified as map_to_existing without re-panel. 1 service-error timeout held. 10 map_to_existing rows held for Pass-3 BC binding. 5 defer + 1 reject + 21 slice-blocked. Operator authored a new Checker-First Preflight doctrine (memory feedback_checker_first_preflight.md) as the load-bearing learning from this cluster. C3 entry is not authorized in this checkpoint.
status: closeout_held
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-c2-closure
related_docs:
  - bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md
  - bcf-oagis-broad-buildout-blueprint-2026-06-23.md
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
---

# BCF × OAGIS Pass 1 C2 — Closure Checkpoint (2026-06-25)

> Closeout state of the C2 (date|temporal) cluster. **Pass 1 C2 stays held at this state; the 7 parks and 1 service-error are NOT chased further in this session.** The load-bearing learning is the **Checker-First Preflight doctrine** the operator authored after the parks revealed a recurring precision-tail trap.

## 1. Substrate state

| Metric | Value |
|---|---|
| Active entities | 26 (unchanged) |
| Active characteristics | 62 (unchanged) |
| Draft characteristics | **18** (+1 this session: `estimated arrival date time`) |
| Active value BCs | 194 (unchanged) |
| Total non-archived characteristics | 80 |

The +1 delta from this checkpoint's C5 confirm step:

| # | Term | characteristic_uid | certification_record_uid | created_at | admission_scope |
|---:|---|---|---|---|---|
| 1 | estimated arrival date time | `2f90d4d3-68f6-43c5-9c8a-56a5b160511b` | `2d1069ff-62fe-4e30-99bb-2d8e8f2415b9` | 2026-06-25T03:17:Z | function_scoped / logistics_transportation |

## 2. C2 transport — outcomes

C2 was a single transport wave (no iterations), per the C2 readiness brief rev 2.1 §6.5 ("single transport batch, no iterations" — codifies the cost-control lesson from C1's 5-iteration trail). 9 Tier-A `panel_ready_retry` packets were transported under DEC-ec341c admission-scope rubric.

| Outcome | Count | panel_run_uids |
|---|---:|---|
| APPROVE_FOR_DRAFT → confirmed | 1 | `ca88b689-aad5-497b-8f21-80fceea63a7a` (estimated_arrival_date_time) |
| OPERATOR_REVIEW (parked) | 7 | See §3 below |
| service_error (timeout 180s) | 1 | `pass1-c2-clean-04-transaction_date_time` — no panel_run_uid (network fail before stamp) |

Approval rate this batch: 1/8 substantive panels = 12.5%. Lower than the C1 RP-3 retry rate (25%) — root cause is the recurring **precision-tail trap** in 5 of the 7 parks (see §3.1).

## 3. Parked residuals (7 rows — held as residuals, not chased)

### 3.1 Precision-tail trap parks (5 rows — reclassified as `map_to_existing`, no re-panel)

The Checker correctly applied No-Synonym-Admission against existing date-shaped substrate when the proposed term was a precision-tail variant of a substrate sibling. **These rows are reclassified `map_to_existing_characteristic` based on the panel's substantive feedback; no re-transport is scheduled.** Pass-3 BC binding will carry the timestamp precision per the empirical `effective date × Customer Invoice` precedent (BC binding at `date_time|timestamp` over substrate at `date|date`).

| panel_run_uid | proposedName | Reclassification | Substrate sibling |
|---|---|---|---|
| `3644392d-7b8e-4d38-8dfe-679597adc3bb` | creation date time | map_to_existing | `system entry date` (`df1064f0-…`) |
| `97d2677f-f909-443e-95b6-ad2a8303aa16` | goods receipt date time | map_to_existing | `delivery date` (`2dfd4747-…`), role_qualifier=goods-receipt |
| `a0210dbd-be68-431d-bbfe-a6645129733f` | services receipt date time | map_to_existing | `delivery date` (`2dfd4747-…`), role_qualifier=services-receipt |
| `feba2c0c-9f85-49cf-883e-010cf5aac707` | requested execution date time | needs operator framing | ISO 20022 names the field `RequestedExecutionDate`; precision-tail over-specifies. Hold for operator decision on naming. |
| `92c1fb76-e9ae-4621-8c41-9461f8e99179` | estimated departure date time | map_to_existing | `ship date` (`dba7cf96-…`), role_qualifier=estimated-departure |

### 3.2 Scope-inflation park (1 row)

| panel_run_uid | proposedName | Concern |
|---|---|---|
| `a4dc27f4-ea70-4619-a729-ecf91c5725d5` | best used by date | Maker said `cross_function`; Checker flagged industry-specific (food / pharmaceutical / CPG). Operator decision: reclassify as `industry_scoped` (industry: consumer_packaged_goods), or hold as cross_function and re-prep with cross-industry evidence. |

### 3.3 Single-source scoped park (1 row)

| panel_run_uid | proposedName | Concern |
|---|---|---|
| `5838b063-ad89-44d8-bc37-426c3dbf0e0d` | loading date time | `function_scoped` packet cited only OAGIS Standard 10.12. ADR-ec341c §3 precondition 4 requires evidence across two or more systems / standards. Could be retried with a second standard (e.g., UN/EDIFACT loading messages, port-loading EDI codes) but held this session. |

## 4. Service-error row (1 — held pending investigation)

| candidateRef | Status | Hypothesis |
|---|---|---|
| `pass1-c2-clean-04-transaction_date_time` | timeout at 180s (HTTP 0, no panel_run_uid stamped) | Likely Trap 6 (Maker `max_output_tokens` truncation) — the packet carried long multi-source evidence (ISO 8601 + RFC 3339 + posting-date distinction text). bc-ai PR #32 raised the cap to 8192, but the running interpreter should be probe-verified before any retry. Alternative: bc-ai transient slowdown. Not retried this session. |

## 5. Held semantic rows (operator_semantic_decision — slice-blocked)

21 C2 rows were classified `operator_semantic_decision` in the prep step because they target only non-finance entity slices (production-composite, quality-composite, asset-maintenance-simple, master-data, logistics) — substrate has no entities in those slices yet, so the value-properties have no Pass-3 binding target. Premature to admit characteristics without binding destinations.

These rows are held until Pass 2 admits the relevant entity slices.

| seq | bf_name | Slice block |
|---:|---|---|
| 09 | received_date_time | overlaps with goods/services receipt + invoice receipt — held for operator framing |
| 18 | payment_date_time | overlaps with clearing / value / requested-execution — held |
| 22 | need_delivery_date | production |
| 23 | available_date_time | production |
| 24 | manufacture_date_time | quality |
| 25 | sampled_date_time | quality |
| 27 | activity_date_time | project-accounting |
| 32-33 | last_shipment_date_time, last_receiving_date_time | logistics |
| 34-37, 40 | start/end/desired-completion/planned-completion/estimated-completion_date_time | production / quality |
| 38-39 | birth_date_time, death_date_time | quality.corrective-action (oddly placed HCM-shape) |
| 41 | certification_date | quality |
| 42-43, 45 | reported / respond-by / failure_date_time | maintenance |
| 46 | completion_date_time | maintenance-composite |

## 6. C2 program — cumulative authoring tally

| Phase | Draft characteristics authored (cumulative) | Notes |
|---|---:|---|
| Pre-C2 baseline (C1 closure state) | 17 | 16 C1-program drafts + 1 pre-existing `fiscal period` |
| C2 wave transport + confirm | +1 | estimated arrival date time |
| **C2 + pre-C2 total drafts** | **18** | All currently at `lifecycle_state='draft'` |

## 7. C2 row disposition — final accounting (46 rows)

| Disposition | Count | Notes |
|---|---:|---|
| Authored (draft) | 1 | estimated arrival date time |
| Map_to_existing (Pass-3 BC binding work) | **15** | 10 pre-classified + 5 reclassified post-park per §3.1 |
| Defer_insufficient_evidence | 5 | required_date_time, set_date_time, accept_by_date_time, engineering_change_date_time, change_date_time |
| Reject_circular_or_generic | 1 | `date_time` (bare rep-term) |
| Operator_semantic_decision (slice-blocked) | 21 | See §5 |
| Operator_semantic_decision (post-park: scope inflation) | 1 | best used by date |
| Operator_semantic_decision (post-park: naming) | 1 | requested execution date time |
| Defer (post-park: single-source) | 1 | loading date time |
| Service_error (held for investigation) | 1 | transaction date time |
| **Total** | **46** | |

## 8. The Checker-First Preflight doctrine (load-bearing learning)

C2's 12.5% approval rate vs C1 RP-3 retry's 25% — and the 5-of-7 parks sharing one defect (precision-tail trap) — surfaced that the Desktop-role packet authoring pass was operating Maker-first instead of Checker-first. The operator authored a new doctrine in response:

**Rule of thumb:** "panel-ready" means **"survived the panel's likely objections"** — not **"well-written."**

Six elements (full text in memory `feedback_checker_first_preflight.md`):

1. **Invert the workflow** — substrate-sibling search → duplicate/role/representation/scope attack → only then proposed term.
2. **Substrate-sibling deny gate** — strip precision tail (`_date_time` → `date`); strip role modifiers (actual/promised/scheduled/required/estimated); compare semantic root.
3. **Required `why_not_bc_binding` field** — every panel_ready_retry candidate must carry a crisp argument for why an existing substrate sibling does NOT cover it.
4. **Simulate Maker / Checker / Moderator locally** — Moderator must beat the Checker, not just produce a Maker case.
5. **Trap-specific rubrics** — precision-tail, role-qualifier, source-field-tail, single-source-scoped, scope-inflation.
6. **Parked rows are calibration fixtures** — "would this fail like X?" becomes the preflight check for future candidates.

**For C3 and forward:** the Desktop-role authoring pass MUST run the Checker-First Preflight before any candidate is marked `panel_ready_retry`. The C2 parks become the calibration corpus. The brief at `.claude/bcf-c2-readiness-brief-2026-06-25.md` will be updated with this as Trap 7 in the next-session refresh.

## 9. Authority + verification trail

- **Program authorization:** DEC-f94895 (caps, halt rules) — unchanged.
- **Admission policy:** DEC-ec341c (D453) — implemented end-to-end (bc-core PR #358, bc-ai PR #31 merged 2026-06-24T15:31Z; DBCP migration applied; verified at C1 closure checkpoint §7).
- **Runtime state at checkpoint:** bc-core on port 3100 from `C:\MyProjects\bc-core` dist; bc-ai on port 4300 from `C:\MyProjects\bc-ai` source. Both responsive on `/api/health` and `/docs`. Verified by transport-time HTTP 200 on 8 of 9 panel calls.
- **Maker truncation fix (Trap 6):** bc-ai PR #32 (`820c5b8`, merged 2026-06-24T16:20:52Z) — `RegistryAuthoringMaker.max_output_tokens = 8192`. Live-interpreter probe was attempted but failed (local venv mismatch, not running process). The 1 service-error row may indicate fix not loaded in running interpreter — to verify before any retry.
- **Writer guard:** `registry-authoring-orchestrator.service.ts:293` unchanged (the seatbelt). Verified by 7 parks correctly refusing to author non-APPROVE outcomes.
- **C5 confirm:** 1 confirm posted with writer concurrency = 1. HTTP 200, 149 ms. Outcome `authored`. characteristic_uid `2f90d4d3-…`, cert_uid `2d1069ff-…`.
- **Pre-confirm substrate-collision check:** 0 active or draft characteristic terms match `estimated arrival date time` (verified via pg_query immediately before confirm).
- **Pre-write substrate-collision counts post-confirm:** 62 active + 18 draft = 80 total non-archived characteristic terms.

## 10. C2 closure stance

**Closed with residuals.** This checkpoint marks the end of active C2 execution under DEC-f94895.

- **Substrate output:** 1 draft characteristic from C2 (estimated arrival date time).
- **Residuals carried forward:** 5 precision-tail parks reclassified as `map_to_existing` (Pass-3 work, no re-panel) + 1 scope-inflation park (best used by date — operator framing) + 1 single-source park (loading date time — could retry with second standard) + 1 service-error (transaction date time — investigate then retry).
- **C2 row catalogue coverage:** 1 authored + 15 map_to_existing + 5 defer + 1 reject + 24 operator_semantic_decision/held = 46 rows accounted for.
- **Cumulative C1+C2 catalogue coverage:** 17 confirmed + 11 C1 residuals + 7 C2 residuals + 15 C2 map_to_existing + 5 C2 defer + 1 C2 reject + 24 C2 slice-blocked = continuous accounting against the original 40-row C1 + 46-row C2 = 86 total.

## 11. Scope locks honoured at this checkpoint

- 0 panel calls beyond the 9 C2 Tier-A transport calls.
- 0 substrate writes beyond the 1 authorized C5 confirm in §1.
- 0 retry-ledger writes for the parked / service-error rows.
- 0 C3 entry — explicitly out of scope.
- 1 C5 confirm (the authorized estimated_arrival_date_time row). Writer concurrency 1; HTTP 200; substrate-collision check returned 0 matches.
- No DDL changes; no ADR authoring; no policy changes.

## 12. Next gate

C2 is held at this closure state. No further action authorized in this checkpoint.

Future work surfaces requiring explicit separate operator authorization:
- **C2 residual remediation** — best used by date (scope reclassification), loading date time (multi-source re-prep), transaction date time (Trap 6 investigation + retry), requested execution date time (rename decision).
- **C1 residual remediation** — 11 C1 residuals still held per C1 closure checkpoint §8.
- **C3 entry** — operator authorization required.
- **Checker-First Preflight mechanisation** — codify §8 doctrine into the `_desktop-prep-output-*.mjs` generator so the rubric is enforced at packet-author time, not by post-hoc reading of panel review_reasons.

Held.
