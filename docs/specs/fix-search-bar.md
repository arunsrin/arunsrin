# Feature Specification: Full-Text Search Relevance Scoring & Keyboard Navigation

## 1. Overview & User Story
When searching arunsrin's digital garden via `Ctrl+K` or the site search input, readers searching for specific tools or topics (such as "Python", "Go", "Git", "Docker", "Security") expect the corresponding dedicated note to appear immediately at the top of the search dropdown (**Rank #1**). Previously, unweighted alphabetical filtering caused notes with exact title matches (like *Python* at index #13 and *Go* at index #26) to be crowded out by incidental body mentions in earlier notes (like *About*, *AWS*, *Databases*) and truncated by the 10-result limit.

This feature introduces **weighted relevance scoring**, **search term highlighting**, **full keyboard navigation**, and **safe excerpt cleaning** while preserving zero bloat and Cloudflare Rocket Loader safety.

---

## 2. Weighted Relevance Scoring Algorithm

For each entry in `searchIndex`, calculate a match score:

| Signal | Condition | Score Bonus | Rationale |
| :--- | :--- | :--- | :--- |
| **Exact Title Match** | `item.title.toLowerCase() === query` | **+1000** | Direct match to the note's identity (e.g. searching "Python" for *Python*). |
| **Title Word / Prefix Match** | Title starts with query or contains word boundary `\b<query>\b` | **+500** | Leading word or standalone token in title (e.g. "Linux" in *Linux Systemd*). |
| **Title Substring Match** | Title contains query substring | **+250** | Partial title match. |
| **Exact Tag Match** | Query exactly equals an entry in `item.tags` | **+300** | Curated frontmatter topic match. |
| **Tag Substring Match** | Query is a substring of any tag in `item.tags` | **+100** | Partial tag match. |
| **Permalink Slug Match** | Leaf slug matches query (e.g. `/python/`) | **+200** | URL structure matches query. |
| **Body Content Match** | Query appears in note content text | **+10 to +50** | Scaled by frequency and capped at +50 so body mentions never overtake titles or tags. |
| **Home / Index Demotion** | `item.permalink === "/"` | **-100** | Prevents the homepage from crowding out specific leaf notes. |

### Sorting & Slicing:
- Filter candidate pool: `score > 0`.
- Sort candidates: `b.score - a.score` (descending score).
- Return top 10: `.slice(0, 10)`.

---

## 3. UI, Accessibility & Keyboard Navigation

1. **Query Term Highlighting:**
   - Matched search terms within result titles and snippets are highlighted with `<mark class="search-highlight">` styled to match the theme accent.
2. **Keyboard Navigation:**
   - `ArrowDown`: Moves selection down through search results.
   - `ArrowUp`: Moves selection up through search results (or returns to search input).
   - `Enter`: Navigates to the currently highlighted result (or the #1 result if none actively highlighted).
   - `Escape`: Closes search results and blurs/clears input.
   - Mouse hover updates the `.search-result-active` state seamlessly.
3. **Snippet Cleanliness:**
   - Excerpt snippets centered on the match term cleanly strip unparsed icon syntax (`:material-*:`, `:simple-*:`, etc.) and markdown heading hashes (`#`).

---

## 4. Architectural Constraints & Non-Negotiables

1. **Zero Bloat & Zero External Frameworks:**
   - Vanilla JavaScript only (<2.5KB minified), inlined cleanly inside `layouts/partials/header.html`.
   - No heavy search libraries (no Lunr, Fuse, etc.).
2. **Cloudflare Rocket Loader Compatibility:**
   - Absolutely zero inline HTML event handlers (`onclick`, `onkeydown`, `onmouseover`, etc.).
   - All interactions bound cleanly via `addEventListener`.
3. **Sacred Prose Principle:**
   - Zero modifications to markdown prose in `home/**/*.md`.
4. **Automated Test Coverage:**
   - Automated regression test suite `scripts/test_search.js` integrated into `./scripts/test.sh`.

---

## 5. Acceptance Criteria

1. **Exact Match Ranking:**
   - Query `"python"` returns `/tech/programming/python/` at **Rank #1**.
   - Query `"go"` returns `/tech/programming/go/` at **Rank #1**.
   - Queries `"docker"`, `"git"`, `"security"`, `"linux"` return their corresponding notes in the **top 3**.
2. **Term Highlighting:**
   - Generated search results contain `<mark class="search-highlight">` wrapping the query term in titles/snippets.
3. **Keyboard Listener Verification:**
   - Script event listeners properly handle `ArrowDown`, `ArrowUp`, `Enter`, and `Escape` without errors.
4. **Cloudflare Rocket Loader Safety:**
   - Zero inline event handlers anywhere in generated search markup.
5. **Strict Build & Full Test Pass:**
   - `./scripts/test.sh` passes 100% green with zero Hugo build warnings.
