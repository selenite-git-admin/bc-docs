---
title: D445 CAS v0 Evidence Substrate — DBCP
status: proposed
date: 2026-06-16
project: bc-core
domain: governance
subdomain: chain-engines
focus: schema
session: SES-18e856
authority: DEC-1fa08f (D445)
---

# D445 CAS v0 Evidence Substrate — DBCP

## Authority
- **DEC-1fa08f / D445** — Chain Audit Service (decided 2026-06-16)
- Design packet: `bc-docs-v3/docs/implementation/chain-engines-design-packet-2026-06-15.md`

## Scope

Creates the audit-evidence substrate for CAS v0. **Read-only with respect to all business substrate (MC, MCV, MVB, MFC, MCDR, BC, BCV, CC, OC, certification_record, PE-MC results).**

### Tables created
1. `mcf.chain_audit_evidence` — per-audit-run evidence row (verdict + per-check findings + substrate snapshot hash)

### Roles created (best-effort in local dev)
1. `chain_auditor_readonly` — SELECT on all relevant schemas + INSERT only on `mcf.chain_audit_evidence`

### Triggers created (best-effort in local dev)
1. `trg_cae_role_check` BEFORE INSERT — rejects inserts unless `current_user = 'chain_auditor_readonly'` (belt-and-suspenders)

### Out of scope
- No DROP/ALTER on any existing business-substrate table
- No data migration
- No write to existing `certification_record` table
- No changes to PE-MC, M14, or chain_status tables

## Verdict model (v0)

Per operator authorization, v0 uses `PASS | FAIL | OPERATOR_REVIEW | NOT_APPLICABLE` verdict codes (NOT the `green/yellow/red` originally drafted in D445 ADR body). Future amendment to D445 text will reconcile.

## Pre-apply gates

1. Read-only baseline counts:
   - `SELECT COUNT(*) FROM mcf.metric_contract_version` — must be unchanged after apply
   - `SELECT COUNT(*) FROM mcf.certification_record` — must be unchanged
   - No table named `mcf.chain_audit_evidence` exists yet
   - No role named `chain_auditor_readonly` exists yet

2. DB connection: `postgresql://barecount:barecount_dev@localhost:5435/bc_platform_dev`

## Migration

File: `bc-core/docker/redesign/migrations/d445-cas-v0-evidence-substrate.sql`

Rollback: `bc-core/docker/redesign/migrations/d445-cas-v0-evidence-substrate-rollback.sql`

### Hard rules
- Idempotent (`CREATE TABLE IF NOT EXISTS`, `CREATE ROLE IF NOT EXISTS` patterns)
- Best-effort role + trigger creation: if local DB user lacks CREATE ROLE privilege, the DDL completes WITHOUT the role + trigger, and CAS service falls back to application-layer guard (documented in service)
- All CHECK constraints inline at CREATE TABLE time
- No `ALTER TABLE` post-create

## Post-apply verification

1. `SELECT COUNT(*) FROM mcf.chain_audit_evidence` → 0 (no rows yet)
2. `SELECT * FROM information_schema.tables WHERE table_schema='mcf' AND table_name='chain_audit_evidence'` → 1 row
3. `SELECT rolname FROM pg_roles WHERE rolname='chain_auditor_readonly'` → 0 or 1 row (depending on privilege)
4. `SELECT tgname FROM pg_trigger WHERE tgname='trg_cae_role_check'` → 0 or 1 row
5. Business substrate unchanged: counts on `mcf.metric_contract_version`, `mcf.certification_record`, `mcf.metric_publication_eligibility_result` unchanged

## Rollback strategy

Atomic: `DROP TABLE IF EXISTS mcf.chain_audit_evidence CASCADE; DROP ROLE IF EXISTS chain_auditor_readonly;`

## Risk

- **DB privilege blocked:** if local dev user can't create roles, migration completes without role + trigger; CAS falls back to app-layer guard (still safe). Reported in apply log.
- **Trigger ambiguity:** the role check `current_user = 'chain_auditor_readonly'` may fire against legitimate test inserts if tests use the wrong connection. Tests use Drizzle mocks; no live INSERT in unit tests.
