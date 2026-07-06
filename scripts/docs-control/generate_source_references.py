#!/usr/bin/env python3
"""Generate source-derived reference docs from the bc-core inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "source-reference-generation-report.md"
DEFAULT_CORE_ROOT = Path("C:/MyProjects/bc-core")
GENERATOR_NAME = "generate_source_references.py"
GENERATOR_VERSION = "0.1.0"

HTTP_DECORATORS = {
    "Get": "GET",
    "Post": "POST",
    "Put": "PUT",
    "Patch": "PATCH",
    "Delete": "DELETE",
    "Options": "OPTIONS",
    "Head": "HEAD",
}

DATA_DICTIONARY_DOMAINS = [
    "admin",
    "contract",
    "envelope",
    "evidence",
    "execution",
    "fact",
    "infrastructure",
    "master",
    "metric",
    "operations",
    "organization",
    "pricing",
    "progression",
    "runtime",
    "source",
    "support",
    "tenant",
    "tenant_dim",
    "test_bench",
    "users",
]

CODE_INDEX_TYPES = ["config", "module", "service", "script"]
CODE_INDEX_ROOT = "docs/reference/code-index"

DOMAIN_PATH_MATCHES = {
    "admin": [],
    "contract": ["src/database/schema/contract/"],
    "envelope": ["src/database/schema/envelope.ts"],
    "evidence": ["src/database/schema/evidence.ts"],
    "execution": ["src/database/schema/execution/"],
    "fact": [],
    "infrastructure": ["src/database/schema/infrastructure/"],
    "master": ["src/database/schema/master/"],
    "metric": ["src/database/schema/metric/", "src/database/schema/mcf/"],
    "operations": ["src/database/schema/operations/"],
    "organization": ["src/database/schema/tenant-db/organization/"],
    "pricing": ["src/database/schema/pricing/"],
    "progression": ["src/database/schema/progression.ts"],
    "runtime": ["src/database/schema/runtime/"],
    "source": ["src/database/schema/source/"],
    "support": ["src/database/schema/support/"],
    "tenant": [
        "src/database/schema/tenant/",
        "src/database/schema/tenant.ts",
        "src/database/schema/tenant-user.ts",
        "src/database/schema/tenant-db/",
    ],
    "tenant_dim": ["src/database/schema/tenant-db/tenant-dim/"],
    "test_bench": ["src/database/schema/test-bench/"],
    "users": ["src/database/schema/users/"],
}


@dataclass(frozen=True)
class CoverageTarget:
    coverage_target_id: int
    target_type: str
    target_path: str
    identifier: str
    fingerprint: str


@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str
    handler: str
    summary: str


@dataclass(frozen=True)
class ControllerInfo:
    target: CoverageTarget
    tag: str
    base_path: str
    roles: str
    endpoints: list[Endpoint]


@dataclass(frozen=True)
class SchemaInfo:
    target: CoverageTarget
    domain: str
    tables: list[str]
    exports: list[str]


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def slug_title(slug: str) -> str:
    return slug.replace("_", "-").replace("-", " ").title()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_commit(core_root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(core_root), "rev-parse", "--short", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def load_targets(conn: sqlite3.Connection) -> list[CoverageTarget]:
    rows = conn.execute(
        """
        SELECT coverage_target_id, target_type, target_path, COALESCE(identifier, ''), COALESCE(fingerprint, '')
        FROM coverage_targets
        WHERE repo_key = 'bc-core'
        ORDER BY target_type, target_path
        """
    ).fetchall()
    return [CoverageTarget(int(row[0]), row[1], row[2], row[3], row[4]) for row in rows]


def planned_generated_docs(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        """
        SELECT md.target_path, md.source_doc_id
        FROM migration_decisions md
        WHERE md.decision_code = 'regenerate_from_source'
          AND md.target_path IS NOT NULL
        ORDER BY md.target_path
        """
    ).fetchall()
    return {row[0]: int(row[1]) for row in rows}


def read_text(core_root: Path, target: CoverageTarget) -> str:
    path = core_root / target.target_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def first_string_arg(value: str) -> str:
    match = re.search(r"['\"]([^'\"]*)['\"]", value)
    return match.group(1) if match else ""


def parse_controller(core_root: Path, target: CoverageTarget) -> ControllerInfo:
    text = read_text(core_root, target)
    tag = first_string_arg(re.search(r"@ApiTags\(([^)]*)\)", text).group(1)) if re.search(r"@ApiTags\(([^)]*)\)", text) else ""
    base_path = first_string_arg(re.search(r"@Controller\(([^)]*)\)", text).group(1)) if re.search(r"@Controller\(([^)]*)\)", text) else ""
    roles = first_string_arg(re.search(r"@Roles\(([^)]*)\)", text).group(1)) if re.search(r"@Roles\(([^)]*)\)", text) else ""
    endpoints: list[Endpoint] = []
    pending_method: tuple[str, str] | None = None
    pending_summary = ""
    for line in text.splitlines():
        stripped = line.strip()
        route_match = re.match(r"@(Get|Post|Put|Patch|Delete|Options|Head)\(([^)]*)\)", stripped)
        if route_match:
            pending_method = (HTTP_DECORATORS[route_match.group(1)], first_string_arg(route_match.group(2)))
            pending_summary = ""
            continue
        summary_match = re.search(r"@ApiOperation\(\{\s*summary:\s*['\"]([^'\"]+)['\"]", stripped)
        if summary_match:
            pending_summary = summary_match.group(1)
            continue
        method_match = re.match(r"(?:async\s+)?([A-Za-z0-9_]+)\s*\(", stripped)
        if pending_method and method_match:
            method, route = pending_method
            full_path = "/".join(part.strip("/") for part in [base_path, route] if part.strip("/"))
            endpoints.append(Endpoint(method, "/" + full_path if full_path else "/", method_match.group(1), pending_summary))
            pending_method = None
            pending_summary = ""
    return ControllerInfo(target, tag, base_path, roles, endpoints)


def schema_domain(path: str) -> str:
    prefix = "src/database/schema/"
    if not path.startswith(prefix):
        return "unknown"
    rest = path.removeprefix(prefix)
    parts = rest.split("/")
    if len(parts) == 1:
        return parts[0].removesuffix(".ts")
    return parts[0]


def parse_schema(core_root: Path, target: CoverageTarget) -> SchemaInfo:
    text = read_text(core_root, target)
    tables = re.findall(r"\.table\(\s*['\"]([^'\"]+)['\"]", text)
    exports = re.findall(r"\bexport\s+const\s+([A-Za-z0-9_]+)", text)
    return SchemaInfo(target, schema_domain(target.target_path), sorted(set(tables)), sorted(set(exports)))


def frontmatter(title: str, commit: str, generated_at: str) -> str:
    return "\n".join(
        [
            "---",
            f"title: \"{title}\"",
            "type: generated-reference",
            "status: generated",
            "authority: source-derived",
            f"source_repo: bc-core",
            f"source_commit: {commit}",
            f"generated_at: {generated_at}",
            f"generator: {GENERATOR_NAME}",
            "---",
            "",
        ]
    )


def api_reference(controllers: list[ControllerInfo], commit: str, generated_at: str) -> tuple[str, str]:
    title = "API Reference"
    lines = [
        frontmatter(title, commit, generated_at),
        f"# {title}",
        "",
        "Generated from NestJS controller files in `bc-core`.",
        "",
        "## Controllers",
        "",
    ]
    lines.append("| Controller | Base Path | Tag | Roles | Endpoints | Source |")
    lines.append("|---|---|---|---|---|---|")
    for controller in controllers:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(controller.target.identifier or Path(controller.target.target_path).stem),
                    markdown_escape("/" + controller.base_path.strip("/") if controller.base_path else ""),
                    markdown_escape(controller.tag),
                    markdown_escape(controller.roles),
                    str(len(controller.endpoints)),
                    markdown_escape(controller.target.target_path),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Endpoints", ""])
    lines.append("| Method | Path | Handler | Controller | Summary |")
    lines.append("|---|---|---|---|---|")
    for controller in controllers:
        for endpoint in controller.endpoints:
            lines.append(
                "| "
                + " | ".join(
                    [
                        endpoint.method,
                        markdown_escape(endpoint.path),
                        markdown_escape(endpoint.handler),
                        markdown_escape(controller.target.identifier or Path(controller.target.target_path).stem),
                        markdown_escape(endpoint.summary),
                    ]
                )
                + " |"
            )
    return title, "\n".join(lines) + "\n"


def schemas_reference(schemas: list[SchemaInfo], commit: str, generated_at: str) -> tuple[str, str]:
    title = "Schema Reference"
    by_domain: dict[str, list[SchemaInfo]] = defaultdict(list)
    for schema in schemas:
        by_domain[schema.domain].append(schema)
    lines = [
        frontmatter(title, commit, generated_at),
        f"# {title}",
        "",
        "Generated from Drizzle schema files in `bc-core`.",
        "",
        "## Domains",
        "",
        "| Domain | Files | Tables |",
        "|---|---|---|",
    ]
    for domain in sorted(by_domain):
        files = by_domain[domain]
        table_count = sum(len(item.tables) for item in files)
        lines.append(f"| {markdown_escape(domain)} | {len(files)} | {table_count} |")
    lines.extend(["", "## Files", "", "| Domain | Source | Tables | Exports |", "|---|---|---|---|"])
    for schema in schemas:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(schema.domain),
                    markdown_escape(schema.target.target_path),
                    markdown_escape(", ".join(schema.tables) or "none detected"),
                    markdown_escape(", ".join(schema.exports[:12]) + (" ..." if len(schema.exports) > 12 else "")),
                ]
            )
            + " |"
        )
    return title, "\n".join(lines) + "\n"


def matches_domain(path: str, domain_key: str) -> bool:
    return any(path == pattern or path.startswith(pattern) for pattern in DOMAIN_PATH_MATCHES[domain_key])


def dictionary_readme(schemas: list[SchemaInfo], commit: str, generated_at: str) -> tuple[str, str]:
    title = "Data Dictionary"
    lines = [
        frontmatter(title, commit, generated_at),
        f"# {title}",
        "",
        "Generated from `bc-core/src/database/schema`.",
        "",
        "| Page | Source Files | Tables |",
        "|---|---|---|",
    ]
    for domain in DATA_DICTIONARY_DOMAINS:
        selected = [schema for schema in schemas if matches_domain(schema.target.target_path, domain)]
        tables = sum(len(schema.tables) for schema in selected)
        lines.append(f"| [{slug_title(domain)}]({domain}.md) | {len(selected)} | {tables} |")
    return title, "\n".join(lines) + "\n"


def dictionary_domain(domain: str, schemas: list[SchemaInfo], commit: str, generated_at: str) -> tuple[str, str]:
    title = f"{slug_title(domain)} Data Dictionary"
    selected = [schema for schema in schemas if matches_domain(schema.target.target_path, domain)]
    lines = [
        frontmatter(title, commit, generated_at),
        f"# {title}",
        "",
        "Generated from `bc-core/src/database/schema`.",
        "",
    ]
    if not selected:
        lines.extend(
            [
                "No matching bc-core schema files were found for this planned dictionary slice.",
                "",
                "This page remains generated so the absence is explicit and auditable.",
            ]
        )
        return title, "\n".join(lines) + "\n"
    lines.extend(["| Source | Tables | Exports |", "|---|---|---|"])
    for schema in selected:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(schema.target.target_path),
                    markdown_escape(", ".join(schema.tables) or "none detected"),
                    markdown_escape(", ".join(schema.exports[:16]) + (" ..." if len(schema.exports) > 16 else "")),
                ]
            )
            + " |"
        )
    return title, "\n".join(lines) + "\n"


def code_index_readme(targets: list[CoverageTarget], commit: str, generated_at: str) -> tuple[str, str]:
    title = "bc-core Code Index"
    by_type: dict[str, list[CoverageTarget]] = defaultdict(list)
    for target in targets:
        by_type[target.target_type].append(target)
    lines = [
        frontmatter(title, commit, generated_at),
        f"# {title}",
        "",
        "Generated from the bc-core coverage inventory.",
        "",
        "| Area | Targets | Reference |",
        "|---|---|---|",
    ]
    for target_type in CODE_INDEX_TYPES:
        label = slug_title(target_type)
        lines.append(f"| {label} | {len(by_type[target_type])} | [{label}]({target_type}.md) |")
    lines.extend(
        [
            f"| Controllers | {len(by_type['controller'])} | [API Reference](../api/README.md) |",
            f"| Schemas | {len(by_type['schema'])} | [Schema Reference](../schemas/README.md) |",
        ]
    )
    return title, "\n".join(lines) + "\n"


def code_index_type_page(
    target_type: str,
    targets: list[CoverageTarget],
    commit: str,
    generated_at: str,
) -> tuple[str, str]:
    title = f"bc-core {slug_title(target_type)} Index"
    selected = [target for target in targets if target.target_type == target_type]
    lines = [
        frontmatter(title, commit, generated_at),
        f"# {title}",
        "",
        "Generated from the bc-core coverage inventory.",
        "",
        "| Source | Identifier | Fingerprint |",
        "|---|---|---|",
    ]
    for target in selected:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(target.target_path),
                    markdown_escape(target.identifier),
                    markdown_escape(target.fingerprint[:12]),
                ]
            )
            + " |"
        )
    return title, "\n".join(lines) + "\n"


def planned_outputs(
    controllers: list[ControllerInfo],
    schemas: list[SchemaInfo],
    targets: list[CoverageTarget],
    commit: str,
    generated_at: str,
) -> dict[str, tuple[str, str, list[CoverageTarget]]]:
    outputs: dict[str, tuple[str, str, list[CoverageTarget]]] = {}
    title, text = api_reference(controllers, commit, generated_at)
    outputs["docs/reference/api/README.md"] = (title, text, [item.target for item in controllers])
    title, text = schemas_reference(schemas, commit, generated_at)
    outputs["docs/reference/schemas/README.md"] = (title, text, [item.target for item in schemas])
    title, text = dictionary_readme(schemas, commit, generated_at)
    outputs["docs/reference/data-dictionary/README.md"] = (title, text, [item.target for item in schemas])
    for domain in DATA_DICTIONARY_DOMAINS:
        title, text = dictionary_domain(domain, schemas, commit, generated_at)
        selected = [schema.target for schema in schemas if matches_domain(schema.target.target_path, domain)]
        outputs[f"docs/reference/data-dictionary/{domain}.md"] = (title, text, selected)
    title, text = code_index_readme(targets, commit, generated_at)
    outputs[f"{CODE_INDEX_ROOT}/README.md"] = (title, text, targets)
    for target_type in CODE_INDEX_TYPES:
        selected = [target for target in targets if target.target_type == target_type]
        title, text = code_index_type_page(target_type, targets, commit, generated_at)
        outputs[f"{CODE_INDEX_ROOT}/{target_type}.md"] = (title, text, selected)
    return outputs


def source_fingerprint(targets: list[CoverageTarget], commit: str) -> str:
    digest = hashlib.sha256()
    digest.update(commit.encode("utf-8"))
    for target in sorted(targets, key=lambda item: item.target_path):
        digest.update(target.target_path.encode("utf-8"))
        digest.update(target.fingerprint.encode("utf-8"))
    return digest.hexdigest()


def upsert_target_doc(
    conn: sqlite3.Connection,
    canonical_path: str,
    title: str,
    source_doc_id: int | None,
) -> int:
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
          source_doc_id
        ) VALUES (?, ?, 'generated_reference', 'reference', 'generated', 'reference', 1, ?)
        ON CONFLICT(canonical_path) DO UPDATE SET
          title = excluded.title,
          document_kind = excluded.document_kind,
          authority = excluded.authority,
          lifecycle_status = excluded.lifecycle_status,
          reader_visibility = excluded.reader_visibility,
          current_truth = excluded.current_truth,
          updated_at = CURRENT_TIMESTAMP
        """,
        (canonical_path, title, source_doc_id),
    )
    row = conn.execute("SELECT target_doc_id FROM target_documents WHERE canonical_path = ?", (canonical_path,)).fetchone()
    return int(row[0])


def upsert_generated_reference(
    conn: sqlite3.Connection,
    target_doc_id: int,
    canonical_path: str,
    commit: str,
    generated_at: str,
    fingerprint: str,
) -> None:
    reference_key = canonical_path.removeprefix("docs/reference/").removesuffix(".md").replace("/README", "")
    conn.execute(
        """
        INSERT INTO generated_references(
          target_doc_id,
          reference_key,
          source_repo_key,
          source_commit,
          generator_name,
          generator_version,
          generated_at,
          source_fingerprint,
          freshness_status,
          notes
        ) VALUES (?, ?, 'bc-core', ?, ?, ?, ?, ?, 'fresh', 'Generated during v4 clean-room build')
        ON CONFLICT(reference_key) DO UPDATE SET
          target_doc_id = excluded.target_doc_id,
          source_commit = excluded.source_commit,
          generator_name = excluded.generator_name,
          generator_version = excluded.generator_version,
          generated_at = excluded.generated_at,
          source_fingerprint = excluded.source_fingerprint,
          freshness_status = 'fresh',
          notes = excluded.notes
        """,
        (target_doc_id, reference_key, commit, GENERATOR_NAME, GENERATOR_VERSION, generated_at, fingerprint),
    )


def write_report(generated: list[str], skipped: list[str], dry_run: bool, commit: str) -> None:
    lines = [
        "# Source Reference Generation Report",
        "",
        f"Generated: `{now_iso()}`",
        f"Dry run: `{dry_run}`",
        f"bc-core commit: `{commit}`",
        f"Generated files: `{len(generated)}`",
        f"Skipped unplanned outputs: `{len(skipped)}`",
        "",
        "## Generated",
        "",
    ]
    for path in generated:
        lines.append(f"- `{path}`")
    if skipped:
        lines.extend(["", "## Skipped", ""])
        for path in skipped:
            lines.append(f"- `{path}`")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-root", default=str(DEFAULT_CORE_ROOT), help="path to bc-core")
    parser.add_argument("--apply", action="store_true", help="write generated docs and SQLite rows")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    core_root = Path(args.core_root)
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    generated_at = now_iso()
    commit = source_commit(core_root)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        targets = load_targets(conn)
        planned = planned_generated_docs(conn)
        controllers = [parse_controller(core_root, target) for target in targets if target.target_type == "controller"]
        schemas = [parse_schema(core_root, target) for target in targets if target.target_type == "schema"]
        outputs = planned_outputs(controllers, schemas, targets, commit, generated_at)
        generated: list[str] = []
        skipped: list[str] = []
        for canonical_path, (title, text, source_targets) in sorted(outputs.items()):
            additional_code_index = canonical_path.startswith(f"{CODE_INDEX_ROOT}/")
            if canonical_path not in planned and not additional_code_index:
                skipped.append(canonical_path)
                continue
            if args.apply:
                path = ROOT / canonical_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
                target_doc_id = upsert_target_doc(conn, canonical_path, title, planned.get(canonical_path))
                upsert_generated_reference(
                    conn,
                    target_doc_id,
                    canonical_path,
                    commit,
                    generated_at,
                    source_fingerprint(source_targets, commit),
                )
            generated.append(canonical_path)
        if args.apply:
            conn.commit()
    write_report(generated, skipped, not args.apply, commit)
    print(f"generated={len(generated)} skipped={len(skipped)} apply={args.apply}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
