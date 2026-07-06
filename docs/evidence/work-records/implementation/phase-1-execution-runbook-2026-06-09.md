---
title: Phase-1 Execution Runbook — prove one AR metric end-to-end on the clean chain
description: The grounded, step-by-step runbook to produce one trustworthy AR Metric Snapshot for the fresh pilot1 tenant (TSK-f77fd2), per DEC-b54a43 (D437). Post the 2026-06-09 data reset the contract chain is greenfield, so this starts with re-authoring (OC+CC) + re-materialization from the surviving MCF authority (MCV b1933c30), then the live run. HELD for operator (first run watched).
status: active
date: 2026-06-09
project: bc-core
domain: contracts
subdomain: core-chain-consolidation
focus: runtime
governs: DEC-b54a43 (D437)
---

# Phase-1 Execution Runbook — one AR metric, end-to-end

> **Goal (TSK-f77fd2):** one **trustworthy** AR Metric Snapshot for the fresh **`pilot1`** tenant, whose readiness verdict is its **M13/M14 evidence** — produced by the four runtime boundaries from clean SDG source data through the governed chain. **Specimen = ARPI** (`average_revenue_per_invoice`).
>
> **⚠ POST-RESET STATE (data reset EXECUTED 2026-06-09 — see `core-chain-data-reset-dbcp-2026-06-09.md`).** The contract chain is now a **clean greenfield**: the ARPI `OC`/`CC` and the materialized MC `98ae46ed` were **wiped**. What survives: the `mcf` MCV **`b1933c30`** (active+current, ARPI authority), the 30k SC/AC catalog, BCF `concept_registry` (108 BC), and runtime readers/flavors (65, now **unbound** — `observation_contract_id = NULL`). So this runbook now begins with **re-authoring** (OC+CC) and **re-materialization**, *then* the live run.
>
> **✅ PROGRESS 2026-06-10 — contract+metric chain REBUILT (steps 1–3 done):** `pilot1` provisioned (`tbc_pilot1_dev`, registry clean); OC `oc__customer_invoice_arpi_slice_type_sd_s_map` **active** (`019eaf2d`); CC `cc__customer_invoice_arpi_slice` **active** (`019eaf31`); ARPI MC **materialized** (`f3c5fe87`, `metric_definition_id=NULL` → mcf-governed) from kept MCV `b1933c30`, binding the re-authored CC; `contract.metric_contract` total = **1** (pristine). OC/CC are byte-exact reproductions of the pre-reset shapes (recovered from the golden snapshot). Materializer env-gate re-closed (bc-core in normal state).
>
> **HELD for the operator's first run** — only the live runtime (steps 4–8: reader connection → SDG emit → 4 boundaries → ARPI snapshot) remains; that's where surprises live, best done watched.

## Grounded facts (post-reset, 2026-06-09)
- **Contract chain is EMPTY (greenfield).** OC/CC/MC/mappings all 0. The ARPI OC+CC must be **re-authored** fresh at 1.0.0 via the governed `ContractService` path, BCF-bound (D430/D431 concept gates).
- **ARPI authority survives in MCF:** `mcf` MCV **`b1933c30`** (active+current) + its parent MC. Re-materialize from it — the old projection `98ae46ed` was wiped. **Verify at re-materialization:** the kept MCV's immutable binding snapshot must re-bind to the freshly authored CC — bridge **Guard B** re-validates; if it fails, a fresh MCF authoring pass is required (don't force it).
- **ARPI runtime need:** Canonical Objects for the re-authored **`cc__customer_invoice_arpi_slice`** (fields **`amount`** + **`document_number`**). Runtime reads `contract.metric_contract` (the re-materialized projection), not `mcf.*`.
- **Source side:** 25 readers / 61 flavors / 47 bindings survive; **0 connections**, and the **65 reader_flavors are now unbound** (`observation_contract_id = NULL`) — they must be re-bound to the freshly authored OC, then a connection wired.
- **Services (last up 2026-06-09):** bc-core 3100, bc-ai 4300 (10 models), bc-sdg OData 4200. ⚠ the reader chain may target the **6100 in-memory** sim (bc-sdg dual-simulator note) — confirm before wiring the connection.

## Steps (post-reset sequence — re-author → re-materialize → live run)
**0. Prereqs** — bc-core (3100), bc-ai (4300), bc-sdg up (restart if needed post-reset; bc-core reads the now-empty `contract.metric_contract` — harmless). Confirm the BCF concepts the ARPI slice needs (Customer Invoice × amount, × document_number) exist + are active in `concept_registry` (108 BC preserved) before re-authoring.

**1. Provision `pilot1`** — provision `tbc_pilot1_dev` via `scripts/provision-apex.ts` / `schema-provisioner.service` with slug **`pilot1`** + register the tenant. *(Additive; reversible by dropping it.)*

**2. Re-author ARPI OC + CC** *(NEW — the chain was wiped)* — via the governed `ContractService` path: author an Observation Contract + a Canonical Contract `cc__customer_invoice_arpi_slice` (fields `amount`, `document_number`) at 1.0.0, BCF-bound, activated through the D430/D431 concept gates; bind to the surviving SC/AC for the invoice source.

**3. Re-materialize the ARPI MC** — from `mcf` MCV `b1933c30` via `McfArpiMaterializationWriterService`. **Guard B re-validates** the fresh CC binding; if it fails, stop and run a fresh MCF authoring pass (don't force).

**4. Reader connection → bc-sdg** — re-bind the AR reader_flavor's `observation_contract_id` to the fresh OC, then configure a `runtime.connection` pointing at the correct bc-sdg endpoint (**6100 vs 4200 — confirm**). The source wiring.

**5. SDG emit** — bc-sdg emits a small, coherent Customer-Invoice dataset (the SAP table the SC reads) carrying `amount` + `document_number`, scoped to `pilot1`.

**6. Run reader → Admission → Canonical** — execute the reader (`POST /execute-reader/:readerId`) → Source Objects (`fact.so_*`); auto-resolve (D336) or `OrchestratorService` → Canonical Objects for `cc__customer_invoice_arpi_slice` (`fact.co_*`). + Evidence/Lineage.

**7. Metric eval** — auto-trigger (reader-driven / ledger-dispatch) OR force via `POST /api/admin/test-bench/evaluate-mc-for-tenant` (the **re-materialized** MC, `pilot1`) → ARPI **Metric Snapshot** + `progression.metric_evaluation` + Evidence/Lineage.

**8. Verify trustworthiness** — (a) the snapshot value is correct vs the SDG inputs; (b) its Evidence/Lineage ties back SO→CO→source; (c) readiness verdict via `McfReadinessBridgeService` / chain-detail = **mcf-governed (M13/M14)**, not D305. That triad = a *trustworthy* AR metric.

## Gates & rollback
- One-then-many: prove this ONE metric fully before any second.
- No raw DB inserts — only governed endpoints (readers, orchestrator, test-bench).
- Rollback: drop the fresh tenant DB (no other state depends on it); no platform mutation needed.

## Open items to resolve at execution (with operator)
1. bc-sdg endpoint for the reader connection (6100 in-memory vs 4200 OData). **← the load-bearing first-run unknown.**
2. **Re-author scope** — confirm the BCF concepts (Customer Invoice × amount, × document_number) exist + are active before authoring the OC/CC; decide which surviving SC/AC to bind.
3. ~~Use existing MC or re-materialize?~~ **RESOLVED — `98ae46ed` was wiped in the reset; re-materialize fresh from MCV `b1933c30`** (Guard B re-validates the fresh CC binding).
4. SDG dataset shape + size for a clean, verifiable ARPI value.

## Pointers
- Golden path: `core-chain-golden-path.md` · ADR: `ADR-b54a43.md` (DEC-b54a43/D437) · Reset: `core-chain-data-reset-dbcp-2026-06-09.md`
- Tasks: TSK-f77fd2 (this proof) · TSK-20f5e1 (reset)
