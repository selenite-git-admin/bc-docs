---
uid: DEC-7ab22b
title: "MCF-materialized metrics governed by MCF M13/M14, not legacy D305 chain_status"
description: "S3 lock: MCF-materialized metrics governed by MCF M13/M14 evidence; legacy D305 readiness reports 'MCF-governed / N/A', not inferred-complete and not false-RED."
status: implemented
date: 2026-06-09T09:32:54.379Z
project: bc-core
domain: metrics
subdomain: metrics/mcf-materialization
focus: governance
---

# MCF-materialized metrics governed by MCF M13/M14, not legacy D305 chain_status

## Context

Per HA-1/D426 the MCF M14 activation surface reads only mcf.* and is the authoritative publication gate; ARPI carries a complete, hash-consistent MCF evidence chain (20 PE rows, passing non-stale verifier, metric_transition cert). The legacy D305 funnel is metric_definition + CF/BF/canonical_mapping based and cannot correctly evaluate a v2-concept-bound MCF metric (S1 probe confirmed the bulk refresh would enumerate the row but render a false RED via the wrong registry). Foundation Invariant VI (evidence emitted, not inferred) requires the verdict be emitted as MCF-governed rather than inferred complete or fabricated via the wrong registry. Resolves stop-condition S3 of study docs/implementation/mcf-materialized-metric-readiness-visibility-study-2026-06-09.md (D429 Step-5 check-5).

## Decision

MCF-materialized metrics — legacy `contract.metric_contract` rows with `metric_definition_id IS NULL` and `header.lineage.note='mcf-step5-writer'` — are governed by MCF M13/M14 evidence (the PE-MC eligibility ledger + the self-verification/verifier result + the M14 activation `certification_record`), NOT by the legacy D305 `contract.chain_status` funnel or the MLS-14 activation gate. Legacy readiness for these rows MUST be reported explicitly as `MCF-governed / legacy-readiness N/A` — never inferred `complete`, and never rendered false-RED by running the legacy L1–L8 chain walk (which targets the CF/BF/canonical_mapping registry, not the v2 concept chain). Do NOT synthesize or write `contract.chain_status` for these rows. The D429 Step-5 ARPI materialization write succeeded and the metric is active; the absence of a chain_status / l_node verdict is an evidence-emission/visibility gap, not an ungated activation — the upstream supply-chain gate was applied at write time via Guard B + D430 (single active CC-v2 + posting_date_field=document_date).
