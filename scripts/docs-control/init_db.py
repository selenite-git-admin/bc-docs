#!/usr/bin/env python3
"""Initialize the bc-docs-v4 SQLite control database."""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
SCHEMA_PATH = ROOT / "docs-control" / "schema.sql"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema)
        conn.commit()
    print(f"initialized {DB_PATH}")


if __name__ == "__main__":
    main()
