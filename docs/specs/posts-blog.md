# Feature Specification: Chronological Posts & Dispatches Space (`/posts/`)

## 1. Overview & Context
This digital garden is primarily organized conceptually (Tech Notes, Books, Games, Other Media, Research), reflecting the author's preference for evergreen notes over ephemeral feeds. However, an evergreen garden naturally creates friction for throwaway remarks, announcements, brief commentary, and timely dispatches.

Following the author's scoping discussion and sign-off, this feature introduces a dedicated, lightweight chronological space: **Posts** (`/posts/`).

Inspired by Bryce Wray's clean archive design ([Posts | BryceWray.com](https://www.brycewray.com/posts/)), this section provides:
- A reverse-chronological archive of posts sorted by publication date (`date`).
- Readable post cards featuring titles, formatted dates, reading times, optional tags, and short descriptions.
- Responsive, clean pagination controls for browsing past posts without loading massive DOM trees.
- Sequential post navigation (Previous / Next post) on individual post pages.
- Built-in RSS feed auto-generation at `/posts/index.xml`.
- Seamless integration into site navigation (sidebar, homepage hubs, and sitemap directory).

---

## 2. Architecture & Implementation Design

### 2.1 Content Organization (`home/posts/`)
- **Section Root (`home/posts/_index.md`):**
  Defines the section metadata:
  ```yaml
  ---
  title: "Posts"
  description: "Chronological dispatches, announcements, quick updates, and throwaway thoughts."
  weight: 50
  params:
    icon: "📝"
  ---
  ```
- **Post Markdown Files (`home/posts/<slug>.md`):**
  Each post contains:
  ```yaml
  ---
  title: "Post Title"
  date: 2026-09-21T12:00:00+05:30
  description: "Brief summary or excerpt of the post."
  tags: [] # optional
  ---
  ```
- An introductory inaugural post is provided to establish the section and demonstrate format.

### 2.2 Templates (`layouts/posts/`)
Hugo template lookup order allows `layouts/posts/` to specialize rendering for the `posts` section without disrupting evergreen notes:
1. **`layouts/posts/list.html`:**
   - Standard breadcrumbs (`🏠 Home / Posts`).
   - Section header with title `📝 Posts`, description, and a subtle link to the RSS feed (`/posts/index.xml`).
   - Reverse-chronological list of regular pages sorted by `.Date.Reverse`.
   - Card layout displaying:
     - Title link (`.RelPermalink`).
     - Published date formatted cleanly (`.Date.Format "Jan 02, 2006"`).
     - Reading time badge (`⏱️ {{ .ReadingTime }} min read`).
     - Description snippet (`.Description` or `.Summary`).
     - Tags when present (`.Params.tags`).
   - Built-in Hugo pagination (`.Paginate`) with previous/next and page number controls.
2. **`layouts/posts/single.html`:**
   - Standard breadcrumbs (`🏠 Home / Posts / <Title>`).
   - Metadata bar: publication date, reading time, word count, tags.
   - Post content body.
   - Sequential post navigation: "← Previous Post" and "Next Post →" (`.PrevInSection` and `.NextInSection`).
   - Related notes/posts component (`related-notes.html`).

### 2.3 Visual Styling (`home/css/extra.css`)
- Reuses the site's design tokens and light blue palette (`#40E0D0`, `#2fa4e7`, `#0284c7`, and `#38bdf8` in dark mode).
- Post list styling:
  - `.posts-list-stream`: Grid or flex stream of `.post-entry-card`.
  - `.post-entry-card`: Card with subtle border, soft hover elevation, clean typography.
  - `.post-entry-header`: Title and date alignment.
  - `.post-entry-meta`: Meta badges for date and reading time.
  - `.post-entry-desc`: Muted description text.
  - `.posts-nav-pager`: Elegant pagination buttons with accessible active/hover states.
  - `.post-sequential-nav`: Previous/Next post navigation footer.

### 2.4 Navigation & Discovery Integration
1. **Left Sidebar (`layouts/partials/sidebar.html`):**
   - Automatically included via `.Site.Sections.ByWeight` with `weight: 50` and `icon: "📝"`.
2. **Homepage Hubs (`home/_index.md`):**
   - Added as a 5th card under `# :material-compass-outline:{ .anim-rotate } Hubs` in `home/_index.md`:
     `[Explore Posts](posts/index.md)`
3. **Sitemap (`home/sitemap.md`):**
   - Added to `home/sitemap.md` with deep-link anchor `posts`.
4. **Search Index (`layouts/index.json`):**
   - Posts are automatically indexed for full-text client search on `/` and `Ctrl+K`.

---

## 3. Constraints & Guardrails

1. **Sacred Prose Principle:**
   No existing author prose, notes, or reviews may be modified or altered.
2. **Zero Bloat & Vanilla JavaScript:**
   Pure static HTML/CSS with native Hugo templates. Zero external scripts or frameworks.
3. **Cloudflare Rocket Loader & Event Safety:**
   Zero inline event handlers (`onclick`, `onload`, etc.).
4. **Minified HTML Regex Robustness:**
   All test assertions on generated HTML must handle optional quotes for `--minify` compatibility (Rule 14).
5. **Fixed Tag Taxonomy Guardrail:**
   The site strictly enforces a 32-tag taxonomy in `scripts/test_tags.py`. Starter posts must not introduce unauthorized tags or skew frequency limits.
6. **Automated Regression Test Suite (`scripts/test_posts.py`):**
   Companion test suite asserting:
   - Structural presence of `/posts/` archive and generated HTML.
   - Reverse chronological ordering by date.
   - Post metadata (date format, reading time, description).
   - Pagination controls presence and markup validity.
   - Sequential prev/next navigation on single post pages.
   - RSS feed generation at `/posts/index.xml`.
   - Sidebar, homepage hub card, and sitemap presence.
   - Negative tests against broken links or invalid dates.
7. **Zero Direct Commits to Master:**
   All work must be developed, tested, reviewed, and committed exclusively in the feature worktree (`.worktrees/feat-posts`). Master advances only via PR merge after author sign-off.
