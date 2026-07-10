---
uid: DEC-1e55d3
title: "Post-Activation Integrity Audit — CAS regression_audit build-out, BCF-subject lens, invariant-tagged findings, SSOT split with mcv_chain_status"
description: "Extends DEC-1fa08f: build the deferred CAS regression_audit mode as THE post-activation audit of record (BCF+MCF+cross-framework), add BCF subjects as first-class audit targets, tag every finding with the Foundation invariant it defends, and lock the two-surface SSOT split (mcv_chain_status = fast live traffic-light; CAS regression = rigorous signed verifier). Response model: advisory + auto-spawn owning task — never auto-blocks, never auto-unbinds."
status: decided
date: 2026-07-10T01:17:39.976Z
project: bc-core
domain: governance
subdomain: chain-engines
focus: post-activation-audit
---

# Post-Activation Integrity Audit — CAS regression_audit build-out, BCF-subject lens, invariant-tagged findings, SSOT split with mcv_chain_status

## Context

Research showed the decision surface already exists: DEC-1fa08f decided a regression_audit mode ("re-check active metrics after substrate changes") with signed evidence and role isolation, but it was never built — while D481 shipped a lighter live traffic-light (mcv_chain_status) covering part of the same ground. Filing a third surface would fragment the SSOT. Extending CAS reuses shipped substrate (chain_audit_evidence table + chain_auditor_readonly role), inherits the rigor a post-activation audit of record needs (signed, deterministic, hash-anchored — which mcv_chain_status was never built to carry), and closes verified real gaps: BCF has zero post-activation auditing, and a producible withdraw-path defect can strand an active CC on an archived concept invisibly. Invariant-tagging the finding registry (operator addition) gives ISO-style traceability from every finding to the Foundation invariant it defends; the advisory + auto-spawn-task response respects Invariant III (no auto-remediation/historical rewrite) and avoids gate deadlock.

## Context

Operator asked (2026-07-10): BCF and MCF activation are governed point-in-time gates — should there be a post-activation auditing process (auto/manual) that keeps verifying already-activated substrate?

Substrate research (this conversation, verified in bc-core) established:

1. **MCF has a light live audit**: `mcf.mcv_chain_status` (DEC-9c0da7/D481) — per-active-MCV green/amber/red, 4 checks (bindings_resolve, grain_cc_active, pe_current, self_verification), nightly + explicit refresh, strictly read-only, feeds the session-close gate. Known gaps: `bindings_resolve` reads only `mcf.metric_variable_binding` (blind to BC refs in `metric_filter_clause` and `metric_computed_dimension_ref`); `loadActiveCcEntities` applies no lifecycle filter to grain-CC field_selection concepts.
2. **BCF has NO continuous post-activation audit**: activation writes a `bcf.certification_record` + one-time `lifecycle_state` flip and never re-examines. The `bcf` schema is 5 governance tables; no `*_status` table; no scheduler step touches BCF.
3. **A producible cross-framework defect exists**: `withdrawCharacteristic` (registry-authoring.service.ts:1545-1598) guards direct MC bindings (`assertConceptNotBoundInActiveMc`) but — unlike supersession (`assertConceptNotConsumedByActiveCc`, :1686-1711) — has NO active-CC field_selection consumer guard. A business concept consumed only by an active CC's field_selection can be cascade-archived, stranding a live CC on an archived concept. No check detects this state today.
4. **The decision surface already exists**: DEC-1fa08f (CAS) decided a read-only deterministic verifier with 5 lifecycle modes including `regression_audit` — "re-check active metrics after substrate changes" — with signed evidence (`mcf.chain_audit_evidence`, shipped), DB-role isolation (`chain_auditor_readonly`, shipped), and deferred checks C6/C8/C10 that already cover immutability drift and archived-dep detection. CAS v1 shipped `pre_m13_audit` only (bc-core#296/#297); `regression_audit` was decided but never built.

**Filing a third post-activation audit surface would be the mistake.** This ADR extends DEC-1fa08f instead.

## Decision (operator-locked)

### 1. CAS `regression_audit` is THE post-activation audit of record

Build out the deferred `regression_audit` mode as the unified post-activation integrity audit across BCF, MCF, and the cross-framework binding chain. CAS's decided properties carry over unchanged: read-only, deterministic, signed evidence into `mcf.chain_audit_evidence`, `chain_auditor_readonly` role isolation, never authors, never mutates.

### 2. SSOT split — two surfaces, two jobs, no third

- **`mcf.mcv_chain_status` (D481)** stays the **fast live traffic-light**: cheap structural checks, nightly + on-demand, feeds the session-close gate and readiness dial. Its check set gets completeness fixes only (Stage 1) — no scope growth into deep auditing.
- **CAS `regression_audit`** is the **rigorous signed verifier**: immutability-hash drift, transitive archived-dep detection, BCF-subject checks, cert-trail verification. Runs scheduled (weekly by default; frequency operator-tunable) + on-demand + targeted after substrate-changing events.
- Any future post-activation check lands in one of these two surfaces per the split above. No new audit tables/services for this concern.

### 3. Response model: advisory + auto-spawn owning task

Per DEC-1fa08f's own regression note ("produces operational incident on FAIL; does NOT auto-unbind"), now sharpened: a `regression_audit` FAIL **never blocks and never auto-remediates**. It (a) records the signed finding, (b) auto-spawns an owning DevHub task tagged `cas-regression` (pattern: l-node-regression / foundation-gate-override auto-spawn), (c) surfaces on the readiness dial. OPERATOR_REVIEW findings surface without task auto-spawn. Rationale: auto-blocking dependent activations risks deadlock and violates the advisory-evidence posture; auto-remediation would violate Invariant III (clear-and-re-resolve is a historical rewrite).

### 4. Foundational constraints are the check taxonomy (operator addition)

Every finding code in `AUDIT_FINDING_REGISTRY` gains a mandatory `invariant_ref` (I–VI) naming the Foundation invariant it defends. The regression_audit check set, mapped:

| Check | Invariant | Status |
|---|---|---|
| C8: M13/M14 cert hashes match current substrate (immutability drift) | III | decided in DEC-1fa08f, promoted to regression scope — **highest value: nothing on the platform detects post-hoc mutation of frozen activated records today** |
| C10: no hidden dep on archived/superseded object — extended to CC field_selection → BC liveness, filter-clause and computed-dim BC refs | IV + III | promoted + extended (closes the stranded-CC blind spot) |
| C6: MVB/MFC point to BCV not BC heads | IV | promoted |
| NEW R1: single active meaning per boundary — one active MCV per metric_code (legacy-bridge collision), ≤1 active CC per grain entity | I | new |
| NEW R2: object-progression integrity — active MCV's SC→AC→OC→CC→MC chain intact, unskipped | II | new |
| NEW R3: evidence rows append-only — PE / self-verification / cert rows never overwritten in place | V | new |
| NEW R4 (BCF): active concept/entity has complete cert trail | VI | new |
| NEW R5 (BCF): active concept not stranded (≥1 live consumer) ; active entity has ≥1 active concept (orphan) | IV | new |
| NEW R6 (BCF, advisory-tier): D500 concept_source_reference resolves | — advisory | new — **can only ever emit OPERATOR_REVIEW, never FAIL** (D500 is is_advisory by CHECK constraint; evaluation never reads it; treating a soft-ref break as FAIL would misstate its authority) |

### 5. BCF subjects become first-class audit targets

Extend `mcf.chain_audit_evidence.target_kind_code` CHECK to add `'business_concept'` and `'entity'` (DB change — requires DBCP approval before landing). CAS already holds SELECT on schemas bcf + concept-registry substrate via `chain_auditor_readonly`.

### 6. Prevention fix is separate from detection

The withdraw-guard asymmetry (missing CC-consumer guard in `withdrawCharacteristic`) is filed as a **standalone defect task**, not a stage of this ADR — prevention must not wait on the detection build. Repair location D (guard parity at the authoring-service boundary; supersession already implements the same guard, so no new semantics).

## Build stages

- **Stage 0 (standalone defect, immediate):** withdraw guard parity — add `assertConceptNotConsumedByActiveCc` to `withdrawCharacteristic`.
- **Stage 1 (mcv_chain_status completeness, no schema change):** `bindings_resolve` extends to `metric_filter_clause` + `metric_computed_dimension_ref`; checks_json only.
- **Stage 2 (CAS regression core):** implement `regression_audit` mode over existing shipped substrate — C6, C8, C10-extended, R1–R3; scheduler step; targeted-run trigger after withdraw/supersession/CC-activation events. No new tables.
- **Stage 3 (BCF lens):** target_kind CHECK extension (**DBCP required**) + R4–R6.
- **Stage 4 (response wiring):** auto-spawn owning task on FAIL; invariant_ref backfill on existing v1 finding codes; readiness-dial surface.

## Foundation gate

**Repair location: B** — same classification as DEC-1fa08f: extension of a decided governance-artifact family (new mode scope, new target kind, invariant-tagged taxonomy). Not F: CAS evidence is signed governance evidence of record, though regression verdicts remain advisory. **Why not upper layers:** no contract-grammar change; the artifact family is already decided at B. **Why not lower layers:** no evaluation-engine change — audit is read-derive-compare; reads never trigger evaluation (Invariant V); findings are emitted evidence (Invariant VI); activated records are never mutated (Invariant III).

## Out of scope

- Auto-remediation / auto-unbind / activation-blocking on regression findings (explicitly rejected)
- Per-tenant fact verification; cross-tenant audit (unchanged from DEC-1fa08f)
- Substrate-change-triggered refresh of mcv_chain_status (separate D481 follow-up)
- CEE repair automation (sibling ADR territory)

## References

- Extends: DEC-1fa08f (CAS) — NOT superseded; this ADR builds out its deferred regression_audit mode and amends its target-kind and finding-taxonomy scope
- SSOT peer: DEC-9c0da7/D481 (mcv_chain_status)
- Withdraw path: DEC-1fbaf1; guard asymmetry at registry-authoring.service.ts:1580 vs :1686
- D500 advisory layer: concept_source_reference (is_advisory CHECK, never runtime authority)
- Response-model precedent: D481 R3 l-node-regression auto-spawn; ADR-804874 (D366) §4 override pattern
- Foundation: bc-docs/docs/foundation/the-invariants.md (I–VI)
