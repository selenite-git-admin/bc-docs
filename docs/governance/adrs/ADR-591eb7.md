---
uid: DEC-591eb7
title: "Single modular SoT → generated platform monolith + CI parity gate vs live/golden"
description: "Target model for TSK-3f52d7: unify the platform-DB schema on the modular set, generate the monolith from it, gate fresh-build ≡ live parity in CI, repoint docker-compose, correct stale CLAUDE.md."
status: proposed
date: 2026-09-08T07:11:01.942Z
project: bc-core
domain: infrastructure
subdomain: platform-db/schema-custody
focus: build-tooling
---

# Single modular SoT → generated platform monolith + CI parity gate vs live/golden

## Context

No rationale recorded.

## Decision

PROPOSED (design-first; awaiting operator confirmation before any reconciliation edit — authorizes NO schema/DDL change).

TARGET MODEL:
(1) Single Source of Truth = the modular set docker/redesign/02-platform-tables/*.sql (00..14 + genesis 15/16), reconciled to faithfully equal intended LIVE bc_platform_dev structure; the ONLY hand-edited schema artifact.
(2) The monolith 02-platform-tables.sql becomes a GENERATED artifact — deterministic concat of the modular files in _all.sql order (checked-in generator); never hand-edited again; header marks it generated.
(3) A CI parity gate proves per-PR that a from-zero build from the modular SoT is STRUCTURALLY EQUIVALENT to the live/golden baseline, AND that the regenerated monolith is byte-identical to the checked-in one; fails closed. Reuses scripts/comparator canon+compare vs a golden-dump restore into a fresh scratch_* DB.
(4) docker-compose repoints to the GENERATED monolith only AFTER the gate is green (current hand-maintained monolith stays bootstrap until then — no broken-deploy window).
(5) Correct the stale CLAUDE.md line ("monolith is a generated aggregate, do not hand-edit — keep in lockstep until the generator lands") once the generator makes it true.

PHASES (each its own DBCP+review-gated unit): P0 this session = ADR + operator confirmation (read-only). P1 = full COLUMN+CONSTRAINT drift audit (read-only) vs live oracle → per-divergence classification. P2 = reconcile modular to live: add the 8 missing live tables + column back-ports, drop the 2 stale tables (contract.chain_status, operations.audit_log), fix 07-operations.sql:229 (COALESCE-in-UNIQUE → partial unique index), complete _all.sql (add 07a + 12). P3 = generator + CI parity gate. P4 = repoint docker-compose + fix CLAUDE.md.

HARD GATES: no schema change without present→approve→apply; live bc_platform_dev is the ORACLE, never mutated by this task (source+generator+CI only); keep the current monolith as bootstrap until the generated one passes parity; scratch builds on disposable scratch_* only; read-only live via REPEATABLE READ READ ONLY.

FOUNDATION GATE: build-tooling + schema-custody reconciliation (DEC-b1a286 mechanism), not an evaluation/contract/metric-meaning change — A–F boundary taxonomy N/A; primary act = DESIGN. Does NOT supersede DEC-b1a286 — enforces its stated intent (modular=SoT, monolith=generated). Precedent (do NOT redo): PR #730 (merged 9ebd0af0) fixed only the master/source genesis subset + applied archived_at to live (schema_migration_event seq 9). Full rationale + measured evidence in the rationale field and the committed ADR file.
