---
id: ADR-ERR-012
title: "DEC-ffbc24 §4 Layer-A premise wrong: company_id is already observed on the SO; no re-observe needed"
status: adopted
authority: authoritative
affected: DEC-ffbc24 (D673) §4 (Layer-A observation prerequisite) and §5/M-4 (honest-cost + G3 sequencing) — the claim that the source company key is not observed
resolution: bc-core PR #963 (merged — regression guard pinning the company_id-observed invariant); no design change to DEC-ffbc24
opened: 2026-10-21
---

# ADR-ERR-012 — DEC-ffbc24 §4: the Layer-A company_id premise is disconfirmed

## Contradiction summary

DEC-ffbc24 §4 declared, as a **blocking** activation prerequisite, that LE-bearing observation contracts
do **not** observe the source company key: *"oc-3kgrr does not fetch the SO columns needed, and Kaveri's
reader never fetched `company_id`"* — and §5/M-4 inflated the opaque-id activation cost with a
`company_id` **re-observe → re-admit → re-emit** chain, sequenced behind a "G3 admission fix."

Grounded at bc-core `origin/main` (689dd240 / ca2989eb) and the live `bc_platform_dev` registry, this is
**factually wrong**:

- All four LE-bearing posting-fact observation contracts **declare `company_id` in their `so_schema`**:
  `oc-vg0zn` (journal_entry / cc-dh5d9), `oc-h827j` (journal_entry_line / cc-x13pb),
  `oc-3kgrr` (customer_invoice / cc-das36), `oc-jbpz8` (supplier_invoice / cc-7174p); the parent source
  contracts declare it too, so each `fact.so_*` table carries the column.
- `deriveFetchFields` (`resolved-admission-context.ts`) unions **all** `so_schema.properties` into the
  fetch list; the Odoo executor fetches them and admission coerces the many2one `[id, name] → id` onto the
  scalar SO column. So a declared `company_id` **is** observed and projected.
- The `kaveridemo` G3 admission HALT cited by §4 was a **different field — `currency_id`** (`nullable:false`,
  not observed) hitting a storage NOT NULL — already resolved by bc-core **PR #959** (source-family columns
  no longer projected NOT NULL; source-required enforced at admission as SC-required ∩ observed). It was
  never a `company_id` problem.

Independent corroboration: the per-family LC5 validation (DLV-f771c6) computes its oracle by filtering
`fact.so_sc_snedd` on **`company_id = 1`** — which only yields the validated figures if the admitted Source
Objects already carry a populated `company_id`.

## Resolution

- The §4 **requirement** (the LE-bearing SO must carry the source company key so the canonical boundary can
  resolve the legal entity) is **already satisfied** at origin/main. No `company_id` re-observe / re-admit
  chain is needed; the §5/M-4 re-observe **cost for `company_id` is zero**; the "G3-first" sequencing
  referred to a currency issue already fixed.
- **No design change** to DEC-ffbc24: the LE axis, the universal opaque-id stamp, the source-to-entity
  binding resolution, the per-LE evaluator/reader changes, and the opaque-id/D9 migration are unchanged.
  Only the factual Layer-A premise and the associated cost/sequencing in §4/§5/M-4 are corrected.
- bc-core **PR #963** (merged 2026-10-21) adds named regression guards pinning the invariant
  (`deriveFetchFields` includes `company_id` from `so_schema`; the many2one → scalar `id` coercion onto the
  SO column) so a future refactor cannot silently break the LE stamp's input.

## Note on review provenance

DEC-ffbc24's §4 premise survived five Codex rounds and three adversarial red-team rounds because all of them
inherited the same stale reading (that the OCs do not declare / the executor does not project `company_id`).
The disconfirming datum was found only when Leg 0 of the build grounded the claim directly against the live
registry and the admission code. Recorded here as the standing correction; verification is a direct source
read, not a review consensus.
