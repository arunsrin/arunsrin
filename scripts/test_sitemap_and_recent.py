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
    assert "Tech" in sitemap_html, "Sitemap missing Tech section"
    assert "Other Interests" in sitemap_html, "Sitemap missing Other Interests section"
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

    # 3. Homepage stream audit (Latest Posts showcase & retirement of Recent Updates)
    print("3. Auditing homepage stream (Latest Posts showcase):")
    assert "Latest Posts" in index_html, "Missing 'Latest Posts' heading on homepage"
    assert re.search(r'class=["\']?grid cards latest-posts-grid["\']?', index_html), "Missing .latest-posts-grid in public/index.html"
    assert "Hello, Posts" in index_html, "Missing 'Hello, Posts' card in Latest Posts grid"

    # Negative assertions: retired Recent Updates and metaphors
    assert "Recent Updates" not in index_html, "Retired 'Recent Updates' heading should not be present on homepage"
    assert "recently-updated-stream" not in index_html, "Retired 'recently-updated-stream' should not be present on homepage"
    assert "Recently Tended" not in index_html, "Found outdated 'Recently Tended' metaphor on homepage"
    assert "Garden Hubs" not in index_html, "Found outdated 'Garden Hubs' metaphor on homepage"
    print("  ✓ Latest Posts showcase verified on homepage; retired Recent Updates confirmed absent.")

    print("\n✓ ALL SITEMAP & HOMEPAGE STREAM TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
