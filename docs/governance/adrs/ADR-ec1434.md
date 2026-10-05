---
uid: DEC-ec1434
title: "Validation against a proof source is a tenant-plane evidence act: a deterministic comparator records in the bench tenant whether governed values match an outside-platform oracle"
description: "\"Validated against <source> for <scope>\" is derived from append-only tenant evidence written by a deterministic, tenant-scoped comparator; a match needs full two-way cell coverage of an explicit legal-entity x period scope with every input proved back to admissions from the bench world; never a state, never a certification input; no outcome ever rejects."
status: decided
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
- "Validated against <source> for <scope>" is derived from the newest record for that exact scope. A match needs full, input-proved cell coverage of the scope. It is never a state, never a certification input, and no other outcome ever rejects a metric.

Invariants I, III, IV, V and VI.

## Status and authority

- **Decided** on the operator's recorded grant `2026-10-05T02-13-20-149Z-d0995adb` (desk request 204), text sha256 `d0995adba24f2357f810a85b4c77f674b35fd6b9b06ddfdbfbbe7dad2953a724`. It approves this ADR as written at commit `319832cde4f428f5af6b64ee4ddebb2b29bb555f` (ADR sha256 `164f930eb5085a66c4fbbda53fba5b1c5c453b16884ba1497b9d31ad3c35b07e`), which Codex accepted with a boundary on gen-263fe9-03. Its third review round was authorized by grant `2026-10-05T02-05-54-741Z-fedacd9e` (request 203). The only changes since those bytes are this status and authority text and the boundary clarification below.
- **Boundary clarification (Codex, gen-263fe9-03; added under grant d0995adb).** Validating data that already exists needs a **fresh** source-identified admission, per-object canonical resolution and governed evaluation, not a metric-only re-evaluation over existing canonical objects. Wherever D5 or the Consequences say "a new governed evaluation" after P1 and P2 land, it means that full fresh chain.
- **Acceptance is of the design only.** P1 (TSK-9c7b32), P2 (TSK-1e8eaa), the oracle registry, the comparator and any positive validation record do not exist yet. Each is a separate unit with its own review.
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

**D1. Meaning, always bounded by a stated scope** (revised in Codex round 1). A certified metric version is **validated against** a proof source **for a comparison scope** when the **newest** validation record for (that metric version, that proof source, that scope) has outcome `match`.
- **A comparison scope** is an explicit set of legal entities × fiscal periods, with a canonical text key (the legal-entity codes and period keys, sorted). Every record carries one.
- **The word is always said with its source and its scope**, for example "validated against Odoo LC5 for KAVERI-IN, FY2025 Q1–FY2026 Q1". The vocabulary defines the proof "for a stated period" (`docs/reference/vocabulary.md`, the "validated against" row).
- **The unqualified "validated against <source>"** is allowed only as shorthand for the metric's **full declared scope**: the scope that source's oracle-of-record manifest declares for that metric (D3). A match on a narrower scope never yields the unqualified word.
- **Scopes are independent:** a match for one scope says nothing about any other.
- **Newest wins:** a later record for the same (metric version, proof source, scope) replaces the earlier one's meaning. A later `mismatch`, `incomplete_coverage` or `input_unbound` withdraws "validated" for that scope. The earlier record stays as history.
- The word is derived on read. It is never a state of the metric contract version and never an input to certification.

**D2. Plane.** Validation consumes produced values, so it is an **evaluation-plane (tenant) act**. It runs after certification, activation and release (DEC-ca8943 D3).
- It runs **tenant-scoped**, against the proof source's declared **bench tenant** only, over the standard tenant connection.
- Nothing is written on the platform plane.
- If a platform surface ever shows the word, that is a separate read projection (location F), designed later. It never triggers evaluation and is never a certification input.

**D3. Proof source.** Each proof source is declared once, in its committed **oracle-of-record manifest**:
- its code (for example `odoo-lc5`);
- its bench tenant (for `odoo-lc5`, the demo tenant Kaveri);
- its frozen bench identity: the dump sha256 and the world pin;
- its **source identity**, the value an admission run must record to prove its data came from that bench's world (D5);
- per metric, its **full declared comparison scope** (D1).

Another proof source (SFDC, Business Central) is another manifest, with its own bench.

**D4. Oracle.** The expected values are computed **outside the platform**, deterministically:
- no AI anywhere in the path (DEC-3300f3), and no BareCount object read;
- against the frozen bench, a read-only restore of the pinned dump;
- one committed query per oracle;
- a single runner writes a committed, hashed **oracle-of-record**: values, bench identity, each query's sha and its independence class (for example L4).

Nothing labels anything until the oracle-of-record is on main.

**D5. Governed side: the inputs must be proved, not assumed** (revised in Codex rounds 1 and 2). The comparator compares only the bench tenant's **governed** metric snapshots and evaluations, the normal campaign act and its records.

A snapshot row counts toward `match` only if the comparator **proves its full input tree** from recorded lineage and evidence. The tree is never assumed, and it is never inferred from a run-wide list:
1. **The snapshot row and its evaluation.** The snapshot row was produced by that evaluation, of that metric version, and its key is inside the record's scope (D6).
2. **Composites, recursively.** For a composite, every upstream snapshot the evaluation consumed is recorded on it (bc-core `governed-metric-persistence.adapter.ts:303-326, 420-468` at `4bae7f7`). Each one is proved by this same list, recursively, down to base evaluations. One unproved branch makes the whole row unbound.
3. **Base evaluations, per object.** Every canonical object a base evaluation consumed is named in that evaluation's own lineage. Each canonical object's own `evaluated_by` lineage names the admitted source objects it read. That per-object canonical lineage is TSK-1e8eaa (designed, not built), and it is never backfilled. The canonical resolution run's run-wide `admissionRunIds` (`ccv2-canonical-resolver.service.ts:347-359, 392-398, 464-475`) does **not** bind an object to its admission, and is not used as proof.
4. **Admission, per source object.** Each admitted source object belongs to an admission run that **recorded the proof source's source identity** (D3). Any missing or different identity anywhere in the tree makes the row unbound.

A comparison with any unbound row records `input_unbound`, never `match`. A coincidental equal value on unproved inputs is never validation evidence.

**Two prerequisites, stated plainly; neither exists today:**
- **P1, source identity at admission.** `progression.admission_run_context` (tenant migration 0004) pins contract versions and the filter, but not the extract or world.
- **P2, per-object canonical lineage.** This is TSK-1e8eaa. It is not retroactive, so canonical objects resolved before it lands can never be proved: their metrics need a new governed evaluation after P1 and P2 land. Whether to re-evaluate the demo tenant then is a Metric and operator decision.

Until both prerequisites land, every comparison resolves to `input_unbound` and nothing is validated. The design refuses rather than assumes.

**D6. The record and its coverage** (revised in Codex round 1). For each (metric version, proof source, scope, comparison), one append-only `evidence.evidence_object`:
- of the new code-level type **`metric_source_validation`**, whose `subject_ref` is the metric contract version;
- with exactly one outcome:
  - **`match`**: the **cell key** is the governed snapshot key: the legal entity, the period, and **every grouping dimension** of the metric's declared output grain (bc-core `governed-metric-evaluation.service.ts` `snapshotKeyColumns`). Coverage is exhaustive and two-way on full keys. Every governed snapshot row in scope has an oracle row with the same full key, and every oracle row in scope has a governed row. Every row is input-bound (D5) and agrees exactly at the metric's declared precision. An extra or missing grouped row on either side is never ignored;
  - **`mismatch`**: at least one bound cell present on both sides differs; it lists every diverging cell;
  - **`incomplete_coverage`**: at least one full-key row in scope, including any grouped row, is missing on either side; it lists the missing keys;
  - **`input_unbound`**: at least one cell's inputs could not be proved (D5); it lists them;
  - **`no_oracle_data`**: the oracle-of-record has no cells for this metric;
  - when several apply, the record takes the first in this order: `input_unbound`, `mismatch`, `incomplete_coverage`;
- with typed `evidence.evidence_record` context rows, so every key is in text columns, not JSON (DEC-1918d0 rule 1):
  - `proof_source`;
  - `comparison_scope` (the canonical scope key);
  - one `metric_snapshot` row and one `metric_evaluation` row per compared cell;
  - one `admission_run` row per proved admission run;
  - one `oracle_artifact` row (path@commit), whose sha is in the input references;
- with one `evidence.lineage_object` per compared evaluation, relationship `validated_by`;
- written atomically in the comparator's tenant transaction: the object, every context row and every lineage row together, with any archive published only after commit.

The comparison rule (exact at the metric's declared precision) is recorded with the result. A rerun is a new record, never an edit. **No DDL is needed**: the tenant evidence tables already carry free-text types and statuses and typed context rows (Codex, gen-263fe9-01).

**D7. Consequences of a result.** No outcome other than `match` (`mismatch`, `incomplete_coverage`, `input_unbound`, `no_oracle_data`) **ever** rejects, abandons or decertifies a metric. It stays "certified, not yet validated against <source>", with the recorded reason. A mismatch is triaged by its cause:
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
  - **IV:** every reference is explicit: snapshot and evaluation ids, the proved admission runs, the scope key, oracle path@commit and sha, bench dump sha and world pin, proof source.
  - **V:** validation references existing governed evaluations and never re-runs history.
  - **VI:** the result is emitted evidence, written in the act's transaction.
- **Design or execution act:** a design act. It declares the record and the act that DRIVE-2OCT §13a.1 named as missing.

## Consequences and order

1. **The prerequisites (D5):**
   - **P1:** admission records the extract or world identity it read. A separate design act and build unit (Platform with Demo); any tenant schema change is a migration with the operator's DB yes.
   - **P2:** per-object canonical lineage, TSK-1e8eaa (Platform; designed and approved with conditions).

   Until both land, every comparison resolves to `input_unbound`. After both land, the demo tenant's metrics need a new governed evaluation before any can be proved (Metric and operator decision).
2. **Demo:** confirm the S3 dump is the world drop Kaveri was admitted from, and that a local read-only restore is acceptable.
3. **Metric with Demo:** the oracle registry, DSO first: committed queries with typed rows, and each metric's full declared scope (D3).
4. **Platform:** the comparator and the code-level changes the existing seams lack (Codex, gen-263fe9-01):
   - the `metric_source_validation` type, the five outcomes and the `validated_by` relationship added to the allowlists;
   - `createEvidenceRecord` accepting the transaction executor, so the context rows commit atomically with the object (`createLineage` already does);
   - archives published after commit.

   Red-first cases:
   - an unproved input → `input_unbound`;
   - a missing cell → `incomplete_coverage`;
   - a diverging cell → `mismatch` with that cell listed, and no metric state change;
   - a full, bound, equal scope → `match`;
   - a grouped metric with one extra or missing group → `incomplete_coverage`;
   - a composite with one upstream branch from another world, or unproved → `input_unbound`;
   - a run-wide `admissionRunIds` alone never proves a row;
   - a later mismatch for the same scope withdraws the word;
   - a narrower-scope match never yields the unqualified word;
   - a rerun writes a second record.
5. DSO end to end, then family by family.

This ADR authorizes no build by itself; each build unit takes its normal review.

## Review

- **Codex round 1** (gen-263fe9-01): CHANGES REQUIRED, two blocking false-positive paths, both closed in this revision.
  1. **The word had no bounded scope.** D1 now keys the word to an explicit comparison scope with two-way cell coverage. D6 defines `match` as full, bound, equal coverage and adds `incomplete_coverage`; a later non-match withdraws the word for that scope.
  2. **The world pin alone did not bind the compared inputs.** D5 now requires proved lineage from snapshot to evaluation to canonical objects to admission runs that recorded the source identity, within scope. Otherwise the outcome is `input_unbound`. The missing admission-side identity is named as a prerequisite.

  Codex's build boundaries (evidence-record writer transaction, allowlists, atomic context rows, archives after commit) are carried into Consequences 4.
- **Codex round 2** (gen-263fe9-02): CHANGES REQUIRED, the final auditor round for this unit. Two residual false-positive paths, both closed in this revision.
  1. **Grouped output.** A cell was entity × period, but a governed snapshot key also carries every grouping dimension. D6 now keys cells on the full snapshot key, with exhaustive two-way coverage; an extra or missing grouped row is `incomplete_coverage`.
  2. **Composites and per-object binding.** A composite consumes upstream snapshots, not canonical objects, and the run-wide `admissionRunIds` does not bind an object to its admission. D5 now requires recursive proof through every upstream snapshot, down to per-object canonical lineage and source-identified admissions. P2 (TSK-1e8eaa) is named as the second prerequisite.

  Per the auditor-session rule, no third review is opened without the operator's direction.
