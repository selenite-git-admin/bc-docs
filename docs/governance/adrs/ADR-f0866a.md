---
uid: DEC-f0866a
title: "Connector Ecosystem — transport abstraction, dynamic registry, test harness, scaffold CLI"
description: "4-layer connector architecture: ReaderExecutor interface, config-driven registry, transport helpers (HTTP/OData/SDMX), and scaffold CLI with 7-category test harness."
status: implemented
subdomain: connectors
focus: connector-ecosystem
date: 2026-03-05
project: platform
domain: database
refs:
  - type: decision
    label: "D038"
authority: authoritative
migrated_from: legacy v2 archive
---


# Connector Ecosystem — transport abstraction, dynamic registry, test harness, scaffold CLI

## Context

With 6 executors, hardcoded wiring and duplicated HTTP logic are manageable. At 50+ connectors (D039 Standard tier), they become blockers. Transport abstraction ensures library swaps (CVE, license change, abandonment) are 1-file changes. Dynamic registry means adding/removing connectors requires no shared module changes. Test harness provides automated quality gates for auto-generated and community connectors.

## Decision

BareCount adopts a 4-layer connector ecosystem: Layer 1 ReaderExecutor interface (D038 unchanged), Layer 2 ExecutorRegistryService (config-driven, replaces hardcoded BoundaryModule), Layer 3 Transport Helpers (HttpTransport, ODataTransport, SdmxTransport — pagination/retry/auth extraction), Layer 4 Executor (domain logic only). Test harness with 7-category validation suite enforces quality gate for all connectors. Scaffold CLI generates boilerplate. Migration is additive — existing executors continue working.

## Options Considered

N/A

## Consequences

N/A
