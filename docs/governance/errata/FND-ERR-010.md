---
id: FND-ERR-010
title: "Metric groups are not grounded in governed concepts: the directory holds free JSON, unversioned concept references and aging buckets as canonical values"
status: open
authority: authoritative
affected: The Contract Grammar §Lifecycle and deprecation policy, Metric Directory Member family (as amended by DEC-6187a8); The Invariants, Invariants I and IV (explanatory disallowed behaviours); Metric Directory §6 item 2
temporary_governance:
  - DEC-6187a8 (proposed; decided together with DEC-45200d)
target_resolution: the directory is changed to match the amended Foundation through the later units (group design TSK-09855b, Unit V, the group schema, the sweep); this erratum moves to rejected when the decision unit lands and to closed when the sweep completes
opened: 2026-11-26
---

# FND-ERR-010 — Metric groups are not grounded in governed concepts

*Drafted with the decision unit DEC-6187a8 and DEC-45200d (bc-docs PR 276). Status `open` until the owner's landing grant; on landing it becomes `rejected` (the platform falls short of the amended Foundation and is changed to match it).*

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

DEC-6187a8, once decided with DEC-45200d, governs new group and member work. Until the group schema exists, no new group is opened on the free-JSON template; existing groups and their historical versions stay as recorded (Invariant III).

## Resolution state

Open. Path to closure, in order: the decision unit lands (this erratum becomes `rejected`); the group design (TSK-09855b); Unit V, typed allowed values; the group, breakdown and member schema; the sweep of every group. The erratum closes when the sweep completes and no current group version reads its parts from `template_json`.

## References

- DEC-6187a8 (the grammar commitment), DEC-45200d (the as-of schedule, decided with it), DEC-5a9dee 2c, DEC-b5c7ff, DEC-3926bf, DEC-79b62f
- `docs/governance/proposals/foundation-amendment-concept-grounded-metrics.md` (revision 6)
- `docs/reference/technical-notes/implementation/structured-group-design.md` (revision 3)
- The Contract Grammar, Metric Directory Member family; The Invariants, I and IV; Metric Directory §6
- Auditor: bc-external-audit `RESPONSE-Codex-gen-52eda8-01`, `RESPONSE-Codex-gen-52eda8-02`, `RESPONSE-Codex-gen-339991-01` (`7f2a41d1`)
- FND-ERR-009 is claimed by bc-docs PR 266; this is the next free number
