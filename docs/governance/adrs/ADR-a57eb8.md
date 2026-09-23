---
uid: DEC-a57eb8
title: "BareCount is not a system of record: canonical record identity is the faithful carry of the source's record key; fiscal period is a derived dimension, never identity"
description: "Observed records carry a deterministic stamp over the source's own natural key (observed, not established); fiscal year/period is a derived metric dimension, never identity. Supersedes DEC-f4e9a0's composite identity; amends DEC-beef5c/D489."
status: decided
date: 2026-09-23T13:53:46.971Z
project: bc-core
domain: contracts
subdomain: concept-registry/identity
focus: identity
supersedes: DEC-f4e9a0
---

# BareCount is not a system of record: canonical record identity is the faithful carry of the source's record key; fiscal period is a derived dimension, never identity

## Context

Every record BareCount observes needs a stable per-record identity — to deduplicate repeated observations, to anchor metric grain, and to carry evidence lineage. This ADR settles, once, **how that identity is formed when the same business record is admitted from heterogeneous source systems** whose native keys differ.

The platform accumulated a large apparatus around this question:

- **DEC-f4e9a0 (implemented)** modelled a Customer Invoice's canonical identity as a *system-agnostic composite* — `{issuing Legal Entity (reference), document number, document fiscal year (source-attested, GJAHR)}` — on one empirical fact: SAP `belnr` recycles per fiscal year (`(bukrs,belnr,gjahr)`=1716 distinct vs `(bukrs,belnr)`=1162), so a year discriminator was deemed "required."
- **DEC-beef5c / D489 (decided)** generalised that into a three-class record-identity rulebook, with Class-1 DOCUMENT identity = `{customer, legal entity, fiscal year, document number}`.
- To realise a *source-attested* fiscal year on a source with no such field (Odoo `account.move`), an **identity-carrier mechanism** was built — `identity_realization[] subsumed_by_carrier` with a mandatory per-installation attestation (bc-core PR #698, D573 meta-schema sync) — governed only by an external-audit exchange, **with no ADR**.
- The fiscal-time doctrine (`operating-model/fiscal-time-and-temporal-gates.md`, "Substrate Boundary") kept two fiscal years in tension: a **source-attested** identity year (SAP `GJAHR`) versus the **resolver-stamped reporting** fiscal year (Layer A, derived from posting date + tenant calendar), warning that conflating them is a "category error."

The trigger: onboarding a Customer Invoice chain over real Odoo data (Kaveri, `v3_lc5`) stalled at the identity preflight — Odoo has no `GJAHR`-equivalent field, forcing the half-built carrier+attestation path, which even once authored cannot yet evaluate (its attestation substrate + resolution-time resolver are unbuilt). Grounding: all 2,714 Kaveri customer invoices already carry the fiscal year *inside* the `l10n_in` document number (`INV/26-27/0316`), globally unique, zero cross-year reuse — the year is already part of the source's own key, not a thing the platform must attest.

## The reframe that dissolves the problem

**BareCount is not a system of record.** A system of record must *establish and guarantee* a record's identity — which is why SAP needs `bukrs+belnr+gjahr` and reasons about `belnr` recycling. BareCount **observes and references**; the source already owns identity and uniqueness. The entire apparatus above solves a problem the platform does not have: it re-engineers a canonical business identity as if the platform were the authoritative keeper of the record. It is not. The complexity became self-justifying — once the composite-identity / source-attested-fiscal-year / carrier-subsumption / attestation machinery existed, a simpler account felt untrustworthy. It is not naive; it is what remains once the system-of-record assumption is removed.

## Scope

This ADR governs the identity of **observed / admitted records** — canonical objects that are the platform's faithful projection of a source-system record (a document, a master row). It does **not** change the identity of **derived / computed canonical objects** — metric snapshots, action objects — which are genuinely the platform's own and keep their platform-established identity (grain + formula + period; DEC-3fe389/D560, D068).

## Decision

1. **An observed record's canonical identity is the source's own natural key, declared where meaning is owned.** Which grain-entity concepts *are* identity is declared in the BCF registry (`identity_role = identity_bearing`); the Observation Contract maps those concepts to the source fields the source system itself uses to identify the record (SAP `bukrs+belnr+gjahr`, Odoo `company_id + name`); and the canonical resolver keys each Canonical Object on exactly those concepts (`groupByIdentity` over the identity-bearing set — never an invented composite). This is a **composite key over the declared identity concepts** — which is what the resolver does today, at zero added computation. A **SHA-256 stamp over that composite is an OPTIONAL uniform realization** — a fixed-size opaque key for wherever cross-source uniformity earns its keep — **not required** for correctness or dedup (the composite key already suffices; the hash cost is negligible either way, so it is a convenience choice, not a mandate). The raw source key values are carried as descriptive/lineage fields. The platform **observes** this identity; it never re-establishes, re-decomposes, or re-guarantees uniqueness — the source (the system of record) owns that.

2. **Fiscal year and fiscal period are a derived dimension, for metric periodisation only, and are never an identity component** — for every entity and every source. They are resolved at canonical evaluation from the CC's declared posting-date field plus the tenant's **per-legal-entity fiscal calendar**. **Declaring that per-legal-entity fiscal calendar is mandatory and blocking at onboarding** — no tenant/chain proceeds without it; a missing calendar fails closed, never a `'*'` fallback. The source system's own fiscal year (SAP `GJAHR`, the year embedded in the Odoo document number) is retained as a **descriptive / source-reconciliation control** field (§11.6 Layer B), never as identity.

3. **The only purpose of a canonical per-record key is deduplication of repeated observations, metric grain, and evidence lineage** — all three satisfied by the stamp in point 1. No further identity engineering is warranted.

4. **Source-agnosticism lives at the grain, not the key.** A metric is defined over a system-agnostic entity/grain (e.g. Customer Invoice); the per-record key is the source-carried stamp. This is more source-agnostic than a re-engineered universal identity schema, not less — no source is forced to synthesise an identity field it does not natively hold.

5. **Fail-closed, never fabricate.** If a source yields no natural key that identifies its own records, admission refuses; the platform never invents identity from mutable or derived values (Invariant I; preserves the DEC-beef5c guard against composite identity from mutable fields). The stamp must be taken over the source's *stable* key; where a source stabilises its business key late (e.g. an unposted Odoo draft), the record's stable source reference is used.

## Repair location & Foundation

- **Location B (contract grammar / declared identity) + A (what the source emits).** Identity is declared as the carried source key at the boundary where meaning is owned — not re-engineered downstream.
- **Invariant I:** identity is observed at admission from the source's own key, not invented at evaluation or reconstructed by inference.
- **Invariant III:** the stamped source key is immutable per record; a fiscal year derived from mutable tenant-calendar config is correctly excluded from identity and confined to the reporting dimension (stamped into the immutable CO/snapshot at resolution — a later calendar correction yields new snapshots, never rewrites old).
- **Invariant IV:** the canonical record explicitly references the source record by the declared key stamp. Nothing implicit.
- **Object model:** honoured — "a Canonical Object is identified by business identity keys, deterministic from the recorded inputs and the governed contract version." The business identity key is the deterministic key over the faithfully-carried source key; system-agnosticism is achieved per-contract without a universal cross-source identity schema (the earlier over-reach).

## Alignment with Reader & Evaluation mechanics (verified)

This doctrine matches the running engine; it is realized by a concept-registry change, not an engine rewrite.

- **Canonical resolver** (`ccv2-canonical-resolver.service.ts`) already keys COs on the grain entity's `identity_bearing` concepts (`loadIdentity` → `groupByIdentity`) and **stamps fiscal period as a derived dimension**, emitting one CO per grain instance. Demoting the fiscal-year concept from `identity_bearing → descriptive` therefore makes the resolver key on `(document number, legal entity)` automatically — no resolver code change.
- **Reader** fetches the declared source fields into `fact.so_*`; identity grouping happens later at the resolver — unaffected by this ADR.
- **Admission is deliberately non-idempotent** — every admission is a distinct immutable observation act (Invariant V). "Same record not observed twice" is therefore **not** an admission guarantee; repeat observations of the same record are collapsed to **one CO at canonical resolution, by this identity** (`groupByIdentity` + a governed latest-by selector; version-scoped idempotency `UNIQUE(admission_id, CC version)`). This identity *is* the dedup key — which is the strongest confirmation that it must be the source's natural key.

## Supersession & amendment

- **Supersedes DEC-f4e9a0's identity model** — the `{Legal Entity, document number, document fiscal year}` composite and the "document fiscal year as source-attested identity." **Retains** the Legal Entity entity and the record→Legal-Entity reference, re-cast as a **descriptive dimension** (it anchors the per-LE fiscal calendar and roll-ups — useful, not an identity the platform must guarantee).
- **Amends DEC-beef5c / D489** — removes fiscal year from Class-1 DOCUMENT identity; the source's own natural key (stamped) is the identity, fiscal year is a derived dimension. The additive-first posture and the "never fabricate identity from mutable fields" guard are retained and reinforced.
- **Retires the `subsumed_by_carrier` + per-installation-attestation apparatus for identity/fiscal-year.** The mechanism (PR #698, D573 meta-schema) stays in the substrate but is dormant for this purpose — there is no fiscal-year identity to carry. A genuine future fused-identity case that is *not* a category error may re-charter it by a separate ADR.

## Known bounded consequences & deferred items

- **Cross-source same-record identity is a known, rare, DEFERRED problem** demanding its own feature/design call. Carrying each source's key faithfully means the *same* real-world record admitted from *two* sources (a SAP→Odoo migration, or dual feeds into one entity) receives *two* stamps → double-count unless explicitly reconciled. This is correct default behaviour for a non-SoR: identity is naturally partitioned per SC/AC (the SO fact table changes when the SC/AC changes), so within-source is clean. Cross-source record merging is an explicit reconciliation feature, recorded here and deferred — not automatic, and not solved by this ADR.
- **Admission-side uniqueness via the identity key (deferred; enabled, not mandated).** Today admission is non-idempotent (immutable append-only observations) and repeat observations of a record are collapsed to one CO only at canonical resolution (`groupByIdentity` + latest-by selector). This platform has already been bitten by read-side double-counting from stale runs (SES-8f7232), fixed with a read-side selector, with admission-side uniqueness recorded as "the architectural follow-up." This ADR's natural-key identity is exactly the foundation that makes that follow-up expressible — a future option to upsert `fact.so_*` by the identity key so re-observation is idempotent-per-record — but it is not mandated here; the append-only/immutable-observation model stands until a separate ADR takes it up.
- **Day-granular watermarks should be the DEFAULT, not opt-in (deferred design + operational item).** The reader watermark (`entities.{E}.watermark:true` + `dateField`) is currently opt-in, and readers without it (e.g. the Kaveri Odoo reader today) full-fetch every run — re-observing the entire source each time. With admission non-idempotent, that accumulates duplicate observations in `fact.so_*` and yields a **false data landscape** (inflated observation counts, correctness resting entirely on read-time dedup) unless the identity collapse is flawless. The default should be a day-granular watermark on every reader/entity with a stable `dateField`, opt-*out* only with recorded justification. Recorded here as a design default + an immediate operational gap (Kaveri Odoo reader has no watermark).
- **The fiscal-dimension derivation is now load-bearing.** Point 2 is only true if the canonical fiscal resolver derives the period source-agnostically. This makes the companion decision below a **hard prerequisite**, not optional.

## Companion decision (named, separate)

The canonical fiscal resolver must be **source-agnostic**: derive the reporting fiscal period from the CC's declared posting-date field and the resolved legal entity's per-LE calendar, fail-closed on a missing calendar, and remove the SAP literal (`enrichFiscal` currently reads `resolvedLegalEntity ?? String(row['bukrs'] ?? '*')`; the `bukrs`/`'*'` fallback is deleted). Odoo `company_id`/`currency_id` many-to-one FKs must be dereferenced to codes at the reader/observation boundary (integer FKs are not codes; `direct`/`code_lookup` do not dereference). Authored as its own implementation decision so this doctrine ADR stays declarative.

## Consequences (held for ratification)

- Demote `document fiscal year` (`9ccdca4a`, Customer Invoice) and its Supplier-Invoice / Journal-Entry-Line / GL-Account equivalents from `identity_bearing` → descriptive dimension (governed BCF concept change; mirrors the already-done demotion of the customer concept to descriptive `bill_to`).
- The Customer Invoice chain simplifies to identity = a stamp over Odoo's own invoice key (`company_id + name`) — no fiscal-year concept, no carrier, no attestation. The onboarding blocker never existed.

## Evidence base (corpus reconciled)

Decided/implemented: DEC-f4e9a0 (composite identity — superseded here), DEC-beef5c/D489 (record-identity rulebook — amended here), DEC-acce2b (CC-v2 resolver), DEC-a8e8fc/D365 + DEC-d7e7a0/D364 (posting-date + per-LE fiscal calendar — the derived-dimension substrate), DEC-1efa47/D363 (grain honours declared source), DEC-3fe389/D560 (contract-identity: UUID sole authority, identity-tuple dedup — the stamp generalises its dedup rule to observed records), DEC-97bb94 (N:1 SO→CO by source business keys), DEC-4a17e0 (author-time O↔C concept-identity check). Doctrine: `foundation/the-invariants.md` (I/III/IV), `foundation/the-object-model.md` (SO source-keys vs CO business-identity keys), `operating-model/fiscal-time-and-temporal-gates.md` "Substrate Boundary" (Layer A reporting vs Layer B source-attested). Ungoverned-until-now: the `subsumed_by_carrier`/`identity_realization` mechanism (bc-core PR #698, D573 meta-schema sync) and the source-agnostic fiscal-resolver/m2o design memo — this ADR is the charter that reconciles both.
