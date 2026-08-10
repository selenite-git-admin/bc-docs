---
uid: odoo-connector-build-plan
title: Odoo 19 EE Connector — Build Plan (Part 1)
description: Sequenced plan to author a platform Odoo 19 Enterprise JSON-RPC Connector (catalog row + reader-runtime executor + Odoo credential resolution + reachability proof) so a Reader can reach the Odoo source for admission. Part 1 of a two-part arc; the live-source Scanner is Part 2 (deferred, depends on the parked field-capability ADR DEC-7a18af). Anchors on DEC-731c15 (pilot connector-read release) and DEC-95687d (connector = primary onboarding trigger). Under review — not yet a design; design (ADR + PR to Codex) follows plan sign-off.
status: complete
date: 2026-08-10
project: bc-core
domain: connectors
subdomain: source-catalog/connector
focus: build-plan
---

# Odoo 19 EE Connector — Build Plan (Part 1)

## 0. Status & provenance

**Status: COMPLETE (2026-08-10).** Delivered end-to-end via the drill (plan → design → Codex disposition → execute):
- **Design:** ADR **DEC-12558e (D568)** — Odoo as a proprietary JSON-RPC connector (`transport_type=http`,
  `executor_class=OdooJsonRpcProtocolReader`, reuse `basic` auth). Codex ACCEPTED-WITH-BOUNDARY.
- **Code:** `OdooJsonRpcExecutor` merged (bc-core PR #675, `d78e1747`) — read-only, 10 unit tests.
- **Registration:** `odoo-jsonrpc` (generic) + `odoo-ent-v19` (source-bound) rows registered via `POST /connectors`,
  now `available` (after the TSK-813287 status-vocab DBCP, PR #676).
- **Reachability ladder complete:** rung-1 (container-internal, authenticated — `login_uid=2`, 49,720 account.move)
  + rung-3 (external — `15.207.106.146:8169`, Odoo `19.0+e-20260806`).
- **Boundary held:** Reader Flavor / Connection / live observation deferred behind the OC hold (**D555**); the
  live-source Scanner is Part 2 (**DEC-7a18af**, parked).

The original plan text follows unchanged for the record.

Grounded by a read-only study (2026-08-10) of the platform model (bc-docs) and the bc-core implementation:
- Connector concept: `docs/reference/glossary/README.md`, `docs/operating-model/admission-and-observation.md`, `docs/implementation/internal-modules.md`.
- Anchoring ADRs: `docs/governance/adrs/ADR-731c15.md` (DEC-731c15), `docs/governance/adrs/ADR-95687d.md` (DEC-95687d).
- bc-core code: `src/database/schema/runtime/connector.ts`, `src/registry/connections/connector.*`, `src/registry/seed/seed-protocol-connectors.ts`, `src/boundary/reader-runtime/executors/sap-odata-v2.executor.ts`, `src/boundary/reader-runtime/{reader-executor.interface,executor-registry.service}.ts`.
- Transport reference: `bc-demo/simulator/adapters/odoo19ee/client.py` (live-proven Odoo-19 JSON-RPC; crib, do not ship).

## 1. What this is / is not

**Is:** a plan to author a **platform Odoo 19 EE JSON-RPC Connector** — the artifact that declares the protocol-level ability to *reach* the Odoo source and returns observed records for admission (step 1 of the fixed admission sequence).

**Is not:** schema/mapping work (that is the Source Catalog + Observation Contract), tenant credential work (that is a Connection), or live-source introspection (that is the Scanner — Part 2).

## 2. The concept, as established by study

A **Connector** is a *platform-authored protocol + auth-method capability, per source-system type* — glossary: "the protocol-level ability to reach a Source System over a defined protocol with supported authentication methods." Four-artifact split:

| Artifact | Scope | Role |
|---|---|---|
| **Connector** | Platform | Protocol + supported auth methods to reach a source-system class |
| **Reader / Reader Flavor** | Platform | UniBAT admission; a Flavor binds **one Connector + one Observation Contract + one source-version** |
| **Connection** | Tenant | Pairs a Reader Flavor with a catalog entry; carries **per-tenant instance credentials** |

Storage (D089 three-table split): `runtime.connector` + `connector_protocol` (`transport_type`, `executor_class`, `supported_auth_methods`, `default_flavor_config_json`) + `connector_provenance`. Lifecycle `draft → available → deprecated → retired` (D063). Runtime: a `ReaderExecutor.execute()` in `src/boundary/reader-runtime/executors/`, registered by `executor_class` into `ExecutorRegistryService`, receiving **pre-resolved** credentials and mapping records → `RunObservationItem[]`.

**Gap today:** no Odoo, no JSON-RPC/XML-RPC anywhere; `transport_type ∈ {http, sdk, file}`; 8 seeded protocol connectors (closest generic = `rest-oauth2`, draft). DEC-95687d makes the Connector the **primary onboarding trigger** that chain-walks `connector → readers → reader_flavor → SC → OC → CC → MC → fact.*`.

## 3. Scoping constraint (the boundary of Part 1)

A runnable **Reader Flavor requires an Observation Contract**, and **OC/CC/MC are HELD under D555**. Part 1 therefore stops at the boundary that does **not** need an OC:

- **In scope (Part 1, unblocked):** Connector catalog row(s) + JSON-RPC executor + Odoo credential resolution + reachability proof.
- **Deferred (gated elsewhere):** Reader Flavor + Connection + live observation run — need an OC (D555) + a tenant; belong to the tenant-onboarding lane.
- **Part 2 (Scanner):** live-source introspection → catalog; depends on the parked field-capability ADR **DEC-7a18af** (empirical `source_field_capability` satellite). Not started.

## 4. Units of work (one-then-many, sequenced)

| Unit | Work | Notes |
|---|---|---|
| **U1** | Transport model decision | Recommend `protocol_name='odoo-jsonrpc'` over `transport_type='http'` (JSON-RPC *is* HTTP POST to `/jsonrpc`) — avoids widening the transport enum. Executor class `OdooJsonRpcProtocolReader`. Resolve in design phase. |
| **U2** | Connector catalog registration | Via official `POST /connectors` (no direct DB inserts): a generic `odoo-jsonrpc` protocol connector + a source-bound `odoo-ent-v19` connector (mirrors `odata-v2` + `sap-odata-v4`). `supported_auth_methods=['password']`; `default_flavor_config` (base-URL template, batch size, company-context strategy). |
| **U3** | JSON-RPC executor | `OdooJsonRpcExecutor implements ReaderExecutor` in `boundary/reader-runtime/executors/`: port `client.py` — authenticate→uid, `execute_kw` search+read paginated, company context (S-4/S-34), map each record → `RunObservationItem` (sourceKey = id+company, `observedPayloadJson`, provenance). Plain `fetch()`, no npm deps. Register in `BoundaryModule.onModuleInit`. Read-only (S-32: never write `state`). |
| **U4** | Credential resolution | Confirm/extend `credential-resolver` to produce Odoo's `{url, db, login, password}` shape for the two-step auth. Pilot secret read from the host file at run time (never into repo/scripts). |
| **U5** | Reachability proof (go/no-go) | Prove **rung 1** (container-internal `execute_kw` on `pilot_ent` with the real credential) through the executor path. Independent verification: an observed `login_uid` / re-read is the proof, not script output. Rung 3 (external URL + security-group posture) is an explicitly-gated, operator-facing step — not folded in. |

## 5. Foundation gate (admission-boundary A change)

- **Location A** (source reality / admission boundary — the Connector is *how* the source is reached); executor lives in the reader-runtime boundary (D). No lower-layer compensation.
- **Design vs execution (D541):** authoring the Connector capability + executor is the design act; running it against pilot is execution over it.
- **Invariants:** VI (evidence emitted) — a reachability claim is proven by observed `login_uid`/re-read, not asserted; III — executor is read-only, observation is non-mutating (S-32). No invariant conflict.

## 6. Governance / the drill

Plan (this doc, reviewed) → **Design:** ADR for the Odoo connector + transport model + executor, as a **PR to Codex for disposition** → **Execute** on ACCEPT + operator authorization: register via API, land the executor, prove rung 1. No live writes and no PR until the plan is agreed. Bracketed by the session plan/report change record (ISO 27001 pair).

## 7. Open decisions to resolve in the design phase

1. **Transport modeling** — model as `odoo-jsonrpc`/`http` (no enum change, recommended), or a first-class `jsonrpc` transport type?
2. **Part-1 boundary** — confirm Part 1 ends at the reachability proof (Connector + executor + creds), with Reader Flavor/Connection deferred behind the OC (D555) hold.
3. **Reachability depth** — rung 1 (container-internal) as the Part-1 go/no-go, treating external URL as a separate gated step?

## 8. Risks

- **R1 — External reachability is operator-gated.** The platform Reader consumes the external URL (rung 3); Part 1 deliberately proves only rung 1. A "connector works" claim must not over-reach to rung 3.
- **R2 — Credential shape mismatch.** `credential-resolver` may not model Odoo's two-step `authenticate→uid` today; U4 may surface a small resolver extension (design-phase check).
- **R3 — OC dependency (D555).** No runnable Reader Flavor until an OC exists; Part 1 must not quietly build toward a Flavor that cannot be activated.
- **R4 — Field renames (S-10).** Odoo v19 field/model renames (`payment.ref→memo`, `groups_id→group_ids`, etc.) affect any concrete read; the executor is generic (model+fields passed in) so this bites at reader-flavor authoring, not here — noted for Part 2/OC lane.

## 9. Verification protocol

- **U2:** re-read the registered connector rows via `GET /connectors/:id` (side-effect is proof).
- **U3:** unit test the executor against the JSON-RPC transport contract (mock transport), asserting the observation mapping shape.
- **U5:** container-internal `execute_kw` returns a live `login_uid` and a sample record for one model on `pilot_ent` — captured as evidence.
