---
uid: DEC-7eec2e
title: "Chain-based navigation for bc-admin v1.0.0"
description: "bc-admin nav restructured to 9 chain-aligned topbar items: Source Chain, Canonical Chain, Metric Chain, Runtime, Operations, etc."
status: implemented
subdomain: ui-architecture
focus: chain-nav
date: 2026-03-23
project: bc-admin
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Chain-based navigation for bc-admin v1.0.0

## Context

Flat sections (Sources, Model, Metrics, Contracts) didn't form a logical flow. Chain-based nav maps directly to BareCount's execution model — each chain owns its catalog + bindings + contracts together. A platform admin working on source onboarding sees everything in Source Chain; someone defining canonical objects sees everything in Canonical Chain. No more artificial separation of contracts into a standalone section.

## Decision

bc-admin navigation restructured from flat sections to chain-aligned sections. 9 topbar items: Source Chain (catalog + source/admission/observation contracts), Canonical Chain (fields + objects + bindings + canonical contracts), Metric Chain (catalog + bindings + metric/intervention contracts), Runtime, Operations, Tickets, Tenants, Platform, Pricing. AI contracts dropped from v1. Discovery Scans moved to Operations. Intervention contracts under Metric Chain (noted: tenant-scoped, not platform contracts). Stub pages remain as "Coming Soon".

## Options Considered

N/A

## Consequences

N/A
