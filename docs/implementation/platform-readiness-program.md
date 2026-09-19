---
title: Platform Readiness & Legibility — Program (SSOT)
status: drafting
date: 2026-09-19
supersedes: >
  bc-core/docs/design/platform-functional-refactor-plan.md and
  bc-core/docs/design/platform-functional-refactor-package.md (R4, 2026-08-23) —
  migrated here and consolidated; those files become pointers.
folds_in: >
  barecount-devhub/artifacts/lanes/LOCKED-LANE-TAXONOMY-2026-08-24.md (DEC-a67bae/D590)
  as the authoritative lane section; barecount-devhub/CONVERGENCE-MAP.md (working map);
  finding: design-plane vs execution-plane (Kaveri E2E walk).
anchor_task: TSK-4b2404
governing_adrs: >
  DEC-33d436/D606 (this program's mandate + platform/tenant readiness split +
  SSOT consolidation); DEC-a67bae/D590 (locked lanes); DEC-c9e623 (Object Life
  States); DEC-c48b0f (design-act vs execution-act); DEC-48d222 (metric-evidence
  persistence).
related: >
  Platform DB Foundation program (overview/platform-db-foundation.md,
  TSK-cc348a) — the converging program.
---

# Platform Readiness & Legibility — Program (SSOT)

> One line: make the platform's metric-producing **mechanics** ready — and keep the
> program **legible** — so that a metric can be trusted. This is the single home
> for the program (formerly "functional refactor"); it consolidates the R4
> plan/package, the locked lane taxonomy, and the design/execution-plane finding.

## 1. What "readiness" means — and the platform/tenant split

**Readiness = the mechanics are `streamlined · governed · documented · proven-once-end-to-end`.** The first three are confirmable by inspection; the fourth is the guard against declaring readiness from a checklist while the front door never opened.

**Readiness is two-layered, along the Object Life States ladder (DEC-c9e623):**

| Layer | OLS range | Lanes | What it means | Proven by |
|---|---|---|---|---|
| **Platform readiness** | **OLS 01–14** | **L1–L9** + runtime-engine conformance | The platform machinery (authoring → certification → activation, and the runtime engines that execute a chain) is streamlined, governed, documented, and **Foundation-conformant** — up to platform activation (OLS-14). | A **controlled conformance run on a fixture/sandbox tenant** (e.g. `probe_unit4`): fixture data crosses every platform boundary to a snapshot with complete evidence, all fail-closed. **No customer onboarding required.** |
| **Tenant readiness** | **OLS 15–25** | **L10** + the runtime | A real tenant is onboarded and its KPI surfaces (OLS-23 snapshot → OLS-24 proof → OLS-25 KPI). | The **Kaveri pilot** (a real tenant end-to-end). **Depends on** platform readiness (OLS-14 active) **and** Platform DB Foundation W2. |

The handoff is **OLS-14 → OLS-15**: a tenant cannot enter OLS-15 for an MC until that MC's platform row is `active` at OLS-14. **Platform readiness is the arc this program owns; tenant readiness (the Kaveri pilot) rides on it and is a downstream milestone, not the platform gate.** (This corrects an earlier framing that used the Kaveri tenant walk as the platform proof.)

## 2. The model — three cuts of one space

The program is legible only if the different decompositions are named and kept distinct:

- **Execution axis — the four TRACKS (T/R/L/S):** *what work to do, in what order,* to reach readiness. §3.
- **Ownership axis — the ten LANES (L1–L10):** *the onboarding artifact families* (authoring a step of source→snapshot). Strict one-lane-per-surface. §4.
- **Plane cut — design vs execution:** the *design plane* (AI authoring panels that judge whether each artifact's declaration is sound) is governed and works; the *execution plane* (the runtime couplings that carry one boundary's output into the next) is ungoverned and can silently no-op. §5.

A lane is an *artifact family*; a track is a *work programme*; a **workflow** (e.g. source onboarding, tenant onboarding) is an *orchestration over lanes* — explicitly **not** a lane (DEC-a67bae).

## 3. The four tracks

Ordering rule **T → (R ∥ L) → S** — S moves the very files R changes.

- **T — Tooling & executable gates (no behavior change). ✅ CLOSED (2026-08-25).** T1 doctor, T2 column linter, T3 QA consolidation (D589), T4 import/controller-DB metadata gates, T5 architecture-spec typecheck, T6 route/provider/persisted-code snapshots — all merged. Lesson carried: pin the declared enforcement surface (exact positive validation), don't out-parse an adversary.
- **R — Runtime Foundation conformance (behavior changes). 🟡 THE GATE / critical path.** The units that decide whether a metric can be trusted: **E6-B / FND-VI** ("metric emits its own evidence, not inferred"; DEC-48d222), converting the **six fail-open proof paths** to fail-closed, the **readiness-dispatcher cascade** (DEC-01bd6b §62), **RuntimeScheduler retirement**, **D575 provisioner parity**, and **governing the execution-plane couplings** (the seams — §5). *Definition of platform-ready with confidence:* the R units land green **under the T gates**, proven on a fixture tenant. Nothing in Track S is required for it.
- **L — Legibility & alignment (no behavior change; parallel with R).** Regenerate derived docs (code-index, data dictionary, lifecycle/enforcement maps), a dead-code/duplicate inventory with dispositions, taxonomy constants for the lifecycle capabilities, **extend the ten lane kits with code paths to become the capability catalog** (no parallel catalog document), doctrine↔code gap filing. Largely unblocked; the hardest dependency — the BCF authority/authoring SOP rewrite — is done. Residual onboarding-body cleanup (TSK-f13259) is non-blocking.
- **S — Structure (decided file moves only). ⏸ DEFERRED until R lands.** Ports to kill boundary→registry path imports; decompose `BoundaryModule` into four boundary + two orchestrator modules behind a compatibility aggregate; shared pure kernel; then the ADR-gated cert-writer command extraction / McfReadService split / registry-root cleanup. Each move ADR-gated — a decision, not drift.

## 4. The onboarding runway — ten lanes (LOCKED: DEC-a67bae/D590, amends D581)

**Book-ends framing:** the runway enters at **L1 (source)** and exits at **L10 (tenant)**, bracketing the **L2–L9 authoring core**. The two *workflows* that traverse it — **source onboarding** (`onboarding/source-registration.md`) and **tenant onboarding** (`onboarding/tenant-onboarding.md`) — are orchestrations over these lanes, not lanes themselves.

| Lane | Class | Plane | Owns (strict, corrected) |
|---|---|---|---|
| **L1** Source Catalog | SD | Platform | `source.*`; `source-catalog/*` |
| **L2** SC + AC | SD | Platform | `contract.source_contract*`, `admission_contract*`; `contracts` |
| **L3** BCF Enrichment | SA | Platform | `concept_registry.*` (13); `bcf/registry*` |
| **L4** OC | SD | Platform | `contract.observation_contract*`, `observation_field_map`; `contracts/observation-chains` |
| **L5** CC | SD | Platform | `contract.canonical_contract*`, `canonical_mapping*`; `contracts/chains`, `t/ccv2-resolve` |
| **L6** MCF Metric | SA | Platform | `mcf.metric_contract*` + bindings + `mcf.certification_record`; `mcf/authoring`, `mcf/intakes`. **Certification (D541) is an L6 *capability*, not a lane.** |
| **L7** Reader | SD | Platform | `runtime.reader*/connector*/connection*`; `readers`, `reader-authoring`, `connectors`, `connections` (authors the reader; *running* it is runtime/not-a-lane) |
| **L8** Registration / Directory | SA | Platform | `metric_directory.*`; `metric-directory` |
| **L9** Chain Integrity | SA | Platform | `mcf.mcv_chain_status`, `mcf.chain_audit_evidence`; `registry/mcf/chain-status`, `mcf/chain-audit` |
| **L10** Tenant Onboarding | tenant-handoff | **Platform→Tenant boundary (OLS-14→15)** | tenant DB provisioning (skeleton owned by DB-Foundation W2.3-e), `admin.connection*`; `tenants`, `connections` |

**Note on L10's classification (this SSOT's refinement):** the locked taxonomy classed L10 "tenant," but provisioning a tenant is a **platform-operator act** (`@PlatformOnly`) at the OLS-14→15 handoff — so L10 is best read as **the boundary-crossing lane** (the platform's last act before the tenant runtime), not a tenant-side lane. The truly tenant-side work (running the chain, KPIs, OLS 15–25) is the runtime — **not a lane**.

**Not-a-lane register** (out of scope, correctly): runtime/execution `/t/*` engines (owned by the runtime-ecosystem program); privacy/retention `operations.*`; platform masters/dims `master.*`; platform ops/admin (`admin/*`, `support`, `pricing`, `infrastructure`, `schema-provisioner`, `packages`, `auth`, `docs`, `health`, …).

**Retirement list** (dead in doctrine, remove not lane): legacy pre-MCF `metric.*` + `metric-catalog*`; retired external metric-audit `metric_audit.*` (**carve out live `mcf.certification_record` first**); retired SAP `source-reference`/`onboarding` controllers (D564 Odoo-only).

## 4a. Operator UI coverage — the door-walk (no black boxes)

Every lane and every workflow should have a visible **bc-admin operator door**; a lane with none is a black box (a governed step no operator can see or drive). Mapped against bc-admin routes 2026-09-19. This is the legibility (Track L) view of the runway.

| Lane | bc-admin door (route → page) | Coverage |
|---|---|---|
| L1 Source Catalog | `/sources/onboard` (OnboardSourceSystemPage), `/sources/catalog/systems` (SourceRegistryPage) | ✅ covered |
| L2 SC + AC | `/registry/contracts/source` \| `/admission` (+ `/new`) | ✅ covered |
| L3 BCF Enrichment | `/business-concepts` (browse / review-adjudicate / author) | ✅ covered |
| L4 OC | `/registry/contracts/observation` + author via metric `author-chain` | ✅ covered (no list-level `/new`) |
| L5 CC | `/registry/contracts/canonical` + `/source-chain/mappings` (FieldResolutionPage) | ✅ covered (no list-level `/new`) |
| L6 MCF Metric (+cert) | `/catalog/metrics/register` (MCF intake) + `/catalog/metrics/governed/:uid` (MetricDetailPage — cert + activation inline) | ✅ covered (certification inline; no dedicated cert console) |
| L7 Reader | `/registry/readers` \| `connectors` \| `connections` | ✅ covered |
| **L8 Registration / Directory** | — | ⛔ **BLACK BOX** — no route/page/nav/api for `metric_directory` anywhere in bc-admin |
| **L9 Chain Integrity** | `/catalog/metrics/readiness` (ChainIntegrityDashboardPage) | 🟡 **PARTIAL** — `mcv_chain_status` covered; **`chain_audit_evidence` has no door** |
| **L10 Tenant Onboarding** | `/platform/tenants` (+ `/new-tenant`, `/:slug`) | 🟡 **PARTIAL** — provision step only; `tenant/{configuration,health,scoping,infrastructure}` are Placeholder stubs |

**Workflows:** source onboarding → `/sources/onboard` = 🟡 partial (registers a system; no guided walk across L2–L5 + discovery). Tenant onboarding → `/platform/tenants/new-tenant` = 🟡 partial (provision step only). Neither has an end-to-end guided walk — the **lane-as-workflow** (§5) is the natural home for one.

**Black-box backlog (Track L / door-walk), priority order:**
1. **L8 Registration/Directory — full black box.** No operator door for `metric_directory` at all. Highest-priority missing door.
2. **L9 chain-audit evidence — no door.** Chain integrity is view-only over `mcv_chain_status`; audit-evidence review is unseen.
3. **L10 tenant stubs.** `/tenant/{configuration,health,scoping,infrastructure}` render "Coming Soon" placeholders.
4. **No guided walk for either onboarding workflow** — per-artifact doors only.
5. Minor: certification (L6) has no standalone console (inline on MetricDetailPage); L4/L5 lack a list-level "new contract" door.

These gaps are legibility debt, not runtime blockers — but "no black boxes" is a readiness criterion (*documented* + operator-legible), so closing them is Track-L / door-walk work.

## 5. Design plane vs execution plane (DEC-c48b0f)

- **Design plane = governed & sound.** The ~4 AI authoring panels (BCF concept, MCF metric authoring, MCF audit, contract authoring) judge each artifact's *declaration*. Do not rebuild.
- **Execution plane = ungoverned.** The runtime *couplings* between boundaries (Source→Reader→SO→CO→Snapshot) have no governance — a job can be green while the chain silently breaks. **Three coupling seams** found on the first Kaveri walk, same class (two sides disagree on an identifier → silent no-op):
  - seam #1 `source_key` object-vs-string — **FIXED** (PR #726).
  - seam #2 `sc_contract_id` vs `sc_version_id` (`schema-provisioner.repository.ts`, TSK-35c386) — **OPEN on main** (fix on an unmerged branch).
  - seam #3 admission `writeSourceFact` looks up SC by AC-id → silent `return` (`admission.repository.ts`, TSK-a5f7c5) — **OPEN**.
- **The fix = the lane-as-workflow** (parked design, `artifacts/lanes/onboarding-lane-as-workflow-design.md`): one governed onboarding-run — single-entry, ordered, **fail-closed at every coupling**, idempotent, resumable, run-recorded. Seams #2/#3 are **platform-code** defects → **platform-readiness (Track R) work, fixture-provable**, clear of DB-Foundation.

## 6. Convergence with Platform DB Foundation

Two programs, one proof. **Platform DB Foundation** (`overview/platform-db-foundation.md`, TSK-cc348a) is the "database as a product" (`bc-db`) program that **productionizes L10 / tenant onboarding at scale** (tenant skeleton, fleet runner, onboarding_record, durability, credentials). **Platform readiness (L1–L9 + engine conformance) is separable from it** and provable on a fixture tenant. They **converge at L10 / the Kaveri pilot**, where tenant readiness rides on *both* a ready platform *and* the Foundation's tenant substrate. Notably the pilot itself needs **no schema change** — so the platform-readiness proof does not wait on DB-Foundation W2+.

## 7. The Kaveri pilot — reclassified

The Kaveri pilot (compute one real, evidence-backed metric from the live Kaveri Odoo world) is **Tenant readiness (OLS 15–25)** — the first tenant-readiness milestone — **not** the platform-readiness proof. Its value is confirmation of the *tenant* path on a ready platform. It depends on platform readiness (Track R closed) + DB-Foundation W2 (tenant substrate) + operator credentials. It is currently parked; its diagnostic walk is what exposed the three execution-plane seams (§5), which are themselves platform-readiness work.

## 8. Current gate & sequencing

1. **Close Track R = platform readiness:** land the R units (E6-B/FND-VI, fail-open→fail-closed ×6, dispatcher, scheduler, D575 parity) + govern the execution-plane couplings (fix seams #2/#3), **proven green under the T gates on a fixture tenant**. This is the platform-readiness gate. It is largely decoupled from the live DB-Foundation work.
2. **Then tenant readiness (Kaveri):** onboard the real Kaveri tenant (L10, riding on DB-Foundation W2 + creds) and walk OLS 15–25 to a first KPI.
3. **L** runs parallel to R; **S** follows R.

## 9. Authority & supersession

This SSOT supersedes and consolidates the R4 `platform-functional-refactor-{plan,package}.md` (bc-core) — those become pointers here. The lane section is authoritative per **DEC-a67bae/D590**; the platform/tenant readiness split per **DEC-c9e623** + this program's mandate ADR **DEC-33d436/D606**. Legibility's lane-kit capability-catalog rule (no parallel catalog document) holds. Related programs: Platform DB Foundation (TSK-cc348a), Onboarding Runway Lanes (D581), Runtime Ecosystem (owns the not-a-lane runtime engines).
