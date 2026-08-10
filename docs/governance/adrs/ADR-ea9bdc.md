---
uid: DEC-ea9bdc
title: "The SAP source catalogs (ECC + S/4HANA) and the contract chain over them are declared CONTAMINATION and retired under the D564 expunge path"
description: "Declares the ~31k scraped, unauthored SAP catalog objects/fields and their SC/AC layer contamination, unlocking the D564 carve-out for governed deletion with per-object emitted evidence. Odoo untouched; canonical contracts held until the Odoo chain exists."
status: decided
date: 2026-08-10T12:44:50.654Z
project: bc-core
domain: sources
subdomain: source-catalog
focus: governance
---

# The SAP source catalogs (ECC + S/4HANA) and the contract chain over them are declared CONTAMINATION and retired under the D564 expunge path

## Context

The catalogs were produced by scraping, not by authorship, and nothing downstream that anyone trusts was built on them.

The decisive evidence is absence of authorship: created_by_name is EMPTY on all 30,683 source contracts and all 30,681 admission contracts, and 30,367 source contracts were created on a single day (2026-04-06). A contract with no recorded author was never a governed artifact. There is therefore no authored history to preserve, and the usual archive-over-delete instinct does not apply.

The operator's argument, adopted here: applying governance ceremony to entries we know are wrong is not governance, it is laundering. Versioning a wrong thing makes it look legitimate, and a legitimate-looking wrong entry costs far more at a blind spot than a deleted one. This is not theoretical — leftover catalog state cost two separate incidents on 2026-08-03: a full morning lost to a phantom 68-family duplicate crisis that was entirely archived-but-present rows, and an unresolvable ambiguity between two source contracts on account.move (sc-929yc opaque versioned vs sc__odoo__account.move semantic unversioned) where neither could be shown authoritative.

Retaining the catalogs also carries forward a false provenance surface: all 91 concept source references pointed at SAP fields nobody had verified, which reads as evidence while being none.

A correction is recorded as part of this decision. An earlier position (SES-862fe3) argued archive-over-delete and cited D564 in support. D564 is a DELETE precedent — a governed delete path with emitted evidence — so the citation was backwards and the position is withdrawn. Invariant III protects the history of legitimate acts; it was never a mandate to preserve noise that no act produced.

The declaration is made rather than assumed because the D564 carve-out is a narrow exception, and an exception invoked silently is indistinguishable from an exception abused. Naming the catalog contamination on the record is what separates a governed retirement from a convenient one.

## Decision

The SAP source catalogs — ECC (26 modules / 14,569 objects / 222,572 fields) and S/4HANA (39 modules / 16,273 objects / 259,405 fields) — together with the source contracts and admission contracts built over them, are DECLARED CONTAMINATION within the meaning of DEC-e2c1f4 (D564).

This declaration is the on-the-record act that the D564 carve-out in source.fn_source_catalog_delete_guard requires. It is invoked deliberately, not stretched: the guard is honoured, never disabled, per D564's own standing instruction.

CONSEQUENCES.
1. The 30,828 approved SAP source_object rows become eligible for governed DELETE via the carve-out, which permits the delete ONLY where a source.catalog_expunge_log row already exists for the object. Evidence-first is enforced by the trigger.
2. The 481,967 registered SAP source_field rows delete under the guard's DEFAULT path (D557 pt 4) and need no carve-out.
3. Execution is child-first — the guard's field branch reads the PARENT object's type, so the parent must still exist when its fields are deleted.
4. Evidence is per-object (30,842 rows), because a summary row cannot satisfy a per-object trigger condition, plus one sha-pinned object-manifest artifact so the act remains auditable after its subjects are gone.

EXPLICITLY FORBIDDEN. Demoting catalog_status from approved to registered in order to delete via the default path. That is a cosmetic status change whose only purpose is to defeat a guard — prohibited by DEC-ebf0b4 (D268) and a laundering of exactly the kind this declaration exists to end.

SCOPE BOUNDARIES.
- Odoo is untouched: 36 modules / 303 objects / 9,766 fields and its ~297 source contracts.
- BCF concepts and entities, the metric corpus, and the metric directory taxonomy are untouched.
- The ~19 source contracts created individually outside the two bulk-generation events are untouched in this pass (operator instruction 2026-08-10); their disposition is a separate act.
- Runtime: connectors sap-odata-v4 (s4hana) and sap-ecc-odata-v2 (ecc), one reader_flavor and one connection go with the catalog. Connector odata-v2 is protocol-category with no system_id and survives.
- The SAP canonical contract chain (23 contracts / 57 versions) is HELD, not wiped in this pass — see the timing decision below.

TIMING OF THE CANONICAL CONTRACTS. The 21 active SAP canonical contracts are retained until an Odoo canonical chain exists. Wiping them now would make grain_cc_active fail for every metric, turning all chain verdicts red; chain status is display-only and never a gate, but the D481 R3 session-close gate blocks on new reds within a session window, so closes would begin requiring routine overrides — and a gate that is routinely overridden has stopped being a gate. Invariant III version coexistence means the Odoo chain can be built alongside, after which the SAP chain is retired with no intervening zero-contract state.

PRESERVED BEFORE EXECUTION. All 91 concept_registry.concept_source_reference rows (52 S/4HANA, 39 ECC, zero Odoo) were exported to CSV with both ends, join metadata and original UUIDs (devhub ffaa90d). The catalog they point at is untrustworthy; the concept-to-field mapping knowledge is not, and is reusable when a real SAP DDIC lands.

EXECUTION REMAINS GATED. This declaration authorises nothing by itself. Execution requires Codex disposition, a reviewed expunge service or driver (no service currently writes catalog_expunge_log — only the Drizzle schema exists), a clone rehearsal, and explicit operator apply-authorization under the Database Change Protocol.
