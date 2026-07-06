---
title: "Activation / Publication Gates — fail-open audit (X5/X4), read-only study"
description: D429 Step 4. A read-only audit + classification of every gate that decides whether a contract version may become active/released, grounding X5 (degraded fail-open activation integrity gate reading dropped tables) and X4 (dead compatibility gate filtering a 'released' state the lifecycle never sets). Surfaces the dead-signal trap (naive fail-closed would brick all activation because the tables are permanently dropped) and recommends a narrow fix: stop trusting the dead IntegrityService signal (metric backstopped by the D305 ChainStatus/MLS-14 SSOT; canonical fail-closed or deferred to D430) + align the 'released'->'active' vocabulary. Authorizes no code/schema/DB/DDL/service change — held.
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: activation-gates
focus: governance
---

# Activation / Publication Gates — fail-open audit (X5 / X4), read-only study

> **What this is.** D429 **Step 4**. A read-only audit + classification of every gate that decides whether a contract version may become `active`/released, grounding audit findings **X5** (fail-open activation integrity gate) and **X4** (dead compatibility gate). It **authorizes nothing** — no code/schema/DB/DDL/service change; no MCF materialization; D430/D431 not solved here; parent/version desync not touched.
>
> **Method.** Three read-only subagents over `bc-core` (activation/transition gate inventory + X4; IntegrityService deep-read + ChainStatus wiring for X5; adjacent publication gates + test blast radius), file:line evidence retained.
>
> **Decision status (2026-06-07): LOCKED.** Recorded in the Step-4 ADR. Canonical **X5-C1** (fail closed now; safe — 0 active CCs; real CC field→concept check lands with D430); metric **X5** (remove the vestigial/deprecated IntegrityService metric gate — live gate is D305 ChainStatus → MLS-14); **X4** (replace the dead `'released'` lookup with `'active'`/`findLatestActiveVersion` so compatibility + version-increment checks run). Scope = gate plumbing + lifecycle vocabulary only; IntegrityService kept for detail/read contexts; no D430/D431, no parent/version desync cleanup, no lifecycle state-machine redesign. Implementation deferred to a DBCP (with the dead-signal guardrail); MCF materialization remains paused.

---

## Headline

Both findings confirmed — and X5 is **narrower and trickier** than the audit framed it:

- **X5** — the deprecated `IntegrityService` activation gate reads three **permanently-dropped** tables (`cc_field_mapping`, `canonical_field`, `business_field`; D417/D418) → empty result → `broken = 0` → the gate never refuses (**fail-open**). **But metric activation is backstopped** by the live D305 SSOT chain (`ChainStatusService` pre-activation refresh → **MLS-14** gate). **Canonical activation has no backstop** — it is the genuinely exposed fail-open path.
- **X4** — the compatibility / version-increment gate filters `governance_state_code = 'released'`, a state the lifecycle **never sets** (it uses `draft/review/approved/active/superseded`). The lookup always returns null, so the entire compatibility check silently no-ops (**dead → fail-open**).

**The trap (most important finding).** A naive "fail-closed when integrity data is unavailable" would **brick all activation**, because the IntegrityService data source is gone *permanently* (D417/D418 dropped the tables) — "unavailable" is the steady state, not an outage. The correct fix is to **stop trusting the dead signal**, not to invert the dead gate's default:
- **Metric:** the IntegrityService metric gate is **vestigial** — remove it; the real gate is already ChainStatus → MLS-14 (the D305 SSOT). Net behavior unchanged (it was passing everything anyway); the gating becomes honest.
- **Canonical:** there is **no SSOT gate** — fail **closed** here (refuse CC activation when integrity is unverifiable), which is safe today (0 active CCs; the next CC is the D430 greenfield ARPI CC that *will* carry a verifiable signal). The real CC integrity check (field→concept verification) lands with **D430**.
- **X4:** pure correctness — align the filter `'released'` → `'active'` so the compatibility + version-increment check actually fires.

---

## Classified gate inventory

| Gate | file:line | Stage | Blocks? | Classification |
|---|---|---|---|---|
| Governance state-machine transition | `contract.service.ts:41-47, 455` | activation | **yes** | **live-and-correct** |
| D284 source-veracity gate | `contract.service.ts:83-100` | createContract | yes | live-and-correct *(not activation)* |
| D244 meta-schema validation | `contract.service.ts:346` | createVersion | yes | live-and-correct *(admission)* |
| **Compatibility / version-increment (X4)** | `contract.service.ts:349-375` via `contract-version.repository.ts:175` | createVersion | **no — silently skipped** | **dead-unreachable → fail-open** |
| **Metric integrity gate (X5)** | `contract.service.ts:462-477` (`integrityService.getKpiIntegrity`) | activation | **no — null⇒pass** | **live-but-fail-open** *(vestigial; MLS-14 backstops)* |
| Metric pre-activation ChainStatus refresh | `contract.service.ts:488-497` | activation | yes (aborts on compute fail) | **live-and-correct** (D305 SSOT) |
| **MLS-14 gate** (semantic_class_collapse, chain_not_complete) | `contract.service.ts:507-522`; `mls/gate/mls14-activation-gate.service.ts:104-172` | activation | **yes** | **live-and-correct** *(the real metric blocker)* |
| **Canonical integrity gate (X5)** | `contract.service.ts:526-541` (`integrityService.getCanonicalIntegrity`) | activation | **no — null⇒pass** | **live-but-fail-open** *(no backstop — exposed)* |
| OC 7-key body completeness gate | `contract.service.ts:543-558` | activation | yes | live-and-correct |
| D305 post-activation refresh (async) | `contract.service.ts:575-578` | post | no (by design) | live-but-fail-open *(non-blocking; acceptable)* |
| D369 activation fanout (async) | `contract-activation.service.ts:65-182` | post | no (by design) | live-but-fail-open *(non-blocking)* |
| Intervention activation | `contract-activation.service.ts:225-239` | post | — | **dead-unreachable** (stub; no IC) |
| MCF governance transitions (submit/approve/activate) | `mcf-cert-writer.service.ts:967, 1127, 1279` | MCF activation | yes | **live-and-correct** *(separate substrate)* |
| M14 publication-activation preconditions | `mcf-publication-activation.controller.ts:82-108` | MCF activation | yes | live-and-correct |
| BCF registry-publication (C5/F3) | `registry-publication.service.ts:120-165` | BCF publication | yes | live-and-correct |
| `IntegrityService` class | `integrity.service.ts:2-7` | — | — | **legacy-only** (`@deprecated` D305; 5 known bugs) |
| `compatibility.spec` `'released'` fixture | `compatibility.spec.ts:33` | — | — | **test-only** (dead path) |

---

## X5 — the fail-open chain, precisely

1. D417/D418 dropped `cc_field_mapping` / `canonical_field` / `business_field` (`docker/redesign/02-platform-tables/02-contract.sql:7-16`).
2. `integrity.service.ts` still queries them: `getCfToBfMap` (~1001-1021) and `lookupStandardFields` (~1269-1313) return **empty Maps** when no rows.
3. Empty maps → `getKpiIntegrity` / `getCanonicalIntegrity` report `summary.broken = 0`.
4. The caller: `if (integrity) { if (broken > 0) throw }` (`462-477` metric, `526-541` canonical) → `broken=0` never throws → **activation proceeds**.
5. `IntegrityService` is `@deprecated` (D305 / DEC-bebaec): *"Kept for (1) activation gates in contract.service.ts, (2) per-MC detail views. Will be migrated fully to D305."*

**Asymmetry that matters:** for **metric**, the live `ChainStatusService.refreshChainStatusForVersion` (488-497) + **MLS-14** gate (507-522) read the persisted `chain_status` SSOT and *do* block on `chain_not_complete` / `semantic_class_collapse`. So the metric IntegrityService gate is redundant and misleading, not load-bearing. For **canonical**, there is no ChainStatus/MLS-14 equivalent in the activation path → the fail-open IntegrityService gate is the *only* CC integrity gate, and it never refuses.

---

## X4 — the dead compatibility gate, precisely

- Lifecycle enum: `draft/review/approved/active/superseded` (`types/governance.ts:5-10`); state machine routes never produce `'released'` (`contract.service.ts:41-47`).
- `'released'` exists only as a **display label** in `seed-master-statuses.ts:31` — never written to `governance_state_code`.
- `findLatestReleasedVersion` (`contract-version.repository.ts:175`) → `WHERE governance_state_code = 'released'` → always 0 rows → null.
- `createVersion` (`contract.service.ts:349-375`): `if (latestReleased) { compareEnvelopes(...); /* version-increment validation */ }` — null ⇒ the whole block is skipped. **Any** new version can be created with any compatibility profile / any version bump, unchecked.

---

## Recommended narrow fix

| Finding | Narrow fix | Notes |
|---|---|---|
| **X4** | Align vocabulary: `findLatestReleasedVersion` filter `'released'` → `'active'` (rename → `findLatestActiveVersion`), so the compatibility + version-increment check fires against the current active version. | Pure correctness. No live test depends on the dead path (the `compatibility.spec` `'released'` fixture is test-only). |
| **X5 — metric** | **Remove the vestigial `IntegrityService` metric gate** (462-477); rely on the existing ChainStatus → MLS-14 SSOT. | Net runtime behavior unchanged (the gate passed everything); removes a deprecated, misleading dependency. **Test update:** `contract.service.transitionState.spec.ts` ordering assertions (C1/C2) reference the integrity step and must be updated — test-only blast radius. |
| **X5 — canonical** | **Fail closed:** replace the silent `null ⇒ pass` with an explicit refusal when CC integrity is unverifiable. | Safe today (0 active CCs; next CC is D430 greenfield). **Couples CC activation to D430 delivering a verifiable signal** — see options below. |

**The dead-signal guardrail (call out in the DBCP):** do **not** make `IntegrityService` "fail closed when its tables are absent" — the tables are permanently dropped, so that bricks all activation. Fail-closed must be keyed to *"no valid SSOT signal"*, not *"the dead service returned empty."*

**Canonical sub-decision (needs operator lock):**
- **X5-C1 (recommended): fail closed now.** CC activation refuses until a verifiable signal exists. Costs nothing operationally (0 active CCs) and is honest. The real CC integrity check (field→concept) arrives with D430.
- **X5-C2: leave canonical fail-open but documented**, and let D430 deliver the real CC gate (no interim CC change). Avoids the D430 coupling but knowingly leaves a fail-open gate until D430.

---

## Blast radius (tests)

- `contract.service.transitionState.spec.ts` (C1/C2 ordering, R1-R5): assert the gate sequence incl. the integrity step — **will need updating** if the metric gate is removed (test-only).
- `integrity.service.spec.ts`: pins the `status_code AS "status"` column alias — unaffected by gate removal; the service stays for detail views.
- `compatibility.spec.ts:33`: uses a `'released'` fixture but does not exercise the live path — **safe** under the `'released'`→`'active'` fix.
- MCF specs (`mcf-cert-writer`, `mcf-publication-activation`): **orthogonal** — untouched.

---

## What to preserve / what NOT to do

- **Preserve:** the state-machine transition gate, OC 7-key gate, ChainStatus refresh, MLS-14, MCF governance gates, BCF publication, and the non-blocking async fanouts (D305/D369) — all live-and-correct.
- **Preserve valid metadata/state transitions** (supersession, metadata-only updates) — untouched.
- **Do NOT** solve D430/D431 here (the canonical field→concept *verification* is D430; this step only stops the gate from silently passing).
- **Do NOT** clean the parent/version desync here.
- **Do NOT** "fail closed inside IntegrityService" (the dead-signal trap).
- **Do NOT** resume MCF materialization.

---

## Foundation gate (for the eventual fix)

- **Repair location:** the **publication/activation gate** — governance of the promotion to `active`. Closest to **B** (publication-gate discipline) implemented at **D** (the activation service). The fix restores the gate's purpose (do not admit unverifiable state into `active`) and aligns vocabulary; it does not compensate for an upstream semantic gap at a lower layer.
- **Invariant alignment:** supports Invariant I/VI — only verifiable, evidenced contract versions reach `active`. Removing a dead gate + failing closed on a missing SSOT signal is honest gating, not lower-layer compensation. No DB row edits; no data mutation.

---

## Relationship to the D429 sequence

Step 1 (immutability) ✅ applied. Step 2 — canonical identity **D430** + observation identity **D431** ✅ decided. Step 3 — guard legacy MC door **D432** ✅ decided. **Step 4 (this study)** makes the activation/publication gates honest (no silent pass on a dead signal; correct compatibility vocabulary). Note the **canonical coupling**: X5-C1 ties CC activation to D430 delivering a verifiable field→concept signal — which is the intended sequence (the greenfield ARPI CC is authored under D430). Step 5 (resume MCF materialization) remains paused until 1–4 land.

## Decisions taken (locked 2026-06-07)

1. **Canonical X5-C1 — fail closed now** when canonical integrity is unverifiable (replace the silent `null ⇒ pass` at `contract.service.ts:526-541` with an explicit refusal). Safe because there are **0 active Canonical Contracts**; D430 later supplies the real canonical field→concept integrity check (CC activation is thereby coupled to D430 — the intended sequence).
2. **Metric X5 — remove the vestigial/deprecated IntegrityService metric gate** (`contract.service.ts:462-477`). The live metric gate is the D305 SSOT chain: ChainStatus refresh (488-497) → MLS-14 (507-522). Net runtime behavior unchanged.
3. **X4 — replace the dead `released` lookup with `active`** (`findLatestReleasedVersion` → `findLatestActiveVersion`, `contract-version.repository.ts:175`), so the compatibility + version-increment check in `createVersion` (`contract.service.ts:349-375`) actually runs. (Expect it to begin enforcing semver discipline on new versions — previously dormant.)
4. **Scope = gate plumbing + lifecycle vocabulary only.** Keep IntegrityService only for detail/read contexts if still needed. Do NOT implement D430/D431; do NOT clean parent/version desync; do NOT redesign the lifecycle state machine; do NOT resume MCF materialization.

**Dead-signal guardrail (mandatory in the DBCP):** fail-closed MUST key on *"no valid SSOT signal,"* NEVER on *"the deprecated IntegrityService returned empty"* — the IntegrityService tables are permanently dropped (D417/D418), so inverting the dead gate's default would brick all activation. Recorded in the Step-4 ADR; implementation deferred to a later DBCP (note `transitionState.spec` ordering updates). No code/schema/DB change here.

## Scope guard

Read-only audit. No code/schema/DB/DDL/service change, PR, or panel. No MCF materialization. Runtime objects in `tbc_sandbox1_dev` not queried. This memo recommends; the operator locks; only then is a fix DBCP drafted.
