#!/usr/bin/env python3
"""Write the current v4 documentation cleanup queue from SQLite state."""
from __future__ import annotations

import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "cleanup-queue.md"
MUTABLE_REPORT_PATH = ROOT / "docs-control" / "reports" / "mutable-claim-review.md"

MUTABLE_CATEGORIES = {
    "temporal-claim",
    "iso-date-claim",
    "percentage-stat",
    "large-number-stat",
    "unit-stat",
}


def latest_run(conn: sqlite3.Connection, tool_name: str) -> int | None:
    row = conn.execute(
        "SELECT MAX(run_id) FROM inventory_runs WHERE tool_name = ? AND status = 'completed'",
        (tool_name,),
    ).fetchone()
    if row is None or row[0] is None:
        return None
    return int(row[0])


def scalar(conn: sqlite3.Connection, sql: str, params: tuple[object, ...] = ()) -> int:
    row = conn.execute(sql, params).fetchone()
    return int(row[0] or 0)


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def write_table(lines: list[str], headers: list[str], rows: list[tuple[object, ...]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        lines.append("| " + " | ".join(markdown_escape(value) for value in row) + " |")


def audit_category_rows(conn: sqlite3.Connection, audit_run_id: int) -> list[tuple[str, str, int]]:
    return [
        (row[0], row[1], int(row[2]))
        for row in conn.execute(
            """
            SELECT severity, category, COUNT(*)
            FROM audit_findings
            WHERE run_id = ?
            GROUP BY severity, category
            ORDER BY CASE severity WHEN 'blocker' THEN 1 WHEN 'error' THEN 2 WHEN 'warning' THEN 3 ELSE 4 END,
                     category
            """,
            (audit_run_id,),
        )
    ]


def top_warning_docs(conn: sqlite3.Connection, audit_run_id: int) -> list[tuple[str, int, str]]:
    rows = conn.execute(
        """
        SELECT subject_path, COUNT(*) AS findings, GROUP_CONCAT(DISTINCT category)
        FROM audit_findings
        WHERE run_id = ?
          AND severity = 'warning'
        GROUP BY subject_path
        ORDER BY findings DESC, subject_path
        LIMIT 30
        """,
        (audit_run_id,),
    ).fetchall()
    return [(row[0], int(row[1]), row[2] or "") for row in rows]


def stale_token_rows(conn: sqlite3.Connection, audit_run_id: int) -> list[tuple[str, str, int]]:
    counts: Counter[tuple[str, str]] = Counter()
    for severity, message in conn.execute(
        """
        SELECT severity, message
        FROM audit_findings
        WHERE run_id = ?
          AND category = 'stale-doc-root-reference'
        """,
        (audit_run_id,),
    ):
        parts = str(message).split("`")
        token = parts[1] if len(parts) > 1 else str(message)
        counts[(severity, token)] += 1
    return [(severity, token, count) for (severity, token), count in sorted(counts.items())]


def regeneration_rows(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    rows = conn.execute(
        """
        SELECT sd.rel_path, COALESCE(md.target_path, ''), COALESCE(md.rationale, '')
        FROM migration_decisions md
        JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
        LEFT JOIN target_documents td ON td.canonical_path = md.target_path
        LEFT JOIN generated_references gr
          ON gr.target_doc_id = td.target_doc_id
         AND gr.freshness_status = 'fresh'
        WHERE md.decision_code = 'regenerate_from_source'
          AND gr.generated_ref_id IS NULL
        ORDER BY sd.rel_path
        """
    ).fetchall()
    return [(row[0], row[1], row[2]) for row in rows]


def generated_reference_pending_count(conn: sqlite3.Connection) -> int:
    return scalar(
        conn,
        """
        SELECT COUNT(*)
        FROM migration_decisions md
        LEFT JOIN target_documents td ON td.canonical_path = md.target_path
        LEFT JOIN generated_references gr
          ON gr.target_doc_id = td.target_doc_id
         AND gr.freshness_status = 'fresh'
        WHERE md.decision_code = 'regenerate_from_source'
          AND gr.generated_ref_id IS NULL
        """,
    )


def coverage_rows(conn: sqlite3.Connection) -> list[tuple[str, int, int, int]]:
    rows = conn.execute(
        """
        SELECT
          ct.target_type,
          COUNT(*) AS targets,
          SUM(CASE WHEN EXISTS (
            SELECT 1 FROM coverage_links cl WHERE cl.coverage_target_id = ct.coverage_target_id
          ) THEN 1 ELSE 0 END) AS linked
        FROM coverage_targets ct
        WHERE ct.repo_key = 'bc-core'
        GROUP BY ct.target_type
        ORDER BY ct.target_type
        """
    ).fetchall()
    return [(row[0], int(row[1]), int(row[2] or 0), int(row[1]) - int(row[2] or 0)) for row in rows]


def decision_rows(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    rows = conn.execute(
        "SELECT decision_code, COUNT(*) FROM migration_decisions GROUP BY decision_code ORDER BY decision_code"
    ).fetchall()
    return [(row[0], int(row[1])) for row in rows]


def mutable_report_summary() -> tuple[int | None, int | None]:
    if not MUTABLE_REPORT_PATH.exists():
        return None, None
    line_total: int | None = None
    body_total: int | None = None
    for line in MUTABLE_REPORT_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("Line findings:"):
            parts = line.split("`")
            if len(parts) > 1 and parts[1].isdigit():
                line_total = int(parts[1])
        if line.startswith("| body |"):
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) >= 2 and parts[1].isdigit():
                body_total = int(parts[1])
    if line_total is not None and body_total is None:
        body_total = 0
    return line_total, body_total


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        audit_run_id = latest_run(conn, "audit_target_docs.py")
        coverage_run_id = latest_run(conn, "inventory_bc_core.py")
        if audit_run_id is None:
            raise SystemExit("no completed audit run found")
        severity = Counter(
            {
                row[0]: int(row[1])
                for row in conn.execute(
                    "SELECT severity, COUNT(*) FROM audit_findings WHERE run_id = ? GROUP BY severity",
                    (audit_run_id,),
                )
            }
        )
        category_rows = audit_category_rows(conn, audit_run_id)
        stale_rows = stale_token_rows(conn, audit_run_id)
        category_counts = Counter()
        mutable_warning_total = 0
        stale_total = 0
        for _severity, category, count in category_rows:
            category_counts[category] += count
            if category in MUTABLE_CATEGORIES:
                mutable_warning_total += count
            if category == "stale-doc-root-reference":
                stale_total += count
        broken_link_total = sum(
            category_counts[category]
            for category in ["absolute-local-link", "link-escapes-docs-root", "missing-internal-link"]
        )
        target_docs = scalar(conn, "SELECT COUNT(*) FROM target_documents")
        generated_remaining = generated_reference_pending_count(conn)
        mutable_line_total, mutable_body_total = mutable_report_summary()
        coverage_total = scalar(conn, "SELECT COUNT(*) FROM coverage_targets WHERE repo_key = 'bc-core'")
        coverage_linked = scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM coverage_targets ct
            WHERE ct.repo_key = 'bc-core'
              AND EXISTS (
                SELECT 1 FROM coverage_links cl WHERE cl.coverage_target_id = ct.coverage_target_id
              )
            """,
        )
        lines = [
            "# v4 Cleanup Queue",
            "",
            f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
            f"Audit run: `{audit_run_id}`",
            f"Coverage run: `{coverage_run_id or 'not run'}`",
            "",
            "## Gate Status",
            "",
            f"- Target documents registered: `{target_docs}`",
            f"- Audit errors/blockers: `{severity['error'] + severity['blocker']}`",
            f"- Broken-link findings: `{broken_link_total}`",
            f"- Warning findings: `{severity['warning']}`",
            f"- Informational findings: `{severity['info']}`",
            f"- Mutable-claim review lines: `{mutable_line_total if mutable_line_total is not None else 'not generated'}`",
            f"- Mutable-claim body lines: `{mutable_body_total if mutable_body_total is not None else 'not generated'}`",
            f"- Generated references still pending regeneration: `{generated_remaining}`",
            f"- bc-core coverage targets linked: `{coverage_linked}/{coverage_total}`",
            "",
            "## Audit Categories",
            "",
        ]
        write_table(lines, ["Severity", "Category", "Findings"], category_rows)
        coverage_queue = (
            "4. Preserve bc-core coverage: all tracked bc-core targets are linked; keep generated references fresh as code evolves."
            if coverage_total and coverage_linked == coverage_total
            else "4. Expand bc-core coverage: prioritize unlinked controllers, services, schemas, and scripts that represent live user-facing or governance-critical behavior."
        )
        lines.extend(
            [
                "",
                "## Remaining Queues",
                "",
                f"1. Regenerate source-derived references: `{generated_remaining}` generated reference document(s) are missing or stale.",
                f"2. Review mutable current/reference claims: `{mutable_warning_total}` warning rows across temporal wording, dates, percentages, large numbers, and unit/count claims.",
                f"3. Defer v3 cutover references: `{stale_total}` remaining legacy-root mentions are warnings/info; after dead-root cleanup these should be v3-only until Claude/v3 cutover.",
                coverage_queue,
                "",
                "## Stale Root Tokens",
                "",
            ]
        )
        write_table(lines, ["Severity", "Token", "Findings"], stale_rows)
        lines.extend(
            [
                "",
                "## Migration Decisions",
                "",
            ]
        )
        write_table(lines, ["Decision", "Documents"], decision_rows(conn))
        lines.extend(["", "## Generated References Pending", ""])
        write_table(lines, ["Source", "Planned Target", "Rationale"], regeneration_rows(conn))
        lines.extend(["", "## bc-core Coverage", ""])
        write_table(lines, ["Target Type", "Targets", "With Links", "Without Links"], coverage_rows(conn))
        lines.extend(["", "## Top Warning Documents", ""])
        write_table(lines, ["Document", "Warnings", "Categories"], top_warning_docs(conn, audit_run_id))
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
