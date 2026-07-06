---
uid: DEC-efe97f
title: "Inline text[] tags retained — junction tables deferred until cross-entity tag querying needed"
description: "Keep inline text[] arrays for tags across 14 tables. Junction tables deferred — migration blast radius disproportionate to normalization benefit with no cross-entity query need."
status: decided
subdomain: deferred-normalization
focus: inline-tags-deferral
date: 2026-03-17
project: bc-admin
domain: database
refs:
  - type: decision
    label: "D089"
authority: authoritative
migrated_from: legacy v2 archive
---


# Inline text[] tags retained — junction tables deferred until cross-entity tag querying needed

## Context

Cost-benefit: massive migration for zero current benefit. The rule exists for cases where tags are shared entities — ours are simple annotations. Will revisit when the need materializes.

## Decision

14 tables use inline text[].array() for tags. D089 rule 5 recommends shared tag + entity_tag junction tables. Decision: retain inline arrays for now.

Rationale: (1) Tags are simple strings, not rich entities with lifecycle/metadata. (2) PostgreSQL text[] with ANY() is efficient for per-entity tag filtering. (3) Junction tables would add JOINs to every list query across 14 entities with no current use case for cross-entity tag querying. (4) Migration blast radius is 14 tables + 14 repositories + 14 services + bc-admin — disproportionate to the normalization benefit.

Trigger for revisiting: when a "find all entities tagged X" cross-entity search is needed, or when tag governance (who can create tags, tag synonyms, tag hierarchy) becomes a requirement.

## Options Considered

N/A

## Consequences

N/A
