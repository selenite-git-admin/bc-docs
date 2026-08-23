---
uid: DEC-c48b0f
title: "Metric certification is an MCF lifecycle act — second panel certifies before activation; the \"external audit\" framing is retired"
description: "Certification (not \"audit\") is an MCF lifecycle act: panel 1 admits (M12), panel 2 certifies the frozen package before activation; rules before judgement; design-vs-execution plane question added to the Foundation gate; supersedes D519's external two-engine architecture"
status: decided
date: 2026-08-01T11:46:20.413Z
project: bc-core
domain: metrics
subdomain: metric-lifecycle/certification
focus: governance

---

# Metric certification is an MCF lifecycle act — second panel certifies before activation; the "external audit" framing is retired

## Context

Five weeks of the external-audit arc produced governance machinery (courier D535, signed exchange D540, packages, custody chains, calibration ceremony) that never stopped a single wrong metric, while the one grounded element — a doctrine-primed panel enforcing Invariant VI against a frozen package — produced the programme's only real findings (unit omission r22, currency-context gap r23, leading to the currency_policy_supported chain-status check). Root cause, identified by the operator: the WORD "audit" imported an entire model (independence, custody, evidence transport, opinions) that nobody required; the actual need was "is this metric's definition correct before activation" — and the platform already had certification substrate (3,530 contract.certification_record rows, McfCertWriterService, the Stage-4 activation certificate in the D397 lifecycle ladder). BCF/MCF stayed grounded because they live inside Foundation's four evaluation boundaries and check against grammar + substrate; the audit arc sat one layer above with no external referent and drifted by construction. Foundation is untouched by this decision: its boundary inventory stands, and the invented fifth quasi-boundary is removed. Supersedes DEC-3d6eeb (D519): the permanent pre-release gate SURVIVES as the certification gate, but the "external, two-engine, signature-bound" architecture is retired — D540 had already retired the exchange transport; this closes the doctrine. Measured drift surface at decision time: ~20 living doc files, ~12 zombie tasks, ~8 memory topics, 3 dead Drizzle schemas, 1 repo to archive — bounded reconciliation, not a refactoring programme.

## Decision

1. RENAME AND RECLASSIFY. The discipline previously called "metric audit" / "external audit" is METRIC CERTIFICATION: a lifecycle act inside MCF, performed at a defined point in the metric lifecycle, producing a certification record in the substrate the platform already models (mcf certification/PE evidence; contract.certification_record lineage). It is not a separate discipline, not independent, not transported. Any certification artifact that acquires a transport, an exchange, a courier, a signature-bound hand-off, or an independence boundary is a defect, not a feature.

2. TWO PANELS, TWO QUESTIONS. Panel 1 — ADMISSION (M12 authoring panel, maker/checker/moderator): judges a PROPOSAL — should this metric exist, is it well-formed; output is a draft MCV. Panel 2 — CERTIFICATION (assessor/adversary/moderator, the roster calibrated over r5–r23): judges the FROZEN PACKAGE of a governed MCV — is the definition faithful to the formula, bindings, grain, and declared semantics; output is a certification record. Different inputs, different questions; empirically panel 2 refutes things panel 1 admitted.

3. GATE POSITION. Certification gates activation: an MCV reaches governance_state 'active' only with a certification record. The "audited-active" vocabulary is retired in favor of "certified". Panel cost/reliability therefore bounds activation throughput and is an architectural constraint, to be engineered (roster cost, retry policy), not discovered.

4. RULES BEFORE JUDGEMENT. Mechanically checkable properties — binding resolution, grain/CC agreement, currency-policy support, unit declaration, vocabulary conformance — belong to deterministic rule surfaces (Publication Review PE-MC checks, mcv_chain_status) and MUST NOT be delegated to a panel. The panel receives only what requires judgement: definition↔formula fidelity and semantic coherence. A rule found by a panel is a missing rule; the remedy is to add the rule, not another panel run.

5. PLANE DISCIPLINE (CLAUDE.md Foundation gate extension). Before any fix, name the plane: a DESIGN act (a contract/declaration is incomplete) or an EXECUTION act (a runtime behaves wrongly). If the defect is a missing declaration in a contract, an execution-plane detector is a net, not a fix — the design act must be named before the net is built. This question joins the three pre-action questions in the Foundation Invariant Check.

6. RECONCILIATION CRITERION. Every open artifact of the audit arc (tasks, docs, memory, branches, the bc-external-audit repo, ~494 ramp5-exchange files) is dispositioned by one test: does it exist because judgement needed to TRAVEL between independent authorities? Then close/archive it. Is it a correctness check on a definition? Then it survives under the certification name. The exchange residue is archived-and-indexed, never edited.
