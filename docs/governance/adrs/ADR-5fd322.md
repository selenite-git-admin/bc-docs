---
uid: DEC-5fd322
title: "Observation Contract is the central design-time artifact, readers are runtime executors"
description: "OCs are created before readers and declare field mappings + canonical targets. Readers bind to existing OCs, they don't create them."
status: implemented
subdomain: contract-authoring
focus: oc-first-flow
date: 2026-03-24
project: platform
domain: contracts
refs:
  - type: decision
    label: "D200"
authority: authoritative
migrated_from: legacy v2 archive
---


# Observation Contract is the central design-time artifact, readers are runtime executors

## Context

The D200 wizard created a circular dependency: reader creates its own observation contract then consumes it. This breaks the contract-first philosophy where contracts are the authority and executors bind to them. Every other contract type (source, admission, canonical, metric) exists independently of its executor. Observation contracts should follow the same pattern.

## Decision

Observation contracts are independent registry artifacts created BEFORE readers. They declare: which source system, which fields to observe, how those fields map to business fields, and which canonical contract they feed. Readers bind to existing observation contracts — they do not create them. The D200 wizard is refactored into two flows: (1) Create Observation Contract (steps 1-3: pick BO, pick source, map fields → produces observation contract + field map + canonical mapping + lineage), (2) Create Reader (pick existing observation contract → create reader + flavor bound to it).

## Options Considered

N/A

## Consequences

N/A
