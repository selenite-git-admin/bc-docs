#!/usr/bin/env python3
"""Inventory legacy documentation roots before any safe-delete or physical removal."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTS_ROOT = ROOT.parent
SAFE_DELETE_ROOT = PROJECTS_ROOT / "bc-docs-safe-delete"
ARCHIVED_ROOT = PROJECTS_ROOT / "Archived"
REPORT_PATH = ROOT / "docs-control" / "reports" / "legacy-documentation-retirement-inventory.md"

CANDIDATE_NAMES = [
    "bc-docs",
    "bc-docs-site",
    "bc-docs-v2",
    "BareCount-Documentation",
    "BareCount-Intra-Site",
    "documentation.cxofacts",
    "platform-documentation",
]

ACTIVE_ROOTS = {
    "bc-docs-v3": "hold active v3 source; do not move, rename, or repoint while Claude sessions rely on it",
    "bc-docs-v4": "active isolated successor; no cutover rename until explicitly approved",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "node_modules",
    "site-packages",
}

DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".txt", ".html", ".htm"}


@dataclass(frozen=True)
class RootInventory:
    name: str
    path: Path
    state: str
    total_files: int
    doc_files: int
    markdown_files: int
    html_files: int
    total_bytes: int
    git_branch: str
    git_dirty_entries: int
    action: str


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_table(lines: list[str], headers: list[str], rows: list[tuple[object, ...]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        lines.append("| " + " | ".join(markdown_escape(value) for value in row) + " |")


def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def candidate_paths() -> list[tuple[str, Path, str]]:
    roots: list[tuple[str, Path, str]] = []
    for name, action in ACTIVE_ROOTS.items():
        path = PROJECTS_ROOT / name
        if path.exists():
            roots.append((name, path, action))
    for container in [PROJECTS_ROOT, SAFE_DELETE_ROOT, ARCHIVED_ROOT]:
        if not container.exists():
            continue
        for name in CANDIDATE_NAMES:
            path = container / name
            if path.exists():
                if container == SAFE_DELETE_ROOT:
                    action = "already staged in bc-docs-safe-delete; verify no live references before physical deletion"
                elif container == ARCHIVED_ROOT:
                    action = "archived legacy root; verify no live references before physical deletion"
                else:
                    action = "legacy root still outside safe-delete; move only after external reference scan"
                roots.append((name, path, action))
    return sorted(roots, key=lambda item: str(item[1]).lower())


def git_summary(path: Path) -> tuple[str, int]:
    git_dir = path / ".git"
    if not git_dir.exists():
        return "", 0
    try:
        branch = subprocess.run(
            ["git", "-C", str(path), "branch", "--show-current"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(path), "status", "--short"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.splitlines()
    except (OSError, subprocess.TimeoutExpired):
        return "git check failed", 0
    return branch, len([line for line in status if line.strip()])


def inventory_root(name: str, path: Path, action: str) -> RootInventory:
    total_files = 0
    doc_files = 0
    markdown_files = 0
    html_files = 0
    total_bytes = 0
    for current_root, dirs, files in os.walk(path):
        dirs[:] = [directory for directory in dirs if directory not in SKIP_DIRS]
        for filename in files:
            file_path = Path(current_root) / filename
            total_files += 1
            try:
                total_bytes += file_path.stat().st_size
            except OSError:
                pass
            suffix = file_path.suffix.lower()
            if suffix in DOC_EXTENSIONS:
                doc_files += 1
            if suffix in {".md", ".mdx"}:
                markdown_files += 1
            if suffix in {".html", ".htm"}:
                html_files += 1
    branch, dirty_entries = git_summary(path)
    if path == ROOT:
        state = "active_v4"
    elif path.name == "bc-docs-v3":
        state = "active_v3_hold"
    elif SAFE_DELETE_ROOT in path.parents:
        state = "staged_safe_delete"
    elif ARCHIVED_ROOT in path.parents:
        state = "archived"
    else:
        state = "top_level"
    return RootInventory(
        name=name,
        path=path,
        state=state,
        total_files=total_files,
        doc_files=doc_files,
        markdown_files=markdown_files,
        html_files=html_files,
        total_bytes=total_bytes,
        git_branch=branch,
        git_dirty_entries=dirty_entries,
        action=action,
    )


def main() -> None:
    inventories = [inventory_root(name, path, action) for name, path, action in candidate_paths()]
    lines = [
        "# Legacy Documentation Retirement Inventory",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Safety Boundary",
        "",
        "- Inventory only; this report does not move, delete, rename, or repoint any root.",
        "- `bc-docs-v3` remains an active hold while Claude sessions rely on it.",
        "- Roots already under `bc-docs-safe-delete` stay staged until the user approves physical deletion.",
        "- Before deletion, run the cutover-reference plan and an external reference scan across repos, MCP configs, and Claude-facing files.",
        "",
        "## Roots",
        "",
    ]
    write_table(
        lines,
        [
            "Name",
            "State",
            "Path",
            "Files",
            "Doc Files",
            "Markdown",
            "HTML",
            "Size",
            "Git Branch",
            "Dirty Entries",
            "Recommended Action",
        ],
        [
            (
                item.name,
                item.state,
                item.path,
                item.total_files,
                item.doc_files,
                item.markdown_files,
                item.html_files,
                format_bytes(item.total_bytes),
                item.git_branch or "",
                item.git_dirty_entries,
                item.action,
            )
            for item in inventories
        ],
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
