---
id: ADR-ERR-002
title: "D569 overstated the authorship evidence: one SAP source contract IS authored"
status: adopted
authority: authoritative
affected: DEC-ea9bdc (D569) — SAP catalog contamination declaration, Rationale §2
resolution: correction recorded here; D569's decision stands, its evidence sentence is amended
opened: 2026-08-10
---

# ADR-ERR-002 — D569 overstated the authorship evidence

## Contradiction summary

DEC-ea9bdc (D569) rests its central argument on an absolute:

> "`created_by_name` is EMPTY on all 30,683 source contracts and all 30,681 admission contracts …
> A contract with no recorded author was never a governed artifact."

**The universal is false.** Live substrate (verified 2026-08-10, and independently by the external
auditor during disposition of the retirement design):

| | count |
|---|---|
| source contracts, total | 30,683 |
| **unauthored** (`created_by_name` null/empty) | **30,682** |
| **authored** | **1** |

The authored row is **`sc__s4hana__i_billingdocument`**, `created_by_name = 'apex-onboarding-v1'`,
created **2026-05-10**, bound to a source object. The same actor (`apex-onboarding-v1`) created the
`sap-odata-v4` connector on the same date — so this was a real, deliberate S/4HANA onboarding act,
not a bulk artefact.

Admission contracts are unaffected: all 30,681 remain unauthored.

## Why the error occurred

The claim was derived from a `GROUP BY created_by_name` whose output showed an empty author for
every visible row, and was generalised to "all" without testing the negative case — i.e. without
asking the query *which rows have an author*. This is the same failure mode recorded four times on
2026-08-03: a predicate that returns a plausible, uniform result and is never tested against a case
known to be positive.

## What changes, and what does not

**The decision stands.** 30,682 of 30,683 source contracts were never authored, 30,367 were created
in a single day (2026-04-06), and the contamination declaration is unaffected in substance.

**The evidence sentence is amended** to: *"`created_by_name` is empty on 30,682 of 30,683 source
contracts and on all 30,681 admission contracts; exactly one source contract carries an author."*

**The authored row is already out of scope.** `sc__s4hana__i_billingdocument` was created outside
both bulk-generation events and therefore falls within the ~19 individually-created source contracts
the operator instructed be left untouched in this pass (2026-08-10). No scope change is required —
but the exclusion is now *known* rather than *incidental*, which is the point of recording this.

**Consequence for the execution unit:** the expunge scope must be defined by an explicit predicate
that excludes authored rows, not by "all SAP source contracts". A scope derived from the retracted
universal would have deleted a deliberately-authored artefact.

## Disclosure

The overstated claim reached the external auditor inside the retirement design relay
(`DESIGN-sap-retirement-2026-08-10.md`). It was caught in disposition and returned as a blocker.
This erratum is the disclosure; the design is corrected at r3.
