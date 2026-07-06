---
uid: DEC-149ab2
title: "BCF Authority Delegation — Framework Approval for the Business Context Framework"
description: "D6: foundational ADR establishing the Business Context Framework (BCF) authority model under operator-overrideable AI-by-default operation, with first delegation limited to Scope 1 (BF/BO). Scope 2 (CF) and Scope 3 (BF↔CF mapping) deferred to a subsequent ADR amendment on substrate prereqs. Resolves 9 open questions from the BCF evidence chain."
status: decided
date: 2026-05-18T15:54:29.672Z
project: bc-docs
domain: contracts
subdomain: catalog
focus: governance
decided_date: 2026-05-19
---

# BCF Authority Delegation — Framework Approval for the Business Context Framework

## Context

BCF requirements v0.4 establishes the framework's shape. The inventory pass (2026-05-18 narrow update) identifies what exists and what must be treated carefully. The failure-evidence map (47 findings) shows why prior catalog work failed under the cert-as-flag-mutation regime. The gap-research sweep (27 findings + Codex §8 verification + scoped drivers §9) bridges intent and reality with line-grounded current-code evidence. Together the four documents converge on a single question this ADR must answer: under what authority, on what scope, with what discipline does the framework begin operating? Authority-first ADR per operator instruction; mechanics (build plan, effort sizing, code) follow in subsequent work. Nine open questions identified in the evidence chain are resolved here as decided positions after operator review on 2026-05-19.

## Decision

### Authority

The Business Context Framework (BCF) is established as an ADR-governed authoring mechanism under Foundation §The Authority Model. Within BCF scope, AI consensus constitutes **Framework Approval**: AI proposes, prepares, and approves contextual members through the framework lifecycle under policy. Operator override is the exception path; operator approval remains the sole authority for everything outside BCF scope.

Framework Approval requires, for every framework write: (1) three-model consensus with closed-enum verdict, (2) same-input-snapshot rule, (3) no-fabrication grounding check pass, (4) immutable authoring record with the full NF1 field set, (5) calibration sampling enrollment recorded, (6) active operator override mechanism. Failure of any one of these conditions invalidates the approval and routes the action to OPERATOR_REVIEW.

The framework's three immutable rules (Requirements Chapter 5) are adopted verbatim: Framework Approval discipline (Rule 1), always-available operator override (Rule 2), non-bypassable authoring-record trail (Rule 3).

### Nine resolved positions

**Q1 — Framework Approval scope at first delegation.** **Scope 1 (BF/BO contextual vocabulary) only.** Scope 2 (CF contextual naming) and Scope 3 (BF↔CF field-level mapping) are deferred to a subsequent ADR amendment. Sub-deferral conditions for Scope 2/3 activation: (a) `cc-onboarding.service.ts` mapping-write CF trust check lands per inventory §2.4 gap item 1 (G6b); (b) `cc-onboarding.service.ts` Meaning-once write-time semantic-signature check lands per inventory §2.4 gap item 2 (G7); (c) `canonical-field.service.ts` lifecycle becomes operationally non-dormant. Rationale: inventory §9.7 hypothesis confirmed — Scope 1 has the highest concentration of reusable bc-ai artifacts (`bf_dedup`, `bo_composer`, `bo_dedup`) and the strongest data motivation (4,769 non-clean-state legacy BFs). Scope 3 is structurally blocked from first delegation on the G6b/G7 substrate gaps.

**Q2 — Legacy disposition of 4,769 non-clean-state BFs.** **Option A: freeze + parallel.** Legacy catalog content in non-clean state pairs per inventory §1.2 — (status_code='certified' + catalog_state_code='candidate_import', 4,745 rows; status_code='certified' + catalog_state_code='correction_required', 11 rows; status_code='draft' + catalog_state_code='certified_catalog', 12 rows; status_code='draft' + catalog_state_code='correction_required', 1 row); total 4,769 — is marked quarantined via an explicit quarantine_marker, retained read-only, excluded from BCF authoring paths. The fourth pair (draft + correction_required) is included in the quarantine cohort even though inventory §1.2 marks it workflow-consistent, because Foundation Contract Grammar §Lifecycle does not contain `correction_required` and quarantining it preserves the option to either promote it to a Foundation amendment (Requirements Open question, Chapter 4) or supersede it. The framework operates only on new content authored via the framework. Eventual reconciliation, supersession, or restart-from-clean is **explicitly deferred to a sibling ADR** that consumes BCF's first 90 days of calibration data. Rationale: Option B (reconcile+migrate) requires deciding 4,769 cases without evidence; Option C (restart-from-clean-active) loses encoded knowledge in the 4,769 rows. Freeze permits scoped activation now without prejudicing the eventual reconciliation choice.

**Q3 — Lifecycle-column consolidation.** **Consolidate to one column (`governance.state`) per Foundation Contract Grammar §Lifecycle.** Two-columns-with-invariant has failed in practice — the 4,769 non-clean-state legacy pairs are the evidence. Migration sequencing: (i) `governance.state` added as a new column populated from the existing pair via a deterministic mapping; (ii) the quarantine_marker from Q2 captures the legacy state-pair separately so no information is lost; (iii) dual-column read paths become deprecated and removed; (iv) the existing `status_code` and `catalog_state_code` columns are dropped after the deprecation window. Requirements N19 enforces this consolidation as a negative requirement.

**Q4 — Authoring-record substrate.** **Hybrid: extend `certification_record` for transition records; add sibling `panel_output_record` for panel-run-level immutable outputs.** Cross-link via `panel_run_uid` foreign key on `certification_record`. Rationale: `certification_record`'s row-per-action shape is correct for state-transition logs (one row per `from_state → to_state` event) but wrong for panel outputs (one panel run produces three agent transcripts, an input hash, a grounding-check result, a verdict, a sampling status — a different cardinality and shape). Separating them keeps each table coherent and avoids polymorphic columns. Extension scope on `certification_record`: add `panel_run_uid`, `prompt_version`, `model_identity_json`, `input_hash`, `policy_version`, `sampling_status`, `grounding_check_result`. New `panel_output_record` carries the per-agent transcripts and verdicts; append-only; replicated per NF1.

**Q5 — Initial calibration regression threshold under AI-by-default with no prior data.** **Bootstrap + tightening ladder, not a fixed numeric threshold.** Three phases:
- **Phase 0 — Bootstrap (first 50 AI executions per scope per stage):** 100% sampling. Every AI action routes to operator review for confirm/override. Override rate is logged but does not auto-pause. Phase 0 produces the first calibration evidence base.
- **Phase 1 — Conservative (next 500 executions or 30 days, whichever sooner):** sampling drops to 25%. Auto-pause threshold = any single operator override in the sampled population. Conservative bound from inventory §9.8.
- **Phase 2 — Operating (after 500 executions with override rate ≤ 5% over the trailing 100 sampled):** sampling drops to operator-tunable, default 5%. Auto-pause threshold = override rate >10% week-over-week.

Quarantine-rate auto-pause crosses all phases: >5% quarantine in any 100-execution rolling window triggers immediate pause regardless of phase. Operator may at any time tighten (raise sampling, lower auto-pause threshold). Operator MAY NOT loosen below the phase floor without an ADR amendment.

**Q6 — Vocabulary direction.** **BCF vocabulary is canonical; bc-ai harmonizes.** Use "Moderator" throughout BCF documentation, UI, ADRs, operator vocabulary, and the renamed bc-ai `AgentRole` enum (MAKER, CHECKER, MODERATOR). Rationale: "Gate" is overloaded in BCF (deterministic publication gates are refuse-only; operator-confirm gates are policy-driven); "Moderator" disambiguates and more accurately describes the role (adjudicates Maker/Checker disagreement, reaches consensus verdict). Implementation rename is deferred to a follow-on task; this ADR locks the direction. ADR-b8ec00 (D409) and related bc-ai code are subject to the rename.

**Q7 — REJECT-eligible defect-code closed list (Deferral D4).** **Adopt the D409-empirical defect classes as the v1 closed list. ADR-governed and extensible.** v1 list:

| Code | Meaning |
|---|---|
| `DEF_PLACEHOLDER` | Template-placeholder definition (e.g., "X from OAGIS undefined") |
| `DEF_RATIONALE` | Rationale-style definition (e.g., "Fundamental for…", "Needed to…") |
| `DEF_BOILERPLATE` | Shared boilerplate across distinct members (verbatim definition reuse) |
| `IDENT_NAME_SPLITTER` | Multi-word property fragment absorbed into object_class |
| `IDENT_SOURCE_SUFFIX_LEAK` | Source-system table suffix (e.g., `_hdr`) leaking into platform identity |
| `IDENT_TAUTOLOGICAL` | Tautological object_class (e.g., `budget_ledger_line_budget_ledger`) |
| `PROV_FABRICATED` | Citation/standard_ref does not trace to bc-seed lineage or row provenance |
| `STRUCT_TYPE_INCOHERENT` | Type-pair invalid (data_type + representation_term disagree) |
| `STRUCT_FAMILY_UNIT_MISSING` | Semantic family demands unit anchoring; none present and not derivable |

Additions require ADR amendment. Defects observed during operation that do not match a v1 code route to OPERATOR_REVIEW with defect-proposal; operator may file the amendment.

**Q8 — Operator-confirm rule grammar (Chapter 4 open question).** **Closed-form predicate × transition × scope × action grammar.** Rule shape:

```
rule_uid: <UID>
scope:       bf | bo | cf | mapping | any
transition:  intake_to_draft | draft_to_review | review_to_approved | approved_to_active | any
predicate:   <closed-form expression over member attributes, row history, importer signals, panel outputs>
action:      require_operator_confirm | route_to_operator_review | block
rationale_required: bool (default true)
```

Predicate grammar v1 (closed-form; no free expressions):
- Attribute equality / null-checks on member fields.
- Set membership (e.g., `member.object_class IN (...)`).
- Cohort signals via registered built-in signals on importer or panel history (e.g., `member.importer_uid IN cohort:importers_with_recent_high_reject_rate`). Built-in signals are registered alongside the policy and versioned; they are not free-form function calls.
- Panel-output signals (e.g., `panel.grounding_check = 'PASS'`).
- Composition signals (e.g., `bo.composition_count < 4`).
- Numeric comparisons and boolean composition (AND/OR/NOT).

v1 explicitly disallows: subqueries, joins, user-defined functions, write actions, anything that could trigger evaluation (reads must not trigger evaluation per Foundation). Default seed configurations adopt Chapters 12-14 SHOULD lists.

**Q9 — Anti-coverage-KPI guard rail.** **Adopt N30 as a new negative requirement.** "The framework MUST NOT report, surface, or display any metric whose primary axis is volume of approvals (count of approved BFs, BOs, CFs, mappings) without simultaneously displaying paired calibration metrics (operator-override rate, quarantine rate, supersession rate) on the same surface." Every Activity Dashboard view, Calibration Dashboard view, operator notification, framework status report subject to this rule. Coverage alone is forbidden as a framework KPI.

*Related operational control (not part of N30):* gap-research G24's default-untrusted classification of helper scripts in `bc-core/scripts/*` addresses a different vector (helper-script trust + tenant/schema hardcoding). It is named here for cross-reference only; N30 is a UI/reporting-surface rule, G24 is a tooling-trust rule.

### Explicit non-decisions

The following are explicitly NOT decided by this ADR:

1. **Build order and effort sizing.** Mechanics follow in the gap-pass document; this ADR is authority-only.
2. **Legacy reconciliation method.** Quarantine is the decision; how the 4,769 are eventually superseded, reconciled, or restarted from is a sibling ADR after 90 days of BCF calibration data.
3. **Scope 2 (CF) and Scope 3 (mapping) activation timing.** Conditional on the G6b/G7 substrate gaps; an ADR amendment activates them.
4. **Exact long-term operating thresholds.** Q5 establishes pilot defaults (50 / 500 / 30-day / 5% / 10%) as the bootstrap-and-tightening ladder; long-term operating thresholds beyond Phase 2 are not decided here and may be tightened (operator-side, in-band) or loosened (ADR amendment) once steady-state calibration data exists.
5. **bc-ai code rename mechanics.** Q6 locks direction; the actual `AgentRole` enum rename and call-site updates are a follow-on task.
6. **bc-seed operational state.** G21 remains needs-operational-verification; this ADR assumes bc-seed will be operationally adequate but does not certify it. If bc-seed coverage is found insufficient at first activation, the framework auto-routes affected proposals to OPERATOR_REVIEW per F8 grounding check and N1 no-fabrication.
7. **MCF (Metric Context Framework) decisions.** Sibling document; this ADR does not bind MCF.
8. **Foundation amendment proposals (Deferrals D2, D5).** Carried forward unchanged.

### Authority lineage

This ADR is the D6 foundational ADR named in Requirements Deferral D6. It supersedes nothing; it establishes a new authority pattern. It is itself subject to Foundation §The Authority Model — operator may modify, supersede, or reverse it through subsequent ADRs. Calibration regression auto-pause (F12, Q5) is an in-band mechanism for halting framework operation; it does not require ADR amendment to invoke, but reactivation after pause requires operator action and is logged in the Activity Log.

### Consequences

**What changes:**
- BCF begins operating on Scope 1 (BF/BO) only under Framework Approval after Scope 1 build-plan prerequisites are satisfied. Those prerequisites are scoped by the gap-pass document (not this ADR), and at minimum cover: (a) `governance.state` column from Q3 in place with legacy quarantine_marker populated; (b) `panel_output_record` table and `certification_record` extension from Q4 in place; (c) Phase 0 sampling configuration from Q5 in place; (d) operator UI surfaces sufficient for Phase 0's 100%-sample workload (Activity Dashboard + Per-Member Detail + Override Action + Authoring Panel Rejection Log, per Requirements Chapter 6); (e) bc-ai panel role-rename from Q6 landed in code or explicitly waived for Phase 0.
- New BFs and BOs flow through the framework lifecycle under AI-by-default; operator override remains always-available.
- 4,769 legacy non-clean-state BFs are quarantined; BCF does not touch them.
- `governance.state` column added; dual-column lifecycle deprecated.
- `panel_output_record` table created; `certification_record` extended with NF1 fields.
- bc-ai vocabulary renamed (Gate → Moderator) on the path to Phase 1.
- All framework UI surfaces subject to N30 anti-coverage-KPI rule.

**What does NOT change:**
- Foundation Contract Grammar.
- Any of the four evaluation boundaries.
- Tenant runtime path.
- MCF concerns.
- CC composition, SC/AC/OC/CM/IC authoring (Foundation default applies).
- Operator's ultimate authority — every Framework Approval is overrideable.

### Status

Filed at `decided` after operator review on 2026-05-19. Implementation follows in the gap-pass document and subsequent build sessions. ADR amendments will be filed when (a) Scope 2/3 activate, (b) legacy reconciliation method is chosen, (c) Phase 2 thresholds tighten, (d) REJECT defect-code list extends, (e) operator-confirm grammar extends.
