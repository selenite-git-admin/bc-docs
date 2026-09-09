---
uid: DEC-c99f72
title: "Platform schema capture authority: reviewed read-only capture script with hash-bound written operator authorization (D12 = B)"
description: "D12: baseline capture = reviewed read-only script in bc-db + hash-bound written operator authorization (simplified gate ①); launcher stays parked (D7 open)"
status: decided
date: 2026-09-09T09:41:44.331Z
project: bc-db
domain: database
subdomain: database/foundation
focus: capture-authority
---

# Platform schema capture authority: reviewed read-only capture script with hash-bound written operator authorization (D12 = B)

## Context

Operator decision 2026-09-09 ("approve W1.1 brief; D12 = B; D13 = yes") on the W1.1 design brief (bc-db PR #1). The launcher package was built for a de-drift flow that no longer exists, and its signing ceremony is the operator burden the ratified operating model (DEC-0e4547) removes; the lightweight path keeps the operator gate, keeps the evidence admissible under the pattern the auditor accepted for the foundation study (PR #747), and costs one reviewed script.

## Decision

**Policy (decided).** For the Platform DB Foundation Program's baseline capture (requirement FR-4c), the operator selects path B: a checked-in, read-only capture script in bc-db, authorized per run by a written, hash-bound operator statement — the simplified form of operator gate ① (acquisition authorization). The gate remains the operator's. The parked schema-acquisition launcher package (F7) and bc-core PR #746 are unchanged by this decision; their disposition remains decision D7.

**Three things this record distinguishes.** (1) *Path selection* — made here. (2) *Acceptance of the executable contract* — delegated to the exact-head, independently accepted W1.1 design brief (bc-db `docs/briefs/W1.1-custody-scope-capture-versions-2026-09-09.md`) and the capture script it governs; the brief specifies the connection and snapshot consistency contract, the per-connection read-only enforcement proved by fixture tests, the authorization and completion-receipt binding (validated before any connection; candidate set verified as an isolated commit before finalization), the observation coverage and secret exclusions, and the custody verification at the exact commit and on the fetched remote. Neither the selection nor this record accepts any particular script or run. (3) *Per-run authorization* — a separate written operator statement for each capture run, referring to the reviewed script bytes, the target database and cluster identity, and a validity window, accepted by the independent auditor before the script connects.

**Custody.** Where this record and the accepted brief differ on execution detail, the accepted brief at its exact head governs; this record carries only the policy choice.
