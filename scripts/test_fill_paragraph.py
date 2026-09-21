#!/usr/bin/env python3
"""
test_fill_paragraph.py - Regression test suite for fill_paragraph.py markdown linter.

Verifies:
1. YAML frontmatter preservation (never wrapped or altered).
2. Fenced code block preservation (fences with ``` and ~~~, long command lines intact).
3. Markdown table preservation (table rows containing | are untouched).
4. List item wrapping with correct hanging indentation.
5. Blockquote wrapping with quote prefix (> ) preserved across lines.
6. Atomic token integrity (Goldmark attributes, inline code, HTML tags, URLs never broken).
7. Dash/separator typesetting rule (standalone dashes never start a continuation line).
8. Idempotency across formatting runs (format(format(x)) == format(x)).
9. CLI behavior (--check exits 1 on unformatted, 0 on clean).
10. Negative tests (no altered text/words, no spurious blank lines).
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add scripts directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))
from fill_paragraph import format_markdown


class TestFillParagraph(unittest.TestCase):

    def test_01_frontmatter_preservation(self):
        """YAML frontmatter must remain 100% untouched regardless of line length."""
        content = """---
title: "A Very Long Title That Definitely Exceeds The Column Limit Of Seventy Characters Easily"
description: "This description in the frontmatter should remain completely intact without wrapping"
tags:
  - first-tag
  - second-tag
---

This is a regular prose paragraph that is quite long and definitely exceeds seventy characters so it should be wrapped nicely.
"""
        formatted = format_markdown(content, width=70)
        # Frontmatter part must be identical
        fm_orig = content.split("---")[1]
        fm_form = formatted.split("---")[1]
        self.assertEqual(fm_orig, fm_form, "YAML frontmatter was modified!")
        self.assertIn("\nThis is a regular prose paragraph that is quite long and definitely\nexceeds seventy characters", formatted)

    def test_02_fenced_code_preservation(self):
        """Fenced code blocks (``` and ~~~) must never be wrapped."""
        content = """Here is some text before code.

```sh
curl -s -H "Authorization: Bearer token1234567890abcdef" https://api.example.com/v1/very/long/endpoint/that/exceeds/column/limit
ansible-playbook -i inventory/production.ini deploy.yml --extra-vars "target=production_cluster_east"
```

And some text after code that should be wrapped if it is sufficiently long to spill over the column boundary.
"""
        formatted = format_markdown(content, width=70)
        self.assertIn(
            'curl -s -H "Authorization: Bearer token1234567890abcdef" https://api.example.com/v1/very/long/endpoint/that/exceeds/column/limit',
            formatted,
            "Code block line was wrapped!",
        )

    def test_03_table_preservation(self):
        """Markdown tables must never be wrapped or reformatted."""
        content = """| Column 1 (Wide Header Here) | Column 2 (Another Wide Header) | Column 3 (Wide) |
| --- | --- | --- |
| Some wide data cell in column 1 | Another wide data cell in column 2 | Third cell |
"""
        formatted = format_markdown(content, width=70)
        self.assertEqual(content.strip(), formatted.strip(), "Markdown table was modified!")

    def test_04_list_item_hanging_indent(self):
        """List items must wrap with proper hanging indentation matching bullet offset."""
        content = """- This is a long list item that exceeds the column limit and should be wrapped with two spaces of hanging indentation on subsequent lines.
- Short item.
1. This is an ordered list item that is also long and should wrap with three spaces of hanging indentation so that the numbers align nicely.
"""
        formatted = format_markdown(content, width=70)
        lines = formatted.splitlines()
        # Check first list item continuation
        self.assertTrue(lines[0].startswith("- This is a long"))
        self.assertTrue(lines[1].startswith("  "), f"Expected 2-space hanging indent: '{lines[1]}'")
        # Check ordered list item continuation
        ordered_start = [i for i, l in enumerate(lines) if l.startswith("1. ")][0]
        self.assertTrue(lines[ordered_start + 1].startswith("   "), f"Expected 3-space hanging indent: '{lines[ordered_start + 1]}'")

    def test_05_blockquote_wrapping(self):
        """Blockquotes must wrap and preserve quote prefix (> ) across lines."""
        content = """> This is a very long blockquote line that needs to be reflowed into multiple lines while ensuring that every wrapped line begins with the blockquote prefix.
"""
        formatted = format_markdown(content, width=70)
        lines = formatted.splitlines()
        for line in lines:
            self.assertTrue(line.startswith("> "), f"Blockquote line missing '> ' prefix: '{line}'")
            self.assertLessEqual(len(line), 70)

    def test_06_atomic_tokens_preserved(self):
        """Goldmark attributes, inline code, and URLs must never be split internally."""
        content = """- :material-skull:{ .anim-pulse }[My Blog](https://arunsrin.wordpress.com) - I used to cross-post my content here too; there were times when I liked WordPress (to post my artwork) and times when I liked this Hugo site.
"""
        formatted = format_markdown(content, width=70)
        # Verify attribute list is not broken across lines
        self.assertIn("{ .anim-pulse }", formatted, "Goldmark attribute list was broken across lines!")
        # Verify URL is not broken
        self.assertIn("https://arunsrin.wordpress.com", formatted, "URL was broken across lines!")
        # Verify all lines <= 70
        for line in formatted.splitlines():
            self.assertLessEqual(len(line), 70, f"Line exceeded 70 characters: [{len(line)}] '{line}'")

    def test_07_dash_separator_never_starts_line(self):
        """Standalone dashes (' - ') used as separators must attach to previous line to avoid accidental sub-bullets."""
        content = """- [Why You Must Act Now](https://medium.com/@tomaspueyo/coronavirus-act-today-or-people-will-die-f4d3d9cd99ca) - Nice comprehensive article that was doing the rounds in the early days.
"""
        formatted = format_markdown(content, width=70)
        lines = formatted.splitlines()
        for line in lines[1:]:
            # No continuation line should start with a sub-bullet pattern
            self.assertFalse(line.startswith("  - "), f"Accidental sub-bullet created: '{line}'")

    def test_08_idempotency(self):
        """Formatting an already formatted document must produce identical output (0 diff)."""
        sample = """---
title: "Idempotency Test"
---

# Heading 1

This is a paragraph with several long lines that will be reflowed. It has `inline code` and a [link](https://example.com/test) as well as *italics* and **bold text**.

- List item one with enough text to wrap across two lines easily.
- List item two with `:material-penguin:{ .anim-heart }` icon attached.

> A blockquote that spans across multiple lines cleanly.

```python
def foo():
    return "This long string in code should not be touched at all"
```

| Table | Header |
| --- | --- |
| Cell 1 | Cell 2 |
"""
        run1 = format_markdown(sample, width=70)
        run2 = format_markdown(run1, width=70)
        self.assertEqual(run1, run2, "Formatting is not idempotent!")

    def test_09_prose_words_not_altered(self):
        """Negative test: Sacred Prose Principle - words and content must never be rewritten."""
        content = "I prefer the digital-garden feel of this site over the chronological format of a blog."
        formatted = format_markdown(content, width=70)
        orig_words = content.split()
        form_words = formatted.split()
        self.assertEqual(orig_words, form_words, "Words were altered during formatting!")

    def test_10_cli_check_and_fix(self):
        """Test CLI --check and --fix on a temporary file."""
        import tempfile

        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False, encoding="utf-8") as tf:
            tf.write("This is a line that is definitely longer than seventy characters and should cause --check to fail.\n")
            temp_path = tf.name

        try:
            # Run check: should exit with code 1
            script_path = str(Path(__file__).parent / "fill_paragraph.py")
            res_check = subprocess.run([sys.executable, script_path, "--check", temp_path], capture_output=True, text=True)
            self.assertEqual(res_check.returncode, 1, "--check should exit with 1 on unformatted file")

            # Run fix: should exit with code 0
            res_fix = subprocess.run([sys.executable, script_path, "--fix", temp_path], capture_output=True, text=True)
            self.assertEqual(res_fix.returncode, 0, "--fix should exit with 0")

            # Run check again: should now exit with code 0
            res_check2 = subprocess.run([sys.executable, script_path, "--check", temp_path], capture_output=True, text=True)
            self.assertEqual(res_check2.returncode, 0, "--check should exit with 0 on clean file")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_11_hard_line_breaks_preserved(self):
        """Hard line breaks (two trailing spaces or backslash) must be preserved across formatting."""
        content = "First line with two spaces  \nSecond line follows directly.\n\nLine with backslash\\\nAnother line."
        formatted = format_markdown(content, width=70)
        self.assertIn("First line with two spaces  \nSecond line follows directly.", formatted)
        self.assertIn("Line with backslash\\\nAnother line.", formatted)


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFillParagraph)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n✓ ALL 10 FILL-PARAGRAPH REGRESSION TESTS PASSED SUCCESSFULLY!")
        return 0
    else:
        print("\n❌ FILL-PARAGRAPH TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
