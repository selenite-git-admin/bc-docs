---
uid: DEC-3196eb
title: "Drop operational schema — discovery to operations, connections tenant-only"
description: "Eliminated operational schema. Discovery tables moved to operations; connection tables become tenant-only"
status: superseded
date: 2026-03-25
project: bc-core
domain: database
authority: retired
migrated_from: legacy v2 archive
---


# Drop operational schema — discovery to operations, connections tenant-only

## Context

Superseded by D168. D163 over-reached — connections are infrastructure/config, not execution data. Moving them to tenant DB broke FK integrity with connectors (D162 Rule 3), required fan-out queries for admin visibility, and created circular dependency in reader runtime. Connections return to platform DB runtime schema with tenant_id for ownership. Discovery tables moving to operations remains valid (not reversed).

## Decision

Eliminated bc_platform.operational schema. Discovery tables (scan, object, field, diff) moved to operations schema as platform metadata. Connection tables (connection, config, check) and admission_run dropped from platform — tenant-only. Rationale: operational was a staging area for tables that belonged elsewhere. Discovery feeds contract design (platform workflow), connections are tenant-scoped resources.

## Options Considered

N/A

## Consequences

N/A
