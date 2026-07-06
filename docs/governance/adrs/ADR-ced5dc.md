---
uid: DEC-ced5dc
title: "BCF Enrichment Program-2 — non-finance vocabulary buildout to max coverage"
description: "Enrich the P3 Business-Concept layer across 112 non-finance entity shells to max coverage via the Path-A panel, unblocking first-client MCF onboarding across all functions."
status: decided
date: 2026-07-04T05:42:52.257Z
project: bc-core
domain: contracts
subdomain: contracts/business-concept-registry
focus: vocabulary-enrichment
---

# BCF Enrichment Program-2 — non-finance vocabulary buildout to max coverage

## Context

The MCF engine is proven on finance but idle for the other 19 functions because their vocabulary substrate is empty. Enriching BCF to max coverage ahead of demand is the single foundation that unblocks first-client onboarding for any function without per-client vocabulary work. Path-A panel authoring is chosen for grounding rigor (Checker/Moderator catch operator-direct errors); the reference-BC panel gap and the cost-roster are addressed as gated precursors so scaling is both correct and affordable.

## Context

BCF (Business Concept Registry, DEC-02f5a9) is enriched for finance only. Live substrate verified 2026-07-04: 140 entities (28 finance-enriched, **112 non-finance empty shells**), 160 characteristics (64 bound, 96 unused with broad non-finance breadth), 220 active Business Concepts (all finance), 44 identity-bearing BCs (33 value keys + 11 reference edges, all finance). The MCF metric runtime is BUILT and PROVEN — 82 active MCVs / 154 bindings live (finance) — so the engine works end-to-end; the blocker for every non-finance function is the upstream vocabulary + contracts + data. Program-2 delivers the vocabulary half.

## Decision

Run **BCF Enrichment Program-2**: enrich the P3 (Business Concept) layer across the 112 non-finance entity shells — identity-bearing keys, reference DAG edges (which MCF PE-MC-2/PE-MC-7 grain-reachability consumes), and descriptive value properties, plus new characteristics where the 96-unused pool does not already cover — to **max coverage** (doctrine: max-coverage, not demand-driven; demand sets order, never scope). Sequenced in **9 functional waves** (A Sales/CRM → B Supply-chain/procurement completion → C HR → D IT/ITSM → E Quality+Manufacturing → F Asset-Mgmt → G Risk/Compliance/Legal/Governance → H Marketing → I Engineering/Product/R&D), each a coherent backbone slice referencing only already-enriched targets, so no wave blocks another.

### Sub-decisions locked with the operator (2026-07-04)

1. **"assembler" is the official name** for the candidate-preparer role — assembles grounded candidate packets (proposedName + definition + source_citations) from the seed catalog and named standards, distinct from the panel Maker. Model-agnostic by contract; current implementation is Claude Code Desktop on Fable. The role is NOT coupled to any model.

2. **Path A (the in-process Maker/Checker/Moderator panel) is the default authoring path**, chosen over operator-direct because the Checker/Moderator have repeatedly overturned incorrect operator-direct calls. Structural caveat found in code: `POST /api/bcf/registry-authoring-runs` authors VALUE concepts + characteristics only — reference BCs (DAG edges) and identity_bearing flips are operator-direct-only today. Resolution: a precursor build task extends the panel path to author reference/identity BCs so the highest-risk ~350 structural acts get panel scrutiny (build-first preferred over the operator-direct hybrid).

3. **Cost-roster A/B test before scaling.** The roster is calibration-locked (DEC-ffee4e); a candidate cheaper roster (Sonnet 5 Maker / GPT-5.4-mini Moderator vs locked Opus 4.7 / DeepSeek V3.2 / GPT-5.5) is tested on 3 hand-picked candidates from the checker-first parked corpus on byte-identical packets, judged on **verdict + grounding parity**, disqualified on any lenience/false-approve. Downgrading the Moderator (adjudicator) carries more risk than the Maker (proposal, scrutinized twice downstream). Model swaps are env-driven (BCF_PANEL_MAKER_MODEL / BCF_PANEL_MODERATOR_MODEL); pre-test checks: add non-Opus models to ANTHROPIC_NO_TEMPERATURE_MODELS if they reject temperature, register exact pricing for clean telemetry.

## Scope boundary

Program-2 makes every non-finance function metric-AUTHORABLE. It does NOT make any non-finance metric runtime-LIVE — per function, source registration, SC/AC/OC/CC(grain)/MC contract chain, source data (SDG synthetic then client extract), and MCF panel→publish→bind→evaluate still follow. That downstream machinery is proven on 82 finance metrics; Program-2 removes the shared vocabulary blocker ahead of demand (clean split: complete BCF → demand-ordered MCF).

## Discipline

Each wave is repair-location B (contract semantics / vocabulary) and runs the Foundation six-invariant gate + Checker-First Preflight before authoring. Max coverage, real standards-grounding per item (no funnel-padding). Services-only writes; no raw INSERT. createCharacteristic is high-risk (panel + operator-confirm ≥40 chars). Meaning columns immutable — corrections via supersede. One-then-many: prove the recipe on one non-finance entity before scaling a wave.

## Sizing

~700–800 BCs across 112 entities (~150 identity keys, ~150–200 reference edges, ~400–450 descriptive values) + ~150–250 new characteristics; ~9–12 batch sessions; cost advisory (no hard cap since D483), materially reduced if the roster A/B test passes.
