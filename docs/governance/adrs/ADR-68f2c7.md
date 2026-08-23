---
uid: DEC-68f2c7
title: "company_code is a shared dimension BF (5th D292 exception)"
description: "Adds company_code as 5th shared BF exception to D292. Updates bf-bo-onboarding-sop shared list from 4 to 5."
status: implemented
subdomain: business-vocabulary
focus: shared-dimensions
date: 2026-04-07T09:40:59.162Z
project: platform
domain: contracts
migrated_from: legacy v2 archive
---

# company_code is a shared dimension BF (5th D292 exception)

## Context

Gemini cross-audit (SES-cf6410) found that chain-mapping-requirements.md and mc-creation-sop.md treat company_code as shared, but bf-bo-onboarding-sop.md (locked) only lists 4 shared dims. company_code appears in every BO's grain and must match across COs for metric evaluation. BO-scoping it (ar_receivable_hdr_company_code vs billing_document_hdr_company_code) would break cross-BO grain matching in MC co_bindings.

## Decision

Add company_code to the D292 shared BF exception list, making 5 shared dimensions: company_code, currency_code, language_code, country_code, unit_of_measure. These BFs are NOT BO-scoped because they are universal grain keys used identically across all BOs. This enables the metric engine to match grain keys across COs from different BOs (e.g., company_code from AR CC matches company_code from Billing CC in the DSO metric).
