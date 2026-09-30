#!/usr/bin/env python3
"""Mechanical frontmatter sweep for DEC-e0a8ca (TSK-d3dd83). Dry run by default.

Applies only the rules that need no judgement; every other offender is listed
for its owning controller. Rules (see the ADR for the mapping table):

  adr        drop the `authority` key (an ADR's force is its status)
  generated  authority `source-derived` -> `generated`
  docket     add `authority: reference` after `authority_role`; status
             `verification_required` -> `draft`
  chapter    authority `derived`|`informative`|`descriptive` -> `reference`,
             `draft-authoritative` -> `authoritative`; status `draft-for-review`
             -> `reviewing`, `draft` -> `drafting`
  evidence   authority: a value that is a DEC citation or free text moves to
             `governing_adrs` (the DEC uids found in it) and `authority` becomes
             `evidentiary`; a missing `authority` becomes `evidentiary`;
             status `draft`|`proposed`|`plan`|`open` -> `drafting`,
             `complete`|`closed`|`executed`|`accepted`|`approved`|`applied`|
             `implemented`|`decided`|`closeout_complete`|`locked` -> `locked`
  archive    status -> `retired`

Everything else (a chapter with no `authority`, a status like `active` or
`living`, an evidence record `held` at an operator gate) is a judgement call
and is only reported. `--apply` writes; the frontmatter check must be run
after and the baseline shrunk by hand (`audit_frontmatter.py` reports the
entries that became clean). Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_frontmatter import DOCS, check_file, classify, parse_frontmatter  # noqa: E402

DEC_RE = re.compile(r"DEC-[0-9a-f]{6}")
CHAPTER_AUTH = {"derived": "reference", "informative": "reference", "descriptive": "reference",
                "draft-authoritative": "authoritative"}
CHAPTER_STATUS = {"draft-for-review": "reviewing", "draft": "drafting"}
EVIDENCE_STATUS = {
    **{s: "drafting" for s in ("draft", "proposed", "plan", "open")},
    **{s: "locked" for s in ("complete", "closed", "executed", "accepted", "approved", "applied",
                             "implemented", "decided", "closeout_complete", "locked")},
}


def split(text: str):
    """Returns (frontmatter lines, rest) or None when there is no block."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return None


def set_key(fm: list[str], key: str, value: str, after: str | None = None) -> list[str]:
    pat = re.compile(rf"^{key}:\s")
    if any(pat.match(l) for l in fm):
        return [f"{key}: {value}" if pat.match(l) else l for l in fm]
    if after:
        for i, l in enumerate(fm):
            if l.startswith(after + ":"):
                return fm[:i + 1] + [f"{key}: {value}"] + fm[i + 1:]
    return fm + [f"{key}: {value}"]


def drop_key(fm: list[str], key: str) -> list[str]:
    return [l for l in fm if not re.match(rf"^{key}:\s", l) and l.rstrip() != f"{key}:"]


def rewrite(kind: str, fm: list[str], d: dict) -> list[str] | None:
    """Returns the new frontmatter lines, or None when no mechanical rule applies."""
    out = list(fm)
    a, s = d.get("authority"), d.get("status")
    if kind == "adr":
        if a is not None:
            out = drop_key(out, "authority")
    elif kind == "generated":
        if a == "source-derived":
            out = set_key(out, "authority", "generated")
    elif kind == "docket":
        if a is None:
            out = set_key(out, "authority", "reference", after="authority_role")
        if s == "verification_required":
            out = set_key(out, "status", "draft")
    elif kind == "chapter":
        if a in CHAPTER_AUTH:
            out = set_key(out, "authority", CHAPTER_AUTH[a])
        if s in CHAPTER_STATUS:
            out = set_key(out, "status", CHAPTER_STATUS[s])
    elif kind == "evidence":
        if a != "evidentiary":
            uids = sorted(set(DEC_RE.findall(a or "")))
            if uids and "governing_adrs" not in d:
                out = set_key(out, "governing_adrs", "[" + ", ".join(uids) + "]")
            out = set_key(out, "authority", "evidentiary")
        if s in EVIDENCE_STATUS:
            out = set_key(out, "status", EVIDENCE_STATUS[s])
    elif kind == "archive":
        if s != "retired":
            out = set_key(out, "status", "retired")
    return None if out == fm else out


def main() -> int:
    ap = argparse.ArgumentParser(description="Mechanical frontmatter sweep (DEC-e0a8ca).")
    ap.add_argument("--apply", action="store_true", help="write the files (default: dry run)")
    ap.add_argument("--kind", help="restrict to one kind")
    ap.add_argument("--only", help="restrict to one file (path relative to docs/), for one-then-many")
    args = ap.parse_args()

    changed, cleaned, still, judgement = Counter(), Counter(), Counter(), []
    for path in sorted(DOCS.rglob("*.md")):
        rel = path.relative_to(DOCS).as_posix()
        kind = classify(rel)
        if kind is None or (args.kind and kind != args.kind) or (args.only and rel != args.only):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        parts = split(text)
        d = parse_frontmatter(text)
        if parts is None or d is None:
            if check_file(kind, d):
                judgement.append(f"[{kind}] {rel}: no frontmatter block")
            continue
        if not check_file(kind, d):
            continue
        new_fm = rewrite(kind, parts[0], d)
        if new_fm is None:
            judgement.append(f"[{kind}] {rel}: " + "; ".join(check_file(kind, d)))
            continue
        new_text = "---\n" + "\n".join(new_fm) + "\n---\n" + parts[1]
        remaining = check_file(kind, parse_frontmatter(new_text))
        changed[kind] += 1
        (cleaned if not remaining else still)[kind] += 1
        if remaining:
            judgement.append(f"[{kind}] {rel} (after sweep): " + "; ".join(remaining))
        if args.apply:
            path.write_text(new_text, encoding="utf-8")

    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"Frontmatter sweep ({mode})")
    print(f"  files rewritten: {sum(changed.values())} {dict(sorted(changed.items()))}")
    print(f"  clean after the sweep: {sum(cleaned.values())} {dict(sorted(cleaned.items()))}")
    print(f"  rewritten but still needing judgement: {sum(still.values())} {dict(sorted(still.items()))}")
    print(f"  judgement calls (not touched): {len(judgement)}")
    for j in judgement:
        print(f"    ? {j}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
