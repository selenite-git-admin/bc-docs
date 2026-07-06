---
id: structural-differentiators
order: 2
title: "Structural Differentiators"
status: drafting
authority: informative
depends_on: [platform-overview, the-invariants]
governing_sources:
  - Foundation (the locked architectural authority — this document derives from it and adds nothing to it)
  - The Invariants
  - The Evaluation Boundaries
  - The Contract Grammar
governing_adrs:
  - DEC-6b35e0 (D441 — source vocabulary discipline at the MC boundary)
  - DEC-75cb8a (D492 — machine-enforced metric-authoring drift guard, two layers)
  - DEC-95687d (D369 — progression/fact/S3 split; boundary-event records)
  - DEC-a4e550 (D221 — ADR-first; the evidence citations below resolve through the registry)
errata_referenced: []
word_target: 2200
---

# Structural Differentiators

## Scope and register

This document records the platform's technical differentiators in one specific, falsifiable form: **industry failure classes that this platform structurally cannot have** — not because a process avoids them, but because the execution model gives the failure no place to occur. It is derived positioning: Foundation and The Invariants remain the authority; every claim below cites the mechanism that enforces it and, where one exists, the live proof that exercised it.

Two register rules govern this document. First, "structurally cannot" is claimed only where a defect would require violating an invariant or bypassing a machine gate — never where correct behavior merely depends on convention or review. Second, the platform's honesty discipline applies to itself: §Honest boundaries lists confirmed gaps of the same severity class as the wins, because a differentiators document that hides its gap register would itself be the kind of artifact this platform refuses to produce.

The external evidence base referenced throughout is the three-source ERP KPI-pitfall research of 2026-07-06 (two independent external passes plus one adversarially verified pass; merged catalog and substrate cross-walk in the engineering research archive), which ranked the industry's most damaging metric-corruption classes across SAP ECC/S4HANA, Oracle EBS/Fusion, NetSuite, and Dynamics 365.

## 1. Historical truth is read, never reconstructed

**The industry failure class.** Tier-1 ERP live tables store *current* state: Oracle's `AMOUNT_DUE_REMAINING` and Dynamics' `CustTransOpen` reflect today, so any historical or point-in-time report built on them silently shows the present instead of the past. Practitioner research ranks this among the most damaging analytics failures — backdated aging reports that match today's balance, historical DSO that drifts as items clear.

**Why it cannot happen here.** Invariants III and V make every authoritative object immutable and every evaluation act non-replayable: a Canonical Object version or Metric Snapshot preserves what was true when it was produced, permanently addressable, never overwritten. Point-in-time questions are answered by *reading preserved state*, not by reconstructing it from live fields — reconstruction has no API surface to exist on. Audit is a read operation, not a rerun operation (The Invariants, §Invariant V corollary).

**Live proof.** Canonical-version coexistence was exercised end-to-end in the first version-coexistent contract succession (2026-07-06): the successor Canonical Object set was produced as new boundary acts while every prior version's objects remained untouched and byte-verified (per-period sums identical across versions). Metric snapshots are append-only; reads select per-period state without ever mutating history.

## 2. Meaning is produced once, at a governed boundary

**The industry failure class.** In conventional stacks, semantics live in whichever report, view, or pipeline last touched the data — the same field means different things in different dashboards, and a change to a transformation silently reinterprets history.

**Why it cannot happen here.** Invariant I: business meaning is produced exactly once per Canonical Object version, at the canonical evaluation boundary, by applying a declared, versioned contract. Consumers cannot produce meaning by querying raw source objects; reads never trigger evaluation; a newer contract produces *new* versions rather than reinterpreting old ones. Source-code translation (e.g. SAP document-type codes to canonical document kinds) is a declared, versioned mapping applied at that boundary — each object version's meaning is exactly what its contract declared at production time.

## 3. Source vocabulary cannot leak into metric definitions

**The industry failure class.** The single most common semantic defect in ERP analytics: source-system codes (SAP BLART `DR`/`DZ`, Oracle transaction-type ids, NetSuite tranType strings) hard-coded into KPI logic — breaking the metric on the next source system and coupling business meaning to a vendor's storage format.

**Why it cannot happen here.** This is enforced by machine gates, not convention, at three depths (DEC-75cb8a / D492): the authoring panel refuses maker proposals embedding source literals in filters or formulas; the deterministic publication-eligibility gate (G4, filter and formula legs) rejects any Metric Contract whose literals are not declared canonical values of the bound concept — nothing carrying a source literal can reach ACTIVE; and a session-facing preflight catches the class before any authoring spend. Metric Contracts bind Business Concepts, never source fields (The Contract Grammar, §Metric Contract — "references raw Source Objects" is a listed disallowed behavior).

**Live proof.** The gate's validation corpus is real, not synthetic: three historical violators (authored before the formula-leg gate existed) fail the check exactly, and the eighty clean contracts pass — the escape route they used is now closed by construction. The defect class was found by audit, fixed at the correct layer (canonical translation), and then made unrepresentable.

## 4. Metrics are source-agnostic by construction — multi-ERP portability

**The industry failure class.** KPI definitions rebuilt per ERP; "DSO" implemented three different ways against three systems; migration projects that re-author the entire metric estate.

**Why it cannot happen here.** The portability test is a grammar rule: the same Metric Contract must onboard a second source system through the binding layer with **zero metric edits**. Source-specific knowledge (which field carries the document-type classifier, which codes mean invoice vs payment, which column is the local-currency amount) lives in per-source Observation/Canonical contracts; the metric layer sees only canonical vocabulary. A second ERP arrives as new mappings to the same concepts — the 84 active metrics are untouched by design, and the gates of §3 make regressions to source-coupling impossible to author.

## 5. Every number is evidence-backed; absent evidence means the act did not happen

**The industry failure class.** Numbers whose provenance is a pipeline log at best; audits that reconstruct what "probably" ran; partial failures that leave state recorded as success.

**Why it cannot happen here.** Invariant VI: Evidence and Lineage are emitted synchronously with the evaluation that produced the object, preserved on the authoritative chain; an evaluation without an evidence record is treated as not having occurred. The discipline is self-correcting in practice: when a mid-act failure mode was discovered that could record acceptance without an artifact, the boundary act was made honest (failure now records `rejected`, retries are new acts) and the false records were corrected under explicit governance — the invariant defined both the defect and its fix.

## 6. Governed numbers cannot be silently replayed or backfilled

**The industry failure class.** Nightly rebuilds that quietly change last quarter; backfills indistinguishable from original computation; "same" numbers whose lineage differs run to run.

**Why it cannot happen here.** Invariant V plus storage-level enforcement: one accepted evaluation per input per contract version (a partial-unique constraint in the progression layer), and any re-evaluation is a *distinct* act producing a *new* version with its own evidence. Restatement, when it happens, is visible as new versions — never as history changing in place.

## 7. "Runtime-live" means payload-verified, not status-green

**The industry failure class.** Dashboards trusted because jobs succeeded; correctness inferred from pipeline health.

**Why it is different here.** A metric is not called live until its served values are verified against an independent recomputation from the canonical layer, per period — a standing discipline, not a launch-week ritual (recent examples: 26/26 and 27/27 periods exact for the invoiced-tax family). This is a discipline rather than a structural impossibility, so it is stated as such — but it is enforced by the authoring workflow's terminal step, and its known blind spot is documented (§Honest boundaries).

## 8. Rule compliance is machine-gated, not vigilance-dependent

**The industry failure class.** Standards that live in wikis and code review; correctness that decays as teams scale.

**Why it is different here.** The platform's own history proved that rules enforced at human level fail at human level — and the response was to move enforcement into the substrate: deterministic publication gates, panel-time fail-fasts, a step-gated authoring workflow that structurally refuses out-of-order or cross-unit actions, and a pre-spend preflight. The governance panels refuse work for the right reasons (vocabulary synonym stretching, unmapped amendments) — refusals are a designed feature, and overrides exist only as evidenced, audited operator acts that spawn follow-up obligations.

## 9. Pitfall immunity is prospective, not reactive

**The industry failure class.** Every implementation rediscovers SAP sign conventions, clearing-table migrations, and currency mixing at production cost.

**Why it is different here.** The known failure classes of tier-1 ERP analytics are maintained as a verified, machine-checkable taxonomy (three-source research, adversarially verified, cross-walked against the live substrate), routed into: conformance checks that run against produced data, authoring-time preflight rules, classifier features for candidate triage, and per-metric risk records. The catalog's most-damaging class (unsigned amount conventions) and its as-of reconstruction semantics (the open-item/cleared-item predicate) are recorded with primary-source verification *before* the features that need them are built.

## Honest boundaries

The same discipline that produces the wins above surfaces the platform's own confirmed gaps, tracked in the open engineering register at the same severity grammar as external pitfalls. As of 2026-07-06: **aggregation-currency basis** (amount metrics currently aggregate document-currency values; masked in the development dataset, design decision filed and prioritized), **debit/credit sign semantics** (not yet projected at the canonical layer; safe today only by population separation), and a set of latent classes (reversals, special G/L, partial/residual lifecycles) that are unexercised by current synthetic data and are being made testable deliberately. The §7 payload-verification discipline is known to be blind to failure classes where the canonical layer itself carries the defect — which is precisely why the prospective taxonomy of §9 exists.

A reader evaluating these differentiators should weigh exactly this: the wins are structural, and the gaps are *listed*. Platforms whose failure modes are conventions do not usually know where their bodies are buried; this one publishes the map.

## References

- The Invariants; The Evaluation Boundaries; The Contract Grammar (Foundation chapters — the authority for every "cannot" above)
- ADR-6b35e0 (D441), ADR-75cb8a (D492) — source-vocabulary discipline and the two-layer drift guard
- ADR-95687d (D369) — progression/fact/S3 evidence architecture
- Engineering research archive: ERP KPI-pitfall three-source catalog and substrate cross-walk, 2026-07-06 (barecount-devhub `.claude/research/`)
