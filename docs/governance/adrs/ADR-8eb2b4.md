---
uid: DEC-8eb2b4
title: "Execution schema carved from operations for boundary aggregation"
description: "New execution schema for boundary rollups, health, chain status, run/rejection summaries. Operations retains discovery and admin work."
status: implemented
subdomain: schema-organization
focus: ddl
date: 2026-03-26
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Execution schema carved from operations for boundary aggregation

## Context

Operations schema was mixing two concerns: platform admin activities (discovery scans, verification logs) and aggregated tenant execution data (rollups, chain status). These have different audiences (admin vs execution monitoring), different update patterns (manual vs automatic), and different data sources (platform actions vs tenant boundary processing).

## Decision

New `execution` schema in platform DB for aggregated tenant boundary data: boundary_rollup, boundary_health, chain_status, run_summary, rejection_summary. `operations` schema retains platform admin work: discovery, verification, enrichment, activity log. Semantic split: runtime=driving the car, operations=garage/maintenance, execution=dashboard telemetry from driving.

## Options Considered

N/A

## Consequences

N/A
