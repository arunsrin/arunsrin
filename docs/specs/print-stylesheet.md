# Feature Specification: Dedicated Print & PDF Export Stylesheet (@media print)

## 1. Overview & Context

Readers of **arunsrin's notes** frequently reference technical notes, book summaries, and research documents, often wishing to print them or export them as PDFs via browser print dialogs (`Ctrl+P` / `Cmd+P` / Save as PDF).

Currently, triggering browser print renders all screen UI chrome—including the top navigation header, collapsible sidebars, table of contents, search triggers, theme toggle, footer fortunes with reroll dice, back-to-top floating buttons, and background watermarks. This clutters the document and wastes paper.

This feature introduces a dedicated, high-performance `@media print` stylesheet that transforms any note into an elegant, publication-grade document formatted specifically for physical printing and PDF export.

---

## 2. Human Sign-Off & Scoping Alignment

Based on interactive alignment with the author:
1. **Related Notes & Backlinks:** Hidden during print to keep documents concise and focused.
2. **Table of Contents (TOC):** Hidden during print (anchor navigation is not applicable on paper).
3. **Link URL Annotations:** Displayed **only for external links** (`a.external-link` / `a[href^="http"]`), expanding their URL in parentheses. Internal links remain clean without appended URLs to avoid paragraph clutter.
4. **Trigger Mechanism:** Native browser printing (`Ctrl+P` / `Cmd+P` / browser print menu) without adding extra buttons to the UI chrome.

---

## 3. Technical Architecture & Component Design

### 3.1 Targeted Element Pruning
The following elements must have `display: none !important;` under `@media print`:
- **Navigation & Layout Chrome:** `.site-header`, `.sidebar-left`, `.sidebar-right`, `.mobile-menu-btn`, `#sidebar-overlay`, `.site-nav`.
- **In-Page Navigational Anchors:** `.toc-container`, `.toc-wrapper`, `.table-of-contents`.
- **Interactive Widgets:** `.search-container`, `#search-modal`, `#search-dialog`, `.theme-toggle-btn`, `.fortune-card`, `#quote-container`, `#back-to-top-btn`.
- **Peripheral & Footer Sections:** `.site-footer`, `.related-notes`, `.chess-watermark`.

### 3.2 Typography, Layout & High Contrast
- **Page Geometry:**
  ```css
  @page {
    margin: 1.5cm;
    size: auto;
  }
  ```
- **Container Sizing:**
  - `.layout-container`, `main`, `article`, and `.content` must expand to `width: 100% !important; max-width: 100% !important; margin: 0 !important; padding: 0 !important;`.
  - Grid/flex layout structures for screen columns must flatten to block flow.
- **Color Overrides:**
  - Background must be forced to pure white (`#ffffff !important;`) and text to deep charcoal/black (`#111111 !important;`).
  - Dark mode variables (`[data-theme="dark"]`) must be neutralized under `@media print`.
  - Links should print in a clean, legible dark tone (e.g. `#0f172a` or underlined `#0284c7`) without bright background fills.

### 3.3 Page Break & Pagination Discipline
- **Avoid Breaks Inside Atomic Content:**
  - Code blocks (`pre`, `code`, `.highlight`), tables (`table`), blockquotes (`blockquote`), and figure images (`img`, `figure`) must declare:
    ```css
    break-inside: avoid;
    page-break-inside: avoid;
    ```
- **Avoid Stranded Headings (Orphans):**
  - Section headings (`h1`, `h2`, `h3`, `h4`, `h5`, `h6`) must enforce:
    ```css
    break-after: avoid;
    page-break-after: avoid;
    ```

### 3.4 External Link Footnoting / Expansion
- External links must display their target URL immediately following the link text:
  ```css
  a.external-link::after,
  article .content a[href^="http"]:not([href*="arunsr.in"])::after {
    content: " (" attr(href) ")";
    font-size: 0.85em;
    font-weight: normal;
    color: #475569;
    word-break: break-all;
  }
  ```
- Internal links (e.g. `href="/books/thinking-in-bets/"` or `href="#tech-notes"`) must NOT have URLs appended.
- Anchor links (`a[href^="#"]`) must NOT have URLs appended.
- Breadcrumbs and tag pills must NOT have URLs appended.

---

## 4. Acceptance Criteria

1. **Clean Print Output:** When printing or saving as PDF, only the breadcrumbs, note title, page metadata (reading time, word count, updated date, tags), and body content are rendered.
2. **Hidden UI Chrome:** The site header, mobile menu, search modal, theme toggle, left sidebar, right sidebar (TOC), footer fortunes, reroll button, back-to-top button, chess watermark, and related notes card are completely hidden.
3. **Full Width Layout:** The printed content occupies 100% printable width without horizontal truncation or artificial screen-based column constraints.
4. **Contrast & Theme Invariance:** Print output is rendered in high-contrast dark text on pure white background, irrespective of whether the active theme is light or dark.
5. **Smart Page Breaks:** Code blocks, tables, and blockquotes do not split awkwardly across page breaks; headings do not appear as orphans at the bottom of a page.
6. **Selective Link Annotations:** External links show their target URL in parentheses; internal links and anchor links remain clean.
7. **Performance & Zero Bloat:** Pure CSS implementation; zero JavaScript dependencies; zero impact on screen rendering or Lighthouse scores.
8. **Automated Test Coverage & CI Parity:** A companion automated test script (`scripts/test_print_stylesheet.py`) validates CSS rules, hidden selector coverage, link expansion rules, and runs in both local runners (`test.ps1` / `test.sh`) and GitHub CI.

---

## 5. Guardrails & Compliance Checklist

- [x] **Sacred Prose Principle:** Zero markdown content files are modified or rewritten.
- [x] **Zero Bloat:** Pure CSS; no client-side JavaScript or external libraries.
- [x] **Cloudflare Rocket Loader Safety:** No inline event handlers.
- [x] **CI Parity:** Companion test suite covered by dynamic CI discovery (`scripts/test_*.py`).
- [x] **Console Encoding:** Test script includes UTF-8 stdout reconfiguration.
