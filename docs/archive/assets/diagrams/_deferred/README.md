---
status: deferred
authority: reference
---

# Deferred Diagrams

Diagrams in this directory are not referenced from any chapter. They were imported from v2 but require structural redraw before they can satisfy v3 chapter authority. Keeping them here preserves the v2 source so a future structural redraw does not start from scratch.

The sync into `bc-admin/public/docs/` carries this directory along, but no chapter links to them. They are not discoverable through the docs reader sidebar.

## Why each is deferred

### DG-contract-chain-model.svg

**Reason:** Places Observation Contract in the "Canonical Chain" group. The Evaluation Boundaries chapter establishes that the admission boundary is governed by the Admission Contract together with the Observation Contract. The Observation Contract is admission-side, not canonical-side. The diagram's chain grouping therefore teaches a different boundary alignment than the chapter.

**Also drifted:** legacy labels `tenant_binding` and `canonical_field_map` that no longer match v3 names (`contract_binding` and Canonical Mapping respectively).

**Required for redraw:** move the Observation Contract box into the source-chain or admission-chain group, rename `tenant_binding` to `contract_binding`, replace `canonical_field_map` with `Canonical Mapping`. Removing the chain-grouping labels entirely is also acceptable if the rewrite would otherwise misrepresent the v3 boundary alignment.

### DG-runtime-topology.svg

**Reason:** The diagram shows Connector, Reader, Reader Flavor, Reader Binding, Source Contract, Observation Contract, and Business Object, but does not show Admission Contract or Admission Run. The Admission and Observation chapter names the Admission Contract as the validation governance applied at runtime, and names Admission Run as the tenant-scoped execution record. A runtime-topology diagram that omits both understates the topology the chapter describes.

**Required for redraw:** add an Admission Contract box on the platform-scoped side referenced by Reader Binding; add an Admission Run box on the tenant-scoped side produced by Reader invocation. The platform-tenant boundary should be visible in the diagram.

## Re-introduction process

When a structural redraw is performed:

1. Copy the SVG out of `_deferred/` back into `docs/assets/diagrams/`.
2. Verify all label text passes `scripts/diagram-rewrite.mjs` rules and the diagram-discipline checks in outline.
3. Re-add the chapter's frontmatter `diagrams:` entry and the body image markdown reference.
4. Re-sync and verify in bc-admin reader before commit.
5. Delete this entry from the deferred list.
