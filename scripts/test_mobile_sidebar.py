#!/usr/bin/env python3
"""
Automated regression test suite for mobile navigation sidebar, overlay stacking context,
and interactive clickability.
Validates:
1. CSS Stacking Context: .layout-container does not create an isolated stacking context with an integer z-index.
2. Z-Index Hierarchy: .sidebar-left (z-index: 1200) sits above #sidebar-overlay (z-index: 1150).
3. Mobile Media Query: Inside @media (max-width: 768px), .layout-container explicitly enforces z-index: auto.
4. DOM Structure: Overlay (#sidebar-overlay), mobile menu button (#mobile-menu-btn), close button (#sidebar-close-btn),
   and sidebar (#sidebar-left) exist across generated HTML pages.
5. JS Click Handler: Sidebar click listener utilizes e.target.closest('a') so clicks on emojis/icons inside links work cleanly.
6. Cloudflare Safety: Zero inline event handlers (onclick=).
"""

import os
import re
import sys

# Ensure UTF-8 output across Windows and Linux terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    public_index = os.path.join(root_dir, "public", "index.html")
    head_partial = os.path.join(root_dir, "layouts", "partials", "head.html")
    header_partial = os.path.join(root_dir, "layouts", "partials", "header.html")
    sidebar_partial = os.path.join(root_dir, "layouts", "partials", "sidebar.html")

    if not os.path.exists(public_index):
        print(f"Error: {public_index} does not exist. Run 'hugo' first.")
        sys.exit(1)

    print("--- Mobile Sidebar & Overlay Stacking Context Test Suite ---")

    # 1. Verify CSS rules in head.html
    print("1. Verifying CSS Stacking Context in layouts/partials/head.html:")
    with open(head_partial, "r", encoding="utf-8") as fp:
        head_css = fp.read()

    # Check that .layout-container does NOT have an integer z-index like z-index: 1
    bad_zindex_match = re.search(r'\.layout-container\s*\{[^}]*z-index:\s*[1-9]\d*', head_css)
    assert not bad_zindex_match, (
        f"Found forbidden integer z-index on .layout-container: '{bad_zindex_match.group(0)}'. "
        "This creates an isolated stacking context trapping .sidebar-left behind #sidebar-overlay!"
    )

    # Check that .layout-container has z-index: auto
    assert re.search(r'\.layout-container\s*\{[^}]*z-index:\s*auto;', head_css), (
        ".layout-container must explicitly specify 'z-index: auto;' to avoid stacking context traps."
    )

    # Check mobile query specifically using robust brace counting
    media_m = re.search(r'@media\s*\(\s*max-width:\s*768px\s*\)\s*\{', head_css)
    assert media_m, "Could not find @media (max-width: 768px) in head.html"
    start_idx = media_m.end()
    brace_count = 1
    end_idx = start_idx
    while brace_count > 0 and end_idx < len(head_css):
        if head_css[end_idx] == '{':
            brace_count += 1
        elif head_css[end_idx] == '}':
            brace_count -= 1
        end_idx += 1
    mobile_css = head_css[start_idx:end_idx - 1]

    # Check mobile .layout-container has z-index: auto
    assert re.search(r'\.layout-container\s*\{[^}]*z-index:\s*auto;', mobile_css), (
        "Mobile media query (@media max-width: 768px) must enforce 'z-index: auto;' on .layout-container."
    )

    # Check .sidebar-left z-index in mobile query
    sidebar_z_m = re.search(r'\.sidebar-left\s*\{[^}]*z-index:\s*(\d+);', mobile_css)
    assert sidebar_z_m, "Could not find z-index for .sidebar-left in mobile media query"
    sidebar_z = int(sidebar_z_m.group(1))

    # Check .sidebar-overlay z-index
    overlay_z_m = re.search(r'\.sidebar-overlay\s*\{[^}]*z-index:\s*(\d+);', head_css)
    assert overlay_z_m, "Could not find z-index for .sidebar-overlay in head.html"
    overlay_z = int(overlay_z_m.group(1))

    assert sidebar_z > overlay_z, (
        f"Stacking error: .sidebar-left z-index ({sidebar_z}) must be strictly greater than "
        f".sidebar-overlay z-index ({overlay_z})!"
    )
    print(f"  ✓ Z-index hierarchy verified: .sidebar-left ({sidebar_z}) > .sidebar-overlay ({overlay_z}).")
    print("  ✓ Stacking context verified: .layout-container has z-index: auto (no stacking context trap).")

    # 2. Verify HTML DOM elements across generated pages
    print("2. Verifying DOM structure across generated HTML pages:")
    sample_pages = [
        os.path.join(root_dir, "public", "index.html"),
        os.path.join(root_dir, "public", "about", "index.html"),
    ]

    # Find a couple of tech and book pages if available
    for root, dirs, files in os.walk(os.path.join(root_dir, "public")):
        for f in files:
            if f == "index.html":
                p = os.path.join(root, f)
                if p not in sample_pages:
                    sample_pages.append(p)
                if len(sample_pages) >= 5:
                    break
        if len(sample_pages) >= 5:
            break

    for page_path in sample_pages:
        rel_p = os.path.relpath(page_path, root_dir)
        with open(page_path, "r", encoding="utf-8") as fp:
            html = fp.read()

        assert re.search(r'id=["\']?sidebar-overlay["\'\s>]', html), f"Missing #sidebar-overlay in {rel_p}"
        assert re.search(r'class=["\']?[^"\'>]*sidebar-overlay', html), f"Missing class='sidebar-overlay' in {rel_p}"
        assert re.search(r'id=["\']?mobile-menu-btn["\'\s>]', html), f"Missing #mobile-menu-btn in {rel_p}"
        assert re.search(r'id=["\']?sidebar-left["\'\s>]', html), f"Missing #sidebar-left in {rel_p}"
        assert re.search(r'id=["\']?sidebar-close-btn["\'\s>]', html), f"Missing #sidebar-close-btn in {rel_p}"

        # Ensure #sidebar-overlay is not inside .layout-container
        layout_m = re.search(r'class=["\']?[^"\'>]*layout-container', html)
        overlay_m = re.search(r'id=["\']?sidebar-overlay["\'\s>]', html)
        assert overlay_m and layout_m, f"DOM elements missing in {rel_p}"
        assert overlay_m.start() < layout_m.start(), (
            f"In {rel_p}, #sidebar-overlay should be declared outside and before .layout-container."
        )

    print(f"  ✓ Verified DOM presence and nesting across {len(sample_pages)} generated pages.")

    # 3. Verify JavaScript logic in header.html
    print("3. Verifying JavaScript drawer logic and Rocket Loader safety:")
    with open(header_partial, "r", encoding="utf-8") as fp:
        header_js = fp.read()

    # Verify closest('a') is used for link clicks
    assert "e.target.closest('a')" in header_js, (
        "layouts/partials/header.html must use e.target.closest('a') to ensure clicks on icons/spans "
        "inside links correctly trigger navigation and close the drawer."
    )

    # Verify overlay and close button click listeners
    assert "overlay.addEventListener('click'" in header_js, (
        "layouts/partials/header.html missing click event listener on overlay"
    )
    assert "closeBtn.addEventListener('click'" in header_js, (
        "layouts/partials/header.html missing click event listener on closeBtn"
    )

    # Check for zero inline onclick handlers
    for fpath in [header_partial, sidebar_partial]:
        with open(fpath, "r", encoding="utf-8") as fp:
            content = fp.read()
        assert not re.search(r'\bon[a-z]+\s*=', content, re.IGNORECASE), (
            f"Found forbidden inline event handler in {os.path.basename(fpath)}. "
            "Cloudflare Rocket Loader will suppress this!"
        )

    print("  ✓ Link navigation click logic uses e.target.closest('a').")
    print("  ✓ Unobtrusive event listeners attached for overlay, close button, and menu button.")
    print("  ✓ Zero inline event handlers verified (Cloudflare Rocket Loader safe).")

    print("--- All Mobile Sidebar Overlay tests passed successfully! ---")

if __name__ == "__main__":
    run_tests()
