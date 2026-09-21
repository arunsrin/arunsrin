#!/usr/bin/env python3
"""
Automated regression test suite for Hub Re-categorisation & Hierarchical Display.
Validates:
1. 4 Main Hubs standardization (Tech, Books, Games, Other Interests) across homepage and sitemap.
2. Negative assertions: 'Tech Notes' and 'Other Media' eliminated from hub cards.
3. Page relocations and alias redirects for AI and Productivity.
4. Hub / Section page display: automated nested rendering of children and grandchildren.
5. Presence of sub-sections (people, research) and anti-spurious isolation on /tech/.
"""

import os
import re
import sys

# Ensure UTF-8 stdout/stderr across Windows and Linux terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    public_dir = "public"
    if not os.path.exists(public_dir):
        print(f"Error: {public_dir} does not exist. Run 'hugo' first.")
        sys.exit(1)

    print("--- 4 Main Hubs & Page Re-categorisation Test Suite ---")

    # 1. Four Main Hubs Standardization on Homepage
    print("1. Verifying 4 Main Hubs on Homepage:")
    home_html_path = os.path.join(public_dir, "index.html")
    assert os.path.exists(home_html_path), "public/index.html not found!"
    with open(home_html_path, "r", encoding="utf-8") as fp:
        home_html = fp.read()

    expected_hubs = [
        ("Tech", "/tech/", "Explore Tech"),
        ("Books", "/books/", "Explore Books"),
        ("Games", "/games/", "Explore Games"),
        ("Other Interests", "/other-interests/", "Explore Other Interests"),
    ]

    for title, href, btn_text in expected_hubs:
        assert title in home_html, f"Homepage missing hub title '{title}'"
        assert href in home_html, f"Homepage missing link to '{href}'"
        assert btn_text in home_html, f"Homepage missing exploration button '{btn_text}'"
        print(f"  ✓ Hub '{title}' verified on homepage with button '{btn_text}'.")

    # Negative check: old hub names eliminated
    assert "Explore Tech Notes" not in home_html, "Outdated 'Explore Tech Notes' button still on homepage!"
    assert "Explore Media" not in home_html, "Outdated 'Explore Media' button still on homepage!"
    print("  ✓ Negative checks passed: 'Explore Tech Notes' and 'Explore Media' eliminated.")

    # 2. Sitemap Hub Cards
    print("2. Verifying Hub Cards in Sitemap:")
    sitemap_html_path = os.path.join(public_dir, "sitemap", "index.html")
    assert os.path.exists(sitemap_html_path), "public/sitemap/index.html not found!"
    with open(sitemap_html_path, "r", encoding="utf-8") as fp:
        sitemap_html = fp.read()

    assert "Tech" in sitemap_html, "Sitemap missing 'Tech' card"
    assert "Other Interests" in sitemap_html, "Sitemap missing 'Other Interests' card"
    assert re.search(r'id=["\']?tech["\'\s>]', sitemap_html), "Sitemap missing anchor id='tech'"
    assert re.search(r'id=["\']?other-interests["\'\s>]', sitemap_html), "Sitemap missing anchor id='other-interests'"
    # Backward-compatible anchor preservation
    assert re.search(r'id=["\']?tech-notes["\'\s>]', sitemap_html), "Sitemap missing backward-compatible id='tech-notes'"
    assert re.search(r'id=["\']?other-media["\'\s>]', sitemap_html), "Sitemap missing backward-compatible id='other-media'"
    print("  ✓ Sitemap contains Tech & Other Interests cards with current and legacy anchor targets.")

    # 3. 404 Page Verification
    print("3. Verifying 404 Page:")
    not_found_path = os.path.join(public_dir, "404.html")
    assert os.path.exists(not_found_path), "public/404.html not found!"
    with open(not_found_path, "r", encoding="utf-8") as fp:
        not_found_html = fp.read()
    assert "Tech" in not_found_html, "404 page missing 'Tech' button"
    assert "Tech Notes" not in not_found_html, "404 page still references 'Tech Notes'"
    print("  ✓ 404 page has clean 'Tech' button.")

    # 4. Page Relocations & Alias Redirects
    print("4. Verifying Relocated Pages and Aliases:")
    ai_src = os.path.join("home", "other-interests", "ai.md")
    ai_old_src = os.path.join("home", "tech", "ai.md")
    prod_src = os.path.join("home", "other-interests", "productivity.md")
    prod_old_src = os.path.join("home", "other-interests", "research", "productivity.md")

    assert os.path.exists(ai_src), "home/other-interests/ai.md does not exist!"
    assert not os.path.exists(ai_old_src), "home/tech/ai.md should have been moved!"
    assert os.path.exists(prod_src), "home/other-interests/productivity.md does not exist!"
    assert not os.path.exists(prod_old_src), "home/other-interests/research/productivity.md should have been moved!"

    # Check generated files
    assert os.path.exists(os.path.join(public_dir, "other-interests", "ai", "index.html")), "public/other-interests/ai/index.html missing!"
    assert os.path.exists(os.path.join(public_dir, "other-interests", "productivity", "index.html")), "public/other-interests/productivity/index.html missing!"

    # Check alias redirect HTML files
    tech_ai_alias = os.path.join(public_dir, "tech", "ai", "index.html")
    assert os.path.exists(tech_ai_alias), "Alias redirect public/tech/ai/index.html missing!"
    with open(tech_ai_alias, "r", encoding="utf-8") as fp:
        alias_content = fp.read()
    assert "/other-interests/ai/" in alias_content, "tech/ai alias does not redirect to /other-interests/ai/"

    prod_alias = os.path.join(public_dir, "other-interests", "research", "productivity", "index.html")
    assert os.path.exists(prod_alias), "Alias redirect for research/productivity missing!"
    with open(prod_alias, "r", encoding="utf-8") as fp:
        alias_content = fp.read()
    assert "/other-interests/productivity/" in alias_content, "productivity alias does not redirect to /other-interests/productivity/"
    print("  ✓ AI and Productivity relocated with working HTML alias redirects.")

    # 5. Tech Hub Section-Pages: Children & Grandchildren
    print("5. Verifying /tech/ Hierarchical Display:")
    tech_index_path = os.path.join(public_dir, "tech", "index.html")
    with open(tech_index_path, "r", encoding="utf-8") as fp:
        tech_html = fp.read()

    sec_m = re.search(r'<section class=[\"\']?section-pages[\"\']?[^>]*>(.*?)</section>', tech_html, re.DOTALL)
    assert sec_m, "section-pages missing on /tech/index.html"
    sec_html = sec_m.group(1)

    # Grandchildren under Linux
    for grandchild in ["/tech/linux/learnings-and-notes/", "/tech/linux/package-management/", "/tech/linux/systemd/"]:
        assert grandchild in sec_html, f"Linux grandchild page '{grandchild}' missing from /tech/ section list!"
    print("  ✓ Linux grandchild pages (learnings-and-notes, package-management, systemd) visible on /tech/.")

    # Grandchildren under Programming
    for grandchild in ["/tech/programming/go/", "/tech/programming/java/", "/tech/programming/powershell/", "/tech/programming/python/"]:
        assert grandchild in sec_html, f"Programming grandchild page '{grandchild}' missing from /tech/ section list!"
    print("  ✓ Programming grandchild pages (go, java, powershell, python) visible on /tech/.")

    # Anti-spurious check on /tech/
    assert "/tech/ai/" not in sec_html, "AI should NOT appear in /tech/ section list"
    assert "/other-interests/ai/" not in sec_html, "AI should NOT appear in /tech/ section list"
    print("  ✓ Negative test passed: AI is no longer listed in /tech/ section list.")

    # 6. Other Interests Hub Section-Pages
    print("6. Verifying /other-interests/ Hierarchical Display:")
    other_index_path = os.path.join(public_dir, "other-interests", "index.html")
    with open(other_index_path, "r", encoding="utf-8") as fp:
        other_html = fp.read()

    other_sec_m = re.search(r'<section class=[\"\']?section-pages[\"\']?[^>]*>(.*?)</section>', other_html, re.DOTALL)
    assert other_sec_m, "section-pages missing on /other-interests/index.html"
    other_sec_html = other_sec_m.group(1)

    # Top-level items in other-interests
    for top_page in ["/other-interests/ai/", "/other-interests/media/", "/other-interests/productivity/"]:
        assert top_page in other_sec_html, f"Direct note '{top_page}' missing from /other-interests/ section list!"
    print("  ✓ Direct notes (AI, Media/Movies, Productivity) visible on /other-interests/.")

    # People sub-section children
    for person in ["/other-interests/people/chomsky/", "/other-interests/people/dawkins/", "/other-interests/people/sagan/", "/other-interests/people/stallman/"]:
        assert person in other_sec_html, f"Person note '{person}' missing from /other-interests/ section list!"
    print("  ✓ People sub-section child notes (Chomsky, Dawkins, Sagan, Stallman) visible on /other-interests/.")

    # Research sub-section children
    for rnote in ["/other-interests/research/capitalism/", "/other-interests/research/climate-change/", "/other-interests/research/covid-19/", "/other-interests/research/cryptocurrencies/"]:
        assert rnote in other_sec_html, f"Research note '{rnote}' missing from /other-interests/ section list!"
    print("  ✓ Research sub-section child notes visible on /other-interests/.")

    # 7. Books Hub Section-Pages
    print("7. Verifying /books/ Hierarchical Display:")
    books_index_path = os.path.join(public_dir, "books", "index.html")
    with open(books_index_path, "r", encoding="utf-8") as fp:
        books_html = fp.read()

    books_sec_m = re.search(r'<section class=[\"\']?section-pages[\"\']?[^>]*>(.*?)</section>', books_html, re.DOTALL)
    assert books_sec_m, "section-pages missing on /books/index.html"
    books_sec_html = books_sec_m.group(1)

    assert "/books/fiction/sci-fi/" in books_sec_html, "Fiction sub-genre sci-fi missing from /books/ section list"
    assert "/books/non-fiction/philosophy/" in books_sec_html, "Non-fiction sub-genre philosophy missing from /books/ section list"
    assert "/books/non-fiction/philosophy/think-like-a-stoic/" in books_sec_html, "Review 'think-like-a-stoic' missing from /books/ section list"
    print("  ✓ Books hierarchical sub-genres and reviews visible on /books/.")

    print("\n✓ ALL 7 HUBS & RE-CATEGORISATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
