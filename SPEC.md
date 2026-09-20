# Feature Specification: Bi-directional Backlinks ("Mentioned In / Linked From")

## 1. User Story & Context
As a reader exploring arunsrin's digital garden, I want to see which other notes link to the current note ("Mentioned In"), along with a contextual snippet where the reference occurs, so that I can explore interconnected trains of thought across Tech, Books, Games, and Research.

## 2. Layout & Positioning Order
In `layouts/_default/single.html`, notes must display sections in the following strict vertical sequence:
1. **Note Content (`.Content`)**
2. **Backlinks Section (`🔗 Mentioned In`)** — rendered ONLY if at least one incoming backlink exists.
3. **Related Notes Section (`🔗 Related Notes`)** — rendered ONLY if related notes exist.

## 3. Detailed Acceptance Criteria
1. **Accurate Backlink Discovery:**
   - Detect pages in `site.RegularPages` whose `.Content` links to the current page (e.g. matching `.RelPermalink`, or clean permalink path).
   - Ignore self-references (a note cannot be listed as a backlink to itself).
   - Exclude non-content/utility pages.
2. **Contextual Excerpt Display (Obsidian Style):**
   - Each backlink item displays:
     - Note title with icon (`📄` for page, `📁` for section).
     - Section / category badge (e.g. `Tech`, `Books`).
     - A readable surrounding context snippet showing the sentence or clause where the reference is made (plain text, no broken HTML tags).
3. **Clean Empty State:**
   - If a page has zero incoming backlinks, the `Mentioned In` section must NOT render any HTML, headers, or empty containers.
4. **Related Notes Visibility Check:**
   - Preserve and polish the existing `Related Notes` section so it renders properly directly beneath the Backlinks section whenever related notes exist.
5. **Sacred Prose Principle:**
   - Absolutely NO modifications to markdown content files (`home/**/*.md`).
6. **Performance & Cloudflare Safety:**
   - 100% build-time template logic; zero client-side render-blocking JS.
   - Any client enhancements must be vanilla JS, Rocket Loader safe.
   - Styling must strictly match the turquoise/sky-blue digital garden aesthetic (`#0284c7` in light mode, `#38bdf8` in dark mode).
7. **Strict QA Certification:**
   - `./scripts/test.sh` must exit 0 with 0 Hugo warnings, valid JSON indexes, and 0 broken links.
