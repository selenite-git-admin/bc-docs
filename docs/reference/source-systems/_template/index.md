---
uid: SRC-TEMPLATE
slug: _template
title: "<System Name>"
description: "<One-line admission posture: what BareCount admits, via which researched access path, under which policy — no clearance conclusions here.>"
type: source-systems
status: draft
domain: <enterprise-erp | accounting | payments | crm | hcm | itsm | project-management | procurement | manufacturing | advertising | reference-data>
subdomain: <vendor-or-family, e.g. sap, oracle, microsoft>
focus: governance
authority_role: projection      # D526 Amendment 1 — the docket is a PROJECTION, never an authority
# --- evidence maturity (D385): what evidence exists, at what scope. NOT an audit verdict. ---
proof_status: designed          # designed | shape_tested | first_hand_proven
proof_scope_refs: []            # governed source-proof-scope UIDs (audit substrate) — authoritative
source_realization_refs: []     # governed source-realization-package UIDs (exact release+reader+catalog+contract+MCV+evidence digest)
audit_decision_refs: []         # signed audit-decision UIDs (audit substrate) — PASS/REJECT/OPERATOR_REVIEW live THERE, never restated here
# --- exact governed reference coordinates (Codex P1-4) — authority is the REFERENCED object, not these strings ---
source_registry_ref: null       # source-system registry UID + exact provider/system/release
reader_flavor_versions: []      # exact reader-flavor version UID + digest (the slugs in reader_flavors[] below are labels only)
catalog_root: null              # source-catalog snapshot / mapping-root digest (not a doc link)
contract_set_ref: null          # SC/AC/OC/CC version-set UID or contract-set digest
admission_contract_versions: [] # AC version UIDs realized against this system — see contracts.md
official_research_refs: []      # structured official citations: [{source, version, retrieved_at, digest}] — 3rd capability gate (versioned + digest-bound before projected as verified)
last_verified_at: <YYYY-MM-DD>
official_docs_url: <vendor docs URL>
system_type_code: <runtime system_type_code, e.g. sap_ecc>   # label; authority = source_registry_ref
reader_flavors: []              # reader-flavor slugs (labels; authority = reader_flavor_versions[])
catalog_ref: null               # human link to catalog.md; authority = catalog_root + source catalog (source.*)
docket_files:
  - contracts.md
  - catalog.md
  - onboarding-log.md
  - evidence.md
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1, authority semantics)
supersedes: <legacy path, or remove>
---

# <System Name>

> **Docket cover — this is a PROJECTION, not an authority (DEC-8570d4 Amendment 1).**
> This `index.md` indexes and links governed objects; it does not create source registration, contract
> identity, catalog authority, evidence, or audit decisions. Registries own identities; the audit substrate
> owns evidence and PASS/REJECT/OPERATOR_REVIEW decisions. Every substantive value here resolves to a
> governed UID/digest in its owning substrate. `proof_status` is **evidence maturity, not an audit verdict**.
> The reference narrative lives here; concrete artifacts are referenced via the sibling files under
> [Docket Contents](#docket-contents).

<Opening: what the system is, its access posture, governing policy/ADR, maintenance horizon.>

---

## Docket Contents

| File | Holds |
|---|---|
| **index.md** (this file) | Proof status, reader-flavor binding, reference (admits / legal / technical / semantics / gaps), references, changelog |
| [contracts.md](contracts.md) | Source/Admission/Observation/Canonical Contracts authored against this system + Contract Registry links |
| [catalog.md](catalog.md) | Seed-catalog + source-registration entries (provider/system/version/module/table/field) |
| [onboarding-log.md](onboarding-log.md) | Dated per-onboarding runbook-execution log (customer-side + BareCount-side) |
| [evidence.md](evidence.md) | Proof entries — simulator runs, first-hand verifications, metric snapshots realized |

---

## 1. Proof Status (evidence maturity) & Audit Decisions

Two orthogonal vocabularies — never infer one from the other (D526 Amendment 1):

**Evidence maturity** — **`<proof_status>`** as of <YYYY-MM-DD>. Answers *what evidence exists, at what scope*.
Scope is bound by `proof_scope_refs[]` / `source_realization_refs[]` (governed) — not by this label. First-hand
proof is **entity/scope-specific**, never a whole-system promotion. Zero-claims rule (D385): no external claim
runs ahead of first-hand proof. Detail + governed evidence UIDs in [evidence.md](evidence.md).

**Audit decision** — *derived projection only.* PASS/REJECT/OPERATOR_REVIEW are decided and stored in the audit
substrate (per D525), keyed to an exact source-realization package. This docket **links** the decision UID/digest
(`audit_decision_refs[]`); it never restates a verdict as its own authority. `shape_tested`/`first_hand_proven`
do **not** imply PASS.

---

## 2. Reader Flavor Binding

| Flavor | Target | Executor | AC version |
|---|---|---|---|
| `<flavor-slug>` | <target> | `<Executor>` | <ac version or —> |

---

## 3. What BareCount Admits

### 3.1 Metadata
<Field/table/entity metadata admitted; catalog tier. See catalog.md for the concrete entries.>

### 3.2 Business data
<Posted business records / entities admitted, via which path.>

---

> **Scope of §4–§5 (D526 Amendment 1).** These sections record **official, general** research only — vendor
> policy and the requirements *any* customer must satisfy. They must **not** contain tenant names, contracts,
> credentials, endpoints, approvals, or legal conclusions. Actual tenant authorization and execution evidence
> live in the restricted governed substrate and are linked by pseudonymous UID/digest (see onboarding-log.md /
> evidence.md). Each cited official source carries its applicability, retrieval date, and a digest.

## 4. Legal & Licensing

### 4.A Platform Plane — vendor legal & licensing (general)
<Vendor API/licensing policy; permitted vs prohibited access methods; read- vs write-back implications;
user/license-type requirements; maintenance/support horizon. Cite official references with applicability +
retrieval date + digest.>

### 4.B Tenant Connection Plane — customer authorization prerequisites (general, not tenant-specific)
<What any customer must have/do, stated generically: required vendor entitlement/licence; MSA/DPA/Order-Form/
security approvals that must exist; authorization for the selected module/data scope; residency, retention and
subprocessor considerations; the customer-side authorizer roles required. No named tenant, no actual approval —
those are governed-substrate objects referenced by UID/digest.>

---

## 5. Technical

### 5.A Platform Plane — vendor technical (general)
<Supported releases/components; protocols and authentication methods; metadata/schema discovery; API limits,
pagination and delta behavior; network requirements; known source semantics and restrictions.>

### 5.B Tenant Connection Plane — customer technical prerequisites (general)
<Customer-side setup steps; service account and minimum permissions; endpoint/network allow-listing; modules/
entities that must be enabled; connection-test and first-chain proof requirements; release/customization
verification requirements. Stated as general requirements — concrete endpoints/accounts live only in the
governed substrate.>

---

## 6. Source-System Semantics
<Pitfalls and vendor-specific characteristics the resolver must handle: sign conventions, currency/rounding,
open-item vs current-state, timezones, coded-value sets. Primary-source-verified pitfall record.
**Optional/omit** when a system's semantics are already captured as a contract pattern in
[contracts.md](contracts.md) (e.g. a sign-indicator OC pattern) — in that case cross-reference it here or
under §5.A "known source semantics" rather than duplicating. Section numbering shifts if a Commercial or other
section precedes it.>

---

## 7. Known Gaps
<Numbered list of what is not yet built/proven for this system.>

---

## 8. References
| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../../governance/adrs/ADR-6cb4f3.md) |
| ADR — Source-System Docket structure (D526) | [ADR-8570d4](../../../governance/adrs/ADR-8570d4.md) |
| <vendor docs> | <url> |

## 9. Changelog
- **<YYYY-MM-DD>** — <change>.
