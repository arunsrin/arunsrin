#!/usr/bin/env python3
"""
Automated Test Suite for Dark Mode Code Blocks with Dracula Theme
Validates class-based Chroma syntax highlighting, Dracula dark mode styling,
inline code formatting, and verifies zero inline background color regressions across generated HTML.
"""

import glob
import os
import re
import sys

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
    config_path = os.path.join(root_dir, "hugo.toml")
    head_path = os.path.join(root_dir, "layouts", "partials", "head.html")
    css_path = os.path.join(root_dir, "home", "css", "extra.css")
    spec_path = os.path.join(root_dir, "docs", "specs", "fix-dark-mode-code-blocks.md")

    print("=== Dark Mode Code Blocks & Dracula Theme Test Suite ===")

    # 1. Spec existence check
    print("\n1. Auditing Feature Specification:")
    if not os.path.exists(spec_path):
        print(f"  ✗ Spec file not found at {spec_path}")
        sys.exit(1)
    print("  ✓ Living specification exists at docs/specs/fix-dark-mode-code-blocks.md")

    # 2. Hugo Configuration Audit
    print("\n2. Auditing Hugo Chroma Configuration (hugo.toml):")
    if not os.path.exists(config_path):
        print(f"  ✗ Configuration file not found at {config_path}")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        config_content = f.read()

    if not re.search(r'noClasses\s*=\s*false', config_content):
        print("  ✗ hugo.toml missing 'noClasses = false' under [markup.highlight]")
        sys.exit(1)
    print("  ✓ 'noClasses = false' correctly configured for class-based Chroma highlighting")

    # 3. CSS Tokens & Dracula Palette Validation
    print("\n3. Auditing CSS Styling & Dracula Theme Tokens:")
    with open(head_path, "r", encoding="utf-8") as f:
        head_content = f.read()

    # Dark mode token: --code-bg: #282a36
    if not re.search(r'\[data-theme=["\']?dark["\']?\][^}]*--code-bg:\s*#282a36', head_content):
        print("  ✗ head.html [data-theme='dark'] missing '--code-bg: #282a36;'")
        sys.exit(1)
    print("  ✓ Dark mode --code-bg token configured to Dracula canvas (#282a36)")

    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    # Verify inline code styling
    if ":not(pre) > code" not in css_content:
        print("  ✗ extra.css missing inline code styling (:not(pre) > code)")
        sys.exit(1)
    print("  ✓ Inline code snippet styling (:not(pre) > code) verified")

    # Verify light mode .chroma
    if ".chroma" not in css_content:
        print("  ✗ extra.css missing .chroma styles")
        sys.exit(1)
    print("  ✓ Light mode .chroma styles verified")

    # Verify dark mode Dracula tokens in extra.css
    dracula_tokens = {
        "keywords (pink #ff79c6)": r'\[data-theme=["\']?dark["\']?\]\s*\.chroma\s*[^}]*#ff79c6',
        "builtins/vars (cyan #8be9fd)": r'\[data-theme=["\']?dark["\']?\]\s*\.chroma\s*[^}]*#8be9fd',
        "functions (green #50fa7b)": r'\[data-theme=["\']?dark["\']?\]\s*\.chroma\s*[^}]*#50fa7b',
        "strings (yellow #f1fa8c)": r'\[data-theme=["\']?dark["\']?\]\s*\.chroma\s*[^}]*#f1fa8c',
        "numbers (purple #bd93f9)": r'\[data-theme=["\']?dark["\']?\]\s*\.chroma\s*[^}]*#bd93f9',
        "comments (muted #6272a4)": r'\[data-theme=["\']?dark["\']?\]\s*\.chroma\s*[^}]*#6272a4',
        "base text (#f8f8f2)": r'\[data-theme=["\']?dark["\']?\]\s*\.chroma\s*\{[^}]*color:\s*#f8f8f2',
    }

    for token_name, pattern in dracula_tokens.items():
        if not re.search(pattern, css_content):
            print(f"  ✗ extra.css missing Dracula token for {token_name}")
            sys.exit(1)
        print(f"  ✓ Dracula {token_name} verified")

    # 4. Generated HTML Audit in public/
    print("\n4. Auditing Generated HTML in public/:")
    html_files = glob.glob(os.path.join(public_dir, "**", "*.html"), recursive=True)
    real_pages = []
    for hf in html_files:
        try:
            with open(hf, "r", encoding="utf-8") as f:
                content = f.read()
            if not is_redirect_stub(content):
                real_pages.append((hf, content))
        except Exception:
            continue

    print(f"  ✓ Examined {len(real_pages)} real HTML pages in public/")

    # Find pages with code blocks (Rule 14: accommodates optional quotes from minified HTML)
    pages_with_code_blocks = [
        (hf, content) for hf, content in real_pages if re.search(r'<pre[^>]*class=["\']?chroma["\'\s>]', content)
    ]
    if not pages_with_code_blocks:
        print("  ✗ Zero generated pages contained class-based Chroma code blocks")
        sys.exit(1)

    print(f"  ✓ Found {len(pages_with_code_blocks)} pages containing class-based Chroma code blocks")

    # 5. Anti-Regression & Negative Testing
    print("\n5. Auditing Anti-Regression & Zero Inline Background Overrides:")
    # Verify that NO <pre> in real pages has inline style="background-color: #f7f7f7" or similar
    bad_inline_pres = []
    for hf, content in real_pages:
        # Check for pre tags with hardcoded light background style
        matches = re.findall(r'<pre[^>]*style=["\'][^"\']*background-color:\s*#(?:f7f7f7|fff|ffffff)[^"\']*["\']', content, re.IGNORECASE)
        if matches:
            bad_inline_pres.append((hf, matches))

    if bad_inline_pres:
        print(f"  ✗ Detected {len(bad_inline_pres)} pages with hardcoded inline light backgrounds on <pre>:")
        for hf, matches in bad_inline_pres[:3]:
            rel = os.path.relpath(hf, root_dir)
            print(f"    - {rel}: {matches[0]}")
        sys.exit(1)
    print("  ✓ Negative test: ZERO pages contain hardcoded light inline background-color on <pre>")

    # Verify fallback language blocks use .chroma class and line structure
    ansible_html = None
    for hf, content in real_pages:
        if "tech" in hf and "ansible" in hf:
            ansible_html = content
            break

    if ansible_html:
        if not re.search(r'<div class=["\']?highlight["\']?>\s*<pre[^>]*class=["\']?[^"\']*chroma', ansible_html):
            print("  ✗ /tech/ansible/ missing expected <div class='highlight'><pre class='chroma'> structure")
            sys.exit(1)
        print("  ✓ Verified /tech/ansible/ has clean class-based Chroma structure")
        if 'data-lang="fallback"' in ansible_html:
            print("  ✓ Verified fallback language blocks rendered with clean class-based markup")

    print("\n=== All Dark Mode Code Blocks tests passed successfully! ===")


if __name__ == "__main__":
    run_tests()
