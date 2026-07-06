---
uid: DEC-ca4c1e
title: "AC Master Shape Locked — DQC-Integrated Admission Contract Body v1"
description: "AC body locked: 8 fields with DQC three-tier rules (GL/PL/TN), structural validation, rulebook reference. Foundation F04 authored. All 6 families now locked."
status: implemented
subdomain: master-shape
focus: master-shape
date: 2026-04-02T06:25:32.681Z
project: bc-docs
domain: foundation
migrated_from: legacy v2 archive
---

# AC Master Shape Locked — DQC-Integrated Admission Contract Body v1

## Context

AC was the last unlocked family, pending DQC integration (D247). With Foundation F04 QC Rulebook authored, the AC body can reference the rulebook for global rules and carry only table-specific platform rules in its body. This completes the contract shape unification — all 6 families have locked v1 body shapes.

## Decision

AC body finalized with DQC integration per D247. 8 fields: source_contract_version_id, rulebook_version, structural_validation, field_rules[], record_rules[], outcome_thresholds, validation_policy, max_observation_age.

Key design:
- `rulebook_version` references Foundation F04 QC Rulebook — global rules (GL-*) loaded at runtime, not duplicated in body
- `structural_validation` runs BEFORE any rules — catches schema drift (field count, unknown/missing fields)
- `field_rules[]` and `record_rules[]` carry PL-* (platform) rules with DQC category, severity, action per rule
- Tenant rules (TN-*) in contract_binding.extensions_json — complete, self-standing rule entries
- Execution follows QC Rulebook precedence: structural → completeness → uniqueness → referential → range → freshness → duplicate → business_logic
- DQ score computed per QC Rulebook penalty weights

Foundation F04 authored: index.md (DQC overview + boundary mapping) and qc-rulebook-v1.md (8 categories, 4 GL-* rules, penalty weights, precedence, rule entry structure).

All 6 contract families now have locked v1 body shapes.
