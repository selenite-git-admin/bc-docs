---
title: BCF × OAGIS Pass 1 C5 — Closure Checkpoint (2026-06-25)
description: Closeout checkpoint for the C5 (quantity / measure cluster) of the BCF × OAGIS broad foundation buildout. 2 draft characteristics authored (dunnage weight + tare weight); 2 rows reclassified as map_to_existing → gross weight via Checker-First Preflight before transport; 1 row rejected at compiler (bare measure); 3 rows held slice-blocked. 100% panel approval rate on the 2 transported packets — vindicates the Checker-First Preflight discipline. Pass 2 entry recommended next per Option A from Session 3 projection.
status: closeout_complete
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-c5-closure
related_docs:
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
  - bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-1-c2-closure-checkpoint-2026-06-25.md
  - bcf-coverage-compiler-validation-2026-06-25.md
  - bcf-c3-c6-projection-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
---

# BCF × OAGIS Pass 1 C5 — Closure Checkpoint (2026-06-25)

> Closeout of the C5 (quantity / measure) cluster. **2 substrate writes landed.** Executed under the operator's Option A 6-step sequence and Checker-First Preflight discipline. The cluster is closed for this session; Pass 2 AMBER entity admissions are the next gate.

## 1. Substrate state

| Metric | Value |
|---|---|
| Active entities | 26 (unchanged) |
| Active characteristics | 62 (unchanged) |
| Draft characteristics | **20** (+2 this session: dunnage weight, tare weight) |
| Active value BCs | 194 (unchanged) |
| Total non-archived characteristics | 82 |

The +2 delta from this checkpoint:

| # | Term | characteristic_uid | certification_record_uid | created_at | admission_scope | panel_run_uid |
|---:|---|---|---|---|---|---|
| 1 | dunnage weight | `fd638c0d-6c5b-45f1-b4f9-cf89e0515c86` | `8065892c-2286-43a2-bb6a-3039ba0b9f1f` | 2026-06-25T04:50Z | cross_function | `0ef89128-74b9-4bea-ad78-96fc5093b0bc` |
| 2 | tare weight | `bed92cea-f423-4211-80e6-383c7528eeb4` | `19993492-ca2c-4894-88a9-8cb42690c486` | 2026-06-25T04:50Z | cross_function | `94b508cc-9c11-415c-a738-1b110e7c717b` |

## 2. C5 — Checker-First Preflight outcomes

**The operator's discipline was applied BEFORE transport: 4 compiler-routed new_substrate candidates → manual 5-question gauntlet per row → 2 transported, 2 reclassified.**

| seq | bf_name | BC | Compiler route | Checker-First verdict | Final route | Panel outcome | Cert outcome |
|---:|---|---:|---|---|---|---|---|
| 1 | `dunnage_weight_measure` | 7 | new_substrate | SURVIVE (multi-source standards, structurally distinct) | **panel_ready_retry** | APPROVE_FOR_DRAFT | **AUTHORED (draft)** |
| 2 | `tare_weight_measure` | 7 | new_substrate | SURVIVE (ISO 6346 + SOLAS VGM, separate measurement event) | **panel_ready_retry** | APPROVE_FOR_DRAFT | **AUTHORED (draft)** |
| 3 | `estimated_weight_measure` | 4 | new_substrate | DOWNGRADE (estimated = forecast-role on gross_weight; single source) | **map_to_existing** → `gross weight` (role=estimated) | (no panel) | (no cert) |
| 4 | `loading_weight_measure` | 4 | new_substrate | DOWNGRADE (loading = event-role on gross_weight; single source) | **map_to_existing** → `gross weight` (role=at-loading) | (no panel) | (no cert) |

**Panel approval rate: 2/2 = 100%.** Compare to C1 v1 (7%), C2 batch (12.5%), C1 RP-3 retry (25%). Cleanest panel run in the entire program.

**BC coverage**: 7+7+4+4 = 22 BC addressed (matches Session 3 projection). 2 via new substrate writes, 2 via map_to_existing (Pass-3 BC binding work).

**No review_reason on either panel** — clean approves, no Maker/Checker disagreements surfaced. `grounding_check_result=pass`, `quarantined=false` on both.

## 3. C5 final accounting (8 rows / 26 BC)

| Disposition | Rows | BC targets | % of cluster BC |
|---|---:|---:|---:|
| Authored (draft) | 2 | 14 | 53.8% |
| Map_to_existing → `gross weight` | 2 | 8 | 30.8% |
| Operator_semantic_decision (slice-blocked) | 3 | 3 | 11.5% |
| Reject_circular_or_generic (bare `measure`) | 1 | 1 | 3.8% |
| **Total** | **8** | **26** | **100%** |

**Addressed coverage: (14 + 8) / 26 = 84.6%.** Highest single-cluster addressed rate in the program. Higher than C1 (41%) and C2 (53%).

### Slice-blocked rows (3)
- `age_measure` (BC=1, quality-simple) — held pending Pass 2 quality entities
- `measure` — rejected as bare rep-term (not counted in slice_blocked)
- `physical_area_measure` (BC=1, master-data) — held pending Pass 2 master-data entities
- `weight_measure` (BC=1, logistics) — held pending Pass 2 logistics entities

## 4. C5 cumulative tally vs program

| Phase | Draft characteristics authored (cumulative) |
|---|---:|
| Pre-C5 baseline (C1+C2 closure state) | 18 |
| C5 this checkpoint | +2 |
| **C5 + pre-C5 total drafts** | **20** |

## 5. Authority + verification trail

- **Program authorization:** DEC-f94895 (caps, halt rules) — unchanged.
- **Admission policy:** DEC-ec341c (admission_scope) — implemented end-to-end as of 2026-06-24T15:31Z (verified at C1 closure checkpoint §7).
- **Maker truncation fix:** bc-ai PR #32 (`820c5b8`) — verified in-effect (long multi-source evidence at 99-165s wall-clock per panel completed cleanly).
- **Writer guard at `registry-authoring-orchestrator.service.ts:293`:** unchanged.
- **Pre-confirm substrate-collision check:** 0 matches for `dunnage weight` and `tare weight` (verified live via pg_query immediately before each confirm).
- **C5 confirms:** writer concurrency = 1, sequential. dunnage weight first (114 ms), tare weight second (42 ms). HTTP 200 on both. Outcome `authored` on both.
- **Substrate state post-confirm:** 26 / 62 / 20 / 194 (verified live via pg_query immediately after).

## 6. Cost actuals vs Session 3 projection

| Metric | Session 3 projection (compiler-only) | Checker-First-applied actual |
|---|---:|---:|
| Panel calls | 4 | **2** (–50%) |
| Substrate writes | up to 4 | **2** |
| Map_to_existing rows | 0 | **2** (Pass-3 BC binding work) |
| BC coverage addressed | 22 | **22** (identical — same gain, different routes) |
| Panel approval rate | (unprojectable) | **100%** |
| Wall-clock | (unprojectable) | **165s transport + ~5 min confirm + ~30 min preflight authoring** |
| Pass 1 panel cap consumed (cumulative) | n/a | ~85/270 (~31%) |

The Checker-First Preflight worked exactly as the doctrine intended: same BC coverage, half the panel cost, no avoidable burn.

## 7. Checker-First Preflight calibration corpus addition

The 2 DOWNGRADE rows (`estimated_weight_measure`, `loading_weight_measure`) join the C2 precision-tail rows as calibration fixtures. The trap pattern they share:

**Role-modifier-on-existing-substrate trap** — compiler routes to new_substrate because no exact term matches, but Checker-First reveals the proposed concept is a forecast-role / event-role variant of an existing substrate characteristic with no separate external standard distinguishing it.

Calibration fixture entries:

```
Would this fail like estimated_weight_measure? (estimated = forecast-role on gross_weight; no separate standard distinguishes "estimated weight" from gross-weight-estimation)
Would this fail like loading_weight_measure?  (loading = event-role on gross_weight; same underlying measurement at different timestamp)
```

These join the C2 fixtures (precision-tail trap): creation_date_time, goods_receipt_date_time, services_receipt_date_time, requested_execution_date_time, estimated_departure_date_time.

## 8. C5 closure stance

**Closed completely.** No residuals to chase from this cluster.

- 2 substrate writes landed at draft state.
- 2 map_to_existing reclassifications recorded for Pass-3 BC binding (no panel cost; no transport queue).
- 3 slice-blocked rows held pending Pass 2 entity admissions (per Option A sequence).
- 1 reject (bare `measure`).
- Panel approval rate 100%, panel cost ~50% under projection, BC coverage on plan.

C5 is the cleanest cluster in the program. The combination of Session 2 compiler routing + Session 3 projection + operator's Checker-First Preflight discipline + small-batch transport with operator-gated confirms produced this outcome.

## 9. Scope locks honoured at this checkpoint

- 2 panel calls (operator-approved subset only).
- 2 substrate writes (operator-approved per row).
- 0 retry-ledger writes for the held rows.
- 0 transport scripts run beyond the approved subset.
- 0 DDL changes; 0 ADR authoring; 0 policy changes.
- 0 changes to BC-coverage ledger.
- 0 substrate writes beyond the 2 authorized C5 confirms.

## 10. Next gate

**C5 is closed.** The next gate per Option A from Session 3 projection is **Pass 2 entry planning** — specifically the AMBER entity slices that would unlock the largest set of currently-slice-blocked C3-C6 work:

1. **Item** (master-data-root, 1 AMBER entity) → unlocks ~17 BC of slice-blocked C3-C6 rows
2. **Asset + Equipment + Maintenance Order** (asset-maintenance-simple, 3 AMBER entities) → unlocks ~34 BC
3. **8 master-data AMBER entities** (Business Partner / Cost Centre / Location / Org Unit / Party / Price List / Price List Item / Project) → unlocks ~22 BC

Open operator questions before Pass 2 entry (carried from Session 3 §5):
- Does DEC-f94895 program authorization extend to Pass 2, or does Pass 2 require its own A1-A5 authorization?
- Priority order: Item first (single entity, 17 BC) or asset-maintenance-simple first (3 entities, 34 BC)?
- Entity admission via F4-v2 panel or a different surface?
- RED composite-identity packets (Bill of Materials Line, Inspection Lot, Inventory Position, Maintenance Order Operation, Operation, Test Result, Work Order Operation) — out-of-scope for Pass 2 AMBER wave; held until separate operator decision packets.

Held. Pass 2 entry awaits operator authorization.
