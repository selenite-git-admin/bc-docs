---
title: Platform Readiness & Legibility — Overview
status: drafting
date: 2026-09-19
anchor_task: TSK-4b2404
detail: implementation/platform-readiness-program.md
related: overview/platform-db-foundation.md
---

# Platform Readiness & Legibility

**Destination:** the platform can take a *real* source system, run it through the whole
governed runway, and produce a first **trusted** metric — and we've **proven it once,
end-to-end**. Streamlined · governed · documented · proven. Everything else is a means to this.

**What "proven" means (decided 2026-09-19):** *platform readiness* = a **fixture/engine-conformance
proof** (fixture data crosses every boundary to a snapshot with emitted evidence, all fail-closed,
on a sandbox tenant — no customer needed). *Demo readiness* = platform readiness **+ a thin
real-source (Kaveri) slice**, a named downstream milestone that rides on it — **not** the platform
gate. (Corrects the earlier framing that used the Kaveri tenant walk as the platform proof.)

**The platform functions (the stable spine):**
- **Shared:** S1 Auth · S2 User/access · S3 Tenant lifecycle · S4 Pricing · S5 Operator console
- **Runway (10 lanes):** L1 Source Catalog … L10 Tenant Onboarding (LOCKED, DEC-a67bae/D590)
- **Runtime & cross-cutting:** Runtime engine · Evidence/audit · Tenant self-service · **A1 Action/Intervention** *(design pending)*
- **Parked as cosmetic:** design-system/visual-language → a future dedicated UI refactoring program (not a function).

Each function is scored **backend / DB / UI** and carries its governing ADRs with real status —
a function with thin/no ADRs is itself a finding. Full matrix in the detail doc.

**Where we stand (grounded 2026-09-19, synced same day):** the metric authoring/certification
path is green (L1–L3, L6, L7). The **runtime execution-plane seam class is CLOSED** — all three
silent coupling seams merged to bc-core `main` (fail-closed, disposable-DB CI regression). What
remains on Track R: E6-B's first-*observed* evidence emit (FND-VI, **deferred** — rides on a real
metric run + operator-only auditor-store health) and the by-design fail-open follow-ups.
Legibility gaps (missing operator doors: L9 chain-audit, S2 users; the L8 Metric Registry UI shipped, PR #45) are
co-requisite, *not* cosmetic. L10's onboarding lane is green; its four operational tabs are
reclassified to S5 (deferred). S4 pricing is deferred-by-decision (v1 flat band, no plan binding)
and S2 RBAC unbuilt — neither blocks a compute demo.

**Three cuts of the space** (kept distinct for legibility): **4 tracks** (work axis — T ✅ / R 🟡
the gate / L parallel / S deferred); **the functions** (what the platform does); **design vs
execution plane** (DEC-c48b0f). A **unit ledger** with a mandatory design/execution intake gate
ties each unit of work to a function and a piece of the distance-to-destination.

**Current gate:** close **Track R** (seams **done ✅**; remaining = E6-B first-observed emit —
deferred — and the by-design fail-open follow-ups; proven green on a fixture tenant) **and**
Track L's no-black-boxes doors (L8/L9 doors, S2 users). Then demo readiness (the thin Kaveri
slice) rides on it.

**Converges with** the [Platform DB Foundation](platform-db-foundation.md) program (bc-db,
TSK-cc348a), which productionizes tenant onboarding at scale; the two meet at the Kaveri demo
milestone.

→ Full detail — functions, per-function ADRs, the readiness matrix, the seams, the unit ledger,
and the punch-list: **[implementation/platform-readiness-program.md](../implementation/platform-readiness-program.md)**.
