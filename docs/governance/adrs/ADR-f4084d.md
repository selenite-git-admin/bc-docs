---
uid: DEC-f4084d
title: "Governed chain-authoring capability: publishChain + registerSourceStack + substrate resolver (logic in bc-core)"
description: "CONTEXT: The grounded reuse study (devhub .claude/chain-authoring-reuse-map-2026-07-10.md, SES-24769c) found that concept + SC/AC/OC/CC chain authoring has NO governed wrapper — served by ~40 historical + ~15 per-session bespoke scripts firing raw POSTs at bc-core. The 5 proven chain patterns (single-table master, multi-table join, classify-scoped field, source stack, discriminator concept) collapse to 2 primitives + a lookup layer. The repetition also carries live hazards: concept-id ALIASING (one term, 3-4 ids by entity → silent wrong-entity binding), invented grammar shapes (join_semantics travel-back), D461 both-places and strict_backward violations re-hit per session. Operator directive: logic belongs in bc-core only; devhub is a thin client (DEC-bf7842/D501).

DECISION — three bc-core capabilities, all ORCHESTRATORS over existing governed services (no new grammar, no validator bypass, no new tables):

1. **publishChain** — `POST /api/contracts/chains` {dryRun?, spec: ChainSpec}. ONE declarative ChainSpec states each fact ONCE; the service mechanically derives the OC and CC bodies and composes the EXISTING ContractService lifecycle (createContract→createVersion→submit→approve→activate→supersede-priors). ChainSpec: business_object_code + oc_name/cc_name (shells created if absent) + versions (explicit or auto-bump, supersede_prior) + sources[] ({role header|lookup, table, sc, ac, cardinality, join{on[], type, filter?, reduce?}}) + identity{fields, deduplication} + grain + fields[] (per field: canonical name, concept (UUID or {entity, term} resolved entity-scoped), source{table, field}, type, representation_term, required?, resolution rule, transform (direct|code_lookup{value_map, unmapped}), or reference{role, target_entity}) + derivations[] (verbatim CC derivation grammar) + temporal{posting_date_field, gate defaults}. DERIVED mechanically: OC field_mappings, so_schema, CC field_selection (derivation outputs auto-included — D461 both-places AUTOMATED), resolution_rules, resolved_schema (non-required new fields land as OPTIONAL properties — strict_backward satisfied by construction), the invariant header block. dryRun returns the derived OC/CC bodies WITHOUT writes. Per-step outcome report (metric_drive style); re-invocation resumes name-based (existing shell → new version). SINGLE chain per call — D268 no-bulk upheld structurally.

2. **registerSourceStack** — `POST /api/source-catalog/stacks` {dryRun?, spec: {system_version, module, table, data_pattern, fields[{name,type,length,key}], primary_key, activate}}. Registers the object if absent (D284 veracity gate applies), registers missing fields, authors SC v1 + AC v1 (the invariant 2-rule admission body, expected_field_count=N), activates both. Returns the id map.

3. **Substrate resolver** — `POST /api/registry/substrate/resolve` (read-only, batch): {entities?, concepts? [{entity, term}], characteristics?, fields? [{table, field}], contracts?, source_versions?} → ids. ENTITY-SCOPED concept resolution kills the aliasing hazard; ambiguity REFUSES with candidate list (never guesses). Used internally by publishChain and directly by sessions/tools.

SCOPE FENCES: no concept/characteristic creation (BCF surface, separate governance); no metric authoring (drive exists); no meta-schema changes; no directory writes; one chain per call.

THIN DEVHUB CLIENTS: devhub_chain_publish + devhub_source_register — pure pass-throughs, dryRun-default with confirm=true to execute (devhub_tenant_bind_metrics pattern). No rules in devhub.

G4 (same program): fold the devhub preflight live legs (mcp-server.js:2761-2931 — G4-mirror literal roles, canonicalValueSet check, 0.6 near-dup heuristic, CC runtime-projection probes) into bc-core validate-envelope; delete from devhub (completes D501). G5 (parallel-drive verification) is operational, out of ADR scope.

FOUNDATION: composition at the authoring surface — every artifact still passes the unchanged B-layer validators (meta-schema, D430, D431, strict_backward); the ChainSpec→body projection is mechanical, meaning is still declared by the author once (Invariant IV strengthened: single statement of each fact eliminates OC/CC restatement drift). Repair-location: none of A–F is altered; this is tooling over B-writes. No DB change.

BUILD PLAN (phases, each a coordinated non-panel window where bc-core code is touched): B1 substrate resolver (read-only, safe) → B2 registerSourceStack → B3 publishChain + dryRun + GOLDEN PARITY TESTS (derive the live cc__asset v2 and cc__journal_entry_line v5 bodies from specs and diff against the actual live contract_json — one-then-many built in: the capability must reproduce what was hand-proven before it authors anything new) → B4 thin devhub MCP clients → B5 G4 fold-in. Tracked under TSK-539bbe."
status: decided
date: 2026-07-10T02:16:22.309Z
project: bc-core
domain: metric-runtime
subdomain: chain-authoring
focus: authoring-surface
---

# Governed chain-authoring capability: publishChain + registerSourceStack + substrate resolver (logic in bc-core)

## Context

No rationale recorded.

## Decision

See description_text (ADR body authoritative).
