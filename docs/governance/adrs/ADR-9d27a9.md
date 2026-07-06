---
uid: DEC-9d27a9
title: "BCF supersession-cascade: fail-closed guard on supersede + systematic consumer remediation"
description: "supersedeBusinessConcept gains a fail-closed guard blocking supersession while live consumers exist; existing stranded consumers remediated systematically."
status: decided
date: 2026-06-27T03:00:46.784Z
project: bc-core
domain: contracts
subdomain: bcf/supersession
focus: lifecycle
---

# BCF supersession-cascade: fail-closed guard on supersede + systematic consumer remediation

## Context

The supersession-cascade gap stranded consumers on superseded BCs and blocked ARPI at PE-MC-11. A fail-closed guard at supersede time is chosen over auto-cascade because Foundation Invariant IV requires references to be explicit — the consumer must re-affirm the new reference rather than have it silently re-pointed (which would also risk Invariant-I meaning drift on meaning-changing supersessions). Prevention alone is insufficient because 41 BCs are already superseded with stranded consumers, so systematic remediation via the CC authoring path is paired with the guard. The hybrid auto-cascade-for-safe-supersessions optimization is deferred until a reliable meaning-preserving classifier exists.

## Decision

**Problem.** `supersedeBusinessConcept` (concept-registry/registry-authoring.service.ts) neither guards nor cascades. When a BC is superseded, its consumers keep referencing the predecessor: (1) `contract.canonical_contract_version.contract_json` field→BC bindings (CCs), and (2) `mcf.metric_variable_binding.bound_business_concept_id` (metrics). They are silently stranded. 41 superseded BCs exist. CONFIRMED LIVE BLOCKER: ARPI (MCV 16aaadad) failed PE-MC-11 because `cc__customer_invoice_arpi_slice` v4.0.0 declares the SUPERSEDED document number `51482979` while ARPI binds the active identity-bearing `2887850a` (51482979→2887850a, descriptive→identity_bearing, verified in business_concept_supersession). The chain-integrity gate (PE-MC-11) caught it correctly; the defect is upstream at supersede time.

**Decision 1 — PREVENT (fail-closed guard).** `supersedeBusinessConcept` is extended to detect live consumers of the predecessor BC (CCs whose contract_json binds it + active metric_variable_binding rows) and BLOCK the supersession when any exist, returning the consumer list. The operator must explicitly re-bind each consumer to the successor first, then supersede the now-consumer-free predecessor. Flow: create successor → guard surfaces consumers → consumers re-bound to successor → predecessor retired.

**Foundation rationale.** Invariant IV (all references are explicit): a CC author explicitly chose `51482979`; auto-re-pointing would silently change their explicit reference (and risks Invariant-I meaning drift on meaning-changing supersessions). The guard forces the consumer to explicitly RE-AFFIRM the reference to the successor — preserving explicitness. This is why the guard is chosen over auto-cascade.

**Decision 2 — REMEDIATE (existing 41).** A prevention guard does not unstick already-stranded consumers. Systematically enumerate consumers of the 41 superseded BCs (CC contract_json bindings; metric bindings are 0 post-clean-slate) and re-bind them to their successors via the CC authoring path. ARPI's `cc__customer_invoice_arpi_slice → 2887850a` is the first (a meaning-preserving role/precision upgrade — document number stays document number).

**Rejected / deferred.**
- Auto-cascade (re-point consumers automatically) — rejected: Invariant-I meaning-drift risk + violates the spirit of Invariant IV (silently rewrites an explicit reference).
- Hybrid (auto-cascade only meaning-preserving supersessions, guard the rest) — DEFERRED as a later ergonomic optimization; it needs a reliable "meaning-preserving" classifier (same characteristic + role/precision/representation upgrade). The guard is the correct, simplest base; the hybrid can layer on top without re-deciding.

**Defence in depth.** PE-MC-2 / PE-MC-7 / PE-MC-11 already reject metric publication when a binding references a superseded BC the CC doesn't declare — keep these (they caught ARPI). The guard moves enforcement upstream to supersede time so the chain never reaches publication stranded.

**Consequences.** Superseding a BC with live consumers requires explicit re-bind first (intended friction; preserves explicitness). Existing stale CCs (incl. ARPI's) get remediated. ARPI then resumes: re-author `cc__customer_invoice_arpi_slice` → 2887850a → re-run M13 (PE-MC-11 passes) → M14 → Guard-A projection → Bar-2. Implementation deferred to a fresh session per operator (this session's classification fix DEC-31c212 is proven + banked).
