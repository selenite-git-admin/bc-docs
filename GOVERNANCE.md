# Documentation Governance Ground Rules

1. `bc-docs` is the canonical documentation source of truth.
2. The retired v3 tree is source provenance only; new work lands here.
3. No bulk copy is accepted as migration.
4. Every source document gets a classification before it can land as canonical documentation.
5. Historical evidence is preserved, not promoted as current truth.
6. Anything not migrated receives a reason.
7. Provenance travels with content: source path, checksum, source metadata, decision, and migration timestamp.
8. Generated references are regenerated from current code or live source state where possible.
9. Navigation is controlled by SQLite, not folder shape alone.
10. Tooling defaults point at the canonical `bc-docs` root after cutover.
11. Guardrails must detect old paths and stale doc roots.
12. Legacy-root references are allowed only inside historical evidence, archive material, or migration-control records where the old path is itself provenance.
