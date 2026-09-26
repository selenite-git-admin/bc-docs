---
uid: DEC-7a8cbc
title: "Binding-realized issuer identity: a source-key component on the pinned primary leg may realize an identity-bearing issuer reference whose canonical value is the binding-resolved legal-entity code (amends DEC-a57eb8)"
description: "Adds a third bounded realization to DEC-a57eb8 Decision 1: the complete source-key component (e.g. Odoo company_id) on the pinned primary leg is the identity carrier for an identity-bearing issuer reference, and the canonical field carries the governed binding's legal_entity_code (d617-068 code-not-key); parity across authoring preflight, activation F4a and the resolver."
status: proposed
date: 2026-09-26T06:40:10.607Z
project: bc-core
domain: contracts
subdomain: concept-registry/identity
focus: identity
---

# Binding-realized issuer identity: a source-key component on the pinned primary leg may realize an identity-bearing issuer reference whose canonical value is the binding-resolved legal-entity code (amends DEC-a57eb8)

## Rationale (summary)

DEC-a57eb8 requires the complete source key, including the company component, while d617-068 requires the canonical issuer value to be the resolved legal_entity_code, not the source key. Neither of DEC-a57eb8's realizations (a) or (b) satisfies both, and today the Journal Entry grain resolves nothing. The raw key as identity carrier plus the resolved code as payload is the smallest governed rule that satisfies both. It is bounded to the one admitted binding mechanism on the primary leg, never a blanket derived-identity exemption. Rejected alternatives: demoting the concept's identity role (restating meaning to fit the machinery); a direct company_id mapping (source key as canonical value, contradicting d617-068); carrier subsumption under the document number (falsely claims entry numbers are unique across companies); dedup by resolved code (merges records the source keeps distinct).

## Context
DEC-a57eb8 makes an observed record's identity the source's COMPLETE natural key. It names the issuer/company component as identity-bearing (Odoo Journal Entry: company_id + name). It admits two realizations: (a) direct, where every source-key component maps to an identity-bearing concept through an OC field_mapping; (b) a governed opaque source-record key (named, not built).

RESPONSE-Codex-d617-068 fixed a second rule for the Journal Entry issuer reference, `recording_legal_entity` (concept 115b2945, minted identity_bearing in D623 7c-a). Its canonical value is the open legal_entity_code resolved through the governed source-legal-entity binding (DEC-c05551 / DEC-bacbf5, resolve_source_entity_binding, value_keyed). It is never the source key.

Realization (a) cannot satisfy both rules: a direct mapping of company_id to the reference concept would make the source key its canonical value. So the unamended code refuses both ways:
- activation F4a (`assertConceptsCoveredByPinnedLegs`) refuses cc-dh5d9 1.6.0;
- the canonical resolver (`buildIdentitySourceFields`, Unit0/F4) refuses every CC on the Journal Entry grain, including the active 1.5.0;
- the authoring preflight (`assertIdentityConceptsCoveredBySpec`) would refuse an equivalent chain spec.

Evidence: gen-e90cd0-01 and its RESPONSE (CHANGES REQUIRED R1), barecount-devhub f0f61e36 artifacts/d623/stage7c/7cc-design.

## Decision
1. **Realization (c): binding-realized issuer identity.** An identity-bearing REFERENCE concept R of the grain entity is realized, and therefore covered for identity, when all of the following hold in the SAME canonical contract body (or chain spec). Anything else is refused as uncovered, exactly as today.
   - (i) field_selection carries exactly one entry for R: binding_kind=reference, with R's frozen reference snapshot (reference_role, target_entity_id) **equal to the live registry concept's**, and no value-kind snapshot fields. The shared decision receives the authoritative registry facts and compares them itself (R1.c); presence alone never passes;
   - (ii) derivations[] carries EXACTLY ONE resolve_source_entity_binding derivation, and its output_business_concept_id = R;
   - (iii) its canonical_field equals R's field_selection canonical_field;
   - (iv) params.binding_kind = source_legal_entity AND params.mapping_shape = value_keyed; connection_scoped is NOT admitted under this realization;
   - (v) exactly one input, role raw_signal, whose observation_ref is the CC's single PRIMARY observation leg and whose source_field is present in that pinned OC version's so_schema;
   - (vi) no OC field_mapping on any pinned leg also maps R. A direct mapping and a binding realization of the same concept conflict and are refused.
   Secondary-leg carriers, arbitrary derivation functions, missing, duplicate or conflicting declarations, and a second resolve_source_entity_binding are all refused.
2. **Identity carrier (what groups records).** For a realized R, the resolver's identity key component is the tuple (primary admission run's connection_id, primary admission's source_contract id@version, raw value of the declared source_field). The source key is meaningful only inside its installation and source contract; that is the binding's own B2 scope.
   - The canonical payload field for R carries the binding-resolved legal_entity_code (d617-068).
   - The complete raw source key and its provenance stay in the CO business key and lineage (DEC-a57eb8 Decision 1 lineage).
   - Two different raw keys remain two different records even when their legal_entity_code is equal: records are never deduplicated or merged by the resolved code.
3. **Missing provenance or key (revised after RESPONSE-Codex-gen-e90cd0-02 R1.b).**
   - A row missing any runtime provenance its binding evidence is keyed on (connection_id, source contract id@version, observed_at, admission) **halts the resolution before any write**. No governed evidence can be bound to it, so nothing is resolved in that run (fail closed, never a silent skip).
   - A row whose declared raw key is null or empty forms no identity group. It is routed through the **governed** binding resolve, which records the existing refusal evidence (missing_source_key, or the declaration-level refusal) for that admission, tuple, key and observed time **before** the row is counted failed. It is never merged into a null-keyed group. Inability to record that evidence halts the run.
   - No new refusal reason and no DB change is needed.
4. **Time: the binding is as-of the CO's own admission (revised after R1.a).**
   - A group's CO is the canonical evaluation of its primary admission; every value field already comes from that row. Its legal_entity_code is the binding as-of **that admission's** stamped observed_at, resolved through the unchanged governed path: selection evidence before use, the lineage guard's 40001 stale-selection fence, and on retry the **whole payload re-derived** in a fresh transaction.
   - The other observations of the same record (same carrier tuple and identity components) contribute only group-scoped derivations, never the legal entity. Their outcomes are not inputs, so there is no group-wide agreement predicate to fence. The first proposal's read-only agreement check was withdrawn: it was not fenced through commit or retry and its refusals produced no governed evidence.
   - Which observation is primary follows the existing resolver rule and is unchanged here. The latest-by selector across repeat observations remains the deferred item DEC-a57eb8 names; this ADR claims no whole-history guarantee over the loaded subset.
   - Prior COs are immutable and are never relabelled (Invariant III).
5. **Parity.** One shared structural validator decides (1) and returns the realized set. It is used by all three consumers, which must agree:
   - the authoring preflight (AuthorObservationChainService → assertIdentityConceptsCoveredBySpec, evaluated against the spec's in-memory primary leg and so_schema);
   - activation (assertConceptsCoveredByPinnedLegs, against the persisted pinned primary OC version);
   - resolution (buildIdentitySourceFields → groupByIdentity, against the loaded pinned legs).
   The realized set joins the existing carrier-subsumed exemption. It is never a blanket exemption for derived identity concepts.
6. **What does not change.**
   - A CC that does not declare the realization (cc-dh5d9 1.5.0) stays refused at activation and resolution. It is not silently exempted; it retires by supersession.
   - Direct realization (a) is unchanged byte-for-byte.
   - The D431 O↔C rule and d617-068 are unchanged.
   - The canonical meta-schema v2 already expresses every declaration above, so no **structural** meta-schema change is needed.
   - **One description correction is needed, sequenced separately:** the `identity_realization` description in canonical-v2 says that, absent a realization entry, every identity-bearing concept must be directly mapped by a pinned leg. After this ADR that sentence is incomplete. Correcting it changes the governed meta-schema's canonical digest, so it is a governed meta-schema change (repo file `src/registry/meta-schemas/canonical-v2.schema.json` + the live `contract.contract_meta_schema` row through the two-principal change-request path, as B1 was). It is sequenced **after** this ADR is decided and after D623 7c-c (whose drivers pin the current digest a283410b), as its own reviewed unit. The live meta-schema is not touched by this ADR.
   - No DB change.
7. **Tests (against the real grouping and resolution path, not a lookalike helper):**
   - positive: same name in two companies gives two COs with their two codes;
   - two raw keys mapping to one legal_entity_code give two COs;
   - absent derivation: refused (1.5.0 shape);
   - wrong leg (secondary) or a field not in so_schema: refused;
   - connection_scoped: refused;
   - duplicate or conflicting declarations, or direct-plus-binding on R: refused;
   - null or empty key: refused row with governed refusal evidence recorded for that admission;
   - missing runtime provenance on any row: the run halts with no writes;
   - binding change between two observations of one record: one CO whose code is the as-of outcome of its own admission;
   - stale selection: a binding revision landing between the binding derive and the selection-evidence insert → the selection guard raises 40001, the stale insert rolls back and the binding is re-derived (one CO with the new code and revision);
   - a revision after selection: the governed binding writer **refuses** an outcome-changing revision effective at or before an already-selected observation, so the CO keeps its code and revision;
   - the lineage guard's 40001 and the resolver's whole-payload retry are a **backstop** that governed writers cannot reach given the rule above; that path is pinned by the atomicity unit test, not claimed as exercised end-to-end;
   - a keyless row whose binding outcome is an exhausted stale selection (no durable refusal) halts the run (evidence-or-halt);
   - a wrong reference snapshot: refused at preflight, activation and resolution;
   - same raw key under two connections: two groups;
   - direct-mapping CCs unchanged;
   - parity: the same fixture decided identically by all three consumers.

## Repair location and Foundation
- **Location B**, contract grammar (how an identity-bearing concept may be realized). It is not compensation below B: the concept's role (A) and the binding mechanism (DEC-c05551) are correct and unchanged.
- **Invariant I:** identity is still the source's own complete key, observed at admission.
- **Invariant III:** no CO is rewritten; a stale selection re-derives or refuses, never relabels.
- **Invariant IV:** the carrier and binding tuple are explicit, and time comes from observed_at stamps, never the clock.
- **Invariant VI:** selection evidence for every written CO, and refusal evidence for every refused keyless row, are emitted before use or count through the existing governed mechanism. A row to which no evidence can be bound halts the run.
