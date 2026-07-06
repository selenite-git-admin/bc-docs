---
title: "D433 Activation-Gate Fix — change proposal (code-only; NO DDL)"
description: Implementation proposal for DEC-29b518/D433 (D429 Step 4). Three code-only fixes to the contract activation/publication gates — canonical fail-closed when integrity is unverifiable, removal of the vestigial deprecated IntegrityService metric gate (live gate = D305 ChainStatus->MLS-14), and replacing the dead 'released' compatibility lookup with 'active'/findLatestActiveVersion. Service + repository + tests only; NO schema/DDL/migration/data change. Draft proposal — authorizes no coding yet.
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: activation-gates
focus: governance
---

# D433 Activation-Gate Fix — change proposal (code-only)

> **What this is.** The implementation proposal for **DEC-29b518 / D433** (D429 Step 4). **This is a code change only: service + repository + tests. There is NO database change — no DDL, schema, migration, or data mutation.** (The "DBCP" label is kept for sequence continuity; unlike D429 Step 1, nothing here touches the DB.) Scope is gate plumbing + lifecycle vocabulary only. No D430/D431/D432 implementation, no parent/version desync cleanup, no lifecycle state-machine redesign, no MCF materialization.
>
> **Decision status (2026-06-07): LOCKED.** Canonical = **C1-a** (refuse outright; do not trust the dead IntegrityService signal). **Keep** the IntegrityService injection (do not widen the PR). **D430 implementation owns** replacing the canonical fail-closed stub with the real field→concept check. **Accept X4 reactivation** (`released`→`active`/`findLatestActiveVersion`). PR authored from this proposal: Fixes 1-3 + focused tests + gates, opened **holding** (no merge).

---

## Summary of the three fixes

| # | Fix | File | Behavior change | Risk |
|---|---|---|---|---|
| 1 | **X4** — `'released'` → `'active'` lookup (`findLatestReleasedVersion` → `findLatestActiveVersion`) | `contract-version.repository.ts` (+ 1 caller) | **Yes** — reactivates a dormant compatibility/version-increment gate | **Medium** — start enforcing semver/compat on new versions |
| 2 | **X5-metric** — remove the vestigial deprecated IntegrityService metric gate | `contract.service.ts:462-477` | **No** — it was fail-open (always passed); MLS-14/ChainStatus stays | **Low** |
| 3 | **X5-canonical** — fail closed when canonical integrity is unverifiable | `contract.service.ts:526-541` | **Yes** — CC activation goes from always-pass to always-refuse | **Low operationally** (0 active CCs); **couples to D430** |

---

## Fix 1 — X4 vocabulary (`released` → `active`)

**Current** (`contract-version.repository.ts:162-180`): `findLatestReleasedVersion` filters `governance_state_code = 'released'`, a state the lifecycle never sets → always null → the compatibility block never runs. Single caller: `contract.service.ts:349`.

**Proposed:**
- Rename `findLatestReleasedVersion` → `findLatestActiveVersion`; change the filter `'released'` → `'active'`.
  ```sql
  WHERE ${sql.raw(f.sqlIdCol)} = ${contractId}::uuid AND governance_state_code = 'active'
  ```
- Update the single caller (`contract.service.ts:349`): `const latestActive = await this.versionRepo.findLatestActiveVersion(contractId);` and the local references in the block (`latestReleased` → `latestActive`, evidence `hasCompatibilityCheck: !!latestActive`).

**Effect:** for a contract's 2nd+ version, `compareEnvelopes` + `validateVersionIncrement` now run against the current **active** version (first version still skips — no active predecessor). This is the dormant gate coming alive.

**Risk to verify (Medium):** every code path that creates a new contract *version* on a contract that already has an active version will now be subject to compatibility + semver-increment enforcement. **Action in implementation:** grep all `createVersion` call sites + run the full `vitest` suite; confirm no legitimate flow (seeds, generators, MCF) relies on the dormant behavior. (D430/D431/D432 implementations that add versions must satisfy the gate — expected and correct.)

---

## Fix 2 — X5-metric (remove the vestigial gate)

**Current** (`contract.service.ts:462-477`): inside `if (contract?.category === 'metric')`, calls `integrityService.getKpiIntegrity` and throws if `broken > 0`. Because the IntegrityService tables are dropped (D417/D418), `broken` is always 0 → never throws (fail-open). The **real** metric gate is the ChainStatus refresh (488-497) + MLS-14 (507-522) immediately after.

**Proposed:** delete the `getKpiIntegrity` call and its `if (broken > 0)` block (lines 464-477). Keep the `if (contract?.category === 'metric')` wrapper (it also wraps ChainStatus + MLS-14). Net runtime behavior unchanged (the removed gate never blocked); the deprecated dependency is dropped from the activation path.

**`getKpiIntegrity` stays** in `IntegrityService` — still used by `integrity.controller.ts:50` and the test-bench controllers (detail/read), per the decision "keep IntegrityService for detail/read."

---

## Fix 3 — X5-canonical (fail closed) — the one design sub-choice

**Current** (`contract.service.ts:526-541`): `getCanonicalIntegrity` returns `{ summary: { full, partial, broken }, fields }` — and `null` **only** if the CC slug isn't found. With the BF/CF tables dropped, `traceFieldChains` cannot detect breaks, so it reports **`broken: 0`** — a **false-clean**. The gate `if (integrity) { if (broken>0) throw }` therefore never refuses (fail-open). So "fail closed" cannot be a null-check — the signal is *structurally untrustworthy*, not absent.

**Proposed (C1-a, recommended): refuse canonical activation outright.** Replace the gate body with an explicit refusal:
```ts
if (contract?.category === 'canonical') {
  throw new ForbiddenException(
    'Cannot activate canonical contract: field-level integrity is not verifiable under the ' +
    'current substrate (IntegrityService is deprecated and cc_field_mapping/canonical_field/' +
    'business_field were dropped per D417/D418). The canonical field→concept integrity gate ' +
    'is delivered by D430 (DEC-a6258b); CC activation is fail-closed (D429 Step 4 / DEC-29b518) until then.',
  );
}
```
Rationale: honest to the decision ("fail closed when integrity is unverifiable"); the dead signal is not consulted (satisfies the **dead-signal guardrail** — we refuse by policy, not by reading the dead service's empty result). Safe: **0 active Canonical Contracts**, so nothing is blocked operationally.

**Alternative (C1-b): keep calling `getCanonicalIntegrity`, refuse unless positively verified** (e.g., refuse when `null`, or when `fields.length < declared field_selection length`, or a future `verifiedBy: 'd430'` flag is absent). More surgical and leaves the call in place, but relies on detecting degradation from a deprecated service — fragile, and still refuses everything today. **Not recommended** — C1-a is cleaner and the gate is replaced wholesale by D430 anyway.

**IntegrityService injection handling.** With Fix 2 + Fix 3 (C1-a), `contract.service.ts` no longer calls `integrityService` at all. Two options:
- **Keep the constructor injection** (unused in gates), with a `// retained for D430 canonical-gate rewiring` note — **minimal blast radius** (no constructor / `ContractModule` / test-ctor positional-arg changes). **Recommended** for this narrow step.
- Drop the injection — cleaner, but shifts positional constructor args (the test ctor passes it as param 9) and touches `ContractModule`. Defer to D430 (which reworks this gate).

---

## ⚠️ Cross-dependency: D433 canonical fail-closed blocks D430's greenfield CC

C1-a refuses **all** CC activation. D430's implementation authors and **activates** a greenfield Customer Invoice CC. Therefore **D430's implementation must replace this fail-closed refusal with the real field→concept integrity check** — otherwise D430 cannot activate its CC. This is the intended sequence (the Step-4 study flagged the coupling), but it is a hard ordering constraint:
- If **D433 lands before D430**: CC activation is fully blocked — fine, 0 active CCs, nothing to activate yet.
- **D430's DBCP owns** swapping the D433 canonical stub for the real check. Recommended build order therefore keeps D430 *after* D433 but treats "replace the canonical gate" as an explicit D430 task.

---

## Test plan (the blast radius)

**Update** `contract.service.transitionState.spec.ts`:
- **C1** (ordering, line 117-133): remove `'integrity'` from the expected order array (the metric IntegrityService step is gone). New order: `cfTrust → markForSupersession → cfTrust → chainStatusForVersion → mls14 → updateVersionState`.
- **R1** (line 146-153): drop the `kind === 'integrity'` assertion (metric gate removed); keep chainStatus + mls14 assertions.
- **R4** (line 190-200): currently activates a **canonical** successfully — under C1-a it must now **reject** with the fail-closed `ForbiddenException`. Rewrite to `expect(...).rejects.toBeInstanceOf(ForbiddenException)` + message contains "fail-closed"/"D430".
- C2, R2, R3, R5, R6, R7: unaffected (they don't depend on the metric integrity step firing, or already assert it absent).

**Add:**
- Metric activate → IntegrityService **not** called; activation still gated by ChainStatus + MLS-14 (and succeeds when those pass).
- Canonical activate → fail-closed refusal (message cites D430 + DEC-29b518).
- **X4 compatibility** (in `createVersion`/`compatibility.spec` context): with an existing **active** prior version, a backward-incompatible new version (or wrong semver increment) is now **rejected**; first version (no active predecessor) still passes. This proves the dormant gate is live.

**Gates:** `tsc` (strict) + `eslint` (block in bc-core) + `npx vitest run`. Expect the transitionState spec to need the updates above to stay green.

---

## Rollback

Code-only → **`git revert`** the merge commit. No DB/DDL/data to undo; no migration. Zero data risk. (Contrast D429 Step 1, which needed rollback DDL — D433 needs none.)

## Foundation gate

- **Repair location: B (publication-gate discipline) implemented at D (activation service).** The change restores the gate's purpose (do not promote unverifiable/incompatible versions to `active`) and aligns lifecycle vocabulary.
- **Dead-signal guardrail honored:** canonical fail-closed refuses *by policy*, not by inverting the dead IntegrityService's empty result. Metric removal drops a dead gate, leaving the live SSOT gate (ChainStatus→MLS-14).
- No DB row edits; no data mutation; reads still do not trigger evaluation.

## Scope guard / explicitly NOT in this change

- No D430/D431 (the real canonical/observation field→concept checks); no D432 (legacy-authoring guard).
- No parent/version desync cleanup. No lifecycle state-machine redesign. No MCF materialization. No DDL/schema/DB/data.
- `IntegrityService` retained for detail/read (integrity.controller, test-bench).

## Proposed PR shape (on operator go — not now)

1. Branch off `bc-core` main.
2. Fix 1 (repository rename + filter + caller), Fix 2 (remove metric gate), Fix 3 (canonical fail-closed, C1-a; keep injection).
3. Update + add tests (above).
4. Gates: tsc + eslint + vitest.
5. Open PR **holding** (no merge) with this DBCP linked; report exact files/tests; await review.

## Decisions taken (locked 2026-06-07)

1. **Canonical = C1-a** — refuse outright with an explicit D430/field-concept-integrity message; do **not** trust the dead IntegrityService signal.
2. **Keep the IntegrityService injection** for now — do not widen the PR by removing dependencies.
3. **D430 implementation owns** replacing the canonical fail-closed stub with the real canonical field→concept integrity check (CC activation resumes under D430).
4. **Accept X4 reactivation** — replace `released` with `active`/`findLatestActiveVersion` so compatibility + version-increment checks run.

## Scope guard

Draft proposal. No code/schema/DB/DDL/service change made. No PR opened. MCF materialization remains paused. This proposal recommends; the operator approves; only then is the PR authored (holding, for review).
