---
uid: DEC-ac05fc
title: "Three contract chains: Source → Metric → AI (layered, feed-forward)"
description: "Superseded three-chain model (Source, Metric, AI). Replaced by six contract families with unified chain model."
status: superseded
date: 2026-03-01
project: platform
domain: database
refs:
  - type: decision
    label: "D021"
authority: retired
migrated_from: legacy v2 archive
---


# Three contract chains: Source → Metric → AI (layered, feed-forward)

## Context

Superseded by D069 (DEC-36d78f). D022 described Source Chain as "extraction → source → admission → canonical." With Extraction Contract retired (D069), Source Chain becomes: "source → admission → canonical" with extraction handled by Reader Flavor + Observation Schema. The three-chain model (Source → Metric → AI) and feed-forward principle remain valid — only the Extraction step within Source Chain is removed as a contract type.

## Decision

Contract registry organizes 7 contract categories into 3 layered chains that feed forward:

**Source Chain** (data ingress — "what happened"): extraction → source → admission → canonical. Bound to source_version_id. Linear, per-source. Produces governed Canonical Objects. No intelligence.

**Metric Chain** (measurement — "how are we doing"): metric + intervention. Metric references N canonical contracts (cross-cutting, per D021). Intervention is rule-based threshold response (if X crosses Y, do Z). Produces Metric Facts. Deterministic computation, no intelligence.

**AI Chain** (intelligence — "what does it mean, what's next"): ai contracts. Consumes N Canonical Objects + N Metric Facts. Produces interpretations (pattern recognition, correlation, root cause) and anticipations (forecasts, risk scores, anomaly probabilities). This is where intelligence lives.

Chains feed forward strictly: Source → Metric → AI. No back-references. Each layer consumes the output of the previous layer but never feeds back into it. This preserves immutability guarantees at each boundary.

Implementation: contract_canonical_dependency join table for metric/AI contracts. source_version_id only for source-chain contracts. Contract registry UI groups by chain.

## Options Considered

N/A

## Consequences

N/A
