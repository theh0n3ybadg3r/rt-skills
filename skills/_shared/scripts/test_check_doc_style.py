"""Offline tests for check_doc_style.py. Run: python -m unittest -q test_check_doc_style."""
import unittest

import check_doc_style as c


def cats(text):
    return {name for name, _, _, _ in c.scan_text(text)}


class Clean(unittest.TestCase):
    def test_plain_prose_passes(self):
        text = "The red team reached both flags. Attachment delivery was blocked; a link variant succeeded."
        self.assertEqual(c.scan_text(text), [])


class Tells(unittest.TestCase):
    def test_em_dash_flagged(self):
        self.assertIn("unicode-punct", cats("The gate is fail-closed — nothing passes unverified."))

    def test_jargon_flagged(self):
        self.assertIn("jargon", cats("We leverage a powerful, seamless detection pipeline."))

    def test_utilize_flagged(self):
        self.assertIn("jargon", cats("The operator will utilize the console."))

    def test_stock_phrase_flagged(self):
        self.assertIn("stock-phrase", cats("It's worth noting that when it comes to custody, keys matter."))

    def test_not_only_but_also_flagged(self):
        self.assertIn("stock-phrase", cats("Not only did it reach the flag, but also it evaded response."))

    def test_all_three_categories_and_nonzero_exit(self):
        text = "It's worth noting we leverage a robust approach — truly seamless."
        self.assertEqual(cats(text), {"unicode-punct", "jargon", "stock-phrase"})


class CodeAndMarkupIgnored(unittest.TestCase):
    def test_jargon_inside_fenced_code_ignored(self):
        text = "Run the check.\n\n```\nleverage --utilize --robust\n```\n\nDone."
        self.assertEqual(c.scan_text(text), [])

    def test_jargon_inside_inline_code_ignored(self):
        self.assertEqual(c.scan_text("Pass the `leverage` flag to the tool."), [])

    def test_jargon_inside_html_tag_ignored(self):
        # attribute value in a tag is markup, not prose
        self.assertEqual(c.scan_text('<div class="robust-card">Reached the flag.</div>'), [])

    def test_style_block_ignored(self):
        text = "<p>Reached the flag.</p>\n<style>\n.powerful { color: red; }\n</style>"
        self.assertEqual(c.scan_text(text), [])

    def test_line_numbers_preserved_after_code_block(self):
        text = "```\ncode\n```\nWe leverage this."
        hits = [h for h in c.scan_text(text) if h[0] == "jargon"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0][1], 4)  # 'leverage' is on line 4

    def test_em_dash_in_code_still_flagged(self):
        # unicode punctuation is checked on raw text, even in code
        self.assertIn("unicode-punct", cats("```\na — b\n```"))


if __name__ == "__main__":
    unittest.main()
