# Feature Specification: Consistent Animated Emojis for Tech Notes

## 1. Overview & User Story
When navigating to `/tech/` (Tech Notes), readers should see every note and sub-category prefixed with its characteristic animated icon (such as 🧠 for AI, 🐳 for Docker, 🐧 for Linux, 🔒 for Security & OpenSSL), consistent with the presentation on `/books/`, `/games/`, and the homepage.

Previously, [`home/tech/openssl.md`](home/tech/openssl.md) was the only file with a hardcoded emoji in its frontmatter (`title: "🔒 OpenSSL"`), while all other notes only had animated icons in their markdown H1 headings. Consequently, Hugo's `list.html` rendered `📄 🔒 OpenSSL` alongside plain `📄 AI`, `📄 Docker`, etc.

---

## 2. Technical Architecture & Changes

1. **Frontmatter `icon:` Definition:**
   - Every tech note in `home/tech/` (including sub-categories `linux/` and `programming/`) declares an `icon:` frontmatter string matching the animated icon used on the home page and in its H1 heading (e.g. `icon: ":material-brain:{ .anim-bounce }"`).
2. **OpenSSL Title Normalization:**
   - In `home/tech/openssl.md`:
     - Change `title: "🔒 OpenSSL"` $\rightarrow$ `title: "OpenSSL"`.
     - Add `icon: ":material-lock:{ .anim-bounce }"`.
     - Update H1 heading to `# :material-lock:{ .anim-bounce } OpenSSL` to match the site's Iconify syntax.
3. **Template Rendering in `layouts/_default/list.html`:**
   - Section page lists display the icon when present, falling back to `📁` / `📄`:
     ```html
     {{ with .Params.icon }}{{ . }} {{ else }}{{ if .IsSection }}📁{{ else }}📄{{ end }} {{ end }}{{ .Title }}
     ```
   - Processed by the existing client-side `transformIcons()` in `layouts/partials/footer.html`.
4. **Sidebar Navigation Consistency:**
   - In `layouts/partials/sidebar-tree.html`, use `{{ with .Params.icon }}{{ . }} {{ else }}📁/📄 {{ end }}` so the navigation tree in the sidebar also renders animated icons for tech sub-pages.
5. **Related Notes Card Consistency:**
   - In `layouts/partials/related-notes.html`, use `{{ with .page.Params.icon }}{{ . }}{{ else }}...{{ end }}` so related note cards also display the note's canonical animated icon.

---

## 3. Architectural Constraints & Non-Negotiables

1. **Sacred Prose Principle:**
   - Author's commentary, notes, reviews, and prose remain 100% untouched. Only frontmatter metadata (`icon:`) and structural heading formatting are touched.
2. **Zero Bloat:**
   - Leverages the existing lightweight self-hosted Iconify bundle (`iconify-icon.min.js`). No external icon fonts or frameworks.
3. **Cloudflare Rocket Loader Safety:**
   - Zero inline event handlers.
4. **Automated Test Coverage & CI Parity:**
   - Dedicated test script `scripts/test_tech_emojis.py` wired into both `./scripts/test.sh` and `.github/workflows/ci.yml`.

---

## 4. Acceptance Criteria

1. **Animated Icon Presence on `/tech/`:**
   - All sub-pages listed under `/tech/` render an animated Iconify icon (e.g. `iconify-icon`).
2. **OpenSSL Normalization:**
   - OpenSSL renders title as `OpenSSL` (not `🔒 OpenSSL`) with an animated lock icon.
3. **Child Sections Consistency:**
   - Sub-pages under `/tech/linux/` and `/tech/programming/` also render their respective animated icons.
4. **Search Index Cleanliness:**
   - Title in `public/index.json` remains clean plain text without unparsed icon shortcodes.
5. **Full CI Pass:**
   - Both `./scripts/test.sh` and GitHub Actions CI pass with zero warnings and 100% green tests.
