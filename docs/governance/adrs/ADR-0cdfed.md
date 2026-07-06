---
uid: DEC-0cdfed
title: "Drift Visibility & Chapter Conformance — citation lint, loud-warn, structured drift inventory, anti-revisionism gate"
description: "Lock the discipline that keeps v3 chapters and runtime in agreement: (1) operationalize each chapter's prose Drift Inventory as structured audit checks; (2) convert silent-green code paths to loud-warn at every observed silence point; (3) require @chapter citation tags on chapter-governed code units, lint-enforced; (4) PR template forces explicit doc-reconciliation acknowledgment; (5) chapter PRs that change structural contracts (gate counts, schema shapes, decision counts) require ADR citation — prevents doc revisionism under code-precedence."
status: decided
date: 2026-04-28T08:30:55.925Z
project: bc-core
domain: governance
subdomain: documentation-discipline
focus: drift-visibility-and-conformance
---

# Drift Visibility & Chapter Conformance — citation lint, loud-warn, structured drift inventory, anti-revisionism gate

## Context

D381 → D382 surfaced multiple platform issues that are all the same shape: documented chapter ↔ runtime code disagreement. CR-QG-RDR-002.3 says config_present required; 9 active flavors have config_json=NULL. C2 governance check says draft contracts fail; 576 MCs ignore it. OC chapter says identity_fields = source-table PK; OCs declare insufficient fields. Each is a "local fix, global violation" pattern: someone fixed Part A correctly for Part A, violating a contract Part B silently relied on. The worse failure mode that compounds this: under deadline, "syncing the doc to match wrong code" becomes the path of least resistance, codifying the violation as new truth. Without governance, original intent is lost forever. D382 fixes the specific cases. D383 locks the discipline that prevents recurrence and detects new instances at the boundary, not by chance. Five layers, sized for incremental rollout: (1) drift visibility (operationalize chapter Drift Inventory sections + loud-warn at silence points); (2) chapter ↔ code coupling (citation lint + cross-check); (3) review-time enforcement (PR template); (4) anti-revisionism gate (chapter structural changes require ADR citation); (5) longer-term: schema-first authoritative contracts (flagged for future work, not this ADR).

# Drift Visibility & Chapter Conformance

## The two-layer problem

D381 → D382 surfaced enough chapter-vs-runtime drift to make the pattern undeniable. Every drift case shares two failure modes:

**Layer 1 — Drift accumulates silently.** Code fixes in Part A violate contracts Part B silently relies on. Both layers continue to operate, neither knows the other's expectation has changed. "Local fix, global violation."

**Layer 2 — Documentation revisionism.** Eventually someone spots the disagreement. Under deadline pressure, the cheaper move is to *update the chapter to match the wrong code* rather than fix the code to match the (correct) chapter. Original intent is lost; future engineers can't distinguish "this is what we always wanted" from "this is what we settled for".

D382 fixes the specific cases we've already found. D383 closes both failure modes structurally so new instances are caught at the boundary, not by chance.

## Decisions

### D-1: Operationalize Chapter Drift Inventory sections

Every v3 authoritative chapter today has a `## Drift Inventory` table describing known gaps between the documented procedure and the as-built runtime. Today these are prose. They become **structured audit checks**: each entry is `{ chapter, drift_id, check_function_ref, severity, expected_remediation_task_uid }`. A nightly (or per-deploy) audit runs every check against real data and emits a structured drift report. The drift count is tracked in DevHub as a time series; growth is a deploy-blocking signal at a configurable threshold.

The text remains in the chapter as the human-readable form. The structured frontmatter is the machine-readable form. Both stay in sync via a CI test that parses the chapter and compares the two.

### D-2: Convert silent-green to loud-warn at every observed silence point

Every code path that today produces "looks green" output despite known input-mismatch conditions emits a `LOG WARN` (or structured event with severity=warn). Examples surfaced in D381 → D382:

- `canonical_resolution.groups=0 with bindingsConsidered>0` → WARN
- Reader executor `keyFields=[]` AND `OC.identity_semantics.identity_fields=[]` at executor init → WARN (or throw per D382 D-2)
- Admission `source_key.length === 1 && key === '_entity'` → WARN
- ChainStatusService verdict='complete' for a chain whose underlying readers/OCs have non-active status → WARN

Logs feed DevHub activity_log so audit trails persist. Doesn't change behavior — just makes drift audible.

### D-3: Citation lint — chapter-governed code units must cite their chapter

Every TypeScript file under known chapter-governed paths (`bc-core/src/registry/gates/`, `bc-core/src/boundary/`, `bc-core/src/schema-provisioner/`, etc.) carries a top-of-file JSDoc tag pointing at a v3 chapter and section:

```ts
/**
 * @chapter onboarding/reader-creation.md#CR-QG-RDR-002
 * @cite-lock 2026-04-28  // last reviewed against the chapter on this date
 */
```

Two ESLint custom rules enforce:
- **`bc-core/require-chapter-citation`**: every file under chapter-governed paths MUST have `@chapter` tag. PR fails lint if added without citation.
- **`bc-core/citation-resolves`**: a build-time script (`npm run docs:verify`) walks every `@chapter` citation and verifies the file exists AND the anchor (`#CR-QG-RDR-002`) actually exists in the file's headings. Broken cite → CI fails.

Initial rollout: scope the rules to NEW files first (allow legacy files to remain uncited until backfilled), then ratchet the path glob to require citations on touched files.

### D-4: PR template — explicit doc-reconciliation acknowledgment

Every PR description carries a required section:

```
## Documentation reconciliation
Choose one:
- [ ] This PR doesn't touch chapter-governed code
- [ ] I read the relevant chapters (list them) and my change conforms to them
- [ ] My change *requires* a chapter update (link the chapter PR or the ADR authorizing the intent change)
```

GitHub Actions enforces presence of this section. PRs without it are blocked. The mechanism makes the engineer pause before "local fix, global violation" — they have to type out which chapters they consulted, which forces the consultation.

### D-5: Anti-revisionism gate on chapter PRs

Every chapter file has structured frontmatter declaring its **structural contracts** — gate counts, decision counts, required body keys, etc.:

```yaml
---
id: reader-creation
status: authoritative
gates:
  - { id: CR-QG-RDR-001, count: 4, last_changed_by: DEC-d228ec }
  - { id: CR-QG-RDR-002, count: 4, last_changed_by: DEC-d228ec }
  - { id: CR-QG-RDR-003, count: 7, last_changed_by: DEC-d228ec }
---
```

A CI rule on chapter PRs: if a change modifies any structural-contract field (gate count, decision count, schema-key list, etc.), the commit MUST include either:
- A reference to an ADR UID that authorized the intent change (`adr_ref: DEC-xxxxxx`), OR
- A label `chapter-cleanup-only` on the PR (audit-traced; reviewer must approve)

PRs that change a gate count without ADR citation fail CI. Caps the "doc revisionism" surface — you can't silently update the chapter to match wrong code; you have to either justify the intent change via an ADR or explicitly mark cleanup-only with reviewer approval.

This is the strongest of the five mechanisms because it directly addresses the worst failure mode (codifying disagreement as new truth).

## Sequencing

| # | Decision | Cost | Leverage | Order |
|---|---|---|---|---|
| D-1 | Operationalize Drift Inventory | Small | Medium | first |
| D-2 | Loud-warn at silence points | Small | High | first |
| D-3 | Citation lint | Medium | Medium | second |
| D-4 | PR template doc-reconciliation | Small | High | second |
| D-5 | Anti-revisionism CI gate | Medium | Highest | third |

D-1 and D-2 ship together — they make existing drift visible and audible without behavior change. D-3 and D-4 ship next — they enforce chapter ↔ code coupling for new work. D-5 ships last and is the most important — it's the structural defense against the worst failure mode.

## Out of scope (flagged for future)

**Schema-first authoritative contracts.** The deeper structural antidote to "local fix, global violation" is making the schema (not prose) the authority. Code generates from schema; chapters reference schema; runtime validates against schema. This pattern is partially in place via `bc-core/src/registry/meta-schemas/*.schema.json` for OC/CC/MC body shapes. Extending this — auto-generated chapter sections from schema, schema-driven type generation, etc. — is a substantially larger initiative. D383 doesn't propose it; D-1 through D-5 are tractable first steps that don't require it.

## Consequences

- D-2 will produce noisy logs initially. The log volume itself is the drift inventory in motion. Spike → ratchet down as drift gets fixed.
- D-3's citation requirement on touched files (not new files) means drift surfaces gradually as files are edited. Whole-codebase backfill is its own task; not blocking.
- D-5's PR gate adds friction to chapter editing. That's the point. Friction prevents revisionism. Reviewer-approved cleanup-only label is the escape hatch for genuinely cosmetic edits.
- The 576 chain_complete count, after D382 D-4 lands, will drop to an honest number. D383 D-1 makes that drop visible as a tracked drift metric.
- New chapters land with frontmatter requirements on day one — D-5 doesn't apply retroactively but does retroactively for any chapter PR that lands after D-5 ships. Gate counts on existing chapters get backfilled by chapter-conformance audits.

## Tracking

D-1 through D-5 each become a separate DevHub task linked to this ADR. Implementation lives across bc-core (lint rules, audit jobs, log instrumentation), bc-docs-v3 (frontmatter shape, chapter cleanup), and platform CI (GitHub Actions, ESLint, markdown verification).

## Drift cases observed during D381 Phase 1 chain proving (2026-04-28)

While driving sandbox1's AR chain end-to-end, eight more silent-failure modes were uncovered, each fitting D-2's "loud-warn at silence points" pattern. All eight are fixed in bc-core commit `5bd766d`; they're recorded here as canonical examples for the Drift Inventory work in D-1 to operationalize.

Each case shares the same shape: a layer's contract changed, downstream consumers weren't updated, both sides operate "successfully" without surfacing the disagreement. Detection happens by accident, often layers later, when symptoms manifest as zero records or "not found" errors.

| # | Silent-failure surface | Layer | Effect |
|---|------------------------|-------|--------|
| 1 | TypedFactWriter swallows PG error on `""` → date column; returns `db_error` without throwing | schema-provisioner | source admissions appeared accepted but no fact row written; downstream resolver returns null payload |
| 2 | `resolveField` is case-sensitive; FactReader returns lowercase columns, OC field_map uses SAP case | canonical-resolution | merged CO payload silently missing every BF; D365 fiscal gate rejects 100% with `missing_posting_date` |
| 3 | `FiscalCalendarService.getTenantDbName` looks up `tenants.id` (UUID), runtime callers pass slug | registry/fiscal-calendar | every fiscal resolution fails with PG-side query error; logged as `fiscal_calendar_resolution_error` |
| 4 | `reader-runtime` falls back to hardcoded `'demo-selenite'` when caller omits tenantId | reader-runtime | requests for tenant X silently write to demo-selenite's DB (or fail when that DB doesn't exist) |
| 5 | `ReadinessEvaluationDispatcher` reads `boundary.canonical_object` (table removed in D369 M4.2e) | metric-dispatcher | every dispatch errors with `Failed query`; dispatcher reports `evaluated N — accepted=0 rejected=0`; UI surface looks "running" |
| 6 | `writeProgressionCanonical` is fire-and-forget; following `createCanonicalObject` writes fact row with FK to canonical_evaluation that hasn't been inserted yet | canonical-resolution | every CO except the first ~2 hits FK-violation, dropped silently by typed-fact-writer's catch-and-warn; downstream metric dispatcher finds zero COs |
| 7 | `canonicalObjectId = idService.generate()` instead of `evaluationId`; downstream consumers (FactReader, dispatcher, evaluation.repository) all assume `canonicalObjectId === canonicalEvaluationId` per the M4.2b "identity rule" | canonical-resolution | dispatcher loads CO IDs from progression, looks up by fact_id → not found → `Canonical object N not found` rejection cascade |
| 8 | tenant.contract_binding for canonical contracts not propagated; SP reconcile sees only MC bindings → no fact.co_*_v* tables provisioned | schema-provisioner | CO writer returns `missing_table` (silent skip); resolver chain "succeeds"; metric eval can't load anything |

Common shape: each emits success at its own layer's exit boundary. Failure surfaces multiple layers later, usually as zero-records-found or "not found" — phenotype that masks the upstream root cause.

These eight cases reinforce why D-2 (loud-warn) and D-5 (anti-revisionism) are the highest-leverage of the five mechanisms in this ADR. Cases 5, 6, 7 in particular show the failure mode where a refactor (D369 M4.2e envelope→progression) shipped with the happy path but missed cross-layer assumptions; an end-to-end chain run on a fresh tenant was the only signal that surfaced them.
