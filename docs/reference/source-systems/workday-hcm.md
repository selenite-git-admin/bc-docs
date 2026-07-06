---
uid: SRC-w4d002
slug: workday-hcm
title: "Workday HCM"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: draft
domain: hcm
subdomain: workday
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://community.workday.com/api-reference
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/workday-hcm.md
---

# Workday HCM

This page records BareCount's source-admission posture for Workday HCM. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Same proof status as Workday Financials: architecture documented from public references; no reader executor; no Workday auth helper; no customer engagement.

This page is `status: draft` — needs cold-read by someone with first-hand Workday HCM integration experience.

---

## 2. Reader Flavor Binding

Empty list. Same candidate flavors as Workday Financials (shared executor, model-scoped configuration).

---

## 3. What BareCount Admits

### 3.1 Metadata

Organizations (Supervisory Organisations, Cost Centres, Companies, Locations); job profiles, job families, pay grades; positions; compensation packages and pay components; benefit plans; absence types; learning catalogue.

### 3.2 Business data

| Domain | Workday objects |
|---|---|
| Worker master | Worker, Personal Data, Contact Information |
| Employment | Hire, Job Change, Termination, Worker History |
| Compensation | Compensation, Allowance Plan, One-Time Payment |
| Time | Time Entry, Time Off |
| Performance | Performance Review, Goals |
| Absence | Absence Cases, Balances |
| Learning | Course Enrolments, Completions |
| Recruiting | Job Requisitions, Candidates, Job Applications |

PII-heavy throughout — see §4.

---

## 4. Legal & Licensing

Vendor licensing, access-tier, rate-limit, pricing, and contractual terms are not maintained as static facts in v4.

During source onboarding, verify:

- customer entitlement for the selected API or interface
- whether a dedicated service identity requires a paid license
- whether read-only extraction is permitted under the customer contract
- rate-limit, concurrency, and data-egress constraints that affect reader scheduling

Record the verified terms in the onboarding evidence for that tenant and source. This page may name the admission stance, but it must not be treated as vendor-license advice.

---

## 5. Commercial

No static commercial estimate is maintained here.

Capture customer-specific subscription, add-on, service-account, API, connector, egress, partnership, or infrastructure costs during onboarding evidence review.

---

## 6. Technical

Identical to Workday Financials (see [workday-financials.md §6](workday-financials.md)) — same REST + SOAP + RaaS surfaces, same auth, same endpoint patterns. The only difference is which Get/Search operations and which RaaS reports the ISU is permitted to call.

For HCM-specific RaaS reports, common shapes:
- Worker profile report (one row per worker, columns from configured worker fields).
- Headcount-by-cost-centre report (organisation hierarchy + worker counts).
- Compensation history (effective-dated compensation rows per worker).

### Effective-dating

Workday is **fundamentally effective-dated**. Most worker objects have effective-from/effective-to dates. Default queries return the snapshot at "in the readiness baseline"; historical queries require effective-date parameters. The reader and canonical resolution must respect this — a worker observation is bound to an effective date, not just a `last_modified` timestamp.

---

## 7. Customer-Side Onboarding

1. Workday administrator creates the ISU (or extends the one used for Financials).
2. Assigns HCM-specific domain security policies (Worker Data, Job Information, Compensation, etc.).
3. Builds RaaS custom reports for HCM data shapes BareCount needs.
4. Customer signs PII data-flow agreement with BareCount.
5. Hand BareCount: shared tenant credentials + the HCM-specific RaaS report URLs.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'workday_hcm'`
- `tenant_host`, `tenant_name`
- `auth.credential_ref` — may share with `workday_financials` profile if same tenant + ISU
- `raas_reports[]` — HCM-specific reports
- `pii_policy_ref` — reference to the signed data-flow agreement

Smoke test: `GET /ccx/api/v1/common/v1/workers?limit=1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

Same as Workday Financials plus:

1. **Effective-dating model** in canonical resolution — Workday HCM is effective-dated end-to-end; observations must carry the effective-date dimension.
2. **PII data-flow agreement template** — must be Workday-aware (Worker entity is PII by default).
3. **First-hand verification** — no real Workday HCM tenant observed.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Companion source page | [Workday Financials](workday-financials.md) |
| Workday Community API reference | https://community.workday.com/api-reference |
| Reports-as-a-Service | https://community.workday.com/sites/default/files/file-hosting/restapi/index.html |
| Predecessor — legacy v2 archive Workday HCM reference | legacy-v2/reference/sources/workday-hcm.md (stub) |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
