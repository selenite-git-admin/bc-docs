---
uid: DEC-b8b825
title: "OLS-14 Semantic Activation Gate — refusal rules, signature-hash comparison, intentional reuse pattern, MT-04971 specimen"
description: "Locks the semantic activation gate for OLS-14: within one MC formula, two distinct variables MUST NOT resolve to an identical semantic signature unless explicitly declared as intentional reuse via a registered token. Defines the deterministic signature_hash computation, the metric.intentional_reuse_pattern registry table, the gate's emission codes, and records mc__ar_staff_productivity (MT-04971) as the canonical drift specimen."
status: decided
date: 2026-05-03T01:49:45.469Z
project: bc-core
domain: metrics
subdomain: metric-runtime
focus: activation-gate
---

# OLS-14 Semantic Activation Gate — refusal rules, signature-hash comparison, intentional reuse pattern, MT-04971 specimen

> **Renamed 2026-05-03 — OLS-14 Semantic Activation Gate → MLS-14 Semantic Activation Gate.** Emission codes migrate accordingly. The body of this ADR retains the original "OLS" wording as historical record; future references use **MLS-14**. Companion to the framework rename in DEC-c9e623 (D389). Full details in the Errata section at the bottom of this file. Implementation: `Mls14ActivationGate` + `Mls14SignatureHashService` in `bc-core/src/mls/gate/`.

## Context

Specimen MT-04971 (mc__ar_staff_productivity v1.0.0) shipped with chain_status='complete' and metric_contract_version.governance_state_code='active' despite both formula variables resolving to the same source field WRBTR @ BSID. The formula collapses to SUM(WRBTR)/SUM(WRBTR)=1.0 — semantic noise the platform has no representation for. Chain status is structural; semantic refusal needs its own gate. OLS-14 is the only place the framework permits to refuse the draft→active transition on this rule (per DEC-c9e623 D-5 probe-vs-gate separation).

## Context

Sibling to DEC-c9e623 (D389, OLS Framework) and DEC-9d7a5c (D390, Failure Vocabulary). The framework defined OLS-14 as "Platform semantic activation gate" but left the refusal rules unspecified. This ADR locks them.

The motivating specimen, walked end-to-end during SES-c37208:

**`mc__ar_staff_productivity` v1.0.0 (MT-04971)** — Platform OLS row data:

- `metric_contract_version.governance_state_code = 'active'` (set without a gate)
- `metric_contract_version.last_validated_at = NULL` (formula audit never written at version level)
- `metric_definition.temporality_kind = NULL` (D386 Stage 1 backfill never ran)
- `metric_definition.status_code = 'draft'` (parent in draft, child version in active — incoherent)
- `chain_status.chain_verdict = 'complete'`, `variables_complete=2/2`, `grain_complete=true`, `has_live_source=true`
- `l_node_semantic_trace`: 0 rows for this MC (writer doesn't exist)
- `chain_trace` for both variables:

| Variable | l2_bf_name | l4_source_field | l4_source_table | l4_oc_id | l5_ac_id | l6_reader_id |
|---|---|---|---|---|---|---|
| `total_ar_volume_processed` (I1) | `receivable_hdr_amount` | `WRBTR` | `BSID` | 019d79e1… | 019d6238… | 019d867d… |
| `number_of_ar_staff` (I2) | `receivable_hdr_amount` | `WRBTR` | `BSID` | 019d79e1… | 019d6238… | 019d867d… |

Identical signatures across both variables. Formula `O1 = SUM(I1) / SUM(I2)` reduces to `SUM(WRBTR) / SUM(WRBTR) = 1.0` for every grain bucket. Every existing probe (ChainStatusService, Inspector, IntegrityService) returns green. Only a human reading the metric name and the resolved fields side-by-side catches it. This is the funnel-padding pattern from `feedback_funnel_padding.md` made flesh.

## Decisions

### D-1. The semantic-collapse refusal rule

> **Within one MC formula, two distinct formula variables MUST NOT resolve to an identical semantic signature unless explicitly declared as intentional reuse via a registered `intentional_reuse_token`.**

Where **semantic signature** is the deterministic hash over the following components, computed per (MC version, variable):

| Component | Source |
|---|---|
| canonical_field code | MC variable's `field_code` |
| business_field code | resolved BF (chain_trace `l2_bf_name`) |
| source_table | chain_trace `l4_source_table` |
| source_field | chain_trace `l4_source_field` |
| source filter / qualifier | OC body's filter/qualifier for this BF (if present); empty string otherwise |
| grain role | role of this variable in the MC's grain (output / input / grain-key) |
| time window | MC's temporal_gate field_code + window_size, or empty string if instantaneous |

The hash is SHA-256 over the canonical JSON encoding (RFC 8785 JCS) of these seven fields. Stored on each `chain_trace` row in a new column `signature_hash` (added by the implementation task).

**Refusal logic** — the gate runs at MC authoring AND at the `governance_state_code → active` transition (D386's two-gate rule). Pseudocode:

```
SELECT signature_hash, ARRAY_AGG(variable_field_code) AS vars
FROM chain_trace
WHERE metric_contract_id = $1
  AND metric_version_code = $2
  AND intentional_reuse_token IS NULL
GROUP BY signature_hash
HAVING COUNT(*) > 1
```

If any row returns, the gate refuses with code `OLS-14.semantic_class_collapse` (per DEC-9d7a5c) and evidence `{ var1, var2, signature_hash, signature_components }`.

### D-2. The `intentional_reuse_pattern` registry

New platform table `metric.intentional_reuse_pattern`:

| Column | Purpose |
|---|---|
| `pattern_code` | Stable identifier (e.g., `range_max_minus_min`, `quartile_split`, `period_over_period`, `ratio_to_self_baseline`) |
| `display_name` | Human label |
| `description` | What the pattern means and when it is appropriate |
| `expected_signature_collapse_shape` | Description of the expected collapse pattern (e.g., "two vars same signature differ only by aggregation primitive") |
| `governance_state_code` | `draft` / `active` / `retired` |
| `governing_decision` | DEC-xxxxxx that introduced or validated the pattern |
| `created_at`, `created_by_name`, `updated_at`, `updated_by_name` | audit |

Initial seeded patterns (created with this ADR's implementation task; **not** added by this ADR):

- `range_max_minus_min` — two vars same signature, formula uses MAX and MIN to derive a range
- `period_over_period` — two vars same signature, time window differs (already captured in signature, but a token affirms intent)
- `ratio_to_self_baseline` — explicit ratio of a value to its own baseline (rare, requires justification in the registration)

The MC contract body schema gains `co_bindings[].intentional_reuse_token` (optional string). The token must reference a `pattern_code` whose `governance_state_code='active'`. Unknown or retired tokens fail the gate the same as no token.

### D-3. Codes the gate emits — registered against DEC-9d7a5c

All codes follow the OLS-NN.snake_case convention. All are severity `blocker`, signal_kind `activation-refused`. Audit surface is the (future) `metric_contract_version_activation_log`.

| Code | Trigger | Evidence |
|---|---|---|
| `OLS-14.semantic_class_collapse` | ≥2 variables share signature_hash without intentional_reuse_token | `{ var1, var2, signature_hash, signature_components }` |
| `OLS-14.formula_primitive_unsupported` | formula primitive ∉ engine.implemented_primitives | `{ primitive, formula_text, implemented_primitives }` |
| `OLS-14.temporality_kind_missing` | `metric_definition.temporality_kind IS NULL` | `{ metric_definition_id }` |
| `OLS-14.temporality_class_mismatch` | temporality_kind ↔ formula primitive incompatible per DEC-952faa D-2 | `{ temporality_kind, primitive, allowed_primitives }` |
| `OLS-14.formula_audit_not_run` | `metric_contract_version.last_validated_at IS NULL` | `{ metric_contract_id, version_code }` |
| `OLS-14.formula_audit_failed` | last_validated_at present AND success_score below threshold | `{ success_score, threshold, last_validated_at }` |
| `OLS-14.chain_not_complete` | upstream `chain_status.chain_verdict ≠ 'complete'` | `{ chain_verdict, break_summary_json }` |
| `OLS-14.unknown_intentional_reuse_token` | token references unknown or retired pattern_code | `{ token, var_code }` |

The gate may emit multiple codes for one refusal — operators see the full list, not just the first. Activation is permitted only when zero codes fire.

### D-4. OLS-14 is the sole refusal authority on these rules

Per DEC-c9e623 D-5 (probe-vs-gate separation):

- L-node verifier may **probe** for semantic collapse and report the verdict
- Inspector may **render** the verdict in its Semantic Checks section
- ChainStatusService may **read** signature_hash and surface collapse counts
- **Only OLS-14's Activation Service may refuse `governance_state_code → active`** based on these codes

A probe that returns a "semantic collapse detected" verdict is a signal. The transition refusal is OLS-14's exclusive write authority. No other service may block on this rule. This separation is the architectural invariant; codifying the codes here without codifying the authority would re-introduce the muddle this framework was created to fix.

### D-5. Re-evaluation of currently-`'active'` MCs

When the implementation task lands, all extant MC versions with `governance_state_code='active'` are re-evaluated against the new gate. Versions that fail are downgraded to `'draft'`. Their `chain_status.break_summary_json.reasons[]` records the codes that fired. A followup task surfaces the downgrade list to operators with the remediation hints.

MT-04971 is the first known specimen that fails. There are likely others — the funnel-padding feedback memory cites "81 CFs = 1 NETWR sum" from prior incidents, indicating the pattern is widespread. The re-evaluation will produce the precise count. This is the platform telling the truth, not a regression.

### D-6. The L-node semantic trace writer is a precondition

The gate's signature_hash logic reads `chain_trace`. Today `contract.l_node_semantic_trace` exists with rich schema but has 0 rows. The verifier (D366) was scaffolded but never runs. Without it, the gate has nothing to read for the more nuanced semantic checks (the basic signature_hash check can run from `chain_trace` alone, but per-variable semantic verdicts need the trace populated).

Implementation sequencing:

1. **First** — L-node semantic trace writer + backfill (separate DevHub task)
2. **Then** — OLS-14 gate implementation (this ADR's task) — depends on (1)

The dependency is recorded on the implementation task. Without (1), the gate ships in degraded mode (basic signature_hash only); with (1), the gate has full signal coverage.

## Consequences

**Positive:**
- The funnel-padding pattern stops being invisible — it has a name, a code, a refusal, and a registered escape hatch
- MT-04971 and any other tautological MCs become discoverable in one SQL query
- Authors that need legitimate signature reuse have a structured path (register a pattern, declare the token) instead of either silently shipping bad metrics or working around the gate
- OLS-14 fills the missing primitive at the framework's most important seam — the platform/tenant handoff

**Negative:**
- Some currently-`'active'` MCs will be downgraded. This is correct but disruptive — the followup task to surface the downgrade list to operators is non-optional
- The `intentional_reuse_pattern` table will accumulate patterns that turn out to be misuse over time. Each pattern row is a governance act; pruning is a separate workflow
- The signature_hash includes "source filter / qualifier" which is hard to extract from current OC bodies. Initial implementation may approximate (empty string when not extractable); ADR is explicit this is a known weakness that tightens over time

**Neutral:**
- The gate runs at two boundaries (authoring + activation) per D386 D-3. This catches both new MCs at creation and existing MCs whose `governance_state_code` was set without a gate
- The gate is read-only on chain_trace and metric tables — it does not modify anything except `governance_state_code` (and the audit log). Re-running the gate is idempotent

## Out of scope (separate ADRs / tasks)

- Activation Services for other OLS rows (OLS-10 temporality_kind backfill, OLS-12 formula audit, OLS-19 contract_binding lifecycle) — separate gates, separate ADRs
- Internationalization or per-tenant rephrasing of refusal messages — DEC-9d7a5c keeps templates English-only
- Automatic suggestions for differentiation when collapse is detected — pure heuristic territory; out of scope for the gate, fits in a future operator-assistance feature
- Bulk pattern-token registration during the re-evaluation pass — operators must register tokens one at a time so each is a deliberate governance act

## References

- DEC-c9e623 (D389) — MLS Framework (renamed from OLS — see DEC-c9e623 errata 2026-05-03) — defines MLS-14 as a state and probe-vs-gate as the invariant this ADR enforces
- DEC-9d7a5c (D390) — MLS Failure Vocabulary (renamed from OLS — see DEC-9d7a5c errata 2026-05-03) — registers the codes this gate emits
- DEC-952faa (D386) — Metric Temporality Class & Inspector — D-2/D-3 two-gate rule that MLS-14 inherits; D-1 temporality_kind axis whose absence triggers `MLS-14.temporality_kind_missing`
- DEC-bebaec (D305) — Chain Completeness SSOT — defines `chain_trace` that this gate reads from
- DEC-804874 (D366) — L-Node Semantic Gate — the writer dependency for full signal coverage
- TSK-bdb5be — D386 Stage 3 catalog backfill (parked) — when activated, surfaces MCs whose temporality_kind is unset and they will fail this gate too
- `feedback_funnel_padding.md` — origin of the rule; this ADR graduates the feedback into a structural refusal
- Specimen: `mc__ar_staff_productivity` v1.0.0 (metric_contract_id `019d762a-1c66-7da0-a14d-63e93740c103`)

## Errata

### 2026-05-03 — Renamed: OLS-14 Semantic Activation Gate → MLS-14 Semantic Activation Gate; emission codes migrate

In tandem with DEC-c9e623's framework rename (OLS → MLS) and DEC-9d7a5c's vocabulary rename, this ADR is renamed from **OLS-14 Semantic Activation Gate** to **MLS-14 Semantic Activation Gate**.

**Emission codes migrate** under the MLS-14.* namespace:

| Before | After |
|---|---|
| `OLS-14.semantic_class_collapse` | `MLS-14.semantic_class_collapse` |
| `OLS-14.formula_primitive_unsupported` | `MLS-14.formula_primitive_unsupported` |
| `OLS-14.temporality_kind_missing` | `MLS-14.temporality_kind_missing` |
| `OLS-14.temporality_class_mismatch` | `MLS-14.temporality_class_mismatch` |
| `OLS-14.formula_audit_not_run` | `MLS-14.formula_audit_not_run` |
| `OLS-14.formula_audit_failed` | `MLS-14.formula_audit_failed` |
| `OLS-14.chain_not_complete` | `MLS-14.chain_not_complete` |
| `OLS-14.unknown_intentional_reuse_token` | `MLS-14.unknown_intentional_reuse_token` |

**The signature_hash rule, intentional_reuse_pattern table, two-gate enforcement, MT-04971 specimen, and probe-vs-gate authority assignment are all unchanged.** Only the framework/code naming migrates from OLS to MLS.

**Body of this ADR retains the original "OLS-14" wording** as the historical record. Future references use MLS-14. The implementation task (TSK-3c08cf, filed under SES-c37208) inherits the rename: the gate emits `MLS-14.*` codes from the start, not `OLS-14.*`.

**Cross-references stable.** TSK-f85cee (L-node writer), TSK-3c08cf (gate impl), TSK-4bb6e5 (failure-surface migration) keep their UIDs; their tag set updates from `ols-*` to `mls-*` at first edit.

### 2026-05-04 — Clarification: signature_hash inputs (D-1)

ADR-b8b825 D-1 specified seven hash components, the first listed as "canonical_field code | MC variable's `field_code`". Read literally during Phase 1 implementation (SES-7e37a8), this prevented the gate from firing on its motivating specimen MT-04971: each variable carries a unique `variable_field_code` and the two variables also bind to **different** canonical fields, so the hash would never collide even though both CFs resolve to the same business_field and the same `WRBTR @ BSID`.

**Clarification:** `signature_hash` is computed over the resolved-chain signature only:

  `(business_field, source_table, source_field, source_filter, grain_role, time_window)`

It MUST NOT include the MC variable's local field code or the bound canonical_field code, because those identifiers can differ while the resolved semantic/source path has collapsed. Variable field code and canonical field code MAY be recorded as evidence on the refusal payload (`MLS-14.semantic_class_collapse` evidence) for operator review.

**Why:** the activation gate's job is to detect resolved-chain collapse, not variable-name uniqueness or CF-label uniqueness. Including the variable or CF identifiers in the hash defeats the gate against the very pattern it was designed to catch (MT-04971 and the funnel-padding family).

**Scope:** clarification only. The signature_hash rule (D-1), intentional_reuse_pattern table (D-2), emission codes (D-3), authority assignment (D-4), re-evaluation pass (D-5), and L-node writer dependency (D-6) are all unchanged.

**Implementation reference:** Mls14SignatureHashService in bc-core (under `src/mls/gate/`).
