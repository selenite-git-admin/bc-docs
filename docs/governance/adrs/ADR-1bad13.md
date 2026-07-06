---
uid: DEC-1bad13
title: "Execution schema — carve out from operations"
description: "Split operations schema into operations (admin maintenance) and execution (aggregated tenant boundary telemetry). 5 tables moved. 12 schemas total."
status: implemented
subdomain: platform-schema-organization
focus: schema-split
date: 2026-03-26
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Execution schema — carve out from operations

## Context

Operations schema was a grab-bag mixing admin maintenance work (discovery, verification, enrichment logs) with aggregated tenant execution data (rollups, health, chain status). These are semantically distinct: operations is what admins DO to the platform, execution is what HAPPENED when tenants ran through boundaries. Clean separation enables bc-admin to build distinct Operations (admin tools) and Execution (boundary monitoring) page groups.

## Decision

Split platform DB operations schema into two: operations (admin/maintenance work) and execution (aggregated tenant boundary execution telemetry). 5 tables moved: boundary_rollup, boundary_health, chain_status, run_summary, rejection_summary. Operations retains: activity_log, discovery_*, catalog_verification_log, bo_enrichment_log, bo_verification_log. Semantic: operations = garage (maintaining the platform), execution = dashboard telemetry (what happened when tenants ran through boundaries). Platform DB now has 12 schemas.

## Options Considered

N/A

## Consequences

N/A
