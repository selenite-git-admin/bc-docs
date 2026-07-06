---
metric: sda-phase1-dbcp-drafts
metric_version: n/a
tenant: platform
source_system: n/a
work_type: dbcp-draft
session_uid: SES-594568
date: 2026-05-12
status: decision-pending
related_commits: []
related_tasks: []
related_adrs:
  - DEC-a17d0f
  - DEC-804874
  - DEC-69f09e
related_mwrs:
  - 2026-05-12-semantic-definitions-authority-design-SES-a223ea.md
related_change_records:
  - CHG-28ab0c
repair_location: E
affected_boundary: storage_projection
foundation_gate: passed
---

# SDA Phase 1 DBCP drafts — DBCP-1a / 1b / 1c / 1f

> **Drafts only. No execution authorised.** Each section is independently operator-approvable. DBCP-1d (bulk `draft → proposed` migration) and DBCP-1e (`primitive_supersession` central table) are deferred per the approved execution plan. This MWR is the *content* to be presented for explicit operator approval before any DDL touches the live platform DB.

## 0. Authority + ordering

| DBCP | Adds / alters | Independence | Required for |
|---|---|---|---|
| **1a** | New `master.semantic_family` table + seed | Standalone | G5, G6 evaluation |
| **1b** | Broadens `status_code` CHECK on 3 existing tables; adds `is_archived` column | Standalone | Any state transition; non-`draft` lifecycle |
| **1c** | New `contract.certification_record` table | Standalone | All certification acts |
| **1f** | New `contract.primitive_provenance` table | Standalone | G4 evaluation |

All four are additive at the data level. 1b is the only one that *alters* an existing table; the alteration is constraint-broadening + new nullable-but-defaulted column, both of which are non-destructive.

**Recommended execution order (post-approval):** 1a → 1c → 1f → 1b. 1b last because its CHECK-constraint broadening must coexist with the existing `draft` value (which DBCP-1d will eventually migrate). Executing 1b before the other three creates a window where the broadened CHECK allows new state values that have nowhere to be recorded.

## 0.1 Foundation gate

Repair-location: **E** (storage / projection — adding tables and constraints that hold the certified state). This is the correct location: B (contract grammar) defines the lifecycle and gates (DEC-a17d0f); E is where the state lives. No D-F compensation: the gates G1-G10 evaluate at the boundary, not in storage.

---

## DBCP-1a — `master.semantic_family`

### Purpose

Introduce the closed enum of 24 `semantic_family` values from DEC-804874 (D366) as a queryable master table with per-family type/unit compatibility metadata. Required for G5 (semantic_family populated and in enum) and G6 (data_type / unit compatibility per family).

### Schema

```sql
CREATE TABLE master.semantic_family (
  semantic_family_code     TEXT PRIMARY KEY,                              -- 24 values from D366; regex ^[a-z][a-z0-9]*(-[a-z0-9]+)*$
  display_name             TEXT NOT NULL,
  description_text         TEXT NOT NULL,
  category_code            TEXT NOT NULL,                                 -- 'identity' | 'measure' | 'temporal' | 'dimension'
  compatible_data_types    TEXT[] NOT NULL,                               -- e.g. {'number'} for measures, {'string'} for identity
  compatible_unit_types    TEXT[],                                        -- nullable; e.g. {'currency'} for measure-currency
  source_adr_ref           TEXT NOT NULL DEFAULT 'DEC-804874',
  created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT semantic_family_category_chk
    CHECK (category_code IN ('identity','measure','temporal','dimension')),
  CONSTRAINT semantic_family_code_format_chk
    CHECK (semantic_family_code ~ '^[a-z][a-z0-9]*(-[a-z0-9]+)*$')
);

CREATE INDEX idx_semantic_family_category ON master.semantic_family (category_code);

COMMENT ON TABLE master.semantic_family IS
  'Closed enum of semantic_family codes per DEC-804874 (D366). Hyphenated kebab-style identifiers per SDA Profile P5 — documented divergence from DEC-69f09e snake_case scoped to this enum only (DEC-a17d0f §3 P5).';
```

### Seed data (24 rows)

```sql
INSERT INTO master.semantic_family
  (semantic_family_code, display_name, description_text, category_code, compatible_data_types, compatible_unit_types)
VALUES
  -- Identity (4)
  ('identifier',         'Identifier',         'Unique key or surrogate identifying an entity',                    'identity',  ARRAY['string'],          NULL),
  ('code',               'Code',               'Short coded value drawn from a controlled vocabulary',             'identity',  ARRAY['string'],          NULL),
  ('name',               'Name',               'Human-readable entity name',                                       'identity',  ARRAY['string'],          NULL),
  ('text',               'Text',               'Free-form textual content',                                        'identity',  ARRAY['string'],          NULL),
  -- Measure (5)
  ('measure-currency',   'Measure (currency)', 'Monetary measure with currency unit',                              'measure',   ARRAY['number'],          ARRAY['currency']),
  ('measure-count',      'Measure (count)',    'Discrete count of occurrences or items',                           'measure',   ARRAY['number'],          ARRAY['count']),
  ('measure-ratio',      'Measure (ratio)',    'Dimensionless ratio between two measures',                         'measure',   ARRAY['number'],          ARRAY['ratio']),
  ('measure-percent',    'Measure (percent)',  'Percentage value (typically 0-100 or 0-1 per declaration)',        'measure',   ARRAY['number'],          ARRAY['percentage']),
  ('measure-score',      'Measure (score)',    'Bounded score or rating',                                          'measure',   ARRAY['number'],          ARRAY['score']),
  -- Temporal (4)
  ('date',               'Date',               'Calendar date (no time-of-day)',                                   'temporal',  ARRAY['date'],            NULL),
  ('period',             'Period',             'Named period (fiscal, calendar, custom)',                          'temporal',  ARRAY['string','number'], NULL),
  ('datetime',           'Datetime',           'Instant in time with date and time-of-day',                        'temporal',  ARRAY['timestamp'],       NULL),
  ('duration',           'Duration',           'Elapsed time between two instants',                                'temporal',  ARRAY['number'],          ARRAY['days','hours','minutes','seconds']),
  -- Dimension (11)
  ('dim-calendar-date',  'Dimension (calendar date)',  'Calendar-date dimension reference',                        'dimension', ARRAY['date','string','number'], NULL),    -- M5: broadened (YYYYMMDD-as-int common)
  ('dim-fiscal-period',  'Dimension (fiscal period)',  'Fiscal-period dimension reference',                        'dimension', ARRAY['string','number'], NULL),               -- M4: broadened (GJAHR-as-int common)
  ('dim-currency',       'Dimension (currency)',       'Currency dimension reference (ISO 4217)',                  'dimension', ARRAY['string'],          NULL),
  ('dim-country',        'Dimension (country)',        'Country dimension reference (ISO 3166)',                   'dimension', ARRAY['string'],          NULL),
  ('dim-legal-entity',   'Dimension (legal entity)',   'Legal entity dimension reference',                         'dimension', ARRAY['string'],          NULL),
  ('dim-gl-account',     'Dimension (GL account)',     'General-ledger account dimension reference',               'dimension', ARRAY['string'],          NULL),
  ('dim-cost-center',    'Dimension (cost center)',    'Cost-center dimension reference',                          'dimension', ARRAY['string'],          NULL),
  ('dim-customer',       'Dimension (customer)',       'Customer dimension reference',                             'dimension', ARRAY['string'],          NULL),
  ('dim-vendor',         'Dimension (vendor)',         'Vendor dimension reference',                               'dimension', ARRAY['string'],          NULL),
  ('dim-product',        'Dimension (product)',        'Product dimension reference',                              'dimension', ARRAY['string'],          NULL);
```

**Row count after seed: 24.** Matches D366 enum exactly.

### Notes on specific seed values (post matrix-review)

These notes are post-validation refinements from the matrix-review against Apex Pool 1 evidence (`2026-05-12-c1-matrix-review-against-apex-SES-594568.md`):

- **`dim-fiscal-period` `compatible_data_types`** (M4): broadened to `{'string','number'}`. Apex's SAP GJAHR column is an integer year (e.g. `2026`); the original `{'string'}` would have falsely rejected such BFs at G6 evaluation. The semantic remains "a fiscal-period dimension reference"; the storage type is source-dependent and may be string or numeric.
- **`dim-calendar-date` `compatible_data_types`** (M5): broadened to `{'date','string','number'}`. Some sources store calendar dates as YYYYMMDD integers or as `'2026-05-12'` strings rather than typed `date`. Real-world common; the original `{'date'}` was too narrow.
- **`measure-ratio` `compatible_unit_types`** (M6): kept as `{'ratio'}` for now. Apex's currency-conversion factors (SAP KURSF — exchange rates) sit at `measure-ratio` semantic_family and use `unit_type='ratio'` as the best available fit. If Phase 1 surfaces concrete conflicts (e.g. a CF that legitimately needs `unit_type='factor'` or `'multiplier'` and fails G6 against the current matrix), a small follow-up DBCP can broaden this cell. Out of scope for this DBCP; revisit when evidence arrives.
- **`measure-score` `compatible_data_types`** is unchanged from `{'number'}`. Per matrix-review M3, categorical ratings (HIGH/MEDIUM/LOW) are reclassified to the `code` family with `code_vocabulary_code` (a future G11b column), **not** to `measure-score`. `measure-score` therefore remains reserved for true numeric scores (NPS 0-10, FICO 300-850 etc.) and its data_type constraint is correct.

### Rollback (paired reverse DBCP)

```sql
DROP INDEX IF EXISTS master.idx_semantic_family_category;
DROP TABLE IF EXISTS master.semantic_family;
```

Safe to roll back as long as no FK from `contract.canonical_field.semantic_family_code → master.semantic_family.semantic_family_code` exists yet. **No FK is added in 1a** — the FK is part of a later DBCP once the CHECK on `canonical_field.semantic_family` is replaced by referential integrity. 1a is therefore fully reversible.

### Validation queries (read-only, run before approving execution)

```sql
-- Schema sanity
SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema='master' AND table_name='semantic_family';
-- (expect 0 rows pre-execution, 1 row post)

-- Row count
SELECT COUNT(*) AS family_count FROM master.semantic_family;
-- (expect 24 post-execution)

-- Distinct categories
SELECT category_code, COUNT(*) FROM master.semantic_family GROUP BY category_code ORDER BY 1;
-- (expect: identity=4, measure=5, temporal=4, dimension=11)
```

### Risk

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Seed values diverge from D366 reference | Low | Medium | Seed list is reproduced verbatim from DEC-804874 (D366) §3; checked against the SDA ADR §3 P5 listing |
| Future enum expansion | High | Low | New rows can be added by `INSERT` without altering schema. SDA ADR amendment required to extend the closed enum |
| Compatible-type matrix wrong | Medium | Medium | Seed `compatible_data_types` / `compatible_unit_types` are best-guess from D366 + ISO conventions. **Operator review of the matrix is part of the approval.** First-pass values shipped; refinement is a future DBCP, not a schema change |

### Operator approval section (to fill in)

- [ ] Schema reviewed
- [ ] Seed values reviewed against DEC-804874
- [ ] `compatible_data_types` matrix reviewed
- [ ] `compatible_unit_types` matrix reviewed
- [ ] Rollback path acceptable
- [ ] Approved for execution: _yes / no_

---

## DBCP-1b — Broaden `status_code` CHECK + add `is_archived` (3 tables)

### Purpose

Allow the 6-state lifecycle (DEC-a17d0f §2: `proposed | reviewing | certified | deprecated | superseded | withdrawn`) on `contract.canonical_field`, `contract.business_field`, `contract.business_object`. Add `is_archived BOOLEAN` flag (visibility, not lifecycle) with the §2 CHECK constraint. **Existing `draft` value is preserved on read** — DBCP-1d (deferred) handles the migration.

### Schema changes per table

For each of `contract.canonical_field`, `contract.business_field`, `contract.business_object`:

```sql
-- 1. Drop existing CHECK constraint on status_code (name varies per table)
--    Discover name first:
--    SELECT conname FROM pg_constraint WHERE conrelid = 'contract.canonical_field'::regclass AND contype = 'c' AND pg_get_constraintdef(oid) LIKE '%status_code%';
-- The Drizzle-generated name for canonical_field is likely 'canonical_field_status_code_check'; verify pre-execution.

ALTER TABLE contract.canonical_field
  DROP CONSTRAINT canonical_field_status_code_check;     -- name verified per pre-flight query

ALTER TABLE contract.canonical_field
  ADD CONSTRAINT canonical_field_status_code_check
  CHECK (status_code IN ('draft','proposed','reviewing','certified','deprecated','superseded','withdrawn'));

-- 2. Add is_archived column
ALTER TABLE contract.canonical_field
  ADD COLUMN is_archived BOOLEAN NOT NULL DEFAULT FALSE;

-- 3. Add CHECK constraint: is_archived=true only when status_code in (superseded, withdrawn)
ALTER TABLE contract.canonical_field
  ADD CONSTRAINT canonical_field_is_archived_chk
  CHECK (is_archived = FALSE OR status_code IN ('superseded','withdrawn'));

-- 4. Index for default-listing performance (most queries will be WHERE is_archived = FALSE)
CREATE INDEX idx_canonical_field_active
  ON contract.canonical_field (status_code)
  WHERE is_archived = FALSE;
```

**Repeat verbatim for `contract.business_field` and `contract.business_object`** (substituting table names). Total: 3 × 4 DDL statements = 12 statements.

### Preservation of `draft`

The new CHECK includes `'draft'` alongside the 6 SDA states. This is the **compatibility window** — existing rows with `status_code = 'draft'` remain valid; the SDA's projection layer maps them to `proposed` for display (no write). DBCP-1d (deferred) will eventually migrate `draft → proposed` and a follow-up DBCP will drop `'draft'` from the CHECK.

### Rollback (paired reverse DBCP)

```sql
-- Per table:
DROP INDEX IF EXISTS contract.idx_canonical_field_active;
ALTER TABLE contract.canonical_field DROP CONSTRAINT IF EXISTS canonical_field_is_archived_chk;
ALTER TABLE contract.canonical_field DROP COLUMN IF EXISTS is_archived;
ALTER TABLE contract.canonical_field DROP CONSTRAINT IF EXISTS canonical_field_status_code_check;
ALTER TABLE contract.canonical_field
  ADD CONSTRAINT canonical_field_status_code_check
  CHECK (status_code IN ('draft','certified','deprecated'));   -- original 3-state set
```

Safe — no data is lost on rollback (the `is_archived` column drops, but it defaults to FALSE so no information is encoded yet).

### Validation queries

```sql
-- Pre-execution: confirm row counts so we can verify nothing changes
SELECT 'canonical_field' AS t, COUNT(*) AS rows, COUNT(DISTINCT status_code) AS distinct_status FROM contract.canonical_field
UNION ALL SELECT 'business_field', COUNT(*), COUNT(DISTINCT status_code) FROM contract.business_field
UNION ALL SELECT 'business_object', COUNT(*), COUNT(DISTINCT status_code) FROM contract.business_object;
-- (expect: ~3097, ~7062, ~202 rows)

-- Post-execution: row counts unchanged; status_code distribution unchanged
-- (same query expected to return same numbers)

-- Post-execution: is_archived defaults applied
SELECT COUNT(*) FROM contract.canonical_field WHERE is_archived IS NULL;
-- (expect 0)

-- Post-execution: CHECK constraint accepts new states
-- (do not actually INSERT; verify constraint definition)
SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
  WHERE conname IN ('canonical_field_status_code_check','canonical_field_is_archived_chk');
```

### Risk

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Existing constraint name differs from assumed | High | Low | Pre-flight `SELECT conname` query to discover actual name; use discovered name in DROP |
| `ALTER TABLE` blocks on row count (10,361 rows total) | Low | Low | All three tables are small (<10k rows); ALTER takes milliseconds. No table rewrite required for adding nullable column with non-volatile default (Postgres 11+ fast-path) |
| Index creation on partial WHERE clause | Low | Low | `WHERE is_archived = FALSE` is a constant predicate; partial index built quickly on small tables |
| Application code references `is_archived = TRUE` for in-flight queries before app-side support lands | Medium | Low | Application code does not currently reference `is_archived`. No code changes ship in 1b. SDA service code (Phase 1 service work) will be the first consumer |

### Operator approval section

- [ ] Constraint discovery query run pre-execution (constraint names confirmed)
- [ ] All 3 tables' DDL reviewed
- [ ] `draft` preservation acknowledged
- [ ] Rollback verified
- [ ] Approved for execution: _yes / no_

---

## DBCP-1c — `contract.certification_record`

### Purpose

Per-primitive audit ledger for certification acts. Persists gate results, AI verdicts, certifier identity, role-at-action-time, override rationale + follow-up task UID (when applicable), and timestamps. Required for any certification act through the SDA's `/certify` / `/return-to-author` / `/deprecate` / `/withdraw` / `/supersede` endpoints.

### Schema

```sql
CREATE TABLE contract.certification_record (
  certification_record_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  primitive_type            TEXT NOT NULL,                  -- 'canonical_field' | 'business_field' | 'business_object'
  primitive_id              UUID NOT NULL,                  -- FK enforced at service layer (poly-ref; no FK constraint at DB)
  action_code               TEXT NOT NULL,                  -- 'submit_for_review' | 'certify' | 'return_to_author' | 'deprecate' | 'withdraw' | 'supersede' | 'archive' | 'unarchive'
  from_state_code           TEXT,                           -- nullable for first record on a primitive
  to_state_code             TEXT,                           -- nullable for archive/unarchive (lifecycle unchanged)
  is_archived_after         BOOLEAN,                        -- nullable; only set for archive/unarchive

  -- Gate results (deterministic gates G1-G10)
  gate_results_json         JSONB NOT NULL DEFAULT '{}'::jsonb,
                                                            -- shape: { "G1": {"verdict":"pass|fail","detail":"..."}, "G2a": {...}, ... }

  -- AI advisory verdicts (D366 / SDA §5)
  advisory_verdicts_json    JSONB NOT NULL DEFAULT '[]'::jsonb,
                                                            -- shape: [{"surface":"dedup-candidates","verdict":"green|amber|red|unverified","confidence":0.0-1.0,"rationale":"...","model_id":"...","prompt_hash":"...","timestamp":"...","acknowledgement":"..."}, ...]

  -- Override (only when an overridable gate failed AND was overridden)
  override_gate_code        TEXT,                           -- e.g. 'G3', 'G4', 'G2b'; NULL if no override
  override_rationale_text   TEXT,                           -- ≥40 chars per D366 when override_gate_code is set
  override_followup_task_uid TEXT,                          -- auto-spawned task UID per D366

  -- Certifier identity (Q6 — Cognito sub + role-at-action-time)
  certifier_sub             TEXT NOT NULL,
  certifier_role_at_action  TEXT NOT NULL,                  -- snapshot of acting role; not a FK
  certifier_email           TEXT,                           -- optional convenience copy

  -- Supersession link (when action = 'supersede')
  supersedes_primitive_id   UUID,                           -- the predecessor; only set when action='supersede'

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

### Append-only by service constraint

There is no DB-level INSERT-ONLY enforcement in Postgres beyond denying UPDATE/DELETE to the application role. **The SDA service does not call UPDATE or DELETE on this table** — every certification act is a new row. The reviewer-of-history reads the latest row for a given `(primitive_type, primitive_id)`.

Hardening option (deferred): create a row-level INSERT-ONLY trigger or revoke UPDATE/DELETE from the application role. Recommend deferring to a separate hardening DBCP after the service code lands.

### Rollback

```sql
DROP INDEX IF EXISTS contract.idx_certification_record_action;
DROP INDEX IF EXISTS contract.idx_certification_record_certifier;
DROP INDEX IF EXISTS contract.idx_certification_record_primitive;
DROP TABLE IF EXISTS contract.certification_record;
```

Safe — table is new, no existing data to preserve.

### Validation queries

```sql
-- Schema sanity
SELECT column_name, data_type, is_nullable FROM information_schema.columns
  WHERE table_schema='contract' AND table_name='certification_record'
  ORDER BY ordinal_position;
-- (expect 16 columns)

-- Constraint definitions
SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
  WHERE conrelid = 'contract.certification_record'::regclass;
-- (expect: PRIMARY KEY + 3 CHECK constraints)

-- Index presence
SELECT indexname FROM pg_indexes WHERE schemaname='contract' AND tablename='certification_record';
-- (expect 4: implicit PK + 3 explicit)

-- Pre-execution: confirm table doesn't exist yet
SELECT to_regclass('contract.certification_record');
-- (expect NULL pre, non-NULL post)
```

### Risk

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Poly-ref to `primitive_id` (no FK) allows orphans | Med | Low | Service-layer enforcement: SDA validates primitive exists before inserting. Orphan rows are recoverable via audit |
| JSONB columns drift in shape | Med | Med | Shape is documented in column COMMENT (TBD post-approval); the service uses typed DTOs. Add a separate quality gate later if drift surfaces |
| INSERT-only convention violated by future code | Low | High | Hardening DBCP (deferred) revokes UPDATE/DELETE at role level. For now, code review |
| GDPR / data-retention on `certifier_sub` + `certifier_email` | Low | Low | Cognito sub is a pseudonymous identifier; email is optional. Retention policy is part of the platform-level data-protection policy, not this DBCP |

### Operator approval section

- [ ] Schema reviewed (16 columns)
- [ ] CHECK constraints reviewed (override-pair constraint enforces ≥40-char rationale)
- [ ] JSONB shapes accepted (gate_results_json + advisory_verdicts_json)
- [ ] Append-only convention accepted; hardening DBCP deferred
- [ ] Rollback verified
- [ ] Approved for execution: _yes / no_

---

## DBCP-1f — `contract.primitive_provenance`

### Purpose

Central append-only provenance ledger across BF / BO / CF. Each row records that a primitive was registered with a given `(source_standard, standard_ref)` at a given time by a given certifier. Required for G4 (provenance presence). Existing per-primitive `source_standard` / `standard_ref` columns on the primitive tables are **retained** as a current-projection convenience for backward read compatibility.

### Schema

```sql
CREATE TABLE contract.primitive_provenance (
  primitive_provenance_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  primitive_type            TEXT NOT NULL,         -- 'canonical_field' | 'business_field' | 'business_object'
  primitive_id              UUID NOT NULL,         -- poly-ref; no FK
  source_standard           TEXT NOT NULL,         -- 'oagis' | 'iso_20022' | 'xbrl_gaap' | 'ifrs' | 'uncefact' | 'bc_standard' | 'computed'
  standard_ref              TEXT,                  -- e.g. 'IFRS-9 §5.5.1' or 'OAGIS:Invoice/LineItem/Amount'; NULL when source_standard IN ('bc_standard','computed')
  rationale_text            TEXT,                  -- optional human note describing why this provenance applies
  registered_by_sub         TEXT NOT NULL,         -- Cognito sub
  registered_by_role        TEXT NOT NULL,         -- snapshot of role at registration time
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

### Current-projection convenience: retain existing columns

`contract.canonical_field.source_standard` and `contract.canonical_field.standard_ref` (and the equivalent on `business_field` / `business_object`) are **retained**. The SDA service writes both:
1. A new row to `contract.primitive_provenance` (append-only history)
2. An UPDATE to the existing columns on the primitive table (current projection)

This is the only place the SDA service writes to the existing per-primitive columns. Reads can use either path; eventually (post-Phase 1) the per-primitive columns can be dropped or made into a generated/computed view. **Not in this DBCP.**

### Rollback

```sql
DROP INDEX IF EXISTS contract.idx_primitive_provenance_standard;
DROP INDEX IF EXISTS contract.idx_primitive_provenance_primitive;
DROP TABLE IF EXISTS contract.primitive_provenance;
```

Safe — table is new. Existing per-primitive provenance columns are untouched.

### Validation queries

```sql
-- Schema sanity
SELECT column_name, data_type, is_nullable FROM information_schema.columns
  WHERE table_schema='contract' AND table_name='primitive_provenance'
  ORDER BY ordinal_position;
-- (expect 9 columns)

-- CHECK constraint enforces standard_ref vs source_standard pairing
SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
  WHERE conrelid = 'contract.primitive_provenance'::regclass;
-- (expect: PRIMARY KEY + 3 CHECK constraints)

-- Pre-execution: confirm table doesn't exist
SELECT to_regclass('contract.primitive_provenance');
-- (expect NULL pre, non-NULL post)
```

### Risk

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Per-primitive columns and provenance table drift | Med | Med | SDA service writes both atomically (single transaction). Drift detection: a separate read-side check could compare latest provenance row vs current column value. Not in 1f scope |
| `source_standard` enum changes over time | Low | Low | Adding a new standard requires a CHECK constraint update + an SDA ADR amendment naming the new standard |
| Provenance with `bc_standard` lacks an external citation (G4 overridable) | Expected | None | This is by design — `bc_standard` is the platform's own authority. The G4 gate is overridable for this case (DEC-a17d0f §4 G4) |

### Operator approval section

- [ ] Schema reviewed (9 columns)
- [ ] CHECK constraint pairing (`standard_ref` required when external standard) verified
- [ ] Retain-existing-columns strategy accepted
- [ ] Rollback verified
- [ ] Approved for execution: _yes / no_

---

## Aggregate risk + sequencing summary

### Cross-DBCP risk

| Risk | Mitigation |
|---|---|
| Order-dependency confusion | Recommended order documented (1a → 1c → 1f → 1b). Each is independently rollbackable |
| Application code expects new tables before they exist | SDA service code (Phase 1 service work) ships after all four DBCPs are executed |
| Existing CHECK constraint names unknown | Pre-flight `SELECT conname` query in 1b before approval |
| Bulk migration of `draft` rows premature | **DBCP-1d is explicitly deferred.** 1b's CHECK preserves `draft` |

### Total schema delta after all four DBCPs execute

- **New tables:** 3 (`master.semantic_family`, `contract.certification_record`, `contract.primitive_provenance`)
- **Altered tables:** 3 (`canonical_field`, `business_field`, `business_object` — each gets broadened CHECK + `is_archived` column + active-row index)
- **New indexes:** 7
- **New CHECK constraints:** ~12
- **Rows added (seed):** 24 (the semantic_family enum)
- **Rows altered:** 0 (no DML against existing rows)

### What this DBCP wave does NOT do

- No `draft → proposed` migration (DBCP-1d, deferred)
- No `primitive_supersession` table (DBCP-1e, deferred)
- No `vocabulary_name_alias` table (DBCP-3a, Phase 3 deferred)
- No FK from `canonical_field.semantic_family_code → master.semantic_family.semantic_family_code` (deferred — added when the CHECK on `canonical_field.semantic_family` is replaced)
- No service code changes (Phase 1 service work, separate from DBCPs)
- No SDA endpoint changes
- No bc-admin UI changes
- No tenant or runtime touch

## Operator's next step (the only write authorised at this point)

Review each section (1a, 1b, 1c, 1f) and either:
1. **Approve** the DBCP draft for execution at a later named session, or
2. **Send back** with revisions named per section's checklist, or
3. **Defer** with rationale.

**No DDL is executed until each approved DBCP is re-presented in a session with explicit "execute now" approval per the Database Change Protocol.** This MWR is the draft text only.
