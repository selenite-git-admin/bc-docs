---
uid: DEC-e0a8ca
title: "One frontmatter vocabulary for bc-docs: one authority axis for every document kind, one status axis per kind, enforced in CI and read by the DevHub scanner"
description: "Declares the four authority values and the per-kind status values for every bc-docs file, a shrink-only CI check, and the DevHub scanner change to read both axes; carries the operator's open question on collapsing source-derived, derived and projection."
status: proposed
date: 2026-09-30T11:06:20.497Z
project: bc-docs
domain: docs
subdomain: documentation-system
focus: frontmatter-vocabulary
---

# One frontmatter vocabulary for bc-docs: one authority axis for every document kind, one status axis per kind, enforced in CI and read by the DevHub scanner

## Context

The Documentation System chapter states an authority axis (authoritative, reference, evidentiary) and a status axis (drafting, reviewing, locked, superseded, retired) and cites outline.md, a file that has never existed in the repository, as its source. No ADR defines either axis. Verified on 2026-09-30 at bc-docs main fa17b924: the 1,217 Markdown files under docs/ use 37 distinct authority values and 47 distinct status values. The DevHub scanner (barecount-devhub src/lib/doc-scanner.js) normalises authority to five values of its own (locked, authoritative, evolving, reference, retired), maps evidentiary and source-derived to evolving, and does not read the file's status at all; the registry column documents.status_code is the registry's own freshness lifecycle (DEC-a4e550), not the file's declared status. The bc-admin reader (bc-admin src/components/docs/types.ts) already implements exactly the chapter's two axes. The operator approved Part D decision 3 of the report "Controller charters from documentation" on 2026-09-30: one vocabulary, a CI check, a scanner change and a sweep, with the collapse question left to the operator. Document kinds have real and different lifecycles (an ADR is proposed then decided then implemented; an erratum is open then adopted; a docket is draft then published), so one status list for every kind would flatten meaning; one authority list for every kind loses nothing, because authority answers the same question for every file: where does this file's force come from. A CI check that failed on the current estate would block every bc-docs pull request, so the check carries a shrink-only baseline until the sweep empties it.

## The authority axis: one list for every document kind

Every Markdown file under `docs/` that carries frontmatter declares `authority` with exactly one of four values.

| Value | Meaning | Examples |
|---|---|---|
| `authoritative` | The file is where a rule, structure or procedure is declared. When it disagrees with another file, this file wins. | Foundation and section chapters, errata, the section openers |
| `reference` | The file describes, indexes or projects something whose authority lives elsewhere (code, a database, a governed object, another chapter). | Source-system dockets, technical notes, hand-written coverage tables, the glossary |
| `evidentiary` | The file records what happened: an audit, a closeout, a ledger, a work record. It is never edited after it is finalised except to mark it superseded or retired. | Everything under `docs/evidence/` |
| `generated` | A generator emitted the file from a named source at a named commit. It is never edited by hand; it is regenerated. | The data dictionary, the code index, the lifecycle and enforcement-surface maps |

The following values are retired and mapped: `source-derived` becomes `generated` (identical meaning); `derived`, `informative` and `descriptive` become `reference` (hand-written files whose authority is elsewhere); `draft-authoritative` becomes `authoritative` (the status axis, not the authority axis, carries the draft state). `projection` is not an authority value: it is the value of the docket field `authority_role`, which ADR DEC-8570d4 Amendment 1 defines as normative for source-system dockets; that field stays as it is, and every docket also declares `authority: reference`.

Architecture decision records do not carry `authority`. An ADR's force is its status; the 273 ADR files that carry an `authority` key today (values `authoritative`, `retired`, `evolving`, `reference`) lose it in the sweep.

These four values record where a file's force comes from within its own level of the authority ladder that The Authority Model and DEC-5a9dee define; they are not a second ladder. The ladder's five levels are Foundation, the ADR and errata layer, the generated enforcement map, the live substrate, and the descriptive layer. `authoritative` on a section chapter means the declaring document for its subject inside the descriptive layer; it is never authority over a Foundation chapter, an ADR, an erratum, the enforcement map or the live substrate, and a file marked `authoritative` wins only against files at its own level or lower. A `generated` file's force is its source at the named commit, and the enforcement-surface and lifecycle maps sit at the ladder's generated-enforcement-map level, above every descriptive chapter, so `generated` is not read as ranking below `authoritative`. Document lifecycle words are declared here and in `documentation-system.md`; the status words of metrics and tenants are declared in `docs/reference/vocabulary.md` under DEC-c897cd, and neither page governs the other's words.

## The status axis: one list per document kind

| Kind | Path rule | Status values | Source of the lifecycle |
|---|---|---|---|
| Chapter | `docs/overview/`, `foundation/`, `operating-model/`, `implementation/`, `ai/`, `development/`, `onboarding/`, `operations/`, `compliance/`, and `docs/reference/` files that are neither dockets nor generated | `drafting`, `reviewing`, `locked`, `superseded`, `retired` | Documentation System chapter (unchanged). Binding force still requires `authoritative` plus `locked`. |
| Architecture decision record | `docs/governance/adrs/ADR-*.md` | `proposed`, `decided`, `implemented`, `superseded`, `reversed` | DEC-623f8f (unchanged) |
| Erratum | `docs/governance/errata/*-ERR-*.md` | `open`, `adopted`, `rejected`, `deferred`, `closed` | `docs/governance/errata/README.md` (unchanged) |
| Source-system docket | `docs/reference/source-systems/**` | `draft`, `published`, `retired` | DEC-8570d4 template; `verification_required` becomes `draft` |
| Generated reference | `docs/reference/data-dictionary/`, `code-index/`, `api/`, `schemas/`, `lifecycle-map.md`, `enforcement-surface-map.md` | `generated`, and the keys `generator`, `source_repo`, `source_commit`, `generated_at` are required | This decision. The two maps carry no frontmatter today; their generators must emit it. |
| Evidence record | `docs/evidence/**`, `docs/governance/plans/**` | `drafting`, `locked`, `superseded`, `retired`; `authority` is always `evidentiary` | This decision. A finalised record is `locked`. The decision a record was produced under moves from the `authority` key, where 100 files carry it today as free text, to `governing_adrs`. |
| Archive | `docs/archive/**` | `retired` | This decision |
| Exempt | `docs/README.md`, `docs/NAVIGATION.md`, every `README.md` that is a folder index, `docs/assets/**` | none required | Navigation files |

**Foundation's lock and the `status` field.** Binding force for a chapter requires `authoritative` plus `locked`, unchanged. Foundation is the top of the ladder and binds regardless of this rule: The Authority Model makes Foundation the top authority and `foundation-overview.md` declares it locked, so Foundation's force comes from the model, not from a `status` value, even though all ten Foundation chapters still carry `status: drafting`. Moving those chapters to `status: locked`, so the field matches the model, is a Foundation-level act for the Architect; it is named here as a consequence, owned under TSK-65f57d, and is not performed by this ADR. Until then the gap between the declared lock and the `status` field is recorded, not resolved here.

## The declaring document

`docs/development/documentation-system.md` remains the chapter that declares the axes. Its "bc-docs as the SSOT" table is updated to the four authority values and the per-kind status table above, and its governing source becomes this decision instead of `outline.md`. No other chapter restates the vocabulary; chapters cite this one.

## Enforcement in bc-docs

`scripts/docs-control/audit_frontmatter.py` (Python standard library only, like `audit_adrs.py`) classifies every file by the path rules above and checks both axes and the required keys per kind. It runs in `.github/workflows/adr-hygiene.yml` on every push to main and every pull request. It fails when any file is outside its kind's vocabulary unless the file is listed in the shrink-only baseline `docs-control/frontmatter-baseline.json`, and it also fails when a baseline entry has become clean and was not removed, so the baseline can only shrink. Writing the baseline is a local act (`--write-baseline`), never a CI act. The sweep empties the baseline; after that the file is deleted and the check runs bare.

## The DevHub scanner

The scanner reads both axes from the file. `authority` is recorded as one of the four values, or `unknown` when the key is missing or carries another value; nothing is normalised silently any more. The file's `status` is recorded in a new column of its own. The registry's existing `status_code` (the freshness lifecycle of DEC-a4e550: unvalidated, fresh, possibly_stale, stale, retired) is unchanged and stays separate from the file's declared status. The CHECK constraint on `documents.authority_code` changes from the scanner's five values to the four values plus `unknown`, and the new column is added. Both are changes to the DevHub database and take the operator's separate approval under the database change protocol before they are applied; the `devhub_doc_list` filter and the REST document routes change with them. The reader gains `generated` in its `DocAuthority` type; nothing else in the reader chain changes.

## The sweep

One mechanical pull request per repository after this decision is `decided`, reviewed through the gen- exchange. Counts from `audit_frontmatter.py` on 2026-09-30 at fa17b924, 1,205 files checked and 13 exempt: 56 chapter-kind files (27 in the nine sections, 27 technical notes, 2 other reference files), 26 generated files (`source-derived` to `generated`) plus the 2 generated maps that carry no frontmatter (generator change), 94 dockets (add `authority: reference`; 1 status correction), 273 ADR files (drop `authority`; 1 status outlier), 290 evidence records (authority; the status mapping is done by each record's owning controller from the table the check's report lists), 5 archive files. The check's report `docs-control/reports/frontmatter-audit.md` is the sweep worklist; the baseline holds the same 744 paths and only shrinks. Docs owns form and placement; the owning controller of each chapter confirms its classification where the mapping marks a judgement call.

## The operator's question

Do `projection`, `source-derived` and `derived` collapse into `generated`, or stay?

Recommendation: `source-derived` collapses into `generated` (28 files; the same meaning). `derived` does not: the six files that carry it are hand-written coverage tables under `docs/implementation/` that nothing generates, so they become `reference`. `projection` stays where it is, as the docket field `authority_role` defined by DEC-8570d4, and dockets declare `authority: reference` beside it; collapsing it would amend DEC-8570d4 and re-touch 95 files for no gain in meaning.
