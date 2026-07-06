---
uid: DEC-f1dae0
title: "Standards-First BF/BO Creation — OAGIS Primary, Metrics Validate"
description: "BF/BO sourced from OAGIS/CCTS standards, not metric formulas. BO→CC is 1:N (CCTS ACC→ABIE). PII on BF. D225 data deleted."
status: implemented
subdomain: business-object-model
focus: governance
date: 2026-04-06T02:40:38.766Z
project: bc-docs
domain: contracts
supersedes: DEC-6d8be5
migrated_from: legacy v2 archive
---

# Standards-First BF/BO Creation — OAGIS Primary, Metrics Validate

## Context

D225 generated 45 BOs and 1,604 BFs from metric formula variables. All BFs were measures — zero identifiers, dimensions, keys, dates, text. Structurally useless for canonical chain. Root cause: metrics are consumers of business vocabulary, not the source. Coupling BFs to metric i/o causes error propagation, measure bias, incomplete vocabulary, and implicit coupling. Standards (OAGIS, CCTS) provide production-proven, complete entity definitions with all semantic roles. The controlled vocabulary principle ensures formula authors pick from the directory instead of inventing names.

## Decision

Business Fields and Business Objects are defined from authoritative standards (OAGIS, UN/CEFACT CCTS, ISO 20022, SID), not from metric formula variables. Metric formulas validate against the BF vocabulary — they bind to existing BFs, not generate new ones. The D225 bottom-up premise (metric variables → BF → BO) is superseded. BO→CC cardinality corrected from 1:1 to 1:N following CCTS ACC→ABIE derivation pattern. BF carries PII classification (4-tier) propagating through contract chain. All D225-generated BOs (45) and BFs (1,604) to be deleted and regenerated from standards.
