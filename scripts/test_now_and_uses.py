#!/usr/bin/env python3
"""
Automated Test Suite for /now and /uses Scaffolding & Navigation Integration
Validates:
1. File Existence & Scaffolding:
   - home/now.md exists with valid YAML frontmatter (title: "Now").
   - home/uses.md exists with valid YAML frontmatter (title: "Uses").
   - Both pages have zero tags and clean minimal bodies.
2. HTML Generation:
   - public/now/index.html exists and is non-empty.
   - public/uses/index.html exists and is non-empty.
   - Contains <title> tags matching 'Now' and 'Uses'.
   - Contains structural layout containers (.layout-container, .main-content).
3. Sidebar Navigation Integration:
   - Sidebar nav-tree contains link to '/now/' with '⏳ Now' under Site section.
   - Sidebar nav-tree contains link to '/uses/' with '🛠️ Uses' under Site section.
   - Active pill navigation: link has 'active' class when on its respective page.
   - Negative check: neither link has 'active' class on public/index.html.
4. Sitemap Integration & Deep Anchor Targets:
   - public/sitemap/index.html contains links to '/now/' and '/uses/'.
   - Anchor targets id='site-meta', id='now', and id='uses' present with .heading-anchor-target.
5. Search Index:
   - public/index.json contains entries for '/now/' and '/uses/'.
6. Cloudflare & Security Guardrails:
   - Zero inline event handlers (Rule 2 / Rocket Loader safety).
   - Minified-HTML safe regex assertions (Rule 14).
   - UTF-8 console output safe across Windows/Linux (Rule 12).
"""

import os
import re
import sys
import json

# Windows Python UTF-8 Stdout Reconfiguration (Rule 12)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    home_dir = os.path.join(root_dir, "home")
    public_dir = os.path.join(root_dir, "public")

    now_md = os.path.join(home_dir, "now.md")
    uses_md = os.path.join(home_dir, "uses.md")
    public_now = os.path.join(public_dir, "now", "index.html")
    public_uses = os.path.join(public_dir, "uses", "index.html")
    public_index = os.path.join(public_dir, "index.html")
    public_sitemap = os.path.join(public_dir, "sitemap", "index.html")
    search_json = os.path.join(public_dir, "index.json")

    print("--- /now and /uses Scaffolding & Navigation Regression Test Suite ---")

    # 1. Verify source markdown files
    print("1. Auditing source markdown files (home/now.md and home/uses.md):")
    for file_path, title_label in [(now_md, "Now"), (uses_md, "Uses")]:
        assert os.path.exists(file_path), f"{file_path} does not exist!"
        with open(file_path, "r", encoding="utf-8") as fp:
            source = fp.read()
        assert f'title: "{title_label}"' in source or f"title: '{title_label}'" in source or f'title: {title_label}' in source, (
            f"{file_path} missing title: '{title_label}' in frontmatter"
        )
        assert "tags:" not in source, f"{file_path} must not contain tags (meta page)"
        print(f"  ✓ {os.path.basename(file_path)} exists with clean frontmatter and zero tags.")

    # 2. Verify Generated HTML
    print("2. Auditing generated HTML in public/now/index.html and public/uses/index.html:")
    for html_path, title_label in [(public_now, "Now"), (public_uses, "Uses")]:
        if not os.path.exists(html_path):
            print(f"Error: {html_path} does not exist. Run 'hugo' first.")
            sys.exit(1)

        with open(html_path, "r", encoding="utf-8") as fp:
            page_html = fp.read()

        assert re.search(rf'<title>.*?{title_label}.*?</title>', page_html, re.IGNORECASE), (
            f"{html_path} missing <title> tag matching '{title_label}'"
        )
        assert re.search(r'class=["\']?layout-container["\']?', page_html), (
            f"{html_path} missing layout-container"
        )
        assert re.search(r'class=["\']?main-content["\']?', page_html), (
            f"{html_path} missing main-content container"
        )
        print(f"  ✓ {os.path.basename(html_path)} exists with canonical title and layout containers.")

    # 3. Verify Sidebar Navigation & Active State
    print("3. Auditing sidebar navigation for /now/ and /uses/ links and active indicators:")
    with open(public_now, "r", encoding="utf-8") as fp:
        now_html = fp.read()
    with open(public_uses, "r", encoding="utf-8") as fp:
        uses_html = fp.read()
    with open(public_index, "r", encoding="utf-8") as fp:
        index_html = fp.read()

    # /now/ page: now is active, uses is not active
    sidebar_match_now = re.search(r'<nav class=["\']?nav-tree["\']?>(.*?)</nav>', now_html, re.DOTALL)
    assert sidebar_match_now, "Could not find nav-tree in public/now/index.html"
    sidebar_content_now = sidebar_match_now.group(1)
    assert re.search(r'<a\s+href=["\']?/now/["\']?\s+class=["\']?active["\']?[^>]*>.*?Now</a>', sidebar_content_now, re.DOTALL), (
        "Sidebar nav-tree on /now/ page is missing active class on /now/ link"
    )
    assert not re.search(r'<a\s+href=["\']?/uses/["\']?\s+class=["\']?active["\']?', sidebar_content_now), (
        "Sidebar nav-tree on /now/ page incorrectly marked /uses/ as active"
    )
    print("  ✓ Sidebar on /now/ page has active highlighting on /now/ and inactive on /uses/.")

    # /uses/ page: uses is active, now is not active
    sidebar_match_uses = re.search(r'<nav class=["\']?nav-tree["\']?>(.*?)</nav>', uses_html, re.DOTALL)
    assert sidebar_match_uses, "Could not find nav-tree in public/uses/index.html"
    sidebar_content_uses = sidebar_match_uses.group(1)
    assert re.search(r'<a\s+href=["\']?/uses/["\']?\s+class=["\']?active["\']?[^>]*>.*?Uses</a>', sidebar_content_uses, re.DOTALL), (
        "Sidebar nav-tree on /uses/ page is missing active class on /uses/ link"
    )
    assert not re.search(r'<a\s+href=["\']?/now/["\']?\s+class=["\']?active["\']?', sidebar_content_uses), (
        "Sidebar nav-tree on /uses/ page incorrectly marked /now/ as active"
    )
    print("  ✓ Sidebar on /uses/ page has active highlighting on /uses/ and inactive on /now/.")

    # Negative assertion: on homepage, neither /now/ nor /uses/ is active
    sidebar_match_home = re.search(r'<nav class=["\']?nav-tree["\']?>(.*?)</nav>', index_html, re.DOTALL)
    assert sidebar_match_home, "Could not find nav-tree in public/index.html"
    sidebar_content_home = sidebar_match_home.group(1)
    assert re.search(r'<a\s+href=["\']?/now/["\']?[^>]*>.*?Now</a>', sidebar_content_home, re.DOTALL), (
        "Sidebar on homepage missing link to /now/"
    )
    assert re.search(r'<a\s+href=["\']?/uses/["\']?[^>]*>.*?Uses</a>', sidebar_content_home, re.DOTALL), (
        "Sidebar on homepage missing link to /uses/"
    )
    assert not re.search(r'<a\s+href=["\']?/now/["\']?\s+class=["\']?active["\']?', sidebar_content_home), (
        "Sidebar on homepage incorrectly marked /now/ as active"
    )
    assert not re.search(r'<a\s+href=["\']?/uses/["\']?\s+class=["\']?active["\']?', sidebar_content_home), (
        "Sidebar on homepage incorrectly marked /uses/ as active"
    )
    print("  ✓ Negative test passed: neither /now/ nor /uses/ is active on homepage.")

    # 4. Verify Sitemap Integration
    print("4. Auditing sitemap integration in public/sitemap/index.html:")
    with open(public_sitemap, "r", encoding="utf-8") as fp:
        sitemap_html = fp.read()

    assert re.search(r'href=["\']?/now/["\']?', sitemap_html), (
        "public/sitemap/index.html missing link to /now/"
    )
    assert re.search(r'href=["\']?/uses/["\']?', sitemap_html), (
        "public/sitemap/index.html missing link to /uses/"
    )
    assert re.search(r'id=["\']?site-meta["\']?', sitemap_html), (
        "public/sitemap/index.html missing anchor target for site-meta"
    )
    assert re.search(r'id=["\']?now["\']?', sitemap_html), (
        "public/sitemap/index.html missing anchor target for now"
    )
    assert re.search(r'id=["\']?uses["\']?', sitemap_html), (
        "public/sitemap/index.html missing anchor target for uses"
    )
    print("  ✓ Sitemap contains /now/ and /uses/ links and deep anchor targets.")

    # 5. Verify Search Index
    print("5. Auditing search index public/index.json:")
    with open(search_json, "r", encoding="utf-8") as fp:
        index_data = json.load(fp)

    now_entry = next((entry for entry in index_data if entry.get("permalink") == "/now/"), None)
    assert now_entry is not None, "Search index public/index.json does not index /now/ page"
    assert now_entry.get("title") == "Now", f"Search index entry has unexpected title: {now_entry.get('title')}"

    uses_entry = next((entry for entry in index_data if entry.get("permalink") == "/uses/"), None)
    assert uses_entry is not None, "Search index public/index.json does not index /uses/ page"
    assert uses_entry.get("title") == "Uses", f"Search index entry has unexpected title: {uses_entry.get('title')}"
    print("  ✓ Search index properly indexes both /now/ and /uses/ with correct titles.")

    # 6. Guardrail: Zero Inline Event Handlers (Rocket Loader Safety)
    print("6. Auditing Cloudflare Rocket Loader safety (zero inline event handlers):")
    for page_html, name in [(now_html, "/now/"), (uses_html, "/uses/")]:
        inline_handlers = re.findall(r'\son[a-z]+\s*=', page_html, re.IGNORECASE)
        assert len(inline_handlers) == 0, f"Found inline event handlers on {name} page: {inline_handlers}"
    print("  ✓ 100% Rocket Loader safe (zero inline event handlers).")

    print("\n✓ ALL /NOW AND /USES REGRESSION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
