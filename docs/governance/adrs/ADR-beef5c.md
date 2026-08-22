---
uid: DEC-beef5c
title: "Record-identity doctrine: three-class rulebook for BC identity_role + additive-first-declaration (amends DEC-02f5a9)"
description: ""
status: decided
date: 2026-07-04
project: bc-core
domain: contracts
decision_code: D489
subdomain: semantic-vocabulary
focus: identity
---

# Record-identity doctrine: three-class rulebook for BC identity_role + additive-first-declaration (amends DEC-02f5a9)

> **Provenance.** Re-materialized on 2026-08-22 (SES-c2bd78) from the DevHub decision registry (`decision_text`, row created 2026-07-04); the ADR file had never been written to bc-docs (registry `file_path` pointed at the pre-D373 `docs/adrs/` location). Content below is the registry text verbatim. Frontmatter per D373/D334.

## Decision

Operator-locked 2026-07-04 (TSK-9fc313), gating Wave D of BCF Enrichment Program-2. Settles how every non-finance entity declares record identity via business_concept.identity_role, closing the parked HR-event and CRM-record questions from Waves A and C.

## The three-class rulebook (one question per entity: how does the business point at one record?)

CLASS 1 — DOCUMENT. A business-visible record number exists. The number is an identity-bearing VALUE property (+ qualifiers where the business genuinely needs them, e.g. Customer Invoice = {customer, legal entity, fiscal year, document number}); master references stay DESCRIPTIVE. Covers all finance documents (existing precedent) and every Wave-D ITSM record (incident/change/request number). Case entities (Grievance, HR Service Inquiry) are Class 1 IF a visible case number attests.

CLASS 2 — EFFECTIVE-DATED SUBORDINATE. No own number; the business addresses the record as \"the X OF {master} EFFECTIVE {date}\". Master reference is IDENTITY-BEARING + the effective date/period is IDENTITY-BEARING (+ a second reference where real, e.g. Program Enrollment + program). Covers Promotion, Separation, Hire, Compensation Change, Program Enrollment, Timesheet. In-substrate precedent: Credit Status = {customer (identity-bearing ref), effective date (identity-bearing value)}. Evidence shape is business-visible and standards-attestable: SAP PA PERNR+BEGDA, Workday worker + effective date.

CLASS 3 — SOURCE-IDENTIFIED. No business-visible identity exists at all. DECLARE NO IDENTITY-BEARING PROPERTIES — the empty set is the honest statement. Per-record identity is source-assigned and binds at the Canonical Contract grain[] (repair-location C), where tenant/source identity legitimately lives (DEC-02f5a9 §1 tenant-binding principle). Covers Opportunity, Lead, Sales Activity, Customer Contact, Recognition Event. This is a RULING (no visible identity exists), not a deferred gap; a tenant that genuinely uses visible record numbers can add a Class-1 identity BC later (additive).

Two hard guards: (a) NEVER fabricate composite identity from mutable fields (customer+name+date) — a mutable identity is worse than none and violates the immutability the identity set exists to provide; (b) system GUIDs stay out of the vocabulary (implementation_artifact — panel already enforces). Class is assigned per-entity at packet-prep by field attestation.

## Resolved open questions
- HR event -> employee = IDENTITY-BEARING (Class 2). Credit Status is the in-substrate precedent; the Maker was correct in both parked runs. Leaving them descriptive would leave the entities permanently identity-less despite the business addressing them as employee + effective date.
- CRM record identity = DELIBERATELY EMPTY (Class 3). Identity binds at CC grain, not vocabulary.

## Doctrinal amendment to DEC-02f5a9 §5 (the supersession rule)
DEC-02f5a9 / business-concept-registry.md §5: \"Changing an entity's identity-bearing property set is supersession — a new entity.\" This ADR CLARIFIES its scope: the FIRST declaration of identity on a previously identity-LESS entity (empty set -> non-empty) is ENRICHMENT COMPLETION (additive), NOT entity supersession — PROVIDED the entity has no consuming artifact. Once any OC/CC/MC binds the entity, identity change reverts to full entity supersession per §5. This is not a loosening of Invariant III; it is a precise statement of III's scope — the supersession rule protects produced evidence and finalized references from historical rewrite, and where none exist, none is rewritten.

## Foundation Invariant Check (MANDATORY gate — repair-location B, contract semantics)
Ran the six-invariant test; VERDICT: within foundational limits.
- I (meaning once): PASS. Class 3 places the per-record identifier at CC grain (C) where source-assigned identity actually lives — not lower-layer compensation, because no business-visible identity exists at B to compensate for. Vocabulary identity (B) and concrete per-record id (C) are distinct meanings, each evaluated once at its own boundary.
- II (ordering fixed): PASS. Identity DAG stays acyclic — all Class-2 targets (Employee, program) are simple master entities; no cycle, no back-reference.
- III (immutability): PASS WITH GUARD. BC-level flip is inline-mint supersedeBusinessConcept (old descriptive BC superseded, new identity_bearing coexists — no active-row mutation). Entity-level additive-first-declaration is III-clean ONLY because nothing consumes these entities. EMPIRICALLY VERIFIED 2026-07-04: 0 MCF metrics on these grains, 0 metric_variable_binding refs, 0 metric_computed_dimension_ref refs, 0 canonical_contract_version referencing any of the 28 active BCs. GUARD (binding): additive-first-declaration applies only while no consuming artifact exists; on first consumption, revert to §5 supersession.
- IV (explicit references): PASS (improves). Class 2 master-ref is a typed entity reference; Class 3 pushes the record id to explicit CC grain[] rather than smuggling it into vocabulary.
- V (non-replayable): N/A. Authoring-time declaration; no evaluation runs.
- VI (evidence emitted): PASS. Declarations emitted through the governed panel / BC-correction surface with certification records + named-field attestation; not inferred.
Three pre-action questions: (1) location B because identity_role is a vocabulary declaration; (2) upper layer A is not underspecified — sources DO emit PERNR+BEGDA, we are not tuning source shapes; (3) not compensating at a lower layer — Class 3 correctly places per-record id at C.

## Execution (governed, within the locked design)
1. Re-run the 2 parked packets (Promotion->employee, Separation->employee) with identity_bearing + PERNR/BEGDA-shape evidence via the panel (amended GLM-5-moderator roster).
2. Wave-C completion: flip the master-ref + effective-date edges on Hire, Program Enrollment, Timesheet to identity_bearing (and author Separation's missing effective date) via the BC-correction identity_role flip (inline-mint supersede).
3. No CRM action. Wave-D packets carry the rulebook; ITSM is all Class 1, so the identityRole split that caused the parks cannot recur there.

Amends (does not supersede) DEC-02f5a9. References the finance identity substrate (45 identity-bearing BCs, Credit Status precedent) and the D469/D471 finding that PE-MC-2/7 walk reference-KIND BCs with no identity_role filter (so identityRole is vocabulary truth, not an MCF-eligibility lever).
