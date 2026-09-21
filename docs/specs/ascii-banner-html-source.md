# Feature Specification: ASCII Banner and Stoic Quote in HTML View-Source

## 1. Overview & Context
In keeping with the digital garden's Easter egg philosophy (joining the random footer fortunes, chess watermarks, animated emojis, and custom `x-lotr` HTTP response headers), this feature introduces a playful ASCII art banner and philosophical quote hidden in the HTML source code. When curious visitors or developers open "View Source" or inspect page markup, they are greeted by an ASCII Owl of Athena and a Stoic pun on self-examination:

> *"Examine thyself, and inspect thy source."*

This builds on classic Stoic and classical literature themes (Seneca, Socrates' *Apology*, and Marcus Aurelius' *Meditations*) while gently poking fun at the act of inspecting page source code.

---

## 2. Architecture & Design

### 2.1 ASCII Art Banner Design
The banner features a clean, high-contrast ASCII Owl of Athena (classical symbol of wisdom and scrutiny) paired with the pun quote and site metadata:

```html
<!--!
             ,___,
            (O,o)   "Examine thyself,
            /)__)    and inspect thy source."
            -" "-
-->
```

### 2.2 Template Integration
The banner is placed in `layouts/_default/baseof.html` directly following the `<!DOCTYPE html>` declaration:
```html
<!DOCTYPE html>
<!--!
             ,___,
            (O,o)   "Examine thyself,
            /)__)    and inspect thy source."
            -" "-
-->
<html lang="{{ or .Site.Language.Lang "en" }}">
...
```
Because `baseof.html` serves as the base template for the entire site, the banner will be consistently present at the top of every generated page (homepage, tech notes, book reviews, sitemap, 404, etc.).

### 2.3 Hugo Minification Configuration (`hugo.toml`)
Hugo uses `tdewolff/minify` during `hugo --gc --minify`. To ensure the HTML banner is never stripped during production builds:
1. The comment utilizes the special comment prefix `<!--!`, which `tdewolff/minify` respects when `keepSpecialComments = true` (default in Hugo).
2. Explicitly configure `keepComments = true` under `[minify.tdewolff.html]` in `hugo.toml` to guarantee comment retention across all Hugo versions and environments.

---

## 3. Constraints & Guardrails

1. **Sacred Prose Principle:**
   No markdown content in `home/` or any author notes may be modified.
2. **Zero Bloat & Zero Runtime Overhead:**
   The feature is pure static HTML comment markup. No JavaScript, CSS, or external resources are required.
3. **HTML5 Standards Compliance:**
   Placing the comment immediately after `<!DOCTYPE html>` ensures standards mode is reliably triggered in all modern and legacy browsers, while keeping the Easter egg within the first 15 lines of view-source.
4. **Automated Test Coverage & CI Parity:**
   A dedicated Python test suite (`scripts/test_ascii_banner.py`) is added, integrated into both `./scripts/test.ps1` and `./scripts/test.sh`, and dynamically verified by `scripts/test_ci_parity.py`.

---

## 4. Acceptance Criteria

1. **HTML Source Comment Presence:**
   - In the generated HTML of all pages, an HTML comment contains the ASCII Owl of Athena `(O,o)` and the quote `"Examine thyself, and inspect thy source."`.
2. **Hugo Minification Preservation:**
   - When building with `hugo --gc --minify --panicOnWarning`, the banner comment remains fully intact in `public/index.html` and across all generated HTML files.
3. **Multi-Page Coverage:**
   - The banner is present on the homepage (`/index.html`), section overview pages (e.g. `/books/index.html`, `/tech/index.html`), and leaf notes (e.g. `/tech/k8s/index.html`).
4. **CI & Local Test Suite Parity:**
   - `scripts/test_ascii_banner.py` passes with exit code 0.
   - `./scripts/test.ps1` and `./scripts/test.sh` pass cleanly with zero warnings.
   - `scripts/test_ci_parity.py` validates dynamic test discovery without CI drift.
