---
uid: metric-context-framework-m9-fixture-substrate-preflight
title: MCF M9 Self-Verification Fixture Substrate Preflight
description: Docs-only preflight framing the M9 self-verification fixture substrate gate, parallel-eligible with M11/M12 per build plan §M9 (depends on M2/M7/M8 only — no M5 dependency). Per MCF §12, the fixture is a structured (declared-input rowset → expected-output) artifact bound to an exact package_signature_hash that closes the gap between PE-MC well-formedness checks (which prove structural soundness) and executable correctness (proven by M10's deterministic verifier running fixtures). M9 ships the substrate side: a per-MCV mcf.metric_self_verification_fixture table holding Section A inputs + Section B expected output + Section C resolver fixture config + 4 hashes (formula_ast_hash, variable_binding_set_hash, grain_filter_temporal_dimension_signature_hash, self_verification_fixture_hash) + bound package_signature_hash; structural-check engine C-FX-1..C-FX-11 (per §12.5); stale-fixture rule enforcement (per §12.7). NO verifier execution engine (M10), no reservoir ingestion (M11), no panel implementation (M12). Recommendation: D-M9-B — single mcf-owned fixture table + service-side C-FX validation + service-side stale-fixture detection (no substrate triggers beyond the standard NF1 + format CHECKs). Optional panel_run_uid attribution column (nullable, FK to contract.panel_output_record per existing repo pattern) lets future M12 panel attribute fixture proposals without requiring M5 ingestion at M9 time. Docs-only. No bc-core edits. No DDL. No data writes. No M10/M11/M12+ gates.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m9-fixture-substrate-preflight
---

# MCF M9 Self-Verification Fixture Substrate Preflight

## 1. Scope and grounding

Frame the M9 fixture substrate gate — parallel-eligible with M11/M12 per build plan §M9 (depends on M2/M7/M8 only). Per MCF §12, the **self-verification fixture** is the executable test that closes the gap between PE-MC structural well-formedness (M7/M8 hash discipline + PE-MC-1..PE-MC-9) and execution correctness (proven by M10 verifier running fixtures). M9 ships the substrate; M10 ships the verifier service.

This is **docs-only preflight**. No DBCP. No DDL. No bc-core edits. No M10/M11/M12+ work.

### 1.1 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ read-only |
| No DDL applied or drafted | ✓ |
| No real MCF metric contracts | ✓ substrate empty post-M5 apply |
| No M10 verifier engine | ✓ — substrate only at M9 |
| No M11 ingestion / M12 panel implementation | ✓ downstream |
| No BCF data touches | ✓ |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

### 1.2 Source documents (already in context — referenced, not re-read here)

- ADR DEC-c3e57f / D422 (MCF M1 foundational)
- MCF requirements §12 (Self-Verification Fixtures — §12.1 purpose, §12.4 three-section body, §12.5 C-FX-1..C-FX-11 structural checks, §12.6 verifier behavior, §12.7 stale-fixture rule, §12.8 multi-fixture coverage, §12.9 immutability)
- MCF requirements §13 (PE-MC-10 references this substrate)
- MCF build plan §M9 (scope + T-shirt L + dependencies M2/M7/M8 + risk: structural checks not exhaustive)
- M5 closeout `7800437` (live state confirmation)
- M7/M8 closeout `6b3ffb2` (package_signature_hash + intermediate hash live)
- M4 service spec (`metric_publication_eligibility_result.satisfying_verification_result_uid` carries FK to M10's `mcf.metric_self_verification_result`, NOT M9's fixture table — see §7 boundary note)

---

## 2. Current live substrate state after M5/M7/M8

| | |
|---|---|
| bc-core main | `bb98642` (M5 evidence merged) |
| bc-docs-v3 main | `7800437` (M5 closeout) |
| `mcf.*` tables | **14 present, all 0 rows** |
| `mcf.metric_contract_version.formula_ast_canonical_json` | live (M7); placeholder default; service-side guard active |
| 6 hash columns on `mcf.metric_contract` | live (M2/M7/M8); CHECK regex `^sha256:[0-9a-f]{64}$` |
| Algorithm version | `mcf-hash-v1` (M7/M8 forever-lock) |
| M3 trigger amendment | live (3-IF) |
| M5 panel substrate | live; 4 tables empty; trigger `trg_mapt_immutability` active |
| `mcf_v1.panel_discipline` | present; algorithm/registry versions pinned at `v1` |
| BCF | untouched (10 BC + 2 entity + 24 `contract.panel_output_record` BCF rows) |

Verified empirically via bc-postgres MCP throughout the M5 arc; no re-verification needed for this preflight.

---

## 3. Why M9 is next

| Reason | Detail |
|---|---|
| **Parallel-eligible** | Per build plan §M9, depends only on M2/M7/M8 (all live). No M5/M11/M12 dependency. Can proceed without waiting for M11 ingestion or M12 panel implementation. |
| **Unblocks M10** | M10 verifier engine reads fixtures by `self_verification_fixture_hash` + executes packages by `package_signature_hash`. No fixtures → nothing to verify. |
| **Unblocks PE-MC-10** | PE-MC-10 (§13) requires "at least one passing fixture per package" — the substrate must exist for fixtures to be authored against. |
| **M11+ already needs the substrate** | When M11/M12 ship, panel-proposed fixtures need a substrate to land in. Shipping M9 in parallel lets M11/M12 land with fixture-substrate already live. |
| **Smallest substrate-only gate left** | M11 = service. M12 = service + UI. M9 = substrate (mirrors M5 pattern). Substrate gates ship faster + have cleaner verification. |

---

## 4. M9 ownership boundary

### 4.1 M9 MUST own

| # | Deliverable |
|---|---|
| 1 | `mcf.metric_self_verification_fixture` table (per-MCV; Section A/B/C body + 4 hashes + bound `package_signature_hash` + audit fields) |
| 2 | Format CHECKs on the 4 hash columns (`^sha256:[0-9a-f]{64}$` — matches existing MCF convention) |
| 3 | FK to `mcf.metric_contract_version` (intra-mcf; in Drizzle) |
| 4 | Optional `panel_run_uid` attribution column FK to `contract.panel_output_record` (cross-schema; DDL-only per repo convention) — nullable so M9 stays parallel-eligible without M5 ingestion |
| 5 | UNIQUE constraint on `(mcv_uid, self_verification_fixture_hash)` — same fixture body can't be authored twice against the same MCV |
| 6 | Indexes per query patterns (lookup-by-mcv, lookup-by-package-hash, lookup-by-active) |
| 7 | C-FX-1..C-FX-11 structural-check spec documented in the DBCP (engine implementation deferred to bc-core service alongside M9 DDL, OR to M10) |
| 8 | Stale-fixture rule per §12.7 — substrate stores bound `package_signature_hash`; service-side equality check at fixture-bind / fixture-verify time (M10 also re-checks per §12.6 step 3) |
| 9 | Fixture immutability per §12.9 — fixture is **mutable while no `pass` cited by PE-MC-10**; immutable thereafter. Two clean options: (i) all-substrate trigger gated on a `pass_cited_at` column or downstream verification result, or (ii) service-side discipline. DBCP picks one. |
| 10 | Dry-run + post-apply verifier scripts |

### 4.2 M9 MUST NOT own

| # | Out-of-scope | Belongs to |
|---|---|---|
| 1 | Verifier execution engine (read package + run AST + compare to Section B) | **M10** |
| 2 | `mcf.metric_self_verification_result` table (verification result substrate) | **M10** — note: M4 DBCP comment incorrectly attributes this to "M9"; that's a doc bug to correct in M9 DBCP / M10 DBCP |
| 3 | Activating `fk_mper_verification_result` on `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` | **M10** (target table is M10's `mcf.metric_self_verification_result`, not an M9 table) |
| 4 | Fixture proposal generation (panel work) | M12 |
| 5 | Reservoir ingestion of fixture rows | M11 |
| 6 | Minimum-fixture-coverage discipline per formula class | Open question §19.13 Q37; not in M9 scope |
| 7 | Real metric contracts / real fixtures | substrate stays empty pending M11+M12+operator runs |
| 8 | BCF data | NEVER in MCF gates |
| 9 | M5 service code (panel-side fixture proposal) | M12 |

---

## 5. Relationship to M7/M8 hash authority

M9 depends on M7/M8 because:

- **Bound package_signature_hash** — fixture-binding key per §12.7. M7/M8 computes it at `review → approved`; fixture is authored against this hash; verifier confirms equality before execution.
- **Stale-fixture rule** — any change to formula AST, bindings, filters, temporal gate, grain, or computed-dim refs changes `package_signature_hash` (per M7/M8 §11.1 composition); fixture's stored bound hash no longer matches; fixture becomes stale.
- **Fixture's 4 hashes are subsets of M7/M8 hashes** — `formula_ast_hash`, `variable_binding_set_hash`, `grain_filter_temporal_dimension_signature_hash` are all already computed by M7/M8 services. Fixture stores them as-of-authoring-time snapshots. The new hash M9 introduces is `self_verification_fixture_hash` = sha256 over canonical Section A+B+C.
- **Algorithm version coupling** — fixture hashes use the same `mcf-hash-v1` bundle marker as M7/M8 (per M7/M8 §12.4 single-bundle versioning). Any M7/M8 algorithm bump → fixture hashes recompute.

**No new hashing service needed for M9.** Reuse `FormulaCanonicalizationService` + `PackageSignatureService` from M7/M8 to produce the 3 sub-hashes; add a small helper (or extend `PackageSignatureService`) for `self_verification_fixture_hash` over Section A+B+C JCS-canonical bytes.

---

## 6. Relationship to M5 panel substrate

**M9 has NO M5 hard dependency** per build plan. But the optional `panel_run_uid` attribution column on the fixture table lets M12 attribute fixture proposals to the panel run that produced them.

| Aspect | Decision |
|---|---|
| FK target if column included | `contract.panel_output_record(panel_run_uid)` — matches existing MCF pattern (`fk_mcf_cert_panel_run`, `fk_mcr_panel_run`, etc.) |
| FK in Drizzle vs DDL-only | DDL-only (cross-schema FK per repo convention; see `metric_supersession.ts`) |
| Nullable | YES — operator-authored fixtures (no panel) carry NULL; panel-proposed fixtures carry a real uid |
| Required when authored by panel | service-side discipline at M12 (substrate doesn't enforce panel attribution; mirrors M4 NF1 panel-attestation pattern) |

**M9 ships without the column** is also viable (M9-A.1 below): defer panel attribution to a future amendment after M12 ships and the column is concretely needed. Operator picks per D-M9-3 below.

---

## 7. Relationship to M10 verifier engine

Strict separation:

| Surface | Owner | Notes |
|---|---|---|
| `mcf.metric_self_verification_fixture` (table + body + 4 hashes) | **M9** | Fixture authoring substrate |
| C-FX-1..C-FX-11 structural-check engine | **M9** (or M10 — see D-M9-5) | The structural shape check runs at fixture-authoring time (per §12.5) AND re-runs at verifier-execution time (per §12.6 step 4) |
| `mcf.metric_self_verification_result` (table + verdicts + diff trace) | **M10** | Verifier output substrate |
| Verifier service (read package by hash → run AST → compare to Section B → emit verdict) | **M10** | Deterministic; algorithm-versioned `mcf-verifier-v1` |
| `fk_mper_verification_result` (mper.satisfying_verification_result_uid → verification_result) | **M10** | Activation belongs to the gate that ships the target table |

**Doc-bug correction needed:** M4 DBCP comment on `metric_publication_eligibility_result.panel_run_uid` says the deferred FK targets "M9's `mcf.metric_self_verification_result`". That's wrong — `mcf.metric_self_verification_result` is M10. The M9 DBCP should explicitly flag this and the M10 DBCP should correct the comment when activating the FK.

---

## 8. Candidate designs

### 8.1 M9-A — static fixture files only (no DB substrate)

Fixtures live as versioned JSON files in `bc-core/fixtures/mcf/`. M10 verifier reads files by path keyed on `package_signature_hash`.

**Pros:** zero DDL; zero substrate impact; fast to ship.

**Cons:** violates Foundation Invariant V (evidence emitted, not inferred — file storage isn't audit-substrate); can't FK from `metric_publication_eligibility_result` to a fixture row; stale-fixture detection requires file-system walk; no per-fixture audit trail; build plan §M9 explicitly calls for `mcf.metric_self_verification_fixture` table.

**Rejected** because it contradicts the build plan and the Foundation discipline.

### 8.2 M9-B — single mcf-owned fixture registry table (RECOMMENDED per §9)

Per build plan §M9. Adds `mcf.metric_self_verification_fixture` with:
- 1 PK (`fixture_uid uuid`)
- 1 FK to `mcf.metric_contract_version` (intra-mcf; Drizzle)
- Optional 1 FK to `contract.panel_output_record` (cross-schema; DDL-only) — per D-M9-3
- 1 JSONB column carrying Section A+B+C body (or split into 3 columns per D-M9-2)
- 4 hash columns + bound `package_signature_hash` (5 hash text columns total)
- Audit columns (`created_at`, `created_by_name`, `superseded_at`, etc.)
- ~12 columns total — mirrors M4 / M5 sizing

**Pros:** matches build plan; FK-able from PE-result; queryable per-MC; stale-fixture detection via simple SQL on bound vs current `package_signature_hash`; substrate-enforced UNIQUE on `(mcv_uid, self_verification_fixture_hash)`.

**Cons:** ~12 columns is non-trivial; structural-check engine still needs implementation (in M9 or M10).

**Recommended.**

### 8.3 M9-C — fixture registry + fixture pack metadata

M9-B PLUS a `mcf.metric_self_verification_fixture_pack` parent table grouping related fixtures (null-handling + boundary + resolver-sensitivity per §12.8).

**Pros:** explicit modeling of multi-fixture coverage; lets PE-MC-10 cite a "pack" rather than a single fixture.

**Cons:** scope creep; §12.8 minimum-coverage-per-formula-class is explicitly an open question (§19.13 Q37); shipping pack-grouping pre-decides a Q37 design that isn't decided.

**Defer.** A pack table can be added in a future amendment if Q37 lands.

---

## 9. Recommendation

**D-M9-B** (single mcf-owned fixture registry table) per build plan §M9.

| Aspect | Decision |
|---|---|
| Table | `mcf.metric_self_verification_fixture` |
| MCV FK | intra-mcf, in Drizzle |
| Panel attribution | `panel_run_uid` nullable; cross-schema FK to `contract.panel_output_record`; DDL-only per repo convention (operator decides include/defer per D-M9-3) |
| Body shape | 1 jsonb column or 3 jsonb columns — operator picks per D-M9-2 |
| Hashes | 5 text columns (4 fixture-side + 1 bound `package_signature_hash`); format CHECK regex matches M7/M8 pattern |
| UNIQUE | `(mcv_uid, self_verification_fixture_hash)` |
| Stale-fixture | service-side equality check at fixture-bind + verifier re-checks per §12.6 step 3 |
| Immutability | per §12.9 — DBCP picks substrate-trigger vs service-side per D-M9-6 |
| C-FX engine | implementation deferred to M9 impl PR; can split into separate gate if operator wants substrate-only ship first (per D-M9-5) |
| Hashing service | reuse M7/M8 `FormulaCanonicalizationService` + `PackageSignatureService`; add `computeSelfVerificationFixtureHash(sectionA, sectionB, sectionC)` helper |

---

## 10. Risks and stop conditions

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M9-1 | C-FX-1..C-FX-11 structural checks not exhaustive — fixture passes C-FX but verifier fails on a corner case | Medium | Iterate via M10 evidence per build plan §M9 primary risk note; M9 DBCP enumerates all 11 checks + positive/negative test pairs |
| R-M9-2 | Stale-fixture detection asymmetry — substrate stores bound hash; service may forget to re-check | Low | M10 verifier per §12.6 step 3 re-checks; defense-in-depth optional service-side check at M9-side `bind_fixture` action |
| R-M9-3 | Fixture immutability discipline split — trigger vs service | Low | DBCP picks per D-M9-6; both are valid; trigger matches M5 transcript-immutability pattern |
| R-M9-4 | M5 panel doc bug propagation — M4 comment about M9 owning `metric_self_verification_result` is wrong (M10 owns) | Low | M9 DBCP explicitly flags and corrects; M10 DBCP confirms ownership |
| R-M9-5 | C-FX engine split between M9 and M10 — risk of double-implementation or gap | Medium | DBCP commits to ONE owner (recommend M9; M10 calls into the same service for re-check at verifier-execution time) per D-M9-5 |
| R-M9-6 | Body shape — single JSONB vs 3 columns — affects query patterns + JSONB-schema validation surface | Low | Operator picks per D-M9-2; both work; 3-column split eases per-section indexing |
| R-M9-7 | `self_verification_fixture_hash` canonicalization choice — JCS over Section A+B+C vs custom | Low | Reuse M7/M8 RFC 8785 JCS (per `mcf-jcs.ts`); no new canonicalization algorithm; algorithm version bundle marker `mcf-hash-v1` covers it |

### Stop conditions

- §19.13 Q37 (minimum-fixture-coverage per formula class) lands before M9 DBCP → may reshape the table (potentially add a pack table); rework needed.
- Build plan §M9 scope changes materially (e.g. adds reservoir-provenance on fixtures) → DBCP rescopes.
- M10 DBCP opens first → M9 stays consistent with M10's verifier-side hash expectations.

---

## 11. Operator decisions needed before M9 DBCP can open

| # | Decision |
|---|---|
| **D-M9-1** | Approve M9-B (single mcf-owned fixture registry table) over M9-A (static files) / M9-C (with pack) |
| **D-M9-2** | Body shape — single `body_json jsonb NOT NULL` carrying Section A+B+C OR 3 separate columns (`section_a_inputs_json`, `section_b_expected_output_json`, `section_c_resolver_config_json`) |
| **D-M9-3** | `panel_run_uid` attribution column — include nullable column + cross-schema FK at M9, OR defer to a future amendment after M12 lands |
| **D-M9-4** | UNIQUE constraint on `(mcv_uid, self_verification_fixture_hash)` — confirm at-most-one-fixture-per-(mcv, body-hash) — prevents accidental duplicate authoring |
| **D-M9-5** | C-FX-1..C-FX-11 structural-check engine ownership — M9 ships the engine (alongside DDL) OR M10 ships the engine (M9 ships substrate only). Recommend **M9 owns engine** so authoring fails at fixture-INSERT time, not at first verifier run. |
| **D-M9-6** | Fixture immutability per §12.9 — substrate-side trigger (mirrors M5 transcript pattern) OR service-side discipline. The §12.9 condition ("immutable once a pass is cited by PE-MC-10") requires reading a downstream M10 result row; trigger would FK-reference M10 (circular dependency). Recommend **service-side** for v1; trigger amendment in a future post-M10 gate if needed. |
| **D-M9-7** | Algorithm version marker for `self_verification_fixture_hash` — reuse `mcf-hash-v1` bundle (per M7/M8 §12.4) vs introduce `mcf-fixture-v1` — Recommend **reuse `mcf-hash-v1`** (single bundle scope) |
| **D-M9-8** | DBCP shape — combined M9 DBCP (substrate + C-FX engine + hashing helper) OR M9-substrate-only + M9-engine-followup. Recommend **combined** for atomicity. |

---

## 12. Recommended next gate

Combined M9 DBCP (single document) per D-M9-1 + D-M9-8.

**Suggested filename:** `metric-context-framework-m9-fixture-substrate-dbcp.md`

**Suggested PR title for impl PR (NO DB APPLY):** `feat(mcf): M9 Self-Verification Fixture Substrate — metric_self_verification_fixture + C-FX-1..C-FX-11 engine + computeSelfVerificationFixtureHash (NO DB APPLY)`

Sequencing per established pattern:
1. M9 DBCP → operator review → operator-accepted decisions D-M9-1..D-M9-8
2. M9 implementation PR (NO DB APPLY)
3. M9 small-DDL apply gate (separate operator-authorized session)
4. M9 evidence PR + bc-docs-v3 closeout

**Parallel-eligible** with **M11 preflight** (M11 also depends only on M5 which is live).

---

## 13. What stays closed

| | |
|---|---|
| M9 DBCP | not opened by this preflight |
| M9 impl PR | pending DBCP |
| M9 DDL apply | pending impl PR |
| M9 evidence PR | pending apply |
| **M10 deterministic verifier service** | CLOSED — gated on M9; separate gate |
| **M10 `mcf.metric_self_verification_result` table** | CLOSED — M10 owns; not M9 |
| **M11 reservoir ingestion** | CLOSED — separate gate (parallel-eligible to M9) |
| **M12 Metric Authoring Panel implementation** | CLOSED — gated on M5 + M7 + M10 + M11 |
| **M13 PE-MC evaluator** | CLOSED — gated on M5 + M7 + M9 + M10 |
| **M14+** | CLOSED |
| **Real MCF metric contracts** | CLOSED |
| **BCF data changes** | CLOSED — untouched throughout |
| **Q37 minimum-fixture-coverage per formula class** | OPEN (per §19.13); not a M9 dependency |
| **NF1 tightening on `mcf.certification_record`** | DEFERRED per D-M5-10 |
| **MCF defect-code v2 taxonomy** | CLOSED — v1 pinned |
| **MCF hash algorithm v2 bump** | CLOSED — `mcf-hash-v1` forever-locked unless ADR-governed change |
