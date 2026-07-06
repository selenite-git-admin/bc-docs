---
uid: DEC-da4c51
title: "Contract Trust Chain — Lifecycle Stages with Upward Trust Propagation"
description: "Lifecycle stages across source/canonical/metric layers with upward trust propagation and deterministic validation gates"
status: decided
subdomain: lifecycle
focus: governance
date: 2026-04-05T02:27:16.321Z
project: bc-core
domain: metrics
related: [DEC-9dce29, DEC-ecec75, DEC-69f09e]
foundation_doc: FND-msf001
migrated_from: legacy v2 archive
---

# Contract Trust Chain — Lifecycle Stages with Upward Trust Propagation

## Context

BareCount's metric catalog has grown to 10K+ metrics sourced from APQC, CXO packs, and internet KPIs. The current processing model relies on ad-hoc scripts (`metric-register.mjs`, enrichment SQL), AI classification (bc-ai maker-checker-gate), and human orchestration via SOPs. This model breaks at scale:

1. **No per-metric state.** Answering "which metrics are structurally complete?" requires joining across tables and hoping for consistency.
2. **No resumability.** Scripts crash at metric 847 of 2,000 — recovery is manual log-grep.
3. **No trust verification.** A metric formula references CO fields, but nothing checks whether those fields are themselves backed by verified source data. The metric looks complete but its inputs may be unproven.
4. **AI proposes, nothing validates.** AI enrichment suggests formulas and variable bindings, but no deterministic engine confirms structural soundness.

The 5D Metric Specification Framework (D282/FND-msf001) defines what a metric IS — purpose, shape, temporality, precision, impact. This decision defines what makes a metric TRUSTWORTHY by introducing lifecycle stages with deterministic gates that check trust downward through the contract chain.

## Decision

Introduce explicit lifecycle stages across three contract layers with deterministic advancement gates. Trust propagates upward; validation checks downward. A metric cannot advance unless its inputs are ready. Each gate is deterministic — no AI, no ambiguity.

## The Three Layers

### Layer 1: Source Field (already exists — D107/D110)

Source fields already track trust via two dimensions:

| Column | States | Meaning |
|--------|--------|---------|
| `verification_status` | `unverified → verified / manually_verified / disputed / rejected` | AI + human confidence in metadata quality |
| `validation_status` | `not_validated → validated` | Runtime proof: data has flowed through this field |

**No changes needed.** The source layer is the most mature trust model in the platform. CO fields check this layer when advancing.

### Layer 2: Business Field (CO field proxy — NEW)

Business fields (`contract.business_field`) currently have `status: draft → approved → deprecated`. This is a governance state, not a trust state. We add a trust dimension:

**New column: `certification_status`**

```sql
ALTER TABLE contract.business_field
  ADD COLUMN certification_status TEXT NOT NULL DEFAULT 'uncertified'
  CHECK (certification_status IN ('uncertified', 'certified'));
```

| Stage | Meaning | Gate to advance |
|-------|---------|-----------------|
| `uncertified` | Field definition exists but inputs unproven | — |
| `certified` | All source bindings resolve to verified source fields | Deterministic check (see gates below) |

**Certification gate (deterministic):**

```
For each business_field:
  1. At least one canonical_mapping references this field
  2. Each mapping's source_field has verification_status = 'verified' or 'manually_verified'
  3. Field data_type is explicitly set (not null, not 'unknown')
  → All pass: certification_status = 'certified'
  → Any fail: stays 'uncertified', gate returns specific blockers
```

Certification is **re-evaluated** whenever a source field's verification_status changes. If a source field is later disputed, the business field reverts to `uncertified`, which cascades upward to any metric referencing it.

### Layer 3: Metric Definition (EXTENDED)

Metric definitions currently have `maturity_code: draft → verified → locked`. This is too coarse — it conflates classification, enrichment, and structural validation into a single "verified" state.

**Replace `maturity_code` values** with a 5-stage lifecycle:

```sql
ALTER TABLE metric.metric_definition
  ALTER COLUMN maturity_code TYPE TEXT,
  DROP CONSTRAINT IF EXISTS metric_definition_maturity_code_check,
  ADD CONSTRAINT metric_definition_maturity_code_check
    CHECK (maturity_code IN ('registered', 'classified', 'enriched', 'validated', 'locked'));

-- Migrate existing data:
-- 'draft' → 'registered'
-- 'verified' → 'enriched' (conservative — verification was AI-only, not structural)
-- 'locked' → 'locked' (preserves any locked metrics)
```

| Stage | Meaning | Gate to advance |
|-------|---------|-----------------|
| `registered` | Metric passed AI 4-gate verification (classification, dedup, function, name) | AI verification evidence exists |
| `classified` | All 5D codes assigned, no collision-rule violations | All 5 codes non-null + no hard-block combinations (D282) |
| `enriched` | Formula decomposed, variables bound to business fields | Formula exists + every variable has a `business_field` binding |
| `validated` | Formula structurally sound, all inputs certified | Deterministic structural proof (see gate below) |
| `locked` | Ready for tenant binding and evaluation | Human or authorized agent sign-off |

## The Validation Gate (Layer 3 → `validated`)

This is the core engine. It is **deterministic, not AI**. It runs on all metrics in seconds.

```
Input:  metric_definition + metric_formula + variable_bindings

Checks:
  1. FORMULA PARSEABLE
     - Formula string parses to a valid expression tree (AST)
     - No undefined operators, no syntax errors

  2. VARIABLES RESOLVE
     - Every variable referenced in the formula has a binding record
     - Every binding points to an existing business_field (by field_id)
     - No dangling references

  3. INPUTS CERTIFIED
     - Every referenced business_field has certification_status = 'certified'
     - If any field is 'uncertified', the metric stays at 'enriched'
     - Gate returns: "blocked by N uncertified fields: [field_a, field_b, ...]"

  4. TYPES COMPATIBLE
     - Variable data types are dimensionally compatible
     - Division of currency by currency-per-time yields time (e.g., DPO)
     - No string ÷ number, no boolean + currency

  5. OUTPUT UNIT MATCHES
     - Computed output unit matches the metric's declared unit_code
     - If metric says "days" but formula computes "currency", reject

Output: PASS → advance to 'validated'
        FAIL → stay at 'enriched' + specific error list per check
```

**Checks 1-2** are structural (syntax + references).
**Check 3** is the trust chain — this is where upward propagation happens.
**Checks 4-5** are semantic (type system). These may be implemented in a later phase if a type system for business fields is not yet mature.

## Trust Propagation — The Full Chain

```
Source Field                    Business Field              Metric Definition
─────────────                   ──────────────              ─────────────────
verification_status             certification_status        maturity_code
  unverified                      uncertified                 registered
  verified ──────────────────────→ certified ────────────────→ classified
  manually_verified ─────────────→ certified                   enriched
  disputed ──────────────────────→ uncertified (CASCADE)       validated
  rejected ──────────────────────→ uncertified (CASCADE)       locked
                                                                │
validation_status                                               │
  not_validated (informational)                                 │
  validated (runtime proof)                                     │
                                                                ↓
                                                     Tenant binding + evaluation
```

**Cascade rule:** If a source field's `verification_status` changes from `verified` to `disputed`:
1. All business fields bound to it via `canonical_mapping` revert to `uncertified`
2. All metrics referencing those business fields revert from `validated` to `enriched`
3. This is logged as a trust chain break event (auditable)

Cascade is **downgrade-only**. Upgrading (re-certification after dispute resolution) requires re-running the gates.

## What Each Layer Owns

| Concern | Layer | Not |
|---------|-------|-----|
| "Does this source field exist and have good metadata?" | Source field (`verification_status`) | Metric or CO |
| "Is this business field backed by verified source data?" | Business field (`certification_status`) | Metric |
| "Is this metric structurally sound with trusted inputs?" | Metric (`maturity_code`) | Source or CO |

No layer re-validates another layer's concern. Each checks down one level only.

## Schema Summary

### New column

```sql
-- contract.business_field
certification_status TEXT NOT NULL DEFAULT 'uncertified'
  CHECK (certification_status IN ('uncertified', 'certified'))
```

### Modified column

```sql
-- metric.metric_definition: maturity_code
-- Old values: draft, verified, locked
-- New values: registered, classified, enriched, validated, locked
-- Migration: draft→registered, verified→enriched, locked→locked
```

### New indexes

```sql
idx_business_field__certification ON contract.business_field (certification_status);
idx_metric_definition__maturity   ON metric.metric_definition (maturity_code);
```

## Operational Impact — The Funnel

bc-admin metric catalog dashboard shows a funnel:

```
10,241 seeded (MongoDB seed catalog — outside this lifecycle)
 4,200 registered (passed AI verification)
 3,800 classified (5D codes assigned)
 2,100 enriched (formula + variable bindings)
   600 validated (structural proof + certified inputs)
   200 locked (signed off, ready for tenants)

Blocked at enriched → validated:
  340 uncertified business fields across 12 canonical contracts
  → Fix these 340 fields to unblock 1,500 metrics
```

This is how you stop holding 10K states in your head. The system holds them.

## Implementation Phases

**Phase 1: Metric lifecycle (high value, self-contained)**
- Extend `maturity_code` to 5 states
- Migrate existing data
- Build classification gate (5D check)
- bc-admin funnel view

**Phase 2: Business field certification**
- Add `certification_status` to `business_field`
- Build certification gate (check source bindings)
- Wire cascade from source `verification_status` changes

**Phase 3: Validation engine**
- Formula parser (AST) — builds on D281
- Variable resolution checker
- Trust chain check (certified inputs)
- Type compatibility (if type system is ready)

**Phase 4: Batch runner**
- Query "all metrics at stage X" → attempt next transition
- Resumable, idempotent, checkpointed
- Replaces ad-hoc scripts

## What This Does NOT Cover

- **Tenant runtime evaluation.** The execution model (SO → CO → Metric Snapshot) is unchanged. This decision governs platform definition readiness, not tenant runtime.
- **AI enrichment quality.** AI proposes formulas and bindings. This decision validates structure, not semantic correctness of formulas.
- **Seed catalog lifecycle.** The seed catalog remains a library with `confidence` (high/medium/low). Lifecycle starts at registration.

## Supersedes

Nothing. This extends D282 (5D framework) with a lifecycle dimension and extends D107/D110 (source catalog status) with upward trust propagation.

## References

- **D282** (DEC-9dce29): Metric Specification Framework — defines the 5D classification this lifecycle advances through
- **D068** (DEC-ecec75): One contract per KPI — the 714→10K metric architecture this engine must scale to
- **D107/D110**: Source catalog 3-dimensional status — the foundation this trust chain builds on
- **D281** (DEC-063b5e): Formula AST parser — prerequisite for Phase 3 validation engine
- **D148** (DEC-69f09e): Naming standards — column naming follows ISO 11179
- **FND-msf001**: Metric Specification Framework foundation document
