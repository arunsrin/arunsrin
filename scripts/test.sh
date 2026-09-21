#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== 1. Running strict Hugo build ==="
hugo --gc --minify --panicOnWarning

echo "=== 2. Validating JSON indexes ==="
jq . public/index.json > /dev/null
echo "✓ public/index.json is valid"
jq . public/static/quotes.json > /dev/null
echo "✓ public/static/quotes.json is valid"

echo "=== 3. Checking internal links ==="
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi
"$PYTHON_CMD" "$SCRIPT_DIR/check_links.py" "$ROOT_DIR/public"

echo "=== 4. Running JavaScript & Cloudflare safety tests ==="
node "$SCRIPT_DIR/test_js.js"

echo "=== 5. Validating Related Notes & Mentions ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_related_notes.py"

echo "=== 6. Validating Search Relevance & Scoring ==="
node "$SCRIPT_DIR/test_search.js"

echo "=== 7. Validating Tech Folder Animated Emojis ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_tech_emojis.py"

echo "=== 8. Validating Homepage Cards Consistency ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_homepage_cards.py"

echo "=== 9. Validating Mobile Sidebar & Overlay Stacking ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_mobile_sidebar.py"

echo "=== 10. Validating GitHub CI Parity & Test Discovery ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_ci_parity.py"

echo "=== 11. Validating Tag Taxonomy Regression ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_tags.py"

echo "=== 12. Validating Sitemap & Recently Tended Stream ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_sitemap_and_recent.py"

echo "=== 13. Validating Title Bar & Sidebar UX ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_title_sidebar_ux.py"

echo "=== 14. Validating ASCII Banner & HTML Source Easter Egg ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_ascii_banner.py"

echo "=== 15. Validating Chronological Posts & Dispatches Space ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_posts.py"

echo "=== 16. Validating Fill-Paragraph Prose Linter ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_fill_paragraph.py"

echo "=== 17. Validating /now & /uses Pages Scaffolding & Navigation ==="
"$PYTHON_CMD" "$SCRIPT_DIR/test_now_and_uses.py"

echo "=== All checks passed successfully! ==="



