#!/usr/bin/env python3
"""Convert a PDF intel source to markdown via pdfplumber.

The whole extraction pipeline rests on a verbatim-quote contract: `rt-intel` copies a quote exactly
and `rt-verify` re-resolves it as a substring of the cited source. PDF is where that fidelity is most
fragile (column reflow, line-break hyphenation, ligature substitution), so a `.pdf` source is
normalized to markdown up front: one `## Page N` header per page (which keeps the schema's `page`
locator exact) and a normalization pass that folds ligatures, rejoins hyphenated line breaks, and
collapses stray whitespace. The produced `.md` is the single cited source both skills then read.

With `--archive`, the original is moved into a sibling `_ingested/` directory afterward so a later
run or glob will not re-read it. pdfplumber runs locally and makes no network calls, so conversion is
safe on an `engagement-sensitive` run (no new egress).

pdfplumber is a pip dependency (MIT). It is imported lazily, so this module and the other bundled
helpers stay importable without it; only an actual PDF conversion needs it installed.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

from ingest_common import archive_original, archive_path, markdown_output_path

_HYPHEN_LINEBREAK = re.compile(r"(\w)-\n(\w)")
_HORIZONTAL_WS = re.compile(r"[ \t]+")
_AROUND_NEWLINE = re.compile(r" *\n *")
_BLANK_LINES = re.compile(r"\n{3,}")


class PdfplumberMissingError(RuntimeError):
    """Raised when the pdfplumber package is not installed."""


class ConversionError(RuntimeError):
    """Raised when an input is unusable."""


def _require_pdfplumber():
    """Return the pdfplumber module or raise PdfplumberMissingError with an actionable message."""
    try:
        import pdfplumber
    except ImportError as exc:
        raise PdfplumberMissingError(
            "pdfplumber is required to convert PDF sources but is not installed. "
            "Install it (pip install pdfplumber) and re-run."
        ) from exc
    return pdfplumber


def normalize_text(text: str) -> str:
    """Fold ligatures (NFKC), rejoin hyphenated line breaks, and collapse stray whitespace."""
    text = unicodedata.normalize("NFKC", text)
    text = _HYPHEN_LINEBREAK.sub(r"\1\2", text)
    text = _HORIZONTAL_WS.sub(" ", text)
    text = _AROUND_NEWLINE.sub("\n", text)
    text = _BLANK_LINES.sub("\n\n", text)
    return text.strip()


def to_markdown(pdf: Path, archive: bool = False) -> Path:
    """Convert a PDF to page-numbered markdown; optionally archive the original. Returns the .md path."""
    if not pdf.is_file():
        raise ConversionError(f"not a file: {pdf}")
    if pdf.suffix.lower() != ".pdf":
        raise ConversionError(f"expected a .pdf file, got: {pdf}")
    pdfplumber = _require_pdfplumber()
    parts: list[str] = []
    with pdfplumber.open(str(pdf)) as doc:
        for i, page in enumerate(doc.pages, start=1):
            body = normalize_text(page.extract_text() or "")
            parts.append(f"## Page {i}\n\n{body}".rstrip())
    out = markdown_output_path(pdf)
    out.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    if archive:
        archive_original(pdf)
    return out


def _cmd_to_markdown(args: argparse.Namespace) -> int:
    out = to_markdown(Path(args.file), archive=args.archive)
    print(out)
    if args.archive:
        print(f"archived original -> {archive_path(Path(args.file))}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p_md = sub.add_parser("to-markdown", help="convert a PDF source to markdown")
    p_md.add_argument("file", help="path to the .pdf source")
    p_md.add_argument(
        "--archive",
        action="store_true",
        help="move the original pdf into a sibling _ingested/ directory after converting",
    )
    p_md.set_defaults(func=_cmd_to_markdown)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (PdfplumberMissingError, ConversionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
