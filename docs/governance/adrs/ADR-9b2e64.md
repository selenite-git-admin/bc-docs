---
uid: DEC-9b2e64
title: "Curated-content promotion — scope disposition (closed at the governed vocabulary)"
description: "Curated-content promotion (W3) is complete and closed at the governed vocabulary. A mechanical review of the enforced schema shows only the vocabulary is identified by a real-world natural key; every other named collection is anchored on generated identifiers and is version-centric, so it cannot be keyed for cross-database promotion without re-shaping how it is composed — out of scope for the spine. With a single Platform database reproduced per environment by whole-database restore, restore already delivers an authentic database including all curated content, and the narrow case promotion serves (updating content into a second, already-live database) is not on the roadmap. The reference-resolution machinery remains built, tested, and parked for any future need."
status: decided
subdomain: spine
focus: curated-content-promotion
date: 2026-09-17
project: platform
domain: platform
refs:
  - type: decision
    uid: DEC-018138
    label: "Curated-content promotion through the spine (W3) — this dispositions its collection scope"
  - type: decision
    uid: DEC-20d545
    label: "Relational reference canonicalization — the machinery this disposition parks after completion"
  - type: decision
    uid: DEC-b1a286
    label: "The live database is schema and content ground truth; whole-database restore reproduces it per environment"
---

# Curated-content promotion — scope disposition (closed at the governed vocabulary)

## Context

W3 (DEC-018138) made curated content a promotable data class and named five collections: metric content, business concepts and the governed vocabulary, the metric directory, source catalogs, and the contract families. The reference-canonicalization machinery it needed (DEC-20d545) was built and merged in full — canonical export that represents every foreign key by the referenced row's natural key (composite keys, exact constraint identity, and same-named cross-table constraints all handled), and promotion that resolves those natural keys back to the target environment's own identifiers, covering single-collection resolution, digest-bound cross-collection resolution, and nested multi-level keys. Each was proven uuid-independent — a from-empty rebuild reproduces the exact source content though every generated identifier differs (`build == dump == live`) — on disposable engines.

Name-based promotion exists for one purpose: to reproduce selected content across two databases that each mint their own internal identifiers — that is, to push curated content into a database that **already exists with its own data**, without overwriting it. It is only necessary when more than one independently-living copy of the content must be kept consistent.

A mechanical review of the **enforced** schema — every primary-key and unique constraint across the five collections — established which collections can actually be keyed by real-world identity rather than by environment-specific generated identifiers.

## Decision

Curated-content promotion is **complete and closed at the governed vocabulary.** No further collections are wired into the promotion path. The reasons are mechanical and operational.

1. **Only the governed vocabulary is real-world-natural-keyed as built.** Its rows are identified by a text term and reference nothing else. Every other named collection is anchored on generated identifiers and is version-centric: the entity and business-concept anchors, the metric-directory family and group, the six contract families, and the metric-contract tables all have generated-identifier primary keys, and their human identity lives in append-only version rows that are not themselves uniquely constrained on that identity. There is therefore no real-world key for promotion to translate. Inventing one would mean changing how those areas are composed, which is out of scope for the spine — the spine reproduces what exists, it does not re-shape it, and it does not have the vantage point to judge that composition.

2. **There is a single Platform database, reproduced per environment by whole-database restore.** The Platform database is the one system of record. Each environment is stood up as a fresh, faithful restore of it — schema and all content, generated identifiers included. A database cluster is the server that hosts that one Platform database (alongside the per-tenant databases); several clusters each host their own restored copy of the **same single** Platform database, not multiple independently-authored ones. Tenant databases are many, but they reference Platform content by binding and never hold promoted copies of it.

3. **Restore already delivers the outcome promotion would.** Because every environment is a fresh restore of the one authoritative database, an authentic database — including all curated content — is reproduced in full by the backup/restore custody established in W1. The narrow case promotion is for — incrementally updating curated content into a second, already-live Platform database — is not on the roadmap.

The promotion machinery (canonical export, reconcile, the release manifest, and reference resolution) remains built, tested, and available. It is **parked, not removed**: if a future need to update curated content into an already-live database arises, the mechanism exists and applies to whatever content presents a real-world natural key at that time, without re-shaping upstream composition.

## Consequences

1. For a new environment, `build == dump == live` for curated content is satisfied by whole-database restore of the single Platform database; the parity proof of the vocabulary export — the one promotable collection — stands as the worked example of the promotion path.
2. The remaining W3 collections named in DEC-018138 are reproduced by restore, not promotion; no schema-composition changes are made to force them into the promotion shape.
3. DEC-20d545's illustrative premise that the metric-directory family carries a real-world key (function, subfunction, theme) does not match the enforced schema, where the family is anchored on a generated identifier and its human identity is version-borne and not uniquely constrained. This disposition supersedes the expectation that the metric directory would be promoted, without altering the machinery DEC-20d545 specified, which is correct and merged.
4. No production or live-promotion action is taken or authorized here.

## Not decided here

- Whether a future product need — keeping a second, already-live Platform database's curated content in step with the system of record — re-opens a specific collection. That would be its own decision, gated on such a need actually existing and on the target content presenting a real-world natural key without re-shaping upstream composition.
