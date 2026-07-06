---
title: MCF Final Operating Flow — Pre-Doctrine Decisions
date: 2026-06-22
status: draft
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-pre-doctrine-decisions
scope: documentation-only; no substrate mutation; no runtime change; no code patch; no DB write; no PR
audit_pointer: bc-docs-v3/docs/implementation/mcf-framework-audit-2026-06-22.md
followed_by: bc-docs-v3/docs/operating-model/metric-management-system.md (operator-ratified 2026-06-22; draft-authoritative; relocated from implementation/ on that date)
---

# MCF Final Operating Flow — Pre-Doctrine Decisions

## Purpose

This note pins five design choices that must be settled **before** the full Final MCF Operating Flow + Naming Doctrine document is drafted. Each choice is a load-bearing question the doctrine cannot leave open without producing a half-finished rename of the kind the audit (`bc-docs-v3/docs/implementation/mcf-framework-audit-2026-06-22.md`) warned against in §7A. The decisions captured here are draft operator decisions — they direct the doctrine, but they do not authorize substrate change, code change, or runtime change. The doctrine, when drafted, must reflect every decision below in its flow, gate map, recovery taxonomy, and naming rules.

This note is not the doctrine. It is the input to it.

## Decision 1 — Readiness Screening is a gating service, not advisory documentation

**Decision.** Readiness Screening is a first-class gating service positioned between Metric Intake and Metric Draft Review. It consumes the seed / request + Metric Intent (see Decision 2) and emits a persisted result of one of:

```
proceed
needs_bcf
needs_cc_oc
needs_verifier
duplicate_intent
needs_intent_clarification
```

Metric Draft Review (the Maker / Checker / Moderator panel) cannot be called unless the Readiness Screening result is `proceed`. The single permitted bypass is an explicit operator override that captures rationale (minimum length matching existing override-rationale conventions in the substrate, e.g. the 40-character minimum used by `mcf-cert-writer.service.ts` `readAbandonGates`). Every override is persisted alongside the screening result as auditable evidence.

**Rationale.** The current loop discovers blockers after expensive panel runs. The audit evidence (`mcf.metric_authoring_panel_run` shows 11 consecutive `OPERATOR_REVIEW` results before an `APPROVE_FOR_DRAFT` could land for `a-track-paid-customer-invoice-count-v2`; two of eight ever-authored Metric Contract Versions sit stuck in publication review with REJECT verdicts) demonstrates a ~50% downstream-failure rate. Front-loading the check is the speed and quality fix. Without a gate, screening becomes documentation; with a gate, screening becomes substrate the framework reads, writes, and audits.

**Doctrine must address.**

- The owning service and its surface (new controller; new persisted result row; FK from the result to the seed / intake / Metric Intent it screened).
- The override grammar (who can override which screening verdict; whether some verdicts — e.g. `duplicate_intent` against an active Metric Contract — are non-overridable by anyone below operator role).
- The relationship between Readiness Screening and the existing `mcf.metric_authoring_intake_queue` substrate (whether the screening result is a column on the intake row, a sibling row, or a new table; Foundation Invariant III applies — historical results are never rewritten).
- The screening's read sources (BCF substrate, active Canonical Contract / Observation Contract surface, verifier portfolio inventory, active Metric Contract identity catalog).

## Decision 2 — Metric Intent is a first-class artifact above seed metric

**Decision.** Metric Intent is a named artifact distinct from `mcf.seed_metric` and distinct from the panel's `candidate_proposal_json`. It captures the human / business meaning the operator wants the metric to express, before the Maker interprets the seed's `reference_formula` text. The artifact carries at minimum:

- **Metric intent statement** — one-to-three sentences naming what the metric is intended to measure and why. Plain operator language; not a formula.
- **Target grain expectation** — the business entity the metric is expected to aggregate over (e.g. Customer Invoice, Supplier Invoice, GL Account, Customer Payment).
- **Formula-shape expectation** — one of the canonical shape families (`count`, `sum`, `ratio`, `average of delta`, `as-of balance`, `window / rolling`, `bucket / status share`); marked uncertain if not yet decided.
- **For temporal metrics — allowed start / end anchors** — the operator's expectation of which date concepts the metric depends on (e.g. for an average-of-delta metric, both the start anchor concept and the end anchor concept are named at intent time, not inferred at Maker time).
- **Exclusions / non-goals** — what the metric explicitly is *not* (e.g. "this is invoice cycle time, not collection time; due-date and clearing-date are out of scope").
- **Ambiguity notes** — open questions the operator wants to surface (e.g. "the seed reference formula says 'cycle time' — is this doc-date → sent-date, or doc-date → clearing-date?").
- **Operator-approved interpretation** — when ambiguity exists in the seed, the operator's chosen reading, captured before the Maker runs.

**Rationale.** The audit's two stuck Metric Contract Versions both trace to ambiguity the seed did not resolve. Billing Cycle Time's Maker had to infer that "cycle" meant document-date → sent-date; the inference was substrate-unreachable (the active Canonical Contract declares neither anchor Business Concept). Paid Customer Invoice Count v2's Self-Verification failure may also reduce to an intent question (what does "paid" mean — `status='paid'` only, or a status superset; what is the de-duplication key — document_number across all invoice statuses, or document_number filtered by status). Intent precedes inference. Without an Intent artifact, the framework discovers operator intent post-hoc from the Maker's interpretation; the failure mode is then either a chain miss (Source-Chain Resolvability REJECT) or a semantic mismatch the operator catches only at review.

**Doctrine must address.**

- Where Intent is authored (operator-facing surface, not panel-authored) and where it is persisted (likely `mcf.metric_intent` table or a column set on the intake row; Foundation Invariant III applies).
- The relationship between Intent and the seed catalog row (Intent may exist without a seed for operator-direct metrics; a seed may produce multiple Intents if it carries ambiguous reference formulas).
- The Maker's read access to Intent — the Maker prompt receives the Intent verbatim and must produce a proposal consistent with it; Checker / Moderator roles validate Maker output against Intent as well as against substrate.
- Intent versioning and supersession when the operator refines the reading after a stuck-review verdict.

## Decision 3 — Duplicate intent operates at two layers

**Decision.** Duplicate-intent screening runs at two points in the flow, with two distinct matching algorithms and two distinct purposes:

- **Early — inside Readiness Screening (Step 2).** Lossy fingerprint match. Inputs are `Metric Intent + metric_name + grain candidate + formula-shape expectation`. Compares against active Metric Contracts and against in-flight Readiness Screening results for not-yet-published candidates. Returns `duplicate_intent` verdict when a match exceeds the lossy-match threshold. Accepts false-passes (lossy by design — a real near-duplicate may slip past the early screen). Purpose: prevent wasted Maker runs on metrics the catalog already owns.
- **Late — inside Publication Eligibility Evaluation (Step 6) as the existing Duplicate Intent Gate.** Canonical match against the `identity_tuple_hash` (formula AST + variable bindings + filter clauses + grain entity + temporal gate shape + temporal gate params), the substrate-authoritative tuple computed by the M8 PackageSignatureService. This is the existing PE-MC-9 check, renamed semantically. Purpose: substrate-authoritative uniqueness; never overridden.

Both layers are required. The early layer reduces waste; the late layer is authoritative. The early layer may produce false-passes; the late layer cannot.

**Rationale.** The canonical identity tuple is not computable until the Maker has produced the full proposal (formula AST + bindings + filters + temporal gate). Moving the duplicate-intent check entirely to early-screening would weaken the substrate-uniqueness guarantee. Moving it entirely to late-evaluation preserves the existing waste pattern (a Maker run on a metric the catalog already owns produces an `OPERATOR_REVIEW` near-duplicate verdict — the ARPI rebind path consumed this cycle in `mcf-m13-v3` evidence). Two layers, two purposes, two algorithms.

**Doctrine must address.**

- The lossy fingerprint algorithm (which fields, normalized how, matched at what threshold). The fingerprint should be operator-readable, not opaque.
- The relationship between the early and late layers in the audit ledger (whether a metric that passed the early layer and failed the late layer is treated as a Readiness Screening defect or accepted as honest disagreement between layers).
- Override discipline for the early layer (operator may legitimately override `duplicate_intent` to author a successor with refined bindings; the override surfaces in the audit trail).

## Decision 4 — Every legacy `PE-MC-N` gate gets an exhaustive mapping; no silent retirement

**Decision.** The doctrine's gate inventory must include a per-gate mapping table where every live `PE-MC-N` from `mcf.metric_publication_eligibility_result` resolves to exactly one of:

- **Semantic gate name** — the legacy gate becomes a renamed semantic gate, behavior preserved, identity in the persisted ledger preserved via the alias rules in the audit's §7.6.
- **Merged into another semantic gate** — the legacy gate's behavior is absorbed into a broader semantic gate (e.g. binding completeness + type/unit + computed-dimension coherence merging into a Binding Integrity Gate); the doctrine names the merger and what the absorbing gate's predicate becomes.
- **Retired** — the legacy gate is removed from the flow because it never fired meaningfully, was a placeholder, or was superseded by a substrate-side check that obsoletes it. The doctrine names the retirement reason. Retired gates remain in the historical ledger (Foundation Invariant III — never rewrite).
- **Deferred placeholder** — the legacy gate stays in the flow but is explicitly named as a deferred-pass / always-`OPERATOR_REVIEW` slot pending a future redesign, with the redesign trigger named.

The doctrine must produce this table. It must not declare "the new gate list is shorter" without the per-legacy-gate destination being explicit.

**Specific call-out — PE-MC-8 (Runtime Readiness Intent).** This gate is currently a deferred-pass placeholder per the M13 closeout (`mcf-m13-implementation-closeout.md` §4.2 — emits `OPERATOR_REVIEW` always with `mode='default-pass-pending-m18+'`; the `operator-reject` branch is `D-M13-10b open`). It cannot survive the rename as-is because it makes no operator-visible verdict and produces no failure routing. The doctrine must explicitly resolve PE-MC-8 to one of:

- A real semantic gate (Runtime Readiness Gate) with a defined predicate that fires PASS / REJECT, scheduled for the M18+ window the placeholder names.
- Retirement of PE-MC-8 with the runtime-readiness check moved to Step 9 (Runtime Evaluation) where it semantically belongs, on the grounds that authoring publication should not be blocked by tenant-runtime readiness.
- Continued deferral with an explicit named retirement trigger and an ADR pointer.

A silent rename of PE-MC-8 to a semantic name without resolving its predicate is forbidden.

**Rationale.** Twelve codes collapsing to eight semantic names without a mapping table replicates the audit's §7A naming gap at the gate layer. Every silent retirement is a future debugging surprise; every silent merger is a future failure-mode that no one can name. The mapping table is the disambiguator.

**Doctrine must address.** The mapping table itself, plus a one-paragraph rationale per legacy gate explaining its destination.

## Decision 5 — Stuck-Review Doctrine is a parallel repair track, not absorbed here

**Decision.** The stuck-review doctrine — the operating rules for what an operator does when a Metric Contract Version lands in publication review with REJECT verdicts (gap §6.2 of the audit) — is a parallel artifact, scoped separately from the Final MCF Operating Flow + Naming Doctrine. The Final Operating Flow doctrine names Recovery Routing as Step 7 in the flow and links to the stuck-review doctrine as the artifact that operationalizes one of the recovery routes (the abandon-from-review path). The Final Operating Flow doctrine does not solve stuck-review.

**Rationale.** The Final Operating Flow doctrine is a system-shape document; it names what surfaces must exist and how they sequence. The stuck-review doctrine is an operational-policy document; it names what the operator does when the flow lands a metric in a stuck state. Bundling them produces a document that is neither comprehensive about the system shape nor specific enough about the operational rules. They are also independent — the stuck-review doctrine can be drafted and ratified while the Final Operating Flow doctrine is still in design, because the two stuck Metric Contract Versions (billing_cycle_time, paid_customer_invoice_count_v2) sit on the substrate today and need an operational answer regardless of how the future flow is shaped.

**Doctrine must address.** The Final Operating Flow doctrine must (a) name Recovery Routing as Step 7, (b) name the candidate routes (re-evaluate, append fixture, verifier repair, Canonical Contract / Observation Contract delta, BCF admission, abandon, restart-from-draft, semantic supersession), (c) name the stuck-review doctrine as a required parallel artifact and link to it by filename, and (d) not attempt to solve the per-route operational policy itself.

## Doctrine completeness rule

The Final MCF Operating Flow + Naming Doctrine document is not considered complete unless **all five decisions above are reflected** in its content:

- **Flow** includes Readiness Screening as a gating step (Decision 1) and Metric Intent as an authored artifact preceding Readiness Screening (Decision 2).
- **Gate map** includes the exhaustive per-legacy-gate mapping table (Decision 4) with PE-MC-8 explicitly resolved.
- **Recovery taxonomy** includes both the early-screen duplicate-intent verdict and the late-evaluation Duplicate Intent Gate (Decision 3), plus a link to the parallel stuck-review doctrine (Decision 5).
- **Naming rules** follow the audit's §7A.3 staged-refactor discipline — semantic names primary, legacy aliases survive in inline comments / log metadata / persisted historical evidence / migration appendix only.
- **Cross-references** to the parallel stuck-review doctrine, the audit findings (`mcf-framework-audit-2026-06-22.md`), and any ADR(s) the doctrine cites are explicit and resolvable.

Any draft of the Final Operating Flow doctrine that omits any of the five reflections is incomplete and must be revised before adoption.

## Next document

**Target filename (updated 2026-06-22).** `bc-docs-v3/docs/operating-model/metric-management-system.md`. The doctrine was relocated from `implementation/` to `operating-model/` and renamed when the operator ratified the MMS umbrella framing; this note's original recommended filename (`mcf-final-operating-flow-naming-doctrine-2026-06-22.md`) was retired in the same revision.

**Scope locks for the next document.** Same as the audit and this note — documentation-only; no substrate mutation; no runtime change; no code patch; no DB write; no PR; status `draft` until operator review.

**Cross-references the next document must carry forward.**

- This note (`mcf-final-operating-flow-pre-doctrine-decisions-2026-06-22.md`) — as the authority for the five decisions.
- The audit (`mcf-framework-audit-2026-06-22.md`) — as the evidence base for why the doctrine is needed.
- The stuck-review doctrine — by name, even if not yet drafted.
- The vocabulary-lock ADR draft inside the audit's §7 — filed 2026-06-22 as [DEC-7a1c98](../../../governance/adrs/ADR-7a1c98.md), then superseded the same day by **[DEC-54f221 / D449](../../../governance/adrs/ADR-54f221.md)** (three-layer model: Interpretation Surfaces / Implementation Names / Compatibility Names). DEC-54f221 is the live naming-discipline authority; DEC-7a1c98's legacy-code scope and migration appendix are preserved verbatim by DEC-54f221.
- The controlled-refactor staging in the audit's §7A — as the implementation-sequence authority.

This note is now the operator's input to the next drafting session.
