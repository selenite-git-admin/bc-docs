---
title: "D409 BF-BO Catalog Expansion Factory — SOP / ADR-lite"
date: 2026-05-17
authority: DEC-b8ec00 (D409 — BF-BO Catalog Expansion Factory)
adr: bc-docs-v3/docs/adrs/ADR-b8ec00.md
predecessor: DEC-1ce490 (D408 — contract.business_field is the certified BF-BO catalog)
session: SES-5e0796
type: sop
status: draft
version: 0.1
hands_off_from: D408 — BF catalog admission cleanup
supersedes: none
governing_invariants:
  - I (Meaning is evaluated once)
  - IV (All references are explicit)
  - VI (Evidence is emitted, not inferred)
---

# D409 — BF-BO Catalog Expansion Factory

A disciplined multi-agent workflow that scales BF/BO catalog review capacity **without** drifting back into coverage-chasing. Agents recommend; only governed endpoints/scripts mutate state.

This document is the founding governance artifact for D409. It is **docs-only**: no DB writes, no endpoint calls, no remediation are performed in the act of writing it, and the SOP itself forbids agents from performing them at any other time.

---

## 1. Purpose and non-goals

### 1.1 Purpose

D408 left the catalog in a defensible — but not finished — state. The closeout of `SES-c5af8c` named six residual streams across asset, credit, and ISO 20022 modeling. D409 is the workflow that processes residuals like these *and* the next wave that will follow (depreciation, tax, treasury, payroll, derivatives, etc.) **at scale**, without re-introducing the failure mode D408 was created to remove.

D409 turns BF/BO catalog review into a factory with:

- **A bounded review packet** — one BF or one BF cluster per packet, with the evidence already attached so the reviewer is not the discoverer.
- **A bounded verdict** — six labels, no free text in the decision slot.
- **A bounded write surface** — the four D408 governed endpoints, period. Agents never write.
- **A bounded role split** — Explorer proposes, Skeptic challenges, Moderator decides what reaches the operator.

### 1.2 Non-goals

D409 is explicitly **not**:

- A coverage drive. Coverage is an *output* of admitting only what is defensible, never an *input* that drives admission.
- A re-litigation of D408. The D408 catalog state (`certified_catalog=1,655`, `correction_required=12`, `demoted_catalog=388`, etc.) is the starting state. D409 does not re-open closed rows.
- A new endpoint surface. D409 reuses the four D408 governed endpoints and the 1q-D / 1q-E / 1q-G DBCP patterns. If a new write shape is needed, it is filed as a *new* DBCP/endpoint under D408 substrate, not invented inside an agent loop.
- An agent autonomy framework. Agents in D409 are bounded research and challenge functions feeding a human-operator decision. They do not act.

---

## 2. Agent roles

Three roles, three prompts, three outputs. No role mutates state.

### 2.1 Explorer

**Job.** Given a packet (one residual BF, BF cluster, or modeling question), produce an *evidence-first* recommendation.

**Inputs.**
- Packet payload (§4).
- Read-only DevHub + bc-core read endpoints.
- Standards corpora (US-GAAP SDA, IFRS, XBRL US-GAAP taxonomy, OAGIS, ISO 20022) — as cited evidence, not as automatic admission triggers.

**Outputs.**
- Proposed verdict (one of the six in §5).
- Cited evidence — each citation typed per §4.3.
- Suggested governed endpoint + parameters (recommendation only; the Moderator forwards the recommendation to the operator if the verdict survives).

**Forbidden.** Calling any write endpoint. Inferring evidence ("this looks like a normal asset row, so probably US-GAAP SDA covers it"). Picking a verdict not in §5.

### 2.2 Skeptic

**Job.** Attack the Explorer's recommendation. The Skeptic's goal is to *prevent admission*, not to confirm it.

**Inputs.**
- The Explorer's full packet output.
- The same read-only surfaces.

**Outputs.**
- For each cited evidence item: accepted / rejected / weak, with reason.
- For the proposed verdict: stand / overturn / weaken (e.g. `ADMIT_READY` → `NEEDS_EVIDENCE`).
- A halt flag (§9) if any halt rule is tripped.

**Forbidden.** Inventing new evidence to *replace* the Explorer's. The Skeptic is a filter, not a parallel Explorer. If new evidence is needed, the verdict becomes `NEEDS_EVIDENCE` and the packet re-enters the queue.

### 2.3 Moderator

**Job.** Decide what reaches the operator.

**Inputs.**
- Explorer output.
- Skeptic output.

**Outputs.**
- A single operator-facing packet: final proposed verdict, surviving evidence, suggested governed endpoint call, dissent log (any Skeptic objection the Moderator overruled, with reason).
- A queue-routing decision: forward to operator, return to Explorer for more evidence, or drop into `HOLD`.

**Forbidden.** Calling any write endpoint. Replacing the operator. Hiding Skeptic dissent.

---

## 3. Write boundaries

> **Agents recommend. Only governed endpoints/scripts mutate state.**

The only mutation surface D409 may produce is a recommendation that the **operator** issues against one of the D408 endpoints, or against a new D408-substrate DBCP filed for that purpose.

### 3.1 Allowed write surface (operator-driven, not agent-driven)

Inherited from D408 (see `SES-c5af8c` closeout):

- `POST /api/business-fields/remediate-semantics` (BF semantic remediation, §12 SDA uplift path)
- `POST /api/business-fields/correct-definition` (definition-only correction, no type/structure change)
- `POST /api/business-fields/correct-type` (typed correction with re-verification gate)
- `POST /api/business-fields/admit-from-correction-required` (governed re-admit path; `admit_bf_from_correction_required` action_code from 1q-G)
- Governed DBCP patterns: **1q-D** (no-CC type-incoherence demotion), **1q-E** (A1 MISMATCH `cc_field_mapping` removal), **1q-G** (additive CHECK enum expansion).

If a residual requires a shape these endpoints/DBCPs do not cover (e.g. BF rename, short-named ISO 20022 BO creation), D409 produces a **DBCP draft** that the operator reviews and applies; D409 itself does not apply it.

### 3.2 Forbidden

- Direct `INSERT` / `UPDATE` / `DELETE` against `contract.business_field`, `contract.business_object`, `contract.business_field_object`, `contract.canonical_field`, `contract.canonical_field_mapping`, `contract.certification_record`, or any related catalog table.
- Drizzle migrations or schema patches authored from inside the factory loop.
- Bulk re-mapping of CFs to share source columns just to unblock MCs (see CLAUDE.md: *"funnel padding"*).
- Backdoor admissions to clear `correction_required`.

---

## 4. Packet schema

The unit of work. One packet → one Explorer pass → one Skeptic pass → one Moderator output → one operator decision.

### 4.1 Packet identity

| field | type | notes |
|---|---|---|
| `packet_id` | string | `D409-PKT-{yyyy-mm-dd}-{seq}-{kind}`; e.g. `D409-PKT-2026-05-17-001-asset-orphan-cf` |
| `packet_kind` | enum | `bf-residual` \| `cf-orphan` \| `bo-modeling` \| `cluster-merge` \| `iso20022-modeling` |
| `seed_source` | enum | `d408-residual` \| `operator-raised` \| `audit-finding` (D409 seeds will all be `d408-residual` initially) |
| `predecessor_thread` | string | e.g. `SES-c5af8c` for D408 residuals |

### 4.2 Subject

| field | notes |
|---|---|
| `subject_kind` | `business_field` \| `canonical_field` \| `business_object` \| `cc_field_mapping` \| `bf_cluster` |
| `subject_ids` | array of UUIDs / codes — one for singletons, many for clusters |
| `current_state_snapshot` | read-only capture of `catalog_state_code`, `status_code`, BO membership, alias presence, SDA evidence, `cc_field_mapping` references — taken once, at packet open |

### 4.3 Evidence types (allowed)

Every evidence item carries `{type, citation, location, scope}`. Free-form "we believe..." text is **not** evidence.

| `type` | accepted citation form | scope |
|---|---|---|
| `us-gaap-sda` | concept name + revision date (e.g. `Assets / 2024-Q4`) | A single accounting domain concept |
| `ifrs` | standard + paragraph (e.g. `IAS 16.6`) | One concept |
| `xbrl-us-gaap` | element name + namespace + version | One element |
| `oagis` | property path + bod + revision | One property |
| `iso20022` | message ID + element xpath + version | One element |
| `internal-bo-membership` | `business_object_code` + `is_required` / `is_business_key` | Membership-as-evidence |
| `internal-cc-reference` | `canonical_contract_code` + `cc_field_code` | Already-trusted use |
| `internal-sda-projection` | SDA observation log row id + as-of | Operational evidence |
| `internal-alias` | source system + field code | Alias-as-evidence (weakest tier) |

**Order of precedence (Skeptic enforces).** Standard citations (US-GAAP / IFRS / XBRL / OAGIS / ISO 20022) **dominate** internal evidence. An `internal-alias`-only packet may not reach `ADMIT_READY`.

### 4.4 Output slots (filled by Moderator)

| field | notes |
|---|---|
| `final_verdict` | one of §5 |
| `surviving_evidence` | subset of Explorer evidence accepted by Skeptic |
| `suggested_endpoint` | one of §3.1 (or `dbcp-draft-required`) |
| `suggested_payload` | parameters for the operator's call (illustrative) |
| `dissent_log` | Skeptic objections the Moderator overruled, with reason |
| `quality_gate_results` | §8 |
| `halt_flags` | §9 |

---

## 5. Verdict taxonomy

Six labels. Closed set. No free-text decisions in the verdict slot.

| Verdict | Meaning | Operator's likely next action |
|---|---|---|
| `ADMIT_READY` | Subject is defensible with cited standard-tier evidence; no open Skeptic objection survives | Issue `/admit-from-correction-required` (or appropriate admit endpoint) |
| `NEEDS_EVIDENCE` | Subject *may* be defensible but the packet's evidence is incomplete or all-internal | Park packet; re-queue with additional evidence (operator sourcing or `TSK-926c77` bc-ai panel) |
| `DEMOTE_RECOMMENDED` | Subject cannot be defended under current standards; no upgrade path visible | Issue `demote_bf_catalog` (1q-D-style DBCP if multi-row) |
| `REBIND_RECOMMENDED` | Subject is defensible but is currently bound (BO membership, CF, `cc_field_mapping`) to the wrong target | Re-bind via the appropriate governed endpoint; do not admit until re-bind is clean |
| `DUPLICATE_OR_MERGE` | Subject restates an already-certified BF/BO; the right move is to merge or alias, not to admit a parallel row | Operator decides on merge target; D409 packet stays open until merge is done |
| `HOLD` | A halt rule fired, or the packet exposed a structural gap larger than the packet itself | Stop. Surface to operator. Do not re-queue without resolving the parent issue |

A packet that reaches `HOLD` is a finding, not a failure — it means D409 discovered something the factory cannot resolve on its own.

---

## 6. Pilot scope

Three pilot streams, all seeded from D408 residuals (`SES-c5af8c` closeout). No other queue is opened until these clear.

### 6.1 Asset / `cc__asset` residuals

| seed | count | initial packet kind |
|---|---:|---|
| Orphaned CFs from DBCP-1q-E (A1 MISMATCH `cc_field_mapping` removal) | 45 | `cf-orphan` |
| REVIEW `cc_field_mapping` row (`change_in_value_of_underlying_asset`) | 1 | `bf-residual` |
| INSUFFICIENT_CONTEXT `cc_field_mapping` row (`total_asset_value`) | 1 | `bf-residual` |
| P&L depreciation flow CFs (need new `asset_depreciation_expense_amount` BF) | 3 | `bo-modeling` |

The depreciation cluster is explicitly a **modeling** packet, not a re-bind packet — a new BF must be admitted before the orphan CFs can be rebound. This is the pilot's hardest case and the one most likely to trip §9 halt rules.

### 6.2 Credit / `cc__credit` residuals

| seed | count | initial packet kind |
|---|---:|---|
| Orphaned CFs from DBCP-1q-C (credit type-code mapping removal) | 11 | `cf-orphan` |

Smaller, more uniform — a good control for the asset stream's complexity.

### 6.3 ISO 20022 modeling review

| seed | subject | initial packet kind |
|---|---|---|
| `iso20022_camt_xchg_rate` | 1 BF currently in `correction_required` | `iso20022-modeling` |

The packet's central question is **not** "how do we admit this row as it stands?" — it is "is this row's *shape* defensible, or does ISO 20022 force a different BO/BF structure that we should admit instead?" Expected verdicts skew toward `DEMOTE_RECOMMENDED` (kill the bad shape) + a new `bo-modeling` packet (admit a properly modeled `camt.014`-shaped BF/BO under a real ISO 20022 evidence trail).

---

## 7. D408 → D409 residual ingestion

How the six residual streams from `SES-c5af8c` enter the D409 queue.

| D408 residual stream | D409 packet kind | initial verdict bias | queue priority |
|---|---|---|---|
| 45 A1 orphan CFs (1q-E) | `cf-orphan` | `REBIND_RECOMMENDED` or `DEMOTE_RECOMMENDED` | high |
| 3 P&L depreciation flow CFs | `bo-modeling` then `cf-orphan` | `ADMIT_READY` (new BF) → `REBIND_RECOMMENDED` (orphans) | high |
| 1 REVIEW mapping | `bf-residual` | operator-driven | medium |
| 1 INSUFFICIENT_CONTEXT mapping | `bf-residual` | `NEEDS_EVIDENCE` | medium |
| 11 NEEDS_EVIDENCE definition rows | `bf-residual` | `NEEDS_EVIDENCE` (until `TSK-926c77` bc-ai panel produces standard-tier citations) | medium |
| 1 ISO 20022 `camt_xchg_rate` | `iso20022-modeling` | `DEMOTE_RECOMMENDED` + new `bo-modeling` packet | high (precedent-setting) |

Ingestion rule: each residual stream becomes packets only after the **current_state_snapshot** is taken read-only; the operator verifies the snapshot count matches the D408 closeout numbers (45 / 3 / 1 / 1 / 11 / 1). If the numbers have drifted, the factory does **not** open packets — it raises the drift as a finding first.

---

## 8. Quality gates

Each packet must pass these gates before the Moderator may forward it to the operator. Gate failure pushes the packet back to Explorer (or to `HOLD` if the failure is structural).

| Gate | Test | Failure mode |
|---|---|---|
| G-Evidence-Standard | At least one piece of standard-tier evidence (US-GAAP / IFRS / XBRL / OAGIS / ISO 20022) survives Skeptic review for any verdict in {`ADMIT_READY`, `REBIND_RECOMMENDED`} | `NEEDS_EVIDENCE` |
| G-Evidence-Cite | Every evidence item carries `{type, citation, location}` and the citation is verifiable (not paraphrased) | Reject packet |
| G-Verdict-Closed-Set | `final_verdict ∈ §5` | Reject packet (Moderator bug) |
| G-Endpoint-Match | `suggested_endpoint` matches verdict (e.g. `ADMIT_READY` → admit endpoint, not `correct-type`) | Reject packet |
| G-Snapshot-Stable | `current_state_snapshot` row was unchanged between packet open and Moderator close | Reject packet; re-snapshot |
| G-No-Funnel-Padding | The recommendation does not result in many CFs sharing one source column to clear a downstream MC | `HOLD` |
| G-D408-Substrate-Only | `suggested_endpoint` resolves to a D408 governed endpoint or a filed D408-substrate DBCP draft | Reject packet |
| G-Scope-Single | Packet touches at most one BF cluster (≤ ~50 rows, single domain) | Split packet |

---

## 9. Halt rules

When any of these fire, the Moderator stamps `HOLD` and the packet stops. **No verdict, no recommendation reaches the operator until the halt is resolved.**

1. **Snapshot drift.** The subject row changed between packet open and Moderator close. Catalog state is moving outside the factory; surface it before continuing.
2. **Standards corpus disagreement.** Two cited standard-tier sources disagree on the subject's meaning or shape. Operator must pick the authoritative source first.
3. **Cross-domain spillover.** Resolving the packet requires changes outside its named domain (e.g. asset packet that requires a `cc__revenue` change). Spawn a sibling packet rather than expanding scope.
4. **Endpoint gap.** No D408 endpoint or DBCP pattern can express the recommended write. Draft a new DBCP for operator review **outside** the factory loop.
5. **Foundation invariant test fails.** Per CLAUDE.md §Foundation Invariant Check, a recommendation that would compensate at C–F for a missing A or B definition halts. The fix belongs higher in the stack.
6. **Funnel-padding pattern detected.** Per `feedback_funnel_padding.md` — bulk CF re-pointing to one source column to unblock MCs is a halt, not an optimization.
7. **D408 closeout count drift.** Per §7, if the residual counts at packet open don't match D408 closeout numbers, the factory halts.
8. **Operator-flagged halt.** Operator may halt any packet at any time without justification; restart requires a fresh packet.

---

## 10. Versioning and revision

- This SOP is `v0.1`. The verdict taxonomy (§5), evidence types (§4.3), and quality gates (§8) are **the most likely to evolve** after the pilot lands. Each change is a new version + a one-line changelog entry below.
- Extensions to the closed verdict set or evidence-type set must be made here, not inside an agent prompt.
- A future ADR (DEC- to be allocated) will lift this SOP into a decided artifact once the pilot has produced a representative sample of packets across all six verdicts.

### Changelog

| Version | Date | Note |
|---|---|---|
| 0.1 | 2026-05-17 | Initial SOP (SES-5e0796). Pilot scope = D408 residuals only. |

---

## 11. References

- [D408 correction_required cleanup closeout](../../../../closeouts/onboarding/2026-05-17-d408-correction-cleanup-closeout-DEC-1ce490.md) — source of all six pilot residual streams.
- [D408 BF catalog admission cleanup closeout](../../../../closeouts/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md) — establishes the catalog-state primitive D409 reads from.
- [D408 admit-from-correction-required design](2026-05-17-d408-admit-from-correction-required-design-DEC-1ce490.md) — the new endpoint D409 will most often recommend.
- [ADR-1ce490](../../../../../governance/adrs/ADR-1ce490.md) — *contract.business_field is the certified BF-BO catalog* (D409's parent decision).
- [the-invariants.md](../../../../../foundation/the-invariants.md) — Foundation invariants the §9 halt rules enforce.
- CLAUDE.md §Foundation Invariant Check — repair-location classification + override path.
- `feedback_funnel_padding.md` — the anti-pattern §9 rule 6 forbids.
