---
uid: DEC-8e5f5a
title: "Canonical classification: multi-input classify compute in CcV2CanonicalResolverService"
description: "CONTEXT: Several metric-directory clusters count/sum a measure scoped by a CANONICAL CLASSIFICATION of the row — e.g. JE line_type (intercompany/recurring/corrective_adjusting/first_time_originating/other), asset transaction_type (acquisition/impairment/revaluation), payment account_type (customer/vendor). The directory members already declare canonical-value discriminator predicates (member.discriminator_json → {concept_id, values}); the generator turns those into filtered aggregates (row_count_where/sum_where). The missing piece is the CANONICAL FIELD carrying the classified value. The CC-v2 resolver's computeDerivation supports only date_diff/date_add/subtract, and OC field transforms support only single-field code_lookup (applyCodeLookup). A classification that depends on MULTIPLE raw fields (e.g. line_type = intercompany if trading-partner present, else corrective if reversal-reference present, else first_time_originating) cannot be expressed. This blocks ~15 directory members (line_type 10, ANEP impairment/reval, payments).

DECISION: Add a declarative multi-input `classify` compute to the CC-v2 resolver's computeDerivation, expressed in the existing CC derivation grammar ({inputs:[{role,business_concept_id}], function:'classify', params, canonical_field, output_business_concept_id}). params = {cases:[{when:{input:<role>, op:'present'|'absent'|'eq'|'ne'|'in', value?}, then:<canonical code>}...], default:<canonical code>}. The resolver evaluates cases IN ORDER against the derivation's source-resolved input values (each input is an OC-mapped business concept — Invariant IV, no fact-shape coupling) and returns the first match's code, else the default. Emitted as a canonical field per the D461 both-places pattern (field_selection + derivations), so PE-MC-11 sees compute-proof via observable inputs.

FOUNDATION: Invariant I — the classified meaning is produced once, at the canonical boundary, from explicitly declared inputs + declared case rules (no downstream re-derivation). Invariant IV — inputs are business concepts, not raw columns; the case rules are explicit in the contract. No new node semantics beyond what formula-canonicalization already reserves ('case'/'bucket_assign' node kinds); this is the CC-derivation-side realization. Composes with the multi-source join (DEC-0a187d) — a classify input may be a secondary-table concept (e.g. reversal-reference on BKPF joined to a BSEG-grain line).

ZERO-CLAIMS: the classify compute is unit-tested; a member is only 'resolved' when the classified value is runtime-real in a CO payload. E2E application requires authoring the discriminator business concepts (trading-partner←VBUND, reversal-reference←BKPF.STBLG, transaction-type←ANEP.ANBWA, account-type←BSEG.KOART) — BCF authoring, done separately.

DATA-QUALITY FINDING: the existing 'line type' concept (ffaaee59) is soft-ref'd to BSEG.KOART (account type D/K/S) — WRONG for the intercompany/recurring/corrective member predicates. line_type must be the classify OUTPUT, not a direct KOART map; the KOART soft-ref should be corrected/repurposed (KOART is really account_type). Flag for the application step.

SCOPE: per-row classification only (no cross-row aggregation — that stays at the metric boundary). Ordered first-match cases + default. Ops: present/absent/eq/ne/in."
status: decided
date: 2026-07-09T16:36:59.837Z
project: bc-core
domain: metric-runtime
subdomain: canonical-resolver
focus: evaluation-boundary
---

# Canonical classification: multi-input classify compute in CcV2CanonicalResolverService

## Context

No rationale recorded.

## Decision

See description_text (ADR body authoritative).
