---
uid: DBCP-mcf-m12-deferred-prereqs
title: MCF M12 deferred prerequisites DBCP
description: Short governance DBCP defining the three deferred prerequisites that must be satisfied before any first real M12 panel run may be operator-authorized. Implements PR #27 §8 step 4. Decision-only; no code execution; no DB mutation in this gate itself.
status: proposed
date: 2026-05-30
project: bc-core
domain: implementation
subdomain: mcf
focus: governance
supersedes: null
superseded_by: null
---

# MCF M12 deferred prerequisites DBCP

Implements **PR #27 §8 step 4**: defines the three deferred prerequisites — allowlist seed, vendor adapter verification, first real M11 intake row — that must be satisfied before any first real M12 panel run may be operator-authorized.

**Decision-only.** No code execution in this DBCP. The mutating prerequisite steps each require their own separate operator authorization, evidence PR, and merge.

---

## 1. Scope / non-scope

### 1.1 In scope

- Naming the three deferred prerequisites that remain after PR #161 + PR #162 closed §8 steps 2 and 3.
- Locking the source, method, evidence shape, and abort rules for each.
- Defining the exact condition that unlocks the next-gate (first-real-M12-run) authorization.
- D1..D8 decisions with recommendations.

### 1.2 Non-scope (explicit)

1. No invocation of `MetricAuthoringPanelService.runPanel()`.
2. No invocation of `M12PanelRunWriterService.writePanelRun()` (standalone) or `.writePanelRunInTx()`.
3. No `M12.5` materialization / `M13` PE-MC / `M14` publication invocation.
4. No metric contract authored.
5. No rollback executed.
6. No tenant DB touch.
7. No DDL.
8. **No DML in this DBCP itself.** The mutating steps (allowlist seed, intake row insert) are each separately operator-authorized follow-up PRs after this DBCP merges.
9. No retraction of PR #160's placeholder row.
10. No re-litigation of PR #157-162 / PR #23-27 governance.

---

## 2. Authority anchor chain

| Anchor | Reference |
|---|---|
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) |
| M12 implementation closeout (pre-A4 era) | `docs/implementation/mcf-m12-implementation-closeout.md` — establishes HA-1..HA-9 + deferred prereqs |
| MCF M14/M12 governance DBCP | bc-docs-v3 main `6d20c8d` (PR #23) |
| MCF M14 unblock apply DBCP | bc-docs-v3 main `2c56151` (PR #24) |
| MCF M12 first real panel-run DBCP | bc-docs-v3 main `ab144f4` (PR #25) |
| MCF M12 trust-path reconciliation DBCP | bc-docs-v3 main `87a52806` (PR #27); O1 Adapter locked |
| M14 unblock implementation | bc-core main `98efc29` (PR #157) |
| M14 unblock apply evidence | bc-core main `e04950d` (PR #158); apply-ts `2026-05-29T16-03-50-994Z` |
| M12 writer real-body | bc-core main `f1a5992` (PR #154) |
| M12 orchestrator O1 Adapter implementation | bc-core main `a0fee4e` (PR #161) |
| M12 orchestrator Adapter SAVEPOINT evidence | bc-core main `9f74d9c` (PR #162); evidence-ts `2026-05-30T03-26-30Z` |
| Allowlist seed script | `bc-core/scripts/mcf-m12-seed-allowlists.mjs` (canonical; idempotent; landed pre-A1) |
| bc-docs-v3 anchor (this DBCP base) | `87a52806` |
| bc-core anchor | main `9f74d9c` |

---

## 3. Substrate state pre-step-4

Live verified via `bc-postgres` MCP at authoring-time:

| Substrate | Value | Status |
|---|---|---|
| `mcf.workspace_tool_allowlist` | **0** | UN-SEEDED — prerequisite §4.1 |
| `mcf.evidence_source_allowlist` | **0** | UN-SEEDED — prerequisite §4.1 |
| `mcf.metric_authoring_intake_queue` | **0** | EMPTY — prerequisite §4.3 |
| `bcf.panel_output_record` | 20 | post-A1 backfill + PR #160 placeholder |
| `bcf.panel_output_record` WHERE `verdict_code = 'APPROVE_FOR_DRAFT'` AND no mapr child | **17** | **Legacy untrustworthy backfill** (A1 lifted these from pre-A4-freeze `contract.panel_output_record`). M12.5 is safe because it reads `mcf.metric_authoring_panel_run` first (zero reachable); any future consumer that reads `bcf.panel_output_record.verdict_code` directly MUST filter via the mapr join to avoid re-introducing trust risk. |
| `contract.panel_output_record` | 19 | frozen by A4 |
| `mcf.metric_authoring_panel_run` total | 1 | PR #160 placeholder; `consensus_payload_json.verdict_code IS NULL` |
| `mcf.metric_authoring_panel_run` WHERE `consensus_payload_json->>'verdict_code' = 'APPROVE_FOR_DRAFT'` | **0** | M12.5 blocker (downstream of step 5). **Note:** M12.5 reads `verdict_code` from the `consensus_payload_json` jsonb field, not a top-level mapr column (see `metric-authoring-materialization.service.ts:364`). |
| `mcf.metric_contract` | 0 | no MCF metric authored |
| `mcf.metric_contract_version` | 0 | same |
| M14 governance gate | OPEN | unchanged |
| A5 rollback envelope outcome | (C) durable | unchanged |

**The three prerequisite tables (`workspace_tool_allowlist`, `evidence_source_allowlist`, `metric_authoring_intake_queue`) are all empty.** None of the prerequisites have begun.

---

## 4. The three deferred prerequisites

### 4.1 Allowlist seed

`mcf.workspace_tool_allowlist` enumerates tools the M12 panel agents may call (e.g., `bcf.search_entity`, `evidence.search`, `kpi_catalog.read_intent`). `mcf.evidence_source_allowlist` enumerates evidence corpora the panel may cite (e.g., `gaap`, `ifrs`, `oagis`, `xbrl_us_gaap`). Both lists are read at orchestrator boot (via `readActiveToolAllowlist` + `readActiveEvidenceAllowlist`); they participate in the **workbench fingerprint** (`mcf-workbench-v1`).

Until seeded, the M12 orchestrator's Step 2 fingerprint computation returns a degenerate fingerprint and Step 5/6 grounding/consensus has no allowed evidence sources to cite against. **No real M12 panel run is possible without these seeds.**

The canonical seed script `bc-core/scripts/mcf-m12-seed-allowlists.mjs` exists, is idempotent (`ON CONFLICT (tool_code, tool_version) DO NOTHING` + `ON CONFLICT (source_code, source_version) DO NOTHING`), and seeds 10 tools + 6 evidence sources per the M12 implementation DBCP §11.1 + §11.3.

### 4.2 Vendor adapter verification

The M12 implementation closeout records vendor adapters (`anthropic-agent.adapter.ts`, `openai-agent.adapter.ts`, `google-agent.adapter.ts` — located at `bc-core/src/registry/mcf/panel-agents/`) as **SHELLS**: their `.run()` method throws on invocation. Vendor SDKs are installed via CodeArtifact (`@anthropic-ai/sdk`, `openai`, `@google/generative-ai`) but the adapter bodies are not yet wired to real model endpoints.

**The first real M12 panel run requires real deliberation by 3 distinct vendor model agents, with role outputs produced exclusively by the approved adapter services calling real provider APIs.** Placeholder transcript content, hand-authored substitute, fixture payloads, directly-constructed role outputs, replayed responses, or fabricated consensus payloads are **ineligible** — they would violate the trust-discipline guarantee that the bcf/mcf framework was built to provide. See §5 and D4 (§10).

### 4.3 First real M11 intake row

The M12 orchestrator's `runPanel(intakeUid, opts, deps)` requires an existing `mcf.metric_authoring_intake_queue` row with `status_code = 'pending'`. The current substrate has zero rows in this table. The first real M11 intake row defines the **candidate metric** the panel will deliberate on:

- `reservoir_name` — provenance source (`seed_metrics` | `metric_definition` | `operator_direct`)
- `reservoir_entry_id` — uid in the source corpus
- `reservoir_provenance_source_json` — provenance trail
- `reservoir_confidence_band` — high / medium / low
- `candidate_name` — proposed metric name
- `candidate_description_text` — natural-language description
- `normalized_candidate_json` — structured candidate spec
- `co_bindings_stripped_flag` — true if CO bindings were removed at intake time

**Until a real intake row exists, the orchestrator has nothing to deliberate on.**

---

## 5. Service/API-only rule for first-real-M12

**First-real-M12 requires service/API-only panel outputs: maker/checker/moderator outputs must be produced by approved vendor adapter services calling real provider APIs. Hand-authored transcripts, fixture payloads, directly constructed role outputs, replayed responses, or placeholder content are ineligible.**

No substitute or fallback path is permitted. The HR1 substrate CHECK (`bcf_panel_output_record_no_synthetic_provider_chk`) is a string filter on the provider tag; it cannot prove API origin, and it cannot be relied upon to detect operator-fabricated content tagged with a real vendor name. The trust premise is provided by the **adapter-emitted provenance** (see D4 §10 + §11 Enforcement), not by substrate CHECKs.

### 5.1 What "service/API-only" means

| Aspect | Requirement |
|---|---|
| Role output origin | Real provider API response, returned by the approved `PanelAgentAdapter.run(...)` implementation for that vendor |
| Vendor `model_identity_json.maker.provider` | `'anthropic'` / `'openai'` / `'google'` (real provider tag emitted by the adapter, not operator-supplied) |
| Provenance fields per role output (emitted by the adapter) | `provider`, `model_id`, `provider_request_id` and/or `provider_response_id` (where available), `timestamp`, `prompt_hash`, `raw_response_hash` (or `transcript_hash`), `status`, `latency_ms`, `usage` (token counts where available) |
| Trust value | The only first-real-M12 trust value defined by this DBCP. Anything weaker is procedural-only and does NOT count as the first real M12 panel run (see §9 + D8). |
| Vendor unavailability behaviour | First-real-M12 run is DEFERRED until vendor service is restored. There is no substitute fallback. |

### 5.2 What is explicitly ineligible

- Hand-authored transcripts (single-operator or multi-operator) presented as panel deliberation
- Fixture payloads, canned JSON responses, recorded SDK fixtures replayed at run-time
- Directly constructed role outputs (any code path that builds a `RoleAgentResult` from operator-supplied content rather than from an adapter API response)
- Replayed prior provider responses (cached transcripts re-used across runs)
- Placeholder / stub content (the PR #160 failure mode)
- Any role output whose adapter-emitted provenance is incomplete, redacted in a way that hides origin, or unverifiable

A run that contains any of the above is a procedural exercise. It does NOT satisfy the first-real-M12 prerequisite under §9 / D8 regardless of how the operator labels it.

---

## 6. Evidence artifact requirements

Each prerequisite step emits durable evidence under `bc-core/scripts/audit-output/`. Mirrors the established pattern from PR #155 / #156 / #158 / #160 / #162.

| Step | Evidence files |
|---|---|
| §4.1 Allowlist seed | `mcf-m12-allowlist-seed-<ts>.evidence.jsonl` (per-row insertions + post-seed counts) + `<ts>.summary.md` (16 expected rows: 10 tools + 6 evidence sources) |
| §4.2 Vendor adapter verification | `mcf-m12-vendor-adapter-verification-<ts>.evidence.jsonl` (per-vendor real provider API call result with adapter-emitted provenance: `provider`, `model_id`, `provider_request_id`/`provider_response_id`, `timestamp`, `prompt_hash`, `raw_response_hash`, `status`, `latency_ms`, `usage`; cost metadata) + `<ts>.summary.md` (all 3 vendors verified via real API per §5 + D4 + §11; no substitute path accepted) |
| §4.3 First real M11 intake | `mcf-m12-first-real-intake-<ts>.evidence.jsonl` (intake row uid + content snapshot + provenance) + `<ts>.summary.md` |

All evidence files are committed to a separate operator-authorized evidence PR per step.

---

## 7. Abort / failure behavior

| Failure point | Behavior |
|---|---|
| Allowlist seed: script fails / partial / unexpected count | Abort. Substrate state captured in evidence; re-run is a fresh operator-authorized event. The script is idempotent so partial state from a prior abort is recoverable. |
| Vendor adapter verification: any of 3 vendors fails to produce a verifiable real-API sample call with full provenance | Abort. Evidence files document the failure (provider, attempted request id if available, error class, retry count, latency). Operator options: (i) fix the failing vendor wiring (SDK version, credentials, network, model id) and re-attempt as a fresh authorized event, OR (ii) wait for vendor service restoration and re-attempt. **No substitute path is available** — the first-real-M12 gate cannot open with fewer than 3 verified real-API vendor adapters (§5 + D4 + §11). |
| First M11 intake row: substrate CHECK violation or upstream-source mismatch | Abort. Re-author the intake content; re-attempt as fresh event. |
| Operator review of any evidence PR rejects the step | The step does NOT complete. The first-real-M12-run unlock gate (per D8) remains closed. |

No auto-retry. Each prerequisite step is its own per-event operator-authorized gate. Mirrors PR #25 D7 discipline.

---

## 8. DB mutation scope

This DBCP **itself** applies no DML. The three prerequisite steps that DO apply DML are:

| Step | DML target | Volume | Authorization |
|---|---|---|---|
| §4.1 | `mcf.workspace_tool_allowlist` + `mcf.evidence_source_allowlist` | 10 tool rows + 6 evidence source rows | Separate operator authorization for the seed run; evidence PR for the seed evidence |
| §4.3 | `mcf.metric_authoring_intake_queue` | 1 row | Separate operator authorization for the intake row insert; evidence PR for the intake evidence |

§4.2 produces no DML (vendor verification is API call validation only).

After this DBCP merges, the operator authorizes step §4.1, then §4.2, then §4.3, each as a separate evidence PR. The unlock condition (D8) requires all three evidence PRs merged.

---

## 9. First-real-M12-run unlock condition

The first-real-M12-run authorization gate (per PR #25 §4.3 env-gate pattern) MAY be opened by the operator only when ALL of the following are true:

1. **This DBCP merged** at bc-docs-v3.
2. **PR #161 (orchestrator O1 Adapter impl)** merged at bc-core (`a0fee4e`) — DONE.
3. **PR #162 (orchestrator Adapter SAVEPOINT evidence)** merged at bc-core (`9f74d9c`) — DONE.
4. **Allowlist seed evidence PR** merged at bc-core. Post-evidence substrate: `mcf.workspace_tool_allowlist >= 10` AND `mcf.evidence_source_allowlist >= 6`.
5. **Vendor adapter verification evidence PR** merged at bc-core. Post-evidence: all 3 approved vendor adapters (`anthropic-agent.adapter.ts`, `openai-agent.adapter.ts`, `google-agent.adapter.ts`) successfully called real provider APIs through their `PanelAgentAdapter.run(...)` implementation, AND captured request-traceable, redacted-where-appropriate provenance per role (per D4 §10 + §11 Enforcement): `provider`, `model_id`, `provider_request_id` / `provider_response_id`, `timestamp`, `prompt_hash`, `raw_response_hash` (or `transcript_hash`), `status`, `latency_ms`, `usage`. No substitute / hand-authored / fixture-replay path is accepted at this gate.
6. **First real M11 intake row evidence PR** merged at bc-core. Post-evidence: `mcf.metric_authoring_intake_queue` row exists with `status_code = 'pending'` and the agreed `reservoir_name` per D3.
7. **Operator confirmation:** all five preceding bullet points complete; explicit per-run authorization recorded.

The env-gate value for the first-real-M12-run authorization (issued by a new DBCP after this one closes) follows the locked PR #25 §4.3 pattern (`BCCORE_M12_FIRST_REAL_RUN_CONFIRM=I_HAVE_REVIEWED_...`) but binds to the prerequisites-complete ts rather than the M14-unblock-apply ts. **That env-gate is NOT defined in this DBCP** — it is the next gate's load-bearing decision.

---

## 10. Operator decisions D1..D8 — recommendations

| # | Decision | Recommendation |
|---|---|---|
| **D1** | Allowlist seed source and method | **`bc-core/scripts/mcf-m12-seed-allowlists.mjs`** — canonical, idempotent, already shipped. No inline DBCP-level SQL; no operator manual SQL. Run via `DATABASE_URL=... node scripts/mcf-m12-seed-allowlists.mjs` with `TENANT_DATABASE_URL=""` shell prefix. |
| **D2** | Vendor adapter proof model | **Real API calls** for maker (Anthropic), checker (OpenAI), moderator (Google). Each vendor adapter must successfully execute a minimal sample call against its real endpoint (cost-bounded; operator-authorized cost ceiling) and the result must round-trip through `panel-role-agent.interface` type-validation **with the full adapter-emitted provenance keys per D4**. No substitute path. If a vendor is operationally unavailable at first-run time, the gate defers per D4 + R3. |
| **D3** | First M11 intake source | **`reservoir_name = 'operator_direct'`** — operator hand-authors a single candidate metric proposal. Smallest path; source-auditable; no dependency on seed corpus or legacy bridge. The candidate metric should be a low-stakes example (e.g., a simple count or sum from a known source) — not a business-critical metric. |
| **D4** | Service/API-only rule for first-real-M12 | **Real API calls from all 3 distinct vendor model agents are mandatory.** Calls must be made through the **approved M12 vendor adapter services** (`PanelAgentAdapter.run(...)` for Anthropic / OpenAI / Google), not by hand-authored transcript injection or any code path that constructs role outputs from operator-supplied content. Each role output must carry **adapter-emitted provider API provenance**: `provider`, `model_id`, `provider_request_id` and/or `provider_response_id` (where the SDK exposes them), `timestamp`, `prompt_hash`, `raw_response_hash` (or `transcript_hash`), `status`, `latency_ms`, and `usage` (token counts where available). If any vendor is operationally unavailable, **the first real M12 run is deferred** until vendor service is restored. **No operator-authored transcript or substitute path may satisfy the first-real-M12 gate.** A substitute attempt is a procedural exercise only and does NOT qualify for the §9 / D8 unlock condition. |
| **D5** | Evidence artifact requirements | **JSONL + summary.md per step**, under `bc-core/scripts/audit-output/`, committed in a separate per-step evidence PR. Shape mirrors the established pattern (PR #155 / #156 / #158 / #160 / #162). |
| **D6** | Abort / failure behavior | **Hard fail at first failing assertion within a step. No auto-retry.** Each re-attempt is a fresh operator-authorized event. Idempotent steps (allowlist seed) recover cleanly from partial state on re-run. Non-idempotent steps (intake row insert) must address the failure cause before re-attempt. Mirrors PR #25 D7 discipline. |
| **D7** | DB mutation in this prerequisites gate | **NONE in this DBCP.** The three prerequisite steps apply DML, but each is separately operator-authorized (see §8). This DBCP is docs-only governance; the mutating steps are subordinate evidence PRs. |
| **D8** | Unlock condition for first-real-M12-run | **All 7 conditions in §9 satisfied.** Specifically: this DBCP merged + PR #161/#162 merged + allowlist seed evidence merged (≥10 tools + ≥6 evidence sources) + **vendor adapter verification evidence merged showing real provider API calls by all 3 approved adapters with full per-role provenance (provider, model_id, provider_request_id/response_id, timestamp, prompt_hash, raw_response_hash, status, latency_ms, usage)** + first M11 intake row evidence merged + operator explicit per-run authorization recorded. **No substitute / hand-authored / fixture-replay attestation may satisfy condition 5.** The next-gate DBCP (first-real-M12-run authorization) is authored AFTER all 7 conditions are met. |

---

## 11. Enforcement (layered)

The service/API-only rule (§5 + D4) is not a documentation convention — it is enforced at multiple layers so that even an operator who attempts to bypass one layer is caught by another.

### 11.1 Code-path enforcement

- The operational M12 orchestrator obtains role outputs **only** through the approved `PanelAgentAdapter.run(input)` interface (the implementations under `bc-core/src/registry/mcf/panel-agents/{anthropic,openai,google}-agent.adapter.ts`). The orchestrator MUST NOT contain any branch that accepts a pre-built `RoleAgentResult` from operator input, environment variables, JSON files, fixtures on disk, or any other non-adapter source in operational mode.
- The adapter `.run()` body MUST call the real vendor SDK (no mock client, no recorded-response replay) and MUST construct the `RoleAgentResult` from the live SDK response.
- Any code path that constructs a `RoleAgentResult` from operator-supplied data is a **test seam**. Test seams MUST be visibly test-only (file name `*.spec.ts`, `__test__/`, `__fixtures__/`, or behind a Vitest-only export) and MUST NOT be reachable from the operational `MetricAuthoringPanelService.runPanel(...)` call site.

### 11.2 Runtime guard

- Operational mode rejects any role output whose adapter-emitted provenance is missing or incomplete. The minimum required provenance keys per role output are: `provider`, `model_id`, `timestamp`, `prompt_hash`, `raw_response_hash` (or `transcript_hash`), `status`. The keys `provider_request_id` / `provider_response_id`, `latency_ms`, and `usage` are required where the vendor SDK exposes them.
- The orchestrator MUST verify the provenance shape BEFORE writing through the O1 Adapter (HA-7 AJV validation already enforces consensus shape; provenance keys are an additive contract).
- Provider tag values are restricted to `{anthropic, openai, google}` for the first-real-M12 gate. Strings outside this set are rejected at the orchestrator boundary regardless of HR1 substrate CHECK.

### 11.3 Lockfile / source guard

- The bcf phase-a3 import lockfile (`bc-core/scripts/bcf-phase-a3-import-lockfile.mjs`) MUST include a negative assertion: no first-real-M12 script (`scripts/mcf-m12-first-real-run.mjs` or any successor) imports a fixture-loading helper, a pre-built `RoleAgentResult` factory, or any code path that bypasses `PanelAgentAdapter.run(...)`.
- A scripted grep gate on `scripts/mcf-m12-*real-run*.mjs` rejects any literal occurrence of `RoleAgentResult` construction, fixture JSON path imports, or `replayPanelTranscript`-style helpers.

### 11.4 Vendor adapter proof PR

- Before the first real M12 panel run, a separate operator-authorized evidence PR (the §4.2 vendor adapter verification evidence PR) runs the 3 adapter `.run()` methods against the real provider APIs once each.
- Captured artifacts: per-vendor `request_id`, `response_id`, `model_id`, `latency_ms`, `usage`, `transcript_hash`. Raw response bodies MAY be redacted; the **hash chain** stays intact and is the audit anchor.
- The proof PR is independent of the first-real-M12 run itself: it proves capability, not consumption.

### 11.5 DB CHECKs are a weak backstop

- `bcf_panel_output_record_no_synthetic_provider_chk` is a string filter on the provider column. It blocks the literal strings `{synthetic, replay, mock, canned}` but cannot prove API origin.
- The CHECK is retained as a defence-in-depth layer. It is NOT the load-bearing trust attestation; the adapter-emitted provenance per §11.1 + §11.2 is.

### 11.6 Operator override of §11 is forbidden by this DBCP

Unlike §7 (per-step abort/failure), the layered enforcement in §11 has no operator override path. An operator who believes a substitute path is acceptable must author and merge a successor DBCP that defines the trust-equivalent attestation. No per-run authorization may waive §11.

---

## 12. Hard rule mapping

- **HR1** — no synthetic / mock / replay / canned data. Allowlist seed content is curated real names (real tools, real evidence corpora). Vendor adapter verification produces real API call results captured with adapter-emitted provenance per §11.1–§11.2 (no operator-authored substitute path is permitted; see §5 and D4). Intake row content is operator-authored real candidate metric. The substrate CHECK `bcf_panel_output_record_no_synthetic_provider_chk` is a defence-in-depth string filter; it is NOT the load-bearing safeguard (see §11.5 and R8).
- **HR2** — when M12 runs (post-prerequisites), writer targets mcf.* via bcf.* anchor (A5 topology); orchestrator owns outer tx (PR #161). Unchanged by this DBCP.
- **HR3** — M12 writer body never imports contract.* (unchanged; lockfile-enforced).
- **HR4** — tenant DB OUT OF SCOPE. All prerequisite steps operate on platform DB only (`bc_platform_dev` via `DATABASE_URL`); `TENANT_DATABASE_URL=""` shell prefix enforces.
- **HR5** — production path; the prerequisite steps prepare for the first real production invocation of `runPanel()`.
- **DEC-7f9597 / D423** — operator authorization required per gate. This DBCP merges, then §4.1 step authorized, then §4.2 step authorized, then §4.3 step authorized; each is a separate event.

---

## 13. Risk register

| # | Risk | Mitigation |
|---|---|---|
| **R1** | Allowlist seed script broken / drifted from substrate shape | Script is pre-shipped, idempotent, and tested in the M12 implementation PR. The script has no `--dry-run` flag — every run inserts; mitigation is to run against an isolated target first, OR inspect the seed rows via a read-only `SELECT` against `bc_platform_dev` before allowing the seed run to mutate, OR rely on the `ON CONFLICT DO NOTHING` idempotency to recover from any partial state. |
| **R2** | Vendor API cost overrun | Per locked D2, operator-authorized cost ceiling for the sample calls. Sample calls are deliberately minimal (single-turn, small token budget). |
| **R3** | Vendor API unavailable / rate-limited at first-run time | **First real M12 run is DEFERRED until vendor service is restored. No substitute fallback.** D2 implementation includes vendor SLA monitoring and a cost-bounded sample-call retry policy; if retries exhaust within the operator-authorized window, the run defers. Deferral is documented in the evidence PR (failure trace + restoration timestamp). |
| **R4** | First M11 intake row content rejected by M12 panel | The intake row's purpose is to feed deliberation; rejection is a valid panel outcome. The `REJECT_DEFECT` path exists in the orchestrator (covered by unit tests in PR #161). Re-attempt with a different candidate is a fresh operator-authorized event. |
| **R5** | Operator authorizes step out of order (e.g., intake before allowlists seeded) | The orchestrator boot reads allowlists at construction time; running M12 with empty allowlists would degrade the fingerprint and likely fail HA-7 AJV validation. D8 enforces explicit ordering. |
| **R6** | M12.5 read predicate mismatch | M12.5 requires `consensus_payload_json->>'verdict_code' = 'APPROVE_FOR_DRAFT'` (jsonb extraction, not top-level column). The first real run may produce `OPERATOR_REVIEW` or `REJECT_DEFECT`; M12.5 invocation remains blocked until an `APPROVE_FOR_DRAFT` row exists. Subsequent runs (per PR #25 D8) can reach that state. |
| **R7** | Prerequisite evidence PRs land out of operator-intended order | Each evidence PR's commit body lists its prerequisites. Reviewer can confirm dependencies. D8 §9 lists the 7 conditions explicitly. |
| **R8** | **Provider-name spoofing** — operator hand-authors content under provider tag `'anthropic'` / `'openai'` / `'google'` to bypass HR1 substrate CHECK | **HR1 CHECK is not the load-bearing safeguard.** The load-bearing safeguard is the §11 Enforcement chain: (i) operational `MetricAuthoringPanelService.runPanel(...)` accepts role outputs **only** through `PanelAgentAdapter.run(...)`; no operator-supplied `RoleAgentResult` branch exists; (ii) adapter `.run()` bodies call the real vendor SDK and construct `RoleAgentResult` from live SDK responses; (iii) runtime guard rejects role outputs lacking provider API provenance keys (`provider_request_id`, `prompt_hash`, `raw_response_hash`, etc.); (iv) lockfile / source-grep gate rejects any first-real-M12 script that constructs `RoleAgentResult` literals or imports fixture loaders; (v) vendor adapter proof PR captures redacted request-traceable provenance per role before the first real M12 run. A spoofed provider tag with no matching request-id provenance is detected at the runtime guard and the orchestrator rejects the panel run. |
| **R9** | **Legacy `bcf.panel_output_record` orphans** — 17 rows with `verdict_code='APPROVE_FOR_DRAFT'` and no `mcf.metric_authoring_panel_run` child exist on the substrate (A1 backfill of pre-A4-freeze contract rows) | M12.5 is safe because it reads from `mcf.metric_authoring_panel_run` first (live count of reachable APPROVE_FOR_DRAFT rows: 0). Future consumers (PE-MC, M14, audit queries) that read `bcf.panel_output_record.verdict_code` directly MUST filter via `INNER JOIN mcf.metric_authoring_panel_run mapr ON mapr.panel_run_uid = bcf.panel_output_record.panel_run_uid`. A bcf-direct consumer without the mapr join would consume the 17 legacy untrustworthy rows. This DBCP records the orphan condition in §3; resolving the orphans (either retraction or re-anchor) is a separate operator-authorized scope (see PR #160 placeholder retraction track). |

---

## 14. Standing gate state target

| State element | Pre-step-4 (today) | Post-step-4 closeout | Post-step-5 (first-real-M12-run) |
|---|---|---|---|
| `mcf.workspace_tool_allowlist` | 0 | ≥ 10 | ≥ 10 (preserved) |
| `mcf.evidence_source_allowlist` | 0 | ≥ 6 | ≥ 6 (preserved) |
| `mcf.metric_authoring_intake_queue` | 0 | 1 (pending) | depends on verdict path |
| Vendor adapters verified | NO (shells) | YES (3 vendors via real provider API calls; full per-role provenance captured per §11.4 — no substitute path) | YES (preserved) |
| First-real-M12-run authorization gate | CLOSED | OPENABLE pending operator confirmation per D8 | OPEN (this DBCP's successor authorizes) |
| `mcf.metric_authoring_panel_run` total | 1 (PR #160 placeholder) | 1 (unchanged) | 2 (+1 from first real run) |
| `mcf.metric_authoring_panel_run` WHERE `consensus_payload_json->>'verdict_code' = 'APPROVE_FOR_DRAFT'` | 0 | 0 (unchanged) | 0 or 1 (depends on panel outcome) |
| `mcf.metric_contract` | 0 | 0 | 0 (M12.5 still gated downstream) |
| M14 governance gate | OPEN | OPEN | OPEN |
| A5 rollback envelope outcome | (C) durable | (C) durable | (C) durable |
| C2 force-rollback envelope DBCP | NOT AUTHORED | NOT AUTHORED | NOT AUTHORED |

---

## 15. Out-of-scope re-statement

This DBCP does NOT:

- Apply DDL or DML against any DB.
- Invoke `MetricAuthoringPanelService.runPanel()`.
- Invoke `M12PanelRunWriterService.writePanelRun()` (standalone) or `.writePanelRunInTx()`.
- Invoke `M12.5` / `M13` / `M14` services.
- Permit any hand-authored, fixture-replay, or directly-constructed role-output substitute path for the first real M12 panel run. The service/API-only rule (§5 + D4) is enforced by §11.
- Author the next-gate (first-real-M12-run authorization) DBCP — that follows this one when prerequisites are complete.
- Author the C2 force-rollback envelope DBCP.
- Touch any tenant DB.
- Mutate PR #160's placeholder row.
- Resolve the 17 legacy `bcf.panel_output_record` `APPROVE_FOR_DRAFT` orphan rows (R9) — that is a separate operator-authorized track.
- Re-touch any merged A1-A5 / M14-unblock / first-real-run / O1-Adapter / SAVEPOINT-evidence PR.

It only **decides** the prerequisites' shape so each subordinate step has a settled premise when the operator authorizes it.
