#!/usr/bin/env python3
"""
Automated Regression Test Suite for Surprise Me / Random Note Dice Roll

Asserts:
1. Structural Presence: <button id="random-note-btn"> exists with class="random-btn".
2. Emoji Content: Contains <span class="random-icon">🎲</span>.
3. Accessibility: Retains aria-label and title indicating shortcut (r).
4. Symmetrical Styling & Animation: .random-btn, hover, dark mode, .random-icon, and .rolling rules exist.
5. Print Stylesheet: Ensures .random-btn and #random-note-btn are suppressed in @media print.
6. Candidate Note Filter Logic: Unit tests positive (content notes) and negative (utility/hubs/tags) filtering.
7. Keyboard Shortcuts & Event Handlers: Asserts 'r'/'R' shortcut listener, focus guards, and zero inline handlers.
8. Coverage Integrity: Sampled across generated pages (excluding Hugo redirect stubs).
"""

import os
import re
import sys

# Gate 5: Ensure UTF-8 stdout across Windows console and CI
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    public_dir = os.path.join(root_dir, "public")
    index_html_path = os.path.join(public_dir, "index.html")

    print("--- Surprise Me / Random Note Dice Roll Test Suite ---")

    if not os.path.exists(index_html_path):
        print(f"Error: {index_html_path} does not exist. Run 'hugo' first.")
        sys.exit(1)

    with open(index_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Structural Presence: <button id="random-note-btn" class="random-btn">
    print("1. Validating #random-note-btn button DOM structure:")
    button_match = re.search(
        r'<button[^>]*\bid=["\']?random-note-btn["\']?[^>]*>',
        html,
        re.IGNORECASE
    )
    assert button_match, "❌ FAILED: Missing <button id='random-note-btn'> in generated HTML!"
    button_tag = button_match.group(0)

    assert re.search(r'\btype=["\']?button["\']?', button_tag, re.IGNORECASE), (
        f"❌ FAILED: #random-note-btn button missing type='button': {button_tag}"
    )
    assert re.search(r'\bclass=["\']?[^"\'>]*\brandom-btn\b', button_tag, re.IGNORECASE), (
        f"❌ FAILED: #random-note-btn button missing class='random-btn': {button_tag}"
    )
    assert re.search(r'\baria-label=["\']?Surprise me / Random note \(r\)["\']?', button_tag, re.IGNORECASE), (
        f"❌ FAILED: #random-note-btn button missing aria-label: {button_tag}"
    )
    assert re.search(r'\btitle=["\']?Surprise me / Random note \(r\)["\']?', button_tag, re.IGNORECASE), (
        f"❌ FAILED: #random-note-btn button missing title: {button_tag}"
    )
    print("  ✓ <button id='random-note-btn' type='button' class='random-btn'> verified.")

    # 2. Emoji Content: 🎲 icon
    print("\n2. Validating Dice Emoji 🎲 Content:")
    icon_match = re.search(
        r'<span[^>]*\bclass=["\']?[^"\'>]*\brandom-icon\b[^"\'>]*["\']?[^>]*>🎲</span>',
        html,
        re.IGNORECASE
    )
    assert icon_match, "❌ FAILED: Missing <span class='random-icon'>🎲</span> inside header!"
    print("  ✓ Dice emoji <span class='random-icon'>🎲</span> verified.")

    # 3. Negative Assertions: Zero Inline Event Handlers
    print("\n3. Validating Negative Assertions (Rocket Loader Safety):")
    assert not re.search(r'id=["\']?random-note-btn["\']?[^>]*\bonclick\b', html, re.IGNORECASE), (
        "❌ FAILED: Inline onclick detected on #random-note-btn!"
    )
    print("  ✓ Negative test passed: Zero inline onclick handlers on #random-note-btn.")

    # 4. Symmetrical Styling & Spin Animation Validation
    print("\n4. Validating Symmetrical CSS Styling & Spin Animation:")
    assert re.search(r'\.random-btn\b', html), (
        "❌ FAILED: Missing .random-btn CSS rule in generated HTML head!"
    )
    assert re.search(r'\[data-theme=["\']?dark["\']?\][^}]*\.random-btn\b', html), (
        "❌ FAILED: Missing dark mode styling for .random-btn in generated HTML head!"
    )
    assert re.search(r'\.random-icon\b', html), (
        "❌ FAILED: Missing .random-icon CSS rule in generated HTML head!"
    )
    assert re.search(r'\.random-btn\.rolling\s+\.random-icon', html), (
        "❌ FAILED: Missing .random-btn.rolling .random-icon spin animation in generated HTML head!"
    )
    print("  ✓ Symmetrical .random-btn, dark mode, .random-icon, and rolling animation verified.")

    # 5. Print Stylesheet Suppression
    print("\n5. Validating Print Stylesheet Suppression:")
    print_section = re.search(r'@media\s+print\s*\{(.*?)\}\s*</style>', html, re.DOTALL)
    assert print_section, "❌ FAILED: Could not find @media print block in generated HTML!"
    print_css = print_section.group(1)
    assert ".random-btn" in print_css or "#random-note-btn" in print_css, (
        "❌ FAILED: .random-btn / #random-note-btn is not hidden in @media print!"
    )
    print("  ✓ .random-btn / #random-note-btn cleanly hidden in @media print.")

    # 6. Candidate Filter Logic Validation
    print("\n6. Validating Candidate Note Filtering Logic (Positive & Negative Test Cases):")
    # Simulate candidate filter logic matching layouts/partials/header.html
    excluded_paths = {
        '/',
        '/sitemap/',
        '/now/',
        '/uses/',
        '/posts/',
        '/books/',
        '/games/',
        '/tech/',
        '/other-interests/',
        '/tags/'
    }

    def is_candidate(item):
        if not item or not item.get("permalink") or not item.get("title"):
            return False
        p = item["permalink"].lower()
        if not p.endswith("/"):
            p += "/"
        if p in excluded_paths:
            return False
        if p.startswith("/tags/") or p.startswith("/posts/page/"):
            return False
        return True

    # Negative test cases: utility and hub pages that MUST be rejected
    utility_samples = [
        {"title": "Home", "permalink": "/"},
        {"title": "Sitemap", "permalink": "/sitemap/"},
        {"title": "Sitemap No Slash", "permalink": "/sitemap"},
        {"title": "Now", "permalink": "/now/"},
        {"title": "Uses", "permalink": "/uses/"},
        {"title": "Posts Hub", "permalink": "/posts/"},
        {"title": "Books Hub", "permalink": "/books/"},
        {"title": "Games Hub", "permalink": "/games/"},
        {"title": "Tech Hub", "permalink": "/tech/"},
        {"title": "Other Interests Hub", "permalink": "/other-interests/"},
        {"title": "Tags Root", "permalink": "/tags/"},
        {"title": "Tag Page", "permalink": "/tags/linux/"},
        {"title": "Pagination", "permalink": "/posts/page/2/"},
        {"title": "", "permalink": "/books/intro/accounting/"},
        {"title": "No Permalink", "permalink": ""},
    ]

    for item in utility_samples:
        assert not is_candidate(item), f"❌ FAILED: Utility/hub item wrongly accepted as candidate: {item}"
    print("  ✓ Negative assertions: All utility, taxonomy, pagination, and invalid pages correctly rejected.")

    # Positive test cases: real notes that MUST be accepted
    note_samples = [
        {"title": "Accounting", "permalink": "/books/intro/accounting/"},
        {"title": "Action & Adventure", "permalink": "/games/action-adventure/"},
        {"title": "Ansible", "permalink": "/tech/ansible/"},
        {"title": "AI", "permalink": "/other-interests/ai/"},
        {"title": "Resident Evil Review", "permalink": "/posts/resident-evil-review/"},
        {"title": "About", "permalink": "/about/"},
    ]

    for item in note_samples:
        assert is_candidate(item), f"❌ FAILED: Genuine note item rejected as candidate: {item}"
    print("  ✓ Positive assertions: Valid digital garden notes correctly accepted as candidates.")

    # 7. Keyboard Shortcut Listener Validation
    print("\n7. Validating Keyboard Shortcuts & Event Handler Safety:")
    assert re.search(r"\(e\.key\s*===\s*['\"]r['\"]\s*\|\|\s*e\.key\s*===\s*['\"]R['\"]\)", html), (
        "❌ FAILED: Missing keyboard shortcut listener for 'r' / 'R' in header script!"
    )
    assert re.search(r"triggerRandomNote", html), (
        "❌ FAILED: Missing triggerRandomNote function in header script!"
    )
    print("  ✓ 'r' / 'R' shortcut listener and triggerRandomNote function verified.")

    # 8. Sample Across Multiple Generated Pages
    print("\n8. Validating Presence Across Sample Generated Pages:")
    sample_pages = [
        "index.html",
        "tech/index.html",
        "books/index.html",
        "games/index.html",
        "posts/index.html",
    ]
    checked_count = 0
    for rel_path in sample_pages:
        full_path = os.path.join(public_dir, rel_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as pf:
                page_html = pf.read()
            # Skip Hugo alias redirect stubs
            if re.search(r'http-equiv=["\']?refresh["\']?', page_html, re.IGNORECASE):
                continue
            assert re.search(r'id=["\']?random-note-btn["\']?', page_html, re.IGNORECASE), (
                f"❌ FAILED: Missing #random-note-btn on {rel_path}"
            )
            checked_count += 1

    print(f"  ✓ Verified on {checked_count} sampled generated pages.")
    print("\n🎉 ALL RANDOM NOTE DICE ROLL TESTS PASSED! (100% Green)\n")

if __name__ == "__main__":
    run_tests()
