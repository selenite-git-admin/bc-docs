---
uid: DEC-6c57e2
title: "Legacy Vocabulary Stack Quarantine — BF/BO/CF/CM physically retained, semantically non-authoritative"
description: "Operationalizes the quarantine of the legacy BF/BO/CF/Canonical Mapping stack after the BCF backend + UI MVPs. Physically retained for operational continuity only; semantically non-authoritative. Hard prohibition on all reads of quarantined surfaces by BCF/MCF authoring — including for \"weak inspiration\". Carves out bc-seed, Source/Admission/Observation Contracts, source-reality evidence, and KPI catalog as intent. End condition pins the trigger for a future physical-disposition DBCP. No deletion, no migration, no bridge in this ADR."
status: decided
date: 2026-05-25T01:41:05.908Z
project: bc-docs
domain: contracts
subdomain: catalog
focus: lifecycle
---

# Legacy Vocabulary Stack Quarantine — BF/BO/CF/CM physically retained, semantically non-authoritative

## Context

The legacy BF/BO/CF/CM stack is not merely "older" than the BCF Registry; it is actively contaminated. ADR DEC-02f5a9 §3 declared the legacy vocabulary identity model unsound (permits duplicate concepts and merged concepts; both violate Foundation Invariant I). The gap-research pass surfaced specific contamination vectors (FieldMappingService.suggest as state-blind, alias-overwrite bug, MetricWizardService quarantine, etc.). DEC-02f5a9 §4 rejected a name-string compatibility shim as "lower-layer compensation for an upper-layer semantic gap, forbidden by the Foundation invariant gate. A shim is the corruption preserved, not a fix."

DEC-02f5a9 + DEC-65dc86 set the architectural decision and the direction. Neither pinned the operational prohibition surface sharply enough to prevent the sunk-cost trap — the human and tooling tendency to "rescue" existing work by reading it, drawing lineage from it, or "lightly converting" it. Every such attempt creates the lower-layer compensation the Foundation invariant gate forbids; every such attempt re-introduces the contamination DEC-02f5a9 §4 was designed to prevent.

This ADR closes the channels: substrate (no bridge / mapping / lineage tables); panel (PE1 / PE-MC-1 cannot cite quarantined rows); code (future bc-qa rule + CLAUDE.md guardrail); and crucially the human read-channel (no "weak inspiration" reads). The hard read prohibition is the load-bearing addition — substrate checks alone cannot prevent an operator from reading a quarantined row's prose and unconsciously reproducing its meaning in a new BCF candidate.

The carve-outs (§5) are explicit because they are structurally similar to the quarantined surfaces (catalog rows, semantic content, AI-tooling-adjacent) but on the opposite side of the contamination line: bc-seed is curated, source-reality contracts reference source fields rather than vocabulary, KPI catalog metric intent is operator knowledge distinct from the discarded bindings. Without explicit carve-outs, an over-zealous reader could quarantine these too and lose the legitimate evidence inputs DEC-02f5a9 §5 preserved.

The end condition (§6) is structural rather than temporal because the trigger is the absence of quarantined references in active runtime artifacts. A date-based trigger would invite the wrong pressures (rush to delete vs. delay forever); a structural trigger ties retirement to the completion of MCF re-authoring, which is the only path that produces a Foundation-correct replacement.

This ADR does not delete, migrate, or build a bridge. It locks the rule that prevents BCF/MCF from accidentally inheriting the contamination, and names the future gates that operationalize the rule. The first three sketches in the BCF arc (DEC-02f5a9, MCF Foundation Requirements sketch a967970, BCF Greenfield Enrichment Plan sketch c0aeade) jointly provide the boundary positions this ADR needs to be sharp.

## Context

The BCF Business Concept Registry backend MVP is complete (close-out `589a07d` + amendment `b0f3fcf`). The BCF operator console MVP is complete (UI-S1 → UI-S5; close-out `faf1914`; first UI-driven publication proven by `cycle time` `7042ca4f-…`). The MCF Foundation Requirements sketch is filed (`a967970`). The Greenfield BCF Enrichment Plan sketch is filed (`c0aeade`).

The legacy vocabulary / identity / mapping stack — Business Field (BF), Business Object (BO), Canonical Field (CF), Canonical Mapping including `cc_field_mapping` (CM), and BF/BO/CF/CM-derived bindings inside the old canonical and metric chain artifacts — remains physically present in `bc_platform_dev` and backs the active runtime: `contract.canonical_contract.object_id`, `contract.cc_field_mapping.business_field_id`, `contract.observation_field_map.business_field_id`, `runtime.reader.business_object_id`, plus the BF/BO supersession / alias / object-field / object-relation tables. Thirteen FK edges, 7,072 BF rows, 203 BO rows.

ADR DEC-02f5a9 §3 declared the legacy vocabulary identity model unsound (it permits duplicate concepts and merged concepts; both violate Foundation Invariant I) and §4 mandated greenfield rebuild with no compatibility shim, explicitly rejecting a name-string shim as *"lower-layer compensation for an upper-layer semantic gap, forbidden by the Foundation invariant gate. A shim is the corruption preserved, not a fix."* §6 sequenced cutover: *"three primitive identity surfaces are retired or compatibility-wrapped during cutover; physical table disposition is a later DBCP."*

ADR DEC-65dc86 (D416) set the operational direction: BCF forward governance model; BF/BO legacy compatibility; new product investment moves to BCF; retirement requires a later multi-PR program.

What neither ADR enumerated sharply enough is the operational prohibition surface that prevents accidental re-contamination through migration thinking. The sunk-cost pull — "rescue what exists" — is exactly the trap that creates the lower-layer compensation DEC-02f5a9 §4 forbids. The MCF + BCF Enrichment sketches surfaced concrete examples of where the boundary needs to be locked: PE1 evidence sources, route-to-MCF tests, KPI catalog reads, panel grounding citations, "weak inspiration" reads by humans.

This ADR locks the operational rule formally. It is not a re-decision of DEC-02f5a9 or DEC-65dc86; it is the operational interpretation those decisions deliberately deferred to a follow-on, made explicit so future operators, future code, and future AI agents cannot accidentally re-introduce contamination by reading their way into a "rescue" path.

## Decision

### §1 The rule

**BF/BO/CF/CM are physically retained for operational continuity but semantically quarantined.** They are non-authoritative residue.

### §2 Precise quarantine scope

The quarantine covers, exactly and exhaustively:

- `contract.business_field`
- `contract.business_object`
- `contract.business_field_alias`
- `contract.business_object_field`
- `contract.business_object_relation`
- `contract.canonical_field`
- `contract.cc_field_mapping`
- `contract.observation_field_map.business_field_id` (column-level scope on this otherwise non-quarantined table)
- BF / BO / CF / CM-derived bindings inside old canonical and metric chain artifacts

Tables not listed above are not in this quarantine scope. New BCF / MCF substrate tables (`concept_registry.entity`, `concept_registry.business_concept`, `concept_registry.characteristic`, and their version / supersession / authoring-cert tables) are explicitly not quarantined — they are the forward model.

### §3 Prohibitions

Quarantined surfaces must not be used by BCF or MCF authoring as:

- evidence
- candidate source
- lineage
- bridge
- migration input
- mapping source
- compatibility shim
- design input
- **weak inspiration**

**Hard read prohibition.** New BCF / MCF authoring code paths must not read quarantined surfaces. The B6 / MCF panels' PE1 / PE-MC-1 grounding traces must not cite quarantined rows. An operator must not read a quarantined row's prose to "remind themselves" what a concept means while authoring a BCF or MCF candidate — even read-only inspection for inspiration is prohibited. The operator must reach an external standard, a `bc-seed` entry, or a source-reality observation for inspiration. This closes the human read-channel that no substrate check can fully prevent.

**No conversion.**
- No CF → BusinessConcept conversion (the source-side / canonical-side split is collapsed per DEC-02f5a9 §2; converting reintroduces it).
- No BF → Characteristic or BF → BusinessConcept conversion.
- No BO → Entity conversion.

**No bridge.** No lineage table, no mapping table, no bridge table, no compatibility shim, no cross-reference index that resolves a quarantined identifier to a BCF / MCF identifier. This is the §4 shim DEC-02f5a9 already forbade, named again at the operational layer.

### §4 Operational continuity

"Operational continuity" means existing runtime paths continue resolving as-is. Specifically:

- The canonical evaluation boundary may continue reading active CCs that reference BO ids; the active CCs run unchanged.
- The metric evaluation engine may continue reading active MCs that reference BF ids via `cc_field_mapping`; the active MCs run unchanged.
- Observation field maps may continue reading active OCs that reference BF ids via `observation_field_map.business_field_id`; the active OCs run unchanged.
- `runtime.reader` may continue binding to `business_object_id` for active reader configurations; the active readers run unchanged.

It does **not** mean:

- Make the legacy stack better, easier, more usable, more integrated.
- Add new features, new endpoints, new UI, new wrappers, new helpers to the legacy stack.
- Extend the legacy stack with new rows produced by greenfield authoring (greenfield BCF / MCF rows must not be back-written into BF/BO/CF/CM).
- Refactor or modernize the legacy stack as a step toward retirement (refactoring is implicitly retention; the path is replacement, not improvement).

The legacy stack receives maintenance fixes only when a maintenance fix is the smallest change that keeps the runtime resolving. Anything beyond that is implicit investment in what this ADR declares non-authoritative.

### §5 Carve-outs — surfaces explicitly NOT in quarantine

The following surfaces are not quarantined. They may be used as BCF / MCF authoring inputs under the discipline named:

- **`bc-seed` catalog entries** with verifiable provenance lineage. Per ADR DEC-02f5a9 §5 (*"Source registration / seed catalogs — Survive — source knowledge and candidate inputs"*) and per BCF Enrichment sketch §6.2. bc-seed is structurally similar to BF/BO/CF (catalog rows, semantic content, AI-tooling-adjacent) but is on the *opposite* side of the contamination line — curated, evidence-bearing, never authored at the contamination scale BF/BO/CF was. bc-seed is BCF PE1 (b) evidence source.
- **Source Contract family.** Per DEC-02f5a9 §5 (*"Source Contract / Admission Contract — Survive — source-reality contracts; reference source fields, not vocabulary"*).
- **Admission Contract family.** Same.
- **Observation Contract family**, as source-reality / observation evidence. Per DEC-02f5a9 §5 (*"Observation Contract family — Survives. Existing OC versions are re-authored against Registry Business Concepts because their `observation_field_map` binding target changes from `Business Field` to `Business Concept`. Only the target vocabulary changes; the source→concept binding act is unchanged."*). Note: the OC's `observation_field_map.business_field_id` column itself is in quarantine scope per §2; the OC family as a contract artifact is not.
- **Source-system observations and source-reality evidence** — `source_system`, `source_table`, `source_field`, raw observed values. These are admission-side data, not vocabulary. BCF PE1 (c) evidence source.
- **KPI catalog metric definition knowledge as operator intent** — `contract.metric_definition` + `metric_definition_knowledge`. Per DEC-02f5a9 §5 (*"Metric definitions / knowledge (the KPI catalog) — Survive as knowledge — only the binding to concepts is rebuilt"*). MCF authoring may read: metric name, prose definition, owner, thresholds, formula prose, references. MCF authoring may **not** read: the BF/CF binding fields on those rows (which are the discarded bindings DEC-02f5a9 §5 names). The intent survives; the bindings do not.
- **Contract body knowledge** — resolution rules, type coercion, unit conversion, temporal interpretation, reduction-over-grain. Per DEC-02f5a9 §2 (*"Field-resolution logic survives where it is genuinely real. Type coercion, unit conversion, reduction over grain, and temporal interpretation remain authored content within the Observation and Canonical Contracts"*). These may be re-authored into future governed OC / CC / MCF bodies; they must not be inherited as authority from the discarded CC / Canonical Mapping rows.

### §6 End condition

The quarantine compatibility period ends when no active Canonical Contract, active Metric Contract, active Observation Contract, active reader, or active metric runtime path carries a reference to any quarantined surface.

That condition opens a future physical-disposition DBCP. The DBCP is its own gate, with its own DDL review and DB approval. **This ADR does not delete or migrate anything.**

Reaching the end condition is the work of MCF re-authoring the active metric chain against BCF objects (per DEC-02f5a9 §5 cleavage plane and MCF sketch §3.5). It is not BCF Enrichment's work; BCF Enrichment supplies the vocabulary MCF re-authoring binds to.

Until the end condition is reached, the quarantine compatibility window remains open. The window has no time limit imposed by this ADR — the trigger is structural (no quarantined references in active runtime artifacts), not temporal.

## Consequences

- **BCF / MCF authoring cannot consume quarantined surfaces.** Panel grounding, candidate intake, evidence citations, lineage traces, design inspiration — all closed channels.
- **Runtime remains stable.** The active CC / MC / OC / Reader chain continues to resolve through the legacy stack until MCF re-authors each binding against BCF objects.
- **Metric intent may survive without preserving old bindings.** The KPI catalog's prose, owners, thresholds, and intent are operator knowledge that MCF re-authoring inherits; the BF / CF references on those rows are the discarded bindings.
- **Physical deletion is deferred.** No row is dropped, no table is renamed, no FK is broken by this ADR. Physical disposition is the future DBCP triggered by §6's end condition.
- **No bulk migration program is authorized.** A future operator-opened gate may design a per-binding re-authoring plan (per DEC-02f5a9 §6 sequencing), but that plan must produce BCF objects through the proven B6 / C5 / B10 path — not bulk-import quarantined rows.
- **The legacy compatibility window has no time limit set by this ADR.** It is structurally bounded by the end condition (§6), not by a date. The full Greenfield BCF Enrichment Plan and the full MCF Foundation Requirements doc will jointly determine the per-binding sequencing.
- **Sunk-cost framing is rejected.** Existing BF/BO/CF/CM work that does not survive the carve-outs (§5) is treated as already lost cost. Attempting to recover that cost by reading, inspiring from, lineage-bridging, or "lightly converting" quarantined rows risks contaminating the clean BCF/MCF model. The rejection is operational, not philosophical: every such attempt is a §3 prohibition violation.

## Guardrails / follow-ons (named, not implemented in this ADR)

This ADR records the decision. Enforcement and tooling are separate later gates:

1. **CLAUDE.md addition** (`barecount-devhub/CLAUDE.md`): "Don't read BF/BO/CF/CM for BCF/MCF authoring." Future gate to add this rule under the existing repo guardrails.
2. **bc-qa rule** (`bc-qa` repo): detect imports / reads from quarantined surfaces in BCF/MCF authoring paths (specifically the `bc-core/src/registry/concept-registry/`, `bc-core/src/registry/registry-authoring-panel/`, and future `bc-core/src/registry/mcf/` paths). The full bc-qa rule design is its own gate; this ADR names the rule as required follow-on. (Cross-referenced from MCF sketch §15.9 Q27.)
3. **PE1 / PE-MC-1 substrate-level citation check.** The B6 panel currently enforces PE1 no-fabrication at the panel-prompt layer; a substrate-level check on grounding citation URIs (rejecting URIs that resolve to quarantined tables) is a hardening follow-on. (Cross-referenced from MCF sketch §15.9 Q28 and BCF Enrichment sketch §6.1.)
4. **Full Greenfield BCF Enrichment Plan.** Expands the sketch `c0aeade`. Defines per-unit candidate lists, the cross-framework signal mechanics, the operator-confirm override rationale shape for §7 route-to-MCF rejects, and the substrate prerequisite gates.
5. **Full MCF Foundation Requirements doc.** Expands the sketch `a967970`. Settles MCF identity model, formula AST normalization rules, computed dimension taxonomy, authority model, lifecycle, PE-MC contract, substrate, panel mechanics, publication path, and UI design — each a multi-week design arc.
6. **KPI catalog read discipline doc.** Operationalizes §5's "intent survives, bindings do not" rule for MCF authoring — exact column allow-list on `contract.metric_definition` + `metric_definition_knowledge`, query patterns, prohibition enforcement. (Cross-referenced from BCF Enrichment sketch §11.7 Q14.)

None of these follow-ons are authorized by this ADR. Each is its own future operator-opened gate.

## Non-goals

This ADR explicitly does not:

- Delete any BF, BO, CF, or CM row.
- Migrate any BF, BO, CF, or CM row into a BCF object.
- Build a bridge table, mapping table, or compatibility shim between the legacy stack and BCF/MCF.
- Implement any BCF Enrichment work (vocabulary authoring is the full Enrichment Plan's job).
- Implement any MCF work (MCF substrate, panel, publication, UI are all MCF program work).
- Change any UI surface.
- Enforce any of the §3 prohibitions in code (the bc-qa rule, the PE1 substrate-level check, and the CLAUDE.md guardrail are separate future gates).
- Set a calendar date for the end of the quarantine compatibility window — §6's trigger is structural.
- Re-decide DEC-02f5a9 or DEC-65dc86 / D416.

## Relationship to prior decisions

- **Operationalizes DEC-02f5a9** (Business Concept Registry adoption + greenfield rebuild + cleavage plane + cutover sequencing). DEC-02f5a9 §4 + §6 named what must happen; this ADR names what must not be done in the meantime.
- **Stands alongside DEC-65dc86 / D416** (BCF forward / BF/BO legacy compatibility). D416 set direction; this ADR locks the operational rule. Does not supersede D416 — different abstraction levels. D416's status remains `decided`.
- **Does not supersede any ADR.** No prior ADR is reversed, superseded, or amended by this decision.
- **Aligns with DEC-26b6e2 / D415** (Immutable Characteristic Atoms). The atom discipline DEC-26b6e2 imposes on Characteristics is the same discipline this ADR imposes on the quarantine boundary — meaning is locked at the boundary, not reconstructable from contaminated sources.
