#!/usr/bin/env python3
"""Repair missing Markdown links using v4 file aliases and unique basename matches."""
from __future__ import annotations

import argparse
import posixpath
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = ROOT / "docs"
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "missing-link-repair-report.md"

LINK_RE = re.compile(r"(!?\[([^\]]*)\]\()([^)]+)(\))")
MISSING_RE = re.compile(r"Internal link `(.+?)` does not resolve from this document\.")

ALIASES = {
    "d335-mc-log.md": "docs/evidence/work-records/operations/d335/2026-04-15-mc-walkthrough-log.md",
    "mc-chain-integrity-sop.md": "docs/archive/onboarding/mc-chain-integrity.md",
}


@dataclass(frozen=True)
class Repair:
    canonical_path: str
    old_target: str
    new_target: str
    reason: str
    label: str


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


def code_text(label: str, target: str) -> str:
    value = label.strip() or target.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        value = value[1:-1]
    value = value.replace("`", "'")
    return f"`{value}`"


def latest_audit_run(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT MAX(run_id) FROM inventory_runs WHERE tool_name = 'audit_target_docs.py'"
    ).fetchone()
    if row is None or row[0] is None:
        raise SystemExit("no audit_target_docs.py run found; run docs:audit first")
    return int(row[0])


def missing_targets(conn: sqlite3.Connection, run_id: int) -> dict[str, set[str]]:
    rows = conn.execute(
        """
        SELECT subject_path, message
        FROM audit_findings
        WHERE run_id = ?
          AND category = 'missing-internal-link'
        ORDER BY subject_path, message
        """,
        (run_id,),
    ).fetchall()
    result: dict[str, set[str]] = defaultdict(set)
    for path, message in rows:
        match = MISSING_RE.search(message)
        if not match:
            continue
        result[path].add(match.group(1))
    return dict(result)


def file_index() -> dict[str, list[str]]:
    by_name: dict[str, list[str]] = defaultdict(list)
    for path in DOCS_ROOT.rglob("*"):
        if not path.is_file():
            continue
        canonical = path.relative_to(ROOT).as_posix()
        by_name[path.name].append(canonical)
    return dict(by_name)


def relative_link(from_canonical: str, to_canonical: str, fragment: str) -> str:
    from_parent = posixpath.dirname(from_canonical)
    rel = posixpath.relpath(to_canonical, from_parent or ".")
    return rel + fragment


def target_name(target: str) -> str:
    path_part, _fragment = split_fragment(target)
    path_part = normalize_posix(path_part)
    return PurePosixPath(path_part).name


def should_make_inert(target: str) -> bool:
    path_part, _fragment = split_fragment(target)
    lowered = path_part.lower().replace("\\", "/")
    if any(token in lowered for token in ["bc-core", "barecount-devhub", ".claude"]):
        return True
    if lowered.startswith("src/"):
        return True
    if re.search(r":\d+(?:-\d+)?$", path_part):
        return True
    return False


def resolve_target(target: str, by_name: dict[str, list[str]]) -> tuple[str, str] | None:
    path_part, fragment = split_fragment(target)
    name = target_name(path_part)
    alias = ALIASES.get(name)
    if alias:
        return alias, "alias"
    matches = by_name.get(name, [])
    if len(matches) == 1:
        return matches[0], "unique-basename"
    return None


def rewrite_text(
    canonical_path: str,
    text: str,
    wanted_targets: set[str],
    by_name: dict[str, list[str]],
) -> tuple[str, list[Repair], list[str]]:
    repairs: list[Repair] = []
    unresolved: list[str] = []

    def replace(match: re.Match[str]) -> str:
        prefix, label, raw_target, suffix = match.groups()
        target = clean_link(raw_target)
        if target not in wanted_targets:
            return match.group(0)
        if should_make_inert(target):
            replacement = code_text(label, target)
            repairs.append(Repair(canonical_path, target, replacement, "inert-provenance", label))
            return replacement
        resolved = resolve_target(target, by_name)
        if resolved is None:
            unresolved.append(target)
            return match.group(0)
        target_canonical, reason = resolved
        _path_part, fragment = split_fragment(target)
        new_target = relative_link(canonical_path, target_canonical, fragment)
        repairs.append(Repair(canonical_path, target, new_target, reason, label))
        return f"{prefix}{new_target}{suffix}"

    return LINK_RE.sub(replace, text), repairs, unresolved


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def write_report(
    dry_run: bool,
    run_id: int,
    repairs: list[Repair],
    unresolved: dict[str, list[str]],
    missing_files: list[str],
) -> None:
    by_reason = Counter(repair.reason for repair in repairs)
    by_doc = Counter(repair.canonical_path for repair in repairs)
    lines = [
        "# Missing Link Repair Report",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Dry run: `{dry_run}`",
        f"Audit run source: `{run_id}`",
        f"Repairs: `{len(repairs)}`",
        f"Files touched: `{len(by_doc)}`",
        f"Unresolved targets: `{sum(len(values) for values in unresolved.values())}`",
        f"Missing candidate files skipped: `{len(missing_files)}`",
        "",
        "## Reasons",
        "",
        "| Reason | Repairs |",
        "|---|---|",
    ]
    for reason, count in sorted(by_reason.items()):
        lines.append(f"| {markdown_escape(reason)} | {count} |")
    lines.extend(["", "## Files", "", "| File | Repairs |", "|---|---|"])
    for path, count in by_doc.most_common(80):
        lines.append(f"| {markdown_escape(path)} | {count} |")
    lines.extend(["", "## Sample Repairs", "", "| File | Old Target | New Target | Reason |", "|---|---|---|---|"])
    for repair in repairs[:140]:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(repair.canonical_path),
                    markdown_escape(repair.old_target),
                    markdown_escape(repair.new_target),
                    markdown_escape(repair.reason),
                ]
            )
            + " |"
        )
    if unresolved:
        lines.extend(["", "## Unresolved", "", "| File | Target |", "|---|---|"])
        for path, targets in sorted(unresolved.items()):
            for target in sorted(set(targets)):
                lines.append(f"| {markdown_escape(path)} | {markdown_escape(target)} |")
    if missing_files:
        lines.extend(["", "## Missing Candidate Files", ""])
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
        run_id = latest_audit_run(conn)
        targets_by_doc = missing_targets(conn, run_id)
    by_name = file_index()
    all_repairs: list[Repair] = []
    unresolved_by_doc: dict[str, list[str]] = {}
    missing_files: list[str] = []
    for canonical_path, wanted_targets in targets_by_doc.items():
        path = ROOT / canonical_path
        if not path.exists():
            missing_files.append(canonical_path)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        new_text, repairs, unresolved = rewrite_text(canonical_path, text, wanted_targets, by_name)
        if repairs and args.apply:
            path.write_text(new_text, encoding="utf-8", newline="\n")
        all_repairs.extend(repairs)
        if unresolved:
            unresolved_by_doc[canonical_path] = unresolved
    write_report(not args.apply, run_id, all_repairs, unresolved_by_doc, missing_files)
    print(
        "repairs="
        f"{len(all_repairs)} files={len(set(repair.canonical_path for repair in all_repairs))} "
        f"unresolved={sum(len(values) for values in unresolved_by_doc.values())} apply={args.apply}"
    )
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
