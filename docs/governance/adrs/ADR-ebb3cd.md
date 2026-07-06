---
uid: DEC-ebb3cd
title: "Evidence and Lineage Write Semantics — Best-Effort + Degraded Marker, Per-Evaluation Lineage with Snapshot Fan-Out"
description: "Lock the durability contract for Evidence/Lineage writes (best-effort + proof_status=degraded marker, not transactional rollback) and the cardinality contract for metric-evaluation lineage (one lineage per evaluation, snapshot identities recorded as toObjects[]); aligns docs to current code and underwrites D386 D-5 inspectability."
status: decided
date: 2026-04-28T16:14:01.286Z
project: bc-docs
domain: evidence-lineage
subdomain: proof-durability
focus: runtime-semantics
---

# Evidence and Lineage Write Semantics — Best-Effort + Degraded Marker, Per-Evaluation Lineage with Snapshot Fan-Out

## Rationale

Audit `bc-docs-v3/reports/platform-code-doc-gap-report.md` (Apr 28 2026) surfaced two P1 doc-vs-code drifts (GAP-001, GAP-002) on evidence/lineage write semantics. Operating-model docs assert synchronous, authoritative, per-snapshot proof emission; live boundary services (admission.service, action.service, metric.service) treat evidence/lineage writes as best-effort and emit one lineage per metric evaluation, not per snapshot. Without a written contract, every Inspector and chain-completeness claim built on top of these writes is structurally ambiguous. D386/D-5 ("chain-complete ⇒ inspectable") is a load-bearing invariant; it fails silently if a "complete" snapshot has a quietly-failed evidence write. This ADR locks the WHAT so D386 Stage 1 can encode the matching reason_code, Stage 2 Inspector can render the right per-section signal, and the operating-model chapters can be aligned in one pass instead of drifting further.

## Context

The platform's operating-model documentation (`docs/operating-model/evidence-and-lineage.md`, `docs/operating-model/metric-evaluation.md`) asserts two strong claims about proof emission:

- **Synchronous-and-authoritative:** every proof-emitting act emits at least one Evidence record synchronously with the act; missing proof is not authoritatively established (`evidence-and-lineage.md:48,51,61,112`).
- **Per-snapshot lineage on metric evaluation:** metric evaluation emits one Lineage per emitted Metric Snapshot (`evidence-and-lineage.md:76`, `metric-evaluation.md:159`).

The Apr 28 2026 platform code/docs audit (`bc-docs-v3/reports/platform-code-doc-gap-report.md`, GAP-001 and GAP-002) confirmed that live code under `bc-core/src/boundary/` does neither:

- `admission.service.ts:455-478` and `action.service.ts:363-395` catch evidence/lineage write errors, log warnings, and return `false` while authoritative object persistence proceeds; `admission.service.ts:285-308` already returns a `degraded` admission status under partial-success conditions.
- `metric.service.ts:399-456` batch-creates snapshots and then records exactly one lineage with `toObject: metric_evaluation:{id}` (`:433-440`) and one evidence event `metric_evaluated` (`:442-453`), regardless of how many snapshots the evaluation emitted.

Both gaps are doc-vs-code drift, not bugs. Both are load-bearing for D386 / DEC-952faa, which makes "chain-complete ⇒ inspectable" a platform invariant (D386/D-5). Without a written durability and cardinality contract, the Inspector cannot render an honest per-section signal, and `chain_status.chain_verdict = complete` can be claimed for snapshots whose proof writes silently failed.

This ADR exists to lock the WHAT in alignment with what the runtime actually does, then let the operating-model chapters and Stage 1 implementation reconcile against a single source of truth — not to re-write the boundary services or amend D386's scope.

## Scope

In scope: the durability semantics of Evidence and Lineage writes during proof-emitting acts (admission, action, canonical resolution, metric evaluation); the cardinality of lineage records emitted per metric evaluation; the chain-status and Inspector-level surfacing of degraded proof state.

Out of scope: changes to evidence schema; new evidence kinds; SC/AC/OC/CC/MC contract changes; D386's metric-temporality axis (its own ADR); replay/repair tooling for degraded proofs (own ADR if and when needed).

## Decision

### D-1 — Best-Effort Proof Writes with `proof_status` Degraded Marker

Authoritative object persistence (Source Object, Canonical Object, Action Object, Metric Snapshot) is the act-of-record. Evidence and Lineage writes that accompany the act are **best-effort**: a failure does NOT roll back the authoritative write.

Failure of an evidence or lineage write during a proof-emitting act:

1. MUST be captured durably on the authoritative object via a **`proof_status`** column carrying one of `complete | partial | degraded`. `complete` is the default (all expected proof writes succeeded). `partial` indicates some, but not all, expected proof writes succeeded. `degraded` indicates that one or more proof writes failed entirely. Existing `admission_status = degraded` semantics in `admission.service.ts:285-308` are subsumed by this column for admission objects; the local field becomes a derived/legacy alias and is not changed by this ADR.
2. MUST be recorded as a row in `contract.chain_status.break_summary_json.reason_code = 'proof_degraded'` for the affected variable/MC, so the four-verdict enum (`complete | partial | broken | unlinked`) does not require amendment. This mirrors the D386/D-2 and D386/D-5 mechanism — semantic causes ride in `reason_code`, not in the verdict.
3. MUST emit a structured warning log carrying: object id, object type, failed-proof kind (`evidence` or `lineage`), error class, correlation id. Rate-limited to one per (object_type, error_class) per minute to avoid log floods on systemic outages.

Implication for `chain_verdict`:
- A snapshot/object with `proof_status = complete` may contribute to `chain_verdict = complete`.
- A snapshot/object with `proof_status = partial` or `degraded` MUST NOT contribute to `chain_verdict = complete`. The verdict resolves to `partial` with `reason_code = 'proof_degraded'`.

Implication for D386/D-5 (Inspector):
- Inspector renders `proof_status` as a non-failing per-section signal. `degraded` is visible, not hidden. Sections downstream of a missing evidence/lineage write resolve to fail-closed-per-section (the section response shape from D386/D-4) without faulting the page.

### D-2 — Per-Evaluation Lineage with Snapshot Fan-Out via `toObjects[]`

Metric evaluation emits **one Lineage record per evaluation act**, not per snapshot. The single lineage record:

1. MUST carry `fromObjects[]` listing the canonical objects consumed.
2. MUST carry `toObjects[]` listing every metric snapshot identity emitted by the evaluation. `toObjects[]` is a non-empty array even when the evaluation produces a single snapshot. Empty `toObjects[]` is an evaluation that emitted no snapshots and is recorded as `toObjects: []` with an explicit `evaluation_outcome` reason field.
3. MUST be paired with one Evidence event of kind `metric_evaluated` for the evaluation as a whole.

This codifies what `bc-core/src/boundary/metric.service.ts:399-456` already does. It accepts the linear-cost trade-off of per-snapshot lineage records in exchange for cardinality matching the act-of-record (the evaluation, not the snapshot). Per-snapshot provenance is preserved via `toObjects[]`; downstream readers (Inspector, audit replay) MUST treat `toObjects[]` as the per-snapshot identity surface.

**Tooling implication (binding consequence of D-2):**

Any consumer that walks lineage to reason about snapshots — audit replay, Inspector chain-spine drilldown, integrity checks, evidence-trail visualizations, downstream publication emitters (e.g. OpenLineage egress per parked TSK-8158e7) — MUST treat the lineage record as a one-to-many edge with `toObjects[]` as the per-snapshot identity surface.

The naive integrity check `count(lineage_object) == count(metric_snapshot)` is **invalid** under D-2 and MUST NOT be used. Tooling that historically assumed per-snapshot lineage cardinality must be updated to:

- Walk `toObjects[]` to enumerate per-snapshot identities.
- Use `count(lineage_object WHERE fromObjects ⊇ {co_id}) ≥ 1` as the per-CO trace existence check, not a row-count equality.
- Surface the "no snapshots emitted" case via `toObjects: []` + `evaluation_outcome` rather than absent lineage.

Implementation tasks for D386 Inspector (TSK-614ff6) and any future replay/audit/publication tooling MUST treat this as a hard pre-condition, not a discovered behavior. The operating-model chapter alignment (D387 Stage 2) MUST document the per-evaluation cardinality and the `toObjects[]` walk pattern as the authoritative consumer guidance.

### Scope of D-1 across acts

D-1 applies to all proof-emitting acts: admission (SC/AC), canonical resolution (CC), action (IC), and metric evaluation (MC). Implementation of `proof_status` on each authoritative object table is staged work; this ADR locks the contract, not the migration order.

### Compatibility with D386

- D386/D-1 (`temporality_kind`) is independent and unaffected.
- D386/D-2 authoring/activation gate is unaffected; semantic mismatches and proof-degraded states are encoded in different `reason_code` values (`semantic_class_mismatch` vs `proof_degraded`).
- D386/D-5 (chain-complete ⇒ inspectable) gains a single dependency line: Inspector reads `proof_status` and surfaces degraded per D387.

## Consequences

### Positive

- Operating-model chapters can be aligned with runtime in a single doc-edit pass once D387 flips to decided. No Inspector mock or doc claim outpaces what code actually delivers.
- D386/D-5 becomes implementable without ambiguity. Inspector has a real per-section signal (`proof_status`) instead of inferring degraded state from absent records.
- Logging and alerting policy on systemic evidence outages becomes a single contract (the rate-limited warning log + `proof_degraded` reason_code), not per-call ad hoc.
- Verdict enum stays at four values. D386's lighter-touch `reason_code` mechanism extends naturally to a second semantic cause.

### Negative / Trade-offs

- `proof_status` adds one column to four authoritative object tables (admission, canonical, action, metric snapshot fact tables). Migration is staged work and adds DDL surface.
- Per-evaluation lineage means consumers cannot use `count(lineage) = count(snapshot)` as an integrity check — they must walk `toObjects[]`. Inspector and any downstream replay tooling must be updated to read this shape.
- `proof_status = degraded` is an observable state that audit reviewers can question. The ADR accepts this — the alternative (silent log + green verdict) is worse.

### Forward dependencies

- Stage 1 task for D387: ADD `proof_status` column and chain-status `reason_code = 'proof_degraded'` plumbing. Sequenced after D386 Stage 1 (TSK-9a0d7b) lands the `temporality_kind` column to avoid two concurrent migrations on `metric_definition` family.
- Stage 2 task for D387: align `docs/operating-model/evidence-and-lineage.md` and `docs/operating-model/metric-evaluation.md` with the locked semantics.
- Stage 3 task for D387: update `bc-core/src/boundary/admission.service.ts`, `action.service.ts`, `canonical-resolution.service.ts`, `metric.service.ts` to write `proof_status` and the `proof_degraded` `reason_code` consistently.
- Stage 4 task for D387: D386 Inspector (TSK-614ff6) reads `proof_status` per section.

These tasks are filed separately when D387 reaches `decided`. They are not part of this ADR.

## Alternatives considered

- **Strict-synchronous (rejected):** roll back the authoritative write on any evidence/lineage failure. Doctrinally pure; turns every transient S3/network blip on the proof bus into a runtime failure on the hot admission/evaluation path. The current `degraded` admission status pattern is evidence the team already preferred best-effort + marker; this ADR generalizes it.
- **Per-snapshot lineage (rejected):** change `MetricService.createGrainSnapshots()` to emit one lineage per snapshot. Linear lineage volume increase; doctrinally cleaner but rounds against an act-of-record (the evaluation) that is genuinely one act with N outputs. `toObjects[]` already preserves per-snapshot identity.
- **Amend `chain_verdict` enum to add `proof_degraded` (rejected):** parallels the rejected D386/P1.2 option. Extending `reason_code` is the lighter-touch lever and keeps the four-verdict taxonomy stable across the platform.

## Status

Decided. Authored 2026-04-28 from audit GAP-001 and GAP-002. User verdict received same day (Q1 + Q2 + Q3 in the verdict pass). Implementation tasks filed parked/later with strict-serial sequencing per D386/D387 Stage 1 ordering (Q6).

## Review history

- 2026-04-28: Initial proposal. Two decisions locked (D-1 best-effort + `proof_status`; D-2 per-evaluation lineage). One dependency line added to ADR-952faa D-5 in the same commit.
- 2026-04-28 (verdict pass Q1–Q3): User accepted both decisions. Q2 amendment landed — D-2 body now carries an explicit "Tooling implication" callout: any consumer that walks lineage to reason about snapshots (audit replay, Inspector chain-spine drilldown, integrity checks, evidence-trail visualizations, downstream publication emitters) MUST treat the lineage record as one-to-many with `toObjects[]` as the per-snapshot identity surface. The naive `count(lineage_object) == count(metric_snapshot)` check is invalid and MUST NOT be used. Q3 flip: status `proposed` → `decided` after Q2 amendment landed. Implementation Stage tasks (3) filed parked/later with strict-serial sequencing per Q6 — D387 Stage 1 (proof_status migration) waits for D386 Stage 1 (temporality_kind migration) to land before starting.
