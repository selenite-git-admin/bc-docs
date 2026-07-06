---
uid: DEC-06cb2c
title: "Two sectors in bc-portal: CXO Portal + Control Plane (gated)"
description: "bc-portal splits into CXO Portal (metrics/dashboards for business users) and Control Plane (readers/connections for data teams), role-gated."
status: decided
subdomain: bc-portal-ia
focus: sector-split
date: 2026-03-03
project: bc-admin
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Two sectors in bc-portal: CXO Portal + Control Plane (gated)

## Context

A CFO opening BareCount should see metrics and actions — not UinBAT readers, admission contracts, and connection health. The plumbing was mixed into the main UI because it was designed before the architecture was locked. Separating into two sectors within one app keeps deployment simple (no new app) while giving CXOs a clean experience and data teams the operational control they need.

## Decision

bc-portal has two sectors within the same app, role-gated:

1. **Portal** (default) — CXO-facing. Metrics, dashboards, insights, actions. Clean, business-language, no plumbing visible.
2. **Control Plane** (gated, data team only) — Reader configuration, connection management, admission contracts, operational monitoring. Technical, operational.

All current "Data Sources", "Readers", "Connector Catalog", "Sync Health", "Contract Alerts" move into the Control Plane sector. The main portal navigation stays clean for business users. bc-admin remains the BareCount platform admin (tenant management, billing, infra) — separate from the customer's Control Plane.

## Options Considered

N/A

## Consequences

N/A
