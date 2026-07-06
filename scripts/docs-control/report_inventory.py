#!/usr/bin/env python3
"""Write a compact inventory report from the v4 control database."""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "initial-v3-inventory.md"


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        latest = conn.execute(
            "SELECT run_id, completed_at FROM inventory_runs WHERE run_kind='source_inventory' ORDER BY run_id DESC LIMIT 1"
        ).fetchone()
        if not latest:
            raise SystemExit("no source inventory run found")
        run_id, completed_at = latest
        lines = [
            "# Initial v3 Inventory",
            "",
            f"Run: `{run_id}`",
            f"Completed: `{completed_at}`",
            "",
            "This report is generated from the v4 SQLite control database. It inventories `bc-docs-v3` as read-only source material; it does not migrate or edit source content.",
            "",
            "## By Top-Level Directory",
            "",
            "| Directory | Files |",
            "|---|---:|",
        ]
        for top, count in conn.execute(
            "SELECT top_level_dir, COUNT(*) FROM source_documents WHERE run_id = ? GROUP BY top_level_dir ORDER BY top_level_dir",
            (run_id,),
        ):
            lines.append(f"| `{top}` | {count} |")
        lines.extend([
            "",
            "## By Guessed Kind",
            "",
            "| Kind | Files |",
            "|---|---:|",
        ])
        for kind, count in conn.execute(
            "SELECT guessed_kind, COUNT(*) FROM source_documents WHERE run_id = ? GROUP BY guessed_kind ORDER BY COUNT(*) DESC, guessed_kind",
            (run_id,),
        ):
            lines.append(f"| `{kind}` | {count} |")
        lines.extend([
            "",
            "## Frontmatter Coverage",
            "",
            "| Has Frontmatter | Files |",
            "|---|---:|",
        ])
        for has_fm, count in conn.execute(
            "SELECT has_frontmatter, COUNT(*) FROM source_documents WHERE run_id = ? GROUP BY has_frontmatter ORDER BY has_frontmatter DESC",
            (run_id,),
        ):
            label = "yes" if has_fm else "no"
            lines.append(f"| {label} | {count} |")
        lines.extend([
            "",
            "## Link Risk Snapshot",
            "",
            "| Scope | Links | Missing/Flagged |",
            "|---|---:|---:|",
        ])
        for scope, total, flagged in conn.execute(
            """
            SELECT COALESCE(target_scope, 'unknown'), COUNT(*),
                   SUM(CASE WHEN finding_severity IS NOT NULL OR target_exists = 0 THEN 1 ELSE 0 END)
            FROM extracted_links
            WHERE source_doc_id IN (SELECT source_doc_id FROM source_documents WHERE run_id = ?)
            GROUP BY COALESCE(target_scope, 'unknown')
            ORDER BY COUNT(*) DESC
            """,
            (run_id,),
        ):
            lines.append(f"| `{scope}` | {total} | {flagged or 0} |")
        lines.extend([
            "",
            "## Next Decisions",
            "",
            "- Tune classification rules before copying any prose.",
            "- Mark current chapters versus evidence/archive candidates.",
            "- Regenerate API, schema, and data-dictionary references from source code instead of migrating stale generated pages.",
            "- Keep `bc-docs-v3` untouched until final cutover.",
        ])
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
