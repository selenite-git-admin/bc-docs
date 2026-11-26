---
id: FND-ERR-010
title: "Metric groups are not grounded in governed concepts: the directory holds free JSON, unversioned concept references and aging buckets as canonical values"
status: open
authority: authoritative
affected: The Contract Grammar §Lifecycle and deprecation policy, Metric Directory Member family (as amended by DEC-6187a8); The Invariants, Invariants I and IV (explanatory disallowed behaviours); Metric Directory §6 item 2
temporary_governance:
  - DEC-6187a8 (proposed; decided together with DEC-45200d)
target_resolution: Foundation and the Metric Directory chapter are updated in the same landing as DEC-6187a8 (the-contract-grammar.md, the-invariants.md, metric-directory.md §6 item 2); the erratum lands closed
opened: 2026-11-26
---

# FND-ERR-010 — Metric groups are not grounded in governed concepts

*Drafted with the decision unit DEC-6187a8 and DEC-45200d (bc-docs PR 276). Status `open` until the owner's landing grant; it lands `closed`: the resolution is applied in the same landing, by updating Foundation and the Metric Directory chapter themselves.*

## Contradiction summary

The amended grammar (DEC-6187a8) states that a metric group version is made of pinned entity or concept versions and typed governed parameters, that members select governed values and never classify records, and that an age band is a typed temporal choice. The platform and the earlier text say otherwise:

- A group's parts other than its grain and, sometimes, its date are free JSON (`metric_directory.group_version.template_json`); 11 documents carry `closing_concept_id` inside JSON.
- `group.temporal_anchor_concept_id` points at a concept identity, not a concept version; the group version's grain and anchor columns have no foreign key.
- Allowed values are a JSONB array (`business_concept_version.canonical_value_set`), and a member's discriminator values sit in `governed_values_json`.
- `metric-directory.md` §6 item 2 makes aging buckets canonical values, so a record's age would be stamped rather than selected relative to P.

Counts were read live from `bc_platform_dev` on 2026-11-26 (proposal section 1); re-read before acting.

## Implementation behavior

The directory accepts a group whose meaning is held in JSON keys and an anchor named without a version. The realization relation of DEC-5a9dee 2c compares a metric contract with that intent without a role-by-role grammar. No incident is attributed to the gap; the auditor's gen-52eda8-02 findings (a reversed or gross-for-residual value from one ungrounded group) are the failure class it would allow.

## Temporary governance

Until the landing, the current Foundation text and DEC-5a9dee 2c govern. On landing, DEC-6187a8, decided together with DEC-45200d, governs, and the amended Foundation text states it. Existing groups and their historical versions stay as recorded (Invariant III).

## Resolution state

Open until landing; lands `closed`. The resolution is a Foundation update, not an implementation change: the same landing adds the grammar commitment to `the-contract-grammar.md` (Metric Directory Member family), the two disallowed behaviors to `the-invariants.md` (Invariants I and IV), and corrects `metric-directory.md` §6 item 2. Bringing the directory's tables to the amended grammar is the later units' work (the group design TSK-09855b, Unit V, the group, breakdown and member schema, the sweep), each its own act; it is not tracked by this erratum.

## References

- DEC-6187a8 (the grammar commitment), DEC-45200d (the as-of schedule, decided with it), DEC-5a9dee 2c, DEC-b5c7ff, DEC-3926bf, DEC-79b62f
- `docs/governance/proposals/foundation-amendment-concept-grounded-metrics.md` (revision 6)
- `docs/reference/technical-notes/implementation/structured-group-design.md` (revision 3)
- The Contract Grammar, Metric Directory Member family; The Invariants, I and IV; Metric Directory §6
- Auditor: bc-external-audit `RESPONSE-Codex-gen-52eda8-01`, `RESPONSE-Codex-gen-52eda8-02`, `RESPONSE-Codex-gen-339991-01` (`7f2a41d1`)
- FND-ERR-009 is claimed by bc-docs PR 266; this is the next free number
