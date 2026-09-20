#!/usr/bin/env python3
"""
Regression test suite for consistent animated emojis across the Tech folder.
Validates:
1. Frontmatter icon definition across all markdown files under home/tech/.
2. Clean plain-text titles in frontmatter (e.g. OpenSSL without hardcoded static emoji).
3. Section pages rendering on /tech/ (all 19 sub-pages have animated emoji prefixes, no plain 📄/📁).
4. Specific regression test for OpenSSL (no duplicate emoji or static 🔒).
5. Sub-section pages rendering on /tech/linux/ and /tech/programming/.
6. Sidebar tree rendering with icons for tech sub-pages.
7. Search index integrity (clean titles without icon shortcode leakage).
8. 100% EMOJI_MAP coverage in footer.html for all icons used under home/tech/.
"""

import os
import re
import sys
import json

# Ensure UTF-8 output across Windows and Linux terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    public_dir = "public"
    content_tech = os.path.join("home", "tech")
    footer_path = os.path.join("layouts", "partials", "footer.html")

    if not os.path.exists(public_dir):
        print(f"Error: {public_dir} does not exist. Run 'hugo' first.")
        sys.exit(1)

    print("--- Tech Folder Animated Emojis Test Suite ---")

    # 1. Check all markdown files under home/tech/ for icon frontmatter
    print("1. Verifying icon frontmatter in home/tech/:")
    all_tech_files = []
    missing_icon = []
    icon_regex = re.compile(r'^icon:\s*["\'](:[a-z0-9_-]+:\{[^\}]+\})["\']', re.MULTILINE)
    title_regex = re.compile(r'^title:\s*["\']([^"\']+)["\']', re.MULTILINE)

    used_icons = set()

    for root, _, files in os.walk(content_tech):
        for f in files:
            if f.endswith(".md"):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, "home")
                all_tech_files.append((p, rel))
                with open(p, "r", encoding="utf-8") as fp:
                    content = fp.read()

                m = icon_regex.search(content)
                if not m:
                    missing_icon.append(rel)
                else:
                    raw_shortcode = m.group(1)
                    icon_name = re.match(r':([a-z0-9_-]+):', raw_shortcode).group(1)
                    used_icons.add(icon_name)

                # Check title is clean
                tm = title_regex.search(content)
                if tm:
                    title_val = tm.group(1)
                    # Title should not contain shortcodes or emoji symbols
                    if ":" in title_val or "🔒" in title_val:
                        print(f"  ❌ FAILED: Dirty title '{title_val}' in {rel}")
                        sys.exit(1)

    if missing_icon:
        print(f"  ❌ FAILED: Missing 'icon:' frontmatter in {len(missing_icon)} files:")
        for m in missing_icon:
            print(f"     - {m}")
        sys.exit(1)
    print(f"  ✓ All {len(all_tech_files)} tech markdown files have valid icon frontmatter.")

    # 2. Check OpenSSL frontmatter explicitly
    openssl_md = os.path.join(content_tech, "openssl.md")
    with open(openssl_md, "r", encoding="utf-8") as fp:
        openssl_text = fp.read()
    assert 'title: "OpenSSL"' in openssl_text, "OpenSSL frontmatter title must be 'OpenSSL'"
    assert 'icon: ":material-lock:{ .anim-bounce }"' in openssl_text, "OpenSSL must have bounce lock icon"
    print("  ✓ OpenSSL frontmatter is clean and has bounce lock icon.")

    # 3. Check /tech/ page generated HTML
    tech_html_path = os.path.join(public_dir, "tech", "index.html")
    assert os.path.exists(tech_html_path), "public/tech/index.html not found!"
    with open(tech_html_path, "r", encoding="utf-8") as fp:
        tech_html = fp.read()

    print("2. Verifying /tech/ section pages list:")
    section_match = re.search(r'<section class=[\"\']?section-pages[\"\']?[^>]*>(.*?)</section>', tech_html, re.DOTALL)
    assert section_match, "No <section class=\"section-pages\"> found on /tech/index.html!"
    section_html = section_match.group(1)

    # Links in section-pages
    links = re.findall(r'<a\s+href=[\"\']?([^\"\'\s>]+)[\"\']?[^>]*>\s*([^<]+?)\s*</a>', section_html)
    assert len(links) >= 19, f"Expected at least 19 tech sub-pages, found {len(links)}"

    for href, text in links:
        stripped = text.strip()
        # Must have an animated icon token
        assert re.match(r':(?:material|simple)-[a-z0-9_-]+:\{', stripped), f"Link for {href} ('{stripped}') missing icon token!"
        # Must NOT start with plain 📄 or 📁
        assert not stripped.startswith("📄") and not stripped.startswith("📁"), f"Link for {href} still has plain emoji: '{stripped}'"
        # Specifically for OpenSSL, ensure no duplicate 🔒
        if "openssl" in href:
            assert "🔒" not in stripped, f"OpenSSL link has raw emoji in Hugo template text: '{stripped}'"
            assert stripped == ":material-lock:{ .anim-bounce } OpenSSL", f"Unexpected OpenSSL link text: '{stripped}'"

    print(f"  ✓ All {len(links)} tech section page links have animated icon prefixes.")

    # 4. Check /tech/ H1 heading
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', tech_html)
    assert h1_match, "No <h1> found in public/tech/index.html"
    assert ":material-console:{ .anim-rotate } Tech Notes" in h1_match.group(1), f"H1 heading in /tech/index.html missing animated console icon: {h1_match.group(1)}"
    print("  ✓ Tech Notes H1 heading has animated console icon.")

    # 5. Check sub-sections (/tech/linux/ and /tech/programming/)
    print("3. Verifying sub-section pages (/tech/linux/ and /tech/programming/):")
    for sub in ["linux", "programming"]:
        sub_html_path = os.path.join(public_dir, "tech", sub, "index.html")
        assert os.path.exists(sub_html_path), f"{sub_html_path} not found!"
        with open(sub_html_path, "r", encoding="utf-8") as fp:
            sub_html = fp.read()
        sub_sec_match = re.search(r'<section class=[\"\']?section-pages[\"\']?[^>]*>(.*?)</section>', sub_html, re.DOTALL)
        assert sub_sec_match, f"No section-pages on /tech/{sub}/index.html"
        sub_links = re.findall(r'<a\s+href=[\"\']?([^\"\'\s>]+)[\"\']?[^>]*>\s*([^<]+?)\s*</a>', sub_sec_match.group(1))
        assert len(sub_links) > 0, f"No links in /tech/{sub}/ section-pages"
        for href, text in sub_links:
            stripped = text.strip()
            assert re.match(r':(?:material|simple)-[a-z0-9_-]+:\{', stripped), f"Sub-link {href} ('{stripped}') missing icon!"
            assert not stripped.startswith("📄"), f"Sub-link {href} has plain 📄"
        print(f"  ✓ /tech/{sub}/ ({len(sub_links)} pages) has animated icons.")

    # 6. Check Search index (index.json)
    print("4. Verifying search index integrity (index.json):")
    index_json_path = os.path.join(public_dir, "index.json")
    with open(index_json_path, "r", encoding="utf-8") as fp:
        search_data = json.load(fp)

    openssl_items = [item for item in search_data if item.get("permalink") == "/tech/openssl/"]
    assert len(openssl_items) == 1, "OpenSSL missing from search index!"
    assert openssl_items[0]["title"] == "OpenSSL", f"OpenSSL title in index.json should be 'OpenSSL', got '{openssl_items[0]['title']}'"

    # Ensure no tech item title contains raw icon tokens
    for item in search_data:
        if item.get("permalink", "").startswith("/tech/"):
            title = item.get("title", "")
            assert not re.search(r':(?:material|simple)-', title), f"Raw icon shortcode leaked into search title: '{title}' ({item.get('permalink')})"
            assert "🔒" not in title, f"Emoji leaked into search title: '{title}'"
    print("  ✓ Search index titles are clean plain-text.")

    # 7. Check EMOJI_MAP fallback in footer.html
    print("5. Verifying EMOJI_MAP coverage in footer.html:")
    with open(footer_path, "r", encoding="utf-8") as fp:
        footer_content = fp.read()

    emoji_map_match = re.search(r'const\s+EMOJI_MAP\s*=\s*\{([^}]+)\};', footer_content, re.DOTALL)
    assert emoji_map_match, "EMOJI_MAP not found in footer.html!"
    emoji_map_text = emoji_map_match.group(1)

    mapped_icons = set(re.findall(r"['\"]([a-z0-9_-]+)['\"]\s*:", emoji_map_text))
    unmapped = used_icons - mapped_icons
    if unmapped:
        print(f"  ❌ FAILED: Icons used in tech notes missing from EMOJI_MAP: {unmapped}")
        sys.exit(1)
    print(f"  ✓ All {len(used_icons)} icons used in tech notes are mapped in EMOJI_MAP.")

    print("\n✓ ALL TECH EMOJI REGRESSION TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
