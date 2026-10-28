# Feature Specification: Surprise Me / Random Note Dice Roll

## 1. Overview & Context

In an extensive digital garden, serendipitous discovery is a key delight of exploration. Readers may want to wander outside hierarchical browsing and jump directly to an unexpected note across Books, Games, Tech Notes, Research, or Posts.

This feature adds a playful, accessible "Surprise Me" dice roll trigger:
- A glassmorphic header button (`#random-note-btn`) in `layouts/partials/header.html` displaying `🎲`.
- A global keyboard shortcut (`r` / `R`) to trigger the dice roll from anywhere on the site (when not typing in an input).
- A playful rolling spin animation on the dice before jumping to the random note.
- Candidate filtering using the existing client index (`/index.json`) that strips out utility pages (homepage, sitemap, now, uses, tags, section hubs) and the current note.

---

## 2. Technical Architecture & Component Design

### 2.1 Semantic Header Markup (`layouts/partials/header.html`)
Inside `.nav-controls`, preceding `#site-search`:
```html
<button type="button" id="random-note-btn" class="random-btn" title="Surprise me / Random note (r)" aria-label="Surprise me / Random note (r)">
  <span class="random-icon">🎲</span>
</button>
```

- **Semantic HTML:** Native `<button type="button">`.
- **Accessibility:** Explicit `aria-label="Surprise me / Random note (r)"` and `title="Surprise me / Random note (r)"`.

### 2.2 Symmetrical Button Styling & Animation (`layouts/partials/head.html`)
Share button styling with `.theme-toggle-btn` and `.search-btn`:
```css
.theme-toggle-btn,
.search-btn,
.random-btn {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  border-radius: 0.375rem;
  padding: 0.35rem 0.55rem;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
}

.random-icon {
  display: inline-block;
  line-height: 1;
  transition: transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.random-btn.rolling .random-icon {
  transform: rotate(360deg) scale(1.18);
}
```

Dark mode support:
```css
[data-theme="dark"] .random-btn {
  background: rgba(30, 41, 59, 0.7);
  border-color: var(--border-color);
  color: var(--text-color);
}
```

### 2.3 Candidate Note Filtering & Roll Execution (`layouts/partials/header.html`)
The client search index `/index.json` is fetched and cached (sharing `searchIndex` if the command palette has already fetched it).

Utility and navigation pages are excluded:
- Root: `/`
- Utility pages: `/sitemap/`, `/now/`, `/uses/`
- Taxonomies: `/tags/`, `/tags/*`
- Hub indexes: `/posts/`, `/books/`, `/games/`, `/tech/`, `/other-interests/`
- The current page (`window.location.pathname`) to prevent rolling to the note currently being read.

When triggered:
1. Add `.rolling` class to `#random-note-btn` to trigger the playful 360° spin.
2. Select a uniform random note from the filtered candidate pool.
3. After a brief animation delay (~250-300ms), navigate to `target.permalink`.
4. If `/index.json` is not yet cached, fetch asynchronously and jump upon resolution.

### 2.4 Keyboard Shortcut Handling (`layouts/partials/header.html`)
- Listens for `keydown` event on `document`.
- Key: `e.key === 'r' || e.key === 'R'`.
- Ignored if modifiers are pressed (`e.ctrlKey`, `e.metaKey`, `e.altKey`).
- Ignored if user is interacting with an input, textarea, select, or `isContentEditable`.
- Ignored if the search modal (`#search-modal`) is currently open.

### 2.5 Cloudflare Rocket Loader & Zero Bloat Safety
- Zero inline event handlers (pure `addEventListener`).
- Pure vanilla JS under 400 bytes, atomic deployment within `layouts/partials/header.html`.

---

## 3. Acceptance Criteria

1. **Header Button Markup & Symmetry:**
   - `#random-note-btn` exists within `.nav-controls` in `layouts/partials/header.html`.
   - Has `class="random-btn"`, contains `<span class="random-icon">🎲</span>`, and has `aria-label="Surprise me / Random note (r)"` and `title="Surprise me / Random note (r)"`.
   - Symmetrically styled with `.search-btn` and `.theme-toggle-btn` across light and dark modes.

2. **Random Note Jump & Filtering:**
   - Clicking `#random-note-btn` navigates to a valid note URL.
   - Non-content pages (homepage, `/sitemap/`, `/now/`, `/uses/`, `/tags/*`, `/posts/`, `/books/`, `/games/`, `/tech/`, `/other-interests/`) are excluded from candidates.
   - The current URL is excluded so the roll always navigates to a different note.

3. **Playful Roll Animation:**
   - Triggering the random note triggers a rotation animation on the dice icon before navigation.

4. **Keyboard Shortcut (`r`):**
   - Pressing `r` / `R` outside form inputs and modal dialogs initiates the roll and navigation.
   - Pressing `r` inside text fields or search input does not trigger navigation.

5. **Automated Regression Test Suite & CI Parity:**
   - Dedicated regression test suite authored at `scripts/test_random_note.py`.
   - Includes positive assertions (button presence, accessibility attributes, CSS rules, script logic) and negative assertions (exclusion of utility/taxonomy URLs).
   - Test suite runs in `./scripts/test.ps1`, `./scripts/test.sh`, and passes all 10 adversarial review gates.

6. **Sacred Prose Preservation:**
   - Zero markdown notes or commentary files are modified.
