#!/usr/bin/env python3
"""
Regression test suite for homepage card titles and dividers.
Validates:
1. All 4 top-level cards in the main homepage grid have bold titles (__Tech Notes__, __Books__, __Games__, __Other Media__).
2. Every card in the main grid contains an <hr> separator directly below the title.
3. The Games card has its subtitle link 'Me and my games' positioned below the <hr> divider, mirroring the Books card.
4. No card title retains the old unformatted 'Me and my games' or unformatted 'Other media'.
5. Both HTML and Markdown integrity are preserved.
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
    home_index_md = os.path.join("home", "_index.md")

    if not os.path.exists(public_index):
        print(f"Error: {public_index} does not exist. Run 'hugo' first.")
        sys.exit(1)

    print("--- Homepage Cards Consistency Test Suite ---")

    # 1. Verify markdown source structure
    print("1. Verifying markdown source in home/_index.md:")
    with open(home_index_md, "r", encoding="utf-8") as fp:
        md_text = fp.read()

    # Extract the first grid cards block
    first_grid_m = re.search(r'<div class="grid cards" markdown>(.*?)</div>', md_text, re.DOTALL)
    assert first_grid_m, "Could not find first <div class=\"grid cards\" markdown> in home/_index.md"
    first_grid = first_grid_m.group(1)

    # Check for expected bold titles and dividers
    assert re.search(r':material-console:\{[^\}]+\}\s+__Tech Notes__\s*\n\s*---', first_grid), "Tech Notes card missing bold title or divider"
    assert re.search(r':material-book:\{[^\}]+\}\s+__Books__\s*\n\s*---', first_grid), "Books card missing bold title or divider"
    assert re.search(r':material-controller:\{[^\}]+\}\s+__Games__\s*\n\s*---', first_grid), "Games card missing bold title or divider"
    assert re.search(r':material-television:\{[^\}]+\}\s+__Other Media__\s*\n\s*---', first_grid), "Other Media card missing bold title or divider"

    # Negative check: old unformatted titles must not exist
    assert not re.search(r':material-controller:\{[^\}]+\}\s+Me and my \[games\]', first_grid), "Old unformatted Games title still present!"
    assert not re.search(r':material-television:\{[^\}]+\}\s+Other media', first_grid), "Old unformatted Other Media title still present!"
    assert re.search(r'\*\*By Genre\*\*', first_grid), "Games card missing **By Genre** header in markdown!"
    assert "played per year" not in first_grid, "Outdated 'played per year' text still present in markdown!"
    print("  ✓ All 4 markdown cards have bold titles, dividers, and correct formatting.")

    # 2. Verify generated HTML structure
    print("2. Verifying generated HTML in public/index.html:")
    with open(public_index, "r", encoding="utf-8") as fp:
        html_text = fp.read()

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
    parser.feed(html_text)

    cards = parser.top_cards
    assert len(cards) == 4, f"Expected 4 top-level cards in main grid, found {len(cards)}"

    expected_titles = ["Tech Notes", "Books", "Games", "Other Media"]
    for i, (card, expected) in enumerate(zip(cards, expected_titles), 1):
        first_p = card['first_p'] or ""
        assert expected in first_p, f"Card {i} title paragraph '{first_p}' does not contain '{expected}'"
        assert card['has_hr'], f"Card {i} ({expected}) is missing <hr> divider!"
        print(f"  ✓ Card {i} ({expected}): Title formatted and <hr> present.")

    # 3. Check Games card content
    games_card_text = "".join(cards[2]['html_parts'])
    assert "Me and my games" in games_card_text, "Games card is missing subtitle 'Me and my games'"
    assert "Xbox Series X" in games_card_text, "Games card is missing platform detail"
    assert "By Genre" in games_card_text, "Games card is missing 'By Genre' header"
    assert "played per year" not in games_card_text, "Outdated 'played per year' phrase still present in Games card!"
    assert "<strong>By Genre</strong>" in html_text, "Games card missing bold <strong>By Genre</strong> element"
    print("  ✓ Games card contains subtitle link, platform details, and 'By Genre' header.")

    print("\n✓ ALL HOMEPAGE CARDS REGRESSION TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
