---
uid: DEC-057c1f
title: "Mapping is embedded in contract constructors — no standalone mapping entity"
description: "Field mapping is always a step inside the contract constructor wizard. No standalone mapping page, entity, or CRUD exists."
status: implemented
subdomain: contract-authoring
focus: mapping-pattern
date: 2026-03-25
project: bc-core
domain: database
refs:
  - type: decision
    label: "D208"
  - type: decision
    label: "D203"
authority: authoritative
migrated_from: legacy v2 archive
---


# Mapping is embedded in contract constructors — no standalone mapping entity

## Context

Mapping is the substance of the contract, not a standalone artifact. The OC wizard already proves this pattern — field mapping is Step 3 of contract creation, not a separate workflow. Nobody creates mappings before envisioning the contract that gives them context. Each contract constructor embeds its own mapping step.

## Problem

The task backlog included a standalone "MappingsPage" (TSK-05e8db) for managing mapping templates. But mapping doesn't exist as an independent artifact — it's the substance of the contract itself. You can't map Source→Canonical fields before the Canonical Contract is envisioned. The mapping depends on knowing BOTH sides, and the contract constructor is the only place where both sides are known.

## Proof: OC wizard already does this

The OC creation wizard (D208, completed) embeds field mapping as Step 3:
- Step 1: Pick business object (defines the canonical target)
- Step 2: Pick source system (defines the source)
- Step 3: Map source fields → canonical fields (this IS the mapping)
- Step 4: Review

The mapping only makes sense after Steps 1 and 2 establish context. Nobody creates mappings first and contracts later.

## Decision

**Mapping is always a step inside the contract constructor. There is no standalone mapping page, no standalone mapping entity, no mapping CRUD outside of contract creation.**

Each contract constructor embeds its relevant mapping:

| Constructor | What it maps | Why it can't be standalone |
|-------------|-------------|---------------------------|
| OC wizard | Source fields → Canonical fields | Need to know source system AND business object first |
| CC wizard | Canonical fields → Metric inputs + evaluation rules | Need to know which canonical entity and what metrics exist |
| MC wizard | Metric formula → CO inputs + dimensions + thresholds | Need to know the metric definition and available CO fields |

The chain of constructors IS the chain of mappings:
- OC: "what to observe, how source maps to canonical"
- CC: "how to evaluate, how canonical resolves meaning"
- MC: "what to measure, how canonical feeds metrics"


## Options Considered

N/A

## Implications

1. **MappingsPage is obsolete** — TSK-05e8db aborted
2. **No mapping API endpoints needed** — mapping is created/stored as part of contract creation
3. **Mapping lives inside contract_version JSON** — canonical_mapping_version.mapping_json is the mapping, stored as part of the contract version
4. **Editing a mapping = creating a new contract version** — you don't "edit a mapping", you version the contract

## Relation to D203

D203 (formalize mapping_json) is still relevant — the structure of the mapping inside the contract needs to be well-defined. But it's a schema concern (what fields does mapping_json contain), not a UI concern (no separate page needed).

## Consequences

N/A
