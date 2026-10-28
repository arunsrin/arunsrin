#!/usr/bin/env python3
"""
Automated Test Suite for Outdated Content Freshness Callout Banner
Validates that technical reference notes older than 2 years (>730 days) render
a polite, dynamic advisory banner in Hugo-generated HTML without affecting non-tech
sections or modifying the author's prose.
"""

import glob
import os
import re
import sys
import tempfile
import subprocess

# Rule 12: Reconfigure stdout and stderr for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def is_redirect_stub(html_content: str) -> bool:
    """Rule 20: Differentiate Hugo alias redirect stubs from real layout pages."""
    return bool(re.search(r'http-equiv=["\']?refresh["\']?', html_content, re.IGNORECASE))


def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    public_dir = os.path.join(root_dir, "public")
    partial_path = os.path.join(root_dir, "layouts", "partials", "freshness-banner.html")
    single_path = os.path.join(root_dir, "layouts", "_default", "single.html")
    css_path = os.path.join(root_dir, "home", "css", "extra.css")
    spec_path = os.path.join(root_dir, "docs", "specs", "tech-freshness-banner.md")

    print("=== Outdated Content Freshness Callout Banner Test Suite ===")

    # 1. Spec existence check
    print("\n1. Auditing Feature Specification:")
    if not os.path.exists(spec_path):
        print(f"  ✗ Spec file not found at {spec_path}")
        sys.exit(1)
    print("  ✓ Living specification exists at docs/specs/tech-freshness-banner.md")

    # 2. Template Partial Validation
    print("\n2. Validating Template Architecture:")
    if not os.path.exists(partial_path):
        print(f"  ✗ Partial template not found at {partial_path}")
        sys.exit(1)
    with open(partial_path, "r", encoding="utf-8") as f:
        partial_content = f.read()

    # Verify section scoping
    if 'eq .Section "tech"' not in partial_content:
        print("  ✗ freshness-banner.html missing tech section guard ('eq .Section \"tech\"')")
        sys.exit(1)
    print("  ✓ Tech section guard verified in partial")

    # Verify opt-out handling
    if "freshness_warning" not in partial_content:
        print("  ✗ freshness-banner.html missing freshness_warning opt-out parameter check")
        sys.exit(1)
    print("  ✓ Frontmatter opt-out parameter ('freshness_warning') verified")

    # Verify age threshold calculation (730 days = 63072000 seconds)
    if "63072000" not in partial_content and "730" not in partial_content:
        print("  ✗ Age threshold (730 days / 63072000s) not found in partial template")
        sys.exit(1)
    print("  ✓ 2-year age threshold (63072000 seconds) verified")

    # Verify single.html includes the partial
    with open(single_path, "r", encoding="utf-8") as f:
        single_content = f.read()
    if 'partial "freshness-banner.html"' not in single_content:
        print("  ✗ single.html does not include 'freshness-banner.html'")
        sys.exit(1)
    print("  ✓ single.html correctly includes freshness-banner partial")

    # 3. CSS Styling Validation
    print("\n3. Auditing CSS Styling & Theme Harmony:")
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    if ".freshness-banner" not in css_content:
        print("  ✗ .freshness-banner rule missing from home/css/extra.css")
        sys.exit(1)
    if '[data-theme="dark"] .freshness-banner' not in css_content:
        print("  ✗ Dark mode styling missing for .freshness-banner")
        sys.exit(1)
    print("  ✓ .freshness-banner and dark mode overrides verified in extra.css")

    # 4. Public Generated HTML Assertions
    print("\n4. Auditing Generated HTML in public/:")
    if not os.path.exists(public_dir):
        print("  ✗ public/ directory not found. Please build hugo first.")
        sys.exit(1)

    # 4.1 Positive Assertion: Older tech note (openssl)
    openssl_html = os.path.join(public_dir, "tech", "openssl", "index.html")
    if not os.path.exists(openssl_html):
        print(f"  ✗ {openssl_html} not found")
        sys.exit(1)
    with open(openssl_html, "r", encoding="utf-8") as f:
        html = f.read()

    # Rule 14: Minified HTML quote-agnostic regex
    banner_match = re.search(r'class=["\']?freshness-banner["\'\s>]', html)
    if not banner_match:
        print("  ✗ Freshness banner element not found in /tech/openssl/index.html")
        sys.exit(1)
    print("  ✓ Freshness banner successfully rendered on /tech/openssl/")

    # Semantic attributes
    if not re.search(r'role=["\']?note["\'\s>]', html):
        print("  ✗ role='note' attribute missing from freshness banner")
        sys.exit(1)
    if "Content freshness advisory" not in html:
        print("  ✗ aria-label='Content freshness advisory' missing from freshness banner")
        sys.exit(1)
    print("  ✓ Accessibility attributes (role='note', aria-label) confirmed")

    # Dynamic elapsed duration check (e.g., 'over 2 years ago (Jan 2024)')
    time_match = re.search(r'over\s+(\d+)\s+years\s+ago\s+\(([A-Za-z]{3}\s+\d{4})\)', html)
    if not time_match:
        print("  ✗ Dynamic elapsed time copy not found or misformatted in banner")
        sys.exit(1)
    years_elapsed, formatted_date = time_match.groups()
    print(f"  ✓ Dynamic time formatted correctly: 'over {years_elapsed} years ago ({formatted_date})'")

    # 4.2 Negative Assertion: Recent tech note (< 730 days old)
    docker_html = os.path.join(public_dir, "tech", "docker", "index.html")
    if os.path.exists(docker_html):
        with open(docker_html, "r", encoding="utf-8") as f:
            d_html = f.read()
        if re.search(r'class=["\']?freshness-banner["\'\s>]', d_html):
            print("  ✗ Freshness banner spuriously rendered on recent note /tech/docker/")
            sys.exit(1)
        print("  ✓ Freshness banner correctly suppressed on recent note /tech/docker/ (< 730 days)")

    # 4.3 Negative Assertion: Non-tech sections (books, games, posts, root pages)
    print("\n5. Auditing Section Isolation (Anti-Spurious Protection):")
    non_tech_patterns = [
        os.path.join(public_dir, "books", "*", "index.html"),
        os.path.join(public_dir, "games", "*", "index.html"),
        os.path.join(public_dir, "posts", "*", "index.html"),
        os.path.join(public_dir, "other-interests", "*", "index.html"),
        os.path.join(public_dir, "about", "index.html"),
        os.path.join(public_dir, "uses", "index.html"),
        os.path.join(public_dir, "now", "index.html"),
    ]

    checked_pages = 0
    for pattern in non_tech_patterns:
        for file_path in glob.glob(pattern):
            if not os.path.isfile(file_path):
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if is_redirect_stub(content):
                continue
            if re.search(r'class=["\']?freshness-banner["\'\s>]', content):
                print(f"  ✗ Freshness banner spuriously leaked into non-tech page: {file_path}")
                sys.exit(1)
            checked_pages += 1

    print(f"  ✓ Verified {checked_pages} non-tech pages: 0 spurious freshness banner leaks detected")

    # 4.4 Opt-Out Verification via Synthetic Note Build
    print("\n6. Verifying Opt-Out Frontmatter ('freshness_warning: false'):")
    opt_out_file = os.path.join(root_dir, "home", "tech", "_test_opt_out_freshness.md")
    try:
        with open(opt_out_file, "w", encoding="utf-8") as f:
            f.write(
                "---\n"
                'title: "Test Opt Out Freshness"\n'
                "lastmod: 2020-01-01\n"
                "freshness_warning: false\n"
                "---\n"
                "# Test Content\n"
                "Testing opt-out.\n"
            )

        # Run fast build in quiet mode
        res = subprocess.run(
            ["hugo", "--quiet"],
            cwd=root_dir,
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            print(f"  ✗ Hugo build failed during opt-out test: {res.stderr}")
            sys.exit(1)

        test_html_path = os.path.join(public_dir, "tech", "_test_opt_out_freshness", "index.html")
        if not os.path.exists(test_html_path):
            print(f"  ✗ Generated test page not found: {test_html_path}")
            sys.exit(1)

        with open(test_html_path, "r", encoding="utf-8") as f:
            test_html = f.read()

        if re.search(r'class=["\']?freshness-banner["\'\s>]', test_html):
            print("  ✗ Freshness banner rendered despite 'freshness_warning: false'")
            sys.exit(1)
        print("  ✓ Freshness banner successfully suppressed when 'freshness_warning: false'")

    finally:
        # Clean up temporary test file
        if os.path.exists(opt_out_file):
            os.remove(opt_out_file)
        # Rebuild site to restore clean public/ directory
        subprocess.run(["hugo", "--quiet"], cwd=root_dir, capture_output=True)

    print("\n✓ ALL FRESHNESS BANNER TESTS PASSED CLEANLY (100% SUCCESS)")


if __name__ == "__main__":
    run_tests()
