---
uid: DEC-633b2a
title: "D-code monotonic allocator - prevent concurrent-session drift"
description: "D-code monotonic allocator. Counter table + atomic endpoint + boot reconciliation from ADR files + MCP tool signature change. No UNIQUE constraint (24 historical dupes). Backfills 3 drift + 12 orphan ADRs."
status: implemented
date: 2026-04-15T05:49:19.983Z
project: barecount-devhub
domain: governance
migrated_from: legacy v2 archive
---

# D-code monotonic allocator - prevent concurrent-session drift

## Context

**Why now.** The race is real - observed this session (two Claude instances both picked D332). As concurrent Claude sessions become common (parallel worktrees, auto-commit hooks, scheduled tasks), the collision rate rises.

**Why within DevHub, not a separate service.** All sessions hit localhost:4000. Express single-threads requests. SQLite transactions are serializable. No distributed locking needed. A micro-service adds complexity without benefit.

**Why atomic counter table and not SELECT MAX.** MAX-based allocation races under concurrent reads. Counter + transaction is the simplest serializable primitive.

**Why drop UNIQUE.** 24 existing dupes. Adding UNIQUE would fail the ALTER or require destructive historical dedup. D-codes were never unique; honest beats aspirational.

**Why remove decision_code from MCP tool input.** If the tool accepts it, drift returns. Structural prevention beats discipline. The last manual D-code is this ADR itself (D334).

**Alignment**
- D221 (ADR-first): auto-generates its canonical file
- D268 (session discipline): structural prevention at the tool layer
- D305 (SSOT): counter is authoritative, not derived ad-hoc
- D332/D333: pattern-consistent - scanner-derived, bounded surface

## Decision

**Problem.** Today, devhub_decision_record accepts a user-supplied decision_code. Two concurrent Claude sessions can both pick the same D-number (observed: Sonnet 4.6 and Opus 4.6 both landed on D332). The decisions table has no uniqueness constraint and 24 existing historical duplicates (D210 4x, D232 4x). ADR filenames use DEC-xxxxxx UIDs, which are generated atomically via generateUid() with collision check - D-codes have no such protection.

**Decision.** Ship a monotonic D-code allocator within DevHub.

**v1 scope**
- New table decision_code_counter (id=1 singleton row, next_d integer)
- Boot-time reconciliation: scan legacy-v2/docs/decisions/ADR-*.md for decision_code frontmatter, set counter to max(DB_max, FS_max) + 1
- New endpoint POST /api/decisions/allocate-code - atomic SELECT+UPDATE in a db.transaction, returns { decision_code: "Dxxx" }
- Modified MCP tool devhub_decision_record: decision_code REMOVED from input schema. Tool calls /allocate-code internally. Breaking change.
- One-time backfill: insert rows for 3 D-drift ADRs (D327, D329, D331) and 12 orphan-UID ADRs

**Explicitly not doing**
- UNIQUE constraint on decisions.decision_code: 24 existing dupes make this impossible without destructive dedup. D-codes are henceforth treated as nicknames, not unique identifiers.
- Retroactive dedup of historical duplicates.
- External-writer detection (devs hand-writing ADR files): mitigated by boot reconciliation eventually catching up.
- Separate micro-service: DevHub is already the single allocation point.

**CLAUDE.md clarification (separate change this session)**
D-code is a human-readable nickname. DEC-xxxxxx UID is the canonical identifier. Code references should prefer UID.
