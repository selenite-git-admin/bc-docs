---
uid: DEC-4aa1ff
title: "Canonical legal-entity identity: a platform-minted LE id is the partition axis of the object progression; source company keys are confirmed cross-references; identity is declared at tenant onboarding and realized at source onboarding"
description: "Executes DEC-c05551 B1's deferred opaque-LE-id migration; declared→realized LE lifecycle; the DEC-bacbf5 mapping becomes the xref to the canonical id; attribute survivorship; LE as an explicit evaluation partition (fixes the tenant-wide D-7 assertion); raw-key LE references banned; amends DEC-c05551, DEC-bacbf5, DEC-103acb and the DEC-fa7c63 D-7 enforcement."
status: proposed
date: 2026-10-20T05:05:30.854Z
project: bc-core
domain: tenants
subdomain: tenant-dim/legal-entity
focus: identity-resolution
amends:
  - DEC-c05551
  - DEC-bacbf5
  - DEC-103acb
  - DEC-fa7c63
---

# Canonical legal-entity identity: a platform-minted LE id is the partition axis of the object progression; source company keys are confirmed cross-references; identity is declared at tenant onboarding and realized at source onboarding

## Context

ADR-c05551 and ADR-bacbf5 already decide the separation of LE identity from source keys, the many-to-one binding and tenant ≠ LE. What remains open is the identity form (B1 was deferred: a free-text tenant label is still the PK), the point where identity is established, attribute survivorship, and above all the partition. Evaluation today is a de-facto tenant=LE, because checkScopeEntity refuses any multi-LE tenant, and the scheduler still uses '*'. Minting a platform id, realizing it against source evidence, keeping source keys as confirmed xrefs and making the LE the explicit partition axis closes these gaps with declarations, not resolver patches. That is consistent with the ERP/MDM practice the operator cited and with Invariants I–VI.

## Grounding (2026-10-20, bc-core and bc-docs origin/main, platform DB read-only; no tenant read)

**Operator thesis, via the Chief, with ERP/MDM research:**
1. A tenant owns a set of legal entities (LEs).
2. An LE's identifier lives in the source system, so tenant onboarding should carry a display name and intent, not a free-text identity.
3. The same real-world LE in several sources (Odoo, SFDC) must reconcile to one canonical LE: first source wins, later sources are mapped.
4. The design should follow how ERP and MDM systems do it.
5. The whole progression (observe, admit, evaluate, CO, metric snapshot) repeats per LE, so canonical-LE identity is the **partition axis**, not a side dimension.

The research's core finding: a source-agnostic platform mints its own canonical LE id and treats every source id as a cross-reference.

**Already decided (not re-decided here):**
- **DEC-c05551:** LE identity is canonical and separate from any source key. A governed, versioned, many-to-one source→entity binding is applied at the canonical boundary, and an unbound key is refused, never wildcarded.
- **DEC-bacbf5:**
  - D1: a tenant is not an LE (one or more per tenant), and LE declarations carry no source identifiers.
  - D2: a connection belongs to exactly one tenant.
  - D3: the mapping is keyed on an immutable key domain plus `connection_id`, in value_keyed or connection_scoped shape.
  - D4: a source-onboarding completeness predicate.
- **DEC-ea4523:** no `'*'` LE.
- **DEC-7a8cbc:** binding-realized issuer identity.
- **Most of the research model is therefore already doctrine.**

**Gaps found:**
- **G1. Identity equals a tenant-typed label.** `tenant_dim.dim_legal_entity.legal_entity_code` (free text typed at tenant onboarding, e.g. `KAVERI-IN`) is the primary key and the join key for `tax_registration`, `organization.fiscal_calendar_config`, the binding target, CO LE values and the metric scope. DEC-c05551 **B1 explicitly deferred** the opaque-id migration to "a later, separately-reviewed identity migration" that must define the key transition, every FK/reference/evidence surface, historical-query semantics and rollback. This ADR is that proposal.
- **G2. Identity is established at tenant onboarding.** DEC-bacbf5 D1 and DEC-103acb require an LE to be declared at tenant onboarding, and that declaration *is* the identity. No source evidence is ever required for an LE to exist.
- **G3. No attribute survivorship.** Legal name, registration and tax id carry no source provenance. Multi-source attribute conflicts have no rule.
- **G4. Evaluation is not LE-partitioned.** `co-candidate-reader.ts` `checkScopeEntity` reads every CO of the grain for the tenant and **refuses the whole evaluation** if any CO belongs to another LE. That is DEC-fa7c63 D-7 ("scope: one legal entity E") enforced as a tenant-wide assertion, so a tenant with two LEs on one grain can be evaluated for neither. It contradicts DEC-bacbf5 D1. In addition, `runtime-scheduler.service.ts` defaults `legalEntityCode` to `'*'` (env `BC_SCHEDULE_LEGAL_ENTITY`), contrary to DEC-ea4523.
- **G5. Raw source keys used as the LE reference (Inv-IV):**
  - OC field mappings put `company_id` straight onto the LE reference: oc-3kgrr 1.1.0/1.2.0/1.3.0, oc-jbpz8 1.0.0/1.1.0, oc-c0q9s 1.0.0.
  - The SAP provenance-bound bukrs fiscal route (DEC-ea4523) uses the source company code as the LE code. It is the "degenerate case" DEC-c05551 point 5 tolerated.
  - TSK-1ec1a7 already rules the OC/CC pair fix and a fiscal-LE gate for cc-das36 and cc-7174p.

## Decision

**D1. Canonical LE identity is platform-minted and opaque.**
- Each LE gets an opaque, immutable, never-reused identifier (D560 doctrine, e.g. `LE-xxxxxx`). It is minted by a governed writer and is never derived from a source key, a tax id or the tenant's label.
- `legal_entity_code` becomes a tenant **label**, unique per tenant, changeable only by a governed rename event that never changes the id.
- Display name, country, functional currency and the optional registration, tax id and LEI are **attributes** with recorded provenance (D4).
- Every reference to an LE (FKs, CO LE fields, fiscal calendar, tax registration, xref, metric scope, snapshots, evidence) uses the canonical id.

**D2. Lifecycle: declared at tenant onboarding, realized at source onboarding.**
- **Tenant onboarding records an LE *declaration*:** display name and intent (for example "the Indian operating company"), optional identifiers, functional currency and the fiscal-calendar intent. The governed writer mints the canonical id **in state `declared`**, so the calendar and tax configuration attach to a stable id from the start and nothing is re-keyed later. A declaration carries **no source identifier** (DEC-bacbf5 D1 kept) and is **not an authoritative identification**.
- **Source onboarding realizes it.**
  - The connection's entity master is *discovered* as evidence: Odoo `res.company`, SAP company codes, SFDC legal entity, a QuickBooks realm.
  - Each discovered source entity is disposed by **one explicit, confirmed, governed act** with an actor and a rationale. It either:
    - (a) adds an xref to an existing canonical LE; or
    - (b) fulfils an open declaration, moving the LE `declared → realized`; or
    - (c) creates a new LE, realized at birth, for an entity found only in the source.
  - The platform may *propose* matches (equal registration or tax id, name similarity) **as evidence only**. **It never infers a mapping.**
- **Only a `realized` LE can be evaluated.**

**D3. The cross-reference is the DEC-bacbf5 mapping, retargeted to the canonical id.**
- The xref is the existing two-step key-domain declaration plus mapping revision: `(connection_id, key_domain, source_key_value) → canonical LE id`. It is immutable, as-of, exactly-one, with governance events and lineage (DEC-c05551 B3).
- One canonical LE has many xrefs: across connections and source systems, and many source companies to one LE.
- Cross-source reconciliation (Odoo company 1 and SFDC account X are the same LE) is the D2(a) confirmed act on the second source.
- **The first source to realize an LE does not own the identity.** The platform owns it. "First-source-wins" applies to attributes only (D4).

**D4. Attribute survivorship.**
- Source-supplied legal attributes (legal name, registration, tax id) **survive from the first realizing xref**, with lineage naming that xref.
- Tenant-declared attributes (display name, intent) are declarations and govern display.
- A later source's differing value is **recorded as an attribute observation and surfaced as a data-quality signal**, never overwritten and never buried.
- An attribute change is a new attribute revision (Inv-III). Changing the surviving value is a governed act.

**D5. The LE is the explicit partition axis of the object progression.**
- Every CO of an LE-bearing CC (fiscal, or carrying an issuing or recording LE reference) carries **exactly one canonical LE id**, realized through the declared binding derivation. An unbound or unresolved CO is refused, never wildcarded.
- An LE-scoped evaluation **selects the partition**: the COs whose LE is E. It does not assert that the tenant has a single LE. DEC-fa7c63 D-7's meaning ("one legal entity E") is unchanged; only its enforcement changes. Unbound COs and composite operand mismatches (E, currency, calendar, T) still refuse.
- Fiscal periods, metric snapshots, evidence and the portal LE filter are keyed by the canonical id.
- Scheduled campaigns iterate the tenant's **realized** LEs. The `'*'` scheduler default is removed.
- Cross-LE aggregation (consolidation, eliminations) is out of scope. It will be a declared consolidation entity in a follow-on ADR, never an implicit cross-partition sum.

**D6. Reorganizations and non-1:1 sources.**
- An LE is never merged, split or re-identified in place. Mergers, splits and re-domiciliations are effective-dated **supersession events** with successor ids. Xref revisions are effective-dated, and history keeps its original LE (Inv-III, Inv-V).
- **One source key → many LEs** (for example SAP shared-services codes) cannot be resolved per record. It needs a finer declared key domain (segment or profit centre) or it is a recorded refusal. It is never guessed.
- **Many keys → one LE** is native (D3).
- **A source with no natural company key** uses DEC-bacbf5's `connection_scoped` shape with a human-confirmed mapping.

**D7. No raw source key is ever an LE reference (Inv-IV).**
- No OC may map a source company key directly as the LE reference. Resolution happens only through the declared xref derivation (`resolve_source_entity_binding`).
- The SAP bukrs special route retires: bukrs becomes the key value of a value_keyed key domain.
- The fiscal-LE gate (TSK-1ec1a7 amendment 1) generalizes to: *"an LE-bearing CC resolves each CO to a canonical LE id through exactly one declared xref derivation."* The SAP alternative branch is removed when bukrs is xref'd.

**D8. Completeness and readiness (amends DEC-103acb and DEC-bacbf5 D4).**
- **Tenant-onboarding completeness:** at least one LE *declared*, each with its fiscal calendar.
- **Evaluation readiness per LE:** realized, calendar in force, and every entitled source key on every feeding connection xref'd (the DEC-bacbf5 D4 predicate, now per LE).
- Birth ends in `onboarding_incomplete` (bc-db 0034 + the birth/activation split, TSK-49f8d8). Readiness is a computed, recorded result, never a controller's read (Inv-VI).

**D9. Migration (B1's required content; each act separately reviewed).**
- **Surfaces:**
  - `tenant_dim.dim_legal_entity` (new id PK; the label stays unique);
  - `tax_registration` and `organization.fiscal_calendar_config` FKs;
  - the binding target (bc-db tenant/0002);
  - the CO LE fields (derivation output);
  - metric scope and snapshot keys;
  - `metric-proof-scope` and evidence;
  - the portal apex filter;
  - the scheduler.
- **Key transition:**
  - New tenants are born on the canonical id.
  - Existing tenants (`kaveri`, preserved by non-action) are **not re-keyed in place**. Their historical facts keep their code values, and the historical-query semantics name the key form per tenant and fact version.
- **Version rule:** a change in what the derivation's output *means* (code → canonical id) requires a **new major CC version** (a new fact table). Values never mix inside one fact table (Inv-I, Inv-III).
- **Execution home:**
  - skeleton DDL as bc-db tenant migrations (`fact.*` is never targeted; TSK-4d297e);
  - engine changes in the Codex platform lane;
  - contract versions on the SOP rails;
  - operator DB yes for each DDL.
- **Rollback:** the label stays unique and resolvable throughout, so readers can fall back to label resolution until cutover.

## Knock-ons

- **(a) D3 / tenant onboarding:** reshaped as in D2 and D8. Intent and calendar are captured at tenant onboarding; identity is realized, with evidence, at source onboarding.
- **(b) The fiscal-LE gate:** generalizes as in D7. The rule is "resolve to the canonical LE via the xref", and the mechanism is the same derivation.
- **(c) The cc-das36 instance fix survives unchanged in shape.** It is oc-3kgrr 1.4.0 (drop the direct `company_id` LE mapping) plus cc-das36 3.0.0 (declare `resolve_source_entity_binding`), which is exactly the single-source case of this model. Under D9 only the *value* the derivation emits (label → canonical id) changes, and that comes with its own major CC version.
- **(d) CC-version ↔ tenant fan-out.** It is acceptable for **provisioning**: per-tenant fact tables are idempotent, empty and cheap. It becomes a smell only if provisioning or activation is read as **evaluability**. Evaluability must be the per-tenant, per-LE readiness of D8, so a global CC activation never implies that any tenant or LE can evaluate. The one real hazard in the fan-out is version regression (an older `pending_provisioning` version activating late), which the readiness newer-version guard closes. That guard is load-bearing (TSK-1ec1a7).

## Foundation (DEC-79b62f)

**Four questions:**
1. **Location: B**, what an LE identity is, where it is established and how attributes survive; **with C**, the xref binding. The partition selection is the D-layer execution of a declaration made at B.
2. **Not upper:** the sources are correct. Their entity masters are **evidence of** an LE, not its identity.
3. **Not lower:** the tenant-wide scope assertion, the `'*'` scheduler default and the bukrs route are lower-layer stand-ins for an undeclared partition and an undeclared identity. They are replaced by declarations, not patched in the resolver.
4. **Design act:** identity, lifecycle, survivorship and partition are all declared here. Every migration and engine change is a separately reviewed execution act.

**Invariants:**
- **I:** an LE's identity and attribute meaning are decided once, at their governed acts.
- **II:** the canonical id fixes the partition, and the progression order is unchanged.
- **III:** ids are never reused; attributes, xrefs and reorganizations are revisions or supersessions; history is never re-keyed.
- **IV:** every LE reference is an explicit, binding-realized canonical id, and raw-key references are banned.
- **V:** evaluations are per-LE fresh acts, never re-pointed.
- **VI:** realization, xref, survivorship conflicts and readiness are emitted records.

## Needs an operator decision

1. **Adopt the platform-minted opaque LE id** (executing DEC-c05551 B1's deferral) for new tenants? Recommended: yes.
2. **Mint at declaration (`declared → realized`)**, or mint only at source onboarding? Recommended: declared → realized.
3. **Survivorship:** first realizing source for legal attributes, tenant declaration for display, conflicts surfaced. Confirm?
4. **Sequencing.** Recommended: **unpause** the cc-das36 fix and the prove-on-one now, on the status-quo label key, which DEC-c05551 B1 still governs and which is model-invariant. Migrate under D9 afterwards, on new CC versions and a new greenfield tenant. The alternative is to hold the prove-on-one until D9 lands.
5. **Retire the SAP bukrs special route** into the uniform xref at migration? Recommended: yes.

**Next:** a Codex design review, then the operator's terms, then separately reviewed execution units:
- DB: skeleton DDL;
- Platform: the partition-selection fix for G4, the scheduler, the readiness guard and the fiscal-LE gate;
- Metric: contract versions.
