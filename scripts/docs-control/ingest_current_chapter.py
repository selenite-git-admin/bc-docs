#!/usr/bin/env python3
"""Ingest a net-new current-chapter target_documents row from the chapter bytes.

The legacy migration pipeline (inventory_v3.py -> import_approved.py) creates
target_documents rows only for documents carried from the legacy source inventory
under an approved decision. A chapter authored directly in the v3 `docs/` tree
(e.g. the-runtime-ecosystem.md, or a net-new chapter) has no source_documents row
and therefore no automatic target_documents ingest. This command closes that gap:
it discovers the given chapter path(s), reads the chapter bytes ONCE, derives the
title / authority / class / current_truth AND the source_sha256 from that one byte
read, and upserts the `target_documents` row (ON CONFLICT DO UPDATE), so
seed_navigation renders the chapter as a visible target rather than a planned stub.

FAIL-CLOSED. Because this command writes the SSOT navigation inventory, it refuses:
  - any path whose resolved real path (symlinks + `..` resolved) escapes `ROOT/docs`;
  - anything that is not a regular `.md` file;
  - non-current classes — a resolved path under `docs/archive/`, `docs/evidence/`,
    or `docs/governance/` is archived / evidentiary / adr, not a current chapter;
  - a chapter whose reviewed frontmatter `authority:` is not `authoritative`.

EXACT-BYTE BINDING. The file is read exactly once into `raw`; title, authority,
class, current_truth, and source_sha256 are all derived from that same `raw`. The
stored digest therefore proves the exact bytes that authorized the row — a
concurrent edit cannot split metadata from digest. The stored key is canonicalized
from the RESOLVED relative path, not the raw input.

Env-overridable for isolated proofs: DOCS_CONTROL_DB (control DB) and
DOCS_CONTROL_ROOT (repo root, so an ingest can run against a temp docs tree).

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

ROOT = Path(os.environ.get("DOCS_CONTROL_ROOT", Path(__file__).resolve().parents[2])).resolve()
DOCS_ROOT = (ROOT / "docs").resolve()
DB_PATH = Path(os.environ.get("DOCS_CONTROL_DB", ROOT / "docs-control" / "docs-control.db"))

INELIGIBLE_PREFIXES = ("archive/", "evidence/", "governance/")


class IngestRefused(Exception):
    pass


def _fm_field(text: str, field: str) -> str | None:
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return None
    fld = re.search(rf'(?m)^{re.escape(field)}:\s*["\']?(.+?)["\']?\s*$', m.group(1))
    return fld.group(1).strip() if fld else None


def _title(text: str, canonical_path: str) -> str:
    t = _fm_field(text, "title")
    if t:
        return t
    h1 = re.search(r'(?m)^#\s+(.+?)\s*$', text)
    return h1.group(1).strip() if h1 else Path(canonical_path).stem.replace("-", " ").title()


def prepare_row(rel: str) -> dict:
    """Resolve, validate, and derive the full row from ONE byte read. Raise IngestRefused."""
    resolved = (ROOT / rel).resolve()  # resolves `..` and symlinks
    try:
        rel_posix = resolved.relative_to(DOCS_ROOT).as_posix()
    except ValueError:
        raise IngestRefused(f"path escapes docs/ tree (resolved {resolved})")
    if not resolved.is_file() or resolved.suffix.lower() != ".md":
        raise IngestRefused(f"not a regular .md file: {resolved}")
    if rel_posix.startswith(INELIGIBLE_PREFIXES):
        raise IngestRefused(f"not a current chapter (archived/evidentiary/governance class): docs/{rel_posix}")
    raw = resolved.read_bytes()  # THE ONE READ — everything below derives from `raw`
    text = raw.decode("utf-8")
    authority = _fm_field(text, "authority")
    if authority != "authoritative":
        raise IngestRefused(f"frontmatter authority={authority!r} is not an eligible current chapter")
    status = _fm_field(text, "status") or "reviewing"
    canonical_path = "docs/" + rel_posix
    return {
        "canonical_path": canonical_path,
        "title": _title(text, canonical_path),
        "authority": authority,
        "current_truth": 0 if status in {"superseded", "retired"} else 1,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
    }


def upsert(conn: sqlite3.Connection, row: dict) -> str:
    conn.execute(
        """
        INSERT INTO target_documents(
          canonical_path, title, document_kind, authority, lifecycle_status,
          reader_visibility, current_truth, source_doc_id, source_sha256,
          created_at, updated_at)
        VALUES(:canonical_path, :title, 'current_chapter', :authority, 'reviewing',
               'primary', :current_truth, NULL, :source_sha256,
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
        row,
    )
    return (f"{row['canonical_path']}  title={row['title']!r}  authority={row['authority']}"
            f"  current_truth={row['current_truth']}  sha256={row['source_sha256'][:16]}…")


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    args = sys.argv[1:]
    if not args:
        raise SystemExit("usage: ingest_current_chapter.py <docs/...md> [more...]")
    with sqlite3.connect(DB_PATH) as conn:
        for rel in args:
            try:
                row = prepare_row(rel)
            except IngestRefused as exc:
                raise SystemExit(f"refused: {rel}: {exc}")
            print("ingested:", upsert(conn, row))
        conn.commit()


if __name__ == "__main__":
    main()
