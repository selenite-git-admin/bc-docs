---
uid: DEC-75fc71
title: "Platform DB Foundation Program — mandate (execute ADR-b1a286's waves and extend the discipline to tenant databases, object stores, durability, credentials and capacity)"
description: "D1: mandate for the Platform DB Foundation Program (TSK-cc348a) — execute ADR-b1a286 waves + tenant/object-store/durability/credentials/capacity discipline per the accepted requirements doc; TSK-3f52d7 subsumed into W5"
status: decided
date: 2026-09-09T09:33:25.437Z
project: bc-db
domain: database
subdomain: database/foundation
focus: program-mandate
---

# Platform DB Foundation Program — mandate (execute ADR-b1a286's waves and extend the discipline to tenant databases, object stores, durability, credentials and capacity)

## Context

Ratified by the operator on 2026-09-09 ("ratify D1 D6 D8"). The accepted study (bc-core PR #747, main 3e7a69d7) established that the platform database has a decided foundation (ADR-b1a286) that is incomplete and now load-bearing: no reproducible fresh build (two bootstrap defects), a stale golden dump that is not a source, nine ledger records against 140 forward migration files, curated content with no versioned source, no recovery mechanism found, object stores decided but not built, tenant databases without a source-of-truth decision or upgrade engine, cloud deployment undefined in code, and no capacity model. A task record (TSK-cc348a) is not a decision; this record gives the program its mandate and binds it to the accepted requirements document. The mandate authorizes planning and gated execution; it ratifies no recovery objective (D10), no baseline and no wave design — each of those is its own record.

## Decision

The Platform DB Foundation Program (DevHub TSK-cc348a) is mandated to execute the unexecuted waves of ADR-b1a286 and to extend the same source-of-truth, evidence and change discipline to the tenant databases, the object stores (held, rejected and archived inputs), transactional durability, credentials and capacity, as specified in docs/design/platform-db-foundation-requirements.md (bc-core; v0.4 accepted with boundary by the independent auditor and merged at main 2b8ff207 on 2026-09-09, with successors reviewed and merged under the operator's standing authority). Scope is the matrix: Platform DB with one hosting option; Tenant DB across BareCount-hosted and BYO-DB; BC-Agent deferred (DEC for D6); five data classes per cell (schema, master data, curated content, transactional data, held/rejected/archived inputs). Waves W0–W5 as defined there (W0 records; W1 migration baseline and runner in units W1.1–W1.6; W2 tenant source of truth, upgrade path, fleet and credentials; W3 curated-content promotion; W4 durability, object stores and capacity; W5 cleanup). Every wave is delivered as independently reviewable units, each accepted by the independent auditor at an exact commit and, where it touches a database, applied only under the Database Change Protocol. The four operator-only live gates (acquisition authorization, DDL apply, scope/golden ratification, Phase-4 promotion) remain. The earlier de-drift task TSK-3f52d7 is subsumed into W5. Decision D3 (machinery home = bc-db, DEC-826390) stands.
