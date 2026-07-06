# v4 Migration Ground Rules

1. `bc-docs-v3` is read-only source material.
2. All new work happens in `bc-docs-v4` until cutover.
3. No bulk copy is accepted as migration.
4. Every source document gets a classification before it can land as a v4 document.
5. Historical evidence is preserved, not promoted as current truth.
6. Anything not migrated receives a reason.
7. Provenance travels with content: source path, checksum, source metadata, decision, and migration timestamp.
8. Generated references are regenerated from current code or live source state where possible.
9. Navigation is controlled by SQLite, not folder shape alone.
10. Tooling defaults stay isolated until the final rename/cutover window.
11. Guardrails must detect old paths and stale doc roots before cutover.
12. Renaming v4 to `bc-docs` and updating Claude ecosystem references is a separate operator-approved operation.
