---
uid: DEC-4a8abb
title: "MC Constant Value Propagation — End-to-End"
description: "Constants in metric formulas (C1=100, C1=90) must carry their value from seed catalog through metric_formula_variable to MC contract_json so the engine can evaluate them"
status: decided
date: 2026-04-15
project: bc-core
domain: metrics
decision_code: D329
authority: authoritative
refs:
  - type: decision
    uid: DEC-d72560
    label: "D301 — Canonical Field as 3rd Contract Primitive"
  - type: decision
    uid: DEC-c0290f
    label: "Metric Evaluation Engine spec (formula + variables + constants)"
  - type: decision
    uid: DEC-9d1f4b
    label: "D327 — Shared Dimension Normalization (prior session discovered alias collision, now discovers constant gap)"
  - type: document
    path: "docs/sops/metric-registration-sop.md"
    label: "Metric Registration SOP (Link 2b)"
  - type: document
    path: "docs/sops/mc-creation-sop.md"
    label: "MC Creation SOP (Link 5)"
migrated_from: legacy v2 archive
devhub_registration: doc-registry indexed; decision-registry PATH_MISMATCH **RESOLVED 2026-06-22** via the audit-driven `devhub_decision_update` extension (title_text + file_path now mutable). Registry row DEC-4a8abb: title="MC Constant Value Propagation — End-to-End", file_path=docs/adrs/ADR-4a8abb.md — both aligned with this file. Original drift recorded in Decision-Registration Integrity Audit 2026-06-22 §3.1 and Repair Closeout (same date).
---

# MC Constant Value Propagation — End-to-End

> **Decision-registration integrity (2026-06-22).** Originally classified `PATH_MISMATCH` in the [integrity audit](../../evidence/audits/implementation/devhub-decision-registration-integrity-audit-2026-06-22.md) §3.1 — **resolved the same day** via the audit-driven `devhub_decision_update` tool extension. The registry row `DEC-4a8abb` now correctly carries title "MC Constant Value Propagation — End-to-End" (D329) with `file_path: docs/adrs/ADR-4a8abb.md`. See the [repair closeout](../../evidence/closeouts/implementation/devhub-decision-registration-integrity-repair-closeout-2026-06-22.md) for the full pre-repair vs post-repair record. Content below is preserved verbatim per Foundation Invariant III.

## Context

During the greenfield tenant execution for demo-selenite (proven on 2026-04-15), 11 of 25 data-available AR MCs were rejected by the metric evaluation engine. Three of them failed with the same error:

```
No values for 'constant_percentage_multiplier' (C1)
```

Example MC — `mc__active_customer_rate`:
```json
"formula": { "text": "O1 = (SUM(I1) / SUM(I2)) * C1" },
"variables": [
  { "role": "output", "var_code": "O1", "field_code": "active_customer_rate" },
  { "role": "input",  "var_code": "I1", "field_code": "number_of_active_customer_accounts" },
  { "role": "input",  "var_code": "I2", "field_code": "total_customer_accounts" },
  { "role": "constant", "var_code": "C1", "field_code": "constant_percentage_multiplier" }
]
```

The engine reads `variable.value` for constants (`metric-evaluation-engine.service.ts:662`). If absent, it falls back to trying `Number(field_code)` — `Number("constant_percentage_multiplier")` is `NaN`, so the variable resolves to "no values" and evaluation fails.

A broader scan found **30+ MCs in accounts_payable** with the same pattern (constants like `constant_percentage_multiplier`, `constant_days_in_period`, `constant_100`). The gap is platform-wide, not AR-specific.

### Root Cause — 5-layer data gap

| Layer | State | Issue |
|---|---|---|
| Seed catalog (`bc_seed.seed_metrics`) | No `formula.constants` field | No upstream source of truth for constant values |
| Table `metric.metric_formula_variable` | No `constant_value` column | Platform data model cannot store the value |
| `CreateMcDto.variables` (mc-onboarding) | Only `role: 'input' \| 'output'` accepted | DTO rejects constant role outright |
| `buildMcEnvelope` (mc-onboarding) | Spreads `{var_code, role, field_code, description}` only | Even if DTO accepted `value`, the envelope builder would drop it |
| `CR-QG-MC-001` (quality gate) | No check for constant value presence | MCs with broken constants are registered as "passing" |

The chain is broken end-to-end. A one-off SQL patch on `metric_contract_version.contract_json` is a shortcut that:
- Violates **CM-INV-006** (active contracts are immutable; changes require a new version)
- Skips **CR-QG-MC-001** validation
- Has no provenance (no ADR, no approval, no audit trail)
- Does not prevent regression — the next MC registration reproduces the bug

## Decision

### D329-R1: Seed Catalog carries constant values

`bc_seed.seed_metrics` documents add a `formula.constants` field:

```json
{
  "metric_name": "active_customer_rate",
  "formula": {
    "text": "O1 = (SUM(I1) / SUM(I2)) * C1",
    "variables": [
      { "var_code": "I1", "role": "input",    "field_name": "number_of_active_customer_accounts" },
      { "var_code": "I2", "role": "input",    "field_name": "total_customer_accounts" },
      { "var_code": "C1", "role": "constant", "field_name": "constant_percentage_multiplier", "value": 100 },
      { "var_code": "O1", "role": "output",   "field_name": "active_customer_rate" }
    ]
  }
}
```

The `value` is a JSON `number`. Seed loaders (mega-CSV, TS-pack merge, internet merge) populate this when a constant reference is detected in `formula.text` (regex: `C\d+` without aggregation wrapper or documented as constant).

### D329-R2: Platform schema stores constant values

Add column to `metric.metric_formula_variable`:

```sql
ALTER TABLE metric.metric_formula_variable
ADD COLUMN constant_value NUMERIC NULL;

-- Integrity: constants must have value, inputs/outputs must not
ALTER TABLE metric.metric_formula_variable
ADD CONSTRAINT ck_constant_value_matches_role CHECK (
  (role = 'constant' AND constant_value IS NOT NULL)
  OR (role IN ('input', 'output') AND constant_value IS NULL)
);
```

Metric registration populates this column from the seed catalog.

### D329-R3: DTO accepts constant role

`mc-onboarding.service.ts CreateMcDto`:

```typescript
variables: Array<{
  varCode: string;
  role: 'input' | 'output' | 'constant';
  fieldCode: string;
  value?: number;          // required when role='constant'
  description?: string;
}>;
```

### D329-R4: MC onboarding propagates constant value

`buildMcEnvelope` includes `value` for constants:

```typescript
const variables: MetricVariable[] = dto.variables.map(v => ({
  var_code: v.varCode,
  role: v.role,
  field_code: v.fieldCode,
  ...(v.value !== undefined ? { value: v.value } : {}),
  ...(v.description ? { description: v.description } : {}),
}));
```

### D329-R5: Quality gate enforces constant value

Add to CR-QG-MC-001:

| # | Check | What it validates |
|---|---|---|
| 16 | **Constant variables have value (D329)** | Every `variables[]` entry with `role: 'constant'` MUST have a numeric `value` field. MCs missing this are rejected at creation time. |

### D329-R6: Existing broken MCs — versioned upgrade, not in-place patch

For the ~33 MCs currently missing constant values:
1. Seed catalog is updated with `formula.constants` via the seed-metrics merge script (D329-R1)
2. `metric_formula_variable.constant_value` is backfilled from the seed (D329-R2)
3. A **new MC version** is created via `mc-onboarding.service.create` (new version_code, e.g., `1.1.0`) carrying the constant value
4. The new version is activated; the old version is superseded via the governance state machine (`active` → `superseded`)
5. `contract_json` of the OLD version is NOT modified (CM-INV-006 preserved)

### D329-R7: Metric engine unchanged

The engine already handles `variable.value` correctly (`metric-evaluation-engine.service.ts:662`). No code change needed there — the fix is pushing the value into the contract, not changing how the engine reads it.

## Options Considered

### Option A: In-place SQL patch on `contract_json` (REJECTED)

Fastest, but violates CM-INV-006 (active contract immutability), has no provenance, doesn't fix the root (next MC registration reproduces the bug), doesn't populate the platform data model.

### Option B: Engine-side workaround — treat `field_code: "constant_N"` as value N (REJECTED)

Parse `constant_100` → 100, `constant_90` → 90. Works for numeric suffixes but fails for semantic ones like `constant_percentage_multiplier`. Encodes a magic-string convention into the engine. Technical debt.

### Option C: End-to-end propagation (CHOSEN)

Fix all 5 layers (seed → schema → DTO → service → gate). Larger change but addresses the root, preserves governance, prevents regression, makes BareCount's type authority consistent with its claim.

## Consequences

### Positive

- ~33 MCs immediately eligible to produce metric snapshots after remediation
- Future MCs with constants cannot be registered without a value (CR-QG-MC-001 #16 blocks)
- `metric_formula_variable` becomes the platform's source of truth for constants
- Seed catalog → metric_definition → MC propagation becomes lossless
- Provenance preserved — new MC versions carry the constant, old versions superseded via governance flow

### Negative

- Schema migration required (one column + check constraint)
- Seed catalog regeneration needed for metrics that reference constants
- MC onboarding service must be extended to accept `role: 'constant'` and `value`
- Each affected MC requires a new version — coordinated rollout

### Neutral

- No engine change (engine already correctly reads `variable.value`)
- No CC, OC, or BF impact (constants are MC-local)
- No tenant-facing breaking change (old MC versions stay superseded but readable for audit)

## Implementation Plan (summary)

1. Migration: `ALTER TABLE metric.metric_formula_variable ADD COLUMN constant_value ...`
2. Seed loader: extract constants from formula.variables during MongoDB seed_metrics load
3. Metric registration service: populate `constant_value` during `metric_formula_variable` insert
4. MC onboarding DTO + service: accept and propagate `role='constant'` with `value`
5. CR-QG-MC-001: add check #16
6. Backfill script: for each affected MC, call `mc-onboarding/create` with new version, carrying constant value from refreshed seed
7. SOP updates: metric-registration-sop.md (constant value step), mc-creation-sop.md (constant DTO shape)

## Out of Scope

- Derived/computed field support (covered by D330)
- Type conformance across SO→MS (covered by D331)
- Retroactive changes to engine behavior for unpatched MCs (engine guardrails stay; rejection is the correct outcome)
