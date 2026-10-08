---
uid: DEC-ab630a
title: "OCT-02 is green-field, mechanical-integrity-first: the Metric Directory is a decoupled intent/spec dictionary (base-registry + composition DAG), and integrity is a three-layer discipline (mechanical to compute to value)"
description: "Phase A of the OCT-02 drive is re-axed to a green-field, mechanical-integrity-first model; the Metric Directory is a decoupled intent/spec dictionary whose load-bearing role is the base-measure registry + composition DAG; integrity is enforced in three ordered layers."
status: decided
date: 2026-10-08T09:44:21.134Z
project: bc-core
domain: metrics
subdomain: metric-directory/drive-model
focus: the green-field mechanical-integrity-first Phase-A model; the directory's load-bearing role; the three integrity layers
---

# OCT-02 is green-field, mechanical-integrity-first: the Metric Directory is a decoupled intent/spec dictionary (base-registry + composition DAG), and integrity is a three-layer discipline (mechanical to compute to value)

## Context

The OCT-02 drive, under the Integrity Assurance thesis (2026-10-08, memory `project_barecount_product_thesis_2026_10_08`), needed Phase A defined. A grounded study of the directory charter (`docs/operating-model/metric-directory.md` §1/§2, `authority: authoritative`, DEC-c3e57f, Invariants I & IV) plus a read-only substrate audit (element #1, TSK-05d5b2, PR #263, Chief-verified) established:

- The Metric Directory is the metric-side peer of BCF — a **self-contained intent/spec dictionary, decoupled from the catalog**, not the built inventory. The two sets overlap only where a member is realized: of 451 catalog contracts, 190 have no directory member; of 434 directory members, 173 have no contract.
- Its contents are **degraded**: 153/226 live base members are unbound (no measure), only 35/246 are realizable, and there is a 34/93 column-vs-ledger realization desync (latent hygiene — the back-link column `member.realized_metric_contract_uid` is vestigial; the ledger `realization_operative` is realization-of-record per DEC-fa9424).

In-place cleanup of 434 drifted rows would spend effort making a legacy layer look trustworthy. The thesis's own logic — re-gate everything, prior approvals void — argues instead to **re-derive the trustworthy core** and triage the legacy against it.

## Decision

1. **DIRECTORY ROLE.** The Metric Directory is the intent/spec dictionary, decoupled from the catalog; its load-bearing role under Integrity Assurance is the **BASE-MEASURE REGISTRY + the COMPOSITION DAG**, not the full 434-member dictionary and not the industry/pack tree. A member is REGISTERED (exists, with a decided intent); REALIZED (has an operative contract) is a separate, optional back-link. **Directory cleanliness is NOT realization.** Resolves the charter §11 parked role question.

2. **THREE INTEGRITY LAYERS**, in order, each gating the next:
   - (1) **MECHANICAL/REFERENTIAL** — the Seed↔Directory↔Catalog skeleton holds: references resolve, no orphans, the base/composite DAG is sound and acyclic, provenance traces. Deterministic; no compute, no Odoo, no panel.
   - (2) **COMPUTE/DEFINITION** — the integrity bar on a contract: the deterministic machine gate (binding/grain/temporal/closure/misbound-input/currency/vocabulary) is primary and hard, **AND** a residual true-meaning certification-panel FIT verdict is still required, per **DEC-92f709** (this ADR does **not** supersede it; the residual panel stays).
   - (3) **VALUE/VALIDATION** — the active metric reproduces a named source's figure (Odoo LC5 as a robustness harness, never the certifier), append-only.
   - Seed stays **SECONDARY** (authority flows Directory→Catalog; Charter §8).

3. **PHASE A = GREEN-FIELD, KEEP-WHAT-MAPS.** Derive a fresh minimal integrity-core (base-measure × grain registry + composition DAG) from the union of [directory members ∪ orphan catalog contracts ∪ the Odoo-computable triage], then triage the legacy rows AGAINST it — keep what maps, **nothing inherits trust** (every row re-passes the mechanical checks). The soft target is the provable/doable delta across the union (a live read, never written, DEC-b049f6).

4. **THE CORE**, adopted on verified evidence (element #1, PR #263, Chief-reproduced): base = **22 distinct (measure × grain) pairs** over 63 grained bound base members (expandable to ~32 as the ~10 measures on the 26 active-orphan contracts are adopted-or-retired); composition = **114-member DAG, clean** (0 cycles, max depth 6); keep-what-maps backlog = 153 unbound base + 10 no-current-version + 58 underived derived + 26 active-orphan contracts; one latent-hygiene defect (the realization column-vs-ledger desync, DB-lane remediation later).

## Consequences

- Supersedes the in-place directory-reconciliation framing of Phase A (old DRIVE-2OCT Stage 2) and the panel-centric certify framing of Stage 4. DRIVE-2OCT §6/§6b are re-spec'd to the three-layer sequence (A0 mechanical-integrity audit → A1 adopt-core → B integrity bar → C validate).
- Binds to the Integrity Assurance thesis.
- References **without superseding**: DEC-92f709 (the integrity bar / residual panel), DEC-fa9424 (directory realization-of-record), DEC-b049f6 (readiness-projection count authority), DEC-0f3e57 and DEC-ada203 (base/composite architecture).
- **Next:** Layer 2 build converges the deterministic entry-gate checks and runs the 22 base pairs through them.
- **Open:** the realization column→ledger one-source-of-truth repair (DB-lane, DB rule 4, DEC-1918d0); leg 3 (Odoo ~900) appended later as unvalidated candidates; the member-level directory→seed lineage needs the A5 seed-ledger surface (lower priority, seed secondary).
