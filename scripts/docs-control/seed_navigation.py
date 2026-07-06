#!/usr/bin/env python3
"""Seed reader navigation from imported v4 target documents."""
from __future__ import annotations

import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
NAV_DOC_PATH = ROOT / "docs" / "NAVIGATION.md"
REPORT_PATH = ROOT / "docs-control" / "reports" / "navigation-report.md"

NAV_SECTIONS = [
    (
        "overview",
        "overview",
        [
        "platform-overview.md",
        "structural-differentiators.md",
        ],
    ),
    (
        "foundation",
        "foundation",
        [
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
        ],
    ),
    (
        "operating_model",
        "operating-model",
        [
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
        "metric-management-system-recovery-track.md",
        "mcf-legacy-bridge.md",
            "source-change-classification.md",
        ],
    ),
    (
        "implementation",
        "implementation",
        [
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
        ],
    ),
    (
        "ai",
        "ai",
        [
            "ai-overview.md",
            "ai-architecture.md",
            "bedrock-and-inference-profiles.md",
            "ai-agents.md",
            "ai-gates.md",
            "ai-trust-and-verification.md",
            "ai-usage-visibility.md",
        ],
    ),
    (
        "development",
        "development",
        [
            "development-overview.md",
            "devhub.md",
            "decision-and-change-procedure.md",
            "build-and-release.md",
            "quality-assurance.md",
            "documentation-system.md",
            "developer-experience.md",
            "metric-readiness-toolkit.md",
        ],
    ),
    (
        "onboarding",
        "onboarding",
        [
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
        ],
    ),
    (
        "operations",
        "operations",
        [
        "operations-overview.md",
        "demo-operations.md",
        "tenant-lifecycle-and-subscription.md",
        "security-operations.md",
        "deployment-topology.md",
        "incident-and-change-management.md",
        "upgrade-and-migration.md",
            "observability-and-telemetry.md",
            "performance-and-scale.md",
            "support-and-escalation.md",
            "runtime-runbook.md",
            "runtime-operations.md",
        ],
    ),
    (
        "compliance",
        "compliance",
        [
            "compliance-overview.md",
            "infosec-and-access-control.md",
            "iso-27001-conformance.md",
            "soc-2-conformance.md",
            "privacy-and-the-immutable-fact.md",
            "risk-and-vendor-management.md",
        ],
    ),
]


def collection_ids(conn: sqlite3.Connection) -> dict[str, int]:
    return {
        row["collection_key"]: int(row["collection_id"])
        for row in conn.execute("SELECT collection_id, collection_key FROM reader_collections")
    }


def target(conn: sqlite3.Connection, canonical_path: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT target_doc_id, title, canonical_path FROM target_documents WHERE canonical_path = ?",
        (canonical_path,),
    ).fetchone()


def all_targets(conn: sqlite3.Connection, prefix: str, document_kind: str | None = None) -> list[sqlite3.Row]:
    params: list[object] = [f"{prefix}%"]
    kind_clause = ""
    if document_kind:
        kind_clause = " AND document_kind = ?"
        params.append(document_kind)
    return conn.execute(
        f"""
        SELECT target_doc_id, title, canonical_path, document_kind
        FROM target_documents
        WHERE canonical_path LIKE ?
          {kind_clause}
        ORDER BY canonical_path
        """,
        params,
    ).fetchall()


def add_item(
    conn: sqlite3.Connection,
    collections: dict[str, int],
    collection_key: str,
    label: str,
    sort_order: int,
    target_doc_id: int | None = None,
    parent_nav_item_id: int | None = None,
    visibility: str = "visible",
    notes: str | None = None,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO reader_nav_items(
          collection_id,
          parent_nav_item_id,
          target_doc_id,
          label,
          sort_order,
          visibility,
          notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            collections[collection_key],
            parent_nav_item_id,
            target_doc_id,
            label,
            sort_order,
            visibility,
            notes,
        ),
    )
    return int(cursor.lastrowid)


def doc_link(canonical_path: str) -> str:
    path = canonical_path.removeprefix("docs/")
    return path.replace("\\", "/")


def seed_primary_flow(conn: sqlite3.Connection, collections: dict[str, int]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for collection_key, folder, files in NAV_SECTIONS:
        for index, file_name in enumerate(files, start=1):
            path = f"docs/{folder}/{file_name}"
            row = target(conn, path)
            if not row:
                add_item(
                    conn,
                    collections,
                    collection_key,
                    file_name.removesuffix(".md").replace("-", " ").title(),
                    index * 10,
                    visibility="planned",
                    notes=f"Missing target document: {path}",
                )
                counts["planned"] += 1
                continue
            add_item(
                conn,
                collections,
                collection_key,
                row["title"],
                index * 10,
                target_doc_id=int(row["target_doc_id"]),
                visibility="visible",
            )
            counts["visible"] += 1
    return counts


def seed_reference(conn: sqlite3.Connection, collections: dict[str, int]) -> Counter[str]:
    counts: Counter[str] = Counter()
    glossary = target(conn, "docs/reference/glossary/README.md")
    if glossary:
        add_item(conn, collections, "reference", "Glossary", 10, target_doc_id=int(glossary["target_doc_id"]))
        counts["visible"] += 1
    generated_parent = add_item(conn, collections, "reference", "Generated References", 20)
    api = target(conn, "docs/reference/api/README.md")
    if api:
        add_item(
            conn,
            collections,
            "reference",
            "API Reference",
            10,
            target_doc_id=int(api["target_doc_id"]),
            parent_nav_item_id=generated_parent,
            visibility="visible",
        )
        counts["visible"] += 1
    data_dictionary = target(conn, "docs/reference/data-dictionary/README.md")
    data_dictionary_parent = generated_parent
    if data_dictionary:
        data_dictionary_parent = add_item(
            conn,
            collections,
            "reference",
            "Data Dictionary",
            20,
            target_doc_id=int(data_dictionary["target_doc_id"]),
            parent_nav_item_id=generated_parent,
            visibility="visible",
        )
        counts["visible"] += 1
    for index, row in enumerate(all_targets(conn, "docs/reference/data-dictionary/"), start=1):
        if row["canonical_path"].endswith("/README.md"):
            continue
        add_item(
            conn,
            collections,
            "reference",
            row["title"],
            index * 10,
            target_doc_id=int(row["target_doc_id"]),
            parent_nav_item_id=data_dictionary_parent,
            visibility="visible",
        )
        counts["visible"] += 1
    schemas = target(conn, "docs/reference/schemas/README.md")
    if schemas:
        add_item(
            conn,
            collections,
            "reference",
            "Schema Reference",
            30,
            target_doc_id=int(schemas["target_doc_id"]),
            parent_nav_item_id=generated_parent,
            visibility="visible",
        )
        counts["visible"] += 1
    code_index = target(conn, "docs/reference/code-index/README.md")
    code_index_parent = generated_parent
    if code_index:
        code_index_parent = add_item(
            conn,
            collections,
            "reference",
            "Code Index",
            40,
            target_doc_id=int(code_index["target_doc_id"]),
            parent_nav_item_id=generated_parent,
            visibility="visible",
        )
        counts["visible"] += 1
    for index, row in enumerate(all_targets(conn, "docs/reference/code-index/"), start=1):
        if row["canonical_path"].endswith("/README.md"):
            continue
        add_item(
            conn,
            collections,
            "reference",
            row["title"],
            index * 10,
            target_doc_id=int(row["target_doc_id"]),
            parent_nav_item_id=code_index_parent,
            visibility="visible",
        )
        counts["visible"] += 1
    technical_parent = add_item(conn, collections, "reference", "Technical Notes", 30)
    for index, row in enumerate(all_targets(conn, "docs/reference/technical-notes/"), start=1):
        add_item(
            conn,
            collections,
            "reference",
            row["title"],
            index * 10,
            target_doc_id=int(row["target_doc_id"]),
            parent_nav_item_id=technical_parent,
            visibility="visible",
        )
        counts["visible"] += 1
    runbook_parent = add_item(conn, collections, "reference", "Runbooks", 40)
    for index, row in enumerate(all_targets(conn, "docs/reference/runbooks/"), start=1):
        add_item(
            conn,
            collections,
            "reference",
            row["title"],
            index * 10,
            target_doc_id=int(row["target_doc_id"]),
            parent_nav_item_id=runbook_parent,
            visibility="visible",
        )
        counts["visible"] += 1
    source_parent = add_item(conn, collections, "reference", "Source Systems", 50)
    for index, row in enumerate(all_targets(conn, "docs/reference/source-systems/"), start=1):
        add_item(
            conn,
            collections,
            "reference",
            row["title"],
            index * 10,
            target_doc_id=int(row["target_doc_id"]),
            parent_nav_item_id=source_parent,
            visibility="visible",
        )
        counts["visible"] += 1
    return counts


def seed_governance(conn: sqlite3.Connection, collections: dict[str, int]) -> Counter[str]:
    counts: Counter[str] = Counter()
    adr_parent = add_item(conn, collections, "governance", "ADRs", 10)
    errata_parent = add_item(conn, collections, "governance", "Errata", 20)
    for index, row in enumerate(all_targets(conn, "docs/governance/adrs/"), start=1):
        visibility = "visible" if row["canonical_path"].endswith("/README.md") else "hidden"
        add_item(
            conn,
            collections,
            "governance",
            row["title"],
            index * 10,
            target_doc_id=int(row["target_doc_id"]),
            parent_nav_item_id=adr_parent,
            visibility=visibility,
        )
        counts[visibility] += 1
    for index, row in enumerate(all_targets(conn, "docs/governance/errata/"), start=1):
        add_item(
            conn,
            collections,
            "governance",
            row["title"],
            index * 10,
            target_doc_id=int(row["target_doc_id"]),
            parent_nav_item_id=errata_parent,
            visibility="hidden",
        )
        counts["hidden"] += 1
    return counts


def seed_evidence(conn: sqlite3.Connection, collections: dict[str, int]) -> Counter[str]:
    counts: Counter[str] = Counter()
    groups = [
        ("DBCPs", "docs/evidence/dbcp/"),
        ("Closeouts", "docs/evidence/closeouts/"),
        ("Audits", "docs/evidence/audits/"),
        ("Ledgers", "docs/evidence/ledgers/"),
        ("Work Records", "docs/evidence/work-records/"),
    ]
    for group_index, (label, prefix) in enumerate(groups, start=1):
        parent = add_item(conn, collections, "evidence", label, group_index * 10)
        for index, row in enumerate(all_targets(conn, prefix), start=1):
            add_item(
                conn,
                collections,
                "evidence",
                row["title"],
                index * 10,
                target_doc_id=int(row["target_doc_id"]),
                parent_nav_item_id=parent,
                visibility="hidden",
            )
            counts["hidden"] += 1
    return counts


def visible_rows(conn: sqlite3.Connection, collection_key: str) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
          ni.label,
          ni.visibility,
          td.canonical_path,
          ni.parent_nav_item_id,
          ni.sort_order,
          parent.label AS parent_label
        FROM reader_nav_items ni
        JOIN reader_collections rc ON rc.collection_id = ni.collection_id
        LEFT JOIN target_documents td ON td.target_doc_id = ni.target_doc_id
        LEFT JOIN reader_nav_items parent ON parent.nav_item_id = ni.parent_nav_item_id
        WHERE rc.collection_key = ?
          AND ni.visibility = 'visible'
        ORDER BY COALESCE(parent.sort_order, ni.sort_order), ni.parent_nav_item_id, ni.sort_order
        """,
        (collection_key,),
    ).fetchall()


def planned_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT rc.collection_key, ni.label, ni.notes
        FROM reader_nav_items ni
        JOIN reader_collections rc ON rc.collection_id = ni.collection_id
        WHERE ni.visibility = 'planned'
        ORDER BY rc.sort_order, ni.sort_order
        """
    ).fetchall()


def write_navigation_doc(conn: sqlite3.Connection) -> None:
    labels = {
        "overview": "Overview",
        "foundation": "Foundation",
        "operating_model": "Operating Model",
        "implementation": "Implementation",
        "ai": "AI",
        "development": "Development",
        "onboarding": "Onboarding",
        "operations": "Operations",
        "compliance": "Compliance",
    }
    lines = [
        "# Navigation",
        "",
        "Generated from `docs-control/docs-control.db` by `scripts/docs-control/seed_navigation.py`.",
        "",
        "## Primary Reader Flow",
        "",
    ]
    for collection_key, _folder, _files in NAV_SECTIONS:
        lines.extend([f"### {labels[collection_key]}", ""])
        for row in visible_rows(conn, collection_key):
            if row["canonical_path"]:
                lines.append(f"- [{row['label']}]({doc_link(row['canonical_path'])})")
            else:
                lines.append(f"- {row['label']}")
        lines.append("")

    planned = planned_rows(conn)
    if planned:
        lines.extend(["## Planned Gaps", ""])
        for row in planned:
            note = f" - {row['notes']}" if row["notes"] else ""
            lines.append(f"- `{row['collection_key']}`: {row['label']}{note}")
        lines.append("")

    lines.extend(["## Reference", ""])
    glossary = target(conn, "docs/reference/glossary/README.md")
    if glossary:
        lines.append(f"- [Glossary]({doc_link(glossary['canonical_path'])})")
    lines.extend(["", "### Generated References", ""])
    api = target(conn, "docs/reference/api/README.md")
    if api:
        lines.append(f"- [API Reference]({doc_link(api['canonical_path'])})")
    schemas = target(conn, "docs/reference/schemas/README.md")
    if schemas:
        lines.append(f"- [Schema Reference]({doc_link(schemas['canonical_path'])})")
    code_index = target(conn, "docs/reference/code-index/README.md")
    if code_index:
        lines.append(f"- [Code Index]({doc_link(code_index['canonical_path'])})")
    data_dictionary = target(conn, "docs/reference/data-dictionary/README.md")
    if data_dictionary:
        lines.append(f"- [Data Dictionary]({doc_link(data_dictionary['canonical_path'])})")
    lines.extend(["", "### Code Index", ""])
    for row in all_targets(conn, "docs/reference/code-index/"):
        if row["canonical_path"].endswith("/README.md"):
            continue
        lines.append(f"- [{row['title']}]({doc_link(row['canonical_path'])})")
    lines.extend(["", "### Data Dictionary", ""])
    for row in all_targets(conn, "docs/reference/data-dictionary/"):
        if row["canonical_path"].endswith("/README.md"):
            continue
        lines.append(f"- [{row['title']}]({doc_link(row['canonical_path'])})")
    lines.extend(["", "### Technical Notes", ""])
    for row in all_targets(conn, "docs/reference/technical-notes/"):
        lines.append(f"- [{row['title']}]({doc_link(row['canonical_path'])})")
    lines.extend(["", "### Runbooks", ""])
    for row in all_targets(conn, "docs/reference/runbooks/"):
        lines.append(f"- [{row['title']}]({doc_link(row['canonical_path'])})")
    lines.extend(["", "### Source Systems", ""])
    for row in all_targets(conn, "docs/reference/source-systems/"):
        lines.append(f"- [{row['title']}]({doc_link(row['canonical_path'])})")
    lines.append("")

    lines.extend(["## Governance And Evidence", ""])
    counts = conn.execute(
        """
        SELECT document_kind, COUNT(*)
        FROM target_documents
        WHERE document_kind IN (
          'adr',
          'errata',
          'evidence_dbcp',
          'evidence_closeout',
          'evidence_work_record',
          'evidence_audit',
          'evidence_ledger'
        )
        GROUP BY document_kind
        ORDER BY document_kind
        """
    ).fetchall()
    for kind, count in counts:
        lines.append(f"- `{kind}`: {count}")
    lines.append("")
    lines.append("Governance and evidence files are preserved in the repository, but most individual records are intentionally hidden from the primary reader flow.")
    NAV_DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(conn: sqlite3.Connection, counts: Counter[str]) -> None:
    lines = [
        "# Navigation Seed Report",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Item Visibility",
        "",
        "| Visibility | Items |",
        "|---|---|",
    ]
    for key, count in sorted(counts.items()):
        lines.append(f"| {key} | {count} |")
    lines.extend(["", "## Collection Counts", "", "| Collection | Items |", "|---|---|"])
    for row in conn.execute(
        """
        SELECT rc.collection_key, COUNT(ni.nav_item_id)
        FROM reader_collections rc
        LEFT JOIN reader_nav_items ni ON ni.collection_id = rc.collection_id
        GROUP BY rc.collection_key
        ORDER BY rc.sort_order
        """
    ):
        lines.append(f"| {row[0]} | {row[1]} |")
    planned = planned_rows(conn)
    if planned:
        lines.extend(["", "## Planned Items", "", "| Collection | Item | Note |", "|---|---|---|"])
        for row in planned:
            note = str(row["notes"] or "").replace("|", "\\|")
            lines.append(f"| {row['collection_key']} | {row['label']} | {note} |")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        collections = collection_ids(conn)
        conn.execute("DELETE FROM reader_nav_items")
        counts: Counter[str] = Counter()
        counts.update(seed_primary_flow(conn, collections))
        counts.update(seed_reference(conn, collections))
        counts.update(seed_governance(conn, collections))
        counts.update(seed_evidence(conn, collections))
        write_navigation_doc(conn)
        write_report(conn, counts)
        conn.commit()
    print(f"seeded navigation: {dict(counts)}")
    print(f"wrote {NAV_DOC_PATH}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
