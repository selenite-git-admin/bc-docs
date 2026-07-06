---
title: D446 CEE v0 — chain_enrichment_plan substrate DBCP
status: applied
date: 2026-06-16
authority: DEC-739e23 / D446
project: bc-core
domain: platform
subdomain: chain-engines
focus: substrate
---

# D446 CEE v0 — `mcf.chain_enrichment_plan` substrate DBCP

## Authority
- **ADR**: [DEC-739e23 / D446](../../../governance/adrs/ADR-739e23.md) — Chain Enrichment Engine v0
- **Sibling**: [DEC-1fa08f / D445](../../../governance/adrs/ADR-1fa08f.md) — Chain Audit Service v0 (shipped)
- **Operator authorization**: SES-40eefa, 2026-06-16

## Scope

Single new table, new indexes only. **No mutation of any existing substrate.**

| What | Direction |
|---|---|
| `mcf.chain_enrichment_plan` (new) | CREATE TABLE |
| `mcf.idx_cep_mode_target` (new) | CREATE INDEX |
| `mcf.idx_cep_packet_hash` (new) | CREATE INDEX |
| `mcf.idx_cep_status` (new) | CREATE INDEX |
| `contract.*` | none |
| `concept_registry.*` | none |
| `mcf.metric_*` | none |
| `mcf.seed_metric` | none |
| `mcf.chain_audit_evidence` | none |

## Files

| File | Purpose |
|---|---|
| `docker/redesign/migrations/d446-cee-v0-plan-substrate.sql` | Apply |
| `docker/redesign/migrations/d446-cee-v0-plan-substrate-rollback.sql` | Rollback |
| `src/database/schema/mcf/chain-enrichment-plan.ts` | Drizzle schema |
| `src/database/schema/mcf/index.ts` | Barrel export |

## Column inventory

| Column | Type | Null | Constraints |
|---|---|---|---|
| `plan_uid` | `uuid` | NOT NULL | PK |
| `mode_code` | `text` | NOT NULL | CHECK IN (`source_contract_gap_plan`) |
| `target_kind_code` | `text` | NOT NULL | CHECK IN (`source_contract_gap_plan`) |
| `target_ref_json` | `jsonb` | NOT NULL | — |
| `status_code` | `text` | NOT NULL | CHECK IN (`sc_gap_satisfied`, `sc_create_proposed`, `blocked_out_of_scope`, `blocked_input_invalid`) |
| `plan_json` | `jsonb` | NOT NULL | DEFAULT `'{}'::jsonb` |
| `emitted_packet_json` | `jsonb` | NULL | — |
| `emitted_packet_hash` | `text` | NULL | CHECK `~ '^sha256:[0-9a-f]{64}$'` |
| `planner_version` | `text` | NOT NULL | DEFAULT `'cee-v0'` |
| `evidence_json` | `jsonb` | NOT NULL | DEFAULT `'{}'::jsonb` |
| `created_by_sub` | `text` | NOT NULL | — |
| `created_at` | `timestamptz` | NOT NULL | DEFAULT `now()` |

## Index inventory

| Index | Columns | Predicate |
|---|---|---|
| `idx_cep_mode_target` | `(mode_code, target_kind_code, created_at DESC)` | — |
| `idx_cep_packet_hash` | `(emitted_packet_hash)` | `WHERE emitted_packet_hash IS NOT NULL` |
| `idx_cep_status` | `(status_code, created_at DESC)` | — |

## Status code semantics

| Status | Meaning | Packet emitted? |
|---|---|---|
| `sc_gap_satisfied` | Target SC already exists in `contract.source_contract`. No packet needed. | No |
| `sc_create_proposed` | Target SC missing; CEE has emitted a harness v1.1-compatible `sc.create_draft` packet. Operator runs harness to apply. | Yes |
| `blocked_out_of_scope` | SC gap satisfied OR resolvable, but the next gap (AC/OC/CC/metric chain) is out of D446 v0 scope. Plan documents the next gap but emits no packet. | No |
| `blocked_input_invalid` | `target_ref_json` could not be resolved to a recognizable source-system specimen. | No |

## Hard rules

1. **Idempotent apply**: DDL uses `CREATE TABLE IF NOT EXISTS` + `CREATE INDEX IF NOT EXISTS`. Re-running yields a no-op.
2. **No writes to existing substrate** — verified by file scan: zero `INSERT` / `UPDATE` / `DELETE` / `ALTER TABLE` against any pre-existing table.
3. **Append-only at the table level** — D446 §Rule 4: CEE plan rows are immutable. No `UPDATE` or `DELETE` ever issued by the service. Hand-edit only under separate emergency DBCP.
4. **Rollback is destructive but unambiguous** — `DROP TABLE IF EXISTS` + `DROP INDEX IF EXISTS`. Safe when the table is empty.
5. **No special privileges**: applies as the standard `barecount` app role. No new DB role required (CEE writes through the same connection pool that owns `mcf.*`).

## Apply procedure (local)

```bash
# from bc-core repo root
docker exec -i <postgres-container> psql -U barecount -d bc_platform_dev \
  -v ON_ERROR_STOP=1 \
  < docker/redesign/migrations/d446-cee-v0-plan-substrate.sql
```

Expected output ends with `COMMIT`.

## Post-apply verification

```sql
-- row count
SELECT COUNT(*) FROM mcf.chain_enrichment_plan;       -- expect 0

-- indexes
SELECT indexname FROM pg_indexes
WHERE schemaname='mcf' AND tablename='chain_enrichment_plan'
ORDER BY indexname;
-- expect: chain_enrichment_plan_pkey, idx_cep_mode_target, idx_cep_packet_hash, idx_cep_status

-- check constraints
SELECT conname FROM pg_constraint
WHERE conrelid = 'mcf.chain_enrichment_plan'::regclass
  AND contype = 'c'
ORDER BY conname;
-- expect: chain_enrichment_plan_mode_code_check,
--         chain_enrichment_plan_target_kind_code_check,
--         chain_enrichment_plan_status_code_check,
--         chain_enrichment_plan_emitted_packet_hash_check
```

## Rollback procedure (local)

```bash
docker exec -i <postgres-container> psql -U barecount -d bc_platform_dev \
  -v ON_ERROR_STOP=1 \
  < docker/redesign/migrations/d446-cee-v0-plan-substrate-rollback.sql
```

## Cross-references
- Author authority and audit-first loop: [ADR-739e23](../../../governance/adrs/ADR-739e23.md)
- Sibling CAS DBCP (already applied): `docker/redesign/migrations/d445-cas-v0-evidence-substrate.sql`
- D162 / D163 database rules: snake_case naming, FK constraints, soft-delete via `archived_at` not enforced here (immutable plan rows; no delete path), ≤20 columns, indexes match query patterns ✅
