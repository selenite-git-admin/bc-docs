---
uid: metric-context-framework-m3-m4-cert-substrate-correction-preflight
title: MCF M3 / M4 Certification Substrate Correction Preflight
description: Discovery-driven correction preflight. M4 implementation gate (per DBCP e56fc7e) was halted at pre-implementation read because 10 live Foundation Governance Substrate CHECK constraints reject the cert-reuse design that M3 DBCP D-12 + M4 DBCP D-19 confirmed. `contract.certification_record` admits only two row shapes today (legacy BF/BO/CF + BCF Registry Model A per Phase A Bucket-1 alignment); no MCF row shape is admissible. `contract.framework_policy.scope_code` rejects 'mcf'; `contract.operator_confirm_rule.scope` rejects 'mcf'; the transition enum lacks `active_to_superseded`; the rule.action_code column was semantically confused with cert.action_code in the M4 DBCP. This preflight frames the mismatch, evaluates 3 resolution options (A extend shared cert table to a third row-shape; B per-framework `mcf.certification_record` sibling; C hybrid — sibling for cert semantics + small CHECK extensions for shared policy/rule grammar), recommends Option C with rationale, specifies the 6 amendment areas required (M3 DBCP D-12 reversal + M3 trigger lookup target ALTER + M3 supersession FK redirect + M4 DBCP D-19/§9/§10 rewrite + M4 dry-run/verifier assumption update + shared CHECK extensions), assesses M3 rollback necessity (recommendation: no rollback — M3 substrate live but operationally dormant since 0 cert writes attempted; forward amendment via CREATE OR REPLACE FUNCTION + DROP/ADD CONSTRAINT is safer and complete), proposes a 9-gate sequencing (this preflight → M3 amendment DBCP → M3 amendment PR → M3 apply → M3 evidence PR → M4 DBCP rewrite → M4 implementation PR → M4 apply → M4 evidence PR), and enumerates 7 operator decisions required before the M3 amendment DBCP can open. M3 substrate stays unaffected (live + dormant; no cert writes have occurred). No DDL applied; no bc-core code edited; no MCF metric contracts created; no certification rows written; no BCF data touched. Doc-only correction record.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-cert-substrate-correction
---

# MCF M3 / M4 Certification Substrate Correction Preflight

## 1. Scope and grounding

### 1.1 Purpose

Frame the substrate mismatch discovered at pre-implementation of MCF Gate M4 (lifecycle certification / transition authority). Evaluate resolution options. Recommend a path forward. Specify the cross-gate amendments the chosen option entails. Enumerate the operator decisions required before any further gate opens.

This is a **docs-only correction preflight**. It does not implement the correction. It does not apply DDL. It does not edit bc-core. It does not author the M3 amendment DBCP (that's a subsequent gate). It is the formal record of "Foundation gate fired; M4 design conflicts with live substrate; here is the violation and the option set."

### 1.2 What this preflight is and is not

| | This preflight |
|---|---|
| Is | A docs-only framing of the substrate mismatch + option set + recommendation + operator decisions needed |
| Is | The formal trigger for a sequenced correction arc (M3 amendment + M4 redesign) |
| Is not | The M3 amendment DBCP itself (next gate; designs the exact DDL + Drizzle + trigger ALTER) |
| Is not | The M4 DBCP rewrite (later gate; depends on amendment outcome) |
| Is not | An M3 substrate apply or rollback — M3 stays live and dormant per §7 |
| Is not | A bc-core code edit |
| Is not | A BCF DBCP — the shared-table CHECK extensions in Option C touch BCF-shared substrate, which warrants BCF arc coordination (see §9 D-Correction-7) |

### 1.3 Source documents consumed

| Source | Role | Commit / location |
|---|---|---|
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority; Decision 10 guardrails | `bc-docs-v3/docs/adrs/ADR-c3e57f.md` |
| MCF M3 DBCP §3.12 D-12 (cert reuse) + §6.3 (state-transition trigger body) + §5 (supersession FK) | The cert-reuse decision being reversed; the trigger and FK that must be amended | `metric-context-framework-m3-lifecycle-substrate-dbcp.md` (`3147bd4 + 938fb0f`) |
| MCF M3 apply closeout | M3 live substrate state | `mcf-m3-ddl-apply-closeout.md` (`d1f67d0`) |
| MCF M4 DBCP §3.19 D-19 (cert reuse confirmed) + §9 (cert column matrix) + §10 (seed rows) | The cert-reuse confirmation being reversed; the design that must be rewritten | `metric-context-framework-m4-lifecycle-certification-dbcp.md` (`e56fc7e`, 21 patches applied) |
| Live `contract.certification_record` Drizzle schema | Documents the 8 CHECK constraints, 5 indexes, FK to `panel_output_record`, row-shape discriminator + couplings | `bc-core/src/database/schema/contract/certification-record.ts` |
| Live `contract.framework_policy` Drizzle schema | Documents `scope_code` CHECK enum, active-per-scope UNIQUE | `bc-core/src/database/schema/contract/framework-policy.ts` |
| Live `contract.operator_confirm_rule` Drizzle schema | Documents `scope` / `transition` / `action_code` CHECK enums | `bc-core/src/database/schema/contract/operator-confirm-rule.ts` |
| M3 lifecycle DDL | The exact trigger body that must ALTER + the cross-schema FK that must redirect | `bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql` |
| Live CHECK constraint definitions on `contract.*` tables | Empirically verified via `pg_query` against `bc_platform_dev` this session (16 CHECK constraint definitions retrieved) | `bc_platform_dev` |

### 1.4 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — read-only this session |
| No DDL applied or drafted | ✓ — this is docs-only |
| No MCF metric contracts created | ✓ — M3 + M4 substrates stay empty |
| No certification rows written | ✓ — M3 cert lookup will never find a row until the amendment lands |
| No BCF data touched | ✓ — `concept_registry.*` unchanged |
| No M3 substrate rollback | ✓ — per §7 recommendation; forward amendment only |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |
| No M4 implementation PR opened | ✓ — blocked pending operator decision |

---

## 2. The mismatch — what M4 assumed vs what the live substrate admits

### 2.1 The M4 DBCP's design assumptions (per `e56fc7e`)

The M4 DBCP §9.1 column population matrix assumed every M4 cert row would set:
- `governance_scope = 'mcf'`
- `primitive_type = 'metric_contract_version'`
- `primitive_id = <mcv_uid>`
- `action_code` ∈ {`'metric_create'`, `'metric_transition'`, `'metric_supersede'`}
- `subject_kind` ∈ {`'metric_contract_version'`, `'metric_publication'`, `'metric_supersession'`}
- Row shape mixing the legacy and Registry shapes (primitive set + subject_kind set + governance_scope set)

The M4 DBCP §10 seed INSERTs assumed:
- `contract.framework_policy.scope_code = 'mcf'`
- `contract.operator_confirm_rule.scope = 'mcf'`
- `contract.operator_confirm_rule.transition = 'approved->active'` and `'active->superseded'` (arrow notation)
- `contract.operator_confirm_rule.action_code = 'metric_transition'` and `'metric_supersede'` (semantic confusion: the cert action codes, not the rule enforcement action codes)

### 2.2 What the live substrate actually admits

`contract.certification_record` carries 8 CHECK constraints (live definitions from `pg_query` this session):

| # | Constraint | Live enum / shape | Admits MCF design? |
|---|---|---|---|
| 1 | `certification_record_governance_scope_chk` | `governance_scope IS NULL OR governance_scope = 'registry'` | **NO** — `'mcf'` rejected |
| 2 | `certification_record_action_code_chk` | 28-element closed enum: 21 legacy (`submit_for_review`, `certify`, `return_to_author`, `deprecate`, ...) + 7 BCF Registry (`registry_create`, `registry_transition`, ...) | **NO** — `metric_create` / `metric_transition` / `metric_supersede` not present |
| 3 | `certification_record_primitive_type_chk` | `primitive_type IS NULL OR primitive_type IN ('canonical_field','business_field','business_object')` | **NO** — `'metric_contract_version'` rejected |
| 4 | `certification_record_subject_kind_chk` | `subject_kind IS NULL OR subject_kind IN ('entity','business_concept','characteristic','alias','supersession_proposal')` | **NO** — MCF subject kinds rejected |
| 5 | `certification_record_row_shape_chk` | Exactly two shapes: <br>**Legacy** = `(governance_scope IS NULL AND primitive_type IS NOT NULL AND primitive_id IS NOT NULL AND subject_kind IS NULL AND target_registry_id IS NULL)` <br>**Registry** = `(governance_scope = 'registry' AND subject_kind IS NOT NULL AND primitive_type IS NULL AND primitive_id IS NULL AND panel_run_uid IS NOT NULL)` | **NO** — M4 row has governance_scope='mcf' AND primitive set AND subject_kind set: neither shape |
| 6 | `certification_record_scope_action_chk` | Couples `governance_scope = 'registry'` to `registry_*` action codes, ELSE `governance_scope IS NULL` to non-`registry_*` codes | **NO** — `governance_scope='mcf'` has no matching branch; any M4 row violates this CHECK regardless of action_code |
| 7 | `certification_record_nf1_all_or_none_chk` | All 7 NF1 panel-audit fields NULL OR all 7 non-NULL | Compatible with MCF design (panel-driven path sets all 7; operator-direct sets none) |
| 8 | `certification_record_override_chk` | Override-triplet all-or-nothing with ≥40-char rationale | Compatible with MCF design |

`contract.framework_policy`:

| # | Constraint | Live enum | Admits MCF design? |
|---|---|---|---|
| 9 | `framework_policy_scope_code_chk` | `scope_code IN ('bf_bo','cf','mapping','all','registry')` | **NO** — `'mcf'` rejected |

`contract.operator_confirm_rule`:

| # | Constraint | Live enum | Admits MCF design? |
|---|---|---|---|
| 10 | `operator_confirm_rule_scope_chk` | `scope IN ('bf','bo','cf','mapping','any','registry')` | **NO** — `'mcf'` rejected |
| 11 | `operator_confirm_rule_transition_chk` | `transition IN ('intake_to_draft','draft_to_review','review_to_approved','approved_to_active','any')` | **PARTIAL** — `'approved_to_active'` admissible (DBCP used `'approved->active'` arrow notation — minor wording error) but `'active_to_superseded'` rejected (not in enum) |
| 12 | `operator_confirm_rule_action_chk` | `action_code IN ('require_operator_confirm','route_to_operator_review','block')` | **SEMANTIC MISMATCH** — DBCP populated this column with cert action codes (`'metric_transition'`, `'metric_supersede'`); the column is for the rule's enforcement action (e.g. `'require_operator_confirm'`), not the action being authorized |

**Net:** 10 substrate-level rejections + 1 partial transition enum gap + 1 semantic confusion in the M4 DBCP design.

### 2.3 Verified empirically

The CHECK definitions above were retrieved via:

```sql
SELECT conname, pg_get_constraintdef(oid) AS def
FROM pg_constraint
WHERE conrelid IN (
  'contract.certification_record'::regclass,
  'contract.framework_policy'::regclass,
  'contract.operator_confirm_rule'::regclass
)
  AND contype = 'c'
ORDER BY conrelid::regclass::text, conname;
```

16 rows returned. The text above quotes them verbatim. The live `bc_platform_dev` rejects the M4 design at apply time, not at runtime.

### 2.4 How the design slipped through

| Gate | Where the assumption was made | Why it wasn't caught |
|---|---|---|
| M3 DBCP §3.12 D-12 (`REUSE`) | Working position: shared substrate accepts MCF rows | M3 wrote zero certs at apply time; M3 trigger's cert lookup `SELECT EXISTS` never executed against real data; M3 post-apply verifier exercised triggers but didn't try to write certs |
| M3 apply (PR #103 + PR #104) | Substrate landed; verifier passed | Same — verifier exercised triggers' reject paths, not their accept-via-cert path |
| M4 preflight (`dd54f44`) | §9 cert column matrix written under the cert-reuse assumption | Designer (me) did not pg_query the CHECK constraints; trusted the M3 DBCP's working position |
| M4 DBCP (`ea20be2`) | Same assumption ported into §3.19 D-19, §9, §10 | Same gap |
| M4 DBCP review (P-1..P-13 patches, `a248a4b`) | Catastrophic design issues hunted; line-by-line | Reviewer (me) checked column EXISTENCE (`pg_describe_table`-equivalent) but not CHECK enum values |
| M4 DBCP verification review (P-14..P-21 patches, `e56fc7e`) | Stale wording hunted; coherence verified | Same — no CHECK-enum query |
| M4 implementation pre-read (this session) | First time the Drizzle schemas were opened with CHECK definitions in scope | Found the mismatch at line-1 of the certification-record.ts file |

The lesson: substrate-shape assumptions must be empirically verified against live CHECK constraints (not just column lists) before downstream design depends on them. This is a Foundation gate diagnostic worth recording.

---

## 3. Why M4 must stop

### 3.1 The Foundation gate

Per CLAUDE.md §Foundation Invariant Check:

> **If a fix would violate Foundation, stop and present the violation rather than the fix.**

Implementing M4 against the live substrate would either:

(a) **Fail at apply time** — `psql -v ON_ERROR_STOP=1 -f 06-mcf-cert-authority.sql` would error on the first `INSERT` violating a CHECK; no rows written. The implementation PR's dry-run would catch this if the dry-run inspected CHECK enums, but the dry-run was written under the same assumption and would not.

(b) **Worse: be patched around** — a tempted implementation could add an `ON CONFLICT DO NOTHING` to the seeds, or hand-edit the live CHECK constraints inline ("just add 'mcf' real quick"), or wrap the cert INSERT in a try/catch that swallows the violation. Each of these would compromise Foundation Governance Substrate integrity and propagate the design error into production.

Either path makes the substrate more fragile. The right call is to stop, frame the violation, and ask the operator how to correct the design.

### 3.2 What stays sound

- M3 substrate: live, structurally correct, behaviorally verified. Triggers compose correctly with M2. The state-transition trigger's cert lookup at `→ active` simply doesn't find rows yet because no service writes them. **No safety issue.**
- M4 preflight + DBCP text: still the design record. The decisions D-1..D-20 + patches P-1..P-21 remain valid except for D-12 (M3) / D-19 (M4) which need reversal.
- Tooling discipline: M2 + M3 4-gate pattern + verifier discipline + apply-evidence-PR pattern all worked.

### 3.3 What needs correction

- M3 DBCP D-12 (cert-reuse working position) — **reverse to per-framework sibling**
- M3 trigger's cert-lookup target — **redirect to `mcf.certification_record` sibling**
- M3 supersession's FK target — **redirect from `contract.certification_record` to `mcf.certification_record`**
- M4 DBCP D-19 + §9 + §10 — **rewrite under the sibling-cert design**
- Shared `framework_policy.scope_code` + `operator_confirm_rule.scope` + `operator_confirm_rule.transition` CHECK enums — **extend additively for MCF**
- M4 DBCP §10 operator_confirm_rule.action_code mis-use — **clarify semantic distinction**

---

## 4. Option evaluation

### 4.1 Option A — Extend `contract.certification_record` to admit MCF row shape

Add MCF as a third row shape to `certification_record_row_shape_chk`, extend the action_code / governance_scope / primitive_type / subject_kind / scope_action_chk enums to accept MCF values.

**What it touches:**
- `certification_record_governance_scope_chk` — add `'mcf'` branch
- `certification_record_action_code_chk` — extend 28-element enum to ≥31 by adding `metric_create` / `metric_transition` / `metric_supersede`
- `certification_record_primitive_type_chk` — extend to include `metric_contract_version`
- `certification_record_subject_kind_chk` — extend to include 3 MCF subject kinds
- `certification_record_row_shape_chk` — add a third branch for MCF rows (governance_scope='mcf' + primitive set + subject_kind set + panel_run_uid optional)
- `certification_record_scope_action_chk` — add MCF-scope → MCF-action coupling branch

**Pros:**
- Single cert ledger across BCF + MCF; one audit surface; one dashboard query
- No new table; minimal mcf.* additions
- Aligns with the original "Foundation Governance Substrate" intent (shared)

**Cons:**
- Touches BCF-shared substrate; requires BCF arc coordination (BCF Phase A authority owns the row-shape CHECK; MCF must not unilaterally extend)
- `certification_record_row_shape_chk` already complex (legacy XOR Registry); adding MCF makes it a three-shape discriminated union — increased CHECK complexity
- Every future framework (e.g. some hypothetical M-framework for evaluation) would add another row-shape branch; substrate becomes a multiplexer for all frameworks
- The action_code enum grows unboundedly across frameworks (BCF added 7; MCF wants 3; each future framework adds more)
- Each enum extension is a small DDL but cumulative complexity is high

### 4.2 Option B — Per-framework `mcf.certification_record` sibling table

Create a new `mcf.certification_record` table with MCF-specific column shapes + tight CHECK enums. M3 trigger references the sibling. M3 supersession FK redirects to the sibling. Shared `framework_policy` / `operator_confirm_rule` either also get per-framework siblings OR get extended (this option doesn't specify).

**What it touches:**
- New `mcf.certification_record` table with ~20+ columns (mirror of contract.certification_record minus the legacy-shape columns + plus MCF-specific tight CHECKs)
- M3 trigger's `SELECT EXISTS` clause: `FROM contract.certification_record` → `FROM mcf.certification_record`
- M3 supersession FK: `REFERENCES contract.certification_record(certification_record_id)` → `REFERENCES mcf.certification_record(certification_record_id)`
- M4 cert writer service: writes to `mcf.certification_record` instead of `contract.certification_record`
- M4 PE result table's `fk_mper_cert` FK target: `contract.certification_record` → `mcf.certification_record`
- (Open question) `framework_policy` and `operator_confirm_rule` — per-framework siblings OR extended?

**Pros:**
- Cleanest per-framework separation; MCF substrate fully self-contained
- MCF CHECK enums are tight (only valid MCF values; no XOR row shapes)
- No coordination with BCF for cert-table changes ever
- Easier to evolve (MCF can add subject_kinds, action_codes, etc. without touching BCF)
- Storage / index sizing per-framework

**Cons:**
- Two cert ledgers; audit/dashboard tools need UNION queries to see all certs
- Shared columns (created_at, certifier_sub, NF1 cross-link fields, override discipline columns) duplicated in code/schema
- M3 substrate amendment required (trigger ALTER + FK ALTER)
- If `framework_policy` + `operator_confirm_rule` are also siblings, even more duplication; if shared, this Option folds into Option C

### 4.3 Option C — Hybrid (sibling cert + shared policy/rule extension)

Per-framework sibling for the **cert** table (per Option B); small additive CHECK extensions for the **shared** policy/rule grammar.

**What it touches:**
- **Cert table:** new `mcf.certification_record` sibling. M3 trigger + supersession FK redirected. M4 cert writer + PE result FK target redirected.
- **Policy:** extend `contract.framework_policy_scope_code_chk` to add `'mcf'`. Policy stays shared; one row for `scope_code='mcf'`.
- **Rule:** extend `contract.operator_confirm_rule_scope_chk` to add `'mcf'`. Extend `contract.operator_confirm_rule_transition_chk` to add `'active_to_superseded'` (a generic transition needed for MCF + future frameworks). The `action_code` CHECK does NOT extend — it correctly takes enforcement actions (`require_operator_confirm` etc.), not cert actions. The M4 DBCP's misuse of this column is a documentation bug to fix in the M4 rewrite, not a substrate change.

**Pros:**
- Cert table aligned with semantic reality (cert content is per-framework)
- Policy + rule grammar stays shared infrastructure (the grammar applies across frameworks — additive extension is small, focused, and BCF-neutral)
- M3 amendment is bounded — table + trigger + FK
- BCF coordination needed only for the small policy/rule CHECK extensions (which are additive; don't break BCF rows or behavior)
- Easy operator audit per framework AND across frameworks (mcf.* for MCF-specific; framework_policy / operator_confirm_rule for governance discipline)
- Each future framework gets its own cert table; no row-shape CHECK growth on the shared cert table

**Cons:**
- Two cert ledgers (per Option B)
- BCF arc coordination still needed for policy/rule CHECK extensions (though additive — see §9 D-Correction-7)
- One extra mcf table to maintain

### 4.4 Side-by-side comparison

| Dimension | Option A (extend shared) | Option B (full sibling) | Option C (hybrid) |
|---|---|---|---|
| Cert table | extended in-place | sibling | sibling |
| `framework_policy` | unchanged | sibling or extended (TBD) | extended (additive) |
| `operator_confirm_rule` | unchanged | sibling or extended (TBD) | extended (additive) |
| M3 trigger ALTER | none | required | required |
| M3 supersession FK redirect | none | required | required |
| BCF coordination | required (cert table) | required if policy/rule are siblings; none if extended | required (policy/rule small extension) |
| Future-framework friction | high (each adds row-shape branch) | low (each gets its own cert) | low (each gets its own cert) |
| Audit complexity | low (single ledger) | high (per-framework + cross-framework UNION) | medium (cert per-framework; policy/rule cross-framework via scope_code) |
| Substrate complexity | high (3-shape CHECK + cross-framework enums) | low (per-framework tight CHECKs) | low for cert; small additive for policy/rule |
| M3 ALTER scope | none | trigger + FK | trigger + FK |
| Reversibility | hard (CHECK changes are migrations) | easy per framework | medium (cert sibling reversible; policy/rule extensions are additive) |

---

## 5. Recommendation: Option C (hybrid)

### 5.1 Why Option C

**Cert content is per-framework.** A BCF cert and an MCF cert have genuinely different shapes — different primitive types, different action codes, different subject kinds. The row-shape CHECK that BCF Phase A had to extend once already (legacy XOR Registry) is the brittle outcome of trying to share a single table; adding a third branch makes it worse. The cleanest mapping is per-framework cert tables, where each framework's CHECK enums are tight and the row shape is uniform within the table.

**Policy and rule grammar are genuinely shared.** The discipline of `framework_policy` (`policy_version`, `consensus_requirement_json`, `sampling_rate`, `effective_from`/`effective_to`, etc.) and `operator_confirm_rule` (`transition`, `predicate_ast_json`, `rationale_required`) is universal — they apply identically across frameworks. There's nothing MCF-specific about how a framework_policy is structured; only the `scope_code` value differs. Per-framework siblings here would duplicate infrastructure without semantic benefit.

**The right split is at the framework boundary for content, at the discipline boundary for grammar.** Option C realizes that split cleanly.

### 5.2 Why not Option A

Option A's `certification_record_row_shape_chk` becoming a three-shape discriminated union is a structural complexity smell. BCF Phase A's row-shape CHECK is already non-trivial (uses `IS NOT DISTINCT FROM` for NULL-safety after a corrective migration). Adding MCF as a third shape compounds this. Each future framework (a hypothetical evaluation framework, a hypothetical tenancy framework, etc.) would add another branch. The pattern doesn't scale.

The cert table is the wrong place for shared substrate. The framework_policy + operator_confirm_rule tables are the right place.

### 5.3 Why not Option B (full sibling)

Option B's full per-framework sibling pattern (cert + policy + rule all duplicated) over-fragments. The `framework_policy` and `operator_confirm_rule` tables encode discipline grammar that is genuinely the same across frameworks — sampling rates, consensus requirements, predicate ASTs, transition enums. Per-framework duplication would create three places to author the same rule grammar, with attendant drift risk.

The hybrid (Option C) preserves shared discipline grammar while letting framework-specific cert content live in its own table.

### 5.4 Why this is the right call given M3 is already live

M3 substrate is live + dormant. No cert writes have ever been attempted. The M3 amendment is therefore forward-compatible:
- `CREATE OR REPLACE FUNCTION mcf.fn_mcv_state_transition_check()` — idempotent ALTER of the trigger function body
- `ALTER TABLE mcf.metric_supersession DROP CONSTRAINT fk_mcs_cert; ALTER TABLE mcf.metric_supersession ADD CONSTRAINT fk_mcs_cert FOREIGN KEY (certification_record_id) REFERENCES mcf.certification_record(certification_record_id) ON DELETE RESTRICT;` — atomic FK redirect, safe against zero existing rows
- `CREATE TABLE mcf.certification_record (...);` — new table

No rollback needed. No data migration needed. M3 substrate stays applied; only the function body and FK target change.

---

## 6. Specific amendments required (Option C)

### 6.1 M3 DBCP D-12 reversal

**Current text** (M3 DBCP §3.12):
> **Decision:** REUSE. MCF writes rows into `contract.certification_record` scoped by MCF `action_code` values (`metric_create`, `metric_transition`, `metric_supersede`). No `mcf.certification_record` sibling.

**Amendment text:**
> **Decision (reversed per cert substrate correction preflight, 2026-05-26):** PER-FRAMEWORK SIBLING. MCF writes rows into a new `mcf.certification_record` table (M3 amendment ships the DDL). `framework_policy` and `operator_confirm_rule` remain shared (per MCF §17.3 + Option C); their CHECK enums are extended additively for `scope='mcf'`. The original "REUSE" position was structurally incompatible with the live `certification_record_row_shape_chk` and surrounding scope/action couplings — see correction preflight §2 for the 10 specific blockers.

The reversal is recorded as a formal amendment to M3 DBCP; the original D-12 text is preserved with a "REVERSED" annotation pointing at the amendment DBCP.

### 6.2 M3 live trigger lookup target ALTER

**Current trigger body** (`bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql` lines 113-127, applied to `bc_platform_dev`):

```sql
-- approved → active: matching cert must exist (with primitive_type guard)
IF NEW.governance_state_code = 'active' THEN
  SELECT EXISTS (
    SELECT 1 FROM contract.certification_record cr
    WHERE cr.primitive_type  = 'metric_contract_version'
      AND cr.primitive_id    = NEW.metric_contract_version_uid
      AND cr.action_code     = 'metric_transition'
      AND cr.from_state_code = 'approved'
      AND cr.to_state_code   = 'active'
      AND (cr.is_archived_after IS NOT TRUE)
  ) INTO has_active_cert;
  ...
END IF;
```

**Amendment** — change FROM clause to `mcf.certification_record cr`. All other predicates (`primitive_type`, `primitive_id`, `action_code`, `from_state_code`, `to_state_code`, `is_archived_after`) remain valid for the sibling table because the sibling's columns are the same names. Applied via `CREATE OR REPLACE FUNCTION mcf.fn_mcv_state_transition_check() ...` — idempotent.

The supersession check inside the same trigger (`IF NEW.governance_state_code = 'superseded' THEN ... JOIN mcf.metric_supersession ...`) is unaffected — it JOINs `mcf.metric_supersession` directly, not the cert table.

### 6.3 `mcf.metric_supersession.certification_record_id` FK redirect

**Current FK** (M3 DBCP §5.3 + applied DDL `05-mcf-lifecycle-substrate.sql` lines 426-427):

```sql
CONSTRAINT fk_mcs_cert FOREIGN KEY (certification_record_id)
  REFERENCES contract.certification_record(certification_record_id) ON DELETE RESTRICT
```

**Amendment** — DROP the FK + ADD redirected:

```sql
ALTER TABLE mcf.metric_supersession DROP CONSTRAINT fk_mcs_cert;
ALTER TABLE mcf.metric_supersession
  ADD CONSTRAINT fk_mcs_cert FOREIGN KEY (certification_record_id)
  REFERENCES mcf.certification_record(certification_record_id) ON DELETE RESTRICT;
```

Safe because `mcf.metric_supersession` has 0 rows (verified at M3 apply closeout) — no existing FK references to migrate.

Drizzle schema for `mcf.metric_supersession` (`bc-core/src/database/schema/mcf/metric-supersession.ts`) currently has a note that "Cross-schema FKs are DDL-only" — the Drizzle column for `certificationRecordId` is `notNull()` with no Drizzle-level FK. The M3 amendment DDL changes the FK target; the Drizzle file gets an updated comment but no Drizzle-level FK is added (per the existing pattern).

### 6.4 M4 DBCP D-19 / §9 / §10 amendments

**D-19 reversal:** mirror the M3 D-12 reversal — change from "REUSE — confirms M3 D-12" to "PER-FRAMEWORK SIBLING — confirms M3 amendment".

**§9 cert column matrix rewrite:** the matrix becomes simpler because `mcf.certification_record` has a single row shape, not the BCF-shared 3-shape:

| Column | metric_create | metric_transition | metric_supersede |
|---|---|---|---|
| `certification_record_id` | auto | auto | auto |
| `primitive_type` | `'metric_contract_version'` (CHECK-bound) | same | same |
| `primitive_id` | new MCV uid | activating MCV uid | predecessor MCV uid |
| `action_code` | `'metric_create'` (CHECK-bound) | `'metric_transition'` | `'metric_supersede'` |
| `from_state_code` | NULL | `'approved'` | `'active'` |
| `to_state_code` | `'draft'` | `'active'` | `'superseded'` |
| `is_archived_after` | NULL | NULL | NULL |
| `gate_results_json` | from input | from input | from input |
| `advisory_verdicts_json` | from input or `[]` | from input | from input |
| `override_gate_code` / `override_rationale_text` / `override_followup_task_uid` | from input or NULL | same | same |
| `certifier_sub` / `certifier_role_at_action` / `certifier_email` | from input | from input | from input |
| `supersedes_primitive_id` | NULL | NULL | predecessor MCV uid |
| `created_at` | auto | auto | auto |
| `panel_run_uid` / `prompt_version` / `model_identity_json` / `input_hash` / `policy_version` / `sampling_status` / `grounding_check_result` | from input | from input | from input |
| `subject_kind` | `'metric_contract_version'` | `'metric_publication'` | `'metric_supersession'` |

**Removed columns** (not on the sibling): `governance_scope` (single-table; always implicitly `'mcf'`); `target_registry_id` (BCF-specific Registry Model A field). The sibling table simply doesn't have them.

**§10.1 operator_confirm_rule seeds:** the seeds need 3 corrections:
- `scope = 'mcf'` (admissible after CHECK extension)
- `transition = 'approved_to_active'` and `'active_to_superseded'` (underscore notation matches the enum; the second value requires the transition CHECK extension)
- `action_code = 'require_operator_confirm'` (the enforcement action — NOT `'metric_transition'` / `'metric_supersede'`; M4 DBCP §10.1 was wrong; semantic correction in the rewrite)

**§10.2 framework_policy seed:** `scope_code = 'mcf'` admissible after the CHECK extension.

**§10 new sub-section** on the rule.action_code vs cert.action_code distinction: explicit documentation that `contract.operator_confirm_rule.action_code` is the enforcement directive (the rule says "do this when matched"), while the cert action codes (`metric_create`, etc.) live on `mcf.certification_record.action_code` (the cert says "this is the act being authorized").

### 6.5 M4 dry-run + verifier assumption updates

**M4 dry-run script:**
- New precondition: `mcf.certification_record` table present (shipped by M3 amendment; M4 apply requires it)
- New precondition: `contract.framework_policy.scope_code` CHECK admits `'mcf'` (extended by M3 amendment or M4 apply — sequencing TBD; M3 amendment is cleaner)
- New precondition: `contract.operator_confirm_rule.scope` CHECK admits `'mcf'` (same)
- New precondition: `contract.operator_confirm_rule.transition` CHECK admits `'active_to_superseded'` (same)
- Existing precondition: `mcf.certification_record` row count = 0 (clean slate before M4 cert writer ships)

**M4 post-apply verifier:**
- New structural check: synthetic cert row INSERT into `mcf.certification_record` succeeds (validates the CHECK enums admit the M4 values)
- Existing behavioral checks (#8-13): all unchanged
- Check #11 `activateMetric`: cert written to `mcf.certification_record`, not `contract.certification_record`

### 6.6 Shared `framework_policy` + `operator_confirm_rule` CHECK extensions

**`contract.framework_policy_scope_code_chk` extension:**

```sql
ALTER TABLE contract.framework_policy
  DROP CONSTRAINT framework_policy_scope_code_chk;
ALTER TABLE contract.framework_policy
  ADD CONSTRAINT framework_policy_scope_code_chk
  CHECK (scope_code IN ('bf_bo','cf','mapping','all','registry','mcf'));
```

Additive — every existing row satisfies the new CHECK (the existing enum is a subset of the new).

**`contract.operator_confirm_rule_scope_chk` extension:**

```sql
ALTER TABLE contract.operator_confirm_rule
  DROP CONSTRAINT operator_confirm_rule_scope_chk;
ALTER TABLE contract.operator_confirm_rule
  ADD CONSTRAINT operator_confirm_rule_scope_chk
  CHECK (scope IN ('bf','bo','cf','mapping','any','registry','mcf'));
```

Additive.

**`contract.operator_confirm_rule_transition_chk` extension:**

```sql
ALTER TABLE contract.operator_confirm_rule
  DROP CONSTRAINT operator_confirm_rule_transition_chk;
ALTER TABLE contract.operator_confirm_rule
  ADD CONSTRAINT operator_confirm_rule_transition_chk
  CHECK (transition IN ('intake_to_draft','draft_to_review','review_to_approved','approved_to_active','active_to_superseded','any'));
```

Additive — `'active_to_superseded'` is generic enough to be useful for any future framework with a supersession path; not MCF-specific.

**`contract.operator_confirm_rule_action_chk`** — NO extension. The current 3 values (`require_operator_confirm`, `route_to_operator_review`, `block`) are correct and complete. The M4 DBCP's misuse of this column is a documentation error to fix in the rewrite.

### 6.7 Drizzle schema changes scope

Per Option C, Drizzle schemas affected:

| File | Change |
|---|---|
| `bc-core/src/database/schema/mcf/certification-record.ts` (new) | Drizzle pgTable for `mcf.certification_record` |
| `bc-core/src/database/schema/mcf/metric-supersession.ts` | Update the cross-schema FK comment to reflect redirect to `mcf.certification_record` (Drizzle still doesn't model this FK; DDL-only) |
| `bc-core/src/database/schema/mcf/index.ts` | Re-export `certificationRecord` |
| `bc-core/src/database/schema/contract/framework-policy.ts` | Update `framework_policy_scope_code_chk` enum to include `'mcf'` |
| `bc-core/src/database/schema/contract/operator-confirm-rule.ts` | Update `operator_confirm_rule_scope_chk` to include `'mcf'`; update `operator_confirm_rule_transition_chk` to include `'active_to_superseded'` |

No changes to existing `mcf/metric-contract.ts`, `mcf/metric-contract-version.ts`, etc.

---

## 7. M3 rollback assessment

### 7.1 Recommendation: NO rollback

M3 substrate is live + dormant. All MCF tables have 0 rows (verified at M3 apply closeout `d1f67d0`; verified again at M4 implementation pre-read). No cert has ever been written to `contract.certification_record` with MCF action codes (the M3 state-transition trigger's cert-lookup hasn't fired against real data because no service writes the cert).

Forward amendment is safer:

| Forward amendment step | Operation | Safety |
|---|---|---|
| Create `mcf.certification_record` table | `CREATE TABLE mcf.certification_record (...)` | Idempotency-safe via dry-run precondition (table absent before apply) |
| ALTER trigger function | `CREATE OR REPLACE FUNCTION mcf.fn_mcv_state_transition_check() ...` | Idempotent by Postgres semantics |
| Redirect FK | `ALTER TABLE mcf.metric_supersession DROP CONSTRAINT fk_mcs_cert; ALTER TABLE ... ADD CONSTRAINT fk_mcs_cert ...` | Safe — 0 existing rows in `mcf.metric_supersession`; FK validation succeeds vacuously |
| Extend `contract.framework_policy_scope_code_chk` | `ALTER TABLE ... DROP CONSTRAINT ...; ALTER TABLE ... ADD CONSTRAINT ...` | Additive — every existing row satisfies new CHECK |
| Extend `contract.operator_confirm_rule_scope_chk` | same | Additive |
| Extend `contract.operator_confirm_rule_transition_chk` | same | Additive |

### 7.2 Why rollback would be worse

Rolling back M3 means:
- `DROP TRIGGER trg_mcf_mcv_state_transition` + 6 sibling triggers
- `DROP FUNCTION` × 7
- `DROP TABLE mcf.metric_supersession`
- `DROP TABLE mcf.metric_contract_revision`

— then re-running M3 with the amended trigger body + new FK target + new sibling table. This is more substrate churn, more apply gates, and operationally equivalent to forward amendment with greater risk.

### 7.3 Why forward amendment is complete

Per §6.7, the Drizzle schemas update to reflect the new structure. The DDL ships ALTERs (not DROP/RECREATE). The live substrate's M3 triggers + tables remain physically present throughout the amendment. The amendment's post-apply verifier confirms:
- New `mcf.certification_record` table present + correct shape
- M3 trigger function body now references `mcf.certification_record` (verify via `pg_get_functiondef`)
- `mcf.metric_supersession.fk_mcs_cert` FK target = `mcf.certification_record` (verify via `pg_constraint`)
- Shared CHECK extensions present (verify via `pg_get_constraintdef`)
- Pre-existing M3 behavioral tests (positive + negative trigger exercises) still PASS — confirms no regression

---

## 8. Sequencing recommendation

### 8.1 Nine-gate sequence

| # | Gate | Type | Authority needed | Deliverable |
|---:|---|---|---|---|
| 1 | **This preflight** | docs-only | Operator opens correction gate | This document |
| 2 | **M3 amendment DBCP** | docs-only | Operator authorizes after preflight review | New doc: `metric-context-framework-m3-cert-amendment-dbcp.md` — specifies exact DDL ALTERs + new `mcf.certification_record` table + Drizzle updates + amended D-12 + dry-run/verifier design |
| 3 | **M3 amendment implementation PR** | bc-core code | Operator authorizes after DBCP review | Branch from `a6a3e64`; DDL file `docker/redesign/05a-mcf-cert-amendment.sql` (or numbering scheme TBD); new Drizzle schema `mcf/certification-record.ts`; updates to `mcf/metric-supersession.ts` comment + `contract/framework-policy.ts` CHECK + `contract/operator-confirm-rule.ts` CHECK; dry-run + post-apply verifier scripts; **NO DB APPLY** |
| 4 | **M3 amendment live DDL apply** | DB apply | Operator-authorized DCP gate; same discipline as M2 + M3 apply gates | psql apply against `bc_platform_dev`; post-apply verifier exit 0 |
| 5 | **M3 amendment evidence PR** | bc-core artifacts | Operator authorizes | Audit artifacts from #4 committed under `scripts/audit-output/`; closeout doc in bc-docs-v3 |
| 6 | **M4 DBCP rewrite** | docs-only | Operator authorizes | Substantive rewrite of `metric-context-framework-m4-lifecycle-certification-dbcp.md` reversing D-19, rewriting §9 cert matrix, correcting §10 seed semantics, updating dry-run/verifier assumptions per §6.5 |
| 7 | **M4 implementation PR** | bc-core code | Operator authorizes per rewritten DBCP | Per the rewritten DBCP; **NO DB APPLY** |
| 8 | **M4 DDL apply** | DB apply | Operator-authorized DCP gate | As designed in rewritten DBCP |
| 9 | **M4 evidence PR** | bc-core artifacts | Operator authorizes | As designed in rewritten DBCP |

### 8.2 Could gates 2 and 6 be combined?

Possibly — both are docs-only DBCPs and they cross-depend. A combined "M3 amendment + M4 DBCP rewrite" doc gate would surface design coherence in one place. But the natural split (M3 amendment is about substrate; M4 rewrite is about service contract on top of amended substrate) maps to two distinct concerns. **Operator decision D-Correction-2** captures this choice.

### 8.3 Could gates 4 and 7 be combined into a single apply session?

No. The M3 amendment apply must land BEFORE the M4 implementation PR is opened, because M4's dry-run script checks that the new `mcf.certification_record` table exists + the shared CHECK extensions are in place. Compressing them risks the M4 PR being authored against a non-applied amendment.

### 8.4 Estimated calendar

If operator decisions are quick:
- Gate 2 (M3 amendment DBCP) — one session
- Gate 3 (M3 amendment PR) — one session
- Gate 4 (M3 apply) — short session, operator approval required mid-flight
- Gate 5 (M3 evidence) — one session
- Gate 6 (M4 rewrite) — one session
- Gate 7 (M4 PR) — one session (larger)
- Gate 8 (M4 apply) — short session
- Gate 9 (M4 evidence) — one session

Eight follow-on sessions. Comparable in shape to the M2 + M3 arcs combined.

---

## 9. Operator decisions required before M3 amendment DBCP opens

| # | Decision | Recommendation |
|---:|---|---|
| D-Correction-1 | **Option A / B / C** for cert substrate correction | **C (hybrid)** per §5; rationale: cert content is per-framework, policy/rule grammar is shared |
| D-Correction-2 | Combine gates 2 + 6 (M3 amendment DBCP + M4 DBCP rewrite) into one doc, or keep separate | Keep separate (per §8.2) — M3 substrate concerns and M4 service-contract concerns are distinct enough that one-per-doc aids review |
| D-Correction-3 | M3 rollback or forward amendment | **Forward amendment only** (per §7) — substrate live + dormant; forward is safe and complete |
| D-Correction-4 | Shared CHECK extensions scope — confirm only `framework_policy.scope_code` + `operator_confirm_rule.scope` + `operator_confirm_rule.transition` need extension, NOT `operator_confirm_rule.action_code` | **Confirmed per §6.6** — `action_code` enum is correctly typed (enforcement actions); the M4 DBCP's misuse is a doc bug, not a substrate gap |
| D-Correction-5 | Ownership of `mcf.certification_record` table — M3 amendment ships it, or M4 ships it | **M3 amendment ships it** — because the M3 trigger references it; without the sibling table, the M3 trigger's ALTER would fail apply |
| D-Correction-6 | Whether the M4 DBCP rewrite also reverses + amends the operator_confirm_rule.action_code semantic confusion documented in §10 | **YES** — the rewrite explicitly clarifies the distinction (cert.action_code = act being authorized; rule.action_code = enforcement directive). Add a §10.5 subsection on this distinction |
| D-Correction-7 | BCF arc coordination for shared CHECK extensions — does this require a BCF DBCP sign-off, or can MCF amendment proceed unilaterally on additive enum extensions | **Recommend coordinated** — even though the extensions are additive (don't break BCF rows or behavior), `contract.framework_policy` + `contract.operator_confirm_rule` are BCF-owned per their build plan annotations (BCF requirements Ch.7). Operator pings BCF arc maintainer (or maintains own ownership across both arcs) before the M3 amendment apply. Light-touch (one-line ack), not a separate DBCP. |

### 9.1 Cross-framework substrate ownership note

`contract.certification_record` + `contract.framework_policy` + `contract.operator_confirm_rule` are Foundation Governance Substrate — shared between BCF and MCF per MCF requirements §17.3. Today, BCF arc authored their initial shape and Phase A extended them; MCF would extend them again in Option C.

There's an open question whether the "Foundation Governance Substrate" should formally have a separate ADR governing its evolution (rather than being implicitly BCF-owned with MCF as a downstream consumer). This is broader than this correction preflight; the right move is to note the question and proceed pragmatically (D-Correction-7 light-touch coordination) without blocking on it.

---

## 10. What stays closed in this preflight

| | Status |
|---|---|
| M3 amendment DBCP design | Operator authorizes next; not opened by this preflight |
| M3 amendment implementation PR | Pending DBCP |
| M3 amendment DDL apply | Pending PR |
| M3 amendment evidence PR | Pending apply |
| M4 DBCP rewrite | Pending M3 amendment landing |
| M4 implementation PR | BLOCKED until M3 amendment + M4 rewrite |
| M4 DDL apply | Blocked |
| M4 evidence PR | Blocked |
| M5+ gates (panel substrate, formula AST, package signature, fixture, verifier, panel impl, etc.) | All downstream of M4; blocked |
| MCF metric contract authoring | Blocked (no path to publish) |
| BCF data touches | None |
| `bc-postgres` MCP `allow_write` widening | None |
| bc-core code edits this preflight | None |
| M3 substrate rollback | NOT recommended (per §7) |

---

## 11. Recommended next gate

### 11.1 Open M3 amendment DBCP

**Next gate: open the M3 amendment DBCP (docs-only).** Deliverable: a new doc at `bc-docs-v3/docs/implementation/metric-context-framework-m3-cert-amendment-dbcp.md` (or similar naming) specifying:

- Resolution of D-Correction-1 through D-Correction-7
- Exact `mcf.certification_record` table schema (columns, CHECKs, FKs, indexes, COMMENTs)
- Exact M3 trigger function ALTER (the CREATE OR REPLACE FUNCTION body)
- Exact `mcf.metric_supersession.fk_mcs_cert` FK redirect DDL
- Exact shared-table CHECK extension DDL (3 ALTERs)
- Drizzle schema additions/modifications per §6.7
- Dry-run script preconditions (≥7 preconditions)
- Post-apply verifier checks (≥12 including structural + behavioral)
- Rollback DDL companion (FK redirect back; trigger restore; sibling table DROP; CHECK extension reversal — though forward-only is the discipline)
- Apply order discipline (per M3 DBCP §11 pattern)
- Risk + stop-conditions assessment
- 5+ operator approvals (O-Amendment-1..O-Amendment-N)

### 11.2 Why this preflight first

The preflight establishes the problem framing + option set + recommendation + cross-gate impact. Without this record, the M3 amendment DBCP would have to re-derive the same framing. Splitting the preflight from the DBCP gives the operator a clean review point before substantive design.

### 11.3 What does NOT happen until the operator authorizes the M3 amendment DBCP

- No bc-core branches
- No DDL drafted
- No M4 DBCP edits
- No `mcf.certification_record` substrate work
- No CHECK extension drafted
- No verifier scripts written
- No commits beyond this preflight commit

---

## Document verification

- **All 11 required sections present** (§1 Scope and grounding; §2 The mismatch; §3 Why M4 must stop; §4 Option evaluation A/B/C; §5 Recommendation Option C; §6 Specific amendments; §7 M3 rollback assessment; §8 Sequencing recommendation; §9 Operator decisions; §10 What stays closed; §11 Recommended next gate).
- **10 specific CHECK-constraint blockers enumerated** in §2.2 with live constraint definitions retrieved via `pg_query`.
- **3 resolution options evaluated** in §4 with side-by-side comparison.
- **Option C recommended** with explicit rationale in §5 (4 sub-sections).
- **6 amendment areas specified** in §6 covering M3 DBCP D-12 / M3 trigger / M3 supersession FK / M4 DBCP D-19+§9+§10 / M4 dry-run+verifier / shared CHECK extensions.
- **M3 rollback assessment** in §7 — recommendation: NO rollback; forward amendment only.
- **9-gate sequencing** in §8 with combinability + ordering rationale.
- **7 operator decisions** enumerated in §9 with recommendations.
- **No code changes, no DDL applied, no MCF metric contracts created, no certification rows written, no BCF data touched, no bc-core file edits.** Doc-only correction preflight commit to bc-docs-v3 main.
- **M3 substrate stays unaffected** — live, dormant, no rollback.
- **Foundation gate discipline followed** — stopped M4 implementation, presented violation per CLAUDE.md.
