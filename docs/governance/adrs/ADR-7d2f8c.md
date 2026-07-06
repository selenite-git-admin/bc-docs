---
uid: DEC-7d2f8c
title: "D461 derivation home — canonical-boundary 1-hop derived fields; cross-concept comparison at the metric boundary (corrects DEC-bc6be2 observation-boundary mechanism + design-doc L2/L3)"
description: "D461 derivation lives in the CC body (1-hop, inputs directly observed); cross-concept comparison with a derived input is a metric-boundary op (secondary-metric DAG); corrects DEC-bc6be2's observation-boundary date_offset and the design-doc canonical_mapping/transitive choices."
status: decided
date: 2026-06-28T02:42:15.210Z
project: bc-core
domain: contracts
subdomain: contracts/canonical
focus: derived-canonical-field
---

# D461 derivation home — canonical-boundary 1-hop derived fields; cross-concept comparison at the metric boundary (corrects DEC-bc6be2 observation-boundary mechanism + design-doc L2/L3)

## Context

Grounded in a full re-read of three authoritative Foundation chapters. (1) Invariant I: "Business meaning is produced exactly once per Canonical Object version, at the canonical evaluation boundary, by applying a Canonical Contract to one or more Source Objects." (2) the-contract-grammar lists "An Observation Contract declares canonical evaluation logic" as a DISALLOWED behavior; the OC declares field SELECTION only; the CC declares "resolution rules across multiple Source Objects." (3) Canonical Mapping is Superseded (DEC-02f5a9): "Field-resolution content … survives within the Observation and Canonical Contract bodies … new authoring does not create Canonical Mappings." (4) Invariant II forbids "hidden derivation" and fixes object ordering. Two prior D461 choices contradict this and are corrected here before any are implemented.

## Decision

PROBLEM (surfaced by a 100%-Foundation re-read for calculator-grade reliability). Two prior D461 design choices contradict the Foundation. Neither was implemented yet, so correcting now is clean.

(a) DEC-bc6be2 (D461 sequencing ADR) sanctioned a `date_offset` transform IN THE OBSERVATION grammar, asserting "due date is a real derivation produced once at the observation boundary." That violates Invariant I (meaning is produced once at the CANONICAL boundary, by the Canonical Contract — not the observation boundary) and the contract grammar (an Observation Contract declaring "canonical evaluation logic" is a DISALLOWED behavior; the OC does field selection only). A derivation IS canonical evaluation logic.

(b) The D461 design doc (d461-canonical-reduction-derived-field-dbcp) homed the derivation in `canonical_mapping` (L2) and made the chain gate transitively/multi-hop observability-aware (L3). But Canonical Mapping is SUPERSEDED (DEC-02f5a9): resolution content survives in the OC and CC BODIES, and new authoring does not create Canonical Mappings. And "resolution across Source Objects" + Invariant II ("no hidden derivation") require single-hop, not a transitive intra-CO derivation chain (an internal mini-pipeline — against the anti-pipeline model).

DECISION (Foundation-grounded; locks the derivation home).

1. DERIVATION HOME = THE CANONICAL CONTRACT BODY. A derived canonical field is a CC resolution element: the CC `field_selection` includes the derived concept and a resolution rule computes it. NOT the Observation Contract (Invariant I — meaning is produced at the canonical boundary by the CC; the OC only selects fields). NOT `canonical_mapping` (superseded). This replaces design-doc L2.

2. ONE HOP ONLY at the canonical boundary. A derived canonical field's compute inputs MUST be DIRECTLY observed Business Concepts (mapped by an active observation-v2 OC) — never themselves derived. Basis: the CC resolves "across Source Objects"; Invariant II forbids hidden derivation; the anti-pipeline model forbids an intra-CO derivation chain. `due = date_add(baseline, terms)` is a VALID 1-hop CC derived field (baseline=ZFBDT, terms=ZBD1T both observed on BSAD). This replaces design-doc L3 (the gate is 1-hop, not transitive).

3. CROSS-CONCEPT COMPARISON WHERE AN INPUT IS ITSELF DERIVED → THE METRIC BOUNDARY, via the Foundation-sanctioned secondary-metric DAG ("the [metric] boundary may also read one or more upstream Metric Snapshot versions explicitly referenced by [a governed secondary metric] chain"). `collection_lag = date_diff(clearing, due)` with `due` derived is NOT a canonical field (that would be 2-hop). It is a metric operation: either a single metric `AVG(date_diff(clearing, due))` over canonical concepts clearing+due, or a per-invoice `collection_lag` metric (entity grain) feeding an `AVG` secondary metric (period grain). The metric formula computing over CANONICAL concepts is not source-coupling (the D330 Option C objection was about raw SOURCE fields).

4. CS-3 GATE ENFORCES 1-HOP (not transitive). A derived concept selected by a CC is proven observable iff EVERY compute input is directly present in an active OC. Drop the transitive recursion + cycle guard.

5. SOURCE-AGNOSTIC / NO BUILDER CHOICE. One canonical resolution per concept (Invariant I); the metric binds concepts and never sees production. A source produces a derived field iff it observes the inputs; otherwise the comparison moves to the metric DAG. This resolves the operator's Y1/Y2 question: there is nothing for a builder to choose — the CC resolves each concept once, and conflict (a source that BOTH observes a concept and could derive it) is resolved by the CC's own resolution_rules conflict policy at the canonical boundary, once.

WORKED EXAMPLES.
- clearance_time = date_diff(clearing, document): both inputs DIRECTLY observed on BSAD (AUGDT, BLDAT) → 1-hop, a valid canonical derived field; metric = plain AVG. THE clean D461 proof (build first).
- collection_lag = date_diff(clearing, due): `due` derived (1-hop date_add(baseline, terms)) → the subtraction is a METRIC op (secondary-metric DAG). due itself is a 1-hop canonical field. (Resolves the design-doc CB-005/CB-006 blockers without canonical chaining.)

CORRECTS.
- DEC-bc6be2: the date-derivation unlock STANDS (sequencing unchanged), but its MECHANISM moves from the observation boundary (date_offset OC transform — Invariant-I violation) to the canonical boundary (a 1-hop CC `date_add` derived field for `due`). The OC observes baseline+terms (field selection); the CC derives due.
- D461 design doc L2 (canonical_mapping → CC body) and L3 (transitive → 1-hop). L1 (date arithmetic is a canonical derived field) holds ONLY for the 1-hop case; the 2-hop case is a metric op (point 3). L4 (D330 function library) holds.

REPAIR LOCATION: B (contract semantics — the derived-field resolution grammar in the CC body) + D (the CS-3 evaluation-boundary gate).
INVARIANTS: I honored (derivation in the CC, at the canonical boundary — not the OC); II honored (1-hop prevents hidden intra-CO derivation; multi-hop only as the sanctioned forward metric DAG); III/IV/V/VI unaffected. PASSES the Foundation gate.

SCOPE OF THIS ADR: locks the home + hop limit + the metric-DAG boundary. It does not itself add DDL. The CC-body derived-field grammar shape (a `resolution_kind: compute` element in the CC body vs a new `derivations[]` key) is an implementation detail settled in the D461 design doc amendment. Runtime evaluation (Phase 2 / Bar-2) is unchanged in scope.
