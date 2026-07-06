#!/usr/bin/env python3
"""Bidirectional bc-core documentation relevance and grounding audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "docs-control" / "docs-control.db"
REPORT_PATH = ROOT / "docs-control" / "reports" / "bidirectional-bc-core-audit.md"
RELEVANCE_REPORT_PATH = ROOT / "docs-control" / "reports" / "bc-core-relevance-coverage-queue.md"
DEFAULT_CORE_ROOT = Path("C:/MyProjects/bc-core")
TOOL_NAME = "audit_bidirectional_bc_core.py"
TOOL_VERSION = "0.2.0"
MAX_DEEP_PARSE_BYTES = 2_000_000

HTTP_DECORATORS = {
    "Get": "GET",
    "Post": "POST",
    "Put": "PUT",
    "Patch": "PATCH",
    "Delete": "DELETE",
    "Options": "OPTIONS",
    "Head": "HEAD",
}

EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".claude",
    ".idea",
    "node_modules",
    "dist",
    "tmp",
    "var",
    "_archives",
    "private-docs",
}

CURRENT_DOC_KINDS = {"current_chapter", "curated_reference", "source_system_reference"}

CLASS_RE = re.compile(r"\bexport\s+class\s+([A-Za-z0-9_]+)")
ANY_CLASS_RE = re.compile(r"\b(?:export\s+)?class\s+([A-Za-z0-9_]+)")
CLASS_SYMBOL_RE = re.compile(
    r"\b[A-Z][A-Za-z0-9_]*(?:Controller|Service|Module|Guard|Interceptor|Middleware|Repository|Evaluator|Reader|Writer)\b"
)
HTTP_ENDPOINT_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)\s+(/[A-Za-z0-9_./:{}*?=-]+)", re.IGNORECASE)
API_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])(/api/[A-Za-z0-9_./:{}*?=-]+)")
CODE_PATH_RE = re.compile(
    r"(?:(?:bc-core|C:[/\\]MyProjects[/\\]bc-core)[/\\])?"
    r"((?:src|docker|scripts|test|tests)[/\\][A-Za-z0-9_./\\@{}=+-]+(?:\.[A-Za-z0-9]+)?)"
    r"|(?<![A-Za-z0-9_])((?:package\.json|docker-compose\.yml|tsconfig(?:\.build|\.tools)?\.json|vitest\.config(?:\.e2e)?\.ts))"
)
ENV_RE = re.compile(r"\bprocess\.env\.([A-Z][A-Z0-9_]{2,})\b|`([A-Z][A-Z0-9_]{2,})`")
PG_TABLE_RE = re.compile(r"\b(?:pgTable|mysqlTable|sqliteTable)\(\s*['\"]([^'\"]+)['\"]")
SCHEMA_TABLE_RE = re.compile(r"\b([A-Za-z0-9_]+)\.table\(\s*['\"]([^'\"]+)['\"]")
SQL_CREATE_TABLE_RE = re.compile(r"(?im)^\s*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z0-9_.\"]+)")
CODE_SPAN_RE = re.compile(r"`([^`]+)`")


@dataclass(frozen=True)
class CodeFact:
    fact_type: str
    source_path: str
    line_number: int | None
    symbol: str
    normalized_key: str
    fact_value: str
    evidence: str
    fingerprint: str


@dataclass(frozen=True)
class DocClaim:
    target_doc_id: int
    canonical_path: str
    document_kind: str
    line_number: int
    claim_type: str
    claim_text: str
    normalized_key: str
    context: str


@dataclass(frozen=True)
class Assessment:
    claim: DocClaim
    status: str
    matched_fact: int | None
    confidence: str
    rationale: str


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_table(lines: list[str], headers: list[str], rows: list[tuple[object, ...]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        lines.append("| " + " | ".join(markdown_escape(value) for value in row) + " |")


def clip(value: str, limit: int = 220) -> str:
    value = " ".join(value.strip().split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def normalize_path(value: str) -> str:
    value = value.strip().strip("`'\".,);:]")
    value = value.replace("\\", "/")
    value = value.removeprefix("bc-core/")
    value = re.sub(r"^C:/MyProjects/bc-core/", "", value, flags=re.IGNORECASE)
    return value


def normalize_endpoint_path(value: str) -> str:
    value = value.strip().strip("`'\".,);:]")
    value = value.split("?", 1)[0]
    value = re.sub(r":([A-Za-z_][A-Za-z0-9_]*)", r"{\1}", value)
    if not value.startswith("/"):
        value = "/" + value
    value = re.sub(r"/+", "/", value)
    if len(value) > 1:
        value = value.rstrip("/")
    return value


def endpoint_key_variants(key: str) -> set[str]:
    parts = key.lower().split(" ", 1)
    if len(parts) != 2:
        return {key.lower()}
    method, path = parts
    paths = {normalize_endpoint_path(path).lower()}
    if path.startswith("/api/"):
        paths.add(normalize_endpoint_path(path[4:]).lower())
    elif path == "/api":
        paths.add("/")
    elif path != "/":
        paths.add(normalize_endpoint_path("/api" + path).lower())
    return {f"{method} {item}" for item in paths}


def route_path(global_prefix: str, base_path: str, route: str) -> str:
    parts = [global_prefix.strip("/"), base_path.strip("/"), route.strip("/")]
    joined = "/".join(part for part in parts if part)
    return normalize_endpoint_path("/" + joined if joined else "/")


def normalize_table(value: str) -> str:
    return value.strip().strip("`'\".,);:]").lower()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_commit(core_root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(core_root), "rev-parse", "--short", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def global_api_prefix(core_root: Path) -> str:
    main_path = core_root / "src" / "main.ts"
    if not main_path.exists():
        return ""
    text = main_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\bsetGlobalPrefix\(\s*['\"]([^'\"]+)['\"]", text)
    return match.group(1).strip("/") if match else ""


def line_number_for(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def should_skip(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in EXCLUDED_DIRS for part in rel_parts)


def schema_sql(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS code_facts (
          code_fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
          run_id INTEGER NOT NULL REFERENCES inventory_runs(run_id) ON DELETE CASCADE,
          repo_key TEXT NOT NULL,
          fact_type TEXT NOT NULL CHECK(fact_type IN (
            'code_path','controller','endpoint','service','module','guard','interceptor','middleware',
            'schema_table','script_command','env_var'
          )),
          source_path TEXT NOT NULL,
          line_number INTEGER,
          symbol TEXT,
          normalized_key TEXT NOT NULL,
          fact_value TEXT,
          evidence TEXT,
          fingerprint TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_code_facts_run_type ON code_facts(run_id, fact_type);
        CREATE INDEX IF NOT EXISTS idx_code_facts_repo_key ON code_facts(repo_key, normalized_key);
        CREATE INDEX IF NOT EXISTS idx_code_facts_source ON code_facts(source_path);

        CREATE TABLE IF NOT EXISTS doc_claims (
          doc_claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
          run_id INTEGER NOT NULL REFERENCES inventory_runs(run_id) ON DELETE CASCADE,
          target_doc_id INTEGER REFERENCES target_documents(target_doc_id),
          canonical_path TEXT NOT NULL,
          line_number INTEGER NOT NULL,
          claim_type TEXT NOT NULL CHECK(claim_type IN (
            'code_path','class_symbol','endpoint','endpoint_path','schema_table','env_var'
          )),
          claim_text TEXT NOT NULL,
          normalized_key TEXT NOT NULL,
          context TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_doc_claims_run_type ON doc_claims(run_id, claim_type);
        CREATE INDEX IF NOT EXISTS idx_doc_claims_path ON doc_claims(canonical_path);
        CREATE INDEX IF NOT EXISTS idx_doc_claims_key ON doc_claims(normalized_key);

        CREATE TABLE IF NOT EXISTS doc_code_assessments (
          assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
          run_id INTEGER NOT NULL REFERENCES inventory_runs(run_id) ON DELETE CASCADE,
          doc_claim_id INTEGER NOT NULL REFERENCES doc_claims(doc_claim_id) ON DELETE CASCADE,
          status TEXT NOT NULL CHECK(status IN ('grounded','ungrounded','ambiguous','out_of_scope')),
          matched_code_fact_id INTEGER REFERENCES code_facts(code_fact_id),
          confidence TEXT NOT NULL CHECK(confidence IN ('high','medium','low')),
          rationale TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_doc_code_assessments_run_status ON doc_code_assessments(run_id, status);
        CREATE INDEX IF NOT EXISTS idx_doc_code_assessments_claim ON doc_code_assessments(doc_claim_id);

        CREATE TABLE IF NOT EXISTS code_doc_assessments (
          code_doc_assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
          run_id INTEGER NOT NULL REFERENCES inventory_runs(run_id) ON DELETE CASCADE,
          code_fact_id INTEGER NOT NULL REFERENCES code_facts(code_fact_id) ON DELETE CASCADE,
          generated_claims INTEGER NOT NULL DEFAULT 0,
          current_claims INTEGER NOT NULL DEFAULT 0,
          current_grounded_claims INTEGER NOT NULL DEFAULT 0,
          coverage_depth TEXT NOT NULL CHECK(coverage_depth IN (
            'current_grounded','current_claim_unverified','generated_only','uncovered','not_required'
          )),
          relevance_priority TEXT NOT NULL CHECK(relevance_priority IN ('critical','high','medium','low','none')),
          best_doc_path TEXT,
          rationale TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_code_doc_assessments_run_depth ON code_doc_assessments(run_id, coverage_depth);
        CREATE INDEX IF NOT EXISTS idx_code_doc_assessments_fact ON code_doc_assessments(code_fact_id);
        """
    )
    conn.execute("INSERT OR REPLACE INTO schema_meta(key, value) VALUES ('schema_version', '0.2.0')")


def start_run(conn: sqlite3.Connection, core_root: Path) -> int:
    row = conn.execute("SELECT repo_id FROM repositories WHERE repo_key = 'bc-core'").fetchone()
    repo_id = int(row[0]) if row else None
    cursor = conn.execute(
        """
        INSERT INTO inventory_runs(run_kind, source_repo_id, tool_name, tool_version, status)
        VALUES ('audit', ?, ?, ?, 'running')
        """,
        (repo_id, TOOL_NAME, TOOL_VERSION),
    )
    conn.execute(
        """
        INSERT INTO repositories(repo_key, repo_name, root_path, role, active_for_cutover, notes)
        VALUES ('bc-core', 'bc-core', ?, 'codebase', 1, 'Primary backend/codebase coverage source')
        ON CONFLICT(repo_key) DO UPDATE SET
          root_path = excluded.root_path,
          role = 'codebase',
          active_for_cutover = 1
        """,
        (str(core_root),),
    )
    return int(cursor.lastrowid)


def finish_run(conn: sqlite3.Connection, run_id: int, status: str, summary: dict[str, object], error: str | None = None) -> None:
    conn.execute(
        """
        UPDATE inventory_runs
        SET completed_at = CURRENT_TIMESTAMP,
            status = ?,
            summary_json = ?,
            error_text = ?
        WHERE run_id = ?
        """,
        (status, json.dumps(summary, sort_keys=True), error, run_id),
    )


def coverage_targets(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT coverage_target_id, target_type, target_path, COALESCE(identifier, '') AS identifier, COALESCE(fingerprint, '') AS fingerprint
        FROM coverage_targets
        WHERE repo_key = 'bc-core'
        ORDER BY target_type, target_path
        """
    ).fetchall()


def first_string_arg(value: str) -> str:
    match = re.search(r"['\"]([^'\"]*)['\"]", value)
    return match.group(1) if match else ""


def class_identifier(text: str, target_type: str) -> str:
    matches = CLASS_RE.findall(text)
    preferred_suffix = {
        "controller": "Controller",
        "service": "Service",
        "module": "Module",
    }.get(target_type)
    if preferred_suffix:
        for name in matches:
            if name.endswith(preferred_suffix):
                return name
    return matches[-1] if matches else ""


def parse_controller_facts(row: sqlite3.Row, text: str, fingerprint: str, global_prefix: str) -> list[CodeFact]:
    source_path = row["target_path"]
    class_name = row["identifier"] or class_identifier(text, "controller")
    facts = [
        CodeFact("controller", source_path, 1, class_name, class_name.lower(), source_path, "controller class", fingerprint)
    ]
    base_match = re.search(r"@Controller\(([^)]*)\)", text)
    base_path = first_string_arg(base_match.group(1)) if base_match else ""
    pending_method: tuple[str, str, int] | None = None
    pending_summary = ""
    for line_offset, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        summary_match = re.search(r"@ApiOperation\(\{\s*summary:\s*['\"]([^'\"]+)['\"]", stripped)
        if summary_match:
            pending_summary = summary_match.group(1)
            continue
        route_match = re.match(r"@(Get|Post|Put|Patch|Delete|Options|Head)\(([^)]*)\)", stripped)
        if route_match:
            pending_method = (HTTP_DECORATORS[route_match.group(1)], first_string_arg(route_match.group(2)), line_offset)
            continue
        method_match = re.match(r"(?:async\s+)?([A-Za-z0-9_]+)\s*\(", stripped)
        if pending_method and method_match:
            method, route, route_line = pending_method
            endpoint_path = route_path(global_prefix, base_path, route)
            key = f"{method} {endpoint_path}".lower()
            facts.append(
                CodeFact(
                    "endpoint",
                    source_path,
                    route_line,
                    method_match.group(1),
                    key,
                    f"{method} {endpoint_path}",
                    pending_summary or f"{class_name}.{method_match.group(1)}",
                    fingerprint,
                )
            )
            pending_method = None
            pending_summary = ""
    return facts


def schema_facts_for_text(source_path: str, text: str, fingerprint: str) -> list[CodeFact]:
    facts: list[CodeFact] = []
    seen: set[str] = set()
    for regex in [PG_TABLE_RE, SQL_CREATE_TABLE_RE]:
        for match in regex.finditer(text):
            table = normalize_table(match.group(1).replace('"', ""))
            if not table or table in seen:
                continue
            seen.add(table)
            facts.append(
                CodeFact(
                    "schema_table",
                    source_path,
                    line_number_for(text, match.start()),
                    table,
                    table,
                    table,
                    "table declaration",
                    fingerprint,
                )
            )
    for match in SCHEMA_TABLE_RE.finditer(text):
        schema_name, table_name = match.groups()
        table = normalize_table(f"{schema_name}.{table_name}")
        if table in seen:
            continue
        seen.add(table)
        facts.append(
            CodeFact(
                "schema_table",
                source_path,
                line_number_for(text, match.start()),
                table,
                table,
                table,
                "schema table declaration",
                fingerprint,
            )
        )
    return facts


def env_facts_for_text(source_path: str, text: str, fingerprint: str) -> list[CodeFact]:
    facts: list[CodeFact] = []
    seen: set[str] = set()
    for match in re.finditer(r"\bprocess\.env\.([A-Z][A-Z0-9_]{2,})\b", text):
        env_name = match.group(1)
        if env_name in seen:
            continue
        seen.add(env_name)
        facts.append(
            CodeFact(
                "env_var",
                source_path,
                line_number_for(text, match.start()),
                env_name,
                env_name.lower(),
                env_name,
                "process.env reference",
                fingerprint,
            )
        )
    return facts


def collect_guard_like_facts(core_root: Path) -> list[CodeFact]:
    facts: list[CodeFact] = []
    suffix_types = {
        ".guard.ts": "guard",
        ".interceptor.ts": "interceptor",
        ".middleware.ts": "middleware",
    }
    for path in (core_root / "src").glob("**/*.ts"):
        if should_skip(path, core_root) or path.name.endswith((".spec.ts", ".test.ts")):
            continue
        fact_type = next((value for suffix, value in suffix_types.items() if path.name.endswith(suffix)), "")
        if not fact_type:
            continue
        rel = path.relative_to(core_root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        fingerprint = sha256(path)
        classes = ANY_CLASS_RE.findall(text)
        symbol = classes[-1] if classes else path.stem
        facts.append(CodeFact(fact_type, rel, 1, symbol, symbol.lower(), rel, f"{fact_type} class", fingerprint))
        facts.extend(env_facts_for_text(rel, text, fingerprint))
    return facts


def collect_script_command_facts(core_root: Path) -> list[CodeFact]:
    package_path = core_root / "package.json"
    if not package_path.exists():
        return []
    text = package_path.read_text(encoding="utf-8", errors="replace")
    fingerprint = sha256(package_path)
    try:
        package_json = json.loads(text)
    except json.JSONDecodeError:
        return []
    facts: list[CodeFact] = []
    for name, command in sorted((package_json.get("scripts") or {}).items()):
        facts.append(
            CodeFact(
                "script_command",
                "package.json",
                None,
                name,
                f"npm run {name}".lower(),
                str(command),
                "package.json script",
                fingerprint,
            )
        )
    return facts


def collect_code_facts(conn: sqlite3.Connection, core_root: Path) -> list[CodeFact]:
    facts: list[CodeFact] = []
    global_prefix = global_api_prefix(core_root)
    for row in coverage_targets(conn):
        path = core_root / row["target_path"]
        fingerprint = row["fingerprint"] or (sha256(path) if path.exists() and path.is_file() else "")
        facts.append(
            CodeFact(
                "code_path",
                row["target_path"],
                None,
                row["identifier"] or Path(row["target_path"]).name,
                normalize_path(row["target_path"]).lower(),
                row["target_type"],
                "coverage target path",
                fingerprint,
            )
        )
        if not path.exists() or not path.is_file():
            continue
        try:
            file_size = path.stat().st_size
        except OSError:
            continue
        if file_size > MAX_DEEP_PARSE_BYTES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        target_type = row["target_type"]
        if target_type == "controller":
            facts.extend(parse_controller_facts(row, text, fingerprint, global_prefix))
        elif target_type in {"service", "module"}:
            symbol = row["identifier"] or class_identifier(text, target_type)
            if symbol:
                facts.append(
                    CodeFact(target_type, row["target_path"], 1, symbol, symbol.lower(), row["target_path"], f"{target_type} class", fingerprint)
                )
        if target_type == "schema" or path.suffix.lower() == ".sql":
            facts.extend(schema_facts_for_text(row["target_path"], text, fingerprint))
        if path.suffix.lower() in {".ts", ".js", ".mjs"}:
            facts.extend(env_facts_for_text(row["target_path"], text, fingerprint))
    facts.extend(collect_guard_like_facts(core_root))
    facts.extend(collect_script_command_facts(core_root))
    deduped: dict[tuple[str, str, str], CodeFact] = {}
    for fact in facts:
        deduped.setdefault((fact.fact_type, fact.source_path, fact.normalized_key), fact)
    return list(deduped.values())


def insert_code_facts(conn: sqlite3.Connection, run_id: int, facts: list[CodeFact]) -> dict[tuple[str, str], list[int]]:
    index: dict[tuple[str, str], list[int]] = defaultdict(list)
    for fact in facts:
        cursor = conn.execute(
            """
            INSERT INTO code_facts(
              run_id, repo_key, fact_type, source_path, line_number, symbol, normalized_key, fact_value, evidence, fingerprint
            ) VALUES (?, 'bc-core', ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                fact.fact_type,
                fact.source_path,
                fact.line_number,
                fact.symbol,
                fact.normalized_key,
                fact.fact_value,
                fact.evidence,
                fact.fingerprint,
            ),
        )
        index[(fact.fact_type, fact.normalized_key)].append(int(cursor.lastrowid))
    return index


def body_lines(text: str) -> list[tuple[int, str]]:
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                start = index + 1
                break
    result: list[tuple[int, str]] = []
    in_fence = False
    for index, line in enumerate(lines[start:], start=start + 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append((index, line))
    return result


def target_docs(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT target_doc_id, canonical_path, document_kind, current_truth
        FROM target_documents
        WHERE document_kind IN ('current_chapter', 'curated_reference', 'source_system_reference')
        ORDER BY canonical_path
        """
    ).fetchall()


def extract_doc_claims(conn: sqlite3.Connection, code_facts: list[CodeFact]) -> list[DocClaim]:
    table_keys = {fact.normalized_key for fact in code_facts if fact.fact_type == "schema_table"}
    table_leaf_keys = {key.split(".")[-1] for key in table_keys}
    env_keys = {fact.symbol for fact in code_facts if fact.fact_type == "env_var"}
    claims: list[DocClaim] = []
    seen: set[tuple[int, int, str, str]] = set()

    def add(row: sqlite3.Row, line_number: int, claim_type: str, claim_text: str, normalized_key: str, context: str) -> None:
        key = (int(row["target_doc_id"]), line_number, claim_type, normalized_key)
        if key in seen:
            return
        seen.add(key)
        claims.append(
            DocClaim(
                int(row["target_doc_id"]),
                row["canonical_path"],
                row["document_kind"],
                line_number,
                claim_type,
                claim_text,
                normalized_key,
                clip(context),
            )
        )

    for row in target_docs(conn):
        path = ROOT / row["canonical_path"]
        if not path.exists():
            continue
        for line_number, line in body_lines(path.read_text(encoding="utf-8", errors="replace")):
            endpoint_path_spans: list[tuple[int, int]] = []
            for match in CODE_PATH_RE.finditer(line):
                raw = match.group(1) or match.group(2) or ""
                normalized = normalize_path(raw).lower()
                if normalized:
                    add(row, line_number, "code_path", raw, normalized, line)
            for match in HTTP_ENDPOINT_RE.finditer(line):
                method, endpoint = match.groups()
                endpoint_path_spans.append(match.span(2))
                normalized = f"{method.upper()} {normalize_endpoint_path(endpoint)}".lower()
                add(row, line_number, "endpoint", f"{method.upper()} {endpoint}", normalized, line)
            for match in API_PATH_RE.finditer(line):
                if any(match.start(1) >= start and match.end(1) <= end for start, end in endpoint_path_spans):
                    continue
                endpoint = normalize_endpoint_path(match.group(1))
                add(row, line_number, "endpoint_path", endpoint, endpoint.lower(), line)
            for match in CLASS_SYMBOL_RE.finditer(line):
                symbol = match.group(0)
                add(row, line_number, "class_symbol", symbol, symbol.lower(), line)
            for match in ENV_RE.finditer(line):
                env_name = match.group(1) or match.group(2)
                if env_name in env_keys or "env" in line.lower() or "profile" in line.lower():
                    add(row, line_number, "env_var", env_name, env_name.lower(), line)
            for code_match in CODE_SPAN_RE.finditer(line):
                value = code_match.group(1).strip()
                normalized = normalize_table(value)
                if normalized in table_keys or normalized in table_leaf_keys:
                    add(row, line_number, "schema_table", value, normalized, line)
    return claims


def insert_doc_claims(conn: sqlite3.Connection, run_id: int, claims: list[DocClaim]) -> list[tuple[int, DocClaim]]:
    inserted: list[tuple[int, DocClaim]] = []
    for claim in claims:
        cursor = conn.execute(
            """
            INSERT INTO doc_claims(
              run_id, target_doc_id, canonical_path, line_number, claim_type, claim_text, normalized_key, context
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                claim.target_doc_id,
                claim.canonical_path,
                claim.line_number,
                claim.claim_type,
                claim.claim_text,
                claim.normalized_key,
                claim.context,
            ),
        )
        inserted.append((int(cursor.lastrowid), claim))
    return inserted


def build_fact_indexes(conn: sqlite3.Connection, run_id: int) -> dict[str, dict[str, list[int]]]:
    indexes: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    rows = conn.execute(
        "SELECT code_fact_id, fact_type, normalized_key, source_path, symbol FROM code_facts WHERE run_id = ?",
        (run_id,),
    ).fetchall()
    for row in rows:
        fact_id = int(row["code_fact_id"])
        fact_type = row["fact_type"]
        normalized_key = row["normalized_key"]
        indexes[fact_type][normalized_key].append(fact_id)
        if fact_type == "schema_table" and "." in normalized_key:
            indexes[fact_type][normalized_key.split(".")[-1]].append(fact_id)
        if row["symbol"]:
            indexes[fact_type][str(row["symbol"]).lower()].append(fact_id)
        indexes["code_path"][normalize_path(row["source_path"]).lower()].append(fact_id)
    return indexes


def assess_claim(
    claim_id: int,
    claim: DocClaim,
    indexes: dict[str, dict[str, list[int]]],
    core_root: Path,
) -> tuple[int, Assessment]:
    if claim.claim_type in {"endpoint", "endpoint_path"} and claim.document_kind == "source_system_reference":
        return claim_id, Assessment(claim, "out_of_scope", None, "high", "Source-system API path; validate in connector/source-system audit.")
    if claim.claim_type in {"endpoint", "endpoint_path"} and claim.canonical_path.startswith("docs/ai/"):
        return claim_id, Assessment(claim, "out_of_scope", None, "high", "AI service API path; validate in bc-ai/devhub audit.")
    if claim.claim_type == "code_path" and (ROOT / claim.normalized_key).exists():
        return claim_id, Assessment(claim, "out_of_scope", None, "high", "Path belongs to the documentation repository, not bc-core.")
    if claim.claim_type == "code_path" and claim.canonical_path.startswith("docs/ai/"):
        return claim_id, Assessment(claim, "out_of_scope", None, "medium", "AI implementation path; validate in bc-ai/devhub audit.")
    if claim.claim_type == "code_path" and claim.canonical_path == "docs/development/devhub.md":
        return claim_id, Assessment(claim, "out_of_scope", None, "medium", "DevHub implementation path; validate in DevHub audit.")
    match_types = {
        "code_path": ["code_path"],
        "class_symbol": ["controller", "service", "module", "guard", "interceptor", "middleware"],
        "endpoint": ["endpoint"],
        "endpoint_path": ["endpoint"],
        "schema_table": ["schema_table"],
        "env_var": ["env_var"],
    }[claim.claim_type]
    matches: list[int] = []
    if claim.claim_type == "endpoint_path":
        path_variants = {variant.split(" ", 1)[1] for variant in endpoint_key_variants(f"GET {claim.normalized_key}")}
        for fact_key, fact_ids in indexes["endpoint"].items():
            if any(fact_key.endswith(" " + path) for path in path_variants):
                matches.extend(fact_ids)
    else:
        for fact_type in match_types:
            matches.extend(indexes[fact_type].get(claim.normalized_key, []))

    unique_matches = sorted(set(matches))
    if not unique_matches and claim.claim_type == "endpoint":
        for variant in endpoint_key_variants(claim.normalized_key):
            matches.extend(indexes["endpoint"].get(variant, []))
        unique_matches = sorted(set(matches))
    if unique_matches:
        if len(unique_matches) == 1:
            return claim_id, Assessment(claim, "grounded", unique_matches[0], "high", "Matched extracted bc-core code fact.")
        return claim_id, Assessment(claim, "ambiguous", unique_matches[0], "medium", f"Matched {len(unique_matches)} extracted bc-core code facts.")

    if claim.claim_type == "code_path" and (core_root / claim.normalized_key).exists():
        return claim_id, Assessment(claim, "grounded", None, "medium", "Referenced path exists in bc-core but was not a tracked coverage target.")
    return claim_id, Assessment(claim, "ungrounded", None, "medium", "No matching bc-core code fact was found.")


def insert_assessments(conn: sqlite3.Connection, run_id: int, assessments: list[tuple[int, Assessment]]) -> None:
    for claim_id, assessment in assessments:
        conn.execute(
            """
            INSERT INTO doc_code_assessments(
              run_id, doc_claim_id, status, matched_code_fact_id, confidence, rationale
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                claim_id,
                assessment.status,
                assessment.matched_fact,
                assessment.confidence,
                assessment.rationale,
            ),
        )


def code_fact_claim_counts(conn: sqlite3.Connection, run_id: int) -> dict[int, dict[str, object]]:
    rows = conn.execute(
        """
        SELECT
          cf.code_fact_id,
          dc.canonical_path,
          td.document_kind,
          dca.status
        FROM code_facts cf
        LEFT JOIN doc_code_assessments dca
          ON dca.matched_code_fact_id = cf.code_fact_id
         AND dca.run_id = ?
        LEFT JOIN doc_claims dc
          ON dc.doc_claim_id = dca.doc_claim_id
        LEFT JOIN target_documents td
          ON td.target_doc_id = dc.target_doc_id
        WHERE cf.run_id = ?
        """,
        (run_id, run_id),
    ).fetchall()
    counts: dict[int, dict[str, object]] = defaultdict(lambda: {"generated": 0, "current": 0, "current_grounded": 0, "best": ""})
    for row in rows:
        fact_id = int(row["code_fact_id"])
        if not row["canonical_path"]:
            counts[fact_id]
            continue
        if row["document_kind"] == "generated_reference":
            counts[fact_id]["generated"] = int(counts[fact_id]["generated"]) + 1
        elif row["document_kind"] in CURRENT_DOC_KINDS:
            counts[fact_id]["current"] = int(counts[fact_id]["current"]) + 1
            if row["status"] == "grounded":
                counts[fact_id]["current_grounded"] = int(counts[fact_id]["current_grounded"]) + 1
            if not counts[fact_id]["best"]:
                counts[fact_id]["best"] = row["canonical_path"]
    return counts


def generated_coverage_by_source_path(conn: sqlite3.Connection) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in conn.execute(
        """
        SELECT ct.target_path, COUNT(DISTINCT cl.coverage_link_id)
        FROM coverage_targets ct
        JOIN coverage_links cl ON cl.coverage_target_id = ct.coverage_target_id
        JOIN target_documents td ON td.target_doc_id = cl.target_doc_id
        WHERE ct.repo_key = 'bc-core'
          AND td.document_kind = 'generated_reference'
        GROUP BY ct.target_path
        """
    ):
        counts[row[0]] = int(row[1])
    return counts


def priority_for_fact(fact_type: str, coverage_depth: str, source_path: str) -> str:
    if coverage_depth == "current_grounded":
        return "none"
    if fact_type in {"controller", "endpoint"}:
        if coverage_depth == "generated_only":
            return "medium"
        return "high" if coverage_depth == "current_claim_unverified" else "critical"
    if fact_type in {"guard", "interceptor", "middleware", "env_var"}:
        return "high" if coverage_depth == "uncovered" else "medium"
    if fact_type in {"schema_table", "script_command"}:
        return "medium" if coverage_depth == "uncovered" else "low"
    if fact_type in {"service", "module"}:
        if any(token in source_path.lower() for token in ["auth", "tenant", "contract", "metric", "docs", "audit", "chain"]):
            return "medium"
        return "low"
    return "low"


def code_area(source_path: str) -> str:
    parts = source_path.replace("\\", "/").split("/")
    if not parts:
        return "(unknown)"
    if parts[0] == "src":
        if len(parts) >= 3 and "." in parts[2]:
            return "/".join(parts[:2])
        if len(parts) >= 3 and parts[1] in {"registry", "boundary", "platform"}:
            return "/".join(parts[:3])
        if len(parts) >= 2:
            return "/".join(parts[:2])
    if parts[0] == "docker" and len(parts) >= 2:
        return "/".join(parts[:2])
    return parts[0]


def priority_rank(priority: str) -> int:
    return {"critical": 1, "high": 2, "medium": 3, "low": 4, "none": 5}.get(priority, 9)


def insert_code_doc_assessments(conn: sqlite3.Connection, run_id: int) -> None:
    counts = code_fact_claim_counts(conn, run_id)
    generated_by_path = generated_coverage_by_source_path(conn)
    for row in conn.execute(
        """
        SELECT code_fact_id, fact_type, source_path, normalized_key
        FROM code_facts
        WHERE run_id = ?
        """,
        (run_id,),
    ):
        fact_id = int(row["code_fact_id"])
        item = counts[fact_id]
        generated = max(int(item["generated"]), generated_by_path[row["source_path"]])
        current = int(item["current"])
        current_grounded = int(item["current_grounded"])
        if row["fact_type"] == "code_path":
            depth = "not_required"
        elif current_grounded:
            depth = "current_grounded"
        elif current:
            depth = "current_claim_unverified"
        elif generated:
            depth = "generated_only"
        else:
            depth = "uncovered"
        priority = priority_for_fact(row["fact_type"], depth, row["source_path"]) if depth != "not_required" else "none"
        conn.execute(
            """
            INSERT INTO code_doc_assessments(
              run_id, code_fact_id, generated_claims, current_claims, current_grounded_claims,
              coverage_depth, relevance_priority, best_doc_path, rationale
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                fact_id,
                generated,
                current,
                current_grounded,
                depth,
                priority,
                item["best"] or None,
                "Assessment from doc claims extracted during bidirectional bc-core audit.",
            ),
        )


def write_audit_report(conn: sqlite3.Connection, run_id: int, core_root: Path) -> None:
    lines = [
        "# Bidirectional bc-core Documentation Audit",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Audit run: `{run_id}`",
        f"bc-core commit: `{source_commit(core_root)}`",
        "",
        "## Code Fact Inventory",
        "",
    ]
    write_table(
        lines,
        ["Fact Type", "Facts"],
        [
            (row[0], row[1])
            for row in conn.execute(
                """
                SELECT fact_type, COUNT(*)
                FROM code_facts
                WHERE run_id = ?
                GROUP BY fact_type
                ORDER BY fact_type
                """,
                (run_id,),
            )
        ],
    )
    lines.extend(["", "## Doc Claim Grounding", ""])
    write_table(
        lines,
        ["Claim Type", "Status", "Claims"],
        [
            (row[0], row[1], row[2])
            for row in conn.execute(
                """
                SELECT dc.claim_type, dca.status, COUNT(*)
                FROM doc_claims dc
                JOIN doc_code_assessments dca ON dca.doc_claim_id = dc.doc_claim_id
                WHERE dc.run_id = ?
                GROUP BY dc.claim_type, dca.status
                ORDER BY dc.claim_type, dca.status
                """,
                (run_id,),
            )
        ],
    )
    lines.extend(["", "## Ungrounded Claim Hotspots", ""])
    write_table(
        lines,
        ["Document", "Claim Type", "Ungrounded Claims"],
        [
            (row[0], row[1], row[2])
            for row in conn.execute(
                """
                SELECT dc.canonical_path, dc.claim_type, COUNT(*)
                FROM doc_claims dc
                JOIN doc_code_assessments dca ON dca.doc_claim_id = dc.doc_claim_id
                JOIN target_documents td ON td.target_doc_id = dc.target_doc_id
                WHERE dc.run_id = ?
                  AND td.document_kind IN ('current_chapter', 'curated_reference', 'source_system_reference')
                  AND dca.status = 'ungrounded'
                GROUP BY dc.canonical_path, dc.claim_type
                ORDER BY COUNT(*) DESC, dc.canonical_path, dc.claim_type
                LIMIT 30
                """,
                (run_id,),
            )
        ],
    )
    lines.extend(["", "## Code-To-Doc Coverage Depth", ""])
    write_table(
        lines,
        ["Fact Type", "Coverage Depth", "Facts"],
        [
            (row[0], row[1], row[2])
            for row in conn.execute(
                """
                SELECT cf.fact_type, cda.coverage_depth, COUNT(*)
                FROM code_doc_assessments cda
                JOIN code_facts cf ON cf.code_fact_id = cda.code_fact_id
                WHERE cda.run_id = ?
                GROUP BY cf.fact_type, cda.coverage_depth
                ORDER BY cf.fact_type, cda.coverage_depth
                """,
                (run_id,),
            )
        ],
    )
    lines.extend(["", "## Ungrounded Current Claims", ""])
    write_table(
        lines,
        ["Document", "Line", "Claim Type", "Claim", "Rationale"],
        [
            (row[0], row[1], row[2], row[3], row[4])
            for row in conn.execute(
                """
                SELECT dc.canonical_path, dc.line_number, dc.claim_type, dc.claim_text, dca.rationale
                FROM doc_claims dc
                JOIN doc_code_assessments dca ON dca.doc_claim_id = dc.doc_claim_id
                JOIN target_documents td ON td.target_doc_id = dc.target_doc_id
                WHERE dc.run_id = ?
                  AND td.document_kind IN ('current_chapter', 'curated_reference', 'source_system_reference')
                  AND dca.status = 'ungrounded'
                ORDER BY dc.canonical_path, dc.line_number
                LIMIT 80
                """,
                (run_id,),
            )
        ],
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_relevance_report(conn: sqlite3.Connection, run_id: int) -> None:
    lines = [
        "# bc-core Relevance And Coverage Queue",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Audit run: `{run_id}`",
        "",
        "This queue is a prioritization aid. `generated_only` means the control plane has generated inventory coverage, not necessarily human explanatory coverage.",
        "",
        "## Priority Summary",
        "",
    ]
    write_table(
        lines,
        ["Priority", "Coverage Depth", "Fact Type", "Facts"],
        [
            (row[0], row[1], row[2], row[3])
            for row in conn.execute(
                """
                SELECT cda.relevance_priority, cda.coverage_depth, cf.fact_type, COUNT(*)
                FROM code_doc_assessments cda
                JOIN code_facts cf ON cf.code_fact_id = cda.code_fact_id
                WHERE cda.run_id = ?
                  AND cda.relevance_priority != 'none'
                GROUP BY cda.relevance_priority, cda.coverage_depth, cf.fact_type
                ORDER BY CASE cda.relevance_priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END,
                         cda.coverage_depth,
                         cf.fact_type
                """,
                (run_id,),
            )
        ],
    )
    area_counts: Counter[tuple[str, str, str]] = Counter()
    for row in conn.execute(
        """
        SELECT cda.relevance_priority, cda.coverage_depth, cf.source_path
        FROM code_doc_assessments cda
        JOIN code_facts cf ON cf.code_fact_id = cda.code_fact_id
        WHERE cda.run_id = ?
          AND cda.relevance_priority != 'none'
          AND cda.current_grounded_claims = 0
          AND cf.fact_type != 'code_path'
        """,
        (run_id,),
    ):
        area_counts[(code_area(row[2]), row[0], row[1])] += 1
    lines.extend(["", "## Top Code Areas Without Current Grounding", ""])
    write_table(
        lines,
        ["Code Area", "Priority", "Coverage Depth", "Facts"],
        [
            (area, priority, depth, count)
            for (area, priority, depth), count in sorted(
                area_counts.items(),
                key=lambda item: (priority_rank(item[0][1]), -item[1], item[0][0], item[0][2]),
            )[:40]
        ],
    )
    lines.extend(["", "## Critical And High Priority Code Fact Samples", ""])
    write_table(
        lines,
        ["Priority", "Fact Type", "Symbol", "Source Path", "Evidence", "Generated Claims", "Current Claims"],
        [
            (row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            for row in conn.execute(
                """
                SELECT cda.relevance_priority, cf.fact_type, COALESCE(cf.symbol, ''), cf.source_path,
                       COALESCE(cf.evidence, ''), cda.generated_claims, cda.current_claims
                FROM code_doc_assessments cda
                JOIN code_facts cf ON cf.code_fact_id = cda.code_fact_id
                WHERE cda.run_id = ?
                  AND cda.relevance_priority IN ('critical', 'high')
                  AND cf.fact_type != 'code_path'
                ORDER BY CASE cda.relevance_priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 ELSE 3 END,
                         cf.fact_type,
                         cf.source_path
                LIMIT 120
                """,
                (run_id,),
            )
        ],
    )
    lines.extend(["", "## Current Documents With Ungrounded Claims", ""])
    write_table(
        lines,
        ["Document", "Ungrounded Claims"],
        [
            (row[0], row[1])
            for row in conn.execute(
                """
                SELECT dc.canonical_path, COUNT(*)
                FROM doc_claims dc
                JOIN doc_code_assessments dca ON dca.doc_claim_id = dc.doc_claim_id
                JOIN target_documents td ON td.target_doc_id = dc.target_doc_id
                WHERE dc.run_id = ?
                  AND td.document_kind IN ('current_chapter', 'curated_reference', 'source_system_reference')
                  AND dca.status = 'ungrounded'
                GROUP BY dc.canonical_path
                ORDER BY COUNT(*) DESC, dc.canonical_path
                LIMIT 80
                """,
                (run_id,),
            )
        ],
    )
    RELEVANCE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RELEVANCE_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-root", type=Path, default=DEFAULT_CORE_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    core_root = args.core_root.resolve()
    if not core_root.exists():
        raise SystemExit(f"bc-core root not found: {core_root}")
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        schema_sql(conn)
        run_id = start_run(conn, core_root)
        try:
            code_facts = collect_code_facts(conn, core_root)
            insert_code_facts(conn, run_id, code_facts)
            doc_claims = extract_doc_claims(conn, code_facts)
            inserted_claims = insert_doc_claims(conn, run_id, doc_claims)
            indexes = build_fact_indexes(conn, run_id)
            assessments = [assess_claim(claim_id, claim, indexes, core_root) for claim_id, claim in inserted_claims]
            insert_assessments(conn, run_id, assessments)
            insert_code_doc_assessments(conn, run_id)
            summary = {
                "code_facts": len(code_facts),
                "doc_claims": len(doc_claims),
                "claim_status": dict(Counter(assessment.status for _, assessment in assessments)),
            }
            finish_run(conn, run_id, "completed", summary)
            write_audit_report(conn, run_id, core_root)
            write_relevance_report(conn, run_id)
            conn.commit()
        except Exception as exc:
            finish_run(conn, run_id, "failed", {}, str(exc))
            conn.commit()
            raise
    print(f"bidirectional audit run={run_id} code_facts={len(code_facts)} doc_claims={len(doc_claims)}")
    print(f"wrote {REPORT_PATH}")
    print(f"wrote {RELEVANCE_REPORT_PATH}")


if __name__ == "__main__":
    main()
