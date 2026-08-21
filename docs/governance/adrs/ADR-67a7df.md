---
uid: DEC-67a7df
title: "Contract TESTING lifecycle stage with a governed delete disposition"
description: "Contracts gain a lifecycle stage (testing|governed); test/proof artifacts are deletable-from-testing, governed contracts stay archive/immutable."
status: decided
date: 2026-08-14T03:34:38.061Z
project: bc-core
domain: contracts
subdomain: contracts/lifecycle
focus: lifecycle
---

# Contract TESTING lifecycle stage with a governed delete disposition

## Context

The contract lifecycle had no stage for test/proof artifacts. Versions progress draft→…→superseded and the shell has only archived_at, so every artifact is treated as history and the only removal is archive — which PRESERVES noise (it still counts in scans/dials/lists). Surfaced when Unit-B proof runs left orphan OC shells in bc_platform_dev: archiving them was wrong (noise, not history) and the generic delete path was itself broken (dead cc_field_mapping reference — PR #688). Operator doctrine 2026-08-14: test/proof artifacts are noise, not history → their disposition is DELETE, not archive. This is the same logic as D564 (contamination/scaffolding → governed expunge): Invariant III protects EVALUATED state, not test scaffolding. Deleting a testing contract corrects/discards a trial; it does not rewrite governed history. Born-testing + auto-promote-on-activation makes the default safe (anything that ever produces evaluated state becomes immutable), and a DB-trigger guard makes the delete permission un-bypassable per the D564 hard rule (never disable the guard).

## Decision

Add a contract-level lifecycle stage, orthogonal to the per-version governance state (draft→review→approved→active→superseded):
- `testing` — a trial/proof artifact that has produced no committed evaluated state. Disposition: governed DELETE (evidence-emitting) OR promote to `governed`.
- `governed` — a real contract, immutable history under Invariant III. Disposition: archive/supersede only; DELETE forbidden.

Rules:
1. New contracts are BORN `testing` (provisional). Existing contracts are backfilled to `governed` (grandfather — they are real).
2. Promotion `testing→governed` is AUTOMATIC on version activation (the commit), and may also be explicit. It is ONE-WAY: `governed→testing` is forbidden (Inv III — real history cannot be re-labelled a test). So a contract can hold `testing` only while it has NO active version (no evaluated state); any contract that ever activates is `governed`/immutable.
3. DELETE is permitted iff: lifecycle_stage='testing' AND no active version AND no dependents (existing D075 blockers) AND an emitted evidence row exists. A `governed` contract can only be archived/superseded.
4. The delete guard is a DB-LEVEL, un-bypassable trigger (never disabled), mirroring D564's fn_source_catalog_delete_guard: it permits DELETE only via a narrow carve-out gated on emitted evidence. Evidence: append-only contract.contract_expunge_log, no FK to the deleted row (evidence outlives it).

Scope: the lifecycle_stage column + evidence log + delete guard are uniform across all contract family shells; birth-stage + promotion wiring lands first for observation/canonical/reader (the live Unit-B authoring surface), then SC/AC.

Foundation gate: repair location B (contract semantics — the stage is a declaration on the contract) primary + D (evaluation-boundary enforcement — guard/promotion/birth). Design act (declaring the stage + the one-way rule + delete-from-testing rule) named before the guard (net-vs-fix passes). Invariants: III (governed immutable, testing discardable, stage immutable once governed), I (stage set once at the authoring boundary), VI (delete emits evidence before permitting the delete).

Delivery is a separate governed DBCP (additive column + CHECK + governed→testing immutability trigger + contract_expunge_log + delete guard + backfill existing→governed), clone-rehearsed and operator-apply-authorized (migration-57-equivalent), followed by the code (authoring birth-stage, promotion, guard interaction, tests) through the normal package → Codex head-pinned PR → operator merge flow.
