---
title: Tenant Readiness — Program (SSOT)
status: drafting
date: 2026-09-21
anchor_task: TSK-d73f01
governing_adrs: >
  DEC-33d436/D606 (program mandate + platform/tenant readiness split — tenant readiness
  = MLS 15-25 / lane L10, the downstream milestone); DEC-c9e623/D389 (Metric Lifecycle
  States — the 25-rung ladder, Platform 01-14 / Tenant 15-25, and the MLS-14→15 handoff);
  DEC-a67bae/D590 (locked lanes — L10 is the platform→tenant boundary lane); DEC-958d3a/D613
  (the single continuous real run was reclassified out of platform readiness INTO this program);
  DEC-f02230/D368 (tenant DB schema organization — locates the tenant fiscal-calendar config);
  DEC-f44a71/D617 (program EXECUTION & sequencing — the Kaveri walk + route (a) for the MLS-23
  gate; the readiness DEFINITION stays in DEC-33d436, not re-decided here).
related: >
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
| **24** | Snapshot proof complete | evidence + lineage writes; D387 `proof_status='complete'` |
| **25** | KPI rendered in bc-portal | snapshot index + typed value row + tenant binding/permission pass |

## 3. Readiness matrix — grounded against live substrate (2026-09-21)

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
| 24 Proof complete | T | 🔴 | 🟡 evidence path exists (E6-B armed); **gated by non-superuser runtime identity + evidence immutability** (TSK-d43263 / D575) | Engineering |
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

Dated, grounded record of what was actually executed against live substrate, newest first. Every
write went through a governed service; every claim is re-runnable read-only.

### 2026-09-21 — MLS-17 wired, MLS-19 source binding attempted (fail-closed blocked)

**MLS-15 (tenant) — done earlier this session:** Kaveri provisioned via governed `POST /tenants`
(`tenantId f0a5e695-b475-472c-87f8-71609be1a8c3`, `tbc_kaveri_dev`, active). Tenant DB is empty of
runtime data (admission / canonical_evaluation / metric_evaluation / evidence / fiscal_calendar_config
/ org_profile / legal_entity all 0 rows; no `fact` schema).

**Contract chain is authored + ACTIVE (not a gap):** for source object `account.move`
(`019fdfdb-e56e-7003-ad43-3e3f0286c38a`) the full chain is live at the platform — SC `sc-929yc`
(`019fe42b-7f2b…`, active 1.0.0), AC (`019fe42b-7fe8…`, active 1.1.0), OC `45f8b60c…` (active 1.2.0,
pair-grammar), CC `cc-dh5d9` (`7fa4b84f…`, active 1.2.0). No SC/AC/OC/CC authoring is required.

**MLS-17 (connection) — DONE.** `runtime.connection kaveri-odoo-v3lc5` (`01a07b9d…`) moved
`draft → connected` via a governed connectivity check (`POST /api/connections/:id/checks`), after
verifying Odoo `:8100` responds (HTTP 200). `connection.tenant_id` stays NULL **by design** — the
reader runtime resolves the connection via its reader flavor and scopes by run/tenant context, not
`connection.tenant_id` (`reader-runtime.service.ts:125,154`); no governed endpoint sets it and none
is needed. **Credential verified:** `admin/admin` authenticates to `v3_lc5` (uid 2) via both
`/web/session/authenticate` and XML-RPC; the authenticated session reads `account.move` — **2,699
posted `out_invoice`** rows (of 10,744 moves) — recorded as an `authentication` success check.

**MLS-19 (source binding) — ATTEMPTED, FAIL-CLOSED BLOCKED.** Kaveri has 0 `tenant.tenant_binding`
and 0 `tenant.contract_binding`. The governed binding path is `POST /schema-provisioner/onboard-metric`
(reverse-walk metric → grain CC → upstream SC → populate bindings → enqueue provisioning; no served
DDL). Invoked for the invoice leaf `gross_invoiced_amount` (`cdd2a474…`, env `dev`). Result: **HTTP
422, zero writes** — *"no active canonical contract declares grain entity `e3963e45` — the metric's
chain is not resolvable."*

> **Root cause — grain-entity mismatch (the current MLS-19 blocker).** The DSO metric family
> (`gross_invoiced_amount`, `ar_balance`, `days_sales_outstanding`) all declare grain entity
> `e3963e45` = **"Customer Invoice"** (finance / accounts_receivable). The only active CC on the
> account.move chain, `cc-dh5d9`, derives grain `6e47ef23` = **"Journal Entry"** (its fields
> `entry_rate` / `posting_date` / `status` all resolve to the Journal Entry entity). **Customer
> Invoice ≠ Journal Entry**, so no active CC declares the metrics' grain and the chain is
> unresolvable. This is a **contract-authoring decision** (author/re-grain an active CC on the
> Customer Invoice grain, or re-grain the metric family), upstream of — and distinct from — the
> MLS-23 leaf-audit gate below. `mcf.mcv_chain_status` for `gross_invoiced_amount` (verdict `amber`,
> `grain_cc_active:pass`) is **stale** (computed 2026-08-02); the live reverse-walk is authoritative.

**Two adjacent defects surfaced (do not block MLS-19 root cause but block later rungs):**
- **reader_binding defect (MLS-18/21).** Reader "Journal Entry" (`ae6a3b99`, flavor `13a0bc42`) has
  its `runtime.reader_binding.source_contract_id` set to the **AC id** (`019fe42b-7fe8…`), not the
  SC id, and in environment `dev`. The D369 forward `onboard-connector` walk inner-joins
  `source_contract` on that column, so it resolves 0 SCs → the forward path is a no-op until the
  binding is corrected to the SC id.
- **Environment inconsistency.** The connection is `development`; the reader_binding is `dev`;
  `tenant.tenant_binding` across tenants uses both `dev` and `development`. Kaveri's wiring should be
  reconciled to one environment code before admission.

**MLS-23 (downstream, unchanged):** composite leaf `gross_invoiced_amount` (`8a38e79c`) is
`audit_pending`/`is_current=false`; DSO chain verdict `red` (`bindings_resolve:fail:1_unresolved`).
Gated behind MLS-19.

**Incidental fix landed (governed):** the `flavorCount=0` anomaly on the connection traced to a
wrong-column filter in `ConnectionRepository.{count,list}FlavorsByConnection` (filtered the
`@deprecated` `observation_contract_id` instead of `connection_id`). Fixed with a RED-first
DB-integration regression test + CI wiring; Codex-reviewed (RESPONSE-Codex-d617-020, accepted with
boundary) and merged as **bc-core PR #810** (squash `7d95e953`).
