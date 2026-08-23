---
uid: DEC-683cf3
title: "Business Object tiers — basic (business events) vs derived (accounting artifacts)"
description: "BOs classified via tier_code: basic (real business events like invoices) vs derived (computed artifacts like GL entries from basic BOs)."
status: implemented
subdomain: business-object-model
focus: schema
date: 2026-03-23
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Business Object tiers — basic (business events) vs derived (accounting artifacts)

## Context

Module-centric modeling (GL Journal Entry, AP Invoice, AR Invoice as separate canonical objects) creates N COs for one business event — metrics must then understand all variants. Business-level modeling (Customer Invoice) creates one CO regardless of source — metrics consume a single shape. This aligns with the patent's "system-independent structure dictated by the business domain, not by source system quirks."

## Decision

Business Objects are classified into two tiers via tier_code CHECK constraint:

basic — fundamental business events and master data that represent what the business actually does. Examples: Customer Invoice, Vendor Invoice, Customer Payment, Vendor Payment, Purchase Order, Sales Order, Goods Receipt, Customer, Vendor, Material, Employee.

derived — objects computed from basic objects, typically accounting artifacts or aggregated views. Examples: GL Journal Entry, Trial Balance, Aging Report, Bank Reconciliation, Period Close. Derived objects declare their basic inputs via business_object_relation (derives_from edges).

Key insight: GL Journal Entry is NOT a basic business object — it is a derived accounting record produced when business events (invoices, payments) are posted. The Canonical Object for "Customer Invoice" should contain the business facts, not how the GL posted it. This prevents module-centric modeling (AP Invoice, AR Invoice, GL Journal as separate objects for the same business event).

Canonical evaluation resolves to basic BOs (source-independent). Derived BOs are produced downstream via accounting rules, not at the admission boundary.

## Options Considered

N/A

## Consequences

N/A
