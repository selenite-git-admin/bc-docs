---
id: evaluation-evidence-dbcp-application
order: 33.5
title: "Evaluation-Evidence DBCP Application (E6-B singleton index, Invariant VI)"
status: authoritative
authority: authoritative
depends_on: [operations-overview, evidence-and-lineage, metric-evaluation, tenant-lifecycle-and-subscription, upgrade-and-migration]
governing_adrs:
  - DEC-48d222 (D578 — E6-B first-class atomic metric-evaluation Evidence + Lineage; Invariant VI at the finalization boundary)
  - DEC-ebb3cd (D-2 — evidence/lineage governed-persistence contract)
---

# Evaluation-Evidence DBCP Application — existing-tenant singleton index (E6-B, Invariant VI)

> **This runbook APPLIES NOTHING by being read.** Every step below requires explicit operator
> authorization bound to the exact DBCP-SHA + tenant-scope recorded in §7. Nothing here is
> auto-implied by the merge of the E6-B code (PR #704 `b8cd6dfe`): the emit is dormant behind a
> runtime control and the DBCP is unapplied until the separate gated acts are authorized.

## 1. Identity (pin these exactly)

| Artifact | Path (bc-core) | SHA-256 |
|---|---|---|
| **APPLY** | `docker/redesign/migrations/20260819-d578-e6b-eval-proof-lineage-singleton-existing-tenants.sql` | `50e7383f97d5857b826ce625b1a3f04d6fa402ea169c972fddc1a4c2b9cb6c4b` |
| **REVERT** | `…-singleton-existing-tenants.revert.sql` | `e3c7166b523987334e4c5865ddd9165d6a6658d316dca7287a81121f4903d096` |
| **Dry-run evidence** | `…-singleton-validation.txt` (fail-closed proof on throwaway DB `tbc_e6bdbcp_*`) | on main |
| **Code provenance** | `bc-core#704` merged `b8cd6dfe` (reviewed head `a20215136…`, Codex ACCEPTED-WITH-BOUNDARY `5016335069`) | — |

**What it does:** creates two UNIQUE partial indexes enforcing the E6-B singletons on an existing
tenant DB — `uq_evidence_object__metric_eval_proof_subject` (one `metric_evaluated` proof per
subject) and `uq_lineage_object__evaluated_by_target` (one `evaluated_by` lineage per target).
Built with `CREATE INDEX CONCURRENTLY` (non-blocking). **Idempotent** (clean re-run → exit 0) and
**fail-closed** (§5).

**Scope:** per existing tenant DB `tbc_<slug>_<env>`, applied one tenant at a time, each under its
own recorded authorization. New tenants receive the surface from the base tenant DDL
(`03-tenant-db.sql`) at provision time; this runbook is only for tenants that predate E6-B.

## 2. Preconditions (ALL must hold before any apply)

1. **PR #704 merged to `main`** — satisfied (`b8cd6dfe`).
2. **Auditor-store HEALTHY** — `ledger_verify_integrity` available, not `DEGRADED /
   AUDIT_STORE_STARTUP_FAILED`. Verify immediately before apply; abort if degraded.
3. **Target tenant list identified and frozen** for this authorization.
4. **Explicit operator authorization recorded** (§7), bound to APPLY-SHA `50e7383f…` and the exact
   tenant-scope. Authorization for one tenant/batch does NOT extend to others (per-action,
   per-scope).
5. **Backup / PITR restore point** confirmed for each target tenant DB (index creation is additive
   and revertible, but capture the restore point regardless).

## 3. Pre-apply dry-run against a COPY of the REAL target (mandatory)

The `validation.txt` on the branch proves fail-closed behaviour on a *synthetic* clean tenant. That
is not sufficient — a real tenant may already carry a same-named index of a different shape. So, per
tenant:

1. Clone the target tenant schema into a throwaway DB (schema + index catalog; data optional — the
   guard reads `pg_index`/`pg_class`, not rows).
2. Run the APPLY against the clone with `psql -v ON_ERROR_STOP=1`.
3. **Expected: exit 0**, and both indexes report `indisvalid=true indisready=true`.
4. **If exit 3** → the tenant hits a §5 fail-closed case. STOP that tenant; resolve per §5 on the
   clone first; only then schedule the real apply. Do NOT proceed to the real DB on a nonzero
   dry-run (pre-apply execution-disposition gate: dry-run vs the REAL target first).
5. Drop the throwaway DB (zero-residue).

## 4. Apply (per authorized tenant)

1. Re-verify §2.2 (auditor-store healthy) — abort if it flipped to degraded.
2. `psql -v ON_ERROR_STOP=1 -d tbc_<slug>_<env> -f <APPLY.sql>` (tee the output; capture the psql
   exit code). `CREATE INDEX CONCURRENTLY` does not take a blocking lock.
3. **Expected psql exit: 0.**
4. Confirm the DBCP is recorded in `infrastructure.schema_migration_event` with the APPLY-SHA and
   tenant.

## 5. Fail-closed cases (do NOT force past them)

| psql exit | Message contains | Meaning | Action |
|---|---|---|---|
| 3 | `already exists with a DIFFERENT shape … Refusing` (A1/A2) | A same-named index of the wrong shape exists (non-unique, or missing the partial predicate) — it does NOT enforce the singleton | Investigate + resolve the conflicting index deliberately (it may mask a real data problem), then re-run |
| 3 | `exists but is INVALID/NOT-READY (interrupted CONCURRENTLY build)` (B1/B2) | A prior `CONCURRENTLY` build was interrupted; the index is a dead remnant | Run the paired **REVERT** (`DROP INDEX CONCURRENTLY`) as recovery, then re-run the APPLY (validated: re-run-after-recovery → exit 0) |

The guard reads the live `pg_index` shape, so it cannot be satisfied by a hash-identical name — only
by a correctly-shaped unique partial index.

## 6. Verification (per tenant, after exit 0)

1. Both indexes: `SELECT indisvalid, indisready FROM pg_index …` → `true, true` for
   `uq_evidence_object__metric_eval_proof_subject` and `uq_lineage_object__evaluated_by_target`.
2. **Index-surface parity**: run the E6-B parity check against the applied tenant
   (`bc-core: src/tenant-management/tenant-baseline-e6b-index-parity.integration.spec.ts` /
   `src/database/schema/tenant-e6b-index-surface-parity.spec.ts`) — the tenant surface must match the
   base-DDL declared surface exactly.
3. Confirm zero throwaway/dry-run DBs remain (zero-residue).

## 7. Authorization (operator completes per tenant/batch — REQUIRED before §4)

```
APPLY-SHA authorized : 50e7383f97d5857b826ce625b1a3f04d6fa402ea169c972fddc1a4c2b9cb6c4b
Tenant-scope         : <tbc_<slug>_<env>, … — exact list>
Auditor-store health : <verified HEALTHY at <ts>>
Authorized by        : <operator> at <ts>
```

## 8. Rollback

`psql -v ON_ERROR_STOP=1 -d tbc_<slug>_<env> -f <REVERT.sql>` (`DROP INDEX CONCURRENTLY`, SHA
`e3c7166b…`). **Rollback removes the singleton enforcement** — run it only (a) as the §5 B1/B2
recovery, or (b) if E6-B is being deliberately withdrawn on that tenant. Not part of a normal apply.

## 9. Out of scope of this runbook (each a separate gated operator act)

- **Deployment / live-enable** of the emit (the runtime control that starts writing the proof
  Evidence + Lineage). This DBCP only prepares the index surface; it does not turn the emit on.
- **FND-VI closure** (Invariant VI declared live).

Applying this DBCP with the emit still disabled is safe: the indexes sit unused until live-enable.
