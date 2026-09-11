"""Tests for pdf_convert.py. Run: python -m unittest -q test_pdf_convert.

The normalization, path, and missing-dependency tests always run (they never invoke pdfplumber). The
round-trip test converts a committed sample.pdf and is skipped when pdfplumber is not installed, so
`make test` stays green on hosts without it.
"""
import builtins
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pdf_convert as pdf

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "sample.pdf"


def _has_pdfplumber() -> bool:
    try:
        import pdfplumber  # noqa: F401

        return True
    except ImportError:
        return False


class Normalize(unittest.TestCase):
    def test_rejoins_hyphenated_line_break(self):
        self.assertEqual(pdf.normalize_text("spear-\nphishing"), "spearphishing")

    def test_folds_ligature(self):
        # U+FB01 is the "fi" ligature; NFKC folds it back to the two ASCII letters.
        self.assertEqual(pdf.normalize_text("ﬁle"), "file")

    def test_collapses_whitespace(self):
        self.assertEqual(pdf.normalize_text("a   b\n\n\n\nc"), "a b\n\nc")


class PathDerivation(unittest.TestCase):
    def test_markdown_output_path(self):
        self.assertEqual(
            pdf.markdown_output_path(Path("/a/b/advisory.pdf")),
            Path("/a/b/advisory.md"),
        )

    def test_archive_path(self):
        self.assertEqual(
            pdf.archive_path(Path("/a/b/advisory.pdf")),
            Path("/a/b/_ingested/advisory.pdf"),
        )


class MissingPdfplumber(unittest.TestCase):
    def _force_missing(self):
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "pdfplumber":
                raise ImportError("no pdfplumber")
            return real_import(name, *args, **kwargs)

        return mock.patch.object(builtins, "__import__", side_effect=fake_import)

    def test_require_raises_actionable_message(self):
        with self._force_missing():
            with self.assertRaises(pdf.PdfplumberMissingError) as ctx:
                pdf._require_pdfplumber()
        self.assertIn("pip install pdfplumber", str(ctx.exception))

    def test_main_exits_2_when_missing(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "source.pdf"
            src.write_bytes(b"%PDF-1.4 stub")  # exists + .pdf, so it reaches the import
            with self._force_missing():
                rc = pdf.main(["to-markdown", str(src)])
        self.assertEqual(rc, 2)


class BadInput(unittest.TestCase):
    def test_rejects_non_pdf(self):
        with tempfile.TemporaryDirectory() as d:
            txt = Path(d) / "source.txt"
            txt.write_text("hi")
            with self.assertRaises(pdf.ConversionError):
                pdf.to_markdown(txt)


@unittest.skipUnless(_has_pdfplumber(), "pdfplumber not installed")
class RoundTrip(unittest.TestCase):
    def test_extracts_page_numbered_markdown_and_archives(self):
        self.assertTrue(FIXTURE.is_file(), "sample.pdf fixture missing")
        with tempfile.TemporaryDirectory() as d:
            work = Path(d) / "sample.pdf"
            shutil.copy(FIXTURE, work)  # never mutate the committed fixture
            out = pdf.to_markdown(work, archive=True)
            text = out.read_text()
            self.assertIn("## Page 1", text)
            self.assertIn("## Page 2", text)
            self.assertIn("spearphishing", text)
            # Original moved out of the way so it is not re-read.
            self.assertFalse(work.exists())
            self.assertTrue(pdf.archive_path(work).exists())


if __name__ == "__main__":
    unittest.main()
