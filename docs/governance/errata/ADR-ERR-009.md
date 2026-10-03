---
id: ADR-ERR-009
title: "DEC-ca8943 states G2's date rule and G4's grain-contract rule as universal; both vary by gate shape, and pure compositions bind through their operands"
status: open
authority: authoritative
affected: DEC-ca8943 (D650) — Decision D2, the G2 and G4 rows of the entry-gate table
resolution: correction recorded here; the entry-gate decision stands; G2 and G4 are read per member class and per gate shape as below
opened: 2026-10-03
---

# ADR-ERR-009 — DEC-ca8943: G2 and G4 depend on the member class and the gate shape

## Contradiction summary

DEC-ca8943 D2 states two rules as if they held for every member:

- **G2** refuses "a structured declared date basis … that is neither the gate's declared `anchor_field` (DEC-26f75a) nor, when no anchor is declared, the grain canonical contract's `posting_date_field` concept". That is the `period_aggregate` rule (ADR-ERR-008). Other gate shapes select rows by other fields, or by no date at all.
- **G4** refuses "a grain with no active canonical contract … an anchor, filter or required currency field not declared in that contract's resolved schema". A **pure composition** binds no business concept. It reads upstream metric snapshots and aggregates no rows, so it needs no grain canonical contract (DEC-fa7c63 Amendment 4). Its bindability is its operands' bindability. And for `as_of` the contract must declare more than the anchor: the closing field, or the series keys and tiebreak.

Applied literally, the two rules fail every pure composition on G4, and they misjudge the date basis of every non-`period_aggregate` shape. The first census did exactly that (barecount-devhub `claude/metric-clean-directory-census` @c627c171).

## Implementation behavior

Read at bc-core `51cb955fc2011fb53ded1707b7d912fbe27f5896`:

- **Rows are selected per shape** in `src/boundary/select-by-gate.ts`:
  - `period_aggregate`, `point_in_time` and `instantaneous` resolve to identity at the boundary (`:27`, `:101`, `:497`);
  - trailing and rolling windows measure on a stamped event field (day unit) or on stamped fiscal periods (DEC-6fd09d D-1) (`:75-95`);
  - `as_of` open or closed item uses `anchor_field` and `closing_field`;
  - `as_of` `latest_observation` uses `anchor_field`, the series key fields and an optional tiebreak field (DEC-d3492b).
- **The package projection carries each shape's own parameters:** `src/registry/mcf/package-signature.service.ts:80-110`, where `point_in_time` carries only `anchor_role` (`:90-93`).
- **`point_in_time`'s `anchor_role`** is used in three places outside row selection. The realization projection resolves it to the bound anchor concept (`mcf-realization-projection.service.ts:194-205`). The fixture structural check C-FX-8 requires the anchor variable to be supplied (`fixture-structural-check.service.ts:606-640`). The directory generator writes it (`metric-directory.service.ts:295-302`). **No row-selection evaluator reads it.** For `point_in_time` the boundary is identity.

## Resolution

DEC-ca8943 D2's G2 and G4 rows are read as follows. Every other check and every other decision point stands.

**Member classes.**
- **Base:** binds at least one business concept or entity.
- **Pure composition:** every non-constant binding is a `metric_input` (DEC-0f3e57) or a `calendar_context` (DEC-6fd09d D-2), and it binds no business concept (DEC-fa7c63 Am.4).
- **Mixed:** both kinds of binding. It follows the base rules for its concept and entity bindings, and the composition rules for its metric inputs.

Constant bindings are ignored.

**G2 and G4 for base and mixed members, by gate shape:**

| Gate shape | G2: the structured date basis must be | G4: the grain contract must declare |
|---|---|---|
| `instantaneous` | none (no date basis) | no date field |
| `period_aggregate` | the gate's `anchor_field` if declared; otherwise the contract's `posting_date_field` (ADR-ERR-008) | `anchor_field` if declared; otherwise `posting_date_field` |
| `cumulative_to_date` | the stamped fiscal period (posting date) | `posting_date_field` |
| `trailing_window` / `rolling_window`, fiscal-period unit | the stamped fiscal period (posting date) | `posting_date_field` |
| `trailing_window` / `rolling_window`, day unit | the bound stamped event field | that event field |
| `as_of`, open or closed item | `anchor_field` and `closing_field` | both |
| `as_of`, `latest_observation` | `anchor_field` | `anchor_field`, every series key field, and the tiebreak field if declared |
| `point_in_time` | **referred to the panel (advisory), neither PASS nor FAIL**, until `anchor_role`'s meaning is defined (open question below) | no date field at gate level |

For every base or mixed member, whatever the shape, G4 also requires that the grain has an active canonical contract, that every bound and filter concept is in its resolved schema, and that a currency field is declared where the currency policy requires one (DEC-f4b2b0).

**G2 and G4 for pure compositions:**
- **G2:** no own date basis. Each operand's snapshot selection must match that operand's shape (PE-MC-14). The structured currency check applies only if the composition declares an amount output.
- **G4:** no grain canonical contract is required. **Every operand passes G4 in its own right** (recursively), and every `calendar_context` code is governed.

**Open question (owner: Architect with Platform).** What `point_in_time`'s `anchor_role` means for row selection is not defined: the boundary treats the shape as identity. Until an ADR defines it, a `point_in_time` member's date intent is an advisory flag for the panel, never a gate verdict.

## Effect on the current directory

The matrix-applied census is barecount-devhub `claude/metric-clean-directory-census` @33e85e92, rows CSV sha256 `fac3a9d7…`. The Architect recomputed its totals from the CSV and checked its canonical-contract facts against the live platform database, read-only, on 2026-10-03.

- **Overall:** 120 of 265 member versions pass all five checks. Every G2 failure is also a G4 failure; none is definition-text drift.
- **Canonical contract work to make the current base members bindable:**
  - **12 grains with no active canonical contract** (43 base members): Asset, Contract, Tax Line, Budget, Customer Invoice Line Item, Revenue Recognition Line, Bank Account, Maintenance Order, Debt Instrument, Hedge Instrument, Customer Payment, Vendor Payment.
  - **9 fields missing from 5 existing contracts** (47 base members):
    - customer_invoice: clearing_date, document_date, due_date, document_type_code, debit_credit_code;
    - supplier_invoice: clearing_date;
    - gl_account: cash_flow_category;
    - journal_entry_line: line_type;
    - journal_entry: entry_method.
- **Pure compositions:** 37 pass through their operands; 54 fail because an operand fails, and are re-judged once their operands pass.

These are definitional findings on the platform plane (DEC-ca8943 D3). They say nothing about whether a tenant can produce values.

## Resolution state

Open until the gate evaluator's specification takes the class × shape table above as its truth table (one red-first case per row), and the `point_in_time` question is decided. Source of the table: barecount-devhub `artifacts/architect/clean-directory-2026-10-03/MATRIX-entry-gate-by-shape-and-class.md` (PR 245 @88c4032b). This entry corrects that matrix's statement that only the projection and the corrective cohort read `anchor_role`. Recorded by the Architect, SES-b9b0ef, 2026-10-03.
