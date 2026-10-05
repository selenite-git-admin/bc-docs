---
id: GOV-ERR-004
title: "DEC-d9fa49's metric-activation retirement is enforced only at transitionState; ContractAnalyticsRepository.bulkTransition is a second governance-state writer that bypasses it"
status: open
authority: authoritative
affected: docs/governance/adrs/ADR-d9fa49.md (DEC-d9fa49, F-018) — Decision item 2 (the `transitionState` Gone-class refusal that retires legacy `category='metric'` → `active`; metric activation exclusively the MCF/D541 lane) and item 1(c) (the warning that an unblocked path could reopen metric → active bypassing D541). The retirement's enforcement is incomplete: it covers `transitionState` but not the second governance-state writer `ContractAnalyticsRepository.bulkTransition`.
temporary_governance:
  - Operational control until the remediation lands: `POST /contracts/bulk-transition` must not be used to transition a fact-producing category (`canonical`, `metric`) to `active` or `pending_provisioning`. Risk RSK-314ec1 records the exposure.
  - DEC-d9fa49's refusal and the MCF/D541 certification gate (DEC-c48b0f) remain the authority for metric-contract activation; the only legitimate metric → active path is the MCF lane via `transitionState`.
target_resolution: Route `bulkTransition`'s governance-state writes through the single governed guard (`transitionState` / a shared governed-guard chain), so the DEC-d9fa49 metric refusal, the D541 gate, the fact-producing → `pending_provisioning` redirect, `assertProvisioningComplete`, the grain-lock and the D430 field-integrity checks all apply to it — never a raw `UPDATE`. Tracked on TSK-28678a (Architect erratum + Platform code). On the remediation, this erratum closes.
opened: 2026-10-05
---

# GOV-ERR-004 — DEC-d9fa49's metric-activation retirement is bypassed by `bulkTransition`

## Contradiction summary

DEC-d9fa49 (F-018) retired legacy metric-contract activation: `ContractService.transitionState` throws a Gone-class refusal when `category='metric'` targets `'active'`, and metric activation is exclusively the MCF certification lane (`audit_pending → active` under the C8 gate, DEC-c48b0f). Its item 1(c) explicitly warned that "nothing marks the route retired — a future repair would silently reopen a path to active that bypasses D541 certification."

The substrate realizes exactly that risk through a different door. `ContractAnalyticsRepository.bulkTransition` is a **second** governance-state writer that does not pass through `transitionState`, so its path to `active`/`pending_provisioning` is governed by neither the DEC-d9fa49 metric refusal nor the fact-producing activation gates.

## Implementation behavior (grounded, bc-core `origin/main` cc08875b)

- `ContractAnalyticsRepository.bulkTransition` raw-`UPDATE`s `governance_state_code` directly: `contract-analytics.repository.ts:266-285` (`UPDATE … SET governance_state_code = <toState> … WHERE … governance_state_code = <fromState>`). This is a second writer of `contract.canonical_contract_version.governance_state_code` beside the guarded `updateVersionState` (reached only via `transitionState` / `activateCanonicalUnderLock`).
- `ContractService.bulkTransition` (`contract.service.ts:419`) applies only `assertTransitionContext` + the generic `governanceMachine` edge check (Platform-grounded). It does NOT invoke `transitionState`, so it bypasses: the DEC-d9fa49 `category='metric' → active` Gone-refusal; the fact-producing `active` → `pending_provisioning` redirect; `assertProvisioningComplete`; the canonical grain-lock; and the D430 field-integrity check.
- Reachability (live): `POST /contracts/bulk-transition` (`contract.controller.ts:128`) is `@PlatformOnly()` (class, `:27`) + `@Roles('platform_admin', 'operator')` (`:127`). So a privileged bulk `category='metric'` (or `canonical`) `draft|…→active` reopens the retired metric → active path (bypassing D541) and, for canonical/metric, bypasses provisioning and integrity — a governed-path bypass, mitigated only by privileged-role-only access. Pre-existing (predates DEC-b36e15).

## Temporary governance

Until the remediation lands, `bulkTransition` must not move a fact-producing category (`canonical`, `metric`) to `active`/`pending_provisioning` (operational control; risk RSK-314ec1). DEC-d9fa49's refusal + the DEC-c48b0f certification gate remain the authority for metric activation; the only legitimate metric → active path is the MCF lane through `transitionState`. This erratum is the admissible record of that temporary precedence.

## Resolution state

`open`. The fix is to route `bulkTransition`'s governance-state writes through the single governed guard (`transitionState` / one shared guard chain), never a raw `UPDATE` and never a duplicated copy (guard the class, not the instance), so every governed gate applies on both paths. Tracked on TSK-28678a (Architect erratum + Platform code), risk RSK-314ec1. DEC-d9fa49's decision and every other clause stand unchanged — this erratum corrects only the **completeness** of its enforcement (a second write path existed that the retirement did not cover). On the remediation, this erratum closes.

Surfaced during DEC-b36e15 round-2/3 (gen-9c1607): that ADR's forward-invariant (b) adds the fact-producing draft-skip guard to **both** write paths (the narrow slice the membership binding needs); this erratum carries the **broader** bypass (D541/provisioning/grain-lock/D430) as its own track.

## References

- `docs/governance/adrs/ADR-d9fa49.md` (DEC-d9fa49, F-018 legacy-metric-activation retirement) — Decision items 2 and 1(c).
- DEC-c48b0f (the MCF/D541 C8 certification gate — the authoritative metric-activation lane).
- DEC-b36e15 (platform-plane pool-readiness) — where this bypass surfaced; its (b) guard covers the draft-skip slice on both write paths.
- bc-core `origin/main`: `src/registry/contracts/contract-analytics.repository.ts:266-285`, `src/registry/contracts/contract.service.ts:419`, `src/registry/contracts/contract.controller.ts:27,127-128`.
- DevHub: TSK-28678a (remediation), RSK-314ec1 (risk).
