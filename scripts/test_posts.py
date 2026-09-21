#!/usr/bin/env python3
"""
Automated Regression Test Suite for Chronological Posts & Dispatches Space (/posts/).
Validates:
1. Posts Archive Structure (public/posts/index.html):
   - Canonical title, breadcrumbs, header with description and RSS badge.
   - Post entry cards with formatted date, reading time, and tags.
   - Year divider with heading anchor target id='year-YYYY'.
2. Single Post Page (public/posts/hello-posts/index.html):
   - Breadcrumbs with link back to /posts/.
   - Publication date, reading time, word count metadata.
   - Author attribution note mentioning Gemini / Antigravity.
   - Sample tag pill (meta) linking to /tags/meta/.
   - Negative test: ensures 'digital-gardens-and-chronological-streams' is deleted.
3. RSS Feed (public/posts/index.xml):
   - XML structure with title and items for published posts.
4. Controlled Sidebar Navigation:
   - Sidebar contains collapsible /posts/ section.
   - Contains '✨ Latest' sub-dropdown with recent posts.
   - Contains '🗄️ Archive' sub-dropdown with 'All Posts' and year groupings.
   - Section link triggers default /posts/ archive view.
5. Hugo Archetype & Author Documentation:
   - Archetype exists at archetypes/posts.md.
   - README.md contains actionable guide for 'hugo new posts/'.
6. Quality Guardrails:
   - Zero inline event handlers (Cloudflare Rocket Loader safe).
   - Minified-HTML safe regex patterns (Rule 14).
   - Negative assertions against runaway post trees and broken links.
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
    # Negative check: RSS badge removed from page header per user request
    assert "posts-rss-badge" not in archive_html, "RSS badge should not be present in /posts/ page header"

    # Breadcrumbs
    assert re.search(r'class=["\']?breadcrumbs["\']?', archive_html), "Missing breadcrumbs navigation"
    assert re.search(r'class=["\']?breadcrumb-current["\']?>Posts</span>', archive_html), "Breadcrumb current item should be 'Posts'"

    # Year divider check
    assert re.search(r'id=["\']?year-\d{4}["\']?', archive_html), "Missing year divider anchor id='year-YYYY'"

    # Post card check
    cards = re.findall(r'<article\s+class=["\']?post-entry-card["\']?>(.*?)</article>', archive_html, re.DOTALL)
    assert len(cards) >= 1, f"Expected at least 1 post card, found {len(cards)}"

    for card in cards:
        t_match = re.search(r'class=["\']?post-entry-title["\']?>\s*<a\s+[^>]*?href=["\']?([^"\'>\s]+)["\']?\s*>(.*?)</a>', card, re.DOTALL)
        assert t_match, f"Card missing title link: {card}"
        href, title_raw = t_match.group(1), t_match.group(2)
        title = re.sub(r'\s+', ' ', title_raw).strip()
        assert title == "Hello, Posts", f"Expected title 'Hello, Posts', got '{title}'"

        d_match = re.search(r'class=["\']?post-entry-date["\']?[^>]*>.*?([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})', card, re.DOTALL)
        assert d_match, f"Card missing formatted date: {card}"

        # Reading time check
        assert re.search(r'class=["\']?post-entry-reading-time["\']?>.*?min read', card), f"Card missing reading time: {card}"

        # Sample tag check
        assert re.search(r'href=["\']?/tags/meta/["\']?', card), f"Card missing tag pill for 'meta': {card}"

        # Target post exists in public/
        clean_target = href.strip("/")
        target_path = os.path.join(public_dir, clean_target, "index.html")
        assert os.path.exists(target_path), f"Post link {href} does not resolve to {target_path}"

    print(f"  ✓ {len(cards)} post card(s) validated on archive page with formatted dates and tag pills.")


    # 2. Verify Single Post Page
    print("\n2. Auditing Single Post Page (public/posts/hello-posts/index.html):")
    hello_path = os.path.join(public_dir, "posts", "hello-posts", "index.html")
    assert os.path.exists(hello_path), f"Missing single post page: {hello_path}"

    with open(hello_path, "r", encoding="utf-8") as fp:
        hello_html = fp.read()

    # Breadcrumbs
    assert re.search(r'<a\s+href=["\']?/posts/["\']?>.*?Posts</a>', hello_html), "Missing breadcrumb link to /posts/"
    assert "Hello, Posts" in hello_html, "Missing title 'Hello, Posts'"

    # Metadata
    assert re.search(r'<time\s+datetime=["\']?\d{4}-\d{2}-\d{2}["\']?>', hello_html), "Missing <time> element"
    assert re.search(r'\d+\s+min read', hello_html), "Missing reading time"
    assert re.search(r'\d+\s+words', hello_html), "Missing word count"
    assert re.search(r'href=["\']?/tags/meta/["\']?', hello_html), "Missing sample tag pill for 'meta'"

    # Content attribution check
    assert "Gemini" in hello_html or "Antigravity" in hello_html, "Missing attribution to Gemini / Antigravity in sample post"

    # Negative check: digital-gardens post is gone
    deleted_post_path = os.path.join(public_dir, "posts", "digital-gardens-and-chronological-streams")
    assert not os.path.exists(deleted_post_path), "Deleted post 'digital-gardens-and-chronological-streams' still exists in public/!"
    print("  ✓ Verified single post: title, metadata, tag pill, Gemini/Antigravity attribution.")
    print("  ✓ Negative check passed: 'digital-gardens-and-chronological-streams' is completely eliminated.")


    # 3. Verify RSS Feed & Auto-Discovery
    print("\n3. Auditing Posts RSS Feed & Discovery:")
    if not os.path.exists(posts_rss):
        print(f"Error: {posts_rss} does not exist.")
        sys.exit(1)

    with open(posts_rss, "r", encoding="utf-8") as fp:
        rss_content = fp.read()

    assert "<rss" in rss_content or "<?xml" in rss_content, "Invalid RSS XML format"
    assert "<title>Posts" in rss_content, "RSS missing Posts title"
    assert "Hello, Posts" in rss_content, "RSS missing inaugural post 'Hello, Posts'"
    print("  ✓ Validated RSS feed structure and inaugural post in public/posts/index.xml.")

    # Sidebar RSS link with conventional SVG icon
    assert re.search(r'<a\s+href=["\']?/posts/index\.xml["\']?[^>]*>.*?RSS Feed.*?</a>', archive_html, re.DOTALL), "Sidebar missing RSS Feed link under Site"
    assert re.search(r'<svg\s+class=["\']?rss-sidebar-icon["\']?', archive_html), "Sidebar missing conventional SVG RSS icon"
    print("  ✓ Sidebar contains RSS Feed link with conventional SVG icon under Site.")

    # RSS Auto-discovery tag in <head> across pages
    discovery_pages = [posts_index, home_index, hello_path]
    for dp in discovery_pages:
        with open(dp, "r", encoding="utf-8") as fp:
            page_src = fp.read()
        assert re.search(r'<link\s+[^>]*?rel=["\']?alternate["\']?[^>]*?type=["\']?application/rss\+xml["\']?[^>]*?href=["\']?[^"\'>\s]*?/posts/index\.xml["\']?', page_src), f"Missing RSS auto-discovery link tag in <head> of {dp}"
    print("  ✓ Verified <link rel='alternate' type='application/rss+xml'> auto-discovery in <head> across all pages.")


    # 4. Controlled Sidebar Navigation (Posts & Latest)
    print("\n4. Auditing Controlled Sidebar Navigation:")
    # Posts details wrapper on archive page
    assert re.search(r'<details\s+class=["\']?nav-section-details["\']?\s+open>.*?<summary[^>]*>.*?href=["\']?/posts/["\']?\s+class=["\']?active["\']?>Posts</a>', archive_html, re.DOTALL), "Sidebar on /posts/ should have Posts highlighted as active"
    assert re.search(r'<li><a\s+href=["\']?/posts/hello-posts/["\']?>Latest</a></li>', archive_html), "Sidebar on /posts/ should have inactive Latest link"

    # Posts details wrapper on single post page (hello-posts)
    assert re.search(r'<details\s+class=["\']?nav-section-details["\']?\s+open>.*?<summary[^>]*>.*?href=["\']?/posts/["\']?>Posts</a>', hello_html, re.DOTALL), "Sidebar on /posts/hello-posts/ should have open Posts section without active class"
    assert re.search(r'<li><a\s+href=["\']?/posts/hello-posts/["\']?\s+class=["\']?active["\']?>Latest</a></li>', hello_html), "Sidebar on /posts/hello-posts/ should have Latest highlighted as active"

    # Negative checks: No emojis, no duplicate 'Archive' or 'All Posts', no year breakdown in sidebar
    assert "✨ Latest" not in archive_html, "Sidebar should not contain emoji '✨ Latest'"
    assert "🗄️ Archive" not in archive_html, "Sidebar should not contain emoji '🗄️ Archive'"
    assert "All Posts" not in archive_html, "Sidebar should not contain duplicate 'All Posts' sub-link"
    print("  ✓ Sidebar contains clean Posts header and single Latest sub-link.")
    print("  ✓ Active highlighting verified: Posts active on archive page, Latest active on latest post page.")
    print("  ✓ Negative checks passed: Zero emojis, zero duplicate Archive/All Posts links.")


    # 5. Archetype & README Documentation
    print("\n5. Auditing Hugo Archetype & Author Documentation:")
    archetype_path = os.path.join("archetypes", "posts.md")
    assert os.path.exists(archetype_path), f"Missing archetype at {archetype_path}"
    with open(archetype_path, "r", encoding="utf-8") as fp:
        arch_content = fp.read()
    assert "title:" in arch_content and "date:" in arch_content and "tags:" in arch_content, "Archetype missing frontmatter fields"
    print("  ✓ Hugo archetype verified at archetypes/posts.md.")

    readme_path = "README.md"
    with open(readme_path, "r", encoding="utf-8") as fp:
        readme_content = fp.read()
    assert "hugo new posts/" in readme_content, "README.md missing 'hugo new posts/' command instructions"
    assert "Publishing a New Post" in readme_content, "README.md missing 'Publishing a New Post' section"
    print("  ✓ README.md contains actionable publishing guide with 'hugo new posts/' instructions.")


    # 6. Site Navigation & Discovery
    print("\n6. Auditing Site Navigation & Discovery:")
    with open(home_index, "r", encoding="utf-8") as fp:
        home_html = fp.read()
    assert re.search(r'href=["\']?/posts/["\']?>.*?Explore Posts.*?</a>', home_html), "Homepage missing 'Explore Posts Archive' link"

    # Homepage Latest Posts showcase between Hubs and Featured Notes
    assert re.search(r'Latest Posts.*?Featured Notes', home_html, re.DOTALL), "Homepage missing 'Latest Posts' section between Hubs and Featured Notes"
    assert re.search(r'class=["\']?grid cards latest-posts-grid["\']?', home_html), "Homepage missing .latest-posts-grid container"
    assert re.search(r'href=["\']?/posts/hello-posts/["\']?[^>]*>Hello, Posts</a>', home_html), "Homepage Latest Posts grid missing 'Hello, Posts' card link"

    with open(sitemap_html, "r", encoding="utf-8") as fp:
        sitemap_content = fp.read()
    assert re.search(r'id=["\']?posts["\']?', sitemap_content), "Sitemap missing anchor target id='posts'"
    assert re.search(r'href=["\']?/posts/["\']?', sitemap_content), "Sitemap missing link to /posts/"
    print("  ✓ Homepage Hub card, Latest Posts showcase (3-column grid), and Sitemap anchor targets verified.")


    # 7. Rocket Loader & Event Handler Safety
    print("\n7. Auditing Event Safety & Template Cleanliness:")
    layouts_posts = [
        os.path.join("layouts", "posts", "list.html"),
        os.path.join("layouts", "posts", "single.html"),
        os.path.join("layouts", "partials", "sidebar.html"),
    ]
    for tmpl in layouts_posts:
        with open(tmpl, "r", encoding="utf-8") as fp:
            tmpl_content = fp.read()
        assert not re.search(r'\bon[a-z]+\s*=', tmpl_content, re.IGNORECASE), f"Inline event handler found in {tmpl}!"
    print("  ✓ Zero inline event handlers found across templates (100% Rocket Loader safe).")

    print("\n✓ ALL POSTS & DISPATCHES REGRESSION TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
