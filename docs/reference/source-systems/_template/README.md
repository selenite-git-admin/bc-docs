---
uid: SRC-TEMPLATE-readme
slug: source-systems-docket-readme
title: "Source-System Docket — Convention"
description: "How to author a per-source-system docket folder. Governed by DEC-8570d4 (D526)."
type: source-systems-docket
status: published
domain: documentation
subdomain: source-systems
focus: governance
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure
  - DEC-6cb4f3   # D385 — Source Systems framework
---

# Source-System Docket — Convention

Per **DEC-8570d4 (D526)**, every source system is a **folder** `docs/reference/source-systems/<slug>/`
that co-locates all onboarding reference material for that system. This replaces the flat
one-markdown-per-system layout of D385 (the reference narrative moves into the folder's `index.md`).

## Folder shape

```
source-systems/<slug>/
  index.md          # registered docket cover/manifest + reference narrative (SRC-* uid lives here)
  contracts.md      # SC/AC/OC/CC authored against this system
  catalog.md        # seed-catalog + source-registration footprint
  onboarding-log.md # dated per-onboarding execution log
  evidence.md       # proof entries → basis for proof_status
```

## Authoring a new system

1. Copy `_template/` to `source-systems/<slug>/`.
2. Fill `index.md` frontmatter: allocate a real `SRC-*` uid (do not reuse the template's), set `slug`,
   `proof_status` (honestly — start `designed`), `system_type_code`, `reader_flavors[]`, `governing_adrs[]`.
3. Write the reference narrative in `index.md` (proof status, reader binding, admits, legal, technical,
   semantics/pitfalls, gaps). Use `sap-ecc/` as the migrated exemplar.
4. As contracts/catalog/evidence accrue, fill the sibling files AND the `index.md` linking hooks
   (`admission_contract_versions[]`, `catalog_ref`, `evidence_records[]`).
5. Register in the parent [index.md](../index.md) category table (link to `<slug>/`, not `<slug>.md`).
6. Run `devhub_doc_scan` then `devhub_doc_validate`.

## Registry stability

The `SRC-*` uid is the stable *documentation* identity — the DevHub doc scanner keys on frontmatter, so moving
a page into a folder does not change its registry identity. Only markdown **relative links** and `supersedes:`
paths change (`<slug>.md` → `<slug>/`). When migrating an existing flat page, rewrite inbound links accordingly.

## Authority semantics (DEC-8570d4 Amendment 1 — normative)

> Source-System Dockets are **documentation projections**. They do not create source registration, contract
> identity, catalog authority, evidence, or audit decisions. All such objects are referenced by exact governed
> UID and digest from their owning substrate. Proof maturity is scope-bound and distinct from source-realization
> audit verdict. CI fails when a docket reference cannot be resolved or disagrees with its authority.

Rules every docket must obey:

1. **Registries own identities; the audit substrate owns evidence and decisions; the docket only projects.**
   Every file carries `authority_role: projection`.
2. **No hand-asserted authority.** Values copied from governed systems are generated or CI-reconciled. A docket
   may *link* an authority object; it must not *create* one by assertion.
3. **`proof_status` is evidence maturity, not a verdict.** Pair it with `proof_scope_refs[]`,
   `source_realization_refs[]`, `audit_decision_refs[]`. The referenced governed objects are authoritative.
   PASS/REJECT/OPERATOR_REVIEW live in the audit substrate and are only ever rendered as a labelled "derived
   projection" with the exact decision UID/digest.
4. **Proof is scoped to an exact source-realization package** (source release, reader/runtime version+digest,
   catalog/mapping roots, contract-set, MCV/closure scope, evidence-set digest). The bare `SRC-*` uid is *not*
   the audit-usable coordinate. First-hand proof is entity/scope-specific, never a whole-system promotion.
5. **`evidence.md` / `onboarding-log.md` outcome & proof fields are emitted or referenced** (governed evidence
   UID/digest; onboarding-session receipt) — never author-asserted. Narrative prose may be hand-authored.
6. **Customer identity stays out of Git** — pseudonymous instance UID + evidence digest + allowed scope +
   disclosure-safe summary only. Raw evidence and tenant identity live in the restricted audit/evidence store.
7. **Community-catalogue seed = provisional provenance**, not verified source truth, until exact release/DDIC
   (or vendor-equivalent) verification. "Standard field semantics are universal" is qualified by release,
   support-package, industry-extension, and customizing differences, which remain in scope per realization.

Full auditor review: `barecount-devhub/artifacts/metric-audit/RESPONSE-Codex-source-system-docket-d526-2026-07-13.md`.

## Four-quadrant §4–§5 (DEC-8570d4 Amendment 2)

`index.md` §4 Legal & Licensing and §5 Technical each split into two planes, recording **official, general research only**:

- **Platform Plane** — vendor-general. §4: API/licensing policy, permitted/prohibited access, read-vs-write, licence types, maintenance horizon, official refs + retrieval date + digest. §5: supported releases, protocols/auth, schema discovery, API limits/pagination/delta, network, source semantics.
- **Tenant Connection Plane** — what *any* customer must have/do, stated generically. §4: vendor entitlement, MSA/DPA/approvals that must exist, scope authorization, residency/retention/subprocessor, authorizer roles. §5: customer setup steps, service account + min permissions, allow-listing, modules to enable, connection-test/first-chain-proof, release/customization verification.

**Never** put tenant names, contracts, credentials, endpoints, approvals, or legal conclusions in the docket — those are governed-substrate objects linked by pseudonymous UID/digest.

## Amendment 3 (external-auditor sign-off) — evidence, coordinates, research

1. **`proof_status` needs governed evidence.** Project `shape_tested`/`first_hand_proven` only when a governed proof-scope/evidence object exists and `proof_scope_refs[]`/`source_realization_refs[]` are populated; otherwise `designed`, with any prior run kept as **ungoverned historical background**.
2. **Exact coordinates are frontmatter, not prose.** Populate `source_registry_ref`, `reader_flavor_versions[]`, `catalog_root`, `contract_set_ref`, `admission_contract_versions[]`, `official_research_refs[]`. Slug fields are labels; authority is the referenced object.
3. **Legal/technical = research, not clearance.** No blanket "sanctioned/banned/zero-cost/licence" conclusions; render candidate paths + conditions, each backed by a version-exact official source in `official_research_refs[]` (source + version + retrieved_at + digest) and, at runtime, the governed authority objects. Credentials only via governed secret-ingress (`credential_ref` + receipt) — never person-to-person, never raw in Git.

**Rollout capability gates:** (G1) governed evidence UIDs/receipts exist; (G2) CI fails on unresolved/stale/disagreeing docket references; (G3) official research is versioned + digest-bound before any legal/technical projection is presented as verified.
