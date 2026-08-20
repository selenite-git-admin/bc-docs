---
uid: DEC-64ad7c
title: "Company-scoped canonical party names for cross-company duplicates (supersedes shared party master)"
description: "Drop the shared-party master; a party trading with >1 group company stays as SEPARATE per-company records with the canonical name (no ' 2' suffix). Simpler, no economic change. Resolves QA-024/061."
status: decided
date: 2026-08-20T06:44:21.320Z
project: bc-synth
domain: sources
subdomain: demo-estate/party-identity
focus: identity
supersedes: DEC-e4eb7c
---

# Company-scoped canonical party names for cross-company duplicates (supersedes shared party master)

## Context

DEC-e4eb7c chose the shared-party master as the maximal-realism option (one identity for a party trading with multiple group companies, realized as a shared commercial entity + per-GST-registration child contacts). Scoping the implementation showed it is operationally complex and economically risky: it restructures the roster, changes cross-company transaction binding, touches the immutable join-key registry, and — critically — the ' 2' twins carry ~0.9 of total revenue weight, so merging them shifts the economic calibration and can only be validated by a full rebuild. The demo does not claim a specific realism percentage, so that complexity is not warranted (operator, 2026-08-20: 'if it is operationally complex then drop the idea ... we are not claiming % realism'). The company-scoped canonical-name fix clears the actual visible defect (the ' 2' suffix) with NO economic change and minimal governance (id retire + fresh-allocate), keeps the customer pool the same size, and stays within the join-key contract via tombstone rather than in-place rename (which is what made the earlier F1 attempt a violation). Lower consequence, lower risk, satisfies the acceptance tests.

## Decision

A customer or vendor that transacts with more than one of the Kaveri group's three companies (KPC/KFF/KTW) is kept as SEPARATE per-company partner records — one per company relationship — each carrying the party's CANONICAL name with NO numeric dedupe suffix. Odoo permits duplicate partner names across different companies (company-scoped), so 'Deccan Motors' under KPC and 'Deccan Motors' under KFF coexist cleanly without the 'Deccan Motors 2' artifact. The join key stays company|name (unique per company).

Realization in the v2rc8 roster re-authoring: the 23 customer + 12 vendor ' 2' twin entries are renamed to their canonical name; because the (id, company, name) binding is frozen (join-key successor-5, Inv III), the twin ids are governed-RETIRED via append-only journal tombstone and FRESH ids allocated for the canonical-named entries. NO shared commercial entity, NO cross-company partner merge, NO per-GST child-contact restructure, and NO economic change — the same transactions, revenue weights, and company assignments carry over; only the display name changes.

Supersedes DEC-e4eb7c (multi-company shared party master). Resolves QA-024 (no numeric dedupe suffix) and QA-061 (vendor consistent across card/form/report/receipt/bill/ledger).
