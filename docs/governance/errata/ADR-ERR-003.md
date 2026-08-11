---
id: ADR-ERR-003
title: "D569 names the wrong mechanism: the SAP tables cannot be retired under the D564 expunge path"
status: adopted
authority: authoritative
affected: DEC-ea9bdc (D569) — title, description, and every body sentence citing the D564 carve-out
resolution: correction recorded here; D569's declaration stands, its named mechanism is superseded by DEC-e1312a (D570)
opened: 2026-08-11
---

# ADR-ERR-003 — D569 names a mechanism that cannot reach its own subject

## Contradiction summary

DEC-ea9bdc (D569) declares the SAP source catalogs contamination and states, in its title and
description, that they are:

> "retired under the **D564 expunge path**" … "unlocking the **D564 carve-out** for governed deletion"

**The named mechanism cannot act on the declared subject.** `source.fn_source_catalog_delete_guard()`
gates the D564 carve-out on:

```sql
IF OLD.object_type_code IS DISTINCT FROM 'table' THEN   -- contamination: NON-TABLE only
```

So D564 cannot admit the deletion of a single one of the **30,608** SAP `table` objects D569
declares. Live counts (verified 2026-08-11, and independently by the external auditor during
disposition of the amendment proposal):

| system | kind | catalog_status | count |
|---|---|---|---|
| ecc | table | approved | 14,566 |
| s4hana | table | approved | 16,028 |
| ecc | table | registered | 3 |
| s4hana | table | registered | 11 |
| s4hana | view | approved | 234 |

**30,594 approved + 14 registered = 30,608 tables**, none reachable by D564. The 234 views are the
only SAP objects D564's branch can admit.

## What changes, and what does not

**The declaration stands.** The catalogs are contamination; that judgement is unaffected. What is
wrong is the *mechanism sentence*, and only that.

**The mechanism is superseded by DEC-e1312a (D570)**, the sibling governed-retirement carve-out,
which exists precisely because D564 could not do this. Corrected reading:

- **non-table objects** (234 SAP views) — delete via D564's existing contamination branch;
- **table objects** (30,608) — retire via D570's `catalog_retirement_log` branch;
- **the SC/AC contract chain over them** — retires under **neither**. D570 governs source-catalog
  table objects only. The contract layer requires its own governed, child-first sequence, and no
  decision has yet authorised it.

That third line is the one most likely to be misread, and it is why this erratum exists as a
record rather than as a frontmatter edit: a reader who takes D569's title at face value would
conclude a single mechanism swept catalogs and contracts together.

## Why the error occurred

D569 was written on 2026-08-10 on the expectation that declaring contamination would unlock the
existing carve-out. The narrowness of that carve-out — `IS DISTINCT FROM 'table'` — was established
afterwards, in r7/r8 of the retirement design, and is what motivated D570. The decision was correct
about intent and wrong about mechanism, because the mechanism had not yet been read closely enough
when the decision was recorded.

## Consequence for execution

`decision_ref` on every retirement evidence row remains **DEC-ea9bdc**: D569 supplies the
population authority and purpose, D570 supplies the mechanism. The runbook must record **both**
lineages — authority and mechanism — so that neither can be reconstructed from the other by
assumption.

## Disclosure

The obsolete D564 framing has been carried in D569's title and description since 2026-08-10 and was
relayed to the external auditor inside the amendment proposal. It was returned as a required
correction. This erratum is the authoritative record, following the ADR-ERR-002 precedent; D569's
own body supersession is applied with the scope amendment under operator authorization.
