---
id: ADR-ERR-013
title: "DEC-eb612b §6.1/§7.1 cannot execute under D575: the proof-currency leg must be EMITTED at the act, read mcf-only on the served process"
status: adopted
authority: authoritative
affected: DEC-eb612b (D688) §6.1 (arm-S currency rule) and §7.1 (the VALIDATED read-time projection) — the placement of the "the proof still projects current" leg at READ time as a demo-plane re-derive
resolution: bc-db 0066 (mcf.demoed_bridge_proof_attestation) + bc-core credit-read path made mcf-only (resolveBridgeCredit, readClaim, chain arm S), both draft; no change to the DEC-eb612b decision (BR1–BR6 stand)
opened: 2026-11-11
---

# ADR-ERR-013 — DEC-eb612b: the Demoed-bridge currency leg is unsatisfiable at read time under D575

## Contradiction summary

DEC-eb612b (Phase A) placed one leg of the §6.1 arm-S currency rule — *"the proof still projects current"* —
at **read time**, as a re-derive over the demo plane (memo §6.1/§7.1; the Inv-V framing *"consumers validate
the record's currency at read time"*; the 0065 header *"V (consumers re-check currency at read time)"*). The
VALIDATED projection (§7.1) and chain arm S (§6.1) are consumers that run **only on the served process**.

Under **DEC-89db41 / D575** the served `:3100` process holds no demo-plane credential (`assertServedCredentialSource`,
main.ts), and it never can (the demo plane is the exposure-isolated plane). So that read-time demo re-derive is
**structurally unsatisfiable on the served process**: `resolveBridgeCredit → DemoProofProjectionService.readPinCurrency`
opens a guarded demo transaction with no demo URL, which throws, and the catch mapped the throw to
`proof_not_current`. Grounded live (freeze-1044 `e8b1a15a`): both demoed bridge heads (`customer_invoice_volume`,
`ar_balance_outstanding`) return `bridgeCurrencyRefusal = proof_not_current` and `customer_invoice_volume` stays
CERTIFIED — no bridge can ever surface VALIDATED, however correctly it was authored. The design carried a latent
D575 contradiction it never addressed.

This is an **error, not a policy change**: as written, the design cannot execute on the one process its consumers
run on.

## The conforming reading (what changes is mechanism and wording, not the decision)

Currency is **evaluated once, at the governed act** (which CAN reach the demo plane), **emitted as evidence**, and
read **by reference** on the served process — Foundation I (evaluate once), VI (evidence emitted, not inferred at
read). Concretely, the errata names all of:

- **(a) The attestation is the currency evidence.** A new append-only control-plane sibling,
  `mcf.demoed_bridge_proof_attestation` (bc-db 0066, 15 columns), records the full `readPinCurrency` verdict and
  the stored hashes it verified (contract content sha, oracle-custody-set sha, consumed-CO digest, the proof's CO
  store, the ccy-grid flag, the verdict, the failed legs, the checker version, actor, a ≥40-char rationale). It is
  immutable; the **latest row per bridge head** is that head's currency; a `not_current` row is **emitted
  staleness** that withdraws credit. It is written by two governed acts: **W1** — a new bridge is *born attested*
  in the bridge act's own SERIALIZABLE transaction (the step-2 pin already verified current); **W2** —
  `attestBridgeProofCurrency`, a new governed act (CLI `demoed-bridge-attest-cli`) that re-runs `readPinCurrency`
  and appends `current` or `not_current`. A **thrown** reader (unreachable plane / auth failure) is fatal and is
  never recorded: an attestation records a verdict, never an outage.

- **(b) The served credit read is mcf-only, and the served process never holds a demo credential (D575
  unchanged).** `resolveBridgeCredit`, `readClaim`, and `McvChainStatusService.bridgeCredit` decide credit from mcf
  alone: the control-plane rule, the head's **latest attestation**, and the **one mcf-side leg** (the governed
  content-sha of the proof's own world) re-checked live on `CONTROL_PLANE_DB`. The demo projection reader leaves
  the credit-read path entirely; the served process gains no demo-plane dependency. This is sound because, of the
  seven `readPinCurrency` legs, five are immutability-backed facts (Inv III — once true, true forever), one is the
  mcf-side leg (re-checked live at read), and exactly one (the whole-store CO digest) can go stale, only by a
  governed demo promote, which **(d)** bounds.

- **(c) Bridge authoring and attestation are governed CLI-only acts.** The HTTP `POST …/demoed-bridge` refuses by
  name (`bridge_authoring_cli_only`); both the bridge act and the attestation act run only as governed CLIs
  (`demoed-evidence-bridge-cli`, `demoed-bridge-attest-cli`), because they re-derive the proof on the demo plane
  the served process cannot hold. (Folds in RULING F-a/F-b.) The `GET …/demoed-claim` read is unaffected.

- **(d) R-4 — the drift-ordering rule.** A governed promote into a CO store named by any current attestation
  (`co_store_code`) must, in the same governed runbook, re-run W2 for every affected head; those heads then carry
  `not_current` and credit is withdrawn until re-bridged. Today this is a runbook/precheck gate (structural form —
  the promote CLI invokes W2 post-commit — is follow-up F-3). Only `co_cc_das36_v5_1_0` is affected, and no promote
  into it is planned on R2's path.

- **(e) Coverage checker v2 fail-closes on non-period gates.** The v1 checker drew `variable_role` witnesses from
  period-membership rows **whatever the gate shape**. For an `as_of` metric (e.g. `ar_balance_outstanding`, a SUM
  of outstanding), period membership is **not** the exercised population, so those witnesses do not evidence the
  role (Inv VI). Checker `demoed-coverage-v2` derives role witnesses only for `period_aggregate`; for any other
  shape each `variable_role` is **uncovered, fail-closed** (never borrowed from period membership). Consequently
  `ar_balance_outstanding` is refused `b5_coverage_insufficient` under v2 and must be re-bridged under v2 (with
  fresh dispositions) before it can be attested or credited; `customer_invoice_volume` (period_aggregate COUNT) is
  unaffected and proceeds.

- **(f) The corrected refusal vocabulary.** The served credit ladder's named refusals are, in order:
  `unreconciled` · `snapshot_hash_stale` · `mc_hash_drift` · `residue_undisposed:<…>` ·
  `proof_currency_unattested` · `proof_not_current:<failed legs>` · `proof_contract_superseded` ·
  `proof_currency_unverifiable` (a thrown mcf-side pin read, the corrected meaning of the former
  `demoed-bridge-head.ts:168` catch — the served path no longer calls the demo reader at all).

## What the decision keeps (DEC-eb612b stands unchanged)

BR1 (the act), BR1a (identity), BR2 (coverage / residue / provenance labels), BR3 (arm S may satisfy
`self_verification` from a current covered head), BR4 (VALIDATED = certified_active + a current covered head,
rendered as a **read-time projection** — still projected at read, not stored), BR5 (what never transfers) and BR6
(no cascade) all keep their terms. The C8 battery is untouched: `metric_audit.fn_intrinsic_decision_refusal` c1–c15
byte-unchanged, no c16. Only the **mechanism and wording** of §6.1/§7.1 and the Inv-V line change — from a read-time
demo re-derive to an act-time emitted attestation with the mcf-side leg re-checked at read.

## Why an errata, not a successor ADR

The decision's guarantees are intact and the staleness window is **bounded and stated** (whole-store CO growth by a
governed promote, handled by R-4). That matches an errata — "the ADR as written cannot execute under a binding
constraint it never addressed; here is the conforming reading" — not a reversal. A successor ADR would be needed
only if the operator rejected R-4's bounded-staleness reading and insisted on instant demo-drift visibility on the
served process; that would require widening the D575 served guard to admit a demo READ login, which is rejected (it
reintroduces the 2026-11-09 serve landmine and puts a second plane's credential into the internet-facing process).

## Provenance

Grounded read-only at bc-core freeze-1044 `e8b1a15a` (= served `:3100`), bc-db `origin/main` (0065 applied live),
and the live `bc_platform_dev` (SELECT-only). Architect memo
`artifacts/architect/MEMO-demoed-bridge-credit-read-path-2026-11-11.md` (DLV-039f42). Build (draft, under Codex
platform-lane landing + a gated apply/serve the Chief sequences): bc-db `0066` and the bc-core credit-read path.
This errata corrects the author's own earlier G6 ("readClaim is mcf-only"), which checked that `readClaim` *writes*
nothing outside mcf and wrongly inferred it *reads* nothing outside mcf.
