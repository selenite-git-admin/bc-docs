#!/usr/bin/env python3
"""Write the first-pass migration decision report."""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "migration-plan.md"


def latest_run_id(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT run_id FROM inventory_runs WHERE run_kind='source_inventory' AND status='completed' ORDER BY run_id DESC LIMIT 1"
    ).fetchone()
    if not row:
        raise SystemExit("no completed source inventory run found")
    return int(row[0])


def table(lines: list[str], headers: tuple[str, ...], rows: list[tuple[object, ...]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        lines.append("| " + " | ".join(str(col) for col in row) + " |")


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        run_id = latest_run_id(conn)
        total_docs = conn.execute(
            "SELECT COUNT(*) FROM source_documents WHERE run_id = ?",
            (run_id,),
        ).fetchone()[0]
        decision_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM migration_decisions md
            JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
            WHERE sd.run_id = ?
            """,
            (run_id,),
        ).fetchone()[0]
        lines = [
            "# v4 Migration Plan",
            "",
            f"Inventory run: `{run_id}`",
            f"Source documents: `{total_docs}`",
            f"Documents with migration decisions: `{decision_count}`",
            "",
            "This report combines the first-pass control-plane classification and the second-pass undecided review. It does not copy prose from v3. `regenerate_from_source` rows remain intentionally unimported until generators rebuild them from current source.",
            "",
            "## Decision Summary",
            "",
        ]
        table(
            lines,
            ("Decision", "Files"),
            conn.execute(
                """
                SELECT md.decision_code, COUNT(*)
                FROM migration_decisions md
                JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
                WHERE sd.run_id = ?
                GROUP BY md.decision_code
                ORDER BY COUNT(*) DESC, md.decision_code
                """,
                (run_id,),
            ).fetchall(),
        )
        lines.extend(["", "## Target Kinds", ""])
        table(
            lines,
            ("Target Kind", "Files"),
            conn.execute(
                """
                SELECT COALESCE(md.target_kind, '(none)'), COUNT(*)
                FROM migration_decisions md
                JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
                WHERE sd.run_id = ?
                GROUP BY COALESCE(md.target_kind, '(none)')
                ORDER BY COUNT(*) DESC, COALESCE(md.target_kind, '(none)')
                """,
                (run_id,),
            ).fetchall(),
        )
        lines.extend(["", "## Reader Visibility", ""])
        table(
            lines,
            ("Visibility", "Files"),
            conn.execute(
                """
                SELECT md.reader_visibility, COUNT(*)
                FROM migration_decisions md
                JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
                WHERE sd.run_id = ?
                GROUP BY md.reader_visibility
                ORDER BY COUNT(*) DESC, md.reader_visibility
                """,
                (run_id,),
            ).fetchall(),
        )
        lines.extend(["", "## Current Truth Flag", ""])
        table(
            lines,
            ("Current Truth", "Files"),
            conn.execute(
                """
                SELECT md.current_truth, COUNT(*)
                FROM migration_decisions md
                JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
                WHERE sd.run_id = ?
                GROUP BY md.current_truth
                ORDER BY md.current_truth DESC
                """,
                (run_id,),
            ).fetchall(),
        )
        lines.extend(["", "## High-Confidence Current Chapters", ""])
        current_rows = conn.execute(
            """
            SELECT sd.top_level_dir, sd.rel_path, md.target_path
            FROM migration_decisions md
            JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
            WHERE sd.run_id = ? AND md.decision_code = 'migrate_current'
            ORDER BY sd.top_level_dir, sd.rel_path
            """,
            (run_id,),
        ).fetchall()
        table(lines, ("Section", "Source", "Target"), current_rows)

        lines.extend(["", "## Regenerate Instead Of Copy", ""])
        regen_rows = conn.execute(
            """
            SELECT sd.rel_path, md.target_path, md.rationale
            FROM migration_decisions md
            JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
            WHERE sd.run_id = ? AND md.decision_code = 'regenerate_from_source'
            ORDER BY sd.rel_path
            """,
            (run_id,),
        ).fetchall()
        table(lines, ("Source", "Planned Target", "Rationale"), regen_rows)

        lines.extend(["", "## Evidence Preserved Outside Reader Flow", ""])
        evidence_rows = conn.execute(
            """
            SELECT md.target_kind, COUNT(*)
            FROM migration_decisions md
            JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
            WHERE sd.run_id = ? AND md.decision_code = 'migrate_evidence'
            GROUP BY md.target_kind
            ORDER BY COUNT(*) DESC, md.target_kind
            """,
            (run_id,),
        ).fetchall()
        table(lines, ("Evidence Kind", "Files"), evidence_rows)

        lines.extend(["", "## Undecided Review Queue", ""])
        undecided_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM migration_decisions md
            JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
            WHERE sd.run_id = ? AND md.decision_code = 'undecided'
            """,
            (run_id,),
        ).fetchone()[0]
        lines.append(f"Total undecided: `{undecided_count}`")
        lines.append("")
        undecided_rows = conn.execute(
            """
            SELECT sd.guessed_kind, sd.rel_path, md.rationale
            FROM migration_decisions md
            JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
            WHERE sd.run_id = ? AND md.decision_code = 'undecided'
            ORDER BY sd.guessed_kind, sd.rel_path
            LIMIT 120
            """,
            (run_id,),
        ).fetchall()
        table(lines, ("Guessed Kind", "Source", "Reason"), undecided_rows)
        if undecided_count > len(undecided_rows):
            lines.append("")
            lines.append(f"_Report truncated to {len(undecided_rows)} undecided rows._")

        lines.extend([
            "",
            "## Next Migration Gates",
            "",
            "1. Clean link/path findings from `target-audit.md`, starting with missing internal links and legacy doc-root references.",
            "2. Build generators for API, schemas, and data dictionary before importing generated references.",
            "3. Run a correctness pass on primary reader-flow chapters against `bc-core` coverage.",
            "4. Keep source v3 read-only until explicit cutover.",
        ])
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
