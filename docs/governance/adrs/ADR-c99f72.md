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

For the Platform DB Foundation Program's baseline capture (requirement FR-4c), the capture authority is a checked-in, auditor-reviewed, read-only capture script in bc-db (every statement inside BEGIN TRANSACTION READ ONLY; pg_dump --schema-only with owners, privileges and comments plus catalog queries; exact command strings, raw outputs and a sha256 manifest; executed inside the pinned engine container so tool versions match the version contract). It runs only after a hash-bound written operator authorization naming the target database and cluster system identifier, the script's git blob hash and a validity window, reviewed by the independent auditor before execution; the committed capture is verified by the custody verifier at the exact commit and on the fetched remote. This is the simplified form of operator gate ① (acquisition authorization); the gate remains the operator's. The parked schema-acquisition launcher package (F7) and bc-core PR #746 are unchanged by this decision; their disposition remains decision D7.
