---
uid: DEC-bacbf5
title: "Source-system onboarding completeness: every tenant connection maps its company identity to the tenant's declared legal entities before it may feed evaluation"
description: "Source-side sibling of DEC-103acb/D504: tenant != legal entity; a connection belongs to one tenant; onboarding ANY source requires a governed, source-agnostic legal-entity mapping (value-keyed or connection-scoped) keyed on a governed key domain, plus a witnessed, derived completeness predicate re-checked at every observation entry. Amends DEC-c05551/D574 B2 and DEC-103acb/D504 D1 (calendar clause)."
status: decided
date: 2026-09-25T01:22:08.304Z
project: bc-core
domain: tenant
subdomain: onboarding/source-identity
focus: governance
amends:
  - DEC-c05551
  - DEC-103acb
---

# Source-system onboarding completeness: every tenant connection maps its company identity to the tenant's declared legal entities before it may feed evaluation

## Context

Verified read-only on 2026-09-25 (SES-bde699).

- **No '*' fallback.** DEC-ea4523/D623 removes the `'*'` legal-entity fallback. Every canonical row that needs a fiscal period must resolve a concrete legal entity through a governed source→legal-entity binding.
- **No source-system onboarding service exists.** Only fragments do:
  - `POST /connections` is PlatformOnly, and its controller calls `createConnection(dto)` without a tenant, so `runtime.connection.tenant_id` is never recorded. Kaveri's only connection, `kaveri-odoo-v3lc5`, has `tenant_id` NULL. `connection_status` (draft→connected) tracks connectivity only.
  - `POST /schema-provisioner/onboard-connector` (DEC-95687d/D369) reports provisioning readiness only.
  - The tenant-onboarding chapter names an "onboarding-incomplete" source state that nothing records.
- **Reader fetch lists are hand-kept per executor and never checked against the contracts.** Kaveri's reader never fetched `company_id`, so all 10,744 admitted journal-entry rows lack the company key.
- **The D623 binding substrate (bc-db tenant/0002, never applied) supports only a record-field key and pins every mapping to SC/OC versions**, as DEC-c05551/D574 B2 requires. Two consequences:
  - A source with no company concept, or with a request-scoped company, cannot be mapped.
  - Every contract re-version forces re-mapping.

**Operator doctrine (2026-09-25):**
- a tenant and a legal entity are different concepts;
- tenant onboarding declares at least one legal entity;
- onboarding **any** source system requires mapping it onto the tenant's legal entities (declare the entity first if it is missing);
- source onboarding is not complete without this and the other mandatory steps.

A source's company identifiers are only knowable at source onboarding, so tenant onboarding and source onboarding are separate, ordered acts.

**Review history.** RESPONSE-Codex-d617-034 was CHANGES REQUIRED:
1. the anchoring change conflicted with D574 B2;
2. key coverage was unwitnessed;
3. the reader/key checks were too weak;
4. D504's `'*'` calendar clause was unreconciled.

This revision answers each. RESPONSE-Codex-d617-035's rulings on shape serialization and actor provenance are adopted as requirements in D3 and D6.

**Revision 2.** RESPONSE-Codex-d617-036 accepted the authority direction and found three remaining gaps:
- a bounded-scan pass was not tied to the run's window;
- first-run key evidence was undefined;
- the calendar horizon was open.

D4 now decides completeness per candidate run, against one finite window.

## Decision

### D1 — A tenant is not a legal entity
- **Definitions.** A tenant is the BareCount customer account and data boundary (subscription, users, tenant database). A legal entity is a registered company whose books are observed.
- **Cardinality.** A tenant holds one or more legal entities; a legal entity belongs to exactly one tenant.
- **Onboarding.** Tenant onboarding MUST declare at least one legal entity with its own fiscal calendar.
- **No source identifiers.** Legal-entity and calendar declarations carry no source identifier of any kind.
- **Timing.** They are writable at any time (acquisitions, entities discovered during source onboarding), through the governed writers of D504 D4.

### D2 — A connection belongs to exactly one tenant
A source connection (`runtime.connection`) is the tenant's instance of a source system. Its owning tenant must be recorded through a governed act and is immutable afterwards. A connection with no owning tenant cannot be onboarded. Every mapping target (D3) must be a legal entity of that owning tenant.

### D3 — Governed, source-agnostic legal-entity mapping per connection (amends D574 B2)

**Key domain.** A key domain is a governed, immutable identity for one company-identifier space observed on one connection. Examples:
- "the company ids of this Odoo installation";
- "the company codes of this SAP client";
- "the organisation this QuickBooks realm reads".

Each domain has:
- an id and a `domain_code` unique within its connection;
- a shape: `value_keyed` or `connection_scoped`;
- a locator kind: `record_field` or `observed_scope`, for `value_keyed` only;
- a creating governance event (D6).

Rules:
- **Scope.** Two feeds or scopes on one connection whose identifiers are different spaces MUST be different domains. Two installations are different connections.
- **No inheritance across a change of meaning.** A change of key meaning or scope (a field that starts carrying a different identifier space, a scope that changes grain) creates a NEW domain. It never inherits mappings.

**Two shapes, chosen by what the source exposes, never by vendor name:**
- **`value_keyed`** — the source exposes a company key, either as a record field or as a request scope the reader OBSERVES and records per record. The scope must be observed, never a configured default. Each observed key value maps to exactly one legal entity; many values may map to one entity.
- **`connection_scoped`** — the source has no company concept at all. The whole connection maps to one entity. This is not a workaround for a reader that failed to fetch an existing key.
- **Choosing.** Use `value_keyed` whenever a key exists, even with one company today.

**Domain declaration (the version-equivalence rule).** Each pinned contract version that a connection is bound to MUST declare which key domain it reads and where the key is located:

```
(connection_id, source-contract UUID + version, observation-contract UUID + version, pinned leg,
 locator) -> key domain
```

This is the full D574 B2 provenance tuple.
- **Form.** The declaration is an immutable, governed, as-of record, with exactly one applicable declaration per tuple; zero or multiple refuse.
- **Re-versions.** A contract re-version that reads the same identifier space declares the SAME domain. That declaration is the explicit, reviewable equivalence assertion. A re-version that changes meaning declares a new domain.

**Resolution, in two governed steps:**
1. The record's B2 provenance tuple → its domain, via the declaration.
2. `(connection_id, domain, key value)` → legal entity, via the mapping revision. For `connection_scoped` the key value is absent.

Lineage records the full B2 tuple, the declaration revision, the mapping revision and `observed_at` (D574 B3(d)). So a recorded realization stays reproducible, and no contract version is left implicit (Invariant IV).

**What changes in B2.** B2's closed provenance coordinate remains the lookup INPUT. What changes is the MAPPING row's identity: it is shared across contract versions that declare equivalence, instead of being duplicated per version. B2's motivating case (two installations sharing `res.company.id`) stays separated by `connection_id`.

**Mapping revision rules:**
- **Append-only and as-of.** Supersession is a later revision; retirement is a null-target revision.
- **No back-dating** past any evaluated observation.
- **Exactly one applicable revision**, or refuse.

**Shape transitions are connection-wide:**
- **Serialization.** Every mapping or declaration writer takes an EXCLUSIVE connection-level lock. Every realization that records lineage takes a SHARED connection-level lock, then re-derives its as-of choice after the lock. The lock order is connection, then row.
- **Switching shape:**
  1. retire every active mapping of the old shape at T;
  2. open the new shape strictly after T;
  3. T must be later than every observation already evaluated on the connection.
- **Refusals:**
  - a gap between shapes: observations in it are refused;
  - an unmapped value: refused `no_legal_entity`;
  - two shapes in effect at the same instant: unrepresentable.

The state table and adversarial proofs are part of the D623 successor design (d617 exchange), not this ADR.

### D4 — Source onboarding completeness: a DERIVED predicate, decided per candidate run

**ONBOARDED is not a stored status.** It is a derived read, computed from the latest immutable evidence of every step below. Each step reports `pass` / `fail` / `unknown` with an enumerated reason (Invariant VI), and the read triggers no evaluation. `unknown` is never a pass.

**Candidate run.** Every observation entry is a candidate run: scheduled, on-demand, retry, re-observation or replay. It carries exactly one **candidate window**: a finite business-date interval `[from, to]` plus its connection, runnable reader configuration hash and bound key-domain declarations.
- **First run:** the window starts at the declared historic start (step 8).
- **Incremental run:** the window runs from its watermark to the run's start date.

Every window-dependent step below (4, 6, 7) is evaluated against that ONE window, and the gate records the window with its decision.

1. **Owning tenant** — recorded (D2).
2. **Connectivity** — the latest connection check is a pass. It is newer than any credential or endpoint change, and within the declared freshness bound. A failed or expired check fails the step.
3. **Runnable reader** — the exact reader configuration the run will execute: its flavor id plus a config content hash. Its connection must be this connection, its environment/scenario must match the connection's, and it must be paired with the tenant's active pinned contract versions.
4. **Key capture** — for each bound observation-contract version and its declared key locator:
   - **(a) Configuration:** the fetch list covers every declared field, and the locator is requested (`record_field`) or captured from the source's response per record (`observed_scope`). A configured value is never an observed scope.
   - **(b) Prospective capture probe:** before admission, the gate reads a bounded sample of records in the candidate window through the exact runnable configuration. The probe is non-admitting: it creates no source or canonical object.
     - `pass` when the sample is non-empty and every sampled record carries a non-null key at the locator;
     - `fail` when any sampled record lacks it;
     - `pass_empty` when the source returns no records in the window, because nothing would be admitted.

     This is how the FIRST run is gated: absence of prior admissions never passes by itself, and the probe does not demand evidence only the run could create.
   - **(c) Post-run evidence:** every admitted record's key is checked at canonical resolution, and a missing or null key is refused (D623 fail-closed). The run's evidence records the keyed and refused counts. Any missing-key refusal sets step 4 to `fail` for later entries, until the configuration changes and a new probe passes.

   Generic fetch-list derivation stays in the TSK-b5ab8a class.
5. **Provisioning** — fact tables for the bound contracts are provisioned (DEC-95687d/D369 readiness).
6. **Mapping coverage (witnessed)** — each `value_keyed` domain needs a COVERAGE WITNESS: an immutable record of the key values present, with its method, domain, reader configuration hash, as-of time, evidence hash and (for a scan) its window. Every witnessed value must have a mapping in effect. The two methods differ in what they can cover:
   - **`authoritative_enumeration`** (the source's own company list, read through the connection) covers the whole domain as of its as-of time, for any candidate window. It stays valid until one of: a declaration change, a reader configuration change, an unmapped-value refusal, or its declared maximum age.
   - **`bounded_scan`** (the distinct key values over a scanned window, read by a non-admitting key probe) is a `pass` ONLY for a candidate run whose domain and reader configuration hash equal the witness's AND whose candidate window lies wholly inside the scanned window. Any wider or different run is `unknown`, and the gate refuses it until a new scan covers that window.
     - A source without an authoritative enumeration therefore takes a fresh scan over each candidate window before admission. It never claims connection-wide completeness from a past scan.
   - **Missing or revoked witness.** No witness is `unknown`. An unmapped-value refusal REVOKES the witness in force: every later entry is `unknown` until a new witness is taken and every witnessed value is mapped.
   - **`connection_scoped`** domains need exactly one mapping in effect over the whole candidate window.
7. **Calendar coverage** — every mapped legal entity belongs to the owning tenant and has per-entity fiscal-calendar revisions covering the WHOLE candidate window `[from, to]` without gap.
   - **Open-ended rule:** a revision's coverage starts at its `effective_from`. The latest revision covers every later date, and an earlier revision ends where the next begins.
   - **Checked window:** the check is always evaluated against the finite candidate window, never against "today".
   - **Out-of-window records:** a record whose business date falls outside the candidate window, or outside calendar coverage, is refused at resolution.
8. **Historic start** — the first-observation historic start (backfill watermark) is declared. It is the `from` of the first candidate window.

**The gate (Phase 2)** evaluates this predicate for each candidate run, under the shared connection-level lock, BEFORE admission. It records the decision's evidence tuple:
- the candidate window;
- the reader configuration hash;
- the declaration and witness revision ids;
- the probe result;
- the calendar revision ids;
- the hash of the whole tuple.

A change to mappings, declarations, witnesses, contract bindings, credentials or reader configuration is reflected at the next evaluation, because nothing is cached as a durable flag.

### D5 — Calendar authority (amends D504 D1)
D504 D1's clause "at least one fiscal_calendar_config resolvable for each legal entity (tenant-default '*' or per-entity)" is amended to: **per-entity only**.
- A tenant-default `'*'` row no longer satisfies onboarding.
- D623 resolution refuses wildcard identity and reads only an exact legal-entity calendar.
- Existing `'*'` rows are legacy history: never rewritten, never read by resolution.

### D6 — Authenticated governance events
Every declaration (D3), mapping revision (D3), owning-tenant assignment (D2) and coverage witness (D4 step 6) is bound to a mandatory, immutable governance event.
- **Producer.** Only the tenant-authorized service may create the event, after authentication.
- **Content.** The event carries: the authenticated subject and issuer, tenant, connection, action, rationale, request correlation, and the exact revision it authorizes.
- **Binding.** The DB writer binds to the event and never trusts a caller-supplied name. The DB principal is separately guard-stamped.
- **Privileges.** The writer role's grants must not open a bypass path.
- **DBCP-driven acts** also carry and validate their accepting disposition.

This implements D574 B3(c) for routine onboarding without a per-mapping review round-trip.

### D7 — Enforcement phases
1. **Phase 1:** governed writers (legal entity + calendar per D504 D4, owning-tenant assignment, domain declaration, mapping, coverage witness) and the read-only completeness report.
2. **Phase 2:** the gate at every observation entry and replay path.
3. **Phase 3:** bc-admin onboarding UI.

Scope and precedence:
- **Existing connections** reach ONBOARDED through the same writers; there is no grandfathering by default.
- **Kaveri** (Odoo, `value_keyed` on its company field) is the first subject.
- **D504 Phase C** (tenant activation) remains a distinct prerequisite; a source being ONBOARDED never confers tenant `active`.

## Foundation gate
- **Repair location:** C (binding), plus the onboarding boundary.
- **Design act, not execution-plane net:** the fix is declaring tenant identity, key domains and source-to-entity mapping.
- **Invariants:**
  - **III:** declarations, mappings, witnesses and calendars are append-only; corrections are new revisions.
  - **IV:** every legal-entity reference and every contract version used is explicit, with no `'*'`/blank identity and no vendor-name routing.
  - **VI:** completeness emits enumerated reasons and evaluated evidence tuples, never a silent pass.
- **Portability test:** a second source of a different shape onboards through D3/D4 with no engine change.

## Not solved here
- Generic derivation of reader fetch lists from observation contracts (TSK-b5ab8a).
- A source-by-source catalogue of authoritative company enumerations; the method is chosen per source at onboarding.
- Per-legal-entity reporting-standard override.
- Identity migration to an opaque entity id (D574 B1 still stands).

## Relationship
- **Amends:**
  - DEC-c05551/D574 **B2**: the mapping identity becomes connection + governed key domain + value, with the B2 tuple kept as the lookup input via the domain declaration, and in lineage;
  - DEC-103acb/D504 **D1**: calendar clause, per-entity only.
- **Consistent with:** D574 B1, B3 and B4. B4's "every entitled source-company coordinate bound before a chain that can emit it may run" is realized by D4 steps 6 and 7 and the Phase 2 gate.
- **Source-side sibling of** DEC-103acb/D504.
- **Requires the DEC-ea4523/D623 binding-substrate successor**, reviewed on the d617 exchange: domain and declaration tables, connection-level serialization, stale-lineage rejection, governance events.
- **DEC-95687d/D369** onboard-connector becomes step 5.
- **Landing:** the PR that lands this ADR as `decided` also adds amendment notes to `ADR-c05551.md` (B2) and `ADR-103acb.md` (D1 calendar clause) pointing here, so the amended records name their amendment.
