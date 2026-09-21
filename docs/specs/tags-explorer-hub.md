# Specification: Multi-Tag Explorer Hub (/tags/)

## 1. Context & User Story
The personal digital garden at [arunsr.in](https://www.arunsr.in) features a standardized 33-tag taxonomy spanning books, games, tech notes, and research. Previously, navigating to `/tags/` rendered a plain fallback directory list via `layouts/_default/list.html` without frequency indicators, search filtering, or categorization.

As a visitor or reader exploring arunsrin's digital garden, I want an interactive, responsive Multi-Tag Explorer Hub at `/tags/` so that I can:
- Instantly discover cross-disciplinary topic clusters.
- Filter tags in real-time as I type.
- Toggle between an alphabetical index and a frequency-ranked tag cloud.
- See at-a-glance note counts for every topic.
- Quickly access cross-cutting topics directly from the homepage and sidebar.

---

## 2. Author Decisions (Phase 1 Interview)
During the Phase 1 interview, the author confirmed:
1. **Organization on `/tags/`**: Alphabetical by default (grouped by letter A-Z) with a toggle button to switch to 'By Frequency' (most frequent first).
2. **Homepage Topic Cloud**: Place a clean tag cloud shortcode (`{{< tag-cloud >}}`) right before the 'About' section on the homepage (`home/_index.md`), displaying all tags with counts and an action link to `/tags/`.
3. **Sidebar Link Placement**: Under the `Site` section in `layouts/partials/sidebar.html`, ordered as:
   - `⏳ Now`
   - `🛠️ Uses`
   - `🏷️ Tags` *(active on `/tags/` and `/tags/*`)*
   - `ℹ️ About`
   - `🗺️ Sitemap`
   - `RSS Feed`

---

## 3. Core Guardrails (AGENTS.md Compliance)
- **Sacred Prose (Rule 9)**: No markdown prose or note text may be rewritten or altered. In `home/_index.md`, only the new topic cloud section is appended before `About`.
- **Performance & Zero Bloat (Rule 1)**: Pure vanilla JavaScript (<1.5 KB), zero external libraries or heavy frameworks.
- **Cloudflare Rocket Loader Safety (Rule 2)**: ZERO inline event handlers (`onclick`, `oninput`, `onchange`). All event listeners attached unobtrusively via `addEventListener` after DOM load.
- **Visual Identity (Rule 1)**: Theme-consistent styling matching the light blue palette (`#0284c7` for light mode, `#38bdf8` for dark mode).
- **Automated Regression Testing & CI Parity (Rules 10 & 11)**: Dedicated test suite `scripts/test_tags_explorer.py` verified in `./scripts/test.ps1` / `./scripts/test.sh` and discovered dynamically by GitHub Actions CI.
- **Windows UTF-8 Stdout Reconfiguration (Rule 12)**: Required UTF-8 console initialization in test scripts.

---

## 4. Numbered Acceptance Criteria

1. **Dedicated Taxonomy Terms Template (`layouts/_default/terms.html`)**:
   - Navigating to `/tags/` renders a dedicated Explorer Hub page with breadcrumbs (`Home / Tags`), page heading (`🏷️ Tags Explorer`), and total tag count badge.
2. **Real-Time Client-Side Filter**:
   - An instant search input (`#tag-search-input`) filters visible tag pills and letter group sections in real-time on keystroke.
   - Dynamic counter updates to indicate visible count (e.g. `Showing 33 of 33 tags`, `Showing 4 of 33 tags`).
   - Friendly empty state displayed when no tags match the query.
3. **Dual-Mode Organization (A-Z vs. Frequency)**:
   - **Alphabetical View (Default)**: Tags grouped under uppercase letter headings (A, C, D, ...) with count badges `(N)`.
   - **Frequency View**: Tags sorted descending by frequency count, displaying all tags with count badges.
   - View toggle controls allow switching between Alphabetical and Frequency modes with clear active button state.
4. **Pill Grid Styling & Theme Integration**:
   - Tag pills adhere to `--link-color` (`#0284c7` in light mode, `#38bdf8` in dark mode) and background variables.
   - Count badges styled cleanly inside each pill.
   - Clicking any tag pill navigates to `/tags/<term>/`.
5. **Homepage Tag Cloud Shortcode**:
   - Reusable shortcode `layouts/shortcodes/tag-cloud.html` renders tag pills with count badges and a link to `/tags/`.
   - Integrated into `home/_index.md` before the About section.
6. **Sidebar Navigation Link**:
   - Link to `🏷️ Tags` (`/tags/`) present in `layouts/partials/sidebar.html` under `Site` section.
   - Active highlighting applies when current URL is `/tags/` or starts with `/tags/`.
7. **Automated Regression Suite (`scripts/test_tags_explorer.py`)**:
   - Validates generated HTML in `public/tags/index.html` for controls, pills, counts, and zero inline handlers.
   - Validates presence of sidebar link across pages and homepage tag cloud.
   - 100% passing across `./scripts/test.ps1` and `./scripts/test.sh`.
