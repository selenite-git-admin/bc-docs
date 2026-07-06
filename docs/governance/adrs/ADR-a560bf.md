---
uid: DEC-a560bf
title: "Platform DB never queries tenant DB — orchestrator pushes summaries"
description: "Strict one-way data flow: platform never reads tenant DB directly. An orchestrator pushes tenant summaries up."
status: implemented
subdomain: tenant-topology
focus: runtime
date: 2026-03-26
project: bc-admin
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Platform DB never queries tenant DB — orchestrator pushes summaries

## Context

Strict boundary between platform and tenant databases. Platform visibility into tenant execution is achieved by write-back during processing, not by read-time cross-DB queries. This maintains tenant isolation, simplifies bc-admin, and avoids multi-tenant fan-out complexity.

## Decision

Platform API endpoints (used by bc-admin) read only from platform DB. The orchestrator pushes aggregated summaries from tenant execution context to platform `execution.*` tables during boundary processing. No cross-DB queries, no fan-out reads.

## Options Considered

N/A

## Consequences

N/A
