---
uid: DEC-c027fb
title: "Identity tuple v3: aggregation currency policy is a metric identity element"
description: "identity_tuple_hash gains the effective aggregation currency policy as an optional trailing element under hash_algorithm_version mcf-hash-v3, stamped on newly-created MCs only; amends the D470 hash authority using its own backward-compatible precedent"
status: decided
date: 2026-08-02T02:25:29.077Z
project: bc-core
domain: metrics
subdomain: metric-runtime
focus: identity-hash
---

# Identity tuple v3: aggregation currency policy is a metric identity element

## Context

The identity tuple's purpose is one-live-contract-per-meaning. A declaration the runtime consults during evaluation is part of meaning (Invariant I: meaning is evaluated once, at its declared boundary). The rehearsal produced the disconfirming datum: a semantically-corrected successor that the substrate treated as identical to the contract it corrects. Option B (version succession under the same MC) was considered and deferred — doctrinally attractive but diverges from the shipped corrective pattern (production __tacorr_* successors are separate MCs) and requires a new M4 write path; it does not conflict with this amendment. Backward-compatible form chosen over a clean 8-element retuple because service-side dedup compares raw hash strings across versions and a byte-incompatible bump would silently blind it for the whole existing corpus.

## Decision

The metric identity tuple (hash authority D-M7-8 §10.2, as amended by D470/DEC-327d4e) is amended a second time, using D470's own backward-compatible pattern:

1. ELEMENT. The EFFECTIVE aggregation currency policy — mcv.aggregation_currency_code with NULL normalized to the runtime default 'document_currency' — becomes a trailing element of the identity tuple, appended ONLY when the effective policy differs from 'document_currency'. A metric declaring the default (explicitly or by omission) produces a tuple byte-identical to its mcf-hash-v2 form, exactly as D470 kept ungrouped metrics byte-identical to v1.

2. VERSION. hash_algorithm_version becomes 'mcf-hash-v3' for newly stamped metric contracts. The v1/v2 corpus is NEVER restamped: active MC identity columns are immutable (mcf.fn_mc_active_immutability_check, Invariant III), and the partial unique index idx_mcf_mc_identity_active keys on (identity_tuple_hash, hash_algorithm_version), so rows stamped under different versions coexist without constraint interaction. Duplicate/alias handling (L-V1h) continues to compare stored hash strings without a version filter; because the default-policy form is byte-compatible, cross-version dedup behavior is unchanged for the entire existing corpus.

3. TYPE DISAMBIGUATION. The tuple now has two optional trailing elements: the D470 computed-dimension kernel set (a JCS array, present only when grouped) and the currency policy (a JCS string, present only when non-default). Their JCS encodings are type-distinct (array vs string), so no byte collision is possible between a grouped/default-currency tuple and an ungrouped/non-default-currency tuple; the canonical order when both are present is [.., kernelSet, currencyPolicy].

4. WHY IDENTITY. The declared aggregation currency policy is evaluation-bearing: 'document_currency' adds the currency partition key (governed-metric-runtime.currencyPartition) and 'single_currency_required' arms a runtime safety check. Two contracts identical in every other element but differing in this declaration evaluate differently and are therefore distinct identities. Its omission from the tuple was underspecification of the same class D470 corrected for grouped metrics.

5. TRIGGER. Discovered by the first clone dress-rehearsal of the D540/D520 currency-semantics corrective path (bc_platform_cert_r2, 2026-08-02): a corrective successor whose ONLY delta is aggregation_currency_code ('document_currency' → 'not_applicable', the D520 count-vocabulary correction) produced an identity tuple byte-identical to its live predecessor and was refused by idx_mcf_mc_identity_active. The currency corrective is the first whose entire delta lies outside the v2 tuple; the temporal/unit siblings avoided collision only because their deltas changed the binding set hash. Without this amendment every one of the 43 currency-cohort corrective runs halts at hash stamping.

6. WHAT THIS IS NOT. Not a restamp (forbidden), not a driver-side dodge (rejected as compensation at the implementation layer for a declaration-layer gap, per the DEC-c48b0f design-plane question), and not the long-term successor-shape question (whether a corrective successor should be a new MCV under the same MC rather than a new MC — that remains open as a separate architectural track and is not blocked by this amendment).
