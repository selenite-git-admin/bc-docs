---
uid: DEC-f7d4fc
title: "A tenant's adoption of a source contract is recorded in tenant.tenant_binding; a tenant's overrides of any contract, source included, stay in tenant.contract_binding (DEC-ec9e89)"
description: "Settles the bound-source record (TSK-8376a8): adoption and override are two meanings with one home each; no database change; corrects the D250 mis-citation."
status: proposed
date: 2026-10-02T10:42:48.022Z
project: bc-docs
domain: tenants
subdomain: tenants/contract-binding
focus: governance
---

# A tenant's adoption of a source contract is recorded in tenant.tenant_binding; a tenant's overrides of any contract, source included, stay in tenant.contract_binding (DEC-ec9e89)

## Context

The engine, the live data and the decided ADRs (DEC-ec9e89, DEC-005ea7) all agree once the two meanings are separated. Only the chapter text and a mis-cited D-code disagree. Naming one record per meaning settles the bound-source question with no migration, and keeps DEC-ec9e89's live source overrides.

## Context

Vocabulary slice 4 (defect 6, TSK-8376a8) found two records that both seem to say "this tenant adopted this contract version":
- tenant.tenant_binding (source contract, version, tenant, environment, effective dates);
- tenant.contract_binding (any family, including source, with is_active, override_json and effective dates).

Platform's grounded study (on TSK-8376a8, 2026-10-02) found that the engine and the live data use tenant_binding for source adoption and contract_binding for canonical and metric adoption. No row in contract_binding has family source. The study cited a "D250 unification" intent for contract_binding.

The Architect read the decisions by UID, at bc-docs origin/main:
- D250 is DEC-bae0ef ("IC Simplification"), unrelated to bindings. The citation is wrong.
- The authority for contract_binding is DEC-ec9e89 (D233, implemented): level 3, "Tenant Override (per tenant, per contract), Storage: tenant.contract_binding (override_json + extensions_json)", for every family. For source it names two override cases: drift_detection enforcement (overridable) and fields[] Z-fields (extensible). DEC-0b3c08 (D112) is the earlier master and tenant-override pattern.
- This use is live: bc-core schema-provisioner.repository.ts reads contract_binding.override_json for tenant Z-field mappings (:134, :160-165).
- DEC-005ea7 (implemented) fixes a single production environment: no dev, staging or prod per tenant.

Grounded at bc-core origin/main: tenant_binding is written by TenantBindingPopulatorService (tenant-binding-populator.service.ts:57, upsertTenantBinding) and by reader.repository.ts:453. It is read for source by findActiveSourceBindings (schema-provisioner.repository.ts:92). contract_binding is written by upsertContractBinding (:604, from contract-activation.service.ts) for canonical and metric, and read by findActiveContractBindings (:124).

## Decision

1. **Two meanings, one home each.**
   - **Adoption** (which contract version a tenant uses) and **override** (the tenant's bounded variation of an adopted version, per DEC-ec9e89) are different values.
   - Each has exactly one record per family (DEC-1918d0 rule 4, one source of truth per value).
2. **Source adoption is recorded in tenant.tenant_binding.**
   - A tenant is bound to a source contract version if and only if it has a tenant_binding row for it with effective_to empty.
   - This is the "bound source" record for the onboarding completeness gate (TSK-49f8d8) and for tenant views (TSK-f507fa).
3. **Overrides of every family, source included, are recorded in tenant.contract_binding,** as DEC-ec9e89 decided. A contract_binding row whose family is source is an override of an adopted source version; it never states adoption. No reader treats it as adoption.
4. **Canonical and metric adoption stay in tenant.contract_binding,** as built.
5. **environment_code on tenant_binding carries no decided meaning.** Under DEC-005ea7 there is one production environment, so a reader must not choose a binding by environment. The duplicate environment values seen on 2026-10-02 belong to the env-suffix defect (TSK-330258). Whether the column is retired is a later database decision.
6. **No database change.**
   - contract_binding's family CHECK keeps source, because DEC-ec9e89's source overrides need it.
   - The rule in point 3 is held by a test: no code path reads contract_binding to decide source adoption. A database rule (for example, that a source row must carry an override) is a later option if a second writer appears.

Rejected:
- (A) narrowing contract_binding's CHECK to exclude source: it would forbid DEC-ec9e89's source overrides, a decided and live use.
- (B) moving source adoption into contract_binding with an environment column: no decision mandates the move, and per-environment adoption contradicts DEC-005ea7.

## Foundation gate

- **Location:** C (tenant binding). It names the record that already holds each value; nothing is compensated below.
- **Invariants:**
  - IV, explicit references: adoption is a named record, never inferred from an override row;
  - III: binding rows are ended by effective_to, not rewritten.
- **Design act:** this ADR. The detector is the test in point 6.

## Consequences

- TSK-49f8d8 phase 2 and TSK-f507fa read source adoption from tenant_binding.
- Docs correct tenancy-and-binding.md ("Contract Binding"), which describes one generic artifact for every family, to describe both records and both meanings.
- Platform corrects the bc-core comment in contract-binding.ts ("Replaces tenant_override (D054 Pattern B)") to cite DEC-ec9e89, and adds the point-6 test.
- Vocabulary (slice 4, S4.2): "contract binding" now means a tenant's adoption (canonical, metric) or override (any family) recorded in contract_binding. Source adoption is the "source binding" in tenant_binding.

## Status

Proposed. It becomes decided on the operator's recorded grant.
