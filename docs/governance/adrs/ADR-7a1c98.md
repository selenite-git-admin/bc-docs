---
uid: DEC-7a1c98
title: "Vocabulary Lock for the Opaque Workflow-Code Family — MMS / MCF doctrinal renaming policy"
description: "Operationally locks the semantic-naming policy for the opaque workflow-code family that accumulated inside MCF and the adjacent BCF surfaces — M-track process codes (M12, M12.5, M13, M14, M15, broader M0–M20 where used as process names), publication / coverage / precondition codes (PE-MC-*, L-V1*, C-FX-*), and BCF-style process / action shorthand (B6, C5, F3, C1/C2/F1/F2 where used as process names). Semantic names become primary in new doctrine, new docs, new operator-facing labels, new code identifiers, new route aliases, and future enum aliases; legacy codes survive only in inline comments, log metadata, persisted historical evidence, and migration appendices, and historical evidence is never rewritten (Foundation Invariant III). Names the canonical six-step Controlled Semantic Refactor sequence (Doctrine → Operator-facing docs/UI → Code identifiers → HTTP route aliases → DB enum aliases additive-only → per-metric controller quarantine). Names the MMS hierarchy — MMS umbrella; MCF grammar/substrate layer not renamed; Metric Engine runtime executor; Creation/Recovery/Runtime/Evolution Tracks. Filing this ADR completes Step 1 only; Steps 2–6 each require their own future operator authorization. Decision identifiers (DEC-…, D-…, ADR UIDs) are explicitly NOT renamed. This ADR renames nothing by itself; it is the authority future refactor sessions cite."
status: superseded
date: 2026-06-22T12:00:00.000Z
project: bc-docs
domain: contracts
subdomain: catalog
focus: vocabulary-lock
supersedes: []
superseded_by: DEC-54f221
devhub_registration: doc-registry indexed as DOC-4ccba8 via devhub_doc_scan on 2026-06-22 (Path A accepted by operator); decision-registry row creation deferred — superseded by DEC-54f221 (D449) on 2026-06-22 before the decision-registry sync was performed; DEC-54f221 is the live decision row in the DevHub decision registry. ADR file remains the source of truth per CLAUDE.md for the period during which it was authoritative; substrate persistence per Foundation Invariant III preserves its content unchanged.
governing_adrs:
  - DEC-c3e57f (D422 — Foundational MCF ADR; defines the framework whose vocabulary is locked here)
  - DEC-69f09e (D148 — substrate naming discipline; this ADR is consistent with snake_case + ISO 11179 substrate rules while operating one altitude above them at the doctrinal layer)
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Invariants (particularly Invariant III append-only — historical evidence never rewritten)
  - The Authority Model (doctrine + ADR authority precedes implementation work)
  - Metric Management System chapter (operator-ratified draft-authoritative doctrine)
  - Metric Management System — Recovery Track chapter (operator-ratified draft-authoritative doctrine)
  - MCF Framework Audit §7 (Vocabulary-Lock ADR draft body) and §7A (Controlled Semantic Refactor staging)
  - MCF Final Operating Flow Pre-Doctrine Decisions note
---

# Vocabulary Lock for the Opaque Workflow-Code Family — MMS / MCF doctrinal renaming policy

> **⚠ Superseded by [DEC-54f221 (D449)](ADR-54f221.md) on 2026-06-22.** The six-step refactor sequence locked here is replaced by a three-layer model (Interpretation Surfaces / Implementation Names / Compatibility Names). The legacy-code scope (Decision 1), the DEC-/D-/ADR-UID exclusion, the migration appendix (Decision 6), the MMS hierarchy (Decision 5), and Foundation Invariant III are preserved verbatim by DEC-54f221. Decision 3 (inline source comments as a permanent alias context) is **changed** in DEC-54f221 — comments are renamed at Layer 1 with transition-window annotation only. Decision 4's six-step ordering is **replaced** by the three-layer model. This ADR's content is preserved as historical evidence per Foundation Invariant III; the live authority is DEC-54f221.

## Rationale

The Metric Context Framework (MCF) build plan numbered its stages and gates by position in the build list. The numbers were a development sequencing convenience. They have since propagated into code identifiers, controller routes, service method names, runbook chapter headings, audit artifact filenames, the operator console UI, and the database enum values that participate in cert and Publication-Eligibility verdict surfaces. The adjacent Business Concept Framework (BCF) has accumulated a parallel set of stage / action shorthand codes. Every reader of every artifact in `mcf-*` or `bcf-*` maintains a glossary translating these codes into the behavioral intent of each stage or gate.

The cost of carrying this opaque code family is documented in the [MCF Framework Audit](../../evidence/audits/implementation/mcf-framework-audit-2026-06-22.md) §6.5 (operator-facing naming / code opacity) and §7A (Controlled Semantic Refactor). The doctrine response is recorded in the [Metric Management System chapter](../../operating-model/metric-management-system.md) §6 (naming rules) and the [Metric Management System — Recovery Track chapter](../../operating-model/metric-management-system-recovery-track.md).

This ADR operationally locks the semantic-naming policy that the doctrine establishes. It completes **Step 1** of the canonical six-step Controlled Semantic Refactor sequence in Audit §7A.3 / §7.3. It does not by itself rename any code, route, schema, enum, UI label, or historical artifact. It is the authority that future refactor sessions cite.

## Context

The doctrine and the audit reached the following state before this ADR was filed:

- [Metric Management System chapter](../../operating-model/metric-management-system.md) — operator-ratified draft-authoritative; carries the MMS umbrella framing (§1A), the Creation Track stage map (§3), the gate inventory and exhaustive PE-MC-N → semantic mapping (§4), the recovery-route enumeration (§5), the naming rules (§6 — including §6.3 doctrinal vs. substrate identifiers and §6.4 legacy-alias survival rules), and the refactor implications (§7).
- [Metric Management System — Recovery Track chapter](../../operating-model/metric-management-system-recovery-track.md) — operator-ratified draft-authoritative; carries the per-route operational policy for the eight recovery routes (R1–R8) and inherits MMS §6 naming rules.
- [MCF Framework Audit](../../evidence/audits/implementation/mcf-framework-audit-2026-06-22.md) — §6 gap inventory, §7 vocabulary-lock ADR body (this ADR is filed from that held draft), §7A Controlled Semantic Refactor staged sequence, §8 framework-ready exit criteria.
- [Pre-doctrine decisions note](../../evidence/work-records/implementation/mcf-final-operating-flow-pre-doctrine-decisions-2026-06-22.md) — five locked draft decisions, including Decision 4 (exhaustive PE-MC-N mapping) and Decision 5 (Recovery Track as parallel doctrine).
- Operating-model overview — already lists both MMS chapters in the Chapter Map, the Diagram Convention inventory, the reading sequences, and the References list.

This ADR consolidates the doctrine into a governance artifact and authorises **Step 1 only** of the controlled refactor. It does not authorise Steps 2 through 6.

## Decision 1 — Scope of codes covered

This ADR locks the semantic-naming policy for the following **opaque workflow-code family**:

- **M-track process codes** — `M12`, `M12.5`, `M13`, `M14`, `M15`, and the broader `M0`–`M20` sequence wherever they function as **names for stages or processes**. The build-plan document itself ([MCF requirements + build plan, see DEC-c3e57f / D422](ADR-c3e57f.md)) may retain the M0–M20 integers as pure sequencing scaffolding for build ordering; the rename rule applies wherever these integers are used as semantic process names in code identifiers, controller routes, service method names, runbook chapters, ADR titles, operator console UI labels, or new database enum values.
- **Publication / coverage / precondition codes** — `PE-MC-*` (gates inside Publication Eligibility Evaluation; exhaustively mapped per the [MMS chapter](../../operating-model/metric-management-system.md) §4.3), `L-V1*` (Materialization Preconditions), `C-FX-*` (Fixture Structural Check codes inside Self-Verification).
- **BCF-style stage / action shorthand** — `B6` (Business Concept Draft Review panel), `C5` (Operator Certification), `F3` (Registry Write / Registry Transition), and the `C1` / `C2` / `F1` / `F2` series **where they function as process names**. The same letters used as in-document section identifiers inside ADRs and chapters are out of scope; only the process-name uses are renamed.

**Explicitly NOT renamed.** Decision identifiers — `DEC-…`, `D-…`, ADR UIDs of any form — are unique identifiers of governed decisions, not process names. They remain unchanged by this ADR regardless of how often they appear alongside legacy process codes. Cross-references continue to cite the existing IDs verbatim.

## Decision 2 — Semantic naming rule (primary surfaces)

Semantic names — as established in [MMS chapter §6.1–§6.3](../../operating-model/metric-management-system.md) (stage names, gate names, artifact names) and the parallel naming surfaces in the [Recovery Track chapter §5](../../operating-model/metric-management-system-recovery-track.md) (route names R1–R8) — become **primary** in:

- New doctrine chapters in `bc-docs-v3/docs/foundation/`, `docs/operating-model/`, `docs/implementation/`, and `docs/onboarding/`.
- New documentation generally, including audit-artifact filenames and ADR titles authored after this ADR is filed.
- New operator-facing labels — operator console UI, runbook chapter headings, bc-admin Metric Lifecycle / Metric Chain surface labels.
- New code identifiers — class names, service names, controller filenames, method names, type names — in `bc-core/src/registry/mcf/`, `bc-core/src/registry/bcf/`, and adjacent code surfaces touched by the legacy codes.
- New HTTP route aliases — semantic routes added alongside legacy routes.
- Future database enum aliases — additive only, per Decision 4 Step 5.

## Decision 3 — Legacy-alias survival rules

Legacy codes may survive **only** in the following contexts:

1. **Inline code comments** in source files, with an explicit annotation pattern (e.g. `// legacy: M12`) on the semantic identifier. The annotation may persist for at least one published portfolio activation cycle (per the [Audit §8 exit criteria](../../evidence/audits/implementation/mcf-framework-audit-2026-06-22.md)).
2. **Log metadata fields and emitted telemetry tags**, where downstream log-pipeline consumers were built against the legacy codes and rename is coordinated separately on the log-pipeline side.
3. **Persisted historical evidence** — database rows already written under legacy values stay under those values forever per Foundation Invariant III. The substrate may carry both legacy and semantic values in the same enum column during the transition window after Step 5 (Decision 4); the reader side accepts both; historical rows are never rewritten.
4. **Migration appendix / cross-reference tables** — the legacy ↔ semantic mapping table that accompanies this ADR (Decision 6 below) and any successor cross-reference document that future audits, runbooks, or ADRs may cite.

Legacy codes **do NOT survive** in: new code identifiers, new controller class names, new HTTP route names, new runbook chapter titles, new operator console labels, new ADR titles, new audit-artifact filenames, or new database enum values being written by new substrate work.

## Decision 4 — Canonical six-step Controlled Semantic Refactor sequence

The implementation sequence for renaming, derived from [Audit §7A.3](../../evidence/audits/implementation/mcf-framework-audit-2026-06-22.md), is locked at six steps:

| Step | Layer | Scope | Owner |
|---|---|---|---|
| 1 | Doctrine + Vocabulary-Lock ADR | File this ADR (or its operator-revised successor) and the migration appendix that records the full legacy ↔ semantic mapping for cross-reference. New doctrine chapters in `bc-docs-v3/docs/implementation/`, `docs/operating-model/`, and `docs/foundation/` adopt semantic names from the date of ADR filing. Doctrine landing has zero substrate impact; it is the reference every subsequent step cites. | Documentation |
| 2 | Operator-facing docs and UI labels | Rename runbook chapter titles in `bc-docs-v3/docs/onboarding/`, operator console labels, audit-artifact filenames (new artifacts only — historical artifact filenames are never rewritten per Foundation Invariant III), and the bc-admin Metric Lifecycle / Metric Chain surface labels. UI rename is operator-visible but reversible at the label layer. | Documentation + bc-admin |
| 3 | Code identifiers and class / service / controller names | Rename inside `bc-core/src/registry/mcf/` (and adjacent BCF code surfaces touched by `B6` / `C5` / `F3` shorthand) — class names, service method names, file names, type names. Each rename is a pure refactor (no behavior change); test suites pass against either the legacy or the new name during the transition window via re-export aliases. HTTP routes are NOT renamed in this step. | bc-core |
| 4 | HTTP route aliases | Add semantic routes (e.g. `POST /api/mcf/metric-contract-versions/:uid/recover-post-review`) alongside the existing legacy routes (`POST /api/mcf/metric-contract-versions/:uid/abandon` continues to work). Both routes resolve to the same handler. The legacy routes are deprecated in a later operator-authorized step once consumers migrate; the deprecation window length is an operator decision. | bc-core |
| 5 | Database enum and persisted-code aliases (additive only) | Extend `governance_state_code`, `verdict_code`, `pe_check_code`, `action_code`, and similar enum columns with semantic-named values alongside the existing legacy values. The writer side may emit either; the reader side accepts both. **Historical evidence is never rewritten** (Foundation Invariant III) — database rows already written under legacy values stay under those values forever. A future operator decision may deprecate the legacy aliases at the *writer* layer; the *reader* layer must continue to accept them for as long as historical rows exist. | bc-core + DDL |
| 6 | Per-metric controller quarantine / fold-in | After the semantic routes in Step 4 are stable, the per-metric controllers (`mcf-arpi-materialization.controller.ts`, `billing-volume-retry-unlock/`, and any sibling per-metric surfaces) are either folded into the generic Stage 4 / Stage 7 surfaces or moved to a `legacy/` directory and marked deprecated. This step is small but visible; doing it last keeps Steps 2–5 independently revertible. | bc-core |

**Filing this ADR completes Step 1 only.** Steps 2 through 6 each require their own future operator authorization session at the point of execution. Each step is independently scoped; later steps gate on earlier steps having landed without correction.

## Decision 5 — MMS hierarchy (doctrinal, not substrate)

The hierarchy below is **doctrinal** — it organises how documents are scoped, owned, and read. It does NOT rename anything in substrate or code by itself.

- **Metric Management System (MMS)** — the umbrella system. Owns the full lifecycle of a metric in the BareCount platform: creation, activation, runtime evaluation, recovery from stuck states, evolution (supersession / retirement), and catalog visibility. Operationalised through four tracks: **Creation Track**, **Recovery Track**, **Runtime Track**, **Evolution Track**.
- **Metric Contract Framework (MCF)** — the formal **grammar / substrate** layer inside MMS. Defines what a Metric Contract *is*: identity tuple, formula AST, variable-binding shape, filter-clause shape, temporal-gate grammar, package signature, immutability rules, cert grammar. MCF schema (`mcf.*`), the foundational MCF ADR ([DEC-c3e57f / D422](ADR-c3e57f.md)), and MCF code surfaces (`bc-core/src/registry/mcf/`) keep their established names. This ADR does NOT rename MCF.
- **Metric Engine** — runtime executor terminology. The runtime component that applies an active Metric Contract Version against tenant data to produce Metric Snapshots. Owned by the Runtime Track. The current platform's runtime evaluator is documented in [Metric Evaluation](../../operating-model/metric-evaluation.md); the Metric Engine doctrine name is the term MMS uses for the executor role across the four tracks.
- **Creation Track / Recovery Track / Runtime Track / Evolution Track** — doctrinal track names; each will eventually have its own operating doctrine document. Creation Track and Recovery Track doctrines are landed (operator-ratified draft); Runtime Track and Evolution Track doctrines are future artifacts.

## Decision 6 — Migration appendix (legacy → semantic mapping)

### 6.1 Stage names (M-track)

| Legacy | Semantic | Notes |
|---|---|---|
| `M12` | Metric Draft Review | Panel (Maker / Checker / Moderator) proposes a metric candidate. |
| `M12.5` | Metric Contract Materialization | Approved panel proposal becomes draft `mcf.metric_contract` + `mcf.metric_contract_version` + bindings + fixture + initial verifier_result. |
| `M13` | Publication Eligibility Evaluation | Runs the nine-gate matrix (G1–G9) against a draft MCV; advances state on all-pass. |
| `M14` | Metric Activation | Transitions approved MCV to active; issues `metric_transition` cert. |
| `M15` | Metric Supersession | Active MCV → superseded; cert-bearing. |

The broader `M0`–`M20` sequence remains in the build-plan document as pure sequencing scaffolding; wherever it functions as a process name it follows the same semantic-primary rule.

### 6.2 Publication-Eligibility gates (PE-MC-*)

Mapping per [MMS §4.3](../../operating-model/metric-management-system.md) exhaustive table:

| Legacy | Semantic | Notes |
|---|---|---|
| `PE-MC-1` | **G9 Provenance Grounding Gate** | Promoted to its own gate (operator-ratified per [MMS §8.1](../../operating-model/metric-management-system.md)). Predicate preserved from PE-MC-1. |
| `PE-MC-2` (Grain coherence) | merged into **G2 Binding Integrity Gate** | Grain reachability is a property of every binding. |
| `PE-MC-3` (Binding completeness) | merged into **G2 Binding Integrity Gate** | Same family. |
| `PE-MC-4` (Type + unit coherence) | merged into **G2 Binding Integrity Gate** | Same family. |
| `PE-MC-5` (Self-verification fixture presence) | absorbed into **G5 Self-Verification Gate** | Fixture presence is a precondition of pass. |
| `PE-MC-6` (Temporal-gate shape) | merged into **G2 Binding Integrity Gate** | Temporal gate shape is part of the binding identity. The OPERATOR_REVIEW branch of PE-MC-6 is preserved as a G2 sub-verdict. |
| `PE-MC-7` (Computed-dimension coherence) | merged into **G2 Binding Integrity Gate** | Computed-dimension reachability is part of binding integrity. |
| `PE-MC-8` (Runtime readiness intent) | **retired from publication gating**; runtime-readiness concern relocated to **Stage 9 Runtime Evaluation** (operator-ratified per [MMS §8.2](../../operating-model/metric-management-system.md)) | Authoring publication proves contract validity; it does not require tenant / runtime readiness. Legacy PE-MC-8 rows in `mcf.metric_publication_eligibility_result` remain in the ledger as historical evidence per Invariant III. |
| `PE-MC-9` (Duplicate-intent detection) | **G8 Duplicate Intent Gate** | Renamed; predicate preserved exactly. Late-layer of the two-layer duplicate-intent discipline (the early-layer fingerprint check runs at Stage 2 Readiness Screening). |
| `PE-MC-10` (Self-verification fixture pass) | **G5 Self-Verification Gate** | Renamed; predicate preserved; absorbs PE-MC-5. |
| `PE-MC-11` (Source-Chain Resolvability) | **G3 Source-Chain Resolvability Gate** | Renamed; predicate preserved exactly. |
| `PE-MC-12` (Source-Vocabulary Discipline) | **G4 Source-Vocabulary Discipline Gate** | Renamed; predicate preserved exactly. |
| (new gate, no legacy predecessor) | **G1 Identity Uniqueness Gate** | Lifts substrate-side `idx_mcf_mc_mc_name_active` enforcement into the verdict ledger. |
| (new, lifted from PE-MC-10's stale check) | **G6 Package Signature Currency Gate** | Lifts the `stale_fixture_flag` sub-check out of legacy PE-MC-10 into its own gate. |
| (new, lifted from substrate triggers) | **G7 Lifecycle Authority Gate** | Lifts substrate-trigger cert-presence enforcement into the verdict ledger. |

### 6.3 Materialization Preconditions and Fixture Structural Check codes

- **`L-V1*`** (Materialization Preconditions family) — semantic family name: **Materialization Precondition checks** within Stage 4 (Metric Contract Materialization). Individual per-code mapping is **not yet locked** at the per-code level. Each `L-V1a` … `L-V1i` retains its existing identity in code and verdict ledger pending the exhaustive per-code naming pass that the verifier-portfolio work will produce ([Audit §6.4](../../evidence/audits/implementation/mcf-framework-audit-2026-06-22.md)). Until then, semantic references in new documentation use the family name "Materialization Precondition check" with the legacy code in parentheses on first mention.
- **`C-FX-*`** (Fixture Structural Check codes inside Self-Verification) — semantic family name: **Fixture Structural Check codes** within Stage 5 (Self-Verification) and G5. Eleven codes (`C-FX-1` through `C-FX-11`) emitted by `FixtureStructuralCheckService.runStructuralChecks`. Per-code semantic naming is deferred to the verifier-portfolio work; the family name is the doctrinal label.

### 6.4 BCF-style stage / action shorthand

| Legacy | Semantic |
|---|---|
| `B6` | Business Concept Draft Review (panel) |
| `C5` | Operator Certification |
| `F3` | Registry Write / Registry Transition |
| `C1` / `C2` / `F1` / `F2` (process-name uses) | **Code family — semantic naming deferred** | The `C1/C2/F1/F2` series functions as a process-name family inside BCF authoring; per-code semantic mapping is not yet locked. Until the BCF-side doctrine produces the per-code mapping, semantic references in new documentation use the family designation "BCF stage/action shorthand" with the legacy code in parentheses on first mention. The same letters used as in-document section identifiers inside ADRs and chapters are out of scope. |

### 6.5 Not renamed

Decision identifiers — `DEC-…`, `D-…`, ADR UIDs — are unchanged by this ADR. They identify governed decisions; they are not process names. Cross-references continue to cite the existing IDs verbatim.

## Decision 7 — Relationship to refactor

This ADR is the **authority** future refactor sessions cite. It does not by itself:

- Rename any code, controller, service, or class identifier.
- Add or remove any HTTP route.
- Extend or modify any database enum.
- Relabel any operator console UI element.
- Rename any historical artifact (filename, log row, audit row, persisted enum value).
- File any companion ADR or doctrine document.

The Controlled Semantic Refactor begins **only after this ADR is filed** and **only by explicit operator authorization** opening Step 2 (Operator-facing docs and UI labels) as its own session. Each subsequent step (Steps 3–6) requires the same — its own operator authorization at the point of execution.

If the operator chooses to defer Steps 2–6 indefinitely, this ADR's authority remains valid; the legacy-code opacity gap recorded in [Audit §6.5](../../evidence/audits/implementation/mcf-framework-audit-2026-06-22.md) simply remains open at the implementation layer while the doctrine layer carries the semantic vocabulary forward in all new artifacts.

## Cross-references

| Document | Role |
|---|---|
| [Metric Management System](../../operating-model/metric-management-system.md) | Parent doctrine — Creation Track flow, gate inventory, recovery-route enumeration, naming rules. |
| [Metric Management System — Recovery Track](../../operating-model/metric-management-system-recovery-track.md) | Recovery Track child doctrine — per-route operational policy for R1–R8. |
| [MCF Framework Audit](../../evidence/audits/implementation/mcf-framework-audit-2026-06-22.md) | Evidence base — §6 gap inventory, §7 vocabulary-lock ADR body (this ADR is filed from that draft), §7A Controlled Semantic Refactor staging. |
| [Pre-doctrine decisions](../../evidence/work-records/implementation/mcf-final-operating-flow-pre-doctrine-decisions-2026-06-22.md) | Locked draft decisions, particularly Decision 4 (exhaustive PE-MC-N mapping) and Decision 5 (Recovery Track as parallel doctrine). |
| [Operating Model overview](../../operating-model/operating-model-overview.md) | Section opener; carries the chapter map, the diagram convention, and the references list under which MMS and Recovery Track chapters sit. |
| [ADR DEC-c3e57f / D422](ADR-c3e57f.md) | Foundational MCF ADR. This vocabulary-lock ADR refines but does not contradict its build-plan scope; MCF substrate (`mcf.*`, code surfaces) is not renamed. |
| [ADR DEC-69f09e / D148](ADR-69f09e.md) | Substrate naming discipline (snake_case, ISO 11179). This ADR is consistent with the substrate rules while operating one altitude above them at the doctrinal layer. |
| [The Invariants](../../foundation/the-invariants.md) | Invariant III (append-only — historical evidence never rewritten) is the load-bearing constraint that shapes Step 5's "additive only" rule. |

## Reversal path

Foundation Invariant III applies: this ADR may be superseded by a future ADR. Individual decisions within this ADR (e.g. the specific per-code mappings in Decision 6, or the six-step sequence in Decision 4) are independently amendable via Errata against the named structural section without re-opening the whole ADR.

If a future ADR supersedes this one, the prior ADR's vocabulary lock remains historically valid for the period during which it was authoritative; rows persisted under that vocabulary remain under those values per Invariant III; the successor ADR's vocabulary applies forward.

## Consequences

Filing this ADR completes **Step 1** of the canonical six-step Controlled Semantic Refactor sequence ([Audit §7A.3](../../evidence/audits/implementation/mcf-framework-audit-2026-06-22.md)). The doctrine vocabulary established by the [MMS chapter](../../operating-model/metric-management-system.md) and the [Recovery Track chapter](../../operating-model/metric-management-system-recovery-track.md) is now governance-locked.

**Immediate consequences:**

- New doctrine chapters, new ADRs, new audit artifacts, and new runbook chapters authored after this ADR's filing date adopt semantic names as primary.
- Legacy codes appearing in already-filed artifacts remain as-is; this ADR does not rewrite history.
- Future operator-authorized sessions opening Steps 2–6 cite this ADR as their authority.

**What does NOT change as a consequence of filing this ADR:**

- No code is renamed, no service / class / controller is renamed, no HTTP route is added or removed, no database enum is extended, no UI label is relabeled, no historical artifact is renamed. Each of Steps 2–6 is its own operator-authorized session.
- The MCF substrate (`mcf.*` schema, [DEC-c3e57f / D422](ADR-c3e57f.md), `bc-core/src/registry/mcf/` code surfaces) is unchanged; MCF remains the grammar/substrate layer beneath MMS.
- Decision identifiers (`DEC-…`, `D-…`, ADR UIDs) are unchanged.
- The two stuck Metric Contract Versions on `bc_platform_dev` (`billing_cycle_time`, `paid_customer_invoice_count_v2`) are untouched by this ADR; their recommended recovery route plans are recorded in the [Recovery Track chapter §9](../../operating-model/metric-management-system-recovery-track.md) but are not invoked by this ADR.

**Next operator-authorized decision:** whether to open **Step 2 — Operator-facing docs and UI labels** as its own session, or to pause and defer the controlled refactor. Either choice is consistent with this ADR's authority.

## Registration state (2026-06-22)

This ADR's authority is the file itself, per CLAUDE.md (*"ADR files in bc-docs-v3 are the source of truth for decisions. DevHub stores metadata only (uid, title, status, description, file_path, domain_code)."*). Operator decision 2026-06-22 ratifies **Path A**: the ADR file remains source of truth, `DEC-7a1c98` remains the canonical UID, the doc-registry indexing is accepted as complete, and the decision-registry row creation is deferred as a small tooling / admin follow-up.

**Doc-registry sync — completed 2026-06-22.** `devhub_doc_scan` ran cleanly on 2026-06-22 (865 files scanned). The ADR is registered as **`DOC-4ccba8`** pointing at `bc-docs-v3/docs/adrs/ADR-7a1c98.md`; type `decision`; authority `evolving` (scanner default for unvalidated ADRs); domain `contracts`; status `unvalidated`. Promoting the doc-registry status (via `devhub_doc_validate DOC-4ccba8`) is a separate operator-authorized step that was not invoked at filing time.

`devhub_doc_scan` is a **metadata-index update only** — it reads ADR / chapter frontmatter from the `bc-docs-v3` filesystem and writes index rows into DevHub's own SQLite store at `data/devhub.db`. The scan did **not** mutate `bc_platform_dev` or any business substrate, did **not** change runtime behavior, did **not** patch code, did **not** file a PR, did **not** perform a refactor or rename. It updates DevHub's operational metadata index — bytes were written, scoped to DevHub's own data store.

**Decision-registry sync — deferred per operator Path A (2026-06-22).** A row keyed on `DEC-7a1c98` in the DevHub decision registry is not created by this ADR's filing. The canonical `devhub_decision_record` MCP tool auto-allocates a fresh DEC-UID and auto-generates a new ADR file under that UID — both behaviors would conflict with the already-filed `ADR-7a1c98.md` and the cross-references already laid down (in [MMS chapter](../../operating-model/metric-management-system.md), [Recovery Track chapter](../../operating-model/metric-management-system-recovery-track.md), the [audit](../../evidence/audits/implementation/mcf-framework-audit-2026-06-22.md), and the [pre-doctrine note](../../evidence/work-records/implementation/mcf-final-operating-flow-pre-doctrine-decisions-2026-06-22.md)). Decision-registry sync is therefore deferred as a small tooling / admin follow-up that the operator may authorize separately (e.g. via an admin endpoint or scoped DB insert into `data/devhub.db` that accepts `DEC-7a1c98` as the chosen UID).

The D-code nickname (e.g. `D-…`) is unallocated until the decision-registry row exists. Until then, all cross-references — in chapters, audits, ADRs, runbooks — use the canonical UID **`DEC-7a1c98`**. The operator explicitly directs: do NOT use `devhub_decision_record` to re-mint this ADR under a new UID; do NOT delete, replace, rename, or regenerate `ADR-7a1c98.md`.

**Consequences of the deferral.** `devhub_decision_list` will not surface this ADR under `status=decided` filters until the decision-registry row exists. The ADR's authority is unaffected — the file is the source of truth per CLAUDE.md. ADR-hygiene audit scripts (`bc-docs-v3/scripts/adr-audit.js`) may flag the ADR as registry-missing; that flag is expected and remains until decision-registry sync is performed.

**Step 2 status.** Step 2 of the Controlled Semantic Refactor (Operator-facing docs and UI labels per Decision 4 of this ADR) remains operator-gated. It was not begun by this filing session, was not begun by the doc-registry sync, and is not begun by this continuation note. Opening Step 2 requires its own operator-authorized session; the same applies to Steps 3 through 6.
