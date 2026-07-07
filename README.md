# bc-docs

Canonical documentation spine for BareCount.

This repository is the governed documentation source of truth after the 2026-07-07 v3 to canonical cutover. The former `bc-docs-v3` tree is retired source material; new documentation work should land here through the control-plane and governance rules below.

## Purpose

`bc-docs` is the controlled documentation spine:

- Markdown remains the human-readable artifact.
- SQLite is the control plane for inventory, migration decisions, provenance, navigation, freshness, coverage, and audit findings.
- Generated references are regenerated from source systems instead of copied as current truth.
- Historical DBCPs, closeouts, work records, ledgers, and dated snapshots are preserved as evidence, not promoted into current reader navigation.

## First Rule

Do not bulk-copy legacy documentation into the canonical tree. Every source document must pass through the migration ledger with a classification and a decision.

## Local Commands

```powershell
python scripts/docs-control/init_db.py
python scripts/docs-control/inventory_v3.py --source C:\MyProjects\bc-docs-v3-retired-2026-07-07
python scripts/docs-control/classify_migration.py
python scripts/docs-control/report_inventory.py
python scripts/docs-control/report_migration_plan.py
python scripts/docs-control/import_approved.py --dry-run
python scripts/docs-control/import_approved.py
python scripts/docs-control/seed_navigation.py
python scripts/docs-control/audit_target_docs.py
python scripts/docs-control/inventory_bc_core.py
```

Generated SQLite state lives at `docs-control/docs-control.db` and is intentionally ignored by Git until a later decision says otherwise. Replayable exports for operator-approved delta syncs live under `docs-control/exports/`.

## Current State

- The v3-to-canonical migration is ledgered under `docs-control/reports/` and `docs-control/exports/`.
- Approved v3 documents were imported only after classification and review.
- API, schema, and data-dictionary references are regenerated from source rather than copied as truth.
- Raw evidence that is not reader navigation is preserved under `docs/evidence/`.
- Diagrams and supporting assets are mirrored under `docs/assets/` and remain byte-for-byte covered by the migration checks.
