---
uid: DEC-c9e623
title: "BareCount Object Life States — framework, state ledger schema, probe-vs-gate separation, cross-boundary code rule"
description: "Locks the 25-step Object Life States (OLS) framework as the canonical sequence from connector existence to tenant KPI surface; splits Platform OLS (1-14) from Tenant OLS (15-25); defines the 17-column state ledger schema (incl. Activation/Probe/Self-Declaration triplet); locks two architectural invariants — probe-vs-gate separation and cross-boundary code rule."
status: decided
date: 2026-05-03T01:46:52.889Z
project: bc-core
domain: governance
subdomain: metric-lifecycle-states
focus: framework
---

# BareCount Object Life States — framework, state ledger schema, probe-vs-gate separation, cross-boundary code rule

> **Renamed 2026-05-03 — Object Life States (OLS) → Metric Lifecycle States (MLS).** The body of this ADR retains the original "OLS" wording as historical record of what was filed; future references in code, ADRs, and conversation use **MLS**. Sibling errata in DEC-9d7a5c (D390) and DEC-b8b825 (D391). Full details in the Errata section at the bottom of this file. Substrate ADR: DEC-e7b7b3 (D392).

## Context

Many prior approaches (IntegrityService, ChainStatusService, Readiness ledger, L-node verifier, Inspector, tenant.contract_binding) each told a partial truth about metric activation; none was the activation primitive. The platform lacked a canonical sequence describing what must be true for a tenant to see a KPI, and lacked a clean separation between read services (probes) and write services (gates). OLS supplies both: an ordered ladder of 25 named states, and the rule that exactly one Activation Service per state is permitted to refuse a transition.

## Context

A long arc of work on metric activation produced six overlapping and partially-conflicting approaches:

- **IntegrityService** — deprecated, still imported in test-bench and integrity flows
- **ChainStatusService** — D305 SSOT, returns `chain_verdict` per MC version
- **Readiness ledger + mc_dependency** — D316, runtime-readiness scheduler
- **L-node verifier** — D366, semantic verdict gate at session close
- **Inspector** — D386/D388, read-only audit surface at `/api/admin/inspection/*`
- **`tenant.contract_binding`** — tenancy table, decoupled from runtime evaluation (TSK-e6ffdc)

Each was a probe over a different slice. None was the activation primitive. The schema-level evidence: `governance_state_code` exists on all 7 contract version tables (SC, AC, OC, CC, CM, MC, AI) as a free string with no transition gate; `metric.metric_definition.temporality_kind` exists in DDL but is NULL on all rows and missing from Drizzle; `contract.l_node_semantic_trace` exists as a table but has 0 rows.

Specimen `mc__ar_staff_productivity` v1.0.0 (MT-04971) makes the gap concrete: BOTH formula variables `total_ar_volume_processed` and `number_of_ar_staff` resolve via `chain_trace` to the same source field WRBTR @ BSID through the same OC, AC, and Reader. Formula `O1 = SUM(I1)/SUM(I2)` collapses to `SUM(WRBTR)/SUM(WRBTR) = 1.0` for every grain bucket. `chain_status.chain_verdict='complete'`. `metric_contract_version.governance_state_code='active'`. No probe flags it. The bc-portal shows it as "Not activated for any tenant" because `tenant.contract_binding` is empty for it, while `tbc_sandbox1_dev` already holds 1 metric_evaluation + 15 metric_snapshot_index rows.

This decision lays the canonical ladder, the per-state ledger schema, and the architectural rules that prevent this kind of muddle from recurring.

## Decisions

### D-1. The framework is named "BareCount Object Life States"

- Proper-noun name: **BareCount Object Life States** (acronym: OLS)
- Lowercase generic: *object state* — the value at one OLS position
- Each state has a stable code: `OLS-NN` where NN is `01`–`25`
- "Stage" is on the platform's forbidden vocabulary list; OLS uses "state" exclusively
- Naming covers both authoring/governance states (Platform OLS) and runtime states (Tenant OLS); they are one ladder, two halves

### D-2. The 25 numbered states (Platform OLS 01-14, Tenant OLS 15-25)

**Platform side — runs once per MC version, tenant-agnostic:**

| ID | State | Description |
|---|---|---|
| OLS-01 | Connector exists | Source-system connector/runtime capability is supported |
| OLS-02 | Source catalog populated | Source system/table/field rows exist for the metric's source |
| OLS-03 | BO + BFs authored | Business object + business fields exist for the metric's domain |
| OLS-04 | Canonical fields seeded | CFs the formula targets exist in the canonical_field registry |
| OLS-05 | SC active | Source contract version locked at `governance_state_code='active'` |
| OLS-06 | AC active | Admission contract version active for the source table |
| OLS-07 | OC active | Observation contract version active with field map BF→source |
| OLS-08 | Reader flavor active | Runtime reader flavor authored and bound to OC |
| OLS-09 | CC active | Canonical contract version active with cc_field_mapping CF→BF and posting_date_field where needed |
| OLS-10 | MD authored with temporality_kind | Metric definition exists with temporality_kind set + 5D classification |
| OLS-11 | MC authored | Metric contract version exists with formula, grain, thresholds, temporal gate |
| OLS-12 | Formula/audit support established | Formula primitive in engine.implemented_primitives + version-level audit verdict recorded |
| OLS-13 | Chain status complete | `contract.chain_status.chain_verdict='complete'` per D305 |
| OLS-14 | Platform semantic activation gate | Eligibility gate that may flip `metric_contract_version.governance_state_code` to `'active'` |

**Tenant side — runs per (tenant, MC version):**

| ID | State | Description |
|---|---|---|
| OLS-15 | Tenant exists/active | Row in `tenant.tenants` (active) + tenant DB provisioned |
| OLS-16 | Tenant fiscal calendar | `tenant.fiscal_calendar_config` per legal_entity (D364) |
| OLS-17 | Tenant connector instance | Tenant has credentials/endpoint for the source system |
| OLS-18 | Tenant reader configured | Reader flavor bound to connector instance with execution config |
| OLS-19 | Tenant contract bindings recorded | `tenant.contract_binding` rows pin the active SC/AC/OC/CC/MC versions for this tenant |
| OLS-20 | Tenant fact tables exist | `fact.so_*`, `fact.co_*`, `fact.ms_*` tables exist per binding (schema-provisioner reconciled) |
| OLS-21 | SO produced | Reader execution → `progression.admission` + `fact.so_*` |
| OLS-22 | CO produced | Canonical evaluation → `progression.canonical_evaluation` + `fact.co_*` |
| OLS-23 | Metric snapshot produced | Metric evaluation → `progression.metric_evaluation` + `progression.metric_snapshot_index` + `fact.ms_*` |
| OLS-24 | Snapshot proof complete | Evidence + lineage writes succeeded; D387 `proof_status='complete'` |
| OLS-25 | KPI rendered in bc-portal | Snapshot index row exists, typed value row present, tenant binding/permission checks pass |

The handoff between halves is OLS-14 → OLS-15. **Tenant OLS for an MC cannot enter OLS-15 until that MC's Platform OLS row at OLS-14 is `'active'`.** This is the gate that makes "platform activation" mean something to the tenant side.

### D-3. State ledger — 17-column schema per state

Each OLS row carries the following columns:

| # | Column | Purpose |
|---|---|---|
| 1 | State ID | Stable code (`OLS-01` … `OLS-25`) |
| 2 | State Name | Human label |
| 3 | Description | What "being in this state" means |
| 4 | Boundary | platform-side / tenant-side / both |
| 5 | Input | Upstream State ID(s) whose Output feeds this one |
| 6 | Process | Action that produces the Output |
| 7 | Output | Artifact/condition produced |
| 8 | Success Signal | How we know we are in (row presence, service 200, computed verdict) |
| 9 | Failure Signal | How we know we are rejected (distinct from "we don't know yet") |
| 10 | Activation Service | Who writes the transition (sole write authority for this state) |
| 11 | Probe Service | Who reads the verdict (read-only) |
| 12 | Self Declaration Service | Service letting the subject assert "I am in state X" (where applicable; mostly N/A on platform side, load-bearing on tenant side) |
| 13 | Audit Surface | Where this state's history is durable |
| 14 | Governing Decision | DEC-xxxxxx that locks this state's contract |
| 15 | Implementation Status | durable / partial / missing / drift |
| 16 | Blocking Tasks | TSK-xxx that must close to make it durable |
| 17 | Owner Role | Platform team / Tenant operator / Engineering |

Keying:
- **Platform OLS rows:** keyed by `(mc_version_id, state_id)` — one row per MC version per state
- **Tenant OLS rows:** keyed by `(tenant_slug, mc_version_id, state_id)` — tenant_slug is the per-tenant differentiator

Cardinality:
- Platform OLS rows are state-row (latest verdict overwrites)
- Tenant OLS runtime rows (OLS-21 through OLS-23) are naturally state-event (one per evaluation cycle); the table holds the latest verdict, full event history sits in a sibling `_event` table

### D-4. L-nodes are not separate states — they are Probe Service implementations

The L1-L7 chain (D305 / DEC-bebaec) does not introduce new states. Each L-node is the per-variable probe primitive that feeds the verdict for a Platform OLS row:

| L-node | What it checks | Probe for OLS row |
|---|---|---|
| L1 | CF registered for the variable | OLS-04 |
| L2 | CF→BF mapped in CC's `cc_field_mapping` | OLS-09 |
| L3 | BF in CC's `resolved_schema` (exact match) | OLS-09 |
| L4 | BF→source mapped in OC's `observation_field_map` | OLS-07 |
| L5 | AC active for the source table feeding L4 | OLS-06 |
| L6 | Reader bound + governance-active on OC | OLS-08 |
| L7 | Source field in Source Catalog | OLS-02 |
| C1–C5 | Per-contract checks | Probes for the contract-state OLS rows (5, 6, 7, 9, 11) |
| E1–E3 | End-to-end roll-up | Probe for OLS-13 |

The probe service for an OLS row does the AND across all variables internally (L-nodes are per-variable; OLS rows are per-MC). Per-variable detail remains in `chain_trace`. The OLS row's verdict is the rollup.

D366's L-Node Semantic Gate is **not a state and not a probe** — it is an **audit gate** on `session_close` that consumes L-node semantic verdicts. It sits in the Audit Surface column, not as a state.

### D-5. Architectural invariant — probe-vs-gate separation

> **Probes report verdicts. Gates refuse transitions. No probe may block; no gate may probe.**

Stated formally:

- A **probe** (Probe Service column) is a read-only service that observes the current value of an OLS row's success/failure signal and returns a verdict. Probes never write state.
- A **gate** (Activation Service column) is the sole write authority for an OLS row. Gates may consume probe outputs to decide whether to permit a state transition. The gate is the only surface allowed to refuse.
- An OLS row has at most one Activation Service. It may have multiple Probe Services (different surfaces reading different signals); none of them is allowed to block.

Consequence: services like Inspector, ChainStatusService, L-node verifier all become probes. `governance_state_code` transitions go through their per-OLS Activation Service exclusively. There is no "probe that also blocks" anywhere in the framework.

### D-6. Architectural invariant — cross-boundary code rule

> **Cross-boundary failures MUST carry a stable code from the OLS Failure Registry. Human messages are derived from the code's `message_template` at presentation time — never authored at the throw site.**

Operational consequence:

- Inside one module, raw exceptions with free-string messages remain acceptable
- Any failure that crosses a service boundary (controller→client, service→other-service, event emission) must carry a code from the registry
- `throw new XException("free string")` patterns at module boundaries are a violation
- Lintable in future via an ESLint rule that flags free-string throws in exported controllers/services
- Until then, this is a code-review checklist item with a clear test

The OLS Failure Vocabulary ADR (sibling to this one) defines the registry shape, namespaces, and seeded codes.

## Consequences

**Positive:**
- Single canonical sequence for "what must be true for a tenant to see a KPI" — disagreements about activation reduce to disagreements about which OLS row a signal belongs to
- Clear ownership per state (Activation Service column) — no more "everyone is a probe and no one is the activator"
- L-nodes get a clean role (probe primitives), not a parallel framework
- Inspector retains its role as the read surface across all 25 states; the muddle was role overload, not the surface itself
- New gates land in known places (the Activation Service column for the relevant OLS row), not as ad-hoc services

**Negative:**
- Existing `governance_state_code` rows will need re-validation against per-OLS gates as gates land — some currently-`'active'` rows may have been activated without their preconditions holding (MT-04971 is one such row)
- The 17-column schema is heavy. Some columns (Self Declaration Service for platform states) are intentionally N/A; resist filling them with placeholders
- Three ADRs landing in one session (this one + Failure Vocabulary + OLS-14 Gate) is a lot of governance at once; the alternative is incoherence between them, which is worse

**Neutral:**
- This ADR locks shape, not implementation. The state ledger may live as documentation in a v3 chapter first, become a real platform table later when probe-write coverage warrants. No DB changes from this ADR alone.

## Out of scope (separate decisions)

- The OLS Failure Vocabulary (registry shape, namespaces, seeded codes) — sibling ADR
- The OLS-14 Semantic Activation Gate (signature_hash rule, intentional_reuse_pattern, MT-04971 specimen) — sibling ADR
- Promotion of the state ledger from prose chapter to a real platform table — future ADR when probe-write coverage warrants
- Per-state implementation tasks for Activation Services that don't yet exist (OLS-10, OLS-12, OLS-14, OLS-19) — filed as DevHub tasks, not ADRs

## References

- DEC-bebaec (D305) — Chain Completeness SSOT — defines L1-L7, C1-C5, E1-E3 that this framework re-keys as Probe Service implementations
- DEC-952faa (D386) — Metric Temporality Class & Inspector — motivates OLS-10 and OLS-14
- DEC-f0e78e (D388) — Platform/tenant authority boundary — defines the Inspector that becomes the read surface for OLS rows
- DEC-804874 (D366) — L-Node Semantic Gate — re-framed as audit gate, not as state
- DEC-d316mr (D316) — Readiness scheduler — re-framed as Probe Service for OLS-19/20
- TSK-e6ffdc — runtime rows without contract_binding (the MLS-19 inconsistency this framework makes legible)
- TSK-bdb5be — D386 Stage 3 catalog backfill (MLS-10 implementation precondition)
- `feedback_funnel_padding.md` — origin of the MLS-14 semantic-collapse rule
- `feedback_zero_claims_policy.md` — same family of discipline (no claim without first-hand proof)

## Errata

### 2026-05-03 — Renamed: Object Life States → Metric Lifecycle States (OLS → MLS)

The framework is renamed from **Object Life States (OLS)** to **Metric Lifecycle States (MLS)**, effective 2026-05-03. Founder ruling during SES-5f806e while designing the bc-admin surface placement.

**Why the rename.** The framework was originally named "Object" because the BareCount platform vocabulary uses Object (BO/SO/CO/AO). On reflection during surface design, this generalization was a hedge, not a fit — the framework does not describe BO/SO/CO/AO lifecycles directly; it describes the lifecycle from concept to live KPI. All 25 states are eventually about getting a metric live for a tenant, including infrastructure-side states (MLS-01 connector, MLS-02 source catalog) which are preconditions for some metric. The bc-admin surface that consumes this framework is "Metric Lifecycle" (folded into Metric Chain — see surface-placement decision in SES-5f806e). Naming the engine MLS so it matches the surface eliminates avoidable vocabulary drift.

**What changes.**

| Surface | Before | After |
|---|---|---|
| Framework name (proper noun) | Object Life States | Metric Lifecycle States |
| Acronym | OLS | MLS |
| State IDs | `OLS-01` … `OLS-25` | `MLS-01` … `MLS-25` |
| Lowercase generic | "object state" | "metric state" |
| Failure code namespace | `OLS-NN.snake_case` | `MLS-NN.snake_case` (per DEC-9d7a5c errata) |
| Activation gate ADR | OLS-14 Semantic Activation Gate | MLS-14 Semantic Activation Gate (per DEC-b8b825 errata) |
| Cross-cutting `OPS.*` namespace | unchanged | unchanged |

**What does NOT change.** The 25 states themselves, the Platform/Tenant split, the 17-column ledger schema, the probe-vs-gate invariant, the cross-boundary code rule, the L-node-as-Probe mapping. Only the name changes. Substantive content is unaltered.

**Future-proofing.** MLS is the **first instantiation of a per-platform-domain lifecycle-states framework**. If intervention/action lifecycle later needs the same treatment, it lands as a sibling framework (e.g., **ALS — Action Lifecycle States**) reusing the same substrate shape, not as an extension of MLS. The substrate ADR (drafted in SES-5f806e) is authored MLS-first; siblings can be added without renaming MLS.

**Body of this ADR retains the original "OLS" wording** as the historical record of what was filed. Future references to this framework — in new ADRs, code, ADR file paths cited externally, conversation, MCP tool calls — use MLS. No supersession; the rename is recorded as errata per ADR Hygiene Policy (DEC-623f8f).

**Affected ADRs renamed in tandem (sibling errata).**

- DEC-9d7a5c (D390) — was OLS Failure Vocabulary, now MLS Failure Vocabulary; code namespace migrates `OLS-NN.*` → `MLS-NN.*`
- DEC-b8b825 (D391) — was OLS-14 Semantic Activation Gate, now MLS-14 Semantic Activation Gate; emission codes migrate

**Memory file rename.** `feedback_object_life_states.md` becomes `feedback_metric_lifecycle_states.md`; MEMORY.md index updated in same change.
