#!/usr/bin/env python3
"""Cross-platform internal link checker for arunsrin's notes."""
import os
import re
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def check_internal_links(public_dir: str = "public") -> bool:
    if not os.path.isdir(public_dir):
        print(f"Error: Directory '{public_dir}' does not exist. Run hugo first.", file=sys.stderr)
        return False

    broken = []
    checked = 0

    for root, _, files in os.walk(public_dir):
        for f in files:
            if f.endswith(".html"):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read()
                for href in re.findall(r'href=[\"\']?(/[^\"\'\s>#]+)', content):
                    checked += 1
                    clean_href = href.split("?")[0].rstrip("/")
                    if not clean_href:
                        continue
                    # Normalize target across Windows and Unix path separators
                    rel_target = clean_href.lstrip("/").replace("/", os.sep)
                    target = os.path.join(public_dir, rel_target)
                    if not (
                        os.path.exists(target)
                        or os.path.exists(target + ".html")
                        or os.path.exists(os.path.join(target, "index.html"))
                    ):
                        broken.append((path, href))

    print(f"Checked {checked} internal links.")
    if broken:
        print(f"FAILED: {len(broken)} broken internal links found!", file=sys.stderr)
        for src, dest in broken[:10]:
            print(f"  {src} -> {dest}", file=sys.stderr)
        return False

    print("✓ All internal links valid!")
    return True


if __name__ == "__main__":
    public_directory = sys.argv[1] if len(sys.argv) > 1 else "public"
    success = check_internal_links(public_directory)
    sys.exit(0 if success else 1)
