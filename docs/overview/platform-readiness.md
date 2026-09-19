---
title: Platform Readiness & Legibility — Overview
status: drafting
date: 2026-09-19
anchor_task: TSK-4b2404
detail: implementation/platform-readiness-program.md
related: overview/platform-db-foundation.md
---

# Platform Readiness & Legibility

**Goal:** make the platform's metric-producing **mechanics** ready — `streamlined · governed · documented · proven-once-end-to-end` — and keep the program **legible**. Formerly "functional refactor"; renamed after an August stall-analysis found code structure caused ~9% of stalls, so structural refactor is *not* the remedy.

**Readiness is two-layered** (Object Life States, DEC-c9e623):
- **Platform readiness** = OLS 01–14 / lanes **L1–L9** + runtime-engine conformance — provable on a **fixture/sandbox tenant** (no customer onboarding). *This is the arc this program owns.*
- **Tenant readiness** = OLS 15–25 / lane **L10** + the runtime — the **Kaveri pilot**; a downstream milestone that rides on platform readiness **and** the Platform DB Foundation program. *Not the platform gate.*

**Three cuts of the space** (kept distinct for legibility):
- **4 tracks** (work axis): **T** ✅ closed · **R** 🟡 the gate (runtime Foundation conformance) · **L** legibility (parallel) · **S** structure (deferred until R).
- **10 lanes** (ownership axis, LOCKED DEC-a67bae/D590): L1 Source Catalog … L10 Tenant Onboarding — artifact families, strict one-lane-per-surface. Source-onboarding and tenant-onboarding are **workflows** over the lanes, not lanes.
- **Design vs execution plane** (DEC-c48b0f): the authoring panels (design) are governed; the runtime **couplings** (execution) are not — the lane-as-workflow is the missing governance.

**Current gate:** close **Track R** — land the R units (E6-B/FND-VI evidence emission, fail-open→fail-closed, dispatcher, scheduler retirement, D575 parity) and govern the execution-plane couplings (fix the open seams), proven green under the T gates on a fixture tenant. Then tenant readiness (Kaveri) rides on it.

**Converges with** the [Platform DB Foundation](platform-db-foundation.md) program (bc-db, TSK-cc348a), which productionizes tenant onboarding (L10) at scale; the two meet at the Kaveri pilot.

→ Full program detail, track scope, the 10-lane table, seams, and sequencing: **[implementation/platform-readiness-program.md](../implementation/platform-readiness-program.md)**.
