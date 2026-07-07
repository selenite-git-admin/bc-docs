---
uid: DEC-a6cdae
title: "Metric program split: chain-readiness (per-metric) vs data-readiness (SDG table-level program)"
description: "Metric enrichment runs to chain-readiness only (machine-checkable via mcv_chain_status + projection preflight); data readiness = separate SDG table-level program with bulk verification per drop; one runtime canary per new shape; zero-claims vocabulary preserved"
status: decided
date: 2026-07-07T10:41:29.218Z
project: bc-core
domain: metrics
subdomain: metric-runtime
focus: program-governance
---

# Metric program split: chain-readiness (per-metric) vs data-readiness (SDG table-level program)

## Context

Field-by-field runtime verification does not amortize: three runtime units (2026-07-07) showed the per-metric hand-recompute cost is the program's long pole (~90 min/unit) while its unique findings were all either (a) engine/contract defects that surfaced on the FIRST metric of a shape (D495 snapshot key, as_of empty selection, DZ/DR literals) — captured by the shape-canary guardrail at a fraction of the cost — or (b) data facts already knowable from one table-level SQL query (discounts 100% NULL, cleared-only slice → no disputes/write-offs/open items possible). All current data gaps root at the SDG table level, where one drop (BSID + discount/dispute emission) makes dozens of chain-ready metrics meaningful simultaneously; verifying metrics one-by-one before that data exists is verifying zeros. Authoring-to-ACTIVE now runs at ~1-3 min/metric through devhub_metric_drive, so chain throughput is bounded by verification policy, not tooling — this split moves the program bound to authoring speed while preserving defect discovery (canaries) and claim honesty (zero-claims vocabulary). Doctrine-compatible: creation vs runtime were already separate units (D492 workflow kinds); this elevates the split to program level.

## Decision

The MCF metric-enrichment program (PLN-457cd0 Phase 1) narrows its per-metric definition of done to CHAIN-READINESS; DATA-READINESS becomes a separate, SDG-anchored program. 

**Chain-ready (per metric, the enrichment program's scope):** governance chain complete to ACTIVE (preflight → panel → materialize → PE-MC → activate via devhub_metric_drive) PLUS structural runtime readiness — bindings resolve, bound/filter concepts and temporal-gate fields projected in the active grain-CC resolved_schema. This is machine-checkable on the existing `mcf.mcv_chain_status` substrate (D481 R3 checks: bindings_resolve, grain_cc_active, pe_current, self_verification) plus the D492 preflight runtime_projection leg — the program boundary sits on checkable substrate, not judgment.

**Data-ready (the separate program):** SDG realism lands at TABLE level (TSK-72a0a7 anchor: BSID open items, discount/dispute/status emission, FX realism), followed by ONE bulk runtime-verification pass per SDG drop — a campaign evaluation across all chain-ready metrics verified by identity checks (e.g. gross = net + tax, partition sums) and spot-checks, NOT per-metric hand-recomputes.

**Guardrails (binding):**
1. **Vocabulary honesty (zero-claims):** "chain-ready" ≠ "runtime-live". No metric is claimed runtime-live without payload verification; the split defers the verification work, never the claim discipline. Seed-ledger `published` = chain-ready only.
2. **One runtime canary per NEW SHAPE:** the first metric of a new (formula-op class × temporal-gate shape × binding pattern) combination gets a single canary evaluation before its siblings fan out — engine defects surface at shape level (precedent: the D495 snapshot-key defect, the as_of empty-selection gap — both caught on shape-first metrics, never on siblings). Siblings skip runtime entirely until the data program's bulk pass.
3. **Chain-correctness defects stay in the chain program:** wrong formula literals, unprojected concepts, role-ineligibility (e.g. the DZ/DR literal rot, TSK-f15818) are contract-layer defects fixed by supersession in the chain program — they are not deferred as "data issues".
