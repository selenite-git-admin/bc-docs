---
uid: DEC-cf2cbc
title: "Foundation naming compliance + schema integrity for boundary tables"
description: "Rename boundary tables to Foundation vocab (canonical_evaluation, intervention), drop redundant tenant_id, add metric_evaluation_input junction table."
status: superseded
superseded_by: DEC-f02230
subdomain: naming-convention
focus: ddl
date: 2026-03-17
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Foundation naming compliance + schema integrity for boundary tables

## Context

Foundation Specification vocabulary is LOCKED. Current table names (evaluation, action_object, action_evaluation) violate the spec which requires canonical_evaluation, intervention, intervention_evaluation. tenant_id is redundant in per-tenant isolated schemas — it wastes storage and creates a data consistency risk (schema says tenant A but tenant_id says B). Metric evaluation's JSON-only CO references break the FK chain visible in DBeaver ERD and lose referential integrity. Evidence with text-only subject references can't enforce that the referenced object exists.

## Decision

1. RENAME tables to match Foundation Specification vocabulary (LOCKED):
   - boundary.evaluation → boundary.canonical_evaluation
   - boundary.action_object → boundary.intervention
   - boundary.action_evaluation → boundary.intervention_evaluation
   All column names, FKs, indexes renamed accordingly (evaluation_id → canonical_evaluation_id, action_object_id → intervention_id, etc.)

2. DROP tenant_id from all 12 boundary+evidence tables. When data lives in per-tenant schema (t_{slug}), tenant_id is redundant. Schema isolation IS the tenant boundary.

3. ADD metric_evaluation_input junction table with proper FKs to metric_evaluation and canonical_object. Replaces the inputReferencesJson JSONB column for CO references, making the SO→CO→MetricEvaluation chain visible in ERD and enforceable via FK constraints.

4. ADD subjectId UUID FK on evidence_object pointing to the boundary object it proves. Evidence currently uses text subjectRef with no referential integrity — boundary objects should have a traceable FK relationship to their evidence.

## Options Considered

N/A

## Consequences

N/A
