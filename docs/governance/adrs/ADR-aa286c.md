---
uid: DEC-aa286c
title: "Multi-binding MC evaluation end-to-end"
description: "Multi-binding MC evaluation end-to-end"
status: implemented
subdomain: metric-evaluation
focus: multi-binding-dispatch
date: 2026-04-17T12:47:00.618Z
project: bc-core
domain: platform
migrated_from: legacy v2 archive
---

# Multi-binding MC evaluation end-to-end

## Context

No rationale recorded.

## Decision

Metric Contracts with multiple co_bindings (e.g. ratio formulas I1/I2 with I1 and I2 from different CCs) were silently unable to evaluate because: (1) MC envelopes had duplicate role='primary' on all bindings, collapsing to one alias in assembleInputPayloads; (2) resolveMcDispatchMetadata's LIMIT 1 + role filter returned only one CC; (3) dispatchOne fetched COs from only that single CC. Fix: (a) data - rename second binding role primary->secondary for 77 MCs in demo-selenite; (b) code - resolveMcDispatchMetadata returns all binding CCs; (c) code - dispatchOne uses contract_id = ANY(...) across all bindings. Impact: bucket C dropped 77->5, producing +6 (115->121). Remaining bucket-C tail exposed bucket B/D data-alignment issues.
