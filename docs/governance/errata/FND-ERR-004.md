---
id: FND-ERR-004
title: "Source-to-Canonical cardinality is N:1"
status: adopted
authority: authoritative
affected: Foundation §4.3 (canonical evaluation inputs)
temporary_governance:
  - DEC-97bb94
target_resolution: Foundation v2 SO→CO cardinality statement
opened: 2026-04-23
---

# FND-ERR-004 — Source-to-Canonical cardinality N:1

## Contradiction summary

Foundation §4.3 describes canonical evaluation as reading "one or more Source Objects" but then frames the progression as linear SO → CO, implying a 1:1 pattern in practice. In the platform implementation, a single Canonical Object is produced from N Source Objects drawn from the same or different admission boundaries. The Canonical Contract declares the multi-source composition explicitly.

## Implementation behavior

- A Canonical Contract declares its eligible Source Contract inputs, including the cardinality required (one, many, at-least-one-per-type).
- At the canonical evaluation boundary, the platform resolves the Source Object inputs per the declared specification, applies the contract's evaluation logic, and emits one Canonical Object.
- The Canonical Object's Lineage records every Source Object version consumed, preserving full multi-source ancestry.

This cardinality is N:1. It is the default for real-world canonical objects (for example, a customer canonical object composed from CRM records plus billing records plus support tickets). The Foundation's linear framing was a historical simplification.

## Temporary governance

**DEC-97bb94** codifies the N:1 cardinality at the canonical evaluation boundary and defines how multi-source inputs are declared on the Canonical Contract.

## Resolution state

**Adopted.** The platform's cardinality is correct. Foundation v2 will state that one Canonical Object may evaluate from N Source Objects, each preserved in Lineage. This erratum closes when Foundation v2 publishes the revised cardinality statement.

## References

- DEC-97bb94 — N:1 canonical evaluation
- Chapter 9 — Canonical Evaluation (describes multi-source composition and evaluation order)
- Chapter 2 — The Invariants (Invariant I cites this erratum for the cardinality correction)
- Appendix A — canonical-v1 contract schema body page
- Foundation §4.3 — affected section
