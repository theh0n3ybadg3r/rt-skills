#!/usr/bin/env python3
"""Flag AI-written tells in generated deliverables (and any markdown / HTML).

Backs `skills/_shared/references/writing-style.md` the way validate.py backs technique-ID claims: a
deterministic check behind model-authored prose. `rt-report` runs this on the rendered deliverables and
revises anything flagged before finalizing; an operator can run it on any document.

Three categories:
  - unicode punctuation: em/en dashes, curly quotes, ellipsis, unicode arrows (checked on raw text)
  - jargon / unearned superlatives: leverage, utilize, seamless, robust, powerful, delve, ...
  - stock phrases: "it's worth noting", "when it comes to", "let's dive in", "not only ... but also", ...

Fenced code blocks, HTML <style>/<script> blocks, inline `code`, and HTML tags are blanked before the
jargon/phrase check (line numbers preserved) so commands and markup do not cause false positives. The
unicode check runs on the raw text, because an em dash anywhere in prose is a tell.

Exit status: 1 if any tell is found, 0 when clean. Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

UNICODE_PUNCT = re.compile(r"[–—‘’“”…→⇒≥≤•]")

# High-signal jargon and unearned superlatives (word-boundary, case-insensitive).
JARGON_TERMS = [
    r"leverag(?:e|es|ed|ing)", r"utili[sz]e[sd]?", r"utili[sz]ing", r"seamless(?:ly)?", r"robust",
    r"powerful", r"cutting[- ]edge", r"state[- ]of[- ]the[- ]art", r"game[- ]?chang(?:er|ing)",
    r"empower(?:s|ed|ing)?", r"unlock(?:s|ed|ing)?", r"elevate(?:s|d)?", r"streamline(?:s|d)?",
    r"effortless(?:ly)?", r"delve(?:s|d)?", r"fast[- ]paced", r"ever[- ]evolving", r"realm",
    r"tapestry", r"testament", r"plethora", r"boasts?", r"holistic", r"synerg(?:y|ies|istic)",
    r"paradigm", r"supercharg(?:e|ed|ing)", r"revolutioni[sz]e[sd]?", r"deep dive", r"dive[- ](?:in|into)",
    r"thrilled", r"excited to",
]
JARGON = re.compile(r"\b(?:" + "|".join(JARGON_TERMS) + r")\b", re.I)

# Stock AI phrasing.
STOCK_TERMS = [
    r"it'?s worth noting", r"worth noting", r"important to note", r"it is important to", r"keep in mind",
    r"that said", r"at the end of the day", r"when it comes to", r"needless to say", r"in conclusion",
    r"let'?s (?:dive|explore|take a look)", r"whether you'?re", r"in today'?s", r"in the world of",
    r"in the realm of", r"look no further", r"rest assured", r"by leveraging",
    r"plays? a (?:key|crucial|vital) role", r"this (?:is|isn'?t) just", r"it'?s not just",
    r"not only\b[^.\n]{0,60}\bbut also",
]
STOCK = re.compile(r"(?:" + "|".join(STOCK_TERMS) + r")", re.I)

CATEGORIES = [("unicode-punct", UNICODE_PUNCT), ("jargon", JARGON), ("stock-phrase", STOCK)]

EXCLUDE_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}
# fixtures are mock external CTI; docs/plans is historical; writing-style.md necessarily lists the tells.
EXCLUDE_SUBSTR = ("_shared/fixtures", "docs/plans", "writing-style.md")


def _blank(m: re.Match) -> str:
    """Replace a matched span with blanks, preserving newline count so line numbers do not shift."""
    return "\n" * m.group(0).count("\n")


def strip_code_and_markup(text: str) -> str:
    """Blank fenced code, <style>/<script> blocks, inline code, and HTML tags (line numbers preserved)."""
    text = re.sub(r"```.*?```", _blank, text, flags=re.S)
    text = re.sub(r"<(style|script)\b.*?</\1>", _blank, text, flags=re.S | re.I)
    text = re.sub(r"`[^`]*`", _blank, text)
    text = re.sub(r"<[^>]+>", _blank, text)
    return text


def scan_text(text: str) -> list[tuple[str, int, str, str]]:
    """Return (category, line_no, term, context) for every tell. Unicode on raw text; the rest on prose."""
    raw_lines = text.splitlines()
    prose_lines = strip_code_and_markup(text).splitlines()
    hits = []
    for name, pat in CATEGORIES:
        lines = raw_lines if name == "unicode-punct" else prose_lines
        for i, line in enumerate(lines, 1):
            for m in pat.finditer(line):
                ctx = raw_lines[i - 1].strip()[:100] if i - 1 < len(raw_lines) else ""
                hits.append((name, i, m.group(0).strip(), ctx))
    return hits


def scan_file(path: Path) -> list[tuple[str, int, str, str]]:
    try:
        return scan_text(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return []


def collect_paths(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            for f in sorted(path.rglob("*")):
                if f.suffix in (".md", ".html") and f.is_file() \
                        and not (EXCLUDE_DIRS & set(f.parts)) \
                        and not any(s in f.as_posix() for s in EXCLUDE_SUBSTR):
                    out.append(f)
        elif path.is_file():
            out.append(path)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Flag AI-written tells in deliverables (markdown / HTML).")
    ap.add_argument("paths", nargs="+", help="files or directories to scan")
    args = ap.parse_args(argv)

    total = 0
    for f in collect_paths(args.paths):
        hits = scan_file(f)
        if not hits:
            continue
        total += len(hits)
        print(f"{f}:")
        for name, line, term, ctx in hits:
            print(f"  {line}: [{name}] {term!r}  |  {ctx}")
    if total:
        print(f"\n{total} AI-tell(s) found. See skills/_shared/references/writing-style.md.")
        return 1
    print("clean: no AI tells found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
