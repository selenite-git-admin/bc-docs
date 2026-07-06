#!/usr/bin/env python3
"""Inventory bc-core coverage targets and rough documentation links."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "bc-core-coverage.md"
DEFAULT_CORE_ROOT = Path("C:/MyProjects/bc-core")

EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".claude",
    ".idea",
    "node_modules",
    "dist",
    "tmp",
    "var",
    "_archives",
    "private-docs",
}

CLASS_RE = re.compile(r"\bexport\s+class\s+([A-Za-z0-9_]+)")


def within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_id(conn: sqlite3.Connection, core_root: Path) -> int:
    row = conn.execute("SELECT repo_id FROM repositories WHERE repo_key = 'bc-core'").fetchone()
    if row:
        conn.execute(
            "UPDATE repositories SET root_path = ?, role = 'codebase', active_for_cutover = 1 WHERE repo_key = 'bc-core'",
            (str(core_root),),
        )
        return int(row[0])
    cursor = conn.execute(
        """
        INSERT INTO repositories(repo_key, repo_name, root_path, role, active_for_cutover, notes)
        VALUES ('bc-core', 'bc-core', ?, 'codebase', 1, 'Primary backend/codebase coverage source')
        """,
        (str(core_root),),
    )
    return int(cursor.lastrowid)


def start_run(conn: sqlite3.Connection, repo_id_value: int) -> int:
    cursor = conn.execute(
        """
        INSERT INTO inventory_runs(run_kind, source_repo_id, tool_name, tool_version, status)
        VALUES ('coverage_inventory', ?, 'inventory_bc_core.py', '0.1.0', 'running')
        """,
        (repo_id_value,),
    )
    return int(cursor.lastrowid)


def finish_run(conn: sqlite3.Connection, run_id: int, status: str, summary: dict[str, object], error: str | None = None) -> None:
    conn.execute(
        """
        UPDATE inventory_runs
        SET completed_at = CURRENT_TIMESTAMP,
            status = ?,
            summary_json = ?,
            error_text = ?
        WHERE run_id = ?
        """,
        (status, json.dumps(summary, sort_keys=True), error, run_id),
    )


def should_skip(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    return any(part in EXCLUDED_DIRS for part in rel_parts)


def class_identifier(path: Path, target_type: str) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except UnicodeDecodeError:
        return None
    matches = CLASS_RE.findall(text)
    if not matches:
        return None
    preferred_suffix = {
        "controller": "Controller",
        "service": "Service",
        "module": "Module",
    }.get(target_type)
    if preferred_suffix:
        for name in matches:
            if name.endswith(preferred_suffix):
                return name
    return matches[-1]


def add_candidate(candidates: dict[str, tuple[str, Path]], target_type: str, path: Path, root: Path) -> None:
    if should_skip(path, root):
        return
    if path.name.endswith(".spec.ts") or path.name.endswith(".test.ts"):
        return
    rel = path.relative_to(root).as_posix()
    candidates[rel] = (target_type, path)


def collect_targets(core_root: Path) -> dict[str, tuple[str, Path]]:
    candidates: dict[str, tuple[str, Path]] = {}
    for path in (core_root / "src").glob("**/*.controller.ts"):
        add_candidate(candidates, "controller", path, core_root)
    for path in (core_root / "src").glob("**/*.service.ts"):
        add_candidate(candidates, "service", path, core_root)
    for path in (core_root / "src").glob("**/*.module.ts"):
        add_candidate(candidates, "module", path, core_root)
    schema_root = core_root / "src" / "database" / "schema"
    if schema_root.exists():
        for path in schema_root.glob("**/*.ts"):
            add_candidate(candidates, "schema", path, core_root)
    scripts_root = core_root / "scripts"
    if scripts_root.exists():
        for ext in ("*.mjs", "*.js", "*.ts", "*.sql"):
            for path in scripts_root.glob(f"**/{ext}"):
                if "audit-output" in path.relative_to(core_root).parts:
                    continue
                add_candidate(candidates, "script", path, core_root)
    redesign_root = core_root / "docker" / "redesign"
    if redesign_root.exists():
        for path in redesign_root.glob("**/*.sql"):
            add_candidate(candidates, "script", path, core_root)
    for file_name in (
        "package.json",
        "docker-compose.yml",
        "tsconfig.json",
        "tsconfig.build.json",
        "tsconfig.tools.json",
        "vitest.config.ts",
        "vitest.config.e2e.ts",
    ):
        path = core_root / file_name
        if path.exists():
            add_candidate(candidates, "config", path, core_root)
    return candidates


def upsert_coverage_targets(
    conn: sqlite3.Connection,
    repo_key: str,
    candidates: dict[str, tuple[str, Path]],
) -> dict[str, int]:
    ids: dict[str, int] = {}
    for rel_path, (target_type, path) in sorted(candidates.items()):
        identifier = class_identifier(path, target_type) if path.suffix == ".ts" else None
        fingerprint = sha256(path)
        conn.execute(
            """
            INSERT INTO coverage_targets(repo_key, target_type, target_path, identifier, fingerprint)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(repo_key, target_type, target_path, COALESCE(identifier, '')) DO UPDATE SET
              fingerprint = excluded.fingerprint,
              last_seen_at = CURRENT_TIMESTAMP
            """,
            (repo_key, target_type, rel_path, identifier, fingerprint),
        )
        row = conn.execute(
            """
            SELECT coverage_target_id
            FROM coverage_targets
            WHERE repo_key = ?
              AND target_type = ?
              AND target_path = ?
              AND COALESCE(identifier, '') = COALESCE(?, '')
            """,
            (repo_key, target_type, rel_path, identifier),
        ).fetchone()
        ids[rel_path] = int(row[0])
    return ids


def target_documents(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT target_doc_id, canonical_path, document_kind, reader_visibility, current_truth
        FROM target_documents
        WHERE document_kind IN (
          'current_chapter',
          'generated_reference',
          'source_system_reference',
          'curated_reference',
          'adr',
          'errata'
        )
        ORDER BY canonical_path
        """
    ).fetchall()


def doc_text(row: sqlite3.Row) -> str:
    path = ROOT / row["canonical_path"]
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def clear_existing_links(conn: sqlite3.Connection, repo_key: str) -> None:
    conn.execute(
        """
        DELETE FROM coverage_links
        WHERE coverage_target_id IN (
          SELECT coverage_target_id FROM coverage_targets WHERE repo_key = ?
        )
        """,
        (repo_key,),
    )


def reset_existing_coverage(conn: sqlite3.Connection, repo_key: str) -> None:
    clear_existing_links(conn, repo_key)
    conn.execute("DELETE FROM coverage_targets WHERE repo_key = ?", (repo_key,))


def link_docs_to_targets(
    conn: sqlite3.Connection,
    coverage_ids: dict[str, int],
    candidates: dict[str, tuple[str, Path]],
) -> Counter[str]:
    counts: Counter[str] = Counter()
    docs = [(row, doc_text(row)) for row in target_documents(conn)]
    for rel_path, (target_type, path) in sorted(candidates.items()):
        coverage_id = coverage_ids[rel_path]
        slash_path = rel_path.replace("\\", "/")
        backslash_path = rel_path.replace("/", "\\")
        basename = path.name
        stem = path.stem
        for doc_row, text in docs:
            if not text:
                continue
            relation = None
            confidence = None
            if slash_path in text or backslash_path in text:
                relation = "documents"
                confidence = "high"
            elif basename not in {"index.ts", "README.md"} and basename in text:
                relation = "mentions"
                confidence = "medium"
            elif target_type in {"controller", "service", "module"} and len(stem) > 12 and stem in text:
                relation = "mentions"
                confidence = "low"
            if not relation:
                continue
            conn.execute(
                """
                INSERT INTO coverage_links(
                  target_doc_id,
                  coverage_target_id,
                  relation_type,
                  confidence,
                  notes
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    int(doc_row["target_doc_id"]),
                    coverage_id,
                    relation,
                    confidence,
                    "rough text/path match from inventory_bc_core.py",
                ),
            )
            counts[f"{relation}:{confidence}"] += 1
    return counts


def write_report(conn: sqlite3.Connection, run_id: int, counts: Counter[str]) -> None:
    lines = [
        "# bc-core Coverage Inventory",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Coverage run: `{run_id}`",
        "",
        "## Coverage Targets",
        "",
        "| Target Type | Targets | With Links | Without Links |",
        "|---|---|---|---|",
    ]
    rows = conn.execute(
        """
        SELECT
          ct.target_type,
          COUNT(DISTINCT ct.coverage_target_id) AS target_count,
          COUNT(DISTINCT cl.coverage_target_id) AS linked_count
        FROM coverage_targets ct
        LEFT JOIN coverage_links cl ON cl.coverage_target_id = ct.coverage_target_id
        WHERE ct.repo_key = 'bc-core'
        GROUP BY ct.target_type
        ORDER BY ct.target_type
        """
    ).fetchall()
    for target_type, target_count, linked_count in rows:
        lines.append(f"| {target_type} | {target_count} | {linked_count} | {target_count - linked_count} |")
    lines.extend(["", "## Link Match Counts", "", "| Match | Links |", "|---|---|"])
    for key, count in sorted(counts.items()):
        lines.append(f"| {key} | {count} |")
    lines.extend(["", "## Unlinked Controllers", "", "| Path | Identifier |", "|---|---|"])
    for row in conn.execute(
        """
        SELECT ct.target_path, COALESCE(ct.identifier, '')
        FROM coverage_targets ct
        LEFT JOIN coverage_links cl ON cl.coverage_target_id = ct.coverage_target_id
        WHERE ct.repo_key = 'bc-core'
          AND ct.target_type = 'controller'
          AND cl.coverage_link_id IS NULL
        ORDER BY ct.target_path
        LIMIT 80
        """
    ):
        lines.append(f"| {row[0]} | {row[1]} |")
    lines.extend(["", "## Unlinked Schema Files", "", "| Path | Identifier |", "|---|---|"])
    for row in conn.execute(
        """
        SELECT ct.target_path, COALESCE(ct.identifier, '')
        FROM coverage_targets ct
        LEFT JOIN coverage_links cl ON cl.coverage_target_id = ct.coverage_target_id
        WHERE ct.repo_key = 'bc-core'
          AND ct.target_type = 'schema'
          AND cl.coverage_link_id IS NULL
        ORDER BY ct.target_path
        LIMIT 80
        """
    ):
        lines.append(f"| {row[0]} | {row[1]} |")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-root", type=Path, default=DEFAULT_CORE_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    core_root = args.core_root.resolve()
    if not core_root.exists():
        raise SystemExit(f"bc-core root not found: {core_root}")
    if not within(core_root, core_root):
        raise SystemExit("invalid core root")
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        repo_id_value = repo_id(conn, core_root)
        run_id = start_run(conn, repo_id_value)
        try:
            candidates = collect_targets(core_root)
            reset_existing_coverage(conn, "bc-core")
            coverage_ids = upsert_coverage_targets(conn, "bc-core", candidates)
            link_counts = link_docs_to_targets(conn, coverage_ids, candidates)
            type_counts = Counter(target_type for target_type, _ in candidates.values())
            summary = {
                "targets": len(candidates),
                "target_types": dict(type_counts),
                "links": dict(link_counts),
            }
            finish_run(conn, run_id, "completed", summary)
            write_report(conn, run_id, link_counts)
            conn.commit()
        except Exception as exc:
            finish_run(conn, run_id, "failed", {}, str(exc))
            conn.commit()
            raise
    print(f"bc-core targets={len(candidates)} links={sum(link_counts.values())}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
