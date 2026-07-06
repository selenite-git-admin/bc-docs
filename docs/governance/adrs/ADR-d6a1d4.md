---
uid: DEC-d6a1d4
title: "Contract Generation Service — programmatic, not hand-built JSON"
description: "Drop 57 hand-built JSON contracts. Build a service that programmatically generates the full contract chain from catalog state when objects reach approved."
status: implemented
subdomain: contract-generation
focus: programmatic-build
date: 2026-03-20
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Contract Generation Service — programmatic, not hand-built JSON

## Context

1. 57 hand-built JSON contracts are stale and only cover 6 domains (AR/AP/GL/SD/FI/EXR). 2. Contract schema evolved (observation_field_map, canonical_mapping are new in v2) — old JSONs don't match. 3. With 2,428 KPIs and 63 providers, hand-building contracts doesn't scale. 4. Programmatic generation ensures contracts always match the catalog state. 5. Enables e2e testing across the full contracted profile.

## Decision

Drop all 57 hand-built contract JSON files. Build a Contract Generation Service that programmatically creates the full contract chain (source → admission → observation → canonical → metric) when a source object reaches approved status. Contracts become derived artifacts from the catalog (source objects + standard fields + metric definitions), not manually maintained JSON. This completes the e2e profile so that e2e tests can run against a fully contracted system. The service runs as part of seed:v2 after catalog data is loaded.

## Options Considered

N/A

## Consequences

N/A
