---
uid: DEC-0a614d
title: "Retain the real-SAP OData executors dormant (do not retire) — corollary of D524"
description: "Keep bc-core SapOdataV4Executor + SapOdataV2Executor dormant (inert, protocol-stable, tested) rather than retiring them during the bc-sdg archival; supersedes no ADR — corollary of D524's SAP retention."
status: decided
date: 2026-09-06T13:18:34.603Z
project: bc-core
domain: readers
subdomain: reader-runtime
focus: lifecycle
---

# Retain the real-SAP OData executors dormant (do not retire) — corollary of D524

## Context

During the bc-sdg archival the real-SAP executors surfaced as apparent dead code. Removing them would (1) contradict the still-live D524, which deliberately retains SAP realization for a future real SAP customer; (2) discard working, tested, protocol-stable transport — the genuinely reusable part, since the SAP OData protocol does not drift like flavor/contract bindings — for purely cosmetic cleanliness with zero live benefit; and (3) force re-deriving that transport when a real SAP customer lands. The executors are fully inert (no SAP source_system/connector/reader_flavor/connection after TSK-efb8f5) so they cannot be mistaken for a live SAP integration in the catalog. What was retired was SAP coupled to synthetic data; generic real-SAP transport is a different category. Recording this as a governed ADR keeps the retention decision from being re-litigated in future cleanups. The decision was delegated to Claude (co-owner / Principal Architect) by the operator on 2026-09-06 and is filed as 'proposed' for operator sign-off (proposed -> decided).

The bc-core reader-runtime executors **SapOdataV4Executor** (registered as `ODataV4ProtocolReader` and legacy flavor `sap_odata_v4`) and **SapOdataV2Executor** (`ODataV2ProtocolReader`) are RETAINED in a DORMANT state and are NOT retired during or after the bc-sdg archival arc (2026-09-06).

DORMANT means: the executor classes and their `BoundaryModule` registrations remain, but no active SAP `source_system`, `connector`, `reader_flavor`, or `connection` references them. Verified 2026-09-06 against bc_platform_dev — the live catalog is Odoo-only; the synthetic `sap_ecc` connections and the `SAP SE` provider were deleted under TSK-efb8f5. The executors are therefore unreachable at runtime until a real SAP source is onboarded through the normal source-registration flow.

## Scope boundary — retired vs retained

RETIRED already (NOT by this ADR):
- SAP as a live source and everything coupled to synthetic SAP data — the SAP source catalogs + their contract chain (DEC-ea9bdc; expunged under DEC-296505 / D564);
- the bc-sdg SDG-SAP simulator and the **SdgOdataExecutor** (bc-sdg archived 2026-09-06; SdgOdataExecutor removed in bc-core PR #723 / TSK-fc8606);
- the SAP-as-live-source ADR family incl. DEC-076521 (all superseded by DEC-b390ef on 2026-08-23).

RETAINED (this ADR): the generic real-SAP OData transport executors — CSRF handshake, `sap-client`/`sap-language` headers, `$top`/`$skip` + `@odata.nextLink` pagination — which are protocol-stable, unit-tested (`sap-odata-v4.executor.spec.ts`, green in CI), and independent of the synthetic data that was retired.

## Relationship to existing ADRs — THIS ADR SUPERSEDES NO ADR

- **DEC-58b56c (D524) — basis.** D524 retains SAP realization "until a real SAP customer grants access." This ADR is a corollary that names the concrete consequence: the real-SAP transport code IS that retained capability and stays. D524 is affirmed, not superseded.
- **DEC-b390ef — clarified, not changed.** The 2026-08-23 legacy-doctrine supersession register superseded the SAP-as-live-source family (incl. DEC-076521). This ADR clarifies that that supersession retired the *design* (SAP as a live source / the apex-demo framing) and the synthetic coupling — NOT the generic transport executor *code*.
- **DEC-076521 — remains superseded;** its `SapOdataV4Executor` is retained dormant (the code outlives the superseded design ADR). Status unchanged.
- **DEC-ea9bdc / DEC-296505 (D564)** — the SAP catalog + chain contamination/expunge; cited as what was retired; unchanged.

**This ADR does not supersede any ADR and requires no status change to any other ADR.**

## Trigger to reverse (retire the executors)

An explicit decision that SAP is permanently off BareCount's roadmap. That is a governed AMENDMENT to D524 (DEC-58b56c), not a cleanup — at which point SapOdataV4Executor/SapOdataV2Executor and their BoundaryModule registrations are removed under normal bc-core review, and this ADR is marked superseded by that amendment.

## Adjacent hygiene note (not acted on here)

DEC-b0839a ("SDG Coherent Snapshots and Multi-Projection Architecture") is still `decided` yet describes the now-archived bc-sdg SDG-snapshot path. It is orthogonal to this decision (SDG snapshot architecture, not the transport executors) and is NOT superseded here — this ADR is not its successor. Flag for a separate ADR-hygiene review.

## Operator decision record

Ruled `proposed → decided` by anant on 2026-09-06 (DevHub session SES-bef51e). The decision was delegated to Claude (co-owner / Principal Architect) on 2026-09-06 and drafted as `proposed`; the operator reviewed and ruled it decided. Supersedes no ADR; no other ADR status changed.
