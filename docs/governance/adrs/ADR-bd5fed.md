---
uid: DEC-bd5fed
title: "Orphaned routes — remove from router"
description: "Dead routes with no backing implementation must be removed from the router, not left as stubs."
status: implemented
subdomain: bc-admin-cleanup
focus: dead-route-removal
date: 2026-02-24
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Orphaned routes — remove from router

## Context

Dead code with no user path to reach them. Can be re-added when navigation entries are created. Reduces router bloat and maintenance surface.

## Decision

Remove the 10 orphaned routes (4 data-contracts-*, 4 reader-*, 1 kpi-store/risk-compliance, 1 customer-portal-map) from AppRouter.tsx since they have no navigation entry.

## Options Considered

N/A

## Consequences

N/A
