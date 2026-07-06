---
uid: DEC-b5bedb
title: "Execution run tables for all 4 evaluation boundaries"
description: "Each evaluation boundary (admission, canonical, metric, action) gets its own run tracking table in operations schema."
status: implemented
subdomain: evidence-model
focus: 4-boundary-run-tables
date: 2026-03-20
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Execution run tables for all 4 evaluation boundaries

## Context

Previously only admission_run existed. The execution model has 4 evaluation boundaries, each producing batch execution records. canonical_run, metric_run, and action_run fill the gap. Short names chosen over longer alternatives (canonical_evaluation_run) for consistency. Quarantine table rejected after reviewing bc-docs foundation spec: rejection occurs only at admission, evidence tables already capture rejection details, and S3 handles payload preservation for reprocessing.

## Decision

4 batch execution tables in tenant DB: admission_run (existing, moved), canonical_run (new), metric_run (new), action_run (new). Naming pattern: {boundary_output}_run. All share the same status CHECK (pending/running/completed/failed/cancelled), timing columns (started_at, finished_at, duration_ms), and error tracking (error_count, error_ref, trace_id). Each has boundary-specific counters (e.g. records_observed/admitted/rejected for admission, metrics_evaluated/computed/failed for metric). No quarantine table needed — rejection happens only at admission boundary, rejection evidence goes to evidence_object table, quarantined payloads go to S3.

## Options Considered

N/A

## Consequences

N/A
