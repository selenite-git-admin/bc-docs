---
uid: DEC-1fa08f
title: "Chain Audit Service (CAS) — read-only verifier with 5-mode lifecycle gating"
description: "Chain Audit Service (CAS) — read-only verifier with 5-mode lifecycle gating"
status: decided
date: 2026-06-16T00:46:03.486Z
project: bc-core
domain: platform
subdomain: chain-engines
focus: verification
---

# Chain Audit Service (CAS) — read-only verifier with 5-mode lifecycle gating

## Context

See decision text below.

## Context

The platform's governance evidence is distributed across 11 tables. Each authoring service mints its own evidence. But cert rows alone are not sufficient proof that the chain is correct — substrate can drift after certification:

- A BC supersession can leave older MVBs pointing to a now-superseded BCV
- A canonical_value_set update can invalidate prior MC filter literals
- An OC v(N+1) can introduce a field mapping that conflicts with an existing CC field selection
- A package_signature_hash recomputed today may diverge from the one cited in an M14 cert

For calculator-grade production, the existence of governed-write cert rows is not enough. The system needs an **independent verifier** that re-reads the substrate and proves the chain is still correct.

## Decision

Introduce a **Chain Audit Service** (CAS) — a read-only, deterministic verifier that re-derives evidence from current substrate and certifies chain readiness across five lifecycle modes:

- `pre_m12_audit` — substrate ready before authoring?
- `pre_m13_audit` — draft MCV structurally sane before PE-MC eval?  **(v1 ships this mode only)**
- `pre_m14_audit` — are PE rows complete + replayable?
- `pre_runtime_release_audit` — safe to bind to tenant/runtime?
- `regression_audit` — re-check active metrics after substrate changes

**CAS NEVER authors. CAS NEVER mutates. CAS produces signed evidence.**

CAS is the sibling of the Chain Enrichment Engine (CEE, separate ADR). Two-Person Rule: the auditor must not trust the authoring path. The auditor defines what "correct enough to proceed" means; CEE will be built to satisfy CAS's specification.

## Locked decisions

| D | Topic | Choice |
|---|---|---|
| D4 | Audit evidence table | New `mcf.chain_audit_evidence` (NOT mixed with `certification_record`) |
| D5 | Finding taxonomy | Fixed registry `AUDIT_FINDING_REGISTRY_V1`, enum CHECK on `findings_json[*].finding_code` |
| D6 | Mode chaining | Strict superset: `pre_m14 ⊇ pre_m13 ⊇ pre_m12`; `pre_runtime_release ⊇ pre_m14` |
| D7 | Determinism contract | `SET TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE`; same snapshot → identical canonicalized findings → identical `input_substrate_snapshot_hash` |
| D8 | Physical isolation | New DB role `chain_auditor_readonly` (SELECT-only); BEFORE INSERT trigger on `chain_audit_evidence` rejects any other `current_user` |

## V1 scope (sharpened 2026-06-16)

**Mode:** `pre_m13_audit` only. Other 4 modes deferred to subsequent versions.

**Target:** MCF draft MCV (one MCV uid per audit run).

**Rationale:**
- Hits real recent pain (PE-MC-12, BCV pointers, canonical filters)
- Runs before irreversible M14 certification / activation
- Read-only safe
- Exposes drift + chain gaps without having to solve runtime binding yet
- Auditor defines correctness → CEE v0 (separate ADR) will be built to satisfy what this audit specifies for `pre_m13_audit`

## Surface

```
POST /api/mcf/chain-audit/runs
  body: { mode: 'pre_m13_audit', target: { kind: 'mcv', uid } }
  auth: @PlatformOnly() @Roles('mcf_author' | 'mcf_publisher')
  response: { audit_evidence_uid, mode, verdict_code, findings_count, substrate_snapshot_hash }

GET /api/mcf/chain-audit/evidence/:auditEvidenceUid
  auth: same

GET /api/mcf/chain-audit/latest?target_kind=mcv&target_uid=...&mode=pre_m13_audit
  auth: same
```

## Substrate

New table:

```sql
CREATE TABLE mcf.chain_audit_evidence (
  audit_evidence_uid              uuid PRIMARY KEY,
  audit_mode_code                 text NOT NULL CHECK (audit_mode_code IN
    ('pre_m12_audit','pre_m13_audit','pre_m14_audit',
     'pre_runtime_release_audit','regression_audit')),
  target_kind_code                text NOT NULL CHECK (target_kind_code IN ('mc','mcv','tenant_binding')),
  target_uid                      uuid NOT NULL,
  verdict_code                    text NOT NULL CHECK (verdict_code IN ('PASS','FAIL','OPERATOR_REVIEW','NOT_APPLICABLE')),
  findings_json                   jsonb NOT NULL DEFAULT '[]',
  input_substrate_snapshot_hash   text NOT NULL CHECK (input_substrate_snapshot_hash ~ '^sha256:[0-9a-f]{64}$'),
  audit_engine_version            text NOT NULL DEFAULT 'cas-v1',
  computed_at                     timestamptz NOT NULL DEFAULT now(),
  computed_by_role                text NOT NULL CHECK (computed_by_role = 'chain_auditor_readonly')
);
CREATE INDEX idx_cae_target_mode ON mcf.chain_audit_evidence(target_kind_code, target_uid, audit_mode_code, computed_at DESC);
CREATE INDEX idx_cae_verdict_failing ON mcf.chain_audit_evidence(computed_at DESC) WHERE verdict_code IN ('FAIL','OPERATOR_REVIEW');

CREATE OR REPLACE FUNCTION fn_cae_insert_role_check() RETURNS trigger AS $$
BEGIN
  IF current_user <> 'chain_auditor_readonly' THEN
    RAISE EXCEPTION 'chain_audit_evidence may only be written by chain_auditor_readonly role (got %)', current_user;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_cae_role_check BEFORE INSERT ON mcf.chain_audit_evidence
  FOR EACH ROW EXECUTE FUNCTION fn_cae_insert_role_check();
```

New DB role:

```sql
CREATE ROLE chain_auditor_readonly NOINHERIT NOLOGIN;
GRANT USAGE ON SCHEMA mcf, contract, bcf TO chain_auditor_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA mcf, contract, bcf TO chain_auditor_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA mcf, contract, bcf
  GRANT SELECT ON TABLES TO chain_auditor_readonly;
GRANT INSERT ON mcf.chain_audit_evidence TO chain_auditor_readonly;
```

## Checks (11 operator-mandated, mapped to Pattern A or B)

V1 implementation covers a subset gated by `pre_m13_audit` mode (checks 1-5, 11). Other checks deferred with their modes.

| # | Check | Pattern | V1? |
|---|---|---|---|
| C1 | BC active, version-bound, semantically correct | A + B | ✓ |
| C2 | CC field selection covered by active OC union | A + B | ✓ |
| C3 | OC source mappings valid + role-disambiguated | A | ✓ |
| C4 | No source-specific codes in MC filters (D441) | A | ✓ |
| C5 | Canonical values in CURRENT canonical_value_set | B | ✓ |
| C11 | No silent ambiguity: two OCs emit same canonical field without resolver | A | ✓ |
| C6 | MVB/MFC point to BCV not BC heads | A + B | deferred (pre_m14) |
| C7 | PE-MC gates replayable from persisted evidence | A + B | deferred (pre_m14) |
| C8 | M13/M14 certs match current substrate hashes (drift detection) | B | deferred (pre_m14) |
| C9 | Runtime binding matches approved MC/MCV + tenant scope | A + B | deferred (pre_runtime_release) |
| C10 | No hidden dep on archived/superseded object | B | deferred (pre_m14) |

## Verdict rules

Aggregated from per-check `verdict_code` values via the rule:

- **FAIL** — any check returned `FAIL`
- **OPERATOR_REVIEW** — no `FAIL`, but at least one check returned `OPERATOR_REVIEW`
- **NOT_APPLICABLE** — every check returned `NOT_APPLICABLE` (e.g., all v0 checks deferred for this target)
- **PASS** — at least one check returned `PASS` and none returned `FAIL` or `OPERATOR_REVIEW`

Per-check `verdict_code` semantics:

- **PASS** — the check ran and observed no violation of its rule
- **FAIL** — the check ran and observed a definite violation; lifecycle gate refuses
- **OPERATOR_REVIEW** — the check ran but cannot decide deterministically; requires human disposition before the gate advances
- **NOT_APPLICABLE** — the check did not apply to this target (e.g., deferred to a later CAS version, or the target shape excludes the check); not a violation

Caller behavior (downstream gating):

- M13 evaluator: refuses if `pre_m13_audit` aggregate verdict for target MCV is `FAIL` or `OPERATOR_REVIEW`
- M14 activator: refuses if `pre_m14_audit` aggregate verdict is `FAIL` or `OPERATOR_REVIEW` (deferred mode)
- Tenant binding flow: refuses if `pre_runtime_release_audit` aggregate verdict is `FAIL` or `OPERATOR_REVIEW` (deferred mode)
- Regression: produces operational incident on `FAIL`; does NOT auto-unbind (deferred mode)

> **Amendment (TSK-180e3a, 2026-06-16)** — The verdict vocabulary above supersedes the original draft of this ADR, which used `green`/`yellow`/`red`. The PASS/FAIL/OPERATOR_REVIEW/NOT_APPLICABLE model was authorized at SES-18e856 and shipped in the foundation PR ([bc-core#296](https://github.com/selenite-git-admin/bc-core/pull/296)) and the service-wiring PR ([bc-core#297](https://github.com/selenite-git-admin/bc-core/pull/297)). The DDL and per-check codes in this ADR have been reconciled to the shipped model.

## Finding taxonomy V1

`AUDIT_FINDING_REGISTRY_V1` codes for `pre_m13_audit` scope.

**C1 — BC active + BCV-bound + semantically correct** (shipped FULL in v0):
- `AUDIT_C1_BC_ARCHIVED`
- `AUDIT_C1_BC_NOT_ACTIVE`
- `AUDIT_C1_BCV_POINTER_NULL`
- `AUDIT_C1_BCV_NOT_ON_CURRENT_HEAD`
- `AUDIT_C1_BC_HEAD_MISSING`

**C2 — CC field selection covered by active OC union** (deferred to CAS v1):
- `AUDIT_C2_DEFERRED_TO_V1`

**C3 — OC source mappings valid + role-disambiguated** (deferred to CAS v1):
- `AUDIT_C3_DEFERRED_TO_V1`

**C4 — D441 source-literal guard against MC filter literals** (shipped FULL in v0):
- `AUDIT_C4_BLART_VALUE_AS_LITERAL`
- `AUDIT_C4_SOURCE_SYSTEM_TOKEN_IN_LITERAL`
- `AUDIT_C4_SOURCE_SYSTEM_TOKEN_IN_EXPRESSION`

**C5 — canonical value in CURRENT `canonical_value_set` (Pattern B drift)** (shipped FULL in v0):
- `AUDIT_C5_LITERAL_NOT_IN_CURRENT_CANONICAL_VALUE_SET`
- `AUDIT_C5_NO_CANONICAL_VALUE_SET_DEFINED`

**C11 — OC resolver ambiguity** (deferred to CAS v1):
- `AUDIT_C11_DEFERRED_TO_V1`

The deferred-check codes (`AUDIT_C2_DEFERRED_TO_V1`, `AUDIT_C3_DEFERRED_TO_V1`, `AUDIT_C11_DEFERRED_TO_V1`) are emitted alongside a per-check `verdict_code = 'NOT_APPLICABLE'` and `not_applicable_reason = 'deferred_to_v1'`. They preserve the contract envelope shape so callers receive a consistent six-check result set regardless of v0/v1 differences.

Codes for deferred lifecycle modes (`pre_m12_audit`, `pre_m14_audit`, `pre_runtime_release_audit`, `regression_audit`) added with those modes.

## Out of scope

- Authoring or repair (CEE's job — separate ADR)
- Auto-remediation of findings
- Real-time runtime evaluation
- Per-tenant fact verification
- Cross-tenant audit
- Audit-of-the-audit (recursive verification)
- v1 implements `pre_m13_audit` only; other 4 modes are deferred

## Foundation gate

**Repair location:** **B** (contract semantics / governance grammar). Introduces a new governance artifact family — chain audit evidence with fixed finding taxonomy and mode contracts.

**Why not D:** no evaluation in the contract sense. CAS re-derives hashes and compares, but does not produce contract outputs.

**Why not F:** F is read-model/diagnostics. The new evidence table participates in lifecycle gating (M13 refuses on `FAIL` / `OPERATOR_REVIEW`), so it's contract-level governance, not diagnostic surface.

**Three pre-action answers:**
1. **Why here?** Independent verification governance is missing. Substrate drift detection requires a new evidence shape that is *governance* (gates M13/M14), not *diagnostic* (informational).
2. **Why not upper layers?** No grammar change in contract artifacts themselves; the addition is a new governance artifact, not a change to existing ones.
3. **Why not lower layers?** No evaluation engine change. The audit is a read-derive-compare loop over existing artifacts, not new evaluation logic.

## Risks

1. **Audit cost** — Pattern B re-derivation expensive on large substrates. Mitigation: cache substrate snapshot hash; if hash unchanged since last audit, return cached evidence.
2. **False positives on drift** — C8 (deferred to pre_m14) could fire on legitimate substrate evolution. Mitigation: distinguish "drift since cert" (`FAIL`) from "drift since last audit" (`OPERATOR_REVIEW`).
3. **Role isolation bypass** — operator could grant `chain_enrichment_writer` temporary SELECT on audit evidence. Mitigation: trigger-level INSERT guard; periodic role-grant audit.
4. **Mode chaining cost** — `pre_runtime_release` runs all 11 checks; slow. Mitigation: per-check caching keyed on substrate snapshot hash.

## References

- Chain Engines Design Packet (SES-9b9b71, SES-74258f): `bc-docs-v3/docs/implementation/chain-engines-design-packet-2026-06-15.md`
- Sibling ADR: ADR-A Chain Enrichment Engine (proposed, to be filed after CAS v0 ships)
- D305 ChainStatusService SSOT (ADR-bebaec)
- D366 L-node semantic verdict (ADR-804874)
- TSK-1ee570 B1 BCV pointer columns (substrate enabling C6)
- D441 source-literal guard (ADR-46ff0a / ADR-61850f / ADR-6b35e0) — substrate enabling C4
- D444 Phase 1 panel composition v3 (ADR-5cb154)
- Foundation invariants `bc-docs-v3/docs/foundation/the-invariants.md`
- Evaluation boundaries `bc-docs-v3/docs/foundation/the-evaluation-boundaries.md`</decision_text>
<parameter name="status">decided</parameter>
<parameter name="domain_code">governance
