#!/usr/bin/env python3
"""
Regression test suite for ASCII Banner & Stoic Quote HTML Source Easter Egg.

Validates:
1. Presence of ASCII Owl of Athena `(O,o)` and Stoic pun quote
   `"Examine thyself, and inspect thy source."` in HTML comments.
2. Placement immediately following `<!doctype html>` before `<html`.
3. Multi-page coverage: Home (`/index.html`), Hubs (`/books/index.html`, `/tech/index.html`),
   leaf note (`/tech/k8s/index.html`), and directory (`/sitemap/index.html`).
4. Minification preservation under `hugo --gc --minify`.
5. Negative assertions:
   - No unwanted text ("arunsrin's notes", URL, delimiter bars `====`) inside the comment.
   - Zero invalid double hyphens (`--`) within the comment body.
"""

import os
import re
import sys

# Ensure UTF-8 output across Windows and Linux terminals (Rule 12)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    public_dir = os.path.join(root_dir, "public")

    test_pages = [
        os.path.join(public_dir, "index.html"),
        os.path.join(public_dir, "books", "index.html"),
        os.path.join(public_dir, "tech", "index.html"),
        os.path.join(public_dir, "tech", "k8s", "index.html"),
        os.path.join(public_dir, "sitemap", "index.html"),
    ]

    print("--- ASCII Banner & HTML Source Easter Egg Test Suite ---")

    for page_path in test_pages:
        rel_path = os.path.relpath(page_path, root_dir)
        if not os.path.exists(page_path):
            print(f"Error: {rel_path} does not exist. Run 'hugo' first.")
            sys.exit(1)

        with open(page_path, "r", encoding="utf-8") as fp:
            content = fp.read()

        print(f"1. Checking {rel_path}:")

        # Extract the banner comment
        # Hugo minification strips whitespace or renders: <!doctype html><!--! ... --><html
        banner_match = re.search(r'<!doctype\s+html>\s*<!--!(.*?)-->\s*<html', content, re.DOTALL | re.IGNORECASE)
        assert banner_match, f"ASCII banner HTML comment missing or misplaced in {rel_path}"

        comment_body = banner_match.group(1)

        # 1. Verify ASCII Owl
        assert ",___," in comment_body, f"Owl head ',___,' missing from {rel_path}"
        assert "(O,o)" in comment_body, f"Owl face '(O,o)' missing from {rel_path}"
        assert "/)__)" in comment_body, f"Owl body '/)__)' missing from {rel_path}"
        assert '-" "-' in comment_body, f"Owl feet '-\" \"-' missing from {rel_path}"
        print(f"  ✓ ASCII Owl of Athena present in {rel_path}")

        # 2. Verify Stoic pun quote
        assert '"Examine thyself,' in comment_body, f"First line of quote missing from {rel_path}"
        assert 'and inspect thy source."' in comment_body, f"Second line of quote missing from {rel_path}"
        print(f"  ✓ Stoic pun quote 'Examine thyself, and inspect thy source.' present in {rel_path}")

        # 3. Negative assertions (clean minimalist comment - no extra banner box or URL)
        assert "arunsrin's notes" not in comment_body, f"Unwanted site name found in comment in {rel_path}"
        assert "https://www.arunsr.in" not in comment_body, f"Unwanted URL found in comment in {rel_path}"
        assert "====" not in comment_body, f"Unwanted box delimiter found in comment in {rel_path}"

        # 4. Standards compliance: No double hyphens inside comment body
        assert "--" not in comment_body, f"Forbidden double hyphen '--' found inside comment body in {rel_path}"
        print(f"  ✓ Standards compliance and negative assertions verified in {rel_path}")

    print("\n✓ ALL ASCII BANNER HTML SOURCE TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
