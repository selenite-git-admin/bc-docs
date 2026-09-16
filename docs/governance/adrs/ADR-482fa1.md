---
uid: DEC-482fa1
title: "BYO-DB portability boundary — defer the flow, hold the engine-portability invariant"
description: "The detailed BYO-DB onboarding flow is deferred until a concrete customer drives its specifics; the current AWS-Shared provisioning stays as v1. In the meantime a load-bearing invariant is enforced: no spine or provisioning unit may bake in a BareCount-hosting assumption, so BYO-DB remains an additive later unit and not a rework."
status: proposed
subdomain: tenant-topology
focus: byo-db-portability
date: 2026-09-16
project: platform
domain: tenants
refs:
  - type: decision
    uid: DEC-1918d0
    label: "Deployment and database architecture — engine-portable plain PostgreSQL spine"
  - type: decision
    uid: DEC-324d9e
    label: "Hosting tiers — AWS-Shared is v1; BYO-DB / BC-Agent / AWS-Separate held"
  - type: decision
    uid: DEC-a67518
    label: "Tenant onboarding gate — the checklist-readiness gate the BYO-DB variant will require"
---

# BYO-DB portability boundary — defer the flow, hold the engine-portability invariant

## Context

The BYO-DB *posture* is already decided (W2 entry, D5): BYO-DB is a **custody variant** — the tenant database is treated backup-first, with a light forward-only upgrade path, and from-scratch parity is not required for tenant databases. The hosting tiers are fixed (DEC-324d9e): **AWS-Shared is the v1 tier**, and BYO-DB, BC-Agent and AWS-Separate flows are held; the tenant-onboarding design targets AWS-Shared only in its first version.

What is *not* designed is the detailed **BYO-DB onboarding flow**: how the platform reaches and authenticates to a customer-owned database, the credential-custody split, the DEC-a67518 checklist-readiness gate for the variant, the backup/recovery responsibility split, and the network/security posture. These specifics depend on a concrete customer's environment.

Two facts make deferral safe:

1. **The current provisioning works and is the intended v1.** BareCount-hosted (AWS-Shared) tenants provision end-to-end today via `POST /tenants`. No customer is on BYO-DB, so nothing is blocked by the flow being absent.
2. **The spine is already engine-portable by design.** Per DEC-1918d0 / ADR-b1a286 the platform and tenant spine target plain PostgreSQL 17.x with no hosting-specific assumptions — the runner, forward migrations, tenant ledger, backup/recovery and the tenant skeleton all operate against any conforming PG instance. BYO-DB was always intended to be an **additive** later unit, not a rework.

The risk of waiting is therefore not architectural rework — it is *silent erosion*: a future spine or provisioning unit could quietly bake in a BareCount-hosting assumption and make BYO-DB expensive later, without anyone deciding to. This ADR closes that risk with an enforceable invariant.

## Decision

1. **Defer the detailed BYO-DB onboarding flow** until a concrete BYO-DB customer or commitment drives its specifics. Keep the current **AWS-Shared / BareCount-hosted** provisioning as v1; BYO-DB, BC-Agent and AWS-Separate flows remain held. This ADR does **not** design the flow.

2. **Hold the portability invariant (load-bearing).** No spine or provisioning unit may bake in a **BareCount-hosting assumption**. The tenant-database spine — canonical/skeleton baseline, the forward-only runner, migrations, the tenant migration ledger, and backup/recovery — **must remain applicable to any conforming PostgreSQL 17.x instance regardless of who hosts it**. Concretely, a unit violates the invariant if it:
   - resolves connection or credentials on the spine/apply path in a way that only a BareCount-owned instance can satisfy (hosting-specific resolution belongs in the provisioning/deployment layer, not the spine);
   - makes correctness depend on **from-scratch parity for a tenant database** (dropped for tenant DBs by the D5 posture — tenant DBs are backup-first + forward-only);
   - assumes BareCount owns or exclusively controls the instance in backup/recovery mechanics (e.g. cluster-global operations a customer would not grant), rather than degrading to the tenant-database-scoped, customer-grantable form;
   - assumes BareCount-specific network, tablespace, superuser, or filesystem topology on the tenant-DB path.

   A unit that needs any such assumption must either avoid it or propose an explicit amendment to this decision — it may not introduce it by default.

## Enforcement

Future tenant-DB spine and provisioning units are reviewed against this invariant at their exact head (the standard builder–auditor review). This ADR is the reference a reviewer cites to refuse a hosting assumption that arrives without an amendment. It adds no code and no gate; it is a review-time boundary.

## Not decided here

- The BYO-DB onboarding flow itself — connection reachability, credential custody, the checklist-readiness gate mechanics (DEC-a67518), the backup/recovery responsibility split, and the network/security posture. All deferred to the driving-customer design.
- AWS-Separate and BC-Agent variants (BC-Agent is separately deferred, DEC-66d3ca).
- Anything requiring cloud budget or a live/production action.

## Consequences

1. BYO-DB stays an **additive later unit**, entered when a real requirement exists — not a speculative design now and not a rework later.
2. Deferral cannot silently erode BYO-DB-readiness: the invariant is enforceable at review, so a hosting assumption cannot slip in undecided.
3. The AWS-Shared tier remains the working v1; no current provisioning changes.
