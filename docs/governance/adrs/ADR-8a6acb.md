---
uid: DEC-8a6acb
title: "SC Body Purity — Remove extraction_rules and effective_period"
description: "SC body carries only structural declaration (6 fields). extraction_rules moved to Reader Flavor, effective_period to governance lifecycle."
status: implemented
subdomain: body-purity
focus: master-shape
date: 2026-04-02T04:11:30.186Z
project: bc-docs
domain: foundation
migrated_from: legacy v2 archive
---

# SC Body Purity — Remove extraction_rules and effective_period

## Context

SC's own requirements (CR-SC-004) state "does not define extraction scheduling or connection credentials — those are runtime/deployment concerns." extraction_rules contradicted this boundary. effective_period duplicated governance state already on the version table. Removing both makes the SC body a clean structural declaration with no runtime or lifecycle leakage.

## Decision

Source Contract body is purely structural. Two fields removed during master shape review:

1. **`extraction_rules`** (batch_size, ordering, pagination) — runtime/Reader Flavor concern, not contract structure. SC declares WHAT is contracted, not HOW to extract. Moved to Reader Flavor config.

2. **`effective_period`** — governance lifecycle concern, not body concern. Contract activity is governed by the version table's governance state (draft → approved → active → superseded). A date range in the body is redundant.

SC v1 master shape: 6 fields only — table_code, label, source_system_version_id, module_code, fields[], primary_key. Pure structure, nothing else.
