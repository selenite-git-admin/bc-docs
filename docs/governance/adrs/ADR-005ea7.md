---
uid: DEC-005ea7
title: "Single production environment — no dev/staging/prod per tenant"
description: "BareCount operates one production environment per tenant. No environment tiers. Trial = real tenant, delete-and-recreate on purchase."
status: implemented
subdomain: tenant-lifecycle
focus: environment-model
date: 2026-03-16
project: platform
domain: tenants
refs:
  - type: decision
    uid: DEC-1918d0
    label: "D162: Deployment & Database Architecture"
  - type: decision
    uid: DEC-0b3c08
    label: "D112/D053: Master/Tenant-Override contract pattern"
authority: authoritative
migrated_from: legacy v2 archive
---

# Single Production Environment

## Context

Enterprise data platforms typically offer dev/staging/prod environments per tenant. This adds significant complexity: environment promotion workflows, per-environment contract versioning, environment-aware UI, and a `tenant_bindings` table tracking which contract version runs in which environment for which tenant.

At BareCount's stage (pre-launch, zero tenants), this complexity has zero customer value and high engineering cost.

## Decision

BareCount operates a **single production environment** per tenant. No dev/staging/prod tiers.

### Trial Strategy

If a customer wants to trial with their SAP quality server, we treat it as a production tenant. The customer tests, decides, and either converts or we delete the account. If they buy, they start fresh — new account, new setup. Having been tested with quality data, no migration is required.

We actively discourage non-production environments.

### Implications

1. **`tenant_bindings` table retired** — it existed to track "which contract version in which environment." Without environments, it has no purpose.
2. **No environment badges, selectors, or filtering** in bc-admin or bc-portal.
3. **No "promote to prod" workflows.**
4. **Tenant-contract relationship** fully described by:
   - `contract.tenant_id` — Pattern A instances (source, admission, mapping) belong to tenant directly
   - `tenant_override` — Pattern B customizations (thresholds, alerts, schedule)
   - Both derived from source selection + onboarding, not manual binding
5. **Contract scoping model (D053/D054) unchanged** — Patterns A, B, C still apply.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Single production (chosen)** | Simple, fast to build, no environment sprawl | Customers can't test in isolation |
| Dev/staging/prod per tenant | Enterprise-expected, safe testing | Massive complexity, tenant_bindings table, promotion workflows, environment-aware UI |
| Shared staging + per-tenant prod | Compromise | Still needs promotion workflow |

## Consequences

1. **Engineering simplification** — no environment dimension in any table, API, or UI
2. **Trial is a real tenant** — customer gets authentic experience
3. **Delete-and-recreate on purchase** — clean start, no migration debt
4. **Future:** if enterprise customers demand environments, it's an additive feature, not a retrofit
