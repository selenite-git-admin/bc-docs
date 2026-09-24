---
uid: DEC-a57eb8
title: "BareCount is not a system of record: canonical record identity is the faithful carry of the source's complete record key; the reporting fiscal period is a derived dimension, never identity"
description: "An observed record's identity is the source's own COMPLETE natural key (observed, not established) — every component, including a year or company component the source key contains; the resolver-derived reporting fiscal year/period is a metric dimension, never identity. Supersedes DEC-f4e9a0's universal composite; amends DEC-beef5c/D489."
status: decided
date: 2026-09-23T13:53:46.971Z
project: bc-core
domain: contracts
subdomain: concept-registry/identity
focus: identity
supersedes: DEC-f4e9a0
---

# BareCount is not a system of record: canonical record identity is the faithful carry of the source's complete record key; the reporting fiscal period is a derived dimension, never identity

> **Landing-review correction (2026-09-24).** The first ratified text (bc-docs#60 @ `cf457333`) said fiscal year is never identity "for every entity and every source" and prescribed demoting the document-fiscal-year concept globally. The external landing review (RESPONSE-Codex-pr-batch-landing-review-2026-09-24, P1 ×2) found that this drops an indispensable component of SAP's key (`belnr` recycles per fiscal year) and recasts the issuer as merely descriptive while still relying on it for identity. This text corrects both. The rule is now **the complete source key**, and the **reporting** fiscal period is separated from a **year component of the source's own key**. The demotion had already been executed in the registry on 2026-09-23. That live state and its held remediation are recorded under *Live state and held remediation*.

## Context

Every record BareCount observes needs a stable per-record identity — to deduplicate repeated observations, to anchor metric grain, and to carry evidence lineage. This ADR settles, once, **how that identity is formed when the same business record is admitted from heterogeneous source systems** whose native keys differ.

The platform accumulated a large apparatus around this question:

- **DEC-f4e9a0 (implemented)** modelled a Customer Invoice's canonical identity as a *system-agnostic composite* — `{issuing Legal Entity (reference), document number, document fiscal year (source-attested, GJAHR)}` — on one empirical fact: SAP `belnr` recycles per fiscal year (`(bukrs,belnr,gjahr)`=1716 distinct vs `(bukrs,belnr)`=1162), so a year discriminator was deemed "required."
- **DEC-beef5c / D489 (decided)** generalised that into a three-class record-identity rulebook, with Class-1 DOCUMENT identity = `{customer, legal entity, fiscal year, document number}`.
- To realise a *source-attested* fiscal year on a source with no such field (Odoo `account.move`), an **identity-carrier mechanism** was built — `identity_realization[] subsumed_by_carrier` with a mandatory per-installation attestation (bc-core PR #698, D573 meta-schema sync) — governed only by an external-audit exchange, **with no ADR**.
- The fiscal-time doctrine (`operating-model/fiscal-time-and-temporal-gates.md`, "Substrate Boundary") kept two fiscal years in tension: a **source-attested** identity year (SAP `GJAHR`) versus the **resolver-stamped reporting** fiscal year (Layer A, derived from posting date + tenant calendar), warning that conflating them is a "category error."

The trigger: onboarding a Customer Invoice chain over real Odoo data (Kaveri, `v3_lc5`) stalled at the identity preflight — Odoo has no `GJAHR`-equivalent field, forcing the half-built carrier+attestation path, which even once authored cannot yet evaluate (its attestation substrate + resolution-time resolver are unbuilt). Grounding: all 2,714 Kaveri customer invoices already carry the fiscal year *inside* the `l10n_in` document number (`INV/26-27/0316`), globally unique, zero cross-year reuse — the year is already part of the source's own key, not a thing the platform must attest.

## The reframe that dissolves the problem

**BareCount is not a system of record.** A system of record must *establish and guarantee* a record's identity — which is why SAP needs `bukrs+belnr+gjahr` and reasons about `belnr` recycling. BareCount **observes and references**; the source already owns identity and uniqueness. Carrying the source's key faithfully means carrying **all of it**: SAP's key *is* `bukrs+belnr+gjahr`, so `gjahr` is carried as a key component — not because the platform attests a fiscal year, but because dropping it would merge records the source keeps distinct. The entire apparatus above solves a problem the platform does not have: it re-engineers a canonical business identity as if the platform were the authoritative keeper of the record. It is not. The complexity became self-justifying — once the composite-identity / source-attested-fiscal-year / carrier-subsumption / attestation machinery existed, a simpler account felt untrustworthy. It is not naive; it is what remains once the system-of-record assumption is removed.

## Scope

This ADR governs the identity of **observed / admitted records** — canonical objects that are the platform's faithful projection of a source-system record (a document, a master row). It does **not** change the identity of **derived / computed canonical objects** — metric snapshots, action objects — which are genuinely the platform's own and keep their platform-established identity (grain + formula + period; DEC-3fe389/D560, D068).

## Decision

1. **An observed record's canonical identity is the source's own COMPLETE natural key, declared where meaning is owned.**
   - **Every component of the source's key is identity-bearing** for records from that source, whatever its business meaning. That includes a **year** component (SAP `gjahr`) and an **issuer/company** component (SAP `bukrs`, Odoo `company_id`). Examples: SAP `bukrs+belnr+gjahr`; Odoo `company_id + name`.
   - **Where the declaration lives.** Which grain-entity concepts *are* identity is declared in the BCF registry (`identity_role = identity_bearing`). The Observation Contract maps those concepts to the source fields. The canonical resolver keys each Canonical Object on exactly that set (`loadIdentity` → `groupByIdentity`) and never invents a composite.
   - **Two admissible realizations.** Either way the complete key must be covered:
     - **(a) direct:** every source-key component maps to an identity-bearing concept of the grain entity;
     - **(b) governed opaque key:** a single identity-bearing *source record key* concept whose governed mapping covers **every** component of the source's key. This requires its own governed mechanism and ADR. It is named here, not built.
   - **A partial key is refused, never resolved.** If a source's complete key is not covered by the grain entity's identity-bearing set, resolution refuses.
   - **Optional stamp.** A **SHA-256 stamp over the complete key is an OPTIONAL uniform realization**, not required for correctness or deduplication.
   - **Lineage.** The raw source key values are also carried as lineage fields.
   - **Ownership.** The platform **observes** this identity. It never re-establishes, re-decomposes or re-guarantees uniqueness; the source owns that. Observing it faithfully, however, forbids *dropping* any part of it.

2. **The reporting fiscal year and fiscal period are a derived dimension, for metric periodisation only, and are never an identity component.**
   - **Derivation.** They are resolved at canonical evaluation (§11.6 Layer A) from the CC's declared posting-date field plus the tenant's **per-legal-entity fiscal calendar**.
   - **Calendar is mandatory.** Declaring that per-legal-entity fiscal calendar is **mandatory and blocking at onboarding**. A missing calendar fails closed, never a `'*'` fallback.
   - **A different thing: a year inside the source's own key.** SAP `gjahr` is identity-bearing **as a key component** (point 1). It is never used as the reporting period, and the derived reporting period never replaces it.
   - **Where the source key has no year, none is added.** For example, Odoo `company_id + name` carries the year only *inside* `name`.
   - **What is withdrawn:** a **platform-attested fiscal year imposed as identity on sources whose key does not contain one** (the carrier/attestation apparatus). A year that is *not* part of a given source's key — such as the year embedded in an Odoo `name` — is a **descriptive / source-reconciliation** value (§11.6 Layer B), never a separate identity component.

3. **The only purpose of a canonical per-record key is deduplication of repeated observations, metric grain, and evidence lineage.** The complete source key in point 1 satisfies all three. No further identity engineering is warranted.

4. **Source-agnosticism lives at the grain, not the key.** A metric is defined over a system-agnostic entity/grain (e.g. Customer Invoice); the per-record key is the source-carried stamp. This is more source-agnostic than a re-engineered universal identity schema, not less — no source is forced to synthesise an identity field it does not natively hold.

5. **Fail-closed, never fabricate — in either direction.**
   - **No invention.** If a source yields no natural key that identifies its own records, admission refuses. The platform never invents identity from mutable or derived values (Invariant I; preserves the DEC-beef5c guard against composite identity from mutable fields).
   - **No omission.** Keying on a **subset** of the source's key is fabrication by omission: it asserts that records are the same when the source says they are distinct. It refuses just the same.
   - **Stable key.** The key must be the source's *stable* key. Where a source stabilises its business key late (e.g. an unposted Odoo draft), the record's stable source reference is used.

## Repair location & Foundation

- **Location B (contract grammar / declared identity) + A (what the source emits).** Identity is declared as the carried source key at the boundary where meaning is owned — not re-engineered downstream.
- **Invariant I:** identity is observed at admission from the source's own key, not invented at evaluation or reconstructed by inference.
- **Invariant III:** the stamped source key is immutable per record; a fiscal year derived from mutable tenant-calendar config is correctly excluded from identity and confined to the reporting dimension (stamped into the immutable CO/snapshot at resolution — a later calendar correction yields new snapshots, never rewrites old).
- **Invariant IV:** the canonical record explicitly references the source record by the declared key stamp. Nothing implicit.
- **Object model:** honoured — "a Canonical Object is identified by business identity keys, deterministic from the recorded inputs and the governed contract version." The business identity key is the deterministic key over the faithfully-carried source key; system-agnosticism is achieved per-contract without a universal cross-source identity schema (the earlier over-reach).

## Alignment with Reader & Evaluation mechanics (verified)

This doctrine fits the running engine, with one boundary the first text missed.

- **Canonical resolver** (`ccv2-canonical-resolver.service.ts` @ bc-core `main`) keys COs on the grain entity's `identity_bearing` concepts:
  - `loadIdentity` reads them per **entity**, not per source;
  - `buildIdentitySourceFields` throws if a pinned observation leg does not map one of them (Unit 0/F4, fail-closed);
  - `groupByIdentity` keys on exactly the mapped source fields.
  
  It **stamps the reporting fiscal period as a derived dimension**.
- **The boundary:** because identity is declared per entity, the resolver cannot know a given source's key. Demoting the document-fiscal-year concept makes it key on `(legal entity, document number)` for **every** source:
  - **correct for Odoo** (`company_id + name`);
  - **wrong for SAP**, where `gjahr` is a key component. DEC-f4e9a0's recorded evidence: `(bukrs,belnr,gjahr)` = 1716 distinct vs `(bukrs,belnr)` = 1162, so 554 invoices would merge.
  
  A registry concept change alone therefore **does not** realize point 1 for all sources. The remediation below is required.
- **Reader** fetches the declared source fields into `fact.so_*`; identity grouping happens later at the resolver — unaffected by this ADR.
- **Admission is deliberately non-idempotent** — every admission is a distinct immutable observation act (Invariant V). "Same record not observed twice" is therefore **not** an admission guarantee; repeat observations of the same record are collapsed to **one CO at canonical resolution, by this identity** (`groupByIdentity` + a governed latest-by selector; version-scoped idempotency `UNIQUE(admission_id, CC version)`). This identity *is* the dedup key — which is the strongest confirmation that it must be the source's **complete** natural key: a partial key silently collapses distinct records into one CO.

## Supersession & amendment

- **Supersedes DEC-f4e9a0's identity model**, meaning the **universal** composite `{Legal Entity, document number, document fiscal year}` imposed on every source, and a "document fiscal year" that the platform attests even where the source key has none.
  - For a source whose key *is* that composite (SAP), the same three components remain identity-bearing, now **because they are the source's key** (Decision 1).
  - **Retains** the Legal Entity entity and the record→Legal-Entity reference. The issuer reference stays **identity-bearing wherever the issuer/company is a component of the source's key**: SAP `bukrs`, Odoo `company_id`, and today every live finance source. It **additionally** anchors the per-LE fiscal calendar and roll-ups. The same document number in two companies therefore remains two records.
- **Amends DEC-beef5c / D489.** Class-1 DOCUMENT identity becomes **the source's complete natural key**.
  - A fiscal year is identity-bearing only as a component of that key, never as a platform-imposed universal component.
  - The reporting fiscal year is a derived dimension.
  - The additive-first posture and the "never fabricate identity from mutable fields" guard are retained and reinforced; Decision 5 adds "never by omission".
- **Retires the `subsumed_by_carrier` + per-installation-attestation apparatus for identity/fiscal-year.** The mechanism (PR #698, D573 meta-schema) stays in the substrate but is dormant for this purpose — there is no fiscal-year identity to carry. A genuine future fused-identity case that is *not* a category error may re-charter it by a separate ADR.

## Known bounded consequences & deferred items

- **Cross-source same-record identity is a known, rare, DEFERRED problem** demanding its own feature/design call. Carrying each source's key faithfully means the *same* real-world record admitted from *two* sources (a SAP→Odoo migration, or dual feeds into one entity) receives *two* stamps → double-count unless explicitly reconciled. This is correct default behaviour for a non-SoR: identity is naturally partitioned per SC/AC (the SO fact table changes when the SC/AC changes), so within-source is clean. Cross-source record merging is an explicit reconciliation feature, recorded here and deferred — not automatic, and not solved by this ADR.
- **Admission-side uniqueness via the identity key (deferred; enabled, not mandated).** Today admission is non-idempotent (immutable append-only observations) and repeat observations of a record are collapsed to one CO only at canonical resolution (`groupByIdentity` + latest-by selector). This platform has already been bitten by read-side double-counting from stale runs (SES-8f7232), fixed with a read-side selector, with admission-side uniqueness recorded as "the architectural follow-up." This ADR's natural-key identity is exactly the foundation that makes that follow-up expressible — a future option to upsert `fact.so_*` by the identity key so re-observation is idempotent-per-record — but it is not mandated here; the append-only/immutable-observation model stands until a separate ADR takes it up.
- **Day-granular watermarks should be the DEFAULT, not opt-in (deferred design + operational item).** The reader watermark (`entities.{E}.watermark:true` + `dateField`) is currently opt-in, and readers without it (e.g. the Kaveri Odoo reader today) full-fetch every run — re-observing the entire source each time. With admission non-idempotent, that accumulates duplicate observations in `fact.so_*` and yields a **false data landscape** (inflated observation counts, correctness resting entirely on read-time dedup) unless the identity collapse is flawless. The default should be a day-granular watermark on every reader/entity with a stable `dateField`, opt-*out* only with recorded justification. Recorded here as a design default + an immediate operational gap (Kaveri Odoo reader has no watermark).
- **The fiscal-dimension derivation is now load-bearing.** Point 2 is only true if the canonical fiscal resolver derives the period source-agnostically. This makes the companion decision below a **hard prerequisite**, not optional.

## Companion decision (named, separate)

The canonical fiscal resolver must be **source-agnostic**: derive the reporting fiscal period from the CC's declared posting-date field and the resolved legal entity's per-LE calendar, fail-closed on a missing calendar, and remove the SAP literal (`enrichFiscal` currently reads `resolvedLegalEntity ?? String(row['bukrs'] ?? '*')`; the `bukrs`/`'*'` fallback is deleted). Odoo `company_id`/`currency_id` many-to-one FKs must be dereferenced to codes at the reader/observation boundary (integer FKs are not codes; `direct`/`code_lookup` do not dereference). Authored as its own implementation decision so this doctrine ADR stays declarative.

## Live state and held remediation

The first text listed a global demotion of the document-fiscal-year concepts as a consequence "held for ratification". **That demotion was already executed** through governed BCF panel runs with certification. Read-only query of `concept_registry` in `bc_platform_dev`, 2026-09-24:

| Grain entity | Superseded (`identity_bearing`) | Active replacement (`descriptive`) | Executed |
|---|---|---|---|
| Customer Invoice | `9ccdca4a` document fiscal year | `07aa3b07` | 2026-09-23 14:45 UTC |
| Supplier Invoice | `3faa6c98` document fiscal year | `2f50d102` | 2026-09-23 14:46 UTC |

**Live identity-bearing sets:**
- **Customer Invoice:** `issuing_legal_entity` (`da984e53`) + `document number` (`2887850a`);
- **Supplier Invoice:** `recording_legal_entity` (`5fd47701`) + `document number` (`f5dd46ef`).

**What that means:**
- **Odoo (Kaveri):** by design, these sets cover the complete key `company_id + name` (legal entity ← `company_id`, document number ← `name`), which is correct under Decision 1.
  - **Not yet observed.** The Kaveri Customer Invoice and Supplier Invoice CO tables (`fact.co_cc_das36_v1_0_0`, `fact.co_cc_7174p_v1_0_0`) hold **0 rows** as of 2026-09-24, so no invoice CO has been resolved under this identity and V3 below is unproven.
- **SAP:** they do **not** cover `gjahr`. **Latent hazard.**
  - No SAP tenant database exists in the current environment: `tbc_pilot1_dev` has been retired, and the only tenant DB holding canonical objects is `tbc_kaveri_dev`.
  - **No SAP record has been resolved under the shortened identity.**

**Rule until remediated.** No chain may be resolved for a source whose key contains a component the grain entity's identity-bearing set does not cover. Today that means any SAP-sourced (or other year-recycling) Customer or Supplier Invoice. Onboarding such a source first lands the remediation.

**Remediation — a separate governed change, not authorized by this ADR:**
1. **Realize Decision 1 for mixed sources**, preferably by route (b), the governed opaque *source record key* (own ADR + mechanism). Restoring a universal year component would re-impose a year on sources whose key has none, which Decision 2 withdraws.
2. **Distinctness vectors, run against the actual resolver `groupByIdentity`**, required before any further identity-concept change and before any year-recycling source is resolved. Each must yield two distinct COs, or a refusal — never one CO:
   - **V1 (two years):** same company, same document number, two fiscal years;
   - **V2 (two companies):** same document number, same fiscal year, two companies;
   - **V3 (Odoo):** same `name` in two companies.
3. **Journal Entry** (`89462975` document number is its only identity-bearing concept) is observed to have the same gap for any multi-company or year-recycling source. It is recorded as a separate finding and is out of scope here.

**The Customer Invoice chain on Odoo** keeps identity = Odoo's own invoice key (`company_id + name`), with no fiscal-year concept, no carrier and no attestation. For that source, the onboarding blocker never existed.

## Evidence base (corpus reconciled)

Decided/implemented: DEC-f4e9a0 (composite identity — superseded here), DEC-beef5c/D489 (record-identity rulebook — amended here), DEC-acce2b (CC-v2 resolver), DEC-a8e8fc/D365 + DEC-d7e7a0/D364 (posting-date + per-LE fiscal calendar — the derived-dimension substrate), DEC-1efa47/D363 (grain honours declared source), DEC-3fe389/D560 (contract-identity: UUID sole authority, identity-tuple dedup — the stamp generalises its dedup rule to observed records), DEC-97bb94 (N:1 SO→CO by source business keys), DEC-4a17e0 (author-time O↔C concept-identity check). Doctrine: `foundation/the-invariants.md` (I/III/IV), `foundation/the-object-model.md` (SO source-keys vs CO business-identity keys), `operating-model/fiscal-time-and-temporal-gates.md` "Substrate Boundary" (Layer A reporting vs Layer B source-attested). Ungoverned-until-now: the `subsumed_by_carrier`/`identity_realization` mechanism (bc-core PR #698, D573 meta-schema sync) and the source-agnostic fiscal-resolver/m2o design memo — this ADR is the charter that reconciles both.
