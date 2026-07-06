---
uid: DEC-d5fb43
title: "Contract Version Format — Semver, Release Notes, Tenant Notifications"
description: "Single semver format (MAJOR.MINOR.PATCH) enforced in DB and JSON. Release notes per version bump. Tenant notifications triggered by severity."
status: implemented
subdomain: governance
focus: lifecycle
date: 2026-04-02
project: bc-docs
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---

# D256: Contract Version Format — Semver, Release Notes, Tenant Notifications

## Context

Contract versions are tracked in three places, none consistent:

| Location | Current Value | Problem |
|----------|--------------|---------|
| DB `version_code` column | `v1` | Freeform text, no CHECK constraint, no semver |
| `contract_json.version` (top-level) | `1.0.0` | Semver but not enforced at DB level |
| `contract_json.header.version` | `null` | Not populated — dead field |

All 6 contract family `_version` tables use `version_code text NOT NULL` with no format constraint. The JSON Schema `$defs/semver` validates `^\d+\.\d+\.\d+$` but only inside the JSON body — the DB column accepts anything.

There is no mechanism for release notes, no record of what changed between versions, and no way to notify tenants when a contract they're bound to changes.

## Decision

### 1. Single Version Format: `MAJOR.MINOR.PATCH`

Every contract version has exactly one version identifier, stored in two places that must always agree:

| Location | Value | Example |
|----------|-------|---------|
| `version_code` (DB column) | `MAJOR.MINOR.PATCH` | `1.0.0` |
| `contract_json.version` (top-level JSON key) | Same value | `1.0.0` |

**Eliminated:** `contract_json.header.version` — redundant with top-level `version`. Remove from all contract instances and meta-schemas.

**DB enforcement** — add CHECK constraint to all `_version` tables:

```sql
ALTER TABLE contract.{family}_contract_version
  ADD CONSTRAINT chk_{family}_version_semver
  CHECK (version_code ~ '^\d+\.\d+\.\d+$');
```

Applied to: `source_contract_version`, `admission_contract_version`, `observation_contract_version`, `canonical_contract_version`, `metric_contract_version`, `intervention_contract_version`, plus `canonical_mapping_version` and approval tables.

### 2. Semver Semantics for Contracts

| Bump | Meaning | Examples |
|------|---------|---------|
| **MAJOR** | Breaking shape change | New required body key, removed key, changed type, field_selection contraction, grain change |
| **MINOR** | Additive/non-breaking change | New optional key, new enum value, field_selection expansion, threshold adjustment |
| **PATCH** | Metadata correction | Description fix, display_name change, tag update, typo |

**First version** of every contract is `1.0.0`. No `0.x.x` versions — contracts are governed artifacts, not experiments.

### 3. Release Notes

Every version bump records a release note. New table:

```sql
CREATE TABLE contract.contract_release_note (
  release_note_id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_family    text NOT NULL,        -- 'source', 'admission', etc.
  contract_name      text NOT NULL,        -- e.g., 'mc_dso_days'
  from_version_code  text,                 -- NULL for initial version
  to_version_code    text NOT NULL,
  change_type        text NOT NULL CHECK (change_type IN ('major', 'minor', 'patch')),
  release_note_text  text NOT NULL,        -- What changed and why
  breaking_changes   text[],               -- List of breaking changes (MAJOR only)
  migration_guide    text,                 -- How to adapt (MAJOR only)
  created_by_name    text,
  created_at         timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_release_note__family_contract
  ON contract.contract_release_note(contract_family, contract_name, to_version_code);
```

**Release note is mandatory** — the API rejects version creation without a release note. Even `1.0.0` (initial) has a note: "Initial version."

### 4. Tenant Notification Triggers

When a contract version is created, the system checks which tenants are bound via `tenant.contract_binding` and triggers notifications based on change severity:

| Change Type | Notification | Channel | Tenant Action Required |
|-------------|-------------|---------|----------------------|
| **MAJOR** | Immediate alert | In-app notification + email | Review breaking changes, may need to update override or re-bind |
| **MINOR** | Informational | In-app notification | No action required, review at convenience |
| **PATCH** | Silent | Activity log only | None |

Notification record stored in `infrastructure.notification`:

```sql
INSERT INTO infrastructure.notification (
  notification_id, tenant_id, category_code, title_text, body_text,
  severity_code, source_entity, source_id, created_at
) VALUES (
  gen_random_uuid(), :tenant_id, 'contract_update',
  'Contract Update: mc_dso_days v2.0.0',
  'Breaking change to metric contract mc_dso_days. Review migration guide.',
  'warning',  -- 'info' for minor
  'contract_release_note', :release_note_id,
  now()
);
```

### 5. Migration Plan (Existing Data)

All 733 existing contract versions (46 CC + 687 MC) currently use `version_code = 'v1'`. Migration:

1. `UPDATE` all `version_code` from `'v1'` to `'1.0.0'`
2. `UPDATE` all `contract_json.version` to ensure it matches `'1.0.0'`
3. Add CHECK constraints
4. Insert initial release notes for all existing versions

SC/AC/OC/IC have no instances yet — they will be seeded with `1.0.0` from the start.

## Impact

| Artifact | Change |
|----------|--------|
| DDL (`02-platform-tables.sql`) | CHECK constraint on all `_version` tables, new `contract_release_note` table |
| Meta-schemas (all 6 families) | Remove `header.version`, keep only top-level `version` |
| Contract validation service | Enforce version_code = contract_json.version match |
| Contract API (`POST /contracts/:id/versions`) | Require release_note in request body |
| Notification service | Trigger tenant notifications on version creation |
| bc-admin | Show release notes in contract version history |
| bc-portal | Show notifications for contract updates |
| Existing data | Migrate `v1` → `1.0.0` for 733 contract versions |

## References

- D253 (DEC-bef347) — Structural completeness (all keys required)
- D233 — Three-level governance (version is per-instance)
- D164 — Platform-only (tenant notifications go to bound tenants only)
- D018 (DEC-24b4ec) — Contract Registry (6 contract families)
