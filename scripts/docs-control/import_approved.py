#!/usr/bin/env python3
"""Import approved v3 documents into the isolated v4 tree."""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "import-report.md"
DEFAULT_SOURCE = Path("C:/MyProjects/bc-docs-v3")
DEFAULT_DECISIONS = (
    "migrate_current",
    "migrate_reference",
    "migrate_governance",
    "migrate_evidence",
)


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


def latest_run_id(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT run_id FROM inventory_runs WHERE run_kind='source_inventory' AND status='completed' ORDER BY run_id DESC LIMIT 1"
    ).fetchone()
    if not row:
        raise SystemExit("no completed source inventory run found")
    return int(row[0])


def humanize_title(path: str, existing_title: str | None) -> str:
    if existing_title:
        return existing_title
    stem = Path(path).stem.replace("-", " ").replace("_", " ").strip()
    return stem.title() if stem else Path(path).name


def authority_for(target_kind: str, current_truth: int) -> str:
    if target_kind == "current_chapter":
        return "authoritative" if current_truth else "informative"
    if target_kind in {"source_system_reference", "curated_reference", "generated_reference"}:
        return "reference"
    if target_kind in {"adr", "errata"}:
        return "authoritative" if current_truth else "retired"
    if target_kind.startswith("evidence_"):
        return "evidentiary"
    return "retired"


def lifecycle_for(target_kind: str, current_truth: int) -> str:
    if target_kind == "generated_reference":
        return "generated"
    if target_kind.startswith("evidence_") or target_kind == "archive_only":
        return "archived"
    if target_kind in {"adr", "errata"}:
        return "locked" if current_truth else "archived"
    return "reviewing"


def validate_source_path(source_path: Path, source_root: Path) -> None:
    resolved = source_path.resolve()
    if not within(resolved, source_root):
        raise RuntimeError(f"source path escaped source root: {source_path}")
    if not resolved.exists():
        raise RuntimeError(f"source path missing: {source_path}")


def resolve_target(target_rel: str) -> Path:
    rel = Path(target_rel)
    if rel.is_absolute() or ".." in rel.parts:
        raise RuntimeError(f"unsafe target path: {target_rel}")
    target = (ROOT / rel).resolve()
    if not within(target, ROOT.resolve()):
        raise RuntimeError(f"target path escaped v4 root: {target_rel}")
    if not within(target, (ROOT / "docs").resolve()):
        raise RuntimeError(f"target path must be under docs/: {target_rel}")
    return target


def rows_for_import(
    conn: sqlite3.Connection,
    run_id: int,
    decisions: tuple[str, ...],
    sections: tuple[str, ...],
    limit: int | None,
) -> list[sqlite3.Row]:
    placeholders = ",".join("?" for _ in decisions)
    params: list[object] = [run_id, *decisions]
    section_clause = ""
    if sections:
        section_placeholders = ",".join("?" for _ in sections)
        section_clause = f" AND sd.top_level_dir IN ({section_placeholders})"
        params.extend(sections)
    limit_clause = ""
    if limit is not None:
        limit_clause = " LIMIT ?"
        params.append(limit)
    return conn.execute(
        f"""
        SELECT
          sd.source_doc_id,
          sd.rel_path,
          sd.abs_path,
          sd.sha256,
          sd.title,
          sd.top_level_dir,
          md.decision_code,
          md.target_path,
          md.target_kind,
          md.reader_visibility,
          md.current_truth,
          md.rationale
        FROM migration_decisions md
        JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
        WHERE sd.run_id = ?
          AND md.decision_code IN ({placeholders})
          AND md.target_path IS NOT NULL
          AND md.target_kind IS NOT NULL
          {section_clause}
        ORDER BY md.decision_code, md.target_path
        {limit_clause}
        """,
        params,
    ).fetchall()


def upsert_target_document(conn: sqlite3.Connection, row: sqlite3.Row) -> None:
    target_kind = row["target_kind"]
    current_truth = int(row["current_truth"])
    conn.execute(
        """
        INSERT INTO target_documents(
          canonical_path,
          title,
          document_kind,
          authority,
          lifecycle_status,
          reader_visibility,
          current_truth,
          source_doc_id,
          source_sha256
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(canonical_path) DO UPDATE SET
          title = excluded.title,
          document_kind = excluded.document_kind,
          authority = excluded.authority,
          lifecycle_status = excluded.lifecycle_status,
          reader_visibility = excluded.reader_visibility,
          current_truth = excluded.current_truth,
          source_doc_id = excluded.source_doc_id,
          source_sha256 = excluded.source_sha256,
          updated_at = CURRENT_TIMESTAMP
        """,
        (
            row["target_path"],
            humanize_title(row["target_path"], row["title"]),
            target_kind,
            authority_for(target_kind, current_truth),
            lifecycle_for(target_kind, current_truth),
            row["reader_visibility"],
            current_truth,
            row["source_doc_id"],
            row["sha256"],
        ),
    )


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def write_report(
    run_id: int,
    dry_run: bool,
    force: bool,
    decisions: tuple[str, ...],
    sections: tuple[str, ...],
    statuses: Counter[str],
    samples: list[tuple[str, str, str, str]],
) -> None:
    lines = [
        "# v4 Import Report",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Inventory run: `{run_id}`",
        f"Dry run: `{dry_run}`",
        f"Force overwrite: `{force}`",
        f"Decision filter: `{', '.join(decisions)}`",
        f"Section filter: `{', '.join(sections) if sections else '(all)'}`",
        "",
        "## Result Summary",
        "",
        "| Result | Files |",
        "|---|---|",
    ]
    for status, count in sorted(statuses.items()):
        lines.append(f"| {markdown_escape(status)} | {count} |")
    lines.extend(["", "## Sample Rows", "", "| Result | Source | Target | Decision |", "|---|---|---|---|"])
    for status, source, target, decision in samples[:80]:
        lines.append(
            f"| {markdown_escape(status)} | {markdown_escape(source)} | {markdown_escape(target)} | {markdown_escape(decision)} |"
        )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="v3 source docs root")
    parser.add_argument(
        "--decision",
        action="append",
        choices=(
            "migrate_current",
            "migrate_reference",
            "migrate_governance",
            "migrate_evidence",
            "archive_only",
        ),
        help="decision code to import; may be passed multiple times",
    )
    parser.add_argument("--section", action="append", help="source top-level section to import; may be repeated")
    parser.add_argument("--limit", type=int, help="limit imported rows")
    parser.add_argument("--dry-run", action="store_true", help="plan the import without copying or updating target_documents")
    parser.add_argument("--force", action="store_true", help="overwrite existing target files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    source_root = args.source.resolve()
    decisions = tuple(args.decision or DEFAULT_DECISIONS)
    sections = tuple(args.section or ())
    statuses: Counter[str] = Counter()
    samples: list[tuple[str, str, str, str]] = []

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        run_id = latest_run_id(conn)
        rows = rows_for_import(conn, run_id, decisions, sections, args.limit)
        for row in rows:
            source_path = Path(row["abs_path"])
            target_path = resolve_target(row["target_path"])
            validate_source_path(source_path, source_root)
            status = "dry_run"
            if not args.dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                existed_before = target_path.exists()
                if existed_before and not args.force:
                    target_hash = sha256(target_path)
                    if target_hash == row["sha256"]:
                        status = "already_current"
                        upsert_target_document(conn, row)
                    else:
                        status = "conflict_existing"
                else:
                    shutil.copy2(source_path, target_path)
                    status = "copied_overwrite" if args.force and existed_before else "copied"
                    upsert_target_document(conn, row)
            statuses[status] += 1
            if len(samples) < 80:
                samples.append((status, row["rel_path"], row["target_path"], row["decision_code"]))
        if not args.dry_run:
            conn.commit()
    write_report(run_id, args.dry_run, args.force, decisions, sections, statuses, samples)
    print(f"rows={len(rows)} results={dict(statuses)}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
