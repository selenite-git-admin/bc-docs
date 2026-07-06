---
uid: SRC-d6e4f2
slug: rockwell-factorytalk
title: "Rockwell Automation FactoryTalk"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: mes
subdomain: rockwell
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://support.rockwellautomation.com
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/rockwell-factorytalk.md
---

# Rockwell Automation FactoryTalk

This page records BareCount's source-admission posture for Rockwell Automation FactoryTalk. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no Rockwell auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidates:

- `rockwell-plex-rest` — Plex Cloud REST API (well-documented).
- `rockwell-factorytalk-eihub` — EIHub bridge for on-premises FactoryTalk products.
- `rockwell-historian` — historian-specific time-series reader (separate from MES).

---

## 3. What BareCount Admits

### 3.1 Metadata

Equipment master (machines, work cells, production lines, areas, sites — ISA-95 hierarchy); product definitions (part numbers, BOMs, routings, material specs); work-order definitions (structures, operation sequences, material requirements); recipe master (Batch / PharmaSuite — master recipes, control recipes, formula parameters per ISA-88); resource definitions (personnel quals, tools, material classes).

### 3.2 Business data — production

Production records (work-order execution events, op start/complete timestamps, quantities, scrap); material consumption (raw material usage per WO, lot-level); genealogy (forward + backward, serial-number tracking); WIP tracking; labour records.

### 3.3 Business data — quality and performance

Inspection results (in-process and final, measurements, pass/fail); SPC (control charts, Cp/Cpk, OOC events); OEE (availability, performance, quality); downtime events (reason codes, duration); batch execution records (electronic batch records).

### 3.4 Business data — historian

Time-series tag data (sub-second resolution); tag metadata (names, engineering units, ranges, scan classes, data types).

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

### 6.1 API surfaces (per product)

| Product | Surface |
|---|---|
| Plex | REST API at `https://cloud.plex.com/api/` |
| FactoryTalk ProductionCentre | EIHub (on-prem bridge) |
| Historian | OPC-HDA / proprietary API |
| Edge Gateway | MQTT / Kafka / REST egress |

### 6.2 Auth

| Product | Auth |
|---|---|
| Plex | OAuth 2.0 client credentials |
| FactoryTalk on-prem | EIHub-managed credentials |
| Historian | Per-product (typically Windows AD) |

### 6.3 Pagination and incrementality

Plex REST: standard offset/cursor. Incremental via `modified_since` filters. Historian: time-range based (start/end timestamp per query).

### 6.4 Edge data path

For real-time machine data (Historian, Edge Gateway), BareCount admission goes through the platform's API surface or via Edge Gateway egress (MQTT / Kafka) — not direct equipment connection.

---

## 7. Customer-Side Onboarding

1. Identify FactoryTalk products in scope (Plex, ProductionCentre, Historian, etc.).
2. For Plex: customer authorises BareCount via OAuth 2.0 in Plex Developer Portal.
3. For FactoryTalk on-prem: customer configures EIHub bridge to expose required services.
4. Hand BareCount: tenant URL, OAuth credentials (Plex) or EIHub configuration (on-prem), list of products + modules in scope.

---

## 8. BareCount-Side Onboarding

Per-product connection profile:

- Plex: `system_type_code: 'rockwell_plex'`; OAuth client credentials.
- FactoryTalk on-prem: `system_type_code: 'rockwell_factorytalk_eihub'`; EIHub credentials.
- Historian: `system_type_code: 'rockwell_historian'`; per-product auth.

A single Rockwell customer may have multiple connection profiles (one per product).

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Plex REST executor** with OAuth 2.0 client credentials.
2. **EIHub bridge** for on-premises FactoryTalk products.
3. **Historian time-series reader** — different shape from MES (OPC-HDA-style).
4. **Edge Gateway egress** subscriber (MQTT / Kafka).
5. **Per-product canonical mapping** — Plex schema differs from FactoryTalk on-prem; common canonical layer must accommodate both.
6. **Multi-product onboarding** — connection-profile model must support multiple Rockwell products under one customer.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Rockwell Automation Support | https://support.rockwellautomation.com |
| Plex Developer Portal | https://cloud.plex.com/developer/ |
| FactoryTalk product page | https://www.rockwellautomation.com/en-us/products/software/factorytalk.html |
| Predecessor — legacy v2 archive Rockwell FactoryTalk reference | legacy-v2/reference/sources/rockwell-factorytalk.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
