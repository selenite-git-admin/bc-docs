---
id: business-vocabulary
order: 8.5
title: "Business Vocabulary"
status: drafting
authority: authoritative
depends_on: [the-contract-grammar, sources-and-the-catalog]
governing_sources:
  - Foundation (scope and non-negotiability)
governing_adrs:
  - DEC-aa6251 (D255 BO and BF as Contract Primitives)
  - DEC-616e02 (D103 Business Object Model)
  - DEC-d72560 (D301 Canonical Field as 3rd Contract Primitive)
  - DEC-f66378 (D292 BO-Scoped BF Composition)
  - DEC-68f2c7 (D294 company_code as 5th shared dimension)
  - DEC-339c97 (External standards provenance)
  - DEC-5017fe (Standard Field Registry)
  - DEC-683cf3 (BO tiers basic vs derived)
  - DEC-9a5dc0 (CF Boundary)
  - DEC-b5631b (Field Data Type Quality Gate)
errata_referenced: []
v2_sources: []
word_target: 3500
---

# Business Vocabulary

## Scope

This chapter defines the platform's internal vocabulary: Business Field, Business Object, and Canonical Field. It defines each primitive's role, the relationship between the primitives, the standards-sourcing discipline that authorizes each primitive, the BO-scoped composition rule for Business Fields, the five shared-dimension exceptions, and the certification lifecycle that makes a primitive available to contract authoring.

This chapter does not redefine the contract grammar that uses these primitives, the Source Catalog from which observed fields originate, or canonical evaluation runtime behavior. The Contract Grammar defines the grammar role of primitives. Sources and the Catalog defines observable external structure. Canonical Evaluation applies the vocabulary at runtime.

**Governing source.** Foundation; The Contract Grammar; Sources and the Catalog.

## Vocabulary Inventory

The platform recognizes three vocabulary primitives. Each primitive is governed and versioned like a contract-family artifact, but no primitive carries a contract envelope and no primitive emits authoritative state by itself.

| Primitive | Role | Used by |
|---|---|---|
| Business Field | Atomic business-side field definition with name, data type, description, and standards provenance | Source Contract field selection, Observation Contract source-to-business mapping, Canonical Mapping source-side identifier |
| Business Object | Composition of Business Fields representing a domain concept | Canonical Contract `business_object_code`, Observation Contract `business_object_code`, contract-chain assembly |
| Canonical Field | Atomic canonical-side field definition produced at canonical evaluation | Canonical Contract `field_selection`, Metric Contract variable bindings, Canonical Mapping target-side identifier |

The platform operates two vocabularies. Business Field is the source-side business vocabulary, and Business Object scopes Business Field composition. Canonical Field is the canonical-side vocabulary. Canonical Mapping translates from Business Field to Canonical Field at canonical evaluation.

**Governing source.** The Contract Grammar; DEC-aa6251; DEC-d72560.

## Business Field

**Purpose.** A Business Field is the atomic business-side field definition that contracts reference when they select, validate, or map data from Source Tables.

**Scope.** A Business Field covers a single business-side field definition with a code, data type, description, standards provenance, and any controlled-list constraints required for validation. Source-side identifiers are Source Fields. Canonical-side identifiers are Canonical Fields. Runtime values belong to admission acts, not to the vocabulary record.

**Behavior.** Each Business Field is registered with a unique business field code, declared data type, registered business description, and standards provenance. The platform composes Business Fields into Business Objects through membership records. Each membership record carries per-Business-Object metadata, including required status, business-key status, ordinal position, and semantic role.

**Constraints.**

- A Business Field has exactly one data type. Type widening or narrowing requires a new Business Field.
- A Business Field is BO-scoped unless it is one of the declared shared-dimension exceptions.
- A Business Field does not carry tenant-specific values.
- A Business Field must be certified before a contract version can reference it.

**Failure modes.**

- If a contract references an uncertified Business Field, contract publication is blocked.
- If a contract references a Business Field whose declared data type is incompatible with the observed Source Field type, admission rejects the affected records under the type-conformance rule.
- If a Business Field is registered without standards provenance, vocabulary registration rejects the record.

**Interactions.** Business Fields compose into Business Objects through membership records. Source Contracts select Business Fields by code. Observation Contracts map Source Field paths to Business Field codes. Canonical Mapping identifies the source-side Business Field used for Canonical Field translation.

**Governing source.** DEC-aa6251; DEC-616e02; DEC-b5631b; The Contract Grammar.

## Business Object

**Purpose.** A Business Object is a named composition of Business Fields that represents a domain concept.

**Scope.** A Business Object covers the domain concept it represents, the industry and function classification under which it sits, the Business Fields composed within it, the tier classification assigned to it, and the certification status of the composition. Tenant-specific schemas, source-system-specific tables, and runtime evaluation logic are outside this chapter.

**Behavior.** A Business Object is registered with a business object code, domain classification, tier classification, description, and standards provenance. Member Business Fields are added through membership records. The certification lifecycle approves the composition before contract versions can reference the Business Object.

**Constraints.**

- Each Business Object has exactly one tier classification: basic or derived.
- A basic Business Object represents a business event. A derived Business Object represents an accounting artifact.
- Member Business Fields are BO-scoped except for the five shared-dimension exceptions.
- A Business Object does not carry runtime data.
- A Business Object must be certified before a contract version can reference it.

**Failure modes.**

- If a Canonical Contract references an uncertified Business Object, contract publication is blocked.
- If a membership record violates the BO-scoped composition rule, vocabulary registration rejects the membership.
- If the tier classification conflicts with the member Business Fields, certification blocks approval pending correction.

**Interactions.** Business Objects are composed of Business Fields. Canonical Contracts and Observation Contracts identify scope by Business Object code. Contract-chain assembly uses Business Object identity to align observation, canonical evaluation, and metric evaluation against the same domain concept. Canonical Mapping records Business Field to Canonical Field translation per Business Object and Canonical Contract version.

**Governing source.** DEC-aa6251; DEC-616e02; DEC-683cf3; The Contract Grammar.

## Canonical Field

**Purpose.** A Canonical Field is the atomic canonical-side field definition produced at the canonical evaluation boundary.

**Scope.** A Canonical Field covers any single canonical-side field that a Canonical Contract emits or that a Metric Contract reads through a formula variable binding. Business Fields are the source-side vocabulary. Canonical evaluation runtime logic and tenant-specific extensions are outside this chapter.

**Behavior.** Each Canonical Field is registered with a canonical field code, declared data type, description, and standards provenance. Canonical Mapping records the Business Field to Canonical Field translation per Canonical Contract version. Canonical evaluation applies the mapping deterministically and produces a Canonical Object whose payload is keyed by Canonical Field codes.

**Constraints.**

- A Canonical Field is not implicit. Every Canonical Object payload key is a registered Canonical Field code.
- A Canonical Field has exactly one data type. Type widening or narrowing requires a new Canonical Field.
- A Canonical Field is admitted only when promoted from an authoritative reporting standard or otherwise governed under the CF Boundary rule.
- A Canonical Field must be certified before a Canonical Contract can reference it.

**Failure modes.**

- If a Canonical Contract references an uncertified Canonical Field, contract publication is blocked.
- If Canonical Mapping targets a Canonical Field whose data type is incompatible with the source Business Field, mapping registration is rejected.
- If a Canonical Field is registered without standards provenance, the CF Boundary rule rejects the registration.

**Interactions.** Canonical Fields are produced through Canonical Mapping at canonical evaluation. Canonical Contracts declare `field_selection` by Canonical Field code. Metric Contracts bind formula variables to Canonical Field codes. Chain-readiness checks read Canonical Field certification status before a metric chain becomes available.

**Governing source.** DEC-d72560; DEC-9a5dc0; The Contract Grammar; The Evaluation Boundaries.

## Vocabulary Sourcing

The platform admits vocabulary primitives only when each primitive is sourced from an authoritative external standard or governed equivalent. The sourcing discipline applies to registration, certification, and contract authoring.

**Primary standards.** OAGIS is the primary source for Business Objects and Business Fields when an OAGIS equivalent exists. XBRL, IFRS, and US-GAAP are admissible secondary sources when OAGIS does not cover the domain concept. Reporting-standard sources also promote Canonical Fields under the CF Boundary rule.

**Standards provenance record.** Each Business Field, Business Object, and Canonical Field carries a standards provenance record. The record names the source standard, the citation reference within that standard, and the registration timestamp. The provenance record is registered with the primitive and is not edited in place.

**Standard Field Registry.** The Standard Field Registry applies ISO 11179 metadata-registry conventions to vocabulary registration. The registry validates field names, data types, and descriptions before admitting a registration.

**Multi-standard onboarding.** The platform can admit primitives sourced from multiple standards when the same domain concept has overlapping coverage. Multi-standard onboarding produces one registered primitive with multiple provenance records. It does not produce duplicate primitives for the same concept.

**Failure modes.**

- If a primitive is registered without a standards provenance record, registration is rejected.
- If a provenance reference does not resolve to an admissible standard, registration is rejected pending revision.
- If two primitive registrations have overlapping provenance and overlapping semantics, the Standard Field Registry flags the duplicate and certification withholds approval until the duplication is resolved.

**Governing source.** DEC-339c97; DEC-5017fe; DEC-9a5dc0; The Contract Grammar.

## BO-Scoped Composition And Shared Dimensions

The platform applies a BO-scoped composition rule to Business Field membership. The rule has five named exceptions for shared dimensions. The rule and the exceptions define how Business Fields compose into Business Objects.

**Rule.** A Business Field is scoped to one Business Object. Its name and semantic role belong to that Business Object's composition. A field concept that appears in two different Business Objects is registered as two separate Business Fields, each scoped to its own Business Object. The rule prevents silent reuse across unrelated domain concepts.

**Shared-dimension exceptions.** Five Business Fields are exempt from BO-scoped composition because they are universal grain dimensions used identically across Business Objects. The exception list is closed.

| Shared dimension | Role |
|---|---|
| `company_code` | Legal entity identifier shared across all Business Objects |
| `currency_code` | ISO 4217 currency identifier shared across monetary Business Fields |
| `language_code` | ISO 639 language identifier shared across localizable Business Fields |
| `country_code` | ISO 3166 country identifier shared across geographic Business Fields |
| `unit_of_measure` | Unit identifier shared across measurable Business Fields |

A metric formula that reads multiple Canonical Contracts can use a shared-dimension Business Field as a grain key across Canonical Objects from different Business Objects. The exception is required for cross-Business-Object metric evaluation.

**Constraints.**

- A new shared-dimension exception requires a governed authority change.
- The five exception identifiers are reserved.
- A Business Object cannot register a reserved identifier under a non-shared-dimension role.
- An exception identifier carries the same name and data type wherever it appears.

**Failure modes.**

- If a Business Field registration uses a reserved identifier under a non-shared-dimension role, registration is rejected.
- If a Business Object registration includes a non-exception Business Field that already belongs to another Business Object, membership is rejected.
- If a metric formula uses a non-exception field as a cross-Business-Object grain key, chain-readiness validation rejects the metric chain.

**Governing source.** DEC-f66378; DEC-68f2c7; DEC-9a5dc0; The Contract Grammar.

## Certification Lifecycle

Each vocabulary primitive passes through a certification lifecycle before it becomes available to contract authoring. The lifecycle applies to Business Fields, Business Objects, and Canonical Fields.

| State | Meaning | Permitted next states |
|---|---|---|
| `proposed` | The primitive is registered with provenance but not yet reviewed | `reviewing`, `withdrawn` |
| `reviewing` | The primitive is under review against the certification gate set | `certified`, `proposed`, `withdrawn` |
| `certified` | The primitive is admissible to contract authoring | `superseded` |
| `superseded` | A newer primitive replaces this one for new authoring; historical references remain addressable | terminal |
| `withdrawn` | The primitive was rejected before certification | terminal |

Only `certified` primitives are admissible to new contract authoring. A `superseded` primitive remains addressable for historical contract versions. Supersession does not retroactively invalidate a contract version that already references the prior primitive.

**Gate set.** Certification records standards provenance, data type validity, name conformance with ISO 11179 conventions, BO-scoped composition for Business Fields, tier consistency for Business Objects, and CF Boundary compliance for Canonical Fields. AI-assisted verification can produce advisory output, but the governed certification record is authoritative only when preserved through the authoring path.

**Constraints.**

- A primitive cannot bypass the lifecycle.
- A primitive cannot register directly into `certified`.
- A primitive's data type cannot change during the lifecycle.
- Standards provenance is appended, not edited in place.

**Failure modes.**

- If a primitive is registered directly as `certified`, registration is rejected.
- If certification lacks a required gate result, certification is blocked.
- If a new contract version references a superseded primitive, publication is rejected and the authoring path identifies the superseding primitive.

**Governing source.** The Authority Model; The Contract Grammar; The Dual-Layer Interaction Model; DEC-b5631b.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- The Authority Model: The Authority Model
- The Dual-Layer Interaction Model: The Dual-Layer Interaction Model
- Sources and the Catalog: Sources and the Catalog
- Canonical Evaluation: Canonical Evaluation
