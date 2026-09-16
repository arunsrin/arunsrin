#!/usr/bin/env bash
set -euo pipefail

echo "=== 1. Running strict Hugo build ==="
hugo --gc --minify --panicOnWarning

echo "=== 2. Validating JSON indexes ==="
jq . public/index.json > /dev/null
echo "✓ public/index.json is valid"
jq . public/static/quotes.json > /dev/null
echo "✓ public/static/quotes.json is valid"

echo "=== 3. Checking internal links ==="
python3 -c "
import os, re, sys

public_dir = 'public'
broken = []
checked = 0

for root, _, files in os.walk(public_dir):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
            for href in re.findall(r'href=[\"\']?(/[^\"\'\s>#]+)', content):
                checked += 1
                clean_href = href.split('?')[0].rstrip('/')
                if not clean_href:
                    continue
                target = os.path.join(public_dir, clean_href.lstrip('/'))
                if not (os.path.exists(target) or os.path.exists(target + '.html') or os.path.exists(os.path.join(target, 'index.html'))):
                    broken.append((path, href))

print(f'Checked {checked} internal links.')
if broken:
    print(f'FAILED: {len(broken)} broken internal links found!')
    for src, dest in broken[:10]:
        print(f'  {src} -> {dest}')
    sys.exit(1)
else:
    print('✓ All internal links valid!')
"

echo "=== All checks passed successfully! ==="
