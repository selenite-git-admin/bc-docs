---
uid: DEC-d3b916
title: "Certification roster registrations are governed by D541: the roster-pin CHECK moves from DEC-05815d to DEC-c48b0f"
description: "Roster-pin CHECK moves to DEC-c48b0f (D541) as strict successor; D536 stays the calibration-methodology authority cited via calibration_evidence_ref; registration = operator judgement with evidence, not computed clearance; one DBCP"
status: decided
date: 2026-08-01T17:48:41.423Z
project: bc-core
domain: metrics
subdomain: metric-lifecycle/certification
focus: governance
---

# Certification roster registrations are governed by D541: the roster-pin CHECK moves from DEC-05815d to DEC-c48b0f

## Context

The CHECK pinning governing_decision_uid = 'DEC-05815d' was discovered during the s6 rehearsal battery and flagged in the s6 package; Codex's s6 boundary confirmed it blocks any real production roster registration until a successor decision exists. D541 renamed the discipline (audit → certification) and defined panel 2's role; a roster registered today under the D536 literal would claim governance by a framing the platform retired. Clause 3 exists because the last calibration run (r23) returned fit=false on a corpus subsequently shown structurally broken (unanswerable negative, near-vacuous attribution): pretending a clean computed fitness basis exists would be dishonest, and blocking registration forever on a retired corpus would be ceremony. The operator's explicit registration act with cited evidence is the honest middle. Operator word 2026-08-01: "rule the DEC-05815d roster-pin successor".

## Decision

1. A panel roster REGISTRATION binds to the decision that gives the roster its authority to gate. Under DEC-c48b0f (D541) that is the certification doctrine itself: panel 2 (assessor/adversary/moderator) certifies the frozen package, and certification gates activation. The CHECK constraint on mcf.audit_panel_roster_registration.governing_decision_uid therefore moves from the literal 'DEC-05815d' to the literal 'DEC-c48b0f'. Strict successor, not a set: production holds ZERO registrations, so nothing historical needs the old literal, and a two-member set would leave a lane for registering new rosters under superseded framing.

2. DEC-05815d (D536) is NOT superseded by this decision. It remains the calibration-methodology authority: the r5–r23 corpus lineage, the fitness predicate, the seat/roster mechanics. Its evidence stays exactly where it already lives — calibration_evidence_ref on the registration row (format-CHECKed name=sha256:hex) cites the calibration artifacts produced under D536 methodology.

3. Registration content under D541: calibration_evidence_ref MUST cite real calibration evidence for the seats being registered (the r22/r23 corpus reports for the qwen/deepseek/kimi roster). The fitness question those runs left open (fit_for_registration=false on a corpus later found structurally broken) is acknowledged, not laundered: the registration's evidence ref points at what was actually measured, and the operator's registration act — authorized_by — is the explicit acceptance of that evidence basis. Registering is an operator judgement recorded with its evidence, not a computed clearance.

4. Implementation is one DBCP: drop the old CHECK, add the new literal CHECK, companion rollback guarded against existing D541-governed rows; rehearse on clone (new literal inserts, old literal refuses, malformed refuses); operator-run production apply per §0 act 1.
