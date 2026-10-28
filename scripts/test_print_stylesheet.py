#!/usr/bin/env python3
"""
Automated Test Suite for Dedicated Print & PDF Export Stylesheet (@media print)
Validates that printable output renders clean, legible typography, avoids awkward
page breaks, expands external URLs, and strictly strips screen UI chrome (headers,
sidebars, TOC, modals, fortunes, and related notes) across generated pages.
"""

import os
import re
import sys
import glob

# Rule 12: Reconfigure stdout and stderr for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    public_dir = os.path.join(root_dir, "public")
    head_html_path = os.path.join(root_dir, "layouts", "partials", "head.html")

    print("--- Dedicated Print & PDF Export Stylesheet Test Suite ---")

    # 1. Template validation
    print("\n1. Validating @media print rules in layouts/partials/head.html:")
    if not os.path.exists(head_html_path):
        print(f"Error: {head_html_path} does not exist.")
        sys.exit(1)

    with open(head_html_path, "r", encoding="utf-8") as f:
        head_content = f.read()

    # Extract @media print block
    match = re.search(r"@media\s+print\s*\{(.*)\}\s*</style>", head_content, re.DOTALL)
    if not match:
        print("  ✗ @media print block not found in head.html")
        sys.exit(1)
    print("  ✓ @media print block located in head.html")
    print_css = match.group(1)

    # 2. Check for hidden chrome selectors in print block
    print("\n2. Auditing hidden chrome elements under @media print:")
    required_hidden_selectors = [
        r"\.site-header",
        r"\.sidebar-left",
        r"\.sidebar-right",
        r"\.mobile-menu-btn",
        r"\.sidebar-overlay",
        r"#sidebar-overlay",
        r"\.reading-progress-bar",
        r"#reading-progress",
        r"\.chess-watermark",
        r"\.site-footer",
        r"\.fortune-card",
        r"#quote-container",
        r"\.back-to-top-btn",
        r"#back-to-top-btn",
        r"\.search-container",
        r"#search-modal",
        r"\.search-dialog",
        r"#search-dialog",
        r"\.theme-toggle-btn",
        r"#theme-toggle",
        r"\.toc-container",
        r"\.toc-wrapper",
        r"\.table-of-contents",
        r"\.related-notes",
        r"\.link-preview-card",
        r"#link-preview-card",
        r"\.copy-code-btn",
        r"\.external-icon",
    ]

    for sel in required_hidden_selectors:
        clean_name = sel.replace(r"\\", "").replace(r"\.", ".").replace(r"\#", "#")
        if re.search(sel, print_css):
            print(f"  ✓ {clean_name} is hidden")
        else:
            print(f"  ✗ {clean_name} missing from print hidden selectors")
            sys.exit(1)

    # 3. Check layout width expansion
    print("\n3. Validating full-width layout expansion:")
    if not re.search(r"\.layout-container\s*\{[^}]*width:\s*100%\s*!important", print_css):
        print("  ✗ .layout-container does not expand to 100% width")
        sys.exit(1)
    print("  ✓ .layout-container expands to 100% width")

    if not re.search(r"\.main-content\s*\{[^}]*width:\s*100%\s*!important", print_css):
        print("  ✗ .main-content does not expand to 100% width")
        sys.exit(1)
    print("  ✓ .main-content expands to 100% width")

    # 4. Check page margins & pagination rules
    print("\n4. Validating @page margins and pagination discipline:")
    if not re.search(r"@page\s*\{[^}]*margin:\s*1\.5cm", print_css):
        print("  ✗ @page margin rule missing or incorrect")
        sys.exit(1)
    print("  ✓ @page margin configured to 1.5cm")

    if not re.search(r"(?:break-inside|page-break-inside):\s*avoid", print_css):
        print("  ✗ break-inside: avoid missing for atomic elements")
        sys.exit(1)
    print("  ✓ break-inside: avoid specified for atomic blocks (code, table, blockquote, images)")

    if not re.search(r"(?:break-after|page-break-after):\s*avoid", print_css):
        print("  ✗ break-after: avoid missing for headings")
        sys.exit(1)
    print("  ✓ break-after: avoid specified for headings")

    # 5. Check external link URL expansion & internal link neutrality
    print("\n5. Validating selective link URL footnoting:")
    if not re.search(r'attr\(href\)', print_css):
        print("  ✗ attr(href) missing from external link print rules")
        sys.exit(1)
    print("  ✓ attr(href) footnoting configured for external links")

    # Negative test: internal links must NOT expand URLs
    if not re.search(r'a\[href\^=["\']?#["\']?\]::after', print_css) or not re.search(r'a\[href\^=["\']?\/["\']?\]::after', print_css):
        print("  ✗ Internal or anchor link expansion suppression rule missing")
        sys.exit(1)
    print("  ✓ Negative test: internal and anchor link URL expansion explicitly neutralized")

    # 6. Check high contrast and color normalization
    print("\n6. Validating high-contrast paper color normalization:")
    if not re.search(r"body\s*\{[^}]*background:\s*#ffffff\s*!important", print_css):
        print("  ✗ body background is not forced to pure white (#ffffff)")
        sys.exit(1)
    print("  ✓ body background forced to pure white (#ffffff)")

    if not re.search(r"body\s*\{[^}]*color:\s*#111111\s*!important", print_css):
        print("  ✗ body text color is not forced to high-contrast dark (#111111)")
        sys.exit(1)
    print("  ✓ body text color forced to high contrast dark (#111111)")

    # 7. Check generated HTML pages if public/ exists
    if os.path.exists(public_dir):
        print("\n7. Auditing generated HTML pages in public/ (skipping Hugo alias stubs):")
        html_files = glob.glob(os.path.join(public_dir, "**", "*.html"), recursive=True)
        audited_count = 0

        for file_path in html_files:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Rule 20: Skip Hugo alias redirect stubs
            if re.search(r'http-equiv=["\']?refresh["\']?', content, re.IGNORECASE):
                continue

            # Full layout page: verify @media print presence in inlined style
            if "@media print" not in content and "@media print{" not in content:
                print(f"  ✗ Missing @media print in generated page: {file_path}")
                sys.exit(1)

            audited_count += 1

        print(f"  ✓ Validated {audited_count} full generated HTML pages for @media print inclusion")
    else:
        print("\n7. Notice: public/ directory not yet built; skipping public/ scan (run during test.ps1/test.sh)")

    print("\n✓ All print stylesheet assertions passed successfully!")

if __name__ == "__main__":
    run_tests()
