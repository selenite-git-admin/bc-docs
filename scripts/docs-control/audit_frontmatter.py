#!/usr/bin/env python3
"""Frontmatter vocabulary audit for bc-docs (TSK-d3dd83; Part D decision 3, 2026-09-30).

Every Markdown file under docs/ is classified into a document kind by its path.
Each kind has one allowed set of `authority` values (the same four for every kind
that carries the key), one allowed set of `status` values (per kind, because the
kinds have different lifecycles) and, for generated files, a set of required keys.
The declaring chapter is docs/development/documentation-system.md.

The check fails (exit 1) when a file is outside its kind's vocabulary and is not
listed in the shrink-only baseline docs-control/frontmatter-baseline.json, and
when a baseline entry has become clean but was not removed (the baseline can only
shrink). `--write-baseline` rewrites the baseline from the current offenders and
is a local act, never a CI act. Pure Python standard library, like audit_adrs.py.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
BASELINE_PATH = ROOT / "docs-control" / "frontmatter-baseline.json"
REPORT_PATH = ROOT / "docs-control" / "reports" / "frontmatter-audit.md"

AUTHORITY_VALUES = {"authoritative", "reference", "evidentiary", "generated"}
CHAPTER_SECTIONS = (
    "overview", "foundation", "operating-model", "implementation", "ai",
    "development", "onboarding", "operations", "compliance",
)
GENERATED_PATHS = (
    "reference/data-dictionary/", "reference/code-index/", "reference/api/",
    "reference/schemas/", "reference/lifecycle-map.md",
    "reference/enforcement-surface-map.md",
)
GENERATED_REQUIRED_KEYS = ("generator", "source_repo", "source_commit", "generated_at")

# kind -> (authority rule, allowed status values)
# authority rule: "any" = one of AUTHORITY_VALUES; "absent" = key must not exist;
# a single value = the key must equal it.
KIND_RULES: dict[str, tuple[str, set[str]]] = {
    "chapter": ("any", {"drafting", "reviewing", "locked", "superseded", "retired"}),
    "adr": ("absent", {"proposed", "decided", "implemented", "superseded", "reversed"}),
    "erratum": ("any", {"open", "adopted", "rejected", "deferred", "closed"}),
    "docket": ("reference", {"draft", "published", "retired"}),
    "generated": ("generated", {"generated"}),
    "evidence": ("evidentiary", {"drafting", "locked", "superseded", "retired"}),
    "archive": ("any", {"retired"}),
}

KEY_RE = re.compile(r"^([A-Za-z][\w-]*):\s*(.*)$")


def parse_frontmatter(text: str) -> dict | None:
    """Scalars only: returns None when the file has no frontmatter block."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm: dict = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fm
        m = KEY_RE.match(line)
        if m:
            raw = re.sub(r"\s+#.*$", "", m.group(2))  # drop an inline YAML comment
            fm[m.group(1)] = raw.strip().strip("\"'")
    return None


def classify(rel: str) -> str | None:
    """Path rules from the decision. None means exempt."""
    name = rel.rsplit("/", 1)[-1]
    if rel in ("README.md", "NAVIGATION.md") or rel.startswith("assets/"):
        return None
    if rel.startswith("governance/adrs/"):
        return "adr" if name.startswith("ADR-") else None
    if rel.startswith("governance/errata/"):
        return "erratum" if "-ERR-" in name else None
    if name == "README.md":
        return None
    if rel.startswith("archive/"):
        return "archive"
    if rel.startswith("evidence/") or rel.startswith("governance/plans/"):
        return "evidence"
    if rel.startswith(GENERATED_PATHS):
        return "generated"
    if rel.startswith("reference/source-systems/"):
        return "docket"
    if rel.startswith("reference/") or rel.startswith(tuple(s + "/" for s in CHAPTER_SECTIONS)):
        return "chapter"
    return "chapter"


def check_file(kind: str, fm: dict | None) -> list[str]:
    """Returns the list of problems for one file (empty when clean)."""
    if fm is None:
        return ["no frontmatter block"]
    auth_rule, statuses = KIND_RULES[kind]
    problems: list[str] = []
    authority = fm.get("authority")
    if auth_rule == "absent":
        if authority is not None:
            problems.append(f"authority must be absent on an ADR (found '{authority}')")
    elif auth_rule == "any":
        if authority not in AUTHORITY_VALUES:
            problems.append(f"authority '{authority}' not in {sorted(AUTHORITY_VALUES)}")
    elif authority != auth_rule:
        problems.append(f"authority must be '{auth_rule}' (found '{authority}')")
    if kind == "docket" and fm.get("authority_role") != "projection":
        problems.append("docket must carry authority_role: projection (DEC-8570d4)")
    status = fm.get("status")
    if status not in statuses:
        problems.append(f"status '{status}' not in {sorted(statuses)}")
    if kind == "generated":
        missing = [k for k in GENERATED_REQUIRED_KEYS if not fm.get(k)]
        if missing:
            problems.append(f"generated file missing keys {missing}")
    return problems


def scan() -> tuple[dict[str, list[str]], Counter, int]:
    offenders: dict[str, list[str]] = {}
    per_kind: Counter = Counter()
    exempt = 0
    for path in sorted(DOCS.rglob("*.md")):
        rel = path.relative_to(DOCS).as_posix()
        kind = classify(rel)
        if kind is None:
            exempt += 1
            continue
        per_kind[kind] += 1
        problems = check_file(kind, parse_frontmatter(path.read_text(encoding="utf-8", errors="replace")))
        if problems:
            offenders[rel] = [f"[{kind}] {p}" for p in problems]
    return offenders, per_kind, exempt


def load_baseline() -> set[str]:
    if not BASELINE_PATH.is_file():
        return set()
    return set(json.loads(BASELINE_PATH.read_text(encoding="utf-8")).get("offenders", []))


def write_report(offenders, per_kind, exempt, new, stale) -> None:
    lines = ["# Frontmatter vocabulary audit (TSK-d3dd83)", ""]
    lines.append(f"Files by kind: {dict(sorted(per_kind.items()))}; exempt: {exempt}")
    lines.append(f"Offenders: {len(offenders)}; not in baseline: {len(new)}; "
                 f"baseline entries now clean: {len(stale)}")
    lines.append("")
    lines.append("## Offenders not in the baseline (MUST be 0)")
    lines.extend(f"- {p}: {'; '.join(offenders[p])}" for p in sorted(new)) or lines.append("- (none)")
    lines.append("")
    lines.append("## Baseline entries now clean (remove them from the baseline)")
    lines.extend(f"- {p}" for p in sorted(stale)) or lines.append("- (none)")
    lines.append("")
    by_kind: dict[str, list[str]] = defaultdict(list)
    for p, probs in offenders.items():
        by_kind[probs[0].split("]")[0].strip("[")].append(p)
    lines.append("## All offenders by kind")
    for kind in sorted(by_kind):
        lines.append(f"### {kind} ({len(by_kind[kind])})")
        lines.extend(f"- {p}: {'; '.join(offenders[p])}" for p in sorted(by_kind[kind]))
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="bc-docs frontmatter vocabulary audit.")
    ap.add_argument("--write-baseline", action="store_true",
                    help="rewrite docs-control/frontmatter-baseline.json from the current offenders (local act only)")
    args = ap.parse_args()
    if not DOCS.is_dir():
        print(f"docs dir not found: {DOCS}", file=sys.stderr)
        return 2

    offenders, per_kind, exempt = scan()
    if args.write_baseline:
        BASELINE_PATH.write_text(json.dumps(
            {"note": "shrink-only baseline for audit_frontmatter.py; entries may only be removed",
             "offenders": sorted(offenders)}, indent=2) + "\n", encoding="utf-8")
        print(f"baseline written: {len(offenders)} offenders -> {BASELINE_PATH.relative_to(ROOT)}")

    baseline = load_baseline()
    new = sorted(set(offenders) - baseline)
    stale = sorted(baseline - set(offenders))
    write_report(offenders, per_kind, exempt, new, stale)

    print(f"Frontmatter audit - {sum(per_kind.values())} files checked, {exempt} exempt")
    print(f"  by kind: {dict(sorted(per_kind.items()))}")
    print(f"  offenders: {len(offenders)} (baseline {len(baseline)})")
    print(f"  NOT in baseline: {len(new)}")
    for p in new:
        print(f"    x {p}: {'; '.join(offenders[p])}")
    print(f"  baseline entries now clean (remove them): {len(stale)}")
    for p in stale:
        print(f"    - {p}")
    print(f"  report: {REPORT_PATH.relative_to(ROOT)}")
    return 1 if (new or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
