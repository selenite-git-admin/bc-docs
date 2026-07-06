---
title: BCF × OAGIS Pass-2 E2 — Equipment Operator-Decision Packet (2026-06-25)
description: Recommendation-leading, falsifiable decision packet for the Equipment entity admission question, held from Pass-2 E2 wave. Six sections per operator structure (Recommendation Up Front + Decision Test + Standards Evidence + BC-Binding Consequences + Foundation Invariant Check + Operator Gate). Recommendation is admit-as-peer-entity with moderate confidence; principal contrary evidence (OAGIS Equipment-Master has Item-Master shape, not Asset shape) shown prominently so operator can reject without redoing research.
status: held_operator_gate
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-2-e2-equipment-decision
related_docs:
  - bcf-oagis-pass-2-entry-note-2026-06-25.md
  - bcf-oagis-pass-2-e1-item-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-2-e2-asset-maintenance-closure-checkpoint-2026-06-25.md
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
---

# BCF × OAGIS Pass-2 E2 — Equipment Operator-Decision Packet

> Held from E2 closure 2026-06-25 because the Asset-subtype-vs-peer-entity choice is structural and too consequential for a side decision inside a transport wave. This packet exists to give the operator one falsifiable decision: admit Equipment as a peer entity, model Equipment as an Asset discriminator/subtype characteristic, or defer pending more evidence.

> No transport. No panel calls. No substrate writes.

---

## 1. Recommendation Up Front

**Admit Equipment as a peer entity in a later E-wave (Option A).** Confidence: **moderate (3/5).**

One sentence: two of three standards consulted (OAGIS 10.12, SAP EAM module split) place Equipment as a peer master of Asset rather than a subtype, and the substrate cost of being wrong on this — one extra entity to supersede — is bounded; ISO 55000 is permissive on this choice and does not force the question either way.

The principal contrary evidence the operator must weigh before approving: **OAGIS 10.12 `equipment-master` is structurally shaped more like `item-master` than like `asset` — same Item Identifier Set / Customer-Manufacturer-Supplier Item Identification / Operational Role / Manufacturing Party fields**. This is a substantive signal that "Equipment as peer of Item" or "Equipment as a kind of Item" is a third interpretation that this packet does not recommend but that the operator might.

The recommendation is to **author Equipment as an entity that is peer to both Asset and Item**, not as a subtype of either, with admission deferred until E3 or later, AND with operator framing on the definition that explicitly names which trade-side fields (manufacturing-party, supplier-item-identification) are in-scope versus excluded — the packet calls this out as a sharpening question in §6.

---

## 2. Decision Test

> Would making Equipment active now reduce future BC ambiguity, or create future supersession / migration churn?

Sub-tests, all answerable from this packet:

| Sub-test | Answer | Source |
|---|---|---|
| Does any current Pass-1 BC row block on Equipment specifically? | **No.** 15 BC-ledger rows target the `asset-maintenance-simple` slice; all 15 are generic dimension fields (type_code, base_uom_code, storage_uom_code, …) tied to master-data root, not Equipment-specific. | §4.1 + bcf-bc-coverage-ledger.json records[].target_slices |
| Does any current Pass-3 binding require Equipment as a target entity to be unambiguous? | **Likely yes**, but not yet exercised. A0.5 catalogue lists Equipment in the asset-maintenance-simple slice alongside Asset and Maintenance Order; Pass-3 BCs like "maintenance order targets equipment" need an unambiguous entity to bind to. | §4.2 + bcf-oagis-a0.5-template-catalogue-2026-06-24.md L362 |
| Does deferring block E3 (master-data 8 AMBER) or Pass-1 retrofit? | **No.** E3 entities (Business Partner / Cost Centre / Location / Org Unit / Party / Price List / Price List Item / Project) are independent of Equipment. Pass-1 retrofit on the 17 BCs newly unlocked by E1 + Asset + Maintenance Order can proceed without Equipment. | §4.3 |
| Does admitting Equipment now create supersession risk if Option A is wrong? | **Bounded.** Substrate carries one extra entity. Foundation Invariant III formal-supersession path is the correction route (mint new entity_id, supersede old, preserve audit chain). The 39-field OAGIS shape needs a clean definition before admission. | §5 |
| Does admitting Equipment now create supersession risk if Option B (discriminator) is right? | **Higher.** A discriminator field on Asset would be the simpler model. If we admit Equipment as peer and later decide it should have been a discriminator, every Pass-3 BC bound to Equipment must rebind to `Asset.assetType='equipment'` — that is migration churn at the BC layer, not just the entity layer. | §4.4 + §5 |

**Net decision test:** admitting Equipment as peer now does NOT reduce immediate Pass-1 BC ambiguity (no row blocks on it), but DOES preempt Pass-3 BC ambiguity at the cost of one entity that may later need supersession if the discriminator interpretation wins. Deferring is cheap; admitting now is moderate-risk-bounded.

---

## 3. Standards Evidence

### 3.1 Source-coverage labelling

| Standard | Source actually consulted | Coverage |
|---|---|---|
| OAGIS 10.12 | Local enriched extract `.claude/desktop-prep-bundle-c1-clean-2026-06-25/oagis/extract.json` — 133 nouns including `asset`, `equipment-master`, `maintenance-order`, `item-master` — full field lists and component structure | **Primary** |
| SAP EAM (S/4HANA) | SAP Community blog posts + SAP Help Portal articles (web-fetched, not vendor-direct) — table-level data model (EQUI, IFLOT, EQUZ, ILOA, ANLA) | **Secondary — table model documented, runtime semantics summarised** |
| ISO 55000 / 55001 | Standards body summaries (assetleadership.net, upkeep.com, Wikipedia), iso.org abstract pages — vocabulary definitions only, full normative text paywalled | **Tertiary — vocabulary only, not normative hierarchy** |

This packet does NOT have direct access to the ISO 55000:2024 normative text, the OAGIS 10.12 PDF specification, or any running SAP EAM system. Claims are grounded in what was actually consulted.

### 3.2 OAGIS 10.12 — peer with shape divergence

OAGIS 10.12 carries `asset`, `equipment-master`, and `maintenance-order` as **three distinct nouns** at different domain/subfunction classifications:

| Noun | Domain / subfunction | Description (from OAGIS) | Field count |
|---|---|---|---|
| `asset` | asset_management / fixed_assets | "Any resource owned or controlled by a business or an economic entity." | 17 |
| `equipment-master` | master_data / equipment | "A master definition for a piece of equipment." | 39 |
| `maintenance-order` | asset_management / maintenance | "A Maintenance Order is an order for a machine, building, tooling or fixed asset to be repaired or for preventitive maintenance to be performed." | 29 (header) + line |

The peer-vs-subtype question is decided in OAGIS by treating these as separate nouns. No subtype declaration exists between them. The asset noun field list is a fixed-asset-shape (Asset Type, Serial Number Identifier, Contract Reference, Vendor Party, Supplier Party, Manufacturing Party, Effective Time Period, Order Date Time…) — financial-and-procurement framing.

#### The contrary evidence the operator must weigh

`equipment-master` has these complex fields **also present in `item-master`**:
- Item Identifier Set
- Customer Item Identification
- Manufacturer Item Identification
- Supplier Item Identification
- Operational Role
- Manufacturing Party

This is item-master shape. It tells us OAGIS modelled equipment-master as a **product/material-style master** with procurement-side identification fields, not as a fixed-asset-style master. The two interpretations this opens:

1. Equipment Master is its own peer master because OAGIS designed it as a separate noun with its own domain;
2. Equipment Master is conceptually a specialised Item Master with maintenance metadata, and BareCount could legitimately treat it as a discriminator/scope variant of Item (not Asset).

Neither interpretation matches the A0.5 catalogue's a-priori placement of Equipment in the `asset-maintenance-simple` slice next to Asset. If the operator accepts interpretation 2, Equipment becomes a discriminator on Item, not Asset, and the slice assignment in A0.5 was the wrong frame from the start.

The maintenance-order noun targets "a machine, building, tooling or fixed asset" — covering both asset-shape and equipment-shape targets. The MO header field list does NOT carry an explicit foreign-key field to either Asset or Equipment in the local extract; cross-entity references happen at the BC layer in OAGIS, not via hard FK in the noun.

### 3.3 SAP EAM — peer with module separation

SAP separates the financial-asset record (FI-AA `ANLA`) and the operational-equipment record (PM `EQUI`) at the **module level**, not at the table level only:

| SAP table | Module | Purpose |
|---|---|---|
| `ANLA` | FI-AA (Fixed Asset Accounting) | Financial asset master — depreciation, asset class, cost-centre attribution, value adjustments |
| `EQUI` | PM (Plant Maintenance) / EAM | Equipment master — maintenance object, serial number, manufacturer, plant assignment, equipment category EQTYP |
| `IFLOT` | PM / EAM | Functional Location — spatial/process hierarchy where equipment is installed |
| `EQUZ` | PM / EAM | Equipment time segment — time-sliced binding equipment → functional location |
| `ILOA` | PM / EAM | Location-equipment cross-reference (used to navigate FL ↔ EQUI relationships) |

Equipment in SAP is **not a subtype of fixed asset**. They are two separate records that an enterprise may link 1:1 in practice (the same physical pump has an ANLA record for depreciation accounting and an EQUI record for maintenance scheduling), but the linkage is operational, not structural. The lifecycles diverge: a pump can be operationally retired (EQUI) before being financially fully depreciated (ANLA), or financially written off before being physically dismantled.

This is the strongest peer-entity evidence in this packet. SAP is the dominant enterprise EAM implementation; its data model is a load-bearing reference for what enterprises *actually run*. SAP's choice to keep Asset and Equipment in separate modules — with separate masters, separate lifecycle gates, and separate teams owning them — supports peer-entity over discriminator.

### 3.4 ISO 55000 / 55001 — permissive on hierarchy

ISO 55000:2024 defines an Asset as "an item, thing or entity that has potential or actual value to an organization." The standard's scope statement says the standards "apply to tangible assets (e.g. equipment, property, inventory, infrastructure, IT, human resources, etc.) and intangible assets (e.g. leases, options, brands, …)".

This phrasing places **equipment as one example category of tangible asset**, which is consistent with either a peer-entity model OR a discriminator-on-asset model. ISO 55000 does NOT force a hierarchy and does NOT mandate that equipment be a sub-record of asset. Equipment in ISO 55000 is a vocabulary category, not a structural entity.

ISO 55001 sets management-system requirements (governance over asset-management activities) and is implementation-agnostic on data model.

**Net standards finding:** OAGIS = peer (with the item-shape complication). SAP EAM = peer (module-separated). ISO 55000 = permissive. No standard mandates the discriminator path; one standard's structural shape (OAGIS Equipment Master) is more item-shaped than asset-shaped, opening the alternate interpretation.

---

## 4. BC-Binding Consequences — "Is this equipment under maintenance?"

The Pass-1 / Pass-3 BC question that motivates the decision: *"Is this equipment currently under a maintenance order?"* Below is how the question binds under each option.

### 4.1 Current Pass-1 BC ledger — no Equipment blockage

The BC-coverage ledger (`bcf-bc-coverage-ledger.json`) covers Pass-1 C1 + C2 only (86 rows). 15 of those target the `asset-maintenance-simple` slice. **All 15 are generic master-data dimension fields** (type_code, base_uom_code, storage_uom_code, usage_restriction_code, formulation_code, tracking_method_code, shipping_uom_code, alternate_uom_code, expiration_control_code, source_type_code …). None are Equipment-specific identifier or relation fields.

**Implication:** the Pass-1 layer is not currently blocked by the Equipment decision. The decision is about Pass-3 BC binding, not Pass-1 character admission.

### 4.2 Pass-3 BC binding under Option A — peer entity

```
BC: maintenance_order.target_object
  bound to: Equipment   (entity_id = ?)  via canonical_field cf__equipment_identifier
           OR
  bound to: Asset       (entity_id = 47f66f57-d73c-4512-a106-0f8a6e809e72)  via cf__asset_identifier
  resolution: runtime routing rule based on source-system EQTYP or asset_type_code
```

Costs:
- Two parallel BCs (or one BC with a discriminated reference) per maintenance-order-target relationship
- Runtime routing logic at the canonical-resolution boundary
- Clear ontology — Asset and Equipment never collide

Benefits:
- Maintenance-order can directly reference whichever target the source system uses without source-shape distortion
- OAGIS / SAP shape is preserved end-to-end (Foundation Invariant IV: explicit references)

### 4.3 Pass-3 BC binding under Option B — discriminator on Asset

```
BC: maintenance_order.target_object
  bound to: Asset (entity_id = 47f66f57-d73c-4512-a106-0f8a6e809e72)
  filter:   Asset.asset_type_code = 'equipment'   (a new characteristic on Asset)
```

Costs:
- A new identity-bearing characteristic on Asset (`asset_type_code`) admitted in a future Pass-1 / Pass-2 sub-wave
- Source-system mapping loses fidelity: SAP EQUI rows get materialised as `Asset` rows with `asset_type_code='equipment'`, losing the FI-AA-vs-PM distinction
- BCR §4 single-identity is preserved (Asset has one identifier; equipment-ness is a property)

Benefits:
- One entity for all operational masters → simpler substrate
- Cheaper BC binding — one binding, one filter
- Easier ad-hoc analytics ("how many of my assets are equipment?")

### 4.4 Pass-3 BC binding under Option C — defer

```
BC: maintenance_order.target_object
  bound to: <held — not bindable to any active entity until decision lands>
```

Costs:
- Pass-3 BC binding for any maintenance-order-target work waits for the decision
- E3 can still proceed (Equipment is not in master-data slice)
- Pass-1 retrofit can still proceed (no asset-maintenance-simple row blocks on Equipment)
- A future operator review consumes one panel cycle to re-open this question

Benefits:
- Zero immediate substrate cost
- Time to gather more evidence (e.g., ask a domain expert, read OAGIS 10.12 normative text)

### 4.5 The migration-churn estimate

If Option A is wrong (we admit peer, later decide discriminator is right):
- 1 entity to supersede (Equipment)
- N Pass-3 BCs rebind from Equipment to Asset (filter on asset_type_code)
- N = number of maintenance-order-target and equipment-master-specific BCs admitted between now and the decision reversal

If Option B is wrong (we admit as discriminator, later decide peer is right):
- 1 characteristic (asset_type_code on Asset) to supersede
- 1 entity (Equipment) to author fresh
- N Pass-3 BCs rebind from Asset+filter to Equipment

Migration churn is comparable in size in either direction. Option C (defer) carries zero immediate churn but trades cycle time.

---

## 5. Foundation Invariant Check

### 5.1 Invariant III — substrate immutability

> All state is immutable.

| Option | Invariant III posture |
|---|---|
| A — peer entity | Admitting Equipment locks one new entity_id into substrate. If interpretation changes later, the formal entity-supersession path (mint new entity_id, supersede old, preserve audit chain) applies — bounded cost. |
| B — discriminator | Admitting `asset_type_code` characteristic on Asset locks the discriminator into substrate. Reversal requires characteristic supersession AND amending the (already active) Asset definition body to remove the discriminator clause — Asset is already active per E2, so amending its definition triggers entity-version supersession on Asset itself. **This is the cost B owes that A does not.** |
| C — defer | No substrate change. Invariant III is not exercised. |

Net: Option C is invariant-neutral. Option A is bounded. Option B carries cascading supersession risk (because Asset is already active — Option B retroactively changes what Asset means).

### 5.2 Invariant IV — explicit references

> All references are explicit.

| Option | Invariant IV posture |
|---|---|
| A — peer entity | Two explicit entities; BCs reference whichever they mean. Maximum clarity. Routing logic at canonical-resolution time is explicit (mapping table). |
| B — discriminator | One entity with a type field. BCs that "mean" equipment must encode the filter (`asset_type_code='equipment'`) in the binding. The reference is technically explicit (you can see the filter) but the *meaning* "this is an equipment" is implicit in the type field, not in the entity reference. Tension with the spirit of IV. |
| C — defer | No new references; existing references stand. |

Net: Option A best preserves the spirit of Invariant IV. Option B technically preserves explicitness but encodes meaning in a filter rather than in an entity choice.

### 5.3 No lower-layer compensation rule

The Foundation hard rule: *no lower-layer compensation for upper-layer semantic gaps.*

Choosing Option B (discriminator) because it's "simpler at the substrate layer" while OAGIS and SAP both model Equipment as a peer is the textbook lower-layer-compensating-for-upper-layer-semantic-gap. Standards say peer; substrate would say discriminator; the substrate would be compensating for "ergonomics" at the expense of OAGIS/SAP shape fidelity.

This is the strongest single argument against Option B.

### 5.4 Repair-location classification

For any operator-decision packet that triggers Foundation review, the repair-location naming (A–F):

| Repair location | Asset–Equipment decision location |
|---|---|
| **B (contract semantics)** | This is where the question lives. We are defining whether Equipment is a peer concept or a refinement of Asset at the BCF concept-grammar layer. |
| **C (mapping / binding)** | Pass-3 BC bindings will sit here once Equipment is decided. They cannot land cleanly until B is decided. |
| **D (evaluation)** | The canonical resolution service routes source-system EQUI / ANLA rows to either Equipment or Asset under Option A. Under Option B, it routes all to Asset with a type code. |
| **E (storage)** | Substrate stores the Equipment entity_id under Option A; the asset_type_code characteristic under Option B; nothing under Option C. |

The decision is correctly located at **B**. Any choice that defers the decision but lands D/E artefacts (e.g., admitting a temporary equipment characteristic on Asset just to unblock something) would be lower-layer compensation.

---

## 6. Operator Gate

Exactly one of three. The operator picks.

### 6.A. Admit Equipment as peer entity in a later E-wave

Operator approves Equipment for a future E-wave (E3 or later, sequenced operator-side). The packet author will:
- Author an Equipment-definition packet under the same Checker-First Preflight 6-Q discipline
- Resolve the OAGIS-item-shape contrary evidence in the definition body — operator must frame whether the manufacturing-party / supplier-item-identification fields are in scope (treat Equipment as both a maintenance-target and a procurement-master) or excluded (treat Equipment as maintenance-target only and let Item carry procurement)
- Stage Equipment for the E-wave panel run with no fast-lane bypass beyond what the orchestrator already does

This is the **recommended option** with moderate confidence.

### 6.B. Model Equipment as Asset discriminator / subtype characteristic

Operator approves modelling Equipment as an `asset_type_code` characteristic on Asset, with Pass-3 BC bindings going to `Asset filter asset_type_code='equipment'`. The packet author will:
- Mark Equipment as not-an-entity in the A0.5 catalogue
- Author the `asset_type_code` characteristic admission packet for a future C-wave (the characteristic family per BCR), with `cross_function` admission scope
- Amend the active Asset entity definition body to explicitly admit the discriminator clause (this triggers Asset entity-version supersession — Foundation Invariant III cost)

Operator should pick this only if interpretation 2 of the OAGIS contrary evidence (Equipment ⊂ Item, not peer-of-Asset) is rejected AND the substrate simplification is judged worth the Asset-supersession cost.

### 6.C. Defer pending more evidence

Operator approves deferring the Equipment decision. The packet author will:
- Mark Equipment as `held_operator_decision` in the A0.5 catalogue
- Note in the next gate's packet (E3 or Pass-1 retrofit) that Equipment-target BC bindings are held until decision lands
- Reopen this packet when one of: (a) operator has consulted OAGIS 10.12 normative text directly, (b) operator has consulted a domain expert with SAP EAM / ISO 55000 implementation experience, or (c) a Pass-3 BC actually needs to bind to Equipment and the work demands the decision

This is the **safest** option. Zero substrate cost, zero risk, time to reach a higher-confidence verdict.

---

## 7. What the recommendation depends on

The recommendation (Option A) becomes wrong if any of these turn out to be true:

| Falsifier | Effect |
|---|---|
| OAGIS Equipment-Master's item-shape is load-bearing for BareCount (manufacturing-party / supplier-item-identification fields are used by Pass-3 BCs) | Option B (Equipment-as-discriminator-on-Item) becomes the better answer — neither A nor the originally-considered B-on-Asset. |
| Operator's mental model of "equipment" matches SAP EQUI's pure-maintenance framing, NOT OAGIS's procurement-master framing | Option A remains right but the Equipment definition body must explicitly exclude the OAGIS-item-shape fields (operator gates the definition before transport) |
| BareCount tenants in scope for Phase 0 will never run SAP EAM (only QuickBooks / NetSuite / Tally) | The peer-vs-discriminator decision is academically settled but operationally inert; Option C (defer) becomes the cheapest correct answer |
| A future ADR locks BareCount's master-data model to "one master entity per operational concept" as an Invariant | Option B (discriminator) becomes mandated by policy; Option A would be locked-out by the new Invariant |

If any of these conditions hold or are close to holding, the operator should reject Option A and pick B or C accordingly. The recommendation is falsifiable; the contrary evidence is in §3.2.

---

## 8. Scope locks honoured authoring this packet

- 0 panel calls.
- 0 substrate writes.
- 0 transport script invocations.
- 0 DDL changes.
- 0 ADR authoring (the packet RECOMMENDS that the operator's chosen option may warrant a DEC ADR; it does not write one).
- 0 changes to BC-coverage ledger.
- 0 changes to A0.5 catalogue.
- 0 amendments to active Asset / Maintenance Order / Item entities.

Source coverage labelled honestly in §3.1; ISO 55000 / 55001 normative text was not consulted directly.

Held.
