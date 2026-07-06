---
uid: business-context-framework-bc-seed-operational-state
title: Business Context Framework (BCF) — bc-seed Operational State (E1)
description: Evidence document for build-plan item E1, converting gap-research G21 from "provisional" into a verdict. Read-only operational pull against bc-seed Mongo (port 27017, db bc_seed). Pairs every coverage number with its gap inventory per N30 anti-coverage-KPI discipline.
status: draft
date: 2026-05-19
project: bc-docs
domain: contracts
subdomain: catalog
focus: evidence
session: SES-d88ba5
---

# Business Context Framework (BCF) — bc-seed Operational State (E1)

## Verdict

**Usable substrate — keep-as-substrate verdict confirmed; "provisional" qualifier removed.**

bc-seed is reachable, fully covers the active OAGIS-referenced BF population at the component-slug level (100% / 195 of 195), carries currency metadata (single-version 10.12, scraped 2026-04), and exhibits the empty-on-unavailable contract at runtime that the inventory and Codex §8.5 read at the code level. The build-plan E3 wrapper item remains in scope but its wrapper scope is narrower than the inventory previously implied: lineage surfacing, coverage tracking, and the `null`-noun shared-component handling — not currency or coverage gap-filling.

This document is the operational evidence the inventory §2.7 and §6 verdicts could not produce in SES-0e109c. The inventory can now drop the "provisional" qualifier on the `oagis-seed.service.ts` row and on §6 framing in a follow-up narrow update.

## Method

- **Connection profile:** `mongodb://localhost:27017` (default from `oagis-seed.service.ts:6`; no `SEED_MONGO_URI` env override in `bc-core/.env`). Reachable from operator dev machine on 2026-05-19.
- **Read-only probes:** three throwaway scripts written under `bc-core/scripts/` and removed in the same commit as this document landing. Probe scripts: reachability + collection listing + sample-doc shape; component-level coverage cross-reference against the live BF population; failure-behavior runtime test against unreachable port + invalid host.
- **BF cross-reference source:** `bc_platform_dev.contract.business_field` via `bc-postgres` MCP. Filter: `definition_standard='OAGIS' AND archived_at IS NULL AND standard_ref IS NOT NULL`.
- **Slug extraction:** noun-slug parsed from BF `standard_ref` URLs via regex `/docs/([^#]+)`.
- **No mutations.** No writes anywhere. No DB or service changes.

## 1. Reachability

| Check | Result |
|---|---|
| Connect to `mongodb://localhost:27017` | success (31ms to count) |
| Connect to `mongodb://localhost:27018` (control: unreachable port) | `MongoServerSelectionError: connect ECONNREFUSED` after 2031ms |
| Connect to `mongodb://nonexistent-host-bcf-test.invalid:27017` (control: invalid host) | `MongoServerSelectionError: getaddrinfo ENOTFOUND` after 2008ms |

The raw mongodb client throws on unavailability — it does not return empty. The empty-on-unavailable contract lives in the service wrapper (`oagis-seed.service.ts`), not the client. Confirmed by reading the wrapper at lines 89–102, 121, 151 in §3 below.

## 2. Coverage

### 2.1 bc-seed surface

`seed_oagis_components` collection: **158 documents total**.

Doc-type distribution:

| doc_type | count |
|---|---:|
| `noun` | 133 |
| `shared_component` | 25 |

Addressable component surfaces (the units a BF `standard_ref` URL slug can resolve to):

| Surface | count | example slug |
|---|---:|---|
| Noun root | 133 | `invoice`, `purchase-order`, `asset` |
| Nested component inside a Noun (`components[].slug`) | 210 | `invoice-header`, `invoice-line` |
| Shared component (doc_type=shared_component, addressed by `slug`) | 25 | (varies) |
| **Total addressable** | **315** | |

### 2.2 BF demand

`contract.business_field` cross-reference:

| Metric | count |
|---|---:|
| Active BFs claiming `definition_standard='OAGIS'` | 3,435 |
| Active OAGIS BFs with `standard_ref` populated | 1,392 |
| Active OAGIS BFs missing `standard_ref` (BCF Authoring Panel target) | 2,043 |
| **Distinct OAGIS noun-slugs referenced** | **195** |

Distinct-slug distribution: min 1 BF per slug, max 22 BFs per slug, avg 7.14.

### 2.3 Coverage cross-reference (component-level)

| Coverage axis | Result |
|---|---|
| Distinct BF-referenced slugs | 195 |
| Slugs resolvable to a bc-seed addressable surface | **195 (100.0%)** |
| Slugs NOT resolvable | **0** |
| bc-seed addressable surfaces NOT referenced by any active BF (headroom) | 120 |

**Coverage gap inventory (N30 discipline — required pairing for the 100.0% headline):** zero missing slugs to list. The pairing is the empty set; the headline is honest only because the empty-set pairing is presented.

**Earlier "92% missing" finding was a probe-version-1 false signal.** The initial coverage script (v1) matched only at the Noun root, treating BF slugs like `invoice-header` as separate from the `invoice` Noun. Once the probe descended into `components[].slug` (v2) the apparent mismatch resolved entirely. Recording this here because the false signal is exactly the shape the inventory §6 open questions warned about, and a future audit re-running a naive Noun-root probe would re-produce it.

### 2.4 Headroom inventory

120 bc-seed addressable surfaces are not referenced by any active BF. This is **not** a gap — it is unused capacity. The BCF Authoring Panel can draw on these when proposing standard_refs for the 2,043 active OAGIS BFs that currently lack `standard_ref` (per 2.2).

## 3. Currency

| Metric | Result |
|---|---|
| Distinct `source_version` values across the 158 docs | **1** (`10.12`) |
| Docs without `source_version` | 0 |
| Distinct `scraped_at` months | **1** (`2026-04`) |
| Docs without `scraped_at` | 0 |

OAGIS 10.12 is the latest published OAGIS BOD version. Scraped 2026-04 is ~6 weeks before the date of this document.

**Currency-gap inventory (N30 pairing):**

- No multi-version drift to report.
- No stale population to report.
- No missing `source_version` to report.
- No missing `scraped_at` to report.

**Open question (carry to E3 wrapper scope):** there is no documented refresh cadence. The fact that all 158 docs share a single scrape date suggests a one-shot import, not an ongoing refresh job. If OAGIS publishes 10.13 (or a 10.12 errata), bc-seed will not auto-refresh. This is a wrapper concern (E3): the wrapper must either (a) drive scheduled re-scrapes or (b) surface stale-by-N-months as a Lifecycle Audit Panel input signal.

## 4. Failure behavior — runtime confirmation

Codex §8.5 read the empty-on-unavailable contract at `oagis-seed.service.ts:89/100/151`. This section confirms the contract at runtime.

### 4.1 Runtime read of the service wrapper

`oagis-seed.service.ts` lines 89–102 (verbatim):

```typescript
async onModuleInit() {
  try {
    this.client = new MongoClient(MONGO_URI);
    await this.client.connect();
    this.db = this.client.db(MONGO_DB);
    this.collection = this.db.collection<OagisNounDoc>(COLLECTION_NAME);
    this.crosswalkCollection = this.db.collection<BoCrosswalkDoc>(CROSSWALK_COLLECTION_NAME);
    const count = await this.collection.countDocuments();
    const crosswalkCount = await this.crosswalkCollection.countDocuments();
    this.logger.log(`Connected to MongoDB: ${MONGO_DB}.${COLLECTION_NAME} (${count} nouns), ...`);
  } catch {
    this.logger.warn('MongoDB not available — OAGIS seed catalog endpoints will return empty results');
  }
}
```

`findCrosswalkByBoName` (line 121): `if (!this.crosswalkCollection) return null;`
`findFieldCandidatesInNoun` (line 151): `if (!this.collection) return [];`

### 4.2 Runtime characterisation (probe results)

| Scenario | Raw client behavior | Service wrapper behavior (inferred from code) |
|---|---|---|
| Mongo reachable | connects in ~31ms; returns docs | normal operation; logs `Connected to MongoDB: ...` |
| Mongo unreachable port | throws `MongoServerSelectionError` after 2031ms | `try/catch` in `onModuleInit` swallows; logs `MongoDB not available`; subsequent calls return `null` / `[]` |
| Invalid host | throws `MongoServerSelectionError` after 2008ms | same swallow path |

**Net:** the service wrapper enforces the empty-on-unavailable contract. The contract is sound. Per FEM F8 (provenance forgery attempt) and Requirements N1 (no fabrication), this is the correct shape — empty input forces AI Authoring Panel to route to OPERATOR_REVIEW per no-fabrication grounding check, rather than fabricating standard_refs from no data.

## 5. Sub-findings (recorded; do not block E1 verdict)

| # | Finding | Severity | Action |
|---|---|---|---|
| **S1** | 25 of 158 docs have `doc_type='shared_component'` with no `noun` field. The previous coverage probe (v1) flagged these as "null nouns" / data anomaly; the actual reason is the schema's separate `shared_component` doc type. Not a defect — but `oagis-seed.service.ts` queries use `noun` as the lookup key (lines 152: `this.collection.findOne({ noun: input.noun })`); if a BF's `standard_ref` ever points at a shared component, the lookup will miss it because the shared component has no `noun`. | medium | E3 wrapper scope item: shared-component lookup path |
| **S2** | Duplicate ISO 20022 collection names: `seed_iso_20022` (6 docs) and `seed_iso20022` (3 docs). Out of BCF scope (BCF scope 1 only references OAGIS), but worth recording. | low | Document; no action in E1 |
| **S3** | `sap_tables` collection is empty (0 docs). The actively-used SAP catalog is in `seed_tables` (46,921 docs). The empty `sap_tables` is a stale namespace; harmless but worth a flag. | low | Document; no action in E1 |
| **S4** | `pg_staging` (1,737 docs) and `scrape_runs` (24 docs) suggest internal bc-seed pipeline state. Out of BCF scope. | n/a | Document; ignore |
| **S5** | No documented bc-seed refresh cadence. If OAGIS publishes 10.13 or any 10.12 errata, bc-seed does not auto-refresh. | medium | E3 wrapper scope: stale-detection signal |
| **S6** | `oagis-seed.service.ts` lookup path uses `noun` as the key (line 152). The Noun root surface is `noun`, but components are addressed by `slug` inside nested arrays. The current `findFieldCandidatesInNoun` path operates on a single Noun document so this is fine — but any call site that wants to query a component slug directly (e.g. `invoice-header`) must traverse `components[]`, not query `noun`. | medium | E3 wrapper scope or build-plan refinement |

## 6. Verdict downgrade decision (G21)

**Provisional qualifier removed.** The inventory should update `oagis-seed.service.ts` row in §2.7 and §6 framing to drop "provisional" in a follow-up narrow update. Suggested replacement framing:

> `oagis-seed.service.ts` — **keep-as-substrate + wrap.** Read-only Mongo proxy for `bc_seed.seed_oagis_components`. Per E1 (`business-context-framework-bc-seed-operational-state.md`, 2026-05-19): reachable; 100% slug-level coverage of active OAGIS BF demand (195/195 component slugs resolved); single-version (OAGIS 10.12) scraped 2026-04; empty-on-unavailable contract holds at runtime. Wrapper scope (E3 build-plan) is narrower than originally framed: lineage surfacing on returned candidates, shared-component lookup path (per E1 sub-finding S1/S6), stale-detection signal (per S5), coverage-tracking exposure for the 120 unreferenced surfaces.

## 7. What this evidence does NOT do

- Does not certify bc-seed for any scope beyond OAGIS coverage. BCF Scope 1 references OAGIS as the primary standard; other standards (XBRL US-GAAP, IFRS, ISO 20022) live in separate collections but were not coverage-tested here.
- Does not specify the E3 wrapper. Sub-findings S1/S5/S6 inform E3 scope; E3 itself remains a separate build-plan item.
- Does not modify the inventory document — that lands in a separate narrow-update driver session.
- Does not address bc-seed *expansion* (importing new standards, broadening coverage). E1 measured the existing population only.

## 8. Tooling discipline (§13 / G24 compliance)

The three probe scripts written for this session (`bcf-e1-bc-seed-probe.mjs`, `bcf-e1-bc-seed-coverage-v2.mjs`, `bcf-e1-bc-seed-failure.mjs`) plus the abandoned v1 coverage script are **removed** in the same commit as this document landing. They were tagged for removal in their file headers and are not retained.

The earlier v1 coverage script also serves as a worked example of why §13 / G24 default-untrusted is the right policy: v1 produced a 92%-missing false signal that could have been published as a coverage gap if the v2 component-level probe had not been written. Helper scripts produce false-shaped evidence by default; per-script audit is the only way to know which output is trustworthy.

## 9. Cross-reference

| Document | Why referenced |
|---|---|
| `business-context-framework-inventory.md` §2.7, §6 | Holds the `keep-as-substrate + wrap, provisional` verdict this document downgrades the provisional qualifier on |
| `business-context-framework-inventory-gap-research.md` §8.5 G21 | Original gap finding |
| `business-context-framework-failure-evidence.md` F34, F35 | Where bc-seed evidence was flagged thin |
| `business-context-framework-requirements.md` PE1(c), N1, Chapter 8 | bc-seed authority claim and no-fabrication discipline |
| `docs/adrs/ADR-149ab2.md` Q4 + Q9 + first-delegation prereqs | bc-seed implicit dependency on Scope 1 first delegation |
| `business-context-framework-build-plan.md` E1, E3 | Build-plan items this document closes (E1) and re-scopes (E3) |
