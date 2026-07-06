---
uid: metric-context-framework-m5-panel-substrate-dbcp
title: MCF M5 Panel Substrate DBCP
description: Combined design-blueprint for MCF gate M5 (Metric Authoring Panel substrate) per operator-accepted preflight decisions D-M5-1..D-M5-10 (preflight 6e46d77). Patched 2026-05-27 per review M-M5-1/M-M5-2/M-M5-3: transcript FK retargeted to mcf.metric_authoring_panel_run (substrate-enforced MCF-only attachment); index count corrected to 7 (3 CREATE INDEX + 4 CREATE UNIQUE INDEX); §15.4 byte-match discipline tightened with semantic-equivalence carve-out for multi-line CHECKs. Realizes D-M5-B hybrid composition: KEEP `contract.panel_output_record` as the canonical panel-run identity (cross-framework shared substrate already exists and is structurally MCF-compatible per stage_code enum + 24 live BCF rows untouched); ADD 4 mcf-owned tables for MCF-specific panel discipline (`mcf.metric_authoring_panel_run` with workbench fingerprint hash + reservoir-provenance fields per addendum guardrail #6 + consensus payload + 1:1 PK FK to contract.panel_output_record; `mcf.metric_authoring_panel_transcript` per-model immutable interactive transcript with FK to mcf.metric_authoring_panel_run per M-M5-1 patch — NOT to contract.panel_output_record, which substrate-enforces transcripts cannot orphan to BCF/non-MCF panel runs — and M3-style append-only/immutability trigger; `mcf.workspace_tool_allowlist` versioned MCF tool registry with effective_from/effective_to; `mcf.evidence_source_allowlist` versioned MCF evidence source registry); ACTIVATE 3 deferred FKs from `mcf.metric_contract_revision` + `mcf.metric_publication_eligibility_result` + `mcf.metric_supersession` → `contract.panel_output_record` (matches the already-live `fk_mcf_cert_panel_run` precedent wired by M3 cert-amendment); EXTEND seeded `contract.framework_policy mcf_v1.consensus_requirement_json` in-place with panel-discipline fields (workbench fingerprint algorithm name + version, defect-code registry version, transcript retention policy, allowlist version pinning). NO `contract.*` CHECK extensions — BCF substrate stays BCF-scoped (`contract.authoring_panel_rejection_log` not extended per D-M5-7; `contract.panel_output_record.verdict_payload_json` defect-code CHECK not extended — MCF writes summary verdicts to shared table, MCF defect detail to `mcf.metric_authoring_panel_run.consensus_payload_json` JSON-schema validated at M12 layer). NO bc-core edits this session. NO DDL apply. NO MCF metric contracts. NO panel implementation (M12 gate). NO ingestion service (M11 gate). NO M9 fixture substrate. NO M10 verifier engine. NO BCF data touches. Substrate change: 4 new tables (~30 columns total), 3 FK activations (plus 2 new FKs declared inline at table creation: panel_run → contract and transcript → panel_run), 1 trigger function, 1 in-place UPDATE on seeded policy row; all atomic inside one BEGIN/COMMIT per §14 + M3/M7/M8 atomicity pattern. 10 risks (R-M5-1..R-M5-10; R-M5-10 added + RESOLVED-at-substrate by M-M5-1 patch) + 10 operator approvals (O-M5-1..O-M5-10) + test plan (structural verifier + behavioral synthetic-row append-only trigger exercises + FK enforcement exercises incl #11a transcript-orphan-rejection per M-M5-1 + policy-extension regression assertion). Recommended next gate: M5 implementation PR (NO DB APPLY); separate small-DDL apply gate after impl PR merges. Mirrors M3 cert-amendment + M7/M8 sequencing.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m5-panel-substrate-dbcp
---

# MCF M5 Panel Substrate DBCP

## 1. Scope and grounding

### 1.1 Purpose

Design the M5 panel substrate that unblocks future Metric Authoring Panel (M12) implementation, reservoir ingestion (M11), and PE-MC evaluator (M13). The substrate ships 4 new mcf-owned tables + 3 FK activations + 1 policy extension under a single combined DBCP per the preflight recommendation.

The substrate stays **dormant** post-apply: no panel runs are written, no transcripts are recorded, no MCF metric contracts are authored. The 4 new tables exist, the 3 FKs enforce referential integrity, the policy carries panel-discipline metadata — but no row flow happens until M11 ingestion + M12 panel implementation ship and operator-driven test runs begin.

The DBCP follows the operator-accepted preflight (`bc-docs-v3 6e46d77`) recommendations and the 10 locked operator decisions enumerated in §2.

### 1.2 What this DBCP is and is not

| | This DBCP |
|---|---|
| Is | A combined docs-only design blueprint for M5 (panel substrate + FK activations + policy extension) under one document, per D-M5-1 hybrid composition |
| Is | The formal trigger for a sequenced implementation arc (DBCP → impl PR → small-DDL apply gate → evidence PR) |
| Is not | A code edit — bc-core stays unchanged this session |
| Is not | A DDL apply — the substrate changes are a separate operator-authorized session |
| Is not | An M11 reservoir ingestion design (downstream; depends on M5) |
| Is not | An M12 Metric Authoring Panel implementation design (downstream; depends on M5 + M7 + M10 + M11) |
| Is not | An M9 fixture substrate design or M10 verifier engine design (independent; can ship in parallel) |
| Is not | A BCF substrate change — `contract.authoring_panel_rejection_log` and `contract.panel_output_record.verdict_payload_json` defect-code CHECK are explicitly NOT extended per D-M5-7 |
| Is not | An M2/M3/M4/M7/M8 substrate change — those gates are closed and live |

### 1.3 Source documents consumed

| Source | Role |
|---|---|
| M5 preflight (`6e46d77`) | Decision options + recommendations the operator accepted |
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority |
| MCF requirements §11.3 (Metric Authoring Panel) | Three-model workbench architecture; tool-set composition; per-agent immutable transcripts as audit artifacts |
| MCF requirements §17.1 (per-panel-run record) | Required fields on every panel run |
| MCF build plan §M5 | Substrate scope: panel_run + transcript + tool/evidence allowlists + reservoir-provenance fields per addendum guardrail #6; primary risk: workbench fingerprint algorithm spec drift |
| BCF Chapter 7 + ADR DEC-149ab2 / D411 | Cross-framework panel architecture MCF mirrors |
| M3 cert-amendment closeout (`60efd9d`) | Live `fk_mcf_cert_panel_run` → `contract.panel_output_record` precedent |
| M4 DBCP §6.7 + service spec | M4 cert writer accepts 6 panel-attestation fields; M4 stores snapshots, panel writes to `contract.panel_output_record` separately |
| M4 apply closeout (`c2bc3fc`) | M4 service live; operationally dormant pending panel |
| M7/M8 apply closeout (`6b3ffb2`) | Formula AST + hash authority live; M5 unblocks panel-attested authoring |
| Live `contract.panel_output_record` schema + CHECKs | Verified empirically: 13 columns; `stage_code` enum `(authoring/publication/lifecycle_audit)` already MCF-compatible without extension; 24 BCF rows untouched |
| Live `contract.authoring_panel_rejection_log` schema + CHECKs | Verified empirically: BCF-specific by design; M5 does NOT extend |
| Live `mcf.*` substrate (10 tables, all empty) | Verified empirically: 3 deferred panel_run_uid FKs absent on revision/PE-result/supersession; 1 live FK on certification_record |

### 1.4 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits this session | ✓ — read-only |
| No DDL applied | ✓ — DBCP designs the substrate change; apply is a separate gate |
| No MCF metric contracts created | ✓ — substrate stays empty |
| No panel runs written | ✓ — no panel exists |
| No transcripts recorded | ✓ — substrate dormant |
| No certification rows written | ✓ — M4 service operationally dormant |
| No BCF data touched | ✓ — 24 live BCF panel runs in `contract.panel_output_record` untouched; `concept_registry.*` untouched; `contract.authoring_panel_rejection_log` CHECKs untouched |
| No `contract.panel_output_record` CHECK extensions | ✓ per D-M5-7 |
| No `contract.authoring_panel_rejection_log` CHECK extensions | ✓ per D-M5-7 |
| No M9 / M10 / M11 / M12+ work | ✓ — downstream gates |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

---

## 2. Accepted operator decisions (D-M5-1..D-M5-10)

Per operator-accepted preflight recommendations (`6e46d77`):

| # | Decision | Locked |
|---|---|---|
| **D-M5-1** | ACCEPT D-M5-B hybrid composition (4 new mcf tables + 3 FK activations + mcf_v1 policy extension; NO `contract.*` CHECK extensions) | ACCEPTED |
| **D-M5-2** | `mcf.metric_authoring_panel_run` as mcf-owned run metadata table — 8 columns; `panel_run_uid PK FK → contract.panel_output_record` (1:1 composition); reservoir fields nullable until M11 populates them | ACCEPTED |
| **D-M5-3** | `mcf.metric_authoring_panel_transcript` as per-model immutable transcript table; append-only via M3-style child-immutability trigger | ACCEPTED |
| **D-M5-4** | `mcf.workspace_tool_allowlist` as versioned MCF tool registry with `effective_from` / `effective_to` (NULL = active) | ACCEPTED |
| **D-M5-5** | `mcf.evidence_source_allowlist` as versioned MCF evidence source registry (mirrors tool allowlist shape) | ACCEPTED |
| **D-M5-6** | Activate 3 deferred FKs from `mcf.metric_contract_revision`, `mcf.metric_publication_eligibility_result`, `mcf.metric_supersession` → `contract.panel_output_record(panel_run_uid)` (matches live `fk_mcf_cert_panel_run` precedent) | ACCEPTED |
| **D-M5-7** | MCF defect codes live in `mcf.metric_authoring_panel_run.consensus_payload_json` (JSON-schema validated at M12 layer); `contract.authoring_panel_rejection_log` stays BCF-specific; `contract.panel_output_record.verdict_payload_json` defect-code CHECK not extended | ACCEPTED |
| **D-M5-8** | Use M3-style append-only/immutability trigger for transcript rows (UPDATE/DELETE rejected post-insert) | ACCEPTED |
| **D-M5-9** | Extend seeded `contract.framework_policy mcf_v1.consensus_requirement_json` in-place with panel-discipline fields (workbench fingerprint algorithm + version, defect-code registry version, transcript retention, allowlist version pinning); no new policy column | ACCEPTED |
| **D-M5-10** | DEFER optional NF1 tightening; default stance is no NF1 change in M5 (panel-attestation fields on `mcf.certification_record` may still be all-NULL post-M5; production tightening is a future operator-authorized amendment) | DEFERRED — no change this DBCP |

---

## 3. Current live substrate state

### 3.1 Live state recap (after M7/M8 evidence apply at `6b3ffb2`)

After bc-core `090bc65` + bc-docs-v3 `6e46d77`:

- **10 `mcf.*` tables, all empty.** Identity-bearing parent columns on `mcf.metric_contract` carry M7/M8 hash discipline; `mcf.metric_contract_version` carries `formula_ast_canonical_json jsonb NOT NULL`.
- **M3 + M7 triggers live**: `fn_mcv_state_transition_check` (state-transition lifecycle); `fn_mcv_descriptive_immutability_check` (3-IF amended per §13.2.1 of M7/M8 DBCP).
- **M4 cert writer service live**; integration-tested 7/7 PASS; accepts 6 panel-attestation fields via `CertContextInput`.
- **M7/M8 services live**: `FormulaCanonicalizationService`, `PackageSignatureService`, `McfHashComputerCoordinator`; algorithm version `mcf-hash-v1`.
- **Panel-run column inventory** (verified empirically via bc-postgres MCP):

| Table | `panel_run_uid` column | FK status |
|---|---|---|
| `mcf.certification_record` | present | **LIVE** — `fk_mcf_cert_panel_run → contract.panel_output_record` (wired by M3 cert-amendment) |
| `mcf.metric_contract_revision` | present | **DEFERRED** — no FK |
| `mcf.metric_publication_eligibility_result` | present | **DEFERRED** — no FK |
| `mcf.metric_supersession` | present | **DEFERRED** — no FK |

- **Shared `contract.*` substrate** (BCF-shared):

| Table | Rows | MCF compatibility |
|---|---|---|
| `contract.panel_output_record` | 24 (all `stage_code='authoring'`, BCF panel runs) | Structurally MCF-compatible at column level; `stage_code` enum already admits `(authoring/publication/lifecycle_audit)`; only friction is the BCF-specific `defect_code` CHECK on `verdict_payload_json` (resolved per D-M5-7) |
| `contract.authoring_panel_rejection_log` | 1 | BCF-specific by design; M5 does NOT extend |

- **M4-seeded mcf rows** intact:
  - `contract.framework_policy` 1 row (`mcf_v1` / `1.0.0`)
  - `contract.operator_confirm_rule` 2 rows (`mcf_metric_transition_approved_to_active`, `mcf_metric_supersede_active_to_superseded`)

- **No `mcf.metric_authoring_panel_*`** tables exist. No `mcf.workspace_tool_allowlist` / `mcf.evidence_source_allowlist` tables exist.

### 3.2 Why real panel-attested authoring remains blocked

| # | Block | Resolved by |
|---|---|---|
| 1 | No `mcf.metric_authoring_panel_run` substrate → no MCF-specific panel-run record to extend the shared `contract.panel_output_record` row | M5 (this DBCP) |
| 2 | No per-model transcript substrate → no audit artifact for panel reasoning | M5 |
| 3 | No tool/evidence allowlist substrate → no governance over workbench surface | M5 |
| 4 | 3 of 4 mcf panel_run_uid columns lack FKs → cert writer's panel-attestation fields can reference unverified uuid | M5 |
| 5 | `mcf_v1` policy lacks panel-discipline fields → algorithm version + defect registry version + retention not pinned | M5 |
| 6 | No reservoir ingestion service → reservoir-provenance fields would be unpopulated even if substrate existed | M11 (downstream of M5) |
| 7 | No three-model panel implementation → no panel can run | M12 (downstream of M5 + M7 + M10 + M11) |

This DBCP resolves blocks 1-5. Blocks 6-7 are downstream gates.

---

## 4. M5 ownership boundary

### 4.1 What M5 owns

| # | Deliverable | Section |
|---|---|---|
| 1 | `mcf.metric_authoring_panel_run` table | §6 |
| 2 | `mcf.metric_authoring_panel_transcript` table + append-only trigger | §7 + §13 |
| 3 | `mcf.workspace_tool_allowlist` table | §8 |
| 4 | `mcf.evidence_source_allowlist` table | §9 |
| 5 | 3 FK activations on existing mcf.* panel_run_uid columns | §10 |
| 6 | In-place UPDATE on seeded `contract.framework_policy mcf_v1` row to extend `consensus_requirement_json` with panel-discipline fields | §11 |
| 7 | MCF defect-code registry strategy (JSON-schema validated, lives in code as TS const; registry version pinned via mcf_v1 policy field per D-M5-9) | §12 |
| 8 | Dry-run + post-apply verifier scripts | §16 + §17 |
| 9 | Rollback DDL with guard refusing if any new-table rows exist | §14.4 |

### 4.2 What M5 does NOT own

| # | Out-of-scope | Belongs to |
|---|---|---|
| 1 | Real panel run writes | M12 + operator-driven test runs |
| 2 | Transcript content generation | M12 |
| 3 | Workbench fingerprint algorithm | M12 (M5 stores the hash; algorithm spec is M12) |
| 4 | Tool-call runtime enforcement | M12 (M5 defines allowlist substrate; runtime check is M12) |
| 5 | Reservoir ingestion service | M11 (M5 defines reservoir-provenance columns; populator is M11) |
| 6 | PE-MC evaluator (PE-MC-1..PE-MC-10 verdicts) | M13 |
| 7 | Self-verification fixture substrate | M9 |
| 8 | Deterministic verifier engine | M10 |
| 9 | Publication / supersession orchestration | M14 / M15 |
| 10 | Operator console UI | M16 / M17 |
| 11 | Extending `contract.authoring_panel_rejection_log` CHECKs | NEVER per D-M5-7 |
| 12 | Extending `contract.panel_output_record.verdict_payload_json` defect-code CHECK | NEVER per D-M5-7 |
| 13 | NF1 tightening on `mcf.certification_record` | DEFERRED per D-M5-10 |
| 14 | bc-core service code | This DBCP is substrate-only; service code (if any) ships in a separate gate alongside M11 / M12 |

---

## 5. Shared `contract.panel_output_record` composition model

### 5.1 The 1:1 PK FK composition

Per D-M5-2, `mcf.metric_authoring_panel_run.panel_run_uid` is BOTH the primary key AND a foreign key to `contract.panel_output_record(panel_run_uid)`. This is a true 1:1 composition: every MCF panel run has exactly one row in each table, and the same UUID identifies the run across both schemas.

```
contract.panel_output_record                      mcf.metric_authoring_panel_run
┌────────────────────────────┐                    ┌──────────────────────────────────────────┐
│ panel_run_uid PK           │ ◄──────── 1:1 ────►│ panel_run_uid PK FK → contract.panel...  │
│ stage_code                 │                    │ workbench_fingerprint_hash               │
│ prompt_version             │                    │ consensus_payload_json                   │
│ model_identity_json        │                    │ reservoir_name (nullable until M11)      │
│ agent_outputs_json         │                    │ reservoir_entry_id (nullable until M11)  │
│ input_hash                 │                    │ reservoir_provenance_source_json (..nul..)│
│ verdict_code               │                    │ reservoir_confidence_band (..nullable..) │
│ verdict_payload_json       │                    │ created_at                               │
│ grounding_check_result     │                    └──────────────────────────────────────────┘
│ quarantined                │                                       │
│ sampling_status            │                                       │
│ policy_version             │                                       │ 1:N
│ created_at                 │                                       ▼
└────────────────────────────┘                    ┌──────────────────────────────────────────┐
            ▲                                     │ mcf.metric_authoring_panel_transcript    │
            │ FK (4 paths after M5)               │ transcript_uid PK                        │
            │                                     │ panel_run_uid FK → mcf.metric_author...  │
   ┌────────┴─────────────────────────┐           │ model_role_code (maker/checker/moderator)│
   │ mcf.certification_record         │           │ model_identity_json                      │
   │ mcf.metric_contract_revision     │           │ transcript_payload_json (append-only)    │
   │ mcf.metric_publication_eligibili │           │ created_at                               │
   │ mcf.metric_supersession          │           └──────────────────────────────────────────┘
   └──────────────────────────────────┘
```

### 5.2 Why composition, not extension

Rationale for choosing 1:1 composition over (a) extending `contract.panel_output_record` with MCF columns or (b) creating a fully-parallel mcf-owned panel-run table:

- **(a) Extension rejected** because adding MCF-specific columns (workbench fingerprint, reservoir-provenance) to the shared `contract.panel_output_record` violates the per-framework substrate boundary (per ADR DEC-149ab2 §3) and pollutes BCF's substrate with MCF-specific fields that BCF panel runs would have to write as NULL.
- **(b) Parallel rejected** because creating `mcf.metric_authoring_panel_run` with its own UUID generation would split panel-run identity across two namespaces (BCF runs identified by `contract.panel_output_record.panel_run_uid`; MCF runs identified by `mcf.metric_authoring_panel_run.panel_run_uid`) — cross-framework analytics would require schema-aware unioning. The 1:1 composition keeps a single canonical panel-run identity (`contract.panel_output_record.panel_run_uid`) used uniformly across frameworks.

### 5.3 Insert ordering

For an MCF panel run, the insert ordering is:

1. Panel writes `contract.panel_output_record` row (canonical run identity established)
2. Panel writes `mcf.metric_authoring_panel_run` row (MCF-specific extension; PK FK to `contract.panel_output_record` enforced)
3. Panel writes N (typically 3) `mcf.metric_authoring_panel_transcript` rows (per-model transcripts; FK to **`mcf.metric_authoring_panel_run(panel_run_uid)`** enforced per M-M5-1 patch; append-only thereafter)

The FK on `mcf.metric_authoring_panel_run.panel_run_uid` ensures step 2 fails if step 1 was skipped. The FK on `mcf.metric_authoring_panel_transcript.panel_run_uid` ensures step 3 fails if step 2 was skipped (substrate-enforced MCF-only attachment — transcripts cannot orphan to BCF or other non-MCF panel runs). The full chain is substrate-enforced; partial writes at any layer are rejected by referential integrity.

### 5.3.1 Why transcript FK targets `mcf.metric_authoring_panel_run` (per M-M5-1 patch)

Originally drafted with `mcf.metric_authoring_panel_transcript.panel_run_uid → contract.panel_output_record(panel_run_uid)` for symmetry with the other 3 deferred FKs (revision / PE-result / supersession all point to the shared `contract.panel_output_record` per §10). Review found this allowed orphan transcripts attached to BCF or non-MCF panel runs (FK satisfied by the shared row's existence, even with no `mcf.metric_authoring_panel_run` row). The MCF transcript table is unambiguously MCF-specific (model_role_code enum from MCF §11.3 three-model architecture; transcript_payload_json shape per MCF §11.3.5).

**Resolution per M-M5-1:** Retarget the transcript FK to `mcf.metric_authoring_panel_run(panel_run_uid)`. This preserves the D-M5-B hybrid composition model (the MCF-specific extension row is still 1:1 with `contract.panel_output_record`) while pushing MCF-ownership enforcement DOWN to the substrate. Insert chain becomes serial: panel runs MUST cross the contract → mapr → mapt boundary in order; the substrate rejects any insertion that skips a layer. The other 3 deferred FKs (revision / PE-result / supersession) keep their targets on `contract.panel_output_record` per §10 because those tables carry primary MC identity (their panel_run_uid is an attestation reference, not an ownership claim).

### 5.4 Stage-code semantics for MCF

`contract.panel_output_record.stage_code` CHECK admits `(authoring, publication, lifecycle_audit)`. MCF panel-run rows MUST use one of:

| `stage_code` | MCF meaning |
|---|---|
| `authoring` | Metric Authoring Panel run during intake → draft (M12 will write these) |
| `publication` | PE-MC re-evaluation run during approveForActivation (M13 will write these) |
| `lifecycle_audit` | Periodic re-audit of an active MC under operator-initiated re-evaluation (future gate) |

No CHECK extension needed; values are already admitted.

---

## 6. New table design: `mcf.metric_authoring_panel_run`

### 6.1 Purpose

The mcf-owned 1:1 extension of `contract.panel_output_record` for MCF-specific panel-run fields. Holds workbench fingerprint hash (the proof that all 3 models worked in the same governed workspace), consensus payload (per-model verdicts + consensus result + MCF defect codes if rejected), and reservoir-provenance fields (per addendum guardrail #6, populated by M11 ingestion).

### 6.2 Column inventory (8 columns)

| Column | Type | NULL | Default | Notes |
|---|---|---|---|---|
| `panel_run_uid` | `uuid` | NOT NULL | — | PRIMARY KEY + FK to `contract.panel_output_record(panel_run_uid)` ON DELETE RESTRICT |
| `workbench_fingerprint_hash` | `text` | NOT NULL | — | Format `sha256:<64hex>` enforced by CHECK; algorithm version pinned in `mcf_v1.consensus_requirement_json.workbench_fingerprint_algorithm_version` |
| `consensus_payload_json` | `jsonb` | NOT NULL | `'{}'::jsonb` | Holds per-model verdicts + consensus result + MCF defect codes (if `verdict_code='REJECT_*'`); JSON schema validated at M12 layer; registry version pinned in `mcf_v1.consensus_requirement_json.defect_code_registry_version` |
| `reservoir_name` | `text` | NULL allowed | — | Populated by M11 ingestion; NULL until M11 ships (or for substrate-internal exercises) |
| `reservoir_entry_id` | `text` | NULL allowed | — | Populated by M11 ingestion |
| `reservoir_provenance_source_json` | `jsonb` | NULL allowed | — | Populated by M11 ingestion; JSON-schema validated at M11 layer |
| `reservoir_confidence_band` | `text` | NULL allowed | — | CHECK `IN ('high','medium','low')` when not NULL; populated by M11 ingestion |
| `created_at` | `timestamptz` | NOT NULL | `now()` | Audit |

### 6.3 Constraint inventory

| Constraint | Type | Definition |
|---|---|---|
| `mapr_pkey` | PRIMARY KEY | `(panel_run_uid)` |
| `fk_mapr_panel_run` | FOREIGN KEY | `panel_run_uid` → `contract.panel_output_record(panel_run_uid)` ON DELETE RESTRICT |
| `mapr_workbench_fp_hash_fmt_chk` | CHECK | `workbench_fingerprint_hash ~ '^sha256:[0-9a-f]{64}$'` |
| `mapr_reservoir_confidence_band_chk` | CHECK | `reservoir_confidence_band IS NULL OR reservoir_confidence_band IN ('high','medium','low')` |
| `mapr_reservoir_all_or_none_chk` | CHECK | The 4 reservoir-provenance fields (reservoir_name, reservoir_entry_id, reservoir_provenance_source_json, reservoir_confidence_band) MUST be all-NULL OR all-non-NULL. Mirrors the M4 NF1 panel-attestation all-or-none discipline. Pre-M11 reality: all-NULL. Post-M11 production reality: all-non-NULL. |

### 6.4 Index inventory

| Index | Definition | Purpose |
|---|---|---|
| `idx_mcf_mapr_created_at` | `(created_at DESC)` | Recent panel runs lookup for operator console |
| `idx_mcf_mapr_reservoir_name` | `(reservoir_name) WHERE reservoir_name IS NOT NULL` | Partial index for reservoir-attributed runs (M11 will benefit) |

### 6.5 DDL

```sql
CREATE TABLE mcf.metric_authoring_panel_run (
  panel_run_uid                       uuid NOT NULL PRIMARY KEY,
  workbench_fingerprint_hash          text NOT NULL,
  consensus_payload_json              jsonb NOT NULL DEFAULT '{}'::jsonb,
  reservoir_name                      text,
  reservoir_entry_id                  text,
  reservoir_provenance_source_json    jsonb,
  reservoir_confidence_band           text,
  created_at                          timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT fk_mapr_panel_run
    FOREIGN KEY (panel_run_uid)
    REFERENCES contract.panel_output_record(panel_run_uid)
    ON DELETE RESTRICT,
  CONSTRAINT mapr_workbench_fp_hash_fmt_chk
    CHECK (workbench_fingerprint_hash ~ '^sha256:[0-9a-f]{64}$'),
  CONSTRAINT mapr_reservoir_confidence_band_chk
    CHECK (reservoir_confidence_band IS NULL OR reservoir_confidence_band IN ('high','medium','low')),
  CONSTRAINT mapr_reservoir_all_or_none_chk
    CHECK (
      (reservoir_name IS NULL AND reservoir_entry_id IS NULL AND
       reservoir_provenance_source_json IS NULL AND reservoir_confidence_band IS NULL)
      OR
      (reservoir_name IS NOT NULL AND reservoir_entry_id IS NOT NULL AND
       reservoir_provenance_source_json IS NOT NULL AND reservoir_confidence_band IS NOT NULL)
    )
);

CREATE INDEX idx_mcf_mapr_created_at
  ON mcf.metric_authoring_panel_run (created_at DESC);

CREATE INDEX idx_mcf_mapr_reservoir_name
  ON mcf.metric_authoring_panel_run (reservoir_name)
  WHERE reservoir_name IS NOT NULL;

COMMENT ON TABLE mcf.metric_authoring_panel_run IS
  'MCF-specific 1:1 extension of contract.panel_output_record per DBCP M5 §6 + D-M5-2. Holds workbench fingerprint hash (per MCF §11.3 / build plan §M5; algorithm spec is M12 — substrate stores hash only), consensus payload (per-model verdicts + MCF defect codes if rejected, JSON-schema validated at M12 per D-M5-7), and reservoir-provenance fields per addendum guardrail #6 (nullable until M11 ingestion populates them; all-or-none enforced post-population). panel_run_uid is both PK and FK to contract.panel_output_record — same identity across both tables; insert ordering requires shared row first.';
```

### 6.6 Ownership

`MetricAuthoringPanelRunWriterService` (future M12 service; NOT in M5 scope). M5 ships the substrate; service code that writes rows ships with M12 (or with M11 if reservoir-only rows are written by ingestion).

---

## 7. New table design: `mcf.metric_authoring_panel_transcript`

### 7.1 Purpose

Per-model immutable interactive transcript per build plan §M5 + MCF §11.3 (per-agent immutable interactive transcripts as audit artifacts). Typically 3 rows per panel run (Maker / Checker / Moderator). Append-only via M3-style trigger per D-M5-8.

### 7.2 Column inventory (6 columns)

| Column | Type | NULL | Default | Notes |
|---|---|---|---|---|
| `transcript_uid` | `uuid` | NOT NULL | `gen_random_uuid()` | PRIMARY KEY |
| `panel_run_uid` | `uuid` | NOT NULL | — | FK to `mcf.metric_authoring_panel_run(panel_run_uid)` ON DELETE RESTRICT (per M-M5-1 patch — substrate-enforced MCF-only attachment; see §5.3.1) |
| `model_role_code` | `text` | NOT NULL | — | CHECK `IN ('maker','checker','moderator')` per MCF §11.3 three-model architecture |
| `model_identity_json` | `jsonb` | NOT NULL | — | Vendor + model + revision identity for this specific agent run; sub-shape per M12 |
| `transcript_payload_json` | `jsonb` | NOT NULL | — | Tool calls + responses + reasoning + verdict for this agent. Append-only post-insert per §13 trigger. |
| `created_at` | `timestamptz` | NOT NULL | `now()` | Audit |

### 7.3 Constraint inventory

| Constraint | Type | Definition |
|---|---|---|
| `mapt_pkey` | PRIMARY KEY | `(transcript_uid)` |
| `fk_mapt_panel_run` | FOREIGN KEY | `panel_run_uid` → `mcf.metric_authoring_panel_run(panel_run_uid)` ON DELETE RESTRICT (per M-M5-1 patch — was `contract.panel_output_record`; retargeted to enforce MCF-only attachment per §5.3.1) |
| `mapt_model_role_chk` | CHECK | `model_role_code IN ('maker','checker','moderator')` |
| `uq_mapt_run_role` | UNIQUE | `(panel_run_uid, model_role_code)` — at most one transcript per (run, role) |

### 7.4 Index inventory

| Index | Definition | Purpose |
|---|---|---|
| `idx_mcf_mapt_panel_run` | `(panel_run_uid)` | Lookup all transcripts for a panel run (typically 3) |

(`uq_mapt_run_role` already provides the (panel_run_uid, model_role_code) lookup path.)

### 7.5 DDL

```sql
CREATE TABLE mcf.metric_authoring_panel_transcript (
  transcript_uid           uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
  panel_run_uid            uuid NOT NULL,
  model_role_code          text NOT NULL,
  model_identity_json      jsonb NOT NULL,
  transcript_payload_json  jsonb NOT NULL,
  created_at               timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT fk_mapt_panel_run
    FOREIGN KEY (panel_run_uid)
    REFERENCES mcf.metric_authoring_panel_run(panel_run_uid)
    ON DELETE RESTRICT,
  CONSTRAINT mapt_model_role_chk
    CHECK (model_role_code IN ('maker','checker','moderator')),
  CONSTRAINT uq_mapt_run_role
    UNIQUE (panel_run_uid, model_role_code)
);

CREATE INDEX idx_mcf_mapt_panel_run
  ON mcf.metric_authoring_panel_transcript (panel_run_uid);

COMMENT ON TABLE mcf.metric_authoring_panel_transcript IS
  'Per-model immutable interactive transcript per DBCP M5 §7 + D-M5-3 + MCF §11.3 (per-agent immutable transcripts as audit artifacts). Typically 3 rows per panel run (Maker/Checker/Moderator). FK target is mcf.metric_authoring_panel_run(panel_run_uid) — NOT contract.panel_output_record — per M-M5-1 patch: this substrate-enforces MCF-only attachment, blocking transcript rows from orphaning to BCF or other non-MCF panel runs (see DBCP §5.3.1). UNIQUE (panel_run_uid, model_role_code) enforces at-most-one transcript per (run, role). Append-only post-insert via trigger fn_mapt_immutability_check per §13 (UPDATE/DELETE rejected once the row exists; mirrors mcf.fn_mvb_active_immutability_check pattern). Substrate-enforced; not service-side.';
```

### 7.6 Append-only trigger

See §13 for the trigger function `mcf.fn_mapt_immutability_check` and its attachment.

### 7.7 Ownership

`MetricAuthoringPanelTranscriptWriterService` (future M12 service; NOT in M5 scope).

---

## 8. New table design: `mcf.workspace_tool_allowlist`

### 8.1 Purpose

Versioned registry of MCF-specific tools the Metric Authoring Panel may call during the workbench session. Per MCF §11.3.3 (tool-set composition is MCF's only divergence from BCF). Examples (illustrative; specific tool list is M12's responsibility):

- `bcf_registry_search` — query the BCF Registry for variable candidates
- `ast_validity_probe` — check if a candidate AST is well-formed (uses M7 service)
- `grain_reachability_check` — confirm the grain entity is reachable from the bound variables
- `fiscal_calendar_resolve` — resolve a fiscal-period anchor against the tenant calendar
- `mls_readiness_probe` — check tenant Metric Lifecycle State readiness

M5 ships the substrate; the specific tool list at v1 is M12.

### 8.2 Column inventory (6 columns)

| Column | Type | NULL | Default | Notes |
|---|---|---|---|---|
| `tool_uid` | `uuid` | NOT NULL | `gen_random_uuid()` | PRIMARY KEY |
| `tool_code` | `text` | NOT NULL | — | Stable identifier (e.g. `bcf_registry_search`) |
| `tool_version` | `text` | NOT NULL | — | Semver-like (e.g. `1.0.0`) |
| `effective_from` | `timestamptz` | NOT NULL | `now()` | When this tool version becomes admissible |
| `effective_to` | `timestamptz` | NULL allowed | — | When this tool version is retired; NULL = currently active |
| `tool_metadata_json` | `jsonb` | NULL allowed | — | M12-specific metadata (tool input/output schema reference, etc.) |

### 8.3 Constraint inventory

| Constraint | Type | Definition |
|---|---|---|
| `mwta_pkey` | PRIMARY KEY | `(tool_uid)` |
| `mwta_effective_to_chk` | CHECK | `effective_to IS NULL OR effective_to > effective_from` |
| `mwta_active_per_code_uniq` | UNIQUE INDEX (partial) | `(tool_code) WHERE effective_to IS NULL` — at most one currently-active version per tool_code |
| `mwta_version_per_code_uniq` | UNIQUE INDEX | `(tool_code, tool_version)` — each (code, version) pair appears once |

### 8.4 Index inventory

| Index | Definition | Purpose |
|---|---|---|
| `idx_mcf_mwta_code_active` | `(tool_code) WHERE effective_to IS NULL` | Quick lookup of currently-active tool versions |

(`mwta_active_per_code_uniq` doubles as this index.)

### 8.5 DDL

```sql
CREATE TABLE mcf.workspace_tool_allowlist (
  tool_uid             uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
  tool_code            text NOT NULL,
  tool_version         text NOT NULL,
  effective_from       timestamptz NOT NULL DEFAULT now(),
  effective_to         timestamptz,
  tool_metadata_json   jsonb,
  CONSTRAINT mwta_effective_to_chk
    CHECK (effective_to IS NULL OR effective_to > effective_from)
);

CREATE UNIQUE INDEX mwta_active_per_code_uniq
  ON mcf.workspace_tool_allowlist (tool_code)
  WHERE effective_to IS NULL;

CREATE UNIQUE INDEX mwta_version_per_code_uniq
  ON mcf.workspace_tool_allowlist (tool_code, tool_version);

COMMENT ON TABLE mcf.workspace_tool_allowlist IS
  'Versioned MCF workbench tool allowlist per DBCP M5 §8 + D-M5-4 + MCF §11.3.3 (tool-set composition is MCFs only divergence from BCF). Effective_from / effective_to model standard temporal pattern (NULL effective_to = active). Partial UNIQUE on (tool_code) WHERE effective_to IS NULL guarantees at-most-one active version per tool_code. M12 will reference rows by tool_uid (or tool_code + active-at-time-of-run) to enforce panel tool-call discipline at runtime; substrate-enforced version pinning per policy.';
```

### 8.6 Ownership

`WorkspaceToolAllowlistService` (future; NOT in M5 scope). M5 ships the substrate; seed rows for v1 tool registry are deferred to M12 (or a tiny seed PR co-located with M12).

---

## 9. New table design: `mcf.evidence_source_allowlist`

### 9.1 Purpose

Versioned registry of MCF-specific evidence sources the Metric Authoring Panel may cite for grounding per MCF §11.3.1. Examples (illustrative):

- IFRS / GAAP standards
- Industry reference documents
- Operator-provided business context (per-tenant)
- Internal working papers

M5 ships the substrate; the specific source list at v1 is M12.

### 9.2 Column inventory (6 columns)

| Column | Type | NULL | Default | Notes |
|---|---|---|---|---|
| `evidence_source_uid` | `uuid` | NOT NULL | `gen_random_uuid()` | PRIMARY KEY |
| `source_code` | `text` | NOT NULL | — | Stable identifier (e.g. `ifrs_15`) |
| `source_version` | `text` | NOT NULL | — | Source version (e.g. `2018-amendment`) |
| `effective_from` | `timestamptz` | NOT NULL | `now()` | When this source version becomes admissible |
| `effective_to` | `timestamptz` | NULL allowed | — | When this source version is retired; NULL = currently active |
| `source_metadata_json` | `jsonb` | NULL allowed | — | M12-specific metadata (URL, citation format, etc.) |

### 9.3 Constraint inventory

| Constraint | Type | Definition |
|---|---|---|
| `mesa_pkey` | PRIMARY KEY | `(evidence_source_uid)` |
| `mesa_effective_to_chk` | CHECK | `effective_to IS NULL OR effective_to > effective_from` |
| `mesa_active_per_code_uniq` | UNIQUE INDEX (partial) | `(source_code) WHERE effective_to IS NULL` |
| `mesa_version_per_code_uniq` | UNIQUE INDEX | `(source_code, source_version)` |

### 9.4 DDL

```sql
CREATE TABLE mcf.evidence_source_allowlist (
  evidence_source_uid    uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
  source_code            text NOT NULL,
  source_version         text NOT NULL,
  effective_from         timestamptz NOT NULL DEFAULT now(),
  effective_to           timestamptz,
  source_metadata_json   jsonb,
  CONSTRAINT mesa_effective_to_chk
    CHECK (effective_to IS NULL OR effective_to > effective_from)
);

CREATE UNIQUE INDEX mesa_active_per_code_uniq
  ON mcf.evidence_source_allowlist (source_code)
  WHERE effective_to IS NULL;

CREATE UNIQUE INDEX mesa_version_per_code_uniq
  ON mcf.evidence_source_allowlist (source_code, source_version);

COMMENT ON TABLE mcf.evidence_source_allowlist IS
  'Versioned MCF evidence source allowlist per DBCP M5 §9 + D-M5-5 + MCF §11.3.1 (panel grounding sources). Mirrors workspace_tool_allowlist shape — same temporal + active-per-code-uniqueness discipline. M12 will reference rows to enforce panel claim-grounding discipline (every cited claim must trace to an active source in this allowlist at the time of the run).';
```

### 9.5 Ownership

`EvidenceSourceAllowlistService` (future; NOT in M5 scope).

---

## 10. Three deferred FK activations

### 10.1 Targets

All 3 FKs target `contract.panel_output_record(panel_run_uid)`, matching the live `fk_mcf_cert_panel_run` precedent.

| Source table | Column | FK name | ON DELETE |
|---|---|---|---|
| `mcf.metric_contract_revision` | `panel_run_uid` | `fk_mcr_panel_run` | RESTRICT |
| `mcf.metric_publication_eligibility_result` | `panel_run_uid` | `fk_mper_panel_run` | RESTRICT |
| `mcf.metric_supersession` | `panel_run_uid` | `fk_mcs_panel_run` | RESTRICT |

### 10.2 DDL

```sql
ALTER TABLE mcf.metric_contract_revision
  ADD CONSTRAINT fk_mcr_panel_run
  FOREIGN KEY (panel_run_uid)
  REFERENCES contract.panel_output_record(panel_run_uid)
  ON DELETE RESTRICT;

ALTER TABLE mcf.metric_publication_eligibility_result
  ADD CONSTRAINT fk_mper_panel_run
  FOREIGN KEY (panel_run_uid)
  REFERENCES contract.panel_output_record(panel_run_uid)
  ON DELETE RESTRICT;

ALTER TABLE mcf.metric_supersession
  ADD CONSTRAINT fk_mcs_panel_run
  FOREIGN KEY (panel_run_uid)
  REFERENCES contract.panel_output_record(panel_run_uid)
  ON DELETE RESTRICT;
```

### 10.3 Safety of activation on empty tables

All 3 source tables are empty (verified empirically). FK activation on an empty table is metadata-only — no existing row needs to be validated. The constraints take effect at the next INSERT (none expected this DBCP).

### 10.4 Post-M5 FK landscape

After M5 apply, all 4 mcf.* `panel_run_uid` columns FK to `contract.panel_output_record(panel_run_uid)`:

| Source table | FK | Constraint name |
|---|---|---|
| `mcf.certification_record` | `panel_run_uid → contract.panel_output_record` | `fk_mcf_cert_panel_run` (live since M3 cert-amendment) |
| `mcf.metric_contract_revision` | `panel_run_uid → contract.panel_output_record` | `fk_mcr_panel_run` (M5) |
| `mcf.metric_publication_eligibility_result` | `panel_run_uid → contract.panel_output_record` | `fk_mper_panel_run` (M5) |
| `mcf.metric_supersession` | `panel_run_uid → contract.panel_output_record` | `fk_mcs_panel_run` (M5) |

Consistent canonical panel-run identity across the entire MCF substrate post-apply.

---

## 11. `mcf_v1.consensus_requirement_json` extension

### 11.1 Pre-extension shape

M4 seeded `contract.framework_policy mcf_v1 / 1.0.0` with:

```json
{
  "models_required": 3,
  "agreement_threshold": 2,
  "models": ["maker","checker","moderator"]
}
```

### 11.2 Post-extension shape (M5)

```json
{
  "models_required": 3,
  "agreement_threshold": 2,
  "models": ["maker","checker","moderator"],
  "panel_discipline": {
    "workbench_fingerprint_algorithm_name": "mcf-workbench-fp",
    "workbench_fingerprint_algorithm_version": "v1",
    "defect_code_registry_version": "v1",
    "transcript_retention_policy": {
      "retention_mode": "indefinite",
      "retention_rationale": "Per MCF §11.3 + Invariant V — per-agent transcripts are immutable authoring records used by audit; never deleted."
    },
    "allowlist_version_pinning": {
      "tool_allowlist_mode": "active_at_run_time",
      "evidence_source_allowlist_mode": "active_at_run_time",
      "rationale": "Panel runs pin against the active version of each allowlist at panel-open time. M12 enforces tool/source membership against versions active at run.created_at."
    }
  }
}
```

### 11.3 In-place UPDATE DDL

```sql
UPDATE contract.framework_policy
SET consensus_requirement_json = consensus_requirement_json || '{
  "panel_discipline": {
    "workbench_fingerprint_algorithm_name": "mcf-workbench-fp",
    "workbench_fingerprint_algorithm_version": "v1",
    "defect_code_registry_version": "v1",
    "transcript_retention_policy": {
      "retention_mode": "indefinite",
      "retention_rationale": "Per MCF §11.3 + Invariant V — per-agent transcripts are immutable authoring records used by audit; never deleted."
    },
    "allowlist_version_pinning": {
      "tool_allowlist_mode": "active_at_run_time",
      "evidence_source_allowlist_mode": "active_at_run_time",
      "rationale": "Panel runs pin against the active version of each allowlist at panel-open time. M12 enforces tool/source membership against versions active at run.created_at."
    }
  }
}'::jsonb
WHERE policy_uid = 'mcf_v1' AND policy_version = '1.0.0';
```

### 11.4 Why in-place vs new policy version

Per D-M5-9: in-place UPDATE because:
- The seeded `mcf_v1 / 1.0.0` is the active mcf policy (`effective_to IS NULL`); replacing it with `1.0.1` would create temporal coverage gap or require split-second cutover
- The new fields are additive metadata, not breaking semantics — JSONB-merge (`||`) preserves existing keys, adds new ones
- No referencing rows yet (substrate empty), so policy mutation has no downstream impact
- A future material change to the panel-discipline policy WOULD warrant a new policy version (mcf_v2 / 2.0.0) — this DBCP adds the initial metadata only

### 11.5 Regression assertion

Post-apply verifier (§17) asserts:
- `consensus_requirement_json->'models_required' = '3'::jsonb` (preserved)
- `consensus_requirement_json->'agreement_threshold' = '2'::jsonb` (preserved)
- `consensus_requirement_json->'models'` array contains all 3 of `['maker','checker','moderator']` (preserved)
- `consensus_requirement_json->'panel_discipline'->>'workbench_fingerprint_algorithm_name' = 'mcf-workbench-fp'` (added)
- `consensus_requirement_json->'panel_discipline'->>'workbench_fingerprint_algorithm_version' = 'v1'` (added)
- `consensus_requirement_json->'panel_discipline'->>'defect_code_registry_version' = 'v1'` (added)

---

## 12. Defect-code registry and consensus payload schema

### 12.1 MCF defect code taxonomy (v1)

Per MCF requirements §13 + §11.3.4, the MCF defect codes (illustrative v1 set; final canonical list is M12's authority):

| Code | Triggered when |
|---|---|
| `MC_DEFECT_PLACEHOLDER_AST` | Formula AST is the literal `kind='placeholder'` (caught at M4 service guard per M7/M8 §12.5.1, but panel can also surface it) |
| `MC_DEFECT_IDENTITY_COLLISION` | Identity tuple matches an existing active MC (panel advisory; substrate is the decider per requirements §4.2) |
| `MC_DEFECT_AST_INVALID` | Formula AST fails v1 taxonomy / forbidden patterns / type promotion (panel surfaces the InvalidAstError from M7) |
| `MC_DEFECT_UNGROUNDED_CLAIM` | Panel made a claim without tracing to an allowed evidence source |
| `MC_DEFECT_BINDING_UNRESOLVED` | A `variable_ref.role` has no corresponding `metric_variable_binding` row |
| `MC_DEFECT_GRAIN_UNREACHABLE` | The grain entity is not reachable from any bound variable |
| `MC_DEFECT_TEMPORAL_GATE_INCOMPATIBLE` | The temporal gate shape does not admit the formula's time-anchor structure |
| `MC_DEFECT_RESERVOIR_PROVENANCE_MISSING` | Reservoir-attributed run lacks one or more reservoir-provenance fields (post-M11 production stance) |
| `MC_DEFECT_FIXTURE_FAILED` | M9 self-verification fixture binding failed at panel-time |

### 12.2 Consensus payload JSON schema (v1)

The `mcf.metric_authoring_panel_run.consensus_payload_json` is validated at the M12 panel-service layer against this schema (deferred to M12 implementation; M5 substrate stores the JSONB without column-level schema enforcement):

```typescript
// Stored in bc-core/src/registry/mcf/metric-authoring-panel.types.ts (M12 deliverable; NOT in M5)
interface ConsensusPayload {
  // Per-model verdicts (length matches mcf_v1.consensus_requirement_json.models_required)
  per_model_verdicts: Array<{
    model_role_code: 'maker' | 'checker' | 'moderator';
    verdict_code: 'APPROVE_FOR_DRAFT' | 'OPERATOR_REVIEW' | 'REJECT_DEFECT';
    defect_codes: string[]; // Empty unless verdict_code === 'REJECT_DEFECT'; values from MCF defect taxonomy
    confidence_score?: number; // 0..1 optional
  }>;

  // Consensus computation result
  consensus: {
    verdict_code: 'APPROVE_FOR_DRAFT' | 'OPERATOR_REVIEW' | 'REJECT_DEFECT';
    consensus_method: 'unanimous' | 'majority' | 'moderator_resolved';
    rationale_text: string; // ≥40 chars per existing operator-confirm rationale discipline
  };

  // Grounding check (per MCF §11.3.6)
  grounding: {
    claims_total: number;
    claims_grounded: number;
    claims_quarantined: number; // Should equal grounding_check_result='quarantined' on the contract.panel_output_record row
  };
}
```

### 12.3 Registry versioning

The defect-code registry version is pinned in `mcf_v1.consensus_requirement_json.panel_discipline.defect_code_registry_version` (set to `'v1'` by this DBCP per §11.2). A future taxonomy change requires:

1. New defect-code TS const (e.g. `MCF_DEFECT_REGISTRY_V2`)
2. New `mcf_v1` policy version (e.g. `1.0.1`) with `defect_code_registry_version: 'v2'` OR new policy `mcf_v2`
3. Migration plan for in-flight panel runs (per the same algorithm-version discipline as M7/M8 §12.4)

### 12.4 Why JSON-schema vs column-level CHECK

Per D-M5-7: MCF defect codes are JSON-schema validated at the M12 layer (NOT a Postgres column CHECK) because:

- The defect-code set is operator-extensible per release; substrate-level CHECK enums force a DDL change per new code
- The taxonomy lives in code (TS const) co-located with the panel logic that emits the codes
- Substrate enforces structural integrity (`consensus_payload_json jsonb NOT NULL`) but not semantic content — the panel service is the authority
- This mirrors how M7/M8 enforces formula AST shape at the service layer (per `validateAndNormalizeAst`) rather than via a Postgres JSON-schema CHECK

The trade-off: defect-code violations are only caught at panel run time, not at INSERT time. The mitigation: M5 substrate never sees a real panel run until M12 ships; substrate-internal exercises (the synthetic-row tests in the post-apply verifier) use minimal `'{}'::jsonb` payloads that pass trivially.

---

## 13. Transcript immutability / append-only trigger design

### 13.1 Pattern source

Mirrors the M3 child-immutability trigger pattern (e.g. `mcf.fn_mvb_active_immutability_check` for `metric_variable_binding`). Per D-M5-8: UPDATE/DELETE on `mcf.metric_authoring_panel_transcript` rows is rejected once the row exists, ensuring per-agent transcripts are immutable per MCF §11.3 + Invariant V.

### 13.2 Trigger function

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mapt_immutability_check()
RETURNS TRIGGER AS $$
BEGIN
  -- Per DBCP M5 §13.2 + D-M5-8 + MCF §11.3 + Invariant V:
  -- per-agent transcripts are immutable authoring records used by audit.
  -- UPDATE and DELETE are rejected unconditionally once the row exists.
  --
  -- This is stricter than mcf.fn_mvb_active_immutability_check (which permits
  -- mutation while the parent MCV is in draft state) because transcript rows
  -- are immutable from the moment of insert — there is no panel-run state
  -- transition that should ever permit transcript mutation.
  IF TG_OP = 'UPDATE' THEN
    RAISE EXCEPTION 'mcf.metric_authoring_panel_transcript transcript_uid=% is immutable; UPDATE rejected (per DBCP M5 §13 + Invariant V)', OLD.transcript_uid
      USING ERRCODE = 'check_violation';
  END IF;
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'mcf.metric_authoring_panel_transcript transcript_uid=% is immutable; DELETE rejected (per DBCP M5 §13 + Invariant V)', OLD.transcript_uid
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

### 13.3 Trigger attachment

```sql
CREATE TRIGGER trg_mapt_immutability
BEFORE UPDATE OR DELETE ON mcf.metric_authoring_panel_transcript
FOR EACH ROW EXECUTE FUNCTION mcf.fn_mapt_immutability_check();
```

### 13.4 What about TRUNCATE?

TRUNCATE bypasses row-level triggers but requires explicit ALTER TABLE permissions and is not part of normal application code paths. Defense in depth: production-DB role grants must not include TRUNCATE on `mcf.metric_authoring_panel_transcript` (deferred to operational policy; not a substrate concern).

### 13.5 Behavioral verification (in §17)

Post-apply verifier exercises:
- INSERT a synthetic transcript row → succeeds
- UPDATE the same row → rejected with the expected error message
- DELETE the same row → rejected with the expected error message
- INSERT a second row with the same `(panel_run_uid, model_role_code)` → rejected by `uq_mapt_run_role` UNIQUE (not by trigger; UNIQUE fires first)

All exercises wrapped in `BEGIN; ... ROLLBACK;` so the substrate remains empty after the verifier completes.

---

## 14. DDL apply sequence and rollback story

### 14.1 Forward DDL file

`bc-core/docker/redesign/08-mcf-panel-substrate.sql` (single file; whole-file `BEGIN/COMMIT` wrapper per the M3-cert-amendment + M7/M8 atomic-DDL pattern).

### 14.2 Apply sequence (single transaction)

```sql
BEGIN;

-- Step 1: CREATE 4 new tables
CREATE TABLE mcf.metric_authoring_panel_run (...);
CREATE TABLE mcf.metric_authoring_panel_transcript (...);
CREATE TABLE mcf.workspace_tool_allowlist (...);
CREATE TABLE mcf.evidence_source_allowlist (...);

-- Step 2: CREATE indexes on the 4 new tables — 7 statements total
-- (3 `CREATE INDEX` from §6.5 + §7.5; 4 `CREATE UNIQUE INDEX` from §8.5 + §9.4)
-- (Per M-M5-2 patch — corrected from earlier "6 indexes total" mis-count.)
CREATE INDEX ... (×3)
CREATE UNIQUE INDEX ... (×4)

-- Step 3: CREATE trigger function + attach trigger
CREATE OR REPLACE FUNCTION mcf.fn_mapt_immutability_check() ...
CREATE TRIGGER trg_mapt_immutability ...

-- Step 4: 3 FK activations
ALTER TABLE mcf.metric_contract_revision ADD CONSTRAINT fk_mcr_panel_run ...
ALTER TABLE mcf.metric_publication_eligibility_result ADD CONSTRAINT fk_mper_panel_run ...
ALTER TABLE mcf.metric_supersession ADD CONSTRAINT fk_mcs_panel_run ...

-- Step 5: In-place UPDATE on mcf_v1 policy
UPDATE contract.framework_policy SET consensus_requirement_json = ... WHERE ...

-- Step 6: COMMENT annotations on the 4 new tables

COMMIT;
```

### 14.3 Atomicity rationale

All 6 steps commit together or roll back together. A partial apply would leave the substrate in an inconsistent state:
- New tables created but the 3 FK activations skipped → asymmetric FK enforcement across the 4 mcf panel_run_uid columns (mapr / mapt would be FK-enforced via their CREATE TABLE; the 3 existing tables would remain FK-deferred, contradicting §10.4's "Consistent canonical panel-run identity across the entire MCF substrate post-apply" claim)
- FK activations executed before target table created → ALTER TABLE would fail on mapt's FK to mapr if mapr CREATE hadn't completed (intra-step ordering safeguarded by Step 1 → Step 2 sequencing inside the single BEGIN/COMMIT)
- Policy update without table changes → consensus_requirement_json references algorithm/registry that doesn't exist yet (acceptable but inconsistent narrative)

The whole-file BEGIN/COMMIT wrapper enforces all-or-nothing. Intra-transaction step ordering ensures mapr is created before mapt's FK references it.

### 14.4 Rollback DDL

`bc-core/docker/redesign/08-mcf-panel-substrate-rollback.sql` (per the M3/M7-M8 rollback pattern).

**Precondition guard** (refuses if substrate has been used):

```sql
DO $$
DECLARE
  panel_run_count integer;
  transcript_count integer;
  tool_count integer;
  source_count integer;
BEGIN
  SELECT COUNT(*) INTO panel_run_count FROM mcf.metric_authoring_panel_run;
  SELECT COUNT(*) INTO transcript_count FROM mcf.metric_authoring_panel_transcript;
  SELECT COUNT(*) INTO tool_count FROM mcf.workspace_tool_allowlist;
  SELECT COUNT(*) INTO source_count FROM mcf.evidence_source_allowlist;
  IF panel_run_count > 0 OR transcript_count > 0 OR tool_count > 0 OR source_count > 0 THEN
    RAISE EXCEPTION 'M5 rollback REFUSED: tables have rows (panel_run=%, transcript=%, tool=%, source=%). Drop rows first OR accept data loss with manual override.',
      panel_run_count, transcript_count, tool_count, source_count
      USING ERRCODE = 'check_violation';
  END IF;
END $$;
```

**Reversal sequence:**

```sql
BEGIN;

-- Step 1: Revert mcf_v1 policy extension (jsonb_minus on the panel_discipline key)
UPDATE contract.framework_policy
SET consensus_requirement_json = consensus_requirement_json - 'panel_discipline'
WHERE policy_uid = 'mcf_v1' AND policy_version = '1.0.0';

-- Step 2: Drop 3 FKs
ALTER TABLE mcf.metric_contract_revision DROP CONSTRAINT fk_mcr_panel_run;
ALTER TABLE mcf.metric_publication_eligibility_result DROP CONSTRAINT fk_mper_panel_run;
ALTER TABLE mcf.metric_supersession DROP CONSTRAINT fk_mcs_panel_run;

-- Step 3: Drop trigger + function
DROP TRIGGER IF EXISTS trg_mapt_immutability ON mcf.metric_authoring_panel_transcript;
DROP FUNCTION IF EXISTS mcf.fn_mapt_immutability_check();

-- Step 4: Drop the 4 new tables in reverse-dependency order.
-- Per M-M5-1 patch: mcf.metric_authoring_panel_transcript now FKs to
-- mcf.metric_authoring_panel_run, so transcript MUST drop before run.
-- The current order (transcript → run) already satisfies this.
-- allowlists have no FK to the panel-run pair so they drop first/independently.
DROP TABLE mcf.evidence_source_allowlist;
DROP TABLE mcf.workspace_tool_allowlist;
DROP TABLE mcf.metric_authoring_panel_transcript;
DROP TABLE mcf.metric_authoring_panel_run;

COMMIT;
```

---

## 15. Drizzle impact

### 15.1 New Drizzle schema files

| File | Purpose |
|---|---|
| `bc-core/src/database/schema/mcf/metric-authoring-panel-run.ts` | Mirrors §6 DDL exactly |
| `bc-core/src/database/schema/mcf/metric-authoring-panel-transcript.ts` | Mirrors §7 DDL exactly |
| `bc-core/src/database/schema/mcf/workspace-tool-allowlist.ts` | Mirrors §8 DDL exactly |
| `bc-core/src/database/schema/mcf/evidence-source-allowlist.ts` | Mirrors §9 DDL exactly |
| `bc-core/src/database/schema/mcf/index.ts` | Export the 4 new tables |

### 15.2 Drizzle FK foreignColumns — cross-schema + intra-mcf imports

**Cross-schema FKs (5 paths to `contract.panel_output_record`):**

- `mcf.metric_authoring_panel_run.fk_mapr_panel_run` (new this DBCP — 1:1 PK FK per §6)
- `mcf.metric_contract_revision.fk_mcr_panel_run` (new per §10)
- `mcf.metric_publication_eligibility_result.fk_mper_panel_run` (new per §10)
- `mcf.metric_supersession.fk_mcs_panel_run` (new per §10)

All require importing the `panelOutputRecord` table object from `bc-core/src/database/schema/contract/panel-output-record.ts` (existing).

**Intra-mcf FK (1 path to `mcf.metric_authoring_panel_run`, per M-M5-1 patch):**

- `mcf.metric_authoring_panel_transcript.fk_mapt_panel_run → mcf.metric_authoring_panel_run(panel_run_uid)` — Drizzle imports `metricAuthoringPanelRun` from `bc-core/src/database/schema/mcf/metric-authoring-panel-run.ts` (sibling file in the same `mcf` directory). File-load ordering matters: the transcript schema file must be imported AFTER the panel-run schema file (Drizzle resolves foreignColumns references at module-load time). Typically handled correctly by alphabetical re-export from `mcf/index.ts`; if drift surfaces, explicit ordering can be enforced in `index.ts`.

```typescript
// Example: mcf/metric-authoring-panel-run.ts (sketch)
import { uuid, text, jsonb, timestamp, index, uniqueIndex, check, foreignKey } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';
import { mcfSchema } from './pg-schema';
import { panelOutputRecord } from '../contract/panel-output-record';

export const metricAuthoringPanelRun = mcfSchema.table(
  'metric_authoring_panel_run',
  {
    panelRunUid: uuid('panel_run_uid').primaryKey(),
    workbenchFingerprintHash: text('workbench_fingerprint_hash').notNull(),
    consensusPayloadJson: jsonb('consensus_payload_json').notNull().default(sql`'{}'::jsonb`),
    reservoirName: text('reservoir_name'),
    reservoirEntryId: text('reservoir_entry_id'),
    reservoirProvenanceSourceJson: jsonb('reservoir_provenance_source_json'),
    reservoirConfidenceBand: text('reservoir_confidence_band'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    foreignKey({
      name: 'fk_mapr_panel_run',
      columns: [table.panelRunUid],
      foreignColumns: [panelOutputRecord.panelRunUid],
    }).onDelete('restrict'),
    check('mapr_workbench_fp_hash_fmt_chk', sql`${table.workbenchFingerprintHash} ~ '^sha256:[0-9a-f]{64}$'`),
    check('mapr_reservoir_confidence_band_chk', sql`${table.reservoirConfidenceBand} IS NULL OR ${table.reservoirConfidenceBand} IN ('high','medium','low')`),
    check('mapr_reservoir_all_or_none_chk', sql`(${table.reservoirName} IS NULL AND ${table.reservoirEntryId} IS NULL AND ${table.reservoirProvenanceSourceJson} IS NULL AND ${table.reservoirConfidenceBand} IS NULL) OR (${table.reservoirName} IS NOT NULL AND ${table.reservoirEntryId} IS NOT NULL AND ${table.reservoirProvenanceSourceJson} IS NOT NULL AND ${table.reservoirConfidenceBand} IS NOT NULL)`),
    index('idx_mcf_mapr_created_at').on(table.createdAt),
    index('idx_mcf_mapr_reservoir_name').on(table.reservoirName).where(sql`reservoir_name IS NOT NULL`),
  ],
);
```

### 15.3 Drizzle modifications to existing schemas (3 FK additions)

| Existing schema file | Modification |
|---|---|
| `bc-core/src/database/schema/mcf/metric-contract-revision.ts` | Add `fk_mcr_panel_run` foreignKey entry |
| `bc-core/src/database/schema/mcf/metric-publication-eligibility-result.ts` | Add `fk_mper_panel_run` foreignKey entry |
| `bc-core/src/database/schema/mcf/metric-supersession.ts` | Add `fk_mcs_panel_run` foreignKey entry |

### 15.4 Byte-matching DDL discipline — with semantic-equivalence carve-out for multi-line CHECKs

Mirrors M7/M8 §13.4 with one nuance from M-M5-3 review patch:

**Byte-match for stable cases:**
- Simple column DEFAULTs (e.g. `'{}'::jsonb`, `now()`, `gen_random_uuid()`) — Drizzle's `sql\`...\`` template stores the literal string Postgres receives; `pg_get_expr(pg_attrdef.adbin)` returns deterministically the same byte sequence post-normalization. Post-apply verifier checks via JSON deep-equal pattern (mirrors M7/M8 L-3 tightened default check).
- Single-line CHECK predicates (e.g. `workbench_fingerprint_hash ~ '^sha256:[0-9a-f]{64}$'`, `reservoir_confidence_band IS NULL OR reservoir_confidence_band IN ('high','medium','low')`) — Postgres normalizes whitespace minimally; raw string comparison via `pg_get_constraintdef()` is stable.

**Semantic-equivalence for multi-line CHECKs (per M-M5-3 patch):**
- The `mapr_reservoir_all_or_none_chk` CHECK spans multiple SQL lines with line-breaks inside the predicate. Postgres normalizes the stored text via `pg_get_constraintdef()` in a way that may differ in whitespace / parenthesization from the Drizzle `sql\`...\`` template string. Raw byte comparison would be brittle.
- **Verification strategy:** instead of raw string match, post-apply verifier asserts SEMANTIC EQUIVALENCE — required predicate fragments are all present in the `pg_get_constraintdef()` output:
  - `reservoir_name IS NULL`
  - `reservoir_entry_id IS NULL`
  - `reservoir_provenance_source_json IS NULL`
  - `reservoir_confidence_band IS NULL`
  - `reservoir_name IS NOT NULL`
  - `reservoir_entry_id IS NOT NULL`
  - `reservoir_provenance_source_json IS NOT NULL`
  - `reservoir_confidence_band IS NOT NULL`
  - `OR` (boolean disjunction connecting the all-NULL and all-NOT-NULL halves)
- All 9 fragments present → semantic equivalence to the all-or-none invariant. This is robust against Postgres's choice of parenthesization, whitespace, or sub-expression reordering.
- §17.2 #1 (post-apply verifier) implements both byte-match (for simple CHECKs) and semantic-equivalence (for the all-or-none CHECK) per this discipline.

### 15.5 No Drizzle changes for the trigger / policy UPDATE

The trigger function lives in DDL only (Drizzle has no first-class trigger support). The `mcf_v1` policy UPDATE is data, not schema — not part of Drizzle schema.

---

## 16. Dry-run verifier plan

### 16.1 Script

`bc-core/scripts/mcf-m5-dry-run.mjs` (mirrors M3/M4/M7-M8 dry-run script pattern)

### 16.2 Checks (8 total)

| # | Check | HARD-GATE? |
|---|---|---|
| #1 | M7/M8 substrate prereq — all 10 `mcf.*` tables present AND `mcf.metric_contract_version.formula_ast_canonical_json` column present (M7/M8 applied) | YES |
| #2 | None of the 4 new tables exist: `metric_authoring_panel_run`, `metric_authoring_panel_transcript`, `workspace_tool_allowlist`, `evidence_source_allowlist` (clean slate) | YES |
| #3 | None of the 3 deferred FKs exist: `fk_mcr_panel_run`, `fk_mper_panel_run`, `fk_mcs_panel_run` (clean slate); existing `fk_mcf_cert_panel_run` IS present (regression check) | YES |
| #4 | `contract.framework_policy mcf_v1.consensus_requirement_json` does NOT yet contain `panel_discipline` key (clean slate for in-place UPDATE) | YES |
| #5 | All 10 MCF tables empty (no rows would be affected by FK activations) | (no, advisory) |
| #6 | `contract.panel_output_record` exists (FK target exists); 24 existing BCF rows untouched | (no, advisory) |
| #7 | Forward DDL parse + statement counts: 4 `CREATE TABLE` + **7 index-creating statements (3 `CREATE INDEX` + 4 `CREATE UNIQUE INDEX`)** + 1 `CREATE OR REPLACE FUNCTION` + 1 `CREATE TRIGGER` + 3 `ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY` + 1 `UPDATE contract.framework_policy` + 4 `COMMENT ON TABLE` + BEGIN/COMMIT. Dry-run script regex MUST match BOTH `CREATE INDEX` AND `CREATE UNIQUE INDEX` (e.g. `/CREATE\s+(UNIQUE\s+)?INDEX/gi` total = 7) OR count them as two separate categories (3 + 4 = 7). (Per M-M5-2 patch — corrected from earlier "6 CREATE INDEX" mis-count.) | (no, but parse failure = abort) |
| #8 | DDL sha256 captured (forward + rollback) for drift detection | always pass; recording artifact |

### 16.3 Pre-amendment artifact

Unlike M3 cert-amendment and M7/M8 (which CREATE OR REPLACE the existing M3 trigger), this DBCP only CREATEs a NEW trigger function (`fn_mapt_immutability_check`). No pre-amendment snapshot needed for trigger replacement. However, capture a snapshot of the pre-extension `mcf_v1.consensus_requirement_json` for rollback safety:

```sql
-- captured by dry-run script to .pre-extension-policy.json
SELECT consensus_requirement_json
FROM contract.framework_policy
WHERE policy_uid = 'mcf_v1' AND policy_version = '1.0.0';
```

### 16.4 Exit codes

| Exit | Meaning |
|---|---|
| 0 | All checks PASS |
| 1 | DATABASE_URL not set |
| 2 | DDL file not found |
| 3-10 | Per-check failure |
| 20 | Hard-gate refused (M7/M8 not applied OR partial M5 apply detected) |
| 21 | Unexpected error |

---

## 17. Post-apply verifier plan

### 17.1 Script

`bc-core/scripts/mcf-m5-post-apply-verification.mjs`

### 17.2 Checks (14 total — per M-M5-1 patch added #11a)

**Structural (1–8):**

| # | Check |
|---|---|
| #1 | `mcf.metric_authoring_panel_run` present with 8 columns + 3 CHECKs + 1 FK to `contract.panel_output_record(panel_run_uid)` ON DELETE RESTRICT + 2 indexes. The 2 single-line CHECKs (`mapr_workbench_fp_hash_fmt_chk`, `mapr_reservoir_confidence_band_chk`) verified via byte-match against `pg_get_constraintdef()`; the multi-line `mapr_reservoir_all_or_none_chk` verified via semantic-equivalence per §15.4 (asserts all 9 required predicate fragments present + `OR` disjunction). |
| #2 | `mcf.metric_authoring_panel_transcript` present with 6 columns + 1 CHECK + 1 FK to `mcf.metric_authoring_panel_run(panel_run_uid)` ON DELETE RESTRICT (per M-M5-1 patch — NOT to `contract.panel_output_record`; semantic-equivalence to "MCF-only attachment" surfaced via FK target match) + 1 UNIQUE + 1 index + trigger attached |
| #3 | `mcf.workspace_tool_allowlist` present with 6 columns + 1 CHECK + 2 UNIQUE indexes |
| #4 | `mcf.evidence_source_allowlist` present with 6 columns + 1 CHECK + 2 UNIQUE indexes |
| #5 | All 3 deferred FKs active: `fk_mcr_panel_run`, `fk_mper_panel_run`, `fk_mcs_panel_run` (all targeting `contract.panel_output_record(panel_run_uid)`) |
| #6 | Existing `fk_mcf_cert_panel_run` STILL present (regression) |
| #7 | `mcf_v1.consensus_requirement_json` extended in-place: pre-extension keys preserved (`models_required=3`, `agreement_threshold=2`, `models=[maker,checker,moderator]`); new `panel_discipline` key present with all 4 sub-keys (algorithm name, version, registry version, retention policy, allowlist pinning) |
| #8 | Trigger function `mcf.fn_mapt_immutability_check` present + attached to `metric_authoring_panel_transcript` as BEFORE UPDATE OR DELETE |

**Behavioral (9–12 + 11a) — tx-rolled-back synthetic-row exercises:**

| # | Check |
|---|---|
| #9 | Synthetic INSERT panel_run row to `contract.panel_output_record` + INSERT to `mcf.metric_authoring_panel_run` (1:1 composition) succeeds + rolls back |
| #10 | INSERT to `mcf.metric_authoring_panel_run` WITHOUT prior insert to `contract.panel_output_record` is REJECTED by FK |
| #11 | INSERT 3 transcripts (maker/checker/moderator) AFTER setting up the contract.panel_output_record + mcf.metric_authoring_panel_run pair → succeeds. UPDATE one transcript → REJECTED by trigger; DELETE one → REJECTED by trigger; INSERT a 4th transcript with same (panel_run_uid, model_role_code='maker') → REJECTED by UNIQUE; rolls back |
| #11a | (per M-M5-1 patch) INSERT a transcript with a `panel_run_uid` that exists in `contract.panel_output_record` but has NO `mcf.metric_authoring_panel_run` row → REJECTED by `fk_mapt_panel_run` (substrate-enforces MCF-only attachment per §5.3.1). The test creates only the BCF-style contract row, skips the mapr insert, then attempts the transcript insert; verifier asserts FK violation citing `fk_mapt_panel_run`. |
| #12 | INSERT to `mcf.metric_publication_eligibility_result` (or revision / supersession) with bogus `panel_run_uid` → REJECTED by new FK |

**Cleanup (13):**

| # | Check |
|---|---|
| #13 | All 4 new MCF tables empty after verifier completes (rollback discipline preserved across all 5 behavioral exercises including #11a); existing mcf.* tables also empty; existing 24 `contract.panel_output_record` BCF rows untouched |

### 17.3 Exit codes

| Exit | Meaning |
|---|---|
| 0 | All 14 checks PASS (incl #11a per M-M5-1 patch) |
| 1 | DATABASE_URL not set |
| 3-16 | Per-check failure (check_number + 2; #11a is exit 13 / check_number 11.5 packed into linear ordering) |
| 17 | Unexpected error |

---

## 18. Risks and mitigations

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M5-1 | **Workbench fingerprint algorithm drift between M5 substrate spec and M12 implementation** | Medium | M5 stores only the hash (format `sha256:<64hex>`); algorithm is pinned via `mcf_v1.consensus_requirement_json.panel_discipline.workbench_fingerprint_algorithm_version`. M12 implementation MUST honor the pinned version. Any algorithm change → policy version bump (mcf_v1 → mcf_v2). |
| R-M5-2 | **Reservoir-provenance fields stay NULL post-M5 until M11 ingestion ships, allowing test-fixture panel runs to write incomplete provenance and pollute production audit trail** | Low | M11 ingestion is the only path that produces reservoir-attributed panel runs. M5 substrate's all-or-none CHECK ensures partial population is rejected. Test-fixture panel runs (substrate-internal exercises) use all-NULL reservoir fields (admitted), which is correct semantically. |
| R-M5-3 | **Transcript trigger UNCONDITIONAL immutability rejects legitimate panel-side bug fixes** | Low (acknowledged) | Per MCF §11.3 + Invariant V transcripts are immutable by design. If a transcript has a bug, the correct response is to author a new panel run (new panel_run_uid). The substrate refuses to permit transcript mutation. Operator override path: temporarily DROP TRIGGER, mutate, recreate trigger — operationally feasible but highly unusual; not part of normal application code. |
| R-M5-4 | **Tool/evidence allowlist `effective_to > effective_from` CHECK rejects legitimate "void this version" use case** (operator wants to retire a tool version effective immediately, but `now()` may sometimes equal `effective_from` due to clock granularity) | Low | Substrate-internal exercises set `effective_from = now() - interval '1 hour'` to avoid the edge case. Production: M12 retires tool versions by setting `effective_to = now() + interval '1 second'` (small forward offset). Mirrors the M4 integration spec's `framework_policy_effective_to_chk` mitigation. |
| R-M5-5 | **JSON-schema validation of `consensus_payload_json` deferred to M12** — bad payloads can be written to substrate without immediate rejection | Medium | Substrate enforces structural integrity (`jsonb NOT NULL`) but not semantic content. M12 panel service is the authority on payload shape. Defense in depth: post-M12 evidence PRs can audit live `consensus_payload_json` rows for taxonomy violations. M5 substrate is empty until M12 ships → no premature pollution risk. |
| R-M5-6 | **In-place policy UPDATE rejected by some hypothetical CHECK on `framework_policy.consensus_requirement_json`** | Low | Verified: no CHECK on `consensus_requirement_json` exists. Inspection of `pg_constraint` on `contract.framework_policy` confirms the only CHECKs are on `scope_code`, `sampling_rate`, `effective_to`. UPDATE will succeed. |
| R-M5-7 | **3 FK activations cause cascading regression in M4 service code paths that previously expected `panel_run_uid` to be nullable + unconstrained** | Low | All 4 mcf.* `panel_run_uid` columns remain nullable (M4 NF1 all-or-none allows all-NULL). FK only fires when the column is NON-NULL. M4 service code paths that set `panel_run_uid=null` are unaffected. Code paths that set a non-null value MUST point at a real `contract.panel_output_record` row, which is the intended contract. |
| R-M5-8 | **The 1:1 PK FK composition between `contract.panel_output_record` and `mcf.metric_authoring_panel_run` allows BCF panel runs to NOT have a matching `mcf.metric_authoring_panel_run` row, but blocks MCF panel runs from being written without the shared row** | Low (intentional) | This is the desired semantic: BCF panel runs (existing 24 rows + future) don't need an MCF extension row. MCF panel runs require both. The 1:1 is enforced only in the MCF → contract direction. |
| R-M5-9 | **Defect-code taxonomy v1 set in §12.1 may not survive operator review at M12 implementation time** | Low | M5 ships ONLY substrate + policy registry version pinning (`defect_code_registry_version: 'v1'`). The actual taxonomy lives in code (TS const) and is enumerable but not substrate-enforced. M12 finalizes the v1 list. Future taxonomy changes → policy version bump. |
| R-M5-10 | **Transcript-orphan attachment to non-MCF panel runs** (raised by review M-M5-1) | RESOLVED at substrate per M-M5-1 patch | `mcf.metric_authoring_panel_transcript.panel_run_uid` FK retargeted to `mcf.metric_authoring_panel_run(panel_run_uid)` (NOT `contract.panel_output_record`). Substrate now rejects transcript inserts whose `panel_run_uid` lacks an `mcf.metric_authoring_panel_run` row — i.e. transcripts cannot orphan to BCF or any non-MCF panel run. See §5.3.1 + §7.3 + §17.2 #11a. The change preserves D-M5-B hybrid composition (the panel-run extension row is still 1:1 with `contract.panel_output_record`) while pushing MCF-ownership enforcement DOWN to the substrate. |

### 18.1 Stop conditions

The M5 implementation PR STOPS and re-frames if:

- Operator decides to reverse D-M5-7 and extend BCF rejection log CHECKs (changes scope significantly)
- Operator decides to tighten NF1 per D-M5-10 (changes scope; requires synthetic-test migration plan)
- BCF substrate amendment lands during M5 implementation that conflicts with shared `contract.panel_output_record` use (coordinate)
- New addendum guardrail introduces additional MCF-specific panel-run fields not covered by §6.2

---

## 19. Operator approvals for implementation PR (O-M5-1..O-M5-10)

Before the M5 implementation PR opens, the operator approves these 10 items:

| # | Approval item |
|---|---|
| **O-M5-1** | Confirm D-M5-1 (D-M5-B hybrid composition) — 4 new mcf tables + 3 FK activations + mcf_v1 policy extension; NO `contract.*` CHECK extensions |
| **O-M5-2** | Confirm `mcf.metric_authoring_panel_run` 8-column shape + 3 CHECKs (workbench FP format, reservoir confidence band, reservoir all-or-none) + 1 PK FK to `contract.panel_output_record` + 2 indexes |
| **O-M5-3** | Confirm `mcf.metric_authoring_panel_transcript` 6-column shape + model_role_code CHECK + 1 FK to **`mcf.metric_authoring_panel_run(panel_run_uid)`** ON DELETE RESTRICT (per M-M5-1 patch — substrate-enforces MCF-only attachment; see §5.3.1 + §7.3 + R-M5-10) + UNIQUE (panel_run_uid, model_role_code) + 1 index + append-only trigger |
| **O-M5-4** | Confirm `mcf.workspace_tool_allowlist` 6-column shape + effective_to CHECK + 2 UNIQUE indexes (active-per-code partial + version-per-code full) |
| **O-M5-5** | Confirm `mcf.evidence_source_allowlist` 6-column shape (mirrors tool allowlist) |
| **O-M5-6** | Confirm 3 FK activations target `contract.panel_output_record(panel_run_uid)` with ON DELETE RESTRICT (matches `fk_mcf_cert_panel_run` precedent) |
| **O-M5-7** | Confirm `mcf_v1.consensus_requirement_json` in-place extension via jsonb-merge `||` (preserves existing keys; adds `panel_discipline` with 4 sub-keys) |
| **O-M5-8** | Confirm trigger function `mcf.fn_mapt_immutability_check` unconditionally rejects UPDATE + DELETE on transcript rows (no state-conditional permit) |
| **O-M5-9** | Confirm DDL atomicity — all 6 steps inside one `BEGIN/COMMIT` per §14.2; rollback DDL has precondition guard refusing if any new-table row exists |
| **O-M5-10** | Approve the next gate: M5 implementation PR (NO DB APPLY) |

---

## 20. Recommended next gate

### 20.1 Recommendation: open M5 implementation PR (NO DB APPLY)

The implementation PR ships:

| Deliverable | Location |
|---|---|
| Forward DDL | `bc-core/docker/redesign/08-mcf-panel-substrate.sql` (single file, BEGIN/COMMIT) |
| Rollback DDL | `bc-core/docker/redesign/08-mcf-panel-substrate-rollback.sql` (with precondition guard per §14.4) |
| Drizzle: 4 new schema files | `bc-core/src/database/schema/mcf/metric-authoring-panel-run.ts` + `metric-authoring-panel-transcript.ts` + `workspace-tool-allowlist.ts` + `evidence-source-allowlist.ts` |
| Drizzle: 3 schema modifications | `bc-core/src/database/schema/mcf/metric-contract-revision.ts` + `metric-publication-eligibility-result.ts` + `metric-supersession.ts` (each adds one foreignKey) |
| Drizzle: index file update | `bc-core/src/database/schema/mcf/index.ts` (export 4 new tables) |
| Dry-run script | `bc-core/scripts/mcf-m5-dry-run.mjs` (per §16; captures pre-extension policy JSON) |
| Post-apply verifier | `bc-core/scripts/mcf-m5-post-apply-verification.mjs` (per §17; 13 checks) |
| Optional unit tests | Trigger behavior tests against a test DB if straightforward — otherwise deferred to integration tests post-apply |

NO bc-core service code edits in M5 implementation PR — the M11 / M12 services that write to these tables are separate gates.

**PR title (suggested):** `feat(mcf): M5 Panel Substrate — metric_authoring_panel_run + transcript + tool/evidence allowlists + 3 FK activations + mcf_v1 policy extension (NO DB APPLY)`

### 20.2 Subsequent gate: small DDL apply

After the impl PR merges, a separate operator-authorized session applies the DDL. Mirrors M3 cert-amendment + M4 + M7/M8 apply gate patterns:

1. `node scripts/mcf-m5-dry-run.mjs` → expect exit 0 (all 8 preconditions PASS; pre-extension policy captured)
2. STOP for operator approval
3. `psql -v ON_ERROR_STOP=1 -f docker/redesign/08-mcf-panel-substrate.sql` → expect exit 0
4. `node scripts/mcf-m5-post-apply-verification.mjs` → expect exit 0 (all 13 checks PASS)

### 20.3 Subsequent gate: M5 evidence PR

Mirrors M3 / M4 / M7/M8 evidence PR pattern: 6 basis-of-apply artifacts (4 dry-run + 2 post-apply) committed explicitly to `bc-core/scripts/audit-output/`; closeout doc pushed to bc-docs-v3 main.

### 20.4 Parallel-eligible: M9 fixture substrate

Per build plan, M9 has no M5 dependency (depends on M7 only). M9 preflight can open in parallel to M5 implementation PR if operator wants to fan out.

### 20.5 Downstream gates (gated on M5)

| Gate | Status post-M5 apply |
|---|---|
| M11 reservoir ingestion service | UNBLOCKED — needs M5 to populate `reservoir_provenance_*` fields |
| M12 Metric Authoring Panel implementation | UNBLOCKED — needs M5 + M7 + M10 + M11 |
| M13 PE-MC evaluator | Still gated on M9 + M10 |
| M14 publication path | Still gated on M5 + M13 |

---

## 21. What stays closed

| | Status |
|---|---|
| M5 impl PR | Operator authorizes next; not opened by this DBCP |
| M5 DDL apply | Pending impl PR |
| M5 evidence PR | Pending apply |
| **M9 fixture substrate** | CLOSED — parallel-eligible; gated on operator authorization |
| **M10 deterministic verifier service** | CLOSED — gated on M9 |
| **M11 reservoir ingestion service** | CLOSED — gated on M5 + operator authorization |
| **M12 Metric Authoring Panel implementation** | CLOSED — gated on M5 + M7 + M10 + M11 |
| **M13 PE-MC evaluator** | CLOSED — gated on M5 + M7 + M9 + M10 |
| **M14 / M15 publication / supersession paths** | CLOSED — gated on M4 + M5 + M13 |
| **M16 / M17 operator console** | CLOSED — gated on M12 + M14 |
| **M18 tenant binding console** | CLOSED — gated on M6 (not yet opened) |
| **Real MCF metric contracts** | CLOSED — substrate accepts authoring + has panel-attestation referential integrity post-M5, but no panel + no ingestion = no real authoring |
| **BCF data changes** | CLOSED — untouched throughout MCF arc |
| **`contract.authoring_panel_rejection_log` extensions** | CLOSED per D-M5-7 — table stays BCF-specific by architectural choice |
| **`contract.panel_output_record.verdict_payload_json` defect-code CHECK extension** | CLOSED per D-M5-7 — MCF defect detail lives in `mcf.metric_authoring_panel_run.consensus_payload_json` |
| **NF1 tightening on `mcf.certification_record`** | DEFERRED per D-M5-10 — no NF1 change in M5; future amendment if operator selects production tightening |
| **MCF panel service** | CLOSED — M12 gate |
| **MCF defect-code v2 taxonomy** | CLOSED — v1 registry pinned via `mcf_v1.consensus_requirement_json.panel_discipline.defect_code_registry_version='v1'`; v2 requires policy bump |
| **MCF tool/evidence allowlist v1 seed rows** | CLOSED — M5 ships only the substrate; the specific tool/source list is M12 |

---

## Document verification

- **Scope clear** — §1 frames as docs-only DBCP; §1.4 enumerates 11 discipline assertions
- **Operator decisions accepted** — §2 itemizes D-M5-1..D-M5-9 as ACCEPTED; D-M5-10 explicitly DEFERRED
- **Live state captured** — §3 enumerates 10 mcf.* tables (all empty); 24 BCF panel runs untouched; 4 panel_run_uid columns (1 live FK + 3 deferred); M4 seeds intact; M3 + M7 triggers + M4 + M7/M8 services live
- **Ownership boundary** — §4 enumerates 9 MUST deliverables + 14 MUST NOT items
- **Composition model** — §5 documents 1:1 PK FK composition with `contract.panel_output_record`; rationale vs alternatives; insert ordering; stage-code semantics
- **4 new table designs** — §6/§7/§8/§9 each define purpose + column inventory + constraints + indexes + DDL + ownership
- **3 FK activations** — §10 enumerates targets, DDL, safety of empty-table activation, post-M5 FK landscape
- **Policy extension** — §11 enumerates pre/post shape, in-place UPDATE DDL, rationale for in-place vs versioned, regression assertions
- **Defect-code registry** — §12 v1 taxonomy (9 codes) + consensus payload schema + versioning + JSON-schema-vs-CHECK rationale
- **Trigger design** — §13 pattern source, function body, attachment, behavioral verification
- **DDL apply + rollback** — §14 single-transaction sequence (6 steps); rollback with precondition guard
- **Drizzle impact** — §15 4 new files + 3 modifications + byte-match discipline
- **Verifier plans** — §16 dry-run 8 checks (3 hard-gates) + §17 post-apply 13 checks (8 structural + 4 behavioral + 1 cleanup)
- **Risk register** — §18 enumerates 9 risks (R-M5-1..R-M5-9) with severity + mitigation; 4 stop conditions
- **Operator approvals enumerated** — §19 lists 10 approvals (O-M5-1..O-M5-10) the operator must give before the M5 implementation PR can open
- **Next gate recommended** — §20 specifies the M5 impl PR (NO DB APPLY) + subsequent small-DDL apply gate + evidence PR + parallel-eligible M9; §20.5 enumerates downstream gates
- **What stays closed** — §21 enumerates 18 closed/deferred gates
- **No DDL, no code, no metric authoring, no BCF touches** this session — this DBCP only
