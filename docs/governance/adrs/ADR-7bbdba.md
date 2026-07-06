---
uid: DEC-7bbdba
title: "4-Level KPI Taxonomy: Industry Category → Industry → Business Function → Business Sub-function"
description: "KPIs classified by 4 levels: industry category (~9), industry (~21), business function (19), sub-function. Enterprise KPIs use industry=universal."
status: implemented
subdomain: taxonomy
focus: 4-level-kpi-taxonomy
date: 2026-03-20
project: bc-infra
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# 4-Level KPI Taxonomy: Industry Category → Industry → Business Function → Business Sub-function

## Context

domain/subdomain are ambiguous terms. Business Function/Sub-function maps to how enterprises organize. 4 levels enable: (a) industry-aware KPI suggestions during tenant onboarding, (b) two navigation axes in bc-admin (by industry OR by business function), (c) package binding to business functions not industries. Rename deferred per Option B — finish seed first, rename is mechanical next session.

## Decision

KPI/metric definitions use a 4-level hierarchy: (1) Industry Category (master_industry_category) — sector grouping (~9: universal, financial_services, manufacturing, services, infrastructure, commerce, logistics, primary, public_sector), (2) Industry (master_industry) — specific vertical (~21: banking, automotive, pharma, etc.), (3) Business Function (master_domain today, rename to master_function later) — what the department does (19: finance, hr, sales, operations, etc.), (4) Business Sub-function (master_subdomain today, rename to master_subfunction later) — specific area (AP, AR, GL, etc.). Enterprise KPIs live at industry=universal. Industry KPIs carry their specific industry_code. Column rename from domain_code→function_code and subdomain_code→subfunction_code is deferred to a dedicated session to avoid mid-seed disruption.

## Options Considered

N/A

## Consequences

N/A
