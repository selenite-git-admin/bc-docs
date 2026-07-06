#!/usr/bin/env python3
"""Generate the bc-docs-v3 -> bc-docs cutover replacement queue."""
from __future__ import annotations

import argparse
import csv
import os
import re
import sqlite3
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTS_ROOT = ROOT.parent
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "cutover-replacement-queue.md"
CSV_PATH = ROOT / "docs-control" / "reports" / "cutover-replacement-queue.csv"

TOKEN_PATTERNS = [
    (re.compile(r"C:\\MyProjects\\bc-docs-v3", flags=re.IGNORECASE), r"C:\MyProjects\bc-docs"),
    (re.compile(r"C:/MyProjects/bc-docs-v3", flags=re.IGNORECASE), "C:/MyProjects/bc-docs"),
    (re.compile(r"\bbc-docs-v3\b", flags=re.IGNORECASE), "bc-docs"),
]
TOKEN_RE = re.compile("|".join(pattern.pattern for pattern, _ in TOKEN_PATTERNS), flags=re.IGNORECASE)

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

SERVED_COPY_DIRS = {"private-docs"}

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

MAX_FILE_BYTES = 1_000_000


@dataclass(frozen=True)
class QueueRow:
    scope: str
    repo: str
    path: str
    line_number: int
    action: str
    token: str
    replacement: str
    reference_class: str
    reason: str
    excerpt: str
    replacement_preview: str


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_table(lines: list[str], headers: list[str], rows: list[tuple[object, ...]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        lines.append("| " + " | ".join(markdown_escape(value) for value in row) + " |")


def clip(value: str, limit: int = 220) -> str:
    value = " ".join(value.strip().split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def replacement_for(token: str) -> str:
    for pattern, replacement in TOKEN_PATTERNS:
        if pattern.fullmatch(token):
            return replacement
    if "\\" in token:
        return token.replace("bc-docs-v3", "bc-docs")
    return "bc-docs"


def replace_line(line: str) -> str:
    replaced = line
    for pattern, replacement in TOKEN_PATTERNS:
        replaced = pattern.sub(lambda _match, value=replacement: value, replaced)
    return replaced


def reference_class(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    if ".claude" in parts or name == "claude.md":
        return "claude_handoff_or_memory"
    if parts.intersection(SERVED_COPY_DIRS):
        return "served_docs_copy"
    if parts.intersection({"docs", "documentation", "reports"}):
        return "documentation_or_report"
    if path.suffix.lower() in {".sql", ".ts", ".tsx", ".js", ".jsx", ".json", ".yaml", ".yml", ".toml", ".ps1", ".py", ".md"}:
        return "code_or_config"
    return "other"


def historical_context(line: str, path: str) -> bool:
    lowered = line.lower()
    path_lower = path.lower()
    markers = [
        "adr:",
        "bc-docs-v3 main",
        "build plan:",
        "commit ",
        "design:",
        "merged at",
        "preflight:",
        "pr #",
        "authority:",
        "dbcp:",
        "revision:",
        "closeout",
        "evidence",
        "superseded",
        "historical",
    ]
    if any(marker in lowered for marker in markers):
        return True
    return any(
        part in path_lower
        for part in [
            "/archive/",
            "\\archive\\",
            "/audit-output",
            "\\audit-output",
            "/evidence/",
            "\\evidence\\",
            "/adrs/",
            "\\adrs\\",
        ]
    )


def operational_pointer_context(line: str) -> bool:
    lowered = line.lower()
    markers = [
        "c:/myprojects/bc-docs-v3",
        r"c:\myprojects\bc-docs-v3",
        "bc_docs_path",
        "bc_docs_root",
        "v3_docs_root",
        "v3_root",
        "docsroot",
        "docs root",
        "source path",
        "ssot",
        "single root",
        "docs registry",
        "document index",
        "auto-generates",
        "auto-generate",
        "read from bc-docs-v3",
        "reads bc-docs-v3",
        "scan bc-docs-v3",
        "rescan bc-docs-v3",
    ]
    return any(marker in lowered for marker in markers)


def classify_internal(row: sqlite3.Row, line: str) -> tuple[str, str]:
    path = str(row["canonical_path"])
    document_kind = str(row["document_kind"])
    visibility = str(row["reader_visibility"])
    current_truth = int(row["current_truth"] or 0)
    if historical_context(line, path) or document_kind.startswith("evidence_") or document_kind == "adr":
        return "preserve_historical_provenance", "Historical decision/evidence provenance; do not blind replace."
    if current_truth == 1 and visibility in {"primary", "reference", "governance"}:
        return "replace_after_cutover", "Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs."
    if visibility in {"primary", "reference", "governance"}:
        return "manual_review", "Reader-visible but not marked current truth; review before repointing."
    return "preserve_historical_provenance", "Hidden/evidence/archive reference; preserve unless it is proven operational."


def classify_external(repo: str, path: Path, line: str, ref_class: str) -> tuple[str, str]:
    rel = path.relative_to(PROJECTS_ROOT).as_posix()
    lowered = line.lower()
    if ref_class == "served_docs_copy":
        return "regenerate_served_doc_copy", "Generated served documentation copy; rebuild from the cutover docs root instead of hand editing."
    if ref_class == "claude_handoff_or_memory":
        return "defer_claude_ecosystem", "Claude-facing instruction or memory; replace only after active Claude sessions are stopped."
    if repo == "barecount-devhub" and operational_pointer_context(line):
        return "replace_after_cutover", "DevHub operational docs-root reference; repoint during the approved cutover window."
    if any(name in rel.lower() for name in ["claude.md", ".claude/"]):
        return "defer_claude_ecosystem", "Claude-facing instruction or handoff; replace only during the Claude cutover window."
    if historical_context(line, rel):
        return "preserve_historical_provenance", "Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer."
    if ref_class == "code_or_config" and operational_pointer_context(line):
        return "replace_after_cutover", "Operational docs-root pointer; candidate for direct repoint during cutover."
    if ref_class == "code_or_config":
        return "manual_review", "Code/config comment or reference; review whether it is live guidance or historical provenance."
    if ref_class == "documentation_or_report":
        return "manual_review", "Documentation/report reference outside v4; review whether it is live guidance or history."
    return "manual_review", "Unclassified external reference; review before editing."


def target_doc_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT canonical_path, document_kind, reader_visibility, current_truth
        FROM target_documents
        ORDER BY canonical_path
        """
    ).fetchall()


def scan_internal_docs(conn: sqlite3.Connection) -> list[QueueRow]:
    rows: list[QueueRow] = []
    for doc in target_doc_rows(conn):
        path = ROOT / str(doc["canonical_path"])
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            for match in TOKEN_RE.finditer(line):
                token = match.group(0)
                action, reason = classify_internal(doc, line)
                rows.append(
                    QueueRow(
                        scope="internal_v4",
                        repo="bc-docs-v4",
                        path=str(doc["canonical_path"]),
                        line_number=line_number,
                        action=action,
                        token=token,
                        replacement=replacement_for(token),
                        reference_class=str(doc["document_kind"]),
                        reason=reason,
                        excerpt=clip(line),
                        replacement_preview=clip(replace_line(line)),
                    )
                )
    return rows


def scan_roots() -> list[Path]:
    return [
        path
        for path in sorted(PROJECTS_ROOT.iterdir(), key=lambda item: item.name.lower())
        if path.is_dir() and path.name in INCLUDED_TOP_LEVEL and path.name not in EXCLUDED_TOP_LEVEL
    ]


def iter_text_files(root: Path, include_served_copies: bool):
    skip_dirs = set(SKIP_DIRS)
    if not include_served_copies:
        skip_dirs.update(SERVED_COPY_DIRS)
    if (root / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "-C", str(root), "ls-files"],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            result = None
        if result and result.returncode == 0:
            for rel in result.stdout.splitlines():
                path = root / rel
                rel_parts = Path(rel).parts
                if any(part in skip_dirs for part in rel_parts):
                    continue
                if path.suffix.lower() in SKIP_EXTENSIONS:
                    continue
                try:
                    if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
                        continue
                except OSError:
                    continue
                yield path
            return
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [directory for directory in dirs if directory not in skip_dirs]
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


def scan_external_refs(include_served_copies: bool) -> list[QueueRow]:
    rows: list[QueueRow] = []
    for root in scan_roots():
        repo = root.name
        for path in iter_text_files(root, include_served_copies):
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            ref_class = reference_class(path)
            rel_path = path.relative_to(PROJECTS_ROOT)
            for line_number, line in enumerate(lines, start=1):
                for match in TOKEN_RE.finditer(line):
                    token = match.group(0)
                    action, reason = classify_external(repo, path, line, ref_class)
                    rows.append(
                        QueueRow(
                            scope="external_repo",
                            repo=repo,
                            path=rel_path.as_posix(),
                            line_number=line_number,
                            action=action,
                            token=token,
                            replacement=replacement_for(token),
                            reference_class=ref_class,
                            reason=reason,
                            excerpt=clip(line),
                            replacement_preview=clip(replace_line(line)),
                        )
                    )
    return rows


def write_csv(rows: list[QueueRow]) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "scope",
                "repo",
                "path",
                "line",
                "action",
                "token",
                "replacement",
                "reference_class",
                "reason",
                "excerpt",
                "replacement_preview",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.scope,
                    row.repo,
                    row.path,
                    row.line_number,
                    row.action,
                    row.token,
                    row.replacement,
                    row.reference_class,
                    row.reason,
                    row.excerpt,
                    row.replacement_preview,
                ]
            )


def write_report(rows: list[QueueRow], include_served_copies: bool) -> None:
    action_counts = Counter(row.action for row in rows)
    scope_counts = Counter((row.scope, row.action) for row in rows)
    repo_counts = Counter((row.repo, row.action) for row in rows if row.scope == "external_repo")
    ready_rows = [row for row in rows if row.action == "replace_after_cutover"]
    claude_rows = [row for row in rows if row.action == "defer_claude_ecosystem"]
    manual_rows = [row for row in rows if row.action == "manual_review"]
    historical_rows = [row for row in rows if row.action == "preserve_historical_provenance"]

    lines = [
        "# Cutover Replacement Queue",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Rows: `{len(rows)}`",
        f"CSV: `{CSV_PATH.relative_to(ROOT)}`",
        "",
        "## Safety Boundary",
        "",
        "- This is a queue only; it does not edit, rename, delete, or repoint anything.",
        "- Do not execute replacements while active Claude sessions still depend on `bc-docs-v3`.",
        "- Do not rename `bc-docs-v4` to `bc-docs` until the cutover window is explicitly approved.",
        "- Historical provenance rows are intentionally separated from replacement candidates.",
        f"- Served documentation copies are {'included' if include_served_copies else 'excluded'}; when excluded, rebuild served copies from the cutover docs root instead of hand-editing them.",
        "",
        "## Action Summary",
        "",
    ]
    write_table(lines, ["Action", "Rows"], action_counts.most_common())
    lines.extend(["", "## Scope Summary", ""])
    write_table(lines, ["Scope", "Action", "Rows"], [(scope, action, count) for (scope, action), count in sorted(scope_counts.items())])
    lines.extend(["", "## External Repo Summary", ""])
    write_table(lines, ["Repo", "Action", "Rows"], [(repo, action, count) for (repo, action), count in sorted(repo_counts.items())])

    lines.extend(
        [
            "",
            "## Ready Replace Candidates",
            "",
            "These rows are candidates for direct `bc-docs-v3` -> `bc-docs` replacement during the approved cutover window.",
            "",
        ]
    )
    write_table(
        lines,
        ["Scope", "Repo", "Path", "Line", "Token", "Replacement", "Reason"],
        [(row.scope, row.repo, row.path, row.line_number, row.token, row.replacement, row.reason) for row in ready_rows[:200]],
    )
    if len(ready_rows) > 200:
        lines.append("")
        lines.append(f"Ready replace table truncated to 200 rows; full queue is in `{CSV_PATH.relative_to(ROOT)}`.")

    lines.extend(["", "## Claude Ecosystem Hold", ""])
    write_table(
        lines,
        ["Repo", "Path", "Line", "Token", "Replacement"],
        [(row.repo, row.path, row.line_number, row.token, row.replacement) for row in claude_rows[:120]],
    )
    if len(claude_rows) > 120:
        lines.append("")
        lines.append(f"Claude hold table truncated to 120 rows; full queue is in `{CSV_PATH.relative_to(ROOT)}`.")

    lines.extend(["", "## Manual Review Samples", ""])
    write_table(
        lines,
        ["Scope", "Repo", "Path", "Line", "Reason", "Excerpt"],
        [(row.scope, row.repo, row.path, row.line_number, row.reason, row.excerpt) for row in manual_rows[:80]],
    )
    if len(manual_rows) > 80:
        lines.append("")
        lines.append(f"Manual review table truncated to 80 rows; full queue is in `{CSV_PATH.relative_to(ROOT)}`.")

    lines.extend(["", "## Historical Provenance Samples", ""])
    write_table(
        lines,
        ["Scope", "Repo", "Path", "Line", "Reason", "Excerpt"],
        [(row.scope, row.repo, row.path, row.line_number, row.reason, row.excerpt) for row in historical_rows[:80]],
    )
    if len(historical_rows) > 80:
        lines.append("")
        lines.append(f"Historical provenance table truncated to 80 rows; full queue is in `{CSV_PATH.relative_to(ROOT)}`.")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-served-copies", action="store_true", help="include generated/private served-doc copies")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = scan_internal_docs(conn)
    rows.extend(scan_external_refs(args.include_served_copies))
    rows.sort(key=lambda row: (row.action, row.scope, row.repo, row.path, row.line_number, row.token.lower()))
    write_csv(rows)
    write_report(rows, args.include_served_copies)
    print(f"rows={len(rows)}")
    print(f"wrote {REPORT_PATH}")
    print(f"wrote {CSV_PATH}")


if __name__ == "__main__":
    main()
