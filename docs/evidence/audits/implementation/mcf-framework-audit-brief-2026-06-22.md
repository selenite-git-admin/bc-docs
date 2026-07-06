---
title: MCF Framework Audit Briefing
date: 2026-06-22
status: open
scope: no substrate mutation; no runtime change; no MCF activation attempts; no BCF / CC / OC mutation; no code patch; no DB write
deliverable: one durable audit briefing document only (this file is the briefing — the audit produces its own findings document)
owner: Principal Architect
context_session: prior session attempted Billing Cycle Time activation; halted at Publication Eligibility Evaluation (legacy: M13) with Source-Chain Resolvability Gate (legacy: PE-MC-11) REJECT and Self-Verification Gate (legacy: PE-MC-10) REJECT; same wall as IPCT
---

# MCF Framework Audit Briefing

## 1. Why this audit exists

The Metric Context Framework was declared closed at the stage level (Metric Draft Review through Publication Eligibility Evaluation) on the basis of one fully-activated metric (ARPI) and one partially-activated metric (IPCT, which required mid-flight authoring of a new Observation Contract + Canonical Contract chain to pass Source-Chain Resolvability). Every subsequent activation attempt has surfaced a new structural blocker that required a code patch, a new controller, or a fresh chain authoring. The conclusion is that closeout was premature at the framework level even though it was correct at the stage level: each stage's verification ran on a happy path, not a portfolio of failure modes, and the integration was never stress-tested.

This audit re-grades the framework's actual readiness before any further metric activation is attempted, and locks an operator-facing vocabulary so the artifacts of that re-grading are legible without a glossary.

The audit makes no substrate mutation and no runtime change. This audit may write its own briefing/findings documents, but it must not mutate runtime substrate or execution state: no writes to `bcf.*`, `contract.*`, `mcf.*`, no database changes, no code patches, no service restarts, no PRs, no MCF activation attempts, no BCF waves, no CC/OC authoring.

## 2. Operator-facing vocabulary lock (in force throughout this briefing and the resulting audit document)

The legacy stage and gate codes (M12, M12.5, M13, M14, M15, B6, C5, F3, PE-MC-*, L-V1*, C-FX-*) describe positions in a build-plan list. They do not describe behavior, and they force every reader to maintain a mental glossary. From here forward, the framework uses the names below. The legacy code appears in parentheses on the first mention only; after that, the semantic name stands alone.

### 2.1 Stages

| Semantic name | Legacy alias | What this stage does |
|---|---|---|
| Metric Draft Review | M12 | Panel (Maker / Checker / Judge) proposes a metric candidate from an intake; produces a panel-run record + a candidate proposal envelope |
| Metric Contract Materialization | M12.5 | Converts an approved panel proposal into draft `mcf.metric_contract` + `mcf.metric_contract_version` + variable bindings + a seed fixture + a Self-Verification result; transitions intake to `consumed_by_panel` |
| Self-Verification | M10 verifier | The engine runs the candidate metric's formula against its seed fixture(s) and compares the result to the fixture's expected output; pass/fail is one of the gates in Publication Eligibility Evaluation |
| Publication Eligibility Evaluation | M13 | Runs the full PE gate matrix against a draft Metric Contract Version; on all-pass advances the Metric Contract Version state draft → review → approved and stamps parent Metric Contract hash columns; on partial pass advances draft → review and stops |
| Metric Activation | M14 | Transitions an approved Metric Contract Version to active and issues the activation certification record; gated on Publication Eligibility Evaluation having advanced state to approved and on parent Metric Contract hash columns being stamped |
| Metric Supersession | M15 | Active Metric Contract Version → superseded; cert-bearing |
| Business Concept Draft Review | B6 | Panel proposes a Business Concept candidate (admission) |
| Operator Certification | C5 | Operator confirms a Business Concept Draft Review proposal and mints the certification record |
| Registry Write | F3 | The cert is applied to the registry — the Business Concept lands as active |
| Registry Transition | F3-like supersession / amend variants | The cert is applied as a state transition (supersession, definition amendment) rather than a fresh registry insert |

### 2.2 Gates

| Semantic name | Legacy alias | What this gate tests |
|---|---|---|
| Source-Chain Resolvability Gate | PE-MC-11 | Every variable binding's Business Concept must be declared by the resolved Canonical Contract's field selection and reachable through the Source Contract / Admission Contract / Observation Contract chain; this is the gate that has rejected both IPCT and Billing Cycle Time |
| Source-Vocabulary Discipline Gate | PE-MC-12 | Variable bindings stay within source vocabulary (no derived / synthesized fields posing as source) |
| Self-Verification Gate | PE-MC-10 | The Self-Verification result for the candidate's seed fixture must be `pass` against the current package signature |
| Materialization Preconditions | L-V1* (a–i) | Read-only checks before Metric Contract Materialization may proceed: shape-code validity, formula AST grammar, prior-materialization absence, collision avoidance, etc. |
| Draft Review Coverage Checks | C-FX-* | In-panel checks the Checker role runs to enforce that the Maker's proposal covers required structural and semantic dimensions (temporal grain, formula well-formedness, evidence binding, resolver mapping, fiscal-time handling, etc.) |

### 2.3 Naming discipline

The vocabulary lock applies to all artifacts the audit produces. Every reference in the audit findings uses the semantic name. Legacy codes appear only at first mention or in a single appendix that maps legacy → semantic for the migration. The audit's final section proposes a vocabulary-lock ADR (frontmatter only is sufficient for the briefing; the ADR is drafted inside the audit itself).

DEC-* / D-* decision codes are unchanged. They identify *decisions*, not *processes*. The decisions cite the new process names; the process names do not inherit the decision numbering.

## 3. Audit scope

The audit covers exactly the six tracks below. It does not exceed them. Findings that surface adjacent issues are noted but deferred.

### 3.1 Re-grade prior MCF closeouts

For each closeout document in `bc-docs-v3/docs/implementation/mcf-m2...m13`, answer:

- Was the closeout a stage-local success (the stage's own unit tests + a single happy-path proof) or an end-to-end publication success (the stage drove a real Metric Contract Version through to Metric Activation under realistic substrate)?
- Did the closeout stress-test the failure paths the stage owns, or did it only document the happy path?
- Did the closeout assume substrate properties (e.g., a co-designed Canonical Contract) that don't generalize?
- What evidence would have caught the gaps that have since emerged (Maker / Canonical Contract coupling, no generic governance transition surface, stuck-review doctrine missing, verifier instability)?

The output is a single table with one row per closeout doc, columns: stage, current grade (`stage-local` / `end-to-end` / `mixed`), failure modes verified, failure modes assumed-away.

### 3.2 Inventory all Metric Contracts and Metric Contract Versions by semantic lifecycle state

Produce one table with one row per Metric Contract Version in `mcf.metric_contract_version`, columns:

- Metric Contract name, Metric Contract UID, Metric Contract Version UID, semver / version_code
- Lifecycle state (semantic): `authored` (draft, no Publication Eligibility Evaluation rows), `materialized draft` (draft, has Self-Verification result), `publication review` (review, Publication Eligibility Evaluation has run with partial pass), `activation-ready` (approved, all gates pass, hash columns stamped), `active / published` (active, certification record issued), `superseded / abandoned` (terminal)
- Legacy state code (`governance_state_code` raw value) for cross-check
- Last Publication Eligibility Evaluation verdict snapshot (PASS / OPERATOR_REVIEW / REJECT counts per gate)
- Path to advancement or block reason

This is the master inventory the audit's recommendations key off. It will reveal in particular which Metric Contract Versions are stuck (publication review with REJECTs and no abandon route).

### 3.3 Metric-shape × Canonical Contract / Observation Contract coverage matrix for near-term seeds

For the next ~25 candidate seed metrics (rank by recency of operator intent, then by seed status), produce a row with columns:

- Seed metric name + ID
- Inferred metric shape (`count`, `sum`, `average of delta`, `ratio`, `bucket / status share`, `as-of balance`, `window / rolling`)
- Required Business Concepts the formula would name (inferred from the seed's `formula_hints` and the Maker's typical output shape)
- Whether each required Business Concept is declared by an active Canonical Contract on the relevant grain entity (`covered` / `missing`)
- Whether the Observation Contract / Admission Contract / Source Contract chain back to a source-system field exists for each required Business Concept
- Predicted Publication Eligibility Evaluation result: `would pass`, `would fail at Source-Chain Resolvability Gate`, `would fail at Self-Verification Gate`, `unknown`
- Recommended unblock action if predicted-fail

The point of this matrix is to make the Source-Chain Resolvability Gate wall visible before any further metric activation is attempted. Today we discover the wall one metric at a time; this matrix shows the entire wall up front.

### 3.4 Framework gap inventory

For each of the gaps surfaced by IPCT and Billing Cycle Time, produce one entry with:

- Gap name (semantic, e.g. "no generic lifecycle transition surface")
- Symptom (what the operator / audit observer sees today)
- Root cause (which assumption in the framework's design is violated)
- Architectural fix recommendation (what surface or doctrine needs to exist)
- Migration impact (code, database, doctrine, operator UI)
- Owner layer (which `mcf-*` controller / service / ADR is on the hook)

Minimum coverage:

1. **No generic lifecycle transition surface.** There is no HTTP route for draft → review → approved transitions outside the Publication Eligibility Evaluation evaluator's internal calls and the ARPI-specific controller. Every non-ARPI metric depends on Publication Eligibility Evaluation succeeding all-pass to reach approved; a partial pass leaves the Metric Contract Version stuck in review with no governed forward path.

2. **Missing stuck-review / abandon doctrine.** The `abandon` route exists only for draft state. A Metric Contract Version in publication review with REJECT gates has no canonical exit: it can't roll back (Foundation Invariant III: append-only ledger), can't re-evaluate the same gates productively without a substrate change, and can't be abandoned through the existing surface. The framework needs an `abandon-from-review` doctrine (and surface) plus a `restart-from-draft` (new Metric Contract Version) doctrine.

3. **Weak Canonical Contract delta-publish path.** When the Maker proposes Business Concepts the active Canonical Contract doesn't declare, there is no governed surface that turns the proposal into a Canonical Contract v(n+1) authoring request. Today the operator must either author a new Canonical Contract chain manually (IPCT's path) or abandon the metric. A `Canonical Contract delta` surface — "propose adding fields X, Y, Z to Canonical Contract C because Metric Contract Version M needs them" — would close this loop.

4. **Verifier portfolio stability gap.** The Self-Verification engine has been patched once for date arithmetic (PR #344 / engine date-arithmetic fix). The Self-Verification Gate REJECT on Billing Cycle Time's Metric Contract Version (with `stale_fixture_flag: false`) suggests there are unaddressed evaluation paths. The framework needs a verifier portfolio: one fixture per metric shape (count, sum, average-of-delta, ratio, bucket-share, as-of, rolling) with a known-good expected output, run on every engine change.

5. **Operator-facing naming / code opacity.** Stage codes (M12, M12.5, M13) and gate codes (PE-MC-*, L-V1*, C-FX-*) force a glossary for every reader. The vocabulary lock in §2 above resolves this gap; the audit's deliverable includes the lock ADR draft.

The audit may add gaps it surfaces but must not subtract from this list.

### 3.5 Vocabulary-lock ADR draft

The audit drafts the body of an ADR (target: `bc-docs-v3/docs/adrs/`) with the following sections:

- Context (why we are renaming — premature closeout symptom, glossary tax)
- Decision (the full legacy → semantic map; the discipline rule that semantic names are primary and legacy codes appear at first mention only)
- Migration plan (rename order: doctrine + audit artifacts first → code identifiers + controller routes + service methods next → database enum values last with transition-window aliases → operator UI labels last; each step gates the next)
- Owner layer per renamed surface
- Migration impact summary (count of files / routes / enum values / labels affected per layer)
- Decisions left to operator (whether legacy codes survive as comments in code; whether to keep PE-MC-N numbering for cross-reference inside the new "Publication Eligibility Gate" family or drop entirely)

The ADR draft does not need to be filed in the audit pass; it ships inside the audit document as a held proposal.

### 3.6 "MCF framework ready" exit criteria

Define the threshold at which the framework should be re-declared closed, in terms an outside observer can verify:

- Minimum portfolio: N distinct metric shapes (e.g. count, sum, average-of-delta, ratio, bucket-share, as-of, rolling) each driven to Metric Activation back-to-back
- Zero per-metric code patches during the portfolio run (every patch needed surfaces as a framework gap before the portfolio, not during it)
- Every gap in §3.4 resolved before the portfolio begins
- Every Metric Contract Version in the inventory in §3.2 in a non-stuck state (active, superseded, or cleanly abandoned)
- Vocabulary lock landed and propagated to code identifiers in at least one layer

Propose the exact N and the exact shape list. Lean honest, not optimistic: if 15-of-15 with five shapes is the right bar, say so. If 25-of-25 is the right bar, say so. The point of this section is to set a falsifiable target so future closeout claims can be tested against evidence.

## 4. Hard scope (verbatim — no exceptions)

- No substrate mutation / no runtime change.
- No Metric Draft Review attempts.
- No Metric Contract Materialization attempts.
- No Publication Eligibility Evaluation invocation.
- No Metric Activation invocation.
- No Business Concept Framework / Canonical Contract / Observation Contract mutation.
- No code patch.
- No database write.
- Produce one durable audit findings document only.
- Stop after the findings document and report its path.

The findings document is durable doctrine, not a held packet. It belongs in `bc-docs-v3/docs/implementation/` with a name matching the convention `mcf-framework-audit-2026-06-XX.md` (the XX is the audit completion date, not this briefing's date). It does not live in `.claude/` and does not live in `bc-core/scripts/audit-output/`.

## 5. Suggested audit-session execution shape (for the fresh session)

The audit is one fresh session, not a multi-session program. Recommended internal ordering:

1. Read this briefing end-to-end. Read the M2–M13 closeout docs.
2. Run the read-only queries needed for §3.2 (Metric Contract Version inventory) and §3.3 (coverage matrix). These are the only DB reads. They should be parameterized through `mcp__bc-postgres__pg_query` only.
3. Author §3.1 (re-grade) from the closeout docs.
4. Author §3.4 (gap inventory) from this briefing's seeding + whatever the inventory + matrix surface.
5. Author §3.5 (vocabulary lock ADR draft) — this is the lock; everything else cites it.
6. Author §3.6 (exit criteria) last, since it depends on §3.1–§3.4 to set N and the shape list honestly.
7. Stop. Report the findings document path.

No PRs. No code edits. No `gh` invocations. The findings document is the only artifact. The audit session may consult the live database for read-only inventories and the live filesystem for documentation reads.

## 6. Context the fresh session should have

The current session ended in a HALT at Publication Eligibility Evaluation for Billing Cycle Time:

- Metric Contract: `37b7e70a-7209-4db0-9c9c-ce50f9e4a89f` (`billing_cycle_time`)
- Metric Contract Version: `995f90e3-70a0-4b0d-8f12-aa1f4619c2b5` (v1, currently in publication review state)
- Maker bound `cycle_end_anchor` to Business Concept `30a7afa5-…` (Customer Invoice × sent date) and `cycle_start_anchor` to Business Concept `8cbd57be-…` (Customer Invoice × document date)
- Active Canonical Contract `cc__customer_invoice_arpi_slice v4.0.0` declares neither Business Concept; it declares a field literally named `document_date` that is bound to the *posting date* Business Concept `61e19048-…`, plus eight other fields covering clearing date, net / gross / tax amounts, currency, document number, document type, and status
- Publication Eligibility Evaluation verdicts: Source-Chain Resolvability Gate REJECT, Self-Verification Gate REJECT (verifier returned `fail` on a fresh fixture with `stale_fixture_flag: false`), Self-Verification (the M18-pending operator-review placeholder gate) OPERATOR_REVIEW, all nine other gates PASS
- IPCT hit the same Source-Chain Resolvability Gate wall and was unblocked only by authoring a new Observation Contract + Canonical Contract chain (a path forbidden by the current pre-execution constraints)

These are the live specimens the inventory and gap analysis can cite.

## 7. Stop condition

Stop after producing the findings document. Report its path. Do not begin any subsequent activation attempt. Do not propose follow-up sessions inside the findings document — the findings are the input to the operator's next decision, not a plan for the operator to approve sight-unseen.
