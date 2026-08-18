#!/usr/bin/env python3
"""Ingest a net-new current-chapter target_documents row from the chapter bytes.

The legacy migration pipeline (inventory_v3.py -> import_approved.py) creates
target_documents rows only for documents carried from the legacy source inventory
under an approved decision. A chapter authored directly in the v3 `docs/` tree
(e.g. the-runtime-ecosystem.md, or a net-new chapter) has no source_documents row
and therefore no automatic target_documents ingest. This command closes that gap:
it discovers the given chapter path(s), reads the chapter bytes, derives the title
from the H1 / frontmatter, computes source_sha256, and upserts the
`target_documents` row (ON CONFLICT(canonical_path) DO UPDATE), so seed_navigation
renders the chapter as a visible target rather than a planned stub.

Idempotent: re-running upserts the same row. Reviewable and byte-derived — it does
not hand-invent identity; title and hash come from the chapter file.

DB path is env-overridable (DOCS_CONTROL_DB) so an ingest+reseed can be proven in
isolation against a copy without mutating the live control DB.

Usage:
  python scripts/docs-control/ingest_current_chapter.py docs/operating-model/the-runtime-ecosystem.md
"""
from __future__ import annotations

import hashlib
import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.environ.get("DOCS_CONTROL_DB", ROOT / "docs-control" / "docs-control.db"))


def derive_title(text: str, canonical_path: str) -> str:
    # Prefer frontmatter `title:`; fall back to the first H1; then the stem.
    fm = re.search(r'(?m)^title:\s*["\']?(.+?)["\']?\s*$', text[:2000])
    if fm:
        return fm.group(1).strip()
    h1 = re.search(r'(?m)^#\s+(.+?)\s*$', text)
    if h1:
        return h1.group(1).strip()
    return Path(canonical_path).stem.replace("-", " ").title()


def upsert(conn: sqlite3.Connection, abs_path: Path, canonical_path: str) -> str:
    raw = abs_path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    title = derive_title(raw.decode("utf-8"), canonical_path)
    conn.execute(
        """
        INSERT INTO target_documents(
          canonical_path, title, document_kind, authority, lifecycle_status,
          reader_visibility, current_truth, source_doc_id, source_sha256,
          created_at, updated_at)
        VALUES(?, ?, 'current_chapter', 'authoritative', 'reviewing', 'primary', 1, NULL, ?,
               strftime('%Y-%m-%d %H:%M:%S','now'), strftime('%Y-%m-%d %H:%M:%S','now'))
        ON CONFLICT(canonical_path) DO UPDATE SET
          title = excluded.title,
          document_kind = excluded.document_kind,
          authority = excluded.authority,
          reader_visibility = excluded.reader_visibility,
          current_truth = excluded.current_truth,
          source_sha256 = excluded.source_sha256,
          updated_at = excluded.updated_at
        """,
        (canonical_path, title, sha),
    )
    return f"{canonical_path}  title={title!r}  sha256={sha[:16]}…"


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    args = sys.argv[1:]
    if not args:
        raise SystemExit("usage: ingest_current_chapter.py <docs/...md> [more...]")
    with sqlite3.connect(DB_PATH) as conn:
        for rel in args:
            canonical_path = rel.replace("\\", "/")
            if not canonical_path.startswith("docs/"):
                canonical_path = "docs/" + canonical_path.lstrip("/")
            abs_path = ROOT / canonical_path
            if not abs_path.is_file():
                raise SystemExit(f"chapter not found: {abs_path}")
            print("ingested:", upsert(conn, abs_path, canonical_path))
        conn.commit()


if __name__ == "__main__":
    main()
