---
uid: DEC-f4e9a0
title: "Customer Invoice identity = composite {Legal Entity (ref), document number, document fiscal year}; introduce Legal Entity entity"
description: "The CO business identity (grain) of a Customer Invoice is a system-agnostic composite: issuing Legal Entity (identity-bearing reference), document number, and source-attested document fiscal year. Introduces the missing Legal Entity entity. Prerequisite to DEC-acce2b."
status: implemented
date: 2026-07-02T06:43:08.365Z
project: bc-core
domain: contracts
subdomain: concept-registry/identity
focus: identity
---

# Customer Invoice identity = composite {Legal Entity (ref), document number, document fiscal year}; introduce Legal Entity entity

## Context

The invoice identity must be declared (Location B) so the canonical resolver reads it rather than inventing a composite (forbidden Invariant-I compensation). Modeling the issuing organization as a referenced Legal Entity — not a SAP-BUKRS value characteristic — is what the BCF system-agnosticism doctrine and the parked company-code panel both point to, and it stands up the organizational backbone the fiscal calendar and every finance document already assume but which is absent from the 133-entity substrate. The year component is empirically required (belnr recycles per fiscal year: 1162 vs 1716) and is modeled as source-attested document fiscal year, kept strictly distinct from the resolver-stamped reporting fiscal_year per the fiscal-time §11.6 boundary.

## Context (grounded 2026-07-02, SES-4b4210)

Building the CC-v2 canonical resolver (DEC-acce2b) surfaced a Foundation-gate halt: the Customer Invoice's canonical identity is under-specified. Grounded study established:

- **Object-model doctrine:** a Source Object is identified by *source business keys* (SAP `bukrs`/`belnr`/`gjahr` — legitimate, source-shaped at the SO layer); a Canonical Object is identified by *business identity keys* — the CC `grain[]`, which must be system-agnostic (`foundation/the-object-model.md`; N:1 SO→CO per DEC-97bb94). Identity belongs in `grain[]`, NOT in ad-hoc `business_concept.identity_role` flips.
- **Empirical (tbc_pilot1_dev.fact.so_bsad, 1716 rows):** `(bukrs,belnr,gjahr)` distinct = 1716, `(bukrs,belnr)` = 1162, `belnr` alone = 530. `belnr` recycles across fiscal years within a company code, so a year discriminator is REQUIRED; `(org, document_number)` alone collapses 554 distinct invoices. Generalizes: SAP/Oracle recycle document numbers per period; globally-unique-ID systems (NetSuite) make the year redundant-but-harmless — the composite is robust across sources.
- **BCF doctrine (business-concept-registry-vocabulary-evidence-framework §11.1/§6):** platform vocabulary is system-agnostic; an organization is an *entity* (ISO 20022 organisation, FIBO legal entity, LEI), not a SAP-`BUKRS`-derived value characteristic. "No global-by-accident": System-Specific candidates cannot be APPROVE (this is why an SAP-only `company code` characteristic correctly parked).
- **Fiscal-time doctrine (fiscal-time-and-temporal-gates §11.6):** the resolver-stamped reporting `fiscal_year` is Layer A — owned by canonical resolution + tenant calendar, NEVER a BCF concept (category error). A source-attested year (SAP `GJAHR`) is a distinct, source-path value. The fiscal calendar is configured *per legal entity*.
- **Substrate gap:** among 133 active `concept_registry.entity` rows there is NO Legal Entity / Company / Organization entity. The organization `BUKRS` represents — the issuer of every invoice and the anchor the fiscal calendar keys on — is unmodeled.

## Decision (proposed — design lock)

The canonical (CO) identity of a **Customer Invoice** is the system-agnostic composite of three identity-bearing components, declared in the Canonical Contract `grain[]`:

1. **Issuing organization** — an identity-bearing **reference edge** from Customer Invoice to a new **Legal Entity** entity. Source carrier: SAP `BUKRS` (Oracle ledger/LE, NetSuite subsidiary in other systems). Modeled as a referenced entity, never a source-field-derived value characteristic.
2. **Document number** — the existing identity-bearing value concept (`2887850a`, source carrier `BELNR`).
3. **Document fiscal year** — a NEW identity-bearing, **source-attested** value concept (source carrier `GJAHR`). It is the year the document is assigned to *in the source ledger* — a component of the document's identity. It is explicitly DISTINCT from the resolver-stamped reporting `fiscal_year` (§11.6 Layer A). Naming discipline: `document fiscal year` / `accounting document year` with a source-attestation marker — NEVER bare `fiscal year` (which would collide with the resolver concept and invite cross-layer drift).

**Introduce the Legal Entity entity** as a foundational, system-agnostic entity with its own declared identity (a `legal entity identifier` value concept; `company code` is a source-attested alias/carrier, not the identity's name). It is the organizational backbone the platform is currently missing and that fiscal-time (per-legal-entity calendar), multi-entity groups, and every finance document require.

**SO layer is unchanged:** Source Objects keep their source business keys (`bukrs`,`belnr`,`gjahr`); the composite is the CO/grain business identity that those SO keys map to at canonical evaluation.

## Repair-location & Foundation

- **Location B (contract grammar / BCF entity + CC grain).** The correct upper-layer fix: declare the identity where meaning is owned. Keying the resolver on a composite WITHOUT declaring it (the tempting D-layer move) is forbidden compensation (Invariant I) — this ADR removes that temptation by fixing B first.
- **Invariant IV (references explicit):** the issuing-organization reference + the two value identity concepts are explicit declared references; the resolver reads declared identity, infers nothing.
- **Invariant II (ordering fixed):** SO → CO composition follows the declared grain identity.
- **Invariant I (meaning at its boundary):** invoice identity is produced at BCF/CC declaration, not invented at the evaluation boundary.

## Governance / route discipline

All artifacts authored via governed routes ONLY: entities + concepts via the BCF authoring panel (`POST /api/bcf/registry-authoring-runs` → publication/confirm; operator-adjudication where a panel parks on Maker/Checker disagreement); CC/OC versions via the contract-version APIs. No raw substrate inserts. Legal Entity + the two identity concepts require system-agnostic T2/T3 evidence (ISO 20022 / FIBO / LEI for the organization; cross-ERP posting-year for the document fiscal year) — SAP is T4 carrier evidence only.

## Consequences

Prerequisite to DEC-acce2b (CC-v2 resolver). Implementation order: (1) author Legal Entity entity + its identity concept; (2) author the Customer Invoice → Legal Entity identity-bearing reference; (3) author `document fiscal year` identity concept; (4) bump arpi_slice CC to a composite `grain[]` (v9) + OC maps `BUKRS`→legal-entity-ref, `GJAHR`→document_fiscal_year; (5) build DEC-acce2b keyed on the declared composite → 1716 correct invoice COs. The same identity pattern applies to Supplier Invoice (whose current `grain=posting_date` is separately flagged as mis-specified).
