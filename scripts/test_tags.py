#!/usr/bin/env python3
"""
Automated Regression Test Suite for Consistent Tag Taxonomy Assimilation.
Validates:
1. Every tag present has count >= 2 (zero singletons).
2. Every tag present has count <= 10 (zero umbrella tags).
3. Exactly 32 unique tags matching target taxonomy.
4. Zero prohibited directory/hierarchy/meta tags ('books', 'tech', 'games', 'research', 'intro', 'non-fiction', 'about', 'home', etc.).
5. Clean lowercase alphanumeric tag format matching r'^[a-z0-9]+(-[a-z0-9]+)*$'.
6. Negative assertions: explicitly checks for previously troublesome singletons.
7. Meta/root pages (_index.md, about.md) have zero tags.
"""

import os
import re
import sys

# Enforce UTF-8 stdout/stderr reconfiguration across Windows and Linux terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

TARGET_TAXONOMY = {
    "science": 10,
    "fiction": 9,
    "devops": 8,
    "sysadmin": 7,
    "programming": 6,
    "philosophy": 5,
    "tools": 5,
    "history": 4,
    "linux": 4,
    "media": 4,
    "people": 4,
    "psychology": 4,
    "security": 4,
    "literary": 3,
    "math": 3,
    "medicine": 3,
    "monitoring": 3,
    "politics": 3,
    "productivity": 3,
    "writing": 3,
    "climate": 2,
    "containers": 2,
    "data": 2,
    "databases": 2,
    "environment": 2,
    "fantasy": 2,
    "finance": 2,
    "gaming": 2,
    "nabokov": 2,
    "reading": 2,
    "sci-fi": 2,
    "windows": 2,
}

PROHIBITED_TAGS = {
    "books",
    "tech",
    "games",
    "research",
    "intro",
    "non-fiction",
    "about",
    "home",
    "index",
    "profile",
    "hub",
    "reference",
}

TROUBLESOME_SINGLETONS = [
    # Tool names
    "docker",
    "k8s",
    "kubernetes",
    "ansible",
    "git",
    "kafka",
    "prometheus",
    "grafana",
    "openssl",
    "go",
    "java",
    "python",
    "powershell",
    "aws",
    "elastic",
    # Mapped singletons
    "historical",
    "biography",
    "cryptocurrencies",
    "economics",
    "cryptography",
    "privacy",
    "ethics",
    "logic",
    "stoicism",
    "neuroscience",
    "evolution",
    "astronomy",
    "literature",
    "language",
    "business",
    "automation",
    "cloud",
    "development",
    "coding",
    "emacs",
    "editors",
    "browsers",
    "ai",
    # Game genre / section singletons
    "action",
    "adventure",
    "fighting",
    "shooter",
    "fps",
    "platformer",
    "puzzle",
    "rpg",
    "strategy",
    "cyberpunk",
    "story",
    "interactive",
    "console",
    "classics",
    "mystery",
    "myth",
    "movies",
    "tv",
    "networking",
    "open-source",
    "os",
    "linguistics",
]

# Complete canonical mapping for each file in home/
CANONICAL_FILE_TAGS = {
    # Root & Meta pages
    "_index.md": [],
    "about.md": [],

    # Books Root & Intro
    os.path.join("books", "_index.md"): ["reading"],
    os.path.join("books", "intro", "_index.md"): [],
    os.path.join("books", "intro", "accounting.md"): ["finance"],
    os.path.join("books", "intro", "advertising.md"): ["media"],
    os.path.join("books", "intro", "alexander.md"): ["history"],
    os.path.join("books", "intro", "anaesthesia.md"): ["medicine", "science"],

    # Books Fiction
    os.path.join("books", "fiction", "_index.md"): ["fiction"],
    os.path.join("books", "fiction", "classics", "_index.md"): ["fiction"],
    os.path.join("books", "fiction", "fantasy", "_index.md"): ["fiction", "fantasy"],
    os.path.join("books", "fiction", "historical", "_index.md"): ["fiction", "history"],
    os.path.join("books", "fiction", "literary", "_index.md"): ["fiction", "literary"],
    os.path.join("books", "fiction", "literary", "despair.md"): ["fiction", "literary", "nabokov"],
    os.path.join("books", "fiction", "literary", "pale-fire.md"): ["fiction", "literary", "nabokov"],
    os.path.join("books", "fiction", "mystery", "_index.md"): ["fiction"],
    os.path.join("books", "fiction", "sci-fi", "_index.md"): ["fiction", "sci-fi"],

    # Books Non-Fiction
    os.path.join("books", "non-fiction", "_index.md"): [],
    os.path.join("books", "non-fiction", "history", "_index.md"): ["history"],
    os.path.join("books", "non-fiction", "history", "hate-inc.md"): ["history", "media", "politics"],
    os.path.join("books", "non-fiction", "math", "_index.md"): ["math"],
    os.path.join("books", "non-fiction", "math", "good-math.md"): ["math"],
    os.path.join("books", "non-fiction", "math", "the-art-of-the-infinite.md"): ["math"],
    os.path.join("books", "non-fiction", "philosophy", "_index.md"): ["philosophy"],
    os.path.join("books", "non-fiction", "philosophy", "think-like-a-stoic.md"): ["philosophy"],
    os.path.join("books", "non-fiction", "psychology", "_index.md"): ["psychology"],
    os.path.join("books", "non-fiction", "psychology", "flow.md"): ["psychology", "productivity"],
    os.path.join("books", "non-fiction", "psychology", "happiness.md"): ["psychology", "philosophy"],
    os.path.join("books", "non-fiction", "psychology", "we-are-our-brains.md"): ["psychology"],
    os.path.join("books", "non-fiction", "science", "_index.md"): ["science"],
    os.path.join("books", "non-fiction", "science", "crypto101.md"): ["science", "security"],
    os.path.join("books", "non-fiction", "science", "immune.md"): ["science", "medicine"],
    os.path.join("books", "non-fiction", "science", "thinking-climate-change.md"): ["science", "climate", "environment"],
    os.path.join("books", "non-fiction", "writing", "_index.md"): ["writing"],
    os.path.join("books", "non-fiction", "writing", "eats-shoots-leaves.md"): ["writing"],
    os.path.join("books", "non-fiction", "writing", "how-to-read-a-book.md"): ["writing", "reading"],

    # Games
    os.path.join("games", "_index.md"): ["gaming"],
    os.path.join("games", "action-adventure", "_index.md"): [],
    os.path.join("games", "fantasy-myth", "_index.md"): ["fantasy"],
    os.path.join("games", "fighting", "_index.md"): [],
    os.path.join("games", "fps", "_index.md"): [],
    os.path.join("games", "platform-puzzle", "_index.md"): [],
    os.path.join("games", "rpg-strategy", "_index.md"): [],
    os.path.join("games", "sci-fi-cyberpunk", "_index.md"): ["sci-fi"],
    os.path.join("games", "story-interactive", "_index.md"): [],
    os.path.join("games", "xbox.md"): ["gaming"],

    # Other Interests
    os.path.join("other-interests", "_index.md"): ["media"],
    os.path.join("other-interests", "media.md"): ["media"],
    os.path.join("other-interests", "people", "chomsky.md"): ["people", "politics"],
    os.path.join("other-interests", "people", "dawkins.md"): ["people", "science"],
    os.path.join("other-interests", "people", "sagan.md"): ["people", "science"],
    os.path.join("other-interests", "people", "stallman.md"): ["people"],
    os.path.join("other-interests", "research", "capitalism.md"): ["politics"],
    os.path.join("other-interests", "research", "climate-change.md"): ["science", "climate", "environment"],
    os.path.join("other-interests", "research", "covid-19.md"): ["science", "medicine"],
    os.path.join("other-interests", "research", "cryptocurrencies.md"): ["finance"],
    os.path.join("other-interests", "research", "philosophy.md"): ["philosophy"],
    os.path.join("other-interests", "research", "privacy-internet.md"): ["security"],
    os.path.join("other-interests", "research", "productivity.md"): ["productivity", "tools"],
    os.path.join("other-interests", "research", "scepticism.md"): ["science", "philosophy"],

    # Tech
    os.path.join("tech", "_index.md"): ["programming"],
    os.path.join("tech", "ai.md"): ["tools", "productivity"],
    os.path.join("tech", "ansible.md"): ["devops"],
    os.path.join("tech", "aws.md"): ["devops"],
    os.path.join("tech", "browsers.md"): ["tools"],
    os.path.join("tech", "databases.md"): ["databases", "data"],
    os.path.join("tech", "docker.md"): ["containers", "devops"],
    os.path.join("tech", "editors.md"): ["tools"],
    os.path.join("tech", "elastic.md"): ["monitoring", "databases"],
    os.path.join("tech", "git.md"): ["devops", "tools"],
    os.path.join("tech", "grafana.md"): ["monitoring", "devops"],
    os.path.join("tech", "k8s.md"): ["containers", "devops"],
    os.path.join("tech", "kafka.md"): ["data", "devops"],
    os.path.join("tech", "linux", "_index.md"): ["linux", "sysadmin"],
    os.path.join("tech", "linux", "learnings-and-notes.md"): ["linux", "sysadmin"],
    os.path.join("tech", "linux", "package-management.md"): ["linux", "sysadmin"],
    os.path.join("tech", "linux", "systemd.md"): ["linux", "sysadmin"],
    os.path.join("tech", "networking.md"): ["sysadmin"],
    os.path.join("tech", "openssl.md"): ["security"],
    os.path.join("tech", "programming", "_index.md"): ["programming"],
    os.path.join("tech", "programming", "go.md"): ["programming"],
    os.path.join("tech", "programming", "java.md"): ["programming"],
    os.path.join("tech", "programming", "powershell.md"): ["programming", "windows"],
    os.path.join("tech", "programming", "python.md"): ["programming"],
    os.path.join("tech", "prometheus.md"): ["monitoring", "devops"],
    os.path.join("tech", "security.md"): ["security", "sysadmin"],
    os.path.join("tech", "windows.md"): ["windows", "sysadmin"],
}

def parse_frontmatter_tags(file_path):
    with open(file_path, "r", encoding="utf-8") as fp:
        content = fp.read()
    m = re.match(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
    if not m:
        return []
    fm = m.group(1)
    # Check block tags:
    # tags:
    #   - tag1
    block_m = re.search(r"^tags:\s*\n((?:\s+-\s*.*\r?\n?)*)", fm, re.MULTILINE)
    if block_m and block_m.group(1).strip():
        tags = [
            re.sub(r"^\s*-\s*", "", line).strip().strip("'\"")
            for line in block_m.group(1).strip().splitlines()
            if line.strip()
        ]
        return tags
    # Check inline tags:
    # tags: [tag1, tag2]
    inline_m = re.search(r"^tags:\s*\[(.*?)\]", fm, re.MULTILINE)
    if inline_m:
        return [t.strip().strip("'\"") for t in inline_m.group(1).split(",") if t.strip()]
    return []

def assimilate_frontmatter_tags(home_dir):
    """
    Applies the canonical tag taxonomy strictly adhering to Rule 9 (Sacred Prose).
    Only YAML frontmatter tags block is modified; note body text is 100% preserved.
    """
    updated_files = 0
    for rel_path, canonical_tags in CANONICAL_FILE_TAGS.items():
        file_path = os.path.join(home_dir, rel_path)
        if not os.path.exists(file_path):
            continue
        with open(file_path, "r", encoding="utf-8", newline="") as fp:
            content = fp.read()

        m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", content, re.DOTALL)
        if not m:
            continue

        fm = m.group(1)
        body = m.group(2)

        # Parse fm lines
        fm_lines = fm.split("\n")
        new_fm_lines = []
        in_tags = False

        for line in fm_lines:
            if re.match(r"^tags:\s*(\[.*\])?$", line.strip()):
                in_tags = True
                continue
            if in_tags:
                if re.match(r"^\s+-\s+.*$", line):
                    continue
                else:
                    in_tags = False
            new_fm_lines.append(line)

        # Clean trailing blank lines in frontmatter
        while new_fm_lines and new_fm_lines[-1].strip() == "":
            new_fm_lines.pop()

        if canonical_tags:
            new_fm_lines.append("tags:")
            for tag in canonical_tags:
                new_fm_lines.append(f"  - {tag}")

        new_fm = "\n".join(new_fm_lines)
        new_content = f"---\n{new_fm}\n---\n{body}"

        if new_content != content:
            with open(file_path, "w", encoding="utf-8", newline="\n") as fp:
                fp.write(new_content)
            updated_files += 1

    return updated_files

def validate_tags(home_dir):
    print("--- Consistent Tag Taxonomy Regression Test Suite ---")
    all_files = []
    for root, _, files in os.walk(home_dir):
        for f in files:
            if f.endswith(".md"):
                all_files.append(os.path.join(root, f))

    print(f"1. Scanning {len(all_files)} markdown files in {home_dir}...")
    tag_counts = {}
    file_tags_map = {}
    format_pattern = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    format_errors = []
    prohibited_errors = []

    for file_path in all_files:
        rel_path = os.path.relpath(file_path, home_dir)
        tags = parse_frontmatter_tags(file_path)
        file_tags_map[rel_path] = tags

        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Tag format check
            if not format_pattern.match(tag):
                format_errors.append((rel_path, tag))

            # Prohibited tag check
            if tag.lower() in PROHIBITED_TAGS:
                prohibited_errors.append((rel_path, tag))

    # Assert clean tag format
    print(f"2. Validating tag format against r'^[a-z0-9]+(-[a-z0-9]+)*$'...")
    if format_errors:
        print(f"  ❌ FAILED: Found {len(format_errors)} invalid tag format(s):")
        for p, t in format_errors:
            print(f"     - {p}: '{t}'")
        sys.exit(1)
    print("  ✓ All tags adhere strictly to lowercase alphanumeric kebab-case.")

    # Assert no prohibited tags
    print(f"3. Validating absence of prohibited directory / hierarchy / meta tags...")
    if prohibited_errors:
        print(f"  ❌ FAILED: Found prohibited tags in {len(prohibited_errors)} instance(s):")
        for p, t in prohibited_errors:
            print(f"     - {p}: '{t}'")
        sys.exit(1)
    print("  ✓ Zero prohibited tags found ('books', 'tech', 'games', 'research', 'intro', 'non-fiction', 'about', 'home', etc.).")

    # Assert root and meta pages have zero tags
    print(f"4. Validating root and meta pages have zero orphan tags...")
    meta_pages = ["_index.md", "about.md"]
    for mp in meta_pages:
        tags = file_tags_map.get(mp, [])
        assert len(tags) == 0, f"Root/meta page '{mp}' must have zero tags, but has {tags}!"
    print("  ✓ Root and meta pages (_index.md, about.md) have zero tags.")

    # Assert zero singletons (count >= 2)
    print(f"5. Validating Min Frequency Guardrail (count >= 2, zero singletons)...")
    singletons = [tag for tag, count in tag_counts.items() if count < 2]
    if singletons:
        print(f"  ❌ FAILED: Found {len(singletons)} singleton tag(s) (count < 2):")
        for s in singletons:
            print(f"     - '{s}': count={tag_counts[s]}")
        sys.exit(1)
    print(f"  ✓ Zero singletons: every tag appears on at least 2 pages.")

    # Assert zero umbrella tags (count <= 10)
    print(f"6. Validating Max Frequency Guardrail (count <= 10, zero umbrella tags)...")
    umbrellas = [tag for tag, count in tag_counts.items() if count > 10]
    if umbrellas:
        print(f"  ❌ FAILED: Found {len(umbrellas)} umbrella tag(s) (count > 10):")
        for u in umbrellas:
            print(f"     - '{u}': count={tag_counts[u]}")
        sys.exit(1)
    print(f"  ✓ Zero umbrella tags: every tag appears on at most 10 pages.")

    # Negative assertions: explicitly check for previously troublesome singletons
    print(f"7. Executing negative assertions against troublesome singletons...")
    troublesome_found = []
    for tag in TROUBLESOME_SINGLETONS:
        if tag in tag_counts:
            troublesome_found.append((tag, tag_counts[tag]))
    if troublesome_found:
        print(f"  ❌ FAILED: Found troublesome singletons that should have been pruned/assimilated:")
        for t, c in troublesome_found:
            print(f"     - '{t}': count={c}")
        sys.exit(1)
    print(f"  ✓ All {len(TROUBLESOME_SINGLETONS)} troublesome singletons are successfully eliminated.")

    # Assert exact 32 unique tags matching target taxonomy
    print(f"8. Validating Exact 32 Tag Taxonomy & Target Frequencies...")
    if len(tag_counts) != 32:
        print(f"  ❌ FAILED: Expected exactly 32 unique tags, found {len(tag_counts)}: {sorted(tag_counts.keys())}")
        sys.exit(1)

    taxonomy_mismatches = []
    for tag, expected_count in sorted(TARGET_TAXONOMY.items()):
        actual_count = tag_counts.get(tag, 0)
        if actual_count != expected_count:
            taxonomy_mismatches.append((tag, expected_count, actual_count))

    if taxonomy_mismatches:
        print(f"  ❌ FAILED: Tag count mismatches with target taxonomy:")
        for t, exp, act in taxonomy_mismatches:
            print(f"     - '{t}': expected={exp}, actual={act}")
        sys.exit(1)
    print(f"  ✓ Target taxonomy verified: EXACTLY 32 unique tags matching target distribution.")

    print("\n✓ ALL 8 TAG TAXONOMY REGRESSION TESTS PASSED SUCCESSFULLY!")

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    home_dir = os.path.join(root_dir, "home")

    if "--assimilate" in sys.argv or "--fix" in sys.argv:
        print("Assimilating frontmatter tags across home/...")
        updated = assimilate_frontmatter_tags(home_dir)
        print(f"Updated frontmatter tags in {updated} files.")

    validate_tags(home_dir)

if __name__ == "__main__":
    main()
