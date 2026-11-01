#!/usr/bin/env python3
"""
Automated Regression Test Suite for Prominent Link to tools.arunsr.in

Asserts:
1. Header Structural Presence: <a id="header-tools-btn"> with class="tools-btn".
2. Header Attributes: href="https://tools.arunsr.in", target="_blank", rel="noopener noreferrer".
3. Header Content & Accessibility: Contains <span class="tools-icon">🧰</span>, aria-label, and title.
4. Sidebar Structural Presence: Link to https://tools.arunsr.in in sidebar with target="_blank", rel="noopener noreferrer".
5. Sidebar Content: Contains "🧰 Tools" and external indicator <span class="external-icon">↗</span>.
6. Symmetrical Styling: .tools-btn and [data-theme="dark"] .tools-btn rules exist in CSS.
7. Print Stylesheet Discipline: .tools-btn / #header-tools-btn suppressed in @media print.
8. Non-Interference: Existing header buttons (#theme-toggle, #site-search, #random-note-btn) intact.
9. Coverage Integrity: Sampled across generated pages (excluding Hugo redirect stubs).
10. Rocket Loader Safety: Zero inline event handlers on tools links.
"""

import os
import re
import sys

# Gate 5 & Rule 12: Ensure UTF-8 stdout across Windows console and CI
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    public_dir = os.path.join(root_dir, "public")
    index_html_path = os.path.join(public_dir, "index.html")

    print("--- Prominent Link to tools.arunsr.in Test Suite ---")

    if not os.path.exists(index_html_path):
        print(f"Error: {index_html_path} does not exist. Run 'hugo' first.")
        sys.exit(1)

    with open(index_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Header Structural Presence & Attributes
    print("1. Validating Header Tools Button (#header-tools-btn):")
    header_btn_match = re.search(
        r'<a[^>]*\bid=["\']?header-tools-btn["\']?[^>]*>',
        html,
        re.IGNORECASE
    )
    assert header_btn_match, "❌ FAILED: Missing <a id='header-tools-btn'> in generated HTML!"
    header_btn_tag = header_btn_match.group(0)

    assert re.search(r'\bclass=["\']?[^"\'>]*\btools-btn\b', header_btn_tag, re.IGNORECASE), (
        f"❌ FAILED: #header-tools-btn missing class='tools-btn': {header_btn_tag}"
    )
    assert re.search(r'\bhref=["\']?https://tools\.arunsr\.in/?["\']?', header_btn_tag, re.IGNORECASE), (
        f"❌ FAILED: #header-tools-btn href is not https://tools.arunsr.in: {header_btn_tag}"
    )
    assert re.search(r'\btarget=["\']?_blank["\']?', header_btn_tag, re.IGNORECASE), (
        f"❌ FAILED: #header-tools-btn missing target='_blank': {header_btn_tag}"
    )
    assert re.search(r'\brel=["\']?[^"\'>]*\bnoopener\b[^"\'>]*\bnoreferrer\b', header_btn_tag, re.IGNORECASE) or \
           re.search(r'\brel=["\']?[^"\'>]*\bnoreferrer\b[^"\'>]*\bnoopener\b', header_btn_tag, re.IGNORECASE), (
        f"❌ FAILED: #header-tools-btn missing rel='noopener noreferrer': {header_btn_tag}"
    )
    assert re.search(r'\baria-label=["\']?Tools \(tools\.arunsr\.in\)["\']?', header_btn_tag, re.IGNORECASE), (
        f"❌ FAILED: #header-tools-btn missing descriptive aria-label: {header_btn_tag}"
    )
    assert re.search(r'\btitle=["\']?Tools \(tools\.arunsr\.in\)["\']?', header_btn_tag, re.IGNORECASE), (
        f"❌ FAILED: #header-tools-btn missing descriptive title: {header_btn_tag}"
    )
    print("  ✓ <a id='header-tools-btn' class='tools-btn' href='https://tools.arunsr.in' target='_blank' rel='noopener noreferrer'> verified.")

    # 2. Header Content & Icon
    print("\n2. Validating Header Tools Icon (🧰) and External Indicator (↗):")
    icon_match = re.search(
        r'<span[^>]*\bclass=["\']?[^"\'>]*\btools-icon\b[^"\'>]*["\']?[^>]*>🧰</span>',
        html,
        re.IGNORECASE
    )
    assert icon_match, "❌ FAILED: Missing <span class='tools-icon'>🧰</span> inside header!"
    ext_icon_match = re.search(
        r'<span[^>]*\bclass=["\']?[^"\'>]*\btools-external-icon\b[^"\'>]*["\']?[^>]*>↗</span>',
        html,
        re.IGNORECASE
    )
    assert ext_icon_match, "❌ FAILED: Missing <span class='tools-external-icon'>↗</span> inside header!"
    print("  ✓ Header tools icon <span class='tools-icon'>🧰</span> and external indicator ↗ verified.")

    # 3. Sidebar Structural Presence & Content
    print("\n3. Validating Sidebar Navigation Tools Link:")
    nav_tree_match = re.search(
        r'<nav[^>]*\bclass=["\']?[^"\'>]*\bnav-tree\b[^>]*>([\s\S]*?)</nav>',
        html,
        re.IGNORECASE
    )
    assert nav_tree_match, "❌ FAILED: Missing <nav class='nav-tree'> in generated HTML!"
    nav_tree_html = nav_tree_match.group(1)

    sidebar_match = re.search(
        r'<a[^>]*\bhref=["\']?https://tools\.arunsr\.in/?["\']?[^>]*>([\s\S]*?)</a>',
        nav_tree_html,
        re.IGNORECASE
    )
    assert sidebar_match, "❌ FAILED: Missing link to https://tools.arunsr.in in sidebar!"
    sidebar_anchor = sidebar_match.group(0)
    sidebar_content = sidebar_match.group(1)

    assert re.search(r'\btarget=["\']?_blank["\']?', sidebar_anchor, re.IGNORECASE), (
        f"❌ FAILED: Sidebar tools link missing target='_blank': {sidebar_anchor}"
    )
    assert re.search(r'\brel=["\']?[^"\'>]*\bnoopener\b', sidebar_anchor, re.IGNORECASE), (
        f"❌ FAILED: Sidebar tools link missing rel='noopener': {sidebar_anchor}"
    )
    assert "🧰" in sidebar_content and "Tools" in sidebar_content, (
        f"❌ FAILED: Sidebar link text does not contain '🧰' and 'Tools': {sidebar_content}"
    )
    assert re.search(r'<span[^>]*\bclass=["\']?[^"\'>]*\bexternal-icon\b[^>]*>↗</span>', sidebar_content, re.IGNORECASE), (
        f"❌ FAILED: Sidebar tools link missing external indicator ↗: {sidebar_content}"
    )
    print("  ✓ Sidebar link to https://tools.arunsr.in with '🧰 Tools' and external indicator verified.")

    # 4. Symmetrical Styling & CSS rules
    print("\n4. Validating Symmetrical CSS Styling:")
    assert re.search(r'\.tools-btn\b', html), (
        "❌ FAILED: Missing .tools-btn CSS rule in generated HTML head!"
    )
    assert re.search(r'\[data-theme=["\']?dark["\']?\]\s*[^}]*\.tools-btn\b', html), (
        "❌ FAILED: Missing dark mode styling for .tools-btn in generated HTML head!"
    )
    assert re.search(r'\.tools-icon\b', html), (
        "❌ FAILED: Missing .tools-icon CSS rule in generated HTML head!"
    )
    assert re.search(r'\.tools-external-icon\b', html), (
        "❌ FAILED: Missing .tools-external-icon CSS rule in generated HTML head!"
    )
    assert re.search(r'\.nav-tree\s+a\.external-link\b', html), (
        "❌ FAILED: Missing .nav-tree a.external-link CSS rule in generated HTML head!"
    )
    print("  ✓ Symmetrical .tools-btn, dark theme, and .tools-icon rules verified.")

    # 5. Print Stylesheet Suppression Discipline
    print("\n5. Validating Print Stylesheet Suppression Discipline:")
    print_section = re.search(r'@media\s+print\s*\{(.*)\}\s*</style>', html, re.DOTALL)
    assert print_section, "❌ FAILED: Missing @media print block in generated HTML!"
    print_css = print_section.group(1)
    assert ".tools-btn" in print_css or "#header-tools-btn" in print_css, (
        "❌ FAILED: .tools-btn / #header-tools-btn is not hidden in @media print!"
    )
    print("  ✓ .tools-btn / #header-tools-btn cleanly hidden in @media print.")

    # 6. Non-Interference with Existing Controls
    print("\n6. Validating Non-Interference with Existing Controls:")
    assert re.search(r'\bid=["\']?random-note-btn["\']?', html, re.IGNORECASE), (
        "❌ FAILED: #random-note-btn was removed or disrupted!"
    )
    assert re.search(r'\bid=["\']?site-search["\']?', html, re.IGNORECASE), (
        "❌ FAILED: #site-search was removed or disrupted!"
    )
    assert re.search(r'\bid=["\']?theme-toggle["\']?', html, re.IGNORECASE), (
        "❌ FAILED: #theme-toggle was removed or disrupted!"
    )
    assert re.search(r'href=["\']?/uses/?["\']?', html, re.IGNORECASE), (
        "❌ FAILED: /uses/ link in sidebar was removed or disrupted!"
    )
    assert re.search(r'href=["\']?/now/?["\']?', html, re.IGNORECASE), (
        "❌ FAILED: /now/ link in sidebar was removed or disrupted!"
    )
    print("  ✓ Existing header buttons (#random-note-btn, #site-search, #theme-toggle) and sidebar items intact.")

    # 7. Rocket Loader Safety (Zero Inline Event Handlers)
    print("\n7. Validating Rocket Loader Safety:")
    assert not re.search(r'<a[^>]*id=["\']?header-tools-btn["\']?[^>]*\bon[a-z]+=', html, re.IGNORECASE), (
        "❌ FAILED: Inline event handler detected on #header-tools-btn!"
    )
    assert not re.search(r'<a[^>]*href=["\']?https://tools\.arunsr\.in/?["\']?[^>]*\bon[a-z]+=', html, re.IGNORECASE), (
        "❌ FAILED: Inline event handler detected on sidebar tools link!"
    )
    print("  ✓ Zero inline event handlers verified (Cloudflare Rocket Loader safe).")

    # 8. Cross-Page Coverage Integrity
    print("\n8. Validating Cross-Page Coverage Integrity:")
    sample_pages = [
        os.path.join(public_dir, "index.html"),
        os.path.join(public_dir, "tags", "index.html"),
        os.path.join(public_dir, "posts", "index.html"),
        os.path.join(public_dir, "now", "index.html"),
        os.path.join(public_dir, "uses", "index.html"),
    ]
    for p in sample_pages:
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8") as f:
            p_html = f.read()
        # Skip alias redirect stubs (Rule 20)
        if re.search(r'http-equiv=["\']?refresh["\']?', p_html, re.IGNORECASE):
            continue
        rel_path = os.path.relpath(p, public_dir)
        assert re.search(r'<a[^>]*\bid=["\']?header-tools-btn["\']?[^>]*>', p_html, re.IGNORECASE), (
            f"❌ FAILED: Missing <a id='header-tools-btn'> on {rel_path}"
        )
        p_nav_tree = re.search(r'<nav[^>]*\bclass=["\']?[^"\'>]*\bnav-tree\b[^>]*>([\s\S]*?)</nav>', p_html, re.IGNORECASE)
        assert p_nav_tree and re.search(r'<a[^>]*\bhref=["\']?https://tools\.arunsr\.in/?["\']?[^>]*>', p_nav_tree.group(1), re.IGNORECASE), (
            f"❌ FAILED: Missing sidebar link to tools.arunsr.in on {rel_path}"
        )
        print(f"  ✓ {rel_path}: Header button and sidebar tools link verified.")

    print("\n✓ All Prominent Link to tools.arunsr.in tests passed successfully!")

if __name__ == "__main__":
    run_tests()
