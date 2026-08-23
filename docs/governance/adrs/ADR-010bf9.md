---
uid: DEC-010bf9
title: "Connection simulation — bc-sdg serves as mock SAP system for end-to-end demo"
description: "bc-sdg runs as a mock SAP landscape for full-stack demo: connection, reader, admission, canonical, metric, action — no hand-waving."
status: implemented
subdomain: e2e-demo
focus: mock-sap-runtime
date: 2026-03-02
project: bc-admin
domain: readers
authority: authoritative
migrated_from: legacy v2 archive
---


# Connection simulation — bc-sdg serves as mock SAP system for end-to-end demo

## Context

Difference between 'here is pre-loaded data' and 'watch BareCount connect to SAP and start working.' Proves the full stack: connection → reader → admission → canonical → metric → action. No hand-waving in the demo.

## Decision

bc-sdg runs as a mock SAP landscape that BareCount connects to as if it were a real SAP system. Supports: connection health checks, paginated extraction, delta extraction (watermark-based), daily batch generation via internal scheduler. Demo flow: start bc-sdg → pick profile → generate 18-month backfill → register connection in bc-admin → BareCount readers connect, extract, admit, evaluate → dashboard shows KPIs. Scheduler generates tomorrow's data → readers pick it up → KPIs update automatically.

## Options Considered

N/A

## Consequences

N/A
