---
uid: DEC-dd11e3
title: "Certification is withdrawable, and machine-checkable defect classes must be structural gates rather than panel discretion"
description: "Auditor opinion (Codex, 2026-08-02) on the date-as-measure finding: the five affected production certifications are valid records but unsound claims, to be suspended then withdrawn; a count metric's counted binding must denote row identity, not a nullable temporal field; the rule belongs in authoring/preflight/publication/certification eligibility, and the panel is demoted from primary detector to backstop for this class"
status: decided
date: 2026-08-02T09:25:55.908Z
project: bc-core
domain: metrics
subdomain: metric-certification
focus: governance
---

# Certification is withdrawable, and machine-checkable defect classes must be structural gates rather than panel discretion

## Context

Certification asserts intrinsic metric correctness. A claim that survives every enforced gate while embedding a known structural defect is not made true by the gates having passed — but neither is it a fabrication, because the gates genuinely ran and their record is accurate. Suspension-then-withdrawal preserves both facts, which deletion or silent re-certification would not. Putting the rule in the structural plane follows the precedent of currency_policy_supported, which was added to the machine-checkable surface after the currency gap was found by similar means: where a defect is decidable from the package alone, discretion is the wrong instrument. Step (e) is last because this programme spent a day patching panel prompts to silence objections and reporting the resulting quiet as progress; the sequence encodes that lesson so it cannot recur by habit.

## Decision

On 2026-08-02 the first production certification wave certified 7 metrics. Five of them were then found to carry a structural defect — a `count` formula whose `measure` role binds a concept whose representation_term and data_type are `date`, so the metric evaluates COUNT(date_field) and counts non-null dates rather than rows at the grain. The same panel rejected the identical defect in 10 other metrics during the same run (15 in the class: 10 audit_pending, 5 active).

The auditor's opinion is adopted as doctrine:

1. WITHDRAWABILITY. The five certifications are NOT void ab initio and NOT sound as certification claims. They are valid RECORDS of what the system enforced at the time, and are treated as valid-but-withdrawable — suspended pending withdrawal. Certification may be withdrawn when later evidence proves the certified definition defective. The audit trail is kept; nothing is deleted and the gate's having run is not denied. This establishes, for the first time, that this programme can un-certify.

2. INERT IS NOT ACCEPTABLE. That no data has yet been evaluated (progression.metric_evaluation holds 0 rows) makes the defect inert, not acceptable. Inertness affects urgency, never validity.

3. THE STRUCTURAL RULE. For a `count` metric at an entity grain, the counted binding MUST denote row identity/existence, not a nullable temporal/date measure — unless an explicit reviewed exception records that the metric intentionally counts populated dates.

4. PLANE. This rule is CERTIFICATION-plane, not chain-plane. The defect is visible entirely inside the MCF package (formula AST says count, role says measure, BCF metadata says temporal/date); it is not a question of whether the metric resolves against a source. It belongs in authoring / preflight / publication / certification eligibility so that future metrics cannot reach panel discretion carrying this class.

5. THE PANEL IS DEMOTED FOR THIS CLASS. A gate that catches a defect 10 times in 15 is a useful triage aid but is not reliable enough to be the final authority where the defect is machine-checkable. The lane machinery itself is not implicated — refusals, PASS decisions, admission evidence and c1-c14 all behaved correctly. The weak component was letting the panel be the ONLY detector for a structural class.

6. SEQUENCE. (a) Immediately mark the five claims as under auditor hold / not to be relied on — containment, not yet withdrawal, and deliberately separated so it does not block. (b) Ratify the structural rule. (c) Withdraw or suspend the five under that rule. (d) Supersede all fifteen as ONE cohort — not only the ten rejected, not only the five active. (e) Only then update panel prompts, if still useful. Teaching the panel before the structural rule exists is forbidden by this sequence.
