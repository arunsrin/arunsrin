# Feature Specification: Dark Mode Code Blocks with Dracula Theme

## 1. Overview & Context

In **arunsrin's notes** ([https://www.arunsr.in](https://www.arunsr.in)), technical notes, tutorials, and development logs include numerous code blocks (`pre > code`) and inline code snippets (`code`).

When users view the site in dark mode (`[data-theme="dark"]`), code blocks become completely illegible: unstyled tokens, shell output, prompts, and plain code snippets render as white text on a white/light gray background.

### Root Cause
1. **Chroma Inline Styles:** Hugo's Chroma highlighter defaults to `noClasses = true`, baking inline `style="background-color:#f7f7f7;..."` directly onto `<pre>` tags.
2. **CSS Variable Override Failure:** In `home/css/extra.css`, `.content pre { background-color: var(--code-bg); }` cannot override the inline HTML style attribute due to CSS specificity rules.
3. **Dark Mode Text Collision:** In `[data-theme="dark"]`, the body color is `--text-color: #f1f5f9` (near-white). Any unhighlighted text in code blocks inherits this light text color while the `<pre>` container remains fixed at `#f7f7f7`, yielding invisible white-on-white text.
4. **Poor Token Contrast:** Even if container backgrounds were forced dark via `!important`, light-mode Chroma token inline colors (such as dark blue `#0a3069`) provide insufficient contrast on dark backgrounds.

---

## 2. Human Sign-Off & Scoping Alignment

Based on interactive alignment with the author:
1. **Dark Mode Syntax Palette:** Dracula theme was selected by the author for dark mode code blocks.
2. **Light Mode Syntax Palette:** Clean GitHub Light theme for daylight readability.
3. **Class-Based Highlighting:** Switch Hugo to `markup.highlight.noClasses = false` to eliminate inline styles and enable clean, theme-aware CSS styling.
4. **Inline Code:** Explicit styling for inline `<code>` tags with subtle background pill matching `--code-bg` and border matching `--border-color`.

---

## 3. Technical Architecture & Component Design

### 3.1 Hugo Configuration (`hugo.toml`)
Enable class-based syntax highlighting:
```toml
[markup.highlight]
  codeFences = true
  guessSyntax = true
  lineNos = false
  noClasses = false
  style = "github"
```

### 3.2 Dark Mode Design Tokens (`layouts/partials/head.html`)
In `[data-theme="dark"]`, configure `--code-bg` to Dracula's authentic dark canvas:
- `--code-bg: #282a36;`
- Contrast border: `--border-color: #44475a;` or existing `--border-color: #334155;`

### 3.3 Dual-Theme Chroma Stylesheet (`home/css/extra.css`)
1. **Light Mode (.chroma / default):**
   - Background: `var(--code-bg)` (`#f8fafc`)
   - Text color: `#1f2328`
   - High-contrast GitHub Light tokens (`.k`, `.kd`, `.s`, `.m`, `.c`, etc.)
2. **Dark Mode (`[data-theme="dark"] .chroma`):**
   - Background: `var(--code-bg)` (`#282a36`)
   - Text color: `#f8f8f2` (Dracula foreground)
   - Dracula syntax tokens:
     - Keywords / Operators: `#ff79c6` (pink)
     - Functions / Classes: `#50fa7b` (green)
     - Strings: `#f1fa8c` (yellow)
     - Numbers / Constants: `#bd93f9` (purple)
     - Variables / Builtins / Types: `#8be9fd` (cyan)
     - Comments: `#6272a4` (muted blue-slate)
3. **Inline Code Snippets (`:not(pre) > code`):**
   - Font family: `var(--font-family-mono)`
   - Background: `var(--code-bg)`
   - Border: `1px solid var(--border-color)`
   - Color: `var(--text-color)`
   - Border radius: `0.25rem`
   - Padding: `0.15rem 0.35rem`
   - Font size: `0.88em`

### 3.4 Code Block Container & Copy Button Harmony
Preserve `.code-container` and `.copy-code-btn` in `layouts/partials/footer.html` and `layouts/partials/head.html`:
- Ensure copy button stays clearly visible on hover in both themes.
- Pre blocks have consistent border, border-radius, and horizontal scrolling (`overflow-x: auto`).

---

## 4. Verifiable Acceptance Criteria

1. **Class-Based Highlighting Active:**
   - `hugo.toml` explicitly sets `noClasses = false`.
   - Generated HTML contains `<div class="highlight"><pre tabindex="0" class="chroma">` with zero inline `style="background-color: ..."` attributes on `<pre>`.
2. **Dark Mode Dracula Styling:**
   - In `[data-theme="dark"]`, `.chroma` and `.content pre` use `#282a36` background and `#f8f8f2` base text.
   - Dracula syntax token classes (`.k`, `.s`, `.nf`, `.m`, `.c`, etc.) are defined under `[data-theme="dark"]`.
   - Fallback and unhighlighted text blocks (e.g. `data-lang="fallback"`) have high-contrast text against `#282a36`.
3. **Light Mode GitHub Styling:**
   - In light mode, `.chroma` uses light background (`#f8fafc` or `#f7f7f7`) with dark, high-contrast text and standard GitHub token colors.
4. **Inline Code Styling:**
   - Inline `<code>` elements outside of `<pre>` have distinct background (`var(--code-bg)`), border (`var(--border-color)`), and legible text in both light and dark modes.
5. **Print Stylesheet Integrity:**
   - Under `@media print`, code blocks retain clear borders and dark text on white backgrounds (`pre, .content pre { background-color: #f8fafc !important; color: #0f172a !important; }`).
6. **Automated Test Coverage & CI Parity:**
   - Dedicated test suite `scripts/test_code_blocks.py` validates all criteria above.
   - Dynamic discovery by `scripts/test_ci_parity.py` ensures 100% CI coverage.

---

## 5. Architectural Guardrails
- **Sacred Prose:** No content markdown files modified.
- **Zero Bloat:** Zero third-party runtime JS or CSS libraries; pure vanilla CSS and Hugo build-time Chroma output.
- **Rocket Loader Safety:** Zero inline event handlers.
