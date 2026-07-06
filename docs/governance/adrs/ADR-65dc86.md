---
uid: DEC-65dc86
title: "BCF is the forward governance model for business meaning; BF/BO is legacy compatibility"
description: "Sunset declaration: BCF Registry (Entity / BusinessConcept / Characteristic) is the forward model; BF/BO becomes legacy compatibility with no immediate deletion; primary nav and new product investment move to BCF; retirement is a later dedicated program."
status: decided
date: 2026-05-24T02:06:30.191Z
project: bc-docs
domain: contracts
subdomain: catalog
focus: lifecycle
---

# BCF is the forward governance model for business meaning; BF/BO is legacy compatibility

## Context

BCF Registry expresses business meaning with three structural disciplines that BF/BO does not: (a) structural identity — Entity has an identity-bearing property set, BusinessConcept has the (entity, characteristic, representation term) tuple, Characteristic is an immutable semantic atom; (b) governed lifecycle — every authoring run is panel-verified and operator-confirmed under C5, every publication is a draft→active transition with full cert provenance; (c) immutable-atom semantics for vocabulary, which makes 'meaning drift under a stable reference' (Foundation Invariant I) impossible by construction.

BF/BO is the earlier, looser shape. It is productive — 7,072 BFs back the metric chain and the green Finance readiness — but it lacks the structural identity discipline (BF is a flat name + type), the governed lifecycle discipline (no panel evidence, no operator-confirm-required gate, no publication cert), and the immutable-atom discipline (a BF can be edited in place). Continuing to invest in BF/BO product surface alongside BCF would (1) split operator muscle memory across two models, (2) keep authoring drift open — new business meaning quietly going into BF when it should land in Characteristic / BusinessConcept, (3) make the BCF investment look like a parallel option rather than the forward model.

Hard deletion now is rejected because BF/BO is currently load-bearing across the production pipeline (13 FK edges, including cc_field_mapping which is the spine of the metric chain) and because no BCF authoring UI exists yet — operators have nowhere to author replacement business meaning. A direction-setting ADR with explicit non-goals is the safe move: it commits the product strategy without breaking the running pipeline, and it makes the eventual retirement program a deliberate program with its own gates, dependency inventory, bridge / backfill, and validation proofs — not a single PR delete. The 'authoring freeze when BCF authoring UI exists' clause is the operational anchor that prevents the legacy classification from becoming permanent.

## Decision

The BCF Business Concept Registry — Entity, BusinessConcept, and Characteristic — is the forward governance model for business meaning in BareCount. The legacy Business Field (BF) and Business Object (BO) model is reclassified as **legacy compatibility**, not a parallel forward product.

This is a direction-setting decision. It changes how the product is named, navigated, and invested in. It does NOT delete any BF/BO code, table, controller, service, or row. It does not migrate any data. Implementation of the consequences is sequenced and gated separately.

### Operative rules (effective immediately)

1. **Forward model.** New business-meaning work — new entities, concepts, characteristics, vocabulary — is authored through the BCF Registry path (F3 + F4-v2 + B6 panel + C5 governance + B10a/B10b publication). The product narrative, documentation, and roadmap treat BCF as the canonical model.

2. **Primary navigation moves to BCF.** Once the BCF operator console exists in bc-admin (UI-S2 onwards), "Business Concepts" becomes a primary navigation group. The existing "Business Chain" group, which currently hosts BF/BO surfaces, will be removed from primary navigation **only after** the BCF console is operator-usable end-to-end. UI-S2 itself does not retire any BF/BO page.

3. **No hard deletion now.** BF/BO remains load-bearing across the platform: contract.canonical_contract.object_id, contract.cc_field_mapping.business_field_id, contract.observation_field_map.business_field_id, runtime.reader.business_object_id, operations.bo_enrichment_log / bo_verification_log, plus BF/BO supersession / alias / object-field / object-relation tables — 13 foreign-key edges in total, 7,072 BF rows and 203 BO rows on bc_platform_dev, and a substantial code surface in bc-core (~50 files including mc-onboarding, oc-onboarding, oagis-onboarding, reader.service, seed-context-readiness, and the BCF C5/C6/C7/D412/D413 governance arc). Hard deletion before a migration program would break the existing canonical chain, every reader binding, the cc_field_mapping spine of the metric chain, and the green Finance chain status.

4. **Authoring freeze gated on BCF authoring UI.** BF/BO authoring (creating new BFs / BOs) is permitted until a BCF authoring UI exists. Once that UI exists, BF/BO authoring is frozen for new greenfield work; BF/BO authoring is permitted only as continuity for existing-chain needs (extending an already-bound canonical contract, fixing an existing OC field map) and is discouraged. The freeze is operational discipline, recorded here as a forward commitment; it is not enforced by code in this ADR.

5. **Services, controllers, tables, and data persist.** Until the dedicated retirement program completes, BF/BO services and controllers continue to back the production pipeline. They are not deprecated as code surfaces; they are reclassified as legacy compatibility surfaces.

6. **Retirement is a separate, later, multi-PR program.** Actual sunset of BF/BO requires a dedicated design gate that produces, at minimum: a complete dependency inventory (FK + code + UI + docs + ops); a per-table data-migration strategy (7K BFs → BusinessConcepts, 200 BOs → Entities, both through BCF governed authoring); rebind plans for canonical_contract, cc_field_mapping, observation_field_map, reader; compatibility windows for tenants; validation proofs (chain integrity, metric snapshot equivalence) before each retirement step; rollback rules per stage; explicit operator gates between stages. No BF/BO row is dropped, no BF/BO table is renamed, no FK is broken until this program completes its stage-by-stage validation.

7. **New UI investment goes to BCF.** New operator-facing surfaces — browse, publication, evidence inspection, eventually authoring — are built against the BCF Registry endpoints (F5-S2, provenance-inspection read, B10a/B10b publication). The BF/BO pages in bc-admin (BusinessFieldDetailPage, BusinessCatalogPage, CreateBusinessObjectPage, CreateCanonicalContractPage where it binds BO, CreateObservationContractPage, CanonicalReaderWizardPage) receive maintenance fixes only; they receive no feature investment.

### What this decision does not do

- It does not delete or rename any BF/BO table, column, or FK.
- It does not remove any BF/BO controller or service.
- It does not freeze BF/BO authoring at this moment — the freeze trigger is "BCF authoring UI exists", which is itself a later UI gate.
- It does not migrate any of the existing 7,072 BF or 203 BO rows.
- It does not break the existing Onboarding SOP "Business Field and Business Object Onboarding" — that SOP remains current until the retirement program supersedes it.
- It does not change the metric chain runtime, the readiness funnel, or the chain-status SSOT.
- It does not retire the existing "Business Chain" nav group in UI-S2.

These are intentional non-goals. The point of this decision is to set direction without disturbing the production pipeline. Each consequence has its own gate, in its own time.

### Grounding

- **business-concept-registry-backend-mvp-closeout.md** (bc-docs-v3, accepted, commit 589a07d) — the BCF backend is complete through B10b-S4, with live proofs for Entity (Sales Order Line), BusinessConcept (Sales Order Line · unit price (amount)), and Characteristic (lead time).
- **business-concept-registry-ui-mvp-planning.md** (bc-docs-v3, accepted, commit 58f67db) — UI-S1, the operator console MVP planning note.
- **ADR DEC-26b6e2 — Immutable Characteristic Atoms** — the immutability commitment that distinguishes a Characteristic from a versioned shape, and that BF (which is essentially a versionable atom with weaker discipline) does not capture.
- **B10 implementation design and the B10a-S4 UI-readiness checklist** — the original architectural ground.
- **FK dependency map (this session, 2026-05-23)** — 13 referencing rows into contract.business_field / contract.business_object, including the canonical_contract / cc_field_mapping / observation_field_map / reader spine.
- **Live state on bc_platform_dev** — 7,072 BF rows, 203 BO rows; 3 BCF Registry objects (Sales Order Line, Unit Price, lead time, all active).
