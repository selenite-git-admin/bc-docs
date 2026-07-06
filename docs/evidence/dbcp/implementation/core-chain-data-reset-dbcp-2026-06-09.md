---
title: Core-Chain Data Reset DBCP (dev greenfield) — EXECUTED 2026-06-09
description: The keep/delete/provision plan for the dev-phase data reset under DEC-b54a43 (D437) / TSK-20f5e1. EXECUTED 2026-06-09 under operator GO (4 decisions + GO-with-metric_definition). Records the actual FK-safe scope (expanded into metric.* spillover + the metric_definition legacy closure) and post-reset verification.
status: active
date: 2026-06-09
project: bc-core
domain: contracts
subdomain: core-chain-consolidation
focus: schema
governs: DEC-b54a43 (D437)
---

# Core-Chain Data Reset DBCP — EXECUTED 2026-06-09

> **EXECUTED 2026-06-09** under explicit operator GO. Decisions locked: ① full-wipe + re-author all · ② delete + re-materialize ARPI MC `98ae46ed` from kept MCV `b1933c30` · ③ drop both tenant DBs · ④ slug `pilot1`; plus opt-in GO to also wipe `metric.metric_definition`. Golden snapshot taken + verified **first** (736 MB `pg_dumpall` → `docker/redesign/golden-snapshot-pre-reset-2026-06-09.sql`, exit 0, 0-byte stderr, "cluster dump complete"). Executed SQL: `docker/redesign/reset-wipe-platform-2026-06-09.sql` — **atomic** (`BEGIN…COMMIT`, `ON_ERROR_STOP=1`); **every DELETE count matched the planned count.** **Dev-only** — Invariant III governs prod, not dev historical cleanup.
>
> ### Actual executed scope (FK-verified against live `pg_constraint`; larger than the original §2 plan)
> - **`contract.*` → 0:** metric_contract 781 · metric_contract_version 1023 · observation_contract 64 · observation_contract_version 155 · observation_field_map 455 · canonical_contract 57 · canonical_contract_version 84 · canonical_mapping 36 · canonical_mapping_version 82 · chain_status 540 · chain_trace 800 · l_node_semantic_verdict 202 · l_node_semantic_trace 25 237 · mc_integrity_state 268.
> - **`metric.*` spillover → 0** (FK-blockers that had to go to release the contract wipe): metric_binding 1133 · mc_dependency 1133 · metric_contract_version_activation_log 1656.
> - **`metric.metric_definition` closure → 0** (opt-in "fuller greenfield"; verified self-contained legacy, ZERO mcf/seed/MLS/readiness coupling): metric_definition 1241 · metric_formula 1216 · metric_formula_variable 4226 · metric_formula_verification 8 · metric_knowledge 1241 · metric_enrichment_job 1141 · lifecycle_event_log 3951 = **13 024**.
> - **`runtime.reader_flavor`:** 65 rows **KEPT**, `observation_contract_id` unbound → NULL (re-bind to fresh OCs after re-author). Nullable column; rows preserved.
> - **Tenant DBs dropped** (`WITH FORCE`): `tbc_apex_dev`, `tbc_sandbox1_dev`. Only `bc_platform_dev` remains.
> - **Trigger note:** `trg_cv_immutable` (on every `*_version`) fires on UPDATE only — DELETE unaffected; no trigger disable needed.
>
> ### Post-reset verification (read-only, immediately after)
> - All wiped tables = **0** ✓.
> - **PRESERVED:** source_contract **30 368** · admission_contract **30 367** · `mcf.metric_contract` **7** · mcf active+current MCV **1** (ARPI `b1933c30`) · `mcf.seed_metric` **12 501** · `concept_registry.business_concept` **108** · `runtime.reader_flavor` **65** (oc_id NOT NULL = **0**) ✓.
>
> ### Remaining (Phase-1 build, not part of this destructive reset)
> Provision fresh `tbc_pilot1_dev`; re-author ARPI OC+CC at 1.0.0 (BCF-bound); re-materialize MC from MCV `b1933c30`; run the chain to a trustworthy ARPI snapshot. **Rollback for the entire reset = restore from the golden snapshot.**
>
> ---
> *The sections below are the original pre-execution plan, retained as the decision record.*

## 0. Golden snapshot (step 1 — MANDATORY, non-destructive)
```
docker exec bc-postgres pg_dumpall -U barecount > <backups>/golden-snapshot-pre-reset-2026-06-09.sql
# verify file size > 0 and restorability before ANY delete
```
Rollback for the entire reset = restore from this file.

## 1. KEEP (do not touch)
- `concept_registry.*` — BCF vocabulary (103 BCs, 25 chars)
- `master.*` — dimensions (fiscal/date/currency/etc.)
- `contract.source_contract(_version)` + `contract.admission_contract(_version)` — the ~28k SC/AC SAP catalog
- `mcf.*` — metric authoring machinery + `mcf.seed_metric` reservoir (12,501)
- `runtime.*` — readers/flavors/bindings (25/61/47)
- **ALL authoring services + UI** — mark, don't delete (separate tasks TSK-a6502d / TSK-7a2699 / TSK-c6f0be)

## 2. DELETE / RESET — platform DB `bc_platform_dev`
| Target | Rows | Action |
|---|---|---|
| `contract.metric_contract` + `_version` (legacy corpus) | 781 / 1023 | **DELETE all** — re-materialize the one AR MC fresh from its active `mcf` MCV (bridge proven) |
| `contract.chain_status`, `chain_trace`, `l_node_semantic_verdict`, `l_node_semantic_trace`, `mc_integrity_state` | 540 / 800 / 202 / 25237 / 268 | **DELETE** — status sprawl, recomputable |
| `contract.observation_contract(_version)`, `canonical_contract(_version)`, `canonical_mapping(_version)`, `observation_field_map`, `cc_field_mapping` | 61/151 · 56/83 · 35/55 · 340 · — | **RE-AUTHOR fresh at 1.0.0** (see §5 open decision — keep the AR slice or full re-author) |

## 3. DROP tenant DBs + provision fresh
```
DROP DATABASE tbc_apex_dev;       -- untrusted (frozen 2026-05-11), useless
DROP DATABASE tbc_sandbox1_dev;   -- untrusted
# then provision ONE fresh pilot tenant DB from canonical DDL:
#   scripts/provision-apex.ts  (or schema-provisioner.service) with a fresh slug
```

## 4. Rollback
Restore `bc_platform_dev` (+ tenants if needed) from the §0 golden snapshot. Drop the fresh tenant DB if mis-provisioned (no other state depends on it).

## 5. OPEN DECISIONS for the operator (resolve before execution)
1. **ARPI materialized row (`98ae46ed`)** — keep as the proof specimen, or delete-all + re-materialize from `mcf` MCV `b1933c30`? *Recommendation: delete-all + re-materialize (clean slate; bridge is proven).*
2. **Curated OC/CC** — full re-author, or **keep `cc__customer_invoice_arpi_slice`** (already D430-governed on BCF; ARPI's primary CC, fields `amount`+`document_number`) and reset only its versioning? *Recommendation: keep the AR slice, reset versioning — it's already on the clean path.*
3. **Fresh tenant slug** — name for the new pilot tenant (e.g. `pilot1`).

## Grounded facts (read-only, 2026-06-09, while drafting)
- ARPI runtime need: COs for `cc__customer_invoice_arpi_slice` (fields `amount`, `document_number`).
- Source side: 25 readers / 61 flavors / 47 bindings exist, **0 connections** — no live source wired yet (a connection to bc-sdg is needed for the run — see the Phase-1 runbook).
