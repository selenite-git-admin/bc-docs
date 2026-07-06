#!/usr/bin/env python3
"""Write the deferred v3-root reference cutover plan from the latest target audit."""
from __future__ import annotations

import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "cutover-reference-plan.md"


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_table(lines: list[str], headers: list[str], rows: list[tuple[object, ...]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        lines.append("| " + " | ".join(markdown_escape(value) for value in row) + " |")


def latest_audit_run(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        """
        SELECT MAX(run_id)
        FROM inventory_runs
        WHERE tool_name = 'audit_target_docs.py'
          AND status = 'completed'
        """
    ).fetchone()
    if row is None or row[0] is None:
        raise SystemExit("no completed target audit run found")
    return int(row[0])


def token_from_message(message: str) -> str:
    parts = message.split("`")
    if len(parts) > 1:
        return parts[1]
    return message


def stale_rows(conn: sqlite3.Connection, audit_run_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
          af.severity,
          af.subject_path,
          af.message,
          COALESCE(td.document_kind, '') AS document_kind,
          COALESCE(td.reader_visibility, '') AS reader_visibility,
          COALESCE(td.current_truth, 0) AS current_truth
        FROM audit_findings af
        LEFT JOIN target_documents td
          ON td.canonical_path = af.subject_path
        WHERE af.run_id = ?
          AND af.category = 'stale-doc-root-reference'
        ORDER BY
          CASE af.severity WHEN 'blocker' THEN 1 WHEN 'error' THEN 2 WHEN 'warning' THEN 3 ELSE 4 END,
          af.subject_path
        """,
        (audit_run_id,),
    ).fetchall()


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        audit_run_id = latest_audit_run(conn)
        rows = stale_rows(conn, audit_run_id)

    severity_counts = Counter(row["severity"] for row in rows)
    token_counts = Counter((row["severity"], token_from_message(row["message"])) for row in rows)
    kind_counts = Counter((row["severity"], row["document_kind"], row["reader_visibility"]) for row in rows)

    warning_rows = [row for row in rows if row["severity"] == "warning"]
    info_rows = [row for row in rows if row["severity"] == "info"]

    lines = [
        "# Cutover Reference Plan",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Audit run: `{audit_run_id}`",
        f"Deferred references: `{len(rows)}`",
        "",
        "## Safety Boundary",
        "",
        "- Do not repoint these references while active Claude sessions still rely on `bc-docs-v3`.",
        "- Do not rename `bc-docs-v4` to `bc-docs` until the user explicitly approves the cutover window.",
        "- Treat evidence and archive references as historical provenance unless the cutover report marks them as operational links.",
        "",
        "## Summary By Severity",
        "",
    ]
    write_table(lines, ["Severity", "References"], sorted(severity_counts.items()))
    lines.extend(["", "## Summary By Token", ""])
    write_table(lines, ["Severity", "Token", "References"], [(severity, token, count) for (severity, token), count in sorted(token_counts.items())])
    lines.extend(["", "## Summary By Document Kind", ""])
    write_table(
        lines,
        ["Severity", "Document Kind", "Visibility", "References"],
        [(severity, kind, visibility, count) for (severity, kind, visibility), count in sorted(kind_counts.items())],
    )
    lines.extend(
        [
            "",
            "## Warning References",
            "",
            "These are current or reader-visible references to review first during cutover.",
            "",
        ]
    )
    write_table(
        lines,
        ["Path", "Document Kind", "Visibility", "Current Truth", "Token"],
        [
            (
                row["subject_path"],
                row["document_kind"],
                row["reader_visibility"],
                row["current_truth"],
                token_from_message(row["message"]),
            )
            for row in warning_rows
        ],
    )
    lines.extend(
        [
            "",
            "## Informational References",
            "",
            "These are evidence, archive, or hidden references. Preserve them when they are historical provenance; repoint only if they are operational links.",
            "",
        ]
    )
    write_table(
        lines,
        ["Path", "Document Kind", "Visibility", "Current Truth", "Token"],
        [
            (
                row["subject_path"],
                row["document_kind"],
                row["reader_visibility"],
                row["current_truth"],
                token_from_message(row["message"]),
            )
            for row in info_rows
        ],
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
