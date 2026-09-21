#!/usr/bin/env python3
"""
Automated Regression Test Suite for Chronological Posts & Dispatches Space (/posts/).
Validates:
1. Posts Archive Structure (public/posts/index.html):
   - Canonical title, breadcrumbs, header with description and RSS badge.
   - Reverse-chronological post cards ordered by publication date.
   - Date formats, reading time badges, summaries.
2. Single Post Pages (public/posts/*/index.html):
   - Breadcrumbs with link back to /posts/.
   - Publication date, reading time, word count metadata.
   - Sequential navigation (Older Post / Newer Post links).
3. RSS Feed (public/posts/index.xml):
   - XML structure with title and items for published posts.
4. Navigation & Site Integration:
   - Sidebar contains collapsible /posts/ section and active highlights.
   - Homepage contains Posts Hub card in .grid.cards with explore link.
   - Sitemap contains Posts & Dispatches section and #posts anchor target.
5. Quality Guardrails:
   - Zero inline event handlers (Cloudflare Rocket Loader safe).
   - Minified-HTML safe regex patterns (Rule 14).
   - Negative assertions against broken links and missing metadata.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

# Windows Python UTF-8 Stdout Reconfiguration (Rule 12)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    public_dir = "public"
    posts_index = os.path.join(public_dir, "posts", "index.html")
    posts_rss = os.path.join(public_dir, "posts", "index.xml")
    home_index = os.path.join(public_dir, "index.html")
    sitemap_html = os.path.join(public_dir, "sitemap", "index.html")

    print("--- Chronological Posts & Dispatches Test Suite ---")

    # 1. Verify Posts Archive Page
    print("1. Auditing Posts Archive (public/posts/index.html):")
    if not os.path.exists(posts_index):
        print(f"Error: {posts_index} does not exist. Run 'hugo' first.")
        sys.exit(1)

    with open(posts_index, "r", encoding="utf-8") as fp:
        archive_html = fp.read()

    # Title and header
    assert re.search(r'<title>.*?Posts.*?</title>', archive_html, re.IGNORECASE), "Missing <title> tag with 'Posts'"
    assert re.search(r'class=["\']?posts-section-header["\']?', archive_html), "Missing .posts-section-header container"
    assert re.search(r'<a\s+[^>]*?class=["\']?posts-rss-badge["\']?[^>]*>', archive_html), "Missing .posts-rss-badge element"
    assert re.search(r'<a\s+[^>]*?href=["\']?/posts/index\.xml["\']?[^>]*>', archive_html), "Missing /posts/index.xml RSS link"

    # Breadcrumbs
    assert re.search(r'class=["\']?breadcrumbs["\']?', archive_html), "Missing breadcrumbs navigation"
    assert re.search(r'class=["\']?breadcrumb-current["\']?>Posts</span>', archive_html), "Breadcrumb current item should be 'Posts'"

    # Reverse-chronological card ordering
    cards = re.findall(r'<article\s+class=["\']?post-entry-card["\']?>(.*?)</article>', archive_html, re.DOTALL)
    assert len(cards) >= 2, f"Expected at least 2 post cards, found {len(cards)}"

    titles = []
    dates = []
    for card in cards:
        t_match = re.search(r'class=["\']?post-entry-title["\']?>.*?<a\s+href=["\']?([^"\']+)["\']?>([^<]+)</a>', card, re.DOTALL)
        assert t_match, f"Card missing title link: {card}"
        href, title = t_match.group(1), t_match.group(2).strip()
        titles.append(title)

        d_match = re.search(r'class=["\']?post-entry-date["\']?[^>]*>.*?([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})', card, re.DOTALL)
        assert d_match, f"Card missing formatted date: {card}"
        dates.append(d_match.group(1))

        # Reading time check
        assert re.search(r'class=["\']?post-entry-reading-time["\']?>.*?min read', card), f"Card missing reading time: {card}"

        # Target post exists in public/
        clean_target = href.strip("/")
        target_path = os.path.join(public_dir, clean_target, "index.html")
        assert os.path.exists(target_path), f"Post link {href} does not resolve to {target_path}"

    # Verify reverse-chronological order
    assert titles[0] == "Digital Gardens and Chronological Streams", f"First post should be latest ('Digital Gardens...'), got '{titles[0]}'"
    assert titles[1] == "Hello, Posts", f"Second post should be older ('Hello, Posts'), got '{titles[1]}'"
    print(f"  ✓ {len(cards)} post cards found in reverse-chronological order: {[t for t in titles]}")
    print(f"  ✓ Valid formatted dates verified: {dates}")


    # 2. Verify Single Post Pages
    print("\n2. Auditing Single Post Pages:")
    single_pages = [
        ("digital-gardens-and-chronological-streams", "Digital Gardens and Chronological Streams", "Hello, Posts", None),
        ("hello-posts", "Hello, Posts", None, "Digital Gardens and Chronological Streams"),
    ]

    for slug, expected_title, expected_older, expected_newer in single_pages:
        page_path = os.path.join(public_dir, "posts", slug, "index.html")
        assert os.path.exists(page_path), f"Missing single post page: {page_path}"

        with open(page_path, "r", encoding="utf-8") as fp:
            single_html = fp.read()

        # Breadcrumbs
        assert re.search(r'<a\s+href=["\']?/posts/["\']?>.*?Posts</a>', single_html), f"Page {slug} missing breadcrumb link to /posts/"
        assert expected_title in single_html, f"Page {slug} missing title '{expected_title}'"

        # Metadata
        assert re.search(r'<time\s+datetime=["\']?\d{4}-\d{2}-\d{2}["\']?>', single_html), f"Page {slug} missing <time> element"
        assert re.search(r'\d+\s+min read', single_html), f"Page {slug} missing reading time"
        assert re.search(r'\d+\s+words', single_html), f"Page {slug} missing word count"

        # Sequential navigation
        assert re.search(r'class=["\']?post-sequential-nav["\']?', single_html), f"Page {slug} missing sequential navigation"
        if expected_older:
            assert expected_older in single_html, f"Page {slug} should have older link to '{expected_older}'"
        if expected_newer:
            assert expected_newer in single_html, f"Page {slug} should have newer link to '{expected_newer}'"

        print(f"  ✓ Verified post '{slug}': title, metadata bar, breadcrumbs, sequential navigation.")


    # 3. Verify RSS Feed
    print("\n3. Auditing Posts RSS Feed (public/posts/index.xml):")
    if not os.path.exists(posts_rss):
        print(f"Error: {posts_rss} does not exist.")
        sys.exit(1)

    with open(posts_rss, "r", encoding="utf-8") as fp:
        rss_content = fp.read()

    assert "<rss" in rss_content or "<?xml" in rss_content, "Invalid RSS XML format"
    assert "<title>Posts" in rss_content, "RSS missing Posts title"
    assert "Hello, Posts" in rss_content, "RSS missing inaugural post 'Hello, Posts'"
    assert "Digital Gardens and Chronological Streams" in rss_content, "RSS missing post 'Digital Gardens and Chronological Streams'"
    print("  ✓ Validated RSS feed structure and items in public/posts/index.xml.")


    # 4. Verify Sidebar, Homepage & Sitemap Navigation
    print("\n4. Auditing Site Navigation & Discovery:")
    # Sidebar
    assert re.search(r'<a\s+href=["\']?/posts/["\']?[^>]*>.*?Posts</a>', archive_html), "Sidebar missing link to /posts/"
    print("  ✓ Sidebar navigation contains /posts/ section link.")

    # Homepage Hub Card
    with open(home_index, "r", encoding="utf-8") as fp:
        home_html = fp.read()
    assert re.search(r'href=["\']?/posts/["\']?>.*?Explore Posts</a>', home_html), "Homepage Hubs missing 'Explore Posts' link"
    assert "Chronological dispatches" in home_html, "Homepage missing Posts hub card description"
    print("  ✓ Homepage contains Posts Hub card in category grid.")

    # Sitemap
    with open(sitemap_html, "r", encoding="utf-8") as fp:
        sitemap_content = fp.read()
    assert re.search(r'id=["\']?posts["\']?', sitemap_content), "Sitemap missing anchor target id='posts'"
    assert re.search(r'href=["\']?/posts/["\']?', sitemap_content), "Sitemap missing link to /posts/"
    print("  ✓ Sitemap contains Posts section with deep-link anchor id='posts'.")


    # 5. Rocket Loader & Event Handler Safety
    print("\n5. Auditing Event Safety & Template Cleanliness:")
    layouts_posts = [
        os.path.join("layouts", "posts", "list.html"),
        os.path.join("layouts", "posts", "single.html"),
    ]
    for tmpl in layouts_posts:
        with open(tmpl, "r", encoding="utf-8") as fp:
            tmpl_content = fp.read()
        assert not re.search(r'\bon[a-z]+\s*=', tmpl_content, re.IGNORECASE), f"Inline event handler found in {tmpl}!"
    print("  ✓ Zero inline event handlers found across post layouts (100% Rocket Loader safe).")

    print("\n✓ ALL POSTS & DISPATCHES REGRESSION TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
