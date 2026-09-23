---
uid: DEC-ea4523
title: "Canonical fiscal resolver must be source-agnostic: derive fiscal period from declared posting-date + resolved legal-entity calendar; delete the bukrs/'*' literal; dereference source m2o FKs"
description: "Companion to DEC-a57eb8/D622. The canonical fiscal resolver derives the reporting fiscal period source-agnostically (declared posting-date field + resolved per-LE calendar, fail-closed), with no SAP bukrs literal and no '*' fallback; source m2o code FKs are dereferenced at the reader boundary."
status: decided
date: 2026-09-23T14:17:27.358Z
project: bc-core
domain: contracts
subdomain: canonical-resolver/fiscal
focus: infrastructure
---

# Canonical fiscal resolver must be source-agnostic: derive fiscal period from declared posting-date + resolved legal-entity calendar; delete the bukrs/'*' literal; dereference source m2o FKs

## Context

No rationale recorded.

## Decision

Companion to DEC-a57eb8 (D622); a hard prerequisite of D622 decision-point 2 (fiscal period is a derived dimension). The canonical fiscal resolver must derive the reporting fiscal period SOURCE-AGNOSTICALLY. (1) enrichFiscal (bc-core/src/boundary/ccv2-canonical-resolver.service.ts) currently reads `resolvedLegalEntity ?? String(row['bukrs'] ?? '*')` — DELETE the SAP `bukrs` literal and the `'*'` silent fallback; derive strictly from the CC's declared posting_date_field + the resolved legal entity's per-LE fiscal calendar (DEC-a8e8fc/D365, DEC-d7e7a0/D364); FAIL-CLOSED (rejectGroup) when the per-LE calendar is missing, never a `'*'` fallback. (2) The CC declares the legal-entity field (mirroring posting_date_field) so the resolver reads it source-agnostically rather than a SAP column name. (3) Source many-to-one / reference FKs that carry codes (Odoo company_id, currency_id — INTEGER many2one) must be dereferenced to their codes at the reader/observation boundary; integer FKs are not codes, and the `direct`/`code_lookup` transforms do not dereference an m2o. (4) Declaring the per-LE fiscal calendar is mandatory + blocking at onboarding (D622 decision 2). SAP backward-compat: CCs without a declared legal-entity field keep the legacy bukrs path ONLY during migration, with the `'*'` fallback removed. ACCEPTANCE: a RUNTIME proof — an actual CO with a correct fiscal period on a non-SAP (Odoo) source — not a dry-run. Design memo of record (promote): bc-core artifacts DESIGN-fiscal-source-agnostic-and-m2o-code-2026-08-16.md. Foundation: source-agnosticism (a resolver reading a SAP column name is a source-literal contamination point); Invariant I (meaning derived at the canonical boundary from declared inputs, not a hard-coded source field).
