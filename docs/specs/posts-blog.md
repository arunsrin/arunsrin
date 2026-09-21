# Feature Specification: Chronological Posts & Dispatches Space (`/posts/`)

## 1. Overview & Context
This digital garden is primarily organized conceptually (Tech Notes, Books, Games, Other Media, Research), reflecting the author's preference for evergreen notes over ephemeral feeds. However, an evergreen garden naturally creates friction for throwaway remarks, announcements, brief commentary, and timely dispatches.

Following the author's scoping discussion, sign-off, and iteration review, this feature introduces a dedicated, lightweight chronological space: **Posts** (`/posts/`).

Inspired by Bryce Wray's clean archive design ([Posts | BryceWray.com](https://www.brycewray.com/posts/)), this section provides:
- A reverse-chronological archive of posts sorted by publication date (`date`).
- Readable post cards featuring titles, formatted dates, reading times, tags, and short descriptions.
- Responsive, clean pagination controls for browsing past posts without loading massive DOM trees.
- Sequential post navigation (Older / Newer post) on individual post pages.
- Built-in RSS feed auto-generation at `/posts/index.xml`.
- Controlled Sidebar Navigation: Sub-dropdowns for `Latest` (showing the most recent posts) and `Archive` (linking to `/posts/` and year groupings) so the sidebar never balloons with hundreds of links over time.
- Clicking `Posts` triggers standard Hugo behavior (navigating to `/posts/` archive).
- Hugo archetype and documentation in `README.md` detailing how the author can easily author new posts (`hugo new posts/<slug>.md`).
- A single concise sample post (`Hello, Posts`) equipped with sample tags and a note on Gemini / Antigravity generation.

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
  tags:
    - meta
  ---
  ```
- **Inaugural Sample Post:**
  `home/posts/hello-posts.md` serves as the sole reference post, tagged with `meta`, and notes its AI-assisted creation during the sprint.

### 2.2 Hugo Archetype (`archetypes/posts.md`)
To make publishing frictionless for the author, an archetype template is provided at `archetypes/posts.md`. When the author runs:
```bash
hugo new posts/my-title.md
```
Hugo automatically creates `home/posts/my-title.md` pre-populated with title, timestamp, description, and tag structure.

### 2.3 Templates (`layouts/posts/` & Sidebar)
1. **`layouts/posts/list.html`:**
   - Standard breadcrumbs (`🏠 Home / Posts`).
   - Section header with title `📝 Posts`, description, and a subtle link to the RSS feed (`/posts/index.xml`).
   - Reverse-chronological list of regular pages sorted by `.Date.Reverse`.
   - Post entry cards with title, date, reading time badge, description, and tag pills.
   - Built-in Hugo pagination (`.Paginate`) with previous/next controls.
2. **`layouts/posts/single.html`:**
   - Standard breadcrumbs (`🏠 Home / Posts / <Title>`).
   - Metadata bar: publication date, reading time, word count, tags.
   - Post content body.
   - Sequential post navigation: "← Older Post" and "Newer Post →" (`.PrevInSection` and `.NextInSection`).
   - Related notes/posts component (`related-notes.html`).
3. **Sidebar Specialization for Posts (`layouts/partials/sidebar.html`):**
   - When `.Section == "posts"`:
     - Root summary links to `/posts/` (default archive view).
     - Sub-dropdown `✨ Latest`: lists the 5 most recent posts for quick access.
     - Sub-dropdown `🗄️ Archive`: links to `/posts/` (All Posts) and displays year counts.
     - Prevents hundreds of future posts from cluttering the root navigation tree.

### 2.4 Visual Styling (`home/css/extra.css`)
- Reuses the site's design tokens and light blue palette (`#40E0D0`, `#2fa4e7`, `#0284c7`, and `#38bdf8` in dark mode).
- Post list styling: `.post-entry-card`, `.post-entry-meta`, `.post-entry-desc`, `.posts-nav-pager`, `.post-sequential-nav`.
- Full dark mode support using CSS custom properties.

### 2.5 Tag Taxonomy Architecture
- The digital garden's evergreen notes maintain their strict 32-tag taxonomy in `scripts/test_tags.py`.
- Posts in `home/posts/` are validated for kebab-case formatting and absence of reserved hierarchy tags, allowing the author to tag posts freely with tags like `meta`, `announcement`, etc. without causing evergreen taxonomy regression failures.

---

## 3. Constraints & Guardrails

1. **Sacred Prose Principle:**
   Existing evergreen notes remain untouched.
2. **Zero Bloat & Vanilla JavaScript:**
   Pure static HTML/CSS with native Hugo templates. Zero external scripts or frameworks.
3. **Cloudflare Rocket Loader & Event Safety:**
   Zero inline event handlers (`onclick`, `onload`, etc.).
4. **Minified HTML Regex Robustness:**
   All test assertions on generated HTML handle optional quotes and attribute order independence.
5. **Automated Regression Test Suite (`scripts/test_posts.py`):**
   Validates:
   - Posts archive and RSS feed.
   - Single post metadata, tags, and breadcrumbs.
   - Sidebar `Latest` and `Archive` sub-dropdown structure.
   - Negative assertions against runaway post trees in the sidebar.
