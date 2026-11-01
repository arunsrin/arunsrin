# Feature Specification: Prominent Link to tools.arunsr.in

## 1. Overview & Context

The author builds web tools and utilities hosted on the neighboring domain [https://tools.arunsr.in](https://tools.arunsr.in). To provide seamless discoverability and quick navigation across sites, `tools.arunsr.in` should be prominently featured in two key locations:
1. **Header Top-Right (`.nav-controls`):** A symmetrical glassmorphic icon button alongside the Surprise/Random note dice roll, Search modal trigger, and Theme toggle.
2. **Left Navigation Drawer (`sidebar.html`):** A dedicated entry under the "Site" section of the sidebar navigation.

Visual identity:
- Icon: Toolbox emoji `🧰` (distinct from `🛠️ Uses`).
- Label: `🧰 Tools`.
- Behavior: External link opening in a new tab (`target="_blank" rel="noopener noreferrer"`).

---

## 2. Technical Architecture & Component Design

### 2.1 Header Top-Right Button (`layouts/partials/header.html`)

Inside `.nav-controls` of `layouts/partials/header.html`:
```html
<a href="https://tools.arunsr.in" id="header-tools-btn" class="tools-btn" title="Tools (tools.arunsr.in)" aria-label="Tools (tools.arunsr.in)" target="_blank" rel="noopener noreferrer">
  <span class="tools-icon">🧰</span><span class="tools-external-icon" aria-hidden="true">↗</span>
</a>
```

- Positioned in `.nav-controls` alongside `#random-note-btn`, `.search-container`, and `#theme-toggle`.
- Rendered as a semantic `<a>` link with secure external navigation attributes (`target="_blank"` and `rel="noopener noreferrer"`).
- Displays `🧰` with a clear diagonal arrow indicator `↗` (`.tools-external-icon`) differentiating it as an external destination from the internal site controls.
- Accessible `aria-label` and `title` describing the destination.

### 2.2 Symmetrical Button Styling (`layouts/partials/head.html`)

In `layouts/partials/head.html`, group `.tools-btn` with `.theme-toggle-btn`, `.random-btn`, and `.search-btn`:
```css
.theme-toggle-btn,
.random-btn,
.search-btn,
.tools-btn {
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
  text-decoration: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
}
.theme-toggle-btn:hover,
.search-btn:hover,
.random-btn:hover,
.tools-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--link-color);
  transform: scale(1.05);
  color: var(--text-color);
}
[data-theme="dark"] .theme-toggle-btn,
[data-theme="dark"] .random-btn,
[data-theme="dark"] .search-btn,
[data-theme="dark"] .tools-btn {
  background: rgba(30, 41, 59, 0.7);
  border-color: var(--border-color);
  color: var(--text-color);
}
```

### 2.3 Sidebar Navigation Link (`layouts/partials/sidebar.html`)

Under the `<div class="nav-section-title">Site</div>` navigation list in `layouts/partials/sidebar.html`:
```html
<li>
  <a href="https://tools.arunsr.in" class="external-link" target="_blank" rel="noopener noreferrer">
    🧰 Tools<span class="external-icon" aria-hidden="true">↗</span>
  </a>
</li>
```
- Positioned under the `Site` section immediately following `🛠️ Uses`.
- Styled with `.external-link` and external indicator `↗` matching the site's link convention.

---

## 3. Acceptance Criteria

1. **Header Top-Right Link:**
   - `#header-tools-btn` with class `tools-btn` is rendered inside `.nav-controls`.
   - Links to `https://tools.arunsr.in` with `target="_blank"` and `rel="noopener noreferrer"`.
   - Displays `🧰` emoji alongside the diagonal arrow indicator `↗` (`<span class="tools-external-icon" aria-hidden="true">↗</span>`), with `aria-label="Tools (tools.arunsr.in)"` and `title="Tools (tools.arunsr.in)"`.
   - Inherits symmetrical glassmorphic button styling across light and dark themes.

2. **Sidebar Navigation Link:**
   - Rendered in `layouts/partials/sidebar.html` under the `Site` section.
   - Links to `https://tools.arunsr.in` with `target="_blank"` and `rel="noopener noreferrer"`.
   - Displays `🧰 Tools` followed by the external indicator `<span class="external-icon" aria-hidden="true">↗</span>`.

3. **Performance, Accessibility & Cloudflare Safety:**
   - Zero inline event handlers (full Cloudflare Rocket Loader compliance).
   - Zero external libraries or render-blocking assets.
   - Responsive and accessible on both desktop and mobile viewports.

4. **Automated Regression Testing & CI Parity:**
   - Companion automated test suite `scripts/test_tools_link.py` verifying:
     - Header tools button presence, href, target, rel, and aria attributes.
     - Sidebar tools link presence, href, target, rel, and external indicator.
     - CSS rules and styling parity for `.tools-btn` in light and dark modes.
     - Zero disruption to existing navigation elements (`#theme-toggle`, `#random-note-btn`, `#site-search`).
   - The test suite is included in `./scripts/test.ps1`, `./scripts/test.sh`, and automatically picked up by GitHub Actions CI.

5. **Sacred Prose Preservation:**
   - Zero markdown content or note prose modified.
