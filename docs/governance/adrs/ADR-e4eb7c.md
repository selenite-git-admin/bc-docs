---
uid: DEC-e4eb7c
title: "Multi-company shared party master for the demo group (join-key identity successor-6)"
description: "Kaveri demo group's 3 companies share ONE party master; a party trading with >1 company is one CUST/VEND id, no ' 2' suffix (resolves QA-024/061)."
status: superseded
superseded_by: DEC-64ad7c
date: 2026-08-20T02:46:38.939Z
project: bc-synth
domain: sources
subdomain: demo-estate/party-identity
focus: identity
---

> **SUPERSEDED by DEC-64ad7c (2026-08-20):** the shared party master proved operationally complex and
> economically risky (the ' 2' twins carry ~0.9 of revenue weight; merging shifts the calibration). The demo
> does not claim a realism percentage, so the simpler company-scoped canonical-name fix was adopted instead —
> keep the twins as separate per-company records with the canonical name (no ' 2'), retire the old ids +
> fresh-allocate. No shared entity, no economic change. See ADR-64ad7c.

# Multi-company shared party master for the demo group (join-key identity successor-6)

## Context

The ' 2' suffix is a name-uniqueness artifact, not a duplicate or a mislabel: 23 customers and 12 vendors that trade with more than one of the three group companies were authored as one partner PER company, and the second name collision got ' 2' appended. Base and twin differ only in company-scoped context (company, city, GSTIN, state, currency, credit) — they are the same external brand. A real corporate group runs a SHARED customer/vendor master, so customer-level metrics (DSO, credit exposure, on-time delivery) consolidate correctly across the group's companies; a per-company partner split would fragment those metrics and surface a fake 'Deccan Motors 2' in customer-facing screens (the QA-024 defect). An in-place rename of the twin is barred by Invariant III (the (id, company, name) binding is immutable — successor-5 J-S3); retire+fresh-allocate of the duplicate ids preserves the append-only registry journal and cross-system join stability (D538 stable join keys). The parent + per-GST-registration child-contact realization is the realistic Odoo India model for a party registered in multiple states, and aligns with D574 legal-entity source binding (one shared party projects a single identity across the group's legal entities). Operator decision 2026-08-20: shared party master (over company-scoped-same-name and distinct-names alternatives).

## Decision

The Kaveri demo group's three companies (KPC = Kaveri Precision Components, Pune/MH; KFF = Kaveri Forge & Fabrication, Chennai/TN; KTW, Bengaluru/KA) SHARE ONE party master. A customer or vendor that transacts with more than one group company is a SINGLE logical party bound to ONE stable join key (CUST-#### / VEND-####), authored once with its canonical name and NO uniqueness suffix.

Odoo realization: the shared party is a commercial entity (parent res.partner, group-shared / company_id NULL) with per-GST-registration child contacts — one child per state/GSTIN where the party is registered — all sharing commercial_partner_id. Group companies transact with the appropriate registration child; per-company commercial context (payment term, receivable/payable account, credit limit, currency, export flag) is carried as company-scoped property_* on the shared partner or on the relevant child, NOT as a second top-level partner.

Immutability handling: this does NOT introduce a mutable display label (it supersedes-in-approach the successor-5 stance 'there is no separate mutable display name' by making the fix a single shared IDENTITY, not a label). The frozen (id, company, name) binding stays immutable per surviving id. The spurious per-company duplicate ids created by the ' 2' name-collision hack are GOVERNED-RETIRED via append-only journal tombstone (never renamed in place, never id-reused); the surviving canonical party keeps its id. In the fresh v2rc8 mint the roster generator emits each real party once, so no ' 2' entity is ever allocated.

Scope: ~23 customer and ~12 vendor ' 2' entities collapse into their canonical party. Resolves QA-024 (customer names carry a duplicate-load ' 2' suffix) and QA-061 (RFQ shows 'X 2' while the vendor form field is blank). This is the Lane C design successor (JOIN-KEY-IDENTITY-DESIGN.md successor-6) and must land BEFORE the Lane A generator batches touch sale.order/purchase.order partner bindings.
