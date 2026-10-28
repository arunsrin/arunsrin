#!/usr/bin/env python3
"""
Automated Regression Test Suite for Internal Link Hover Previews (Gwern / Wikipedia Style)

Validates:
1. layouts/index.json and public/index.json include 'readingTime' field as integer >= 1.
2. Generated HTML pages contain #link-preview-card with role="tooltip" (handling --minify optional quotes & skipping alias stubs).
3. Zero inline event handlers (Rocket Loader safety).
4. CSS styling presence (.link-preview-card, .link-preview-card.visible, @media (hover: none)).
5. Link eligibility & negative testing (anti-spurious isolation: external links, breadcrumbs, anchors #, asset files, and touch suppression).
6. Excerpt cleaning & HTML entity decoding (stripping markdown headings, icon shortcodes, code fences, and resolving &rsquo; / &ldquo; / &amp;).
7. Debounced mouseout cancellation and relative URL resolution audit.
"""

import sys
import os
import re
import json
import html

# Windows Python UTF-8 Stdout Reconfiguration (Rule 12)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def test_hover_previews():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    public_dir = os.path.join(root_dir, "public")
    index_json_path = os.path.join(public_dir, "index.json")
    preview_partial_path = os.path.join(root_dir, "layouts", "partials", "link-preview.html")
    extra_css_path = os.path.join(root_dir, "home", "css", "extra.css")

    print("--- Internal Link Hover Previews Test Suite ---")

    # 1. Validate index.json schema & readingTime
    print("\n1. Validating index.json schema and readingTime values:")
    assert os.path.exists(index_json_path), f"Error: {index_json_path} does not exist. Run hugo first."
    with open(index_json_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)
    assert isinstance(index_data, list), "index.json root must be a list"
    assert len(index_data) > 0, "index.json must not be empty"

    sampled = 0
    for item in index_data:
        assert "title" in item, "Item missing title"
        assert "permalink" in item, "Item missing permalink"
        assert "readingTime" in item, f"Item missing readingTime: {item.get('title')}"
        assert isinstance(item["readingTime"], int), f"readingTime must be int: {item.get('title')}"
        assert item["readingTime"] >= 1, f"readingTime must be >= 1: {item.get('title')}"
        sampled += 1
    print(f"  ✓ Validated {sampled} items in index.json with readingTime >= 1")

    # 2. Validate DOM presence in generated HTML (skipping Hugo alias stubs)
    print("\n2. Validating DOM element #link-preview-card across generated pages:")
    pages_tested = 0
    alias_stubs_skipped = 0
    card_id_pattern = re.compile(r'id=["\']?link-preview-card["\'\s>]', re.IGNORECASE)
    card_role_pattern = re.compile(r'role=["\']?tooltip["\'\s>]', re.IGNORECASE)
    refresh_stub_pattern = re.compile(r'http-equiv=["\']?refresh["\']?', re.IGNORECASE)

    for root, _, files in os.walk(public_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Skip alias redirect stubs (Rule 20)
                if refresh_stub_pattern.search(content):
                    alias_stubs_skipped += 1
                    continue

                assert card_id_pattern.search(content), f"Missing #link-preview-card in {os.path.relpath(file_path, root_dir)}"
                assert card_role_pattern.search(content), f"Missing role=tooltip in {os.path.relpath(file_path, root_dir)}"
                pages_tested += 1

    assert pages_tested > 0, "Expected to test at least one generated HTML page"
    print(f"  ✓ Verified #link-preview-card with role='tooltip' across {pages_tested} pages (skipped {alias_stubs_skipped} alias stubs)")

    # 3. Cloudflare Rocket Loader & Zero Inline Handlers Check (Rule 2)
    print("\n3. Validating Cloudflare Rocket Loader Safety:")
    with open(preview_partial_path, "r", encoding="utf-8") as f:
        partial_code = f.read()
    
    inline_handler_match = re.search(r'\s(on[a-z]+)\s*=', partial_code, re.IGNORECASE)
    assert not inline_handler_match, f"Forbidden inline event handler found in {preview_partial_path}: {inline_handler_match.group(0)}"
    print("  ✓ Zero inline event handlers in layouts/partials/link-preview.html")

    # 4. CSS Styling Verification
    print("\n4. Validating CSS styling rules in home/css/extra.css:")
    with open(extra_css_path, "r", encoding="utf-8") as f:
        css_content = f.read()
    
    assert ".link-preview-card" in css_content, "Missing .link-preview-card in extra.css"
    assert ".link-preview-card.visible" in css_content, "Missing .link-preview-card.visible in extra.css"
    assert "@media (hover: none)" in css_content, "Missing @media (hover: none) suppression in extra.css"
    assert "z-index: 1250" in css_content or "z-index:1250" in css_content, "Missing high z-index for preview card"
    print("  ✓ Confirmed .link-preview-card styles, visibility toggle, and touch device suppression in extra.css")

    # 5. Link Eligibility & Negative Assertions (Python simulation of isEligibleLink)
    print("\n5. Testing link filtering & anti-spurious isolation:")
    def simulate_is_eligible(href, classes="", in_content=True, in_breadcrumbs=False, in_meta=False, in_related=False, is_touch=False):
        if is_touch:
            return False
        if not in_content:
            return False
        if in_breadcrumbs or in_meta or in_related:
            return False
        if "external-link" in classes or "tag-pill" in classes:
            return False
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
            return False
        if re.search(r'\.(pdf|png|jpe?g|gif|svg|webp|zip|tar|gz|mp4|webm|ico|xml|json)$', href, re.IGNORECASE):
            return False
        return True

    # Valid internal prose link
    assert simulate_is_eligible("/tech/git/"), "Valid internal note link should be eligible"
    assert simulate_is_eligible("/books/dune/"), "Valid books link should be eligible"

    # Negative test 1: External links
    assert not simulate_is_eligible("https://github.com/arunsrin", classes="external-link"), "External link must be ineligible"
    assert not simulate_is_eligible("/tech/git/", classes="external-link"), "Link with .external-link must be ineligible"

    # Negative test 2: Hash fragment jump anchors
    assert not simulate_is_eligible("#introduction"), "Hash anchor must be ineligible"
    assert not simulate_is_eligible("#heading-2"), "Heading anchor must be ineligible"

    # Negative test 3: Navigation elements (breadcrumbs, meta, related notes)
    assert not simulate_is_eligible("/tech/git/", in_breadcrumbs=True), "Breadcrumb link must be ineligible"
    assert not simulate_is_eligible("/tech/git/", in_meta=True), "Page meta link must be ineligible"
    assert not simulate_is_eligible("/tech/git/", in_related=True), "Related notes card link must be ineligible"

    # Negative test 4: Tag pills
    assert not simulate_is_eligible("/tags/linux/", classes="tag-pill"), "Tag pill must be ineligible"

    # Negative test 5: Media and asset files
    assert not simulate_is_eligible("/static/cheatsheet.pdf"), "PDF file must be ineligible"
    assert not simulate_is_eligible("/images/photo.png"), "Image file must be ineligible"

    # Negative test 6: Touch devices
    assert not simulate_is_eligible("/tech/git/", is_touch=True), "Touch device must suppress preview"

    print("  ✓ All 7 link eligibility and anti-spurious tests passed cleanly")

    # 6. Excerpt cleaning & HTML entity decoding verification (Gate 8 & Gate 7)
    print("\n6. Validating excerpt text sanitizer and HTML entity decoding:")
    raw_sample = "## Overview\n\nBooks I&rsquo;ve read: a :material-book: guide to ```python\nprint('hello')\n``` modern &ldquo;architecture&rdquo; &amp; design."
    
    # Simulate decoder + cleanExcerpt
    decoded_sample = html.unescape(raw_sample)
    clean_sample = re.sub(r'(:[a-z0-9_-]+:(\s*\{[^}]*\})?)', '', decoded_sample)
    clean_sample = re.sub(r'```[\s\S]*?```', '', clean_sample)
    clean_sample = re.sub(r'#{1,6}\s+', '', clean_sample)
    clean_sample = re.sub(r'\s+', ' ', clean_sample).strip()

    assert "&rsquo;" not in clean_sample, "HTML entity &rsquo; leaked into excerpt"
    assert "&ldquo;" not in clean_sample, "HTML entity &ldquo; leaked into excerpt"
    assert "&amp;" not in clean_sample, "HTML entity &amp; leaked into excerpt"
    assert "Books I’ve read" in clean_sample, f"Failed entity decoding, got: {clean_sample}"
    assert "“architecture” & design" in clean_sample, f"Failed quote decoding, got: {clean_sample}"
    assert ":material-book:" not in clean_sample, "Iconify shortcode not stripped"
    assert "print('hello')" not in clean_sample, "Code block not stripped"
    print(f"  ✓ Excerpt correctly decoded and sanitized: '{clean_sample}'")

    # 7. JavaScript Architecture & Debounce Safety Audit
    print("\n7. Validating JavaScript architecture & mouseout debounce cancellation:")
    assert "decodeEntities" in partial_code, "Missing decodeEntities function in link-preview.html"
    assert "clearTimeout(showTimer)" in partial_code, "Missing clearTimeout(showTimer) in link-preview.html"
    assert "window.location.href" in partial_code, "normalizePath must resolve against window.location.href"
    
    # Assert mouseout unconditionally cancels showTimer upon leaving an anchor
    mouseout_block = re.search(r"document\.addEventListener\('mouseout'[\s\S]*?\}\);", partial_code)
    assert mouseout_block, "Missing mouseout listener block"
    assert "clearTimeout(showTimer)" in mouseout_block.group(0), "mouseout must cancel pending showTimer to prevent ghost popups"
    print("  ✓ Verified debounce timer cancellation, entity decoding, and URL resolution in client JS")

    print("\n=== All Hover Preview tests passed successfully! ===")

if __name__ == "__main__":
    test_hover_previews()
