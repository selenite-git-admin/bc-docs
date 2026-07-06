---
title: "Session findings — MC body authority, D329 constants, seed thinness, header divergence (SES-594568)"
session: SES-594568
date: 2026-05-14
status: complete
type: session-findings
authority: DEC-a17d0f
related:
  - 2026-05-14-pass1-calibration-q1-q4-SES-594568.md
  - 2026-05-14-slice1-promotion-gate-plan-SES-594568.md
  - 2026-05-14-slice1-preflight-result-SES-594568.md
  - 2026-05-14-dbcp-verdict-code-extension-SES-594568.md
  - DEC-01419c     # MC body purity, 9 keys
  - DEC-01df6b     # contract_json authoritative; catalog derived
  - DEC-4a8abb     # D329 — MC Constant Value Propagation End-to-End
---

# Session findings — for future sessions

Recorded after slice (1) pre-flight surfaced multiple architectural
realities that future sessions need to know without re-discovering.
None of these findings introduce new architecture; they document
the live state, name the divergences from Foundation, and lock in
the rules that the slice ladder is operating under.

## 1. Master-shape JSON authority

**Live runtime authority:**
`C:\MyProjects\bc-core\src\registry\meta-schemas\metric-v1.schema.json`.

**Stale archive copy:**
`legacy-v2-docs-root\docs\system\foundation\contract-schemas\schemas\metric-v1.json`.

The v2 archive **lacks** the D329 `value` property on
`variables[].items` and is otherwise out of date. Future sessions
must read the bc-core copy when verifying body shape. Reading the
v2 file produced a false blocker mid-session and cost time.

Foundation chapter `the-contract-grammar.md` is correct at the
prose level but does not contain the JSON; the JSON lives in
bc-core.

## 2. MC envelope shape (Foundation §Common Header)

Per `bc-docs-v3/docs/foundation/the-contract-grammar.md` §Envelope
and §Common Header:

**Envelope — 4 keys, `additionalProperties: false`:**

| Key | Type | Purpose |
|---|---|---|
| `$contract` | string constant | Meta-schema identifier, e.g. `barecount/metric/v1` |
| `version` | string (semver) | Version of the published contract instance |
| `header` | object | Common governance and identity metadata |
| `body` | object | Family-specific declaration |

**Common header — 16 required keys** (each required per
Foundation): `contract_id`, `name`, `display_name`, `category`
(enum), `kind`, `created_at`, `owner`, `tags`, `description`,
`domain`, `subdomain`, `tenant_scope`, `governance`,
`compatibility_policy`, `lineage`, `bindings`.

Foundation specifies sub-shapes for `owner` (`team`, `email`,
`slack`, `oncall`), `tenant_scope` (`scope`, `provider`,
`variant`), `governance` (`state`, `data_classification`, `pii`,
`sox_critical`), `lineage[]` (`from_contract_id`, `from_version`,
`relation`, optional `note`), and `bindings[]`
(`target_contract_id`, `target_category`, `relation`, optional
mapping ref / `note`).

## 3. MC body — D329 constants mechanism

Live bc-core master-shape **permits** `variables[].items` to
carry these properties (`additionalProperties: false`, required
= `var_code, role, field_code`):

| Property | Type | Notes |
|---|---|---|
| `var_code` | string | required |
| `role` | enum | required; one of `input`/`output`/`constant` |
| `field_code` | string | required |
| `value` | number | optional; **D329** — numeric value; required when `role='constant'` unless `field_code` is a numeric literal |
| `description` | string | optional |

**D329 / DEC-4a8abb** decided end-to-end constant propagation
(seed → schema → DTO → service → quality gate). Today, live
state is partially fixed: the schema permits `value`, the
seed-side column `metric.metric_formula_variable.constant_value`
exists, the evaluator reads `variable.value` correctly, **but**:

- 332 currently-active MCs declare a constant variable without
  `value` in their body (321 use `constant_percentage_multiplier`,
  9 use `constant_days_in_period`, 2 use `constant_100`). They
  rely on a transitional TS-resident `KNOWN_CONSTANTS` map in
  `bc-core/src/registry/seed/d329-constants.ts` to resolve at
  evaluation time.
- 1,216 seeds carry `constant_value=NULL` on their constant
  variables. The D329-R2 CHECK declared in the ADR was never
  applied.

### Explicit rule for new promoted MC versions

> **For new promoted MC versions, constants must be persisted
> into `contract_json.body.variables[].value`. `KNOWN_CONSTANTS`
> may help resolve the value during authoring / backfill, but
> must not be the runtime source of truth.**

This rule is the slice (1) precedent and the path forward.
Replacement of the TS map with a governed master surface is
tracked separately at TSK-1f4988 (planned/later). Until that
work lands, the TS map remains in place to keep the 332 legacy
MCs functioning; new promotions write `value` into the body
directly and do not depend on it.

## 4. Header divergence from Foundation in live data

**Status: divergence recorded, no path chosen in this MWR.**

The 540 currently-active MC versions consistently deviate from
Foundation §Common Header in two ways:

- **`tags`.** Foundation: "array of slug strings. Classification
  tags." Live: variable codes, e.g. `["O1","I1","I2"]`.
- **`description`.** Foundation: "Contract purpose statement."
  Live: formulaic placeholders, e.g. `"Metric contract: O1 = (I1 / I2) * C1"`.

Two options for new promotions, **neither chosen here**:

- **(α) Match existing pattern.** Header carries the same
  divergences as the 540 precedents. Predictable for any
  tooling that has been reading these patterns. Carries forward
  a Foundation divergence.
- **(β) Match Foundation strictly.** `tags` = real classification
  slugs (e.g. `["ratio","accounts_receivable","percentage"]`);
  `description` = the seed's `description_text` as a real
  purpose statement. Diverges from 540 precedents but conforms
  to Foundation.

Future sessions: pick deliberately, not by inheritance from
live data. If a tooling-impact audit is warranted before
choosing, that audit is itself a small slice.

## 5. Lifecycle in live data

`contract.metric_contract_version.governance_state_code` CHECK
admits the five Foundation states: `draft`, `review`, `approved`,
`active`, `superseded`. Live data uses only three: `draft`
(289), `active` (729), `superseded` (2). **`review` and
`approved` are theoretical — zero rows across 1,020 versions.**

Slice (1) writes the new version directly to `active` after the
verification act passes. This is a **slice-local** decision
recorded in `2026-05-14-slice1-promotion-gate-plan-SES-594568.md`
§16. It does not amend Foundation's five-state lifecycle. A
future ADR may formalize a four- or three-state lifecycle if
the verification act is accepted as subsuming review/approved
in general.

## 6. Seed `status_code` is unused as a promotion signal

`metric.metric_definition.status_code` CHECK admits `draft`,
`active`, `deprecated`. Live state: **all 1,216 non-deprecated
seeds carry `draft`**, regardless of whether a contract has been
created from them. 778 of those `draft` seeds have a contract;
the seed-status field was never advanced.

**Future tooling rule:** to ask "is this metric promoted?", join
to `contract.metric_contract.metric_definition_id`. Do not read
`metric_definition.status_code` as a promotion signal — that
field is currently meaningless. Slice (1) is the first promotion
path that advances it; until the slice ladder closes and
remediation runs, the field remains untrustworthy for the
existing population.

The four-population breakdown of the 1,241-metric catalog is
documented in TSK-9ecaee (438 never-started, 289 stuck-mid-
promotion, 189 abandoned, 729 promoted-unverified, 3
promoted-verified, 25 deprecated).

## 7. D329-R2 CHECK never applied

ADR-4a8abb §D329-R2 declared:

```sql
CHECK ( (role='constant' AND constant_value IS NOT NULL)
     OR (role IN ('input','output') AND constant_value IS NULL) )
```

Live `metric.metric_formula_variable` has only the role-vocabulary
CHECK (`role ∈ {input, output, constant}`). The constant-value
CHECK is **not enforced**. This is why 1,216 seeds with
`constant_value=NULL` on constant roles can coexist with D329 as
documented.

Fold into TSK-1f4988 — the governed-registry work will revisit
whether this CHECK belongs at the seed layer, the body layer, or
both.

## 8. Seed thinness principle (operator decision 2026-05-14)

The seed catalog is **intentionally incomplete**. Seed rows
declare a metric's structure and intent; they do not always
encode every literal value required to make the body
self-contained. **Promotion is the formalization act** that
closes the gap — by authoring into the body, not by patching
the seed.

Concrete cases of seed thinness that promotion handles:

- NULL `constant_value` on a `role='constant'` variable —
  operator authors the literal into `body.variables[].value`.
- (Future slices may extend to NULL `field_name` on an input,
  etc. — not in scope for slice (1).)

Rules:

- Promotion **does not modify** seed rows.
- Operator-authored completions land in `contract_json.body`.
- Seed-side `metric_formula_variable.constant_value` may
  remain NULL throughout. The body becomes the self-contained
  artifact.

This preserves DEC-01df6b ("contract_json is authoritative") and
keeps the seed catalog declarative. Codified in slice (1) plan
§4.5.

## 9. Slice (1) precedent decisions (this session)

Recorded so future slices can adopt or deliberately deviate:

| Decision | What it locks in | Where recorded |
|---|---|---|
| Option 2 — deterministic-only verification | Pilot/proof tier below Q4's cross-family target. Lower trust ladder rung. | DBCP MWR (committed `f60523a`); slice plan §6.1 |
| `verdict_code='deterministic_passed'` | New CHECK value alongside `agree`/`reconciled`/`disputed`/`failed`. Honors "no fabrication" rule. | DBCP MWR; live in `metric.metric_formula_verification` |
| Body-authoring `variables[].value` per D329-R4 | Constants persisted in the body, not via TS map | Rule in §3 above |
| Direct-to-`active` lifecycle | Skip `review`/`approved` per §5 | Slice plan §16 |
| Failed verification writes nothing | No row at all on rejection (vs SDA-4's emit-on-failure pattern) | Slice plan §8, §11 |
| Seed thinness / promotion-time completion | §8 above | Slice plan §4.5 |
| Schema-name discipline | `metric.*` for formula/variable/binding; `contract.*` for metric_contract and metric_contract_version | Slice plan throughout |
| Body-key vocabulary unified to live master-shape | 9 keys: `input_type, formula, variables, co_bindings, temporal_gate, unit, direction_code, thresholds, grain` | Slice plan §4 |
| **Header path** | **Pending** — see §4 above | — |

## 10. Tracking tasks filed this session

| Task | Title | Status |
|---|---|---|
| TSK-9ecaee | Metric catalog population cleanup — 4 populations (438 never-started, 289 stuck-mid-promotion, 189 abandoned, 726 promoted-unverified) | planned/later |
| TSK-1f4988 | Replace KNOWN_CONSTANTS TS map with governed constant registry + versioned remediation of legacy MCs missing variables[].value | planned/later |

Both are bc-core project tasks, both held until the slice ladder
closes.

## 11. Anti-patterns to avoid in future sessions

### 11.0 SERVICES-ONLY DISCIPLINE (load-bearing)

**Before designing any DB write against `metric.*` or
`contract.*` tables, locate the official service that
mediates writes to that surface. Use it. Never raw-INSERT
behind it.**

Concretely:

- `*-onboarding.service.ts` files in `bc-core/src/registry/`
  are the canonical creation paths for each contract family
  (MC, CC, OC, SC, AC, IC). Look there first:
  - `mc-onboarding.service.ts` — Metric Contract creation
    (with `/onboarding/mc/preview` and `/onboarding/mc/create`,
    plus D329 version-bump on `/onboarding/mc/:mcId/versions/:versionCode`)
  - `cc-onboarding.service.ts` — Canonical Contract creation
  - `oc-onboarding.service.ts` — Observation Contract creation
  - `cm-onboarding.service.ts` — Canonical Mapping creation
  - `oagis-onboarding.service.ts` — OAGIS-driven onboarding
- These services run the family-specific quality gates
  (CR-QG-MC-001 has 14 checks for MC creation; equivalents
  exist for other families). Bypassing them produces
  contracts that pass DB constraints but fail the
  cross-cutting invariants.
- If the service doesn't yet do what you need (e.g. doesn't
  write to a related ledger, doesn't advance a seed status),
  the correct move is to **extend the service or compose a
  thin wrapper around it** — not to write raw INSERTs.

CLAUDE.md already states this rule ("Don't bulk-create data
via direct DB inserts — always use official API endpoints
with quality gates. No backdoor entry."). This anti-pattern
caught the slice (1) plan mid-session, where the plan was
designing an atomic 4-INSERT transaction while
`McOnboardingService` existed and was the right path. Slice
(0) (`2026-05-14-slice0-mc-onboarding-extension-plan-SES-594568.md`)
is the corrective work.

**Mental check before writing any DB-write plan against the
contract or metric schemas:**

1. Is there a `<family>-onboarding.service.ts` or similar?
2. If yes, what does its public DTO/result shape look like?
3. What quality gates does it run?
4. Does the gap I'm trying to fill live inside the service or
   in a wrapper around it?
5. If neither — *should* the service grow to cover this, or
   is a new wrapper service the right shape?

Only after answering these is it safe to plan code changes.

### 11.1 Other anti-patterns

- **Don't** read `legacy-v2/docs/system/foundation/contract-schemas/schemas/metric-v1.json` as authority. It is stale. Read the bc-core copy.
- **Don't** fabricate AI-agreement values (`agree`, `reconciled`) when the verification act is deterministic. The DBCP-added `deterministic_passed` is the honest verdict.
- **Don't** copy live MC patterns blindly when they diverge from Foundation. Header `tags` and `description` divergences are debt — and the source is
  `mc-onboarding.service.ts` lines 442–443 hardcoding the
  drifted values. Foundation-strict authoring requires either
  the slice (0) overrides or future further service work, not
  envelope hand-construction.
- **Don't** add fields to `body.variables[]` outside the 5 master-shape-permitted properties (`var_code`, `role`, `field_code`, `value`, `description`). `unit_type_code`, `sort_order`, and other seed-side richness do **not** belong in the body.
- **Don't** update seed rows during promotion. Promotion authors into the body; the seed is intentionally thin (§8).
- **Don't** treat `metric_definition.status_code` as a promotion signal — it is currently unused. Join to `contract.metric_contract` to ask "is this promoted?".
- **Don't** rely on `KNOWN_CONSTANTS` for new promoted MCs. New MCs persist `value` directly into the body (rule in §3).
- **Don't** assume `co_bindings: []` is a permitted state. The live master-shape enforces `minItems: 1`. Bindings are resolved by `McOnboardingService` from CC `field_selection` automatically; the caller does not author them. If a metric's variables don't map to any CC's `field_selection`, the service correctly rejects the promotion — that's the gate doing its job.

## 12. What is NOT in this MWR

- No ADR. None of these findings warrant ADR-class governance change today; they document live state plus operator decisions for slice (1).
- No DBCP. The single DBCP this session ran (`deterministic_passed`) is recorded in its own MWR (`2026-05-14-dbcp-verdict-code-extension-SES-594568.md`).
- No code change. This MWR records, it does not implement.
- No header decision. Pending future session (see §4).
- No slice (1) execution. Still gated on operator approval after header decision.

## 13. Cross-references

- Foundation: `bc-docs-v3/docs/foundation/the-contract-grammar.md` (envelope, header, body)
- Foundation: `bc-docs-v3/docs/foundation/the-invariants.md` (Invariant VI — evidence emitted, not inferred)
- ADR: `bc-docs-v3/docs/adrs/ADR-01419c.md` (DEC-01419c, D249 — MC body purity, 9 keys)
- ADR: `bc-docs-v3/docs/adrs/ADR-01df6b.md` (DEC-01df6b, D248 — catalog tables derived from contract_json)
- ADR (legacy v2): `legacy-v2/docs/decisions/ADR-4a8abb.md` (DEC-4a8abb, D329 — MC Constant Value Propagation End-to-End)
- Live master-shape: `bc-core/src/registry/meta-schemas/metric-v1.schema.json`
- Live evaluator constant resolution: `bc-core/src/boundary/metric-evaluation-engine.service.ts` (reads `variable.value`)
- Live transitional map: `bc-core/src/registry/seed/d329-constants.ts` (`KNOWN_CONSTANTS`)
- Calibration MWR (Q1–Q4 outcomes): `2026-05-14-pass1-calibration-q1-q4-SES-594568.md`
- Slice (1) plan: `2026-05-14-slice1-promotion-gate-plan-SES-594568.md`
- Slice (1) pre-flight result: `2026-05-14-slice1-preflight-result-SES-594568.md`
- DBCP execution: `2026-05-14-dbcp-verdict-code-extension-SES-594568.md`

---

**End of session findings.**
