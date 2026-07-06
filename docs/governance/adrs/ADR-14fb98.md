---
uid: DEC-14fb98
title: "bc-ai uses own SQLite database, not shared with DevHub"
description: "bc-ai owns its SQLite DB independently; revisit if batch volume outgrows single-writer"
status: superseded
superseded_by: DEC-ffee4e
subdomain: ai-storage
focus: separate-sqlite
date: 2026-03-31
project: bc-ai
domain: execution
authority: authoritative
migrated_from: legacy v2 archive
---


# bc-ai uses own SQLite database, not shared with DevHub

## Context

bc-ai is a separate Python/FastAPI service (port 4300) with different data lifecycle — high-volume, append-heavy, ephemeral AI evidence vs DevHub's low-volume governance state. Sharing a DB would create cross-service coupling. SQLite is sufficient at current scale (single-writer, single process). Real relational data lives in bc-core PostgreSQL; bc-ai writes back via API.

## Decision

bc-ai maintains its own SQLite database (data/bc-ai.db) with 7 tables: model_registry, flow_config, evidence, draft_evidence, budget_log, review_queue, pinned_decisions. This is separate from DevHub's SQLite (data/devhub.db). bc-ai writes results back to bc-core PostgreSQL via API, not direct DB access. If AI batch volume grows significantly (thousands of concurrent enrichment runs), revisit whether SQLite single-writer lock becomes a bottleneck — potential migration to PostgreSQL or async write queue.

## Options Considered

N/A

## Consequences

N/A
