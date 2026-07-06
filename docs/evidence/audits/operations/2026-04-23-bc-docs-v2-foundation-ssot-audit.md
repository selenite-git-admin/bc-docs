# legacy v2 archive Foundation SSOT Audit

Date: 2026-04-23
Scope: `legacy-v2-docs-root`
Report location: `C:\MyProjects\bc-core\BC_DOCS_V2_FOUNDATION_SSOT_AUDIT.md`

## Executive Verdict

The Foundation is conceptually strong, but it is not yet a clean SSOT.

The platform idea is protected by a serious spine: feed-forward execution, immutable facts, explicit evidence, contract-governed boundaries, and no downstream reinterpretation. That is the right trust foundation for enterprise data.

The current documentation risk is different: the truth is spread across Foundation, Patent, Architecture, ADRs, SOPs, DB meta-schema notes, and hidden requirement docs. Several documents correctly record gaps, contradictions, and implementation evolution, but the override rules are scattered. For a pressure test driven by synthetic data generators, this is dangerous because the SDG can silently follow one version of truth while runtime, SOP, and Foundation assume another.

The next phase should not be a sprint of random doc fixes. It should be an SSOT hardening pass with explicit authority, version, errata, and publication gates.

## Evidence Snapshot

Inventory:

- Markdown docs scanned: 1,173
- Foundation markdown docs scanned: 62
- Overall missing `status`: 594 docs
- Overall missing `authority`: 99 docs
- Foundation docs missing `status`: 39, mostly patent annexures/sections with `authority: locked`
- Foundation docs missing `authority`: 5 QA report files under the Foundation tree

Navigation and hidden authority:

- `mkdocs.yml` hides 423 docs via `not_in_nav`
- Hidden docs include 352 ADR files, 68 source reference files, and 3 architecture requirement docs
- Hidden architecture docs include `architecture/contract-requirements-v1.md`, `architecture/bf-bo-architecture-insights.md`, and `architecture/bf-sf-alias-requirements-v1.md`
- Hidden docs are acceptable only if they are indexed by an authority registry; otherwise they become invisible governing law

Reference hygiene:

- Broken structured `refs.path` links: 29
- Broken inline relative links/assets: 15
- Critical broken references point SOPs and architecture docs at non-existent Foundation paths:
  - `docs/system/foundation/contract-requirements-v1.md`
  - `docs/system/foundation/bf-sf-alias-requirements-v1.md`
  - `system/foundation/contract-chain-assembly.md`

ADR registry:

- ADR files present: 352
- `docs/decisions/index.md` states "256 decisions" and links 256 ADRs
- ADR files missing from the index: 96
- ADR authorities: 228 `authoritative`, 81 missing, 30 `retired`, 13 `evolving`

Publication tooling:

- Strict MkDocs build could not be run: `legacy v2 archive\venv` points to a missing Windows Store Python path
- Bundled Codex Python is available but does not have `mkdocs`
- This leaves the documentation publication gate non-reproducible in the current environment

## Priority Findings

### P0. Foundation Authority Precedence Is Ambiguous

Foundation index says Foundation contains the locked invariants and "every other stream references these documents." But `system/foundation/principles/execution-model.md` says: "Where conflicts arise, component references take precedence." `system/foundation/principles/data-object-model.md` marks the provisional patent as the source of truth. `system/foundation/principles/contract-chains.md` says D021 and D022 take precedence over Foundation v1 for metric/AI cardinality until Foundation v2.

That may be historically true, but it is not safe as an SSOT rule. A locked Foundation cannot also say external component references, patent text, and Architecture/ADR documents can override it without a central override ledger.

Required fix: create a Foundation authority ladder and errata mechanism. No document should locally decide that it overrides Foundation.

### P0. Known Foundation Contradictions Are Scattered Instead Of Governed

The contradictions are honestly documented, which is good. They are not governed in one place, which is the trap.

Examples:

- `system/foundation/index.md` lists Foundation gaps: Observation Contract, Reader Observation Schema, metric cardinality, SO->CO cardinality.
- `system/foundation/principles/contract-chains.md` contains `FOUNDATION-CONTRADICTION-001` and `FOUNDATION-CONTRADICTION-003`.
- `system/foundation/patent/foundation-gaps.md` includes adopted resolutions for canonical versioning, metric recomputation, and patent/Foundation alignment.

Required fix: create a Foundation Errata Ledger with one row per contradiction, the temporary governing authority, the target Foundation version, and current resolution state.

### P0. Contract Requirements Are In A Hidden, Evolving Architecture Doc But SOPs Treat Them As Locked Foundation

`architecture/contract-requirements-v1.md` is hidden from nav and has frontmatter `authority: evolving`, but the body says all 6 master shapes are locked and ready for JSON Schema authoring. Architecture index labels it "Locked." Multiple authoritative SOPs reference a non-existent Foundation path:

- `sops/oc-creation-sop.md`
- `sops/cc-creation-sop.md`
- `sops/mc-creation-sop.md`
- `sops/bf-sf-alias-sop.md`

This is a high-risk versioning trap. A human or agent can follow the SOP and fail to resolve the governing requirements, or find the hidden architecture file and misread its authority.

Required fix: promote the contract requirements doc into Foundation, or explicitly keep it in Architecture and change every SOP/reference/authority label accordingly. Do not leave it hidden and governing.

### P1. Contract Taxonomy Has Active/Retired/Provisional Drift

F03 schema inventory lists:

- 6 active family schemas
- Canonical Mapping as active
- Extraction as retired
- AI as provisional
- 3 primitives

But the same page says "3 Primitives + 6 Contract Families = 9 governed artifacts." Meanwhile `contract-chains.md` still lists `extraction` in the Source Chain, and Architecture describes active chains with Observation and Canonical Mapping.

Required fix: publish a single contract taxonomy table with these columns: artifact, artifact kind, family/primitive/supporting schema, active status, governing ADR, schema file, body doc, runtime table, and deprecation policy.

### P1. F03 Has JSON Schemas Without Body Reference Pages

The F03 inventory links body docs for Source, Admission, Observation, Canonical, Metric, and Intervention. It has JSON schemas but no body reference pages for:

- `canonical-mapping-v1.json`
- `extraction-v1.json`
- `ai-v1.json`

That creates a grammar blind spot. Even if Extraction is retired and AI is provisional, the docs need explicit pages saying so.

Required fix: add body/reference pages or retirement/provisional notices for all schema files in `contract-schemas/schemas`.

### P1. Evaluation Boundary Count Is Internally Inconsistent

`execution-model.md` defines 4 evaluation boundaries: Admission, Canonical, Metric, and Action. `evaluation-boundaries.md` says BareCount produces state at exactly 4 evaluation boundaries, then lists Observation, Admission, Canonical, Metric, and Action/Intervention.

Required fix: decide whether Observation is a non-evaluation observation boundary or a fifth boundary. Then update Foundation, Architecture, diagrams, SOPs, and runtime naming consistently.

### P1. Locked Foundation Pages Mix Law, Audit Notes, and Backlog

`system/foundation/contract-schemas/index.md` is `authority: locked`, but includes a live architectural quality audit, implementation findings, recommendations, open schema cleanup notes, and source file references.

That makes the page both law and work queue. It is understandable during migration, but risky when used as a pressure-test baseline.

Required fix: move dated audit/backlog content into QA or an implementation audit report. Keep F03 as contract grammar authority only.

### P1. ADR Registry Is Not A Complete Authority Index

ADRs are hidden from nav, but many Foundation/Architecture/SOP documents depend on them. The ADR index is stale: 352 ADR files exist, while the index links 256. There are 96 ADRs missing from the index.

Required fix: regenerate `docs/decisions/index.md` and make it a CI gate. Every ADR should have `status`, `authority`, `supersedes`, `superseded_by`, `domain`, and `focus` normalized.

### P1. Documentation Build Is Not Reproducible

The repo has `requirements.txt` and `venv`, but the venv launcher points to a missing Python path. A strict MkDocs build could not be run in this audit. That means the docs cannot currently prove publication health from a clean environment.

Required fix: add a reproducible docs build command, lock Python/tooling, and gate PRs on strict build plus link/frontmatter checks.

### P2. Status And Authority Vocabulary Is Too Loose

Across docs, `status` includes `implemented`, `published`, `authored`, `superseded`, `decided`, `authoritative`, `current`, `proposed`, `locked`, `draft`, and more. `authority` includes `evolving`, `authoritative`, `reference`, `locked`, `retired`, `decided`, and blanks.

Some combinations are meaningful; others are traps. Example: `status: evolving` plus `authority: authoritative` appears on `architecture/contract-chain-mapping-requirements.md`.

Required fix: define allowed status/authority values per document class and lint them.

### P2. Authoring Templates And SDG Docs Have Broken Links

Corrected inline-link scan found 15 broken inline references. Most are authoring template placeholders, but `system/platform/P09-platform-services/sdg/index.md` references ADR files that do not exist at the target path.

Required fix: allow explicit placeholder links only in template docs using a marker, and fix SDG ADR links before pressure testing.

## Recommended SSOT Model

Use a simple authority ladder:

1. Foundation Invariants
   - Defines what the platform is.
   - Contains only stable principles, object model, contract grammar, vocabulary, and authority rules.

2. Foundation Errata Ledger
   - The only allowed place for temporary contradictions or v1->v2 exceptions.
   - Each erratum names the affected Foundation section, governing ADR/patent/architecture source during the gap, target version, and resolution state.

3. ADR Registry
   - Records decisions and supersessions.
   - Can extend or override implementation design.
   - Cannot silently override Foundation unless linked to an erratum or Foundation version bump.

4. Architecture
   - Explains assembled system behavior.
   - Can be authoritative design guidance.
   - Cannot create locked semantic law without promotion to Foundation or ADR-backed errata.

5. SOPs
   - Define how to execute a process.
   - Must reference governing docs.
   - Must not introduce new semantics.

6. DB Meta-Schema, DDL, and Code
   - Are implementation authority.
   - If implementation disagrees with Foundation, create an implementation deviation record or erratum. Do not bury the discrepancy in prose.

7. Patent
   - Legal/protective source and conceptual evidence.
   - Operational truth should be expressed through Foundation or errata, not by asking readers to interpret patent text directly.

## Required Artifacts

Create these docs in `legacy v2 archive`:

- `docs/system/foundation/authority-ladder.md`
- `docs/system/foundation/errata-ledger.md`
- `docs/system/foundation/version-ledger.md`
- `docs/system/foundation/contract-taxonomy.md`
- `docs/system/foundation/contract-requirements-v1.md` or an explicit redirect/stub if Architecture remains the home
- `docs/system/foundation/contract-schemas/canonical-mapping-v1.md`
- `docs/system/foundation/contract-schemas/extraction-v1.md`
- `docs/system/foundation/contract-schemas/ai-v1.md`

Regenerate or enforce:

- `docs/decisions/index.md`
- all `refs.path` references
- all nav-hidden governing docs through a registry
- status/authority frontmatter for every doc class

## Methodical Remediation Plan

### Phase 0: Freeze The Foundation Baseline

Goal: prevent further drift while hardening.

- Mark Foundation docs as change-frozen except for SSOT corrections.
- No new SOP, SDG, or contract-shape change may cite an unresolved Foundation contradiction without an errata row.
- Capture the current Foundation baseline as `Foundation v1.0-current` in the version ledger.

Exit gate:

- `authority-ladder.md` and `version-ledger.md` exist.

### Phase 1: Centralize Contradictions

Goal: move scattered exceptions into one governed ledger.

- Extract current contradictions from Foundation index, Contract Chains, Patent Gaps, Architecture, and ADRs.
- Assign IDs like `FND-ERR-001`.
- For each erratum, record:
  - affected doc and line/section
  - contradiction summary
  - temporary governing authority
  - implementation behavior
  - target Foundation version
  - state: `open`, `adopted`, `rejected`, `deferred`, `closed`

Exit gate:

- No Foundation page contains an unmanaged "takes precedence" statement.

### Phase 2: Resolve Hidden Requirement Docs

Goal: remove hidden governing law.

- Promote or relocate `contract-requirements-v1.md`.
- Promote or relocate `bf-sf-alias-requirements-v1.md`.
- Update SOP refs to real paths.
- Decide whether hidden architecture insight docs are reference-only or governing.

Exit gate:

- `refs.path` broken count is zero for Foundation, Architecture, SOP, and ADR docs.

### Phase 3: Normalize Contract Taxonomy And Schema Surface

Goal: make F03 impossible to misread.

- Add a single contract taxonomy table.
- Add missing body/reference pages for Canonical Mapping, Extraction, and AI.
- Move dated audit/backlog content out of F03 schema authority.
- Explicitly state whether Canonical Mapping is a contract family, supporting schema, or chain artifact.

Exit gate:

- Every JSON schema has a doc page or explicit retired/provisional page.
- Active/retired/provisional counts match across F01, F03, Architecture, and SOPs.

### Phase 4: Rebuild ADR Authority

Goal: make decisions queryable and complete.

- Regenerate `docs/decisions/index.md` from the actual 352 ADR files.
- Normalize missing ADR authority values.
- Enforce supersession integrity.
- Add an ADR registry section for "Foundation-impacting decisions."

Exit gate:

- ADR files count equals ADR index count.
- No implemented/decided ADR is missing authority.

### Phase 5: Add Docs CI Gates

Goal: make SSOT health measurable.

Add scripts or CI jobs for:

- strict MkDocs build
- frontmatter schema lint
- broken `refs.path` lint
- relative Markdown link lint
- hidden-governing-doc lint
- Foundation contradiction lint
- status/authority compatibility lint
- schema-file-to-doc-page coverage lint
- ADR index regeneration check

Exit gate:

- A clean checkout can build the docs and produce zero P0/P1 documentation gate failures.

### Phase 6: Pressure-Test Readiness Gate

Goal: stop synthetic data from reinforcing stale assumptions.

Before SDG pressure testing:

- SDG manifests must declare which Foundation version, errata set, contract taxonomy, and schema versions they target.
- Synthetic tests must include edge cases from the errata ledger:
  - N Source Objects -> 1 Canonical Object
  - N Canonical Contracts -> 1 Metric Snapshot
  - Observation Contract as canonical-chain mapping/execution plan
  - retired Extraction behavior
  - AI provisional boundaries
  - tenant override vs platform-only contracts
- SDG outputs must be labeled as conformance data, demo data, or adversarial/error data.
- A Foundation SSOT checker should verify SDG assumptions before the run.

Exit gate:

- Pressure test can prove it is testing the current Foundation, not an accidental mixture of Foundation v1, Architecture evolution, and hidden SOP assumptions.

## Immediate Fix Order

If time is tight, do these first:

1. Add `authority-ladder.md`.
2. Add `errata-ledger.md` with the existing four Foundation gaps.
3. Promote or fix references to `contract-requirements-v1.md`.
4. Fix SOP broken references.
5. Regenerate ADR index.
6. Add schema docs/stubs for Canonical Mapping, Extraction, and AI.
7. Split audit/backlog content out of F03 schema index.
8. Repair docs build environment and add strict build/link/frontmatter gates.

## Bottom Line

The Foundation is not weak. It is overloaded.

The safest next move is to turn the documented uncertainty into governed uncertainty. Once authority, errata, taxonomy, and ADR indexing are explicit, the platform can enter pressure testing with much less risk of proving the wrong version of itself.
