---
id: metric-catalog
order: 11.5
title: "Metric Catalog"
status: drafting
authority: authoritative
depends_on: [the-contract-grammar, business-vocabulary, contract-chain-assembly, quality-gates-and-chain-integrity, metric-evaluation]
governing_sources:
  - Foundation (scope and non-negotiability)
governing_adrs:
  - DEC-ecec75 (D068 one contract per KPI metric architecture)
  - DEC-c0290f (Metric Evaluation Engine universal formula engine)
  - DEC-c566f3 (D223 KPI Catalog AI Assistant)
  - DEC-9dce29 (Metric Specification Framework 5-Dimensional Classification)
  - DEC-6ee36c (D345 Metric discipline taxonomy)
  - DEC-e8a4d2 (D344 Definition is canonical parent of Metric Contract)
  - DEC-37967b (Function and Subfunction Taxonomy APQC PCF)
  - DEC-da4c51 (Contract Trust Chain Lifecycle)
errata_referenced: []
v2_sources: []
word_target: 4000
---

# Metric Catalog

## Scope

This chapter defines the Metric Catalog: the platform-scoped registry of metric definitions, the five-dimensional classification framework that every definition carries, the function and discipline taxonomy that organizes definitions for browsing and authoring, the lifecycle state machine that admits a definition into authoritative use, the formula tests that verify formula correctness before activation, the AI registration gates that govern at-scale onboarding under the trust contract, and the tenant view through which an authenticated tenant sees an entitled subset of the catalog.

This chapter does not redefine the Metric Contract grammar (The Contract Grammar) or the runtime metric evaluation act (Metric Evaluation). It does not define the per-act gate set in general; Quality Gates and Chain Integrity defines that gate set. It refines the gate set for the metric-registration domain. It does not define the entitlement mechanism through which tenants subscribe to catalog subsets; that mechanism is named here only at the chapter signpost level.

**Governing source.** Foundation; The Contract Grammar; Metric Evaluation; Quality Gates and Chain Integrity.

## Catalog Inventory

The catalog records two related artifacts. Metric Definition is the canonical parent. Metric Contract is the runtime artifact derived from a registered Definition.

| Artifact | Role | Scope | Persistent store |
|---|---|---|---|
| Metric Definition | Catalog entry that names the metric, classifies it across five dimensions, declares its function and discipline, and provides the formula text and variable signature | Platform | `metric.metric_definition` |
| Metric Contract | Governed runtime contract that binds the Definition's formula variables to Canonical Field codes, declares grain, temporal gate, and thresholds, and is evaluatable at the metric evaluation boundary | Platform | `metric.metric_contract` |

Per DEC-e8a4d2, the Metric Definition is the canonical parent. A Metric Contract version exists only as a child of one Definition. The Definition's classification, function, discipline, and formula are the source of truth that the Contract inherits. Per DEC-ecec75, one Metric Contract exists per KPI metric, not per module. A metric defined once in the catalog produces one Contract that activates wherever the metric is needed.

The two-artifact split keeps the inventory and classification surface governed and browsable independently of the runtime contract. The runtime contract carries grain, temporal-gate, and threshold attributes specific to evaluation. A Definition can be classified, reviewed, and approved without yet having a runtime Contract. Activation is a separate authoring act that registers the Contract.

**Governing source.** DEC-e8a4d2; DEC-ecec75; The Contract Grammar; Business Vocabulary.

## Metric Definition

**Purpose.** A Metric Definition is the catalog entry that names a metric, classifies it, and declares its formula and variable signature.

**Scope.** A Metric Definition covers the metric's name, description, five-dimensional classification, function and discipline taxonomy assignments, formula text in the platform's formula language, the variable signature, and provenance. Provenance names the authoritative source that authored or curated the definition, such as APQC, OAGIS, or an industry standard. A Metric Definition does not cover variable-to-Canonical-Field bindings, grain, temporal gate, or threshold structure. Those attributes live on the Metric Contract.

**Behavior.** A Metric Definition is registered with a definition code, name, description, classification, taxonomy assignments, formula, variable signature, and provenance. The Definition enters the lifecycle state machine starting at `seed` and proceeds through registration, review, and approval before any Metric Contract referencing it is admissible.

**Constraints.**

- A Metric Definition has exactly one classification across each of the five dimensions. A definition that is unclassified on any dimension cannot reach the `approve` state.
- A Metric Definition has exactly one function assignment and one discipline assignment.
- A Metric Definition's formula text uses the platform's formula language and references variables by name. It does not reference Canonical Field codes directly. The variable-to-Canonical-Field binding lives on the Metric Contract.
- A Metric Definition does not duplicate another Definition. Detection of likely duplication is part of the AI Registration Gates and the certification gate set.

**Failure modes.**

- If a Metric Definition is registered without a five-dimensional classification, the certification gate emits red and the Definition cannot reach the `approve` state.
- If a Metric Definition's formula text fails to parse against the platform's formula language, registration is rejected.
- If a Metric Definition is registered with provenance that does not resolve to a recognized authoritative source, registration is rejected pending revision.
- If a Metric Definition duplicates an existing Definition, the metric catalog duplication check flags the second registration. Certification withholds approval until the duplication is resolved.

**Interactions.** A Metric Definition is the parent of one Metric Contract version when the Definition reaches the `active` state. The Definition is consumed by the catalog browsing surface, by the AI Registration Gates during onboarding, and by the chain-readiness mechanism that determines whether a metric can be evaluated end-to-end.

**Governing source.** DEC-e8a4d2; DEC-ecec75; The Contract Grammar; Business Vocabulary.

## Five-Dimensional Classification

Every Metric Definition is classified across five orthogonal dimensions per DEC-9dce29. The dimensions are independent. A single Definition carries one value per dimension, and any combination of values is admissible. The dimensions govern how the platform stores, computes, surfaces, and alerts on the metric.

| Dimension | Question answered | Example values |
|---|---|---|
| Purpose | Why the metric exists | `performance`, `efficiency`, `operational`, `predictive`, `diagnostic`, `reference` |
| Shape | What output the metric produces | `monetary`, `count`, `ratio`, `duration`, `index` |
| Temporality | When the metric value is valid | `as-of`, `period`, `point-in-time`, `forecast` |
| Precision | How much trust the metric value carries | `exact`, `estimate`, `rolled-up`, `forecasted` |
| Impact | Which business lever the metric informs | `cash`, `cost`, `revenue`, `service`, `risk`, `compliance` |

The example values above are not exhaustive. The canonical value sets are recorded in the Metric Specification Framework dossier and are governed independently of this chapter.

The five-dimensional classification is the platform's metric schema. Tenant-facing surfaces filter, route, and render metrics by dimension. Alerting subscribes by dimension. The metric evaluation engine reads the temporality and shape dimensions when it applies the formula. Precision and impact are surfacing concerns.

**Constraints.**

- Each dimension is mandatory for any Metric Definition that reaches the `approve` state.
- A Metric Definition cannot carry an undeclared dimension value. Each dimension's admissible value set is governed.
- Dimensions are orthogonal. A given Definition's classification on one dimension does not constrain its classification on any other.

**Failure modes.**

- If a Metric Definition is registered with a dimension value outside the governed value set for that dimension, registration is rejected.
- If a Metric Definition is missing a dimension value at certification time, the certification gate emits red.
- If a Metric Definition's dimension assignments are inconsistent with its formula, the AI Registration Gate flags the inconsistency for human review.

**Governing source.** DEC-9dce29; The Contract Grammar.

## Function and Discipline Taxonomy

Beyond the five dimensions, every Metric Definition is placed in a hierarchical function and discipline taxonomy. The taxonomy organizes the catalog for browsing and authoring. It does not affect runtime evaluation semantics.

| Layer | Role | Source |
|---|---|---|
| Domain | Top-level business area (Finance, Procurement, Supply Chain, Workforce, Customer, Sales) | Platform-governed |
| Function | Business function within a domain (for Finance: Order to Cash, Procure to Pay, Record to Report, Treasury, Tax, FP&A) | APQC PCF, per DEC-37967b |
| Subfunction | Activity grouping within a function | APQC PCF |
| Discipline | Mandatory sub-grouping on the Metric Definition (per DEC-6ee36c, for Finance: Working Capital, P&L, Close and Control, Planning, Others) | Platform-governed; aligns with finance-domain practice |

The Discipline layer is a governed sub-grouping introduced by DEC-6ee36c. It is required on every Metric Definition. A child Metric Contract inherits the parent Definition's function and discipline. The inheritance is recorded but not separately asserted on the Contract.

**Constraints.**

- A Metric Definition has exactly one Domain, one Function, one Subfunction when the function has declared subfunctions, and one Discipline.
- A Metric Definition cannot carry a function or subfunction that is not part of the platform's APQC-aligned taxonomy.
- A Metric Definition cannot carry a discipline that is not in the governed discipline set for its domain.

**Failure modes.**

- If a Metric Definition is registered with a function not in the APQC-aligned taxonomy, registration is rejected.
- If the discipline assignment is missing, registration is rejected.
- If the Metric Contract derived from a Definition disagrees with the Definition's taxonomy assignments, chain integrity rejects the Contract publication.

**Governing source.** DEC-37967b; DEC-6ee36c; Business Vocabulary.

## Lifecycle

Every Metric Definition proceeds through a lifecycle of governed states. The lifecycle is the same across all definitions. The gate set applied at each transition is described in Quality Gates and Chain Integrity and refined for the metric domain by the AI Registration Gates section.

| State | Meaning | Permitted next states |
|---|---|---|
| `seed` | The Definition has been added to the catalog from an authoritative source but has not been formally registered | `register`, `withdrawn` |
| `register` | The Definition is registered with name, description, classification, taxonomy assignments, formula, variable signature, and provenance | `review`, `withdrawn` |
| `review` | The Definition is under AI verification and human review against the metric-registration gate set | `approve`, `register`, `withdrawn` |
| `approve` | The Definition has cleared classification, taxonomy, formula-test, and AI verification gates; it is admissible to Metric Contract registration | `active`, `withdrawn` |
| `active` | A Metric Contract version exists for the Definition; the metric is evaluatable at the metric evaluation boundary | `superseded` |
| `superseded` | A newer Metric Definition replaces this one for new authoring; existing Metric Contract versions referencing this Definition continue to apply per Invariant IV | (terminal) |

Two consequences follow from the state model.

The first is monotonic admissibility. Only `active` Definitions have evaluatable Metric Contract versions. A Definition in `seed`, `register`, `review`, or `approve` is not yet evaluatable. A Definition in `superseded` is not eligible for new Metric Contract registration, but its existing Contracts continue to evaluate.

The second is supersession discipline. When a Metric Definition is superseded, the prior Definition's `superseded_by` field references the superseding Definition. The runtime does not silently re-bind existing Metric Contract versions to the superseding Definition. Adopting the superseding Definition for an existing Contract requires registering a new Metric Contract version that references the superseding Definition. The prior Contract continues to apply at evaluation time until the new Contract activates and tenant-side binding changes reference the new version. Per Invariant IV, every reference identifies the version it touches.

**Constraints.**

- The lifecycle is non-skippable. A Definition cannot register directly into `approve` or `active`.
- A Definition cannot return to `seed` from `register` or later. Errors detected during review return a pre-approval Definition to `register` for correction.
- A `withdrawn` state is terminal. A withdrawn Definition that needs to be revived is registered as a new Definition.
- A `superseded` Definition's existing Metric Contract versions remain addressable and evaluatable. Supersession changes only future authoring eligibility.
- A formula change after `approve` creates a new Definition version or a superseding Definition. It does not mutate the approved or active Definition in place.

**Failure modes.**

- If a Definition is registered directly into `approve` or `active`, the registration is rejected.
- If a Definition's transition to `approve` lacks a recorded gate verdict for any required gate, the transition is blocked.
- If a Definition reaches `active` but no Metric Contract version exists for it, the chain integrity check records the state inconsistency and routes the Definition to manual review.
- If an approved or active Definition is edited in place, the change is rejected. The authoring act must register a new Definition version or a superseding Definition.

**Governing source.** DEC-da4c51; The Authority Model; Quality Gates and Chain Integrity.

## Formula Tests

**Purpose.** Formula Tests verify that a Metric Definition's formula text computes the expected value when given a controlled set of input values. They catch formula errors before a Definition reaches the `approve` state.

**Scope.** Formula Tests cover deterministic correctness of the formula expression: arithmetic, conditionals, aggregations, and the variable-substitution behavior the formula language defines. They do not cover variable-to-Canonical-Field bindings, grain alignment across multiple Canonical Contract versions, or threshold semantics. Those concerns are checked when a Metric Contract exists.

**Behavior.** Each Metric Definition carries one or more registered Formula Tests. A Formula Test is registered with a test code, the parent Definition reference, a controlled input set, and an expected output value. Each input variable is bound to a literal value. The platform evaluates the formula against the controlled inputs and compares the actual output to the expected output. The test passes when the values match within the formula language's declared precision tolerance for the metric's shape dimension.

**Constraints.**

- A Metric Definition cannot reach the `approve` state unless it has at least one passing Formula Test recorded.
- A Formula Test's controlled inputs must cover every variable in the Definition's variable signature. Tests with missing variables are rejected at registration.
- Formula Tests are deterministic. They do not read Canonical Object payloads. They bind variables to literal values declared on the test record.
- Formula Tests are versioned with the Definition. A pre-approval formula correction invalidates prior Formula Tests on that Definition and requires the tests to be recorded again. A post-approval formula change requires a new Definition version or a superseding Definition with its own Formula Tests.

**Failure modes.**

- If a Formula Test's actual output diverges from the expected output beyond the declared tolerance, the test fails. The Definition is held at the failing transition. For a pre-approval Definition, the test or formula is corrected and recorded again before review resumes.
- If the formula language cannot evaluate the formula against the controlled inputs, registration is rejected.
- If a Formula Test does not cover every variable in the Definition's signature, registration is rejected.
- If a Formula Test is attached to a superseded or active Definition as a formula correction, the registration is rejected. The correction must occur through a new Definition version or a superseding Definition.

**Interactions.** Formula Tests are inputs to the certification gate that admits a Definition to `approve`. They are recorded with the Definition's act history and remain addressable for audit. Formula Tests for a superseding Definition do not alter the proof history of the superseded Definition.

**Governing source.** DEC-c0290f; The Authority Model; Quality Gates and Chain Integrity.

## AI Registration Gates

The AI Registration Gates refine the AI-Verification Gates defined in Quality Gates and Chain Integrity for the metric-registration domain. They participate at the `review` state of the lifecycle and produce advisory output that informs the certification gate's verdict. AI does not write authoritative state directly. The trust contract defined in The Dual-Layer Interaction Model holds.

| Gate | What it verifies | Output |
|---|---|---|
| Classification consistency | The Definition's five-dimensional classification is consistent with its formula and provenance | Advisory annotation on the act record |
| Function and discipline alignment | The Definition's function and discipline assignments match the formula's business intent | Advisory annotation |
| Duplication detection | The Definition is checked against the existing catalog for likely duplication of name, classification, and formula intent | Advisory annotation listing candidate duplicates |
| Cross-family classification | Per DEC-9dce29, the Definition's classification is verified across multiple authoritative standards where overlapping coverage exists; semantic-family classification is recorded | Advisory annotation listing standards alignment |
| Formula plausibility | The formula's structure is reviewed for likely errors, including division-by-zero risk, aggregation grain mismatch, and sign convention mismatch | Advisory annotation listing detected risks |

The AI Registration Gates are advisory at every step. A red advisory output does not directly reject a Definition. It informs the human reviewer's decision and the certification gate's evaluation. An approved exception to an advisory finding is preserved as certification rationale and act evidence. It is not recorded as Errata unless the exception identifies a governed contradiction that requires the Errata Ledger.

**Constraints.**

- AI advisory output is recorded with evidence and timestamp on the act record.
- AI advisory output cannot override a Structural or Data-Quality gate verdict from the broader gate set.
- AI advisory output is the same across the Manual-with-AI and Programmatic authoring tracks. Track equivalence per Quality Gates and Chain Integrity holds at metric registration as it holds at every authoring act.

**Failure modes.**

- If the AI Registration Gates are unavailable when required, the Definition's transition to `review` records the unavailability and the act pauses until the gates can evaluate.
- If AI advisory output lacks recorded evidence, the output is rejected and not added to the act record.
- If AI advisory output contradicts a Data-Quality gate verdict on the same Definition, the conflict is recorded and resolved at the certification gate. AI does not silently override.
- If a reviewer approves a Definition against an AI advisory finding without certification rationale, the transition is blocked until the rationale is recorded.

**Governing source.** DEC-c566f3; DEC-9dce29; Quality Gates and Chain Integrity; The Dual-Layer Interaction Model.

## Tenant View

The catalog is platform-scoped. Every authenticated tenant sees a subset of the catalog determined by the tenant's entitlements. The entitlement mechanism is named here at the chapter signpost level only. Later runtime material defines the entitlement records, activation surface, and subscription scope.

Tenants browse the catalog through the entitled subset. Filters apply across the five-dimensional classification and the function and discipline taxonomy. A tenant cannot author Metric Definitions directly. Definitions are platform-governed, and tenants subscribe to a subset rather than extending the catalog.

**Constraints.**

- A tenant view is read-only with respect to Metric Definitions.
- A tenant cannot see a Definition that is outside the tenant's entitled subset.
- A tenant view does not expose authoring history that other tenants would consider operationally sensitive.

**Failure modes.**

- If a tenant's entitlement record has not been resolved at view time, the catalog renders empty for that tenant and records the missing entitlement state.
- If a Definition becomes superseded after a tenant has subscribed to it, the tenant view continues to show the existing entitled Definition. Transition to the superseding Definition requires a governed binding change per Invariant IV.

**Governing source.** Foundation; The Authority Model; Tenancy and Binding.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- The Authority Model: The Authority Model
- The Dual-Layer Interaction Model: The Dual-Layer Interaction Model
- Business Vocabulary: Business Vocabulary
- Contract Chain Assembly: Contract Chain Assembly
- Quality Gates and Chain Integrity: Quality Gates and Chain Integrity
- Metric Evaluation: Metric Evaluation
- Tenancy and Binding: Tenancy and Binding
