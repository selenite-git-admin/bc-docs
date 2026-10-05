---
uid: DEC-b36e15
title: "Platform-plane pool-readiness binds to the authoritative canonical-contract declaration, not the tenant-provisioned 'active' state"
description: "Platform-plane pool-readiness binds to the authoritative canonical-contract declaration, not the tenant-provisioned 'active' state"
status: decided
date: 2026-10-05T13:37:21.367Z
project: platform
domain: platform
subdomain: canonical-contract-lifecycle
focus: plane separation (platform vs tenant) for metric directory pool-readiness
---

# Platform-plane pool-readiness binds to the authoritative canonical-contract declaration, not the tenant-provisioned 'active' state

## Context

See decision text below.

# Platform-plane pool-readiness binds to the authoritative canonical-contract declaration, not the tenant-provisioned 'active' state

**Status:** decided. Authority: the operator approved the plane-split repair, relayed by the Chief Controller, 2026-10-05 (if a desk grant was recorded for this decision, cite its grant_id here for parity with DEC-ec1434). Author: Architect SES-b9b0ef. Grounding study: barecount-devhub `artifacts/architect/clean-directory-2026-10-03/RULING-plane-clean-platform-pool-vs-tenant-provisioning-2026-10-05.md` @3a313592.

## Context

The Oct-2 objective (metric pool → Certified/Released) is a PLATFORM-plane act (define → certify → release; it never produces a value). Phase A cleans the metric directory to entry-ready/clean terminal states platform-side; tenant evaluation/reporting is the tenant plane (Phase C+).

The canonical-v2 lifecycle makes a FACT-PRODUCING canonical contract version's `governance_state_code = 'active'` depend on every AFFECTED (bound) tenant being provisioned — the provisioning-readiness mechanism labelled **D575 Unit-3 F1** in bc-core `contract.service.ts` (distinct from **ADR-09fb2f**, which is the related D575 platform prerequisite: tenant evidence-chain immutability + runtime identity separation). A target of `active` is redirected to `pending_provisioning`, and `pending_provisioning → active` is fail-closed until the provisioning worker has provisioned every affected tenant (bc-core `contract.service.ts:946-1067`; `provisioning-readiness.service.ts:6-23`, which rules "zero affected tenants ⇒ ready"; affected tenants are a reverse-walk via `contract_binding`, `contract-activation.service.ts:70,89-90`). The platform-plane pool-readiness / G4 loci read the grain's active CC in the chain-status and declaration readers, each currently keyed on `governance_state_code = 'active'`: `mcv-chain-status.service.ts` `grain_cc_active` (via `loadActiveCcEntities` + `loadCcCurrencyEntities`), `mcf-chain-declaration-reader.readActiveCcDeclarations`, `audit-panel-canonical-facts.reader`, and `chain-audit.readResolvedCcBody` (Platform-verified first-hand, 2026-10-05). Note: `ccv2-canonical-resolver.service.ts:584` (`loadActiveCc`, via `resolveForContract` — the TENANT CO-production path, called with a `tenantSlug`) also reads `'active'`, but that is tenant fact production, **not** platform pool-readiness, and it is explicitly OUT of scope of this decision (see Decision → Scope).

For a grain NOT bound to a live tenant the CC reaches `active` with no provisioning. For a grain bound to a live tenant (customer_invoice ↔ Kaveri), platform-plane pool-readiness is held hostage to tenant provisioning — a plane-clean violation. The operator: "no Oct-2 objective up to Released should need a tenant."

## Decision

Platform-plane pool-readiness — the 0036 entry gate G4 "grain has a canonical contract", certification, and release — binds to the grain CC version's **current-state membership**: `governance_state_code ∈ {approved, pending_provisioning, active}` (EXCLUDE `draft`, `review`). The declared `field_selection`/`resolved_schema` G4 reads is locked at `approved` and provisioning never changes it.

**Why membership is the right predicate — and a record/transition predicate is NOT — grounded live read-only 2026-10-05 (Architect-confirmed + Platform):**
- `contract.canonical_contract_approval` is EMPTY (0 rows); the transition log carries a `to_state='approved'` row for only 3 versions. The 4 foundational 1.0.0 Kaveri grain CCs were **direct-inserted at `active`** (seeded baseline — no approval record and no transition history; NOT a draft-skip). A predicate keyed on an approval record OR a `→approved` transition would therefore wrongly RED those live CCs and break pool-readiness, with no retroactive evidence to backfill.
- There are **ZERO governed skip-paths**: the only transitions into `active`/`pending_provisioning` are `approved→pending_provisioning` (3) and `pending_provisioning→active` (2) — no `draft→` or `review→` into those states. So every non-seeded member reached its state through `approved`, and the seeded baseline is legitimate-but-unevidenced.

**Precondition — the forward invariant (b), APP-LEVEL, no DDL:** a CONDITIONAL fact-producing guard in `transitionState` (the single governed state-write path, DEC-d9fa49): refuse a transition when the contract is **fact-producing** (`category ∈ {canonical, metric}`) AND `currentState = draft` AND the target `∈ {active, pending_provisioning}`. It is **not** a blanket edge removal — `governanceMachine` is SHARED across contract families and the direct `draft→active` edge is intentionally retained for the sync path and the non-fact-producing families (observation / source / admission / …; `contract.service.ts:51-53`). Scoped this way, the guard makes `{approved, pending_provisioning, active}` membership provably equivalent to "passed through `approved`" for exactly the fact-producing grain CCs that G4 / pool-readiness reads. It ships WITH the binding (same Platform bc-core unit, platform lane), so there is no live window in which membership is unguarded. It does **not** retroactively evidence the seeded 1.0.0 baseline — the invariant protects forward; those seeded CCs are the legitimate baseline it guards. A durable DB-level direct-insert guard (a CHECK/trigger forbidding insert-at-active) is **deferred** (it collides with the seeded baseline and needs the full DDL chain) and logged as a hardening task, not part of this binding.

**This reverses the record-based predicate proposed in Codex's gen-9c1607-01 finding 1.** Codex proposed keying readiness on a recorded approval; the live grounding above is the disconfirming evidence — the record and transition sources are unpopulated for the foundational CCs, so a record predicate reds live pool-readiness. Codex is looped on the re-send to concur with the data.

D575 Unit-3 F1's provisioning-gated `'active'` is RETAINED UNCHANGED as the TENANT/evaluation-plane readiness (fact production). The plane split: platform-plane declaration-authoritative readiness (state membership + the forward invariant) vs tenant-plane provisioned-active readiness.

**Scope — platform readers only; the tenant producer is excluded.** The evidenced-approval binding applies ONLY to the platform-plane pool-readiness / G4 loci named in Context: `mcv-chain-status` (`grain_cc_active` + the currency entities), the G4 declaration readers (`mcf-chain-declaration-reader.readActiveCcDeclarations`, `audit-panel-canonical-facts.reader`), and `chain-audit.readResolvedCcBody`. It **explicitly EXCLUDES** `ccv2-canonical-resolver.service.ts:584` (`loadActiveCc` / `resolveForContract`) and **all tenant fact-production and provisioning paths**: those MUST stay keyed on provisioned `active` (D575 Unit-3 F1). Relaxing the tenant producer to `approved`/`pending_provisioning` would let an approved-but-unprovisioned CC produce tenant facts — the exact violation this decision exists to prevent. So the plane split is concrete at the code loci: **platform readers use the evidenced-approval predicate; tenant producers keep provisioned `active`.** Platform grounded this first-hand (2026-10-05) and corrected the original mis-citation.

## Foundation

Repair location B (contract semantics / the plane boundary), not a lower-layer (0036/D) compensation (Foundation gate Q2: the upper layer was underspecified — `'active'` carried two meanings). No lower-layer compensation. Certification rests on validity, not production (DEC-793e13, DEC-c48b0f). Platform metrics exist independent of tenants (DEC-c220e4). The Canonical Contract is a platform-plane declaration (the-evaluation-boundaries.md); producing Canonical Objects is the tenant-plane act. Invariants III/IV/V/VI preserved.

## Consequences

- The directory members, including those on live-bound grains, reach entry-ready/clean platform-side without tenant provisioning; Phase-A proving units need not avoid live-bound grains.
- customer_invoice 1.1.1 (`pending_provisioning`) is platform-ready now — `pending_provisioning` is in the membership set — with no restoration action and no Kaveri drain for Phase A (the drain is Phase C so Kaveri can evaluate).
- The evaluator binding change (G4 binds current-state membership `{approved, pending_provisioning, active}`, excluding `draft`/`review`) applies at the platform pool-readiness / G4 readers named in Context and Scope — NOT the tenant CO-production resolver, which stays at provisioned `active`. It is a Platform bc-core code unit via the normal review flow (platform lane, Codex), dispatched on this DEC-uid, and ships WITH the app-level forward invariant (b) above (a conditional fact-producing guard in `transitionState` refusing `draft→active`/`draft→pending_provisioning` for `category ∈ {canonical, metric}`; non-fact-producing families and the sync path unchanged) as its precondition.
- No 0036 migration bytes change: the grain-CC state G4 reads is evaluator logic, not DDL. The 0036 design §4 is updated to match.

## References

ADR-09fb2f (D575 platform prerequisite: tenant evidence-chain immutability + runtime identity separation); the D575 Unit-3 F1 provisioning-readiness mechanism in bc-core `contract.service.ts` / `provisioning-readiness.service.ts`; DEC-d9fa49 (`transitionState` as the single governed state-write path / `governanceMachine`); live grounding 2026-10-05 (read-only: `contract.canonical_contract_approval` 0 rows; `contract.canonical_contract_version_transition` sparse — 3 versions with `to_state='approved'`; 4 foundational 1.0.0 Kaveri CCs direct-inserted at `active`; zero `draft→`/`review→` transitions into active/pending); DEC-ca8943 (entry gate G1–G5); DEC-c220e4; DEC-793e13; DEC-c48b0f; `foundation/the-evaluation-boundaries.md`; `foundation/the-invariants.md`.
