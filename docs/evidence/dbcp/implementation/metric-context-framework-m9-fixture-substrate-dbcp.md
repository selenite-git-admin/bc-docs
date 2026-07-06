---
uid: metric-context-framework-m9-fixture-substrate-dbcp
title: MCF M9 Self-Verification Fixture Substrate DBCP
description: Combined design-blueprint for MCF gate M9 (Self-Verification Fixture Substrate) per operator-accepted preflight decisions D-M9-1..D-M9-8 (preflight 686afc3). Realizes the operator-locked D-M9-B option — one mcf-owned fixture registry table `mcf.metric_self_verification_fixture` (16 columns; 1 PK + 2 intra-mcf FKs to metric_contract + metric_contract_version + 1 intra-mcf FK to metric_authoring_panel_run + 3 Section jsonb columns + 6 hash text columns + rationale_text NOT NULL ≥40 chars + authored_by_name NOT NULL + created_at timestamptz NOT NULL); 7 CHECK constraints (5 sha256 format CHECKs + 1 algorithm version regex + 1 rationale length); 1 UNIQUE constraint on (metric_contract_version_uid, self_verification_fixture_hash) preventing duplicate-content fixtures per MCV; 3 indexes per query patterns (lookup-by-mcv, lookup-by-bound-package-hash, lookup-by-panel-run); 1 trigger function + 1 trigger attachment (M3/M5-style unconditional immutability post-INSERT — UPDATE/DELETE rejected; per operator design constraint "Immutable after insert via M3-style trigger"); 1 cross-schema doc-only reference to M7/M8 `FormulaCanonicalizationService` + `PackageSignatureService` for fixture hash semantics (no new hash machinery; algorithm version `mcf-hash-v1` reused per M7/M8 forever-lock per inferred D-M9-A1); C-FX-1..C-FX-11 structural-check engine specification documented for impl-PR scope (engine implementation co-located with M9 DDL impl PR per inferred D-M9-A2 — fail at INSERT time, not at first M10 verifier run). NO `mcf.metric_self_verification_result` substrate (M10 owns). NO verifier execution engine (M10 owns). NO real fixture rows. NO synthetic metric contract rows. NO M10/M11/M12+ work. NO BCF data touches. Substrate change: 1 new table + 1 trigger function + 1 trigger attachment + COMMENT annotation; all atomic inside one BEGIN/COMMIT per §12 + M3/M5/M7-M8 atomicity pattern. Rollback file with row-count precondition guard refusing reverse if fixture rows exist (matches M5 rollback discipline). Dry-run verifier plan (8 checks; 4 HARD-GATEs: M5/M7/M8 prereq + new table absent + no real-fixture rows would orphan + DDL parse counts). Post-apply verifier plan (13 checks; 5 structural + 7 behavioral SAVEPOINT-protected synthetic-row exercises per M-M5-1 verifier-fix discipline + 1 cleanup). 7 risks (R-M9-1..R-M9-7) + 3 stop conditions + 9 operator approvals (O-M9-1..O-M9-9). Recommended next gate: M9 implementation PR (NO DB APPLY) shipping the substrate + C-FX-1..C-FX-11 engine + computeSelfVerificationFixtureHash() helper extending M7/M8 PackageSignatureService. NO bc-core edits this session. NO DDL apply this session. NO data writes this session.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m9-fixture-substrate-dbcp
---

# MCF M9 Self-Verification Fixture Substrate DBCP

## 1. Scope and grounding

### 1.1 Purpose

Design the M9 self-verification fixture substrate that closes the gap between PE-MC structural well-formedness (M7/M8 hash discipline + PE-MC-1..PE-MC-9) and execution correctness (proven by M10 verifier running fixtures, per MCF §12.6). M9 ships the substrate side: a per-MCV fixture registry table with the three-section body, four fixture-side hashes, the bound `package_signature_hash` per §12.7 stale-fixture rule, and substrate-enforced immutability per the operator's design constraint.

The substrate stays **dormant** post-apply: no fixtures are written, no panel runs are recorded, no MCF metric contracts are authored. The table exists with substrate-enforced format/uniqueness/immutability discipline — but no row flow happens until M12 panel implementation ships and operator-driven fixture authoring begins.

The DBCP follows the operator-accepted preflight (`bc-docs-v3 686afc3`) recommendations and the 8 locked operator decisions enumerated in §2.

### 1.2 What this DBCP is and is not

| | This DBCP |
|---|---|
| Is | A combined docs-only design blueprint for M9 (one mcf-owned fixture registry table + immutability trigger + C-FX-1..C-FX-11 engine specification) under one document, per operator's "Keep it focused" instruction |
| Is | The formal trigger for a sequenced implementation arc (DBCP → impl PR → small-DDL apply gate → evidence PR) |
| Is not | A code edit — bc-core stays unchanged this session |
| Is not | A DDL apply — the substrate change is a separate operator-authorized session |
| Is not | The M10 verifier engine or `mcf.metric_self_verification_result` substrate (M10 owns) |
| Is not | An M11 reservoir ingestion design (downstream; depends on M5; can ship in parallel with M9-M10) |
| Is not | An M12 Metric Authoring Panel implementation design (downstream; depends on M5 + M7 + M9 + M10 + M11) |
| Is not | A BCF substrate change — no `contract.*` schema touches |
| Is not | An M2/M3/M4/M5/M7/M8 substrate change — those gates are closed and live |

### 1.3 Source documents consumed

| Source | Role |
|---|---|
| M9 preflight (`686afc3`) | Decision options + recommendations the operator accepted |
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority |
| MCF requirements §12 (Self-Verification Fixtures) | §12.1 purpose; §12.4 three-section body; §12.5 C-FX-1..C-FX-11 structural checks; §12.6 verifier behavior; §12.7 stale-fixture rule + bound package_signature_hash; §12.8 multi-fixture coverage; §12.9 immutability and supersession |
| MCF requirements §13 (PE-MC-10) | PE-MC-10 cites a satisfying verification result whose bound `package_signature_hash` matches the candidate's current hash |
| MCF requirements §8.7 (package signature) | Composition of `package_signature_hash` (formula AST + bindings + grain + filter + temporal gate + computed-dim refs) |
| MCF requirements §17.1 (per-MC-version substrate) | `mcf.metric_self_verification_fixture` substrate row obligation |
| MCF build plan §M9 | Substrate scope: per-MC-version fixture body + bound `package_signature_hash` + `self_verification_fixture_hash` + structural-check engine + stale-fixture rule; T-shirt size L; primary risk: structural checks not exhaustive |
| M5 apply closeout (`7800437`) | Live state confirmation — 14 mcf.* tables, all empty; panel substrate live with `mcf.metric_authoring_panel_run` FK target for fixture's authoring attribution |
| M7/M8 apply closeout (`6b3ffb2`) | `FormulaCanonicalizationService`, `PackageSignatureService`, `mcf-jcs.ts` (RFC 8785 JCS), algorithm version `mcf-hash-v1` forever-lock — M9 reuses for the new `self_verification_fixture_hash` |
| M3 cert-amendment closeout (`60efd9d`) | Live `mcf.fn_mvb_active_immutability_check` pattern reference for the M9 immutability trigger (M9 mirrors M5 transcript pattern — unconditional UPDATE/DELETE reject, per operator design constraint) |
| Live `mcf.metric_contract` + `mcf.metric_contract_version` schemas | Verified empirically: parent identity carries 6 hashes (formula_intent, variable_binding_set, filter_set, identity_tuple, package_signature, hash_algorithm_version); MCV carries `formula_ast_canonical_json jsonb NOT NULL` (M7) |
| Live `mcf.metric_authoring_panel_run` | Verified empirically post-M5: 8 columns, PK FK to `contract.panel_output_record(panel_run_uid)` — fixture's `panel_run_uid` FKs to this MCF-owned table per D-M9-4 panel-only authoring boundary |
| Live `mcf.*` substrate (14 tables, all empty) | Verified empirically: target FK parents exist + zero rows so FK activation is metadata-only |

### 1.4 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits this session | ✓ — read-only |
| No DDL applied | ✓ — DBCP designs the substrate change; apply is a separate gate |
| No MCF metric contracts created | ✓ — substrate stays empty |
| No fixtures written | ✓ — substrate dormant pending M12 |
| No verification results written | ✓ — `mcf.metric_self_verification_result` is M10, not in scope |
| No BCF data touched | ✓ — no `contract.*` / `concept_registry.*` touches |
| No M10 / M11 / M12+ work | ✓ — downstream gates |
| No M4 DBCP doc-bug correction this session | ✓ — folded into M10 DBCP per D-M9-8 (see §11.4) |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

---

## 2. Accepted operator decisions (D-M9-1..D-M9-8)

Per operator-accepted preflight recommendations (`686afc3`) and explicit acceptance in the DBCP-gate operator message:

| # | Decision | Locked |
|---|---|---|
| **D-M9-1** | ACCEPT D-M9-B — single mcf-owned fixture registry table `mcf.metric_self_verification_fixture`. (Rejects D-M9-A static repo-only files; defers D-M9-C fixture-pack envelope.) | ACCEPTED |
| **D-M9-2** | Store Section C resolver fixture config / probe gate plan as JSONB in M9; structured child rows deferred unless M10 proves the need | ACCEPTED |
| **D-M9-3** | M10 enforcement requires ≥1 fixture per cert; M9 substrate itself remains empty until fixture authoring begins under M12 | ACCEPTED |
| **D-M9-4** | Fixture authoring boundary is panel-only / governed workbench path; no public API authoring in M9. (Operationalized in M9 substrate as `panel_run_uid NOT NULL` FK to `mcf.metric_authoring_panel_run` — see §5.) | ACCEPTED |
| **D-M9-5** | Fixtures are per `metric_contract_version`; supersession requires re-authoring or an explicit future copy-forward helper (not implicit reuse). (Operationalized as FK to MCV + UNIQUE (mcv, fixture_hash) + immutability trigger — see §5 + §8.) | ACCEPTED |
| **D-M9-6** | `rationale_text` minimum length = 40 chars (matches M3 supersession `mcs_rationale_min_length_chk` + M4 cert-override pattern) | ACCEPTED |
| **D-M9-7** | M9 first, then M11. No concurrent DBCPs. (M11 preflight remains parked until M9 lands.) | ACCEPTED |
| **D-M9-8** | M4 DBCP doc-bug correction (comment incorrectly attributing `mcf.metric_self_verification_result` to M9) folded into M10 DBCP unless it blocks M9. (Non-blocking by inspection — see §11.4.) | ACCEPTED |

### 2.1 DBCP-inferred design decisions (not directly addressed by D-M9-1..D-M9-8)

These three decisions are inferred from the preflight recommendations + operator design constraints and listed here for explicit operator review at §17:

| # | Decision | Source |
|---|---|---|
| **D-M9-A1** | Reuse `mcf-hash-v1` algorithm version bundle marker for the new `self_verification_fixture_hash` (per M7/M8 §12.4 single-bundle versioning forever-lock) | Preflight D-M9-7 recommended `mcf-hash-v1`; operator's design constraint "Reuse M7/M8 canonicalization/hash services" |
| **D-M9-A2** | C-FX-1..C-FX-11 structural-check engine ships in the M9 impl PR (co-located with the DDL), so fixture authoring fails at INSERT time, not at first M10 verifier run | Preflight D-M9-5 recommended M9-owns-engine; operator's "Target implementation-ready" instruction |
| **D-M9-A3** | Body shape = 3 separate JSONB columns (`section_a_inputs_json`, `section_b_expected_output_json`, `section_c_resolver_config_json`) rather than 1 combined JSONB column | Operator's D-M9-2 explicitly names "Section C ... as JSONB" + operator's required-section list names "Section A JSON, Section B JSON, Section C JSONB probe plan" as distinct items |

---

## 3. Current live substrate state

### 3.1 Live state recap (after M5 apply at `bb98642`)

After bc-core `bb98642` + bc-docs-v3 `7800437` + M9 preflight at `686afc3`:

- **14 `mcf.*` tables, all empty.** Identity-bearing parent columns on `mcf.metric_contract` carry the 6 M2/M7/M8 hash columns with sha256 format CHECKs and `mcf-hash-v1` algorithm version; `mcf.metric_contract_version` carries `formula_ast_canonical_json jsonb NOT NULL`.
- **M3 + M7 + M5 triggers live**: `fn_mcv_state_transition_check`, `fn_mvb_active_immutability_check`, `fn_mfc_active_immutability_check`, `fn_mcdr_active_immutability_check`, `fn_mcv_descriptive_immutability_check` (M7 3-IF amended), `fn_mapt_immutability_check` (M5 unconditional).
- **M4 cert writer service live**; M7/M8 services live (`FormulaCanonicalizationService`, `PackageSignatureService`, `McfHashComputerCoordinator`, `mcf-jcs.ts`); algorithm version `mcf-hash-v1`.
- **M5 panel substrate live**: 4 tables empty; `mcf.metric_authoring_panel_run` is the canonical FK target for MCF authoring runs.
- **`mcf_v1` policy** carries `panel_discipline` sub-key (M5).

### 3.2 Verified empirically via bc-postgres MCP

| Pre-state assertion | Confirmed |
|---|---|
| 14 mcf.* tables, all 0 rows | ✓ (this DBCP's bc-postgres MCP query) |
| `mcf.metric_self_verification_fixture` does NOT exist | ✓ — clean slate |
| `mcf.metric_self_verification_result` does NOT exist (M10 owns) | ✓ — out of scope for M9 |
| `mcf.metric_contract.package_signature_hash` column live with format CHECK | ✓ (M7/M8 substrate live since M7/M8 apply) |
| `mcf.metric_authoring_panel_run` live | ✓ (M5 substrate live since M5 apply) |
| `mcf.metric_contract_version.formula_ast_canonical_json` jsonb NOT NULL | ✓ (M7/M8) |

### 3.3 Live state for M9 FK targets

| FK target | Status | Used by M9 |
|---|---|---|
| `mcf.metric_contract(metric_contract_uid)` | live since M2 | YES — `fk_msvf_mc` |
| `mcf.metric_contract_version(metric_contract_version_uid)` | live since M2 | YES — `fk_msvf_mcv` |
| `mcf.metric_authoring_panel_run(panel_run_uid)` | live since M5 | YES — `fk_msvf_panel_run` |

---

## 4. M9 ownership boundary

### 4.1 M9 MUST own (this DBCP)

| # | Deliverable | Location |
|---|---|---|
| 1 | `mcf.metric_self_verification_fixture` table (16 columns; per-MCV fixture body) | New DDL `09-mcf-fixture-substrate.sql` |
| 2 | 7 CHECK constraints (5 sha256 format + 1 algorithm version regex + 1 rationale length ≥40) | Inline in CREATE TABLE |
| 3 | 1 UNIQUE constraint on `(metric_contract_version_uid, self_verification_fixture_hash)` | Inline in CREATE TABLE |
| 4 | 3 FKs — 2 intra-mcf (mc, mcv) + 1 intra-mcf (panel_run) | Inline in CREATE TABLE |
| 5 | 3 indexes (lookup-by-mcv, lookup-by-bound-package-hash, lookup-by-panel-run) | CREATE INDEX |
| 6 | Immutability trigger function + attachment (`mcf.fn_msvf_immutability_check` + `trg_msvf_immutability`) — M3/M5-style unconditional UPDATE/DELETE reject | DDL §3 |
| 7 | COMMENT ON TABLE | DDL §4 |
| 8 | C-FX-1..C-FX-11 structural-check engine SPEC (this DBCP §7.4); implementation co-located with M9 impl PR per D-M9-A2 | this DBCP + impl PR |
| 9 | `computeSelfVerificationFixtureHash(sectionA, sectionB, sectionC)` helper SPEC (this DBCP §6.4); implementation extends M7/M8 `PackageSignatureService` per D-M9-A1 | this DBCP + impl PR |
| 10 | Dry-run + post-apply verifier scripts | bc-core `scripts/mcf-m9-dry-run.mjs` + `mcf-m9-post-apply-verification.mjs` |
| 11 | Rollback DDL with row-count precondition guard | `09-mcf-fixture-substrate-rollback.sql` |

### 4.2 M9 MUST NOT own

| # | Out-of-scope | Belongs to |
|---|---|---|
| 1 | `mcf.metric_self_verification_result` (verification result substrate — verdict / diff trace / executed-at) | **M10** |
| 2 | Verifier execution engine (read package by hash → run AST → compare to Section B → emit verdict) | **M10** |
| 3 | Activation of `fk_mper_verification_result` on `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` | **M10** (target table is M10's, not M9's) |
| 4 | M4 DBCP doc-bug correction (M4 inline comment incorrectly attributes `mcf.metric_self_verification_result` to "M9") | **M10 DBCP** per D-M9-8 (non-blocking by inspection — see §11.4) |
| 5 | Fixture authoring path / proposal generation | **M12** Metric Authoring Panel |
| 6 | Reservoir ingestion of fixture proposals | **M11** |
| 7 | Minimum-fixture-coverage discipline per formula class (§12.8 / §19.13 Q37) | OPEN — not a M9 dependency |
| 8 | Real metric contracts / real fixtures | substrate stays empty pending M11 + M12 + operator runs |
| 9 | BCF data | NEVER in MCF gates |
| 10 | Fixture-pack envelope (multi-fixture grouping) | Deferred (D-M9-1 selected D-M9-B not D-M9-C; pack revisit if Q37 lands) |
| 11 | Public-API fixture authoring | Excluded per D-M9-4 (panel-only) |
| 12 | Service-side stale-fixture detection beyond bound `package_signature_hash` storage | M10 verifier re-checks per §12.6 step 3 (defense-in-depth) |

---

## 5. Table design: `mcf.metric_self_verification_fixture`

### 5.1 Purpose

Per-MCV registry of self-verification fixtures. Each row carries:
- Section A inputs (typed rowsets per declared variable binding) per §12.4
- Section B expected output (typed value or rowset) per §12.4
- Section C resolver fixture config (computed-dimension resolver config) per §12.4
- 4 fixture-side hashes (3 reused from M7/M8 + 1 new `self_verification_fixture_hash`)
- Bound `package_signature_hash` snapshot pinned at fixture-bind time per §12.7
- Algorithm version marker
- Audit (rationale ≥40 chars, authored_by_name, panel_run_uid FK, created_at)

The bound `package_signature_hash` is the substrate-stored snapshot the M10 verifier compares against the package's current `package_signature_hash` for the §12.7 stale-fixture check.

Per D-M9-5, fixtures are per `metric_contract_version` (not per `metric_contract`). A revised MCV (new MCV row) gets new fixtures; predecessors' fixtures remain addressable but do not vouch for the successor (§12.9).

### 5.2 Column inventory (16 columns)

| Column | Type | NULL | Default | Notes |
|---|---|---|---|---|
| `fixture_uid` | `uuid` | NOT NULL | `gen_random_uuid()` | PRIMARY KEY |
| `metric_contract_uid` | `uuid` | NOT NULL | — | FK to `mcf.metric_contract(metric_contract_uid)` (D-M9-1; redundant with mcv but query-efficient) |
| `metric_contract_version_uid` | `uuid` | NOT NULL | — | FK to `mcf.metric_contract_version(metric_contract_version_uid)` (D-M9-5 — fixtures are per MCV) |
| `section_a_inputs_json` | `jsonb` | NOT NULL | — | Per §12.4 Section A — declared inputs (one typed rowset per declared variable binding); shape per §7.1 below (D-M9-A3) |
| `section_b_expected_output_json` | `jsonb` | NOT NULL | — | Per §12.4 Section B — declared expected output (typed value or rowset); shape per §7.2 below |
| `section_c_resolver_config_json` | `jsonb` | NOT NULL | `'{}'::jsonb` | Per §12.4 Section C — resolver fixture config (computed-dimension configs); JSONB per D-M9-2; default empty `{}` when MC has no computed dimensions (per §9.2 only `fiscal_*` / `bucket_label` / `derived_grain` require config; `calendar_*` and zero-computed-dim MCs need none) |
| `formula_intent_hash` | `text` | NOT NULL | — | sha256 over canonical formula AST per M7/M8 §6 (matches the parent `mcf.metric_contract.formula_intent_hash` column convention; subset of `package_signature_hash` bundle); snapshot at fixture-bind time |
| `variable_binding_set_hash` | `text` | NOT NULL | — | sha256 over canonical variable binding set per M7/M8 §11.1; snapshot at fixture-bind time |
| `grain_filter_temporal_dimension_signature_hash` | `text` | NOT NULL | — | sha256 over canonical (grain entity + filter set + temporal gate + computed-dim refs) per M7/M8 §11.1 intermediate hash; snapshot at fixture-bind time |
| `self_verification_fixture_hash` | `text` | NOT NULL | — | sha256 over canonical (Section A + Section B + Section C) JCS bytes — NEW hash introduced by M9; computed via `computeSelfVerificationFixtureHash()` per §6.4 |
| `bound_package_signature_hash` | `text` | NOT NULL | — | Snapshot of `mcf.metric_contract.package_signature_hash` at fixture-bind time per §12.7 — substrate stores it; M10 verifier compares against current `package_signature_hash` for stale-fixture detection |
| `hash_algorithm_version` | `text` | NOT NULL | — | `mcf-hash-v1` per D-M9-A1 (reuses M7/M8 forever-lock bundle); CHECK enforces format `^mcf-[a-z-]+-v[0-9]+$` matching `mc_hash_algorithm_version_chk` precedent on `mcf.metric_contract` |
| `rationale_text` | `text` | NOT NULL | — | Why this fixture exists / what it exercises (boundary / null / resolver-sensitivity / etc.); ≥40 chars per D-M9-6 |
| `authored_by_name` | `text` | NOT NULL | — | Operator or panel identity (e.g. `anant@selenite.co` or `mcf_authoring_panel_v1`); free-form text |
| `panel_run_uid` | `uuid` | NOT NULL | — | FK to `mcf.metric_authoring_panel_run(panel_run_uid)` per D-M9-4 — panel-only authoring boundary; substrate-enforces no orphan / no operator-direct authoring |
| `created_at` | `timestamptz` | NOT NULL | `now()` | Insert timestamp; immutable via trigger |

**Total: 16 columns** (under D162's 20-column max; matches M5 `metric_authoring_panel_run` sizing of 8 cols + the 4 new sections + 4 new hashes).

### 5.3 No archived_at / no soft-delete

Per operator's design constraint "Immutable after insert via M3-style trigger" + §12.9 immutability + D-M9-5 per-MCV supersession:
- No `archived_at` column — the immutability trigger blocks UPDATE, so soft-delete via column mutation is unreachable.
- Supersession discipline: author a NEW fixture (new `fixture_uid`) for the new MCV; predecessors remain queryable but the M10 verifier's stale-fixture check (§12.6 step 3) routes around them.
- Multiple fixtures per MCV are admitted by design (per §12.8 multi-fixture coverage); UNIQUE on `(mcv, fixture_hash)` prevents duplicate-content fixtures but admits N distinct fixtures per MCV.

### 5.4 Constraint inventory

| Constraint | Type | Definition |
|---|---|---|
| `msvf_pkey` | PRIMARY KEY | `(fixture_uid)` |
| `fk_msvf_mc` | FOREIGN KEY | `metric_contract_uid` → `mcf.metric_contract(metric_contract_uid)` ON DELETE RESTRICT |
| `fk_msvf_mcv` | FOREIGN KEY | `metric_contract_version_uid` → `mcf.metric_contract_version(metric_contract_version_uid)` ON DELETE RESTRICT |
| `fk_msvf_panel_run` | FOREIGN KEY | `panel_run_uid` → `mcf.metric_authoring_panel_run(panel_run_uid)` ON DELETE RESTRICT |
| `msvf_formula_intent_hash_fmt_chk` | CHECK | `formula_intent_hash ~ '^sha256:[0-9a-f]{64}$'` |
| `msvf_variable_binding_set_hash_fmt_chk` | CHECK | `variable_binding_set_hash ~ '^sha256:[0-9a-f]{64}$'` |
| `msvf_grain_filter_temporal_dim_sig_hash_fmt_chk` | CHECK | `grain_filter_temporal_dimension_signature_hash ~ '^sha256:[0-9a-f]{64}$'` |
| `msvf_self_verification_fixture_hash_fmt_chk` | CHECK | `self_verification_fixture_hash ~ '^sha256:[0-9a-f]{64}$'` |
| `msvf_bound_package_signature_hash_fmt_chk` | CHECK | `bound_package_signature_hash ~ '^sha256:[0-9a-f]{64}$'` |
| `msvf_hash_algorithm_version_chk` | CHECK | `hash_algorithm_version ~ '^mcf-[a-z-]+-v[0-9]+$'` (matches `mc_hash_algorithm_version_chk` precedent) |
| `msvf_rationale_min_length_chk` | CHECK | `LENGTH(rationale_text) >= 40` (matches `mcs_rationale_min_length_chk` per D-M9-6) |
| `uq_msvf_mcv_fixture_hash` | UNIQUE | `(metric_contract_version_uid, self_verification_fixture_hash)` — prevents duplicate-content fixtures per MCV; admits N distinct fixtures per MCV per §12.8 |

**Total: 12 constraints** — 1 PK + 3 FK + 7 CHECK (5 sha256 format + 1 algorithm-version regex + 1 rationale-length) + 1 UNIQUE.

### 5.5 Index inventory

| Index | Definition | Purpose |
|---|---|---|
| `idx_mcf_msvf_mcv` | `(metric_contract_version_uid)` | Lookup all fixtures for a MCV (M12 + M10 query pattern) |
| `idx_mcf_msvf_bound_package_hash` | `(bound_package_signature_hash)` | M10 verifier reads fixtures by bound package hash for stale-fixture check (§12.6) |
| `idx_mcf_msvf_panel_run` | `(panel_run_uid)` | Lookup fixtures by authoring panel run (audit / debug) |

(`uq_msvf_mcv_fixture_hash` already provides the (mcv, fixture_hash) lookup path — no separate index needed.)

### 5.6 DDL

```sql
CREATE TABLE mcf.metric_self_verification_fixture (
  fixture_uid                                      uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_contract_uid                              uuid NOT NULL,
  metric_contract_version_uid                      uuid NOT NULL,
  section_a_inputs_json                            jsonb NOT NULL,
  section_b_expected_output_json                   jsonb NOT NULL,
  section_c_resolver_config_json                   jsonb NOT NULL DEFAULT '{}'::jsonb,
  formula_intent_hash                                 text NOT NULL,
  variable_binding_set_hash                        text NOT NULL,
  grain_filter_temporal_dimension_signature_hash   text NOT NULL,
  self_verification_fixture_hash                   text NOT NULL,
  bound_package_signature_hash                     text NOT NULL,
  hash_algorithm_version                           text NOT NULL,
  rationale_text                                   text NOT NULL,
  authored_by_name                                 text NOT NULL,
  panel_run_uid                                    uuid NOT NULL,
  created_at                                       timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT fk_msvf_mc
    FOREIGN KEY (metric_contract_uid)
    REFERENCES mcf.metric_contract(metric_contract_uid)
    ON DELETE RESTRICT,

  CONSTRAINT fk_msvf_mcv
    FOREIGN KEY (metric_contract_version_uid)
    REFERENCES mcf.metric_contract_version(metric_contract_version_uid)
    ON DELETE RESTRICT,

  CONSTRAINT fk_msvf_panel_run
    FOREIGN KEY (panel_run_uid)
    REFERENCES mcf.metric_authoring_panel_run(panel_run_uid)
    ON DELETE RESTRICT,

  CONSTRAINT msvf_formula_intent_hash_fmt_chk
    CHECK (formula_intent_hash ~ '^sha256:[0-9a-f]{64}$'),

  CONSTRAINT msvf_variable_binding_set_hash_fmt_chk
    CHECK (variable_binding_set_hash ~ '^sha256:[0-9a-f]{64}$'),

  CONSTRAINT msvf_grain_filter_temporal_dim_sig_hash_fmt_chk
    CHECK (grain_filter_temporal_dimension_signature_hash ~ '^sha256:[0-9a-f]{64}$'),

  CONSTRAINT msvf_self_verification_fixture_hash_fmt_chk
    CHECK (self_verification_fixture_hash ~ '^sha256:[0-9a-f]{64}$'),

  CONSTRAINT msvf_bound_package_signature_hash_fmt_chk
    CHECK (bound_package_signature_hash ~ '^sha256:[0-9a-f]{64}$'),

  CONSTRAINT msvf_hash_algorithm_version_chk
    CHECK (hash_algorithm_version ~ '^mcf-[a-z-]+-v[0-9]+$'),

  CONSTRAINT msvf_rationale_min_length_chk
    CHECK (LENGTH(rationale_text) >= 40),

  CONSTRAINT uq_msvf_mcv_fixture_hash
    UNIQUE (metric_contract_version_uid, self_verification_fixture_hash)
);

CREATE INDEX idx_mcf_msvf_mcv
  ON mcf.metric_self_verification_fixture (metric_contract_version_uid);

CREATE INDEX idx_mcf_msvf_bound_package_hash
  ON mcf.metric_self_verification_fixture (bound_package_signature_hash);

CREATE INDEX idx_mcf_msvf_panel_run
  ON mcf.metric_self_verification_fixture (panel_run_uid);

COMMENT ON TABLE mcf.metric_self_verification_fixture IS
  'MCF self-verification fixture registry per DBCP M9 §5 + D-M9-1..D-M9-8 + MCF requirements §12 (Self-Verification Fixtures). Per-MCV fixture body (Section A typed input rowsets per declared variable binding + Section B typed expected output + Section C computed-dimension resolver fixture config). Carries 5 hashes: formula_intent_hash + variable_binding_set_hash + grain_filter_temporal_dimension_signature_hash (3 fixture-side snapshots of M7/M8 hashes pinned at fixture-bind time) + self_verification_fixture_hash (sha256 over canonical Section A+B+C JCS bytes per §6.4 — NEW M9 hash) + bound_package_signature_hash (snapshot of mcf.metric_contract.package_signature_hash at fixture-bind time per §12.7 stale-fixture rule; M10 verifier compares against current value). Hash algorithm version mcf-hash-v1 reused per D-M9-A1 (M7/M8 forever-lock bundle). Authoring boundary panel-only per D-M9-4 (panel_run_uid NOT NULL FK to mcf.metric_authoring_panel_run; substrate rejects any insert without a real panel-run reference). Per-MCV via fk_msvf_mcv per D-M9-5 (supersession requires new fixture row; no implicit reuse). UNIQUE (metric_contract_version_uid, self_verification_fixture_hash) prevents duplicate-content fixtures per MCV; admits N distinct fixtures per MCV per §12.8 multi-fixture coverage. rationale_text NOT NULL ≥40 chars per D-M9-6 (matches mcs_rationale_min_length_chk). Append-only / immutable post-INSERT via trigger fn_msvf_immutability_check per §8 (UPDATE/DELETE rejected unconditionally once the row exists; mirrors mcf.fn_mapt_immutability_check pattern from M5; operator design constraint). Substrate-enforced; not service-side. Substrate stays dormant post-apply: M11 ingestion + M12 panel implementation + M10 verifier required before fixture rows flow.';
```

### 5.7 Ownership

`MetricSelfVerificationFixtureWriterService` (future M12 service; NOT in M9 scope). M9 ships the substrate + the C-FX-1..C-FX-11 structural-check engine + the `computeSelfVerificationFixtureHash()` helper (per D-M9-A2) so the substrate is ready when M12 authoring lands.

---

## 6. Fixture hash definition

### 6.1 Five hashes carried by every fixture row

| Hash | Source | Reused or new |
|---|---|---|
| `formula_intent_hash` | M7/M8 `FormulaCanonicalizationService.computeFormulaIntentHash()` over canonical formula AST | **Reused** (snapshot at fixture-bind time) |
| `variable_binding_set_hash` | M7/M8 `PackageSignatureService` over canonical variable binding set | **Reused** (snapshot at fixture-bind time) |
| `grain_filter_temporal_dimension_signature_hash` | M7/M8 `PackageSignatureService` intermediate hash per §11.1 over (grain + filter + temporal gate + computed-dim refs) | **Reused** (snapshot at fixture-bind time) |
| `self_verification_fixture_hash` | NEW M9 — sha256 over canonical (Section A + Section B + Section C) JCS bytes | **NEW** (computed via new helper per §6.4) |
| `bound_package_signature_hash` | M7/M8 `PackageSignatureService.computePackageSignatureHash()` over (formula AST + bindings + grain + filter + temporal gate + computed-dim refs) | **Reused** (snapshot at fixture-bind time per §12.7) |

### 6.2 Why 5 hashes (not 4 or 2)

| Hash | Purpose |
|---|---|
| `formula_intent_hash` | Audit — pin which formula AST this fixture vouches for, independent of binding set / grain |
| `variable_binding_set_hash` | Audit — pin which binding set this fixture asserts (variable name + role + resolved BC + cardinality) |
| `grain_filter_temporal_dimension_signature_hash` | Audit — pin grain + filter + temporal gate + computed-dim composition |
| `self_verification_fixture_hash` | Fixture content identity — UNIQUE per (mcv, fixture-content); the body fingerprint |
| `bound_package_signature_hash` | Stale-fixture detection per §12.7 — M10 verifier's primary comparison key against the package's current hash |

The first three are subsets of the package hash bundle and are stored for forensic/audit purposes (M7/M8 §11.1 makes them addressable directly). `self_verification_fixture_hash` identifies the fixture content. `bound_package_signature_hash` is the §12.7 binding key.

### 6.3 Algorithm version per D-M9-A1

`hash_algorithm_version` carries `mcf-hash-v1` for every fixture row, reusing M7/M8's single-bundle versioning (per M7/M8 §12.4 forever-lock). Any change to the canonicalization or hash composition for any of the 5 hashes requires:
1. A new bundle marker (e.g. `mcf-hash-v2`)
2. An ADR-governed change (per M7/M8 §12.4 §12.4)
3. Migration plan for existing fixtures + verification results (none exist in M9 — substrate dormant)

The format CHECK `msvf_hash_algorithm_version_chk` enforces the bundle marker shape (`^mcf-[a-z-]+-v[0-9]+$`) matching the `mc_hash_algorithm_version_chk` precedent on `mcf.metric_contract`.

### 6.4 `computeSelfVerificationFixtureHash()` helper specification

New helper to extend M7/M8 `PackageSignatureService` (per D-M9-A2; co-located with M9 DDL impl PR):

```typescript
// bc-core/src/registry/mcf/package-signature.service.ts (M9 impl PR — extends existing M7/M8 service)
//
// Adds a new method alongside the existing computePackageSignatureHash().
// Uses the same RFC 8785 JCS canonicalization (mcf-jcs.ts) as the rest of M7/M8.

interface FixtureBodyForHash {
  section_a_inputs: unknown;          // jsonb-equivalent shape — caller provides the operator-asserted Section A
  section_b_expected_output: unknown; // jsonb-equivalent shape — caller provides the operator-asserted Section B
  section_c_resolver_config: unknown; // jsonb-equivalent shape — caller provides the resolver fixture config (or {} for no-config MCs)
}

class PackageSignatureService {
  // existing M7/M8 methods unchanged

  computeSelfVerificationFixtureHash(body: FixtureBodyForHash): string {
    // Canonicalize via RFC 8785 JCS (reuse mcf-jcs.ts)
    const canonicalBytes = jcsSerialize({
      section_a_inputs: body.section_a_inputs,
      section_b_expected_output: body.section_b_expected_output,
      section_c_resolver_config: body.section_c_resolver_config,
    });

    // sha256 → format 'sha256:<64hex>' matching M7/M8 convention
    return `sha256:${sha256Hex(canonicalBytes)}`;
  }
}
```

**Algorithm bundle**: `mcf-hash-v1` (per D-M9-A1).

**Determinism guarantees** (mirrors M7/M8):
- Same input body → same hash, across runs, across executor instances, across language runtimes (RFC 8785 JCS is a standard).
- Key ordering inside each Section JSONB is alphabetized by JCS; map/object key insertion order is not significant.
- Numbers normalized per JCS (no trailing zeros, no `.0` for integers, etc.).
- Strings are UTF-8 NFC-normalized per JCS.

### 6.5 No new canonicalization algorithm

Reuses `mcf-jcs.ts` (RFC 8785 JCS) shipped by M7/M8. The Section A/B/C body is passed through the same JCS function; no new canonicalization machinery is introduced.

---

## 7. Section A / B / C JSON contracts

### 7.1 Section A — Declared inputs (`section_a_inputs_json`)

Per MCF §12.4 Section A, a typed rowset per declared variable binding. JSON shape:

```jsonc
{
  "variables": [
    {
      "variable_role_code": "numerator",           // matches mcf.metric_variable_binding.variable_role_code
      "rowset": [                                  // typed rowset; one element per row
        {
          "grain_keys": { ... },                   // per §12.5 C-FX-5: every row carries the grain entity's identity-bearing key(s)
          "filter_inputs": { ... },                // per §12.5 C-FX-7: every filter clause's referenced BC has a value
          "temporal_anchor": "...",                // per §12.5 C-FX-8: if temporal gate requires a time anchor variable
          "grouping_inputs": { ... },              // per §12.5 C-FX-6: grouping dims either present or computable from Section C
          "value": <typed value>,                  // the variable's typed value (Number / String / Date / etc per BC type)
          "is_null": false                         // per §12.5 C-FX-11: nullability explicit
        },
        // ...more rows
      ],
      "type": "Number",                            // matches binding's resolved BC type
      "unit": "USD",                               // matches binding's unit (where applicable)
      "cardinality": "many"                        // matches binding's expected cardinality (one|many)
    },
    {
      "variable_role_code": "denominator",
      "rowset": [ ... ],
      "type": "Number",
      "unit": "days",
      "cardinality": "many"
    }
    // ...one entry per declared variable binding
  ]
}
```

**Substrate enforcement**: `section_a_inputs_json jsonb NOT NULL` — no schema CHECK at substrate level. JSON-schema validation deferred to M9 impl PR's C-FX-1..C-FX-11 engine (per D-M9-A2 — fail at INSERT time via service-side `validateAndComputeFixtureHash()` that runs C-FX-1..C-FX-11 then computes the hash and INSERTs the row).

**Why no substrate CHECK**: Matches the M5 `consensus_payload_json` rationale (D-M5-7) — schema-level CHECK on JSONB would force a DDL change per binding-type extension. The taxonomy lives in code (TS const + JSON schema) co-located with the C-FX engine.

### 7.2 Section B — Declared expected output (`section_b_expected_output_json`)

Per MCF §12.4 Section B, a typed value or rowset:

```jsonc
{
  "output": {
    "type": "Number",                              // matches MC's declared output type
    "unit": "ratio",                               // matches MC's output unit
    "cardinality": "one",                          // matches MC's output cardinality (one|many)
    "value": 0.42,                                 // expected value per formula evaluated over Section A
    "is_null": false,                              // per §12.5 C-FX-11
    "tolerance": {                                 // per §12.4 — per-fixture tolerance for floating-point comparison
      "mode": "relative_epsilon",                  // 'absolute' | 'relative_epsilon' | 'exact'
      "value": 0.0001                              // tolerance value (interpretation per mode)
    },
    "null_match_policy": "strict"                  // per §12.4 — 'strict' | 'permissive_on_zero_denom' | etc
  }
}
```

For rowset outputs (e.g. per-grain MC output):

```jsonc
{
  "output": {
    "type": "rowset",
    "rowset": [
      { "grain_keys": { ... }, "value": 0.42, "is_null": false },
      { "grain_keys": { ... }, "value": 0.55, "is_null": false }
    ],
    "tolerance": { ... },
    "null_match_policy": "strict"
  }
}
```

### 7.3 Section C — Resolver fixture config (`section_c_resolver_config_json`)

Per MCF §12.4 Section C + §9.2 resolver fixture config requirement, a per-computed-dimension-class config:

```jsonc
{
  "fiscal_calendar": {                             // per §9.2 fiscal_period / fiscal_year / fiscal_quarter
    "calendar_kind": "calendar_month",             // or '4-4-5', 'custom', etc
    "year_start_month": 1,
    "year_start_day": 1,
    "period_boundaries": [ ... ]                   // optional, for custom calendars
  },
  "bucket_specs": {                                // per §9.2 bucket_label
    "aging_bucket_spec_id": "ar_aging_30_60_90"
  },
  "derived_grain_params": { ... }                  // per §9.2 derived_grain
  // calendar_* needs no config per §9.2
}
```

Default `'{}'::jsonb` is admitted when the MC references no computed dimensions (Section C is empty per §12.5 C-FX-9 if no computed dims).

### 7.4 C-FX-1..C-FX-11 structural-check engine specification

Per MCF §12.5 + D-M9-A2 (M9 ships the engine alongside the DDL). Each check fails fast at INSERT time before the row lands:

| # | Check | Implementation note |
|---|---|---|
| C-FX-1 | Variable presence — every declared variable in the package has a corresponding rowset in Section A | Read `mcf.metric_variable_binding` rows for the MCV; assert every `variable_role_code` appears in `section_a_inputs_json.variables[].variable_role_code` |
| C-FX-2 | No extra variables — no Section A rowset has a name not declared in the package's binding set | Reverse of C-FX-1 |
| C-FX-3 | Type/unit/cardinality match — each variable's type, unit, and cardinality match the binding's resolved BC + the package's expected cardinality | Read binding's resolved BC from `mcf.metric_variable_binding.resolved_bc_uid` (or equivalent); compare to Section A entry. **Cardinality source:** `mcf.metric_variable_binding` does not carry a `cardinality_snapshot` column — cardinality is derived from AST context for the `variable_ref` usage (a `variable_ref` inside an `aggregate` node implies `many`; a bare `variable_ref` outside any aggregate implies `one`). Final semantic enforcement belongs to the C-FX checks walking the formula AST + binding row jointly. |
| C-FX-4 | Rowset length alignment — where the formula requires aligned rowsets (e.g. paired numerator/denominator grouped by the same grain), fixtures' rowsets have aligned lengths | Inspect formula AST (`mcf.metric_contract_version.formula_ast_canonical_json`) for paired-variable nodes; assert Section A rowset lengths match grouped by grain key |
| C-FX-5 | Grain keys present — every row in every input rowset carries the grain entity's identity-bearing key(s) | Read `mcf.metric_contract.grain_entity_id`; assert `grain_keys` present in every Section A row |
| C-FX-6 | Grouping dimensions present or computable | Inspect formula AST for grouping ops; assert grouping dim either in `grouping_inputs` or computable from Section C |
| C-FX-7 | Filter inputs present — every filter clause's referenced BC has a value in the input row | Read `mcf.metric_filter_clause` rows; assert each filter's BC has a value in `filter_inputs` |
| C-FX-8 | Temporal anchor inputs present — if temporal gate shape requires a time-anchor variable, it's supplied in Section A | Inspect `mcf.metric_contract.temporal_gate_shape_code` + params; assert temporal anchor in Section A when required |
| C-FX-9 | Resolver fixture config present — every computed dim the package references has a config in Section C | Read `mcf.metric_computed_dimension_ref` rows; assert each computed-dim class has a key in `section_c_resolver_config_json` |
| C-FX-10 | Expected output shape match — Section B output type, unit, and cardinality match the package's declared output shape | Read MC's declared output shape (from MCV body); compare to Section B |
| C-FX-11 | Nullability explicit — every variable and the output declare nullability explicitly | Walk Section A + Section B; assert `is_null` is present (true or false) on every row's `value` |

**Failure mode**: Each C-FX check produces a structured rejection (defect_code + message + payload) that the impl service maps to either:
- An exception at fixture-INSERT time (M9 service path), OR
- A `structural_reject` verification result row (M10 verifier path per §12.6 step 4)

M9 impl PR ships the engine; M9 service path runs it before INSERT; M10 re-runs it before verifier execution.

---

## 8. Immutability trigger design

### 8.1 Pattern source

Per operator's design constraint "Immutable after insert via M3-style trigger". Mirrors:
- M3 `mcf.fn_mvb_active_immutability_check` (child-immutability trigger; permits mutation while parent MCV is draft)
- M5 `mcf.fn_mapt_immutability_check` (unconditional UPDATE/DELETE reject post-INSERT)

M9 trigger follows the M5 pattern (unconditional immutability) — stricter than the M3 conditional pattern. Rationale: fixtures are immutable from the moment of insert per §12.9; there is no fixture state transition that should permit fixture mutation. If the operator needs a revised fixture, author a new fixture row (new `fixture_uid`).

### 8.2 Trigger function

```sql
CREATE OR REPLACE FUNCTION mcf.fn_msvf_immutability_check()
RETURNS TRIGGER AS $$
BEGIN
  -- Per DBCP M9 §8 + MCF §12.9 + Invariant III + operator design constraint:
  -- self-verification fixtures are immutable authoring records used by audit and
  -- by the M10 verifier as the operator-asserted source-of-truth for the
  -- expected-output assertion. UPDATE and DELETE are rejected unconditionally
  -- once the row exists.
  --
  -- This is stricter than mcf.fn_mvb_active_immutability_check (which permits
  -- mutation while the parent MCV is in draft state) because fixture rows are
  -- immutable from the moment of insert — there is no panel-run state transition
  -- or MCV lifecycle transition that should ever permit fixture mutation.
  -- Mirrors mcf.fn_mapt_immutability_check (M5 transcript pattern).
  --
  -- Per D-M9-5 supersession discipline: revising a fixture means authoring a NEW
  -- fixture row (new fixture_uid). The substrate-enforced UNIQUE on
  -- (metric_contract_version_uid, self_verification_fixture_hash) prevents
  -- duplicate-content fixtures per MCV; admits N distinct fixtures per MCV per
  -- §12.8 multi-fixture coverage.
  IF TG_OP = 'UPDATE' THEN
    RAISE EXCEPTION 'mcf.metric_self_verification_fixture fixture_uid=% is immutable; UPDATE rejected (per DBCP M9 §8 + Invariant III)', OLD.fixture_uid
      USING ERRCODE = 'check_violation';
  END IF;
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'mcf.metric_self_verification_fixture fixture_uid=% is immutable; DELETE rejected (per DBCP M9 §8 + Invariant III)', OLD.fixture_uid
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

### 8.3 Trigger attachment

```sql
CREATE TRIGGER trg_msvf_immutability
BEFORE UPDATE OR DELETE ON mcf.metric_self_verification_fixture
FOR EACH ROW EXECUTE FUNCTION mcf.fn_msvf_immutability_check();
```

### 8.4 What about TRUNCATE?

TRUNCATE bypasses row-level triggers but requires explicit ALTER TABLE permissions and is not part of normal application code paths. Defense in depth: production-DB role grants must not include TRUNCATE on `mcf.metric_self_verification_fixture` (deferred to operational policy; not a substrate concern). Same posture as M5 transcript §13.4.

### 8.5 Behavioral verification (in §15)

Post-apply verifier exercises (SAVEPOINT-protected per M-M5-1 verifier-fix recipe):
- INSERT a synthetic fixture row (with synthetic mc + mcv + panel_run prerequisites) → succeeds
- UPDATE the same row → rejected with the expected error message
- DELETE the same row → rejected with the expected error message
- INSERT a second row with the same `(metric_contract_version_uid, self_verification_fixture_hash)` → rejected by `uq_msvf_mcv_fixture_hash` UNIQUE
- INSERT a row with a `panel_run_uid` that doesn't exist in `mcf.metric_authoring_panel_run` → rejected by `fk_msvf_panel_run`

All exercises wrapped in `BEGIN; ... SAVEPOINT ... ROLLBACK TO SAVEPOINT ...; ROLLBACK;` so the substrate remains empty after the verifier completes.

---

## 9. Relationship to M7/M8 hash services

### 9.1 Reuse summary

M9 introduces ONE new hash (`self_verification_fixture_hash`) and reuses three existing M7/M8 hashes as snapshots stored on each fixture row:

| Service | Method | Used for |
|---|---|---|
| `FormulaCanonicalizationService` | `computeFormulaIntentHash(ast)` | `formula_intent_hash` snapshot column |
| `FormulaCanonicalizationService` | `computeVariableBindingSetHash(mcvUid, deps)` | `variable_binding_set_hash` snapshot column |
| `PackageSignatureService` | `computeGrainFilterTemporalDimensionSignatureHash(...)` | `grain_filter_temporal_dimension_signature_hash` snapshot column |
| `PackageSignatureService` | `computePackageSignatureHash(...)` | `bound_package_signature_hash` snapshot column |
| `PackageSignatureService` | `computeSelfVerificationFixtureHash(body)` (NEW per §6.4) | `self_verification_fixture_hash` column |

### 9.2 No M7/M8 service signature changes

The 4 reused methods are called as-is — M9 does not change their signatures or behavior. The only addition is `computeSelfVerificationFixtureHash()` which is a new method on `PackageSignatureService` per §6.4, mirroring the existing methods' shape (input → canonical JCS bytes → sha256 → return formatted hash string).

### 9.3 Algorithm version coupling per D-M9-A1

Fixture's `hash_algorithm_version = 'mcf-hash-v1'` per the single-bundle forever-lock established in M7/M8. The 4 reused hashes already carry this version implicitly (M7/M8 only emits `mcf-hash-v1`). The new `self_verification_fixture_hash` joins the same bundle — any future change to fixture hash canonicalization OR to any of the 4 M7/M8 hashes is an `mcf-hash-v2` event requiring ADR-governed change + migration plan.

### 9.4 Stale-fixture rule mechanics (§12.7)

```text
At fixture-bind time (INSERT to mcf.metric_self_verification_fixture):
  bound_package_signature_hash = (current value of mcf.metric_contract.package_signature_hash)

At M10 verifier-execution time (M10 service — not in scope for M9):
  fixture = SELECT * FROM mcf.metric_self_verification_fixture WHERE self_verification_fixture_hash = $1
  mc = SELECT * FROM mcf.metric_contract WHERE metric_contract_uid = fixture.metric_contract_uid
  IF mc.package_signature_hash <> fixture.bound_package_signature_hash THEN
    RETURN { verdict: 'structural_reject', reason: 'stale_fixture' }
  ELSE
    -- Run package against Section A, apply Section C, compare to Section B
    ...
  END IF
```

The substrate stores the bound hash; the comparison happens at verifier-execution time. M9 ships only the substrate side; M10 implements the comparison.

---

## 10. Relationship to M5 panel substrate

### 10.1 Authoring boundary per D-M9-4

Per D-M9-4, fixture authoring is panel-only. M9 operationalizes this at the substrate via `panel_run_uid NOT NULL` FK to `mcf.metric_authoring_panel_run(panel_run_uid)`:

| Aspect | Decision |
|---|---|
| `panel_run_uid` column | NOT NULL |
| FK target | `mcf.metric_authoring_panel_run(panel_run_uid)` (intra-mcf; in Drizzle) |
| FK name | `fk_msvf_panel_run` |
| ON DELETE | RESTRICT |
| Substrate-enforced consequence | Every fixture row MUST reference a real MCF panel run; no operator-direct or BCF-panel authoring path |

This is stricter than the M9 preflight's recommendation (preflight suggested `panel_run_uid` nullable + service-side enforcement). The operator's D-M9-4 explicitly closes the API path, so substrate-enforces.

### 10.2 Why intra-mcf (Drizzle) and not cross-schema (DDL-only)

Per the M3/M5 cross-schema FK convention (per `mcf.metric_supersession` and `mcf.metric_authoring_panel_run`):
- Cross-schema FKs (mcf → contract) are DDL-only, Drizzle column is plain uuid
- Intra-mcf FKs (mcf → mcf) are declared in Drizzle via `foreignKey()`

`fk_msvf_panel_run` targets `mcf.metric_authoring_panel_run` (intra-mcf), so it is declared in Drizzle. Same for `fk_msvf_mc` and `fk_msvf_mcv`. There are NO cross-schema FKs in M9.

### 10.3 Substrate dormancy

M5 panel substrate is live but dormant (no panel runs written). M9 fixture substrate will be live but dormant (no fixture rows written) until M12 panel implementation ships AND the panel begins generating fixture proposals. The two dormant substrates are FK-coupled (`fk_msvf_panel_run`) — when M12 finally writes a panel run, it can subsequently INSERT a fixture row referencing that panel run; until then both stay empty.

### 10.4 Audit attribution

`mcf.metric_self_verification_fixture.panel_run_uid` provides the audit trail back to the panel run that authored the fixture. Combined with M5's `mcf.metric_authoring_panel_run.consensus_payload_json` (per-model verdicts + defect codes + grounding check) + `mcf.metric_authoring_panel_transcript` (per-agent transcripts), every fixture is fully auditable to the panel session that produced it.

---

## 11. Relationship to M10 verifier engine

### 11.1 Strict M9/M10 boundary

| Surface | Owner | Notes |
|---|---|---|
| `mcf.metric_self_verification_fixture` (table + body + 5 hashes + immutability trigger) | **M9 (this DBCP)** | Fixture authoring substrate |
| `computeSelfVerificationFixtureHash()` helper | **M9 (this DBCP)** | Extends M7/M8 PackageSignatureService |
| C-FX-1..C-FX-11 structural-check engine | **M9 (this DBCP)** per D-M9-A2 | Runs at fixture-INSERT time |
| `mcf.metric_self_verification_result` (table + verdicts + diff trace + executed-at) | **M10** | NOT in M9 scope |
| Verifier service (read package by hash → run AST → compare to Section B → emit verdict) | **M10** | NOT in M9 scope |
| Re-running C-FX-1..C-FX-11 at verifier-execution time per §12.6 step 4 | **M10** (calls M9-shipped engine) | M10 reuses M9's engine; no duplicate implementation |
| Stale-fixture detection (compare `bound_package_signature_hash` to `mcf.metric_contract.package_signature_hash`) per §12.6 step 3 | **M10** | Verifier-time check; M9 ships the substrate column only |
| Activating `fk_mper_verification_result` on `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` | **M10** | Target table is M10's `mcf.metric_self_verification_result`, not M9's `mcf.metric_self_verification_fixture` |

### 11.2 M10 reads M9; M9 does not read M10

M9 ships substrate + structural-check engine + hash helper. M9 does NOT have any read or write dependency on M10's `mcf.metric_self_verification_result`. M10 reads M9's `mcf.metric_self_verification_fixture` to:
- Look up fixture by `self_verification_fixture_hash`
- Compare `bound_package_signature_hash` to the package's current `package_signature_hash` (stale-fixture check)
- Re-run C-FX-1..C-FX-11 (calling the M9-shipped engine)
- Execute the package against Section A applying Section C resolver configs
- Compare actual output to Section B expected output
- Emit a verification result row to `mcf.metric_self_verification_result` (M10's table)

### 11.3 No FK from M9 to M10

There is intentionally NO column on `mcf.metric_self_verification_fixture` pointing at a verification result. The relationship is one-to-many fixture → results, and it lives on M10's `mcf.metric_self_verification_result.fixture_uid` (M10 DBCP will design this column with FK to `mcf.metric_self_verification_fixture(fixture_uid)`).

### 11.4 M4 DBCP doc-bug — folded into M10 DBCP per D-M9-8

**The bug**: M4 DBCP comment on `metric_publication_eligibility_result.satisfying_verification_result_uid` says the deferred FK targets "M9's `mcf.metric_self_verification_result`". The same comment is mirrored in DDL at `bc-core/docker/redesign/06-mcf-lifecycle-certification.sql:179`:

```sql
COMMENT ON COLUMN mcf.metric_publication_eligibility_result.satisfying_verification_result_uid IS
  'PE-MC-10 only: the mcf.metric_self_verification_result row that satisfied this check. FK deferred until M9 ships (D-16). Nullable + FK-less until then; service-layer validation when the table exists.';
```

**Why it's wrong**: `mcf.metric_self_verification_result` is M10, not M9. M9 ships `mcf.metric_self_verification_fixture` only. The `satisfying_verification_result_uid` column will FK to M10's `mcf.metric_self_verification_result`, not M9's `mcf.metric_self_verification_fixture`.

**Why it does not block M9** (per D-M9-8 "unless it blocks M9" qualifier):
- The bug is a comment-only documentation error
- The substrate column `satisfying_verification_result_uid` is FK-less today (deferred until M10)
- M9 ships its own table (`mcf.metric_self_verification_fixture`) with a different name and different role
- M9's substrate has zero FK references back to the M4-commented column
- M9 dry-run and post-apply verifier do not touch the M4 comment
- The bug is benign at substrate level — the comment misnames the future M10 owner, but the substrate column behavior is correct

**Resolution path** (deferred to M10 DBCP per D-M9-8): M10 DBCP corrects the comment when activating the FK from `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` to `mcf.metric_self_verification_result(verification_result_uid)`. The correction lands as a `COMMENT ON COLUMN` UPDATE in the M10 DDL.

---

## 12. DDL apply sequence and rollback story

### 12.1 Forward DDL file

`bc-core/docker/redesign/09-mcf-fixture-substrate.sql` (single file; whole-file `BEGIN/COMMIT` wrapper per the M3-cert-amendment + M5 + M7/M8 atomic-DDL pattern).

### 12.2 Apply sequence (single transaction)

```sql
BEGIN;

-- ─── Step 1: CREATE the new mcf-owned table ─────────────────────────────────
-- Per DBCP M9 §5 — single table with 16 columns, 12 constraints (1 PK + 3 FK +
-- 7 CHECK + 1 UNIQUE), 3 inline FKs (2 to mc/mcv, 1 to panel_run; all intra-mcf).
CREATE TABLE mcf.metric_self_verification_fixture (
  -- 16 columns per §5.6
  ...
  -- 12 constraints per §5.4 (inline)
  ...
);

-- ─── Step 2: CREATE 3 indexes per query patterns ────────────────────────────
-- Per DBCP M9 §5.5 — lookup-by-mcv, lookup-by-bound-package-hash, lookup-by-panel-run.
-- (uq_msvf_mcv_fixture_hash UNIQUE constraint already provides the
-- (mcv, fixture_hash) lookup index.)
CREATE INDEX idx_mcf_msvf_mcv ON mcf.metric_self_verification_fixture (metric_contract_version_uid);
CREATE INDEX idx_mcf_msvf_bound_package_hash ON mcf.metric_self_verification_fixture (bound_package_signature_hash);
CREATE INDEX idx_mcf_msvf_panel_run ON mcf.metric_self_verification_fixture (panel_run_uid);

-- ─── Step 3: Immutability trigger function + attachment ─────────────────────
-- Per DBCP M9 §8 — M3/M5-style unconditional UPDATE/DELETE reject post-INSERT.
-- Operator design constraint "Immutable after insert via M3-style trigger".
CREATE OR REPLACE FUNCTION mcf.fn_msvf_immutability_check() ... ;

CREATE TRIGGER trg_msvf_immutability
BEFORE UPDATE OR DELETE ON mcf.metric_self_verification_fixture
FOR EACH ROW EXECUTE FUNCTION mcf.fn_msvf_immutability_check();

-- ─── Step 4: COMMENT ON TABLE ───────────────────────────────────────────────
COMMENT ON TABLE mcf.metric_self_verification_fixture IS '...' ;

COMMIT;
```

### 12.3 Atomicity rationale

All 4 steps commit together or roll back together. A partial apply would leave the substrate in an inconsistent state:
- Table created but trigger attachment skipped → fixture rows could be UPDATE/DELETE'd, violating §12.9 immutability
- Indexes created without table → impossible (CREATE INDEX would fail first), but the BEGIN/COMMIT enforces all-or-nothing across all 4 steps
- COMMENT skipped → benign but inconsistent with documentation discipline

The whole-file BEGIN/COMMIT wrapper enforces all-or-nothing. Intra-transaction step ordering ensures the table exists before indexes + trigger are attached.

### 12.4 Rollback DDL

`bc-core/docker/redesign/09-mcf-fixture-substrate-rollback.sql` (per the M3/M5/M7-M8 rollback pattern).

**Precondition guard** (refuses if substrate has been used):

```sql
DO $$
DECLARE
  fixture_count integer;
BEGIN
  SELECT COUNT(*) INTO fixture_count FROM mcf.metric_self_verification_fixture;
  IF fixture_count > 0 THEN
    RAISE EXCEPTION 'M9 rollback REFUSED: mcf.metric_self_verification_fixture has % rows. Drop rows first OR accept data loss with manual override.',
      fixture_count
      USING ERRCODE = 'check_violation';
  END IF;
END $$;
```

**Reversal sequence:**

```sql
BEGIN;

-- Step 1: Drop trigger + function
DROP TRIGGER IF EXISTS trg_msvf_immutability ON mcf.metric_self_verification_fixture;
DROP FUNCTION IF EXISTS mcf.fn_msvf_immutability_check();

-- Step 2: Drop the table (drops associated indexes + constraints in CASCADE behavior)
DROP TABLE mcf.metric_self_verification_fixture;

COMMIT;
```

### 12.5 Why no FK activations on existing mcf.* tables

Unlike M5 (which activated 3 deferred FKs on existing mcf.* tables), M9 introduces NO FK on any existing mcf.* table. The only new FKs are on the new table itself (3 inline FKs in CREATE TABLE). No `ALTER TABLE ... ADD CONSTRAINT` outside the new table is required.

The future M10 DBCP will activate `fk_mper_verification_result` on `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` — that activation belongs to M10, not M9.

---

## 13. Drizzle impact

### 13.1 New Drizzle schema file

| File | Purpose |
|---|---|
| `bc-core/src/database/schema/mcf/metric-self-verification-fixture.ts` | Mirrors §5.6 DDL exactly |
| `bc-core/src/database/schema/mcf/index.ts` | Export the new table |

### 13.2 Drizzle FK foreignColumns — all intra-mcf

All 3 FKs are intra-mcf and declared in Drizzle (no cross-schema FKs in M9):

- `fk_msvf_mc` → `mcf.metric_contract(metric_contract_uid)` — Drizzle imports `metricContract` from `./metric-contract`
- `fk_msvf_mcv` → `mcf.metric_contract_version(metric_contract_version_uid)` — Drizzle imports `metricContractVersion` from `./metric-contract-version`
- `fk_msvf_panel_run` → `mcf.metric_authoring_panel_run(panel_run_uid)` — Drizzle imports `metricAuthoringPanelRun` from `./metric-authoring-panel-run`

File-load ordering: alphabetical re-export from `mcf/index.ts` handles this correctly (the 3 target tables all have names lexicographically before `metric-self-verification-fixture`).

### 13.3 Drizzle schema sketch

```typescript
// bc-core/src/database/schema/mcf/metric-self-verification-fixture.ts (M9 impl PR)
import { uuid, text, jsonb, timestamp, index, uniqueIndex, check, foreignKey } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';
import { mcfSchema } from './pg-schema';
import { metricContract } from './metric-contract';
import { metricContractVersion } from './metric-contract-version';
import { metricAuthoringPanelRun } from './metric-authoring-panel-run';

export const metricSelfVerificationFixture = mcfSchema.table(
  'metric_self_verification_fixture',
  {
    fixtureUid: uuid('fixture_uid').primaryKey().default(sql`gen_random_uuid()`),
    metricContractUid: uuid('metric_contract_uid').notNull(),
    metricContractVersionUid: uuid('metric_contract_version_uid').notNull(),
    sectionAInputsJson: jsonb('section_a_inputs_json').notNull(),
    sectionBExpectedOutputJson: jsonb('section_b_expected_output_json').notNull(),
    sectionCResolverConfigJson: jsonb('section_c_resolver_config_json').notNull().default(sql`'{}'::jsonb`),
    formulaIntentHash: text('formula_intent_hash').notNull(),
    variableBindingSetHash: text('variable_binding_set_hash').notNull(),
    grainFilterTemporalDimensionSignatureHash: text('grain_filter_temporal_dimension_signature_hash').notNull(),
    selfVerificationFixtureHash: text('self_verification_fixture_hash').notNull(),
    boundPackageSignatureHash: text('bound_package_signature_hash').notNull(),
    hashAlgorithmVersion: text('hash_algorithm_version').notNull(),
    rationaleText: text('rationale_text').notNull(),
    authoredByName: text('authored_by_name').notNull(),
    panelRunUid: uuid('panel_run_uid').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    foreignKey({
      name: 'fk_msvf_mc',
      columns: [table.metricContractUid],
      foreignColumns: [metricContract.metricContractUid],
    }).onDelete('restrict'),
    foreignKey({
      name: 'fk_msvf_mcv',
      columns: [table.metricContractVersionUid],
      foreignColumns: [metricContractVersion.metricContractVersionUid],
    }).onDelete('restrict'),
    foreignKey({
      name: 'fk_msvf_panel_run',
      columns: [table.panelRunUid],
      foreignColumns: [metricAuthoringPanelRun.panelRunUid],
    }).onDelete('restrict'),
    check('msvf_formula_intent_hash_fmt_chk', sql`${table.formulaIntentHash} ~ '^sha256:[0-9a-f]{64}$'`),
    check('msvf_variable_binding_set_hash_fmt_chk', sql`${table.variableBindingSetHash} ~ '^sha256:[0-9a-f]{64}$'`),
    check('msvf_grain_filter_temporal_dim_sig_hash_fmt_chk', sql`${table.grainFilterTemporalDimensionSignatureHash} ~ '^sha256:[0-9a-f]{64}$'`),
    check('msvf_self_verification_fixture_hash_fmt_chk', sql`${table.selfVerificationFixtureHash} ~ '^sha256:[0-9a-f]{64}$'`),
    check('msvf_bound_package_signature_hash_fmt_chk', sql`${table.boundPackageSignatureHash} ~ '^sha256:[0-9a-f]{64}$'`),
    check('msvf_hash_algorithm_version_chk', sql`${table.hashAlgorithmVersion} ~ '^mcf-[a-z-]+-v[0-9]+$'`),
    check('msvf_rationale_min_length_chk', sql`LENGTH(${table.rationaleText}) >= 40`),
    uniqueIndex('uq_msvf_mcv_fixture_hash').on(table.metricContractVersionUid, table.selfVerificationFixtureHash),
    index('idx_mcf_msvf_mcv').on(table.metricContractVersionUid),
    index('idx_mcf_msvf_bound_package_hash').on(table.boundPackageSignatureHash),
    index('idx_mcf_msvf_panel_run').on(table.panelRunUid),
  ],
);
```

### 13.4 Byte-matching DDL discipline

Mirrors M5 §15.4 + M7/M8 §13.4 — Drizzle template strings must byte-match the DDL:

**Byte-match for stable cases:**
- Simple column DEFAULTs (`'{}'::jsonb`, `now()`, `gen_random_uuid()`) — verifier asserts via `pg_attrdef.adsrc` deep-equal
- Simple CHECK predicates (all 7 in M9 are single-line) — verifier asserts via `pg_get_constraintdef()` byte-equal

**No multi-line CHECKs in M9** — unlike M5's `mapr_reservoir_all_or_none_chk`, all 7 M9 CHECKs are simple single-line predicates (sha256 format regex, algorithm-version regex, rationale-length comparison). The semantic-equivalence carve-out from M5 §15.4 is not needed for M9.

### 13.5 No Drizzle changes for trigger / C-FX engine / hash helper

- The trigger function lives in DDL only (Drizzle has no first-class trigger support)
- The C-FX-1..C-FX-11 engine lives in `bc-core/src/registry/mcf/fixture-structural-check.service.ts` (new file; M9 impl PR)
- The `computeSelfVerificationFixtureHash()` helper extends existing `bc-core/src/registry/mcf/package-signature.service.ts` (modification; M9 impl PR)

---

## 14. Dry-run verifier plan

### 14.1 Script

`bc-core/scripts/mcf-m9-dry-run.mjs` (mirrors M3/M4/M5/M7-M8 dry-run script pattern)

### 14.2 Checks (8 total)

| # | Check | HARD-GATE? |
|---|---|---|
| #1 | M5/M7/M8 substrate prereq — all 14 `mcf.*` tables present AND `mcf.metric_contract_version.formula_ast_canonical_json` column present AND `mcf.metric_authoring_panel_run` present (M5 + M7/M8 applied) | YES |
| #2 | `mcf.metric_self_verification_fixture` does NOT yet exist (clean slate for CREATE) | YES |
| #3 | `mcf.fn_msvf_immutability_check` function does NOT yet exist; `trg_msvf_immutability` trigger does NOT yet exist (clean slate) | YES |
| #4 | All 14 MCF tables empty — no real fixture rows would land + no real metric contract / MCV / panel_run rows to orphan from FK activations | YES |
| #5 | FK targets present: `mcf.metric_contract` + `mcf.metric_contract_version` + `mcf.metric_authoring_panel_run` (regression checks on M2/M5) | (no, advisory) |
| #6 | M9 doc-bug awareness — verifier flags the M4 DBCP doc-bug at `06-mcf-lifecycle-certification.sql:179` for future M10 DBCP attention (informational only; does not fail dry-run) | (no, advisory) |
| #7 | Forward DDL parse + statement counts: 1 `CREATE TABLE` + 3 `CREATE INDEX` + 1 `CREATE OR REPLACE FUNCTION` + 1 `CREATE TRIGGER` + 1 `COMMENT ON TABLE` + BEGIN/COMMIT. (No `ALTER TABLE` outside the new table; no `UPDATE` data statements.) | (no, but parse failure = abort) |
| #8 | DDL sha256 captured (forward + rollback) for drift detection | always pass; recording artifact |

### 14.3 No pre-amendment artifact needed

Unlike M3 cert-amendment + M7/M8 (which mutate existing triggers / columns), this DBCP only CREATEs new substrate. There is no pre-state to snapshot for rollback restoration — the rollback simply DROPs everything M9 created.

### 14.4 Exit codes

| Exit | Meaning |
|---|---|
| 0 | All checks PASS |
| 1 | DATABASE_URL not set |
| 2 | DDL file not found |
| 3-10 | Per-check failure |
| 20 | Hard-gate refused (M5 + M7/M8 not applied OR partial M9 apply detected) |
| 21 | Unexpected error |

---

## 15. Post-apply verifier plan

### 15.1 Script

`bc-core/scripts/mcf-m9-post-apply-verification.mjs`

### 15.2 Checks (13 total — SAVEPOINT-protected per M-M5-1 verifier-fix discipline)

**Structural (1–5):**

| # | Check |
|---|---|
| #1 | `mcf.metric_self_verification_fixture` present with 16 columns + 7 CHECKs + 3 FKs + 1 UNIQUE + 3 indexes. All 7 CHECKs verified via byte-match against `pg_get_constraintdef()` (no multi-line CHECKs — semantic-equivalence carve-out from M5 §15.4 not needed). |
| #2 | All 3 FKs active: `fk_msvf_mc` → `mcf.metric_contract(metric_contract_uid)` ON DELETE RESTRICT, `fk_msvf_mcv` → `mcf.metric_contract_version(metric_contract_version_uid)` ON DELETE RESTRICT, `fk_msvf_panel_run` → `mcf.metric_authoring_panel_run(panel_run_uid)` ON DELETE RESTRICT |
| #3 | UNIQUE `uq_msvf_mcv_fixture_hash` on `(metric_contract_version_uid, self_verification_fixture_hash)` present |
| #4 | All 3 indexes present: `idx_mcf_msvf_mcv`, `idx_mcf_msvf_bound_package_hash`, `idx_mcf_msvf_panel_run` |
| #5 | Trigger function `mcf.fn_msvf_immutability_check` present + attached to `metric_self_verification_fixture` as `trg_msvf_immutability` BEFORE UPDATE OR DELETE |

**Behavioral (6–12) — SAVEPOINT-protected synthetic-row exercises per M-M5-1 verifier-fix recipe:**

Each behavioral check wraps negative assertions in `tx.savepoint(async (sp) => { ... })` so a check_violation from one assertion does NOT abort the entire transaction. Recipe per `bc-core/scripts/mcf-m5-post-apply-verification.mjs` (patched in PR #113 / `10e8b95`).

| # | Check |
|---|---|
| #6 | Synthetic prereq insert: INSERT a `contract.panel_output_record` row + `mcf.metric_authoring_panel_run` row + `mcf.metric_contract` row + `mcf.metric_contract_version` row → all succeed. (Wrapped in outer BEGIN; ROLLBACK to clean up.) |
| #7 | INSERT a valid fixture row referencing those prereqs → succeeds. Verifier captures the new fixture_uid + asserts all 5 hash columns + bound_package_signature_hash all pass sha256 format CHECK + rationale_text passes length CHECK + algorithm_version passes format CHECK. |
| #8 | (SAVEPOINT-protected) UPDATE the inserted fixture row → REJECTED by trigger `fn_msvf_immutability_check`; assert error message contains `'is immutable; UPDATE rejected'` |
| #9 | (SAVEPOINT-protected) DELETE the inserted fixture row → REJECTED by trigger; assert error message contains `'is immutable; DELETE rejected'` |
| #10 | (SAVEPOINT-protected) INSERT a second fixture row with the SAME `(metric_contract_version_uid, self_verification_fixture_hash)` → REJECTED by `uq_msvf_mcv_fixture_hash` UNIQUE; assert error code is unique violation |
| #11 | (SAVEPOINT-protected) INSERT a fixture row with `panel_run_uid` referencing a NON-EXISTENT panel run → REJECTED by `fk_msvf_panel_run`; assert error message cites `fk_msvf_panel_run` |
| #12 | (SAVEPOINT-protected) INSERT a fixture row with `rationale_text = 'short'` (under 40 chars) → REJECTED by `msvf_rationale_min_length_chk`; assert error message cites the CHECK constraint |

**Cleanup (13):**

| # | Check |
|---|---|
| #13 | All **15 mcf.* tables** (10 pre-M5 + 4 M5 + 1 new M9) empty after verifier completes. Behavioral exercises (#6 onwards) all rolled back; existing `contract.panel_output_record` 24 BCF rows untouched; existing mcf.* tables remain at 0 rows. |

### 15.3 Exit codes

| Exit | Meaning |
|---|---|
| 0 | All 13 checks PASS |
| 1 | DATABASE_URL not set |
| 3-15 | Per-check failure (check_number + 2) |
| 16 | Unexpected error |

### 15.4 SAVEPOINT-protection discipline (per M-M5-1)

Per the M5 verifier false-negative diagnostic (see `mcf-m5-apply-closeout.md` §4.1):

- Negative assertions inside a single `sql.begin(async (tx) => {...})` block can cause cascade failure: when one assertion raises `check_violation`, postgres marks the entire tx as failed; subsequent assertions return `'current transaction is aborted, commands ignored until end of transaction block'` rather than their own constraint rejection messages.
- **Fix**: Wrap each negative assertion in `tx.savepoint(async (sp) => {...})`. If the SAVEPOINT body throws (expected for negative tests), postgres rolls back to SAVEPOINT; outer tx remains usable for subsequent assertions.
- M9 verifier ships with this pattern from the start (no patch cycle needed).

### 15.5 Synthetic prerequisite setup complexity (per L4 review note)

Each behavioral exercise in §15.2 #6–#12 requires a 4-row synthetic prerequisite-setup chain before the fixture INSERT can be attempted:

1. `contract.panel_output_record` row (BCF-shared substrate; the M5 verifier already exercises this insert path — recipe reusable)
2. `mcf.metric_authoring_panel_run` row (M5; 1:1 PK FK to row 1)
3. `mcf.metric_contract` row (M2; `grain_entity_id` may be a random uuid per the M2 design note *"No physical FK from `mcf.metric_contract.grain_entity_id` to `concept_registry.entity`"*; `temporal_gate_shape_code` must be in the enum, e.g. `'instantaneous'`)
4. `mcf.metric_contract_version` row (M2/M7; `formula_ast_canonical_json` picks up the M7 placeholder default `'{"kind":"placeholder","reason":"created_before_m7_apply"}'::jsonb`; `governance_state_code` picks up the default `'draft'`)

Then the fixture INSERT (or the negative-test INSERTs for #10/#11/#12) can run. This is more wiring than M5's 2-INSERT chain (which only set up `contract.panel_output_record` + `mcf.metric_authoring_panel_run`). All 4+1 INSERTs happen inside the outer `BEGIN; ... ROLLBACK;` so the substrate stays empty after the verifier exits; negative-test assertions are individually SAVEPOINT-wrapped per §15.4.

The M9 impl PR's verifier script should carry a `setupSyntheticPrereqs(tx)` helper that emits valid values for all 4 prerequisite rows, with synthetic values documented in script comments for future maintenance.

---

## 16. Risks and mitigations

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M9-1 | **C-FX-1..C-FX-11 structural checks not exhaustive** — fixture passes C-FX but M10 verifier fails on a corner case | Medium | Iterate via M10 evidence per build plan §M9 primary risk; M9 DBCP enumerates all 11 checks + positive/negative test pairs in §7.4 + post-apply verifier §15.2 #7+#12. M10 re-runs the engine per §12.6 step 4 (defense in depth). |
| R-M9-2 | **`self_verification_fixture_hash` canonicalization drift from M7/M8 JCS** — if the new helper somehow uses different canonicalization than M7/M8 hashes, fixture hashes won't match across runs | Low | Helper reuses `mcf-jcs.ts` (the M7/M8 RFC 8785 JCS module) unchanged; same algorithm-version bundle marker `mcf-hash-v1` per D-M9-A1. Cross-method byte-equal test in impl PR's unit suite confirms identical canonicalization. |
| R-M9-3 | **`bound_package_signature_hash` snapshot semantics** — if the snapshot is taken at the wrong moment (e.g. fixture INSERT vs panel proposal vs operator-confirm), stale-fixture rule misfires | Low | DBCP §6.4 + §9.4 + §12.7 lock the semantics: snapshot is taken at fixture INSERT time, mirroring the package's current `package_signature_hash` value at that instant. M12 service path must NOT recompute or modify it; impl PR's service-side tests assert the snapshot equals `mcf.metric_contract.package_signature_hash` at the moment of INSERT. |
| R-M9-4 | **Substrate-enforced `panel_run_uid NOT NULL` blocks operator-direct authoring path** — if M12 needs to support a non-panel authoring path later, schema change required | Low (intentional) | This is per D-M9-4 by design. Operator-direct authoring is explicitly out of M9 scope. Future operator decision to admit non-panel authoring → schema amendment to make `panel_run_uid` nullable + add a new attribution column (e.g. `operator_direct_authoring_record_uid`). |
| R-M9-5 | **`section_c_resolver_config_json` empty default `'{}'::jsonb` admits MCs with computed dims to author fixtures missing required resolver configs** — substrate doesn't enforce C-FX-9 at INSERT time | Medium | C-FX-9 enforcement lives in the M9 impl PR's structural-check engine (per D-M9-A2), which runs BEFORE the INSERT. Substrate default exists only to admit no-computed-dim MCs (where Section C IS legitimately empty). M9 verifier #12 includes a positive test confirming a fixture with computed dims + missing Section C is rejected by the engine. |
| R-M9-6 | **Multi-fixture coverage discipline (§12.8 / §19.13 Q37) lands later** — current substrate admits 1..N fixtures per MCV; future Q37 decision may strengthen to "at least N for ratio metrics", "at least M for windowed metrics", etc | Low | M9 substrate admits 1..N per MCV — no upper or lower bound enforced. Q37 decisions land as service-side discipline (M12 panel rule) OR a future fixture-pack envelope amendment (D-M9-C deferred). Either path is compatible with M9 substrate. |
| R-M9-7 | **Fixture immutability discipline diverges from §12.9** — operator's design constraint + M3-style trigger enforces unconditional immutability post-INSERT; §12.9 spec admits revision until a passing PE-MC-10 result is cited | Low (intentional divergence) | §12.9 admits limited mutability ("permitted only before the fixture has produced a `pass` result that has been cited by a PE-MC-10 evaluation"). M9 substrate enforces STRICTER discipline (unconditional immutability) per operator design constraint. Rationale: the conditional mutability path requires reading downstream M10 verification + M13 PE-MC-10 result; M9 substrate cannot model this without a circular FK to M10/M13 tables (not yet existing). For v1, "author a new fixture for a new fixture_uid" is the supersession path. A future post-M13 amendment may relax to §12.9 semantics if operationally needed. |

### 16.1 Stop conditions

The M9 implementation PR STOPS and re-frames if:

- §19.13 Q37 (minimum-fixture-coverage per formula class) lands before M9 impl PR — may reshape the substrate (potentially add a pack table per D-M9-C)
- Build plan §M9 scope changes materially (e.g. adds reservoir-provenance on fixtures)
- M10 DBCP opens first — M9 stays consistent with M10's verifier-side hash expectations

---

## 17. Operator approvals for implementation PR (O-M9-1..O-M9-9)

Before the M9 implementation PR opens, the operator approves these 9 items:

| # | Approval item |
|---|---|
| **O-M9-1** | Confirm D-M9-1 (D-M9-B single mcf-owned fixture registry table) + reject D-M9-A (static files) + defer D-M9-C (fixture-pack envelope) |
| **O-M9-2** | Confirm `mcf.metric_self_verification_fixture` 16-column shape + 7 CHECKs (5 sha256 format + 1 algorithm-version regex + 1 rationale-length ≥40) + 3 FKs (mc/mcv/panel_run all intra-mcf in Drizzle) + 1 UNIQUE (mcv, fixture_hash) + 3 indexes |
| **O-M9-3** | Confirm D-M9-A3 — 3 separate JSONB columns for Section A / B / C (not 1 combined column) |
| **O-M9-4** | Confirm D-M9-A1 — reuse `mcf-hash-v1` algorithm version bundle for `self_verification_fixture_hash` (no `mcf-fixture-v1` separate bundle) |
| **O-M9-5** | Confirm D-M9-A2 — C-FX-1..C-FX-11 structural-check engine ships in M9 impl PR (co-located with DDL); M10 reuses the M9 engine |
| **O-M9-6** | Confirm `panel_run_uid NOT NULL` per D-M9-4 (panel-only authoring boundary enforced at substrate; no operator-direct authoring path in M9) |
| **O-M9-7** | Confirm M3/M5-style unconditional UPDATE/DELETE-reject trigger per operator design constraint (stricter than §12.9 conditional-mutability spec; rationale per R-M9-7) |
| **O-M9-8** | Confirm DDL atomicity — all 4 steps inside one `BEGIN/COMMIT` per §12.2; rollback DDL has row-count precondition guard refusing if any fixture row exists |
| **O-M9-9** | Approve the next gate: M9 implementation PR (NO DB APPLY) — ships substrate + C-FX engine + `computeSelfVerificationFixtureHash()` helper + dry-run + post-apply verifier scripts |

---

## 18. Recommended next gate

### 18.1 Recommendation: open M9 implementation PR (NO DB APPLY)

The implementation PR ships:

1. `bc-core/docker/redesign/09-mcf-fixture-substrate.sql` (forward DDL per §12.2)
2. `bc-core/docker/redesign/09-mcf-fixture-substrate-rollback.sql` (rollback DDL per §12.4)
3. `bc-core/src/database/schema/mcf/metric-self-verification-fixture.ts` (Drizzle schema per §13.3)
4. `bc-core/src/database/schema/mcf/index.ts` (re-export update)
5. `bc-core/src/registry/mcf/package-signature.service.ts` (extension — add `computeSelfVerificationFixtureHash()` method per §6.4)
6. `bc-core/src/registry/mcf/package-signature.service.spec.ts` (unit tests — golden-vector + canonicalization-determinism tests for new method)
7. `bc-core/src/registry/mcf/fixture-structural-check.service.ts` (NEW — C-FX-1..C-FX-11 engine per §7.4)
8. `bc-core/src/registry/mcf/fixture-structural-check.service.spec.ts` (NEW — 11 positive + 11 negative tests per check)
9. `bc-core/scripts/mcf-m9-dry-run.mjs` (8 checks per §14.2)
10. `bc-core/scripts/mcf-m9-post-apply-verification.mjs` (13 checks per §15.2 — SAVEPOINT-protected from the start)

**Suggested PR title:** `feat(mcf): M9 Self-Verification Fixture Substrate — metric_self_verification_fixture + C-FX-1..C-FX-11 engine + computeSelfVerificationFixtureHash (NO DB APPLY)`

### 18.2 Sequencing per established pattern

1. M9 DBCP → operator review → 9 approvals O-M9-1..O-M9-9 ← **THIS DBCP**
2. M9 implementation PR (NO DB APPLY)
3. M9 small-DDL apply gate (separate operator-authorized session)
4. M9 evidence PR + bc-docs-v3 closeout

### 18.3 What unblocks after M9

- **M10** — verifier engine + `mcf.metric_self_verification_result` substrate (depends on M9 fixture substrate)
- **M11** — reservoir ingestion (independent; can run in parallel after M9 lands per D-M9-7 sequencing)
- **PE-MC-10** evaluation (M13) — depends on M10, which depends on M9
- **Future post-M10 amendment** — M4 DBCP doc-bug correction folded into M10 DBCP per D-M9-8

---

## 19. What stays closed

| | |
|---|---|
| M9 impl PR | not opened by this DBCP |
| M9 DDL apply | pending impl PR |
| M9 evidence PR | pending apply |
| **M10 deterministic verifier service** | CLOSED — gated on M9 substrate; separate gate |
| **M10 `mcf.metric_self_verification_result` substrate** | CLOSED — M10 owns; not M9 |
| **M10 activation of `fk_mper_verification_result`** | CLOSED — M10 owns; target table doesn't exist until M10 |
| **M11 reservoir ingestion DBCP** | CLOSED — sequenced after M9 per D-M9-7 |
| **M12 Metric Authoring Panel implementation** | CLOSED — gated on M5 + M7 + M9 + M10 + M11 |
| **M13 PE-MC evaluator** | CLOSED — gated on M5 + M7 + M9 + M10 |
| **M14+** | CLOSED |
| **Real MCF metric contracts** | CLOSED — substrate stays empty through M9 apply |
| **Real fixtures** | CLOSED — substrate stays empty through M9 apply |
| **BCF data changes** | CLOSED — no `contract.*` / `concept_registry.*` touches |
| **§19.13 Q37 minimum-fixture-coverage per formula class** | OPEN (per MCF §19.13); not a M9 dependency |
| **§12.9 conditional fixture mutability (mutable until passing PE-MC-10 cite)** | DEFERRED — M9 enforces stricter unconditional immutability per operator design constraint (see R-M9-7); future post-M13 amendment may relax |
| **M4 DBCP doc-bug correction** | DEFERRED to M10 DBCP per D-M9-8; non-blocking for M9 (see §11.4) |
| **D-M9-C fixture-pack envelope** | DEFERRED — revisit if Q37 lands |
| **Operator-direct authoring path** | CLOSED — D-M9-4 panel-only boundary; future amendment if needed |
| **MCF defect-code v2 taxonomy** | CLOSED — v1 pinned |
| **MCF hash algorithm v2 bump** | CLOSED — `mcf-hash-v1` forever-locked unless ADR-governed change |
