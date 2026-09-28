---
title: MLS-24/G1 for the Kaveri journal-entry KPI — evidence closeout (2026-09-28)
description: Read-only evidence that the 2026-09-27 total_journal_entries proof meets the MLS-24/G1 development criterion (tenant-readiness-program §2 row 24), with the residuals and the MLS-substrate disclosure.
status: closed
authority: implementation-checkpoint
date: 2026-09-28
project: bc-docs-v3
domain: tenant-readiness
subdomain: mls-24
focus: g1-evidence-closeout
governing_adr: DEC-09fb2f
related_adrs: [DEC-48d222, DEC-33d436, DEC-c9e623, DEC-e7b7b3]
---

# MLS-24/G1 for the Kaveri journal-entry KPI — evidence closeout (2026-09-28)

**Claim.** For Kaveri's `total_journal_entries`, FY2026-27/P05 (value 212), MLS-24 is met **at G1 in development**, per the criterion in [`tenant-readiness-program.md`](../../../../implementation/tenant-readiness-program.md) §2 row 24. The claim is structural, identity and scope proof only. **Content-hash integrity is not established** (TSK-105345). This is not D575 complete and not a production proof.

**Subject.** Snapshot `1d570b5f-e330-8a20-8a13-d7296f43993d` in `fact.ms_total_journal_entries_v1_0_0` ← evaluation `e960533f-0716-88c1-ba40-fd66006e7a1b` (run `ef3eafac-25f7-4a66-8611-9c763e65ee64`, 2026-09-27T09:39:55Z, the live 7d window, barecount-devhub `artifacts/serve-move/live/record/2026-09-27T093745Z-7d/`) ← proof evidence `adbbcf4c-6589-80e8-85d7-5b9aa3f2d447` (`metric_evaluation_proof:e960533f…`, `e6b.lineage.v2`).

**Where it ran.** Live Mac cluster, system identifier `7689410286420172840`, tenant DB `tbc_kaveri_dev`. Served bc-core `:3100` = `_wt/freeze-e` @ `d5530d6c` (contains the v2 writer and projection, bc-core #836 `e6b79566`). Every query ran inside `BEGIN READ ONLY … ROLLBACK`; nothing was written.

## 1. The criterion, condition by condition

| Criterion (§2 row 24) | Result | Evidence |
|---|---|---|
| MetricProofProjection returns `qualified` for the 7d snapshot | **qualified**, all 24 checks `passed` (tenant, D_status, ID-1…ID-4, singletons, K3…K9, K10 a/c/d/e, scope MC/period/LE/calendar, receipt) | `projection-output.json` (first object), produced by `project-proof.cjs`: the served build's own compiled `dist/evidence/metric-proof-projection.js` with a read-only psql executor. Expected scope from the governed declaration: MC `c5ebf6d5…` v1.0.0, `FY2026-27/P05`, `KAVERI-IN`, `IN-APR-MAR-MONTHLY`. |
| The check can go red | expecting period `FY2026-27/P04` → `out_of_scope` (`scope_period failed`) | `projection-negative-period.json`, `project-proof-neg.cjs` |
| (i) exactly one `metric_evaluated` Evidence and one `evaluated_by` Lineage for the evaluation | `evidence_singleton` and `lineage_singleton` passed; ids recomputed from the evaluation (ID-1…ID-4) | projection checks. Atomicity with the snapshot is D578's code guarantee in the governed persistence adapter; these reads show only that all rows exist and share the transaction timestamp. |
| (ii) the tenant pool authenticates as `bc_tenant_runtime`; no owner variable in the served environment | served process env: `DATABASE_URL` user `bc_platform_runtime`, `TENANT_DATABASE_URL` user `bc_tenant_runtime`; `TENANT_OWNER_DATABASE_URL` **absent** (names only; no values read). Live sessions: `tbc_kaveri_dev` → `bc_tenant_runtime`, `bc_platform_dev` → `bc_platform_runtime`. The proof's own `identityReceipt`: sessionUser = currentUser = `bc_tenant_runtime`, not superuser, no RLS bypass. | observed 2026-09-28 ~03:20Z; receipt in `evidence_object.metadata_json` (receipt check `passed`) |
| (iii) `evidence.*` refuses UPDATE / DELETE / TRUNCATE for that identity, which cannot disable or bypass the guard | gate G-c (runtime privilege matrix), G-d (no UPDATE/DELETE/TRUNCATE/TRIGGER/REFERENCES on `evidence.*`; six `prevent_mutation` triggers present, enabled, pinned), G-e (no role memberships) all return zero rows | `u3-gate-20260928T031159Z-95347.txt` |
| The switch gate held at the switch and at proof time | **at the switch:** live window `2026-09-27T073808Z` (W6-U5a serve move to the runtime logins), step A2 "tenant gate G-a..G-g GREEN" at 07:38:34Z, before the 09:39:55Z evaluation. **At proof time:** the same pinned tool (`u3-gate.sh live`, `SQL-PINS.sha256` all OK) → "U3 GATE GREEN (1 tenant DB(s): kaveri; G-a..G-g zero rows)", 2026-09-28T03:11:59Z; direct sessions are exactly `bc_tenant_runtime` / `bc_tenant_owner`, not superuser | barecount-devhub `artifacts/serve-move/live/record/2026-09-27T073808Z/`; `u3-gate-20260928T031159Z-95347.txt` (sha256 `d8387a82…`) |
| Only exact ID-4 qualifies | the KPI is scalar (no grain columns); ID-4 `passed` | projection checks |

The earlier proof for the same period, snapshot `11e78abf…` (evaluation `9e57b668…`, 2026-09-23, `e6b.lineage.v1`), projects **`unqualified_legacy`**: it carries no scope and no identity receipt. It stays unqualified and does not count.

## 2. Residuals (disclosed on the claim)

- **R-1**, in the operator's words "the served process keeps the platform superuser credential". Observed 2026-09-28: the served platform URL user is `bc_platform_runtime`. R-1 stays disclosed until W6-P (TSK-1a240c) verifies it and closes it; this note does not close it.
- **R-2**, the served AWS principal and OS user can retrieve owner material (W6-P).
- **R-3 (new, umbrella ruling 2026-09-28)**, the per-transaction tenant seam (W6-U5b, `withTenantTx`, TSK-ab7809) is not built. G1 rests on the served login and the receipt, not on a per-unit-of-work identity assertion. U5b is hardening and is not required for G1.
- **Writer attribution** is application-emitted (the receipt); the evidence tables have no writer column and connection/statement logging is off (TSK-8a9186).
- **G2** (capability absence, W6-P) is a production-readiness item and is not claimed.

## 3. Disclosed fact: tenant rungs are called from evidence, not from the MLS substrate

`metric.mls_state_event` (the D392 MLS substrate, DEC-e7b7b3) holds rows only for **MLS-13 and MLS-14** (2026-09-28, read-only: 1,656 + 1,674 rows, writers `MlsBackfillService` and `ContractActivationService`). It holds **no row for any tenant rung, MLS-15 to MLS-25**. The trigger bindings for MLS-21/22/23 exist, but no emitter calls the recorder (the per-emitter migration TSK-1f9c3b stopped at 2 of 8). The MLS-24 binding still names the retired `evidence_proof_status_set` event.

Therefore **MLS 21–25 for Kaveri are called from evidence** (this note, the 7d window record, and the program SSOT §3.0), not from substrate rows. The bc-admin Metric Lifecycle funnel will **under-report tenant rungs** until the substrate is wired. Nobody should read that funnel as the truth for tenants. Wiring the tenant rungs (emitters or probe bindings, including the MLS-24 binding swap) is a separate, later unit.

## 4. Files

| File | What |
|---|---|
| `project-proof.cjs` | read-only runner for the served projection (both 7d-period snapshots) |
| `project-proof-neg.cjs` | the same, expecting the wrong period (negative control) |
| `projection-output.json` | projections of snapshots `1d570b5f…` (qualified) and `11e78abf…` (unqualified_legacy) |
| `projection-negative-period.json` | negative control → `out_of_scope` |
| `u3-gate-20260928T031159Z-95347.txt` | proof-time gate transcript |
| `MANIFEST.sha256` | sha256 of the five files above |

Reproduce: from a host with the served checkout at `/Users/anant/MyProjects/_wt/freeze-e` and the `bc-postgres` container, run `node project-proof.cjs 1d570b5f-e330-8a20-8a13-d7296f43993d 11e78abf-2178-816c-89de-fb1194f446d6`; the gate is barecount-devhub `artifacts/w6-u3-tenant-convergence/tools/u3-gate.sh live`.

Session SES-f70e69 (research), arc plan PLN-c96901, umbrella rulings of 2026-09-28 (record against the existing proof, no re-run; U5b not required for G1).
