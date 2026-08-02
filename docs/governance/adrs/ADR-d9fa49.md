---
uid: DEC-d9fa49
title: "Legacy metric-contract activation retired with a governed refusal — F-018 disposition (accidental dead-signal freeze replaced)"
description: "ContractService.transitionState refuses category='metric' → 'active' with an explicit Gone-class refusal; the MLS-14 gate wiring (whose R3-dropped-table query was the only thing freezing the route, behind an @Optional injection that would fail OPEN if absent) is removed from the service. Metric activation is exclusively the MCF certification lane (D541 C8 gate)."
status: decided
date: 2026-08-02T17:02:45.562Z
project: bc-core
domain: contracts
subdomain: contracts/activation
focus: lifecycle
---

# Legacy metric-contract activation retired with a governed refusal — F-018 disposition (accidental dead-signal freeze replaced)

## Context

The freeze must not depend on a bug staying broken. An accidental 500 is not a governance statement: it is illegible to operators, invisible to consumers, and reversible by any well-meaning repair of the underlying query. Making the retirement explicit converts F-018 from a live defect into doctrine, at the cost of ~30 lines. Codex's ratification ranked this first in the fast lane for exactly this reason.

## Decision

F-018 DISPOSITION (lifecycle authority study, ratified fast-lane item; Codex Phase-1 review: "the current implementation form should not remain the standing freeze mechanism").

1. THE DEFECT BEING RETIRED. The legacy activation route `POST /:contractId/versions/:version/activate` → `ContractService.transitionState` was "frozen" for metric contracts only by accident, in three stacked ways: (a) the MLS-14 gate's query LEFT JOINs `contract.chain_status`, DROPPED at Runtime Spine R3 — every invocation 500s; (b) the gate is injected `@Optional` — were it absent, the metric branch FALLS THROUGH and activates with NO gate (fail-open); (c) nothing marks the route retired — a future repair of the gate query would silently reopen a path to `active` that bypasses D541 certification. This is precisely the dead-signal failure class DEC-29b518 (D429 Step 4) forbade: "fail-closed MUST key on 'no valid SSOT signal', NEVER on [a dead signal]."

2. THE GOVERNED SHAPE. In `transitionState`, `category='metric'` targeting `'active'` throws an explicit Gone-class refusal naming the doctrine: legacy metric-contract activation is RETIRED; metric activation is exclusively the MCF lane (`audit_pending → active` under the C8 certification gate, DEC-c48b0f). Mirrors the M17 pattern (legacy definitions POST → 410 with machinery removed) and joins F-014's defence stack as its explicit service-layer statement. The `Mls14ActivationGate` wiring, `hasBlocker`, and `MLS14_BLOCKER_CODES` usages are removed from ContractService (this was their sole consumer).

3. SCOPE GUARDS. (a) Non-activation legacy metric transitions (draft→review etc.) are untouched — harmless over a 0-row corpus, and door-guarded at authoring by DEC-7bdd03. (b) SC/AC/OC/CC activation paths in the same method are untouched. (c) The `Mls14ActivationGate` SERVICE and the `src/mls` module are NOT removed here — their fate belongs to the F-021/F-023 dial-repair design decision (7ab22b N/A-doctrine vs MCF-native ladder), not this unit. (d) DEC-b8b825's "MLS-14 is the sole refusal authority on governance_state_code → active" claim is superseded IN EFFECT for the metric category by this refusal + D541; recorded here rather than editing the historical ADR.

4. PLANE DISCIPLINE (D541 §5). This is an EXECUTION-plane act implementing standing design: D429 Step-4 dead-signal doctrine + M17 retirement pattern + D541 gate position. No new design is introduced; the missing declaration was the route's retirement, which this ADR supplies.
