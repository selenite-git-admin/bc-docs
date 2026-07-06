#!/usr/bin/env python3
"""Audit imported v4 target documents for stale references and link issues."""
from __future__ import annotations

import argparse
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "target-audit.md"

LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")
ABS_LOCAL_RE = re.compile(r"(?i)([A-Z]:[\\/][^\s)]+|/Users/[^\s)]+|/home/[^\s)]+)")
LINK_TARGET_RE = re.compile(r"\]\([^)]*\)")
BARE_URL_RE = re.compile(r"https?://\S+")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
TEMPORAL_CLAIM_RE = re.compile(r"(?i)\b(as of|current as of|currently|today|latest|now)\b")
ISO_DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
PERCENT_RE = re.compile(r"\b\d+(?:\.\d+)?\s?%")
BIG_NUMBER_RE = re.compile(r"\b\d{1,3}(?:,\d{3})+\b")
UNIT_STAT_RE = re.compile(
    r"(?i)\b\d+(?:\.\d+)?\s?(ms|sec|secs|seconds|minutes|gb|mb|rows|records|controllers|tables|files|documents)\b"
)


def body_without_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :])
    return text


def body_without_frontmatter_or_code(text: str) -> str:
    body = body_without_frontmatter(text)
    kept: list[str] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    return "\n".join(kept)


def claim_scan_text(text: str) -> str:
    text = LINK_TARGET_RE.sub("]", text)
    text = BARE_URL_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def start_audit_run(conn: sqlite3.Connection) -> int:
    cursor = conn.execute(
        """
        INSERT INTO inventory_runs(run_kind, tool_name, tool_version, status)
        VALUES ('audit', 'audit_target_docs.py', '0.1.0', 'running')
        """
    )
    return int(cursor.lastrowid)


def finish_audit_run(conn: sqlite3.Connection, run_id: int, status: str, summary: str, error: str | None = None) -> None:
    conn.execute(
        """
        UPDATE inventory_runs
        SET completed_at = CURRENT_TIMESTAMP,
            status = ?,
            summary_json = ?,
            error_text = ?
        WHERE run_id = ?
        """,
        (status, summary, error, run_id),
    )


def add_finding(
    conn: sqlite3.Connection,
    run_id: int,
    severity: str,
    category: str,
    path: str,
    message: str,
    action: str,
) -> None:
    conn.execute(
        """
        INSERT INTO audit_findings(run_id, severity, category, subject_path, message, suggested_action)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (run_id, severity, category, path, message, action),
    )


def target_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
          canonical_path,
          document_kind,
          authority,
          lifecycle_status,
          reader_visibility,
          current_truth
        FROM target_documents
        ORDER BY canonical_path
        """
    ).fetchall()


def stale_patterns(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT pattern_text, severity, replacement_guidance FROM stale_path_patterns ORDER BY severity DESC, pattern_text"
    ).fetchall()


def clean_link(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    return raw


def is_external_or_special(target: str) -> bool:
    parsed = urlparse(target)
    return parsed.scheme in {"http", "https", "mailto", "tel", "mcp", "app"}


def audit_links(conn: sqlite3.Connection, run_id: int, canonical_path: str, text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    source_path = (ROOT / canonical_path).resolve()
    docs_root = (ROOT / "docs").resolve()
    for match in LINK_RE.finditer(text):
        label, raw_target = match.groups()
        target = clean_link(raw_target)
        if not target or target.startswith("#") or is_external_or_special(target):
            continue
        if ABS_LOCAL_RE.search(target) or re.match(r"^[A-Z]:\\", target, flags=re.IGNORECASE):
            add_finding(
                conn,
                run_id,
                "error",
                "absolute-local-link",
                canonical_path,
                f"Absolute local link `{target}` found in link `{label}`.",
                "Replace with a repository-relative link, generated reference, or explicit historical note.",
            )
            counts["absolute-local-link"] += 1
            continue
        path_part = unquote(target.split("#", 1)[0])
        if not path_part:
            continue
        if path_part.startswith("/docs/"):
            resolved = (ROOT / path_part.lstrip("/")).resolve()
        else:
            resolved = (source_path.parent / path_part).resolve()
        if not within(resolved, docs_root):
            add_finding(
                conn,
                run_id,
                "error",
                "link-escapes-docs-root",
                canonical_path,
                f"Internal link `{target}` resolves outside `docs/`.",
                "Repoint the link to a v4 document or remove it.",
            )
            counts["link-escapes-docs-root"] += 1
            continue
        if not resolved.exists():
            add_finding(
                conn,
                run_id,
                "warning",
                "missing-internal-link",
                canonical_path,
                f"Internal link `{target}` does not resolve from this document.",
                "Repoint to the v4 target path, regenerate the referenced artifact, or remove the link.",
            )
            counts["missing-internal-link"] += 1
    return counts


def audit_stale_patterns(
    conn: sqlite3.Connection,
    run_id: int,
    canonical_path: str,
    text: str,
    patterns: list[sqlite3.Row],
    document_kind: str,
    reader_visibility: str,
    current_truth: int,
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in patterns:
        pattern = row["pattern_text"]
        if pattern not in text:
            continue
        severity = stale_pattern_severity(
            row["severity"],
            document_kind,
            reader_visibility,
            current_truth,
        )
        add_finding(
            conn,
            run_id,
            severity,
            "stale-doc-root-reference",
            canonical_path,
            f"Found legacy/staging path reference `{pattern}`.",
            row["replacement_guidance"] or "Replace or mark as historical provenance.",
        )
        counts["stale-doc-root-reference"] += 1
    return counts


def stale_pattern_severity(base_severity: str, document_kind: str, reader_visibility: str, current_truth: int) -> str:
    if document_kind == "adr":
        return "warning" if base_severity == "error" else "info"
    if current_truth:
        return base_severity
    if document_kind in {"current_chapter", "generated_reference", "curated_reference", "source_system_reference"}:
        return base_severity
    if (
        document_kind.startswith("evidence_")
        or document_kind == "archive_only"
        or reader_visibility in {"evidence", "archive", "hidden"}
    ):
        return "info"
    return "warning" if base_severity == "error" else "info"


def audit_mutable_claims(
    conn: sqlite3.Connection,
    run_id: int,
    canonical_path: str,
    text: str,
    document_kind: str,
    current_truth: int,
) -> Counter[str]:
    counts: Counter[str] = Counter()
    if not current_truth:
        return counts
    if document_kind not in {"current_chapter", "source_system_reference", "curated_reference"}:
        return counts
    body_text = claim_scan_text(body_without_frontmatter_or_code(text))
    checks = [
        ("temporal-claim", TEMPORAL_CLAIM_RE, "Replace live/time-relative language with versioned provenance or remove the claim."),
        ("iso-date-claim", ISO_DATE_RE, "Keep dates only when they are historical provenance, decision dates, or explicit version markers."),
        ("percentage-stat", PERCENT_RE, "Avoid volatile percentages in current docs unless backed by generated evidence."),
        ("large-number-stat", BIG_NUMBER_RE, "Avoid volatile counts in current docs unless backed by generated evidence."),
        ("unit-stat", UNIT_STAT_RE, "Avoid volatile operational statistics in current docs unless backed by generated evidence."),
    ]
    for category, regex, action in checks:
        matches = regex.findall(body_text)
        if not matches:
            continue
        add_finding(
            conn,
            run_id,
            "warning",
            category,
            canonical_path,
            f"Found {len(matches)} possible mutable claim(s) in a current/reference document.",
            action,
        )
        counts[category] += 1
    return counts


def write_report(conn: sqlite3.Connection, run_id: int, counts: Counter[str]) -> None:
    lines = [
        "# Target Documentation Audit",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Audit run: `{run_id}`",
        "",
        "## Finding Categories",
        "",
        "| Category | Findings |",
        "|---|---|",
    ]
    for category, count in sorted(counts.items()):
        lines.append(f"| {category} | {count} |")
    lines.extend(["", "## Severity", "", "| Severity | Findings |", "|---|---|"])
    for row in conn.execute(
        """
        SELECT severity, COUNT(*)
        FROM audit_findings
        WHERE run_id = ?
        GROUP BY severity
        ORDER BY CASE severity WHEN 'blocker' THEN 1 WHEN 'error' THEN 2 WHEN 'warning' THEN 3 ELSE 4 END
        """,
        (run_id,),
    ):
        lines.append(f"| {row[0]} | {row[1]} |")
    lines.extend(["", "## Top Open Findings", "", "| Severity | Category | Path | Message |", "|---|---|---|---|"])
    for row in conn.execute(
        """
        SELECT severity, category, subject_path, message
        FROM audit_findings
        WHERE run_id = ?
        ORDER BY CASE severity WHEN 'blocker' THEN 1 WHEN 'error' THEN 2 WHEN 'warning' THEN 3 ELSE 4 END,
                 category,
                 subject_path
        LIMIT 80
        """,
        (run_id,),
    ):
        message = str(row[3]).replace("|", "\\|")
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {message} |")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="limit audited target documents")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        run_id = start_audit_run(conn)
        counts: Counter[str] = Counter()
        try:
            patterns = stale_patterns(conn)
            rows = target_rows(conn)
            if args.limit:
                rows = rows[: args.limit]
            for row in rows:
                canonical_path = row["canonical_path"]
                path = (ROOT / canonical_path).resolve()
                if not path.exists():
                    add_finding(
                        conn,
                        run_id,
                        "error",
                        "target-file-missing",
                        canonical_path,
                        "Registered target document file does not exist.",
                        "Restore the file or remove the target document row.",
                    )
                    counts["target-file-missing"] += 1
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                counts.update(audit_links(conn, run_id, canonical_path, text))
                counts.update(
                    audit_stale_patterns(
                        conn,
                        run_id,
                        canonical_path,
                        text,
                        patterns,
                        row["document_kind"],
                        row["reader_visibility"],
                        int(row["current_truth"]),
                    )
                )
                counts.update(
                    audit_mutable_claims(
                        conn,
                        run_id,
                        canonical_path,
                        text,
                        row["document_kind"],
                        int(row["current_truth"]),
                    )
                )
            finish_audit_run(conn, run_id, "completed", str(dict(counts)))
            write_report(conn, run_id, counts)
            conn.commit()
        except Exception as exc:
            finish_audit_run(conn, run_id, "failed", "{}", str(exc))
            conn.commit()
            raise
    print(f"audited run={run_id} findings={sum(counts.values())} categories={dict(counts)}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
