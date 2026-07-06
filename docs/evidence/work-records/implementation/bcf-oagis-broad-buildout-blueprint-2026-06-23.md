---
title: BCF × OAGIS Broad Buildout Blueprint (2026-06-23)
description: Operator-authorised blueprint and target backlog for using the enriched OAGIS finance extract (133 nouns / 6,131 fields / 49 subfunctions) to systematically expand the Business Concept Registry beyond the current finance-rich substrate (26 active entities / 63 characteristics / 194 active BCs). Records the bridge model OAGIS → BCR, the six-bucket pre-admission filter taxonomy, the comprehensive target catalogue, the natural 14-wave sequence with GREEN/AMBER/RED classification, the persistent retry ledger design, the recommended first three waves with stated pull demand, and the autonomous safe-mode policy. The load-bearing rule from orphan-inventory §8 — orphans are vocabulary capacity, not a triable backlog; BCF activation requires concrete pull — governs the whole document.
status: held
authority: implementation-blueprint
date: 2026-06-23
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-buildout
related_docs:
  - business-concept-registry.md
  - business-concept-registry-vocabulary-evidence-framework.md
  - bcf-backbone-breadth-and-batch-doctrine.md
  - bcf-characteristic-scope-audit-2026-06-23.md
  - bcf-orphan-characteristic-decision-inventory-2026-06-23.md
  - bcf-wave-a-supplier-invoice-header-parity-closeout-2026-06-23.md
  - bcf-wave-b-fast-track-parity-closeout-2026-06-23.md
  - bcf-grounding-recheck-2026-06-23.md
  - ADR-fb0b12.md
  - ADR-02f5a9.md
---

# BCF × OAGIS Broad Buildout Blueprint (2026-06-23)

> **What this is.** Operator-authorised blueprint and target backlog for using
> the enriched OAGIS finance extract
> (`barecount-devhub/data/oagis-finance-extract-enriched-2026-05-15.json`) to
> systematically expand the Business Concept Registry beyond the current
> finance-rich substrate. The document defines the bridge model, the six-bucket
> pre-admission filter, the comprehensive target catalogue, the natural wave
> sequence, the persistent retry ledger, the recommended first three waves, and
> the autonomous safe-mode policy.
>
> **What this is not.** Not a panel run. Not a DB write. Not a characteristic
> amendment. Not a supersession proposal. Not a PR. Not code. Blueprint and
> backlog only.

## 0. Provenance + scope

### 0.1 Authority chain

| Layer | Source | Role |
|---|---|---|
| **Foundation** | `bc-docs-v3/docs/foundation/the-invariants.md`, `the-object-model.md`, `the-contract-grammar.md` | The six invariants, the six object types, the twelve grammar artifacts. Locked. |
| **BCR identity model** | DEC-02f5a9 (Business Concept Registry, decided 2026-05-21); `business-concept-registry.md` | `entity.property` is the only addressable concept identity. Standards are evidence, never identity authority. |
| **BCF admission rubric** | `business-concept-registry-vocabulary-evidence-framework.md` v1 + §11 amendment 2026-06-19 | Bounded evidence corpus (T1–T5 + OUT); Vocabulary Admission Checklist v1 MUST/SHOULD/MAY; system-agnosticism + characteristic hygiene; canonical-vs-source-diagnostic substrate role; source-attested-vs-resolver-stamped boundary. |
| **BCF backbone doctrine** | `bcf-backbone-breadth-and-batch-doctrine.md` | Complete-enough vs complete; coherent slice vs item-count; one slice per session; continue-to-exhaustion. |
| **BCF amendment doctrine** | DEC-fb0b12 (Editorial Amendment refinement of DEC-26b6e2, decided 2026-06-23) | Six-condition editorial test E1–E6; supersession is the safe path; default-to-supersession under uncertainty. |
| **Operative pull rule** | `bcf-orphan-characteristic-decision-inventory-2026-06-23.md` §8 amendment | Orphans are vocabulary capacity, not a triable backlog. Admission requires concrete pull. |
| **Live substrate** | `concept_registry.*` read-only via bc-postgres MCP, snapshot 2026-06-23 | 29 entities (26 active, 3 superseded), 63 characteristics (62 active, 1 draft `fiscal period`), 203 BCs (194 active). |
| **OAGIS seed** | `barecount-devhub/data/oagis-finance-extract-enriched-2026-05-15.json` | 133 nouns, 6,131 fields, 49 subfunctions, 25 shared components. Pre-enriched with `semantic_role`, `representation_term`, `data_type`, `bf_name` candidate, OAGIS 10.12 source description. Tier-T2 cross-enterprise authority per Vocabulary Evidence Framework §2. |

### 0.2 What this blueprint covers

Twelve explicit deliverables, in document order:

1. **§1 Evidence-Governed Foundation Buildout** — the load-bearing admission rule with five rationales (AR-1..AR-5) + two new foundation-buildout safeguards. Replaces the strict orphan pull rule for the program scope.
2. The bridge model: OAGIS noun / component / field → BCR entity / characteristic / business_concept (§2).
3. The six-bucket pre-admission filter taxonomy (§3).
4. The comprehensive target catalogue with **actual counted numbers** from the deterministic OAGIS profiler (§4A): proposed entities (54), proposed new characteristics (~224 bf_names → ~90–130 admissible after operator review), proposed BC targets (773 deduplicated), substrate-role classification, **counts by admission rationale (§4A.10)**.
5. **§1A layer-first sequencing rationale and cache optimization** — three-pass model (Characteristic → Entity → BC); cache precedence; cost and park-elimination economics.
6. **Layer-first re-aggregation (§4B) and layer-first wave list (§5)** — restructures the 773 BC target backlog into three passes per §1A. Reduces cost, eliminates mixed-decision parks, improves cache reuse.
7. The persistent retry ledger design (§6) with row-level statuses aligned to §8 row execution outcomes; row schema extended with `admission_rationale`, `used_by_bc_target_count`, `target_entities`, `target_waves`, `entity_slice_name`, `composite_identity_decision`, `packet_hash`, `retry_reason`; per-pass program-completion state header (§6.7).
8. **§6A Program Compile / Preflight Layer** — deterministic, no-LLM step that builds the executable retry ledger before any panel runs. The only approved dry-run style for this program.
9. **§6B Batch + Cache Execution Economy** — safe batching policy; six cache layers; invalidation triggers; retry economy (no retry on unchanged hash); future microbatch panel design (NOT authorised by this blueprint).
10. The recommended first waves under layer-first model (§7): C1 + E1 + BC-AR, each with stated admission rationale and pre-execution prereq.
11. **The program-level autonomous execution policy** (§8): A1–A5 program authorisation model + row execution rules + nonfatal outcomes + fatal/systemic stops + checkpoint rules + per-pass program completion. The layer-first + Evidence-Governed Foundation Buildout reconciliation preserves this policy unchanged.
12. The amended status + next operator action: A1–A5 program approval is the single operator act that enables autonomous layer-first execution under Evidence-Governed Foundation Buildout.

### 0.3 What this blueprint does not do

- Does not author any characteristic, BC, or entity.
- Does not amend any definition.
- Does not propose a supersession.
- Does not run any panel.
- Does not change schema. The retry ledger Phase 1 lives in Markdown; Phase 2 is a candidate DBCP, not an executed one.
- Does not by itself authorise wave execution. The operator's A1–A5 program approval (§8.1, §11) is the act that enables autonomous wave execution.
- Does not authorise RED row execution under any approval. RED rows always require separate operator decisions per row.
- Does not authorise the microbatch panel design in §6B.6. That design is captured for future consideration only.
- Does not authorise the Phase-2 ledger DBCP. Phase 1 Markdown ledger is the substrate-of-record until operator decides otherwise.
- Does not propose touching `mcf.*`, `contract.*`, or `bcf.*` writer paths.
- Does not change the strict orphan pull rule's applicability to steady-state orphan cleanup. The orphan pull rule remains canonical for non-program work.

## 1. Evidence-Governed Foundation Buildout (load-bearing admission rule)

This blueprint replaces the strict pull-driven rule (from `bcf-orphan-characteristic-decision-inventory-2026-06-23.md` §8 amendment) with a broader **Evidence-Governed Foundation Buildout** rule for the BCF × OAGIS program scope. The orphan pull rule remains the doctrine for steady-state orphan-cleanup work (Vocab Framework §11.3, §11.6, orphan inventory §8); this blueprint's foundation-buildout program uses the wider rule below.

### 1.1 Why the change

The strict pull rule worked for orphan cleanup because every characteristic the registry already carried but had no binding for needed a concrete metric / source-chain / workflow / entity-backbone demand before it activated. That model fits steady-state vocabulary maintenance.

It does **not** fit broad BCF foundation building. Reasons:

| Symptom | Reason |
|---|---|
| Most foundation candidates cannot express "known metric pull" | The 773 BC backlog the OAGIS extract proposes spans 54 new entities + ~90-130 new characteristics. The metric universe that will demand them has not been declared. The legacy metric chunk can express pull; the larger seed-metric universe cannot yet. |
| Strict pull keeps BCF reactive | Admitting only what existing metrics need leaves BCF reactive — playing catch-up — and prevents it from becoming the load-bearing business vocabulary foundation the platform's design promises. |
| Standards-backed need has no orphan analogue | OAGIS T2 evidence declares characteristics + entities as load-bearing for cross-enterprise business domains (e.g., `incoterms code` for international trade, `quality status code` for QM). Refusing admission on grounds of "no current metric pull" leaves the foundation incomplete by design. |
| Operator strategic priority cannot be a current pull | "We're entering manufacturing as a vertical, so admit production-side vocabulary" cannot be expressed as a current metric pull because the metric chain has not been authored yet. Strategic-priority admission is a foundation act, not a steady-state act. |

The broader rule preserves discipline through the safeguards in §1.3 + the two new foundation-specific safeguards in §1.4.

### 1.2 The rule — five admission rationales

A BCF candidate may enter the executable backlog if it satisfies **at least one** of five admission rationales:

| # | Rationale | Operative test | Evidence required |
|---|---|---|---|
| **AR-1** | `known_metric_pull` | A concrete metric (active MC, or seed MC with declared chain) requires the binding. | metric_uid named; for seed MC: declared chain reference (MCF M1+) |
| **AR-2** | `source_chain_pull` | A source-chain (SC → AC → OC → CC) enrichment in scope requires the binding for a tenant onboarding or seed configuration. | source_contract_uid + admission_contract_uid named; for seed: declared CC field selection |
| **AR-3** | `entity_backbone_completeness` | The entity is admitted (or will be in Pass 2) and the characteristic is part of a coherent backbone for future metric / source-chain / workflow demand. | backbone slice named (e.g., "Customer Invoice header"); load-bearing role stated ("join key for AR-AP three-way match") |
| **AR-4** | `standards_backed_foundation` | OAGIS T2 (or other admissible T3 standards) names the characteristic or entity as load-bearing for a cross-enterprise business domain. | OAGIS noun + component cited; section reference; standards version pinned |
| **AR-5** | `operator_strategic_priority` | The operator names the candidate as a strategic capacity for an upcoming initiative. | strategic-priority text rationale ≥40 chars + named initiative + named operator |

A row may carry **multiple rationales**. The ledger records all applicable rationales as `admission_rationale: [...]`. The primary rationale (first in the array) is used for cost/priority sequencing; the secondary rationales are recorded for audit.

### 1.3 Safeguards that remain

The broader admission rule does NOT relax foundational safeguards. The following all remain enforced:

| Safeguard | Source rule |
|---|---|
| OAGIS is Tier-T2 evidence, not identity authority | BCR §9; Vocabulary Evidence Framework §2 |
| No source-field copy (M9 of admission checklist) | Vocabulary Evidence Framework §4 |
| No metadata / envelope rows (Bucket B) | §3.1 |
| No runtime-derived / resolver-stamped rows (Bucket A) | Vocabulary Evidence Framework §11.6 |
| No source-diagnostic-only rows unless explicitly justified | Vocab Framework §11.3 (canonical-vs-diagnostic substrate role) |
| No ambiguous RED rows; classification must be definitive | §5.1; §8.2 |
| Foundation Invariants I–VI bind every row | `the-invariants.md` |
| DEC-fb0b12 E1–E6 binds editorial amendments | DEC-fb0b12 |
| System-agnosticism — source-system carriers are evidence, not scope | Vocab Framework §11.1 |
| Forbidden terms (`fiscal period`, etc.) | Vocab Framework §11.6 |
| BCR §4 acyclicity for composite entities | BCR §4 |
| One characteristic, one meaning (no synonyms; no homonyms) | BCR §6 |
| F4-v2 v1 Vocabulary Admission Checklist for new characteristics | Vocab Framework §4 |

### 1.4 Two new safeguards specific to foundation buildout

The broader admission rule introduces two safeguards specifically to prevent "vocabulary push" — admitting unused vocabulary because OAGIS or operator strategic priority justify it abstractly.

**Safeguard 1 — Characteristic must support at least one target BC.** A new characteristic enters Pass 1 only if at least one downstream target BC row in the ledger names it. The retry ledger tracks this as `used_by_bc_target_count` on every characteristic row. A characteristic with `used_by_bc_target_count = 0` cannot be admitted under any rationale — it is either deferred (vocabulary capacity, rationale met but BC count zero) or rejected.

**Safeguard 2 — Entity must belong to a coherent entity slice.** A new entity enters Pass 2 only if it belongs to a coherent entity slice — a slice that delivers at least one of: (a) a load-bearing metric, (b) a source-chain enrichment, (c) a documented operator-strategic initiative, or (d) a multi-entity backbone where the entity is structurally required (e.g., Item is required for Inventory Position).

These two safeguards preserve the spirit of the orphan pull rule — don't push unused vocabulary — while admitting the four broader rationale classes. They are enforced by the Program Compile / Preflight Layer (§6A) and the row execution rules (§8.2): a row that fails either safeguard cannot reach `program_authorized` status.

### 1.5 Compared to the orphan pull rule

| Aspect | Orphan pull rule (Vocab Framework §11 + orphan inventory §8) | Evidence-Governed Foundation Buildout (this blueprint) |
|---|---|---|
| Admission triggers | 4 concrete pulls (metric / source-chain / workflow / entity-backbone) | 5 rationales (AR-1..AR-5 above) |
| Standards as admission trigger | No — standards are T2-T4 evidence but not by themselves a pull | Yes — `standards_backed_foundation` (AR-4) is admissible |
| Operator strategic priority | Not an admissible trigger | Yes — `operator_strategic_priority` (AR-5) is admissible |
| Backbone completeness | Yes (one of 4 pulls) | Yes (one of 5 rationales — AR-3) |
| Scope | All BCF substrate in steady-state | BCF × OAGIS foundation buildout (this program scope) |
| Vocabulary capacity rule | Strict — capacity held until pull | Modified — capacity may be admitted if it serves at least one target BC AND a rationale holds (§1.4 Safeguard 1) |
| Foundation-building vs steady-state | Steady-state (orphan cleanup) | Foundation-building (broad expansion) |
| Coexistence | Continues to govern post-program steady-state | Concludes when the program concludes (BCF reverts to pull-driven steady state) |

### 1.6 Why this is not a relaxation

The Evidence-Governed Foundation Buildout rule is **broader in admission triggers** but **stricter in row-level traceability**. Every admitted row must carry:

| Per-row attribute | Purpose |
|---|---|
| `admission_rationale: [AR-1..AR-5]` array | Names which rationale(s) justify admission |
| `admission_rationale_evidence` | Per-rationale evidence (metric_uid, source_contract_uid, OAGIS citation, operator-priority text) |
| `used_by_bc_target_count` (characteristic rows only) | Enforces Safeguard 1 |
| `entity_slice_name` (entity rows only) | Enforces Safeguard 2 |
| `f4_v2_verdict` (characteristic rows) | Verdict from F4-v2 v1 admission checklist |
| `composite_identity_decision` (entity rows) | Simple / composite + identity-bearing graph if composite |

The compile layer (§6A) refuses to mark a row `executable` unless all required attributes are populated. The autonomy policy (§8.2) refuses to execute a row whose evidence is incomplete. The combination admits broader vocabulary while preserving Foundation Invariant VI (evidence is emitted, not inferred) at the row level.

## 1A. Layer-first sequencing — three-pass program model

> **Note on numbering.** This was previously labelled §1.5, which collided with §1.5 (the "Compared to the orphan pull rule" subsection inside §1). Renamed to §1A. Earlier cross-references to "§1.5" that pointed to layer-first now read "§1A" or "§1A.x".

An earlier draft of this blueprint sequenced waves by **business domain** (AR, AP, GL, Inventory, Production, ...). Each wave mixed three distinct decisions: admit new characteristics, admit new entities, bind new BCs. For a 773-BC program this is too costly and ambiguity-prone — each wave re-litigated vocabulary scope while also adjudicating entity identity while also binding BCs, and a single park on a characteristic-definition question stalled the whole wave. That mixed-wave shape is replaced; the per-wave authorisation model it implied is also replaced — see §8 program-level execution policy.

The operator-revised model sequences work by **decision layer**, not by domain. Three passes execute in order:

| Pass | Layer | What is decided | What is read | Cache surface |
|---|---|---|---|---|
| **Pass 1** | Characteristic vocabulary | Admit / amend / supersede characteristics (representation_term + data_type + semantic_role + definition + F4-v2 v1 Global classification). One decision per term, regardless of how many entities will eventually bind it. | OAGIS bf_name candidates · existing 62 characteristic terms · ISO 11179 representation_term closed set · evidence corpus T1–T4 | Per-characteristic decision packet; per-representation_term checklist; F4-v2 v1 admission rubric |
| **Pass 2** | Entity backbone | Admit / coalesce / split entities (name + family + simple-vs-composite + identity-bearing reference graph for composites). One decision per entity, regardless of how many characteristics will eventually bind to it. | OAGIS noun + component candidates · existing 26 active entities · composite-identity acyclicity rule (BCR §4) | Per-entity decision packet; composite-identity graph; entity-family classification |
| **Pass 3** | Business Concept binding | Bind `(entity, characteristic)` BCs against resolved identities. No vocabulary semantics, no entity semantics. The packet contains: the resolved characteristic (from Pass 1), the resolved entity (from Pass 2), the OAGIS provenance citation, the sibling representation_term pin, the F3 createBusinessConcept invocation. | Resolved characteristics from Pass 1 · resolved entities from Pass 2 · OAGIS provenance · sibling shape pins from prior BCs on the same entity | Per-entity packet prefix (cached across all that entity's BCs); per-characteristic shape pin (cached across all that characteristic's BCs); F3 panel cache reuse |

### 1A.1 Why layer-first

| Property | Mixed-wave cost | Layer-first benefit |
|---|---|---|
| **One characteristic supports many BCs** | A new characteristic admitted inside a mixed wave gets one panel cycle for its admission, but its decision is then re-cited in every later BC wave that binds it — and if the wave's notes carry an incomplete pin, the next BC wave re-runs the adjudication. | Admit once, cache cited, every later BC wave reads from cache. The 257 EE_NC + 355 NE_NC BCs (612 of 773) all depend on Pass 1 admissions; admitting them up-front amortises ~140 panel sessions across 612 BC bindings. |
| **One entity unlocks many BCs** | A new entity admitted inside a mixed wave proceeds immediately to bind its first BCs in the same session. If the entity admission surfaces a composite-identity question or a simple-vs-composite ambiguity, the entire wave's BC bindings stall. | Admit entity once, then return in Pass 3 to bind its full BC set in a packet-cached BC-wave. The 438 RED-class BCs (NE_EC + NE_NC) all depend on Pass 2 admissions; admitting them up-front means BC-wave executions don't re-confront entity questions. |
| **BC binding should not decide vocabulary/entity semantics** | When a BC wave's Maker proposes a binding and the entity is freshly admitted in the same session, the Maker's evidence packet carries entity context still being formed. Park risk on definition-scope, identity-tuple, family-classification questions is high. | A BC-wave Maker reads cached characteristic decisions (definition + shape) + cached entity decisions (identity + family + scope) and only adjudicates whether the binding is sound under those decisions. Park risk drops to the per-row binding question alone. |
| **Mixed-decision parks** | Wave B (2026-06-23) halted twice in one session — once on `net amount` definition scope, once on `line number` representation_term shape. Both were vocabulary questions surfacing inside a BC-binding wave. | C-waves resolve vocabulary first; E-waves resolve identity second; BC-waves carry no vocabulary or identity questions to surface. The mixed-decision park class is structurally eliminated. |
| **Cache and retry economics** | The Maker / Checker / Moderator session prompt-cache is per-session. Mixed-wave sessions cache a heterogeneous prefix (vocabulary + identity + binding) that does not reuse well across the next session's heterogeneous prefix. | C-wave sessions cache a uniform vocabulary prefix; E-wave sessions cache a uniform identity prefix; BC-wave sessions cache a uniform `(this entity, prior BCs on this entity)` prefix. Cache hit rates rise dramatically — and parks / rejects in one layer no longer stall the others. |

### 1A.2 Cache precedence

Operationally, the program executes three nested caches in order:

```
1. Characteristic cache      ← Pass 1 sessions populate this
   - Each admitted characteristic: term + definition + representation_term + data_type + semantic_role + F4-v2 v1 verdict
   - Cited by entity in Pass 2, by BC in Pass 3

2. Entity cache              ← Pass 2 sessions populate this
   - Each admitted entity: name + family + simple-vs-composite + identity-bearing graph + lifecycle_state
   - Cited by BC in Pass 3

3. BC packet cache           ← Pass 3 sessions populate this
   - Each per-entity BC packet: entity context + prior BCs on entity + sibling shape pins
   - Re-used across all that entity's BC bindings in the same BC-wave session
```

BC waves never re-adjudicate term-definition. If a BC wave's Maker proposes binding `(entity, characteristic)` and the characteristic's cached definition does not validly cover the proposed binding, the row parks with `next_action_text='characteristic scope question — refer to Pass 1 follow-up packet'`. The agent does NOT silently broaden, does NOT mint a substitute characteristic, and does NOT autonomously re-cycle to Pass 1.

### 1A.3 What layer-first does NOT change

- The Evidence-Governed Foundation Buildout rule (§1) still binds. A characteristic is admitted in Pass 1 only when at least one downstream BC target exists (Safeguard 1) AND at least one admission rationale AR-1..AR-5 is fully evidenced. Layer-first sequences when the admission happens; it does not relax the admission rule.
- The Foundation invariants (I–VI) still bind every act.
- The Vocabulary Evidence Framework v1 + §11 amendment + §11.6 source-attested/resolver-stamped boundary still bind every characteristic admission.
- DEC-fb0b12 E1–E6 still binds editorial amendments in Pass 1.
- BCR §4 acyclicity still binds composite-identity entity admissions in Pass 2.
- The fatal-stop list in §8.4 still binds every row execution.
- A1–A5 program approval (§8.1) authorises all three passes at once; the operator does not re-authorise per pass.

## 2. Bridge model — OAGIS → BCR shape

### 2.1 OAGIS shapes

The OAGIS finance-extract is structured at four levels:

| OAGIS shape | What it is | Count in the extract |
|---|---|---|
| **Noun** | A top-level OAGIS business document (e.g., `Invoice`, `PurchaseOrder`, `Shipment`) | 133 |
| **Component** | A sub-structure within a noun (e.g., `invoice-header`, `invoice-line`) | varies per noun |
| **Field** | A scalar attribute within a component (e.g., `Identifier`, `NetAmount`, `DocumentDateTime`) | 2,868 scalar (after stripping nested complex fields, which add 3,263 more for 6,131 total) |
| **Shared component** | A cross-noun reusable type (e.g., `Tax`, `Allowance`, `Charge`, `Party`) | 25 |

Each scalar field in the extract is pre-enriched with:

- `oagis_data_type` (OAGIS-side type, e.g., `String`, `DecimalType`, `IndicatorType`)
- `representation_term` (OAGIS's own ISO 11179-aligned term, e.g., `Identifier`, `Amount`, `Code`)
- `data_type` (BareCount-side normalised, e.g., `string`, `code`, `timestamp`)
- `semantic_role` (BareCount-side enrichment, e.g., `identifier`, `dimension`, `descriptor`, `temporal`, `measure`)
- `bf_name` (candidate slug, e.g., `delivery-date`, `unit-price`)
- `description` (verbatim from OAGIS noun-page; 773 blanks were resolved during enrichment by walking up the OAGIS shared-component graph)

### 2.2 BCR shapes (post-DEC-02f5a9)

The Business Concept Registry, after DEC-02f5a9, exposes three first-class shapes and one closed reference set:

| BCR shape | What it is | Live count (2026-06-23) |
|---|---|---|
| **Entity** | A globally governed, role-bearing business concept; simple or composite | 29 (26 active) |
| **Characteristic** | A flat (term, definition) immutable atom under DEC-26b6e2 + DEC-fb0b12 | 63 (62 active, 1 draft) |
| **Business Concept (value-kind)** | An (entity, characteristic, representation_term, data_type, semantic_role) quintuple bound under `UNIQUE(entity_id, property_id)` | 203 (194 active) |
| **Representation term** (closed set) | ISO 11179-seeded vocabulary primitives | `amount, code, count, date, identifier, indicator, quantity, text` + tagged extensions in `concept_registry.representation_term` |

Reference properties (concept identity by reference between entities) are a future expansion; the current substrate is value-kind-dominated.

### 2.3 Surgery patterns — when OAGIS shape ≠ BCR shape

OAGIS and BCR are not isomorphic. The five common surgical patterns:

| Pattern | OAGIS-side trigger | BCR-side result | Example |
|---|---|---|---|
| **Role split** | 1 noun is genuinely two business roles | 2 distinct entities, one per role | `Invoice` → `Customer Invoice` (sell-side) + `Supplier Invoice` (buy-side); `Party` → `Customer` + `Supplier` + `Vendor`; `Shipment` → `Customer Shipment` (+ future `Supplier Shipment` if pull-justified) |
| **Header/Line decomposition** | 1 noun has a header component + repeated line component, each load-bearing | 2 entities: parent header + composite line | `Invoice` → `Customer Invoice` (header) + `Customer Invoice Line Item` (line); already present in current substrate for CI/SI/PO/SO/GR/JE |
| **Coalesce** | N nouns describe variations of one business concept | 1 entity with multiple binding sources | OAGIS `Item`, `ItemMaster`, `Material`, `Product` → 1 `Item` entity (pull-driven; not yet admitted) |
| **Demote** | Noun is purely procedural / acknowledgment / metadata | No entity; possibly characteristic on host entity | OAGIS `Acknowledgement`, `Confirmation`, `Response` → no entity (procedural metadata) |
| **Skip** | Noun is out of platform scope | No BCR mapping | OAGIS `Screening`, `OperationsRoutine`, `Compliance` (when not domain-relevant) → skipped |

### 2.4 Shape-mapping table — generic

| OAGIS shape | Possible BCR mappings | Decision driver |
|---|---|---|
| 1 noun | 0..N entities | Role split / coalesce / demote / skip per §2.3 |
| 1 component | 0..1 entity (when load-bearing) OR 0 (when structural envelope) | Whether the component carries an independent business identity |
| 1 scalar field | 0..1 candidate BC (when admissible per §3 filter) | Six-bucket filter taxonomy |
| 1 shared component (Tax, Party, etc.) | 0..1 entity OR cross-cutting characteristic pattern | Whether the shared component is itself a business concept (Party → Customer/Supplier/Vendor) or a structural decorator (Tax → characteristics `tax` + `tax rate` on host) |

### 2.5 Semantic role and representation term mapping

The OAGIS extract's `semantic_role` enrichment values map cleanly to BCR's `semantic_role` enum:

| OAGIS enrichment | BCR `semantic_role` | Notes |
|---|---|---|
| `identifier` | `identity` | Document numbers, line numbers, party IDs |
| `dimension` | `dimension` | Code-based classifiers (currency, country, status enums) |
| `descriptor` | `descriptive` | Free-form descriptors (description, note, role labels) |
| `temporal` | `temporal` | Dates and timestamps |
| `measure` | `amount` | Monetary, quantitative, rate-like measures |

The OAGIS `representation_term` enrichment maps cleanly to BCR's closed set (BCR §5):

| OAGIS / ISO 11179-5 term | BCR `representation_term` | Notes |
|---|---|---|
| `Amount` | `amount` | Monetary value |
| `Code` | `code` | Value from a code list |
| `Count` | `count` | Non-monetary numeric count |
| `Date` / `DateTime` | `date` (with optional finer granularity flag) | Calendar date or instant |
| `Identifier` | `identifier` | Identity within a scheme |
| `Indicator` | `indicator` | Boolean / yes-no signal |
| `Quantity` | `quantity` | Numeric measurable with optional unit |
| `Text` | `text` | Free-form language content |

OAGIS `representation_term` is **evidence** that the BareCount closed set already covers the OAGIS-side vocabulary. No new BCR representation_term is needed because of OAGIS coverage.

## 3. Pre-admission filter taxonomy (six buckets)

Every OAGIS field passes through a six-bucket filter before any panel call. The filter is applied at blueprint time (Phase 1, here) and re-checked at wave-execution time (Phase 2, in the retry ledger).

### 3.1 The six buckets

| # | Bucket | Definition | Downstream action |
|---|---|---|---|
| **A** | **Runtime-derived (resolver-stamped)** | A concept the canonical resolver computes from canonical context (fiscal period, fiscal year, derived amounts under tenant arithmetic, normalised statuses produced by the resolver). Per Vocabulary Evidence Framework §11.6. | **Drop.** Not BCF. Lives at the Canonical Contract / canonical-resolution boundary. |
| **B** | **Metadata-only (envelope)** | Generic envelope or admin fields not specific to a business concept: `description`, `note`, `uuid`, `lastModificationDateTime`, `processIdentifier`, `requesterIdentifier`, `parentIdentifier`, `key`, `definition`. Carriers, not concepts. | **Drop.** Not BCF. May appear at lineage / evidence layer if needed. |
| **C** | **Source-diagnostic** | A classifier that preserves source-system context but does not drive any metric / join / filter / comparison the platform exposes. Per Vocabulary Evidence Framework §11.3. | **Defer.** Record in retry ledger as `intentional deferral with documented system-agnostic rationale`. Activate only on pull. |
| **D** | **Candidate characteristic (new term)** | A generic business term not yet in `concept_registry.characteristic`. Subject to F4-v2 Vocabulary Admission Checklist v1 (M1–M10, S1–S6, X1–X6 per Vocabulary Evidence Framework §4). | **Route to operator decision** for term + definition + classification (Global / Industry / System / Alias / Reject). Only `Global` is admissible under F4-v2 v1. |
| **E** | **Candidate BC (reuse-only)** | An (entity, characteristic) binding that reuses an existing active characteristic and falls within its governed definition scope. | **Route to F3 BC authoring panel** under the panel-execution doctrine. Subject to representation_term + data_type + semantic_role sibling-pattern check (Wave B §5.3). |
| **F** | **Candidate entity (new)** | An entity not yet in `concept_registry.entity`. May be simple or composite. | **Route to operator decision** for entity name + family + composite-identity declaration. Entity admission is a prerequisite for any subsequent BC binding on that entity. |

### 3.2 Filter precedence — decision tree

Applied top-to-bottom; first match wins.

```
For each OAGIS scalar field f:
  1. Does f name a concept the canonical resolver computes?
     YES → A (Runtime-derived) → DROP
  2. Is f a generic envelope / admin field?
     YES → B (Metadata-only) → DROP
  3. Does f's binding require admitting a new entity that does not yet exist?
     YES → F (Candidate entity) → route to operator; field becomes a future
            candidate BC once the entity is admitted
  4. Does f's business meaning belong to an existing active characteristic
     whose definition validly covers the proposed binding?
     YES → E (Candidate BC reuse-only) → eligible for F3 panel
  5. Does f introduce a new term not in concept_registry.characteristic?
     YES → D (Candidate characteristic) → route to operator F4-v2 admission
  6. Is f a source-system classifier with no current metric / workflow demand?
     YES → C (Source-diagnostic) → defer in retry ledger
  Else → unclassified; surface for operator triage as RED.
```

Note: Bucket E is favoured by reuse-is-the-default (Grounding Recheck Q1). The decision tree privileges reuse before admission of new terms.

### 3.3 Per-bucket downstream routing

| Bucket | Routing | Operator touch | Substrate write |
|---|---|---|---|
| A | Document in ledger as `runtime_derived`; reference §11.6 + the owning operating-model chapter | None | None |
| B | Document in ledger as `metadata_only` | None | None |
| C | Document in ledger as `source_diagnostic_deferred` with system-agnostic rationale | On pull-event only | None until pull |
| D | Held packet → operator F4-v2 admission decision → if Global, panel run via `createCharacteristic` | Required | Possible (new characteristic row + activation cert) |
| E | A0 Compile classifies + ledger seeds → A1–A5 program approval → row executes autonomously under §8.2 within its BC-wave → panel run via `createBusinessConcept` (F3 single-writer service) | Operator at A1–A5 (not per row) | Possible (new BC row + create cert + activation cert) |
| F | Held packet → operator entity decision → panel run via `createEntity` → entity activation → cascade unblocks downstream E candidates | Required | Possible (new entity row + entity_version row + activation cert) |

### 3.4 Worked examples — applying the filter to the extract

| OAGIS field | Path | Bucket | Disposition |
|---|---|---|---|
| `Invoice.invoice-header.NetAmount` | scalar, `representation_term=Amount`, `semantic_role=measure` | E (reuse) | Maps to existing `net amount` characteristic. After DEC-fb0b12-validated broadening 2026-06-23, doctrinally clean on both CI and SI; PO already bound. |
| `Invoice.invoice-header.DocumentDateTime` | scalar, `representation_term=DateTime`, `semantic_role=temporal` | E (reuse) | Maps to existing `document date` characteristic (with optional finer granularity); 11 active bindings. |
| `Invoice.invoice-header.UUID` | scalar, `representation_term=Identifier`, semantic_role=identifier (system identifier) | B (metadata-only) | Generic surrogate identifier; not a business concept. Drop. |
| `Invoice.invoice-header.LastModificationDateTime` | scalar, `representation_term=DateTime`, semantic_role=temporal | B (metadata-only) | Source-system audit timestamp; not a business observation. Drop. |
| `JournalEntry.journal-entry-header.FiscalPeriod` | scalar, `representation_term=Code` | A (runtime-derived) | Fiscal period is resolver-stamped per D364. Drop. If source-attested distinct period code is needed, use `posting period code` per §11.6. |
| `PurchaseOrder.purchase-order-header.DocumentTypeCode` | scalar, `representation_term=Code` | C (source-diagnostic) | Operator-deferred 2026-06-19 per Vocabulary Evidence Framework §11.4. Defer. |
| `Item.item-master.GrossWeightMeasure` | scalar, `representation_term=Quantity` | F+E (entity gating) | `Item` not yet admitted as an entity → F (entity decision). Once admitted, becomes E reusing existing `gross weight` characteristic. |
| `WorkOrder.work-order-header.OperationCode` | scalar, `representation_term=Code` | D (candidate characteristic) | No `operation code` characteristic in registry; admission requires F4-v2 v1 Global classification + operator decision. |

### 3.5 Filter coverage estimate on the extract

Approximation against the OAGIS extract's 6,131-field corpus (2,868 scalar + 3,263 complex):

| Bucket | Estimated count | Basis |
|---|---|---|
| A — Runtime-derived | 80–150 scalar fields | Periods, derived totals, computed indicators. Includes `fiscalPeriod`, `fiscalYear`, derived `totalAmount`-style fields where applicable. |
| B — Metadata-only | 600–900 scalar fields | UUIDs, descriptions, notes, last-modification timestamps, process / requester identifiers, definitions, keys, screening references. Substantially overlaps with the 55 enrichment-time blanks (uuid, description, note, definition, key, parent-identifier, plot-identifier, etc., per `enrichment_summary.slug_results`). |
| C — Source-diagnostic | 400–800 scalar fields | Document type codes, classifier codes, source-system enums. Defer; activate on pull. |
| D — Candidate characteristic | 200–400 scalar fields | New terms not in current 62-active characteristic set: e.g., `operation code`, `routing step`, `batch number`, `serial number`, `valuation class`, `inspection lot`. |
| E — Candidate BC (reuse) | 800–1200 scalar fields | Reuse opportunities for the 16-characteristic safe-autonomous-reuse whitelist + the additional ~30 doctrinally-clean characteristics. Most of these are gated on prior F (entity) admission. |
| F — Candidate entity (gating) | 25–50 nouns (and their dependent fields) | Item / Material, Inventory Position, Warehouse / Storage Location, Work Order / Manufacturing Order, Routing, Quality Inspection Lot, Work Centre, Employee, Position, Job, Asset, Maintenance Order, Skills / Qualification, Project, etc. |
| Complex (nested) | 3,263 fields | Recurse into sub-component to extract scalars; filter applied at the scalar level. |

The estimates are approximate. Phase-2 (per-(C/E/BC)-wave) refinement happens at retry-ledger row authoring time.

## 4. Comprehensive target catalogue

The catalogue lists candidates by domain. For each, the table shows what the OAGIS extract supports and how it maps to existing or proposed BCR substrate. Each row is a **candidate**, not an authorisation. Admission is gated on §1 Evidence-Governed Foundation Buildout (5 admission rationales + 2 safeguards) and the §3 filter.

### 4.1 OAGIS subfunctions ↔ BCR substrate domains (delta map)

The 49 OAGIS subfunctions cluster into 11 BCR-side domains. The map below identifies what is currently covered, what is partial, and what is absent.

| BCR domain | OAGIS subfunctions (noun counts) | Current BCR coverage | Delta |
|---|---|---|---|
| **AR / Sell-side** | accounts_receivable (4), order_management (1), ecommerce (2), crm (2), pricing (1) | RICH: Customer, Customer Invoice, Customer Invoice Adjustment, Customer Invoice Line Item, Customer Payment, Customer Shipment, Remittance Advice, Sales Order, Sales Order Line, Credit Application, Credit Status — 11 entities | Mostly complete-enough. Minor extensions on payment / billing parity. |
| **AP / Buy-side** | accounts_payable (6), procurement (6) | USABLE: Supplier, Supplier Invoice, Supplier Invoice Line, Vendor Payment, Purchase Order, Purchase Order Line, Goods Receipt, Goods Receipt Line — 8 entities | AP master extension needed; procurement contract / requisition surfaces absent. |
| **GL / Accounting** | general_ledger (5), cost_accounting (2) | PRESENT-BUT-THIN: GL Account, Journal Entry, Journal Entry Line — 3 entities; debit/credit/posting characteristics in place but per-entity BC counts low | Strengthen JE line characteristics; admit cost-accounting entities if pull surfaces. |
| **Treasury / Banking** | treasury (4) | USABLE: Bank Account, Bank Statement, Bank Statement Line, Currency Exchange Rate — 4 entities | Closure already adequate; BSL × line number outlier deferred audit. |
| **Master data** | business_partner (5), location (3), organization (1), reference_data (3) | PARTIAL: Customer, Supplier covered; no Item / Material; no Org Unit; no Location entity | Item / Material master is the load-bearing gap. |
| **Inventory** | inventory (5) | ABSENT | Inventory Position (composite entity Item × Warehouse), Stock Item, Storage Location candidates. |
| **Production / WIP** | production (4), wip (6), engineering (3), engineering_bom (1), shop_floor (3), planning (6) | ABSENT | Work Order / Manufacturing Order, Routing, Operation, Bill of Materials, Production Order Confirmation. |
| **Logistics / Fulfilment** | logistics (15), traceability (1), fleet_management (1) | PARTIAL: Customer Shipment present; no Supplier Shipment, no Delivery, no Transport | Shipment-side extension and delivery / transport admission. |
| **Quality** | quality_management (6), testing (3), certification (2), compliance (1), risk_management (1) | ABSENT | Quality Inspection Lot, Inspection, Test Result, Certificate. |
| **Workforce** | workforce (3), training (3) | ABSENT | Employee, Position, Job, Training Record. |
| **Asset / Maintenance** | fixed_assets (1), maintenance (3), warranty (1), material (1), equipment (1) | ABSENT | Asset, Equipment, Maintenance Order, Warranty Claim. |
| **Project / Programme** | project (1), project_management (1), program_management (1), change_management (1), resource_management (1), configuration (1), metadata (1), documentation (4), customer_service (1), messaging (1), support (1), screening (2) | ABSENT or out-of-scope | Project entity if pull; rest mostly Bucket A/B/C. |

### 4.2 Proposed new entities (pull-gated)

Twenty-three candidate entities organised by domain. Each is a **prerequisite** for downstream BC waves on that entity. Admission requires operator entity-decision per §3.3 Bucket F.

| # | Domain | Entity name (proposed) | Identity | OAGIS source | Pull rationale (illustrative — must be reconfirmed at wave time) |
|---|---|---|---|---|---|
| **1** | Master data | `Item` | Simple, identity-bearing on item code | OAGIS `Item`, `ItemMaster` (5 nouns coalesced) | Inventory metrics, three-way-match completeness, pricing |
| **2** | Master data | `Org Unit` (deferred: composite vs simple) | TBD | OAGIS `OrganizationStructure` | Reporting cuts; tenant multi-entity hierarchy |
| **3** | Master data | `Location` / `Site` | Simple | OAGIS `Location` (3 nouns) | Multi-site reporting, logistics, inventory |
| **4** | Master data | `Cost Centre` | Simple | OAGIS `BalanceSheet` / `JournalEntry` references | Cost-centre P&L; allocation metrics |
| **5** | Inventory | `Inventory Position` | **Composite** = (Item, Location, [Batch / Serial]) | OAGIS `InventoryBalance`, `MaterialQuantity` | DSI, inventory turn, stock-out frequency |
| **6** | Inventory | `Stock Item` (TBD — may collapse to Inventory Position) | Composite | OAGIS `Item` aggregate | Optionality |
| **7** | Production | `Work Order` / `Manufacturing Order` | Simple | OAGIS `WorkOrder`, `ProductionOrder` | Shop-floor variance, throughput, OEE |
| **8** | Production | `Operation` (BOM/routing step) | Composite = (Work Order, sequence number) | OAGIS `Routing`, `Operation` | Operation-level efficiency, bottleneck analysis |
| **9** | Production | `Bill of Materials` | Composite = (Parent Item, version) | OAGIS `BillOfMaterials` | BOM accuracy, material requirements planning |
| **10** | Production | `Production Confirmation` | Composite = (Work Order, Operation, confirmation seq) | OAGIS `ProductionConfirmation` | Confirmed-vs-planned variance |
| **11** | Logistics | `Delivery` / `Outbound Delivery` (TBD coalesce with Customer Shipment) | Simple | OAGIS `Delivery`, `Shipment` | OTIF, fill rate, delivery accuracy |
| **12** | Logistics | `Inbound Delivery` (TBD distinct from Goods Receipt) | Simple | OAGIS `InboundDelivery` | Supplier-side OTIF metrics |
| **13** | Logistics | `Transport / Shipment` (carrier-level) | Simple | OAGIS `Shipment`, `Transport` | Carrier performance, freight cost |
| **14** | Procurement | `Purchase Requisition` | Simple | OAGIS `PurchaseRequisition` | Requisition-to-PO cycle time, requisition-to-PO conversion |
| **15** | Procurement | `Outline Agreement` / `Contract` | Simple | OAGIS `Contract`, `OutlineAgreement` | Contract compliance, spend visibility |
| **16** | Procurement | `RFQ` / `Quotation` | Simple | OAGIS `RFQ`, `Quote` | Sourcing-cycle metrics |
| **17** | Quality | `Inspection Lot` | Composite = (Item, batch, inspection plan) | OAGIS `QualityInspectionLot` | Quality acceptance rate, defect rate |
| **18** | Quality | `Test Result` | Composite = (Inspection Lot, characteristic) | OAGIS `TestResult` | Test pass-fail metrics |
| **19** | Quality | `Certificate` | Simple | OAGIS `Certification` | Compliance status |
| **20** | Workforce | `Employee` | Simple | OAGIS `Personnel`, `Employee` | Headcount, attrition, span of control |
| **21** | Workforce | `Position` / `Job` | Simple (or composite if position-version semantics needed) | OAGIS `Position` | Org structure, vacancy rate |
| **22** | Asset | `Asset` / `Equipment` | Simple | OAGIS `Asset`, `Equipment` | Asset utilisation, depreciation tracking |
| **23** | Asset | `Maintenance Order` | Simple | OAGIS `MaintenanceOrder` | Maintenance cost, MTTR, MTBF |

**Notes on composite identity (per BCR §4):** Inventory Position is the canonical first composite-identity entity; once its identity-tuple shape is settled (Item × Location with optional Batch / Serial), the same pattern applies to Operation, BOM, Production Confirmation, Inspection Lot, Test Result. Composite identity is a Foundation-strict pattern; the registry's structural-uniqueness rule already supports it, but no composite entity has been admitted yet. The first composite admission carries doctrinal weight; the operator decision must include the identity-bearing reference graph and confirm acyclicity (BCR §4).

### 4.3 Proposed new characteristics (pull-gated)

Twenty-eight candidate characteristics organised by representation_term. Each requires F4-v2 v1 Vocabulary Admission Checklist approval and Global classification (Vocabulary Evidence Framework §6). Source-attested only — runtime-derived candidates (Bucket A) excluded.

#### 4.3.1 Identifier (representation_term = `identifier`, data_type = `string`, semantic_role = `identity`)

| # | Term (proposed) | OAGIS evidence | Likely first-binding entity | Notes |
|---|---|---|---|---|
| C-01 | `batch number` | OAGIS Item / Material `BatchIdentifier` | Inventory Position | Composite identity component candidate |
| C-02 | `serial number` | OAGIS Item / Material `SerialNumber` | Inventory Position; Asset | Composite identity component candidate |
| C-03 | `cost centre code` | OAGIS Accounting `CostCenter` | Cost Centre; Journal Entry Line | Likely already aligns with `account class code` or distinct concept — operator decision |
| C-04 | `routing identifier` | OAGIS Routing | Operation | Required for Operation composite identity |
| C-05 | `bill of materials identifier` | OAGIS BillOfMaterials | BOM | Required for BOM composite identity |
| C-06 | `work centre code` | OAGIS WorkCentre | Operation | Operation-level capacity attribution |
| C-07 | `inspection plan identifier` | OAGIS QualityInspectionPlan | Inspection Lot | Required for Inspection Lot composite identity |

#### 4.3.2 Code (representation_term = `code`, data_type = `code`, semantic_role = `dimension`)

| # | Term (proposed) | OAGIS evidence | Likely first-binding entity | Notes |
|---|---|---|---|---|
| C-08 | `operation code` | OAGIS Operation | Operation | Names the type of production step |
| C-09 | `inspection result code` | OAGIS TestResult | Test Result | Accept / Reject / Conditional |
| C-10 | `valuation class code` | OAGIS Item | Item | Inventory valuation classification |
| C-11 | `material type code` | OAGIS Material | Item | Item classification |
| C-12 | `unit of measure code` | OAGIS shared component `UnitOfMeasure` | Item; (cross-cutting on quantity-bearing BCs) | Closed-set candidate; operator decides whether UoM is a characteristic OR a per-BC metadata on quantity-bearing BCs |
| C-13 | `incoterm code` | OAGIS Logistics | Customer Shipment / Delivery / PO | Logistics shipping terms |
| C-14 | `transport mode code` | OAGIS Transport | Transport / Shipment | Air / Ocean / Road / Rail |
| C-15 | `delivery priority code` | OAGIS Delivery | Delivery | Priority classification |
| C-16 | `quality status code` | OAGIS QualityInspectionLot | Inspection Lot | Pass / Fail / Hold |

#### 4.3.3 Date / Timestamp (representation_term = `date`, data_type = `date` or `timestamp`, semantic_role = `temporal`)

| # | Term (proposed) | OAGIS evidence | Likely first-binding entity | Notes |
|---|---|---|---|---|
| C-17 | `planned start date` | OAGIS WorkOrder | Work Order; Operation | Production planning anchor |
| C-18 | `actual start date` | OAGIS WorkOrder, ProductionConfirmation | Work Order; Operation | Variance computation |
| C-19 | `actual completion date` | OAGIS ProductionConfirmation | Work Order; Operation | Completion stamp |
| C-20 | `inspection date` | OAGIS QualityInspectionLot | Inspection Lot | Inspection event timestamp |
| C-21 | `maintenance scheduled date` | OAGIS MaintenanceOrder | Maintenance Order | Planning anchor |
| C-22 | `maintenance completion date` | OAGIS MaintenanceOrder | Maintenance Order | Variance computation |

Note on potential overlap with existing characteristics: `planned start date` may overlap semantically with `ship date` / `delivery date` in some bindings; F4-v2 admission must confirm the term is genuinely distinct (no semantic duplicate) before approve.

#### 4.3.4 Quantity / Count (representation_term = `quantity` or `count`)

| # | Term (proposed) | OAGIS evidence | Likely first-binding entity | Notes |
|---|---|---|---|---|
| C-23 | `produced quantity` | OAGIS ProductionConfirmation | Work Order; Operation | Confirmed output |
| C-24 | `scrapped quantity` | OAGIS ProductionConfirmation, QualityInspectionLot | Operation; Inspection Lot | Yield-loss measure |
| C-25 | `defect count` | OAGIS QualityInspectionLot, TestResult | Inspection Lot | Defect-rate base |

#### 4.3.5 Amount (representation_term = `amount`, data_type = `decimal`, semantic_role = `amount`)

| # | Term (proposed) | OAGIS evidence | Likely first-binding entity | Notes |
|---|---|---|---|---|
| C-26 | `acquisition cost` | OAGIS Asset, MaterialCost | Asset; Item | Asset / inventory valuation |
| C-27 | `depreciation amount` | OAGIS Asset | Asset | Depreciation cycle metrics |
| C-28 | `freight amount` | OAGIS Logistics | Delivery; Transport | Already `freight charge` exists; this may be reuse (Bucket E), not new (Bucket D). Operator decides whether `freight charge` covers this binding under DEC-fb0b12 E1–E6. |

#### 4.3.6 Indicator (representation_term = `indicator`, data_type = `boolean`, semantic_role = `dimension`)

| # | Term (proposed) | OAGIS evidence | Likely first-binding entity | Notes |
|---|---|---|---|---|
| C-29 | `goods receipt indicator` | OAGIS PurchaseOrder, GoodsReceipt | PO Line | Booleanises three-way-match presence |
| C-30 | `invoice receipt indicator` | OAGIS PurchaseOrder | PO Line | Booleanises three-way-match presence |

### 4.4 Proposed reuse-only BCs (Bucket E candidates)

These are entity-extensions of existing characteristics — no new characteristic, no new entity beyond what §4.2 admits. The catalogue here is illustrative, not exhaustive. Per-wave packets enumerate the full set per slice.

| # | Entity (existing or to-be-admitted) | Characteristic (existing) | Source attestation | Pull |
|---|---|---|---|---|
| R-01 | Sales Order Line | `delivered quantity` | OAGIS SalesOrderLine | Order fulfilment metrics |
| R-02 | Sales Order Line | `ordered quantity` | OAGIS SalesOrderLine | Order completeness |
| R-03 | Purchase Order Line | `delivered quantity` | OAGIS PurchaseOrderLine | Three-way-match |
| R-04 | Customer Payment | `clearing date` | OAGIS Payment | DSO computation |
| R-05 | Vendor Payment | `clearing date` | OAGIS Payment | DPO computation |
| R-06 | Goods Receipt | `posting date` | OAGIS GoodsReceipt | Receipt timing |
| R-07 | Goods Receipt Line | `delivered quantity` | OAGIS GoodsReceiptLine | Receipt variance |
| R-08 | Bank Statement Line | `clearing date` | OAGIS BankStatement | Bank reconciliation completeness |
| R-09 | Customer Payment | `currency code` | OAGIS Payment | Multi-currency reporting |
| R-10 | Vendor Payment | `currency code` | OAGIS Payment | Multi-currency reporting |
| R-11 | Bank Account | `currency code` | OAGIS BankAccount | Account-level multi-currency |
| R-12 | Journal Entry Line | `debit amount` | OAGIS JournalEntry | Trial balance |
| R-13 | Journal Entry Line | `credit amount` | OAGIS JournalEntry | Trial balance |
| R-14 | Journal Entry Line | `posting date` | OAGIS JournalEntry | Period close |
| R-15 | Journal Entry | `document type code` (after operator scope-broadening if needed; defer per §11.4 worked example) | OAGIS JournalEntry | Posting classification |
| R-16 | GL Account | `account class code` | OAGIS ChartOfAccounts | Trial balance classification |
| R-17 | GL Account | `normal balance side` | OAGIS ChartOfAccounts | Debit/credit polarity |
| R-18 | Item (once admitted) | `description`, `net weight`, `gross weight`, `volume`, `unit price`, `currency code` | OAGIS Item | Item master loading |
| R-19 | Inventory Position (once admitted) | `quantity on hand` | OAGIS InventoryBalance | Inventory level metric; activates the existing orphan |
| R-20 | Work Order (once admitted) | `status`, `posting date`, `document type code` (subject to scope broadening if needed) | OAGIS WorkOrder | Shop-floor metric baseline |
| R-21 | Maintenance Order (once admitted) | `status`, `posting date`, `document date` | OAGIS MaintenanceOrder | Maintenance metric baseline |
| R-22 | Inspection Lot (once admitted) | `status`, `inspection date` (new C-20) | OAGIS QualityInspectionLot | Quality metric baseline |
| R-23 | Asset (once admitted) | `description`, `currency code`, `acquisition cost` (new C-26), `depreciation amount` (new C-27) | OAGIS Asset | Asset depreciation tracking |
| R-24 | Employee (once admitted) | `status`, `description`, `effective date` | OAGIS Personnel | Headcount baseline |
| R-25 | Purchase Requisition (once admitted) | `status`, `posting date`, `document date`, `currency code` | OAGIS PurchaseRequisition | Requisition cycle |
| R-26 | Delivery (once admitted) | `posting date`, `document date`, `ship date`, `delivery date`, `currency code` | OAGIS Delivery | OTIF metric chain |
| R-27 | Customer Shipment | `delivered quantity` (existing not yet bound on Customer Shipment header but is on lines) | OAGIS Shipment | Shipment-level completeness |
| R-28 | Sales Order Line | `delivery date` | OAGIS SalesOrderLine | Order-fulfilment temporal arc |

### 4.5 Substrate-role classification per candidate

Each candidate carries a substrate-role tag per Vocabulary Evidence Framework §11.3. Tags drive deferral discipline.

| Role | Candidates from above (sample) | Backbone implication |
|---|---|---|
| **Canonical metric substrate** | R-04, R-05, R-12, R-13, C-17 through C-22, R-26 OTIF chain, R-19 quantity on hand, C-23 produced quantity | Load-bearing. Required for the slice's named pull. |
| **Source-diagnostic substrate** | C-10 valuation class code, C-11 material type code, C-15 delivery priority code | Optional. Deferred until a concrete metric / reconciliation / audit / source-mapping workflow demands them. |
| **Composite-identity component** | C-01 batch number, C-02 serial number, C-04 routing identifier, C-05 BOM identifier, C-07 inspection plan identifier | Required for entity admission (Bucket F prerequisite). |

### 4.6 Per-domain candidate count summary

| Domain | New entities | New characteristics | New BCs (illustrative; per-(C/E/BC)-wave packet enumerates) |
|---|---|---|---|
| Master data | 4 (Item, Org Unit, Location, Cost Centre) | 1 (`cost centre code`) | 6 + cross-cutting reuse |
| Inventory | 2 (Inventory Position, Stock Item TBD) | 2 (`batch number`, `serial number`) | 1 (`quantity on hand` activates) + ~5 reuse |
| Production / WIP | 4 (Work Order, Operation, BOM, Production Confirmation) | 9 (C-04, C-05, C-06, C-08, C-17–C-19, C-23, C-24) | ~15 reuse + ~10 new |
| Logistics / Fulfilment | 3 (Delivery, Inbound Delivery, Transport) | 3 (C-13, C-14, C-15) + reuse `freight charge` audit | ~12 reuse + ~5 new |
| Procurement | 3 (Purchase Requisition, Outline Agreement, RFQ) | 0 (all reuse) | ~10 reuse |
| Quality | 3 (Inspection Lot, Test Result, Certificate) | 4 (C-07, C-09, C-16, C-20) + reuse C-24, C-25 | ~8 reuse + ~6 new |
| Workforce | 2 (Employee, Position) | 0 (all reuse via existing temporal + status + description) | ~6 reuse |
| Asset / Maintenance | 2 (Asset, Maintenance Order) | 2 (C-26, C-27) | ~8 reuse + ~2 new |
| **TOTAL** | **23 new entities** | **~28 new characteristics** | **~80–120 new BCs (illustrative)** |

These counts are blueprint-illustrative. **§4A is the actual counted catalogue from the deterministic OAGIS profiler.**

## 4A. Target State Catalogue — actual counts (2026-06-23)

§4 above is the illustrative catalogue, derived by walking the OAGIS subfunction inventory by hand. §4A is the **actual counted catalogue**: the result of running a deterministic 8-bucket classifier (`barecount-devhub/scripts/_oagis-classify.mjs`, session-scratch artifact) against the OAGIS finance-extract's 2,868 scalar fields, cross-referenced against the live BCR substrate snapshot 2026-06-23 (26 active entities + 62 active characteristics).

### 4A.1 Methodology

Every scalar field in the extract is classified into exactly one of 8 buckets via the precedence ladder in §3.2 plus the heuristic decoration below. Counts are reported both as raw field occurrences (counting every binding-candidate site) and as deduplicated `(entity, characteristic)` BC tuples (since the same BC may surface from multiple OAGIS nouns).

| Heuristic layer | Rule |
|---|---|
| METADATA_BF_NAMES filter list (~60 slugs) | Drops envelope/admin OAGIS structural fields (`uuid`, `description`, `note`, `identifier`, `source_identifier`, `party_identifier`, `action_code`, `name`, `uri`, `last_modification_date_time`, etc.) — Bucket 6 |
| RUNTIME_DERIVED_BF_NAMES filter list (~16 slugs) | Drops resolver-stamped concepts (`fiscal_period`, `fiscal_year`, `reporting_period`, `total_amount`, `total_volume_measure`, `subtotal_amount`, etc.) — Bucket 5 |
| Source-diagnostic patterns (suffix + slug list) | Drops `*_class_code` / `*_category_code` / `*_subcategory_code` / `*_segment_code` / `*_group_code` + ~20 specific diagnostic slugs (`priority_code`, `reason_code`, `condition_code`, etc.) — Bucket 7 |
| Noun → entity map (133 nouns) | Maps each OAGIS noun (and component) to BCR entity candidate(s); component-aware for header/line splits; role-split-aware for Invoice / Payment / Shipment |
| bf_name → characteristic normalisation | Kebab → space; suffix stripping (`_measure`, `_identifier`, `_date_time`, `_amount`, `_code`, `_indicator`); alias table for common semantic equivalents (`document_date_time` → `document date`, `extended_amount` → `line extension amount`, etc.) |
| Buckets 1–4 assignment | Cross-product of (entity exists, characteristic exists) — gives the four admissible-with-prep buckets |
| Unmapped noun → Bucket 8 | Nouns intentionally skipped at noun-mapping time (planning, documentation, messaging, screening, online, configuration, fleet, training, etc.) or genuinely ambiguous flag as SEMANTIC_AMBIGUITY_HALT for operator triage |

Heuristic risk and accuracy bands:

- **Buckets 5 + 6 are filter-list-deterministic.** A field is METADATA or RUNTIME_DERIVED only if its bf_name appears on the filter list. Counts are exact under the listed slugs.
- **Bucket 7 is heuristic.** The source-diagnostic suffix+slug list is the project's best estimate and may over- or under-include. Operator review per row at AMBER admission time refines.
- **Bucket 8 is residual.** Any unmapped noun → HALT. Most are intentional skips (operational/envelope nouns).
- **Buckets 1–4 dedupe by (entity, characteristic).** Multiple OAGIS nouns proposing the same binding count once — that is the executable BC target count.

### 4A.2 Field-occurrence bucket counts (raw, not deduplicated)

| Bucket | Count | % of scalar fields |
|---|---|---|
| 1 EXISTING_ENTITY_EXISTING_CHARACTERISTIC_BC | 112 | 3.9% |
| 2 EXISTING_ENTITY_NEW_CHARACTERISTIC | 321 | 11.2% |
| 3 NEW_ENTITY_EXISTING_CHARACTERISTIC | 108 | 3.8% |
| 4 NEW_ENTITY_NEW_CHARACTERISTIC | 384 | 13.4% |
| 5 RUNTIME_DERIVED_DROP | 48 | 1.7% |
| 6 METADATA_DROP | 1,561 | 54.4% |
| 7 SOURCE_DIAGNOSTIC_DEFER | 44 | 1.5% |
| 8 SEMANTIC_AMBIGUITY_HALT | 290 | 10.1% |
| **Total scalar fields** | **2,868** | **100.0%** |

Plus 3,263 complex (nested) fields; the classifier recurses into them per §3 decision tree but does not directly score them as candidates.

### 4A.3 Deduplicated BC target counts (the executable backlog)

After deduplication on `(entity, characteristic)` tuples:

| Bucket | BC targets |
|---|---|
| 1 EXISTING_ENTITY_EXISTING_CHARACTERISTIC_BC | **78** |
| 2 EXISTING_ENTITY_NEW_CHARACTERISTIC | **257** |
| 3 NEW_ENTITY_EXISTING_CHARACTERISTIC | **83** |
| 4 NEW_ENTITY_NEW_CHARACTERISTIC | **355** |
| **TOTAL BC TARGETS** | **773** |

This is the headline executable backlog: 773 BCs across 4 admissible buckets (after operator deferral of source-diagnostic and skip-class HALT rows that turn out to be intentional skips).

### 4A.4 Proposed new entities — actual count: 54

| # | Entity | Wave | Notes |
|---|---|---|---|
| 1 | Asset | W12 | Fixed assets |
| 2 | Bill of Materials | W8 | Composite candidate |
| 3 | Bill of Materials Line | W8 | Line subentity |
| 4 | Budget Ledger Entry | W14 | Budget-side of GL |
| 5 | Budget Ledger Entry Line | W14 | |
| 6 | Business Partner | W13 | Master data |
| 7 | Certificate | W10 | Quality / cert |
| 8 | Corrective Action | W10 | Quality |
| 9 | Cost Centre | W13 | Reporting cuts |
| 10 | Delivery | W9 | Logistics outbound |
| 11 | Employee | W11 | Workforce |
| 12 | Equipment | W12 | Asset class |
| 13 | Inspection Lot | W10 | Composite candidate |
| 14 | Inventory Count | W6 | |
| 15 | Inventory Count Line | W6 | |
| 16 | Inventory Movement | W6 | |
| 17 | Inventory Movement Line | W6 | |
| 18 | Inventory Position | W6 | **First composite-identity entity** |
| 19 | Item | W5 | Master data root |
| 20 | Location | W13 | |
| 21 | Maintenance Order | W12 | |
| 22 | Maintenance Order Operation | W12 | |
| 23 | Manufacturing Process | W8 | |
| 24 | Nonconformance Notification | W10 | |
| 25 | Nonconformance Notification Line | W10 | |
| 26 | Operation | W8 | Composite candidate |
| 27 | Org Unit | W13 | |
| 28 | Outline Agreement | W7 | Procurement |
| 29 | Outline Agreement Line | W7 | |
| 30 | Party | W13 | |
| 31 | Pick List | W9 | |
| 32 | Pick List Line | W9 | |
| 33 | Price List | W13 | |
| 34 | Price List Item | W13 | |
| 35 | Production Confirmation | W8 | |
| 36 | Production Schedule | W8 | |
| 37 | Project | W13 | |
| 38 | Purchase Requisition | W7 | |
| 39 | Purchase Requisition Line | W7 | |
| 40 | Quote | W7 | |
| 41 | Quote Line | W7 | |
| 42 | RFQ | W7 | |
| 43 | RFQ Line | W7 | |
| 44 | Routing | W8 | |
| 45 | Shipment Request | W9 | |
| 46 | Shipment Unit | W9 | |
| 47 | Test Method | W10 | |
| 48 | Test Result | W10 | Composite candidate |
| 49 | Three-Way Match Document | W9 | |
| 50 | Three-Way Match Document Line | W9 | |
| 51 | Warranty Claim | W14 | |
| 52 | Work Centre | W8 | |
| 53 | Work Order | W8 | |
| 54 | Work Order Operation | W8 | Composite candidate |

This list is the profiler output. Operator review at wave-execution time may coalesce some (e.g., Inventory Movement + Inventory Count + their line entities may collapse to fewer if shared identity emerges) or split others; the catalogue here is the upper bound entity count under the current noun→entity mapping.

### 4A.5 Proposed new characteristics — actual count

The profiler identifies **224 unique bf_names** as new-characteristic candidates after the filter list excludes metadata and runtime-derived terms. Operator-admissible count after review for source-diagnostic deferral + coalescing is estimated at **~120–180**.

Top 30 new-characteristic candidates by raw field occurrence (some will defer or coalesce at operator F4-v2 admission time):

| # | bf_name candidate | Occurrences | Likely operator disposition |
|---|---|---|---|
| 1 | `type_code` | 61 | Most defer as source-diagnostic per §11.4 worked example; small subset (line type, doc type) admit |
| 2 | `gl_entity_identifier` | 13 | Admit on JE Line / Cost Centre (as new char or alias for `cost centre code`) |
| 3 | `amount` | 13 | Too generic — operator coalesces to existing terms or splits per context |
| 4 | `system_identifier` | 10 | Defer as metadata-like (source-system tag) |
| 5 | `tax_base_amount` | 9 | Admit on invoice / order line entities — new char |
| 6 | `functional_amount` | 9 | Admit (functional-currency amount, distinct from document amount) |
| 7 | `tax_base_functional_amount` | 9 | Admit — companion to tax_base_amount |
| 8 | `required_delivery_date_time` | 9 | Admit — `required delivery date` new temporal char |
| 9 | `payment_method_code` | 8 | Admit — new code char on payment / invoice / order |
| 10 | `serial_number_identifier` | 8 | Admit — composite-identity component for Item / Asset |
| 11 | `dunnage_weight_measure` | 7 | Likely defer (logistics packaging detail) |
| 12 | `tare_weight_measure` | 7 | Likely defer |
| 13 | `upcid` | 7 | Defer as identifier-scheme code (party / item GS1 carrier) |
| 14 | `epcid` | 7 | Defer as identifier-scheme code |
| 15 | `ledger_identifier` | 6 | Admit on JE / Journal Entry Line |
| 16 | `cageid` | 6 | Defer as US gov supplier-id scheme |
| 17 | `cost_center_identifier` | 6 | Admit as `cost centre code` — coalesce with #2 |
| 18 | `promised_ship_date_time` | 6 | Admit — `promised ship date` new temporal char |
| 19 | `promised_delivery_date_time` | 6 | Admit — `promised delivery date` new temporal char |
| 20 | `shipping_instructions` | 6 | Defer / route to metadata-like |
| 21 | `transaction_date_time` | 6 | Operator decides vs `posting date` (likely defer) |
| 22 | `transportation_method_code` | 5 | Admit — `transport mode code` |
| 23 | `requested_delivery_date` | 5 | Admit — `requested delivery date` |
| 24 | `gl_destination_entity_identifier` | 5 | Admit (cost-centre transfer destination) or defer |
| 25 | `special_price_authorization_code` | 5 | Defer as workflow-procedural |
| 26 | `account_identifier` | 5 | Admit — overlap with `ledger account identifier` |
| 27 | `dunsid` | 5 | Defer as identifier-scheme |
| 28 | `dodaacid` | 5 | Defer |
| 29 | `bicid` | 5 | Defer |
| 30 | `scacid` | 5 | Defer |

The full 224-entry list lives in the profiler output. About **70–80 candidates are clearly operator-deferral material** (identifier schemes, source-system tags, ultra-specific logistics packaging). The remaining **~140–150** are admit-or-coalesce candidates.

### 4A.6 Final target range

| Surface | Current (2026-06-23) | Proposed addition | Final target | Final target (low end if operator defers aggressively) |
|---|---|---|---|---|
| Active entities | 26 | +54 | **~80** | ~50 (if Q-side + master-data fully reuse OAGIS coalesce + lines collapse) |
| Active characteristics | 62 | +120–180 | **~180–240** | ~120 |
| Active BCs | 194 | +500–773 executable (after DEFER/SKIP application) | **~700–970** | ~500 |

The high end reflects every admissible row executing; the low end reflects aggressive operator deferral on source-diagnostic and entity-collapse decisions.

### 4A.7 Counts by wave (BC targets, deduplicated; new entities + new characteristics)

| Wave | New entities | New char bf_names | BC: EE_EC (reuse) | BC: EE_NC (new-char on existing entity) | BC: NE_EC (existing-char on new entity) | BC: NE_NC (new-char on new entity) | **Total BCs** | Wave type |
|---|---|---|---|---|---|---|---|---|
| W1 (Payment parity) | 0 | 4 | 2 | 8 | 0 | 0 | **10** | reuse + char-admission |
| W2 (Order Line parity) | 0 | 9 | 5 | 15 | 0 | 0 | **20** | reuse + char-admission |
| W3 (GL JE Line) | 0 | 12 | 6 | 20 | 0 | 0 | **26** | reuse + char-admission |
| W4 (GL housekeeping) | 0 | 0–1 | — | — | 0 | 0 | **3–5** | housekeeping |
| W5 (Item) | 1 | 23 | 0 | 0 | 2 | 23 | **25** | entity + char-admission |
| W6 (Inventory composite) | 5 | 13 | 0 | 0 | 5 | 20 | **25** | entity + char-admission (composite-identity pilot) |
| W7 (Procurement extension) | 8 | 9 | 0 | 0 | 14 | 21 | **35** | entity + char-admission |
| W8 (Production / WIP) | 10 | 40 | 0 | 0 | 13 | 54 | **67** | entity + char-admission |
| W9 (Logistics outbound) | 7 | 57 | 0 | 0 | 16 | 69 | **85** | entity + char-admission |
| W10 (Quality) | 7 | 27 | 0 | 0 | 11 | 38 | **49** | entity + char-admission |
| W11 (Workforce) | 1 | 2 | 0 | 0 | 2 | 2 | **4** | entity + char-admission |
| W12 (Asset / Maintenance) | 4 | 44 | 0 | 0 | 6 | 52 | **58** | entity + char-admission |
| W13 (Master-data hardening) | 8 | 38 | 0 | 0 | 9 | 65 | **74** | entity + char-admission |
| W14 (Reference / Warranty / Budget) | 3 | 10 | 0 | 0 | 5 | 11 | **16** | entity + char-admission |
| W-extend (new chars landing on existing entities, not in W1–W4) | 0 | 98 | 65 | 214 | 0 | 0 | **279** | char-admission across already-existing entities |
| **TOTAL** | **54** | **~224 unique bf_names** | **78** | **257** | **83** | **355** | **773** | |

**W-extend** is the cross-noun fill-in: OAGIS nouns whose fields land on existing BCR entities (Customer Invoice, Supplier Invoice, GL Account, Journal Entry, etc.) introducing new characteristics like `payment_method_code`, `gl_entity_identifier`, `tax_base_amount`, `transaction_date_time`, etc. These can be sequenced as a dedicated wave OR distributed across W1–W14 as each new characteristic gets admitted. The blueprint treats W-extend as its own logical wave for accounting purposes; execution-time sequencing is a per-row scheduling decision.

### 4A.8 Counts by GREEN / AMBER / RED / DEFER class

| Class | Coverage | BCs | Notes |
|---|---|---|---|
| **GREEN** (reuse-only on safe-autonomous-reuse whitelist) | Pure EE_EC_BC reuse on whitelist characteristics only; subset of W1+W2+W3 | **13** | The truly autonomous-safe-today subset. The whitelist (16 characteristics from scope-audit §5) constrains this. |
| **AMBER** (reuse + new-characteristic admission on existing entities) | All EE_NC BCs (257) + the W1/W2/W3 reuse beyond the strict whitelist + W-extend's 65 reuse | **335** | Each new characteristic needs F4-v2 v1 Vocabulary Admission Checklist approval. Once admitted, BC authoring is reuse-like. |
| **RED** (entity admission required, then BC authoring) | W5–W14 totals = all NE_EC + NE_NC = 83 + 355 = 438 BCs across 54 new entities | **438** | Each new entity needs operator entity-admission decision (simple vs composite; identity-bearing reference graph for composites). |
| **DEFER** (intentional source-diagnostic / runtime-derived / metadata) | Buckets 5 + 6 + 7 = 1,653 raw field occurrences | **0 BC targets** | Not in executable backlog. Recorded as `deferred_*` ledger rows for traceability. |
| **HALT** (semantic ambiguity, operator triage required) | Bucket 8 = 290 raw field occurrences across mostly-skip subfunctions | **0 BC targets** until operator triage | Most resolve to SKIP per noun once operator confirms no pull demand. |
| **TOTAL executable BC targets** | | **786** | (13 GREEN + 335 AMBER + 438 RED). Note: 13 GREEN + 65 (EE_EC reuse counted under AMBER) = 78 EE_EC total reconciling with §4A.3. |

### 4A.9 Operative observations

1. **The truly-GREEN portion is small.** Only ~13 BCs are pure whitelist reuse on existing entities — the autonomous-safe core. The bulk of the executable backlog is AMBER (needs char admission) or RED (needs entity admission).
2. **W-extend is the largest single bucket (279 BCs).** Cross-noun reuse + char admission on existing AR/AP/GL/Banking entities. Many of these are mid-difficulty AMBER.
3. **W8 (Production / WIP) and W9 (Logistics) are the largest entity-admission waves.** 67 and 85 BCs respectively, each across 7–10 new entities. Both candidates for splitting.
4. **W11 (Workforce) is the smallest entity-admission wave** at 4 BCs. Fast wave; minimal scope.
5. **The 290 SEMANTIC_AMBIGUITY_HALT raw fields** concentrate in planning (66), logistics (44 — within an otherwise-mapped domain), documentation (27), wip (17), maintenance (16), crm (24). Most resolve to SKIP at noun level once operator confirms no pull demand; the wave list excludes them.
6. **Composite-identity entities concentrated in W6 (Inventory Position), W8 (Operation, BOM line, Work Order Operation), W10 (Inspection Lot, Test Result).** W6 is the doctrinal pilot.
7. **The full target is large but not unbounded.** 773 BCs is achievable across the program at ~55s panel wall-time per BC = ~12 panel-execution hours total, plus held-packet drafting time and operator decisions.

### 4A.10 Counts by admission rationale

Per §1.2 the executable backlog admits rows under five rationales (AR-1..AR-5). The expected distribution across the 773 BC target backlog (compile-time estimate; operator review at A1–A5 program approval finalises per-row assignments):

| Admission rationale | Primary on N BCs | % of 773 | Typical examples |
|---|---|---|---|
| **AR-1** known_metric_pull | ~80–120 | 10–15% | Active MC `accounts_receivable_dso` cites `clearing date` on Customer Payment / Vendor Payment (W1 parity); active MC `arpi` cites `net amount` on Sales Order (BC-AR fresh-binding) |
| **AR-2** source_chain_pull | ~50–80 | 6–10% | Tenant onboarding declares OC field selection over Customer Invoice header pulling in `payment_method_code` (W-extend AR) |
| **AR-3** entity_backbone_completeness | ~300–400 | 40–50% | Item entity admitted (E1) → `unit price` + `currency code` + `description` + `gross weight` + `net weight` etc. are needed to make Item a load-bearing master (BC-Master); same pattern for Purchase Requisition, Work Order, Inspection Lot, etc. |
| **AR-4** standards_backed_foundation | ~150–200 | 20–25% | OAGIS T2 names `incoterms_code`, `transportation_method_code`, `quality_status_code`, `operation_code` as load-bearing for trade / quality / production domains — admitted in C1/C2 (Pass 1) for cross-cutting reuse |
| **AR-5** operator_strategic_priority | ~50–100 | 6–13% | Operator names "enable manufacturing vertical" → E5/E6 Production + BC-Production-simple/composite get strategic-priority status; "rollout AP automation" → BC-AP gets strategic-priority for accelerated sequencing |
| Multi-rationale rows (2+ rationales) | ~150–200 | 20–25% | Most foundation BCs cite both AR-3 (backbone) AND AR-4 (standards); some also cite AR-1 (active metric) |
| **TOTAL executable BC rows** | **773** | **100%** | Multi-rationale rows counted once in primary class |

Per-pass admission-rationale skew (which rationales dominate which pass):

| Pass | Dominant rationale(s) | Why |
|---|---|---|
| **Pass 1 (C-waves)** | AR-3 + AR-4 (~70%) | Characteristics admitted to support backbone completeness across multiple downstream entities; OAGIS T2 cites them as load-bearing for the domain |
| **Pass 2 (E-waves)** | AR-4 + AR-5 (~75%) | Entities admitted on standards backing (OAGIS noun = load-bearing entity) + operator strategic priority (which verticals open next) |
| **Pass 3 (BC-waves)** | AR-3 + AR-1 (~60%) | Binding waves are dominated by backbone completeness (the entity needs the characteristic to be load-bearing) + active metric pulls where they exist |

Per-row admission rationale is a required field at A1–A5 program approval; the Compile layer (§6A) flags any row missing rationale evidence as `unknown_halt`.

## 4B. Layer-first re-aggregation (per §1A three-pass model)

§4A counts the executable backlog by the historical mixed-wave allocation (W1–W14 + W-extend grouping — preserved here as audit-trace only; superseded by the layer-first execution view). §4B re-aggregates the **same 773 BC target backlog** by layer per §1A. The total counts reconcile to §4A.3 — every characteristic admission, every entity admission, and every BC binding accounted for under both views. **The §5 layer-first wave list is the authoritative execution view; §4A.7 is retained for traceability only.**

### 4B.1 Pass 1 — Characteristic Vocabulary Pass

**Pre-dedupe step.** All ~224 new-characteristic bf_name candidates (§4A.5) are first deduped against the 62 active characteristic terms via the bf_name → characteristic alias table (§4A.1). Operator review at admission time:

- Filters ~70–80 candidates as DEFER (source-diagnostic identifier schemes like `cageid`, `dunsid`, `dodaacid`, `scacid`; ultra-specific logistics like `dunnage_weight_measure`, `tare_weight_measure`; classifier codes without analytical pull).
- Coalesces ~20–40 candidates that semantically duplicate other candidates after definition study (e.g., `cost_center_identifier` + `gl_entity_identifier` → one `cost centre code` characteristic).
- Net admitted: **~90–130 new characteristics** in Pass 1.

**C-wave breakdown by representation_term cluster** (cache-cluster groupings — admitted in batches sharing the same closed-set representation_term decision context):

| Wave | Representation_term | Illustrative members | Est. admitted | Class |
|---|---|---|---|---|
| **C1** | `code` | payment_method_code, incoterms_code, transportation_method_code, freight_term_code, ownership_code, transaction_analysis_code, base_uom_code, storage_uom_code, valuation_class_code, material_type_code, delivery_priority_code, quality_status_code, inspection_result_code, operation_code | ~20–25 | AMBER (F4-v2 v1 admission with pinned classification = Global) |
| **C2** | `date` (incl. timestamp granularity) | promised_ship_date, promised_delivery_date, required_delivery_date, scheduled_delivery_date, requested_delivery_date, expiration_date, best_used_by_date, received_date, required_date, creation_date, transaction_date, payment_date, shipment_release_date, earliest_ship_date, actual_ship_date, latest_start_date, planned_start_date, actual_start_date, actual_completion_date, inspection_date, maintenance_scheduled_date, maintenance_completion_date | ~15–20 | AMBER |
| **C3** | `identifier` | payment_term_identifier, employee_identifier, fixed_asset_identifier, container_identifier, activity_identifier, ledger_identifier, cost_centre_code (coalesced from gl_entity_identifier + cost_center_identifier), account_identifier (after operator coalesce with ledger_account_identifier), authorization_identifier, work_centre_identifier, asset_identifier, operation_identifier, inspection_plan_identifier, BOM_identifier, routing_identifier | ~15–20 | AMBER |
| **C4** | `amount` | tax_base_amount, functional_amount, tax_base_functional_amount, unit_amount, total_charge_amount, total_allowance_amount, labor_rate_amount, depreciation_amount, acquisition_cost, freight_amount (operator decides reuse-of-`freight charge` vs new) | ~10–15 | AMBER |
| **C5** | `quantity` / `count` | estimated_weight_measure, loading_weight_measure, produced_quantity, scrapped_quantity, defect_count, lead_time_duration (operator decides — possibly reuse of orphan `lead time` activation) | ~5–10 | AMBER |
| **C6** | `text` / `indicator` | short_name (operator decides vs `description` reuse), title, special_handling_note, goods_receipt_indicator, invoice_receipt_indicator, urgency_indicator | ~5–10 | AMBER |
| **C-DEFER** | n/a | ~70–80 source-diagnostic candidates (identifier schemes, classifier codes, ultra-specific logistics measures) | 0 admitted; held in ledger as `deferred_diagnostic` with system-agnostic rationale | DEFER |
| **C-RED** | varies | Characteristics flagged as RED at operator review — e.g., terms colliding with §11.6 forbidden names; terms requiring supersession of an active characteristic; first-of-kind shape candidates without sibling precedent | held; per-row decision | RED |
| **TOTAL** | | | **~70–100 admitted** + **70–80 deferred** + **~5–15 RED-held** | |

**Pass 1 completion criterion (C1':** all admissible characteristics are `lifecycle_state='active'`; all deferred have a `deferred_diagnostic` / `deferred_pull_gated` ledger entry; all RED-held have a `red_held` ledger entry with operator decision packet drafted.

### 4B.2 Pass 2 — Entity Backbone Pass

**Pre-dedupe step.** All 54 proposed new entities (§4A.4) are first deduped against the 26 active entities + the 3 superseded entities. Operator review at admission time:

- Coalesces where two OAGIS nouns map to one BCR entity (e.g., `item-master` + future `material` → `Item`; `manufacturing-process` + `production-schedule` → possibly one entity).
- Splits where one OAGIS noun maps to multiple BCR entities (existing pattern: Invoice → Customer Invoice + Supplier Invoice; Payment → Customer Payment + Vendor Payment).
- Classifies each entity as **simple** (operator-decidable via single-field identity) or **composite** (identity-bearing reference graph required per BCR §4).

Simple entities are AMBER under program approval (admitted via `createEntity` panel with operator-pinned name + family + classification). Composite entities are RED — each requires a separate operator decision packet for the identity-bearing graph + acyclicity confirmation (BCR §4).

**E-wave breakdown by domain + dependency** (cache-cluster groupings — admitted in batches sharing the same domain context):

| Wave | Domain | New entities (simple → AMBER) | New entities (composite → RED) | Est. count | Class profile |
|---|---|---|---|---|---|
| **E1** | Master data root | Item | — | 1 | AMBER (simple). Prerequisite for E4 + E5 + E6 + downstream. |
| **E2** | Master data | Business Partner, Cost Centre, Location, Org Unit, Party, Price List, Price List Item, Project | — | 8 | AMBER |
| **E3** | Procurement transactional | Purchase Requisition, PR Line, Outline Agreement, Outline Agreement Line, RFQ, RFQ Line, Quote, Quote Line | — | 8 | AMBER |
| **E4** | Inventory composite (doctrinal pilot) | Inventory Movement, Inventory Movement Line, Inventory Count, Inventory Count Line | **Inventory Position** | 5 (1 RED + 4 AMBER) | mixed (composite-identity pilot) |
| **E5** | Production simple | Work Order, Routing, Bill of Materials, Production Confirmation, Production Schedule, Manufacturing Process, Work Centre | — | 7 | AMBER |
| **E6** | Production composite | — | Work Order Operation, Operation, Bill of Materials Line | 3 | RED |
| **E7** | Logistics | Delivery, Pick List, Pick List Line, Shipment Request, Shipment Unit, Three-Way Match Document, Three-Way Match Document Line | — | 7 | AMBER |
| **E8** | Quality simple | Certificate, Corrective Action, Nonconformance Notification, Nonconformance Notification Line, Test Method | — | 5 | AMBER |
| **E9** | Quality composite | — | Inspection Lot, Test Result | 2 | RED |
| **E10** | Workforce | Employee | — | 1 | AMBER |
| **E11** | Asset / Maintenance simple | Asset, Equipment, Maintenance Order | — | 3 | AMBER |
| **E12** | Maintenance composite | — | Maintenance Order Operation | 1 | RED |
| **E13** | Reference / Warranty / Budget | Budget Ledger Entry, Budget Ledger Entry Line, Warranty Claim | — | 3 | AMBER |
| **TOTAL** | | **~47 simple-AMBER** | **~7 composite-RED** | **54** | |

Pre-dedupe entity coalescing decisions stay open (operator-decidable at entity admission time):

- Coalesce candidates: `Customer Shipment` ↔ `Delivery` (OQ-5 deferred); `Production Schedule` ↔ `Manufacturing Process`; `Pick List` ↔ `Delivery` (in some ERPs picking is part of delivery).
- Split candidates: `Item` may need to split into `Item Master` + `Item Variant` if substrate carries Material × variant axes.

These are operator decisions at E-wave preflight time; they may reduce the 54 to 48–52 final entities.

**Pass 2 completion criterion (C2'):** all simple-AMBER entities are `lifecycle_state='active'`; all composite-RED entities have either an admitted active state OR a held operator decision packet with the identity-bearing graph drafted.

### 4B.3 Pass 3 — Business Concept Binding Pass

After Pass 1 + Pass 2 have populated the characteristic and entity caches, the 773 BC targets are bound via Pass 3 BC-waves. Each BC-wave is a pure binding session — no vocabulary admission, no entity admission, no scope-broadening adjudication. The packet for each BC row carries:

- The resolved characteristic_id (from Pass 1's cache)
- The resolved entity_id (from Pass 2's cache)
- The OAGIS provenance citation (noun + component + field path)
- The sibling representation_term shape pin (from prior BCs on the same entity in this BC-wave)
- The F3 createBusinessConcept invocation

**BC-wave breakdown by entity domain** (cache-cluster groupings — bound in batches sharing the same entity context, maximising per-entity packet prefix cache reuse):

| BC-wave | Domain | Entities receiving BCs | Approx BCs | Class profile |
|---|---|---|---|---|
| **BC-AR** | AR existing entities | Customer Invoice, CILI, Customer Invoice Adjustment, Customer Payment, Customer Shipment, Customer, Credit Application, Credit Status, Remittance Advice, Sales Order, Sales Order Line | ~75–95 | mostly AMBER (W-extend AR portion + W1/W2 AR-side) |
| **BC-AP** | AP existing entities | Supplier Invoice, Supplier Invoice Line, Purchase Order, Purchase Order Line, Goods Receipt, Goods Receipt Line, Vendor Payment, Supplier | ~85–110 | mostly AMBER (W-extend AP portion + W1/W2 AP-side) |
| **BC-GL** | GL existing entities | Journal Entry, Journal Entry Line, GL Account | ~70–85 | AMBER (W-extend GL + W3 + W4) |
| **BC-Bank** | Bank existing entities | Bank Account, Bank Statement, Bank Statement Line, Currency Exchange Rate | ~50–65 | mostly AMBER (W-extend Banking portion + W1 banking-side) |
| **BC-Master** | New master-data entities | Item, Business Partner, Cost Centre, Location, Org Unit, Party, Price List, Price List Item, Project | ~50–70 | AMBER (binds to E1 + E2 admissions + Pass 1 characteristics) |
| **BC-Procurement** | New procurement entities | Purchase Requisition + Line, Outline Agreement + Line, RFQ + Line, Quote + Line | ~30–40 | AMBER (binds to E3 + Pass 1) |
| **BC-Inventory** | New inventory entities | Inventory Position (composite), Inventory Movement + Line, Inventory Count + Line | ~25–30 | AMBER for binding to simple entities; **AMBER-with-composite-pin** for Inventory Position bindings (identity-tuple membership) |
| **BC-Production-simple** | New production simple entities | Work Order, Routing, BOM, Production Confirmation, Production Schedule, Manufacturing Process, Work Centre | ~35–45 | AMBER (binds to E5 + Pass 1) |
| **BC-Production-composite** | New production composite entities | Work Order Operation, Operation, BOM Line | ~20–25 | AMBER-with-composite-pin (binds to E6 + Pass 1) |
| **BC-Logistics** | New logistics entities | Delivery, Pick List + Line, Shipment Request, Shipment Unit, Three-Way Match + Line | ~75–90 | AMBER (binds to E7 + Pass 1) |
| **BC-Quality-simple** | New quality simple entities | Certificate, Corrective Action, Nonconformance + Line, Test Method | ~25–35 | AMBER (binds to E8 + Pass 1) |
| **BC-Quality-composite** | New quality composite entities | Inspection Lot, Test Result | ~10–15 | AMBER-with-composite-pin (binds to E9 + Pass 1) |
| **BC-Workforce** | New workforce entities | Employee | ~4 | AMBER (binds to E10 + Pass 1) |
| **BC-Asset** | New asset / maintenance entities | Asset, Equipment, Maintenance Order, Maintenance Order Operation (composite) | ~50–60 | AMBER + AMBER-with-composite-pin (binds to E11 + E12 + Pass 1) |
| **BC-Reference** | New reference / warranty / budget entities | Budget Ledger Entry + Line, Warranty Claim | ~12–18 | AMBER (binds to E13 + Pass 1) |
| **TOTAL** | | | **773 BCs** | (count reconciles to §4A.3) |

**Pass 3 completion criterion (C3'):** for each BC row: `authored_active` OR `authored_idempotent` (preferred); `panel_parked` / `panel_rejected` / `blocked_transient` (recorded per-row failure, agent continues); `red_held` (composite-identity pin still required); `deferred_*` (pull condition unmet).

### 4B.4 Reconciliation with §4A.7

| §4A.7 wave | BCs | Pass 1 contribution | Pass 2 contribution | Pass 3 BC-wave landing |
|---|---|---|---|---|
| W1 Payment parity | 10 | 4 chars in C1/C2/C3 | 0 | BC-AR + BC-AP + BC-Bank |
| W2 Order Line parity | 20 | 9 chars across C1–C5 | 0 | BC-AR + BC-AP |
| W3 GL JE Line | 26 | 12 chars across C1/C3 | 0 | BC-GL |
| W4 GL housekeeping | 3–5 | 0–1 chars (`posting period code` per §11.6) | 0 | BC-GL |
| W5 Item | 25 | 23 chars across C1–C6 | 1 entity in E1 | BC-Master |
| W6 Inventory composite | 25 | 13 chars across C1/C3 | 5 entities in E4 (1 RED + 4 AMBER) | BC-Inventory |
| W7 Procurement | 35 | 9 chars in C1 | 8 entities in E3 | BC-Procurement |
| W8 Production / WIP | 67 | 40 chars across C1–C5 | 10 entities in E5 + E6 (7 AMBER + 3 RED) | BC-Production-simple + BC-Production-composite |
| W9 Logistics | 85 | 57 chars across C1–C5 | 7 entities in E7 | BC-Logistics |
| W10 Quality | 49 | 27 chars across C1–C5 | 7 entities in E8 + E9 (5 AMBER + 2 RED) | BC-Quality-simple + BC-Quality-composite |
| W11 Workforce | 4 | 2 chars in C2/C6 | 1 entity in E10 | BC-Workforce |
| W12 Asset / Maint | 58 | 44 chars across C1–C5 | 4 entities in E11 + E12 (3 AMBER + 1 RED) | BC-Asset |
| W13 Master-data | 74 | 38 chars across C1–C5 | 8 entities in E2 | BC-Master |
| W14 Ref / Warranty / Budget | 16 | 10 chars across C1–C5 | 3 entities in E13 | BC-Reference |
| W-extend | 279 | 98 chars across C1–C5 (mostly C1 + C2) | 0 | BC-AR + BC-AP + BC-GL + BC-Bank |
| **TOTAL** | **773** | **~224 bf_names → ~90–130 admitted** | **54** | **773 BCs across 15 BC-waves** |

The 773 BC target is preserved across both views. §4A is retained as the per-domain audit view; §4B is the layer-first execution view.

### 4B.5 Cost / cache implications

| Metric | Mixed-wave (historical; pre-§1A) | Layer-first (post-§1A) |
|---|---|---|
| Estimated total panel sessions | ~140 (one per characteristic + ~25 per entity + per-BC binding sessions, with high adjudication overlap) | ~95 (~70 char + ~14 entity + ~13 BC-wave sessions, each cache-cohesive) |
| Average cache hit rate per session | ~20–40% (heterogeneous prefix) | ~60–85% (homogeneous prefix per layer) |
| Park / reject rate due to mixed-decision ambiguity | High (Wave A/B showed 2 parks in 1 session — both vocabulary surfacing inside BC binding) | Structurally eliminated for vocabulary-in-binding parks; per-row binding parks still possible but bounded |
| Operator decision burden | ~150–180 distinct decisions interleaved with binding sessions | ~70–100 grouped decisions in Pass 1 + ~50 entity decisions in Pass 2 + minimal in Pass 3 |
| Wall-time-to-completion estimate | ~16–22 hours of panel execution + ~30–50 hours of operator decision time | ~10–14 hours of panel execution + ~20–30 hours of operator decision time |

Estimates are blueprint-level. Actual cost is measurable at execution time via `bcf.panel_output_record` token + duration columns.

## 5. Wave list — layer-first (per §1A three-pass model)

The wave list below replaces the prior mixed W1–W14 + W-extend table. The same 773 BC target backlog is now sequenced as Pass 1 (C-waves) → Pass 2 (E-waves) → Pass 3 (BC-waves). Counts reconcile to §4A.3 and §4B.4.

Each wave declares: **new characteristics admitted · new entities admitted · BC bindings unlocked · class (GREEN/AMBER/RED/DEFER) · halt rules**. The same backbone-doctrine rules apply (coherent slice, complete-enough vs complete, continue-to-exhaustion within session); the layer-first arrangement adds cache discipline.

### 5.1 Row execution classification (unchanged from §8.2)

The row classification is unchanged from the program-level execution policy — what changes under §1A is the **sequencing** of rows across waves, not the row classes themselves.

| Class | Row definition | Default execution mode under program approval |
|---|---|---|
| **GREEN** | Pure EE_EC_BC reuse — existing entity bound to existing safe-autonomous-reuse-whitelist characteristic with sibling-shape match already in substrate. | Autonomous. |
| **AMBER** | One of: (a) EE_NC (new characteristic on existing entity) where F4-v2 v1 admission gates pass + operator-pinned shape; (b) EE_EC_BC where the characteristic is on hold-from-autonomous list but operator has authorised the binding-specific shape; (c) DEC-fb0b12 editorial amendment with E1–E6 pre-decided; (d) **simple-entity admission via createEntity panel with operator-pinned name + family + classification (introduced under layer-first model — Pass 2 simple entities)**. | Autonomous only if the blueprint or retry ledger carries the explicit pinned decision for the row. Otherwise halt for pin. |
| **RED** | New characteristic admission with first-of-kind shape (no sibling precedent) OR composite-identity entity admission (BCR §4 acyclicity graph required) OR Foundation-level tension requiring ADR / operating-model note OR cross-registry effect. | Held — never executed under program authorisation. Requires separate operator decision packet. |
| **DEFER** | Source-diagnostic-deferred (Bucket 7) OR pull-gated vocabulary capacity (orphan rule from §1) OR runtime-derived (Bucket 5) OR metadata (Bucket 6). | Held — never executed. Activation requires a concrete pull event recorded as a new ledger row. |
| **UNKNOWN** | Any row whose classification is not unambiguously GREEN / AMBER / RED / DEFER — including unmapped nouns (Bucket 8) and rows the profiler could not score. | Fatal stop. Operator triage required before any row can be reclassified. |

Note the layer-first refinement: **simple-entity admissions are AMBER under program approval** (previously they were lumped under RED). Composite-entity admissions remain RED. This refinement reflects that simple entity admission via `createEntity` is operationally analogous to characteristic admission — operator pins name + family + classification, then the F3 panel admits the entity row.

### 5.2 Pass 1 — Characteristic-vocabulary waves (C-waves)

Six characteristic-admission waves grouped by representation_term, plus C-DEFER (catalogue of deferred candidates) and C-RED (catalogue of operator-decision-held candidates).

| Wave | Cluster | Admission rationale (illustrative; primary AR + secondaries) | New characteristics | New entities | BC bindings unlocked | Class | Halt rules |
|---|---|---|---|---|---|---|---|
| **C1** | `code` characteristics | OTIF + reconciliation chains need payment_method, incoterms, transport_mode, UoM, valuation_class, quality_status, inspection_result, operation, material_type codes | ~20–25 admitted | 0 | Caches codes for ~250+ downstream BCs in BC-Logistics, BC-Procurement, BC-Quality, BC-Production, BC-AR/AP | AMBER | Halt on any candidate whose definition narrows to a single source system (Vocab §11.1 system-agnosticism); halt on any closed-set representation_term mismatch (M3/M7 of admission checklist). |
| **C2** | `date` (+ timestamp) characteristics | OTIF, planning-vs-actual variance, expiry/effective windows, maintenance lifecycle need promised/required/scheduled/actual ship/delivery/start/completion/inspection dates | ~15–20 admitted | 0 | Caches temporals for ~180+ downstream BCs | AMBER | Halt on `fiscal period` / `fiscal year` proposal (forbidden per §11.6); halt on any date characteristic colliding with `posting date` / `document date` semantics without operator distinguish-rationale. |
| **C3** | `identifier` characteristics | Composite-identity components (serial, batch, routing_id, BOM_id, inspection_plan_id, operation_id) + reference identifiers (cost_centre, employee, asset, work_centre) needed by Pass 2 + Pass 3 | ~15–20 admitted | 0 | Pre-loads identifiers required by E4/E6/E9/E12 composite admissions + unlocks ~80+ BC bindings | AMBER | Halt on any identifier-scheme bf_name (cageid, dunsid, dodaacid, scacid, upcid, epcid, dunsid) — these are source-diagnostic per §11.1 and route to C-DEFER. |
| **C4** | `amount` characteristics | Tax base + functional-currency arithmetic, asset acquisition + depreciation, freight, totals (non-derived) needed by AR/AP/GL + asset metrics | ~10–15 admitted | 0 | Unlocks ~60+ amount BCs across BC-AR / BC-AP / BC-GL / BC-Asset / BC-Logistics | AMBER | Halt on `total_*` candidate — operator decides between RUNTIME_DERIVED (most cases) vs source-attested (rare). Halt on `freight_amount` vs existing `freight charge` — DEC-fb0b12 E1–E6 if reuse path; supersession if not. |
| **C5** | `quantity` / `count` characteristics | Production variance, defect tracking, weight estimates, lead-time activation | ~5–10 admitted | 0 | Unlocks ~30+ quantity BCs across BC-Production / BC-Quality / BC-Logistics / BC-Procurement | AMBER | Halt on `cycle time` activation attempt (already orphan + §11.6 metric-derived). Halt on weight-measure characteristic candidates that fall below logistics-detail threshold without explicit operator pull. |
| **C6** | `text` / `indicator` characteristics | Free-form short names, titles, handling notes, three-way-match presence indicators | ~5–10 admitted | 0 | Unlocks ~20+ BCs across multiple BC-waves | AMBER | Halt on `description` / `note` proposal — already exist; the candidate is reuse not new. Halt on any indicator characteristic that conflates with `status` semantics. |
| **C-DEFER** | source-diagnostic catalogue | n/a (no pull) | 0 admitted; ~70–80 recorded as `deferred_diagnostic` | 0 | 0 | DEFER | n/a — held until pull surfaces. |
| **C-RED** | per-row operator decisions | Characteristics colliding with §11.6 forbidden names, requiring supersession, or first-of-kind shape without precedent | 0 autonomous; ~5–15 held with operator decision packet | 0 | 0 | RED | n/a — separate per-row operator packet required. |
| **Pass 1 TOTAL** | | | **~70–100 admitted**, **70–80 deferred**, **~5–15 RED-held** | 0 | Enables Pass 3 binding for ~470+ BCs that would otherwise stall on vocabulary | | |

### 5.3 Pass 2 — Entity-backbone waves (E-waves)

Thirteen entity-admission waves grouped by domain and dependency. E1 is the master-data root (Item); E4 / E6 / E9 / E12 are the composite-identity waves (RED). All others are simple-AMBER under program approval.

| Wave | Cluster | Admission rationale (primary AR + secondaries) | New characteristics | New entities | BC bindings unlocked | Class | Halt rules |
|---|---|---|---|---|---|---|---|
| **E1** | Master data root | Inventory + Production + Procurement + Logistics all depend on Item identity | 0 | **1** (Item, simple) | Unlocks ~25 Item BCs in BC-Master | AMBER (simple) | Halt on operator deciding Item composite vs simple after preflight pin; halt on Item family-classification ambiguity (Material vs Stock vs Product). |
| **E2** | Master data | Reporting cuts, allocation, multi-site analytics | 0 | **8** (Business Partner, Cost Centre, Location, Org Unit, Party, Price List, Price List Item, Project) | Unlocks ~50–70 BCs in BC-Master | AMBER (all simple) | Halt on Business Partner vs existing Customer/Supplier coalesce question; halt on Location granularity (site vs storage) decision. |
| **E3** | Procurement transactional | Requisition-to-PO cycle, contract compliance, sourcing-cycle metrics | 0 | **8** (Purchase Requisition + Line, Outline Agreement + Line, RFQ + Line, Quote + Line) | Unlocks ~30–40 BCs in BC-Procurement | AMBER | Halt on Outline Agreement vs Contract entity-name collision; halt on RFQ ↔ Quote semantic disambiguation. |
| **E4** | Inventory composite pilot | Inventory turn, DSI, stock-out — activates orphan `quantity on hand` | 0 | **5** — Inventory Movement, Inventory Movement Line, Inventory Count, Inventory Count Line (simple AMBER) + **Inventory Position (composite RED)** | Unlocks ~25 BCs in BC-Inventory | mixed (4 AMBER + 1 RED) | Halt on Inventory Position composite-identity acyclicity failure (BCR §4); halt on identity-tuple membership decision (Item × Location × Batch?). RED held until operator packet drafted. |
| **E5** | Production simple | Shop-floor variance, OEE baseline, throughput | 0 | **7** (Work Order, Routing, Bill of Materials, Production Confirmation, Production Schedule, Manufacturing Process, Work Centre) | Unlocks ~35–45 BCs in BC-Production-simple | AMBER | Halt on Production Schedule vs Manufacturing Process coalesce question; halt on Work Centre family classification. |
| **E6** | Production composite | Operation-level variance, BOM accuracy | 0 | **3** (Work Order Operation, Operation, Bill of Materials Line — all composite RED) | Unlocks ~20–25 BCs in BC-Production-composite | RED | Halt on composite-identity acyclicity for any of the 3; held until operator packet drafted for each. |
| **E7** | Logistics | OTIF, fill rate, three-way-match | 0 | **7** (Delivery, Pick List + Line, Shipment Request, Shipment Unit, Three-Way Match Document + Line) | Unlocks ~75–90 BCs in BC-Logistics | AMBER | Halt on Delivery vs Customer Shipment coalesce (OQ-5); halt on Three-Way Match Document identity (is it composite over PO × GR × SI?). |
| **E8** | Quality simple | Quality acceptance rate baseline | 0 | **5** (Certificate, Corrective Action, Nonconformance Notification + Line, Test Method) | Unlocks ~25–35 BCs in BC-Quality-simple | AMBER | Halt on Corrective Action vs Nonconformance overlap question. |
| **E9** | Quality composite | Detail-level defect rate, test-result tracking | 0 | **2** (Inspection Lot, Test Result — both composite RED) | Unlocks ~10–15 BCs in BC-Quality-composite | RED | Halt on Inspection Lot identity tuple (Item × Batch × Inspection Plan?); halt on Test Result identity (Inspection Lot × Characteristic?). |
| **E10** | Workforce | Headcount, attrition, span of control | 0 | **1** (Employee) | Unlocks ~4 BCs in BC-Workforce | AMBER | Halt on PII classification decision (which Employee attributes are PII?); halt on Position vs Job distinction (deferred to operator). |
| **E11** | Asset / Maintenance simple | Asset utilisation, maintenance cost, MTTR | 0 | **3** (Asset, Equipment, Maintenance Order) | Unlocks ~40–50 BCs in BC-Asset | AMBER | Halt on Equipment vs Asset coalesce question. |
| **E12** | Maintenance composite | Operation-level maintenance variance | 0 | **1** (Maintenance Order Operation — composite RED) | Unlocks ~5–10 BCs in BC-Asset | RED | Halt on composite-identity acyclicity; held until operator packet drafted. |
| **E13** | Reference / Warranty / Budget | Budget vs actual, warranty cost tracking | 0 | **3** (Budget Ledger Entry + Line, Warranty Claim) | Unlocks ~12–18 BCs in BC-Reference | AMBER | Halt on Budget Ledger Entry vs Journal Entry distinction (is Budget Ledger a parallel structure or extension?). |
| **Pass 2 TOTAL** | | | 0 | **~47 simple-AMBER + ~7 composite-RED = 54** | Enables Pass 3 binding for ~340+ BCs that would otherwise stall on entity admission | | |

### 5.4 Pass 3 — Business-Concept-binding waves (BC-waves)

Fifteen BC-binding waves grouped by entity domain. Each wave binds only — no vocabulary admission, no entity admission, no scope adjudication. Per-row Maker packets cite Pass 1 cached characteristic decisions + Pass 2 cached entity decisions + OAGIS provenance.

| Wave | Cluster | New characteristics | New entities | BC bindings | Class | Halt rules |
|---|---|---|---|---|---|---|
| **BC-AR** | Customer Invoice, CILI, Customer Invoice Adjustment, Customer Payment, Customer Shipment, Customer, Credit Application, Credit Status, Remittance Advice, Sales Order, Sales Order Line | 0 (Pass 1 cached) | 0 (Pass 2 cached) | **~75–95** | AMBER | Halt on any sibling representation_term ambiguity surfacing during binding — refer to Pass 1 follow-up packet. Halt on `posted amount` per-line vs header question (operator decision held; see scope audit §3.3). |
| **BC-AP** | Supplier Invoice, SI Line, Purchase Order, PO Line, Goods Receipt, GR Line, Vendor Payment, Supplier | 0 | 0 | **~85–110** | AMBER | Halt on `ordered quantity` CILI/GR Line wording question (OQ-2). Halt on AR↔AP asymmetry on non-whitelist characteristic (becomes follow-up packet). |
| **BC-GL** | Journal Entry, JE Line, GL Account | 0 | 0 | **~70–85** | AMBER | Halt if Maker proposes `fiscal period` binding (forbidden per §11.6). Halt on `document type code` scope question without Pass 1 verdict cached. |
| **BC-Bank** | Bank Account, Bank Statement, Bank Statement Line, Currency Exchange Rate | 0 | 0 | **~50–65** | AMBER | Halt on BSL × `line number` outlier remediation question (OQ-8 deferred). |
| **BC-Master** | Item, Business Partner, Cost Centre, Location, Org Unit, Party, Price List, Price List Item, Project | 0 | 0 (E1 + E2 cached) | **~50–70** | AMBER | Halt on Item characteristic binding that the operator did not pre-resolve at E1 family-classification decision. |
| **BC-Procurement** | Purchase Requisition + Line, Outline Agreement + Line, RFQ + Line, Quote + Line | 0 | 0 (E3 cached) | **~30–40** | AMBER | Halt on Requisition vs PO relationship characteristic (lineage_through_PO_identifier — operator decision). |
| **BC-Inventory** | Inventory Position (composite), Inventory Movement + Line, Inventory Count + Line | 0 | 0 (E4 cached) | **~25–30** | AMBER + AMBER-with-composite-pin | Halt on `quantity on hand` binding to Inventory Position without identity-tuple pin in evidence (E4 decision must be cached). Halt on composite-identity component binding without composite-pin. |
| **BC-Production-simple** | Work Order, Routing, BOM, Production Confirmation, Production Schedule, Manufacturing Process, Work Centre | 0 | 0 (E5 cached) | **~35–45** | AMBER | Halt on attempt to bind metric-derived `cycle time` (orphan, §11.6 forbidden). |
| **BC-Production-composite** | Work Order Operation, Operation, BOM Line | 0 | 0 (E6 RED packets active) | **~20–25** | AMBER-with-composite-pin | Halt on any binding without composite-identity tuple in evidence (E6 RED packets must be operator-decided and active before BC-wave runs). |
| **BC-Logistics** | Delivery, Pick List + Line, Shipment Request, Shipment Unit, Three-Way Match + Line | 0 | 0 (E7 cached) | **~75–90** | AMBER | Halt on `freight charge` scope question (DEC-fb0b12 E1–E6 if reuse path; supersession if not — Pass 1 verdict required). |
| **BC-Quality-simple** | Certificate, Corrective Action, Nonconformance + Line, Test Method | 0 | 0 (E8 cached) | **~25–35** | AMBER | Halt on Corrective Action characteristic binding that overlaps with Nonconformance semantics. |
| **BC-Quality-composite** | Inspection Lot, Test Result | 0 | 0 (E9 RED packets active) | **~10–15** | AMBER-with-composite-pin | Halt on composite-identity tuple binding without E9 RED packet active. |
| **BC-Workforce** | Employee | 0 | 0 (E10 cached) | **~4** | AMBER | Halt on PII characteristic binding without explicit PII tag (Pass 1 must have admitted Employee characteristics with PII flag). |
| **BC-Asset** | Asset, Equipment, Maintenance Order, Maintenance Order Operation (composite) | 0 | 0 (E11 + E12 cached) | **~50–60** | AMBER + AMBER-with-composite-pin | Halt on Maintenance Order Operation binding without composite-pin from E12. Halt on depreciation amount binding question (Pass 1 verdict required on runtime-vs-source-attested). |
| **BC-Reference** | Budget Ledger Entry + Line, Warranty Claim | 0 | 0 (E13 cached) | **~12–18** | AMBER | Halt on Budget Ledger Entry × `posting date` binding if Budget Ledger semantics aren't fully distinguished from Journal Entry (E13 entity decision must be conclusive). |
| **Pass 3 TOTAL** | | 0 | 0 | **773 BCs** (reconciles to §4A.3) | | |

### 5.5 Layered wave-types — definitions

| Wave-layer | Wave type | What it does | What it does NOT do |
|---|---|---|---|
| **Pass 1 (C-waves)** | **characteristic-admission** | Admits / amends / supersedes characteristics via F4-v2 v1 panel. Caches per-characteristic decisions for downstream layers. | Does NOT admit entities. Does NOT bind BCs. |
| **Pass 2 (E-waves)** | **entity-admission** | Admits / coalesces / splits entities via `createEntity` panel. Caches per-entity decisions for Pass 3. | Does NOT admit characteristics (Pass 1 cache reads only). Does NOT bind BCs. |
| **Pass 3 (BC-waves)** | **bc-binding** | Binds `(entity, characteristic)` BCs via F3 `createBusinessConcept` panel. Cites Pass 1 + Pass 2 caches. | Does NOT admit characteristics (Pass 1 cache reads only). Does NOT admit entities (Pass 2 cache reads only). Does NOT scope-broaden (parks for Pass 1 follow-up if surfaced). |
| **Any pass** | **operator-decision packet (RED)** | Drafts the held packet for an operator decision (composite-identity graph, supersession rationale, ADR proposal). Does NOT execute panels. | Does NOT advance autonomous execution; RED rows wait. |
| **Any pass** | **deferred (DEFER)** | Records the deferred candidate with rationale + pull condition. | Does NOT execute panels; held indefinitely until pull. |

## 6. Persistent retry ledger design

### 6.1 Why a ledger

Without a persistent ledger, every session re-litigates which OAGIS fields are filtered, which BCs are pending, and which entities are gating downstream waves. The Evidence-Governed Foundation Buildout rule (§1) requires the registry to record every candidate's admission_rationale + used_by_bc_target_count + entity_slice_name — Markdown-only memory fragments across sessions, and the existing `bcf.panel_output_record` only captures panel-execution history, not pre-admission pipeline state.

The ledger is the substrate-of-record for the buildout itself.

### 6.2 Statuses

The statuses below align with §8.2 row execution rules and §8.3 nonfatal outcomes. The agent transitions a row across statuses as work progresses; the operator transitions only at A1–A5 program approval, RED-row decisions, and parked/rejected/blocked triage.

| Status | Meaning | Set by | Next-action surface |
|---|---|---|---|
| `proposed` | Listed in this blueprint's catalogue (§4A). No A1–A5 program approval yet. | Blueprint authoring | Operator A1–A5 review surfaces this row for program-level authorisation. |
| `program_authorized` | The program's A1–A5 has been approved. This row is in-scope for autonomous execution per §8.2 if its class is GREEN or AMBER-with-pin. | Operator (program-level A1–A5 act) | Wave executor picks this row when the wave starts. |
| `packet_pending` | Held packet drafted for a RED-class wave; row awaits operator entity / doctrine decision. | Agent (wave preflight) | Operator reads the packet; transitions rows to `program_authorized` (becomes executable) or `withdrawn` / `deferred_*`. |
| `panel_pending` | Row is queued for the next F3 panel call. | Agent (wave entry) | Wave executor schedules panel call. |
| `panel_running` | F3 panel call in flight. | Agent (at panel invocation) | Telemetry stream; fatal-stop triggers if applicable. |
| `authored_active` | BC / characteristic / entity is `lifecycle_state='active'` after the panel run. Happy path. | Agent (on panel success) | Terminal — successful row. |
| `authored_idempotent` | The proposed `(entity, characteristic)` BC already existed active prior to the panel call. No new substrate row written; the row is satisfied by prior state. | Agent (preflight idempotency check) | Terminal — idempotent success. |
| `panel_parked` | Moderator returned `OPERATOR_REVIEW`. Panel output preserved in `bcf.panel_output_record`. Nonfatal — agent continues with next row. | Agent (on panel park) | Operator triage. Transitions to `withdrawn`, `panel_pending` (retry with refined evidence), or `superseded_by` (link to follow-up row). |
| `panel_rejected` | Moderator returned `REJECT`. Per-row terminal failure; agent continues with next row. | Agent (on panel reject) | Operator triage. Usually terminal; rare retry with refined evidence. |
| `transient_retry` | A transient bc-ai / bc-core failure fired (5xx, timeout, parser stutter). Bounded retry pending. | Agent (on transient failure) | Auto-retried up to `MAX_TRANSIENT_RETRIES=3`. |
| `blocked_transient` | Bounded transient retries exhausted (`retry_count >= MAX_TRANSIENT_RETRIES`). Nonfatal — agent continues with next row; this row becomes operator triage. | Agent (on retry exhaustion) | Operator triage. Usually resolves to `panel_pending` after operator confirms upstream service is healthy. |
| `blocked_prereq` | Waiting on a prerequisite (e.g., parent entity admission). | Agent (preflight prerequisite check) | Auto-flips to `panel_pending` when prerequisite reaches `authored_active`. |
| `deferred_diagnostic` | Intentional deferral under Vocab Framework §11.3 (source-diagnostic). Stays held under §1 admission rule — no rationale currently evidences it. | Blueprint / operator | Stays open; revisits when a rationale becomes evidenced. |
| `deferred_pull_gated` | Vocabulary capacity; no rationale currently evidenced. Stays held under §1 Evidence-Governed Foundation Buildout. | Blueprint / operator | Stays open; activates when AR-1 / AR-2 / AR-3 / AR-4 / AR-5 evidence is recorded by operator. |
| `deferred_runtime` | Bucket A — resolver-stamped concept that lives at the canonical resolution boundary; never BCF. | Blueprint / agent | Terminal — not in BCF executable backlog. |
| `deferred_metadata` | Bucket B — envelope / admin field; not a business concept. | Blueprint / agent | Terminal — not in BCF executable backlog. |
| `superseded` | Predecessor of a successor row created via supersession path. | Operator decision + agent | Terminal — historical. |
| `withdrawn` | Operator cancelled the proposal. | Operator | Terminal. |
| `red_held` | RED-class row awaiting separate operator entity / doctrine decision. NEVER autonomously executable per §8.2. | Blueprint / operator | Operator decision packet (per Wave A/B convention) required before transitioning. |
| `unknown_halt` | Row classification could not be resolved to GREEN / AMBER / RED / DEFER. Fatal-stop trigger per §8.4. | Agent (on classification failure) | Operator triage required before any row can be reclassified. |

### 6.3 Schema (ledger row)

| Field | Type | Notes |
|---|---|---|
| `ledger_uid` | text (LDG-<6hex>) | Stable id; survives across sessions and storage migrations |
| `wave_uid` | text (`C1`..`C6` / `C-DEFER` / `C-RED` for Pass 1 · `E1`..`E13` for Pass 2 · `BC-AR` / `BC-AP` / `BC-GL` / `BC-Bank` / `BC-Master` / `BC-Procurement` / `BC-Inventory` / `BC-Production-simple` / `BC-Production-composite` / `BC-Logistics` / `BC-Quality-simple` / `BC-Quality-composite` / `BC-Workforce` / `BC-Asset` / `BC-Reference` for Pass 3) | References §5 layer-first wave list |
| `subject_kind` | enum | `entity` / `characteristic` / `business_concept` |
| `subject_name_proposed` | text | `Item`, `quantity on hand`, etc. |
| `proposed_entity_id` | uuid \| null | Existing entity id if known; else null with `entity_proposed_name` for new entities |
| `proposed_characteristic_id` | uuid \| null | Existing characteristic id if known; else null with `characteristic_proposed_term` for new characteristics |
| `proposed_rep_term` | enum (closed set per BCR §5) | `amount` / `code` / `count` / `date` / `identifier` / `indicator` / `quantity` / `text` |
| `proposed_data_type` | text | `string` / `code` / `decimal` / `integer` / `date` / `timestamp` / `boolean` |
| `proposed_semantic_role` | text | `amount` / `identity` / `dimension` / `descriptive` / `temporal` / `status` |
| `oagis_provenance` | json | `{ noun, component, field_path, oagis_data_type, oagis_representation_term, source_url, source_version, cited_text }` |
| `filter_bucket` | enum | A / B / C / D / E / F per §3.1 |
| `f4_v2_classification` | enum | `global` / `industry` / `system` / `alias` / `reject` / `n_a` (n/a for entity + BC subjects) |
| `f4_v2_verdict` | json \| null | For characteristic rows: the F4-v2 v1 admission checklist verdict per item M1–M10 + SHOULD/MAY rationales. Populated by operator at A1–A5 approval. |
| `substrate_role` | enum | `canonical_metric` / `source_diagnostic` / `composite_identity_component` |
| `admission_rationale` | array[enum] | One or more of `known_metric_pull` / `source_chain_pull` / `entity_backbone_completeness` / `standards_backed_foundation` / `operator_strategic_priority` per §1.2. First entry is primary; remainder are secondary. |
| `admission_rationale_evidence` | json | Per-rationale evidence: `{ AR_1: { metric_uid }, AR_2: { source_contract_uid, admission_contract_uid }, AR_3: { backbone_slice_name, load_bearing_role }, AR_4: { oagis_section_ref, standards_version }, AR_5: { initiative_name, operator_id, rationale_text_min_40 } }`. Empty entries permitted; at least one rationale must be fully populated for `executable` status. |
| `used_by_bc_target_count` | integer | (Characteristic rows only.) Count of downstream BC ledger rows that reference this characteristic in their proposed binding. `>= 1` required for admission per §1.4 Safeguard 1. |
| `target_entities` | array[uuid \| text] | (Characteristic rows only.) Set of entity_ids or proposed entity names where this characteristic will be bound. |
| `target_waves` | array[wave_uid] | (Characteristic rows only.) Set of waves (BC-AR / BC-AP / etc.) where this characteristic is consumed by BC rows. Used for Pass 1 sequencing. |
| `entity_slice_name` | text \| null | (Entity rows only.) The coherent entity slice this entity belongs to. Required for admission per §1.4 Safeguard 2. |
| `composite_identity_decision` | json \| null | (Entity rows only.) `{ kind: simple / composite, identity_bearing_properties: [...], acyclicity_verified: bool }`. Required for composite entities; null for simple. |
| `prereq_ledger_uids` | array[ledger_uid] | Other ledger rows that must reach `authored_active` first |
| `status` | enum | Per §6.2 |
| `status_at` | timestamp | Last status change |
| `status_reason` | text | Why this status (operator note or system note) |
| `last_panel_run_uid` | uuid \| null | From `bcf.panel_output_record` if applicable |
| `last_create_cert_uid` | uuid \| null | From `bcf.certification_record` if applicable |
| `last_activation_cert_uid` | uuid \| null | From `bcf.certification_record` if applicable |
| `linked_subject_uid` | uuid \| null | Once authored: entity_id / characteristic_id / business_concept_id |
| `halt_reason` | text | If status involves a halt — verbatim halt reason |
| `retry_count` | integer | Number of panel runs attempted on this row |
| `next_action_text` | text | Free-form direction for the next session that picks this row up |
| `class` | enum | `GREEN` / `AMBER` / `RED` / `DEFER` / `UNKNOWN` per §5.1 row classification — drives §8.2 execution rule |
| `pin_evidence_text` | text \| null | For AMBER rows: the explicit pinned decision that admits autonomous execution. E.g., representation_term shape pin (`identifier/string/identity`), DEC-fb0b12 E1–E6 verdict, F4-v2 classification (`global, approved per checklist v1`). Null for GREEN / RED / DEFER. |
| `program_authorized_at` | timestamp \| null | When the operator's A1–A5 act flipped the row into `program_authorized`. Null until program approval. |
| `transient_retries_remaining` | integer | Decremented on each transient retry; the row becomes `blocked_transient` at 0. Default `MAX_TRANSIENT_RETRIES=3`. |
| `packet_hash` | text (sha256) | Computed by §6A Compile layer: SHA-256 over `(entity_id_or_proposed_name, characteristic_id_or_proposed_term, representation_term, data_type, semantic_role, oagis_provenance, primary_admission_rationale)`. Used by §6B retry-cache invalidation. Recomputed on any field change above. |
| `retry_reason` | text \| null | Set on every transition from `panel_parked` / `panel_rejected` / `blocked_transient` back to `panel_pending`. States what changed since last attempt (substrate change, evidence refinement, operator override, or hash invalidation). Empty means no retry attempted. |
| `coordinator_run_id` | text (CRR-<6hex>) | Set by Coordinator (§6C.1) on row assignment. Survives across sessions. |
| `worker_id` | text (WKR-<6hex>) \| null | Set by Worker on row claim (§6C.6). Identifies the current owner of the row's in-flight step. Null when no claim. |
| `work_claimed_at` | timestamp \| null | Set by Worker on row claim. Null when no claim. |
| `claim_expires_at` | timestamp \| null | Set by Worker on row claim. Past expiry → row may be reclaimed by Coordinator. |
| `substrate_snapshot_hash` | text (sha256) | Set by Read worker on substrate-read at classification time. SHA-256 over `(entity_ids, characteristic_ids, business_concept_ids)` materialised view. Invalidates packet_hash if substrate changes. |
| `evidence_hash` | text (sha256) | Set by Packet worker on packet build. SHA-256 over `oagis_provenance.cited_text` + `admission_rationale_evidence` digest. Used to detect evidence refinement that warrants retry. |
| `panel_attempt_count` | integer | Set by Coordinator on panel handoff. Increments each time a panel worker invokes the panel for this row. Default 0. |
| `writer_attempt_count` | integer | Set by Writer on write handoff. Increments each time the writer attempts the substrate write for this row. Default 0. |
| `model_cost_estimate` | decimal (USD) \| null | Set by Packet worker before panel call. From per-provider price table × estimated token usage. |
| `model_cost_actual` | decimal (USD) \| null | Set by Panel worker after panel response. From provider usage headers. |
| `dependency_group` | text \| null | Set by A0 on classification. Logical grouping of rows that must execute in FIFO order at the writer (e.g., `bc-ar-customer-invoice-header`). Coordinator respects within-group order, may reorder across disjoint groups. |
| `write_queue_position` | integer \| null | Set by Writer on queue admission. Position in the writer's serialised queue at the moment of admission. |
| `final_prewrite_check_at` | timestamp \| null | Set by Writer on prewrite recheck (§6C.2). When the writer last performed the pre-write recheck for this row. |
| `final_prewrite_check_result` | enum \| null | Set by Writer on prewrite recheck. `ok` (proceed) / `idempotent_skip` (active row exists; transition to `authored_idempotent`) / `shape_mismatch_fatal` (substrate shape disagrees — fatal stop) / `collision_fatal` (different row holds the same `(entity, characteristic)` tuple — fatal stop). |
| `terminal_outcome_code` | enum \| null | Set by Coordinator on terminal transition. Per §6C.5 enum: `authored_active` / `authored_idempotent` / `panel_parked` / `panel_rejected` / `blocked_transient` / `red_held` / `deferred_diagnostic` / `deferred_pull_gated` / `deferred_runtime` / `deferred_metadata` / `superseded` / `withdrawn` / `unknown_halt`. Immutable once set unless explicit operator reset OR changed hash. |
| `created_at` | timestamp | Row creation |
| `created_by` | text | Session id + operator id |

### 6.4 Storage — Phase 1 (Markdown) + Phase 2 (DBCP candidate)

#### Phase 1 — Markdown ledger

File: `bc-docs-v3/docs/implementation/bcf-oagis-retry-ledger-2026-06-23.md` (sibling to this blueprint).

Shape: a Markdown table per wave, plus a top-of-file index. Each session that touches a ledger row updates the row in place via `Edit` and commits the file alongside the wave's closeout packet.

Pros: zero substrate footprint; fully versioned in git; reviewable in PR.

Cons: no concurrency safety (last-writer-wins); no programmatic query (must be parsed); no integration with `bcf.*` substrate.

#### Phase 2 — DBCP candidate

When Phase 1's overhead exceeds its benefit (likely around wave W5–W6 when entity admissions and composite-identity rows scale), file a DBCP for:

```
concept_registry.oagis_retry_ledger
  (one row per ledger entry; columns mirror §6.3)
  + indexes on (wave_uid, status), (proposed_entity_id), (status, status_at desc)
  + check constraint on filter_bucket / status / substrate_role
  + foreign keys to concept_registry.entity / characteristic / business_concept
    where the linked_subject_uid columns hold ids
```

Phase 2 is a **candidate** DBCP. It is not authorised by this blueprint. The DBCP itself requires its own held packet, operator decision, schema migration, and writer-service design.

### 6.5 DevHub task integration

The program is one DevHub PLN (`bcf-oagis-broad-buildout`) with `plan_uid` linking to this blueprint. Each wave is a task under the PLN; per-row state lives in the ledger. Closeout per wave produces a closeout packet (per Wave A/B convention) and flips the wave's DevHub task to `completed`. The program PLN closes only when §6.7 program completion is reached or operator withdraws A1–A5.

DevHub tasks complement, not replace, the ledger. The ledger is the per-row state; DevHub tasks are the per-(C/E/BC)-wave coordination surface; the PLN is the program-level coordination surface.

### 6.6 Session-resume protocol (program-level)

A future session resumes from the ledger as follows:

1. Read this blueprint to ground intent.
2. Read the Markdown ledger (Phase 1) — read the §6.7 program completion state header to determine program-level posture.
3. If `program_authorization='withdrawn'` or `unknown_halt` is set → operator triage required before any execution. Stop.
4. If `program_authorization='active'` and the in-flight wave has executable rows (rows where `class ∈ {GREEN, AMBER}` AND `status='program_authorized'` AND prerequisites satisfied) → resume executing the wave per §8.5 loop.
5. If the in-flight wave has only non-executable rows (RED held, DEFER, parked, rejected, blocked) → write the wave closeout (if not already written) + advance to the next wave with executable rows per §8.5.
6. Read the latest wave closeout packet (if a wave is mid-flight).
7. For each `transient_retry` row: check whether retry pre-conditions still hold (service health, auth fresh). If yes, execute next retry; if no, transition to `blocked_transient` and continue.
8. For each `blocked_prereq` row: check whether prerequisite is now `authored_active`. If yes, flip to `panel_pending` and execute; if no, leave held.
9. On every state transition: update the row in the Markdown ledger AND update the §6.7 program-completion state header.

The agent does not re-ask the operator between C / E / BC waves. Operator authorisation is at the program level (A1–A5); per-row execution is delegated to the agent under §8.2 row rules. The only events that pause the program for operator are: fatal stops (§8.4), parks / rejects / blocks (recorded for triage but agent continues), and the program-completion event itself (§6.7 closeout).

### 6.7 Program completion state header

A small structured block at the head of the Phase-1 Markdown ledger that the agent updates on every wave closeout. It is the single source of truth for "where is the BCF × OAGIS program right now".

```yaml
# bcf-oagis-program-completion-state — updated by each wave closeout

program_authorization: proposed | active | withdrawn | completed | halted
program_authorization_at: <ISO 8601 timestamp>
program_authorization_session: SES-xxxxxx
program_authorization_operator: <operator id>

budget_caps:
  total_panel_runs_max: <number, optional>
  total_token_spend_max: <number, optional>
  per_row_latency_max_seconds: <number, optional>
  total_wall_time_max_hours: <number, optional>

cumulative_progress:
  green_rows_total: <count>
  green_rows_authored_active: <count>
  green_rows_authored_idempotent: <count>
  green_rows_parked: <count>
  green_rows_rejected: <count>
  green_rows_blocked_transient: <count>
  amber_rows_total: <count>
  amber_rows_authored_active: <count>
  amber_rows_authored_idempotent: <count>
  amber_rows_parked: <count>
  amber_rows_rejected: <count>
  amber_rows_blocked_transient: <count>
  red_rows_total: <count>
  red_rows_held: <count>
  red_rows_packet_drafted: <count>
  defer_rows_total: <count>
  unknown_halt_rows_total: <count>

# Per-pass progress (layer-first model, §1A)
pass_1_characteristic:
  state: not_started | in_progress | complete | halted
  c1_state: { state, started_at, completed_at, admitted: count, deferred: count, red_held: count, parked: count, rejected: count }
  c2_state: { ... }
  c3_state: { ... }
  c4_state: { ... }
  c5_state: { ... }
  c6_state: { ... }
  c_defer_state: { recorded: count }
  c_red_state: { held: count, packet_drafted: count, decided: count }

pass_2_entity:
  state: not_started | in_progress | complete | halted
  e1_state: { state, started_at, completed_at, admitted: count, red_held: count }
  e2_state: { ... }
  # ... e3 through e13
  composite_red_pending: <count>
  composite_red_decided: <count>

pass_3_bc:
  state: not_started | in_progress | complete | halted
  bc_ar_state: { state, started_at, completed_at, authored: count, parked: count, rejected: count, blocked: count }
  bc_ap_state: { ... }
  bc_gl_state: { ... }
  bc_bank_state: { ... }
  bc_master_state: { ... }
  bc_procurement_state: { ... }
  bc_inventory_state: { ... }
  bc_production_simple_state: { ... }
  bc_production_composite_state: { ... }
  bc_logistics_state: { ... }
  bc_quality_simple_state: { ... }
  bc_quality_composite_state: { ... }
  bc_workforce_state: { ... }
  bc_asset_state: { ... }
  bc_reference_state: { ... }

fatal_stops:
  - { fired_at: ts, trigger: <§8.4 trigger name>, halt_reason: text, pass_affected: pass_1|pass_2|pass_3, resolved: bool }

last_updated_at: <ISO 8601 timestamp>
last_updated_session: SES-xxxxxx
```

An earlier draft used a `waves_state` block keyed by W1–W14 + W-extend under the mixed-wave model. Under the layer-first §1A model that block is replaced by the three pass blocks above. The per-pass state is the source of truth; no derived W-keyed projection is required for execution.

Completion criteria — the program transitions to `program_authorization='completed'` when all of these hold (§8.6):

| Criterion | Check |
|---|---|
| **C1** | All executable GREEN rows ∈ {`authored_active`, `authored_idempotent`} |
| **C2** | All executable AMBER rows ∈ {`authored_active`, `authored_idempotent`, `panel_parked`, `panel_rejected`, `blocked_transient`} |
| **C3** | All RED rows are `red_held` with `next_action_text` documented |
| **C4** | All DEFER rows are `deferred_*` with documented rationale |
| **C5** | No `unknown_halt` rows remain (all Bucket 8 SEMANTIC_AMBIGUITY_HALT rows resolved to a class) |

When C1–C5 hold, the agent writes a program-completion packet (`bcf-oagis-program-completion-<date>.md`) with cumulative counts, operator-handoff list (RED + parked + blocked + DEFER), and the final substrate delta. The program PLN closes.

## 6A. A0 — Program Compile / Preflight Layer (deterministic, no-LLM)

The Program Compile / Preflight Layer (also referenced as **A0** throughout this blueprint) is a deterministic, no-LLM step that runs against the OAGIS extract + live substrate snapshot to produce the executable retry ledger **before any panel runs**. It is the **only approved dry-run style** for this program — it saves cost and time by mechanically classifying every candidate row + checking pre-conditions, so that Pass 1 / Pass 2 / Pass 3 panel sessions execute pre-validated rows only.

### 6A.0 A0 authority — runs before A1–A5 (read-only) ; A1–A5 still gates all writes

A0 is **read-only / no-LLM / no-panel / no-substrate-mutation** by definition. It can therefore run **before** the operator records A1–A5 program-execution approval, because A1–A5 is required only for state changes — panel calls, entity admissions, characteristic admissions, BC authoring, confirmations, substrate writes — and A0 performs none of these. In fact A0 is needed precisely to produce the exact target ledger and counts the operator reviews at A1–A5.

The sequencing is:

| Step | Authority required | What it does | What it touches |
|---|---|---|---|
| **A0 — Compile / Preflight** | None beyond standard read access | Build retry ledger seed; classify every candidate; compute hashes; produce compile report + operator decision queue | Read-only OAGIS extract + read-only substrate snapshot |
| **A1–A5 — Program approval** | Operator decision | Approve §1 admission rule + §4A/§4A.10 catalogue + §4B/§5 layer-first wave list + §6 ledger + §6A/§6B + §8 row/halt rules + budget caps | None — paperwork act |
| **Pass 1 / Pass 2 / Pass 3** | A1–A5 must be recorded | Execute GREEN + AMBER-with-pin rows per §8 row execution rules | Substrate writes via F3 / F4-v2 / createEntity / createCharacteristic / createBusinessConcept governed paths |

Until A1–A5 is recorded, the agent may run A0 (and re-run it on substrate / extract / operator-override events per §6A.4), update the retry ledger, draft held packets, and amend the blueprint. The agent may **not** invoke any panel, write any substrate row, fire any certification, or amend any active characteristic / entity / BC.

### 6A.0.1 Counts policy — blueprint ranges vs A0 exact

The blueprint records counts at **ranged** granularity (e.g. "~90–130 admitted characteristics", "~80–120 AR-1 BCs"). Ranges reflect compile-time heuristic uncertainty and operator-deferral expectations.

**A0 produces the exact executable ledger.** Per A0 invocation:

| A0 output | Granularity |
|---|---|
| Proposed entity rows | Exact count + per-row name + family + simple-vs-composite proposal |
| Proposed characteristic rows | Exact count + per-row term + representation_term + data_type + semantic_role + F4-v2 v1 classification candidate |
| Proposed BC target rows | Exact count + per-row `(entity, characteristic)` tuple + OAGIS provenance + sibling shape pin (if available) |
| DROP / DEFER / RED / AMBER / GREEN counts | Exact per-bucket counts per Pass per wave |
| Packet hashes | One per row, computed deterministically |
| Evidence hashes | One per row's `oagis_provenance.cited_text` + `admission_rationale_evidence` digest |

The blueprint ranges + A0 exact counts coexist: blueprint ranges are operator-readable design targets; A0 exact counts are the operationally binding ledger seed. Operator A1 approval reads both — the blueprint range first (for sanity check), then the A0 exact counts (for ledger-row authorisation).

### 6A.0.2 Implementation reference

The A0 compile layer was prototyped in scratch form in prior session SES-a18549 as `barecount-devhub/scripts/_oagis-classify.mjs` (the bucket profiler). The full A0 layer extends that scratch profiler into the program's substrate-of-record seeder. Implementation work is not authorised by this blueprint; A4 program approval is required to enable A0 to run as the program's official seeder.

### 6A.1 What it does (in order)

| Step | Input | Output |
|---|---|---|
| **1 Read OAGIS extract** | `barecount-devhub/data/oagis-finance-extract-enriched-<version>.json` | All 133 nouns, 6,131 fields (2,868 scalar + 3,263 complex) loaded into memory |
| **2 Read live substrate snapshot** | `bc-postgres` MCP read-only against `concept_registry.*` | Active entities (26+), active characteristics (62+), active BCs (194+) loaded |
| **3 Dedupe OAGIS fields** | Step 1 output | Same `(noun, component, bf_name)` triple yields one candidate row; cross-noun bf_name reuse counted as multiple rows |
| **4 Map noun → entity** | Noun→entity mapping table | Component-aware split for header/line; role-split for Invoice/Payment/Shipment; new-entity proposals named |
| **5 Map bf_name → characteristic** | bf_name normalisation + alias table | Kebab→space; suffix stripping; alias matches; new-characteristic candidates named |
| **6 Classify into 8 buckets** | §3.1 + §3.2 decision tree | Every scalar field assigned: METADATA_DROP / RUNTIME_DERIVED_DROP / SOURCE_DIAGNOSTIC_DEFER / SEMANTIC_AMBIGUITY_HALT / EE_EC_BC / EE_NC / NE_EC / NE_NC |
| **7 Compute admission rationale candidates** | §1.2 rationales + per-row evidence | Which of AR-1..AR-5 plausibly apply; flagged for operator confirmation at A1–A5 |
| **8 Compute `used_by_bc_target_count` per characteristic** | Step 6 output | Count of BC ledger rows that bind this characteristic. Used by §1.4 Safeguard 1. |
| **9 Compute `target_entities` / `target_waves` per characteristic** | Step 6 + per-(C/E/BC)-wave allocation | Set of entities + (C/E/BC)-waves consuming this characteristic |
| **10 Compute `entity_slice_name` per entity** | Operator-pinned slice catalogue + §4B.2 E-wave grouping | Used by §1.4 Safeguard 2 |
| **11 Assign GREEN/AMBER/RED/DEFER/UNKNOWN** | §5.1 row rules | Every row carries a definitive class |
| **12 Check pinned decisions on AMBER rows** | `pin_evidence_text` populated or not | AMBER rows lacking pin flagged for operator triage |
| **13 Compute `packet_hash` per row** | SHA-256 over the 7-tuple (§6.3) | Used by §6B retry-cache invalidation |
| **14 Check collisions / idempotency** | Step 13 hashes vs prior ledger | (entity, characteristic) tuples already active in substrate flagged as `authored_idempotent` targets at first run |
| **15 Estimate wave cost** | Per-wave row counts × ~55–75s panel wall-time | Per-wave cost in seconds + per-pass cumulative cost |
| **16 Produce executable rows** | Rows where class ∈ {GREEN, AMBER-with-pin} AND `admission_rationale` ≥ 1 entry AND safeguards 1 + 2 satisfied AND prerequisites in DAG resolvable | Listed in compile report as `executable` |
| **17 Produce held rows** | Rows where class ∈ {AMBER-without-pin, RED, DEFER, UNKNOWN} | Listed in compile report as `held`; operator triage item per row |

### 6A.2 What it does NOT do

| Excluded action | Reason |
|---|---|
| Call any panel (F3 / F4-v2 / createEntity / createCharacteristic / createBusinessConcept) | The compile layer is deterministic and no-LLM by design |
| Call any LLM (bc-ai, Anthropic, Bedrock, OpenAI, etc.) | Same — no LLM evaluation in compile |
| Write any database row | Compile reads substrate; never mutates it |
| Issue any `bcf.certification_record` row | Certification fires only at panel execution time |
| Mutate any `concept_registry.*` or `bcf.*` row | Substrate is read-only during compile |
| Validate Foundation invariants beyond mechanical checks | Invariant validation happens at panel execution; compile only checks structural pre-conditions |
| Pre-approve any AMBER row's pinned decision | Pinning is the operator's act, not the compile layer's |
| Run any "shadow" / "trial" F3 invocation | No trial-panel runs of any kind |
| Make any commitment about whether a row will succeed at panel-time | Compile produces classification + executability; outcomes are determined at panel execution |

### 6A.3 Compile artefacts

The compile layer produces three artefacts at every run:

| Artefact | Format | Purpose |
|---|---|---|
| **Retry ledger seed** | Markdown table (Phase 1, per §6.4) OR DBCP-pending row set (Phase 2) | Per-row status `proposed`; per-row class; per-row rationale; per-row packet hash; per-row evidence |
| **Compile report** | Markdown document at `bc-docs-v3/docs/implementation/bcf-oagis-compile-report-<date>.md` | Bucket counts; classification breakdown; executable-vs-held split; wave cost estimate; halt pre-conditions for held rows; operator decision queue |
| **Operator decision queue** | Markdown table within the compile report | Per-held-row: what operator decision unblocks it (pin shape, decide entity simple-vs-composite, accept supersession, resolve UNKNOWN classification, etc.) |

The retry ledger seed is the **program's substrate-of-record**. Once operator A1–A5 approves the catalogue, the agent reads from this seed at every wave session start.

### 6A.4 When the compile layer runs

| Event | Compile action |
|---|---|
| Initial program execution | Full compile against OAGIS extract + substrate snapshot at A1–A5 approval time |
| Substrate change (new char / entity / BC active) | Incremental re-compile of affected rows; ledger updated; cache invalidation per §6B.4 |
| OAGIS extract version change | Full re-compile against new extract; new ledger seed; operator re-reviews catalogue |
| Operator override of admission rationale | Re-classification of affected rows; ledger updated |
| Wave closeout | Per-wave re-compile of next-wave rows incorporating substrate deltas from current wave |
| Characteristic definition amendment (DEC-fb0b12 editorial) | Re-compile of all BC rows binding the amended characteristic; `packet_hash` recomputed; downstream rows reclassified if needed |
| Characteristic supersession (new characteristic_id) | New ledger rows added for the successor; existing rows on predecessor preserved as historical |

### 6A.5 Compile layer authority

The compile layer is a **read-only diagnostic + ledger seeder**. It is not part of the F3 / C5 governed write path. It does not constitute admission; admission is the operator A1–A5 approval + the panel-execution outcome. Foundation Invariant VI (evidence is emitted) is satisfied at panel execution time; the compile layer's role is to ensure that evidence is *available* when the panel runs.

This is the **only approved dry-run style** for the BCF × OAGIS program. No "trial panel runs", "shadow F3 invocations", "preview certifications", "speculative entity admissions", or similar dry-run patterns are sanctioned anywhere in this blueprint or the program.

## 6B. Batch + Cache Execution Economy

This section defines the cost discipline for the program. It governs which operations may batch and which may not, the cache layers and their invalidation triggers, the retry economy, and a future microbatch-panel design (design only — **not authorised** by this blueprint).

### 6B.1 Safe batching — operations that may batch

| Operation | Batch policy | Rationale |
|---|---|---|
| Deterministic OAGIS profiling (§6A) | Full extract loaded once per compile run; all 133 nouns / 6,131 fields processed in one pass | Compile is mechanical; batching does not introduce risk |
| Substrate preflight reads per wave / pass | Single read transaction per pass start; cached for the pass's duration | Reduces DB round-trips; reads are stable per pass |
| Evidence packet construction | Pre-build packets for all rows in a wave before the wave's first panel call | Cache + reuse across rows; no LLM calls during construction |
| Ledger updates within a session | Buffer per-row updates within a session; flush to Markdown on session close | Reduces git churn; preserves ledger atomicity per session |
| Cost / time estimation per wave (§6A.1 step 15) | Compute once per compile; reuse during planning | Mechanical; reads only |

### 6B.2 NOT-yet-safe — operations that must NOT batch

| Operation | NOT-batched policy | Reason |
|---|---|---|
| **F3 / C5 substrate writes** | One panel call → one substrate write → one `bcf.certification_record` row | F3 single-writer service is the governed write path; bulk inserts bypass governance |
| **Certification acts** | One cert per row; never `bulk-confirm` multiple candidates in one cert | DEC-26b6e2 / DEC-fb0b12 require per-act cert traceability; bulk certs break the audit chain |
| **Operator decision packets** | One operator decision per row at A1–A5 time; multi-row pins permitted within one session but tracked per-row | Per-row provenance preserves DEC-fb0b12 E1–E6 + Foundation Invariant VI evidence emission |
| **Panel invocations** | One BC / characteristic / entity per panel call (current state) | Microbatch design in §6B.6 is not authorised; current Maker/Checker/Moderator design is per-row |
| **`concept_registry.entity` admissions** | One entity per `createEntity` panel call | Per-entity simple-vs-composite + family + classification decisions are per-row by design |
| **Characteristic admissions** | One characteristic per `createCharacteristic` panel call | F4-v2 v1 checklist per-row verdict; no batch-verdict possible |

### 6B.3 Cache layers

The program uses five primary cache layers and one optional provider-side cache.

| Cache layer | Scope | Stored in | Hit on |
|---|---|---|---|
| **OAGIS source-evidence cache** | Per-extract-version | Compile artefact + memory during session | Same `(noun, component, field_path)` across multiple ledger rows |
| **Substrate snapshot cache** | Per-pass session | Memory during session | Repeated reads of `concept_registry.*` / `bcf.*` during one session |
| **Candidate packet hash cache** | Per-row | Ledger row column `packet_hash` | Retry of same `(entity_id_or_proposed, characteristic_id_or_proposed, rep_term, data_type, semantic_role, oagis_provenance, primary_admission_rationale)` |
| **Sibling-shape cache** | Per-entity within a BC-wave session | Memory | Sequential BC bindings on the same entity reuse cached representation_term / data_type / semantic_role from prior rows in this session |
| **Prior outcome / retry ledger cache** | Per-program (persistent) | Ledger rows + closeout packets | Skip rows already `authored_active` / `authored_idempotent`; respect `panel_parked` / `panel_rejected` halt reasons until invalidation |
| **Provider prompt-prefix cache** (optional) | Per-session, provider-dependent | Provider cache control header (Anthropic ephemeral cache) | Wave session with stable prefix reuses cached prefix tokens (only if provider supports) |

### 6B.4 Invalidation triggers

Caches invalidate on the following events. The compile layer (§6A.4) detects invalidation events and triggers re-compile of affected rows.

| Event | Caches invalidated | Re-compile scope |
|---|---|---|
| Entity / characteristic / BC substrate change | Substrate snapshot cache (full); Sibling-shape cache (affected entity); Packet hash (recomputed if row shape changes) | Affected rows |
| Characteristic definition amendment (DEC-fb0b12 editorial) | Substrate snapshot cache (affected characteristic); BC ledger rows binding this characteristic — packet hash recomputed; retry permitted under new hash | Affected BC rows |
| Characteristic supersession (new characteristic_id) | All affected ledger rows reclassified; BCs binding predecessor remain historically correct (DEC-26b6e2); BCs targeting the successor become new ledger rows | New successor ledger rows + cross-referenced predecessor rows |
| OAGIS extract version change | OAGIS source-evidence cache (full); Full compile re-run; full ledger seed re-generated | All rows |
| Prompt / checklist version change | Provider prompt-prefix cache (full); `checklist_version` on every new panel run incremented | None (cache reset only) |
| Operator override of admission rationale or classification | Affected ledger rows reclassified; downstream caches per row change | Affected rows |
| Session-level write (any substrate mutation) | Substrate snapshot cache invalidated for next session's start | All rows next session reads |

### 6B.5 Retry economy

Three retry rules govern when a row may re-execute:

| Rule | Behavior |
|---|---|
| **No retry on unchanged packet_hash** | If a `panel_parked` / `panel_rejected` row's `packet_hash` is unchanged since the last attempt, do **NOT** retry — the same packet will produce the same outcome. Operator triage is required first (hash invalidation = new attempt). |
| **Retry on substrate / evidence / operator-decision change** | If substrate has changed (e.g., new sibling shape now provides a pin) OR the candidate evidence has been refined OR operator has overridden the disposition — recompute `packet_hash`, set `retry_reason` text, mark row as `panel_pending`, retry under the bounded transient-retry rule. |
| **Record retry_reason explicitly** | Every retry transition writes `retry_reason` to the ledger row — explicit, free-form text stating what changed since last attempt. Used for compile-time invalidation tracking and post-hoc audit. |

The bounded transient-retry rule from §6.3 `transient_retries_remaining` (default 3) applies to transient bc-ai / bc-core failures (5xx, timeout, parser stutter). It does **NOT** apply to candidate-specific parks / rejects — those require operator triage + hash invalidation before retry.

### 6B.6 Future microbatch panel — design only

> **NOT AUTHORISED by this blueprint.** Captured for future consideration. Adoption requires a separate operator decision packet + ADR proposal + bc-ai / bc-core implementation work.

A future microbatch panel would invoke the Maker / Checker / Moderator session once for N candidates that share a homogeneous shape (e.g., 3–5 BC bindings on the same entity in the same BC-wave, all reusing the same characteristic). The design constraints, recorded here so the future authorisation packet starts from a settled shape:

| Constraint | Reason |
|---|---|
| Max 3–5 same-shape candidates per microbatch | Bounds prompt-context size; preserves per-row reasoning quality |
| Per-row verdicts required (no batch-level verdict) | Moderator returns one verdict per row; Foundation Invariant VI requires evidence per evaluation act |
| Per-row evidence hashes required | Each row carries its own `evidence_hash` for audit cert pairing |
| Per-row cert / write path remains isolated | One `bcf.certification_record` per row; F3 single-writer one write per row; bulk inserts not permitted |
| Any systemic failure aborts the batch | Prompt / parser / cache-prefix failure across the batch → whole batch aborts; partial-batch outcomes not honoured |
| Same `packet_hash` discipline | Each row in the microbatch carries its own packet_hash for retry / invalidation per §6B.4 + §6B.5 |
| Same admission_rationale discipline | Each row in the microbatch carries its own admission_rationale array per §1.2 |

The microbatch panel design is a cost-optimisation candidate for Pass 3 BC-waves on existing entities (BC-AR / BC-AP / BC-GL / BC-Bank), where sibling shapes are stable and rows are homogeneous. It is **NOT recommended** for:

- Pass 1 characteristic-admission waves (per-characteristic F4-v2 v1 verdicts are needed; batching is structurally inappropriate)
- Pass 2 entity-admission waves (per-entity simple-vs-composite + family + identity decisions are per-row)
- Pass 3 BC-waves on freshly-admitted entities (Pass 2 cache discipline still settling)
- Any RED row (always per-row)

## 6C. Program Execution Architecture — Coordinator / Workers / Single Writer

This section closes the gap between the §1A layer-first model (which says "what work runs in what order") and the §8 row execution policy (which says "what each row may do"), by stating **how the work runs** at the program level. The shape is **Coordinator / parallel read + packet workers / bounded panel workers / single writer** — designed to make the autonomous program executable at scale without becoming unsafe.

### 6C.1 Roles

| Role | Cardinality | What it does | What it does NOT do |
|---|---|---|---|
| **Coordinator** | Exactly one per program run | Owns the program ledger; assigns work to workers; enforces A0 / A1–A5 authority; applies §8.4 fatal stop rules; aggregates per-(C/E/BC)-wave + per-pass + per-program reports; persists every row outcome; updates §6.7 program-completion state | Does NOT invoke panels directly; does NOT mutate substrate directly; does NOT bypass the writer |
| **Read workers** | 4–8 (parallel) | A0 OAGIS profiling; substrate inventory reads; candidate classification; evidence packet generation; collision prechecks; cache lookup; sibling-shape lookup | Do NOT call LLM / panel; do NOT mutate substrate; do NOT write certifications; do NOT advance row state past `panel_pending` |
| **Panel workers** | Bounded concurrency (starts at 2; rises to 3 after 20 consecutive clean panel outcomes) | F3 / F4-v2 / createEntity / createCharacteristic / createBusinessConcept panel invocations against bc-ai; record Maker / Checker / Moderator verdicts | Do NOT mutate substrate directly (Maker/Checker/Moderator verdict alone is not a write); do NOT confirm certifications (cert confirmation is the writer's act); do NOT mark row terminal until writer confirms |
| **Writer** | Exactly one — serialised single writer lane | Owns all substrate mutations: characteristic admission / amendment, entity admission, BC authoring, certification confirmation, retry-ledger state transitions that record write outcomes; re-checks collision / state immediately before each write; refuses duplicate writes when an equivalent active row already exists | Does NOT invoke panels; does NOT batch writes; does NOT bypass governance (DEC-26b6e2 / DEC-fb0b12 / F3 / C5 paths) |

### 6C.2 Parallelism policy

| Operation | Parallelism | Reason |
|---|---|---|
| **A0 Compile / Preflight** | Fully parallel | No LLM, no panels, no writes; CPU + read I/O bound only |
| **Substrate inventory reads** | Parallel (4–8 read workers) | Read-only; safe to fan out |
| **Candidate classification** | Parallel (4–8 read workers) | Deterministic mechanical work; no shared state mutation |
| **Evidence packet preparation** | Parallel + cacheable (4 packet workers) | Per-row packet builds; reuse via per-row packet hash cache; safe to fan out |
| **Collision prechecks** | Parallel (4–8 read workers) | Read-only check against substrate snapshot cache |
| **Panel calls (LLM)** | **Bounded concurrency — start low (2; ramp to 3)** | LLM provider rate limits + initial caution against systemic parser/schema/cache-drift failures; ramp only after demonstrated clean outcomes |
| **Governed substrate writes** | **Serialised through single writer (cardinality = 1)** | F3 single-writer service; per-row certification chain; idempotency rechecks; DEC-26b6e2 / DEC-fb0b12 enforcement |
| **Writer pre-write recheck** | Synchronous within writer | Immediately before each write, the writer re-queries the substrate snapshot (not the cached snapshot from earlier read workers) and confirms the candidate's idempotency assumption (no duplicate active BC / entity / characteristic) still holds; if violated → idempotent skip OR fatal stop depending on shape mismatch |
| **Nonfatal candidate parks / rejects** | Recorded; do NOT halt the program | Per §8.3 — agent continues with next row |
| **Fatal / systemic stops** | Halt the whole program | Per §8.4 — coordinator writes closeout + updates §6.7 + closes session |

The pre-write recheck is the writer's **most important safety act**. Read workers may have classified the row as `panel_pending` against a substrate snapshot from minutes earlier; in that window another row may have authored a colliding BC / entity / characteristic. The writer re-checks against current substrate state before the F3 call; if a duplicate exists, the row transitions to `authored_idempotent` and the writer continues.

### 6C.3 Initial safe concurrency defaults

These defaults are baseline; operator may override at A5 (budget / time caps) or A2 (row classification rules) approval time. The coordinator records actual concurrency configuration on every wave closeout.

| Role / pool | Default concurrency | Ramp rule | Override surface |
|---|---|---|---|
| A0 read / classification workers | **4–8** (start 4; CPU-aware scaling up to 8 if local compute permits) | None — A0 is CPU/IO-bound and free | A5 caps; coordinator config |
| Evidence packet workers | **4** | None — packet builds are deterministic | A5 caps; coordinator config |
| Panel workers | **2 concurrent at program start** → **3 only after 20 consecutive clean panel outcomes** (no parser / schema / systemic failures) | Ramp gate: 20 clean panels in a row before increase; reset to 2 on any systemic failure | A5 caps; coordinator config |
| Writer concurrency | **1** (serialised single lane) | Never increases beyond 1 under this blueprint | Not overridable without separate ADR (changes F3 single-writer contract) |
| Confirmation / write queue | **FIFO within dependency group** | May reorder across disjoint dependency groups only when coordinator records `write_queue_reorder_reason` text | Coordinator config; A5 caps |

The **20-consecutive-clean-panels** ramp gate is the key safety mechanism. It bounds early-program risk: if the panel pool is misconfigured (parser failure, schema drift, cache-prefix bug), the failure shows up in the first 20 panels and the pool stays at 2 — not 3 — until the issue is resolved.

### 6C.4 Cost-control policy

| Rule | Operative |
|---|---|
| **No LLM / panel dry-run** | LLM calls are the only mode for panel evaluation; "trial panel" / "shadow panel" / "preview panel" is prohibited (§6A.5 reinforces this for A0 specifically) |
| **A0 is deterministic and free** beyond local compute | A0 reads OAGIS extract + substrate snapshot; does CPU work; emits ledger seed + report; no LLM invocation; no provider charge |
| **Panel calls require `packet_hash`** | A panel worker may not invoke a panel for a row that lacks a `packet_hash` populated by A0; the writer may not confirm a write without the row's `packet_hash` |
| **No re-run on unchanged hash** | If a row's `packet_hash` is unchanged AND `panel_attempt_count > 0` AND a terminal outcome (`panel_parked` / `panel_rejected` / `authored_active` / `authored_idempotent`) exists, do NOT re-run the panel. Re-run permitted only when `substrate_snapshot_hash`, `evidence_hash`, or operator pin changed |
| **OAGIS candidate evidence cache** | Cached by `(noun, component, field_path)` signature; reused across all ledger rows that cite the same OAGIS field |
| **Sibling-shape cache** | Cached by `(characteristic_id_or_proposed_term, entity_cluster)` signature; reused across all BC rows binding the same characteristic to entities in the same cluster |
| **Packet-build result cache** | Cached by `packet_hash`; reused across panel retries and idempotency checks |
| **Cost recording** | Per panel row: `model_cost_estimate` populated before panel call (from per-provider price table × estimated token usage); `model_cost_actual` populated after panel response (from provider usage headers); both persisted to ledger |
| **Total program spend cap** | Coordinator tracks cumulative `model_cost_actual` across all rows; if cumulative cost reaches A5 total program spend cap → fatal stop trigger fires (§8.4) |
| **Total panel-call cap** | Coordinator tracks cumulative panel-invocation count across all rows (sum of `panel_attempt_count` across the ledger); if count reaches A5 total panel-call cap → fatal stop trigger fires (§8.4) |
| **Optional pass-level cap** | Coordinator tracks per-pass cumulative `model_cost_actual` AND per-pass cumulative panel-invocation count; if either reaches an A5-configured pass-level cap → fatal stop trigger fires (§8.4). Pass-level caps are optional; absent caps are not enforced. |
| **Per-row latency cap** | Coordinator tracks per-row wall-time from `work_claimed_at` to `final_prewrite_check_at` (writer confirmation) for each row; if a single row's elapsed wall-time reaches A5 per-row latency cap → fatal stop trigger fires (§8.4) |
| **Wall-time cap** | Coordinator tracks total wall-time since program start; if wall-time reaches A5 wall-time cap → fatal stop trigger fires (§8.4) |
| **Backlog-exhaustion completion** | Program may run autonomously until executable backlog is exhausted (§8.6 completion criteria); cumulative spend / time within caps remain bounded by §8.4 fatal stops |

### 6C.5 Ledger fields — extensions to §6.3

The §6.3 schema is extended with the following fields for safe parallel execution. (`packet_hash` and `retry_reason` were already added in the SES-02e53a comprehensive reconciliation pass.)

| Field | Type | Set by | Purpose |
|---|---|---|---|
| `coordinator_run_id` | text (CRR-<6hex>) | Coordinator on row assignment | Identifies which coordinator run claimed this row; survives across sessions |
| `worker_id` | text (WKR-<6hex>) | Worker on row claim | Identifies the specific worker (read / packet / panel) that owns the row's current step |
| `work_claimed_at` | timestamp | Worker on row claim | When the worker took the row |
| `claim_expires_at` | timestamp | Worker on row claim | When the claim expires (worker dies / coordinator may reclaim) |
| `substrate_snapshot_hash` | text (sha256) | Read worker on substrate read | SHA-256 over the substrate snapshot's `(entity_ids, characteristic_ids, business_concept_ids)` materialised view used at classification time; invalidates packet_hash if substrate changes |
| `evidence_hash` | text (sha256) | Packet worker on packet build | SHA-256 over `oagis_provenance.cited_text + admission_rationale_evidence` digest; used to detect evidence refinement that warrants retry |
| `panel_attempt_count` | integer | Coordinator on panel handoff | Increments each time a panel worker invokes the panel for this row |
| `writer_attempt_count` | integer | Writer on write handoff | Increments each time the writer attempts the substrate write for this row |
| `model_cost_estimate` | decimal (USD) | Packet worker | Estimated provider cost from per-provider price table × estimated token usage |
| `model_cost_actual` | decimal (USD) | Panel worker | Actual provider cost from provider response usage headers |
| `dependency_group` | text | A0 on classification | Logical grouping of rows that must execute in FIFO order (e.g., `bc-ar-customer-invoice-header` — all CI header BCs flow through one writer queue position group); coordinator respects within-group order, may reorder across disjoint groups |
| `write_queue_position` | integer | Writer on queue admission | Position in the writer's serialised queue at the moment of admission |
| `final_prewrite_check_at` | timestamp | Writer on prewrite recheck | When the writer last performed the §6C.2 pre-write recheck for this row |
| `final_prewrite_check_result` | enum | Writer on prewrite recheck | `ok` (proceed with write) / `idempotent_skip` (active row already exists; transition to `authored_idempotent`) / `shape_mismatch_fatal` (substrate shape disagrees with row — fatal stop) / `collision_fatal` (different row holds the same `(entity, characteristic)` tuple — fatal stop) |
| `terminal_outcome_code` | enum | Coordinator on terminal transition | Final outcome enum: `authored_active` / `authored_idempotent` / `panel_parked` / `panel_rejected` / `blocked_transient` / `red_held` / `deferred_diagnostic` / `deferred_pull_gated` / `deferred_runtime` / `deferred_metadata` / `superseded` / `withdrawn` / `unknown_halt` |

### 6C.6 Locking + duplicate in-flight protection

| Rule | Operative |
|---|---|
| **Single-claim per row** | A ledger row may be claimed (`work_claimed_at` set; `worker_id` populated; `claim_expires_at` set to claim_window from now) by only one worker at a time. A second worker attempting to claim a claimed row reads `claim_expires_at` and waits OR (if expired) reclaims via coordinator |
| **Expired-claim reclamation** | If `claim_expires_at` is in the past AND the row's status is not terminal, the coordinator may reclaim the row, log `claim_expired_at_reclaim` + the original `worker_id`, and reassign to a fresh worker |
| **Writer refuses duplicate writes** | Before every substrate mutation the writer re-queries the substrate via §6C.2 prewrite recheck. If an equivalent active BC / entity / characteristic exists, the writer transitions the row to `authored_idempotent` (no second write, no second cert) and continues |
| **Terminal-outcome immutability** | A row with `terminal_outcome_code` set is immutable. The coordinator does not re-assign; panel workers do not retry; writer does not re-write. Reset requires either: (a) explicit operator action (`status: program_authorized` re-assertion with `retry_reason` documenting the override) OR (b) a changed `packet_hash` / `substrate_snapshot_hash` / `evidence_hash` (which logically creates a new row's worth of intent — the prior terminal outcome remains preserved as historical) |
| **Coordinator claim-arbitration** | If two workers race for the same row, the coordinator's claim-recording is the tiebreaker. The first claim recorded wins; the loser receives an `ECLAIM` signal and picks the next executable row |

### 6C.7 Single writer is not slow mode

A common misread: "single writer = single-threaded program = slow". This is **wrong**.

| What "single writer" means | What it does NOT mean |
|---|---|
| All irreversible governed writes pass through one serialised lane | The entire program runs single-threaded |
| Substrate mutations (entity / characteristic / BC / certification) are serialised | Read workers, A0, evidence packet workers, and panel workers run in parallel |
| F3 / C5 governance paths preserved | Reads or packet building wait on the writer |
| DEC-26b6e2 / DEC-fb0b12 + per-row certification chain enforced | Panel concurrency is artificially capped at 1 |
| Idempotency rechecks happen serially before each write | The total wall-time grows linearly with row count |

This is the **safety / performance compromise**:
- **Safety**: governed writes are serialised — no concurrent F3 calls, no concurrent certifications, no race conditions on `(entity, characteristic)` uniqueness, no DEC-26b6e2 violations.
- **Performance**: every step before the write — A0, evidence packet build, panel call — runs in parallel up to its respective concurrency cap, so the program's wall-time is dominated by the slowest serialised lane: writer's serialised throughput.

At the §6C.3 defaults (panel pool 2 → 3; writer 1; ~55–65s per panel; ~5–15s per write), a program executing 773 BC + 90–130 char + 47 simple entity admissions sees its panel throughput cap at ~2–3 concurrent panels and its write throughput cap at ~12–15s per row serialised. A writer-bottleneck program completes at the writer's pace; a panel-bottleneck program completes at the panel pool's pace. The 20-clean-panel ramp gate ensures the panel pool grows only when safe.

### 6C.8 §8.5 pseudocode reference

The §8.5 program checkpoint pseudocode has been updated to reflect the §6C model:

```
A0 parallel compile (read workers fan out)
  → ledger seed (rows with packet_hash + substrate_snapshot_hash + evidence_hash)
  → operator A1–A5 program approval (gate)
  → for each pass in [Pass 1, Pass 2, Pass 3]:
      for each wave in pass (DAG-driven):
        coordinator dispatches:
          - read workers prepare evidence packets (parallel)
          - packet workers build packets + estimate cost (parallel)
          - panel workers invoke panels (bounded concurrency: 2 → 3 after 20 clean)
            - returns Maker/Checker/Moderator verdict + actual cost
          - writer claims serialised lane:
            - prewrite recheck (substrate snapshot at this exact moment)
            - if idempotent: transition row to authored_idempotent + continue
            - if shape mismatch: fatal stop
            - if ok: F3 / F4-v2 / createEntity / createCharacteristic / createBusinessConcept governed write
            - record outcome + cert + transition row to authored_active
          - coordinator persists outcome to ledger + updates §6.7
        nonfatal row outcomes (parked / rejected / blocked_transient) recorded; agent continues
        fatal §8.4 stops halt the whole program
      after wave: coordinator writes wave closeout packet + updates §6.7
    after pass: coordinator updates §6.7 pass-completion state
  on backlog exhaustion (§8.6 C1–C5 + P1'/P2'/P3'): coordinator writes program-completion packet
```

Full §8.5 detailed pseudocode (with all branches expanded) remains in §8.5; this is the §6C summary view.

## 7. Recommended first waves under layer-first model

Under the §1A three-pass model, the first wave from each pass demonstrates layer-first execution and validates the cache-precedence discipline (§1A.2). The three "first waves" together cover one full vertical slice — admit characteristics, admit entity, then bind BCs against those caches.

### 7.1 First Pass-1 wave — C1 (code characteristics)

**Admission rationale.** Primary: AR-4 standards_backed_foundation — OAGIS T2 names these ~20–25 codes (payment_method, incoterms, transport_mode, UoM, valuation_class, quality_status, inspection_result, operation, material_type) as load-bearing across multiple cross-enterprise domains. Secondary: AR-3 entity_backbone_completeness — these codes underpin ~250+ downstream BCs across BC-Logistics / BC-Procurement / BC-Quality / BC-Production / BC-AR / BC-AP. Tertiary: AR-1 known_metric_pull for the OTIF / reconciliation / procurement-cycle metric chains that explicitly cite a subset. Admitting them in one cache-cohesive session amortises the per-characteristic F4-v2 v1 admission overhead.

**Scope.** F4-v2 v1 panel admission for each code characteristic in the C1 cluster. Operator-pinned (term, definition, classification=Global) per row; agent reads pin from ledger, invokes the panel, records `authored_active` / `authored_idempotent` / `panel_parked` / `panel_rejected` outcomes per §8.3.

**Approximate authoring delta.** 0 entities + ~20–25 new characteristics + 0 BCs (BCs come in Pass 3).

**Class.** AMBER (all rows; each carries `pin_evidence_text` for F4-v2 v1 verdict + closed-set representation_term=`code` confirmation).

**Halt rules.**
- Halt on any candidate whose definition narrows to a single source system (Vocab §11.1 system-agnosticism failure → fatal stop).
- Halt on closed-set representation_term mismatch (M3 / M7 of admission checklist).
- Halt on source-field-copy detection (M9).
- Per-row park on missing T1–T4 evidence; agent records `panel_parked` and continues.

**Pre-execution prereq.**
- Operator pins term + definition + classification per row in the ledger (`pin_evidence_text`).
- The C1 cluster's representation_term=`code` decision is uniform across the wave — single Maker / Checker / Moderator prompt prefix.

**Estimated session cost.** 20–25 panel runs × ~55–75s each = ~20–30 minutes. One session.

### 7.2 First Pass-2 wave — E1 (Item master admission)

**Admission rationale.** Primary: AR-3 entity_backbone_completeness — Inventory + Production + Procurement + Logistics all gate on Item identity; without Item admitted, none of E4–E12 can advance. Secondary: AR-4 standards_backed_foundation — OAGIS T2 names Item / Material / Product as the master-data root of finance + supply-chain integration. Tertiary: AR-5 operator_strategic_priority where the operator names "manufacturing vertical readiness" as a strategic capacity.

**Scope.** Single-entity admission via `createEntity` panel. Operator-pinned (name=`Item`, family=master data, simple-vs-composite=simple, classification=Global). Agent reads pin, invokes the panel, records outcome.

**Approximate authoring delta.** 1 entity + 0 characteristics + 0 BCs.

**Class.** AMBER (one row; carries `pin_evidence_text` for simple-vs-composite + family classification).

**Halt rules.**
- Halt on operator deciding Item is composite after preflight pin (re-classes to RED — separate decision packet).
- Halt on Item family-classification ambiguity (Material vs Stock vs Product) — operator decides via packet, not autonomously.

**Pre-execution prereq.**
- Operator pins simple-vs-composite + family in the ledger.
- C1 (or full Pass 1) need not complete first — E1 is independent of Pass 1.

**Estimated session cost.** 1 panel run × ~60s = ~1 minute panel wall-time. One session (fast).

### 7.3 First Pass-3 wave — BC-AR (binding to existing AR entities)

**Admission rationale.** Primary: AR-1 known_metric_pull — AR-side metric chains (DSO, ARPI, dispute rate, billing accuracy) consume BCs on Customer Invoice, CILI, Customer Payment, Sales Order. Secondary: AR-3 entity_backbone_completeness — symmetric AR / AP backbone parity that legacy work (Wave A/B 2026-06-23) explicitly named. Tertiary: AR-4 standards_backed_foundation for OAGIS-derived terms (payment_method_code, transaction_date_time, tax_base_amount). The W-extend AR portion (~50–70 BCs) + W1 / W2 AR-side BCs (~25–35) = ~75–95 BC bindings on existing AR entities. All characteristics + entities are pre-resolved (Pass 1 cache + existing substrate).

**Scope.** F3 `createBusinessConcept` panel calls per BC row. Each Maker packet cites: cached Pass 1 characteristic decision (term + shape) + existing entity (Pass 2 not needed — these are existing entities) + OAGIS provenance + sibling representation_term shape pin from prior BCs on the same entity in this wave session.

**Approximate authoring delta.** 0 entities + 0 characteristics + ~75–95 BCs.

**Class.** AMBER (all rows; each carries `pin_evidence_text` for the characteristic + sibling shape).

**Halt rules.**
- Halt on any sibling representation_term ambiguity surfacing during binding (refer to Pass 1 follow-up packet; do NOT autonomously re-cycle to Pass 1).
- Halt on `posted amount` per-line vs header question (operator decision held; see scope audit §3.3).
- Halt on `ordered quantity` CILI/GR Line wording question (OQ-2; defers to Pass 1 follow-up if surfaces).

**Pre-execution prereq.**
- C1 (and ideally C2 + C3) must be `Pass 1 complete` for the characteristics this wave will bind.
- E1 + E2 must be `Pass 2 complete` if the wave touches any new-entity bindings. (BC-AR only touches existing entities, so Pass 2 is not a prerequisite.)
- BC-AR rows that bind newly-admitted characteristics (historically grouped as W-extend AR fill-in) must have `pin_evidence_text` populated from Pass 1's admitted characteristics.

**Estimated session cost.** ~75–95 panel runs × ~55–65s = ~75–100 minutes panel wall-time. Likely two sessions (split AR-existing-entities into per-entity sub-batches: BC-AR-Invoice + BC-AR-Payment + BC-AR-Customer + BC-AR-Order).

### 7.4 What the first three layer-first waves test together

| Test | Wave covering it |
|---|---|
| F4-v2 v1 panel admission under program approval + operator pin | C1 |
| Closed-set representation_term enforcement (`code` cluster) | C1 |
| System-agnosticism + source-field-copy halt triggers | C1 |
| Single-entity admission via `createEntity` under operator pin | E1 |
| Simple-vs-composite operator-pin requirement | E1 |
| Pass 1 cache → Pass 3 BC packet citation discipline | BC-AR (every row cites C1/C2/C3 cached decisions) |
| Pass 3 halt-on-scope-question (no autonomous re-cycle to Pass 1) | BC-AR |
| Sibling-shape pinning from prior-in-wave BCs (cache reuse) | BC-AR |
| End-to-end vertical slice: char → entity → BC | C1 + E1 + BC-AR together |
| Evidence-Governed admission preserved at each layer — admission_rationale codes AR-1..AR-5 + safeguards S1 (used_by_bc_target_count ≥ 1) and S2 (entity_slice_name non-null) (§1) | All three |

If C1 + E1 + BC-AR close cleanly, the layer-first model is validated end-to-end. Pass 1 + Pass 2 + Pass 3 can then continue with subsequent C-waves (C2–C6), E-waves (E2–E13), and BC-waves (BC-AP, BC-GL, ..., BC-Reference) autonomously under the same A1–A5 program approval.

### 7.5 Sequencing options for the first three

**Sequential (recommended for first run).** C1 → E1 → BC-AR in three distinct sessions. Each session validates one layer; operator reviews ledger between sessions. Best for first program execution; safest cache discipline validation.

**Parallel (after first program execution).** C1 + E1 + (read-only BC-AR plan) in one session: characteristic admission and entity admission can run in parallel since they don't share decision context. BC-AR follows once both complete. Faster, but requires program-level concurrency discipline (ledger last-writer-wins).

The operator's A1–A5 program approval implicitly enables whichever sequencing the agent chooses; the agent records the chosen sequencing in the ledger.

## 8. Program-level autonomous execution policy

This section supersedes the per-wave authorisation model from the blueprint's first draft. The intended model is **program-level authorisation**: operator approves the program once (the target-state catalogue, the GREEN/AMBER/RED/DEFER/UNKNOWN classification rules, the halt rules, the retry ledger, the budget caps); the agent then executes wave after wave autonomously until the executable backlog is exhausted or a fatal stop fires.

Wave boundaries become **execution and checkpoint units**, not authorisation units.

### 8.1 Program authorisation model

The operator authorises the whole BCF × OAGIS program by approving, in a single explicit act:

| Approval item | What is being approved | Reference |
|---|---|---|
| **A1 Target-state catalogue + admission rule** | §1 Evidence-Governed Foundation Buildout (5 admission rationales AR-1..AR-5 + 2 new safeguards) + §4A target-state catalogue (54 new entities, ~90–130 admitted characteristics, 773 BC targets) + §4A.10 admission-rationale distribution + §4B layer-first re-aggregation | §1, §4A, §4A.10, §4B |
| **A2 Row classification + admission rules** | GREEN / AMBER / RED / DEFER / UNKNOWN per-row classification rules (§5.1, §8.2) + admission rationale validation (§1.2 — each row has ≥1 rationale fully evidenced) + safeguards 1 + 2 (§1.4) | §5.1, §8.2, §1.2, §1.4 |
| **A3 Halt rules** | The fatal / systemic stops list (§8.4) + per-(C/E/BC)-wave halt rules (§5.3) + compile-layer halt pre-conditions (§6A.1 step 17) | §5.3, §8.4, §6A |
| **A4 Retry ledger + compile layer + cache economy** | The §6 ledger (Phase-1 Markdown; Phase-2 DBCP candidate deferred) + §6.7 program-completion state + §6A Compile / Preflight Layer (the only approved dry-run style) + §6B Batch + Cache Execution Economy | §6, §6A, §6B |
| **A5 Budget / time caps** | The operator-stated caps: (a) **total program spend cap** (cumulative `model_cost_actual` ceiling for the whole program — USD); (b) **total panel-call cap** (maximum number of panel invocations across the whole program); (c) **optional pass-level cap** (per-pass spend or panel-call sub-cap, e.g. "Pass 1 ≤ $X / N panels"); (d) **per-row latency cap** (maximum wall-time a single row may consume from claim to writer-confirmation); (e) **wall-time cap** (total wall-time from program start). All caps live on the ledger; the coordinator enforces them; breach fires §8.4 fatal stop. | §8.4 trigger rows |

A single operator decision flipping A1–A5 from `proposed` to `program_authorized` enables autonomous execution. The agent then proceeds row by row, wave by wave, without re-asking — except for the row execution rules in §8.2 (RED rows are never executed; UNKNOWN rows fatal-stop) and the §8.4 fatal triggers.

The operator may withdraw program authorisation at any time. The agent then completes any in-flight wave's closeout (preserving completed work and ledger state), updates §6.7 program-completion state, and stops.

### 8.2 Row execution rules

The agent evaluates every ledger row against its class before any panel call.

| Row class | Execution rule |
|---|---|
| **GREEN** | Execute autonomously. No further operator approval required. The agent picks the next GREEN row from the active wave or the next wave in sequence and runs the F3 BC-authoring panel. |
| **AMBER** | Execute autonomously **only when** the blueprint or retry ledger carries an explicit pinned decision for the ambiguity. Pinned decisions are recorded in the ledger row as `pin_evidence_text` (e.g., representation_term shape pin: `identifier/string/identity`; DEC-fb0b12 verdict: `E1–E6 all pass`; F4-v2 classification: `global, approved per checklist v1`). Without a pinned decision, the row reclassifies to UNKNOWN and a fatal stop fires (§8.4). |
| **RED** | **Never execute.** RED rows remain held. Each RED row represents a separate operator decision (entity-admission packet, composite-identity declaration, supersession decision, ADR). The program-level authorisation does NOT include RED rows — they are explicitly out of scope for autonomous execution. |
| **DEFER** | **Never execute** under the current pull. DEFER rows are intentionally deferred capacity. Activation requires a new pull signal (concrete metric / source-chain / workflow / entity-backbone need) that operator records as a new row reclassification. |
| **UNKNOWN** | **Fatal stop.** Any row whose classification is not unambiguously GREEN / AMBER / RED / DEFER halts the program. Operator triage required before any row can be reclassified. This covers unmapped nouns (Bucket 8 SEMANTIC_AMBIGUITY_HALT), rows the profiler could not score, and AMBER rows that lack a pinned decision. |

### 8.3 Nonfatal row outcomes — record and continue

When a row executes, the panel result drives one of four nonfatal outcomes. The agent records the outcome on the ledger row, advances to the next executable row, and does NOT halt the program.

| Outcome | Substrate state | Ledger transition | Next agent action |
|---|---|---|---|
| **authored / active** | The row's BC / characteristic / entity is `lifecycle_state='active'` after the panel run. `bcf.certification_record` carries the create + activation certs. | `panel_pending` → `authored_active`; record `linked_subject_uid`, `last_create_cert_uid`, `last_activation_cert_uid` | Pick next executable row |
| **already exists / duplicate (idempotent success)** | The row's `(entity_id, characteristic_id)` already has an active BC row — the substrate already represents what the row proposed. No new panel call needed; the row is satisfied by prior state. | `panel_pending` → `authored_idempotent`; record `linked_subject_uid` of the prior BC | Pick next executable row |
| **candidate-specific park** | Panel Moderator returned `OPERATOR_REVIEW`. The panel run is preserved in `bcf.panel_output_record`. The park is a per-row failure, not a program-level failure. | `panel_running` → `panel_parked`; record `halt_reason` + `last_panel_run_uid` + `next_action_text` | Pick next executable row. The parked panel becomes an operator triage item, not a program-level halt. |
| **candidate-specific reject** | Panel Moderator returned `REJECT`. The reject is a per-row terminal failure. | `panel_running` → `panel_rejected`; record `halt_reason` + `last_panel_run_uid` | Pick next executable row. The reject is terminal for this row; the operator may file a follow-up row with refined evidence if they choose. |
| **transient failure** | bc-ai or bc-core returned a transient error (5xx, timeout, parser stutter, API rate-limit) that does not signal systemic failure. | `panel_running` → `transient_retry`; increment `retry_count` | Retry the same row up to `MAX_TRANSIENT_RETRIES=3`. After exhaustion, transition to `blocked_transient` and continue with the next executable row. The blocked row becomes operator triage. |

The agent's loop is therefore **continue-to-exhaustion** at the program level: parks, rejects, transients, and idempotent successes are all non-fatal. The wave's totals reflect (authored_active + authored_idempotent + panel_parked + panel_rejected + blocked_transient) per row; the program closes when no executable rows remain in any wave or a fatal stop fires.

### 8.4 Fatal / systemic stops

The triggers below halt the entire program — not just the row, not just the wave. The agent writes a final closeout packet for the in-flight wave (preserving completed work and ledger state), updates §6.7 program-completion state, and closes the session.

| Trigger | Source rule | Detection signal |
|---|---|---|
| **Service unavailable** | Backbone doctrine §3.4 | bc-core or bc-ai returns sustained 5xx, or consecutive auth failures (≥ 3) suggesting expired Cognito token / config drift, or unreachable upstream |
| **Auth / config failure** | Backbone doctrine §3.4 | JWT minting fails; `mcf_publisher` role check fails; environment misconfig (DATABASE_URL / AWS_PROFILE / Cognito IDs missing) |
| **Schema / prompt / parser failure** | Backbone doctrine §3.4 | Maker / Checker / Moderator output schema fails validation; required envelope fields missing; structural parser breaks across multiple rows (≥ 2 in same wave) |
| **Repeated same park/reject reason** | New program-level rule | Same park / reject `halt_reason` fires across ≥ 3 consecutive rows in any wave — indicates systemic rather than per-row issue |
| **Evidence packet malformed** | Vocabulary Evidence Framework §3 | Candidate evidence missing `sourceLabel` or `citedText`; T1–T4 source cited but content does not validate; OAGIS provenance citation does not match extract |
| **Unexpected mutation shape** | Backbone doctrine §3.4 | Substrate write touches a column or table not on the F3 single-writer expected list; `bcf.certification_record` row lacks `subject_kind` or `action_code` |
| **Write path outside F3 / C5 governed path** | Backbone doctrine §3.4 + ADR D432 (legacy MC authoring guard pattern) | Direct SQL `INSERT` / `UPDATE` detected; non-F3 endpoint hit; legacy-pattern write attempted |
| **New characteristic / entity attempted in a reuse-only row** | Row execution rule | A row classed GREEN attempts to mint a new characteristic / entity — class mismatch |
| **Representation_term ambiguity not pinned** | Wave B §5.3 | Substrate has ≥ 2 representation_term shapes for the proposed term and the row lacks `pin_evidence_text` |
| **Budget / time cap reached** | A5 program approval | Any of: cumulative `model_cost_actual` ≥ total program spend cap; cumulative panel-invocation count ≥ total panel-call cap; cumulative `model_cost_actual` or panel-invocation count for a pass ≥ optional pass-level cap; per-row wall-time (claim → writer-confirmation) ≥ per-row latency cap; total wall-time since program start ≥ wall-time cap |
| **Foundation invariant violation** | `the-invariants.md` | Any of Invariants I–VI detected as violated by a proposed candidate or amendment |
| **DEC-fb0b12 E1–E6 ambiguity without pin** | DEC-fb0b12 | Editorial amendment attempted on a row where one of E1–E6 is ambiguous and the ledger row does not carry the operator pin |
| **System-agnosticism failure** | Vocabulary Evidence Framework §11.1 | Candidate is justified only by source-system carrier (SAP / Oracle / NetSuite); fails Global classification |
| **Resolver-stamped attempt** | Vocabulary Evidence Framework §11.6 | Candidate names a concept the canonical resolver computes |
| **Forbidden term** | Vocabulary Evidence Framework §11.6 | Candidate is `fiscal period` or other §11.6-reserved name |
| **Source-field copy** | Vocabulary Admission Checklist M9 | Candidate term is a vendor identifier verbatim |
| **Cross-registry mutation** | Backbone doctrine §3.4 | BCF run attempts to write `mcf.*` or `contract.*` |
| **Telemetry missing** | Backbone doctrine §3.4 | HTTP 200 but no `bcf.panel_output_record` or no `bcf.certification_record` row stamped |
| **Direct-write detected** | Backbone doctrine §3.4 | SQL `INSERT` / `UPDATE` outside the F3 single-writer service |
| **Prompt / cache-prefix drift** | Backbone doctrine §3.4 | Maker / Checker prompt prefix changes mid-batch; cache-key invalidation across a wave |
| **Composite-identity acyclicity failure** | BCR §4 | Proposed composite entity's identity-bearing reference graph forms a cycle |
| **UNKNOWN row encountered** | §8.2 row execution rule | Any row not classed GREEN / AMBER / RED / DEFER — including a Bucket 8 SEMANTIC_AMBIGUITY_HALT row that reaches the executor |

### 8.5 Program checkpoint rules

The agent's loop structure follows the §1A layer-first DAG (A0 Program Compile / Preflight → Pass 1 C-waves → Pass 2 E-waves → Pass 3 BC-waves grouped by entity/domain) and the §6C execution architecture (Coordinator + parallel read/packet workers + bounded panel workers + single writer queue). No mixed-wave loop. No wave-level authorisation between waves.

```
# A0 — Program Compile / Preflight (read-only, no LLM, no panels, no writes)
# May run before A1–A5 to produce the exact target ledger/counts for approval.
# A1–A5 is REQUIRED before any panel call, entity admission, characteristic
# admission, BC authoring, confirmation, or substrate write.

run A0 parallel compile:                            # §6A; read workers fan out (4–8 per §6C.3)
  load OAGIS extract                                # read-only
  load substrate snapshot (concept_registry.* / bcf.*)  # read-only via bc-postgres
  dedupe + map + bucket-classify + admission_rationale + class  (parallel)
  compute used_by_bc_target_count + target_entities + target_waves
  compute entity_slice_name + composite_identity_decision
  compute packet_hash + substrate_snapshot_hash + evidence_hash per row
  emit retry ledger seed + compile report + operator decision queue
  -- no panels, no LLMs, no substrate mutation --

# A1–A5 program approval gate
require operator A1–A5 approval before proceeding to Pass 1
record program_authorization_at on every row that flips proposed → program_authorized

# Coordinator dispatches per-pass per-(C/E/BC)-wave work via §6C role model:
#   - read workers (4–8 parallel) prepare evidence packets + collision prechecks
#   - packet workers (4 parallel) build packets + estimate model_cost_estimate
#   - panel workers (bounded: 2 concurrent → 3 after 20 consecutive clean outcomes)
#       invoke F4-v2 v1 / createEntity / F3 panels; record model_cost_actual
#   - writer (cardinality = 1, serialised) performs §6C.2 pre-write recheck;
#       on prewrite OK → governed F3 / F4-v2 / createEntity write + cert
#       on prewrite idempotent_skip → transition to authored_idempotent
#       on prewrite shape_mismatch_fatal / collision_fatal → §8.4 fatal stop
#   - coordinator persists every row outcome + updates §6.7

# Pass 1 — Characteristic Vocabulary
for each C-wave in [C1, C2, C3, C4, C5, C6]:               # §5.2; C-DEFER + C-RED held, not executed
  coordinator dispatches C-wave rows where class ∈ {GREEN, AMBER-with-pin}:
    if class == UNKNOWN: fatal_stop("UNKNOWN row")           # §8.4
    if class ∈ {RED, DEFER}: skip (held); continue
    read workers prepare packets in parallel  (§6C.3 4–8 parallel)
    packet workers build packets + estimate cost in parallel  (§6C.3 4 parallel)
    panel workers invoke F4-v2 v1 createCharacteristic panel  (§6C.3 bounded 2→3)
      → Maker/Checker/Moderator verdict + model_cost_actual recorded
    writer claims serialised lane (§6C.6 single-claim per row):
      prewrite_recheck → if ok: governed createCharacteristic + cert
                       → if idempotent_skip: transition to authored_idempotent
                       → if shape_mismatch_fatal / collision_fatal: §8.4 fatal stop
    coordinator records outcome: authored_active | authored_idempotent
                               | panel_parked | panel_rejected | transient_retry → blocked_transient
    if §8.4 fatal_stop fires: write closeout, update §6.7, close session
  write C-wave closeout packet
  update §6.7 pass_1_characteristic.c{i}_state
  continue automatically to next C-wave

# Pass 2 — Entity Backbone
for each E-wave in [E1, E2, …, E13]:                          # §5.3
  coordinator dispatches E-wave rows (same role model as Pass 1)
    panel workers invoke createEntity panel
    writer claims serialised lane: prewrite_recheck → governed createEntity + cert
  write E-wave closeout packet
  update §6.7 pass_2_entity.e{i}_state

# Pass 3 — Business Concept Binding
for each BC-wave grouped by entity / domain
       in [BC-AR, BC-AP, BC-GL, BC-Bank, BC-Master, BC-Procurement,
           BC-Inventory, BC-Production-simple, BC-Production-composite,
           BC-Logistics, BC-Quality-simple, BC-Quality-composite,
           BC-Workforce, BC-Asset, BC-Reference]:              # §5.4
  coordinator dispatches BC-wave rows (same role model)
    panel workers invoke F3 createBusinessConcept panel
    writer claims serialised lane: prewrite_recheck → governed createBusinessConcept + cert
  write BC-wave closeout packet
  update §6.7 pass_3_bc.bc_*_state

# Per-pass DAG
# Pass 2 may begin as soon as C3 (identifier characteristics needed for
# composite-identity components) is sufficiently complete to support its
# composite-RED entities. Pass 3's per-BC-wave can begin as soon as the
# characteristics it cites (Pass 1) AND the entities it cites (Pass 2 or
# existing substrate) are authored_active. The retry ledger's prereq_ledger_uids
# DAG drives executable-at-now determination.

# Cost / time caps (§6C.4 + A5)
on every panel response:
  cumulative_model_cost_actual += row.model_cost_actual
  cumulative_panel_invocations += 1
  pass_cumulative_cost[current_pass] += row.model_cost_actual
  pass_cumulative_invocations[current_pass] += 1
  if cumulative_model_cost_actual >= A5.total_program_spend_cap:
    §8.4 fatal_stop("total program spend cap reached")
  if cumulative_panel_invocations >= A5.total_panel_call_cap:
    §8.4 fatal_stop("total panel-call cap reached")
  if A5.pass_level_cap[current_pass] is set:
    if pass_cumulative_cost[current_pass] >= A5.pass_level_cap[current_pass].spend
       or pass_cumulative_invocations[current_pass] >= A5.pass_level_cap[current_pass].invocations:
      §8.4 fatal_stop("optional pass-level cap reached")
on every row state transition to final_prewrite_check_at:
  row_latency = row.final_prewrite_check_at - row.work_claimed_at
  if row_latency >= A5.per_row_latency_cap:
    §8.4 fatal_stop("per-row latency cap reached")
on every coordinator tick:
  wall_time_elapsed = now - program_start
  if wall_time_elapsed >= A5.wall_time_cap: §8.4 fatal_stop("wall-time cap reached")

# Cache + retry economy (§6C.4 + §6B.5)
on row terminal outcome:
  if outcome ∈ {panel_parked, panel_rejected}:
    do NOT re-run unless packet_hash | substrate_snapshot_hash | evidence_hash
       or operator pin changed
  record retry_reason on any retry-permitting transition

# Completion
when no executable rows remain in any pass AND all RED/DEFER rows are held with reason
       AND no unknown_halt rows remain (§8.6 C1–C5 + P1' + P2' + P3'):
  write program completion packet
  update §6.7 program_authorization = completed
  close session
```

After each wave, the agent:

1. Writes a wave closeout packet (`bcf-oagis-<wave-id>-closeout-<date>.md`) matching the Wave A/B doctrinal convention — per-row outcomes, substrate deltas, parked/rejected/blocked rows, telemetry, ledger updates.
2. Updates the Phase-1 Markdown retry ledger so every row's status reflects post-wave reality. Every row outcome is persisted (no in-memory-only state).
3. Updates the §6.7 per-pass program-completion state to reflect cumulative progress.
4. Continues automatically to the next executable wave (DAG-driven). No operator decision is required between waves under A1–A5 program authorisation.
5. Stops only if (a) no executable rows remain anywhere in the DAG (program completion), or (b) a §8.4 fatal stop fires.

### 8.6 Final program completion state

The agent records the program's final state when it exits — whether by exhaustion (happy path) or by fatal stop. The final state lives at the head of the Phase-1 Markdown ledger and is updated after each wave closeout.

Completion criteria for happy-path exhaustion:

| Criterion | Description |
|---|---|
| **C1** | All executable GREEN rows are `authored_active` OR `authored_idempotent`. |
| **C2** | All executable AMBER rows are `authored_active` OR `authored_idempotent` OR `panel_parked` (with operator-triageable park reason) OR `panel_rejected` (terminal per-row failure) OR `blocked_transient` (operator-triageable bounded-retry exhaustion). |
| **C3** | All RED rows remain `held` with `next_action_text` documenting the operator entity / doctrine decision required. |
| **C4** | All DEFER rows remain `deferred_*` with documented system-agnostic rationale or pull-condition for activation. |
| **C5** | No unclassified OAGIS scalar fields remain — every candidate is in one of buckets 1–8 with a ledger row OR explicitly skipped at noun-mapping time (Bucket 8 resolved). |

Under the §1A layer-first model, completion is reached **per pass + overall**. The program transitions to `completed` only when all three pass completion criteria hold AND C1–C5 hold:

| Per-pass criterion | Check |
|---|---|
| **Pass 1 complete (P1')** | Every C-wave (C1–C6) has its admitted-characteristic rows `authored_active` OR `authored_idempotent`; all C-DEFER rows are `deferred_diagnostic` / `deferred_pull_gated`; all C-RED rows are `red_held` with operator decision packet drafted. |
| **Pass 2 complete (P2')** | Every E-wave (E1–E13) has its admitted-entity rows `authored_active`; all RED-composite entity rows are either `authored_active` (after operator decision packet resolved) OR `red_held` (operator decision still pending). |
| **Pass 3 complete (P3')** | Every BC-wave's BC rows are `authored_active` OR `authored_idempotent` OR `panel_parked` OR `panel_rejected` OR `blocked_transient` OR `red_held` (composite-pin still required). |

When P1' + P2' + P3' + C1 + C2 + C3 + C4 + C5 all hold, the program is **complete**. The blueprint records the program-completion event with cumulative counts per pass (P1: chars authored / deferred / red-held; P2: entities authored / red-held; P3: BCs authored / idempotent / parked / rejected / blocked / red-held / deferred) and the operator-handoff list of RED + parked + blocked + DEFER rows requiring follow-up.

If a fatal stop fires before completion is reached, the program is **halted, not failed**. The agent records the halt reason, preserves all completed work in the affected pass, and surfaces the systemic issue. Operator can either resolve and resume (re-authorise A1–A5 if the issue is operator-resolvable) or restructure the blueprint (if the issue is doctrinal).

**Per-pass milestone discipline.** Pass 2 can begin as soon as Pass 1 has admitted the characteristics that Pass 2 entities depend on (composite-identity components from C3 in particular). Pass 3 can begin per BC-wave as soon as the corresponding Pass 1 characteristics + Pass 2 entities are `authored_active`. The dependencies form a DAG: characteristics → entities → BCs (per layer); within layers, items are mostly independent. The agent reads the dependency graph from the retry ledger to determine what is executable in any moment.

### 8.7 What this policy is *not*

- Not an authorisation to admit RED rows autonomously. RED rows always require a separate operator decision per row.
- Not an authorisation to override the §11.6 forbidden-term list, the no-vocabulary-stretch rule, or any Foundation invariant. The fatal-stop list (§8.4) preserves these.
- Not an authorisation to bypass DEC-fb0b12. Editorial amendments still require E1–E6 verdicts; pin them in the ledger before the AMBER row executes.
- Not an authorisation to write outside F3 / C5 governed paths. Cross-registry mutation, direct SQL, and legacy write paths are fatal triggers.
- Not an authorisation for an unbounded run. Budget / time caps (A5) constrain wall-time, tokens, and per-row latency.
- Not a replacement for the doctrine. Foundation, BCR, Vocabulary Evidence Framework, backbone doctrine, DEC-fb0b12 all still bind every row execution.

### 8.8 Resume-from-halt protocol

When a fatal stop fires:

1. The current session writes a halt note to the relevant ledger row (`halt_reason` + `next_action_text`) and to the program-completion state header (§6.7).
2. The session writes a closeout packet for the in-flight wave preserving any successfully completed rows. Already-active BCs are not rolled back.
3. The session closes via `devhub_session_close` with self-audit recording the halt as a `rules_obeyed` event (the halt was the rule firing as designed, not a violation).
4. The next session reads the ledger; finds the halted state; consults `halt_reason` + `next_action_text`; consults operator for unresolved operator-decision items.
5. Operator either resolves the systemic issue and re-authorises A1–A5 (program may resume), OR restructures the blueprint (program redesigned), OR closes the program at its current state (held rows become deferred indefinitely).

## 9. Non-goals

- This blueprint does not by itself authorise any panel run, substrate write, or cert. Authorisation is the **program-level A1–A5 act** per §8.1; until the operator records A1–A5, the blueprint is held doctrine. (A0 Compile / Preflight may run before A1–A5 per §6A.0 because it is read-only / no-LLM / no-write.)
- It does not amend any characteristic. The `ordered quantity` wording question (§7.2) and the `document type code` scope question (§7.3) remain operator decisions, recorded in this document but not pre-emptively resolved.
- It does not propose any supersession.
- It does not propose any new ADR. Where a wave surfaces a doctrine question, that wave's held packet drafts the ADR proposal.
- It does not specify the F4-v2 admission UI / API. F4-v2 v1 is still pre-implementation per the Vocabulary Evidence Framework.
- It does not commit to the 224-bf_name new-characteristic count as final. Operator review at F4-v2 admission time will reclassify ~70–80 candidates as DEFER (source-diagnostic) and coalesce others; the operator-admissible count after review is estimated at ~120–180.
- It does not touch `mcf.*`, `contract.*`, or `bcf.*` writer paths.
- It does not autonomously execute RED rows. Every new entity admission requires its own operator decision packet.

## 10. Open questions

| # | Question | Owner | Blocking |
|---|---|---|---|
| **OQ-1** | Packet-builder enhancement for sibling representation_term visibility (Wave B §7 path 1) — when? | Engineering | Affects AMBER row execution. Workaround is per-row `pin_evidence_text` shape pin in the ledger. |
| **OQ-2** | `ordered quantity` definition wording (audit §3.4) — clarify or leave? | Operator | Mildly. Blocks autonomous SI Line × ordered quantity if Maker parks on wording. |
| **OQ-3** | `document type code` scope broadening — accept Vocab Framework §11.4 worked-example reasoning? | Operator | Yes for W4 (JE × document type code). |
| **OQ-4** | Phase-2 ledger DBCP — when to file? | Operator | No until W5 or so. |
| **OQ-5** | Customer Shipment ↔ Delivery — entity-supersession question (W9)? | Operator | Yes for W9 design. |
| **OQ-6** | First composite-identity entity (Inventory Position W6) — does the registry's current structural-uniqueness rule satisfy BCR §4 acyclicity, or is a doctrine packet required? | Operator + architecture | Yes for W6. |
| **OQ-7** | UoM (unit of measure) — characteristic on quantity-bearing BCs, OR cross-cutting per-BC metadata? | Operator | Yes for BC-Reference / final-pass design. |
| **OQ-8** | BSL × line number outlier (Wave B §6) — remediate via supersession or formalise as banking exception? | Operator | No for the early BC-waves; surfaces only when BC-Bank reaches the BSL × line number row. |
| **OQ-9** | Inventory Position composite identity — Item × Location, or Item × Location × Batch + Serial as optional? | Operator | Yes for W6. |
| **OQ-10** | OAGIS extract version pinning — current extract is OAGIS 10.12 / enriched 2026-05-15. Re-scrape policy? | Operator | No for current waves; eventually yes. |
| **OQ-11** | A5 budget / time caps — what are the operator-stated maximums for (a) total program spend cap (USD), (b) total panel-call cap (count), (c) optional pass-level cap per Pass 1 / 2 / 3, (d) per-row latency cap (seconds, claim → writer-confirmation), (e) wall-time cap (hours / days, program-start)? | Operator | Yes for A5 program approval. |
| **OQ-12** | Should BC rows that bind newly admitted characteristics be scheduled inside their natural BC-domain waves (BC-AR / BC-AP / BC-GL / BC-Bank / BC-Master / BC-Procurement / BC-Inventory / BC-Production-* / BC-Logistics / BC-Quality-* / BC-Workforce / BC-Asset / BC-Reference) as the per-row characteristic becomes `authored_active` in Pass 1, OR held for a dedicated post-characteristic fill-in BC-wave that runs after all Pass 1 admissions complete? | Operator | Affects Pass 3 scheduling for the ~279 BC rows that bind net-new characteristics on existing entities. |
| **OQ-13** | RED row sequencing within an authorised program — does the operator commit to sequential RED decisions (one at a time, each its own packet) or parallel (multiple RED packets held simultaneously)? | Operator | Affects Pass 2 composite-RED E-wave cadence (E4 Inventory Position, E6 Production composite, E9 Quality composite, E12 Maintenance composite). |

## 11. Status + next operator action

**Status.** `held`. Awaiting operator review of the comprehensive blueprint (twelve deliverables per §0.2) and the A1–A5 program approval act.

**Next operator actions, in priority order.**

1. **Review the comprehensive reconciliation pass.** Particularly the load-bearing changes:
   - **§1** Evidence-Governed Foundation Buildout (5 admission rationales + 2 new safeguards) — replaces the strict orphan pull rule for program scope.
   - **§4A.10** Counts by admission rationale (AR-1..AR-5 distribution across 773 BCs).
   - **§6A** Program Compile / Preflight Layer (the only approved dry-run style; deterministic; no LLM).
   - **§6B** Batch + Cache Execution Economy (safe-batching policy; cache layers; retry economy; future microbatch design — NOT authorised).
   - **§6.3** Extended ledger schema with `admission_rationale`, `used_by_bc_target_count`, `target_entities`, `target_waves`, `entity_slice_name`, `composite_identity_decision`, `packet_hash`, `retry_reason`.
   - **§8.1** Updated A1–A4 to include the new sections.
2. **Decide on A1–A5 program approval.** Single operator act enabling autonomous execution:
   - **A1** — Approve §1 admission rule + §4A target-state catalogue + §4A.10 admission-rationale distribution + §4B layer-first re-aggregation.
   - **A2** — Approve §5.1 + §8.2 row classification + §1.2 admission rationale validation + §1.4 safeguards.
   - **A3** — Approve §5 per-(C/E/BC)-wave halt rules + §8.4 fatal stops + §6A compile-layer halt pre-conditions.
   - **A4** — Approve §6 retry ledger + §6A Compile / Preflight Layer + §6B Batch + Cache Execution Economy + §6.7 program-completion state header.
   - **A5** — Set budget / time caps (OQ-11): (a) total program spend cap (USD); (b) total panel-call cap (count); (c) optional pass-level caps per Pass 1 / 2 / 3; (d) per-row latency cap (seconds, claim → writer-confirmation); (e) wall-time cap (program-start to now).
3. **Decide OQ-1 posture for AMBER rows.** Either (a) wait for packet-builder enhancement before any AMBER autonomous run, or (b) accept per-row `pin_evidence_text` shape pinning recorded in the ledger.
4. **Decide OQ-14 layer-first vs mixed sequencing.** Recommendation: layer-first per §1A. Alternative: keep §4A.7 mixed-wave catalogue as execution view (do not adopt §4B / §5 layer-first). Two views NOT compatible at execution time — operator picks one. **This blueprint treats §5 layer-first as the authoritative execution view; §4A.7 is retained for traceability only.**
5. **Decide OQ-13 RED row sequencing.** Sequential (one packet at a time) OR parallel (multiple RED packets in flight). Under layer-first affects Pass 2 RED waves (E4 Inventory Position, E6 Production composite, E9 Quality composite, E12 Maintenance composite).
6. **Decide OQ-15 first-wave sequencing (layer-first).** §7 recommends sequential C1 → E1 → BC-AR for first program execution. Alternative: parallel C1 + E1 in one session, then BC-AR.
7. **Decide OQ-16 admission rationale review depth.** At A1, does operator review per-row admission rationale before approval (slow but thorough — ~70–100 grouped decisions), OR approve at the §4A.10 distribution level + delegate per-row rationale assignment to the compile layer (faster but less per-row scrutiny)?
8. **Authorise (or permit ahead of A1–A5) the §6A A0 compile layer to seed the Phase-1 Markdown retry ledger.** Per §6A.0, A0 is read-only / no-LLM / no-write and may run before A1–A5 — it is in fact the source of the **exact** target ledger and counts the operator reviews at A1–A5. The blueprint's §4A / §4A.10 / §4B / §5 counts are ranges; A0 produces the exact rows + hashes. A1–A5 remains required before any panel call, entity admission, characteristic admission, BC authoring, confirmation, or substrate write.
9. **Authorise the BCF × OAGIS PLN under DevHub.** Single program PLN, one task per pass per wave per §6.5 — i.e., 6 C-tasks + 13 E-tasks + 15 BC-tasks = 34 tasks under one PLN.
10. **Defer** OQ-2 to BC-AP-start (wording surfaces in BC-AP, not earlier), OQ-3 to BC-GL-start, OQ-4 to Pass 2 mid-stage, OQ-5 to E7-design, OQ-6 + OQ-9 to E4-design, OQ-7 + OQ-8 + OQ-10 to final-wave design time.

**No execution follows from this packet.** This blueprint is the held doctrine; the first authorisation that starts substrate change is the **program-level A1–A5 approval**. The §6A A0 compile / preflight layer may run independently (and is in fact needed) before A1–A5 because it is read-only / no-LLM / no-write — it produces the exact ledger and counts the operator reviews. Panel execution, entity admission, characteristic admission, BC authoring, confirmations, and substrate writes all follow §8 row execution rules only after A1–A5 is recorded.

**A0 / A1–A5 sequencing is now unambiguous.** A0 is the deterministic compile / preflight; A1–A5 is the operator approval that flips the agent into autonomous execution per the layer-first DAG (Pass 1 C-waves → Pass 2 E-waves → Pass 3 BC-waves grouped by entity / domain). Per-row execution rules (§8.2) govern GREEN / AMBER-pinned / RED / DEFER / UNKNOWN. Per-wave authorisation is not part of the model.

**Open questions added in this pass:** OQ-16 (admission rationale review depth). Previous open questions OQ-1..OQ-15 carry forward; the pull-related framing has been replaced with admission-rationale framing throughout.

## 12. Non-actions in this session

- No BCF panel calls.
- No `concept_registry.*` writes.
- No `bcf.*` writes.
- No characteristic amendments.
- No characteristic supersessions.
- No entity admissions.
- No BC authoring.
- No PR.
- No code edits.
- No direct SQL writes.
- No new ADR filed by this session (DEC-fb0b12 was filed in the prior session SES-a85b7b on 2026-06-23 and is referenced here as input).
- No DevHub plan creation by this session (the program PLN, if any, awaits operator decision per §11 priority 9).

**Operational state (carried forward unchanged).**

- bc-core PID 29912 from runtime worktree `C:\MyProjects\bc-core-runtime` at `c63db8ed`, healthy.
- bc-ai PID 28444, port 4300, healthy.
- Dirty primary worktree `C:\MyProjects\bc-core` untouched.
- bc-docs-v3 working tree clean at 38e22ee (post prior session SES-a85b7b housekeeping push).
- This blueprint is a new untracked file in bc-docs-v3 working tree; commit batch deferred per operator preference.
- DEC-fb0b12 ADR present at `bc-docs-v3/docs/adrs/ADR-fb0b12.md` from prior session.
- Wave A's 4 SI header BCs active; Wave B's 7 BCs active; two parked panels (`be8bea24-…`, `0a5d2e5c-…`) preserved as audit history.

Held for operator decision per §11.
