#!/usr/bin/env python3
"""Populate first-pass migration decisions from the latest v3 inventory."""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
CLASSIFIER = "classifier-v0.1"

CANONICAL_CHAPTERS = {
    "overview": {
        "platform-overview.md",
    },
    "foundation": {
        "foundation-overview.md",
        "the-problem.md",
        "the-solution.md",
        "the-invariants.md",
        "the-object-model.md",
        "the-contract-grammar.md",
        "the-evaluation-boundaries.md",
        "the-authority-model.md",
        "the-dual-layer-interaction-model.md",
        "the-governed-selection.md",
    },
    "operating-model": {
        "operating-model-overview.md",
        "sources-and-the-catalog.md",
        "business-vocabulary.md",
        "contract-chain-assembly.md",
        "quality-gates-and-chain-integrity.md",
        "connectors-and-readers.md",
        "admission-and-observation.md",
        "canonical-evaluation.md",
        "metric-evaluation.md",
        "metric-catalog.md",
        "action-evaluation.md",
        "evidence-and-lineage.md",
        "tenancy-and-binding.md",
        "tenant-extensions-and-overrides.md",
        "tenant-entitlement-enforcement.md",
        "fiscal-time-and-temporal-gates.md",
        "chain-completeness-and-verdict.md",
        "metric-management-system.md",
        "mcf-legacy-bridge.md",
        "source-change-classification.md",
    },
    "implementation": {
        "implementation-overview.md",
        "architecture.md",
        "backend-services.md",
        "internal-modules.md",
        "auxiliary-services.md",
        "infrastructure.md",
        "data-model-and-schema.md",
        "api-surface.md",
        "frontend-experience.md",
        "notifications-and-webhooks.md",
        "audit-and-activity-logging.md",
        "synthetic-data-and-testing.md",
        "business-concept-registry.md",
    },
    "ai": {
        "ai-overview.md",
        "ai-architecture.md",
        "bedrock-and-inference-profiles.md",
        "ai-agents.md",
        "ai-gates.md",
        "ai-trust-and-verification.md",
        "ai-usage-visibility.md",
    },
    "development": {
        "development-overview.md",
        "devhub.md",
        "decision-and-change-procedure.md",
        "build-and-release.md",
        "quality-assurance.md",
        "documentation-system.md",
        "developer-experience.md",
        "metric-readiness-toolkit.md",
    },
    "onboarding": {
        "onboarding-overview.md",
        "source-registration.md",
        "seed-catalog-management.md",
        "metric-workstream.md",
        "business-field-and-business-object-onboarding.md",
        "canonical-field-seeding.md",
        "source-and-admission-contract-creation.md",
        "observation-contract-creation.md",
        "canonical-contract-creation.md",
        "tenant-metric-binding.md",
        "reader-creation.md",
        "multi-standard-onboarding.md",
        "tenant-onboarding.md",
    },
    "operations": {
        "operations-overview.md",
        "tenant-lifecycle-and-subscription.md",
        "security-operations.md",
        "upgrade-and-migration.md",
        "observability-and-telemetry.md",
        "performance-and-scale.md",
        "support-and-escalation.md",
        "runtime-runbook.md",
        "runtime-operations.md",
    },
    "compliance": {
        "compliance-overview.md",
        "infosec-and-access-control.md",
        "iso-27001-conformance.md",
        "soc-2-conformance.md",
        "privacy-and-the-immutable-fact.md",
        "risk-and-vendor-management.md",
    },
}


def latest_run_id(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT run_id FROM inventory_runs WHERE run_kind='source_inventory' AND status='completed' ORDER BY run_id DESC LIMIT 1"
    ).fetchone()
    if not row:
        raise SystemExit("no completed source inventory run found")
    return int(row[0])


def is_retired_or_superseded(status: str | None, authority: str | None) -> bool:
    blob = " ".join(part for part in [status, authority] if part).lower()
    return any(token in blob for token in ["superseded", "retired", "reversed", "abandoned"])


def evidence_subdir(kind: str) -> tuple[str, str]:
    if kind == "evidence_dbcp":
        return "dbcp", "evidence_dbcp"
    if kind == "evidence_closeout":
        return "closeouts", "evidence_closeout"
    if kind == "evidence_audit":
        return "audits", "evidence_audit"
    if kind == "evidence_ledger":
        return "ledgers", "evidence_ledger"
    return "work-records", "evidence_work_record"


def classify(row: sqlite3.Row) -> dict[str, object]:
    rel_path = row["rel_path"]
    file_name = Path(rel_path).name
    top = row["top_level_dir"]
    kind = row["guessed_kind"]
    status = row["frontmatter_status"]
    authority = row["frontmatter_authority"]
    retired = is_retired_or_superseded(status, authority)

    if rel_path == "operations/metric-onboarding-case-book.md":
        return {
            "decision_code": "migrate_evidence",
            "target_path": "docs/evidence/work-records/operations/metric-onboarding-case-book.md",
            "target_kind": "evidence_work_record",
            "reader_visibility": "evidence",
            "current_truth": 0,
            "rationale": "Living metric-onboarding case register is evidence/work-record material, not primary Operations doctrine.",
        }

    if rel_path == "source-systems/sap-licensing-reference.md":
        return {
            "decision_code": "migrate_reference",
            "target_path": "docs/reference/source-systems/sap-licensing-reference.md",
            "target_kind": "source_system_reference",
            "reader_visibility": "reference",
            "current_truth": 0,
            "rationale": "SAP licensing appendix is vendor/legal context that must be verified during onboarding, not current truth.",
        }

    if file_name in CANONICAL_CHAPTERS.get(top, set()):
        return {
            "decision_code": "migrate_current",
            "target_path": f"docs/{top}/{file_name}",
            "target_kind": "current_chapter",
            "reader_visibility": "primary",
            "current_truth": 0 if retired else 1,
            "rationale": "Canonical reader-flow chapter candidate.",
        }

    if kind == "adr":
        return {
            "decision_code": "migrate_governance",
            "target_path": f"docs/governance/adrs/{file_name}",
            "target_kind": "adr",
            "reader_visibility": "governance",
            "current_truth": 0 if retired else 1,
            "rationale": "ADR files are governance records; superseded/retired records remain governance history, not current truth.",
        }

    if kind == "errata":
        return {
            "decision_code": "migrate_governance",
            "target_path": f"docs/governance/errata/{file_name}",
            "target_kind": "errata",
            "reader_visibility": "governance",
            "current_truth": 0 if retired else 1,
            "rationale": "Errata are governance records and must move with provenance.",
        }

    if kind == "source_system_reference":
        return {
            "decision_code": "migrate_reference",
            "target_path": f"docs/reference/source-systems/{file_name}",
            "target_kind": "source_system_reference",
            "reader_visibility": "reference",
            "current_truth": 0 if retired else 1,
            "rationale": "Source-system pages are curated reference material; preserve separately from reader-flow chapters.",
        }

    if kind == "generated_or_curated_reference":
        if top in {"api", "schemas", "data-dictionary"}:
            return {
                "decision_code": "regenerate_from_source",
                "target_path": f"docs/reference/{top}/{file_name}",
                "target_kind": "generated_reference",
                "reader_visibility": "hidden",
                "current_truth": 0,
                "rationale": "Generated references must be rebuilt from current source, not copied from stale v3 output.",
            }
        if top == "glossary":
            return {
                "decision_code": "migrate_reference",
                "target_path": f"docs/reference/glossary/{file_name}",
                "target_kind": "curated_reference",
                "reader_visibility": "reference",
                "current_truth": 0 if retired else 1,
                "rationale": "Glossary is curated reference material.",
            }
        return {
            "decision_code": "undecided",
            "target_path": f"docs/reference/{top}/{file_name}",
            "target_kind": "curated_reference",
            "reader_visibility": "hidden",
            "current_truth": 0,
            "rationale": "Reference-like file needs review before migration.",
        }

    if kind.startswith("evidence_"):
        subdir, target_kind = evidence_subdir(kind)
        return {
            "decision_code": "migrate_evidence",
            "target_path": f"docs/evidence/{subdir}/{top}/{file_name}",
            "target_kind": target_kind,
            "reader_visibility": "evidence",
            "current_truth": 0,
            "rationale": "Dated execution/governance evidence is preserved outside the main reader flow.",
        }

    if kind == "current_chapter_candidate":
        return {
            "decision_code": "undecided",
            "target_path": f"docs/archive/{top}/{file_name}",
            "target_kind": "archive_only",
            "reader_visibility": "hidden",
            "current_truth": 0,
            "rationale": "Located in a reader-flow folder but not in the canonical chapter allowlist; requires review before promotion.",
        }

    return {
        "decision_code": "archive_only",
        "target_path": f"docs/archive/{rel_path}",
        "target_kind": "archive_only",
        "reader_visibility": "archive",
        "current_truth": 0,
        "rationale": "Not part of current navigation or governed reference categories.",
    }


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        run_id = latest_run_id(conn)
        docs = conn.execute(
            "SELECT * FROM source_documents WHERE run_id = ? ORDER BY rel_path",
            (run_id,),
        ).fetchall()
        doc_ids = [int(row["source_doc_id"]) for row in docs]
        if doc_ids:
            placeholders = ",".join("?" for _ in doc_ids)
            conn.execute(
                f"DELETE FROM migration_decisions WHERE decided_by = ? AND source_doc_id IN ({placeholders})",
                [CLASSIFIER, *doc_ids],
            )
        insert = conn.cursor()
        inserted = 0
        skipped_manual = 0
        for row in docs:
            existing = conn.execute(
                "SELECT decision_id FROM migration_decisions WHERE source_doc_id = ?",
                (row["source_doc_id"],),
            ).fetchone()
            if existing:
                skipped_manual += 1
                continue
            decision = classify(row)
            insert.execute(
                """
                INSERT INTO migration_decisions(
                  source_doc_id, decision_code, target_path, target_kind, reader_visibility,
                  current_truth, rationale, decided_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["source_doc_id"],
                    decision["decision_code"],
                    decision["target_path"],
                    decision["target_kind"],
                    decision["reader_visibility"],
                    decision["current_truth"],
                    decision["rationale"],
                    CLASSIFIER,
                ),
            )
            inserted += 1
        conn.commit()
    print(f"classified run {run_id}: inserted={inserted}, skipped_manual={skipped_manual}")


if __name__ == "__main__":
    main()
