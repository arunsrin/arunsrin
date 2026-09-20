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

echo "=== All checks passed successfully! ==="
