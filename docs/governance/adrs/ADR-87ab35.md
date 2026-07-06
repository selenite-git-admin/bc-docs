---
uid: DEC-87ab35
title: "18-month backfill covering 2 full fiscal years (April 2024 — September 2025)"
description: "Synthetic data covers Apr 2024 to Sep 2025 (complete FY24-25 + H1 FY25-26). Enables YoY comparison, period-end, and aging history."
status: decided
subdomain: synthetic-data-window
focus: backfill-horizon
date: 2026-03-02
project: bc-sdg
domain: sdg
authority: authoritative
migrated_from: legacy v2 archive
---


# 18-month backfill covering 2 full fiscal years (April 2024 — September 2025)

## Context

2 fiscal years gives YoY comparison on every KPI. Complete close cycles prove month-end/year-end handling. 18 months is the minimum for meaningful trend analysis without excessive generation time.

## Decision

bc-sdg generates 18 months of historical data: April 2024 through September 2025. This covers complete FY24-25 (April 2024 — March 2025) + H1 FY25-26 (April — September 2025). Indian fiscal year (April-March). Enables year-over-year comparison, complete period-end and year-end close cycles, seasonal pattern visibility, meaningful AR/AP aging history. Daily generation continues from the last generated date forward.

## Options Considered

N/A

## Consequences

N/A
