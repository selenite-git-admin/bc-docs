---
metric: platform-wide-cf-certification-and-duplicate-resolution
metric_version: n/a
tenant: platform
source_system: n/a
work_type: cleanup
session_uid: SES-a223ea
date: 2026-05-12
status: decision-pending
related_commits: []
related_tasks: []
related_adrs:
  - DEC-69f09e   # D148 — ISO 11179 naming standard
  - DEC-d72560   # MC variables reference Canonical Fields (CFs are the metric vocabulary)
  - DEC-ebf0b4   # D268 — Session Discipline
related_mwrs:
  - 2026-05-12-semantic-base-audit-SES-a223ea.md   # the audit this design responds to
  - 2026-05-11-total-revenue-production-gap-SES-1c080e.md   # CF-PATCH endpoint gap noted in §8
  - 2026-05-11-total-company-revenue-production-gap-SES-524cdc.md
  - 2026-05-11-operating-cash-flow-production-gap-SES-524cdc.md
related_change_records:
  - CHG-a880b3
repair_location: B
affected_boundary: canonical_evaluation
foundation_gate: passed
---

# Tier-1 Remediation Design — CF identity, certification, and duplicate resolution

> **Design-level only.** No DBCP. No DDL. No endpoint specs. No ADR filing. No task filing. The output is a decision frame the operator can review and revise before any artifact is authored. The audit ([2026-05-12-semantic-base-audit-SES-a223ea.md](../../../../audits/onboarding/2026-05-12-semantic-base-audit-SES-a223ea.md)) is the input; this MWR proposes how Tier-1 of the audit's cleanup plan should be structured.

## Why this work is Tier-1

The audit established that **603 canonical fields sit in `status='draft'`, 122 use non-snake_case names, 67 % cluster into 172 near-name stems (G2b normalized-form collisions — G2a byte-identical duplicates do not occur, verified by Phase 0; the live unique index `canonical_field_field_name_key` prevents them)**. Every cc_field_mapping, every MC variable, every metric_binding currently resolves against a CF table that:

- has enforced byte-level uniqueness on `field_name` (Phase 0 verified) — but no service-level governance over near-duplicate (G2b) naming
- has no certified set
- has no `semantic_family` populated
- has no governing-source citation

Any downstream remediation (funnel-padding cleanup §2, CC naming consolidation §3, shell-CC cluster builds §4, etc.) depends on the assumption that "CF X means exactly one thing." Today that assumption does not hold. **CF certification + duplicate resolution is therefore the structural prerequisite for every other Tier-1+ workstream.**

This design pass does not certify any individual CF and does not pick any survivor. It defines the rules under which certification + survivor-selection will happen.

## Foundation Gate Result

- **Repair location:** **B** (contract semantics). CF identity is the canonical-layer vocabulary; certification is the canonical-layer authority claim.
- **Affected boundary:** the canonical evaluation boundary's entry vocabulary. Once CFs are certified, metric evaluation can rely on Meaning-once at the CF level.
- **Six-invariant pre-check:**
  - **I (Meaning once):** the design's whole purpose is to restore Invariant I at the CF layer. Certification = the platform's assertion that *one CF = one meaning*. Deprecation of duplicates removes ambiguity.
  - **II (Object ordering):** unchanged.
  - **III (State immutability):** the design preserves prior MC snapshots — Invariant III holds. Survivor selection does not rewrite historical evaluations; it sets the rule for going-forward authoring. Existing references to deprecated CF UUIDs are migrated by alias preservation (§4), not by mutation.
  - **IV (Explicit references):** survivor selection makes every CF reference explicit (each `field_code` resolves to exactly one row).
  - **V (Non-replayable evaluation):** unchanged.
  - **VI (Evidence emitted):** unchanged for evaluations; certification itself emits its own evidence (when, who, governing source).
- **Why not other layers:** A (source / SDG), C (mapping), D (engine), E (storage), F (read) cannot resolve CF identity. The vocabulary lives at layer B.
- **Override:** none.

## Scope of this design

| In scope | Out of scope |
|---|---|
| Define what "certified" means for a CF | Authoring any CF certification |
| Define duplicate detection criteria | Marking any specific CF as a duplicate |
| Define survivor-selection criteria | Choosing any specific survivor |
| Define alias / reference preservation strategy | Implementing alias storage |
| Define the deprecation lifecycle | Deprecating any CF |
| Identify what additional service / DDL surface is *needed* for the strategy | Proposing the DDL or endpoint shape |
| Identify operator decisions required | Filing tasks or ADRs |

## §1 — CF certification — definition

A canonical field transitions `draft → certified` only when **all** of the following are true at the time of promotion:

| Promotion gate | Source of truth |
|---|---|
| `field_name` is snake_case and matches D148 / DEC-69f09e | Naming standard chapter |
| `description_text` is present, ≥ 1 sentence, and authored to be understandable without reference to any specific source system | The CF body itself |
| `semantic_family` is populated with one of a small enumerated set (see §1.a) | Canonical-field-seeding chapter — the enumeration is part of this design's open questions |
| `function_code` and `subfunction_code` accurately describe the CF's business domain (no `total_company_revenue` mis-tagged `accounts_payable`-shape errors) | Business-catalog taxonomy |
| `data_type` matches the implied unit / numeric / categorical / temporal type | The CF body |
| `unit_type_code` is set when the CF expresses a quantity | The CF body |
| `role` is `input` (consumed by metrics) or `output` (produced by metrics) and matches actual usage | metric_formula_variable + metric_binding |
| A **governing-source citation** is present — at minimum the doc / ADR / storyboard that defines the CF's meaning | new schema slot `standard_ref` or a follow-on field |
| **Meaning-once test:** no other certified CF has the same governing-source-citation OR the same `(target CC, BF, rule, filter_json, compute_json)` signature in active mappings | cross-CF check; this is the operational test for Invariant I |

Certification is per-CF and timestamped. It does not require all CFs to be certified at once; it sets a gate that **new CFs must pass and existing draft CFs may pass on their own cadence**.

### §1.a — `semantic_family` — open enumeration

The audit found `semantic_family = NULL` for every CF. The field exists in schema but no taxonomy has been adopted. Candidate families (for operator review, not declared here):

- `monetary_amount_flow` (revenue, expenses, payments — events accumulated over a period)
- `monetary_amount_balance` (AR balance, AP balance, cash position, inventory value — points-in-time)
- `count` (invoices processed, transactions count, employees)
- `ratio` (margin %, current ratio, debt-to-equity)
- `rate` (interest rate, FX rate, growth rate)
- `score` (risk score, compliance score, automation index)
- `categorical` (currency code, vendor type, account class)
- `temporal` (fiscal year, fiscal period, posting date)
- `identifier` (customer ID, vendor ID, employee ID)

Each family carries its own valid operators (Meaning-once interacts with this). Adopting the enumeration is its own design decision — open question §6 below.

### §1.b — Certification authority

Open question (§6): who certifies. Three candidate paths:

- **Operator certification** — an operator with the `schema_author` role flips a CF to certified after meeting the gate. Simplest; requires no new role definition.
- **AI-assisted certification with operator confirmation** — bc-ai proposes certification based on the gate's machine-checkable parts (snake_case, non-null description, unique signature), operator confirms semantic alignment.
- **ADR-grade certification per CF family** — each `semantic_family` is certified collectively by an ADR. Heaviest; most defensible long-term.

No path proposed here. Operator decision.

## §2 — Duplicate detection — three classes

The audit's data supports three distinct duplicate classes, each with its own evidence shape:

### §2.a — Literal duplicates (G2a — theoretical class; 0 observed)

**Definition:** two or more `canonical_field` rows have byte-identical `field_name`, regardless of UUID, description, or mappings.

**Observed in live DB:** **zero.** Phase 0's `/diagnostics/unique-index-state` confirmed that `contract.canonical_field` has a live single-column unique index `canonical_field_field_name_key` enforcing global byte-level uniqueness on `field_name` (R3 PM correction A4 in the audit MWR; SDA §C3). The audit's earlier "12+ literal duplicates" claim was a misread of the stem-grouping output — the apparent byte-repeat samples (`Asset Age`, `Asset Age`, `Asset Age`) were normalisations of distinct underlying strings, not byte-identical rows.

**Defensibility test:** **none.** Two CFs with byte-identical names cannot be defensibly distinct unless the platform explicitly supports namespacing (which it does not). The class is preserved here as a theoretical guard so that any future migration-drift event that introduces byte-identical rows is named and treated correctly.

**Severity if observed:** Sev-1. Currently no cleanup workload, because no rows match.

### §2.b — Semantic duplicates (mapping-signature collision with no distinguishing artifact)

**Definition:** two or more CFs have at least one `cc_field_mapping` row each that collapses onto the same `(canonical_contract_id, business_field_id, resolution_rule_code, filter_json, compute_json)` signature, AND the CFs have no other distinguishing artifact (no `compute_json` elsewhere, no `filter_json` elsewhere, no different governing-source citation).

**Evidence in audit:** R4 funnel-padding — 144 candidate groups, 1,380 colliding mapping rows. Top supercluster: 281 CFs on `cc__actual_ledger.actual_ledger_amount` SUM ∅ ∅.

**Defensibility test:** per Revision A3 of the audit MWR, each candidate group falls into one of three resolutions:

1. **Defensible-once-distinguished** — CFs are genuinely distinct in meaning; the missing `filter_json` / `compute_json` is an authoring gap. Remediation: author the distinguishing artifact. *Not a duplicate after authoring.*
2. **Semantic duplicate** — CFs are the same meaning by another name. Remediation: deprecate non-survivors per §3.
3. **Misclassification** — one or more CFs is mapped to the wrong BF (R2-shape — target BF in `unmapped_fields`). Remediation: repoint per Meaning-once discipline.

Per-cluster governing-source review determines which class. **Severity at candidate stage: Sev-1 for top-25 superclusters, Sev-2 for smaller groups.** Confirmation requires per-cluster review.

### §2.c — Near-name duplicates (heuristic candidates)

**Definition:** two or more CFs share a stem under a stem function, even if their full names differ. Catches `accounts_receivable_balance` vs `average_accounts_receivable_balance`, or `operating_cash_flow` vs `cash_flow_from_operations` vs `current_period_operating_cash_flow`.

**Evidence in audit:** R1.b — 172 stem-clusters covering 403 CFs.

**Defensibility test:** **the stem function is heuristic** (per Revision A2). A near-name cluster is a candidate-list for review, not a duplicate declaration. Many clusters will resolve to "genuinely different metrics under similar names" (e.g. `current_ratio` vs `quick_ratio` would stem-collide but they are distinct ratios). Review is required.

**Severity at candidate stage: Sev-2** — review-needed catalog cleanup, not stop-the-line.

## §3 — Survivor selection criteria

For each confirmed duplicate cluster (§2.a or §2.b case 2), exactly one CF becomes the **survivor**; the rest are **non-survivors** and enter the deprecation lifecycle (§5).

Survivor-selection criteria, applied in order:

| Order | Criterion | Why |
|---|---|---|
| 1 | **Governing-source citation present and authoritative** | A CF backed by a doc / ADR / storyboard outranks a CF authored by drift. If both are cited, the more authoritative source (Foundation > ADR > onboarding chapter > storyboard) wins. |
| 2 | **Name matches D148 / DEC-69f09e** | snake_case + ISO-11179 outranks Title Case With Spaces. |
| 3 | **`description_text` present and richer** | A CF with a non-null, substantive description outranks one without. Length is not the test; intent-clarity is — operator judgment per cluster. |
| 4 | **Most-referenced by active artifacts** | A CF referenced by N MCs + M cc_field_mappings outranks one with fewer references. Reduces migration cost (§4). |
| 5 | **Most recent metadata update** | If above are tied, the most recently `updated_at` row wins — newer authoring presumably reflects newer thinking. |
| 6 | **Smallest `canonical_field_id` (UUID v7 timestamp)** | Final tie-breaker. Deterministic and reproducible. |

Survivor selection is **per-cluster operator decision** (informed by governing-source review). The criteria above are a default ordering; the operator may override with documented reason per cluster.

## §4 — Alias and reference preservation

When a non-survivor CF is deprecated, every existing reference must continue to resolve correctly until migration is complete. The design:

### §4.a — Alias storage

A non-survivor CF carries (in body or as a new column) a `superseded_by_canonical_field_id` reference pointing at the survivor. The old `field_name` remains queryable on the deprecated row so search-by-name still finds it; UI / API surfaces present it as "alias of <survivor>".

The audit-time `business_field` table already has `aliasCount` on its rows — there is precedent for alias-tracking in the registry. The CF table does not have an alias column today; whether to add one (DDL) or carry aliases in a new `canonical_field_alias` table is a downstream service-design decision **out of scope here**.

### §4.b — Reference migration plan (rule, not execution)

Active references to a deprecated CF must be migrated to the survivor in batches:

| Reference type | Migration shape |
|---|---|
| `cc_field_mapping.canonical_field_id` | Update row's `canonical_field_id` to survivor's UUID. Governed via a new "repoint CF reference" service if not already covered by D330-R5 (D330-R5 today swaps BF on a mapping, not CF). |
| `metric_formula_variable.field_name` | Update to survivor's `field_name`. This is a metric-version-impacting change → requires MC version bump per Live MC Safety Workflow (Metric Workstream §5). |
| `metric_binding.fields_used[]` array | Update array entries; requires MC version bump. |
| `metric_definition.*` references (if any) | Update; metric_definition is platform-level metadata. |
| External docs (storyboards, MWRs, ADRs) | Markdown find-replace per doc. Cite the survivor going forward. |

**No migration is executed in this design.** The plan exists so that whoever executes Tier-1 understands the migration is a known set of governed operations, not an ad-hoc rewrite.

### §4.c — Backward-compat window

Each deprecated CF stays queryable (returns from `GET /canonical-fields/:id` with status `deprecated` + the `superseded_by` link) for a window long enough for downstream consumers to update. Window length is open question §6.

## §5 — Deprecation lifecycle

A CF moves through four states:

| State | Definition | Operations allowed |
|---|---|---|
| `draft` | newly registered, not yet certified | metadata edits, mapping authoring |
| `certified` | meets the §1 gate; declared canonical | metadata edits **only** with audit trail; no semantic mutation in place (Invariant III) |
| `deprecated` | identified as a non-survivor; references being migrated | read-only; emits `superseded_by` |
| `archived` | all references migrated; no active dependents | hidden from default listings; remains queryable for historical audit |

The `archived` state is optional and downstream. Without it, the platform retains the deprecated row indefinitely — also defensible.

Promotion `draft → certified` is the certification act of §1. Demotion `draft → deprecated` is for duplicates that are never certified. Demotion `certified → deprecated` is for duplicates discovered after certification (rare; should be a recorded mistake, not a normal path).

## §6 — Open questions for operator

| # | Question | Why it matters |
|---|---|---|
| Q1 | Adopt the `semantic_family` enumeration as proposed (§1.a), or propose a different taxonomy? | Certification gate references this. |
| Q2 | Certification authority — operator, AI-assisted, or per-family ADR (§1.b)? | Affects who can flip a CF to certified and how often. |
| Q3 | For near-name clusters (§2.c), what threshold separates "review-required" from "ignored"? Today's stem function catches 172 clusters; not all are duplicate candidates. | Determines workload of the review pass. |
| Q4 | Backward-compat window length for `deprecated` CFs (§4.c) — fixed (e.g., 90 days), variable per CF, or indefinite? | Affects when references must finish migrating. |
| Q5 | When the gate's "Meaning-once test" finds two certified CFs with same signature (§1, last row), is that a hard certification failure, or a flag for review? | Affects how strict the gate is in practice. |
| Q6 | Should certification require explicit citation of a single governing source, or accept a list (e.g., "ADR D210 + storyboard §3")? | Affects how flexible authoring is. |
| Q7 | Survivor-selection criterion #1 (§3) says "governing-source citation outranks." If a non-survivor has a citation and the proposed survivor does not, does the citation transfer, or does survivor selection re-pick? | Edge case; affects deterministic-replay of the cleanup. |

## §7 — What comes after this design lands

Only **after** the operator confirms the §1–§6 frame, the work that follows in order:

1. **CF-level review of normalized-form (G2b) clusters (§2.c)** — 172 clusters covering 403 CFs identified by the audit. Per-cluster survivor selection. Open questions resolved by Q1–Q7 first. (G2a literal-duplicate cleanup is a no-op: 0 observed; the live unique index `canonical_field_field_name_key` prevents them.)
2. **CF-level review of top-25 funnel-padding superclusters (§2.b)** — per-cluster governing-source review classifies each as defensible / duplicate / misclassification (Revision A3 of the audit). Mapping-level remediation per classification.
3. **CF-level review of near-name clusters (§2.c)** — heuristic candidates; operator-led culling first, then per-cluster review of the survivors.
4. **Service / DDL design pass** — only once the review work has surfaced what surfaces are actually needed: a CF metadata PATCH endpoint ([total_revenue MWR §8](2026-05-11-total-revenue-production-gap-SES-1c080e.md) followup), a CF alias table or column, a service-level G2b normalized-form uniqueness pre-check (the live DB unique index already covers G2a byte-identical), an optional governed migration aligning the Drizzle-declared index name `uq_canonical_field__name` to the live `canonical_field_field_name_key`, etc. The shape of these surfaces depends on the review outcomes — designing them now would prejudge the cleanup.
5. **Cleanup execution** — Tier-1 itself, per the audit's prioritized cleanup plan §1–§3.

Steps 4 and 5 are **explicitly out of scope** for this design MWR. Steps 1–3 require operator approval of §1–§6 before they can begin.

## §8 — What this design does NOT do

- No DBCP authored.
- No DDL proposed (no `UNIQUE` index, no new columns, no new tables).
- No endpoint specs proposed (no PATCH endpoint, no alias-resolution endpoint, no batch-deprecate endpoint).
- No ADR drafted or filed.
- No DevHub tasks filed.
- No CF specifically marked as a duplicate.
- No specific survivor proposed for any cluster.
- No `semantic_family` taxonomy adopted (proposed only).
- No certification authority chosen.
- No backward-compat window picked.
- No work executed.

## §9 — Decisions required from operator before any further step

In the order above (§6): Q1 – Q7. Without these, the §7 review work cannot begin because the rules are undefined.

Additionally, operator confirmation on:

- **D1.** Tier-1 ordering — does CF certification + duplicate resolution precede every other audit-cleanup workstream (per audit §"Prioritized cleanup plan" §1), or does another workstream (e.g. CC naming consolidation §3) precede or run in parallel?
- **D2.** Whether this design proceeds as a standalone Tier-1 ADR (elevating it to architectural authority) or remains an operating-model design captured in MWR + onboarding-chapter updates.

## Evidence

- Audit MWR [2026-05-12-semantic-base-audit-SES-a223ea.md](../../../../audits/onboarding/2026-05-12-semantic-base-audit-SES-a223ea.md) — full findings + cluster data
- Audit datasets at `C:/Users/anant/AppData/Local/Temp/bc-semantic-audit/` (working memory)
- Related MWRs: total_revenue (Slice 1 + §8 service gap), total_company_revenue (deferred), operating_cash_flow (deferred), DSO grammar design
- Foundation: [the-invariants.md](../../../../../foundation/the-invariants.md), [the-contract-grammar.md](../../../../../foundation/the-contract-grammar.md)
- Onboarding chapters: [canonical-field-seeding.md](../../../../../onboarding/canonical-field-seeding.md), [business-field-and-business-object-onboarding.md](../../../../../onboarding/business-field-and-business-object-onboarding.md), [metric-workstream.md](../../../../../onboarding/metric-workstream.md)
- ADRs: DEC-69f09e (D148 — ISO 11179), DEC-d72560 (CF as MC vocabulary), DEC-ebf0b4 (D268 — session discipline)

## Closing

This design pass converts the audit's "Tier-1: CF certification + funnel-padding cleanup + CC naming consolidation" into a defined decision frame for the first of those three workstreams (CF identity). It deliberately stops short of authoring DDL, endpoints, ADRs, or tasks — those depend on operator decisions on Q1–Q7 and D1–D2. The design is decision-pending; no further work begins until the operator confirms the frame or revises it.
