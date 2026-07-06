---
uid: SRC-a1c4d7
slug: bmc-helix
title: "BMC Helix ITSM"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: itsm
subdomain: bmc
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://docs.bmc.com/xwiki/bin/view/Service-Management/IT-Service-Management/BMC-Helix-ITSM/itsm253/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/bmc-helix.md
---

# BMC Helix ITSM

This page records BareCount's source-admission posture for BMC Helix ITSM. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for either Helix REST surface; no AR System auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `bmc-helix-simplified-rest` — recommended for new integrations.
- `bmc-helix-platform-rest` — fallback for entities not in the Simplified surface.

---

## 3. What BareCount Admits

### 3.1 Metadata

ITSM categories and templates, SLA definitions, support group structure; CMDB class definitions (rooted at `BMC_BaseElement`), attribute definitions, relationship types; categorisation schemas, status / lifecycle models, approval workflows.

### 3.2 Business data

| Domain | AR form |
|---|---|
| Incidents | `HPD:Help Desk` |
| Problems | `PBM:Problem Investigation` |
| Changes | `CHG:Infrastructure Change` |
| Work Orders | `WOI:WorkOrder` |
| Known Errors | `PBM:Known Error` |
| CMDB CIs | `BMC.CORE:BMC_BaseElement` |
| Assets | `AST:ComputerSystem` |
| Service Requests | `SRM:Request` |
| Knowledge Articles | `KMS:Knowledge` |

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

### 6.1 Simplified REST API (recommended)

| Aspect | Detail |
|---|---|
| Base path | `/api/smart-it/v1/` |
| Methods | GET / POST / PUT / DELETE on ITSM-specific entities |
| Format | JSON |
| Auth | Token-based after login |

### 6.2 Platform REST API (fallback)

| Aspect | Detail |
|---|---|
| Base path | `/api/arsys/v1/entry/{form}` |
| Methods | Lower-level AR System form CRUD |
| Format | JSON |
| Use | Entities not exposed in Simplified API; complex queries via Q query language |

### 6.3 Auth

1. POST credentials to `/api/jwt/login` → receive JWT.
2. Use `Authorization: AR-JWT <token>` on subsequent calls.
3. Token has configurable lifetime; refresh by re-authenticating.

### 6.4 Pagination and incrementality

Q-style queries with `offset` + `limit`. Incremental admission via `Modified-Date` filter; the legacy AR System uses YYYY-MM-DDTHH:MM:SS format with timezone awareness.

### 6.5 Rate limits

Not publicly published. Per-tenant fair-use; HTTP 429 on excess.

---

## 7. Customer-Side Onboarding

1. Customer allocates one named-user licence to a BareCount service-account user.
2. Configures the user with read-only role (e.g. "Read License") for the modules in scope.
3. Customer provides JWT login endpoint, service-account credentials, and tenant URL.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'bmc_helix'`
- `tenant_url`
- `auth.method: 'arsys_jwt'`
- `auth.credential_ref` — service-account credentials (login → JWT)
- `licensed: true` — informational

Smoke test: `POST /api/jwt/login`, then `GET /api/smart-it/v1/incidents?limit=1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **AR System JWT auth helper** — login → JWT → use-on-subsequent-calls flow.
2. **Simplified REST executor** for the recommended new-integration path.
3. **Platform REST executor** for fallback entities.
4. **Q query language** support for complex Platform API queries.
5. **Licence-cost advisory** — same as ServiceNow; surface during onboarding.
6. **Form-name discovery** — AR forms can be customer-customised; admission contract design must enumerate.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| BMC Helix ITSM docs | https://docs.bmc.com/xwiki/bin/view/Service-Management/IT-Service-Management/BMC-Helix-ITSM/itsm253/ |
| Simplified REST API | https://docs.bmc.com/xwiki/bin/view/Service-Management/IT-Service-Management/BMC-Helix-ITSM/itsm253/Developing-and-extending/Smart-IT-REST-APIs/ |
| AR System JWT auth | https://docs.bmc.com/xwiki/bin/view/IT-Operations-Management/Action-Request-System/Action-Request-System-25/Developing/AR-System-REST-API/ |
| Predecessor — legacy v2 archive BMC Helix reference | legacy-v2/reference/sources/bmc-helix.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
