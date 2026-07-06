---
uid: DEC-324d9e
title: "Stripe Billing integration — subscription and payment management from day 1"
description: "Stripe handles all payment and billing. Four tiers (Demo/Starter/Professional/Enterprise). No card data in BareCount"
status: decided
subdomain: billing
focus: stripe-integration
date: 2026-03-03
project: bc-admin
domain: tenants
authority: evolving
migrated_from: legacy v2 archive
---


# Stripe Billing integration — subscription and payment management from day 1

## Context

Payment infrastructure must be in place before prospect hunting begins. Stripe is the industry standard for B2B SaaS billing — handles PCI compliance, supports INR + international currencies, has Indian entity, and provides subscription management out of the box. ~5-6 days integration effort for a fully functional billing system. Zero pain for revenue recovery from day 1.

## Decision

BareCount uses Stripe Billing as the payment and subscription management platform. Four subscription tiers: Demo (free 14-day trial), Starter (AWS Shared, monthly/annual, self-service), Professional (AWS Shared or Separate, annual, self-service or sales-assisted), Enterprise (BYO-DB or BC-Agent, custom pricing, sales-led with invoice billing). Stripe handles: payment collection (Checkout), recurring billing (Subscriptions), self-service portal (Customer Portal), and enterprise invoicing (Stripe Invoicing). bc-core integrates via Stripe SDK + webhooks for payment event processing. bc-admin gets a Subscription menu group with Plans and Pricing, Tenant Billing, Onboarding, and Revenue pages. No card/payment data stored in BareCount systems — Stripe is the merchant processor.

## Options Considered

N/A

## Consequences

N/A
