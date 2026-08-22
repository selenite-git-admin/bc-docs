---
uid: DEC-9f7c18
title: "D531 authority caps are origin-scoped: not applicable to panel-origin certification payloads, retained for external-evidence origins"
description: "V-D8/CF-R4 citation caps are origin-scoped: skipped for declared run-origin (panel act IS the authority; citations must stay empty), retained byte-identically for exchange/checker; report exchange-era workflow blocks origin-gated likewise"
status: implemented
date: 2026-08-01T17:39:38.594Z
project: bc-core
domain: metrics
subdomain: metric-lifecycle/certification
focus: governance
---

# D531 authority caps are origin-scoped: not applicable to panel-origin certification payloads, retained for external-evidence origins

## Context

Found by building the certification decision writer (PR #612): the composed panel-origin decision/report failed validateDecision/validateReport ONLY on the D531 cap family — machinery structurally unsatisfiable for panel-origin because panels ground in exhibits over the frozen package, not publisher citations. Forcing satisfaction would mean fabricating publisher citations for panel judgements (the checker-fiction class, third appearance); dropping the caps globally would weaken the external-evidence controls D531 ratified. Origin-scoping resolves both: each origin keeps exactly the authority control that matches how its payloads actually derive authority. Aligned with DEC-dc5d52 (D531, authority by derivation), DEC-c48b0f (D541 clauses 2+4), and the PR #612 r1 P1 fix (origin is the caller's declaration, never payload shape) which supplies the enforcement point. Operator word 2026-08-01: "rule the D531 cap fork".

## Decision

1. THE CAPS' SCOPE IS THEIR THREAT MODEL. The D531 citation-cap machinery (decision V-D8: max axis score 5 requires a qualified non-DISCOVERY_ONLY, closure-bound citation; report CF-R4: scores above the policy cap require counted qualified publisher citations) exists to stop an EXTERNAL evidence author from claiming high confidence without qualified published sources. That threat model does not exist for panel-origin (run-origin) payloads: the platform composes them FROM the recorded panel act, whose grounding is exhibit reads over the frozen package — authority by derivation, which is D531's own doctrine.

2. RULING: for payloads validated under declared origin 'run', V-D8 and CF-R4 are NOT APPLICABLE and are skipped. The authority controls for panel-origin are, and remain: c8 (recorded panel act, PANEL_VERIFIED, valid roster registration), c13 (run corroboration: subject/panel/bytes/basis), c11 Arm R (byte custody from the run's own artifact), and the panel's own exhibit-grounding discipline recorded in seat outputs. Score authority IS the panel act.

3. NO SMUGGLING IN EITHER DIRECTION. Run-origin payloads MUST NOT carry counted publisher citations (claiming external authority the panel did not derive) — citations stay empty on run-origin; the validators refuse otherwise. Exchange/checker origins keep the caps byte-identically — this ruling narrows applicability by origin, it weakens nothing for external evidence.

4. REPORT RUN-ORIGIN ARM. The report-v5 validator's exchange-era demands that encode external-engine workflow (per-axis publisher citations arrays, reproduction_evidence, re_audit, affected_dependencies objects) are origin-gated with the caps: required for exchange/checker, not applicable for run origin. Per-axis rationales REMAIN required for run origin (they carry real panel prose). Panel grounding is NOT duplicated into the payload — it lives in the recorded panel run (S3 exhibit doctrine); the payload references the panel act.

5. The two characterization vectors pinned in certification-decision-writer.spec.ts flip to expect clean validation under origin 'run', closing the fork they were built to flag.
