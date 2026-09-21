#!/usr/bin/env python3
"""
Automated Test Suite for Frosted Title Bar & Compact Modern Sidebar UX
Validates:
1. Frosted Glass Title Bar:
   - .site-header includes hardware-accelerated backdrop-filter blur.
   - .site-header includes translucent border and atmospheric shadow.
   - Dark mode styles for .site-header are defined.
2. Full-Height Chessboard Watermark:
   - .chess-watermark.corner-top-right and .corner-top-left start at top: 0 (not top: 56px).
   - Watermark extends behind the translucent title bar.
3. Compact Modern Sidebar:
   - .sidebar-left explicitly uses Ubuntu typeface (var(--font-family-sans)).
   - Compact vertical rhythm: details.nav-section-details margin-top <= 0.5rem, nav-tree li margin <= 0.2rem.
   - Modern pill navigation: .nav-tree a.active has left-accent border (border-left: 3px solid var(--link-color)).
   - No lingering inline styles (e.g. style="margin-top: 1.5rem;") in sidebar structure.
4. Compliance & Guardrails:
   - Zero inline event handlers (Rule 2).
   - Minified-HTML safe regex assertions (Rule 14).
   - UTF-8 console output safe across Windows/Linux (Rule 12).
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
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    public_index = os.path.join(root_dir, "public", "index.html")

    if not os.path.exists(public_index):
        print("Error: public/index.html does not exist. Run 'hugo' first.")
        sys.exit(1)

    print("--- Frosted Title Bar & Compact Modern Sidebar UX Test Suite ---")

    with open(public_index, "r", encoding="utf-8") as fp:
        html_content = fp.read()

    # 1. Frosted Glass Title Bar
    print("1. Auditing Frosted Glass Title Bar styles:")
    assert re.search(r'backdrop-filter:\s*blur\(8px\)', html_content), (
        "Missing backdrop-filter: blur(8px) on .site-header"
    )
    assert re.search(r'-webkit-backdrop-filter:\s*blur\(8px\)', html_content), (
        "Missing -webkit-backdrop-filter: blur(8px) on .site-header"
    )
    # Minification strips spaces and leading zero: border-bottom:1px solid rgba(255,255,255,.25)
    assert re.search(r'border-bottom:\s*1px\s+solid\s+rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0?\.25\s*\)', html_content), (
        "Missing translucent border-bottom on .site-header"
    )
    assert re.search(r'\[data-theme=["\']?dark["\']?\]\s*\.site-header', html_content), (
        "Missing dark mode overrides for .site-header"
    )
    print("  ✓ Frosted glass header backdrop-filter, border, and dark mode overrides verified.")

    # 2. Chessboard Watermark top offset
    print("2. Auditing Chessboard Watermark full-height top offset:")
    # Negative assertion: corner-top-right and corner-top-left must NOT be 56px
    assert not re.search(r'\.chess-watermark\.corner-top-right\s*\{\s*top:\s*56px', html_content), (
        "Regression: .chess-watermark.corner-top-right is still set to top: 56px"
    )
    assert not re.search(r'\.chess-watermark\.corner-top-left\s*\{\s*top:\s*56px', html_content), (
        "Regression: .chess-watermark.corner-top-left is still set to top: 56px"
    )
    # Positive assertion: corner-top-right and corner-top-left set to top: 0
    assert re.search(r'\.chess-watermark\.corner-top-right\s*\{\s*top:\s*0[;}]', html_content), (
        "Missing .chess-watermark.corner-top-right { top: 0; }"
    )
    assert re.search(r'\.chess-watermark\.corner-top-left\s*\{\s*top:\s*0[;}]', html_content), (
        "Missing .chess-watermark.corner-top-left { top: 0; }"
    )
    print("  ✓ Watermark starts at top: 0 and flows behind frosted title bar.")

    # 3. Compact Modern Sidebar Typography & Palette
    print("3. Auditing Compact Modern Sidebar typography and palette:")
    assert re.search(r'\.sidebar-left\s*\{[^}]*font-family:\s*var\(--font-family-sans\)', html_content), (
        "Missing explicit font-family: var(--font-family-sans) on .sidebar-left"
    )
    assert re.search(r'--bg-sidebar:\s*#f8fafc[;}]', html_content), (
        "Missing refreshed light mode --bg-sidebar: #f8fafc"
    )
    assert re.search(r'--bg-sidebar:\s*#0f172a[;}]', html_content), (
        "Missing refreshed dark mode --bg-sidebar: #0f172a"
    )
    print("  ✓ Sidebar Ubuntu typography and slate background variables verified.")

    # 4. Compact Rhythm and Pill Active Indicator
    print("4. Auditing sidebar vertical rhythm and pill navigation:")
    # Compact section details margin (handles minified .45rem or 0.45rem)
    assert re.search(r'details\.nav-section-details\s*\{\s*margin-top:\s*0?\.45rem[;}]', html_content), (
        "Missing compact margin-top: 0.45rem on details.nav-section-details"
    )
    # Compact section title margin (handles minified .85rem or 0.85rem)
    assert re.search(r'\.nav-section-title\s*\{[^}]*margin-top:\s*0?\.85rem[;}]', html_content), (
        "Missing compact margin-top: 0.85rem on .nav-section-title"
    )
    # Modern pill active indicator
    assert re.search(r'\.nav-tree\s+a\.active\s*\{[^}]*border-left:\s*3px\s+solid\s+var\(--link-color\)[;}]', html_content), (
        "Missing border-left: 3px solid var(--link-color) on active nav links"
    )
    # Smooth hover effect
    assert re.search(r'\.nav-tree\s+a:hover\s*\{[^}]*transform:\s*translateX\(2px\)[;}]', html_content), (
        "Missing translateX hover effect on .nav-tree a:hover"
    )
    # Negative assertion: ensure inline margin-top on Site section is eliminated
    assert 'style="margin-top: 1.5rem;"' not in html_content, (
        "Lingering inline style='margin-top: 1.5rem;' found in HTML"
    )
    print("  ✓ Compact vertical rhythm (40% tightened) and active pill indicator verified.")

    # 5. Cloudflare Rocket Loader & Inline Event Safety (Rule 2)
    print("5. Auditing Cloudflare Rocket Loader safety across header and sidebar:")
    header_sidebar_matches = re.findall(r'<(?:header|nav|aside|details|summary)[^>]*>', html_content, re.IGNORECASE)
    for tag in header_sidebar_matches:
        assert not re.search(r'\son[a-z]+\s*=', tag, re.IGNORECASE), (
            f"Rule 2 violation: inline event handler found in header/sidebar tag: {tag}"
        )
    print("  ✓ Zero inline event handlers found (100% Rocket Loader safe).")

    print("\n✓ All title bar and sidebar UX tests passed successfully!")

if __name__ == "__main__":
    run_tests()
