# Feature Specification: Re-categorise Pages & Standardize Main Hubs

## User Story & Context
As a reader exploring arunsrin's notes, I want a clean, logical, and consistent taxonomy across the digital garden, with 4 primary hubs: **Tech**, **Books**, **Games**, and **Other Interests**.
Previously:
- "Tech Notes" was inconsistently named compared to "Books" and "Games".
- The homepage and sitemap highlighted "Other Media" instead of the comprehensive "Other Interests" hub.
- Pages like `AI` were placed under `tech/` despite being an eclectic interest and workflow topic, and `Productivity` was buried deep within `research/`.
- Visiting hub landing pages (such as `/tech/`) only listed direct child pages and top-level folder names (`Linux`, `Programming`), hiding all grandchild notes (`Go`, `Python`, `SystemD`, etc.) unless readers looked at the sidebar.

This feature re-categorises pages, standardizes the four hubs across the site, and upgrades the hub/section list display so children and grandchildren are clearly visible in the main content area.

---

## Acceptance Criteria

### 1. Four Main Hubs Standardization
1. **Rename "Tech Notes" to "Tech":**
   - The hub title in `home/tech/_index.md` is updated from "Tech Notes" to "Tech".
   - The H1 heading is updated to `:material-console:{ .anim-rotate } Tech`.
   - The homepage card (`home/_index.md`), sitemap card (`home/sitemap.md`), 404 page, and breadcrumbs refer to "Tech".
   - Explore button on homepage reads `Explore Tech` linking to `tech/index.md`.
2. **Promote "Other Interests" as a Distinct Main Hub:**
   - Homepage card is updated from "Other Media" to "Other Interests" (`__Other Interests__`), linking to `other-interests/index.md` with button `Explore Other Interests`.
   - Sitemap card is updated from "Other Media" to "Other Interests", linking to `other-interests/`.
   - Sidebar maintains "Other Interests" as a primary section.

### 2. Page Re-categorization & Alias Integrity
1. **Relocate `ai.md`:**
   - Move from `home/tech/ai.md` to `home/other-interests/ai.md`.
   - Include `aliases: ["/tech/ai/"]` in frontmatter for zero broken inbound links.
2. **Relocate `productivity.md`:**
   - Move from `home/other-interests/research/productivity.md` to `home/other-interests/productivity.md`.
   - Include `aliases: ["/other-interests/research/productivity/"]` in frontmatter.
3. **Sections for `people/` and `research/`:**
   - Add `_index.md` in `home/other-interests/people/` with `title: "People"` and appropriate tags/icon.
   - Add `_index.md` in `home/other-interests/research/` with `title: "Research"` and appropriate tags/icon.
4. **Internal Links & References:**
   - Update internal markdown links (e.g. `home/about.md`, `home/sitemap.md`, `home/other-interests/productivity.md`) to reflect new paths.
   - Full link check (`python scripts/check_links.py`) passes with zero broken links.

### 3. Hub & Section Display: Children and Grandchildren Visibility
1. **Hierarchical Page Tree in Section List:**
   - Update section list rendering (`layouts/_default/list.html` or a dedicated partial) so that when a section contains sub-sections:
     - Direct pages are listed with their title, icon, and description.
     - Sub-sections are listed with their icon/title, followed by an indented list of their own child pages (grandchildren of the parent hub).
2. **Consistent Hub Presentation:**
   - On `/tech/`: readers see tools (Ansible, AWS, Docker, etc.) AND under Linux they see `Learnings & Notes`, `Package Management`, `SystemD`; under Programming they see `Go`, `Java`, `Powershell`, `Python`.
   - On `/other-interests/`: readers see `AI`, `Movies`, `Productivity` AND under People and Research they see their respective notes.
   - On `/books/` and `/games/`: the automated listing consistently displays the sub-sections and their nested pages.

### 4. Guardrails & Compliance
1. **Sacred Prose Principle:** The author's prose in markdown notes is strictly preserved without alterations.
2. **Zero Bloat & Performance:** No JavaScript frameworks. Lightweight vanilla CSS using existing theme variables (`var(--link-color)`, `var(--border-color)`, `var(--text-muted)`).
3. **Cloudflare & Rocket Loader Safety:** Zero inline event handlers.
4. **Automated Test Coverage & CI Parity:**
   - Update existing test scripts (`scripts/test_homepage_cards.py`, `scripts/test_sitemap_and_recent.py`, `scripts/test_tech_emojis.py`, `scripts/test_tags.py`).
   - Add `scripts/test_hubs_and_recategorisation.py` asserting all acceptance criteria and negative regression checks.
