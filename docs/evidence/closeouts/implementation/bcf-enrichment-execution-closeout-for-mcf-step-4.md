---
uid: bcf-enrichment-execution-closeout-for-mcf-step-4
title: BCF Enrichment Execution Closeout for MCF Step 4 — Option B
description: Execution closeout for the Step 4 BCF enrichment slice under Option B (per pre-execution plan bc-docs-v3 248b004, recommendation §5.5). Ten panel runs executed via POST /api/bcf/registry-authoring-runs against bc-core 92a9056 + bc-ai live path 2026-05-26. Outcome — 1 entity authored at draft (Customer Invoice), 6 BCs authored at draft (CI · due date / posting date / status / effective date; SOL · discount / ordered quantity), 1 BC parked OPERATOR_REVIEW (CI · invoice id), 1 characteristic parked OPERATOR_REVIEW (`posted amount`), 1 characteristic awaiting operator-confirm (`clearing date`, F4-v2 happy path), 2 BCs not attempted (CI · posted amount + CI · clearing date — target characteristics not yet active). 0 enrichment writes outside the BCF panel path (allow_write false confirmed); 0 supersessions, 0 aliases, 0 supersession_proposals. Step 4 8-of-10 unblock target is NOT met in this single session — Metrics 5 and 8 are immediately authorable post-B10 activation (2 of 10); the remaining 6 metrics depend on operator-confirm and B10 acts enumerated in §9. No MCF M2 DDL apply, no MCF M3 open, no MC creation, no B6-v2 retrofit; no widening of bc-postgres allow_write.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: enrichment-execution-closeout
---

# BCF Enrichment Execution Closeout for MCF Step 4 — Option B

## 1. Scope and grounding

### 1.1 Purpose

Closeout report for the first BCF enrichment execution session under MCF Step 4. The session opened with the operator's authorization to execute Option B per the pre-execution plan recommendation, performed 10 panel runs through the production BCF authoring path, captured each outcome, and is now writing the operator-facing report on what landed, what is parked, what is awaiting confirm, and what remains.

### 1.2 Discipline assertions (all hold)

| Assertion | Status |
|---|---|
| No direct SQL writes to `concept_registry.*` | ✓ — every authoring act went through `POST /api/bcf/registry-authoring-runs` (the `RegistryAuthoringRunController` platform endpoint). |
| No widening of bc-postgres allow_write | ✓ — `pg_server_info` end-of-session confirms `allow_write: false` (re-verified). |
| No bypass of Framework Approval / panel / operator-confirm discipline | ✓ — every outcome is a verbatim `RegistryAuthoringOutcome` returned by the bc-core orchestrator; parked / awaiting-operator-confirm results are reported as-is and not coaxed. |
| No MCF M2 DDL apply, no MCF M3 open, no MC creation | ✓ — none of those gates touched. |
| No B6-v2 retrofit opened | ✓ — no hard trigger fired (§7). |
| Enrichment limited to Option B minimal slice | ✓ — only entities, BCs, and characteristics enumerated in pre-execution plan §6.3 column B were attempted; negative-test entity (out of handoff Scope) not authored. |

### 1.3 Stack state when execution opened

- bc-postgres MCP: `allow_write: false`; `concept_registry` in `schema_allowlist` (verified via `pg_server_info`).
- bc-core: was DOWN on session open; started via `npm run start:dev` (background) — `RegistryAuthoringPanelModule` initialized; `POST /api/bcf/registry-authoring-runs` mapped; `/api/health` returned 200.
- bc-ai: was DOWN; started via `.venv\Scripts\python -m uvicorn main:app --port 4300` — `model_registry_initialized model_count=7`; `Application startup complete`.
- Docker postgres: already up (since `pg_server_info` worked at session open).
- Cognito admin JWT: obtained via `devhub_get_cognito_token`.

### 1.4 Live registry baseline at session open (re-verification)

Same as pre-execution plan §3.1 — confirmed unchanged between SES-0e8cac close (2026-05-26 03:44 PM) and this session open (10:04 AM, +5h41m wall — calendar order reflects two attempts at session window):

- 1 entity (Sales Order Line, active)
- 1 BC (Sales Order Line · unit price, active)
- 26 characteristics, all active (24 F4-S1 + lead time + cycle time)
- 15 representation_terms
- 0 aliases, 0 supersessions, 0 supersession_proposals

---

## 2. Pre-execution plan consumed

| Source | Commit / UID | Role |
|---|---|---|
| Pre-execution plan | bc-docs-v3 `248b004` — `docs/implementation/bcf-enrichment-pre-execution-plan-for-mcf-step-4.md` | The plan this execution session operates against |
| Step 4 selection doc | bc-docs-v3 `f08b1ee` — `docs/implementation/mcf-step-4-first-representative-metrics-and-bcf-enrichment-slice.md` | The 10 representative metrics whose bindings drive the slice |
| BCF preflight | bc-docs-v3 `3495739` — `docs/implementation/bcf-enrichment-preflight-for-mcf-seed-cases.md` | v1 packet sufficiency + B6-v2 trigger conditions |
| MCF M1 foundational ADR | DEC-c3e57f (D422) | BCF as sole semantic-binding authority; operator-confirm discipline |
| BCF authoring controller + service + DTO + types | bc-core `92a9056` files: `registry-authoring-run.{controller,dto,service,types}.ts`, `registry-authoring-panel.types.ts`, `registry-authoring-orchestrator.service.ts` | The exact request shape, outcome union, and orchestrator routing |

The pre-execution plan §5.5 recommendation was **Option B**: compose `outstanding` via MCF AST filter over a new `posted amount` characteristic; author `clearing date` as a separate characteristic per operator decision; defer Metrics 3 + 6 to Step-4-bis.

---

## 3. Final operator decisions

The operator's handoff at execution-gate open recorded the following decisions:

| Decision point | Choice |
|---|---|
| Option A / B / C | **B** — compose via MCF AST filter; defer Metrics 3 + 6 |
| Service startup | Start bc-core + bc-ai myself |
| Clearing-date treatment | Separate `clearing date` characteristic (not overload `effective date`) |
| Negative-test entity | Out of handoff Scope; not attempted this session |
| Evidence sources | Operator-implicit: BareCount-bounded references to OAGIS BODs, APQC PCF, SAP S/4HANA table semantics (BSEG, VBAP, VBRK, BKPF, KONV), IFRS where relevant. All citations cross-checked with public business architecture references; no internet retrieval inside the panel run (panel reads only the bounded packet bc-core assembles from F5 + the candidateEvidence supplied in the request body). |

The operator did NOT pre-specify per-BC characteristic resolution. The panel was permitted to choose the characteristic / representation_term for each BC from the live active vocabulary; this judgement is the panel's by construction (BCF requirements + alignment note `da8d9b7`).

---

## 4. Enrichment items executed — outcome summary

10 panel runs were attempted. None bypassed the panel; every act issued one POST and accepted the orchestrator's `RegistryAuthoringOutcome` verbatim.

### 4.1 Outcome counts

| Outcome `kind` | Count | Implication |
|---|---:|---|
| `authored` (entity) | 1 | C5 cert issued + F3 wrote row at `lifecycle_state = draft` |
| `authored` (business_concept) | 6 | Same — row at `lifecycle_state = draft` |
| `awaiting_operator_confirm` (characteristic) | 1 | F4-v2 happy path: panel APPROVE; C5 returned `operator_confirm_required`; **no F3 write yet**. Awaits the operator-confirm endpoint + F4-v2 S2b post-confirm executor. |
| `parked` (verdict_code OPERATOR_REVIEW) | 2 | Panel non-APPROVE (review-requested verdict). No Registry write. No rejection-log row (B6 D2). |
| Not attempted (deferred this session) | 2 | Target characteristics aren't active yet — authoring blocked by precondition. |

Total: 10 panel runs + 2 deferred = 12 items in pre-execution Phase A + B + C inventory under Option B.

### 4.2 Per-item summary

| # | Item | Type | Outcome | Subject UID |
|---:|---|---|---|---|
| 1 | Customer Invoice | Entity | authored (draft) | entityId `e3963e45-ad13-4f6c-a1c3-fa56d8fd6446` |
| 2 | Customer Invoice · due date | BC | authored (draft) | conceptId `f8a30b35-cf5e-43b4-b645-31e71b56ac45` |
| 3 | Customer Invoice · posting date | BC | authored (draft) | conceptId `d05f24b3-c701-4864-a7f7-be50703d1575` |
| 4 | Customer Invoice · status | BC | authored (draft) | conceptId `92a5eea0-8b24-43fc-b019-b9b637790073` |
| 5 | Customer Invoice · effective date | BC | authored (draft) | conceptId `e5774d89-2478-4d46-95e5-1af821a72eda` |
| 6 | Customer Invoice · invoice id | BC | **parked OPERATOR_REVIEW** | panelRunUid `5555752f-5209-4d81-986d-89f06808563e` |
| 7 | Sales Order Line · discount | BC | authored (draft) | conceptId `ea91771f-694c-4316-95e6-8925944c1b7e` |
| 8 | Sales Order Line · ordered quantity | BC | authored (draft) | conceptId `1bb02176-756e-4a7b-87f8-36109eaa1bd4` |
| 9 | `posted amount` | Characteristic (F4-v2) | **parked OPERATOR_REVIEW** | panelRunUid `2542b4bf-aa44-40b4-9f3f-1afc1184a3a7` |
| 10 | `clearing date` | Characteristic (F4-v2) | **awaiting_operator_confirm** | panelRunUid `1d79141d-a4f6-4b5e-838e-ea156c74d76f`; governingPolicyUid `bcf-registry-scope1`; policyVersion `v1` |
| 11 | Customer Invoice · posted amount | BC | not attempted (deferred — target char not active) | — |
| 12 | Customer Invoice · clearing date | BC | not attempted (deferred — target char not active) | — |

### 4.3 Critical lifecycle finding — authored rows are `draft`, not `active`

The orchestrator's `authored` outcome confirms the F3 substrate write completed (row exists, certification recorded). It does NOT mean the row is `active`. Per the live verification in §6, all newly-authored rows landed at `lifecycle_state = draft`. **BCF publication (B10) is a separate operator-confirm act that flips draft → active.** Until B10 activation, MCF cannot bind to these BCs.

This is the documented BCF lifecycle (per `business-concept-registry-b10-publication-lifecycle-design.md` line 84: "a draft characteristic is invisible to BCF binding"; the same rule extends to entities and BCs). The pre-execution plan §6.4 D1-D3 acceptance criteria are explicit that all Phase A / B / C rows must be `active` — that criterion is NOT met by mere authoring.

Operator action sequence to reach Step 4 acceptance is enumerated in §9.

---

## 5. Per-item evidence and approval trail

Each panel run carried a non-empty `candidateEvidence` block (the panel mechanically rejects any request with empty evidence per `registry-authoring-run.dto.ts:99` validation + bc-ai `registry_authoring_panel.py` grounding check). The full payloads are saved at `barecount-devhub/.claude/scripts/bcf-step4-*.json` for audit; this section summarizes the source labels actually submitted.

### 5.1 Authored rows — evidence supplied

| # | Item | sourceLabel summary | citedText anchor |
|---:|---|---|---|
| 1 | Customer Invoice entity | OAGIS Customer Invoice BOD; APQC PCF v7.4 process 9.4.x | "the document tracks the buyer's payment obligation across its lifecycle" |
| 2 | CI · due date | SAP ZTERM + ZFBDT; OAGIS PaymentTerms element | "ZFBDT + days = due date" |
| 3 | CI · posting date | SAP BKPF.BUDAT; OAGIS DocumentDateTime | "anchoring fiscal-period assignment for the receivable" |
| 4 | CI · status | SAP BSID/BSAD partitioning + dispute flags; OAGIS StatusCode | "partitions customer-invoice line items by status across BSID (open) and BSAD (cleared)" |
| 5 | CI · effective date | SAP CDPOS (Change Document Items) status-change audit | "the basis for aging metrics such as 'disputes older than 30 days'" |
| 7 | SOL · discount | SAP VBAP / KONV (Pricing Conditions); OAGIS PricingComponent | "KONV pricing condition records on the sales order line" |
| 8 | SOL · ordered quantity | SAP VBAP.KWMENG; OAGIS OrderQuantity | "the customer's requested count of units" |

### 5.2 Panel-decided characteristic / representation-term bindings (panel judgement, not operator-supplied)

The BCF authoring DTO does not include `characteristicId` / `representationTerm` / `unit` / `kind` / `identityRole` — the panel resolves these from the candidate's `proposedName` + `definition` + `candidateEvidence` against the active vocabulary in the bounded packet. Live verification shows the panel's choices:

| BC | Panel-chosen characteristic | Panel-chosen representation_term |
|---|---|---|
| CI · due date | `due date` (existing F4-S1) | `date` |
| CI · posting date | `posting date` (existing F4-S1) | `date` |
| CI · status | `status` (existing F4-S1) | `code` |
| CI · effective date | `effective date` (existing F4-S1) | `date_time` (NB: not `date` — see §5.3 below) |
| SOL · discount | `discount` (existing F4-S1) | `amount` |
| SOL · ordered quantity | `ordered quantity` (existing F4-S1) | `quantity` |

All six panel characteristic choices match the pre-execution plan §6.3 expected bindings. The `effective date` characteristic was successfully overloaded for status-change-date semantics — a panel-judgement call the pre-execution plan §5.5 had flagged as Medium collision risk; the panel approved given the candidate evidence (CDPOS status-change audit + AR-aging-metric framing).

### 5.3 The `date_time` representation-term call (effective date)

The panel selected `representation_term: 'date_time'` for CI · effective date, not the `date` we used for the other date-typed BCs. This is the panel exercising real judgement: a status-change timestamp is more naturally a `date_time` than a `date`. This is a positive finding — the panel reads candidate evidence carefully and picks the right representation class. No operator action needed; the choice is sound.

### 5.4 Non-APPROVE outcomes — what the panel said

#### CI · invoice id — parked OPERATOR_REVIEW

The panel routed this to OPERATOR_REVIEW (not REJECT). Likely cause: the active characteristic vocabulary (26 rows per §1.4) does not contain a fitting characteristic for an invoice-document-level identifier. The closest is `line number` ("Ordinal position of a line item within a multi-line document"), which is semantically wrong for an invoice document id. The panel could not autonomously bind to a vocabulary characteristic and routed to operator review per the BCF B6 D2 + F4-v2 review-routing rules.

**Operator resolution path:** either (a) author a new identifier-class characteristic (e.g. `document identifier` or `business document number`) via F4-v2 createCharacteristic, then re-submit the invoice id BC; or (b) accept overload of `line number` if the panel surfaces that as the operator-review choice (semantically poor); or (c) accept that BC may carry no `characteristic_id` if the schema allows identifier-role BCs without a vocabulary characteristic (panel decision).

#### `posted amount` — parked OPERATOR_REVIEW

The panel routed this to OPERATOR_REVIEW (not REJECT). Likely cause: F4-v2 Vocabulary Admission Checklist classified the candidate as something other than `global` (the only auto-APPROVEable class in v1). The panel may have classified `posted amount` as `industry_specific` (finance) or `alias_localization_candidate` (overlap with existing amount-class characteristics). Per F4-v2 §6, non-`global` classification routes to operator-review.

**Operator resolution path:** operator reviews the panel's classification rationale (in `panel_output_record.verdict_payload_json`) and either (a) accepts the non-`global` classification and confirms via the operator-review path, (b) re-submits with adjusted framing that the panel may classify `global`, or (c) defers `posted amount` and reframes the affected metrics.

#### `clearing date` — awaiting_operator_confirm (F4-v2 happy path)

This is the **expected F4-v2 happy path** per `registry-authoring-panel.types.ts:96-102`. The panel APPROVED `clearing date`; C5 issued no cert because the operation is high-risk (`registry_author_vocabulary` action code); the orchestrator returned `awaiting_operator_confirm` with `governingPolicyUid: bcf-registry-scope1` + `policyVersion: v1`. No F3 write happened yet — the operator must complete the F4-v2 S2b post-confirm executor to land the characteristic at `active`.

**Operator resolution path:** complete the operator-confirm via the configured operator-confirm endpoint or surface (bc-admin UI-S4b publication confirm flow). The Fork-ii idempotent-resume pattern means re-attempting the run after confirm produces `already_authored` rather than a duplicate.

### 5.5 Deferred BCs — why not attempted

CI · posted amount and CI · clearing date were not posted this session. Both target characteristics (`posted amount`, `clearing date`) are not in `lifecycle_state = active` (one parked, one awaiting confirm). Attempting them now would either fail at the panel's bounded-packet validation (the target characteristic isn't in `activeCharacteristics`) or land an orphaned BC. They wait for the target characteristics to reach `active` post operator-confirm + B10.

---

## 6. Live post-execution registry verification (read-only)

All counts and rows below are from live SELECT 2026-05-26 immediately after the 10 panel runs, against `bc-postgres` with `allow_write: false`.

### 6.1 Aggregate counts vs baseline

```sql
SELECT 'entity', COUNT(*) FROM concept_registry.entity
UNION ALL SELECT 'business_concept', COUNT(*) FROM concept_registry.business_concept
UNION ALL SELECT 'characteristic', COUNT(*) FROM concept_registry.characteristic
-- ... (full query in §6.4)
```

| table | baseline | post-execution | delta |
|---|---:|---:|---:|
| entity | 1 | 2 | **+1** (Customer Invoice) |
| business_concept | 1 | 7 | **+6** (4 CI BCs + 2 SOL BCs) |
| characteristic | 26 | 26 | 0 (posted amount parked / clearing date awaiting confirm — neither written yet) |
| representation_term | 15 | 15 | 0 |
| alias | 0 | 0 | 0 |
| entity_supersession | 0 | 0 | 0 |
| business_concept_supersession | 0 | 0 | 0 |
| characteristic_supersession | 0 | 0 | 0 |
| supersession_proposal | 0 | 0 | 0 |

### 6.2 Entity table (2 rows)

| entity_id | lifecycle_state | canonical_name | created_at | created_by |
|---|---|---|---|---|
| `e974a6cd-…fe71` | active | Sales Order Line | 2026-05-22T07:31:59Z | bcf-registry-authoring-panel |
| `e3963e45-…6446` | **draft** | Customer Invoice | 2026-05-26T10:31:03Z | bcf-registry-authoring-panel |

Sales Order Line entity remains unchanged. Customer Invoice is the new authored entity at `draft`.

### 6.3 Business concept table (7 rows)

| concept_id | lifecycle_state | entity | characteristic | rep term |
|---|---|---|---|---|
| `f66642ad-…f5c3` | active | Sales Order Line | unit price | amount |
| `f8a30b35-…ac45` | **draft** | Customer Invoice | due date | date |
| `d05f24b3-…1575` | **draft** | Customer Invoice | posting date | date |
| `92a5eea0-…0073` | **draft** | Customer Invoice | status | code |
| `e5774d89-…2eda` | **draft** | Customer Invoice | effective date | date_time |
| `ea91771f-…1b7e` | **draft** | Sales Order Line | discount | amount |
| `1bb02176-…1bd4` | **draft** | Sales Order Line | ordered quantity | quantity |

Sales Order Line · Unit Price BC remains `active` and unchanged. Six new BCs all at `draft`. No characteristic supersession; no BC supersession; no proposal in flight.

### 6.4 Characteristics — no new rows

Live count of characteristics created after this session's start time: **0**. The 26 active characteristics from the baseline are unchanged. `posted amount` is parked (no row written; the panel run produced a `panel_output_record` but not a substrate row). `clearing date` is awaiting operator-confirm (the F3 registerCharacteristic write is gated behind the operator-confirm executor — no row written yet).

This confirms the discipline: a parked / awaiting-confirm characteristic does NOT pre-write the substrate; the substrate row only appears when the full APPROVE → C5 → F3 chain completes.

### 6.5 Sales Order Line / Unit Price unchanged

Verified in §6.2 and §6.3 — the pre-existing Entity row and Unit Price BC carry their original `2026-05-22` timestamps and `active` state. No `_supersession` rows reference them. The session did not touch the existing BCF substrate.

### 6.6 Allow-write discipline

`pg_server_info` re-checked: `allow_write: false`, `schema_allowlist: [..., concept_registry]`. Unchanged from session open. Zero writes were attempted outside the BCF panel path.

---

## 7. BCF v1 packet sufficiency observations

The pre-execution plan §8 verdict was that v1 packet sufficiency holds for the Option B slice with no hard trigger expected. Re-checking against the actual session evidence:

| Hard trigger | Status this session |
|---|---|
| T-H1 — cross-entity disambiguation load-bearing | NOT TRIGGERED. Every BC's target entity was operator-supplied via `targetEntityId`; no cross-entity reasoning was needed. |
| T-H2 — source-reality grounding PE-MC-1-mandatory for a class | NOT TRIGGERED. Each candidateEvidence cited SAP table semantics or OAGIS BOD elements as operator-supplied evidence, satisfying the bc-ai grounding-deep-equal check without requiring registry-side source-reality probes. |
| T-H3 — active characteristic vocabulary wire-size threshold | NOT TRIGGERED. 26 active characteristics × ~150 chars ≈ 4 KB per createBusinessConcept packet; no observable latency impact in the 10 panel runs. |
| T-H4 — bc-ai acquires free Registry query path | NOT TRIGGERED. L1 lock preserved; bc-ai panel runs from the bounded packet only. |

**Verdict carried:** v1 packet remains sufficient; **no B6-v2 retrofit opens**.

Soft observations recorded for future trigger monitoring:

- The two OPERATOR_REVIEW verdicts (CI · invoice id, posted amount) reveal that v1 packet's `activeCharacteristics` list, when it does not contain a fitting characteristic for a BC, leaves the panel without a path to APPROVE. The panel correctly routes to OPERATOR_REVIEW rather than reject. This is not a B6-v2 trigger by itself (the operator-review surface exists for exactly this case), but if it becomes a recurring blocker for multiple slices, the operator could consider seeding identifier-class characteristics ahead of slice openings.
- The `date_time` choice for CI · effective date (panel judgement) is a positive — the panel reads candidate definitions carefully and selects representation-term granularity intelligently.

---

## 8. Deferred Step-4-bis items

Items not addressed this session, per Option B + handoff Scope. These are explicit out-of-scope items, not failures.

### 8.1 Metrics 3 and 6 (per Option B recommendation)

| Metric | Reason for deferral |
|---|---|
| Metric 3 — Unbilled revenue (`recognized − billed`) | Requires `recognized amount` + `billed amount` characteristics; Option B avoids by deferring rather than authoring. Step-4-bis opens after operator decides whether to revisit Option A's deferral reversal for these characteristics or compose them differently. |
| Metric 6 — Recognized revenue per fiscal_period | Requires `invoice amount` characteristic plus D365 `posting_date_field` runtime prerequisite. Step-4-bis opens after the same characteristic decision plus D365 landing. |

### 8.2 Negative-test entity

Out of handoff Scope (only required for later MCF grain-coherence checking). Not attempted this session. Pre-execution plan §6.1 reserves this as a follow-up authoring act when MCF Gate M11 / M12 grain-coherence implementation needs a negative-test target.

### 8.3 Aliases

The Customer Invoice entity and the 6 new BCs were authored with canonical names only; no `alias` rows were created. If operators in future surfaces want to expose `Invoice` / `Sales Invoice` / `AR Invoice` as alternate display names mapping to Customer Invoice, those can be added via the alias surface in subsequent sessions. Not required for the Option B slice's metric unblock.

---

## 9. Risks and follow-ups

### 9.1 Live operator action sequence to reach Step 4 acceptance (the 8-of-10 unblock)

The 8-of-10 Option B unblock promise is **NOT met by this session alone**. The following operator actions are required to reach it. Each act is operator-driven (one operator session each, or batched per operator preference); none is autonomously executable by Claude:

| # | Operator act | Mechanism | Unblocks |
|---:|---|---|---|
| O-1 | B10-activate Customer Invoice entity (draft → active) | bc-admin UI-S4b publication confirm flow OR a B10 endpoint call | Pre-requisite for any CI BC to be `active` |
| O-2 | B10-activate the 6 new BCs: CI · due date, posting date, status, effective date; SOL · discount, ordered quantity | Same B10 flow, one act per BC | Pre-requisite for MCF to bind these BCs |
| O-3 | Operator-confirm `clearing date` characteristic | F4-v2 operator-confirm endpoint (Fork-ii idempotent-resume pattern) → F3 `registerCharacteristic` writes the row | Unblocks authoring of CI · clearing date BC |
| O-4 | Resolve `posted amount` characteristic OPERATOR_REVIEW (parked) | Operator reviews `panel_output_record` for panelRunUid `2542b4bf-aa44-40b4-9f3f-1afc1184a3a7`; either accepts non-`global` classification + confirms, or re-submits with adjusted framing | Unblocks authoring of CI · posted amount BC |
| O-5 | Resolve CI · invoice id OPERATOR_REVIEW (parked) | Operator reviews `panel_output_record` for panelRunUid `5555752f-5209-4d81-986d-89f06808563e`; likely needs to author a new identifier-class characteristic via F4-v2 first, then re-submit the BC | Unblocks Metric 4 |
| O-6 | After O-3, O-4 complete + characteristics `active`: author CI · posted amount BC | `POST /api/bcf/registry-authoring-runs` createBusinessConcept (next session) | Authors BC at draft |
| O-7 | After O-3, O-4 complete + characteristics `active`: author CI · clearing date BC | Same | Authors BC at draft |
| O-8 | B10-activate the 2 new char-dependent BCs + the new `posted amount` + `clearing date` characteristic rows | B10 flow | Final state: all Phase A / B / C rows `active` |

### 9.2 Metric unblock arithmetic at each operator-action milestone

| State after | Metrics unblocked |
|---|---|
| This session only (current) | **2 of 10** — Metric 5 (Avg days late, needs CI · posting date + due date) + Metric 8 (Discount/line amount, needs SOL · discount + ordered quantity + Unit Price). **Both pending B10 activation** of CI entity + 4 new BCs. |
| After O-1 + O-2 | Same 2 metrics — but now actually authorable into MCF (the BCs are `active`). |
| After + O-5 (invoice id resolved + BC active) | **3 of 10** — adds Metric 4. |
| After + O-3 + O-4 + O-6 + O-7 + O-8 | **8 of 10** — adds Metrics 1, 2, 7, 9, 10. Matches Option B target. |
| Metrics 3 + 6 | Always Step-4-bis — separate enrichment session. |

### 9.3 Risks updated against live findings

| # | Risk | Mitigation |
|---|---|---|
| R-1 | Operator may not be aware that authored rows are at `draft` and require B10 — could attempt MCF binding prematurely. | §4.3 and §6 prominently document the lifecycle finding. CLAUDE.md and BCF B10 design already record this; closeout reinforces. |
| R-2 | `posted amount` OPERATOR_REVIEW resolution may take multiple panel runs if operator + panel cannot reach a `global`-class agreement. | If multiple OPERATOR_REVIEW iterations don't converge, fall back to Option A's `outstanding amount` directly (with operator reversing F4-S1 §6 deferral) — see pre-execution plan §5.5 "Conditions for the recommendation to hold". |
| R-3 | CI · invoice id BC may require authoring a new identifier-class characteristic first (chain of dependencies). | Cleanest: author `business document number` or `document identifier` characteristic via F4-v2, then re-submit the BC. Bypasses awkward `line number` overload. |
| R-4 | The `effective date` overload for CI · effective date was panel-approved but may surface semantic confusion later (different BC kinds — invoice-status-change vs document-issued-on — both binding `effective date`). | Document the overload in the BC definitions (already done in the authored BC definition: "the timestamp at which the invoice's present state began"). Operator may revisit later via an alias rather than a new characteristic. |
| R-5 | bc-pg-mcp `pg_count` / `pg_list_tables` bug (carried from pre-execution plan §2.2) still present. | Workaround documented; ticket for bc-pg-mcp owner. |

### 9.4 What NOT to do as follow-up

- Do not retry parked items by softening evidence or re-framing solely to coax APPROVE — operator-review IS the discipline, not a bug.
- Do not direct-SQL the draft BCs to `active`; the only correct path is B10 publication-confirm.
- Do not author the 2 deferred BCs (CI · posted amount, CI · clearing date) until the target characteristics are `active`.
- Do not open MCF M3, M2 DDL apply, MC creation, or B6-v2 retrofit (none triggered).

---

## 10. MCF handoff — which representative metrics are unblocked

Per the Step 4 §4 metric inventory, mapped against the live post-execution state and the operator-action milestones (§9.2).

### 10.1 Today's authorable-into-MCF set (after operator B10-activates the draft rows)

| Step 4 metric | Required BCs | All required BCs `active`? | Authorable into MCF post-O-1+O-2? |
|---|---|---|---|
| Metric 5 — Avg days late, 30d window | CI · posting date + CI · due date | After O-1+O-2: yes | **YES** |
| Metric 8 — Discount-to-line-amount (Sales Order Line) | SOL · discount + SOL · ordered quantity + SOL · Unit Price (existing) | After O-2: yes (SOL · Unit Price already active; the 2 new SOL BCs need B10) | **YES** |

Two of ten today, after B10.

### 10.2 Authorable after each operator follow-up milestone

| Milestone | Newly authorable |
|---|---|
| O-1 + O-2 (B10 activation of this session's draft rows) | Metrics 5, 8 (= 2) |
| + O-5 (invoice id BC resolved + active) | + Metric 4 (Aged dispute count) → 3 total |
| + O-3 (clearing date char operator-confirmed) | (no metric yet — BC still needs to be authored) |
| + O-4 (posted amount char resolved + active) | (no metric yet — BC still needs to be authored) |
| + O-6 + O-7 + O-8 (BCs authored + B10) | + Metrics 1, 2, 7, 9, 10 → 8 total. Option B target met. |

### 10.3 Step-4-bis-only metrics

Metric 3 (Unbilled revenue) and Metric 6 (Recognized revenue per fiscal_period) — out of scope this session per Option B + Step 4 §5.5. Step-4-bis required.

### 10.4 MCF authoring is the NEXT framework's responsibility

This closeout is BCF-side only. MCF authoring of the unblocked metrics (M3-M20 + the Metric Authoring Panel work) is governed by MCF M1 (DEC-c3e57f / D422) and the MCF build plan; it requires MCF M2 DDL apply + M3 onwards. None of those gates is opened here.

When MCF M2 + the substrate land (separate operator-authorized session under Database Change Protocol), the MCF Metric Authoring Panel can begin authoring the 2-then-8 metrics against the BCs this session and its follow-ups produced.

---

## Document verification

- **All 10 required sections present** per handoff (§1 Scope and grounding; §2 Pre-execution plan consumed; §3 Final operator decisions; §4 Enrichment items executed; §5 Per-item evidence and approval trail; §6 Live post-execution registry verification; §7 BCF v1 packet sufficiency observations; §8 Deferred Step-4-bis items; §9 Risks / follow-ups; §10 MCF handoff with the unblocked-metric list).
- **Discipline assertions hold** (§1.2) — no direct SQL writes, allow_write unchanged, no operator-confirm bypassed, no MCF gates touched, no B6-v2 opened.
- **Outcome counts cited verbatim** — every authored / parked / awaiting-confirm result in §4.2 and §5 is the literal `RegistryAuthoringOutcome` returned by `RegistryAuthoringOrchestrator.runS1`.
- **Lifecycle reality recorded** — §4.3 + §6.2 + §6.3 + §9.1 make explicit that authored rows are at `draft` and require B10 activation before MCF binding; the 8-of-10 unblock arithmetic in §9.2 accounts for every operator follow-up act.
- **No code changes, no DDL, no DB writes outside the BCF panel path.** Doc-only commit to bc-docs-v3 main.
