---
uid: DEC-ae331f
title: "Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria"
description: "Platform commits to ISO 27001 readiness posture now with certification after pilot evidence; SOC 2 Type I first on Security + Confidentiality + Processing Integrity, with Availability and Privacy added per maturity gates."
status: decided
date: 2026-04-24T02:49:40.968Z
project: bc-docs
domain: governance
subdomain: compliance
focus: certification
migrated_from: legacy v2 archive
---

# Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria

## Context

# Rationale

Enterprise buyers require a declared compliance posture before engaging. Naming the pursuit as a staged decision (rather than as aspirational) lets the platform align its documentation, control evidence, and operational discipline to a concrete target from the earliest v3 chapters forward. Three specific choices need justification:

**Why staged rather than all-at-once.** A platform that commits to all five SOC 2 Trust Service Criteria at Type II before it has sustained operation evidence would either overstate its actual posture or fail audit. Staging acknowledges the reality: Security, Confidentiality, and Processing Integrity are supported by the platform's structural invariants and can be evidenced from day one; Availability requires sustained operation; Privacy requires a specific product-scope posture that may or may not obtain.

**Why ISO 27001 readiness now, certification later.** Formal certification is expensive (external auditor engagement, evidence preparation cycles, gap remediation). Engaging before pilot evidence exists means paying for an audit of a platform that has not yet operated. Establishing readiness now means the platform is defensibly aligned with the standard when pilot begins, and the certification engagement runs against a mature operating record.

**Why record this as an ADR now (Session 2).** v3 documentation is built under voice spec §2 and editorial gates §3, which require every invariant-grade claim to cite a governing source. Chapters 27 and 28 need an ADR to cite; drafting those chapters in later sessions without this ADR in place would create either orphan claims or citation drift. Recording the pursuit now resolves both concerns.

Source for this decision: DevHub plan PLN-4c9700 (ISO 27001 Gap Analysis & Improvement Roadmap), founder instruction in Session 1 review (Codex-reviewed), and the outline §4.7 scope of Chapters 27 and 28.

# Decision

BareCount pursues ISO 27001 and SOC 2 compliance in a staged sequence. The pursuit is declared as a first-class platform decision so that v3 documentation, controls, and evidence paths are aligned to a named target from Session 2 onward, rather than accruing retroactively after pilot.

## ISO 27001

- **Readiness posture — now.** The platform establishes ISO 27001 readiness as its operating posture. Governance, access control, change management, risk management, vendor management, and incident management policies are drafted as first-class v3 artifacts (Chapters 24, 26, 27, 29 and related policy documents). Evidence of control operation accrues in Evidence Objects, change records, session audit trails, and the ADR registry from this decision forward.
- **Certification — after pilot evidence.** Formal certification engagement with an accredited body begins only after pilot evidence exists — that is, after the platform has operated under its declared controls with real tenant data for long enough to produce defensible evidence packs. No external auditor engagement is initiated before pilot.
- **Evidence location.** Chapter 27 (ISO 27001 Conformance) maps each Annex A control to either a platform-enforced invariant, a policy document, or an operational procedure. The detailed control crosswalk lives as a generated appendix table, not as separate chapters.

## SOC 2

- **Type I first, Type II after one operating window.** SOC 2 pursuit begins with Type I (control design as of a point in time). Type II engagement (control operation over a period) begins only after one real operating window with sustained control operation.
- **Initial criteria — three, not five.** Type I pursues a reduced set of Trust Service Criteria: **Security, Confidentiality, Processing Integrity.** These three are supported by the platform's structural invariants (Chapter 2), data model (Chapter 17), access model (Chapter 26), evidence model (Chapter 12), and change discipline (Chapter 24 and DEC-ebf0b4 / D268).
- **Availability — staged behind maturity gate.** Availability is added only when uptime, observability, and incident discipline are demonstrably mature. Specific signals: one full operating window without SLO breach, observability stack fully instrumented, incident response documented with post-mortem discipline. Availability is not pursued before these signals are met.
- **Privacy — conditional on product scope.** Privacy is added only if product scope grows to include regulated personal data beyond incidental identity and admin data. If the product continues to handle primarily business data (invoices, metrics, canonical evaluations of enterprise state), Privacy remains out of scope.

## What this decision does NOT commit to

- External auditor selection, timing, or scope — out of scope for this ADR; a separate decision when pilot is complete.
- SOC 2 Type II timing without Type I first — explicitly refused.
- Privacy Trust Service Criterion by default — added only if scope justifies.
- Adding additional criteria (e.g. GDPR, HIPAA) to the stage gate — tracked separately if product scope warrants.

## Sequencing

1. **Session 2 (now):** this ADR recorded; Chapters 27 and 28 of v3 scoped with staged pursuit in their outlines.
2. **Sessions 17–20:** Chapters 26, 27, 28 drafted in single-chapter sessions; evidence paths declared for each control.
3. **Pilot readiness:** when v3 is locked and platform has tenant operation, readiness is reviewed.
4. **Pilot window:** sustained operation with real tenant data; evidence accrues.
5. **Post-pilot:** certification engagement begins for ISO 27001; SOC 2 Type I engagement begins with Security + Confidentiality + Processing Integrity.
6. **Post-Type-I:** Type II engagement on the same three criteria.
7. **Future:** Availability added when maturity gates pass; Privacy added if scope warrants.
