---
uid: SRC-b9d4f8
slug: odoo-crm
title: "Odoo CRM"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: crm
subdomain: odoo
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.odoo.com/documentation/18.0/developer/reference/external_api.html
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/odoo-crm.md
---

# Odoo CRM

This page records BareCount's source-admission posture for Odoo CRM. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor (shared gap with Odoo ERP); no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped (shared with Odoo ERP — same executor, model-scoped configuration):

- `odoo-crm-jsonrpc` — JSON-RPC for Odoo v14–v18.
- `odoo-crm-json2` — JSON-2 API for Odoo v19+.

---

## 3. What BareCount Admits

### 3.1 Metadata

Pipeline stage definitions (`crm.stage`); sales team structures (`crm.team`); partner categories/tags (`res.partner.category`); activity types (`mail.activity.type`); product categories and units of measure; model field definitions via `fields_get()`.

### 3.2 Business data

| Domain | Models |
|---|---|
| CRM | `crm.lead` — leads and opportunities (unified model, distinguished by `type` field) |
| Contacts | `res.partner` — companies, contacts, vendors, individuals |
| Sales | `sale.order`, `sale.order.line` — quotations and confirmed sales orders |
| Pipeline | `crm.stage` — pipeline stage definitions |
| Teams | `crm.team` — sales team assignments |
| Activities | `mail.activity` — scheduled calls, meetings, tasks, emails |
| Products | `product.product` / `product.template` — product catalog |

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

The Odoo external API is database-aware and ORM-shaped — same protocol details as the Odoo ERP page (see [odoo-erp.md §6](odoo-erp.md)).

For CRM specifically:
- `crm.lead` is a single model; the `type` field distinguishes `lead` vs `opportunity`.
- `crm.stage` defines pipeline stages with `sequence` ordering.
- `mail.activity` ties activities polymorphically via `res_model` + `res_id` — admission contract must filter to CRM-relevant activity rows.

### Common operations

```
search_read('crm.lead', [['type','=','opportunity'], ['stage_id.fold','=',False]],
            ['id','name','expected_revenue','probability','stage_id','team_id','user_id'])

search_read('mail.activity', [['res_model','=','crm.lead']], [...])
```

### Delta strategy

Universal `write_date` field on every Odoo record:
```
search_read('crm.lead', [['write_date', '>=', last_seen]], [...])
```

---

## 7. Customer-Side Onboarding

Same as Odoo ERP: confirm edition (must not be Enterprise Standard); generate an API key; provide server URL, database name, login, API key.

---

## 8. BareCount-Side Onboarding

Connection profile inherits from `odoo_erp` shape with `connector_module: 'crm'` selector or via shared connection — a single Odoo connection can serve both ERP and CRM modules.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

Same as Odoo ERP plus CRM-specific:

1. **Shared Odoo executor** (per Odoo ERP §10).
2. **CRM-specific admission contracts** — `crm.lead`, `mail.activity` filtered by `res_model='crm.lead'`, etc.
3. **Lead vs opportunity distinction** — the `type` field discriminator must be respected in canonical resolution; opportunities and leads are different business observations.
4. **Pipeline stage drift** — customer-customised stages need careful canonical-mapping management.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Companion source page | [Odoo ERP](odoo-erp.md) |
| Odoo External API (v18) | https://www.odoo.com/documentation/18.0/developer/reference/external_api.html |
| Odoo CRM module docs | https://www.odoo.com/documentation/18.0/applications/sales/crm.html |
| Predecessor — legacy v2 archive Odoo CRM reference | legacy-v2/reference/sources/odoo-crm.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
