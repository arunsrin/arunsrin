# Feature Specification: Scaffold '/now' and '/uses' Pages (Living Snapshots & Colophon)

## 1. Overview & Context

This feature introduces two essential personal web staples to **arunsrin's notes**:
1. **Now Page (`/now`):** Following Derek Sivers' movement ([nownownow.com](https://nownownow.com)), providing visitors with a living snapshot of what the author is currently reading, playing, hacking on, and thinking about.
2. **Uses Page (`/uses`):** Following Wes Bos' colophon standard ([uses.tech](https://uses.tech)), detailing the author's hardware setup, GNU Emacs environment, Linux workstation, keybindings, dotfiles, and daily productivity workflow.

### Division of Responsibility
- **LLM Role (The Fellowship):** In an isolated worktree (`.worktrees/now-page`), scaffold `home/now.md` and `home/uses.md` with minimal YAML frontmatter (`title: "Now"`, `title: "Uses"`), empty body, wire up sidebar navigation links in `layouts/partials/sidebar.html`, integrate both pages into `home/sitemap.md`, register both as untagged meta pages in `scripts/test_tags.py`, author a dedicated automated test suite (`scripts/test_now_and_uses.py`), format prose cleanly via `scripts/fill_paragraph.py`, and verify 100% CI parity.
- **Author Role (Arun):** Carve out and author personal content at his own pace without artificial AI structure, inspired by curated examples across the web.

---

## 2. Technical Architecture & Implementation Details

### 2.1 Content Files (`home/now.md` and `home/uses.md`)
- `home/now.md` (URL: `/now/`):
  ```yaml
  ---
  title: "Now"
  ---
  ```
- `home/uses.md` (URL: `/uses/`):
  ```yaml
  ---
  title: "Uses"
  ---
  ```
- Both files feature clean minimal frontmatter and empty content bodies (0 content bytes), allowing the author complete creative freedom.

### 2.2 Navigation Integration (`layouts/partials/sidebar.html`)
- In `layouts/partials/sidebar.html`, under `<div class="nav-section-title">Site</div>`:
  ```html
  <div class="nav-section-title">Site</div>

  <ul>
    <li><a href="/now/" class="{{ if eq .RelPermalink "/now/" }}active{{ end }}">⏳ Now</a></li>
    <li><a href="/uses/" class="{{ if eq .RelPermalink "/uses/" }}active{{ end }}">🛠️ Uses</a></li>
    <li><a href="/about/" class="{{ if eq .RelPermalink "/about/" }}active{{ end }}">ℹ️ About</a></li>
    <li><a href="/sitemap/" class="{{ if eq .RelPermalink "/sitemap/" }}active{{ end }}">🗺️ Sitemap</a></li>
  ...
  ```
- Both links include active indicator pill styling when browsing their respective URLs.

### 2.3 Sitemap Integration (`home/sitemap.md`)
- Under the `Site Meta` section:
  ```markdown
  ---

  # :material-information-outline:{ .anim-pulse } Site Meta

  <span id="site-meta" class="heading-anchor-target"></span>

  - <span id="now"
    class="heading-anchor-target"></span>[:material-clock-outline:{
    .anim-pulse } Now](now.md) — What I'm currently reading, playing,
    and thinking about.
  - <span id="uses"
    class="heading-anchor-target"></span>[:material-tools:{
    .anim-pulse } Uses](uses.md) — Hardware, Emacs setup, Linux
    workstation, and daily workflow.
  - <span id="about"
    class="heading-anchor-target"></span>[:material-penguin:{
    .anim-pulse } About](about.md) — About me, the tools I use, and this
    site.
  ```

### 2.4 Tag Taxonomy Integration (`scripts/test_tags.py`)
- Register `"now.md"` and `"uses.md"` in `meta_pages` list (`meta_pages = ["_index.md", "about.md", "now.md", "uses.md"]`).
- Asserts that meta pages have zero orphan tags and preserve the strict 33-tag taxonomy distribution.

### 2.5 Dedicated Automated Test Suite (`scripts/test_now_and_uses.py`)
Validates:
1. `home/now.md` and `home/uses.md` exist with valid frontmatter and zero tags.
2. `public/now/index.html` and `public/uses/index.html` exist with canonical titles and `.layout-container` / `.main-content`.
3. Sidebar navigation contains both `/now/` and `/uses/` links with active indicators on their pages, and inactive on homepage.
4. Sitemap contains links and anchor targets (`id="site-meta"`, `id="now"`, `id="uses"`).
5. Search index `public/index.json` indexes both `/now/` and `/uses/` with correct titles.
6. Zero inline event handlers (Rocket Loader safety).

---

## 3. Acceptance Criteria

1. **Scaffolding Presence:** `home/now.md` and `home/uses.md` exist with valid frontmatter (`title: "Now"`, `title: "Uses"`) and empty bodies.
2. **Build Cleanliness:** `hugo --gc --minify --panicOnWarning` builds cleanly with 0 errors and 0 warnings.
3. **HTML Generation:** `public/now/index.html` and `public/uses/index.html` generated with canonical titles and layout containers.
4. **Sidebar Navigation:** Sidebar nav includes `/now/` (`⏳ Now`) and `/uses/` (`🛠️ Uses`) under the `Site` section; has active pill class when on their respective pages.
5. **Sitemap Integration:** `home/sitemap.md` references `now.md` and `uses.md` with anchor targets and descriptions; verified in generated `public/sitemap/index.html`.
6. **Search Index Validity:** `public/index.json` indexes `/now/` and `/uses/` with correct titles.
7. **Tag Taxonomy Compliance:** `scripts/test_tags.py` passes cleanly with both files having zero tags.
8. **Automated Test Coverage:** Dedicated regression test suite integrated into `./scripts/test.ps1`, `./scripts/test.sh`, and GitHub Actions CI.
9. **Zero Bloat & Safety:** Vanilla CSS/HTML, zero inline JS event handlers, UTF-8 console output.
10. **Sacred Prose:** Zero author writing modified or altered across existing notes.
