#!/usr/bin/env python3
"""Normalize legacy repository-root names in selected docs."""
from __future__ import annotations

import argparse
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "legacy-root-normalization-report.md"

REPLACEMENTS = [
    ("C:\\MyProjects\\bc-docs-v2", "legacy-v2-docs-root"),
    ("C:/MyProjects/bc-docs-v2", "legacy-v2-docs-root"),
    ("bc-docs-v2/docs/reference/sources/", "legacy-v2/reference/sources/"),
    ("bc-docs-v2/docs/", "legacy-v2/docs/"),
    ("bc-docs-v2/", "legacy-v2/"),
    ("bc-docs-v2", "legacy v2 archive"),
    ("BareCount-Documentation", "legacy BareCount documentation"),
    ("BareCount-Intra-Site", "legacy BareCount intra-site"),
    ("documentation.cxofacts", "legacy documentation site"),
    ("platform-documentation/", "legacy-platform-docs/"),
    ("platform-documentation", "legacy platform documentation"),
]


@dataclass(frozen=True)
class ReplacementCount:
    canonical_path: str
    old_text: str
    new_text: str
    count: int


def latest_audit_run(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT MAX(run_id) FROM inventory_runs WHERE tool_name = 'audit_target_docs.py'"
    ).fetchone()
    if row is None or row[0] is None:
        raise SystemExit("no audit_target_docs.py run found; run docs:audit first")
    return int(row[0])


def candidate_paths(conn: sqlite3.Connection, run_id: int, scope: str) -> list[str]:
    severity_clause = "AND severity = 'error'" if scope == "errors" else ""
    rows = conn.execute(
        f"""
        SELECT DISTINCT subject_path
        FROM audit_findings
        WHERE run_id = ?
          AND category = 'stale-doc-root-reference'
          {severity_clause}
        ORDER BY subject_path
        """,
        (run_id,),
    ).fetchall()
    return [row[0] for row in rows]


def normalize_text(canonical_path: str, text: str) -> tuple[str, list[ReplacementCount]]:
    changes: list[ReplacementCount] = []
    next_text = text
    for old_text, new_text in REPLACEMENTS:
        count = next_text.count(old_text)
        if not count:
            continue
        next_text = next_text.replace(old_text, new_text)
        changes.append(ReplacementCount(canonical_path, old_text, new_text, count))
    return next_text, changes


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def write_report(
    dry_run: bool,
    run_id: int,
    target_paths: list[str],
    changes: list[ReplacementCount],
    missing_files: list[str],
) -> None:
    by_doc = Counter()
    by_token = Counter()
    for change in changes:
        by_doc[change.canonical_path] += change.count
        by_token[change.old_text] += change.count
    lines = [
        "# Legacy Root Normalization Report",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Dry run: `{dry_run}`",
        f"Audit run source: `{run_id}`",
        f"Candidate files: `{len(target_paths)}`",
        f"Replacements: `{sum(change.count for change in changes)}`",
        f"Files touched: `{len(by_doc)}`",
        f"Missing candidate files skipped: `{len(missing_files)}`",
        "",
        "## Tokens",
        "",
        "| Old Token | Replacements |",
        "|---|---|",
    ]
    for token, count in by_token.most_common():
        lines.append(f"| {markdown_escape(token)} | {count} |")
    lines.extend(["", "## Files", "", "| File | Replacements |", "|---|---|"])
    for path, count in by_doc.most_common(80):
        lines.append(f"| {markdown_escape(path)} | {count} |")
    lines.extend(["", "## Replacement Rules Hit", "", "| File | Old | New | Count |", "|---|---|---|---|"])
    for change in changes[:140]:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(change.canonical_path),
                    markdown_escape(change.old_text),
                    markdown_escape(change.new_text),
                    str(change.count),
                ]
            )
            + " |"
        )
    if missing_files:
        lines.extend(["", "## Missing Candidate Files", ""])
        for path in missing_files[:80]:
            lines.append(f"- `{path}`")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes to Markdown files")
    parser.add_argument(
        "--scope",
        choices=["errors", "all-stale"],
        default="errors",
        help="errors limits cleanup to hard stale-root findings; all-stale targets every stale-root finding in the latest audit",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        run_id = latest_audit_run(conn)
        paths = candidate_paths(conn, run_id, args.scope)
    all_changes: list[ReplacementCount] = []
    missing_files: list[str] = []
    for canonical_path in paths:
        path = ROOT / canonical_path
        if not path.exists():
            missing_files.append(canonical_path)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        new_text, changes = normalize_text(canonical_path, text)
        if changes and args.apply:
            path.write_text(new_text, encoding="utf-8", newline="\n")
        all_changes.extend(changes)
    write_report(not args.apply, run_id, paths, all_changes, missing_files)
    print(f"replacements={sum(change.count for change in all_changes)} files={len(set(change.canonical_path for change in all_changes))} apply={args.apply}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
