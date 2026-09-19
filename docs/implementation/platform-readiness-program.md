---
title: Platform Readiness & Legibility — Program (SSOT)
status: drafting
date: 2026-09-19
supersedes: >
  bc-core/docs/design/platform-functional-refactor-plan.md and
  bc-core/docs/design/platform-functional-refactor-package.md (R4, 2026-08-23) —
  migrated here and consolidated; those files are now pointers.
folds_in: >
  barecount-devhub/artifacts/lanes/LOCKED-LANE-TAXONOMY-2026-08-24.md (DEC-a67bae/D590)
  as the authoritative lane section; the design-plane vs execution-plane finding
  (Kaveri E2E walk); and the 2026-09-19 grounded readiness study (3 code-readiness
  agents + all 588 ADRs reconciled to functions).
anchor_task: TSK-4b2404
governing_adrs: >
  DEC-33d436/D606 (program mandate + platform/tenant readiness split + SSOT
  consolidation; this destination-first refactor is an evolution under that mandate);
  DEC-a67bae/D590 (locked lanes); DEC-c9e623/D389 (Metric Lifecycle States);
  DEC-c48b0f/D541 (design-act vs execution-act plane gate); DEC-48d222 (metric-evidence
  atomic proof / E6-B).
related: >
  Platform DB Foundation program (overview/platform-db-foundation.md, TSK-cc348a) —
  the converging program that productionizes tenant onboarding at scale.
---

# Platform Readiness & Legibility — Program (SSOT)

> This document leads with the **destination**, then the **platform functions** that must
> render it, then **where each function stands** (backend / DB / UI), and only then the
> **work** to close the gap. Read top-down. If a unit of work can't be tied to a function
> and a piece of the distance-to-destination below, it is drift.

## 1. The destination

**BareCount's platform can take a real source system, run it through the whole governed
runway, and produce a first *trusted* metric — and we have proven it once, end-to-end.**
Everything else — the functions, the tracks, the lanes, the seams — is a means to this.

Readiness has four criteria, all required: the mechanics are **streamlined · governed ·
documented · proven-once-end-to-end**. The first three are confirmable by inspection; the
fourth is the guard against declaring readiness from a checklist while the front door never
opened.

**What "proven" means here — the platform-readiness proof (decided 2026-09-19):**

- **Platform readiness = a fixture/engine-conformance proof.** Fixture data crosses *every*
  platform boundary (Source → Reader → SO → Canonical → CO → Metric Snapshot) to a snapshot
  with complete, emitted evidence, all couplings fail-closed — on a **sandbox/fixture tenant**
  (e.g. `probe_unit4`). **No customer onboarding required.** This is the arc this program owns,
  and it is what closing the runtime seams (§6) unblocks.
- **Demo readiness = platform readiness + a thin real-source slice.** A *named downstream
  milestone*, not the platform gate: the Kaveri/Odoo world walked far enough to show a
  believable metric came from a real system. It **rides on** platform readiness (and the
  Platform DB Foundation tenant substrate); it is **not** the platform proof itself.

This corrects the earlier framing that used the Kaveri tenant walk *as* the platform proof.
Platform readiness is fixture-provable; the Kaveri run is tenant-readiness confirmation on top.

## 2. The platform functions — the stable spine

The tracks and lanes churn; the **functions the platform must render do not**. This is the
north-star list. Each function carries its scope and its governing ADRs *with real status*
(open / decided / implemented) — a function with thin or no governing ADRs is itself a
finding. Statuses below are grounded against the ADR registry + files, 2026-09-19.

### Shared platform services (the multi-tenant chassis)

| # | Function | Scope (plain) | Governing ADRs (status) |
|---|---|---|---|
| **S1** | **Authentication** | Who are you — Cognito login, JWT, MFA/TOTP, global guards | 1fcbc0·a537bf·f6c2e5·912f4f·13a260·a2af9e·8dc51d *impl* · 78b437 *impl* |
| **S2** | **User & access management** | What may you do — users, roles, permissions, invites, platform/tenant scoping | 42b9c0 *impl* · f0e78e *decided* · **6a9777 (RBAC/owner deferred)** |
| **S3** | **Tenant lifecycle & management** | Provision container/DB, states, config, health, scoping, retirement | 7df811·103acb·ad76e9·a67518·66d3ca·c193a1·8ba0ea·3ee0f6 · **09fb2f *proposed*** |
| **S4** | **Pricing & subscription** | Packages, entitlements, tier gating, billing | **324d9e (Stripe) decided-not-built** · **4aa2fd reversed** |
| **S5** | **Operator console (bc-admin)** | The operator's cockpit surfacing/administering everything below | 5cef91·c800d2·b39a00·7eec2e *impl* |

### Core — the governed authoring runway (10 lanes, LOCKED DEC-a67bae/D590)

Each lane is a first-class function (an artifact family). The runway enters at **L1 (source)**
and exits at **L10 (tenant handoff)**. Source-onboarding and tenant-onboarding are **workflows
over these lanes**, not lanes.

| # | Lane | Owns | Governing ADRs (status) |
|---|---|---|---|
| **L1** | Source Catalog | `source.*`; catalog | 3078ce·3b2ff9·05140c·908a69·12558e·3d4304 |
| **L2** | Source + Admission Contract | `contract.source_contract*`, `admission_contract*` | 426b24·8a6acb·ca4c1e·baaa09·e27625·3fe389 |
| **L3** | BCF Enrichment | `concept_registry.*`; bcf/registry | 149ab2·02f5a9·65dc86·6c57e2·ffee4e |
| **L4** | Observation Contract | `contract.observation_contract*` | 36d78f·5fd322·0e3c64·4a17e0·585edb |
| **L5** | Canonical Contract | `contract.canonical_contract*`, `canonical_mapping*` | acce2b·a7c0f9·f5018a·7d2f8c·35b34b·9d1f4b |
| **L6** | MCF Metric (+ certification) | `mcf.metric_contract*` + bindings + `certification_record` | c3e57f·542722·09f86b·327d4e·31c212·c48b0f (cert = an L6 *capability*, not a lane) |
| **L7** | Reader | `runtime.reader*/connector*/connection*` | 17112b·0d5b39·f656a6·ecd55c·f0866a |
| **L8** | Registration / Directory | `metric_directory.*` | **b5c7ff/D506** · 5842d4·375e6b·37967b |
| **L9** | Chain Integrity | `mcf.mcv_chain_status`, `chain_audit_evidence` | 29b518·354552·762336·b049f6 |
| **L10** | Tenant Onboarding | tenant DB provisioning, `admin.connection*` (Platform→Tenant boundary, MLS-14→15) | a67518·ad76e9 (+ S3) |

### Core — runtime & cross-cutting

| # | Function | Scope (plain) | Governing ADRs (status) |
|---|---|---|---|
| **RT** | **Runtime / metric-evaluation engine** | Execution plane — observe→admit→canonical→evaluate→snapshot→evidence | 9c0da7·01bd6b·0d5b39·95687d·c4c742·c48b0f · 48d222 (E6-B) |
| **EV** | **Evidence, chain-integrity & audit** | Prove it, immutably — evidence store, custody, chain-status | 48d222·ebb3cd·97445d·dc5d52·b049f6·793e13 |
| **TS** | **Tenant self-service (bc-portal)** | The customer's face — finish onboarding, connect source, view metrics | 6cdceb *(current; chain cce1d3→04dade→6cdceb)* · a1290e·c566f3·e82f0a |
| **A1** | **Action / Intervention** *(design pending)* | The execution model's final boundary — Metric Snapshot → **Action Object**; Intervention Contract | 615b87 (IC 6th family) · bae0ef · 3cc8a1 *(reversed)* — **no design yet** ([[TSK-4609a6]]) |

**A1 is deliberately on the map with an honest `design pending` status.** It is the layer the
program has deferred "for later" for months; naming it as a function is what stops it staying
invisible. It is **not** a demo-gate blocker.

**Parked as cosmetic (not a function):** design-system / visual-language governance
(DEC-2cf250 visual language, DEC-2d5df2 dark-mode, the DS stack) is owned by a future
**dedicated UI refactoring program** ([[TSK-91c05f]]), not the readiness function set. This
covers *cosmetic* only — missing operator *doors* (below) are readiness gaps, not cosmetic.

## 3. Function readiness matrix (grounded 2026-09-19)

RAG: 🟢 built/sound/door present · 🟡 partial/stub · 🔴 absent/gap · ❓ unverifiable this pass.
Every cell is evidence-backed (see the grounding study; DB counts are live).

| Function | Backend | DB | UI | Headline |
|---|:--:|:--:|:--:|---|
| S1 Auth | 🟢 | 🟢 | 🟢 | 4 global guards + Cognito TOTP; mature |
| S2 User/access | 🟡 | 🔴 | 🔴 | admin-provision only; no RBAC tables; UI placeholder |
| S3 Tenant lifecycle | 🟢 | 🟢 | 🟡 | provisioning + 5-state model live; config/health/scoping/infra = stubs |
| S4 Pricing | 🔴 | 🔴 | 🔴 | no Stripe/billing tables; `pricing.package` = reader-tiers only |
| S5 Operator console | 🟢 | — | 🟡 | mature (255 commits); placeholder doors (users, tenant-ops, pricing, infra) |
| L1 Source Catalog | 🟢 | 🟢 | 🟢 | full |
| L2 SC+AC | 🟢 | 🟢 | 🟢 | SC 305 / AC 305 (1:1); create doors |
| L3 BCF | 🟢 | 🟢 | 🟢 | concept_registry 18 tables; full console |
| L4 OC | 🟢 | 🟡 | 🟡 | `observation_field_map`=0; authored via metric author-chain |
| L5 CC | 🟢 | 🟡 | 🟡 | `canonical_mapping`=0; **CC-authoring UI removed** (D418) |
| L6 MCF | 🟢 | 🟢 | 🟢 | metric_contract 432; cert 1316; full |
| L7 Reader | 🟢 | 🟢 | 🟢 | reader_observation_binding populated; full |
| L8 Directory | 🟢 | 🟢 | 🟡 | rich BE/DB (member 415); **only directory-tree door missing** (not a full black box) |
| L9 Chain Integrity | 🟢 | 🟢 | 🟡 | status door yes; `chain_audit_evidence` (127) no door |
| L10 Tenant Onboarding | 🟡 | 🟡 | 🟡 | provision only; `onboarding_record`=0; 4 tenant tabs = stubs |
| RT Runtime engine | 🟡 | 🟢\* | ❓ | all boundaries wired; **2 live silent seams** (§6); E6-B evidence LIVE. \*tenant fact/progression unverifiable via allowlist |
| EV Evidence/audit | 🟢 | 🟢 | 🟡 | hash-chained + atomic proof live; cert 3530; no inspector UI verified |
| TS Tenant self-service | 🟢 | — | 🟡 | metric/dashboard views real; onboarding = static shell |
| A1 Action/Intervention | 🔴 | 🔴 | 🔴 | design pending — the deferred layer |

**Reading the matrix as distance-to-destination:**
- **The metric authoring/certification path is green** (L1–L3, L6, L7). The runway can author and certify a metric.
- **Blocks a *correct* metric (destination-critical):** RT seams #2 and #3 (§6) — both execution-plane, both silent, both fixable *without design change*.
- **"No-black-boxes" legibility gaps (Track L):** L8 directory-tree door, L9 chain-audit door, L10 tenant tabs, S2 users. Functional doors missing — **not cosmetic**.
- **Incomplete platform, not blocking a compute demo:** S4 pricing (unbuilt), S2 RBAC (absent), C5/TS onboarding-completion (static), A1 (design pending).

## 4. Scope boundary — what this program owns

- **Platform readiness = MLS 01–14** (DEC-c9e623): authoring → certification → activation +
  runtime-engine conformance, fixture-provable. **This program.** Handoff at **MLS-14 → 15**.
- **Tenant readiness = MLS 15–25**: a real tenant's chain runs to a KPI (the Kaveri pilot).
  Downstream; rides on platform readiness **and** Platform DB Foundation W2.
- **Design plane vs execution plane (DEC-c48b0f):** the AI authoring panels (design) are
  governed and sound — do not rebuild. The runtime *couplings* between boundaries (execution)
  were ungoverned and can silently no-op — that is the seam work in §6.

## 5. The work — four tracks (the work axis)

Ordering **T → (R ∥ L) → S**.

- **T — Tooling & executable gates. ✅ CLOSED (2026-08-25).** doctor · column linter · QA
  consolidation (D589) · import/controller-DB gates · architecture-spec typecheck ·
  route/provider/persisted-code snapshots. Lesson: pin the declared enforcement surface, don't
  out-parse an adversary.
- **R — Runtime Foundation conformance. 🟡 THE GATE / critical path.** Close the RT function's
  execution-plane gaps: govern the coupling seams (§6), and complete the by-design fail-open
  follow-ups. **Corrected facts (2026-09-19):** E6-B/FND-VI evidence emission is **LIVE, not
  dormant** (PR #704, no flag) — atomic for governed MCF metric evaluation; the remaining
  fail-open boundaries are **four** by ADR design (observation, canonical-single-item, action,
  evaluation — DEC-48d222), **not "six / §35"** (that was a phantom). RuntimeScheduler is
  disabled-by-default and reconcile-stripped (D575 owner worker), not class-retired.
- **L — Legibility & no-black-boxes (parallel with R).** Close the operator-door gaps in the
  matrix (L8 directory-tree, L9 chain-audit, L10 tenant tabs, S2 users). Co-requisite with R —
  a governed step with no operator door is not "ready." Also: derived-doc regen, dead-code
  inventory, doctrine↔code gap filing.
- **S — Structure (decided file moves only). ⏸ DEFERRED until R lands.** Each move ADR-gated.

## 6. The runtime seams (execution plane) — the destination-critical gap

Three coupling seams found on the Kaveri E2E walk, same class (two sides disagree on an
identifier → silent no-op). Grounded 2026-09-19:

- **seam #1** `source_key` object-vs-string — **FIXED** (PR #726; 10,744 rows admitted).
- **seam #2** — provisioner `findSourceContractsForCanonical` reads only `sc_version_id`; a
  live **pair-grammar** OC (`account.move`) has none → NULL join → CC resolves 0 upstream SCs →
  activation fanout **silently strands**. Fix: read the pair-grammar keys (or both shapes) like
  the resolver does. **Real live bug** (a prior "not-a-bug" read was half-wrong). → [[TSK-35c386]] (fix reportedly ready on a branch; anchor [[TSK-b5ab8a]])
- **seam #3** — admission resolves the source-fact table name via an **AC id**
  (`getName('source', effectiveAc.contractId)` → null → `fact.so_` row silently skipped).
  **PROVEN an execution fix, not a design change:** `fact.so_{sc}` is provisioned/keyed by
  Source-Contract identity, so SC-keying is a declaration the runtime *violates*. Fix: use the
  already-resolved `parentSc.contractId` (three sites — guard the class). → [[TSK-a5f7c5]] (anchor [[TSK-b5ab8a]])

## 7. Unit ledger — the DB-Foundation-style work breakdown

Every unit of Track work is a row here, with a mandatory **design/execution intake gate**
(DEC-c48b0f/D541) filled *before* any code: a unit cannot be built until its intake states
either *"declaration correct, engine violates it (execution) — verified against ground truth"*
**or** *"declaration missing/wrong (design) → this is a contract change, not a boundary patch."*
Live status stays in git/PR/DevHub; this table is the decomposition + intake record.

| Unit | Function | Plane | D541 intake | Status | Task |
|---|---|---|---|---|---|
| R-1 seam #3 admission→fact | RT | **execution** | fact.so_ is SC-keyed by the provisioner; runtime uses AC id → verified execution bug; fix = parentSc.contractId, no contract change | ready to build (parked design-first hold liftable) | [[TSK-a5f7c5]] |
| R-2 seam #2 provisioner wire-shape | RT | **execution** | pair-grammar keys are declared on the OC; provisioner ignores them → execution bug | ready to build | [[TSK-35c386]] |
| L-1 L8 directory-tree door | L8 | UI (legibility) | door absent for a built+governed subsystem → no-black-boxes gap | backlog | — |
| L-2 L9 chain-audit door | L9 | UI (legibility) | `chain_audit_evidence` unsurfaced → gap | backlog | — |
| A-1 Action/Intervention design | A1 | **design** | declaration missing → design act, not a patch | design pending | [[TSK-4609a6]] (UI door [[TSK-c33757]]) |

The RT units are satellites of the execution-plane anchor **[[TSK-b5ab8a]]** (coupling guards + onboarding lane-as-workflow). *(Ledger grows as units are scoped. New rows require the intake field before build.)*

## 8. Punch-list — surfaced, not fixed (operator ruling 2026-09-19)

The all-588-ADR reconciliation + code study surfaced items that are **recorded, not fixed** in
this arc (each is a DevHub task). Notably, the machine hygiene audit reported *0 supersession
issues*, yet reading ADR bodies found real reversals never flipped — which is why the full read
was worth it.

- Content-level reversals never flipped → [[TSK-f720ba]]
- Status-vs-body contradictions (incl. `bc6be2`: `decided` but body says "NOT to be built") → [[TSK-d3e83a]]
- Proposed-at-the-gate decisions to decide/waive (incl. `09fb2f` proposed-but-code-merged) → [[TSK-1557c5]]
- Legacy supersedes-not-flipped backfill (~16) → [[TSK-0c4e67]]
- Duplicates / filing anomalies + verify DEC-b390ef register → [[TSK-c4c8a3]]
- Propagate proven citation corrections to memory/docs → [[TSK-2d166b]]

**Proven corrections folded into this SSOT** (previously wrong in the doc or in memory): L8 is
not a "full black box" (governor DEC-b5c7ff/D506, not 01df6b/b049f6); E6-B is LIVE not dormant;
the fail-open set is four not six (no §35); seam #2 is a real bug; `f656a6` is L7; `1db6e9`
does not exist; bc-portal arch is 6cdceb.

## 9. Current gate & sequencing

1. **Close Track R** (runtime-trust): govern seams #2/#3, land the by-design fail-open
   follow-ups, **proven green under the T gates on a fixture tenant**. Critical path.
2. **Close Track L's no-black-boxes doors** (co-requisite): L8/L9 doors, L10 tabs, S2 users.
3. **Then demo readiness:** platform readiness + a thin real-source (Kaveri) slice — the named
   downstream milestone, riding on DB-Foundation W2 + operator creds.

Steps 1–2 together are the **platform-readiness gate**; step 3 rides on it.

## 10. Convergence with Platform DB Foundation

Two programs, one proof. **Platform DB Foundation** (`overview/platform-db-foundation.md`,
TSK-cc348a) productionizes L10 / tenant onboarding **at scale**. Platform readiness (L1–L9 +
engine conformance) is **separable** and fixture-provable; the pilot itself needs **no schema
change**, so the platform-readiness proof does not wait on DB-Foundation W2+. They converge at
L10 / the Kaveri demo milestone.

## 11. Authority & provenance

This SSOT supersedes and consolidates the R4 `platform-functional-refactor-{plan,package}.md`
(bc-core, now pointers). The lane section is authoritative per **DEC-a67bae/D590**; the
platform/tenant split per **DEC-c9e623/D389**; the design/execution plane gate per
**DEC-c48b0f/D541**; the program mandate + platform/tenant readiness definition per
**DEC-33d436/D606** (this destination-first refactor + the platform-functions framing +
`A1` and the parked cosmetic concern are an evolution under that mandate — a light amendment
note to ADR-33d436 records the framing). The readiness matrix and per-function ADR statuses were
grounded 2026-09-19 (3 code-readiness agents + all 588 ADRs reconciled to functions); statuses
are a snapshot and live status stays in git/PR/DevHub.
