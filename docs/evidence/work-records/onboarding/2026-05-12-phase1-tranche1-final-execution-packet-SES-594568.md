---
metric: phase1-tranche1-final-execution-packet
metric_version: n/a
tenant: platform
source_system: n/a
work_type: dbcp-execution-packet
session_uid: SES-594568
date: 2026-05-12
status: decision-pending
related_commits:
  - bc-core@a751dc5
  - bc-core@05c888d
  - bc-core@fc936b0
related_tasks: []
related_adrs:
  - DEC-a17d0f
  - DEC-b7affa
  - DEC-889238
  - DEC-af8247
  - DEC-804874
related_mwrs:
  - 2026-05-12-phase1-tranche1-dbcp-bundle-SES-594568.md
  - 2026-05-12-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md
  - 2026-05-12-c1-matrix-review-against-apex-SES-594568.md
related_change_records:
  - CHG-28ab0c
repair_location: E
affected_boundary: storage_projection
foundation_gate: passed
---

# Phase 1 Tranche 1 — final execution packet

> **NO EXECUTION YET.** This packet consolidates every Tranche 1 DBCP into one self-contained, copy-pasteable document for the operator's final review. Execution requires a separate explicit "execute now" approval per the Database Change Protocol (CLAUDE.md). When approved, the SQL in §3 (one DBCP at a time, in the recommended order) is what runs.
>
> **All five DBCPs are additive new tables.** Total existing-row mutations: zero. The only INSERTs run are the seed inserts for the two `master.*` enum tables.

## 0. What this packet contains

| Section | Content |
|---|---|
| §1 | DBCP roster + recommended execution order |
| §2 | Combined preflight read-only checks (run before any execution) |
| §3 | Per-DBCP exact forward SQL (DDL + seed inserts) |
| §4 | Combined postflight verification checks (run after each DBCP executes, or all together at the end) |
| §5 | Per-DBCP rollback SQL |
| §6 | Additivity statement |
| §7 | Modules unblocked after execution |
| §8 | Operator approval section |

The packet draws verbatim from:
- `2026-05-12-phase1-tranche1-dbcp-bundle-SES-594568.md` (bundled review packet, currently approved-for-execution-pending)
- `2026-05-12-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md` (prior draft for 1c and 1f full DDL)
- bc-core@a751dc5 + bc-core@05c888d + bc-core@fc936b0 (the SDA / MCE module code that consumes these tables)

No DDL has been edited from the bundle review; only consolidated.

## 1. DBCPs to execute + recommended order

| Order | DBCP | Target table | Role |
|---|---|---|---|
| 1 | **DBCP-1a** | `master.semantic_family` | Closed enum of `semantic_family` codes from DEC-804874 (D366) with per-family type/unit compatibility metadata. Consumed by SDA-1 gates G5 + G6. |
| 2 | **DBCP-1j** | `master.industry` | Closed industry enum from DEC-af8247 §2 (sentinel `cross_industry` + the specific industries listed in the ADR body). Consumed by C3 cross-domain scope gate (Phase 2). |
| 3 | **DBCP-1c** | `contract.certification_record` | SDA primitive certification audit ledger. Consumed by SDA-2 history writes. |
| 4 | **DBCP-1f** | `contract.primitive_provenance` | Append-only provenance ledger across BF / BO / CF. Consumed by SDA-3 history writes. |
| 5 | **DBCP-2a** | `contract.mc_envelope_audit_record` | MC Envelope Governance audit ledger (dedup + supersede + override). Consumed by MCE-7 writes. |

**Inter-DBCP dependencies:** none. All five are independent additive new tables. Order is for human readability and predictable error-isolation if any one fails — the operator can stop after any single DBCP and the others remain unexecuted.

**Execution mode:** each DBCP runs in its own transaction (BEGIN ... COMMIT). Recommended: one session per DBCP with the operator checking postflight before moving to the next, OR all five back-to-back with combined postflight at the end. Both modes are safe.

## 2. Combined preflight read-only checks

Run these BEFORE executing any DBCP. All checks must pass before approval is given.

```sql
-- 2.1 Confirm schemas exist
SELECT schema_name FROM information_schema.schemata
  WHERE schema_name IN ('master', 'contract')
  ORDER BY schema_name;
-- expect: 2 rows ('contract', 'master')

-- 2.2 Confirm none of the target tables already exists
SELECT
  to_regclass('master.semantic_family')         AS sf,
  to_regclass('master.industry')                AS ind,
  to_regclass('contract.certification_record')  AS cr,
  to_regclass('contract.primitive_provenance')  AS pp,
  to_regclass('contract.mc_envelope_audit_record') AS mear;
-- expect: all 5 columns NULL

-- 2.3 Confirm gen_random_uuid is available (required by 3 of the 5 DBCPs)
SELECT gen_random_uuid() IS NOT NULL AS uuid_ok;
-- expect: t (true)

-- 2.4 Confirm contract.metric_contract exists (poly-ref target for DBCP-2a; service-layer FK only)
-- Corrected from `metric.metric_contract` (the wrong schema prefix in the initial packet):
-- the metric_contract table lives in the `contract` schema alongside the other contract-family
-- tables (source_contract, admission_contract, observation_contract, canonical_contract,
-- metric_contract, intervention_contract). The `metric` schema holds runtime/binding/state
-- tables (metric_definition, metric_binding, metric_formula, etc.) — not metric_contract.
SELECT to_regclass('contract.metric_contract');
-- expect: non-NULL

-- 2.5 Confirm canonical_field / business_field / business_object exist
SELECT
  to_regclass('contract.canonical_field')   AS cf,
  to_regclass('contract.business_field')    AS bf,
  to_regclass('contract.business_object')   AS bo;
-- expect: all 3 columns non-NULL

-- 2.6 Snapshot existing row counts on the 3 primitive tables (sanity — nothing in this packet should change these)
SELECT 'canonical_field' AS t, COUNT(*) AS rows FROM contract.canonical_field
UNION ALL SELECT 'business_field',  COUNT(*) FROM contract.business_field
UNION ALL SELECT 'business_object', COUNT(*) FROM contract.business_object;
-- record the numbers; re-run after execution and verify unchanged
```

If any 2.1-2.5 check returns an unexpected result, **stop and report**. Do not proceed to execution.

## 3. Per-DBCP forward SQL

Each block is self-contained. Run inside a single transaction per DBCP:

```
BEGIN;
  -- <DBCP body>
COMMIT;
```

If COMMIT succeeds, immediately run that DBCP's postflight checks (§4) before moving on.

### 3.1 DBCP-1a — `master.semantic_family`

```sql
CREATE TABLE master.semantic_family (
  semantic_family_code     TEXT PRIMARY KEY,
  display_name             TEXT NOT NULL,
  description_text         TEXT NOT NULL,
  category_code            TEXT NOT NULL,
  compatible_data_types    TEXT[] NOT NULL,
  compatible_unit_types    TEXT[],
  source_adr_ref           TEXT NOT NULL DEFAULT 'DEC-804874',
  created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT semantic_family_category_chk
    CHECK (category_code IN ('identity','measure','temporal','dimension')),
  CONSTRAINT semantic_family_code_format_chk
    CHECK (semantic_family_code ~ '^[a-z][a-z0-9]*(-[a-z0-9]+)*$')
);

CREATE INDEX idx_semantic_family_category ON master.semantic_family (category_code);

COMMENT ON TABLE master.semantic_family IS
  'Closed enum of semantic_family codes per DEC-804874 (D366). Hyphenated kebab-style identifiers per SDA Profile P5 — documented divergence from DEC-69f09e snake_case scoped to this enum only (DEC-a17d0f §3 P5). Authoritative member set lives in seed rows below + bc-core profiles.ts SEMANTIC_FAMILY_ENUM.';

INSERT INTO master.semantic_family
  (semantic_family_code, display_name, description_text, category_code, compatible_data_types, compatible_unit_types)
VALUES
  -- Identity families
  ('identifier',         'Identifier',         'Unique key or surrogate identifying an entity',                    'identity',  ARRAY['string'],          NULL),
  ('code',               'Code',               'Short coded value drawn from a controlled vocabulary',             'identity',  ARRAY['string'],          NULL),
  ('name',               'Name',               'Human-readable entity name',                                       'identity',  ARRAY['string'],          NULL),
  ('text',               'Text',               'Free-form textual content',                                        'identity',  ARRAY['string'],          NULL),
  -- Measure families
  ('measure-currency',   'Measure (currency)', 'Monetary measure with currency unit',                              'measure',   ARRAY['number'],          ARRAY['currency']),
  ('measure-count',      'Measure (count)',    'Discrete count of occurrences or items',                           'measure',   ARRAY['number'],          ARRAY['count']),
  ('measure-ratio',      'Measure (ratio)',    'Dimensionless ratio between two measures',                         'measure',   ARRAY['number'],          ARRAY['ratio']),
  ('measure-percent',    'Measure (percent)',  'Percentage value (typically 0-100 or 0-1 per declaration)',        'measure',   ARRAY['number'],          ARRAY['percentage']),
  ('measure-score',      'Measure (score)',    'Bounded numeric score (NPS 0-10, FICO 300-850 etc.)',              'measure',   ARRAY['number'],          ARRAY['score']),
  -- Temporal families
  ('date',               'Date',               'Calendar date (no time-of-day)',                                   'temporal',  ARRAY['date'],            NULL),
  ('period',             'Period',             'Named period (fiscal, calendar, custom)',                          'temporal',  ARRAY['string','number'], NULL),
  ('datetime',           'Datetime',           'Instant in time with date and time-of-day',                        'temporal',  ARRAY['timestamp'],       NULL),
  ('duration',           'Duration',           'Elapsed time between two instants',                                'temporal',  ARRAY['number'],          ARRAY['days','hours','minutes','seconds']),
  -- Dimension families
  ('dim-calendar-date',  'Dimension (calendar date)',  'Calendar-date dimension reference',                        'dimension', ARRAY['date','string','number'], NULL),
  ('dim-fiscal-period',  'Dimension (fiscal period)',  'Fiscal-period dimension reference',                        'dimension', ARRAY['string','number'], NULL),
  ('dim-currency',       'Dimension (currency)',       'Currency dimension reference (ISO 4217)',                  'dimension', ARRAY['string'],          NULL),
  ('dim-country',        'Dimension (country)',        'Country dimension reference (ISO 3166)',                   'dimension', ARRAY['string'],          NULL),
  ('dim-legal-entity',   'Dimension (legal entity)',   'Legal entity dimension reference',                         'dimension', ARRAY['string'],          NULL),
  ('dim-gl-account',     'Dimension (GL account)',     'General-ledger account dimension reference',               'dimension', ARRAY['string'],          NULL),
  ('dim-cost-center',    'Dimension (cost center)',    'Cost-center dimension reference',                          'dimension', ARRAY['string'],          NULL),
  ('dim-customer',       'Dimension (customer)',       'Customer dimension reference',                             'dimension', ARRAY['string'],          NULL),
  ('dim-vendor',         'Dimension (vendor)',         'Vendor dimension reference',                               'dimension', ARRAY['string'],          NULL),
  ('dim-product',        'Dimension (product)',        'Product dimension reference',                              'dimension', ARRAY['string'],          NULL);
```

### 3.2 DBCP-1j — `master.industry`

```sql
CREATE TABLE master.industry (
  industry_code              TEXT PRIMARY KEY,
  display_name               TEXT NOT NULL,
  description_text           TEXT NOT NULL,
  is_cross_industry_sentinel BOOLEAN NOT NULL DEFAULT FALSE,
  source_adr_ref             TEXT NOT NULL DEFAULT 'DEC-af8247',
  created_at                 TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT industry_code_format_chk
    CHECK (industry_code ~ '^[a-z][a-z0-9_]*$'),
  CONSTRAINT industry_cross_sentinel_unique_chk
    CHECK (
      (is_cross_industry_sentinel = TRUE AND industry_code = 'cross_industry')
      OR is_cross_industry_sentinel = FALSE
    )
);

CREATE INDEX idx_industry_cross_sentinel
  ON master.industry (is_cross_industry_sentinel)
  WHERE is_cross_industry_sentinel = TRUE;

COMMENT ON TABLE master.industry IS
  'Closed enum of industry codes per DEC-af8247 (D406) §2. The `cross_industry` row is the catch-all sentinel; the remaining rows are specific industries per the §2 body listing. The is_cross_industry_sentinel flag is queryable; only the cross_industry row may have it set. Authoritative member set lives in seed rows; extension via amendment ADR.';

INSERT INTO master.industry
  (industry_code, display_name, description_text, is_cross_industry_sentinel)
VALUES
  -- Cross-industry sentinel
  ('cross_industry',         'Cross-industry',           'Applicable to any tenant regardless of industry. Default for un-backfilled MCs per DEC-af8247 §2.', TRUE),
  -- Specific industries (per DEC-af8247 §2 body listing)
  ('hospitality',            'Hospitality',              'Hotels, restaurants, lodging, and related hospitality businesses.',                                   FALSE),
  ('manufacturing',          'Manufacturing',            'Industrial production of goods including discrete and process manufacturing.',                         FALSE),
  ('retail',                 'Retail',                   'Consumer-facing retail operations including brick-and-mortar and e-commerce.',                         FALSE),
  ('banking',                'Banking',                  'Commercial banking, retail banking, investment banking, and credit unions.',                          FALSE),
  ('insurance',              'Insurance',                'Life, health, property, casualty, and reinsurance operations.',                                       FALSE),
  ('healthcare',             'Healthcare',               'Hospitals, clinics, providers, payers, and related healthcare services.',                              FALSE),
  ('energy',                 'Energy',                   'Oil, gas, electricity generation, renewable energy, and utilities.',                                  FALSE),
  ('telecommunications',     'Telecommunications',       'Telecom service providers, ISPs, and network infrastructure operators.',                              FALSE),
  ('software_saas',          'Software / SaaS',          'Software vendors, SaaS platforms, and technology service providers (Apex platform itself).',         FALSE),
  ('professional_services',  'Professional services',    'Consulting, legal, accounting, engineering, and other professional service firms.',                  FALSE),
  ('real_estate',            'Real estate',              'Property development, leasing, REITs, and real estate operations.',                                   FALSE),
  ('transportation',         'Transportation',           'Logistics, shipping, freight, passenger transport, and supply chain operators.',                      FALSE),
  ('pharmaceuticals',        'Pharmaceuticals',          'Drug discovery, development, manufacturing, and distribution.',                                       FALSE),
  ('media_entertainment',    'Media & entertainment',    'Publishing, broadcasting, streaming, gaming, and entertainment operations.',                          FALSE),
  ('agriculture',            'Agriculture',              'Farming, crop production, livestock, and agricultural supply chain.',                                 FALSE);
```

### 3.3 DBCP-1c — `contract.certification_record`

```sql
CREATE TABLE contract.certification_record (
  certification_record_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  primitive_type            TEXT NOT NULL,
  primitive_id              UUID NOT NULL,
  action_code               TEXT NOT NULL,
  from_state_code           TEXT,
  to_state_code             TEXT,
  is_archived_after         BOOLEAN,

  -- Gate results (deterministic gates G1-G10)
  gate_results_json         JSONB NOT NULL DEFAULT '{}'::jsonb,

  -- AI advisory verdicts (D366 / SDA §5)
  advisory_verdicts_json    JSONB NOT NULL DEFAULT '[]'::jsonb,

  -- Override (only when an overridable gate failed AND was overridden)
  override_gate_code        TEXT,
  override_rationale_text   TEXT,
  override_followup_task_uid TEXT,

  -- Certifier identity (Q6 — Cognito sub + role-at-action-time)
  certifier_sub             TEXT NOT NULL,
  certifier_role_at_action  TEXT NOT NULL,
  certifier_email           TEXT,

  -- Supersession link (when action = 'supersede')
  supersedes_primitive_id   UUID,

  -- Timestamps
  created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT certification_record_primitive_type_chk
    CHECK (primitive_type IN ('canonical_field','business_field','business_object')),
  CONSTRAINT certification_record_action_code_chk
    CHECK (action_code IN ('submit_for_review','certify','return_to_author','deprecate','withdraw','supersede','archive','unarchive')),
  CONSTRAINT certification_record_override_chk
    CHECK (
      (override_gate_code IS NULL AND override_rationale_text IS NULL AND override_followup_task_uid IS NULL) OR
      (override_gate_code IS NOT NULL AND char_length(override_rationale_text) >= 40 AND override_followup_task_uid IS NOT NULL)
    )
);

CREATE INDEX idx_certification_record_primitive ON contract.certification_record (primitive_type, primitive_id, created_at DESC);
CREATE INDEX idx_certification_record_certifier ON contract.certification_record (certifier_sub, created_at DESC);
CREATE INDEX idx_certification_record_action    ON contract.certification_record (action_code, created_at DESC);

COMMENT ON TABLE contract.certification_record IS
  'Per-primitive audit ledger for SDA certification acts (DEC-a17d0f §6, §9 Phase 1 DBCP-1c). Append-only by service constraint; no UPDATE path. INSERT-only.';
```

### 3.4 DBCP-1f — `contract.primitive_provenance`

```sql
CREATE TABLE contract.primitive_provenance (
  primitive_provenance_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  primitive_type            TEXT NOT NULL,
  primitive_id              UUID NOT NULL,
  source_standard           TEXT NOT NULL,
  standard_ref              TEXT,
  rationale_text            TEXT,
  registered_by_sub         TEXT NOT NULL,
  registered_by_role        TEXT NOT NULL,
  registered_at             TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT primitive_provenance_type_chk
    CHECK (primitive_type IN ('canonical_field','business_field','business_object')),
  CONSTRAINT primitive_provenance_standard_chk
    CHECK (source_standard IN ('oagis','iso_20022','xbrl_gaap','ifrs','uncefact','bc_standard','computed')),
  CONSTRAINT primitive_provenance_ref_chk
    CHECK (
      (source_standard IN ('bc_standard','computed') AND standard_ref IS NULL) OR
      (source_standard NOT IN ('bc_standard','computed') AND standard_ref IS NOT NULL AND char_length(standard_ref) > 0)
    )
);

CREATE INDEX idx_primitive_provenance_primitive ON contract.primitive_provenance (primitive_type, primitive_id, registered_at DESC);
CREATE INDEX idx_primitive_provenance_standard  ON contract.primitive_provenance (source_standard);

COMMENT ON TABLE contract.primitive_provenance IS
  'Append-only provenance ledger for BF/BO/CF (DEC-a17d0f §7 Q4). The latest row per (primitive_type, primitive_id) is the current provenance; the existing per-primitive source_standard/standard_ref columns are retained as a backward-compat projection of the latest row.';
```

### 3.5 DBCP-2a — `contract.mc_envelope_audit_record`

```sql
CREATE TABLE contract.mc_envelope_audit_record (
  mc_envelope_audit_record_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- MC envelope reference (poly-ref; no FK at DB layer)
  metric_contract_id           UUID NOT NULL,
  metric_contract_version_code TEXT,

  -- Action taken
  action_code                  TEXT NOT NULL,
  fingerprint_signature        TEXT,

  -- Dedup / supersession linkage
  related_mc_id                UUID,
  supersedes_mc_id             UUID,
  survivor_mc_id               UUID,

  -- Override (when action ends in '_override')
  override_rationale_text      TEXT,
  override_followup_task_uid   TEXT,

  -- Operator identity
  operator_sub                 TEXT NOT NULL,
  operator_role_at_action      TEXT NOT NULL,
  operator_email               TEXT,

  -- Timestamp
  created_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT mc_envelope_audit_action_chk
    CHECK (action_code IN ('dedup_check','dedup_block','dedup_override','supersede','survivor_override')),
  CONSTRAINT mc_envelope_audit_override_chk
    CHECK (
      (action_code NOT IN ('dedup_override','survivor_override') AND override_rationale_text IS NULL AND override_followup_task_uid IS NULL)
      OR
      (action_code IN ('dedup_override','survivor_override') AND char_length(override_rationale_text) >= 40 AND override_followup_task_uid IS NOT NULL)
    ),
  CONSTRAINT mc_envelope_audit_supersede_chk
    CHECK (
      (action_code != 'supersede' AND supersedes_mc_id IS NULL AND survivor_mc_id IS NULL)
      OR
      (action_code = 'supersede' AND supersedes_mc_id IS NOT NULL AND survivor_mc_id IS NOT NULL)
    )
);

CREATE INDEX idx_mc_envelope_audit_mc       ON contract.mc_envelope_audit_record (metric_contract_id, created_at DESC);
CREATE INDEX idx_mc_envelope_audit_op       ON contract.mc_envelope_audit_record (operator_sub, created_at DESC);
CREATE INDEX idx_mc_envelope_audit_action   ON contract.mc_envelope_audit_record (action_code, created_at DESC);
CREATE INDEX idx_mc_envelope_audit_finger   ON contract.mc_envelope_audit_record (fingerprint_signature) WHERE fingerprint_signature IS NOT NULL;

COMMENT ON TABLE contract.mc_envelope_audit_record IS
  'Per-MC-envelope audit ledger for MC Envelope Governance (DEC-889238 §7). Append-only by service convention; no UPDATE/DELETE path. INSERT-only. Sibling of contract.certification_record (DBCP-1c) which serves SDA primitive certification.';
```

## 4. Combined postflight verification checks

Run these AFTER each DBCP (or all together at the end). Every check must pass.

```sql
-- 4.1 All five tables now exist
SELECT
  to_regclass('master.semantic_family')         AS sf,
  to_regclass('master.industry')                AS ind,
  to_regclass('contract.certification_record')  AS cr,
  to_regclass('contract.primitive_provenance')  AS pp,
  to_regclass('contract.mc_envelope_audit_record') AS mear;
-- expect: all 5 non-NULL

-- 4.2 master.semantic_family seed populated; category breakdown matches expected partition
SELECT category_code, COUNT(*) AS rows
  FROM master.semantic_family
  GROUP BY category_code
  ORDER BY category_code;
-- expect: identity=4, measure=5, temporal=4, dimension=10

SELECT semantic_family_code FROM master.semantic_family ORDER BY semantic_family_code;
-- expect rows match seed-list verbatim (23 rows total)

-- 4.3 master.industry seed populated; sentinel correctly flagged
SELECT COUNT(*) AS cross_sentinel_count
  FROM master.industry
  WHERE is_cross_industry_sentinel = TRUE;
-- expect: 1

SELECT industry_code FROM master.industry ORDER BY industry_code;
-- expect rows match seed-list verbatim (16 rows total, including cross_industry)

-- 4.4 Each new table has the expected constraint set (PK + CHECKs)
SELECT conrelid::regclass::text AS table_name, conname, contype, pg_get_constraintdef(oid)
  FROM pg_constraint
  WHERE conrelid IN (
    'master.semantic_family'::regclass,
    'master.industry'::regclass,
    'contract.certification_record'::regclass,
    'contract.primitive_provenance'::regclass,
    'contract.mc_envelope_audit_record'::regclass
  )
  ORDER BY table_name, contype, conname;
-- expect:
--   master.semantic_family            : 1 PRIMARY KEY + 2 CHECK
--   master.industry                   : 1 PRIMARY KEY + 2 CHECK
--   contract.certification_record     : 1 PRIMARY KEY + 3 CHECK
--   contract.primitive_provenance     : 1 PRIMARY KEY + 3 CHECK
--   contract.mc_envelope_audit_record : 1 PRIMARY KEY + 3 CHECK
-- Total: 5 PKs + 13 CHECKs = 18 explicit constraints

-- 4.5 Indexes created
SELECT schemaname, tablename, indexname
  FROM pg_indexes
  WHERE (schemaname = 'master' AND tablename IN ('semantic_family','industry'))
     OR (schemaname = 'contract' AND tablename IN ('certification_record','primitive_provenance','mc_envelope_audit_record'))
  ORDER BY schemaname, tablename, indexname;
-- expect 11 explicit indexes + 5 implicit PKs = 16 rows total:
--   master.semantic_family:           implicit PK + idx_semantic_family_category
--   master.industry:                  implicit PK + idx_industry_cross_sentinel
--   contract.certification_record:    implicit PK + 3 explicit (primitive, certifier, action)
--   contract.primitive_provenance:    implicit PK + 2 explicit (primitive, standard)
--   contract.mc_envelope_audit_record: implicit PK + 4 explicit (mc, op, action, finger)

-- 4.6 New tables are empty (history/projection tables; no seed rows)
SELECT 'certification_record' AS t, COUNT(*) AS rows FROM contract.certification_record
UNION ALL SELECT 'primitive_provenance',  COUNT(*) FROM contract.primitive_provenance
UNION ALL SELECT 'mc_envelope_audit_record', COUNT(*) FROM contract.mc_envelope_audit_record;
-- expect: 0 / 0 / 0

-- 4.7 Existing primitive tables UNCHANGED (re-run 2.6 sanity)
SELECT 'canonical_field' AS t, COUNT(*) AS rows FROM contract.canonical_field
UNION ALL SELECT 'business_field',  COUNT(*) FROM contract.business_field
UNION ALL SELECT 'business_object', COUNT(*) FROM contract.business_object;
-- expect: identical to the 2.6 snapshot recorded pre-execution

-- 4.8 master.semantic_family content matches bc-core profiles.ts (invariant assertion at the DB level)
-- (To be run from bc-core test harness post-execution; SDA-1 gates module
--  already encodes the same enum via SEMANTIC_FAMILY_ENUM and the
--  DEFAULT_FAMILY_COMPATIBILITY matrix. The bc-core invariant test
--  `gates.spec.ts > "default matrix is coextensive with the D366 semantic_family enum"`
--  will be augmented to also assert against the DB once a Drizzle read path lands.)
```

If any postflight check returns an unexpected result, **stop and rollback** the offending DBCP before proceeding.

## 5. Per-DBCP rollback SQL

Each block undoes exactly one DBCP. Safe to run in any order. All `DROP TABLE` calls use `IF EXISTS` so re-running rollback is idempotent.

### 5.1 Rollback DBCP-1a

```sql
DROP INDEX IF EXISTS master.idx_semantic_family_category;
DROP TABLE IF EXISTS master.semantic_family;
```

### 5.2 Rollback DBCP-1j

```sql
DROP INDEX IF EXISTS master.idx_industry_cross_sentinel;
DROP TABLE IF EXISTS master.industry;
```

### 5.3 Rollback DBCP-1c

```sql
DROP INDEX IF EXISTS contract.idx_certification_record_action;
DROP INDEX IF EXISTS contract.idx_certification_record_certifier;
DROP INDEX IF EXISTS contract.idx_certification_record_primitive;
DROP TABLE IF EXISTS contract.certification_record;
```

### 5.4 Rollback DBCP-1f

```sql
DROP INDEX IF EXISTS contract.idx_primitive_provenance_standard;
DROP INDEX IF EXISTS contract.idx_primitive_provenance_primitive;
DROP TABLE IF EXISTS contract.primitive_provenance;
```

### 5.5 Rollback DBCP-2a

```sql
DROP INDEX IF EXISTS contract.idx_mc_envelope_audit_finger;
DROP INDEX IF EXISTS contract.idx_mc_envelope_audit_action;
DROP INDEX IF EXISTS contract.idx_mc_envelope_audit_op;
DROP INDEX IF EXISTS contract.idx_mc_envelope_audit_mc;
DROP TABLE IF EXISTS contract.mc_envelope_audit_record;
```

## 6. Additivity statement

All five DBCPs in this packet are **purely additive**:

- **Zero ALTERs to existing tables.** No column added, no constraint added, no column type changed, no row updated, no row deleted on `canonical_field`, `business_field`, `business_object`, `metric_contract`, `tenant`, `metric_definition`, or any other pre-existing table.
- **Zero existing-row mutations.** The only INSERTs run are the seed rows for `master.semantic_family` (closed enum listed in §3.1) and `master.industry` (closed enum listed in §3.2). Both are new tables; INSERTs touch only those new tables.
- **Zero schema changes to the Drizzle layer.** Tranche 1 does not require any matching Drizzle schema file update; that work happens when the Drizzle-backed repositories are authored (separate ticket; SDA-2 and SDA-3 Drizzle implementations).
- **Zero impact on running services.** No bc-core service reads or writes any of these tables today. The bc-core SDA + MCE modules currently use in-memory repository implementations (74 + 29 + 27 + 29 + 31 = 232 tests pass without any of these tables existing).

The execution is reversible at every step via the rollback SQL in §5.

## 7. Modules unblocked after execution

These shipped bc-core modules can begin binding to the live tables once the matching DBCP executes:

| Module | Files (already shipped) | Tests | Unblocked by | What lands next |
|---|---|---|---|---|
| **SDA-2 Drizzle repository** | `semantic-definitions/certification-record.{ts,repository.ts,service.ts,spec.ts}` (29 tests) — abstract `CertificationRecordRepository` port + in-memory impl | 29 | **DBCP-1c** | A Drizzle-backed `DrizzleCertificationRecordRepository` extending the same port. Module wiring registers it (production) or the in-memory impl (tests). |
| **SDA-3 Drizzle repository** | `semantic-definitions/provenance-record.{ts,repository.ts,service.ts,spec.ts}` (31 tests) — abstract `ProvenanceRecordRepository` + `PrimitiveProvenanceProjectionRepository` ports + in-memory impls | 31 | **DBCP-1f** | Drizzle-backed history + projection repositories. Production wiring wraps both writes in one transaction per the atomicity contract documented in `provenance-record.service.ts`. |
| **MCE-7 audit ledger repository** | (not yet shipped — to be authored as `mc-envelope-governance/audit-record.{ts,repository.ts,service.ts,spec.ts}` mirroring SDA-2 pattern) | — | **DBCP-2a** | Author the mock-backed module first (same pattern as SDA-2 / SDA-3); Drizzle impl follows DBCP-2a execution. |
| **G5 live enum lookup** | `semantic-definitions/gates.ts` evaluates G5 against `SEMANTIC_FAMILY_ENUM` constant from `profiles.ts` today | 74 | **DBCP-1a** | The G5 evaluator can switch from the in-code enum constant to a DB-backed lookup once `master.semantic_family` exists. Invariant test `gates.spec.ts > "default matrix is coextensive..."` will be extended to assert against the DB. |
| **C3 industry lookup** | (not yet shipped — Phase 2 work per DEC-af8247 §8) | — | **DBCP-1j** | The cross-domain intersection check at tenant-binding time needs `master.industry` to validate the closed enum. Phase 2 ticket; not authored yet. |

**No module unblocks immediately upon execution** — each one requires either (a) authoring a Drizzle-backed implementation conforming to the existing abstract port (SDA-2, SDA-3), (b) authoring the as-yet-unshipped mock-backed module first then the Drizzle impl (MCE-7), or (c) future Phase 2 service code that depends on these tables existing (G5 live lookup, C3 industry lookup).

**What the execution does NOT do:**
- Does not flip any primitive's status_code (no DBCP-1d in this Tranche)
- Does not certify any primitive
- Does not bind or unbind any MC for any tenant
- Does not run any service code
- Does not change any Drizzle schema file
- Does not modify any existing application configuration
- Does not require a service restart (these tables are not yet wired into any module)

## 8. Operator approval

Mark each row before execution begins. Approval can be granted as a single block or per-DBCP.

| DBCP | Reviewed | Approved for execution |
|---|---|---|
| **1a** master.semantic_family | [ ] | [ ] yes / no |
| **1j** master.industry | [ ] | [ ] yes / no |
| **1c** contract.certification_record | [ ] | [ ] yes / no |
| **1f** contract.primitive_provenance | [ ] | [ ] yes / no |
| **2a** contract.mc_envelope_audit_record | [ ] | [ ] yes / no |
| **Preflight checks (§2) all green** | [ ] | n/a |
| **Postflight checks (§4) all green** | [ ] (to verify after execution) | n/a |
| **Rollback SQL (§5) understood** | [ ] | n/a |
| **Execution mode** | [ ] one session per DBCP / [ ] all five back-to-back | — |
| **Final go for execution** | — | [ ] yes / no |

## 9. After execution — recommended next steps

Once Tranche 1 is live and postflight is green:

1. **No metric repair writes** — Tranche 1 unblocks substrate, not Apex content. Apex demo certifications remain hold-pending per prior direction.
2. **Author MCE-7 mock-backed module** (`mc-envelope-governance/audit-record.*`) to mirror the SDA-2 pattern against the freshly-live `contract.mc_envelope_audit_record` table. Pure-function + in-memory + spec; Drizzle impl follows naturally.
3. **Author Drizzle-backed repositories** for SDA-2 (`certification-record.drizzle.repository.ts`) and SDA-3 (`provenance-record.drizzle.repository.ts` + `primitive-provenance-projection.drizzle.repository.ts`). Each conforms to its existing abstract port; service code unchanged.
4. **NestJS module wiring** for the SDA + MCE modules. One module per authority; provider registration selects in-memory (test) or Drizzle (production) implementation. No endpoints exposed yet — that's SDA-4 territory.
5. **Tranche 2 review** — DBCP-1b (status_code CHECK + `is_archived` column on the three primitive tables). Separate execution packet when ready.

## 10. References

- **Source ADRs:** DEC-a17d0f (D403, SDA umbrella), DEC-b7affa (D404, G11 amendment + G5-on-BF), DEC-889238 (D405, MC Envelope Governance), DEC-af8247 (D406, cross-domain scope), DEC-804874 (D366, semantic_family enum).
- **Bundled review packet (parent):** [`2026-05-12-phase1-tranche1-dbcp-bundle-SES-594568.md`](../../dbcp/onboarding/2026-05-12-phase1-tranche1-dbcp-bundle-SES-594568.md). This execution packet is the consolidated form of that bundle.
- **Original DBCP drafts:** [`2026-05-12-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md`](../../dbcp/onboarding/2026-05-12-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md). Source for 1c and 1f DDL.
- **Matrix review (M4-M6 applied to 1a):** [`2026-05-12-c1-matrix-review-against-apex-SES-594568.md`](metric-work-records/_cross/2026-05-12-c1-matrix-review-against-apex-SES-594568.md).
- **Shipped bc-core code consuming these tables (mock-backed; awaiting execution to bind Drizzle):**
  - bc-core@fc936b0 — SDA-1 gates module + tests (74 tests)
  - bc-core@a751dc5 — SDA-2 cert-record + MCE-1 normalizeFormula + tests (29 + 27 tests)
  - bc-core@05c888d — SDA-3 provenance + MCE-2 fingerprint + tests (31 + 29 tests)

## 11. No-execution statement

**This packet is for review only. No DDL has been executed as a result of producing this MWR.** When approved, the operator authorises a separate execution session in which:

1. The preflight checks in §2 are run and verified.
2. Each DBCP's forward SQL from §3 runs inside its own transaction.
3. The postflight checks in §4 are run after each DBCP (or after all five together).
4. If any check fails, the rollback SQL in §5 for the offending DBCP is executed and the operator is notified before continuing.

Until that separate approval, **no DBCP runs.**

---

# Execution result — 2026-05-12 PM

**Status: green.** All five Tranche 1 DBCPs executed successfully against `bc_platform_dev` (PostgreSQL 17.8, `bc-postgres-redesign` container). Each DBCP ran inside its own transaction with per-DBCP postflight verification. Combined §4 postflight cross-check ran at the end and passed.

## Execution environment

| Item | Value |
|---|---|
| Database | `bc_platform_dev` |
| Engine | PostgreSQL 17.8 (Alpine 15.2.0 build) |
| Container | `bc-postgres-redesign` |
| Host port | 5435 |
| Executor | psql via `docker exec -i -e PGPASSWORD=… psql` (stdin SQL, `--set ON_ERROR_STOP=on`) |
| Session | SES-594568 |
| Date | 2026-05-12 PM |
| Source packet commit | bc-docs-v3@9bba81f (then patched as part of this execution; see *Pre-execution packet patch* below) |

## Pre-execution packet patch

The initial §2.4 preflight check in the committed packet (bc-docs-v3@9bba81f) referenced `metric.metric_contract`, which is not a table that exists in the live database. The check returned NULL on the first preflight run and execution halted per the operator's "stop on any preflight failure" rule.

Investigation confirmed:

- The actual table lives at **`contract.metric_contract`** (alongside the other family-pattern contract tables: `source_contract`, `admission_contract`, `observation_contract`, `canonical_contract`, `metric_contract`, `intervention_contract`).
- The `metric` schema holds runtime / binding / state tables (`metric_definition`, `metric_binding`, `metric_formula`, `mls_state*`, `readiness_ledger`, etc.) — but not `metric_contract`.
- DBCP-2a's `metric_contract_id UUID NOT NULL` is a poly-ref with no DB-level FK; service-layer enforcement only. The structural prerequisite is "a table exists for the poly-ref to point at", which IS satisfied at `contract.metric_contract`.

**Action taken:** the operator authorised patching §2.4 of the committed packet to reference `contract.metric_contract`, then re-running preflight. The corrected check passed and execution proceeded.

The patch is a one-line schema-prefix correction in the §2.4 SQL block; no semantic change to the DBCPs themselves, no change to the structural intent. The corrected text is present in this file (§2.4 above) and is committed alongside this execution-result section.

## Per-DBCP results

### DBCP-1a — `master.semantic_family`

```
BEGIN
CREATE TABLE             25.251 ms
CREATE INDEX              1.350 ms
COMMENT                   1.694 ms
INSERT 0 23               1.325 ms
COMMIT                    3.211 ms
```

Postflight:
- `to_regclass('master.semantic_family')` = `master.semantic_family` ✓
- Seed rows: 23 total
- Category breakdown: `identity=4, measure=5, temporal=4, dimension=10` ✓ (matches DBCP-1a §3.1 seed list)
- Constraints: 1 PK (`semantic_family_pkey`) + 2 CHECK (`semantic_family_category_chk`, `semantic_family_code_format_chk`) ✓
- Indexes: 2 (`semantic_family_pkey`, `idx_semantic_family_category`) ✓
- Existing primitive tables unchanged: `canonical_field=3097, business_field=7062, business_object=202` ✓

### DBCP-1j — `master.industry`

```
BEGIN
CREATE TABLE             11.478 ms
CREATE INDEX              2.460 ms
COMMENT                   0.300 ms
INSERT 0 16               0.965 ms
COMMIT                    3.475 ms
```

Postflight:
- `to_regclass('master.industry')` = `master.industry` ✓
- Seed rows: 16 total
- Sentinel rows (`is_cross_industry_sentinel = TRUE`): 1, on `cross_industry` ✓
- All non-sentinel rows are the specific industries listed in DBCP-1j §3.2 (alphabetical: agriculture, banking, energy, healthcare, hospitality, insurance, manufacturing, media_entertainment, pharmaceuticals, professional_services, real_estate, retail, software_saas, telecommunications, transportation) ✓
- Constraints: 1 PK (`industry_pkey`) + 2 CHECK (`industry_code_format_chk`, `industry_cross_sentinel_unique_chk`) ✓
- Indexes: 2 (`industry_pkey`, `idx_industry_cross_sentinel` — partial WHERE flag) ✓
- Existing primitive tables unchanged ✓

### DBCP-1c — `contract.certification_record`

```
BEGIN
CREATE TABLE             16.511 ms
CREATE INDEX × 3          4.340 ms (cumulative)
COMMENT                   0.272 ms
COMMIT                    4.730 ms
```

Postflight:
- `to_regclass('contract.certification_record')` = `contract.certification_record` ✓
- Row count: 0 (empty ledger) ✓
- Column count: **17** (note: bundled-MWR operator-approval prose said "16 columns" — off by one in the prose; the §3.3 DDL itself defines 17 columns; the live table matches the DDL exactly. Treated as a packet-prose typo, not a structural issue, by the same logic as the §2.4 schema-prefix typo. No semantic change.)
- Constraints: 1 PK (`certification_record_pkey`) + 3 CHECK (`certification_record_primitive_type_chk`, `certification_record_action_code_chk`, `certification_record_override_chk`) ✓
- Indexes: 4 (`certification_record_pkey`, `idx_certification_record_primitive`, `idx_certification_record_certifier`, `idx_certification_record_action`) ✓
- Existing primitive tables unchanged ✓

### DBCP-1f — `contract.primitive_provenance`

```
BEGIN
CREATE TABLE              7.235 ms
CREATE INDEX × 2          2.322 ms (cumulative)
COMMENT                   0.296 ms
COMMIT                    2.825 ms
```

Postflight:
- `to_regclass('contract.primitive_provenance')` = `contract.primitive_provenance` ✓
- Row count: 0 ✓
- Column count: 9 ✓ (matches DDL exactly)
- Constraints: 1 PK (`primitive_provenance_pkey`) + 3 CHECK (`primitive_provenance_type_chk`, `primitive_provenance_standard_chk`, `primitive_provenance_ref_chk`) ✓
- Indexes: 3 (`primitive_provenance_pkey`, `idx_primitive_provenance_primitive`, `idx_primitive_provenance_standard`) ✓
- Existing primitive tables unchanged ✓

### DBCP-2a — `contract.mc_envelope_audit_record`

```
BEGIN
CREATE TABLE             17.571 ms
CREATE INDEX × 4          7.145 ms (cumulative)
COMMENT                   0.372 ms
COMMIT                    2.899 ms
```

Postflight:
- `to_regclass('contract.mc_envelope_audit_record')` = `contract.mc_envelope_audit_record` ✓
- Row count: 0 ✓
- Column count: 14 ✓
- Constraints: 1 PK (`mc_envelope_audit_record_pkey`) + 3 CHECK (`mc_envelope_audit_action_chk`, `mc_envelope_audit_override_chk`, `mc_envelope_audit_supersede_chk`) ✓
- Indexes: 5 (`mc_envelope_audit_record_pkey`, `idx_mc_envelope_audit_mc`, `idx_mc_envelope_audit_op`, `idx_mc_envelope_audit_action`, `idx_mc_envelope_audit_finger` — partial WHERE not-null) ✓
- Existing primitive tables unchanged ✓

## Final combined §4 postflight

Run after all five DBCPs landed:

- §4.1 — all 5 tables present at their qualified names ✓
- §4.4 — 5 primary keys + 13 CHECK constraints across the 5 tables (3+3+3+2+2 CHECKs) ✓
- §4.5 — 16 indexes total across the 5 tables (4+5+3+2+2) ✓
- §4.6 — all 3 ledger tables empty (`certification_record`, `primitive_provenance`, `mc_envelope_audit_record`) ✓
- §4.7 — `canonical_field=3097, business_field=7062, business_object=202` matches preflight snapshot exactly ✓
- §4.8 (bc-core DB-vs-enum invariant) — deferred to a follow-up; bc-core test harness extension out of execution scope

## Findings surfaced during execution (all non-blocking)

| # | Finding | Action |
|---|---|---|
| EX-1 | §2.4 preflight referenced `metric.metric_contract`; live table is `contract.metric_contract`. | Patched in this file; documented above under "Pre-execution packet patch". |
| EX-2 | DBCP-1c bundled-MWR approval prose said "Schema reviewed (16 columns)" but the DDL defines 17 columns. The live table has 17 columns matching the DDL. | Prose typo only; DDL is correct; live table is correct. No re-execution needed. |

Both findings are prose-level documentation typos that surfaced via diligent postflight checks. Neither indicates a structural issue with the platform DB or the executed DDL.

## Modules now unblocked

Per the packet's §7 mapping, these become bindable:

| Module | Status |
|---|---|
| **SDA-2 Drizzle repository** (consumes `contract.certification_record`) | Unblocked. Author Drizzle-backed `CertificationRecordRepository` extending the existing abstract port. |
| **SDA-3 Drizzle repository** (consumes `contract.primitive_provenance` + per-primitive projection columns) | Unblocked. Author Drizzle history + projection repos with one-transaction atomicity. |
| **MCE-7 audit ledger repository** (consumes `contract.mc_envelope_audit_record`) | Unblocked. First author the mock-backed module mirroring SDA-2 / SDA-3 pattern, then Drizzle impl. |
| **G5 live enum lookup** (reads `master.semantic_family`) | Unblocked. G5 currently uses the in-code `SEMANTIC_FAMILY_ENUM` constant; can now be switched to DB-backed lookup with the invariant test extended to assert against the DB. |
| **C3 industry lookup** (reads `master.industry`) | Substrate unblocked. Phase 2 service code still to be written. |

## What was NOT touched in this execution

- No DBCP-1b (status_code CHECK + `is_archived`) — Tranche 2, separate session.
- No DBCP-1d (bulk `draft → proposed` migration) — deferred.
- No DBCP-1e (`primitive_supersession` central table) — deferred.
- No DBCP-1g / 1h / 1i (Tranche 3 additive-column DBCPs) — separate session.
- No service code changes in bc-core.
- No NestJS module wiring.
- No primitive certification acts.
- No metric repair writes.
- No tenant/runtime writes.
- No Apex demo certification work.
- No Drizzle schema file updates (that work follows when the Drizzle-backed repos are authored).

## Rollback availability

The §5 per-DBCP rollback SQL remains valid and unchanged. If any consumer surfaces a defect tied to one of the new tables, the rollback for that DBCP can be executed in isolation without affecting the others (all five are independent additive tables; no inter-table FK constraints).

## Correction note — DBCP-1f current-projection convenience retired (2026-05-12 PM)

The DBCP-1f draft (and the body of this packet's §3.4) describes a current-projection convenience:

> *Existing per-primitive `source_standard` / `standard_ref` columns on `contract.canonical_field`, `contract.business_field`, `contract.business_object` are retained as a backward-compat projection of the latest provenance row. The SDA-3 service writes both: a history row + the per-primitive projection columns, transactionally in production.*

**This assumption is false against the live schema.** Verified via `information_schema.columns` against `bc_platform_dev` while preparing the SDA-3 Drizzle slice (operator decision SES-594568 — Option A):

| Live DB column | `canonical_field` | `business_field` | `business_object` |
|---|---|---|---|
| `source_standard` | not present | not present | not present |
| `standard_ref` | not present | present | present |

The bc-core Drizzle schema files for the three primitive tables accurately model this — `canonical-field.ts` carries neither column; `business-field.ts` and `business-object.ts` carry `standard_ref` only. No `source_standard` exists on any of the three. The mismatch is between the DBCP-1f design prose and the live schema, not between code and DB.

### Resolution (Option A)

- **The SDA-3 projection layer is retired.** `contract.primitive_provenance` (DBCP-1f, executed in this packet) is the single source of truth for both history and current provenance.
- **Current provenance for a primitive is derived by querying the latest row** via `getLatestByPrimitive(primitiveType, primitiveId)`.
- **No new DBCP** to add the missing columns. **No partial projection.** **No ALTER TABLE** on the primitive tables.
- **No filed ADR amendment.** DEC-a17d0f §7 Q4 references the projection only as an implementation convenience; the convenience is dropped without changing any decided text. If a future implementation needs material divergence from DEC-a17d0f, a small amendment ADR is the path — not surfaced by this correction.

### Atomicity contract — moot

Because there is only one write per provenance act (history append; no projection follow-up), the atomicity contract documented in the prior `provenance-record.service.ts` header is no longer needed. The Drizzle implementation does not wrap multi-statement work in `db.transaction()` because there is no multi-statement work.

### Code changes that land with this correction (bc-core)

- `provenance-record.repository.ts` — `PrimitiveProvenanceProjectionRepository` abstract class + `InMemoryPrimitiveProvenanceProjectionRepository` removed. `ProvenanceProjection` type removed.
- `provenance-record.service.ts` — constructor reduced to one repository arg (history). `recordProvenance` writes one row. `getProjection` method removed. `getLatestByPrimitive` is the canonical current-state read.
- `provenance-record.spec.ts` — projection-repo + projection-service tests removed; history-only service tests cover the current-state-via-latest path.
- `provenance-record.drizzle.repository.ts` — `DrizzleProvenanceRecordRepository` ships now (no atomicity wrapper needed).

### Why this is a small correction, not an amendment

The four filed ADRs (DEC-a17d0f, DEC-b7affa, DEC-889238, DEC-af8247) do not depend on the projection convenience as a load-bearing decision. The provenance ledger itself (`contract.primitive_provenance`) is unchanged by this correction. Consumers that previously would have read the projection columns can read the history table instead — same authority, derived on read.

The packet text in §3.4 and §7 above is preserved as-is for the historical record. This correction note is the authoritative interpretation.

## Operator next step (no immediate execution required)

Tranche 1 is live. Recommended next moves, in priority order:

1. **MCE-7 mock-backed module** in bc-core, mirroring SDA-2 / SDA-3 patterns. Pure builder + repository port + in-memory impl + spec. No DBCP execution needed for this.
2. **Drizzle-backed repository implementations** for SDA-2, SDA-3, and (after MCE-7 mock lands) MCE-7. Each conforms to its existing abstract port; no service-code change required.
3. **NestJS module wiring** so the bc-core SDA + MCE modules can be instantiated against either in-memory (test) or Drizzle (production) impls via DI configuration. Still no endpoints.
4. **Tranche 2 execution packet** for DBCP-1b (status_code CHECK + `is_archived` column on the three primitive tables). Separate review session when ready.

No write authorisation is implied by this execution-result section. Each subsequent step requires its own operator approval per the Database Change Protocol.
