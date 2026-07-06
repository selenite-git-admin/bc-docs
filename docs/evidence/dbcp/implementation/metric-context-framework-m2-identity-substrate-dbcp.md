---
uid: metric-context-framework-m2-identity-substrate-dbcp
title: Metric Context Framework (MCF) — M2 Identity Substrate DBCP Design
description: Design-only Database Change Protocol for MCF Gate M2 — Identity Substrate. Proposes the mcf schema and five identity-bearing tables (mcf.metric_contract, mcf.metric_contract_version, mcf.metric_variable_binding, mcf.metric_filter_clause, mcf.metric_computed_dimension_ref) plus DDL COMMENT annotations on the three core legacy SQL MC tables per M2 preflight P1. Includes hash and identity rules, immutability/state boundary with M3, BCF Registry reference strategy, Drizzle/bc-core implementation notes (no code), DDL sequence proposal, rollback story, verification requirements for future execution, and risks/open questions. Authority anchor: DEC-c3e57f (D422). Locked positions consumed: M2 preflight P1 (3-table COMMENT scope) + P2 (candidate_source_ref_json with CHECK on source_type). Status proposed; awaits operator approval before any future M2-execution gate writes DDL into bc-core or runs migrations.
status: proposed
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: m2-dbcp-design
---

# Metric Context Framework (MCF) — M2 Identity Substrate DBCP Design

> **Revision note (2026-05-26):** Two operator-locked clarifications applied to this design after initial commit `a4b25a5`. (1) Hash columns on `mcf.metric_contract` are nullable in M2 (was NOT NULL): `formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash`, `identity_tuple_hash`, `package_signature_hash`, `hash_algorithm_version`. Writer services populate as authoring progresses; M3 enforces NOT NULL once `governance_state_code='approved'`. Partial UNIQUE on `identity_tuple_hash` updated to include `AND identity_tuple_hash IS NOT NULL`. (2) M2 execution DDL ships explicit `COMMENT ON COLUMN` statements declaring M3 / M7 / M8 / M9 ownership boundaries on every column reserved-for-but-not-enforced-by-M2 (per new §11.5). Naming stays (`governance_state_code` retained); discipline becomes visible at the substrate level.

## 1. Scope and status

### 1.1 Status

**Proposed.** This is a design-only DBCP. No DDL is executed by this document. No bc-core schema files are edited. No migration is written. The DBCP proposes the M2 substrate shape for operator review; a separate M2 execution gate (later) would author the `bc-core/src/database/schema/mcf/*.ts` Drizzle files, write the `bc-core/docker/redesign/*.sql` DDL block, and run the migration after explicit operator approval per CLAUDE.md Database Change Protocol.

### 1.2 In scope (Gate M2)

- New `mcf` schema creation.
- Five new identity-bearing tables: `mcf.metric_contract`, `mcf.metric_contract_version`, `mcf.metric_variable_binding`, `mcf.metric_filter_clause`, `mcf.metric_computed_dimension_ref`.
- Identity tuple UNIQUE enforcement per MCF requirements §4.2.
- Hash columns (`formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash`, `identity_tuple_hash`, `package_signature_hash`) with hash-algorithm-version column.
- Closed-enum CHECK constraints where applicable.
- DDL `COMMENT ON TABLE` markers on three legacy SQL MC tables per M2 preflight P1.
- Lifecycle column placeholder (M3 enforces semantics).
- Drizzle / bc-core implementation file-layout proposal (no code).
- DDL sequence proposal + rollback story.

### 1.3 Explicitly out of scope (other gates own)

- **M3** — Lifecycle / certification substrate: `mcf.metric_contract_revision`, `mcf.metric_supersession`, immutability triggers, cert reuse pattern for MCF `action_code='metric_create'`.
- **M4** — Publication eligibility substrate: `mcf.metric_publication_eligibility_result`, cert reuse for `metric_transition`, operator-confirm rule policy entries.
- **M5** — Panel / workbench substrate: `mcf.metric_authoring_panel_run` (with reservoir-provenance fields per D422 guardrail 6), `mcf.metric_authoring_panel_transcript`, `mcf.workspace_tool_allowlist`, `mcf.evidence_source_allowlist`.
- **M6** — Tenant binding / MLS integration: `mcf.tenant_binding`.
- **M7** — Formula AST authoring service: AST taxonomy implementation, normalization, identity-hash computation logic, bind-time check implementation. M7 service POPULATES `formula_intent_hash` on the M2 substrate column.
- **M8** — Package signature service: composite `package_signature_hash` computation logic per MCF §8.7. M8 service POPULATES the M2 substrate column.
- **M9** — Self-verification fixture substrate: `mcf.metric_self_verification_fixture` + structural-check engine.
- **M11** — Reservoir ingestion service: reads M2 substrate column `candidate_source_ref_json` indirectly via M5 panel-run records.
- **M12-M20** — panel implementation, PE-MC evaluator, publication, supersession, console, etc.

M2 ships the **columns and constraints**; later gates populate and govern them.

---

## 2. Grounding and decisions consumed

### 2.1 Authority anchor

**ADR DEC-c3e57f / D422** — Foundational MCF ADR (commit `155ed4f`). All ten decisions inform this DBCP; specifically:

- Decision 1 (Framework scope) → `mcf` schema is correct ownership.
- Decision 2 (Post-D418 stance) → no FK from `mcf.*` to legacy SQL MC tables; P1 COMMENT annotations on legacy.
- Decision 3 (Reservoirs vs authority) → `candidate_source_ref_json` field shape (P2).
- Decision 5 (Formula authority) → `formula_intent_hash` column ships in M2; M7 service populates.
- Decision 7 (Layered activation gates) → governance_state_code placeholder for M3.
- Decision 8 (BCF boundary) → MCF cannot write `concept_registry.*`; binding columns reference BCF ids only.
- Decision 10 (Guardrails) → guardrail 6 (reservoir provenance) supported by P2 column.

### 2.2 MCF requirements sections

- **§4 MCF identity model** — identity tuple definition (§4.2); supersession-vs-revision boundary (§4.6); composite-grain edge case (§4.8).
- **§6 BCF variable-binding model** — binding shapes (§6.2); bind-time compatibility checks (§6.3); grain as typed Entity reference (§6.5).
- **§7 Formula AST requirements** — AST closed taxonomy (§7.2); immutability per Foundation Invariant III (§7.4).
- **§8 Formula normalization and identity hash** — normalization rules (§8.2); identity hash construction (§8.4); algorithm versioning (§8.6); composite package signature hash (§8.7).
- **§9 Computed dimensions** — closed-set computed-dimension classes (§9.2); resolver fixture config requirement (§9.2 subsection).
- **§10 Lifecycle and immutability model** — five-state Foundation lifecycle (§10.1); supersession with explicit successor pointer (§10.5).
- **§12 Self-verification fixtures** — package signature hash binds fixtures (§12.7); referenced by package_signature_hash column.
- **§13 PE-MC publication eligibility** — PE-MC-1..PE-MC-10 evaluator (M11) reads M2 substrate.
- **§17 Required substrate tables** — table list and conceptual descriptions consumed by M2.

### 2.3 MCF build plan

- **Gate M2 — Identity substrate DBCP** per build plan §4.2: `mcf.metric_contract` + identity-tuple UNIQUE + `mcf.metric_contract_version` + `mcf.metric_variable_binding` + `mcf.metric_filter_clause` + `mcf.metric_computed_dimension_ref`. Plus M8 package signature substrate (per build plan §4.3 — partially anticipated in M2 via the `package_signature_hash` column).

### 2.4 M2 preflight decisions (commit `1987306`)

- **P1 — Legacy SQL MC corpus marker (Option B):** DDL `COMMENT ON TABLE` on three core tables: `contract.metric_contract`, `contract.metric_contract_version`, `metric.metric_binding`. NOT extended to `metric.metric_formula` or `metric.metric_contract_approval` unless M2 discovers necessity.
- **P2 — Source/provenance reference (Option C with CHECK):** `mcf.metric_contract.candidate_source_ref_json jsonb NULL`. Non-authoritative; outside identity tuple; outside `package_signature_hash`; not PE-MC-1-citable. Closed `source_type` enum enforced via CHECK constraint on JSONB if practical (`jsonb_field->>'source_type'` IN enum); fallback to generated column or documented validation service.

---

## 3. Legacy SQL MC corpus annotation

### 3.1 Proposed DDL — `COMMENT ON TABLE` (P1 = Option B, 3-table scope)

```sql
COMMENT ON TABLE contract.metric_contract IS
  'HISTORICAL / PRE-MCF — non-authoritative per ADR DEC-c3e57f (D422) Decision 2. '
  'Future MCF metric contracts live in mcf.metric_contract. This table remains '
  'queryable for historical reference. No new rows expected. 778 of 780 rows '
  'archived as of 2026-05-26.';

COMMENT ON TABLE contract.metric_contract_version IS
  'HISTORICAL / PRE-MCF — non-authoritative per ADR DEC-c3e57f (D422) Decision 2. '
  'Future MCF versions live in mcf.metric_contract_version. This table remains '
  'queryable for historical reference. 1,022 rows including 729 active MCVs on '
  'archived parent MCs (pre-MCF data state).';

COMMENT ON TABLE metric.metric_binding IS
  'HISTORICAL / PRE-MCF — non-authoritative per ADR DEC-c3e57f (D422) Decision 2. '
  'Future MCF variable-grain bindings live in mcf.metric_variable_binding (which '
  'is variable-grain, not CC-grain). This table remains queryable for historical '
  'reference. 1,133 rows.';
```

### 3.2 What this annotation does NOT do

- **No data mutation.** Zero rows touched.
- **No column add.** Table structure unchanged.
- **No constraint add.** No new triggers, no new indexes.
- **No FK from `mcf.*` to any of these tables.** They are historical-only.
- **No automated migration trigger.** No `mcf.*` code path reads these tables as input.

### 3.3 Why three tables, not more

Per M2 preflight P1 scope-lock: `metric.metric_formula` is deferred until the AST service design (M7) starts because the formula text disposition may need its own treatment. `metric.metric_contract_approval` has 0 rows (gap survey Q-1) and is not added unless M2 execution discovers active tooling references — which is unlikely given its empty state.

---

## 4. New schema

### 4.1 Proposed DDL

```sql
CREATE SCHEMA IF NOT EXISTS mcf;
COMMENT ON SCHEMA mcf IS
  'Metric Context Framework substrate. MCF authors metric meaning and metric-context packages '
  'per ADR DEC-c3e57f (D422). Owned by MCF Framework Approval discipline. BCF cannot write here.';
```

### 4.2 Ownership and search_path

- **Owner:** the bc-core platform DB role (`barecount` per local dev convention). Same role that owns `contract`, `metric`, `master`, `runtime`, `source` schemas.
- **search_path:** `mcf` is added to search_path for the bc-core write user. Per CLAUDE.md D162, schemas are explicit in query references where possible; search_path is a convenience for repository code.
- **Read-only for tooling:** the `bc-postgres` MCP allowlist should be extended to include `mcf` when M2 ships. This is a `bc-pg-mcp` configuration change (not in M2 scope; flagged as follow-on).

### 4.3 What M2 creates

**M2 creates the `mcf` schema AND the five identity tables in a single DBCP transaction.** Separating "schema only" from "schema + tables" adds no value — the identity tables have no dependencies outside their own FKs.

The M2 DBCP transaction is atomic: either all five tables land with the schema, or none does (rollback to pre-M2 state).

---

## 5. Table: `mcf.metric_contract`

The identity-bearing parent row. One row per distinct MCF metric contract (in MCF's identity-tuple sense per §4.2).

### 5.1 Column list (17 columns; under D162 max-20 limit)

| # | Column | Type | Constraints | Role |
|---|---|---|---|---|
| 1 | `metric_contract_uid` | `uuid` | PK NOT NULL | Atomically allocated UID |
| 2 | `mc_name` | `text` | NOT NULL | Operator-friendly handle (e.g. `mc__dso`) |
| 3 | `display_name` | `text` | nullable | Human-readable display name |
| 4 | `grain_entity_id` | `uuid` | NOT NULL | BCF Entity ref (soft FK — see §12) |
| 5 | `formula_intent_hash` | `text` | **nullable** (NOT NULL enforced by M3 once active) | `sha256:hex...`; populated by M7 AST service write |
| 6 | `variable_binding_set_hash` | `text` | **nullable** (NOT NULL enforced by M3 once active) | Composed from `mcf.metric_variable_binding` rows by M7 binding service |
| 7 | `filter_set_hash` | `text` | **nullable** (NOT NULL enforced by M3 once active) | Composed from `mcf.metric_filter_clause` rows by M7 filter service |
| 8 | `temporal_gate_shape_code` | `text` | NOT NULL, CHECK enum | Closed enum: `instantaneous`, `trailing_window`, `period_aggregate`, etc. |
| 9 | `temporal_gate_params_json` | `jsonb` | nullable | Params per shape (e.g. `{"length":30,"unit":"day"}` for trailing_window) |
| 10 | `identity_tuple_hash` | `text` | **nullable** (NOT NULL enforced by M3 once active); UNIQUE basis when populated | sha256 over the full identity tuple; populated by M7 identity service |
| 11 | `package_signature_hash` | `text` | **nullable** (NOT NULL enforced by M3 once active) | Composite per MCF §8.7; **populated by M8 package signature service — column reserved in M2, M8 service ships separately** |
| 12 | `hash_algorithm_version` | `text` | **nullable** (NOT NULL enforced by M3 once active) | E.g. `mcf-package-hash-v1` — applies to all hash columns; populated when first hash is computed |
| 13 | `candidate_source_ref_json` | `jsonb` | nullable, CHECK source_type enum | Non-authoritative provenance per P2 |
| 14 | `created_at` | `timestamptz` | NOT NULL DEFAULT now() | |
| 15 | `updated_at` | `timestamptz` | NOT NULL DEFAULT now() | |
| 16 | `created_by_name` | `text` | nullable | Operator name from authoring context |
| 17 | `archived_at` | `timestamptz` | nullable | Soft delete per D162 |

### 5.2 Constraints

- `PRIMARY KEY (metric_contract_uid)`
- `CREATE UNIQUE INDEX idx_mcf_mc_identity_active ON mcf.metric_contract (identity_tuple_hash, hash_algorithm_version) WHERE archived_at IS NULL AND identity_tuple_hash IS NOT NULL` — **partial unique** enforcing "only one active row per identity tuple, once the identity is computed". The `IS NOT NULL` clause is essential because hash columns are nullable during draft/authoring (per §10.2 revised); UNIQUE only applies when the writer service has populated the identity hash. This is the core identity-uniqueness constraint per MCF §4.2.
- `CHECK temporal_gate_shape_code IN ('instantaneous', 'trailing_window', 'period_aggregate', 'point_in_time', 'as_of', 'rolling_window')` — closed enum per MCF §4.4. Exact enum values are an M7+ refinement (open question §17.5).
- `CHECK candidate_source_ref_json IS NULL OR (candidate_source_ref_json->>'source_type') IN ('seed_metric', 'metric_definition', 'operator_direct', 'legacy_metric_contract', 'other')` — closed source_type enum per P2.
- `CHECK hash_algorithm_version ~ '^mcf-[a-z-]+-v[0-9]+$'` — algorithm-version string discipline (e.g. `mcf-package-hash-v1`).
- **NO FK to `concept_registry.entity`** — service-level validation per §12.
- **NO FK to legacy `metric.*` tables** — historical-only per D422 Decision 2.

### 5.3 Indexes (beyond constraints)

- `CREATE INDEX idx_mcf_mc_grain_entity ON mcf.metric_contract (grain_entity_id)` — for grain-entity-grouped reads (e.g. "all MCs grounded on Sales Order Line").
- `CREATE INDEX idx_mcf_mc_archived_at ON mcf.metric_contract (archived_at) WHERE archived_at IS NULL` — partial index for active-row queries.
- `CREATE INDEX idx_mcf_mc_mc_name ON mcf.metric_contract (mc_name)` — for human-handle lookup.

### 5.4 Triggers

- **None in M2.** Immutability enforcement on identity-bearing columns when lifecycle reaches `active` is M3 scope (M3 owns the `metric_contract_revision` table + the immutability triggers).
- M2 does NOT install the BEFORE UPDATE trigger that blocks identity-column mutations.

---

## 6. Table: `mcf.metric_contract_version`

Descriptive-only version body per MCF §4.6. Versions exist for descriptive revisions; identity changes are supersession (new parent row).

### 6.1 Column list (15 columns)

| # | Column | Type | Constraints | Role |
|---|---|---|---|---|
| 1 | `metric_contract_version_uid` | `uuid` | PK NOT NULL | Atomically allocated |
| 2 | `metric_contract_uid` | `uuid` | NOT NULL FK | Parent MC reference |
| 3 | `version_code` | `text` | NOT NULL | Semver-like, e.g. `v1.0.0` |
| 4 | `version_seq` | `int` | NOT NULL | Monotonic per parent |
| 5 | `is_current` | `boolean` | NOT NULL DEFAULT false | Only one current per parent |
| 6 | `description_text` | `text` | nullable | Operator-attached description (weak hint context per D422) |
| 7 | `function_code` | `text` | nullable | Business function (e.g. `finance`) |
| 8 | `subfunction_code` | `text` | nullable | Business subfunction (e.g. `accounts_receivable`) |
| 9 | `owner_json` | `jsonb` | nullable | Owner info (team, contact) |
| 10 | `tags` | `text[]` | nullable | Operator tags |
| 11 | `threshold_json` | `jsonb` | nullable | Threshold spec (descriptive; NOT identity-bearing per MCF §4.7) |
| 12 | `governance_state_code` | `text` | NOT NULL DEFAULT 'draft' | Lifecycle placeholder for M3 |
| 13 | `created_at` | `timestamptz` | NOT NULL DEFAULT now() | |
| 14 | `created_by_name` | `text` | nullable | |
| 15 | `supersedes_version_uid` | `uuid` | nullable FK | Predecessor version pointer (M3 enforces semantics) |

### 6.2 Constraints

- `PRIMARY KEY (metric_contract_version_uid)`
- `FOREIGN KEY (metric_contract_uid) REFERENCES mcf.metric_contract(metric_contract_uid) ON DELETE RESTRICT` — versions cannot orphan; supersession is the only termination path.
- `FOREIGN KEY (supersedes_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` — predecessor chain integrity.
- `CREATE UNIQUE INDEX idx_mcf_mcv_version_code ON mcf.metric_contract_version (metric_contract_uid, version_code)` — no duplicate version per parent.
- `CREATE UNIQUE INDEX idx_mcf_mcv_current ON mcf.metric_contract_version (metric_contract_uid) WHERE is_current = TRUE` — exactly one current per parent.
- `CHECK governance_state_code IN ('draft', 'review', 'approved', 'active', 'superseded')` — Foundation lifecycle 5-state per MCF §10.1.
- `CHECK version_seq > 0`

### 6.3 Indexes

- `CREATE INDEX idx_mcf_mcv_mc_uid ON mcf.metric_contract_version (metric_contract_uid)` — for version-list-by-parent reads.
- `CREATE INDEX idx_mcf_mcv_governance_state ON mcf.metric_contract_version (governance_state_code)` — for lifecycle queries.

### 6.4 Lifecycle ownership boundary

- M2 ships the `governance_state_code` column with the CHECK enum.
- M2 does NOT ship transition-rule triggers (M3 owns `'draft' → 'review' → 'approved' → 'active' → 'superseded'` validity).
- M2 does NOT ship `'active' immutability` triggers (M3 owns).
- M2 documents in this DBCP that `governance_state_code` is a placeholder that M3 wires.

---

## 7. Table: `mcf.metric_variable_binding`

Per-variable binding per MCF §6. Binding rows are version-scoped (per operator brief §7).

### 7.1 Column list (13 columns)

| # | Column | Type | Constraints | Role |
|---|---|---|---|---|
| 1 | `metric_variable_binding_uid` | `uuid` | PK NOT NULL | |
| 2 | `metric_contract_version_uid` | `uuid` | NOT NULL FK | Version parent |
| 3 | `variable_role_code` | `text` | NOT NULL | E.g. `I1`, `I2`, `O1`, `C1` |
| 4 | `role_kind_code` | `text` | NOT NULL CHECK | `input` / `output` / `constant` |
| 5 | `bound_business_concept_id` | `uuid` | nullable | BCF BC reference (for input/output) |
| 6 | `bound_entity_id` | `uuid` | nullable | BCF Entity reference (for grain-binding variables) |
| 7 | `constant_value_json` | `jsonb` | nullable | For role_kind='constant' per D329 |
| 8 | `representation_term_snapshot` | `text` | nullable | BC's representation term at bind time (audit) |
| 9 | `unit_code_snapshot` | `text` | nullable | BC's unit at bind time (audit) |
| 10 | `data_type_snapshot` | `text` | nullable | BC's data type at bind time (audit) |
| 11 | `bind_time_check_results_json` | `jsonb` | nullable | Audit of §6.3 checks |
| 12 | `structural_sort_key` | `text` | NOT NULL | Canonicalization key for `variable_binding_set_hash` |
| 13 | `created_at` | `timestamptz` | NOT NULL DEFAULT now() | |

### 7.2 Constraints

- `PRIMARY KEY (metric_variable_binding_uid)`
- `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` — bindings cannot orphan.
- `CREATE UNIQUE INDEX idx_mcf_mvb_role ON mcf.metric_variable_binding (metric_contract_version_uid, variable_role_code)` — variable role unique per version.
- `CHECK role_kind_code IN ('input', 'output', 'constant')`.
- `CHECK ((role_kind_code = 'constant' AND constant_value_json IS NOT NULL AND bound_business_concept_id IS NULL AND bound_entity_id IS NULL) OR (role_kind_code IN ('input', 'output') AND constant_value_json IS NULL AND (bound_business_concept_id IS NOT NULL OR bound_entity_id IS NOT NULL)))` — role-kind / binding-target consistency.
- **NO FK to `concept_registry.*`** — service-level validation per §12.
- **NO free-text BC references** — `bound_business_concept_id` is uuid only.

### 7.3 Hash contribution

Rows in `mcf.metric_variable_binding` for a given `metric_contract_version_uid` are canonicalized by `structural_sort_key`, serialized per row as `(variable_role_code, role_kind_code, bound_business_concept_id || bound_entity_id || constant_value_json, representation_term_snapshot, unit_code_snapshot)`, concatenated, and hashed by the M7 binding service to produce `variable_binding_set_hash` on `mcf.metric_contract`.

### 7.4 Identity-immutability discipline

Per MCF §4.6, variable bindings are identity-bearing. Two versions of the SAME MC (same parent) MUST have identical variable bindings (because identity-bearing fields don't change across versions). The M7+ writer service enforces this by:

1. Computing `variable_binding_set_hash` from the new version's rows.
2. Comparing against the parent's stored `variable_binding_set_hash`.
3. Rejecting the version write if hashes don't match — that change is supersession (new parent MC), not revision.

This discipline lives in the service, not the substrate. M2 substrate stores the rows; service enforces immutability across versions.

---

## 8. Table: `mcf.metric_filter_clause`

Per-filter clause per MCF §4.5. Filter set canonicalization is identity-bearing.

### 8.1 Column list (9 columns)

| # | Column | Type | Constraints | Role |
|---|---|---|---|---|
| 1 | `metric_filter_clause_uid` | `uuid` | PK NOT NULL | |
| 2 | `metric_contract_version_uid` | `uuid` | NOT NULL FK | Version parent |
| 3 | `clause_role_code` | `text` | NOT NULL CHECK | `where` / `having` / `pre_filter` |
| 4 | `clause_expression_json` | `jsonb` | NOT NULL | Typed expression shape |
| 5 | `bound_business_concept_id` | `uuid` | nullable | BC the clause references |
| 6 | `operator_code` | `text` | NOT NULL CHECK | Closed enum: `eq`, `ne`, `lt`, `lte`, `gt`, `gte`, `in`, `not_in`, `is_null`, `is_not_null`, `between` |
| 7 | `literal_value_json` | `jsonb` | nullable | Typed literal value (for non-null/not-null operators) |
| 8 | `structural_sort_key` | `text` | NOT NULL | Canonicalization key for `filter_set_hash` |
| 9 | `created_at` | `timestamptz` | NOT NULL DEFAULT now() | |

### 8.2 Constraints

- `PRIMARY KEY (metric_filter_clause_uid)`
- `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT`
- `CHECK clause_role_code IN ('where', 'having', 'pre_filter')`
- `CHECK operator_code IN ('eq', 'ne', 'lt', 'lte', 'gt', 'gte', 'in', 'not_in', 'is_null', 'is_not_null', 'between')` — closed enum; exact set is M7+ refinement.
- `CHECK ((operator_code IN ('is_null', 'is_not_null') AND literal_value_json IS NULL) OR (operator_code NOT IN ('is_null', 'is_not_null') AND literal_value_json IS NOT NULL))` — operator-literal consistency.

### 8.3 Indexes

- `CREATE INDEX idx_mcf_mfc_version ON mcf.metric_filter_clause (metric_contract_version_uid)` — for version-list-of-filters reads.
- `CREATE INDEX idx_mcf_mfc_bc ON mcf.metric_filter_clause (bound_business_concept_id)` — for impact analysis when a BC is superseded.

### 8.4 Hash contribution

Rows for a given version are canonicalized by `structural_sort_key`, serialized per row as `(clause_role_code, operator_code, bound_business_concept_id, canonical(literal_value_json))`, concatenated, and hashed by service to produce `filter_set_hash` on `mcf.metric_contract`.

Empty filter set has a sentinel hash (e.g. `sha256:e3b0c44...` of empty string) so identity tuple computation always has a value.

---

## 9. Table: `mcf.metric_computed_dimension_ref`

Per-computed-dim reference per MCF §9. Computed-dim references are identity-bearing.

### 9.1 Column list (9 columns)

| # | Column | Type | Constraints | Role |
|---|---|---|---|---|
| 1 | `metric_computed_dimension_ref_uid` | `uuid` | PK NOT NULL | |
| 2 | `metric_contract_version_uid` | `uuid` | NOT NULL FK | Version parent |
| 3 | `dimension_class_code` | `text` | NOT NULL CHECK | Closed enum per MCF §9.2 |
| 4 | `resolver_config_ref_json` | `jsonb` | NOT NULL | Reference to governing config (e.g. `{"config_type":"tenant_fiscal_calendar","artifact_table":"organization.fiscal_calendar_config"}`) |
| 5 | `resolver_params_hash` | `text` | NOT NULL | Hash over canonical resolver params |
| 6 | `role_in_formula_code` | `text` | NOT NULL CHECK | `grain` / `filter` / `group_by` |
| 7 | `source_business_concept_id` | `uuid` | nullable | BC for source data (e.g. posting_date BC for fiscal_period) |
| 8 | `structural_sort_key` | `text` | NOT NULL | Canonicalization key |
| 9 | `created_at` | `timestamptz` | NOT NULL DEFAULT now() | |

### 9.2 Constraints

- `PRIMARY KEY (metric_computed_dimension_ref_uid)`
- `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT`
- `CHECK dimension_class_code IN ('fiscal_period', 'fiscal_year', 'fiscal_quarter', 'calendar_quarter', 'calendar_week_iso', 'derived_grain', 'bucket_label')` — closed v1 enum per MCF §9.2.
- `CHECK role_in_formula_code IN ('grain', 'filter', 'group_by')`.

### 9.3 Relation to MCF §9 computed dimensions

The `dimension_class_code` enum aligns with MCF §9.2 closed set. `resolver_config_ref_json` is a structured pointer that the M9 verifier service uses to substitute fixture configs at verification time. `source_business_concept_id` (e.g. the posting_date BC for fiscal_period) is the BCF input the resolver reads.

D365 runtime prerequisite (D422 Decision 9): `contract.canonical_contract.posting_date_field` must be populated for runtime evaluation of fiscal-period MCs. This is a build-plan prerequisite, NOT enforced by M2 substrate.

### 9.4 Hash contribution

Rows are canonicalized into `grain_filter_temporal_dimension_signature_hash` (per MCF §8.7), which composes into `package_signature_hash` on `mcf.metric_contract`.

---

## 10. Hash and identity rules

### 10.1 Hash inventory

Five hash values stored on `mcf.metric_contract`, plus `hash_algorithm_version`:

| Hash | Source | Computed by | Where stored |
|---|---|---|---|
| `formula_intent_hash` | Normalized formula AST (M7 service input) | M7 AST authoring service | `mcf.metric_contract.formula_intent_hash` |
| `variable_binding_set_hash` | `mcf.metric_variable_binding` rows for current version | M7 binding service | `mcf.metric_contract.variable_binding_set_hash` |
| `filter_set_hash` | `mcf.metric_filter_clause` rows for current version | M7 filter service | `mcf.metric_contract.filter_set_hash` |
| `identity_tuple_hash` | Composite over (grain_entity_id, formula_intent_hash, variable_binding_set_hash, temporal_gate_shape_code, canonical(temporal_gate_params_json), filter_set_hash) | M7 identity service | `mcf.metric_contract.identity_tuple_hash` — **UNIQUE basis** |
| `package_signature_hash` | Composite per MCF §8.7 | M8 package signature service | `mcf.metric_contract.package_signature_hash` |

### 10.2 Computation discipline

- **Hash columns are nullable in M2 substrate; populated as authoring progresses.** A new MC starts with hash columns NULL during the draft phase; M7 binding service populates `variable_binding_set_hash` and `filter_set_hash` as bindings/filters are written; M7 AST service populates `formula_intent_hash` when the AST is composed; M7 identity service populates `identity_tuple_hash` when all identity-bearing fields are stable; M8 package signature service populates `package_signature_hash` last. **No hash is required to be populated for an MC to exist in `draft` state.** M3 lifecycle enforcement (later) trigger-checks that all hash columns are NOT NULL once `governance_state_code` reaches `'approved'` or `'active'`.
- **Service-computed, never client-trusted.** M7 (formula AST + binding + filter + identity) and M8 (package signature) services own the canonicalization + hash logic. The M2 substrate accepts hash values from writers but does not compute them.
- **Substrate-enforced consistency.** M2 ships CHECK constraints on hash format when populated (e.g. `formula_intent_hash IS NULL OR formula_intent_hash ~ '^sha256:[0-9a-f]{64}$'`); but does NOT trigger-recompute hashes (that's service work).
- **Deterministic canonicalization.** Algorithm version (`mcf-package-hash-v1`) covers all hashes for v1; future bumps increment the version. `hash_algorithm_version` is nullable in M2 alongside the hashes; once any hash is populated, `hash_algorithm_version` must be populated; service enforces this at write time.
- **UNIQUE constraint behavior under nullability.** Per §5.2, the partial UNIQUE index on `identity_tuple_hash` includes `WHERE identity_tuple_hash IS NOT NULL`, so multiple draft-state rows with NULL identity hashes coexist. Once identity is computed, the UNIQUE enforces single-active-MC-per-identity.

### 10.3 Identity tuple hash basis (UNIQUE)

The partial UNIQUE index on `mcf.metric_contract`:

```sql
CREATE UNIQUE INDEX idx_mcf_mc_identity_active
  ON mcf.metric_contract (identity_tuple_hash, hash_algorithm_version)
  WHERE archived_at IS NULL AND identity_tuple_hash IS NOT NULL;
```

Composite UNIQUE on `(identity_tuple_hash, hash_algorithm_version)` allows future algorithm-version migrations without collision across versions. The `identity_tuple_hash IS NOT NULL` predicate is essential because hash columns are nullable during draft (per §10.2); multiple draft-state rows with NULL identity hashes are permitted and coexist.

### 10.4 Package signature hash (M8 anticipation)

Per build plan, M8 is a separate gate that ships the composite `package_signature_hash` computation logic. M2 **reserves the column** as nullable; M8 ships the SERVICE that populates it.

For M2 acceptance: M2 enforces nothing on `package_signature_hash` directly — the column is nullable and the M2 substrate accepts rows with NULL value. Fixture binding per MCF §12.7 requires the hash to be populated, but that requirement applies at fixture-creation time (M9 substrate), not at MC-row-write time. M3 lifecycle enforcement (later) checks `package_signature_hash IS NOT NULL` when `governance_state_code` reaches `'approved'`.

The hash value itself is service-computed by M8 once the AST + bindings + grain + filters + temporal gate + computed-dim refs are all stable.

Open question (§17.5): should `package_signature_hash` be in M2 or M8? **Locked position per operator clarification: column in M2 (nullable, M8 populates); service in M8.**

### 10.5 What hashes are NOT in M2

- **`self_verification_fixture_hash`** — fixture content hash. Belongs to M9 fixture substrate, not M2.
- **`workbench_fingerprint_hash`** — panel-run hash. Belongs to M5 panel substrate, not M2.
- **`per_agent_transcript_hash`** — panel-run hash. Belongs to M5, not M2.

---

## 11. Immutability and state boundary

### 11.1 What M2 enforces now

- Column-level CHECK constraints on closed enums (lifecycle states, dimension classes, operator codes, etc.).
- Partial UNIQUE on `identity_tuple_hash` for active rows.
- UNIQUE on `(metric_contract_uid, version_code)` for versions.
- Partial UNIQUE on `is_current = TRUE` per parent.
- FK integrity on parent-child relationships.

### 11.2 What M3 enforces later

- **BEFORE UPDATE triggers** on `mcf.metric_contract` blocking identity-bearing column updates when any version is `governance_state_code='active'`.
- **BEFORE UPDATE triggers** on `mcf.metric_contract_version` blocking body changes when state is `'active'`.
- **Transition validity triggers** enforcing `'draft' → 'review' → 'approved' → 'active' → 'superseded'`.
- **`mcf.metric_supersession` table** with explicit predecessor → successor edges (M3 scope).
- **`mcf.metric_contract_revision` table** for descriptive-only revisions (M3 scope per MCF §17.1).

### 11.3 Lifecycle column placeholder

M2 ships `governance_state_code text NOT NULL DEFAULT 'draft'` with a CHECK enum but NO transition trigger. M3 wires the trigger later.

Why placeholder rather than defer entirely: most consumer reads (M16 console, M5 panel-run records) need the state column to exist NOW so they can filter / display. Shipping the column in M2 with documented "M3 enforces semantics" is cleaner than M3 having to add a NOT NULL column with defaults later.

### 11.4 Active-immutability narrative

M2 does NOT enforce "active rows are immutable" at the substrate level. This is intentional:
- M3 owns immutability triggers.
- Until M3 lands, active-row immutability is service-discipline (the writer service does not issue UPDATE statements against active rows).
- Once M3 ships, the trigger enforces structurally.

The interim (M2 shipped, M3 not yet) is acceptable because the writer service is the only path; no other code path writes to `mcf.*` substrate.

### 11.5 DDL `COMMENT ON COLUMN` discipline for M3/M8-owned placeholders

To make M3 and M8 ownership boundaries visible at the substrate level — not buried in this DBCP — the M2 execution DDL ships explicit `COMMENT ON COLUMN` statements on every column that is reserved-for-but-not-enforced-by-M2. A reader who runs `\d+ mcf.metric_contract` or queries `information_schema.columns.column_comment` sees the ownership-boundary inline.

**M3-owned placeholder columns** (lifecycle, transitions, immutability — M2 reserves, M3 enforces):

```sql
COMMENT ON COLUMN mcf.metric_contract_version.governance_state_code IS
  'Lifecycle placeholder per ADR DEC-c3e57f (D422). M2 substrate ships the column '
  'with CHECK enum (draft | review | approved | active | superseded). Transition validity '
  'and activation authority are enforced by M3 lifecycle substrate (mcf.metric_contract_revision '
  '+ mcf.metric_supersession + immutability triggers). This column does not '
  'represent enforced lifecycle until M3 ships. Until M3, the writer service is the only '
  'path; service-side discipline holds.';

COMMENT ON COLUMN mcf.metric_contract_version.supersedes_version_uid IS
  'Predecessor version pointer placeholder per ADR DEC-c3e57f (D422). M2 substrate '
  'ships the column with FK to mcf.metric_contract_version. Supersession semantics '
  '(when a predecessor pointer is required; supersession side effects; chain validity) '
  'are enforced by M3 supersession service. This column does not enforce supersession '
  'semantics until M3 ships.';
```

**M7/M8-owned hash placeholder columns** (computation, population, NOT NULL once active — M2 reserves, M7/M8 services populate):

```sql
COMMENT ON COLUMN mcf.metric_contract.formula_intent_hash IS
  'Reserved per ADR DEC-c3e57f (D422). Populated by M7 AST authoring service when '
  'the formula AST is composed and normalized. Nullable in M2; M3 lifecycle '
  'enforcement adds NOT NULL when governance_state_code reaches approved.';

COMMENT ON COLUMN mcf.metric_contract.variable_binding_set_hash IS
  'Reserved per ADR DEC-c3e57f (D422). Populated by M7 binding service from '
  'mcf.metric_variable_binding rows for the current version. Nullable in M2; '
  'M3 lifecycle enforcement adds NOT NULL when governance_state_code reaches approved.';

COMMENT ON COLUMN mcf.metric_contract.filter_set_hash IS
  'Reserved per ADR DEC-c3e57f (D422). Populated by M7 filter service from '
  'mcf.metric_filter_clause rows. Nullable in M2; M3 lifecycle enforcement adds '
  'NOT NULL when governance_state_code reaches approved.';

COMMENT ON COLUMN mcf.metric_contract.identity_tuple_hash IS
  'Reserved per ADR DEC-c3e57f (D422). Populated by M7 identity service from '
  'grain_entity_id + formula_intent_hash + variable_binding_set_hash + temporal_gate_shape_code '
  '+ canonical(temporal_gate_params_json) + filter_set_hash. UNIQUE basis when populated '
  '(partial unique index idx_mcf_mc_identity_active includes WHERE identity_tuple_hash IS NOT NULL). '
  'Nullable in M2; M3 lifecycle enforcement adds NOT NULL when governance_state_code reaches approved.';

COMMENT ON COLUMN mcf.metric_contract.package_signature_hash IS
  'Reserved per ADR DEC-c3e57f (D422) and MCF requirements §8.7. Composite signature '
  'computed by M8 package signature service. M2 substrate reserves the column as '
  'nullable; M8 service ships separately and populates this column once the package '
  '(AST + bindings + grain + filters + temporal gate + computed-dim refs) is stable. '
  'Fixture binding per MCF §12.7 reads this hash; M9 fixture substrate enforces fixture-to-package '
  'hash equality. M3 lifecycle enforcement adds NOT NULL when governance_state_code reaches approved.';

COMMENT ON COLUMN mcf.metric_contract.hash_algorithm_version IS
  'Reserved per ADR DEC-c3e57f (D422). Applies uniformly to all hash columns on this row. '
  'Nullable in M2; populated by the first hash-computing service to write to this row. '
  'M3 lifecycle enforcement adds NOT NULL when governance_state_code reaches approved.';
```

**M9-owned reference column** (computed-dim resolver — M2 reserves, M9 fixture verifier reads):

```sql
COMMENT ON COLUMN mcf.metric_computed_dimension_ref.resolver_config_ref_json IS
  'Reserved per ADR DEC-c3e57f (D422) and MCF requirements §9. Reference to the '
  'governing config artifact (e.g. tenant fiscal calendar). M9 verifier service '
  'substitutes a fixture-scoped resolver config at verification time per MCF §12.4 '
  'Section C. M2 substrate stores the reference; M9 service reads and applies.';
```

**Substrate-level visibility** (every reader sees the ownership boundary). The COMMENTs are part of the M2 execution DDL block; they ship in the same transaction as the table creations and become queryable via `information_schema.columns.column_comment` and `pg_description`.

---

## 12. BCF Registry references

### 12.1 The question

`mcf.metric_contract.grain_entity_id` references a BCF `concept_registry.entity` row. `mcf.metric_variable_binding.bound_business_concept_id` references `concept_registry.business_concept`. Should these be physical FKs?

### 12.2 Recommendation: service-level validation, no physical FK (for v1)

**Reasons:**

- **BCF lifecycle semantics.** BCF rows have lifecycle (`draft`, `review`, `approved`, `active`, `superseded`). MCF binds to **active** rows only. A physical FK enforces existence (any row), not active state. So the FK alone is insufficient.
- **BCF supersession is a normal operation.** When BCF supersedes a BC, MCF bindings continue to reference the predecessor uid (per Foundation Invariant III — historical references stay addressable). A FK that resists supersession-driven cleanup is friction.
- **Cross-schema FK adds platform/tenant boundary considerations.** Future moves of `concept_registry` schema (unlikely but not impossible) become harder with FKs.
- **MCF cannot write `concept_registry.*` (D422 Decision 8).** FK or no FK, MCF is read-only on BCF substrate.

**Discipline:**

- M7 binding service validates that `bound_business_concept_id` resolves to an **active** `concept_registry.business_concept` row at bind time.
- M7 grain service validates that `grain_entity_id` resolves to an **active** `concept_registry.entity` row at bind time.
- Validation is recorded in `mcf.metric_variable_binding.bind_time_check_results_json` (audit).
- M3 supersession flow (later) updates MCF bindings to successor BCs via operator-confirm supersession path; does NOT auto-mutate active MCF MCs (per Foundation Invariant III).

### 12.3 Future revisit

Open question §17.1: revisit FK feasibility after M3 lands. If BCF supersession patterns are stable + readable from a `concept_registry.entity_active` materialized view, a FK to that view would catch the "row exists" case without the active-state issue. Defer to post-M3.

### 12.4 What M2 ships re BCF refs

- `grain_entity_id uuid NOT NULL` on `mcf.metric_contract` (no FK).
- `bound_business_concept_id uuid` and `bound_entity_id uuid` (both nullable, mutually exclusive per CHECK) on `mcf.metric_variable_binding` (no FK).
- `bound_business_concept_id uuid` on `mcf.metric_filter_clause` (no FK).
- `source_business_concept_id uuid` on `mcf.metric_computed_dimension_ref` (no FK).

All BCF references are uuid columns; service validates resolution at write time.

---

## 13. Drizzle / bc-core implementation notes

### 13.1 Proposed file layout (for future M2-execution gate)

```
bc-core/
├── docker/redesign/
│   ├── 01-platform-db.sql                  (existing — bc_platform_dev base)
│   ├── 02-tenant-db.sql                    (existing — tbc_*_dev base)
│   ├── 03-runtime.sql                      (existing — runtime substrate)
│   └── 04-mcf-substrate.sql                (NEW — M2 substrate DDL)
└── src/database/schema/
    ├── concept-registry/                    (existing BCF substrate)
    ├── contract/                            (existing legacy + chain status)
    ├── metric/                              (existing legacy + MLS substrate)
    └── mcf/                                 (NEW — M2 substrate Drizzle)
        ├── index.ts                         (barrel export)
        ├── metric-contract.ts
        ├── metric-contract-version.ts
        ├── metric-variable-binding.ts
        ├── metric-filter-clause.ts
        └── metric-computed-dimension-ref.ts
```

### 13.2 Repository / service boundary (no code in this DBCP)

The M2-execution gate (later) would add:

- `bc-core/src/mcf/metric-contract.repository.ts` — read-only repository for MCF metric contracts.
- `bc-core/src/mcf/metric-contract-version.repository.ts` — read-only repository for versions.
- `bc-core/src/mcf/metric-variable-binding.repository.ts` — read-only repository for bindings.
- Writer services are M7+ scope (formula AST, binding, package signature, etc.) — they call writer methods on the repositories, but the substrate accepts writes through the SERVICES-ONLY discipline per CLAUDE.md.

No service code is authored in M2-execution. M2-execution ships only the schema + DDL + repository skeletons. Writer services land in M7+.

### 13.3 Naming conventions

Per CLAUDE.md D162 + DEC-69f09e / D148:
- snake_case for column names: `metric_contract_uid`, `formula_intent_hash`, `created_at`.
- PKs: `{entity}_uid` (e.g. `metric_contract_uid`) — note `uid` not `id` since DevHub UIDs are first-class.
- Codes: `{noun}_code` (e.g. `temporal_gate_shape_code`, `dimension_class_code`).
- Booleans: `is_{adj}` (e.g. `is_current`).
- Timestamps: `{verb}_at` (e.g. `created_at`, `updated_at`, `archived_at`).
- JSON: `{noun}_json` (e.g. `candidate_source_ref_json`, `clause_expression_json`).
- Tables: singular (e.g. `metric_contract`, not `metric_contracts`).
- Indexes: `idx_{schema}_{table}_{cols}` (e.g. `idx_mcf_mc_identity_active`).
- FKs: implicit name via Postgres; explicit name where multi-FK on same table (`fk_mcf_mcv_supersedes`).

---

## 14. Migration / DDL sequence proposal

### 14.1 Proposed order (single atomic transaction at M2-execution time)

1. `CREATE SCHEMA IF NOT EXISTS mcf;` + `COMMENT ON SCHEMA`.
2. `COMMENT ON TABLE contract.metric_contract ...` (P1).
3. `COMMENT ON TABLE contract.metric_contract_version ...` (P1).
4. `COMMENT ON TABLE metric.metric_binding ...` (P1).
5. `CREATE TABLE mcf.metric_contract (...)` — parent identity-bearing table. **Hash columns nullable per §10.2.**
6. `CREATE TABLE mcf.metric_contract_version (...)` — child with FK to (5).
7. `CREATE TABLE mcf.metric_variable_binding (...)` — child with FK to (6).
8. `CREATE TABLE mcf.metric_filter_clause (...)` — child with FK to (6).
9. `CREATE TABLE mcf.metric_computed_dimension_ref (...)` — child with FK to (6).
10. CHECK constraints on closed enums (per §5.2, §6.2, §7.2, §8.2, §9.2).
11. CHECK constraint on `candidate_source_ref_json` source_type (P2) — see §17.3 if CHECK on JSONB proves problematic.
12. UNIQUE INDEXes per §5.2, §6.2, §7.2 (with `IS NOT NULL` clauses on nullable hash columns).
13. Non-unique indexes per §5.3, §6.3, §8.3.
14. **`COMMENT ON COLUMN` block** for M3-owned placeholders (`governance_state_code`, `supersedes_version_uid`), M7/M8-owned hash placeholders (`formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash`, `identity_tuple_hash`, `package_signature_hash`, `hash_algorithm_version`), and M9-owned reference (`resolver_config_ref_json`) per §11.5.
15. Final transaction commit.

### 14.2 No execution by this DBCP

This DBCP is design-only. M2-execution gate (separate, future) ships the DDL into `bc-core/docker/redesign/04-mcf-substrate.sql`, the Drizzle into `bc-core/src/database/schema/mcf/*.ts`, and runs the migration. M2-execution must:

- Pass per-gate verification (§16 below).
- Get explicit operator approval per CLAUDE.md Database Change Protocol.
- Pass pre-commit hooks (no `--no-verify`).
- Land via PR with rollback story.

### 14.3 No triggers in M2 DDL

Per §11.4, M2 does NOT install lifecycle / immutability triggers. Those are M3 scope. M2 DDL is purely structural.

---

## 15. Rollback / reversibility story

### 15.1 Pre-data rollback (M2 ships but no MCF MCs authored yet)

- `DROP TABLE mcf.metric_computed_dimension_ref;`
- `DROP TABLE mcf.metric_filter_clause;`
- `DROP TABLE mcf.metric_variable_binding;`
- `DROP TABLE mcf.metric_contract_version;`
- `DROP TABLE mcf.metric_contract;`
- `DROP SCHEMA mcf;`
- `COMMENT ON TABLE contract.metric_contract IS NULL;` (or the prior comment if any).
- `COMMENT ON TABLE contract.metric_contract_version IS NULL;`
- `COMMENT ON TABLE metric.metric_binding IS NULL;`

Clean rollback, no data loss.

### 15.2 Post-data rollback (MCF MCs exist)

Once any `mcf.metric_contract` row exists, dropping the schema loses authored MCs. At that point, rollback becomes **archive/supersession discipline** per Foundation Invariant III:

- Set `mcf.metric_contract.archived_at = now()` for the MCs to retire.
- Author replacement MCs under the new architecture.
- The dropped substrate is preserved as audit reference (analogous to the post-D418 stance for legacy `contract.metric_contract`).

The destructive-rollback path is intentionally NOT available post-data. This mirrors the BCF v1 substrate discipline.

### 15.3 What rollback does NOT touch

- Legacy `metric.*` tables — never modified by M2 beyond COMMENT additions; comments are reversible.
- BCF `concept_registry.*` substrate — MCF cannot write here.
- Foundation Governance Substrate (`contract.certification_record`, etc.) — M2 doesn't touch.
- D316 substrate (`mc_dependency`, `readiness_ledger`) — M2 doesn't touch.
- MLS substrate — M2 doesn't touch.

---

## 16. Verification requirements for future M2 execution

### 16.1 Dry-run verification (before applying DDL)

The M2-execution gate must ship a dry-run script that proves, against a copy of `bc_platform_dev`:

- Schema `mcf` does not currently exist (clean slate).
- Five new tables do not currently exist in any schema.
- Three legacy tables (`contract.metric_contract` + `_version` + `_binding`) exist.
- No active code path writes to those three legacy tables (grep `bc-core/src/` for INSERT/UPDATE on these tables — should be 0 hits except in deprecated/quarantined paths).
- No FK exists from any current substrate to the three legacy tables that would be affected by COMMENT changes (COMMENT doesn't affect FKs but a clean check is cheap).

### 16.2 Post-apply verification (after DDL runs)

Apply-time verifier checks via `information_schema`:

- **Schema present.** `SELECT 1 FROM information_schema.schemata WHERE schema_name = 'mcf';` returns 1 row.
- **Five tables present.** `SELECT table_name FROM information_schema.tables WHERE table_schema = 'mcf';` returns exactly the 5 expected table names.
- **Column counts.** Per-table column count matches design (§5.1, §6.1, §7.1, §8.1, §9.1).
- **Identity UNIQUE.** `SELECT indexname FROM pg_indexes WHERE schemaname = 'mcf' AND indexname = 'idx_mcf_mc_identity_active';` returns 1 row.
- **Closed-enum CHECK constraints.** `SELECT conname FROM pg_constraint WHERE conrelid = 'mcf.metric_contract'::regclass AND contype = 'c';` returns expected CHECK names.
- **FK integrity.** Per-FK verifier check confirms target table + column.
- **No FK to legacy `metric.*` from `mcf.*`.** Negative check via `pg_constraint`.
- **COMMENT applied.** `SELECT obj_description('contract.metric_contract'::regclass);` returns non-NULL and contains "HISTORICAL / PRE-MCF".
- **No data mutation.** Row counts on `contract.metric_contract`, `contract.metric_contract_version`, `metric.metric_binding` unchanged from pre-apply baseline.

### 16.3 Verification artifacts to commit

The M2-execution gate ships (analogous to D418 Gate 5.3 pattern):

- A dry-run output JSONL.
- A post-apply verification JSONL.
- A summary markdown.

All three committed to `bc-core/scripts/audit-output/m2-mcf-substrate-{timestamp}.*`.

---

## 17. Risks and open questions

### 17.1 Physical FK vs service validation to BCF Registry

**Position recommended in §12: service-level validation, no physical FK for v1.** Revisit post-M3 if patterns warrant.

**Risk:** missing-row bug at runtime if a `bound_business_concept_id` references a non-existent uuid. Mitigation: service validates at bind time + records check result in `bind_time_check_results_json`.

### 17.2 Lifecycle ownership M2 vs M3

**Locked position per operator clarification: `governance_state_code` column ships in M2 with CHECK enum AND with explicit `COMMENT ON COLUMN` declaring M3 ownership of transitions and activation authority (per §11.5). M3 owns triggers + `metric_contract_revision` + `metric_supersession` tables + immutability enforcement.**

The column COMMENT makes the M2/M3 boundary visible at the substrate level — any reader of `\d+ mcf.metric_contract_version` or `information_schema.columns.column_comment` sees the ownership declaration. M2 does not present a column that looks lifecycle-enforced when it is not.

**Risk:** during the M2-shipped, M3-not-yet interim, active-row immutability is service-only discipline. Mitigation: writer service is the only path to `mcf.*`; no other code writes; column COMMENT documents the gap publicly.

### 17.3 JSONB CHECK constraint shape for `candidate_source_ref_json`

**Position recommended: CHECK on `(candidate_source_ref_json->>'source_type') IN (...)` enforces the closed enum.**

**Risk:** CHECK constraints on JSONB are valid SQL but the operator `->>` extracts text, which is acceptable. If Postgres version or M2 runtime constraints (e.g. read-write performance on inserts) make the CHECK annoying, fallback options:
- Generated column: `source_type_extracted text GENERATED ALWAYS AS ((candidate_source_ref_json->>'source_type')) STORED` + CHECK on the generated column.
- Documentation-only: discipline enforced at the M11 reservoir-ingestion service write path.

**Operator-locked preference:** substrate enforcement via CHECK if practical. Test in M2-execution dry-run.

### 17.4 Whether `identity_tuple_hash` is stored or computed

**Position recommended: stored on `mcf.metric_contract`.**

**Reasons:**
- Service computes once at write time; substrate stores.
- UNIQUE index requires a column.
- Avoids computed-column complexity.

**Risk:** drift between stored hash and actual identity-tuple content if service has a bug. Mitigation: M7+ writer service tests + periodic verification job (later gate).

### 17.5 Package signature hash in M2 or M8?

**Locked position per operator clarification: column in M2 (reserved as nullable), service in M8.**

**Reasons:**
- M2 substrate reserves the column; M8 service computes and populates.
- M2 ships sooner; M8 service ships when its dependencies (M7 AST service, M2 substrate) exist.
- **Nullable in M2**, NOT NULL enforced by M3 lifecycle when `governance_state_code` reaches `'approved'`. This means M2 substrate accepts draft-state rows with NULL `package_signature_hash` (consistent with all hash columns per §10.2). M8 service ships separately; the M2-shipped-but-M8-not-yet interim is acceptable because the writer flow is M7 → M8 → state transition.
- Column COMMENT (per §11.5) declares M8 ownership publicly.

**Alternative considered:** defer `package_signature_hash` column to M8 substrate gate. Rejected because the column is intrinsic to the identity-bearing parent row; splitting is awkward.

**Same nullable discipline applies to component hashes** (`formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash`, `identity_tuple_hash`, `hash_algorithm_version`) — all populated by M7 services as authoring progresses; all nullable in M2; all NOT NULL once `governance_state_code='approved'` per M3.

### 17.6 Naming collision with existing `metric` schema

**Position: no collision.** `mcf` is a new schema; all five tables are in the `mcf` namespace. Legacy `contract.metric_contract*` tables stay in `metric` namespace with COMMENT markers. No table name clash.

**Risk:** human operators may confuse `contract.metric_contract` (legacy) with `mcf.metric_contract` (new). Mitigation: COMMENT markers per §3 point readers to the right table; bc-admin UI consistently uses one or the other per consumer per build plan §5.

### 17.7 Avoiding accidental migration semantics

**Position: zero FK from `mcf.*` to `metric.*`; zero trigger reading from `metric.*`; zero ingestion path that auto-imports legacy rows.**

**Risk:** future engineer adds a "convenience" view that joins MCF MCs to legacy `contract.metric_contract` rows and treats the join result as authoritative. Mitigation: D422 Decision 2 + the `candidate_source_ref_json` provenance pattern give engineers a documented non-FK reference if orientation is needed. Code review discipline catches the rest.

### 17.8 Whether to include `temporal_gate_params_json` as a separate substrate item

**Position: inline as `jsonb` column on `mcf.metric_contract`.**

**Reasons:**
- Closed-enum shape is small (per shape: `length`, `unit`, etc.).
- Splitting into a separate table adds JOIN overhead for every MC read.
- M7+ service canonicalizes params for hashing.

**Risk:** D162 Rule 1 ("No JSONB for queryable data") if temporal-gate-params become a query dimension. Mitigation: temporal-gate-params are not typically a query dimension (queries filter by `temporal_gate_shape_code`, which IS a column, not by params).

### 17.9 Whether `resolver_config_ref_json` on `mcf.metric_computed_dimension_ref` is opaque

**Position: structured JSONB with documented schema; opaque to SQL queries but readable by service.**

**Reasons:**
- Variability per dimension class (fiscal_period needs different config than bucket_label).
- Substrate-schema enforcement of a polymorphic structure is heavy.

**Risk:** schema drift between writer service and reader service. Mitigation: M9 fixture verifier validates resolver_config shape per dimension class.

### 17.10 Index strategy for query patterns

**Position: ship minimal indexes per §5.3 / §6.3 / §8.3; iterate based on M16 console query patterns.**

**Risk:** missing index causes slow MC List / Detail page renders. Mitigation: M16 (operator console) gate adds indexes as needed; M2 ships the structural minimum.

---

## 18. Recommended next gate

### 18.1 If operator approves this M2 DBCP

**Open M2 execution / dry-run gate in bc-core.** Scope:

- Author `bc-core/docker/redesign/04-mcf-substrate.sql` with the DDL block from §14.
- Author `bc-core/src/database/schema/mcf/*.ts` with the Drizzle equivalents.
- Author dry-run verifier script under `bc-core/scripts/`.
- Author post-apply verifier script.
- Get explicit operator approval per CLAUDE.md Database Change Protocol before any `psql` apply.
- Land via PR with rollback story per §15.

The execution gate is NOT this document; this document specifies WHAT the execution gate ships. The execution gate is a separate session brief.

### 18.2 If operator revises this DBCP

Re-issue this design document with revisions before opening the execution gate.

### 18.3 If operator's open questions (§17) need resolution first

Each open question in §17 has a recommended position. Operator may:
- Accept all positions → open execution gate.
- Revise specific positions → re-issue this design.
- Defer specific positions → execution gate proceeds with documented-deferral; deferred items become follow-on DBCPs.

### 18.4 What NOT to open before M2 execution

- **M3 lifecycle substrate DBCP** — needs M2 substrate to exist.
- **M5 panel substrate DBCP** — needs M2 substrate for FKs from panel runs to MCs.
- **M7 formula AST service** — needs M2 substrate for write target.
- **M11 reservoir ingestion service** — needs M5 panel substrate (and indirectly M2).

---

## Document verification

- **All 18 required sections present** (§1 Scope, §2 Grounding, §3 Legacy annotation, §4 New schema, §5 metric_contract, §6 metric_contract_version, §7 metric_variable_binding, §8 metric_filter_clause, §9 metric_computed_dimension_ref, §10 Hash and identity rules, §11 Immutability and state boundary, §12 BCF Registry references, §13 Drizzle/bc-core notes, §14 Migration/DDL sequence, §15 Rollback, §16 Verification, §17 Risks and open questions, §18 Recommended next gate).
- **Design-only.** Illustrative SQL snippets included for clarity. No DDL is run by this document. No `bc-core/*` file is edited.
- **Comments scoped to 3 core legacy tables only.** Per P1 lock: `contract.metric_contract`, `contract.metric_contract_version`, `metric.metric_binding`. NOT `metric_formula` or `metric_contract_approval`.
- **`candidate_source_ref_json` non-authoritative in every mention.** §5.1 column role; §5.2 CHECK constraint; §2.4 P2 lock cite. Outside identity tuple, outside package signature hash, not PE-MC-1-citable.
- **No code/DB/schema files changed.** Only this design doc.

**Status: proposed.** Awaits operator approval before any future M2-execution gate writes DDL or runs migration.
