#!/usr/bin/env python3
"""Convert machine-local and cross-repo Markdown links into inert code references."""
from __future__ import annotations

import argparse
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "local-link-normalization-report.md"

LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")
ABS_LOCAL_RE = re.compile(r"(?i)([A-Z]:[\\/][^\s)]+|/Users/[^\s)]+|/home/[^\s)]+)")


@dataclass(frozen=True)
class Replacement:
    canonical_path: str
    label: str
    old_target: str
    replacement: str
    reason: str


def clean_link(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    return raw


def is_external_or_special(target: str) -> bool:
    parsed = urlparse(target)
    return parsed.scheme in {"http", "https", "mailto", "tel", "mcp", "app", "data"}


def within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def code_text(label: str, target: str) -> str:
    value = label.strip() or target.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        value = value[1:-1]
    value = value.replace("`", "'")
    return f"`{value}`"


def link_reason(source_path: Path, target: str) -> str | None:
    if not target or target.startswith("#") or is_external_or_special(target):
        return None
    if ABS_LOCAL_RE.search(target) or re.match(r"^[A-Z]:\\", target, flags=re.IGNORECASE):
        return "absolute-local-link"
    path_part = unquote(target.split("#", 1)[0])
    if not path_part:
        return None
    docs_root = (ROOT / "docs").resolve()
    if path_part.startswith("/docs/"):
        resolved = (ROOT / path_part.lstrip("/")).resolve()
    else:
        resolved = (source_path.parent / path_part).resolve()
    if not within(resolved, docs_root):
        return "link-escapes-docs-root"
    return None


def target_paths(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT canonical_path FROM target_documents ORDER BY canonical_path").fetchall()
    return [row[0] for row in rows]


def rewrite_text(canonical_path: str, text: str) -> tuple[str, list[Replacement]]:
    source_path = (ROOT / canonical_path).resolve()
    replacements: list[Replacement] = []

    def replace(match: re.Match[str]) -> str:
        bang, label, raw_target = match.groups()
        if bang:
            return match.group(0)
        target = clean_link(raw_target)
        reason = link_reason(source_path, target)
        if not reason:
            return match.group(0)
        replacement = code_text(label, target)
        replacements.append(
            Replacement(
                canonical_path=canonical_path,
                label=label,
                old_target=target,
                replacement=replacement,
                reason=reason,
            )
        )
        return replacement

    return LINK_RE.sub(replace, text), replacements


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def write_report(dry_run: bool, replacements: list[Replacement], missing_files: list[str]) -> None:
    by_doc = Counter(replacement.canonical_path for replacement in replacements)
    by_reason = Counter(replacement.reason for replacement in replacements)
    lines = [
        "# Local Link Normalization Report",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Dry run: `{dry_run}`",
        f"Replacements: `{len(replacements)}`",
        f"Files touched: `{len(by_doc)}`",
        f"Missing registered files skipped: `{len(missing_files)}`",
        "",
        "## Reasons",
        "",
        "| Reason | Replacements |",
        "|---|---|",
    ]
    for reason, count in sorted(by_reason.items()):
        lines.append(f"| {markdown_escape(reason)} | {count} |")
    lines.extend(["", "## Files", "", "| File | Replacements |", "|---|---|"])
    for path, count in by_doc.most_common(40):
        lines.append(f"| {markdown_escape(path)} | {count} |")
    lines.extend(["", "## Sample Replacements", "", "| File | Label | Old Target | Replacement | Reason |", "|---|---|---|---|---|"])
    for replacement in replacements[:120]:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(replacement.canonical_path),
                    markdown_escape(replacement.label),
                    markdown_escape(replacement.old_target),
                    markdown_escape(replacement.replacement),
                    markdown_escape(replacement.reason),
                ]
            )
            + " |"
        )
    if missing_files:
        lines.extend(["", "## Missing Registered Files", ""])
        for path in missing_files[:80]:
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
        paths = target_paths(conn)
    all_replacements: list[Replacement] = []
    missing_files: list[str] = []
    for canonical_path in paths:
        path = ROOT / canonical_path
        if not path.exists():
            missing_files.append(canonical_path)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        new_text, replacements = rewrite_text(canonical_path, text)
        if replacements and args.apply:
            path.write_text(new_text, encoding="utf-8", newline="\n")
        all_replacements.extend(replacements)
    write_report(not args.apply, all_replacements, missing_files)
    print(f"replacements={len(all_replacements)} files={len(set(r.canonical_path for r in all_replacements))} apply={args.apply}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
