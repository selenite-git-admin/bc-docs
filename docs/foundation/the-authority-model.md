---
id: the-authority-model
order: 7
title: "The Authority Model"
status: drafting
authority: authoritative
depends_on: [the-invariants]
governing_sources:
  - Foundation §1 (scope and non-negotiability)
  - Foundation §9 (invariants and invalid designs)
governing_adrs:
  - DEC-a4e550 (D221 ADR-first decision workflow)
  - DEC-623f8f (D370 ADR hygiene policy)
  - DEC-633b2a (D334 UID vs D-code identifiers)
  - DEC-ebf0b4 (D268 session discipline and change records)
errata_referenced:
  - FND-ERR-001
  - FND-ERR-002
  - FND-ERR-003
  - FND-ERR-004
  - FND-ERR-005
  - FND-ERR-006
v2_sources:
  - system/foundation/index.md
  - system/foundation/patent/foundation-gaps.md
  - docs/decisions/index.md
  - CLAUDE.md (session protocol and ADR hygiene policy)
---

# The Authority Model

## Scope

This chapter defines the authority model under which platform documentation and decisions are governed. It defines the three-level authority ladder, the mechanism by which contradictions are recorded and resolved, the structure and lifecycle of Architecture Decision Records, the distinction between `DEC-xxxxxx` UIDs and `Dxxx` nicknames, and the patent's status as an evidentiary track rather than an operational one. It does not redefine the execution model described in The Invariants through The Evaluation Boundaries, the contract grammar described in The Contract Grammar, or the runtime systems that store governance records and session artifacts (DevHub and Governance).

## Authority ladder

The authority model has three levels. A lower level does not silently override a higher level. Conflicts are resolved only through an explicit higher-level decision, an Errata Ledger entry, or both.

| Level | Artifacts | Governs | Change mechanism |
|---|---|---|---|
| Foundation | Foundation, The Invariants through The Evaluation Boundaries, and locked Foundation documents | Invariants, object taxonomy, contract grammar taxonomy, and boundary model | Changed only through a governed platform-version change recorded by ADR and reflected in errata where needed |
| ADR and Errata layer | Decisions, Errata, and their governed source records | Decisions, supersessions, reversals, and temporary authority over Foundation contradictions | Changed through new ADRs, supersession pairs, and errata state transitions |
| Descriptive layer | Sources and the Catalog through Risk and Vendor Management, appendices other than F and G, SOPs, runbooks, and development guides | Operational detail, implementation description, audit mapping, and platform use | Updated through chapter editing and session records, subject to higher-level authority |

The ladder is distinguished by scope and by recording discipline. Foundation defines what the platform is. ADRs and errata define how change is governed. Descriptive layers explain how the governed system operates and is implemented.

## Foundation authority

Foundation is the top authority level. All other artifacts are validated against it.

| Foundation subject | Canonical v3 reading |
|---|---|
| Execution invariants | Six invariants govern execution (The Invariants) |
| Authoritative object types | Six object types are recognized: four progression objects and two proof objects (The Object Model) |
| Grammar artifacts | Twelve governed grammar artifacts are recognized (The Contract Grammar) |
| Evaluation boundaries | Four evaluation boundaries produce authoritative state (The Evaluation Boundaries) |

Foundation does not change through descriptive editing. A Foundation-level change requires all of the following:

1. A new platform version declared through ADR.
2. Explicit Errata Ledger entries naming each affected Foundation statement where transition handling is required.
3. Coordinated updates to all affected Foundation chapters and later descriptive chapters that depend on the changed rule.

The adopted errata register includes:

- `FND-ERR-001` Observation Contract outside the earlier six-family Foundation list
- `FND-ERR-002` Reader Observation Schema dual-layer arrangement
- `FND-ERR-003` Metric cardinality N:1
- `FND-ERR-004` Source-to-Canonical cardinality N:1
- `FND-ERR-005` Object count clarification
- `FND-ERR-006` Evaluation boundary count clarification

These errata do not lower Foundation authority. They record where the current canonical reading is governed while Foundation text is aligned.

## ADR and Errata layer

The middle authority level records decisions and controlled divergence. ADRs record what was decided. Errata record where a higher-level source and the current canonical reading differ during an alignment period.

### ADR record

An Architecture Decision Record documents one decision. The canonical identifier is a `DEC-xxxxxx` UID.

| Frontmatter field | Required | Purpose |
|---|---|---|
| `uid` | Yes | Canonical `DEC-xxxxxx` identifier |
| `title` | Yes | One-line decision statement |
| `description` | Yes | One-line summary used in scanning and registries |
| `status` | Yes | One of `proposed`, `decided`, `implemented`, `superseded`, `reversed` |
| `date` | Yes | Decision date |
| `domain` | Yes | Top-level domain classification |
| `subdomain` | Recommended | Finer domain classification |
| `focus` | Recommended | Aspect within the domain |
| `supersedes` | When applicable | Prior ADR UID superseded by this record |
| `superseded_by` | When applicable | Later ADR UID that superseded this record |

The ADR body uses these sections: Context, Decision, Rationale, and, where applicable, Consequences, Non-goals, and Sequencing. The full template is defined in Decisions.

### `DEC-UID` and `D-code`

Each ADR may carry two identifiers. Only one is canonical.

| Identifier | Form | Canonicality | Use |
|---|---|---|---|
| `DEC-UID` | `DEC-` plus six hexadecimal characters | Canonical | Primary key in registries, filenames, chapter references, code references, and frontmatter |
| `D-code` | `D` plus monotonic integer | Nickname | Human shorthand in conversation, commits, and session notes |

DEC-633b2a (D334) governs the dual-identifier model. Cross-references in chapters, ADR bodies, and code use `DEC-UID`. `D-code` remains a convenience label and is not the canonical key.

The allocator assigns both identifiers atomically. Sessions do not hand-author the `D-code`.

### ADR hygiene

DEC-623f8f (D370) governs ADR hygiene. Four rules are especially important to authority handling.

| Rule | Enforcement | Effect |
|---|---|---|
| Supersession pair rule | Audit tooling and review discipline | A new ADR that supersedes an existing ADR updates the prior ADR to `superseded` in the same change |
| `closes:` commit token | Commit convention and optional automation | A commit implementing an ADR references the `DEC-UID` so status transitions can be tracked |
| Canonical reference rule | Authoring convention | Chapters, code, and registries use `DEC-UID` rather than `D-code` |
| Proposed-age limit | Audit tooling | ADRs do not remain indefinitely in `proposed` state without resolution, reversal, or split |

Additional classification and naming rules are applied during authoring and registry review.

### Errata Ledger

Errata holds the Errata Ledger. An erratum records a contradiction between a source of authority and the current governed reading, usually between Foundation text and the platform's current canonical interpretation.

| Erratum state | Meaning | Transition rule |
|---|---|---|
| `open` | Contradiction identified; temporary governing artifact named | Initial state |
| `adopted` | Current governed reading is accepted while the higher-level source is updated | Promoted from `open` when the reading is confirmed |
| `rejected` | Current implementation is incorrect and will be changed to match the higher-level source | Promoted from `open` when corrective direction is chosen |
| `deferred` | Contradiction acknowledged but resolution postponed to a named milestone | Promoted from `open` with explicit deferral reason |
| `closed` | Resolution applied and higher-level source aligned | Terminal state retained as history |

Each erratum identifies the affected authority source, the temporary governing artifact, and the target resolution version or milestone. Errata are not deleted. Closed errata remain part of the authority history.

## Descriptive layer

The descriptive layer carries operational and implementation detail. It includes later chapters in this documentation, reference materials other than F and G, SOPs, runbooks, and repository-local guidance.

| Descriptive layer may | Descriptive layer may not |
|---|---|
| Describe runtime component behavior | Introduce a new invariant |
| Describe deployment topology, operational procedures, and audit mappings | Redefine an existing invariant |
| Render schemas, APIs, and data dictionaries from governed sources | Override an ADR without a new ADR |
| Explain how governed artifacts are used in practice | Contradict Foundation without an erratum |

An apparent descriptive-layer override has only two valid explanations:

1. the chapter is describing a higher-level change already governed elsewhere, or
2. the descriptive text is incorrect and must be corrected.

## Patent as evidentiary track

Patent material is not part of the operational authority ladder. It is an evidentiary and historical track.

| Concern | Patent role | Operational authority |
|---|---|---|
| Platform concept and protected claim surface | Evidentiary and historical | Foundation plus governed ADRs |
| Runtime component behavior | Informative only | Operating Model chapters and governing ADRs |
| Contract shape and grammar | Informative only | The Contract Grammar and the Contract Schemas reference |
| Audit behavior | Informative only | Evidence and Lineage and preserved Evidence and Lineage |

Where patent language differs from current operational behavior, operational authority governs the platform. The difference is recorded in errata or ADRs when it affects the authority model.

Patent filings are not updated as part of routine operational evolution. Operational change is recorded through the authority ladder.

## Override and conflict handling

No lower-level artifact silently overrides a higher-level artifact.

| Conflict case | Required handling |
|---|---|
| Descriptive chapter appears to change an invariant | Not permitted. The chapter is corrected unless a higher-level governed change already exists |
| ADR conflicts with Foundation | Requires an Errata Ledger entry naming the affected Foundation statement and governing ADR |
| ADR supersedes prior ADR | Requires supersession-pair update in the same change |
| Later chapter contradicts earlier chapter | Not permitted without an intervening higher-level governing record |
| Platform code or behavior conflicts with ADR | Requires either a new ADR that reverses or supersedes the earlier ADR, or a code correction in line with the ADR |

Silent override is itself a governance defect. Intent does not change that classification.

## Recording a new decision

The governed mechanism for recording a new decision is the DevHub decision-record workflow described in DevHub and Governance. The operating sequence is as follows.

1. Open a governed session for the affected project.
2. Save the session plan describing the decision.
3. Invoke the decision-record mechanism with title, description, decision text, rationale, classification fields, and any supersession reference.
4. The system allocates the `DEC-UID` and `D-code` pair and writes the ADR at the canonical path.
5. If the decision supersedes an earlier ADR, update the prior ADR to `superseded` in the same change.
6. If the decision creates or resolves a Foundation contradiction, record or update the corresponding erratum in the same change.
7. Close the session with a change record referencing the `DEC-UID`.

DEC-ebf0b4 (D268) governs the session discipline associated with this procedure.

## Chapter boundaries

This chapter has defined the authority ladder, the role of Foundation authority, the ADR and Errata layer, the `DEC-UID` and `D-code` distinction, ADR hygiene rules, the patent's evidentiary status, override handling, and the operating procedure for recording a new decision. It has deferred:

- DevHub runtime components that implement session discipline and ADR recording (DevHub and Governance)
- Publication and browse surfaces for ADRs and errata (Frontend Experience)
- Compliance use of ADR and errata records (ISO 27001 Conformance and SOC 2 Conformance)
- Full ADR template and registry details (Decisions)

Subsequent chapters describe the runtime, platform, and control surfaces that operate under this model.

## References

- Foundation: Scope and non-negotiability
- Foundation: Invariants and invalid designs
- DEC-a4e550: ADR-first decision workflow (Decisions)
- DEC-623f8f: ADR hygiene policy (Decisions)
- DEC-633b2a: UID versus D-code identifiers (Decisions)
- DEC-ebf0b4: Session discipline and change records (Decisions)
- FND-ERR-001 through FND-ERR-006: Adopted errata (Errata)
- The Invariants: The Invariants
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- Frontend Experience
- DevHub and Governance
- ISO 27001 Conformance
- SOC 2 Conformance
- Contract Schemas reference
- Decisions: ADR Registry
- Errata: Errata Ledger
- CLAUDE.md: Session protocol and ADR hygiene policy
