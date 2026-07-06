---
uid: DEC-957fb0
title: "Editorial rebind evidence handling — PE-MC carry-forward"
description: "M13 PE-MC evidence for editorial rebind MCVs via governed carry-forward (inherit grounding, re-verify fixture), explicit provenance, no silent default-pass"
status: decided
date: 2026-06-08T14:51:18.919Z
project: bc-core
domain: metrics
subdomain: metrics/mcf-m13
focus: governance
---

# Editorial rebind evidence handling — PE-MC carry-forward

## Context

First live exercise of M13 on the ARPI editorial rebind (successor 9ffed384) showed the metric is SEMANTICALLY sound — PE-MC-2/3/4/6/7/9 (grain, roles, types, temporal, computed dims, identity) all PASS — but PE-MC-1/5/10 REJECT only because the draft-only rebind path produces no M12 panel run and no self-verification fixture, which those checks require. An editorial rebind (formula/grain/roles unchanged; BCF anchors refreshed to same-representation_term/data_type successors) is a provably equivalent metric, so its publication evidence should be INHERITED with explicit provenance rather than re-authored via a fresh panel. The package_signature_hash changes (binding-set hash differs), so a verifier result cannot be inherited as-is — it must be re-run bound to the successor's package. Keeping every inherited/fresh artifact explicitly provenance-tagged preserves Invariants V (non-replayable evaluation) and VI (evidence emitted, not inferred) and avoids a silent default-pass.

## Decision

M13 PE-MC eligibility evidence for EDITORIAL REBIND successors (MCVs minted by MetricMcvRebindService) is satisfied by a governed CARRY-FORWARD model — never a silent default-pass, never a copied verifier result.

(1) Editorial-equivalence precondition. Carry-forward is permitted ONLY when, versus the predecessor MCV: formula_intent_hash unchanged, filter_set_hash unchanged, grain unchanged, temporal gate unchanged, variable roles unchanged, and each rebound concept passes the same representation_term + data_type gate (unit may refresh). If any fail, NO carry-forward path exists — the metric is treated as fresh (full M12/M12.5/M13).

(2) PE-MC-1 (provenance/grounding) — inherit by EXPLICIT REFERENCE to the predecessor's panel grounding. Either stamp the predecessor panel_run_uid onto the rebind metric_create cert, or have M13 resolve it via supersedes_version_uid / rebind provenance. The PE-MC-1 evidence_json MUST record grounding_inherited_from_panel_run and rebind_predecessor_mcv. No silent default-pass. (Grounding is package-independent + semantic; an editorial rebind introduces no new claims.)

(3) PE-MC-5 / PE-MC-10 (fixture + self-verification) — do NOT copy the predecessor verifier result as proof. Carry-forward ONLY the fixture CONTENT (section A inputs / section B expected output / section C resolver config); re-bind/mint the fixture for the SUCCESSOR's package signature; run a FRESH self-verification. The fresh verifier result MUST bind to the successor's package_signature_hash (the rebind changes variable_binding_set_hash, so the predecessor's verifier result is stale for the successor). Evidence MUST record carried_from_fixture and the new verifier_result_uid + bound hash.

(4) PE-MC-8 — kept SEPARATE. It remains a general M18 / operator-review policy issue (default-pass-pending-m18+ for ALL metrics) and is NOT solved inside rebind evidence handling.

(5) Repair of the existing reviewed successor 9ffed384 — Option A. After implementation, governed-ABANDON 9ffed384 (frees the deterministic derived mc_name average_revenue_per_invoice__rebind_8c088f55) and create a FRESH rebind successor that carries forward evidence at draft time — a single clean audit trail. Option B (in-place PE-MC re-run on the same review MCV) is REJECTED for 9ffed384 because (a) its metric_create cert is immutable so panel_run_uid cannot be retroactively stamped, forcing check-time-only grounding, and (b) it leaves a mixed REJECT-then-PASS PE ledger. A is preferred unless a future change makes a safe in-place PE-MC re-run on review explicitly supported.

Scope of this decision: documentation only. No runtime evaluation, no tenant fact writes, no code, no DB writes. Implementation is a separate governed DBCP + held PR.
