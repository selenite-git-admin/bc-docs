---
title: First complete chain-engine loop — milestone marker (2026-06-16)
status: milestone
date: 2026-06-16
project: bc-core
domain: platform
subdomain: chain-engines
focus: milestone
authority: DEC-1fa08f / DEC-739e23
---

# First complete chain-engine loop — milestone marker

**2026-06-16.** The three governed pieces of the chain-engine architecture were first proven to compose end-to-end on real substrate:

```
CEE plans  →  Harness applies  →  CAS verifies
```

This file marks the milestone. It is **not** a runbook, **not** a design doc, **not** an operating manual. It records what existed at the moment the loop first closed.

## Component status

| Component | Authority | Status | Surface |
|---|---|---|---|
| Harness v1.1 | [B-track FSCM governed-apply](../onboarding/) | operational | CLI — applies `sc.create_draft` and friends |
| CAS v0 → v1 | [DEC-1fa08f / D445](../../../governance/adrs/ADR-1fa08f.md) | v1 operational (all six checks substantive) | `POST /api/mcf/chain-audit/runs` (mode = `pre_m13_audit`) |
| CEE v0 | [DEC-739e23 / D446](../../../governance/adrs/ADR-739e23.md) | operational | `POST /api/mcf/chain-enrichment/plans` (mode = `source_contract_gap_plan`) |

## Key PRs

| Component | PRs | Merged at |
|---|---|---|
| Harness v0 (packet schema + seed apply + idempotent replay) | [bc-core#287](https://github.com/selenite-git-admin/bc-core/pull/287) | 2026-06-15 |
| Harness v1.0 (dry-run + classifier for `sc.create_draft`) | [bc-core#288](https://github.com/selenite-git-admin/bc-core/pull/288) | 2026-06-15 |
| Harness v1.1 (`sc.create_draft` governed apply) | [bc-core#289](https://github.com/selenite-git-admin/bc-core/pull/289) | 2026-06-15 |
| CAS v0 foundation (substrate + pure check executors) | [bc-core#296](https://github.com/selenite-git-admin/bc-core/pull/296) | 2026-06-16 |
| CAS v0 service wiring | [bc-core#297](https://github.com/selenite-git-admin/bc-core/pull/297) | 2026-06-16 |
| CAS v0 AuthUser fix-forward | [bc-core#298](https://github.com/selenite-git-admin/bc-core/pull/298) | 2026-06-16 |
| CEE v0 substrate (`mcf.chain_enrichment_plan`) | [bc-core#299](https://github.com/selenite-git-admin/bc-core/pull/299) | 2026-06-16 |
| CEE v0 service wiring | [bc-core#300](https://github.com/selenite-git-admin/bc-core/pull/300) | 2026-06-16 |
| **CAS v1 body-walker checks (C2/C3/C11 substantive)** | **[bc-core#301](https://github.com/selenite-git-admin/bc-core/pull/301)** | **2026-06-16** |

## Live evidence at the moment of closure

| Artifact | UID |
|---|---|
| First CAS v0 evidence row (`pre_m13_audit` on ARPI v2 specimen MCV) | `c36bea48-751a-45ca-8858-1fe58a477a74` |
| First **CAS v1** evidence row (same specimen MCV, post-PR#301 merge at main@`32e178f`, aggregate PASS, all six checks PASS, 0 findings) | **`c6650277-026a-4801-91da-da91f4d0d7d2`** |
| First CEE plan row (`sc_gap_satisfied` for B-track FSCM) | `407ebb3d-f759-4cee-b37f-a8c55776e55b` |
| B-track FSCM source contract that satisfied the gap | `019ecaad-7d05-72c1-a902-fcaef8705e4f` (`sc__sap_fscm_dispute_case`) |

## What the loop proved

- **Harness v1.1** can apply a governed `sc.create_draft` packet and land a new active `source_contract` row.
- **CAS v0** can audit an MCF MCV by re-reading current substrate (6 checks: C1 / C2 / C3 / C4 / C5 / C11), aggregate a verdict from the `PASS / FAIL / OPERATOR_REVIEW / NOT_APPLICABLE` model, and persist signed evidence into its own table without touching any business substrate.
- **CEE v0** can plan against the source-contract layer: detect when an SC gap is already satisfied, identify the next gap as out-of-v0-scope, and persist a plan row — without invoking the harness, mutating any business substrate, or touching CAS evidence.
- The three operate as siblings, not as a chain: there is no internal call from one to the next. The operator (or a future driver) walks the loop deliberately.

## What the loop did NOT prove

| Surface | Status at milestone |
|---|---|
| AC / OC / CC planning | not built — CEE v0 explicitly defers to v1 with `out_of_v0_scope` |
| M14 activation | not invoked in the loop |
| Runtime binding | not exercised |
| Full ChainAuditService (5 modes) | CAS v1 ships `pre_m13_audit` only; 4 modes deferred |
| Full ChainEnrichmentEngine (auto-apply + execution journal) | CEE v0 is planner-only; v1 surface designed but not implemented |
| `sc_create_proposed` branch of CEE v0 | spec-tested only at this point — see follow-up note |
| `FAIL` / `OPERATOR_REVIEW` verdict of CAS v1 on real substrate | spec-tested only at this point — see follow-up note |
| CAS v1 snapshot hash coverage of `ccBody` + `activeOcBodies` | follow-up `TSK-3db4ed` filed; hash today still uses the v0 projection |

## Context this milestone closes

Before today, the three substrate-touching layers — apply, audit, enrich — each existed in isolation, with no shared discipline about who owns what. The audit-first sequencing (CAS shipped before CEE, so that the auditor defined "correct enough to proceed" before the enricher started proposing) is what made the loop coherent rather than tangled. That sequencing is recorded in the two ADRs, not here.

## Next decisions

Out of scope for this marker. The follow-up menu is recorded in the closing checkpoint of SES-44b6a1 and in the operator's consolidation message of 2026-06-16.
