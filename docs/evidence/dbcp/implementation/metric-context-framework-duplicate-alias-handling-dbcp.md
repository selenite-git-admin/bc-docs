---
uid: metric-context-framework-duplicate-alias-handling-dbcp
title: MCF Duplicate and Semantic Alias Handling — Judge-first with deterministic backstops
description: Design note for layered duplicate/semantic-alias detection in the MCF pipeline. Layer 1 — the M12 Judge makes the first semantic call against a narrowed docket of currently-active MCF contracts. Layer 2 — M12.5 enforces a deterministic identity_tuple_hash collision gate (L-V1h) before any draft MCV write. Layer 3 — M13 PE-MC-9 remains the final substrate-side backstop, unchanged. M11 fuzzy/name similarity is explicitly NOT promoted to a hard gate (D424 — rules are not valid as semantic judges). Uses `average_invoice_value` (cf98979d-…) as the canonical first negative specimen against the already-active `average_revenue_per_invoice` (MC 49cdde1a-…, MCV 8c088f55-…). DBCP-only. No code. No DDL. No intake creation. No M12 run. No DB mutation. The three implementation PRs (A read surface + docket injection, B Judge prompt/verdict extension, C M12.5 L-V1h backstop) are separately operator-authorized.
status: proposed
date: 2026-06-02
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-duplicate-alias-handling-dbcp
---

# MCF Duplicate and Semantic Alias Handling DBCP

## 0. Scope and discipline

Design-only DBCP. No bc-core implementation, no DDL apply, no DB write, no M12 invocation, no intake creation, no legacy writes. `bc-postgres` MCP `allow_write=false` throughout. The three implementation PRs (A, B, C — §8) are separately operator-authorized.

Baseline at DBCP-author time:
- bc-core main = `0cacdec` (PR #209 — M14 invocation-surface controller live)
- bc-docs-v3 main = `13cb297` (PR #48 — M14 invocation-surface DBCP)
- 1 active MCF metric: MC `49cdde1a-8bb3-41ad-9f67-9bb05d9f18a0`, MCV `8c088f55-5cd2-41f0-a1e6-501dce0fe104` (`average_revenue_per_invoice`).

## 1. Problem

The seeded `metric.metric_definition` catalog contains 1,241 rows. Many describe the same business concept under different surface labels (`metric_name`, `display_name`, `subfunction_code`, description). When such a candidate enters the MCF pipeline, the current substrate has **only one** gate that catches semantic equivalence: M13 PE-MC-9, which fires after M11 → M12 panel (expensive LLM cost) → M12.5 materialization (draft MCV written + orphaned on rejection). Catching duplicates that late is correct but wasteful.

A duplicate or semantic-alias candidate accepted as a new draft would:
1. Consume M12 budget for a metric the substrate already has.
2. Leave an orphan draft MCV plus 10 PE rows behind on PE-MC-9 rejection.
3. Confuse readers of `mcf.metric_contract_version` who scan for active candidates.

The pipeline needs duplicate detection earlier — but the early gates must respect D424 (Context Judge): rules are valid at deterministic system boundaries; rules are not valid as semantic judges. Name-similarity at intake fails this rule.

## 2. Example — `average_invoice_value` vs active `average_revenue_per_invoice`

| Field | ARPI (active MCV `8c088f55-…`) | AIV (candidate `cf98979d-…`) |
|---|---|---|
| Seed `metric_name` | `average_revenue_per_invoice` | `average_invoice_value` |
| Seed `display_name` | Average Revenue per Invoice | Average Invoice Value |
| Seed `subfunction_code` | `billing` | `general_finance` |
| Seed `description_text` | "average amount of revenue generated per invoice…" | "mean monetary value per invoice…" |
| Grain entity | Customer Invoice (`e3963e45-…`) | Customer Invoice (forced — only invoice entity in BCF) |
| `numerator_source` (input) BC | `amount` USD decimal (`a42d3fc0-…`) | `amount` USD decimal (forced — only monetary BC on Customer Invoice) |
| `denominator_key` (input) BC | `identifier` string (`095afe86-…`) | `identifier` string (forced — only identity BC) |
| `temporal_anchor` (input) BC | `date` (`d05f24b3-…`) | `date` (forced — only date BC) |
| Temporal gate | `period_aggregate` + `{period_type:'fiscal_period'}` | `period_aggregate` + `{period_type:'fiscal_period'}` |
| Formula AST | binary_op division (numerator / denominator) | binary_op division (forced — same shape under same bindings) |
| `identity_tuple_hash` | (stamped on MC `49cdde1a-…`) | **byte-identical** under the proven BCF substrate |

Under the **current** BCF, AIV authored honestly produces an identical `identity_tuple_hash` to ARPI. Surface differences (name, subfunction, description) do not translate to a different substrate identity because the BCF does not yet contain a `recognized_revenue` BC distinct from `amount`. AIV is therefore a **semantic alias** of ARPI today; it could become genuinely distinct only after a BCF extension. This conclusion is substrate-bound and must be re-evaluated whenever BCF changes.

## 3. Layer 1 — M12 Judge semantic duplicate review

**Layer 1 is the first semantic decision layer for duplicate / alias classification — no earlier rule-based gate makes the call (per D424).**

The Judge runs after the Maker proposes a candidate metric. Before the Judge issues `APPROVE_FOR_DRAFT`, the panel service injects a **docket** of currently-active MCF contracts narrowed for recall (§6). The Judge classifies the proposal into one of five outcomes:

| Judge outcome | Verdict code | Reason code | Carried in consensus |
|---|---|---|---|
| **New metric** | `APPROVE_FOR_DRAFT` (existing happy path) | — | normal `candidate_proposal` |
| **Exact substrate duplicate** | `REJECT_DEFECT` | `duplicate_active_metric` | colliding `mc_uid` + display name |
| **Semantic alias** (different surface, same substrate intent under current BCF) | `OPERATOR_REVIEW` | `semantic_alias_active_metric` | aliased `mc_uid` + alignment evidence (which proposed bindings collapse to which active bindings) |
| **Supersession candidate** (intentional next version of an active MC) | `OPERATOR_REVIEW` | `supersession_candidate` | predecessor `mc_uid` + delta narrative |
| **Near-duplicate, Judge uncertain** | `OPERATOR_REVIEW` | `near_duplicate_requires_review` | top-3 close matches + confidence notes |

`REJECT_DEFECT` is used **only** for the exact-substrate-duplicate case — there is no defensible reason to register a byte-identical second MC. The other three duplicate-adjacent outcomes route to `OPERATOR_REVIEW` because:
- An alias may be a deliberate operator choice (e.g., catalog organization), to be approved with an override note.
- A supersession is valid but routes through M15, a separate gate not yet open.
- An ambiguous case is by definition an operator decision.

The Judge does **not** compute `identity_tuple_hash`. That computation lives in M12.5 / M13 (deterministic). The Judge reasons over the docket structurally and semantically; the deterministic check is Layer 2's job.

A duplicate/alias verdict at this layer prevents M12.5 materialization entirely — the intake transitions to a duplicate-aware status (e.g., `pending_operator_decision` or `quarantined_alias`), NOT `consumed_by_panel`.

## 4. Layer 2 — M12.5 deterministic backstop (L-V1h)

**Layer 2 is mandatory deterministic enforcement — it runs on every materialization attempt regardless of Layer 1's verdict, including when the Judge has approved the candidate as a new metric.**

A new pre-TX-A precondition in `MetricAuthoringMaterializationService` — mirroring the L-V1a..L-V1g pattern from PR #205 / PR #202.

Steps (deterministic, no LLM):
1. Compute candidate `identity_tuple_hash` from the panel output's proposed bindings + grain + temporal gate via `PackageSignatureService.computeIdentityTupleHash` — the same SSOT M13 PE-MC-9 uses.
2. Query `mcf.metric_contract` for any non-archived row with the same `identity_tuple_hash`.
3. If a row exists: refuse with blocker `identity_tuple_hash_collision_with_active_mc` carrying the colliding `mc_uid` in the blocker payload. No draft MCV is written. No PE rows. No cert.
4. If no row exists: proceed to TX-A and continue normal materialization.

Preflight parity: the same check is exposed via `mcf-read.service.ts` so the M12.5 preflight HTTP endpoint surfaces the blocker before invocation, matching the L-V1c/L-V1g preflight pattern.

This layer is structural, not semantic. It does not understand "alias" vs "supersession"; it only knows that two MCs cannot share the same `identity_tuple_hash` and remain non-archived simultaneously.

## 5. Layer 3 — M13 PE-MC-9

**Unchanged.** `runPeMc9DefinitionDiscipline` already computes the candidate `identity_tuple_hash` via the same M8 SSOT and REJECTs on collision with an active MC. It is the final substrate-side guard and stays exactly as locked at PR #208.

PE-MC-9 fires after the draft MCV is in substrate, so it is the most expensive of the three to trigger — but it remains necessary as the final correctness backstop in case Layer 1 + Layer 2 are both bypassed (e.g., by a future hand-applied invocation that skips M12 panel + M12.5 entirely).

## 6. Docket read surface

A new read on `McfReadService` — `readActiveMcfContractDocket(narrowingFilter)` — returns one fully-dereferenced entry per active MC. The read is the only producer of the docket; the M12 panel service is the only consumer.

**Per-entry contents:**
- `mc_uid`, `mc_name`, `mc_display_name`
- Grain entity: `entity_id`, `canonical_name`, optional `family_code`
- Temporal gate: `shape_code`, kernel params
- Active MCV: `formula_ast_canonical_json`
- Variable bindings, each fully dereferenced: `variable_role_code`, `role_kind_code`, BC `representation_term`, BC `semantic_role`, entity `canonical_name`, unit, data_type
- Filter clauses (if any)
- `identity_tuple_hash` (for cross-reference + Layer 2 carryover; Judge does NOT recompute it)
- Source lineage: legacy `metric_definition_id` if known + ADM seed_ref if known
- Subfunction + 1-line description (sanity context)

**Excluded:** PE-MC history, tenant runtime data, performance metrics, cert chain — token bloat with no semantic-judgment value.

**Narrowing** (deterministic, recall-favoring; rules-on-recall, not rules-on-semantics):
- Hard filter: candidate's proposed grain entity OR an entity sharing `family_code`.
- Soft filter: display-name token-set Jaccard ≥ 0.3 against candidate's proposed `mc_display_name`; top-K by score.
- Cap: 20 entries default, 50 hard ceiling. If the candidate matches >50 actives by grain alone, surface as a separate operator note ("catalog overpopulation in {entity}").

Recall failures at the narrower layer are caught deterministically by Layer 2 — the narrower's role is to keep the prompt focused, not to be the correctness boundary.

**Today's docket** (1 active MC): trivially returns ARPI for any Customer Invoice candidate. Scales linearly with active catalog growth.

## 7. First negative test — `average_invoice_value`

The canonical first negative specimen. Concrete sequencing when the three PRs land:

1. **Read-only verification (now, no code):** the §2 substrate analysis is the proof that AIV's expected substrate identity equals ARPI's.
2. **Intake (after PR A + B land, operator-authorized):** author an intake row for `average_invoice_value` (`cf98979d-…`) via the normal reservoir → intake path.
3. **M12 run (operator-authorized):** the panel runs. Maker proposes; Judge sees ARPI in the docket; Judge issues consensus = `OPERATOR_REVIEW` with `reason_code = 'semantic_alias_active_metric'` and `aliased_mc_uid = 49cdde1a-…`.
4. **Expected substrate state post-run:** intake row in duplicate-aware status (e.g., `pending_operator_decision`); zero MCF substrate writes beyond the consensus and intake transition; zero draft MCV; zero PE rows; zero cert.
5. **Layer 2 chaos verification (after PR C lands):** canned Judge response that wrongly issues `APPROVE_FOR_DRAFT` → M12.5 L-V1h refuses with `identity_tuple_hash_collision_with_active_mc` blocker; zero substrate writes from M12.5. Proves the layers are independent.

This specimen also becomes a regression test at three tiers:
- Unit: Judge prompt + canned docket + canned AIV proposal → expected reason code.
- Integration: full M12 with mock vendor → consensus + intake transition match.
- Live: one operator-authorized real M12 invocation; archive the consensus payload to bc-docs-v3 as canonical evidence.

If the Judge ever wrongly approves AIV, Layer 2 catches it — and that itself is a useful signal (prompt drift; docket recall regression; vendor change).

## 8. Implementation sequence

Three PRs, separately operator-authorized in this order:

| PR | Scope | Authority |
|---|---|---|
| **PR A — Read surface + docket injection** | New `readActiveMcfContractDocket(narrowingFilter)` on `McfReadService`; new narrower helper (deterministic; recall-favoring; capped); panel-service wiring to fetch the docket and pass it to the Judge prompt context. Adds the `ActiveMcDocketEntry` type. No prompt changes yet. No verdict-grammar changes. | This DBCP §6 |
| **PR B — Judge prompt + verdict payload extension** | M12 Judge prompt update with the duplicate-classification grammar (§3 five outcomes); consensus payload schema extension carrying `reason_code` + `aliased_mc_uid` (or `colliding_mc_uid` / `predecessor_mc_uid` per case); intake transition update so the new statuses route correctly (e.g., `pending_operator_decision`). Reason codes added to the existing `panel_output_record` enum surface (small substrate update if needed; otherwise carried in the JSON payload). | This DBCP §3 + §7 |
| **PR C — M12.5 L-V1h identity collision backstop** | New pre-TX-A precondition mirroring L-V1g shape; preflight parity in `McfReadService`; integration spec covering hit + miss paths + chaos-verification scenario from §7 step 5. | This DBCP §4 |
| **(unchanged)** | M13 PE-MC-9 stays exactly as locked at PR #208 / D-M13-5. | §5 |

**M11 is intentionally not on the list.** M11 fuzzy / display-name similarity is **not** promoted to a hard gate per D424 (rules are not valid as semantic judges). The recall-favoring narrower (§6) uses similarity heuristics, but only as a recall filter for the docket presented to the Judge — never as a standalone reject decision.

Each PR is small enough to ship on its own; together they implement the layered design. PR A is a pure additive read; PR B carries the semantic gate; PR C carries the deterministic backstop. The order matters because the Judge in PR B cannot reason about active MCs without PR A's docket; and PR C is most useful once PR B is producing structured duplicate-adjacent verdicts that PR C can backstop.

## 9. Risks

| Risk | Layer | Mitigation |
|---|---|---|
| Narrower (§6) misses a relevant active MC (recall failure) | Layer 1 | Layer 2's deterministic check scans **all** active MCs unconditionally |
| LLM Judge hallucinates `new_metric` for a structural duplicate | Layer 1 | Layer 2 catches via `identity_tuple_hash` collision; PE-MC-9 catches as backstop |
| Prompt drift weakens duplicate sensitivity over time | Layer 1 | Layer 2 has no prompt; PE-MC-9 has no prompt |
| Direct M12.5 invocation that bypasses M12 panel | Layer 1 | Layer 2 runs regardless of M12 panel state |
| BCF extension (e.g., `recognized_revenue` BC) flips the verdict | All | Verdict is substrate-bound; re-evaluation policy on BCF change is recorded in §2 |
| Two-MC-author race on the same identity_tuple_hash | Layer 2 | Substrate UNIQUE on (identity_tuple_hash WHERE archived_at IS NULL) is the final guarantor (already covered by PE-MC-9's substrate-side guard; L-V1h is the service-layer prefix) |
| Catalog overpopulation under one entity (>50 active MCs sharing grain) | Layer 1 (narrower) | Surface as an operator note ("catalog overpopulation in {entity}") — not silent truncation |

No HIGH-severity risks remain after the three layers compose.

## 10. Deferred / out of scope

- **`average_invoice_value` actual intake + M12 run** — separately operator-authorized after PR A + B land.
- **Display-name similarity as a hard gate** — explicitly rejected (D424).
- **Auto-supersession routing from Layer 1** — when Judge identifies a `supersession_candidate`, intake routes to operator review. The actual M15 supersession gate (and its DBCP) is a separate future work item.
- **Operator-facing UI for alias review** — bc-admin surface for `pending_operator_decision` intakes is a separate UX work item.
- **Bulk re-evaluation of existing intakes** — after the three PRs land, retroactive scanning of pending intakes for hidden aliases is a separate operator-authorized batch task.

## 11. Constraints respected

- ✓ Design only; no bc-core implementation
- ✓ No M12 run
- ✓ No intake creation
- ✓ No DB mutation
- ✓ No DDL apply
- ✓ No legacy writes
- ✓ No Cognito changes
- ✓ Single concise DBCP — no separate ADR (the D424 / DEC-32a56e ADR already covers the Judge-as-semantic-authority principle; this DBCP applies it to duplicate detection specifically)

## 12. Authority

- ADR: `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) — MCF Build Plan.
- ADR: `bc-docs-v3/docs/adrs/ADR-3f093f.md` (DEC-3f093f / D426) — MCF Canonicality and Legacy Runtime Boundary.
- ADR: `bc-docs-v3/docs/adrs/ADR-32a56e.md` (DEC-32a56e / D424) — Context Judge for semantic grounding (the principle this DBCP applies).
- M12.5 DBCP: `metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md` — upstream gate; L-V1h slots in as a new precondition.
- M13 PE-MC evaluator DBCP: `metric-context-framework-m13-pe-mc-evaluator-dbcp.md` D-M13-5 — locks PE-MC-9's identity-tuple-hash recipe.
- M7/M8 hash authority DBCP — `PackageSignatureService.computeIdentityTupleHash` is the SSOT both M12.5 L-V1h and M13 PE-MC-9 consume.

---

**End of DBCP.**

Three implementation PRs (A read surface + docket injection, B Judge prompt + verdict payload, C M12.5 L-V1h backstop) are separately operator-authorized follow-ups. No code change lands until those PRs open, review, and merge. `average_invoice_value` is the canonical first negative specimen; no intake or M12 run for it occurs until the operator explicitly authorizes both.
