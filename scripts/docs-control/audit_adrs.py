#!/usr/bin/env python3
"""ADR hygiene audit (DEC-623f8f / D370).

Enforces the two commit-gating rules of the ADR Hygiene Policy over
docs/governance/adrs/:

  1. Supersession pair rule — an ADR with `supersedes: DEC-xxx` requires the
     target's `status` to be `superseded` (and SHOULD carry `superseded_by`).
     Unflipped pairs are reported as supersessionIssues.
  2. Stuck-proposed rule — an ADR left in `status: proposed` for more than
     STALE_PROPOSED_DAYS days.

Advisory (non-failing) checks: classification coverage (subdomain + focus) and
missing/duplicate uids. Pure diagnostic — writes a report and prints a summary.
Exit code is non-zero when supersessionIssues exist, so it can gate CI.

Replaces the never-migrated `scripts/adr-audit.js` referenced in CLAUDE.md;
matches the Python docs-control toolchain (v3->v4 refactor).
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADR_DIR = ROOT / "docs" / "governance" / "adrs"
REPORT_PATH = ROOT / "docs-control" / "reports" / "adr-hygiene.md"
STALE_PROPOSED_DAYS = 30

KEY_RE = re.compile(r"^([A-Za-z][\w-]*):\s*(.*)$")
LIST_ITEM_RE = re.compile(r"^\s*-\s*(.+)$")


def parse_frontmatter(text: str) -> dict:
    """Manual YAML-frontmatter parse: scalars, inline `[a, b]`, and block lists."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm: dict = {}
    cur_list_key: str | None = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = KEY_RE.match(line)
        if m:
            key, raw = m.group(1), m.group(2).strip()
            val = raw.strip("\"'")
            if raw == "":
                fm[key] = []
                cur_list_key = key
            elif raw.startswith("[") and raw.endswith("]"):
                fm[key] = [
                    x.strip().strip("\"'") for x in raw[1:-1].split(",") if x.strip()
                ]
                cur_list_key = None
            else:
                fm[key] = val
                cur_list_key = None
            continue
        item = LIST_ITEM_RE.match(line)
        if item and cur_list_key is not None and isinstance(fm.get(cur_list_key), list):
            fm[cur_list_key].append(item.group(1).strip().strip("\"'"))
    return fm


def as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v]
    return [value] if value else []


def parse_date(value: str | None):
    if not value:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", value)
    if not m:
        return None
    return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)


def main() -> int:
    ap = argparse.ArgumentParser(description="ADR hygiene audit (D370).")
    ap.add_argument("--strict", action="store_true",
                    help="also fail (exit 1) on stuck-proposed ADRs, not just supersession issues")
    args = ap.parse_args()

    if not ADR_DIR.is_dir():
        print(f"ADR dir not found: {ADR_DIR}", file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc)
    adrs: list[dict] = []
    by_uid: dict[str, dict] = {}
    dup_uids: list[str] = []

    quarantined = 0
    for path in sorted(ADR_DIR.glob("ADR-*.md")):
        fm = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        rec = {"file": path.name, **fm}
        adrs.append(rec)
        uid = fm.get("uid")
        if not uid:
            continue
        # A self-quarantined duplicate marks itself: superseded_by its OWN uid, or
        # an explicit [QUARANTINED ...] title. It is a dispositioned artifact — not
        # the canonical row and not a duplicate-uid violation.
        title_up = str(fm.get("title", "")).upper()
        if fm.get("superseded_by") == uid or "QUARANTINED" in title_up:
            rec["_quarantine"] = True
            quarantined += 1
            continue
        if uid in by_uid:
            dup_uids.append(uid)
        by_uid[uid] = rec

    supersession_issues: list[str] = []
    for rec in adrs:
        targets = as_list(rec.get("supersedes")) + as_list(rec.get("supersedes_ref"))
        for target in targets:
            t = by_uid.get(target)
            if t is None:
                supersession_issues.append(
                    f"{rec.get('uid', rec['file'])} supersedes {target} — TARGET NOT FOUND"
                )
            elif str(t.get("status", "")).lower() != "superseded":
                supersession_issues.append(
                    f"{rec.get('uid', rec['file'])} supersedes {target} — "
                    f"target status is '{t.get('status')}', expected 'superseded'"
                )
            elif not t.get("superseded_by"):
                supersession_issues.append(
                    f"{rec.get('uid', rec['file'])} supersedes {target} — target is "
                    f"superseded but MISSING superseded_by (SHOULD be set)"
                )

    stuck_proposed: list[str] = []
    for rec in adrs:
        if str(rec.get("status", "")).lower() != "proposed":
            continue
        dt = parse_date(rec.get("date"))
        age = (now - dt).days if dt else None
        if age is None or age > STALE_PROPOSED_DAYS:
            stuck_proposed.append(
                f"{rec.get('uid', rec['file'])} — "
                f"{'age unknown (no date)' if age is None else f'{age}d old'} — "
                f"{str(rec.get('title', ''))[:70]}"
            )

    missing_classification = [
        rec.get("uid", rec["file"])
        for rec in adrs
        if not rec.get("subdomain") or not rec.get("focus")
    ]
    status_counts = Counter(str(r.get("status", "MISSING")) for r in adrs)

    lines: list[str] = []
    lines.append("# ADR hygiene audit (D370 / DEC-623f8f)")
    lines.append("")
    lines.append(f"Generated: {now.isoformat()}")
    lines.append(f"ADRs scanned: {len(adrs)}")
    lines.append(f"Status distribution: {dict(sorted(status_counts.items()))}")
    lines.append("")
    lines.append(f"## supersessionIssues ({len(supersession_issues)}) — MUST be 0")
    lines.extend(f"- {s}" for s in supersession_issues) or lines.append("- (none)")
    lines.append("")
    lines.append(f"## stuck 'proposed' (> {STALE_PROPOSED_DAYS}d) ({len(stuck_proposed)})")
    lines.extend(f"- {s}" for s in stuck_proposed) or lines.append("- (none)")
    lines.append("")
    lines.append(f"## advisory — missing subdomain/focus ({len(missing_classification)})")
    lines.append(f"## quarantined duplicates skipped: {quarantined}")
    if dup_uids:
        lines.append(f"## WARNING — duplicate uids: {sorted(set(dup_uids))}")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"ADR hygiene audit - {len(adrs)} ADRs scanned")
    print(f"  status: {dict(sorted(status_counts.items()))}")
    print(f"  supersessionIssues: {len(supersession_issues)}"
          + ("" if not supersession_issues else ""))
    for s in supersession_issues:
        print(f"    x {s}")
    print(f"  stuck-proposed (>{STALE_PROPOSED_DAYS}d): {len(stuck_proposed)}")
    for s in stuck_proposed:
        print(f"    ! {s}")
    print(f"  advisory missing subdomain/focus: {len(missing_classification)}")
    print(f"  quarantined duplicates skipped: {quarantined}")
    if dup_uids:
        print(f"  WARNING duplicate uids: {sorted(set(dup_uids))}")
    print(f"  report: {REPORT_PATH.relative_to(ROOT)}")

    if supersession_issues:
        return 1
    if args.strict and stuck_proposed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
