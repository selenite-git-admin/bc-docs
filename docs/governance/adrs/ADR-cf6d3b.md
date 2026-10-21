---
uid: DEC-cf6d3b
title: "Tenant Activation model: active = verified admin + assigned subscription; Activation/Onboarding plane split"
description: "Declares the meaning of tenant `active` as Activation-complete (verified Cognito admin + assigned subscription); splits the bundled Tenant Onboarding SOP into a platform Activation plane and a tenant Onboarding plane; re-scopes the deferred bc-db 0034 activation-gate verdict to the Activation plane."
status: proposed
date: 2026-10-21
project: platform
domain: tenants
subdomain: tenant-topology/activation
focus: activation-model
amends: DEC-7df811
authority: authoritative
refs:
  - type: decision
    uid: DEC-7df811
    label: "Tenant onboarding state model and isolation model (amended: §1 subscription deferral lifted, §3 status endorses onboarding_incomplete)"
  - type: decision
    uid: DEC-42b9c0
    label: "Admin-provisioned users only (no self-signup) — the tenant-admin provisioning act"
  - type: decision
    uid: DEC-324d9e
    label: "Stripe Billing; four subscription tiers — the future commercial authority the Pre Launch Exclusive offer is interim to"
  - type: doc
    label: "operating-model/tenant-entitlement-enforcement.md — the authoritative Subscription governance-record design (one-per-active-tenant; catalog-entitlement incl. metrics; all surfaces 'Not yet wired')"
  - type: decision
    uid: DEC-103acb
    label: "D504-C — onboarding_incomplete state origin"
  - type: decision
    uid: DEC-4aa1ff
    label: "Canonical legal-entity identity — LE declaration is a tenant-app (Onboarding-plane) act after the platform shell + admin exist (operator grant 2026-10-20T11-09-28-199Z-11867ed1)"
  - type: decision
    uid: DEC-c48b0f
    label: "Design act vs execution act — this ADR is a design act (a declaration)"
  - type: task
    uid: TSK-49f8d8
    label: "Architect: served PATCH may only suspend; 0034 activation gate authored"
  - type: task
    uid: TSK-b8981d
    label: "Operator-locked Activation vs Onboarding vocabulary alignment (this ADR formalizes it)"
---

# Tenant Activation model: active = verified admin + assigned subscription; Activation/Onboarding plane split

## Context

The platform today has a single governed operation — "Tenant Onboarding" — that bundles two things the operator wants kept distinct: bringing a tenant *into existence as an operable container* (a platform act), and *flowing the tenant's own data through the chain to a first Metric Snapshot* (a tenant act). The operator has locked a two-plane model — **Tenant Activation** (platform) and **Tenant Onboarding** (tenant) — and wants a clean fixture tenant created through the Activation flow to re-establish the LC5 oracle. This ADR formalizes that model as a design act (DEC-c48b0f): it declares what an `active` tenant *means*. It is design-only and authorizes no DDL and no code.

Grounded at `origin/main` (bc-core `689dd240`, bc-db `49fb73cd`), the as-built state is:

1. **`active` has no declared meaning.** `TenantManagementRepository.completeProvisioning(...)` flips a newborn straight to `active` at the end of the governed birth act (`TenantBirthService`), gated only by the birth postconditions (catalog digest, ownership, runtime verification). Nothing ties `active` to a real admin user or to a subscription. (The `UpdateTenantDto` comment describes a "completeness gate + verdict"; that is the *intended* invariant from `TSK-49f8d8`, not current enforcement — see point 4.)
2. **The Subscription is authoritatively designed but not instantiated; the catalog is a bare, un-wired reader-tier table.** The operating-model chapter `tenant-entitlement-enforcement.md` (authoritative) defines the **Subscription** as the platform-scoped governance record that holds tenant entitlement: *"each active tenant identity references exactly one Subscription record at a time"*, its **catalog-entitlement** axis is a reference set of entitled process chains / functions / subfunctions / **metrics** / Source Systems, and *"a tenant identity without a referenced Subscription record cannot proceed past Connection registration — the same outcome as a terminated state."* That chapter's Wiring Status declares **every** enforcement surface **"Not yet wired"** in the current release. Grounding confirms the record is **designed, not built**: the physical `tenant` schema has only `tenants / tenant_binding / contract_binding / tenant_infrastructure` — **no Subscription table**, consistent with `ADR-7df811 §1` deferring it. The only catalog that exists is `pricing.package` (D086; Drizzle `subscriptionPackage`) — a *platform-level, tenant-agnostic reader-tier* table whose payload is readers (`reader_manifest_json`), not metrics; it is un-wired (no module imports `PackageService`). There is **no** tenant↔Subscription link, **no** catalog-entitlement-of-metrics representation, and **no** per-tenant metric-allowance. So "all metrics allowed" is the *trivial current behavior* — nothing restricts metrics per tenant today. (The nearest per-tenant metric surface is `tenant.contract_binding`, a metric-*contract* overlay / version pin, not an allow-list.)
3. **Admin provisioning exists.** `DEC-42b9c0` (admin-provisioned users only; no self-signup) now has its API: `POST /admin/users` (`UserProvisioningController`, `PlatformOnly` + `platform_admin`) → `CognitoAdminService.createUser` stamps `custom:tenant_id` + `custom:roles` and Cognito emails the temp-password invitation. First login runs the `FORCE_CHANGE_PASSWORD` flow; completing it moves the Cognito `UserStatus` to `CONFIRMED`.
4. **The activation-gate substrate already exists, deferred.** bc-db migration `0034_onboarding_completeness_result` (DEFERRED / unapplied) creates the append-only `tenant.onboarding_completeness_result` verdict table, the `trg_tenants_activation_gate` trigger (refuses an `UPDATE` *into* `active` unless the newest verdict is `complete`), and a new `onboarding_incomplete` tenant status. Its verdict `unmet_code` vocabulary is `{no_legal_entity, no_fiscal_calendar, unresolved_source_binding}` — all **data / Onboarding-plane** concerns. 0034 is deferred precisely because its paired bc-core consumer (completeProvisioning emitting the verdict; a newborn resting at `onboarding_incomplete`) is not wired. (Citation note: 0034's header cites the `D622/D623` *nicknames*; those nicknames do not resolve to tenant-activation-prerequisite ADRs at the bc-docs base, so this ADR does not inherit them — the authority for re-scoping 0034 is `TSK-49f8d8` plus the operator-locked model, and `DEC-103acb` for the `onboarding_incomplete` state.)

The tension point 4 exposes is the heart of this ADR: a gate that blocks `active` on *data* readiness contradicts the operator's lock that a tenant is Activated as an **empty-but-active bound container**, with data onboarding happening *after* `active`.

## Decision

The bundled operation is split into two distinctly-named, strictly-sequenced planes, and the meaning of `active` is declared.

### A. Tenant Activation (platform plane)

Through governed platform acts, the platform operator:

1. **Creates the tenant identity** — UUID + display name + unique slug + database-per-tenant — via the governed birth act (`TenantBirthService` → `completeProvisioning`), unchanged in mechanism.
2. **Assigns a subscription** — in the interim a **"Pre Launch Exclusive"** package denoting *all-metrics-allowed*, until real pricing packages exist (see *Pre Launch Exclusive* below).
3. **Provisions the tenant admin** as a Cognito user under `DEC-42b9c0` (admin-provisioned only; `custom:tenant_id` + `custom:roles` stamped; invitation email).
4. **The admin verifies the invitation** (completes `FORCE_CHANGE_PASSWORD` → `UserStatus = CONFIRMED`), on which the tenant transitions to `active`.

### B. The declared meaning of `active`

A tenant is `active` **if and only if** Activation is complete, i.e. **(i)** a provisioned *and verified admin* exists for the tenant — the verified-admin predicate (below) holds — **and (ii)** the tenant references a **Subscription** record (per `tenant-entitlement-enforcement.md`: exactly one, lifecycle-state `active`). `active` does **not** require any onboarded data — no connections, no admitted facts, no legal entity, no fiscal calendar, no source binding. An Activated tenant is an **empty-but-active bound container**. Requirement (ii) makes the activation gate agree with the entitlement chapter, which already rejects a subscription-less tenant at Connection registration — closing the gap that a tenant could be `active` yet unable to onboard.

This **amends `ADR-7df811`** (it does not supersede it; 7df811 remains authoritative for the isolation model, the onboarding-record lifecycle, and the status set):

- **§1 (subscription lifecycle):** the v1 deferral of a tenant subscription *record* is lifted to the minimal extent needed for requirement (ii) — a tenant↔package assignment with the `active / suspended / terminated` lifecycle §1 already declared. No billing, no tiers.
- **§3 (status set):** the `onboarding_incomplete` state added by bc-db 0034 is endorsed as the pre-`active` resting state of a newborn tenant.

### C. Tenant Onboarding (tenant plane)

The **verified admin** — not the platform operator — creates Connections to the tenant's source system, authorizes them, and triggers admission. Data flows through the platform's already-authored, governed shared contracts (Source State → UniBAT Reader → SO → Canonical Evaluation → CO → Metric Snapshot) to the first Metric Snapshot. **Contracts and metric bindings remain platform-governed; a tenant admin never authors a canonical or metric contract.** Onboarding strictly follows Activation.

### D. Activation-gate re-scope

The DB activation gate (`trg_tenants_activation_gate`, bc-db 0034, deferred) is **retained as the enforcement mechanism**, but the verdict it consumes is re-scoped to the **Activation** plane:

- The verdict is `complete` **iff** B(i) and B(ii) hold; its `unmet_code` vocabulary becomes **`{no_verified_admin, no_assigned_subscription}`**.
- The prior data-plane codes `{no_legal_entity, no_fiscal_calendar, unresolved_source_binding}` are **re-homed to an Onboarding-readiness signal** that governs *trust in the first Metric Snapshot* and does **not** gate the `active` transition.
- Because 0034 is **unapplied**, this is a design-time amendment to a *deferred* migration — not a change to any applied object. The clean path is to amend 0034 in place before it lands (its `ck_ocr_unmet_allowed` CHECK and header); a successor migration is the fallback only if 0034's number is already frozen by an in-flight apply.

### E. The verified-admin predicate and signal

**Predicate (all must hold, verified by a fresh authoritative read at the activation act).** A tenant has a verified admin iff a Cognito user exists whose: (1) `custom:tenant_id` equals the tenant's canonical slug; (2) `custom:roles` includes the governed tenant-admin role; (3) account is **enabled**; and (4) `UserStatus` is `CONFIRMED`. `CONFIRMED` alone is insufficient — it proves only that the password challenge was completed, not that the user is an enabled admin bound to *this* tenant. The verdict is **refused** (`unmet_code` includes `no_verified_admin`) if any component is absent or mismatched. (Grounding: `POST /admin/users` accepts a caller-supplied slug and an arbitrary `roles[]`, so none of (1)–(3) can be assumed from provisioning alone; they must be read and checked at activation.)

**Signal.** `completeProvisioning` no longer flips a newborn straight to `active`; **birth ends the tenant in `onboarding_incomplete`**. Because the Cognito **post-confirmation Lambda trigger does not fire for admin-created (`AdminCreateUser`) accounts**, the activation transport is an **operator-invoked (or operator-surface-invoked) activation act** that performs an authoritative `AdminGetUser` read, checks the predicate, **emits** the Activation-completeness verdict (Foundation VI — emitted at the act, not inferred by a read-time scan), and attempts the `active` transition; the DB gate (D) then admits it only on a `complete` verdict. This ADR fixes the **requirement and the predicate**; the exact activation-act surface is detailed in the companion study and built in the downstream unit. A background post-confirmation push is **not** a viable default and is removed from scope.

### F. SOP split

`bc-docs/docs/onboarding/tenant-onboarding.md` is split into two SOP sections/chapters — **Tenant Activation (platform)** and **Tenant Onboarding (tenant)** — with the existing ten steps re-homed (detail in the companion design study). The aspirational four-tier/Stripe model (`DEC-324d9e`) is held as the subscription set's *future* authority, not the interim built reality.

### G. The onboarding-record journey attests Onboarding, not Activation

At the pinned bc-core commit, `completeProvisioning` calls `recordOnboardingActivated` in the birth transaction, which sets `tenant.onboarding_record` to terminal `activated` and stamps `activated_at` (bc-db 0006 retains terminal rows). Under the two-plane model that is **wrong**: it would permanently attest the tenant-plane journey as *activated* before any Connection, admission, or Metric Snapshot. This ADR declares:

- The `tenant.onboarding_record` lifecycle (`initiated / in_progress / ready / activated / cancelled`, `ADR-7df811 §2`) is the **tenant Onboarding-plane journey**. Its terminal `activated` attests **Onboarding completion** (the first Metric Snapshot / operational), **not** Activation.
- Birth (`completeProvisioning`) must **not** stamp `onboarding_record = activated`. Activation leaves the journey at `initiated` (its birth-intake state); the terminal `activated` write moves to the Onboarding-completion act.
- Activation completion is attested solely by the Activation-completeness verdict (D) and the tenant status `active`. (Naming tension noted: the verdict table is `onboarding_completeness_result`, yet it now attests *Activation*; a later cosmetic rename is possible but is **not** done here — no substrate rename on this design-only ADR.)
- Cancelled/retry: a cancelled journey still blocks re-activation per the existing `recordOnboardingActivated` guard; the build must preserve that and add a test that an **empty active tenant is not reported as onboarded** (journey not `activated`).

## Pre Launch Exclusive (interim subscription)

The "Pre Launch Exclusive" offer (operator-named 2026-10-21) is expressed in the real vocabulary of `tenant-entitlement-enforcement.md`: a **Subscription** whose **catalog entitlement references all metrics** (an all-permitting set), lifecycle-state `active`. Because enforcement is "Not yet wired" and no metric-allowance model exists, its job is to be an **explicit, recorded reference** (Foundation IV), not to enforce restriction in the interim.

- **It is an all-entitlement interim *template*, not a fifth commercial tier.** It sits outside the `DEC-324d9e` four-tier (Demo/Starter/Professional/Enterprise) Stripe taxonomy: no billing, no hosting-variant pairing. When real packages land, the Pre Launch Exclusive offer is retired/replaced; `DEC-324d9e` remains the future commercial authority.
- **Catalog shape:** a `pricing.package` (Drizzle `subscriptionPackage`) row with `display_name = "Pre Launch Exclusive"` and `package_name = pre_launch_exclusive` (the stable natural-key code), `status_code` `active`, marking the all-entitlement template. Reusing the seeded `Free` row is an acceptable fallback; a clearly-named row is preferred so the interim offer is legible and later-replaceable.
- **The all-metrics entitlement** is represented so that it says "all" without enumerating every metric (an `all`-scope sentinel on the Subscription), avoiding both a brittle enumerated list and JSONB-for-queryable-data (D162). Enumerated per-metric entitlement link tables are the *future* shape for real packages.
- **The tenant↔Subscription reference** is the Subscription record `ADR-7df811 §1` deferred and `tenant-entitlement-enforcement.md` assumes: one *current* per tenant, lifecycle `active / suspended / terminated`. Because the record is **append-only** (Foundation III), a suspension or termination **appends a new row**, never overwrites — so the build must define *current active* explicitly: the latest row by `effective_from` with `status_code = active` and `effective_to` null, enforced as "exactly one active per tenant" via a partial unique index (`WHERE status_code = 'active' AND effective_to IS NULL`). Requirement B(ii) = a *current active* assignment so defined.
- The operator assigns it in **Activation step A(2)**, as a governed platform act alongside identity creation.

## Foundation invariant check

This is a **design act** (DEC-c48b0f): the repair of a missing/wrong *declaration* of what `active` means. Repair location **A/B** — admission-boundary identity (A) + contract semantics of the tenant status (B).

1. **Why A/B?** The defect is a meaning gap at the identity/admission boundary: `active` has no declared meaning binding it to a verified admin + a subscription. The fix *declares* that meaning. The DB trigger (layer E) only *enforces* the declaration.
2. **Why not an upper layer?** The status-meaning declaration and the activation act are the top of this stack; the operator's model is the source declaration being recorded. The under-specification lives exactly at A/B, so this is not compensation beneath an underspecified upper layer.
3. **Why not a lower layer (D–F)?** A lower-layer check (a bc-admin read-model detector, or a scan for admin-less active tenants) is a net, not a declaration — it finds violations after the fact. The DB gate is enforcement of the declared meaning, not the meaning itself; `completeProvisioning`'s straight-to-`active` flip is the gap, so no working implementation is being bypassed.
4. **Design or execution act?** **Design.** Named design act: declare Activation-completeness = {verified admin, assigned subscription}; the 0034 verdict/trigger is the detector/enforcement that consumes it. No detector substitutes for the declaration.

Invariants honored: **I** — `active` is evaluated once at the activation verdict; reads never re-derive it. **VI** — the verdict is emitted at the activation act (append-only), and the admin-verified signal is an emitted event, not a read-time inference. **III** — verdict rows are append-only (0034 triggers). **II** — Activation precedes Onboarding; the fixed object progression is preserved, not reordered. **IV** — the subscription is an explicit tenant→package reference, not implicit. **No invariant is violated.**

## Consequences

1. `active` becomes a truthful claim: an active tenant has a real, verified admin and an assigned subscription. The clean LC5 fixture (`lc5new`) is created through this flow, which unblocks the "≥1 active tenant" and "kaveri-last removal" dependencies.
2. A newborn tenant now rests at `onboarding_incomplete`; the data-onboarding plane is explicitly *after* `active`, matching the operator model.
3. The deferred bc-db 0034 is amended before it lands; its gate mechanism is reused unchanged, only the verdict's meaning changes.
4. Downstream work (bc-core: emit the activation verdict, rest at `onboarding_incomplete`, fix the tenant-status seed drift, wire the subscription assignment; bc-db: amend 0034 + add the tenant↔package assignment table; the test surface) lands through its own reviewed units under the Database Change Protocol. **This ADR authorizes none of it.**
5. **Risk flagged:** re-scoping 0034's verdict codes reinterprets the D622/D623 intent. Mitigated by 0034 being unapplied and by the conservative alternative being available (keep the data codes as *additional* activation requirements) — rejected here because it contradicts the operator lock that a tenant can be Activated with zero onboarded data.

## Not decided here

The real pricing/packages model (`DEC-324d9e` four tiers + billing), per-tenant metric-allowance enforcement, and the exact activation-act surface are out of scope. The **legal-entity** question is *settled* for this ADR, not deferred: the operator's recorded grant `2026-10-20T11-09-28-199Z-11867ed1` (text SHA-256 `11867ed166f6b1006d64b3583c0de12089811142e4cf7737637f290ff00cbd51`) decides, via `DEC-4aa1ff`, that LE declaration is a **tenant-app (Onboarding-plane) act after the platform shell and admin exist** — which is exactly why `active` requires no LE. That grant confers no build or activation authority; this ADR fixes the Activation meaning and the plane split only.
