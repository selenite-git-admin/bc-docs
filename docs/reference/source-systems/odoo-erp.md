---
uid: SRC-a8c3e7
slug: odoo-erp
title: "Odoo ERP"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: enterprise-erp
subdomain: odoo
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.odoo.com/documentation/18.0/developer/reference/external_api.html
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/odoo-erp.md
---

# Odoo ERP

This page records BareCount's source-admission posture for Odoo ERP. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for any Odoo external API; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `odoo-erp-jsonrpc` — JSON-RPC for Odoo v14–v18.
- `odoo-erp-json2` — JSON-2 API for Odoo v19+ (forward-compatible to v20).

(XML-RPC executor not planned — overlaps with JSON-RPC capability and is on the same removal track.)

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of accounts (`account.account`, `account.group`); companies, currencies, exchange rates (`res.company`, `res.currency`); fiscal positions, journals, tax configuration; partners (customers, vendors, contacts); products, categories, warehouses, location hierarchy; model field introspection via `fields_get()`.

### 3.2 Business data

| Domain | Models |
|---|---|
| Journal Entries | `account.move` (type=`entry`), `account.move.line` |
| Customer Invoices | `account.move` (type=`out_invoice`, `out_refund`) |
| Vendor Bills | `account.move` (type=`in_invoice`, `in_refund`) |
| Payments | `account.payment` |
| Bank Statements | `account.bank.statement`, `account.bank.statement.line` |
| Sales Orders | `sale.order`, `sale.order.line` |
| Purchase Orders | `purchase.order`, `purchase.order.line` |
| Stock Moves | `stock.picking`, `stock.move` |
| Manufacturing | `mrp.production`, `mrp.bom`, `mrp.workorder` |

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

### 6.1 API protocols

| Protocol | URL | Status |
|---|---|---|
| JSON-RPC | `/jsonrpc` | Current standard (v10+). **Deprecated in v19, removal in v20.** |
| XML-RPC | `/xmlrpc/2/common`, `/xmlrpc/2/object` | Legacy. **Deprecated in v19, removal in v20.** |
| JSON-2 API | `/json/2/{model}/{method}` | New in v19. Future standard. |
| REST API | Various | Experimental (v17+); incomplete coverage. Not for production. |

### 6.2 Authentication

Two phases per session:

1. **Authenticate** — `common.authenticate(db, login, password_or_apikey, {})` returns a `uid` (user ID).
2. **Operate** — subsequent calls pass `db`, `uid`, `apikey` plus `model`, `method`, `args`, `kwargs`.

API keys are preferred over passwords (configurable in Odoo's user preferences).

### 6.3 ORM operations (the mental model)

Odoo's external API exposes the **ORM** — every record-level operation is `model.method(args)`:

- `search([domain])` — returns IDs matching the domain expression.
- `read(ids, fields)` — returns dicts of records.
- `search_read([domain], fields)` — combined.
- `create([dicts])` — write new records.
- `write(ids, dict)` — update.
- `unlink(ids)` — delete.

For BareCount admission, the primary operations are `search_read` and `fields_get` (for schema introspection).

### 6.4 Pagination and incrementality

`search_read` accepts `limit` and `offset`. Incremental admission via domain filter on `write_date` (every Odoo record has it):

```
search_read([['write_date', '>=', last_seen]], ['id', 'name', 'write_date'])
```

### 6.5 Modules and customisation

Odoo customers commonly install community / custom modules that add models or fields. The catalogue must auto-discover via `fields_get()` per customer; cannot be pre-seeded for non-stock modules.

---

## 7. Customer-Side Onboarding

1. Confirm Odoo edition: Community / Enterprise Custom / Odoo.sh — or **decline** if Enterprise Standard.
2. Confirm Odoo version.
3. Customer creates a dedicated API user with read-only permissions for the modules in scope.
4. Customer generates an API key for the user (Settings → Users → Account Security → New API Key).
5. Confirm network access to the Odoo server (hosted URL or VPN for self-hosted).
6. Hand BareCount: server URL, database name, login, API key, list of installed modules.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'odoo_erp'`
- `endpoint_url`
- `database_name`
- `odoo_version` (drives JSON-RPC vs JSON-2 protocol choice)
- `auth.method: 'odoo_apikey'`
- `auth.credential_ref` — api key + login

Smoke test: authenticate, then `res.company.search_read([], ['name'])` for company list.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **JSON-RPC executor** — phase-1 fit for v14–v18 customers (the majority in the readiness baseline).
2. **JSON-2 executor** — phase-2 for v19+ customers.
3. **ORM domain expression DSL** — must serialise domains to the polish-prefix list shape Odoo expects.
4. **Schema introspection at admission contract design time** — `fields_get()` per model.
5. **`write_date` delta** — universal; should be the default delta strategy.
6. **Edition gate detection** — admission onboarding must reject Enterprise Standard prospects with a clear message.
7. **Module discovery** — installed modules vary; the catalogue is per-customer.
8. **v20 removal of XML-RPC + JSON-RPC** (fall 2026) — protocol-version gate must be enforced; customers approaching v20 must migrate to JSON-2 first.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Odoo External API (v18) | https://www.odoo.com/documentation/18.0/developer/reference/external_api.html |
| Odoo Documentation — All versions | https://www.odoo.com/documentation/ |
| Odoo Pricing | https://www.odoo.com/pricing-plan |
| API Keys | https://www.odoo.com/documentation/18.0/applications/general/users/access_rights.html |
| Predecessor — legacy v2 archive Odoo ERP reference | legacy-v2/reference/sources/odoo-erp.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
