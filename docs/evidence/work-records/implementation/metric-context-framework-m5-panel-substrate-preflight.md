---
uid: metric-context-framework-m5-panel-substrate-preflight
title: MCF M5 Panel Substrate Preflight
description: Docs-only preflight that frames the next substrate gate after M7/M8 (formula AST + hash/signature authority live). M2/M3/M4/M7/M8 are complete, live, evidenced, and closed; the MCF substrate accepts MC authoring at the structural + lifecycle + hash-discipline layers, but no panel exists yet to produce the panel-attestation rows that M4 records on `mcf.certification_record` (via the already-wired `fk_mcf_cert_panel_run → contract.panel_output_record`) and that M4 records on `mcf.metric_publication_eligibility_result.panel_run_uid` (FK currently deferred). Per MCF build plan §M5 + requirements §11.3 + §17.1, the Metric Authoring Panel is a governed tool workbench (mirroring BCF Chapter 7 / DEC-149ab2 panel architecture) producing per-run records + per-model transcripts + workbench fingerprints. The build plan calls for mcf-owned panel-run + transcript + allowlist tables carrying reservoir-provenance fields (addendum guardrail #6) that don't fit the shared `contract.panel_output_record` shape. Live state confirms: `contract.panel_output_record` already exists (24 rows from BCF authoring; `stage_code` enum includes `authoring/publication/lifecycle_audit` which is already MCF-compatible without CHECK extension); `contract.authoring_panel_rejection_log` is BCF-scoped (CHECK on `scope_code` admits `bf_bo/cf/mapping`, `primitive_type` admits `business_field/business_object/canonical_field`, `defect_code` admits 9 BCF-specific codes) — MCF will not extend this BCF-specific table but will need its own MC-specific defect-code registry and rejection-routing decisions. This preflight enumerates the M5 ownership boundary (what the substrate must own vs what M11 ingestion + M12 panel impl own); the relationship to the shared `contract.*` panel substrate; 4 candidate substrate designs (D-M5-A composition vs D-M5-B hybrid vs D-M5-C reuse-only vs D-M5-D mirror-BCF-rejection-log-pattern); 8 risks (R-M5-1..R-M5-8); 10 operator decisions (D-M5-1..D-M5-10) needed before any M5 DBCP can open. Recommendation: **D-M5-B hybrid composition** — keep `contract.panel_output_record` as the canonical panel-run identity (panel_run_uid lives there; cross-framework panel-run discipline reused); add 4 new mcf-owned tables (`mcf.metric_authoring_panel_run` for MCF-specific extensions including workbench fingerprint + reservoir-provenance fields, `mcf.metric_authoring_panel_transcript` for per-model immutable transcripts, `mcf.workspace_tool_allowlist` for versioned MCF tool registry, `mcf.evidence_source_allowlist` for versioned MCF evidence sources); activate 3 deferred FKs from `mcf.metric_contract_revision` + `mcf.metric_publication_eligibility_result` + `mcf.metric_supersession` → `contract.panel_output_record` (matches the already-wired `fk_mcf_cert_panel_run` pattern); add 1 mcf-specific defect-code CHECK enum on `mcf.metric_authoring_panel_run.consensus_payload_json` schema validator (no extension to `contract.authoring_panel_rejection_log` BCF-specific table); seed `contract.framework_policy` entries for MCF panel discipline (extends the existing M4-seeded `mcf_v1` policy with panel-specific fields). Docs-only. No bc-core edits. No DDL. No MCF metric contracts. No M11 ingestion / M12 panel impl. No M9/M10 work. No BCF data touches. Recommended next gate: combined M5 DBCP (covers all 4 new mcf tables + 3 FK activations + panel-discipline policy extension + defect-code registry strategy in one document, since they are all in service of "the panel substrate" and decomposition adds gate-count without reducing review surface).
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m5-panel-substrate-preflight
---

# MCF M5 Panel Substrate Preflight

## 1. Scope and grounding

### 1.1 Purpose

Frame the next substrate gate in the MCF arc now that M7/M8 (formula AST + hash/signature authority) is live and the MCF substrate can accept MC authoring at the structural + lifecycle + hash-discipline layers. M4 already wires panel-attestation snapshots on `mcf.certification_record` and `mcf.metric_publication_eligibility_result`; the M3 cert-amendment shipped the FK from `mcf.certification_record.panel_run_uid` to `contract.panel_output_record`. What is **still missing** is the Metric Authoring Panel substrate itself — the tables that hold per-run records, per-model transcripts, workbench fingerprints, reservoir-provenance fields, tool/evidence allowlists, and the panel-discipline policy entries — without which no real panel can run and no real metric contracts can be authored.

This preflight scopes M5 (the substrate gate), identifies design options, surfaces the ownership boundary between shared `contract.*` substrate and mcf-owned tables, and recommends a path. It is **docs-only**. It does not write an M5 DBCP. It does not apply DDL. It does not edit bc-core. It does not author M11 ingestion / M12 panel implementation work. It enumerates what an operator-approved M5 DBCP would need to decide.

### 1.2 What this preflight is and is not

| | This preflight |
|---|---|
| Is | A docs-only framing of the M5 scope + open questions + operator decisions + DBCP-shape recommendation |
| Is | The formal record of "M7/M8 is live but operationally dormant for real-metric authoring; here is the bounded path to first-real-panel capability" |
| Is not | The M5 DBCP itself (next gate; designs the panel substrate tables + FK activations + policy seeds + defect-code registry) |
| Is not | The M11 ingestion DBCP (gates on M5; designs the reservoir → intake-queue pipeline) |
| Is not | The M12 Metric Authoring Panel implementation (gates on M5 + M7 + M10 + M11; designs the three-model workbench service) |
| Is not | An M2/M3/M4/M7/M8 substrate change — those gates are closed and live |
| Is not | A BCF substrate change — `contract.authoring_panel_rejection_log` BCF-specific CHECKs will NOT be extended; MCF uses its own defect-code surface |
| Is not | A bc-core code edit |
| Is not | A real-metric authoring action — substrate stays empty pending M12 panel + operator-authored test runs |

### 1.3 Source documents consumed

| Source | Role | Commit / location |
|---|---|---|
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority | `bc-docs-v3/docs/adrs/ADR-c3e57f.md` |
| MCF requirements §11.3 (Metric Authoring Panel) | Three-model panel architecture; workbench discipline; tool-set composition; per-agent immutable transcripts | `metric-context-framework-requirements.md` §11.3 |
| MCF requirements §17.1 (per-panel-run record) | Required fields on every panel run (panel_run_uid, prompt_version, policy_version, workbench fingerprint, per-model verdicts, consensus result, grounding check per claim) | same doc §17.1 |
| MCF build plan §M5 | T-shirt L; scope enumeration (mcf.metric_authoring_panel_run + mcf.metric_authoring_panel_transcript + mcf.workspace_tool_allowlist + mcf.evidence_source_allowlist + framework_policy entries for MCF panel discipline); addendum guardrail #6 reservoir-provenance fields; primary risk: workbench fingerprint algorithm specification drift | `metric-context-framework-build-plan.md` §M5 |
| BCF Chapter 7 (Context Panels as governed tool workbenches) | Workbench architecture MCF mirrors; same discipline (input-hashed + output-hashed + transcript + scoped + dropped-surface-blocked tool calls; workbench fingerprint) | `business-context-framework-requirements.md` Chapter 7 (commit `1d7d209`) + `bc-docs-v3/docs/adrs/ADR-149ab2.md` (DEC-149ab2 / D411 BCF panel architecture) |
| M3 cert-amendment closeout | Confirms `fk_mcf_cert_panel_run → contract.panel_output_record` already live | `mcf-m3-cert-amendment-apply-closeout.md` (`60efd9d`) |
| M4 DBCP §6.7 + service spec | Confirms M4 cert writer accepts 6 panel-attestation fields (`panelRunUid`, `promptVersion`, `modelIdentityJson`, `inputHash`, `samplingStatus`, `groundingCheckResult`) via `CertContextInput`; M4 stores snapshots, panel writes to `contract.panel_output_record` separately | `metric-context-framework-m4-lifecycle-certification-dbcp.md` (3983530) + `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` |
| M4 apply closeout | M4 cert writer live; integration tested 7/7 PASS; operationally dormant pending panel | `mcf-m4-ddl-apply-closeout.md` (`c2bc3fc`) |
| M7/M8 apply closeout | Formula AST storage + trigger amendment live; M7/M8 services + coordinator live; algorithm-version `mcf-hash-v1` | `mcf-m7-m8-apply-closeout.md` (`6b3ffb2`) |
| Live `contract.panel_output_record` schema + CHECKs | Verified empirically against `bc_platform_dev`: 13 columns; `stage_code` enum admits `authoring/publication/lifecycle_audit`; `defect_code` enum is BCF-specific (9 codes); 24 rows from BCF authoring | `bc-postgres` MCP `pg_describe_table` + `pg_query` (read-only) |
| Live `contract.authoring_panel_rejection_log` schema + CHECKs | Verified empirically: `scope_code` enum admits `bf_bo/cf/mapping` (NOT `mcf`); `primitive_type` enum admits `business_field/business_object/canonical_field` (NOT `metric_*`); 1 row | same |

### 1.4 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — read-only this session |
| No DDL applied or drafted | ✓ — docs-only |
| No MCF metric contracts created | ✓ — substrate stays empty |
| No certification rows written | ✓ — M4 service operationally dormant |
| No panel runs written to `contract.panel_output_record` | ✓ — no MCF panel exists |
| No BCF data touched | ✓ — `concept_registry.*` unchanged; existing 24 BCF panel runs untouched |
| No M9/M10 work | ✓ — gated on later DBCPs |
| No M11 ingestion work | ✓ — gates on M5; this is M5 preflight only |
| No M12 panel implementation | ✓ — gates on M5 + M7 + M10 + M11 |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |
| No new M5 DBCP opened | ✓ — preflight only |

---

## 2. Current live substrate state

### 2.1 What is live (after M7/M8 apply)

**MCF substrate (10 `mcf.*` tables, all 0 rows):**

| Table | Origin gate | Panel-related columns |
|---|---|---|
| `mcf.metric_contract` | M2 | — |
| `mcf.metric_contract_version` | M2 (M7 amended) | `formula_ast_canonical_json` (new in M7) |
| `mcf.metric_variable_binding` | M2 | — |
| `mcf.metric_filter_clause` | M2 | — |
| `mcf.metric_computed_dimension_ref` | M2 | — |
| `mcf.metric_contract_revision` | M3 | `panel_run_uid uuid` — **FK currently deferred** |
| `mcf.metric_supersession` | M3 | `panel_run_uid uuid` — **FK currently deferred** |
| `mcf.certification_record` | M3 cert-amendment | `panel_run_uid uuid` — **FK LIVE: `fk_mcf_cert_panel_run → contract.panel_output_record`** |
| `mcf.metric_publication_eligibility_result` | M4 | `panel_run_uid uuid` — **FK currently deferred** |
| `mcf.metric_cert_writer_idempotency` | M4 | — |

**Shared `contract.*` panel substrate (BCF-shared):**

| Table | Origin | Rows | MCF-compatible today? |
|---|---|---|---|
| `contract.panel_output_record` | BCF | 24 (all `stage_code='authoring'`, BCF panel runs) | **YES** — `stage_code` CHECK admits `('authoring','publication','lifecycle_audit')`; MCF can write rows without CHECK extension. `defect_code` CHECK on `verdict_payload_json` is conditional on `verdict_code='REJECT'` AND admits 9 BCF-specific codes — would reject MCF-specific defect codes if used. |
| `contract.authoring_panel_rejection_log` | BCF | 1 | **NO** — `scope_code` admits `('bf_bo','cf','mapping')`, `primitive_type` admits `('business_field','business_object','canonical_field')`, `defect_code` admits 9 BCF codes. None of these admit MCF values. |

**M4-seeded mcf rows on shared substrate (intact):**

| Table | Rows |
|---|---|
| `contract.framework_policy` (scope=mcf) | 1: `mcf_v1` / `1.0.0` |
| `contract.operator_confirm_rule` (scope=mcf) | 2: `mcf_metric_transition_approved_to_active`, `mcf_metric_supersede_active_to_superseded` |

**BCF data (untouched):**

| Table | Rows |
|---|---|
| `concept_registry.business_concept` | 10 |
| `concept_registry.entity` | 2 |

### 2.2 Service layer state

| Symbol | Status |
|---|---|
| `McfCertWriterService` (5 methods) | LIVE; 7/7 integration PASS with `MockMcfHashComputer`; accepts 6 panel-attestation fields per `CertContextInput` (NF1 all-or-none CHECK enforced); operationally dormant for real authoring (no panel to call it) |
| `McfHashComputerCoordinator` (real) | LIVE post-M7/M8 PR #110; returns 6 hashes + `mcf-hash-v1` marker |
| `FormulaCanonicalizationService` + `PackageSignatureService` | LIVE; AST normalization + JCS + 6 hashes computed deterministically |
| Production guard (`assertProductionHashAlgorithm`) | LIVE; rejects `mcf-mock-*` and legacy `mock-*` markers in production |
| **MCF panel service** | **DOES NOT EXIST** — no `MetricAuthoringPanelService`, no `mcf.metric_authoring_panel_run` substrate, no workbench-fingerprint algorithm implementation |
| **MCF intake / ingestion service** | **DOES NOT EXIST** — M11 gate (downstream of M5) |
| **MCF self-verification fixture / verifier engine** | **DOES NOT EXIST** — M9 / M10 gates (independent of M5; can ship in parallel) |

### 2.3 What this means

The MCF substrate is **structurally complete for one-row-at-a-time programmatic authoring** via the M4 service. An operator (or a future panel) can construct a `CreateMetricDraftInput`, pass it to `McfCertWriterService.createMetricDraft`, and a `mcf.metric_contract` + `mcf.metric_contract_version` row will be written under cert discipline with hashes computed via M7/M8. **But no panel exists to produce the per-run record that the cert depends on for grounding.** The 6 panel-attestation fields on `CertContextInput` would be set to `null` (allowed per NF1 all-or-none), which means the cert would carry the audit-only flag indicating no panel attestation was present — which is not the production discipline target. Production MCF authoring requires panel attestation on every cert, which requires the M5 substrate to exist so panel runs can be persisted before cert writes.

---

## 3. Why M5 is the next gate

### 3.1 What unblocks if M5 ships

| Capability | Currently blocked by | After M5 |
|---|---|---|
| Real Metric Authoring Panel run can be persisted | No `mcf.metric_authoring_panel_run` table | Panel can write per-run records + per-model transcripts |
| M4 cert writer can accept panel-attested input with FK-resolvable `panel_run_uid` | 3 of 4 mcf panel_run_uid columns lack FKs; cert writer accepts a `panel_run_uid` but no upstream gate enforces it exists | FKs activated; M4 cert writer's NF1 all-or-none discipline can be tightened from "all-NULL OR all-non-NULL" to "all-non-NULL for production paths" |
| Panel workbench has a fingerprint algorithm and substrate-stored fingerprint hash | No `workbench_fingerprint_hash` column | Substrate stores the fingerprint; M12 impl computes per the algorithm spec; consensus validity check (M12 § per requirements §11.3) can run |
| Panel tool/evidence allowlists are versioned and substrate-controlled | Allowlists exist conceptually only | `mcf.workspace_tool_allowlist` + `mcf.evidence_source_allowlist` substrate-enforced; tool calls outside the allowlist rejected before the panel can use them |
| Reservoir provenance (addendum guardrail #6) is captured per panel run | No reservoir-provenance fields anywhere | Panel runs carry reservoir name, entry ID, provenance source, confidence band; ingestion (M11) populates these |
| `contract.framework_policy` MCF panel-discipline fields are populated | M4 seeded only `consensus_requirement_json` + `operator_confirm_rules_uid_list`; no panel-specific policy fields | M5 extends the seeded `mcf_v1` policy with panel-discipline fields (workbench fingerprint algorithm name + version; defect-code registry version; transcript retention policy) |

### 3.2 What does NOT unblock by M5 alone

| Capability | Still gated by |
|---|---|
| Reservoir ingestion service (`co_bindings` stripping; reservoir-provenance population) | M11 |
| Metric Authoring Panel service (three-model workbench; tool calls; consensus; grounding-check) | M12 (depends on M5 + M7 + M10 + M11) |
| Self-verification fixture substrate | M9 (independent of M5; ships in parallel) |
| Deterministic verifier engine | M10 (depends on M9) |
| PE-MC evaluator | M13 (depends on M5 + M7 + M9 + M10) |
| Publication path (operator-confirm activation) | M14 (depends on M4 + M5 + M13) |
| Real MCF metric contracts | Sum of M5 + M11 + M12 + M13 + operator-driven test runs |

### 3.3 Sequencing rationale

M5 is selected as the next gate (not M9 or another) because:

1. **The build plan declares M5 the immediate post-M4 gate** (build plan §M5, t-shirt L). M9 is independent (per build plan: "BCF-enrichment dependency: No"; depends only on M7).
2. **M11 / M12 / M13 all depend on M5** (per build plan dependency table). M5 unblocks 4 downstream gates; M9 unblocks 2 (M10 + M13).
3. **The M4 cert writer's panel-attestation fields are unused** — every cert today (if one were written) would set them NULL. M5 ends that asymmetry: post-M5, the substrate has somewhere to point those fields.
4. **M3 cert-amendment already wired one FK** to `contract.panel_output_record`; M5 is the natural moment to activate the other 3 deferred FKs on the same target (cheap completion of a partially-shipped pattern).
5. **No ingestion service is needed yet** — M5 is substrate-only. Operator can hand-author panel-run rows for substrate verification (mirrors M4 pattern of hand-authoring synthetic cert rows in the post-apply verifier).

---

## 4. M5 ownership boundary

### 4.1 What M5 MUST do (substrate scope)

| # | Deliverable | Rationale |
|---|---|---|
| 1 | **`mcf.metric_authoring_panel_run`** table | Per-run record per build plan §M5 + MCF §17.1. Holds workbench fingerprint hash + reservoir-provenance fields + consensus payload + per-model verdict snapshots. Keyed on `panel_run_uid` (UUID; matches `contract.panel_output_record.panel_run_uid` — same identity across both tables). |
| 2 | **`mcf.metric_authoring_panel_transcript`** table | Per-model immutable transcript per build plan §M5 + MCF §11.3 (per-agent immutable interactive transcripts as audit artifacts). One row per (panel_run_uid, model_role_code) — typically 3 rows per panel run (Maker / Checker / Moderator). Append-only per Invariant V; rejects UPDATE/DELETE via substrate trigger (mirrors M3 child-immutability pattern). |
| 3 | **`mcf.workspace_tool_allowlist`** table | Versioned registry of MCF-specific tools the workbench may call (e.g. `bcf_registry_search`, `ast_validity_probe`, `grain_reachability_check`, `fiscal_calendar_resolve`, `mls_readiness_probe`). Per build plan §M5 + MCF §11.3.3 (tool-set composition is MCF's only divergence from BCF). |
| 4 | **`mcf.evidence_source_allowlist`** table | Versioned registry of MCF-specific evidence sources for citation (e.g. industry standards, regulatory references, internal working papers). Per build plan §M5 + MCF §11.3.1. |
| 5 | **3 FK activations**: `mcf.metric_contract_revision.panel_run_uid` + `mcf.metric_publication_eligibility_result.panel_run_uid` + `mcf.metric_supersession.panel_run_uid` → `contract.panel_output_record` | Completes the partial-FK pattern started by M3 cert-amendment's `fk_mcf_cert_panel_run`. After M5: all 4 mcf panel_run_uid columns FK to the same target, ensuring referential consistency for the entire panel-attestation surface. |
| 6 | **Panel-discipline extension to `contract.framework_policy` `mcf_v1`** | Add panel-discipline fields to the seeded mcf policy: workbench fingerprint algorithm name + version, defect-code registry version, transcript retention policy, allowlist version pinning rules. Implemented as additional JSON fields in `consensus_requirement_json` OR a new policy column (TBD per D-M5-9). |
| 7 | **Defect-code registry strategy** | MCF panel needs its own defect-code taxonomy (`MC_DEFECT_*` per MCF §11.3.4 + requirements §13). Decision: defect codes live in `mcf.metric_authoring_panel_run.consensus_payload_json` validated by JSON schema (NOT a CHECK enum on the column), OR in a new `mcf.metric_defect_code` registry table. Per D-M5-7 below. |
| 8 | **Optional rollback DDL** | Per M3/M7/M8 pattern — rollback drops the 4 new tables, removes the 3 FKs, reverts the policy extension. Refuses if any panel run / transcript / allowlist row exists. |
| 9 | **Dry-run + post-apply verifier scripts** | Mirror M3/M4/M7/M8 pattern: dry-run confirms preconditions (M4 substrate live; no `mcf.metric_authoring_panel_run` table; 3 deferred FKs absent); post-apply confirms structural + behavioral (synthetic-row exercises for FK enforcement + transcript immutability trigger). |

### 4.2 What M5 MUST NOT do

| # | Out-of-scope | Belongs to |
|---|---|---|
| 1 | Write real panel runs to any substrate | M12 implementation (with operator-driven test runs) |
| 2 | Fabricate PE verdicts on `mcf.metric_publication_eligibility_result` | M13 PE-MC evaluator |
| 3 | Implement the three-model panel service (Maker / Checker / Moderator) | M12 |
| 4 | Implement the workbench fingerprint algorithm | M12 (substrate stores the hash; algorithm spec is M12) |
| 5 | Implement the tool-call boundary (allowlist enforcement at call time) | M12 (substrate defines the allowlist; runtime enforcement is M12) |
| 6 | Build the self-verification fixture substrate | M9 |
| 7 | Build the deterministic verifier engine | M10 |
| 8 | Build the reservoir ingestion service | M11 |
| 9 | Build the operator console / workbench UI | M16 / M17 |
| 10 | Extend `contract.authoring_panel_rejection_log` to admit MCF scope/primitive/defect codes | NEVER — that table is BCF-specific by design (per BCF Chapter 7); MCF rejection routing lives in `mcf.metric_authoring_panel_run.consensus_payload_json` per D-M5-7 |
| 11 | Touch BCF data (`concept_registry.*` or BCF panel runs) | NEVER in MCF gates |
| 12 | Real MCF metric contracts | Sum of M5 + M11 + M12 + M13 + operator runs |

---

## 5. Relationship to `contract.panel_output_record` and existing panel/audit substrate

### 5.1 The shared `contract.panel_output_record` is already MCF-compatible at the structural level

Empirical inspection (read-only via bc-postgres MCP) confirms:

| Column | CHECK | MCF compatibility |
|---|---|---|
| `panel_run_uid uuid` | PK (implicit) | Native — same UUID identity across BCF and MCF |
| `stage_code text NOT NULL` | `IN ('authoring','publication','lifecycle_audit')` | **Native MCF-compatible** — MCF authoring uses `authoring`; PE-MC re-eval uses `publication`; M3 amendment audit uses `lifecycle_audit`. **No CHECK extension needed.** |
| `prompt_version text NOT NULL` | (no CHECK) | Native — MCF prompts versioned independently from BCF |
| `model_identity_json jsonb NOT NULL` | (no CHECK) | Native — MCF panel can record its own 3-model identity (Maker/Checker/Moderator vendor + model + revision) |
| `agent_outputs_json jsonb NOT NULL` | (no CHECK) | Native — MCF panel writes per-agent outputs here OR delegates to `mcf.metric_authoring_panel_transcript` (per D-M5-2 below) |
| `input_hash text NOT NULL` | (no CHECK) | Native — MCF computes input hash over the candidate intake bundle |
| `verdict_code text NOT NULL` | (no CHECK at column level; conditional CHECK at `defect_code`) | Native — MCF verdicts use `APPROVE_FOR_DRAFT / OPERATOR_REVIEW / REJECT_*` per MCF §11.3.5 (vs BCF's set) |
| `verdict_payload_json jsonb NOT NULL` | `verdict_code='REJECT' → defect_code IN (9 BCF codes)` | **PARTIAL conflict** — if MCF panel writes `verdict_code='REJECT'` to `contract.panel_output_record` with an MCF-specific defect code, the CHECK will reject it. **Per D-M5-7: MCF writes REJECT verdicts to `mcf.metric_authoring_panel_run.consensus_payload_json` (its own structured record) and writes a simpler `verdict_code='REJECT'` summary without an MCF defect code in `verdict_payload_json` to `contract.panel_output_record`** — preserves BCF CHECK integrity while keeping MCF defect taxonomy MCF-owned. Alternative D-M5-D would extend the shared CHECK additively (mirrors M3 cert-amendment shared-CHECK extension pattern). |
| `grounding_check_result text NOT NULL` | `IN ('pass','quarantined')` | Native MCF-compatible |
| `quarantined boolean NOT NULL` | `(quarantined = (grounding_check_result = 'quarantined'))` | Native MCF-compatible |
| `sampling_status text NOT NULL` | `IN ('not_sampled','sampled_for_calibration','sample_routed_to_operator')` | Native MCF-compatible |
| `policy_version text NOT NULL` | (no CHECK) | Native — MCF panel references `mcf_v1` or successor |
| `created_at timestamptz NOT NULL` | (default `now()`) | Native |

**Conclusion:** `contract.panel_output_record` is the canonical panel-run identity for MCF. M5 must NOT create a parallel `mcf.metric_authoring_panel_run` that duplicates the panel_run_uid identity; instead, the MCF panel-run record EXTENDS the contract row with MCF-specific fields keyed on the same panel_run_uid.

### 5.2 The shared `contract.authoring_panel_rejection_log` is BCF-specific by design

| Column | CHECK | MCF compatibility |
|---|---|---|
| `scope_code text NOT NULL` | `IN ('bf_bo','cf','mapping')` | **NOT MCF-compatible** — admits no MCF scope value |
| `primitive_type text NOT NULL` | `IN ('business_field','business_object','canonical_field')` | **NOT MCF-compatible** |
| `defect_code text NOT NULL` | `IN (9 BCF-specific codes)` | **NOT MCF-compatible** |

**Conclusion:** This table is **BCF-scoped by deliberate architectural choice** (per BCF Chapter 7 panel rejection semantics). MCF does NOT extend these CHECKs. MCF rejection routing lives in the MCF panel substrate per D-M5-7.

### 5.3 The already-wired `fk_mcf_cert_panel_run` is the precedent

The M3 cert-amendment wired `mcf.certification_record.panel_run_uid → contract.panel_output_record` via `fk_mcf_cert_panel_run`. M5 completes this pattern by wiring the 3 other deferred FKs to the same target. After M5, all 4 mcf panel_run_uid columns reference `contract.panel_output_record` — the canonical panel-run identity is consistent across the entire MCF substrate.

### 5.4 The new mcf-owned tables compose, do not replace

The 4 new mcf tables (`metric_authoring_panel_run` + `metric_authoring_panel_transcript` + `workspace_tool_allowlist` + `evidence_source_allowlist`) carry MCF-specific extensions that don't fit the shared substrate:

| mcf Table | What it adds beyond `contract.panel_output_record` |
|---|---|
| `mcf.metric_authoring_panel_run` | Workbench fingerprint hash; reservoir-provenance fields (per addendum guardrail #6); MCF-specific consensus payload; transcript-uid list; per-model verdict snapshots |
| `mcf.metric_authoring_panel_transcript` | Per-model immutable interactive transcript (tool calls + responses + reasoning + verdict per agent) — append-only |
| `mcf.workspace_tool_allowlist` | Versioned registry of MCF-specific tools (BCF tool list is in BCF substrate; MCF has its own) |
| `mcf.evidence_source_allowlist` | Versioned registry of MCF-specific evidence sources |

The composition pattern (one row in `contract.panel_output_record` PLUS one row in `mcf.metric_authoring_panel_run` keyed on the same `panel_run_uid`) mirrors how `mcf.certification_record` extends a per-framework cert pattern that `contract.certification_record` ships for BCF (per M3 cert-amendment closeout).

---

## 6. Candidate substrate designs

Four options surfaced from cross-cutting the live state, the build plan §M5, and BCF's panel architecture. Each option is summarized; the recommendation in §7 picks one.

### 6.1 D-M5-A — Composition without extension

**Shape:**
- New `mcf.metric_authoring_panel_run` table with `panel_run_uid PK FK → contract.panel_output_record`
- New `mcf.metric_authoring_panel_transcript`
- New `mcf.workspace_tool_allowlist`
- New `mcf.evidence_source_allowlist`
- 3 FK activations (revision + PE result + supersession → `contract.panel_output_record`)
- No extensions to any `contract.*` CHECKs (defect code conflict resolved by writing only summary verdicts to contract.panel_output_record, MCF detail in mcf.metric_authoring_panel_run.consensus_payload_json)

**Pros:** Minimal CHECK extensions on shared substrate; preserves BCF isolation; mirrors the M3 cert-amendment per-framework sibling pattern (one shared-identity row + one framework-specific extension row). No coordination with BCF on defect-code taxonomy.

**Cons:** Two-table read for panel-run details (join via panel_run_uid); MCF defect codes are NOT enforced by Postgres CHECK at the shared substrate boundary (enforcement lives in `mcf.metric_authoring_panel_run.consensus_payload_json` JSON-schema validator at the M12 panel layer).

### 6.2 D-M5-B — Hybrid composition (RECOMMENDED — see §7)

Same as D-M5-A. The name distinguishes it as the recommended path explicitly per §7.

### 6.3 D-M5-C — Reuse-only (no new mcf tables)

**Shape:**
- Use `contract.panel_output_record` as the sole panel-run substrate
- 3 FK activations to `contract.panel_output_record`
- Store workbench fingerprint + reservoir-provenance + per-model transcripts as JSON inside `contract.panel_output_record.agent_outputs_json`
- Extend `contract.panel_output_record.verdict_payload_json` defect-code CHECK additively to admit MCF defect codes (mirrors M3 cert-amendment shared-CHECK extension pattern)

**Pros:** Zero new mcf tables; everything lives in the shared substrate. Cross-framework analytical queries are simpler (one panel-run table). Defect codes are CHECK-enforced.

**Cons:** Violates per-framework substrate boundary (per ADR DEC-149ab2 §3 — BCF and MCF maintain separate substrates for framework-specific extensions). Schema-on-read of JSON for MCF-specific fields means no Postgres-level constraint enforcement (reservoir-provenance fields can be absent without a substrate-level error). Per-model transcripts inside a single `agent_outputs_json` blob make append-only enforcement awkward (M3-style child-immutability triggers don't apply to JSON sub-paths). Build plan §M5 explicitly calls for separate `mcf.metric_authoring_panel_run` + `mcf.metric_authoring_panel_transcript` tables — D-M5-C contradicts the build plan.

### 6.4 D-M5-D — Mirror-BCF-rejection-log-pattern

**Shape:**
- Same as D-M5-A/B for the 4 new mcf tables + FK activations
- **PLUS** extend `contract.authoring_panel_rejection_log` CHECKs additively to admit MCF scope/primitive/defect codes (mirrors M3 cert-amendment shared-CHECK extension pattern)
- MCF rejection routing writes to `contract.authoring_panel_rejection_log` (the shared rejection table) instead of `mcf.metric_authoring_panel_run.consensus_payload_json`

**Pros:** Cross-framework rejection analytics (one rejection log table). Defect codes CHECK-enforced. Manual override workflow (per BCF override pattern in `authoring_panel_rejection_log.override_state` column) automatically applies to MCF.

**Cons:** Violates the BCF architectural boundary (per BCF Chapter 7: the rejection log is part of BCF's authoring-defect taxonomy, not a cross-framework primitive). MCF defect codes pollute the BCF substrate. The manual-override workflow's `override_to_state IN ('draft')` CHECK is BCF-specific (BCF returns rejected primitives to `draft` state; MCF's lifecycle may have different rejection-recovery semantics). Adds an extension that is hard to back out if MCF's rejection model diverges from BCF in later iterations.

---

## 7. Recommendation

### 7.1 Recommended path: D-M5-B (hybrid composition)

**Decision summary:**

| Aspect | Choice |
|---|---|
| Panel-run identity | `contract.panel_output_record.panel_run_uid` (shared canonical identity) |
| MCF extension table | New `mcf.metric_authoring_panel_run PK panel_run_uid FK → contract.panel_output_record` |
| Per-model transcripts | New `mcf.metric_authoring_panel_transcript` (append-only via M3-style child-immutability trigger) |
| Tool allowlist | New `mcf.workspace_tool_allowlist` (versioned per release) |
| Evidence allowlist | New `mcf.evidence_source_allowlist` (versioned per release) |
| FK activations | 3 deferred FKs activated → `contract.panel_output_record` (matches the live `fk_mcf_cert_panel_run` pattern) |
| Shared CHECK extensions | **NONE** — `contract.*` BCF substrate remains BCF-scoped |
| MCF defect codes | Stored in `mcf.metric_authoring_panel_run.consensus_payload_json`; JSON-schema validated at the M12 panel layer (NOT a Postgres CHECK enum) |
| `contract.framework_policy mcf_v1` | Extended with panel-discipline JSON fields (no new column; uses existing `consensus_requirement_json` jsonb) |

### 7.2 Why D-M5-B over the alternatives

- **vs D-M5-C (reuse-only):** D-M5-C contradicts the build plan §M5 (which explicitly lists `mcf.metric_authoring_panel_run` + `mcf.metric_authoring_panel_transcript` as substrate). It also makes per-model-transcript append-only enforcement impossible at the substrate (Postgres can't run an immutability trigger on JSON sub-paths of `agent_outputs_json`).
- **vs D-M5-D (extend shared rejection log):** The BCF `authoring_panel_rejection_log` is part of BCF's authoring-defect surface, not a cross-framework primitive. Extending it for MCF creates coupling that is hard to unwind if MCF's rejection-recovery lifecycle diverges (which it likely will — MCF's `intake → draft` transition has different recovery semantics than BCF's `proposed → draft`).
- **vs D-M5-A (composition without extension):** D-M5-A is functionally identical to D-M5-B. The naming distinction is documentary: D-M5-B is the operator-recommended path; D-M5-A is the same shape but presented as a generic option for completeness.

### 7.3 Tighter NF1 panel-attestation discipline (deferred to M5 DBCP)

The M4 service's NF1 CHECK on `mcf.certification_record` requires the 6 panel-attestation fields to be all-NULL OR all-non-NULL. Today, all-NULL is permitted (panel didn't run; cert is system-generated). Post-M5, the M5 DBCP can tighten this to require all-non-NULL for production cert writes (where production is defined as `cert.action_code IN ('metric_create','metric_transition','metric_supersede')` AND `policy_version` references an `mcf_v1` policy with `panel_required=true`). This tightening is OPTIONAL in M5 — operator decides per D-M5-10.

### 7.4 Operational decisions deferred to M12

| M5 substrate-only decision | M12 implementation decision (out of scope here) |
|---|---|
| `mcf.workspace_tool_allowlist` table shape + versioning | Which specific MCF tools to register at v1 (e.g. `bcf_registry_search`, `ast_validity_probe`); the tool-call runtime that enforces allowlist membership |
| `mcf.metric_authoring_panel_run.workbench_fingerprint_hash` column shape | The fingerprint algorithm itself (which tools + which sources + which BCF Registry snapshot version → fingerprint string → sha256) |
| `mcf.metric_authoring_panel_run.consensus_payload_json` JSON schema | The consensus algorithm (per MCF §11.3.5 — quorum / majority / Moderator-resolved) |
| `mcf.metric_authoring_panel_run.reservoir_provenance_*` columns | The reservoir ingestion service that populates them (M11) |

---

## 8. Risks and stop conditions

### 8.1 Design risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M5-1 | **Workbench fingerprint algorithm drift** | High | M5 substrate stores the hash; the algorithm spec is M12's responsibility. M5 DBCP defines the column shape + format CHECK (`sha256:<64hex>`) but does NOT pin the algorithm. M12 algorithm version is recorded in `contract.framework_policy mcf_v1.consensus_requirement_json.workbench_fingerprint_algorithm_version`. |
| R-M5-2 | **Reservoir-provenance fields not populated by ingestion (M11)** | Medium | M5 DBCP makes reservoir-provenance fields NOT NULL for production-source panel runs; sets DEFAULT to `'no_reservoir_attached'` placeholder for substrate-internal exercises. M11 ingestion service is responsible for populating them; tests in M11 assert non-placeholder values. |
| R-M5-3 | **Per-model transcript append-only enforcement** | Medium | M3-style child-immutability trigger on `mcf.metric_authoring_panel_transcript` (mirrors `mcf.fn_mvb_active_immutability_check`) rejects UPDATE/DELETE once the parent panel run reaches a terminal state. Substrate-enforced; not service-side. |
| R-M5-4 | **FK target divergence** — if a future operator-confirm flow adds a panel_run_uid column to another mcf.* table, the FK target choice (contract vs mcf) must be re-confirmed each time | Low | M5 DBCP documents the canonical target (`contract.panel_output_record`) and references the now-4 FKs as the pattern. Any future addition is a separate operator decision. |
| R-M5-5 | **MCF defect-code taxonomy drift between substrate (none) and panel (full)** | Medium | M5 ships defect codes as JSON-schema validated payloads in `mcf.metric_authoring_panel_run.consensus_payload_json`. The JSON schema lives in code (TS const) — versioned via `mcf_v1.consensus_requirement_json.defect_code_registry_version`. Any taxonomy change → policy bump (mirrors algorithm-version discipline from M7/M8). |
| R-M5-6 | **Allowlist drift between substrate (versioned) and panel (uses subset)** | Low | M5 ships versioned allowlists; M12 service enforces "panel must use only tools in the allowlist version pinned to the panel-run's `policy_version`". Substrate is the source of truth; service code references it by foreign key to the allowlist version row. |
| R-M5-7 | **Panel-attestation NF1 tightening regression** — if M5 tightens the NF1 CHECK on `mcf.certification_record` to require all-non-NULL for production, any existing test fixture that constructs certs with all-NULL panel attestation will break | Medium | M5 DBCP defers the tightening to optional per D-M5-10. If operator selects tightening, M5 DBCP ships the migration of existing test fixtures (none exist in production yet — substrate is empty — so the tightening is safe today). |
| R-M5-8 | **`contract.authoring_panel_rejection_log` BCF-specific CHECK pressure** — future M5/M12 amendment may want to use the BCF rejection-log table for cross-framework reporting | Low (deferred) | M5 explicitly chooses D-M5-B over D-M5-D. If MCF later needs cross-framework rejection analytics, the path is a future amendment (similar to M3 cert-amendment); not in M5 scope. |

### 8.2 Stop conditions

The M5 DBCP STOPS and re-frames if:

- **Build plan §M5 changes** — if reservoir-provenance fields are removed from the scope (addendum guardrail #6 revised), the `mcf.metric_authoring_panel_run` shape changes
- **MCF requirements §11.3 panel architecture changes** — if the workbench discipline is materially revised (e.g. consensus algorithm changed from 3-model to different model count), substrate shape changes
- **BCF panel substrate amendment** — if BCF decides to extend `contract.panel_output_record` or `contract.authoring_panel_rejection_log` in a way that conflicts with MCF's planned reuse, MCF coordinates
- **Operator selects D-M5-C or D-M5-D over the recommended D-M5-B** — DBCP scope changes significantly

---

## 9. Operator decisions needed before M5 DBCP can open

Before the M5 DBCP opens, the operator approves these 10 items:

| # | Decision | DBCP position |
|---|---|---|
| **D-M5-1** | Approve D-M5-B (hybrid composition) over D-M5-A / D-M5-C / D-M5-D | Recommended per §7 |
| **D-M5-2** | Confirm `mcf.metric_authoring_panel_run` columns: `panel_run_uid PK FK → contract.panel_output_record`, `workbench_fingerprint_hash text NOT NULL` (format `sha256:<64hex>`), `consensus_payload_json jsonb NOT NULL`, `reservoir_name text`, `reservoir_entry_id text`, `reservoir_provenance_source_json jsonb`, `reservoir_confidence_band text`, `created_at timestamptz NOT NULL DEFAULT now()` (8 columns; reservoir fields nullable until M11 populates them) | Recommended per §4.1 |
| **D-M5-3** | Confirm `mcf.metric_authoring_panel_transcript` columns: `transcript_uid PK uuid`, `panel_run_uid FK → contract.panel_output_record`, `model_role_code text NOT NULL` (CHECK `IN ('maker','checker','moderator')`), `model_identity_json jsonb NOT NULL`, `transcript_payload_jsonb NOT NULL` (append-only via trigger), `created_at timestamptz NOT NULL` | Recommended per §4.1 |
| **D-M5-4** | Confirm `mcf.workspace_tool_allowlist` table shape: `tool_uid PK`, `tool_code text NOT NULL`, `tool_version text NOT NULL`, `effective_from timestamptz NOT NULL`, `effective_to timestamptz` (NULL = active), `tool_metadata_json jsonb` | Recommended per §4.1 |
| **D-M5-5** | Confirm `mcf.evidence_source_allowlist` table shape (mirrors tool allowlist) | Recommended per §4.1 |
| **D-M5-6** | Confirm 3 FK activations target `contract.panel_output_record` (matching live `fk_mcf_cert_panel_run`) | Recommended per §4.1 / §5.3 |
| **D-M5-7** | Confirm MCF defect codes live in `mcf.metric_authoring_panel_run.consensus_payload_json` (JSON-schema validated at M12 layer), NOT in `contract.authoring_panel_rejection_log` (which stays BCF-specific) | Recommended per §6.1 |
| **D-M5-8** | Confirm `mcf.metric_authoring_panel_transcript` is append-only via M3-style child-immutability trigger (UPDATE/DELETE rejected once parent panel run reaches terminal state) | Recommended per R-M5-3 |
| **D-M5-9** | Confirm `contract.framework_policy mcf_v1.consensus_requirement_json` is the home for panel-discipline fields (workbench fingerprint algorithm version + defect-code registry version + transcript retention policy + allowlist version pinning) — extends in-place, no new column | Recommended per §4.1 #6 |
| **D-M5-10** | **Optional:** tighten `mcf.certification_record` NF1 CHECK to require all-non-NULL panel-attestation fields for production cert writes (where production = `cert.action_code IN ('metric_create','metric_transition','metric_supersede')` AND `policy_version` references `mcf_v1` with `panel_required=true`) | Operator choice; safe today (substrate empty); deferred to D-M5-10 confirmation |

---

## 10. Recommended next gate

### 10.1 Recommendation: open combined M5 DBCP (single document)

The M5 DBCP covers all 4 new mcf tables + 3 FK activations + panel-discipline policy extension + defect-code registry strategy in one document because:

1. All 6 deliverables (4 tables + 3 FKs + policy extension + defect registry — though FKs count as one operation logically) are in service of the same architectural goal ("the MCF panel substrate"). Decomposing them into multiple DBCPs adds gate-count without reducing review surface.
2. The DDL applies atomically inside one `BEGIN/COMMIT` (mirrors M3 cert-amendment + M7/M8 atomic combined DDL pattern).
3. The dry-run + post-apply verifier scripts naturally cover the full set in one pass.
4. The closeout doc references the full substrate-change set in one timeline.

**Suggested DBCP filename:** `metric-context-framework-m5-panel-substrate-dbcp.md`

**Suggested PR title:** `feat(mcf): M5 Panel Substrate — metric_authoring_panel_run + transcript + tool/evidence allowlists + 3 FK activations + mcf_v1 policy extension (NO DB APPLY)`

### 10.2 Subsequent gates (after M5 DBCP merges, applies, evidence-PRs)

| Gate | Status post-M5 apply |
|---|---|
| M9 fixture substrate | UNBLOCKED — can ship in parallel with M11 (no M5 dependency per build plan) |
| M11 reservoir ingestion service | UNBLOCKED — needs M5 to populate `reservoir_provenance_*` fields |
| M12 Metric Authoring Panel implementation | UNBLOCKED — needs M5 + M7 + M10 + M11 |
| M13 PE-MC evaluator | Still gated on M9 + M10 |
| M14 publication path | Still gated on M4 + M5 + M13 |
| Real MCF metric contracts | Still requires sum of M5 + M11 + M12 + M13 + operator-driven test runs |

### 10.3 Sequencing per build plan

M5 → M9 (parallel) → M10 → M11 → M12 → M13 → M14 → real metrics. M5 is the foundational substrate gate; M9 can ship in parallel because it depends only on M7 (which is live).

---

## 11. What stays closed

| Gate | Status |
|---|---|
| M5 DBCP | Operator authorizes next; not opened by this preflight |
| M5 small-DDL apply | Pending M5 DBCP merge |
| M5 evidence PR | Pending M5 apply |
| **M9 fixture substrate** | CLOSED — gated on operator authorization (can ship parallel to M5 / M11) |
| **M10 deterministic verifier service** | CLOSED — gated on M9 |
| **M11 reservoir ingestion service** | CLOSED — gated on M5 + operator authorization |
| **M12 Metric Authoring Panel implementation** | CLOSED — gated on M5 + M7 + M10 + M11 |
| **M13 PE-MC evaluator** | CLOSED — gated on M5 + M7 + M9 + M10 |
| **M14 / M15 publication / supersession paths** | CLOSED — gated on M4 + M5 + M13 |
| **M16 / M17 operator console** | CLOSED — gated on M12 + M14 |
| **M18 tenant binding console** | CLOSED — gated on M6 (not yet opened) |
| **Real MCF metric contracts** | CLOSED — substrate accepts authoring post-M7/M8, but no panel + no ingestion = no real authoring |
| **BCF data changes** | CLOSED — untouched throughout MCF arc |
| **`contract.authoring_panel_rejection_log` extensions** | CLOSED — table stays BCF-specific per architectural choice; MCF uses its own rejection routing per D-M5-7 |
| **`contract.panel_output_record.verdict_payload_json` defect-code CHECK extension** | CLOSED — MCF writes summary verdicts to the shared table; MCF defect detail lives in `mcf.metric_authoring_panel_run.consensus_payload_json` per D-M5-7 |
| **M7/M8 algorithm bump (v2)** | CLOSED — `mcf-hash-v1` remains forever-locked unless an ADR-governed change requires bump |

---

## Document verification

- **Scope clear** — §1 frames as docs-only preflight; §1.4 enumerates 11 discipline assertions
- **Live state captured** — §2 enumerates 10 mcf.* tables (all empty), shared contract.* substrate (24 BCF panel runs untouched), M4 seeds intact, BCF concept_registry.* untouched
- **Why M5 next** — §3 enumerates what unblocks (6 capabilities) + what stays blocked + sequencing rationale (5 reasons M5 is the right next gate)
- **Ownership boundary** — §4 enumerates 9 MUST deliverables + 12 MUST NOT items
- **Relationship to shared substrate** — §5 documents structural compatibility of `contract.panel_output_record` (native MCF-compatible per CHECK inspection); BCF-specificity of `contract.authoring_panel_rejection_log` (NOT extending); precedent set by live `fk_mcf_cert_panel_run`; composition rationale
- **Candidate designs** — §6 enumerates 4 options (D-M5-A / D-M5-B / D-M5-C / D-M5-D) with pros/cons each
- **Recommendation** — §7 selects D-M5-B (hybrid composition); cross-references the build plan + ADR DEC-149ab2 boundary; defers operational decisions to M12
- **Risk register** — §8 enumerates 8 risks (R-M5-1..R-M5-8) with severity + mitigation; 4 stop conditions
- **Operator approvals enumerated** — §9 lists 10 decisions (D-M5-1..D-M5-10) the operator must give before the M5 DBCP can open
- **Next gate recommended** — §10 specifies the combined M5 DBCP (single document); §10.2 enumerates downstream gates post-apply; §10.3 sequences M5 → M9 (parallel) → M10 → M11 → M12 → M13 → M14
- **What stays closed** — §11 enumerates 14 closed gates including BCF-substrate-related ones explicitly NOT touched
- **No DDL, no code, no metric authoring, no BCF touches** this session — this preflight only
