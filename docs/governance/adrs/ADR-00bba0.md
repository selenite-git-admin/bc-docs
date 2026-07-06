---
uid: DEC-00bba0
title: "Discovery scan counts are frozen snapshots, not denormalized counters"
description: "Scan count columns on discovery_scan are append-once-then-freeze metadata, exempt from D089 rule 2 counter prohibition."
status: implemented
subdomain: deferred-normalization
focus: frozen-snapshot-counter-exemption
date: 2026-03-17
project: platform
domain: database
refs:
  - type: decision
    label: "D089"
authority: authoritative
migrated_from: legacy v2 archive
---


# Discovery scan counts are frozen snapshots, not denormalized counters

## Context

D089 rule 2 prohibits live counters derivable from child rows because they create update anomalies. Frozen snapshots don't have this problem — the child data never changes after the scan is sealed. Removing these counts would force a JOIN + COUNT on every scan listing query with no correctness benefit.

## Decision

The 6 count columns on discovery_scan (objectCount, fieldCount, matchedCount, suggestedCount, unmatchedCount) and discovered_object (fieldCount) are classified as frozen snapshots, not D089 rule 2 violations. Discovery scans are append-once-then-freeze: once a scan completes, its child rows (discovered_object, discovered_field) are never added, removed, or modified. The counts are computed at scan completion time and preserved as immutable scan metadata.

## Options Considered

N/A

## Consequences

N/A
