#!/usr/bin/env python3
"""
Automated Regression Test Suite for Symmetrical Search Emoji Header Button

Asserts:
1. Structural Presence: #site-search is a <button type="button"> with class="search-btn".
2. Emoji Content: Contains <span class="search-icon">🔍</span>.
3. Accessibility: Retains aria-label and title for search shortcuts (/ or Ctrl+K).
4. Negative Testing: Obsolete faux <input> and placeholder="/" completely eliminated.
5. Symmetrical Styling: .search-btn and [data-theme="dark"] .search-btn rules exist in CSS.
6. Coverage Integrity: Sampled across generated pages (excluding Hugo redirect stubs).
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

    print("--- Symmetrical Search Emoji Header Button Test Suite ---")

    if not os.path.exists(index_html_path):
        print(f"Error: {index_html_path} does not exist. Run 'hugo' first.")
        sys.exit(1)

    with open(index_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Structural Presence: <button> with id="site-search" and class="search-btn"
    print("1. Validating #site-search button DOM structure:")
    button_match = re.search(
        r'<button[^>]*\bid=["\']?site-search["\']?[^>]*>',
        html,
        re.IGNORECASE
    )
    assert button_match, "❌ FAILED: Missing <button id='site-search'> in generated HTML!"
    button_tag = button_match.group(0)

    assert re.search(r'\btype=["\']?button["\']?', button_tag, re.IGNORECASE), (
        f"❌ FAILED: #site-search button missing type='button': {button_tag}"
    )
    assert re.search(r'\bclass=["\']?[^"\'>]*\bsearch-btn\b', button_tag, re.IGNORECASE), (
        f"❌ FAILED: #site-search button missing class='search-btn': {button_tag}"
    )
    assert re.search(r'\baria-label=["\']?Search notes', button_tag, re.IGNORECASE), (
        f"❌ FAILED: #site-search button missing aria-label='Search notes...': {button_tag}"
    )
    print("  ✓ <button id='site-search' type='button' class='search-btn'> verified.")

    # 2. Emoji Content: 🔍 icon
    print("\n2. Validating Search Emoji 🔍 Content:")
    icon_match = re.search(
        r'<span[^>]*\bclass=["\']?[^"\'>]*\bsearch-icon\b[^"\'>]*["\']?[^>]*>🔍</span>',
        html,
        re.IGNORECASE
    )
    assert icon_match, "❌ FAILED: Missing <span class='search-icon'>🔍</span> inside header!"
    print("  ✓ Search emoji <span class='search-icon'>🔍</span> verified.")

    # 3. Negative Assertions: Old Faux Input Elimination
    print("\n3. Validating Negative Assertions (Faux Input & Stray '/' Slash Elimination):")
    assert not re.search(r'<input[^>]*\bid=["\']?site-search["\']?', html, re.IGNORECASE), (
        "❌ FAILED: Legacy <input id='site-search'> still present in generated HTML!"
    )
    assert not re.search(r'id=["\']?site-search["\']?[^>]*placeholder=["\']?\/["\']?', html, re.IGNORECASE), (
        "❌ FAILED: Legacy placeholder='/' on #site-search still present in generated HTML!"
    )
    assert not re.search(r'id=["\']?site-search["\']?[^>]*\bclass=["\']?[^"\'>]*\bsearch-input\b', html, re.IGNORECASE), (
        "❌ FAILED: Obsolete class='search-input' on #site-search still present in generated HTML!"
    )
    print("  ✓ Negative test passed: Legacy faux <input>, placeholder='/', and .search-input cleanly eliminated.")

    # 4. Symmetrical Styling Validation
    print("\n4. Validating Symmetrical CSS Styling:")
    assert re.search(r'\.search-btn\s*\{', html), (
        "❌ FAILED: Missing .search-btn CSS rule in generated HTML head!"
    )
    assert re.search(r'\[data-theme=["\']?dark["\']?\]\s*[^}]*\.search-btn', html), (
        "❌ FAILED: Missing dark mode styling for .search-btn in generated HTML head!"
    )
    assert re.search(r'\.search-icon\s*\{', html), (
        "❌ FAILED: Missing .search-icon CSS rule in generated HTML head!"
    )
    print("  ✓ Symmetrical .search-btn, dark theme, and .search-icon rules verified.")

    # 5. Keyboard Shortcut & Event Handlers
    print("\n5. Validating Keyboard Shortcuts & Event Handler Safety:")
    assert re.search(r"e\.key\s*===\s*['\"]\/['\"]", html), (
        "❌ FAILED: Missing keyboard shortcut listener for '/' in header script"
    )
    assert re.search(r"\((?:e\.ctrlKey\s*\|\|\s*e\.metaKey|e\.metaKey\s*\|\|\s*e\.ctrlKey)\)\s*&&\s*e\.key(\.toLowerCase\(\))?\s*===\s*['\"]k['\"]", html), (
        "❌ FAILED: Missing keyboard shortcut listener for Ctrl+K in header script"
    )
    # Confirm zero inline handlers on site-search
    assert not re.search(r'<button[^>]*id=["\']?site-search["\']?[^>]*\bon[a-z]+=', html, re.IGNORECASE), (
        "❌ FAILED: Inline event handler detected on #site-search button!"
    )
    print("  ✓ Keyboard shortcuts ('/', Ctrl+K) and unobtrusive event handling verified.")

    # 6. Cross-Page Sampling
    print("\n6. Validating Cross-Page Coverage Integrity:")
    sample_pages = [
        os.path.join(public_dir, "index.html"),
        os.path.join(public_dir, "tags", "index.html"),
        os.path.join(public_dir, "posts", "index.html"),
        os.path.join(public_dir, "now", "index.html"),
    ]
    for p in sample_pages:
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8") as f:
            p_html = f.read()
        # Skip alias redirect stubs (Gate 20)
        if re.search(r'http-equiv=["\']?refresh["\']?', p_html, re.IGNORECASE):
            continue
        rel_path = os.path.relpath(p, public_dir)
        assert re.search(r'<button[^>]*\bid=["\']?site-search["\']?[^>]*>', p_html, re.IGNORECASE), (
            f"❌ FAILED: Missing <button id='site-search'> on {rel_path}"
        )
        assert "🔍" in p_html, f"❌ FAILED: Missing search emoji on {rel_path}"
        print(f"  ✓ {rel_path}: Search emoji button verified.")

    print("\n✓ All Symmetrical Search Emoji Header Button tests passed successfully!")

if __name__ == "__main__":
    run_tests()
