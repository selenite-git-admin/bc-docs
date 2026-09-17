---
uid: DEC-9b2e64
title: "Curated-content promotion — scope disposition (a product decision to close the wave at the governed vocabulary)"
description: "A product decision: with a single Platform database reproduced per environment by whole-database restore, there is no second independently-living Platform database to keep in step, so curated-content promotion (W3) is unnecessary and is closed at the governed vocabulary. This is NOT a claim of mechanical impossibility — a full unique-index inventory shows most named collections do carry enforceable real-world natural keys. This decision amends DEC-018138: for every collection other than the governed vocabulary it retires the per-collection canonical/digest-bound export and independent parity requirement (FR-12) and the per-collection reviewed-unit expectation, leaving whole-database restore fidelity (W1) as the recorded evidence boundary. The reference-resolution machinery (DEC-20d545) remains built, tested, and parked."
status: decided
subdomain: spine
focus: curated-content-promotion
date: 2026-09-17
project: platform
domain: platform
refs:
  - type: decision
    uid: DEC-018138
    label: "Curated-content promotion through the spine (W3) — this decision amends its collection scope and retires FR-12 for the non-vocabulary collections"
  - type: decision
    uid: DEC-20d545
    label: "Relational reference canonicalization — the machinery this disposition parks after completion"
  - type: decision
    uid: DEC-b1a286
    label: "The live database is schema and content ground truth; whole-database restore reproduces it per environment"
---

# Curated-content promotion — scope disposition (a product decision to close the wave at the governed vocabulary)

## Context

W3 (DEC-018138) made curated content a promotable data class and named five collections: metric content, business concepts and the governed vocabulary, the metric directory, source catalogs, and the contract families. The reference-canonicalization machinery it needed (DEC-20d545) was built and merged in full — canonical export that represents every foreign key by the referenced row's natural key (composite keys, exact constraint identity, and same-named cross-table constraints handled), and promotion that resolves those natural keys back to the target environment's own identifiers, covering single-collection, digest-bound cross-collection, and nested multi-level keys, each proven uuid-independent on disposable engines.

Name-based promotion exists for one purpose: to reproduce selected content across two databases that each mint their own internal identifiers — to push curated content into a database that **already exists with its own data**, without overwriting it. It is only necessary when more than one independently-living copy of the content must be kept consistent.

**A correction to the record.** An earlier reading of this scope looked only at declared primary-key and unique **constraints** and concluded that only the governed vocabulary was real-world-natural-keyed. That reading was incomplete: it missed **unique indexes** (many of them *partial*, scoped to active/non-archived rows), which enforce real-world identity just as constraints do. A full unique-index inventory shows the opposite — most named collections **do** carry enforceable real-world natural keys:

- **Metric directory** — `family (function_slug, subfunction_slug, theme_code)`, `group (family_id, group_code)`, `member (group_id, member_code)`, each unique among active rows.
- **Source catalogs** — a fully nested hierarchy: `source_field (object_id, field_name)` → `source_object (module_id, object_name)` → `source_module (version_id, module_name)` → `source_version (system_id, flavor, version_code)` → `source_system (provider_id, system_name)` → `source_provider (provider_name)`.
- **Contracts** — `admission_contract`/`ai_contract`/`source_contract` by name, `canonical_mapping (mapping_name)`, `contract_uid (family_code, uid_payload)`, and more.
- **Metric content** — `mcf.metric_contract (mc_name)` among active rows, `metric_contract_version (metric_contract_uid, version_code)`.
- **Governed vocabulary** — `characteristic (term)` among live rows; `representation_term (term)`.

So promotion is **not mechanically precluded** for these collections. The reason to close the wave is not that it cannot be done — it is that, under the platform's deployment model, it does not need to be.

## Decision

Curated-content promotion is **complete and closed at the governed vocabulary, as a product decision.** No further collections are wired into the promotion path.

**The basis is the deployment model, not mechanical impossibility.** There is a single Platform database — the one system of record. Each environment is stood up as a fresh, faithful **whole-database restore** of it (schema and all content, generated identifiers included), under the W1 backup/restore custody. A database cluster is the server that hosts that one Platform database (alongside the per-tenant databases); several clusters each host their own restored copy of the **same single** Platform database, not multiple independently-authored ones. Tenant databases are many, but they reference Platform content by binding and never hold promoted copies of it. There is therefore no second, independently-living Platform database whose curated content must be kept in step — which is the only situation name-based promotion serves. Restore already delivers an authentic database, curated content included; promotion is unnecessary.

**This decision amends DEC-018138.** For every collection other than the governed vocabulary — metric content (`mcf.*`), business concepts (`concept_registry.*` beyond the vocabulary tables), the metric directory (`metric_directory.*`), source catalogs (`source.*`), and the contract families (`contract.*`) — the following DEC-018138 requirements are **retired**:

1. §1/§2 — a per-collection canonical, deterministic, digest-bound content export in the versioned tree.
2. §3/§6 — promotion of that collection through the runner and the release-manifest activation path.
3. §5 / **FR-12** — the per-collection parity gate proving a from-versioned-export build equals an authorized immutable scoped capture of live content.
4. Consequence 5 — that each of these collections lands as its own reviewed implementation unit.

The governed vocabulary retains its delivered export/promotion path (the worked example); its live authorized-capture parity run (a Gate-① step) was never executed and is retired along with the rest.

**The remaining evidence boundary is whole-database restore fidelity (W1), and it is explicitly not FR-12.** Whole-database restore faithfully reproduces the source database — this is evidenced by the W1 backup/restore custody and the from-zero schema-equivalence gate — but it is **not** the per-collection canonical/deterministic/digest-bound export and **independent** content parity gate that DEC-018138/FR-12 defined. This decision does not claim `build == dump == live` for curated content in the FR-12 sense; it retires that per-collection guarantee for the non-vocabulary collections and records that the platform's curated content is reproduced, and evidenced, as part of whole-database restore.

The promotion machinery (canonical export, reconcile, the release manifest, and reference resolution) remains **built, tested, and parked** — available if a future need to update curated content into an already-live database arises, at which point the collections above already present the natural keys it needs.

## Consequences

1. For a new environment, an authentic database — curated content included — is reproduced by whole-database restore of the single Platform database. There is no per-collection content parity gate for the non-vocabulary collections; their content-reproduction evidence is the W1 restore fidelity boundary named above.
2. DEC-018138's promotion requirements for the non-vocabulary collections are retired (enumerated above); its decision otherwise stands. This ADR is the governing amendment of that scope.
3. DEC-20d545's machinery is correct and merged; it is parked, not removed. Its illustrative premise about the metric-directory family key is, in fact, borne out by the enforced schema (an active-scoped unique key on `(function_slug, subfunction_slug, theme_code)`) — but the metric directory is still not promoted, on the product grounds above.
4. No production or live-promotion action is taken or authorized here.

## Not decided here

- Whether a future product need — keeping a second, already-live Platform database's curated content in step with the system of record — re-opens a specific collection. That would be its own decision, gated on such a need actually existing; the natural keys the machinery needs are already present in the collections above.
