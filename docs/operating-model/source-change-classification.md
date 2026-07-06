---
id: source-change-classification
order: 9.5
title: "Source Change Classification and Version-Bump Policy"
status: drafting
authority: authoritative
depends_on: [sources-and-the-catalog, the-contract-grammar, contract-chain-assembly, admission-and-observation, chain-completeness-and-verdict]
governing_sources:
  - Sources and the Catalog
  - The Contract Grammar
  - Contract Chain Assembly
  - Admission and Observation
governing_adrs:
  - DEC-bebaec (Chain Completeness SSOT)
  - DEC-c9e623 (MLS Framework — defines lifecycle states a source change cascades through)
  - DEC-e7b7b3 (MLS State Substrate — the read model where a detected change surfaces)
errata_referenced: []
v2_sources:
  - system/sops/cc-creation-sop.md (cc-creation-sop §"CC Versioning policy" — change classification table)
  - decisions/ADR-0002.md (Version model — Major / Minor / Update)
  - decisions/ADR-0003.md (Major = breaking change; explicit approval and downstream re-alignment)
  - decisions/ADR-09b8e6.md (New fields enter as `registered`, trigger minor version bump)
  - decisions/ADR-05140c.md (Approved object → contract auto-creation; new fields trigger MINOR bump)
diagrams: []
---

# Source Change Classification and Version-Bump Policy

## Scope

This chapter records how the platform classifies changes to source-side artifacts (source fields, source tables, source-system schemas) and which contract version bump each kind of change requires. The classification is the policy bridge between two surfaces:

- **Authoring side** — when an operator updates the source catalog or a contract body, the version-bump policy says whether the change is `additive` (minor bump), `destructive` (major bump), or `semantic` (review queue, not auto-classifiable)
- **Runtime side** — when a reader execution observes a payload that differs from what the active contract declared, the same classification governs how the runtime responds (admit-with-flag, quarantine, or human-review). Runtime cascade is governed by a separate ADR (forward reference: Runtime Drift Detection)

This chapter does not redefine the contract grammar (The Contract Grammar), the catalog (Sources and the Catalog), the admission boundary (Admission and Observation), or the chain status SSOT (Chain Completeness and Verdict). It locks one cross-cutting policy that those chapters reference.

**Governing source.** v2 cc-creation-sop (CC Versioning policy table); ADR-0002, ADR-0003, ADR-09b8e6, ADR-05140c.

## The Three Change Kinds

Source-side changes are classified into three kinds. Each kind has a deterministic cascade (additive, destructive) or requires human review (semantic).

| Kind | Definition | Detection | Version bump | Cascade |
|---|---|---|---|---|
| **additive** | A new field, table, or attribute appears that the active contract does not declare. The existing contract remains structurally valid. | Catalog scan diff (authoring) or runtime payload diff (drift detection) | **Minor** version bump on the contract. New artifact enters as `registered`, goes through approval, and is incorporated in the next minor version | Non-disruptive. Existing chains continue to operate against the prior version. New version supersedes once activated; transition window per DEC-bebaec |
| **destructive** | A field, table, or attribute that the active contract declares is removed, renamed, or has its type narrowed incompatibly. The existing contract is structurally invalid against the new source shape | Same — catalog scan or runtime payload diff (a missing required field surfaces as admission rejection) | **Major** version bump on the contract. Requires explicit approval and downstream re-alignment | Disruptive. Records that fail validation against the prior contract are rejected (per the contract's `validation_policy`). Operator authors a new major version; cascade fanout per DEC-95687d (Nightly Reconciler) propagates the new version to bound tenants |
| **semantic** | A field's name, type, and structural properties are unchanged, but its meaning has shifted (e.g., an amount field that previously excluded tax later includes it). The contract structurally accepts the new payload but the values are no longer comparable to historical values | **Cannot be auto-detected.** Requires human or AI-assisted review | Review queue; case-by-case decision (typically major bump if the semantic shift breaks downstream metric definitions) | No automatic action. Operator decides per metric whether to mark the prior contract version superseded. Historical snapshots produced under the prior contract remain truthful under their computation record |

The **additive** and **destructive** kinds are mechanical — the platform can classify them deterministically from a structural diff. The **semantic** kind is irreducibly a human-or-AI judgment call; the platform surfaces the candidates but does not auto-classify.

## Per-Artifact Change Type → Bump Mapping

The following table promotes the v2 cc-creation-sop classification (originally for CC body changes) and generalizes it across artifact types. Each row is a specific change action against a specific artifact; the bump column is the policy.

### Source artifact changes

| Change | Bump | Kind | Notes |
|---|---|---|---|
| Add field to source catalog (`source.source_field`) | Minor SC | additive | New field enters as `registered`; promotes to active SC version through standard approval |
| Remove field from source catalog | Major SC | destructive | Affected OCs, ACs, and downstream MCs require new versions if they reference the removed field |
| Rename field in source catalog | Major SC | destructive | Treated as remove + add for contract purposes; old field references break |
| Add table to source catalog (`source.source_table`) | Minor SC (or new SC) | additive | New table can be referenced by new ACs/OCs without disturbing existing chains |
| Remove table from source catalog | Major SC | destructive | All ACs/OCs bound to this table require re-author or supersede |
| Change field type compatibly (e.g., `varchar(50)` → `varchar(100)`) | Minor SC | additive | Wider type accepts existing values; non-breaking |
| Change field type incompatibly (e.g., `numeric(15,2)` → `numeric(20,4)` or `string` → `int`) | Major SC | destructive | Existing parsers may misinterpret; explicit approval required |

### Admission Contract (AC) changes

| Change | Bump | Kind | Notes |
|---|---|---|---|
| Add admissibility rule | Minor AC | additive | Stricter validation accepts a subset of prior payloads; no records previously admitted retroactively become rejected |
| Remove admissibility rule | Minor AC | additive | Looser validation accepts more payloads; no breaking effect |
| Change `validation_policy` (`block` → `quarantine`, etc.) | Major AC | destructive | Materially changes runtime behavior; explicit approval required |
| Add field to `body.fields[]` | Minor AC | additive | New field admitted alongside existing |
| Remove field from `body.fields[]` | Major AC | destructive | Existing payloads with the field still admit; downstream OC/CC may fail to map |
| Change `identity_semantics.primary_key` | Major AC | destructive | Identity contract changes; record uniqueness rules differ |

### Observation Contract (OC) changes

| Change | Bump | Kind | Notes |
|---|---|---|---|
| Add `field_mapping` entry (BF → source field) | Minor OC | additive | New BF available; existing chains unchanged |
| Remove `field_mapping` entry | Major OC | destructive | Downstream CC may fail at L4 (chain completeness) |
| Change `field_mapping.resolution_rule` (e.g., `latest` → `aggregate`) | Minor OC | additive (semantic-adjacent) | Same shape, different values; CC consumers unaware. Note: this can shade into semantic if the operational difference is large; review before bumping |
| Change `identity_semantics` | Major OC | destructive | OC identity contract changes |

### Canonical Contract (CC) changes (per v2 cc-creation-sop)

| Change | Bump | Kind | Notes |
|---|---|---|---|
| Add field to `field_selection` | Minor CC | additive | New field available to MCs; existing MCs unchanged |
| Remove field from `field_selection` | Major CC | destructive | Downstream MC may reference it |
| Change grain | Major CC | destructive | CO identity changes; downstream snapshots invalidated |
| Change `resolution_rule` for a field | Minor CC | additive (semantic-adjacent) | Same CO shape, different values; review for semantic-shift impact on MCs |
| Add `semantic_rule` | Minor CC | additive | Stricter validation; no shape change |
| Change `temporal_gate` schedule | Minor CC | additive | Timing only; no shape change |

### Metric Contract (MC) changes

| Change | Bump | Kind | Notes |
|---|---|---|---|
| Add input variable | Major MC | destructive | Formula changes; downstream snapshots not comparable |
| Remove input variable | Major MC | destructive | Same |
| Change formula | Major MC | destructive | Output values change semantically |
| Add threshold band | Minor MC | additive | Categorization only; raw value unchanged |
| Change `temporal_gate` parameters | Minor MC | additive | Cadence change; no shape change |
| Change `temporality_kind` | Major MC | destructive | Class semantics change; downstream interpretation differs (per DEC-952faa / D386) |

The classification is non-exhaustive. Edge cases default to **major** (treat as destructive) when uncertain — major bumps are governance acts that surface for review; minor bumps cascade automatically. Conservative defaulting protects downstream consumers.

## Cascade Rules — Additive

When a change is classified additive:

1. The artifact (new field, new table, new mapping) enters the catalog or contract body as `registered`
2. Standard approval flow runs (per Decision and Change Procedure)
3. A new minor version of the affected contract is authored with the additive change incorporated
4. Activation triggers `ContractActivationService` fanout (per DEC-95687d / D369): tenants bound to the prior version receive bindings to the new version; fact tables reconcile
5. Prior version enters 48h transition window (per DEC-bebaec); both versions active
6. After transition window, prior version auto-supersedes
7. No data quarantine; no operator intervention beyond standard approval

The cascade is event-driven, idempotent, and recoverable.

## Cascade Rules — Destructive

When a change is classified destructive:

1. The catalog or contract body change is rejected at structural validation against the active version (records would no longer admit)
2. A new **major** version of the affected contract is authored. The new version omits or replaces the destructive element
3. The new major version enters the standard `draft → review → approved → active` flow with **explicit approval required** (governance act, not silent fanout)
4. During the authoring window, runtime continues against the prior version; records that fail per the prior contract enter the contract's `validation_policy` path (typically `block` or `quarantine`)
5. Activation of the new major version triggers `ContractActivationService` fanout. Tenant bindings can either:
   - **Migrate** to the new version automatically (if the binding is configured for auto-major-migration; rare)
   - **Suspend** at the prior version with `binding_state='suspended'`, requiring explicit operator action to rebind to the new major (default for major bumps)
6. Historical snapshots produced under the prior version remain truthful under their computation record. The platform does not retroactively recompute against new major versions

Suspension preserves audit history; the operator's rebind action is recorded as a change record.

## Cascade Rules — Semantic

When a change is suspected semantic (or human-flagged as such):

1. The catalog and contract bodies are unchanged structurally — by definition, semantic changes do not show up as structural diffs
2. A review item is filed (mechanism out of scope of this chapter; future ADR will lock the queue)
3. Operator (or AI-assisted reviewer) determines whether the semantic shift breaks downstream metrics
4. If it breaks: typically promote to a major version bump (the structurally-equivalent contract gets a new major number to record the semantic break; downstream consumers re-evaluate)
5. If it does not break: no contract change; the semantic shift is recorded as an annotation on the contract version
6. Historical snapshots produced under the prior contract version remain truthful. New snapshots produced after the semantic shift carry an annotation if the shift is material

The semantic kind is the most operator-intensive; the platform's role is to make the candidates discoverable, not to auto-classify.

## Cross-Reference: Runtime Drift Detection

This chapter classifies changes as a **policy**. Runtime detection (when a reader execution observes a payload that differs from the active contract) implements the policy at the admission boundary. The runtime cascade — how `validation_policy` dispatches per-classified-delta, how tickets are lodged, how the S3 quarantine route works — is governed by a separate ADR (Runtime Drift Detection, sibling to this chapter).

In summary:

| Detected at runtime | Active contract result | Policy reference |
|---|---|---|
| New field in payload, not in OC | Admission accepts (additive); flag + ticket lodged for catalog onboarding | Additive cascade; this chapter |
| Required field absent from payload | Admission rejects (destructive); records routed per `validation_policy` (quarantine/block); ticket lodged for major bump | Destructive cascade; this chapter |
| Field type incompatible with declared type | Admission rejects (destructive); same route | Destructive cascade |
| Field semantics shifted (no structural diff) | Admission accepts; no automatic detection; review-queue mechanism | Semantic kind; out of automatic detection |

## Constraints

| Constraint | Form |
|---|---|
| Conservative defaulting | When a change cannot be cleanly classified additive or destructive, default to major (destructive). Minor bumps are silent fanouts; major bumps are governance acts. Conservative defaulting protects downstream consumers |
| Historical truth | Historical snapshots produced under a prior contract version remain truthful under their computation record. The platform does not retroactively recompute against new major versions |
| Suspension over deletion | Tenant bindings to a superseded prior version are suspended (`binding_state='suspended'`), not deleted. Audit history is preserved |
| Operator authority on majors | Major bumps require explicit operator approval (governance act). The platform may *propose* a major version (e.g., on detected destructive drift), but cannot auto-author one |
| Semantic is human-judged | The semantic kind cannot be auto-classified. The platform surfaces candidates; humans (or AI-assisted reviewers) decide |

## Failure Modes

| Failure | Behavior |
|---|---|
| Catalog scan misses an additive change (silent drift) | Records continue to admit; new field sits in `observed_payload_json` unmapped. Detection happens on next catalog scan or operator review. No production data lost |
| Catalog scan misses a destructive change (silent drift) | Records start failing admission via existing `validation_policy`. Rejection rate spike is the operational signal. Detection is reactive, not proactive |
| Operator approves a destructive bump without rebinding tenants | Tenants stay on suspended prior version; their snapshots stop. Drift surfaces in MLS-19 (binding state) per the MLS substrate (DEC-e7b7b3) |
| Semantic shift goes unreviewed | Snapshots produced post-shift carry semantically different values without annotation. Risk surface that the platform mitigates only via human review discipline |

## Drift Inventory

| Drift item | Status |
|---|---|
| Runtime drift detection (reader-level payload diff against catalog) | Recorded; runtime probe is separate ADR (Runtime Drift Detection); in the readiness baseline, drift exits exclusively via per-record rejection + ad-hoc rejection-rate observation |
| Auto-proposed major version on detected destructive drift | Recorded; operator-driven in the readiness baseline; AI-assisted authoring is a future surface |
| Semantic drift review queue | Recorded; mechanism not yet locked. In the readiness baseline, semantic drift is undetected unless a downstream metric reader reports anomalous values |
| `tenant.contract_binding` lifecycle on supersession (auto-migrate vs auto-suspend default) | Recorded; tracked under TSK-e6ffdc |
| `chain_status.break_summary_json.reason_code` integration | Recorded under TSK-296271 (deferred per DEC-bebaec drift inventory); when implemented, populated `reason_code` values flow back into the MLS substrate via trigger binding |

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| Sources and the Catalog | Source catalog model and onboarding flow | The version-bump policy that catalog mutations trigger |
| The Contract Grammar | Contract body schemas | The change kinds (additive / destructive / semantic) per contract family and the bump policy for each |
| Contract Chain Assembly | The contract chain assembly procedure | The cascade through chain consumers when a contract version bumps |
| Admission and Observation | The runtime admission boundary | The destructive cascade at runtime; integration with `validation_policy` |
| Chain Completeness and Verdict | The chain status SSOT | The break codes that surface when destructive bumps cascade and dependents fall behind |
| Decision and Change Procedure | The governance change-record substrate | The procedural backing for major-bump approvals as governance acts |

## References

- Sources and the Catalog
- The Contract Grammar
- Contract Chain Assembly
- Admission and Observation
- Chain Completeness and Verdict
- Decision and Change Procedure
- DEC-bebaec (Chain Completeness SSOT) — version transition window
- DEC-c9e623 (MLS Framework) — lifecycle states the cascade flows through
- DEC-e7b7b3 (MLS State Substrate) — read model where detected changes surface
- DEC-95687d (Nightly Reconciler) — the cascade fanout machinery
- v2 ADR-0002, ADR-0003 — version model (Major / Minor / Update)
- v2 ADR-09b8e6, ADR-05140c — minor-bump policy on additive field changes
- v2 cc-creation-sop §"CC Versioning policy" — original classification table generalized in this chapter
