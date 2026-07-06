---
title: "D408 service-guard design plan (GS-1 … GS-5)"
date: 2026-05-16
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
closeout: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md
session: SES-8714df
type: service-guard-design
status: proposed
---

# D408 service-guard design plan (GS-1 … GS-5)

**This is a design plan only. No code is authored or modified by this commit. No DB writes. No tenant DB touched. Implementation sequencing is proposed; each slice requires its own commit and operator authorisation.**

## 1. Authority and scope

- **ADR:** [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md) — *contract.business_field is the certified BF-BO catalog* (decided).
- **Closeout:** [2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md](../../closeouts/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md) (D408 dev pipeline complete: schema + 1q-A backfill + importer fix + 1q-B demotion).
- **Scope of this plan:** the five consumer-side guard slices named in ADR §UI surface and the closeout §10:
  - GS-1 `FieldMappingService.suggest()` default certified-only.
  - GS-2 `CanonicalWizardService` candidate read default certified-only.
  - GS-3 `cc_field_mapping` insert refusal of non-certified BFs.
  - GS-4 SDA projections + integrity reads state-aware.
  - GS-5 bc-admin UI: `<BFStateChip />`, review-queue page, binding-time admission drawer.
- **Not in scope:** MC variable / grain binding refusal — already required `certified` per ADR §3 and is a separate, stricter slice ("GS-6 MC bind refusal") flagged at the end of §11 for the next planning round; it is not GS-1..GS-5.

## 2. Current risk

D408's data model is in place on dev. `catalog_state_code` distinguishes the 1,651 `certified_catalog` rows from the 374 `demoted_catalog` rows from the 30 `correction_required` rows from the 5,007 `candidate_import` rows. **None of the consumer services read this column today.** Every authoring suggestion, every wizard pick list, every BF list view continues to surface all 7,062 rows by name with no state distinction.

Concrete operational consequences as of 2026-05-16:

- `FieldMappingService.suggest()` will offer a demoted BF as a candidate mapping target for a source field. An operator clicking through without checking state will create a `cc_field_mapping` row that points to a row the catalog has already disclaimed.
- `CanonicalWizardService.writeCanonicalVersion()` materialises canonical contract schemas from `business_object_field` joins — a demoted BF in a BO appears in the resolved schema unchanged.
- `cc_field_mapping` insert paths (`cc-onboarding.service.ts:506`, replace-mapping flow at line 668-680) accept any `business_field_id`. There is no server-side check that the BF is in `certified_catalog`.
- `integrity.service.ts` (lines 999-1003, 1155-1158) joins `business_field` for chain-completeness diagnostics — demoted rows still appear in chain-status output, misleading operators about catalog health.
- bc-admin's `GET /api/standard-fields` list (consumed by `bc-admin/src/api/standard-fields.ts`) returns all rows; the catalog browser shows demoted/candidate rows alongside certified ones with no visual distinction.

**Until these guards land, `catalog_state_code` is decorative at the read boundary.** D408's data correctness is not yet enforced where it matters most: at the moment an operator picks a BF.

## 3. Consumer inventory (grounded in bc-core)

The following services and read sites must be updated by GS-1..GS-5. File paths are bc-core unless noted.

| # | File / path | Read shape | Guard slice |
|---|---|---|---|
| 1 | `src/registry/field-mapping.service.ts:162-175` `loadBoFields()` | `JOIN business_object_field bof JOIN business_field bf …` — returns all BFs in a BO for source-mapping suggestions | **GS-1** |
| 2 | `src/registry/field-mapping.service.ts:220-230` alias lookup | Reads `business_field_alias` to layer alias-based mapping hints | GS-1 (related; same caller) |
| 3 | `src/registry/canonical-wizard.service.ts:280-300` `writeCanonicalVersion()` | Same BO-field join, materialises canonical schema | **GS-2** |
| 4 | `src/registry/canonical-wizard.service.ts:440-450` (second occurrence) | Same join; preview path | GS-2 |
| 5 | `src/registry/cc-onboarding.service.ts:506` | `INSERT INTO contract.cc_field_mapping (..., business_field_id, ...)` (bulk create) | **GS-3** |
| 6 | `src/registry/cc-onboarding.service.ts:668-724` `replaceMapping()` | Single-row replace of cc_field_mapping | GS-3 (same write boundary) |
| 7 | `src/registry/integrity.service.ts:999-1003` and `:1155-1158` | Chain status / BO-coverage diagnostics joining `business_field` | **GS-4** |
| 8 | `src/registry/seed-context-readiness.service.ts` (BF readiness joins) | Diagnostic readout | GS-4 |
| 9 | `src/registry/semantic-definitions/gate-evaluation.{service,reader}.ts` | Reads BF rows in admission-related diagnostics | GS-4 |
| 10 | `src/boundary/canonical-resolution.service.ts` | Runtime resolution of CC fields to BF metadata — *read at evaluation, not at authoring* | GS-4 (read-only diagnostic / evaluation-time) |
| 11 | `src/registry/standard-field.controller.ts` + `standard-field.repository.ts` | `GET /api/standard-fields` list/detail | **GS-5 backend** |
| 12 | `src/registry/standard-field.repository.ts:190-206` `remediateSemantics()` UPDATE | Touches the BF row directly with `WHERE statusCode='certified'` filter — should also consider `catalog_state_code` | GS-5 follow-on (touches remediation path) |
| 13 | bc-admin `src/api/standard-fields.ts` + `BusinessCatalogPage` + `BusinessFieldDetailPage` + the 9 other modified pages from ADR §UI surface | Lists / detail / pick-lists across the UI | **GS-5** |
| 14 | bc-admin `src/api/reader-wizard.ts` | Reader wizard surface that consumes BF metadata | GS-5 |

**Out of scope here (separate slices):**

- `src/registry/mc-onboarding.service.ts` MC variable / grain binding — already requires `certified` per ADR §3; refusal logic is a separate "GS-6 MC bind refusal" slice.
- Repositories for `canonical_field`, `metric_contract` — not directly affected by D408.
- Tenant projection tables (`progression.*`, `fact.*`) — out of scope by D408 §"Out of scope".

## 4. Guard matrix

| Slice | Service | Read default | Override flag | Refusal behaviour | Caller surfaces |
|---|---|---|---|---|---|
| **GS-1** | `FieldMappingService.suggest()` | filter to `catalog_state_code='certified_catalog'` on `loadBoFields()` | `?include_uncertified=true` query param on the controller; platform-admin only | none — suggestions are read-only; non-certified rows simply hidden | `bc-admin` field-resolution page; reader-wizard mapping step |
| **GS-2** | `CanonicalWizardService` candidate read | same filter on `writeCanonicalVersion()` BO-field join + preview path | same flag, same scope | refuse to write a canonical contract version when *any* required BO field is non-certified — surface the list of disqualifying BFs | `bc-admin` canonical-reader wizard |
| **GS-3** | `cc_field_mapping` insert (`cc-onboarding.service.ts` bulk and `replaceMapping`) | n/a (this is a write path) | bind-time approval via paired `certification_record` row (per ADR §3 approve-as-you-go) | **422** `non_certified_bf` if the BF is in `demoted_catalog`, `correction_required`, or `recertify_pending`; **409** `catalog_state_conflict` if the BF moved out of the readable state between the suggest read and the insert; **403** if non-platform attempts override | `bc-admin` CC onboarding; cc-onboarding controller |
| **GS-4** | SDA projections + `integrity.service.ts` chain joins + seed-context-readiness diagnostics | filter joins to `catalog_state_code IN ('certified_catalog','recertify_pending')` for "trusted" projections; expose full join behind a diagnostic flag for catalog-health views | flag on each diagnostic endpoint; default trusted | none — diagnostic, read-only; non-trusted rows visible only on the catalog-health endpoints | `bc-admin` integrity / chain-status / readiness pages |
| **GS-5** | bc-admin UI (BFStateChip + ListView + DetailView + PickList components) | catalog list defaults to certified-or-recertify-pending; pick lists default to certified-only | "Show all states" toggle in UI list view; "Include uncertified" advanced affordance in pick lists with explicit warning | UI surfaces the refusal payloads from GS-1..GS-4 server responses; the new review-queue page (`/catalog/business-fields/review-queue`) is the dedicated surface for `gates_passed` / `recertify_pending` triage | catalog browser, BF detail, BO detail, mapping pages, canonical-wizard, CC onboarding, metric wizard, reader wizard |

## 5. Default read rule

**Every read of `contract.business_field` (or any join through it) that produces a list, suggestion, pick-list option, or runtime resolution that an operator or downstream consumer treats as canonical material defaults to a filter:**

```sql
catalog_state_code IN ('certified_catalog')
-- OR for recertify-tolerant reads (per ADR §3, mostly non-runtime):
catalog_state_code IN ('certified_catalog', 'recertify_pending')
```

Two read tiers, distinguished by purpose:

- **Authoring reads (GS-1, GS-2, GS-3, GS-5 pick-lists):** `certified_catalog` only. `recertify_pending` is intentionally excluded — a row whose certification has been invalidated by an event should not be bindable to a new artifact until reviewed. (ADR §3 makes an explicit exception for non-runtime boundaries; this design tightens GS-1..GS-3 to `certified_catalog` only because authoring of *new* bindings is closer to a runtime act than to a passive list view.)
- **Diagnostic reads (GS-4, GS-5 catalog browser default):** `certified_catalog` or `recertify_pending`. These surface known catalog members without misrepresenting them as durably certified.

**Reads that are evaluation-time (boundary services that resolve a CC field to its BF metadata at metric evaluation):** read whatever state the binding pointed to at evaluation, **plus** record the `catalog_state_code` at evaluation in the snapshot. They do not re-filter — that would change semantics mid-evaluation. They surface the state through evidence (Invariant VI).

## 6. Operator override rule

`include_uncertified=true` is the single canonical override flag. The rules:

1. **Platform-admin only.** Tenant or non-platform callers receive **403**. Authorisation is checked at the controller via the existing JWT role guard (`@PlatformOnly()` decorator); the controller propagates the flag to the service only after auth passes.
2. **Read-only effect.** The flag widens a read result. It NEVER bypasses a write refusal (GS-3). An operator who needs to bind a non-certified BF goes through the approve-as-you-go ledger path (ADR §3, paired `certification_record` row), not through an override of the read.
3. **Warning-labeled.** Every response that was widened by `include_uncertified=true` carries a `_d408_widened: true` field plus the count of non-certified rows surfaced. The UI badges these rows distinctly.
4. **Audit-logged.** The controller writes an `audit_log` entry (existing infrastructure) recording the override use, the certifier identity, and the count of widened rows. No PII; just operational evidence.
5. **Default off everywhere.** New endpoints inherit the default. There is no opt-out flag from the default; the only switch is `include_uncertified=true`.

## 7. Write / refusal rule

`cc_field_mapping` insert and any future write that takes a `business_field_id` foreign key must enforce, **at the service layer** (not only at the DB CHECK level — there is no such CHECK today, and adding one is a separate decision):

- The target BF's `catalog_state_code` must be `certified_catalog`.
- If `recertify_pending`: refuse with **422** and instruct operator to recertify first.
- If `correction_required`: refuse with **422** and surface the `catalog_state_reason_code`.
- If `demoted_catalog`: refuse with **422** and the demote ledger reference.
- If `candidate_import`: refuse with **422** unless the same request carries an `admit_in_place=true` payload that the controller maps to a paired `admit_bf_catalog` ledger row (approve-as-you-go per ADR §3); the service writes the admission ledger first, then the cc_field_mapping insert, both inside one transaction.

Refusals are **detail responses** (RFC 7807) with structured `type`, `title`, `status`, `detail`, `instance`, and a custom extension carrying the offending `field_id` + `catalog_state_code` + `catalog_state_reason_code` + `certification_record_id` of the most recent ledger row. The UI uses the extension to render a human-readable explanation and a one-click action ("Approve in place" / "View ledger" / "Pick different BF").

## 8. Error taxonomy

| HTTP | `type` (problem URI suffix) | When | Required extension fields |
|---|---|---|---|
| **422** | `non_certified_bf` | Write attempt against a BF in any state other than `certified_catalog`, without a valid in-place admission payload | `field_id`, `catalog_state_code`, `catalog_state_reason_code`, `certification_record_id` |
| **409** | `catalog_state_conflict` | Optimistic-concurrency: BF's `catalog_state_code` changed between the read that built the request and the write attempt (detected via `gate_signals_row_hash` mismatch or simple `catalog_state_code` re-check inside the write transaction) | `field_id`, `expected_state`, `actual_state`, `since_ts` |
| **403** | `include_uncertified_forbidden` | Non-platform caller sent `include_uncertified=true` | `caller_role`, `required_role='platform_admin'` |
| **422** | `mc_bind_requires_certified` | (Reserved for the GS-6 MC bind slice, not GS-1..GS-5) | `mc_id`, `field_id`, `catalog_state_code` |

The `type` URIs follow the convention `https://barecount.io/problems/<type>` per platform standard. The body type is `application/problem+json` per RFC 7807. Existing problem-detail middleware in bc-core renders these uniformly; this design adds new `type` strings, not new middleware.

## 9. Tests per guard

### GS-1 FieldMappingService.suggest()

- **Unit (Vitest):** `loadBoFields()` returns only `certified_catalog` rows when called without override; returns all rows when called with `includeUncertified=true`. Use an in-memory fixture or test DB seed.
- **Integration:** controller responds 200 with filtered list; 200 with widened list when `include_uncertified=true` and JWT is `platform_admin`; 403 when JWT is tenant role with the flag.
- **Snapshot:** suggestion shape unchanged when no demoted/candidate rows exist in the BO (regression guard).

### GS-2 CanonicalWizardService

- **Unit:** `writeCanonicalVersion()` throws a structured error listing all non-certified BFs when the target BO contains any non-certified `business_object_field`.
- **Integration:** wizard preview surfaces the disqualifying BFs by name + state; wizard write refuses with 422 problem-detail body.
- **Edge:** BO with mixed states — error message must list each disqualifying row.

### GS-3 cc_field_mapping insert refusal

- **Unit (`cc-onboarding.service.spec.ts`):** bulk-create refuses if any DTO references a non-certified BF; replace-mapping refuses likewise.
- **Integration:** controller returns 422 `non_certified_bf` with required extension fields populated.
- **Concurrency:** insert succeeds when BF is certified at the time of the call; insert returns 409 `catalog_state_conflict` if a parallel transaction demotes the BF between read and write (simulated with a transaction-level pause).
- **Approve-in-place:** when `admit_in_place=true` payload is present, both the admission ledger row and the cc_field_mapping row are inserted atomically (single transaction, both visible together or neither).

### GS-4 SDA + integrity diagnostics

- **Unit:** `integrity.service.ts` chain-status defaults to trusted state filter; catalog-health endpoint surfaces full breakdown.
- **Integration:** existing chain-status report regression — `chain_status` totals shift to match certified+recertify_pending only by default; legacy callers using the chain-status pages see no breakage because the totals already reflected business reality.

### GS-5 bc-admin UI

- **Component tests (Vitest + Testing Library):** `<BFStateChip />` renders correctly for each of the 5 `catalog_state_code` values; pick-list filters surface "show all states" toggle and respects it.
- **E2E (Playwright):** catalog browser default view hides demoted rows; toggle reveals them with chip; pick-list in CC onboarding shows certified-only by default.

## 10. Implementation sequence (proposed)

Two reasonable orderings; the second is preferred.

### Option A — "value-first" (suggestion endpoints first)

1. GS-1 FieldMappingService
2. GS-2 CanonicalWizardService
3. GS-5 bc-admin UI partial (chips + list view)
4. GS-3 cc_field_mapping refusal
5. GS-4 SDA / integrity diagnostics
6. GS-5 bc-admin UI remainder (review queue + admission drawer)

Lower per-slice risk; defers the "stop the bleeding" refusal until late.

### Option B — "stop-the-bleeding first" (refusal first) *(recommended)*

1. **GS-3** `cc_field_mapping` insert refusal — refuses non-certified BFs at the write boundary. **Highest-value, blocking risk arrested immediately.** Existing operators may have to use the approve-in-place flow; this is the intended D408 user experience.
2. **GS-5 partial** `<BFStateChip />` shared component + BusinessCatalogPage + BusinessFieldDetailPage chip rendering. Operators get visual context immediately.
3. **GS-1** FieldMappingService default certified-only. Suggestions stop offering demoted/candidate rows.
4. **GS-2** CanonicalWizardService default certified-only + write refusal on any non-certified BF in BO.
5. **GS-4** SDA / integrity diagnostics state-aware.
6. **GS-5 remainder** `/catalog/business-fields/review-queue` page + binding-time admission drawer.

Order B fixes the durable correctness issue (new bad cc_field_mapping rows) at slice 1, then layers the visible affordances behind it. Each slice is independently shippable and reversible.

**Recommended first implementation slice: GS-3.** It is the smallest correctness fix with the highest upside — it permanently closes the write boundary against rows the catalog has disclaimed. The subsequent slices are additive UX work.

## 11. Hard boundaries

- No DB writes from this design markdown.
- No code in this turn.
- No tenant DB touched.
- No metric promotion.
- No service-code modifications. The diff in this commit is a single markdown file.
- No bc-admin code changes. UI design notes are forward-looking, not implemented here.
- No changes to `mc-onboarding.service.ts` — MC variable / grain bind refusal is reserved for a separate GS-6 slice (not in this plan; flagged at end of §3).

## 12. References

- ADR: [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md)
- DBCP design: [2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md](../../dbcp/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md)
- Closeout: [2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md](../../closeouts/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md)
- D162 (database rules): `bc-docs-v3/docs/adrs/ADR-1918d0.md`
- bc-core service files referenced above by line number.
