---
uid: DEC-9a5dc0
title: "CF Boundary — Reporting Standards Promote to Canonical Fields"
description: "BFs that represent financial reporting concepts (US_GAAP, IFRS, COSO, IIA) promote to canonical fields. BFs remain source-observable only. Eliminates dual chain routes and misclassified integrity breaks."
status: decided
date: 2026-04-11
project: bc-core
domain: contracts
refs:
  - type: decision
    uid: DEC-d72560
    label: "D301: Canonical Field as 3rd Contract Primitive — Two-Vocabulary Model"
  - type: decision
    uid: DEC-2e4cb3
    label: "BO/BF is organizational grouping, not computational node"
  - type: document
    path: "sops/bf-sf-alias-sop.md"
    label: "BF-SF Alias SOP — defines alias as 1:1 source field mapping"
migrated_from: legacy v2 archive
devhub_registration: doc-registry indexed; decision-registry row absent (FILE_ONLY_UNEXPLAINED per Decision-Registration Integrity Audit 2026-06-22). File-side authority preserved per Foundation Invariant III; no successor minted, no UID re-allocation.
---

# CF Boundary — Reporting Standards Promote to Canonical Fields

> **Decision-registration integrity (2026-06-22).** Classified `FILE_ONLY_UNEXPLAINED` in the [integrity audit](../../evidence/audits/implementation/devhub-decision-registration-integrity-audit-2026-06-22.md) §3.2 and preserved as a file-side authority in the [repair closeout](../../evidence/closeouts/implementation/devhub-decision-registration-integrity-repair-closeout-2026-06-22.md). This ADR was hand-filed and is not in the DevHub decision registry; cross-references treat it as authoritative for D302 (CF Boundary). The current `devhub_decision_record` allocator mints new UIDs, so registering this existing UID via tooling is not supported — preservation is chosen over re-mint per operator doctrine. Content below is preserved verbatim per Foundation Invariant III.

## Context

D301 (DEC-d72560) established two vocabularies:

- **BFs** = source-side vocabulary (what exists in the source system)
- **CFs** = metric-side vocabulary (what metrics need)

But the existing 7,062 BFs were never re-evaluated after D301. Many BFs represent **financial reporting concepts** — line items from XBRL US-GAAP taxonomy, IFRS reporting standards, COSO governance framework, and IIA audit standards. These are metric-side vocabulary sitting in the source-observation layer.

### The Problem: Dual Chain Routes

With reporting-standard BFs on BOs, the integrity chain has two routes:

1. **Observable path** (works): MC → CF → cc_field_mapping → BF → OC field_mapping → source field
2. **Reporting-concept path** (broken): MC → CF → cc_field_mapping → BF (XBRL) → NO OC exists → integrity break

Route 2 creates ~2,400 phantom integrity breaks. These BFs can never have OC field_mappings because they don't map 1:1 to source system fields — they represent aggregated, computed, or classified financial reporting concepts.

### The Wrong Precedent

During alias enrichment (session Apr 11 2026), `definition_standard` was incorrectly treated as a source system discriminator:

- OAGIS BFs → "need SAP aliases" (correct)
- US_GAAP BFs → "need XBRL source system" (WRONG)
- IFRS BFs → "need IFRS reporting source" (WRONG)

But `definition_standard` = WHO DEFINED THE NAME, not where the data comes from. A US_GAAP concept like `retained_earnings` gets its VALUE from SAP GL accounts (FAGLPOSE), not from an XBRL filing feed. The standard defines the vocabulary; the source system provides the data.

### Evidence: XBRL BOs Are Taxonomy Registries, Not Observation Targets

| BO | BFs | Has OC | Has Aliases | Nature |
|---|---|---|---|---|
| xbrl_gaap_balance_sheet | 1,068 | No | 0 | Taxonomy: XBRL reporting line items |
| xbrl_gaap_income_statement | 718 | No | 0 | Taxonomy: XBRL reporting line items |
| xbrl_gaap_cash_flow | 431 | No | 0 | Taxonomy: XBRL reporting line items |
| xbrl_gaap_equity | 189 | No | 0 | Taxonomy: XBRL reporting line items |
| ifrs_balance_sheet | 36 | No | 0 | Taxonomy: IFRS reporting line items |
| ifrs_income_statement | 33 | No | 0 | Taxonomy: IFRS reporting line items |

None of these have OCs or aliases. They never will — they're reporting concepts, not source-observable fields. Treating them as BFs forces the integrity chain into a dual-route model that the architecture wasn't designed for.

### BO-BF Layer Retains Value

Considered retiring BO-BF entirely (absorbing into CC). Rejected because:

1. **Onboarding unit** — BOs define "what fields we observe from your SAP BKPF table" during tenant onboarding
2. **Multi-system abstraction** — BF `company_code` with aliases for SAP (BUKRS), Oracle (ORG_ID), Tally (COMPANY) provides source-system independence
3. **Quality gates** — BF registration has dedup, PII classification, ISO 11179 naming

These serve the source-observation layer and remain valuable. The fix is content migration, not architecture change.

## Decision

### D302.1: CF Boundary Rule

**BFs = source-observable only. CFs = everything else.**

A concept is a BF if and only if it can be mapped 1:1 to a field in at least one source system. If it requires aggregation, computation, classification, or filtering to derive from source data, it is a CF.

| Standard | Nature | Placement |
|---|---|---|
| OAGIS | Source system field vocabulary | **BF** |
| ISO_20022 | Financial messaging fields | **BF** |
| BARECOUNT | Platform operational fields (observable) | **BF** |
| US_GAAP | Financial reporting line items | **CF** |
| IFRS | Financial reporting line items | **CF** |
| COSO | Governance/control concepts | **CF** |
| IIA | Internal audit concepts | **CF** |

### D302.2: Promotion Migration

BFs with `definition_standard` in (US_GAAP, IFRS, COSO, IIA) on reporting-taxonomy BOs are **promoted** to canonical fields:

1. Create corresponding `canonical_field` rows (preserving name, definition, function_code, data_type)
2. Create `cc_field_mapping` rows linking new CFs to source-level BFs with appropriate resolution rules
3. Remove promoted BFs from `business_object_field` junction
4. Archive the reporting-taxonomy BOs (xbrl_gaap_*, ifrs_*)

### D302.3: Integrity Chain — Single Route

After migration, every BF has an OC observation path. The integrity service checks:

- CF → cc_field_mapping → BF → OC field_mapping → source field (single route, no exceptions)

Phantom breaks from reporting-concept BFs are eliminated.

### D302.4: CC Resolution for Reporting Concepts

CCs that serve reporting concepts (cc__xbrl_gaap_equity, cc__gaap_income_statement, etc.) use cc_field_mapping with:

- **resolution_rule**: `sum`, `count`, `latest`, `assert_equal`, etc.
- **filter_json**: account group filters, classification codes, temporal windows

Example: CF `retained_earnings` → BF `gl_posting_amount` (on actual_ledger BO), resolution: `sum`, filter: `{account_group: "retained_earnings_accounts"}`.

## Consequences

### Positive
- Single integrity chain route — no special cases
- ~2,400 phantom breaks eliminated
- CF table grows from ~3,095 to ~5,500 (richer metric vocabulary)
- BF table shrinks from ~7,062 to ~4,500 (all source-observable)
- Clear boundary: BF = source-side, CF = metric-side (D301 fully realized)

### Negative
- Migration effort: ~2,400 BFs to promote, cc_field_mappings to create
- Existing MCs referencing XBRL CCs may need co_bindings updates
- 4 XBRL BOs + 2 IFRS BOs archived (6 BOs retired)

### Risks
- **RSK-1**: cc_field_mapping resolution rules may not cover all XBRL aggregation patterns. Mitigate: extend resolution_rule vocabulary as needed (already extensible per D301).
- **RSK-2**: Some XBRL concepts may actually be source-observable in specific systems. Mitigate: during promotion, flag edge cases for manual review.

## D302.5: Computed BFs Bypass (REVERTED — Apr 11 2026)

**Status: REVERTED.** D302.5 was an evidence-based bypass that silenced integrity checks for BFs with zero aliases and zero OC mappings. It was reverted because relaxing rules to improve compliance numbers defeats the purpose of the integrity chain. The only metric that matters is whether a metric can actually compute end-to-end with real source data. Bypasses that say "don't check this" don't make metrics work — they silence the alarm.

The 221 BFs (191 BARECOUNT, 21 NULL-standard, 9 OAGIS) that D302.5 covered remain as honest gaps. They need real OC field_mappings, not bypass rules.

D302.1 (standard-based bypass for US_GAAP/IFRS/COSO/IIA) is also removed from the integrity service. These reporting-concept BFs still need the migration described in D302.2 — promotion to CFs with proper cc_field_mapping resolution paths that trace to source-observable BFs.

## Migration Plan

Phase 1 (proof): Promote `xbrl_gaap_equity` (189 BFs) → verify chain integrity
Phase 2: Promote remaining XBRL BOs (2,217 BFs)
Phase 3: Promote IFRS BOs (69 BFs)
Phase 4: Promote COSO/IIA BOs (52 BFs)
Phase 5: Archive emptied BOs, update integrity service
