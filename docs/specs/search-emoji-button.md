# Feature Specification: Symmetrical Search Emoji Header Button

## 1. Overview & Context

Currently, the search trigger in the site navigation header (`layouts/partials/header.html`) is rendered as a faux read-only input box:
```html
<div class="search-container">
  <input type="text" id="site-search" class="search-input" placeholder="/" title="Search notes (/ or Ctrl+K)" aria-label="Search notes (/ or Ctrl+K)" autocomplete="off" readonly role="button">
</div>
```
Visually, this appears as an awkward, narrow box containing a single isolated slash (`/`) character. Because clicking it opens the Command Palette / Spotlight Search Modal (`search-modal`) rather than accepting inline input, presenting it as an `<input>` is confusing and clutters the title bar.

Next to the search trigger sits the theme toggle button (`#theme-toggle`), which is an elegant, glassmorphic button displaying `🌙`.

This feature replaces the awkward faux input with a clean, semantic `<button id="site-search" class="search-btn">` featuring the search emoji `🔍`, styled symmetrically with the theme toggle button.

---

## 2. Technical Architecture & Component Design

### 2.1 Semantic Header Markup (`layouts/partials/header.html`)
- Replace the legacy `<input id="site-search" class="search-input" ...>` with an accessible button:
  ```html
  <div class="search-container">
    <button type="button" id="site-search" class="search-btn" title="Search notes (/ or Ctrl+K)" aria-label="Search notes (/ or Ctrl+K)">
      <span class="search-icon">🔍</span>
    </button>
  </div>
  ```
- **Semantic HTML:** Uses native `<button type="button">` instead of a faux input with `role="button"`.
- **Accessibility:** Preserves `aria-label="Search notes (/ or Ctrl+K)"` and `title="Search notes (/ or Ctrl+K)"` for screen readers and tooltips.

### 2.2 Symmetrical Button Styling (`layouts/partials/head.html`)
- Introduce `.search-btn` matching `.theme-toggle-btn` exact sizing, padding, border radius, and transitions:
  ```css
  .search-btn {
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
  .search-btn:hover {
    background: var(--bg-secondary);
    border-color: var(--link-color);
    transform: scale(1.05);
  }
  [data-theme="dark"] .search-btn {
    background: rgba(30, 41, 59, 0.7);
    border-color: var(--border-color);
    color: var(--text-color);
  }
  ```
- Clean up obsolete `.search-input` rules and focus expansion width logic.
- Mobile responsiveness: Ensure `.search-btn` scales naturally with `.theme-toggle-btn` on viewports < 768px.

### 2.3 Command Palette Activation & Focus Management (`layouts/partials/header.html`)
- `searchTriggerBtn = document.getElementById('site-search')` binds unobtrusively via `addEventListener('click', () => openSearchModal())`.
- Zero inline handlers (Cloudflare Rocket Loader safety).
- Global keyboard shortcuts (`/` and `Ctrl+K`) continue to activate `openSearchModal()`.
- Upon modal dismissal (`closeSearchModal()`), focus seamlessly returns to `previouslyFocusedElement` (e.g. `#site-search`).

---

## 3. Acceptance Criteria

1. **Semantic Button Markup:**
   - `#site-search` is rendered as a `<button type="button">` element with `class="search-btn"`.
   - The button contains the search emoji `🔍` wrapped in `<span class="search-icon">🔍</span>`.
   - The button retains `aria-label="Search notes (/ or Ctrl+K)"` and `title="Search notes (/ or Ctrl+K)"`.

2. **Visual Sizing & Symmetry:**
   - `.search-btn` shares identical padding, border-radius, translucent glass background, hover transform, and box-shadow with `.theme-toggle-btn`.
   - Dark mode styles apply matching translucent slate background (`rgba(30, 41, 59, 0.7)`).
   - Obsolete `.search-input` width/expansion CSS is removed or cleanly retired without visual regressions.

3. **Interactive & Shortcut Functionality:**
   - Clicking `#site-search` opens the Command Palette / Search Modal (`#search-modal`).
   - Pressing `/` or `Ctrl+K` from anywhere on the page opens the modal.
   - Closing the modal (`Esc` or backdrop click) restores focus to the trigger button.
   - Zero inline event handlers (full Cloudflare Rocket Loader safety).

4. **Automated Regression Testing & CI Parity:**
   - Dedicated automated regression tests verify the presence, attributes, and styles of `#site-search`.
   - Existing test suites (`test_title_sidebar_ux.py`, `test_search_modal.js`) pass cleanly with 100% green status.
   - All tests run and pass in both local test runners (`./scripts/test.ps1`, `./scripts/test.sh`) and GitHub CI.

5. **Guardrails & Sacred Prose:**
   - Zero markdown content or note prose is modified.
   - Lightweight vanilla CSS and JS with zero new dependencies or frameworks.
