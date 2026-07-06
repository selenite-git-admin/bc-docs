---
uid: DEC-0b3c08
title: "D053: Master/Tenant-Override contract pattern — platform defines, tenant tunes"
description: "Two-layer contract model: platform master definition + tenant override for thresholds, schedules, SLA. Formulas and schemas are platform-locked."
status: implemented
subdomain: contract-scoping
focus: master-override-pattern
date: 2026-03-09
project: bc-admin
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# D053: Master/Tenant-Override contract pattern — platform defines, tenant tunes

## Context

bc-portal UI already implements tenant override screens (KPISettingsTab, ReaderSetupPage, GDPContractDetail) but the architecture docs had not formalized the pattern. D044 and D045 established tenant-scoped mapping bindings and admission contracts, but did not cover the broader override pattern for thresholds, schedules, and SLA. This decision formalizes what the UI already requires and establishes the authorization boundary for self-service vs platform-governed fields.

## Decision

Contracts follow a two-layer model: platform-scoped master definition + tenant-scoped override layer.

**Master Contract (Registry, bc-admin):** The authoritative definition — formula, schema, rules, computation logic, default thresholds, default schedule. Authored and governed by platform team.

**Tenant Override (Tenant management, bc-portal):** Selective customization of designated fields. Tenant (client admin) can self-serve changes within platform-defined guardrails.

**Tenant-overridable fields (confirmed from bc-portal UI):**
- Metric thresholds — Excellent/Good/Warning/Critical levels, min/max values (KPISettingsTab)
- Alert configuration — alert level per threshold, recipients, dynamic rules (KPISettingsTab)
- Metric direction — Higher is Better / Lower is Better / Target Range (KPISettingsTab)
- Reader schedule — observation frequency as cron expression (ReaderSetupPage)
- Reader operational params — lookback days, batch size (ReaderSetupPage)
- Contract SLA — freshness, quality rule adjustments (GDPContractDetail tenant scope)
- Tenant-specific quality rules — stricter or relaxed validation (GDPContractDetail)

**Not tenant-overridable (platform-locked):**
- Formulas and computation logic
- Canonical resolved_schema (CO shape)
- Business key fields
- Semantic rules
- Source dependencies and join context
- Mapping binding structure (authored by platform team, not tenant)

**Authorization boundary update:** Client admin CAN modify designated override fields. Client admin CANNOT modify contract definitions, mapping bindings, canonical wiring, or formula logic. Platform team can override tenant overrides if needed (governance hierarchy).

**Evidence impact:** Evaluation evidence must capture both master contract version AND tenant override state at time of evaluation.

**UI pattern:** bc-portal GDPContractDetail already implements Provider Scope (read-only baseline) vs Tenant Scope (customizable) side-by-side view.

**Cascading concerns (to be addressed separately):**
- Override validation bounds (min/max guardrails per field)
- Override versioning and audit trail
- Evidence chain capture of override state
- Evaluation engine resolution layer (master + tenant merge)
- Platform lockdown capability (override the override)

## Options Considered

N/A

## Consequences

N/A
