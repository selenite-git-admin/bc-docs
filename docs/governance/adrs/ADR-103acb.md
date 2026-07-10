---
uid: DEC-103acb
title: "Tenant onboarding mandatory-field policy + completeness gate (block activation until identity is complete)"
description: "Tenant onboarding mandatory-field policy + completeness gate (block activation until identity is complete)"
status: decided
date: 2026-07-08T02:43:34.793Z
project: bc-core
domain: tenant
subdomain: onboarding/identity
focus: governance
---

# Tenant onboarding mandatory-field policy + completeness gate (block activation until identity is complete)

## Context

No rationale recorded.

## Decision

CONTEXT (verified live, SES-96cf45). Tenant onboarding is piecemeal, not transactional, and enforces almost no identity completeness: POST /tenants (TenantManagementService.createTenant) captures only slug/name/config, provisions an empty schema, and flips tenant.status_code to 'active' purely on DDL success — no identity data is collected or checked. Of the four tenant-identity surfaces, only tax_registration (DEC-9c430b/D503) has a governed writer + enforced required fields; org_profile, tenant_dim.dim_legal_entity, and organization.fiscal_calendar_config have NO governed writers (populated ad hoc/seed/manual), so their NOT NULLs only bite if a row is written and nothing requires the rows to exist. Result: a tenant can be 'active' with an empty org_profile, ZERO legal entities, no fiscal calendar, and no reporting standard. There is no onboarding completeness gate (the readiness subsystem is metric/catalog-only); the sole guard is a lazy runtime exception (FiscalCalendarService: 'complete onboarding before evaluating metrics'). Accounting/reporting standard is not modeled at all (note: 'Multi-Standard Onboarding' is a BF/BO vocabulary concern, NOT tenant reporting standard). This underspecified onboarding is why D502 (currency normalization needs functional/reporting currency + standard) and D503 (tax needs registrations + regime) would fail-closed at runtime on missing config rather than being guaranteed at onboarding.

DECISION.

D1 — MANDATORY-FIELD POLICY. A tenant may reach 'active' only when the following identity set is present:
- Tenant (org_profile): legal_name, reporting_currency_code, hq_country_code, reporting_standard (D2).
- At least ONE legal entity (dim_legal_entity), each with: legal_entity_code, display_name, functional/local currency (currency_code), country_code, fiscal_calendar_code.
- At least one fiscal_calendar_config resolvable for each legal entity (tenant-default '*' or per-entity) — metric evaluation requires it.
- Tax registration (D503): ≥1 per legal entity CONDITIONALLY — required only where the jurisdiction/regime demands one (region-aware, D5); not universally mandatory.
Fields beyond this set (display_name, reporting_jurisdiction, contacts, jurisdiction_code) remain optional/recommended.

D2 — reporting_standard (NEW FIELD). Add organization.org_profile.reporting_standard (the tenant's reporting/accounting standard: ind_as | ifrs | us_gaap | ...), mandatory. It is the tenant-level default; per-legal-entity override (a subsidiary under local GAAP vs group IFRS) is a deferred extension. This field feeds the DEC-f6527b/D502 FX rate-date selector and the DEC-9c430b/D503 tax-point selector — both are 'driven by accounting standard × metric temporal semantic', so the standard must be captured.

D3 — ENFORCEMENT = BLOCK ACTIVATION. Introduce a tenant lifecycle state onboarding_incomplete between provisioning and active: provisioning -> onboarding_incomplete -> active. A tenant advances to 'active' ONLY when a governed completeness check (D4) passes; until then it stays onboarding_incomplete (visible, not silently 'active'). Activation is the single governed choke point (TenantManagementService, or a dedicated complete-onboarding endpoint). This is a governed GATE, not column NOT NULLs — existence-of-rows and cross-surface completeness cannot be a column constraint, and per D268 brittle NOT NULLs are the wrong tool.

D4 — GOVERNED WRITERS (prerequisite). org_profile, dim_legal_entity, and fiscal_calendar_config need governed @TenantScoped services + controllers (services-only), mirroring the tax-registration service/controller template, so the mandatory fields can be populated through a governed path the gate can then check. A TenantIdentityCompletenessService performs the read (per-field present/missing per tenant), modeled on the metric ReadinessService shape.

D5 — REGION-AWARE CONDITIONAL RULES. The tax-registration requirement is conditional on jurisdiction/regime (e.g. an India entity under GST => a GSTIN is required; a jurisdiction without such a scheme => none). Start with a small explicit jurisdiction->required-regime map; a richer rules table is a later extension.

D6 — BUILD PHASES. Phase A (this ADR): policy + gate design locked. Phase B: governed writers for the three identity surfaces + the reporting_standard column (DB Change Protocol). Phase C: the completeness check + the onboarding_incomplete status + activation gate. Phase D (out of unit): bc-admin/portal onboarding UI wiring.

FOUNDATION GATE. Repair-location C (tenant master/binding) + a governed onboarding boundary. Not lower-layer compensation: the runtime fiscal-calendar exception (D) is a symptom of missing B/C config; the fix is completeness at the onboarding boundary, not more lazy runtime guards. Invariants: III — tenant identity is versioned (effective dates + soft-delete on the writable surfaces), corrections are new versions; IV — mandatory references (currency, standard, calendar) are explicit; VI — the completeness check emits a clear, enumerated incomplete reason (evidence), never a silent pass.

WHAT THIS DOES NOT SOLVE. The onboarding UI (bc-admin/portal) — Phase D. Per-legal-entity reporting_standard override — deferred. Automated jurisdiction->tax-regime inference beyond a small seed map — deferred. Backfill/gating of ALREADY-active tenants (e.g. pilot1, currently empty) — a migration decision at Phase C (grandfather vs force-complete).

RELATIONSHIP. Enables DEC-f6527b/D502 (currency) + DEC-9c430b/D503 (tax) by guaranteeing their config inputs at onboarding. Task: TSK-e95066 (this) + follow-ups for Phases B/C.
