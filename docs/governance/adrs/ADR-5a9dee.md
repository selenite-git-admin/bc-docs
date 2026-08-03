---
uid: DEC-5a9dee
title: "Foundation grammar taxonomy admits the live authority-creating families — MCF, BCF, Metric Directory — with states-plus-delegation; five-level authority ladder (F-032 disposition)"
description: "One governed act: the taxonomy catches up with the live platform under the authority-creation admission test (D422 D3). MCF Metric Contract, Business Concept Registry, and Metric Directory (as a governed intent/directory family) enter the grammar; the legacy Metric Contract row flips Superseded/Frozen; the lifecycle section goes family-scoped with state names + delegation of transition matrices to the generated enforcement-surface map; FND-ERR-007/008 record the gap; the authority ladder extends to five levels. Executed via Foundation's own change mechanism (ADR + errata + coordinated edits)."
status: implemented
date: 2026-08-03T01:59:35.939Z
project: bc-docs
domain: governance
subdomain: foundation/grammar-taxonomy
focus: authority-model
---

# Foundation grammar taxonomy admits the live authority-creating families — MCF, BCF, Metric Directory — with states-plus-delegation; five-level authority ladder (F-032 disposition)

## Context

The gap-mechanism was one-family-at-a-time admission: FND-ERR-001 added the Observation Contract, then MCF, BCF, and the Directory each grew outside the taxonomy. Admitting only MCF would schedule the next erratum instead of ending the class. A doctrine-derived admission test makes the scope principled rather than enumerative; states-plus-delegation keeps Foundation stable against enforcement churn; and the five-level ladder gives Phase 3 the ranking it is gated on. The lifecycle story finally starts where it actually begins: intent in the Directory, meaning in BCF, contract in MCF, certification before activation (operator's completeness point).

## Decision

F-032 DISPOSITION (design memo DESIGN-MEMO-foundation-grammar-F032.md at devhub 8d4aad1, sha256 8576bcb4…; operator scope extension 2026-08-03; Codex ACCEPTED WITH BOUNDARY, all six decision points affirmed). This ADR is the governed change record the Authority Model requires for a Foundation-level change; the coordinated chapter edits and errata entries ship in one bc-docs PR under it.

1. ADMISSION TEST (doctrine, not preference). A family enters the Foundation grammar taxonomy iff it CREATES authority — drawn verbatim from DEC-c3e57f Decision 3 ("reservoirs inform authoring; only BCF + MCF gates create authority"). The test admits MCF, BCF, and the Metric Directory; it excludes the seed reservoir on Foundation's own doctrine.

2. THREE ADMISSIONS, ONE FLIP — identical shape per family (taxonomy row + governing records + state NAMES + one delegation sentence; never an embedded transition matrix):
   a. MCF METRIC CONTRACT family (Contract family; governing records DEC-c3e57f/D422, DEC-c48b0f/D541): seven states (draft, review, approved, audit_pending, active, audit_blocked, superseded); certification gates activation; the ten-transition matrix and its C6/C7/C8 gates are enforced in substrate and canonically rendered by the generated enforcement-surface map.
   b. BUSINESS CONCEPT REGISTRY family (Vocabulary family; governing records DEC-02f5a9, DEC-149ab2): already the primitives' successor by callout, now a first-class row — live contract bodies reference concepts structurally (CC/OC business_concept_id per DEC-a6258b/DEC-4a17e0; MC concept bindings). Lifecycle doctrine already decided (supersession cascade DEC-9d27a9; admission-error withdrawal DEC-1fbaf1; editorial-vs-meaning-bearing amendment DEC-26b6e2/DEC-fb0b12).
   c. METRIC DIRECTORY MEMBER family — admitted as a GOVERNED INTENT/DIRECTORY FAMILY, explicitly NOT a contract family and NOT realized metric authority (Codex boundary): it owns intent states and versioned member identity, and REFERENCES realized MCF authority through the realization relation. Governing records DEC-b5c7ff/D506, DEC-5842d4. Evidence of load-bearing status: D546 — the C7 accepted-manifest tuple requires member identity; 31 metrics could not complete a governed lifecycle act without it.
   d. LEGACY METRIC CONTRACT row → Superseded/Frozen (DEC-7bdd03/D432 authoring door; DEC-d9fa49/D547 activation retirement; corpus 0 rows since M17), mirroring the taxonomy's existing superseded primitives.
   The artifact count updates accordingly; the count change is errata-recorded (FND-ERR-001/005 precedent).

3. LIFECYCLE SECTION GOES FAMILY-SCOPED. The five-state linear lifecycle is explicitly scoped to the frozen legacy contract-family envelope. Each admitted family's section carries its state names and its delegation. Foundation names WHO holds each matrix; it never embeds one (the MCF matrix changed three times in eight weeks — migrations 46/48/53 — and would whipsaw Foundation).

4. ERRATA. FND-ERR-007: the live authority-creating families (MCF since 2026-05, BCF since 2026-05, Directory since 2026-07) stood outside the taxonomy until this act — the canonical reading was governed by their ADRs during the window. FND-ERR-008: the five-state section's "linear … rollback does not occur" was loose even for its own family (legacy machine allows review→draft and draft→active); recorded as historical note on a frozen family, not rewritten.

5. AUTHORITY LADDER EXTENDS TO FIVE LEVELS (the-authority-model.md; the Phase-3 ranking anchor per Codex): 1 Foundation (identity: invariants, taxonomy incl. admitted families + state names; delegates matrix detail) · 2 ADR+Errata (intent) · 3 GENERATED ENFORCEMENT MAP (new explicit slot: what is enforced, derived, regenerated after every substrate change; map/ADR disagreement is a FINDING resolved by ADR or fix, never by editing the map) · 4 LIVE SUBSTRATE (fact; map/substrate disagreement means the map is stale — regenerate; substrate wins as fact, ADR wins as intent) · 5 runtime consumers + descriptive prose (never authority). Doctrine line: map beats memory, substrate beats map; Foundation above both because it names identities, not enforcement.

6. RECORDED EXCLUSIONS. Seed reservoir OUT (informs, never creates authority — D422 D3). Reader flavors DEFERRED with reason (real draft→active gate per DEC-354552/DEC-17112b, but Operating-Model runtime configuration; grammar admission, if ever, is its own considered act).

7. PHASE-2 CONSEQUENCE. The generated lifecycle map's derivation scope extends to the BCF and Directory state machines alongside MCF + the enforcement-surface map + C6 surfaces — as DERIVATION scope only, never hand-authored matrices (Codex point 6).

Execution: this ADR → one scoped bc-docs PR (the-contract-grammar.md + the-authority-model.md + errata FND-ERR-007/008; Codex review; operator merge — Foundation edits are operator-domain) → ledger E-10 closes F-032 → fast lane complete.
