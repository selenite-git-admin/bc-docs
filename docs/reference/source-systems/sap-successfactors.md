---
uid: SRC-d2a7c3
slug: sap-successfactors
title: "SAP SuccessFactors"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: hcm
subdomain: sap
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://help.sap.com/doc/2d1d6fcc4eae4db8b9bbd3103baee1c7/2511/en-US/HXMSuiteODataAPIRefGuideV4.pdf
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-d2cdb9   # D384 — SAP API admission stance
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/sap-successfactors.md
---

# SAP SuccessFactors

This page records BareCount's source-admission posture for SAP SuccessFactors. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

What this means concretely:

- Architecture and onboarding documented.
- No reader executor for SuccessFactors OData V4 specifically; the existing `SapOdataV4Executor` could in principle target SuccessFactors but the auth path (OAuth 2.0 SAML Bearer Assertion) is not yet wired into `CredentialResolverService`.
- No customer engagement, no PII data flow agreements drafted.

Until at least the auth path is shape-tested against a SuccessFactors sandbox or trial tenant, **no SuccessFactors capability claim is permitted externally.**

---

## 2. Reader Flavor Binding

Empty list. Candidate flavor when scoped:

- `sap-successfactors-odata-v4` — uses `SapOdataV4Executor` once the OAuth 2.0 SAML Bearer auth method is added to `CredentialResolverService`.

---

## 3. What BareCount Admits

### 3.1 Metadata

Company structure (legal entities `FOCompany`, business units, divisions, departments, cost centres, hierarchical relationships); job classifications (`FOJobCode`, job functions, families); pay component definitions; position hierarchies; location master; picklist definitions; country-specific configuration (`PerGlobalInfo*`).

### 3.2 Business data

| Domain | Entities | Notes |
|---|---|---|
| Employee master | `PerPerson`, `PerPersonal`, `PerEmail`, `PerPhone` | Effective-dated personal information. PII-heavy. |
| Employment | `EmpEmployment` | Lifecycle data, hire/rehire dates, contingent-worker flags. |
| Job information | `EmpJob` | Effective-dated department, business unit, cost centre, manager, job code, pay grade. |
| Compensation | `EmpCompensation`, `EmpPayCompRecurring`, `EmpPayCompNonRecurring` | Effective-dated salary and pay components. |
| Time | `EmployeeTime` | Time-off, timesheets, accruals, overtime. |
| Payroll | EC Payroll posting | Gross/net, deductions, employer contributions. |
| Performance | Performance form data | Ratings, competency assessments. |
| Recruiting | Job requisitions, candidate apps | Offer details. |
| Learning | Course completions, certifications | Compliance training status. |

Most employment entities are effective-dated. By default OData returns only the current active record; historical reads require `fromDate=1900-01-01&toDate=9999-12-31`.

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

### 6.1 Protocol

Two API surfaces in parallel:

| API | Status | Recommendation |
|---|---|---|
| OData V4 | Active migration target | **Use for new integrations** |
| OData V2 | Functional, ATOM/JSON | Acceptable for entities not yet migrated |
| SFAPI (legacy SOAP) | Maintenance mode | Avoid; only relevant if Compound Employee API is needed |

### 6.2 Endpoint pattern

- V4: `https://<api-server>/odata/v4/<EntitySet>`
- V2: `https://<api-server>/odata/v2/<EntitySet>`

The `<api-server>` is region-specific (e.g. `api.successfactors.eu`, `api.successfactors.com`). Customer provides the exact host.

### 6.3 Authentication

**OAuth 2.0 SAML Bearer Assertion (recommended):**

1. Customer registers an OAuth 2.0 Client Application in SuccessFactors Admin Centre.
2. BareCount generates a signed SAML assertion using a private key.
3. POST the assertion to `https://<api-server>/oauth/token` to receive a Bearer JWT.
4. Use the Bearer in `Authorization: Bearer <token>` for subsequent OData calls.
5. Tokens are short-lived (typically 30–60 min); refresh on demand.

**OIDC (emerging):** standard token-based with discovery endpoints — relevant for BTP integration scenarios.

### 6.4 Pagination and deltas

- Server-side pagination via `$skiptoken` (V4) / `$skip` + `$top` (V2).
- Effective-dated reads use `fromDate` / `toDate`.
- Delta detection via `lastModifiedDateTime` filtering.

### 6.5 Schema discovery

Standard OData `$metadata` endpoints. Per-entity OData V4 reference is in the API Guide PDF (linked in §11).

### 6.6 Key entity relationships

```
PerPerson (1)
  +-- PerPersonal (N, effective-dated)
  +-- PerPhone (N), PerEmail (N)
  +-- EmpEmployment (N, one per employment)
        +-- User (1)
        +-- EmpJob (N, effective-dated)
        |     +-- FOCompany, FODepartment, FOJobCode, FOPayGrade, Position
        +-- EmpCompensation (N, effective-dated)
              +-- EmpPayCompRecurring (N)
```

---

## 7. Customer-Side Onboarding

1. **Register an OAuth 2.0 Client Application** in SuccessFactors Admin Centre (Manage OAuth2 Client Applications). Upload BareCount's public certificate; receive the API key.
2. **Identify the integration user** — typically a dedicated technical user with the minimum RBP needed for the modules BareCount will admit.
3. **Confirm regional API host** (e.g. `api.successfactors.eu` for EU-hosted tenants).
4. **Confirm module entitlements** match the entities to be admitted.
5. **Sign the PII data-flow agreement** with BareCount, enumerating fields, retention, and legal basis.
6. **Hand BareCount**: API host, OAuth client ID, integration user identity, RBP role.

---

## 8. BareCount-Side Onboarding

Connection profile shape:

- `system_type_code: 'sap_successfactors'`
- `endpoint_url` — regional API host
- `auth.method: 'oauth2_saml_bearer'` (new method to add to `CredentialResolverService`)
- `auth.credential_ref` — reference to SAML key + OAuth client ID in external store
- `module_scopes[]` — modules BareCount may admit from, matched to PII data-flow agreement
- `pii_policy_ref` — reference to the signed PII agreement

Smoke test: hit `$metadata` for one module's V4 endpoint, then fetch one record with `$top=1`.

---

## 9. Verified Coverage

**Nothing.** No SuccessFactors entity has been admitted from any customer or sandbox tenant.

---

## 10. Known Gaps

1. **OAuth 2.0 SAML Bearer Assertion** auth method is not yet implemented in `CredentialResolverService`. This is a hard prerequisite.
2. **Basic Auth migration deadline** (Nov 2026) means any future Basic-Auth-only customer must migrate before BareCount can integrate.
3. **OIDC** support — second-priority auth method.
4. **PII data-flow agreement template** — needs legal-reviewed template before first SuccessFactors customer.
5. **Effective-dated read strategy** in canonical resolution — SuccessFactors's effective-dating semantics need to be reconciled with BareCount's temporal gates and fiscal-period model.
6. **Module-entitlement vs admission-contract mapping** — policy needs to be documented for prospects.
7. **Concrete reader flavor `sap-successfactors-odata-v4`** not yet built.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — SAP API admission stance (D384) | [ADR-d2cdb9](../../governance/adrs/ADR-d2cdb9.md) |
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Companion appendix — SAP licensing & catalogue rules | [sap-licensing-reference.md](sap-licensing-reference.md) |
| OData V4 API Reference Guide (PDF) | https://help.sap.com/doc/2d1d6fcc4eae4db8b9bbd3103baee1c7/2511/en-US/HXMSuiteODataAPIRefGuideV4.pdf |
| OData V2 API Reference Guide | https://help.sap.com/docs/successfactors-platform/sap-successfactors-api-reference-guide-odata-v2/about-sap-successfactors-odata-apis-v2 |
| Data Protection and Privacy | https://help.sap.com/docs/SAP_SUCCESSFACTORS_PLATFORM/2becac773fcf4f84a993f0556160d3de/13ebd268d4dd4686b8162794305c2984.html |
| OAuth 2.0 SAML Bearer KBA 3462403 | https://userapps.support.sap.com/sap/support/knowledge/en/3462403 |
| SuccessFactors product page | https://www.sap.com/products/hcm.html |
| Predecessor — legacy v2 archive SAP SuccessFactors reference | legacy-v2/reference/sources/sap-successfactors.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
