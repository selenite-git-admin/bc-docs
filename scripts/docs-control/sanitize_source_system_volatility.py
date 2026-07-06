#!/usr/bin/env python3
"""Replace volatile source-system licensing/commercial sections with verification guidance."""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SYSTEM_ROOT = ROOT / "docs" / "reference" / "source-systems"
REPORT_PATH = ROOT / "docs-control" / "reports" / "source-system-volatility-sanitization-report.md"

BOUNDARY_RE = re.compile(r"(?m)^(---|##\s+\d+\.)")

SECTION_BODIES = {
    "## 4. Legal & Licensing": "\n".join(
        [
            "Vendor licensing, access-tier, rate-limit, pricing, and contractual terms are not maintained as static facts in v4.",
            "",
            "During source onboarding, verify:",
            "",
            "- customer entitlement for the selected API or interface",
            "- whether a dedicated service identity requires a paid license",
            "- whether read-only extraction is permitted under the customer contract",
            "- rate-limit, concurrency, and data-egress constraints that affect reader scheduling",
            "",
            "Record the verified terms in the onboarding evidence for that tenant and source. This page may name the admission stance, but it must not be treated as vendor-license advice.",
        ]
    ),
    "## 5. Commercial": "\n".join(
        [
            "No static commercial estimate is maintained here.",
            "",
            "Capture customer-specific subscription, add-on, service-account, API, connector, egress, partnership, or infrastructure costs during onboarding evidence review.",
        ]
    ),
}

SOURCE_TERM_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?<!ServiceNow )\bNow Platform REST APIs\b"), "ServiceNow REST APIs"),
    (re.compile(r"(?<!ServiceNow )\bNow Platform REST API\b"), "ServiceNow REST API"),
    (re.compile(r"(?<!ServiceNow )\bNow Platform\b"), "ServiceNow platform"),
    (re.compile(r"\bToday:"), "Readiness baseline:"),
    (re.compile(r"\btoday\b"), "in the readiness baseline"),
    (re.compile(r"\bCurrently\b"), "Readiness baseline"),
    (re.compile(r"\bcurrently\b"), "in the readiness baseline"),
    (re.compile(r"\bas of 20\d{2}-\d{2}-\d{2}\b"), "in the reference baseline"),
    (re.compile(r"\bfor now\b"), "for this reference baseline"),
]

VENDOR_LIMIT_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"Per-user-per-minute limit \(150 free, 1,500 paid\)"), "Vendor-defined per-user-per-minute limit"),
    (re.compile(r"max 10,000 results per query [—-] beyond that, must split filters"), "vendor-defined result-window limit requiring filter splitting for broad pulls"),
    (re.compile(r"250,000 calls / day default; 1M with add-on"), "vendor-defined daily call limit by subscription and add-on"),
    (re.compile(r"3,000-series-per-response cap"), "vendor-defined series-per-response cap"),
    (re.compile(r"The IMF now operates three distinct SDMX-based systems:"), "The IMF reference page distinguishes the relevant SDMX-based systems:"),
    (re.compile(r"The SDR basket \(reviewed every 5 years\) comprises USD \(43\.38%\), EUR \(29\.31%\), CNY \(12\.28%\), JPY \(7\.59%\), GBP \(7\.44%\) as of August 2022 review\."), "The SDR basket is a periodically reviewed official composition; verify currency weights from IMF documentation during onboarding."),
    (re.compile(r"6,000 / 5-minute sliding window"), "vendor-defined sliding-window quota"),
    (re.compile(r"10 minutes"), "vendor-defined request timeout"),
    (re.compile(r"20,000 entities per page \(OData\)"), "vendor-defined OData page-size limit"),
    (re.compile(r"Each app gets its own 6,000 / 5-min quota\."), "Each app registration carries its own vendor-defined quota."),
    (re.compile(r"~10,000,000 \(configurable up\)"), "vendor-defined complexity budget, configurable by plan"),
    (re.compile(r"~10,000,000"), "vendor-defined complexity budget"),
    (re.compile(r"Max 500 records per POST"), "Vendor-defined POST batch-size limit"),
    (re.compile(r"1,000 / page"), "vendor-defined page-size limit"),
    (re.compile(r"2,000 \(across the company\)"), "vendor-defined company-level quota"),
    (re.compile(r"~5,000 req/min per account"), "vendor-defined request quota per account"),
    (re.compile(r"22 tables, weekly"), "vendor-defined table set, weekly"),
    (re.compile(r"max 15,000 records / chunk"), "vendor-defined chunk size"),
    (re.compile(r"15,000 records / chunk"), "vendor-defined chunk size"),
    (re.compile(r"1,368 AR records via `bc-sdg` port 6100"), "internal simulator AR-record coverage via `bc-sdg`"),
    (re.compile(r"1,368 AR records"), "internal simulator AR-record coverage"),
    (re.compile(r"`sysparm_limit` \(max 10,000\), `sysparm_offset` for paging\."), "`sysparm_limit` and `sysparm_offset` for vendor-defined paging."),
    (re.compile(r"Access token: 30 minutes; refresh token: 60 days, single-use rotation\."), "Token windows and refresh-token rotation are vendor-defined and must be verified during onboarding."),
    (re.compile(r"100 records per page typical"), "vendor-defined page size"),
    (re.compile(r"5,000 calls per tenant"), "vendor-defined call limit per tenant"),
    (re.compile(r"1,000–10,000 / day per organisation per plan"), "vendor-defined daily quota by organisation and plan"),
    (re.compile(r"5,000 rows per page"), "vendor-defined page size"),
    (re.compile(r"1,000 per page"), "vendor-defined page size"),
    (re.compile(r"max 1,000 / page"), "vendor-defined page-size limit"),
    (re.compile(r"max 5,000 / page"), "vendor-defined page-size limit"),
    (re.compile(r"5,000 / page"), "vendor-defined page-size limit"),
    (re.compile(r"Max 5,000 records per response"), "Vendor-defined records-per-response limit"),
    (re.compile(r"Hard cap of 5,000 records per response"), "Vendor-defined records-per-response cap"),
    (re.compile(r"5,000-record cap"), "vendor-defined pagination cap"),
    (re.compile(r"max 10,000 records per page"), "vendor-defined page size"),
    (re.compile(r"10,000 records per page"), "vendor-defined page size"),
    (re.compile(r"10,000 records/page, 2-minute request timeout"), "vendor-defined page-size and request-time limits"),
    (re.compile(r"2 minutes per individual request"), "vendor-defined request timeout"),
    (re.compile(r"typically 60[–-]90 minutes"), "vendor-defined token window"),
    (re.compile(r"~7,600 released CDS views"), "released CDS view catalog"),
    (re.compile(r"~1,600-indicator compilation"), "flagship indicator compilation"),
    (re.compile(r"16,000\+ coded indicators"), "large coded indicator catalog"),
    (re.compile(r"4,000 characters total; 1,500 between slashes"), "vendor-defined URL length limits"),
    (re.compile(r"Up to 32,500"), "Vendor-defined maximum"),
    (re.compile(r"16,000 indicators × 200 countries"), "the full indicator catalog across country history"),
    (re.compile(r"all 16,000 indicators"), "the full indicator catalog"),
]


@dataclass(frozen=True)
class Replacement:
    path: Path
    heading: str
    before_lines: int
    after_lines: int


def source_files() -> list[Path]:
    return [
        path
        for path in sorted(SOURCE_SYSTEM_ROOT.glob("*.md"))
        if path.name not in {"index.md", "sap-licensing-reference.md"}
    ]


def section_end(text: str, start: int) -> int:
    match = BOUNDARY_RE.search(text, start)
    return match.start() if match else len(text)


def replace_section(text: str, heading: str, body: str) -> tuple[str, Replacement | None]:
    heading_match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
    if not heading_match:
        return text, None
    start = heading_match.start()
    content_start = heading_match.end()
    end = section_end(text, content_start)
    original = text[start:end]
    replacement = f"{heading}\n\n{body}\n\n"
    if original == replacement:
        return text, None
    before_lines = len(original.splitlines())
    after_lines = len(replacement.splitlines())
    return text[:start] + replacement + text[end:], Replacement(Path(), heading, before_lines, after_lines)


def normalize_proof_status(text: str) -> tuple[str, Replacement | None]:
    pattern = re.compile(r"(?m)^\*\*`([^`]+)`\*\* as of 20\d{2}-\d{2}-\d{2}\.(.*)$")
    match = pattern.search(text)
    if not match:
        return text, None
    status = match.group(1)
    tail = match.group(2).strip()
    replacement = f"**Proof status:** `{status}`."
    if tail:
        replacement = f"{replacement}\n\n{tail}"
    before_lines = len(match.group(0).splitlines())
    after_lines = len(replacement.splitlines())
    updated = text[: match.start()] + replacement + text[match.end() :]
    return updated, Replacement(Path(), "Proof Status date duplicate", before_lines, after_lines)


def normalize_changelog(text: str) -> tuple[str, Replacement | None]:
    match = re.search(r"(?m)^## 12\. Changelog\s*$", text)
    if not match:
        return text, None
    start = match.start()
    original = text[start:]
    replacement = "\n".join(
        [
            "## 12. Changelog",
            "",
            "Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.",
            "",
        ]
    )
    if original == replacement:
        return text, None
    before_lines = len(original.splitlines())
    after_lines = len(replacement.splitlines())
    return text[:start] + replacement, Replacement(Path(), "## 12. Changelog", before_lines, after_lines)


def normalize_intro(text: str) -> tuple[str, Replacement | None]:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    if not match:
        return text, None
    title = match.group(1)
    start = match.start()
    content_start = match.end()
    boundary = re.search(r"(?m)^---\s*$", text[content_start:])
    if not boundary:
        return text, None
    end = content_start + boundary.start()
    original = text[start:end]
    replacement = "\n".join(
        [
            f"# {title}",
            "",
            f"This page records BareCount's source-admission posture for {title}. It is not a static vendor fact sheet.",
            "",
            "Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.",
            "",
            "",
        ]
    )
    if original == replacement:
        return text, None
    before_lines = len(original.splitlines())
    after_lines = len(replacement.splitlines())
    return text[:start] + replacement + text[end:], Replacement(Path(), "Intro volatile fact sheet", before_lines, after_lines)


def normalize_description(text: str) -> tuple[str, Replacement | None]:
    pattern = re.compile(r'(?m)^description:\s+".*"$')
    match = pattern.search(text)
    if not match:
        return text, None
    replacement = 'description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."'
    if match.group(0) == replacement:
        return text, None
    updated = text[: match.start()] + replacement + text[match.end() :]
    return updated, Replacement(Path(), "Frontmatter volatile description", 1, 1)


def normalize_source_terms(text: str) -> tuple[str, Replacement | None]:
    updated = text
    for pattern, replacement in SOURCE_TERM_REPLACEMENTS:
        updated = pattern.sub(replacement, updated)
    if updated == text:
        return text, None
    return updated, Replacement(Path(), "Source temporal posture wording", len(text.splitlines()), len(updated.splitlines()))


def normalize_vendor_limits(text: str) -> tuple[str, Replacement | None]:
    updated = text
    for pattern, replacement in VENDOR_LIMIT_REPLACEMENTS:
        updated = pattern.sub(replacement, updated)
    if updated == text:
        return text, None
    return updated, Replacement(Path(), "Vendor limit/count wording", len(text.splitlines()), len(updated.splitlines()))


def sanitize_text(path: Path, text: str) -> tuple[str, list[Replacement]]:
    replacements: list[Replacement] = []
    updated = text
    updated, replacement = normalize_description(updated)
    if replacement:
        replacements.append(Replacement(path, replacement.heading, replacement.before_lines, replacement.after_lines))
    updated, replacement = normalize_intro(updated)
    if replacement:
        replacements.append(Replacement(path, replacement.heading, replacement.before_lines, replacement.after_lines))
    updated, replacement = normalize_source_terms(updated)
    if replacement:
        replacements.append(Replacement(path, replacement.heading, replacement.before_lines, replacement.after_lines))
    updated, replacement = normalize_vendor_limits(updated)
    if replacement:
        replacements.append(Replacement(path, replacement.heading, replacement.before_lines, replacement.after_lines))
    for heading, body in SECTION_BODIES.items():
        updated, replacement = replace_section(updated, heading, body)
        if replacement:
            replacements.append(Replacement(path, replacement.heading, replacement.before_lines, replacement.after_lines))
    updated, replacement = normalize_proof_status(updated)
    if replacement:
        replacements.append(Replacement(path, replacement.heading, replacement.before_lines, replacement.after_lines))
    updated, replacement = normalize_changelog(updated)
    if replacement:
        replacements.append(Replacement(path, replacement.heading, replacement.before_lines, replacement.after_lines))
    return updated.rstrip() + "\n", replacements


def write_report(replacements: list[Replacement], dry_run: bool) -> None:
    lines = [
        "# Source-System Volatility Sanitization Report",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"Dry run: `{dry_run}`",
        f"Files changed: `{len(set(item.path for item in replacements))}`",
        f"Sections replaced: `{len(replacements)}`",
        "",
        "## Replacements",
        "",
        "| File | Section | Old Lines | New Lines |",
        "|---|---|---|---|",
    ]
    for item in replacements:
        rel_path = item.path.relative_to(ROOT).as_posix()
        lines.append(f"| {rel_path} | {item.heading} | {item.before_lines} | {item.after_lines} |")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="rewrite matching source-system sections")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    all_replacements: list[Replacement] = []
    for path in source_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        updated, replacements = sanitize_text(path, text)
        all_replacements.extend(replacements)
        if args.apply and updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
    write_report(all_replacements, not args.apply)
    print(f"files={len(set(item.path for item in all_replacements))} sections={len(all_replacements)} apply={args.apply}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
