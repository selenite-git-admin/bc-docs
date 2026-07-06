---
title: D429 Step-5 — ARPI Materialization Arc Closeout
description: Closeout record for the D429 Step-5 (D428 §9 materialization-resume) ARPI slice, completed at the platform-readiness layer. The clean active ARPI MCV b1933c30 was materialized once into the legacy contract.metric_contract* runtime store as MCF-governed legacy MC 98ae46ed (active, metric_definition_id NULL, lineage note mcf-step5-writer); its M13/M14 evidence is surfaced via a read-only readiness bridge (DEC-7ab22b/D436). Records the final status, exact substrate state, the three-PR build, Track 1 complete vs Track 2 and Bar-2 open, the readiness-bridge regression-and-fix, and the held boundary (no runtime evaluation, no tenant binding). Record of completed work; authorizes nothing further.
status: complete
date: 2026-06-09
project: bc-core
domain: metrics
subdomain: metrics/mcf-materialization
focus: step5-materialization-closeout
governs: DEC-7ab22b (D436 S3 lock — implemented) · DEC-61f7c8 (D428 single clean published store) · DEC-c3e57f (D422 MCF) · DEC-957fb0 (D434 editorial-rebind evidence)
change_record: CHG-10d095 (TSK-0ba31e)
---

# D429 Step-5 — ARPI Materialization Arc Closeout

> **What this is.** A record of completed, live, governed work — not authority and not an instruction. The clean active ARPI metric-contract version was materialized once into the legacy runtime store as an MCF-governed metric, and its governance evidence was made honestly surfaceable through a read-only readiness bridge. It authorizes nothing further. The remaining frontier (runtime evaluation, tenant binding, fiscal calendar) is **Bar-2** and is explicitly left open. Change record: **CHG-10d095** (`TSK-0ba31e`).

## 0. Final status

> **`materialized, active, MCF-governed, readiness-bridged, not runtime-evaluated`**

| Facet | State |
|---|---|
| Legacy ARPI MC | `98ae46ed-3c3f-4a31-8cee-4adb762717ab` — **active**, `metric_definition_id IS NULL`, `header.lineage.note='mcf-step5-writer'` |
| Active version | `1.0.0` |
| Source MCF MCV | `b1933c30-c708-4ebe-b2b3-b2a82242f331` — **active / is_current** |
| Governance | **MCF M13/M14** (DEC-7ab22b / D436), NOT legacy D305 chain-status |
| Readiness surface | read-only bridge on bc-core `main c77d998` — chain-detail returns **200** |
| Runtime / tenant | **none** — not runtime-evaluated, not tenant-bound (Bar-2) |

## 1. Why the arc existed

D429 Step-5 resumes the D428 §9 MCF→legacy materialization for one specimen. ARPI (`average_revenue_per_invoice`) was the right first metric: the 2026-06-07 synthesis proof (`mcf-arpi-contract-json-synthesis-proof-2026-06-07.md`) blocked ARPI's evaluable envelope on superseded BCF bindings; the editorial-rebind arc (`mcf-arpi-editorial-rebind-arc-closeout-2026-06-09.md`, CHG-3daea8) cleared that gap, leaving exactly one clean active ARPI MCV (`b1933c30`) with active concept bindings the D430 resolver maps to the active CC-v2 field. With the door unblocked *for ARPI only*, Step-5 was the read-before-write proof (Slice 0, TSK-a8bedb) followed by the one-shot writer (this task, TSK-0ba31e).

## 2. What was built (three SHA-pinned PRs to bc-core `main`)

| Layer | PR | Merge | Substance |
|---|---|---|---|
| Schema | **DDL CHG-3374d9** (TSK-f06131) | — | `contract.metric_contract.metric_definition_id` made **NULLable** (permissive; an MCF-materialized MC has no legacy definition). |
| Writer | **#251** | `ed6c6f0` | ARPI-only `synthesizeContractJson` + materialization writer, with **Guard A** (source MCV `active` + `is_current`) and **Guard B** (resolved CC-v2 declares `posting_date_field=document_date`). D432 legacy-authoring guard recognises this as the authorized MCF writer path. |
| Readiness (Track 1) | **#252** | `75c7387` | Read-only `McfReadinessBridgeService` surfacing M13/M14 evidence + writer-verdict honesty (`readinessMode:'mcf-governed'`, dropped hardcoded `chainVerdict:'complete'`). |
| Readiness fix | **#253** | `c77d998` | M13 read keyed by `metric_contract_version_uid` (the PE-result table's real key) — fixes a chain-detail **500** the DB-mocked tests missed. |

The single non-dry-run writer call created legacy MC `98ae46ed` and was **not** re-run (D432 guard + idempotency).

## 3. Exact substrate state (verified read-only, main `c77d998`)

| Object | Value |
|---|---|
| Active ARPI legacy MC | `98ae46ed-3c3f-4a31-8cee-4adb762717ab` (active, `metric_definition_id` NULL, 1 active version `1.0.0`) |
| Lineage | `header.lineage[0]` = `{ note: mcf-step5-writer, relation: derives_from, from_version: 1.0.0, from_contract_id: b1933c30 }` |
| Source MCF MCV | `b1933c30-c708-4ebe-b2b3-b2a82242f331` — `governance_state_code=active`, `is_current=true`, parent MC `7596213d` |
| M13 PE evidence | **20 total — 18 PASS, 2 OPERATOR_REVIEW** (Model A / D435: OPERATOR_REVIEW is PASS-equivalent at platform M13/M14) |
| Verifier | `verdict_code=pass`, `stale_fixture_flag=false` |
| M14 activation cert | `a2586f9b-de56-448f-8318-b089c381e77a` — `metric_transition`, `to_state_code=active` |
| `contract.chain_status` for ARPI | **0** (none synthesized) |
| `l_node_semantic_verdict` for ARPI | **0** (none synthesized) |
| `contract.metric_contract_version` total | **1023** (unchanged — no new versions) |
| Tenant facts / `metric_snapshot` | **none** (no tenant binding, no runtime evaluation) |

## 4. Track 1 — COMPLETE (readiness bridge)

**DEC-7ab22b / D436 (S3 lock) is IMPLEMENTED.** MCF-materialized metrics (`metric_definition_id IS NULL` + `mcf-step5-writer` lineage) are governed by MCF M13/M14 evidence; legacy D305 readiness is reported **`MCF-governed / legacy-readiness N/A`** — never inferred-complete, never false-RED via the legacy CF/BF/canonical_mapping L1–L8 walk. **Option A (synthesize a `chain_status` row) was rejected** — the legacy walk targets the wrong (v1-concept) registry and would render a false RED; that would be lower-layer compensation for an upper-layer semantic boundary (Foundation Invariant VI: evidence is emitted, not inferred).

Read-only verification on `c77d998`:

- `GET /api/registry/metric-readiness/chain-detail/98ae46ed…` → **200**, `readinessMode=mcf-governed`, `legacyReadiness=na`, `sourceMcvUid=b1933c30`, `mcvGovernanceStateCode=active` + `mcvIsCurrent=true`, `m13={20/18/2}`, `verifier={pass, staleFixture false}`, `m14={a2586f9b, active}`.
- **mc-list** shows ARPI `chainVerdict=mcf-governed`, `readinessMode=mcf-governed`, `lifecycleStage=platform_ready`.
- **orphan-contracts** excludes ARPI.
- A legacy `metric_definition`-backed metric still returns normal **D305** readiness (`readinessMode=d305`, no `mcfReadiness`).

**Regression-and-fix note (kept for the record).** PR #252's bridge shipped a chain-detail **500**: `readM13Summary` queried `mcf.metric_publication_eligibility_result.metric_contract_uid` (a non-existent column; PE results are version-keyed). The unit tests mocked `db.execute` by SQL text, so the column drift passed CI and was caught only by post-merge live verification. PR #253 keyed the read by `metric_contract_version_uid` (passing the source MCV uid). Lesson logged: DB-mocked unit tests do not catch column/relation drift — live verification is the gate.

## 5. Boundary held — no materialization beyond the contract layer

- **No runtime evaluation.** No `progression.*` / `fact.ms_*` / `metric_snapshot` rows. Platform `mcf.*`/`contract.*` transitions do not evaluate metrics into tenant facts.
- **No tenant binding.** ARPI is platform-level only; no `tenant.contract_binding`.
- **No chain-status / l-node synthesis.** Per DEC-7ab22b.
- **D428 §9 guardrail intact** otherwise — this is the *first sanctioned* `contract.metric_contract*` write under the single-clean-published-store amendment (DEC-61f7c8 / D428), scoped to one specimen.

## 6. Open — explicitly NOT part of this closeout

| Track | Item | Status |
|---|---|---|
| **Track 2** | `TSK-d67c82` — inert ContractService legacy activation gates (`@Optional()` `chainStatusService` + `mls14Gate` null at runtime; DI-cycle probe + MlsModule wiring) | **OPEN** (planned). Governed by DEC-7ab22b §context. The ARPI write's absence of a chain-status/l-node verdict is an evidence-emission gap (resolved by Track 1), not an ungated activation — the supply-chain gate was applied at write time via Guard B + D430. |
| **Bar-2** | Tenant contract binding · fiscal calendar seeding (D363/D364/D365) · tenant runtime evaluation → first ARPI tenant facts | **OPEN**. This is the next frontier; the "not runtime-evaluated" half of the status string. The materialization door is open for ARPI, but no evaluation has run and none is authorized by this closeout. |

## 7. Provenance

- Decision: **DEC-7ab22b / D436** (implemented) · store amendment **DEC-61f7c8 / D428** · MCF authority **DEC-c3e57f / D422**.
- DBCPs: `d429-step5-metric-definition-id-nullable-dbcp-2026-06-09.md` · `d429-step5-arpi-materialization-writer-dbcp-2026-06-09.md` · `mcf-readiness-bridge-writer-honesty-dbcp-2026-06-09.md`.
- Study: `mcf-materialized-metric-readiness-visibility-study-2026-06-09.md` (resolved stop-condition S3).
- Predecessor arc: `mcf-arpi-editorial-rebind-arc-closeout-2026-06-09.md` (CHG-3daea8).
- Change record: **CHG-10d095** (`TSK-0ba31e`). DDL change record: **CHG-3374d9** (`TSK-f06131`).
- Merges: DDL CHG-3374d9 · writer **#251** `ed6c6f0` · bridge **#252** `75c7387` · bridge-fix **#253** `c77d998`.
