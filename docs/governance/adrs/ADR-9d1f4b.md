---
uid: DEC-9d1f4b
title: "Shared Dimension Normalization in CC Field Selection"
description: "CC field_selection and resolved_schema MUST normalize BO-scoped shared dimension variants to their shared names, fixing the chain grain check loop"
status: decided
date: 2026-04-14
project: bc-core
domain: contracts
decision_code: D327
authority: authoritative
refs:
  - type: decision
    uid: DEC-f66378
    label: "D292 — BO-Scoped BF Composition"
  - type: decision
    uid: DEC-68f2c7
    label: "D294 — company_code as 5th Shared Exception"
  - type: decision
    uid: DEC-d72560
    label: "D301 — Canonical Field as 3rd Contract Primitive"
  - type: decision
    uid: DEC-bebaec
    label: "D305 — Chain Completeness SSOT"
  - type: document
    path: "docs/architecture/contract-chain-mapping-requirements.md"
    label: "Chain Mapping Requirements (Q2: shared dims everywhere in CC)"
  - type: document
    path: "docs/architecture/contract-chain-assembly.md"
    label: "Contract Chain Assembly (spine)"
  - type: document
    path: "docs/sops/cc-creation-sop.md"
    label: "CC Creation SOP (contradicts itself on shared dim naming)"
  - type: document
    path: "docs/sops/mc-creation-sop.md"
    label: "MC Creation SOP (grain uses shared names — correct)"
migrated_from: legacy v2 archive
devhub_registration: doc-registry indexed; decision-registry PATH_MISMATCH **RESOLVED 2026-06-22** via the audit-driven `devhub_decision_update` extension (title_text + file_path now mutable). Registry row DEC-9d1f4b: title="Shared Dimension Normalization in CC Field Selection", file_path=docs/adrs/ADR-9d1f4b.md — both aligned with this file. Original drift recorded in Decision-Registration Integrity Audit 2026-06-22 §3.1 and Repair Closeout (same date).
---

# Shared Dimension Normalization in CC Field Selection

> **Decision-registration integrity (2026-06-22).** Originally classified `PATH_MISMATCH` in the [integrity audit](../../evidence/audits/implementation/devhub-decision-registration-integrity-audit-2026-06-22.md) §3.1 — **resolved the same day** via the audit-driven `devhub_decision_update` tool extension (title_text + file_path + description_text are now mutable from MCP). The registry row `DEC-9d1f4b` now correctly carries title "Shared Dimension Normalization in CC Field Selection" (D327) with `file_path: docs/adrs/ADR-9d1f4b.md`. See the [repair closeout](../../evidence/closeouts/implementation/devhub-decision-registration-integrity-repair-closeout-2026-06-22.md) for the full pre-repair vs post-repair record. Content below is preserved verbatim per Foundation Invariant III.

## Context

### The Problem

The contract chain has been stuck in a loop where ~62 metric contracts (MCs) remain at `chain_verdict = 'partial'` despite all their variables being complete (`variables_complete = total_variables`). The blocking check is `grain_complete = false` — the E2 grain check in ChainStatusService (D305).

### Root Cause Analysis (7 Gaps)

A comprehensive investigation across 5 independent analyses (DDL/schema, SOPs, services, chain status logic, SOP detail) identified 7 cascading gaps, all stemming from a single unresolved design question: **how should the 5 shared reference dimensions (D292) be named in CC field_selection, resolved_schema, and grain?**

The 5 shared reference dimensions (D292, D294):
- `company_code`
- `currency_code`
- `language_code`
- `country_code`
- `unit_of_measure`

These BFs are exempted from BO-scoping (D292) because they are universal grain dimensions used identically across all BOs. A multi-CC metric like DSO needs ONE grain key (`company_code`) that matches across `cc__receivable_hdr` and `cc__invoice_hdr`.

### The Contradiction

| Document | What it says for shared dims in CC |
|---|---|
| **CC SOP** conceptual sections (lines 130, 139) | `company_code` (shared name) |
| **CC SOP** Step 2 example (line 220) | `field_code: "invoice_hdr_company_code"` (BO-scoped) |
| **CC SOP** Step 3 field_selection (line 240) | `"invoice_hdr_company_code"` (BO-scoped) |
| **CC SOP** Step 4 resolution_rules (line 265) | `"invoice_hdr_company_code"` (BO-scoped) |
| **CC SOP** Programmatic body (line 466) | `"invoice_hdr_company_code"` (BO-scoped) |
| **MC SOP** Step 6 grain (line 279) | `field_code: "company_code"` (shared name) |
| **MC SOP** note (line 284) | "company_code uses the shared BF name, not BO-scoped" |
| **Mapping Requirements** Q2 (line 343) | "shared dims use shared name EVERYWHERE in CC" |

The CC SOP's own conceptual overview and its step-by-step instructions use different naming for the same field. The MC SOP and Mapping Requirements doc are internally consistent (shared names) but contradict the CC SOP examples.

### The Cascade

```
GAP-A (BF+BO)  → BO has both shared + BO-scoped BF for same source field
GAP-C (OC)     → OC picks BO-scoped BF (no shared dim guidance in SOP)
GAP-D (CC)     → CC auto-derives from BO, inherits BO-scoped names — ROOT CAUSE
GAP-E (CM)     → CM overlap: OC BO-scoped name vs CC BO-scoped name = match,
                  but after fix CC has shared name → need equivalence check
GAP-F (MC)     → MC grain uses shared name (correct per MC SOP) but CC schema
                  has BO-scoped name → E2 fails
GAP-G (Chain)  → E2 grain check non-deterministic based on which CCs bound
GAP-B (CF)     → No CF Seeding SOP (compounds problem with ad-hoc CF naming)
```

### The Service Code

CC onboarding service (`cc-onboarding.service.ts:179`):
```typescript
const fieldSelection = boFields.map(f => String(f.name)).filter(name => !exclusions.has(name));
```
No shared dimension handling. BO field names pulled verbatim.

Chain status E2 check (`chain-status.service.ts:633`):
```typescript
const grainComplete = grainFields.every(g => {
  if (g.source === 'evaluation_period') return true;
  return g.field_code != null && ccSchemaFields.has(g.field_code);
});
```
Checks MC grain `field_code` against CC `resolved_schema.properties` keys. If MC has `company_code` but CC has `invoice_hdr_company_code`, the check fails.

### Why This Matters

This is not a cosmetic issue. The grain naming mismatch:
1. Blocks 62 MCs from reaching `chain_verdict = 'complete'`
2. Blocks the metric evaluation engine at runtime (GROUP BY `company_code` finds nothing in COs that have `invoice_hdr_company_code`)
3. Creates an infinite loop: fix CC → breaks OC R4 check → fix OC → breaks BO composition → back to start

## Decision

### D327-R1: CC MUST normalize shared dimensions

When the CC onboarding service derives `field_selection`, `resolved_schema`, and `resolution_rules` from BO composition, BO-scoped variants of the 5 shared reference dimensions MUST be normalized to their shared names.

**Specifically:**
- If BO has `invoice_hdr_company_code` (BO-scoped) and/or `company_code` (shared), CC `field_selection` uses `company_code`
- CC `resolved_schema.properties` uses `company_code` as the property key
- CC `resolution_rules[].field_code` uses `company_code`
- CC `grain[].field_code` uses `company_code`

The normalization constant `SHARED_BF_NAMES` at `bc-core/src/registry/oagis-d292.ts:17` is the single source of truth for which names are shared.

### D327-R2: MC grain MUST use shared names (reaffirmed)

This reaffirms the existing rule in the MC SOP (line 284) and Mapping Requirements Q2. MC grain `field_code` for shared dimensions MUST use the shared BF name (`company_code`), not the BO-scoped variant.

This was already the documented rule. The fix enforces it consistently.

### D327-R3: CM overlap MUST recognize shared dimension equivalence

When computing field overlap between OC `field_mappings` and CC `field_selection`, the CM onboarding service MUST recognize that a BO-scoped variant (e.g., `invoice_hdr_company_code` in OC) matches the shared name (e.g., `company_code` in CC) for the 5 shared reference dimensions.

### D327-R4: Chain status E2 MUST have defensive shared dimension fallback

During the remediation window (some CCs fixed, others not), the E2 grain check MUST fall back to checking BO-scoped variants when the shared name is not directly found in CC schema. This is a temporary measure that becomes a no-op once all CCs are remediated.

### D327-R5: MC creation MUST pre-validate grain against CC resolved_schema

The MC onboarding service MUST add an E2-equivalent check at creation time. If a grain field_code is not found in any bound CC's resolved_schema, the MC preview MUST flag this as a validation failure. This catches the problem at creation time, not after chain status refresh.

### D327-R6: CF Seeding requires a governing SOP

Link 2c (Canonical Field seeding) MUST have a formal SOP. This closes GAP-B. The SOP defines: how to extract CF names from metric formula variables, how to register them, and how to verify completeness before CC creation.

## Options Considered

### Option A: Normalize at CC creation (CHOSEN)

CC is the translator between source vocabulary (BF) and metric vocabulary (CF). It is architecturally correct for the CC to normalize shared dimensions — the CC already translates between vocabularies via `cc_field_mapping`, and normalizing shared dims in `field_selection`/`resolved_schema` is the same kind of translation.

**Pros:**
- Single point of fix (CC onboarding service)
- Backward compatible (existing "complete" chains unaffected)
- No DB schema changes
- Aligns with Mapping Requirements Q2 (already the documented rule)
- CC becomes the consistent translator as designed
- Multi-CC grain matching works automatically

**Cons:**
- CC `field_selection` no longer exactly mirrors BO composition field names for the 5 shared dims
- Existing CCs need one-time remediation (contract_json patch, not re-creation)

### Option B: Normalize at E2 grain check only (REJECTED)

Modify the chain status E2 check to try both shared and BO-scoped names.

**Why rejected:**
- Pushes the problem downstream instead of fixing the source
- Every consumer of CC resolved_schema must implement the same fallback
- Does not fix CM overlap computation (GAP-E)
- Does not fix runtime metric evaluation (GROUP BY still fails on mismatched names)
- Violates "CC is the translator" design principle

### Option C: Normalize at BO composition (REJECTED)

Ensure BOs never have BO-scoped variants of shared dimensions.

**Why rejected:**
- Breaks D292 which requires BO-scoped naming for ALL BFs except the 5 exceptions
- Many BOs correctly have `invoice_hdr_company_code` as a legitimate BF mapped from source fields (e.g., SAP BUKRS)
- Changing BO composition would break existing OC field_mappings that reference BO-scoped names
- Would require re-creating all OCs — massive blast radius

## Consequences

### Positive

- 62 MCs currently stuck at `partial` will reach `complete` after CC remediation
- The infinite fix loop breaks permanently — shared dims have ONE naming rule across all layers
- Multi-CC metrics (DSO, CCC, etc.) work with consistent grain matching
- Runtime metric evaluation GROUP BY finds the correct fields in COs
- CC SOP, MC SOP, and Mapping Requirements Q2 become consistent
- CF Seeding SOP closes the last ungoverned step in the chain

### Negative

- CC `field_selection` will not be a 1:1 mirror of BO composition for the 5 shared dims
- Existing CCs need a one-time contract_json patch (not re-creation)
- CM overlap logic becomes slightly more complex (shared dim equivalence check)

### Risks

| Risk | Mitigation |
|---|---|
| Remediation script damages existing CCs | Run one-then-many (D268). Verify ONE CC fully before scaling. |
| OC field_mappings use shared names but CC now also has shared names → double overlap | CM overlap deduplicates. The overlap set is idempotent. |
| A BO-scoped BF is mistakenly identified as a shared dim variant | Match only the exact 5 names from `SHARED_BF_NAMES`. Use `endsWith('_' + sharedName)` pattern, not substring. |
| New CCs created between decision and service fix | Defensive E2 fallback (D327-R4) handles this transition period. |

### Neutral

- No DB schema changes required
- No API contract changes
- No breaking changes to existing complete chains
- The `SHARED_BF_NAMES` constant already exists and is maintained
