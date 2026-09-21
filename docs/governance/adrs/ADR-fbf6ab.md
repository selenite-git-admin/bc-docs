---
uid: DEC-fbf6ab
title: "Platform DB Foundation program CLOSED — foundation objectives met"
description: "Platform DB Foundation program CLOSED — foundation objectives met"
status: decided
date: 2026-09-21T04:03:55.354Z
project: bc-core
domain: db-foundation
subdomain: platform-db/program-lifecycle
focus: governance
---

# Platform DB Foundation program CLOSED — foundation objectives met

## Context

Verified live end-state 2026-09-21 (baseline adopted, ledger seq 27, PG 17.11, post-drain program check = 0, parity 8bb2b0b7; zero standing bcp-* cloud stacks) and independent auditor acceptance across the waves. Closure recorded in the authoritative overview (bc-docs docs/overview/platform-db-foundation.md, PR #47) and TSK-cc348a marked completed.

## Decision

The Platform DB Foundation program (TSK-cc348a / DEC-c40e7a) is closed. Its foundation objectives are met: the platform database is a governed product on a live, adopted, forward-only spine (bc-db) — ratified engine-portable baseline, append-only review-bound change ledger (bc_platform_dev at seq 27, PostgreSQL 17.11, cluster 7619260324391063586), proven migration/backup/restore/adoption machinery, and the historical wrong turns retired (W5: legacy contract.metric_contract* world drained — 15 tables incl. tenant.tenant_override, ledger 19-27; docker/redesign monolith retired; unified authoring ratified). W1 auditor-accepted; W3 closed at the governed vocabulary; W2 disposed closed-at-substance; cloud units u1-u6 done with the RDS-portable baseline proven (NFR-4, parity c309ea3d) at zero standing cost. Not in program scope, deferred as a separate future operator decision (not unfinished foundation work): cloud standing go-live (W1.6/W4), productization gates D5/D9/D10/D11 (D11 legal-gated), and Gate-④ production cutover. Closing the program strands nothing; a future go-live reopens a distinct, separately-scoped phase.
