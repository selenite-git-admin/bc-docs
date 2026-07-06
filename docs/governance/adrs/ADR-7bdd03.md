---
uid: DEC-7bdd03
title: "Guard the legacy Metric Contract authoring door (D429 Step 3)"
description: "Block new legacy contract.metric_contract* authoring via a repository-layer refuse-to-author guard (G2 only) at the create choke point; default-blocked, escape = env flag + logged maintenanceApproval/rationale; create-authoring only (activation owned by Step 4); preserve reads, audit-metadata, tests, and the future MCF materialization writer. Door guard, not shape fix. Implementation deferred to a DBCP."
status: decided
date: 2026-06-07T16:44:20.970Z
project: bc-core
domain: contracts
subdomain: contracts/metric
focus: governance
---

# Guard the legacy Metric Contract authoring door (D429 Step 3)

## Context

The legacy Metric Contract authoring path still accepts free co_bindings (free canonical_contract, free fields_used; metric-v1.schema.json:52-66) with no create-time grounding — the root anti-pattern behind the metric smell, whose real shape fix is sequenced upstream as D430 (canonical concept identity) + D431 (observation concept identity). Until those land and the MCF materialization writer is built, the legacy free-shape envelope is still the ONLY metric-authoring shape, so tightening the schema now is premature and would break authoring; the correct Step-3 move is to close the door (block new legacy authoring), not change the shape. A repository-layer guard (not controller-only) is chosen because scripts and seeds call the repo directly, bypassing the API; the repo create method is the true choke point. The env-flag-plus-logged-rationale escape mirrors the Step-1 guard pattern and gives an auditable maintenance path; a DB trigger (G3) is deferred to keep this step narrow. Activation gating is deliberately excluded — it belongs to Step 4 (fail-open activation gates).

## Decision

D429 Step 3: guard the legacy Metric Contract authoring door so no new ungrounded legacy contract.metric_contract* envelopes are created while D430/D431 implementation and the future MCF materialization writer are built. Scope = the guard DECISION only; no code/schema/DB/service change is authorized here; implementation is deferred to a later DBCP. This is a door guard, NOT a shape fix (the shape — free co_bindings — is corrected by D430 + D431 + the future MCF materialization writer).

1. G2 ONLY — a repository-layer refuse-to-author guard at the single legacy Metric Contract CREATE choke point (createMinimalMetricContract + the metric branch of the version create). No G3 DB trigger in this step.
2. Default = BLOCKED. Escape requires an env flag (BCCORE_ALLOW_LEGACY_METRIC_AUTHORING) PLUS an explicit, logged maintenanceApproval/rationale — both, not the flag alone. (Mirrors the D429 Step-1 BCCORE_ALLOW_CONTRACT_BODY_REWRITE pattern, with an added logged rationale.)
3. Block create-authoring ONLY — parent + version creation through the legacy path. Activation is NOT gated here; Step 4 owns activation / fail-open gates (X5/X4).
4. Preserve, explicitly: runtime reads (read path performs no inserts); formula-audit metadata-only UPDATEs; MCF mcf.* writes (HA-1, different schema); the future MCF->contract.metric_contract materialization writer (Step 5) — an authorized writer that passes via the escape; and tests/fixtures (test env exempt so direct-repo fixtures keep working).
5. The guard distinguishes legacy ad-hoc authoring (blocked) from the governed MCF materialization writer (permitted) — it is not keyed to the table alone.
6. Out of scope: no schema tightening to reject free fields_used/canonical_contract (that is D430/D431); no route/endpoint removal; no data wipe (1022 legacy versions / 2 active preserved).

Evidence (live 2026-06-07): two open write surfaces — API POST /contracts/:id/versions createVersion for category=metric (contract.service.ts:311-396; meta-schema metric-v1.schema.json:52-66 accepts free canonical_contract + fields_used) and the repository choke point createMinimalMetricContract (contract-metrics.repository.ts:139-158, used by scripts/seeds/fixtures). One unguarded creator script: d225-generate-phases-4-7.js. Runtime is read-only (metric.service.ts); MCF writes mcf.* only; no MCF->contract.metric_contract writer exists yet.

Grounding: docs/implementation/legacy-metric-contract-authoring-guard-study-2026-06-07.md. Sequence: D429 Step 1 (immutability) applied; Step 2 canonical (DEC-a6258b/D430) + observation (DEC-4a17e0/D431) decided; this Step 3 (guard) decided; Step 4 (fix fail-open activation gates X5/X4) and Step 5 (resume materialization) follow. MCF materialization remains paused.
