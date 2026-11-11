---
uid: DEC-eb612b
title: "The Demoed evidence-bridge (Phase A): a Demoed proof consumed as governed, coverage-asserted evidence — VALIDATED claim level + self-verification arm; panel-free certification deferred to a Phase-B DEC; never a cascade"
description: "The Demoed evidence-bridge (Phase A): a Demoed proof consumed as governed, coverage-asserted evidence — VALIDATED claim level + self-verification arm; panel-free certification deferred to a Phase-B DEC; never a cascade"
status: decided
date: 2026-11-10T11:17:01.064Z
project: bc-core
domain: metrics
subdomain: metric-lifecycle
focus: cross-axis evidence bridge
---

# The Demoed evidence-bridge (Phase A): a Demoed proof consumed as governed, coverage-asserted evidence — VALIDATED claim level + self-verification arm; panel-free certification deferred to a Phase-B DEC; never a cascade

## Context

A Demoed proof (the platform's own in-platform demo-plane proof that the engine calculates a metric correctly versus an independent oracle) should become fast, accurate governed evidence that accelerates the certification and chain axes, without a cascade (plane separation DEC-a6cdae; Foundation VI, evidence emitted not inferred). Codex round 1 blocked the original panel-optional path as having no truthful report-and-decision wire; round 2 accepted the phased design — Phase A now, the panel-free path (Phase B) held for its own DEC. Ratified under recorded TOTP operator grant a72a3d33 (desk #400).

## Decision

Phase A of the Demoed evidence-bridge is ratified. Authority: operator grant 2026-11-10T11-14-06-441Z-a72a3d33 (method totp; text_sha256 a72a3d33382a6b8bfc47feecf9fb63250a2e7c377990adffa1ca87552a243b7a; desk request #400); Codex design review gen-6db532-02 ACCEPTED WITH BOUNDARY. Frozen design: MEMO artifacts/architect/MEMO-demoed-evidence-bridge-2026-11-10.md at barecount-devhub 134362f5f51f64a1a8624432f31afdacdec1c294 (file sha256 5538b5ed807202b5c6f7fdbfd86dabfe807c07731f4fc87bfc23f610729957eb). AMENDS DEC-346ae7 (makes the (3b) VALIDATED tier representable; the panel-free Demoed-basis decision is deferred to a Phase-B DEC) and DEC-025bfc (specifies the bridge record T3 names; adds coverage). RELATES DEC-c48b0f, DEC-b049f6, DEC-a6cdae, DEC-89db41, ADR-3f6b1b, DEC-1bb88e, DEC-e662a3, DEC-79b62f.

BR1 (the act): bridgeDemoedProof is the only way a Demoed proof becomes lifecycle evidence — a governed act binding one current Demoed proof to one frozen MCV package through the identity chain, asserting coverage, recording CC equivalence, emitting an immutable supersedable bridge record. It flips no state and writes no demo-plane row; refuses fail-closed with named codes.
BR1a (identity): the bridge identity is the MCV certification package hash (mcv_package_snapshot.package_signature_hash); the proof's parent-MC hash is reconciled by a recorded verdict (reconciled_by_immutability | reconciled_by_direct_pin), never by equality; an unreconciled proof yields no bridge.
BR2 (coverage): credit requires a coverage verdict over the declared semantics derived from the frozen package; uncovered elements carry a recorded residue disposition (accepted_residue with a 40-plus-char rationale and a named disposer, or blocking); hollow proofs refused; witness provenance (proof_emitted | bridge_derived) travels with the claim.
BR3 (chain): the chain judge MAY satisfy self_verification from a current covered bridge head (pass:demoed_bridge); declaration legs are never replaced; CC-equivalent corroboration is informational, a disagree is an Architect-routed defect signal never a verdict input; the bridge head is a chain-fingerprint input and an epoch key.
BR4 (certification, Phase A): VALIDATED = certified_active plus a current covered bridge head, rendered as a read-time projection with residues visible; the certification report, decision, run lifecycle, wire validators and C8 battery are UNCHANGED — c1 through c15 byte-unchanged, no c16, and the panel run still required by completeRun.
BR4b (Phase B, NOT ratified here): a panel-free Demoed-basis decision (the evidence contextual branch; the restated report/decision CHECKs plus decision_demoed_basis; the generalized anti-rubber-stamp amending DEC-05815d; the meaning-reference for DEC-346ae7 part 1; c13 Arm D with the legacy arm byte-identical plus c16; C8 statement c1 through c12, c14 and c15 unchanged, c13 adds Arm D, c16 new) requires its OWN DEC and is NOT authorized by this grant.
BR5 (residue): pe_current; meaning against the standard; uncovered elements; cross-version carry-forward; tenant live numbers; and the C4/C7 request custody never transfer.
BR6 (no cascade): no trigger, job or read changes a lifecycle state because a bridge exists; consumers read it only through BR3/BR4.

Foundation: location B plus E consumed at D; design act (DEC-c48b0f); Invariants I/III/IV/V/VI. Consequences are each separately operator-gated after this ratification: the read-side build (candidate chain read + projection generalisation); the Phase-A bc-db migration (two bridge tables + guards + epoch trigger + fingerprint-basis change, NO C8 battery change) under its own DB-yes, restore-proof and governed apply; the bc-core bridge service + arm S + the VALIDATED read projection; prove-on-one Phase A (a VALIDATED raise on customer_invoice_volume plus a bridge on ar_balance_outstanding through the unchanged panel-retained path); and the known-hollow negative. Phase B and any c13/c16 change are explicitly excluded from this decision.
