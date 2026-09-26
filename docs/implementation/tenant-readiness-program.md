---
title: Tenant Readiness — Program (SSOT)
status: drafting
date: 2026-09-26
anchor_task: TSK-d73f01
governing_adrs: >
  DEC-33d436/D606 (program mandate + platform/tenant readiness split — tenant readiness
  = MLS 15-25 / lane L10, the downstream milestone); DEC-c9e623/D389 (Metric Lifecycle
  States — the 25-rung ladder, Platform 01-14 / Tenant 15-25, and the MLS-14→15 handoff);
  DEC-a67bae/D590 (locked lanes — L10 is the platform→tenant boundary lane); DEC-958d3a/D613
  (the single continuous real run was reclassified out of platform readiness INTO this program);
  DEC-f02230/D368 (tenant DB schema organization — locates the tenant fiscal-calendar config);
  DEC-f44a71/D617 (program EXECUTION & sequencing — the Kaveri walk + route (a) for the MLS-23
  gate; the readiness DEFINITION stays in DEC-33d436, not re-decided here);
  DEC-ea4523/D623 (source-agnostic fiscal periods per legal entity — the Kaveri fiscal and
  identity work logged in §8 from 2026-09-24).
related: >
  Umbrella roadmap: DevHub plan PLN-31c4a1 (v18, 2026-09-26) — its MLS 15-25 table is the
  coordinator's view; this document is the evidenced record.
  Platform Readiness & Legibility (implementation/platform-readiness-program.md, TSK-4b2404) —
  the parent program; its platform half (MLS 01-14 / L1-L9) CLOSED 2026-09-21.
  Platform DB Foundation (overview/platform-db-foundation.md, TSK-cc348a) — the converging
  program that productionizes L10 tenant onboarding + fact-table provisioning (MLS-20) at scale.
  Tenant onboarding SOP: onboarding/tenant-onboarding.md; tenant-metric-binding.md.
---

# Tenant Readiness — Program (SSOT)

> Leads with the **destination**, then the **spine** (the MLS 15-25 ladder) that must render it,
> then **where each rung stands** against live substrate, then the **critical path** and the
> **sequencing** of the Kaveri walk. Read top-down. A unit of work that can't be tied to a rung
> and to the distance-to-destination is drift.

> ## Status — DRAFTING (stood up 2026-09-21, SES-b5c14b)
> This is the **tenant half** of Platform Readiness & Legibility (DEC-33d436/D606). The platform
> half (MLS 01-14 / lanes L1-L9 + engine conformance) is **CLOSED** (2026-09-21). Tenant readiness
> picks up at the **MLS-14→15 handoff gate** and runs the ladder for one real tenant.
>
> **Update 2026-09-26 (SES-d55c25):** §3 now opens with the current state of each rung, re-checked
> read-only against the live databases (queries in §3.1 E–F). §5 opens with the current critical
> path, and §8 logs the walk from 2026-09-23 to 2026-09-26. In short: Kaveri has real source rows,
> canonical rows and **one accepted snapshot**, but for the metric `total_journal_entries`, not yet
> for DSO, which stays the destination. Resolving the canonical contract that produced those rows
> was shown on a clone to throw since 2026-09-26T00:54Z (open regression **TSK-387779**). The date
> is an inference from reading the code; no live resolution was attempted. One E6-B evidence row
> and one lineage row exist for the snapshot. Source reports say they were written by the superuser,
> over `*`-calendar COs, and whether they were written atomically is not proven, so MLS-24 is **not** met. The portal KPI (MLS-25) has not
> started.

## 1. The destination

**Tenant readiness is proven when one real tenant walks the full object progression on a real
source and ends in a trusted, evidenced KPI.** Concretely, for **Kaveri Precision Components** on
the **lc5 Odoo** world (`:8100`, `v3_lc5`, ~10,744 `account.move` — row count is source-reported,
not independently reproduced here): provision the tenant, wire the Odoo source, bind and activate a
metric (**DSO**, via `account.move → journal_entry → DSO`), admit real observations, resolve them to
canonical, evaluate the metric to a **real snapshot**, emit **evidence**, and render the **KPI in
bc-portal** — end-to-end, fail-closed, no fixture.

This is the single continuous **real** run that DEC-958d3a/D613 reclassified out of platform
readiness (which is provable compositionally on a fixture) **into this program** — because the
run is inseparable from the interlocked governed onboarding stack (cert-gated MC activation +
CC-activation provisioning fanout + owner-worker fact-table DDL). Proven once, governed.

## 2. The spine — Metric Lifecycle States 15-25 (verified)

The authoritative structure is the tenant half of the MLS ladder (DEC-c9e623/D389). It is **not**
a new invention: the ladder is locked, substrate-backed, and already rendered in bc-admin as the
**Metric Lifecycle → Tenant tab** (MLS-19…25 funnel).

**Two axes, not to be conflated:** the **MLS ladder** (01-25; Platform 01-14 / Tenant 15-25) is
the lifecycle axis; the **authoring runway lanes** (L1-L10, DEC-a67bae/D590) are the
artifact-family axis. **L10 = Tenant Onboarding** is the single lane that spans the boundary; the
tenant lifecycle rungs MLS 15-25 are executed **through** L10.

**The handoff gate is MLS-14 → MLS-15:** a tenant MC cannot enter MLS-15 until its Platform MLS-14
row is `'active'`. This is the gate that makes "platform activation" mean something to the tenant.

| MLS | State | Ground-truth signal (per DEC-c9e623 D-2, reconciled to current locators) |
|-----|-------|------------------------------------------|
| **15** | Tenant exists / active | `tenant.tenants` (active) + tenant DB `tbc_{slug}_dev` provisioned |
| **16** | Tenant fiscal calendar | tenant-DB `organization.fiscal_calendar_config` per legal_entity (ADR-f02230/D368; **reconciles** the D389 `tenant.fiscal_calendar_config` vocabulary — the config lives in the tenant DB, not a platform table) |
| **17** | Tenant connector instance | tenant credentials/endpoint for the source system |
| **18** | Tenant reader configured | reader flavor bound to connector instance with execution config |
| **19** | Contract bindings recorded | `tenant.contract_binding` pins active SC/AC/OC/CC/MC versions |
| **20** | Tenant fact tables exist | `fact.so_*/co_*/ms_*` per binding (schema-provisioner reconciled) |
| **21** | SO produced | reader execution → `progression.admission` + `fact.so_*` |
| **22** | CO produced | canonical evaluation → `progression.canonical_evaluation` + `fact.co_*` |
| **23** | Metric snapshot produced | metric evaluation → `progression.metric_evaluation` + `metric_snapshot_index` + `fact.ms_*` |
| **24** | **MLS-24/G1 (dev connection-plane)** — the development criterion; never called "complete" | Selected by the operator directly to Codex on 2026-09-26 (Codex's preserved copy: `OPERATOR-DISPOSITION-Codex-gen-bdb784-D575-2026-09-26.md`, bc-external-audit commit `e51c368d`), on the design Codex accepted in RESPONSE-Codex-gen-bdb784-07 (barecount-devhub#35 @ `f80a47ac`). **Scope:** a Kaveri dev-host tenant only. It says nothing about production and does not mean D575 is complete. **Met when** the MetricProofProjection returns `qualified` for a 7d snapshot, **and** the switch gate held both at the switch and at proof time. That means: (i) exactly one `metric_evaluated` Evidence (subject `metric_evaluation_proof:<metric_evaluation_id>`) and exactly one `evaluated_by` Lineage, written in the snapshot's own transaction (DEC-48d222/D578, decided: "no proof, no record"); (ii) **the designated tenant pool authenticates as `bc_tenant_runtime`, and the owner variable is absent from the served environment**; (iii) `evidence.*` refuses UPDATE, DELETE and TRUNCATE for that identity, and it cannot disable or bypass the guard. **Proof strength:** structural, identity and scope proof; content-hash integrity not established (TSK-105345). Only exact ID-4 qualifies (Kaveri's KPI is scalar); a non-text grain cannot qualify. **Residuals, disclosed on this row:** **R-1**, in the operator's words "the served process keeps the platform superuser credential": the served platform URL is the cluster superuser and can reach the tenant, and only the code path is barred. **R-2**, the served AWS principal and OS user can retrieve owner material. **G2** (capability absence, W6-P / TSK-1a240c) is a production-readiness item and is not required for this proof. **Consumers:** MLS-25 may proceed on MLS-24/G1. No consumer may read it as D575 complete or as a production proof. *History:* the D389 signal "D387 `proof_status='complete'`" is retired for metrics. D578 reduced `proof_status` to a marker for WORM-archive completeness only, and the column exists in neither database (§3.1 H). |
| **25** | KPI rendered in bc-portal | snapshot index + typed value row + tenant binding/permission pass |

## 3. Readiness matrix — grounded against live substrate

### 3.0 Current state for Kaveri (re-grounded 2026-09-26T07:17Z)

Each cell is tagged with its evidence type. **RO** (reproducible read-only) means one of the
`BEGIN READ ONLY` queries in **§3.1 E** (platform, `bc_platform_dev`) or **§3.1 F** (tenant,
`tbc_kaveri_dev`) shows it; they were run at 2026-09-26T07:17Z. **SR** (source-reported) means it
rests on a named closure file, Codex response or change record and was not re-run here. Where
Codex accepted a closure after its own read-only check, the cell says so; that corroborates the
claim but does not make it RO. The PLN-31c4a1 v18 MLS table agrees with every row except where
the cell says otherwise.

| MLS | Kaveri state | What the evidence shows | What remains |
|-----|--------------|-------------------------|--------------|
| 15 Tenant | 🟢 infrastructure | RO: `tenant.tenants` `kaveri` active, `schema_name='tbc_kaveri'` (base name; the connection layer adds `_dev`, CHG-bfed75); `tbc_kaveri_dev` exists; 1 `onboarding_record` | The per-metric acceptance described in footnote ¹ has not been recorded for any metric. v18 marks this rung ✓. |
| 16 Fiscal calendar | 🟢 | RO: `organization.fiscal_calendar_config` has 2 active rows: `*` → `IN-APR-MAR-MONTHLY` (created 2026-09-23) and `KAVERI-IN` → `IN-APR-MAR-MONTHLY` from 2023-04-01 (created 2026-09-25T09:47Z). `tenant_dim.dim_legal_entity` has 1 row, `KAVERI-IN` (IN, INR). SR: created by D623 step 3, successor-4 (RESPONSE-Codex-d617-055, closure accepted after Codex's own read-only check) | — |
| 17 Connection | 🟢 | RO: `runtime.connection kaveri-odoo-v3lc5` is `connected` and now carries `tenant_id` = Kaveri (it was NULL on 2026-09-21), `environment_code='development'`. SR: owner assigned by step 3 A2 (d617-055). Odoo is reached through the loopback relay to the laptop (PLN-31c4a1 v18). | Odoo's move to the Mac (W5) comes later. |
| 18 Reader | 🟢 | RO: observation contract `45f8b60c…` has **1.2.0 and 1.3.0 both `active`**. SR: step 5 created 1.3.0 (adds `company_id` and 6 fields) and moved Kaveri's `account.move` reader binding to 1.3.0 (d617-059, accepted) | Supersede OC 1.2.0 (planned in D623 7c-c) |
| 19 Bindings | 🟡 | RO: `tenant.tenant_binding` has SC `019fe42b-7f2b…` 1.0.0, env `dev`, from 2026-09-23. `tenant.contract_binding` has 5 active `canonical` rows: cc-dh5d9 **1.2.0, 1.4.0, 1.5.0**, plus cc-das36 1.0.0 and cc-7174p 1.0.0. The rows for 1.2.0 and 1.4.0 are still `is_active=true` although both versions are `superseded`; this document does not establish whether that is intended. Intent is to be established before 7c-c re-binds, and only through the governed path (**TSK-5f24ee**). | Bind cc-dh5d9 **1.6.0** (RO: `approved`, created 2026-09-26T05:41Z, not active). The activation fan-out that writes these rows does nothing in the served build (TSK-231594, fix bc-core#830 open). |
| 20 Fact tables | 🟡 | RO: `fact.so_sc_929yc_v1_0_0`, `fact.co_cc_dh5d9_v1_4_0`, `fact.co_cc_dh5d9_v1_5_0`, `fact.co_cc_das36_v1_0_0`, `fact.co_cc_7174p_v1_0_0` and `fact.ms_total_journal_entries_v1_0_0` exist. `fact.co_cc_dh5d9_v1_6_0` does **not** exist. The tenant ledger `admin.schema_migration_event` shows 0001, 0002 (2026-09-25T06:38Z) and **0003 (2026-09-26T07:02:15Z)** applied. | Provision the 1.6.0 tables (7c-c) |
| 21 SO | 🟢 (for 1.5.0) | RO: `progression.admission` has **25,744** rows, all `account.move`, SC 1.0.0, `admitted`, in 4 runs on 2026-09-23 (5,000 + 5,000 + 5,000 + 10,744). `fact.so_sc_929yc_v1_0_0` has **10,744** rows, one per Odoo move. The 25,744 therefore counts admission attempts across runs, not distinct moves. | Observe again under OC 1.3.0 and the per-entity identity (7d) |
| 22 CO | ⚠ **regressed** | RO: `progression.canonical_evaluation` has 10,744 `accepted` rows for 1.4.0 and 10,744 for 1.5.0 (all 2026-09-23). `fact.co_cc_dh5d9_v1_5_0` has 10,744 rows, none with an empty `fiscal_period`. They were stamped before the `KAVERI-IN` calendar row existed (09-23 vs 09-25), so they used the `*` row. SR: resolving **active cc-dh5d9 1.5.0 throws** since D623 7c-a minted concept `115b2945` (2026-09-26T00:54Z). Shown on a clone, not observed on live (7cc-design README F1; gen-e90cd0-01). **TSK-387779.** | ADR bc-docs#67 → 7c-c (activate 1.6.0) → 7d (resolve again with correct legal entities) |
| 23 Snapshot | ⚠ wrong metric so far | RO: 1 `progression.metric_evaluation`, `accepted`, 2026-09-23T07:52Z, for metric contract `c5ebf6d5…`. That is **`total_journal_entries`**: the snapshot table is `fact.ms_total_journal_entries_v1_0_0`, and CHG-12f4fd (SR) names MC `c5ebf6d5` / MCV `b8d2a132`, which is RO active with chain `green`. The snapshot `fact.ms_total_journal_entries_v1_0_0` = **212** for FY2026-27/P05, and 212 COs in 1.5.0 carry that period. 3 `metric_run` rows: deferred, failed, completed. **DSO has not been evaluated.** RO: `days_sales_outstanding` chain verdict is `red` (`bindings_resolve: fail:1_unresolved`), and its leaf `gross_invoiced_amount` is still `audit_pending`. | Prove again over COs with correct legal entities (7d). The destination stays DSO (§1, §5.0); this snapshot is the pilot slice only. |
| 24 Proof (G1) | 🟡 emitted once, does not count | **Condition (a) is not proven; only its row shape is.** RO: exactly one `evidence.evidence_object` of type **`metric_evaluated`** (subject `metric_evaluation_proof:9e57b668…`, `e6b.lineage.v1`) and exactly one `evaluated_by` `lineage_object` exist, carrying the same `created_at` (07:52:37.861569Z) as the metric evaluation and the snapshot row. This is the first observed E6-B emit. Surviving rows and equal timestamps show neither membership in one transaction nor that a failed proof write would have rolled the snapshot back; that atomicity is D578's **requirement**, not something these reads prove. The other 4 evidence objects are run records, and the other 25,744 lineage rows are `observed_as` rows from admission. The snapshot row's own `evidence_hash` column is empty. Condition (b) **not met** (SR, not established by the reads): `TENANT_DATABASE_URL` in bc-core's `.env` on the Mac names `barecount`, and the W6 design (barecount-devhub PR #35, §0 and §1.1: the `.env` URL user, the dev secret carries no DB keys, and the live serve script does not override it) reports that the emit, and the served `:3100` in general, log in as the superuser. The rows do not record the role, and no live session was connected to observe. RO for what is already built for D575 (§3.1 G/H): `evidence_object`, `evidence_record` and `lineage_object` in `tbc_kaveri_dev` each carry `no_update` and `no_delete` triggers and belong to `bc_tenant_owner` (not a superuser); role `bc_tenant_runtime` exists (not a superuser) and holds only SELECT and INSERT on them, with no UPDATE, DELETE, TRUNCATE or TRIGGER (§3.1 I). TRUNCATE is refused by privilege, not by the triggers; the six `fact.*` tables belong to `barecount` (a superuser). | **D575 rollout**, the step never taken (SR, W6): serve `:3100` as `bc_tenant_runtime`, reassign the superuser-owned `fact.*`, then observe again in 7d under that identity over COs with correct legal entities (TSK-d43263; W6 sequence U4 → U3 → U5 → 7d). D575 itself is still `proposed`, and is not moved to decided here; see §5.0. *Criterion status (2026-09-26): G1 connection-plane criterion selected by the operator; not yet shown on the served system; G2/D575 incomplete.* |
| 25 KPI in portal | ❓ | Never verified | Verify at the end |

**Served bc-core** (SR): `:3100` runs `9d0dc5aa` (manifest `b749315f`). The move script stopped at
its "move" step (exit 1), but Codex accepted the served state it intended after its own read-only
check (RESPONSE-Codex-gen-6f1e89-04). The fixes waiting to be served together (TSK-4636d8):
bc-core#829 (merged `37dfe3c1`), #830 (open), #831 (draft), and the 7c-c identity change
(PR-B, pending ADR bc-docs#67, draft).

**A further blocker ahead of 7d** (RO for the schema, SR for the code): `progression.canonical_evaluation`
in `tbc_kaveri_dev` has **no** `binding_mechanism_code` column. TSK-da545b reports that the bc-core
resolver writes that column for binding-realized COs, so every such write would fail.

### 3.0.1 Baseline for Kaveri (2026-09-21, historical)

Grounded read-only against `bc_platform_dev` (and, for tenant-DB relations, `tbc_probe_unit4_dev`)
this session; the exact queries, outputs, observation time and source-commit pins are recorded in
**§3.1**. **Two distinct questions per rung:** *(a) is the rung green for Kaveri?* and *(b) is the
machinery to build it present?* At grounding time Kaveri was not onboarded, so **every rung was 🔴
for Kaveri** — the honest baseline. (**Update — see §3.1:** MLS-15 has since been provisioned this
session; the matrix below preserves the grounding-time baseline and calls that change out
explicitly.) The machinery column is what matters for sequencing.

Boundary key: **P** = platform DB (`bc_platform_dev`) · **T** = tenant DB (`tbc_{slug}_dev`).
RAG = Kaveri state at grounding time. Machinery = buildability.

| MLS | Bnd | Kaveri | Machinery (grounded) | Owner |
|-----|-----|--------|----------------------|-------|
| 15 Tenant exists | P | 🔴¹ | 🟢 governed `POST /tenants` + provisioning; at grounding **only `probe_unit4` existed; `onboarding_record`=0**. Kaveri **infrastructure** since provisioned (¹) — this is *not* accepted per-metric MLS-15 | Platform |
| 16 Fiscal calendar | T | 🔴 | 🟢 **machinery present** — `organization.fiscal_calendar_config` in the **tenant DB** (ADR-f02230/D368): Drizzle schema + `FiscalCalendarService` tenant lookup + tenant-skeleton DDL at bc-core `53bb1115`; the relation **exists (0 rows) in `tbc_probe_unit4_dev`**. Remaining = author Kaveri's **config rows**, not build the table | Platform |
| 17 Connector instance | P | 🔴 | 🟢 `runtime.connector` **`odoo-ent-v19` (Odoo 19 Enterprise, source=`odoo`) available** | Platform |
| 18 Reader configured | P | 🔴 | 🟢 3 `odoo` reader flavors active — **1 fully wired (connector+connection FK IDs both set), 2 unwired**. A pair of non-null IDs is a wiring *pointer*, not an end-to-end wiring *test* | Platform |
| 19 Contract bindings | P | 🔴 | 🟡 `tenant.contract_binding`=0; **as-built binding path EXISTS** — `schema-provisioner` `POST onboard-connector`/`onboard-metric` (202 + worker-readiness poll; MCF reverse-walk in `MetricOnboardingService`; `nightly-reconcile` **removed**) at bc-core `53bb1115`. **Per-rung gate completeness + tenant probes still UNVERIFIED** | Platform |
| 20 Fact tables | T | 🔴 | 🟡 owner-privileged fact DDL via **provisioning-worker-cli** (needs `TENANT_OWNER_DATABASE_URL`; NOT in served process) | Engineering |
| 21 SO produced | T | 🔴 | 🟡 `progression.admission` path exists; **tenant probe MLS-21 existence UNVERIFIED** (F-MLS-1) | Engineering |
| 22 CO produced | T | 🔴 | 🟡 `progression.canonical_evaluation` exists; **probe MLS-22 UNVERIFIED** | Engineering |
| 23 Snapshot produced | T | 🔴 | 🔴 **⛔ metric-layer blocker VERIFIED (2026-09-21):** composite leaf **`gross_invoiced_amount` `audit_pending`/`is_current=false`** (`8a38e79c`) → loader (selects `is_current=true`+`active`) finds no active/current upstream. Necessary candidate repair = certify+activate the leaf (corpus cert, held); sufficiency + downstream chain **unverified**. MLS-21/22/23 tenant probes **reported absent** (F-TR-2 code-inventory, pending independent confirm). See ADR-f44a71 Amendment 1 | Engineering |
| 24 Proof complete | T | 🔴 | 🟡 evidence path exists (E6-B armed); **gated by non-superuser runtime identity + evidence immutability** (TSK-d43263 / D575) | Engineering *(2026-09-26: since emitted once, as the superuser over `*`-calendar COs, so it does not count; see §3.0.)* |
| 25 KPI rendered | T | 🔴 | ❓ bc-portal render path — verify at the end (permission/typed-value) | Platform |

¹ **MLS-15 — infrastructure provisioned; per-metric acceptance PENDING (this session, 2026-09-21T05:00Z).**
Kaveri tenant **infrastructure** was provisioned via the governed `POST /tenants` (HTTP 201):
`tenantId f0a5e695-b475-472c-87f8-71609be1a8c3`, `tbc_kaveri_dev`, `active`, 26 tables, D575
`immutabilityVerified=true`, onboarding journey `activated`. **This is execution acceptance of
infrastructure, NOT the accepted per-metric MLS-15 rung.** Per §2 (the MLS-14→15 handoff gate) and
ADR-f44a71 Decision 3, entering the metric-lifecycle MLS-15 for a metric requires that metric's (DSO)
**verified MLS-14** first — calling a governed service does not itself establish it. The cell
therefore stays 🔴 (per-metric MLS-15 pending); it will re-ground to 🟢 **only** once the chosen-metric
MLS-14 proof, the applicable accepted preflight/DBCP + consent, and the hash-bound execution
pre/post-state closure are supplied — items **not yet supplied** (explicitly pending, not fabricated).
Governed execution/custody reconciliation for this write: **CHG-a538a5** (authorization = the operator
session instruction; missing gates enumerated). No green readiness is asserted here.

**Findings surfaced by grounding (observations, inferences and unverified paths kept separate):**
- **F-TR-1 (MLS-16) — CORRECTED:** the D389 signal name `tenant.fiscal_calendar_config` (a platform
  table) does **not** exist, but that is a **vocabulary/locator move, not missing machinery**. Per
  ADR-f02230/D368 the config lives in the **tenant DB** as `organization.fiscal_calendar_config`;
  the Drizzle schema, `FiscalCalendarService` tenant lookup and tenant-skeleton DDL are present at
  bc-core `53bb1115`, and the relation exists (0 rows) in `tbc_probe_unit4_dev`. `master.dim_fiscal_calendar`
  (3 rows) is a **separate platform catalog**, not the tenant signal. The remaining work for the walk
  is authoring Kaveri's per-legal-entity config rows, not building the table. (D389 vocabulary retained
  as historical, reconciled to the current locator.)
- **F-TR-2 (MLS-19/21/22/23 probes):** the MLS-19 as-built binding path **exists** (see the matrix /
  §5). The MLS-21/22/23 **tenant probes** are **reported absent** by peer code-inventory (`mls.module.ts`
  registers only the MLS-13 + MLS-14 probes; `metric.mls_state` holds 2 rows, both MLS-14; CHG-1f065f) —
  **pending independent confirmation**, and **distinct** from "zero tenant progression rows" (a missing
  probe *class* is not the same as no data). Per-rung **gate completeness** likewise remains unverified.
- **F-TR-3 (MLS-23, the gate) — metric-layer blocker VERIFIED; sufficiency + downstream PENDING (2026-09-21; ADR-f44a71 Amendment 1):**
  re-reproduced read-only (queries in §3.1; CHG-1f065f / SES-da0550). **DSO is a composite**:
  `days_sales_outstanding` (mcv `f660fb7b`) is **`active`** (so its **MLS-14 gate is SATISFIED**), and its
  operands bind (acyclic d467) to leaves `ar_balance` (`61a876e7`, **active**) and **`gross_invoiced_amount`
  (`8a38e79c`, `audit_pending`, `is_current=false`, only extant version)**. The runtime composite loader
  selects upstream by `is_current=true` + `active`, so the gross leaf yields **no active/current upstream
  version** → DSO has no evaluable composite. **Necessary candidate repair:** certify+activate the leaf (a
  platform/MCF-corpus certification, **not tenant-isolated**), gated on cert/impact review; **held** pending
  operator approval + cert/DB-Foundation consent. **Not proven sufficient:** downstream source/admission/
  CO/OC/projection defects are **unverified** (no full leaf-chain audit), and no tenant has real COs yet, so
  admission+resolution are also still required. The prior "operand-projection gap / superseded OC-pin"
  framing is **withdrawn as unsupported** by the registry facts (a downstream OC/projection defect is not
  thereby excluded — simply unverified).

### 3.1 Reproducibility record (read-only)

Observation window **2026-09-21T04:56Z–05:00Z**. Source-commit pins: bc-core `53bb1115d9b1c4d841750cce31eb2f60f3174d76`;
databases `bc_platform_dev` and `tbc_probe_unit4_dev` on PostgreSQL 17.11. All reads ran inside a
`BEGIN READ ONLY` transaction (no writes, no builders, no provisioning at read time). The queries
below are the authoritative reproducer for the matrix baseline; an independent auditor run
(RESPONSE-Codex-d617-001) reproduced the same results.

**A. Platform baseline (`bc_platform_dev`):**

```sql
BEGIN READ ONLY;
SELECT slug, status_code FROM tenant.tenants ORDER BY slug;
SELECT datname FROM pg_database WHERE datname LIKE 'tbc_%' ORDER BY 1;
SELECT count(*) AS bindings FROM tenant.contract_binding;
SELECT count(*) AS onboarding_records FROM tenant.onboarding_record;
SELECT to_regclass('tenant.fiscal_calendar_config') AS old_fiscal_signal;   -- D389 vocabulary
SELECT count(*) AS fiscal_calendars FROM master.dim_fiscal_calendar;         -- separate platform catalog
SELECT connector_name, source_system_name, status_code
  FROM runtime.connector WHERE source_system_name='odoo';
SELECT flavor_name, status_code, connector_id IS NOT NULL AS has_connector,
       connection_id IS NOT NULL AS has_connection
  FROM runtime.reader_flavor WHERE source_system_name='odoo' ORDER BY flavor_name;
COMMIT;
```

Captured results (grounding time — pre-provisioning baseline):
- `tenant.tenants` → `probe_unit4 | active` (one row).
- `pg_database LIKE 'tbc_%'` → `tbc_probe_unit4_dev` (one row).
- `tenant.contract_binding` → **0**; `tenant.onboarding_record` → **0**.
- `to_regclass('tenant.fiscal_calendar_config')` → **NULL** (the platform table does not exist — expected; the config is tenant-DB, see B).
- `master.dim_fiscal_calendar` → **3**.
- `runtime.connector` (odoo) → `odoo-ent-v19 | odoo | available` (one row).
- `runtime.reader_flavor` (odoo) → **3** active flavors; exactly **one** has both `connector_id` and `connection_id` set.

**B. Tenant-DB fiscal relation (`tbc_probe_unit4_dev`) — evidences F-TR-1:**

```sql
BEGIN READ ONLY;
SELECT to_regclass('organization.fiscal_calendar_config') AS fiscal_config;
SELECT count(*) AS fiscal_configs FROM organization.fiscal_calendar_config;
COMMIT;
```

Captured results: `organization.fiscal_calendar_config` → **exists**; row count → **0**.

**C. MLS-15 infrastructure provisioning (this session, via governed API — a write; infrastructure
only, per-metric MLS-15 acceptance PENDING):**
`POST /api/tenants {slug:kaveri, name:'Kaveri Precision Components', expectedDbName:tbc_kaveri_dev}`
→ HTTP **201** `{tenantId:f0a5e695-b475-472c-87f8-71609be1a8c3, dbName:tbc_kaveri_dev, status:active,
tableCount:26, immutabilityVerified:true, idempotent:false}`; verified `GET /api/tenants/kaveri`
active + onboarding journey `activated`. **This establishes tenant infrastructure, not the accepted
per-metric MLS-15 rung** — that needs the chosen-metric (DSO) MLS-14 proof + applicable accepted
preflight/DBCP + consent + hash-bound execution pre/post-state closure, **not yet supplied**.
Governed execution/custody reconciliation: **CHG-a538a5**.

**D. MCF metric-state + DSO composite binding (2026-09-21, read-only `bc_platform_dev`; underwrites F-TR-3 / ADR-f44a71 Amendment 1).** Source-commit pin bc-core `53bb1115`; observation 2026-09-21. Corroborated by CHG-1f065f (SES-da0550).

```sql
-- governance state per metric (by name)
SELECT mc.mc_name, mcv.version_code, mcv.is_current, mcv.governance_state_code,
       mcv.metric_contract_version_uid
  FROM mcf.metric_contract_version mcv
  JOIN mcf.metric_contract mc ON mc.metric_contract_uid = mcv.metric_contract_uid
 WHERE mc.mc_name IN ('days_sales_outstanding','ar_balance','gross_invoiced_amount');
```

Captured results:
- `days_sales_outstanding` → v1, `is_current=true`, **`active`** (mcv `f660fb7b`).
- `ar_balance` → v1, `is_current=true`, **`active`** (mcv `61a876e7`).
- `gross_invoiced_amount` → v1, `is_current=false`, **`audit_pending`** (mcv `8a38e79c`) — only extant version.

Runtime composite selection (code, not a query): `CompositeMetricEvaluationService.loadCompositeSpec`
(`src/boundary/composite-metric-evaluation.service.ts:353`, bc-core `53bb1115`) joins each upstream
operand by `bound_metric_contract_uid` + `is_current=true` + `governance_state_code='active'` — so the
`audit_pending`/non-current gross leaf resolves to **no active/current upstream version**. This
establishes the **metric-layer** blocker only; it does **not** audit the source/admission/CO/OC/projection
chain downstream of the leaf.

**Scope of what these reads prove — and do not:** §3.1 A/B/C establish the registry/relation baseline and
machinery presence; §3.1 D establishes the MCF metric-state blocker at the metric layer. They do **not**
prove source credentials, endpoint liveness, tenant binding, gate completeness, or **end-to-end**
evaluability (leaf activation is a *necessary candidate*, not a proven-sufficient remedy); the lc5 row
count is not reproduced; the MLS-21/22/23 tenant-probe absence is peer-reported (code-inventory), pending
independent confirmation.

**E. Platform re-grounding for §3.0 (`bc_platform_dev`, 2026-09-26T07:17:30Z).** PostgreSQL 17.11,
container `bc-postgres` on the Mac, run as `docker exec -i bc-postgres psql -U barecount -d bc_platform_dev`
with the file below on stdin, inside `BEGIN READ ONLY … COMMIT`. The E and F texts exactly as printed
here were then re-run from this document (`-v ON_ERROR_STOP=1`, exit 0) and gave the same results.

```sql
BEGIN READ ONLY;
SELECT id, slug, schema_name, status_code FROM tenant.tenants ORDER BY slug;
SELECT datname FROM pg_database WHERE datname LIKE 'tbc_%' ORDER BY 1;
SELECT contract_family, contract_id, version_code, is_active
  FROM tenant.contract_binding b JOIN tenant.tenants t ON t.id = b.tenant_id
 WHERE t.slug = 'kaveri' ORDER BY contract_family, version_code;
SELECT source_contract_id, version_code, environment_code, effective_from, effective_to
  FROM tenant.tenant_binding b JOIN tenant.tenants t ON t.id = b.tenant_id WHERE t.slug = 'kaveri';
SELECT count(*) FROM tenant.onboarding_record r JOIN tenant.tenants t ON t.id = r.tenant_id
 WHERE t.slug = 'kaveri';
SELECT c.canonical_contract_name,
       (SELECT string_agg(version_code || ':' || governance_state_code, ', ' ORDER BY created_at)
          FROM contract.canonical_contract_version v
         WHERE v.canonical_contract_id = c.canonical_contract_id) AS versions
  FROM contract.canonical_contract c
 WHERE c.canonical_contract_id IN ('7fa4b84f-8ac5-4383-9d0e-2b6427c0ba1c',
       '0947b25a-f7a6-4175-89a0-11220ce07336', '8a1a1f1a-d6c6-47c3-979a-35a0660a2f91');
SELECT version_code, governance_state_code, created_at
  FROM contract.observation_contract_version
 WHERE observation_contract_id = '45f8b60c-6814-4fa9-b4e6-82ecde6da200' ORDER BY created_at;
SELECT connection_name, connection_status, tenant_id, environment_code
  FROM runtime.connection WHERE connection_name = 'kaveri-odoo-v3lc5';
SELECT mc.mc_name, mcv.version_code, mcv.is_current, mcv.governance_state_code
  FROM mcf.metric_contract_version mcv
  JOIN mcf.metric_contract mc ON mc.metric_contract_uid = mcv.metric_contract_uid
 WHERE mc.mc_name IN ('days_sales_outstanding','ar_balance','gross_invoiced_amount','total_journal_entries');
SELECT mc.mc_name, cs.verdict_code, cs.checks_json, cs.computed_at
  FROM mcf.mcv_chain_status cs
  JOIN mcf.metric_contract_version mcv ON mcv.metric_contract_version_uid = cs.metric_contract_version_uid
  JOIN mcf.metric_contract mc ON mc.metric_contract_uid = mcv.metric_contract_uid
 WHERE mc.mc_name IN ('days_sales_outstanding','total_journal_entries') AND mcv.is_current;
COMMIT;
```

Captured results:
- `tenant.tenants`: `kaveri | tbc_kaveri | active` (id `f0a5e695…`) and `probe_unit4 | tbc_probe_unit4_dev | active`. Databases: `tbc_kaveri_dev`, `tbc_probe_unit4_dev`.
- `tenant.contract_binding` (Kaveri): 5 rows, all `canonical`, all `is_active=true`: `7fa4b84f…` (cc-dh5d9) 1.2.0, 1.4.0, 1.5.0; `0947b25a…` (cc-das36) 1.0.0; `8a1a1f1a…` (cc-7174p) 1.0.0.
- `tenant.tenant_binding` (Kaveri): 1 row, SC `019fe42b-7f2b-77f1-b145-226bdbd8e031` 1.0.0, `dev`, from `2026-09-23 05:21:50Z`, open-ended. `onboarding_record`: 1.
- cc-dh5d9 versions: `1.0.0:superseded, 1.1.0:superseded, 1.2.0:superseded, 1.3.0:approved, 1.4.0:superseded, 1.5.0:active, 1.6.0:approved` (1.6.0 created `2026-09-26 05:41:23Z`). cc-das36 and cc-7174p: `1.0.0:active`.
- OC `45f8b60c…`: `1.0.0 superseded`, `1.1.0 superseded`, `1.2.0 active`, `1.3.0 active` (created `2026-09-25 11:14:31Z`).
- `kaveri-odoo-v3lc5`: `connected`, `tenant_id = f0a5e695…`, `development`.
- MCF: `days_sales_outstanding` v1 current `active` (`f660fb7b`); `ar_balance` v1 current `active`; `gross_invoiced_amount` v1 **not current, `audit_pending`**; `total_journal_entries` v1 current **`active`** (`b8d2a132`), plus a non-current `draft`.
- Chain status (computed `2026-09-24 06:11Z`): `days_sales_outstanding` **`red`** (`bindings_resolve: fail:1_unresolved`, `grain_cc_active: vacuous:derived_composition`); `total_journal_entries` **`green`**.

**F. Tenant re-grounding for §3.0 (`tbc_kaveri_dev`, 2026-09-26T07:17:47Z).** Same container and role.

```sql
BEGIN READ ONLY;
SELECT event_seq, migration_name, applied_at, review_disposition_sha256, git_ref
  FROM admin.schema_migration_event ORDER BY event_seq;
SELECT legal_entity_code, fiscal_calendar_code, is_active, effective_from, created_at
  FROM organization.fiscal_calendar_config;
SELECT legal_entity_code, display_name, country_code, currency_code FROM tenant_dim.dim_legal_entity;
SELECT source_entity_name, source_contract_version_code, status, count(*)
  FROM progression.admission GROUP BY 1, 2, 3;
SELECT run_id, count(*), min(admitted_at) FROM progression.admission GROUP BY 1 ORDER BY 3;
SELECT canonical_contract_id, contract_version_code, status, count(*), min(evaluated_at), max(evaluated_at)
  FROM progression.canonical_evaluation GROUP BY 1, 2, 3;
SELECT count(*) FROM fact.so_sc_929yc_v1_0_0;
SELECT count(*) FROM fact.co_cc_dh5d9_v1_4_0;
SELECT count(*) AS total, count(*) FILTER (WHERE fiscal_period IS NULL) AS unstamped
  FROM fact.co_cc_dh5d9_v1_5_0;
SELECT count(*) FROM fact.co_cc_dh5d9_v1_5_0 WHERE fiscal_period = 'FY2026-27/P05';
SELECT to_regclass('fact.co_cc_dh5d9_v1_6_0');
SELECT metric_contract_id, metric_version, status, evaluated_at FROM progression.metric_evaluation;
SELECT metric_contract_id, status_code, started_at FROM progression.metric_run ORDER BY started_at;
SELECT fiscal_period, metric_value, evidence_hash FROM fact.ms_total_journal_entries_v1_0_0;
SELECT count(*) FROM evidence.evidence_record;
SELECT count(*) FROM evidence.evidence_object;
SELECT count(*) FROM evidence.lineage_object;
SELECT count(*) FROM progression.admission_run_completion_hold;
SELECT count(*) FROM progression.admission_run_completion_release;
SELECT column_name FROM information_schema.columns
 WHERE table_schema = 'progression' AND table_name = 'canonical_evaluation';
COMMIT;
```

Captured results:
- Tenant ledger: seq 1 `0001_tenant_ledger` and seq 2 `0002_source_legal_entity_binding`, both applied `2026-09-25 06:38Z` from bc-db `f3735d61`; seq 3 **`0003_admission_run_completion_hold`** applied **`2026-09-26 07:02:15Z`** from bc-db `886161c4`, disposition `sha256:6f77a29d…`.
- Fiscal calendar: `* → IN-APR-MAR-MONTHLY` from 2000-01-01 (created 2026-09-23 06:41Z); `KAVERI-IN → IN-APR-MAR-MONTHLY` from 2023-04-01 (created 2026-09-25 09:47Z). Legal entity: `KAVERI-IN`, "Kaveri Precision Components Ltd", IN, INR.
- Admission: `account.move | 1.0.0 | admitted | 25,744`, in 4 runs starting 2026-09-23 06:45Z / 06:54Z / 07:03Z / 07:16Z with 5,000 / 5,000 / 5,000 / 10,744 rows.
- Canonical evaluation: cc-dh5d9 1.4.0 `accepted` 10,744 (07:31–07:33Z) and 1.5.0 `accepted` 10,744 (07:38–07:41Z), all on 2026-09-23.
- Facts: SO 10,744; CO 1.4.0 10,744; CO 1.5.0 10,744 with 0 unstamped; 212 in `FY2026-27/P05`; `fact.co_cc_dh5d9_v1_6_0` → NULL (does not exist).
- Metric: 1 evaluation, `c5ebf6d5…` v1.0.0 `accepted` at 2026-09-23 07:52:37Z. Runs: `deferred_inputs_unavailable` (07:34Z), `failed` (07:41Z), `completed` (07:52Z). Snapshot: `FY2026-27/P05 | 212 | (empty evidence_hash)`.
- Evidence: `evidence_record` 0, `evidence_object` 5, `lineage_object` 25,745 (see G for the breakdown). Completion hold / release: 0 / 0 (0003's new tables are empty).
- `progression.canonical_evaluation` columns do not include `binding_mechanism_code`.

**G. Evidence breakdown (`tbc_kaveri_dev`, added 2026-09-26 after a peer session, the W6 D575 design,
pointed out the E6-B emit; same container and role).**

```sql
BEGIN READ ONLY;
SELECT evidence_type, subject_ref, created_at FROM evidence.evidence_object ORDER BY created_at;
SELECT relationship_type, left(to_object_ref, 20) AS to_prefix, count(*), min(created_at), max(created_at)
  FROM evidence.lineage_object GROUP BY 1, 2 ORDER BY 4;
SELECT r.rolname, r.rolsuper, n.nspname, c.relname
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace JOIN pg_roles r ON r.oid = c.relowner
 WHERE n.nspname IN ('evidence', 'fact') AND c.relkind = 'r' ORDER BY 4;
COMMIT;
```

Captured results:
- Evidence objects, all dated 2026-09-23:
  - `canonical_resolution_run` for 1.4.0 at 07:33:04Z and for 1.5.0 at 07:41:39Z;
  - `metric_evaluation_run` for the deferred run at 07:34:30Z;
  - **`metric_evaluated`** with subject `metric_evaluation_proof:9e57b668…` at **07:52:37.861569Z**, the same timestamp as the metric evaluation and the snapshot row;
  - `metric_evaluation_run` for the completed run at 07:52:38Z.
- Lineage: 25,744 `observed_as` rows to admissions, written 06:45Z–07:16Z, plus exactly **1** `evaluated_by` row to `metric_evaluation:9e…` at 07:52:37.861569Z.
- Owners: `evidence.evidence_object`, `evidence_record` and `lineage_object` belong to `bc_tenant_owner` (`rolsuper=f`). Every `fact.*` table belongs to `barecount` (`rolsuper=t`).

**H. MLS-24 signal and D575 substrate (both databases, 2026-09-26; same container and role).** Run once
against `bc_platform_dev` and once against `tbc_kaveri_dev`.

```sql
BEGIN READ ONLY;
SELECT current_database(), count(*) AS proof_status_columns
  FROM information_schema.columns WHERE column_name = 'proof_status';
SELECT usename, application_name, count(*)
  FROM pg_stat_activity WHERE datname = 'tbc_kaveri_dev' AND pid <> pg_backend_pid() GROUP BY 1, 2;
SELECT rolname, rolsuper FROM pg_roles WHERE rolname IN ('barecount','bc_tenant_runtime','bc_tenant_owner');
SELECT n.nspname, c.relname, t.tgname FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid
  JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'evidence' AND NOT t.tgisinternal;
COMMIT;
```

Captured results:
- `proof_status` columns: **0** in `bc_platform_dev` and **0** in `tbc_kaveri_dev`.
- No other session was connected to `tbc_kaveri_dev`, so the served build's login role could not be observed.
- Roles: `barecount` is a superuser; `bc_tenant_owner` and `bc_tenant_runtime` are not.
- `tbc_kaveri_dev` evidence triggers: `trg_{evidence_object,evidence_record,lineage_object}_no_{update,delete}` (6 triggers). There are none in `bc_platform_dev`, as expected.

**I. Privileges of the runtime identity on the evidence tables (`tbc_kaveri_dev`, 2026-09-26).**

```sql
BEGIN READ ONLY;
SELECT c.relname, p.priv, has_table_privilege('bc_tenant_runtime', 'evidence.' || c.relname, p.priv) AS granted
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
  CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('TRIGGER')) p(priv)
 WHERE n.nspname = 'evidence' AND c.relkind = 'r' ORDER BY 1, 2;
COMMIT;
```

Captured result: for each of `evidence_object`, `evidence_record` and `lineage_object`, SELECT and INSERT
are granted; UPDATE, DELETE, TRUNCATE and TRIGGER are **not**.

**What E–I do not prove:** they show stored state only. They do not show that a resolution or
evaluation would succeed today (see the MLS-22 regression). They do not show the lc5 source row
count, the served build, or live Odoo connectivity, and they do not replay any of the governed
writes in §8.

## 4. Scope boundary — what tenant readiness owns

- **Owns:** the MLS 15-25 walk for one real tenant (Kaveri) through lane L10 — provisioning →
  source wiring → binding → the runtime object progression → evidence → KPI.
- **Does NOT own (upstream, closed):** the platform engine (MLS 01-14 / L1-L9) — proven and closed
  under the parent program. If a defect is at MLS ≤14, it is a platform-readiness regression, not a
  tenant-readiness gap.
- **Converges with (not owned):** Platform DB Foundation (TSK-cc348a) productionizes L10
  provisioning + MLS-20 fact-table creation **at scale**; this program consumes its verified
  `POST /tenants` contract and the deferred W2 items (tenant SoT + upgrade path, onboarding-record
  through the spine, "Free" package seed, `tenant_infrastructure` population, readiness projection,
  the PR #41 F3 target-preview contract). Coordination acknowledgement re-affirmed 2026-09-21 — cited
  as **DEC-568d0b/D615 (publication/acceptance PENDING**: that record is **not present in this docs
  tree**, so it is referenced as pending authority, not an accepted immutable record).
- **Deferred flows (held, not built):** BYO-DB, BC-Agent, AWS-Separate; AWS-Shared tier only in v1.

## 5. Critical path & blockers

### 5.0 Current critical path (2026-09-26, from PLN-31c4a1 v18, checked against §3.0)

1. **Accept the identity ADR** DEC-7a8cbc/D626, "binding-realized issuer identity" (amends DEC-a57eb8;
   bc-docs#67, draft, proposed). Codex's gen-e90cd0-01 asked for this amendment before the 7c-c code
   change (PR-B) can be accepted. Then **PR-B**, **bc-core#830** (DI fix, TSK-231594) and **#831**
   (worker exit) merge.
2. **One combined move of the served build** (TSK-4636d8), rehearsed on a clone, including proof that
   activation queues its provisioning work.
3. **D623 7c-c:** activate cc-dh5d9 1.6.0, provision it, and supersede CC 1.5.0 and OC 1.2.0
   (TSK-e75f1d). This is what clears the MLS-22 regression (TSK-387779).
4. **Held-tail release proof** on Kaveri (TSK-080294). The 0003 substrate is live, but the release
   path has not been exercised end-to-end.
5. **D623 7d:** observe again and resolve to COs with the correct legal entity. First fix TSK-da545b
   (the resolver writes a column the tenant schema lacks).
6. **Prove MLS-22 and MLS-23 again** over those COs.
7. **MLS-24/G1:** the D575 rollout for development (TSK-d43263). The operator selected the G1
   development criterion on 2026-09-26 (§2). G2 is a production-readiness item, off this path.
   - The evidence triggers and the non-superuser role already exist on Kaveri (§3.1 H).
   - Never done yet: serving as `bc_tenant_runtime` and reassigning the superuser-owned `fact.*`.
   - The W6 design (barecount-devhub PR #35 @ `f80a47ac`) was accepted with boundary on gen-bdb784-07.
     Codex's boundary: design acceptance is not D575 complete, and nothing is implemented yet.
   - DEC-09fb2f/D575 is still `proposed` (since 2026-08-17, beyond the 30-day limit in DEC-623f8f
     rule 4). Moving it to `decided` needs the operator's decision on record. Codex's preserved
     operator record for gen-bdb784 covers the MLS-24/G1 criterion and the probe-tenant retirement,
     but not the ADR status, so the status is unchanged here.
8. **MLS-25:** the portal KPI.

**The destination stays DSO.** This is already governed text: §1 of this document, and
DEC-f44a71/D617 (decided), which names "a trusted, evidenced DSO KPI in bc-portal via account.move →
journal_entry → DSO". No record changes it; changing it would need a new ADR.
`total_journal_entries` is the **pilot slice**. It is **intended** to prove the machinery end-to-end
on Kaveri (per-legal-entity fiscal periods, the D575 identity, atomic evidence), and it has **not yet**
done so: its one snapshot used the `*` calendar, and its writer is reported to be the superuser
(§3.0). **DSO is the destination proof.** Classing `total_journal_entries` as a pilot slice is the
umbrella coordinator's ruling (2026-09-26). It is not a governed decision, and it does not alter D617. DSO's
chain is still `red` (§3.1 E), and the 2026-09-21 grain mismatch (the MLS-19 root cause in §8) has no
recorded resolution yet. Grounding it on Kaveri is a new workstream, **W9 = TSK-ad23c1**, a read-only
design unit. Tenant readiness is therefore proven only when steps 1–8 above hold for DSO, not only for
the pilot slice.

### 5.1 Critical path as written on 2026-09-21 (historical)

The buildable-now rungs are **MLS-15/17/18** (tenant provisioning + Odoo connector/reader — the
machinery exists). The path then narrows:

1. **MLS-16** — author Kaveri's tenant-DB `organization.fiscal_calendar_config` rows (machinery
   present per F-TR-1; this is configuration, not a build). No platform-schema change is implied.
2. **MLS-19** — the as-built binding path **exists** (`schema-provisioner` `onboard-connector`/
   `onboard-metric`, 202 + worker-readiness poll, MCF reverse-walk; `MetricChainReverseWalkService`
   deliberately does **not** write an MCF UID into the legacy metric binding). **Prerequisite:**
   correct the stale `onboarding/tenant-metric-binding.md` SOP (it still mandates the removed
   `nightly-reconcile` endpoint and a direct-UPDATE rollback) to the as-built route before driving the
   rung. Then bind Kaveri's SC/AC/OC/CC/MC; per-rung gate completeness/probes remain to verify.
3. **MLS-20** — run the owner-privileged provisioning worker (out-of-process) to create `fact.*`.
4. **MLS-21→22** — admit lc5 `account.move`, resolve to `journal_entry` canonical.
5. **MLS-23 ⛔** — **the gate. Route (a), corrected (DEC-f44a71/D617 Amendment 1; verified 2026-09-21):**
   the verified **metric-layer** blocker is a non-active/non-current composite leaf —
   **`gross_invoiced_amount` `audit_pending`, `is_current=false`** (`8a38e79c`, only extant version) — so
   the runtime composite loader (which selects upstream by `is_current=true` + `active`) finds no
   active/current upstream; leaf `ar_balance` is active. **Necessary candidate repair:** certify+activate
   the leaf via the governed MCF cert path — the leanest candidate versus route (b) (corpus-wide family
   remediation, parked TSK-afd7ff). ⚠ **Not tenant-isolated:** a **platform/MCF-corpus** cert (the leaf
   serves all consumers), **gated** on MCF certification/activation + downstream-consumer impact review;
   **held** pending explicit operator approval + cert/DB-Foundation consent. **Not proven sufficient:**
   downstream source/admission/CO/OC/projection verification is pending (no full chain audit). **MLS-14
   for DSO is VERIFIED SATISFIED** (`days_sales_outstanding` governance `active`, cert-gated). The prior
   "OC re-pin/operand-projection" framing is withdrawn as unsupported (not excluded — unverified).
6. **MLS-24→25** — evidence (gated by D575 non-superuser identity) + portal KPI.

Upstream hygiene: **TSK-aaa6ae** (chain-status stale, masks the Aug-21 grain archival) should be
refreshed — but MLS-14 readiness for the chosen metric must be **independently verified**, not
inferred from a refreshed status.

## 6. Sequencing (the Kaveri walk)

Thin-real-slice first, same discipline as the platform close: confirm lc5 is up, provision Kaveri,
wire the Odoo source, then walk one metric (DSO) to a snapshot before generalizing. Each rung is a
governed step with its own foundation gate; nothing is hand-seeded past a cert gate; all writes go
through governed services (`POST /tenants`, the `schema-provisioner` onboard endpoints /
tenant-metric-binding as-built route, provisioning worker, admission/resolution/evaluation). Any
shared-contract change (route (a)) is subject to the §5 gating. Every rung transition is verified
against substrate, not asserted.

## 7. Authority & provenance

- **Readiness definition:** DEC-33d436/D606 (platform/tenant split; tenant = MLS 15-25 / L10).
- **Spine:** DEC-c9e623/D389 (the 25-rung ladder + MLS-14→15 handoff + 17-column ledger shape).
- **Reclassification of the continuous run into this program:** DEC-958d3a/D613.
- **Lanes:** DEC-a67bae/D590 (L10 = platform→tenant boundary lane).
- **Tenant fiscal-calendar locator:** DEC-f02230/D368 (tenant-DB `organization.fiscal_calendar_config`).
- **Execution ADR:** DEC-f44a71/D617 — how the Kaveri walk is sequenced and evidenced (route (a) locked,
  source-bounded with the §5 shared-contract gating).
- **Coordination:** DEC-568d0b/D615 — **publication/acceptance pending** (not in this docs tree).
- **Anchor task:** TSK-d73f01. **Stand-up session:** SES-b5c14b (2026-09-21).
- **Grounding:** the read-only `bc_platform_dev` / `tbc_probe_unit4_dev` reads recorded in **§3.1**;
  the matrix RAG is reproducible from those queries.

## 8. Execution log (the Kaveri walk, as run)

Record of what was attempted on the Kaveri walk, newest first. **Evidence discipline (per
RESPONSE-Codex-d617-022/023 F5):** claims are split into two kinds. *(reproducible read-only)* =
substrate state as observed in the **2026-09-21 snapshot**, whose timestamped queries and results are
in the immutable auditor proof **`docs/PROOF-Codex-d617-022-pr57-review-2026-09-21.json`** (bc-external-audit
commit `6630b63cc8`, content SHA-256 `af182041907dc2ec16b20f305441e65084e509a57ea15c5069922786183a2324`);
those reads are re-runnable against `bc_platform_dev` / `tbc_kaveri_dev` at platform code pin **bc-core
`7d95e953`**, and were re-confirmed unchanged on 2026-09-23 (that re-confirmation is uncommitted, so
treat it as source-reported). *(source-reported)* = an out-of-band HTTP/API result from this session
that was **not** independently replayed by the auditor — treat as reported, not proven. No claim here
discharges the D617-019 execution gates.

**From 2026-09-23 on,** entries use the same two tags. *(reproducible read-only)* now means
"shown by the §3.1 E/F queries of 2026-09-26T07:17Z". *(source-reported)* cites the closure file,
Codex response or change record the claim rests on. Codex responses are cited by file name in
`bc-external-audit/docs` at `origin/main` `56c08019`. The D623 evidence is on barecount-devhub branches
`claude/d623-stage2-driver` (`eba67b85`) and `claude/d623-w3-apply` (`9f492acb`) under
`artifacts/d623/`. Where Codex accepted a live closure **after its own read-only check**, the entry
says so. **Authority, bounded per entry:** each D623 attempt logged under 2026-09-25 and 2026-09-26
names its own single-use Codex `EXECUTION CLEARED` response, which binds the exact driver hash, and,
where the evidence records one, its committed operator-grant file (`artifacts/d623/OPERATOR-AUTH-*.md`).
Step 2 was run by Codex itself under d617-048. That assurance covers **only** those entries. The
2026-09-23 run and its direct database edits had **no** such clearance; their only recorded authority
is the operator approval reported in a session checkpoint, and it is logged as such.

### 2026-09-26 — identity concept minted; CC 1.6.0 approved; tenant 0003 live; MLS-22 regression found

- **D623 7c-a: Journal Entry `recording_legal_entity` reference concept (00:56Z).** *(source-reported)*
  BCF `createReferenceConcept` minted concept `115b2945-1fd2-4386-9a60-81b6781926d2` (Journal Entry →
  Legal Entity) with `identityRole=identity_bearing`, published `active` in the same call
  (`stage7c/live-7c-a-20260926T005423Z/closure.json`). Cleared by RESPONSE-Codex-d617-070 (driver
  `410a3e66…`); closure accepted by d617-071.
- **B1: canonical meta-schema v2 gains the derivation function `resolve_source_entity_binding` (04:39Z).**
  *(source-reported)* Change request `2175096c…` was made by the operator and approved by a second
  identity, `bc-dbadmin@selenite.co` (`stage7c/b1-live-20260926T043857Z/closure.json`). The closure
  cites clearance RESPONSE-Codex-gen-e9bcab-05.
- **7c-b act 1: move of the served build to `9d0dc5aa` (05:25Z).** *(source-reported)* The script
  **stopped at its "move" step, exit 1**. Codex checked read-only and accepted that the intended
  served state was reached, without relabelling the attempt as completed (RESPONSE-Codex-gen-6f1e89-04).
- **7c-b act 2: cc-dh5d9 1.6.0 created, submitted, approved (05:41Z).** *(reproducible read-only)*
  1.6.0 is `approved` and 1.5.0 is still the only `active` version. *(source-reported)* Cleared by
  gen-6f1e89-05 (driver `e71f5249…`); closure accepted by gen-6f1e89-06 ("1.5.0 remains the sole
  active version"). Activation is deliberately left to 7c-c (`stage7c/HANDOFF-7c-c.md`).
- **MLS-22 regression: active CC 1.5.0 can no longer be resolved (TSK-387779).** *(source-reported)*
  A 7c-c design check on a clone of live (`stage7c/7cc-design/README.md`, F1) found two effects of
  concept `115b2945`, which is identity-bearing but **derived** (from `company_id` via
  `resolve_source_entity_binding`) and is mapped by no observation-contract field:
  - activating 1.6.0 is refused with **403** ("Unit 0 F4a: … not mapped by any pinned
    observation_references leg");
  - the served build's resolver **throws** on the active 1.5.0 before it reads any tenant data.

  A control run on the clone, with the concept's identity role changed, got past that point.
  **Bounds on the claim:**
  - "Refused on live since 2026-09-26T00:54Z" comes from reading the same code against identical
    registry rows. No live resolution was attempted, and Codex calls the date "an inference, not an
    independently observed runtime history" (RESPONSE-Codex-gen-e90cd0-01, CHANGES REQUIRED, which
    confirms the diagnosis).
  - The stored 1.5.0 COs from 2026-09-23 are unaffected *(reproducible read-only: still 10,744)*.
    What is lost is the ability to resolve new ones.
  - The same design check also found (F2) that the D575 activation fan-out does nothing in the
    served build, because DI resolves the injected dependency to null (TSK-231594, bc-core#830). It
    found (F3) that the provisioning worker does not exit (bc-core#831).
  - The fix path is the D626 ADR (bc-docs#67), then PR-B, then 7c-c (§5.0).
- **W3: tenant migration 0003 applied to `tbc_kaveri_dev` (07:02Z).** *(reproducible read-only)*
  Ledger seq 3 = `0003_admission_run_completion_hold`, applied `07:02:15Z` from bc-db `886161c4`
  (bc-db#76) with disposition `6f77a29d…`. Its new hold/release tables are empty. *(source-reported)*
  Driver `16e332a1…`, cleared by RESPONSE-Codex-gen-00a388-02. The apply log has 65 `ok` checks and
  none failed, fence lease `26338959…`, and 13 refused probes that were rolled back and left nothing
  behind (`w3-apply/live-20260926T070207Z/{closure.json,apply.log}` on `claude/d623-w3-apply`).
  Codex accepted the live closure after its own read-only check (gen-00a388-03) and closed the thread
  (gen-00a388-04). The bc-db release substrate was reviewed on gen-54dcb4 (accepted with boundary,
  -04/-05; thread closed -06). The **release path itself has not yet been exercised on Kaveri**
  (TSK-080294).
- **The d617 exchange was retired (RESPONSE-Codex-d617-072).** New intake is closed, and the
  remaining D623 items continue on gen- threads. Codex's words: this "retires the exchange route, not
  the D623 Platform Readiness program or any unfinished work".

### 2026-09-25 — fiscal legal entity, connection owner, OC 1.3.0, source identity (D623 steps 2–7b)

- **Step 2: platform and tenant migrations (06:38Z).** *(reproducible read-only)* Kaveri ledger seq 1–2
  (`0001_tenant_ledger`, `0002_source_legal_entity_binding`) were applied at 06:38Z from bc-db
  `f3735d61`. *(source-reported)* Platform ledger events 28–30 (`0018`, `0019`, `0021`). This attempt was
  run by Codex under RESPONSE-Codex-d617-048 (driver `603b4de9…`), with an independent closure in
  `CLOSURE-Codex-d617-048-stage2-live-2026-09-25.md` ("ACCEPTED WITH BOUNDARY — COMPLETED").
- **Step 3: legal entity + fiscal calendar + connection owner (09:47Z).** *(reproducible read-only)*
  `KAVERI-IN` (IN, INR) and its `IN-APR-MAR-MONTHLY` calendar from 2023-04-01. The connection's
  `tenant_id` is now Kaveri. *(source-reported)* The first attempt (09:12Z, cleared by d617-052)
  **halted with HTTP 500 on A1 and wrote nothing** (d617-053; `live-stage3-claude-20260925/closure.json`).
  A successor driver, `c38061f0…`, cleared by d617-054, completed A1 and A2 with one assignment
  event (`live-stage3-s4-claude-20260925/`). Codex accepted this after its own read-only check
  (d617-055).
- **Step 5: OC 1.3.0 and reader rebind (11:15Z).** *(reproducible read-only)* OC `45f8b60c…` 1.3.0 is
  active **alongside** 1.2.0. *(source-reported)* The driver `557e9f81…` (cleared by d617-058) created,
  approved and activated 1.3.0, which adds `company_id` and 6 fields, and moved Kaveri's
  `account.move` reader binding to it (`live-stage5-claude-20260925/`). Accepted by d617-059.
  `HANDOFF-7c-c.md` records both OC versions as active and plans to supersede 1.2.0 in 7c-c. The same
  handoff (§4) warns about the CC case. When 1.6.0 activates beside 1.5.0, metric evaluation fails
  with "ambiguous grain CC", while `mcv_chain_status.grain_cc_active` still passes, which is a false
  green. So the window with two active CC versions must stay short and must never span a scheduled
  evaluation.
- **Step 7b: serve pinned build `238f8c09`, then Kaveri source identity (15:39Z).** *(source-reported)*
  The served build moved to a clean checkout at `238f8c09` (bc-core#822). The step then created key
  domain `odoo_res_company_id`, a declaration on leg `je_primary` (locator `company_id`) and a binding
  from Odoo company `1` to `KAVERI-IN` (`stage7b/live-20260925/7b-run/closure.json`). Cleared by
  d617-066 (driver `2c734b0e…`); closure accepted by d617-067.
- **Code landed that day** *(source-reported, Codex landing responses):* bc-db#74/#75 (`f3735d6`,
  d617-046), bc-core#818 (`acf7b22`, 049), #820 (`4746867`, 050), #821 (`e2f3a93`, 056), #817 (`81e02b6`,
  060) and #822 (`238f8c0`, 064). The D624 source-onboarding ADR DEC-bacbf5 was accepted with boundary
  at revision 2 and stays `proposed` (d617-037).

### 2026-09-24 — D623 decided; the first apply package was sent back

*(source-reported)* The D622/D623 ADRs were ratified, but only at a corrected head (RESPONSE-Codex-d617-032,
accepted with boundary). Codex returned the first D623 fiscal-and-binding apply packages with
CHANGES REQUIRED (d617-030, -031) before the corrected successors of 09-25.

### 2026-09-23 — first real run on Kaveri: 10,744 moves admitted, resolved and evaluated to one snapshot

- *(reproducible read-only)* Four admission runs (06:45Z–07:16Z) wrote 25,744 `account.move`
  admissions and 10,744 SO rows. Two resolutions produced 10,744 COs each: cc-dh5d9 1.4.0 at 07:31Z
  and 1.5.0 at 07:38Z (1.5.0 was created at 07:38:03Z). 1.4.0 is now `superseded`. Its
  `supersede_after` of 2026-09-25 07:38Z is the 48-hour mark that activation sets
  (`HANDOFF-7c-c.md` §4), not the moment of supersession. Kaveri's SC binding dates from 05:21Z and the `*` fiscal-calendar row from 06:41Z. Three metric runs
  for `total_journal_entries` followed: `deferred_inputs_unavailable` (07:34Z), `failed` (07:41Z) and
  `completed` (07:52Z). The last is an accepted evaluation with snapshot **212** for FY2026-27/P05.
- *(source-reported, SES-1da00d checkpoint #5 and CHG-12f4fd)* That session found and fixed seven gaps
  in sequence to get there:
  1. CC `resolved_schema` was empty;
  2. Kaveri's `schema_name` was malformed;
  3. there was no fiscal-calendar config, so the `*` row was added;
  4. Odoo relational and false-valued fields were typed wrongly for fact writes;
  5. the SO table name was derived from the Odoo model rather than the SC;
  6. there was no `posting_date_field`, so 1.5.0 was authored;
  7. the `count` path refused string values.

  The checkpoint records three data changes as **operator-approved direct database edits**, not
  governed-service writes:
  - `tenant.tenants.schema_name` (one row, `tbc_kaveri_dev` → `tbc_kaveri`);
  - the `*` row in `organization.fiscal_calendar_config`;
  - `runtime.reader_flavor.config_json`.

  **These are exceptions to the Foundation rule "no DB row hand-edits".** The authority recorded is
  the operator's approval, as stated in that checkpoint ("DB changes (operator-approved)"). No
  governed-service write or change request covers them. The rows they produced are still live: the
  `*` calendar row (§3.1 F) stamped every CO so far, and `schema_name` reads `tbc_kaveri` (§3.1 E). It also records the code fixes as uncommitted at the time. How
  gap 7 was closed before the completed run is not stated in the sources used here.
- **Meaning:** this is the first continuous real-source run for the platform, from source rows to
  snapshot. It is **not** yet readiness:
  - the periods came from the `*` calendar, not per legal entity (which D623 then set out to fix);
  - the metric is `total_journal_entries`, not DSO (§5.0);
  - its one E6-B evidence emit is reported as written by the superuser, and its atomicity is unproven, so it does not satisfy MLS-24 (§3.0);
  - nothing has been shown in the portal (MLS-25).

### 2026-09-21 — MLS-17 wiring attempted, MLS-19 source binding fail-closed on a grain mismatch

**MLS-15 (tenant) — infrastructure provisioned; per-metric MLS-15 NOT accepted (F1).** *(source-reported)*
the tenant was provisioned earlier this session via governed `POST /tenants` — that request's execution
is not independently replayed here. *(reproducible read-only)* the resulting row exists: `tenant.tenants`
has `slug='kaveri'`, `tenantId f0a5e695-b475-472c-87f8-71609be1a8c3`, `schema_name='tbc_kaveri_dev'`,
`status_code='active'`. This is infrastructure provisioning only — **per-metric MLS-15 acceptance
remains pending** (the MLS-14→15 handoff gate, §2 + §3.1C), and **D617-019 F1–F3 remain open**.
*(reproducible read-only)* `tbc_kaveri_dev` holds no runtime data:
`progression.admission` / `canonical_evaluation` / `metric_evaluation`, `evidence.evidence_object` /
`evidence_record` / `lineage_object`, `organization.fiscal_calendar_config` / `org_profile`,
`tenant_dim.dim_legal_entity` all **0 rows** (observed 2026-09-21). The **`fact` schema EXISTS but
holds no relations (F4)** — `pg_namespace` returns `fact` in `tbc_kaveri_dev`; `pg_class` shows no
`fact.*` relations. (No dated evidence of an earlier *absent* `fact` schema is claimed; the earlier
note of "no fact schema" was an `information_schema.tables` artifact — an empty schema returns no
table rows — and is corrected here.)

**Contract chain — existing account.move versions are ACTIVE (F6).** For source object `account.move`
(`019fdfdb-e56e-7003-ad43-3e3f0286c38a`): SC `sc-929yc` (`019fe42b-7f2b…`, active 1.0.0), AC
(`019fe42b-7fe8…`, active 1.1.0), OC `45f8b60c…` (active 1.2.0, pair-grammar), CC `cc-dh5d9`
(`7fa4b84f…`, active 1.2.0) *(reproducible read-only)*. **This does not mean the chain is sufficient
or that no authoring is required for the DSO walk** — the metric family's grain has no active CC (see
MLS-19), so a shared-contract authoring decision is still open and subject to §5 gating.

**MLS-17 (connection) — connectivity/credential source-reported; completion pending tenant-context +
credential-wiring verification (F2).** *(reproducible read-only)* `runtime.connection
kaveri-odoo-v3lc5` (`01a07b9d…`) is `connection_status='connected'` with `tenant_id` **NULL** and
`environment_code='development'`. *(source-reported)* the `draft→connected` transition was recorded
earlier this session by a governed `POST /api/connections/:id/checks` — that request's execution is
not independently replayed here; note `ConnectionService.recordCheck` **accepts the submitted check
status and updates the row — it does not itself authenticate to Odoo**, so a `connected` row is an
attestation, not proof of live connectivity. *(source-reported, not auditor-replayed)* an
out-of-band `admin/admin` login to `v3_lc5` returned uid 2 and a read of `account.move` reporting
**2,699 posted `out_invoice`** of 10,744 moves. **On tenant ownership:** the NULL `tenant_id` is a
lookup fact, not a design claim that ownership is unnecessary — `TenantConnectionController` `POST
/api/t/connections` **does** pass the authenticated `tenant.tenantId` into
`ConnectionService.createConnection` and the repository persists it, and tenant reads enforce
ownership; the reader runtime's `getConnection(flavor.connectionId)` (no tenant arg) only proves the
platform-side lookup path, not that `tenant_id` is unnecessary. MLS-17 completion is therefore
**pending verification** of the tenant-context and credential wiring the runtime will actually use.

**MLS-19 (source binding) — ATTEMPTED, fail-closed.** *(reproducible read-only)* Kaveri has 0
`tenant.tenant_binding` and 0 `tenant.contract_binding`. *(source-reported)* `POST
/schema-provisioner/onboard-metric` for the invoice leaf `gross_invoiced_amount` (`cdd2a474…`, env
`dev`) returned **HTTP 422** — *"no active canonical contract declares grain entity `e3963e45` — the
metric's chain is not resolvable."* The **zero-writes** characterisation is bounded to a code-path
inference (F5), not a full request replay: in `MetricChainReverseWalkService.walkFromMetric` the
missing-grain refusal is thrown **before** `populateBindings` / provisioning enqueue, and the 0/0
binding counts above are consistent with no write having occurred.

> **Root cause — grain-entity mismatch (the current MLS-19 blocker).** *(reproducible read-only)* The
> DSO metric family (`gross_invoiced_amount`, `ar_balance`, `days_sales_outstanding`) all declare
> grain entity `e3963e45` = **"Customer Invoice"** (finance / accounts_receivable). The only active
> CC on the account.move chain, `cc-dh5d9`, derives grain `6e47ef23` = **"Journal Entry"** (its
> fields `entry_rate` / `posting_date` / `status` resolve to the Journal Entry entity via
> `business_concept.entity_id`), and **no active CC declaration derives `e3963e45`**. So the metrics'
> grain has no active CC and the chain is unresolvable. Resolving this is a **shared-contract
> authoring decision** (author an active CC on the Customer Invoice grain, or re-grain the metric
> family), subject to §5 gating — upstream of and distinct from the MLS-23 leaf-audit gate.
> `mcf.mcv_chain_status` for `gross_invoiced_amount` (verdict `amber`, `grain_cc_active:pass`) is
> **stale** (computed 2026-08-02); the live reverse-walk is authoritative.

**Reader binding — forward-walk CONSUMER mismatch, not malformed data (F3).** *(reproducible
read-only)* Reader "Journal Entry" (`ae6a3b99`, flavor `13a0bc42`) has an active
`runtime.reader_binding` in env `dev` whose `source_contract_id` holds `019fe42b-7fe8…@1.1.0`. That
column **carries an admission-contract id by design** (v4 substrate fact,
`resolved-admission-context.ts:152`): the admission path selects it as the AC, loads
`admission_contract_version`, and derives the parent SC from the AC's `contract_json`. The value is
therefore **correct** for the admission runtime — it must **not** be rewritten to an SC id (that would
break `bindAdmissionContract` / admission resolution). The real issue is narrower: the D369 **forward**
walker `findSourceContractsForReader` inner-joins this column to `contract.source_contract`, which
returns 0 because the column holds an AC id — a forward-walk consumer/naming mismatch to reconcile in
code as a **separate governed unit** (resolve AC→parent SC in the forward walker, as the admission path
does), not a data re-bind. Environment note: the binding is env `dev` (the admission default) while the
connection row is `development`; `tenant.tenant_binding` across tenants uses both codes — a wiring
reconciliation to settle before admission, not a defect in this row.

**MLS-23 (downstream):** *(reproducible read-only)* composite leaf `gross_invoiced_amount`
(`8a38e79c`) is `audit_pending` / `is_current=false`; DSO chain verdict `red`
(`bindings_resolve:fail:1_unresolved`). Gated behind the MLS-19 grain decision.

**Incidental fix landed (governed):** the `flavorCount=0` anomaly on the connection traced to a
wrong-column filter in `ConnectionRepository.{count,list}FlavorsByConnection` (filtered the
`@deprecated` `observation_contract_id` instead of `connection_id`). Fixed with a RED-first
DB-integration regression test + CI wiring; Codex-reviewed (RESPONSE-Codex-d617-020, accepted with
boundary) and merged as **bc-core PR #810** (squash `7d95e953`, custody in RESPONSE-021).
