---
uid: DEC-253be2
title: "External metric audit — intrinsic vs source-realization audit-request split, per-realization claim scoping, SAP ECC as first realization-audit ground"
description: "Metric onboarding emits two audit requests (intrinsic C1 unchanged + future source-system-realization-audit-request-v1); realization failure blocks only per-source calculator-grade claim; ~370 audit population stays on SAP ECC, Oracle Fusion later as coexisting second realization program"
status: decided
date: 2026-07-13T07:36:27.688Z
project: platform
domain: metrics
subdomain: external-audit
focus: audit-request-identity
---

# External metric audit — intrinsic vs source-realization audit-request split, per-realization claim scoping, SAP ECC as first realization-audit ground

## Context

A single combined audit request conflates two different assurance objects with different lifecycles: the intrinsic metric (stable across sources, re-audited on definition/formula/package change) and the per-source realization (re-audited on source mapping/version change). Separating identities keeps intrinsic decisions durable when source catalogs evolve, gives each realization its own NC and re-audit history, and makes claim language honest ("calculator-grade for SAP ECC" vs global). Staying on SAP ECC for the audit population converts its documentation ambiguity from liability into the strongest available pressure test of contextual audit — and preserves the substantial evidence base already accumulated — while the coexistence rule keeps the door open for additional realizations over the same MCVs without re-adjudicating intrinsic decisions.

## Decision

Founder direction 2026-07-13, aligned with the external auditor (Codex) in the metric-audit program thread. Four decisions:

1. TWO AUDIT-REQUEST IDENTITIES PER METRIC. A metric onboarding event creates two separate audit requests, not one combined request:
   - INTRINSIC metric audit request — structural + definition + formula + canonical source-field meaning. This is what the pinned `metric-audit-request-v1` (C1) already represents; it carries NO source-scope coordinate and stays as-is.
   - SOURCE-SYSTEM REALIZATION audit request — exact source release + tables/fields + joins + filters + mapping package. Introduced later as a separate `source-system-realization-audit-request-v1` schema; C1 is NOT reopened to absorb it.
   They may be launched together and presented as one onboarding workflow, but they require separate identities, reports, decisions, NCs, and re-audit histories.

2. TRIGGER MODEL (once Source Catalog onboarding is governed): new source mapping/version admitted → identify every affected MCV → emit source-realization audit requests → preserve the existing intrinsic metric decisions untouched.

3. AUDIT POPULATION STAYS ON SAP ECC. The ~370-candidate audit program returns to SAP ECC for the realization layer: substantial SAP evidence and mappings are already accumulated; completing SAP exercises the most difficult and ambiguous source system, which is itself proof of the audit machinery; REJECT and OPERATOR_REVIEW results are useful outputs of the program, not failures. Oracle Fusion Cloud may later run as a SECOND independent source-realization program over the same MCV population; SAP and Oracle results coexist — neither supersedes the other.

4. BLOCKING SEMANTICS (claim scoping):
   - An intrinsic (definition/formula contextual) failure blocks calculator-grade activation of the MCV.
   - A source-realization failure blocks only the claim "calculator-grade for <that source system>" — it does not globally block the MCV or any other source realization.
   - Absence of live-tenant validation for a source is DISCLOSED and may cap confidence, but does not stop completion of the documentation-grounded audit population.

Program shape: complete intrinsic + SAP ECC realization audits for the current population, accept honest PASS/REJECT/OPERATOR_REVIEW outcomes, then repeat only the source-realization layer for Oracle Fusion Cloud.
