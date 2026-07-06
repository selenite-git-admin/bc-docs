# bc-docs-v4

Clean-room documentation rebuild for BareCount.

This repository is isolated from the live Claude-facing `bc-docs-v3` tree. During the v4 build, `bc-docs-v3` is treated as read-only source material. No Claude, DevHub, MCP, bc-core, or bc-admin defaults should be repointed to this repository until the cutover window is explicitly approved.

## Purpose

v4 is the controlled documentation spine:

- Markdown remains the human-readable artifact.
- SQLite is the control plane for inventory, migration decisions, provenance, navigation, freshness, coverage, and audit findings.
- Generated references are regenerated from source systems instead of copied as current truth.
- Historical DBCPs, closeouts, work records, ledgers, and dated snapshots are preserved as evidence, not promoted into current reader navigation.

## First Rule

Do not bulk-copy v3 into v4. Every source document must pass through the migration ledger with a classification and a decision.

## Local Commands

```powershell
python scripts/docs-control/init_db.py
python scripts/docs-control/inventory_v3.py --source C:\MyProjects\bc-docs-v3
python scripts/docs-control/classify_migration.py
python scripts/docs-control/report_inventory.py
python scripts/docs-control/report_migration_plan.py
python scripts/docs-control/import_approved.py --dry-run
python scripts/docs-control/import_approved.py
python scripts/docs-control/seed_navigation.py
python scripts/docs-control/audit_target_docs.py
python scripts/docs-control/inventory_bc_core.py
```

Generated SQLite state lives at `docs-control/docs-control.db` and is intentionally ignored by Git until a later decision says otherwise.

## Current Build State

- v3 inventory, migration decisions, undecided review, import report, navigation report, target audit, and `bc-core` coverage report are under `docs-control/reports/`.
- Approved v3 documents have been imported only after classification and second-pass review.
- API, schema, and data-dictionary references are not copied as truth; they are marked for regeneration from source.
- The formerly undecided v3 documents have been reviewed; one template is rejected and the rest are current, reference, evidence, or archive-only.
- v4 is not the live docs root and must not be renamed or repointed until the explicit cutover window.
