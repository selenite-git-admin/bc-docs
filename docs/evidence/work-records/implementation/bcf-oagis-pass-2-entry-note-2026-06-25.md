---
title: BCF × OAGIS Pass-2 Entry Note (2026-06-25)
description: Short entry note closing the Pass-2 execution-trigger gap left by DEC-f94895. Confirms DEC-f94895 carryover, names the Pass-2 surface as the same /api/bcf/registry-authoring-runs endpoint (operation=createEntity, low-risk action_code), scopes the first wave to E1 = Item only (master-data-root, 1 AMBER entity, 17 BC unlock per Session 3 projection), adapts the Checker-First Preflight 5-question gauntlet to entities, and adds Pass-2-specific halt triggers. No panel runs, no writes, no substrate mutations executed in the writing of this note. Wave execution awaits a separate explicit operator act.
status: pass_2_entry_held
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-2-entry
related_docs:
  - bcf-oagis-broad-buildout-blueprint-2026-06-23.md
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
  - bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-1-c2-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-1-c5-closure-checkpoint-2026-06-25.md
  - bcf-c3-c6-projection-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
  - DEC-fb0b12
---

# BCF × OAGIS Pass-2 Entry Note (2026-06-25)

> **Purpose.** DEC-f94895 authorized the layer-first model and set Pass-2 budget caps but explicitly said "does NOT start panel execution; separate operator act required" (ADR-f94895.md §"What this recording does NOT do"). This note closes the **execution-trigger gap** for Pass 2: it names the surface, scopes the first wave, adapts the Checker-First Preflight, and names additive halt triggers. **No panel runs are authorized by this note alone.** Wave execution begins only when the operator gives an explicit go.

## 1. Authority + DEC-f94895 carryover

| DEC-f94895 element | Status for Pass 2 |
|---|---|
| §1A layer-first model (Pass 1 C-waves → Pass 2 E-waves → Pass 3 BC-waves) | Adopted; Pass 2 = E-waves |
| A5 caps: Pass 2 (E-waves) $40 / 80 panel calls | Unchanged; this note operates inside that envelope |
| A5 program caps: $400 total / 1,216 panel calls / 180 s per row / 24 h wall time | Unchanged |
| A3 halt rules (22 fatal-stop triggers per blueprint §8.4) | Unchanged; this note adds Pass-2-specific triggers (§6 below) |
| DEC-ec341c admission_scope rubric (cross_function / function_scoped / industry_scoped) | Unchanged; applies to entities as well as characteristics |
| DEC-fb0b12 E1–E6 amendment doctrine | Unchanged; applies to entity definitions if amended |
| Writer guard at `bc-core/src/registry/registry-authoring-panel/registry-authoring-orchestrator.service.ts:293` | Unchanged; the seatbelt |

This note **does not** authorize any cap or rule change. It triggers Pass-2 execution under the existing DEC-f94895 envelope.

## 2. Pass-2 surface (verified)

Pass-2 entity admission uses the **same** B6/F4 registry-authoring surface as Pass-1 characteristic admission. No new endpoint required.

| Layer | Path | Notes |
|---|---|---|
| HTTP | `POST /api/bcf/registry-authoring-runs` with `operation: 'createEntity'` | Same endpoint Pass 1 used with `operation: 'createCharacteristic'`. DTO at `bc-core/src/registry/registry-authoring-panel/registry-authoring-run.dto.ts:51` |
| bc-core run service | `bc-core/src/registry/registry-authoring-panel/registry-authoring-run.service.ts:62` | Sends bounded packet to bc-ai then runs orchestrator |
| bc-ai panel | `POST /api/ai/suggest/registry-authoring` | Same surface for both characteristics and entities; client at `bc-core/src/registry/registry-authoring-panel/registry-authoring-panel.client.ts:40` |
| bc-core orchestrator | `bc-core/src/registry/registry-authoring-panel/registry-authoring-orchestrator.service.ts:150` | `createEntity` is `registry_create/entity` (low-risk action_code). Orchestrator: issue cert → call F3 `createEntity` → fast-lane publish active |
| F3 writer | `bc-core/src/registry/concept-registry/registry-authoring.service.ts:366` | Cert-gated; name-conflict-checked |
| bc-ai prompts + validators | Support `createEntity` including duplicate/homonym guard | Verified |

**Implications:**
- Same packet shape as Pass 1 — `proposedName` (entity canonical_name), `definition`, `candidateEvidence`. The validator checks duplicate/homonym at bc-ai; F3 also runs name-conflict-check at write time.
- **Same transport pattern.** The Pass-1 C5 transport script (`scripts/_pass1-c5-transport.mjs`) can be parameterized for Pass-2 entity packets by setting `operation: 'createEntity'`.
- **Same Cognito token + roles** (platform_admin already authorized).
- **Difference from characteristic admission:** `createEntity` fast-lane publishes to **active** (not draft). This is a meaningful state difference — Pass-2 entity admissions land at `lifecycle_state='active'` and immediately enable Pass-3 BC bindings. Pass-1 characteristic admissions landed at draft pending activation. The fast-lane is appropriate for entities because entity identity is governed by canonical_name + definition; once approved, there is no "draft entity" semantic to wait on.

## 3. E1 scope: Item only

First Pass-2 wave is **one entity**: Item.

| Field | Value |
|---|---|
| Entity | Item |
| A0.5 slice | master-data-root |
| AMBER class | yes |
| Sole entity in slice | yes (master-data-root has only this entity per A0.5 §5) |
| Pass-1 BC unlock estimate (per Session 3 projection) | ~17 BC across C3 / C4 / C6 currently slice-blocked |
| Existing-substrate duplicate? | None — substrate has Customer Invoice Line Item (transactional) but no top-level Item master-data entity |
| Identity-bearing reference graph | Item is master-data-root; references nothing for its identity → acyclic by construction |

**Rationale for one-entity first wave** (operator-stated; this note records the choice):
- Item is one AMBER entity in its own slice; cleanest minimum-1 test of the Pass-2 surface end-to-end.
- Highest per-entity BC unlock (17 BC for 1 entity) — better signal-to-noise than starting with a 3-entity batch.
- If E1 succeeds cleanly, E2 (asset-maintenance trio) becomes the first multi-entity batch — that wave validates the batching pattern.
- If E1 surfaces an issue with the surface, schema, or doctrine, only one row is at risk.

## 4. Subsequent waves (named only — no execution yet)

For planning continuity. Each wave requires its own operator go-signal.

| Wave | Slice | Entities | Class | Per-wave estimate (Pass-1 BC unlock) |
|---|---|---|---|---:|
| **E1** | master-data-root | Item | 1 AMBER | ~17 BC |
| **E2** | asset-maintenance-simple | Asset + Equipment + Maintenance Order | 3 AMBER | ~34 BC |
| **E3** | master-data | Business Partner + Cost Centre + Location + Org Unit + Party + Price List + Price List Item + Project | 8 AMBER | ~22 BC |
| E4 | logistics | Delivery + Pick List + Pick List Line + Shipment Request + Shipment Unit + Three-Way Match Document + Three-Way Match Document Line | 7 AMBER | ~11 BC |
| E5 | quality-simple | Certificate + Corrective Action + Nonconformance Notification + Nonconformance Notification Line + Test Method | 5 AMBER | ~9 BC |
| E6 | production-simple | BOM + Manufacturing Process + Production Confirmation + Production Schedule + Routing + Work Centre + Work Order | 7 AMBER | ~12 BC |
| E7 | procurement-transactional | Outline Agreement + Outline Agreement Line + Purchase Requisition + Purchase Requisition Line + Quote + Quote Line + RFQ + RFQ Line | 8 AMBER | small (per A0.5 §5) |
| E8 | inventory-composite (AMBER subset) | Inventory Count + Inventory Count Line + Inventory Movement + Inventory Movement Line | 4 AMBER | small |
| E9 | workforce | Employee | 1 AMBER | small |
| E10 | asset-maintenance-simple residual / reference-warranty-budget | Asset (covered E2) + Budget Ledger Entry + Budget Ledger Entry Line + Warranty Claim | 3 AMBER | small |
| **RED held** | composite-identity slices | Bill of Materials Line / Inspection Lot / Inventory Position / Maintenance Order Operation / Operation / Test Result / Work Order Operation | 7 RED | **out of scope for AMBER waves** — separate operator decision packets per A0.5 §7 (identity-bearing reference graph + BCR §4 acyclicity + operator name) |

Total AMBER entities across E1–E10: ~47 (matches A0.5 §5 count). Total RED: 7 (separate packets, not in this wave plan).

**Sequencing principle:** ranked by per-entity BC unlock + cluster cohesion. E1 single-entity proves the surface; E2 batch proves the trio pattern; E3 batch proves the larger 8-entity pattern. After E3, the unlock-per-entity drops; remaining waves (E4–E10) are smaller-value and can be reordered by operator priority.

## 5. Checker-First Preflight adapted to entities

Same shape as Pass 1 (per `feedback_checker_first_preflight.md`). 5 questions per entity, applied **before** any panel call. Default disposition under uncertainty: hold for operator framing, not transport.

| # | Question | Entity-specific guidance |
|---|---|---|
| **A** | Does substrate already have this entity (by canonical_name)? | Strict equality + close-synonym check against the active entity list. For Item: check substrate's 26 active entities — none match "Item" as a top-level master-data entity (Customer Invoice Line Item is transactional, distinct). |
| **B** | Is this just a role / scope variant of an existing entity? | Rare for entities (more common for characteristics). E.g., is the proposed entity a sub-type or specialization of an admitted entity that should be modelled as a discriminator field instead of a new entity? |
| **C** | Are dependent identity-bearing characteristics admitted? | Some entities require an identity-bearing characteristic in substrate as a precondition (e.g., a future Lot entity might require "lot identifier"). For Item: no hard dependency — Item is the root, its BCs will bind shared identifier characteristics (admitted in Pass-3 BC-wave). Note: this is different from C5's substrate-collision check; here the precondition is *forward* (does the entity need anything pre-existing?). |
| **D** | Is the identity-bearing reference graph clean (BCR §4 acyclic)? | For AMBER entities: must be acyclic. master-data-root entities are roots by construction. For RED composite-identity entities: **always fails** this check at the AMBER-wave level → routes to separate decision packet per A0.5 §7. |
| **E** | Is the AMBER classification confirmed? | Per A0.5 §5: each entity is listed AMBER or RED. RED → out of scope for this wave; route to operator decision packet. AMBER → proceed to step F. |

**Verdict outcomes** (mirror Pass 1):
- **SURVIVE** → transport for panel (`operation: 'createEntity'`)
- **DOWNGRADE** → reclassify (e.g., as a discriminator field on an existing entity if Q-B fires)
- **HOLD** → defer to a later wave (e.g., dependent characteristic missing per Q-C; route to operator decision packet per Q-D/E for RED)

**Worked example (not executed; surfaces only when E1 wave begins):**
- E1 = Item: A=No (no existing Item entity); B=No (not a role variant); C=No precondition; D=Acyclic (root); E=AMBER ✓ → SURVIVE expected.

The actual Checker-First Preflight on Item runs **after** the operator gives E1 go-signal, not now.

## 6. Pass-2 specific halt triggers (additive to DEC-f94895 A3)

Additive to the 22 fatal-stop triggers in blueprint §8.4. Pass-2 specific:

| Trigger | Effect |
|---|---|
| BCR §4 acyclicity failure on identity-bearing reference graph | Halt; raise to operator. Already implied by DEC-f94895 A3; restated here for explicit Pass-2 application. |
| RED composite-identity entity accidentally entered the AMBER wave | Halt; route to separate operator decision packet. Pre-transport Checker-First Q-E should catch this; this trigger is the safety net. |
| Required identity-bearing characteristic missing from substrate at transport time | Halt wave for that entity; defer to a later wave after the characteristic is admitted. Pre-transport Checker-First Q-C should catch this. |
| F3 `createEntity` returns name-conflict (homonym at write time) | Halt that entity; re-run pre-transport substrate-collision check; if collision is real, surface to operator (it should have been caught by bc-ai duplicate-guard pre-transport, so a write-time conflict is itself an anomaly). |
| `createEntity` orchestrator post-panel fast-lane fails between cert + F3 + activation | Halt; substrate may be in mid-transition state (cert exists but no entity row, or entity row at draft awaiting activation). Surface for operator inspection. |

DEC-f94895 A3's existing triggers (service unavailability, auth fail, schema fail, budget cap, foundation invariant violation, forbidden token, source-field copy, etc.) apply unchanged.

## 7. Non-actions for this note

The following are explicitly **not** performed by writing this note:

- No panel call. No `POST /api/bcf/registry-authoring-runs` invocation.
- No bc-ai panel run.
- No cert mint.
- No F3 `createEntity` call.
- No substrate write. Substrate verified unchanged at the C5 closure-checkpoint state: 26 active entities / 62 active characteristics / 20 draft characteristics / 194 active value BCs.
- No ADR authoring (DEC-f94895 already authorizes the program; this is an entry note, not a new decision).
- No DDL changes.
- No bc-core or bc-ai code changes.
- No changes to the BC-coverage ledger.
- No changes to A0.5.

## 8. Next gate (post-note workflow)

After this note is committed and the operator gives an explicit go for E1:

1. **Open a Session for E1 execution** (separate from this note-writing session).
2. **Run the entity Checker-First Preflight on Item** locally — write the rejection case before the admission case, surface to operator.
3. **Operator approves the Item packet** (or downgrades / holds).
4. **Author the Item packet** (proposedName="Item", definition, candidateEvidence with standards anchor — likely UN/CEFACT Item Master conventions, OAGIS item-master noun, ISO product-identifier schemes).
5. **Pre-transport substrate-collision check** — pg_query for any active entity with `canonical_name='Item'`. Expected: 0.
6. **Transport** via the parameterized C5 transport script with `operation: 'createEntity'`. Concurrency 1 (single entity in this wave). Per-row latency cap 180 s.
7. **Panel outcome**: APPROVE_FOR_DRAFT or PARK. If APPROVE, the orchestrator's fast-lane publishes Item active.
8. **Verify substrate post-transport**: 27 active entities (was 26) if approved; characteristic and BC counts unchanged.
9. **Write E1 closure-checkpoint** following the C1+C2+C5 shape.
10. **Open PRs** (barecount-devhub for the E1 transport script + outcomes; bc-docs-v3 for the closure-checkpoint). NOT merged.

**Out of scope for E1 specifically:**
- Pass-3 BC binding work on the newly-admitted Item entity (those are Pass 3, not Pass 2).
- Retrofitting C3/C4/C6 slice-blocked rows that the Item admission unlocks — happens after Pass 2 completes (or operator decides mid-Pass-2 to retrofit).

## 9. Discipline state at note-write time

- 0 panel calls.
- 0 substrate writes.
- 0 code edits.
- 0 ADR authoring.
- 0 changes to BC-coverage ledger.
- 0 changes to A0.5.
- Substrate verified at session-open state: 26 active entities / 62 active characteristics / 20 draft characteristics / 194 active value BCs (carried from Session 4 closure).
- Branch: `bcf-pass-2-entry-note-2026-06-25` in bc-docs-v3.

Held. Awaiting operator E1 go-signal.
