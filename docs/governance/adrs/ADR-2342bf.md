---
uid: DEC-2342bf
title: "Backfill and batch execution model — distinct from live observation"
description: "Backfill uses a dedicated bulk-optimized execution path with chunking, checkpoint/resume, and idempotency. Not a config knob on live admission."
status: decided
subdomain: execution-model
focus: backfill-strategy
date: 2026-03-02
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Backfill and batch execution model — distinct from live observation

## Context

DECIDED (direction, detail deferred): Backfill requires a dedicated execution path — same object outputs (SO, CO, Metric) but bulk-optimized with chunking, checkpoint/resume, idempotency guards, and resource isolation from live admission. Not a config knob on the existing path. Design session needed before first production backfill. Does not affect current development — live observation model is correct for the demo and MVP. Reader flavor backfill_config (TSK-946b36) remains the integration point.

## Decision

BareCount's current execution model assumes lean, event-driven progression: a source state change is observed → UinBAT Reader admits → SO → canonical evaluation → CO → metric → AO. Backfill scenarios (historical data load, bulk file transfer, batch ERP extracts) have fundamentally different characteristics: high volume, bounded time window, tolerance for latency, need for progress tracking and resumability. Should backfill use a separate execution path, or adapt the existing progression with configuration?

## Options Considered

N/A

## Consequences

N/A
