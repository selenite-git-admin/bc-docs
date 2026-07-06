#!/usr/bin/env python3
"""Write a line-level review report for mutable claims in current/reference docs."""
from __future__ import annotations

import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "mutable-claim-review.md"

TEMPORAL_CLAIM_RE = re.compile(r"(?i)\b(as of|current as of|currently|today|latest|now)\b")
ISO_DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
PERCENT_RE = re.compile(r"\b\d+(?:\.\d+)?\s?%")
BIG_NUMBER_RE = re.compile(r"\b\d{1,3}(?:,\d{3})+\b")
UNIT_STAT_RE = re.compile(
    r"(?i)\b\d+(?:\.\d+)?\s?(ms|sec|secs|seconds|minutes|gb|mb|rows|records|controllers|tables|files|documents)\b"
)
LINK_TARGET_RE = re.compile(r"\]\([^)]*\)")
BARE_URL_RE = re.compile(r"https?://\S+")
INLINE_CODE_RE = re.compile(r"`[^`]*`")

CURRENT_DOC_KINDS = {"current_chapter", "source_system_reference", "curated_reference"}
FRONTMATTER_PROVENANCE_KEYS = {
    "audit_pointer",
    "date",
    "last_verified_at",
    "pre_doctrine_decisions",
    "ratification",
}
CHECKS = [
    ("temporal-claim", TEMPORAL_CLAIM_RE, "Replace time-relative wording with versioned provenance or stable doctrine."),
    ("iso-date-claim", ISO_DATE_RE, "Keep only provenance, decision, ratification, or version-marker dates."),
    ("percentage-stat", PERCENT_RE, "Remove volatile percentages unless source-derived and regenerated."),
    ("large-number-stat", BIG_NUMBER_RE, "Remove volatile large counts unless source-derived and regenerated."),
    ("unit-stat", UNIT_STAT_RE, "Remove volatile operational statistics unless source-derived and regenerated."),
]


@dataclass(frozen=True)
class MutableRow:
    canonical_path: str
    document_kind: str
    section: str
    line_number: int
    category: str
    matches: str
    line_excerpt: str
    action: str


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def clip(value: str, limit: int = 220) -> str:
    value = " ".join(value.strip().split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def claim_scan_text(text: str) -> str:
    text = LINK_TARGET_RE.sub("]", text)
    text = BARE_URL_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def is_frontmatter_provenance(line: str, category: str) -> bool:
    if category != "iso-date-claim":
        return False
    stripped = line.strip()
    key = stripped.split(":", 1)[0].strip()
    return key in FRONTMATTER_PROVENANCE_KEYS


def target_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT canonical_path, document_kind
        FROM target_documents
        WHERE current_truth = 1
          AND document_kind IN ('current_chapter', 'source_system_reference', 'curated_reference')
        ORDER BY canonical_path
        """
    ).fetchall()


def line_sections(lines: list[str]) -> list[str]:
    sections: list[str] = []
    in_frontmatter = False
    in_code = False
    frontmatter_seen = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if index == 0 and stripped == "---":
            in_frontmatter = True
            frontmatter_seen = True
            sections.append("frontmatter")
            continue
        if in_frontmatter:
            sections.append("frontmatter")
            if stripped == "---":
                in_frontmatter = False
            continue
        if stripped.startswith("```"):
            sections.append("code")
            in_code = not in_code
            continue
        if in_code:
            sections.append("code")
            continue
        sections.append("body" if frontmatter_seen else "body")
    return sections


def collect_rows(conn: sqlite3.Connection) -> list[MutableRow]:
    rows: list[MutableRow] = []
    for row in target_rows(conn):
        canonical_path = row["canonical_path"]
        path = ROOT / canonical_path
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        sections = line_sections(lines)
        for line_number, (line, section) in enumerate(zip(lines, sections), start=1):
            if section == "code":
                continue
            scan_line = claim_scan_text(line)
            for category, regex, action in CHECKS:
                matches = [match.group(0) for match in regex.finditer(scan_line)]
                if not matches:
                    continue
                if section == "frontmatter" and is_frontmatter_provenance(line, category):
                    continue
                rows.append(
                    MutableRow(
                        canonical_path=canonical_path,
                        document_kind=row["document_kind"],
                        section=section,
                        line_number=line_number,
                        category=category,
                        matches=", ".join(sorted(set(matches))),
                        line_excerpt=clip(line),
                        action=action,
                    )
                )
    return rows


def write_table(lines: list[str], headers: list[str], rows: list[tuple[object, ...]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        lines.append("| " + " | ".join(markdown_escape(value) for value in row) + " |")


def write_report(rows: list[MutableRow]) -> None:
    category_counts = Counter(row.category for row in rows)
    section_counts = Counter(row.section for row in rows)
    body_doc_counts = Counter(row.canonical_path for row in rows if row.section == "body")
    frontmatter_doc_counts = Counter(row.canonical_path for row in rows if row.section == "frontmatter")

    lines = [
        "# Mutable Claim Review",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Line findings: `{len(rows)}`",
        "",
        "This report is line-level review material for the aggregate mutable-claim audit.",
        "Frontmatter provenance dates in approved metadata fields are allowlisted; body rows are the primary cleanup queue.",
        "",
        "## Summary By Category",
        "",
    ]
    write_table(lines, ["Category", "Line Findings"], sorted(category_counts.items()))
    lines.extend(["", "## Summary By Section", ""])
    write_table(lines, ["Section", "Line Findings"], sorted(section_counts.items()))
    lines.extend(["", "## Top Body Documents", ""])
    write_table(lines, ["Document", "Body Findings"], body_doc_counts.most_common(30))
    lines.extend(["", "## Top Frontmatter Documents", ""])
    write_table(lines, ["Document", "Frontmatter Findings"], frontmatter_doc_counts.most_common(20))

    for section in ["body", "frontmatter"]:
        lines.extend(["", f"## {section.title()} Findings", ""])
        section_rows = [
            (
                row.canonical_path,
                row.line_number,
                row.category,
                row.matches,
                row.line_excerpt,
                row.action,
            )
            for row in rows
            if row.section == section
        ]
        write_table(lines, ["Document", "Line", "Category", "Matches", "Excerpt", "Suggested Action"], section_rows)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = collect_rows(conn)
    write_report(rows)
    print(f"mutable claim lines={len(rows)}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
