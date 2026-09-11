#!/usr/bin/env python3
"""Convert documents between markdown and docx via pandoc.

Two mechanical, deterministic jobs, both thin wrappers around the `pandoc` binary:

- `to-markdown <file.docx> [--archive]`: convert a docx intel source to GitHub-flavored markdown so
  the agent can read it (docx is a zip of XML the agent cannot read natively). With `--archive`, move
  the original docx into a sibling `_ingested/` directory afterward so a later run or glob will not
  re-read it.
- `to-docx <file.md> [<file.md> ...] [--out <dir>]`: render human documents (deliverables, intake,
  engagement artifact) to docx for readers who want an editable Word file.

pandoc is an external prerequisite, not bundled. It runs locally and makes no network calls, so
conversion is safe on an `engagement-sensitive` run (no new egress). If pandoc is not on PATH this
helper exits non-zero with an actionable message rather than falling back silently.

The helper's own code is stdlib only (subprocess, shutil, argparse), for Claude Code + Codex
portability; pandoc is the only external tool it shells to.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from ingest_common import archive_original, archive_path, markdown_output_path


class PandocMissingError(RuntimeError):
    """Raised when the pandoc binary is not on PATH."""


class ConversionError(RuntimeError):
    """Raised when an input is unusable or a pandoc invocation fails."""


def find_pandoc() -> str | None:
    """Return the pandoc executable path, or None if it is not on PATH."""
    return shutil.which("pandoc")


def require_pandoc() -> str:
    """Return the pandoc path or raise PandocMissingError with an actionable message."""
    pandoc = find_pandoc()
    if pandoc is None:
        raise PandocMissingError(
            "pandoc is required for document conversion but was not found on PATH. "
            "Install it (https://pandoc.org/installing.html) and re-run."
        )
    return pandoc


def docx_output_path(md: Path, out_dir: Path | None) -> Path:
    """The .docx path a markdown file renders to (in out_dir, else beside the source)."""
    parent = out_dir if out_dir is not None else md.parent
    return parent / (md.stem + ".docx")


def _run_pandoc(args: list[str]) -> None:
    pandoc = require_pandoc()
    result = subprocess.run(
        [pandoc, *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise ConversionError(
            f"pandoc failed ({result.returncode}): {result.stderr.strip()}"
        )


def to_markdown(docx: Path, archive: bool = False) -> Path:
    """Convert a docx to markdown; optionally archive the original. Returns the .md path."""
    if not docx.is_file():
        raise ConversionError(f"not a file: {docx}")
    if docx.suffix.lower() != ".docx":
        raise ConversionError(f"expected a .docx file, got: {docx}")
    out = markdown_output_path(docx)
    _run_pandoc([str(docx), "-f", "docx", "-t", "gfm", "-o", str(out)])
    if archive:
        archive_original(docx)
    return out


def to_docx(md_paths: list[Path], out_dir: Path | None = None) -> list[Path]:
    """Render each markdown file to docx. Returns the .docx paths."""
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for md in md_paths:
        if not md.is_file():
            raise ConversionError(f"not a file: {md}")
        dest = docx_output_path(md, out_dir)
        _run_pandoc([str(md), "-f", "gfm", "-o", str(dest)])
        outputs.append(dest)
    return outputs


def _cmd_to_markdown(args: argparse.Namespace) -> int:
    out = to_markdown(Path(args.file), archive=args.archive)
    print(out)
    if args.archive:
        print(f"archived original -> {archive_path(Path(args.file))}")
    return 0


def _cmd_to_docx(args: argparse.Namespace) -> int:
    out_dir = Path(args.out) if args.out else None
    for dest in to_docx([Path(p) for p in args.files], out_dir):
        print(dest)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_md = sub.add_parser("to-markdown", help="convert a docx source to markdown")
    p_md.add_argument("file", help="path to the .docx source")
    p_md.add_argument(
        "--archive",
        action="store_true",
        help="move the original docx into a sibling _ingested/ directory after converting",
    )
    p_md.set_defaults(func=_cmd_to_markdown)

    p_docx = sub.add_parser("to-docx", help="render markdown documents to docx")
    p_docx.add_argument("files", nargs="+", help="one or more markdown files")
    p_docx.add_argument(
        "--out", help="output directory (default: beside each source)", default=None
    )
    p_docx.set_defaults(func=_cmd_to_docx)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (PandocMissingError, ConversionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
