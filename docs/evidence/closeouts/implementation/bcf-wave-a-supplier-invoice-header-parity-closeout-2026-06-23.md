---
title: BCF Wave A — Supplier Invoice Header Parity Closeout (2026-06-23)
description: Closeout of the bounded BCF Wave A Tier 1 — 4 Supplier Invoice header BCs (clearing date, discount, exchange rate, gross amount) authored + activated against existing characteristics in one session. Records substrate deltas, per-candidate IDs, held Tier 2 items, and recommended next wave.
status: closed
authority: implementation-checkpoint
date: 2026-06-23
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-wave-a-tier1
related_docs: [bcf-backbone-breadth-and-batch-doctrine.md, mms-recovery-closeout-2026-06-23.md]
---

# BCF Wave A — Supplier Invoice Header Parity Closeout (2026-06-23)

Wave A Tier 1 closed without halts. Customer Invoice ↔ Supplier Invoice header parity now stands on the 4 cleanly symmetric terms (clearing date, discount, exchange rate, gross amount). 3 CI-only terms (effective date, posted amount, sent date) are deferred per the inventory's tier rules; the first two await an operator semantic decision, the third is excluded by analysis. No new characteristics minted, no new entities admitted, no MCF/CC/OC side effects.

## 1. Substrate deltas (baseline → post-wave)

| Metric | Before | After | Δ |
|---|---|---|---|
| Supplier Invoice active BCs (value kind, header) | 11 | **15** | **+4** |
| Total active BCs (`concept_registry.business_concept`) | 183 | 187 | +4 |
| `bcf.panel_output_record` | 525 | 529 | +4 (1 per candidate, zero retries) |
| `bcf.certification_record` | 4130 | 4138 | +8 (`registry_create` + `registry_transition draft→active` per candidate) |
| Total characteristics | 63 | 63 | **0** — no new characteristic admitted |
| Total entities | 29 | 29 | **0** — no new entity admitted |

Supplier Invoice entity: `4471cb17-df9c-4e36-8d53-01a391c162ce`.

## 2. Per-candidate outcomes

| # | Term | concept_id | concept_version_id | panel_run_uid | create cert | activation cert | Shape verified |
|---|---|---|---|---|---|---|---|
| 1 | clearing date | `e63d51b1-a0d5-45ff-89a6-10c1829dfe8f` | `14b68967-f43c-40f1-82ad-8e629cbaba94` | `d027d38a-f581-49c1-b2d1-eaa01e20b296` | `b9c9d178-df48-4b13-ae26-2b6d345985ec` | `551356d9-cfea-4260-be30-601f4ac498a5` | value / descriptive / date / date / **temporal** |
| 2 | discount | `2ab3ba3f-7207-4107-a6fc-e6ad3611312b` | `674ee107-939e-49d5-9c6e-e90282c36417` | `12b64477-8bdb-47fb-b4ea-ef216307d85f` | `a579a9ba-46c2-4a69-a0dc-7684baa7ce1f` | `aecb4c06-d31e-42d3-a11a-2a4c1aad7f51` | value / descriptive / amount / decimal / **amount** |
| 3 | exchange rate | `4c221c53-3bd8-4e3f-8e7b-ef7eac66848d` | `35d54e0c-daa3-487a-be90-34229c4e8a3c` | `1688787e-73bf-49f3-bf34-d2486b1a069b` | `60ed11f6-0f7e-4f55-9556-006b4e640cd1` | `1e846406-db50-4b43-a60e-6fe60490b267` | value / descriptive / rate / decimal / **amount** |
| 4 | gross amount | `ae6e6528-612f-4f98-9791-ea30baadc6f4` | `e115e524-84b3-46cf-9408-c80f57de2556` | `69676827-9893-418f-8c09-ad6ff4c08bab` | `3380ea26-c767-4bbc-a93d-8c389f121a07` | `4e081ddd-2c49-4ba1-a593-bda551d3b80d` | value / descriptive / amount / decimal / **amount** |

Reused characteristics: `8ef58f34-…` (clearing date), `cdd0a5af-…` (discount), `bd14dd60-…` (exchange rate), `b1621570-…` (gross amount).

Panel latencies: 51.6 – 64.8 s per candidate, no retries.

## 3. Confirmations

- All 4 BCs reused existing active characteristics — no `registry_author_vocabulary` cert fired; total characteristic count unchanged at 63.
- All 4 BCs in `lifecycle_state='active'`.
- Zero duplicate/collision: each `(entity_id, characteristic_id)` pair has exactly one active BC row (verified post-wave against `uq_business_concept_value_identity`).
- Zero panel park, zero REJECT, zero arbitrator override, zero operator-direct fallback.
- Zero cross-framework MCF / CC / OC side effects: no `mcf.*` rows mutated; runtime bc-core (PID 29912 from `C:\MyProjects\bc-core-runtime` at `c63db8ed`) processed all 4 panel calls in normal `mcf_publisher` role flow.
- bc-ai (PID 28444, port 4300) served all 4 panel runs without timeout.
- Dirty `C:\MyProjects\bc-core` worktree untouched.

## 4. Supplier Invoice header — post-wave (15 active value BCs)

```
clearing date         (date / temporal)        ← Wave A
currency code         (code / dimension)
discount              (amount / amount)        ← Wave A
document date         (date / temporal)
document number       (identifier / identity)
document type code    (code / diagnostic)
due date              (date / temporal)
exchange rate         (rate / amount)          ← Wave A
gross amount          (amount / amount)        ← Wave A
invoice receipt date  (date / temporal)
net amount            (amount / amount)
posting date          (date / temporal)
status                (code / status)
system entry date     (date / temporal)
tax                   (amount / amount)
```

## 5. Held / Excluded items

| Term | Disposition | Reason |
|---|---|---|
| effective date | **Tier 2 — held** | CI uses this as a status-validity *timestamp* (`date_time`/`timestamp`). On SI the `posting date` + `system entry date` already cover the temporal arc; operator must decide whether a distinct status-validity timestamp adds value on the AP side. |
| posted amount | **Tier 2 — held** | CI's BCV definition reads "per-line monetary amount as recorded in the accounting", yet the BC is bound to the header — pre-existing semantic ambiguity on the CI side. Mirroring SI faithfully would inherit it; operator must decide whether to fix CI first, mirror as-is, or skip on both sides. |
| sent date | **Excluded** | Buyer never observes a supplier's "sent date" independently — `document date` (supplier-stamped) + `invoice receipt date` (buyer-received) already cover the supplier-to-buyer temporal arc. Mirroring would be redundant and would clutter the AP temporal vocabulary. Do not author on SI. |

## 6. Recommendation — next BCF wave

**Do not run Tier 2 without an operator semantic decision.** Both `effective date` and `posted amount` are decision-heavy on their own merits; bundling them into a "finish Wave A" panel without clarification risks parking the panel (status-validity ambiguity for effective date) or propagating the existing CI-side definition defect (posted amount).

Two viable next directions, each bounded and operator-selectable:

- **Option A — Targeted orphan-characteristic wave.** Address 2–4 of the 6 active orphan characteristics where the entity binding is operator-resolvable (e.g. `expiry date` → Credit Application, `interest rate` → Credit Application / Bank Account, `lead time` → Purchase Order Line / Supplier, `quantity on hand` → Goods Receipt). Each orphan is an independent panel run; halt conditions same as Wave A.
- **Option B — Another safe parity slice.** Likely candidates: Customer Payment ↔ Vendor Payment parity (both at 9 BCs each but their term overlap has not been audited in this session), or Purchase Order Line ↔ Sales Order Line parity (both at 7 BCs each, symmetric in shape and likely already aligned but not formally compared).

Wave A Tier 1 has demonstrated the panel path is clean end-to-end (51–65 s per BC, single panel run, no retries, exact shape match) — both Option A and Option B are unblocked.

## 7. Operational state (carried forward)

- **bc-core**: PID 29912, runtime worktree `C:\MyProjects\bc-core-runtime` at `c63db8ed`, healthy.
- **bc-ai**: PID 28444, port 4300, healthy.
- **Dirty primary worktree** `C:\MyProjects\bc-core`: untouched (still at `f83ac2b7 [main]`).
- **DDL 15** (`idx_mcf_mper_mcv_check_eval_pkg_chain_evidence`): applied, present.
- **bc-docs-v3** working tree: now also carries this closeout doc as untracked; commit batch still deferred per [mms-recovery-closeout-2026-06-23.md](mms-recovery-closeout-2026-06-23.md).
