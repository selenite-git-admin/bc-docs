# Review Package — Odoo Pilot: Source Framework + Integration Design

**For:** independent review (Codex auditor PoV). **Prepared:** 2026-07-31.
**Nature:** a design + a working repo, for review **before** the expensive build. This is a
package cover — the entry point and reading order for the document set below.

---

## 1. What this is, and the review posture

We are standing up **Odoo as BareCount's first pilot source system**, as the front of a
reusable **at-home source-world lab** on which function-scoped Readers and metrics can be
developed and validated *before* any client system lands. A 5-FY, 3-company Indian-
manufacturer world has already been **built and gate-passed** (the dry-run); this package
is the *design* that world proved out, plus the engine repo it now lives in.

**Codex's role (D519/D523):** governance confidence — is the design coherent, complete, and
free of the class of defect the dry-run surfaced? — **not** platform certification.
**Verdicts per section:** VERIFIED / QUALIFIED / CONTRADICTED / NOT_PROVEN, confidence 1–5
(the D526 docket-enrichment convention). Disposition ledger in §5.

## 2. Two hard boundaries the reviewer must hold

1. **Track-C hold (D524).** Authoring/activating any SC/AC/OC/CC/MC over Odoo is held until
   Track C. The **source-side** (framework + bc-pilot + console) is *outside* the hold and
   buildable now; the **contract chain** (deferred doc §5) is *design only*.
2. **Audit-independence (D524/D525).** The intrinsic metric audit stays on SAP ECC. This
   Odoo work is a separate source-realization lane; projecting one world into Odoo/BC/SFDC
   is execution-side, not audit-side.

## 3. The document set (reading order)

| # | Document | Covers | Status | Track-C |
|---|---|---|---|---|
| A | `FRAMEWORK-odoo-target-company-profiles.md` | **source backbone**: base install + multi-profile data; function-coverage horizon; gate battery; ops | **ACTIVE** (near-term build) | outside |
| B | **`bc-pilot` repo** @ `9f1cc8c` (github: selenite-git-admin/bc-pilot, private) | the world engine itself — profiles × systems; Profile #1 (mfg-in) built + gate-passed | **ACTIVE** (dry-run proven) | outside |
| C | `PLAN-odoo-pilot-v2-2026-07-30.md` | the chronological forward-loop build architecture (§1) | ACTIVE (profile builder) | outside |
| D | `DESIGN-bc-admin-profile-console.md` | **read model** (repair-loc F): bc-core registry + `@PlatformOnly` endpoint + bc-admin pages | ACTIVE (design; DBCP-gated) | outside |
| E | `PKG-odoo-pilot-implementation-design-2026-07-30.md` | **deferred E2E integration**: Reader (§4) + contract chain (§5) + projection. §3/§3.5 SUPERSEDED by A. | DEFERRED | §5 gated |
| — | `RUNBOOK-world-engine-odoo-mfg-in.md` | ops runbook for Profile #1 (supporting reference) | reference | outside |

Read **A → B → C → D** for the near-term, buildable source lab; read **E (§4, §5)** for the
integration design that consumes it at Track C.

## 4. What we specifically want reviewed (per doc)

- **A (framework):** Is the *source-as-backbone / function-coverage* horizon sound — build a
  max-function-module coherent Odoo at home to break the reader/metric catch-22? Is
  *"books history backdated, behavioral (CRM-velocity) history forward-only from go-live"*
  an acceptable, honestly-stated data contract? Is the multi-profile model (one archetype
  covers most functions; second archetype for the rest) right?
- **B (bc-pilot):** Is the **profiles × systems** seam correct (profile = source-agnostic
  definition; system = per-vendor projector)? Any defect in the gate battery as an
  acceptance test?
- **D (console):** Registry-as-projection of the bc-pilot artifact (D526 discipline);
  importer push-model; the DBCP as gating prerequisite — sound?
- **E §4 (reader):** the ORM **domain serializer is net-new** (confirmed gap) — design OK?
  Do we want a hard **"no company ⇒ reject"** enforcement point (new work) or rely on the
  fiscal-calendar gate? (See the doctrine correction below.)
- **E §5 (chain):** the **portability mechanism** (MC binds concepts not columns → same MC
  onboards BC with no edits) — confirmed in code; sound? Sequencing around the
  **`classify_by_binding`/`fiscal_period_end_date` runtime gap** (GL-classification metrics
  wait; AR/AP totals clear) — agree?
- **Cross-cutting:** does projecting one correlated world into Odoo+BC+SFDC threaten
  audit-independence (D524)? (Our position: no — execution-side.)

**Doctrine correction already folded in (flagging so the reviewer sees we caught it):** the
claim "canonical resolution fails closed without a company_id" is **false** — `pickLegalEntity`
falls back to `'*'`; fail-closed is transitive via the fiscal-calendar gate. Corrected across
E §4.7, bc-pilot, and the runbook. `company_id`-on-every-document is still correct; only the
justification was wrong.

## 5. Review protocol & disposition ledger

- This package + docs A/C/D/E graduate to a **bc-docs review branch, SHA-pinned**; the SHA
  is what goes to Codex (D526 exchange pattern). bc-pilot (B) is reviewed at commit
  **`9f1cc8c`**. Review branch: `review/odoo-pilot-source-framework-2026-07-31`, path
  `docs/evidence/reviews/odoo-pilot-source-framework-2026-07-31/`.
- Codex returns findings classified (§1); each is tracked below → response → resolution,
  both repos.
- Build authorization is staged: source-side (A/B/C/D) may proceed on operator sign-off
  after findings clear; the reader (E §4) after its findings clear; the chain (E §5) only at
  Track C.

| Finding | Doc/§ | Codex verdict (conf) | Response | Status |
|---|---|---|---|---|
| _(populated on review)_ | | | | |

## 6. Evidence base
Dry-run world (5 FY · 3 entities · all gates green: integrity, benchmarks, CoA 97%/company,
regression) → AMI `ami-0de1ac3735186651f`. Engine + gates + 15-anomaly answer key in
`bc-pilot`. Business dates verified backdated+spread (finance metrics meaningful);
wall-clock/CRM-velocity living-window-only. Reader/chain sections are bc-core-cited (two
read-only research passes).
