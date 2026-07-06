---
uid: DEC-1ce490
title: "contract.business_field is the certified BF-BO catalog"
description: "BF admission requires evidence-backed contextual correctness via six gates; OAGIS is evidence, not authority; certification is ledgered, not inferred."
status: decided
date: 2026-05-16T03:53:50.346Z
project: bc-core
domain: contract
subdomain: business-field-catalog
focus: admission, governance
---

# contract.business_field is the certified BF-BO catalog

## Context

contract.business_field currently mixes a certified BF-BO vocabulary catalog with an imported-vocabulary inventory. 462 of 7,062 rows have status_code='certified' with templated placeholder definitions and zero anchor evidence; the broader population shows the same shape at scale (6,237 in BOs, only 1,962 with aliases, 1,400 with SDA evidence, 316 referenced by cc_field_mapping). Treating both jobs as 'certified' is an admission-boundary failure: certification is inferred from import metadata rather than emitted as evidenced state, violating Foundation Invariant VI (evidence emitted, not inferred). Downstream cost is not only direct runtime references — FieldMappingService.suggest() and CanonicalWizardService read the catalog to suggest BFs during authoring, so uncertified rows are a latent attack surface on every future authoring decision.

# Decision

`contract.business_field` is, by definition, the certified BF-BO catalog. A row exists in the table only after passing a layered admission pipeline whose human decision step is recorded in `contract.certification_record`. Imported vocabulary that has not passed the pipeline does not live in `contract.business_field`; it lives as filesystem artifacts (OAGIS scrape JSON, SDA discovery output) until promoted.

The intent is not coverage. The intent is that any join, suggestion, or binding made through `contract.business_field` carries a defensible semantic warrant.

## Audit evidence (calibrated, 2026-05-16)

This decision is grounded in the calibrated audit at `bc-core/scripts/audit-output/d408-bf-admission-audit-calibrated-2026-05-16T04-50-46-684Z.{md,json,per-bf.jsonl}` (sibling script: `bc-core/scripts/audit-bf-admission-d408-calibrated.mjs`). Invariant: `contract.certification_record action_code='remediate_bf_semantics'` held at 1,392 pre and post.

**Trust-tier Venn (7,062 BFs total, highest tier wins):**

| Tier | Count | Meaning |
|---|---:|---|
| T0_only | 605 | No anchors at all |
| T1_only | 3,536 | In a BO, no required/BK, no alias, no SDA, no CC |
| T1_req_or_bk | 31 | BO membership with `required`/`business_key` |
| T2 | 1,211 | Has alias |
| T3 | 1,363 | Has SDA evidence |
| T4 | 316 | Referenced by `cc_field_mapping` |

**Hard gate failures (calibrated; G2 is advisory and not counted here):**

| Gate | Failing BFs |
|---|---:|
| G1 lexical | 779 (682 banned templates, 97 too-short) |
| G3 type | 19 (incoherent representation_term vs data_type) |
| G4 anchor | 4,141 (= T0_only + T1_only) |
| G5 evidence | 1,400 (only OAGIS structural) |

**T4 canary (the operational reality — CC-mapped BFs already steering canonical pipelines):**
316 total; **15 hard fails** (G1=11, G3=4, G5=0); 16 are naming-policy advisory only.

**Phase 1/2 re-audit (SDA-evidenced cohort):**
1,400 SDA-evidenced BFs; **13 hard fails** (all `definition_too_short` on `*_uri` / `*_brand_name` / `*_product_name` rows); **1,387 pass**. Phase 1/2 work is sound; the 13 are correction candidates, not evidence of bad methodology.

**Demotion sizing (cross-tabs):**

| Cohort | Count |
|---|---:|
| T1_only ∩ G5 structural | 946 |
| T1_only ∩ G1 fail | 329 |
| T1_only ∩ G1 fail ∩ G5 structural | 259 |
| Broken-fallback definitions total | 682 |
| Broken-fallback ∩ no anchor | 370 |
| Broken-fallback ∩ CC mapping | 4 |

The original 462 reported in TSK-9515d5 Phase 3 was a narrower slice of the broken-fallback cohort. The true comparable population is **370** (broken-fallback ∩ no-anchor) or **259** (the three-way intersection of bad definition, no anchor, no evidence). **4 rows** are the highest-severity cohort: bad definition AND already active in canonical pipelines.

## Context

`contract.business_field` currently holds 7,062 rows of mixed provenance. Phase 3 of TSK-9515d5 surfaced 462 rows with `status_code = 'certified'` whose definitions are templated placeholders (`"<property> from OAGIS undefined"`) and which have zero anchor evidence (0 BO-required, 0 business keys, 0 `cc_field_mapping` references). The count breakdown at scale: 6,237 BFs participate in some BO but only 1,962 have aliases, 1,400 have SDA evidence, 316 are referenced by `cc_field_mapping`.

The table is doing two jobs at once: a certified BF-BO vocabulary catalog and an imported-vocabulary inventory. Treating both as equally `certified` is an admission-boundary failure for the catalog itself.

### Foundation gate

- **Repair location:** B (contract semantics) with a side at A (admission boundary for the BF catalog itself).
- **Why not upper layers:** none — BF is the foundational vocabulary substrate.
- **Why not lower layers:** lower-layer cleanups would compensate for an unspecified admission rule. The rule must exist first.

## 1. Two-axis state model

`status_code` (existing) continues to carry platform-wide lifecycle states: `draft`, `active`, `superseded`. A new column `catalog_state_code` carries the admission-pipeline state.

| `catalog_state_code` | Meaning |
|---|---|
| `candidate` | Row exists but has not yet been scored by the machine gates |
| `gates_passed` | Machine gates G1–G5 have passed; awaiting human action (G6) |
| `gates_failed` | Machine gates have flagged blocking issues; not usable |
| `certified` | Human reviewer has minted certification; ledgered in `certification_record` |
| `recertify_pending` | Re-review required due to a triggering event (see §5); not a calendar state |
| `demoted` | Human reviewer has explicitly demoted; ledgered; `archived_at` set |

A BF is operationally usable when `status_code = 'active'` AND `catalog_state_code IN ('certified', 'recertify_pending')`. `recertify_pending` remains usable to preserve runtime continuity; UI surfaces it with a warning.

## 2. The six admission gates

Gates are normative predicates with stable codes. **Hard gates (admission-blocking): G1, G3, G4, G5. Advisory gates (policy signal only): G2.** The audit script and binding-time approval flow both encode these.

| Code | Gate | Severity | Type | Reject condition |
|---|---|---|---|---|
| `G1_LEXICAL` | Lexical hygiene | **hard** | machine | Definition empty, < 20 chars, matches banned-template regex (`from OAGIS undefined`, `TBD`, `TODO`, `FIXME`, `placeholder`, `see source`, `see OAGIS`), matches CCTS datatype-page boilerplate, **matches synthetic-import templates (e.g. `^<field> on <component>( \(OAGIS <noun>\))?$`, `^<field> from OAGIS <noun>$`, or any structurally-derived placeholder that names the field/parent without supplying business meaning)**, or is a restatement of `field_code`. See §2.2. |
| `G2_NAMING` | Naming policy | **advisory** | machine | (1) `naming_policy_violation`: name does not start with `object_class + '_'` nor a registered abbreviation for that object_class (see §2.1). (2) `generic_advisory`: property is bare-generic (`description`, `note`, `comment`, `type_code`, `status_code`, `action_code`, `value`, `text`) AND BF has no anchor (no alias, no SDA, no CC, not BO-required/BK). Reported as signal; does not block admission. |
| `G3_TYPE` | Type semantics | **hard** | machine | `representation_term` or `data_type` missing or not in valid enum; `representation_term` / `data_type` pair is incoherent (e.g. `representation_term=Text` with `data_type=number`) |
| `G4_ANCHOR` | Anchor predicate | **hard** | machine | BF has none of: BO membership with `is_required` or `is_business_key`; alias; SDA evidence; `cc_field_mapping` reference; foundational whitelist entry (§7) |
| `G5_EVIDENCE` | Source / real-world referent | **hard** | machine + whitelist | None of: SDA observation; foundational whitelist entry with named owner; reviewer rationale row referencing a real-world referent. `oagis_structural_only` is reported as an evidence type but does not satisfy G5 by itself. |
| `G6_HUMAN` | Human certification | **hard (final)** | human | Reviewer reviews G1–G5 snapshot + G2 advisories and decides Certify / Demote / Hold |

Future gates not yet enforced (planned, separate decisions): LLM-assisted `G3_DOMAIN_SANITY` (domain placement plausibility), embedding-assisted `G4_DUPLICATE` (semantic overlap). These are surfaced as candidate signals to humans only; they never auto-decide.

Only G6 mints `certified`. Hard-gate failure blocks admission; G2 advisory failure is recorded on the row but does not block admission.

### 2.1. Registered-abbreviation policy

A BF name satisfies the BO-scoped naming rule if it starts with `object_class + '_'` **OR** with a registered abbreviation for that object_class. The abbreviation registry does not yet exist. Until it lands:

- `naming_policy_violation` is **advisory only** — never an admission hard fail.
- Operationally, 2,688 currently-certified BFs use abbreviated prefixes (e.g. `bc_ar_ops_*` under `object_class = bc_ar_operations`). These continue to operate normally.
- When the registry lands (separate ADR), each registered abbreviation entry will pre-satisfy this rule; unregistered abbreviated prefixes will then begin to fail naming policy. Backfill of abbreviations should precede enforcement.

The registry will live as a sibling reference table or YAML — out of scope for this ADR. This section commits only that abbreviated prefixes are *permitted in principle*, not that any specific abbreviation is yet authorised.

### 2.2. Definition admissibility for `certified_catalog`

**Fallback / synthetic / template definitions cannot certify a BF.** A BF row may carry a structural-fallback definition to avoid null/junk text in candidate or import artifacts, but such a definition can never satisfy G1 for `certified_catalog`. The rule is normative and applies retroactively (any historically-certified BF carrying a fallback definition is a candidate for `correction_required` or demotion under future audits).

**Admissible sources of `definition` for `certified_catalog`** (a row must carry one):

1. **Field-level standard prose** — text drawn from a recognised external standard (OAGIS field-level BIE description, ISO/IFRS clause text, US-GAAP definition text, ISO 20022 message-element description) where the standard supplies a contextual sentence, not a CCTS datatype boilerplate page.
2. **Source-system dictionary evidence** — verbatim or curated dictionary text from a real source system (SAP data element description, Oracle field documentation, vendor data dictionary). Implies SDA evidence is present.
3. **Owner-authored definition with rationale** — text authored by a named owner (Cognito sub) with an evidence row in `certification_record.gate_results_json` describing the real-world referent. Rationale ≥ 40 chars.
4. **Curated foundational definition** — applies only to BFs in `contract.business_field_foundational_whitelist`. The whitelist row's `rationale_text` is the foundational definition source.

**Inadmissible sources of `definition` for `certified_catalog`** (G1 hard-fail):

- OAGIS structural membership alone ("X is part of Y" with no field-level prose).
- CCTS datatype-page boilerplate (e.g. "A character string (i.e., a finite set of characters)…").
- Synthetic templates derived from field name + parent ("`<field> on <component>`", "`<field> from OAGIS <noun>`", "`<field> (OAGIS <noun>)`", or any pattern whose body is structurally interpolated rather than contextually authored).
- The literal "from OAGIS undefined" string and its variants.
- Any definition where the text is reconstructable from `field_code` + `object_class` + `representation_term` without supplying meaning that those columns do not already carry.

**Operational implication for importers.** A reader (OAGIS, OAGIS-CCTS, standards-importer, SDA discovery) that *creates* a `contract.business_field` row when the source supplies no field-level prose **must not** also write `status_code='certified'`. Acceptable behaviours:

- Skip the row entirely (preferred when the field has no business use yet).
- Insert with `status_code='draft'` AND default `catalog_state_code='candidate_import'`, with `catalog_state_reason_code='manual_review_required'`.
- Insert with a placeholder definition AND `catalog_state_code='candidate_import'` AND a `gate_signals_json.fallback_definition_source` marker so the next audit can surface and triage it.

Auto-certification of fallback-defined BFs at import time is **prohibited** under this ADR. Importers that currently violate this rule are out of compliance and must be corrected before the next mass import run. The first such known violation is documented under Open items §6.

## 3. Approve-as-you-go binding rules

Certification can occur lazily at the binding boundary rather than via a separate queue, but only for the looser authoring boundaries. Runtime-critical boundaries require pre-certified BFs.

| Boundary | Minimum `catalog_state_code` | Approval mechanism |
|---|---|---|
| `FieldMappingService.suggest()` (source mapping suggestions) | any | None (read-only); UI distinguishes states |
| `CanonicalWizardService` candidate pick | any | None (read-only); UI distinguishes states |
| `cc_field_mapping` insert | `gates_passed` or above | Binding-time gate review + `certification_record` row |
| `business_object_field` insert with `is_required = true` or `is_business_key = true` | `certified` or `recertify_pending` | Pre-certified |
| MC variable / grain binding | `certified` (not `recertify_pending`) | Pre-certified |

Service-side guards enforce this matrix; UI alone is insufficient. **`naming_policy_violation` (G2) is advisory at every boundary** — it never blocks `cc_field_mapping` insert or any other binding. The UI may surface the advisory; the server does not refuse on it.

### Service-guard implication

`FieldMappingService`, `CanonicalWizardService`, the CC onboarding service, and SDA projections must eventually read only admitted/certified BFs by default, or explicitly include non-certified rows behind an `include_uncertified` flag with an operator-visible warning. Today these services read the catalog without state-awareness; that gap is the contamination vector this ADR closes. Server-side guards must land before client-side filtering, or candidate BFs will appear bindable in UI but fail at the server boundary.

## 4. Ledger — reuse `contract.certification_record`

No new ledger table. `certification_record` is already polymorphic (`primitive_type`, `primitive_id`) and carries `gate_results_json jsonb NOT NULL`, `action_code`, `from_state_code`/`to_state_code`, `override_*`, certifier identity, and `supersedes_primitive_id`. For BF admission:

- `primitive_type = 'business_field'`, `primitive_id = field_id`.
- `action_code ∈ { certify, demote, recertify, hold, mark_recertify_pending, hash_invalidated, rule_version_bump }`.
- `gate_results_json` carries the G1–G5 snapshot at decision time, including LLM reasoning for G3/G4 and the `gate_signals_row_hash` of the BF row state at that moment.
- `override_*` covers the "G3 or G4 flagged but operator approved with rationale" case.
- `supersedes_primitive_id` covers duplicate-merge demotions.

## 5. Re-review triggers (no calendar expiry)

Certification does not expire on a calendar. Business meaning, once certified, is stable; thousands of MCs across hundreds of tenants reference the catalog, and periodic mass `recertify_pending` events would create fleet-wide churn without underlying semantic change and incentivise rubber-stamp re-certification. Once a BF is `certified`, it remains so until a defined trigger fires:

- **Row edit.** Any change to a certification-relevant column (definition, datatype, domain, subdomain, semantic_family, unit_type_code) invalidates `gate_signals_row_hash`. Next read detects the mismatch and flips `catalog_state_code` to `recertify_pending`. A `certification_record` row of action `hash_invalidated` records the event.
- **Admission rule version bump.** When the gate predicates change (new G1 regex, new G3 taxonomy, new G5 evidence rule), the audit script re-runs against all certified BFs. Rows that no longer pass flip to `recertify_pending` with action `rule_version_bump` referencing the new rule version.
- **Post-hoc duplicate detection.** When G4 surfaces a duplicate cluster involving an already-certified BF, the pair enters the cluster review queue. State does not flip automatically; a human decides keep/merge/distinct.
- **Cascade from demotion.** When a BF is demoted, BFs sharing its concept are surfaced for review; no automatic state flip.
- **Explicit recheck.** Any operator can request `mark_recertify_pending` with rationale, ledgered.

No periodic expiry job exists. No `review_due_at` column exists. The platform does not manufacture review work in the absence of a triggering event.

## 6. Demotion semantics (Invariant III compliance)

Demotion never deletes the row. It sets `catalog_state_code = 'demoted'`, `demoted_at = now()`, `demotion_reason_code` (structured enum), optionally `demotion_supersedes_field_id` (for duplicate merges), and `archived_at = now()` per D162 rule 8. Every demotion writes a `certification_record` row. This preserves provenance, enables re-promotion if context later supplies evidence, and complies with Invariant III (no historical rewrite).

## 7. Foundational whitelist (G5 + G4 escape hatch)

A small sibling table `contract.business_field_foundational_whitelist` admits BFs that legitimately lack source evidence and/or cross BO boundaries as shared dimensions. Each row carries a named owner and a written rationale. The whitelist is capped by convention; growth past ~50 rows signals the gate is being abused.

**Whitelist semantics.** Membership satisfies the *relevance-anchor* requirement of G4 and the *real-world-referent* requirement of G5. It does **not** confer certification on its own — G1 (clean definition), G3 (coherent type), and G6 (human approval) still apply. A whitelist row is necessary but not sufficient; the BF must still pass the remaining hard gates.

**Initial seed (decided in this ADR, audit-evidenced):**

| Name | BO refs | Alias | Rationale |
|---|---:|---|---|
| `currency_code` | 23 | yes | ISO 4217 currency identifier; appears across financial, sales, procurement BOs. Source-system-agnostic shared dimension. |
| `language_code` | 66 | yes | ISO 639 language identifier; appears across nearly every document-style BO. Highest-breadth shared dimension in the catalog. |
| `country_code` | 2 | no | ISO 3166 country identifier; appears in address-bearing BOs. Foundational geographic dimension. |

Extensions (e.g. `region_code`, `time_zone_code`, `unit_of_measure_code`, `iso_*_code`) may be added on demand via the same whitelist row format; each addition records its named owner and rationale.

## 8. Cleanup priority (audit-grounded)

T4 failures are the highest-severity cohort — these BFs are already steering canonical pipelines. T1-only demotions are lower severity because no downstream artifact references them. The DBCP (separate decision) must execute cleanup in priority order, not in convenience order:

| Priority | Cohort | Size | Rationale |
|---|---|---:|---|
| **P0** | Broken-fallback definitions ∩ CC mapping | **4** | Bad definition AND already active in canonical pipelines — data correctness risk now |
| **P1** | T4 hard failures | **15** | CC-mapped BFs failing G1/G3 — steering pipelines with incoherent semantics |
| **P2** | G3 type-incoherence rows | **19** | Real data bugs; fix inline as **correction** (not demotion) — pair representation_term with data_type per coherence matrix |
| **P3** | Clean demotion cohort (T1_only ∩ G1 fail ∩ G5 structural) | **259** | Bad definition + no anchor + no source evidence — cleanest demotion target |
| **P4** | Broader broken-fallback ∩ no anchor | **370** | Successor to the original 462; broader demotion sweep |

P2 is a **correction** cohort, not a demotion cohort — the rows have legitimate use but wrong type pairing. Correction lands in the same DBCP as P0/P1 because the cohort is small (19) and fixing inline avoids a second migration. P3 and P4 are demotion cohorts proper.

## Schema changes

Additive on `contract.business_field` (column-additive, nullable initially):

- `catalog_state_code text` (enum per §1)
- `gate_signals_json jsonb`
- `gate_signals_at timestamptz`
- `gate_signals_row_hash text`
- `admission_rule_version_at_certify text`
- `certification_record_id uuid` (FK to `contract.certification_record`)
- `reviewed_at timestamptz`
- `demoted_at timestamptz`
- `demotion_reason_code text`
- `demotion_supersedes_field_id uuid` (FK to `contract.business_field.field_id`)
- `archived_at timestamptz`
- `source_origin_code text` (`oagis_import` | `sda_discovery` | `manual` | `seed` | `external_standard`)
- `source_origin_ref text`

New sibling table `contract.business_field_foundational_whitelist` (4 columns: `field_id PK FK`, `owner_sub`, `rationale_text`, `added_at`).

Zero changes to `contract.certification_record`.

## UI surface (bc-admin)

**Modified pages (~10):** `BusinessCatalogPage`, `BusinessFieldDetailPage` (new Admission panel), `BusinessObjectDetailPage`, `MappingsPage`, `MappingBindingsPage`, `FieldResolutionPage`, `CanonicalReaderWizardPage`, `CreateCanonicalContractPage`, `CreateBusinessObjectPage`, `CreateMetric*Page` (3).

**New surfaces:** one page (`/catalog/business-fields/review-queue`), one shared component (`<BFStateChip />`), one inline drawer (binding-time admission gate review).

**Backend touchpoints:** `FieldMappingService` and `CanonicalWizardService` candidate endpoints gain `include_uncertified` flag; `cc_field_mapping` insert and MC variable binding gain server-side guards matching §3.

## Migration sequencing

1. ~~ADR lands as `proposed`.~~ ✓ Done 2026-05-16 (DEC-1ce490).
2. ~~Read-only audit script encodes G1–G5 machine portions. Reports cohorts.~~ ✓ Done 2026-05-16 (baseline + calibrated artifacts).
3. ~~ADR revised based on audit findings; flips to `decided`.~~ ✓ Done in this revision.
4. **Next:** DBCP design (separate decision). Scope: schema additions on `business_field` (§"Schema changes"); new whitelist table seeded per §7; backfill `catalog_state_code` from calibrated audit per-bf.jsonl. **No data mutation specified in this ADR.**
5. **Then:** DBCP execution in cleanup priority order (§8): P0 (4) and P1 (15) and P2 (19 corrections) in tranche 1; P3 (259) and P4 (370) in tranche 2.
6. Service guards land in bc-core (matrix in §3), then bc-admin UI work lands page-by-page; review-queue page last.
7. Phase 3 of TSK-9515d5 is closed; remaining work folds into the new admission pipeline.

**No data mutation occurs under this ADR.** Cleanup is the DBCP's responsibility. The audit script remains read-only and is the evidence basis for the DBCP's tranche definitions.

## Consequences

**Positive.** Catalog joins carry a defensible warrant. Contamination of authoring suggestions is eliminated by state-aware filtering. Certification becomes evidenced state in `certification_record`, not a status flag mutation. Re-audit and re-promotion paths exist by construction.

**Negative.** Certified row count will drop, possibly significantly, once Phase 1/2 is re-audited. The headline number is a regression even though correctness improves; framing this is a communication task. Approve-as-you-go places real-time review burden on operators at the `cc_field_mapping` boundary; the binding-time drawer must be fast and clear or operators will route around it.

**Risks.** Service guards must land before suggestion-endpoint state-aware filtering, or candidate BFs will appear bindable in UI but fail server-side. Phase 1/2 re-audit may find non-trivial failures; this is a feature of the gate, not a bug.

## Open items (for the DBCP and successor decisions)

Closed in this revision:
- ~~G1 banned-template regex set~~ — finalized; encoded in calibrated audit script.
- ~~Foundational whitelist initial population~~ — seeded in §7 with `currency_code`, `language_code`, `country_code`.
- ~~G2 generic_suffix calibration~~ — rule dropped; reframed as bare-generic-AND-no-anchor advisory.

Still open (deferred to DBCP or successor ADRs):
1. Locate the prior decision authorizing OAGIS bulk import; if found, name it in `supersedes` (D370 rule 1).
2. Confirm `gate_signals_row_hash` column set (which BF columns are certification-relevant).
3. Cosine threshold for the future embedding-assisted `G4_DUPLICATE` (separate ADR when LLM/embedding stack is decided).
4. Registered-abbreviation registry shape and ownership (separate ADR).
5. Admission rule versioning scheme (semver, monotonic int, dated tags?) for the version-bump re-review trigger.
6. **OAGIS onboarding service fallback-definition compliance gap.** `bc-core/src/registry/oagis-onboarding.service.ts` currently auto-certifies imported BFs via `bulkCertifyFields(...)` immediately after `bulkCreateFields(...)`. When the source `field.description` is empty, the row enters the catalog with a synthetic fallback definition (legacy: `"<bfName> from OAGIS <comp.name>"`, often resolving to `"… from OAGIS undefined"`; patched-but-uncommitted: `"<bfName> on <compLabel> (OAGIS <nounLabel>)"`). Both forms violate §2.2. The patched form is *cleaner* but still synthetic and remains inadmissible for `certified_catalog`. The auto-certify step must be made conditional on a real definition source, or moved out of the importer path. Tracked as a code-fix slice separate from this ADR. Existing rows with synthetic definitions are addressed by subsequent audit cycles and DBCP-1q-B / future DBCPs, not retroactively in DBCP-1q-A.
7. LLM/embedding stack choice for the future `G3_DOMAIN_SANITY` and `G4_DUPLICATE` gates (separate ADR).
