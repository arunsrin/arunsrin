# Feature Specification: Consistent Homepage Card Titles and Dividers

## 1. Overview & Context
On the digital garden home page ([`home/_index.md`](home/_index.md)), the top-level sections are presented as a grid of cards (`<div class="grid cards" markdown>`).
Previously, the card titles were inconsistent:
- **Tech Notes:** `:material-console:{ .lg .middle .anim-rotate } __Tech Notes__` followed by a horizontal divider `---` and intro text.
- **Books:** `:material-book:{ .lg .middle .anim-bounce } __Books__` followed by a horizontal divider `---` and intro link `Me and my [books](books/index.md)`.
- **Games:** Inconsistently titled with `:material-controller:{ .lg .middle .anim-bounce } Me and my [games](games/index.md)`, lacking bold card title formatting (`__Games__`) and lacking the `---` visual divider.
- **Other Media:** Inconsistently titled with `:material-television:{ .lg .middle .anim-flip } Other media` lacking bold title formatting (`__Other Media__`) and lacking the `---` visual divider.

This feature standardizes all card titles across the homepage grid to follow the exact same visual structure: an animated Iconify icon followed by bold title (`__<Title>__`), a divider (`---`), and the section summary/links below.

---

## 2. Technical Architecture & Markdown Changes

In [`home/_index.md`](home/_index.md):

1. **Standardize Games Card:**
   ```markdown
   -   :material-controller:{ .lg .middle .anim-bounce } __Games__

       ---

       Me and my [games](games/index.md)

       Current-gen: I have an [:fontawesome-brands-xbox:{ .anim-pulse }Xbox Series X](games/xbox.md)

       Here is a list of games played per year:
   ```

2. **Standardize Other Media Card:**
   ```markdown
   -   :material-television:{ .lg .middle .anim-flip } __Other Media__

       ---

       - [Movies and TV](other-interests/media.md) that I really like
   ```

---

## 3. Constraints & Guardrails

1. **Sacred Prose Principle:**
   All note commentary, descriptions, and linked targets remain untouched. Only the card titles and structural separators are standardized.
2. **CSS Styling Compatibility:**
   In [`home/css/extra.css`](home/css/extra.css), `.grid.cards > ul > li > p:first-child` styles the first paragraph as `font-weight: 700; font-size: 1.1rem; color: var(--text-color);`, and `.grid.cards > ul > li hr` formats the horizontal rule. Declaring `__Games__` and `---` ensures identical CSS application across all cards.
3. **Automated Test Coverage & CI Parity:**
   Dedicated regression test suite `scripts/test_homepage_cards.py` integrated into both `./scripts/test.sh` and `.github/workflows/ci.yml`.

---

## 4. Acceptance Criteria

1. **Card Title Consistency:**
   - Every card `li` in `<div class="grid cards">` on the home page begins with an icon and `<strong>` title (`Tech Notes`, `Books`, `Games`, `Other Media`).
2. **Horizontal Rule Presence:**
   - Every card in the grid contains an `<hr>` separator immediately beneath the title paragraph.
3. **Games Subtitle Structure:**
   - The link `Me and my games` is positioned as the introductory paragraph immediately beneath the `<hr>` divider in the Games card, mirroring the Books card (`Me and my books`).
4. **CI & Local Test Parity:**
   - All tests in `./scripts/test.sh` pass with zero Hugo warnings and 100% green tests in GitHub Actions CI.
