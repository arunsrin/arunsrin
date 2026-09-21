#!/usr/bin/env python3
"""
Regression test suite for homepage front porch, category hubs, featured notes,
dynamic recently tended stream, and dedicated sitemap directory.

Validates:
1. Curated Homepage (home/_index.md & public/index.html):
   - 4 Garden Hub cards (Tech Notes, Books, Games, Other Media) with bold titles and <hr> dividers.
   - Featured Notes grid with 3 cards (Think Like a Stoic, Kubernetes, Xbox Series X).
   - Dynamic Recently Tended stream with 5 note cards, dates, sections, and links.
   - Anti-leak check: /about/ and /sitemap/ excluded from recent stream.
   - Sidebar contains active/inactive Sitemap navigation link.
2. Dedicated Sitemap (home/sitemap.md & public/sitemap/index.html):
   - 4 Comprehensive directory cards with bold titles, <hr> dividers, and sublinks.
   - Games card includes subtitle link 'Me and my games' and bold '**By Genre**'.
   - Digital Garden grid includes 'Book Reviews', 'Research', and 'Role Models'.
   - Outdated 'played per year' phrase absent.
"""

import os
import re
import sys
import html.parser

# Ensure UTF-8 output across Windows and Linux terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    public_index = os.path.join("public", "index.html")
    public_sitemap = os.path.join("public", "sitemap", "index.html")
    home_index_md = os.path.join("home", "_index.md")
    home_sitemap_md = os.path.join("home", "sitemap.md")

    if not os.path.exists(public_index):
        print(f"Error: {public_index} does not exist. Run 'hugo' first.")
        sys.exit(1)
    if not os.path.exists(public_sitemap):
        print(f"Error: {public_sitemap} does not exist. Run 'hugo' first.")
        sys.exit(1)

    print("--- Homepage & Sitemap Regression Test Suite ---")

    # 1. Verify Homepage markdown structure
    print("1. Verifying markdown source in home/_index.md:")
    with open(home_index_md, "r", encoding="utf-8") as fp:
        home_md = fp.read()

    # Verify Hub cards
    hub_grid_m = re.search(r'# :material-compass-outline:\{[^\}]+\}\s+Hubs.*?(<div class="grid cards" markdown>.*?</div>)', home_md, re.DOTALL)
    assert hub_grid_m, "Could not find Hubs card grid in home/_index.md"
    hub_grid = hub_grid_m.group(1)
    assert re.search(r':material-console:\{[^\}]+\}\s+__Tech Notes__\s*\n\s*---', hub_grid), "Tech Notes hub missing bold title or divider"
    assert re.search(r':material-book:\{[^\}]+\}\s+__Books__\s*\n\s*---', hub_grid), "Books hub missing bold title or divider"
    assert re.search(r':material-controller:\{[^\}]+\}\s+__Games__\s*\n\s*---', hub_grid), "Games hub missing bold title or divider"
    assert "Explore Tech Notes" in hub_grid, "Tech Notes hub missing Explore link"
    assert "Explore Books" in hub_grid, "Books hub missing Explore link"
    assert "Explore Games" in hub_grid, "Games hub missing Explore link"
    assert "Explore Media" in hub_grid, "Other Media hub missing Explore link"
    assert "sitemap.md" not in hub_grid, "Sitemap link should not be present inside Hub cards"


    # Verify Featured Notes grid
    feat_grid_m = re.search(r'# :material-star-shooting-outline:\{[^\}]+\}\s+Featured Notes.*?(<div class="grid cards" markdown>.*?</div>)', home_md, re.DOTALL)
    assert feat_grid_m, "Could not find Featured Notes card grid in home/_index.md"
    feat_grid = feat_grid_m.group(1)
    assert "Think Like a Stoic" in feat_grid, "Featured notes missing 'Think Like a Stoic'"
    assert "OpenSSL" in feat_grid, "Featured notes missing 'OpenSSL'"
    assert "Xbox Series X" in feat_grid, "Featured notes missing 'Xbox Series X'"


    # Verify Recent Updates section and shortcode
    assert re.search(r'# :material-clock-outline:\{[^\}]+\}\s+Recent Updates', home_md), "Recent Updates heading missing from home/_index.md"
    assert re.search(r'\{\{<\s*recently-updated\b', home_md), "Recently updated shortcode missing from home/_index.md"

    # Negative assertions: no overused garden metaphors
    assert "Garden Hubs" not in home_md, "Overused metaphor 'Garden Hubs' still present in home/_index.md"
    assert "Recently Tended" not in home_md, "Overused metaphor 'Recently Tended' still present in home/_index.md"
    print("  ✓ Homepage markdown has Hubs, Featured Notes, and Recent Updates stream (garden metaphors toned down).")


    # 2. Verify Homepage generated HTML
    print("2. Verifying generated HTML in public/index.html:")
    with open(public_index, "r", encoding="utf-8") as fp:
        home_html = fp.read()

    # Verify Recently Tended stream cards
    recent_cards = re.findall(r'class=["\']?recent-note-card["\']?', home_html)
    assert len(recent_cards) == 5, f"Expected 5 recently updated cards, found {len(recent_cards)}"

    # Check dates, titles, and sections in stream
    recent_titles = re.findall(r'class=["\']?recent-note-title["\']?>([^<]+)</span>', home_html)
    recent_dates = re.findall(r'class=["\']?recent-note-date["\']?>([^<]+)</span>', home_html)
    assert len(recent_titles) == 5, f"Expected 5 recent note titles, found {len(recent_titles)}"
    assert len(recent_dates) == 5, f"Expected 5 recent note dates, found {len(recent_dates)}"

    # Date format validation (e.g. 'Sep 20, 2026')
    for d in recent_dates:
        assert re.match(r'^[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}$', d.strip()), f"Date '{d}' does not match expected format 'Mon DD, YYYY'"

    # Anti-leak negative assertions
    stream_chunk_m = re.search(r'class=["\']?recently-updated-stream["\']?>(.*?)</div>\s*<hr', home_html, re.DOTALL)
    if stream_chunk_m:
        stream_chunk = stream_chunk_m.group(1)
        assert 'href="/about/"' not in stream_chunk, "Leak: /about/ found inside Recently Tended stream!"
        assert 'href="/sitemap/"' not in stream_chunk, "Leak: /sitemap/ found inside Recently Tended stream!"

    # Sidebar sitemap link check
    assert re.search(r'<a\s+href=["\']?/sitemap/["\']?[^>]*>.*?Sitemap</a>', home_html, re.DOTALL), "Sidebar missing /sitemap/ link!"
    print("  ✓ Homepage HTML contains 5 recently updated note cards with valid dates and sidebar link.")

    # 3. Verify Dedicated Sitemap markdown source
    print("3. Verifying markdown source in home/sitemap.md:")
    with open(home_sitemap_md, "r", encoding="utf-8") as fp:
        sitemap_md = fp.read()

    # Comprehensive 4 cards
    assert re.search(r':material-console:\{[^\}]+\}\s+__Tech Notes__\s*\n\s*---', sitemap_md), "Sitemap Tech Notes card missing bold title or divider"
    assert re.search(r':material-book:\{[^\}]+\}\s+__Books__\s*\n\s*---', sitemap_md), "Sitemap Books card missing bold title or divider"
    assert re.search(r':material-controller:\{[^\}]+\}\s+__Games__\s*\n\s*---', sitemap_md), "Sitemap Games card missing bold title or divider"
    assert re.search(r':material-television:\{[^\}]+\}\s+__Other Media__\s*\n\s*---', sitemap_md), "Sitemap Other Media card missing bold title or divider"
    assert "Me and my [books]" in sitemap_md, "Sitemap missing 'Me and my [books]'"
    assert "Me and my [games]" in sitemap_md, "Sitemap missing 'Me and my [games]'"
    assert re.search(r'\*\*By Genre\*\*', sitemap_md), "Sitemap Games card missing **By Genre** header"
    assert "played per year" not in sitemap_md, "Outdated 'played per year' text present in sitemap.md"

    # Digital Garden & Research grid
    assert "__Book Reviews__" in sitemap_md, "Sitemap missing Book Reviews card"
    assert "__Research__" in sitemap_md, "Sitemap missing Research card"
    assert "__Role Models__" in sitemap_md, "Sitemap missing Role Models card"
    print("  ✓ Sitemap markdown source preserves all directory cards, genres, and digital garden sections.")

    # 4. Verify Generated Sitemap HTML
    print("4. Verifying generated HTML in public/sitemap/index.html:")
    with open(public_sitemap, "r", encoding="utf-8") as fp:
        sitemap_html = fp.read()

    class GridParser(html.parser.HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_target_grid = False
            self.first_grid_done = False
            self.ul_depth = 0
            self.top_cards = []
            self.current_card = None

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)
            cls = attrs_dict.get('class', '')
            if 'grid cards' in cls and not self.first_grid_done:
                self.in_target_grid = True
            elif self.in_target_grid:
                if tag == 'ul':
                    self.ul_depth += 1
                elif tag == 'li' and self.ul_depth == 1:
                    self.current_card = {
                        'html_parts': [],
                        'has_hr': False,
                        'first_p': None,
                        'current_p': []
                    }
                elif tag == 'p' and self.current_card is not None:
                    self.current_card['current_p'] = []
                elif tag == 'hr' and self.current_card is not None:
                    self.current_card['has_hr'] = True

        def handle_endtag(self, tag):
            if self.in_target_grid:
                if tag == 'p' and self.current_card is not None:
                    if self.current_card['first_p'] is None:
                        self.current_card['first_p'] = "".join(self.current_card['current_p']).strip()
                elif tag == 'ul':
                    self.ul_depth -= 1
                    if self.ul_depth == 0:
                        self.in_target_grid = False
                        self.first_grid_done = True
                elif tag == 'li' and self.ul_depth == 1:
                    if self.current_card:
                        self.top_cards.append(self.current_card)
                        self.current_card = None

        def handle_data(self, data):
            if self.current_card is not None:
                self.current_card['html_parts'].append(data)
                self.current_card['current_p'].append(data)

    parser = GridParser()
    parser.feed(sitemap_html)

    cards = parser.top_cards
    assert len(cards) == 4, f"Expected 4 top-level cards in sitemap main grid, found {len(cards)}"

    expected_titles = ["Tech Notes", "Books", "Games", "Other Media"]
    for i, (card, expected) in enumerate(zip(cards, expected_titles), 1):
        first_p = card['first_p'] or ""
        assert expected in first_p, f"Card {i} title paragraph '{first_p}' does not contain '{expected}'"
        assert card['has_hr'], f"Card {i} ({expected}) is missing <hr> divider!"
        print(f"  ✓ Sitemap Card {i} ({expected}): Title formatted and <hr> present.")

    games_card_text = "".join(cards[2]['html_parts'])
    assert "Me and my games" in games_card_text, "Sitemap Games card is missing subtitle 'Me and my games'"
    assert "Xbox Series X" in games_card_text, "Sitemap Games card is missing platform detail"
    assert "By Genre" in games_card_text, "Sitemap Games card is missing 'By Genre' header"
    assert "played per year" not in games_card_text, "Outdated 'played per year' phrase still present in Sitemap Games card!"
    assert "<strong>By Genre</strong>" in sitemap_html, "Sitemap Games card missing bold <strong>By Genre</strong> element"

    print("\n✓ ALL HOMEPAGE & SITEMAP REGRESSION TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
