---
title: BCF × OAGIS Pass-2 E2 (Asset + Maintenance Order) Closure Checkpoint (2026-06-25)
description: Closeout for the second Pass-2 wave. Two of three asset-maintenance-simple AMBER entities admitted via the verified createEntity surface (Asset, Maintenance Order); Equipment held per operator decision as separate operator-decision packet (Q-B × Q-F.3 structural interaction). Orchestrator fast-laned cert + F3 + activation atomically for both. 100% panel approval on the two that ran. 29 active entities post-admission (was 27). First multi-entity Pass-2 batch — proves the batching pattern + the operator-applied Checker-First Preflight Q-F as a real reducer.
status: closeout_complete
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-2-e2-closure
related_docs:
  - bcf-oagis-pass-2-entry-note-2026-06-25.md
  - bcf-oagis-pass-2-e1-item-closure-checkpoint-2026-06-25.md
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
  - bcf-oagis-pass-1-c5-closure-checkpoint-2026-06-25.md
  - bcf-c3-c6-projection-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
---

# BCF × OAGIS Pass-2 E2 (Asset + Maintenance Order) — Closure Checkpoint

> Second Pass-2 wave. First multi-entity batch. Three AMBER asset-maintenance-simple entities went through the 6-question Checker-First Preflight; **two SURVIVE 6/6** (Asset, Maintenance Order) and **one HELD** (Equipment — Q-B × Q-F.3 structural interaction). Operator decision: transport Asset + Maintenance Order; Equipment becomes a separate operator-decision packet. Worksheet did its job: it reduced the batch before any panel call. Orchestrator fast-laned cert + F3 createEntity + activation atomically for both transported entities. No halt triggers fired. Batching pattern proven; Checker-First Preflight Q-F (added in PR #62 amend) validated as a real reducer rather than ceremony.

## 1. Substrate state

| Metric | Before E2 | After E2 |
|---|---:|---:|
| Active entities | 27 | **29** (+2: Asset, Maintenance Order) |
| Active characteristics | 62 | 62 |
| Draft characteristics | 20 | 20 |
| Active value BCs | 194 | 194 |
| Superseded entities | 3 | 3 |
| Total entity rows | 30 | 32 |

The +2 delta:

| Field | Asset | Maintenance Order |
|---|---|---|
| entity_id | `47f66f57-d73c-4512-a106-0f8a6e809e72` | `10b362fd-c2a3-46e7-9701-2556206291cf` |
| entity_version_id | `ee3483b4-0e44-45e0-b5ca-102528871c56` | `bccfd706-22ea-4893-a858-8fe13f8bd65e` |
| certification_record_id | `11c53960-6045-4b6b-bcc5-a0d7daf161ec` | `b476316f-3a51-42e1-a915-755e31387ceb` |
| activation_certification_record_id | `10ae9a0d-7173-419e-ab4b-c673d9c7bd0b` | `17bd32fe-1950-4fde-b0a1-ea38f4c8e5e9` |
| panel_run_uid | `1113e8f0-c75f-4112-8834-67d9f41e9709` | `0a7231ba-bdbf-4e54-aa47-1b43b4983966` |
| lifecycle_state | **active** (fast-laned in same flow) | **active** (fast-laned in same flow) |
| Slice | asset-maintenance-simple | asset-maintenance-simple |
| Class | AMBER | AMBER |

## 2. E2 transport — outcome

Per the operator E2 go contract: 2-entity transport, concurrency 2 (independent entities, zero collision risk), no separate confirm step (orchestrator fast-lanes to active automatically per Pass-2 entry note §2).

| Row | HTTP status | Wall time | Outcome class | Halt? | Activation state |
|---|---:|---:|---|---|---|
| Asset | 200 | 43,648 ms | `authored` | No | `lifecycle_state='active'` |
| Maintenance Order | 200 | 87,052 ms | `authored` | No | `lifecycle_state='active'` |
| **Total (concurrent)** | — | **87,096 ms** | — | — | — |

**Panel approval rate: 2/2 = 100%.** The Pass-2 surface is again proven end-to-end. The asynchronous concurrency-2 batch completed cleanly with no race conditions or partial-state observations.

**Wall-time observation:** Asset 43.6s ≈ E1 (Item) 38.9s; Maintenance Order 87.1s ≈ 2× Asset. The asymmetry is likely tied to the longer Maintenance Order definition body and the more nuanced Purchase-Order / Sales-Order exclusion language requiring more panel deliberation tokens. With concurrency 2, total wall-time = max(rows), not sum — both finished in 87s versus a sequential 130s estimate.

## 3. Checker-First Preflight result (applied pre-transport per operator E2 contract)

The 6-question entity-adapted gauntlet from Pass-2 entry note §5 (v2 with Q-F amended in PR #62). Applied to all three E2-trio entities in a combined worksheet (`barecount-devhub/.claude/bcf-pass-2-e2-asset-maintenance-checker-first-worksheet-2026-06-25.md`) before any panel call.

### 3.1 Asset

| # | Question | Answer | Pass/Fail |
|---|---|---|---|
| A | Substrate has Asset by canonical_name? | No (verified via live entity-list query) | Pass |
| B | Role/scope variant of existing entity? | No — Asset is master-data for operational/physical resources, peer to Item, Customer, Supplier. Not a sub-type. | Pass |
| C | Identity-bearing characteristic precondition? | No precondition required at entity-admission time; characteristics bind via BCs in Pass 3 | Pass |
| D | Identity reference graph acyclic (BCR §4)? | Acyclic — Asset is a master entity at the top of asset-maintenance-simple; no outgoing identity references | Pass |
| E | AMBER classification confirmed? | Yes (per A0.5 §5: asset-maintenance-simple all AMBER, Asset listed) | Pass |
| F | Fast-lane active acceptable (5 sub-checks)? | F.1 keep "Asset" with definition-level exclusion; F.2 definition crisp; F.3 operational-vs-financial-asset boundary stable; F.4 BC-binding readiness real (~34 BC slice-blocked work); F.5 AMBER classification stable | Pass |

**Verdict: SURVIVE (6/6).**

### 3.2 Maintenance Order

| # | Question | Answer | Pass/Fail |
|---|---|---|---|
| A | Substrate has Maintenance Order by canonical_name? | No (verified). Order-family present (Sales Order, Sales Order Line, Purchase Order, Purchase Order Line) but distinct semantic from Maintenance Order. | Pass |
| B | Role/scope variant of existing entity? | No — Maintenance Order is an internal work-authorisation document on operationally-owned assets; Purchase Order and Sales Order are external commercial transactional records. Operational-internal vs commercial-cross-organisational distinction is well-established. | Pass |
| C | Identity-bearing characteristic precondition? | No precondition required at entity-admission time | Pass |
| D | Identity reference graph acyclic (BCR §4)? | Acyclic — Maintenance Order is a work-control entity, holds reference to Asset (parent operational artefact) but not vice versa | Pass |
| E | AMBER classification confirmed? | Yes (A0.5 §5 lists Maintenance Order in asset-maintenance-simple AMBER) | Pass |
| F | Fast-lane active acceptable (5 sub-checks)? | F.1 canonical_name "Maintenance Order" matches OAGIS noun; F.2 definition explicitly excludes Purchase Order and Sales Order; F.3 internal-work vs cross-org-transaction boundary stable; F.4 BC-binding readiness real; F.5 AMBER stable | Pass |

**Verdict: SURVIVE (6/6).**

### 3.3 Equipment — HELD

| # | Question | Answer | Pass/Fail |
|---|---|---|---|
| A | Substrate has Equipment by canonical_name? | No | Pass |
| **B** | **Role/scope variant of existing entity?** | **AMBIGUOUS** — Equipment is plausibly either a peer of Asset (separate operationally-tracked operational artefact distinct from the broader Asset notion) **or** a discriminator-field on Asset (Asset.assetType='equipment'). The choice depends on standards alignment (OAGIS / SAP / ISO 55000) and downstream BC-binding implications. | **AMBIGUOUS** |
| C | Identity-bearing characteristic precondition? | No precondition at admission time | Pass |
| D | Identity reference graph acyclic (BCR §4)? | Acyclic only conditional on B (if peer of Asset). If sub-type of Asset, identity layer is inherited and the BCR §4 walk differs. | Pass conditional on B |
| E | AMBER classification confirmed? | Yes (A0.5 §5) | Pass |
| **F** | **Fast-lane active acceptable?** | **FAIL** — F.3 scope/boundary is not stable, and F.1 canonical_name finalisation depends on B. Fast-laning Equipment to active would lock in a substrate distinction (entity-peer vs Asset-discriminator) that may later require supersession under Foundation Invariant III. | **FAIL** |

**Verdict: HOLD.** Equipment becomes a separate operator-decision packet. Asset subtype vs peer entity is structural and should not be decided as a side decision inside E2. A decision packet comparing OAGIS / SAP / ISO 55000 semantics directly is required before re-attempting.

### 3.4 Worksheet outcome — operator decision contract honoured

The worksheet reduced the batch from 3 panels to 2 before any panel call. The operator explicit decision contract on 2026-06-25:

> "Approve Asset transport with the name Asset, not Operational Asset, but keep the definition exclusion explicit … Approve Maintenance Order transport with explicit exclusion from Purchase Order/procurement … Hold Equipment. Do not transport in E2 … too consequential for a side decision inside E2."

This is the Checker-First Preflight Q-F doing exactly what the PR #62 amendment intended: surfacing the irreversibility risk before it locks in.

## 4. Halt triggers — none fired

Per operator E2 go contract (carried forward from E1), the transport script armed five halt conditions:

| Trigger | Fired? |
|---|---|
| `park` (non-APPROVE verdict) | No |
| `service_error` (HTTP 0/5xx) | No |
| `name_collision` (F3 returns conflict at write time) | No |
| `red_composite_signal` (RED/composite-identity signal in panel response) | No |
| `activation_pending` (cert + F3 ran but activation deferred) | No |

The fast-lane completed cert + F3 createEntity + activation as a single atomic flow for both rows with no partial state.

## 5. Authority + verification trail

- **Program authorization:** DEC-f94895 — unchanged. Pass-2 caps (A5: $40 / 80 panel calls) consumed 3/80 = 3.75% after E1 + E2.
- **Admission policy:** DEC-ec341c admission_scope rubric — applied. Both admitted entities scoped `cross_function` (Asset crosses operational / maintenance / accounting-depreciation / utilisation; Maintenance Order crosses maintenance / accounting-cost-tracking / utilisation-scheduling).
- **Pass-2 entry note (v2):** `bcf-oagis-pass-2-entry-note-2026-06-25.md` §5 with Q-F amendment from PR #62 — gates closed (operator go-signal received per-entity; Checker-First Preflight applied; no halt triggers).
- **E1 closure checkpoint:** `bcf-oagis-pass-2-e1-item-closure-checkpoint-2026-06-25.md` — proven Pass-2 surface; pattern reused without modification at the orchestrator boundary.
- **Pre-transport substrate-collision check (live entity-list query):** 0 matches for "Asset" and 0 matches for "Maintenance Order"; 0 matches for "Equipment" (HELD).
- **F3 createEntity write:** succeeded at `registry-authoring.service.ts:366` for both rows; name-conflict-check passed; cert was minted before each write.
- **Substrate post-admission (live entity-list query, paged through):** 29 active entities, 3 superseded, 32 total. Asset and Maintenance Order resolved by entity_id to canonical_name='Asset' and canonical_name='Maintenance Order' respectively. Equipment correctly absent.

## 6. Pass-2 unlock topology

E2 admission of Asset and Maintenance Order activates 2 of 3 entities in the asset-maintenance-simple slice. Per Session 3 projection (`bcf-c3-c6-projection-2026-06-25.md`), the asset-maintenance-simple slice was expected to unlock ~34 BC across Pass-1 rows held on this slice. The realised unlock from this checkpoint covers the 2 admitted entities only; rows whose Pass-1 binding requires Equipment specifically remain held until the separate Equipment decision packet completes.

| Slice availability | Before E2 | After E2 |
|---|---|---|
| asset-maintenance-simple — Asset | unavailable | available |
| asset-maintenance-simple — Maintenance Order | unavailable | available |
| asset-maintenance-simple — Equipment | unavailable | **still unavailable (HELD)** |

A future Pass-1 retrofit pass can re-route the BC subset that targets Asset and/or Maintenance Order without waiting for Equipment.

## 7. Pass-2 cumulative tally

| Phase | Active entities (cumulative) | Panels consumed | Wall time |
|---|---:|---:|---:|
| Pre-Pass-2 baseline | 26 | 0 | — |
| E1 (Item) | +1 = 27 | 1 | 38.9s |
| **E2 (Asset + Maintenance Order)** | **+2 = 29** | **2** | **87.1s** |
| **Total Pass-2 to date** | **29 (+3 from baseline)** | **3 / 80 (3.75%)** | **126.0s wall, ~$40 cap consumed marginally** |

Remaining AMBER Pass-2 admissions (per Pass-2 entry note §4 wave-plan estimate): ~44 across E3–E10 plus the Equipment operator-decision packet. 7 RED composite-identity entities out-of-scope; separate operator decision packets per A0.5 §7.

## 8. Cost actuals vs Pass-2 entry note + E1 calibration

| Metric | Expectation pre-E2 | Actual |
|---|---|---:|
| Panel calls (E2 trio) | 3 if all SURVIVE | **2** (Equipment HELD) |
| Substrate writes (E2 entities) | 3 if all APPROVE | **2** ✓ matches reduced batch |
| Wall time concurrency 2 | ~80s estimated from E1 + ~150s Pass-1 calibration | **87.1s** ✓ |
| Halt triggers | 0 expected | **0** ✓ |
| Pass-2 panel cap consumed (cumulative incl. E1) | 3/80 = 3.75% | **3/80 = 3.75%** ✓ |

The two notable outcomes:

1. **Checker-First Preflight Q-F reduced the batch by 33%.** Three packets came in; two went out. Equipment was held because Q-B × Q-F.3 surfaced a structural irreversibility risk before any panel deliberation. This is the calibration evidence that PR #62's Q-F amendment is doing real work — without Q-F, Equipment would have been fast-laned and would now be locked in as a peer entity in substrate (or as a draft pending decision — but either way the substrate distinction would be premature).

2. **Concurrency 2 is safe and faster.** Two independent createEntity rows with no collision risk completed in 87s wall-time. Sequential at observed per-row rates would have been ~130s. The Pass-2 batching pattern is proven for the multi-row case.

## 9. E2 closure stance

**Closed completely for the 2 transported entities.** No residuals on Asset or Maintenance Order. Pass-2 surface continues to be proven end-to-end. Substrate is in a clean post-E2 state.

**One held entity carries forward as its own gate:** Equipment is held pending a separate operator-decision packet that compares OAGIS / SAP / ISO 55000 semantics directly. Tag: `pass-2-e2-equipment-held`. Recommendation in §10 below.

## 10. Held: Equipment operator-decision packet

Equipment was the Q-F.3 failure of E2. The structural question to resolve in a dedicated decision packet:

| Option | Implication | Standards alignment |
|---|---|---|
| **A. Equipment as peer of Asset** | New entity at admission; Asset and Equipment are sibling master-data records; downstream BCs bind to one or the other | OAGIS treats `equipment` as a distinct noun in some context; ISO 55000 sometimes uses "equipment" as a category of asset rather than as a separate entity |
| **B. Equipment as Asset discriminator-field** | No new entity; Asset.assetType='equipment' or Asset.assetClass='equipment'; downstream BCs bind via the discriminator | SAP EAM uses a discriminator (TPLNR + ANLN1) but the operational record is still under a unified asset master in many configurations |
| **C. Equipment as Asset subtype with own entity (Foundation Invariant III problem)** | Subtype-as-entity creates a dual-identity problem at characteristic-binding time; not preferred but worth ruling out | Generally disfavoured in OAGIS / ISO 55000 |

The decision packet should produce: (a) standards comparison with citations, (b) downstream BC-binding impact analysis, (c) test case showing how a Pass-1 row asking "is this equipment maintained" would bind under each option, (d) recommendation + operator gate. Until the packet exists, Equipment stays held.

## 11. Scope locks honoured at this checkpoint

- 2 panel calls (operator-approved subset of 2; Equipment held without a panel call).
- 2 substrate writes (operator-approved entity admissions via fast-lane).
- 0 retry-ledger writes for held rows.
- 0 transport script invocations beyond the approved E2 packet.
- 0 DDL changes; 0 ADR authoring; 0 policy changes.
- 0 changes to BC-coverage ledger.

## 12. Next gate

E2 is closed. Three operator-decision options for the next gate:

1. **E3 = master-data 8 AMBER entities** — Item already admitted in E1, but the master-data slice has 8 more entities (Business Partner / Cost Centre / Location / Org Unit / Party / Price List / Price List Item / Project). Largest single wave. ~22 BC unlock per Pass-2 entry note §4.
2. **Equipment operator-decision packet (held from E2)** — resolve the peer-vs-discriminator question before continuing to E3. Smaller scope, structurally important.
3. **Pivot to Pass-1 retrofit** — 8 rows / 17 BC unlocked by master-data-root in C3/C4/C6 from E1, plus subset of the ~34 BC unlocked by asset-maintenance-simple Asset + Maintenance Order from E2. Process under the same Checker-First Preflight + projection-then-act discipline.

All three options remain held pending operator authorisation.

Held.
