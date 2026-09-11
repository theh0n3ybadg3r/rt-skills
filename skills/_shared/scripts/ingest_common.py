#!/usr/bin/env python3
"""Shared source-to-markdown ingest convention (used by pandoc_convert and pdf_convert).

Converting an intel source to markdown writes the `.md` beside the original and, when archiving,
moves the original into a sibling `_ingested/` directory so a later run or glob will not re-read it.
This is the single source of truth for that convention across the docx (pandoc) and pdf (pdfplumber)
ingest helpers. Stdlib only.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ARCHIVE_DIRNAME = "_ingested"


def markdown_output_path(src: Path) -> Path:
    """The .md path a source converts to (beside the original)."""
    return src.with_suffix(".md")


def archive_path(src: Path) -> Path:
    """Where an ingested original is moved to (sibling `_ingested/` directory)."""
    return src.parent / ARCHIVE_DIRNAME / src.name


def archive_original(src: Path) -> Path:
    """Move the original source into its sibling `_ingested/` directory. Returns the new path."""
    dest = archive_path(src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    shutil.move(str(src), str(dest))
    return dest
