---
uid: DEC-bef347
title: "Structural Completeness — All Contract Instance Keys Required, No Structural Optionality"
description: "All contract instances must have identical structure — every key present, no structural optionality. AWS IAM principle."
status: implemented
subdomain: master-shape
focus: governance
date: 2026-04-02T12:43:45.206Z
project: bc-docs
domain: foundation
migrated_from: legacy v2 archive
---

# Structural Completeness — All Contract Instance Keys Required, No Structural Optionality

## Context

1. Code consuming contracts must defensively check every field if keys can be absent — increases complexity and bugs.
2. Two instances of the same type looking structurally different is confusing for new developers and agents.
3. AWS IAM policies follow this principle — every policy of one type has the same keys. Proven at scale.
4. x-governance tags on every direct key enable machine-readable enforcement of tenant override rules.
5. 687 metric contracts validated 100% after migration — proves the approach works.

## Decision

All instances of a contract type must be structurally identical. Every key defined in the master schema (contract_meta_schema) must be present in every platform instance (contract_json). Optional means the VALUE can be empty/null/default — not that the KEY can be absent.

Applied to metric v1: 63 keys total (4 envelope + 16 header + 8 body direct + 35 nested). All 16 header keys moved from optional to required. x-governance tags added to all 26 direct keys (24 fixed, 1 overridable, 1 extensible).

This principle applies to all 6 contract families. Each family will be updated to enforce structural completeness.
