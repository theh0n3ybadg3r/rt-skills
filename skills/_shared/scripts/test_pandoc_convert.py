"""Tests for pandoc_convert.py. Run: python -m unittest -q test_pandoc_convert.

The pure-logic tests (path derivation, the missing-pandoc error path) always run. The round-trip
tests actually invoke pandoc and are skipped when pandoc is not on PATH, so `make test` stays green
on hosts without it.
"""
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import pandoc_convert as pc


class PathDerivation(unittest.TestCase):
    def test_markdown_output_path(self):
        self.assertEqual(
            pc.markdown_output_path(Path("/a/b/advisory.docx")),
            Path("/a/b/advisory.md"),
        )

    def test_archive_path_is_sibling_ingested_dir(self):
        self.assertEqual(
            pc.archive_path(Path("/a/b/advisory.docx")),
            Path("/a/b/_ingested/advisory.docx"),
        )

    def test_docx_output_path_beside_source(self):
        self.assertEqual(
            pc.docx_output_path(Path("/a/b/engagement-report.md"), None),
            Path("/a/b/engagement-report.docx"),
        )

    def test_docx_output_path_into_out_dir(self):
        self.assertEqual(
            pc.docx_output_path(Path("/a/b/engagement-report.md"), Path("/out")),
            Path("/out/engagement-report.docx"),
        )


class MissingPandoc(unittest.TestCase):
    def test_require_pandoc_raises_actionable_message(self):
        with mock.patch.object(pc.shutil, "which", return_value=None):
            with self.assertRaises(pc.PandocMissingError) as ctx:
                pc.require_pandoc()
        self.assertIn("pandoc is required", str(ctx.exception))

    def test_main_exits_2_when_pandoc_missing(self):
        with tempfile.TemporaryDirectory() as d:
            docx = Path(d) / "source.docx"
            docx.write_bytes(b"stub")  # exists + .docx, so it reaches the pandoc call
            with mock.patch.object(pc.shutil, "which", return_value=None):
                rc = pc.main(["to-markdown", str(docx)])
        self.assertEqual(rc, 2)


class BadInput(unittest.TestCase):
    def test_to_markdown_rejects_non_docx(self):
        with tempfile.TemporaryDirectory() as d:
            txt = Path(d) / "source.txt"
            txt.write_text("hello")
            with self.assertRaises(pc.ConversionError):
                pc.to_markdown(txt)

    def test_to_markdown_rejects_missing_file(self):
        with self.assertRaises(pc.ConversionError):
            pc.to_markdown(Path("/does/not/exist.docx"))


@unittest.skipUnless(pc.find_pandoc(), "pandoc not installed")
class RoundTrip(unittest.TestCase):
    def test_md_to_docx_produces_openable_docx(self):
        with tempfile.TemporaryDirectory() as d:
            md = Path(d) / "report.md"
            md.write_text("# Title\n\nHello pandoc, this is a report.\n")
            (docx,) = pc.to_docx([md])
            self.assertTrue(docx.exists())
            # A valid docx is a zip whose payload includes the main document part.
            with zipfile.ZipFile(docx) as zf:
                self.assertIn("word/document.xml", zf.namelist())

    def test_docx_to_markdown_recovers_text_and_archives(self):
        with tempfile.TemporaryDirectory() as d:
            md = Path(d) / "source.md"
            md.write_text("# Advisory\n\nThreat actor used spearphishing.\n")
            (docx,) = pc.to_docx([md])
            out = pc.to_markdown(docx, archive=True)
            self.assertTrue(out.exists())
            self.assertIn("spearphishing", out.read_text())
            # Original moved out of the way so it is not re-read.
            self.assertFalse(docx.exists())
            self.assertTrue(pc.archive_path(docx).exists())


if __name__ == "__main__":
    unittest.main()
