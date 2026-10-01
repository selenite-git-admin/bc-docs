---
uid: DEC-79b62f
title: "The Foundation gate: the repair-location vocabulary, the four pre-action questions, the hard rules and the override path"
description: "Defines, at the ADR layer, the Foundation gate every architectural, data, contract, boundary or behaviour-changing change passes before code: repair location A to F as a naming convenience mapped to Foundation surfaces, the four pre-action questions, the five hard rules with their Foundation derivations, and the override path with its required DevHub enforcer; makes CLAUDE.md, the metric SOP and the controller chapter descriptive restatements of this record. Supersedes nothing."
status: decided
date: 2026-09-30T11:18:43.507Z
project: bc-docs
domain: governance
subdomain: foundation/change-discipline
focus: foundation-gate
---

# The Foundation gate: the repair-location vocabulary, the four pre-action questions, the hard rules and the override path

> **Decided 2026-09-30.** The operator decided this record as written: desk grant `2026-09-30T12-40-45-252Z-594d93aa` (text SHA-256 `594d93aa12aa04e819ca474a43631993abccd659d2545228b245630da9c9e525`, recorded 2026-09-30T12:40:45Z), decision 5 of the fleet resume plan: "ADR DEC-79b62f, the Foundation gate, is decided as written; the Architect flips its status and restates CLAUDE.md and the metric workstream chapter to cite it." Status flipped by the Architect (TSK-3be7c4). The DevHub enforcer of item 6 is not yet built (TSK-083286).

## Context

The Foundation gate has been in daily use since 2026-05-11, when barecount-devhub commit 4b527859 added a "Foundation Invariant Check" section to the project instructions. That commit grounded the gate in the Foundation chapters and named the repair locations A to F "as a non-authoritative naming convenience and question prompt" that "shorthand boundaries and governance surfaces already defined in Foundation". It declared "No new invariant. No new contract artifact. No new authoritative layer model." ADR DEC-c48b0f (2026-08-01, item 5) added a fourth question, design act or execution act, "to the three pre-action questions in the Foundation Invariant Check".

Verified on 2026-09-30 at bc-docs main fa17b924 and barecount-devhub main 421a30de: 69 of the 619 ADR files use the gate's vocabulary (repair location, Foundation gate, Foundation Invariant Check) in their own Foundation-gate sections; 8 of them cite CLAUDE.md as the gate's source, and `ADR-e01fcf.md` line 204 states that the CLAUDE.md section "remains the authority for the gate process". The metric SOP (`docs/onboarding/metric-workstream.md` line 61) calls its own gate section "derivative of CLAUDE.md". No Foundation chapter, ADR or governance page defines the vocabulary, the questions or the hard rules. The Authority Model places repository-local guidance in the descriptive layer, which is "never authority itself" (`docs/foundation/the-authority-model.md` line 49). A level-5 document is therefore being cited as level-2 authority by 69 decisions.

The override path named in the project instructions (a rationale of at least 40 characters in `self_audit_json.foundation_gate_override` at session close, and an auto-spawned task tagged `foundation-gate-override`) was copied from DEC-804874 section 4. That ADR is `superseded` by DEC-b390ef, a supersession register that restates no override pattern. The DevHub close tool has never implemented the field: `src/` carries no reference to it, the tool's `self_audit_json` schema accepts only `l_node_override` and strips unknown keys, and no task with the tag has ever been spawned. The override path has no live authority and no enforcer.

The Architect controller's Foundation study (barecount-devhub `artifacts/architect/FOUNDATION-YARDSTICK-2026-09-30.md`, section 6; session SES-58d3f2) settled where the definition belongs: at the ADR layer, not in a Foundation chapter. Foundation "names identities, not enforcement" (DEC-5a9dee line 36); the Foundation overview says a chapter that fits none of its groups does not belong in Foundation (`foundation-overview.md` line 54); and a Foundation chapter would need a platform version declared by ADR and errata (`the-authority-model.md` lines 69 to 73), which is disproportionate for a procedure that applies the invariants and adds none.

## Decision

1. **The gate and its scope.** Every architectural, data, contract, boundary or behaviour-changing change is tested against the six invariants (`docs/foundation/the-invariants.md`, "Testing a proposed behavior") and answers the four questions in item 3 in the session's saved plan before any code is written. Typos, formatting, comments and behaviour-neutral test refactors are out of scope. A change that fails any one of the six checks is stopped and presented as a violation, not built.

2. **The repair-location vocabulary.** The letters A to F name where a change belongs. They are a naming convenience for surfaces Foundation already defines; they are not a taxonomy, they create no authority, and no artifact carries them as data.

| Letter | Name | The Foundation surface it shorthands |
|---|---|---|
| A | Source or admission boundary | The external state a source system emits, and the admission boundary with its Source, Admission and Observation Contracts (`the-evaluation-boundaries.md`, "Admission boundary"; `the-contract-grammar.md`, the three admission-side families) |
| B | Contract semantics | What a contract of any family declares: the contract grammar itself (`the-contract-grammar.md`) |
| C | Mapping or binding | The binding layer: Contract Binding, metric binding, field mappings. Tenant customisation happens only here (`the-contract-grammar.md` line 325); Metric Contracts are not coupled to it (line 254) |
| D | Evaluation implementation | The runtime that performs a boundary act: Readers, the canonical evaluator, the metric evaluator, the dispatcher (`the-evaluation-boundaries.md` line 31 defers these to the Operating Model chapters) |
| E | Storage or projection | The stores that hold progression and proof objects (`the-object-model.md`; the Data Model and Schema chapter) |
| F | Read model or diagnostics | Consumer surfaces: inspectors, endpoints, dashboards, projections, under the consumption discipline of `the-object-model.md`, "Consumption discipline" |

A change may name two letters (for example B plus D) when a declaration and its evaluator change together.

3. **The four pre-action questions,** answered in the saved plan: (1) Why this location: what is wrong or missing at this layer. (2) Why not an upper layer: if C to F is chosen, confirm A and B are not underspecified; if A or B is underspecified, a fix at C to F is compensation and stops. (3) Why not a lower layer: if A or B is chosen, confirm no working implementation is being bypassed. (4) Design act or execution act, as DEC-c48b0f item 5 defines it: a missing or wrong declaration is a design act and is named first; an execution-plane detector is a net, not a fix. DEC-c48b0f stays in force; this record references it.

4. **The hard rules,** each derived from Foundation:
   - **No lower-layer compensation for an upper-layer semantic gap.** The fix lives at the layer of the gap. Derived from Invariant I (meaning is produced only at the canonical evaluation boundary; "No other operation produces, modifies, or reinterprets meaning", `the-invariants.md` line 54) and the boundary-specific-output rule (`the-evaluation-boundaries.md` line 57). Precedent: DEC-e01fcf principle P8; DEC-02f5a9; DEC-f6527b.
   - **No formulas tied to fact shape.** A Metric Contract declares semantic inputs over canonical meaning, never a source column, a source code value or a fact-table shape. Derived from `the-contract-grammar.md` line 254 (Metric Contracts reference canonical meaning only and are not coupled to the mapping layer) and line 325 (tenant customisation only at binding). DEC-6b35e0 decides the metric-filter case; this record generalises it. The test: the same Metric Contract onboards a second source system through the binding layer (C) without an edit to the contract.
   - **No hand-edits to the substrate.** Every write to authoritative state goes through a governed evaluation or authoring act; a direct write to objects, contracts, bindings, ADRs or errata is forbidden (`the-dual-layer-interaction-model.md` lines 69 and 96). Where no governed service exists, the gap is surfaced and the smallest governed change is proposed for explicit approval. Platform schema changes follow DEC-4c1396.
   - **Reads never trigger evaluation** (`the-evaluation-boundaries.md` line 60 and "Read access does not trigger evaluation"). A diagnostic that re-runs an evaluation to correct a number is a violation.
   - **If a change would violate Foundation, stop and present the violation, not the fix.** Silent override "is itself a governance defect. Intent does not change that classification" (`the-authority-model.md` line 194).

5. **The override path.** A session may close past a Foundation-gate violation only by recording an explicit override: a rationale of at least 40 characters in `self_audit_json.foundation_gate_override` at `devhub_session_close`, written verbatim into the session's change record, and one auto-spawned task tagged `foundation-gate-override` that links the session and the violated invariant or repair-location decision. There is no time-box. An override records a violation or an accepted exception; it does not make the behaviour correct. The pattern's origin is DEC-804874 section 4, superseded by family in DEC-b390ef; this record is the pattern's authority from its date.

6. **The enforcer.** The DevHub close tool implements item 5: it accepts the field, refuses a rationale under 40 characters, persists the text to the change record and spawns exactly one task. Until that build lands, the override path is a discipline with no enforcer, and every document that describes it says so. The build is a barecount-devhub change owned by the DevHub controller (TSK-083286); its merge commit carries `closes:` with this record's UID for the enforcer half.

7. **Descriptive restatements.** The Foundation Invariant Check section of barecount-devhub `CLAUDE.md`, section 2 of `docs/onboarding/metric-workstream.md`, and the Architect judgement rules in `docs/development/the-controller-operating-model.md` are descriptive restatements of this record. Each cites this record as its source; none extends it. The `CLAUDE.md` citation of ADR-804874 for the override pattern is replaced by this record.

8. **Foundation cross-reference and editorial alignment.** This record authorises two edits to Foundation chapters that change no Foundation claim: (a) one sentence at the end of "Testing a proposed behavior" in `the-invariants.md`: "The pre-action procedure that applies these checks to a proposed change is defined in DEC-79b62f."; (b) the editorial alignment of chapters that lag decisions already taken (TSK-65f57d): `foundation-overview.md` (ten chapters, the five-level ladder of DEC-5a9dee, indexing `the-governed-selection.md` under DEC-c4c742), `the-authority-model.md` line 34 (five levels), `the-object-model.md` line 263 (fifteen artifacts), and the three "Governing source" lines in `the-invariants.md` (lines 101, 124, 143) that cite version-2 section numbers, replaced by chapter names. No erratum is needed: no contradiction is introduced, and the governing decisions exist.

## Rationale

The Authority Model allows only three homes for a rule that binds later sections: a Foundation chapter, an ADR, or an erratum (`foundation-overview.md` line 28). The gate is not an invariant, not an object, not a grammar artifact and not a boundary; it is the procedure by which a change is tested against those things. Foundation names identities and delegates enforcement (DEC-5a9dee), so the procedure sits at the ADR layer, where 69 decisions already reach for it. Recording it there ends the citation of a descriptive document as authority, gives the override path a live authority in place of a superseded one, and names the missing enforcer instead of implying it exists.

The vocabulary stays a naming convenience because the 2026-05-11 commit that introduced it said so, and because promoting six letters to a taxonomy would create a seventh classification beside the objects, families and boundaries Foundation already fixes.

## Options considered

- **A Foundation chapter.** Rejected: Foundation names identities, not enforcement; the procedure fits no Foundation group; a Foundation change needs a platform version and errata.
- **A Development chapter alone.** Rejected: the descriptive layer is never authority, and 69 ADRs already cite the gate.
- **An ADR at the governance layer with a Foundation cross-reference (chosen).**

## Consequences

- The 69 ADRs keep their Foundation-gate sections unchanged; new ADRs cite this record for the gate.
- The DevHub controller builds the enforcer (item 6) and proves it goes red once before it is trusted.
- The Architect records the Foundation cross-reference and the editorial alignment (item 8) in one bc-docs pull request with a Codex docs landing.
- The Docs controller updates the three descriptive restatements (item 7).
- This record moves to `implemented` when the enforcer and the cross-reference have both landed.

## Non-goals

No new invariant, object, grammar artifact or boundary. No supersession: DEC-c48b0f, DEC-e01fcf, DEC-6b35e0 and DEC-4c1396 stay in force and are referenced. No behaviour change in bc-core. No change to the L-node override of the chain-status gate (`l_node_override`), which is a separate gate.

## References

- `docs/foundation/foundation-overview.md` lines 28, 54; `docs/foundation/the-authority-model.md` lines 38 to 56, 49, 69 to 73, 194; `docs/foundation/the-invariants.md` lines 54, 192 to 203; `docs/foundation/the-evaluation-boundaries.md` lines 31, 57, 60, 164 to 175; `docs/foundation/the-contract-grammar.md` lines 254, 325; `docs/foundation/the-dual-layer-interaction-model.md` lines 69, 96; `docs/foundation/the-object-model.md`, "Consumption discipline".
- DEC-5a9dee (five-level ladder); DEC-c48b0f item 5; DEC-e01fcf P8 and line 204; DEC-6b35e0; DEC-4c1396; DEC-804874 section 4 (superseded); DEC-b390ef; DEC-ebf0b4 (D268).
- barecount-devhub commit 4b527859 (2026-05-11); barecount-devhub `src/mcp-server.js` lines 368 to 374 (the close tool's schema); `artifacts/architect/FOUNDATION-YARDSTICK-2026-09-30.md` (barecount-devhub PR 157).
