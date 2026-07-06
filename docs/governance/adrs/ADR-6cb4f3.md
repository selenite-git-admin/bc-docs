---
uid: DEC-6cb4f3
title: "Source Systems documentation framework (bc-docs-v3)"
description: "Establish bc-docs-v3/docs/source-systems/ as a top-level governance peer with a canonical per-source document shape, v3 frontmatter conventions, mandatory proof_status discipline, and reader-flavor binding — to migrate and upgrade the v2 source pages under v2 retirement."
status: implemented
date: 2026-04-28T13:21:20.803Z
project: bc-docs
domain: documentation
subdomain: source-systems
focus: governance
---

# Source Systems documentation framework (bc-docs-v3)

## Context

legacy v2 archive has 60 source pages under `docs/reference/sources/` plus a SAP deep-dive sub-section. They follow a consistent template — frontmatter + "What BareCount Admits" / "Legal" / "Commercial" / "Technical" / "Workflow" / "References" — and reach real depth on legal/licensing for SAP and Salesforce. They are useful, not throwaway.

The v2 → v3 cutover (DEC-3395bc / D373) did not bring the source-reference content over. v3 had **zero source documentation** at the time this ADR was drafted. Several v2 pages are also stale: the SAP S/4HANA page calls OData "gray area," contradicted by DEC-d2cdb9 / D384 (SAP API Policy v.4/2026 makes Published OData the sanctioned path).

Beyond migration, v2 pages have structural gaps relative to BareCount's current operating model: no reader-flavor binding, no proof discipline, no onboarding-runbook quality, pre-v3 frontmatter.

Concrete gaps documented at draft time:
1. **Zero migration to v3** — source-reference content was not part of the D373 cutover.
2. **Stale relative to current ADR stance** — pages drift from decisions they are unaware of.
3. **No reader-flavor binding** — pages describe abstract "access models" without naming the BareCount reader flavor and admission-contract version that admits from the source.
4. **No proof discipline** — every v2 page reads as if proven. No field distinguishes "designed" / "shape-tested against simulator" / "proven first-hand against a real customer system." Violates the standing zero-claims rule (memory `feedback_zero_claims_policy.md`).
5. **No onboarding-runbook quality** — no enumeration of customer-side admin steps (SAP Communication Arrangement scenario IDs, NetSuite TBA token creation, Workday ISU setup).
6. **Frontmatter pre-v3 conventions** — no `uid` / `domain` / `subdomain` / `focus` / `proof_status` / `reader_flavors` / `admission_contract_versions`.
7. **No location in v3 layout** — Source Systems is per-source authoritative reference content, not section-narrative content. Belongs as a top-level governance peer like `data-dictionary/`.

## Decision

### 1. Location

Create `bc-docs-v3/docs/source-systems/` as a **top-level governance peer**, alongside `adrs/`, `errata/`, `data-dictionary/`, `glossary/`, `api/`, `schemas/`. Source Systems is per-source authoritative reference content; it is governance, not section-narrative content.

### 2. UI grouping

The seven governance peer collections (`adrs/`, `errata/`, `data-dictionary/`, `glossary/`, `api/`, `schemas/`, `source-systems/`) render in the docs reader sidebar under a single group label: **Reference**. Implemented in `bc-admin/src/components/docs/DocsSidebar.tsx` and surfaced through `bc-admin/scripts/sync-docs.js` `COLLECTION_LABELS` (`source-systems: { title: 'Source Systems' }`).

### 3. Canonical document shape

Every Source Systems page follows this section order:

```
---
{frontmatter — see §4}
---

# {Source Name}

{One-paragraph summary: what the source is, what BareCount admits from it,
which reader flavor admits, current proof status.}

## 1. Proof Status               ← MANDATORY, FIRST SECTION
## 2. Reader Flavor Binding      ← which flavor + which AC/OC versions
## 3. What BareCount Admits      ← metadata + business data inventory
## 4. Legal & Licensing          ← per-source policy posture, prohibitions, exemptions
## 5. Commercial                 ← customer-side cost & access models
## 6. Technical                  ← protocol, auth, paging, throttle, delta, schema discovery
## 7. Customer-Side Onboarding   ← step-by-step runbook (admin actions in source system)
## 8. BareCount-Side Onboarding  ← connection profile, credential ref, smoke test
## 9. Verified Coverage          ← entities/endpoints we have first-hand proven, with date
## 10. Known Gaps                ← entities/metrics we cannot admit yet, why
## 11. References                ← official docs, ADRs that govern this source
## 12. Changelog                 ← dated entries, ADR back-references
```

`§1 Proof Status` is mandatory and first because it sets reader expectations for everything that follows. A source with `proof_status: designed` is permitted to have rich Technical and Onboarding sections — but the reader knows nothing has been validated end-to-end.

### 4. Frontmatter (v3 conventions)

```yaml
---
uid: SRC-xxxxxx                           # generated, stable
slug: sap-s4hana
title: "SAP S/4HANA"
description: "One-line summary for the index"
type: source-systems
status: published | draft | superseded
domain: enterprise-erp                    # category — same taxonomy as v2 index
subdomain: sap                            # vendor or family
focus: governance | onboarding            # primary lens
proof_status: designed | shape_tested | first_hand_proven
last_verified_at: 2026-04-28
official_docs_url: https://api.sap.com/...
reader_flavors:                           # list — empty allowed
  - sap-s4-cloud-odata
  - sap-s4-onprem-cds
admission_contract_versions: []           # AC UIDs/versions — empty until built
governing_adrs:                           # ADR UIDs that constrain this source
  - DEC-d2cdb9                            # SAP API Policy stance
supersedes: legacy-v2/reference/sources/sap-s4hana.md   # when migrating from v2
---
```

`proof_status` semantics:
- `designed` — architecture and onboarding steps documented; nothing has run end-to-end.
- `shape_tested` — protocol path validated against a simulator or sandbox; **not** against a real customer source. Most current SAP work is here.
- `first_hand_proven` — at least one real customer instance of this source has produced metric snapshots through the BareCount chain end-to-end. Includes date and anonymised customer reference.

`proof_status` cannot be set to `first_hand_proven` without a corresponding entry in §9 Verified Coverage with an anonymised real-source reference and date. This operationalises the standing zero-claims rule (memory `feedback_zero_claims_policy.md`).

### 5. Reader-flavor binding rule

Every Source Systems page must list the reader flavors that admit from it (`reader_flavors:`) and the admission-contract versions (`admission_contract_versions:`) — or declare an empty list. An empty list is permitted but means the source is "documented but not yet admittable." This must match what is registered in DevHub's reader/AC catalogue. A page with a flavor listed that does not exist in DevHub is a doc-drift issue caught by `devhub_doc_validate`.

### 6. Migration policy (v2 → v3) — amended 2026-04-28 for v2 retirement

**Original draft policy (recorded for history):** pull-on-demand only; do not bulk-migrate; rewrite per real customer signal.

**Amendment 2026-04-28:** founder directed v2 retirement. v2 is no longer authoritative for any content; everything authoritative must live in v3. The migration policy is therefore amended to permit **bulk migration** of valid v2 source pages, with the following constraints preserved:

- **Bulk migration, not raw copy.** Each migrated page is rewritten to v3 standards — full §1–§12 sections, v3 frontmatter, `proof_status` set honestly, reader-flavor binding declared.
- **Reconciliation against current ADRs.** Each rewrite checks for drift from decisions made after the v2 page was last edited (especially DEC-d2cdb9 / D384 for SAP variants).
- **Stale or superseded pages do not migrate.** If a v2 page describes a system BareCount no longer intends to support, or a model superseded by a later ADR, the page is not carried forward; if it had any operational claim, an Errata Ledger entry records its retirement.
- **The SAP S/4HANA exemplar** (migrated in this session) defines the structural standard.
- **Tracking task** TSK-73e276 carries the per-source migration; pages are pulled in batches as time permits.

The original "pull-on-demand" policy was correct for a slow rewrite under the v2-stays-authoritative regime; under v2 retirement, it would leave v3 incomplete indefinitely. The rewrite discipline survives the policy change — only the timing rule is relaxed.

### 7. Validation

- `devhub_doc_validate` should fail a Source Systems page if:
  - `proof_status` is missing or set to `first_hand_proven` without a §9 entry.
  - `reader_flavors:` references a flavor that does not exist in DevHub.
  - Mandatory sections §1–§12 are not all present (empty section bodies are allowed; missing headers are not).
  - `governing_adrs:` lists a UID that does not exist in DevHub's decision registry.
- This validation is implemented later (parked); the schema is established here.

## Consequences

- Every Source Systems page owns a `proof_status`. No page may imply first-hand proof when only shape-tested has occurred. Hard constraint, not aspirational.
- Reader engineers trace any source page → reader flavor → admission contract version → metric chain.
- Sales/legal read any source page and know exactly what is proven, what is only designed, and which ADRs govern.
- v2 retirement bulk migration replaces the original pull-on-demand policy. v2 pages are removed from authority once their v3 successor is published; references that linked to v2 paths must be updated to v3 paths.
- Reader sidebar gains a "Reference" group header wrapping the seven governance peer collections, including Source Systems.
- New top-level governance peer is a structural change to v3 layout — no other change to v3, just the new folder under `docs/`.

## Alternatives considered

- **Place under a section folder** (e.g. `onboarding/sources/` or `implementation/sources/`): rejected. Source Systems is per-source reference content, not procedure (`onboarding/`) and not implementation narrative (`implementation/`). It belongs as a peer like `data-dictionary/`.
- **Keep pull-on-demand migration policy under v2 retirement**: rejected. Under retirement, pull-on-demand would leave v3 incomplete indefinitely while authority migrates away from v2.
- **Skip the framework, write the SAP page free-form**: rejected. The framework is the point — the SAP page is the exemplar that proves the framework. Without it, the next source page diverges.
- **Use existing v2 frontmatter shape**: rejected. v3 has tighter conventions (uid, domain, subdomain, focus); source pages must match.
- **Render the seven governance collections flat in the sidebar (no group label)**: rejected. Founder cold-read showed the flat list is harder to scan as the collection count grows; "Reference" group disambiguates governance peers from chapter sections.

## Procedure to flip to `decided`

1. User reads this ADR and the SAP S/4HANA exemplar.
2. On acceptance, status flips `proposed → decided` via `devhub_decision_update`.
3. The implementation work — folder rename, index page, SAP exemplar, sync-docs.js, DocsSidebar.tsx, outline.md, parked migration task — is shipped in the same session that records this ADR. Once committed, status flips `decided → implemented`.
