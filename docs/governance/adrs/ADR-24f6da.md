---
uid: DEC-24f6da
title: "Temporal values are absolute — cron + timezone + ISO 8601 durations"
description: "All contract temporal specs use cron+IANA timezone for schedules and ISO 8601 for durations. No relative labels like daily or hourly."
status: implemented
subdomain: contracts-architecture
focus: temporal-spec
date: 2026-03-01
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Temporal values are absolute — cron + timezone + ISO 8601 durations

## Context

Relative labels like 'daily' or 'hourly' are not actionable — they don't specify when, from what timezone, or how long to wait. A cron expression ('0 16 * * 1-5') with timezone ('Europe/Frankfurt') is unambiguous and machine-executable. ISO 8601 durations ('PT4H', 'P1D') are standardized and parseable. This eliminates ambiguity at the contract definition level.

## Decision

All temporal specifications in contract bodies use absolute, machine-executable values: (1) Schedule uses cron expression (5-field) + IANA timezone, not relative labels like 'daily' or 'hourly'. (2) Durations use ISO 8601 format (e.g., PT4H, P1D, P30D). (3) A shared temporal_gate $def is used across canonical-v1 (Tier 2), metric-v1, and ai-v1 meta-schemas. (4) Intervention contracts do not use temporal_gate — they are user-triggered with their own clock model. The temporal_gate contains: schedule (cron + timezone), readiness_gate (strategy: wait_for_all/wait_for_quorum/best_effort, dependencies, quorum_min, timeout), and lookback_window (ISO 8601 duration).

## Options Considered

N/A

## Consequences

N/A
