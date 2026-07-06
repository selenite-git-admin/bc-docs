---
title: "D409 cc__intangible_asset scope decision — broad CC, narrow first apply"
date: 2026-05-17
authority: DEC-b8ec00 (D409 — BF-BO Catalog Expansion Factory)
adr: bc-docs-v3/docs/adrs/ADR-b8ec00.md
sop: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md
modeling_policy: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-credit-facility-modeling-policy.md
scoping_packet: bc-core/scripts/audit-output/d409-intangible-asset-scoping-packet-2026-05-17.md
predecessor: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-asset-queue-closeout-DEC-b8ec00.md
session: SES-d6ec9f
type: scope-decision
status: decided
version: 1.0
governing_invariants:
  - I (Meaning is evaluated once — scope defined once at CC creation)
  - IV (All references are explicit — explicit field families, not implicit)
  - VI (Evidence is emitted, not inferred — first apply requires standards-tier anchor)
---

# D409 — `cc__intangible_asset` scope decision

Sets the CC scope before authoring it. The decision is **broad scope, narrow first apply**. This note settles the modeling boundary; the next operator session creates the CC, admits one BF, and inserts one mapping.

---

## 1. Problem statement

The cc__asset queue closeout (bc-docs-v3@41642b9) handed off one row to the intangible-asset destination: `amortization_expense`. The scoping packet (bc-core@023c05e) confirmed:

- `cc__intangible_asset` does **not** exist.
- Only 1 in-scope CF was found (`amortization_expense`).
- No certified BF anchors the concept; the path is admission via the standing factory (`intangible_asset_amortization_expense_amount`, `us-gaap:AmortizationOfIntangibleAssets`, ASC 350-30-35-6).
- Mapping is blocked until the CC exists.

The blocker is therefore a **CC scope decision**: how broadly should `cc__intangible_asset` be defined? Settling this now avoids the cost of re-creating or re-versioning the CC every time an intangible-related row is discovered.

---

## 2. Options considered

### Option A — Narrow CC just for amortization

Scope the CC to amortization concepts only (amortization_expense, accumulated_amortization). Defer intangible balance-sheet items, impairment, and goodwill to separate CCs.

- **Pro:** smallest scope; trivial first apply.
- **Con:** future intangible balance-sheet rows (carrying amount, accumulated amortization balance, impairment) require a new CC or a version bump. Repeated re-creation cost.

### Option B — Broad intangible-asset CC

Scope cc__intangible_asset broadly to cover the intangible-asset object: amount/cost/carrying amount, accumulated amortization, amortization expense, impairment, write-down. Hold goodwill as an explicit operator decision (it may belong here or in a separate `cc__goodwill`).

- **Pro:** single coherent domain for the intangible-asset object; matches the cc__asset pattern (which covers cost, NBV, depreciation expense, ARO, capex, disposition under one PP&E CC).
- **Pro:** first apply remains narrow (one CF + one BF + one mapping); broad scope doesn't force coverage chasing because the factory still requires standards-tier evidence per row.
- **Con:** slightly larger CC-creation scoping conversation; goodwill question must be settled.

### Option C — Split intangible / goodwill / amortization into separate CCs immediately

Create three CCs at once: `cc__intangible_asset` (balance), `cc__amortization` (income flow), `cc__goodwill` (separate balance-sheet line).

- **Pro:** absolute domain separation.
- **Con:** triple the CC-creation work for a queue that today has 1 in-scope row. Goodwill and intangible-other-than-goodwill share enough structure (both ASC 350) that splitting feels premature. Also creates the cross-CC binding question (which CC owns amortization_expense for goodwill vs other intangibles?).

---

## 3. Decision

**Option B — broad intangible-asset CC, narrow first apply.**

This mirrors the cc__asset pattern (a single CC for an entire object's balance-sheet + flow lifecycle) and the cc__credit pattern (a single CC for credit facility concepts with axis-style filters). It avoids both Option A's re-creation cost and Option C's premature splitting.

---

## 4. Rationale

1. **Avoid repeated CC re-creation.** Every intangible-asset concept (amortization, carrying amount, impairment) lands in the same CC. Adding new concepts is a `field_selection` extension on the existing CC, not a new CC.
2. **Preserve domain coherence.** ASC 350 covers intangibles and goodwill as one accounting subject (with goodwill as a special case). Splitting now without operator-confirmed reason creates a cross-CC binding question that doesn't currently exist.
3. **Still avoids coverage chasing.** Broad CC scope ≠ broad first apply. The factory's "READY only after standards-tier evidence" rule still applies per row. The first apply admits exactly **one** BF for exactly **one** CF.
4. **Compatible with D409 factory machinery.** The reusable apply chain (createBf → admit-from-candidate-import → field-selection → addMappings) works identically against a broadly-scoped CC.
5. **Mirrors cc__asset's success.** cc__asset's hybrid generic-first modeling policy worked at scale across depreciation, write-off, disposition, ARO, and capex. The same pattern applies to intangibles.

---

## 5. Initial CC scope

**Proposed domain:** `intangible_asset`.

### 5.1 Initial field families (in scope)

The CC's `field_selection` will be allowed to grow into these families over time, starting from the narrow first apply:

| Family | Concept examples | ASC anchor (typical) |
|---|---|---|
| Intangible amount / cost / carrying amount | gross intangible asset amount, intangible carrying amount | ASC 350-30-25, 350-30-35 |
| Accumulated amortization | balance of amortization recognised to date | ASC 350-30-35 |
| Amortization expense (flow) | period amortization charge | ASC 350-30-35-6 (`us-gaap:AmortizationOfIntangibleAssets`) |
| Impairment / write-down | intangible-asset impairment loss | ASC 350-30-35-14 / ASC 350-30-35-18 |
| Useful life / remaining life | finite-lived intangible amortisation period | ASC 350-30-35-2 / 35-4 (only if a future CF arrives needing it; not in initial scope) |

### 5.2 Goodwill — held for operator decision

Goodwill (ASC 350-20) is intangible but has special accounting treatment (no amortization for public business entities; impairment-only). It can go either here or in a separate `cc__goodwill`. **Hold this decision until the first goodwill CF arrives at this queue.** Do not include goodwill in the initial `field_selection`.

### 5.3 Explicitly out of scope

- **EBITDA / depreciation-and-amortization aggregates** (8 CFs found in the scoping packet). These belong in an income-statement CC, not here.
- **Goodwill** until decided (see §5.2).
- **R&D capitalised costs** (ASC 730 has special rules; route through cc__r_and_d or similar if/when needed).

---

## 6. First apply scope (narrow)

Exactly:

1. Author short DEC for cc__intangible_asset (optional — this scope-decision note may suffice as the authoritative scope record under DEC-b8ec00; operator decides).
2. Verify the `intangible_asset` business_object exists; author if not.
3. Call `POST /api/onboarding/cc/preview` with the minimal CC shape (BO=intangible_asset, grain TBD by operator, no initial mappings).
4. Call `POST /api/onboarding/cc/create` if preview is clean and has no unexpected side effects.
5. Run the standing D409 factory chain:
   - `createBf asset_depreciation_expense_amount`-style → `admit-from-candidate-import` for `intangible_asset_amortization_expense_amount`.
   - `add-field-selection` for the one new BF.
   - `addMappings` for one row: `amortization_expense` → `intangible_asset_amortization_expense_amount`, `resolutionRuleCode='sum'`, `filterJson={period_basis:'period_total'}` (or whatever the operator decides for the period dimension; the CF name doesn't carry it).

**No other rows.** No second BF. No bulk admit of the 40 non-certified candidates surfaced in the scoping packet.

Expected post-state on completion: `bf_total 7069→7070`, `certified_catalog 1662→1663`, `admit_bf_from_candidate_import 7→8`, `ccfm 1616→1617`.

---

## 7. Guardrails

1. **Do not bulk-import the 40 non-certified candidates.** Each must clear the factory's READY bar per row before admission.
2. **Do not add goodwill** to `field_selection` until the operator explicitly decides the `cc__intangible_asset` vs `cc__goodwill` question.
3. **Do not map EBITDA / D&A aggregate CFs** here. Those belong in an income-statement CC.
4. **Do not touch the income-statement CC.** Out of scope for this queue.
5. **No tenant onboarding** unless the operator explicitly approves. The CC-creation orchestrator may have tenant side-effects; the operator must verify.
6. **No metric promotion.** Out of D409's scope.

---

## 8. Next implementation sequence

Strict order, each step a separate operator session:

1. **(Pre-flight, read-only)** Verify the `intangible_asset` business_object exists in the catalog. If not, author it via the BO authoring path (operator-driven, out of scope for this note).
2. **CC preview** — `POST /api/onboarding/cc/preview` with `{businessObjectCode: 'intangible_asset', grain: [...], temporalGate: {...}, fieldExclusions: [...], fieldMappings: []}`. The `field_selection` will auto-derive from the BO composition + exclusions. Goodwill-related BFs (if present on the BO) should be added to `fieldExclusions` per §5.2.
3. **CC create** — `POST /api/onboarding/cc/create` only if preview is clean, the auto-derived `field_selection` matches the §5.1 scope, and the orchestrator reports no unexpected side effects (no CM re-pin to chase, no tenant onboarding).
4. **BF admission** — run the standing factory chain for `intangible_asset_amortization_expense_amount`:
   - `POST /api/business-fields` → candidate_import.
   - `POST /api/business-fields/:id/admit-from-candidate-import` → certified_catalog with the ASC 350-30-35-6 evidence.
5. **Field-selection extension** — `POST /api/onboarding/cc/:contractId/field-selection` if the new BF wasn't auto-included by the CC-preview field-selection derivation. (May be skipped if the BO composition included it.)
6. **Mapping insert** — `POST /api/onboarding/cc/:contractId/field-mappings` with one mapping for `amortization_expense`.
7. **Verify** — pre/post invariants; per-mapping read-back; check that `cc__intangible_asset` v1.0.0 exists; check that the BF is `certified_catalog`; check that the mapping shape is exactly as expected.

---

## 9. References

- `Scoping packet` — the read-only finding that motivates this decision.
- [cc__asset queue closeout](../../../../closeouts/onboarding/2026-05-17-d409-asset-queue-closeout-DEC-b8ec00.md) — recommended opening intangible next.
- [D409 modeling policy v0.1](2026-05-17-d409-credit-facility-modeling-policy.md) — the hybrid generic-first pattern this CC follows.
- [D409 SOP v0.1](2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md) — the broader governance contract.
- [ADR-b8ec00](../../../../../governance/adrs/ADR-b8ec00.md) — DEC-b8ec00 (D409).
