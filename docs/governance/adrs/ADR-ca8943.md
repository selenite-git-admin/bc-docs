---
uid: DEC-ca8943
title: "The metric directory is refactored in place and every member version passes a deterministic definitional entry gate (G1–G5) before it can be realized or certified"
description: "Refactor the metric directory in place (no rebuild; append-only history preserved). A deterministic, definitional entry gate (declarations resolve; definition is a function of the declared contract; concepts closed; definitional bindability to the canonical layer; definition completeness) runs at member-version creation and again at intake, realization and certification. Corrections are successor member versions; the generator names only declared bases. Plane-clean: the platform defines/certifies/releases and never needs a produced value. Template-derived certification is a separate later ADR."
status: proposed
date: 2026-10-03T14:30:22.219Z
project: bc-core
domain: metrics
subdomain: metric-directory/entry-gate
focus: governance
---

# The metric directory is refactored in place and every member version passes a deterministic definitional entry gate (G1–G5) before it can be realized or certified

## Summary

The directory model is sound and append-only. What fails is content (a generator template naming undeclared date bases) and the absence of any deterministic check that a definition matches its contract or can bind. Moving that check to the declaration boundary (location A/B) makes the certification panel a confirmation of meaning rather than the first filter. Invariants I, III, IV and VI.

## Status and authority

- **Proposed.** It moves to decided only on the operator's recorded grant at the bc-exchange desk. The operator adopted the proposal it records on 2026-10-03; the Chief Controller relayed that adoption, which is not authority by itself.
- **The proposal:** barecount-devhub PR 245, `artifacts/architect/clean-directory-2026-10-03/PROPOSAL-clean-prechecked-directory.md` @083ebf78. Measurements: Metric's barecount-devhub `artifacts/metric-audit/calibration-reframe/SEED-UNIVERSE-BKM-MEASUREMENT-2026-10-03.md` @62ae8e38 and `TSK-41ee58-DATE-BASIS-FIDELITY-ENUMERATION-2026-10-03.md` @1df2bb28.
- **Relation to other ADRs.** It extends DEC-b5c7ff (D506, the directory model) without superseding it. It builds on DEC-fa9424 (realization), DEC-85fd8d (rejection), DEC-4c8bee (the definition-completeness criterion), DEC-26f75a (the period_aggregate anchor_field) and DEC-a6cdae (contract-layer readiness).
- **Authors:** Architect, with Metric (directory meaning) and DB (schema). Tasks TSK-c940ca and TSK-7082ae.

## Context

Read at bc-core `origin/main`, bc-db `origin/main` and the live platform database, read-only, on 2026-10-03.

- **The directory model is append-only and versioned.** `fn_reject_mutation` covers member_version and realization_event; head guards require successors to cite their head (bc-db baseline `:2983-3258`, `:14186-14292`).
- **A definition is versioned per member version** (`member_version.definition_text`), and realization is an audited event (DEC-fa9424 D4).
- **No act creates a successor member version.** `POST members/:uid/version` authors only a missing v1, although the schema and the head guard support successors.
- **Nothing can record a pre-check result.**
- **The directory's definition generator writes `period_aggregate by ${taTerm}`** (the member's date-anchor concept) while emitting an anchorless `fiscal_period` gate (`metric-directory.service.ts:332-337`).
  - Of 67 generated definitions naming a date basis, 45 name a basis their contract does not declare. Eleven of those are on active metrics.
  - Four of the eleven are supplier-invoice counts whose wording is the only defect.
  - Seven sit on grains with no canonical contract. They are **unbindable definitions** that were certified without a bindability check.
- **The PE-MC evaluator has no reference to the definition text,** and the read-only survey found no other deterministic check comparing a definition to its contract. The certification panel is the only place this is judged today.
- **The ~900 entrants are mostly compositions** (about 770, built through the existing derived template), about 200 base measures, about 118–123 novel authorings, and about 9–10 concept gaps (Metric's measurement).

## Decision

**D1. Refactor in place; never discard.** The directory model stays. Every existing member, member version and realization is preserved (Invariants III and VI).
- A corrected definition is a **new member version** that cites its head, through a successor-version act to be built. The schema and head guard already support it.
- A definition that will not be built is rejected under DEC-85fd8d once migration 0035 is applied.
- A realization to a defective metric version is never rewritten. The corrected path supersedes it through MCF and asserts a new realization.

**D2. The entry gate, all definitional and source-agnostic.** One pure evaluator decides five checks from declarations and the canonical layer alone:

| Check | Refuses |
|---|---|
| **G1 Declarations resolve** | An unknown or inactive grain entity version, measure concept, anchor concept or gate shape |
| **G2 Definition is a function of the contract** | For a generated member: definition text ≠ the fixed generator's output for its declarations. For any member: a named date basis that is neither the gate's declared `anchor_field` (DEC-26f75a) nor, when no anchor is declared, the grain canonical contract's `posting_date_field` concept; or a currency promise that needs conversion (DEC-7bccf6, DEC-f4b2b0). Its statements come from the same derivation as the certification panel's `declared_semantics` exhibit. |
| **G3 Concepts closed** | Any referenced concept missing or inactive in the concept registry |
| **G4 Definitional bindability** | A grain with no active canonical contract in the platform canonical layer; an anchor, filter or required currency field not declared in that contract's resolved schema (DEC-a6cdae contract-layer readiness) |
| **G5 Definition complete** | A definition missing the measure, the population, the boundaries or the temporal basis (DEC-4c8bee point 3) |

**D3. Plane boundary.** The platform defines, certifies and releases, and never produces a value. Tenants produce and report.
- No gate check uses a tenant evaluation outcome, data readiness or chain-status colour.
- Certification never requires a produced value.
- Validation against a source is evaluation-plane evidence, after release.

**D4. Where the gate runs.** At member-version creation, and again at intake, at materialization, at realization (beside `fn_realization_event_guard`) and before certification. Realization and bindability are separate properties: the seven unbindable definitions show that a member can be realized to an unbindable metric version. A member version that fails is recorded as **not entry-ready**, with reasons, and is never silently fixed.

**D5. The record.** An append-only result per member version and evaluator version, with per-check rows (check code, outcome, reason). These are rows, not JSON (DEC-1918d0). They are a bc-db migration, presented with its DBCP for the operator's database yes before any build writes.

**D6. The generator** names only a declared basis: the gate's `anchor_field` when the intended anchor is a field of the grain canonical contract (DEC-26f75a); otherwise the contract's posting-date concept, or "per fiscal period". It never authors a fiscal-period aggregate on a grain without an active canonical contract; it flags it as blocked on that contract instead.

**D7. Migration.**
1. A read-only census of every current member version through the gate.
2. The generator fix.
3. Successor member versions for definitions that fail.
4. Audit-pending metric versions corrected before any certification.
5. Active failures superseded and re-certified when certification resumes.
6. Unbindable definitions: a canonical contract added for the grain, or the definition withdrawn. Not producing values for a tenant is not, by itself, grounds.

**D8. Out of scope.** Template-derived certification (certify a template's meaning once, then emit a per-instance record by a deterministic generation check) is a separate, later ADR. Inheriting a certification is not Foundation-viable (Invariant VI).

## Foundation gate

- **Repair location: A/B, the declaration boundary.** Definitions are checked against their declared contract when they enter. Correcting them in the panel or a read model (D–F) would be compensation. This is a design act (DEC-c48b0f item 5): the missing declaration is the entry standard itself.
- **Invariant I.** Meaning is judged once per definition, at the boundary, by a deterministic evaluator.
- **Invariant III.** Corrections are successors; nothing is edited or deleted.
- **Invariant IV.** G2 and G4 make each definition's date basis, concepts and canonical contract explicit and resolvable.
- **Invariant VI.** Each gate result is an emitted, append-only record.

## Consequences and order

1. Census (read-only) and the B/K/M measurement. The measurement is done.
2. The generator fix (TSK-41ee58) and the `declared_semantics` derivation (move 1), which G2 reuses.
3. The gate evaluator, plus the DBCP for its result tables (the operator's database yes).
4. The successor-version act, then migration.
5. ~900 intake through the gate.

This runs in parallel with the certification-reliability track. Certification stays paused under DEC-b5978c.
