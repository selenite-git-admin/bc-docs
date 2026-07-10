---
uid: DEC-0a187d
title: "Multi-source canonical join in CcV2CanonicalResolverService — honor declared secondary source_references"
description: "CONTEXT: CcV2CanonicalResolverService resolves a CC-v2 by picking ONE primary source fact table (coverage vote) and reading only its rows; concepts carried only by a secondary source table resolve to null (ccv2-canonical-resolver.service.ts:424 — 'a later increment joins secondary sources on the identity key'). This blocks every metric whose canonical grain legitimately spans tables — e.g. Fixed Asset value/method metrics need ANLA lifecycle dates (acquisition/disposal) AND ANLC/ANLB/ANEP measures (acquisition cost KANSW, accumulated depreciation KNAFA, depreciation key AFASL, transaction amounts) on the SAME asset grain. ~20 metric-directory members (fixed_assets + cash_flow) are needs_cc solely for this reason.

The OC-v2 body grammar (barecount/observation/v2) ALREADY forward-declares source_references[{role: primary|secondary|reference}] and join_semantics[]. The gap is only that the resolver runtime does not honor declared secondaries. Per Foundation the fix is repair-location D (evaluation boundary implementation): fixing anywhere lower (SDG shape A, fact rows E, read filter F) would be compensation for a runtime that ignores an explicit contract declaration.

DECISION: Complete the resolver to honor declared secondary sources via a minimal declarative join_semantics shape in the OC-v2 body:
  join_semantics: [{ secondary_table, join_on: [{primary_field, secondary_field}...], filter?: {field, op, value}, reduce?: {strategy:'latest_by'|'first', field?} }]
The resolver, after reading primary grain rows, reads each declared secondary fact table, applies the optional pre-filter, reduces many-per-key rows to one via the declared reducer (default first), indexes by join_on secondary fields, and MERGES the needed secondary columns onto each matching primary row before payload assembly. Field/derivation resolution is unchanged — pick() already resolves a secondary-only concept to its secondary carrier column, which now exists on the merged row.

FOUNDATION: Invariant IV — the join is EXPLICIT in the contract (declared join_on/filter/reduce), never inferred; a resolver that silently drops declared secondaries is the violation, honoring them is the fix. Invariant I — canonical meaning (the joined value) is produced once, at the canonical boundary, per the OC's declaration. Invariant II — SO->CO ordering preserved: primary grain rows drive CO emission; secondaries only enrich by identity key, never create grain instances. Invariants III/V/VI unchanged (version-forward, non-replayable, progression+fact emitted).

ZERO-CLAIMS GUARD: a member is only 'resolved' when the joined field is runtime-real (verified in a CO payload cross-check), not merely PE-MC-11 gate-passing. contract-chain-eligible != runtime-ready.

SCOPE: primary→secondary enrichment only (no secondary-driven grain expansion, no N-way transitive joins); additional secondaries are independent merges. Reference stamping (D468/D469) and sign indicators (TSK-04e6df) compose unchanged. No DB change — fact.so_* tables auto-provision on admission."
status: decided
date: 2026-07-09T15:21:02.920Z
project: bc-core
domain: metric-runtime
subdomain: canonical-resolver
focus: evaluation-boundary
---

# Multi-source canonical join in CcV2CanonicalResolverService — honor declared secondary source_references

## Context

No rationale recorded.

## Decision

See description_text (ADR body is authoritative).
