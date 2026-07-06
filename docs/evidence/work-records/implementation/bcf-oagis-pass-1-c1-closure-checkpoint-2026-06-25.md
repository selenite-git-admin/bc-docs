---
title: BCF × OAGIS Pass 1 C1 — Closure Checkpoint (2026-06-25)
description: Closeout checkpoint for the C1 broad foundation buildout. 16 draft characteristics authored across the program (5 prior + 7 RP-2 + 1 RP-3 freight_terms_code + 3 RP-3 retry post-DEC-ec341c). 9 parked residuals and 2 held semantic rows remain; per the closure plan they stay as residuals, not chased. The bc-ai Maker-null defect is captured as an independent service-side thread, separate from policy or packet hygiene. Pass 1 C2 entry is not authorized in this checkpoint.
status: closeout_held
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-c1-closure
related_docs:
  - bcf-oagis-pass-1-c1-rp2-parked-row-analysis-2026-06-25.md
  - bcf-oagis-pass-1-c1-rp3-packet-prep-2026-06-25.md
  - bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
---

# BCF × OAGIS Pass 1 C1 — Closure Checkpoint (2026-06-25)

> Closeout state of the C1 broad foundation buildout. **Pass 1 C1 stays held at this state; residuals are NOT chased further in this session.** Per the operator closure plan: "close C1 with residuals rather than chasing the remaining 9 immediately."

## 1. Substrate state

| Metric | Value |
|---|---|
| Active characteristics (`concept_registry.characteristic` lifecycle_state='active') | 62 |
| Draft characteristics (lifecycle_state='draft') | **17** (+3 this session from the RP-3 retry confirm wave) |
| Total non-archived | **79** |

The +3 delta from this checkpoint's C5 confirm step:

| # | Term | characteristic_uid | certification_record_uid | created_at | admission_scope |
|---:|---|---|---|---|---|
| 1 | location code | `6430a0ce-3ca1-492d-8acc-7845b75a29c4` | `bfff645f-7be1-4830-9681-5edc09a1d386` | 2026-06-24T15:40:19.646Z | cross_function |
| 2 | transport service level code | `82b49116-6d49-40ab-bf07-2e2d11df8b89` | `89e9a627-0d37-4d98-8691-93febbb2430f` | 2026-06-24T15:40:19.824Z | cross_function |
| 3 | wage type code | `223e855c-c3c1-49ea-9c70-ef8db7c1b151` | `754823fe-cab5-4534-9e73-87b6c57a691c` | 2026-06-24T15:40:20.201Z | function_scoped / workforce_payroll |

## 2. C1 program — cumulative authoring tally

| Phase | Draft characteristics authored (cumulative) | Notes |
|---|---:|---|
| Pre-RP-2 baseline (DPO-r1 + early waves; sex code, marital status code, payment method code, country code, currency code) | 5 | Authored prior to RP-2 packet design |
| RP-2 r1 transport + C5 confirms (2026-06-24) | +7 | Unit of measure, tariff classification, invoice match type, schedule date basis, freight classification, usage restriction, tracking method |
| RP-3 r2 (pre-DEC-ec341c) | +1 | freight terms code |
| **RP-3 retry r3 (post-DEC-ec341c, this checkpoint)** | **+3** | location code, transport service level code, wage type code |
| **C1 total draft characteristics from the program** | **16** | All 16 currently in `lifecycle_state='draft'` |

## 3. RP-3 retry verdict outcomes (post-DEC-ec341c runtime)

| Outcome | Count | Rows | Rate vs r2 (pre-DEC-ec341c) |
|---|---:|---|---|
| **APPROVE_FOR_DRAFT → C5-confirmed in this checkpoint** | **3** | location code (cross_function), transport service level code (cross_function), wage type code (function_scoped / workforce_payroll) | r2 saw 1 APPROVE (freight terms code, since confirmed). r3 retry **gained 2 net new approvals** under the corrected admission rubric; wage type code in particular proves the `function_scoped` policy path works end-to-end. |
| OPERATOR_REVIEW (parked) | 9 | See §4 below for residual breakdown. | r2 saw 12 parked (incl. freight). Drop of 3 is real, but 9 residuals remain. |

## 4. Parked residuals (9 rows — held as residuals, not chased)

Breaking down `verdict_payload_json.review_reason` text across the 9 parked rows in the RP-3 retry:

### 4.1 Substantive Maker / Checker scope or evidence disagreement (6 rows)

These are legitimate panel-policy outcomes under the new doctrine — the Checker is actively interrogating admission_scope claims and the supporting evidence. Not the old Global-only mass rejection.

| panel_run_uid | Term | Substantive concern |
|---|---|---|
| `b150c1dd…` | process step number | Maker `function_scoped` / operations_planning, Checker flags evidence may be manufacturing-narrow or function-misclassified |
| `2cf8b71f…` | schedule type code | Maker `function_scoped` / operations_planning, Checker flags evidence spans logistics, production, maintenance, HCM — possibly cross-function not function-scoped |
| `36407608…` | negotiated price authorization reference | Evidence-not-sufficient: cited examples (SAP VK11/VK12, Oracle Pricing, Salesforce CPQ, distribution SPAs) read as authorization-reference patterns but not yet establishing the value-property as a substantive cross-system business characteristic |
| `b6ef5806…` | transaction analysis code | Maker `cross_function`, Checker flags as potentially overstated; evidence may support `function_scoped` instead |
| `a0f31c66…` | product formulation reference | Maker `industry_scoped` / process_manufacturing, Checker raises blocking concern that the evidence may indicate `source_system_specific` leakage |
| `10d6a495…` | item ownership type code | Maker `cross_function` / classification 'global', Checker flags the cross_function claim as potentially overstated; evidence may instead support `function_scoped`. **Reclassified into §4.1 from the earlier §4.2 Maker-null bucket** — this row's Maker output did contain a complete `draft_recommendation`; it was parked for the substantive scope disagreement, not for a null Maker draft. |

**Disposition (per closure plan):** held as residual. Each row needs a packet rewrite + re-transport to address the specific substantive disagreement. Not in scope for this closeout.

### 4.2 Maker draft null — root cause diagnosed, fix landed (2 rows)

These rows landed at OPERATOR_REVIEW because the bc-ai Maker emitted a truncated structured draft (no `draft_recommendation` field). The Checker correctly refused to admit unverified candidates. **This is a service-side truncation, not a policy or packet-hygiene issue.**

| panel_run_uid | Term |
|---|---|
| `10dc2359…` | item sourcing strategy code |
| `dce3e370…` | expiration control code |

**Root cause:** `BaseAgent.max_tokens` defaulted to 4096 and `RegistryAuthoringMaker` did not override it. The Maker's `evidence_findings` + `draft_recommendation` exceeded 4096 tokens on candidates with verbose multi-source evidence; the JSON truncated mid-stream before `draft_recommendation` was emitted; the Moderator surfaced this as "Maker draft is null". On the focused 4-row sample diagnosed for this checkpoint, both Maker-null rows had `output_tokens == 4096` and a missing `draft_recommendation` key in `agent_outputs_json.maker.structured`; the comparison success row (wage type code) finished at 3753 tokens with `draft_recommendation` present. Across the broader window (`bcf.panel_output_record` since 2026-06-23, `prompt_version='registry-authoring/v1.0'`), 8 of 96 panel runs (8.3 %) hit the 4096 ceiling.

**Fix landed:** bc-ai PR #32 (merge commit `820c5b87`, merged 2026-06-24T16:20:52Z) sets `RegistryAuthoringMaker.max_output_tokens = 8192`, using the existing `BaseAgent` per-instance override pattern (`max_tokens = getattr(self, 'max_output_tokens', max_tokens)` at `app/agents/base.py:191`). The fix is verified live in bc-ai PID 34596 (started 2026-06-24T21:53Z from the merged-main source): a direct import probe of `RegistryAuthoringMaker.max_output_tokens` returned `8192`.

**Disposition:** retry of the 2 packets is a targeted follow-up, not authorized by this checkpoint. C1 closure stance is unchanged (closed with residuals); a separate operator authorization is required before the 2 packets are re-transported.

### 4.3 Mechanical violations (1 row)

| panel_run_uid | Term | Concern |
|---|---|---|
| `2bca6c15…` | quality action resource category code | M4 word-count violation (5 words exceeds the 3-word MUST), plus token-similarity to OAGIS path `quality-action.quality-action-resource.resource-type-code` |

**Disposition:** held as residual. The term itself can be shortened (e.g., 3-word candidate); the M4 violation is a clear packet-hygiene fix, not a policy issue.

## 5. Held semantic rows (2 rows — separate from §4)

These were intentionally held in the RP-3 r3 prep and never transported. They remain held.

| Term | Why held |
|---|---|
| receipt routing code | OAGIS canonical field name is `receipt-routing-code`; the prior attempt renamed to "material condition code" (an OAGIS-listed synonym) and broadened the definition. The OAGIS value enumeration (Customer consignment, Vendor consignment, Inspection, Blocked, Bonded, User defined) mixes ownership and disposition decisions — not a strict material-condition value-property. Three coupled operator decisions are open: term name, scope, distinction from substrate `status`. |
| job code | OAGIS path is `project-accounting.project-accounting.job-code`. The citation phrasing supports workforce job-classification, but the project-accounting parent path makes project/job-number identification a plausible alternative reading. Four candidate readings (workforce / project-accounting / map-to-existing / split) need operator decision. |

**Disposition:** held; await operator semantic decisions. Documented in `bcf-oagis-pass-1-c1-rp3-packet-prep-2026-06-25.md` §5.

## 6. Open threads (carried forward, NOT chased in this checkpoint)

| Thread | Owner / category | Notes |
|---|---|---|
| 6 parked rows pending substantive packet rewrite (§4.1) | C1 residual | Can be re-attempted in a future targeted pass; not blocking C1 close |
| 2 Maker-null rows — root cause diagnosed, fix merged in bc-ai PR #32 (§4.2) | bc-ai service defect (resolved upstream) | Fix landed: `RegistryAuthoringMaker.max_output_tokens = 8192`. Re-transport of the 2 packets is a small targeted follow-up; held until separate operator authorization |
| 1 M4 word-count violation (§4.3) | Packet hygiene | Quick fix on term name; deferrable |
| 2 held semantic rows (§5) | Operator semantic decisions | Open-ended; await operator |

## 7. Authority + verification trail

- **Program authorization:** DEC-f94895 (caps, halt rules) — unchanged.
- **Admission policy:** DEC-ec341c (D453) — proposed (2026-06-24T12:54Z) → decided (2026-06-24T12:55Z) → implemented (2026-06-24T15:31Z, both PRs merged: bc-core #358 `2c2e9170`, bc-ai #31 `fd10726`).
- **Runtime state at checkpoint:** bc-core PID 11768 from `C:\MyProjects\bc-core\dist\main` (merged-main dist), bc-ai PID 24332 from `C:\MyProjects\bc-ai` (merged-main source). Both responsive on `/api/health` and `/docs`. DEC-ec341c code present in compiled bc-core dist (25 admission_scope identifiers in validator.js, 9 in service.js, 1 in repository.js) and in bc-ai source (18 in `registry_authoring_panel.py`, 10 in `maker.md`).
- **DB schema:** `bcf.panel_output_record` carries `admission_scope`, `business_function_code`, `industry_code` (all nullable text). Migration applied 2026-06-24 via `20260624-dec-ec341c-panel-output-record-admission-scope.sql` (also merged into main).
- **Writer guard:** `registry-authoring-orchestrator.service.ts:293` unchanged (the seatbelt). Verified by inspection at PR review time.
- **Smoke check pre-confirm wave:** TX-wrapped INSERT/SELECT/ROLLBACK with `industry_scoped` / `process_manufacturing` round-tripped cleanly; 0 leaked rows.
- **Confirm-wave outcomes JSONL:** `barecount-devhub/.claude/pass1-c1-rp3-confirm-outcomes-2026-06-25.jsonl` — 3 rows, all `outcomeKind: authored`, HTTP 200.
- **Maker truncation fix:** bc-ai PR #32 merged 2026-06-24T16:20:52Z (`820c5b87`); `RegistryAuthoringMaker.max_output_tokens = 8192`. bc-ai restarted from merged main (PID 34596 from `C:\MyProjects\bc-ai` source); direct Python-import probe of the running interpreter confirmed the new cap is loaded. No panel retries authorized from this checkpoint.

## 8. C1 closure stance

**Closed with residuals.** This checkpoint marks the end of active C1 execution under the current program authorization (DEC-f94895). Future work on the residuals is not chased here; it would be a separate, scoped wave.

- **Substrate output:** 16 draft characteristics from the C1 program; 3 new from this checkpoint's confirm wave.
- **Residuals carried forward:** 9 parked from RP-3 retry (6 substantive scope disagreements + 2 Maker-null defect rows + 1 M4 violation) + 2 held semantic rows = 11 residual rows on the original 40-row C1 catalogue.
- **Coverage of the original 40-row C1 catalogue:** 16 confirmed + 11 residuals = 27 rows accounted for at the substrate or held-residual layer. The remaining rows on the catalogue map to either (a) map-to-existing-substrate declarations, (b) operator-decision-packet rejections, or (c) earlier-wave inclusions; these are tracked in the operator-decision packet (`bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25.md`) and not re-tabulated here.

## 9. Scope locks honoured at this checkpoint

- 0 new panel calls (no RP-3 second-retry or RP-4 transport).
- 0 substrate writes beyond the 3 authorized C5 confirms in §1.
- 0 retry-ledger writes.
- 0 C2 entry — explicitly out of scope.
- 3 C5 confirms (the authorized step 4 set: location code, transport service level code, wage type code). Writer concurrency 1; stop-on-non-200 rule armed and not triggered.
- Pre-confirm substrate-collision check returned 0 matches for all 3 terms.

## 10. Next gate

C1 is held at this closure state. No further action authorized in this checkpoint. Future C1 residual work, bc-ai Maker-null diagnosis, and C2 entry each require explicit separate authorization.
