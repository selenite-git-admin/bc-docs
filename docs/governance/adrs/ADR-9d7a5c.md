---
uid: DEC-9d7a5c
title: "OLS Failure Vocabulary — registry shape, namespace discipline, definitions-vs-occurrences split, seeded codes"
description: "Locks the failure-message ontology that pairs with the OLS framework: a registry table for code definitions (code, OLS state, severity, message_template, evidence_schema, remediation_hint, governing_decision) and a separate emission shape for occurrences ({code, evidence, observed_at, writer, subject_ref, source_probe}); two namespaces OLS-NN.* (state failures) and OPS.* (cross-cutting infra); seeds the initial vocabulary by re-keying existing in-code reason strings, chain_trace break_points, and Inspector reason_codes."
status: decided
date: 2026-05-03T01:48:15.592Z
project: bc-core
domain: governance
subdomain: failure-vocabulary
focus: failure-codes
---

# OLS Failure Vocabulary — registry shape, namespace discipline, definitions-vs-occurrences split, seeded codes

> **Renamed 2026-05-03 — OLS Failure Vocabulary → MLS Failure Vocabulary.** Code namespace migrates `OLS-NN.*` → `MLS-NN.*`. The body of this ADR retains the original "OLS" wording as historical record; future references use **MLS**. Companion to the framework rename in DEC-c9e623 (D389). Full details in the Errata section at the bottom of this file.

## Context

Failure messages today are scattered across chain_status.break_summary_json (8 of 828 rows non-empty, no reason_code populated despite ADR-bebaec naming it the carrier), chain_trace.break_point (L-codes only, no message), Inspector reason_codes (4 hand-coded strings), and dozens of NestJS exception strings in registry services. Each module invents its own vocabulary; nothing maps to OLS states; UI parsing is brittle. A unified vocabulary, locked to OLS state IDs, with a registry-vs-emission split, ends the drift.

## Context

Sibling to DEC-c9e623 (D389, OLS Framework). The framework defines the 25 numbered states and the architectural rules. This ADR defines the structured vocabulary that probes and gates use to emit failure information.

Scan of the current codebase + DB (2026-05-03) found:

| Surface | Format today | Coverage |
|---|---|---|
| `chain_status.break_summary_json` | `{"L4": 1}` link-counts only; `reason_code` documented but unpopulated | 8 of 828 rows non-empty |
| `chain_trace.break_point` | `L4`/`L5` strings | 8 of 1410 rows non-complete |
| `chain_trace.link_verdict` | `complete` / `partial`; `broken` enum value never used | — |
| `l_node_semantic_trace` | rich schema | **0 rows** — verifier never runs |
| `metric_contract.audit_status_code` | `pass`/`warn`/`fail` | code-only, no detail |
| Inspector reason_codes (in code) | `audit_log_unavailable`, `not_found`, `no_active_tenants`, `no_active_metric_contract` | 4 hand-coded strings |
| NestJS exceptions in registry | `BadRequestException("Business Object X not found")` | dozens of free-string throws |

Failure messages are nominally structured in 4 places, populated in 1 (Inspector partially), drift in 2, and absent everywhere else. This ADR locks one vocabulary that all surfaces emit from.

## Decisions

### D-1. Definitions live in a registry; occurrences are emitted separately

Two distinct shapes, two distinct lifecycles:

**Registry (definitions)** — table `metric.ols_failure_code`:

| Column | Example |
|---|---|
| `code` | `OLS-14.semantic_class_collapse` |
| `ols_state_id` | `OLS-14` (or NULL for `OPS.*` codes) |
| `signal_kind` | `probe-detected` / `activation-refused` / `runtime-thrown` |
| `severity` | `info` / `warn` / `blocker` |
| `message_template` | `"MC variables {var1} and {var2} resolve to identical signature {signature_hash}; no intentional_reuse_token registered."` |
| `evidence_schema` | `{ var1: string, var2: string, signature_hash: string, signature_components: object }` |
| `remediation_hint` | `"Differentiate the variables (filter, qualifier, time window, account) OR register an intentional_reuse_pattern token in metric.intentional_reuse_pattern."` |
| `governing_decision` | DEC-xxxxxx |
| `audit_surface` | Where occurrences of this code are durably written |

**Emission (occurrences)** — shape used everywhere a failure is recorded:

```
{
  code:          "OLS-14.semantic_class_collapse",
  evidence:      { ...matching evidence_schema... },
  observed_at:   ISO-8601,
  writer:        "metric.activation-gate.v1",
  subject_ref:   { kind: "metric_contract_version", id: "..." },
  source_probe:  "chain_trace.signature_hash"
}
```

Emissions are durably written to the `audit_surface` named on the registry row — for chain failures that surface is `chain_status.break_summary_json.reasons[]`; for inspection failures it is the Inspector response payload + `operations.platform_inspection_audit_log.result_state`; for gate refusals it is the (future) `metric_contract_version_activation_log`. The registry tells you where occurrences land for each code.

The registry never holds occurrence data; emissions never duplicate registry data (only `code` references it).

### D-2. Two namespaces — `OLS-NN.*` and `OPS.*`

- **`OLS-NN.snake_case`** — failures of one of the 25 numbered OLS states. The `NN` is the source of truth for which state the failure belongs to. Format `OLS-14.semantic_class_collapse` reads "the OLS-14 gate refused with reason `semantic_class_collapse`."
- **`OPS.snake_case`** — cross-cutting operational/infra failures that are not about an artifact's state. Examples: `OPS.inspection_audit_unavailable`, `OPS.attestation_unreachable`, `OPS.tenant_db_connection_failed`. These don't pollute the OLS namespace because they aren't OLS-row failures — they are infra failures that prevent OLS rows from being observed.
- No third namespace until `OPS.*` exceeds ~15 codes. Don't pre-split. If/when `AUTH.*` or `IO.*` carve-outs become needed, that's a future ADR.

Discipline: the namespace prefix is informative — a reader scanning a stack trace immediately knows whether they're looking at a ladder failure or platform-under-the-ladder failure.

### D-3. Seeded vocabulary — re-key existing strings only; no speculative codes

The registry seeds with codes already in use today, re-keyed to the namespaces. New codes are added when a real failure surfaces, not pre-emptively.

**Re-keyed from existing in-code strings:**

| Existing string / signal | Becomes | OLS state |
|---|---|---|
| Inspector `not_found` | `OLS-11.mc_version_not_found` | OLS-11 |
| Inspector `no_active_metric_contract` | `OLS-11.mc_version_not_active` | OLS-11 |
| Inspector `no_active_tenants` | `OLS-15.no_active_tenants` | OLS-15 |
| Inspector `audit_log_unavailable` | `OPS.inspection_audit_unavailable` | (cross-cutting) |
| chain_trace `break_point=L1` | `OLS-04.cf_not_registered` | OLS-04 |
| chain_trace `break_point=L2` | `OLS-09.cc_field_mapping_missing` | OLS-09 |
| chain_trace `break_point=L3` | `OLS-09.bf_not_in_resolved_schema` | OLS-09 |
| chain_trace `break_point=L4` | `OLS-07.bf_unmapped_in_oc` | OLS-07 |
| chain_trace `break_point=L5` | `OLS-06.ac_missing_for_source_table` | OLS-06 |
| chain_trace `break_point=L6` | `OLS-08.reader_not_bound_or_inactive` | OLS-08 |
| chain_trace `break_point=L7` | `OLS-02.source_field_not_in_catalog` | OLS-02 |
| Inspector `proof_status='degraded'` (D387) | `OLS-24.proof_degraded` | OLS-24 |

**Note on the OLS-13 vs OLS-14 discipline:** chain_status verdicts are structural and remain in the OLS-13 vocabulary (e.g., `OLS-13.chain_partial`, `OLS-13.chain_broken`). Semantic-collapse codes like `semantic_class_collapse` belong to `OLS-14.*` — chain status is structural; semantic refusal is the activation gate's job. This separation is locked by D-5 of DEC-c9e623 (probe-vs-gate) and is critical: a `chain_verdict='complete'` row may still trigger an OLS-14 refusal without contradicting the chain status.

### D-4. Migration of legacy fields — preserve `chain_trace.break_point` as coarse legacy field

The migration is non-disruptive:

- `chain_trace.break_point` stays as a coarse legacy field (single L-code string) for backward compatibility during the transition
- The new canonical carrier is `chain_status.break_summary_json.reasons[]` — array of structured occurrence objects per D-1
- ChainStatusService writes both during the transition; readers prefer `reasons[]` and fall back to `break_point` only for rows written before the migration
- A future ADR can retire `break_point` once all consumers read from `reasons[]`

Same pattern applies to NestJS exception strings: existing throws stay until touched. New throws at module boundaries must use coded exceptions per D-6 of DEC-c9e623.

### D-5. The cross-boundary code rule — operationalized

Per DEC-c9e623 D-6, cross-boundary failures must carry a stable code from this registry. This ADR adds the operational test:

- **Inside-module** raw exceptions with free-string messages remain acceptable (no overhead)
- **Cross-boundary** failures (controller→client, service→other-service, event emission, persisted audit row) must carry a code
- A `throw new BadRequestException("free string")` at a controller method that returns to a client is a violation
- Implementation pattern: a `CodedException` class accepts `(code, evidence)` and the response serializer pulls `message_template` from the registry to render the human message at the boundary
- ESLint rule (deferred) flags free-string throws in exported controllers/services; until then, code-review checklist item

## Consequences

**Positive:**
- One source of truth for every failure surface
- Probes write codes; renderers fetch templates; UI never parses prose
- Severity + remediation hint enable Inspector and bc-portal to show actionable rows instead of generic "Not activated"
- New failures land in known places (one registry row + one emission shape) — no new ad-hoc reason fields per module
- The `OLS-14.semantic_class_collapse` code becomes the canonical name for the MT-04971 specimen pattern; future audits run a single SQL query

**Negative:**
- All existing failure surfaces must migrate. The migration plan is "as touched, plus the three high-value ones now (chain_status, Inspector, registry exceptions)" — slow but bounded
- Free-string throws are common today; the rule will surface during code review for several sessions before reflex sets in
- Registry table is platform DB — cross-region replication and backup posture must include it (treat as governance-critical)

**Neutral:**
- The vocabulary grows organically from real failures, not from speculative completeness
- `OPS.*` namespace size is monitored; split deferred until needed

## Out of scope (separate decisions / tasks)

- Implementation of the registry table and the migration of existing surfaces — filed as a DevHub task, not landed in this ADR
- ESLint rule for free-string throws — future hygiene, not blocking
- The OLS-14 specific codes (`semantic_class_collapse`, `formula_primitive_unsupported`, etc.) — defined in the OLS-14 Semantic Activation Gate ADR, registered against this vocabulary
- Internationalization of `message_template` — out of scope; English-only initially; i18n is a presentation concern that can wrap the template later

## References

- DEC-c9e623 (D389) — MLS Framework (renamed from OLS — see DEC-c9e623 errata 2026-05-03) — defines the 25 states this vocabulary keys to
- DEC-bebaec (D305) — Chain Completeness SSOT — names `chain_status.break_summary_json.reason_code` as the carrier this ADR finally populates
- DEC-952faa (D386) — Metric Temporality Class & Inspector — motivates several new codes
- DEC-f0e78e (D388) — Inspector platform/tenant boundary — defines `state: 'broken' / reason_code: ...` shape that this ADR generalizes
- DEC-ebb3cd (D387) — Evidence and Lineage Write Semantics — defines `proof_status='degraded'` that becomes `MLS-24.proof_degraded`

## Errata

### 2026-05-03 — Renamed: OLS Failure Vocabulary → MLS Failure Vocabulary; code namespace migrates

In tandem with DEC-c9e623's framework rename (OLS → MLS), this ADR is renamed from **OLS Failure Vocabulary** to **MLS Failure Vocabulary**.

**Code namespace migrates.** All seeded codes in D-3 of this ADR keep their structure but the namespace prefix changes:

| Before | After |
|---|---|
| `OLS-11.mc_version_not_found` | `MLS-11.mc_version_not_found` |
| `OLS-11.mc_version_not_active` | `MLS-11.mc_version_not_active` |
| `OLS-15.no_active_tenants` | `MLS-15.no_active_tenants` |
| `OLS-04.cf_not_registered` | `MLS-04.cf_not_registered` |
| `OLS-09.cc_field_mapping_missing` | `MLS-09.cc_field_mapping_missing` |
| `OLS-09.bf_not_in_resolved_schema` | `MLS-09.bf_not_in_resolved_schema` |
| `OLS-07.bf_unmapped_in_oc` | `MLS-07.bf_unmapped_in_oc` |
| `OLS-06.ac_missing_for_source_table` | `MLS-06.ac_missing_for_source_table` |
| `OLS-08.reader_not_bound_or_inactive` | `MLS-08.reader_not_bound_or_inactive` |
| `OLS-02.source_field_not_in_catalog` | `MLS-02.source_field_not_in_catalog` |
| `OLS-24.proof_degraded` | `MLS-24.proof_degraded` |

**`OPS.*` namespace is unchanged** — cross-cutting infra failures keep their existing prefix. Same with `OPS.inspection_audit_unavailable` (which was the rekey of Inspector's `audit_log_unavailable`).

**D-2 namespace discipline updates.** Two namespaces:
- **`MLS-NN.snake_case`** — failures of one of the 25 numbered MLS states
- **`OPS.snake_case`** — cross-cutting operational/infra failures (unchanged)

**Body of this ADR retains the original "OLS" wording** as the historical record. Future references use MLS. Migration of any existing populated occurrences (currently zero outside Inspector's hand-coded strings) becomes part of the implementation task that seeds the registry — registry is seeded with MLS-NN.* codes from the start; no production data migration needed.

**Cross-references updated:** future ADRs and code reference this as the MLS Failure Vocabulary; the file path and DEC UID stay stable.
