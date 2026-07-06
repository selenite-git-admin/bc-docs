---
uid: DEC-deac26
title: "Canonical mapping — rename mapping_binding, move from master to contract schema"
description: "Rename master.mapping_binding to contract.canonical_mapping. It is a contract artifact, not reference data — belongs with other contract tables."
status: implemented
subdomain: naming-convention
focus: schema-rename
date: 2026-03-20
project: bc-core
domain: database
refs:
  - type: decision
    label: "D054"
authority: authoritative
migrated_from: legacy v2 archive
---


# Canonical mapping — rename mapping_binding, move from master to contract schema

## Context

Three issues: (1) "mapping_binding" mashes two nouns — it's just a canonical mapping (how source fields resolve to canonical fields). (2) Not master/reference data — it's a contract artifact per D044 (split from canonical contract). Belongs with other contract tables. (3) master schema should only contain true reference data (domains, currencies, countries, statuses, libraries).

## Decision

Rename `master.mapping_binding` → `contract.canonical_mapping` and `master.mapping_binding_version` → `contract.canonical_mapping_version`. PK: `canonical_mapping_id`. Version FK: `canonical_mapping_id`. binding_json → mapping_json. All indexes renamed accordingly. D054 two-layer scoping preserved: NULL tenant_id = platform template, set tenant_id = tenant instance.

## Options Considered

N/A

## Consequences

N/A
