# Feature Specification: Frosted Title Bar & Compact Modern Sidebar UX

## 1. Overview & Context

The site's top title bar was previously a flat, solid horizontal strip (`linear-gradient(#40E0D0, #2fa4e7 75%, #2c9ad9)`) that felt blocky and disjointed against the page content. Concurrently, the chessboard watermark was hardcoded to start at `top: 56px`, abruptly cutting off at the header boundary.

On the left, the navigation sidebar used a flat dull slate grey (`#f1f5f9`), excessive vertical spacing between sections (e.g. Books, Games), and inconsistent font rendering compared to the main content's Ubuntu typeface.

This feature modernizes both components:
1. **Translucent Frosted Glass Title Bar:**
   - Semi-transparent gradient header (`backdrop-filter: blur(12px)` / `-webkit-backdrop-filter: blur(12px)`).
   - Chessboard watermark begins at `top: 0`, extending smoothly behind the translucent header and fading down into the body.
   - Soft translucent bottom border and luminous shadow dissolving naturally into content.
2. **Compact Modern Sidebar:**
   - Refreshed canvas (`#f8fafc` in light mode, clean dark slate in dark mode) eliminating dull grey.
   - Tighter vertical rhythm (reducing section and list gaps by ~40%).
   - Pure Ubuntu typography across all sidebar headings, summaries, and links.
   - Modern pill navigation with smooth hover transitions, rounded corners, and a crisp left-accent border on active pages.

---

## 2. Technical Architecture & Component Design

### 2.1 Translucent Frosted Header (`layouts/partials/head.html`)
- CSS rule `.site-header`:
  ```css
  .site-header {
    background: var(--header-bg); /* ~50-54% alpha gradient */
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.25);
    box-shadow: 0 4px 20px rgba(47, 164, 231, 0.12);
    position: sticky;
    top: 0;
    z-index: 1000;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.18);
  }
  ```
- In light mode:
  `--header-bg: linear-gradient(135deg, rgba(64, 224, 208, 0.50), rgba(47, 164, 231, 0.52) 75%, rgba(44, 154, 217, 0.54));`
- In dark mode:
  ```css
  [data-theme="dark"] .site-header {
    background: rgba(15, 23, 42, 0.55);
    border-bottom: 1px solid rgba(51, 65, 85, 0.5);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
  }
  ```

### 2.2 Full-Height Chessboard Watermark Integration
- In `layouts/partials/head.html`:
  ```css
  .chess-watermark.corner-top-right,
  .chess-watermark.corner-top-left {
    top: 0;
  }
  ```
  The watermark tile grid starts at the very top edge (`top: 0`) and is visible through the frosted glass title bar, creating a unified, atmospheric corner pattern.

### 2.3 Compact Modern Sidebar Architecture
- **Palette:** `--bg-sidebar` updated from `#f1f5f9` to `#f8fafc` (light mode) and `#0f172a` (dark mode) to eliminate dull flat grey.
- **Typography:** Explicit `font-family: var(--font-family-sans);` (`Ubuntu`) on `.sidebar-left` and navigation tree.
- **Spacing:**
  - `details.nav-section-details`: `margin-top: 0.45rem;`
  - `.nav-section-title`: `margin-top: 0.85rem; margin-bottom: 0.25rem;`
  - `.nav-tree ul`: `padding-left: 0.75rem; margin: 0.15rem 0;`
  - `.nav-tree li`: `margin: 0.15rem 0;`
- **Pill Links & Active Indicator:**
  - `.nav-tree a`: `padding: 0.28rem 0.6rem; border-radius: 0.375rem; border-left: 2px solid transparent; font-size: 0.885rem;`
  - `.nav-tree a:hover`: `background: rgba(2, 132, 199, 0.07); color: var(--link-color); border-left: 2px solid rgba(2, 132, 199, 0.4); transform: translateX(2px);`
  - `.nav-tree a.active`: `background: rgba(2, 132, 199, 0.12); color: var(--link-color); font-weight: 600; border-left: 3px solid var(--link-color);`

---

## 3. Constraints & Guardrails

1. **Sacred Prose Principle (Rule 9):**
   Zero modifications to markdown notes, reviews, or summaries.
2. **Zero Bloat & Performance (Rule 1):**
   Pure CSS enhancements with hardware-accelerated `backdrop-filter`. No JavaScript frameworks or heavy libraries.
3. **Visual Identity:**
   Respects turquoise-to-sky-blue gradient and light blue accent colors (`#0284c7` / `#38bdf8`).
4. **Cloudflare Rocket Loader Safety (Rule 2):**
   Zero inline HTML event handlers.
5. **Automated Regression Testing & Parity (Rules 10 & 11):**
   Dedicated test suite `scripts/test_title_sidebar_ux.py` verifying CSS rules, DOM structure, and CI discovery.

---

## 4. Acceptance Criteria

1. **Frosted Glass Header:**
   - `.site-header` includes `backdrop-filter: blur(...)` and semi-transparent background.
   - Chessboard watermark starts at `top: 0` for seamless background blending.
2. **Compact Sidebar:**
   - Sidebar uses `#f8fafc` canvas and explicit Ubuntu font family.
   - Vertical section gaps between details/sections tightened by ~40% (`margin-top <= 0.5rem`).
   - Active navigation links render with modern pill highlight and left-accent border.
3. **Build & Test Parity:**
   - Hugo builds cleanly with zero warnings.
   - All regression test suites in `./scripts/test.sh` pass cleanly.
