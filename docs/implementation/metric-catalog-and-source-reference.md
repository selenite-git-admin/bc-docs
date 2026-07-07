---
id: metric-catalog-and-source-reference
order: 24
title: "Metric Catalog, Chain-on-Demand & the Source-Reference Layer"
status: drafting
authority: authoritative
depends_on: [architecture, data-model-and-schema, business-concept-registry, synthetic-data-and-testing]
governing_sources:
  - DEC-c3e57f (D422) MCF foundational
  - DEC-2b... D475 entitlement-driven binding
  - DEC-a6cdae (D498) chain-readiness vs data-readiness split
  - DEC-542722 (D499) catalog-first authoring
  - DEC-ddc13e (D500) concept↔source soft-reference layer
---

# Metric Catalog, Chain-on-Demand & the Source-Reference Layer

This chapter records how metric authoring, the contract chain, and synthetic
data relate — the operating shape settled 2026-07-07 (ADRs D498–D500), which
lifted the metric program off a structural saturation cap and made the contract
chain and SDG **generated on demand** rather than hand-authored per metric.

## 1. The three tiers (D498 + D499)

A metric contract (MC) moves through three tiers. Reporting must never conflate
them; the machine-readable rollup is `GET /api/mcf/metric-contracts/catalog-status`.

| Tier | State | Meaning | Gate to reach it |
|---|---|---|---|
| **catalog-defined** | draft MCV | Defined + panel-approved + deduped + fixture-verified, bound to BCF concepts. **Chain-independent.** | materialization (M12.5) |
| **chain-ready** | active MCV | The declared SC/AC/OC/CC spine for its concepts resolves. | PE-MC (esp. **PE-MC-11**, the sole chain gate) |
| **runtime-live** | active + data-backed | Produces payload-verified values on a tenant. | the data program (§4) + payload cross-check |

**Catalog-first (D499):** author freely to *catalog-defined*, bounded only by BCF
vocabulary + panel cost — not by the existing chain. Promote to *chain-ready* on
demand (a customer entitlement), when the chain is built via the D475
reverse-walk. The catalog leads; the chain follows.

**Proof the tiers are real:** a metric materialised to draft on a grain with zero
canonical contracts (Customer Invoice Line Item); PE-MC returned all-PASS except
PE-MC-11 = REJECT. So everything through materialize is chain-independent;
**PE-MC-11 is the only coupling, and it fires only at draft→active.**

Foundation note: the six invariants govern *evaluation*, not catalog definition.
A draft produces no meaning; it is inert until evaluated through the boundary.

## 2. Why chain-on-demand is sound

Contracts are **demand-derivable from metrics** — the D475 `onboard-metric`
reverse-walk builds CC/SC bindings from an entitled MC. Metrics are **not**
derivable from contracts. So the metric catalog is the leading indicator and the
chain is trailing, demand-pulled fulfilment. Gating authoring on the existing
chain caps the corpus at what the live slices already project; catalog-first
removes that cap.

## 3. The source-reference layer (D500)

`concept_registry.concept_source_reference` — a **soft, advisory, design-time**
bridge from a BCF `business_concept` to a physical field in the onboarded source
catalog (`source.source_field`).

```
business_concept_id → FK concept_registry.business_concept   (source-agnostic)
source_field_id     → FK source.source_field                 (encodes system/table/field)
transform_hint      single-field only ('direct' | 'code_lookup:<map>')
rank                precedence among genuine same-concept alternatives
is_advisory         CHECK true — evaluation never reads it
```

It is the single seed a generator reads to emit **(a)** the SDG field-emission
profile, **(b)** draft OC field_mappings, **(c)** SC/AC declarations — collapsing
"hand-tune SDG per field + hand-author every contract" into "declare the profile
once, generate."

**Three invariants keep it clean:**

1. **Evaluation never reads it.** The governed OC field_mapping hard-bind remains
   the sole authority at the evaluation boundary (Invariant IV / source-agnosticism).
   This layer is compiled *into* hard artifacts, never consumed at runtime.
2. **FK-to-catalog robustness.** `source_field_id` FKs the onboarded catalog, so a
   hint cannot point at an un-onboarded field. A new source (e.g. Oracle) must be
   catalogued (`source_system→version→module→object→field`) — the **same** catalog
   SC/AC bind against — before it can be referenced. SDG, SC, AC, OC and this layer
   therefore share one source-of-truth.
3. **Strictly 1:concept ↔ 1:field (+ rank).** Multi-field concepts are NOT modelled
   here. A signed amount = `amount` BC + `debit_credit_code` BC; net = gross − tax;
   amount + currency — each an atomic 1:1 concept, **composed by the CC derivation
   grammar** (`derivations[].inputs[].role`: `subtract`, `date_diff`, …) which
   already owns roles. Re-encoding composition here would duplicate that governed
   vocabulary — the exact drift this layer exists to prevent. `transform_hint` is
   single-field only; a genuine unmodellable composition is fixed by **extending the
   derivation grammar**, never by string-hacking the soft-ref. (Red-teamed; D500.)

**Generator:** `barecount-devhub/.claude/tools/mcf-softref/generate.mjs` resolves
the concept↔field relation and emits `sdg-field-profile.json` + a FK-resolved
`concept-source-reference.seed.json` + coverage. First run: 73 active OC
field-mappings across 39 concepts, **100% resolve** to a catalog field_id; v2
collapses the version fan-out to a canonical field_id per (concept, table, field)
→ 42 clean seed rows across BSAD/BSAK/KURGV/RBKP/TYPE_SD_S_MAP.

## 4. The data program (D498) — making chain-ready metrics runtime-live

Data-readiness is a **separate program** from chain-readiness. It is SDG
table-level work plus **one bulk verification campaign per SDG drop** (identity
checks — gross = net + tax, partition sums — not per-metric hand-recompute).

The 2026-07-07 SDG audit reframed the work into four buckets:

- **REGEN** (cheap): FX divergence (built, opt-in/off) + cash discount (built,
  default-on) — pilot1 is a stale pre-discount, FX-masked dataset; regenerate it.
- **ONBOARD**: open items (BSID/BSIK) — the generator *emits* them; pilot1 never
  ingested them. Needs the BSID/BSIK SC/AC/OC/CC + the as-of runtime capability
  (CB-007). Largest tranche: aging, DSO, balances, within-terms-by-balance.
- **BUILD**: dispute + write-off lifecycle states (not built) + two SDG bugs
  (dunning updates dropped; partial payments never resolve).
- **CHAIN**: SHKZG sign projection at the canonical layer.

Perf is **not** the bottleneck (already solved: 1.6M rows/min, O(n) open-item
index). Realism + plumbing generation is.

## 5. The compounding effect

Catalog-first (define against BCF) + soft-ref (generate the plumbing) + data
program (make it real) compound: catalogue metrics broadly against the concept
vocabulary; when demand pulls one, **generate** its chain from the soft-ref
profile instead of authoring it; the data program lights up whole families per
SDG drop. The metric count is bounded by BCF vocabulary and panel cost, no longer
by the two live slices' projections.
