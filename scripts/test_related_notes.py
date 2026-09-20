#!/usr/bin/env python3
"""
Regression test suite for Related Notes & Mentions.
Validates:
1. 100% coverage across regular content notes (excluding section landing index pages).
2. Accuracy of incoming mentions (backlinks) and badges.
3. Accuracy of outgoing references and badges.
4. Accuracy of tag-based topic recommendations.
5. Anti-spurious match protection (e.g. COVID-19/Capitalism on Productivity).
6. Clean snippet formatting (zero unparsed icon markers or raw markdown hashes).
7. Content-bearing section pages coverage (e.g. games/fps, books/fiction/sci-fi).
"""

import os
import re
import sys

def run_tests():
    public_dir = "public"
    content_dir = "home"
    if not os.path.exists(public_dir):
        print(f"Error: {public_dir} does not exist. Run 'hugo' first.")
        sys.exit(1)

    print("--- Related Notes & Mentions Test Suite ---")

    # 1. Discover all regular content notes
    single_notes = []
    for root, _, files in os.walk(content_dir):
        for f in files:
            if f.endswith(".md") and not f.startswith("_index"):
                rel = os.path.relpath(os.path.join(root, f), content_dir)
                single_notes.append(rel)

    print(f"1. Verifying Related Notes Coverage across {len(single_notes)} notes:")
    missing = []
    card_counts = []
    for note in single_notes:
        html_rel = note[:-3] + "/index.html"
        html_path = os.path.join(public_dir, html_rel)
        if not os.path.exists(html_path):
            missing.append((note, "File not generated in public/"))
            continue
        with open(html_path, "r", encoding="utf-8") as fp:
            html = fp.read()
        if not re.search(r'class=[\"\']?related-notes-section[\"\']?', html):
            missing.append((note, "Missing related-notes-section"))
        else:
            cards = re.findall(r'class=[\"\']?related-note-card[\"\']?', html)
            card_counts.append(len(cards))

    if missing:
        print(f"  ❌ FAILED: {len(missing)} notes missing related notes section:")
        for note, reason in missing:
            print(f"     - {note}: {reason}")
        sys.exit(1)
    else:
        avg_cards = sum(card_counts) / len(card_counts) if card_counts else 0
        print(f"  ✓ 100% coverage ({len(single_notes)}/{len(single_notes)} notes populated, avg {avg_cards:.1f} cards/page)")

    # Helper to load HTML
    def load_html(rel_path):
        p = os.path.join(public_dir, rel_path, "index.html")
        if not os.path.exists(p):
            print(f"  ❌ FAILED: Expected generated page {p} not found.")
            sys.exit(1)
        with open(p, "r", encoding="utf-8") as fp:
            return fp.read()

    # Helper to extract related section
    def get_related_section(html):
        m = re.search(r'<section class=[\"\']?related-notes-section[\"\']?.*?</section>', html, re.DOTALL)
        return m.group(0) if m else ""

    # 2. Mentions (Backlinks) Validation
    print("2. Validating Incoming Mentions (Backlinks):")
    despair_html = load_html("books/fiction/literary/despair")
    despair_rel = get_related_section(despair_html)
    assert "related-badge-mention" in despair_rel, "Despair missing related-badge-mention"
    assert "/about/" in despair_rel, "Despair missing incoming link from About"
    print("  ✓ Despair note features 'Mentioned In' card from About")

    security_html = load_html("tech/security")
    security_rel = get_related_section(security_html)
    assert "/tech/openssl/" in security_rel, "Security missing incoming mention from OpenSSL"
    assert "related-badge-mention" in security_rel, "Security missing related-badge-mention"
    print("  ✓ Security note features 'Mentioned In' card from OpenSSL")

    # 3. Direct References Validation
    print("3. Validating Outgoing References:")
    docker_html = load_html("tech/docker")
    docker_rel = get_related_section(docker_html)
    assert "related-badge-reference" in docker_rel, "Docker missing related-badge-reference"
    assert "/tech/k8s/" in docker_rel, "Docker missing reference to Kubernetes"
    print("  ✓ Docker note features 'Referenced' card to Kubernetes")

    prod_html = load_html("other-interests/research/productivity")
    prod_rel = get_related_section(prod_html)
    assert "/tech/editors/" in prod_rel, "Productivity missing reference to Editors"
    assert "related-badge-reference" in prod_rel, "Productivity missing related-badge-reference"
    print("  ✓ Productivity note features 'Referenced' card to Editors")

    # 4. Topic Tags Validation
    print("4. Validating Topic Similarity:")
    prom_html = load_html("tech/prometheus")
    prom_rel = get_related_section(prom_html)
    assert "/tech/grafana/" in prom_rel, "Prometheus missing related note to Grafana"
    print("  ✓ Prometheus note connects to Grafana via monitoring/devops")

    flow_html = load_html("books/non-fiction/psychology/flow")
    flow_rel = get_related_section(flow_html)
    assert "/other-interests/research/productivity/" in flow_rel, "Flow missing related note to Productivity"
    print("  ✓ Flow note connects to Productivity via #productivity")

    # 5. Anti-Spurious Match Protection
    print("5. Validating Anti-Spurious Topic Isolation:")
    for forbidden in ["COVID-19 References", "Capitalism", "Climate Change"]:
        assert forbidden not in prod_rel, f"Spurious note '{forbidden}' found in Productivity related notes!"
    print("  ✓ Productivity page free of spurious notes (COVID-19, Capitalism, Climate Change)")

    assert "Accounting" not in despair_rel, "Spurious note 'Accounting' found in Despair related notes!"
    print("  ✓ Despair page free of spurious notes (Accounting)")

    # 6. Clean Snippet Formatting Check
    print("6. Validating Snippet Cleanliness across all generated HTML:")
    snippet_errors = []
    for root, _, files in os.walk(public_dir):
        for f in files:
            if f == "index.html":
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read()
                snippets = re.findall(r'class=[\"\']?related-note-snippet[\"\']?>&ldquo;(.*?)&rdquo;</p>', content)
                for s in snippets:
                    if re.search(r':(material|simple|fontawesome|octicons)-[a-z0-9_-]+:', s):
                        snippet_errors.append((path, "Unparsed icon syntax", s))
                    if s.startswith("#") or re.search(r'\s+#\s+', s):
                        snippet_errors.append((path, "Raw heading hashes leaked", s))

    if snippet_errors:
        print(f"  ❌ FAILED: {len(snippet_errors)} snippet formatting issues found:")
        for p, err, s in snippet_errors[:5]:
            print(f"     - {p}: {err} -> '{s[:80]}...'")
        sys.exit(1)
    else:
        print("  ✓ All related note snippets are cleanly formatted with zero icon or markdown leaks")

    # 7. Content-Bearing Section Pages Validation (games, fiction categories)
    print("7. Validating Section Pages with Content (Games, Books):")
    fps_html = load_html("games/fps")
    fps_rel = get_related_section(fps_html)
    assert fps_rel, "Games FPS section missing related-notes-section"
    assert "related-note-card" in fps_rel, "Games FPS section has no related note cards"
    print("  ✓ Games FPS section renders related notes")

    scifi_html = load_html("books/fiction/sci-fi")
    scifi_rel = get_related_section(scifi_html)
    assert scifi_rel, "Books Sci-Fi section missing related-notes-section"
    assert "related-note-card" in scifi_rel, "Books Sci-Fi section has no related note cards"
    print("  ✓ Books Sci-Fi section renders related notes")

    print("\n✓ All Related Notes & Mentions tests passed successfully!")

if __name__ == "__main__":
    run_tests()
