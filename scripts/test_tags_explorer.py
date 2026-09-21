#!/usr/bin/env python3
"""
Automated Regression Test Suite for Multi-Tag Explorer Hub (/tags/) & Homepage Topic Cloud.

Validates:
1. Public files existence: public/tags/index.html and public/index.html.
2. /tags/ Explorer Hub HTML Structure:
   - Breadcrumbs navigation (Home / Tags).
   - Explorer header with title and subtitle.
   - Interactive controls: search input (#tag-search-input), view toggle buttons (Frequency default vs A-Z), and live counter.
3. Frequency View (Default):
   - Container #view-frequency visible by default.
   - Pills sorted strictly descending by note count (monotonic non-increasing order).
4. Alphabetical View:
   - Container #view-alphabetical initially hidden with display:none.
   - Letter navigation bar (.tag-letter-nav) with letter links.
   - Letter groups (.tag-letter-group) with anchor-targeted headings (#letter-X).
   - Tags inside each letter group start with that letter and are sorted alphabetically.
5. Dynamic Taxonomy Verification (Zero Hardcoded Counts):
   - Dynamically scans markdown files in home/ to determine live tag frequencies.
   - Asserts every active tag appears as a pill with its dynamically computed count.
   - Asserts count badge text synchronizes with data-count.
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
   - Prohibited directory/hierarchy tags ('books', 'tech', 'games', 'intro', 'research', etc.) absent.
"""

import os
import re
import sys

# Enforce UTF-8 stdout/stderr reconfiguration across Windows and Linux terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

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

def parse_markdown_tags(home_dir):
    """
    Dynamically scans all markdown files in home/ to extract live tag frequencies.
    Prevents brittle hardcoded counts as new content is authored.
    """
    tag_counts = {}
    for root, _, files in os.walk(home_dir):
        for f in files:
            if not f.endswith(".md"):
                continue
            fp = os.path.join(root, f)
            with open(fp, "r", encoding="utf-8") as file_handle:
                content = file_handle.read()
            m = re.match(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
            if not m:
                continue
            fm = m.group(1)
            # Block tags:
            # tags:
            #   - tag1
            block_m = re.search(r"^tags:\s*\n((?:\s+-\s*.*\r?\n?)*)", fm, re.MULTILINE)
            if block_m and block_m.group(1).strip():
                for line in block_m.group(1).strip().splitlines():
                    t = re.sub(r"^\s*-\s*", "", line).strip().strip("'\"")
                    if t:
                        tag_counts[t] = tag_counts.get(t, 0) + 1
            # Inline tags:
            # tags: [tag1, tag2]
            inline_m = re.search(r"^tags:\s*\[(.*?)\]", fm, re.MULTILINE)
            if inline_m:
                for t in inline_m.group(1).split(","):
                    t = t.strip().strip("'\"")
                    if t:
                        tag_counts[t] = tag_counts.get(t, 0) + 1
    return tag_counts

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tags_html_path = os.path.join(root_dir, "public", "tags", "index.html")
    home_html_path = os.path.join(root_dir, "public", "index.html")
    about_html_path = os.path.join(root_dir, "public", "about", "index.html")
    home_dir = os.path.join(root_dir, "home")

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

    # 3. Interactive Controls (Frequency View as Default)
    print("3. Validating interactive controls (search filter, view toggle, counter)...")
    assert re.search(r'id=["\']?tag-search-input["\']?', tags_html), "Search input #tag-search-input missing!"
    assert re.search(r'id=["\']?toggle-frequency["\']?[^>]*class=["\']?[^>"\']*active', tags_html), "Toggle button #toggle-frequency should be active by default!"
    assert re.search(r'id=["\']?toggle-frequency["\']?[^>]*aria-pressed=["\']?true["\']?', tags_html), "Toggle button #toggle-frequency should have aria-pressed=true by default!"
    assert re.search(r'id=["\']?toggle-alphabetical["\']?[^>]*aria-pressed=["\']?false["\']?', tags_html), "Toggle button #toggle-alphabetical should have aria-pressed=false by default!"
    assert re.search(r'id=["\']?tag-visible-count["\']?', tags_html), "Counter element #tag-visible-count missing!"
    assert re.search(r'id=["\']?tag-empty-state["\']?', tags_html), "Empty state element #tag-empty-state missing!"
    assert re.search(r'id=["\']?tag-clear-filter-btn["\']?', tags_html), "Clear filter button #tag-clear-filter-btn missing!"
    print("  ✓ All interactive control elements present in generated HTML (Frequency default).")

    # 4. Frequency View Verification & Sort Order Invariant
    print("4. Validating Frequency view container and descending count sort...")
    assert re.search(r'id=["\']?view-frequency["\']?', tags_html), "#view-frequency container missing!"
    assert re.search(r'class=["\']?[^>"\']*tag-frequency-wrap', tags_html), ".tag-frequency-wrap missing!"
    # Frequency view must be initially visible (no display:none)
    freq_hidden = re.search(r'id=["\']?view-frequency["\']?[^>]*style=["\']?[^>"\']*display:\s*none', tags_html)
    assert not freq_hidden, "#view-frequency must be visible by default (not display:none)"

    # Extract all pills in frequency view
    freq_section_m = re.search(r'id=["\']?view-frequency["\']?(.*?)</div>\s*</div>', tags_html, re.DOTALL)
    assert freq_section_m, "Could not extract frequency view markup"
    freq_html = freq_section_m.group(1)

    pill_matches = re.findall(
        r'<a[^>]+data-tag=["\']?([^"\'>\s]+)["\']?[^>]+data-count=["\']?(\d+)["\']?[^>]*>.*?class=["\']?tag-count-badge["\']?>(\d+)</span>',
        freq_html,
        re.DOTALL
    )
    assert len(pill_matches) > 0, "Zero pills found in frequency view!"
    
    counts = []
    for tag_name, attr_count_str, badge_count_str in pill_matches:
        attr_count = int(attr_count_str)
        badge_count = int(badge_count_str)
        assert attr_count >= 1, f"Tag '{tag_name}' has non-positive count: {attr_count}"
        assert attr_count == badge_count, f"Tag '{tag_name}' data-count ({attr_count}) does not match badge text ({badge_count})!"
        counts.append(attr_count)

    # Invariant: Counts must be sorted descending (non-increasing)
    assert counts == sorted(counts, reverse=True), f"Frequency view tags are not sorted descending by count! Observed: {counts}"
    print(f"  ✓ Frequency view verified: {len(counts)} tags sorted in strict descending order (counts {counts[0]} -> {counts[-1]}).")

    # 5. Alphabetical View Verification & Letter Group Invariants
    print("5. Validating Alphabetical view, letter navigation, and alphabetical sorting...")
    assert re.search(r'id=["\']?view-alphabetical["\']?', tags_html), "#view-alphabetical container missing!"
    assert re.search(r'id=["\']?view-alphabetical["\']?[^>]*style=["\']?[^>"\']*display:\s*none', tags_html), "#view-alphabetical must be initially hidden with display:none"
    assert re.search(r'class=["\']?[^>"\']*tag-letter-nav', tags_html), ".tag-letter-nav container missing!"
    assert re.search(r'class=["\']?[^>"\']*tag-letter-group', tags_html), ".tag-letter-group elements missing!"

    # Extract all letter groups
    group_matches = re.findall(
        r'<div[^>]+class=["\']?[^>"\']*tag-letter-group[^>"\']*["\']?[^>]+data-letter=["\']?([A-Z])["\']?[^>]*>(.*?)</div>\s*</div>',
        tags_html,
        re.DOTALL
    )
    assert len(group_matches) > 0, "Zero letter groups found in alphabetical view!"

    discovered_letters = []
    for letter, group_html in group_matches:
        discovered_letters.append(letter)
        # Check header ID and scroll margin
        assert f'id="letter-{letter}"' in group_html or f'id=letter-{letter}' in group_html, f"Anchor id letter-{letter} missing!"
        # Check nav link exists
        assert f'data-nav-letter="{letter}"' in tags_html or f'data-nav-letter={letter}' in tags_html, f"Nav link for letter {letter} missing!"
        # Check pills inside this group start with this letter
        group_pills = re.findall(r'data-tag=["\']?([^"\'>\s]+)["\']?', group_html)
        assert len(group_pills) > 0, f"Letter group {letter} has zero pills!"
        for g_tag in group_pills:
            assert g_tag.upper().startswith(letter), f"Tag '{g_tag}' in letter group '{letter}' does not start with '{letter}'!"
        # Check pills in this group are sorted alphabetically
        assert group_pills == sorted(group_pills), f"Tags in letter group '{letter}' are not sorted alphabetically: {group_pills}"

    assert discovered_letters == sorted(discovered_letters), f"Letter groups are not in alphabetical order: {discovered_letters}"
    print(f"  ✓ Alphabetical view verified: {len(discovered_letters)} letter groups ({', '.join(discovered_letters)}) correctly grouped and sorted.")

    # 6. Dynamic Content Parity (Zero Hardcoded Counts)
    print("6. Dynamically auditing tag frequencies against live markdown content in home/...")
    live_markdown_tags = parse_markdown_tags(home_dir)
    print(f"   Discovered {len(live_markdown_tags)} tags dynamically across markdown notes.")

    # Match every tag in markdown against the generated HTML in /tags/
    for live_tag, expected_count in live_markdown_tags.items():
        pill_pattern = rf'<a[^>]+href=["\']?/tags/{live_tag}/["\']?[^>]+data-tag=["\']?{live_tag}["\']?[^>]*>'
        assert re.search(pill_pattern, tags_html), f"Live tag '{live_tag}' linking to /tags/{live_tag}/ missing in generated HTML!"
        badge_pattern = rf'data-tag=["\']?{live_tag}["\']?[^>]*data-count=["\']?{expected_count}["\']?'
        assert re.search(badge_pattern, tags_html), f"Live tag '{live_tag}' expected dynamic count {expected_count}, but was missing in data-count!"
    print(f"  ✓ Dynamic parity verified: All {len(live_markdown_tags)} live markdown tags accurately reflected on /tags/ without hardcoding.")

    # Check total counter matches discovered tag count
    counter_m = re.search(r'id=["\']?tag-visible-count["\']?>(\d+)</strong>\s*of\s*(\d+)', tags_html)
    assert counter_m, "Could not extract tag counter numbers from /tags/"
    visible_cnt, total_cnt = int(counter_m.group(1)), int(counter_m.group(2))
    assert visible_cnt == total_cnt == len(live_markdown_tags), f"Counter ({visible_cnt}/{total_cnt}) does not match live tag count ({len(live_markdown_tags)})!"
    print(f"  ✓ Live counter correctly reports {total_cnt} tags matching content.")

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
    print("10. Running negative assertions against prohibited directory/hierarchy tags...")
    for ptag in PROHIBITED_TAGS:
        prohibited_pill = re.search(rf'data-tag=["\']?{ptag}["\']?', tags_html)
        assert not prohibited_pill, f"Prohibited tag '{ptag}' found in /tags/ pills!"
    print(f"  ✓ All {len(PROHIBITED_TAGS)} prohibited directory/hierarchy tags verified absent.")

    print("\n✓ ALL 10 MULTI-TAG EXPLORER HUB REGRESSION TESTS PASSED (ZERO HARDCODED COUNTS)!")

if __name__ == "__main__":
    run_tests()
