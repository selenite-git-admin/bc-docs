---
uid: DEC-ea9bdc
title: "The SAP source catalogs (ECC + S/4HANA) and the contract chain over them are declared CONTAMINATION and authorised for governed retirement"
description: "Declares the ~31k scraped, unauthored SAP catalog objects/fields and their SC/AC layer contamination, and authorises governed retirement of the source catalog with per-object emitted evidence. Mechanism by kind: 234 non-table objects via D564's contamination branch; 30,608 table objects via the DEC-e1312a (D570) sibling carve-out, which exists because D564 cannot reach them. The SC/AC contract chain retires under NEITHER and requires its own governed child-first sequence, not yet authorised. Odoo untouched; canonical contracts held until the Odoo chain exists."
status: decided
date: 2026-08-10T12:44:50.654Z
project: bc-core
domain: sources
subdomain: source-catalog
focus: governance
retirement_scope:
  systems: [ecc, s4hana]
  object_type_codes: [table]
  max_objects: 30608
---

# The SAP source catalogs (ECC + S/4HANA) and the contract chain over them are declared CONTAMINATION and authorised for governed retirement

## Context

The catalogs were produced by scraping, not by authorship, and nothing downstream that anyone trusts was built on them.

The decisive evidence is absence of authorship: created_by_name is EMPTY on all 30,683 source contracts and all 30,681 admission contracts, and 30,367 source contracts were created on a single day (2026-04-06). A contract with no recorded author was never a governed artifact. There is therefore no authored history to preserve, and the usual archive-over-delete instinct does not apply.

The operator's argument, adopted here: applying governance ceremony to entries we know are wrong is not governance, it is laundering. Versioning a wrong thing makes it look legitimate, and a legitimate-looking wrong entry costs far more at a blind spot than a deleted one. This is not theoretical — leftover catalog state cost two separate incidents on 2026-08-03: a full morning lost to a phantom 68-family duplicate crisis that was entirely archived-but-present rows, and an unresolvable ambiguity between two source contracts on account.move (sc-929yc opaque versioned vs sc__odoo__account.move semantic unversioned) where neither could be shown authoritative.

Retaining the catalogs also carries forward a false provenance surface: all 91 concept source references pointed at SAP fields nobody had verified, which reads as evidence while being none.

A correction is recorded as part of this decision. An earlier position (SES-862fe3) argued archive-over-delete and cited D564 in support. D564 is a DELETE precedent — a governed delete path with emitted evidence — so the citation was backwards and the position is withdrawn. Invariant III protects the history of legitimate acts; it was never a mandate to preserve noise that no act produced.

The declaration is made rather than assumed because each delete carve-out is a narrow exception, and an exception invoked silently is indistinguishable from an exception abused. Naming the catalog contamination on the record is what separates a governed retirement from a convenient one.

## Decision

The SAP source catalogs — ECC (26 modules / 14,569 objects / 222,572 fields) and S/4HANA (39 modules / 16,273 objects / 259,405 fields) — together with the source contracts and admission contracts built over them, are DECLARED CONTAMINATION within the meaning of DEC-e2c1f4 (D564).

WHAT THE GUARD DOES AND DOES NOT READ. source.fn_source_catalog_delete_guard never reads this
declaration and cannot: it validates EVIDENCE ROWS, not decisions. There is no decisions relation in
bc-core. On the D570 branch the guard's whole test of authority is `decision_ref IS NOT NULL` — it
asks that a decision be cited, not which one, and not whether it exists. The `^DEC-[0-9a-f]{6}$`
pattern is a CHECK constraint on source.catalog_retirement_log, enforced when the evidence row is
written, not by the trigger; it constrains shape and proves nothing either.

Authority is established OUTSIDE the trigger by DecisionAuthorityService, which resolves this ADR,
requires a status that admits execution, and bounds the act by the retirement_scope block in the
frontmatter — as a precondition of writing a D570 retirement row. Its reach is exactly that: it
governs the table path and nothing else. NO equivalent exists for the D564 view path, which has no
writer service at all, so nothing today establishes authority before an expunge row is written. The
guard's contribution, on both branches, is that nothing is deleted without evidence; it is never
that the evidence is authorised. The declaration is recorded here because that is where authority
lives, and it is invoked deliberately, not stretched: the guard is honoured, never disabled, per
D564's own standing instruction.

MECHANISM, CORRECTED (see erratum ADR-ERR-003). As first written, this decision named the D564
expunge path as its mechanism. That was wrong and is superseded. D564's carve-out is gated on
`object_type_code IS DISTINCT FROM 'table'`, so it cannot admit a single one of the 30,608 SAP table
objects declared here — only the 234 views. The tables retire under DEC-e1312a (D570), the sibling
governed-retirement carve-out, which exists precisely because D564 could not reach them. The
declaration stands; only the named mechanism changes.

  - 234 non-table objects (S/4HANA views)  -> D564 contamination branch, evidence in source.catalog_expunge_log
  - 30,608 table objects                   -> D570 retirement branch, evidence in source.catalog_retirement_log
  - the SC/AC contract chain               -> NEITHER. D570 governs source-catalog table objects only; the
                                              contract layer needs its own governed child-first sequence,
                                              which no decision has yet authorised.

CONSEQUENCES.
1. The 30,842 SAP source_object rows become eligible for governed DELETE, by kind. 30,608 tables (30,594 approved + 14 registered, verified live 2026-08-11) via the D570 branch, which permits the delete ONLY where a source.catalog_retirement_log row already exists for the object AND that row names the object's own source version. 234 approved views via the D564 branch, which requires a source.catalog_expunge_log row. Evidence-first is enforced by the trigger in both cases.
   The 14 registered tables are INCLUDED deliberately. They would satisfy the D557 default path on their own, but excluding them would leave them out of the manifest and out of the evidence log entirely — deletable later by an evidence-free act. Within a governed service run the D570 branch is evaluated before the D557 default, so all 30,608 are admitted by D570 and every one carries its own evidence row.
2. The 481,977 SAP source_field rows need no new carve-out: 481,967 are registered/unverified and delete under the guard's DEFAULT path (D557 pt 4); the remaining 10 are approved and delete via D564's existing view-parent branch, their parent I_BILLINGDOCUMENT being a view (the I_ prefix is the S/4HANA interface-view convention). By parent kind the split is 474,640 fields under tables and 7,337 under views, which is how a partial table-only phase is proved to have left the view side untouched.
3. Execution is child-first — the guard's field branch reads the PARENT object's type, so the parent must still exist when its fields are deleted.
4. Evidence is per-object (30,842 rows in total: 30,608 retirement rows + 234 expunge rows), because a summary row cannot satisfy a per-object trigger condition.
   Manifests follow the PHASES, not the total. There is no single 30,842-object manifest, because the two paths are executed as separate authorised acts and a manifest that spans both would pin a population no one act ever retires: (a) one sha-pinned 30,608-object manifest for the D570 table phase; (b) one sha-pinned 234-object manifest for the future D564 view phase; (c) a final closure artifact proving the two are DISJOINT and that their union is exactly 30,842. Until (c) exists, the catalog retirement is partial by construction and must be described that way.
   Authority lineage is NOT uniform across the two logs, and must not be described as if it were. Each of the 30,608 D570 retirement rows carries decision_ref = DEC-ea9bdc and manifest_sha256. The 234 D564 expunge rows CANNOT: source.catalog_expunge_log has neither column — it predates D570's shape — so for the view path the lineage exists only in reason_text and in the runbook. That asymmetry is a reason the view path needs its own reviewed service with a machine-readable authority boundary, not a detail to be smoothed over. In both cases this decision supplies the population authority and purpose while D570 supplies the mechanism for the tables, and the runbook must record BOTH lineages so neither is reconstructed from the other by assumption.

EXPLICITLY FORBIDDEN. Demoting catalog_status from approved to registered in order to delete via the default path. That is a cosmetic status change whose only purpose is to defeat a guard — prohibited by DEC-ebf0b4 (D268) and a laundering of exactly the kind this declaration exists to end.

SCOPE BOUNDARIES.
- Odoo is untouched: 36 modules / 303 objects / 9,766 fields and its ~297 source contracts.
- BCF concepts and entities, the metric corpus, and the metric directory taxonomy are untouched.
- The ~19 source contracts created individually outside the two bulk-generation events are untouched in this pass (operator instruction 2026-08-10); their disposition is a separate act.
- Runtime: connectors sap-odata-v4 (s4hana) and sap-ecc-odata-v2 (ecc), one reader_flavor and one connection go with the catalog. Connector odata-v2 is protocol-category with no system_id and survives.
- The SAP canonical contract chain (23 contracts / 57 versions) is HELD, not wiped in this pass — see the timing decision below.

TIMING OF THE CANONICAL CONTRACTS. The 21 active SAP canonical contracts are retained until an Odoo canonical chain exists. Wiping them now would make grain_cc_active fail for every metric, turning all chain verdicts red; chain status is display-only and never a gate, but the D481 R3 session-close gate blocks on new reds within a session window, so closes would begin requiring routine overrides — and a gate that is routinely overridden has stopped being a gate. Invariant III version coexistence means the Odoo chain can be built alongside, after which the SAP chain is retired with no intervening zero-contract state.

PRESERVED BEFORE EXECUTION. All 91 concept_registry.concept_source_reference rows (52 S/4HANA, 39 ECC, zero Odoo) were exported to CSV with both ends, join metadata and original UUIDs (devhub ffaa90d). The catalog they point at is untrustworthy; the concept-to-field mapping knowledge is not, and is reusable when a real SAP DDIC lands.

EXECUTION REMAINS GATED. This declaration authorises nothing by itself, and the retirement_scope block in the frontmatter is a bound on what may be retired, never a permission to retire it. Execution requires, in order: the D570 migration applied under the Database Change Protocol; a clone rehearsal; the conjunctive preflight gate (approved = 30594, registered = 14, total = 30608, plan.objectCount = plan.manifestLines = 30608, and the authorization naming plan.manifestSha256 verbatim — a ceiling refuses MORE and cannot detect absence); explicit operator apply-authorization; and BC_RETIREMENT_AUTHORIZED = DEC-ea9bdc, which binds the grant to this decision and does not generalise.

A TABLE-ONLY PHASE IS EXPLICITLY PARTIAL. The table path has a governed service (CatalogRetirementService, bc-core #678); the D564 view path does not — no service writes catalog_expunge_log, only its Drizzle schema exists, and D564 Part B was driven externally. Raw expunge-log inserts are not an acceptable substitute. A table phase may therefore proceed on its own, but its closure must prove: 30,608 tables and 474,640 table fields retired; 30,608 coherent D570 evidence rows; 234 views and 7,337 view fields unchanged; no shared module, version, system or container row deleted; and NO claim that SAP catalog retirement is complete. Full catalog completion stays blocked on a reviewed D564 view service with its own machine-readable authority boundary, a separate 234-object manifest, rehearsal, and authorization.
