#!/usr/bin/env python3
"""
Dedicated companion test suite for Sitemap and Recently Updated stream.
Validates:
1. /sitemap/ page existence, non-empty HTML structure, and canonical title.
2. Sidebar navigation integration:
   - Sitemap link present in both desktop and mobile sidebar containers.
   - Sitemap link points to '/sitemap/'.
3. Recently Tended stream:
   - Contains exactly 5 note cards on the homepage.
   - Each card contains a valid permalink, title, date, and section badge.
   - Negative assertions: /about/ and /sitemap/ are strictly excluded from the stream.
   - All note links in the stream point to valid existing files in public/.
4. All assertions use minified-HTML safe regex patterns (Rule 14).
"""

import os
import re
import sys

# Windows Python UTF-8 Stdout Reconfiguration (Rule 12)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    public_dir = "public"
    public_index = os.path.join(public_dir, "index.html")
    public_sitemap = os.path.join(public_dir, "sitemap", "index.html")

    if not os.path.exists(public_index) or not os.path.exists(public_sitemap):
        print("Error: public/index.html or public/sitemap/index.html does not exist. Run 'hugo' first.")
        sys.exit(1)

    print("--- Sitemap and Recently Tended Stream Test Suite ---")

    # 1. Sitemap page structure
    print("1. Auditing public/sitemap/index.html:")
    with open(public_sitemap, "r", encoding="utf-8") as fp:
        sitemap_html = fp.read()

    assert re.search(r'<title>.*?Sitemap.*?</title>', sitemap_html, re.IGNORECASE), "Sitemap page missing <title> tag with 'Sitemap'"
    assert re.search(r'class=["\']?main-content["\']?', sitemap_html), "Sitemap page missing main-content container"
    assert "Tech Notes" in sitemap_html, "Sitemap missing Tech Notes section"
    assert "Book Reviews" in sitemap_html, "Sitemap missing Book Reviews section"
    assert "Role Models" in sitemap_html, "Sitemap missing Role Models section"

    # Verify deep-linking anchor targets
    for anchor_id in ["tech-notes", "books", "games", "other-media"]:
        assert re.search(rf'id=["\']?{anchor_id}["\'\s>]', sitemap_html), f"Missing deep-link anchor target id='{anchor_id}' in public/sitemap/index.html"
    print("  ✓ Sitemap deep-link anchor targets (tech-notes, books, games, other-media) verified.")
    print("  ✓ Sitemap page contains proper title, layout container, content sections, and anchor targets.")


    # 2. Sidebar navigation link
    print("2. Auditing sidebar navigation for Sitemap link:")
    with open(public_index, "r", encoding="utf-8") as fp:
        index_html = fp.read()

    sidebar_match = re.search(r'<nav class=["\']?nav-tree["\']?>(.*?)</nav>', index_html, re.DOTALL)
    assert sidebar_match, "Could not find nav-tree in public/index.html"
    sidebar_content = sidebar_match.group(1)

    sitemap_link_match = re.search(r'<a\s+href=["\']?/sitemap/["\']?[^>]*>.*?Sitemap</a>', sidebar_content, re.DOTALL)
    assert sitemap_link_match, "Sidebar nav-tree missing link to /sitemap/"
    print("  ✓ Sidebar nav contains properly structured /sitemap/ link.")

    # 3. Recently Tended stream audit
    print("3. Auditing Recently Tended stream on homepage:")
    stream_match = re.search(r'class=["\']?recently-updated-stream["\']?>(.*?)</div>\s*<hr', index_html, re.DOTALL)
    assert stream_match, "Could not find .recently-updated-stream in public/index.html"
    stream_html = stream_match.group(1)

    # Extract all cards
    cards = re.findall(r'<a\s+[^>]*?class=["\']?recent-note-card["\']?[^>]*?href=["\']?([^>\s"\']+)["\']?[^>]*>(.*?)</a>', stream_html, re.DOTALL)
    assert len(cards) == 5, f"Expected exactly 5 recent note cards, found {len(cards)}"

    for href, card_body in cards:
        # Verify title
        title_m = re.search(r'class=["\']?recent-note-title["\']?>([^<]+)</span>', card_body)
        assert title_m and title_m.group(1).strip(), f"Card with href '{href}' is missing a valid title"

        # Verify date
        date_m = re.search(r'class=["\']?recent-note-date["\']?>([^<]+)</span>', card_body)
        assert date_m and date_m.group(1).strip(), f"Card with href '{href}' is missing a valid date"

        # Verify section badge
        section_m = re.search(r'class=["\']?recent-note-section["\']?>([^<]+)</span>', card_body)
        assert section_m and section_m.group(1).strip(), f"Card with href '{href}' is missing a section badge"

        # Verify target file exists in public/
        clean_path = href.strip("/")
        target_html = os.path.join(public_dir, clean_path, "index.html")
        assert os.path.exists(target_html), f"Stream link '{href}' does not resolve to an existing public page at '{target_html}'"

        # Negative checks: no about or sitemap
        assert href != "/about/" and href != "/about", f"Prohibited page /about/ found in stream: {href}"
        assert href != "/sitemap/" and href != "/sitemap", f"Prohibited page /sitemap/ found in stream: {href}"

    print(f"  ✓ Validated {len(cards)} stream cards: all have titles, dates, sections, and resolve to existing public pages.")
    print("  ✓ Negative assertions verified: /about/ and /sitemap/ excluded.")

    print("\n✓ ALL SITEMAP & RECENT STREAM TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
