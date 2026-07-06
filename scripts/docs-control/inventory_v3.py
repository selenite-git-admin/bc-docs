#!/usr/bin/env python3
"""Inventory bc-docs-v3 into the v4 control database without modifying v3."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
SCHEMA_PATH = ROOT / "docs-control" / "schema.sql"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def parse_frontmatter(text: str) -> dict[str, Any]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    block = match.group(1)
    result: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key:
            if not isinstance(result.get(current_key), list):
                prior = result.get(current_key)
                result[current_key] = [] if prior in (None, "") else [prior]
            item = line[4:].strip().strip("\"'")
            if item:
                result[current_key].append(item)
            continue
        if ":" not in line or line.startswith("-"):
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            result[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            result[key] = [] if not inner else [part.strip().strip("\"'") for part in inner.split(",")]
        else:
            result[key] = value.strip("\"'")
    return result


def title_for(text: str, fm: dict[str, Any], path: Path) -> str:
    title = fm.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    body = FRONTMATTER_RE.sub("", text, count=1)
    match = H1_RE.search(body)
    if match:
        return match.group(1).strip()
    return path.stem.replace("-", " ")


def guess_kind(rel: str, fm: dict[str, Any]) -> str:
    name = Path(rel).name.lower()
    top = rel.split("/", 1)[0]
    if top == "adrs" or name.startswith("adr-"):
        return "adr"
    if top == "errata":
        return "errata"
    if top == "source-systems":
        return "source_system_reference"
    if top in {"api", "schemas", "data-dictionary", "glossary"}:
        return "generated_or_curated_reference"
    if top in {"overview", "foundation", "operating-model", "implementation", "ai", "development", "onboarding", "operations", "compliance"}:
        evidence_markers = (
            "dbcp",
            "closeout",
            "checkpoint",
            "ledger",
            "audit",
            "handoff",
            "packet",
            "prep",
            "study",
            "plan",
            "proposal",
            "inventory",
        )
        if any(marker in name for marker in evidence_markers):
            if "closeout" in name:
                return "evidence_closeout"
            if "dbcp" in name:
                return "evidence_dbcp"
            if "ledger" in name:
                return "evidence_ledger"
            if "audit" in name:
                return "evidence_audit"
            return "evidence_work_record"
        return "current_chapter_candidate"
    return "archive_candidate"


def guess_domain(rel: str, fm: dict[str, Any]) -> str | None:
    domain = fm.get("domain")
    if isinstance(domain, str) and domain.strip():
        return domain.strip()
    top = rel.split("/", 1)[0]
    domain_map = {
        "overview": "overview",
        "foundation": "foundation",
        "operating-model": "operating_model",
        "implementation": "implementation",
        "ai": "ai",
        "development": "development",
        "onboarding": "onboarding",
        "operations": "operations",
        "compliance": "compliance",
        "source-systems": "sources",
        "data-dictionary": "database",
        "api": "api",
        "schemas": "schemas",
        "adrs": "governance",
        "errata": "governance",
    }
    return domain_map.get(top)


def ensure_schema() -> None:
    if not DB_PATH.exists():
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(schema)
            conn.commit()


def upsert_repo(conn: sqlite3.Connection, source: Path) -> int:
    conn.execute(
        """
        INSERT OR IGNORE INTO repositories(repo_key, repo_name, root_path, role, active_for_cutover, notes)
        VALUES('bc-docs-v3', 'bc-docs-v3', ?, 'source_docs', 0, 'Live Claude-facing source during v4 build; read-only for migration')
        """,
        (str(source),),
    )
    row = conn.execute("SELECT repo_id FROM repositories WHERE repo_key = 'bc-docs-v3'").fetchone()
    return int(row[0])


def insert_link_rows(conn: sqlite3.Connection, source_doc_id: int, text: str, source_file: Path, source_root: Path) -> None:
    for match in LINK_RE.finditer(text):
        label = match.group(1)
        raw = match.group(2).strip()
        if "#" in raw:
            without_fragment, fragment = raw.split("#", 1)
        else:
            without_fragment, fragment = raw, None
        scheme = raw.split(":", 1)[0].lower() if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", raw) else None
        target_scope = "unknown"
        target_exists: int | None = None
        severity: str | None = None
        if scheme in {"http", "https", "mailto"}:
            target_scope = "external_url"
        elif scheme == "mcp":
            target_scope = "mcp"
        elif re.match(r"^[A-Za-z]:[\\/]", raw):
            target_scope = "absolute_local"
            target_exists = 1 if Path(without_fragment).exists() else 0
            severity = "warning"
        else:
            target_scope = "internal"
            candidate = (source_file.parent / without_fragment).resolve() if without_fragment else source_file
            try:
                candidate.relative_to(source_root)
                target_exists = 1 if candidate.exists() else 0
                if target_exists == 0:
                    severity = "warning"
            except ValueError:
                target_exists = 1 if candidate.exists() else 0
                severity = "warning"
        conn.execute(
            """
            INSERT INTO extracted_links(source_doc_id, link_text, raw_target, target_without_fragment, target_fragment, target_scheme, target_exists, target_scope, finding_severity)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (source_doc_id, label, raw, without_fragment, fragment, scheme, target_exists, target_scope, severity),
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="C:/MyProjects/bc-docs-v3", help="Read-only source docs root")
    args = parser.parse_args()
    source = Path(args.source).resolve()
    docs_dir = source / "docs"
    if not docs_dir.exists():
        raise SystemExit(f"docs directory not found: {docs_dir}")

    ensure_schema()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        repo_id = upsert_repo(conn, source)
        cur = conn.execute(
            "INSERT INTO inventory_runs(run_kind, source_repo_id, tool_name) VALUES('source_inventory', ?, 'inventory_v3.py')",
            (repo_id,),
        )
        run_id = int(cur.lastrowid)
        count = 0
        kind_counts: dict[str, int] = {}
        try:
            for file_path in sorted(docs_dir.rglob("*.md")):
                rel = file_path.relative_to(docs_dir).as_posix()
                data = file_path.read_bytes()
                text = data.decode("utf-8", errors="replace")
                fm = parse_frontmatter(text)
                kind = guess_kind(rel, fm)
                kind_counts[kind] = kind_counts.get(kind, 0) + 1
                top = rel.split("/", 1)[0]
                sha = hashlib.sha256(data).hexdigest()
                line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
                cur = conn.execute(
                    """
                    INSERT INTO source_documents(
                      run_id, repo_id, rel_path, abs_path, sha256, byte_count, line_count, title,
                      frontmatter_uid, frontmatter_id, frontmatter_status, frontmatter_authority,
                      frontmatter_collection, frontmatter_order_text, top_level_dir, guessed_kind,
                      guessed_domain, has_frontmatter
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        repo_id,
                        rel,
                        str(file_path),
                        sha,
                        len(data),
                        line_count,
                        title_for(text, fm, file_path),
                        fm.get("uid") if isinstance(fm.get("uid"), str) else None,
                        fm.get("id") if isinstance(fm.get("id"), str) else None,
                        fm.get("status") if isinstance(fm.get("status"), str) else None,
                        fm.get("authority") if isinstance(fm.get("authority"), str) else None,
                        fm.get("collection") if isinstance(fm.get("collection"), str) else None,
                        fm.get("order") if isinstance(fm.get("order"), str) else None,
                        top,
                        kind,
                        guess_domain(rel, fm),
                        1 if fm else 0,
                    ),
                )
                source_doc_id = cur.lastrowid
                if source_doc_id:
                    insert_link_rows(conn, int(source_doc_id), text, file_path, source)
                count += 1
            summary = {"documents": count, "kind_counts": kind_counts}
            conn.execute(
                "UPDATE inventory_runs SET completed_at = CURRENT_TIMESTAMP, status = 'completed', summary_json = ? WHERE run_id = ?",
                (json.dumps(summary, sort_keys=True), run_id),
            )
            conn.commit()
            print(json.dumps(summary, indent=2, sort_keys=True))
        except Exception as exc:
            conn.execute(
                "UPDATE inventory_runs SET completed_at = CURRENT_TIMESTAMP, status = 'failed', error_text = ? WHERE run_id = ?",
                (str(exc), run_id),
            )
            conn.commit()
            raise


if __name__ == "__main__":
    main()
