---
uid: DEC-bf5e61
title: "Reader Configuration Presets — fixed option lists, foundation-aligned"
description: "Reader config uses fixed preset lists (output formats, scheduling, error handling) aligned with foundation spec. No freeform."
status: implemented
subdomain: reader-architecture
focus: configuration-presets
date: 2026-03-24
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Reader Configuration Presets — fixed option lists, foundation-aligned

## Context

Foundation spec mandates exactly-one object per boundary crossing. Batch thinking (partial admission, failure tolerance %) is a pipeline concept that violates the architecture. Fixed preset lists prevent tenant misconfiguration while preserving flexibility. Quarantine resolution is platform team responsibility — tenants see operational dashboard only.

Reader operational config uses fixed preset lists — tenants pick from a menu, never free-form values. Foundation mandates one-object-at-a-time boundary crossing (no batches, no partial admission). Quarantine is always 100% — platform team resolves, not tenant.

## Config Presets (fixed enums)

| Config | Options |
|---|---|
| Execution Mode | `incremental` · `full-snapshot` · `cdc-stream` |
| Backfill Mode | `incremental-catchup` · `full-historical` · `none` |
| Schedule Preset | `realtime` · `hourly` · `daily-business` · `daily-offpeak` · `weekly` · `monthly` |
| Retry Strategy | `conservative` (3 retries, exponential) · `aggressive` (5 retries, linear) · `none` |
| Circuit Breaker | `sensitive` (3 failures/30min) · `standard` (5/60min) · `relaxed` (10/120min) |
| Alert Preset | `immediate` (any quarantine) · `standard` (>10% quarantine) · `digest` (daily summary) |

## Removed (foundation violation)
- ~~Partial Admission~~ — no batches exist; each object crosses boundary independently
- ~~Run Atomicity~~ — same reason
- ~~Batch Size~~ — executor implementation detail, not a boundary concept
- ~~Failure Tolerance~~ — quarantine is 100%, platform team resolves

## Defaults by BO Type
- Transactional: incremental, incremental-catchup, daily-business, conservative, standard, standard
- Master Data: full-snapshot, full-historical, weekly, conservative, standard, standard
- Reference: incremental, incremental-catchup, daily-offpeak, conservative, standard, standard
- Derived: full-snapshot, none, monthly, conservative, relaxed, digest

## Override Model
Platform sets defaults at reader creation (derived from BO type). Tenant may override any preset but ONLY from the fixed list. No free-form cron, no custom retry counts.

## Consequences

N/A
