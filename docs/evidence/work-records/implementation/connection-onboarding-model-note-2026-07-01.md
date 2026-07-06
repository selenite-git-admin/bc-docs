---
uid: NOTE-connection-onboarding-model-2026-07-01
title: "Connection Onboarding — Model Note (Slice 1 of the v3 greenfield build)"
description: "The one-page design model for the customer connection flow in the v3 (/beyond) UI: the three-level source catalog (Provider -> System -> Version), the connector selection, and the connection wizard (auth -> scope -> test). Layer ownership + tenancy, the version-as-first-class refinement to the flavor policy, and the open decisions. Design-led-just-ahead for the connector-catalog-first build."
status: draft
authority: note
date: 2026-07-01
project: bc-portal
domain: readers
---

# Connection Onboarding — Model Note

## 0. Purpose

Slice 1 of the v3 (`/beyond`) greenfield build: the **customer connection flow** — how a tenant connects a source system. Legacy `/data-sources` (source-first) is inspiration only; this is the connector-catalog-first target the v3 `ConnectionsPage` stub already specs. Operator-confirmed 2026-07-01.

## 0b. Naming resolution — the Connector lifecycle (operator-locked 2026-07-01)

"Connection" is **retired as a customer-facing concept** — it wrongly implied a live/real-time link, when the object is a *stored profile* (endpoint + credentials + config) the runtime uses. The single concept is the **Connector**, with one lifecycle:

```
Available → Configured → Active → Connected ⇄ Disconnected
```

- **Available** — the driver in the catalog (`runtime.connector`; platform, shared, tenant-agnostic).
- **Configured** — the tenant has added endpoint + a credential *reference*. Held in **`runtime.connection`** (platform DB, per **D168** — connections are infra/config; `tenant_id` for ownership). The connector-TYPE + connection-INSTANCE split; internal table name, never shown to customers. **Credentials go to AWS Secrets Manager** — `connection.authentication_json.credentialRef` points at the secret; the DB never holds the secret (satisfies 771baf: platform reads the secret store, not the tenant DB).
- **Active** — the configuration passed a test (`connection_check`) and is turned on. *Test is the gate INTO Active, not a separate standing state* (per operator "Tested/Active").
- **Connected ⇄ Disconnected** — the live reachability of an Active connector, from the latest check/run. The **only real-time state**.

Crucially, two things previously mushed into `status='connected'` are now **separate**: **lifecycle** (`configured` / `active` / `suspended` / `archived`) vs **health** (`connected` / `disconnected`, derived from the latest `connection_check`). The customer sees a **Connector** moving through these states — never the `connection` table.

The wizard is therefore **"Configure a Connector"** (endpoint + creds → test → Active → Connected), not "add a Connection." Wherever §§2–4 below say "Connection" or imply tenant-side storage, read it as *the tenant's Configured/Active Connector instance in `runtime.connection` (platform, D168)* with credentials in AWS Secrets Manager — **not** tenant-side `admin.connection` (that was a corrected mis-step; see the platform note §0a).

## 1. The source catalog — three levels (platform-managed)

A guided drill-down over the existing catalog schema:

```
Provider   (source.source_provider)   e.g. SAP                     — the vendor/brand
  └ System (source.source_system)     e.g. SAP ECC · SAP S/4HANA   — the product line
      └ Version (source.source_version) e.g. EHP8 6.0 · Public Cloud · Private Cloud — the deployment/edition
```

Live today: Provider **SAP SE**; Systems **SAP ECC**, **SAP S/4HANA**; Versions **EHP8 6.0** (ECC), **On-Premise 2023** + **Cloud 2023** (S/4HANA). The catalog is **platform-managed** — customers browse it, they do not author it.

## 2. Connectors — the protocol drivers (platform-managed)

`runtime.connector` = a driver to reach a `(system, version)` over a protocol (`connector_protocol.protocol_name` + `executor_class`). One `(system, version)` may expose **several** connectors (OData V2, OData V4, RFC…). A connector is **tenant-agnostic** — it declares reachability + capability, never credentials. Live: `odata-v2` (generic), `sap-odata-v4` (s4hana) — sparse; the catalog grows here.

## 3. The connection flow (customer wizard)

```
1. Select System     — grouped under its Provider (SAP ▸ SAP ECC · SAP S/4HANA · …)
2. Select Version    — if the system has >1 (S/4HANA ▸ Public Cloud · Private Cloud); skip if single
3. Choose Connector  — the protocol options for that (system, version)
4. Wizard: auth → scope → test → CREATE Connection
      auth  : endpoint URI + credentials (stored off-DB in the secret surface; connection_config.authentication_json holds the reference)
      scope : which data this connection admits — see §5
      test  : a connection_check (ping + auth_test) recorded on connection_check; must pass before the connection is 'connected'
   => runtime.connection (tenant-owned)
```

The output is one **Connection** — the tenant's credentialed instance of a connector against one `(system, version)`.

## 4. Layer ownership + tenancy (the corner-piece)

| Layer | Stored where | Owner (visibility) |
|---|---|---|
| Provider / System / Version (catalog) | platform | platform (shared) |
| Connector (protocol driver) | platform `runtime.connector` | platform (shared) |
| **Connection** (config: endpoint + connector + status + health) | **platform `runtime.connection` + `tenant_id`** (D168 — infra/config) | **tenant, via `tenant_id` scoping** |
| Connection **credentials** | **AWS Secrets Manager** (referenced by `credentialRef`) | tenant secret; platform reads via IAM, never the tenant DB |
| Reader / Flavor / Binding (templates) | platform | platform (shared) |

**The Connection is the tenant's anchor by *ownership*, not by storage location** (D168). Its config lives in platform `runtime.connection` with `tenant_id` (for FK integrity with connectors, admin visibility, no circular dependency — the D168 reasons); its credentials live in AWS Secrets Manager (`authentication_json.credentialRef`). Tenancy is enforced by **`tenant_id` scoping** on tenant-facing reads (not a tenant-DB move). `environment_code` = deployment stage (dev/staging/prod, NOT a tenant). Establishing a Connection is what will **enable the platform Readers for that tenant** (Slice 2). (Corrected from an earlier tenant-DB `admin.connection` mis-step — see platform note §0a.)

## 5. The `scope` step (to define with Slice 2)

After `auth`, before `test`, `scope` answers *"what does this connection admit?"* — the set of subfunctions/entities the tenant turns on (later plan/subscription-gated; ungated now). This is the seam into **Reader enablement** (Slice 2): a Connection for SAP ECC enables the AR/AP/GL/… readers whose entities that system exposes. For Slice 1 the wizard can default scope to "all available for this system"; the explicit picker lands with Slice 2.

## 6. Refinement this surfaces — version is first-class

`(system, version)` changes the **data shape** (ECC `BSAD`/`BSID` vs S/4HANA `ACDOCA`). So **Version must be a first-class dimension**, flowing down into the reader/flavor identity — not folded into a single `source_system_code`. This refines the flavor policy (ADR-17112b P-F2/P-F3): flavor identity is `(system, version, scenario)`, not `(source_system, scenario)`. Captured here; to be reconciled when Slice 2 designs the reader/flavor templates.

## 7. Decisions

- **Vendor grouping in the UI** — the System list is grouped/filtered by Provider (SAP ▸ ECC, S/4HANA). Operator-confirmed.
- **Version first-class** — flows to reader/flavor identity (§6). Operator-confirmed direction; schema reconciliation deferred to Slice 2.
- **Connection = tenant anchor** — no tenancy in flavor/connector; `environment_code` = deployment stage (§4, P-F6). Confirmed.
- **Open:** the `scope` step's exact shape (§5) — resolved with Slice 2 (reader enablement).

## 8. Slice 1 build (next)

Build the connector-catalog-first flow into the v3 `ConnectionsPage` (`/data/connections`): catalog drill-down (System ▸ Version ▸ Connector) → wizard (auth → scope[default] → test) → Connection list with health chips. Backend: the catalog + connector reads + connection create/test largely exist (legacy `/data-sources` as reference); wire them to the lean v3 page. Reader enablement + monitor = Slice 2.
