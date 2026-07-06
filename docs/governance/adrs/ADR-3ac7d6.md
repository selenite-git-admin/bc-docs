---
uid: DEC-3ac7d6
title: "Reader backfill configuration at flavor level"
description: "Backfill config (chunk size, rate limiting, dedup, resume) lives on reader_flavor, not reader. Each flavor has different needs"
status: decided
subdomain: reader-config
focus: backfill-granularity
date: 2026-02-28
project: platform
domain: readers
authority: authoritative
migrated_from: legacy v2 archive
---


# Reader backfill configuration at flavor level

## Context

ECB allows ~10 req/min with 30-day chunks, OER has API key rate limits, FRED has different pagination. Reader-level config would be too coarse — flavor-specific config lets each source adapter optimize independently.

## Decision

Backfill configuration (chunk size, rate limiting, dedup strategy, resume capability) lives at the flavor level, not reader level. Each flavor (ECB SDMX, OER, FRED) has different rate limits and chunking needs.

## Options Considered

N/A

## Consequences

N/A
