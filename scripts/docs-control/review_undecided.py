#!/usr/bin/env python3
"""Second-pass review for v3 files left undecided by the first classifier."""
from __future__ import annotations

import argparse
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "undecided-review.md"
REVIEWER = "undecided-review-v0.1"

DATE_RE = re.compile(r"(?:^|[/_-])20\d{2}[-_]\d{2}[-_]\d{2}(?:[/_.-]|$)")
WORK_RECORD_TERMS = {
    "preflight",
    "post-apply",
    "execution-result",
    "experiment-result",
    "compile-report",
    "closeout",
    "checkpoint",
    "milestone",
    "handoff",
    "packet",
    "retry-ledger",
    "projection",
    "reproof",
    "proof",
    "slice",
    "phase",
    "pass",
    "operator-decision",
    "operator-decisions",
    "decision-packet",
    "walkthrough",
    "review-against",
    "session-findings",
    "readiness",
}

REFERENCE_TERMS = {
    "doctrine",
    "requirements",
    "first-principles",
    "golden-path",
    "operational-state",
    "trust-catalog",
    "policy",
    "runbook",
    "sop",
    "index",
    "design",
    "framework",
    "boundary",
    "model-note",
}

SUPERSEDED_ONBOARDING = {
    "data-seeding-and-build-order.md": "Superseded by seed-catalog and onboarding flow chapters.",
    "mc-chain-integrity.md": "Superseded by operating-model chain-integrity and metric-workstream chapters.",
    "metric-contract-creation.md": "Superseded by canonical/source/admission contract creation chapters.",
    "metric-registration.md": "Superseded by metric workstream and tenant metric binding chapters.",
    "metric-seed-catalog-management.md": "Superseded by seed catalog management and metric catalog chapters.",
}

MANUAL_OVERRIDES = {
    "implementation/bcf-mcf-panel-workbench-alignment-note.md": {
        "decision_code": "migrate_reference",
        "target_path": "docs/reference/technical-notes/implementation/bcf-mcf-panel-workbench-alignment-note.md",
        "target_kind": "curated_reference",
        "reader_visibility": "reference",
        "current_truth": 0,
        "bucket": "technical-note",
        "confidence": "high",
        "rationale": "Informative architecture-alignment note; useful as technical reference, not primary doctrine.",
    },
    "implementation/business-concept-registry-f4-s1-characteristic-seed-list.md": {
        "decision_code": "migrate_reference",
        "target_path": "docs/reference/technical-notes/implementation/business-concept-registry-f4-s1-characteristic-seed-list.md",
        "target_kind": "curated_reference",
        "reader_visibility": "reference",
        "current_truth": 0,
        "bucket": "curated-data-artifact",
        "confidence": "high",
        "rationale": "Accepted curated seed-content artifact; keep as reference, not current reader chapter.",
    },
    "implementation/business-concept-registry-ui-mvp-shipped.md": {
        "decision_code": "migrate_evidence",
        "target_path": "docs/evidence/closeouts/implementation/business-concept-registry-ui-mvp-shipped.md",
        "target_kind": "evidence_closeout",
        "reader_visibility": "evidence",
        "current_truth": 0,
        "bucket": "closeout",
        "confidence": "high",
        "rationale": "Accepted UI MVP close-out note; preserve as evidence outside reader flow.",
    },
    "implementation/core-chain-golden-path.md": {
        "decision_code": "migrate_reference",
        "target_path": "docs/reference/technical-notes/implementation/core-chain-golden-path.md",
        "target_kind": "curated_reference",
        "reader_visibility": "reference",
        "current_truth": 0,
        "bucket": "technical-note",
        "confidence": "high",
        "rationale": "Authoritative orientation note for chain consolidation; keep as technical reference while primary chapters carry current flow.",
    },
    "implementation/finance-package-v0-gold-universe.md": {
        "decision_code": "migrate_reference",
        "target_path": "docs/reference/technical-notes/implementation/finance-package-v0-gold-universe.md",
        "target_kind": "curated_reference",
        "reader_visibility": "reference",
        "current_truth": 0,
        "bucket": "curated-data-artifact",
        "confidence": "high",
        "rationale": "Planning SSOT/data-artifact note; retain as reference with provenance, not runtime truth.",
    },
    "implementation/mcf-post-bcf-metric-workflow-wiring-impact.md": {
        "decision_code": "migrate_evidence",
        "target_path": "docs/evidence/audits/implementation/mcf-post-bcf-metric-workflow-wiring-impact.md",
        "target_kind": "evidence_audit",
        "reader_visibility": "evidence",
        "current_truth": 0,
        "bucket": "audit",
        "confidence": "high",
        "rationale": "Architecture audit performed before the M12 DBCP gate; preserve as audit evidence.",
    },
    "implementation/pr-g2-first-service-surface-m12-authz.md": {
        "decision_code": "migrate_evidence",
        "target_path": "docs/evidence/dbcp/implementation/pr-g2-first-service-surface-m12-authz.md",
        "target_kind": "evidence_dbcp",
        "reader_visibility": "evidence",
        "current_truth": 0,
        "bucket": "dbcp",
        "confidence": "high",
        "rationale": "Narrow authorization DBCP; preserve in evidence, not reader flow.",
    },
    "operating-model/metric-management-system-recovery-track.md": {
        "decision_code": "migrate_current",
        "target_path": "docs/operating-model/metric-management-system-recovery-track.md",
        "target_kind": "current_chapter",
        "reader_visibility": "primary",
        "current_truth": 1,
        "bucket": "current-chapter",
        "confidence": "high",
        "rationale": "Authoritative MMS recovery-track doctrine; belongs beside the parent Metric Management System chapter.",
    },
    "operations/cognito-identity-remediation.md": {
        "decision_code": "migrate_reference",
        "target_path": "docs/reference/runbooks/operations/cognito-identity-remediation.md",
        "target_kind": "curated_reference",
        "reader_visibility": "reference",
        "current_truth": 1,
        "bucket": "runbook",
        "confidence": "high",
        "rationale": "Specific operational runbook; keep as reference rather than primary operations chapter.",
    },
    "operations/demo-operations.md": {
        "decision_code": "migrate_current",
        "target_path": "docs/operations/demo-operations.md",
        "target_kind": "current_chapter",
        "reader_visibility": "primary",
        "current_truth": 1,
        "bucket": "current-chapter",
        "confidence": "high",
        "rationale": "Authoritative operations chapter for the permanent demo operating model.",
    },
    "operations/deployment-topology.md": {
        "decision_code": "migrate_current",
        "target_path": "docs/operations/deployment-topology.md",
        "target_kind": "current_chapter",
        "reader_visibility": "primary",
        "current_truth": 1,
        "bucket": "current-chapter",
        "confidence": "high",
        "rationale": "Authoritative deployment topology chapter; belongs in the operations reader flow.",
    },
    "operations/incident-and-change-management.md": {
        "decision_code": "migrate_current",
        "target_path": "docs/operations/incident-and-change-management.md",
        "target_kind": "current_chapter",
        "reader_visibility": "primary",
        "current_truth": 1,
        "bucket": "current-chapter",
        "confidence": "high",
        "rationale": "Authoritative incident/change management chapter; belongs in the operations reader flow.",
    },
    "overview/structural-differentiators.md": {
        "decision_code": "migrate_current",
        "target_path": "docs/overview/structural-differentiators.md",
        "target_kind": "current_chapter",
        "reader_visibility": "primary",
        "current_truth": 0,
        "bucket": "current-informative",
        "confidence": "high",
        "rationale": "Informative overview narrative derived from Foundation; include in primary flow but do not mark as authoritative truth.",
    },
}


def latest_run_id(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT run_id FROM inventory_runs WHERE run_kind='source_inventory' AND status='completed' ORDER BY run_id DESC LIMIT 1"
    ).fetchone()
    if not row:
        raise SystemExit("no completed source inventory run found")
    return int(row[0])


def undecided_rows(conn: sqlite3.Connection, run_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
          sd.source_doc_id,
          sd.rel_path,
          sd.abs_path,
          sd.title,
          sd.top_level_dir,
          sd.line_count,
          sd.frontmatter_status,
          sd.frontmatter_authority,
          md.decision_id,
          md.target_path
        FROM migration_decisions md
        JOIN source_documents sd ON sd.source_doc_id = md.source_doc_id
        WHERE sd.run_id = ?
          AND md.decision_code = 'undecided'
        ORDER BY sd.rel_path
        """,
        (run_id,),
    ).fetchall()


def read_text(path: str) -> str:
    source = Path(path)
    if not source.exists():
        return ""
    return source.read_text(encoding="utf-8", errors="replace")


def first_heading(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


def slug_terms(rel_path: str, title: str | None, heading: str | None) -> set[str]:
    blob = " ".join(part for part in [rel_path, title, heading] if part).lower()
    return {term for term in re.split(r"[^a-z0-9]+", blob) if term}


def safe_suffix(rel_path: str, strip_prefix: str) -> str:
    rel = Path(rel_path.replace("\\", "/"))
    parts = rel.parts
    if parts and parts[0] == strip_prefix:
        parts = parts[1:]
    return "/".join(parts)


def evidence_target(rel_path: str) -> str:
    top = rel_path.split("/", 1)[0]
    suffix = safe_suffix(rel_path, top)
    return f"docs/evidence/work-records/{top}/{suffix}"


def reference_target(rel_path: str) -> str:
    top = rel_path.split("/", 1)[0]
    suffix = safe_suffix(rel_path, top)
    return f"docs/reference/technical-notes/{top}/{suffix}"


def archive_target(rel_path: str) -> str:
    return f"docs/archive/{rel_path}"


def decide(row: sqlite3.Row) -> dict[str, object]:
    rel_path = row["rel_path"]
    file_name = Path(rel_path).name
    top = row["top_level_dir"]
    text = read_text(row["abs_path"])
    heading = first_heading(text)
    if rel_path in MANUAL_OVERRIDES:
        decision = dict(MANUAL_OVERRIDES[rel_path])
        decision["heading"] = heading
        return decision
    terms = slug_terms(rel_path, row["title"], heading)
    lower = rel_path.lower()
    title_blob = " ".join(part for part in [row["title"], heading] if part).lower()
    has_date = bool(DATE_RE.search(rel_path))
    is_work_record = bool(terms & WORK_RECORD_TERMS) or "metric-work-records/" in lower
    is_reference = bool(terms & REFERENCE_TERMS)

    if lower.endswith("_template.md"):
        return {
            "decision_code": "reject_do_not_migrate",
            "target_path": None,
            "target_kind": "retired_not_migrated",
            "reader_visibility": "hidden",
            "current_truth": 0,
            "bucket": "template",
            "confidence": "high",
            "rationale": "Template file is not documentation content for v4.",
            "heading": heading,
        }

    if "historical-plans/" in lower:
        return {
            "decision_code": "archive_only",
            "target_path": archive_target(rel_path),
            "target_kind": "archive_only",
            "reader_visibility": "archive",
            "current_truth": 0,
            "bucket": "historical-plan",
            "confidence": "high",
            "rationale": "Historical plan retained only as non-current archive material.",
            "heading": heading,
        }

    if top == "onboarding" and file_name in SUPERSEDED_ONBOARDING:
        return {
            "decision_code": "archive_only",
            "target_path": archive_target(rel_path),
            "target_kind": "archive_only",
            "reader_visibility": "archive",
            "current_truth": 0,
            "bucket": "superseded-onboarding",
            "confidence": "medium",
            "rationale": SUPERSEDED_ONBOARDING[file_name],
            "heading": heading,
        }

    if "metric-work-records/" in lower:
        return {
            "decision_code": "migrate_evidence",
            "target_path": evidence_target(rel_path),
            "target_kind": "evidence_work_record",
            "reader_visibility": "evidence",
            "current_truth": 0,
            "bucket": "metric-work-record",
            "confidence": "high",
            "rationale": "Metric work-record material is dated execution evidence, not reader-flow truth.",
            "heading": heading,
        }

    if has_date or is_work_record:
        return {
            "decision_code": "migrate_evidence",
            "target_path": evidence_target(rel_path),
            "target_kind": "evidence_work_record",
            "reader_visibility": "evidence",
            "current_truth": 0,
            "bucket": "dated-or-execution-work-record",
            "confidence": "high" if has_date else "medium",
            "rationale": "Dated or execution-specific implementation material belongs in evidence work records.",
            "heading": heading,
        }

    if is_reference and top in {"implementation", "operating-model", "onboarding"}:
        confidence = "medium"
        if any(term in title_blob for term in ["requirements", "doctrine", "first principles", "golden path"]):
            confidence = "high"
        return {
            "decision_code": "migrate_reference",
            "target_path": reference_target(rel_path),
            "target_kind": "curated_reference",
            "reader_visibility": "reference",
            "current_truth": 0,
            "bucket": "technical-note",
            "confidence": confidence,
            "rationale": "Durable technical note kept as reference, not promoted into primary navigation.",
            "heading": heading,
        }

    return {
        "decision_code": "archive_only",
        "target_path": archive_target(rel_path),
        "target_kind": "archive_only",
        "reader_visibility": "archive",
        "current_truth": 0,
        "bucket": "archive-fallback",
        "confidence": "low",
        "rationale": "No reliable signal for current/reference/evidence promotion; retain as archive pending future review.",
        "heading": heading,
    }


def update_decision(conn: sqlite3.Connection, row: sqlite3.Row, decision: dict[str, object]) -> None:
    conn.execute(
        """
        UPDATE migration_decisions
        SET decision_code = ?,
            target_path = ?,
            target_kind = ?,
            reader_visibility = ?,
            current_truth = ?,
            rationale = ?,
            decided_by = ?,
            decided_at = CURRENT_TIMESTAMP
        WHERE decision_id = ?
        """,
        (
            decision["decision_code"],
            decision["target_path"],
            decision["target_kind"],
            decision["reader_visibility"],
            decision["current_truth"],
            decision["rationale"],
            REVIEWER,
            row["decision_id"],
        ),
    )


def markdown_escape(value: object) -> str:
    return str(value or "").replace("|", "\\|")


def write_report(run_id: int, dry_run: bool, decisions: list[tuple[sqlite3.Row, dict[str, object]]]) -> None:
    decision_counts = Counter(decision["decision_code"] for _, decision in decisions)
    bucket_counts = Counter(decision["bucket"] for _, decision in decisions)
    confidence_counts = Counter(decision["confidence"] for _, decision in decisions)
    lines = [
        "# Undecided Migration Review",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Inventory run: `{run_id}`",
        f"Dry run: `{dry_run}`",
        f"Rows reviewed: `{len(decisions)}`",
        "",
        "## Decision Summary",
        "",
        "| Decision | Files |",
        "|---|---|",
    ]
    for decision, count in sorted(decision_counts.items()):
        lines.append(f"| {decision} | {count} |")
    lines.extend(["", "## Buckets", "", "| Bucket | Files |", "|---|---|"])
    for bucket, count in sorted(bucket_counts.items()):
        lines.append(f"| {bucket} | {count} |")
    lines.extend(["", "## Confidence", "", "| Confidence | Files |", "|---|---|"])
    for confidence, count in sorted(confidence_counts.items()):
        lines.append(f"| {confidence} | {count} |")
    lines.extend(["", "## Full Review Table", "", "| Confidence | Decision | Bucket | Source | Target | Heading | Rationale |", "|---|---|---|---|---|---|---|"])
    for row, decision in decisions:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(decision["confidence"]),
                    markdown_escape(decision["decision_code"]),
                    markdown_escape(decision["bucket"]),
                    markdown_escape(row["rel_path"]),
                    markdown_escape(decision["target_path"]),
                    markdown_escape(decision["heading"] or row["title"]),
                    markdown_escape(decision["rationale"]),
                ]
            )
            + " |"
        )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="apply decisions to migration_decisions")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        run_id = latest_run_id(conn)
        rows = undecided_rows(conn, run_id)
        decisions = [(row, decide(row)) for row in rows]
        if args.apply:
            for row, decision in decisions:
                update_decision(conn, row, decision)
            conn.commit()
        write_report(run_id, not args.apply, decisions)
    print(f"reviewed={len(decisions)} apply={args.apply}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
