---
title: ARPI Metric Contract rebind — read-only proposal
status: locked-pending-dbcp
date: 2026-06-08
project: bc-core
domain: implementation
governs: DEC-c3e57f (D422 MCF) · DEC-a6258b (D430 canonical identity) · DEC-4a17e0 (D431 observation O↔C)
depends_on: active OC-v2 oc__customer_invoice_arpi_slice_type_sd_s_map · active CC-v2 cc__customer_invoice_arpi_slice
---

# ARPI Metric Contract rebind — read-only proposal

**Proposal only. No MC authored/activated. No DB writes.** Locked by operator 2026-06-08 (§Locked
decisions). The **O-1 condition triggered — no existing governed service path** — so a **mini-DBCP is
required** before any rebind. No execution; no direct `mcf.*` writes.

## Grounding (live, read-only — 2026-06-08)

**ARPI metric = `average_revenue_per_invoice`** (MCF substrate `mcf.*`), grain entity `e3963e45`
(Customer Invoice). Three contract instances exist; one is active:

| mc_uid | MCV uid | version | governance |
|---|---|---|---|
| `49cdde1a` | **`8c088f55`** | v1 | **active** |
| `196b4c8a` | `b2c5c028` | v1 | draft |
| `7528f9c9` | `5e7cce21` | v1 | draft |

**Active MCV `8c088f55` formula AST:** `divide( sum(numerator_source), count_distinct(denominator_key) )`.

**Active MCV `8c088f55` variable bindings (all bound to SUPERSEDED concepts):**

| variable_role | bound concept | live state | active successor (same RT + grain) |
|---|---|---|---|
| `numerator_source` | `a42d3fc0` (amount, snapshot unit=**USD**/decimal) | **superseded** | `1a2ac2f2` amount/**null**/decimal — **active** |
| `denominator_key` | `095afe86` (identifier) | **superseded** | `51482979` identifier/null/string — **active** |
| `temporal_anchor` | `d05f24b3` (date) | **superseded** | `61e19048` date/null/date — **active** |

The active successors are exactly the anchors the just-activated OC-v2 + CC-v2 declare. (Lineage is
confirmable in `concept_registry.business_concept_supersession`; the rebind target is determined by the
**active CC-v2**, the authority for "what concept is canonical on this grain now".) The two draft MCVs
bind the same superseded concepts.

## 1. New governed MC version, or new MC contract?
**A new governed MC *version*** (supersession), **not** a new contract. The metric identity is unchanged —
name `average_revenue_per_invoice`, grain `e3963e45`, formula intent `divide(sum/count_distinct)`. Only the
variable→concept bindings change. Per Invariant III (immutability) the active `8c088f55` is frozen; the new
MCV is authored and supersedes it via `mcf.metric_supersession`. Same metric, new version.

## 2. Which variables need rebinding?
**All three**, each from its superseded anchor to the active successor:
- `numerator_source`: `a42d3fc0` → **`1a2ac2f2`** (amount)
- `denominator_key`: `095afe86` → **`51482979`** (identifier)
- `temporal_anchor`: `d05f24b3` → **`61e19048`** (date)

## 3. Does the MC reference CC-v2 by id/version, or only bind to BCF concept ids?
**Only binds variables to BCF concept ids — never references the CC-v2 (or OC-v2) by contract id/version.**
This is the D430/D431 concept-identity principle: each binding carries a `bound_business_concept_id`. At
resolution, `CanonicalConceptResolverService.resolve(grainEntityId, businessConceptId)` matches the active
canonical-v2 contract that declares the **same** concept_id on the grain (pure A1, no lineage, no contract
reference). So the MC binds `1a2ac2f2/51482979/61e19048`; the resolver dynamically resolves to whatever
active CC-v2 declares them (today `cc__customer_invoice_arpi_slice`). This is the source-agnostic,
supersession-resilient decoupling — and it is *why* the rebind is to **concepts**, not to the new CC.

## 4. Exact MC body changes
The new MCV is byte-identical to `8c088f55` **except** the three `metric_variable_binding` rows:
- `bound_business_concept_id`: `a42d3fc0→1a2ac2f2`, `095afe86→51482979`, `d05f24b3→61e19048`.
- Frozen snapshots refreshed to the **live** successor triples (D430/D431 snapshot == live concept):
  - numerator: representation_term `amount`, **unit `null`** (drops the stale `USD`), data_type `decimal`
  - denominator: `identifier` / null / `string`
  - temporal: `date` / null / `date`
- Unchanged: formula AST, grain entity `e3963e45`, temporal-gate shape, filter set, role kinds.
- Recomputed: `variable_binding_set_hash`, `identity_tuple_hash` (derived from the new bindings).

## 5. Gates on authoring/activation
- **Bind-time check** (M4 / `metric_variable_binding.bind_time_check_results_json`): each bound concept must
  be **active** — the current superseded bindings would fail; the rebound active concepts pass. This is the
  gate that makes the rebind necessary and provable.
- **Canonical resolver gate (D430 CS-3):** `resolve(e3963e45, concept)` must return an active CC-v2 field for
  each of the 3 concepts → satisfied by `cc__customer_invoice_arpi_slice`.
- **O↔C (D431):** each concept observable via active OC-v2 → already satisfied at CC activation.
- **MCF lifecycle gates:** M13 PE-MC publication-eligibility (`metric_publication_eligibility_result`),
  M14 publication, governance state machine, supersession of `8c088f55`.
- **Platform gates:** D305 ChainStatus completeness (L1–L7), D366 L-node semantic verdict, MLS-14 activation.

## 6. Proof that O→C→M is complete
A **static (read-only) resolution trace** — no runtime evaluation:
- **M→C:** `resolve(e3963e45, 1a2ac2f2/51482979/61e19048)` each returns the active CC-v2 field
  (amount / document_number / document_date) — non-null for all 3.
- **C→O:** the D431 O↔C check holds — each CC concept is declared observable by the active OC-v2.
- **Therefore O→C→M:** OC-v2 (observable) → CC-v2 (canonical) → MC (variable bound) for all three concepts,
  mediated purely by concept_id. Proof artifact = the resolver returning the active CC-v2 for all 3 + the
  D305 chain_status for the MC reading complete. No `metric_snapshot`, no fact rows.

## 7. Out of scope (explicit)
- No MCF materialization (M12.5) of runtime substrate · no runtime evaluation / fact writes ·
  no `metric_snapshot` / `contract.*` runtime materialization · no extra OC/CC changes.
- The rebind is confined to the metric-contract layer (variable bindings + new governed MCV).

## Locked decisions (operator, 2026-06-08)

**O-1 — path: lighter governed MCV-rebind / new-version, NOT a fresh M12 panel cycle.** Rationale:
formula, grain, and metric identity are unchanged — a semantic binding refresh from superseded BCF anchors
to active successors, not a new metric-authoring problem.

**O-1 condition RESULT — NO existing governed service path → mini-DBCP required. Stop; do not execute; do
not direct-write `mcf.*`.** Evidence (read-only, main @ `b0f0399`):
- `MetricAuthoringMaterializationService.runMaterialization(panelRunUid)` is the only path that creates a
  new MCV + bindings — it is **panel-coupled** (reads the proposal `WHERE panel_run_uid=`) and sets
  **`supersedesVersionUid: null`** (never supersedes). Using it = a fresh M12 panel cycle (O-1a), rejected.
- `MetricCertWriterService.supersedeMetricInTx(...)` records a supersession link but **requires a successor
  MCV to already exist** (does not create the rebound successor) and requires predecessor/successor on
  different parent MCs.
- `POST mcf/metric-contract-versions/:mcvUid/activate` only **activates an existing draft** — no create/rebind.
- The billing_volume "rebind" (PR #222) was a **candidate-retry via fresh panel** (intake unlock → M12) —
  a full cycle, not a no-panel binding refresh.
- ⇒ No governed service creates a new MCV with refreshed bindings **without** a panel **and** supersedes the
  active predecessor.

**O-2 — supersession: the new MCV supersedes active `8c088f55`** so exactly one ARPI MCV is active after
publication. (The rebind mints a new parent MC uid for the successor, satisfying the
predecessor/successor-different-parent rule, superseding `49cdde1a / 8c088f55`.)

**Locked bindings** (numerator `a42d3fc0→1a2ac2f2` amount/null/decimal; denominator `095afe86→51482979`
identifier/null/string; temporal `d05f24b3→61e19048` date/null/date) and constraints (MC binds only BCF
concept ids; no OC/CC contract-id reference; D430 resolves each to the active CC-v2 field; D431 O↔C holds;
predecessor immutable; no MCF materialization / runtime eval / `contract.*` materialization / snapshot/fact
writes). Proof target = **static O→C→M identity trace only**.

## Required mini-DBCP — governed "MCV binding-refresh / rebind" service (zero DDL)
The substrate exists (`mcf.metric_contract[_version]`, `metric_variable_binding`, `metric_supersession`,
`certification_record`); only a no-panel binding-refresh entry-point composing them is missing.
- **New governed service** (`MetricMcvRebindService`, or a cert-writer entry) — input: predecessor MCV
  `8c088f55`, the three role→concept rebindings (+ live snapshots), rationale/cert. **Reuses** the
  predecessor's `formula_ast`, grain, temporal-gate, filters (identity-preserving — no panel proposal).
- **Composes existing primitives in one all-or-none tx:** writeMetricDraft-style insert (new parent MC +
  successor MCV + rebound `metric_variable_binding` rows, `supersedesVersionUid = 8c088f55`) →
  `supersedeMetricInTx` → cert. **No hand-written `mcf.*`; no DDL.**
- **Gates:** bind-time active-concept (rejects superseded), D430 resolver → active CC-v2 field, D431 O↔C,
  hash recompute (`variable_binding_set_hash`, `identity_tuple_hash`), formula-unchanged assertion,
  structural checks, M13 PE-MC, M14 publication.
- **Endpoint:** `POST /mcf/metric-contract-versions/rebind` (thin pass-through) + DTO + focused tests.
- **Proof (this step):** static O→C→M identity trace only — MC variable concept → CC-v2 field (resolver) →
  observable via active OC-v2 → chain_status/gates complete. No metric_snapshot / fact rows.
- **Shape:** code PR (zero DDL), analogous to the R3-pattern thin modules. Held for separate approval.
