---
uid: DEC-9c430b
title: "Tax semantics — tenant tax-registration model + canonical tax-type classification (observe/classify/measure, not a tax engine)"
description: "Tax semantics — tenant tax-registration model + canonical tax-type classification (observe/classify/measure, not a tax engine)"
status: decided
date: 2026-07-08T01:14:37.539Z
project: bc-core
domain: metrics
subdomain: tax/regional
focus: architecture
---

# Tax semantics — tenant tax-registration model + canonical tax-type classification (observe/classify/measure, not a tax engine)

## Context

No rationale recorded.

## Decision

CONTEXT. Tax handling on the platform is shallow today (verified live, SES-7d00ed): 4 amount/rate metrics (invoiced_tax_amount, effective_tax_rate_on_sales, and the AP mirrors); BCF has only 'tax' (amount) + 'tax rate' concepts — no tax code, type/regime, jurisdiction, or registration; SAP MWSKZ (tax code) + MWSBK (tax amount) are catalogued in the source superset but never canonicalized into a tax type; and there is ZERO tenant/legal-entity tax identity (no GSTIN/VAT/registration field anywhere). Tax is more regime-divergent than currency: India GST (CGST/SGST/IGST/cess, a GSTIN per state, HSN/SAC rates, input tax credit, reverse charge), EU VAT (per-country rates, VAT# per country, VIES, OSS), US sales & use (state/local, nexus, origin-vs-destination, exemption certs) differ in STRUCTURE, not just rate. Tax registration is 1:N per legal entity (a registration per jurisdiction). Modern SaaS onboarding captures {Tax Name + Tax Registration Number} per entity — the pattern this ADR formalizes.

SCOPE BOUNDARY (the load-bearing decision). BareCount is a metric OBSERVATION platform. Its tax job is to OBSERVE tax as the source system emits it, CLASSIFY it canonically, and MEASURE it. It is NOT a tax engine: no rate determination, no return filing, no e-invoice IRN / VIES generation, no exemption-certificate management. Those belong to the source ERP or a dedicated tax product. This boundary prevents scope creep into compliance-filing territory and keeps tax within the fixed object progression (source → canonical → metric).

FOUNDATION GATE. Placement mirrors the currency ADR (DEC-f6527b/D502):
- C (binding / tenant master): tax REGISTRATION identity (regime + number + jurisdiction) is per-legal-entity master data — onboarding config.
- A / C (source + canonical): tax CODE (MWSKZ) → canonical tax TYPE mapping is a reader/canonical concern. Metrics must be SOURCE-AGNOSTIC (Invariant I; same doctrine as document-kind — no MWSKZ literals in an MC filter/formula; discriminate at canonical).
- B (contract semantics): richer tax metrics declare canonical tax inputs (tax type, taxable base, recoverable flag), not source codes.
- Temporal semantic: tax POINT / time-of-supply (when tax is recognized) is regime-driven, a selector analogous to the FX rate-date.

DECISION.

T1 — TENANT TAX-REGISTRATION MODEL (Phase 1, near-term). Capture, per legal entity, its tax registrations: a 1:N tenant_dim.tax_registration table keyed to dim_legal_entity, carrying {tax_regime_code (the 'Tax Name': gst/vat/sales_use/…), registration_number (GSTIN/VAT#/EIN/…), jurisdiction_code (country or ISO-3166-2 subdivision), is_default, effective_from/effective_to, soft-delete}. Written via a governed @TenantScoped service (services-only; no raw INSERT). Surfaced in tenant onboarding. This is identity/master data — it unblocks per-registration metric slicing and future compliance outputs, and is independently useful now.

T2 — CANONICAL TAX-TYPE CLASSIFICATION (deferred). Add BCF vocabulary — tax type (output/input × regime component, e.g. output_igst, input_cgst, output_vat), tax jurisdiction, taxable base, recoverable flag — and a tax-code → canonical-tax-type mapping at the OC/CC layer. Metrics then bind the canonical tax type, never the source code. Needed for correct multi-regime tax metrics.

T3 — RICHER TAX METRICS (deferred). On the T2 vocabulary: output-vs-input tax, net-of-recoverable (ITC), effective-tax-by-type, tax-liability. Source-agnostic (B).

T4 — TAX-POINT / TIME-OF-SUPPLY SELECTOR (deferred). A rate-date-style selector (invoice | payment | earlier-of | accrual-vs-cash) driven by (tax regime × metric temporal semantic), for metrics whose value depends on when tax is recognized.

CONFORMANCE (invariants). III: tax registrations are versioned via effective_from/to + soft-delete (history preserved, no in-place rewrite). IV: a metric sliced by registration references it explicitly. VI: canonical tax classification (T2) emits lineage; an unmapped tax code is a loud defect, not a silent skip. I: tax meaning (type, taxable base) is produced at the canonical boundary; metrics declare canonical inputs.

WHAT THIS DOES NOT SOLVE. Rate determination / tax calculation (source's job). Return filing, e-invoicing IRN, VIES validation (compliance products). Exemption-certificate workflow. Withholding tax (TDS/TCS) beyond observing amounts (a separate family if needed).

IMPLEMENTATION. T1 now (this session, behind the Database Change Protocol — the tenant_dim.tax_registration table + Drizzle + governed endpoint). T2–T4 deferred until multi-regime data or richer tax metrics are scheduled. Relationship: parallel to DEC-f6527b/D502 (currency); both are regional/regulatory tenant-semantics that the metric layer must declare, not infer.
