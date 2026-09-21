# Feature Specification: Curated Garden Front Porch & Dedicated Sitemap

## 1. Overview & Context

`home/_index.md` previously functioned as an exhaustive 50+ link directory list of the entire site. While thorough, this created an overwhelming initial landing experience rather than a welcoming, curated digital garden front porch.

This feature transforms the site entry points:
1. **Dedicated Sitemap Page (`/sitemap/`):** Houses the complete, organized listing of all sections, sub-sections, and notes (relocated from `home/_index.md`). Prominently linked in the sidebar under `Site` below `About`.
2. **Curated Garden Front Porch (`home/_index.md`):** A modern, warm homepage featuring:
   - **Hero / Welcome intro** to the digital garden.
   - **Category Hub cards** (Tech Notes, Books, Games, Other Media) linking to the main hubs and pointing to the full Sitemap.
   - **Featured Notes section:** 3 curated showcase notes (1 Book, 1 Tech, 1 Game; Research omitted for now) as replaceable placeholders.
   - **Dynamic 'Recently Updated Notes' stream:** Built natively with Hugo GitInfo (`enableGitInfo = true`, `.Site.RegularPages.ByLastmod.Reverse | first 5`), displaying note title, formatted update date, section badge, and link. Excludes `about.md` and `sitemap.md`.
   - **About & External Links** cleanly maintained.

---

## 2. Technical Architecture & Component Design

### 2.1 Dedicated Sitemap Page (`home/sitemap.md`)
- File: `home/sitemap.md` (URL: `/sitemap/`)
- Frontmatter:
  ```yaml
  ---
  title: "Sitemap & Full Directory"
  ---
  ```
- Contains the comprehensive multi-column card grids:
  - **Grid 1:** Tech Notes (all 25 tool & language links), Books (all Fiction & Non-Fiction genres), Games (all genres + hardware), Other Media.
  - **Grid 2:** Book Reviews (14 book review links), Research (8 topics + Oxford series), Role Models (Dawkins, Sagan, Stallman, Chomsky).

### 2.2 Sidebar Navigation Update (`layouts/partials/sidebar.html`)
- In the `Site` section below `About`:
  ```html
  <div class="nav-section-title" style="margin-top: 1.5rem;">Site</div>
  <ul>
    <li><a href="/about/" class="{{ if eq .RelPermalink "/about/" }}active{{ end }}">ℹ️ About</a></li>
    <li><a href="/sitemap/" class="{{ if eq .RelPermalink "/sitemap/" }}active{{ end }}">🗺️ Sitemap</a></li>
  </ul>
  ```

### 2.3 Hugo GitInfo & Recently Updated Stream
- In `hugo.toml`:
  ```toml
  enableGitInfo = true

  [frontmatter]
    lastmod = [":git", "lastmod", "date", "publishDate"]
  ```
- Implementation via Hugo shortcode `layouts/shortcodes/recently-updated.html` or direct partial in `layouts/index.html`:
  - Iterates over `.Site.RegularPages.ByLastmod.Reverse`.
  - Filters out `.RelPermalink` matching `/about/` or `/sitemap/`.
  - Takes `first 5`.
  - Renders a clean list/grid of recently tended notes with title, formatted date (`.Lastmod.Format "Jan 02, 2006"`), section tag, and relative link.

### 2.4 Featured Notes Section
- Initial starter placeholders:
  - **Books:** *Think Like a Stoic* (Massimo Pigliucci) — `/books/non-fiction/philosophy/think-like-a-stoic/`
  - **Tech:** *Kubernetes* — `/tech/k8s/`
  - **Games:** *Xbox Series X* — `/games/xbox/`
- Designed for easy customization and editing by the author.

### 2.5 Deep-Link Anchor Targets & Scroll Offsets
- The 4 Garden Hub cards on the homepage link directly to sitemap sections via URL fragments:
  - `sitemap.md#tech-notes`, `sitemap.md#books`, `sitemap.md#games`, `sitemap.md#other-media`.
- To support these deep links on Markdown card items (where Goldmark does not generate automatic heading IDs), anchor spans `<span id="<name>" class="heading-anchor-target"></span>` are placed before each card title in `home/sitemap.md`.
- `.heading-anchor-target` utilizes `scroll-margin-top: 80px` in `head.html` to prevent the sticky site header from obscuring the target card when navigated to.

### 2.6 Cloudflare Pages Deep History Integration
- Hugo's `enableGitInfo = true` reads git commit timestamps for `.Lastmod`.
- Cloudflare Pages build command is configured as: `git fetch --unshallow && hugo` to ensure the full git commit graph is pulled during deployment.

---

## 3. Constraints & Guardrails

1. **Sacred Prose Principle (Rule 9):**
   No author notes, book reviews, or personal commentary will be modified or rewritten. The full directory text moved to `sitemap.md` is preserved verbatim.
2. **Zero Bloat & Rocket Loader Safety (Rules 1 & 2):**
   Pure Hugo Go templates, semantic HTML, and lightweight CSS. Zero JavaScript frameworks; zero inline HTML event handlers.
3. **Visual Identity (Light Blue Theme):**
   Matches site turquoise-sky-blue gradient and clean card styling with existing CSS variables (`--primary-color`, `--border-color`, `--bg-card`).
4. **Automated Regression Testing & CI Parity (Rules 10 & 11):**
   Update `scripts/test_homepage_cards.py` and author companion test suite `scripts/test_sitemap_and_recent.py` to assert HTML presence, negative leak tests, anchor target resolution, and ensure full CI parity discovery.
5. **Windows UTF-8 Console Encoding (Rule 12):**
   All Python test scripts must reconfigure stdout and stderr for UTF-8.

---

## 4. Acceptance Criteria

1. **Dedicated Sitemap (`/sitemap/`):**
   - Page builds at `/sitemap/` containing the full 4-hub main directory card grid and the Digital Garden card grid (Book Reviews, Research, Role Models).
   - Sidebar includes an entry for Sitemap below About.
   - Deep-link anchor targets (`tech-notes`, `books`, `games`, `other-media`) exist with `scroll-margin-top` offsets.
2. **Curated Front Porch (`/`):**
   - Homepage features clean welcome intro, high-level category cards, featured notes placeholders (1 Books, 1 Tech, 1 Games), dynamic Recently Updated Notes stream (5 notes with dates), and external links.
   - Non-content pages (`about.md`, `sitemap.md`) are excluded from the Recently Updated feed.
3. **Hugo Build & GitInfo:**
   - Hugo builds cleanly with `--enableGitInfo --gc --minify --panicOnWarning` with zero warnings.
4. **Testing Suite:**
   - All tests in `./scripts/test.sh` and `./scripts/test.ps1` pass cleanly with 100% test coverage for new sitemap, homepage elements, and fragment anchors.

