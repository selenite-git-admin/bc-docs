---
uid: bcf-mcf-evidence-boundary-operator-decisions-d1-d11
title: BCF/MCF Evidence Boundary — Operator Decisions D1..D11 (record of authorization for PR #11)
description: Operator decision record for the BCF/MCF Evidence Boundary + contract.* Schema Retirement DBCP (`bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md`, merged at bc-docs-v3 main 6f8cc159f6f21b6170c3d3195df616a1aa567348). Records the operator's verdicts on the 11 decisions D1..D11 enumerated in §11 of the parent DBCP. Option A (full BCF isolation via new `bcf.*` schema; framework_code patch rejected) is now the chosen architectural direction. D3 and D5 are obsolete under Option A. D7 (contract.framework_policy placement) is deferred to a separate policy/governance placement DBCP. D8 authorizes PR #133 to merge only as inventory/snapshot tooling. D9 keeps the PR #133 apply gate paused until Phase A1+A2 designs are accepted. D10 confirms tenant DBs out of scope. D11 confirms legacy metric.* retirement out of scope. **NOT EXECUTED.** This decision record authorizes the next planning gate (Phase A1 DBCP) — it does NOT authorize any DDL apply, data migration, FK redirect, writer flip, or M11/M12/M12.5/M13/M14 invocation. M14 remains CLOSED. Tenant `tbc_{slug}_dev` databases remain untouched and out of scope. Legacy `metric.*` schema (16,820 rows including 2 active AR pilot KPIs) remains preserved and out of scope.
status: decided
date: 2026-05-28
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-mcf-evidence-boundary-operator-decisions
---

# BCF/MCF Evidence Boundary — Operator Decisions D1..D11

## 1. Purpose

This is the operator decision record for the BCF/MCF Evidence Boundary + `contract.*` Schema Retirement DBCP. It records the operator's verdicts on the 11 decisions D1..D11 enumerated in §11 of that DBCP and stands as the formal authorization for the next planning gate (Phase A1 DBCP).

This record is **not** the architectural decision — the architectural decision is in the parent DBCP, which describes the four options (A, B, C, D), the architectural conflict between the new hard rules and M5 §5 D-M5-B, the five Option A migration phases (A1..A5), and the sequencing constraints. This record only captures the operator's choices.

## 2. Authority

| Artifact | Location | State |
|---|---|---|
| Parent DBCP | `docs/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` | merged at bc-docs-v3 main `6f8cc159f6f21b6170c3d3195df616a1aa567348` (PR #11 squashed 2026-05-28T16:06:05Z) |
| Operator hard rules HR1..HR5 | parent DBCP §5 | restated below for reading convenience; not re-litigated here |
| Decision source | parent DBCP §11 (D1..D11) | this record fills in the operator-must-confirm column |

## 3. Decisions (verbatim verdicts)

| # | Decision (parent DBCP §11 text, abridged) | Verdict | Note |
|---|---|---|---|
| **D1** | Accept that HR3 ("no MCF writes to generic `contract.*` authoring tables") directly conflicts with M5 §5 D-M5-B + M12 DBCP B1 and cannot be resolved without operator action | **ACCEPT** | The conflict is documented in parent DBCP §6 and is the reason a boundary decision is required. |
| **D2** | Choose target ownership model: A (full BCF isolation — create `bcf.*` schema) / B (rejected) / C (rejected) / D (rejected) | **A** | Option A is the chosen direction. Ownership clarity beats short-term DDL minimization. Framework_code column (Option B) is rejected as a patch, not a boundary. |
| **D3** | (Conditional on Option B) amend HR3 to admit `framework_code='mcf'` writes | **OBSOLETE under Option A** | Option B not chosen. HR3 stands as written. No amendment required because MCF will not write to `contract.*` once Phase A5 ships. |
| **D4** | Authorize Phase A1 + A2 design (separate DBCP per phase): A1 creates `bcf.*` schema + 4 evidence tables; A2 migrates 3,568 authority-bearing BCF rows. PR #133 apply gate stays paused until at least A1+A2 designs are accepted | **ACCEPT** | Phase A1 design is authored separately (see `bcf-evidence-schema-phase-a1-dbcp.md`). Phase A2 design is downstream of A1. |
| **D5** | (Conditional on Option B) M5 §5 D-M5-7 ("no `contract.*` CHECK extensions") is overridden | **OBSOLETE under Option A** | Option A does not extend `contract.*` CHECK constraints; it creates new `bcf.*` tables and retires (Phase A4) the `contract.*` evidence tables. D-M5-7 stands as written. |
| **D6** | Authorize the 5-phase migration sequence (A1..A5; each phase its own DBCP). Bounded effort; each phase operator-authorized in isolation | **ACCEPT** | The sequence is A1 (schema creation) → A2 (data migration) → A3 (writer/reader flip) → A4 (freeze or retire `contract.*` evidence tables) → A5 (MCF FK reconsideration + M12 writer flip). |
| **D7** | `contract.framework_policy` placement (stays in `contract.*` / moves to `governance.framework_policy` / moves to `policy.framework_policy`) is deferred to a separate policy/governance placement DBCP | **DEFER (separate gate)** | The 3 framework_policy rows continue to function in `contract.*` during Phases A1..A5. Placement gate is not bundled with the BCF authoring-evidence migration. |
| **D8** | bc-core PR #133 dry-run script may merge as inventory/snapshot tooling; merge is not required for Option A to proceed | **MERGE PERMITTED as inventory tooling** | PR #133 is not closed. It is not superseded. It is also not yet authorized for merge in this record — merge is a separate explicit operator instruction. The framing under Option A is that PR #133's 3 scripts + 3 artifacts catalog the 11 smoke rows at byte fidelity; under Phase A2 this becomes useful provenance documenting which rows were NOT migrated to `bcf.*`. |
| **D9** | bc-core PR #133 apply gate stays PAUSED until Phase A1 + A2 designs are accepted. Apply executes against `contract.*` BEFORE Phase A2 migration (so smoke debt is retired before authority rows move) | **PAUSE until post-A1+A2-design** | The apply gate is paused under all conditions until both Phase A1 and Phase A2 design DBCPs are operator-authorized. Sequencing: smoke retirement → Phase A2 migration (not the reverse). |
| **D10** | Tenant result DBs (`tbc_{slug}_dev`) remain out of scope under this DBCP | **OUT OF SCOPE** | No tenant DB connection is opened by any work spawned from this decision record. Substrate-enforced via separate DB connections (`DATABASE_URL` vs `TENANT_DATABASE_URL`). |
| **D11** | Legacy `metric.*` retirement remains out of scope under this DBCP; the 2 active AR pilot KPIs + ~16,818 supporting rows are preserved | **OUT OF SCOPE** | `metric.*` retirement is reserved for a separate gate alongside M17 tenant-runtime migration. Not bundled with the BCF authoring-evidence boundary. |

## 4. Authorized next gates (derived from D1..D11)

The decisions above authorize the following bounded planning chunks. They do NOT authorize any DDL, DML, code change, or operational run.

| Gate | Authorization basis | What is authorized | What is NOT authorized |
|---|---|---|---|
| Phase A1 DBCP authoring (`bcf.*` schema design) | D2=A + D4 + D6 | Author the substrate-only design DBCP for the new `bcf.*` schema + 4 evidence tables | DDL apply, data migration, code change, writer flip, FK redirect, MCF substrate touch |
| Phase A2 DBCP authoring (3,568-row migration design) | D4 + D6 | Will be authorized once Phase A1 DBCP ships; not yet authorized | All downstream activity |
| PR #133 merge as inventory tooling | D8 | Permitted but not yet executed; requires separate explicit operator instruction | Apply gate execution; PR #133 script edits to `bcf.*` (scripts stay targeting `contract.*` because that is where the smoke debt lives) |
| Policy/governance placement DBCP | D7 (deferred) | Not authorized by this record. Standalone gate when operator chooses | Anything bundling this with the BCF authoring-evidence boundary |

## 5. Hard boundary rules (restated; from parent DBCP §5)

These remain in force across all gates spawned from this decision record:

- **HR1** — No synthetic / mock / replay / canned data written to persistent substrate
- **HR2** — MCF evidence belongs in `mcf.*`
- **HR3** — Future MCF metric authority events must NOT write to generic `contract.panel_output_record` / `contract.calibration_event` / generic `contract.certification_record`
- **HR4** — Tenant result DBs are separate and out of scope
- **HR5** — Mocks only inside unit tests or SAVEPOINT-rolled-back integration tests

## 6. Explicit non-scope (mirrored from parent DBCP §14)

- ❌ Tenant `tbc_{slug}_dev` databases — out of scope (D10)
- ❌ Legacy `metric.*` retirement — out of scope (D11)
- ❌ `contract.*` chain tables (~127k rows: `source_contract`, `admission_contract`, `canonical_*`, `observation_*`, `chain_status`, `chain_trace`, `mc_integrity_state`, `l_node_*`) — out of scope; different concern from authoring boundary
- ❌ `mcf.*` substrate — not touched (Phase A5 will revisit the FK design, but that is a downstream gate)
- ❌ M11 / M12 / M12.5 / M13 — operational gates remain closed
- ❌ M14 — remains CLOSED
- ❌ M13/M12.5 closeout docs — not amended by this record (Phase A5 will require successor amendments)
- ❌ bc-core code — no service-code change is authorized by this record (Phase A3 will be the writer/reader flip gate)

## 7. Discipline assertions (this decision-record session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — this record is bc-docs-v3 only |
| No DDL applied | ✓ |
| No DML applied | ✓ |
| No M11 / M12 / M12.5 / M13 / M14 invocation | ✓ |
| `bc-postgres` MCP `allow_write=false` throughout | ✓ |
| No `mcf.*` touched | ✓ |
| No `metric.*` touched | ✓ |
| No `contract.*` row mutation | ✓ |
| No tenant `tbc_{slug}_dev` DB connection opened | ✓ |
| PR #133 not modified | ✓ |
| No-synthetic hard rule respected | ✓ |

## 8. Cross-references

- Parent DBCP: `docs/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` (bc-docs-v3 main `6f8cc15`)
- Next planning gate: `docs/implementation/bcf-evidence-schema-phase-a1-dbcp.md` (authored alongside this record; same PR)
- Predecessor cleanup DBCP (smoke debt): `docs/implementation/bcf-authoring-test-row-cleanup-dbcp.md` (bc-docs-v3 main `0f42662`)
- Implementing PR (paused apply gate): bc-core PR #133 (`bcf-authoring-test-row-cleanup-pr1-dry-run`, HEAD `d00a34b7`)
- M5 substrate DBCP: `docs/implementation/metric-context-framework-m5-panel-substrate-dbcp.md` (D-M5-B hybrid composition decision; Phase A5 will revisit)
- M12 panel DBCP: `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` (B1 review patch; Phase A5 will revisit)

---

**End of decision record. Decisions D1..D11 are operator-authorized. No DDL apply, no data migration, no PR merges authorized by this record alone — each requires its own explicit operator instruction at the gate it governs.**
