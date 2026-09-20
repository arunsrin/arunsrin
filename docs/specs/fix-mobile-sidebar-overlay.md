# Feature Specification: Mobile Sidebar Overlay Stacking Context & Clickability Fix

## 1. Overview & Context
In mobile view (screen width <= 768px), opening the mobile navigation drawer previously resulted in a severe visual and interaction bug:
- The entire screen, **including the slide-out navigation sidebar**, appeared blurred and dimmed under `#sidebar-overlay`.
- Nothing inside `.sidebar-left` was clickable because `#sidebar-overlay` covered the entire viewport on top of `.sidebar-left`, intercepting all click events and prematurely closing the drawer without navigating.

### Root Cause Analysis
- In `layouts/_default/baseof.html`, `.sidebar-left` resides inside `.layout-container`.
- In `layouts/partials/head.html`, `.layout-container` had `position: relative; z-index: 1;`.
- Setting an integer `z-index: 1` created a new local CSS stacking context rooted at `1`.
- `#sidebar-overlay` is a direct child of `<body>` with `position: fixed; inset: 0; z-index: 1150; backdrop-filter: blur(2px);`.
- Because `.layout-container` was trapped in stacking context `1`, its child `.sidebar-left` (even with `z-index: 1200`) was rendered **behind** `#sidebar-overlay` (`1150 > 1`).
- Consequently, the overlay's backdrop blur and dark background covered `.sidebar-left`, and all touch/pointer events hit `#sidebar-overlay` instead of the sidebar links.

---

## 2. Technical Architecture & Changes

1. **CSS Stacking Context Correction (`layouts/partials/head.html`):**
   - In `.layout-container`, replace `z-index: 1;` with `z-index: auto;` (or omit integer `z-index`), ensuring `.layout-container` does not establish an isolated stacking context.
   - In `@media (max-width: 768px)`, explicitly enforce `.layout-container { z-index: auto; }`.
   - Ensure `.sidebar-left` (`position: fixed; z-index: 1200;`) and `#sidebar-overlay` (`position: fixed; z-index: 1150;`) participate directly in the root stacking context of `<body>`, guaranteeing that `1200 > 1150` places `.sidebar-left` cleanly on top of `#sidebar-overlay`.

2. **JavaScript Click Handler Enhancement (`layouts/partials/header.html`):**
   - In the sidebar click listener, replace `if (e.target.tagName === 'A')` with `if (e.target.closest('a'))`.
   - This ensures clicks on nested icon spans or emoji text inside link elements correctly trigger navigation and close the drawer cleanly.

3. **Dynamic CI Test Discovery & Parity Guardrail (`.github/workflows/ci.yml` & `scripts/test_ci_parity.py`):**
   - Replace hardcoded script enumerations in GitHub Actions with dynamic wildcard test discovery (`scripts/test_*.py` and `scripts/test_*.js`).
   - Add `scripts/test_ci_parity.py` as Step 10 in `./scripts/test.ps1` and `./scripts/test.sh` to physically fail local runs if any test script in `scripts/` is not covered by CI.

---

## 3. Constraints & Guardrails

1. **Sacred Prose Principle:**
   Markdown content and prose remain completely untouched.
2. **Performance & Zero Bloat:**
   No extra JavaScript libraries or stylesheets. Pure CSS stacking context fix and vanilla JS enhancement.
3. **Cloudflare & Rocket Loader Safety:**
   Zero inline event handlers; all interactions use unobtrusive `addEventListener`.
4. **Automated Test Mandate & CI Parity:**
   Author a dedicated automated regression test suite `scripts/test_mobile_sidebar.py` and enforce continuous execution parity via `scripts/test_ci_parity.py`.
5. **Adversarial Code Review Governance:**
   All changes audited against `REVIEW.md` across 10 adversarial review gates.

---

## 4. Acceptance Criteria

1. **Stacking Context Hierarchy:**
   - On mobile screens (<= 768px), `.sidebar-left` has an effective `z-index` higher than `#sidebar-overlay` (`1200 > 1150`).
   - `.layout-container` does not establish an isolated stacking context with an integer `z-index` lower than `#sidebar-overlay`.
2. **Visual Clarity of Sidebar:**
   - When the sidebar is open on mobile, `#sidebar-overlay` blurs and darkens the main page content, but `.sidebar-left` sits cleanly above the overlay and is completely unblurred.
3. **Sidebar Clickability:**
   - All navigation links in `.sidebar-left` are directly clickable and receive pointer events.
   - Clicking `#sidebar-overlay` (outside the sidebar drawer) closes the drawer.
   - The close button (`#sidebar-close-btn`) closes the drawer.
   - Clicking links (including clicking on icons/emojis inside `<a>`) navigates and closes the drawer.
4. **CI Parity & Zero Hugo Warnings:**
   - All tests in `./scripts/test.ps1` and `./scripts/test.sh` pass cleanly with zero warnings.
5. **Automated Test Discovery & CI Parity Gate:**
   - `scripts/test_ci_parity.py` asserts that every test script in `scripts/` is covered by GitHub Actions CI.

