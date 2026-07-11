---
uid: DEC-195bbd
title: "Human-readable 4-character metric UID for MCF metric contracts"
description: "Add an opaque, immutable, 4-char Crockford base-32 metric_uid to mcf.metric_contract as the human-facing metric identifier, alongside the metric_contract_uid UUID key and the mc_name slug."
status: decided
date: 2026-07-10T07:40:14.023Z
project: bc-core
domain: metrics
subdomain: metrics/metric-identity
focus: schema
---

# Human-readable 4-character metric UID for MCF metric contracts

## Context

The live MCF metric stack identifies metrics only by a raw gen_random_uuid() (`metric_contract_uid`) plus a long descriptive slug (`mc_name`); there is no short, speakable, transcription-safe handle for operators, docs, or UI. The legacy `metric.metric_definition.metric_seq → MT-{seq}` scheme is dead (0 rows) and, being a monotonic serial, would leak catalog size/order (Invariant II) — so it is not revived. A 4-char code over a 10-12k catalog has ample room (32^4 ≈ 1.05M, ~87x headroom) but a small enough space that random assignment collides (~69 expected collided pairs at 12k), mandating a UNIQUE + bounded-retry allocator. Crockford base-32 drops the four transcription-ambiguous letters (I L O U), which is exactly what a human-readable id needs. Keeping the UUID as the sole internal reference and treating `metric_uid` purely as a display label preserves Invariants III (immutable, no reuse) and IV (references stay explicit/UUID). Naming follows DEC-69f09e: an opaque per-row unique surrogate is a `_uid`, not a `_code` (which is reserved for controlled business vocabularies), so the column is `metric_uid`. No tenant scoping: MCF metric contracts are platform-scoped and authored once; tenant specificity lives in the binding layer.

## Decision

Introduce `metric_uid` — an opaque, immutable, globally-unique 4-character human-readable short UID — as the human-facing identifier of an MCF metric contract (`mcf.metric_contract`), alongside (never replacing) the `metric_contract_uid` UUID key and the descriptive `mc_name` slug.

NAMING. Per DEC-69f09e (ISO 11179-5) the representation term `_uid` = "human-readable short UID" (as with `session_uid`, `member_uid`), and `_code` = "business code / controlled vocabulary" (as with `status_code`, `currency_code`). The value is an opaque unique surrogate, not an enumerated vocabulary, so the conforming term is `_uid`, not `_code`. `metric_code` is explicitly rejected.

FORMAT. Alphabet = Crockford base-32 `0123456789ABCDEFGHJKMNPQRSTVWXYZ` (omits I L O U). Exactly 4 chars; regex `^[0-9A-HJKMNP-TV-Z]{4}$`. Stored canonical uppercase; matched case-insensitively. Stored value is BARE 4 characters, no embedded prefix (a deliberate departure from the prefixed `_uid` value convention of SES-/MDM-/TSK-); UI MAY render a display prefix (e.g. `M·A00B`) but the column value remains `A00B`. Capacity = 32^4 = 1,048,576 codes (~87x the 10-12k target; comfortable operating ceiling ~105,000 at 10% fill).

ALLOCATION. Random (CSPRNG), not sequential — mapped into the 32-symbol alphabet and inserted under a UNIQUE constraint; on unique-violation, retry with a fresh draw bounded to N=8 attempts (at 12k fill the per-draw collision rate is ~1.1%, so 8 attempts fail with probability <1e-15). Mirrors the existing MDM-/DEC- allocator convention (random short id + unique index), NOT the retired legacy `metric_seq serial`. Assigned once, at metric-contract creation, inside `insertParentMc` (`mcf-cert-writer.service.ts`) in the same transaction as the `metric_contract` INSERT. Grain = per metric contract (per KPI), not per version: all MCVs under one MC share the parent's `metric_uid`; a genuinely new MC gets a new `metric_uid`.

IMMUTABILITY & ROLE. `metric_uid` is a LABEL, never a reference — all internal joins, FKs, cert subjects, bindings, and fact-table names continue to key on `metric_contract_uid`; `metric_uid` is never used as a foreign key (Invariant IV). Once assigned it is never mutated and never reused, including after archival, so an old value never re-points (Invariant III).

FOUNDATION GATE. Repair location E (storage/projection) — an added immutable attribute on the identity-bearing MC row — with the allocator in D (metric-draft writer). Why this location: an opaque display identifier of MC identity belongs on `mcf.metric_contract`, minted at insert. Why not A/B: the uid carries no measurement meaning, declares nothing in contract grammar, touches no source, and MUST NOT live in MC/CC grammar. Why not lower: this is the lowest identity-storage layer for a metric. Invariant check: I n/a (opaque); II satisfied (random → no order leak, unlike a serial); III satisfied (write-once, no reuse); IV satisfied (label only, never an FK); V n/a; VI satisfied (uid stored at mint, not inferred). No invariant violated.

DBCP (requires explicit operator approval before execution — not yet applied). 1) `ALTER TABLE mcf.metric_contract ADD COLUMN metric_uid text` (18→19 cols, ≤20 per D162 Rule 6). 2) `CHECK (metric_uid ~ '^[0-9A-HJKMNP-TV-Z]{4}$')`; `CREATE UNIQUE INDEX uq_mcf_mc_metric_uid ON mcf.metric_contract(metric_uid)` (global unique — not partial — so archived values are never reissued); NOT NULL added only AFTER backfill. 3) Add `allocateMetricUid(tx)` in `mcf-cert-writer.service.ts`, called from `insertParentMc`, bounded-retry on unique-violation. 4) One-time governed backfill assigns uids to the 149 active MCs (and archived rows, to lock uniqueness) via the same allocator, then SET NOT NULL. 5) Expose `metric_uid` in `mcf-read.service`, chain-status/summary payloads, and metric-directory realized views (joins stay on `metric_contract_uid`; uid is display-only).

CONSEQUENCES. Every metric gains a short, speakable, transcription-safe id; docs/UI reference `A00B` instead of a UUID or long slug. `metric_contract_uid` remains the sole internal reference key — no join/FK migration. A bounded-retry allocator + unique index are mandatory (4-char space → real birthday collisions: ~69 expected collided pairs across 12k without a uniqueness guard). Adds one column + one backfill; no change to MCV, bindings, or fact tables.
