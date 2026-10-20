---
uid: DEC-6e951e
title: "Multi-currency semantics are observed, never converted: currency at the OC, per-currency and source-booked local-currency aggregation, and a fail-closed currency gate"
description: "Makes DEC-f4b2b0 effective and implements DEC-7bccf6's source obligation for the Customer Invoice chain: observe document + company currency and the source-booked company-currency amounts; CC projects currency_code + local amounts; each amount metric declares document_currency (per-currency) or local_currency (source-booked scalar); no platform FX; runtime and lifecycle refuse un-supported currency aggregation; stale chain-status rows are not green."
status: proposed
date: 2026-10-20T12:40:13.942Z
project: bc-core
domain: metrics
subdomain: metric-contract/currency
focus: grammar
amends:
  - DEC-f4b2b0
  - DEC-ea4523
---

# Multi-currency semantics are observed, never converted: currency at the OC, per-currency and source-booked local-currency aggregation, and a fail-closed currency gate

## Context

The packet shows currency dropped at observation and gates that do not refuse. Decided doctrine already resolves the core fork. DEC-7bccf6 forbids platform FX, so option A as framed is out. DEC-f4b2b0 already provides per-currency (B) and source-booked local-currency aggregation. Neither is effective, because the OC never observes currency and the runtime and lifecycle gates are not fail-closed. Observing the currency and the source-booked amounts, projecting them in the CC, declaring each metric's policy, and making the runtime, lifecycle and read-model gates refuse closes the hole without inferring any FX. It validates directly against the source's own per-currency and company-currency figures.

## Grounding (2026-10-20 at bc-core and bc-docs origin/main and the platform DB; Platform packet MULTICURRENCY-DESIGN-INPUT-2026-10-20, SES-e9dd87)

**The data.** On `kaveridemo2` the Customer Invoice population is **INR + USD**. Company currency is INR. In August, 63 invoices are INR and 6 are USD (USD 3,538,610). The CO `amount_total` sum for August, **1,006,087,013.23**, is INR 1,002,548,403.23 + USD 3,538,610, added together with no meaning. That makes the ~15 amount and ratio metrics on cc-das36 unsafe.

**Root cause (A): currency is dropped at observation.**
- oc-3kgrr 1.4.0 observes no `currency_id`, although sc-929yc 1.0.0 declares it.
- sc-929yc 1.0.0 **also exposes Odoo's own booked company-currency amounts**: `amount_total_signed`, `amount_untaxed_signed`, `amount_tax_signed`, `amount_residual_signed`, plus `company_currency_id`, `invoice_currency_rate`, and the document-currency `*_in_currency_signed`.
- cc-das36 3.0.0 projects no `currency_code`.

**What is already decided (and stays decided):**
- **DEC-f4b2b0 (D495, implemented)** defines the per-metric `aggregation_currency` policy:
  - `document_currency`: partition per currency;
  - `single_currency_required`: refuse a mixed population;
  - `local_currency`: aggregate the **source's pre-converted** local amount.
- **DEC-7bccf6 (decided 2026-07-30; it supersedes DEC-f6527b):** **"BareCount does not convert currency."** Platform-computed FX and the canonical FX store are retired as wrong in principle. The **source's own booked conversion is authoritative**, and the source must expose the document currency and amount plus the company currency and amount.
- **DEC-ea4523 (3):** integer many-to-one keys that carry codes (`currency_id`) are dereferenced to codes at the observation boundary; `direct` and `code_lookup` do not dereference.

**Gaps found in the implementation:**
- `governed-metric-runtime.ts`:
  - `currencyPartition()` returns `[]` when the spec has no `currencyField`, so a `document_currency` metric sums every currency **silently**;
  - the `single_currency_required` check runs only when the field exists;
  - `local_currency` has **no implementation** (only its defect code is typed).
- **Chain status:**
  - `currency_policy_supported` is amber by design (tenant-agnostic) and **blocks nothing**;
  - **84 of 332** `mcv_chain_status` rows predate the check and still read green. `total_credit_sales` and `credit_sales_ratio` were computed 2026-08-02, before the check existed (2026-08-03), so their GREEN is **stale, not a judging bug**.
- The Odoo reader stores the raw record and implements no many-to-one dereference. A `res.currency` source contract exists (`sc-198em`, active).

## Decision

**Platform's options, resolved:**
- **(A), converting to INR with `res.currency.rate` under a platform as-of convention, is refused.** It is exactly what DEC-7bccf6 retired.
- **(B) is already doctrine**, and this ADR makes it effective.
- **The single comparable scalar comes from the `local_currency` policy over the source's own booked company-currency amounts.** That is Odoo's conversion, recorded at posting.

So the answer is **B plus source-booked local currency**: a hybrid in which **nothing is converted by BareCount**. The FX as-of question (rates end 2026-07 while documents run to 2026-08) **disappears**, because Odoo already booked each USD document's INR amount at its own posting rate.

**D1. Observe currency; never drop it** (repair location A). A new oc-3kgrr version (minor; mappings are additive) observes:
- **document currency:** `currency_id`;
- **company currency:** `company_currency_id`;
- **the source-booked company-currency amounts:** `amount_total_signed`, `amount_untaxed_signed`, `amount_tax_signed`, `amount_residual_signed`;
- the document-currency amounts it already maps (`amount_total`, `amount_untaxed`, `amount_tax`, `amount_residual`).

The ISO 4217 codes are **dereferenced from the source's own currency master**, per DEC-ea4523 (3):
- through a **secondary observation leg on `res.currency` (`sc-198em`)**, using the existing join-semantics mechanism (DEC-0a187d), joined `currency_id` → `id` and `company_currency_id` → `id`, taking `res.currency.name`;
- **not** by a platform map, and **not** by trusting a display label;
- an unresolvable currency key is a recorded refusal.

**D2. Project currency at the CC** (repair location B). A new major cc-das36 version projects:
- `currency_code`: the document currency;
- `local_currency_code`: the company currency;
- the four source-booked local-currency amount fields, each a BCF concept on the Customer Invoice entity (authored and published through the BCF sequence before CC authoring; existing concepts are reused where they already exist).

**Integrity cross-check (refusal, Inv-VI):** `local_currency_code` must equal the resolved LE's declared functional currency (`dim_legal_entity` / the DEC-4aa1ff D10 attribute). A mismatch is a recorded resolution refusal (`local_currency_mismatch`), never coerced.

**Sign semantics:** the `*_signed` amounts carry Odoo's document-direction sign (credit notes are negative) **as booked**. That is a declared meaning of these concepts, not a transform. A metric that wants gross invoice magnitudes filters `document_type_code = customer_invoice`. A metric that wants net billing (the DSO family) sums the signed amounts.

**D3. Each amount metric declares its policy deliberately** (B, DEC-f4b2b0 D1). There is no blanket default. Each of the ~15 amount and ratio metrics on cc-das36 is re-declared, through Metric's re-author on the SOP rail under an approved family package, as either:
- **`document_currency`:** one value **per document currency**, multi-valued output, keyed by `currency_code`. It validates **directly** against Odoo's per-currency sums (e.g. August INR 1,002,548,403.23 and USD 3,538,610); or
- **`local_currency`:** one value in the company's functional currency, aggregating the **source-booked** company-currency amount. It validates against Odoo's own company-currency total (Σ `amount_*_signed` over the same population).
- **Ratios:** numerator and denominator must share one currency basis. A ratio over `document_currency` operands is per currency, and mixing the two bases is refused (DEC-fa7c63 D-7 composite rule).
- **Counts** declare `not_applicable` (D520).
- The held `gross_revenue → untaxed` correction rides in this same re-author.

**D4. The currency gate is fail-closed** (repair location D for the runtime twin, F for the read model). It is an engine change: Platform builds it and Codex reviews it in the platform lane.
- **(a) The runtime refuses; it never sums blind.** In `governed-metric-runtime.ts`, a currency-denominated aggregation is refused unless its policy is supported by the spec:
  - `document_currency` or `single_currency_required` with no `currencyField` → `MC_DEFECT_CURRENCY_UNSUPPORTED`;
  - `local_currency` with no bound local amount, or a null one on any CO → `MC_DEFECT_LOCAL_CURRENCY_MISSING`, now implemented;
  - an **unset** policy is treated as `single_currency_required`, the DEC-f4b2b0 default for new metrics, **never** as "legacy, no check".
  - "Currency-denominated" uses the same test as the chain judge: a binding with unit `currency` or representation term `amount`.
- **(b) The lifecycle refuses.** Certification, activation and evaluation of a currency-denominated metric refuse while its `currency_policy_supported` is not `pass`.
  - The chain-status verdict for that case moves from amber to **red** (`fail:currency_policy_unsupported`). The "tenant-agnostic" amber rationale no longer holds once the runtime refuses for every tenant: the metric is genuinely non-evaluable.
  - A tenant's declared `currency_posture_code = single_currency` is a declaration, not evidence, so it does **not** waive the requirement.
- **(c) Stale chain status is never green.** Each `mcv_chain_status` row records the **check-set version** it was computed under. A row computed under an older check set reads `stale`, and consumers (the close gate, certification, readiness, dashboards) treat it as **not green** until an explicit refresh. Reads still never trigger evaluation; the refresh is the explicit `POST …/refresh` act. Platform runs the refresh across all 332 rows after the check-set column lands.
- **(d) Authoring refuses.** The MC authoring preflight refuses a currency-denominated MC whose grain CC lacks the field its declared policy needs.

**D4 scope note.** D4 hardens the **currency** gate only. Its sibling **DEC-b01ed4** hardens the rest of the class:
- "green" means the spec assembles against the active grain CC;
- closed-set values are canonical at observation, in filters and at runtime.

The two share D4(c)'s check-set staleness mechanism. The Customer Invoice payment-status `code_lookup` (DEC-b01ed4 G5) rides **this ADR's** new oc-3kgrr version, so there is one OC version and one fresh admission.

**D5. Validation follows the source's own figures, with no inference.**
- Per-currency values validate against Odoo's per-currency sums.
- Local-currency values validate against Odoo's own company-currency totals.
- Both are "Validated against LC5" under the existing seam (DRIVE §6c).

**D6. Explicitly out of scope** (DEC-7bccf6 left these open, and this ADR does not settle them):
- group or consolidation reporting in a currency no entity booked in;
- ECB/RBI reference rates (diagnostic only);
- any FX as-of convention.

## What Platform, DB, BCF and Metric build (each reviewed separately, after this ADR's terms grant)

1. **BCF:** concepts for the document currency code, the local currency code and the four source-booked local amounts on Customer Invoice (reuse existing ones; the operator confirm if high-risk).
2. **Platform contracts (SOP rails):**
   - a new oc-3kgrr version (D1);
   - a `res.currency` observation contract on sc-198em;
   - a new major cc-das36 version (D2), with the secondary-leg join and the local-currency cross-check.
3. **Platform engine (Codex platform lane):** the D4(a) runtime refusals plus the implemented `local_currency`; D4(b) the lifecycle refusal plus the red verdict; D4(c) the check-set version and staleness; D4(d) the preflight.
4. **DB:** the `mcv_chain_status` check-set-version column (a bc-db migration; operator DB yes).
5. **Metric:** re-declare each amount metric's policy (D3) under an approved family package, including `gross_revenue → untaxed`.
6. **Prove-on-one, then many:** re-admit on a fresh tenant (the OC version change requires a fresh admission). Validate first one `document_currency` and one `local_currency` metric against LC5, then the family.

## Foundation (DEC-79b62f)

1. **Location:** **A**, observation, is the root cause: the currency was dropped. **B**: the CC projection and each metric's declared policy. **D/F**: the fail-closed runtime twin and an honest read model.
2. **Not upper:** the source is complete. It carries the currency and **its own booked conversion**.
3. **Not lower:** a platform FX conversion is the lower-layer compensation DEC-7bccf6 forbids. A runtime `GROUP BY` guess, or an amber that does not block, is compensation too. The gates now **enforce declared rules**, not detect after the fact.
4. **Design act** (DEC-c48b0f): declare the observation, the projection and the per-metric policy. Execution acts follow.

**Invariants:**
- **I:** currency meaning is produced once, at the source's booking.
- **II:** order is unchanged.
- **III:** new versions only, and a fresh admission.
- **IV:** currency is an explicit, observed reference, dereferenced from the source's own master.
- **V:** fresh evaluations.
- **VI:** refusals are recorded, conversions are never inferred, and stale diagnostics are never presented as current.

## Needs an operator decision

1. **Confirm the reading that DEC-7bccf6 rules out platform FX** (option A as framed), so the scalar is the source-booked `local_currency`. Recommended: yes. The alternative would be a new ADR superseding DEC-7bccf6.
2. **Per-metric policy:** may Metric pick `document_currency` vs `local_currency` per metric under an approved family package, or does the operator want one rule for the whole family? Recommended: per metric, with `local_currency` for the headline amounts and `document_currency` where per-currency analysis is the point.
3. **Hardening amber to red** (D4b) will **redden** today's amber amount metrics, and certification and activation of those metrics will be refused until D1–D3 land. Recommended: yes. That is the truthful state.
