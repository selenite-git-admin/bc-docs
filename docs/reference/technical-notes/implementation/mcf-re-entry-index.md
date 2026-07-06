---
title: MCF Re-Entry Index
description: One-screen orientation for resuming the MCF M-track without falling into legacy-substrate or M-numbering confusion. Names the canonical authority stack, reconciles M-numbering (build plan is canonical), classifies what is implemented / exploratory / proposed / obsolete, fixes D386/D400/D401 framing, and names the next governed gate. Navigation/orientation index — NOT an authority document.
status: draft
date: 2026-06-06
project: bc-core
domain: contracts
subdomain: catalog
focus: mcf-re-entry
---

# MCF Re-Entry Index

> **What this is.** A navigation index for any session resuming the MCF M-track. It exists because re-entry repeatedly drifted into the legacy metric world (D386 / `contract.metric_contract`) and into divergent M-numbering. **It is NOT an authority document** — authority is DEC-c3e57f + DEC-3f093f/D426 (the store/runtime boundary) + the build plan. Read this first, then the canonical stack.

## 1. Canonical MCF authority stack (precedence order)
| # | Artifact | Role | Status |
|---|---|---|---|
| 1 | **ADR DEC-c3e57f / D422** (`docs/adrs/ADR-c3e57f.md`) | **Foundational MCF ADR = Gate M1.** The authority (10 decisions). | **decided** 2026-05-26 |
| 1a | **ADR DEC-3f093f / D426** (`docs/adrs/ADR-3f093f.md`) | **Decided the metric-contract STORE / RUNTIME boundary** (`mcf.*` canonical; no legacy writes; future `mcf → NEW shadow`). **Store mechanism amended by D428 (below);** D426's runtime-boundary + three-store findings remain in force. | **decided** 2026-06-02 |
| 1a-amend | **ADR DEC-61f7c8 / D428** (`docs/adrs/ADR-61f7c8.md`) | **Amends D426's store mechanism → "clean single published metric-contract store":** `contract.metric_contract*` = single clean published runtime store (MCF materializes after clean-slate adoption); raw PG `mcf.seed_metric` operational reservoir (Mongo/export = preserved upstream seed archive); panel = enricher; legacy archived/exported then wiped under DBCP. | **decided** 2026-06-07 |
| 1b | **ADR DEC-7f9597 / D423** (`docs/adrs/ADR-7f9597.md`) | Execution-discipline stance (no shortcuts / synthetic writes / boundary blurring). **NOT a store-architecture decision.** | decided |
| 2 | **`metric-context-framework-build-plan.md`** (commit `40a9adc`) | **Canonical Gate M0–M20 map.** The M-numbering source of truth. | draft (mechanics) |
| 3 | `metric-context-framework-requirements.md` (`13f9bb6`) | The spec. Ratified-by-reference via M1. ⚠ its **§20 gate table uses divergent numbering, pending sync to the build plan**. | proposed |
| 4 | inventory (`d9b10d2`), gap-survey (`0ba202b`), reservoir/authority addendum (`0e3644b`) | Step-1/2 supporting artifacts | draft |
| 5 | `mcf-legacy-bridge.md` + `errata/MCF-ERR-001.md` | Legacy read-fallback policy (MCF wins) + errata | — |
| 6 | `mcf-m2…m13` closeout docs (`docs/implementation/`) | Per-gate implementation record | — |

## 2. M-numbering — canonical vs historical (the confusion fix)
- ✅ **CANONICAL = build-plan integer gates M0–M20.** Key: M10 verifier · M11 reservoir-ingestion · **M12 = Metric Authoring Panel** · **M13 = PE-MC evaluator** · **M14 = Publication path** · **M15 = Supersession** · M16 console-read · M17 console-authoring · M18 tenant-console · M19 cross-framework · M20 first-metric program.
- 🟡 **HISTORICAL / interstitial = "M12.5"** (materialization). Real work (closeout exists) but a half-label *outside* the integer gate sequence — do not treat it as a canonical gate.
- 🟥 **DIVERGENT / pending-sync = requirements §20 numbering** (there: M10 panel, M11 PE-MC, M12 publication, M13 supersession…). The build plan §3.2 holds the bidirectional map and states §20 is updated to match it. **Always cite build-plan gate IDs, never §20.**

## 3. Status classification
**IMPLEMENTED** (closeout docs + live substrate, 18 `mcf.*` tables):
- M1 ADR (DEC-c3e57f decided) · M2–M5, M7–M11 substrate+services (identity / lifecycle / PE / panel / AST+package-sig / fixture / verifier / reservoir-ingestion) · M12 panel · M12.5 materialization · M13 PE-MC evaluator · **M14 publication (built + run once — ARPI active)**. ⚠ **M6 tenant-binding was SKIPPED** (no `mcf.tenant_binding` table, no closeout).
- Live: `mcf.metric_contract` = **5** (1 active = ARPI, 1 approved, 2 draft, 1 review). Pipeline proven **end-to-end through publication once** (ARPI).
- **D429 Step-5 (ARPI materialization) — COMPLETE at platform-readiness (2026-06-09).** ARPI MCV `b1933c30` materialized once into legacy MC `98ae46ed` (active, `metric_definition_id` NULL, `mcf-step5-writer` lineage) — **MCF-governed** (DEC-7ab22b/D436 **implemented**), **readiness-bridged** (read-only chain-detail 200; M13 20/18/2; verifier pass; M14 cert `a2586f9b`), **not runtime-evaluated, not tenant-bound**. PRs #251 `ed6c6f0` · #252 `75c7387` · #253 `c77d998`; DDL CHG-3374d9. Closeout: `d429-step5-arpi-materialization-closeout-2026-06-09.md` (CHG-10d095). Status: *materialized, active, MCF-governed, readiness-bridged, not runtime-evaluated*.

**EXPLORATORY** (proof, not a program): the 5 MCs are pilot specimens; not a coverage wave.

**PROPOSED / UNIMPLEMENTED — do NOT treat as implementation authority:**
- DEC-c012c0 / D400 (grammar v1.1) — proposed; **not in the engine**.
- DEC-1db1c7 / D401 (open-item canonical) — proposed; Slice 1 **gate-blocked** (`filter_json` + grammar-v1.1-engine gaps, per the receivable-open-item MWR).
- requirements doc — proposed (ratified-by-reference via M1).

**OBSOLETE / SUPERSEDED-IN-APPROACH:**
- **D386 Stage 4/5** balance-engine path (`BALANCE_AS_OF` over snapshots) — **not** the current AR-balance path (that is the D400/D401 canonical-layer approach). D386 **Stage 1 axis + two-gate + Inspector remain valid.**
- Legacy vocabulary **BF/BO/CF/CM** — physically gone (D417/D418, May 2026).
- Legacy metric corpus **`contract.metric_contract`** (780; 778 archived) / `metric_formula` text / `metric_binding` — historical-only/non-authoritative per **D422 Decision 2**; queryable reference, never migrated.
- Dead services: **IntegrityService** (deprecated), **MetricWizardService** (quarantined).
- Session docs `ar-metric-fulfillment-ledger-2026-06-06.md` + `phase-a-coverage-scan-2026-06-06.md` — legacy-engine-framed; **superseded for MCF re-entry** (banners added).

## 4. D386 / D400 / D401 framing (locked)
- **D386 (DEC-952faa, decided)** = `temporality_kind` axis + two-gate + Inspector. **KEEP.** Its Stage 4/5 balance-engine path is **not** the current implementation path.
- **D400 (DEC-c012c0)** = grammar v1.1 (`over_period` / `over_trailing_window`). **Proposed, unimplemented.**
- **D401 (DEC-1db1c7)** = open-item canonical family (`cc__receivable_open_item`). **Proposed, unimplemented, gate-blocked.**
- **Rule:** proposed ADRs are not implementation authority. MCF authority = DEC-c3e57f + the build plan.

## 5. Next gate — BLOCKED on an open store/visibility decision (not a build step)

> ✅ **Gate 0 COMPLETE (2026-06-07)** — merged to bc-core `main` @ `6d8c083` (PR #233, squash). `mcf.seed_metric` is live with **12,501 active seeds** (candidate-source bottleneck resolved: all 12,501 reachable via Postgres now, was 1,241). The candidate reservoir is **Postgres, not Mongo-at-runtime**; seed status is **master-backed** (`master.master_status` context `mcf_seed_metric`, 8 statuses, no table CHECK); `POST /api/mcf/intakes/from-seed` is **rerun-safe** (skips already-ingested seeds). **No legacy wipe, no `contract.*` materialization.** Only 2 seeds are `queued` (live-proof runs: `available_cash_flow`, `absorption_costing_ratio`); the rest `candidate`. DBCP: `mcf-gate0-seed-reservoir-dbcp.md` (status: implemented). **Next:** non-blocking follow-up `TSK-6dda6f` (operator-direct duplicate idempotency) → then the next D428-sequence step (MCF→`contract.*` materialization design) / the store-boundary settlement described below (which remains open).

**Correction (verified 2026-06-07, live DB):** M14 has already **run once** — ARPI (`average_revenue_per_invoice`) is `governance_state_code='active'` (1 `metric_transition` cert + 10 M14 PE rows). "Next gate = M14" is stale.

**Update (2026-06-09) — D429 Step-5 ARPI materialization COMPLETE at platform-readiness.** The store/visibility question below is settled in practice for the first specimen: under **D428 (DEC-61f7c8)** single-clean-published-store, ARPI's clean MCV `b1933c30` was materialized once into legacy MC `98ae46ed` (active, `metric_definition_id` NULL, `mcf-step5-writer` lineage), governed by **MCF M13/M14** (not legacy D305) per **DEC-7ab22b / D436 (implemented)**, and surfaced via a read-only readiness bridge (chain-detail 200; reports `MCF-governed / legacy-readiness N/A`; **no `chain_status`/`l_node` synthesis**). **Not runtime-evaluated, not tenant-bound.** The remaining frontier is **Bar-2** (tenant binding + fiscal calendar + runtime evaluation), not the store-visibility decision. Closeout: `d429-step5-arpi-materialization-closeout-2026-06-09.md` (CHG-10d095). Track-2 (inert ContractService activation gates, `TSK-d67c82`) remains open.

**The real gate is an OPEN architectural decision: the MCF metric-contract STORE / VISIBILITY boundary.** D426 (decided) made `mcf.*` canonical and forbids MCF writing legacy `contract.metric_contract` — but the live runtime evaluates **only** `contract.metric_contract` and MCF has produced **zero** tenant facts. The bridge from MCF-authored contracts to the wired runtime is undesigned. Options under review:
- **A1** — follow D426: expose `mcf.*` via new MCF read APIs/UI; runtime bridge later. *(Visibility only — does not evaluate metrics into tenant facts.)*
- **A2** — follow D426: project `mcf.*` into NEW shadow/read-model tables (NOT live legacy) that the runtime can consume.
- **B** — amend D426: make legacy `contract.metric_contract` the runtime contract store for MCF-authored metrics (reuses the wired runtime; **reverses a decided ADR**; risks re-entangling legacy as active design debt).

**FREEZE (Codex + Claude cross-review, 2026-06-07):** no M14 generalization / M15 / D400 grammar / D401 open-item work until A1/A2/B is settled. This is the track-loss-prevention point.

**Update (2026-06-07) — direction emerging (supersedes the A1/A2/B framing above):** the **candidate-enrichment** fork is resolved — **panel-side enrichment (E2) validated** on a thin seed (see `mcf-enrichment-experiment-2026-06-07.md`). Store direction = **"clean single published metric store"** (Good B clean-slate): raw PG `mcf.seed_metric` operational reservoir (imported from the Mongo/export seed archive) → MCF panel enriches/authors → single clean published `contract.metric_contract*` → existing runtime; legacy Postgres metric data (incl. `metric_knowledge`) archived/exported then wiped. Enacted via the **D426 amendment — DEC-61f7c8 / D428 (decided 2026-06-07)**. **Gate 0 (✅ DONE @ bc-core `6d8c083`, PR #233) = created/imported/wired PG `mcf.seed_metric`** (from the Mongo/export seed archive, with count/hash/sample parity) — the candidate-source bottleneck is resolved: all **12,501** seeds now reachable via Postgres (was 1,241); MCF intake reads Postgres, not Mongo.

After the boundary is settled: M15 supersession → M16–M18 operator console → M19 → M20. Also still unbuilt: **M6 tenant-binding substrate** (skipped), and **service-ification** (MCF not routinely invokable — no UI reads `mcf.*`; legacy `POST` is still the live write path).

## 6. What this index is not
Not authority (DEC-c3e57f + build plan are). Not an implementation instruction. Read-only orientation to stop legacy/numbering drift on MCF re-entry.
