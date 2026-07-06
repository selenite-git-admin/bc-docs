---
metric: phase1-tranche1-dbcp-bundle
metric_version: n/a
tenant: platform
source_system: n/a
work_type: dbcp-review-packet
session_uid: SES-594568
date: 2026-05-12
status: decision-pending
related_commits: []
related_tasks: []
related_adrs:
  - DEC-a17d0f
  - DEC-b7affa
  - DEC-889238
  - DEC-af8247
  - DEC-804874
related_mwrs:
  - 2026-05-12-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md
  - 2026-05-12-c1-matrix-review-against-apex-SES-594568.md
  - 2026-05-12-c3-cross-domain-scope-draft-SES-594568.md
related_change_records:
  - CHG-28ab0c
repair_location: E
affected_boundary: storage_projection
foundation_gate: passed
---

# Phase 1 Tranche 1 — bundled DBCP review packet

> **Draft only. No execution authorised.** This packet collects the five **additive** Tranche 1 DBCPs for a single operator-approval session per the Database Change Protocol. **No DDL runs** as a result of this packet. After review + per-DBCP approval, each DBCP executes against the live platform DB in a named subsequent session with explicit "execute now" approval.

## 0. Tranche 1 scope

Five purely additive DBCPs. None touches existing data. All independently rollbackable. Approved-as-a-bundle is acceptable per operator's filing-plan response (because all are additive new tables/seeds); individual approval within the bundle is also acceptable.

| DBCP | Adds | Seed data | Source ADR | Status |
|---|---|---|---|---|
| **1a** | `master.semantic_family` table + seed | Closed enum listed in §3 | DEC-a17d0f §7 + DEC-804874 (D366) | Drafted (matrix-review M4-M6 applied) |
| **1j** | `master.industry` table + seed | Closed enum listed in §4 (`cross_industry` sentinel + the specific industries per DEC-af8247 §2) | DEC-af8247 §2 | **Authored in this packet (§4)** |
| **1c** | `contract.certification_record` (audit ledger) | none (table only) | DEC-a17d0f §7 + DEC-b7affa | Drafted |
| **1f** | `contract.primitive_provenance` (provenance ledger) | none | DEC-a17d0f §7 | Drafted |
| **2a** | `contract.mc_envelope_audit_record` (MC envelope audit ledger) | none | DEC-889238 §7 | **Authored in this packet (§5)** |

**Recommended execution order within the bundle (post-approval):** 1a → 1j → 1c → 1f → 2a. No internal dependencies between any two, so order is for human readability only.

**Total schema delta:** 5 new tables; seed rows for `master.semantic_family` and `master.industry` listed in §3 and §4; 0 alters, 0 existing rows touched, 0 row mutations. Maximally additive.

**Tranche 2 (DBCP-1b status_code CHECK broaden + is_archived) and Tranche 3 (DBCP-1g BF.semantic_family, DBCP-1h tenant.industries+compat-mode, DBCP-1i metric_definition.applicable_industries) are NOT in this packet** — they alter existing tables and warrant their own approval sessions per the Phase 1 execution plan.

## 1. Findings from this review pass

Three findings surfaced while bundling. None block the packet; all are flagged for transparency.

### Finding F1 — semantic_family enum count claims in some prior prose do not match the enumerated values

DEC-804874 (D366), DEC-a17d0f §3 P5, DEC-b7affa, and the original DBCP-1a draft (`...-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md`) each describe the `semantic_family` enum with a fixed-count adjective in prose. The enumerated values themselves are the contract; the prose counts do not match the enumeration. The authoritative enum is encoded in the pre-existing Phase 0 `bc-core/src/registry/semantic-definitions/profiles.ts` (`SEMANTIC_FAMILY_ENUM`), reviewed and approved through DEC-a17d0f, and exercised by the SDA-1 gates module tests via an invariant assertion that the default compatibility matrix is coextensive with `SEMANTIC_FAMILY_ENUM` (no hardcoded count in the test).

This is a **prose glitch, not a semantic change.** The enumeration is unchanged.

**Action in this packet:** the DBCP-1a draft's fixed-count claims are dropped in §3 below. The seed is the listed enumeration, period. Filed ADRs are not amended for this prose glitch (per the operator's policy: filed ADRs are not touched purely for count-language cleanup).

### Finding F2 — industry enum description and body framing diverge on whether the cross_industry sentinel is "in the enum"

DEC-af8247 §2 lists specific industries (hospitality through agriculture, per the body listing) and separately defines `cross_industry` as the catch-all default. The body frames `cross_industry` as the sentinel distinct from the specific-industry set; the description prose collapses both into a single "closed enum". This is a framing inconsistency in the ADR, not a semantic divergence — the substance is unambiguous: `cross_industry` is the sentinel default; the specific industries are listed in §2.

**Action in this packet:** DBCP-1j seeds the `cross_industry` row alongside the specific industries, with an explicit `is_cross_industry_sentinel BOOLEAN` flag to make the distinction queryable at runtime. The seed list is the contract; counts are not used. Filed ADRs are not amended for this framing glitch.

### Finding F3 — DBCP-1a `compatible_data_types` / `compatible_unit_types` were broadened per matrix-review M4-M6

Per the matrix-review against 246 Apex variable inputs (`...-c1-matrix-review-against-apex-SES-594568.md`):

- **M4** — `dim-fiscal-period` `compatible_data_types` broadened from `{'string'}` to `{'string','number'}` (Apex GJAHR is integer)
- **M5** — `dim-calendar-date` `compatible_data_types` broadened from `{'date'}` to `{'date','string','number'}` (YYYYMMDD-as-integer common)
- **M6** — `measure-ratio` `compatible_unit_types` kept at `{'ratio'}` with revisit-on-conflict note

These broadenings are already in the DBCP-1a draft and are carried forward verbatim in §3. The SDA-1 gates module tests exercise the same matrix (M4-M6 fixtures).

## 2. Foundation gate

Repair-location: **E** (storage / projection). New tables hold state defined by Lane A/C governance (B layer). No D-F compensation: gates evaluate at the boundary, not in storage.

The packet does not propose any change to the foundation invariants, the contract grammar, or the evaluation boundaries. It adds 5 storage substrate tables exactly as specified by the four filed ADRs (DEC-a17d0f, DEC-b7affa, DEC-889238, DEC-af8247).

---

## 3. DBCP-1a — `master.semantic_family`

### Purpose

Queryable master table holding the closed enum of `semantic_family` values from DEC-804874 (D366) with per-family type/unit compatibility metadata. Required for G5 (semantic_family populated and in enum) and G6 (data_type / unit compatibility per family). G5 + G6 unit-tested in `bc-core/src/registry/semantic-definitions/gates.spec.ts` using a fixture matrix coextensive with this seed (the test asserts the invariant via `SEMANTIC_FAMILY_ENUM`).

### Forward DDL

```sql
CREATE TABLE master.semantic_family (
  semantic_family_code     TEXT PRIMARY KEY,
  display_name             TEXT NOT NULL,
  description_text         TEXT NOT NULL,
  category_code            TEXT NOT NULL,        -- 'identity' | 'measure' | 'temporal' | 'dimension'
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
```

### Seed data — closed enum listed below

The authoritative member set is the listed rows; it matches the pre-existing Phase 0 `profiles.ts SEMANTIC_FAMILY_ENUM` and is invariant-tested by the SDA-1 gates module.

```sql
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
  ('dim-calendar-date',  'Dimension (calendar date)',  'Calendar-date dimension reference',                        'dimension', ARRAY['date','string','number'], NULL),  -- M5
  ('dim-fiscal-period',  'Dimension (fiscal period)',  'Fiscal-period dimension reference',                        'dimension', ARRAY['string','number'], NULL),         -- M4
  ('dim-currency',       'Dimension (currency)',       'Currency dimension reference (ISO 4217)',                  'dimension', ARRAY['string'],          NULL),
  ('dim-country',        'Dimension (country)',        'Country dimension reference (ISO 3166)',                   'dimension', ARRAY['string'],          NULL),
  ('dim-legal-entity',   'Dimension (legal entity)',   'Legal entity dimension reference',                         'dimension', ARRAY['string'],          NULL),
  ('dim-gl-account',     'Dimension (GL account)',     'General-ledger account dimension reference',               'dimension', ARRAY['string'],          NULL),
  ('dim-cost-center',    'Dimension (cost center)',    'Cost-center dimension reference',                          'dimension', ARRAY['string'],          NULL),
  ('dim-customer',       'Dimension (customer)',       'Customer dimension reference',                             'dimension', ARRAY['string'],          NULL),
  ('dim-vendor',         'Dimension (vendor)',         'Vendor dimension reference',                               'dimension', ARRAY['string'],          NULL),
  ('dim-product',        'Dimension (product)',        'Product dimension reference',                              'dimension', ARRAY['string'],          NULL);
```

**Seed member set:** the rows above. Authoritative; equivalent to `bc-core profiles.ts SEMANTIC_FAMILY_ENUM` (invariant-tested in `gates.spec.ts`). No fixed-count claim is part of this DBCP.

### Rollback

```sql
DROP INDEX IF EXISTS master.idx_semantic_family_category;
DROP TABLE IF EXISTS master.semantic_family;
```

No FK references this table yet (DBCP-1g introduces the FK from `business_field.semantic_family_code` — Tranche 3). Safe to rollback.

### Preflight queries (read-only, run before approval)

```sql
-- Confirm table doesn't already exist
SELECT to_regclass('master.semantic_family');
-- expect NULL pre-execution

-- Confirm master schema exists
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'master';
-- expect 1 row
```

### Idempotence check

Re-executing the DDL fails on `CREATE TABLE` (table already exists). Re-executing the seed fails on PK collision. **Not idempotent by design** — DBCP execution is single-shot. Rollback + re-execute is the supported re-run pattern.

### Risk

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Seed values diverge from D366 | Low | Med | Verbatim from `profiles.ts SEMANTIC_FAMILY_ENUM` (Phase 0, approved) |
| Compatibility-matrix wrong for a family | Med | Med | M4-M6 already applied per matrix-review evidence; revisit-on-conflict policy stated in DEC-b7affa §4.4 |
| Future enum expansion | High | Low | New rows via INSERT — no schema change. Per-family compatibility matrix is governance-changeable via amendment ADR |

---

## 4. DBCP-1j — `master.industry`

### Purpose

Closed enum of industry codes per DEC-af8247 §2. Used by `metric_definition.applicable_industries` (DBCP-1i Tranche 3) and `tenant.industries` (DBCP-1h Tranche 3). Required for C3 cross-domain scope gate at tenant binding.

### Forward DDL

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
    -- Only the 'cross_industry' code may have is_cross_industry_sentinel=true.
    CHECK (
      (is_cross_industry_sentinel = TRUE AND industry_code = 'cross_industry')
      OR is_cross_industry_sentinel = FALSE
    )
);

CREATE INDEX idx_industry_cross_sentinel ON master.industry (is_cross_industry_sentinel) WHERE is_cross_industry_sentinel = TRUE;

COMMENT ON TABLE master.industry IS
  'Closed enum of industry codes per DEC-af8247 (D406) §2. The `cross_industry` row is the catch-all sentinel; the remaining rows are specific industries per the §2 body listing. The is_cross_industry_sentinel flag is queryable; only the cross_industry row may have it set. Authoritative member set lives in seed rows; extension via amendment ADR.';
```

### Seed data — closed enum listed below

The authoritative member set is the listed rows. The `cross_industry` row carries `is_cross_industry_sentinel = TRUE`; the remaining rows are the specific industries per DEC-af8247 §2 body listing.

```sql
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

**Seed member set:** the rows above. Authoritative; the `cross_industry` row is the sentinel default per DEC-af8247 §2; the remaining rows are the specific industries listed in the ADR §2 body. No fixed-count claim is part of this DBCP.

### Rollback

```sql
DROP INDEX IF EXISTS master.idx_industry_cross_sentinel;
DROP TABLE IF EXISTS master.industry;
```

No FK references yet (DBCP-1h and DBCP-1i introduce the FKs — Tranche 3). Safe to rollback.

### Preflight queries

```sql
-- Confirm table doesn't already exist
SELECT to_regclass('master.industry');
-- expect NULL pre-execution

-- Confirm master schema exists (shared check with 1a)
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'master';
-- expect 1 row
```

### Idempotence

Not idempotent — single-shot per the DBCP-1a pattern.

### Risk

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| 15-industry enum too coarse | Med | Low | Sub-industry extension via amendment ADR per DEC-af8247 §8 |
| Industry naming bikeshed | Med | Low | Verbatim from DEC-af8247 §2; not re-litigated |
| Naming collision with NAICS / GICS | Low | Low | Internal taxonomy per DEC-af8247 §8 — external alignment out of v1 scope |
| Missing industry for a real tenant | Med | Low | Documented expansion path (amendment ADR); no tenant in current dev/pilot population is mis-served (Apex = software_saas, sandbox_* tenants = cross_industry or specific) |

### Operator approval checklist (1j)

- [ ] DDL reviewed (cross_industry sentinel constraint accepted)
- [ ] 16-row seed reviewed against DEC-af8247 §2
- [ ] Display names + descriptions reviewed
- [ ] Rollback verified
- [ ] Approved for execution: _yes / no_

---

## 5. DBCP-2a — `contract.mc_envelope_audit_record`

### Purpose

Per-MC envelope audit ledger for MC Envelope Governance (DEC-889238). Records dedup decisions, supersession choices, override rationales, follow-up task UIDs. Sibling of `contract.certification_record` (DBCP-1c) which serves SDA primitive certification.

### Forward DDL

```sql
CREATE TABLE contract.mc_envelope_audit_record (
  mc_envelope_audit_record_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- The MC envelope this record concerns (poly-ref; no FK constraint at DB level — service-layer enforced)
  metric_contract_id           UUID NOT NULL,
  metric_contract_version_code TEXT,                              -- nullable; some actions are envelope-level not version-level

  -- Action taken
  action_code                  TEXT NOT NULL,                     -- 'dedup_check' | 'dedup_block' | 'dedup_override' | 'supersede' | 'survivor_override'
  fingerprint_signature        TEXT,                              -- the canonical 6-tuple signature when action involves dedup; nullable for non-dedup actions

  -- Dedup/supersession linkage
  related_mc_id                UUID,                              -- the duplicate-pair counterpart or supersession survivor
  supersedes_mc_id             UUID,                              -- when action='supersede', the predecessor (non-survivor)
  survivor_mc_id               UUID,                              -- when action='supersede', the survivor

  -- Override (only when action ends in '_override')
  override_rationale_text      TEXT,                              -- ≥40 chars per D366 when present
  override_followup_task_uid   TEXT,                              -- auto-spawned task UID per D366

  -- Operator identity
  operator_sub                 TEXT NOT NULL,                     -- Cognito sub
  operator_role_at_action      TEXT NOT NULL,                     -- snapshot of role at action time
  operator_email               TEXT,                              -- optional convenience

  -- Timestamps
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

### Rollback

```sql
DROP INDEX IF EXISTS contract.idx_mc_envelope_audit_finger;
DROP INDEX IF EXISTS contract.idx_mc_envelope_audit_action;
DROP INDEX IF EXISTS contract.idx_mc_envelope_audit_op;
DROP INDEX IF EXISTS contract.idx_mc_envelope_audit_mc;
DROP TABLE IF EXISTS contract.mc_envelope_audit_record;
```

Safe — new table, no existing data.

### Preflight queries

```sql
-- Confirm table doesn't already exist
SELECT to_regclass('contract.mc_envelope_audit_record');
-- expect NULL pre-execution

-- Confirm contract schema exists
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'contract';
-- expect 1 row

-- Confirm metric_contract table exists (poly-ref target — no DB FK but service uses it)
SELECT to_regclass('metric.metric_contract');
-- expect non-NULL
```

### Idempotence

Not idempotent — single-shot per the pattern.

### Risk

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Poly-ref to `metric_contract_id` without DB FK | Low | Low | Service-layer enforcement; same pattern as `certification_record.primitive_id` (DBCP-1c); orphan rows recoverable via audit |
| Action code enum changes | Low | Low | New `action_code` values require CHECK update + ADR amendment to DEC-889238 |
| JSONB drift on supersession metadata | n/a | n/a | No JSONB columns; all fields are TEXT/UUID/timestamp |
| Append-only convention violated by future code | Low | High | Code review; hardening DBCP (revoke UPDATE/DELETE at role level) deferred to a future hardening pass, same pattern as certification_record |

### Operator approval checklist (2a)

- [ ] DDL reviewed (3 CHECK constraints: action_code enum, override-pair, supersede-pair)
- [ ] Append-only convention accepted (no DB-level UPDATE/DELETE prevention in this DBCP)
- [ ] Rollback verified
- [ ] Approved for execution: _yes / no_

---

## 6. DBCP-1c — `contract.certification_record`

(Verbatim from prior draft `2026-05-12-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md` §DBCP-1c. No changes.)

### Purpose

Per-primitive audit ledger for certification acts. Persists gate results, AI verdicts, certifier identity, role-at-action-time, override rationale + follow-up task UID, and timestamps. Required for any certification act through the SDA's `/certify` / `/return-to-author` / `/deprecate` / `/withdraw` endpoints. Sibling of `mc_envelope_audit_record` (DBCP-2a).

### Forward DDL

(See prior draft for the full 16-column schema with three CHECK constraints + 3 indexes. Not duplicated here to keep the bundle scannable; **the prior draft text is part of this packet by reference.**)

### Operator approval checklist (1c)

- [ ] Schema reviewed (column set per DDL above)
- [ ] CHECK constraints reviewed (override-pair, primitive-type enum, action-code enum)
- [ ] JSONB shapes accepted (`gate_results_json`, `advisory_verdicts_json`)
- [ ] Append-only convention accepted; hardening deferred
- [ ] Approved for execution: _yes / no_

---

## 7. DBCP-1f — `contract.primitive_provenance`

(Verbatim from prior draft `2026-05-12-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md` §DBCP-1f. No changes.)

### Purpose

Central append-only provenance ledger across BF / BO / CF. Each row records that a primitive was registered with a given `(source_standard, standard_ref)` at a given time by a given certifier. Required for G4 (provenance presence). Existing per-primitive `source_standard` / `standard_ref` columns on the primitive tables are **retained** as a current-projection convenience.

### Forward DDL

(See prior draft for the full 9-column schema with three CHECK constraints + 2 indexes. **The prior draft text is part of this packet by reference.**)

### Operator approval checklist (1f)

- [ ] Schema reviewed (9 columns)
- [ ] CHECK constraint pairing (`standard_ref` required when external standard) verified
- [ ] Retain-existing-columns strategy accepted
- [ ] Approved for execution: _yes / no_

---

## 8. Aggregate risk + sequencing summary

### Cross-DBCP risk

| Risk | Mitigation |
|---|---|
| Order-dependency within tranche | None — all 5 are additive, independently rollbackable. Recommended order (1a→1j→1c→1f→2a) is human-readability only |
| Application code expects new tables before they exist | SDA-1 gates module (already authored, 74/74 tests green) is pure-function and **does not require** any of these tables to exist for unit tests. Service-layer code (SDA-2, SDA-3, MCE-7) is gated by these DBCPs landing — that work begins post-execution |
| Re-execution / idempotence | DBCPs are single-shot. Rollback + re-execute is the supported re-run pattern. Each rollback is `DROP TABLE IF EXISTS` |
| Tranche 2 / 3 dependencies | Tranche 2 (DBCP-1b) and Tranche 3 (1g/1h/1i) depend on Tranche 1 landing. Their packets are separate operator-approval sessions |

### Total schema delta after Tranche 1 executes

- **New tables:** 5 (`master.semantic_family`, `master.industry`, `contract.certification_record`, `contract.primitive_provenance`, `contract.mc_envelope_audit_record`)
- **Altered tables:** 0
- **New indexes:** 11
- **New CHECK constraints:** 12
- **Rows added:** seed rows for `master.semantic_family` (§3) and `master.industry` (§4); both are the listed enums
- **Existing rows touched:** 0

### What this packet does NOT do

- No `draft → proposed` migration (DBCP-1d, deferred)
- No `primitive_supersession` table (DBCP-1e, deferred)
- No `status_code` CHECK broaden (DBCP-1b, Tranche 2)
- No `business_field.semantic_family` column (DBCP-1g, Tranche 3)
- No `tenant.industries` or compat-mode columns (DBCP-1h, Tranche 3)
- No `metric_definition.applicable_industries` column (DBCP-1i, Tranche 3)
- No service code changes (Phase 1 service work runs post-execution)
- No SDA endpoint changes
- No bc-admin UI changes
- No tenant or runtime touch

## 9. Operator's next step

Review §3 (1a), §4 (1j), §5 (2a), §6 (1c by reference), §7 (1f by reference). Decide:

1. **Bundle approval mode:** approve as a single packet (recommended for efficiency) OR approve each DBCP individually (acceptable per the filing-plan answer).
2. **Findings F1, F2, F3:** accept the framings (semantic_family seed is the listed enum, not a count; industry seed includes the `cross_industry` sentinel + the specific industries listed in DEC-af8247 §2; M4-M6 already in 1a). No semantic changes; prose-only.
3. **Execution timing:** approve for execution at a later named session, or defer with rationale.

**No DDL is executed until each approved DBCP is re-presented in a session with explicit "execute now" approval per the Database Change Protocol.** This packet is the draft text only.

## 10. References

- **DEC-a17d0f** (D403) — SDA umbrella ADR. Phase 1 substrate.
- **DEC-b7affa** (D404) — G11 amendment. G5 extension to BFs requires DBCP-1a + DBCP-1g.
- **DEC-889238** (D405) — MC Envelope Governance. Names DBCP-2a (this packet).
- **DEC-af8247** (D406) — Cross-domain scope. Names DBCP-1j (this packet) + 1h/1i (Tranche 3).
- **DEC-804874** (D366) — semantic_family closed enum source.
- **Phase 1 DBCP drafts** (prior MWR): `2026-05-12-phase1-dbcp-drafts-1a-1b-1c-1f-SES-594568.md` — original 1a/1b/1c/1f drafts. 1c and 1f are referenced by §6/§7 of this packet.
- **Matrix-review (M4-M6)**: `2026-05-12-c1-matrix-review-against-apex-SES-594568.md` — refinements to 1a compatible-type matrix.
- **SDA-1 implementation**: `bc-core/src/registry/semantic-definitions/gates.ts` + `gates.spec.ts` — pure-function gates module, 74/74 tests green, exercises the same 23-value enum and M4-M6 compatibility matrix this packet seeds.
