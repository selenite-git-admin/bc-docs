---
uid: DEC-b28b13
title: "Connector lifecycle: status enum replaces available boolean"
description: "Connectors use a status enum (draft, active, deprecated, archived) instead of a simple available boolean flag."
status: implemented
subdomain: connectors
focus: connector-status-enum
date: 2026-03-14
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Connector lifecycle: status enum replaces available boolean

## Context

Boolean `available` is too coarse — doesn't distinguish "not ready yet" from "being phased out" from "fully dead". Lifecycle enum avoids tech debt of bolting on deprecation/retirement logic later.

## Decision

Connector `available` boolean replaced by `status` enum: `draft` → `available` → `deprecated` → `retired`.

- **draft**: registered but not ready for tenant use (default on creation)
- **available**: tenants can create connections against this connector
- **deprecated**: still works but tenants should migrate; no new connections
- **retired**: fully decommissioned, all connections disabled

Platform admin controls lifecycle transitions via ConnectorDetailPage. Status badge visible on connector cards.

Migration: `available=true` → `status='available'`, `available=false` → `status='draft'`. Drop `available` column after migration.

## Options Considered

N/A

## Consequences

N/A
