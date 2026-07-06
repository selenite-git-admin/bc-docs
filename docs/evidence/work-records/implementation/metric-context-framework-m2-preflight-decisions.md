---
uid: metric-context-framework-m2-preflight-decisions
title: Metric Context Framework (MCF) — M2 Preflight Decisions (P1 Legacy MC marker + P2 Provenance reference field)
description: Tiny M2 preflight packet. Locks two small design choices before opening Gate M2 (Identity Substrate DBCP) of the MCF build plan. P1 — how to mark the legacy SQL contract.metric_contract* corpus as historical / pre-MCF. P2 — whether mcf.metric_contract carries an optional source/provenance reference field, and what shape it should have. Both decisions are operator-owned recommendations; this note does not create authority. Not a DBCP and not implementation.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: m2-preflight
---

# Metric Context Framework (MCF) — M2 Preflight Decisions

## 1. Scope and grounding

### 1.1 Purpose

The MCF foundational ADR DEC-c3e57f / D422 is decided (commit `155ed4f` on bc-docs-v3 main). The recommended next gate per `metric-context-framework-build-plan.md` (commit `40a9adc`) is **Gate M2 — Identity substrate DBCP**.

Two small design choices should be locked before M2 DBCP authoring begins, so the substrate design has unambiguous answers to:

- **P1** — How is the legacy SQL `contract.metric_contract*` corpus marked as historical / pre-MCF? (D422 Decision 2 says it is historical-only; what is the surface-level marker?)
- **P2** — Does `mcf.metric_contract` carry an optional source/provenance reference field, and if so, what shape? (D422 Decision 2 mentioned an "optional `provenance.legacy_mc_uid` reference field"; this preflight tightens that proposal.)

Neither decision changes the D422 authority model. Both are substrate-shape decisions that affect M2 DBCP scope and downstream consumer-read patterns.

### 1.2 Grounding

| Source | Commit / status | Relevance |
|---|---|---|
| Foundational MCF ADR DEC-c3e57f / D422 | `155ed4f` | Decision 2 sets the historical-only stance; Decision 10 guardrail 7 forbids SQL MC corpus migration |
| MCF build plan | `40a9adc` | Gate M2 substrate scope |
| MCF gap survey | `0ba202b` | Q1 disposition mechanics (Option C narrow-scope); §6.1 naming-collision analysis |
| Reservoir / authority addendum | `0e3644b` | 5-class classification + 7 guardrails (esp. guardrail 6 — reservoir provenance recorded on panel-run) |
| M0 packet | `5cd72c6` + `6ce9451` correction | §9 operator decisions list (item 1 = retirement marker, item 3 = optional `provenance.legacy_mc_uid`) |

### 1.3 What this is not

- Not a DBCP. Substrate column lists, indexes, constraints, triggers, migrations are M2 DBCP scope.
- Not implementation. No code or schema change.
- Not authority-creating. Recommendations require operator accept; ADR amendment (if any) happens through DEC-c3e57f errata.

---

## 2. Decision P1 — Legacy SQL MC corpus marker

### 2.1 Question

D422 Decision 2 locks the legacy SQL `contract.metric_contract*` corpus as **historical-only / non-authoritative**. What surface-level marker, if any, signals that historical status to future readers (operators querying the DB, engineers reading the schema, automated tooling)?

### 2.2 Options

| Option | Description | Cost | Risk |
|---|---|---|---|
| **A. Docs-only stance** | Historical status lives in D422 ADR + build plan only. No DB-side marker. | Lowest — zero substrate work. | Future reader of the schema doesn't see the marker. May query `contract.metric_contract` and treat it as live. Risk of accidental misuse. |
| **B. DDL comment / schema annotation** | Future DBCP / schema docs add `COMMENT ON TABLE contract.metric_contract IS '...'` and equivalent on `contract.metric_contract_version`, `metric.metric_binding`. Comment text cites D422 and points readers to `mcf.metric_contract`. No data mutation. No column add. No constraint add. | Low — one DDL block in the M2 DBCP (or a separate small DDL); one-time. | None significant. Comments are advisory; tooling that reads `information_schema.tables` will see the historical marker. |
| **C. Data mutation marker** | Add a `is_historical` column, or update existing rows with a status flag, or add a constraint that blocks new inserts. | Medium-High — touches historical corpus; violates D422 Decision 2's "no migration" stance in spirit (no row-level mutation of legacy data); adds new column to existing table. | Touches the historical corpus the operator explicitly chose to leave alone. Violates the narrow-scope spirit of Q1 Option C. |

### 2.3 Recommendation

**Prefer Option B (DDL comment / schema annotation).** It is enough to prevent misuse, avoids touching the historical corpus row-data, and aligns with D422 Decision 2's no-migration stance.

Proposed comment content (template for M2 DBCP, paste-and-edit):

```sql
COMMENT ON TABLE contract.metric_contract IS
  'HISTORICAL / PRE-MCF — non-authoritative per ADR DEC-c3e57f (D422) Decision 2. '
  'Future MCF metric contracts live in mcf.metric_contract. This table remains '
  'queryable for historical reference. No new rows expected. 778 of 780 rows '
  'archived as of 2026-05-26.';

COMMENT ON TABLE contract.metric_contract_version IS
  'HISTORICAL / PRE-MCF — non-authoritative per ADR DEC-c3e57f (D422) Decision 2. '
  'Future MCF versions live in mcf.metric_contract_version. This table remains '
  'queryable for historical reference.';

COMMENT ON TABLE metric.metric_binding IS
  'HISTORICAL / PRE-MCF — non-authoritative per ADR DEC-c3e57f (D422) Decision 2. '
  'Future MCF variable-grain bindings live in mcf.metric_variable_binding (which '
  'is variable-grain, not CC-grain). This table remains queryable for historical '
  'reference.';
```

The same comment block goes into `bc-core/docker/redesign/*.sql` (the authoritative DDL source per CLAUDE.md) at M2 DBCP time, and is reflected in any schema reference documentation (`bc-docs-v3/docs/data-dictionary/`).

### 2.4 Operator decision needed before M2

**Yes — recommend accept Option B.**

Sub-decisions:
- Confirm Option B as the chosen path (vs A or C).
- Confirm proposed comment text or revise.
- Confirm scope: 3 tables (metric_contract + metric_contract_version + metric_binding) or also include adjacent tables (metric_contract_approval which has 0 rows; metric_formula which is the text storage)?

Build plan M2 cannot land DDL comments without this decision.

---

## 3. Decision P2 — Source/provenance reference on `mcf.metric_contract`

### 3.1 Question

D422 Decision 2 mentions "an optional `provenance.legacy_mc_uid` reference field on the new MCF MC for operator orientation". Should `mcf.metric_contract` carry this field? If yes, what shape — narrow (`legacy_mc_uid` only) or generalized to cover all candidate-source classes (seed, KPI catalog, operator-direct, legacy)?

The generalization question matters because addendum guardrail 6 records reservoir provenance on `mcf.metric_authoring_panel_run` (the panel-run substrate). The question here is whether the MC row itself also carries a pointer back to its triggering candidate.

### 3.2 Options

| Option | Description | Cost | Risk |
|---|---|---|---|
| **A. No source-reference field** | Source/provenance lives on `mcf.metric_authoring_panel_run` only (per addendum guardrail 6); the MC row itself is provenance-free. Operator joins MC → panel-run → reservoir info if needed. | Lowest — zero substrate addition. | Operator orientation requires a join. UI must traverse the panel-run table for every MC to surface its triggering candidate. |
| **B. Narrow `legacy_mc_uid`** | One nullable column on `mcf.metric_contract` that holds the UID of a legacy MC if this MCF MC was re-authored from a non-archived legacy MC (per D422 Decision 2 — the 2 non-archived MCs). | Low — one nullable column; one type. | Only covers the legacy-MC re-authoring path. Other candidate sources (seed metric, KPI catalog, operator-direct) still require the join. Asymmetric. |
| **C. Generalized `candidate_source_ref_json`** | One nullable jsonb column on `mcf.metric_contract` covering all candidate-source classes: seed_metric, metric_definition, operator_direct, legacy_metric_contract, other. Non-authoritative orientation only. | Low — one nullable jsonb column with documented shape; CHECK constraint or doc note that it is non-authoritative. | jsonb storage for what could be relational. But MCF requirements §5 (KPI catalog carve-out) already treats reservoir provenance as background context; jsonb is appropriate for a non-authoritative orientation field. |

### 3.3 Recommendation

**Prefer Option C (generalized `candidate_source_ref_json`).** Reasons:

- **Symmetric across reservoir classes.** D422 Decision 3 lists 3 reservoirs (seed_metric, metric_definition, operator_direct) plus the legacy-MC re-authoring path from Decision 2. A narrow `legacy_mc_uid` field handles only one of those four; a generalized jsonb handles all.
- **Orientation utility for every MC, not just legacy-derived MCs.** Every MCF MC has a triggering candidate (per D422 Decision 6 — candidate intent is the trigger). Putting a pointer on the MC row lets operator surfaces show "this MCF MC was triggered by seed_metric `tax_compliance_rate`" without a join.
- **Non-authoritative discipline preserved.** The field is jsonb (deliberately not constrained as a typed reference); operator and tooling read it as orientation, not authority. The authority chain is unchanged (panel-run records full panel proof; PE-MC-1 cites grounding; verifier results record execution proof).
- **Aligns with addendum guardrail 6.** Guardrail 6 records reservoir provenance on `mcf.metric_authoring_panel_run`. Carrying the same reference on the MC row is a forward index; the panel-run is the audit-grade record.

### 3.4 Proposed shape

```json
{
  "source_type": "seed_metric" | "metric_definition" | "operator_direct" | "legacy_metric_contract" | "other",
  "source_id": "...",          // reservoir-specific id (Mongo _id, metric_definition_id uuid, operator-submission uid, legacy mc_uid)
  "source_label": "...",       // human-readable label for operator UI (e.g. "tax_compliance_rate" / "Mc — Revenue Collection Rate")
  "source_hash": "sha256:...", // hash of the candidate's intent content at trigger time (for drift detection — orientation only)
  "notes": "optional"          // free-form operator-attached note at trigger time; mirrors operator-context-hash discipline
}
```

### 3.5 Discipline constraints

The `candidate_source_ref_json` field MUST be all of:

- **Nullable.** Operator-direct submissions without a reservoir entry may have null source_ref. The field is not load-bearing for any gate.
- **Non-authoritative.** Documented in the column comment / MCF substrate ADR errata: "Orientation field; never authoritative; never part of identity tuple; never part of `package_signature_hash`; never used as PE-MC-1 grounding citation."
- **Not part of `mcf.metric_contract` identity tuple** per MCF requirements §4.2. The identity tuple covers formula intent + bindings + grain + filters + temporal; provenance is metadata, not identity.
- **Not a migration bridge.** Even when `source_type = 'legacy_metric_contract'`, the field is orientation only; no automated code path reads this field to import legacy data.

### 3.6 Operator decision needed before M2

**Yes — recommend accept Option C with the proposed shape.**

Sub-decisions:
- Confirm Option C (vs A or B).
- Confirm the proposed jsonb shape and `source_type` enum values.
- Confirm field name (`candidate_source_ref_json` — matches D162 jsonb naming convention `*_json`).
- Optional: confirm whether a CHECK constraint enforces the closed `source_type` enum, or whether the discipline is documentation-only.

Build plan M2 cannot finalize the `mcf.metric_contract` column list without this decision.

---

## 4. M2 implications

### 4.1 If P1 = B accepted

M2 DBCP includes a small DDL block of `COMMENT ON TABLE contract.metric_contract / metric_contract_version / metric_binding` statements (and optionally adjacent legacy tables) per §2.3. The comment text references D422 and points readers to the `mcf.*` equivalents.

This does not change D422 authority model. It is a surface-marker addition only.

### 4.2 If P2 = C accepted

M2 substrate adds `candidate_source_ref_json jsonb NULL` to `mcf.metric_contract`. Documentation (column comment + MCF substrate DBCP scope) records:

- Non-authoritative orientation field.
- Not part of identity tuple (MCF §4.2) or `package_signature_hash` (MCF §8.7).
- Not citable as PE-MC-1 grounding (per D422 Decision 3).
- Closed-enum `source_type` values: `seed_metric`, `metric_definition`, `operator_direct`, `legacy_metric_contract`, `other`. Enforced via CHECK constraint or documentation-only per operator sub-decision.

This does not change D422 authority model. It is a metadata-column addition only.

### 4.3 Neither decision affects

- D422 Decision 1 (framework scope) — unchanged.
- D422 Decision 3 (reservoirs vs authority) — unchanged. The new field is orientation, not authority.
- D422 Decision 5 (formula authority discipline) — unchanged.
- D422 Decision 6 (workbench framing + tool surface) — unchanged.
- D422 Decision 7 (layered activation gates) — unchanged.
- D422 Decision 10 (seven guardrails) — unchanged. Guardrail 6 (reservoir provenance recorded) is reinforced, not modified.
- MCF requirements §4.2 identity tuple — unchanged.
- MCF requirements §8.7 `package_signature_hash` composition — unchanged.

### 4.4 Build plan M2 scope after P1 + P2

M2 substrate, post P1 + P2, ships:

- `mcf` schema creation.
- `mcf.metric_contract` with identity-tuple UNIQUE per MCF §4.2, **plus** `candidate_source_ref_json jsonb NULL` per P2.
- `mcf.metric_contract_version` (no provenance column; version-level provenance lives on the version's `mcf.metric_authoring_panel_run` reference).
- `mcf.metric_variable_binding`, `mcf.metric_filter_clause`, `mcf.metric_computed_dimension_ref`.
- Immutability triggers on identity-bearing columns when `lifecycle_state='active'`.
- DDL `COMMENT ON TABLE` block for the three legacy SQL MC tables per P1.

Everything else in M2 scope per build plan §4.2 is unchanged.

---

## 5. Recommended next gate

### 5.1 If operator accepts P1 = B and P2 = C

**Open Gate M2 — Identity substrate DBCP.** The DBCP scope is unambiguous; M2 authoring can proceed mechanically against MCF requirements §17.1 + this preflight's P1/P2 additions.

Sub-decisions during M2:
- M0 §9 item 1 (legacy retirement marker) is satisfied by P1 = B.
- M0 §9 item 3 (optional `provenance.legacy_mc_uid`) is replaced by the generalized P2 = C (which subsumes the legacy-MC reference as one `source_type` value).

### 5.2 If operator revises P1 or P2

Re-issue this preflight with revisions; do not open M2 until accepted.

### 5.3 If operator defers

Each deferred decision blocks M2:
- P1 deferred → M2 still ships substrate but no legacy table marker; recommend follow-on small DBCP for comments.
- P2 deferred → M2 substrate ships `mcf.metric_contract` without `candidate_source_ref_json`; operator can add later via additive migration, but M2's column list is incomplete at first ship.

Recommend accepting both before M2 opens, since neither decision creates risk and both are operationally trivial.

---

## Document verification

- **All 5 sections present** (§1 Scope and grounding, §2 P1, §3 P2, §4 M2 implications, §5 Recommended next gate).
- **No recommendation is written as already-authoritative.** P1 and P2 carry explicit "OPERATOR DECISION REQUIRED" markers (§2.4 and §3.6).
- **No code/DB/schema files changed.** Single doc commit.
