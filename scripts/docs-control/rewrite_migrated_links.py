#!/usr/bin/env python3
"""Rewrite copied v3 Markdown links to their v4 migration targets."""
from __future__ import annotations

import argparse
import posixpath
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "link-rewrite-report.md"

LINK_RE = re.compile(r"(!?\[([^\]]*)\]\()([^)]+)(\))")
ABS_LOCAL_RE = re.compile(r"(?i)([A-Z]:[\\/][^\s)]+|/Users/[^\s)]+|/home/[^\s)]+)")


@dataclass(frozen=True)
class DocRow:
    source_rel: str
    target_path: str


@dataclass(frozen=True)
class Rewrite:
    canonical_path: str
    old_target: str
    new_target: str
    source_resolved: str
    mapped_target: str


def is_external_or_special(target: str) -> bool:
    parsed = urlparse(target)
    return parsed.scheme in {"http", "https", "mailto", "tel", "mcp", "app", "data"}


def clean_link(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    return raw


def split_fragment(target: str) -> tuple[str, str]:
    if "#" not in target:
        return target, ""
    path, fragment = target.split("#", 1)
    return path, "#" + fragment


def normalize_posix(path: str) -> str:
    normalized = posixpath.normpath(path.replace("\\", "/"))
    return "" if normalized == "." else normalized


def source_link_target(source_rel: str, raw_target: str) -> str | None:
    target = clean_link(raw_target)
    if not target or target.startswith("#") or is_external_or_special(target):
        return None
    if ABS_LOCAL_RE.search(target):
        return None
    path_part, _fragment = split_fragment(target)
    path_part = unquote(path_part)
    if not path_part:
        return None
    if path_part.startswith("/docs/"):
        return normalize_posix(path_part.removeprefix("/docs/"))
    if path_part.startswith("/"):
        return None
    source_parent = str(PurePosixPath(source_rel).parent)
    if source_parent == ".":
        source_parent = ""
    return normalize_posix(posixpath.join(source_parent, path_part))


def relative_link(from_canonical: str, to_canonical: str, fragment: str) -> str:
    from_parent = posixpath.dirname(from_canonical)
    rel = posixpath.relpath(to_canonical, from_parent or ".")
    return rel + fragment


def load_docs(conn: sqlite3.Connection) -> list[DocRow]:
    rows = conn.execute(
        """
        SELECT sd.rel_path, td.canonical_path
        FROM target_documents td
        JOIN source_documents sd ON sd.source_doc_id = td.source_doc_id
        ORDER BY td.canonical_path
        """
    ).fetchall()
    return [DocRow(row[0], row[1]) for row in rows]


def load_source_map(conn: sqlite3.Connection) -> dict[str, str]:
    rows = conn.execute(
        """
        SELECT sd.rel_path, md.target_path
        FROM migration_decisions md
        JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
        WHERE md.target_path IS NOT NULL
          AND md.decision_code IN (
            'migrate_current',
            'migrate_reference',
            'migrate_governance',
            'migrate_evidence',
            'archive_only'
          )
        """
    ).fetchall()
    return {normalize_posix(row[0]): normalize_posix(row[1]) for row in rows}


def replacement_for(doc: DocRow, raw_target: str, source_map: dict[str, str]) -> tuple[str, str, str] | None:
    target = clean_link(raw_target)
    path_part, fragment = split_fragment(target)
    resolved_source = source_link_target(doc.source_rel, raw_target)
    if not resolved_source:
        return None
    mapped_target = source_map.get(resolved_source)
    if not mapped_target:
        return None
    mapped_file = ROOT / mapped_target
    if not mapped_file.exists():
        return None
    new_target = relative_link(doc.target_path, mapped_target, fragment)
    if new_target == target or new_target == raw_target:
        return None
    if path_part.startswith("/docs/assets/"):
        return None
    return new_target, resolved_source, mapped_target


def rewrite_text(doc: DocRow, text: str, source_map: dict[str, str]) -> tuple[str, list[Rewrite]]:
    rewrites: list[Rewrite] = []

    def replace(match: re.Match[str]) -> str:
        prefix, _label, raw_target, suffix = match.groups()
        result = replacement_for(doc, raw_target, source_map)
        if not result:
            return match.group(0)
        new_target, resolved_source, mapped_target = result
        rewrites.append(
            Rewrite(
                canonical_path=doc.target_path,
                old_target=raw_target,
                new_target=new_target,
                source_resolved=resolved_source,
                mapped_target=mapped_target,
            )
        )
        return f"{prefix}{new_target}{suffix}"

    return LINK_RE.sub(replace, text), rewrites


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def write_report(dry_run: bool, rewrites: list[Rewrite], skipped_missing_files: list[str]) -> None:
    by_doc = Counter(rewrite.canonical_path for rewrite in rewrites)
    lines = [
        "# Migrated Link Rewrite Report",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Dry run: `{dry_run}`",
        f"Rewrites: `{len(rewrites)}`",
        f"Files touched: `{len(by_doc)}`",
        f"Missing registered files skipped: `{len(skipped_missing_files)}`",
        "",
        "## Top Files",
        "",
        "| File | Rewrites |",
        "|---|---|",
    ]
    for path, count in by_doc.most_common(40):
        lines.append(f"| {markdown_escape(path)} | {count} |")
    lines.extend(["", "## Sample Rewrites", "", "| File | Old Target | New Target | Source Resolved |", "|---|---|---|---|"])
    for rewrite in rewrites[:120]:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(rewrite.canonical_path),
                    markdown_escape(rewrite.old_target),
                    markdown_escape(rewrite.new_target),
                    markdown_escape(rewrite.source_resolved),
                ]
            )
            + " |"
        )
    if skipped_missing_files:
        lines.extend(["", "## Missing Registered Files", ""])
        for path in skipped_missing_files[:80]:
            lines.append(f"- `{path}`")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes to Markdown files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        docs = load_docs(conn)
        source_map = load_source_map(conn)
    all_rewrites: list[Rewrite] = []
    skipped_missing_files: list[str] = []
    for doc in docs:
        path = ROOT / doc.target_path
        if not path.exists():
            skipped_missing_files.append(doc.target_path)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        new_text, rewrites = rewrite_text(doc, text, source_map)
        if not rewrites:
            continue
        all_rewrites.extend(rewrites)
        if args.apply:
            path.write_text(new_text, encoding="utf-8")
    write_report(not args.apply, all_rewrites, skipped_missing_files)
    print(f"rewrites={len(all_rewrites)} files={len(set(r.canonical_path for r in all_rewrites))} apply={args.apply}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
