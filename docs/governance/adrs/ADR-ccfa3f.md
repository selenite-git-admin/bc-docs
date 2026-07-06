---
uid: DEC-ccfa3f
title: "SFDC flavor fixes — drop ar-invoice-item→OpportunityLineItem, flag material-master rename"
description: "Drop incorrect ar-invoice-item→OpportunityLineItem mapping (category error), flag material-master-reader for rename to product-master-reader."
status: implemented
subdomain: readers-and-flavors
focus: one-time-flavor-cleanup
date: 2026-03-08
project: platform
domain: readers
authority: authoritative
migrated_from: legacy v2 archive
---


# SFDC flavor fixes — drop ar-invoice-item→OpportunityLineItem, flag material-master rename

## Context

Stress-tested all proposed SFDC readers against HubSpot, Dynamics 365, Zoho CRM, Pipedrive, Freshsales. 14/17 sustain neutrality perfectly. 3 issues found and addressed.

## Decision

1. DROP ar-invoice-item-reader → OpportunityLineItem mapping. OpportunityLineItem is a sales pipeline line item (pre-sale), not an AR invoice item (post-sale, finance). Category error. Entity catalog needs correction. OpportunityLineItem stays in source catalog but gets no reader flavor until opportunity-line-item-reader is created.

2. FLAG material-master-reader for rename to product-master-reader. "Material master" is SAP jargon. Every CRM calls this "Product." Rename is cross-cutting (affects SAP, SFDC, Zoho, Tally flavors) — deferred to dedicated task.

3. ACCEPT campaign-member-reader as-is. Business concept (campaign participation) is valid cross-CRM. Flavor handles source-specific mapping.

## Options Considered

N/A

## Consequences

N/A
