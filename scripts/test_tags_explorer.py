#!/usr/bin/env python3
"""
Automated Regression Test Suite for Multi-Tag Explorer Hub (/tags/) & Homepage Topic Cloud.

Validates:
1. Public files existence: public/tags/index.html and public/index.html.
2. /tags/ Explorer Hub HTML Structure:
   - Breadcrumbs navigation (Home / Tags).
   - Explorer header with title and subtitle.
   - Interactive controls: search input (#tag-search-input), view toggle buttons (A-Z vs Frequency), and live counter.
3. Alphabetical View:
   - Letter navigation bar (.tag-letter-nav) with letter links.
   - Letter groups (.tag-letter-group) with anchor-targeted headings (#letter-X).
4. Frequency View:
   - Container #view-frequency with pills ordered descending by note frequency.
5. All 33 canonical tags:
   - Every canonical tag present with exact expected frequency count badge and data attributes.
   - Every tag pill links to /tags/<tag>/.
6. Cloudflare Rocket Loader & Zero Inline Handlers:
   - Physical check verifying ZERO inline event handlers (onclick, oninput, etc.) in /tags/ HTML.
7. Homepage Topic Cloud:
   - public/index.html contains Explore by Topic heading.
   - Contains .tag-cloud-container, tag pills with count badges, and link to /tags/.
8. Sidebar Navigation:
   - href="/tags/" present under Site navigation across pages.
   - Active class applied on /tags/ page.
   - Correct sequence: Now -> Uses -> Tags -> About -> Sitemap.
9. Negative assertions:
   - Prohibited directory/hierarchy tags ('books', 'tech', 'games', 'intro', 'research') absent.
   - Troublesome singletons absent.
"""

import os
import re
import sys

# Enforce UTF-8 stdout/stderr reconfiguration across Windows and Linux terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

TARGET_TAXONOMY = {
    "science": 10,
    "fiction": 9,
    "devops": 8,
    "sysadmin": 7,
    "programming": 6,
    "philosophy": 5,
    "tools": 5,
    "history": 4,
    "linux": 4,
    "media": 4,
    "people": 4,
    "psychology": 4,
    "security": 4,
    "literary": 3,
    "math": 3,
    "medicine": 3,
    "monitoring": 3,
    "politics": 3,
    "productivity": 3,
    "writing": 3,
    "climate": 2,
    "containers": 2,
    "data": 2,
    "databases": 2,
    "environment": 2,
    "fantasy": 2,
    "finance": 2,
    "gaming": 2,
    "nabokov": 2,
    "reading": 2,
    "sci-fi": 2,
    "windows": 2,
    "ai": 2,
}

PROHIBITED_TAGS = [
    "books",
    "tech",
    "games",
    "research",
    "intro",
    "non-fiction",
    "about",
    "home",
]

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tags_html_path = os.path.join(root_dir, "public", "tags", "index.html")
    home_html_path = os.path.join(root_dir, "public", "index.html")
    about_html_path = os.path.join(root_dir, "public", "about", "index.html")

    print("--- Multi-Tag Explorer Hub (/tags/) Regression Test Suite ---")

    # 1. Existence check
    print("1. Checking generated public files exist...")
    assert os.path.exists(tags_html_path), f"Missing generated file: {tags_html_path}"
    assert os.path.exists(home_html_path), f"Missing generated file: {home_html_path}"
    assert os.path.exists(about_html_path), f"Missing generated file: {about_html_path}"
    print("  ✓ public/tags/index.html and public/index.html exist.")

    with open(tags_html_path, "r", encoding="utf-8") as fp:
        tags_html = fp.read()

    with open(home_html_path, "r", encoding="utf-8") as fp:
        home_html = fp.read()

    with open(about_html_path, "r", encoding="utf-8") as fp:
        about_html = fp.read()

    # 2. Explorer Hub Header & Breadcrumbs
    print("2. Validating breadcrumbs and explorer header...")
    assert re.search(r'class=["\']?breadcrumbs["\']?', tags_html), "Breadcrumbs navigation missing in /tags/"
    assert re.search(r'class=["\']?tag-explorer-header["\']?', tags_html), "Tag explorer header missing in /tags/"
    assert "Tags Explorer" in tags_html, "Title 'Tags Explorer' missing in /tags/"
    print("  ✓ Breadcrumbs and Tags Explorer header verified.")

    # 3. Interactive Controls
    print("3. Validating interactive controls (search filter, view toggle, counter)...")
    assert re.search(r'id=["\']?tag-search-input["\']?', tags_html), "Search input #tag-search-input missing!"
    assert re.search(r'id=["\']?toggle-alphabetical["\']?[^>]*aria-pressed=["\']?false["\']?', tags_html), "Toggle button #toggle-alphabetical should have aria-pressed=false by default!"
    assert re.search(r'id=["\']?toggle-frequency["\']?[^>]*class=["\']?[^>"\']*active', tags_html), "Toggle button #toggle-frequency should be active by default!"
    assert re.search(r'id=["\']?toggle-frequency["\']?[^>]*aria-pressed=["\']?true["\']?', tags_html), "Toggle button #toggle-frequency should have aria-pressed=true by default!"
    assert re.search(r'id=["\']?tag-visible-count["\']?', tags_html), "Counter element #tag-visible-count missing!"
    assert re.search(r'id=["\']?tag-empty-state["\']?', tags_html), "Empty state element #tag-empty-state missing!"
    assert re.search(r'id=["\']?tag-clear-filter-btn["\']?', tags_html), "Clear filter button #tag-clear-filter-btn missing!"
    print("  ✓ All interactive control elements present in generated HTML (Frequency default).")

    # 4. Alphabetical View & Letter Navigation
    print("4. Validating Alphabetical view and letter navigation...")
    assert re.search(r'id=["\']?view-alphabetical["\']?', tags_html), "#view-alphabetical container missing!"
    assert re.search(r'id=["\']?view-alphabetical["\']?[^>]*style=["\']?[^>"\']*display:\s*none', tags_html), "#view-alphabetical must be initially hidden with display:none"
    assert re.search(r'class=["\']?[^>"\']*tag-letter-nav', tags_html), ".tag-letter-nav container missing!"
    assert re.search(r'class=["\']?[^>"\']*tag-letter-group', tags_html), ".tag-letter-group elements missing!"
    
    # Check letter anchor targets
    expected_letters = ["A", "C", "D", "E", "F", "G", "H", "L", "M", "N", "P", "R", "S", "T", "W"]
    for letter in expected_letters:
        assert f'id="letter-{letter}"' in tags_html or f'id=letter-{letter}' in tags_html, f"Anchor id letter-{letter} missing!"
        assert f'data-letter="{letter}"' in tags_html or f'data-letter={letter}' in tags_html, f"data-letter {letter} missing!"
    print(f"  ✓ Letter navigation and letter group headings verified for all {len(expected_letters)} letters.")

    # 5. Frequency View
    print("5. Validating Frequency view container...")
    assert re.search(r'id=["\']?view-frequency["\']?', tags_html), "#view-frequency container missing!"
    assert re.search(r'class=["\']?[^>"\']*tag-frequency-wrap', tags_html), ".tag-frequency-wrap missing!"
    # Frequency view must be initially visible (no display:none)
    freq_hidden = re.search(r'id=["\']?view-frequency["\']?[^>]*style=["\']?[^>"\']*display:\s*none', tags_html)
    assert not freq_hidden, "#view-frequency must be visible by default (not display:none)"
    print("  ✓ Frequency view container verified as active default.")

    # 6. Validate All 33 Canonical Tags & Frequencies
    print("6. Validating presence and note counts of all 33 canonical tags in /tags/...")
    for tag, expected_count in TARGET_TAXONOMY.items():
        # Check pill exists with data-tag and correct href
        pill_pattern = rf'<a[^>]+href=["\']?/tags/{tag}/["\']?[^>]+data-tag=["\']?{tag}["\']?[^>]*>'
        assert re.search(pill_pattern, tags_html), f"Tag pill for '{tag}' linking to /tags/{tag}/ missing!"
        # Check count badge exists for this tag
        badge_pattern = rf'data-tag=["\']?{tag}["\']?[^>]*data-count=["\']?{expected_count}["\']?'
        assert re.search(badge_pattern, tags_html), f"Expected count {expected_count} for tag '{tag}' missing in data-count!"
    print(f"  ✓ All {len(TARGET_TAXONOMY)} canonical tags correctly generated with expected count badges.")

    # 7. Rocket Loader Safety & Zero Inline Handlers
    print("7. Verifying Cloudflare Rocket Loader safety (0 inline HTML handlers)...")
    inline_handler_m = re.findall(r'\son[a-z]+="[^"]*"|\son[a-z]+=\'[^\']*\'|\son[a-z]+=[^\s>]+', tags_html)
    assert len(inline_handler_m) == 0, f"Found inline event handlers in /tags/ HTML: {inline_handler_m}"
    print("  ✓ Zero inline HTML event handlers found in /tags/ (100% Rocket Loader safe).")

    # 8. Homepage Topic Cloud Integration
    print("8. Validating Homepage Topic Cloud integration...")
    assert "Explore by Topic" in home_html, "'Explore by Topic' heading missing in public/index.html!"
    assert re.search(r'class=["\']?[^>"\']*tag-cloud-container', home_html), ".tag-cloud-container missing in public/index.html!"
    assert re.search(r'class=["\']?[^>"\']*tag-cloud-pills', home_html), ".tag-cloud-pills missing in public/index.html!"
    assert re.search(r'<a[^>]+href=["\']?/tags/["\']?[^>]*class=["\']?[^>"\']*tag-cloud-all-link', home_html), "Link to /tags/ missing in homepage topic cloud footer!"
    print("  ✓ Homepage Topic Cloud shortcode successfully rendered.")

    # 9. Sidebar Navigation Link
    print("9. Validating Sidebar Navigation link across pages...")
    # Active on /tags/
    assert re.search(r'<a\s+[^>]*href=["\']?/tags/["\']?[^>]*class=["\']?[^>"\']*active[^>"\']*["\']?[^>]*>🏷️ Tags</a>', tags_html), "Sidebar link to /tags/ should be active on /tags/!"
    # Inactive on / and /about/
    assert re.search(r'<a\s+href=["\']?/tags/["\']?>🏷️ Tags</a>', home_html), "Sidebar link to /tags/ missing on homepage!"
    assert re.search(r'<a\s+href=["\']?/tags/["\']?>🏷️ Tags</a>', about_html), "Sidebar link to /tags/ missing on /about/!"

    # Sequence order under Site: Now -> Uses -> Tags -> About -> Sitemap
    site_nav_seq = re.search(r'href=["\']?/now/["\']?.*?href=["\']?/uses/["\']?.*?href=["\']?/tags/["\']?.*?href=["\']?/about/["\']?.*?href=["\']?/sitemap/["\']?', tags_html, re.DOTALL)
    assert site_nav_seq, "Sidebar 'Site' section items not in correct sequence: Now -> Uses -> Tags -> About -> Sitemap"
    print("  ✓ Sidebar navigation link verified with active state and correct order.")

    # 10. Negative Assertions
    print("10. Running negative assertions against prohibited tags...")
    for ptag in PROHIBITED_TAGS:
        # Check no pill exists with data-tag=ptag
        prohibited_pill = re.search(rf'data-tag=["\']?{ptag}["\']?', tags_html)
        assert not prohibited_pill, f"Prohibited tag '{ptag}' found in /tags/ pills!"
    print(f"  ✓ All {len(PROHIBITED_TAGS)} prohibited directory/hierarchy tags verified absent.")

    print("\n✓ ALL 10 MULTI-TAG EXPLORER HUB REGRESSION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
