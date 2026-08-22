---
id: demo-estate-program-status
title: "Demo-Estate Simulator — bc-demo v2.1 program status (as-built current state)"
status: approved
authority: derived
depends_on: [demo-estate-simulator-requirements, demo-estate-max-coverage-rescope, demo-estate-metric-coverage, demo-estate-module-coverage]
governing_sources:
  - D566 / DEC-40b510 (bc-demo v2 simulator-as-product — the authority)
  - "v2.1 program design (Codex-accepted, bound to bc-demo 58c07de)"
  - "operator direction 2026-08-14: ensure the program is implemented + documentation is current"
---

# Demo-estate simulator — program status (as-built)

This is the **living current-state SSOT** for the bc-demo demo-estate simulator program. It reconciles
the two design-time authorities — the requirements (`demo-estate-simulator-requirements.md`, D566) and
the Codex-accepted v2.1 program design (bound to bc-demo `58c07de`) — against **what has actually been
built**. The accepted design contract is immutable; where execution went beyond it (max-coverage, U6)
or diverged from it (CRM), that is recorded here and mirrored in the design repo's as-built addendum
(`bc-demo/estates/demo-mfg-in/V2.1-program-design.md`).

> **One-line status (2026-08-14):** v2.0.0 **released + accepted**; v2.1 **substantially implemented**
> and proven as a green 41-month release candidate (**rc3**), economics in-band and U6 statutory-filing
> coverage real; **not yet tagged v2.1.0** (operator sign-off gate) and **not cut over** (operator gate).
> Remaining code work is the D1 harness tail (5 phased surfaces) plus optional hard-gate promotion.

## Releases

| Release | World | Commit / tag | State |
|---|---|---|---|
| **v2.0.0** | `kaveri_ent` (41mo) | tag `v2.0.0` @ `066b5f5` | ✅ Released + Codex-accepted-with-boundary (bound to tag target) |
| v2.1.0-rc2 | `v2rwf2` (41mo) | evidence `v2.1.0-rc2` @ `c6b02d3` | ✅ Green reference; honest-but-over-band economics; no filing |
| **v2.1.0-rc3** | `v2rwrc3` (41mo) | evidence `v2.1.0-rc3`, build code `ccbbbdc`, HEAD `67caa7e` | ✅ **Release candidate** — economics in-band + U6 filing; **untagged** |

**rc3 headline:** BUILDDONE GREEN, 41 months (2023-04 → 2026-08, three full FYs + current FY), 5,155
events, all 8 R-13 acceptance criteria pass, idempotent. Per-FY PAT **6.77 / 6.77 / 10.75%** (all inside
the 0.04–0.15 gate; realistic 7–11% sector arc). U6 filing coverage real: e-invoice 2,223/2,223,
e-waybill 2,223 native records, GSTR 123. Evidence hash-bound (bundle sha256 `714414af…`).

## Implementation status by design phase

Legend: ✅ done · 🟡 partial · ⏸ deferred (by design or operator) · 🔒 operator-gated

### Phase 0 — Harness foundation
| Item | Status | Notes |
|---|---|---|
| D1 closed gate-manifest meta-test | 🟡 | First **2 phases accepted** (universal×4 + close_act + 3 scoped batteries + ac_verdicts + first production-dispatch flip). **5 phased surfaces remain**: ops/preflight, adapter provisioning refusals, writer/liveness, registry↔test linkage, C1–C6/D7 controls. |
| D2/D3 preflight & env hardening | 🟡 | preflight exists + volume-relative reval guard (U1); PID-lease writer / measured-floor items not fully split out. |
| D6 auto-derived provenance | ⏸ | provenance still partly hand-written; TSK-9b6c60. |
| D7 R0 governance (cutover) gate | 🔒 | Built as design; **invoked only at cutover** — operator-gated. |

### Phase 1 — Structure, taxonomy & identity
| Item | Status | Notes |
|---|---|---|
| C3-identity (join-key schema) | ✅ | Mechanism + registry + catalog + live wiring. Estate-global CUST-/VEND-/ITEM-/RM-/SA- ids, append-only journal, bijective content↔registry, Odoo carriers (`res.partner.ref`, `product.default_code`). |
| C5 profile taxonomy `mfg-in`→`mfg-in-auto-comp` | ⏸ | Post-tag cleanup; TSK-a48d0f. |
| C4 profiles/ out of code tree | ⏸ | Post-tag cleanup; TSK-3896e8. |

### Phase 2 — World richness
| Item | Status | Notes |
|---|---|---|
| C1 roster density + character | ✅ | 100 CUST / 37 VEND / 30 ITEM / 24 RM / 6 SA; personalities, terms, credit, multi-level BoM. Live-validated rc2/rc3. |
| C2 treasury (directors' loan + CC/OD) | ✅ | Live-validated **and** statutory-audited by Codex (1,801/1,801 checks, zero findings). Capitalisation-only WCF; drawing-power haircuts. |
| D4/D5 world-shape gates | 🟡 | reval guard volume-relative (U1); explicit producibility/allocation/loan-classification gates not yet named. |
| **Max-coverage U1–U5** (beyond design) | ✅ | U1 volume-relative reval guard; U2 restored workorders; **U3 CRM**; U4 HR (15 depts / 4,985 employees); U5 scrap/quality (123). |
| **CRM** | ⚠✅ | Design said **DEFERRED** (measured-demand); **built** under max-coverage U3. Recorded divergence — the rich-exhaust doctrine superseded the deferral. |

### Beyond the design contract (max-coverage + calibration, 2026-08-13/14)
| Item | Status | Notes |
|---|---|---|
| U6 statutory filing (e-invoice / e-waybill / GSTR) | ✅ | Converts limitation **L-007** into real exhaust. **Synthetic deterministic artifacts — no live IRP/GSTN/NIC.** Acts fail-soft-guarded (candidate for hard FR-9 promotion). |
| Economics re-calibration | ✅ | conversion 0.70 / real-share 0.90 / capex 0.06 / term-loan share 0.18; per-FY PAT in band; `net_margin_band` tax-double-count bug fixed. |
| Offline P&L projector (pre-build gate verdict) | ✅ | `tests/build/project_pl.py` projects net/gross/FG margin, DSO/DPO/inventory-days, expense-structure, revenue-anchor, interest, tax before an 8-hour build. Validated ≤0.5pt vs live. |

### Phase 3 — Cross-system capstone
| Item | Status | Notes |
|---|---|---|
| C6 adapter boundary + C3-projection | ⏸ | D524-gated (MS-BC second adapter); **does not block v2.1.0** by design. |

### Phase 4 — Release & cutover
| Item | Status | Notes |
|---|---|---|
| v2.1.0 tag | 🔒 | rc3 is ready; tag package prepped; **applying the tag is an operator act**. |
| Cutover `pilot_ent → kaveri_ent` | 🔒 | Enterprise activation transfer + P3 secret rotation + D7 gate — operator-only. |

## Deferred candidates (explicit — not gaps, not oversights)

| Candidate | Task | Why deferred |
|---|---|---|
| **Budget + demand/forecast** (`account_budget` + forecast series) | TSK-26d349 | **Not a v1-parity restore** — v1 mfg-in carried neither. A demo-needs addition that would unlock **budget-variance / forecast-accuracy** metric demos. Additive content, no new adapter. Sequenced after the accepted content members. |
| Profile taxonomy / profiles-out structure cleanup | TSK-a48d0f, TSK-3896e8 | Post-tag mechanical cleanup. |
| FD sweeps, inter-company, IGST/inter-state, multi-op BoM/overhead | (parity DEFERRED block) | Reasonable exclusions for a finite rich-world release; narrative claims none as realized. |
| CRM funnel depth (velocity/stages) | TSK-7a76ae | Base CRM built (U3); deeper funnel restore on demand. |
| Reader / contract-chain / metrics (platform side) | X6 | Platform-side OC/CC + metrics are HELD (D555); the world emits the exhaust, metric coverage grows against it. |

## Known non-blocking carries (into any tag)
1. **Stale `clean-break` verifier check** — the RosterCatalog authors realistic Indian metal-industry
   names that collide with an obsolete v1 forbidden-list; the check is obsolete for the v2 era and
   should be modernised (2 verifier FAILs in rc3 are this + the reval note, both adjudicated).
2. **Deferred reval signal** — perpetual SV runs ~26% hot vs recomputed AVCO physical; **1.5% of PBT**,
   operator-deferred for root-cause later; immaterial to the release.

## Source-of-truth pointers
- **Authority:** `demo-estate-simulator-requirements.md` (D566)
- **Accepted v2.1 design contract:** `bc-demo/estates/demo-mfg-in/V2.1-program-design.md` (+ its as-built addendum)
- **Coverage doctrine:** `demo-estate-max-coverage-rescope.md`, `demo-estate-metric-coverage.md`, `demo-estate-module-coverage.md`
- **rc3 evidence:** `bc-demo/estates/demo-mfg-in/evidence/v2.1.0-rc3/` (PROVENANCE, VERIFIER, COVERAGE, hash-bound)
