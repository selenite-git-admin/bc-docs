#!/usr/bin/env python3
"""Scan project repositories for legacy documentation-root references."""
from __future__ import annotations

import os
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTS_ROOT = ROOT.parent
REPORT_PATH = ROOT / "docs-control" / "reports" / "external-legacy-reference-scan.md"

TOKENS = [
    "BareCount-Documentation",
    "BareCount-Intra-Site",
    "bc-docs-safe-delete",
    "bc-docs-site",
    "bc-docs-v2",
    "bc-docs-v3",
    "documentation.cxofacts",
    "platform-documentation",
]

INCLUDED_TOP_LEVEL = {
    "BareCount-Customer-Portal",
    "barecount-devhub",
    "bc-admin",
    "bc-ai",
    "bc-core",
    "bc-core-dashboard",
    "bc-core-runtime",
    "bc-pg-mcp",
    "bc-portal",
    "bc-qa",
    "bc-sdg",
    "bc-seed",
    "bc-website",
    "github-mcp",
    "platform-infra-stack",
    "Web-BareCount",
}

EXCLUDED_TOP_LEVEL = {
    "Archived",
    "bc-docs-safe-delete",
    "bc-docs-v3",
    "bc-docs-v4",
}

SKIP_DIRS = {
    ".angular",
    ".cache",
    ".git",
    ".gradle",
    ".hg",
    ".next",
    ".svn",
    ".turbo",
    ".venv",
    "__pycache__",
    "coverage",
    "data",
    "dist",
    "build",
    "logs",
    "node_modules",
    "out",
    "target",
    "tmp",
    "uploads",
    "venv",
}

SKIP_EXTENSIONS = {
    ".7z",
    ".bin",
    ".bmp",
    ".class",
    ".dll",
    ".exe",
    ".gif",
    ".ico",
    ".jar",
    ".jpg",
    ".jpeg",
    ".lock",
    ".mp4",
    ".pdf",
    ".png",
    ".pyc",
    ".sqlite",
    ".zip",
}

TOKEN_RE = re.compile("|".join(re.escape(token) for token in TOKENS), flags=re.IGNORECASE)
MAX_FILE_BYTES = 1_000_000


@dataclass(frozen=True)
class MatchRow:
    repo: str
    path: Path
    line_number: int
    token: str
    reference_class: str
    excerpt: str


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_table(lines: list[str], headers: list[str], rows: list[tuple[object, ...]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        lines.append("| " + " | ".join(markdown_escape(value) for value in row) + " |")


def clip(value: str, limit: int = 180) -> str:
    value = " ".join(value.strip().split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def reference_class(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    if ".claude" in parts or name == "claude.md":
        return "claude_handoff_or_memory"
    if "private-docs" in parts:
        return "served_docs_copy"
    if parts.intersection({"docs", "documentation", "reports"}):
        return "documentation_or_report"
    if path.suffix.lower() in {".sql", ".ts", ".tsx", ".js", ".jsx", ".json", ".yaml", ".yml", ".toml", ".ps1", ".py", ".md"}:
        return "code_or_config"
    return "other"


def scan_roots() -> list[Path]:
    return [
        path
        for path in sorted(PROJECTS_ROOT.iterdir(), key=lambda item: item.name.lower())
        if path.is_dir() and path.name in INCLUDED_TOP_LEVEL and path.name not in EXCLUDED_TOP_LEVEL
    ]


def iter_text_files(root: Path):
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [directory for directory in dirs if directory not in SKIP_DIRS]
        for filename in files:
            path = Path(current_root) / filename
            if path.suffix.lower() in SKIP_EXTENSIONS:
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield path


def scan_file(repo: str, path: Path) -> list[MatchRow]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    rows: list[MatchRow] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in TOKEN_RE.finditer(line):
            rows.append(MatchRow(repo, path, line_number, match.group(0), reference_class(path), clip(line)))
    return rows


def main() -> None:
    matches: list[MatchRow] = []
    for root in scan_roots():
        for path in iter_text_files(root):
            matches.extend(scan_file(root.name, path))

    repo_counts = Counter(row.repo for row in matches)
    token_counts = Counter(row.token.lower() for row in matches)
    class_counts = Counter(row.reference_class for row in matches)
    operational_rows = [row for row in matches if row.reference_class == "code_or_config"]
    lines = [
        "# External Legacy Reference Scan",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Scan root: `{PROJECTS_ROOT}`",
        f"Matches: `{len(matches)}`",
        "",
        "## Safety Boundary",
        "",
        "- Scan only; this report does not edit, move, delete, or repoint files.",
        "- Scans BareCount/MCP-relevant project repos only; excludes `bc-docs-v3`, `bc-docs-v4`, `bc-docs-safe-delete`, and `Archived`.",
        "- Claude/Codex user-profile and MCP config scans are deferred until the user approves the cutover window.",
        "",
        "## Summary By Repo",
        "",
    ]
    write_table(lines, ["Repo", "Matches"], repo_counts.most_common())
    lines.extend(["", "## Summary By Token", ""])
    write_table(lines, ["Token", "Matches"], token_counts.most_common())
    lines.extend(["", "## Summary By Reference Class", ""])
    write_table(lines, ["Reference Class", "Matches"], class_counts.most_common())
    lines.extend(
        [
            "",
            "## Code Or Config References",
            "",
            "These are the first external references to review during cutover because they may affect runtime tools, scripts, schema comments, or repo guidance.",
            "",
        ]
    )
    write_table(
        lines,
        ["Repo", "Path", "Line", "Token", "Excerpt"],
        [
            (
                row.repo,
                row.path.relative_to(PROJECTS_ROOT),
                row.line_number,
                row.token,
                row.excerpt,
            )
            for row in operational_rows
        ],
    )
    lines.extend(["", "## Matches", ""])
    write_table(
        lines,
        ["Repo", "Path", "Line", "Token", "Reference Class", "Excerpt"],
        [
            (
                row.repo,
                row.path.relative_to(PROJECTS_ROOT),
                row.line_number,
                row.token,
                row.reference_class,
                row.excerpt,
            )
            for row in matches
        ],
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"matches={len(matches)}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
