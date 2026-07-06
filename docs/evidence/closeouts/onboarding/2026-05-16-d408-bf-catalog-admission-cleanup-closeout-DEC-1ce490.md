---
title: "D408 BF catalog admission cleanup — execution closeout"
date: 2026-05-16
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
session: SES-8714df
type: closeout
status: complete
---

# D408 BF catalog admission cleanup — execution closeout

**D408 dev execution complete.** `contract.business_field` now has explicit catalog admission state; weak imported/fallback rows are no longer silently certified catalog members.

## 1. Authority

- **Decision:** DEC-1ce490 / D408 — *contract.business_field is the certified BF-BO catalog* (status: decided).
- **ADR:** [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md).
- **Session:** SES-8714df (this session). The execution was performed end-to-end inside one session over twelve checkpoints.
- **Originating task:** TSK-9515d5 (OAGIS provenance lookup for bulk BF remediation). Phase 3 of TSK-9515d5 surfaced the 462 weakly-defined `certified` rows that became the trigger for the D408 design. TSK-9515d5 Phase 3 is now superseded by this D408 work and should be closed with a reference back to DEC-1ce490 + the artifacts named below.
- **Environment:** dev only. This deployment has no staging or prod environments; the dev pipeline is the production pipeline.

## 2. Problem statement

`contract.business_field` was acting as two tables at once:

1. The **certified BF-BO catalog** — the semantic vocabulary the platform's authoring services (`FieldMappingService`, `CanonicalWizardService`, CC onboarding, SDA projections, MC variable binding) read from and trust as a defensible reference.
2. The **imported-vocabulary inventory** — the holding area for everything pulled in from OAGIS, SDA discovery, external standards, and prior bulk-import work, regardless of whether each row carried real contextual business meaning.

Phase 3 of TSK-9515d5 exposed the failure mode concretely: **462 rows carried `status_code='certified'` AND a templated placeholder definition (`"<property> from OAGIS undefined"`) AND zero anchor evidence** (no required-or-business-key BO membership, no alias, no SDA observation, no `cc_field_mapping` reference). The broader population showed the same shape at scale — out of 7,062 BFs, 6,237 sat in some BO but only 1,962 had aliases, 1,400 had SDA evidence, 316 were referenced by `cc_field_mapping`.

Foundation Invariant VI was being violated: certification was *inferred* from import metadata rather than *emitted* as evidenced state. Downstream services suggested any catalog row to operators during authoring — every junk row was a latent attack surface on every future authoring decision.

## 3. Decisions encoded by this execution

All five are normative in ADR-1ce490 (decided, commit `bc-docs-v3@f2e46fe`).

1. **`contract.business_field` is, by definition, the certified BF-BO catalog.** A row exists in the table only after passing the admission pipeline whose human decision step is recorded in `contract.certification_record`. Coverage is not the goal; defensible semantic warrant is.
2. **OAGIS / SDA / external-standard imports are evidence, not authority.** Imported vocabulary that has not passed the pipeline lives outside the table (filesystem artifacts) until promoted. Importers MUST NOT auto-certify rows they create from imported metadata alone.
3. **Fallback / synthetic / template definitions cannot certify a BF** (ADR §2.2). Admissible definition sources are: field-level standard prose; source-system dictionary evidence; owner-authored with rationale; curated foundational definition. Inadmissible: OAGIS structural membership alone, CCTS datatype boilerplate, structurally-derived templates ("`<field> on <component>`", "`<field> from OAGIS <noun>`"), `from OAGIS undefined`, field-code restatement.
4. **No calendar expiry; no `review_due_at` column.** Re-review is event-triggered only (row edit invalidates `gate_signals_row_hash`; admission-rule version bump; post-hoc duplicate detection; cascade from demotion; explicit operator request). Periodic mass `recertify_pending` events would create fleet-wide churn without underlying semantic change and incentivise rubber-stamp re-certification across thousands of MCs and hundreds of tenants.
5. **Demotion is reversible by ledgered action, never by `DELETE` / `RESTORE`.** Demoted rows remain physically present with `archived_at` set; FK references continue to resolve. Invariant III (no historical rewrite) is preserved by construction.

## 4. Execution timeline

| Step | Artifact | Commit / state |
|---|---|---|
| ADR filed as `proposed` | `bc-docs-v3/docs/adrs/ADR-1ce490.md` | (initial, prior to commit) |
| Baseline audit (read-only) | `bc-core/scripts/audit-bf-admission-d408.mjs` + outputs `2026-05-16T04:00:14Z` | uncommitted then |
| Calibrated audit (read-only) — separates hard gates from advisory | `bc-core/scripts/audit-bf-admission-d408-calibrated.mjs` + outputs `2026-05-16T04:50:46Z` | uncommitted then |
| ADR revised to `decided` after calibrated audit | `ADR-1ce490.md` | `bc-docs-v3@4d8fb89` |
| DBCP design filed | `2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md` | `bc-docs-v3@deeefac` |
| DBCP decisions locked (grandfathering, whitelist owner, tranche split, no `review_due_at`) | DBCP design §10 | `bc-docs-v3@0b8eed8` |
| DBCP-1q-A artifacts authored (schema + CHECK + whitelist + backfill script) | `20260516-d408-dbcp-1q-a-bf-catalog-admission-state.sql` (+`.revert.sql`), `d408-backfill-bf-catalog-state-1q-a.mjs` | `bc-core@513404d` |
| DBCP-1q-A verification plan | `2026-05-16-d408-dbcp-1q-a-verification-plan.md` | `bc-docs-v3@8390ded` |
| DBCP design whitelist shape reconciled with applied SQL | DBCP design §3.4 | `bc-docs-v3@a4081a9` |
| DBCP-1q-A schema applied on dev | (DB write) | DDL via `docker exec` |
| DBCP-1q-A backfill applied on dev | (DB write) | 1,681 rows touched: 1,651 grandfather + 30 corrections |
| Fallback-definition rule clarified across ADR / DBCP / verification plan | `ADR-1ce490.md` §2.2, DBCP §10.6, verification plan §7.1 | `bc-docs-v3@f2e46fe` |
| Importer fallback fix + audit G1 patterns extended | `oagis-onboarding.service.ts`, `audit-bf-admission-d408*.mjs` | `bc-core@186979d` |
| DBCP-1q-B artifacts authored (precondition SQL + demotion script + fresh audit) | `20260516-d408-dbcp-1q-b-bf-catalog-demotions.sql` (+`.revert.sql` docs-only), `d408-demote-bf-catalog-state-1q-b.mjs`, fresh audit `2026-05-16T08:32:46Z` | `bc-core@21bd035` |
| DBCP-1q-B verification plan | `2026-05-16-d408-dbcp-1q-b-verification-plan.md` | `bc-docs-v3@1a7eab6` |
| DBCP-1q-B precondition SQL applied on dev | (read-only DO block) | All preconditions OK |
| DBCP-1q-B demotion applied on dev | (DB write) | 374 rows demoted: 259 P3 + 115 P4 |
| Execution closeout filed | this document | `bc-docs-v3@<this commit>` |

## 5. Final catalog state on dev

| `catalog_state_code` | Count |
|---|---:|
| `candidate_import` | **5,007** |
| `certified_catalog` | **1,651** |
| `correction_required` | **30** |
| `demoted_catalog` | **374** |
| `recertify_pending` | **0** |
| **Total** | **7,062** |

## 6. Ledger state on dev

D408 action codes in `contract.certification_record`:

| `action_code` | Count |
|---|---:|
| `remediate_bf_semantics` (pre-D408 invariant) | **1,392** |
| `admit_bf_catalog` (1q-A grandfather cohort) | **1,651** |
| `mark_bf_correction_required` (1q-A correction cohort) | **30** |
| `demote_bf_catalog` (1q-B demotion cohort) | **374** |
| `recertify_bf_catalog` | 0 |
| `mark_recertify_pending` | 0 |

Plus pre-existing historical actions on `business_field` and other primitive types (unchanged by D408).

## 7. Correction-required cohort breakdown (30 rows)

From DBCP-1q-A backfill; all in `catalog_state_code='correction_required'` awaiting human fix.

| Cohort | Reason | Count | Notes |
|---|---|---:|---|
| **P0** | `broken_fallback_definition` | **4** | Banned-template definition AND active in `cc_field_mapping`. Highest severity. Sample names: `credit_type_code` (11 cc), `freight_invoice_hdr_net_volume_measure`, `invoice_hdr_net_volume_measure`, `price_list_line_type_code`. |
| **P1 G1-short** | `definition_too_short` | **7** | 5× IFRS rows + 2× XBRL with 16-19 char definitions. Fixable inline by replacing the definition. |
| **P1 G3 + P2** | `type_incoherence` | **19** | `representation_term` / `data_type` pair mismatched (e.g. `representation_term=Text` with `data_type=number`). Names include `asset_net_book_value_amount` (39 cc), `commercial_invoice_line_*_amount`, `warranty_claim_*_amount`. |
| **Total** | – | **30** | – |

Math: P0(4) + P1(11) + P2(15) = 30; P1 split internally into 4 G3 fails + 7 G1-short fails matching gate detail.

## 8. Demoted cohort breakdown (374 rows)

From DBCP-1q-B; all in `catalog_state_code='demoted_catalog'` with `archived_at` set.

| Cohort | Definition | Count |
|---|---|---:|
| **P3** | `T1_only ∩ G1 fail ∩ G5 oagis_structural_only ∩ no_anchor` | **259** (255 banned-template + 4 definition_too_short) |
| **P4** | banned-template ∩ no_anchor, excluding P3 overlap | **115** |
| **Total** | – | **374** |

**Anchor predicate confirmed on entire demoted cohort:**

- `cc_field_mapping` references: **0 / 374** ✓
- `business_field_alias` rows: **0 / 374** ✓
- `business_object_field` with `is_required` OR `is_business_key`: **0 / 374** ✓
- `certification_record` with `action_code IN ('certify','remediate_bf_semantics')`: **0 / 374** ✓

Perfect orphan cohort — exactly the no-anchor predicate. Demotion does not break any downstream reference.

## 9. Invariants preserved

| Invariant | Pre-execution | Final state | Verdict |
|---|---:|---:|:-:|
| `contract.certification_record action_code='remediate_bf_semantics'` count | 1,392 | 1,392 | ✓ held |
| `contract.business_field` row count | 7,062 | 7,062 | ✓ no deletes |
| `contract.canonical_field` row count | 3,097 | 3,097 | ✓ no CF change |
| `contract.metric_contract` row count | 780 | 780 | ✓ no MC change |
| Tenant DBs touched | – | none | ✓ |
| Service code changed | – | one targeted file (`oagis-onboarding.service.ts`) | (importer fix only; no service-guard slices) |
| bc-admin UI changed | – | none | ✓ (UI work tracked as GS-5) |
| Deletions anywhere | – | none | ✓ |

Foundation invariants checked (per ADR-1ce490 §Foundation gate):

- **I (meaning evaluated once):** admission boundary now exists; meaning is no longer redundantly asserted by import + by `status_code='certified'`.
- **III (state immutable; no historical rewrite):** demotion preserves rows via `archived_at` + ledger row; no rewrites.
- **VI (evidence emitted, not inferred):** every state transition writes a `certification_record` row with `gate_results_json`; certification is no longer inferred from import metadata.

## 10. Known remaining work

D408 dev execution is complete, but the wider package is not finished. The following items remain and should be tracked as separate decisions / slices:

### Service-guard slices (GS-1 … GS-5) — gated next step

Without service guards, the new `catalog_state_code` is decorative — `FieldMappingService` and `CanonicalWizardService` continue to suggest from the full catalog, and `cc_field_mapping` insert still accepts any BF. These slices realise the value of D408 at the consumer boundaries:

| Slice | Service | Change |
|---|---|---|
| GS-1 | `FieldMappingService.suggest()` | Default to `catalog_state_code='certified_catalog'`; `include_uncertified=true` opt-in with UI warning. |
| GS-2 | `CanonicalWizardService` candidate endpoint | Same default + opt-in. |
| GS-3 | `cc_field_mapping` insert | Refuse non-`certified_catalog` / `recertify_pending` BFs unless explicit operator override (paired `certification_record` row). |
| GS-4 | SDA projections | State-aware: legacy `status_code` for backwards compat + `catalog_state_code` for UI surfacing. |
| GS-5 | bc-admin UI | `<BFStateChip />`, review-queue page (`/catalog/business-fields/review-queue`), binding-time admission drawer. |

### Successor ADRs (none gate execution)

| Topic | Why it matters |
|---|---|
| Registered-abbreviation registry (ADR §2.1) | Until filed, `naming_policy_violation` advisories cannot enforce; 2,688 abbreviated-prefix BFs continue without policy. |
| G3 domain-sanity LLM stack (ADR §2 future gate) | Adds LLM-assisted plausibility check on `(domain, subdomain)` placement. |
| G4 duplicate-embedding stack (ADR §2 future gate) | Adds embedding-based semantic-overlap detection. |
| Admission rule versioning scheme (ADR §5) | Concretises the `admission_rule_version_at_certify` column's value scheme (currently literal `'v1'`). |
| OAGIS onboarding refactor (D408 follow-up) | The `onboardNoun()` function carries scoped `eslint-disable max-lines-per-function, max-depth` per `bc-core@186979d`. Extract scalar/complex handlers when scope permits. |

### Data work

| Task | Notes |
|---|---|
| Handle the 30 `correction_required` rows | P0 + P1 + P2 cohort needs human-authored definitions and type-pair corrections. Each fix lands as a `recertify_bf_catalog` ledger action moving the row back to `certified_catalog`. |
| Decide future of the 5,007 `candidate_import` rows | Largest residual cohort. Likely splits into: rows worth investing in (real domain BFs that lack only anchor evidence — promote via SDA + G6) and rows that should be demoted in a future tranche (T0_only without business use). Requires a triage policy. |

### Session housekeeping

| Item | Notes |
|---|---|
| Close TSK-9515d5 Phase 3 | Reference DEC-1ce490 + the artifacts listed in §4. Phase 3's original deeper-scrape remediation path is superseded by the D408 admission pipeline. |
| Close SES-03f268 | Orphaned session from the Phase 3 work. Cross-reference DEC-1ce490 + this closeout; SES-03f268 itself remains untouched by D408 execution. |

## 11. Final statement

D408 dev execution complete. `contract.business_field` now has explicit catalog admission state; weak imported / fallback rows are no longer silently certified catalog members. Every catalog state transition since the schema landed is evidenced by a paired `certification_record` row with `gate_results_json` snapshot. The catalog is no longer doing two jobs.

**Service guards (GS-1 … GS-5) should land before any next mass BF onboarding or remediation run.** Until they do, the new `catalog_state_code` is honoured by the data model but not by the read-side services; an operator suggestion-list query will still surface demoted or candidate rows alongside certified ones. The data model is correct; the consumer boundary is the next slice.

---

## Appendix A — Commit ledger

| Repo | Commit | Subject |
|---|---|---|
| bc-docs-v3 | `4d8fb89` | docs(d408): decide BF catalog admission predicate from calibrated audit |
| bc-docs-v3 | `deeefac` | docs(d408): DBCP plan for BF catalog admission cleanup |
| bc-docs-v3 | `0b8eed8` | docs(d408): lock BF catalog cleanup DBCP decisions |
| bc-core | `513404d` | db(d408): author DBCP-1q-A BF catalog admission schema |
| bc-docs-v3 | `8390ded` | docs(d408): verification plan for DBCP-1q-A BF catalog admission state |
| bc-docs-v3 | `a4081a9` | docs(d408): align DBCP whitelist shape with 1q-A SQL |
| bc-docs-v3 | `f2e46fe` | docs(d408): clarify fallback definitions cannot admit BFs |
| bc-core | `186979d` | fix(d408): block OAGIS fallback BFs from certified import |
| bc-core | `21bd035` | db(d408): author DBCP-1q-B BF catalog demotion artifacts |
| bc-docs-v3 | `1a7eab6` | docs(d408): verification plan for DBCP-1q-B demotions |
| bc-docs-v3 | (this) | docs(d408): close out BF catalog admission cleanup execution |

## Appendix B — References

- ADR: [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md)
- DBCP design: [2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md](../../dbcp/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md)
- DBCP-1q-A verification plan: [2026-05-16-d408-dbcp-1q-a-verification-plan.md](../../dbcp/onboarding/2026-05-16-d408-dbcp-1q-a-verification-plan.md)
- DBCP-1q-B verification plan: [2026-05-16-d408-dbcp-1q-b-verification-plan.md](../../dbcp/onboarding/2026-05-16-d408-dbcp-1q-b-verification-plan.md)
- Calibrated audit artifacts (committed at `bc-core@21bd035`): `bc-core/scripts/audit-output/d408-bf-admission-audit-calibrated-2026-05-16T08-32-46-736Z.{md,json,per-bf.jsonl}`.
- D162 (database rules): `bc-docs-v3/docs/adrs/ADR-1918d0.md`
- D268 (session discipline): `bc-docs-v3/docs/adrs/ADR-ebf0b4.md`
- Foundation invariants: `bc-docs-v3/docs/foundation/the-invariants.md`
