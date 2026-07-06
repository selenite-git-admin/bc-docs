---
uid: DEC-c2f499
title: "Control Plane / Data Plane Architecture Split"
description: "Separate control plane (config/metadata) from data plane (tenant execution). Four deployment tiers from shared cloud to on-prem appliance."
status: superseded
date: 2026-03-03
project: bc-infra
domain: database
refs:
  - type: decision
    label: "D028"
  - type: decision
    label: "D029"
authority: retired
migrated_from: legacy v2 archive
---


# Control Plane / Data Plane Architecture Split

## Context

Superseded by the D073/D081/D087 implementation chain. All phases of CP/DP split are complete.

## Decision

BareCount adopts a Control Plane / Data Plane architecture. Control Plane (BareCount-hosted) holds configuration metadata: contract registry, metric catalog, action rules, reader definitions, source catalog, tenant registry, operational telemetry, and ticket system. Data Plane (tenant-located) holds execution and business data: UinBAT Reader engine, evaluation engines (canonical, metric, action), tenant DB (boundary + evidence schemas), and data source connections. Tenant business data never leaves their environment. Data Plane pulls configuration from Control Plane and pushes only operational telemetry back. Three deployment tiers: (1) BareCount Cloud — default shared hosting, BareCount manages everything. (2) Tenant Cloud — Data Plane deployed in tenant's own cloud account (AWS/Azure/GCP VPC), tenant manages infrastructure. (3) On-Premises Appliance (premium) — BC-Agent installed on tenant-purchased hardware per BareCount specifications, with remote access for management and updates. D028 (separate tenant DB) and D029 (dual-write) are prerequisite steps. Implementation phases: Phase 1 — separate tenant DBs (BareCount-hosted). Phase 2 — configurable DB location. Phase 3 — packaged Data Plane agent for tenant cloud deployment. Phase 4 — on-premises appliance program.

## Options Considered

N/A

## Consequences

N/A
