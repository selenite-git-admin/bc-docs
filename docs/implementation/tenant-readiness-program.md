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
the **lc5 Odoo** world (`:8100`, `v3_lc5`, 10,744 `account.move`): provision the tenant, wire the
Odoo source, bind and activate a metric (**DSO**, via `account.move → journal_entry → DSO`), admit
real observations, resolve them to canonical, evaluate the metric to a **real snapshot**, emit
**evidence**, and render the **KPI in bc-portal** — end-to-end, fail-closed, no fixture.

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

| MLS | State | Ground-truth signal (per DEC-c9e623 D-2) |
|-----|-------|------------------------------------------|
| **15** | Tenant exists / active | `tenant.tenants` (active) + tenant DB `tbc_{slug}_dev` provisioned |
| **16** | Tenant fiscal calendar | `tenant.fiscal_calendar_config` per legal_entity (D364) |
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

Grounded read-only against `bc_platform_dev` this session. **Two distinct questions per rung:**
*(a) is the rung green for Kaveri?* and *(b) is the machinery to build it present?* Kaveri is not
onboarded, so **every rung is 🔴 for Kaveri** — the honest baseline. The machinery column is what
matters for sequencing.

Boundary key: **P** = platform DB (`bc_platform_dev`, queryable now) · **T** = tenant DB
(`tbc_kaveri_dev`, does not exist yet). RAG = Kaveri state. Machinery = buildability.

| MLS | Bnd | Kaveri | Machinery (grounded) | Owner |
|-----|-----|--------|----------------------|-------|
| 15 Tenant exists | P | 🔴 | 🟢 governed `POST /tenants` + provisioning; **only `probe_unit4` exists; `onboarding_record`=0** | Platform |
| 16 Fiscal calendar | P | 🔴 | 🟡 **`tenant.fiscal_calendar_config` NOT FOUND** (only `master.dim_fiscal_calendar`=3); signal table absent — VERIFY/author | Platform |
| 17 Connector instance | P | 🔴 | 🟢 `runtime.connector` **`odoo-ent-v19` (Odoo 19 Enterprise, source=`odoo`) available** + `odoo-jsonrpc` | Platform |
| 18 Reader configured | P | 🔴 | 🟢 3 `odoo` reader flavors active — **1 fully wired (connector+connection), 2 unwired** | Platform |
| 19 Contract bindings | P | 🔴 | 🟡 `tenant.contract_binding`=0; **MLS-19 activation service existence UNVERIFIED** (D389 flagged not-yet-existing) | Platform |
| 20 Fact tables | T | 🔴 | 🟡 owner-privileged fact DDL via **provisioning-worker-cli** (needs `TENANT_OWNER_DATABASE_URL`; NOT in served process) | Engineering |
| 21 SO produced | T | 🔴 | 🟡 `progression.admission` path exists; **tenant probe MLS-21 existence UNVERIFIED** (F-MLS-1) | Engineering |
| 22 CO produced | T | 🔴 | 🟡 `progression.canonical_evaluation` exists; **probe MLS-22 UNVERIFIED** | Engineering |
| 23 Snapshot produced | T | 🔴 | 🔴 **⛔ no active metric is evaluable over real COs** (TSK-afd7ff: operand-projection gap / superseded OC-pin) — the critical-path gate; probe MLS-23 UNVERIFIED | Engineering |
| 24 Proof complete | T | 🔴 | 🟡 evidence path exists (E6-B armed); **gated by non-superuser runtime identity + evidence immutability** (TSK-d43263 / D575) | Engineering |
| 25 KPI rendered | T | 🔴 | ❓ bc-portal render path — verify at the end (permission/typed-value) | Platform |

**Findings surfaced by grounding (not assumptions):**
- **F-TR-1 (MLS-16):** the DEC-c9e623 signal table `tenant.fiscal_calendar_config` does not exist; fiscal calendar is currently only `master.dim_fiscal_calendar` (3 rows). Either the rung's signal moved, or the per-tenant fiscal-calendar config is unbuilt. Verify before the Kaveri walk reaches MLS-16.
- **F-TR-2 (MLS-19/21/22/23 probes):** DEC-c9e623 (May-2026) flagged MLS-19 tenant-bindings activation service and MLS-21/22/23 tenant probes as possibly not-yet-existing. Their current existence is **unverified** — an early program task, not an assumption.
- **F-TR-3 (MLS-23, the gate):** no active metric is currently evaluable over real canonical objects (TSK-afd7ff). Tenant readiness cannot reach MLS-23 until DSO (or another metric) is made evaluable for the Kaveri source.

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
  the PR #41 F3 target-preview contract). Coordination acknowledgement re-affirmed 2026-09-21.
- **Deferred flows (held, not built):** BYO-DB, BC-Agent, AWS-Separate; AWS-Shared tier only in v1.

## 5. Critical path & blockers

The buildable-now rungs are **MLS-15/17/18** (tenant provisioning + Odoo connector/reader — the
machinery exists). The path then narrows:

1. **MLS-16** — resolve F-TR-1 (fiscal-calendar signal) before/at this rung.
2. **MLS-19** — verify + (if absent) stand up the tenant-bindings path; bind Kaveri's SC/AC/OC/CC/MC.
3. **MLS-20** — run the owner-privileged provisioning worker (out-of-process) to create `fact.*`.
4. **MLS-21→22** — admit lc5 `account.move`, resolve to `journal_entry` canonical.
5. **MLS-23 ⛔** — **the gate.** Make DSO evaluable for the Kaveri source. **Decided (DEC-f44a71/D617):
   route (a)** — a tenant-scoped DSO/journal chain fix (re-pin the OC / close the operand-projection
   gap for the Kaveri source), **not** route (b) a corpus-wide fix (which stays parked as TSK-afd7ff).
   Until this clears, no snapshot.
6. **MLS-24→25** — evidence (gated by D575 non-superuser identity) + portal KPI.

Upstream hygiene: **TSK-aaa6ae** (chain-status stale, masks the Aug-21 grain archival) should be
refreshed so MLS-14 readiness for the chosen metric reads true.

## 6. Sequencing (the Kaveri walk)

Thin-real-slice first, same discipline as the platform close: confirm lc5 is up, provision Kaveri,
wire the Odoo source, then walk one metric (DSO) to a snapshot before generalizing. Each rung is a
governed step with its own foundation gate; nothing is hand-seeded past a cert gate; all writes go
through governed services (`POST /tenants`, tenant-metric-binding, provisioning worker,
admission/resolution/evaluation). Every rung transition is verified against substrate, not asserted.

## 7. Authority & provenance

- **Readiness definition:** DEC-33d436/D606 (platform/tenant split; tenant = MLS 15-25 / L10).
- **Spine:** DEC-c9e623/D389 (the 25-rung ladder + MLS-14→15 handoff + 17-column ledger shape).
- **Reclassification of the continuous run into this program:** DEC-958d3a/D613.
- **Lanes:** DEC-a67bae/D590 (L10 = platform→tenant boundary lane).
- **Execution ADR:** DEC-f44a71/D617 — how the Kaveri walk is sequenced and evidenced (route (a) locked).
- **Anchor task:** TSK-d73f01. **Stand-up session:** SES-b5c14b (2026-09-21).
- **Grounding:** read-only `bc_platform_dev` reads recorded in this session; matrix RAG is
  reproducible from the queries in §3.
