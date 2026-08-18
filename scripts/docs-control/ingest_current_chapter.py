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

FAIL-CLOSED. Because this command writes the SSOT navigation inventory, it refuses:
  - any path whose resolved real path (symlinks + `..` resolved) escapes `ROOT/docs`;
  - anything that is not a regular `.md` file;
  - non-current classes — a resolved path under `docs/archive/`, `docs/evidence/`,
    or `docs/governance/` is archived / evidentiary / adr, not a current chapter;
  - a chapter whose reviewed frontmatter `authority:` is not `authoritative`.
The stored key is canonicalized from the RESOLVED relative path, not the raw input.
Authority / current_truth are DERIVED from the reviewed frontmatter, never hardcoded
onto arbitrary input. Idempotent: re-running upserts the same row.

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
DOCS_ROOT = (ROOT / "docs").resolve()
DB_PATH = Path(os.environ.get("DOCS_CONTROL_DB", ROOT / "docs-control" / "docs-control.db"))

# Resolved-relative prefixes that are NOT current chapters.
INELIGIBLE_PREFIXES = ("archive/", "evidence/", "governance/")


class IngestRefused(Exception):
    pass


def frontmatter_field(text: str, field: str) -> str | None:
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return None
    fm = m.group(1)
    fld = re.search(rf'(?m)^{re.escape(field)}:\s*["\']?(.+?)["\']?\s*$', fm)
    return fld.group(1).strip() if fld else None


def derive_title(text: str, canonical_path: str) -> str:
    title = frontmatter_field(text, "title")
    if title:
        return title
    h1 = re.search(r'(?m)^#\s+(.+?)\s*$', text)
    if h1:
        return h1.group(1).strip()
    return Path(canonical_path).stem.replace("-", " ").title()


def resolve_eligible(rel: str) -> tuple[Path, str, str, str]:
    """Return (resolved_abs, canonical_path, title, authority) or raise IngestRefused."""
    resolved = (ROOT / rel).resolve()  # resolves `..` and symlinks
    try:
        rel_posix = resolved.relative_to(DOCS_ROOT).as_posix()
    except ValueError:
        raise IngestRefused(f"path escapes docs/ tree (resolved {resolved})")
    if not resolved.is_file() or resolved.suffix.lower() != ".md":
        raise IngestRefused(f"not a regular .md file: {resolved}")
    if rel_posix.startswith(INELIGIBLE_PREFIXES):
        raise IngestRefused(f"not a current chapter (archived/evidentiary/governance class): docs/{rel_posix}")
    text = resolved.read_text(encoding="utf-8")
    authority = frontmatter_field(text, "authority")
    if authority != "authoritative":
        raise IngestRefused(f"frontmatter authority={authority!r} is not an eligible current chapter")
    canonical_path = "docs/" + rel_posix
    return resolved, canonical_path, derive_title(text, canonical_path), authority


def upsert(conn: sqlite3.Connection, resolved: Path, canonical_path: str, title: str, authority: str) -> str:
    sha = hashlib.sha256(resolved.read_bytes()).hexdigest()
    status = frontmatter_field(resolved.read_text(encoding="utf-8"), "status") or "reviewing"
    current_truth = 0 if status in {"superseded", "retired"} else 1
    conn.execute(
        """
        INSERT INTO target_documents(
          canonical_path, title, document_kind, authority, lifecycle_status,
          reader_visibility, current_truth, source_doc_id, source_sha256,
          created_at, updated_at)
        VALUES(?, ?, 'current_chapter', ?, 'reviewing', 'primary', ?, NULL, ?,
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
        (canonical_path, title, authority, current_truth, sha),
    )
    return f"{canonical_path}  title={title!r}  authority={authority}  current_truth={current_truth}  sha256={sha[:16]}…"


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    args = sys.argv[1:]
    if not args:
        raise SystemExit("usage: ingest_current_chapter.py <docs/...md> [more...]")
    with sqlite3.connect(DB_PATH) as conn:
        for rel in args:
            try:
                resolved, canonical_path, title, authority = resolve_eligible(rel)
            except IngestRefused as exc:
                raise SystemExit(f"refused: {rel}: {exc}")
            print("ingested:", upsert(conn, resolved, canonical_path, title, authority))
        conn.commit()


if __name__ == "__main__":
    main()
