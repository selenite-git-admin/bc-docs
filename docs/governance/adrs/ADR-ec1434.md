---
uid: DEC-ec1434
title: "Validation against a proof source is a tenant-plane evidence act: a deterministic comparator records in the bench tenant whether governed values match an outside-platform oracle"
description: "\"Validated against <source>\" is derived from append-only tenant evidence written by a deterministic, tenant-scoped comparator of governed evaluations against a committed oracle-of-record on a frozen bench; never a state, never a certification input, a mismatch never rejects."
status: proposed
date: 2026-10-03T16:00:39.755Z
project: bc-core
domain: metrics
subdomain: metrics/validation
focus: governance
---

# Validation against a proof source is a tenant-plane evidence act: a deterministic comparator records in the bench tenant whether governed values match an outside-platform oracle

## Summary

A certified metric is **validated against a proof source** when its governed produced values match an independent computation made outside the platform from that source's data. This ADR decides what records that, where, and by what act.

- A deterministic, tenant-scoped comparator compares the bench tenant's governed evaluations with a committed oracle-of-record computed on a frozen copy of the source.
- It writes an append-only evidence record in that tenant.
- "Validated against <source>" is derived from the newest record. It is never a state, never a certification input, and a mismatch never rejects a metric.

Invariants I, III, IV, V and VI.

## Status and authority

- **Proposed.** The operator decides, through the Chief.
- **Proposal:** barecount-devhub PR 242, `artifacts/architect/panel-grounding-2026-10-03/DESIGN-move3-lc5-validation-at-scale.md` @`37cbdff9`, with its finalization section.
- **Implements** the design act DRIVE-2OCT §13a.1 and the vocabulary row "validated against *source*" (`docs/reference/vocabulary.md`, addendum grant `12be0a4c`), which names this record as "not yet built".
- **Relation to other ADRs.**
  - It applies DEC-ca8943 D3 (validation is evaluation-plane evidence, after release).
  - It keeps validation separate from certification (DEC-c48b0f; DEC-793e13, self-certification).
  - It uses the existing tenant evidence and lineage stores (DEC-48d222, "no proof, no record"; D575, tenant evidence immutability).
  - It supersedes no ADR.
  - **The drive's earlier wording** that validation is a platform-plane act read through a governed seam (DRIVE-2OCT §1.1, §4a, §13a.1) predates DEC-ca8943 D3. It is withdrawn by the drive's four-phase section (TSK-c59b5d).
- **Author:** Architect (SES-b9b0ef), with Metric (the oracle registry), Platform (the comparator) and Demo (the bench). Task TSK-fa0e4b, move 3.

## Context

Read at bc-core `origin/main` `4bae7f7`, bc-db `origin/main` and bc-demo `origin/main` `91e7e6bf`, on 2026-10-03.

- **The governed side already evaluates many metrics in one tenant-scoped act.**
  - `POST t/metric-evaluation-campaigns` (`src/boundary/campaign-evaluation.controller.ts:62-68`, `@TenantScoped`) runs a declared scope in DAG order, bases before composites (`campaign-evaluation.service.ts:1-14`).
  - Each evaluation is recorded append-only in the tenant: `progression.metric_evaluation`, with its evidence and lineage.
- **Nothing records a validation yet.** There is no validation or proof-source table in bc-core or bc-db.
- **The tenant evidence store can hold one without a schema change.**
  - `evidence.evidence_object` (`baseline/tenant/0000_tenant_skeleton.sql:234-248`): a free-text `evidence_type`, `subject_ref`, `outcome_status`, input and output references, and a hash chain.
  - `evidence.evidence_record` (`:255-263`): typed context rows.
  - `evidence.lineage_object` (`:270-278`).
  - All three are append-only (`evidence.prevent_mutation`, `:1442-1459`).
  - Writes go through `EvidenceService.createEvidence(dto, tx, deferredArchives)` (`src/evidence/evidence.service.ts:67`). Evidence types are a code-level list (`src/types/governance.ts:112`).
- **The oracle side is not yet a machine.**
  - The Foundry's answers are hand-run SQL with prose expected values, pinned to world drop `20260905T031823`.
  - Its 908 L4 rows were recomputed independently by a second model (`MC/STUDY-GOVERNANCE.md`).
  - A `pg_dump` of v3_lc5 is in S3 (`U4-AWS-RUNBOOK.md`).

## Decision

**D1. Meaning.** A certified metric version is **validated against** a proof source when the **newest** validation record for (that metric version, that proof source) has outcome `match`.
- The word is derived on read. It is never a state of the metric contract version and never an input to certification.
- It is always said with its source (vocabulary rule).

**D2. Plane.** Validation consumes produced values, so it is an **evaluation-plane (tenant) act**. It runs after certification, activation and release (DEC-ca8943 D3).
- It runs **tenant-scoped**, against the proof source's declared **bench tenant** only, over the standard tenant connection.
- Nothing is written on the platform plane.
- If a platform surface ever shows the word, that is a separate read projection (location F), designed later. It never triggers evaluation and is never a certification input.

**D3. Proof source.** Each proof source is declared once, in its committed **oracle-of-record manifest**:
- its code (for example `odoo-lc5`);
- its bench tenant (for `odoo-lc5`, the demo tenant Kaveri);
- its frozen bench identity: the dump sha256 and the world pin.

Another proof source (SFDC, Business Central) is another manifest, with its own bench.

**D4. Oracle.** The expected values are computed **outside the platform**, deterministically:
- no AI anywhere in the path (DEC-3300f3), and no BareCount object read;
- against the frozen bench, a read-only restore of the pinned dump;
- one committed query per oracle;
- a single runner writes a committed, hashed **oracle-of-record**: values, bench identity, each query's sha and its independence class (for example L4).

Nothing labels anything until the oracle-of-record is on main.

**D5. Governed side.** The comparator compares only the bench tenant's **governed evaluations**, the normal campaign act and its records.
- **Precondition:** the bench's world pin equals the world the bench tenant was admitted from, checked against admission evidence.
- If it does not, the act refuses, because every comparison would be noise.

**D6. The record.** For each (metric version, proof source, comparison), one append-only `evidence.evidence_object`:
- of the new code-level type **`metric_source_validation`**, whose `subject_ref` is the metric contract version;
- with outcome `match`, `mismatch` (holding the diverging cells) or `no_oracle_data`;
- with typed `evidence.evidence_record` context rows:
  - `proof_source`;
  - one `metric_evaluation` row per compared evaluation;
  - one `oracle_artifact` row (path@commit), whose sha is in the input references;
- with one `evidence.lineage_object` per compared evaluation, relationship `validated_by`;
- written in the comparator's tenant transaction, through the existing evidence seam.

The comparison rule (exact at the metric's declared precision) is recorded with the result. A rerun is a new record, never an edit. **No DDL is needed.**

**D7. Consequences of a result.** A `mismatch` or `no_oracle_data` **never** rejects, abandons or decertifies a metric. It stays "certified, not yet validated against <source>", with the recorded reason. A mismatch is triaged by its cause:
- the definition: Metric;
- the engine: Platform;
- the oracle or the bench: Demo with Metric.

Any change goes through that owner's governed path, never an automatic action.

**D8. Order.** One-then-many. DSO comes first, end to end: bench restore, DSO oracle on main, campaign, comparator, one record. Then family by family, the L4 oracle rows first. Each metric is validated **immediately after** its certification (DRIVE-2OCT rule 13), so a certified, unvalidated value is visible on the demo tenant for as short a time as possible (DEC-c220e4).

## Foundation gate

- **Repair location:**
  - **E**, a recorded act and its evidence;
  - **F**, the derived word.

  Not B: the contract's meaning is judged at certification, and validation proves values, not meaning. Not D: the evaluator is untouched; validation reads its records.
- **Invariants:**
  - **I:** the oracle never produces a platform value; it is only compared against.
  - **III:** records are append-only; a rerun is a new record.
  - **IV:** every reference is explicit: evaluation ids, oracle path@commit and sha, bench dump sha and world pin, proof source.
  - **V:** validation references existing governed evaluations and never re-runs history.
  - **VI:** the result is emitted evidence, written in the act's transaction.
- **Design or execution act:** a design act. It declares the record and the act that DRIVE-2OCT §13a.1 named as missing.

## Consequences and order

1. **Demo:** confirm the S3 dump is the world drop Kaveri was admitted from, and that a local read-only restore is acceptable.
2. **Metric with Demo:** the oracle registry, DSO first, as committed queries with typed rows.
3. **Platform:** the `metric_source_validation` type code and the tenant-scoped comparator, with red-first cases:
   - a world-pin mismatch refuses;
   - a mismatch records the diverging cells and changes no metric state;
   - a rerun writes a second record.
4. DSO end to end, then family by family.

This ADR authorizes no build by itself; each build unit takes its normal review.
