# Feature Specification: Bi-directional Backlinks & Unified Related Notes

## 1. Overview & User Story
As a reader exploring arunsrin's digital garden, I want to discover meaningful connections between notes — whether a note is explicitly referenced by another note ("Mentioned In"), directly links outward to another note ("Referenced"), shares focused intellectual topics ("#tag"), or belongs to the same leaf series/section ("In this series" / "In this section") — consolidated into a single, cohesive **`🔗 Related Notes`** section at the bottom of each page.

---

## 2. Layout, DOM Order & Appearance

1. **Page Position & Flow:**
   - The `🔗 Related Notes` section appears directly below the page content and outward reference links, immediately preceding the footer.
   - Supported across both **Single Pages** (`layouts/_default/single.html`) and **Content-Bearing Section Pages** (`layouts/_default/list.html`, such as `/games/fps/`, `/books/fiction/sci-fi/`).
   - Pure taxonomy listings (e.g. `/tags/`) and the homepage (`/`) are excluded.

2. **Conditional Rendering (Zero-Empty State):**
   - If a page has 0 candidate related notes, the entire section (`<section class="related-notes-section">`) is completely suppressed. No empty headers or placeholders are rendered.

3. **Card Presentation:**
   - Displayed as a responsive card grid (`.related-notes-grid`) with cards styled to match the site's light blue theme (`#2fa4e7` / `#0284c7`).
   - Each card displays:
     - **Section / Hierarchy Label:** (e.g. `Tech`, `Fiction`, `Psychology`).
     - **Note Title:** Cleanly hyperlinked to the target note.
     - **Relationship Badge:** Colored pill indicating why the note was recommended (e.g. `Mentioned In`, `Referenced`, `#productivity`, `In this section`).
     - **Contextual Snippet:**
       - For `Mentioned In`: The exact sentence or surrounding phrase where the link occurred, formatted in italics between quotes (`“...phrase...”`).
       - For other cards: A clean summary excerpt from the note's text.

---

## 3. Relationship Signals & Priority Scoring

All relationship signals are unified into a single candidate pool. Candidates are deduplicated by permalink; if a note matches multiple signals, the highest priority badge and score are retained. Cards are sorted by descending score and capped at a maximum of 4 cards (ensuring pages display a concise deck of 3–4 related notes rather than a verbose list):

| Signal | Badge Text | Score | Description |
| :--- | :--- | :--- | :--- |
| **Incoming Backlink** | `Mentioned In` | **500** | Notes whose body content links directly to the current note. Excerpts capture the exact contextual sentence where the mention occurs. |
| **Outgoing Reference** | `Referenced` | **400** | Notes that the current note explicitly links to in its body text. |
| **Focused Topic Tag** | `#<tag>` | **100/tag** | Notes sharing focused tags (e.g. `#devops`, `#monitoring`, `#psychology`, `#nabokov`). Excludes blanket bucket tags. |
| **Section / Series Sibling** | `In this section` / `In this series` | **50** | Fallback for notes with < 3 candidates; pulls siblings from the immediate parent category (e.g. Oxford VSI series or game genres). Excluded from generic directories. |

---

## 4. Anti-Spurious Match Protection

1. **Blanket Taxonomy Tag Exclusion:**
   - High-level organizational tags (`books`, `games`, `tech`, `research`, `non-fiction`, `fiction`) must be strictly stripped from tag similarity matching.
   - Prevents spurious matches between unrelated topics (e.g., preventing COVID-19, Capitalism, or Climate Change from appearing on the Productivity page).
2. **Ancestor Navigation Link Suppression:**
   - Section landing pages and ancestor TOCs (e.g. `/games/` linking to `/games/fps/`) must NOT be counted as incoming backlink mentions (`(not (.IsAncestor $currentPage))`).
3. **Generic Directory Fallback Suppression:**
   - Generic multi-topic directories (like `other-interests/research/`) are excluded from sibling fallbacks to avoid pairing completely unrelated research notes.

---

## 5. Cleanliness & Formatting Rules

1. **Icon Syntax Cleansing:**
   - Snippets and titles must cleanly strip unparsed icon syntax (e.g. `:material-*:`, `:simple-*:`, `:fontawesome-*:`, `:octicons-*:`) and associated attribute blocks (`{ ... }`).
2. **Heading Marker Cleansing:**
   - Markdown header hashes (`#`, `##`, etc.) must be stripped from snippets to prevent raw markdown artifacts in card previews.

---

## 6. Architectural Constraints & Non-Negotiables

1. **Sacred Prose Principle:**
   - Prose, opinions, and text inside `home/**/*.md` must NOT be modified or rewritten. Only YAML frontmatter metadata tags and templates/CSS may be created or adapted.
2. **Zero Bloat & Performance:**
   - 100% build-time generation via Hugo Go templates (`layouts/partials/related-notes.html`).
   - Zero client-side JavaScript frameworks or render-blocking scripts.
3. **Cloudflare Rocket Loader Compatibility:**
   - Absolutely zero inline HTML event handlers (`onclick`, `onload`, `onchange`, etc.).
4. **Git Worktree Isolation & Background Servers:**
   - All work takes place in isolated worktree `.worktrees/<feature-name>`.
   - Dual-port preview servers maintained by agents (`:1313` for master baseline, `:1314` for feature worktree).

---

## 7. Automated Test Coverage & Verification

Every requirement above is verified by automated regression tests in `scripts/test_related_notes.py` integrated directly into `./scripts/test.sh`:
- **Coverage Assertions:** 100% of single notes (57/57) and content-bearing section pages render populated cards.
- **Mention Accuracy:** Validates incoming `Mentioned In` badges and contextual excerpts (e.g. Despair mentioned in About, Security mentioned in OpenSSL).
- **Reference Accuracy:** Validates outgoing `Referenced` badges (e.g. Docker referencing Kubernetes, Productivity referencing Editors).
- **Topic Accuracy:** Validates `#topic` matches (e.g. Prometheus to Grafana via `#monitoring`, Flow to Productivity via `#productivity`).
- **Anti-Spurious Protection:** Negative assertions verifying COVID-19, Capitalism, and Climate Change never match Productivity, and Accounting never matches Despair.
- **Snippet Cleanliness:** Regex audit verifying zero raw icon syntax or heading hashes leak into HTML across all generated pages.
- **Section Page Coverage:** Verifies content-bearing section pages in `/games/` and `/books/` render related notes.
- **Card Cap & Conciseness:** Verifies no page renders more than 4 cards, ensuring a concise list of 3–4 related notes.
