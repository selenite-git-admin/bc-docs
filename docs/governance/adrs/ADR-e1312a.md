---
uid: DEC-e1312a
title: "Governed retirement as a distinct deletion class — a sibling carve-out in the source-catalog delete guard, with its own evidence relation"
description: "Adds source.catalog_retirement_log and a table-objects-only guard branch, so a catalog retired by decision is deletable without widening D564's contamination carve-out. Contamination and retirement stay separable forever."
status: decided
date: 2026-08-10T14:20:28.216Z
project: bc-core
domain: sources
subdomain: source-catalog
focus: governance
---

# Governed retirement as a distinct deletion class — a sibling carve-out in the source-catalog delete guard, with its own evidence relation

## Context

Contamination and retirement are different claims about the same act of deletion, and the difference must survive in the substrate.

"This row was wrongly classified and never should have existed" and "this catalog was retired by decision" carry different meanings for anyone auditing the act later. Widening D564's carve-out to include table objects would collapse them into one indistinguishable path, and would also remove a protection D564 chose deliberately: its Part-B evidence rows carry authoritative_type_text of non_object and view, which shows the narrowness was intended. Real tables were never meant to be casually deletable.

A separate relation was chosen over a discriminator column on catalog_expunge_log for three reasons. It leaves D564's table AND branch byte-identical rather than merely equivalent. It requires no backfill, so the ten existing evidence rows are not retroactively reclassified under a regime they were not written under. And it follows a doctrine this codebase already states in currency-policy-support.ts — "two questions, two homes" — where the surface a fact lives on is itself part of the answer. Asking why a row was deleted then resolves by which table holds its evidence.

The guard is the right location because it is the enforcement floor: the place where "may this row be deleted" is actually decided. A retirement permission expressed anywhere else would be a convention that a driver could bypass, which is precisely what D557 and D564 exist to prevent. The upper-layer decision already exists (D569); what is missing is the substrate's ability to admit it.

This ADR was opened as proposed rather than decided because it changes deletion semantics for the whole source catalog, not only for the SAP retirement that motivated it. The SAP case is the first application, not the justification. It moved to decided on 2026-08-11, when both capability units merged with lineage verified (bc-core #677 fa9cfed, #678 445f9ea). Decided is not implemented: no migration has been applied and no object has been retired.

## Decision

GOVERNED RETIREMENT is established as a deletion class distinct from contamination, with its own evidence relation and its own branch in source.fn_source_catalog_delete_guard().

WHY A NEW CLASS IS NEEDED. DEC-ea9bdc (D569) declared the SAP catalogs contamination on the expectation that the D564 carve-out would then admit their deletion. It does not: the carve-out is gated on object_type_code IS DISTINCT FROM 'table', so it cannot reach the 30,594 approved SAP table objects, and the default D557 pt-4 path refuses them because they are not registered/unverified. The declaration remains valid as governance; it simply does not unlock the machinery. (SAP fields need nothing — all 481,977 already delete, including I_BILLINGDOCUMENT's 10 approved fields, whose parent is a view.)

NEW RELATION: source.catalog_retirement_log. Mirrors catalog_expunge_log's shape so the two read alike: retirement_id, object_id (plain identity, NO FK — the object is about to be deleted, the same choice D564 made), object_name, object_type_code, version_id, system_name, fields_retired, decision_ref (NOT NULL), manifest_sha256, reason_text, retired_by_name, retired_at.

NEW GUARD BRANCH, additive and table-only. Permits DELETE of a source_object whose object_type_code = 'table' when a catalog_retirement_log row exists for that object AND that row's version_id equals the version reached through the object's own module AND decision_ref is present. Placed alongside, never inside, D564's branch.

NARROWING DEVICES, each deliberate.
1. Version coherence — the retirement row must name the version the object actually belongs to, so a record written for one source version cannot authorise deleting an object from another. This closes scope drift at the trigger rather than in a driver.
2. decision_ref NOT NULL — a delete must point at a recorded decision. The guard CANNOT prove the ADR exists, because decisions live in bc-docs as files and no decisions table exists in bc-core. This is therefore a discipline marker, not validation, and is recorded as such so nobody later mistakes it for proof. Free text with a DEC- pattern check; a foreign key is unavailable today and would be the better form if a decisions relation ever lands.
3. Per-object rows — no batch token, no wildcard. 30,594 deliberate inserts is itself the friction that keeps this from becoming routine.
4. table-only — non-table objects continue through D564 unchanged, so the new path can never shortcut contamination handling.

LEFT BYTE-IDENTICAL. D564's contamination branch, source.catalog_expunge_log, the guard's source_field branch, the default D557 pt-4 path, and the archive route for anything no decision has named. Nothing becomes deletable that a recorded decision has not named.

ROLLBACK. Paired -rollback.sql following D564's own pattern: drop catalog_retirement_log and restore the prior guard body verbatim. Because the amendment is additive and the contamination branch is untouched, rollback cannot disturb D564 behaviour.

NOT AUTHORISED BY THIS DECISION. No migration is applied, no object is deleted. Execution requires Codex disposition, a reviewed migration plus rollback, a reviewed retirement service (no service writes catalog_expunge_log today either — only its Drizzle schema exists), clone rehearsal, and explicit operator apply-authorization under the Database Change Protocol.

## Disposition — external audit, 2026-08-10

**ACCEPTED WITH BOUNDARY.** Response artifact
`RESPONSE-Codex-sibling-retirement-carveout-disposition-2026-08-10.md`,
sha256 `1f9b6cb9cf65ed7de0c0896773c4290253a8fdc63c7c62225d7ee00261b855ba`.

Accepted as designed: the separate `source.catalog_retirement_log` relation, the additive
table-only `source_object` guard branch, version coherence, per-object rows, and `decision_ref`
as a marker.

### The boundary, and the obligation it creates

`decision_ref` is acceptable **only** as pattern-checked discipline — **never** as database proof
that the cited ADR exists, is `decided`, or governs the object being deleted. The trigger cannot
establish authority and must not be read as though it had. **The migration, the retirement service,
and the runbook must verify ADR authority outside the trigger**, and that verification is a
precondition of writing any retirement row — not a post-hoc check on rows already written.

Concretely, the execution unit inherits three obligations:

1. **The service resolves the decision before it writes.** Given `decision_ref`, it must confirm
   the ADR file exists in bc-docs, that its `uid` matches, and that its status admits execution.
   Absent that resolution, no retirement row is written and therefore no delete becomes possible —
   the guard's fail-closed posture is preserved by refusing upstream, not by being asked to judge.
2. **The scope the ADR names is the scope that may be retired.** The service must not accept an
   object set wider than the cited decision describes. A valid `DEC-` string paired with an
   out-of-scope object is precisely the hole the pattern check cannot see.
3. **The runbook records the authority check as an evidence line**, alongside the manifest sha and
   row counts, so an auditor can see that authority was established and where.

### Status

At the time of that disposition D570 was **`proposed`**, and the disposition authorised **nothing**.

**Status now: `decided`** (2026-08-11), on the merge of both capability units — the migration and
rollback (#677, `fa9cfed`) and the retirement service (#678, `445f9ea`), reviewed head `f16cd61`,
lineage verified. What has NOT changed: no migration is applied, no DDL has run against any
database, no object has been retired, and no interlock has been granted. The status records that
the decision is settled, not that it has been carried out; `implemented` waits on application.
Each remaining step — apply under the Database Change Protocol, clone rehearsal, operator
apply-authorization — still requires its own review.
