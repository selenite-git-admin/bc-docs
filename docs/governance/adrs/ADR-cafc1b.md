---
uid: DEC-cafc1b
title: "UinBAT Reader operational shape — schedule, retries, backfill, failure policy"
description: "Reader carries operational config (schedule, retry, backfill, failure) in a single JSONB column. Schedule is on the reader; extraction config is on the flavor."
status: implemented
subdomain: readers
focus: operational-config-shape
date: 2026-03-02
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# UinBAT Reader operational shape — schedule, retries, backfill, failure policy

## Context

Reader identity is business-object-centric (domain-specific, source-system-agnostic). The business cadence (when to observe) is the reader's concern. How to extract from a specific source is the flavor's concern. Operational policies (retry, failure, backfill) are reader-level because they apply uniformly across all source flavors. A single JSONB column keeps the schema stable while the operational shape evolves.

## Decision

Reader carries operational config (schedule, retryPolicy, backfill, failurePolicy) in a single operationalConfig JSONB column. Schedule is on the reader (business cadence), not the flavor. Flavors carry source-specific extraction config + optional sourceWindow timing constraints. Watermark state is per-flavor. Circuit breaker is per-flavor. Rejections are per-record with evidence. Backfill supports incremental, full-snapshot, and explicit range strategies. Documented in Component Ref 091.

## Options Considered

N/A

## Consequences

N/A
